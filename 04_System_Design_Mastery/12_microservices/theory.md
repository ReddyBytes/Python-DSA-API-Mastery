<a id="top"></a>

# Microservices — Theory

> Break a monolith into independently deployable services — and manage the distributed systems complexity that follows.

> 📝 **Practice:** [Q21 · what-is-microservice](../system_design_practice_questions_100.md#q21--normal--what-is-microservice) · [Q22 · monolith-vs-microservice](../system_design_practice_questions_100.md#q22--interview--monolith-vs-microservice) · [Q54 · service-discovery](../system_design_practice_questions_100.md#q54--normal--service-discovery) · [Q59 · service-mesh](../system_design_practice_questions_100.md#q59--thinking--service-mesh) · [Q83 · compare-monolith-microservice](../system_design_practice_questions_100.md#q83--interview--compare-monolith-microservice) · [Q97 · design-decision-monolith-startup](../system_design_practice_questions_100.md#q97--design--design-decision-monolith-startup)

> 📝 **Practice:** [Q55 · circuit-breaker-microservices](../system_design_practice_questions_100.md#q55--thinking--circuit-breaker-microservices) · [Q56 · bulkhead-pattern](../system_design_practice_questions_100.md#q56--normal--bulkhead-pattern) · [Q57 · sidecar-pattern](../system_design_practice_questions_100.md#q57--normal--sidecar-pattern) · [Q58 · bff-pattern](../system_design_practice_questions_100.md#q58--design--bff-pattern) · [Q88 · production-cascade-failure](../system_design_practice_questions_100.md#q88--design--production-cascade-failure)

## 📖 Table of Contents

- [1. Start With the Monolith](#start-with-the-monolith)
- [2. The Pain Points That Force the Split](#pain-points)
  - [Deploy Bottleneck](#deploy-bottleneck)
  - [Cannot Scale Parts Independently](#cannot-scale-independently)
  - [One Bug Brings Down Everything](#one-bug-brings-down-everything)
- [3. What is a Microservice](#what-is-a-microservice)
- [4. The Good — Why Teams Make This Move](#the-good)
  - [Independent Deployability](#independent-deployability)
  - [Team Ownership](#team-ownership)
  - [Fault Isolation](#fault-isolation)
  - [Technology Choice (Polyglot)](#technology-choice)
- [5. The Hard Parts — Being Honest](#the-hard-parts)
  - [Network Calls Replace Function Calls](#network-calls-replace-function-calls)
  - [Distributed Transactions are Hard](#distributed-transactions-are-hard)
  - [Operational Complexity Multiplied by N](#operational-complexity)
  - [Data Consistency Across Services](#data-consistency-across-services)
- [6. Service Communication Patterns](#service-communication-patterns)
  - [Synchronous: REST and gRPC](#synchronous-rest-and-grpc)
  - [Asynchronous: Events and Message Queues](#asynchronous-events-and-message-queues)
- [7. Service Discovery](#service-discovery)
  - [DNS-Based Discovery (Kubernetes)](#dns-based-discovery)
  - [Service Registry (Consul, Eureka)](#service-registry)
- [8. The API Gateway — One Door In](#api-gateway)
- [9. When NOT to Use Microservices](#when-not-to-use-microservices)
- [10. The Full Picture — Monolith vs Microservices](#the-full-picture)
- [Learning Priority](#learning-priority)
- [Summary](#summary)
- [Navigation](#navigation)

## 📌 Learning Priority

<a id="learning-priority"></a>

**Must Learn** — Core concept, daily use, interview essential:
monolith vs microservices trade-offs · Strangler Fig decomposition pattern · synchronous vs asynchronous communication selection

**Should Learn** — Important for real projects, comes up regularly:
circuit breaker pattern · saga pattern · service discovery · distributed tracing need

**Good to Know** — Useful in specific situations, not always tested:
API gateway role · Conway's Law implications

**Reference** — Know it exists, look up syntax when needed:
service mesh (Istio/Linkerd) · mTLS between services · cost per service (operational overhead)

> [↑ Back to Top](#top)

<a id="start-with-the-monolith"></a>

# 1. Start With the Monolith

Nandu joined a Hyderabad fintech startup three years ago. The entire product — payments, user management, KYC, notifications — lived in one Django app. One repo, one deploy, one database. The team of eight engineers shipped features in days. Debugging was a single stack trace. Life was simple. Then the company grew to 80 engineers, and Nandu became the tech lead tasked with breaking things apart. But first, he tells every new hire the same thing:

**A monolith is not a mistake. It's a starting point.**

Every company that runs microservices today started with something simpler. Amazon ran a monolith. Netflix ran a monolith. Shopify largely still does, at enormous scale.

The monolith is easy to understand, easy to debug, easy to deploy, and easy to develop on when your team is small. It lets you move fast when you're still figuring out what to build.

```
The Monolith — everything in one deployable unit:

    ┌────────────────────────────────────────────┐
    │               YOUR APP                     │
    │                                            │
    │   [User Service]  [Order Service]          │
    │   [Payment Logic] [Email Sender]           │
    │   [Search]        [Recommendations]        │
    │   [Auth]          [Notifications]          │
    │                                            │
    │   All talking to each other via            │
    │   function calls. One deploy. One DB.      │
    └────────────────────────────────────────────┘
                        |
                        v
                   [One Database]
```

Function calls between modules are fast, transactional, and debuggable with a single stack trace. This is genuinely good.

The monolith becomes a problem at scale — not before.

> [↑ Back to Top](#top)

<a id="pain-points"></a>

# 2. The Pain Points That Force the Split

At some point, if your company grows, you start feeling real pain. Not theoretical pain. Real, daily, "this is slowing us down" pain. Nandu felt all three of these before he proposed the split to his CTO.

<a id="deploy-bottleneck"></a>

## Deploy Bottleneck

You have 100 engineers. The payment team fixes a one-line bug. To ship it, they have to:

1. Wait for all 100 engineers' in-progress changes to be tested.
2. Coordinate a deploy window.
3. Run 2 hours of integration tests on the entire app.
4. Deploy the whole thing and hope nothing unrelated broke.
5. If it breaks, rollback affects everyone.

```
100 engineers x their changes --> [One Deploy Pipeline] --> [Production]

                                        ^
                               2 hours. Every time.
                               For a one-line fix.
```

The monolith serializes deployments. As team size grows, this becomes unbearable.

<a id="cannot-scale-independently"></a>

## Cannot Scale Parts Independently

Black Friday is coming. Your payment processing load will be 10x normal. Your user profile page won't change at all.

```
MONOLITH SCALING:
    You must scale the entire application
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  10x of:     │  │  10x of:     │  │  10x of:     │
    │  Payments    │  │  Payments    │  │  Payments    │
    │  Profiles    │  │  Profiles    │  │  Profiles    │
    │  Search      │  │  Search      │  │  Search      │
    │  Everything  │  │  Everything  │  │  Everything  │
    └──────────────┘  └──────────────┘  └──────────────┘
    <-- expensive and wasteful -->
```

You're paying to scale code that doesn't need scaling, because it's bundled with code that does.

<a id="one-bug-brings-down-everything"></a>

## One Bug Brings Down Everything

Your recommendations engine has a memory leak. It crashes. In a monolith, the whole app crashes.

```
    [Checkout]  [Payments]  [User Auth]  [Recommendations <-- MEMORY LEAK]
         |            |           |                  |
         +------------+-----------+------------------+
                            |
                     CRASH. Entire app down.
                     Checkout is down.
                     Payments are down.
                     Because of a recommendations bug.
```

These three pain points are the real forcing function for microservices. Not architecture fashion. Nandu's team was experiencing all three — deploys took 3 hours, the payment module couldn't scale independently during salary days, and a notification queue bug crashed the entire platform twice in one month.

> [↑ Back to Top](#top)

<a id="what-is-a-microservice"></a>

# 3. What is a Microservice

Nandu explains it to new hires like this: "Think of our old monolith as a single kitchen where 80 cooks share one stove, one fridge, and one sink. A microservice is giving each team their own kitchen. They cook whatever they want, clean their own dishes, and serve through a window. They don't reach into each other's fridges."

A microservice is a service that:

1. **Does one thing well** — user authentication, payment processing, sending emails. One bounded domain.
2. **Owns its own data** — it has its own database. No other service reads its DB directly.
3. **Deploys independently** — you can ship it without touching any other service.
4. **Communicates over the network** — via HTTP, gRPC, or a message queue.

```
MICROSERVICES:

    [User Service]        [Order Service]         [Payment Service]
         |                      |                        |
    [Users DB]             [Orders DB]             [Payments DB]
                                ^                        ^
                        each owns its own data, deploys independently
```

The key principle is **bounded context**: each service is responsible for one domain and that domain only.

> [↑ Back to Top](#top)

<a id="the-good"></a>

# 4. The Good — Why Teams Make This Move

Once Nandu's team extracted the first service (payments), the benefits became obvious within weeks. The payment team shipped four times in one week without coordinating with anyone else. Here's why teams make this move:

<a id="independent-deployability"></a>

## Independent Deployability

The payment team ships whenever they want. The recommendations team ships whenever they want. No coordination. No waiting.

```
Monday:   [Payment Service v2.1 deployed]  --> others unaffected
Tuesday:  [Search Service v1.8 deployed]   --> others unaffected
Wednesday:[Auth Service v3.0 deployed]     --> others unaffected
```

<a id="team-ownership"></a>

## Team Ownership

Conway's Law: your architecture mirrors your org chart. Microservices make this explicit.

- Team A owns User Service. They are responsible for it, on-call for it, and can evolve it.
- Team B owns Payment Service. Same deal.
- No one needs permission from another team to deploy their own service.

<a id="fault-isolation"></a>

## Fault Isolation

```
Recommendations service crashes?

    [Checkout]  still works
    [Payments]  still works
    [User Auth] still works
    [Recommendations] down — but it's isolated

    Result: checkout still works, just without personalized recommendations.
            Degrade gracefully rather than fully fail.
```

<a id="technology-choice"></a>

## Technology Choice (Polyglot)

Each service can use the language and database best suited for its job.

| Service | Language | Database | Why |
|---------|----------|----------|-----|
| ML inference | Python | Redis | Rich ML ecosystem |
| Low-latency order matching | Go | PostgreSQL | Concurrency model |
| Search | Java | Elasticsearch | Full-text search |
| Payment | Java | PostgreSQL | Enterprise tooling |

No one forces you to use the same tech stack across everything.

> [↑ Back to Top](#top)

<a id="the-hard-parts"></a>

# 5. The Hard Parts — Being Honest

Nandu learned these lessons the hard way. After the initial excitement of the first service extraction, reality hit. "We traded compile-time errors for runtime errors," he tells his team. "We traded function calls for network calls. We traded database transactions for eventual consistency. Every one of those trades has a cost."

This is where most tutorials get soft. Microservices have **real costs**. Do not move to them without understanding these.

<a id="network-calls-replace-function-calls"></a>

## Network Calls Replace Function Calls

In a monolith, calling another module is a function call. It takes nanoseconds. It cannot fail mid-way.

In microservices, calling another service is a network call. It takes milliseconds. It can fail. It can time out. It can partially succeed.

```
MONOLITH:
    checkout() {
        price = inventory.getPrice(item_id)   <-- 0.001ms, never fails
    }

MICROSERVICES:
    checkout() {
        price = http.get("inventory-service/price/" + item_id)
                                               <-- 5ms on a good day
                                               <-- timeout after 30s on a bad day
                                               <-- 500 error if service is down
                                               <-- connection refused if it's deploying
    }
```

Every inter-service call needs retry logic, timeout handling, and circuit breakers. This code has to be written, tested, and maintained.

<a id="distributed-transactions-are-hard"></a>

## Distributed Transactions are Hard

In a monolith, you wrap things in a database transaction:

```sql
BEGIN TRANSACTION
    UPDATE inventory SET quantity = quantity - 1 WHERE item_id = 42
    INSERT INTO orders (user_id, item_id) VALUES (1, 42)
    UPDATE user_credits SET credits = credits - 10 WHERE user_id = 1
COMMIT — or ROLLBACK everything
```

In microservices, these three steps live in three different databases. There is no single transaction that spans them.

```
Deduct inventory (Inventory Service DB)
    |
    v
Create order (Order Service DB)
    |
    v
Deduct credits (User Service DB)

If "Deduct credits" fails:
    - Inventory already decremented  [inconsistent]
    - Order already created          [inconsistent]
    - Credits never deducted         [correct]

    --> System is inconsistent. What do you do?
```

You need Sagas (Chapter 11). Sagas work, but they're significantly more complex than a database transaction. The code to handle failure, compensation, and idempotency is not trivial.

**Common Mistake:** Trying to implement distributed two-phase commit across microservices. It doesn't scale, introduces tight coupling, and defeats the purpose of independent services. Use Sagas with compensating transactions instead.

<a id="operational-complexity"></a>

## Operational Complexity Multiplied by N

One monolith: one set of logs, one set of metrics, one deployment.

Ten microservices: ten sets of logs (in ten different places), ten sets of metrics, ten deployments, ten on-call runbooks.

```
MONOLITH ops:                      10 MICROSERVICES ops:
    - 1 log stream                     - 10 log streams (aggregated somewhere?)
    - 1 deployment pipeline            - 10 deployment pipelines
    - 1 health check endpoint          - 10 health check endpoints
    - 1 runbook                        - 10 runbooks
    - 1 on-call rotation item          - 10 things that can page you at 3am
```

"A request is failing" — which of the 10 services is broken? You need distributed tracing (Chapter 14) just to answer that question.

<a id="data-consistency-across-services"></a>

## Data Consistency Across Services

Each service owns its own data. Service A cannot query Service B's database. So how does Service A know about data that lives in Service B?

```
Question: "Show me all orders with the buyer's name and shipping address."

Order Service knows: order_id, item, price
User Service knows: user_id, name, address

MONOLITH: one JOIN query

MICROSERVICES:
    Option 1: Order Service calls User Service API at query time
              (adds latency, coupling)
    Option 2: Order Service caches a copy of user data
              (eventual consistency problem)
    Option 3: Denormalized read model that aggregates both
              (CQRS, Chapter 11)
```

None of these are as simple as a JOIN. Pick your complexity.

**Common Mistake:** Sharing a database between services "just for reads." This creates hidden coupling — schema changes in one service break others. Each service must own its data completely.

> [↑ Back to Top](#top)

<a id="service-communication-patterns"></a>

# 6. Service Communication Patterns

Nandu's team had to make this decision early: when Service A needs something from Service B, should it call and wait (synchronous), or drop a message and move on (asynchronous)? The answer depends on whether the caller needs an immediate response.

<a id="synchronous-rest-and-grpc"></a>

## Synchronous: REST and gRPC

The caller makes a request and waits for a response.

```
[Order Service] --HTTP GET--> [Inventory Service]
                <--200 OK, stock: 5--
    (waits here)                (responds here)
```

- **Simple and familiar** — like calling a function, but over the network.
- **Tightly coupled** — if Inventory Service is down, Order Service is blocked.
- **Latency adds up** — a chain of 5 synchronous calls = 5x the latency.

Use for: user-facing requests that need an immediate answer.

**gRPC** is like REST but uses binary encoding (Protocol Buffers) instead of JSON. Faster, more efficient, better for service-to-service internal calls.

| Feature | REST (JSON) | gRPC (Protobuf) |
|---------|-------------|-----------------|
| Encoding | Text (JSON) | Binary (Protobuf) |
| Speed | Slower | Faster |
| Streaming | Limited | Built-in bidirectional |
| Browser support | Native | Needs proxy (grpc-web) |
| Best for | External APIs | Internal service-to-service |

<a id="asynchronous-events-and-message-queues"></a>

## Asynchronous: Events and Message Queues

The caller publishes an event and moves on. Other services consume it when ready.

```
[Order Service] --publishes "order_placed"--> [Message Queue]
                                                      |
                              +-------------------+---+-------------------+
                              |                   |                       |
                    [Inventory Service]   [Email Service]    [Analytics Service]
                    (consumes, adjusts    (consumes, sends   (consumes, logs)
                     stock levels)         confirmation)
```

- **Decoupled** — Order Service doesn't know or care about the others.
- **Fault tolerant** — if Email Service is down, the message waits in the queue.
- **Eventually consistent** — Email Service will process the event eventually, not necessarily immediately.

Use for: side effects, notifications, anything that doesn't need an immediate response.

```
DECISION FLOW — Sync vs Async:

    Does the caller need an immediate response?
        |
        +-- YES --> Use synchronous (REST/gRPC)
        |           Example: "What's the current price?"
        |
        +-- NO  --> Use asynchronous (events/queues)
                    Example: "Send a confirmation email"
                    Example: "Update analytics counters"
```

> [↑ Back to Top](#top)

<a id="service-discovery"></a>

# 7. Service Discovery

Nandu's team deployed 12 services to Kubernetes. Each service has 3 replicas. Instances get replaced when they crash or scale up. Their IP addresses change constantly. "How does Order Service know where Payment Service is right now?" asked a junior engineer. Nandu smiled — this is the service discovery problem.

You have 50 microservices. Each has multiple instances. Instances get replaced when they crash or when you deploy. Their IP addresses change constantly.

How does the Order Service know where to send requests?

<a id="dns-based-discovery"></a>

## DNS-Based Discovery (Kubernetes)

Kubernetes assigns a stable DNS name to every service.

```
    order-service.default.svc.cluster.local:8080

    <-- This DNS name always resolves to healthy instances.
    <-- Kubernetes load balances automatically.
    <-- You don't manage IP addresses. You use the DNS name.
```

This is the default in Kubernetes and it's excellent. Most teams using Kubernetes don't need to think about this.

<a id="service-registry"></a>

## Service Registry (Consul, Eureka)

For non-Kubernetes environments, a service registry is a central directory.

```
Service Startup:
    [Inventory Service, IP: 10.0.1.5, port: 8080]
            |
            v
    registers itself with [Consul / Service Registry]

Service Discovery:
    [Order Service] --> "where is inventory-service?" --> [Consul]
                   <-- "10.0.1.5:8080, 10.0.1.6:8080" <--
                   --> picks one, makes request
```

Services register on startup and deregister on shutdown. The registry provides health checks and load-balanced addresses.

| Approach | When to Use | Examples |
|----------|-------------|---------|
| DNS-based (K8s) | Already on Kubernetes | CoreDNS, kube-dns |
| Service registry | VM-based or hybrid | Consul, Eureka, Zookeeper |
| Config-based | Very small setups | Environment variables, config files |

> [↑ Back to Top](#top)

<a id="api-gateway"></a>

# 8. The API Gateway — One Door In

Nandu's mobile team complained first: "We have to call 6 different services to render the home screen. Six different auth checks. Six different error formats. Six different URLs to manage." The API Gateway was the answer — one door in, consistent behavior.

Clients (web, mobile, third-party) should not call 20 microservices directly. You'd need to know each service's address, handle auth for each, deal with CORS for each. It's chaos.

The API Gateway is a single entry point.

```
                       [Mobile App]  [Web Browser]  [Partner API]
                              \            |            /
                               \           |           /
                                v          v          v
                          +------------------------------+
                          |         API GATEWAY          |
                          |  - authentication            |
                          |  - rate limiting             |
                          |  - request routing           |
                          |  - SSL termination           |
                          |  - response aggregation      |
                          +-------------+----------------+
                                        |
                    +-------------------+--------------------+
                    |                   |                     |
          [User Service]      [Order Service]      [Payment Service]
```

The gateway handles cross-cutting concerns (auth, rate limiting, logging) once, centrally, rather than each service implementing them.

| Gateway | Type | Best For |
|---------|------|----------|
| Kong | Open source / enterprise | Full-featured, plugin ecosystem |
| AWS API Gateway | Managed | AWS-native workloads |
| Nginx | Open source | Simple routing, high performance |
| Envoy | Open source | Service mesh sidecar, L7 proxy |
| Traefik | Open source | Kubernetes-native, auto-discovery |

**Common Mistake:** Putting business logic in the API Gateway. It should handle cross-cutting concerns only (auth, rate limiting, routing). Business logic belongs in the services.

> [↑ Back to Top](#top)

<a id="when-not-to-use-microservices"></a>

# 9. When NOT to Use Microservices

Nandu is blunt about this: "If someone on your team is excited about microservices but your startup has 8 engineers and hasn't found product-market fit, stop them. They're solving an organizational scaling problem you don't have yet." The industry does not say this enough.

**Do not use microservices if:**

- You have fewer than 20 engineers. The operational overhead will consume your team.
- You haven't shipped version 1 yet. You don't know your domain boundaries. You'll draw the wrong lines and create a distributed monolith (worst of both worlds).
- Your team doesn't have strong DevOps/platform engineering skills. Microservices require CI/CD pipelines, container orchestration, distributed tracing, centralized logging, service mesh. That's a lot of infrastructure to build and maintain.
- You're not experiencing the pain points described earlier. "Best practice" is not a reason.

```
Signs you're NOT ready:                    Signs you MIGHT be ready:
    x Monolith deploys < 15 mins               + Deploys take hours, block teams
    x Fewer than 5 teams                       + Clear domain boundaries
    x No Kubernetes or similar                  + Dedicated platform/SRE team
    x No distributed tracing                   + Strong CI/CD, monitoring, tracing
    x Engineers not comfortable with Docker     + Parts need independent scaling
    x No clear service boundaries from pain    + Pain is real, daily, measurable
```

The **Strangler Fig** pattern is the pragmatic way to migrate: don't rewrite the monolith from scratch. Extract one service at a time, routing its traffic away from the monolith, until the monolith is gone. This takes years at large companies. That's normal.

```
STRANGLER FIG — Nandu's approach:

    Year 1: Extract Payment Service (highest pain, clearest boundary)
             Monolith still handles everything else.
             Proxy routes /payments/* to new service.

    Year 2: Extract Notification Service, User Service
             Monolith shrinks but still runs.

    Year 3: Extract remaining services one by one.
             Eventually the monolith is empty — delete it.

    Key: At every step, both old and new code work.
         No big-bang rewrite. No "turn off the monolith" day.
```

> [↑ Back to Top](#top)

<a id="the-full-picture"></a>

# 10. The Full Picture — Monolith vs Microservices

Nandu keeps this comparison table on the team wiki. Every engineer who proposes a new service must read it first and explain which benefits they expect and which costs they accept.

```
MONOLITH                          MICROSERVICES

+ Simple to develop               + Independent deployability
+ Simple to debug                 + Team ownership
+ ACID transactions               + Fault isolation
+ Fast internal calls             + Independent scaling
+ Easy to onboard new devs        + Technology flexibility
+ One deploy
                                  - Network calls (latency + failure)
- Scales as one unit              - No distributed transactions
- One bug can crash all           - Operational complexity
- Deploys block all teams         - Data consistency challenges
- Long build/test cycles          - Service discovery needed
- Hard to scale teams on it       - Requires strong DevOps culture
```

Neither is universally better. The right answer depends on your team size, domain complexity, and operational maturity.

| Factor | Favor Monolith | Favor Microservices |
|--------|---------------|---------------------|
| Team size | < 20 engineers | > 50 engineers |
| Domain clarity | Still exploring | Well-understood boundaries |
| Deploy frequency | Weekly is fine | Multiple times daily needed |
| Scale requirements | Uniform load | Highly variable per component |
| Ops maturity | Basic CI/CD | K8s, tracing, service mesh |

> [↑ Back to Top](#top)

<a id="summary"></a>

## 🔥 Summary

| Concept | Key Takeaway |
|---------|--------------|
| Monolith first | Start simple. Split only when pain is real and measurable. |
| Pain points | Deploy bottleneck, can't scale independently, blast radius too wide. |
| Microservice definition | One domain, own data, independent deploy, network communication. |
| Benefits | Independent deploys, team ownership, fault isolation, polyglot. |
| Costs | Network failures, distributed transactions, operational complexity. |
| Sync communication | REST/gRPC — caller waits. Use for immediate-response needs. |
| Async communication | Events/queues — fire and forget. Use for side effects. |
| Service discovery | K8s DNS or service registry (Consul/Eureka). |
| API Gateway | Single entry point for auth, routing, rate limiting. |
| When NOT to split | < 20 engineers, no K8s, no tracing, no real pain. |
| Strangler Fig | Extract services one at a time. No big-bang rewrites. |

> [↑ Back to Top](#top)

<a id="navigation"></a>

## 📂 Navigation

| | |
|---|---|
| [Back to README](../README.md) | Home |

| Direction | Link |
|-----------|------|
| Previous | [11 — Scalability Patterns](../11_scalability_patterns/theory.md) |
| Next | [13 — Security](../13_security/theory.md) |

**This folder:** [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:** [09 — Message Queues](../09_message_queues/theory.md) · [10 — Distributed Systems](../10_distributed_systems/theory.md) · [11 — Scalability Patterns](../11_scalability_patterns/theory.md) · [14 — Observability](../14_observability/theory.md)

**Jump to:** [Monolith](#start-with-the-monolith) · [Pain Points](#pain-points) · [Communication](#service-communication-patterns) · [Discovery](#service-discovery) · [Gateway](#api-gateway) · [When NOT](#when-not-to-use-microservices)
