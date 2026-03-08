# Building Systems That Never Make You Refresh the Page
## A Guide to Real-Time Architecture

> The stock trader watching a ticker. The soccer fan seeing a goal update
> before they hear the crowd. The Figma user watching their colleague's
> cursor move in real-time. These experiences feel like magic.
> They're just websockets, well applied.

---

## Part 1: What "Real-Time" Actually Means

"Real-time" gets thrown around loosely. Let's be precise.

### Hard Real-Time vs Soft Real-Time

```
HARD REAL-TIME (embedded systems, aviation, medical devices):
  Missing a deadline = system failure.
  The ABS in your car must respond in < 1 millisecond.
  Missing that deadline means the car doesn't stop.
  → Deterministic operating systems, no garbage collection, C/C++/Rust
  → Not what web engineers mean when they say "real-time"

SOFT REAL-TIME (web applications):
  Missing a deadline = degraded user experience.
  A chat message arriving in 1.1 seconds instead of 1 second: user notices.
  A chat message arriving in 5 seconds: user is annoyed.
  A chat message arriving in 30 seconds: user reloads.
  → No catastrophic failure, but quality matters
  → This is what web engineers mean: sub-second to low-second latency

Most web "real-time" targets:
  Chat messages:          < 500ms
  Live prices/scores:     < 1 second
  Collaborative editing:  < 100ms (feels laggy if slower)
  Notifications:          < 2 seconds (user doesn't feel the delay)
```

### Why HTTP Alone Cannot Solve This

Standard HTTP has a fundamental limitation: the **client always initiates**.

```
HTTP request-response:

  Client: "Give me any new messages?"   → Server: "None."
  Client: "Give me any new messages?"   → Server: "None."
  Client: "Give me any new messages?"   → Server: "1 new message!"

  This is called polling. Problems:
    → Wastes server resources (99% of polls return nothing)
    → Latency = polling interval (poll every 1s → up to 1s delay)
    → Doesn't scale: 1M users × 1 poll/second = 1M req/sec to your server

  Server CANNOT push to the client unprompted.
  You need a persistent connection for that.
```

---

## Part 2: The Event-Driven Architecture

Before diving into specific protocols, understand the architectural style
that makes real-time systems composable.

### Services Talking Through Events

In an event-driven system, services do not call each other directly.
They publish events to a shared bus. Other services subscribe and react.

```
Direct call (synchronous):
  OrderService → calls → InventoryService.reserve()
                → calls → PaymentService.charge()
                → calls → EmailService.send()

  Problems:
    All three services must be available for OrderService to succeed.
    If Email is slow → Order is slow.
    Tight coupling: OrderService knows about all downstream services.

Event-driven (asynchronous):
  OrderService → publishes → OrderPlaced event

  InventoryService  ← subscribes → hears OrderPlaced → reserves stock
  PaymentService    ← subscribes → hears OrderPlaced → charges card
  EmailService      ← subscribes → hears OrderPlaced → sends email

  Benefits:
    OrderService does not know or care who reacts.
    Email being slow doesn't slow down the order.
    Add a new subscriber (SMS, analytics) without changing OrderService.
    Services can process at their own pace.
```

### Choreography vs Orchestration

```
CHOREOGRAPHY: each service knows what to do when it hears an event.
  No coordinator. Services are autonomous actors.

  OrderPlaced ──→ InventoryService (reserves stock, emits StockReserved)
  StockReserved ──→ PaymentService (charges, emits PaymentCharged)
  PaymentCharged ──→ FulfillmentService (ships, emits OrderShipped)

  + Loosely coupled: each service only knows its own step
  + Easy to add new services
  - Hard to visualize the full workflow
  - Debugging requires tracing events across services
  - Cycle detection: service A reacts to B's event which triggers A again?

ORCHESTRATION: a central process directs each step.
  One orchestrator knows the whole workflow.

  OrderOrchestrator:
    1. call InventoryService.reserve(orderId)
    2. call PaymentService.charge(orderId)
    3. call FulfillmentService.ship(orderId)
    4. call NotificationService.notify(userId)

  + Easy to understand the full flow (it's in one place)
  + Easy to add error handling and retry logic
  - Orchestrator is a dependency for all steps
  - Central bottleneck for complex workflows

In practice: choreography for simple event reactions,
             orchestration (e.g., AWS Step Functions) for long workflows.
```

---

## Part 3: WebSockets — Full Duplex Communication

### The Upgrade Handshake

A WebSocket connection starts as a regular HTTP request and upgrades:

```
1. Client sends HTTP request with special headers:

   GET /ws HTTP/1.1
   Host: app.example.com
   Upgrade: websocket
   Connection: Upgrade
   Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
   Sec-WebSocket-Version: 13

2. Server responds:

   HTTP/1.1 101 Switching Protocols
   Upgrade: websocket
   Connection: Upgrade
   Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=

3. The TCP connection remains open.
   Now BOTH sides can send messages anytime.

   Client → Server: "Hello"
   Server → Client: "World"
   Server → Client: "New notification: you have a reply"  ← unprompted push
   Client → Server: "Thanks"
```

### Full Duplex: Both Directions, Anytime

```
HTTP:
  ─────────────────────────────────────────────→ (client → server only to initiate)
  ←───────────────────────────────────────────── (server → client in response)

WebSocket (after upgrade):
  ──────────────────────────────────────────────→ (client → server, any time)
  ←─────────────────────────────────────────────  (server → client, any time)

  Both at the same time, on one TCP connection.
  True bidirectional, persistent channel.
```

### WebSocket Use Cases

```
EXCELLENT use cases:
  Live chat (Slack, WhatsApp Web)
    → Messages appear instantly in both directions

  Real-time prices (stock tickers, crypto exchanges)
    → Server pushes price updates as they happen

  Collaborative editing (Google Docs, Figma)
    → Every keystroke synchronized to all editors
    → Cursor positions, selections shared in real-time

  Live sports scores / election results
    → Score updates pushed without user refreshing

  Multiplayer games
    → Player positions, actions synchronized constantly

  Live auctions
    → Current bid updates pushed to all watchers

NOT good use cases:
  Notification emails (no persistence, email is better)
  File uploads (multipart HTTP is designed for this)
  Standard REST APIs (request-response is simpler)
  One-time data fetches (just HTTP GET)
```

### Scaling WebSockets: The Hard Problem

A stateful connection. Users are *pinned* to a specific server.

```
Without coordination:
  User connects to Server A (WebSocket)
  User's friend connects to Server B (WebSocket)

  Friend sends message → Server B handles it
  Server B tries to push to User → User is on Server A!
  Server B has no connection to User.
  Message is lost.

Solution 1: Sticky Sessions
  Load balancer routes the same user to the same server always.

  ┌──────────────────┐
  │   Load Balancer  │ → user 12345 always → Server A
  │  (IP/cookie hash)│ → user 67890 always → Server B
  └──────────────────┘

  + Simple, works
  - If Server A dies, all its users lose connections and must reconnect
  - Uneven distribution if some users are more active
  - Cannot scale smoothly

Solution 2: Pub/Sub Message Bus (better)
  All WebSocket servers subscribe to a shared message bus (Redis Pub/Sub,
  Kafka). When Server B needs to push to a user on Server A, it publishes
  to the bus. Server A receives it and pushes to the user.

  ┌──────────┐   publishes message   ┌───────────┐
  │ Server B │ ─────────────────────→│ Redis     │
  │          │                       │ Pub/Sub   │
  └──────────┘                       └─────┬─────┘
                                           │ subscribes
                                     ┌─────▼─────┐
                                     │ Server A  │ → pushes to user 12345
                                     └───────────┘

  + Servers are stateless (mostly) — any server can handle any user message
  + Scales horizontally — add more servers freely
  + Resilient to server failures
  - Redis becomes a bottleneck at extreme scale
  - More infrastructure complexity
```

---

## Part 4: Server-Sent Events — The Simpler Alternative

If you only need the server to push to clients (not the other way),
Server-Sent Events (SSE) is often the right choice.

### How SSE Works

SSE uses a regular HTTP connection that stays open. The server streams
`text/event-stream` formatted data down to the client continuously.

```
Client:  GET /notifications HTTP/1.1
         Accept: text/event-stream

Server:  HTTP/1.1 200 OK
         Content-Type: text/event-stream
         Cache-Control: no-cache

         (connection stays open, server sends events over time)

         data: {"type": "like", "post_id": 99, "liker": "Bob"}\n\n

         data: {"type": "comment", "post_id": 42}\n\n

         event: alert
         data: {"message": "Your order shipped!"}\n\n

         (client receives these as they arrive, auto-reconnects if disconnected)
```

### SSE vs WebSockets: When to Use Which

```
┌─────────────────────────────────┬──────────────────────────────────┐
│            SSE                  │           WebSocket              │
├─────────────────────────────────┼──────────────────────────────────┤
│ Server → client ONLY            │ Bidirectional                    │
│ Plain HTTP (no upgrade needed)  │ Requires upgrade + protocol      │
│ Automatic reconnection built-in │ Must implement reconnect yourself│
│ Works through HTTP/2 mux        │ Separate TCP connection          │
│ Simpler to implement            │ More complex, more powerful      │
├─────────────────────────────────┼──────────────────────────────────┤
│ Good for:                       │ Good for:                        │
│  Live feed / timeline updates   │  Chat (bidirectional)            │
│  Dashboard metrics              │  Collaborative editing           │
│  Progress bars                  │  Games                           │
│  Breaking news ticker           │  Live trading (send + receive)   │
│  Order status updates           │  Interactive real-time features  │
└─────────────────────────────────┴──────────────────────────────────┘

Rule of thumb:
  Client never needs to send real-time data? → SSE
  Client sends data too (messages, edits, moves)? → WebSocket
```

---

## Part 5: Stream Processing — Events as They Arrive

Stream processing is about doing computation on a continuous flow of events,
as opposed to waiting for a batch of data to accumulate.

### Batch vs Stream

```
Batch processing:
  "Every night at midnight, process all of today's events."
  Latency: up to 24 hours from event to result.

Stream processing:
  "Process each event within milliseconds of it occurring."
  Latency: milliseconds to seconds.

Same question, different systems:
  "How many users clicked the Buy button in the last hour?"
  Batch: run at 1 AM → results available at 1:15 AM
  Stream: continuously updated → always current within seconds
```

### Kafka Streams and Apache Flink

```
KAFKA STREAMS:
  Library (not a separate cluster) for stream processing on Kafka topics.
  Your code runs inside your own Java/Scala application.
  Stateful: can maintain counts, windows, join streams.
  Good for: moderate volume, simpler pipelines, you want to stay in the JVM.

APACHE FLINK:
  Separate distributed processing cluster.
  True streaming (event by event, not micro-batches).
  Extremely low latency (milliseconds).
  Complex windowing, stateful operators, exactly-once guarantees.
  Good for: high volume, complex analytics, strict latency requirements.
  Used by: Netflix, Uber, Alibaba, Lyft for real-time analytics.

SPARK STREAMING:
  Micro-batch processing (collects events for 100ms-1s, then processes batch).
  Not true streaming but good throughput.
  Good for: you already use Spark, throughput matters more than latency.
```

### Windowing: Processing Bounded Chunks of an Infinite Stream

An infinite stream has no natural "end." Windowing lets you compute
aggregations over time-bounded segments.

```
TUMBLING WINDOWS (fixed, non-overlapping):
  Divide time into fixed chunks. Each event belongs to exactly one window.

  Window 1: [00:00 - 01:00]  → process → emit count
  Window 2: [01:00 - 02:00]  → process → emit count
  Window 3: [02:00 - 03:00]  → process → emit count

  Use case: "Clicks per minute" — one result per minute.

SLIDING WINDOWS (overlapping):
  Windows slide forward by a smaller step than their size.

  Window size: 5 minutes, slide: 1 minute:
  [00:00 - 05:00] → emit
  [01:00 - 06:00] → emit
  [02:00 - 07:00] → emit

  Use case: "Rate of errors in the last 5 minutes, updated every minute"
            Smooths out spikes better than tumbling windows.

SESSION WINDOWS (activity-based):
  Group events that occur within an inactivity gap of each other.

  User events: click, click, [30 min gap], click, click
  → Session 1: first two clicks
  → Session 2: last two clicks (after inactivity timeout)

  Use case: user session analytics, e-commerce cart behavior.
```

### Stateful Processing

Not all stream processing is stateless (apply function to each event).
Often you need to maintain state across events:

```
Stateless: "For each payment event, send a notification email"
  → Each event is independent. No memory of past events needed.

Stateful: "Alert if a user makes > 5 failed login attempts in 10 minutes"
  → Must count failed attempts per user, within a rolling time window
  → Must remember past events to evaluate the current one

Flink stateful example:
  "Count distinct users who visited the product page in the last 5 minutes"

  For each page view event:
    1. Get current state for this window (set of user_ids)
    2. Add current user_id to set
    3. Emit current count (size of set)
    4. At window close: clear state for that window

  Flink stores this state durably (in RocksDB by default).
  Even if a node fails, state is recovered from checkpoint.
```

---

## Part 6: The Live Feed System — Putting It Together

Let's design a real-time sports scoreboard. Teams score, millions of
users see the update within 1 second.

### The Architecture

```
SCORE UPDATE FLOW:

  Official scorer's app
        │
        │  POST /api/score   (authenticated)
        ▼
  ┌─────────────┐
  │  Score API  │  ← validates, persists to DB
  │  Service    │
  └──────┬──────┘
         │
         │  publishes ScoreUpdated event
         ▼
  ┌─────────────┐
  │    Kafka    │  ← durable buffer, topic: "score-events"
  │  topic      │
  └──────┬──────┘
         │
         │  consumes events
         ▼
  ┌─────────────────┐
  │  WebSocket      │  ← fan-out service
  │  Server Pool    │  maintains ~100K WS connections each
  │  (N servers)    │
  └────────┬────────┘
           │  pushes to all connections
           │  subscribed to this game
           ▼
  ┌──────────────────────────────────────────────────────┐
  │  1M browser clients with open WebSocket connections  │
  │  See: "GOAL! 2-1 Real Madrid"                        │
  └──────────────────────────────────────────────────────┘

  Coordination between WebSocket servers:
  Each server subscribes to Redis Pub/Sub channel "game:{game_id}"
  Score API publishes to Redis → all WS servers receive → push to clients

CONNECTION LIFECYCLE:

  User opens app:
    1. Browser opens WebSocket to wss://scores.example.com/ws
    2. After handshake, client sends: {"subscribe": "game:12345"}
    3. Server records: game:12345 → [connection_a, connection_b, ...]
    4. Client receives all future score events for that game

  Score update arrives:
    1. Kafka consumer on WS server receives ScoreUpdated event
    2. Server looks up all connections subscribed to game:12345
    3. Pushes JSON event to each connection: {"game": 12345, "score": "2-1"}
    4. Client updates UI immediately

  User leaves:
    1. WebSocket disconnected
    2. Server removes from subscription map
    3. No more pushes for that game to this connection
```

### Twitter/X Timeline Refresh (Similar Pattern)

```
User follows 500 accounts.
Any of those accounts can tweet at any time.
The user must see new tweets quickly without polling.

Architecture:
  Tweet created → publish to Kafka topic "tweets"
  Fan-out service: for each tweet, look up author's followers
                   publish to each follower's personal queue
  WebSocket/SSE: client has open connection
                 when a tweet lands in their queue → push it
  Client: receives tweet event → prepends to timeline

This is the push-on-write model (fan-out at write time).
Contrast with pull-on-read (fan-in at read time — Instagram's old approach).

Push pros:  reads are instant (data already in your queue)
Push cons:  celebrities with 50M followers = 50M writes per tweet

Hybrid: push for users with < 1M followers, pull for celebrities.
```

---

## Part 7: WebRTC — Peer-to-Peer Audio and Video

For video calls (Zoom, Google Meet, WhatsApp calls), you want audio/video
data to flow directly between browsers without going through your servers.
That's WebRTC.

### The Three-Stage Problem

```
WebRTC solves three problems:

1. HOW DO PEERS FIND EACH OTHER? (Signaling)
   Peers start behind NAT/firewalls with no direct address.
   Solution: use your server (WebSocket or HTTP) to exchange connection
   parameters (called SDP — Session Description Protocol).

   Alice's browser ─── "I want to call Bob, here are my connection params" ──→ Server
   Server ─── "Bob, Alice wants to connect, here are her params" ──→ Bob's browser
   Alice ←───── "I accept, here are my params" ─────────────────── Bob

   Your server only relays these tiny metadata messages.
   The actual audio/video NEVER goes through your server (ideally).

2. HOW DO PEERS PUNCH THROUGH NAT? (ICE / STUN)
   Both peers are behind NAT routers with private IPs.
   They need to discover their public IP/port.

   STUN server: a simple server that tells you "your public IP is X.X.X.X:Y"
   ICE: protocol that finds the best path between two peers,
        trying direct connection first, then STUN, then TURN as fallback.

3. WHAT IF DIRECT CONNECTION FAILS? (TURN)
   Some corporate firewalls block WebRTC.
   TURN server: relay server that forwards data when direct fails.
   Now your server carries the media → bandwidth cost on you.

   +------------+
   | STUN/TURN  |  ← Usually a free/cheap service
   +------------+
        │ (only metadata / fallback relay)
   Alice ─────────────────────────────────── Bob
         ↑ Direct peer-to-peer media (ideal)
```

### When WebRTC vs When WebSockets for Live Video

```
WebRTC:
  + Peer-to-peer (server not in media path)
  + Low latency (< 200ms, designed for live communication)
  + Built-in adaptive bitrate, echo cancellation, jitter buffer
  - Complex to implement (ICE, STUN, TURN, signaling)
  - TURN relay costs if NAT traversal fails
  - Not suitable for 1-to-many broadcast (each peer = separate connection)

WebSocket for video:
  + Simple (server relays everything)
  + Works for server-side recording, moderation, AI processing
  - Higher latency (media goes through server)
  - Server pays all bandwidth costs
  - Doesn't scale to large numbers of participants easily

RTMP/HLS for live broadcast:
  + Great for 1-to-many (Twitch, YouTube Live)
  + Scales to millions of viewers via CDN
  - Higher latency (5-30 seconds for HLS)
  - Not interactive

Choose:
  1-on-1 or small group video call (< 10 people): WebRTC
  Large group with interaction: WebRTC via SFU (selective forwarding unit)
  Live broadcast to many viewers: RTMP ingest → HLS via CDN
```

---

## The Mental Models to Keep

```
1. "Real-time" for web = soft real-time = sub-second latency.
   Not hard real-time (that's embedded systems with deterministic OS).

2. HTTP cannot push. Use WebSockets for bidirectional.
   Use SSE for server-to-client only (simpler, fewer moving parts).

3. Scaling WebSockets requires coordination (Redis Pub/Sub or Kafka).
   Connection is stateful — where a user is connected matters.

4. Stream processing = compute on events as they arrive.
   Windowing = bound the infinite stream into computable chunks.
   Stateful processing = maintain memory across events.

5. For real-time feeds (sports, finance, social):
   The pattern is always: write → Kafka → fan-out → WebSocket/SSE → client.

6. WebRTC = peer-to-peer audio/video.
   Signaling goes through your server.
   Media ideally does not.
   TURN server is your fallback for unreachable peers.
```

---

## Mini Exercises

**1.** Design a live stock price ticker for a trading platform.
100,000 users are watching prices simultaneously. Prices update 100 times/second.
Sketch the data flow from exchange feed to user's browser.
What is the bottleneck? How do you handle it?

**2.** You are building a collaborative document editor (like Google Docs).
Two users can type simultaneously. Both see each other's changes in real-time.
What protocol do you use? What happens if one user's connection drops for
5 seconds and then reconnects? How do you merge their changes?

**3.** A notification system sends alerts to users (new follower, new like).
Users are rarely active. Alerts can arrive any time.
Compare: (a) polling every 30 seconds, (b) SSE, (c) WebSockets.
What is the trade-off for each? Which would you choose?

**4.** Your WebSocket server handles 500,000 concurrent connections on 5 servers
(100,000 each). You need to send a message to all users subscribed to "topic:news".
There are 300,000 of them, spread across all 5 servers.
How does the message get from the publisher to all 300,000 connections?
Draw the data flow.

---

## Navigation

| | |
|---|---|
| Previous | [20 — Data Systems](../20_data_systems/data_at_scale.md) |
| Next | [22 — Case Studies](../22_case_studies/theory.md) |
| Home | [README.md](../README.md) |
