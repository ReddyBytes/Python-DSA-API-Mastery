# 🏗️ System Design Mastery
> From understanding computers to designing systems that serve millions.
> Structured as a step-by-step learning journey — each topic builds on the previous one.
> Covers: HLD, LLD, distributed systems, networking, cloud, data, and real-world case studies.

---

## 🎯 How to Use This

Read **in order**. Each topic is designed to build on the one before it.

```
Stage 1: Foundations (00–02)   → How computers and networks actually work
Stage 2: APIs & Services (03–04) → How services communicate
Stage 3: Data Layer (05–07)    → Where data lives
Stage 4: Scale & Queues (08–10) → Handling traffic and async work
Stage 5: Advanced Arch (11–15) → Patterns for growing systems
Stage 6: Design Practice (16–19) → HLD, LLD, patterns, clean code
Stage 7: Data at Scale (20–21) → Streaming, analytics, real-time
Stage 8: Interview Prep (22–23 + 99) → Putting it all together
```

---

## 📂 Full Learning Path

### 🖥️ Stage 1: How Computers & Networks Work

| # | Topic | What You'll Understand |
|---|-------|----------------------|
| 00 | [Computer Fundamentals](./00_computer_fundamentals/story.md) | CPU, RAM, disk, processes, threads, I/O — the machine your code runs on |
| 01 | [Networking Basics](./01_networking_basics/theory.md) | TCP/IP, HTTP/1–3, TLS, DNS, WebSockets, gRPC — how data travels |
| 02 | [System Fundamentals](./02_system_fundamentals/theory.md) | CAP theorem, latency, throughput, availability, SLOs — the vocabulary of scale |

---

### 🔌 Stage 2: Services & Communication

| # | Topic | What You'll Understand |
|---|-------|----------------------|
| 03 | [API Design](./03_api_design/theory.md) | REST, GraphQL, gRPC — the interface between services *(See api-mastery for deep dive)* |
| 04 | [Backend Architecture](./04_backend_architecture/intro.md) | Client-server model, monoliths, stateless services, request lifecycle |

---

### 🗄️ Stage 3: The Data Layer

| # | Topic | What You'll Understand |
|---|-------|----------------------|
| 05 | [Databases](./05_databases/theory.md) | SQL vs NoSQL, ACID, indexing, replication, sharding |
| 06 | [Caching](./06_caching/theory.md) | Redis, cache patterns, eviction, CDN, when caching hurts |
| 07 | [Storage & CDN](./07_storage_cdn/theory.md) | Object storage, block storage, CDN strategy, static assets |

---

### ⚡ Stage 4: Handling Traffic & Async Work

| # | Topic | What You'll Understand |
|---|-------|----------------------|
| 08 | [Load Balancing](./08_load_balancing/theory.md) | L4 vs L7, algorithms, health checks, sticky sessions |
| 09 | [Message Queues](./09_message_queues/theory.md) | Kafka, RabbitMQ, SQS — async processing, at-least-once, fan-out |
| 10 | [Distributed Systems](./10_distributed_systems/theory.md) | Consensus (Raft), replication lag, partitioning, split-brain, quorum |

---

### 🏗️ Stage 5: Building for Scale

| # | Topic | What You'll Understand |
|---|-------|----------------------|
| 11 | [Scalability Patterns](./11_scalability_patterns/theory.md) | CQRS, event sourcing, saga, write amplification, fan-out patterns |
| 12 | [Microservices](./12_microservices/theory.md) | Monolith → microservices, service mesh, inter-service communication |
| 13 | [Security](./13_security/theory.md) | Authentication, OAuth2, JWT, rate limiting, DDoS protection |
| 14 | [Observability](./14_observability/theory.md) | Metrics, logs, traces — seeing inside a running system |
| 15 | [Cloud Architecture](./15_cloud_architecture/theory.md) | AWS/GCP/Azure patterns, serverless, containers, Kubernetes |

---

### 📐 Stage 6: Design Practice

| # | Topic | What You'll Understand |
|---|-------|----------------------|
| 16 | [High Level Design (HLD)](./16_high_level_design/theory.md) | How to design any system: capacity, services, data flow, trade-offs |
| 17 | [Low Level Design (LLD)](./17_low_level_design/theory.md) | SOLID, OOP, design patterns, class modeling, state machines |
| 18 | [Design Patterns](./18_design_patterns/theory.md) | GoF patterns — Factory, Observer, Strategy, Command, State, Decorator |
| 19 | [Clean Architecture](./19_clean_architecture/theory.md) | Hexagonal, DDD, ports & adapters, bounded contexts, aggregates |

---

### 📊 Stage 7: Data at Scale & Real-Time

| # | Topic | What You'll Understand |
|---|-------|----------------------|
| 20 | [Data Systems at Scale](./20_data_systems/theory.md) | Data warehouses, lakes, ETL/ELT, Spark, analytics pipelines |
| 21 | [Real-Time Systems](./21_real_time_systems/theory.md) | Stream processing, event-driven architecture, WebRTC, live systems |

---

### 🎯 Stage 8: Interview Preparation

| # | Topic | Content |
|---|-------|---------|
| 22 | [Case Studies](./22_case_studies/theory.md) | URL Shortener, Twitter, Netflix, Uber, WhatsApp — full walkthroughs |
| 23 | [Interview Framework](./23_interview_framework/theory.md) | 45-minute structured approach, what interviewers look for |
| 99 | [Interview Master](./99_interview_master/) | Rapid-fire Q&A, company-specific patterns, scenario questions |

---

## 🔑 Mental Models

### Memory Hierarchy (fastest → slowest)
```
L1 Cache → L2 Cache → L3 Cache → RAM → SSD → HDD → Network
   1 ns       7 ns      10 ns    100ns  150μs  10ms   50-200ms
```
Every system design decision is about keeping data at the fastest level possible.

### The CAP Triangle
```
             Consistency
                 │
        ─────────┼─────────
        │        │         │
        │    Pick Two      │
        │                  │
  Availability ─────── Partition
               Tolerance
```

### Scalability Ladder
```
1 user:      SQLite, single process
1K users:    MySQL + read replica
10K users:   Add Redis caching
100K users:  Add CDN + load balancer
1M users:    Shard DB + message queues + async
10M+ users:  Microservices + multi-region + CQRS
```

---

## ⚡ Quick Decision Guide

```
Need strong consistency?              → SQL + ACID transactions
Need horizontal write scale?          → NoSQL (Cassandra, DynamoDB)
Need full-text search?                → Elasticsearch
Need computed result caching?         → Redis + TTL
Need event streaming / fan-out?       → Kafka
Need simple task queue?               → RabbitMQ or SQS
Need file/image/video storage?        → S3 + CDN
Need real-time bidirectional comms?   → WebSockets
Need internal service comms (fast)?   → gRPC
Need async service decoupling?        → Message queue
Need rate limiting?                   → Token bucket in Redis
Need distributed lock?                → Redis SETNX or ZooKeeper
Need service discovery?               → Consul / Kubernetes DNS
Need distributed tracing?             → Jaeger / OpenTelemetry
Need time-series data?                → InfluxDB / TimescaleDB
Need audit trail / event replay?      → Event Sourcing
Need separate read/write scale?       → CQRS
Need container orchestration?         → Kubernetes
Need serverless compute?              → AWS Lambda / Cloud Functions
```

---

## 📊 Numbers to Know

```
Operation                     Latency       Notes
──────────────────────────────────────────────────────────────
L1 cache reference            0.5 ns
RAM access                    100 ns
SSD random read               150 μs
Network (same data center)    500 μs        ← cost of 1 service call
HDD seek                      10 ms
Network (US → Europe)         150 ms
Network (US → Australia)      200 ms

Throughput:
Single app server             ~10,000 req/s
MySQL (simple queries)        ~10,000 QPS
Redis                         ~100,000 ops/s
Kafka (batching)              ~1M msgs/s

Storage sizing:
1M records × 1KB = 1 GB
1B records × 1KB = 1 TB
1B req/day ÷ 86,400s ≈ 12,000 req/s
```

---

## 🔁 Navigation

| | |
|---|---|
| 🚀 Start | [00 — Computer Fundamentals](./00_computer_fundamentals/story.md) |
| 🏛️ HLD | [16 — High Level Design](./16_high_level_design/theory.md) |
| 🔩 LLD | [17 — Low Level Design](./17_low_level_design/theory.md) |
| 🌐 Distributed | [10 — Distributed Systems](./10_distributed_systems/theory.md) |
| 🎯 Interview | [23 — Interview Framework](./23_interview_framework/theory.md) |
| 🐍 Python Mastery | [../python-complete-mastery/](../python-complete-mastery/) |
| 📊 DSA Mastery | [../dsa-complete-mastery/](../dsa-complete-mastery/) |
