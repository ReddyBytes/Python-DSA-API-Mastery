# System Fundamentals — The Language Every Engineer Must Speak

> Before you can design a system that serves a million users, you need to
> understand the vocabulary. Not definitions to memorize — concepts to *feel*.
> This file builds that intuition, one story at a time.

---

## Contents

```
1.  The Vocabulary of Scale        — latency, throughput, bandwidth
2.  Availability — The Nine Nines  — what uptime actually costs you
3.  SLO, SLA, SLI                  — contracts and measurements
4.  The CAP Theorem                — a story about banks and broken phones
5.  Reliability vs Availability    — they are NOT the same thing
6.  Scalability                    — vertical vs horizontal
7.  Consistency Models             — how fresh is "fresh enough"?
8.  Putting It All Together
```

---

## 1. The Vocabulary of Scale

Imagine you are driving on a highway at midnight. The road is empty. You do
100 mph without hitting traffic. That is **low latency** — the time it takes
for one thing (your car, one request) to get from A to B is very short.

Now imagine rush hour. The road is choked bumper-to-bumper. Each car is moving
at 5 mph — terrible latency. But look from a helicopter: *hundreds of cars per
minute* are still crossing the city. That is **high throughput**.

```
LATENCY vs THROUGHPUT

   Empty highway at midnight           Rush hour highway
   ──────────────────────────          ──────────────────────────
   🚗                                  🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗
   ────────────────────────────────    ────────────────────────────────
                                       🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗🚗

   One car: fast                       One car: slow
   Cars/min crossing city: low         Cars/min crossing city: HIGH

   Low Latency, Low Throughput         High Latency, High Throughput
```

They pull against each other. Optimising for one often hurts the other.

**Bandwidth** is the number of lanes on that highway. More lanes = more cars
can travel simultaneously. You can have a 10-lane highway (huge bandwidth) and
still have high latency if there is an accident at the end (a slow database
query, a congested switch).

```
BANDWIDTH = capacity of the pipe (lanes)
THROUGHPUT = actual data flowing through right now (cars actually moving)
LATENCY = time for one unit to travel end-to-end (one car's trip time)
```

### Real Numbers Worth Remembering

These are approximate but stable across years. Commit them to memory.

```
Operation                         Typical Latency
─────────────────────────────────────────────────
L1 cache reference                ~0.5 ns
L2 cache reference                ~7 ns
RAM access                        ~100 ns
SSD random read                   ~100 µs   (100,000 ns)
HDD random read                   ~10 ms    (10,000,000 ns)
Network: same datacenter          ~0.5 ms
Network: cross-continent          ~150 ms
Network: cross-ocean              ~300 ms
─────────────────────────────────────────────────
```

Rule of thumb: RAM is ~1000x faster than SSD. SSD is ~100x faster than HDD.
The network to a user on another continent adds ~150ms you cannot avoid.

### Throughput Examples

```
A single PostgreSQL node:      ~5,000–10,000 queries/second  (simple reads)
Redis (single thread):         ~100,000+ ops/second
A 1 Gbps network link:         ~125 MB/s  (1 billion bits / 8)
A Kafka topic (single broker): ~hundreds of MB/s
```

---

## 2. Availability — The Nine Nines

"We have 99.9% uptime" sounds great. What does it mean in practice?

```
Availability    Downtime per year    Downtime per month   Downtime per day
────────────────────────────────────────────────────────────────────────────
90%             36.5 days            73 hours             2.4 hours
99%             3.65 days            7.3 hours            14.4 minutes
99.9%           8.76 hours           43.8 minutes         1.44 minutes
99.99%          52.6 minutes         4.4 minutes          8.6 seconds
99.999%         5.26 minutes         26.3 seconds         0.86 seconds
────────────────────────────────────────────────────────────────────────────
```

The jump from 99.9% to 99.99% cuts downtime from ~9 hours per year to ~53
minutes per year. That is not just a number — it is the difference between
one bad night for your ops team versus something that requires redundant
datacenters, automated failover, and a sizeable infrastructure budget.

**Availability is calculated as:**

```
           Uptime
Avail = ──────────────  × 100
         Uptime + Downtime
```

Or equivalently, using the Mean Time metrics (covered in section 4):

```
           MTBF
Avail = ──────────────
         MTBF + MTTR
```

For **composed systems** (System A depends on System B), availability
*multiplies*:

```
System A = 99.9%
System B = 99.9%
A + B in series → 99.9% × 99.9% = 99.8%  (worse than either alone)

This is why redundancy matters. Two dependencies in a chain
make the whole chain weaker.
```

---

## 3. SLI, SLO, and SLA — Who Promises What

These three terms are easy to mix up. Here is the cleanest way to think
about them:

```
SLI  (Service Level Indicator)
     ─── The raw measurement ───
     "Our p99 latency right now is 240ms"
     "Our error rate this week is 0.03%"
     It is just a metric. A reading on a gauge.

SLO  (Service Level Objective)
     ─── Your internal target ───
     "We want p99 latency below 300ms, 99.9% of the time"
     "We want error rate below 0.1%"
     This is the goal your team is aiming for.
     Breaking your SLO is an internal problem.

SLA  (Service Level Agreement)
     ─── The contract with customers ───
     "If uptime drops below 99.9% in any calendar month,
      customers get a 10% service credit."
     This is a legal/business commitment.
     Breaking your SLA costs money — or trust.
```

The relationship:

```
   [SLI — raw measurement]
          ↓
   [SLO — internal target, stricter]
          ↓
   [SLA — external promise, looser buffer]

   SLA is typically looser than SLO deliberately,
   so you have a buffer between "we're struggling"
   and "we owe customers money".
```

Common SLIs:
- Request latency (p50, p99, p999)
- Error rate (5xx responses / total requests)
- Availability (fraction of time the service responds)
- Saturation (CPU %, queue depth)

---

## 4. The CAP Theorem — A Story About Banks

It is 1995. You have two bank branches in two cities: Chicago and Denver.
They share a ledger over a phone line. A customer walks into the Chicago
branch and deposits $500.

Then the phone line breaks.

A few minutes later, a different customer walks into the Denver branch and
asks: "How much is in account #1042?"

The Denver teller has a choice:

```
OPTION A — Refuse to answer
  "I can't tell you, the phone line is down.
   I don't know if Chicago received a deposit."

  → You chose CONSISTENCY over AVAILABILITY.
    The system won't give a potentially wrong answer.
    But it IS unavailable while the partition exists.

OPTION B — Answer with stale data
  "The balance is $1,200" (the pre-deposit number)

  → You chose AVAILABILITY over CONSISTENCY.
    The system keeps serving requests, even when
    it might return outdated information.
```

This is the **CAP Theorem**, stated formally:

```
In any distributed system, during a network partition (P),
you must choose between:

  C — Consistency    Every read gets the most recent write
                     (or an error, not stale data)

  A — Availability   Every request gets a response
                     (though it might be stale)

You cannot have both C and A when P happens.
```

The "P" (partition tolerance) is not really optional. Networks fail. Packets
get dropped. You will have partitions. The real choice is: when a partition
happens, which property do you sacrifice?

```
CP systems  (Consistent + Partition Tolerant)
  Examples: HBase, Zookeeper, etcd, MongoDB (with strong reads)
  Behaviour: "When in doubt, refuse the request rather than lie"
  Good for: Financial systems, leader election, config stores

AP systems  (Available + Partition Tolerant)
  Examples: Cassandra, DynamoDB, CouchDB, DNS
  Behaviour: "Always answer, catch up later"
  Good for: Shopping carts, social feeds, DNS caches
```

### PACELC — The Fuller Picture

CAP only talks about behaviour *during* a partition. But what about
when everything is working fine? PACELC extends the model:

```
  P  —  if there is a Partition...
  A     ...choose Availability
  C     ...or Consistency

  E  —  Else (when the system is running normally)...
  L     ...choose low Latency
  C     ...or Consistency
```

Even without a partition, replicating a write to multiple nodes takes time.
Do you wait for all replicas to confirm (consistency, higher latency) or
do you reply to the client before all replicas are updated (lower latency,
briefly inconsistent)?

```
System         Partition choice    Normal-operation choice
──────────────────────────────────────────────────────────
DynamoDB       PA                  EL  (default; tunable)
Cassandra      PA                  EL  (tunable)
MongoDB        PC                  EC
HBase          PC                  EC
MySQL (InnoDB) PC                  EC
──────────────────────────────────────────────────────────
```

---

## 5. Reliability vs Availability — They Are Not the Same

A car that breaks down once a year, but takes a whole month to repair, is:

```
  Available: 11 out of 12 months = 91.6%
  Reliable?  Not very — it breaks down, it just doesn't break often.
```

A more precise framing:

```
AVAILABILITY — How often is the system UP (percentage of time)

RELIABILITY  — How rarely does the system FAIL
               (failures per unit time, or mean time between failures)
```

The two key metrics:

```
MTBF — Mean Time Between Failures
       Average time the system runs before something breaks.
       You want this HIGH.

       MTBF = Total operating time / Number of failures

MTTR — Mean Time To Recovery (or Repair)
       Average time to restore service after something breaks.
       You want this LOW.

       MTTR = Total downtime / Number of incidents
```

```
Putting it together:

       MTBF
Availability = ──────────
               MTBF + MTTR

If MTBF = 1000 hours, MTTR = 1 hour:
  → 1000 / 1001 = 99.9%

If you double MTBF (system breaks half as often):
  → 2000 / 2001 = 99.95%

If instead you halve MTTR (fix things twice as fast):
  → 1000 / 1001 = 99.9%  (same result — different levers)
```

The practical takeaway:

- To improve availability, you can either make the system *fail less often*
  (harder engineering) or *recover faster* (automation, chaos engineering,
  runbooks, on-call culture).
- High MTBF requires robust architecture, redundancy, and testing.
- Low MTTR requires great observability, automated rollbacks, and practiced
  incident response.

**A highly reliable system that takes 24 hours to recover is less available
than a less reliable system that auto-recovers in 30 seconds.**

---

## 6. Scalability — Vertical vs Horizontal

You run a small web service. Traffic grows. Your server starts sweating.
You have two choices:

### Vertical Scaling (Scale Up)

Buy a bigger machine. More CPUs, more RAM, a faster SSD.

```
Before:                    After:
┌─────────────┐            ┌─────────────────────┐
│  Server     │    →       │  Bigger Server      │
│  4 CPU      │            │  32 CPU             │
│  8 GB RAM   │            │  128 GB RAM         │
│  1 TB SSD   │            │  10 TB NVMe         │
└─────────────┘            └─────────────────────┘
```

Pros: Simple. No code changes needed. No distributed systems headaches.
Cons: Hard ceiling. The biggest machine you can buy has limits. Expensive at
the top end. Single point of failure — if it dies, everything dies.

### Horizontal Scaling (Scale Out)

Add more machines. Put a load balancer in front of them.

```
Before:                      After:

              ┌──────────┐             ┌───────────────┐
Users ──────► │  Server  │   Users ──► │ Load Balancer │
              └──────────┘             └──────┬────────┘
                                              │
                              ┌───────────────┼───────────────┐
                              ▼               ▼               ▼
                         ┌─────────┐    ┌─────────┐    ┌─────────┐
                         │Server A │    │Server B │    │Server C │
                         └─────────┘    └─────────┘    └─────────┘
```

Pros: No hard ceiling — add machines as needed. Redundancy built-in.
Cons: Your application must be designed to be stateless (or state must live
in a shared layer like Redis/a database). More infrastructure complexity.
Distributed bugs become real.

### Which Do You Choose?

```
Start vertical. Switch to horizontal when you hit limits.

Most real systems do BOTH:
  - Each individual node is sized vertically for its role.
  - Many nodes are added horizontally as traffic grows.

A database with 32 CPUs and 512 GB RAM (vertical) replicated
across 3 nodes (horizontal) is a typical production setup.
```

---

## 7. Consistency Models — How Fresh Is "Fresh Enough"?

When data lives on multiple nodes, a write to one node takes time to
propagate to the others. The question every distributed system must answer:
"What does a reader see in the gap between a write and its propagation?"

### Strong Consistency

Every read reflects the most recent write. No exceptions. If you write to
node A, and immediately read from node B, you get the new value.

```
Write: account balance = $500
  ↓  (propagates instantly to all nodes)
Read from any node → $500

Cost: latency. The write cannot "complete" until all nodes confirm.
```

Examples: Single-node MySQL within a transaction, Zookeeper, etcd.
Use when: Financial data, inventory counts, anything where stale = wrong.

### Eventual Consistency

If you stop writing, eventually all nodes will converge to the same value.
In the meantime, different nodes might return different values.

```
Write: post a tweet
  ↓  (propagating to replicas...)
Read from replica A → new tweet visible  ✓
Read from replica B → tweet not yet visible  (still propagating)
...3 seconds later...
Read from replica B → new tweet visible  ✓
```

Examples: DNS, Cassandra (default), DynamoDB (default), S3.
Use when: Social feeds, caches, analytics, anywhere "a few seconds stale"
is acceptable.

### Read-Your-Own-Writes

A middle ground. You might not see what *others* wrote immediately, but
you will always see what *you* wrote.

```
User: posts a comment
User: immediately refreshes the page
  → They see their own comment (even if others on other nodes don't yet)
```

This matters enormously for UX. If you post something and then refresh
and it vanishes, the product feels broken — even if it would reappear
seconds later.

Examples: AWS DynamoDB (with session consistency), most well-designed apps.

### Monotonic Reads

Once you've seen a value, you won't see an older value.

```
Read from replica A at time 1 → balance is $500
Read from replica B at time 2 → balance is $400   ← VIOLATION
                                                      (appears to go backward)
```

Most users expect this implicitly. Seeing the world "go backward" is
deeply confusing.

### Quick Reference

```
Model                   What you get             Cost
─────────────────────────────────────────────────────────────
Strong consistency      Always the latest value  High latency, complex
Eventual consistency    Gets there eventually    Low latency, simple
Read-your-writes        You see your own writes  Moderate complexity
Monotonic reads         Time goes forward        Moderate complexity
─────────────────────────────────────────────────────────────
```

---

## 8. Putting It All Together

These concepts are not independent. They form a web of tradeoffs that you
will reason about in every real design decision:

```
Higher consistency   →  Higher latency   →  Lower availability
Lower latency        →  Eventual consistency (usually)
More replicas        →  Higher throughput (reads) + eventual consistency gap
More shards          →  Higher throughput (writes) + partition management cost
Vertical scaling     →  Simpler code + hard ceiling
Horizontal scaling   →  Higher throughput + distributed complexity
```

A practical example: You are designing a shopping cart.

```
Q: Does the cart need strong consistency?
A: Not necessarily. If two devices show slightly different cart states
   for a second or two, that is fine. Use eventual consistency.

Q: But what about checkout?
A: YES — inventory decrement must be consistent. You cannot oversell.
   Use strong consistency (a database transaction) at checkout time.

Q: What about availability?
A: The cart must always be readable. AP model is correct here.
   The checkout endpoint can tolerate brief unavailability — it is
   better to show an error than to sell inventory you do not have.
```

Most systems end up using different consistency models for different parts
of their data. That is not a cop-out — it is good engineering.

---

## What Comes Next

You now have the vocabulary. The next section uses it immediately:
**APIs** are how services talk to each other, and every API design decision
involves latency, consistency, and availability tradeoffs.

---

## Navigation

| Direction | Link |
|-----------|------|
| Previous | [01 — Networking Basics](../01_networking_basics/theory.md) |
| Next | [03 — API Design](../03_api_design/theory.md) |
| Home | [README.md](../README.md) |
