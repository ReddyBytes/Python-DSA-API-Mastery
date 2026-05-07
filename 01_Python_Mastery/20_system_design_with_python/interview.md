# 🎯 System Design with Python — Interview Preparation Guide  
From Scalable APIs to Distributed Architecture

---

# 🧠 What Interviewers Actually Test

System design interviews evaluate:

- Can you structure a solution logically?
- Can you identify bottlenecks?
- Can you scale horizontally?
- Do you think about failures?
- Can you balance trade-offs?
- Do you consider security and monitoring?

They care about reasoning, not code.

---

# 🔹 Level 1: 2–4 Years Experience

Basic system awareness expected.

---

**Q1: How would you design a simple REST API?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

1. Define endpoints clearly.
2. Use proper HTTP methods.
3. Validate input.
4. Handle errors properly.
5. Use logging.
6. Write unit tests.

Mention stateless design.

</details>

<br>

**Q2: What is stateless architecture and why is it important?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> Stateless services do not store session data locally. This allows easy horizontal scaling and load balancing.

State stored in:

- Database
- Redis
- External storage

Stateless services scale easily.

</details>

<br>

**Q3: How would you handle high traffic on your API?**

<details>
<summary>💡 Show Answer</summary>

Strong structured answer:

- Add load balancer
- Add more application servers
- Add caching layer
- Optimize database queries
- Use asynchronous processing
- Monitor performance metrics

Scalability thinking matters.

</details>


# 🔹 Level 2: 4–7 Years Experience

Now interviewer expects:

- Bottleneck identification
- Caching strategies
- Rate limiting reasoning
- Database scaling awareness

---

**Q4: How would you implement rate limiting?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> I would use a distributed store like Redis to track request counts per user/IP and apply token bucket or sliding window algorithm to enforce limits.

Important:

- Avoid in-memory counter in multi-server system.
- Must be centralized or distributed.

</details>

<br>

**Q5: How would you design caching for high-read system?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

Use cache-aside pattern:

1. Check cache
2. If miss → fetch DB
3. Store in cache
4. Return response

Mention TTL and invalidation strategy.

</details>

<br>

**Q6: What is cache invalidation strategy?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> I use time-based expiration (TTL) or event-based invalidation when underlying data changes.

Also mention:
Cache consistency trade-offs.

</details>

<br>

**Q7: How would you scale a database?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

- Add indexes
- Use read replicas
- Separate read and write traffic
- Shard data if necessary
- Optimize queries

Database often bottleneck.

</details>

<br>

**Q8: What is horizontal scaling?**

<details>
<summary>💡 Show Answer</summary>

Adding more servers.

Mention:

Stateless design required.

</details>


# 🔹 Level 3: 7–10 Years Experience

Now discussion becomes architectural and failure-oriented.

---

**Q9: How would you design a scalable URL shortener?**

<details>
<summary>💡 Show Answer</summary>

Strong structured answer:

1. Define requirements.
2. Estimate traffic.
3. API servers behind load balancer.
4. Use hash-based short code.
5. Store mapping in distributed database.
6. Cache hot URLs in Redis.
7. Use read replicas.
8. Monitor metrics.
9. Implement rate limiting.
10. Plan for data sharding.

Shows structured thinking.

</details>

<br>

**Q10: How would you handle system failures?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

- Implement retries with exponential backoff.
- Use circuit breaker pattern.
- Add timeouts.
- Graceful degradation.
- Log errors.
- Alert monitoring systems.

Resilience thinking is critical.

</details>

<br>

**Q11: How do you design for high availability?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

- Deploy multiple instances.
- Use load balancer.
- Use multi-AZ or multi-region.
- Avoid single point of failure.
- Backup and recovery strategy.

High availability mindset.

</details>

<br>

**Q12: What trade-offs do you consider in caching?**

<details>
<summary>💡 Show Answer</summary>

Trade-offs:

- Freshness vs speed
- Memory usage vs latency
- Consistency vs availability

Mention CAP theorem if relevant.

</details>

<br>

**Q13: How would you design a distributed task processing system?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

- API receives request.
- Push task to message queue (Kafka/RabbitMQ).
- Worker processes tasks asynchronously.
- Store results in DB.
- Monitor worker health.
- Retry failed tasks.

Shows asynchronous architecture thinking.

</details>


# 🔥 Scenario-Based Questions

---

## Scenario 1:

Your API latency spikes randomly.

<details>
<summary>💡 Show Answer</summary>

Possible causes:

- Database slow query
- Cache miss burst
- Network issue
- Blocking operation
- Insufficient worker processes

Structured investigation required.

</details>
---

## Scenario 2:

Cache memory usage grows uncontrollably.

<details>
<summary>💡 Show Answer</summary>

Possible cause:

- No TTL
- Poor invalidation
- Large objects stored

Solution:
Define expiration strategy.

</details>
---

## Scenario 3:

Database CPU at 100%.

<details>
<summary>💡 Show Answer</summary>

Solution:

- Add indexes
- Optimize queries
- Use caching
- Introduce read replicas
- Reduce N+1 queries

System bottleneck awareness.

</details>
---

## Scenario 4:

System must handle 10x traffic growth.

<details>
<summary>💡 Show Answer</summary>

Solution:

- Horizontal scaling
- Stateless services
- Add caching
- Partition data
- Optimize infrastructure

Scalability thinking.

</details>
---

## Scenario 5:

Third-party API occasionally fails.

<details>
<summary>💡 Show Answer</summary>

Solution:

- Retry with backoff
- Circuit breaker
- Timeout control
- Fallback mechanism

Resilience awareness.

</details>
---

# 🧠 How to Answer Like a Strong Candidate

Weak:

“I would add more servers.”

Strong:

> “I would first analyze where the bottleneck lies—application, database, or network. Based on that, I would apply horizontal scaling, introduce caching, optimize queries, and ensure stateless architecture for better load balancing.”

Structured.
Calm.
Logical.

---

# ⚠️ Common Weak Candidate Mistakes

- Jumping to scaling without measuring
- Ignoring database bottlenecks
- Not considering failure scenarios
- Ignoring security and rate limiting
- Not thinking about monitoring
- Overcomplicating simple systems

System design is about balanced thinking.

---

# 🎯 Rapid-Fire Revision

- Stateless services scale easily
- Use load balancer for traffic distribution
- Use caching for high-read systems
- Rate limit to prevent abuse
- Database indexing improves performance
- Horizontal scaling > vertical scaling for large systems
- Use message queues for async processing
- Always plan for failures
- Monitor everything

---

# 🏆 Final Interview Mindset

System design interviews evaluate:

- Structured problem-solving
- Trade-off awareness
- Scalability thinking
- Failure handling
- Calm reasoning

If you demonstrate:

- Step-by-step approach
- Clear bottleneck analysis
- Awareness of caching & rate limiting
- Database scaling knowledge
- Failure resilience
- Monitoring strategy

You appear as senior engineer capable of handling real systems.

System design is not about perfect answer.

It is about structured reasoning.

---

# 🔌 Additional Topics — Pattern Deep Dives

---

## Circuit Breaker Pattern (3 States)

**Q: Explain the three states of a circuit breaker and when each transition happens.**

<details>
<summary>💡 Show Answer</summary>

**CLOSED** (normal operation):
Calls pass through. Failure counter increments on each failure. When `failure_count >= threshold` → transition to OPEN.

**OPEN** (fast fail):
All calls are rejected immediately without calling downstream — no waiting for timeouts. After `recovery_timeout` seconds have elapsed → transition to HALF_OPEN.

**HALF_OPEN** (testing):
One test request is allowed through. If it succeeds → back to CLOSED (reset failure count). If it fails → back to OPEN (reset timeout).

```
CLOSED → (failures >= threshold) → OPEN
OPEN   → (timeout elapsed)       → HALF_OPEN
HALF_OPEN → (success)            → CLOSED
HALF_OPEN → (failure)            → OPEN
```

Why it matters: without a circuit breaker, a slow downstream service causes request threads to pile up and exhaust the thread pool, crashing your entire service.

</details>

<br>

---

## Token Bucket vs Sliding Window

**Q: Compare token bucket and sliding window rate limiters. When would you choose each?**

<details>
<summary>💡 Show Answer</summary>

**Token Bucket:**
- A bucket holds N tokens (capacity = max burst size)
- Tokens refill at `rate` tokens/second
- Each request consumes 1 token
- Allows short bursts (up to capacity) then enforces average rate
- Memory: O(1) per client
- Used by: AWS API Gateway, Stripe, GitHub

**Sliding Window:**
- Stores timestamp of every request in a deque
- On each request: remove timestamps older than window, count remaining
- More accurate — no boundary burst problem
- Memory: O(max_requests) per client
- Used for: strict per-second enforcement, no burst tolerance

**Choose Token Bucket when:**
You want to allow clients to burst (download a large file, batch requests) as long as their long-run average stays within limits.

**Choose Sliding Window when:**
You need strict enforcement — e.g., a free-tier API where every request above limit must be rejected regardless of timing.

</details>

<br>

---

## Cursor vs Offset Pagination

**Q: What is cursor-based pagination and when should you use it over offset pagination?**

<details>
<summary>💡 Show Answer</summary>

**Offset pagination:** `GET /items?offset=20&limit=10`
- Simple: skip N rows, return next M
- Problem: if a row is inserted before offset 20 while paginating, you skip a record on the next page
- Problem: `OFFSET 10000 LIMIT 10` on a large DB forces a full table scan of 10,010 rows
- Good for: small datasets, admin UIs where jumping to any page is needed

**Cursor pagination:** `GET /items?cursor=eyJpZCI6IDIwfQ&limit=10`
- Cursor = base64-encoded pointer to the last seen item (usually an ID or timestamp)
- Stable: inserts/deletes don't affect pagination — the cursor anchors to a specific row
- Efficient: `WHERE id > 20 LIMIT 10` uses an index, no full scan
- Downside: can't jump to "page 5" — must follow cursor chain

**Choose cursor when:** large datasets, data changes frequently, stable pagination matters (social feeds, payment history).

**Choose offset when:** small datasets, the user needs to jump to a specific page number, or total count display is required.

</details>

<br>

---

## Idempotency Key Pattern

**Q: What is an idempotency key and why is it important for payment APIs?**

<details>
<summary>💡 Show Answer</summary>

An **idempotency key** is a unique client-generated ID sent with a mutating request (POST/PUT). The server stores the key + response. If the same key is submitted again (due to retry), the server returns the cached response instead of processing again.

**Why payments:** A client sends `POST /payments` for $100. The network times out. Did the payment go through? The client retries. Without idempotency keys, the user is charged twice.

**How it works:**
1. Client generates a UUID: `Idempotency-Key: a3f9-12bc-4d88`
2. Server checks: has this key been seen?
   - Yes → return cached response (same payment_id, same status)
   - No → process payment, store key + response in Redis
3. Client can safely retry any number of times

**Storage:** Use Redis with a TTL (e.g., 24 hours). Key = `idem:{key}`, Value = JSON response.

Used by: Stripe, PayPal, AWS, every serious payment processor.

</details>

<br>

---

# 🔁 Navigation

Previous:  
[20_system_design_with_python/theory.md](./theory.md)

Next:  
[21_data_engineering_applications/theory.md](../21_data_engineering_applications/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Scalable App Design](./scalable_app_design.md) &nbsp;|&nbsp; **Next:** [Data Engineering Applications — Theory →](../21_data_engineering_applications/theory.md)

**Related Topics:** [Theory](./theory.md) · [API Design Principles](./api_design_principles.md) · [Scalable App Design](./scalable_app_design.md)
