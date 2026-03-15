# The Art of Caching
## Why Smart Systems Remember Things

> The fastest request is the one you never make.

---

## Part 1: Why Cache Exists — The Newspaper Analogy

Every morning a newspaper is printed. It contains today's stock prices,
news, sports scores. Millions of people want to read it.

Now imagine if every single reader had to personally drive to the printing
press to read their copy. The press would be crushed. The commute would
take an hour each way. Nobody would bother.

Instead: newspapers are printed once, distributed to every corner store,
and people pick up their local copy. The information is the same.
The trip is 2 minutes instead of 2 hours.

That is caching.

```
Without cache:
  User request → Application → Database server → response
                                    ^
                            (far away, slow, expensive)


With cache:
  User request → Application → Cache (RAM, nearby) → response
                                    ^
                       (copy of DB data, fast to access)

  Only on cache miss:
  User request → Application → Cache (miss) → Database → response
                                                 ^ also updates cache ^
```

You keep a copy of the data closer to where it's needed.
The "printing press" (database) serves the data once or infrequently.
Everyone else reads from the local copy.

---

## Part 2: The Cache Hit vs Miss — The Numbers That Matter

This is not an abstract concept. The latency gap between a cache hit
and a cache miss is one of the largest performance gaps in computing.

```
┌──────────────────────────────────────────────────────────────┐
│                   Latency Reality Check                      │
│                                                              │
│  RAM read (cache hit)          ~100 nanoseconds              │
│  Database read (cache miss)    ~1-10 milliseconds            │
│                                                              │
│  That is a 10,000× to 100,000× difference.                   │
│                                                              │
│  To make this concrete:                                      │
│    If a cache hit = 1 second                                 │
│    Then a DB read = 2.7 hours to 27 hours                    │
└──────────────────────────────────────────────────────────────┘
```

In a real application: your API has 50ms to respond before users
notice slowness. A single DB query can take 10-50ms. If your API
makes 5 DB queries, you're already at 50-250ms — before any
application logic runs.

Cache a single result? 0.1ms. Budget freed for everything else.

**Cache hit rate** is the percentage of requests that find their data
in cache. Even modest hit rates have dramatic effects:

```
100 requests/second to a database:

  0% hit rate:   100 DB queries/sec (baseline)
  50% hit rate:   50 DB queries/sec (2× reduction)
  90% hit rate:   10 DB queries/sec (10× reduction)
  99% hit rate:    1 DB query/sec   (100× reduction)

Most production caches target 90-99% hit rates.
```

---

## Part 3: Redis in 60 Seconds

**Redis** stands for Remote Dictionary Server. It is, at its core,
a database that lives entirely in RAM.

Why is it fast?

```
Two design choices that make Redis extremely fast:

1. Everything in RAM
   No disk I/O. No seek time. No buffer pool management.
   Your data is always in memory, always one pointer lookup away.

2. Single-threaded command execution
   Redis processes one command at a time, in order.
   No locks. No mutexes. No thread contention.
   No time wasted on synchronization.

   ┌─────────────────────────────────────────────────┐
   │  Command queue:  [GET user:1] [SET x 5] [GET y] │
   │                       │                         │
   │  Single thread:   processes them one at a time  │
   │                   each in ~1 microsecond         │
   │                                                 │
   │  Result: 100,000+ operations per second         │
   │          on a single Redis node                 │
   └─────────────────────────────────────────────────┘
```

Redis is not just a simple key → string store. It has data structures:

```
Data structures in Redis:

  String:      SET user:1:name "Alice"
               GET user:1:name          → "Alice"
               INCR page:views          → 1, 2, 3, ...  (atomic counter)

  Hash:        HSET user:1 name "Alice" email "a@b.com" age 30
               HGET user:1 name         → "Alice"
               HGETALL user:1           → all fields

  List:        RPUSH queue job_1 job_2 job_3   (append)
               LPOP queue                      → job_1 (consume from front)
               (Use case: job queues, activity feeds)

  Set:         SADD online_users user:1 user:2 user:3
               SISMEMBER online_users user:1   → 1 (yes)
               SCARD online_users              → 3 (count)
               (Use case: unique visitors, tags, memberships)

  Sorted Set:  ZADD leaderboard 1500 "alice"
               ZADD leaderboard 2300 "bob"
               ZRANGE leaderboard 0 -1 WITHSCORES  → bob:2300, alice:1500
               (Use case: leaderboards, rate limiting, time-ordered events)

  Expires:     SET session:abc123 "..." EX 3600   (expires in 1 hour)
               TTL session:abc123                 → 3598 (seconds left)
```

---

## Part 4: Cache Patterns

There is no single "right way" to cache. The four major patterns
differ in when data is loaded into cache, when it is written back
to the database, and what happens on failure.

---

### Pattern 1: Cache-Aside (Lazy Loading)

The most common pattern. The application manages the cache directly.

```
READ path:

  ┌──────────────┐
  │ Application  │
  └──────┬───────┘
         │ 1. Check cache first
         ▼
  ┌──────────────┐
  │    Cache     │ ──── HIT ────> return cached data  (fast path)
  └──────┬───────┘
         │ MISS
         │ 2. Go to database
         ▼
  ┌──────────────┐
  │   Database   │ ──── returns data
  └──────┬───────┘
         │ 3. Populate cache for next time
         ▼
  ┌──────────────┐
  │    Cache     │ (now has the data)
  └──────────────┘
         │ 4. Return data to caller
```

```python
def get_user(user_id):
    # Step 1: check cache
    cached = redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)               # cache hit

    # Step 2: load from DB
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)

    # Step 3: populate cache (with 1-hour TTL)
    redis.setex(f"user:{user_id}", 3600, json.dumps(user))

    # Step 4: return
    return user
```

WRITE path: writes go directly to the database. Cache is NOT updated.
The cached copy becomes stale and will expire via TTL.

```
Pros:
  + Simple to implement
  + Cache only fills with data that is actually requested
  + Database failure on cache miss doesn't break cached reads

Cons:
  - First request after miss is always slow (cold start)
  - Stale data between write and TTL expiry
  - Cache and DB can diverge if TTL is long
```

---

### Pattern 2: Write-Through

Every write goes to both the cache AND the database, together.

```
WRITE path:

  ┌──────────────┐
  │ Application  │
  └──────┬───────┘
         │ 1. Write to cache
         ▼
  ┌──────────────┐
  │    Cache     │
  └──────┬───────┘
         │ 2. Immediately also write to database
         ▼
  ┌──────────────┐
  │   Database   │
  └──────────────┘
         │ 3. Both confirmed → return success
```

```python
def update_user(user_id, data):
    # Write to DB
    db.execute("UPDATE users SET ... WHERE id = ?", user_id, data)

    # Immediately update cache too
    redis.setex(f"user:{user_id}", 3600, json.dumps(data))

    return data
```

```
Pros:
  + Cache is always consistent with the database
  + No stale reads immediately after a write
  + Every read is a cache hit (eventually)

Cons:
  - Every write is slower (must write two places)
  - Cache fills with data that may never be read
  - Write failures must handle partial state
    (DB success but cache failure = inconsistency)
```

---

### Pattern 3: Write-Behind (Write-Back)

The riskiest pattern. Writes go to cache first, database later.

```
WRITE path:

  ┌──────────────┐
  │ Application  │
  └──────┬───────┘
         │ 1. Write to cache only
         ▼
  ┌──────────────┐
  │    Cache     │  ← returns success immediately
  └──────┬───────┘
         │
         │ 2. Asynchronously, sometime later...
         ▼
  ┌──────────────┐
  │   Database   │  ← flushed in batch
  └──────────────┘
```

```
Pros:
  + Writes are extremely fast (RAM only, no DB wait)
  + DB writes are batched (fewer round trips, better throughput)
  + Absorbs write spikes without DB overload

Cons:
  - DATA LOSS RISK: if cache crashes before flushing, writes are gone
  - Complexity: must handle flush failures, ordering, retries
  - Not suitable for financial data or anything that must survive a crash
```

Write-behind is used in high-throughput, write-heavy workloads
where losing a small amount of recent data is acceptable.
Games (score updates), analytics counters, view counts.
Never for financial transactions.

---

### Pattern 4: Read-Through

The cache itself knows how to load from the database.
The application only ever talks to the cache.

```
READ path:

  ┌──────────────┐
  │ Application  │
  └──────┬───────┘
         │ "Give me user:1"
         ▼
  ┌──────────────────────────────┐
  │           Cache              │
  │                              │
  │  HIT  → return immediately   │
  │                              │
  │  MISS → cache itself queries │
  │         the database,        │
  │         stores result,       │
  │         returns to caller    │
  └──────────────────────────────┘
```

The difference from Cache-Aside: the application does not know
or care whether data came from cache or database. The cache
handles that logic internally.

```
Pros:
  + Clean application code (one data source to query)
  + Cache fills automatically on misses

Cons:
  - Requires a cache that supports "read-through" (e.g. DAX for DynamoDB)
  - First read is always slow (same cold start problem as Cache-Aside)
  - Less control over cache population logic
```

---

### Choosing a Pattern

```
Pattern       │ Read complexity │ Write complexity │ Staleness risk │ Data loss risk
──────────────┼─────────────────┼──────────────────┼────────────────┼───────────────
Cache-Aside   │ Medium          │ Low              │ Medium (TTL)   │ None
Write-Through │ Low             │ Medium           │ Low            │ None
Write-Behind  │ Low             │ Low              │ Low            │ HIGH
Read-Through  │ Low             │ N/A              │ Medium         │ None

Start with Cache-Aside. It is the most widely used pattern
for a reason: it is simple, predictable, and safe.
```

---

## Part 5: Cache Eviction Policies

Your cache has finite memory. When it fills up, something must be removed
to make room. The eviction policy decides what gets dropped.

### LRU — Least Recently Used

Remove the item that was accessed least recently.

```
Cache state (max 3 items):

  Access: A → [A]
  Access: B → [A, B]
  Access: C → [A, B, C]  (full)
  Access: D → [B, C, D]  (A evicted — longest since last use)
  Access: B → [C, D, B]  (B moved to front, still hot)
  Access: A → [D, B, A]  (C evicted — now the least recent)
```

LRU assumes: if you used it recently, you'll use it again soon.
Good for general-purpose caches, user session data, database query results.

---

### LFU — Least Frequently Used

Remove the item that has been accessed the fewest times overall.

```
Cache state (max 3 items, tracking access counts):

  Item A: accessed 15 times (popular)
  Item B: accessed  2 times (barely used)
  Item C: accessed  8 times (moderate use)

  New item D needs space: evict B (lowest frequency)
```

LFU assumes: frequently accessed items will continue to be accessed.
Good for: recommendation caches, product catalogs with power-law
access patterns (a few items are wildly popular).

Downside: a new item starts with frequency 1, so it can be evicted
immediately even if it would become popular — the "cache pollution"
problem for new data.

---

### TTL — Time To Live

Every item has an expiry time. When the clock runs out, it's gone.

```
SET user:1:profile { ... } EX 3600     ← expires in 3600 seconds (1 hour)
SET hot_deals_list  { ... } EX 300     ← expires in 5 minutes
SET static_config   { ... } EX 86400   ← expires in 24 hours
```

TTL is not an eviction policy in the same sense — it's scheduled
expiration. But it is how you control staleness and prevent cache
from holding outdated data forever.

Use TTL for: anything time-sensitive (sessions, rate limit windows,
pricing data, feature flags). The TTL is your "freshness contract."

---

### Which Policy to Use

```
Use case                          Recommended policy
──────────────────────────────    ──────────────────
General page/query caching        LRU
Session storage                   TTL (sessions expire naturally)
API response caching              LRU + TTL (both: evict AND expire)
Recommendation results            LFU
Rate limiting counters            TTL (fixed windows)
Hot product catalog               LFU (popular items stay warm)
Leaderboards                      TTL (refresh on schedule)
```

In Redis: configure with `maxmemory-policy`. Common choices:
`allkeys-lru`, `volatile-lru` (LRU only on keys with TTL set).

---

## Part 6: The Cache Invalidation Problem

> "There are only two hard things in computer science:
>  cache invalidation and naming things."
>  — Phil Karlton

The hardest question in caching: when the underlying data changes,
how do you update (or remove) the cached copy?

### The Problem

```
Timeline:

  t=0:  User A's profile cached: { name: "Alice", email: "a@old.com" }
  t=1:  Alice updates her email to "a@new.com"  (DB is updated)
  t=2:  User B views Alice's profile
        → Cache hit! Returns { email: "a@old.com" }   ← WRONG
  t=3600: Cache expires
  t=3601: User B views again → cache miss → DB read → correct data
```

Alice's old email was shown for an hour.
For a profile picture, that's annoying.
For a product price, that's a refund waiting to happen.
For permissions ("is this user an admin?"), that's a security hole.

### Invalidation Strategies

**Strategy 1: TTL-based expiry (accept stale)**
Set a short TTL. Stale data is automatically bounded.
```
Best for: data that changes slowly (product descriptions, config)
Tradeoff: stale data up to TTL duration
```

**Strategy 2: Explicit invalidation on write**
When data changes, delete the cache entry immediately.
```python
def update_user_email(user_id, new_email):
    db.execute("UPDATE users SET email = ? WHERE id = ?", new_email, user_id)
    redis.delete(f"user:{user_id}")    # invalidate immediately
    # Next read will miss and re-populate from DB
```
```
Best for: data that must be fresh after writes
Tradeoff: requires write path to know all relevant cache keys
```

**Strategy 3: Versioned cache keys**
Add a version number to the key. "Invalidating" means bumping the version.
```
Before update: cache key = "user:1:v5"
After  update: cache key = "user:1:v6"

Old key (v5) is now unreachable. It will expire by TTL.
New key (v6) is populated on first read.
```
```
Best for: complex objects with many derived cache keys
Tradeoff: old versions sit in cache until TTL (wasted memory)
```

**The honest reality:** perfect cache freshness is very hard.
You must decide: what is the cost of serving stale data?
For most data, a short TTL (seconds to minutes) is "fresh enough."
For financial data and permissions, don't cache or use explicit invalidation.

---

## Part 7: What NOT to Cache

Not everything belongs in cache. Caching the wrong data causes
subtle, hard-to-debug bugs in production.

```
Do NOT cache:

  Financial transactions
    → Stale account balances are worse than slow account balances.
      Always read the source of truth for money.

  Security-critical data (permissions, session validity)
    → If a user is banned and their "is_active=true" is cached
      for 1 hour, they spend 1 hour still accessing your system.
      Revocations must be immediate.

  Unique data with no repetition
    → Caching "get user 12345" when every user is queried once ever
      is pure overhead: populate cache, read once, never hit again.
      Cache hit rate = 0%. Pure waste.

  Data that changes on every request
    → "Current server time", real-time stock prices, live sports scores.
      Caching something that changes every second just adds complexity
      with no benefit.

  Large objects that rarely save you a DB query
    → Caching 5MB of rarely-accessed data to save a 1ms query
      is a bad trade. Cache memory is finite.

Rule of thumb:
  Cache data that is:  READ OFTEN  +  CHANGES RARELY  +  COSTS SOMETHING TO COMPUTE
```

---

## Part 8: CDN — A Cache for Static Content

A CDN (Content Delivery Network) is a global network of cache servers,
geographically distributed, designed to serve static assets — images,
CSS, JavaScript files, videos — from a server close to the user.

```
Without CDN:
  User in Tokyo → requests image → origin server in US-East
  Round-trip: ~150ms (physics: the internet crosses the Pacific)

With CDN:
  User in Tokyo → requests image → CDN node in Tokyo
  Round-trip: ~5ms (CDN node is in the same city)

  The CDN node fetched the image from US-East once.
  Now serves it to every Tokyo user without crossing the ocean.
```

For most applications: put static assets (images, JS, CSS) on a CDN.
It is one of the easiest and highest-impact performance improvements
you can make. AWS CloudFront, Cloudflare, Fastly are common choices.
Dynamic API responses are generally not CDN-cached (they vary per user).

---

## Key Numbers to Remember

```
┌───────────────────────────────────────────────────────────┐
│                  Cache Performance Reference              │
│                                                           │
│  RAM read speed:                    ~100 nanoseconds      │
│  Redis GET latency (local):         ~100 microseconds     │
│  Redis GET latency (network hop):   ~1 millisecond        │
│  Database query (fast, indexed):    ~1-10 milliseconds    │
│  Database query (slow, scanning):   ~100ms - 10 seconds   │
│                                                           │
│  Redis throughput (single node):    ~100,000 ops/second   │
│  Redis throughput (cluster):        millions of ops/sec   │
│                                                           │
│  Target cache hit rate (most apps): 90-99%                │
│                                                           │
│  Common TTL ranges:
│    Session tokens:              15 minutes - 24 hours     │
│    API responses:               30 seconds - 5 minutes    │
│    Database query results:      1 minute - 1 hour         │
│    Static config / feature flags: 1 hour - 24 hours       │
└───────────────────────────────────────────────────────────┘
```

---

## The Mental Models to Carry Forward

```
1. The goal of caching is not to be clever.
   It is to reduce work: fewer DB queries, faster responses.

2. Cache hit rate is the metric. Optimize for it.
   A 95% hit rate means your DB sees 5% of your traffic.

3. Cache-Aside is the safe default. Use it first.
   Reach for Write-Through when you need freshness after writes.
   Avoid Write-Behind unless you truly cannot afford the write latency.

4. TTL is your freshness contract.
   Short TTL = fresher data, more DB load.
   Long TTL = more stale data, less DB load.
   Pick based on how wrong a stale answer would be.

5. Cache invalidation is hard because distributed systems have
   no global "right now." Accept that your cache can be slightly
   stale, and design your system to tolerate it.

6. CDN for static assets is almost always worth doing.
   It is the cheapest, most impactful performance win available.
```

---

## Navigation

| | |
|---|---|
| Previous | [05 — Databases](../05_databases/the_story_of_data.md) |
| Next | [07 — Storage & CDN](../07_storage_cdn/theory.md) |
| Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
