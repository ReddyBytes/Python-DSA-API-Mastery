<a id="top"></a>

# Interview Framework — System Design in 45 Minutes

> A repeatable 45-minute structure for tackling any system design problem confidently and systematically. The difference between a hire and a no-hire is not knowledge — it is how you communicate, structure your thinking, and navigate trade-offs under time pressure.

*Arun is a Telugu interviewer who has coached over 200 candidates through system design rounds. His observation: "The best engineers sometimes fail interviews because they have no framework. They jump to databases before understanding requirements. They draw boxes without explaining why. They run out of time before discussing trade-offs. A framework does not make you smarter — it makes sure your intelligence shows up in the room."*

## 📖 Table of Contents

- [1. The RESHADED Framework](#1-the-reshaded-framework)
  - [RESHADED Walkthrough](#reshaded-walkthrough)
- [2. Structuring the 45-Minute Interview](#2-structuring-the-45-minute-interview)
  - [Phase 1 — Requirements (5 minutes)](#phase-1-requirements-5-minutes)
  - [Phase 2 — Estimation (5 minutes)](#phase-2-estimation-5-minutes)
  - [Phase 3 — High-Level Design (15 minutes)](#phase-3-high-level-design-15-minutes)
  - [Phase 4 — Deep Dive (15 minutes)](#phase-4-deep-dive-15-minutes)
  - [Phase 5 — Trade-offs and Wrap-up (5 minutes)](#phase-5-trade-offs-and-wrap-up-5-minutes)
- [3. Capacity Estimation Approach](#3-capacity-estimation-approach)
  - [Useful Numbers to Memorize](#useful-numbers-to-memorize)
- [4. Drawing Diagrams Effectively](#4-drawing-diagrams-effectively)
- [5. Communicating Trade-offs](#5-communicating-trade-offs)
- [6. Common Mistakes Candidates Make](#6-common-mistakes-candidates-make)
- [7. The Signal Interviewers Look For](#7-the-signal-interviewers-look-for)
- [Summary](#summary)

## Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
structured interview approach (requirements, estimation, design, trade-offs), time allocation per phase, clarifying questions

**Should Learn** — Important for real projects, comes up regularly:
trade-off articulation, common mistakes to avoid, candidate communication style

**Good to Know** — Useful in specific situations, not always tested:
how to handle unknown requirements, drawing diagrams effectively

**Reference** — Know it exists, look up syntax when needed:
RESHADED framework, preparation checklist, post-design Q&A patterns

<a id="1-the-reshaded-framework"></a>

# 1. The RESHADED Framework

"RESHADED is the mnemonic I teach every candidate," Arun says. "It covers the eight dimensions every system design must address. Think of it like a pilot's pre-flight checklist — you do not skip steps even if you have flown a thousand times. Missing one dimension in an interview is like a pilot forgetting to check fuel."

```
R — Requirements
    What does the system need to do? (functional)
    How well does it need to do it? (non-functional: latency, availability, consistency)

E — Estimation
    How many users? How many requests per second?
    How much storage? How much bandwidth?
    These numbers DRIVE your architecture decisions.

S — Storage
    What type of database? SQL vs NoSQL?
    How is data modeled? How is it partitioned?
    What is the access pattern?

H — High-Level Design
    The 10,000-foot view: boxes and arrows.
    Clients, load balancers, services, caches, databases, queues.
    Show the primary data flow.

A — API Design
    What endpoints exist?
    REST, GraphQL, gRPC, or WebSocket?
    What do requests and responses look like?

D — Detailed Design
    Zoom into the hardest component.
    How does the cache invalidation work?
    How does sharding distribute data?
    How does the fan-out service scale?

E — Evaluation (Trade-offs)
    What are the trade-offs of each decision?
    What would change at 10x or 100x scale?
    What would you do differently with unlimited budget?

D — Distinctive Features
    Edge cases, failure modes, monitoring.
    Rate limiting, abuse prevention, deployment strategy.
    What makes this production-ready vs whiteboard-only?
```

<a id="reshaded-walkthrough"></a>

## RESHADED Walkthrough

"Let me show you how RESHADED maps to interview time," Arun demonstrates with a URL shortener example.

```
R (Requirements) — 3 min:
  "Let me clarify: we need to shorten URLs and redirect them.
   Read-heavy (100:1). We need analytics. Global users.
   99.9% availability. Redirect latency < 100ms."

E (Estimation) — 3 min:
  "100M DAU. 500M reads/day = 6K QPS, peak 18K.
   5M writes/day = 60 QPS. Storage: 1 GB/day, 365 GB/year.
   Reads dominate — cache will be critical."

S (Storage) — 3 min:
  "Key-value store for the mapping: short_code --> original_url.
   PostgreSQL for durability, Redis for caching reads.
   Partition by short_code prefix if needed later."

H (High-Level Design) — 8 min:
  [Draw the architecture: clients --> LB --> API --> Redis --> DB]
  "Here's the create flow. Here's the redirect flow."

A (API Design) — 3 min:
  "POST /shorten {url: string} --> {short_url: string}
   GET /{code} --> 302 redirect to original URL"

D (Detailed Design) — 10 min:
  "Let's dive into the ID generation strategy..."
  "Let's discuss cache invalidation..."

E (Evaluation) — 5 min:
  "Trade-off: 301 vs 302 redirect. 301 is cached by browsers
   (less load on us) but we lose analytics visibility."

D (Distinctive) — 3 min:
  "Rate limiting on creation. Abuse detection for phishing URLs.
   Monitoring: cache hit ratio, redirect latency p99."
```

> [↑ Back to Top](#top)

<a id="2-structuring-the-45-minute-interview"></a>

# 2. Structuring the 45-Minute Interview

"Time management is the most underrated skill in system design interviews," Arun says. "I have seen brilliant engineers fail because they spent 30 minutes on requirements and estimation, leaving 15 minutes for the actual design. Or worse — they jumped straight to databases without asking a single question."

```
The 45-minute breakdown:

  Minutes 0-5:    Requirements + Estimation
  Minutes 5-20:   High-Level Design + API Design
  Minutes 20-35:  Deep Dive (interviewer-guided)
  Minutes 35-40:  Trade-offs + Scaling
  Minutes 40-45:  Wrap-up + Questions

  Visual timeline:
  |--- R+E ---|-------- H+A --------|-------- D --------|-- E+D --|
  0           5                     20                  35       45

  The interviewer will steer — if they want more depth in one area,
  adapt. But this default allocation ensures you cover everything.
```

<a id="phase-1-requirements-5-minutes"></a>

## Phase 1 — Requirements (5 minutes)

```
Functional requirements (what it does):
  "What are the core features? Let me list them."
  "Can users do X?" / "Do we need Y?"
  "Who are the users — end users? internal teams? both?"

Non-functional requirements (how well it does it):
  "What scale are we targeting? DAU?"
  "What latency is acceptable?"
  "Availability target? 99.9%? 99.99%?"
  "Consistency requirements? Is eventual consistency OK?"
  "Geographic distribution?"

Arun's tip:
  "Write requirements on the board as you discuss them.
   Reference them when making decisions later:
   'We said read-heavy, so I'll add a cache here.'"

Questions to ALWAYS ask:
  - "Is this read-heavy or write-heavy?"
  - "What is the expected user scale?"
  - "Do we need real-time or near-real-time?"
  - "Are there geographic distribution requirements?"
  - "What is the consistency model — strong or eventual?"
```

<a id="phase-2-estimation-5-minutes"></a>

## Phase 2 — Estimation (5 minutes)

```
The estimation chain:
  Users --> DAU --> Requests/day --> QPS --> Peak QPS
  --> Storage/day --> Storage/year --> Bandwidth

Show your work:
  "Let's assume 100M DAU."
  "Each user makes 10 reads/day: 100M * 10 / 86400 = ~12K QPS"
  "Peak is 3x average: ~36K QPS"
  "Each record is 1KB. 1M new records/day = 1GB/day, 365GB/year"

The estimation MUST lead to architecture decisions:
  WRONG: "We have 12K QPS." (number with no action)
  RIGHT: "12K QPS peak is within a single Postgres's capacity,
          but with peak at 36K, we'll need a read replica or cache."

  WRONG: "Storage is 365GB/year." (number with no action)
  RIGHT: "365GB/year fits on one machine for years. No sharding needed
          for storage — but we may shard for QPS distribution."
```

<a id="phase-3-high-level-design-15-minutes"></a>

## Phase 3 — High-Level Design (15 minutes)

```
Draw the boxes:
  1. Start with the client (mobile app, web browser)
  2. Add a load balancer
  3. Add the main service(s)
  4. Add the database(s)
  5. Add cache if read-heavy
  6. Add message queue if async processing needed
  7. Add CDN if serving static/media content

Walk through the primary flows:
  "Here's the write path: client --> LB --> write service --> DB"
  "Here's the read path: client --> LB --> read service --> cache --> DB (miss)"

Arun's structure for the walkthrough:
  1. Draw the diagram
  2. Walk through the WRITE path first (simpler usually)
  3. Walk through the READ path
  4. Explain each component's purpose in one sentence
  5. Invite the interviewer: "Should I dive deeper into any component?"
```

<a id="phase-4-deep-dive-15-minutes"></a>

## Phase 4 — Deep Dive (15 minutes)

```
The interviewer will usually pick the hardest component and ask you to go deeper.
Common deep dive topics:

  Database design:
    "How would you model the data?"
    "What's the partition key? Why?"
    "How do you handle hot partitions?"

  Caching strategy:
    "When does the cache get invalidated?"
    "What happens on a cache miss?"
    "How do you prevent thundering herd?"

  Scaling:
    "This service handles 100K QPS. How?"
    "What if we need to scale to 10x?"
    "What's the bottleneck?"

  Consistency:
    "What happens if the cache and DB disagree?"
    "How do you handle concurrent writes?"
    "What's your consistency guarantee?"

Arun's deep dive structure:
  1. State the problem clearly
  2. Present 2-3 options
  3. Analyze trade-offs of each
  4. Choose one and justify WHY
  5. Explain the implementation detail
```

<a id="phase-5-trade-offs-and-wrap-up-5-minutes"></a>

## Phase 5 — Trade-offs and Wrap-up (5 minutes)

```
Proactively discuss:
  "The main trade-offs in my design are..."
  "If I had more time, I would add..."
  "At 100x scale, I would change..."
  "The biggest risk in this design is..."

Show awareness of production concerns:
  Monitoring: "I'd track cache hit ratio, p99 latency, error rate"
  Deployment: "Blue-green deploy, canary rollout for new features"
  Failure modes: "If Redis goes down, we fall back to DB (degraded, not dead)"
  Security: "Rate limiting on writes, input validation, auth on all APIs"
```

> [↑ Back to Top](#top)

<a id="3-capacity-estimation-approach"></a>

# 3. Capacity Estimation Approach

"Estimation is not about getting the exact number," Arun emphasizes. "It is about getting the right ORDER OF MAGNITUDE and using that number to make an architecture decision. If you estimate 500 QPS, you know one database is fine. If you estimate 500K QPS, you know you need sharding. The exact number between those does not matter — the architectural implication does."

```
Step-by-step estimation process:

  1. Start with users:
     Total registered users: X
     Daily active users (DAU): usually 10-30% of total
     Concurrent users (peak): usually 10% of DAU

  2. Derive QPS:
     Requests per user per day: varies by feature
     Read QPS = DAU * reads_per_user / 86400
     Write QPS = DAU * writes_per_user / 86400
     Peak QPS = Average QPS * 3 (typical peak factor)

  3. Derive storage:
     Size per record: estimate in bytes
     New records per day: from write QPS * 86400
     Storage per year: records/day * 365 * size

  4. Derive bandwidth:
     Incoming: write QPS * avg request size
     Outgoing: read QPS * avg response size

  5. Make architecture decisions from numbers:
     QPS < 5K? Single DB is fine.
     QPS 5K-50K? Add read replicas or cache.
     QPS > 50K? Need sharding or distributed cache.
     Storage < 1TB? Single machine.
     Storage > 10TB? Need sharding strategy.
```

<a id="useful-numbers-to-memorize"></a>

## Useful Numbers to Memorize

```
QPS capacity of a single machine:
  PostgreSQL:    5K-10K simple queries/sec
  MySQL:         5K-10K simple queries/sec
  Redis:         100K-500K ops/sec
  Memcached:     100K-1M ops/sec
  Nginx:         50K-100K concurrent connections
  Single web server: 1K-10K requests/sec (depends on logic complexity)

Storage rough sizes:
  1 tweet (280 chars + metadata):    ~1 KB
  1 URL mapping:                     ~100 bytes
  1 chat message:                    ~200 bytes
  1 user profile:                    ~1 KB
  1 photo (compressed):              ~200 KB
  1 minute of video (720p):          ~5 MB
  1 minute of audio:                 ~1 MB

Time units for estimation:
  1 day    = 86,400 seconds  (~100K for quick math)
  1 month  = 2.6M seconds   (~3M for quick math)
  1 year   = 31.5M seconds  (~30M for quick math)

Network latency:
  Same data center:    < 1ms
  Same region:         1-5ms
  Cross-continent:     50-150ms
  User to nearest CDN: 10-50ms

Data transfer:
  1 Gbps network: ~100 MB/sec
  S3 read: 1-5 Gbps per request
  SSD read: 500 MB/sec
  HDD read: 100 MB/sec
```

> [↑ Back to Top](#top)

<a id="4-drawing-diagrams-effectively"></a>

# 4. Drawing Diagrams Effectively

"Your diagram is not a work of art," Arun says. "It is a communication tool. A messy diagram that clearly shows data flow beats a beautiful diagram that confuses the interviewer. Label every arrow. Name every box. Show the direction of data."

```
Diagram rules:

  1. LEFT TO RIGHT flow (or TOP TO BOTTOM)
     Client on the left, database on the right.
     Data flows left to right for the happy path.

  2. LABEL EVERY ARROW
     Not just lines between boxes — what travels on that line?
     "HTTP request", "SQL query", "WebSocket push", "Kafka event"

  3. NAME EVERY BOX
     Not "Service" — which service? "URL Shortener API", "Cache (Redis)"
     Include the technology in parentheses.

  4. SHOW BOTH READ AND WRITE PATHS
     Different colors or separate diagrams.
     Read path often skips the write-heavy components.

  5. SHOW NUMBERS ON CRITICAL PATHS
     "6K QPS" on the arrow to the cache.
     "60 QPS" on the arrow to the database.
     Proves you've done the estimation work.

Example structure:

  [Client] --HTTP--> [Load Balancer] --HTTP--> [API Service]
                                                    |
                                         +----------+----------+
                                         |                     |
                                    [Redis Cache]        [PostgreSQL]
                                    (100K ops/sec)       (5K QPS)
                                         |                     |
                                    cache hit (80%)      cache miss (20%)

  [API Service] --Kafka--> [Analytics Worker] --> [ClickHouse]
```

```
Common diagram mistakes:

  WRONG: One massive box labeled "Backend"
  RIGHT: Separate boxes for each service with clear responsibilities

  WRONG: Arrows with no labels
  RIGHT: Every arrow labeled with protocol and data type

  WRONG: No indication of scale/QPS
  RIGHT: Numbers on critical paths showing load distribution

  WRONG: Only showing the happy path
  RIGHT: Also showing failure modes ("if cache miss, fall through to DB")
```

> [↑ Back to Top](#top)

<a id="5-communicating-trade-offs"></a>

# 5. Communicating Trade-offs

"The single biggest differentiator between junior and senior candidates," Arun says, "is trade-off communication. Junior candidates say 'I'll use Redis.' Senior candidates say 'I'll use Redis because our read:write ratio is 100:1 and we need sub-10ms p99 latency. The trade-off is that cached data can be stale for up to 30 seconds, which is acceptable for our use case.' Same decision — completely different signal to the interviewer."

```
The trade-off formula:
  "I chose [option A] because [reason tied to requirements].
   The trade-off is [what we give up].
   This is acceptable because [why it doesn't violate our requirements]."

Examples:

  Caching:
    "I'm caching with a 30-second TTL. We get sub-10ms reads for 80% of traffic.
     The trade-off: users might see stale data for up to 30 seconds.
     Acceptable because our product doesn't require real-time consistency for reads."

  Eventual consistency:
    "Using async replication to read replicas gives us 3x read throughput.
     Trade-off: reads might be 1-2 seconds behind writes.
     Acceptable because a user who just posted can read from primary (read-your-writes)."

  Sharding:
    "Sharding by user_id distributes writes evenly.
     Trade-off: cross-user queries (e.g., 'all orders this hour') require scatter-gather.
     Acceptable because our primary access pattern is single-user."

  Async processing:
    "Sending emails asynchronously via a queue decouples the write path.
     Trade-off: email arrives 5-30 seconds after the action, not instantly.
     Acceptable because users don't expect instant email delivery."
```

```
Trade-offs the interviewer expects you to know:

  Decision                Give up                     Gain
  ─────────────────────   ──────────────────────────  ────────────────────
  Cache                   Freshness (stale data)      Speed (sub-ms reads)
  Eventual consistency    Instant accuracy            Availability + scale
  Sharding                Cross-shard queries         Write throughput
  Async (queues)          Immediate confirmation      Decoupling + resilience
  Denormalization         Storage, update complexity   Read speed
  Microservices           Operational complexity       Independent scaling
  CDN                     Cache invalidation lag       Global latency reduction
  NoSQL                   Complex queries, JOINs      Write throughput, flexibility
```

> [↑ Back to Top](#top)

<a id="6-common-mistakes-candidates-make"></a>

# 6. Common Mistakes Candidates Make

"I have interviewed 500+ candidates," Arun says. "These are the patterns that lead to rejection — and they are all fixable with awareness."

```
Mistake 1: JUMPING TO SOLUTIONS WITHOUT REQUIREMENTS
  "I'll use Kafka and Redis and..."
  The interviewer hasn't even told you the problem yet.
  FIX: Always start with 3-5 clarifying questions.

Mistake 2: NO ESTIMATION
  You design a system with no sense of scale.
  "Let me add a load balancer." Why? How much traffic?
  FIX: Estimate QPS, storage, bandwidth BEFORE designing.

Mistake 3: ONE-SIZE-FITS-ALL ARCHITECTURE
  "I'll use microservices." For a URL shortener with 100 QPS? Over-engineering.
  FIX: Match complexity of architecture to complexity of problem.

Mistake 4: NO TRADE-OFF DISCUSSION
  "I'll cache this." OK, what's the staleness guarantee?
  Every decision has a cost. State it explicitly.
  FIX: For every component, say what you gain AND what you lose.

Mistake 5: GOING TOO DEEP TOO EARLY
  Spending 15 minutes on database schema before showing the high-level flow.
  The interviewer can't evaluate the system if they don't see the full picture.
  FIX: Breadth first, then depth on the interviewer's chosen area.

Mistake 6: NOT COMMUNICATING THOUGHT PROCESS
  Silent thinking for 2 minutes, then drawing a complete diagram.
  The interviewer cannot evaluate your thinking if you don't share it.
  FIX: Think out loud. "I'm considering X vs Y because..."

Mistake 7: IGNORING THE INTERVIEWER'S HINTS
  Interviewer: "What happens if this component fails?"
  Candidate: continues talking about a different component.
  FIX: Treat every question as a redirect signal. Answer it.

Mistake 8: PERFECTIONISM
  Trying to design the perfect system instead of a good enough one.
  FIX: "Here's the 80% solution. Given more time, I'd improve X."
```

```
Junior vs Senior signals:

  Junior signal                      Senior signal
  ────────────────────────────────   ────────────────────────────────
  "I'll use Redis"                   "I'll cache with 30s TTL because..."
  Draws boxes without explanation    Explains why each box exists
  One solution, no alternatives      "Option A vs B, I'd choose A because..."
  Ignores failure modes              "If X fails, we degrade to Y"
  No numbers                         "At 50K QPS, we need to shard"
  Silence while thinking             "I'm thinking about whether to..."
  Over-engineers simple problems     Right-sizes architecture to requirements
```

> [↑ Back to Top](#top)

<a id="7-the-signal-interviewers-look-for"></a>

# 7. The Signal Interviewers Look For

"When I evaluate a candidate," Arun shares, "I am looking for five things. You can have gaps in knowledge — that is fine. But these five signals must be present."

```
Signal 1: STRUCTURED THINKING
  Can the candidate break an ambiguous problem into clear phases?
  Do they follow a logical sequence (requirements --> estimation --> design)?
  Or do they jump randomly between topics?

Signal 2: TRADE-OFF AWARENESS
  Does the candidate acknowledge that every decision has a cost?
  Can they articulate what they gain and what they lose?
  Do they tie decisions back to requirements?

Signal 3: SCALE AWARENESS
  Does the candidate's design handle the stated scale?
  Do they know what breaks at 10x? At 100x?
  Can they explain WHY a component exists (not just WHAT it is)?

Signal 4: COMMUNICATION
  Can the candidate explain their thinking clearly?
  Do they draw diagrams that the interviewer can follow?
  Do they respond to questions and hints appropriately?

Signal 5: DEPTH IN AT LEAST ONE AREA
  When asked to go deep, can the candidate show mastery?
  Not surface-level "use Redis" but deep "here's how cache invalidation works,
  here's the thundering herd problem, here's how we prevent it."
```

```
The grading rubric (most companies use something like this):

  Strong Hire:
    - Clear structure throughout
    - Estimation that drives decisions
    - Trade-offs articulated for every choice
    - Deep dive shows real expertise
    - Adapts when interviewer changes requirements

  Hire:
    - Reasonable structure
    - Some estimation
    - Acknowledges trade-offs when prompted
    - Adequate depth in one area
    - Mostly responds to interviewer guidance

  No Hire:
    - No structure (jumps between topics)
    - No estimation (designs without scale awareness)
    - Single solution with no alternatives discussed
    - Cannot go deep in any area
    - Ignores interviewer's questions/hints
```

> [↑ Back to Top](#top)

<a id="summary"></a>

## 🔥 Summary

```
The 45-Minute System Design Interview:

  Phase            Time      What to Do
  ──────────────   ────────  ──────────────────────────────────────────
  Requirements     0-5 min   Clarify scope, ask questions, write them down
  Estimation       5 min     Derive QPS/storage/bandwidth, make decisions
  High-Level       5-20 min  Draw architecture, walk through flows
  Deep Dive        20-35 min Go deep on interviewer's chosen component
  Trade-offs       35-45 min Discuss alternatives, scaling, production concerns

RESHADED Framework:
  R-Requirements, E-Estimation, S-Storage, H-High-Level,
  A-API Design, D-Detailed Design, E-Evaluation, D-Distinctive

Arun's top rules:
  1. ALWAYS start with requirements — never jump to architecture
  2. Estimation must lead to decisions, not just numbers
  3. Breadth first (show the full picture), then depth (dive into one area)
  4. Every decision needs a trade-off statement
  5. Think out loud — silent design is invisible design
  6. Right-size your architecture — simple problems need simple solutions
  7. Answer the interviewer's questions — they are steering you toward signal
```

## 📂 Navigation

| | |
|---|---|
| 📘 README | [Back to System Design README](../README.md) |

| ⬅ Previous | ➡ Next |
|---|---|
| [22 — Case Studies](../22_case_studies/theory.md) | None (last module) |

**This folder:** [theory.md](./theory.md) | [cheetsheet.md](./cheetsheet.md) | [interview.md](./interview.md) | [practice_local.py](./practice_local.py) | [the_45_minute_playbook.md](./the_45_minute_playbook.md)

**Related modules:** [22 — Case Studies](../22_case_studies/theory.md) | [16 — High Level Design](../16_high_level_design/theory.md) | [02 — System Fundamentals](../02_system_fundamentals/theory.md) | [99 — Interview Master](../99_interview_master/)

**Jump to topics:** [RESHADED Framework](#1-the-reshaded-framework) | [Time Breakdown](#2-structuring-the-45-minute-interview) | [Capacity Estimation](#3-capacity-estimation-approach) | [Common Mistakes](#6-common-mistakes-candidates-make)
