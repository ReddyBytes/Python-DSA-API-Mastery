<a id="top"></a>
# Scalability Patterns

> Vijay ran a food-delivery app in Hyderabad. One server, one database, 1,000 orders a day. On Diwali weekend, the city placed 400,000 orders. The server melted. The database hit connection limits. Customers saw blank screens. "Scaling is not one trick," Vijay told his team the next morning. "It is a playbook. You reach for different patterns depending on where the pressure is." This chapter is that playbook -- every pattern Vijay learned on his journey from 1K to 1M users.

<a id="toc"></a>
## Table of Contents

- [1. The Core Problem: From 1K to 1M Users](#1-the-core-problem)
- [2. CQRS: Read and Write are Different Problems](#2-cqrs)
  - [The Write Side](#the-write-side)
  - [The Read Side](#the-read-side)
  - [A Concrete Example](#a-concrete-example)
  - [When to Use CQRS](#when-to-use-cqrs)
  - [When NOT to Use CQRS](#when-not-to-use-cqrs)
- [3. Event Sourcing: Store What Happened Not What Is](#3-event-sourcing)
  - [The Bank Account Analogy](#the-bank-account-analogy)
  - [Replaying State](#replaying-state)
  - [Benefits](#benefits)
  - [The Cost](#the-cost)
- [4. Fan-Out: One Event Many Side Effects](#4-fan-out)
  - [Push Fan-Out (Write-Time)](#push-fan-out-write-time)
  - [Pull Fan-Out (Read-Time)](#pull-fan-out-read-time)
  - [The Celebrity Problem](#the-celebrity-problem)
- [5. The Saga Pattern: Distributed Transactions Without the Pain](#5-saga-pattern)
  - [What is a Saga](#what-is-a-saga)
  - [Two Flavors of Saga](#two-flavors-of-saga)
  - [What Eventual Consistency Means Here](#what-eventual-consistency-means-here)
- [6. Write Amplification vs Read Amplification](#6-write-vs-read-amplification)
- [7. Horizontal Scaling Patterns](#7-horizontal-scaling)
  - [Stateless Services](#stateless-services)
  - [Database Read Replicas](#database-read-replicas)
  - [Connection Pooling](#connection-pooling)
- [8. Putting It Together](#8-putting-it-together)
- [9. Learning Priority](#9-learning-priority)
- [10. Quick Reference](#10-quick-reference)
- [11. Practice Questions](#11-practice-questions)
- [12. Summary](#12-summary)

[Back to Top](#top)

<a id="1-the-core-problem"></a>
# 1. The Core Problem: From 1K to 1M Users

Vijay's food-delivery app started small. One server, one database. Orders came in, got processed, life was simple.

Then came Diwali weekend.

```
Day 1:        [1K orders]  --> [ Vijay's Server ] --> [ His DB ]   OK
                                                                    
Day 30:       [400K orders] --> [ Vijay's Server ] --> [ His DB ]  Server on fire
                                                                    DB melting
                                                                    Vijay paged at 3am
```

What breaks when traffic explodes:

- **CPU/Memory** -- one server can only handle so many concurrent requests before it buckles
- **Database** -- queries that took 5ms now take 5 seconds; indexes help but only so far
- **Disk I/O** -- every write, every read flows through one spindle
- **Network** -- the single server becomes a bottleneck just accepting connections
- **Deployments** -- any change means downtime for everyone

Scaling is not one trick. It is a playbook -- a collection of patterns you reach for depending on where the pressure is.

[Back to Top](#top)

<a id="2-cqrs"></a>
# 2. CQRS: Read and Write are Different Problems

Here is a fact that most beginners miss:

> Most applications read 10 to 100 times more than they write.

A tweet is written once. It is read millions of times. A product listing is updated occasionally. It is browsed constantly. Despite this, traditional CRUD apps treat reads and writes identically -- the same model, the same table, the same code path. That is the problem.

**CQRS** (Command Query Responsibility Segregation) says: split them.

```
TRADITIONAL (one model for everything):
    [User] --write--> [App] ---> [DB]
    [User] --read --> [App] ---> [Same DB]   <-- no distinction

CQRS (separated):
    [User] --Command--> [Write Service] ---> [Write DB (normalized)]
                                |
                                | event: "product_updated"
                                v
                        [Event Bus / Queue]
                                |
                                v
                        [Read Model Updater] --> [Read DB (denormalized, fast)]
                                                        ^
    [User] --Query-----> [Read Service] ----------------+
```

Vijay applied this to his order system. Write path: validate order, check restaurant availability, debit payment. Read path: "show me my order status" -- served from a denormalized Redis cache that updates within milliseconds of the write.

<a id="the-write-side"></a>
## The Write Side

- **Normalized** -- data stored without redundancy, easy to update consistently
- **Validated** -- every command goes through business rules before being accepted
- **Slower reads are okay** -- the write side is not optimized for querying

<a id="the-read-side"></a>
## The Read Side

- **Denormalized** -- data pre-joined and flattened for fast retrieval
- **Eventually consistent** -- it lags behind the write side slightly (milliseconds to seconds)
- **Can be multiple** -- you can have several read models optimized for different query patterns

<a id="a-concrete-example"></a>
## A Concrete Example

```
Write DB (normalized):
    orders:     id, user_id, created_at
    order_items: id, order_id, product_id, quantity
    products:   id, name, price

Read DB (denormalized, for "show order summary"):
    order_summaries: order_id, user_name, items_as_json, total_price, created_at
    <-- pre-computed, one row per order, no joins needed at query time
```

<a id="when-to-use-cqrs"></a>
## When to Use CQRS

- Read/write ratio is highly skewed
- Different teams own reads vs writes
- You need to scale reads independently

<a id="when-not-to-use-cqrs"></a>
## When NOT to Use CQRS

- Simple CRUD apps -- the complexity is not worth it
- Teams with fewer than ~10 engineers -- you will spend more time on plumbing than features

[Back to Top](#top)

<a id="3-event-sourcing"></a>
# 3. Event Sourcing: Store What Happened Not What Is

Most databases store **current state**. You update a row. The old value is gone.

Event Sourcing flips this: **store every event that happened**. Current state is derived by replaying events.

Vijay's payment service needed an audit trail. Regulators wanted to see every balance change. With traditional state-based storage, once you update the balance column, the history disappears. Event sourcing solved this permanently.

<a id="the-bank-account-analogy"></a>
## The Bank Account Analogy

```
TRADITIONAL (state-based):
    accounts table:
    | user_id | balance |
    | 42      | $350    |   <-- just the current balance, history gone

EVENT SOURCED:
    events table:
    | event_id | user_id | type       | amount | timestamp           |
    | 1        | 42      | DEPOSIT    | $500   | 2024-01-01 09:00    |
    | 2        | 42      | WITHDRAWAL | $200   | 2024-01-03 14:30    |
    | 3        | 42      | DEPOSIT    | $50    | 2024-01-05 11:00    |
    <-- replay these: 500 - 200 + 50 = $350
```

Every change is an immutable event. You never update or delete events -- you only append.

<a id="replaying-state"></a>
## Replaying State

```
function getCurrentBalance(userId):
    events = db.query("SELECT * FROM events WHERE user_id = ? ORDER BY event_id", userId)
    balance = 0
    for event in events:
        if event.type == DEPOSIT:    balance += event.amount
        if event.type == WITHDRAWAL: balance -= event.amount
    return balance
```

For performance, you periodically take **snapshots** so you do not replay from the beginning of time.

```
[Event 1] --> [Event 2] --> [Event 3] --> ... --> [Snapshot at Event 100] --> [Event 101] --> [Event 102]
                                                         ^
                            Start replay from here, not from Event 1
```

<a id="benefits"></a>
## Benefits

- **Audit trail built-in** -- every change is recorded; banks love this, compliance loves this
- **Time travel** -- "What was this user's balance on January 3rd at 2pm?" Just replay up to that point
- **Multiple read models** -- replay the same events into different shapes for different query needs
- **Debugging** -- you can replay events locally to reproduce any bug

<a id="the-cost"></a>
## The Cost

- **Complexity** -- it is a fundamentally different paradigm; harder to onboard new engineers
- **Query performance** -- you cannot just `SELECT balance FROM accounts WHERE user_id = 42`; you need read models
- **Schema evolution** -- old events are immutable, so changing event structure is tricky
- **Storage** -- you are storing everything forever

Event Sourcing is powerful. It is also genuinely complex. Do not use it because it sounds cool. Use it when auditability, time travel, or multiple read projections justify the cost.

[Back to Top](#top)

<a id="4-fan-out"></a>
# 4. Fan-Out: One Event Many Side Effects

When a user posts a tweet, what needs to happen?

1. Store the tweet
2. Update 10 million followers' timelines
3. Update search index
4. Trigger notifications for mentions
5. Update analytics

One action. Many side effects. That is **fan-out**.

Vijay faced this with restaurant menu updates. When a popular restaurant changes its menu, every user currently browsing that restaurant needs to see the update. One write, thousands of reads that need refreshing.

```
User posts tweet
        |
        v
[Write tweet to DB]
        |
        v
[Publish "tweet_created" event]
        |
        +---------> [Update timeline service for each follower]
        |
        +---------> [Update search index]
        |
        +---------> [Send mention notifications]
        |
        +---------> [Log to analytics pipeline]
```

<a id="push-fan-out-write-time"></a>
## Push Fan-Out (Write-Time)

When a tweet is posted, **immediately write to every follower's timeline** cache.

```
POST /tweet by @user (100K followers)
    --> Write tweet to tweets table
    --> For each of 100K followers:
          redis.lpush("timeline:{follower_id}", tweet_id)   <-- push to their queue

GET /timeline for @follower
    --> redis.lrange("timeline:{follower_id}", 0, 50)       <-- instant read
```

- **Read is fast** -- pre-computed, just fetch from cache
- **Write is expensive** -- 100K followers = 100K writes per tweet

<a id="pull-fan-out-read-time"></a>
## Pull Fan-Out (Read-Time)

When a user opens their timeline, **compute it on the fly** by fetching recent tweets from everyone they follow.

```
GET /timeline for @follower
    --> following_list = db.query("SELECT followed_id FROM follows WHERE follower_id = ?")
    --> for each followed_id:
          tweets += db.query("SELECT * FROM tweets WHERE user_id = ? ORDER BY created_at DESC LIMIT 10")
    --> merge, sort, return top 50
```

- **Write is cheap** -- just write the tweet once
- **Read is expensive** -- if you follow 1,000 people, that is 1,000 queries per timeline load

<a id="the-celebrity-problem"></a>
## The Celebrity Problem

Push fan-out has a brutal edge case: celebrities.

```
@celebrity (10M followers) posts a tweet

Push fan-out:
    10,000,000 x redis.lpush()  <-- this takes minutes
    Other users' timeline writes get queued behind this

This is called "hotspot" or "thundering herd" on write.
```

**Hybrid solution** (used by Twitter/X historically):

```
Regular users (< 1M followers)  --> push fan-out   (fast for their followers)
Celebrities (> 1M followers)    --> pull fan-out    (compute at read time)

At read time:
    timeline = redis.get("timeline:{user_id}")     <-- pre-pushed from regular follows
    + db.query(tweets from celebrities you follow) <-- pulled and merged in
```

[Back to Top](#top)

<a id="5-saga-pattern"></a>
# 5. The Saga Pattern: Distributed Transactions Without the Pain

Vijay expanded his delivery app. Now a single order involves: payment service, restaurant service, and rider assignment service. All three must succeed, or none should be charged.

In a monolith, you would wrap this in a database transaction:

```sql
BEGIN TRANSACTION
    INSERT INTO payment_charges ...
    INSERT INTO restaurant_orders ...
    INSERT INTO rider_assignments ...
COMMIT  -- or ROLLBACK if anything fails
```

In a microservices world, each step lives in a different service with its own database. **You cannot do a cross-service ACID transaction.**

This is the distributed transaction problem. The Saga pattern solves it.

<a id="what-is-a-saga"></a>
## What is a Saga

A saga is a sequence of local transactions. If any step fails, compensating transactions undo the previous steps.

```
HAPPY PATH:
    [Charge Payment] --> success
         |
         v
    [Confirm Restaurant] --> success
         |
         v
    [Assign Rider]    --> success
         |
         v
    DONE (order confirmed)

FAILURE PATH (restaurant rejects):
    [Charge Payment] --> success
         |
         v
    [Confirm Restaurant] --> FAIL
         |
         v
    [Refund Payment] <-- compensating transaction
         |
         v
    DONE (order cancelled cleanly)
```

<a id="two-flavors-of-saga"></a>
## Two Flavors of Saga

**Choreography -- services talk to each other via events:**

```
[Payment Service]     -- emits "payment_charged"     --> [Restaurant Service]
[Restaurant Service]  -- emits "restaurant_confirmed" --> [Rider Service]
[Rider Service]       -- emits "rider_assigned"       --> [Order Complete]

On failure:
[Restaurant Service]  -- emits "restaurant_rejected"  --> [Payment Service]
[Payment Service]     -- on "restaurant_rejected": refund payment
```

- Simple, no central coordinator
- Hard to debug -- the "flow" of the saga is implicit, spread across services
- Good for simple sagas with 2-3 steps

**Orchestration -- a central saga coordinator drives the flow:**

```
                [Saga Orchestrator]
                        |
              +---------+---------+
              |                   |
    [Payment Service]   [Restaurant Service]   [Rider Service]
              |                   |                |
          "charge"           "confirm"         "assign"
              |                   |                |
    orchestrator tracks state, calls each, handles rollback

On failure:
    orchestrator calls "refund" on Payment Service explicitly
```

- Explicit flow -- the saga logic lives in one place
- Easier to monitor and debug
- The orchestrator becomes a bottleneck and a new point of failure
- Good for complex sagas with many steps or conditional logic

<a id="what-eventual-consistency-means-here"></a>
## What Eventual Consistency Means Here

During a saga, the system is temporarily inconsistent. The payment is charged but the restaurant has not confirmed yet. This window is unavoidable. You design for it:

- Keep sagas as short-lived as possible
- Make compensating transactions idempotent (safe to run multiple times)
- Use status fields: `PENDING --> CONFIRMED --> CANCELLED`

[Back to Top](#top)

<a id="6-write-vs-read-amplification"></a>
# 6. Write Amplification vs Read Amplification

Every architectural decision is a trade-off between read cost and write cost. Vijay learned this the hard way when his CQRS setup with four read models meant every menu price change triggered five writes.

```
WRITE AMPLIFICATION:
    One logical write --> many physical writes

    Example: CQRS with 3 read models
        User updates their name (1 write)
        --> Write DB updated (1 write)
        --> Read Model 1 updated (1 write)
        --> Read Model 2 updated (1 write)
        --> Read Model 3 updated (1 write)
        = 4 writes for 1 logical change

READ AMPLIFICATION:
    One logical read --> many physical reads

    Example: Pull fan-out timeline
        User loads timeline (1 read)
        --> Query 500 followed users' recent tweets (500 reads)
        --> Merge and sort results
        = 500 reads for 1 logical query

STORAGE AMPLIFICATION:
    One piece of data --> stored multiple times

    Example: denormalized read model
        User name stored in users table, order_summaries table,
        review_summaries table, etc.
        Update name once --> inconsistency until all models sync
```

There is no free lunch. When you optimize reads, you usually pay in writes (and vice versa). The right trade-off depends on your read/write ratio, latency requirements, and consistency needs.

[Back to Top](#top)

<a id="7-horizontal-scaling"></a>
# 7. Horizontal Scaling Patterns

Once you understand the data patterns above, here is how to actually add machines. Vijay started with vertical scaling (bigger server), but eventually hit the ceiling. Horizontal scaling -- adding more machines -- is the only path to truly large scale.

<a id="stateless-services"></a>
## Stateless Services

The golden rule of horizontal scaling:

> If any server can handle any request, you can add servers freely.

```
STATEFUL (bad for scaling):
    Server 1 holds user session in memory
    Server 2 does not know about it
    Load balancer sends user to Server 2 --> user logged out <-- bad

    [User] --> [Load Balancer] --> [Server 1] <-- holds session
                              --> [Server 2] <-- does not hold session
                              --> [Server 3] <-- does not hold session

STATELESS (good for scaling):
    Session stored in Redis (external)
    Any server can read it
    Add/remove servers freely

    [User] --> [Load Balancer] --> [Server 1] \
                              --> [Server 2] --> [Redis] (shared session store)
                              --> [Server 3] /
```

Make your application servers stateless. Push state to a database, cache, or message queue.

<a id="database-read-replicas"></a>
## Database Read Replicas

Writes still go to one primary. Reads can be spread across replicas.

```
                    +-------------------+
                    |    Primary DB     |  <-- all writes go here
                    +---------+---------+
                              |  replication (async, usually < 100ms lag)
              +---------------+---------------+
              |               |               |
    +---------+---+   +-------+-----+   +-----+----------+
    |  Replica 1  |   |  Replica 2  |   |   Replica 3    |
    +-------------+   +-------------+   +----------------+
          ^                ^                   ^
     read traffic     read traffic        read traffic
```

- Reads scale horizontally. Add more replicas for more read capacity
- Writes are still single-server. For write scaling, you need sharding (see Chapter 05 Databases)
- Replication lag: replicas may be slightly behind the primary; reads may return stale data

<a id="connection-pooling"></a>
## Connection Pooling

Databases have a limited number of connections. Opening a new connection per request is expensive (TCP handshake, auth, memory allocation on DB side).

```
WITHOUT POOLING:
    [Server] <--> connect <--> [DB]  (per request)
    [Server] <--> connect <--> [DB]  (per request)
    [Server] <--> connect <--> [DB]  (per request)
    100 concurrent requests = 100 DB connections = DB out of memory

WITH POOLING (PgBouncer, HikariCP, etc.):
    [Server] <--> [Connection Pool (20 connections)] <--> [DB]
    100 concurrent requests share 20 persistent connections
    Requests queue for a free connection (milliseconds)
    DB stays healthy
```

Connection pooling is often the first lever to pull when a database starts dropping connections under load. Vijay added PgBouncer between his app servers and PostgreSQL -- connection errors dropped to zero overnight.

[Back to Top](#top)

<a id="8-putting-it-together"></a>
# 8. Putting It Together

These patterns do not exist in isolation. A real high-scale system might combine all of them. Here is what Vijay's delivery platform looked like after a year of scaling work:

```
[Clients]
    |
    v
[API Gateway]
    |
    +---[Command Path]---> [Write Service] ---> [Primary DB]
    |                              |
    |                              v
    |                      [Event Bus]
    |                              |
    |              +---------------+----------------+
    |              |               |                |
    |     [Read Model A]    [Read Model B]    [Analytics]
    |          (Redis)         (Search)
    |
    +---[Query Path]---> [Read Service] ---> [Read Replica]
                                    \------> [Redis Cache]
```

Start simple. Add patterns only when you have concrete evidence that you need them. A startup with 1,000 users does not need event sourcing. Vijay's rule: "If you cannot point to the dashboard metric that proves you need this pattern, you do not need it yet."

[Back to Top](#top)

<a id="9-learning-priority"></a>
# 9. Learning Priority

**Must Learn** -- core concept, daily use, interview essential:
CQRS (Command Query Responsibility Segregation) trade-offs, event sourcing concepts, fan-out on write vs read

**Should Learn** -- important for real projects, comes up regularly:
data denormalization trade-offs, write amplification costs, database federation, saga pattern orchestration vs choreography

**Good to Know** -- useful in specific situations, not always tested:
event versioning, read model construction, temporal queries

**Reference** -- know it exists, look up syntax when needed:
event store internals, cross-shard transactions, operational debugging of event-sourced systems

[Back to Top](#top)

<a id="10-quick-reference"></a>
# 10. Quick Reference

| Pattern           | Solves                              | Trade-off                        |
|-------------------|-------------------------------------|----------------------------------|
| CQRS              | Read/write ratio mismatch           | Eventual consistency, complexity |
| Event Sourcing    | Audit trail, time travel            | Query complexity, storage        |
| Push Fan-out      | Fast reads for timelines            | Write amplification, hotspots    |
| Pull Fan-out      | Simple writes                       | Slow reads at scale              |
| Saga              | Distributed transactions            | Complexity, temporary inconsistency |
| Read Replicas     | Read scalability                    | Replication lag                  |
| Stateless Services| Horizontal scale of app servers     | Need external state store        |
| Connection Pool   | DB connection exhaustion            | Pool sizing tuning required      |

[Back to Top](#top)

<a id="11-practice-questions"></a>
# 11. Practice Questions

> **Practice:** [Q30 - consistent-hashing](../system_design_practice_questions_100.md#q30--thinking--consistent-hashing)
> **Practice:** [Q53 - rate-limiting-at-scale](../system_design_practice_questions_100.md#q53--design--rate-limiting-at-scale)
> **Practice:** [Q68 - write-heavy-optimisations](../system_design_practice_questions_100.md#q68--thinking--write-heavy-optimisations)
> **Practice:** [Q70 - thundering-herd](../system_design_practice_questions_100.md#q70--thinking--thundering-herd)
> **Practice:** [Q71 - tail-latency-p99](../system_design_practice_questions_100.md#q71--interview--tail-latency-p99)
> **Practice:** [Q79 - explain-consistent-hashing](../system_design_practice_questions_100.md#q79--interview--explain-consistent-hashing)
> **Practice:** [Q80 - explain-rate-limiting-pm](../system_design_practice_questions_100.md#q80--interview--explain-rate-limiting-pm)
> **Practice:** [Q92 - design-rate-limiter-service](../system_design_practice_questions_100.md#q92--design--design-rate-limiter-service)
> **Practice:** [Q26 - read-heavy-write-heavy](../system_design_practice_questions_100.md#q26--design--read-heavy-write-heavy)

[Back to Top](#top)

<a id="12-summary"></a>
# 12. Summary

| Pattern | One-Line Takeaway |
|---|---|
| CQRS | Separate read and write models when read/write ratios are skewed |
| Event Sourcing | Store events not state when you need audit trails or time travel |
| Push Fan-Out | Pre-compute reads at write time for fast timelines |
| Pull Fan-Out | Compute at read time to avoid write hotspots from celebrities |
| Saga | Orchestrate distributed transactions via compensating actions |
| Write Amplification | One logical write costs N physical writes -- know your N |
| Read Amplification | One logical read costs N physical reads -- know your N |
| Stateless Services | Push state external so any server handles any request |
| Read Replicas | Scale reads horizontally while writes stay on primary |
| Connection Pooling | Share persistent connections to prevent DB exhaustion |

Vijay's final lesson: "Every pattern has a cost. The art is knowing which cost you can afford at your current scale -- and which pattern to reach for next."

[Back to Top](#top)

<a id="navigation"></a>
## Navigation

| | |
|---|---|
| Previous | [10 - Distributed Systems](../10_distributed_systems/theory.md) |
| Next | [12 - Microservices](../12_microservices/theory.md) |
| Home | [README.md](../README.md) |

**[Back to README](../README.md)**

**Prev:** [Distributed Systems](../10_distributed_systems/theory.md) | **Next:** [Microservices](../12_microservices/theory.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) | [Interview Q&A](./interview.md)
