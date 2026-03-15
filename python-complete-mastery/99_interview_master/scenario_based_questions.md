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

Explain GIL if needed.

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
