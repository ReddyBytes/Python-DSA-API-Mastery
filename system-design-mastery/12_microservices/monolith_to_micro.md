# 12 — Monolith to Microservices

---

## Start With the Monolith. Seriously.

Before we talk about splitting things apart, let's be clear about something that often gets lost in the hype:

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

---

## The Pain Points That Force the Split

At some point, if your company grows, you start feeling real pain. Not theoretical pain. Real, daily, "this is slowing us down" pain.

### Pain Point 1: The Deploy Bottleneck

You have 100 engineers. The payment team fixes a one-line bug. To ship it, they have to:

1. Wait for all 100 engineers' in-progress changes to be tested.
2. Coordinate a deploy window.
3. Run 2 hours of integration tests on the entire app.
4. Deploy the whole thing and hope nothing unrelated broke.
5. If it breaks, rollback affects everyone.

```
100 engineers × their changes → [One Deploy Pipeline] → [Production]

                                        ↑
                               2 hours. Every time.
                               For a one-line fix.
```

The monolith serializes deployments. As team size grows, this becomes unbearable.

### Pain Point 2: You Can't Scale Parts Independently

Black Friday is coming. Your payment processing load will be 10× normal. Your user profile page won't change at all.

```
MONOLITH SCALING:
    You must scale the entire application
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  10× of:     │  │  10× of:     │  │  10× of:     │
    │  Payments    │  │  Payments    │  │  Payments    │
    │  Profiles    │  │  Profiles    │  │  Profiles    │
    │  Search      │  │  Search      │  │  Search      │
    │  Everything  │  │  Everything  │  │  Everything  │
    └──────────────┘  └──────────────┘  └──────────────┘
    ← expensive and wasteful →
```

You're paying to scale code that doesn't need scaling, because it's bundled with code that does.

### Pain Point 3: One Bug Brings Down Everything

Your recommendations engine has a memory leak. It crashes. In a monolith, the whole app crashes.

```
    [Checkout]  [Payments]  [User Auth]  [Recommendations ← MEMORY LEAK]
         |            |           |                  |
         +------------+-----------+------------------+
                            |
                     CRASH. Entire app down.
                     Checkout is down.
                     Payments are down.
                     Because of a recommendations bug.
```

These three pain points are the real forcing function for microservices. Not architecture fashion.

---

## What is a Microservice?

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
                                ↑                        ↑
                        each owns its own data, deploys independently
```

The key principle is **bounded context**: each service is responsible for one domain and that domain only.

---

## The Good: Why Teams Make This Move

### Independent Deployability

The payment team ships whenever they want. The recommendations team ships whenever they want. No coordination. No waiting.

```
Monday:   [Payment Service v2.1 deployed]  → others unaffected
Tuesday:  [Search Service v1.8 deployed]   → others unaffected
Wednesday:[Auth Service v3.0 deployed]     → others unaffected
```

### Team Ownership

Conway's Law: your architecture mirrors your org chart. Microservices make this explicit.

- Team A owns User Service. They are responsible for it, on-call for it, and can evolve it.
- Team B owns Payment Service. Same deal.
- No one needs permission from another team to deploy their own service.

### Fault Isolation

```
Recommendations service crashes?

    [Checkout]  ✓ still works
    [Payments]  ✓ still works
    [User Auth] ✓ still works
    [Recommendations] ✗ down — but it's isolated

    Result: checkout still works, just without personalized recommendations.
            Degrade gracefully rather than fully fail.
```

### Technology Choice (Polyglot)

Each service can use the language and database best suited for its job.

- ML inference service: Python
- Low-latency order matching: Go
- Search service: Elasticsearch
- Payment service: Java with PostgreSQL

No one forces you to use the same tech stack across everything.

---

## The Hard Parts — Being Honest

This is where most tutorials get soft. Microservices have **real costs**. Do not move to them without understanding these.

### Network Calls Replace Function Calls

In a monolith, calling another module is a function call. It takes nanoseconds. It cannot fail mid-way.

In microservices, calling another service is a network call. It takes milliseconds. It can fail. It can time out. It can partially succeed.

```
MONOLITH:
    checkout() {
        price = inventory.getPrice(item_id)   ← 0.001ms, never fails
    }

MICROSERVICES:
    checkout() {
        price = http.get("inventory-service/price/" + item_id)
                                               ← 5ms on a good day
                                               ← timeout after 30s on a bad day
                                               ← 500 error if service is down
                                               ← connection refused if it's deploying
    }
```

Every inter-service call needs retry logic, timeout handling, and circuit breakers. This code has to be written, tested, and maintained.

### Distributed Transactions are Hard

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
    ↓
Create order (Order Service DB)
    ↓
Deduct credits (User Service DB)

If "Deduct credits" fails:
    - Inventory already decremented ✗
    - Order already created ✗
    - Credits never deducted ✓

    → System is inconsistent. What do you do?
```

You need Sagas (Chapter 11). Sagas work, but they're significantly more complex than a database transaction. The code to handle failure, compensation, and idempotency is not trivial.

### Operational Complexity Multiplied by N

One monolith: one set of logs, one set of metrics, one deployment.

Ten microservices: ten sets of logs (in ten different places), ten sets of metrics, ten deployments, ten on-call runbooks.

```
MONOLITH ops:
    - 1 log stream
    - 1 deployment pipeline
    - 1 health check endpoint
    - 1 runbook
    - 1 on-call rotation item

10 MICROSERVICES ops:
    - 10 log streams (aggregated somewhere?)
    - 10 deployment pipelines
    - 10 health check endpoints
    - 10 runbooks
    - 10 things that can page you at 3am
```

"A request is failing" — which of the 10 services is broken? You need distributed tracing (Chapter 14) just to answer that question.

### Data Consistency Across Services

Each service owns its own data. Service A cannot query Service B's database. So how does Service A know about data that lives in Service B?

```
Question: "Show me all orders with the buyer's name and shipping address."

Order Service knows: order_id, item, price
User Service knows: user_id, name, address

MONOLITH: one JOIN query
MICROSERVICES:
    Option 1: Order Service calls User Service API at query time (adds latency, coupling)
    Option 2: Order Service caches a copy of user data (eventual consistency problem)
    Option 3: Denormalized read model that aggregates both (CQRS, Chapter 11)
```

None of these are as simple as a JOIN. Pick your complexity.

---

## Service Communication Patterns

### Synchronous: REST and gRPC

The caller makes a request and waits for a response.

```
[Order Service] ──HTTP GET──▶ [Inventory Service]
                ◀──200 OK, stock: 5──
    (waits here)                (responds here)
```

- **Simple and familiar** — like calling a function, but over the network.
- **Tightly coupled** — if Inventory Service is down, Order Service is blocked.
- **Latency adds up** — a chain of 5 synchronous calls = 5× the latency.

Use for: user-facing requests that need an immediate answer.

**gRPC** is like REST but uses binary encoding (Protocol Buffers) instead of JSON. Faster, more efficient, better for service-to-service internal calls.

### Asynchronous: Events and Message Queues

The caller publishes an event and moves on. Other services consume it when ready.

```
[Order Service] ──publishes "order_placed"──▶ [Message Queue]
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

---

## Service Discovery — How Does Service A Find Service B?

You have 50 microservices. Each has multiple instances. Instances get replaced when they crash or when you deploy. Their IP addresses change constantly.

How does the Order Service know where to send requests?

### DNS-Based Discovery (Kubernetes)

Kubernetes assigns a stable DNS name to every service.

```
    order-service.default.svc.cluster.local:8080

    ← This DNS name always resolves to healthy instances.
    ← Kubernetes load balances automatically.
    ← You don't manage IP addresses. You use the DNS name.
```

This is the default in Kubernetes and it's excellent. Most teams using Kubernetes don't need to think about this.

### Service Registry (Consul, Eureka)

For non-Kubernetes environments, a service registry is a central directory.

```
Service Startup:
    [Inventory Service, IP: 10.0.1.5, port: 8080]
            |
            v
    registers itself with [Consul / Service Registry]

Service Discovery:
    [Order Service] → "where is inventory-service?" → [Consul]
                   ← "10.0.1.5:8080, 10.0.1.6:8080" ←
                   → picks one, makes request
```

Services register on startup and deregister on shutdown. The registry provides health checks and load-balanced addresses.

---

## The API Gateway — One Door In

Clients (web, mobile, third-party) should not call 20 microservices directly. You'd need to know each service's address, handle auth for each, deal with CORS for each. It's chaos.

The API Gateway is a single entry point.

```
                           [Mobile App]  [Web Browser]  [Partner API]
                                  \            |            /
                                   \           |           /
                                    v          v          v
                              ┌──────────────────────────────┐
                              │         API GATEWAY          │
                              │  - authentication            │
                              │  - rate limiting             │
                              │  - request routing           │
                              │  - SSL termination           │
                              │  - response aggregation      │
                              └──────────┬───────────────────┘
                                         |
                    +--------------------+--------------------+
                    |                   |                     |
          [User Service]      [Order Service]      [Payment Service]
```

The gateway handles cross-cutting concerns (auth, rate limiting, logging) once, centrally, rather than each service implementing them.

Common API gateways: Kong, AWS API Gateway, Nginx, Envoy, Traefik.

---

## When NOT to Use Microservices

This deserves its own section. The industry does not say this enough.

**Do not use microservices if:**

- You have fewer than 20 engineers. The operational overhead will consume your team.
- You haven't shipped version 1 yet. You don't know your domain boundaries. You'll draw the wrong lines and create a distributed monolith (worst of both worlds).
- Your team doesn't have strong DevOps/platform engineering skills. Microservices require CI/CD pipelines, container orchestration, distributed tracing, centralized logging, service mesh. That's a lot of infrastructure to build and maintain.
- You're not experiencing the pain points described earlier. "Best practice" is not a reason.

```
Signs you're not ready for microservices:
    ✗ Your monolith is still fast to deploy (< 15 mins)
    ✗ You have < 5 teams
    ✗ You don't have Kubernetes or similar orchestration
    ✗ You don't have distributed tracing (Jaeger, etc.)
    ✗ Your engineers aren't already comfortable with Docker
    ✗ You haven't identified clear service boundaries from real pain

Signs you might be ready:
    ✓ Deploys take hours and block many teams
    ✓ You have clear domain boundaries that rarely change
    ✓ You have dedicated platform/SRE team
    ✓ You have strong CI/CD, monitoring, and tracing in place
    ✓ Specific parts need to scale independently and can't
```

The "Strangler Fig" pattern is the pragmatic way to migrate: don't rewrite the monolith from scratch. Extract one service at a time, routing its traffic away from the monolith, until the monolith is gone. This takes years at large companies. That's normal.

---

## The Full Picture

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

---

## Navigation

| Direction | Link |
|-----------|------|
| Previous  | [11 — Scalability Patterns](../11_scalability_patterns/patterns_playbook.md) |
| Next      | [13 — Security](../13_security/security_fundamentals.md) |
| Home      | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
