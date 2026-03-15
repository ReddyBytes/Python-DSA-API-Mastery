# 🎯 Fundamentals — Interview Questions

> Questions that appear in every system design interview. Master these first.

---

## Junior Level

### Q1. What is scalability and what are the two main approaches?

**Answer:**

Scalability is a system's ability to handle increased load without redesign.

**Vertical scaling (scale up):** Add more resources to one machine (more CPU, RAM, disk).
Simple, no code changes, but has a hard ceiling and creates a single point of failure.

**Horizontal scaling (scale out):** Add more machines. Theoretically unlimited,
no single point of failure, but requires stateless design and adds network complexity.

In practice: start vertical (simple), switch to horizontal when you hit limits or need HA.

---

### Q2. What is the difference between latency and throughput?

**Answer:**

- **Latency:** time to complete one operation. "My API responds in 50ms."
- **Throughput:** operations per unit time. "My API handles 10,000 req/s."

They're related but different. A batch processing system can have high throughput
but high latency (each item takes time but many are processed in parallel).
An interactive app needs low latency — users notice anything over ~200ms.

**Always track percentiles, not averages.** A P99 of 2 seconds means 1 in 100
users waits 2 seconds, even if the average is 50ms.

---

### Q3. What is availability and how do you measure it?

**Answer:**

Availability is the percentage of time a system is operational and correct.

| "nines" | Downtime/year |
|---------|--------------|
| 99%     | 3.65 days    |
| 99.9%   | 8.76 hours   |
| 99.99%  | 52 minutes   |
| 99.999% | 5 minutes    |

**Key insight:** availability multiplies in series. If two services are both
required and each has 99% availability: combined = 99% × 99% = 98%.
This is why minimizing required dependencies is a key availability strategy.

---

## Mid-Level

### Q4. Explain the CAP theorem. How does it affect your design decisions?

**Answer:**

In a distributed system with network partitions (which always occur), you must
choose between **Consistency** and **Availability**:

- **CP (Consistency + Partition Tolerance):** Returns error during partition rather than stale data. Good for: financial transactions, distributed locks, auth systems.
- **AP (Availability + Partition Tolerance):** Returns potentially stale data during partition. Good for: social feeds, product catalogs, analytics.

**In practice:** most systems pick a baseline and add knobs. Cassandra is AP by default
but lets you tune consistency per-query (QUORUM reads give stronger consistency at
higher latency). DynamoDB offers eventual or strong consistency per-read.

The right answer isn't always obvious — know your access patterns.

---

### Q5. What is eventual consistency? When is it acceptable?

**Answer:**

Eventual consistency means: if no new writes occur, eventually all replicas will
converge to the same value. Reads may return stale data in the interim.

**Acceptable for:**
- Social media likes/follower counts (being off by a few for seconds is fine)
- Product recommendation engines
- Read replicas for reporting queries
- DNS propagation

**NOT acceptable for:**
- Bank balance (user could overdraw)
- Inventory count (could oversell)
- User authentication tokens
- Distributed locks

**The key question:** "What is the impact of reading stale data?" If the answer
is "annoying but not harmful," eventual consistency is fine.

---

### Q6. What is idempotency and why does it matter for distributed systems?

**Answer:**

An operation is idempotent if applying it multiple times produces the same result as
applying it once.

**Why it matters:** in distributed systems, you can't always know if a request
succeeded (network can fail after the server processes it but before it responds).
Retrying a non-idempotent operation is dangerous:

```
POST /payments { amount: $100 }
→ Server processes, network fails before response
→ Client retries
→ User charged twice!

POST /payments { idempotency_key: "uuid-123", amount: $100 }
→ Server stores key on first call, returns cached result on retry
→ User charged exactly once
```

HTTP method idempotency by design:
- `GET`, `PUT`, `DELETE` — idempotent by spec
- `POST` — NOT idempotent (each call may create a new resource)

---

## Senior Level

### Q7. Walk through back-of-envelope estimation for a URL shortener like bit.ly

**Answer:**

**Assumptions:**
- 100M URLs shortened per day
- 10:1 read-to-write ratio → 1B reads/day
- Average URL: 200 bytes, short code: 7 characters + metadata = ~500 bytes/record
- 10 years retention

**Calculations:**
- Writes: 100M/day ÷ 86,400s = ~1,200 writes/sec (peak: ~3,600)
- Reads: 1B/day = ~11,500 reads/sec (peak: ~35,000)
- Storage: 100M/day × 500 bytes × 365 × 10 = ~183 TB over 10 years

**Implications:**
- Read-heavy (10:1) → aggressive caching (most URLs follow 80/20 — cache hot ones)
- ~35K reads/sec easily handled by Redis + a few app servers
- 183 TB is manageable with a single DB cluster (sharded if needed)
- No real-time constraint → can tolerate eventual consistency on redirect counts

---

### Q8. Explain the difference between SLI, SLO, and SLA

**Answer:**

- **SLI (Service Level Indicator):** the actual metric you measure. "P99 latency = 45ms", "availability this month = 99.97%"
- **SLO (Service Level Objective):** your internal target. "P99 latency must stay under 100ms", "availability ≥ 99.9%"
- **SLA (Service Level Agreement):** the external contract with customers. "We guarantee 99.9% uptime or credit your account"

**The gap matters:** SLO should be tighter than SLA. If SLA is 99.9%, your SLO should be 99.95%. This gives you an error budget to work within before violating your contract.

**Error budget:** `1 - SLO = error budget`. At 99.9%, you have 43 minutes/month to fail. This budget governs deployment frequency and risk tolerance.

---

## 🔥 Rapid-Fire

```
Q: Single point of failure definition?
A: A component whose failure causes total system failure

Q: Difference between active-active and active-passive?
A: Active-active: all nodes serve traffic. Active-passive: primary active, backup waits.

Q: What is backpressure?
A: A signal from overloaded component to upstream to slow down production

Q: Thundering herd problem?
A: Many clients simultaneously request a resource that just expired from cache

Q: What's the 99th percentile latency?
A: 99% of requests complete within this time; 1 in 100 are slower

Q: CAP: which do most NoSQL databases choose?
A: AP (availability + partition tolerance) with eventual consistency

Q: When would you choose strong consistency over availability?
A: Financial transactions, inventory, distributed locks — where stale data causes real harm
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ➡️ Next | [02 — Databases](../05_databases/interview.md) |
| 🏠 Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Api Design — Overview →](../03_api_design/overview.md)

**Related Topics:** [Fundamentals](./fundamentals.md) · [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md)
