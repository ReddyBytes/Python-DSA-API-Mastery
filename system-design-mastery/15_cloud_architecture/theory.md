# ☁️ Cloud Architecture — Building Systems That Scale Globally

> In 2010, running a global service meant buying servers in data centers on three continents. Today, a startup can deploy to 30 regions, auto-scale to a million users, and pay nothing until traffic arrives. That's the cloud revolution.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
IaaS vs PaaS vs SaaS vs FaaS · AWS/GCP core services · serverless trade-offs · containers vs VMs · multi-region deployment · disaster recovery (RTO/RPO)

**Should Learn** — Important for real projects, comes up regularly:
auto-scaling groups · managed databases · CDN integration · VPC/networking basics · cost optimization fundamentals · Kubernetes overview

**Good to Know** — Useful in specific situations:
multi-cloud strategy · spot/preemptible instances · reserved capacity · service quotas · infrastructure as code (Terraform basics)

**Reference** — Know it exists, look up when needed:
specific service limits · pricing calculators · compliance certifications (SOC2, HIPAA) · cloud provider SLA details

---

## 🏗️ Chapter 1: Service Models — IaaS, PaaS, SaaS, FaaS

> Think of housing: IaaS is renting bare land (you build everything), PaaS is renting a furnished apartment (infrastructure done, you bring your stuff), SaaS is staying in a hotel (fully managed, just use it), FaaS is booking an Airbnb per night (pay only when occupied).

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

---

## ⚡ Chapter 2: Core AWS Services — The Essential Map

> AWS has 200+ services. You need maybe 15 of them for 90% of real systems. Here's the map.

**Compute:**

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

**Storage:**

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

**Databases:**

```
RDS              → Managed relational DB (MySQL, PostgreSQL, Aurora)
DynamoDB         → Managed NoSQL. Single-digit ms. Auto-scales.
ElastiCache      → Managed Redis/Memcached. In-memory caching.
Redshift         → Data warehouse. Column-oriented. Petabyte scale.
Aurora Serverless → RDS that scales to zero (pause when idle).
```

**Networking:**

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

**Queues and Events:**

```
SQS    → Message queue. At-least-once delivery. Up to 14-day retention.
SNS    → Pub-sub. Push notifications to SQS, Lambda, HTTP endpoints.
Kinesis → Real-time data streaming. Like Kafka as a service.
EventBridge → Event bus. Route events between AWS services.
```

---

## 🔧 Chapter 3: Serverless — When Functions Beat Servers

> A web server runs 24/7 waiting for requests. A Lambda function sleeps for free and wakes up in milliseconds when a request arrives. For spiky, unpredictable workloads, this changes the economics completely.

**When serverless wins:**

```
✓  Event-driven processing (image uploaded → resize → store)
✓  Webhook handlers (GitHub event → CI trigger)
✓  Scheduled jobs (daily report generation)
✓  APIs with unpredictable/spiky traffic
✓  Startup/prototype: zero infrastructure setup

✗  Long-running processes (> 15 min)
✗  Consistent high-throughput (always-on servers cheaper)
✗  Stateful workloads (need external state store)
✗  Cold start sensitive (< 100ms latency requirement)
```

**Lambda cold start:**

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

**Cold start times by runtime (approximate):**

```
Python 3.12:    ~200ms cold,   ~1ms warm
Node.js 20:     ~150ms cold,   ~1ms warm
Java 21:        ~800ms cold,   ~5ms warm  (JVM startup)
Go:             ~100ms cold,   ~1ms warm

Mitigation: Provisioned Concurrency (keep N containers warm, billed idle)
```

---

## 🐳 Chapter 4: Containers and Kubernetes

> A container is a self-contained package: your app, its dependencies, and its runtime all bundled together. Like a shipping container — it runs the same everywhere, no "works on my machine."

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

**Kubernetes core concepts:**

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

**When to use ECS vs EKS:**

```
ECS Fargate:   Simpler. No cluster management. AWS-native. Smaller teams.
EKS:           Full Kubernetes. Multi-cloud portability. Large teams. More control.
```

---

## 🌍 Chapter 5: Multi-Region Deployment

> A single data center is a single point of failure. One backhoe cutting a fiber cable, one power outage, one AWS region going down — and your service vanishes. Multi-region deployment means no single location can take you down.

**Deployment patterns:**

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

**Data replication across regions:**

```python


# Aurora Global Database: one primary region writes, 5 secondary regions read
# Replication lag: typically < 1 second between regions

# DynamoDB Global Tables: active-active, multi-region writes


# Conflict resolution: last-write-wins (by timestamp)

# S3 Cross-Region Replication (CRR):
# Async. Usually < 15 minutes. Enable for compliance or latency.
```

> 📝 **Practice:** [Q60 · blue-green-canary](../system_design_practice_questions_100.md#q60--interview--blue-green-canary)
> 📝 **Practice:** [Q75 · global-system-design](../system_design_practice_questions_100.md#q75--design--global-system-design)


**Route 53 routing policies:**

```
Latency routing:    Route user to lowest-latency region
Geolocation:        Route by user's country/continent (compliance)
Failover:           Route to secondary when primary health check fails
Weighted:           A/B test or canary by sending % to each region
```

---

## 💰 Chapter 6: Cost Optimization

> Cloud bills have surprised every company that didn't plan for them. The same services that make scaling easy also make spending easy. Cost optimization is an engineering discipline, not an afterthought.

**The five pillars of cloud cost optimization:**

**1. Right-sizing** — match instance size to actual usage:

```
Tool: AWS Compute Optimizer (analyzes CloudWatch metrics)
Rule: If CPU avg < 20%, downsize to next smaller instance family.
```

**2. Reserved capacity** — commit to 1–3 years for 30–70% discount:

```
On-Demand:     Pay per hour. No commitment. Most expensive.
Reserved (1yr): 30–40% discount. Commit to instance type/region.
Reserved (3yr): 50–70% discount. Maximum commitment.
Spot/Preemptible: 60–90% discount. Can be terminated with 2-min notice.
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

---

---

## 📝 Practice Questions

> 📝 **Practice:** [Q10 · api-gateway-role](../system_design_practice_questions_100.md#q10--normal--api-gateway-role)

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Prev | [../14_observability/theory.md](../14_observability/theory.md) |
| ➡️ Next | [../16_high_level_design/theory.md](../16_high_level_design/theory.md) |
| 📖 Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Observability](../14_observability/theory.md) &nbsp;|&nbsp; **Next:** [High Level Design →](../16_high_level_design/theory.md)

**Related Topics:** [Distributed Systems](../10_distributed_systems/theory.md) · [Scalability Patterns](../11_scalability_patterns/theory.md) · [Microservices](../12_microservices/theory.md)
