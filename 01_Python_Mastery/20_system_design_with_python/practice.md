# System Design with Python — Practice

> 25 questions covering API design, caching, rate limiting, circuit breaker, connection pooling, task queues, and two capstone problems.

---

## API Design — Q1–Q8

---

### Q1 · REST Endpoints — Name REST endpoints for a blog 🟢

Design all CRUD endpoints for a `posts` resource plus nested `comments`. Give HTTP method + URL + success status code for each.

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

<details><summary>💡 Hint</summary>Plural nouns. Nested: /posts/{id}/comments. Deep dive: 01_api_design_patterns/theory.md</details>

<details><summary>✅ Answer</summary>

```
GET    /posts               200
POST   /posts               201
GET    /posts/{id}          200
PUT    /posts/{id}          200
PATCH  /posts/{id}          200
DELETE /posts/{id}          204
GET    /posts/{id}/comments 200
POST   /posts/{id}/comments 201
```
**Why:** REST = nouns + HTTP verbs. Status codes communicate outcome without parsing the body.
</details>

---

### Q2 · HTTP Status Codes — Match operations to status codes 🟢

Match each scenario to the correct HTTP status code:
a) Resource not found | b) Created successfully | c) Input fails validation | d) Duplicate email | e) Not authenticated | f) Authenticated but no permission | g) Rate limit hit

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

<details><summary>💡 Hint</summary>404, 201, 422, 409, 401, 403, 429</details>

<details><summary>✅ Answer</summary>

```
a) 404 Not Found
b) 201 Created
c) 422 Unprocessable Entity
d) 409 Conflict
e) 401 Unauthorized
f) 403 Forbidden
g) 429 Too Many Requests
```
**Why:** Standardized status codes allow any HTTP client to handle errors programmatically.
</details>

---

### Q3 · Offset Pagination — Implement offset pagination 🟡

Write `paginate(data, offset, limit)` that returns `{data, pagination: {offset, limit, total}}`.

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

<details><summary>💡 Hint</summary>data[offset:offset+limit]; total = len(data)</details>

<details><summary>✅ Answer</summary>

```python
def paginate(data: list, offset: int = 0, limit: int = 10) -> dict:
    return {
        "data": data[offset: offset + limit],
        "pagination": {"offset": offset, "limit": limit, "total": len(data)},
    }
```
**Why:** Without pagination, a list endpoint on large data returns millions of rows.
</details>

---

### Q4 · Cursor Pagination — Implement cursor-based pagination 🟡

Write `paginate_cursor(data, cursor, limit)` where `cursor` is a base64-encoded `{"id": N}`. Return `{data, next_cursor, has_more}`.

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

<details><summary>💡 Hint</summary>Decode cursor to find start position. Encode last item id as next_cursor.</details>

<details><summary>✅ Answer</summary>

```python
import base64, json

def encode_cursor(id_val: int) -> str:
    return base64.b64encode(json.dumps({"id": id_val}).encode()).decode()

def decode_cursor(cursor: str) -> int:
    return json.loads(base64.b64decode(cursor.encode()))["id"]

def paginate_cursor(data: list, cursor: str = None, limit: int = 10) -> dict:
    start = 0
    if cursor:
        last_id = decode_cursor(cursor)
        start   = next((i + 1 for i, d in enumerate(data) if d["id"] == last_id), 0)
    page       = data[start: start + limit]
    next_cursor = encode_cursor(page[-1]["id"]) if len(page) == limit else None
    return {"data": page, "next_cursor": next_cursor, "has_more": next_cursor is not None}
```
**Why:** Cursor pagination is stable — no skipped/duplicated rows when records are inserted during pagination.
</details>

---

### Q5 · API Versioning — Add URL versioning to an endpoint 🟡

Add `/v1/items/{id}` and `/v2/items/{id}` to a FastAPI app. v1 returns flat format; v2 wraps in `{"item": {...}}`.

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

<details><summary>💡 Hint</summary>APIRouter(prefix="/v1"), APIRouter(prefix="/v2"), app.include_router()</details>

<details><summary>✅ Answer</summary>

```python
from fastapi import FastAPI, APIRouter
app = FastAPI()
v1 = APIRouter(prefix="/v1")
v2 = APIRouter(prefix="/v2")

@v1.get("/items/{item_id}")
def item_v1(item_id: int): return {"id": item_id, "name": "Widget"}

@v2.get("/items/{item_id}")
def item_v2(item_id: int): return {"item": {"id": item_id, "name": "Widget"}}

app.include_router(v1)
app.include_router(v2)
```
**Why:** URL versioning makes version visible in logs, browser, and curl — easiest to debug.
</details>

---

### Q6 · Error Envelope — RFC 7807 error response 🟡

Write `problem_response(status, title, detail)` returning a `JSONResponse` following RFC 7807.

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

<details><summary>💡 Hint</summary>Fields: type, title, status (int), detail</details>

<details><summary>✅ Answer</summary>

```python
from fastapi.responses import JSONResponse

def problem_response(status: int, title: str, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "type":   f"https://api.example.com/errors/{status}",
            "title":  title,
            "status": status,
            "detail": detail,
        }
    )
```
**Why:** RFC 7807 is the standard error shape. Consistent errors allow programmatic handling without string parsing.
</details>

---

### Q7 · Idempotency Key — Prevent duplicate orders 🟡

Write a `POST /orders` route that uses an `Idempotency-Key` header to prevent double submission. Use a dict as the store.

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

<details><summary>💡 Hint</summary>Check _store[key] before processing. Store result after processing.</details>

<details><summary>✅ Answer</summary>

```python
from fastapi import FastAPI, Header
import uuid

app = FastAPI()
_store = {}

@app.post("/orders")
def create_order(amount: float, idempotency_key: str = Header(None)):
    if idempotency_key and idempotency_key in _store:
        return _store[idempotency_key]

    result = {"order_id": str(uuid.uuid4()), "amount": amount, "status": "created"}
    if idempotency_key:
        _store[idempotency_key] = result
    return result
```
**Why:** Idempotency keys are essential for any payment or state-mutating endpoint that clients might retry.
</details>

---

### Q8 · Rate Limit Headers — Add X-RateLimit-* headers 🟡

Write a FastAPI middleware that adds `X-RateLimit-Limit`, `X-RateLimit-Remaining` headers to every response, and returns 429 with `Retry-After` when limit is exceeded. Use 10 req/min per IP.

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

<details><summary>💡 Hint</summary>Middleware: track timestamps per IP in a defaultdict. Slide the window on each request.</details>

<details><summary>✅ Answer</summary>

```python
from fastapi import FastAPI, Request, Response
import time, collections

app = FastAPI()
LIMIT, WINDOW = 10, 60
_log = collections.defaultdict(list)

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    ip  = request.client.host
    now = time.time()
    _log[ip] = [t for t in _log[ip] if now - t < WINDOW]
    if len(_log[ip]) >= LIMIT:
        return Response(status_code=429, headers={
            "X-RateLimit-Limit": str(LIMIT),
            "X-RateLimit-Remaining": "0",
            "Retry-After": str(WINDOW),
        })
    _log[ip].append(now)
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"]     = str(LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(LIMIT - len(_log[ip]))
    return response
```
**Why:** Rate limit headers let clients self-throttle before getting a 429.
</details>

---

## Caching — Q9–Q15

---

### Q9 · Dict TTL Cache — Implement a TTL cache class 🟢

Write `TTLCache` with `get(key)` and `set(key, value, ttl)`. Expired entries return None.

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

<details><summary>💡 Hint</summary>Store (value, expiry_time). Check time.time() < expiry.</details>

<details><summary>✅ Answer</summary>

```python
import time

class TTLCache:
    def __init__(self):
        self._store = {}

    def set(self, key, value, ttl: float):
        self._store[key] = (value, time.time() + ttl)

    def get(self, key):
        if key not in self._store: return None
        v, exp = self._store[key]
        if time.time() > exp:
            del self._store[key]; return None
        return v
```
**Why:** TTL is the most important property of any cache entry — without it, caches grow forever and serve stale data.
</details>

---

### Q10 · @lru_cache — Memoize Fibonacci 🟢

Write `fib(n)` with `@lru_cache`. Print cache info after calling `fib(10)` twice. Then clear and confirm.

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

<details><summary>💡 Hint</summary>@lru_cache(maxsize=None) for unlimited; .cache_info(), .cache_clear()</details>

<details><summary>✅ Answer</summary>

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n < 2: return n
    return fib(n-1) + fib(n-2)

fib(10); fib(10)
print(fib.cache_info())   # hits=1
fib.cache_clear()
print(fib.cache_info())   # currsize=0
```
**Why:** @lru_cache turns exponential recursion into linear with one line.
</details>

---

### Q11 · LRU Cache — OrderedDict LRU 🟡

Write `LRUCache(capacity)` with O(1) `get` and `put`. Verify eviction order.

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

<details><summary>💡 Hint</summary>move_to_end(key) on access; popitem(last=False) to evict LRU</details>

<details><summary>✅ Answer</summary>

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self._c = OrderedDict()

    def get(self, key):
        if key not in self._c: return None
        self._c.move_to_end(key)
        return self._c[key]

    def put(self, key, value):
        if key in self._c: self._c.move_to_end(key)
        self._c[key] = value
        if len(self._c) > self.capacity: self._c.popitem(last=False)
```
**Why:** Classic interview problem. OrderedDict + move_to_end = O(1) access and eviction.
</details>

---

### Q12 · Cache-Aside — Write cache-aside with mock Redis 🟡

Write `get_item(item_id)` using cache-aside. Use a dict as mock Redis. Show cache hit on second call.

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

<details><summary>💡 Hint</summary>Check cache first. On miss, fetch DB, store in cache with expiry.</details>

<details><summary>✅ Answer</summary>

```python
import time
_cache = {}

def db_fetch(item_id): return {"id": item_id, "name": f"Item_{item_id}"}

def get_item(item_id):
    key = f"item:{item_id}"
    if key in _cache:
        v, exp = _cache[key]
        if time.time() < exp: return v
    item = db_fetch(item_id)
    _cache[key] = (item, time.time() + 60)
    return item
```
**Why:** Cache-aside is the default pattern — the application explicitly controls what gets cached and when.
</details>

---

### Q13 · Cache Decorator — @cached(ttl, key_fn) 🟡

Write a reusable `@cached(ttl, key_fn=None)` decorator. Test on a simulated DB call.

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)

<details><summary>💡 Hint</summary>Closure dict for storage. key_fn(*args) or str(args) as default key.</details>

<details><summary>✅ Answer</summary>

```python
import time
from functools import wraps

def cached(ttl: float, key_fn=None):
    def decorator(func):
        _store = {}
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = key_fn(*args) if key_fn else str(args)
            if key in _store:
                v, exp = _store[key]
                if time.time() < exp: return v
            result = func(*args, **kwargs)
            _store[key] = (result, time.time() + ttl)
            return result
        return wrapper
    return decorator
```
**Why:** A generic cache decorator avoids repeating cache-aside logic in every function.
</details>

---

### Q14 · Write-Through Cache — Implement write-through update 🟡

Write `update_user(user_id, data)` that writes to both a dict DB and a dict cache simultaneously. Then `get_user(user_id)` serves from cache first.

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)

<details><summary>💡 Hint</summary>Write to _db first, then _cache. Read from _cache; on miss, _db → _cache → return.</details>

<details><summary>✅ Answer</summary>

```python
import time
_db, _cache = {}, {}

def update_user(user_id: int, data: dict):
    _db[user_id] = data
    _cache[user_id] = (data, time.time() + 300)   # write-through

def get_user(user_id: int):
    if user_id in _cache:
        v, exp = _cache[user_id]
        if time.time() < exp: return v
    if user_id in _db:
        _cache[user_id] = (_db[user_id], time.time() + 300)
        return _db[user_id]
    return None
```
**Why:** Write-through ensures cache is always fresh after writes — no stale read window.
</details>

---

### Q15 · Cache Invalidation — Event-driven + TTL combined 🟡

Write `UserStore` with `write(user_id, data)`, `invalidate(user_id)`, and `read(user_id)`. On invalidate, remove from cache. On read, check TTL first.

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)

<details><summary>💡 Hint</summary>invalidate = del _cache[key]. read = TTL check → fall back to DB.</details>

<details><summary>✅ Answer</summary>

```python
import time

class UserStore:
    def __init__(self, ttl=60):
        self._db, self._cache, self._ttl = {}, {}, ttl

    def write(self, uid, data):
        self._db[uid] = data
        self._cache[uid] = (data, time.time() + self._ttl)

    def invalidate(self, uid):
        self._cache.pop(uid, None)

    def read(self, uid):
        if uid in self._cache:
            v, exp = self._cache[uid]
            if time.time() < exp: return v
            del self._cache[uid]
        if uid in self._db:
            self._cache[uid] = (self._db[uid], time.time() + self._ttl)
            return self._db[uid]
        return None
```
**Why:** Combining event-driven invalidation (accuracy) with TTL (safety net) is the production approach.
</details>

---

## Rate Limiting & Circuit Breaker — Q16–Q20

---

### Q16 · Token Bucket — Implement token bucket 🟡

Write `TokenBucket(capacity, refill_rate)` with `consume() -> bool`. Burst of 5 passes; 6th fails; 2 tokens refill after 1 second.

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)

<details><summary>💡 Hint</summary>tokens = min(capacity, tokens + elapsed * rate); if tokens >= 1: tokens -= 1; return True</details>

<details><summary>✅ Answer</summary>

```python
import time

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity, self.refill_rate = capacity, refill_rate
        self._tokens, self._last = float(capacity), time.time()

    def consume(self) -> bool:
        now = time.time()
        self._tokens = min(self.capacity, self._tokens + (now - self._last) * self.refill_rate)
        self._last = now
        if self._tokens >= 1:
            self._tokens -= 1
            return True
        return False
```
**Why:** Token bucket is the standard algorithm for APIs — allows short bursts while enforcing a long-run rate.
</details>

---

### Q17 · Sliding Window — Implement sliding window limiter 🟡

Write `SlidingWindow(max_requests, window_secs)` with `is_allowed() -> bool`.

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)

<details><summary>💡 Hint</summary>Deque of timestamps. Remove entries older than window on each call.</details>

<details><summary>✅ Answer</summary>

```python
import time, collections

class SlidingWindow:
    def __init__(self, max_requests, window_secs):
        self.max_requests, self.window_secs = max_requests, window_secs
        self._log = collections.deque()

    def is_allowed(self) -> bool:
        now = time.time()
        while self._log and self._log[0] <= now - self.window_secs:
            self._log.popleft()
        if len(self._log) < self.max_requests:
            self._log.append(now)
            return True
        return False
```
**Why:** Sliding window is more accurate than fixed window — no boundary burst problem.
</details>

---

### Q18 · Circuit Breaker — 3-state circuit breaker 🟡

Write `CircuitBreaker(failure_threshold, recovery_timeout)` with `call(func)`. Verify CLOSED → OPEN → HALF_OPEN → CLOSED transitions.

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)

<details><summary>💡 Hint</summary>OPEN: check recovery_timeout elapsed → HALF_OPEN. Success in HALF_OPEN → CLOSED.</details>

<details><summary>✅ Answer</summary>

```python
import time
from enum import Enum

class State(Enum):
    CLOSED = "closed"; OPEN = "open"; HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.state = State.CLOSED
        self.failures = 0
        self.threshold = failure_threshold
        self.timeout = recovery_timeout
        self._last = None

    def call(self, func, *args, **kwargs):
        if self.state == State.OPEN:
            if time.time() - self._last > self.timeout:
                self.state = State.HALF_OPEN
            else:
                raise Exception("Circuit OPEN")
        try:
            r = func(*args, **kwargs)
            self.failures = 0; self.state = State.CLOSED; return r
        except Exception:
            self.failures += 1; self._last = time.time()
            if self.failures >= self.threshold: self.state = State.OPEN
            raise
```
**Why:** Circuit breaker stops cascading failures. Without it, one slow service can exhaust all threads across the system.
</details>

---

### Q19 · Rate Limiter Decorator — @rate_limit decorator 🟡

Write `@rate_limit(max_calls, period)` that raises `RuntimeError` if limit exceeded. Use sliding window internally.

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)

<details><summary>💡 Hint</summary>Use a closure deque. Raise RuntimeError with retry_after seconds in message.</details>

<details><summary>✅ Answer</summary>

```python
import time, collections
from functools import wraps

def rate_limit(max_calls: int, period: float):
    log = collections.deque()
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            while log and log[0] <= now - period: log.popleft()
            if len(log) >= max_calls:
                raise RuntimeError(f"Rate limit: {max_calls}/{period}s exceeded")
            log.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_calls=3, period=1.0)
def api_call(n): return f"result_{n}"
```
**Why:** A decorator-based rate limiter is the cleanest way to add limits to existing functions without changing their code.
</details>

---

### Q20 · Retry Backoff — Exponential backoff with jitter 🟡

Write `@retry(max_attempts, base_delay, exceptions)`. Delay doubles each attempt. Add 10% jitter.

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)

<details><summary>💡 Hint</summary>delay = base_delay * 2**attempt; jitter = random.uniform(0, delay * 0.1)</details>

<details><summary>✅ Answer</summary>

```python
import time, random
from functools import wraps

def retry(max_attempts=3, base_delay=1.0, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1: raise
                    d = base_delay * (2 ** attempt)
                    time.sleep(d + random.uniform(0, d * 0.1))
        return wrapper
    return decorator
```
**Why:** Jitter prevents the thundering herd — all failed clients retrying at the exact same time.
</details>

---

## Connection Pooling & Task Queues — Q21–Q23

---

### Q21 · Connection Pool — queue.Queue-based pool 🟡

Write `ConnectionPool(max_size)` with `acquire()` and `release(conn)`. Use `queue.Queue` internally.

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)

<details><summary>💡 Hint</summary>queue.Queue(maxsize=N); get() to acquire; put() to release</details>

<details><summary>✅ Answer</summary>

```python
import queue

class ConnectionPool:
    def __init__(self, max_size: int):
        self._pool = queue.Queue(maxsize=max_size)
        for i in range(max_size):
            self._pool.put(f"conn_{i}")

    def acquire(self, timeout=5.0):
        return self._pool.get(timeout=timeout)

    def release(self, conn):
        self._pool.put(conn)
```
**Why:** Connection pools eliminate per-request connection overhead — critical for database-heavy applications.
</details>

---

### Q22 · SQLAlchemy Pool Config — Configure connection pool 🟡

Write the SQLAlchemy `create_engine()` call for a PostgreSQL database with pool_size=10, max_overflow=20, pool_timeout=30, pool_recycle=1800. Explain each parameter.

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)

<details><summary>💡 Hint</summary>All four params go into create_engine(). pool_recycle prevents stale connections.</details>

<details><summary>✅ Answer</summary>

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@host/db",
    pool_size=10,       # permanent connections always open
    max_overflow=20,    # extra connections allowed under load (total max = 30)
    pool_timeout=30,    # seconds to wait before raising error (pool full)
    pool_recycle=1800,  # recycle connections every 30min (avoid stale TCP)
)
```
**Why:** pool_recycle is critical for long-running servers — databases close idle connections after a timeout, causing errors without recycling.
</details>

---

### Q23 · Celery Task — Background task with Celery 🟡

Write a Celery task `send_email(to, subject)` and show how to call it asynchronously from a FastAPI endpoint. Broker = Redis.

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)

<details><summary>💡 Hint</summary>from celery import Celery; @app.task; task.delay() for async call</details>

<details><summary>✅ Answer</summary>

```python
from celery import Celery
celery_app = Celery("tasks", broker="redis://localhost:6379/0")

@celery_app.task
def send_email(to: str, subject: str):
    # runs in a background worker process
    print(f"Sending email to {to}: {subject}")

# In FastAPI route:
from fastapi import FastAPI
api = FastAPI()

@api.post("/register")
def register(email: str):
    send_email.delay(email, "Welcome!")   # ← non-blocking
    return {"status": "registered"}      # ← returns immediately
```
**Why:** Task queues decouple slow work from API response time. The user doesn't wait for the email to send.
</details>

---

## Capstone — Q24–Q25

---

### Q24 · URL Shortener Design — Design a scalable URL shortener 🟠

Design the complete system for a URL shortener (like bit.ly). Include:
- API endpoints
- Data model
- Caching strategy
- Scaling approach for 1M req/day

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)

<details><summary>💡 Hint</summary>Think: encode short code → store mapping → cache hot URLs → load balance → shard if needed</details>

<details><summary>✅ Answer</summary>

```python
"""
URL Shortener System Design

Endpoints:
  POST /shorten   body: {url: "https://..."} → {short_code: "abc123"}
  GET  /{code}    → 301 redirect to original URL

Data model:
  Table: urls (id, short_code, original_url, created_at, hit_count)
  Index on: short_code (lookup), created_at (cleanup)

Short code generation:
  Take MD5 hash of URL → take first 6 chars (base62 encoded)
  Collision: check DB, increment suffix

Caching strategy (cache-aside):
  Key: short:{code}   Value: original_url   TTL: 24h
  Hot URLs: >80% reads from cache after warm-up
  On redirect: check Redis first → miss → DB → populate cache

Scaling for 1M req/day (~12 req/sec):
  - 2 app servers behind load balancer (stateless)
  - PostgreSQL with read replica (reads >> writes)
  - Redis cache (avoids DB on 90%+ of reads)
  - CDN for redirect responses (cache 301s at edge)
  - Rate limit POST /shorten (prevent abuse)
"""
```
**Why:** URL shortener is a classic system design question — it touches all major components: API, DB, cache, scaling.
</details>

---

### Q25 · End-to-End System — Design a rate-limited cached Python service 🟠

Design and implement a Python service class `WeatherService` that:
1. Fetches weather data from a (mock) external API
2. Caches results with 5-minute TTL
3. Rate-limits calls to 60/minute using token bucket
4. Retries on failure with exponential backoff (3 attempts)
5. Opens circuit after 3 consecutive failures

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)

<details><summary>💡 Hint</summary>Compose TTLCache + TokenBucket + CircuitBreaker + retry logic in fetch_weather(city)</details>

<details><summary>✅ Answer</summary>

```python
import time, random
from collections import OrderedDict

class WeatherService:
    def __init__(self):
        self._cache       = {}          # TTL cache
        self._tokens      = 60.0        # token bucket
        self._token_last  = time.time()
        self._failures    = 0
        self._cb_open     = False
        self._cb_open_at  = None

    def _refill(self):
        now = time.time()
        self._tokens = min(60.0, self._tokens + (now - self._token_last) * 1.0)
        self._token_last = now

    def _rate_ok(self) -> bool:
        self._refill()
        if self._tokens >= 1:
            self._tokens -= 1; return True
        return False

    def _cb_check(self):
        if self._cb_open:
            if time.time() - self._cb_open_at > 30:
                self._cb_open = False   # HALF_OPEN: try once
            else:
                raise RuntimeError("Circuit OPEN")

    def _mock_api(self, city: str) -> dict:
        if random.random() < 0.2: raise ConnectionError("API timeout")
        return {"city": city, "temp": 72, "condition": "sunny"}

    def get_weather(self, city: str) -> dict:
        key = f"weather:{city}"
        if key in self._cache:
            v, exp = self._cache[key]
            if time.time() < exp: return {"source": "cache", **v}

        if not self._rate_ok():
            raise RuntimeError("Rate limit exceeded")

        self._cb_check()

        for attempt in range(3):
            try:
                result = self._mock_api(city)
                self._failures = 0; self._cb_open = False
                self._cache[key] = (result, time.time() + 300)
                return {"source": "api", **result}
            except ConnectionError:
                if attempt == 2:
                    self._failures += 1
                    if self._failures >= 3:
                        self._cb_open = True; self._cb_open_at = time.time()
                    raise
                time.sleep(0.1 * (2 ** attempt))
```
**Why:** This capstone combines every resilience pattern into one service — the real shape of a production external API client.
</details>

---

## 🧭 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 💻 Practice Local | [practice_local.py](./practice_local.py) |
| 🔌 API Design Deep Dive | [01_api_design_patterns/practice.md](./01_api_design_patterns/practice.md) |
| ⚡ Scalability Deep Dive | [02_scalability_caching_patterns/practice.md](./02_scalability_caching_patterns/practice.md) |
| 🎯 Interview | [interview.md](./interview.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) | **Next:** [API Design Deep Dive →](./01_api_design_patterns/theory.md)

**Related Topics:** [Theory](./theory.md) · [Cheetsheet](./cheetsheet.md) · [Interview Q&A](./interview.md)
