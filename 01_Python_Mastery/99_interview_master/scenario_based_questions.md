# 🎯 Python Interview Master — Scenario-Based Questions  
Real Production Problems & Structured Solutions

---

# 🧠 How to Approach Scenario Questions

Before answering:

1. Clarify requirements.
2. Ask questions if needed.
3. Break problem into layers.
4. Identify bottleneck.
5. Suggest structured solution.
6. Mention trade-offs.
7. Stay calm.

Never jump to random solution.

Structured reasoning wins.

---

# 🔥 Scenario 1: API Suddenly Becomes Slow

### Situation:
Your API response time increased from 200ms to 3 seconds.

---

## How to Answer

Step-by-step:

1. Check monitoring dashboards.
2. Identify whether issue is:
   - Application layer
   - Database
   - External service
   - Network
3. Use profiler if needed.
4. Analyze slow queries.
5. Check recent deployments.
6. Add caching if needed.
7. Scale horizontally if load increased.

Mention:

“Measure before optimizing.”

### Trade-offs to Mention

- **Adding cache:** Reduces DB load but risks stale data. Ask: “How stale is acceptable?”
- **Horizontal scaling:** Helps if CPU-bound but not if DB is the bottleneck.
- **Query optimization:** Fastest fix with lowest risk, always start here.
- **Circuit breaker on external services:** Adds resilience but complexity.

### Follow-up Questions an Interviewer Might Ask

- “The slow query is an N+1 query. How do you fix it?”
  → Eager loading / `select_related` / batch loading. Show the query difference.
- “After caching, you see stale data for 2 minutes. The business says 0 stale data. What now?”
  → Cache invalidation on write, event-driven invalidation, or no caching for that endpoint.
- “How would you test this in production without impacting users?”
  → Shadow traffic, feature flags, canary deploy.

---

# 🔥 Scenario 2: Memory Usage Keeps Increasing

### Situation:
Your service runs fine initially but memory keeps growing.

---

## Structured Analysis

Possible causes:

- Memory leak
- Global list accumulating data
- Cache without eviction
- Large objects not released
- Circular references

Steps:

1. Use tracemalloc.
2. Analyze object growth.
3. Check long-lived references.
4. Add TTL to cache.
5. Refactor memory-heavy logic.

### Structured Diagnosis

```
Step 1: Reproduce locally
  memory_profiler → @profile decorator on suspected function
  tracemalloc → snapshot before/after the operation

Step 2: Identify the object type leaking
  import objgraph
  objgraph.show_growth()      # shows which object types are growing
  objgraph.show_backrefs(obj) # shows what's holding the object alive

Step 3: Common culprits
  □ Global dict/list that grows per request (cache without eviction)
  □ Circular references in custom objects with __del__
  □ Event listeners / callbacks never unregistered
  □ Thread-local storage in long-running threads
  □ Large objects held in exception tracebacks (sys.exc_info())
```

### Trade-offs

- **Using weakref for cache:** Memory efficient but objects may disappear unexpectedly.
- **TTL-based cache eviction:** Simple but may evict hot data.
- **Disabling GC (`gc.disable()`):** Faster in some cases but risks circular reference accumulation.

### Follow-up

- "How do you find a memory leak in production (can't modify code)?"
  → `py-spy`, `memray`, `/proc/{pid}/status`, or heap dump from the process.
- "What's the difference between a memory leak and memory bloat?"
  → Leak: memory grows unbounded, objects are unreachable but not collected.
  → Bloat: memory is large but all objects are intentionally kept (e.g., large cache).

---

# 🔥 Scenario 3: Duplicate Data in Pipeline

### Situation:
After rerunning ETL job, duplicates appear.

---

## Answer Approach

Root cause:

No idempotency.

Solution:

- Use upsert instead of insert.
- Add unique constraint.
- Track processed IDs.
- Implement checkpointing.

Mention idempotency clearly.

---

# 🔥 Scenario 4: Multithreaded App Crashes Randomly

### Situation:
App using threading occasionally fails.

---

## Possible Causes

- Race condition
- Shared mutable state
- No synchronization
- Deadlock

Solution:

- Use locks
- Use thread-safe data structures
- Reduce shared state
- Use multiprocessing if CPU-bound

Explain [GIL](../13_concurrency/theory.md#-chapter-2-the-gil--pythons-most-misunderstood-feature) if needed.

---

# 🔥 Scenario 5: Async App Not Performing Well

### Situation:
You implemented async but performance didn't improve.

---

## Analysis

Possible cause:

Blocking synchronous call inside async function.

Solution:

- Identify blocking operations.
- Use async-compatible libraries.
- Use thread pool for blocking calls.

Mention event loop awareness.

---

# 🔥 Scenario 6: High Database CPU Usage

### Situation:
Database CPU at 100%.

---

## Answer Approach

Possible reasons:

- Missing index
- Heavy join
- N+1 query problem
- Large table scan

Solution:

- Add indexes
- Optimize queries
- Add caching
- Use read replicas
- Reduce unnecessary queries

Database often bottleneck.

---

# 🔥 Scenario 7: Service Works Locally But Fails in Production

### Situation:
Works locally, fails in production.

---

## Common Causes

- Missing environment variable
- Dependency mismatch
- File path differences
- OS differences
- Network restrictions

Steps:

1. Compare environments.
2. Check logs.
3. Validate configuration.
4. Verify dependency versions.

Production awareness matters.

---

# 🔥 Scenario 8: Third-Party API Fails Randomly

### Situation:
External API sometimes times out.

---

## Strong Answer

- Add timeout handling.
- Retry with exponential backoff.
- Use circuit breaker.
- Log failures.
- Gracefully degrade feature if needed.

Resilience thinking required.

---

# 🔥 Scenario 9: Traffic Suddenly Increases 10x

### Situation:
Your app must handle 10x users.

---

## Structured Approach

1. Check bottlenecks.
2. Ensure stateless architecture.
3. Add load balancer.
4. Scale horizontally.
5. Add caching layer.
6. Optimize database.
7. Monitor performance.

Never jump directly to “add servers”.

---

# 🔥 Scenario 10: Test Suite Is Very Slow

### Situation:
Tests take 20 minutes to run.

---

## Solution

- Parallelize tests.
- Mock heavy operations.
- Reduce integration tests.
- Separate slow and fast tests.
- Optimize fixtures.

Testing discipline matters.

---

# 🔥 Scenario 11: Cache Causes Stale Data

### Situation:
Users see outdated data.

---

## Solution

- Add TTL.
- Invalidate cache on update.
- Use event-based invalidation.
- Balance consistency vs performance.

Trade-off awareness.

---

# 🔥 Scenario 12: Kafka Consumer Lagging Behind

### Situation:
Consumer falling behind producer.

---

## Causes

- Processing slow
- Insufficient workers
- Heavy transformation logic

Solution:

- Scale consumers
- Optimize processing
- Add partitioning
- Monitor offsets

Streaming knowledge.

---

# 🔥 Scenario 13: Race Condition Bug

### Situation:
Balance calculation incorrect in concurrent environment.

---

## Fix

- Use locks
- Use atomic database operations
- Avoid shared mutable state
- Use transactions

Concurrency maturity required.

---

# 🔥 Scenario 14: Deployment Broke Production

### Situation:
New release caused outage.

---

## Professional Response

1. Rollback immediately.
2. Stabilize system.
3. Analyze logs.
4. Identify root cause.
5. Add regression test.
6. Improve CI pipeline.

Never blame.
Focus on fix.

---

# 🔥 Scenario 15: Large CSV Processing Crashes

### Situation:
Processing 5GB CSV crashes app.

---

## Solution

- Stream file line-by-line.
- Process in chunks.
- Avoid loading full file.
- Use generators.
- Use batch inserts.

Memory efficiency awareness.

---

# 🔥 Scenario 16: Database is the Bottleneck — System Slows Under Load

### Situation:
Your system handles 1,000 req/sec normally. After a feature launch, you're at 5,000 req/sec and DB CPU is at 95%. Read latency went from 5ms to 800ms.

---

### Structured Diagnosis

```
Step 1: Identify query patterns
  EXPLAIN ANALYZE on slow queries
  Look for: sequential scans, missing indexes, N+1 patterns

Step 2: Check connection pool
  Are connections being exhausted?
  pool_size too small → requests queue up waiting for connection

Step 3: Read/Write split analysis
  What % of queries are reads?
  If >80% reads → read replicas can help

Step 4: Cache candidates
  Which queries return the same result frequently?
  User profile? Product catalog? Config data?
```

### Solution Hierarchy (cheapest to most expensive)

```
1. Add missing indexes          → O(1) query time, zero infra cost
2. Fix N+1 queries              → batch/eager load
3. Add query result cache       → Redis, 5ms → 0.1ms, risk: staleness
4. Connection pool tuning       → (cores × 2 + 1) connections per server
5. Read replica                 → offload reads, adds lag complexity
6. Vertical scaling             → quick but expensive ceiling
7. Sharding                     → last resort, massive complexity
```

### Trade-offs to Discuss

- **Index every column?** No — indexes slow writes. Only index columns in WHERE, JOIN, ORDER BY clauses.
- **Read replica lag:** Typically 10-100ms. Fine for product catalog. Not fine for "just paid, show balance."
- **Cache invalidation strategy:** Write-through (always consistent, slower writes) vs TTL (simpler, stale window).

### Follow-up Questions

- "You add a read replica but users sometimes see stale data right after a write. How do you fix this?"
  → Read-your-writes consistency: route reads for the current user to primary for N seconds after a write.
- "An index exists but the query planner isn't using it. Why?"
  → Statistics are stale (ANALYZE), data cardinality too low, query pattern bypasses index (LIKE '%term').
- "What's a covering index and when does it help?"
  → Index contains all columns needed by the query — no heap fetch needed. 10-50× faster for read-heavy.

---

# 🔥 Scenario 17: Design a Rate Limiter for an API

### Situation:
Your public API is being abused. Some clients send 10,000 req/sec. You need to limit each client to 100 req/min.

---

### The Solution Space

```
Algorithm options:
  1. Fixed window counter:   easy, but burst at window boundary
  2. Sliding window log:     accurate, high memory (store all timestamps)
  3. Sliding window counter: good balance (approximate, low memory)
  4. Token bucket:           allows bursts up to bucket size, smooth overall
  5. Leaky bucket:           constant rate output, no bursts allowed
```

### Token Bucket Implementation

```python
import time
import redis

def is_allowed(client_id: str, limit: int = 100, window_seconds: int = 60) -> bool:
    """
    Sliding window rate limiter using Redis.
    limit: max requests per window
    """
    r = redis.Redis()
    key = f"rate:{client_id}"
    now = time.time()
    window_start = now - window_seconds

    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)    # remove old requests
    pipe.zadd(key, {str(now): now})                # add current request
    pipe.zcount(key, window_start, now)            # count in window
    pipe.expire(key, window_seconds)               # auto-cleanup
    _, _, count, _ = pipe.execute()

    return count <= limit
```

### Trade-offs

- **In-memory (single server):** Fast, no network hop. Fails if server restarts or multiple servers.
- **Redis-based:** Distributed, persistent. Adds ~1ms latency. Redis becomes a single point of failure.
- **Approximate vs exact:** Sliding window counter (approximate) vs sliding window log (exact). Log uses O(requests) memory per client.

### Follow-up Questions

- "Your Redis rate limiter goes down. What happens?"
  → Fail open (allow all traffic — risk abuse) vs fail closed (block all — risk legitimate users). Design choice, document it.
- "How do you handle IP spoofing or shared IP addresses (corporate NAT)?"
  → Combine IP with API key. Or use user account ID as the rate limit key.
- "Your rate limiter adds 1ms to every request. Can you eliminate that?"
  → Client-side rate limiting in an API gateway (Kong, Nginx), no extra network hop.

---

# 🧠 How to Sound Like Senior Engineer

Structure your answers:

- Clarify issue
- Identify layer
- Propose solution
- Mention trade-offs
- Mention monitoring
- Mention prevention

Example:

> “I would first identify whether the bottleneck is at application, database, or infrastructure level. Based on profiling data, I would apply caching or optimize queries. I would also ensure proper monitoring to prevent recurrence.”

Calm.
Logical.
Structured.

---

# ⚠️ Common Weak Responses

- Guessing solution immediately
- Overcomplicating simple problem
- Ignoring monitoring
- Ignoring failure handling
- No structured approach
- Panicking under pressure

Structured calm reasoning wins interviews.

---

# 🎯 Final Scenario Preparation Checklist

- Practice structured thinking
- Always measure before optimizing
- Understand idempotency
- Know concurrency pitfalls
- Know memory debugging tools
- Understand database bottlenecks
- Know retry and resilience patterns
- Think in layers: app → DB → network → infrastructure
- Explain trade-offs clearly

---

# 🏆 Final Mindset

Scenario-based interviews test:

- Real-world experience
- Problem-solving under pressure
- System thinking
- Engineering maturity
- Calm decision-making

If you stay structured,
think in layers,
consider failures,
mention monitoring,
and explain trade-offs,

You will stand out.

---

# 🔁 Navigation

Previous:  
[99_interview_master/python_3_5_years.md](./python_3_5_years.md)

Next:  
[99_interview_master/tricky_edge_cases.md](./tricky_edge_cases.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Python 3-5 Years](./python_3_5_years.md) &nbsp;|&nbsp; **Next:** [Tricky Edge Cases →](./tricky_edge_cases.md)

**Related Topics:** [Python 0-2 Years](./python_0_2_years.md) · [Python 3-5 Years](./python_3_5_years.md) · [Tricky Edge Cases](./tricky_edge_cases.md)
