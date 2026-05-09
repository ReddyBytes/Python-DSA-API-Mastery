<a id="top"></a>
# 🏗 System Design with Python

## 📖 Table of Contents

- [Learning Priority](#-learning-priority)
- [1. Scaling Fundamentals](#1-scaling-fundamentals)
- [2. API Design Principles](#2-api-design-principles)
- [3. Rate Limiting](#3-rate-limiting)
- [4. Caching Strategies](#4-caching-strategies)
- [5. Database Design Thinking](#5-database-design-thinking)
- [6. Asynchronous Processing](#6-asynchronous-processing)
- [7. Load Balancing](#7-load-balancing)
- [8. Fault Tolerance](#8-fault-tolerance)
- [9. Security in System Design](#9-security-in-system-design)
- [10. Monitoring and Metrics](#10-monitoring-and-metrics)
- [11. Example: Scalable URL Shortener](#11-example-scalable-url-shortener)
- [Summary](#-summary)
- [Subfolder Deep Dives](#-subfolder-deep-dives)
- [Navigation](#-navigation)

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
REST API design principles · HTTP status codes · Request/response lifecycle · Rate limiting · Pagination strategies · API authentication basics

**Should Learn** — Important for real projects, comes up regularly:
gRPC vs REST · API versioning · Circuit breaker pattern · Graceful shutdown · Idempotency keys · OpenAPI/Swagger docs

**Good to Know** — Useful in specific situations:
GraphQL basics · Webhook design · Distributed tracing · Service mesh concepts · Bulkhead pattern

**Reference** — Know it exists, look up when needed:
HATEOAS · CQRS · Consensus algorithms (Raft/Paxos) · Multi-region strategies

---

Your app works fine at 10 users. At 1 million users, the API slows down, the database crashes, memory spikes, and users leave. System design is the discipline of building systems that survive scale — choosing the right architecture before problems appear, not patching them after. Python is the tool; design thinking is the skill.

---

<a id="1-scaling-fundamentals"></a>
# 1. Scaling Fundamentals

## The Analogy

A restaurant with one chef handles 20 orders a night without thinking. At 200 orders, you face a choice: buy a bigger oven (vertical scaling) or hire more chefs and open a second kitchen (horizontal scaling). Both increase throughput, but they have very different trade-offs.

## Horizontal vs Vertical Scaling

**Vertical scaling** — upgrade the single machine:
- Add more CPU cores, RAM, faster disk
- Simple: no code changes required
- Hard ceiling: there is a largest machine you can buy
- Single point of failure remains

**Horizontal scaling** — add more machines:
- Run many smaller instances behind a load balancer
- Linear cost scaling
- No theoretical ceiling — keep adding nodes
- Requires stateless application design

```
Vertical                    Horizontal
┌─────────────────┐         ┌───────┐  ┌───────┐  ┌───────┐
│                 │         │ app-1 │  │ app-2 │  │ app-3 │
│  BIG SERVER     │  vs.    │ small │  │ small │  │ small │
│  (32 CPU, 256G) │         └───────┘  └───────┘  └───────┘
│                 │              ↑         ↑          ↑
└─────────────────┘         ┌───────────────────────────┐
                             │      Load Balancer        │
                             └───────────────────────────┘
```

Horizontal scaling is preferred for production systems because it is both more resilient and more economical at scale.

## Stateless Design

A service is **stateless** when it stores no user session data locally. Every request carries everything the server needs to process it — typically via a JWT token or session ID that points to shared storage.

```
Stateful (BAD for horizontal scaling):
  Request 1 → App-1 (stores session in memory)
  Request 2 → App-2 (no session — user must log in again!)

Stateless (correct):
  Request 1 → App-1 (reads session from Redis)
  Request 2 → App-2 (reads same session from Redis — works!)
```

```python
# Stateless: session stored in Redis, not in local memory
import redis
import json

redis_client = redis.Redis(host="redis", port=6379)

def get_session(session_id: str) -> dict | None:
    data = redis_client.get(f"session:{session_id}")  # ← any app node can read this
    return json.loads(data) if data else None

def set_session(session_id: str, data: dict, ttl_seconds: int = 3600) -> None:
    redis_client.setex(
        f"session:{session_id}",
        ttl_seconds,
        json.dumps(data),                             # ← shared across all app nodes
    )
```

Store session state in: database, Redis, or external object storage — never in local memory.

[↑ Back to Top](#top)

---

<a id="2-api-design-principles"></a>
# 2. API Design Principles

## The Analogy

A well-designed API is like a hotel concierge: predictable, consistent, and polite. You ask for the same thing the same way every time and get a reliable answer. A badly designed API is like navigating a foreign city with no map — every endpoint is a surprise.

## REST Principles

Good APIs are predictable, consistent, versioned, secure, and documented. REST achieves this through five rules:

- Use proper HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Use resource-oriented endpoints (nouns, not verbs)
- Return proper HTTP status codes
- Be stateless — each request is self-contained
- Return consistent response shapes

```python
# Good REST endpoint design
GET    /users/123           # ← fetch user 123
POST   /users               # ← create a new user
PUT    /users/123           # ← replace user 123 entirely
PATCH  /users/123           # ← partial update
DELETE /users/123           # ← delete user 123

GET    /users/123/orders    # ← nested resource: orders for user 123
POST   /orders              # ← create an order (also acceptable)

# Bad: verbs in URL
POST   /createUser          # ← wrong: verb in endpoint
GET    /getUserById?id=123  # ← wrong: RPC style, not REST
```

Standard status codes:

| Code | Meaning | When |
|---|---|---|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Missing/invalid auth |
| 403 | Forbidden | Authenticated but not allowed |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Duplicate resource |
| 422 | Unprocessable Entity | Semantic validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server failure |

## Idempotency

An operation is **idempotent** if calling it multiple times produces the same result as calling it once.

- `GET` — always safe and idempotent (no side effects)
- `PUT` — idempotent (replace resource — same result every time)
- `DELETE` — idempotent (delete once or ten times — resource is gone)
- `POST` — NOT idempotent by default (calling twice creates two records)

For non-idempotent operations (payment processing, order creation), use an **idempotency key**:

```python
from fastapi import FastAPI, Header, HTTPException
import hashlib

app = FastAPI()
processed_keys: set[str] = set()   # ← in production, use Redis with TTL

@app.post("/orders", status_code=201)
async def create_order(
    payload: dict,
    idempotency_key: str = Header(...),   # ← client sends unique key per attempt
) -> dict:
    if idempotency_key in processed_keys:
        return {"status": "already_processed", "key": idempotency_key}  # ← safe to retry

    # process order...
    processed_keys.add(idempotency_key)
    return {"status": "created", "order_id": "ord-123"}
```

The client generates the idempotency key (a UUID) before sending. If the request times out and they retry, the server detects the duplicate and returns the cached result instead of creating a second order.

📝 **Practice:** [Q1 — Name REST endpoints](./practice.md#q1--rest-endpoints---name-rest-endpoints-for-a-blog-) · [Q2 — Status codes](./practice.md#q2--http-status-codes---match-operations-to-status-codes-) · [Q7 — Idempotency key](./practice.md#q7--idempotency-key---prevent-duplicate-orders-) · [Deep dive →](./01_api_design_patterns/theory.md)

[↑ Back to Top](#top)

---

<a id="3-rate-limiting"></a>
# 3. Rate Limiting

## The Analogy

A nightclub has a capacity limit. The bouncer lets people in at a controlled rate — not a flood all at once. Without the bouncer, the club fills instantly, fire codes are violated, and the bar runs out of drinks. Rate limiting is the bouncer for your API.

## Why Rate Limit?

Without rate limiting, a single misbehaving client — or an attacker — can exhaust your server resources:

- **Abuse prevention** — stops scripts hammering your endpoints
- **DDoS mitigation** — limits impact of distributed attack traffic
- **Resource fairness** — one tenant cannot starve others
- **Cost control** — in cloud environments, unbounded traffic means unbounded bills

## Common Strategies

**Fixed Window** — count requests per fixed time window (e.g., 100 requests per minute):

```
Window:  |--- 0:00-0:01 ---|--- 0:01-0:02 ---|
Count:        97 requests       3 + 97 = 100?
Problem: burst at window boundary (97 + 97 = 194 in 2 seconds)
```

Simple but vulnerable to burst attacks at window edges.

**Sliding Window** — a rolling time window that eliminates the boundary burst problem. More precise but requires more storage.

**Token Bucket** — tokens fill a bucket at a fixed rate; each request consumes one token. Allows short bursts (drain the bucket) while enforcing a long-term average rate. Used by Twitter, GitHub, Stripe.

```
Bucket capacity: 10 tokens
Refill rate: 1 token/second

Time 0: bucket = 10 (full)
Time 0: burst of 10 requests → bucket = 0 (all consumed)
Time 1: refill → bucket = 1
Time 1: 1 request → bucket = 0
Time 2: refill → bucket = 1  (enforces ~1 req/sec average)
```

## Python Token Bucket Implementation

```python
import time
import threading

class TokenBucket:
    """Thread-safe token bucket rate limiter."""

    def __init__(self, capacity: int, refill_rate: float) -> None:
        self.capacity = capacity          # ← max burst size
        self.tokens = float(capacity)     # ← current tokens
        self.refill_rate = refill_rate    # ← tokens per second
        self.last_refill = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)  # ← cap at capacity
        self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        """Returns True if request is allowed, False if rate limit exceeded."""
        with self._lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True             # ← allowed
            return False                # ← rejected


# Per-user rate limiter using Redis in production:
# Store (tokens, last_refill) in Redis with TTL — same logic, distributed
limiter = TokenBucket(capacity=10, refill_rate=1.0)  # ← 10 burst, 1/sec steady


# FastAPI middleware example:
from fastapi import Request, HTTPException

async def rate_limit_middleware(request: Request, call_next):
    if not limiter.consume():
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": "1"},   # ← tell client when to retry
        )
    return await call_next(request)
```

📝 **Practice:** [Q16 — Token bucket](./practice.md#q16--token-bucket---implement-token-bucket-) · [Q17 — Sliding window](./practice.md#q17--sliding-window---implement-sliding-window-limiter-) · [Q8 — Rate limit headers](./practice.md#q8--rate-limit-headers---add-x-ratelimit--headers-) · [Deep dive →](./02_scalability_caching_patterns/theory.md)

[↑ Back to Top](#top)

---

<a id="4-caching-strategies"></a>
# 4. Caching Strategies

## The Analogy

A librarian does not walk to the archive for every request. Popular books sit on the front desk. When a book is requested, they check the desk first (cache hit), then the archive (cache miss). The desk has limited space — only the most-requested books stay there.

Caching improves performance, scalability, and cost efficiency by serving repeated requests from fast storage instead of slow compute or database reads.

## Where to Cache?

```
Request → In-memory (dict/lru_cache)  ← fastest, lost on restart, per-process
        → Redis / Memcached           ← shared across all app nodes, survives restarts
        → CDN (Cloudfront, Cloudflare) ← static assets + API responses at edge
        → Database query cache         ← DB-level, transparent to application
```

## Caching Patterns

**Cache-Aside (Lazy Loading)** — the most common pattern. The application checks the cache first; on a miss it fetches from the database and populates the cache.

```python
import redis
import json
from typing import Any

cache = redis.Redis(host="redis", port=6379)

def get_user(user_id: int) -> dict | None:
    cache_key = f"user:{user_id}"

    # ← 1. Check cache first
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)                  # ← cache hit: return immediately

    # ← 2. Cache miss: fetch from database
    user = db.query("SELECT * FROM users WHERE id = %s", user_id)
    if user is None:
        return None

    # ← 3. Populate cache for next request
    cache.setex(cache_key, 300, json.dumps(user))  # ← TTL: 5 minutes
    return user
```

**Write-Through** — update cache and database together on every write. Cache is always fresh. Adds latency to writes but reads are always fast.

```python
def update_user(user_id: int, data: dict) -> None:
    db.execute("UPDATE users SET ... WHERE id = %s", user_id)  # ← write DB
    cache.setex(f"user:{user_id}", 300, json.dumps(data))      # ← write cache
```

**Write-Back (Write-Behind)** — write to cache first, flush to database asynchronously. Extremely fast writes, but risk of data loss if cache crashes before flush. Used in high-throughput systems where write speed matters more than durability guarantees.

## Cache Invalidation

Cache invalidation is often called the hardest problem in computer science. The challenge: how do you know when cached data is stale?

Three strategies:

- **TTL (time-to-live)** — cache entries expire after N seconds. Simple, but stale window = TTL duration.
- **Event-driven invalidation** — on write, explicitly delete or update the cache entry. Precise, but requires discipline across all write paths.
- **Version tags** — include a version number in the cache key. On schema change, bump the version — old keys become orphans and expire naturally.

```python
# TTL: accept up to 5-minute staleness
cache.setex("user:123", 300, json.dumps(user))

# Event-driven: delete on write
def update_user(user_id: int, data: dict) -> None:
    db.execute("UPDATE users ...")
    cache.delete(f"user:{user_id}")    # ← next read will repopulate

# Version key: safe schema migration
VERSION = "v2"
cache_key = f"{VERSION}:user:{user_id}"   # ← old "v1:user:123" keys ignored
```

📝 **Practice:** [Q9 — TTL cache](./practice.md#q9--dict-ttl-cache---implement-a-ttl-cache-class-) · [Q11 — LRU cache](./practice.md#q11--lru-cache---ordereddict-lru-) · [Q12 — Cache-aside](./practice.md#q12--cache-aside---write-cache-aside-with-mock-redis-) · [Deep dive →](./02_scalability_caching_patterns/theory.md)

[↑ Back to Top](#top)

---

<a id="5-database-design-thinking"></a>
# 5. Database Design Thinking

## The Analogy

A phone book with 10 million entries is useless if you have to scan every page to find a name. An index at the back lets you jump directly to the right page. Database indexes do exactly this — they trade write speed and storage for dramatic read speed improvements.

## Indexing

An **index** is a separate data structure (usually a B-tree) that maps column values to row locations. Reads become logarithmic instead of linear.

```sql
-- Without index: scans all 10M rows
SELECT * FROM orders WHERE user_id = 42;

-- With index: jumps directly to matching rows
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Composite index: optimizes queries filtering on both columns
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
```

⚠️ Every index slows down `INSERT`, `UPDATE`, and `DELETE` (the index must be updated too). Index selectively — high-cardinality columns used frequently in `WHERE` clauses.

## Avoiding N+1 Queries

The **N+1 query problem** is one of the most common performance killers. It appears when you load a list of N items and then issue a separate query for each item.

```python
# N+1 BAD: 1 query for users + N queries for orders (101 queries for 100 users)
users = db.query("SELECT * FROM users LIMIT 100")
for user in users:
    orders = db.query("SELECT * FROM orders WHERE user_id = %s", user["id"])
    # ← 1 extra query per user = 100 extra queries

# GOOD: 2 queries total (JOIN or IN clause)
users = db.query("SELECT * FROM users LIMIT 100")
user_ids = [u["id"] for u in users]
orders = db.query(
    "SELECT * FROM orders WHERE user_id = ANY(%s)", user_ids  # ← 1 batch query
)
# group orders by user_id in Python
orders_by_user = {}
for order in orders:
    orders_by_user.setdefault(order["user_id"], []).append(order)
```

In ORMs (SQLAlchemy, Django ORM), use `joinedload` or `select_related` to avoid N+1 automatically.

## Read Replicas and Sharding

**Read replicas** — the primary database handles all writes; one or more replicas receive asynchronous copies and serve read traffic. Most applications are read-heavy (10:1 read/write ratio is common), so replicas dramatically reduce load on the primary.

```
                 ┌──────────────────────┐
Writes ──────→  │   Primary DB         │
                 └──────────────────────┘
                        │ async replication
              ┌─────────┴──────────┐
              ▼                    ▼
       ┌────────────┐       ┌────────────┐
Reads →│  Replica 1 │  or   │  Replica 2 │← Reads
       └────────────┘       └────────────┘
```

**Sharding** — splitting data across multiple database servers by a shard key (e.g., `user_id % N`). Each shard handles a fraction of the total data. Used when a single database cannot hold or process the full dataset.

```python
def get_shard(user_id: int, num_shards: int = 4) -> str:
    shard_id = user_id % num_shards              # ← deterministic routing
    return f"db-shard-{shard_id}"               # ← always same shard for same user

# user_id=123: 123 % 4 = 3 → db-shard-3
# user_id=456: 456 % 4 = 0 → db-shard-0
```

[↑ Back to Top](#top)

---

<a id="6-asynchronous-processing"></a>
# 6. Asynchronous Processing

## The Analogy

When you submit a tax return online, the website immediately says "received." It does not make you wait 30 minutes while the IRS processes it. The website queues your submission and returns immediately. A background worker picks it up later and does the heavy work.

This is the async processing pattern: accept the request instantly, do the work in the background.

## Why Async Processing?

Use background jobs for work that is too slow for a synchronous HTTP response:

- Email sending (250ms+ per email)
- PDF or report generation
- Image processing / resizing
- Sending webhooks to third-party services
- Heavy data aggregation queries
- ML model inference

Without async processing, your API response time is bounded by the slowest step. With it, your API responds in milliseconds and the slow work happens asynchronously.

## Celery Task Queue Pattern

**Celery** is Python's most popular distributed task queue. It uses a message broker (Redis or RabbitMQ) to pass tasks to worker processes.

```python
# tasks.py
from celery import Celery

app = Celery("myapp", broker="redis://localhost:6379/0")  # ← broker stores task queue

@app.task
def send_welcome_email(user_id: int, email: str) -> None:
    """Heavy work — runs in a separate worker process."""
    # connect to email service, render template, send
    email_service.send(to=email, template="welcome", user_id=user_id)
    print(f"Email sent to {email}")


# api.py — FastAPI endpoint
from fastapi import FastAPI
from .tasks import send_welcome_email

api = FastAPI()

@api.post("/users", status_code=201)
async def create_user(payload: dict) -> dict:
    user = db.create_user(payload)                     # ← fast: create in DB
    send_welcome_email.delay(user.id, user.email)      # ← queues task, returns immediately
    return {"id": user.id, "status": "created"}        # ← responds in <10ms
```

Start a worker in a separate process:

```bash
celery -A tasks worker --loglevel=info   # ← picks up tasks from Redis queue
```

## Tool Comparison

| Tool | Best for |
|---|---|
| **Celery + Redis** | General-purpose task queues, scheduled jobs (cron), retries |
| **Celery + RabbitMQ** | High-reliability queues, complex routing, dead-letter queues |
| **Kafka** | High-throughput event streaming, event sourcing, ordered delivery |
| **RQ (Redis Queue)** | Simpler alternative to Celery for small projects |
| **asyncio tasks** | I/O-bound concurrency within one process (not distributed) |

[↑ Back to Top](#top)

---

<a id="7-load-balancing"></a>
# 7. Load Balancing

## The Analogy

A supermarket with 10 checkout lanes and one cashier is a waste. A load balancer is the manager who directs each customer to the least-busy open lane. Without it, one server is overloaded and nine sit idle.

## Load Balancing Algorithms

```
Incoming Requests
       │
       ▼
┌─────────────────────┐
│    Load Balancer    │
└─────────────────────┘
       │
  ┌────┴────────────────────────┐
  ▼           ▼                 ▼
App-1        App-2            App-3
```

| Algorithm | How it works | Best for |
|---|---|---|
| **Round Robin** | Route to servers in rotating order | Servers of equal capacity |
| **Least Connections** | Route to server with fewest active connections | Varying request durations |
| **IP Hash** | Hash client IP to always route to same server | Session stickiness without Redis |
| **Weighted Round Robin** | Servers get traffic proportional to assigned weight | Mixed-capacity servers |
| **Random** | Pick a random server | Simple, surprisingly effective |

## Load Balancer Types and Tools

**L4 (Transport Layer)** — routes by IP address and TCP port. Does not inspect HTTP content. Fast, low overhead.

**L7 (Application Layer)** — routes by HTTP headers, URL path, cookies. Enables path-based routing (`/api` → backend, `/static` → CDN), header-based canary deployments, and SSL termination.

| Tool | Layer | Common use |
|---|---|---|
| **Nginx** | L4 + L7 | Reverse proxy, SSL termination, static files |
| **AWS ALB** | L7 | Path/header-based routing on AWS |
| **AWS NLB** | L4 | Ultra-low latency, TCP pass-through |
| **HAProxy** | L4 + L7 | High-performance, fine-grained configuration |

```nginx
# Nginx upstream config — round robin by default
upstream app_servers {
    server app-1:8000;
    server app-2:8000;
    server app-3:8000;
}

server {
    location /api/ {
        proxy_pass http://app_servers;   # ← distribute across 3 servers
    }
}
```

[↑ Back to Top](#top)

---

<a id="8-fault-tolerance"></a>
# 8. Fault Tolerance

## The Analogy

Aircraft engines are designed to keep flying if one engine fails. The plane does not drop — it degrades gracefully to single-engine flight and lands safely. Production systems need the same property: when one component fails, the system should degrade, not crash.

Never assume the network always works. Never assume dependencies are always available.

## Retries with Backoff

Transient failures — network blips, brief overload, DNS hiccups — often resolve within seconds. The pattern: retry, but wait longer between each attempt to avoid hammering a struggling service.

```python
import time
import random

def retry_with_backoff(func, max_retries=3, base_delay=1.0, exceptions=(Exception,)):
    for attempt in range(max_retries):
        try:
            return func()
        except exceptions as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)                  # ← 1s, 2s, 4s...
            jitter = random.uniform(0, delay * 0.1)              # ← avoid thundering herd
            time.sleep(delay + jitter)
```

**Thundering herd**: if 1000 clients all retry at the same time, the recovering server gets slammed again. Jitter (random delay variation) spreads out retries.

## Circuit Breaker

A **circuit breaker** tracks failures to a dependency. After N consecutive failures, it "opens" the circuit — subsequent calls fail immediately without even attempting the request. After a timeout, it allows one probe call. If that succeeds, the circuit closes.

```
CLOSED → normal, failures counted
  ↓ (failures ≥ threshold)
OPEN → fail immediately, no calls made
  ↓ (after timeout)
HALF-OPEN → one probe call allowed
  ↓ success → CLOSED
  ↓ failure → OPEN again
```

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"   # CLOSED | OPEN | HALF_OPEN

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.monotonic() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"   # ← allow one probe
            else:
                raise RuntimeError("Circuit open — fast fail")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.monotonic()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
```

💡 The `tenacity` library provides production-ready retry + circuit breaker without rolling your own.

## Graceful Degradation and Timeouts

**Graceful degradation** — when a non-critical dependency fails, return a reduced but valid response instead of a 500 error.

```python
def get_product_page(product_id: int) -> dict:
    product = fetch_product(product_id)          # ← critical: must succeed

    try:
        reviews = fetch_reviews(product_id)      # ← nice-to-have
    except Exception:
        reviews = []                             # ← degrade: return empty, not 500

    return {"product": product, "reviews": reviews}
```

**Timeouts** — always set explicit timeouts on external calls. Without them, one slow dependency can exhaust all connection threads.

```python
import httpx

async with httpx.AsyncClient(timeout=5.0) as client:   # ← 5-second hard limit
    response = await client.get("https://api.example.com/data")
```

[↑ Back to Top](#top)

---

<a id="9-security-in-system-design"></a>
# 9. Security in System Design

## The Analogy

A bank vault has multiple layers: a locked lobby door, a guard, an ID check, a combination lock, and a time lock. Breaking through one layer is not enough. Security in system design works the same way — defense in depth, with independent barriers at every layer.

## Authentication and Authorization

**Authentication** — verifying identity ("who are you?").
**Authorization** — verifying permissions ("what are you allowed to do?").

```python
# JWT authentication in FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return payload                               # ← user_id, role, etc.
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Role-based authorization
def require_role(required_role: str):
    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return checker


@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: dict = Depends(require_role("admin")),   # ← only admins
) -> dict:
    ...
```

## Transport Security and Input Validation

**HTTPS everywhere** — never serve APIs over plain HTTP in production. TLS encrypts data in transit and authenticates your server to clients.

**Rate limiting** — prevents brute-force attacks on auth endpoints. 100 login attempts per minute from one IP is an attack, not a user.

**Input validation** — never trust user-supplied data. Validate every field before processing.

```python
from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    email: EmailStr                         # ← validates email format
    password: str = Field(min_length=8)     # ← enforces minimum length
    age: int = Field(ge=0, le=150)          # ← bounds check
    username: str = Field(pattern=r"^[a-zA-Z0-9_]+$")  # ← alphanumeric only
```

Security must be designed in, not bolted on. OWASP Top 10 covers the most critical vulnerabilities — SQL injection, XSS, broken authentication, insecure direct object references. Addressing these at the framework level (parameterized queries, ORM, Pydantic validation) prevents entire classes of bugs.

[↑ Back to Top](#top)

---

<a id="10-monitoring-and-metrics"></a>
# 10. Monitoring and Metrics

## The Analogy

A car dashboard does not show you engine source code. It shows you what matters: speed, fuel, temperature, warnings. You cannot improve what you cannot measure — and you cannot fix what you cannot see.

Production monitoring is your dashboard. Without it, you learn about problems from angry users, not before.

## The Four Golden Signals

Google SRE defined four metrics that, together, describe the health of any service:

| Signal | Definition | Example |
|---|---|---|
| **Latency** | Time to serve a request (p50, p95, p99) | 95th percentile response time > 500ms |
| **Traffic** | Request volume / throughput | 10,000 requests/second |
| **Errors** | Rate of failed requests | HTTP 5xx rate > 1% |
| **Saturation** | How full is the system? | CPU > 80%, memory > 90% |

Instrument all four. Alert on thresholds. Page on sustained breaches, not transient spikes.

## Tools

| Tool | Purpose |
|---|---|
| **Prometheus** | Metrics collection + alerting (pull-based) |
| **Grafana** | Dashboard visualization for Prometheus/InfluxDB |
| **Datadog** | Full-stack observability SaaS |
| **ELK Stack** | Elasticsearch + Logstash + Kibana for log aggregation |
| **Sentry** | Error tracking with stack traces and context |
| **OpenTelemetry** | Vendor-neutral traces + metrics + logs instrumentation |

## Prometheus Metrics in Python

```python
from prometheus_client import Counter, Histogram, start_http_server
import time

# ← define metrics at module level
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],       # ← label dimensions
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0],  # ← SLA-aligned buckets
)

# FastAPI middleware to instrument every request:
from fastapi import Request
import time

async def metrics_middleware(request: Request, call_next):
    start = time.monotonic()
    response = await call_next(request)
    duration = time.monotonic() - start

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
    ).inc()                                  # ← increment counter

    REQUEST_LATENCY.labels(
        endpoint=request.url.path,
    ).observe(duration)                      # ← record latency sample

    return response

start_http_server(9090)   # ← Prometheus scrapes this endpoint
```

📝 **Practice:** [Q24 — URL shortener design](./practice.md#q24--url-shortener-design---design-a-scalable-url-shortener-) · [Q25 — End-to-end service](./practice.md#q25--end-to-end-system---design-a-rate-limited-cached-python-service-)

[↑ Back to Top](#top)

---

<a id="11-example-scalable-url-shortener"></a>
# 11. Example: Scalable URL Shortener

## The Analogy

A URL shortener is the "hello world" of system design interviews — small enough to implement but rich enough to reveal every scaling concern: read-heavy traffic, cache design, ID generation, database choices, and global distribution.

## Components and Flow

```
Client
  │
  ▼
Load Balancer (Nginx / AWS ALB)
  │
  ├── POST /shorten  →  App Server (FastAPI)
  │                         │ write → PostgreSQL (canonical store)
  │                         │ write → Redis cache (warm on create)
  │
  └── GET /{code}    →  App Server (FastAPI)
                            │ read → Redis (cache hit: 99% of traffic)
                            │ miss → PostgreSQL → populate Redis
                            ↓
                         301/302 Redirect → Original URL
```

## Code Sketch

```python
import hashlib
import base64
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import redis
import psycopg2

app = FastAPI()
cache = redis.Redis(host="redis", port=6379)

def generate_code(url: str, length: int = 7) -> str:
    """Generate a short code from URL hash."""
    hash_bytes = hashlib.sha256(url.encode()).digest()
    return base64.urlsafe_b64encode(hash_bytes)[:length].decode()  # ← e.g. "aB3xK9z"


@app.post("/shorten")
async def shorten_url(payload: dict) -> dict:
    original_url = payload["url"]
    code = generate_code(original_url)

    # ← store in PostgreSQL (durable)
    with db_conn.cursor() as cur:
        cur.execute(
            "INSERT INTO urls (code, original_url) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (code, original_url),
        )

    # ← warm the cache immediately (avoid cold start on first redirect)
    cache.setex(f"url:{code}", 86400, original_url)   # ← 24-hour TTL

    return {"short_url": f"https://short.ly/{code}"}


@app.get("/{code}")
async def redirect(code: str) -> RedirectResponse:
    # ← 1. Check Redis (sub-millisecond)
    cached = cache.get(f"url:{code}")
    if cached:
        return RedirectResponse(url=cached.decode(), status_code=302)

    # ← 2. Cache miss: check PostgreSQL
    with db_conn.cursor() as cur:
        cur.execute("SELECT original_url FROM urls WHERE code = %s", (code,))
        row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Short URL not found")

    original_url = row[0]
    cache.setex(f"url:{code}", 86400, original_url)   # ← repopulate cache
    return RedirectResponse(url=original_url, status_code=302)
```

## Scaling Strategy

| Scale | Approach |
|---|---|
| 10K req/day | Single app + PostgreSQL + Redis — done |
| 1M req/day | Add read replicas, horizontal app scaling, CDN for redirects |
| 100M req/day | Shard PostgreSQL by code prefix, regional Redis clusters, global CDN |
| 1B req/day | Dedicated redirect tier (Nginx + Lua) bypassing app servers entirely |

Hot URLs (viral content) account for 99% of redirects. Caching the top 10,000 codes in Redis covers nearly all traffic.

[↑ Back to Top](#top)

---

## 🔥 Summary

System design is not one big thing — it is a collection of disciplines, each targeting a specific failure mode at scale:

| Discipline | Failure mode it prevents |
|---|---|
| Horizontal scaling + stateless | Single-machine capacity ceiling, cascading failures |
| REST + idempotency | Double-processing, ambiguous contracts |
| Rate limiting | Abuse, DDoS, resource exhaustion |
| Caching | Database overload, slow repeated reads |
| Indexing + N+1 avoidance | Query performance collapse under load |
| Async processing | Slow dependencies blocking API response time |
| Load balancing | Single-server bottleneck, uneven resource usage |
| Fault tolerance | Cascading failures from transient dependency issues |
| Security layers | Auth bypass, data exposure, injection attacks |
| Monitoring | Silent degradation, no visibility into production incidents |

**Engineering maturity levels:**

- **Beginner** — builds a working app
- **Intermediate** — understands APIs and databases
- **Advanced** — adds caching, rate limiting, and error handling
- **Senior** — designs distributed, stateless, scalable systems
- **Architect** — designs fault-tolerant, multi-region, observable systems

Python is the tool. Design thinking is the skill.

---

## 📂 Subfolder Deep Dives

| Subfolder | Contents |
|---|---|
| [01_api_design_patterns](./01_api_design_patterns/theory.md) | REST deep dive, pagination patterns, versioning strategies, OpenAPI, gRPC vs REST comparison |
| [02_scalability_caching_patterns](./02_scalability_caching_patterns/theory.md) | Redis patterns, LRU/LFU eviction, rate limiter implementations, sharding strategies, connection pooling |

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.md](./practice.md) |
| ⬅️ Prev Module | [← Production Best Practices](../19_production_best_practices/theory.md) |
| ➡️ Next Module | [→ Data Engineering Applications](../21_data_engineering_applications/theory.md) |

**[🏠 Back to README](../README.md)**

**Prev:** [← Production Best Practices](../19_production_best_practices/theory.md) &nbsp;|&nbsp; **Next:** [Data Engineering Applications →](../21_data_engineering_applications/theory.md)

**Related Topics:** [API Design Patterns](./01_api_design_patterns/theory.md) · [Scalability & Caching](./02_scalability_caching_patterns/theory.md) · [Interview Q&A](./interview.md) · [Cheatsheet](./cheetsheet.md)

[↑ Back to Top](#top)
