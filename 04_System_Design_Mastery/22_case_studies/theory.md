<a id="top"></a>

# Case Studies — System Design in Practice

> Every system design interview boils down to: "Design X for millions of users." The candidate who has studied real systems (not just memorized architectures) can reason about trade-offs on the fly. Case studies teach you to think like the engineers who built Twitter, Netflix, Uber, WhatsApp, and every URL shortener that handles billions of redirects.

*Arun is a Telugu interviewer who has conducted over 500 system design interviews at top companies. He noticed a pattern: candidates who memorize architectures fail when the interviewer throws a curveball. But candidates who understand WHY each decision was made can adapt to any variation. He now teaches the methodology behind case studies — not the answers, but the thinking process.*

## 📖 Table of Contents

- [1. Why Case Studies Matter](#1-why-case-studies-matter)
- [2. The RESHADED Framework](#2-the-reshaded-framework)
- [3. Case Study Methodology — The Six Steps](#3-case-study-methodology-the-six-steps)
  - [Capacity Estimation Approach](#capacity-estimation-approach)
- [4. URL Shortener — Read-Heavy Caching at Scale](#4-url-shortener-read-heavy-caching-at-scale)
- [5. Twitter Feed — The Fan-Out Problem](#5-twitter-feed-the-fan-out-problem)
- [6. Netflix — CDN and Streaming at Scale](#6-netflix-cdn-and-streaming-at-scale)
- [7. Uber — Real-Time Geo-Location](#7-uber-real-time-geo-location)
- [8. WhatsApp — Reliable Messaging at Scale](#8-whatsapp-reliable-messaging-at-scale)
- [9. Pattern Map Across Case Studies](#9-pattern-map-across-case-studies)
- [Summary](#summary)

## Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
case study methodology (requirements, estimation, architecture, bottlenecks, trade-offs), capacity estimation process

**Should Learn** — Important for real projects, comes up regularly:
pattern recognition across system types, URL shortener, Twitter feed design

**Good to Know** — Useful in specific situations, not always tested:
Netflix CDN pattern, Uber geo-indexing, WhatsApp message ordering

**Reference** — Know it exists, look up syntax when needed:
pattern map across case studies, cost estimation per design

<a id="1-why-case-studies-matter"></a>

# 1. Why Case Studies Matter

"Let me tell you what separates a hire from a no-hire in a system design interview," Arun says. "It is not whether you know the exact architecture of Twitter. It is whether you can reason through trade-offs when I change the requirements. 'What if read traffic is 1000x write traffic?' 'What if the user is on a 3G network?' 'What if we need 99.99% availability?' The candidate who studied real systems can answer these because they have seen how real engineers made these decisions."

```
Why study real systems:

  1. Pattern recognition — the same 10-15 patterns appear in every system
     (caching, fan-out, sharding, pub/sub, CDN, async workers)

  2. Trade-off vocabulary — you learn WHY decisions were made
     (not just "use Redis" but "use Redis because reads are 100:1 over writes
     and p99 latency must be < 10ms")

  3. Failure mode awareness — real systems teach you what breaks
     (not just "use Kafka" but "Kafka consumer lag causes stale dashboards")

  4. Estimation skills — you develop intuition for numbers
     (how many QPS a single Postgres can handle, how much a CDN costs)

How to study a case study:
  DO:  Understand the requirements that drove each decision
  DO:  Ask "what breaks if we removed this component?"
  DO:  Practice explaining trade-offs in your own words
  DON'T:  Memorize architectures as fixed answers
  DON'T:  Copy diagrams without understanding the "why"
  DON'T:  Skip capacity estimation — interviewers test this
```

> [↑ Back to Top](#top)

<a id="2-the-reshaded-framework"></a>

# 2. The RESHADED Framework

"RESHADED is my mnemonic for the eight dimensions every system design must address," Arun explains. "When I interview candidates, I check whether they have touched all eight. Missing even one is a red flag — it means they designed a system that works on a whiteboard but would fail in production."

```
R — Requirements
    Functional: what does the system DO?
    Non-functional: latency, availability, consistency, durability

E — Estimation
    Users, QPS, storage, bandwidth, cost
    Derive the numbers that drive architecture decisions

S — Storage
    What databases? SQL vs NoSQL? How is data modeled?
    Partitioning strategy? Replication factor?

H — High-Level Design
    Draw the boxes: clients, load balancers, services, databases, caches
    Show the data flow for the core use case

A — API Design
    What endpoints exist? What do requests/responses look like?
    REST? GraphQL? gRPC? WebSocket?

D — Detailed Design
    Zoom into the hardest part. How does fan-out work?
    How is the cache invalidated? How does sharding key work?

E — Evaluation (Trade-offs)
    What are the trade-offs of your design?
    What would you change at 10x scale? 100x?

D — Distinctive Features (Edge Cases)
    Rate limiting, abuse prevention, monitoring, deployment
    What makes this system production-ready vs whiteboard-ready?
```

```
Arun's tip for interviews:

  "Touch all 8 letters in 45 minutes. Spend 5 min on R+E,
  15 min on S+H+A (the core design), 15 min on D (deep dive),
  and 10 min on E+D (trade-offs and production concerns).

  If the interviewer focuses on one area, adapt — but make sure
  you signal awareness of all eight dimensions even if briefly."
```

> [↑ Back to Top](#top)

<a id="3-case-study-methodology-the-six-steps"></a>

# 3. Case Study Methodology — The Six Steps

"Every case study in this module," Arun says, "follows the same six steps. This is not a formula — it is how real engineers think. When you design a new system at work, you do these same steps, just less formally."

```
Step 1: CLARIFY REQUIREMENTS
  Ask questions before designing. Never assume.
  "Is this read-heavy or write-heavy?"
  "What is the expected scale — users, requests per second?"
  "What consistency guarantees do we need?"
  "What is the acceptable latency?"
  "Are there geographic distribution requirements?"

Step 2: ESTIMATE SCALE
  Derive concrete numbers from requirements.
  Daily active users --> QPS --> storage --> bandwidth
  These numbers drive every architecture decision.

Step 3: DESIGN THE CORE FLOW
  The simplest architecture that handles the happy path.
  Client --> API --> Service --> Database
  Do not optimize prematurely. Start simple.

Step 4: IDENTIFY BOTTLENECKS
  "What breaks first as scale increases?"
  Single database? Network bandwidth? CPU on one service?
  Think about the 10x moment — what falls over?

Step 5: APPLY TARGETED SOLUTIONS
  Caching (Redis, CDN), sharding, async processing,
  read replicas, message queues, rate limiting.
  Each solution addresses a specific bottleneck.

Step 6: DISCUSS TRADE-OFFS
  "Every decision has a cost."
  Caching --> stale data risk.
  Sharding --> cross-shard queries become hard.
  Async --> eventual consistency, harder debugging.
  Always state what you give up for what you gain.
```

<a id="capacity-estimation-approach"></a>

## Capacity Estimation Approach

"Interviewers love to see you estimate," Arun says. "It shows engineering judgment. You do not need exact numbers — you need the right order of magnitude and the ability to derive architecture decisions from those numbers."

```
The estimation chain:

  Users --> DAU --> QPS --> Peak QPS --> Storage --> Bandwidth

Example (URL Shortener):
  Total users: 500M registered
  DAU: 100M
  Reads per user per day: 5 (click shortened URLs)
  Writes per user per day: 0.1 (create shortened URLs)

  Read QPS: 100M * 5 / 86400 = ~5,800 --> round to 6K QPS
  Peak QPS: 6K * 3 = ~18K QPS (3x for peak hours)
  Write QPS: 100M * 0.1 / 86400 = ~115 QPS

  Storage per URL: 100 bytes (short code + original URL + metadata)
  New URLs per day: 100M * 0.1 = 10M
  Storage per day: 10M * 100B = 1 GB/day
  Storage per year: 365 GB/year

  Insight: read-heavy (100:1 read:write ratio) --> cache aggressively
  Insight: storage is modest --> single database can hold years of data
  Insight: peak 18K QPS reads --> need caching layer (Redis can do 100K+ ops/sec)
```

```
Useful numbers to memorize:

  QPS for a single machine:
    Postgres:    5K-10K simple queries/sec
    Redis:       100K-500K ops/sec
    Nginx:       50K-100K concurrent connections

  Storage rough sizes:
    1 tweet (280 chars + metadata): ~1 KB
    1 URL mapping: ~100 bytes
    1 chat message: ~200 bytes
    1 user profile: ~1 KB
    1 minute of video (720p): ~5 MB
    1 image (compressed): ~200 KB

  Time units:
    1 day = 86,400 seconds (~100K for estimation)
    1 month = 2.6M seconds (~3M for estimation)
    1 year = 31.5M seconds (~30M for estimation)
```

> [↑ Back to Top](#top)

<a id="4-url-shortener-read-heavy-caching-at-scale"></a>

# 4. URL Shortener — Read-Heavy Caching at Scale

"The URL shortener is the 'Hello World' of system design interviews," Arun says. "Simple enough to discuss in 20 minutes, deep enough to test caching strategies, hashing algorithms, and analytics pipelines."

```
Core requirements:
  - Shorten a long URL to a short code (write)
  - Redirect short code to original URL (read)
  - Analytics: how many times was a URL clicked?
  - Read:write ratio = 100:1 (heavily read-biased)

Key architectural decisions:

  Hashing strategy:
    Base62 encoding of auto-increment ID --> "abc123"
    Collision-free, sequential, predictable length
    Alternative: MD5/SHA256 first 7 chars (collision possible, needs check)

  Caching:
    Read-heavy --> cache aggressively
    Redis cache: short_code --> original_url
    Cache hit ratio ~80% (popular URLs clicked repeatedly)
    Reduces DB load by 80%

  Storage:
    Simple key-value: short_code --> {original_url, created_at, user_id, clicks}
    Can be SQL (PostgreSQL) or NoSQL (DynamoDB)
    Scale: 1 billion URLs = ~100 GB (fits on one machine)

  CDN for redirects:
    301 (permanent) or 302 (temporary) redirect
    CDN caches 301 redirects --> DB not hit at all for popular URLs
    302 allows analytics tracking (every request hits your server)

Deep dive: [url_shortener.md](./url_shortener.md)
```

> [↑ Back to Top](#top)

<a id="5-twitter-feed-the-fan-out-problem"></a>

# 5. Twitter Feed — The Fan-Out Problem

"Twitter is the best case study for fan-out," Arun explains. "When a user with 10 million followers tweets, how do you deliver that tweet to 10 million timelines? This is THE classic distributed systems problem."

```
Core requirements:
  - Post tweets (write)
  - View home timeline (read — aggregation of tweets from people you follow)
  - Follow/unfollow users
  - Scale: 500M users, 300K tweets/sec peak

The fan-out problem:
  User A follows 500 people.
  Each person may have tweeted since A last checked.
  "Get A's timeline" = merge latest tweets from 500 followed users.

  Fan-out on Write (push model):
    When user posts tweet --> immediately write to all followers' timelines
    Read is fast (pre-computed), but write is expensive for celebrities
    Celebrity with 50M followers = 50M writes per tweet

  Fan-out on Read (pull model):
    When user requests timeline --> query all 500 followed users' tweets, merge
    Write is cheap (one write), but read is slow (500 DB queries per request)

  Hybrid (Twitter's actual approach):
    Regular users (< 1M followers): fan-out on write
    Celebrities (> 1M followers): fan-out on read (merge at query time)

Key architectural decisions:
  Timeline cache: Redis sorted set per user (tweet_id, timestamp)
  Tweet storage: distributed cache + Cassandra for persistence
  Cursor pagination: "give me tweets after cursor X" (not offset-based)

Deep dive: [twitter.md](./twitter.md)
```

> [↑ Back to Top](#top)

<a id="6-netflix-cdn-and-streaming-at-scale"></a>

# 6. Netflix — CDN and Streaming at Scale

"Netflix accounts for 15% of global internet traffic," Arun says. "Their architecture is a masterclass in CDN strategy, adaptive bitrate streaming, and microservices at scale."

```
Core requirements:
  - Stream video to 230M+ subscribers worldwide
  - Adaptive quality (4K on fiber, 480p on mobile)
  - < 2 second startup time for playback
  - 99.99% availability (users will switch to competitors)

Key architectural decisions:

  Content delivery:
    Netflix Open Connect: Netflix's own CDN
    Edge servers deployed inside ISP data centers
    Popular content pre-positioned at the edge
    User streams from nearest edge server, not origin

  Adaptive bitrate streaming:
    Each video encoded in multiple qualities (480p, 720p, 1080p, 4K)
    Each quality split into 4-second chunks
    Client requests chunks based on current bandwidth
    Bandwidth drops? Switch to lower quality mid-stream

  Transcoding pipeline:
    One upload --> hundreds of output formats (device, resolution, codec)
    Massively parallel: each chunk transcoded independently
    Runs on thousands of worker instances

  Recommendation system:
    Personalized homepage generated per user
    ML models trained on billions of viewing events
    A/B tested constantly (thousands of concurrent experiments)

  Microservices:
    700+ microservices
    Each owns its data, deploys independently
    Circuit breakers (Hystrix) prevent cascade failures

Deep dive: [netflix.md](./netflix.md)
```

> [↑ Back to Top](#top)

<a id="7-uber-real-time-geo-location"></a>

# 7. Uber — Real-Time Geo-Location

"Uber solves the real-time proximity problem," Arun explains. "When you open the app, it shows drivers near you — updated every 4 seconds. That requires ingesting millions of location updates per second and answering 'who is nearby?' queries in milliseconds."

```
Core requirements:
  - Match riders with nearby drivers in real-time
  - Track driver location (updates every 4 seconds)
  - Estimate arrival time
  - Handle surge pricing based on supply/demand
  - Scale: millions of concurrent drivers, location updates every 4s

Key architectural decisions:

  Geo-indexing:
    Problem: "Find drivers within 2km of (lat, lng)"
    Solution: Geohash-based sharding
    Geohash divides the world into grid cells (string prefix = area)
    Nearby = same or adjacent geohash prefix
    Redis GEO commands: GEOADD, GEORADIUS, GEOPOS

  Real-time location tracking:
    Driver app sends location every 4 seconds
    Millions of drivers --> millions of writes per second
    Location stored in Redis (hot data, ephemeral)
    Persisted to Cassandra for trip history

  WebSocket for live updates:
    Rider sees driver moving on map in real-time
    Server pushes driver location via WebSocket
    No polling — instant visual feedback

  Trip state machine:
    REQUESTED --> ACCEPTED --> EN_ROUTE --> ARRIVED --> IN_TRIP --> COMPLETED
    Each transition triggers events (notify rider, start billing, etc.)
    State machine prevents invalid transitions

  Surge pricing:
    Supply (available drivers in area) vs demand (ride requests)
    Computed per geohash cell every few seconds
    High demand + low supply = surge multiplier

Deep dive: [uber.md](./uber.md)
```

> [↑ Back to Top](#top)

<a id="8-whatsapp-reliable-messaging-at-scale"></a>

# 8. WhatsApp — Reliable Messaging at Scale

"WhatsApp handles 100 billion messages per day with a famously small engineering team," Arun says. "The key insight: they optimize for delivery reliability over everything else. A message must NEVER be lost, even if the recipient is offline for days."

```
Core requirements:
  - Send/receive messages (text, media, voice)
  - End-to-end encryption (server cannot read messages)
  - Guaranteed delivery (even if recipient is offline for days)
  - Message ordering within a conversation
  - Read receipts (delivered, read indicators)
  - Group messaging (up to 1024 members)

Key architectural decisions:

  Message delivery guarantee:
    Message stored on server until recipient acknowledges receipt
    Recipient ACKs each message (server deletes after ACK)
    Offline? Messages queued per user (Cassandra, partitioned by user_id)
    On reconnect: pull all queued messages in order

  End-to-end encryption:
    Signal Protocol (Double Ratchet algorithm)
    Server stores encrypted blobs — cannot read content
    Key exchange happens between devices directly
    Server is a dumb relay that stores and forwards

  Message ordering:
    Within a conversation: monotonically increasing sequence numbers
    Server assigns sequence per conversation
    Client orders by sequence, not by timestamp (clocks are unreliable)

  Media handling:
    Media uploaded to object storage (S3-equivalent)
    Only the reference (URL + encryption key) sent via message channel
    Recipient downloads media separately, decrypts with key from message

  Connection management:
    XMPP-based (originally), now custom protocol
    Single persistent TCP connection per device
    Push notifications (APNs/FCM) for offline wake-up
    Heartbeat every 30s to detect disconnection

Deep dive: [whatsapp.md](./whatsapp.md)
```

> [↑ Back to Top](#top)

<a id="9-pattern-map-across-case-studies"></a>

# 9. Pattern Map Across Case Studies

"The magic of studying multiple case studies," Arun says, "is that you start seeing the same patterns everywhere. Once you recognize a pattern, you can apply it to any new system the interviewer throws at you."

```
Pattern                    Appears In
─────────────────────────────────────────────────────────
Read-heavy caching         URL Shortener, Twitter, Netflix homepage
Fan-out write              Twitter (pre-compute timelines)
Fan-out read               Twitter (for celebrities), WhatsApp groups
CDN / edge delivery        URL Shortener (redirects), Netflix (video chunks)
Redis GEO                  Uber (driver proximity)
WebSocket push             Uber (live tracking), WhatsApp (message delivery)
Kafka event streaming      Uber (location updates), Netflix (view events)
Cassandra (write-heavy)    WhatsApp (message queue), Uber (trip events)
State machine              Uber (trip lifecycle), Payment systems
Idempotency keys           URL creation, payments, any POST that shouldn't double-fire
Cursor pagination          Twitter feed, WhatsApp message history
Background workers         Netflix (transcoding), URL analytics aggregation
Adaptive quality           Netflix (bitrate), Uber (map tile detail level)
E2E encryption             WhatsApp (Signal Protocol)
Geohashing                 Uber (proximity), any location-based service
```

```
When you see this requirement...     Think of this pattern...
────────────────────────────────      ────────────────────────────
"Users need to see updates fast"      WebSocket or SSE push
"Reads are 100x more than writes"     Cache layer (Redis + CDN)
"Celebrity with millions of fans"     Hybrid fan-out (push + pull)
"Find nearby X"                       Geohash + Redis GEO
"Never lose a message"                Queue + ACK + persist until confirmed
"Deliver video/media globally"        CDN (edge caching)
"Process millions of events/sec"      Kafka + stream processor
"Need exact ordering"                 Sequence numbers, not timestamps
"Prevent duplicate operations"        Idempotency keys
"Handle variable load spikes"         Auto-scaling + queue buffering
```

> [↑ Back to Top](#top)

<a id="summary"></a>

## 🔥 Summary

```
Case Study Methodology:
  1. Clarify requirements (functional + non-functional)
  2. Estimate scale (users --> QPS --> storage --> bandwidth)
  3. Design core flow (simplest working architecture)
  4. Identify bottlenecks (what breaks at 10x?)
  5. Apply solutions (cache, shard, async, CDN)
  6. Discuss trade-offs (what you gain vs what you lose)

RESHADED Framework (8 dimensions):
  R-Requirements, E-Estimation, S-Storage, H-High-Level Design,
  A-API Design, D-Detailed Design, E-Evaluation, D-Distinctive Features

Arun's rules for case study interviews:
  1. Always start with requirements — never jump to architecture
  2. Estimate before designing — numbers drive decisions
  3. Start simple, add complexity only where bottlenecks demand it
  4. Name trade-offs explicitly — interviewers want to hear "the cost of X is Y"
  5. Study patterns, not answers — new problems use the same 15 building blocks
```

## 📂 Available Case Studies

| System | Core Patterns | File |
|--------|--------------|------|
| URL Shortener | Hashing, redirects, analytics, read-heavy caching | [url_shortener.md](./url_shortener.md) |
| Twitter Feed | Fan-out on write vs read, Redis sorted sets, celebrity problem | [twitter.md](./twitter.md) |
| Netflix | CDN, adaptive bitrate streaming, recommendation pipeline | [netflix.md](./netflix.md) |
| Uber | Geo-indexing with Redis, real-time WebSockets, surge pricing | [uber.md](./uber.md) |
| WhatsApp | End-to-end encryption, message ordering, offline queues | [whatsapp.md](./whatsapp.md) |

## 📂 Navigation

| | |
|---|---|
| 📘 README | [Back to System Design README](../README.md) |

| ⬅ Previous | ➡ Next |
|---|---|
| [21 — Real-Time Systems](../21_real_time_systems/theory.md) | [23 — Interview Framework](../23_interview_framework/theory.md) |

**This folder:** [theory.md](./theory.md) | [cheetsheet.md](./cheetsheet.md) | [interview.md](./interview.md) | [practice_local.py](./practice_local.py)

**Related modules:** [16 — High Level Design](../16_high_level_design/theory.md) | [21 — Real-Time Systems](../21_real_time_systems/theory.md) | [23 — Interview Framework](../23_interview_framework/theory.md) | [11 — Scalability Patterns](../11_scalability_patterns/theory.md)

**Jump to topics:** [RESHADED Framework](#2-the-reshaded-framework) | [Capacity Estimation](#capacity-estimation-approach) | [Pattern Map](#9-pattern-map-across-case-studies) | [URL Shortener](#4-url-shortener-read-heavy-caching-at-scale)
