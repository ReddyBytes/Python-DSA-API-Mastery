# Renting the Datacenter: How Cloud Actually Works
## A Practical Guide to Cloud Architecture

> In 2006, Amazon had a problem: they had built massive amounts of server
> infrastructure to handle holiday traffic peaks, and it sat idle 90% of the year.
> Their solution — renting that infrastructure to others — became AWS.
> That accident of history changed how every company builds software.

---

## Part 1: Why Cloud? On-Premise vs the Alternative

### The Old Way: On-Premise

Before cloud, companies bought their own servers. The process looked like this:

```
Traditional on-premise lifecycle:

  Week 1:  Order servers (predict capacity 18-24 months in advance)
  Week 6:  Servers arrive
  Week 8:  Rack, stack, cable, configure
  Week 10: Deploy your application
  Year 2:  Traffic grew 3x — you're out of capacity
           (or traffic never grew — servers sit idle, you've overpaid)

Capital expenditure:  $500K for a server rack
Lead time:            6-8 weeks minimum
Flexibility:          None — you own what you bought
```

The fundamental economic problem: you must provision for your *peak* traffic,
but you pay for that capacity 24/7, including off-peak hours.

### The Cloud Model: Elasticity and Pay-as-You-Go

```
Cloud model:

  Monday 9 AM: spin up 10 servers for the morning rush
  Monday 11 PM: scale down to 2 servers (much less traffic)
  Black Friday: spin up 500 servers for 6 hours, scale back down

  Pay only for what you use.
  No capital expenditure.
  No lead time — capacity available in seconds.
```

The economics shift from **capital expense (CapEx)** to **operating expense (OpEx)**.

```
On-premise:            Cloud:
  Own the asset          Rent the service
  Fixed cost             Variable cost
  Your problem to manage Their problem to manage
  6-week provisioning    60-second provisioning
  Over/under-provision   Right-sized in real-time
```

**When on-premise still wins:**
- Extremely predictable, flat workloads (steady utilization 24/7)
- Regulatory requirements that forbid cloud (rare, but exists)
- Very high data volumes where egress costs make cloud expensive
- Specialized hardware (GPU clusters, HPC) you would use constantly

For most companies, cloud's elasticity and reduced operational overhead
outweigh the higher per-unit cost.

---

## Part 2: The Big Three — AWS, GCP, Azure

There are three dominant cloud providers. You will encounter all three.

```
┌──────────────────────────────────────────────────────────────────┐
│                         AWS (Amazon)                             │
│                                                                  │
│  Market share:  ~32% (the original and still largest)           │
│  Launched:      2006                                             │
│  Strongest at:  Breadth. AWS has 200+ services.                 │
│                 If it exists in computing, AWS has it.           │
│  Known for:     EC2, S3, Lambda, RDS, DynamoDB                  │
│  Used by:       Netflix, Airbnb, Slack, most startups            │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    GCP (Google Cloud Platform)                   │
│                                                                  │
│  Market share:  ~12%                                             │
│  Launched:      2008 (publicly)                                  │
│  Strongest at:  Data and ML. BigQuery is best-in-class.         │
│                 Kubernetes (Google invented it).                 │
│                 Global fiber network (Google's private internet).│
│  Known for:     GKE, BigQuery, Pub/Sub, Spanner, Vertex AI      │
│  Used by:       Spotify, Twitter (historical), Snap              │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                         Azure (Microsoft)                        │
│                                                                  │
│  Market share:  ~23%                                             │
│  Launched:      2010                                             │
│  Strongest at:  Enterprise. Deep Microsoft/Office 365/AD        │
│                 integration. Dominant in enterprise sales.       │
│  Known for:     Azure AD, Azure DevOps, Cosmos DB, AKS          │
│  Used by:       Fortune 500 enterprises, healthcare, finance     │
└──────────────────────────────────────────────────────────────────┘
```

**The practical answer:** AWS for startups and general use. Azure if your
company runs on Microsoft stack. GCP if you have heavy data/ML workloads
or need Kubernetes best-in-class.

In a system design interview, default to AWS terminology — it's what
interviewers expect unless stated otherwise.

---

## Part 3: Key Cloud Primitives — Know These Cold

These are the building blocks. Every cloud system is assembled from these.

### Compute

```
VIRTUAL MACHINES (EC2 / GCE / Azure VMs)
  A full computer in the cloud, rented by the hour.
  You choose: OS, CPU count, RAM, disk type.

  Use when:
    - Your app needs full OS control
    - You're running a database yourself
    - Long-running processes
    - You need predictable, dedicated resources

  Key concepts:
    Instance types: t3.micro (cheap, shared), c5.4xlarge (compute-optimized)
    AMI: Amazon Machine Image — a snapshot of OS + config to boot from
    Reserved vs On-demand: reserve for 1-3 years for 40-60% discount
    Spot instances: up to 90% cheaper, but can be terminated with 2-min notice

────────────────────────────────────────────────────────────────────

CONTAINERS (ECS / GKE / AKS)
  Package your app + dependencies into a portable unit.
  Multiple containers can run on one VM.
  Faster to start than VMs, more isolated than bare processes.

  Use when:
    - Microservices that need consistent environments
    - You want to run many services efficiently on fewer machines
    - CI/CD pipelines that need reproducibility

────────────────────────────────────────────────────────────────────

SERVERLESS (Lambda / Cloud Functions / Azure Functions)
  Write a function. Cloud runs it when triggered. You pay per invocation.
  No servers to manage — they appear and disappear automatically.

  Use when: (covered in depth in Part 4)
```

### Storage

```
OBJECT STORAGE (S3 / GCS / Azure Blob)
  Files + metadata via HTTP. Unlimited scale.
  Covered in detail in 07_storage_cdn.

BLOCK STORAGE (EBS / Persistent Disk)
  A virtual hard drive attached to a VM.
  Use for: database data volumes, OS disks.

MANAGED DATABASES (RDS / Cloud SQL / Azure Database)
  AWS runs PostgreSQL/MySQL/SQL Server for you.
  They handle: backups, patches, failover, replication.
  You handle: schema, queries, scaling decisions.

  Key services:
    RDS:           Managed MySQL, PostgreSQL, SQL Server, Oracle
    Aurora:        AWS's reimplemented MySQL/Postgres — 5x faster, more durable
    DynamoDB:      Managed NoSQL — key-value + document, auto-scaling
    Cloud SQL:     GCP's managed MySQL/PostgreSQL
    Cosmos DB:     Azure's globally distributed NoSQL
```

### Networking

```
VPC (Virtual Private Cloud):
  Your own private network inside the cloud.
  Isolated from other customers by default.
  You define IP ranges, subnets, routing tables.

  ┌─────────────────────────────────────────────────────┐
  │                   VPC (10.0.0.0/16)                 │
  │                                                     │
  │  Public Subnet (10.0.1.0/24)                        │
  │  ┌────────────────────────┐                         │
  │  │  Load Balancer         │ ← internet-facing       │
  │  │  NAT Gateway           │                         │
  │  └────────────────────────┘                         │
  │                                                     │
  │  Private Subnet (10.0.2.0/24)                       │
  │  ┌────────────────────────┐                         │
  │  │  App Servers           │ ← no direct internet    │
  │  │  Cache (Redis)         │   access                │
  │  └────────────────────────┘                         │
  │                                                     │
  │  Database Subnet (10.0.3.0/24)                      │
  │  ┌────────────────────────┐                         │
  │  │  RDS Primary           │ ← most restricted       │
  │  │  RDS Replica           │                         │
  │  └────────────────────────┘                         │
  └─────────────────────────────────────────────────────┘

Security Groups:
  Stateful firewall rules attached to instances.
  "Allow port 443 from 0.0.0.0/0 (public internet)"
  "Allow port 5432 only from app server security group"

Load Balancers:
  ALB (Application Load Balancer): routes HTTP/HTTPS, path-based routing
  NLB (Network Load Balancer): TCP/UDP, ultra-low latency, fixed IPs

DNS (Route 53):
  AWS's DNS service. Routes domain names to IPs.
  Health checks: automatically remove unhealthy endpoints.
  Routing policies: weighted, latency-based, geolocation, failover.
```

### Queuing and Messaging

```
SQS (Simple Queue Service):
  Managed message queue. Point-to-point.
  Producer puts message → one consumer reads and processes.
  Use for: background job processing, decoupling services.

SNS (Simple Notification Service):
  Managed pub/sub. One message → multiple subscribers.
  "Fan-out" pattern: one event → SQS queue + email + Lambda.
  Use for: notifications, broadcasting events.

  SQS vs SNS:
    SQS: work queue (tasks to be done, processed once)
    SNS: notification bus (news everyone should hear)

  Common combo: SNS topic → multiple SQS queues
    Each subscriber gets its own queue, processes independently.

Pub/Sub (GCP):
  GCP's equivalent to SNS + SQS combined.
  Topics, subscriptions, pull or push delivery.
```

### Caching

```
ElastiCache:
  AWS-managed Redis or Memcached.
  Use for: session storage, query result caching, leaderboards.
  See 06_caching for full caching theory.

CloudFront (CDN):
  AWS's CDN. Edge caching for static content globally.
  See 07_storage_cdn for full CDN theory.
```

---

## Part 4: Serverless — When It Shines (and When It Fails)

### The Promise

You write a function. The cloud runs it. You pay per invocation.
No servers to provision, patch, or monitor.

```python
# This is a Lambda function.
# AWS runs this when triggered (API call, S3 event, schedule, etc.)

def handler(event, context):
    user_id = event['pathParameters']['userId']
    # process something
    return {
        'statusCode': 200,
        'body': json.dumps({'userId': user_id})
    }
```

AWS handles:
- Starting the execution environment
- Scaling from 0 to 10,000 simultaneous invocations automatically
- Shutting down when idle
- Patches and security

You handle: the function logic.

### The Cold Start Problem

When a Lambda function hasn't run recently, AWS needs to provision an
execution environment. This takes 100ms to several seconds.

```
Cold start:  First invocation after idle period
  AWS must: allocate container, load runtime (Python/Node/Java),
            load your code, run initialization

  Cold start times:
    Python/Node:  ~100-500ms
    Java/.NET:    1-5 seconds (heavy JVM startup)
    Compiled (Go/Rust): ~50-100ms

Warm start:  Subsequent invocations (same container reused)
  AWS reuses the container → ~1ms overhead

Problem:
  Unpredictable latency for users hitting cold Lambda functions.
  Bad for: latency-sensitive applications, consistent P99 requirements.

Mitigation:
  Provisioned concurrency: pre-warm N instances (you pay even when idle)
  Keep-alive pings: schedule events every 5 min to prevent cold starts
  Right-size: don't use Lambda where latency consistency matters
```

### When Serverless Wins

```
GOOD fits for Lambda / Cloud Functions:

  Event-driven processing:
    "When a file is uploaded to S3 → run this Lambda"
    "Every night at 2 AM → run this cleanup Lambda"
    Natural fit — you only pay when events happen.

  Infrequent or spiky tasks:
    Thumbnail generation (bursty: many uploads at once, then quiet)
    Sending confirmation emails (triggered by signups)
    Webhooks from external services

  Simple APIs (with caveats):
    CRUD APIs with low latency requirements
    Internal tools, admin APIs
    APIs with predictable traffic patterns

  Glue code:
    ETL transformations triggered by S3 events
    Data enrichment pipelines
    Integration between SaaS services
```

### When Serverless Fails

```
BAD fits for Lambda / Cloud Functions:

  Long-running work:
    Lambda max timeout: 15 minutes. Anything longer → not Lambda.
    Video transcoding, large data processing → use ECS/EC2 instead.

  Complex state:
    Lambda is stateless. Between invocations, nothing persists in memory.
    You need external storage (Redis, DynamoDB) for everything.
    Complex stateful orchestration → use Step Functions or a server.

  Strict latency requirements:
    Cold starts make P99 latency unpredictable.
    If you promise 50ms P99 → Lambda may not deliver consistently.

  High-volume sustained load:
    A Lambda constantly running = paying per invocation indefinitely.
    Often cheaper: one EC2 instance running 24/7.
    Break-even: roughly >10M invocations/month favors EC2.

  Chatty microservices:
    Lambda → Lambda calls add cold start and overhead per hop.
    Better: containerized services with persistent connections.
```

---

## Part 5: Containers and Kubernetes

### Docker: The Packaging Revolution

Before Docker, deploying software meant: "it works on my machine, but not on
production." Different OS versions, different library versions, different
environment variables — endless configuration drift.

Docker packages your application and ALL its dependencies (OS libraries,
language runtime, configs) into a single portable unit called a container.

```
┌─────────────────────────────────────────────────────────┐
│                   Docker Container                      │
│                                                         │
│  Your app code         ← your Python/Node/Java code     │
│  Language runtime      ← Python 3.11 exactly            │
│  System libraries      ← libssl 1.1.1 exactly           │
│  OS layer (minimal)    ← Alpine Linux                   │
│                                                         │
│  Same container runs identically:                       │
│    On your laptop (Mac/Linux/Windows)                   │
│    On staging server                                    │
│    On production server                                 │
│    On any cloud (AWS, GCP, Azure)                       │
└─────────────────────────────────────────────────────────┘
```

Containers vs VMs:

```
VM:                              Container:
  Full OS kernel                   Shares host OS kernel
  1-2 GB per VM                    10-100 MB per container
  Minutes to start                 Seconds to start
  Stronger isolation               Process-level isolation
  Use: full OS environments        Use: application packaging
```

### Kubernetes: The Container Orchestra

Running one container is easy. Running hundreds of containers across dozens
of servers, scaling them up and down, restarting crashed ones, routing traffic
— that's where Kubernetes comes in.

```
What Kubernetes does:

  Scheduling:   "I have 3 server nodes and 50 containers to run.
                 Fit them efficiently across the nodes."

  Healing:      "Container crashed on node-3. Start a new one on node-1."

  Scaling:      "Traffic spiked. I need 10 replicas of this service instead of 3.
                 Spin them up. Traffic dropped. Scale back to 3."

  Routing:      "Send traffic to pods with label app=frontend.
                 Load balance across all healthy replicas."

  Rolling updates: "Deploy new version to 1 pod at a time.
                    If health checks fail, stop and roll back."
```

Key Kubernetes concepts:

```
Pod:         One or more containers that always run together on the same node.
             The smallest deployable unit. Usually = 1 container.

Deployment:  "Run 3 replicas of this pod. Always maintain 3.
              If one dies, replace it."

Service:     A stable endpoint (IP + DNS name) that routes to pods.
             Pods come and go; the Service name stays constant.

Ingress:     HTTP routing rules. "Traffic to /api → backend service.
             Traffic to / → frontend service."

ConfigMap:   Non-secret configuration injected into pods as env vars or files.

Secret:      Like ConfigMap but encrypted at rest. Use for credentials.
```

### When Kubernetes Is Worth the Complexity

Kubernetes is powerful but genuinely complex. Be honest about the trade-off:

```
K8s IS worth it when:
  - You have 10+ microservices to manage
  - You have a dedicated platform/DevOps team
  - You need sophisticated deployment strategies (canary, blue-green)
  - You need automatic scaling and self-healing
  - You're building a platform others will deploy onto

K8s is NOT worth it when:
  - Small team (< 5 engineers) without K8s expertise
  - Monolith or a few simple services
  - Early-stage startup where speed matters more than ops sophistication
  - Simpler alternatives work: ECS + Fargate, App Runner, Fly.io, Render

The hidden cost: K8s takes 20-30% of engineering time for operations.
Make sure you have the team size to absorb that.
```

---

## Part 6: Multi-Region Design

### Why Go Multi-Region?

Three distinct reasons drive multi-region architecture. Know all three:

```
1. LATENCY REDUCTION FOR GLOBAL USERS

   Single region (us-east-1) → users in Asia get 200ms base latency.
   Multi-region (us-east-1 + ap-southeast-1) → Asian users get 20ms.

   Matters for: consumer apps with global audience, real-time features.

2. DISASTER RECOVERY

   Single region failure (rare but happens: AWS us-east-1 outages in 2021).
   With multi-region active-active: traffic fails over in seconds.
   RTO (Recovery Time Objective): how fast you recover.
   RPO (Recovery Point Objective): how much data you can lose.

3. DATA SOVEREIGNTY

   EU GDPR: EU citizens' data may need to stay in EU.
   Some countries (China, Russia) require local data storage.
   Healthcare, finance: specific country storage requirements.
```

### The Cost of Multi-Region

Multi-region is not free. Be explicit about this in design interviews:

```
Engineering complexity:
  Every data operation now has to consider: "which region is the source?"
  Schema changes must be applied in all regions.
  Debugging spans multiple regions.

The Consistency Problem:
  If user Alice updates her profile in us-east-1, and simultaneously
  reads it from ap-southeast-1 — does she see the new or old version?

  Option A: Synchronous replication
    Wait for all regions before confirming write.
    + Consistent reads everywhere
    - Write latency = slowest region (100ms+ added)

  Option B: Asynchronous replication (eventual consistency)
    Confirm write in local region, replicate in background.
    + Fast writes
    - Stale reads in other regions for 100ms-seconds

  Option C: Route reads to write region (read-your-own-writes)
    For critical reads, always go to the region you wrote to.
    + Consistency for the writing user
    - More complex routing logic
    - Users can still see stale data from other users

Data egress costs:
  Cross-region data transfer: ~$0.02/GB
  High-traffic multi-region system: thousands of dollars/month in data costs.

┌──────────────────────────────────────────────────────────┐
│           Multi-Region Architecture Diagram              │
│                                                          │
│  ┌─────────────┐      sync/async     ┌─────────────┐    │
│  │  us-east-1  │ ──────────────────→ │ eu-west-1   │    │
│  │             │ ←────────────────── │             │    │
│  │  App + DB   │   replication       │  App + DB   │    │
│  └──────┬──────┘                     └──────┬──────┘    │
│         │                                   │            │
│         └─────────── Route 53 ─────────────┘            │
│                   (latency-based routing)                │
│                   routes user to nearest region          │
└──────────────────────────────────────────────────────────┘
```

---

## Part 7: Auto-Scaling — Right-Sizing in Real-Time

Manual capacity management is how you get 3 AM pages. Auto-scaling is
the cloud's answer to "provision for peak, pay only for what you use."

### How Auto-Scaling Works

```
You define:
  Min instances:   2   (always running, never below)
  Max instances:  20   (never above, cost control)
  Desired:         4   (current target)

  Scale-out trigger:  CPU > 70% for 5 minutes → add 2 instances
  Scale-in trigger:   CPU < 30% for 15 minutes → remove 1 instance

AWS Auto Scaling Group:

  9 AM:   traffic rises → CPU hits 75% → +2 instances → 6 total
  10 AM:  traffic rises more → CPU hits 72% → +2 more → 8 total
  12 PM:  peak → 12 instances running
  3 PM:   traffic drops → scale in gradually → back to 4
  10 PM:  minimal traffic → scale in to 2 (the minimum)

                instances
        14 │         ╭───╮
        12 │        ╭╯   ╰╮
        10 │       ╭╯     ╰╮
         8 │      ╭╯       ╰╮
         6 │    ╭─╯         ╰─╮
         4 │──╭─╯             ╰─╮──
         2 │──╯                 ╰───
           └─────────────────────────── time
             6AM  9AM  12PM 3PM  6PM  9PM
```

### Types of Scaling

```
Horizontal scaling (scale-out): add more instances
  + No single point of failure
  + Can scale to arbitrary size
  - Requires stateless app design
  - More complex (load balancing, session management)

Vertical scaling (scale-up): make the instance bigger
  + Simple — no app changes needed
  + Good for databases (harder to scale horizontally)
  - Hard ceiling (largest instance type available)
  - Single point of failure
  - Requires downtime to change instance type (usually)

Scaling triggers:
  CPU utilization       → most common
  Request count         → good for APIs
  Queue depth           → for worker fleets (SQS queue length)
  Custom metrics        → business metrics via CloudWatch
  Schedule              → "scale up at 8 AM, down at 8 PM"
```

### Predictive vs Reactive Scaling

```
Reactive (default):
  Wait for metric to breach threshold, then scale.
  Problem: lag between spike and new capacity = brief slowdown.

Predictive (AWS Predictive Scaling):
  ML model analyzes historical patterns.
  Scales up BEFORE expected traffic increase.
  Good for: daily patterns (morning commute traffic spike).

Scheduled scaling:
  "Every weekday at 7 AM, set desired count to 10.
   Every weekday at 9 PM, set to 3."
  Simple, effective when traffic patterns are predictable.
```

---

## The Cloud Architecture Mindset

When you sit down to design a system using cloud services, think in layers:

```
1. What is my compute model?
   Single VM? Auto-scaled fleet? Containers? Serverless?

2. Where does my data live?
   Managed DB (RDS)? NoSQL (DynamoDB)? Object storage (S3)?
   How is it backed up? How does it fail over?

3. How do components communicate?
   Synchronous (HTTP/gRPC)? Asynchronous (SQS/SNS)?
   Where are the bottlenecks?

4. How does traffic enter?
   Load balancer (ALB)? API Gateway? CDN (CloudFront)?
   What is my DNS setup?

5. How does it scale?
   What scales horizontally? What is the scaling bottleneck?
   What triggers scaling?

6. Where can it fail, and what happens?
   Single region or multi-region?
   What is the RTO/RPO?
   Are there SPOFs?

7. How do I observe it?
   Logs → CloudWatch Logs / Datadog
   Metrics → CloudWatch Metrics
   Traces → X-Ray / Jaeger
```

---

## Mini Exercises

**1.** You are designing a startup's first cloud deployment. They have a Python
Flask API and a PostgreSQL database. Sketch the AWS architecture for:
(a) MVP with $200/month budget, (b) post-Series A with 50,000 daily users.

**2.** A Lambda function processes image thumbnails. It's fast (~800ms) but
users complain about occasional 5-second delays. What is happening?
What two strategies could fix it? What is the trade-off of each?

**3.** Your e-commerce site has 10x traffic on Black Friday compared to normal.
You have 4 servers running normally. Design an auto-scaling policy.
What metrics would you scale on? What are the min/max instance counts?

**4.** Leadership wants "multi-region for disaster recovery." Your engineering
team is 6 people. What are the real costs (not just money) of going multi-region?
Under what conditions would you recommend it vs a simpler approach?

---

## Navigation

| | |
|---|---|
| Previous | [14 — Observability](../14_observability/seeing_your_system.md) |
| Next | [16 — High Level Design](../16_high_level_design/theory.md) |
| Home | [README.md](../README.md) |
