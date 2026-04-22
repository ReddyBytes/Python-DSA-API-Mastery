# ⚡ API Performance & Scaling — Cheatsheet

## Learning Priority

| Priority | Topics |
|---|---|
| Must Learn | N+1 query detection and fix · database indexes · connection pooling · p50/p95/p99 metrics |
| Should Learn | Redis cache-aside pattern · circuit breaker · horizontal scaling (stateless design) |
| Good to Know | orjson · `exclude_unset` · async for I/O-bound paths |
| Reference | query plan analysis · multi-level caching · query cost modeling |

---

## Where APIs Get Slow (ranked by frequency)

```
1. Database — N+1 queries, missing indexes, no pagination   ← almost always here
2. Serialization — unnecessary fields, slow JSON library
3. Network — little you can control server-side
4. Framework overhead — negligible in FastAPI
```

---

## N+1 Query Pattern + Fix

```python
# BAD: N+1 — 1 query for orders + N queries for customers
@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()           # 1 query
    for order in orders:
        _ = order.customer.name             # N queries (lazy load!)

# GOOD: eager loading — 1 query with JOIN
from sqlalchemy.orm import joinedload

@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    orders = (
        db.query(Order)
        .options(joinedload(Order.customer))  # JOIN in same query
        .all()
    )
```

```python
# GOOD: batch loading — 2 queries total instead of N+1
orders = db.query(Order).limit(100).all()
user_ids = {o.user_id for o in orders}
users = db.query(User).filter(User.id.in_(user_ids)).all()  # 1 query for all
user_map = {u.id: u for u in users}

for order in orders:
    customer = user_map[order.user_id]      # dict lookup — no DB call
```

---

## Eager Loading Syntax

```python
from sqlalchemy.orm import joinedload, selectinload, subqueryload

# JOIN — good for many-to-one (order → customer)
.options(joinedload(Order.customer))

# SELECT IN — good for one-to-many (order → items list)
.options(selectinload(Order.items))

# Nested eager loading
.options(
    joinedload(Order.customer),
    selectinload(Order.items).joinedload(OrderItem.product)
)
```

---

## Connection Pool Configuration

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@host/db",
    pool_size=9,          # formula: (CPU cores × 2) + 1
    max_overflow=5,       # extra connections when pool is full (temporary)
    pool_timeout=30,      # seconds to wait for a free connection
    pool_recycle=1800,    # recycle after 30 min (prevent stale connections)
    pool_pre_ping=True,   # test connection health before use
)
```

### Pool Sizing Formula
```
pool_size = (number_of_CPU_cores × 2) + 1

4-core server:  (4 × 2) + 1 = 9
8-core server:  (8 × 2) + 1 = 17
```

### Total connections consumed
```
app_servers × workers_per_server × pool_size = total DB connections

Example:
  2 servers × 4 workers × 9 pool_size = 72 connections
  PostgreSQL default max: 100
  Reserve ~20 for admin/migrations → 80 usable
  72 < 80 ✓  (safe)
```

---

## Redis Cache-Aside Pattern

```python
import redis, json
from fastapi import Depends, HTTPException

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
CACHE_TTL = 300   # 5 minutes

@app.get("/products/{product_id}")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    cache_key = f"product:{product_id}"

    # 1. Check cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)               # cache hit — no DB call

    # 2. Cache miss — query DB
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Not found")

    # 3. Store in cache
    data = {"id": product.id, "name": product.name, "price": float(product.price)}
    redis_client.setex(cache_key, CACHE_TTL, json.dumps(data))
    return data

@app.patch("/products/{product_id}")
async def update_product(product_id: int, update: ProductUpdate, db=Depends(get_db)):
    # ... update logic ...
    redis_client.delete(f"product:{product_id}")  # invalidate cache on write
```

---

## Cache TTL Strategy

| Data type | Recommended TTL |
|---|---|
| Product catalog, static content | 5–60 minutes |
| User profile data | 1–5 minutes |
| Leaderboards, aggregates | 30–60 seconds |
| Inventory / stock counts | 10–30 seconds |
| Real-time pricing | 5–10 seconds |
| Auth tokens, sessions | Match token expiry |

---

## Pagination Impact on Performance

```python
# SLOW at deep pages — DB must scan and skip 10,000 rows
db.query(User).offset(10000).limit(20).all()   # OFFSET 10000 = full scan

# FAST — uses index, jumps directly to position
db.query(User).filter(User.id > last_seen_id).limit(20).all()
```

**Use cursor pagination for:** tables with 100k+ rows, feeds, timelines.
**Use offset pagination for:** admin UIs, reports, "jump to page N" UIs.

---

## Index Strategy Table

```python
# SQLAlchemy — add indexes on filtered/sorted columns
class Product(Base):
    __tablename__ = "products"
    id         = Column(Integer, primary_key=True)
    name       = Column(String)
    category   = Column(String, index=True)        # filtered frequently
    status     = Column(String, index=True)        # filtered frequently
    price      = Column(Float)
    created_at = Column(DateTime, index=True)      # sorted frequently

    __table_args__ = (
        # Composite — for queries that filter on BOTH category AND status
        Index("idx_category_status", "category", "status"),
        Index("idx_created_at_status", "created_at", "status"),
    )
```

```sql
-- Find slow queries in PostgreSQL
SELECT query, calls, mean_exec_time AS mean_ms
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Check if a query uses an index
EXPLAIN ANALYZE SELECT * FROM products WHERE category = 'electronics';
-- "Seq Scan" = no index (add one)
-- "Index Scan" = index is being used ✓
```

---

## FastAPI-Specific Optimizations

```python
# Exclude unset optional fields (smaller payloads)
@app.get("/users/{id}", response_model=UserResponse, response_model_exclude_unset=True)
def get_user(id: int): ...

# Faster JSON serialization (Rust-based)
from fastapi.responses import ORJSONResponse
app = FastAPI(default_response_class=ORJSONResponse)

# Async routes for I/O-bound work (avoids thread pool overhead)
import asyncio, httpx

@app.get("/aggregate")
async def aggregate():
    async with httpx.AsyncClient() as client:
        # Fire both concurrently — not sequentially
        users, orders = await asyncio.gather(
            client.get("https://internal/users"),
            client.get("https://internal/orders"),
        )
    return {"users": users.json(), "orders": orders.json()}
```

---

## Horizontal Scaling Pattern

```
              Internet
                 │
        ┌────────┴────────┐
        │  Load Balancer  │
        └────────┬────────┘
          │      │      │
       [API 1] [API 2] [API 3]   ← stateless; any handles any request
          └──────┴──────┘
                 │
        ┌────────┴────────┐
        │                 │
     [Database]        [Redis]
  (Primary + Replicas)  (cache, rate limits, sessions)
```

**Stateless requirement:** no in-process session state. Move to Redis:
- Rate limit counters
- Response cache
- Session data
- Distributed locks

---

## Percentile Metrics (use these, not averages)

```
p50 (median)  → 50% of requests faster than this
p95           → 95% of requests faster than this
p99           → 99% of requests faster than this

Target (typical SaaS API):
  p50 < 100 ms
  p95 < 300 ms
  p99 < 1000 ms

If p99 is slow but p50 is fine:
  → occasional slow queries (lock contention, cache misses)
If p50 is slow:
  → systematic problem (missing index, N+1, bad query)
```

---

## Circuit Breaker Pattern

```python
# Three states
CLOSED   → normal, requests pass through, failures counted
OPEN     → too many failures, fail fast (no network call)
HALF_OPEN → after timeout, probe request: success → CLOSED, fail → OPEN

# With pybreaker (pip install pybreaker)
import pybreaker

db_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)

@db_breaker
def query_database(query):
    return db.execute(query)

# With tenacity (retries with backoff)
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def call_external_service():
    ...
```

| Pattern | Use for |
|---|---|
| Retry with backoff | Transient failures (brief network blip, 503 under load) |
| Circuit breaker | Systemic failures (service down, DB unavailable) |

---

## Performance Checklist

```
DATABASE
  [ ] N+1 queries eliminated (joinedload or batch fetching)
  [ ] Indexes on filtered/sorted columns
  [ ] SELECT only needed columns (load_only, specific selects)
  [ ] Cursor pagination for large tables
  [ ] Connection pool sized correctly
  [ ] Slow query log enabled

CACHING
  [ ] Frequently-read, rarely-written data cached in Redis
  [ ] Cache keys include all relevant params
  [ ] TTL appropriate to data freshness
  [ ] Cache invalidated on writes

FASTAPI
  [ ] response_model_exclude_unset=True for sparse responses
  [ ] orjson as default response class
  [ ] Async routes for I/O-bound handlers
  [ ] asyncio.gather for concurrent outbound calls

SCALING
  [ ] API servers are stateless (no in-process sessions)
  [ ] Rate limit counters in Redis
  [ ] Read replicas for read-heavy endpoints
```

---

## Navigation

**[Back to README](../README.md)**

**Theory:** [performance_guide.md](./performance_guide.md)

**Prev:** [← Versioning](../08_versioning_standards/cheatsheet.md) &nbsp;|&nbsp; **Next:** [Testing & Docs →](../10_testing_documentation/cheatsheet.md)

**Related:** [07 FastAPI](../07_fastapi/cheatsheet.md) · [10 Testing](../10_testing_documentation/cheatsheet.md) · [12 Production Deployment](../12_production_deployment/)
