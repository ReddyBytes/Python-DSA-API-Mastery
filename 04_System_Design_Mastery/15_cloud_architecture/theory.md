<a id="top"></a>

# Cloud Architecture

> "When I started at Infosys in Hyderabad," Rajesh tells his mentee over filter coffee, "we waited eight weeks for servers to arrive from Dell. Eight weeks! Today I spin up a hundred machines in Mumbai region before my chai gets cold. That shift from owning hardware to renting compute changed everything about how we architect systems."

Rajesh is a Telugu cloud solutions architect who has designed multi-region deployments serving hundreds of millions of users across Asia-Pacific and beyond. He learned cloud the hard way: migrating a legacy banking system from on-premise racks in Bangalore to AWS, one service at a time, while keeping five-nines availability. His philosophy is simple: "Cloud is not magic. It is someone else's computer, managed well. Your job is to pick the right abstractions and know when they leak."

## Table of Contents

- [1. Service Models — IaaS, PaaS, SaaS, FaaS](#1-service-models)
- [2. Why Cloud? On-Premise vs the Alternative](#2-why-cloud)
  - [The Old Way: On-Premise](#the-old-way-on-premise)
  - [The Cloud Model: Elasticity and Pay-as-You-Go](#the-cloud-model)
- [3. The Big Three — AWS, GCP, Azure](#3-the-big-three)
- [4. Core AWS Services — The Essential Map](#4-core-aws-services)
  - [Compute](#compute)
  - [Storage](#storage)
  - [Databases](#databases)
  - [Networking](#networking)
  - [Queues and Events](#queues-and-events)
- [5. Key Cloud Primitives — Know These Cold](#5-key-cloud-primitives)
  - [Compute Primitives](#compute-primitives)
  - [Storage Primitives](#storage-primitives)
  - [Networking Primitives](#networking-primitives)
  - [Queuing and Messaging](#queuing-and-messaging)
  - [Caching](#caching)
- [6. Serverless — When Functions Beat Servers](#6-serverless)
  - [The Promise](#the-promise)
  - [The Cold Start Problem](#the-cold-start-problem)
  - [When Serverless Wins](#when-serverless-wins)
  - [When Serverless Fails](#when-serverless-fails)
- [7. Containers and Kubernetes](#7-containers-and-kubernetes)
  - [Docker: The Packaging Revolution](#docker-the-packaging-revolution)
  - [Kubernetes: The Container Orchestra](#kubernetes-the-container-orchestra)
  - [When Kubernetes Is Worth the Complexity](#when-kubernetes-is-worth-the-complexity)
  - [ECS vs EKS](#ecs-vs-eks)
- [8. Multi-Region Deployment](#8-multi-region-deployment)
  - [Why Go Multi-Region](#why-go-multi-region)
  - [Deployment Patterns](#deployment-patterns)
  - [Data Replication Across Regions](#data-replication-across-regions)
  - [The Cost of Multi-Region](#the-cost-of-multi-region)
  - [Route 53 Routing Policies](#route-53-routing-policies)
- [9. Auto-Scaling — Right-Sizing in Real-Time](#9-auto-scaling)
  - [How Auto-Scaling Works](#how-auto-scaling-works)
  - [Types of Scaling](#types-of-scaling)
  - [Predictive vs Reactive Scaling](#predictive-vs-reactive-scaling)
- [10. Cost Optimization](#10-cost-optimization)
- [11. The Cloud Architecture Mindset](#11-the-cloud-architecture-mindset)
- [12. Mini Exercises](#12-mini-exercises)
- [13. Learning Priority](#13-learning-priority)
- [14. Practice Questions](#14-practice-questions)
- [15. Summary](#15-summary)

<a id="1-service-models"></a>

# 1. Service Models — IaaS, PaaS, SaaS, FaaS

"Think of it like housing in Hyderabad," Rajesh explains. "IaaS is buying bare land in Gachibowli — you build everything yourself. PaaS is renting a furnished flat in Madhapur — the building is done, you just move in. SaaS is staying at a hotel on Tank Bund — fully managed, you just show up. And FaaS? That is booking an OYO room for one night — you pay only when you actually sleep there."

**Service models** define how much infrastructure the cloud provider manages vs. how much you manage.

```
                    You Manage          Provider Manages
────────────────────────────────────────────────────────────
On-Premises    App, Runtime, OS,    (nothing — all yours)
               Middleware, Servers,
               Storage, Networking

IaaS           App, Runtime, OS,    Servers, Storage,
               Middleware           Networking, Virtualization
               (EC2, GCE)

PaaS           App code only        Runtime, OS, Middleware,
               (Heroku, App Engine) Servers, Storage, Networking

FaaS           Function logic only  Everything else
               (Lambda, Cloud Run)  Including runtime lifecycle

SaaS           Configuration only   Everything
               (Salesforce, Gmail)
```

**When to choose each:**

```
IaaS (EC2, GCE):     Full OS control, custom networking, legacy software migration
PaaS (App Engine):   Rapid deployment, no ops team, standard web apps
FaaS (Lambda):       Event-driven, variable load, short-lived tasks (< 15 min)
SaaS:                Commodity needs (email, CRM, analytics) — buy not build
```

"In my banking migration," Rajesh recalls, "the legacy COBOL batch jobs needed IaaS — full OS control, specific kernel parameters. The new customer-facing API went on PaaS. The nightly reconciliation triggers became Lambda functions. Different tools for different jobs."

[Back to Top](#top)

<a id="2-why-cloud"></a>

# 2. Why Cloud? On-Premise vs the Alternative

"Let me tell you about 2009," Rajesh says, leaning back. "My manager at the bank asked me to estimate capacity for Diwali season. I said we need 3x our normal servers for two weeks. He said procurement takes eight weeks. So we ordered in August for October traffic. Half those servers sat idle until March. That is the problem cloud solves."

<a id="the-old-way-on-premise"></a>

## The Old Way: On-Premise

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

The fundamental economic problem: you must provision for your *peak* traffic, but you pay for that capacity 24/7, including off-peak hours.

<a id="the-cloud-model"></a>

## The Cloud Model: Elasticity and Pay-as-You-Go

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

For most companies, cloud's elasticity and reduced operational overhead outweigh the higher per-unit cost.

"The bank eventually moved," Rajesh says. "Not because cloud was cheaper per-unit — it was not. But because we stopped paying for idle capacity during non-Diwali months. The total cost of ownership dropped 40%."

[Back to Top](#top)

<a id="3-the-big-three"></a>

# 3. The Big Three — AWS, GCP, Azure

"In interviews," Rajesh advises, "default to AWS terminology. It is what interviewers expect. But know the equivalents — many companies use GCP or Azure, and you should not look lost when someone says 'Cloud SQL' instead of 'RDS'."

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

**The practical answer:** AWS for startups and general use. Azure if your company runs on Microsoft stack. GCP if you have heavy data/ML workloads or need Kubernetes best-in-class.

"My current company uses all three," Rajesh admits. "Data pipelines on GCP BigQuery, customer-facing APIs on AWS, internal tools on Azure because of Active Directory integration. Multi-cloud is messy but real."

[Back to Top](#top)

<a id="4-core-aws-services"></a>

# 4. Core AWS Services — The Essential Map

"AWS has 200+ services," Rajesh says, pulling up his whiteboard. "You need maybe 15 of them for 90% of real systems. Here is the map I give every new engineer on my team."

<a id="compute"></a>

## Compute

```
EC2 (Elastic Compute Cloud)
  → Virtual machines. Full OS control. Any workload.
  → Auto Scaling Groups: automatically add/remove EC2 instances on load.
  → Key choice: instance family (m = general, c = compute, r = memory, g = GPU)

Lambda
  → Functions as a Service. Event-triggered. Auto-scales to zero.
  → Limits: 15 min max runtime, 10 GB RAM, 512 MB /tmp storage.
  → Billing: per 100ms execution (pay zero when idle).

ECS / EKS
  → ECS: AWS-native container orchestration (simpler)
  → EKS: managed Kubernetes (more control, steeper curve)
  → Fargate: serverless containers — no EC2 nodes to manage
```

<a id="storage"></a>

## Storage

```
S3 (Simple Storage Service)
  → Object storage. 11 9s durability. Unlimited capacity.
  → Use for: static assets, backups, data lake, logs, ML datasets.
  → Storage classes: Standard → Standard-IA → Glacier → Deep Archive (cost ↓, latency ↑)

EBS (Elastic Block Store)
  → Block storage. Attached to EC2 like a disk.
  → Use for: databases, OS volumes, high-IOPS workloads.

EFS (Elastic File System)
  → Network file system. Shared across multiple EC2 instances.
  → Use for: shared configuration, content management systems.
```

<a id="databases"></a>

## Databases

```
RDS              → Managed relational DB (MySQL, PostgreSQL, Aurora)
DynamoDB         → Managed NoSQL. Single-digit ms. Auto-scales.
ElastiCache      → Managed Redis/Memcached. In-memory caching.
Redshift         → Data warehouse. Column-oriented. Petabyte scale.
Aurora Serverless → RDS that scales to zero (pause when idle).
```

<a id="networking"></a>

## Networking

```
VPC (Virtual Private Cloud)
  → Isolated network. Your private space in AWS.
  → Subnets: public (internet-accessible) vs private (internal only)
  → NAT Gateway: allows private subnets to reach internet (outbound only)

CloudFront    → CDN. 450+ edge PoPs. HTTPS termination at edge.
Route 53      → DNS. Health checks. Failover routing. Latency routing.
ALB/NLB       → Application Load Balancer (L7) / Network Load Balancer (L4)
API Gateway   → Managed API endpoint. Rate limiting, auth, caching.
```

<a id="queues-and-events"></a>

## Queues and Events

```
SQS    → Message queue. At-least-once delivery. Up to 14-day retention.
SNS    → Pub-sub. Push notifications to SQS, Lambda, HTTP endpoints.
Kinesis → Real-time data streaming. Like Kafka as a service.
EventBridge → Event bus. Route events between AWS services.
```

[Back to Top](#top)

<a id="5-key-cloud-primitives"></a>

# 5. Key Cloud Primitives — Know These Cold

"These are the building blocks," Rajesh says. "Every cloud system is assembled from these. When I design a system on the whiteboard, I am picking from this palette. Know them cold."

<a id="compute-primitives"></a>

## Compute Primitives

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

  Use when: (covered in depth in Section 6)
```

<a id="storage-primitives"></a>

## Storage Primitives

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

<a id="networking-primitives"></a>

## Networking Primitives

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

<a id="queuing-and-messaging"></a>

## Queuing and Messaging

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

<a id="caching"></a>

## Caching

```
ElastiCache:
  AWS-managed Redis or Memcached.
  Use for: session storage, query result caching, leaderboards.
  See 06_caching for full caching theory.

CloudFront (CDN):
  AWS's CDN. Edge caching for static content globally.
  See 07_storage_cdn for full CDN theory.
```

[Back to Top](#top)

<a id="6-serverless"></a>

# 6. Serverless — When Functions Beat Servers

"A web server runs 24/7 waiting for requests," Rajesh explains. "A Lambda function sleeps for free and wakes up in milliseconds when a request arrives. For our festival traffic — Diwali spike, then nothing for weeks — this changed the economics completely. We stopped paying for idle servers during off-peak months."

**When serverless wins:**

```
Good fits:
  Event-driven processing (image uploaded → resize → store)
  Webhook handlers (GitHub event → CI trigger)
  Scheduled jobs (daily report generation)
  APIs with unpredictable/spiky traffic
  Startup/prototype: zero infrastructure setup

Bad fits:
  Long-running processes (> 15 min)
  Consistent high-throughput (always-on servers cheaper)
  Stateful workloads (need external state store)
  Cold start sensitive (< 100ms latency requirement)
```

<a id="the-promise"></a>

## The Promise

You write a function. The cloud runs it. You pay per invocation. No servers to provision, patch, or monitor.

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

<a id="the-cold-start-problem"></a>

## The Cold Start Problem

When a Lambda function hasn't run recently, AWS needs to provision an execution environment. This takes 100ms to several seconds.

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

**Cold start times by runtime (approximate):**

```
Python 3.12:    ~200ms cold,   ~1ms warm
Node.js 20:     ~150ms cold,   ~1ms warm
Java 21:        ~800ms cold,   ~5ms warm  (JVM startup)
Go:             ~100ms cold,   ~1ms warm

Mitigation: Provisioned Concurrency (keep N containers warm, billed idle)
```

**Lambda cold start optimization pattern:**

```python
# Cold start: Lambda initializes container → loads runtime → runs init code
# Warm start: container already running → jumps straight to handler

# Minimize cold start: keep init code outside handler
import boto3
dynamodb = boto3.resource("dynamodb")  # ← runs ONCE at cold start
table = dynamodb.Table("users")        # ← reused on warm invocations

def handler(event, context):
    # ← warm path: runs every invocation
    user_id = event["user_id"]
    return table.get_item(Key={"id": user_id})
```

<a id="when-serverless-wins"></a>

## When Serverless Wins

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

<a id="when-serverless-fails"></a>

## When Serverless Fails

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

"We made this mistake once," Rajesh confesses. "Put the payment processing service on Lambda. It called three other Lambdas downstream. Cold start cascaded — P99 hit 8 seconds during morning spikes. We moved it back to ECS Fargate within a week."

[Back to Top](#top)

<a id="7-containers-and-kubernetes"></a>

# 7. Containers and Kubernetes

"A container is like a tiffin box," Rajesh says. "Everything your app needs — code, runtime, libraries — packed into one portable unit. It runs the same on your laptop, on staging, on production. No more 'but it works on my machine' excuses from developers."

**VM vs Container:**

```
Virtual Machine:             Container:
┌────────────────┐           ┌──────────────────────────┐
│   Application  │           │  App A  │  App B  │ App C │
├────────────────┤           ├─────────┴─────────┴───────┤
│  Guest OS      │           │     Container Runtime      │
├────────────────┤           ├────────────────────────────┤
│  Hypervisor    │           │         Host OS            │
├────────────────┤           ├────────────────────────────┤
│  Physical HW   │           │       Physical HW          │
└────────────────┘           └────────────────────────────┘
Full OS per VM (~GBs)        Shared kernel (MBs, starts in ms)
```

<a id="docker-the-packaging-revolution"></a>

## Docker: The Packaging Revolution

Before Docker, deploying software meant: "it works on my machine, but not on production." Different OS versions, different library versions, different environment variables — endless configuration drift.

Docker packages your application and ALL its dependencies (OS libraries, language runtime, configs) into a single portable unit called a container.

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

<a id="kubernetes-the-container-orchestra"></a>

## Kubernetes: The Container Orchestra

Running one container is easy. Running hundreds of containers across dozens of servers, scaling them up and down, restarting crashed ones, routing traffic — that is where Kubernetes comes in.

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

**Key Kubernetes concepts:**

```
Cluster     → group of nodes (machines)
Node        → one machine (EC2 instance)
Pod         → one or more containers that share network/storage
Deployment  → manages desired number of pod replicas, rolling updates
Service     → stable DNS name + load balancing across pods
Ingress     → HTTP routing rules (path-based, host-based) to services
ConfigMap   → inject config into pods (env vars, files)
Secret      → inject sensitive config (passwords, keys) — base64 encoded
HPA         → Horizontal Pod Autoscaler: scale pods on CPU/custom metrics
```

<a id="when-kubernetes-is-worth-the-complexity"></a>

## When Kubernetes Is Worth the Complexity

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

<a id="ecs-vs-eks"></a>

## ECS vs EKS

```
ECS Fargate:   Simpler. No cluster management. AWS-native. Smaller teams.
EKS:           Full Kubernetes. Multi-cloud portability. Large teams. More control.
```

"I tell my team: if you have fewer than 10 microservices and your entire company is on AWS, use ECS Fargate. If you are building a platform that might move across clouds, or you have 50+ services, then invest in Kubernetes. The learning curve is real — budget three months for your team to get comfortable."

[Back to Top](#top)

<a id="8-multi-region-deployment"></a>

# 8. Multi-Region Deployment

"A single data center is a single point of failure," Rajesh says gravely. "In 2021, AWS us-east-1 went down for hours. Companies with single-region architectures vanished from the internet. Our system? We lost us-east-1 traffic for 45 seconds while Route 53 failed over to ap-south-1. Multi-region saved us."

<a id="why-go-multi-region"></a>

## Why Go Multi-Region

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

<a id="deployment-patterns"></a>

## Deployment Patterns

```
Active-Passive:
  Primary region handles all traffic.
  Secondary region is on standby (warm or cold).
  Failover: DNS switch (Route 53 health-check routing).
  RPO: depends on replication lag.
  RTO: minutes (warm standby) to hours (cold standby).

Active-Active:
  All regions handle traffic simultaneously.
  Users routed to nearest region (latency-based routing).
  Data synchronization required between regions.
  RPO: near-zero.
  RTO: seconds (automatic failover).
  Complexity: much higher — handle write conflicts.
```

<a id="data-replication-across-regions"></a>

## Data Replication Across Regions

```python
# Aurora Global Database: one primary region writes, 5 secondary regions read
# Replication lag: typically < 1 second between regions

# DynamoDB Global Tables: active-active, multi-region writes
# Conflict resolution: last-write-wins (by timestamp)

# S3 Cross-Region Replication (CRR):
# Async. Usually < 15 minutes. Enable for compliance or latency.
```

<a id="the-cost-of-multi-region"></a>

## The Cost of Multi-Region

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

<a id="route-53-routing-policies"></a>

## Route 53 Routing Policies

```
Latency routing:    Route user to lowest-latency region
Geolocation:        Route by user's country/continent (compliance)
Failover:           Route to secondary when primary health check fails
Weighted:           A/B test or canary by sending % to each region
```

"For our India deployment," Rajesh explains, "we use latency-based routing between ap-south-1 Mumbai and ap-southeast-1 Singapore. Users in South India get routed to Mumbai. Users in Southeast Asia get Singapore. If Mumbai goes down, all traffic shifts to Singapore within 60 seconds."

[Back to Top](#top)

<a id="9-auto-scaling"></a>

# 9. Auto-Scaling — Right-Sizing in Real-Time

"Manual capacity management is how you get 3 AM pages," Rajesh says. "Auto-scaling is the cloud's answer to 'provision for peak, pay only for what you use.' I set it up once, and I sleep through the night."

<a id="how-auto-scaling-works"></a>

## How Auto-Scaling Works

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

**Auto Scaling Group policy example:**

```python
# Auto Scaling Group policy — scale based on CPU
{
  "PolicyType": "TargetTrackingScaling",
  "TargetTrackingScalingPolicyConfiguration": {
    "TargetValue": 70.0,            # ← keep average CPU at 70%
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ASGAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,         # ← wait 5 min before scaling in
    "ScaleOutCooldown": 60          # ← scale out faster than in
  }
}
```

<a id="types-of-scaling"></a>

## Types of Scaling

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

<a id="predictive-vs-reactive-scaling"></a>

## Predictive vs Reactive Scaling

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

"We use all three," Rajesh says. "Scheduled scaling pre-warms for known peaks like morning logins. Predictive handles the gradual ramp. Reactive catches unexpected spikes. Belt, suspenders, and a backup belt."

[Back to Top](#top)

<a id="10-cost-optimization"></a>

# 10. Cost Optimization

"Cloud bills have surprised every company that did not plan for them," Rajesh warns. "The same services that make scaling easy also make spending easy. I have seen startups burn through their Series A funding in six months because nobody watched the AWS bill. Cost optimization is an engineering discipline, not an afterthought."

**The five pillars of cloud cost optimization:**

**1. Right-sizing** — match instance size to actual usage:

```
Tool: AWS Compute Optimizer (analyzes CloudWatch metrics)
Rule: If CPU avg < 20%, downsize to next smaller instance family.
```

**2. Reserved capacity** — commit to 1-3 years for 30-70% discount:

```
On-Demand:     Pay per hour. No commitment. Most expensive.
Reserved (1yr): 30-40% discount. Commit to instance type/region.
Reserved (3yr): 50-70% discount. Maximum commitment.
Spot/Preemptible: 60-90% discount. Can be terminated with 2-min notice.
                  Use for: batch jobs, CI/CD, stateless workers.
```

**3. Auto-scaling** — scale in when load drops:

```python
# Auto Scaling Group policy — scale based on CPU
{
  "PolicyType": "TargetTrackingScaling",
  "TargetTrackingScalingPolicyConfiguration": {
    "TargetValue": 70.0,            # ← keep average CPU at 70%
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ASGAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,         # ← wait 5 min before scaling in
    "ScaleOutCooldown": 60          # ← scale out faster than in
  }
}
```

**4. Storage tiering** — move cold data to cheaper tiers:

```
S3 Lifecycle policy:
  Day 0:   Standard (frequent access)    $0.023/GB
  Day 30:  Standard-IA (infrequent)      $0.0125/GB
  Day 90:  Glacier Instant Retrieval     $0.004/GB
  Day 180: Glacier Deep Archive          $0.00099/GB
```

**5. Monitor and alert** — AWS Cost Explorer + budget alerts:

```
Set budget alerts at 80% and 100% of monthly target.
Tag all resources (team, environment, service) for cost attribution.
```

"Rule of thumb," Rajesh adds. "Review your AWS bill every Friday. If anything grew more than 20% week-over-week without a corresponding traffic increase, investigate immediately. Runaway costs are always a bug — either in your code or in your architecture."

[Back to Top](#top)

<a id="11-the-cloud-architecture-mindset"></a>

# 11. The Cloud Architecture Mindset

"When you sit down to design a system using cloud services," Rajesh says, "think in layers. This is my mental checklist — I run through it for every design, whether it is a whiteboard interview or a real production system."

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

"If you can answer all seven of these clearly in an interview," Rajesh says, "you have demonstrated cloud architecture competence. Most candidates only think about compute and storage — they forget networking, scaling, failure modes, and observability."

[Back to Top](#top)

<a id="12-mini-exercises"></a>

# 12. Mini Exercises

**1.** You are designing a startup's first cloud deployment. They have a Python Flask API and a PostgreSQL database. Sketch the AWS architecture for: (a) MVP with $200/month budget, (b) post-Series A with 50,000 daily users.

**2.** A Lambda function processes image thumbnails. It is fast (~800ms) but users complain about occasional 5-second delays. What is happening? What two strategies could fix it? What is the trade-off of each?

**3.** Your e-commerce site has 10x traffic on Black Friday compared to normal. You have 4 servers running normally. Design an auto-scaling policy. What metrics would you scale on? What are the min/max instance counts?

**4.** Leadership wants "multi-region for disaster recovery." Your engineering team is 6 people. What are the real costs (not just money) of going multi-region? Under what conditions would you recommend it vs a simpler approach?

**5.** Rajesh's challenge: Your company serves users in India (ap-south-1), Europe (eu-west-1), and US (us-east-1). The primary database is in us-east-1. Indian users complain about 300ms latency on reads. Design a solution that reduces read latency to under 50ms for Indian users while maintaining write consistency. What trade-offs are you making?

[Back to Top](#top)

<a id="13-learning-priority"></a>

# 13. Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
IaaS vs PaaS vs SaaS vs FaaS, AWS/GCP core services, serverless trade-offs, containers vs VMs, multi-region deployment, disaster recovery (RTO/RPO)

**Should Learn** — Important for real projects, comes up regularly:
auto-scaling groups, managed databases, CDN integration, VPC/networking basics, cost optimization fundamentals, Kubernetes overview

**Good to Know** — Useful in specific situations:
multi-cloud strategy, spot/preemptible instances, reserved capacity, service quotas, infrastructure as code (Terraform basics)

**Reference** — Know it exists, look up when needed:
specific service limits, pricing calculators, compliance certifications (SOC2, HIPAA), cloud provider SLA details

[Back to Top](#top)

<a id="14-practice-questions"></a>

# 14. Practice Questions

> **Practice:** [Q10 - api-gateway-role](../system_design_practice_questions_100.md#q10--normal--api-gateway-role)

> **Practice:** [Q60 - blue-green-canary](../system_design_practice_questions_100.md#q60--interview--blue-green-canary)

> **Practice:** [Q75 - global-system-design](../system_design_practice_questions_100.md#q75--design--global-system-design)

[Back to Top](#top)

<a id="15-summary"></a>

# 15. Summary

```
┌─────────────────────────────────────────────────────────────────┐
│  CLOUD ARCHITECTURE — KEY TAKEAWAYS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Service Models:                                                │
│    IaaS = full OS control (EC2)                                │
│    PaaS = just deploy code (App Engine)                        │
│    FaaS = just write functions (Lambda)                        │
│    SaaS = just configure (Gmail)                               │
│                                                                 │
│  Compute choices:                                               │
│    VMs → full control, any workload                            │
│    Containers → portable, efficient, reproducible              │
│    Serverless → event-driven, pay-per-use, auto-scale          │
│                                                                 │
│  Multi-region:                                                  │
│    Active-Passive = simple DR, minutes RTO                     │
│    Active-Active = low latency, seconds RTO, high complexity   │
│    Cost: engineering time + data egress + consistency trade-offs│
│                                                                 │
│  Auto-scaling:                                                  │
│    Horizontal > Vertical for most workloads                    │
│    Use reactive + predictive + scheduled together              │
│    Always set min AND max limits                               │
│                                                                 │
│  Cost optimization:                                             │
│    Right-size → Reserved → Auto-scale → Tier storage → Monitor │
│    Review bills weekly, not monthly                             │
│                                                                 │
│  Interview mindset (7 layers):                                  │
│    Compute → Data → Communication → Traffic → Scale →          │
│    Failure modes → Observability                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

"Cloud architecture," Rajesh concludes, "is not about memorizing 200 AWS services. It is about understanding the trade-offs between cost, complexity, latency, and reliability — and picking the right combination for your specific problem. In every interview and every design, show that you understand those trade-offs. That is what separates a senior engineer from someone who just reads documentation."

[Back to Top](#top)

**[Back to README](../README.md)**

**Prev:** [Observability](../14_observability/theory.md) | **Next:** [High Level Design](../16_high_level_design/theory.md)

**Related Topics:** [Distributed Systems](../10_distributed_systems/theory.md) | [Scalability Patterns](../11_scalability_patterns/theory.md) | [Microservices](../12_microservices/theory.md)

**Cheatsheet:** [cheetsheet.md](./cheetsheet.md) | **Interview:** [interview.md](./interview.md)
