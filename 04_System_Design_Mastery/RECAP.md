# System Design Mastery — Topic Recap

> One-line summary of every module. Use this to quickly find which module covers the concept you need.

---

## Infrastructure Fundamentals

| Module | Topics Covered |
|--------|---------------|
| [00 — Computer Fundamentals](./00_computer_fundamentals/story.md) | CPU, memory hierarchy (L1/L2/L3 cache, RAM, SSD), process vs thread, context switching, I/O blocking vs async — the hardware layer every system runs on |
| [01 — Networking Basics](./01_networking_basics/theory.md) | OSI and TCP/IP models, TCP vs UDP, DNS, HTTP/1.1–3, TLS, WebSockets, SSE, gRPC, L4 vs L7 networking — how bytes move between machines |
| [02 — System Fundamentals](./02_system_fundamentals/theory.md) | Scalability, availability, reliability, latency vs throughput, CAP theorem, PACELC, consistency models, fault tolerance patterns, back-of-envelope estimation |
| [04 — Backend Architecture](./04_backend_architecture/intro.md) | Stateless design, connection pooling, synchronous vs asynchronous processing, request lifecycle, monolith scaling limits — how a single server handles traffic |
| [15 — Cloud Architecture](./15_cloud_architecture/theory.md) | IaaS vs PaaS vs FaaS vs SaaS, AWS/GCP core services, serverless trade-offs, containers vs VMs, auto-scaling, multi-region deployment, disaster recovery (RTO/RPO) |

---

## Data & Storage

| Module | Topics Covered |
|--------|---------------|
| [05 — Databases](./05_databases/theory.md) | SQL vs NoSQL selection, ACID properties, indexes, sharding strategies, replication modes, connection pooling, query optimization |
| [06 — Caching](./06_caching/theory.md) | Cache-aside, write-through, write-behind, Redis data structures, TTL and eviction policies (LRU/LFU), CDN caching, cache stampede and thundering herd |
| [07 — Storage & CDN](./07_storage_cdn/theory.md) | Block vs file vs object storage, S3 architecture and consistency, CDN PoPs and cache invalidation, media transcoding pipeline, presigned URLs, BLOB chunking |
| [20 — Data Systems](./20_data_systems/theory.md) | OLTP vs OLAP, data warehouse vs data lake, ETL vs ELT, columnar storage (Parquet), batch vs stream processing, CDC, Kafka Streams, data lakehouse |

---

## Distributed Systems

| Module | Topics Covered |
|--------|---------------|
| [08 — Load Balancing](./08_load_balancing/theory.md) | Round-robin, least-connections, IP hash, consistent hashing, L4 vs L7 load balancers, health checks, sticky sessions, GSLB multi-region routing |
| [09 — Message Queues](./09_message_queues/theory.md) | Pub-sub vs point-to-point, Kafka (brokers/topics/partitions/offsets), RabbitMQ (exchanges/bindings), at-least-once vs exactly-once delivery, dead letter queues, consumer groups |
| [10 — Distributed Systems](./10_distributed_systems/theory.md) | Fallacies of distributed computing, Raft consensus, replication modes (leader-follower/multi-leader/leaderless), vector clocks, quorum reads/writes, distributed transactions (2PC/Saga/Outbox), gossip protocols, split-brain |
| [21 — Real-Time Systems](./21_real_time_systems/theory.md) | Event-driven architecture, WebSocket scaling, Redis pub/sub, fan-out strategies, live leaderboards, operational transforms, time-series databases, backpressure, CRDT conflict resolution |

---

## Architecture Patterns

| Module | Topics Covered |
|--------|---------------|
| [11 — Scalability Patterns](./11_scalability_patterns/theory.md) | CQRS (read/write model separation), event sourcing, fan-out on write vs read, write and read amplification, database federation, data denormalization trade-offs |
| [12 — Microservices](./12_microservices/theory.md) | Monolith vs microservices trade-offs, Strangler Fig decomposition, sync vs async communication, service discovery, API gateway, circuit breaker, Saga pattern, distributed tracing |
| [13 — Security](./13_security/theory.md) | Authentication vs authorization, OAuth2 flows, JWT structure and pitfalls, API keys, rate limiting algorithms (token bucket/leaky bucket/sliding window), TLS, DDoS protection, OWASP Top 10 |
| [14 — Observability](./14_observability/theory.md) | Three pillars (metrics/traces/logs), distributed tracing (spans/trace context/OpenTelemetry), SLOs and error budgets, structured logging, alerting thresholds, Grafana, ELK stack |

---

## Design Methodology

| Module | Topics Covered |
|--------|---------------|
| [03 — API Design](./03_api_design/theory.md) | REST vs GraphQL vs gRPC trade-offs, API versioning strategies, cursor-based pagination, idempotency keys, rate limiting placement, OpenAPI documentation |
| [16 — High Level Design](./16_high_level_design/theory.md) | HLD interview framework (clarify→estimate→architecture→deep dive→trade-offs), capacity estimation, communication patterns, architecture selection, complete walkthroughs of URL shortener/Twitter/WhatsApp/Netflix/Uber |
| [17 — Low Level Design](./17_low_level_design/theory.md) | OOP pillars, SOLID principles, design patterns (Factory/Strategy/Observer/State/Decorator), class diagrams, state machines, worked examples (parking lot, elevator, chess, library, notification service) |
| [18 — Design Patterns](./18_design_patterns/theory.md) | GoF creational (Singleton/Factory/Builder), structural (Adapter/Decorator/Facade/Proxy), behavioral (Observer/Strategy/Command/State), patterns in distributed systems, anti-patterns |
| [19 — Clean Architecture](./19_clean_architecture/theory.md) | Dependency rule, layered vs hexagonal vs Clean Architecture, Domain-Driven Design (DDD), bounded contexts, aggregates/entities/value objects, repository pattern, CQRS as architectural pattern |

---

## Case Studies & Interview

| Module | Topics Covered |
|--------|---------------|
| [22 — Case Studies](./22_case_studies/theory.md) | Five complete system walkthroughs: URL shortener (hashing/caching), Twitter feed (fan-out), Netflix (CDN/adaptive bitrate), Uber (geo-indexing/WebSockets), WhatsApp (encryption/message ordering) |
| [23 — Interview Framework](./23_interview_framework/theory.md) | RESHADED 8-step framework, 45-minute time allocation, requirements clarification (functional vs non-functional), capacity estimation, trade-off articulation, common mistakes that separate junior from senior answers |
| [99 — Interview Master](./99_interview_master/) | Rapid-fire flash questions, company-specific patterns, open-ended scenario questions for judgment (cascading failures, real-time notifications, zero-downtime migrations, distributed rate limiter) |

---

*Total modules: 24 + interview · Last updated: 2026-04-21*
