# 11 — Scalability Patterns Playbook

---

## The Core Problem: From 1K to 1M Users

Imagine you built a web app. It works great. You have 1,000 users, one server, one database. Life is simple.

Then your app goes viral.

```
Day 1:        [1K users]  → [ Your Server ] → [ Your DB ]   ✓ Fine

Day 30:       [1M users]  → [ Your Server ] → [ Your DB ]   ✗ Server on fire
                                                               ✗ DB melting
                                                               ✗ You're paged at 3am
```

What breaks, exactly?

- **CPU/Memory**: One server can only handle so many concurrent requests before it buckles.
- **Database**: Queries that took 5ms now take 5 seconds. Indexes help, but only so far.
- **Disk I/O**: Every write, every read — it all flows through one spindle.
- **Network**: The single server becomes a bottleneck just accepting connections.
- **Deployments**: Any change means downtime for everyone.

Scaling isn't one trick. It's a playbook — a collection of patterns you reach for depending on where the pressure is. This chapter covers the most important ones.

---

## Pattern 1: CQRS — Read and Write are Different Problems

Here's a fact that most beginners miss:

> **Most applications read 10 to 100 times more than they write.**

A tweet is written once. It's read millions of times. A product listing is updated occasionally. It's browsed constantly.

Despite this, traditional CRUD apps treat reads and writes identically — the same model, the same table, the same code path. That's the problem.

**CQRS** (Command Query Responsibility Segregation) says: split them.

```
TRADITIONAL (one model for everything):
    [User] --write--> [App] ---> [DB]
    [User] --read --> [App] ---> [Same DB]   ← no distinction

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

### The Write Side

- **Normalized** — data stored without redundancy, easy to update consistently.
- **Validated** — every command goes through business rules before being accepted.
- **Slower reads are okay** — the write side is not optimized for querying.

### The Read Side

- **Denormalized** — data pre-joined and flattened for fast retrieval.
- **Eventually consistent** — it lags behind the write side slightly (milliseconds to seconds).
- **Can be multiple** — you can have several read models optimized for different query patterns.

### A Concrete Example

```
Write DB (normalized):
    orders:     id, user_id, created_at
    order_items: id, order_id, product_id, quantity
    products:   id, name, price

Read DB (denormalized, for "show order summary"):
    order_summaries: order_id, user_name, items_as_json, total_price, created_at
    ← pre-computed, one row per order, no joins needed at query time
```

### When to Use CQRS

- Read/write ratio is highly skewed.
- Different teams own reads vs writes.
- You need to scale reads independently.

### When NOT to Use CQRS

- Simple CRUD apps — the complexity isn't worth it.
- Teams with fewer than ~10 engineers — you'll spend more time on plumbing than features.

---

## Pattern 2: Event Sourcing — Store What Happened, Not What Is

Most databases store **current state**. You update a row. The old value is gone.

Event Sourcing flips this: **store every event that happened**. Current state is derived by replaying events.

### The Bank Account Analogy

```
TRADITIONAL (state-based):
    accounts table:
    | user_id | balance |
    | 42      | $350    |   ← just the current balance, history gone

EVENT SOURCED:
    events table:
    | event_id | user_id | type       | amount | timestamp           |
    | 1        | 42      | DEPOSIT    | $500   | 2024-01-01 09:00    |
    | 2        | 42      | WITHDRAWAL | $200   | 2024-01-03 14:30    |
    | 3        | 42      | DEPOSIT    | $50    | 2024-01-05 11:00    |
    ← replay these: 500 - 200 + 50 = $350 ✓
```

Every change is an immutable event. You never update or delete events — you only append.

### Replaying State

```
function getCurrentBalance(userId):
    events = db.query("SELECT * FROM events WHERE user_id = ? ORDER BY event_id", userId)
    balance = 0
    for event in events:
        if event.type == DEPOSIT:    balance += event.amount
        if event.type == WITHDRAWAL: balance -= event.amount
    return balance
```

For performance, you periodically take **snapshots** so you don't replay from the beginning of time.

```
[Event 1] → [Event 2] → [Event 3] → ... → [Snapshot at Event 100] → [Event 101] → [Event 102]
                                                     ↑
                            Start replay from here, not from Event 1
```

### Benefits

- **Audit trail built-in** — every change is recorded. Banks love this. Compliance loves this.
- **Time travel** — "What was this user's balance on January 3rd at 2pm?" Just replay up to that point.
- **Multiple read models** — replay the same events into different shapes for different query needs.
- **Debugging** — you can replay events locally to reproduce any bug.

### The Cost

- **Complexity** — it's a fundamentally different paradigm. Harder to onboard new engineers.
- **Query performance** — you can't just `SELECT balance FROM accounts WHERE user_id = 42`. You need read models.
- **Schema evolution** — old events are immutable, so changing event structure is tricky.
- **Storage** — you're storing everything forever.

Event Sourcing is powerful. It's also genuinely complex. Don't use it because it sounds cool. Use it when auditability, time travel, or multiple read projections justify the cost.

---

## Pattern 3: Fan-Out — One Event, Many Side Effects

When a user posts a tweet, what needs to happen?

1. Store the tweet.
2. Update 10 million followers' timelines.
3. Update search index.
4. Trigger notifications for mentions.
5. Update analytics.

One action. Many side effects. That's **fan-out**.

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

### Push Fan-Out (Write-Time)

When a tweet is posted, **immediately write to every follower's timeline** cache.

```
POST /tweet by @user (100K followers)
    → Write tweet to tweets table
    → For each of 100K followers:
          redis.lpush("timeline:{follower_id}", tweet_id)   ← push to their queue

GET /timeline for @follower
    → redis.lrange("timeline:{follower_id}", 0, 50)         ← instant read
```

- **Read is fast** — pre-computed, just fetch from cache.
- **Write is expensive** — 100K followers = 100K writes per tweet.

### Pull Fan-Out (Read-Time)

When a user opens their timeline, **compute it on the fly** by fetching recent tweets from everyone they follow.

```
GET /timeline for @follower
    → following_list = db.query("SELECT followed_id FROM follows WHERE follower_id = ?")
    → for each followed_id:
          tweets += db.query("SELECT * FROM tweets WHERE user_id = ? ORDER BY created_at DESC LIMIT 10")
    → merge, sort, return top 50
```

- **Write is cheap** — just write the tweet once.
- **Read is expensive** — if you follow 1,000 people, that's 1,000 queries per timeline load.

### The Celebrity Problem

Push fan-out has a brutal edge case: celebrities.

```
@celebrity (10M followers) posts a tweet

Push fan-out:
    10,000,000 × redis.lpush()  ← this takes minutes
    Other users' timeline writes get queued behind this

This is called "hotspot" or "thundering herd" on write.
```

**Hybrid solution** (used by Twitter/X historically):

```
Regular users (< 1M followers)  → push fan-out   (fast for their followers)
Celebrities (> 1M followers)    → pull fan-out    (compute at read time)

At read time:
    timeline = redis.get("timeline:{user_id}")     ← pre-pushed from regular follows
    + db.query(tweets from celebrities you follow) ← pulled and merged in
```

---

## Pattern 4: The Saga Pattern — Distributed Transactions Without the Pain

You're building a travel booking app. A user books a trip: flight + hotel + rental car.

All three must succeed, or none should be charged.

In a monolith, you'd wrap this in a database transaction:

```sql
BEGIN TRANSACTION
    INSERT INTO flight_bookings ...
    INSERT INTO hotel_bookings ...
    INSERT INTO car_bookings ...
COMMIT  -- or ROLLBACK if anything fails
```

In a microservices world, each booking lives in a different service with its own database. **You cannot do a cross-service ACID transaction.**

This is the distributed transaction problem. The Saga pattern solves it.

### What is a Saga?

A saga is a sequence of local transactions. If any step fails, compensating transactions undo the previous steps.

```
HAPPY PATH:
    [Book Flight] → success
         |
         v
    [Book Hotel]  → success
         |
         v
    [Book Car]    → success
         |
         v
    DONE ✓

FAILURE PATH (hotel fails):
    [Book Flight] → success
         |
         v
    [Book Hotel]  → FAIL
         |
         v
    [Cancel Flight] ← compensating transaction
         |
         v
    DONE (trip cancelled cleanly) ✓
```

### Two Flavors of Saga

**Choreography — services talk to each other via events:**

```
[Flight Service]  -- emits "flight_booked"  --> [Hotel Service]
[Hotel Service]   -- emits "hotel_booked"   --> [Car Service]
[Car Service]     -- emits "car_booked"     --> [Booking Complete]

On failure:
[Hotel Service]   -- emits "hotel_failed"   --> [Flight Service]
[Flight Service]  -- on "hotel_failed": cancel flight
```

- Simple, no central coordinator.
- Hard to debug — the "flow" of the saga is implicit, spread across services.
- Good for simple sagas with 2-3 steps.

**Orchestration — a central saga coordinator drives the flow:**

```
                [Saga Orchestrator]
                        |
              +---------+---------+
              |                   |
    [Flight Service]    [Hotel Service]    [Car Service]
              |                   |                |
          "book"              "book"            "book"
              |                   |                |
    orchestrator tracks state, calls each, handles rollback

On failure:
    orchestrator calls "cancel" on Flight Service explicitly
```

- Explicit flow — the saga logic lives in one place.
- Easier to monitor and debug.
- The orchestrator becomes a bottleneck and a new point of failure.
- Good for complex sagas with many steps or conditional logic.

### What "Eventual Consistency" Means Here

During a saga, the system is temporarily inconsistent. The flight is booked but the hotel hasn't been confirmed yet. This window is unavoidable. You design for it:

- Keep sagas as short-lived as possible.
- Make compensating transactions idempotent (safe to run multiple times).
- Use status fields: `PENDING → CONFIRMED → CANCELLED`.

---

## Pattern 5: Write Amplification vs Read Amplification

Every architectural decision is a trade-off between read cost and write cost.

```
WRITE AMPLIFICATION:
    One logical write → many physical writes

    Example: CQRS with 3 read models
        User updates their name (1 write)
        → Write DB updated (1 write)
        → Read Model 1 updated (1 write)
        → Read Model 2 updated (1 write)
        → Read Model 3 updated (1 write)
        = 4 writes for 1 logical change

READ AMPLIFICATION:
    One logical read → many physical reads

    Example: Pull fan-out timeline
        User loads timeline (1 read)
        → Query 500 followed users' recent tweets (500 reads)
        → Merge and sort results
        = 500 reads for 1 logical query

STORAGE AMPLIFICATION:
    One piece of data → stored multiple times

    Example: denormalized read model
        User name stored in users table, order_summaries table,
        review_summaries table, etc.
        Update name once → inconsistency until all models sync
```

There's no free lunch. When you optimize reads, you usually pay in writes (and vice versa). The right trade-off depends on your read/write ratio, latency requirements, and consistency needs.

---

## Pattern 6: Horizontal Scaling Patterns

Once you understand the data patterns above, here's how to actually add machines.

### Stateless Services

The golden rule of horizontal scaling:

> **If any server can handle any request, you can add servers freely.**

```
STATEFUL (bad for scaling):
    Server 1 holds user session in memory
    Server 2 doesn't know about it
    Load balancer sends user to Server 2 → user logged out ← bad

    [User] → [Load Balancer] → [Server 1] ← holds session
                           ↗ [Server 2] ← doesn't hold session
                           ↗ [Server 3] ← doesn't hold session

STATELESS (good for scaling):
    Session stored in Redis (external)
    Any server can read it
    Add/remove servers freely

    [User] → [Load Balancer] → [Server 1] ↘
                           ↗ [Server 2] →→ [Redis] (shared session store)
                           ↗ [Server 3] ↗
```

Make your application servers stateless. Push state to a database, cache, or message queue.

### Database Read Replicas

Writes still go to one primary. Reads can be spread across replicas.

```
                    ┌─────────────────┐
                    │   Primary DB    │  ← all writes go here
                    └────────┬────────┘
                             │ replication (async, usually < 100ms lag)
              ┌──────────────┼──────────────┐
              │              │              │
    ┌─────────┴───┐  ┌───────┴─────┐  ┌────┴──────────┐
    │  Replica 1  │  │  Replica 2  │  │   Replica 3   │
    └─────────────┘  └─────────────┘  └───────────────┘
          ↑                ↑                  ↑
     read traffic     read traffic        read traffic
```

- Reads scale horizontally. Add more replicas for more read capacity.
- Writes are still single-server. For write scaling, you need sharding (see Chapter 07).
- Replication lag: replicas may be slightly behind the primary. Reads may return stale data.

### Connection Pooling

Databases have a limited number of connections. Opening a new connection per request is expensive (TCP handshake, auth, memory allocation on DB side).

```
WITHOUT POOLING:
    [Server] ←→ connect ←→ [DB]  (per request)
    [Server] ←→ connect ←→ [DB]  (per request)
    [Server] ←→ connect ←→ [DB]  (per request)
    100 concurrent requests = 100 DB connections = DB out of memory

WITH POOLING (PgBouncer, HikariCP, etc.):
    [Server] ←→ [Connection Pool (20 connections)] ←→ [DB]
    100 concurrent requests share 20 persistent connections
    Requests queue for a free connection (milliseconds)
    DB stays healthy
```

Connection pooling is often the first lever to pull when a database starts dropping connections under load.

---

## Putting It Together

These patterns don't exist in isolation. A real high-scale system might combine:

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

Start simple. Add patterns only when you have concrete evidence that you need them. A startup with 1,000 users does not need event sourcing.

---

## Quick Reference

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

---

## Navigation

| Direction | Link |
|-----------|------|
| Previous  | [10 — Distributed Systems](../10_distributed_systems/theory.md) |
| Next      | [12 — Microservices](../12_microservices/monolith_to_micro.md) |
| Home      | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
