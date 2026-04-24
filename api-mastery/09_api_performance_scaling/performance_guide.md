# 13 — API Performance and Scaling

> 📝 **Practice:** [Q51 · api-caching-strategies](../api_practice_questions_100.md#q51--normal--api-caching-strategies)

> 📝 **Practice:** [Q24 · api-rate-limiting-headers](../api_practice_questions_100.md#q24--thinking--api-rate-limiting-headers)

> "Fast by default, scalable by design."

> 📝 **Practice:** [Q75 · mobile-api-optimisation](../api_practice_questions_100.md#q75--design--mobile-api-optimisation)

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
N+1 query detection and fix · database indexes · connection pooling · percentile-based metrics (p50/p95/p99)

**Should Learn** — Important for real projects, comes up regularly:
Redis cache patterns (cache-aside) · circuit breaker pattern · horizontal scaling (stateless design)

**Good to Know** — Useful in specific situations, not always tested:
orjson · exclude_unset · async for I/O-bound paths

**Reference** — Know it exists, look up syntax when needed:
query plan analysis · multi-level caching · query cost modeling

---

## The Problem With Performance Being an Afterthought

Most APIs start life handling a few dozen requests per day. The code works. Tests pass.
It ships.

Three months later, you have ten thousand users. Endpoints that took 80 ms now take
two seconds. The database CPU is at 90%. Your on-call engineer is getting paged at 2 AM.

The problem is almost never the language or the framework. It's the architecture of the
requests themselves — N+1 queries nobody noticed, missing indexes, responses serialized
with fields nobody uses, and a single database connection shared by four app servers.

This chapter is a systematic walkthrough of where API latency comes from and what to do
about each layer.

---

## 1. Where APIs Get Slow — Profiling the Request Lifecycle

> 📝 **Practice:** [Q68 · load-testing-apis](../api_practice_questions_100.md#q68--normal--load-testing-apis)

Before optimizing anything, understand what you are actually optimizing. A request flows
through several stages, and the slowness lives in a specific one:

```
Client
  │
  ▼  Network round-trip to server (typically 1–50 ms)
  │
  ▼  Framework routing + middleware (< 1 ms in FastAPI)
  │
  ▼  Dependency injection / auth check (1–10 ms if DB-backed)
  │
  ▼  Business logic (near zero if no I/O)
  │
  ▼  Database query (5 ms to 5000 ms — this is usually the culprit)
  │
  ▼  Serialization — Pydantic model → JSON (1–50 ms at scale)
  │
  ▼  Network response to client
```

In practice, **database query time is the dominant factor** in the vast majority of slow
API responses. Serialization is second once you're at scale. Everything else is usually
noise.

> 📝 **Practice:** [Q86 · production-api-slow](../api_practice_questions_100.md#q86--design--production-api-slow)

### Adding Timing to Find the Real Bottleneck

Don't guess. Measure. Add a simple timing middleware to understand where time is going:

```python
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api.timing")


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round(duration_ms, 2)
            }
        )

        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
        return response


app.add_middleware(TimingMiddleware)
```

For production profiling, use a proper APM tool (Datadog, New Relic, Sentry Performance).
They show you per-query timing with stack traces, so you can see exactly which endpoint
calls which query and how long it takes.

### The N+1 Query Problem

The most common performance bug in database-backed APIs. It looks like this in
SQLAlchemy:

```python
# SLOW: N+1 queries
@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()          # 1 query: SELECT all orders
    result = []
    for order in orders:
        result.append({
            "id": order.id,
            "total": order.total,
            "customer": order.customer.name  # N queries: one per order (lazy load!)
        })
    return result
```

With 100 orders, this executes 101 queries. With 1000 orders, 1001 queries.

The fix is eager loading — join the related table in the original query:

```python
from sqlalchemy.orm import joinedload

# FAST: 1 query with a JOIN
@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    orders = (
        db.query(Order)
        .options(joinedload(Order.customer))  # JOIN customers in the same query
        .all()
    )
    return [{"id": o.id, "total": o.total, "customer": o.customer.name} for o in orders]
```

One query instead of N+1. At 1000 orders, this is the difference between 1001 roundtrips
to the database and a single roundtrip.

---

## 2. Response Caching — Redis Cache Patterns

> 📝 **Practice:** [Q52 · redis-caching-pattern](../api_practice_questions_100.md#q52--design--redis-caching-pattern)

> 📝 **Practice:** [Q19 · pagination-response-format](../api_practice_questions_100.md#q19--critical--pagination-response-format)

> 📝 **Practice:** [Q12 · cache-control-header](../api_practice_questions_100.md#q12--thinking--cache-control-header)

Caching is the highest-leverage optimization available. If the same data is requested
frequently and changes infrequently, serving it from a memory store instead of recomputing
it on every request can reduce database load by orders of magnitude.

> 📝 **Practice:** [Q53 · cache-invalidation](../api_practice_questions_100.md#q53--thinking--cache-invalidation)

### Cache-Aside for Single Resources

```python
import redis
import json
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

CACHE_TTL = 300  # 5 minutes


@app.get("/products/{product_id}")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    cache_key = f"product:{product_id}"

    # Step 1: Check cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)  # cache hit — no DB call

    # Step 2: Cache miss — query the database
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")

    # Step 3: Serialize and store in cache
    data = {"id": product.id, "name": product.name, "price": float(product.price)}
    redis_client.setex(cache_key, CACHE_TTL, json.dumps(data))

    return data


@app.patch("/products/{product_id}")
async def update_product(product_id: int, update: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Not found")

    for field, value in update.dict(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()

    # Invalidate cache on write
    redis_client.delete(f"product:{product_id}")
    return product
```

### Caching List Endpoints With Query Parameters

List endpoints are trickier — the cache key must encode every filter parameter:

```python
import hashlib

@app.get("/products")
async def list_products(
    category: str = None,
    min_price: float = None,
    max_price: float = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    # Build a deterministic cache key from all parameters
    params = f"cat={category}&min={min_price}&max={max_price}&page={page}&limit={limit}"
    cache_key = f"products:list:{hashlib.md5(params.encode()).hexdigest()}"

    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    total = query.count()
    products = query.offset((page - 1) * limit).limit(limit).all()

    result = {
        "data": [{"id": p.id, "name": p.name, "price": float(p.price)} for p in products],
        "total": total,
        "page": page
    }

    # Shorter TTL for list data (it changes more often than individual records)
    redis_client.setex(cache_key, 60, json.dumps(result))
    return result
```

### Cache TTL Strategy

> 📝 **Practice:** [Q89 · production-rate-limit-good-users](../api_practice_questions_100.md#q89--design--production-rate-limit-good-users)

> 📝 **Practice:** [Q79 · explain-rate-limiting-pm](../api_practice_questions_100.md#q79--interview--explain-rate-limiting-pm)

> 📝 **Practice:** [Q54 · rate-limiting-algorithms](../api_practice_questions_100.md#q54--thinking--rate-limiting-algorithms)

```
Type of data                        Recommended TTL
────────────────────────────────────────────────────
Product catalog, static content     5–60 minutes
User profile data                   1–5 minutes
Leaderboards, aggregates            30–60 seconds
Inventory / stock counts            10–30 seconds
Real-time pricing                   5–10 seconds
Auth tokens, sessions               Match token expiry
```

The right TTL is always a tradeoff between cache freshness and database load. When in
doubt, start with a short TTL (60 seconds) and increase it after monitoring shows the
data is stable.

> 📝 **Practice:** [Q99 · design-rate-limiter](../api_practice_questions_100.md#q99--design--design-rate-limiter)

---

## 3. Database Query Optimization

> 📝 **Practice:** [Q88 · production-stale-data](../api_practice_questions_100.md#q88--design--production-stale-data)

### Add Indexes on Filtered Columns

The most impactful optimization you can make on a slow query is often adding a single
index. Without an index, the database scans every row in the table. With an index, it
jumps directly to matching rows.

```python
# SQLAlchemy model — add Index to frequently filtered columns
from sqlalchemy import Column, Integer, String, Index, Float
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    category = Column(String, index=True)       # frequently filtered
    price = Column(Float)
    status = Column(String, index=True)         # frequently filtered
    created_at = Column(DateTime, index=True)   # frequently sorted

    # Composite index for queries that filter on both category AND status
    __table_args__ = (
        Index("idx_category_status", "category", "status"),
        Index("idx_created_at_status", "created_at", "status"),
    )
```

How to find which queries need indexes:

```sql
-- PostgreSQL: show slow queries (run this periodically)
SELECT
    query,
    calls,
    mean_exec_time AS mean_ms,
    total_exec_time AS total_ms
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Look for sequential scans on large tables:
EXPLAIN ANALYZE SELECT * FROM products WHERE category = 'electronics';
-- If you see "Seq Scan" on a large table, add an index.
-- After adding the index, you should see "Index Scan" instead.
```

### Select Only What You Need

`SELECT *` transfers every column across the network, even columns your code never reads.
At scale this adds up.

```python
# BAD: fetches all columns, including blobs and large text fields
users = db.query(User).all()

# GOOD: fetch only what the response needs
from sqlalchemy import select

users = db.execute(
    select(User.id, User.name, User.email)
    .where(User.active == True)
    .limit(100)
).fetchall()
```

With SQLAlchemy ORM and Pydantic, use `response_model` on your route to document which
fields are returned, and use `load_only` to match:

```python
from sqlalchemy.orm import load_only

@app.get("/users", response_model=List[UserSummary])  # UserSummary has only id, name, email
def list_users(db: Session = Depends(get_db)):
    return (
        db.query(User)
        .options(load_only(User.id, User.name, User.email))
        .filter(User.active == True)
        .all()
    )
```

### Pagination — Cursor Over Offset for Large Datasets

Offset-based pagination (`LIMIT 20 OFFSET 10000`) gets slower as the offset grows.
The database must count and skip 10,000 rows before returning the 20 you want.

Cursor-based pagination jumps directly to the right starting point using an indexed
column, regardless of how many records come before it:

```python
from fastapi import Query
from typing import Optional


# Offset-based — simple but degrades at high page numbers
@app.get("/users/offset")
def list_users_offset(page: int = 1, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(User).offset((page - 1) * limit).limit(limit).all()
    # Problem: page=500 means OFFSET 9980 — DB must skip 9980 rows


# Cursor-based — fast at any depth
@app.get("/users")
def list_users_cursor(
    cursor: Optional[int] = Query(None, description="Last seen user ID"),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(User).order_by(User.id)

    if cursor:
        query = query.filter(User.id > cursor)  # jump to position directly

    users = query.limit(limit + 1).all()        # fetch one extra to check if more exist

    has_more = len(users) > limit
    users = users[:limit]

    return {
        "data": users,
        "next_cursor": users[-1].id if has_more else None,
        "has_more": has_more
    }
```

> 📝 **Practice:** [Q15 · pagination-strategies](../api_practice_questions_100.md#q15--normal--pagination-strategies)


Cursor pagination requires a stable sort order (always sort by the cursor column) and
is best suited for "infinite scroll" style UIs. Use offset pagination when users need
to jump to arbitrary pages.

### Batch Queries to Avoid N+1

When you need to load related data for a list of objects, fetch it in one query rather
than one query per object:

```python
# BAD: one query per order to get customer name
orders = db.query(Order).limit(100).all()
for order in orders:
    customer = db.query(User).filter(User.id == order.user_id).first()  # 100 queries!

# GOOD: one query to get all needed customers
orders = db.query(Order).limit(100).all()
user_ids = {order.user_id for order in orders}
users = db.query(User).filter(User.id.in_(user_ids)).all()
user_map = {u.id: u for u in users}

for order in orders:
    customer = user_map[order.user_id]  # dict lookup, no DB call
```

---

## Connection Pooling — Why Default Settings Kill You

Every database call requires a connection. Creating a connection is expensive:

```
Without pooling:
  Request arrives → open TCP connection → authenticate → run query → close connection
  Time cost:  ~10-50ms for connection setup  +  actual query time

With pooling:
  Request arrives → grab idle connection from pool → run query → return to pool
  Time cost:  ~0.1ms (pool checkout) + actual query time
```

A connection pool maintains a set of pre-established connections that are reused.

---

### How It Works

```
Connection Pool (max_size=10):

┌─────────────────────────────────────────────────────┐
│  conn_1  [IDLE]   conn_2  [IN USE]  conn_3  [IDLE]  │
│  conn_4  [IDLE]   conn_5  [IN USE]  conn_6  [IDLE]  │
│  conn_7  [IDLE]   conn_8  [IDLE]    conn_9  [IDLE]  │
│  conn_10 [IDLE]                                     │
└─────────────────────────────────────────────────────┘

Request → checks out conn_1 (IDLE)
Query runs using conn_1
Request completes → returns conn_1 to pool (IDLE again)
```

If all connections are in use, the request **waits** in a queue until one is returned.
If the wait exceeds `pool_timeout`, it raises a connection timeout error.

---

### The Default Settings Problem

SQLAlchemy default pool size: **5 connections**.
Django default: **no pooling** (new connection per request!).

**At scale:**

```
1,000 concurrent requests → all waiting for 5 pool slots → timeouts → errors
```

---

### Pool Sizing Formula

The widely-used formula for databases (from HikariCP research):

```
pool_size = (number_of_cores × 2) + 1

Examples:
  4-core server: (4 × 2) + 1 = 9 connections
  8-core server: (8 × 2) + 1 = 17 connections
```

Why? A database thread spends ~50% of time waiting on I/O.
Doubling cores + 1 keeps all cores busy while some connections wait.

**SQLAlchemy configuration:**

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@host/db",
    pool_size=9,          # core_count × 2 + 1
    max_overflow=5,       # additional connections when pool is full (temporary)
    pool_timeout=30,      # seconds to wait before timeout
    pool_recycle=1800,    # recycle connections after 30 min (prevent stale)
    pool_pre_ping=True,   # test connection before use (detect dead connections)
)
```

**FastAPI with async SQLAlchemy:**

```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@host/db",
    pool_size=9,
    max_overflow=5,
    pool_timeout=30,
)
```

---

### Connection Pool Anti-Patterns

```
❌ Creating engine inside each request:
   @app.get("/data")
   async def endpoint():
       engine = create_engine(...)   # new pool on every request!
       # Fix: create engine once at startup

❌ Not returning connections:
   conn = pool.getconn()
   result = conn.execute(query)
   # forgot conn.close() or return to pool → pool exhaustion

❌ Pool too large:
   pool_size = 1000
   # Databases have connection limits. PostgreSQL default: 100.
   # 10 app servers × 100 pool = 1000 connections → exceeds DB limit
```

---

## 4. Connection Pool Sizing

Every database connection has a cost: memory on the DB server, a file descriptor on the
app server, overhead in the DB's connection tracking. You need enough connections to
keep your workers busy, but not so many that you exhaust the database's capacity.

The math is straightforward:

```
Workers × Connections per worker = Connection pool size needed

Example:
  4 Gunicorn workers
  × 10 SQLAlchemy connections per worker (pool_size=10)
  = 40 connections to the database

PostgreSQL default: max_connections=100
Headroom for migrations, admin tools, monitoring: 10–20 connections
Usable for app: 80–90 connections

For 4 workers with pool_size=10 → 40 connections. Safe.
For 8 workers with pool_size=10 → 80 connections. At the limit.
For 16 workers with pool_size=10 → 160 connections. Will fail.
```

Configure the pool in SQLAlchemy:

```python
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=10,         # number of connections to keep open
    max_overflow=5,       # allow up to 5 extra connections when pool is full
    pool_timeout=30,      # wait up to 30s for a connection before raising
    pool_pre_ping=True,   # test connections before using them (catches stale connections)
    pool_recycle=3600,    # recycle connections after 1 hour (prevent MySQL "gone away")
)
```

If you are running many workers and hitting connection limits, use a connection pooler
like **PgBouncer** in front of PostgreSQL. PgBouncer multiplexes thousands of app
connections onto a smaller number of real database connections.

---

## 5. FastAPI-Specific Optimizations

### Skip Serializing Null Fields

By default, Pydantic serializes every field in your response model, including fields
that are `None`. With `response_model_exclude_unset=True`, only fields that were
explicitly set are included in the response — smaller payloads, faster serialization.

```python
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


# Default: always serializes all fields, even null ones
# Response: {"id": 1, "name": "Alice", "email": "...", "phone": null, "avatar_url": null, "bio": null}
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    ...


# With exclude_unset: only serializes fields that were set
# Response: {"id": 1, "name": "Alice", "email": "..."}
@app.get("/users/{user_id}", response_model=UserResponse, response_model_exclude_unset=True)
def get_user_slim(user_id: int):
    ...
```

At scale, removing null fields from every response meaningfully reduces bandwidth and
serialization time.

### Faster JSON With `orjson`

The default `json` library in Python is implemented in pure Python. `orjson` is a
Rust-based drop-in replacement that is roughly 5–10x faster for typical API payloads.

```python
# pip install orjson
from fastapi.responses import ORJSONResponse

# Option 1: default all responses to orjson
app = FastAPI(default_response_class=ORJSONResponse)

# Option 2: use it on specific routes
@app.get("/large-dataset", response_class=ORJSONResponse)
def large_dataset():
    return {"data": [{"id": i, "value": i * 2} for i in range(10000)]}
```

The difference is negligible for small responses. For endpoints returning thousands of
objects, the speedup is measurable.

### Use Async Routes for I/O-Bound Work

As covered in chapter 11, async routes avoid thread pool overhead for I/O-bound
operations. When your API makes outbound HTTP calls (to other services, external APIs),
using an async HTTP client like `httpx` keeps the event loop free:

```python
import httpx

@app.get("/aggregate")
async def aggregate_data():
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Fire both requests concurrently — not sequentially
        user_task = client.get("https://internal.service/users")
        order_task = client.get("https://internal.service/orders")

        user_resp, order_resp = await asyncio.gather(user_task, order_task)

    return {
        "users": user_resp.json(),
        "orders": order_resp.json()
    }
```

Using `asyncio.gather` here fires both requests simultaneously. Sequential `await`
calls would take twice as long.

---

## 6. Horizontal Scaling

Vertical scaling — bigger server, more RAM — has a ceiling. Horizontal scaling — more
servers — does not.

A well-designed API scales horizontally by being stateless. Every request carries
everything the server needs to process it (auth token, request body). No server-side
session. Any server in the pool can handle any request.

```
              Internet
                 │
                 ▼
        ┌────────────────┐
        │  Load Balancer │  (nginx, ALB, Cloudflare)
        │  Round-robin   │
        └────────────────┘
          │      │      │
          ▼      ▼      ▼
       [API 1] [API 2] [API 3]   ← stateless; any handles any request
          │      │      │
          └──────┴──────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
    [Database]         [Redis]   ← shared state lives here
    (Primary +         (cache, rate limiting,
     Read Replicas)     sessions)
```

### What Must Be Shared

When you add a second API server, anything that was stored in the first server's memory
becomes inaccessible to the second server. Move it to Redis:

```
Stored in Redis (not in-process):
  - Rate limit counters (chapter 11)
  - Response cache
  - Session data (if you use sessions)
  - Distributed locks
  - WebSocket state (with Redis pub/sub for cross-server broadcast)
```

### Read Replicas for Heavy Read Loads

If 90% of your queries are reads (most APIs), you can add read replicas to distribute
the load. Write to the primary; read from replicas:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Two engines: one primary (writes), one replica (reads)
write_engine = create_engine(os.environ["PRIMARY_DB_URL"], pool_size=10)
read_engine = create_engine(os.environ["REPLICA_DB_URL"], pool_size=20)  # more read connections

WriteSession = sessionmaker(bind=write_engine)
ReadSession = sessionmaker(bind=read_engine)


def get_write_db():
    db = WriteSession()
    try:
        yield db
    finally:
        db.close()


def get_read_db():
    db = ReadSession()
    try:
        yield db
    finally:
        db.close()


# Use write session for mutations
@app.post("/orders")
def create_order(order: OrderCreate, db: Session = Depends(get_write_db)):
    ...


# Use read session for queries (can handle much more traffic)
@app.get("/products")
def list_products(db: Session = Depends(get_read_db)):
    ...
```

---

## 7. Key Metrics to Monitor

### Latency — Use Percentiles, Not Averages

Averages hide the problem. An endpoint with a 50 ms average might be returning 200 ms to
10% of users — that's the population you need to fix.

```
p50 (median)   → 50% of requests are faster than this
p95            → 95% of requests are faster than this
p99            → 99% of requests are faster than this

Example:
  p50 = 45 ms    → half your users see 45 ms or better
  p95 = 180 ms   → 5% see 180 ms or worse
  p99 = 850 ms   → 1% see nearly a second — these users are churning

Target (typical SaaS API):
  p50 < 100 ms
  p95 < 300 ms
  p99 < 1000 ms
```

If your p99 is high but your p50 is fine, look for occasional slow queries (lock
contention, cache misses, large payloads). If your p50 is slow, the problem is
systematic.

### Error Rate

Track the percentage of requests returning 5xx (server errors) and 4xx (client errors).

```
Error rate = (5xx responses / total responses) × 100

Thresholds to alert on:
  5xx > 0.1%   → something is broken
  5xx > 1%     → incident — page someone
  429 spike    → a client is misbehaving (or you're under attack)
  401/403 spike → authentication issue or credential stuffing attempt
```

### Requests Per Second (RPS) and Throughput

Track RPS over time. Sudden drops can indicate a deployment issue. Sudden spikes can
indicate viral traffic or a DoS attack.

Know your capacity before you need it:

```bash


# Quick load test with wrk
wrk -t4 -c100 -d30s http://localhost:8000/products

# Or with locust for more realistic scenarios:
# locustfile.py defines user behavior patterns
locust -f locustfile.py --host=http://localhost:8000
```

> 📝 **Practice:** [Q21 · etag-conditional-requests](../api_practice_questions_100.md#q21--thinking--etag-conditional-requests)


### Database Connection Pool Usage

```python
# Add this to your /health endpoint or expose as a metric
@app.get("/health/detailed")
def health_detailed():
    pool = engine.pool
    return {
        "status": "ok",
        "db_pool": {
            "size": pool.size(),
            "checked_in": pool.checkedin(),   # idle connections
            "checked_out": pool.checkedout(), # in-use connections
            "overflow": pool.overflow(),      # extra connections beyond pool_size
        }
    }
```

If `checked_out` is consistently near your `pool_size`, you are at capacity. Either
increase `pool_size`, add app servers, or optimize queries to hold connections for less
time.

---

## Performance Optimization Checklist

Work through these in order — they are roughly sorted by impact:

```
DATABASE
  [ ] N+1 queries eliminated (use joinedload or batch fetching)
  [ ] Indexes on every filtered/sorted column
  [ ] SELECT only needed columns (load_only, specific select())
  [ ] Pagination uses cursor for large datasets
  [ ] Connection pool sized correctly for your worker count
  [ ] Slow query log enabled and reviewed regularly

CACHING
  [ ] Frequently read, rarely written data is cached in Redis
  [ ] Cache keys include all relevant parameters
  [ ] Cache has a TTL appropriate to data freshness requirements
  [ ] Cache is invalidated on writes (delete the key)
  [ ] Cache hit rate is monitored (aim for > 80% on hot endpoints)

FASTAPI / SERIALIZATION
  [ ] response_model_exclude_unset=True on endpoints with optional fields
  [ ] orjson used as default response class
  [ ] Async routes used for I/O-bound handlers
  [ ] Sync routes used for CPU-bound work (PIL, pandas)
  [ ] asyncio.gather for concurrent outbound requests

SCALING
  [ ] API servers are stateless (no in-process session state)
  [ ] Rate limit counters stored in Redis (not in-process)
  [ ] Read replicas used for read-heavy endpoints
  [ ] Connection pooler (PgBouncer) in front of Postgres at high scale

MONITORING
  [ ] p50, p95, p99 latency tracked per endpoint
  [ ] Error rate tracked (5xx, 4xx separately)
  [ ] DB connection pool utilization tracked
  [ ] Cache hit rate tracked
  [ ] Slow query threshold set (alert if p99 > 1s)
```

---

## Summary

```
Where slowness comes from (most to least common):
  1. Database — N+1 queries, missing indexes, no pagination
  2. Serialization — unnecessary fields, slow JSON library
  3. Network — nothing you can control on the server side
  4. Framework overhead — negligible in FastAPI

High-impact fixes, in order:
  1. Add indexes on filtered columns (5-minute fix, huge impact)
  2. Eliminate N+1 queries with joinedload or batch fetching
  3. Cache frequently-read data in Redis with a reasonable TTL
  4. Use cursor pagination for large tables
  5. Right-size your connection pool
  6. Switch to orjson + response_model_exclude_unset=True

Scaling pattern:
  Stateless API servers behind a load balancer
  Shared Redis for rate limits, cache, sessions
  Read replicas for read-heavy workloads
  PgBouncer when connection count becomes the bottleneck

Metrics that matter:
  p50, p95, p99 latency — not average
  5xx error rate — alert above 0.1%
  DB connection pool utilization
  Cache hit rate
```

---

## 🔌 Circuit Breaker — Stop Cascading Failures

> Imagine your house's electrical circuit breaker. When a wire overloads, the breaker trips to prevent fire spreading to the rest of the house. The software circuit breaker does the same: when a downstream service is failing, stop sending requests and fail fast — before the failure cascades everywhere.

The **circuit breaker pattern** wraps calls to external services and tracks failure rates. When failures exceed a threshold, the circuit "opens" and immediately returns an error without hitting the failing service — giving it time to recover.

**Three states:**
```
CLOSED  →  Normal operation. Requests pass through. Failures are counted.
OPEN    →  Too many failures. Requests fail immediately (no network call).
HALF-OPEN → After timeout, let a test request through. If it succeeds → CLOSED.
                                                       If it fails   → OPEN again.
```

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED    = "closed"      # normal — requests pass through
    OPEN      = "open"        # tripped — fail fast
    HALF_OPEN = "half_open"   # testing — one probe request allowed

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold  # ← failures before opening
        self.timeout = timeout                      # ← seconds before trying again
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN  # ← try probe request
            else:
                raise Exception("Circuit OPEN — service unavailable")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED    # ← reset on success

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN  # ← trip the breaker

# Usage:
cb = CircuitBreaker(failure_threshold=3, timeout=30)

def call_payment_service(order_id):
    return cb.call(payment_client.charge, order_id)
```

**FastAPI integration with tenacity + custom circuit breaker:**

```python
from tenacity import retry, stop_after_attempt, wait_exponential, CircuitBreaker

# Simple approach: retry with backoff (for transient failures)
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def fetch_user_data(user_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE}/users/{user_id}", timeout=5.0)
        response.raise_for_status()
        return response.json()

# Full pattern in production: use a library like 'circuitbreaker' or 'pybreaker'
# pip install pybreaker
import pybreaker

db_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)

@db_breaker
def query_database(query):
    return db.execute(query)
```

**Circuit breaker vs retry — when to use each:**

```
Retry:           Transient failures (brief network blip, 503 under load)
Circuit Breaker: Systemic failures (service down, database unavailable)

Rule: Retry for brief spikes. Circuit Breaker for sustained failures.
Combine: Circuit Breaker wraps the function, Retry is inside.
```

**Key metrics to monitor:**
- Circuit open rate (how often it trips)
- Error rate before/after circuit opens
- Response time distribution (circuit open = near-zero latency for failures)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← API Versioning](../08_versioning_standards/versioning_strategy.md) &nbsp;|&nbsp; **Next:** [Testing APIs →](../10_testing_documentation/testing_apis.md)

**Related Topics:** [FastAPI & Databases](../07_fastapi/database_guide.md) · [Testing APIs](../10_testing_documentation/testing_apis.md) · [Production Deployment](../12_production_deployment/deployment_guide.md) · [OpenTelemetry](../19_opentelemetry/opentelemetry_guide.md)
