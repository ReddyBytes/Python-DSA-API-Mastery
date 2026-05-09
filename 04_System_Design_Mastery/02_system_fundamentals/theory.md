<a id="top"></a>

# System Design Fundamentals

> Kumar is a Telugu distributed systems engineer who once watched a banking app
> return stale balances during a network blip. That day, he learned that "it
> works on my machine" means nothing when your system spans three datacenters.
> This file is everything he wishes someone had told him on day one.

## Contents

- [1. What Makes a System Good](#1-what-makes-a-system-good)
- [2. The Vocabulary of Scale](#2-the-vocabulary-of-scale)
  - [Real Numbers Worth Remembering](#real-numbers-worth-remembering)
  - [Throughput Examples](#throughput-examples)
- [3. Scalability](#3-scalability)
  - [Vertical Scaling (Scale Up)](#vertical-scaling-scale-up)
  - [Horizontal Scaling (Scale Out)](#horizontal-scaling-scale-out)
  - [Stateless vs Stateful](#stateless-vs-stateful)
  - [Which Do You Choose](#which-do-you-choose)
- [4. Availability — The Nine Nines](#4-availability--the-nine-nines)
  - [SLA vs SLO vs SLI](#sla-vs-slo-vs-sli)
  - [Availability in Series vs Parallel](#availability-in-series-vs-parallel)
- [5. Reliability](#5-reliability)
  - [MTBF and MTTR](#mtbf-and-mttr)
  - [Reliability Patterns](#reliability-patterns)
- [6. Latency vs Throughput](#6-latency-vs-throughput)
  - [Percentiles Matter More Than Averages](#percentiles-matter-more-than-averages)
  - [Little's Law](#littles-law)
- [7. CAP Theorem — The Fundamental Trade-off](#7-cap-theorem--the-fundamental-trade-off)
  - [CP vs AP Systems](#cp-vs-ap-systems)
  - [The Interview Answer](#the-interview-answer)
- [8. PACELC — CAP's Practical Extension](#8-pacelc--caps-practical-extension)
- [9. Consistency Models](#9-consistency-models)
  - [Strong Consistency](#strong-consistency)
  - [Eventual Consistency](#eventual-consistency)
  - [Read Your Own Writes](#read-your-own-writes)
  - [Monotonic Reads](#monotonic-reads)
  - [Practical Guidance](#practical-guidance)
- [10. Fault Tolerance Patterns](#10-fault-tolerance-patterns)
  - [Redundancy](#redundancy)
  - [Circuit Breaker](#circuit-breaker)
  - [Bulkhead](#bulkhead)
  - [Timeout and Retry](#timeout-and-retry)
  - [RTO and RPO](#rto-and-rpo)
- [11. Back-of-Envelope Estimation](#11-back-of-envelope-estimation)
  - [Key Numbers](#key-numbers)
  - [Estimation Template](#estimation-template)
- [12. The Vocabulary Every Interviewer Expects](#12-the-vocabulary-every-interviewer-expects)
- [Summary](#summary)

<a id="1-what-makes-a-system-good"></a>

# 1. What Makes a System Good

Kumar remembers his first production outage. The service was fast, the code was
clean, but one database failover brought everything down. He learned that a
"good" system is not about any single property — it is about being fit for
purpose across five dimensions simultaneously.

There is no single definition. A good system is **fit for its purpose**.
But across all systems, five properties matter most:

```
+-----------------------------------------------------------------+
|  SCALABILITY      Can it grow without being redesigned?          |
|  AVAILABILITY     Is it accessible when users need it?           |
|  RELIABILITY      Does it do what it promises?                   |
|  PERFORMANCE      Is it fast enough for its users?               |
|  MAINTAINABILITY  Can engineers change it safely over time?      |
+-----------------------------------------------------------------+
```

These properties conflict. Optimizing for one often sacrifices another.
A senior engineer does not find the perfect design — they make the right
**trade-offs** for the specific context.

```
         Scalability
            /\
           /  \
          /    \
         /      \
        / SYSTEM \
       /  FITNESS \
      /____________\
Availability      Performance
      \            /
       \          /
        \________/
      Reliability
      Maintainability
```

"When I design systems now," Kumar says, "I ask five questions before writing
any code. How many users? How bad is downtime? How bad is wrong data? How fast
must it respond? How often will requirements change?"

[Back to Top](#top)

<a id="2-the-vocabulary-of-scale"></a>

# 2. The Vocabulary of Scale

Kumar explains it like this: "Imagine you are driving on a highway at midnight.
The road is empty. You do 100 mph without hitting traffic. That is **low
latency** — the time it takes for one thing (your car, one request) to get
from A to B is very short."

"Now imagine rush hour. The road is choked bumper-to-bumper. Each car is moving
at 5 mph — terrible latency. But look from a helicopter: hundreds of cars per
minute are still crossing the city. That is **high throughput**."

```
LATENCY vs THROUGHPUT

   Empty highway at midnight           Rush hour highway
   -------------------------          -------------------------
   [car]                              [car][car][car][car][car]
   =============================      =============================
                                      [car][car][car][car][car]

   One car: fast                       One car: slow
   Cars/min crossing city: low         Cars/min crossing city: HIGH

   Low Latency, Low Throughput         High Latency, High Throughput
```

They pull against each other. Optimizing for one often hurts the other.

**Bandwidth** is the number of lanes on that highway. More lanes means more cars
can travel simultaneously. You can have a 10-lane highway (huge bandwidth) and
still have high latency if there is an accident at the end (a slow database
query, a congested switch).

```
BANDWIDTH = capacity of the pipe (lanes)
THROUGHPUT = actual data flowing through right now (cars actually moving)
LATENCY = time for one unit to travel end-to-end (one car's trip time)
```

<a id="real-numbers-worth-remembering"></a>

## Real Numbers Worth Remembering

These are approximate but stable across years. Kumar memorized them for
interviews and still references them in production capacity planning.

```
Operation                         Typical Latency
--------------------------------------------------
L1 cache reference                ~0.5 ns
L2 cache reference                ~7 ns
RAM access                        ~100 ns
SSD random read                   ~100 us   (100,000 ns)
HDD random read                   ~10 ms    (10,000,000 ns)
Network: same datacenter          ~0.5 ms
Network: cross-continent          ~150 ms
Network: cross-ocean              ~300 ms
--------------------------------------------------
```

Rule of thumb: RAM is ~1000x faster than SSD. SSD is ~100x faster than HDD.
The network to a user on another continent adds ~150ms you cannot avoid.

<a id="throughput-examples"></a>

## Throughput Examples

```
A single PostgreSQL node:      ~5,000-10,000 queries/second  (simple reads)
Redis (single thread):         ~100,000+ ops/second
A 1 Gbps network link:         ~125 MB/s  (1 billion bits / 8)
A Kafka topic (single broker): ~hundreds of MB/s
```

[Back to Top](#top)

<a id="3-scalability"></a>

# 3. Scalability

Scalability is a system's ability to handle **increased load** without
a complete redesign. Kumar likes to say: "Scalability is not about being fast
today — it is about not falling over tomorrow when traffic doubles."

<a id="vertical-scaling-scale-up"></a>

## Vertical Scaling (Scale Up)

Add more resources to one machine. Buy a bigger server with more CPUs,
more RAM, a faster SSD.

```
Before:                    After:
+---------------+          +-----------------------+
|  Server       |    ->    |  Bigger Server        |
|  4 CPU cores  |          |  32 CPU cores         |
|  16 GB RAM    |          |  256 GB RAM           |
|  500 GB SSD   |          |  10 TB NVMe           |
+---------------+          +-----------------------+
```

**Pros:** Simple. No code changes needed. Low latency (no network hop). No
distributed systems headaches.

**Cons:** Hard ceiling (the biggest machine you can buy has limits). Single
point of failure — if it dies, everything dies. Expensive at the high end.
Requires downtime to upgrade.

<a id="horizontal-scaling-scale-out"></a>

## Horizontal Scaling (Scale Out)

Add more machines. Put a load balancer in front of them.

```
Before:                      After:

              +----------+             +---------------+
Users ------> |  Server  |   Users --> | Load Balancer |
              +----------+             +-------+-------+
                                               |
                               +---------------+---------------+
                               v               v               v
                          +---------+    +---------+    +---------+
                          |Server A |    |Server B |    |Server C |
                          +---------+    +---------+    +---------+
```

**Pros:** Theoretically unlimited — add machines as needed. No single point of
failure. Commodity hardware. Redundancy built-in.

**Cons:** Complexity. Need stateless design or sticky sessions. Network
overhead. Distributed systems are hard to reason about. Your application must
be designed so that any server can handle any request.

> Practice: [Q1 - horizontal-vs-vertical-scaling](../system_design_practice_questions_100.md#q1--normal--horizontal-vs-vertical-scaling)

<a id="stateless-vs-stateful"></a>

## Stateless vs Stateful

```
Stateless server:  Each request contains all info needed. Any server can handle it.
                   -> Easy to horizontal scale

Stateful server:   Server remembers previous requests (session state).
                   -> Hard to horizontal scale (must route to same server)
```

**Rule:** Keep servers stateless. Move state to a shared layer (Redis, DB).
Kumar learned this the hard way when a stateful service lost all session data
during a rolling deployment.

<a id="which-do-you-choose"></a>

## Which Do You Choose

```
Start vertical. Switch to horizontal when you hit limits.

Most real systems do BOTH:
  - Each individual node is sized vertically for its role.
  - Many nodes are added horizontally as traffic grows.

A database with 32 CPUs and 512 GB RAM (vertical) replicated
across 3 nodes (horizontal) is a typical production setup.
```

Kumar's rule of thumb: "If your traffic is predictable and fits in one big box,
stay vertical. The moment you need redundancy or your load is spiky, go
horizontal."

[Back to Top](#top)

<a id="4-availability--the-nine-nines"></a>

# 4. Availability — The Nine Nines

Availability is the percentage of time a system responds correctly.

"We have 99.9% uptime" sounds great. But Kumar asks: what does it actually
mean in practice?

```
Availability    Downtime per year    Downtime per month   Downtime per day
---------------------------------------------------------------------------
90%             36.5 days            73 hours             2.4 hours
99%             3.65 days            7.3 hours            14.4 minutes
99.9%           8.76 hours           43.8 minutes         1.44 minutes
99.99%          52.6 minutes         4.4 minutes          8.6 seconds
99.999%         5.26 minutes         26.3 seconds         0.86 seconds
99.9999%        31.5 seconds         2.6 seconds          0.26 seconds
---------------------------------------------------------------------------
```

The jump from 99.9% to 99.99% cuts downtime from ~9 hours per year to ~53
minutes per year. That is not just a number — it is the difference between
one bad night for your ops team versus something that requires redundant
datacenters, automated failover, and a sizeable infrastructure budget.

**Availability is calculated as:**

```
           Uptime
Avail = ---------------  x 100
         Uptime + Downtime
```

Or equivalently, using Mean Time metrics:

```
           MTBF
Avail = ---------------
         MTBF + MTTR
```

> Practice: [Q3 - availability-reliability-durability](../system_design_practice_questions_100.md#q3--interview--availability-reliability-durability)

<a id="sla-vs-slo-vs-sli"></a>

## SLA vs SLO vs SLI

Kumar explains these three terms as a hierarchy from measurement to promise:

```
SLI  (Service Level Indicator)
     --- The raw measurement ---
     "Our p99 latency right now is 240ms"
     "Our error rate this week is 0.03%"
     It is just a metric. A reading on a gauge.

SLO  (Service Level Objective)
     --- Your internal target ---
     "We want p99 latency below 300ms, 99.9% of the time"
     "We want error rate below 0.1%"
     This is the goal your team is aiming for.
     Breaking your SLO is an internal problem.

SLA  (Service Level Agreement)
     --- The contract with customers ---
     "If uptime drops below 99.9% in any calendar month,
      customers get a 10% service credit."
     This is a legal/business commitment.
     Breaking your SLA costs money -- or trust.
```

The relationship:

```
   [SLI -- raw measurement]
          |
          v
   [SLO -- internal target, stricter]
          |
          v
   [SLA -- external promise, looser buffer]

   SLA is typically looser than SLO deliberately,
   so you have a buffer between "we're struggling"
   and "we owe customers money".
```

Common SLIs:
- Request latency (p50, p99, p999)
- Error rate (5xx responses / total requests)
- Availability (fraction of time the service responds)
- Saturation (CPU %, queue depth)

<a id="availability-in-series-vs-parallel"></a>

## Availability in Series vs Parallel

```
Two components in SERIES (both must work):
  Component A availability: 99%
  Component B availability: 99%
  Combined: 99% x 99% = 98.01%   <- worse than either alone!

Two components in PARALLEL (either can work):
  Component A availability: 99%
  Component B availability: 99%
  Combined: 1 - (1-0.99) x (1-0.99) = 99.99%   <- much better!
```

```
SERIES (both required):          PARALLEL (either works):

  [A] ---> [B] ---> output         +--[A]--+
                                    |       |---> output
  Fail either = system fails        +--[B]--+

                                    Both must fail = system fails
```

**Lesson:** Redundancy (parallel) improves availability. Every required
dependency in series (database, auth service, cache) multiplies failure risk.

Kumar's team reduced their series chain from 5 services to 3 by combining
steps, which improved their composed availability from 99.5% to 99.7%.

[Back to Top](#top)

<a id="5-reliability"></a>

# 5. Reliability

Reliability is subtly different from availability. Kumar uses this analogy:
"A car that starts every morning (available) but occasionally takes you to
the wrong address (unreliable) is worse than a car that sometimes won't start
but always takes you to the right place."

```
Availability: "Is the system responding?"
Reliability:  "Is the system doing the right thing?"

A system can be:
  Available but unreliable  -> returning wrong data
  Unavailable but reliable  -> down for maintenance, not corrupting data

You want both. But if forced to choose: reliability > availability.
Corrupt data is worse than downtime.
```

<a id="mtbf-and-mttr"></a>

## MTBF and MTTR

```
MTBF -- Mean Time Between Failures
       Average time the system runs before something breaks.
       You want this HIGH.

       MTBF = Total operating time / Number of failures

MTTR -- Mean Time To Recovery (or Repair)
       Average time to restore service after something breaks.
       You want this LOW.

       MTTR = Total downtime / Number of incidents
```

```
Putting it together:

       MTBF
Availability = ----------
               MTBF + MTTR

If MTBF = 1000 hours, MTTR = 1 hour:
  -> 1000 / 1001 = 99.9%

If you double MTBF (system breaks half as often):
  -> 2000 / 2001 = 99.95%

If instead you halve MTTR (fix things twice as fast):
  -> 1000 / 1000.5 = 99.95%  (similar result -- different levers)
```

The practical takeaway:

- To improve availability, you can either make the system fail less often
  (harder engineering) or recover faster (automation, chaos engineering,
  runbooks, on-call culture).
- High MTBF requires robust architecture, redundancy, and testing.
- Low MTTR requires great observability, automated rollbacks, and practiced
  incident response.

**A highly reliable system that takes 24 hours to recover is less available
than a less reliable system that auto-recovers in 30 seconds.**

<a id="reliability-patterns"></a>

## Reliability Patterns

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
Kumar's payment service uses idempotency keys on every mutation endpoint —
the lesson came from a double-charge incident that cost the company thousands.

[Back to Top](#top)

<a id="6-latency-vs-throughput"></a>

# 6. Latency vs Throughput

```
Latency:    Time to complete ONE operation
            "My API responds in 50ms"

Throughput: Number of operations per unit time
            "My API handles 10,000 req/s"
```

**They are related but not the same:**

```
                       Low Latency          High Latency
                  +--------------------+--------------------+
High Throughput   |  Ideal state       |  Batch processing  |
                  |  (fast + lots)     |  (slow per item,   |
                  |                    |   many items)       |
                  +--------------------+--------------------+
Low Throughput    |  Single user,      |  THE PROBLEM       |
                  |  fast response     |  STATE             |
                  +--------------------+--------------------+
```

<a id="percentiles-matter-more-than-averages"></a>

## Percentiles Matter More Than Averages

Kumar insists: "Never report average latency in a production system. It hides
the pain of your worst-served users."

```
P50 (median):  50% of requests complete within this time
P95:           95% of requests complete within this time
P99:           99% of requests complete within this time
P99.9:         99.9% -- "tail latency"

Example distribution:
  Average: 100ms  <- looks fine
  P99:     2000ms <- 1 in 100 users wait 2 seconds
  P99.9:   10000ms<- 1 in 1000 users time out

Always track P99, not just average.
```

<a id="littles-law"></a>

## Little's Law

```
L = lambda x W
L = average number of items in system
lambda = average arrival rate
W = average time in system

Example: If 1000 req/s arrive and each takes 10ms
L = 1000 x 0.010 = 10 concurrent requests in flight
```

Kumar uses Little's Law to size connection pools: "If I know my average query
takes 5ms and I need to handle 2000 queries/second, I need at least 10
concurrent connections to the database."

> Practice: [Q2 - latency-vs-throughput](../system_design_practice_questions_100.md#q2--normal--latency-vs-throughput)

[Back to Top](#top)

<a id="7-cap-theorem--the-fundamental-trade-off"></a>

# 7. CAP Theorem — The Fundamental Trade-off

Kumar tells this story to every new engineer on his team:

"It is 1995. You have two bank branches in two cities: Chicago and Denver.
They share a ledger over a phone line. A customer walks into the Chicago
branch and deposits $500. Then the phone line breaks."

"A few minutes later, a different customer walks into the Denver branch and
asks: How much is in account #1042?"

"The Denver teller has a choice:"

```
OPTION A -- Refuse to answer
  "I can't tell you, the phone line is down.
   I don't know if Chicago received a deposit."

  -> You chose CONSISTENCY over AVAILABILITY.
    The system won't give a potentially wrong answer.
    But it IS unavailable while the partition exists.

OPTION B -- Answer with stale data
  "The balance is $1,200" (the pre-deposit number)

  -> You chose AVAILABILITY over CONSISTENCY.
    The system keeps serving requests, even when
    it might return outdated information.
```

This is the **CAP Theorem**, stated formally:

```
In any distributed system, during a network partition (P),
you must choose between:

  C -- Consistency    Every read gets the most recent write
                     (or an error, not stale data)

  A -- Availability   Every request gets a response
                     (though it might be stale)

You cannot have both C and A when P happens.
```

The "P" (partition tolerance) is not really optional. Networks fail. Packets
get dropped. You will have partitions. The real choice is: when a partition
happens, which property do you sacrifice?

```
                    Consistency
                        /\
                       /  \
                      / ?? \
                     /      \
                    /________\
          Availability    Partition Tolerance

  You MUST have P (partitions are reality).
  So the real choice is C or A during partition.
```

<a id="cp-vs-ap-systems"></a>

## CP vs AP Systems

```
CP systems (Consistent + Partition Tolerant):
  During partition -> refuse requests rather than return stale data
  Examples: HBase, Zookeeper, etcd, MongoDB (with strong reads)
  Behaviour: "When in doubt, refuse the request rather than lie"
  Use when: Financial systems, leader election, config stores,
            inventory counts, anything where wrong = dangerous

AP systems (Available + Partition Tolerant):
  During partition -> serve potentially stale data rather than fail
  Examples: Cassandra, DynamoDB (eventual), CouchDB, DNS
  Behaviour: "Always answer, catch up later"
  Use when: Shopping carts, social feeds, DNS caches,
            product recommendations, analytics

CA (Consistent + Available) -- theoretical only:
  Requires no partitions -> impossible in distributed systems
  Only possible in single-node systems (network always fails eventually)
```

**Visual — Network partition between DC1 and DC2:**

```
DC1                     DC2
+--------+     XXX    +--------+
| Node A |------------| Node B |
+--------+   partition+--------+

CP choice: Node A rejects writes/reads until partition heals
           -> availability sacrificed, consistency preserved

AP choice: Node A and B both serve requests independently
           -> they diverge, consistency sacrificed, availability preserved
```

<a id="the-interview-answer"></a>

## The Interview Answer

Kumar's template for CAP questions in interviews:

"In practice, partition tolerance is not optional — network failures happen.
So the real trade-off is CP vs AP. I would choose CP for financial data and
AP for user-facing features where temporary staleness is acceptable. Most
real systems use different models for different data — strong consistency for
checkout, eventual consistency for the product catalog."

> Practice: [Q4 - cap-theorem](../system_design_practice_questions_100.md#q4--thinking--cap-theorem) | [Q76 - explain-cap-junior](../system_design_practice_questions_100.md#q76--interview--explain-cap-junior)

[Back to Top](#top)

<a id="8-pacelc--caps-practical-extension"></a>

# 8. PACELC — CAP's Practical Extension

CAP describes what happens during partitions. But Kumar points out: "Most of
the time, your system is NOT partitioned. What trade-off are you making then?"

PACELC adds: even when the system is running normally, there is a trade-off
between latency and consistency.

```
PAC: If there is a Partition (P),
     choose between Availability (A) and Consistency (C)

ELC: Else (normally, no partition),
     choose between Latency (L) and Consistency (C)
```

Even without a partition, replicating a write to multiple nodes takes time.
Do you wait for all replicas to confirm (consistency, higher latency) or
do you reply to the client before all replicas are updated (lower latency,
briefly inconsistent)?

```
System         Partition choice    Normal-operation choice
---------------------------------------------------------
DynamoDB       PA                  EL  (latency optimized, eventual consistency)
Cassandra      PA                  EL  (tunable)
MongoDB        PC                  EC
HBase          PC                  EC
MySQL (InnoDB) PC                  EC
PostgreSQL     PC                  EC
ZooKeeper      PC                  EC
---------------------------------------------------------
```

Kumar says: "In interviews, mentioning PACELC shows you understand that CAP
is only half the story. The E/L/C choice is the one you make every day —
partition events are rare, but latency-vs-consistency is constant."

[Back to Top](#top)

<a id="9-consistency-models"></a>

# 9. Consistency Models

When data lives on multiple nodes, a write to one node takes time to
propagate to the others. Kumar frames the central question: "What does a
reader see in the gap between a write and its propagation?"

From strongest to weakest:

```
Strict Linearizability  <- reads always see most recent write
      |                   even across different processes
      |                   -> very expensive, requires coordination
      v
Sequential Consistency  <- all processes see operations in same order
      |                   not necessarily "real time"
      v
Causal Consistency      <- causally related ops seen in correct order
      |                   unrelated ops may differ
      v
Eventual Consistency    <- eventually all nodes converge on same value
      |                   reads may see stale data temporarily
      v
Read Your Own Writes    <- you always see your own writes
      |                   others may not yet
      v
Monotonic Read          <- you won't read older data after reading newer
```

<a id="strong-consistency"></a>

## Strong Consistency

Every read reflects the most recent write. No exceptions. If you write to
node A, and immediately read from node B, you get the new value.

```
Write: account balance = $500
  |  (propagates instantly to all nodes)
  v
Read from any node -> $500

Cost: latency. The write cannot "complete" until all nodes confirm.
```

Examples: Single-node MySQL within a transaction, Zookeeper, etcd.
Use when: Financial data, inventory counts, anything where stale = wrong.

<a id="eventual-consistency"></a>

## Eventual Consistency

If you stop writing, eventually all nodes will converge to the same value.
In the meantime, different nodes might return different values.

```
Write: post a tweet
  |  (propagating to replicas...)
  v
Read from replica A -> new tweet visible  [ok]
Read from replica B -> tweet not yet visible  (still propagating)
...3 seconds later...
Read from replica B -> new tweet visible  [ok]
```

Examples: DNS, Cassandra (default), DynamoDB (default), S3.
Use when: Social feeds, caches, analytics, anywhere "a few seconds stale"
is acceptable.

<a id="read-your-own-writes"></a>

## Read Your Own Writes

A middle ground. You might not see what others wrote immediately, but
you will always see what you wrote.

```
User: posts a comment
User: immediately refreshes the page
  -> They see their own comment (even if others on other nodes don't yet)
```

This matters enormously for UX. If you post something and then refresh
and it vanishes, the product feels broken — even if it would reappear
seconds later.

Examples: AWS DynamoDB (with session consistency), most well-designed apps.

<a id="monotonic-reads"></a>

## Monotonic Reads

Once you have seen a value, you will not see an older value.

```
Read from replica A at time 1 -> balance is $500
Read from replica B at time 2 -> balance is $400   <- VIOLATION
                                                      (appears to go backward)
```

Most users expect this implicitly. Seeing the world "go backward" is
deeply confusing. Kumar says: "If your users ever see a counter decrease
without anyone decrementing it, you have a monotonic read violation."

<a id="practical-guidance"></a>

## Practical Guidance

```
Model                   What you get             Cost
--------------------------------------------------------------
Strong consistency      Always the latest value  High latency, complex
Eventual consistency    Gets there eventually    Low latency, simple
Read-your-writes        You see your own writes  Moderate complexity
Monotonic reads         Time goes forward        Moderate complexity
--------------------------------------------------------------
```

**Mapping to use cases:**

```
Financial transactions:   -> Linearizability (no lost money!)
User profile updates:     -> Read-your-own-writes
Social media feeds:       -> Eventual consistency (ok to see posts slightly late)
Analytics dashboards:     -> Eventual consistency (approximate is fine)
Distributed locks:        -> Linearizability (must be accurate)
Shopping cart:            -> Eventual with conflict resolution (merge carts)
```

> Practice: [Q5 - eventual-vs-strong-consistency](../system_design_practice_questions_100.md#q5--thinking--eventual-vs-strong-consistency) | [Q77 - explain-eventual-consistency](../system_design_practice_questions_100.md#q77--interview--explain-eventual-consistency)

[Back to Top](#top)

<a id="10-fault-tolerance-patterns"></a>

# 10. Fault Tolerance Patterns

Kumar's team has a saying: "Hope is not a strategy." Every system will fail.
The question is whether you designed for it or whether you are scrambling at
2 AM with no playbook.

<a id="redundancy"></a>

## Redundancy

```
Active-Active:  Multiple instances all serving traffic simultaneously
                -> higher utilization, no hot standby waste
                -> complexity: must handle concurrent writes

Active-Passive: Primary instance active, secondary waits
                -> simpler, clear state ownership
                -> failover time, wasted capacity

Visual:

Active-Active:                  Active-Passive:
+---------+   +---------+      +---------+   +---------+
| Node A  |   | Node B  |      | Primary |   | Standby |
| (active)|   | (active)|      | (active)|   | (idle)  |
+---------+   +---------+      +---------+   +---------+
     |             |                 |              |
     +------+------+                 |   (failover) |
            |                        +------->------+
         [users]                       (on failure)
```

<a id="circuit-breaker"></a>

## Circuit Breaker

Kumar explains: "Think of it like an electrical circuit breaker in your house.
When too much current flows (too many failures), the breaker trips to protect
the whole system from burning down."

```
State Machine:  CLOSED -> OPEN -> HALF-OPEN

CLOSED (normal):
  Requests flow through.
  Track failure rate.
  If failures > threshold -> OPEN

OPEN (failing):
  Immediately reject requests (fail fast).
  Don't hit the failing service.
  After timeout -> HALF-OPEN

HALF-OPEN (testing):
  Allow one request through.
  If success -> CLOSED
  If failure -> OPEN again
```

```
Flow diagram:

           success              timeout expires
    +------+------+        +--------+--------+
    |             |        |                 |
    v             |        v                 |
+--------+     +------+     +----------+     |
| CLOSED | --> | OPEN | --> | HALF-OPEN| ----+
+--------+     +------+     +----------+
   |              ^                |
   | failures     | failure        | success
   | exceed       |               |
   | threshold    +               v
   +---->------>--+          back to CLOSED
```

<a id="bulkhead"></a>

## Bulkhead

Isolate resources so one failure does not cascade. Named after the watertight
compartments in a ship — if one floods, the others keep the ship afloat.

```
Without bulkhead:
  Service A (slow) -> exhausts all 100 threads -> Service B also starved

With bulkhead:
  Service A -> 30 dedicated threads  (isolated pool)
  Service B -> 30 dedicated threads  (isolated pool)
  Others   -> 40 remaining threads
  -> A's slowness can't starve B

Visual:

+--------------------------------------------------+
|                   Thread Pool                      |
|  +----------+  +----------+  +------------------+ |
|  | Service A|  | Service B|  | General Pool     | |
|  | 30 threads| | 30 threads| | 40 threads       | |
|  +----------+  +----------+  +------------------+ |
+--------------------------------------------------+
```

<a id="timeout-and-retry"></a>

## Timeout and Retry

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

```
Retry timeline with exponential backoff:

Attempt 1: immediate
  [FAIL] -> wait 1s (+ jitter)
Attempt 2:
  [FAIL] -> wait 2s (+ jitter)
Attempt 3:
  [FAIL] -> wait 4s (+ jitter)
Attempt 4:
  [SUCCESS] -> return result

Without jitter, all clients retry at the same time = thundering herd.
Jitter spreads retries randomly to prevent stampede.
```

<a id="rto-and-rpo"></a>

## RTO and RPO

Two numbers every system designer must know when discussing disaster recovery:

**RTO (Recovery Time Objective)** — the maximum acceptable downtime. How long
can the system be unavailable before it causes unacceptable business impact?

**RPO (Recovery Point Objective)** — the maximum acceptable data loss. How much
data (measured in time) can you afford to lose?

```
Failure occurs at T=0

RPO                        RTO
<-----------------------+   +------------------------------>
Last good backup        T=0  Recovery complete

RPO = time between last backup and failure  (data loss window)
RTO = time from failure to service restored (downtime window)
```

**Examples by system type:**

```
System              RPO          RTO          Strategy
--------------------------------------------------------------
Payment system      ~0 seconds   < 30 seconds  Synchronous replication, hot standby
E-commerce cart     < 5 minutes  < 5 minutes   Async replication, warm standby
Analytics reports   < 24 hours   < 4 hours     Daily backup, cold standby
Dev/test env        < 1 week     < 24 hours    Weekly snapshot
```

**Recovery strategies ranked by cost and speed:**

```
Strategy        Failover Time    Cost       Description
--------------------------------------------------------------
Hot standby     seconds          highest    Live replica always running
Warm standby    minutes          moderate   Replica updated periodically
Cold standby    hours            low        Backup restored on new hardware
Backup/restore  hours to days    lowest     Restore from S3/tape
```

The right choice depends on: cost of downtime per minute multiplied by expected
downtime versus infrastructure cost.

[Back to Top](#top)

<a id="11-back-of-envelope-estimation"></a>

# 11. Back-of-Envelope Estimation

A core skill in system design interviews. Kumar says: "The interviewer does
not care if your numbers are exact. They want to see that you can reason about
scale, know the relevant orders of magnitude, and make simplifying assumptions."

<a id="key-numbers"></a>

## Key Numbers

```
Data sizes:
  1 byte    = 1 character
  1 KB      = 1,000 bytes   = a small text file
  1 MB      = 1,000 KB      = a photo thumbnail
  1 GB      = 1,000 MB      = a movie
  1 TB      = 1,000 GB      = 200,000 photos
  1 PB      = 1,000 TB      = all of Twitter's tweets for 5 years

Time:
  1 ms = 10^-3 s
  1 us = 10^-6 s
  1 ns = 10^-9 s

Latency cheatsheet:
  RAM read:       ~100 ns
  SSD read:       ~150 us  (150,000 ns = 1500x slower than RAM)
  Network (DC):   ~500 us  (round trip in same datacenter)
  Disk seek:      ~10 ms   (100x slower than SSD read)
  Network (US->EU):~150 ms  (transcontinental)
```

<a id="estimation-template"></a>

## Estimation Template

Kumar walks through his standard estimation framework:

```
Twitter example: "Design Twitter's tweet storage"

1. Scale:
   - 300M monthly active users
   - 150M daily active users
   - ~500M tweets/day
   - ~6,000 tweets/second (peak: 3x = 18,000/s)

2. Storage per tweet:
   - tweet_id:    8 bytes
   - user_id:     8 bytes
   - text:        280 chars x 2 bytes (unicode) = 560 bytes
   - timestamp:   8 bytes
   - metadata:    ~50 bytes
   Total: ~640 bytes, round up to 1 KB

3. Storage growth:
   - 500M tweets/day x 1 KB = 500 GB/day
   - 500 GB x 365 = ~182 TB/year
   - 5 years: ~1 PB (petabyte) for tweets alone

4. Read/write ratio:
   - ~2 reads per second per writer (assume)
   - Read-heavy -> optimize for reads (cache, CDN)

5. Bandwidth:
   - Writes: 500M/day x 1 KB = 5.8 MB/s
   - Reads: estimate 10x writes = 58 MB/s inbound read traffic
```

Kumar's tips for estimation in interviews:
- Round aggressively. 500M is easier to work with than 487M.
- State your assumptions explicitly. "I am assuming 1 KB per tweet."
- Work in powers of 10. Move between scales by adding/removing zeros.
- Always sanity-check: "Does 500 GB/day sound reasonable for Twitter? Yes."

[Back to Top](#top)

<a id="12-the-vocabulary-every-interviewer-expects"></a>

# 12. The Vocabulary Every Interviewer Expects

These terms must flow naturally in every system design interview. Kumar reviews
this list before every interview loop — not to memorize definitions, but to
make sure he can use each term in context during a design discussion.

```
Horizontal scaling    Add more machines
Vertical scaling      Add more power to one machine
Load balancer         Distributes traffic across servers
Reverse proxy         Server-side proxy (Nginx, HAProxy)
CDN                   Content Delivery Network -- serve static assets close to users
Cache hit/miss        Hit: served from cache. Miss: must fetch from source
Cache eviction        Removing items when cache is full (LRU, LFU, TTL)
Sharding              Splitting data across multiple DB nodes (horizontal partition)
Replication           Copying data across multiple nodes for redundancy/reads
Leader election       Choosing which node is "primary" (Raft, Paxos)
Consensus             Distributed agreement protocol
Idempotent            Safe to apply multiple times -- same result
At-least-once         Message delivered >=1 times (may duplicate)
At-most-once          Message delivered 0 or 1 times (may lose)
Exactly-once          Message delivered exactly 1 time (hardest, most expensive)
Eventual consistency  All replicas converge eventually, not immediately
Strong consistency    All reads see most recent write
ACID                  Atomicity, Consistency, Isolation, Durability (DB transactions)
BASE                  Basically Available, Soft state, Eventually consistent (NoSQL)
Two-phase commit      Distributed transaction protocol (slow, but atomic)
Saga                  Distributed transaction using compensating transactions
Event sourcing        Store events, not current state
CQRS                  Command Query Responsibility Segregation -- separate read/write models
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

[Back to Top](#top)

<a id="summary"></a>

# Summary

```
+---------------------------------------------------------------------+
| CONCEPT              | KEY TAKEAWAY                                  |
+----------------------+-----------------------------------------------+
| Scalability          | Vertical first, horizontal when you hit limits|
| Availability         | Nines cost exponentially more infrastructure  |
| Reliability          | Corrupt data is worse than downtime           |
| Latency/Throughput   | Track P99, not averages                       |
| CAP Theorem          | Partition is mandatory; choose CP or AP       |
| PACELC               | Even without partition: latency vs consistency|
| Consistency Models   | Match model to use case, not one-size-fits-all|
| Fault Tolerance      | Circuit breaker + bulkhead + retry with jitter|
| Estimation           | Round aggressively, state assumptions, sanity |
| Vocabulary           | Use terms in context, not as definitions      |
+----------------------+-----------------------------------------------+
```

Kumar's three rules for system design interviews:
1. Always state your assumptions before calculating
2. Always ask "what happens when this fails?" for every component
3. Never choose CP or AP without explaining why for your specific use case

**Learning Priority:**

- **Must Learn:** vertical vs horizontal scaling, CAP theorem (CP vs AP), consistency models, fault tolerance patterns (circuit breaker/bulkhead/retry)
- **Should Learn:** back-of-envelope estimation, SLO/SLI/SLA, availability calculations, PACELC theorem
- **Good to Know:** idempotency strategies, Little's Law, percentile-based thinking
- **Reference:** Byzantine fault tolerance, FMEA, chaos engineering principles

[Back to Top](#top)

## Navigation

| | |
|---|---|
| Previous | [01 - Networking Basics](../01_networking_basics/theory.md) |
| Next | [03 - API Design](../03_api_design/theory.md) |
| Interview | [interview.md](./interview.md) |
| Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| Home | [README.md](../README.md) |

**Prev:** [Networking Basics](../01_networking_basics/theory.md) | **Next:** [API Design](../03_api_design/theory.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) | [Interview Q&A](./interview.md) | [Networking Basics](../01_networking_basics/theory.md) | [API Design](../03_api_design/theory.md)
