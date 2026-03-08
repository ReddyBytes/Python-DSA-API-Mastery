# The 45-Minute System Design Playbook

> You have been given the prompt: "Design YouTube."
> The clock starts.
> Most candidates open with: "So we'd use a microservices architecture..."
>
> That is the wrong move.
>
> This playbook gives you a repeatable framework for every system design interview —
> one that signals seniority, shows structured thinking, and keeps you in control.

---

## 1. The Problem with Most Interview Answers

The most common failure mode in system design interviews is not a wrong answer.
It is jumping to solutions before understanding the problem.

```
What most candidates do:
  Interviewer: "Design a URL shortener."
  Candidate:   "OK so we'd have a web server, and for the database I'd
                use PostgreSQL with an auto-increment ID, and then we'd
                hash the URL using MD5 and..."

  What the interviewer sees:
    - No requirements gathered
    - Scale unknown (10 users? 10 billion?)
    - Wrong DB choice for the actual scale
    - Wrong short code algorithm (MD5 has problems)
    - No questions asked → junior signal

What senior engineers actually do:
  Interviewer: "Design a URL shortener."
  Candidate:   "Before I start drawing boxes, I want to make sure I
                understand the problem. Can I ask a few questions?"

  What the interviewer sees:
    - Structured thinking
    - Aware that requirements drive architecture
    - Will not waste time solving the wrong problem
    - Senior signal
```

The architecture always follows the requirements. You cannot design correctly
for a system that handles 100 users and one that handles 100 million with the same answer.

---

## 2. The 45-Minute Framework

Five phases. Strict time boxes. Move through them deliberately.

```
┌──────────────────────────────────────────────────────────────────┐
│                    THE 45-MINUTE FRAMEWORK                        │
├──────────────────┬────────────────────────────────────────────────┤
│ Phase            │ Time          What you produce                 │
├──────────────────┼────────────────────────────────────────────────┤
│ 1. Requirements  │  5–7 minutes  A written list of constraints    │
│ 2. Estimation    │  3–5 minutes  Numbers: QPS, storage, bandwidth │
│ 3. High-Level    │ 10–15 minutes A diagram with named components  │
│ 4. Deep Dive     │ 10–15 minutes One component, fully explained   │
│ 5. Trade-offs    │  5 minutes    Justify every major choice       │
├──────────────────┴────────────────────────────────────────────────┤
│ Total:  ~40 minutes  (5 minutes buffer for questions)             │
└──────────────────────────────────────────────────────────────────┘
```

Each phase has a specific output. Do not move to the next phase until
you have produced that output. Do not skip phases.

---

## 3. Phase 1: Requirements — The Exact Questions to Ask

Time budget: 5–7 minutes.
Output: a written list of functional + non-functional requirements.

### Functional requirements (what does this system DO?)

Always start with the user's perspective:
```
"What are the core actions a user needs to perform?"

For YouTube:
  - Upload a video
  - Watch a video
  - Search for videos
  - Subscribe to a channel
  - Comment on a video

Then scope it:
  "Should I focus on upload + playback for this session,
   and park comments and recommendations?"

Getting the interviewer to agree on scope is not cheating.
It is professional. It shows you know how to prioritize.
```

### Non-functional requirements (how does it need to BEHAVE?)

These drive architecture more than functional requirements do.
Ask about each category:

```
Scale:
  "How many users does this need to support?"
  "What is the read-to-write ratio?"
  "Are there regional requirements? Global or single-region?"

Latency:
  "What is the acceptable latency for reads? Writes?"
  "Is this user-facing (need < 100ms) or background (minutes ok)?"

Consistency:
  "If two users write at the same time, do they need to see
   each other's writes immediately?"
  "Is eventual consistency acceptable, or do we need strong consistency?"

Availability:
  "What is the acceptable downtime? 99.9%? 99.99%?"
  "Are there peak traffic events we need to design for?"

Durability:
  "What is the cost of data loss? Is losing one record ever acceptable?"
```

### The confirmation template

After gathering requirements, summarize back:
```
"Just to confirm my understanding:

 We need a system that:
  - Functional: allows users to [core actions]
  - Scale:      handles [X] users, [Y] requests/sec
  - Latency:    reads under [Z]ms, writes can tolerate [W]ms
  - Consistency: [strong / eventual] — because [reason]
  - Availability: [SLA] — downtime is [acceptable / unacceptable] because [reason]

 For this session, I'll focus on [scope].
 I'll note [out-of-scope items] but won't design them in detail.

 Does that match what you're looking for?"
```

This is one of the highest-signal moves in the interview.
It demonstrates systems thinking before a single box is drawn.

---

## 4. Phase 2: Capacity Estimation — Quick Math Framework

Time budget: 3–5 minutes.
Output: three numbers — QPS, storage, bandwidth.

You do not need exact answers. You need order-of-magnitude estimates
that reveal which components will be under stress.

### The estimation ladder

```
Step 1: Users → DAU
        "100M monthly active users.
         Assume 10% are daily active → 10M DAU."

Step 2: DAU → requests per second
        "Each DAU makes 10 requests/day on average.
         10M × 10 = 100M requests/day
         100M / 86,400 sec ≈ 1,160 req/sec average
         Peak is 3× average → ~3,500 req/sec peak"

Step 3: Storage
        "Each item is [X] bytes.
         [Y] items created per day.
         Retain for [Z] years.
         Total = X × Y × (Z × 365)"

Step 4: Bandwidth
        "Requests/sec × payload size = MB/sec
         3,500 req/sec × 50 KB = 175 MB/sec ingress"
```

### Useful constants to memorize

```
Time:
  1 day   = 86,400 seconds  (approximate as 100K for fast math)
  1 month = 2.6M seconds
  1 year  = 31.5M seconds

Storage:
  1 KB = 10^3 bytes
  1 MB = 10^6 bytes
  1 GB = 10^9 bytes
  1 TB = 10^12 bytes

  Average user record:    ~1 KB
  Average tweet/post:     ~200 bytes
  Average image:          ~200 KB (web-optimized)
  Average video (1 min):  ~50 MB (720p)

Traffic:
  "10% of users are DAU" is a safe assumption unless told otherwise
  Read:write ratio is typically 10:1 to 100:1 for consumer apps
  Cache typically handles 80% of reads (Pareto distribution)
```

### Narrate your math out loud

```
"Let me estimate storage quickly.
 We're storing 100M URLs.
 Each URL record is roughly:
   short code:  8 bytes
   long URL:    200 bytes average
   timestamps:  16 bytes
   user ID:     8 bytes
   Total:       ~232 bytes ≈ 250 bytes to be safe

 100M records × 250 bytes = 25 GB.
 That fits in a single large database node easily.

 For analytics — click events:
   10,000 clicks/sec × 50 bytes = 500 KB/sec
   500 KB/sec × 86,400 sec/day = ~43 GB/day
   Retain 90 days: 43 × 90 ≈ ~3.9 TB
   Need a separate analytics store for this."
```

This narration is the point. The interviewer is watching you think,
not checking your arithmetic.

---

## 5. Phase 3: High-Level Design — Draw the Boxes

Time budget: 10–15 minutes.
Output: a diagram with every major component named,
        every arrow labeled with a protocol.

### The canonical starting point

Every system design starts with this baseline. Add components as you justify them.

```
┌────────┐    HTTPS     ┌────────────────┐    HTTP     ┌─────────────┐
│ Client │─────────────▶│ Load Balancer  │────────────▶│ App Servers │
└────────┘              │ (L7, nginx)    │             │  (stateless)│
                        └────────────────┘             └──────┬──────┘
                                                              │
                                              ┌───────────────┼───────────────┐
                                              │               │               │
                                    ┌─────────▼──────┐ ┌─────▼──────┐ ┌──────▼─────┐
                                    │  Cache (Redis)  │ │  Database  │ │  Object    │
                                    │  (hot data)     │ │  (primary) │ │  Storage   │
                                    └────────────────┘  └────────────┘ └────────────┘
```

**Label every arrow.** This is not optional.

```
Arrows that must be labeled:
  Client → Load Balancer:  HTTPS / WebSocket / gRPC
  App → Cache:             Redis Protocol (TCP port 6379)
  App → Database:          SQL (TCP 5432) / DynamoDB API
  App → Queue:             Kafka Producer API
  Worker → Database:       SQL / NoSQL write
```

### How to add components

Do not add components speculatively. Add them when you justify them.

```
"Reads are 10:1 over writes. The database will be under read pressure.
 I'll add a Redis cache in front of the DB to absorb hot reads."
 → Add Redis to diagram.

"URL creation is bursty. I don't want creation spikes to affect redirects.
 I'll separate the write and read paths onto different app server pools."
 → Split App Servers into Read Servers + Write Servers.

"Analytics must not slow redirects.
 I'll put a Kafka queue between the redirect path and the analytics workers."
 → Add Kafka + Analytics Workers to diagram.
```

Every box you add must have a reason. Interviewers penalize unexplained boxes.

### The checklist before moving to deep dive

```
Before moving to Phase 4, verify:
  [ ] Client entry point is drawn
  [ ] Load balancer is present (if more than one server)
  [ ] App servers are labeled (stateless or stateful?)
  [ ] Primary database is chosen and named
  [ ] Cache layer is drawn (if reads are heavy)
  [ ] Every arrow has a protocol label
  [ ] Async paths (queues) are separated from sync paths
  [ ] "How does data get into the system?" is answered
  [ ] "How does a read request flow through?" is answered
```

---

## 6. Phase 4: Deep Dive — Go Deep on the Hardest Part

Time budget: 10–15 minutes.
Output: a detailed explanation of one component, with trade-offs named.

### The interviewer will guide you

After your high-level diagram, a good interviewer will say something like:
```
"Tell me more about the database choice."
"How would you handle the feed generation at scale?"
"Walk me through what happens when two users create the same custom alias simultaneously."
```

This is not a trap. It is a gift. They are telling you exactly what they want to see.

If they do not redirect you, pick the hardest component yourself:
```
"The part I find most interesting here is [X].
 Do you want me to go deep on that?"
```

### How to structure a deep dive

For any component, follow this pattern:
```
1. State what problem this component solves
2. Describe the naive approach and why it fails at scale
3. Describe your chosen approach
4. Walk through the data flow step by step
5. Name the trade-offs
```

Example — deep diving on "database choice for a URL shortener":
```
"The core access pattern is: given a short code, return a long URL.
 That is a pure key-value lookup — no joins, no aggregations, no complex queries.

 A naive approach is Postgres with an auto-increment primary key.
 The problem: at 10,000 reads/second with a 100ms SLA, a single
 Postgres instance starts degrading above ~5,000 reads/sec.
 We could add read replicas, but write contention on a single primary still exists.

 I'd choose DynamoDB here because:
 - Single-digit ms reads at any scale (provisioned throughput, no degradation)
 - Partition key on short_code = instant key lookups
 - TTL attribute = URL expiry is built-in, no cron job needed
 - Auto-scaling throughput handles traffic spikes

 The trade-off: DynamoDB has no relational queries.
 For the user table (user_id, email, plan) I'd still use Postgres —
 that data is relational and low-volume."
```

### Have opinions. Defend them.

The single biggest differentiator between junior and senior answers:
```
Junior: "We could use SQL or NoSQL, both have pros and cons..."
        (non-answer — no recommendation)

Senior: "I'd choose Cassandra here. Here's why:
         At 500M tweets/day, we need linear write scalability.
         Cassandra scales writes horizontally by adding nodes.
         The access pattern is always by user_id + tweet_id —
         a perfect fit for Cassandra's partition + cluster key model.
         The trade-off is no ad-hoc queries and eventual consistency,
         which is acceptable for a social feed."
```

Saying "it depends" is fine — if you follow it immediately with the conditions:
```
"It depends on the consistency requirement.
 If we need strong consistency (e.g., for payment records), I'd use Postgres.
 For a social feed where slight staleness is acceptable, Cassandra is better.
 In this case the interviewer said eventual consistency is OK, so: Cassandra."
```

---

## 7. Common Trade-off Templates

These are fill-in-the-blank answers for the most common design decisions.

### The fundamental trade-off statement
```
"I'm trading [X] for [Y] because at this scale [Z] is the bottleneck."

Examples:
  "I'm trading strong consistency for availability because
   at 580,000 reads/second, a quorum write would add 20ms of latency
   on every redirect — unacceptable. The stale feed is a better outcome
   than a slow feed."

  "I'm trading storage space for read latency by denormalizing the
   feed table. At 100:1 read-to-write ratio, expensive reads hurt
   far more than expensive writes."
```

### The alternative comparison
```
"The alternative would be [A], but that fails when [B]."

Examples:
  "The alternative to the hybrid push/pull model is pure push.
   That fails when a celebrity with 80M followers tweets —
   the fan-out job takes 13 minutes. Unacceptable."

  "The alternative to Redis for caching is a CDN.
   CDNs work for public content but not for personalized feeds.
   Your timeline is unique to you — it can't be CDN-cached."
```

### The migration path
```
"We could start with [M], and migrate to [N] once we hit [P] users."

Examples:
  "Start with a single Postgres instance. Add read replicas at 10K users.
   Migrate to Cassandra or DynamoDB at 1M users when write throughput
   exceeds what a single primary can handle."

  "Start with a monolith. Extract the Timeline Service as a microservice
   once it becomes the clear bottleneck at 100K DAU."
```

---

## 8. What Interviewers Actually Want

This is the section most candidates never read.

### Structured thinking beats perfect answers

```
A candidate who:
  - Asks clarifying questions
  - Estimates capacity before designing
  - Explains why each component exists
  - Names trade-offs proactively
  - Defends choices with reasoning

...will outperform a candidate who:
  - Jumps to the "right" architecture immediately
  - Uses buzzwords without explanation
  - Cannot explain why they chose Kafka over RabbitMQ
  - Gives a perfect diagram but cannot explain a single box
```

### Communication over correctness

The interviewer is simulating being your future colleague.
They want to know: is this person easy to work with on hard problems?

```
"I'm not sure exactly which approach is best here —
 let me think through the trade-offs out loud."
  → This is GOOD. Senior engineers do this.

"Uhh... I think we use Kafka?"
  → This is not. No reasoning, no confidence.

"I'd use Kafka here because this is a high-throughput,
 multi-consumer fan-out scenario where durability matters.
 RabbitMQ would also work but Kafka's log retention makes
 replaying events easier for the analytics use case."
  → This is what a senior engineer sounds like.
```

### "It depends" IS a great answer — with conditions

```
No context:   "It depends."            → Weak answer.
With context: "It depends on X.        → Strong answer.
               If X, then A because...
               If not X, then B because..."
```

### Asking clarifying questions signals seniority

Junior engineers fear looking dumb by asking questions.
Senior engineers know that designing without requirements is reckless.

```
"I want to ask about the consistency requirement before I choose a database.
 Is it acceptable for one user's write to be visible to another user
 after a short delay — say, a second or two?"

This question tells the interviewer:
  - You know consistency is a spectrum
  - You know database choice depends on it
  - You will not over-engineer for strong consistency when eventual is fine
  - You will not under-engineer and lose data when strong consistency is required
```

---

## 9. Common Mistakes

Knowing what not to do is as valuable as knowing what to do.

**Mistake 1: Over-engineering in Phase 3**
```
Do not design for 1 billion users in the high-level diagram
if requirements say 100,000 users.

Start simple:
  "For 100K users, a single Postgres instance with read replicas is fine.
   I'll note where we'd add sharding or move to Cassandra if scale grew."

Over-engineering early signals:
  - Cannot calibrate complexity to requirements
  - Will build systems nobody asked for
  - Does not think about cost
```

**Mistake 2: Skipping estimation entirely**
```
Estimation is not optional. It changes every architectural decision.

Without estimation:
  "We'll use Redis for caching."

With estimation:
  "We have 100M active URLs at ~250 bytes each.
   Top 20% are hot (Pareto) = 20M × 300 bytes = 6 GB.
   A single Redis r6g.xlarge (32 GB) handles this comfortably.
   We don't need Redis Cluster until we exceed 25 GB of hot data."

The second answer demonstrates engineering judgment.
```

**Mistake 3: Not asking questions**
```
If the first words out of your mouth are a technology name,
you have already signaled that you design without requirements.
Ask at least three clarifying questions before touching the whiteboard.
```

**Mistake 4: Too much detail too early**
```
Phase 3 is boxes and arrows. Not schemas.
Do not design table columns in Phase 3.
Do not discuss index strategies in Phase 3.
That is Phase 4 work.

Moving to schema design before the interviewer can see the full picture
often means you never produce a complete architecture.
```

**Mistake 5: Ignoring the non-functional requirements**
```
"Our system needs to be fast and reliable."
    → Not requirements. Every system needs that.

"Our system needs sub-100ms p99 latency for redirects,
 99.99% availability, and can tolerate eventual consistency
 on analytics with up to 5 seconds of lag."
    → These are requirements. They drive architecture.
```

**Mistake 6: Not timeboxing yourself**
```
Spending 30 minutes on requirements leaves 15 minutes for everything else.
Spending 25 minutes on the high-level design leaves no time for deep dive.

The interviewer wants to see all five phases.
If you are running over on a phase, say it:
  "I could go deeper on the fan-out algorithm —
   should I do that now or should I keep moving to the deep dive?"
This gives the interviewer control and demonstrates time awareness.
```

---

## 10. A Sample 45-Minute Session — URL Shortener

This is what the framework looks like in practice, narrated in real time.

### Minute 0-6: Requirements

```
"Before I start designing, I'd like to ask a few questions.

 Functional: The core feature is — shorten a URL, get a redirect?
 And we want analytics on how many clicks each link gets?

 Scale: How many URLs are we storing? How many redirects per day?
 [Interviewer: 100M URLs, 10:1 read-to-write ratio]

 Latency: The redirect must be fast — under 100ms?
 [Interviewer: Yes, users should not notice the hop]

 Availability: 99.99%? I'm assuming downtime is very visible on a shortener.
 [Interviewer: Yes, aim for very high availability]

 Custom aliases: Can users pick their own short codes?
 Expiry: Do URLs expire?
 [Interviewer: Yes to both]

 OK. So I'm designing a system that:
  - Stores 100M URLs with optional custom aliases and TTL
  - Handles 10,000 redirects/second and 1,000 URL creations/second
  - Redirects in under 100ms p99
  - Tracks click analytics asynchronously
  Does that sound right?
 [Interviewer: Yes, let's go.]"
```

### Minute 6-11: Estimation

```
"Quick math:
 100M URLs × 250 bytes = 25 GB for URL storage — fits comfortably in DB.
 Redirects: 10,000/sec. Analytics: 10,000 events/sec × 50 bytes = 500 KB/sec.
 90 days of analytics = ~3.9 TB. Needs a separate analytics store.
 Cache: top 20% of URLs = 20M × 300 bytes = 6 GB Redis — single node works."
```

### Minute 11-24: High-Level Design

```
[Drawing the diagram]
"Client hits API Gateway for rate limiting and auth.
 Redirects go to App Servers. App Servers check Redis cache first.
 Cache miss → query DynamoDB. Return 302.
 Async: emit click event to Kafka → Analytics Workers → ClickHouse.
 URL creation: App Server validates, generates random 7-char base62 code,
               inserts to DynamoDB with TTL attribute.

 [Diagram is now on the board — cache, DynamoDB, Kafka, analytics are drawn]

 Any part you'd like me to focus on?"
```

### Minute 24-38: Deep Dive (interviewer picks short code generation)

```
"Three options for generating short codes:

 Option 1: MD5 hash. Hash the long URL, take first 6 bytes, base62-encode.
 Problem: same URL always gets same code (breaks our 'no dedup' requirement).
          And truncation causes collisions between different URLs.

 Option 2: Auto-increment counter. ID 1 → 'b', ID 2 → 'c', etc.
 Problem: sequential — enumerable by attackers who can crawl all URLs.
          Distributed generation is complex (who owns the counter?).

 Option 3: Random 7-character base62. 62^7 = 3.5 trillion possible codes.
 At 100M stored: collision probability = 100M / 3.5T ≈ 0.003%.
 On collision: retry — expected retries per creation ≈ 0.003. Negligible.

 I'd go with Option 3. Non-enumerable, trivially distributed, simple retry logic."
```

### Minute 38-43: Trade-offs

```
"A few trade-offs I made:
 302 over 301: 302 costs more server load but enables full analytics.
               The load is mitigated by the Redis cache.

 DynamoDB over Postgres: pure key-value access pattern, need horizontal scale.
                          User table stays in Postgres — it is relational and tiny.

 Async analytics: click events go to Kafka, not written synchronously.
                  Redirect latency stays under 5ms. Analytics lag is ~5 seconds.
                  That is an acceptable trade-off for a click-tracking feature.

 Any trade-off you'd like to challenge?"
```

### Minute 43-45: Buffer

Wrap up, check for questions, be done on time.

---

## Navigation

| | |
|---|---|
| Previous | [22 — Case Studies](../22_case_studies/url_shortener.md) |
| Next | [99 — Interview Master](../99_interview_master/) |
| Home | [README.md](../README.md) |
