# Company Patterns — What Each Company Focuses On
> Understanding what each company cares about lets you prepare specifically, not generically.
> This is not about memorizing their tech stack — it is about understanding what problems they live with at scale
> and why those problems show up in their interviews.

---

## Contents

```
1.  FAANG and Big Tech
    - Google
    - Amazon
    - Meta
    - Apple
    - Microsoft
2.  Mid-Size Tech
    - Uber
    - Airbnb
    - Stripe
    - Twilio
3.  Patterns That Appear Everywhere
4.  Red Flags Interviewers Watch For
5.  Vocabulary That Signals Senior-Level Thinking
```

---

## 1. FAANG and Big Tech

### Google

Google's interview culture is heavily influenced by the fact that Google built foundational distributed systems infrastructure — Bigtable, Spanner, MapReduce, Borg, Chubby — and published papers that shaped the entire field. Interviewers are often engineers who work on these systems or use them daily. Generic answers land poorly; what reads as sophisticated at other companies may seem shallow at Google.

**What they emphasize**:
- Scalability at genuinely massive scale. Google's systems serve hundreds of millions of requests per second. They care whether you understand the difference between designing for 100K QPS and 10M QPS — not just theoretically, but in terms of which components fail first and how the design changes.
- Data modeling and storage choices. Google has a strong culture around choosing the right storage abstraction. Expect to discuss key-value vs. column-family vs. relational vs. document storage and the specific trade-offs at their scale.
- Consistency models in depth. Given Spanner and Chubby, they care about the spectrum from serializability to causal consistency to eventual consistency. Know what each model guarantees and when each is the appropriate choice.
- System reliability and SRE thinking. Google invented Site Reliability Engineering. They care about error budgets, SLOs, designing for graceful degradation, and distinguishing between availability requirements.
- Back-of-the-envelope estimation. Google interviewers take capacity estimation seriously. Weak or absent estimation is a clear negative signal.

**Example questions they have asked publicly**:
- Design Google Search (search indexing and serving at web scale)
- Design Google Maps (geospatial indexing, routing, real-time traffic)
- Design YouTube (video storage, transcoding pipelines, recommendation serving)
- Design a distributed caching system (Memcache-style)
- Design a key-value store with strong consistency guarantees

**Keywords that signal you know their domain**:
Bigtable, Spanner, Chubby, Paxos, Borg, consistent hashing, write-ahead log, vector clocks, hybrid logical clocks, linearizability, external consistency, GFS, MapReduce, Dremel. When discussing distributed consensus, know Paxos and Raft — do not just say "use ZooKeeper" without understanding what it provides.

---

### Amazon

Amazon's interview philosophy is shaped by the Leadership Principles. In system design, this means interviewers are not just evaluating your technical answer — they are evaluating whether your approach reflects ownership, customer obsession, and operational thinking. Amazon runs e-commerce infrastructure that must survive Black Friday (a 5–10× traffic spike that is known weeks in advance) and Prime Day. They care about systems that fail gracefully and can be operated reliably.

AWS is also Amazon's largest business. If you are interviewing for an AWS service team, you are expected to understand cloud-native patterns and the services you would be using or competing with.

**What they emphasize**:
- Availability and resilience above all. Amazon's canonical stance is that availability is more important than consistency for most consumer-facing workloads. The Dynamo paper (2007) emerged directly from this philosophy. Know the Dynamo paper.
- Operational simplicity and runbooks. Amazon's services are operated by the teams that build them. Designs that are clever but operationally complex are viewed skeptically. Interviewers will ask how you would debug your system at 2am when it is misbehaving.
- Service-oriented architecture (SOA) is deeply embedded in Amazon's culture — Jeff Bezos's "API mandate" famously required all teams to expose their functionality through service interfaces. Expect to discuss service boundaries, API contracts, and how services communicate.
- Cost consciousness. Amazon engineers are expected to think about operational cost. A design that requires 10× the hardware to handle a workload that could be solved with better data structures is a negative signal.
- Failure modes and blast radius. "What happens when X fails?" is a standard Amazon follow-up question. They want to see that you have thought through failure modes and designed for partial failure rather than assuming the happy path.

**Example questions they have asked publicly**:
- Design Amazon's product catalog (read-heavy, high availability required)
- Design a flash sale system (massive write spike, inventory accuracy required)
- Design Amazon's recommendation engine
- Design a distributed order management system
- Design S3 (object storage at scale)

**Keywords that signal you know their domain**:
Dynamo, consistent hashing, quorum reads/writes, sloppy quorum, vector clocks, eventual consistency, availability over consistency, service-oriented architecture, dead letter queue, idempotency keys, two-phase commit, saga pattern, circuit breaker, bulkhead, blue/green deployment, canary release, rollback strategy.

---

### Meta

Meta's scale is defined by social graph problems. The social graph — who follows whom, who is friends with whom, how information propagates through social networks — is at the core of almost every Meta product. Their engineering challenges are characterized by extremely high fan-out (a celebrity with 100M followers posting something), graph traversal at scale, and real-time feed generation.

Meta also has a culture of moving fast. They pioneered PHP performance engineering (HHVM), built Cassandra (open-sourced from their inbox search work), and built RocksDB. They are comfortable with complexity if it enables product velocity.

**What they emphasize**:
- Social graph traversal and storage. The news feed, notifications, and friend recommendations all depend on efficiently traversing a massive, constantly-changing graph. Understand TAO (their graph data store) conceptually, or at minimum, know why a relational database is the wrong choice for social graph queries at this scale.
- News feed design. This is one of Meta's classic system design problems. The push vs. pull vs. hybrid fan-out model, how to handle celebrities with large followings differently from regular users, and how to rank feed items are all expected topics.
- Real-time systems. Meta's notifications, messaging (WhatsApp, Messenger), and live reaction counts are real-time at enormous scale. WebSockets, long-polling, and pub/sub infrastructure are relevant topics.
- Data consistency trade-offs in social contexts. For most social features, eventual consistency is acceptable — a like count being one stale for a second is unimportant. Meta's culture values correctly identifying when strong consistency matters (payments, account security) vs. when it does not (social feeds, reaction counts).
- Scale numbers. Meta has ~3 billion monthly active users. They care whether your design accounts for genuine internet scale — designs that break at 10M users are not relevant.

**Example questions they have asked publicly**:
- Design the Facebook News Feed
- Design Facebook Messenger (real-time chat at scale)
- Design Facebook's notification system
- Design a social graph service
- Design Instagram's photo storage and serving

**Keywords that signal you know their domain**:
TAO, social graph, fan-out on write, fan-out on read, hybrid push/pull, news feed ranking, Cassandra, RocksDB, Thrift, ZooKeeper, memcached, EdgeRank (historical), pub/sub fan-out, message store vs. notification service, read-heavy workloads, cache-aside.

---

### Apple

Apple's system design interviews tend to focus on backend infrastructure that supports its consumer hardware ecosystem — iCloud, App Store, Apple Pay, push notifications (APNs), and media services. Apple has unusual privacy requirements compared to other FAANG companies — their on-device processing and differential privacy commitments mean systems that centralize sensitive user data are viewed skeptically, even internally.

**What they emphasize**:
- Privacy and security by design. Apple's brand is built on privacy. System designs that unnecessarily centralize or retain user data raise concerns in Apple interviews. Be prepared to discuss encryption at rest, end-to-end encryption (especially relevant for iMessage), minimal data retention, and data minimization.
- High-availability consumer services. APNs delivers billions of push notifications per day. iCloud syncs data across devices in near real-time for 1 billion+ devices. Reliability engineering at Apple's scale of consumer hardware is a core competency.
- Conflict-free data synchronization. iCloud sync — syncing contacts, notes, photos across multiple devices with intermittent connectivity — is fundamentally a distributed systems problem. CRDT (Conflict-free Replicated Data Types) or last-write-wins semantics for different data types are directly relevant.
- Large-scale content distribution. App Store distributes apps globally; Apple Music distributes audio. CDN architecture, content replication, and efficient binary distribution are relevant.

**Example questions they have asked publicly**:
- Design iCloud sync (cross-device data synchronization with offline support)
- Design a push notification system at Apple's scale (APNs)
- Design the App Store (search, download, update distribution)
- Design a secure messaging system (end-to-end encrypted, like iMessage)

**Keywords that signal you know their domain**:
End-to-end encryption, CRDT (conflict-free replicated data types), differential privacy, on-device processing, certificate pinning, MDM (mobile device management), APNs, offline-first design, sync conflict resolution, vector clocks for sync, CDN edge replication.

---

### Microsoft

Microsoft's system design interviews vary significantly by team — Azure infrastructure teams expect cloud-native depth, Office/Teams product teams focus on collaboration and real-time sync, and gaming teams (Xbox) care about multiplayer game infrastructure. Microsoft acquired GitHub, LinkedIn, and Activision, so the breadth of systems is wide.

Azure is Microsoft's largest growth business. If interviewing for Azure or cloud-related roles, you are expected to know cloud-native patterns deeply and speak the language of managed services, IaaS, PaaS, and multi-tenancy.

**What they emphasize**:
- Enterprise scale and multi-tenancy. Microsoft serves large enterprises with strict SLA requirements. Multi-tenant architecture — serving thousands of customers from shared infrastructure while providing isolation guarantees — is a core pattern.
- Collaboration systems. Teams, SharePoint, and Office online all involve real-time collaborative editing — a hard distributed systems problem (operational transformation or CRDT). Real-time sync, presence indicators, and conflict resolution are relevant.
- Reliability and SLA compliance. Enterprise contracts have teeth — SLA breaches cost money. Reliability engineering, error budgets, and designing for measured uptime levels are important signals.
- Azure-native patterns. Azure Service Bus, Event Hubs (Kafka-compatible), Cosmos DB (globally distributed, multi-model), Azure Cache for Redis, and Kubernetes (Azure pioneered managed Kubernetes with AKS). Expect to discuss these services by name if interviewing for Azure roles.

**Example questions they have asked publicly**:
- Design a collaborative document editor (like Google Docs / Office Online)
- Design Azure Blob Storage (object storage at Microsoft's scale)
- Design a multi-tenant SaaS platform
- Design Microsoft Teams (real-time messaging, video, collaboration)
- Design a distributed job scheduler

**Keywords that signal you know their domain**:
Operational transformation, CRDT, multi-tenancy, tenant isolation, Azure Cosmos DB, Event Hub, Service Bus, Azure Functions, Kubernetes, managed identity, RBAC, blue/green deployment, feature management (LaunchDarkly-style), enterprise SSO, SAML, OAuth2.

---

## 2. Mid-Size Tech

### Uber

Uber is a geospatial, real-time marketplace. The core system design challenge is matching supply (drivers) with demand (riders) in real time, across a city, with sub-second latency requirements. Uber also runs at significant global scale with market-specific regulatory requirements.

**What they emphasize**:
- Geospatial indexing. How do you find the 10 nearest available drivers to a given pickup location, across millions of concurrent drivers? This requires a spatial index — quadtrees, geohashes, or H3 (Uber's own hexagonal grid system). Understand at least one approach deeply.
- Real-time matching. The dispatch system must match rider requests to drivers within seconds. This involves auction-like algorithms, latency requirements, and consistency requirements (a driver cannot be matched to two riders simultaneously).
- Event-driven architecture. Uber's systems generate enormous event streams — location pings from every active driver every few seconds, trip state transitions, payment events. Kafka underpins most of Uber's data infrastructure.
- Surge pricing and market dynamics. Designing systems that can compute and update pricing in real time across a city involves streaming aggregations and low-latency writes.
- High availability with regional isolation. Uber cannot afford the dispatch system to go down in a city. Multi-region active-active with data locality (data stays in the city/region it was created) is a standard pattern.

**Example questions they have asked publicly**:
- Design Uber's dispatch system (match riders to drivers)
- Design Uber's surge pricing system
- Design a location tracking system for real-time driver positions
- Design Uber Eats' order management system

**Keywords that signal you know their domain**:
Geohash, quadtree, H3, consistent hashing, real-time matching, event sourcing, Kafka Streams, saga pattern (for distributed trip state machine), idempotency, at-least-once delivery, CQRS, region-local data.

---

### Airbnb

Airbnb's core engineering challenge is a two-sided marketplace with unique supply (each listing is a unique property) and complex pricing (nightly rates, availability calendars, booking windows). Search is central — displaying the right listings to users in real time, ranked by relevance and price.

**What they emphasize**:
- Search and ranking at scale. Airbnb's search involves Elasticsearch for full-text and filter queries, combined with a machine learning ranking layer. They care about search architecture, indexing pipelines, and how to keep search results fresh as listings change.
- Payments and financial integrity. Booking involves financial transactions with strict correctness requirements. Idempotency, distributed transactions, the saga pattern, and fraud prevention are expected topics.
- Calendar and availability. Availability management — storing and querying which nights a property is available — is a non-trivial problem at Airbnb's scale. Concurrent bookings for the same dates must be prevented.
- Experimentation infrastructure. Airbnb has invested heavily in A/B testing and experimentation tooling (Superset, Minerva). They care about how you design systems to support controlled experiments and metric measurement.

**Example questions they have asked publicly**:
- Design Airbnb's search system
- Design Airbnb's booking system (availability, reservation, payment)
- Design a pricing recommendation system for hosts
- Design Airbnb's review system

**Keywords that signal you know their domain**:
Elasticsearch, inverted index, two-sided marketplace, optimistic locking, saga pattern, idempotency, calendar availability, distributed lock, event sourcing, experimentation platform, feature flags, fraud detection.

---

### Stripe

Stripe's entire business is payment infrastructure. Correctness is non-negotiable — losing or duplicating a financial transaction has direct, auditable consequences. Stripe interviewers have an extremely high bar for understanding distributed transactions, idempotency, and failure handling in financial systems.

**What they emphasize**:
- Idempotency is treated as a first-class citizen. Every write operation at Stripe must be idempotent — if a payment request is submitted twice (due to a retry), it must be processed exactly once. Expect to design idempotency key systems, discuss what idempotency guarantees at the HTTP level vs. the database level.
- Distributed transactions and correctness. Stripe processes transactions across multiple internal services. Two-phase commit, saga patterns, and compensating transactions are core topics.
- Reliability engineering. A payment processor that is down costs merchants money in real time. Stripe's SLA requirements are extreme. Circuit breakers, graceful degradation (queuing card authorizations during brief outages), and retries with backoff are expected.
- API design for developer experience. Stripe is famous for its developer API. They care about API design principles: versioning, backward compatibility, error response formats, webhook design, and idempotency keys as a public API feature.
- Fraud and risk systems. Real-time fraud detection at the point of transaction involves ML scoring, rule engines, and velocity checks — a stream processing problem.

**Example questions they have asked publicly**:
- Design a payment processing system
- Design Stripe's idempotency key system
- Design a fraud detection system for card transactions
- Design a webhook delivery system

**Keywords that signal you know their domain**:
Idempotency key, exactly-once processing, two-phase commit, saga pattern, compensating transaction, distributed lock, optimistic concurrency control, PCI-DSS (compliance context), card network authorization flow, webhook retry with backoff, event sourcing as audit trail, outbox pattern.

---

### Twilio

Twilio is a communications API platform — SMS, voice, email, and video delivered as programmable APIs. Their core challenge is interfacing with carrier networks (which are slow, unreliable, and use protocols from the 1980s) and providing a reliable, developer-friendly abstraction on top.

**What they emphasize**:
- Reliability despite unreliable dependencies. Carrier networks are not reliable. Designing Twilio's infrastructure means building retries, fallback carriers, delivery receipts, and status tracking on top of systems Twilio cannot control.
- High-throughput message queuing. SMS delivery involves ingesting large bursts of messages and delivering them to carriers that impose per-second rate limits per route. Queue management, rate limiting, and priority queuing are central.
- Webhook delivery. Twilio notifies customer applications of delivery status via webhooks. Reliable webhook delivery — at-least-once, with retries, backoff, dead letter queues, and delivery tracking — is a first-class engineering concern.
- Observability and debuggability. Twilio's customers debug their own applications through Twilio's logs. The logging and observability infrastructure must be queryable at the message level.

**Keywords that signal you know their domain**:
Carrier routing, SMPP protocol, at-least-once delivery, webhook delivery, exponential backoff with jitter, DLQ, rate limiting per carrier route, message status tracking, event sourcing for delivery timeline, outbound rate limiting, multi-carrier fallback.

---

## 3. Patterns That Appear Everywhere

These patterns come up at virtually every company. Knowing them well signals broad preparation.

**The read-heavy scaling pattern**: The majority of production systems read far more than they write. The canonical solution is a layered cache hierarchy — application-level cache for hot computed data, Redis for shared hot data across instances, a CDN for static and quasi-static content, read replicas for database read offloading. Be able to explain where each layer fits and what access patterns justify each layer.

**The write-scaling pattern**: Writes cannot be trivially distributed. The progression is: optimize the existing write path (remove unnecessary writes, batch writes, add write-behind buffering), then scale vertically, then add write-specialized storage (append-only logs, LSM-tree stores like Cassandra or RocksDB for high-write-throughput), then shard. Sharding is a last resort because of its operational complexity.

**The fan-out problem**: Any system where one write must be delivered to many readers faces fan-out. Social feeds, notifications, and pub/sub systems all encounter this. The push model (write to each follower on publish) has low read latency but high write amplification. The pull model (fetch from each following account on read) has high read latency but low write amplification. The hybrid model (push to online/small accounts, pull for large accounts and offline users) is the production standard.

**The idempotency pattern**: Any operation that crosses a network boundary must handle retries safely. The idempotency key pattern — the client generates a unique ID for each logical operation and includes it with every attempt; the server stores the result keyed to the idempotency key and returns the cached result for duplicates — is the industry standard for making non-idempotent operations (payments, sends) safe to retry.

**The event sourcing pattern**: Instead of storing current state, store the immutable log of events that produced it. Current state is derived by replaying events. Benefits: complete audit trail, ability to replay events, ability to derive new views by replaying history. Costs: read complexity (you must derive state from events), storage volume, the difficulty of changing event schemas. Used in financial systems, order management, and anywhere an audit trail is required.

**The saga pattern for distributed transactions**: When a business transaction spans multiple services and you cannot use a single ACID transaction, use a saga — a sequence of local transactions, each with a compensating transaction that undoes its effect if a later step fails. The saga coordinates via events (choreography) or a central orchestrator. Used at Uber (trip state machine), Amazon (order fulfillment), and Stripe (payment flow).

---

## 4. Red Flags Interviewers Watch For

These behaviors consistently signal junior thinking regardless of the technical content of the answer.

**Jumping to solutions before understanding the problem.** The first words are a technology name ("I'd use Kafka here"). No requirements were gathered, no scale established. Interviewers interpret this as an inability to work from requirements — a fundamental engineering discipline failure.

**Treating buzzwords as answers.** "We should use microservices," "just put it in the cloud," "use machine learning for this." These phrases without explanation or justification signal that the candidate has heard terms but does not understand when or why to apply them.

**Refusing to commit to a choice.** "It depends" followed by nothing is a non-answer. "It depends on X — in this case X means Y, so I'd choose Z because..." is a great answer. Interviewers are evaluating judgment. Judgment means making recommendations under uncertainty, not cataloguing options indefinitely.

**Over-engineering for the stated scale.** Designing a global multi-region active-active deployment for a system the interviewer described as handling 10,000 users. This signals a failure to read requirements and a tendency to build complex systems because they are interesting, not because they are appropriate.

**Ignoring failure modes.** Describing a happy-path architecture with no acknowledgment of what happens when any component fails. Senior engineers think about failure first. "What happens when the cache is unavailable?" should be answered without prompting.

**Skipping capacity estimation.** Architecture choices — which database, how many servers, whether you need caching — depend on scale. Jumping to architectural decisions without doing the math is like designing a bridge without calculating the load. Some interviewers will let it slide; most will note it as a weakness.

**Not asking clarifying questions.** Walking in and designing for assumptions that were never validated. Senior engineers know that poorly defined requirements produce poorly designed systems.

---

## 5. Vocabulary That Signals Senior-Level Thinking

These phrases, used correctly in context, signal that you think at a senior engineering level. The key word is "correctly" — using them without demonstrating understanding of when and why they apply will backfire.

**"The bottleneck here is..."** — Demonstrates systems thinking. You are identifying the specific constraint, not adding components speculatively.

**"This is a trade-off between X and Y; given the stated requirement of Z, I'd favor X."** — The canonical form of a senior design decision. Shows awareness of trade-offs, ties the choice to requirements, and commits to a recommendation.

**"I'd want to validate this with load testing before committing to this architecture."** — Shows operational maturity. Architectures are hypotheses until tested.

**"What happens when this component fails?"** — Self-asking the failure question. Shows resilience thinking is natural, not prompted.

**"We could start simple and evolve — begin with X, add Y when we hit constraint Z."** — Demonstrates evolutionary design and awareness that over-engineering has costs. The right system for 10,000 users is simpler than the right system for 10 million.

**"The access pattern here is..."** — Storage choices are driven by access patterns, not by what you are familiar with. Naming the access pattern before naming the storage solution shows that you derive the choice from the problem.

**"This assumes..."** — Making assumptions explicit is a senior behavior. Hidden assumptions are where architectures fail. Surfacing them lets the interviewer correct them if wrong.

**"My concern with that approach is..."** — Engaging critically with your own proposals or the interviewer's suggestions. Shows intellectual honesty and the ability to think adversarially about designs.

**"The write amplification here would be..."** — Shows awareness of secondary costs of design choices, not just the primary functionality.

**"I'm optimizing for read latency at the cost of write latency here, which is the right trade-off because..."** — Demonstrates that trade-offs are conscious and reasoned, not accidental.

---

## Navigation

| | |
|---|---|
| Home | [README.md](../README.md) |
| Interview Framework | [23 — Interview Framework](../23_interview_framework/the_45_minute_playbook.md) |
| Rapid Fire Q&A | [rapid_fire.md](./rapid_fire.md) |
| Scenario Questions | [scenario_questions.md](./scenario_questions.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Interview Framework — Interview Q&A](../23_interview_framework/interview.md) &nbsp;|&nbsp; **Next:** [Rapid Fire Q&A →](./rapid_fire.md)

**Related Topics:** [Rapid Fire Q&A](./rapid_fire.md) · [Scenario Questions](./scenario_questions.md)
