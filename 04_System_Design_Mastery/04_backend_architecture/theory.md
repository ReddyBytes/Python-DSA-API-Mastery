<a id="top"></a>

# Backend Architecture

> Satya stares at his whiteboard. His startup just hit 50,000 users and the monolith
> that served them perfectly for two years is starting to groan. The payment module
> crashed last Tuesday and took down the entire app — user profiles, search, everything.
> His CTO brain knows it is time to think about architecture. But which one? Microservices?
> Event-driven? Serverless? He grabs his chai and starts from first principles.

## Table of Contents

- [1. The Simplest Backend That Could Possibly Work](#1-the-simplest-backend-that-could-possibly-work)
- [2. The Client-Server Model](#2-the-client-server-model)
- [3. What Happens When a Request Arrives](#3-what-happens-when-a-request-arrives)
- [4. Stateless vs Stateful Servers](#4-stateless-vs-stateful-servers)
- [5. The Monolith — Not a Dirty Word](#5-the-monolith--not-a-dirty-word)
- [6. Microservices — The Decomposition](#6-microservices--the-decomposition)
- [7. Monolith vs Microservices Deep Comparison](#7-monolith-vs-microservices-deep-comparison)
- [8. Layered Architecture](#8-layered-architecture)
- [9. Event-Driven Architecture](#9-event-driven-architecture)
- [10. Serverless Architecture](#10-serverless-architecture)
- [11. CQRS — Command Query Responsibility Segregation](#11-cqrs--command-query-responsibility-segregation)
- [12. Architecture Decision Framework](#12-architecture-decision-framework)
- [13. Real-World Evolution Stories](#13-real-world-evolution-stories)
- [14. The Request Lifecycle in a Real Backend](#14-the-request-lifecycle-in-a-real-backend)
- [15. Connection Pools](#15-connection-pools)
- [16. Synchronous vs Asynchronous Processing](#16-synchronous-vs-asynchronous-processing)
- [17. Key Numbers for a Single Server](#17-key-numbers-for-a-single-server)
- [18. Common Mistakes](#18-common-mistakes)
- [19. Summary](#19-summary)

[Back to Top](#top)

<a id="1-the-simplest-backend-that-could-possibly-work"></a>

## 1. The Simplest Backend That Could Possibly Work

Satya remembers his first day. He opened his laptop and wrote:

```python
from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/ping")
def ping():
    return jsonify({"status": "ok"})

app.run(port=8080)
```

That is a backend. A process, listening on a port, responding to HTTP.

Everything else — load balancers, databases, caches, queues, Kubernetes — is what
you ADD when this simple thing is no longer enough. Satya kept this running for his
first 100 users. It was beautiful in its simplicity.

[Back to Top](#top)

<a id="2-the-client-server-model"></a>

## 2. The Client-Server Model

Every web system is built on one fundamental idea:

```
+----------------+           +------------------------------------+
|    Client      |           |             Server                 |
|                |  Request  |                                    |
|  Browser       | --------->|  Receives request                  |
|  Mobile app    |           |  Does some work (logic + data)     |
|  Another API   | <---------|  Returns response                  |
|                |  Response |                                    |
+----------------+           +------------------------------------+
```

**Client**: whoever sends the request (browser, mobile app, another service).
**Server**: whoever receives it, processes it, responds.

The client knows the server's address (URL). The server does not know the client exists until it gets a request. This asymmetry is the foundation of all backend architecture.

[Back to Top](#top)

<a id="3-what-happens-when-a-request-arrives"></a>

## 3. What Happens When a Request Arrives

Satya traces `GET /users/42` hitting his server:

```
1. TCP connection established
   -> OS kernel accepts the connection
   -> Hands socket to your process

2. HTTP parsing
   -> Framework reads: method=GET, path=/users/42, headers=...

3. Routing
   -> Framework finds: "for GET /users/{id}, call get_user()"

4. Business logic (your code)
   -> Validate id
   -> Query database: SELECT * FROM users WHERE id = 42

5. Database I/O
   -> Connection pool picks an available connection
   -> Query sent to DB (network call: ~1ms)
   -> Results returned as rows

6. Serialization
   -> Python dict -> JSON bytes

7. HTTP response written
   -> Status 200, headers, body

8. TCP connection kept alive or closed
```

**Total time:** typically 5-50ms for a simple DB-backed endpoint.

[Back to Top](#top)

<a id="4-stateless-vs-stateful-servers"></a>

## 4. Stateless vs Stateful Servers

This is one of the most important decisions in backend design. Satya learned this
the hard way when his single server crashed and all logged-in users lost their sessions.

**Stateful server:**

```
Client A -> Server (remembers Client A's session in memory)
Client B -> Server (remembers Client B's session in memory)

Problem:
  Client A sends request 1 -> Server 1 (stores session)
  Client A sends request 2 -> Server 2 (session not found!)

  If you add more servers, sessions are tied to ONE server.
  Server crash = all sessions lost.
```

**Stateless server:**

```
Client A -> sends auth token with EVERY request
Server reads token, validates it, doesn't store anything

Client A -> Server 1 -> reads token -> OK
Client A -> Server 2 -> reads token -> OK
Client A -> Server 3 -> reads token -> OK

Any server can handle any request!
-> Horizontal scaling becomes trivial
-> Server crash loses nothing
-> Load balancer can route freely
```

**Rule:** Make your servers stateless. Store state in:
- Database (persistent state: user data, orders)
- Cache like Redis (session state: shopping cart, rate limit counters)
- The client itself (JWT tokens are stateless auth)

[Back to Top](#top)

<a id="5-the-monolith--not-a-dirty-word"></a>

## 5. The Monolith — Not a Dirty Word

Satya's startup began as a monolith. A single deployable unit that handles everything.

```
+--------------------------------------------------+
|                    Monolith                       |
|                                                  |
|  +----------+  +----------+  +--------------+   |
|  |  User    |  |  Order   |  |  Payment     |   |
|  |  Module  |  |  Module  |  |  Module      |   |
|  +----------+  +----------+  +--------------+   |
|                                                  |
|  +----------+  +----------+  +--------------+   |
|  |  Search  |  |  Notif.  |  |  Analytics   |   |
|  |  Module  |  |  Module  |  |  Module      |   |
|  +----------+  +----------+  +--------------+   |
|                                                  |
|  Single codebase, single deploy, one DB          |
+--------------------------------------------------+
         |                        |
    Load Balancer             Database
```

**Monolith advantages:**
- Simple to develop and test
- No network calls between components (function calls instead)
- Easy to debug (one log stream, one process)
- Easy to deploy (one artifact)
- Works well for most companies early on
- Transactions are straightforward (single DB, single process)
- Refactoring is easy (IDE can rename across the whole codebase)

**When monolith struggles:**
- Team grows to 50+ engineers editing the same codebase
- Different parts need different scaling (payment service needs 3x capacity of profile service)
- One part crashes, takes down everything
- Need to deploy one module without deploying everything
- Build times grow to 30+ minutes
- One team's bug blocks another team's release

Satya's monolith served 50,000 users before showing cracks. That is normal. Most startups should start here.

[Back to Top](#top)

<a id="6-microservices--the-decomposition"></a>

## 6. Microservices — The Decomposition

When Satya's payment crash took down the entire app, he decided to extract it. Now
each service runs independently:

```
+----------+    +----------+    +-----------+    +----------+
|  User    |    |  Order   |    |  Payment  |    |  Search  |
|  Service |    |  Service |    |  Service  |    |  Service |
+----+-----+    +----+-----+    +-----+-----+    +----+-----+
     |               |                |                |
     v               v                v                v
+----------+    +----------+    +-----------+    +----------+
| User DB  |    | Order DB |    | Payment DB|    | Search   |
| (Postgres)|   | (Postgres)|   | (Postgres) |   | (Elastic)|
+----------+    +----------+    +-----------+    +----------+
```

Each service:
- Has its own codebase and repo
- Deploys independently
- Can scale independently
- Owns its own data (no shared DB)
- Communicates via APIs or messages

**Microservices advantages:**
- Independent deployment (Payment team ships without waiting for Search team)
- Independent scaling (spin up 10 Payment instances during flash sale)
- Fault isolation (Payment crash does not affect User profiles)
- Technology freedom (Search can use Elasticsearch, Payment uses Postgres)
- Smaller codebases per team (easier to understand)

**Microservices costs:**
- Network calls replace function calls (latency, failures)
- Distributed transactions are hard (no simple ROLLBACK across services)
- Operational complexity (deploy 20 services vs 1)
- Data consistency is eventual, not immediate
- Debugging spans multiple services (need distributed tracing)
- You need DevOps maturity (CI/CD, monitoring, alerting per service)

[Back to Top](#top)

<a id="7-monolith-vs-microservices-deep-comparison"></a>

## 7. Monolith vs Microservices Deep Comparison

Satya creates a decision matrix for his board presentation:

```
+--------------------+---------------------------+---------------------------+
| Dimension          | Monolith                  | Microservices             |
+--------------------+---------------------------+---------------------------+
| Deploy speed       | Slow (whole app)          | Fast (one service)        |
| Deploy risk        | High (blast radius=all)   | Low (blast radius=1 svc) |
| Team autonomy      | Low (everyone in 1 repo)  | High (team owns service)  |
| Scaling            | Vertical or clone whole   | Granular per service      |
| Latency            | Low (in-process calls)    | Higher (network calls)    |
| Data consistency   | Strong (1 DB, ACID)       | Eventual (sagas, events)  |
| Debugging          | Easy (1 process, 1 log)   | Hard (distributed traces) |
| Onboarding devs    | Slow (huge codebase)      | Fast (small codebase)     |
| Infra cost         | Low (fewer machines)      | High (many services)      |
| Ops complexity     | Low                       | Very high                 |
| Time to market     | Fast initially            | Fast at scale             |
+--------------------+---------------------------+---------------------------+
```

**The hidden trade-off Satya discovered:** Microservices trade code complexity for
operational complexity. You write simpler code per service, but you need sophisticated
infrastructure (service mesh, distributed tracing, CI/CD pipelines per service).

**When to stay monolith:**
- Team smaller than 20 engineers
- Product still finding market fit (pivots are expensive in microservices)
- Cannot invest in DevOps tooling
- Traffic below 10,000 requests/second

**When to go microservices:**
- Team larger than 50 engineers across multiple domains
- Need to deploy parts independently (10+ deploys/day target)
- Different parts have wildly different scaling needs
- Fault isolation is a hard requirement (payment cannot take down search)

[Back to Top](#top)

<a id="8-layered-architecture"></a>

## 8. Layered Architecture

Before Satya thinks about microservices, he first organizes code within his monolith.
Layered architecture is how you keep a monolith from becoming a tangled mess.

```
+----------------------------------------------------------+
|                   Presentation Layer                      |
|  (HTTP handlers, request parsing, response formatting)   |
+----------------------------------------------------------+
                          |
                          v
+----------------------------------------------------------+
|                    Business Layer                         |
|  (Domain logic, rules, orchestration, validation)        |
+----------------------------------------------------------+
                          |
                          v
+----------------------------------------------------------+
|                    Data Access Layer                      |
|  (Repositories, ORM queries, DB connection management)   |
+----------------------------------------------------------+
                          |
                          v
+----------------------------------------------------------+
|                      Database                            |
|  (PostgreSQL, MySQL, MongoDB)                            |
+----------------------------------------------------------+
```

**Rules of layered architecture:**
- Each layer only talks to the layer directly below it
- Presentation never talks to the database directly
- Business logic never knows about HTTP or JSON
- Data layer never contains business rules

**Why this matters to Satya:** When he eventually extracts a microservice, the clean
layers mean he can lift the Business + Data layers out of the monolith and wrap them
in a new Presentation layer (API). If his code was tangled (HTTP handlers querying
the DB directly), extraction would be a nightmare.

```python
# BAD: tangled (handler does everything)
@app.route("/orders/<id>/cancel")
def cancel_order(id):
    order = db.execute("SELECT * FROM orders WHERE id = ?", id)
    if order.status == "shipped":
        return {"error": "Cannot cancel shipped order"}, 400
    db.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", id)
    send_email(order.user_email, "Your order was cancelled")
    return {"status": "cancelled"}

# GOOD: layered (each layer has one job)
@app.route("/orders/<id>/cancel")
def cancel_order_handler(id):            # Presentation
    result = order_service.cancel(id)     # -> Business
    return jsonify(result)

class OrderService:                       # Business
    def cancel(self, id):
        order = self.repo.get(id)         # -> Data Access
        if order.status == "shipped":
            raise CannotCancelError()
        order.status = "cancelled"
        self.repo.save(order)
        self.notifier.send_cancellation(order)
        return {"status": "cancelled"}

class OrderRepository:                    # Data Access
    def get(self, id):
        return db.execute("SELECT * FROM orders WHERE id = ?", id)
```

[Back to Top](#top)

<a id="9-event-driven-architecture"></a>

## 9. Event-Driven Architecture

Satya notices a pattern: when an order is placed, five things need to happen — update
inventory, send confirmation email, notify the warehouse, update analytics, and charge
payment. With direct calls, the order service knows about all five downstream systems.
Adding a sixth means changing the order service.

Event-driven flips this: the order service publishes an event, and anyone who cares
subscribes.

```
                     +-------------------+
                     |   Order Service   |
                     +--------+----------+
                              |
                    publishes "OrderPlaced" event
                              |
                              v
+-------------------------------------------------------------+
|                    Event Bus / Broker                        |
|                (Kafka, RabbitMQ, SNS/SQS)                   |
+-----+----------+----------+-----------+----------+----------+
      |          |          |           |          |
      v          v          v           v          v
+---------+ +---------+ +----------+ +-------+ +----------+
|Inventory| |  Email  | |Warehouse | |Analyt.| | Payment  |
| Service | | Service | | Service  | |Service| | Service  |
+---------+ +---------+ +----------+ +-------+ +----------+
```

**Event-driven advantages:**
- Loose coupling (Order service does not know who listens)
- Easy to add new consumers (no code change in producer)
- Natural audit log (events are the history of what happened)
- Better fault isolation (one consumer failing does not block others)
- Enables replay (reprocess events to rebuild state)

**Event-driven challenges:**
- Eventual consistency (event delivery is not instant)
- Debugging is harder (follow the event trail across services)
- Event ordering can be tricky
- Duplicate delivery requires idempotent consumers
- Schema evolution (what happens when event format changes)

**When Satya uses event-driven:**
- Multiple services need to react to the same thing
- You want to decouple teams (producer team does not wait for consumer team)
- Audit trail is a business requirement
- You need to replay history (rebuilding search index, fixing data)

[Back to Top](#top)

<a id="10-serverless-architecture"></a>

## 10. Serverless Architecture

Satya's intern suggests serverless for the image processing pipeline. No servers to
manage, pay only for what you use, auto-scales to zero when idle.

```
+----------+        +-------------+        +-----------+
|  Client  | -----> | API Gateway | -----> |  Lambda   |
+----------+        +-------------+        | Function  |
                                           +-----+-----+
                                                 |
                              +------------------+------------------+
                              |                  |                  |
                              v                  v                  v
                        +-----------+     +-----------+     +-----------+
                        | DynamoDB  |     |    S3     |     |   SQS     |
                        +-----------+     +-----------+     +-----------+

Each function:
  - Runs for max 15 minutes (AWS Lambda)
  - Scales from 0 to 1000+ instances automatically
  - Billed per 100ms of execution time
  - Stateless (no local state between invocations)
```

**Serverless advantages:**
- Zero infrastructure management
- Auto-scales to zero (no cost when idle)
- Pay per execution (great for spiky workloads)
- Forces stateless design (good architectural discipline)
- Rapid prototyping (no Dockerfile, no K8s manifests)

**Serverless limitations:**
- Cold starts (first invocation takes 100ms-2s extra)
- Execution time limits (15 min on AWS Lambda)
- Vendor lock-in (Lambda code is tied to AWS ecosystem)
- Hard to test locally (need emulators)
- Cost becomes expensive at high sustained throughput
- Limited control over runtime environment

**When Satya uses serverless:**
- Spiky, unpredictable traffic (marketing campaign processing)
- Background jobs (image resizing, PDF generation)
- Webhooks and integrations (Slack bot, GitHub webhook handler)
- Early-stage features where traffic is low but uptime matters

**When Satya avoids serverless:**
- Sustained high traffic (cheaper to run containers 24/7)
- Sub-10ms latency requirements (cold starts are unacceptable)
- Long-running processes (video transcoding takes hours)
- Needs WebSocket connections (serverless is request/response)

[Back to Top](#top)

<a id="11-cqrs--command-query-responsibility-segregation"></a>

## 11. CQRS — Command Query Responsibility Segregation

Satya's analytics dashboard queries are killing his write-heavy order database.
Reads and writes have fundamentally different needs. CQRS separates them.

```
Traditional (single model for reads and writes):

  +----------+       +-----------+       +----------+
  |  Client  | ----> |  Service  | ----> | Single   |
  |          | <---- |           | <---- | Database |
  +----------+       +-----------+       +----------+

CQRS (separate models):

  +----------+       +---------------+       +--------------+
  |  Client  | ----> | Command Side  | ----> | Write DB     |
  |  (write) |       | (validates,   |       | (normalized, |
  +----------+       |  applies rules)|      |  ACID)       |
                     +-------+-------+       +------+-------+
                             |                      |
                       publishes event              |
                             |                      v
                             v               +-------------+
                     +---------------+       | Event Store |
                     | Projection    |       +-------------+
                     | (builds read  |
                     |  model)       |
                     +-------+-------+
                             |
                             v
  +----------+       +---------------+       +--------------+
  |  Client  | <---- | Query Side    | <---- | Read DB      |
  |  (read)  |       | (fast lookups)|       | (denormalized|
  +----------+       +---------------+       |  optimized)  |
                                             +--------------+
```

**Why CQRS:**
- Read patterns differ from write patterns (dashboards vs transactions)
- Can optimize read DB for queries (denormalized, pre-computed)
- Can scale read and write sides independently
- Write side stays simple (just validate and store)
- Read side can use different storage (Elasticsearch for search, Redis for hot data)

**When Satya uses CQRS:**
- Read-heavy systems where read patterns differ drastically from write patterns
- Need to scale reads independently (add read replicas for dashboards)
- Complex domain logic on the write side that should not slow down reads
- Event sourcing fits naturally (events bridge the two sides)

**When CQRS is overkill:**
- Simple CRUD applications
- Team is small and cannot maintain two models
- Read and write patterns are similar

[Back to Top](#top)

<a id="12-architecture-decision-framework"></a>

## 12. Architecture Decision Framework

Satya creates a framework for choosing architecture based on company stage:

```
+-------------------------------------------------------------------+
|                  ARCHITECTURE BY STAGE                             |
+-------------------------------------------------------------------+
|                                                                   |
|  STARTUP (1-10 engineers, finding product-market fit)             |
|  +-------------------------------------------------------------+ |
|  | Architecture: Modular Monolith                               | |
|  | Database: Single PostgreSQL                                  | |
|  | Deploy: Single container on managed platform (Railway, ECS)  | |
|  | Reason: Speed of iteration > everything else                 | |
|  | Risk: Tech debt if you succeed (good problem to have)        | |
|  +-------------------------------------------------------------+ |
|                                                                   |
|  SCALE-UP (10-50 engineers, proven product, growing fast)         |
|  +-------------------------------------------------------------+ |
|  | Architecture: Monolith + 2-3 extracted services              | |
|  | Database: Primary DB + specialized stores (Redis, Elastic)   | |
|  | Deploy: Kubernetes with CI/CD                                | |
|  | Reason: Extract only what NEEDS to be independent            | |
|  | Risk: Premature decomposition if you split too early         | |
|  +-------------------------------------------------------------+ |
|                                                                   |
|  ENTERPRISE (50-500 engineers, multiple product lines)            |
|  +-------------------------------------------------------------+ |
|  | Architecture: Microservices with event bus                   | |
|  | Database: Polyglot persistence (each service owns its DB)    | |
|  | Deploy: K8s + service mesh + distributed tracing             | |
|  | Reason: Team autonomy and independent deployability          | |
|  | Risk: Distributed systems complexity (need platform team)    | |
|  +-------------------------------------------------------------+ |
|                                                                   |
|  HYPERSCALE (500+ engineers, global traffic)                      |
|  +-------------------------------------------------------------+ |
|  | Architecture: Domain-driven microservices + CQRS + events    | |
|  | Database: Sharded, multi-region, purpose-built per workload  | |
|  | Deploy: Multi-region K8s with traffic shaping                | |
|  | Reason: Each domain team operates as a mini-company          | |
|  | Risk: Coordination overhead, Conway's Law bites back         | |
|  +-------------------------------------------------------------+ |
+-------------------------------------------------------------------+
```

**Satya's decision checklist:**

1. How many engineers will work on this system in 2 years?
2. What is the deployment frequency target? (daily, hourly, continuous)
3. Do different modules have different scaling needs?
4. Can I afford a platform/DevOps team?
5. Is the product stable or still pivoting?

If the answer to 1 is "fewer than 20" and 5 is "still pivoting" — stay monolith.
If the answer to 1 is "more than 50" and 3 is "yes" — microservices make sense.

[Back to Top](#top)

<a id="13-real-world-evolution-stories"></a>

## 13. Real-World Evolution Stories

Satya studies how the giants did it, because nobody started with microservices.

**Netflix Evolution:**

```
2007: Monolithic Java app on Oracle DB
      - Single deployment, single data center
      - One bad deploy = entire Netflix down

2008: Major database corruption, 3-day outage
      - Lesson: single points of failure are existential threats

2009-2012: Migration to AWS + microservices
      - Gradually extracted services: Account, Recommendations, Streaming
      - Built resilience tools: Hystrix (circuit breaker), Eureka (discovery)
      - Each team owns their service end-to-end

2015+: 700+ microservices, millions of requests/second
      - Chaos Monkey: randomly kills instances in production
      - Each service handles 10K+ requests/sec independently
      - Can deploy hundreds of times per day

Key lesson: Netflix did NOT start with microservices.
They earned the right through scale and pain.
```

**Amazon Decomposition:**

```
2001: Single monolithic C++ application
      - All of amazon.com in one codebase
      - Developer productivity cratering (changes took weeks)

2002: Jeff Bezos "API Mandate" memo:
      1. All teams expose data through service interfaces
      2. Teams communicate only through these interfaces
      3. No other form of inter-process communication allowed
      4. It doesn't matter what technology they use
      5. All service interfaces must be designed to be externalizable
      6. Anyone who doesn't do this will be fired

2003-2006: Gradual decomposition
      - Item catalog became a service
      - Ordering became a service
      - Recommendations became a service
      - Each team: "You build it, you run it"

Result: AWS was born from these internal services
        (S3, SQS, EC2 = internal tools made public)

Key lesson: Organizational structure drove architecture.
Conway's Law in action.
```

**Shopify (Modular Monolith):**

```
2004-2016: Ruby on Rails monolith
      - 2M+ lines of Ruby code
      - 1000+ engineers in ONE codebase
      - Deploys became slow and risky

2016+: Modular monolith (NOT microservices!)
      - Split code into isolated "components" within one deploy
      - Strict boundaries: components can only talk via defined APIs
      - Same process, same DB, but logically separate
      - Can extract to microservice LATER if needed

Key lesson: You can get 80% of microservice benefits
(team boundaries, clear APIs, independent development)
without the operational cost of distributed systems.
```

**What Satya learns:** Start with a modular monolith. Extract to microservices only
when you have proven pain that modular boundaries cannot solve (independent scaling,
independent deployment, fault isolation requirements).

[Back to Top](#top)

<a id="14-the-request-lifecycle-in-a-real-backend"></a>

## 14. The Request Lifecycle in a Real Backend

Here is what Satya's production backend looks like with everything added:

```
Client
  |
  v
Load Balancer           <-- distributes requests across servers
  |
  v
API Gateway (optional)  <-- auth, rate limiting, routing
  |
  v
App Server (your code)
  |         |
  v         v
Redis     Database
(cache)   (persistent storage)
  |
  v
Return response to client
```

Each arrow is a network call. Each network call has latency.
This is why **caching** matters: every Redis hit saves a database call (~100x faster).

[Back to Top](#top)

<a id="15-connection-pools"></a>

## 15. Connection Pools

Opening a database connection is expensive:

```
TCP handshake:     ~1ms
Auth + SSL:        ~2-5ms
Total:             3-6ms just to connect
```

If you have 1,000 requests/second, each opening a new connection = 3,000-6,000ms of
wasted connection time per second.

**Connection pool**: a pre-created set of connections that are reused.

```
App startup:
  -> Open 10 DB connections, keep them warm

Per request:
  -> "borrow" a connection from the pool  <-- ~0.01ms
  -> run your query
  -> "return" connection to pool

Result: no connection overhead per request
Most apps need 10-50 connections per server (not 1 per request!)
```

Satya configures his pool size with this formula:

```
pool_size = (number_of_cores * 2) + effective_spindle_count
         = (4 * 2) + 1  (for SSD)
         = 9 connections

For most web apps: 10-20 is a good starting point.
For high-throughput: measure and tune. More is not always better.
Too many connections -> DB context-switching overhead.
```

[Back to Top](#top)

<a id="16-synchronous-vs-asynchronous-processing"></a>

## 16. Synchronous vs Asynchronous Processing

Not every task needs to be done before the response is sent.

```
Synchronous (do everything before responding):
  User uploads photo
  -> resize photo  (500ms)
  -> generate thumbnail (200ms)
  -> save to S3 (300ms)
  -> save metadata to DB (10ms)
  -> return "upload complete"
  Total wait: 1010ms

Asynchronous (respond immediately, do work in background):
  User uploads photo
  -> save original to S3 (300ms)
  -> put job on queue: {task: "process_photo", id: 123}  (1ms)
  -> return "upload received"  <-- user sees success after 301ms!

  Background worker (running separately):
  -> picks up job from queue
  -> resize, thumbnail, save
  -> update status in DB
```

**Rule:** If the user does not need the result immediately, do it async.
This is why you will learn **Message Queues** in module 09.

**Satya's heuristic:**
- User is waiting for the screen to update? Synchronous.
- User will check back later or get notified? Asynchronous.
- Could take more than 1 second? Almost always asynchronous.

[Back to Top](#top)

<a id="17-key-numbers-for-a-single-server"></a>

## 17. Key Numbers for a Single Server

```
Modern app server (4 cores, 8 GB RAM):
  HTTP requests:    ~2,000-10,000 req/s  (depends on work per request)
  RAM per process:  ~50-200 MB (Python/Node)
  DB connections:   10-50 (connection pool)
  Thread pool:      4-32 workers (depends on I/O wait time)

When to add a second server:
  CPU consistently above 70%
  Response times rising
  Single point of failure is unacceptable

Anything that runs fine on 1 server:
  Up to ~1M users (if most are not concurrent)
  ~10,000 concurrent active users
  ~1,000 requests/second
```

Satya reminds his team: "Do not add a second server for redundancy alone. Add it
because you need either more capacity or fault tolerance."

[Back to Top](#top)

<a id="18-common-mistakes"></a>

## 18. Common Mistakes

Satya has seen (and made) all of these:

**Mistake 1: Premature microservices**
```
Symptom:  5-person startup with 12 microservices
Problem:  Operational overhead kills velocity
Fix:      Start with a modular monolith, extract when pain is proven
Rule:     If you cannot name the specific scaling/deployment problem
          a microservice solves, you do not need it yet
```

**Mistake 2: Shared database across services**
```
Symptom:  3 "microservices" all reading/writing the same PostgreSQL tables
Problem:  You have a distributed monolith (worst of both worlds)
Fix:      Each service owns its data. Communicate via APIs or events.
Rule:     If two services share a DB, they are one service pretending to be two
```

**Mistake 3: Synchronous chains**
```
Symptom:  Order -> Payment -> Inventory -> Notification (all synchronous HTTP)
Problem:  Latency adds up. Any service down = entire chain fails.
Fix:      Use events for non-critical downstream actions
Rule:     If service B being down should NOT prevent service A from working,
          do not call B synchronously
```

**Mistake 4: No circuit breakers**
```
Symptom:  Payment service goes slow, all callers pile up waiting
Problem:  Cascading failure (slow service takes down healthy services)
Fix:      Circuit breaker pattern: after N failures, stop calling, return fallback
Rule:     Every external call needs a timeout AND a fallback plan
```

**Mistake 5: Ignoring Conway's Law**
```
Symptom:  Architecture does not match team structure
Problem:  3 teams working on 1 monolith = constant merge conflicts
          1 team running 8 microservices = overhead with no benefit
Fix:      Architecture should mirror team boundaries
Rule:     1 team = 1 service (or 1 well-bounded module). Never fewer teams than services.
```

**Mistake 6: Big bang rewrite**
```
Symptom:  "Let us rewrite the whole monolith in microservices over 6 months"
Problem:  6 months becomes 18 months. Old system still running. Two systems to maintain.
Fix:      Strangler Fig pattern: extract one piece at a time, route traffic gradually
Rule:     Never stop the world. Migrate incrementally.
```

**Mistake 7: Choosing serverless for everything**
```
Symptom:  Entire backend is 200 Lambda functions
Problem:  Cold starts, debugging nightmares, vendor lock-in, costs spiral at scale
Fix:      Serverless for glue/events/spiky-traffic. Containers for steady-state workloads.
Rule:     If the function runs more than 50% of the time, a container is cheaper
```

[Back to Top](#top)

<a id="19-summary"></a>

## 19. Summary

Satya steps back and looks at his whiteboard. After weeks of research, his architecture
decision is clear: keep the modular monolith for now, extract Payment as the first
microservice (proven pain), and use events for the notification pipeline.

**Key takeaways:**

- Start with a monolith. Extract when pain is proven, not predicted.
- Layered architecture keeps your monolith clean and extractable.
- Microservices solve organizational problems (team autonomy, independent deploys) — not code problems.
- Event-driven architecture decouples producers from consumers.
- Serverless excels at spiky, unpredictable workloads.
- CQRS separates read and write concerns when they diverge significantly.
- Architecture should evolve with your team size and traffic patterns.
- Conway's Law is real: your system will mirror your org chart.

```
Architecture Evolution Path:

  Single File -> Modular Monolith -> Monolith + Extracted Services -> Microservices
  (1 dev)        (1-20 devs)         (20-50 devs)                    (50+ devs)

  Each step adds complexity. Only take the next step when
  the current architecture is PROVABLY causing pain.
```

[Back to Top](#top)

## Navigation

| | |
|---|---|
| Previous | [03 - API Design](../03_api_design/theory.md) |
| Next | [05 - Databases](../05_databases/theory.md) |
| Up | [System Design Mastery](../README.md) |
| Home | [Repository Root](../../README.md) |
| Related | [12 - Microservices](../12_microservices/theory.md) |

[Back to Top](#top)
