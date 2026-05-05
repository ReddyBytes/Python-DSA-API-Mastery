# 🎯 API Performance & Scaling — Interview Preparation

> This file prepares you to discuss API performance and scaling like a working engineer.
> Not just definitions — but real-world usage, trade-offs, and production scenarios.

---

# 🔹 Basic Level Questions (0–2 Years)

**Q1: What is the N+1 query problem and why is it dangerous in production?**

<details>
<summary>💡 Show Answer</summary>

The N+1 problem happens when you fetch a list of N records and then execute a separate database query for each one to load a related resource. For example: fetch 100 orders in one query, then inside a loop load each order's customer with a separate query — that is 101 queries total instead of 2.

In production this is dangerous because it is invisible during development (small datasets hide the cost) but destroys performance at scale. 100 orders becomes 1,001 queries with 1,000 records. Each query has network round-trip latency to the database, so at 1 ms per query that is 1 second of pure query overhead for a single request. The fix is eager loading with joinedload (a SQL JOIN) or batch loading with selectinload plus IN queries.

</details>

<br>

**Q2: What is connection pooling and what happens if you do not configure it correctly?**

<details>
<summary>💡 Show Answer</summary>

A database connection is expensive to create — it involves a TCP handshake, authentication, and session setup. Connection pooling maintains a set of open connections that workers reuse rather than create and destroy per request.

If pool_size is too small, workers queue waiting for a free connection and response times spike. If it is too large across all app servers, you exceed the database's max_connections limit and connections are refused. The sizing formula is (CPU cores × 2) + 1 per worker process. You also need pool_pre_ping=True to discard stale connections from the pool, and pool_recycle to replace connections periodically — without these, long-lived connections go stale and throw errors in production.

</details>

<br>

**Q3: What is the cache-aside pattern and when should you use it?**

<details>
<summary>💡 Show Answer</summary>

Cache-aside (also called lazy loading) is the most common caching pattern for APIs. On a read: check the cache first; if there is a hit, return it directly without touching the database. On a miss, query the database, store the result in the cache with a TTL, then return it. On a write or update, delete (invalidate) the cache entry so the next read repopulates it fresh.

Use it for data that is read frequently but changes infrequently — product catalog, user profiles, configuration. Avoid it for data where stale reads are dangerous (inventory counts in a checkout flow) or for data that changes every request. The key decisions are cache key design (must include all query parameters that affect the result) and TTL (short enough to be fresh, long enough to reduce DB load).

</details>

<br>

**Q4: What is the difference between p50, p95, and p99 latency, and why should you monitor p99 instead of average?**

<details>
<summary>💡 Show Answer</summary>

p50 (median) means 50% of requests completed faster than this value. p95 means 95% of requests completed faster. p99 means 99% of requests completed faster — only 1 in 100 was slower.

Average latency hides outliers. If 99 requests take 10 ms and one takes 10 seconds, the average is ~109 ms — it looks fine, but one in every hundred users is waiting 10 seconds. p99 exposes these outliers. When p50 is slow you have a systematic problem — bad query, missing index. When p50 is fine but p99 is slow you have occasional outliers — lock contention, cache misses, garbage collection pauses. Monitoring both gives you the full picture. Typical SaaS targets: p50 < 100 ms, p95 < 300 ms, p99 < 1,000 ms.

</details>

<br>

**Q5: Why must API servers be stateless for horizontal scaling to work?**

<details>
<summary>💡 Show Answer</summary>

Horizontal scaling means running multiple identical API server instances behind a load balancer. If state (sessions, rate limit counters, in-memory cache) lives inside a single server process, a second request from the same user that routes to a different server will not find that state. The user appears logged out, the rate limit counter resets, or cached data is missing.

Stateless design means every request carries all the information needed to process it (JWT tokens instead of server-side sessions) and shared mutable state lives in an external store — Redis for rate limit counters, session data, and response cache; the database for persistent state. Any server can handle any request, so you can add or remove instances freely and the load balancer does not need sticky sessions.

</details>

<br>

---

# 🔹 Intermediate Level Questions (2–5 Years)

**Q6: When should you use cursor pagination instead of offset pagination, and why?**

<details>
<summary>💡 Show Answer</summary>

Offset pagination (OFFSET 10000 LIMIT 20) requires the database to scan and skip 10,000 rows before returning results. On large tables this is a full sequential scan on the skipped rows — it gets slower with every page. On a 1 million row table, page 50,000 is scanning 1 million rows every time.

Cursor pagination replaces the offset with a WHERE id > last_seen_id clause. The database uses the index to jump directly to the cursor position in O(log n) time regardless of page depth. Use cursor pagination for: tables with 100k+ rows, feeds and timelines, any data that is inserted frequently (offset pagination skips or duplicates rows when inserts happen mid-scroll). Use offset pagination for: admin UIs that need "jump to page N", reports with static data, and small tables where performance is not a concern.

</details>

<br>

**Q7: How do you design cache keys and why does key design matter?**

<details>
<summary>💡 Show Answer</summary>

A cache key must uniquely identify the exact set of data being cached. If any parameter that changes the result is omitted from the key, different requests share the same cache entry and wrong data is served. A product endpoint with filtering needs a key like product:list:category=electronics:status=active:page=2, not just product:list.

Key design also affects invalidation. Flat keys (product:42) are easy to invalidate on update — delete that one key. Pattern-based or tag-based invalidation (delete all keys matching product:list:*) requires Redis SCAN, which is slow on large keyspaces. A common pattern: cache individual objects by ID (product:42), and let list queries expire by TTL rather than actively invalidating them — accept slightly stale list results in exchange for simpler invalidation logic.

</details>

<br>

**Q8: What is a circuit breaker and how does it differ from retry with exponential backoff?**

<details>
<summary>💡 Show Answer</summary>

Both patterns deal with failures in downstream services, but they address different failure modes.

Retry with exponential backoff handles transient failures — a brief network blip, a momentary 503 under load. You retry the same request after an increasing delay (1s, 2s, 4s). This works when the downstream service is temporarily overwhelmed and will recover quickly.

A circuit breaker handles systemic failures — the downstream service is fully down or consistently slow. After a threshold of failures (e.g., 5 in a row) the breaker opens: subsequent calls fail immediately without making a network request. After a reset timeout it enters half-open state and allows one probe request. Success closes the breaker; failure keeps it open. This prevents your API from consuming threads waiting on a service that cannot respond, protecting your own stability and giving the downstream service less load to recover from.

</details>

<br>

**Q9: How do database indexes affect query performance, and what are composite indexes used for?**

<details>
<summary>💡 Show Answer</summary>

An index is a separate data structure (typically a B-tree) that maps column values to row locations. Without an index, a WHERE category = 'electronics' query does a sequential scan of every row. With an index on category, the database traverses the B-tree in O(log n) and reads only matching rows. On a 10 million row table the difference is scanning 10 million rows vs. touching a few hundred.

A composite index covers multiple columns and is used when queries filter or sort on multiple columns together. An index on (category, status) speeds up WHERE category = 'electronics' AND status = 'active' in a single index lookup. The column order matters: the index can satisfy a query filtering only on category (the leading column) but not a query filtering only on status. EXPLAIN ANALYZE in PostgreSQL shows whether a query is doing a sequential scan (needs an index) or an index scan (index is being used).

</details>

<br>

**Q10: Explain the async/await pattern in FastAPI and when it actually improves performance.**

<details>
<summary>💡 Show Answer</summary>

FastAPI runs on an async event loop (via Uvicorn/Starlette). When a route is defined with async def and uses await on I/O operations, the event loop can process other requests while waiting for the I/O to complete — the worker thread is not blocked. This matters for I/O-bound workloads: database queries, HTTP calls to external services, file reads.

The improvement is real only when you await genuinely async operations. If you call a synchronous ORM method inside an async route, you block the event loop — worse than a sync route because no other requests can run. The right pattern is: use async def routes with async database drivers (asyncpg, databases library) and async HTTP clients (httpx.AsyncClient). Use asyncio.gather to fire multiple I/O operations concurrently rather than awaiting them sequentially. For CPU-bound work (image processing, ML inference) async provides no benefit — use a background task queue instead.

</details>

<br>

---

# 🔹 Advanced Level Questions (5+ Years)

**Q11: Walk through how you would diagnose and fix a production API that is slow at p99 but fast at p50.**

<details>
<summary>💡 Show Answer</summary>

This pattern — fast median, slow tail — points to occasional rather than systematic slowness. The investigation starts with slow query logs and APM traces for requests in the p99 bucket. Common causes: lock contention (a write locks rows that reads are waiting on), cache misses on cold-start or after cache invalidation events, garbage collection pauses (Python GC or JVM), and hot spots in the data (a few popular records causing cache misses together).

Diagnosis steps: pull the distribution of response times by endpoint to isolate which endpoint drives p99. Check PostgreSQL pg_stat_activity for waiting queries during slow periods. Look at cache hit rate over time — a sudden dip in hit rate corresponds to a p99 spike. Profile the event loop for async lock contention. Common fixes: add database-level row locking hints to reduce contention, implement request coalescing (one request fetches and populates cache while others wait rather than all going to DB), tune GC, and use read replicas for read-heavy endpoints to reduce lock contention on the primary.

</details>

<br>

**Q12: How do you size a connection pool for a horizontally scaled API and avoid exhausting the database?**

<details>
<summary>💡 Show Answer</summary>

Total connections consumed = app_servers × workers_per_server × pool_size. PostgreSQL's default max_connections is 100 and you should reserve ~20 for admin tasks and migrations, leaving 80 usable. If you have 2 app servers × 4 workers × pool_size of 9 = 72 connections — that fits. Adding a third server would be 108 connections, exceeding the limit.

Levers to pull: reduce pool_size per worker (accepting more queuing), use PgBouncer as a connection pooler (multiplexes many application connections into fewer database connections, allowing a much larger fleet), add read replicas and route read-only queries to them (expanding the total connection budget), or increase PostgreSQL max_connections with appropriate shared_buffers tuning. PgBouncer in transaction pooling mode is the most effective lever for large fleets — it can serve thousands of application connections through a pool of dozens of database connections.

</details>

<br>

**Q13: How do you implement multi-level caching and what are the trade-offs at each level?**

<details>
<summary>💡 Show Answer</summary>

Multi-level caching layers from fastest to slowest: in-process memory cache (Python dict or LRU cache) → Redis → database. The in-process cache has sub-millisecond access and zero network overhead, but it is per-process — each worker has its own copy, memory is limited, and invalidation across processes is complex. It is best for immutable or rarely-changed data (feature flags, static config).

Redis is shared across all workers and servers, making invalidation reliable, but it adds a network round-trip (~0.5–2 ms). It is the right layer for user sessions, per-object caches, and rate limit counters. The database is the source of truth and should be reached only on cache miss.

The main trade-offs: stale data risk increases with each cache layer (in-process cache can be stale for its full TTL after a Redis invalidation), memory pressure must be managed (in-process caches can cause OOM if unbounded), and invalidation complexity grows — you must invalidate all layers on a write. In practice, only add in-process caching for data that is truly static or where microsecond latency matters; Redis is the right default for everything else.

</details>

<br>

**Q14: What would you do if EXPLAIN ANALYZE shows a query using an index but it is still slow?**

<details>
<summary>💡 Show Answer</summary>

An index scan being slow means the index exists but the query is still reading a large amount of data. Common causes: high cardinality in a composite index used in the wrong order (index on (status, category) for a query filtering on category only — the index scan degenerates to a full index scan), table bloat where the index has not been vacuumed and contains many dead tuples, or selectivity — the predicate matches a large fraction of rows so the planner correctly uses the index but there is a lot of data to return.

Diagnosis: check the row estimate vs. actual rows in EXPLAIN ANALYZE — a large discrepancy means stale statistics (run ANALYZE). Check index bloat with pg_stat_user_indexes. Review the query plan for index-only scan (covers all needed columns from the index, much faster) vs. index scan (still reads the heap). Fix options: create a covering index that includes the selected columns (enables index-only scan), reorder composite index columns to match the most selective predicate first, run VACUUM ANALYZE to clean dead tuples and refresh statistics, and partition the table by a high-cardinality column to reduce the scan range.

</details>

<br>
