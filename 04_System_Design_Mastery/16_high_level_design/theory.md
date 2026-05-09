<a id="top"></a>

# High Level Design (HLD)

> "Imagine you're an architect designing a city," Mohan says, standing at the whiteboard in the
> Hyderabad office. "You don't draw every brick in every building first. You decide where the
> hospitals go, where the roads connect, where the water supply lives. HLD is the city plan of
> software — what services exist, how they communicate, where data lives, and how the system
> handles scale, failures, and growth. It answers: what does the system look like from 10,000 feet?"

<a id="contents"></a>

## Contents

| # | Topic |
|---|-------|
| 1 | [What is HLD and When Does It Apply?](#1-what-is-hld-and-when-does-it-apply) |
| 2 | [The HLD Interview Framework (45 Minutes)](#2-the-hld-interview-framework-45-minutes) |
| 3 | [Step 1 — Requirements Clarification](#3-step-1--requirements-clarification) |
| 4 | [Step 2 — Capacity Estimation](#4-step-2--capacity-estimation) |
| 5 | [Step 3 — High-Level Architecture](#5-step-3--high-level-architecture) |
| 6 | [Step 4 — Deep Dives](#6-step-4--deep-dives) |
| 7 | [Step 5 — Bottlenecks and Trade-offs](#7-step-5--bottlenecks-and-trade-offs) |
| 8 | [Architecture Patterns](#8-architecture-patterns) |
| 9 | [System Communication Patterns](#9-system-communication-patterns) |
| 10 | [Data Flow Design](#10-data-flow-design) |
| 11 | [HLD of URL Shortener (Complete Walkthrough)](#11-hld-of-url-shortener-complete-walkthrough) |
| 12 | [HLD of Twitter / Social Feed](#12-hld-of-twitter--social-feed) |
| 13 | [HLD of WhatsApp / Messaging](#13-hld-of-whatsapp--messaging) |
| 14 | [HLD of Netflix / Video Streaming](#14-hld-of-netflix--video-streaming) |
| 15 | [HLD of Uber / Ride Sharing](#15-hld-of-uber--ride-sharing) |
| 16 | [Common Design Decisions Cheatsheet](#16-common-design-decisions-cheatsheet) |
| 17 | [Summary](#17-summary) |

<a id="learning-priority"></a>

## Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
HLD framework (clarify, estimate, architecture, deep dive, trade-offs) . capacity estimation . communication patterns (sync vs async)

**Should Learn** — Important for real projects, comes up regularly:
case study patterns (fan-out/geo-indexing/streaming) . architecture selection (monolith vs microservices vs event-driven)

**Good to Know** — Useful in specific situations, not always tested:
design decisions matrix . bottleneck identification

**Reference** — Know it exists, look up syntax when needed:
detailed case study walkthroughs (URL shortener/Twitter/WhatsApp/Netflix/Uber) . cost estimation

[Back to Top](#top)

<a id="1-what-is-hld-and-when-does-it-apply"></a>

# 1. What is HLD and When Does It Apply?

"Think of it this way," Mohan draws two boxes on the whiteboard. "LLD is like designing the
interior of a single room — furniture placement, wiring, plumbing inside one wall. HLD is the
floor plan of the whole building — where each room goes, how hallways connect them, where the
elevators are."

```
LLD (Low Level Design):   How is this service built internally?
                          Classes, methods, design patterns
                          -> "What does the code look like?"

HLD (High Level Design):  How does the overall system work?
                          Services, databases, queues, caches
                          -> "What does the architecture look like?"
```

**HLD deals with:**
- Which services exist and what they do
- How services communicate (sync vs async)
- Where data is stored (SQL, NoSQL, object storage)
- How the system scales (horizontal, sharding, caching)
- How the system handles failures (redundancy, circuit breakers)
- Trade-offs made and why

[Back to Top](#top)

<a id="2-the-hld-interview-framework-45-minutes"></a>

# 2. The HLD Interview Framework (45 Minutes)

"I've seen hundreds of candidates," Mohan says. "The ones who fail jump straight to drawing
boxes. The ones who get offers spend the first five minutes asking smart questions. Here's how
I teach my team to structure the 45 minutes."

```
Timeline:
  0-5  min:  Requirements clarification
  5-10 min:  Capacity estimation (back-of-envelope)
  10-20 min: High-level architecture diagram
  20-35 min: Deep dives (2-3 components)
  35-45 min: Bottlenecks, trade-offs, follow-up questions
```

**The golden rule:** Never jump straight to design. Requirements first, always.

[Back to Top](#top)

<a id="3-step-1--requirements-clarification"></a>

# 3. Step 1 — Requirements Clarification

"Before you draw a single box," Mohan taps the marker on the board, "ask questions. The
interviewer is testing whether you can navigate ambiguity — the same skill you use every day
when a product manager gives you a one-line spec."

Ask questions before drawing anything.

<a id="functional-requirements"></a>

## Functional Requirements

```
"What should the system do?"

Template questions:
  - Who are the users? (end users, developers via API, admins)
  - What are the core user actions?
  - What is out of scope? (explicitly narrow it)
  - Are there mobile clients? Web? Both?
  - Real-time or eventually consistent is acceptable?
```

<a id="non-functional-requirements"></a>

## Non-Functional Requirements

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

<a id="example-url-shortener-requirements"></a>

## Example — URL Shortener

```
Functional (agreed):
  - Create short URL from long URL
  - Redirect to long URL given short URL
  - Custom aliases (optional)
  - Expiration (optional)

Out of scope:
  - User accounts / authentication
  - Analytics dashboard (just basic click count)

Non-functional:
  - 100M URLs created/day
  - 10:1 read/write ratio -> 1B redirects/day
  - Low latency redirects (P99 < 100ms)
  - 99.9% availability
  - URLs valid for 10 years
```

[Back to Top](#top)

<a id="4-step-2--capacity-estimation"></a>

# 4. Step 2 — Capacity Estimation

"Capacity estimation isn't about getting the exact number," Mohan explains. "It's about
proving to the interviewer that your architecture choices are driven by data, not by whatever
you read on a blog last night. Wrong numbers with sound reasoning beats perfect numbers with
no explanation."

**Always do this.** It drives architecture decisions.

<a id="estimation-template"></a>

## Template

```
1. Calculate write QPS
2. Calculate read QPS
3. Calculate storage (per record x records/day x retention)
4. Calculate bandwidth (QPS x avg payload size)
5. Identify bottlenecks (CPU? DB? Bandwidth? Memory?)
```

<a id="url-shortener-estimation"></a>

## URL Shortener Estimation

```
Writes:
  100M URLs/day / 86,400s/day = ~1,160 writes/sec
  Peak (3x): ~3,500 writes/sec

Reads:
  1B redirects/day / 86,400s = ~11,574 reads/sec
  Peak (3x): ~35,000 reads/sec

Storage per URL record:
  long_url:  200 bytes average
  short_code: 7 bytes
  created_at: 8 bytes
  expire_at:  8 bytes
  click_count: 8 bytes
  Total: ~250 bytes -> round to 500 bytes with overhead

Storage growth:
  100M records/day x 500 bytes = 50 GB/day
  50 GB x 365 x 10 years = ~182 TB total

Bandwidth:
  Writes: 1,160 x 500 bytes = ~580 KB/s
  Reads: 11,574 x 500 bytes = ~5.8 MB/s (negligible for redirects)

Key insight:
  -> Read-heavy (10:1) -- optimize for reads
  -> 35K reads/sec is Redis territory (cache hot URLs)
  -> 182 TB is manageable with sharded DB over 10 years
```

<a id="key-numbers-to-memorize"></a>

## Key Numbers to Memorize

```
Seconds in a day:           86,400 (~100K for rough math)
Seconds in a month:         2.6M
Seconds in a year:          31.5M

Storage quick guide:
  1 million records x 1 KB = 1 GB
  1 billion records x 1 KB = 1 TB
  1 billion records x 1 MB = 1 PB

QPS quick guide:
  1M requests/day  = ~12 req/s
  10M requests/day = ~120 req/s
  100M/day         = ~1,200 req/s
  1B/day           = ~12,000 req/s
```

[Back to Top](#top)

<a id="5-step-3--high-level-architecture"></a>

# 5. Step 3 — High-Level Architecture

"Now you earn the right to draw," Mohan smiles. "Start with the simplest diagram that solves
the problem. A client, a load balancer, your services, your data stores. Then expand."

Draw a simple block diagram first. Expand from there.

<a id="generic-web-architecture"></a>

## Generic Web Architecture

```
                        +-------------+
                        |     DNS     |
                        +------+------+
                               |
                        +------v------+
                        |     CDN     |  <- static assets
                        +------+------+
                               |
Client ------------------> +---v-----+
                           |  Load   |
                           | Balancer|
                           +---+-----+
                    +----------+----------+
               +----v----+ +--v---+ +----v----+
               | App     | | App  | | App     |
               | Server 1| | Svr 2| | Server 3|
               +----+----+ +--+---+ +----+----+
                    +---------+----------+
                         +----v----+
                    +----+  Cache  +----+
                    |    | (Redis) |    |
                    |    +---------+    |
             +------v------+    +------v-------+
             |  Primary DB |    |  Read Replica|
             +-------------+    +--------------+
```

<a id="service-oriented-architecture"></a>

## Service-Oriented Architecture

```
                     API Gateway
                         |
          +--------------+--------------+
          |              |              |
   +------v------+ +----v------+ +----v------+
   |   User      | |  Order    | | Payment   |
   |  Service    | |  Service  | | Service   |
   +------+------+ +----+------+ +----+------+
          |              |              |
   +------v------+ +----v------+ +----v------+
   |  Users DB   | |  Orders DB| |Payments DB|
   +-------------+ +-----+-----+ +-----------+
                         |
                  +------v------+
                  |   Message   |
                  |    Queue    |
                  |  (Kafka)    |
                  +------+------+
                  +------v------+
                  |Notification |
                  |  Service    |
                  +-------------+
```

[Back to Top](#top)

<a id="6-step-4--deep-dives"></a>

# 6. Step 4 — Deep Dives

"After the big picture," Mohan says, "the interviewer will push you deeper into two or three
areas. This is where they separate the people who memorized diagrams from the people who
actually build systems. Pick the hardest part and explain it like you own it."

After the overview, pick 2-3 components to explain in detail.

<a id="what-to-deep-dive-on"></a>

## What to Deep-Dive On

```
1. The most complex / critical path
   Example: For Twitter -- how is the home timeline generated?

2. The part that's different from standard patterns
   Example: For Uber -- real-time location matching algorithm

3. Where the interviewer pushes ("how would you scale X?")
```

<a id="common-deep-dive-topics"></a>

## Common Deep-Dive Topics

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

[Back to Top](#top)

<a id="7-step-5--bottlenecks-and-trade-offs"></a>

# 7. Step 5 — Bottlenecks and Trade-offs

"Every system design interview ends the same way," Mohan says. "The interviewer asks: what
breaks first? If you can't answer that, you don't understand your own design. This is the
moment that separates senior from staff."

Always conclude by identifying:

```
1. Where are the bottlenecks?
   "At 100K writes/sec, the single DB becomes the bottleneck.
    We'd shard by user_id."

2. What trade-offs did you make?
   "We chose eventual consistency for the feed.
    Users might see posts up to 5s late.
    That's acceptable -- the alternative is complex distributed locking."

3. What would you do differently at 10x scale?
   "At 10x we'd need a dedicated search service (Elasticsearch),
    separate read and write paths (CQRS), and multi-region replication."

4. What monitoring/alerts would you add?
   "P99 latency on DB queries, cache hit ratio, queue depth,
    error rate per service."
```

[Back to Top](#top)

<a id="8-architecture-patterns"></a>

# 8. Architecture Patterns

"Choosing architecture is like choosing a vehicle," Mohan says. "A bicycle is perfect for a
solo ride to the nearby store — simple, no fuel cost, easy to park. A bus carries fifty people
but needs a driver and a route plan. A fleet of autonomous cars scales infinitely but requires
a traffic management system. Monolith is the bicycle. Microservices are the fleet."

<a id="monolith"></a>

## Monolith

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

<a id="microservices"></a>

## Microservices

```
Each service is independently deployable, owns its data.

Pros:
  Independent scaling (scale only what's hot)
  Independent deployment (teams move faster)
  Technology diversity possible
  Fault isolation (one service down != all down)

Cons:
  Distributed systems complexity
  Network calls instead of function calls (latency + failures)
  Distributed transactions are hard
  Operational overhead (K8s, service mesh, tracing)

Use when: large team (>50 eng), different scale requirements per service,
          need independent deployment cadences
```

<a id="event-driven-architecture"></a>

## Event-Driven Architecture

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

Use when: high write throughput, fan-out (one event -> many handlers),
          decoupled teams, audit log needed
```

<a id="cqrs"></a>

## CQRS (Command Query Responsibility Segregation)

```
Separate read model from write model.

Write path:
  Command -> Validate -> Write to DB -> Emit event

Read path:
  Query -> Read-optimized view (denormalized, cached)

     +---------+  Command  +--------------+
     | Client  |---------->| Command Svc  |--> Write DB
     |         |           +------+-------+
     |         |              Event|
     |         |           +------v-------+
     |         |  Query    | Projection   |--> Read DB
     |         |<----------| (Read Model) |    (denormalized)
     +---------+           +--------------+

Use when: complex domain, high read/write ratio difference,
          different scale needs for reads vs writes
```

[Back to Top](#top)

<a id="9-system-communication-patterns"></a>

# 9. System Communication Patterns

"Communication between services," Mohan says, "is like communication between people. Sometimes
you call someone and wait on the line — that's synchronous. Sometimes you send a text and go
about your day — that's asynchronous. Each has a cost. A phone call blocks you. A text might
get lost or read hours later."

<a id="synchronous-communication"></a>

## Synchronous (Request-Response)

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

<a id="asynchronous-communication"></a>

## Asynchronous (Message-Based)

```
Message Queue (RabbitMQ, SQS):
  Point-to-point: one message -> one consumer
  Good for: task queues, work distribution
  Example: order processing, email sending

Event Streaming (Kafka):
  Publish-subscribe: one event -> many consumers
  Replay-able, partitioned, durable
  Good for: event sourcing, audit logs, fan-out
  Example: user activity stream, CDC (change data capture)
```

<a id="communication-choice-guide"></a>

## Communication Choice Guide

```
Scenario                      Use
----------------------------------------------------
User-facing API               REST or GraphQL
Internal service to service   gRPC (low latency, typed)
Decoupled async processing    Message queue (RabbitMQ/SQS)
Fan-out (many consumers)      Event streaming (Kafka)
Real-time push to client      WebSockets or SSE
Batch processing              Queue + worker pool
```

[Back to Top](#top)

<a id="10-data-flow-design"></a>

# 10. Data Flow Design

"Data flows through a system like water through a city's pipes," Mohan says. "Some pipes are
wide and fast for drinking water (reads). Others are narrow with pressure valves for sewage
(writes). You design different pipes for different flow patterns."

<a id="read-heavy-pattern"></a>

## Read-Heavy Pattern

```
Client -> Cache check
           | miss
        Database -> populate cache -> return

Optimization layers:
  1. Application cache (in-process, e.g., Python dict with TTL)
  2. Distributed cache (Redis/Memcached)
  3. Read replicas (DB load distribution)
  4. CDN (for public, static-enough data)
```

<a id="write-heavy-pattern"></a>

## Write-Heavy Pattern

```
Client -> Validate -> Write to Queue -> Return ack
                         |
                     Consumer -> Write to DB
                              -> Update cache
                              -> Notify downstream

Options:
  Write-through cache: write to cache + DB simultaneously
  Write-behind cache:  write to cache, async to DB
  Write-ahead log:     log every write for durability
```

<a id="fan-out-patterns"></a>

## Fan-Out Patterns

```
Fan-out on write (push model):
  When user posts -> immediately push to all followers' feeds
  + Fast reads (pre-computed)
  - Slow writes (celebrity problem: Beyonce has 100M followers)
  Use for: users with small follower count

Fan-out on read (pull model):
  When user checks feed -> pull from all followed users
  + Fast writes
  - Slow reads (must query all followed users)
  Use for: celebrity users

Hybrid:
  Small follower count -> fan-out on write
  Large follower count (> 10K) -> fan-out on read
  Twitter uses this hybrid approach
```

[Back to Top](#top)

<a id="11-hld-of-url-shortener-complete-walkthrough"></a>

# 11. HLD of URL Shortener (Complete Walkthrough)

"Let me walk you through a full HLD answer," Mohan says, "the way I'd expect a senior
engineer to present it in an interview. Notice the structure — requirements, numbers,
diagram, deep dives. This is the gold standard."

<a id="url-shortener-requirements"></a>

## Requirements

```
Functional:
  - Create short URL -> returns 7-char code (e.g., bit.ly/abc1234)
  - Redirect: GET /{short_code} -> 301/302 to long URL
  - Optional: custom alias, expiration

Non-functional:
  - 100M creations/day, 1B redirects/day
  - P99 redirect < 100ms
  - 99.9% availability
  - 10 year retention
```

<a id="url-shortener-architecture"></a>

## High-Level Architecture

```
                     +--------------+
                     |   Client     |
                     +------+-------+
                            |
                     +------v-------+
                     | API Gateway  |  (rate limiting, auth)
                     +------+-------+
                     +------v-------+
                     | Load Balancer|
                     +------+-------+
              +-------------+-------------+
       +------v------+             +------v------+
       |  URL Create |             |  Redirect   |
       |  Service    |             |  Service    |
       +------+------+             +------+------+
              |                           |
       +------v------+             +------v------+
       |  ID         |             |  Redis      |  <- hot URLs cached
       |  Generator  |             |  Cache      |
       |  (Snowflake)|             +------+------+
       +-------------+                    | miss
                                   +------v------+
                                   |  URL Store  |  <- sharded
                                   |  (MySQL /   |
                                   |   Cassandra)|
                                   +-------------+
```

<a id="url-shortener-database-design"></a>

## Database Design

```sql
urls (
    short_code   CHAR(7)      PRIMARY KEY,
    long_url     TEXT         NOT NULL,
    user_id      BIGINT,
    created_at   TIMESTAMP    DEFAULT NOW(),
    expires_at   TIMESTAMP,
    click_count  BIGINT       DEFAULT 0
)

Index: short_code -> primary key lookup
Sharding: by short_code (hash-based)
```

<a id="short-code-generation"></a>

## Short Code Generation

```
Option 1: Base62 encoding of auto-increment ID
  ID = 12345 -> Base62 -> "dnh"
  Pros: simple, unique
  Cons: predictable, counter is a SPOF

Option 2: Random + uniqueness check
  Generate 7 random chars -> check DB -> retry if collision
  Pros: unpredictable
  Cons: DB roundtrip, collision rate grows with scale

Option 3: Distributed ID generator (Snowflake)
  64-bit ID -> Base62 -> 7-char code
  Timestamp + machine_id + sequence
  Pros: unique, sortable, no DB lookup
  Cons: clock skew handling needed

-> Use Option 3 for production scale
```

<a id="redirect-flow"></a>

## Redirect Flow

```
GET /abc1234
  1. Check Redis: O(1) lookup
     -> HIT:  301 redirect -> long_url (cached in browser)
     -> MISS: query DB, populate Redis, return 302 redirect
  2. Async: increment click_count (don't block redirect)

Why 301 vs 302?
  301 Permanent -> browser caches, reduces server load
                   but you lose click analytics
  302 Temporary -> server sees every redirect (analytics work)
                   but more load
  -> Use 302 for analytics, 301 for pure perf
```

[Back to Top](#top)

<a id="12-hld-of-twitter--social-feed"></a>

# 12. HLD of Twitter / Social Feed

"Twitter's core problem," Mohan explains, "is deceptively simple: show users the latest
tweets from people they follow. But when Beyonce has 300 million followers and tweets once,
you can't write to 300 million timelines. That's the fan-out problem — and it's the heart
of every social feed design."

<a id="twitter-core-challenge"></a>

## Core Challenge: Home Timeline at Scale

```
Write path:
  User posts tweet
       |
  Tweet Service -> Writes to Tweets table
       |
  Fan-out Service -> Kafka (tweet.created event)
       |
  Timeline Workers (consumer group)
       |
  For each follower -> prepend tweet_id to follower's timeline cache
  (Redis sorted set, sorted by timestamp)

Read path:
  User opens app
       |
  Timeline Service -> Read from Redis timeline cache (their pre-built feed)
       |
  Hydration Service -> Fetch tweet details + user info (parallel)
       |
  Return paginated feed

Celebrity problem (Kylie Jenner, 300M followers):
  -> Do NOT fan-out on write for celebrities
  -> On timeline read: merge pre-built cache + fetch latest celebrity tweets
  Threshold: followers > 10,000 -> on-read inclusion
```

<a id="twitter-architecture"></a>

## Architecture

```
Tweet Write:
  Client -> API GW -> Tweet Service -> MySQL (tweets)
                              |
                           Kafka (tweet.created)
                              |
                     Fan-out Workers
                         /         \
               Regular users      Celebrities
               (write to         (skip, pulled
               timeline cache)    at read time)

Timeline Read:
  Client -> API GW -> Timeline Service -> Redis (user's feed)
                                              | hydrate
                                       Tweet Service (batch)
                                       User Service (batch)
```

[Back to Top](#top)

<a id="13-hld-of-whatsapp--messaging"></a>

# 13. HLD of WhatsApp / Messaging

"Messaging has a unique constraint," Mohan says. "The recipient might be offline. Unlike a
web request where you get an immediate response, a message might sit in a queue for hours
until the user's phone comes back online. You need guaranteed delivery to a moving target."

<a id="whatsapp-core-challenge"></a>

## Core Challenge: Reliable Message Delivery to Possibly Offline User

```
Message states:
  SENT -> DELIVERED -> READ
  (server ack) (device ack)  (read receipt)

Architecture:
  Sender -> Chat Server -> Message Queue
                              |
                       Message Store (Cassandra)
                              |
                       Push to recipient (WebSocket / FCM/APNs)
                         +- Online: deliver via persistent WebSocket
                         +- Offline: store + push notification

Message schema (Cassandra):
  Partition key: conversation_id
  Sort key:      message_id (Snowflake -- sortable by time)
  Columns:       sender_id, content, type, created_at, status

Why Cassandra?
  -> High write throughput (WAL + memtable)
  -> Time-series access pattern (latest messages first)
  -> Multi-region replication

Delivery guarantee:
  -> At-least-once + dedup on client side
  -> Message ID used to deduplicate on recipient
```

[Back to Top](#top)

<a id="14-hld-of-netflix--video-streaming"></a>

# 14. HLD of Netflix / Video Streaming

"Netflix's genius," Mohan says, "is that 99% of their traffic never touches their servers.
Videos are pre-encoded, chunked, and pushed to CDN edge nodes around the world. The database
only stores metadata. When you press play, the nearest edge node serves your video, and the
client dynamically adjusts quality based on your bandwidth. The architecture is optimized for
one thing: getting bytes to your eyeballs as fast as possible."

<a id="netflix-core-challenge"></a>

## Core Challenge: Serve High-Quality Video to Millions Concurrently

```
Upload path (content team):
  Raw video -> Transcoding Service (multiple resolutions: 4K, 1080p, 720p, ...)
            -> Chunking (2-4 second segments, HLS/DASH format)
            -> S3 (origin storage)
            -> CDN (pre-pushed to edge nodes globally)

Playback path (user):
  Open Netflix -> Content discovery (recommendation service)
  Press play   -> Manifest request -> CDN (m3u8 playlist)
  Streaming    -> Adaptive bitrate (ABR): client measures bandwidth,
                 selects appropriate quality chunk in real-time

CDN strategy:
  Popular content: pre-pushed to all edge nodes
  Long-tail content: pull-through (first request fetches from origin)
  -> Netflix runs its own CDN (Open Connect) for top content

Key insight:
  Netflix uses S3 + CDN for 99% of traffic
  Database (MySQL/Cassandra) is only used for metadata, not video bytes
```

[Back to Top](#top)

<a id="15-hld-of-uber--ride-sharing"></a>

# 15. HLD of Uber / Ride Sharing

"Uber's core problem," Mohan says, "is matching a rider to the nearest available driver in
real-time. Every four seconds, every driver's phone sends a GPS update. You're maintaining a
live, constantly-changing geospatial index of all drivers in every city. Then when a rider
requests a ride, you query that index: who's available within five kilometers?"

<a id="uber-core-challenge"></a>

## Core Challenge: Match Riders to Nearby Drivers in Real-Time

```
Driver location update:
  Driver app sends GPS every 4s -> WebSocket
       |
  Location Service -> Redis GeoSet (geospatial index)
  (lat/lng stored per driver_id)

Rider match flow:
  Rider requests ride -> Matching Service
       |
  GEORADIUS query: find drivers within X km
       |
  Filter: available drivers only
       |
  Rank by ETA (straight-line distance as proxy)
       |
  Offer to top driver -> accept/reject (timeout 10s)
       |
  If rejected -> next driver in ranked list
       |
  Match confirmed -> notify both parties

Location storage:
  Redis GeoSet: GEOADD drivers <lng> <lat> <driver_id>
                GEORADIUS drivers <rider_lng> <rider_lat> 5 km
  -> O(N+log(M)) where M = members in sorted set

Supply/demand:
  Surge pricing model: if (demand/supply) > threshold -> surge multiplier
  Supply = available drivers in area
  Demand = open ride requests in area
```

[Back to Top](#top)

<a id="16-common-design-decisions-cheatsheet"></a>

# 16. Common Design Decisions Cheatsheet

"Keep this mental model," Mohan says. "When someone says 'user accounts,' your brain should
immediately say 'PostgreSQL.' When someone says 'real-time feed,' your brain should say 'Redis
sorted set.' When someone says 'video,' your brain should say 'S3 plus CDN.' This is the
pattern matching that makes senior engineers fast in design interviews."

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

[Back to Top](#top)

<a id="17-summary"></a>

# 17. Summary

| Concept | Key Takeaway |
|---------|-------------|
| HLD vs LLD | HLD = architecture from 10,000 feet; LLD = code-level design |
| Interview Framework | Requirements -> Capacity -> Architecture -> Deep Dives -> Trade-offs |
| Requirements | Always clarify functional + non-functional before drawing |
| Capacity Estimation | Drives architecture decisions — data beats intuition |
| Architecture Patterns | Monolith (simple) -> Microservices (scale) -> Event-Driven (decouple) |
| Communication | Sync (REST/gRPC) for immediate, Async (Kafka/SQS) for decoupled |
| Data Flow | Read-heavy = cache layers; Write-heavy = queues; Mixed = CQRS |
| Fan-out | Push for normal users, pull for celebrities, hybrid for production |
| URL Shortener | Snowflake IDs + Redis cache + sharded DB |
| Twitter Feed | Fan-out on write + celebrity exception via on-read merge |
| WhatsApp | Cassandra + WebSocket + at-least-once delivery |
| Netflix | Transcode + chunk + CDN edge; DB only for metadata |
| Uber | Redis GeoSet + GEORADIUS + real-time WebSocket updates |
| Design Decisions | Match data pattern to storage tech; match communication to coupling needs |

[Back to Top](#top)

<a id="navigation"></a>

## Navigation

| Link | Destination |
|------|-------------|
| Previous | [15 — Cloud Architecture](../15_cloud_architecture/theory.md) |
| Next | [17 — Low Level Design](../17_low_level_design/theory.md) |
| Home | [README.md](../README.md) |
| Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| Interview | [interview.md](./interview.md) |

[Back to Top](#top)
