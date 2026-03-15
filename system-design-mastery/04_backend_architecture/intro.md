# The Backend — Where Your Code Lives and Breathes

> Before microservices, before Kubernetes, before "distributed" anything —
> there's a backend. A program running on a machine, waiting for requests.
> This is where everything starts.

---

## The Simplest Backend That Could Possibly Work

You open your laptop. You write:

```python
from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/ping")
def ping():
    return jsonify({"status": "ok"})

app.run(port=8080)
```

That's it. That IS a backend. A process, listening on a port, responding to HTTP.

Everything else — load balancers, databases, caches, queues, Kubernetes — is what
you ADD when this simple thing is no longer enough.

---

## The Client-Server Model

Every web system is built on one fundamental idea:

```
┌──────────────┐           ┌──────────────────────────────────┐
│    Client    │           │             Server               │
│              │  Request  │                                  │
│  Browser     │ ─────────→│  Receives request                │
│  Mobile app  │           │  Does some work (logic + data)   │
│  Another API │ ←─────────│  Returns response                │
│              │  Response │                                  │
└──────────────┘           └──────────────────────────────────┘
```

**Client**: whoever sends the request (browser, mobile app, another service)
**Server**: whoever receives it, processes it, responds

The client knows the server's address (URL). The server doesn't know the client exists until it gets a request.

---

## What Happens When a Request Arrives

Let's trace `GET /users/42` hitting your server:

```
1. TCP connection established
   → OS kernel accepts the connection
   → Hands socket to your process

2. HTTP parsing
   → Framework reads: method=GET, path=/users/42, headers=...

3. Routing
   → Framework finds: "for GET /users/{id}, call get_user()"

4. Business logic (your code)
   → Validate id
   → Query database: SELECT * FROM users WHERE id = 42

5. Database I/O
   → Connection pool picks an available connection
   → Query sent to DB (network call: ~1ms)
   → Results returned as rows

6. Serialization
   → Python dict → JSON bytes

7. HTTP response written
   → Status 200, headers, body

8. TCP connection kept alive or closed
```

**Total time:** typically 5–50ms for a simple DB-backed endpoint.

---

## Stateless vs Stateful Servers

This is one of the most important decisions in backend design.

### Stateful server

```
Client A → Server (remembers Client A's session in memory)
Client B → Server (remembers Client B's session in memory)

Problem:
  Client A sends request 1 → Server 1 (stores session)
  Client A sends request 2 → Server 2 (session not found!)

  If you add more servers, sessions are tied to ONE server.
  Server crash = all sessions lost.
```

### Stateless server

```
Client A → sends auth token with EVERY request
Server reads token, validates it, doesn't store anything

Client A → Server 1 → reads token → ✅
Client A → Server 2 → reads token → ✅
Client A → Server 3 → reads token → ✅

Any server can handle any request!
→ Horizontal scaling becomes trivial
→ Server crash loses nothing
→ Load balancer can route freely
```

**Rule:** Make your servers stateless. Store state in:
- Database (persistent state: user data, orders)
- Cache like Redis (session state: shopping cart, rate limit counters)
- The client itself (JWT tokens are stateless auth)

---

## The Monolith — Not a Dirty Word

A **monolith** is a single deployable unit that handles everything.

```
┌────────────────────────────────────────────────┐
│                  Monolith                      │
│                                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │  User    │ │  Order   │ │  Payment     │  │
│  │  Service │ │  Service │ │  Service     │  │
│  └──────────┘ └──────────┘ └──────────────┘  │
│                                                │
│  Single codebase, single deploy, one DB        │
└────────────────────────────────────────────────┘
         │                       │
    Load Balancer            Database
```

**Monolith advantages:**
- Simple to develop and test
- No network calls between components (function calls instead)
- Easy to debug (one log stream, one process)
- Easy to deploy (one artifact)
- Works well for most companies early on

**When monolith struggles:**
- Team grows to 50+ engineers editing the same codebase
- Different parts need different scaling (payment service needs 3× capacity of profile service)
- One part crashes, takes down everything
- Need to deploy one module without deploying everything

This is when you start breaking it apart. See **[12 — Microservices](../12_microservices/theory.md)**.

---

## The Request Lifecycle in a Real Backend

Here's what a production backend looks like with a few additions:

```
Client
  │
  ▼
Load Balancer           ← distributes requests across servers
  │
  ▼
API Gateway (optional)  ← auth, rate limiting, routing
  │
  ▼
App Server (your code)
  │         │
  ▼         ▼
Redis     Database
(cache)   (persistent storage)
  │
  ▼
Return response to client
```

Each arrow is a network call. Each network call has latency.
This is why **caching** matters: every Redis hit saves a database call (~100x faster).

---

## Connection Pools — Why You Can't Just Open a New DB Connection per Request

Opening a database connection is expensive:
```
TCP handshake:     ~1ms
Auth + SSL:        ~2-5ms
Total:             3-6ms just to connect
```

If you have 1,000 requests/second, each opening a new connection = 3,000–6,000ms of
wasted connection time per second.

**Connection pool**: a pre-created set of connections that are reused.

```
App startup:
  → Open 10 DB connections, keep them warm

Per request:
  → "borrow" a connection from the pool  ← ~0.01ms
  → run your query
  → "return" connection to pool

Result: no connection overhead per request
Most apps need 10–50 connections per server (not 1 per request!)
```

---

## Synchronous vs Asynchronous Processing

Not every task needs to be done before the response is sent.

```
Synchronous (do everything before responding):
  User uploads photo
  → resize photo  (500ms)
  → generate thumbnail (200ms)
  → save to S3 (300ms)
  → save metadata to DB (10ms)
  → return "upload complete"
  Total wait: 1010ms

Asynchronous (respond immediately, do work in background):
  User uploads photo
  → save original to S3 (300ms)
  → put job on queue: {task: "process_photo", id: 123}  (1ms)
  → return "upload received"  ← user sees success after 301ms!

  Background worker (running separately):
  → picks up job from queue
  → resize, thumbnail, save
  → update status in DB
```

**Rule:** If the user doesn't need the result immediately → do it async.
This is why you'll learn **[09 — Message Queues](../09_message_queues/theory.md)** next (after databases and caching).

---

## Key Numbers for a Single Server

```
Modern app server (4 cores, 8 GB RAM):
  HTTP requests:    ~2,000–10,000 req/s  (depends on work per request)
  RAM per process:  ~50-200 MB (Python/Node)
  DB connections:   10–50 (connection pool)
  Thread pool:      4–32 workers (depends on I/O wait time)

When to add a second server:
  CPU consistently above 70%
  Response times rising
  Single point of failure is unacceptable

Anything that runs fine on 1 server:
  Up to ~1M users (if most are not concurrent)
  ~10,000 concurrent active users
  ~1,000 requests/second
```

---

## What Comes Next

You understand the basic building blocks. Now we go deeper:

```
                     ┌──────────────────────────────┐
                     │     What you know now         │
                     │   Client → Server → DB        │
                     └──────────────┬───────────────┘
                                    │
          ┌─────────────────────────▼─────────────────────────┐
          │                  What's ahead                       │
          │                                                     │
          │  05 Databases    → HOW does the DB actually work?   │
          │  06 Caching      → HOW do we avoid going to DB?     │
          │  08 Load Bal.    → HOW do we run many servers?      │
          │  09 Queues       → HOW do we do async work?         │
          │  12 Microservices→ HOW do we split the monolith?    │
          │  16 HLD          → HOW do we design a whole system? │
          └─────────────────────────────────────────────────────┘
```

---

## 🔁 Navigation

| | |
|---|---|
| ← Previous | [03 — API Design](../03_api_design/theory.md) |
| ➡️ Next | [05 — Databases](../05_databases/theory.md) |
| 🏠 Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Api Design — Interview Q&A](../03_api_design/interview.md) &nbsp;|&nbsp; **Next:** [Databases — Theory →](../05_databases/theory.md)
