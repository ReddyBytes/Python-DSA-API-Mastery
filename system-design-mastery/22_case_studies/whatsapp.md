# WhatsApp — Full System Design Walkthrough

> It is 3 AM in São Paulo. Maria's mother just had a fall.
> She types a message on her phone and hits send. Seven thousand miles away,
> in a suburb of Lisbon, her sister's phone buzzes within two seconds.
> No email chain. No calling plan. No dropped connection.
> Just a single grey tick, then a double grey tick, then two blue ticks.
>
> That conversation crossed oceans, hit a server cluster, was encrypted
> on Maria's phone, forwarded to her sister's device, decrypted there —
> and nobody but those two women could read it.
>
> Two billion people rely on this every day.
> In 2014, a team of 50 engineers made it work for 450 million of them.
> This is how.

---

## 1. The Problem — Scale and Two Guarantees

WhatsApp in numbers:

```
Users:               2 billion registered
Daily active:        ~500 million
Messages per day:    100+ billion
Messages per second: ~1.16 million (average), ~3-4 million (peak)
Average message:     ~2 KB (text)
Media messages:      ~30% of all messages
Concurrent users:    100–200 million at peak
```

Those numbers put WhatsApp in a class with Google Search and YouTube.
But the engineering challenge is distinct because of two unbreakable guarantees
every real messaging system must provide:

**Guarantee 1: Exactly-once, in-order delivery.**
If Maria sends three messages, her sister sees all three, in order, exactly once.
Not twice. Not out of order. Not missing if her sister's phone was offline for
an hour.

**Guarantee 2: Privacy — nobody but the participants can read the message.**
Not WhatsApp. Not the government (without Alice's device). Not a hacker
who intercepts traffic. The message is encrypted on sender's device and
decrypted only on recipient's device.

These two guarantees — together, at two billion users — are what this case
study is about.

---

## 2. Message Delivery Flow — Alice Sends to Bob

Start with the simplest case: Bob is online. Alice sends a text.

```
HAPPY PATH — BOB IS ONLINE

Alice's phone          Chat Server               Bob's phone
──────────────         ────────────              ───────────
[1] User types, hits send
    msg_id = UUID()
    Encrypt message ──────────────────▶
                        [2] Decrypt envelope
                            Store msg to queue
                            Mark: PENDING_DELIVERY
                            ─────────────────────────────────▶
                                                  [3] Phone receives message
                                                      Decrypt, display
                                                      Send delivery ack
                        [4] ◀─────────────────────────────────
                            Update: DELIVERED
                            Forward ack ──────────▶
[5] ◀────────────────────
    Double grey tick appears
                                                  [6] Bob opens chat
                                                      Sends read receipt
                        [7] ◀─────────────────────────────────
                            Update: READ
                            Forward read receipt ─▶
[8] ◀────────────────────
    Blue ticks appear
```

The three tick states map directly to server-tracked state:

```
Tick State           What it means                   Where state lives
───────────────────  ──────────────────────────────  ──────────────────
Single grey tick     Server received the message     Server (in-memory + Cassandra)
Double grey tick     Recipient's device received     Server (updated on Bob's ack)
Double blue tick     Recipient opened and read        Server (updated on read receipt)
```

This requires the server to maintain per-message, per-recipient delivery state
for every message — potentially billions of state updates per day.

### Why This Is Hard

At 1.16 million messages per second, each message triggers up to three state
transitions (stored, delivered, read). That is potentially 3.5 million
database writes per second just for message state — before we even count the
messages themselves.

The acknowledgment chain also creates latency: Alice is waiting for a round trip
acknowledgment from the server before showing a single tick. If the server
acknowledgment is slow, every send feels sluggish. The server ack must be
sub-100ms even under peak load.

---

## 3. Connection Model — Why WebSockets

### The Polling Alternative (and Why It Fails)

The naive approach: clients poll the server every few seconds asking "any new
messages for me?" At 500 million daily active users polling every 5 seconds:

```
500,000,000 users × (1 request / 5 seconds) = 100,000,000 requests/second

100 million requests/second just for "nothing new" polls.
This is 100× the actual message rate. Completely wasteful.
```

Most of those requests return empty. You're paying the cost of a full HTTP
request, TLS handshake overhead, and server processing for nothing.

### WebSockets — Persistent Bidirectional Connections

WebSocket opens a TCP connection once and keeps it open. The server can push
data to the client without the client asking.

```
HTTP polling:
  Client ──GET /messages──▶ Server ──"nothing new"──▶ Client  (every 5s)
  Client ──GET /messages──▶ Server ──"nothing new"──▶ Client
  Client ──GET /messages──▶ Server ──message!──▶ Client

WebSocket:
  Client ──────────── WS Upgrade ─────────────▶ Server
  ◀──────────────── persistent TCP ──────────────▶
  [Server pushes instantly when message arrives]
  Server ──────────── message! ────────────────▶ Client
  [No polling. No wasted requests.]
```

WhatsApp originally used XMPP (Extensible Messaging and Presence Protocol),
an XML-based standard designed for exactly this purpose — persistent TCP
connections with push delivery. Later versions moved to a custom binary
protocol over the same persistent connection model, reducing overhead
significantly (XML is verbose; a binary protocol can cut message size by 60-70%).

### Connection Server Capacity

```
Concurrent connections at peak:   ~200 million
Connections per chat server:      ~1 million (Erlang handles this
                                               with lightweight processes)

Servers needed:                   200M / 1M = 200 servers
With 3× redundancy and headroom:  ~600 chat servers total

Per connection memory (Erlang):   ~2 KB per live connection
200M connections × 2 KB           = ~400 GB total RAM across fleet
600 servers × 1 GB per server     = 600 GB headroom — comfortable
```

Erlang is the reason WhatsApp could run this lean. It was built for telecom
switches: millions of concurrent lightweight processes, preemptive scheduling,
and soft real-time guarantees. A chat server where each connection is a process
is exactly the use case Erlang was designed for.

### User Presence — Redis

When Alice opens WhatsApp, it needs to know Bob's "last seen" time. This is
tracked in Redis:

```
SET user:{bob_id}:last_seen  1709900123   EX 86400
                             (unix timestamp) (TTL: 24 hours)

ZADD online_users 1709900123 {bob_id}
```

When Bob goes offline (closes app, loses network), his connection closes and
the chat server removes him from the online set. If the connection drops
unexpectedly (no clean close), the TTL on his presence key expires naturally.

Presence is **intentionally eventually consistent**. If Bob's "last seen"
shows 2 minutes ago instead of 3 minutes ago, nobody cares. Presence never
needs strong consistency — which is why Redis (fast, in-memory, no ACID
guarantees needed) is the right tool here rather than a relational database.

---

## 4. Offline Message Storage

### What Happens When Bob Is Offline

Bob's phone dies at 7 PM. Maria sends him five messages between 7 PM and 11 PM.
At 11 PM Bob plugs in his phone, reconnects, and all five messages arrive
within seconds, in order.

```
OFFLINE DELIVERY FLOW

Maria's phone          Chat Server               Cassandra Queue
─────────────          ────────────              ───────────────
Send message ─────────────────────▶
                        Check: is Bob online?
                        Redis: NO
                        Write to offline queue ──────────────────▶
                        Send Maria single tick ◀
                        (server has the message)

                             ... Bob's phone offline for hours ...

                        Bob connects
                        Check offline queue ──────────────────────▶
                        ◀──────────────────────────── messages []
                        Deliver messages to Bob
                        Bob's phone acks each ──────────────────────▶
                        Update: DELIVERED                delete from queue
                        Forward ack to Maria ──▶
Maria sees double ticks ◀
```

### Cassandra for the Message Queue

Why Cassandra for offline message storage?

- **High write throughput**: Cassandra is designed for append-heavy workloads.
  At 1.16M messages/second, a relational database with ACID row-level locking
  would become a bottleneck immediately. Cassandra's log-structured storage
  handles this naturally.
- **Partition key = recipient**: All of Bob's queued messages live on the same
  Cassandra partition, so fetching them is a single efficient range scan —
  not a scatter-gather across nodes.
- **Linear horizontal scale**: Add nodes, add capacity. No resharding headaches.

Cassandra schema sketch:

```
Table: offline_message_queue

  Partition key:   recipient_user_id   (VARCHAR)  -- all Bob's messages together
  Clustering key:  message_timestamp   (TIMESTAMP) -- sorted, newest last
  Columns:
    message_id       UUID
    sender_id        VARCHAR
    encrypted_body   BLOB            -- encrypted ciphertext, server can't read
    message_type     TINYINT         -- 0=text, 1=image, 2=video, 3=audio
    ttl_expires_at   TIMESTAMP

  Access patterns:
    Write: INSERT into queue for recipient (append, fast)
    Read:  SELECT all WHERE recipient = bob_id ORDER BY timestamp (single partition)
    Delete: DELETE after Bob acks (by message_id)

  TTL: 30 days. If Bob never comes online in 30 days, messages are purged.
```

### The Purge Guarantee — Why This Is Unusual

Most apps (iMessage, Gmail, Facebook Messenger) store messages forever on their
servers. WhatsApp does not.

WhatsApp's design: **messages live on WhatsApp servers only until delivered**.
Once Bob's device receives and acknowledges a message, it is deleted from
WhatsApp's servers. If Bob never comes online within 30 days, the message
is purged undelivered.

This is unusual because:
1. It reduces storage costs dramatically — at 100B messages/day, storing
   them forever would require petabytes of server-side message history.
2. It is consistent with the privacy model: if servers don't store messages,
   there is nothing for servers to hand to law enforcement or leak in a breach.
3. The device is the durable store. WhatsApp is fundamentally a delivery
   network, not a storage service.

---

## 5. End-to-End Encryption — The Signal Protocol

### Why Encrypt on the Device?

The simple version: Alice's phone encrypts the message before sending it.
The server receives an unreadable blob. Bob's phone decrypts it. The server
never possesses the plaintext.

```
WITHOUT E2EE:
  Alice ──plaintext──▶ Server ──plaintext──▶ Bob
                         │
                         └── Server can read everything.
                             Government subpoena → server hands over messages.
                             Server breach → all messages exposed.

WITH E2EE (Signal Protocol):
  Alice ──encrypt──▶ ciphertext ──▶ Server ──▶ ciphertext ──▶ Bob ──decrypt──▶ plaintext
                                       │
                                       └── Server sees only encrypted blobs.
                                           Subpoena → server has nothing useful.
                                           Breach → attackers get ciphertext.
```

### Key Exchange — How Alice Gets Bob's Key

On registration, each device generates a keypair (a public key and a private key).
The private key never leaves the device. The public key is registered with
WhatsApp's servers.

```
Alice's phone          WhatsApp Server           Bob's phone
─────────────          ───────────────           ───────────
[Registration]
Generate keypair:
  private_key_A (stays here)
  public_key_A  ─── register ──────────▶  Store public_key_A

                                          [Registration]
                                          Generate keypair:
                                            private_key_B (stays here)
                                            public_key_B  ◀── register
                                          Store public_key_B

[Alice wants to message Bob]
Request Bob's public key ─────────────▶
◀────────────────────────── public_key_B
Encrypt message with public_key_B
  ciphertext = Encrypt(plaintext, public_key_B)
Send ciphertext ──────────────────────▶
                   Forward ciphertext ─────────────────────▶
                                          Decrypt with private_key_B:
                                            plaintext = Decrypt(ciphertext, private_key_B)
                                          Display message
```

The server at no point has the plaintext. It also has no private keys. Even if
WhatsApp's entire server infrastructure were compromised, the attacker would
obtain only ciphertext blobs that cannot be decrypted without Bob's private key,
which lives only on Bob's device.

### Forward Secrecy — Why Past Messages Stay Safe

A simple public key system has one weakness: if Bob's private key is ever
stolen, every past message encrypted to him can be decrypted retroactively.

The Signal Protocol solves this with **forward secrecy**. Rather than using
Bob's static keypair for every message, the protocol derives new ephemeral
session keys for each conversation. These ephemeral keys are discarded after
use.

```
Bob's static keypair:      long-lived, on device
Session keys:              derived fresh per conversation, then deleted

Attacker steals Bob's device 6 months later:
  They have the static keypair.
  The session keys used 6 months ago are gone — deleted after use.
  Past messages cannot be decrypted.
  Only current and future messages (while attacker has the device) are at risk.
```

This is implemented using the **Double Ratchet Algorithm** — a mechanism that
advances cryptographic state with every message sent or received, so that
compromising one message's keys does not compromise any other message.

### The Backup Controversy

WhatsApp stores messages on servers only until delivery (as described above).
But users want conversation history when they switch phones. The solution:
back up to Google Drive (Android) or iCloud (iOS).

The problem: those backups are historically NOT end-to-end encrypted. They
are encrypted by Google/Apple using their keys — meaning Google and Apple
can access them, and government subpoenas to those companies can obtain
message history.

WhatsApp has since introduced optional E2EE backups (2021), where the user
holds an encryption key for their backup. But this is opt-in, and most users
leave it disabled because key loss means permanent backup loss.

This is the unavoidable tension: perfect privacy (E2EE backups with user-held
keys) comes at the cost of recoverability. If you lose your phone and your
backup key, your conversation history is gone forever.

---

## 6. Group Messages

### The Naive Approach and Why It Breaks

WhatsApp supports groups of up to 1,024 members. The naive approach:
when Alice sends a message to a group, the server makes N copies of the
message and delivers one to each member.

```
Alice sends to group of 1,024 members:
  Server creates 1,024 delivery tasks
  Each task = lookup recipient's connection + send + wait for ack
  At 1,024 members × 2 KB per message = ~2 MB of delivery work per message

  At peak: WhatsApp has millions of group messages per second
  1M group messages/sec × 1,024 members = 1 trillion delivery operations/sec
  This does not scale.
```

The challenge is compounded by E2EE: in a pure E2EE system, Alice would need
to encrypt the message separately for each member (each with their own public
key). That is 1,024 encryption operations per message, all on Alice's phone,
which is a low-power mobile device.

### Sender Keys — The Practical Solution

WhatsApp uses a technique called **Sender Keys** (part of the Signal Protocol's
group messaging extension).

Instead of Alice encrypting individually to each member on every message, the
protocol establishes a **shared group session key** once, and then each message
is encrypted once with that group key.

```
ONE-TIME SETUP (when group is created or member joins):
  Alice generates a Sender Key for this group.
  Alice encrypts the Sender Key individually to each member
    (1 encryption per member — happens once per member, not per message).
  Each member receives the Sender Key for this group session.

PER-MESSAGE (the fast path):
  Alice encrypts message once with the Sender Key.
  Server fans out the single ciphertext to all 1,023 other members.
  Each member decrypts locally using the shared Sender Key.

  Cost per message: 1 encryption on Alice's phone (not 1,024).
  Server fan-out: 1,023 deliveries (unavoidable for delivery, but only one
                  ciphertext to forward — no per-member encryption needed).
```

When a member leaves a group, the Sender Key is rotated (a new key is
distributed to remaining members), so the departed member cannot decrypt
future messages even if they somehow captured the ciphertext.

### Server-Side Fan-Out Architecture

```
Alice sends group message
        │
        ▼
Chat Server receives encrypted ciphertext
        │
        ├──▶ Store in group message queue (Cassandra)
        │
        ├──▶ Fetch group member list from Group Service
        │         (cached in Redis: SET group:{group_id}:members)
        │
        └──▶ Fan-out worker distributes to each member:
                  For each member:
                    Is member online?  →  deliver immediately via WebSocket
                    Is member offline? →  write to their offline queue (Cassandra)
```

Group member lists are cached aggressively in Redis because they are read on
every group message but change infrequently (members join/leave rarely compared
to message frequency).

---

## 7. Media Uploads

### Why Media Is Separate From Text

A photo is typically 2–5 MB. A video can be 50–100 MB. Sending these through
the same chat server pipeline as text would be disastrous:

- Chat servers are optimized for millions of tiny, fast messages.
  A 100 MB video upload would block a connection for seconds.
- Media needs to be stored durably (not just until delivery).
  A recipient may want to re-download a photo later if they cleared local storage.
- Media needs CDN distribution. A photo sent in a Brazilian group chat will
  be downloaded by members in Brazil, Portugal, Angola, and Mozambique.
  A CDN edge node can serve it locally in Lisbon rather than routing to a
  US datacenter.

### The Upload and Delivery Flow

```
SENDER SIDE:
  Alice selects a photo
       │
       ▼
  [1] Encrypt media on device:
        media_key = random 256-bit AES key (generated fresh per file)
        encrypted_media = AES-CBC-Encrypt(photo, media_key)
        mac = HMAC-SHA256(encrypted_media, media_key)  -- integrity check
       │
       ▼
  [2] Upload encrypted blob to Media Server (S3-compatible)
        POST /media/upload
        Body: encrypted_media bytes
        Response: { "media_url": "https://media.whatsapp.net/..." }
       │
       ▼
  [3] Send a text message containing:
        { "type": "image",
          "media_url": "https://media.whatsapp.net/abc123",
          "media_key": base64(media_key),       -- key to decrypt it
          "media_sha256": base64(mac),           -- integrity check
          "thumbnail": base64(tiny_jpeg_thumb)  -- inline preview
        }
        This text message goes through the normal E2EE message pipeline.

RECIPIENT SIDE:
  Bob receives the text message
       │
       ▼
  [4] Extract media_url and media_key from message
       │
       ▼
  [5] Download encrypted blob from media_url
       │
       ▼
  [6] Decrypt: AES-CBC-Decrypt(blob, media_key)
      Verify:  HMAC-SHA256(blob, media_key) == media_sha256
       │
       ▼
  [7] Display photo

  WhatsApp's servers store only the encrypted blob.
  The media_key (needed to decrypt it) was sent in the E2EE message.
  WhatsApp cannot decrypt the media.
```

### Media Storage and TTL

Unlike messages (purged on delivery), media is stored longer — typically 60 days
after the last download, or until the storage TTL expires. The rationale:
a recipient might need to re-download a photo after clearing device storage,
or might receive a media message while offline and download later.

```
Media storage rough math:
  30% of 100B messages/day = 30B media messages/day
  Average media: 500 KB per message (mix of small images and video thumbnails)
  30B × 500 KB = ~15 PB/day

  With 60-day TTL and deduplication (same file sent in multiple chats stored once):
  Actual storage: hundreds of petabytes total, growing by several PB/day
```

At this scale, object storage (S3-equivalent) is the only viable option.
The write throughput (millions of new encrypted blobs per hour) and read
throughput (recipients downloading) require horizontal scale that no
traditional file server or relational database can provide.

---

## 8. Read Receipts and Presence at Scale

### The Write Amplification Problem

Every time a user opens a chat and sees new messages, read receipts are
generated. At 500 million daily active users who each read dozens of messages
per day, the read receipt write volume is enormous:

```
500M DAU × 30 chat opens per day × 5 messages seen per open
= 75 billion read receipt events per day
= ~870,000 read receipts per second

Each receipt = 1 write to update message state
             + 1 push to sender (forward the blue tick)
```

This is a bigger write workload than the messages themselves.

### How WhatsApp Handles This

Read receipts are processed asynchronously. The flow:

```
Bob reads a message
        │
        ▼
Bob's phone sends read receipt to server
        │
        ▼
Server updates message state in Cassandra (async write, batched)
        │
        ▼
Server checks: is Alice online?
    YES → push blue tick to Alice's connection immediately
    NO  → Alice sees blue tick next time she opens the app
           (server delivers the state update when Alice reconnects)
```

Cassandra handles this write volume because of its tunable consistency model.
Read receipt writes use consistency level ONE — meaning only one replica
node needs to confirm the write before the operation returns. This sacrifices
strong consistency (for a few milliseconds, different replicas may disagree
on whether a message was read) but accepts that eventual consistency is
perfectly acceptable for delivery state. If the double tick appears 500ms
late, nobody notices.

### Presence at Scale

100 million users online simultaneously, each with a "last seen" timestamp:

```
Presence storage: Redis
  Key:   user:{user_id}:last_seen
  Value: unix timestamp
  TTL:   24 hours (auto-expires if user disappears without clean disconnect)

  100M active users × 30 bytes per entry = ~3 GB in Redis
  This fits in a single Redis cluster easily.

  Update frequency: each user sends a heartbeat every 30 seconds
  100M users × (1 update / 30 seconds) = ~3.3M presence writes/second

  Redis handles this comfortably — it's designed for millions of ops/second.
```

Presence is periodically synced to Cassandra for durability. Redis is the
live read/write store; Cassandra is the persistent fallback if the Redis
cluster is restarted.

### Privacy Controls

WhatsApp allows users to hide their "last seen" timestamp and disable read
receipts (blue ticks). These settings are stored per-user and checked before
forwarding presence/receipt updates.

```
User privacy settings (Redis + Cassandra):
  last_seen_visibility:  EVERYONE | CONTACTS | NOBODY
  read_receipt_enabled:  TRUE | FALSE

If read_receipt_enabled = FALSE:
  - Bob's phone still sends read receipts internally (WhatsApp tracks reads)
  - Server does NOT forward the receipt to Alice
  - Alice never sees blue ticks
  - But WhatsApp knows Bob read the message (used for abuse detection)

If last_seen_visibility = NOBODY:
  - Bob's last_seen timestamp is not forwarded to any other user
  - Bob cannot see anyone else's last seen either (reciprocal restriction)
```

This asymmetry — where WhatsApp internally knows more than it exposes to
users — is a deliberate design choice for abuse detection. Even with all
privacy settings enabled, WhatsApp retains metadata (who messaged whom,
when, how often) even if it cannot read the content.

---

## 9. Full Architecture Diagram

Everything together: how a message travels from Alice's phone to Bob's.

```
 ┌─────────────────────────────────────────────────────────────────────────────────┐
 │                              ALICE'S PHONE                                       │
 │  1. User types message                                                           │
 │  2. Signal Protocol encrypts with Bob's session key → ciphertext                │
 │  3. Send over WebSocket to nearest Chat Server                                  │
 └──────────────────────────────────┬──────────────────────────────────────────────┘
                                    │ WebSocket (persistent TCP)
                                    ▼
 ┌─────────────────────────────────────────────────────────────────────────────────┐
 │                           LOAD BALANCER / EDGE                                   │
 │  Geographic routing — Alice hits nearest datacenter                             │
 │  WebSocket upgrade, connection registry, rate limiting                          │
 └──────────────────────────────────┬──────────────────────────────────────────────┘
                                    │
                                    ▼
 ┌─────────────────────────────────────────────────────────────────────────────────┐
 │                          CHAT SERVER CLUSTER                                     │
 │                                                                                  │
 │   Chat Server A             Chat Server B             Chat Server C             │
 │   (Alice connected here)    (Bob connected here)      (other users)             │
 │                                                                                  │
 │   Per server: ~1M connections (Erlang lightweight processes)                    │
 │   ~600 servers total at peak                                                    │
 └───────┬────────────────────────────────┬────────────────────────────────────────┘
         │                                │
         ▼                                ▼
 ┌───────────────────────┐      ┌─────────────────────────────────────────────────┐
 │      REDIS CLUSTER    │      │             CASSANDRA CLUSTER                    │
 │                       │      │                                                  │
 │  user:*:last_seen     │      │  Table: offline_message_queue                   │
 │  user:*:online        │      │    partition key: recipient_user_id             │
 │  group:*:members      │      │    clustering key: message_timestamp            │
 │  message:*:state      │      │                                                 │
 │                       │      │  Table: message_state                           │
 │  TTL-based presence   │      │    (delivered / read status per message)        │
 │  Ephemeral, fast      │      │                                                 │
 └───────────────────────┘      │  Durable, persistent queue                      │
                                └─────────────────────────────────────────────────┘
         │
         ▼
 ┌─────────────────────────────────────────────────────────────────────────────────┐
 │                          DELIVERY DECISION LOGIC                                 │
 │                                                                                  │
 │  Is Bob online?                                                                  │
 │    YES → Find which Chat Server holds Bob's connection                           │
 │           (via Redis: user:{bob_id}:server_id = "chat_server_B")                │
 │           Forward ciphertext to Chat Server B → push to Bob's WebSocket         │
 │    NO  → Write to Bob's offline queue in Cassandra                              │
 │           Send Alice single tick (message stored)                               │
 │           When Bob reconnects: drain queue, deliver in order, collect acks      │
 └─────────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
 ┌─────────────────────────────────────────────────────────────────────────────────┐
 │                              BOB'S PHONE                                         │
 │  Receives ciphertext over WebSocket                                             │
 │  Signal Protocol decrypts with private key → plaintext                         │
 │  Display message                                                                │
 │  Send delivery ack → Server → Alice (double grey tick)                         │
 │  Bob opens chat → send read receipt → Server → Alice (blue tick)               │
 └─────────────────────────────────────────────────────────────────────────────────┘

                            MEDIA PATH (parallel)
                            ─────────────────────
 Alice's phone                Media Server                  Bob's phone
 ─────────────                ────────────                  ───────────
 Encrypt photo (AES) ──────▶  Store encrypted blob (S3)
 Get media_url ◀───────────   (server cannot decrypt)
 Send msg with url + key ──▶  [Chat Server forwards msg] ──▶
                                                            Download blob
                                                            Decrypt with key
                                                            Display photo

                          KEY MANAGEMENT (Signal Protocol)
                          ─────────────────────────────────
 Alice's phone          WhatsApp Key Server            Bob's phone
 ─────────────          ───────────────────            ───────────
 Register public key ─────────────────────▶
                        Store Alice's public keys
                        Store Bob's public keys ◀──── Register public key
 Fetch Bob's public key ◀───────────────────
 [Establish Double Ratchet session locally]
 [No more server involvement in key exchange]
```

---

## 10. Key Numbers

The numbers that define the system's design constraints:

```
Metric                                    Number
──────────────────────────────────────    ─────────────────────────────
Registered users                          2 billion
Daily active users                        ~500 million
Peak concurrent connections               100–200 million
Messages per day                          100+ billion
Messages per second (average)             ~1.16 million
Messages per second (peak)                ~3–4 million
Average text message size                 ~2 KB
Media messages (% of total)              ~30%
Media storage growth                      several petabytes/day
Offline message TTL                       30 days
Media TTL (after last download)           ~60 days
Chat servers (peak)                       ~600 (Erlang, ~1M conn each)
Read receipt writes/second                ~870,000
Presence updates/second (heartbeats)      ~3.3 million

WhatsApp at acquisition (2014):
  Users served:         450 million
  Engineers:            50
  Key technology:       Erlang (BEAM VM)
  Cost per user-year:   fractions of a cent
```

The 50-engineers-for-450-million-users figure is the most cited statistic
in software engineering. It was made possible by three factors:

1. **Erlang**: Handles millions of concurrent connections per server with
   tiny per-process memory, preemptive scheduling, and built-in fault
   tolerance (the "let it crash" philosophy).

2. **Simplicity of purpose**: WhatsApp ruthlessly avoided feature creep.
   No games, no feeds, no advertising infrastructure. One thing: messaging.
   Complexity scales headcount faster than users do.

3. **Off-device storage minimal**: Because messages are deleted after delivery,
   WhatsApp's server-side storage requirements are vastly lower than apps
   that store full message history forever.

---

## 11. Design Decisions — Rationale Summary

```
Decision                              Why                              Trade-off
───────────────────────────────────   ──────────────────────────────   ─────────────────────────────
WebSocket persistent connections      Push delivery, no polling         Stateful servers — harder
                                      100M concurrent connections        to deploy/scale than HTTP
                                      possible at reasonable cost

Erlang for chat servers               1M connections per server          Niche language, smaller
                                      ~2 KB per connection (Erlang        talent pool, steeper
                                      process is very lightweight)        learning curve

Cassandra for offline queue           High write throughput               No ad-hoc queries;
                                      Partition by recipient = fast       eventual consistency
                                      single-partition reads              (acceptable here)

Signal Protocol (E2EE)                Server cannot read messages         Cannot offer server-side
                                      Subpoena-resistant by design        search of message history;
                                      Forward secrecy protects past       backup encryption is
                                      messages even if key stolen         complex UX problem

Sender Keys for group E2EE           1 encryption per message             Key rotation required
                                      (not 1 per member) — practical     when members leave;
                                      E2EE at group scale                 adds protocol complexity

Delete-on-delivery (no server         Massively reduces storage           No server-side history;
message storage)                      Consistent with E2EE privacy        cross-device sync requires
                                      model                               device-to-device transfer
                                                                          or cloud backup

Media via separate upload path        Chat servers stay fast/small        Two round trips for media
                                      CDN can serve media globally         messages; media delivery
                                      S3 scales independently              slightly slower than text

Eventual consistency for              Read receipts/presence are          Tick may update 500ms late;
receipts and presence                 high-volume, low-stakes writes      presence timestamp may be
                                      Strong consistency not needed        off by a few seconds

Redis for presence + routing          Sub-millisecond lookups              Must sync to Cassandra
                                      "Is Bob online + which server?"     for durability; Redis
                                      answered in <1ms at 200M users      restart loses live state
```

---

## 12. Interview Summary

When asked "Design WhatsApp" in an interview, the key thread to follow is:

**Start with the two guarantees**: exactly-once in-order delivery, and end-to-end
privacy. Every major architectural decision flows from these.

**The connection model drives everything**: WebSockets are not a "nice to have" —
they are the only connection model that makes 200M concurrent connections and
sub-second push delivery viable without 100M wasted polling requests per second.

**Offline delivery is the hardest reliability problem**: Cassandra's append-heavy
write model and partition-by-recipient design solve both the throughput and the
retrieval pattern in a single choice.

**E2EE is not an add-on**: it is structurally baked in. The server is designed
from the start to never see plaintext. Sender Keys make group E2EE practical
by replacing N per-message encryptions with 1.

**Media is architecturally separate**: object storage + CDN handles the 30%
of messages that are media, while chat servers stay lean and fast.

**Scale through simplicity**: the 50-engineer team that served 450M users was
possible because WhatsApp chose boring technology (Erlang, which was a mature
30-year-old telecoms language), deleted messages after delivery (no storage
explosion), and refused to build anything that wasn't core to messaging.

In an interview, sketch the happy path first (Alice online → Bob online), then
handle the offline case, then introduce E2EE as a constraint that changes the
architecture (server can't cache content, can't inspect messages for dedup),
then handle groups as a scaling problem on top of that foundation.

---

## Navigation

| | |
|---|---|
| ← Previous | [Uber Ride-Sharing](./uber.md) |
| ➡️ Next | [23 — Interview Framework](../23_interview_framework/the_45_minute_playbook.md) |
| 🏠 Home | [README.md](../README.md) |
