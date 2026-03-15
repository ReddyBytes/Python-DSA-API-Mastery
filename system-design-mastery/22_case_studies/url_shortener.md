# URL Shortener — Full System Design Walkthrough

> You are in your first system design interview. The interviewer slides a card across the table:
> **"Design a URL shortener like bit.ly."**
> The clock starts. What do you do first?

This walkthrough goes through every decision you'd make in a real interview — and why.

---

## 1. Requirements Clarification

Before drawing a single box, ask questions. This is not stalling — it is what senior engineers do.

**Functional requirements (what does the system do?):**
```
Q: What is the core feature — shorten a URL and redirect users?
A: Yes. Also track click analytics.

Q: Can users choose a custom alias (e.g., bit.ly/my-brand)?
A: Yes, but it is optional.

Q: Do URLs expire? Can users set a TTL?
A: Yes — default TTL of 1 year, configurable up to 5 years.

Q: Do we need authentication? Can anonymous users shorten URLs?
A: Registered users get analytics. Anonymous users can shorten but not see stats.

Q: Should the same long URL always map to the same short code?
A: No deduplication required — same URL can have multiple short codes.
```

**Non-functional requirements (how does it behave at scale?):**
```
Q: How many URLs are stored total?
A: About 100 million.

Q: What is the read-to-write ratio?
A: Heavy read — 10:1 (redirects far outnumber new URL creations).

Q: What latency is acceptable for a redirect?
A: Under 100ms p99. Users should not notice the redirect hop.

Q: What availability do we need?
A: 99.99% — downtime on a URL shortener is highly visible.

Q: Do we need global distribution?
A: Yes — users are worldwide.
```

**Confirmed scope:**
```
IN scope:
  - Shorten URL  →  generate short code
  - Redirect     →  GET /<code> → HTTP 3xx to original URL
  - Custom aliases
  - URL expiry (TTL)
  - Click analytics (async, not on the critical path)

OUT of scope (for this interview):
  - Spam/malware detection
  - Branded domains (yourco.short/link)
  - QR code generation
  - A/B testing / link rotations
```

---

## 2. Capacity Estimation

Back-of-the-envelope math signals engineering maturity. Do it out loud.

**Write throughput (URL creation):**
```
100 million URLs stored
Assume retention of ~5 years → new URLs per year = 100M / 5 = 20M/year

20,000,000 / (365 × 24 × 3600) ≈ 0.63 writes/second

Round up for burst headroom: ~1,000 writes/second (peak)
```

**Read throughput (redirects):**
```
Read:Write = 10:1
→ 10,000 redirects/second at peak
→ ~860 million redirects/day
```

**Storage (URL mappings):**
```
Per URL record:
  short_code:    8 bytes
  long_url:      ~200 bytes (average)
  user_id:       8 bytes
  created_at:    8 bytes
  expires_at:    8 bytes
  click_count:   8 bytes
  Total:        ~240 bytes per record

100M records × 240 bytes = ~24 GB for URL mappings

Analytics events (click logs):
  860M redirects/day × 50 bytes/event = ~43 GB/day
  Retain 90 days → ~3.9 TB for analytics
```

**Bandwidth:**
```
Read:
  10,000 req/sec × 200 bytes (response) = 2 MB/sec  → trivial

Write:
  1,000 req/sec × 500 bytes (request)   = 0.5 MB/sec → trivial
```

**Summary:**
```
Writes:         ~1,000/sec (peak)
Reads:          ~10,000/sec (peak)
URL storage:    ~24 GB
Analytics:      ~3.9 TB / 90 days
Short code length needed: 62^7 = 3.5 trillion  (more than enough for 100M)
```

---

## 3. High-Level Design

Start simple. Draw the boxes, then refine.

```
                               WRITE PATH
                               ----------
┌────────┐   POST /shorten   ┌───────────┐   validate+generate   ┌─────────┐
│ Client │──────────────────▶│   API     │──────────────────────▶│   App   │
│        │◀──────────────────│  Gateway  │◀──────────────────────│  Server │
│        │   {short_url}     │  (auth,   │   {short_code}        │         │
└────────┘                   │   rate    │                        └────┬────┘
                             │   limit)  │                             │
                             └───────────┘                             │ write
                                                                       ▼
                               READ PATH                        ┌─────────────┐
                               ---------                        │  Primary DB │
┌────────┐   GET /abc123     ┌───────────┐                      │  (DynamoDB) │
│ Client │──────────────────▶│   API     │                      └─────────────┘
│        │◀──────────────────│  Gateway  │
│        │   HTTP 302        │           │
└────────┘                   └─────┬─────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │         App Server           │
                    │                              │
                    │  1. check Redis cache        │
                    │  2. cache miss → query DB    │
                    │  3. return long URL          │
                    │  4. emit click event → Kafka │
                    └──────┬───────────┬───────────┘
                           │           │
               ┌───────────▼───┐  ┌────▼────────────┐
               │  Redis Cache  │  │   Primary DB     │
               │  (hot URLs)   │  │   (DynamoDB)     │
               └───────────────┘  └──────────────────┘
                                           │ replication
                                  ┌────────▼────────┐
                                  │  Read Replicas  │
                                  └─────────────────┘

                         ANALYTICS PATH
                         --------------
                App Server ──Kafka──▶ Analytics Workers ──▶ ClickHouse / S3
```

---

## 4. The Core Algorithm — Generating Short Codes

This is the interview's favourite deep-dive point. Know all three approaches cold.

### Option A: MD5 Hash (truncated)

```
long_url = "https://www.example.com/very/long/path"
hash     = md5(long_url)           # 128-bit hex string
code     = base62(hash[:6 bytes])  # take first 6 bytes → 8-char base62 code

Example:
  md5("https://example.com/...") = "a3f5c1..."
  base62(a3f5c1)                 = "dK9mXz"
```

Problems with MD5:
```
1. Collision risk: two different URLs can hash to the same prefix
2. Same URL always gets the same code (breaks "no deduplication" requirement)
3. Output is deterministic → predictable to attackers

Collision handling: check DB before inserting. If collision, append counter and re-hash.
This works but adds DB round-trips to the write path.
```

### Option B: Base62 Counter (auto-increment ID)

```
DB auto-increment ID → convert to base62

ID = 1,234,567
base62(1234567) = "5lJs"  (4 chars)

base62 alphabet: 0-9 a-z A-Z  (62 symbols)
62^6 = 56 billion possible codes  →  sufficient
62^7 = 3.5 trillion              →  comfortable for 100M
```

Problems with sequential IDs:
```
- Enumerable: attacker can crawl all URLs by iterating IDs
- Reveals volume: your competitor knows how many links you've created
- Distributed ID generation is hard (who owns the counter?)

Fix for distribution: pre-allocate ID ranges to app servers
  Server A: 1,000,000 – 1,999,999
  Server B: 2,000,000 – 2,999,999
  Each server exhausts its range locally, then requests the next block.
```

### Option C: Random Code (recommended)

```python
import random
import string

ALPHABET = string.ascii_letters + string.digits  # 62 chars
CODE_LEN  = 7

def generate_code() -> str:
    return "".join(random.choices(ALPHABET, k=CODE_LEN))

# 62^7 = 3.5 trillion  →  collision probability < 0.01% at 100M entries
```

Collision handling:
```
1. Generate random 7-char code
2. Try INSERT into DB (code is unique key)
3. If DB raises unique constraint violation → retry with new code
4. Retry up to 3 times before failing

Expected retries at 100M entries:
  P(collision) = 100M / 3.5T ≈ 0.003%
  P(3 consecutive collisions) ≈ negligible
```

### Comparison table

```
Approach        | Predictable | Collisions | Distributed? | Recommended
----------------|-------------|------------|--------------|------------
MD5 truncated   | Yes         | Rare       | Yes          | No
Base62 counter  | Yes         | None       | Complex      | No
Random base62   | No          | Very rare  | Yes          | YES
```

---

## 5. Database Choice

### Why NoSQL (DynamoDB / Cassandra) wins here

The access pattern is almost exclusively:
```
write: PUT  (short_code → URL record)
read:  GET  (short_code → URL record)   ← 99% of traffic
```

This is a pure key-value workload. NoSQL is purpose-built for it.

```
DynamoDB:
  Partition key:   short_code
  Read:            single-digit ms latency at any scale
  Write:           auto-scaled throughput
  No schema:       easy to add fields (analytics counters, custom metadata)
  TTL built-in:    DynamoDB TTL attribute → automatic expiry, no cron jobs needed

Cassandra:
  Partition key:   short_code
  Naturally sharded across nodes
  High write throughput
  Tunable consistency (read your own writes via LOCAL_QUORUM)
```

### Why SQL struggles here

```
Problem 1: JOIN queries
  URL shortener has no meaningful joins (it's a key-value map)
  SQL overhead for what is essentially a hash table lookup.

Problem 2: Horizontal scaling
  SQL sharding is complex and manual.
  At 10,000 redirects/second with sub-100ms SLA,
  a single Postgres instance becomes a bottleneck.
  Read replicas help, but write contention persists.

Problem 3: Sequential primary keys
  Auto-increment IDs are an enumeration risk (see section 4).

When SQL IS appropriate:
  User table:     user_id, email, plan, created_at  (relational, low volume)
  Billing:        transactions, subscriptions        (ACID required)
```

**Schema (DynamoDB):**
```
Table: urls
  PK: short_code (String)   "dK9mXz"
  Attributes:
    long_url      String     "https://example.com/..."
    user_id       String     "usr_abc123"
    created_at    Number     1709900000  (unix epoch)
    expires_at    Number     1741436000  (TTL attribute — DynamoDB auto-deletes)
    is_active     Boolean    true
    custom_alias  Boolean    false
```

---

## 6. The Redirect Flow

This is the hot path. Every millisecond matters.

### 301 vs 302 — which HTTP status code to use?

```
301 Permanent Redirect:
  Browser caches the redirect permanently.
  On second visit, browser goes DIRECTLY to destination (never hits your server).
  Pro:  Reduces server load dramatically for repeat visitors.
  Con:  You can never update the destination — browser won't re-check.
        Analytics: you lose all repeat visit data. Click counts become inaccurate.

302 Found (Temporary Redirect):
  Browser does NOT cache the redirect.
  Every visit hits your server.
  Pro:  Full analytics — you see every click.
        You can update or expire the destination at any time.
  Con:  Higher server load for popular URLs.

Decision for a URL shortener: USE 302.
  Analytics and updatability are core features.
  The server load is solved by caching (next section).
```

### Cache hit / miss flow

```
Request: GET /dK9mXz

Step 1: Check Redis
          Redis.get("url:dK9mXz")
                  │
          ┌───────┴───────┐
          │               │
        HIT             MISS
          │               │
          │           Step 2: Query DynamoDB
          │               │   GetItem(short_code="dK9mXz")
          │               │
          │           Step 3: Write to Redis
          │               │   Redis.set("url:dK9mXz", long_url, EX=3600)
          │               │
          └───────┬───────┘
                  │
          Step 4: Emit click event to Kafka (async, non-blocking)
                  │
          Step 5: Return HTTP 302
                  Location: https://example.com/...

Cache TTL strategy:
  Popular URLs: 1 hour TTL (reloaded frequently, high hit rate)
  All URLs:     evicted with LRU when cache is full
  Expired URLs: TTL in DB is the source of truth — cache serves until eviction
```

**Redis memory math:**
```
Hot URLs (top 20% of URLs = 80% of traffic — Pareto principle):
  20% of 100M = 20M hot URLs
  Each cache entry: 8-byte key + 200-byte value + overhead ≈ 300 bytes
  20M × 300 bytes = ~6 GB Redis memory
  → Fits comfortably in a single Redis node (r6g.xlarge = 32 GB)
```

---

## 7. Analytics — Tracking Clicks Without Slowing Redirects

The naive approach breaks everything:
```
WRONG approach (synchronous write in redirect path):
  1. Look up URL          ← fast (cache hit: 1ms)
  2. UPDATE click_count   ← slow (DB write: 5-20ms, contention at scale)
  3. Log click to DB      ← slow (another DB write)
  4. Return 302           ← delayed by steps 2+3

At 10,000 redirects/second, step 2 creates a write hotspot on every popular URL row.
```

The right approach: async, non-blocking event pipeline.

```
Redirect path (synchronous, critical):           Analytics path (async):
────────────────────────────────────            ──────────────────────────────
1. Cache lookup (Redis): 1ms
2. Return HTTP 302:      <5ms total    ──────▶  Kafka topic: "click-events"
                                                    │
                                                    ▼
                                          Consumer Group: analytics-workers
                                                    │
                                         ┌──────────┴───────────┐
                                         │   Batch aggregator   │
                                         │  (every 5 seconds)   │
                                         └──────────┬───────────┘
                                                    │
                                         ┌──────────▼───────────┐
                                         │  ClickHouse (OLAP)   │  ← raw events
                                         │  DynamoDB counter    │  ← click_count
                                         │  S3 (cold storage)   │  ← raw logs
                                         └──────────────────────┘

Click event schema (emitted per redirect):
{
  "event":      "click",
  "short_code": "dK9mXz",
  "timestamp":  1709900123,
  "user_agent": "Mozilla/5.0...",
  "referer":    "https://twitter.com/...",
  "ip_country": "US",
  "ip_city":    "New York"
}
```

This gives you:
```
Real-time dashboard:  clicks in last 5 minutes (from Kafka consumer)
Historical analytics: clicks by day/country/referer (from ClickHouse)
Total click count:    eventually consistent counter in DynamoDB
```

---

## 8. Scaling the System

Start simple. Scale each layer independently when you hit limits.

### App Server Layer
```
Stateless servers → scale horizontally with a load balancer.

10,000 req/sec, 5ms per request:
  Threads needed ≈ 10,000 × 0.005 = 50 concurrent threads
  A single 4-core server handles this easily.
  Run 3-5 servers for redundancy and rolling deploys.
```

### Database Layer
```
DynamoDB:
  Auto-scaling — just set target utilization (e.g., 70% capacity units).
  Read replicas: DynamoDB Global Tables for multi-region low-latency reads.
  TTL: built-in, no operational overhead for URL expiry.

If using Cassandra:
  Replication factor = 3 (data lives on 3 nodes)
  Read consistency = LOCAL_ONE (fast, eventual)
  Write consistency = LOCAL_QUORUM (strong enough for unique codes)
```

### Cache Layer
```
Redis Cluster:
  Shard by short_code hash → distribute hot keys across nodes
  At 20M cached URLs × 300 bytes = 6 GB → single node is fine to start

  Scale when: memory > 70% OR cache miss rate > 5%

  Sentinel / Cluster mode for HA:
    Primary handles writes
    Replicas handle reads (read scaling)
    Automatic failover if primary dies
```

### CDN for Mega-Popular URLs

```
The top 0.1% of URLs get millions of hits per day (viral content).
These destroy even a warm Redis cache at scale.

Solution: Push the 302 redirect to CDN edge nodes.

  Normal URL:           Client → API Gateway → App Server → Redis → DB
  CDN-cached URL:       Client → CDN Edge Node → (302 response cached)
                                                  ← no origin hit

  Cache-Control: max-age=300  →  CDN caches redirect for 5 minutes
  Risk: stale redirect for 5 minutes if URL is updated or expired.
  Accept this trade-off for viral URLs — analytics become approximate.
```

---

## 9. Trade-offs

Every design decision has a cost. Name them proactively in the interview.

```
Decision                    What you gain             What you lose
─────────────────────────── ───────────────────────── ──────────────────────────
302 over 301                Full analytics, updatable Higher server load
                            destinations              (mitigated by cache)

Redis cache (LRU, 1h TTL)   Redirect latency <5ms     Stale redirects possible
                            Reduced DB load           during TTL window

Async analytics (Kafka)     Zero latency impact on    Click counts are eventually
                            redirects                 consistent (5-sec delay)
                            Durability via Kafka log

NoSQL (DynamoDB)            Horizontal scale,         No complex queries;
                            low-latency KV lookups    analytics DB is separate
                            TTL built-in

Random short codes          Non-enumerable, secure    Tiny collision probability
                            Easy distributed gen      (handled with retry)

CDN for hot URLs            Extreme scale for viral   Analytics blind spot
                            content, low latency      CDN serves cached 302
```

**Consistency vs Availability:**
```
URL redirect is AP (Availability + Partition Tolerance):
  A slightly stale cache entry is fine — user gets redirected, just maybe
  to a recently-updated destination.
  Downtime (no redirect) is worse than a 5-minute stale entry.

Click analytics is AP with eventual consistency:
  Missing 1 click in a million is acceptable.
  Blocking the redirect path for perfect counts is not acceptable.

Custom alias uniqueness is CP:
  Two users claiming the same alias at the same time must be resolved correctly.
  Use DynamoDB conditional writes:  PutItem with ConditionExpression="attribute_not_exists(short_code)"
```

---

## 10. Common Mistakes

These are the answers that separate junior from senior candidates.

**Mistake 1: Sequential auto-increment IDs as short codes**
```
Problem:
  IDs 1, 2, 3, 4, 5 are trivially enumerable.
  An attacker can scrape all shortened URLs by iterating.
  Sensitive URLs (internal docs, medical records behind a short link)
  become publicly accessible.

Fix: Random base62 codes, or at minimum obfuscate IDs (add random salt).
```

**Mistake 2: Ignoring URL expiry**
```
Problem:
  Storing expired URLs forever wastes storage and slows lookups.
  If you have 100M records and 60M are expired, every read scan
  touches dead data.

Fix:
  DynamoDB TTL: set expires_at attribute, DynamoDB auto-deletes.
  Redis TTL: set cache entry TTL slightly shorter than URL TTL.
  Soft-delete first (is_active=false), hard-delete after 30-day grace period.
```

**Mistake 3: No rate limiting**
```
Problem:
  Without rate limiting, a single client can:
  - Generate millions of short codes (waste storage)
  - Enumerate redirects to harvest data
  - DDoS the redirect endpoint

Fix:
  API Gateway rate limiting:
    Anonymous: 10 creates/hour per IP
    Free tier:  100 creates/day per user
    Paid tier:  10,000 creates/day per user
  Redis token bucket: fast, distributed, per-key rate limit.
```

**Mistake 4: Synchronous analytics on the redirect path**
```
Covered in section 7. Never write to a DB synchronously during a redirect.
The redirect path must be as fast as a cache lookup.
```

**Mistake 5: Using 301 redirects without understanding the analytics loss**
```
Every browser that cached a 301 will never come back to your server.
You permanently lose analytics for that user on that URL.
This is the correct choice ONLY if you never need analytics and want
to reduce load above all else (e.g., a link in a published book).
```

**Mistake 6: Single database, no cache**
```
At 10,000 reads/second with <100ms SLA:
  A single Postgres instance:
    ~5,000 reads/sec max before degradation
    At 10,000 req/sec → each query must complete in <0.1ms → impossible for cold data

  Add Redis:
    Cache hit rate of 95%+ for Pareto-distributed traffic
    DB sees only 500 req/sec (the 5% misses)
    DB is comfortable. Cache does the work.
```

---

## Final Architecture (All Together)

```
                            ┌────────────────────────────────────────────────┐
                            │                  CLIENTS                        │
                            │         browsers / apps / bots                 │
                            └───────────────────┬────────────────────────────┘
                                                │ HTTPS
                                    ┌───────────▼──────────┐
                                    │    CDN (CloudFront)   │  Hot URL cache
                                    │    302 responses      │  (5-min TTL)
                                    └───────────┬───────────┘
                                                │ cache miss
                                    ┌───────────▼──────────┐
                                    │     API Gateway       │  Rate limiting
                                    │     (Kong / AWS)      │  Auth validation
                                    └───────────┬───────────┘
                                                │
                          ┌─────────────────────┼──────────────────────┐
                          │                     │                      │
               ┌──────────▼────────┐  ┌─────────▼────────┐  ┌────────▼─────────┐
               │  App Server 1     │  │  App Server 2     │  │  App Server 3    │
               │  (redirect svc)   │  │  (redirect svc)   │  │  (redirect svc)  │
               └──────────┬────────┘  └─────────┬─────────┘  └────────┬─────────┘
                          │                     │                      │
                ┌─────────▼─────────────────────▼──────────────────────▼──────┐
                │                     Redis Cluster                            │
                │              (short_code → long_url cache)                  │
                │              LRU eviction, 1-hour TTL, 6 GB                 │
                └─────────────────────────────┬─────────────────────────────┘
                                              │ cache miss
                                ┌─────────────▼─────────────┐
                                │       DynamoDB             │
                                │  (URL mappings, TTL)       │
                                │  Global Tables for geo     │
                                └─────────────┬─────────────┘
                                              │ (replicated)
                                 ┌────────────▼────────────┐
                                 │   DynamoDB Read Replicas │
                                 │   (eu-west, ap-south)    │
                                 └──────────────────────────┘

                            ANALYTICS PIPELINE
                            ──────────────────
   App Servers ──Kafka──▶ Analytics Workers ──▶ ClickHouse ──▶ Dashboard API
                                            ──▶ DynamoDB (counters)
                                            ──▶ S3 (raw log archive)
```

---

## Navigation

| | |
|---|---|
| Previous | [19 — Clean Architecture](../19_clean_architecture/theory.md) |
| Next | [22 — Twitter Design](./twitter.md) |
| Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Uber Case Study](./uber.md) &nbsp;|&nbsp; **Next:** [WhatsApp Case Study →](./whatsapp.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Netflix Case Study](./netflix.md) · [Twitter Case Study](./twitter.md) · [Uber Case Study](./uber.md) · [WhatsApp Case Study](./whatsapp.md) · [Interview Q&A](./interview.md)
