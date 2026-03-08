# ⚡ Fundamentals — Cheatsheet

---

## Core Properties

```
Scalability:      Handle increased load without redesign
Availability:     % time system is operational
Reliability:      Doing the right thing (correct, not just up)
Performance:      Fast enough for users
Maintainability:  Engineers can change it safely
```

---

## Availability Numbers

```
99%      → 3.65 days/year downtime
99.9%    → 8.76 hours/year
99.99%   → 52.6 minutes/year
99.999%  → 5.26 minutes/year

Series:   A × B = 0.99 × 0.99 = 98.01%  (worse!)
Parallel: 1 - (1-A)(1-B) = 99.99%       (better!)
```

---

## CAP Theorem

```
Consistency:      Every read sees most recent write
Availability:     Every request gets a response
Partition Tol:    Works despite network partition

P is not optional → choose CP or AP:

CP: HBase, ZooKeeper, etcd, PostgreSQL
    → Returns error during partition (not stale data)
    → Use for: financial, locks, auth

AP: Cassandra, DynamoDB, CouchDB
    → Returns potentially stale data
    → Use for: social feeds, recommendations, analytics
```

---

## Consistency Spectrum

```
Strongest → Weakest:
  Linearizability  → always see most recent write
  Sequential       → same order seen by all
  Causal           → causally related in order
  Eventual         → converges eventually
  Read-your-writes → you see your own writes
```

---

## Latency Reference

```
RAM access:        100 ns
SSD read:          150 μs    (1,500× slower than RAM)
Network (same DC): 500 μs
HDD seek:          10 ms     (100× slower than SSD)
Network (US→EU):   150 ms
```

---

## Key Formulas

```
Little's Law:  L = λ × W
  L = avg items in system
  λ = arrival rate
  W = avg time in system

Throughput degradation:
  At 50% CPU:  predictable
  At 80% CPU:  latency starts climbing
  At 95% CPU:  system becomes unstable
```

---

## Fault Tolerance Patterns

```
Circuit Breaker:  CLOSED→OPEN on failure, HALF-OPEN to test recovery
Bulkhead:         Isolate resource pools so one failure can't starve others
Retry + backoff:  Exponential backoff + jitter to prevent thundering herd
Timeout:          Always set timeouts — hanging requests consume resources
Idempotency:      Safe to retry — server deduplicates using idempotency key
```

---

## SLI / SLO / SLA

```
SLI: actual measurement ("P99 = 45ms right now")
SLO: internal target  ("P99 must stay < 100ms")
SLA: external contract ("99.9% uptime or credit")

Error budget = 1 - SLO
At 99.9%: 43 min/month budget to spend on deployments/incidents
```

---

## Scale Ladder (Rough Guide)

```
1–1K users:    Single server, SQL DB, no cache
1K–10K:        Add read replica, CDN for static assets
10K–100K:      Add Redis cache, multiple app servers + LB
100K–1M:       DB sharding or NoSQL, message queues
1M–10M:        Microservices, multi-region, specialized DBs
10M+:          Global distribution, custom everything
```
