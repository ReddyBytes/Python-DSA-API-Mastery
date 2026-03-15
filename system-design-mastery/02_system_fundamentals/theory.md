# 🏛️ System Design Fundamentals

> The vocabulary, mental models, and core trade-offs that underpin every
> system design decision. Master these before touching any specific technology.

---

## 📋 Contents

```
1.  What makes a system "good"?
2.  Scalability — handling growth
3.  Availability — staying up
4.  Reliability — doing the right thing
5.  Latency vs throughput
6.  CAP theorem — the fundamental trade-off
7.  PACELC — CAP's practical extension
8.  Consistency models spectrum
9.  Fault tolerance patterns
10. Back-of-envelope estimation
11. The vocabulary every interviewer expects
```

---

## 1. What Makes a System "Good"?

There is no single definition. A good system is **fit for its purpose**.
But across all systems, five properties matter most:

```
┌─────────────────────────────────────────────────────────────┐
│  SCALABILITY    Can it grow without being redesigned?        │
│  AVAILABILITY   Is it accessible when users need it?         │
│  RELIABILITY    Does it do what it promises?                  │
│  PERFORMANCE    Is it fast enough for its users?              │
│  MAINTAINABILITY Can engineers change it safely over time?   │
└─────────────────────────────────────────────────────────────┘
```

These properties conflict. Optimizing for one often sacrifices another.
A senior engineer doesn't find the perfect design — they make the right
**trade-offs** for the specific context.

---

## 2. Scalability

Scalability is a system's ability to handle **increased load** without
a complete redesign.

### Vertical Scaling (Scale Up)

Add more resources to one machine:

```
┌─────────────────┐       ┌─────────────────────┐
│  Server         │  →→   │  Server (bigger)      │
│  4 CPU cores    │       │  32 CPU cores         │
│  16 GB RAM      │       │  256 GB RAM           │
│  500 GB SSD     │       │  10 TB SSD            │
└─────────────────┘       └─────────────────────┘
```

**Pros:** Simple. No code change. Low latency (no network hop).
**Cons:** Hard ceiling (can't scale infinitely). Single point of failure.
Expensive at high end. Requires downtime to upgrade.

### Horizontal Scaling (Scale Out)

Add more machines:

```
                    ┌──────────────┐
                    │ Load Balancer│
                    └──────┬───────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Server 1 │    │ Server 2 │    │ Server 3 │
    └──────────┘    └──────────┘    └──────────┘
```

**Pros:** Theoretically unlimited. No single point of failure. Commodity hardware.
**Cons:** Complexity. Need stateless design or sticky sessions. Network overhead.
Distributed systems are hard to reason about.

### Stateless vs Stateful

```
Stateless server:  Each request contains all info needed. Any server can handle it.
                   → Easy to horizontal scale

Stateful server:   Server remembers previous requests (session state).
                   → Hard to horizontal scale (must route to same server)
```

**Rule:** Keep servers stateless. Move state to a shared layer (Redis, DB).

---

## 3. Availability

Availability = percentage of time a system responds correctly.

```
Availability   Downtime per year     Downtime per month
────────────────────────────────────────────────────────
99%            ~3.65 days            ~7.3 hours
99.9%          ~8.76 hours           ~43.8 minutes
99.99%         ~52.6 minutes         ~4.4 minutes
99.999%        ~5.26 minutes         ~26 seconds   ← "five nines"
99.9999%       ~31.5 seconds         ~2.6 seconds
```

### SLA vs SLO vs SLI

```
SLI (Service Level Indicator):  actual measurement
  "Current availability = 99.95%"

SLO (Service Level Objective):  internal target
  "We aim for 99.9% availability"

SLA (Service Level Agreement):  external contract
  "We guarantee 99.9% or you get a refund"
```

### Availability in Series vs Parallel

```
Two components in SERIES (both must work):
  Component A availability: 99%
  Component B availability: 99%
  Combined: 99% × 99% = 98.01%   ← worse than either alone!

Two components in PARALLEL (either can work):
  Component A availability: 99%
  Component B availability: 99%
  Combined: 1 - (1-0.99) × (1-0.99) = 99.99%   ← much better!
```

**Lesson:** Redundancy (parallel) improves availability. Every required
dependency in series (database, auth service, cache) multiplies failure risk.

---

## 4. Reliability

Reliability is subtly different from availability:

```
Availability: "Is the system responding?"
Reliability:  "Is the system doing the right thing?"

A system can be:
  Available but unreliable  → returning wrong data
  Unavailable but reliable  → down for maintenance, not corrupting data

You want both. But if forced to choose: reliability > availability.
Corrupt data is worse than downtime.
```

### Reliability Patterns

**Idempotency:** Same operation can be applied multiple times with the same result.

```python
# NOT idempotent:
def charge_card(amount):
    db.insert("charges", amount)   # each call creates a new charge!

# IDEMPOTENT:
def charge_card(idempotency_key, amount):
    if not db.exists("charges", key=idempotency_key):
        db.insert("charges", key=idempotency_key, amount=amount)
```

**Retry with idempotency key:** safe to retry on network failure.

**Circuit breaker:** stop trying a failing service to prevent cascade failures.

---

## 5. Latency vs Throughput

```
Latency:    Time to complete ONE operation
            "My API responds in 50ms"

Throughput: Number of operations per unit time
            "My API handles 10,000 req/s"
```

**They're related but not the same:**

```
High throughput, low latency   → ideal
High throughput, high latency  → batch processing is fine, interactive is not
Low throughput, low latency    → single user, fast response
Low throughput, high latency   → the problem state
```

**Percentiles matter more than averages:**

```
P50 (median):  50% of requests complete within this time
P95:           95% of requests complete within this time
P99:           99% of requests complete within this time
P99.9:         99.9% — "tail latency"

Example distribution:
  Average: 100ms  ← looks fine
  P99:     2000ms ← 1 in 100 users wait 2 seconds
  P99.9:   10000ms← 1 in 1000 users time out

Always track P99, not just average.
```

**Little's Law:**

```
L = λ × W
L = average number of items in system
λ = average arrival rate
W = average time in system

Example: If 1000 req/s arrive and each takes 10ms
L = 1000 × 0.010 = 10 concurrent requests in flight
```

---

## 6. CAP Theorem

In a distributed system, you can have at most **two** of:

```
C — Consistency:          Every read sees the most recent write
A — Availability:         Every request gets a response (not an error)
P — Partition Tolerance:  System works despite network partitions
```

**Network partitions are not optional** — networks fail. So in practice,
you choose **CP** or **AP**:

```
CP systems (sacrifice Availability):
  Returns error when partition occurs rather than stale data
  Examples: HBase, ZooKeeper, etcd, most SQL databases
  Use when: Financial systems, inventory, user auth

AP systems (sacrifice Consistency):
  Returns potentially stale data rather than error
  Examples: Cassandra, DynamoDB (eventual), CouchDB
  Use when: Social feeds, product recommendations, analytics
```

**Visual:**

```
Network partition between DC1 and DC2:

DC1                     DC2
┌────────┐     ✗✗✗    ┌────────┐
│ Node A │─────────────│ Node B │
└────────┘   partition └────────┘

CP choice: Node A rejects writes/reads until partition heals
           → availability sacrificed, consistency preserved

AP choice: Node A and B both serve requests independently
           → they diverge, consistency sacrificed, availability preserved
```

---

## 7. PACELC — CAP's Practical Extension

CAP describes what happens during partitions. PACELC adds: **even when the
system is running normally**, there's a trade-off between latency and consistency.

```
PAC: If there is a Partition (P),
     choose between Availability (A) and Consistency (C)

ELC: Else (normally, no partition),
     choose between Latency (L) and Consistency (C)
```

```
System          During Partition  Normally
────────────────────────────────────────────
DynamoDB        AP               EL (latency optimized, eventual consistency)
Cassandra       AP               EL (tunable)
MySQL           CP               EC (strong consistency, higher latency)
PostgreSQL      CP               EC
ZooKeeper       CP               EC
```

---

## 8. Consistency Models

From strongest to weakest:

```
Strict Linearizability  ← reads always see most recent write
      │                   even across different processes
      │                   → very expensive, requires coordination
      ▼
Sequential Consistency  ← all processes see operations in same order
      │                   not necessarily "real time"
      ▼
Causal Consistency      ← causally related ops seen in correct order
      │                   unrelated ops may differ
      ▼
Eventual Consistency    ← eventually all nodes converge on same value
      │                   reads may see stale data temporarily
      ▼
Read Your Own Writes    ← you always see your own writes
      │                   others may not yet
      ▼
Monotonic Read          ← you won't read older data after reading newer
```

**Practical guidance:**

```
Financial transactions:   → Linearizability (no lost money!)
User profile updates:     → Read-your-own-writes
Social media feeds:       → Eventual consistency (ok to see posts slightly late)
Analytics dashboards:     → Eventual consistency (approximate is fine)
Distributed locks:        → Linearizability (must be accurate)
Shopping cart:            → Eventual with conflict resolution (merge carts)
```

---

## 9. Fault Tolerance Patterns

### Redundancy

```
Active-Active:  Multiple instances all serving traffic simultaneously
                → higher utilization, no hot standby waste
                → complexity: must handle concurrent writes

Active-Passive: Primary instance active, secondary waits
                → simpler, clear state ownership
                → failover time, wasted capacity
```

### Circuit Breaker

```
CLOSED → OPEN → HALF-OPEN

CLOSED (normal):
  Requests flow through.
  Track failure rate.
  If failures > threshold → OPEN

OPEN (failing):
  Immediately reject requests (fail fast).
  Don't hit the failing service.
  After timeout → HALF-OPEN

HALF-OPEN (testing):
  Allow one request through.
  If success → CLOSED
  If failure → OPEN again
```

### Bulkhead

Isolate resources so one failure doesn't cascade:

```
Without bulkhead:
  Service A (slow) → exhausts all 100 threads → Service B also starved

With bulkhead:
  Service A → 30 dedicated threads  (isolated pool)
  Service B → 30 dedicated threads  (isolated pool)
  Others   → 40 remaining threads
  → A's slowness can't starve B
```

### Timeout and Retry

```python
# Retry with exponential backoff:
import time, random

def call_with_retry(fn, max_attempts=3, base_delay=1.0, max_delay=60.0):
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except (ConnectionError, TimeoutError) as e:
            if attempt == max_attempts:
                raise
            delay = min(base_delay * 2 ** (attempt - 1), max_delay)
            jitter = random.uniform(0, delay * 0.1)  # prevent thundering herd
            time.sleep(delay + jitter)
```

---

## 10. Back-of-Envelope Estimation

A core skill in system design interviews. The interviewer wants to see:
1. You can reason about scale
2. You know the relevant numbers
3. You can make simplifying assumptions

### Key numbers

```
Data sizes:
  1 byte    = 1 character
  1 KB      = 1,000 bytes   = a small text file
  1 MB      = 1,000 KB      = a photo thumbnail
  1 GB      = 1,000 MB      = a movie
  1 TB      = 1,000 GB      = 200,000 photos

Time:
  1 ms = 10^-3 s
  1 μs = 10^-6 s
  1 ns = 10^-9 s

Latency cheatsheet:
  RAM read:       ~100 ns
  SSD read:       ~150 μs  (150,000 ns = 1500× slower than RAM)
  Network (DC):   ~500 μs  (round trip in same datacenter)
  Disk seek:      ~10 ms   (100× slower than SSD read)
  Network (US→EU):~150 ms  (transcontinental)
```

### Estimation template

```
Twitter example: "Design Twitter's tweet storage"

1. Scale:
   - 300M monthly active users
   - 150M daily active users
   - ~500M tweets/day
   - ~6,000 tweets/second (peak: 3× = 18,000/s)

2. Storage per tweet:
   - tweet_id:    8 bytes
   - user_id:     8 bytes
   - text:        280 chars × 2 bytes (unicode) = 560 bytes
   - timestamp:   8 bytes
   - metadata:    ~50 bytes
   Total: ~640 bytes ≈ 1 KB (round up for safety)

3. Storage growth:
   - 500M tweets/day × 1 KB = 500 GB/day
   - 500 GB × 365 = ~182 TB/year
   - 5 years: ~1 PB (petabyte) for tweets alone

4. Read/write ratio:
   - ~2 reads per second per writer (assume)
   - Read-heavy → optimize for reads (cache, CDN)

5. Bandwidth:
   - Writes: 500M/day × 1 KB = 5.8 MB/s
   - Reads: estimate 10× writes = 58 MB/s inbound read traffic
```

---

## 11. The Vocabulary

These terms must flow naturally in every system design interview:

```
Horizontal scaling    Add more machines
Vertical scaling      Add more power to one machine
Load balancer         Distributes traffic across servers
Reverse proxy         Server-side proxy (Nginx, HAProxy)
CDN                   Content Delivery Network — serve static assets close to users
Cache hit/miss        Hit: served from cache. Miss: must fetch from source
Cache eviction        Removing items when cache is full (LRU, LFU, TTL)
Sharding              Splitting data across multiple DB nodes (horizontal partition)
Replication           Copying data across multiple nodes for redundancy/reads
Leader election       Choosing which node is "primary" (Raft, Paxos)
Consensus             Distributed agreement protocol
Idempotent            Safe to apply multiple times — same result
At-least-once         Message delivered ≥1 times (may duplicate)
At-most-once          Message delivered 0 or 1 times (may lose)
Exactly-once          Message delivered exactly 1 time (hardest, most expensive)
Eventual consistency  All replicas converge eventually, not immediately
Strong consistency    All reads see most recent write
ACID                  Atomicity, Consistency, Isolation, Durability (DB transactions)
BASE                  Basically Available, Soft state, Eventually consistent (NoSQL)
Two-phase commit      Distributed transaction protocol (slow, but atomic)
Saga                  Distributed transaction using compensating transactions
Event sourcing        Store events, not current state
CQRS                  Command Query Responsibility Segregation — separate read/write models
Circuit breaker       Fail fast when downstream is unhealthy
Bulkhead              Isolate resources to prevent cascade failure
Backpressure          Signal to upstream to slow down when overwhelmed
Rate limiting         Restrict requests per client per time window
Thundering herd       Many clients hitting a cold cache simultaneously
Fan-out               One write triggers many reads/writes (Twitter home timeline)
Hotspot               One shard or partition gets disproportionate traffic
Write amplification   One logical write causes many physical writes
Read amplification    One logical read requires many physical reads
```

---

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ➡️ Next | [03 — API Design](../03_api_design/theory.md) |
| 🏠 Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Fundamentals](./fundamentals.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Fundamentals](./fundamentals.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
