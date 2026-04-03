# 🏛️ High Level Design (HLD)

> HLD is about designing the architecture of a system — what services exist, how they
> communicate, where data lives, and how the system handles scale, failures, and growth.
> It answers "what does the system look like from 10,000 feet?"

---

## 📋 Contents

```
1.  What is HLD and when does it apply?
2.  The HLD interview framework (45 minutes)
3.  Step 1 — Requirements clarification
4.  Step 2 — Capacity estimation
5.  Step 3 — High-level architecture
6.  Step 4 — Deep dives
7.  Step 5 — Bottlenecks and trade-offs
8.  Architecture patterns
9.  System communication patterns
10. Data flow design
11. HLD of URL Shortener (complete walkthrough)
12. HLD of Twitter / Social Feed
13. HLD of WhatsApp / Messaging
14. HLD of Netflix / Video Streaming
15. HLD of Uber / Ride Sharing
16. Common design decisions cheatsheet
```

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
HLD framework (clarify→estimate→architecture→deep dive→trade-offs) · capacity estimation · communication patterns (sync vs async)

**Should Learn** — Important for real projects, comes up regularly:
case study patterns (fan-out/geo-indexing/streaming) · architecture selection (monolith vs microservices vs event-driven)

**Good to Know** — Useful in specific situations, not always tested:
design decisions matrix · bottleneck identification

**Reference** — Know it exists, look up syntax when needed:
detailed case study walkthroughs (URL shortener/Twitter/WhatsApp/Netflix/Uber) · cost estimation

---

## 1. What is HLD?

```
LLD (Low Level Design):   How is this service built internally?
                          Classes, methods, design patterns
                          → "What does the code look like?"

HLD (High Level Design):  How does the overall system work?
                          Services, databases, queues, caches
                          → "What does the architecture look like?"
```

**HLD deals with:**
- Which services exist and what they do
- How services communicate (sync vs async)
- Where data is stored (SQL, NoSQL, object storage)
- How the system scales (horizontal, sharding, caching)
- How the system handles failures (redundancy, circuit breakers)
- Trade-offs made and why

---

## 2. The HLD Interview Framework (45 Minutes)

```
Timeline:
  0-5  min:  Requirements clarification
  5-10 min:  Capacity estimation (back-of-envelope)
  10-20 min: High-level architecture diagram
  20-35 min: Deep dives (2-3 components)
  35-45 min: Bottlenecks, trade-offs, follow-up questions
```

**The golden rule:** Never jump straight to design. Requirements first, always.

---

## 3. Step 1 — Requirements Clarification

Ask questions before drawing anything.

### Functional Requirements
```
"What should the system do?"

Template questions:
  - Who are the users? (end users, developers via API, admins)
  - What are the core user actions?
  - What is out of scope? (explicitly narrow it)
  - Are there mobile clients? Web? Both?
  - Real-time or eventually consistent is acceptable?
```

### Non-Functional Requirements
```
"What quality attributes matter?"

  Scale:        How many users? DAU / MAU?
  Traffic:      Reads per second? Writes per second?
  Latency:      P99 acceptable latency for core operations?
  Availability: "five nines" or "three nines"?
  Consistency:  Can users see stale data? By how much?
  Durability:   Can data be lost? For how long?
  Geography:    Single region? Multi-region?
```

### Example — URL Shortener
```
Functional (agreed):
  ✓ Create short URL from long URL
  ✓ Redirect to long URL given short URL
  ✓ Custom aliases (optional)
  ✓ Expiration (optional)

Out of scope:
  ✗ User accounts / authentication
  ✗ Analytics dashboard (just basic click count)

Non-functional:
  - 100M URLs created/day
  - 10:1 read/write ratio → 1B redirects/day
  - Low latency redirects (P99 < 100ms)
  - 99.9% availability
  - URLs valid for 10 years
```

---

## 4. Step 2 — Capacity Estimation

**Always do this.** It drives architecture decisions.

### Template
```
1. Calculate write QPS
2. Calculate read QPS
3. Calculate storage (per record × records/day × retention)
4. Calculate bandwidth (QPS × avg payload size)
5. Identify bottlenecks (CPU? DB? Bandwidth? Memory?)
```

### URL Shortener Estimation
```
Writes:
  100M URLs/day ÷ 86,400s/day = ~1,160 writes/sec
  Peak (3×): ~3,500 writes/sec

Reads:
  1B redirects/day ÷ 86,400s = ~11,574 reads/sec
  Peak (3×): ~35,000 reads/sec

Storage per URL record:
  long_url:  200 bytes average
  short_code: 7 bytes
  created_at: 8 bytes
  expire_at:  8 bytes
  click_count: 8 bytes
  Total: ~250 bytes → round to 500 bytes with overhead

Storage growth:
  100M records/day × 500 bytes = 50 GB/day
  50 GB × 365 × 10 years = ~182 TB total

Bandwidth:
  Writes: 1,160 × 500 bytes = ~580 KB/s
  Reads: 11,574 × 500 bytes = ~5.8 MB/s (negligible for redirects)

Key insight:
  → Read-heavy (10:1) — optimize for reads
  → 35K reads/sec is Redis territory (cache hot URLs)
  → 182 TB is manageable with sharded DB over 10 years
```

### Key Numbers to Memorize
```
Seconds in a day:           86,400 (~100K for rough math)
Seconds in a month:         2.6M
Seconds in a year:          31.5M

Storage quick guide:
  1 million records × 1 KB = 1 GB
  1 billion records × 1 KB = 1 TB
  1 billion records × 1 MB = 1 PB

QPS quick guide:
  1M requests/day  = ~12 req/s
  10M requests/day = ~120 req/s
  100M/day         = ~1,200 req/s
  1B/day           = ~12,000 req/s
```

---

## 5. Step 3 — High-Level Architecture

Draw a simple block diagram first. Expand from there.

### Generic Web Architecture
```
                        ┌─────────────┐
                        │     DNS     │
                        └──────┬──────┘
                               │
                        ┌──────▼──────┐
                        │     CDN     │  ← static assets
                        └──────┬──────┘
                               │
Client ────────────────→ ┌─────▼─────┐
                         │  Load     │
                         │ Balancer  │
                         └─────┬─────┘
                    ┌──────────┼──────────┐
               ┌────▼────┐ ┌──▼───┐ ┌────▼────┐
               │ App     │ │ App  │ │ App     │
               │ Server 1│ │ Svr 2│ │ Server 3│
               └────┬────┘ └──┬───┘ └────┬────┘
                    └─────────┼──────────┘
                         ┌────▼────┐
                    ┌────┤  Cache  ├────┐
                    │    │ (Redis) │    │
                    │    └─────────┘    │
             ┌──────▼──────┐    ┌───────▼──────┐
             │  Primary DB │    │  Read Replica│
             └─────────────┘    └──────────────┘
```

### Service-Oriented Architecture
```
                     API Gateway
                         │
          ┌──────────────┼──────────────┐
          │              │              │
   ┌──────▼──────┐ ┌─────▼──────┐ ┌────▼──────┐
   │   User      │ │  Order     │ │ Payment   │
   │  Service    │ │  Service   │ │ Service   │
   └──────┬──────┘ └─────┬──────┘ └────┬──────┘
          │              │              │
   ┌──────▼──────┐ ┌─────▼──────┐ ┌────▼──────┐
   │  Users DB   │ │  Orders DB │ │Payments DB│
   └─────────────┘ └────────────┘ └───────────┘
                         │
                  ┌──────▼──────┐
                  │   Message   │
                  │    Queue    │
                  │  (Kafka)    │
                  └──────┬──────┘
                  ┌──────▼──────┐
                  │Notification │
                  │  Service    │
                  └─────────────┘
```

---

## 6. Step 4 — Deep Dives

After the overview, pick 2-3 components to explain in detail.

### What to deep-dive on:
```
1. The most complex / critical path
   Example: For Twitter — how is the home timeline generated?

2. The part that's different from standard patterns
   Example: For Uber — real-time location matching algorithm

3. Where the interviewer pushes ("how would you scale X?")
```

### Common deep-dive topics:
```
Database design:
  - Table schema / document structure
  - Indexing strategy (what queries need indexes?)
  - Sharding key choice and its implications

Caching strategy:
  - What to cache? (hot paths, computed results)
  - Cache invalidation (TTL vs event-driven)
  - Cache aside vs read-through vs write-through

API design:
  - REST endpoints
  - Request/response payloads
  - Pagination strategy (cursor vs offset)
  - Rate limiting

Message queue usage:
  - Why async here? (decoupling, traffic smoothing)
  - Topic partitioning strategy
  - Consumer group design
  - Dead letter queue handling
```

---

## 7. Step 5 — Bottlenecks and Trade-offs

Always conclude by identifying:

```
1. Where are the bottlenecks?
   "At 100K writes/sec, the single DB becomes the bottleneck.
    We'd shard by user_id."

2. What trade-offs did you make?
   "We chose eventual consistency for the feed.
    Users might see posts up to 5s late.
    That's acceptable — the alternative is complex distributed locking."

3. What would you do differently at 10× scale?
   "At 10× we'd need a dedicated search service (Elasticsearch),
    separate read and write paths (CQRS), and multi-region replication."

4. What monitoring/alerts would you add?
   "P99 latency on DB queries, cache hit ratio, queue depth,
    error rate per service."
```

---

## 8. Architecture Patterns

### Monolith
```
Single deployable unit. All services in one process.

Pros:
  Simple to develop, test, deploy
  No network overhead between components
  Easy transactions (same DB, same process)

Cons:
  Scaling = scale the whole thing
  Long build/test cycles as it grows
  One bug can take down everything
  Tech debt accumulates in a ball of mud

Use when: startup, small team, simple domain, <50 engineers
```

### Microservices
```
Each service is independently deployable, owns its data.

Pros:
  Independent scaling (scale only what's hot)
  Independent deployment (teams move faster)
  Technology diversity possible
  Fault isolation (one service down ≠ all down)

Cons:
  Distributed systems complexity
  Network calls instead of function calls (latency + failures)
  Distributed transactions are hard
  Operational overhead (K8s, service mesh, tracing)

Use when: large team (>50 eng), different scale requirements per service,
          need independent deployment cadences
```

### Event-Driven Architecture
```
Services communicate through events (Kafka/SNS/SQS).

Pros:
  Loose coupling (producer doesn't know consumers)
  Natural buffer for traffic spikes
  Easy to add new consumers without changing producer
  Audit trail of all events

Cons:
  Eventual consistency (consumers process async)
  Harder to debug (correlation IDs needed)
  Complex error handling (dead letter queues, retries)
  Out-of-order event handling

Use when: high write throughput, fan-out (one event → many handlers),
          decoupled teams, audit log needed
```

### CQRS (Command Query Responsibility Segregation)
```
Separate read model from write model.

Write path:
  Command → Validate → Write to DB → Emit event

Read path:
  Query → Read-optimized view (denormalized, cached)

     ┌─────────┐  Command  ┌──────────────┐
     │ Client  │──────────→│ Command Svc  │──→ Write DB
     │         │           └──────┬───────┘
     │         │              Event│
     │         │           ┌──────▼───────┐
     │         │  Query    │ Projection   │──→ Read DB
     │         │←──────────│ (Read Model) │    (denormalized)
     └─────────┘           └──────────────┘

Use when: complex domain, high read/write ratio difference,
          different scale needs for reads vs writes
```

---

## 9. System Communication Patterns

### Synchronous (request-response)
```
REST:
  HTTP verbs: GET, POST, PUT, DELETE, PATCH
  Good for: CRUD operations, public APIs
  Challenge: tight coupling, cascading failures

gRPC:
  Binary protocol (Protocol Buffers), HTTP/2
  Good for: internal services, high throughput, streaming
  Challenge: less human-readable, harder to debug

GraphQL:
  Client specifies exactly what data it needs
  Good for: mobile clients (save bandwidth), complex queries
  Challenge: N+1 queries, caching harder
```

### Asynchronous (message-based)
```
Message Queue (RabbitMQ, SQS):
  Point-to-point: one message → one consumer
  Good for: task queues, work distribution
  Example: order processing, email sending

Event Streaming (Kafka):
  Publish-subscribe: one event → many consumers
  Replay-able, partitioned, durable
  Good for: event sourcing, audit logs, fan-out
  Example: user activity stream, CDC (change data capture)
```

### Communication choice guide
```
Scenario                      Use
─────────────────────────────────────────────────────
User-facing API               REST or GraphQL
Internal service to service   gRPC (low latency, typed)
Decoupled async processing    Message queue (RabbitMQ/SQS)
Fan-out (many consumers)      Event streaming (Kafka)
Real-time push to client      WebSockets or SSE
Batch processing              Queue + worker pool
```

---

## 10. Data Flow Design

### Read-heavy pattern
```
Client → Cache check
           ↓ miss
        Database → populate cache → return

Optimization layers:
  1. Application cache (in-process, e.g., Python dict with TTL)
  2. Distributed cache (Redis/Memcached)
  3. Read replicas (DB load distribution)
  4. CDN (for public, static-enough data)
```

### Write-heavy pattern
```
Client → Validate → Write to Queue → Return ack
                         ↓
                     Consumer → Write to DB
                              → Update cache
                              → Notify downstream

Options:
  Write-through cache: write to cache + DB simultaneously
  Write-behind cache:  write to cache, async to DB
  Write-ahead log:     log every write for durability
```

### Fan-out patterns
```
Fan-out on write (push model):
  When user posts → immediately push to all followers' feeds
  + Fast reads (pre-computed)
  - Slow writes (celebrity problem: Beyoncé has 100M followers)
  Use for: users with small follower count

Fan-out on read (pull model):
  When user checks feed → pull from all followed users
  + Fast writes
  - Slow reads (must query all followed users)
  Use for: celebrity users

Hybrid:
  Small follower count → fan-out on write
  Large follower count (> 10K) → fan-out on read
  Twitter uses this hybrid approach
```

---

## 11. HLD: URL Shortener (Complete Walkthrough)

### Requirements
```
Functional:
  - Create short URL → returns 7-char code (e.g., bit.ly/abc1234)
  - Redirect: GET /{short_code} → 301/302 to long URL
  - Optional: custom alias, expiration

Non-functional:
  - 100M creations/day, 1B redirects/day
  - P99 redirect < 100ms
  - 99.9% availability
  - 10 year retention
```

### High-Level Architecture
```
                     ┌──────────────┐
                     │   Client     │
                     └──────┬───────┘
                            │
                     ┌──────▼───────┐
                     │ API Gateway  │  (rate limiting, auth)
                     └──────┬───────┘
                     ┌──────▼───────┐
                     │ Load Balancer│
                     └──────┬───────┘
              ┌─────────────┴─────────────┐
       ┌──────▼──────┐             ┌──────▼──────┐
       │  URL Create │             │  Redirect   │
       │  Service    │             │  Service    │
       └──────┬──────┘             └──────┬──────┘
              │                           │
       ┌──────▼──────┐             ┌──────▼──────┐
       │  ID         │             │  Redis      │  ← hot URLs cached
       │  Generator  │             │  Cache      │
       │  (Snowflake)│             └──────┬──────┘
       └─────────────┘                    │ miss
                                   ┌──────▼──────┐
                                   │  URL Store  │  ← sharded
                                   │  (MySQL /   │
                                   │   Cassandra)│
                                   └─────────────┘
```

### Database Design
```sql
urls (
    short_code   CHAR(7)      PRIMARY KEY,
    long_url     TEXT         NOT NULL,
    user_id      BIGINT,
    created_at   TIMESTAMP    DEFAULT NOW(),
    expires_at   TIMESTAMP,
    click_count  BIGINT       DEFAULT 0
)

Index: short_code → primary key lookup
Sharding: by short_code (hash-based)
```

### Short Code Generation
```
Option 1: Base62 encoding of auto-increment ID
  ID = 12345 → Base62 → "dnh"
  Pros: simple, unique
  Cons: predictable, counter is a SPOF

Option 2: Random + uniqueness check
  Generate 7 random chars → check DB → retry if collision
  Pros: unpredictable
  Cons: DB roundtrip, collision rate grows with scale

Option 3: Distributed ID generator (Snowflake)
  64-bit ID → Base62 → 7-char code
  Timestamp + machine_id + sequence
  Pros: unique, sortable, no DB lookup
  Cons: clock skew handling needed

→ Use Option 3 for production scale
```

### Redirect Flow
```
GET /abc1234
  1. Check Redis: O(1) lookup
     → HIT:  301 redirect → long_url (cached in browser)
     → MISS: query DB, populate Redis, return 302 redirect
  2. Async: increment click_count (don't block redirect)

Why 301 vs 302?
  301 Permanent → browser caches, reduces server load
                  but you lose click analytics
  302 Temporary → server sees every redirect (analytics work)
                  but more load
  → Use 302 for analytics, 301 for pure perf
```

---

## 12. HLD: Twitter / Social Feed

### Core challenge: Home timeline at scale

```
Write path:
  User posts tweet
       ↓
  Tweet Service → Writes to Tweets table
       ↓
  Fan-out Service → Kafka (tweet.created event)
       ↓
  Timeline Workers (consumer group)
       ↓
  For each follower → prepend tweet_id to follower's timeline cache
  (Redis sorted set, sorted by timestamp)

Read path:
  User opens app
       ↓
  Timeline Service → Read from Redis timeline cache (their pre-built feed)
       ↓
  Hydration Service → Fetch tweet details + user info (parallel)
       ↓
  Return paginated feed

Celebrity problem (Kylie Jenner, 300M followers):
  → Do NOT fan-out on write for celebrities
  → On timeline read: merge pre-built cache + fetch latest celebrity tweets
  Threshold: followers > 10,000 → on-read inclusion
```

### Architecture
```
Tweet Write:
  Client → API GW → Tweet Service → MySQL (tweets)
                              ↓
                           Kafka (tweet.created)
                              ↓
                     Fan-out Workers
                         ↙         ↘
               Regular users      Celebrities
               (write to         (skip, pulled
               timeline cache)    at read time)

Timeline Read:
  Client → API GW → Timeline Service → Redis (user's feed)
                                              ↓ hydrate
                                       Tweet Service (batch)
                                       User Service (batch)
```

---

## 13. HLD: WhatsApp / Messaging

### Core challenge: Reliable message delivery to possibly offline user

```
Message states:
  SENT → DELIVERED → READ
  (server ack) (device ack)  (read receipt)

Architecture:
  Sender → Chat Server → Message Queue
                              ↓
                       Message Store (Cassandra)
                              ↓
                       Push to recipient (WebSocket / FCM/APNs)
                         ├─ Online: deliver via persistent WebSocket
                         └─ Offline: store + push notification

Message schema (Cassandra):
  Partition key: conversation_id
  Sort key:      message_id (Snowflake — sortable by time)
  Columns:       sender_id, content, type, created_at, status

Why Cassandra?
  → High write throughput (WAL + memtable)
  → Time-series access pattern (latest messages first)
  → Multi-region replication

Delivery guarantee:
  → At-least-once + dedup on client side
  → Message ID used to deduplicate on recipient
```

---

## 14. HLD: Netflix / Video Streaming

### Core challenge: Serve high-quality video to millions concurrently

```
Upload path (content team):
  Raw video → Transcoding Service (multiple resolutions: 4K, 1080p, 720p, ...)
            → Chunking (2-4 second segments, HLS/DASH format)
            → S3 (origin storage)
            → CDN (pre-pushed to edge nodes globally)

Playback path (user):
  Open Netflix → Content discovery (recommendation service)
  Press play   → Manifest request → CDN (m3u8 playlist)
  Streaming    → Adaptive bitrate (ABR): client measures bandwidth,
                 selects appropriate quality chunk in real-time

CDN strategy:
  Popular content: pre-pushed to all edge nodes
  Long-tail content: pull-through (first request fetches from origin)
  → Netflix runs its own CDN (Open Connect) for top content

Key insight:
  Netflix uses S3 + CDN for 99% of traffic
  Database (MySQL/Cassandra) is only used for metadata, not video bytes
```

---

## 15. HLD: Uber / Ride Sharing

### Core challenge: Match riders to nearby drivers in real-time

```
Driver location update:
  Driver app sends GPS every 4s → WebSocket
       ↓
  Location Service → Redis GeoSet (geospatial index)
  (lat/lng stored per driver_id)

Rider match flow:
  Rider requests ride → Matching Service
       ↓
  GEORADIUS query: find drivers within X km
       ↓
  Filter: available drivers only
       ↓
  Rank by ETA (straight-line distance as proxy)
       ↓
  Offer to top driver → accept/reject (timeout 10s)
       ↓
  If rejected → next driver in ranked list
       ↓
  Match confirmed → notify both parties

Location storage:
  Redis GeoSet: GEOADD drivers <lng> <lat> <driver_id>
                GEORADIUS drivers <rider_lng> <rider_lat> 5 km
  → O(N+log(M)) where M = members in sorted set

Supply/demand:
  Surge pricing model: if (demand/supply) > threshold → surge multiplier
  Supply = available drivers in area
  Demand = open ride requests in area
```

---

## 16. Common Design Decisions Cheatsheet

```
Data storage:
  User accounts, transactions:      MySQL / PostgreSQL (ACID)
  User sessions, rate limiting:     Redis
  Logs, events, time-series:        Cassandra / InfluxDB
  Full-text search:                 Elasticsearch
  Files, images, videos:            S3 (object storage)
  Graph data (social connections):  Neo4j or adjacency list in SQL

Caching:
  Session data:          Redis (with TTL)
  Computed feeds:        Redis (sorted sets)
  Static files:          CDN (CloudFront, Cloudflare)
  DB query results:      Redis + TTL invalidation

Queuing:
  Task queue (workers):  RabbitMQ / SQS
  Event streaming:       Kafka
  Real-time messaging:   WebSockets + Redis pub/sub

Scale:
  Read-heavy:    Read replicas + cache
  Write-heavy:   Sharding + async writes via queue
  Mixed:         CQRS (separate read/write paths)

Consistency:
  Financial:     Strong consistency (ACID transactions)
  Social feeds:  Eventual consistency (ok to be seconds stale)
  Inventory:     Strong (don't oversell)
  Analytics:     Eventual (approximate is fine)

Reliability:
  Idempotency keys for payments
  Retry with exponential backoff + jitter
  Circuit breaker for downstream services
  Dead letter queue for failed messages
```

---

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ← Previous | [15 — Cloud Architecture](../15_cloud_architecture/theory.md) |
| ➡️ Next | [17 — Low Level Design](../17_low_level_design/theory.md) |
| 🏠 Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cloud Architecture — Interview Q&A](../15_cloud_architecture/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
