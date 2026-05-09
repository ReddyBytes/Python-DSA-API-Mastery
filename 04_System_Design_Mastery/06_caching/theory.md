<a id="top"></a>

# 1. The Art of Caching

Kishore stares at his terminal at 2 AM. His Telugu food delivery app just got featured on a popular tech blog, and traffic has spiked 10x. The database server is melting — every user request hammers the same product listings, the same restaurant menus, the same delivery zones. The same data, fetched fresh from disk, thousands of times per second.

His senior architect messages him: "Kishore, the fastest request is the one you never make. Put a cache in front of the database. Let the system remember what it already knows."

That night, Kishore implements Redis caching. Response times drop from 800ms to 12ms. The database CPU drops from 95% to 15%. The app survives its first traffic spike. And Kishore learns the lesson that every backend engineer eventually learns: smart systems remember things.

> "The fastest request is the one you never make."

<a id="toc"></a>

## Table of Contents

- [1. The Art of Caching](#1-the-art-of-caching)
- [2. Why Cache Exists](#2-why-cache-exists)
- [3. Cache Hit vs Miss](#3-cache-hit-vs-miss)
- [4. Redis in 60 Seconds](#4-redis-in-60-seconds)
- [5. Cache Patterns](#5-cache-patterns)
  - [Cache-Aside (Lazy Loading)](#cache-aside-lazy-loading)
  - [Write-Through](#write-through)
  - [Write-Behind (Write-Back)](#write-behind-write-back)
  - [Read-Through](#read-through)
  - [Choosing a Pattern](#choosing-a-pattern)
- [6. Cache Eviction Policies](#6-cache-eviction-policies)
  - [LRU — Least Recently Used](#lru--least-recently-used)
  - [LFU — Least Frequently Used](#lfu--least-frequently-used)
  - [TTL — Time To Live](#ttl--time-to-live)
  - [Which Policy to Use](#which-policy-to-use)
- [7. The Cache Invalidation Problem](#7-the-cache-invalidation-problem)
  - [The Problem](#the-problem)
  - [Invalidation Strategies](#invalidation-strategies)
- [8. What NOT to Cache](#8-what-not-to-cache)
- [9. CDN — A Cache for Static Content](#9-cdn--a-cache-for-static-content)
- [10. Key Numbers to Remember](#10-key-numbers-to-remember)
- [11. Mental Models to Carry Forward](#11-mental-models-to-carry-forward)
- [12. Learning Priority](#12-learning-priority)
- [13. Practice Questions](#13-practice-questions)
- [14. Summary](#14-summary)

[Back to Top](#top)

<a id="2-why-cache-exists"></a>

# 2. Why Cache Exists

Kishore thinks of his grandmother's kitchen in Hyderabad. Every morning she makes fresh idli batter — but she does not grind rice from scratch each time. She keeps a jar of pre-ground rice flour on the counter. When she needs batter, the flour is right there. No trip to the market. No grinding stone. Instant access to something she prepared once and uses many times.

That jar is a cache. The market is the database. The grinding stone is the expensive computation.

Every morning a newspaper is printed. It contains today's stock prices, news, sports scores. Millions of people want to read it. Now imagine if every single reader had to personally drive to the printing press to read their copy. The press would be crushed. The commute would take an hour each way. Nobody would bother.

Instead: newspapers are printed once, distributed to every corner store, and people pick up their local copy. The information is the same. The trip is 2 minutes instead of 2 hours.

That is caching.

```
Without cache:
  User request --> Application --> Database server --> response
                                       ^
                               (far away, slow, expensive)


With cache:
  User request --> Application --> Cache (RAM, nearby) --> response
                                       ^
                          (copy of DB data, fast to access)

  Only on cache miss:
  User request --> Application --> Cache (miss) --> Database --> response
                                                    ^ also updates cache ^
```

You keep a copy of the data closer to where it's needed. The "printing press" (database) serves the data once or infrequently. Everyone else reads from the local copy.

Kishore's food delivery app has 50,000 restaurants. But at any given time, users are browsing maybe 500 of them — the ones in their delivery zone during peak dinner hours. Caching those 500 restaurant menus means 99% of requests never touch the database at all.

[Back to Top](#top)

<a id="3-cache-hit-vs-miss"></a>

# 3. Cache Hit vs Miss

This is not an abstract concept. The latency gap between a cache hit and a cache miss is one of the largest performance gaps in computing.

```
+--------------------------------------------------------------+
|                   Latency Reality Check                       |
|                                                              |
|  RAM read (cache hit)          ~100 nanoseconds              |
|  Database read (cache miss)    ~1-10 milliseconds            |
|                                                              |
|  That is a 10,000x to 100,000x difference.                  |
|                                                              |
|  To make this concrete:                                      |
|    If a cache hit = 1 second                                 |
|    Then a DB read = 2.7 hours to 27 hours                    |
+--------------------------------------------------------------+
```

Kishore runs the math for his app. His API has a 50ms budget before users notice slowness. A single database query for a restaurant menu takes 15ms. If the user's home screen requires 5 queries (nearby restaurants, promotions, user preferences, delivery zones, order history), that is 75ms — already over budget, before any application logic runs.

Cache a single result? 0.1ms. Budget freed for everything else.

**Cache hit rate** is the percentage of requests that find their data in cache. Even modest hit rates have dramatic effects:

```
100 requests/second to a database:

  0% hit rate:   100 DB queries/sec (baseline)
  50% hit rate:   50 DB queries/sec (2x reduction)
  90% hit rate:   10 DB queries/sec (10x reduction)
  99% hit rate:    1 DB query/sec   (100x reduction)

Most production caches target 90-99% hit rates.
```

Kishore monitors his cache after deployment. Day 1: 72% hit rate. He adjusts TTLs, warms the cache for popular restaurants during pre-dinner hours, and removes low-value keys. By day 3: 94% hit rate. His database now handles 6% of the original traffic. The server bill drops accordingly.

[Back to Top](#top)

<a id="4-redis-in-60-seconds"></a>

# 4. Redis in 60 Seconds

**Redis** stands for Remote Dictionary Server. It is, at its core, a database that lives entirely in RAM.

Kishore's team chooses Redis because it is the industry standard for application caching. But why is it so fast?

```
Two design choices that make Redis extremely fast:

1. Everything in RAM
   No disk I/O. No seek time. No buffer pool management.
   Your data is always in memory, always one pointer lookup away.

2. Single-threaded command execution
   Redis processes one command at a time, in order.
   No locks. No mutexes. No thread contention.
   No time wasted on synchronization.

   +-----------------------------------------------------+
   |  Command queue:  [GET user:1] [SET x 5] [GET y]     |
   |                       |                              |
   |  Single thread:   processes them one at a time       |
   |                   each in ~1 microsecond             |
   |                                                     |
   |  Result: 100,000+ operations per second             |
   |          on a single Redis node                     |
   +-----------------------------------------------------+
```

Redis is not just a simple key to string store. It has data structures:

```
Data structures in Redis:

  String:      SET user:1:name "Alice"
               GET user:1:name          --> "Alice"
               INCR page:views          --> 1, 2, 3, ...  (atomic counter)

  Hash:        HSET user:1 name "Alice" email "a@b.com" age 30
               HGET user:1 name         --> "Alice"
               HGETALL user:1           --> all fields

  List:        RPUSH queue job_1 job_2 job_3   (append)
               LPOP queue                      --> job_1 (consume from front)
               (Use case: job queues, activity feeds)

  Set:         SADD online_users user:1 user:2 user:3
               SISMEMBER online_users user:1   --> 1 (yes)
               SCARD online_users              --> 3 (count)
               (Use case: unique visitors, tags, memberships)

  Sorted Set:  ZADD leaderboard 1500 "alice"
               ZADD leaderboard 2300 "bob"
               ZRANGE leaderboard 0 -1 WITHSCORES  --> bob:2300, alice:1500
               (Use case: leaderboards, rate limiting, time-ordered events)

  Expires:     SET session:abc123 "..." EX 3600   (expires in 1 hour)
               TTL session:abc123                 --> 3598 (seconds left)
```

Kishore uses Redis Hashes for restaurant profiles (HSET restaurant:42 name "Bawarchi" cuisine "Biryani" rating 4.5), Sorted Sets for the "top rated near you" feature (ZADD nearby:zone7 4.5 "restaurant:42"), and simple Strings with TTL for session tokens.

[Back to Top](#top)

<a id="5-cache-patterns"></a>

# 5. Cache Patterns

There is no single "right way" to cache. The four major patterns differ in when data is loaded into cache, when it is written back to the database, and what happens on failure.

Kishore needs to pick a pattern for each type of data in his app. He learns them all to make informed decisions.

<a id="cache-aside-lazy-loading"></a>

## Cache-Aside (Lazy Loading)

The most common pattern. The application manages the cache directly.

```
READ path:

  +----------------+
  |  Application   |
  +-------+--------+
          | 1. Check cache first
          v
  +----------------+
  |     Cache      | ---- HIT ----> return cached data  (fast path)
  +-------+--------+
          | MISS
          | 2. Go to database
          v
  +----------------+
  |    Database    | ---- returns data
  +-------+--------+
          | 3. Populate cache for next time
          v
  +----------------+
  |     Cache      | (now has the data)
  +----------------+
          | 4. Return data to caller
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

WRITE path: writes go directly to the database. Cache is NOT updated. The cached copy becomes stale and will expire via TTL.

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

Kishore uses Cache-Aside for restaurant menus. Menus are read thousands of times per hour but updated only when the restaurant owner changes them. A 10-minute TTL means at worst a user sees a slightly outdated menu — acceptable for his use case.

[Back to Top](#top)

<a id="write-through"></a>

## Write-Through

Every write goes to both the cache AND the database, together.

```
WRITE path:

  +----------------+
  |  Application   |
  +-------+--------+
          | 1. Write to cache
          v
  +----------------+
  |     Cache      |
  +-------+--------+
          | 2. Immediately also write to database
          v
  +----------------+
  |    Database    |
  +----------------+
          | 3. Both confirmed --> return success
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

Kishore uses Write-Through for user profile data. When a user updates their delivery address, the next order must use the correct address — stale data here means a delivery to the wrong location. The slight write latency increase is worth the consistency guarantee.

[Back to Top](#top)

<a id="write-behind-write-back"></a>

## Write-Behind (Write-Back)

The riskiest pattern. Writes go to cache first, database later.

```
WRITE path:

  +----------------+
  |  Application   |
  +-------+--------+
          | 1. Write to cache only
          v
  +----------------+
  |     Cache      |  <-- returns success immediately
  +-------+--------+
          |
          | 2. Asynchronously, sometime later...
          v
  +----------------+
  |    Database    |  <-- flushed in batch
  +----------------+
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

Write-behind is used in high-throughput, write-heavy workloads where losing a small amount of recent data is acceptable. Games (score updates), analytics counters, view counts. Never for financial transactions.

Kishore uses Write-Behind for one thing only: restaurant view counts. When users browse restaurants, every page view increments a counter. These writes happen thousands of times per second during peak hours. If Redis crashes and he loses 30 seconds of view counts, nobody notices. But if those writes hit the database directly, the DB would buckle under the load.

[Back to Top](#top)

<a id="read-through"></a>

## Read-Through

The cache itself knows how to load from the database. The application only ever talks to the cache.

```
READ path:

  +----------------+
  |  Application   |
  +-------+--------+
          | "Give me user:1"
          v
  +-------------------------------+
  |            Cache              |
  |                               |
  |  HIT  --> return immediately  |
  |                               |
  |  MISS --> cache itself queries|
  |          the database,        |
  |          stores result,       |
  |          returns to caller    |
  +-------------------------------+
```

The difference from Cache-Aside: the application does not know or care whether data came from cache or database. The cache handles that logic internally.

```
Pros:
  + Clean application code (one data source to query)
  + Cache fills automatically on misses

Cons:
  - Requires a cache that supports "read-through" (e.g. DAX for DynamoDB)
  - First read is always slow (same cold start problem as Cache-Aside)
  - Less control over cache population logic
```

[Back to Top](#top)

<a id="choosing-a-pattern"></a>

## Choosing a Pattern

```
Pattern       | Read complexity | Write complexity | Staleness risk | Data loss risk
--------------+-----------------+------------------+----------------+---------------
Cache-Aside   | Medium          | Low              | Medium (TTL)   | None
Write-Through | Low             | Medium           | Low            | None
Write-Behind  | Low             | Low              | Low            | HIGH
Read-Through  | Low             | N/A              | Medium         | None

Start with Cache-Aside. It is the most widely used pattern
for a reason: it is simple, predictable, and safe.
```

Kishore's rule of thumb: "If I would get paged at 2 AM because the data was wrong, I use Write-Through or explicit invalidation. If nobody would notice stale data for 10 minutes, Cache-Aside with TTL is simpler and cheaper."

[Back to Top](#top)

<a id="6-cache-eviction-policies"></a>

# 6. Cache Eviction Policies

Your cache has finite memory. When it fills up, something must be removed to make room. The eviction policy decides what gets dropped.

Kishore's Redis instance has 2GB of RAM. His restaurant data alone could fill 10GB if he cached everything. He must choose wisely what stays and what goes.

<a id="lru--least-recently-used"></a>

## LRU -- Least Recently Used

Remove the item that was accessed least recently.

```
Cache state (max 3 items):

  Access: A --> [A]
  Access: B --> [A, B]
  Access: C --> [A, B, C]  (full)
  Access: D --> [B, C, D]  (A evicted -- longest since last use)
  Access: B --> [C, D, B]  (B moved to front, still hot)
  Access: A --> [D, B, A]  (C evicted -- now the least recent)
```

LRU assumes: if you used it recently, you will use it again soon. Good for general-purpose caches, user session data, database query results.

<a id="lfu--least-frequently-used"></a>

## LFU -- Least Frequently Used

Remove the item that has been accessed the fewest times overall.

```
Cache state (max 3 items, tracking access counts):

  Item A: accessed 15 times (popular)
  Item B: accessed  2 times (barely used)
  Item C: accessed  8 times (moderate use)

  New item D needs space: evict B (lowest frequency)
```

LFU assumes: frequently accessed items will continue to be accessed. Good for: recommendation caches, product catalogs with power-law access patterns (a few items are wildly popular).

Downside: a new item starts with frequency 1, so it can be evicted immediately even if it would become popular — the "cache pollution" problem for new data.

<a id="ttl--time-to-live"></a>

## TTL -- Time To Live

Every item has an expiry time. When the clock runs out, it is gone.

```
SET user:1:profile { ... } EX 3600     <-- expires in 3600 seconds (1 hour)
SET hot_deals_list  { ... } EX 300     <-- expires in 5 minutes
SET static_config   { ... } EX 86400   <-- expires in 24 hours
```

TTL is not an eviction policy in the same sense — it is scheduled expiration. But it is how you control staleness and prevent cache from holding outdated data forever.

Use TTL for: anything time-sensitive (sessions, rate limit windows, pricing data, feature flags). The TTL is your "freshness contract."

<a id="which-policy-to-use"></a>

## Which Policy to Use

```
Use case                          Recommended policy
------------------------------    ------------------
General page/query caching        LRU
Session storage                   TTL (sessions expire naturally)
API response caching              LRU + TTL (both: evict AND expire)
Recommendation results            LFU
Rate limiting counters            TTL (fixed windows)
Hot product catalog               LFU (popular items stay warm)
Leaderboards                      TTL (refresh on schedule)
```

In Redis: configure with `maxmemory-policy`. Common choices: `allkeys-lru`, `volatile-lru` (LRU only on keys with TTL set).

Kishore configures his Redis with `allkeys-lru` and 2GB max memory. Restaurant menus that nobody has browsed in hours get evicted automatically, making room for the restaurants people are actively ordering from during dinner rush.

[Back to Top](#top)

<a id="7-the-cache-invalidation-problem"></a>

# 7. The Cache Invalidation Problem

> "There are only two hard things in computer science: cache invalidation and naming things." — Phil Karlton

The hardest question in caching: when the underlying data changes, how do you update (or remove) the cached copy?

<a id="the-problem"></a>

## The Problem

Kishore discovers this the hard way. A restaurant owner updates their menu — removes a dish that sold out. But for the next 10 minutes, customers keep ordering that dish because the cached menu still shows it. Orders fail at the kitchen. Customers complain. The restaurant owner calls support.

```
Timeline:

  t=0:  User A's profile cached: { name: "Alice", email: "a@old.com" }
  t=1:  Alice updates her email to "a@new.com"  (DB is updated)
  t=2:  User B views Alice's profile
        --> Cache hit! Returns { email: "a@old.com" }   <-- WRONG
  t=3600: Cache expires
  t=3601: User B views again --> cache miss --> DB read --> correct data
```

Alice's old email was shown for an hour. For a profile picture, that is annoying. For a product price, that is a refund waiting to happen. For permissions ("is this user an admin?"), that is a security hole.

<a id="invalidation-strategies"></a>

## Invalidation Strategies

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

**The honest reality:** perfect cache freshness is very hard. You must decide: what is the cost of serving stale data? For most data, a short TTL (seconds to minutes) is "fresh enough." For financial data and permissions, do not cache or use explicit invalidation.

Kishore's solution for the restaurant menu problem: when a restaurant owner saves menu changes, the API explicitly invalidates the cache key (`redis.delete(f"restaurant:{id}:menu")`). The next customer request triggers a cache miss, loads the fresh menu, and populates cache again. Problem solved — zero stale menus after an owner update.

[Back to Top](#top)

<a id="8-what-not-to-cache"></a>

# 8. What NOT to Cache

Not everything belongs in cache. Caching the wrong data causes subtle, hard-to-debug bugs in production.

Kishore learns this when his team caches delivery driver locations. The cache TTL is 60 seconds. But a driver moves 1 km in 60 seconds. Customers see a driver "arriving" when the driver is still 5 minutes away. The data changes too fast to cache meaningfully.

```
Do NOT cache:

  Financial transactions
    --> Stale account balances are worse than slow account balances.
        Always read the source of truth for money.

  Security-critical data (permissions, session validity)
    --> If a user is banned and their "is_active=true" is cached
        for 1 hour, they spend 1 hour still accessing your system.
        Revocations must be immediate.

  Unique data with no repetition
    --> Caching "get user 12345" when every user is queried once ever
        is pure overhead: populate cache, read once, never hit again.
        Cache hit rate = 0%. Pure waste.

  Data that changes on every request
    --> "Current server time", real-time stock prices, live sports scores.
        Caching something that changes every second just adds complexity
        with no benefit.

  Large objects that rarely save you a DB query
    --> Caching 5MB of rarely-accessed data to save a 1ms query
        is a bad trade. Cache memory is finite.

Rule of thumb:
  Cache data that is:  READ OFTEN  +  CHANGES RARELY  +  COSTS SOMETHING TO COMPUTE
```

[Back to Top](#top)

<a id="9-cdn--a-cache-for-static-content"></a>

# 9. CDN -- A Cache for Static Content

A **CDN** (Content Delivery Network) is a global network of cache servers, geographically distributed, designed to serve static assets — images, CSS, JavaScript files, videos — from a server close to the user.

Kishore's app serves restaurant photos. High-resolution food images are 500KB each. With 50,000 restaurants and 5 photos each, that is 125GB of images. Every user's home screen loads 20 photos. Without a CDN, every image request crosses the network to his origin server in Mumbai.

```
Without CDN:
  User in Chennai --> requests image --> origin server in Mumbai
  Round-trip: ~80ms (network distance + server load)

With CDN:
  User in Chennai --> requests image --> CDN node in Chennai
  Round-trip: ~5ms (CDN node is in the same city)

  The CDN node fetched the image from Mumbai once.
  Now serves it to every Chennai user without crossing the distance.
```

For most applications: put static assets (images, JS, CSS) on a CDN. It is one of the easiest and highest-impact performance improvements you can make. AWS CloudFront, Cloudflare, Fastly are common choices. Dynamic API responses are generally not CDN-cached (they vary per user).

Kishore moves all restaurant photos to CloudFront. Page load time drops by 400ms. His origin server bandwidth bill drops by 80%. The CDN handles the heavy lifting of serving images globally.

[Back to Top](#top)

<a id="10-key-numbers-to-remember"></a>

# 10. Key Numbers to Remember

```
+-----------------------------------------------------------+
|                  Cache Performance Reference               |
|                                                           |
|  RAM read speed:                    ~100 nanoseconds      |
|  Redis GET latency (local):         ~100 microseconds     |
|  Redis GET latency (network hop):   ~1 millisecond        |
|  Database query (fast, indexed):    ~1-10 milliseconds    |
|  Database query (slow, scanning):   ~100ms - 10 seconds   |
|                                                           |
|  Redis throughput (single node):    ~100,000 ops/second   |
|  Redis throughput (cluster):        millions of ops/sec   |
|                                                           |
|  Target cache hit rate (most apps): 90-99%                |
|                                                           |
|  Common TTL ranges:                                       |
|    Session tokens:              15 minutes - 24 hours     |
|    API responses:               30 seconds - 5 minutes    |
|    Database query results:      1 minute - 1 hour         |
|    Static config / feature flags: 1 hour - 24 hours       |
+-----------------------------------------------------------+
```

[Back to Top](#top)

<a id="11-mental-models-to-carry-forward"></a>

# 11. Mental Models to Carry Forward

Kishore writes these on a sticky note above his monitor. Six months later, he still references them when designing new features:

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

[Back to Top](#top)

<a id="12-learning-priority"></a>

# 12. Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
cache-aside (lazy loading), write-through, write-behind, TTL and expiry, eviction policies (LRU/LFU)

**Should Learn** — Important for real projects, comes up regularly:
Redis data structures, cache stampede and thundering herd prevention, CDN caching

**Good to Know** — Useful in specific situations, not always tested:
multi-tier caching (L1 app / L2 Redis / L3 CDN), cache key design patterns

**Reference** — Know it exists, look up syntax when needed:
bloom filters for negative caching, cache warm-up strategies, cache coherency

[Back to Top](#top)

<a id="13-practice-questions"></a>

# 13. Practice Questions

> **Practice:** [Q16 - cache-when-to-use](../system_design_practice_questions_100.md#q16--normal--cache-when-to-use)
> **Practice:** [Q17 - cache-hit-miss](../system_design_practice_questions_100.md#q17--normal--cache-hit-miss)
> **Practice:** [Q18 - cache-eviction-policies](../system_design_practice_questions_100.md#q18--normal--cache-eviction-policies)
> **Practice:** [Q31 - redis-use-cases](../system_design_practice_questions_100.md#q31--normal--redis-use-cases)
> **Practice:** [Q32 - redis-vs-memcached](../system_design_practice_questions_100.md#q32--interview--redis-vs-memcached)
> **Practice:** [Q38 - cache-write-strategies](../system_design_practice_questions_100.md#q38--thinking--cache-write-strategies)
> **Practice:** [Q84 - compare-redis-db-sessions](../system_design_practice_questions_100.md#q84--interview--compare-redis-db-sessions)
> **Practice:** [Q87 - production-cache-stampede](../system_design_practice_questions_100.md#q87--design--production-cache-stampede)
> **Practice:** [Q93 - design-distributed-cache](../system_design_practice_questions_100.md#q93--design--design-distributed-cache)

[Back to Top](#top)

<a id="14-summary"></a>

# 14. Summary

| Concept | Key Takeaway |
|---------|-------------|
| Cache purpose | Reduce work: fewer DB queries, faster responses |
| Cache-Aside | App manages cache; lazy load on miss; most common pattern |
| Write-Through | Write to cache + DB together; strong consistency; slower writes |
| Write-Behind | Write to cache, flush to DB later; fast but risky (data loss) |
| Read-Through | Cache itself loads from DB on miss; clean app code |
| LRU | Evict least recently used; best general-purpose policy |
| LFU | Evict least frequently used; best for power-law access |
| TTL | Scheduled expiry; your freshness contract with the data |
| Invalidation | Hardest problem; use explicit delete on write for critical data |
| CDN | Global edge cache for static assets; easiest performance win |
| Redis | In-memory, single-threaded, 100K+ ops/sec; industry standard |
| Hit rate target | 90-99% for production systems |

[Back to Top](#top)

<a id="navigation"></a>

## Navigation

| Link | Destination |
|------|-------------|
| Previous | [05 - Databases](../05_databases/theory.md) |
| Next | [07 - Storage and CDN](../07_storage_cdn/theory.md) |
| Home | [System Design Mastery](../README.md) |
| Interview | [interview.md](./interview.md) |
| Cheatsheet | [cheetsheet.md](./cheetsheet.md) |

**Prev:** [Databases](../05_databases/theory.md) | **Next:** [Storage and CDN](../07_storage_cdn/theory.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) | [Interview Q&A](./interview.md)
