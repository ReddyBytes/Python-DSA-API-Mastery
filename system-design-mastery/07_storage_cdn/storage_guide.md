# Where Does All That Data Actually Live?
## A Field Guide to Storage and CDN

> Every photo you've ever uploaded, every video you've ever streamed, every
> file attachment in every email — it lives somewhere specific, in a specific
> format, for very specific reasons. This guide explains why.

---

## The Setup: Three Problems, Three Solutions

Imagine you are building a product like Dropbox. Users upload files. You need
to store them. You open your laptop and think: "I'll just write them to disk."

That works on one server. Then you get 10,000 users. You need more servers.
Now which server has which file? What if a server crashes?

This is the storage problem. And the industry solved it three different ways,
each making different trade-offs.

---

## Part 1: Three Types of Storage

### 1. Block Storage — The Raw Hard Drive

Block storage is the closest thing to plugging a hard drive directly into
a computer. It gives you raw blocks of storage — no file structure, no metadata.
The operating system (or database) decides what to do with those blocks.

```
┌─────────────────────────────────────────────────────────┐
│                   Block Storage (EBS)                   │
│                                                         │
│  [ Block 0 ][ Block 1 ][ Block 2 ][ Block 3 ]...        │
│  Each block is a fixed chunk of bytes (e.g. 512 bytes)  │
│                                                         │
│  The OS formats it as ext4/NTFS/XFS                     │
│  Then you get a /dev/sda that looks like a local disk   │
│                                                         │
│  Attached to: ONE instance at a time                    │
│  Access via: low-level I/O (not HTTP)                   │
└─────────────────────────────────────────────────────────┘
```

**The mental model:** A hard drive screwed into your server. Fast, low-latency,
but only that one server can use it.

**AWS equivalent:** EBS (Elastic Block Store)
**Use cases:**
- The disk your database runs on (PostgreSQL, MySQL)
- The OS volume of a virtual machine
- Anything that needs POSIX filesystem semantics

**Characteristics:**
```
Speed:      Very fast (microseconds)
Access:     One machine at a time (mostly)
Mountable:  Yes — appears as /dev/sda, C:\, etc.
Over HTTP:  No
Scale:      Up to tens of TB per volume
Cost:       Moderate per GB
```

---

### 2. File Storage — The Shared Network Drive

File storage is what you get when multiple servers need to share a filesystem.
It exposes a directory tree with files and folders, accessible over the network.

```
┌───────────────────────────────────────────────────────────┐
│                   File Storage (EFS / NFS)                │
│                                                           │
│   /shared/                                                │
│     ├── app-config/                                       │
│     │     └── settings.json                              │
│     ├── user-uploads/                                     │
│     │     ├── alice/                                      │
│     │     └── bob/                                        │
│     └── logs/                                             │
│           └── 2024-01-15.log                             │
│                                                           │
│   Server A ──┐                                            │
│   Server B ──┼── all mount /shared and see same files    │
│   Server C ──┘                                            │
└───────────────────────────────────────────────────────────┘
```

**The mental model:** A network drive that multiple computers mount simultaneously.
When Server A writes a file, Server B can immediately read it.

**Protocols:** NFS (Linux), SMB/CIFS (Windows)
**AWS equivalent:** EFS (Elastic File System)
**Use cases:**
- Shared config files across multiple app servers
- Legacy applications that use the filesystem as storage
- CMS platforms that store uploaded media on disk

**Characteristics:**
```
Speed:      Good (milliseconds, slower than block)
Access:     Multiple machines simultaneously
Mountable:  Yes — appears as /mnt/shared
Over HTTP:  No
Scale:      Petabytes, but expensive
Cost:       Higher per GB than object storage
```

---

### 3. Object Storage — Files + Metadata via HTTP API

Object storage is the radical departure from the other two. There is no
filesystem. No directories (technically). No mounting. Just a flat namespace
of objects, each with a key and metadata, accessed entirely over HTTP.

```
┌──────────────────────────────────────────────────────────────┐
│                    Object Storage (S3)                       │
│                                                              │
│  Bucket: my-company-uploads                                  │
│                                                              │
│  Key: "users/alice/avatar.jpg"                               │
│  Data: [binary bytes of the image]                           │
│  Metadata: { content-type: image/jpeg, size: 45KB,          │
│              uploaded-by: alice, created: 2024-01-15 }       │
│                                                              │
│  Key: "videos/intro.mp4"                                     │
│  Data: [binary bytes of the video]                           │
│  Metadata: { content-type: video/mp4, size: 240MB }          │
│                                                              │
│  Access: GET https://bucket.s3.amazonaws.com/key            │
│          PUT https://bucket.s3.amazonaws.com/key            │
│                                                              │
│  Any machine, anywhere, over the internet                    │
└──────────────────────────────────────────────────────────────┘
```

**The mental model:** A giant dictionary where keys are file paths and values
are files. You access it with HTTP GET/PUT. No mounting. No servers to manage.

**Cloud equivalents:** AWS S3, Google Cloud Storage (GCS), Azure Blob Storage
**Use cases:** User uploads, static website assets, backups, logs, datasets

**Characteristics:**
```
Speed:      Slower per-request (100ms+), but massively parallel
Access:     Any machine, anywhere, over HTTP
Mountable:  Not natively (special tools like s3fs can fake it)
Over HTTP:  Yes — this is the entire interface
Scale:      Unlimited objects, exabyte scale
Cost:       Very cheap per GB ($0.023/GB/month on S3 standard)
```

---

### The Comparison at a Glance

```
┌──────────────────┬──────────────┬──────────────┬──────────────┐
│                  │    Block     │     File     │    Object    │
│                  │   (EBS)      │    (EFS)     │    (S3)      │
├──────────────────┼──────────────┼──────────────┼──────────────┤
│ Access method    │ Disk I/O     │ NFS/SMB      │ HTTP API     │
│ Filesystem       │ Yes (any)    │ Yes (shared) │ No           │
│ Multiple servers │ No (1 at a   │ Yes          │ Yes          │
│                  │ time)        │              │              │
│ Cost per GB/mo   │ ~$0.10       │ ~$0.30       │ ~$0.023      │
│ Max scale        │ ~64 TB/vol   │ Petabytes    │ Unlimited    │
│ Best for         │ DB volumes   │ Shared files │ Web content  │
└──────────────────┴──────────────┴──────────────┴──────────────┘
```

---

## Part 2: Why Object Storage Won the Web

When the web needed to store billions of profile pictures and petabytes of
video, object storage turned out to be the only thing that actually scaled.

Here is why:

### Reason 1: Unlimited Objects

A filesystem has inodes — there is a maximum number of files you can store,
regardless of disk space. Object storage has no such limit. Amazon S3
reportedly stores over 100 trillion objects. You cannot run out of "slots."

### Reason 2: HTTP Access Means No Infrastructure

With block or file storage, you need servers to mount the volumes and serve
the files. Object storage is just an HTTP endpoint. Your mobile app can
upload directly to S3. Your CDN can pull directly from S3. No file server
in the middle.

```
Traditional file serving:
  User → Your Server → File Server → Disk

Object storage:
  User → S3 (directly)
  User → CDN (which pulls from S3)
```

### Reason 3: Built-in Redundancy

S3 stores each object across multiple physical locations automatically.
The documented durability is 99.999999999% (11 nines). You did not build
any of that redundancy — it came with the service.

### Reason 4: Price

At $0.023 per GB per month, storing 1 TB on S3 costs about $23/month.
Running your own file server with equivalent redundancy would cost far more
in hardware, power, operations, and engineering time.

```
1 TB of user photos on S3:
  Storage: $23/month
  Ops: $0 (AWS manages hardware)
  Redundancy: 11-nines durability (free)

1 TB on your own server:
  Hardware: $200/month amortized
  Power + datacenter: $50/month
  Ops engineer time: significant
  Redundancy: you have to build it yourself
```

---

## Part 3: S3 Concepts You Need to Know Cold

### Buckets

A bucket is the top-level container. Think of it as a namespace.

```
Bucket names are globally unique across all AWS accounts:
  my-company-production-assets  ← valid
  my-company-dev-backups        ← valid

Bucket names become part of the URL:
  https://my-company-production-assets.s3.amazonaws.com/...
```

Rules: lowercase, 3-63 characters, globally unique, region-specific.

### Keys

The key is the full "path" to an object. S3 is actually flat — there are no
real directories. The slashes in keys are just characters, but the console
displays them as folder hierarchy.

```
Key:  "users/alice/2024/avatar.jpg"
      ← this looks like a folder path
      ← it is actually just a string with slashes in it
      ← S3 treats it as a single flat key

GET s3://my-bucket/users/alice/2024/avatar.jpg
→ S3 looks up that exact string as the key
```

### Presigned URLs

This is one of the most important patterns. A presigned URL is a time-limited,
cryptographically signed URL that grants temporary access to an object without
requiring the requester to have AWS credentials.

```
How it works:

  1. Your server asks S3: "Give me a signed URL for object X,
     valid for 15 minutes, for PUT operation"

  2. S3 returns a URL like:
     https://my-bucket.s3.amazonaws.com/users/alice/avatar.jpg
     ?X-Amz-Algorithm=AWS4-HMAC-SHA256
     &X-Amz-Credential=...
     &X-Amz-Expires=900
     &X-Amz-Signature=<hmac_signature>

  3. You give this URL to the client (browser/mobile app)

  4. The client does PUT directly to that URL
     → uploads straight to S3, no data touches your server

  5. After 15 minutes, the URL expires and is useless
```

Why this matters: your app server doesn't become a file transfer bottleneck.
1 GB video uploads bypass your server entirely.

### Versioning

With versioning enabled, S3 keeps every version of every object instead of
overwriting.

```
Bucket: my-documents (versioning enabled)

PUT users/contract.pdf  → version ID: a1b2c3
PUT users/contract.pdf  → version ID: d4e5f6  (new version)
PUT users/contract.pdf  → version ID: g7h8i9  (newer version)

GET users/contract.pdf            → returns g7h8i9 (latest)
GET users/contract.pdf?versionId=a1b2c3 → returns original

DELETE users/contract.pdf         → adds a "delete marker"
                                    previous versions still exist
```

Use versioning for: important documents, backup protection, audit trails.
Do not use versioning for: massive high-churn objects (costs multiply fast).

### Lifecycle Policies

Automatically transition or delete objects based on age. This is how you
manage storage costs at scale.

```
Example lifecycle policy for a backup bucket:

  Day 0:    Object uploaded → S3 Standard ($0.023/GB)
  Day 30:   Transition → S3 Standard-IA ($0.0125/GB)
            (Infrequent Access — cheaper, but retrieval costs more)
  Day 90:   Transition → S3 Glacier ($0.004/GB)
            (For archival — retrieval takes hours)
  Day 365:  DELETE (or move to Deep Archive at $0.00099/GB)

Storage classes (cheapest to most expensive, slowest to fastest):
  Glacier Deep Archive  → $0.00099/GB  retrieval: 12 hours
  Glacier               → $0.004/GB   retrieval: 1-12 hours
  Standard-IA           → $0.0125/GB  retrieval: instant, per-request fee
  Standard              → $0.023/GB   retrieval: instant, no fee
  Intelligent-Tiering   → automatic   moves between tiers based on access
```

---

## Part 4: CDN — Making Your Content Fast Everywhere

### The Problem: Physics

Your S3 bucket lives in us-east-1 (Northern Virginia). A user in Sydney,
Australia requests a 5 MB image. That request travels:

```
Sydney → Pacific Ocean cable → Los Angeles → Virginia
Distance: ~16,000 km
Round-trip latency: ~200ms just for the network

Then: S3 reads the file, sends 5 MB back across the same route
Total time: 1-3 seconds for something that should be instant
```

You cannot make light travel faster. But you can move the data closer.

### The Solution: A Network of Servers Near Your Users

A CDN (Content Delivery Network) is exactly that: dozens or hundreds of
servers (called Points of Presence, or PoPs) distributed globally, caching
your content close to users.

```
Without CDN:                    With CDN:

  [User in Sydney]                [User in Sydney]
       │                               │
  ~200ms latency                  ~10ms latency
       │                               │
  [S3 in Virginia]              [CDN PoP in Sydney]
                                       │
                               (cache hit: serves locally)
                               (cache miss: fetches from S3 once,
                                caches locally for future users)
```

Major CDNs: Cloudflare, AWS CloudFront, Fastly, Akamai, Google Cloud CDN.

### Origin Pull vs Pre-pushed Content

**Origin Pull (lazy caching):**
```
1. User requests /images/banner.jpg
2. CDN PoP checks its cache → miss (first request)
3. CDN PoP fetches from your origin server (S3 or your app)
4. CDN PoP stores the response in its cache
5. CDN PoP returns response to user

Next user in same region:
1. Requests /images/banner.jpg
2. CDN PoP checks cache → HIT
3. Returns immediately, no origin request needed

This is the default mode for most CDNs.
```

**Pre-pushed Content (eager caching):**
```
You explicitly upload content to CDN edge locations before
any user requests it.

Use for:
  - Major product launches (cache before traffic hits)
  - Software releases (distribute binary to all PoPs)
  - Critical assets you know everyone will need

Less common — most CDNs use origin pull.
```

### Cache-Control Headers: Teaching the CDN When to Cache

When your origin server (or S3) sends a response, it includes headers that
tell the CDN (and browsers) how long to cache the content.

```
Response headers:

  Cache-Control: public, max-age=31536000, immutable
  │               │      │                  └── never changes (skip revalidation)
  │               │      └── cache for 1 year (in seconds)
  │               └── any cache (CDN, browser) can store this
  └── the header name

Common patterns:

  Static assets (JS/CSS with content hash in filename):
    Cache-Control: public, max-age=31536000, immutable
    → Cache forever — filename changes when content changes

  Images:
    Cache-Control: public, max-age=86400
    → Cache for 1 day

  API responses:
    Cache-Control: no-store
    → Never cache — always fresh from origin

  HTML pages:
    Cache-Control: public, max-age=0, must-revalidate
    → Always check origin, but serve stale if origin unreachable
```

The key insight: static assets get long TTLs by putting a content hash in the
filename (e.g. `bundle.a3f9c2.js`). If the file changes, the filename changes,
so the CDN treats it as a brand new object.

### Cache Invalidation: When Content Changes Without a New Filename

Sometimes you need to purge content from the CDN before its TTL expires.

```
Scenarios:
  - You deployed bad CSS that breaks the site
  - A user avatar changed but URL is stable
  - A config file at a fixed URL was updated

Invalidation options:

  1. Path invalidation:
     Send request to CDN: "purge /images/banner.jpg from all PoPs"
     Most CDNs support this. Usually costs a small fee.

  2. Versioned URLs (better):
     /images/banner-v2.jpg
     Point your HTML to the new version.
     Old URL stays cached (but nobody uses it anymore).
     New URL is fetched fresh everywhere.

  3. Query string busting:
     /images/banner.jpg?v=2
     CDN treats it as a different object.
     Works, but messier.

The best strategy: use content-hashed filenames so you rarely need invalidation.
```

### When to Use a CDN vs When Not To

```
USE CDN for:                          DO NOT USE CDN for:
────────────────────────────────────  ──────────────────────────────────
Static files (JS, CSS, images)        Dynamic API responses (JSON data)
Videos and large media                Personalized pages per user
File downloads                        Real-time data (stock prices, chat)
Static website HTML                   Authenticated/private content
Software packages/binaries            Write operations (POST/PUT)
Font files                            Session-dependent content

Why not dynamic API responses?
  The whole point of a CDN is to return the same cached response
  to everyone. If alice's /profile is different from bob's /profile,
  you CANNOT cache it — or you serve alice's data to bob.
  (Unless you use sophisticated cache key rules, which is complex.)
```

---

## Part 5: What to Store Where

This is what gets asked in design interviews. Train your intuition:

### User Profile Photos

```
STORE IN:   Object storage (S3) + CDN in front of it

Why S3?     Unlimited scale, cheap, HTTP access
Why CDN?    Profile photos are read far more than written.
            Once cached, they serve from edge in milliseconds.

Flow:
  Upload:  User → presigned URL → S3
  Display: User → CDN edge → (cache miss) → S3 origin → cache

URL pattern: https://cdn.myapp.com/avatars/user-12345.jpg
CDN TTL:     1 day (or content-hash the filename for longer)
```

### Database Backups

```
STORE IN:   Object storage (S3 Glacier / Standard-IA)

Why?        Backups are written once, read very rarely (only when
            disaster strikes). Object storage is cheap and durable.
            You do not need fast access — you need cheap + safe.

Lifecycle:
  Day 0:    S3 Standard    (just in case you need it soon)
  Day 7:    S3 Standard-IA (less likely to need now)
  Day 30:   S3 Glacier     (archive — retrieval in hours is fine)
  Day 365:  Deep Archive or DELETE per compliance policy
```

### Uploaded Documents (PDFs, Word files, etc.)

```
STORE IN:   Object storage (S3 Standard)

Pattern:
  User uploads → your server validates (virus scan, size check)
               → your server PUTs to S3
               → store S3 key in your database
               → to serve: generate presigned GET URL (15-60 min)

Do NOT:     Serve documents directly from your app server
            (memory-intensive, bandwidth from your instance)
Do NOT:     Make documents public unless they should be public
            (use presigned URLs for access control)
```

### Application Configuration

```
STORE IN:   Environment variables, AWS Secrets Manager,
            or HashiCorp Vault

NOT IN:     Object storage

Why not S3?
  1. Config changes require deploys, not file uploads
  2. Secrets in S3 are too easy to accidentally expose (public bucket)
  3. No versioning tied to your deployment pipeline
  4. Environment variables are the 12-factor app standard

Wrong:  Read db_password from s3://my-config/db.json at startup
Right:  Read DATABASE_URL from environment variable
```

---

## Part 6: The Presigned Upload Pattern

This is the pattern you want to know for design interviews. It comes up
any time you design a system with user-uploaded content.

### The Naive Approach (and Why It Fails)

```
Naive: User → POST /upload → Your Server → S3

Problems:
  - 100 users each uploading 100 MB video = 10 GB through your server
  - Your server needs 10 GB of memory/bandwidth simultaneously
  - Your server becomes the bottleneck for all uploads
  - You pay for EC2 bandwidth twice (user → server, server → S3)
```

### The Presigned URL Pattern (Correct Approach)

```
Step 1: Client asks your server for an upload URL

  Client: POST /api/get-upload-url
          { filename: "vacation.mp4", content_type: "video/mp4" }

Step 2: Your server generates a presigned S3 URL

  Server: calls S3 API:
          generate_presigned_url(
            operation='put_object',
            bucket='user-uploads',
            key=f'users/{user_id}/{uuid}.mp4',
            expires_in=3600,          # URL valid for 1 hour
            content_type='video/mp4'
          )
          → returns signed URL

  Server returns to client:
          { upload_url: "https://s3.amazonaws.com/user-uploads/users/42/abc.mp4
                         ?X-Amz-Signature=...",
            object_key: "users/42/abc.mp4" }

Step 3: Client uploads directly to S3

  Client: PUT <that URL>
          Content-Type: video/mp4
          [video bytes]

  → Goes directly to S3, never touches your server

Step 4: Client notifies your server the upload is complete

  Client: POST /api/confirm-upload
          { object_key: "users/42/abc.mp4" }

  Server: verifies object exists in S3
          saves reference in database
          triggers processing (thumbnail generation, etc.)
```

Visually:

```
  ┌────────┐   1. Get upload URL   ┌────────────┐
  │        │ ───────────────────→  │            │
  │ Client │                       │ App Server │
  │        │ ←───────────────────  │            │
  └────────┘   2. Presigned URL    └────────────┘
      │                                  │
      │                           (generates URL
      │                            via S3 API,
      │                            never moves data)
      │
      │   3. PUT directly to S3
      ▼
  ┌────────┐
  │   S3   │
  │ bucket │
  └────────┘
      │
      │   4. Upload complete → notify app server
      │      App server saves reference to DB
```

**Benefits:**
- Your server handles only metadata (URLs, confirmations) — tiny payloads
- S3 handles the actual data transfer with its own massive bandwidth
- Scales to thousands of simultaneous large uploads without touching your servers
- You still control access (the presigned URL is the access grant)

---

## The Mental Models to Keep

```
Storage type decision tree:

  Does it need to be a disk/filesystem for an OS or DB?
    → Block storage (EBS)

  Do multiple servers need concurrent access to shared files?
    → File storage (EFS/NFS)

  Is it web-accessible content, user uploads, or backups?
    → Object storage (S3)


CDN decision:
  Static content that all users see the same way?  → Use CDN
  Dynamic content personalized per user?           → Skip CDN
  Large media files?                               → CDN is critical
  API JSON responses?                              → Usually no CDN


Cost ordering (cheapest to most expensive per GB):
  Glacier Deep Archive → Glacier → S3 Standard-IA → S3 Standard
  → EFS → EBS

  Use lifecycle policies to automatically move aging data down the chain.
```

---

## Mini Exercises

**1.** You are designing Instagram. Users upload photos. Where do photos live?
How do you serve them to followers? Sketch the upload flow and the read flow.

**2.** Your company stores 10 TB of database backups. Currently on EBS snapshots
at $0.05/GB. You haven't restored a backup in 2 years. How would you reduce
this cost using lifecycle policies?

**3.** A user's profile avatar URL is `https://cdn.myapp.com/avatars/user-99.jpg`
with a 7-day CDN TTL. The user updates their avatar. How do you make sure
people see the new avatar quickly? What is the best strategy?

**4.** Your engineering team suggests: "Just serve user-uploaded PDFs directly
from the app server — it's simpler." List three reasons why presigned URLs
to S3 are better for production use.

---

## Navigation

| | |
|---|---|
| Previous | [06 — Caching](../06_caching/the_art_of_caching.md) |
| Next | [08 — Load Balancing](../08_load_balancing/traffic_manager.md) |
| Home | [README.md](../README.md) |
