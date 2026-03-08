# Scenario Questions — Open-Ended System Design Prompts
> These are the questions that separate engineers who know concepts from engineers who can apply judgment.
> Each scenario is open-ended by design. Strong answers demonstrate trade-off reasoning, not memorized architectures.

---

## How to Use These Scenarios

The scenarios in this file are not trivia questions with right answers. They are probes for judgment. When you practice them, do not try to memorize the "strong answer elements" — internalize the reasoning structure behind each one.

For each scenario, practice answering in this order:
1. Ask one or two clarifying questions before saying anything else.
2. State the key constraints and what makes the problem hard.
3. Walk through your approach one layer at a time, starting simple.
4. Name the trade-offs you are making at each step.
5. Acknowledge the failure modes in your design.

Time yourself. Each scenario should produce a 10–15 minute verbal answer in an interview. If you can only talk for 3 minutes, you need more depth. If you are still talking at 20 minutes, you are going too deep into one area at the expense of the full picture.

The "Common mistakes" sections are what interviewers take notes on. They are the signals that distinguish a passing answer from a strong one.

---

## What Makes a Scenario Answer Fail at the Senior Level

Most candidates can describe the right components for a well-known problem. What separates a senior-level answer is the layer of thinking underneath the components.

**Failing pattern: components without trade-offs.** A candidate describes the architecture accurately — load balancer, app servers, Redis, database — but never names what could go wrong with each choice, when this design would break down, or what they gave up to get here. Senior engineers think adversarially about their own designs.

**Failing pattern: solutions without requirements.** Every scenario has parameters that change the answer. "Real-time notifications for 10M users" is different if the notification must be delivered in 100ms (requires persistent connections) vs. 5 seconds (allows long-polling) vs. 30 seconds (push notifications are fine). Senior candidates ask what "real-time" means before designing anything.

**Failing pattern: one right answer.** The best candidates present two or three approaches and explain why they are choosing one over the others given the stated constraints. "I could use Kafka or Redis Pub/Sub here — I'll use Redis because at this scale the persistence Kafka provides is not needed and the operational complexity is not justified, but if the requirement were replay capability, I'd switch to Kafka."

**Failing pattern: ignoring operational concerns.** A design is not complete without answering how you deploy it, how you debug it when it fails at 2am, how you roll back, and what your monitoring strategy is. Operational maturity is a strong positive signal at senior and staff level.

---

## Quick Reference: Scenario-to-Pattern Mapping

```
Scenario                            Core patterns to demonstrate
──────────────────────────────────────────────────────────────────
API is slow                         Observability-first debugging, slow query analysis,
                                    N+1 detection, connection pool diagnosis

Database bottleneck                 Write optimization order, LSM-tree vs B-tree,
                                    sharding trade-offs, write amplification

Real-time notifications             WebSocket connection management, pub/sub fan-out,
                                    push/pull hybrid, APNs/FCM for offline users

Data corruption incident            Incident management phases, blast radius scoping,
                                    PITR recovery, blameless postmortem

Cascading failures                  Circuit breaker, bulkhead, timeout, retry with jitter,
                                    graceful degradation, hard vs soft dependencies

Distributed rate limiter            Redis INCR / sorted set, sliding window, fixed window
                                    trade-offs, fail-open vs fail-closed, shard by user

Monolith to microservices           Strangler Fig, modular monolith first, Conway's Law,
                                    observability prerequisites, per-service CI/CD

Zero-downtime DB migration          Nullable-first, dual-write, batched backfill,
                                    concurrent index, verify before constraint

Global leaderboard                  Redis Sorted Set (ZADD/ZREVRANK), memory sizing,
                                    ZADD GT flag, regional replication, persistence

Traffic spike preparation           Load test first, progressive rollout, cache warm-up,
                                    auto-scaling lead time, feature flags, runbook
```

---

## Navigation

```
1.  "Our API is getting slow. Diagnose and fix it."
2.  "The database is the bottleneck. We can't scale it further. What do you do?"
3.  "We need real-time notifications for 10M users."
4.  "A critical bug is live and corrupting user data. Walk me through your response."
5.  "Cascading failures are taking down multiple services at once."
6.  "Design a rate limiter that works across 50 API servers."
7.  "Our monolith is getting hard to deploy. When and how do you move to microservices?"
8.  "Migrate a live database with zero downtime."
9.  "Design a global leaderboard that updates in real time."
10. "We're launching a feature that could 10x our traffic overnight."
```

---

## Scenario 1: "Our API is getting slow — users are complaining. Diagnose and fix it."

**The problem**: Response times have degraded over the past week. Some users see 5-second page loads. The service handled this traffic volume fine two weeks ago. No recent deployments were made.

**What the interviewer is testing**: Whether you have a systematic debugging process for production performance problems. Strong candidates do not guess — they instrument, measure, and isolate.

**Strong answer elements**:
- Start by defining "slow" precisely before proposing solutions. What endpoint? What percentile? What changed? Is it all requests or specific ones? Is it time-of-day dependent?
- Examine the observability stack first: APM traces (Datadog, Jaeger) to find where latency is being spent. Is it in the application layer, the database, an external service call, or the network?
- Check for the most common causes in order of likelihood: slow database queries (check slow query log, EXPLAIN ANALYZE on the slowest queries), missing index added after a table grew past a threshold, N+1 queries introduced by a recent code change, connection pool exhaustion (pool size vs. traffic), upstream service degradation, or a memory leak causing GC pauses.
- For database causes specifically: check for index scans that became table scans as data grew, queries with `SELECT *` returning far more data than before, lock contention on hot rows, or autovacuum disruption in Postgres.
- Propose short-term mitigation (add missing index, increase connection pool) and long-term fixes (query optimization, read replica for reporting queries, caching for hot read paths).

**Common mistakes**:
- Jumping to "add caching" or "add more servers" before diagnosing. Scaling a broken query does not fix the query — it just makes the problem more expensive.
- Not asking what changed (data volume, traffic pattern, dependency health). "Nothing changed" is almost always untrue.
- Treating the symptom (slow response) without identifying the root cause layer (application? network? database? external dependency?).
- Proposing architectural changes (sharding, microservices) for a problem that is probably a missing index.

---

## Scenario 2: "The database is the bottleneck. We can't scale it further. What do you do?"

**The problem**: You have a single Postgres primary with read replicas. The primary is at CPU saturation during peak hours. Adding read replicas doesn't help because the writes themselves are the bottleneck — 40,000 writes/second, and the primary can only sustain ~12,000.

**What the interviewer is testing**: Whether you know the progression of database scaling options, their trade-offs, and the order in which to apply them. The worst answer is "just shard it" without exploring cheaper options first.

**Strong answer elements**:
- First verify the write bottleneck. Profile the writes: are they all necessary writes? Can any writes be buffered and batched (write coalescing)? Can async writes replace synchronous ones for non-critical data?
- Check write patterns for waste: are you writing the same data multiple times? Are you using transactions where a single statement would do? Are indexes creating unnecessary write amplification (every write to a table with 10 indexes does 11 writes)?
- Layer 1 mitigation — caching at write time: write-behind cache absorbs bursts and flushes to the DB at a sustainable rate. Appropriate only for loss-tolerant data.
- Layer 2 mitigation — vertical scaling: have you actually hit the ceiling? A Postgres instance on a 96-core machine with NVMe SSD and tuned work_mem and max_connections can sustain far more than a default install.
- Layer 3 — read/write splitting: route all writes to the primary, all reads to replicas. This does not help pure write bottlenecks but reduces read pressure that competes with writes for I/O.
- Layer 4 — write sharding: partition the data across multiple primaries by a shard key. Enables linear write scalability. Cost: cross-shard queries, no cross-shard transactions, complex rebalancing, application-level routing.
- Layer 5 — purpose-built write-optimized stores: Cassandra (LSM-tree, extremely high write throughput), DynamoDB (auto-scaling, fully managed), TimescaleDB for time-series. Choose based on access pattern, not just write volume.

**Common mistakes**:
- Going directly to sharding without exploring caching, batching, or proper vertical scaling.
- Not profiling writes — assuming all writes are necessary and correctly structured.
- Proposing NoSQL as a drop-in replacement without addressing the consistency and query flexibility trade-offs.
- Missing write amplification from excessive indexes as a likely culprit.

---

## Scenario 3: "We need real-time notifications for 10M concurrent users. How do you build it?"

**The problem**: A consumer app wants to push notifications to users the moment a relevant event occurs — a friend posts, a bid is accepted, a message is received. 10M users are online simultaneously during peak hours. Delivery must happen within 1 second of the triggering event.

**What the interviewer is testing**: Understanding of WebSocket infrastructure at scale, pub/sub fan-out, connection management, and graceful degradation. This is a genuinely hard distributed systems problem.

**Strong answer elements**:
- Connection management: at 10M concurrent connections, each holding a WebSocket open, you cannot put all connections on one server. A single WebSocket server handles ~50,000–100,000 connections with tuned file descriptor limits. You need ~100–200 connection servers. Each server maintains a map of {user_id → connection_handle}.
- The fan-out problem: when a triggering event occurs (user A posts, which should notify 500 followers), a naive approach queries the follower list and sends 500 individual notifications. This is fine for most users but breaks for celebrities with millions of followers. The same push/pull hybrid used in social feed design applies here.
- Message routing: when an event is published, how does it find the right connection server? Use a pub/sub layer (Redis Pub/Sub or Kafka) — the event publishing service publishes to a topic; all connection servers subscribe; each server delivers to locally connected users matching the event. This requires each server to only deliver to its own connections.
- Redis Pub/Sub limitations: messages are not persisted — if a connection server is restarted, it loses messages published during the restart. For higher durability, use Kafka topics per user or per user-group, with connection servers as consumer groups.
- Offline users: users who are not connected need push notifications via APNs (iOS), FCM (Android), or Web Push. The same event pipeline should fork — one path for WebSocket delivery to online users, one path to a push notification service for offline users.
- Graceful degradation: if the WebSocket connection drops, fall back to long-polling. If long-polling is unavailable, fall back to the client polling on a regular interval.

**Common mistakes**:
- Designing for a single notification server (SPOF and does not scale to 10M connections).
- Using HTTP polling as the primary mechanism — generates enormous load at 10M users even at a 5-second interval (2M requests/second).
- Ignoring the offline user path — real products need push notifications, not just WebSocket delivery.
- Not addressing the celebrity/high-fanout problem — sending 1M WebSocket messages synchronously in a request handler will time out.

---

## Scenario 4: "A critical bug went to production and is corrupting user data. Walk me through your response."

**The problem**: A monitoring alert fired 10 minutes ago. User reports are coming in. A bug in a background job is writing incorrect values to user account balances. The job has been running for 2 hours. You are the on-call engineer.

**What the interviewer is testing**: Incident management judgment. This tests whether you are calm, systematic, and prioritize mitigation over root cause analysis in the heat of the moment. Senior engineers know: stop the bleeding first, understand why later.

**Strong answer elements**:
- Immediate: stop the job. Before any investigation, kill the corrupting process. Every second it runs is more corrupted data. Use a feature flag, kill the process directly, or deploy a hotfix that disables the job.
- Scope the blast radius before doing anything else: how many records are affected? Which users? What time range? Run read-only queries against a replica — do not query the primary while an incident is ongoing (risk of additional load). This drives the rest of the decision-making.
- Communication: notify stakeholders within 5 minutes of declaring an incident. Set up an incident channel. Assign roles: incident commander (coordinates), tech lead (investigates), comms (handles customer/management communications). Updates every 15–30 minutes even if you have nothing new — silence is worse than "we're still investigating."
- Data recovery options in order: (1) point-in-time recovery from a database backup — best if the corruption window is short and clean; (2) replay transactions from the WAL/audit log before the bug was introduced; (3) restore from a snapshot and re-apply valid events since then; (4) manual correction via a reverse-migration script if the corruption pattern is deterministic and reversible.
- Post-incident: write a blameless postmortem within 48 hours. What happened, what was the timeline, what mitigations are needed to prevent recurrence and limit blast radius next time (feature flags, dry-run mode for background jobs, data validation checks, alerting on anomalous write patterns).

**Common mistakes**:
- Trying to understand root cause before stopping the damage. Analysis while the bug runs makes the problem bigger.
- Querying the primary database heavily while it is under incident stress.
- Not scoping the impact before choosing a recovery path — jumping to "restore from backup" before knowing that only 500 of 10M records are affected.
- Fixing the bug and deploying before understanding the full impact of the existing corruption.
- Failing to communicate status to stakeholders until the fix is complete.

---

## Scenario 5: "We're experiencing cascading failures — one service going down takes others with it. How do you prevent this?"

**The problem**: Service A calls Service B synchronously. When B is slow or down, A's thread pool fills with waiting requests, A becomes slow, and now Service C (which calls A) also fails. A localized outage in B has taken down A and C.

**What the interviewer is testing**: Understanding of resilience patterns in distributed systems — circuit breakers, bulkheads, timeouts, and backpressure. The ability to describe these patterns correctly and know when each applies.

**Strong answer elements**:
- Timeouts: every network call must have a timeout. A synchronous call with no timeout will block a thread forever if the downstream service hangs. Timeouts bound the blast radius of slow dependencies. Set timeouts based on your SLO, not based on what you think the downstream should be able to do.
- Circuit breakers: track the error rate on calls to B. After a threshold is exceeded (e.g., 50% errors in a 10-second window), "open" the circuit — subsequent calls to B fail immediately without attempting the network call. After a cooldown period, allow a probe request through ("half-open"). If it succeeds, close the circuit. This prevents A from being held hostage by a degraded B and gives B time to recover. Hystrix, Resilience4j, and service meshes like Envoy implement this.
- Bulkheads: give each downstream dependency its own thread pool or connection pool. If calls to B are slow, only B's pool fills up — calls to C, D, and E from the same service continue normally. Bulkheads contain failure to a single dependency rather than contaminating the entire service.
- Graceful degradation: design services to function in a reduced capacity when dependencies fail. If the recommendation service is down, return an empty recommendation list rather than failing the entire page load. If the user profile service is unavailable, return cached profile data. Identify which dependencies are required for core functionality and which are enrichments.
- Retry with exponential backoff and jitter: retries add load to an already-struggling service. Naive retries (immediate, fixed interval) amplify the load spike. Exponential backoff with random jitter spreads retry load over time and gives the downstream service room to recover.

**Common mistakes**:
- Describing circuit breakers without also describing timeouts — a circuit breaker without a timeout still lets calls hang until the timeout fires.
- Not mentioning graceful degradation — resilience is not just about reducing cascading load but about maintaining useful behavior for users.
- Suggesting "just retry" without acknowledging that retries without backoff and jitter can make cascading failures worse.
- Assuming all services in a cascade are equally critical — understanding which dependencies are soft (can be skipped) vs. hard (service cannot function without them) is a key architectural decision.

---

## Scenario 6: "Design a rate limiter that works across 50 API servers."

**The problem**: You have 50 stateless API servers behind a load balancer. You need to enforce a rate limit of 1,000 requests per minute per user. A per-server in-memory counter does not work because a user's requests are distributed across all 50 servers.

**What the interviewer is testing**: The ability to design a concrete distributed system component from requirements to implementation, including the specific data structures and failure modes.

**Strong answer elements**:
- Central counter store: use Redis as the shared counter. All 50 API servers call the same Redis instance to check and update rate limit state. Redis operations are atomic (INCR is atomic) and fast enough for this use case (~100µs per call).
- Fixed window implementation: on each request, `INCR user:{id}:window:{current_minute}`. Set a TTL of 60 seconds on the key so it auto-expires. If the returned count exceeds 1,000, return 429. The weakness: requests at the end of one window and the start of the next can burst to 2,000 in 2 seconds (the "window boundary" problem).
- Sliding window implementation: use a Redis sorted set. Key is `ratelimit:user:{id}`. On each request: `ZADD` the current timestamp as both score and member, `ZREMRANGEBYSCORE` to remove entries older than 60 seconds, `ZCARD` to count remaining entries, return 429 if over limit, and `EXPIRE` the key for garbage collection. Accurate but uses more memory — O(N) memory where N is requests per window per user.
- Return meaningful headers: `X-RateLimit-Limit: 1000`, `X-RateLimit-Remaining: 750`, `X-RateLimit-Reset: 1699999200`. These are required for any usable rate limiter.
- Failure handling: if Redis is unavailable, what do you do? Options: (a) fail open (allow all requests) — you lose rate limiting but keep availability; (b) fail closed (reject all requests) — you protect the backend but break your service. The right answer depends on the threat model. For API abuse protection, fail open. For billing-based quotas, fail closed.
- Sharding the rate limiter for very high throughput: if one Redis node cannot handle 50 × throughput, use consistent hashing to route each user to a specific Redis shard — all requests for user X always go to the same node, so a local counter works.

**Common mistakes**:
- Designing a per-server counter without acknowledging that it under-counts by a factor of 50.
- Not addressing what happens when Redis is unavailable.
- Forgetting to include rate limit headers in the response.
- Using fixed window without acknowledging the boundary burst problem and not proposing a mitigation.
- Using a rate limiter on a single synchronous path without considering the latency impact of the Redis call on every request (mitigate with local cache + periodic Redis sync for approximate limiting at scale).

**Follow-up questions interviewers ask**:
- "How would you rate limit by IP address for unauthenticated endpoints?"
- "How do you handle rate limit circumvention via multiple accounts from the same user?"
- "How do you implement tiered limits — 1,000/min for free users, 10,000/min for paid users — in the same system?"

---

## Scenario 7: "Our monolith is getting hard to deploy. When and how do you move to microservices?"

**The problem**: A 500,000-line monolith. Deployments take 45 minutes and require full regression testing. Five teams each own a domain within the monolith. A bug in the payments module delays a deployment of an unrelated feature in the notifications module. Leadership wants to "move to microservices."

**What the interviewer is testing**: This is a judgment question as much as a design question. The interviewer wants to know whether you understand the real cost of microservices decomposition and the conditions under which it is justified.

**Strong answer elements**:
- Make the case for NOT migrating immediately. The deployment pain described has multiple cheaper fixes: modular monolith (enforcing package-level boundaries within the monolith), feature flags (deploy code without activating features), automated test parallelization (reduce the 45-minute regression), and clear domain ownership within the codebase. Microservices solve deployment coupling but add distributed systems complexity — that trade-off is not always worth it.
- When decomposition IS justified: when a specific module has significantly different scaling requirements from the rest of the monolith (the recommendation engine needs 50 GPU instances; the rest need 10 CPU instances), when different modules need different release cadences and the coupling genuinely cannot be broken at the module level, or when team autonomy is being blocked by the shared codebase (multiple teams frequently conflict in the same code).
- Strangler Fig pattern: do not rewrite the monolith. Instead, identify a single, well-bounded service to extract first (typically one with a clear, stable API, limited shared state, and no circular dependencies with the rest of the monolith). Route relevant traffic to the new service via the API gateway. Once stable, extract the next service. The monolith continues to run throughout.
- Prerequisite infrastructure before any extraction: observability (distributed tracing is essential when calls span services), service discovery (how does Service A find Service B?), centralized logging, a deployment pipeline per service, and API contracts between services (protobuf/OpenAPI specs with versioning).
- The organizational point: Conway's Law says the system architecture mirrors the communication structure of the organization. Microservices work when team ownership is clear. If five teams all touch the same service post-migration, you have gained the operational cost of microservices without the ownership benefit.

**Common mistakes**:
- Treating "move to microservices" as the given answer and jumping straight to decomposition strategy without questioning the premise.
- Not mentioning the Strangler Fig pattern — rewriting the monolith from scratch is the highest-risk approach and almost never finishes.
- Underestimating the operational cost: each extracted service needs its own CI/CD pipeline, monitoring, on-call rotation, and deployment process.
- Not establishing observable prerequisites before decomposing — debugging a distributed system without distributed tracing is extremely painful.

**Follow-up questions interviewers ask**:
- "How do you handle shared database tables that are accessed by both the monolith and the newly extracted service during the transition?"
- "How do you handle shared authentication — the monolith uses session cookies; the new service needs a different auth mechanism?"
- "What is your criteria for declaring the migration complete?"

---

## Scenario 8: "You need to migrate a live database with zero downtime. How?"

**The problem**: You need to add a `normalized_email` column to the `users` table (100M rows), backfill it, and eventually drop the old `email` column. The users table receives 5,000 writes/second. Any downtime or data corruption is unacceptable.

**What the interviewer is testing**: The ability to execute database changes safely in a live production environment using multi-phase migrations. This is one of the most common failure modes in production engineering.

**Strong answer elements**:
- Phase 1 — Add the column as nullable, with no default: `ALTER TABLE users ADD COLUMN normalized_email VARCHAR(255);`. In most databases, adding a nullable column without a default is a metadata-only change and is nearly instant (no table rewrite). Do NOT add a default value or NOT NULL constraint yet — that rewrites the table.
- Phase 2 — Dual-write: deploy application code that writes to both `email` and `normalized_email` on every user write. New records are fully populated. Old records are still NULL in the new column.
- Phase 3 — Backfill: write a background job that updates `normalized_email` for rows where it is NULL. Do NOT run `UPDATE users SET normalized_email = LOWER(TRIM(email))` in a single transaction — it will lock the entire table. Run it in batches of 1,000–10,000 rows with a short pause between batches to avoid overwhelming the primary. Monitor replication lag.
- Phase 4 — Verify: run a check that counts rows where `normalized_email IS NULL`. Once zero, verify a sample of rows for correctness.
- Phase 5 — Add NOT NULL constraint and index: use a concurrent index build (`CREATE INDEX CONCURRENTLY` in Postgres) to avoid table locking. Adding a NOT NULL constraint can be done safely in Postgres 12+ without a table rewrite if all rows are already populated.
- Phase 6 — Switch reads: deploy application code that reads from `normalized_email` instead of computing from `email`.
- Phase 7 — Remove old column: after at least one deployment cycle confirming no code reads `email` for this purpose, drop the column. Again, check for any foreign keys, indexes, or views that reference `email` before dropping.

**Common mistakes**:
- Running a single large UPDATE that locks the table — this causes write timeouts and replication lag spikes that can cascade.
- Adding NOT NULL with a DEFAULT value in one ALTER TABLE statement — this triggers a full table rewrite in older database versions, locking the table for minutes to hours on large tables.
- Forgetting dual-write — migrating old rows but not writing to the new column on new writes means the backfill is never complete.
- Rushing Phase 6 and 7 — leaving insufficient time between deploying dual-write code and removing the old column. A failed deployment that requires rollback may need the old column to still exist.

**Follow-up questions interviewers ask**:
- "The table you are migrating has 50 foreign key references from other tables. How does that change your plan?"
- "How do you handle the backfill if the table is receiving inserts faster than the backfill job can process?"
- "How would you handle migrating from one database engine to a completely different one (e.g., MySQL to Cassandra) with zero downtime?"

---

## Scenario 9: "Design a global leaderboard that updates in real time."

**The problem**: A mobile game has 50M active players globally. When a player completes a level, their score updates. Players can view a global leaderboard of the top 1,000 players, and their own rank among all players. The leaderboard must reflect the most recent scores within 5 seconds.

**What the interviewer is testing**: How to use the right data structure for the access pattern, at what point to denormalize or pre-compute, and how to handle high write throughput with a low-latency read requirement.

**Strong answer elements**:
- Redis Sorted Set is the canonical data structure for this problem: `ZADD leaderboard {score} {user_id}`. `ZREVRANGE leaderboard 0 999 WITHSCORES` returns the top 1,000 in O(log N + K) time. `ZREVRANK leaderboard {user_id}` returns a user's rank in O(log N). Updates are also O(log N). Redis handles millions of updates per second with sub-millisecond response times.
- At 50M players with 50M entries in the sorted set: memory estimate. Each entry is approximately 50 bytes (8-byte score + member string). 50M × 50 bytes = 2.5 GB. Fits comfortably in a single Redis instance (use a 4–8 GB instance with some headroom).
- Write path: when a player completes a level, the application calls `ZADD leaderboard NX score user_id` (NX = only update if new score is higher) or use `ZADD GT` flag which updates only if the new score is greater than the existing score. This is a single atomic Redis command — no race conditions.
- Handling 50M writes/day: 50M / 86,400 ≈ 578 writes/second average. Peak might be 5× = ~3,000 writes/second. Redis handles this easily on a single node.
- Global distribution: for players in Asia, a Redis instance in us-east adds ~150ms of latency per score update. Use regional Redis instances for write acceptance with async replication to a global primary for the leaderboard. Users see their regional leaderboard; the global leaderboard is eventually consistent by ~1–5 seconds.
- Persistence: Redis Sorted Sets live in memory. Use Redis RDB snapshots + AOF persistence. Have a Postgres backup store as the source of truth for player scores; the Redis sorted set is a derived cache that can be rebuilt from Postgres if lost.

**Common mistakes**:
- Storing scores in a SQL database and recomputing rank with `ORDER BY score` on every request — this is O(N) or requires a full index scan, and does not scale to 50M rows at 5-second refresh.
- Not knowing the Redis Sorted Set API (`ZADD`, `ZREVRANK`, `ZREVRANGE`) — this is a specific tool knowledge test that you will fail if you propose a generic solution.
- Forgetting to handle the "player's own rank" access pattern separately from the top-1000 query.
- Not discussing persistence — Redis data is lost on restart without RDB/AOF configuration.

---

## Scenario 10: "We're launching a feature that could 10x our traffic overnight. How do you prepare?"

**The problem**: Your service handles 1,000 req/s today. A partnership announcement means traffic could spike to 10,000 req/s within hours of launch. You have two weeks to prepare.

**What the interviewer is testing**: Whether you approach capacity planning systematically, understand where load concentrates in a system, and can identify failure points before they fail in production.

**Strong answer elements**:
- Load test first: before any architectural changes, run a load test at 10,000 req/s against a staging environment that mirrors production. Let the test run to failure — find the actual breaking point. You will likely discover the bottleneck is somewhere unexpected (connection pool? A slow third-party API call? An un-indexed query that was fine at 1,000 req/s?).
- Identify the critical path: map every synchronous dependency in the request path. Each one is a potential bottleneck and cascade point. For each: what is its current max throughput? What happens to your service if it fails?
- Horizontal scaling with auto-scaling policies: set up auto-scaling rules that trigger before the system is overwhelmed, not after. Scale at 60% CPU, not 90%. Configure scale-out to be fast (one-minute intervals) and scale-in to be slow (10-minute cooldown) to avoid flapping.
- Cache aggressively for the launch period: identify the data most likely to be requested repeatedly. Pre-warm the cache before launch rather than letting it fill on first access (cold cache during a traffic spike causes a stampede against the database).
- Feature flags on the new feature: deploy behind a flag. Enable for 1% of traffic first, observe, then ramp up. This lets you roll back instantly if the feature causes unexpected load.
- Database: enable connection pooling if not already in place. Add read replicas for read-heavy workloads. Set query timeouts and circuit breakers so that a slow database does not cascade into a full service outage.
- Have a runbook ready: what is the rollback procedure if something goes wrong post-launch? Who is on call? What are the decision criteria for rolling back vs. pushing forward?

**Common mistakes**:
- Proposing architectural changes (sharding, microservices) before running a load test to find the actual bottleneck.
- Not mentioning auto-scaling — adding instances manually during a spike is too slow.
- Forgetting the cache warm-up step — a cold cache during a spike is as dangerous as no cache.
- No mention of feature flags or progressive rollout — launching all-or-nothing to 100% of users on day one is high-risk.

**Follow-up questions interviewers ask**:
- "Your load test showed the database connection pool exhausts at 7,000 req/s. You have one week left. What do you do?"
- "The feature launched, traffic spiked to 15x, not 10x. Walk me through what you do in the first 30 minutes."
- "How do you know when it is safe to scale back down after the spike?"

---

## Navigation

| | |
|---|---|
| Home | [README.md](../README.md) |
| Interview Framework | [23 — Interview Framework](../23_interview_framework/the_45_minute_playbook.md) |
| Rapid Fire Q&A | [rapid_fire.md](./rapid_fire.md) |
| Company Patterns | [company_patterns.md](./company_patterns.md) |
