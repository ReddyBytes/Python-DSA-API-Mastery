# Scalability & Caching Patterns — Theory

> Think of a busy coffee shop. The barista remembers your usual order without asking (cache). Three registers share the customer load so no single one jams (horizontal scaling). A bouncer limits how many orders per minute so the kitchen doesn't drown (rate limiter). Good system design is just this, at software scale.

---

## 📌 Learning Priority

**Must Learn**: in-memory cache (dict/LRU), token bucket rate limiter, load balancing concept
**Should Learn**: Redis basics, circuit breaker pattern, connection pooling
**Good to Know**: consistent hashing, sharding concept
**Reference**: async task queues (Celery), read replicas, write-through cache

---

## 1. Caching Strategies

A **cache** is a fast temporary store. Instead of asking the database every time, you ask the cache first. Cache hit = fast; cache miss = slow (fall through to DB).

### Cache-aside (lazy loading)

The most common pattern. The application manages the cache itself.

```
Request → check cache
              │
          ┌───▼───┐
          │  HIT  │ → return cached value (fast, ~0.1ms)
          └───────┘
              │ MISS
          ┌───▼───┐
          │  DB   │ → fetch data (~50ms)
          └───────┘
              │
          populate cache, return value
```

```python
import json, redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def get_user(user_id: int) -> dict:
    key = f"user:{user_id}"
    cached = r.get(key)
    if cached:
        return json.loads(cached)          # ← cache HIT

    user = db.fetch_user(user_id)          # ← cache MISS
    r.setex(key, 3600, json.dumps(user))   # ← populate, 1h TTL
    return user
```

### Write-through

Every write goes to both the cache and the DB at the same time. Reads are always fresh.

```python
def update_user(user_id: int, data: dict):
    db.update("UPDATE users SET ... WHERE id=%s", user_id)  # DB first
    r.setex(f"user:{user_id}", 3600, json.dumps(data))      # then cache
```

### TTL (time-to-live)

Every cache entry has an expiry time. After TTL expires, the next request fetches fresh data.

```
set TTL = 300 seconds (5 minutes)
at t=0   → cache populated
at t=150 → cache hit (still fresh)
at t=301 → cache expired → fetch DB → repopulate
```

> 📝 **Practice:** [Q1 — Dict cache with TTL](./practice.md#q1--simple-ttl-cache---implement-simple-dict-based-cache-with-ttl-) · [Q8 — Cache-aside with Redis mock](./practice.md#q8--cache-aside-pattern---cache-aside-pattern-with-redis-mock-)

---

## 2. LRU Cache Implementation

**LRU** = Least Recently Used. When the cache is full, the item you used least recently gets evicted — like a whiteboard that erases the oldest note when it fills up.

### functools.lru_cache

Python's built-in. One decorator line — done.

```python
from functools import lru_cache

@lru_cache(maxsize=128)    # ← keeps 128 most-recently-used results
def fetch_config(env: str) -> dict:
    return expensive_db_lookup(env)   # only called once per unique env

fetch_config("prod")   # slow — DB call
fetch_config("prod")   # fast — cache hit
fetch_config.cache_info()   # CacheInfo(hits=1, misses=1, ...)
fetch_config.cache_clear()  # wipe the cache
```

Limitation: no TTL. Args must be hashable (no lists/dicts as arguments).

### LRU cache from scratch (OrderedDict)

Used in coding interviews and when you need more control.

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self._cache = OrderedDict()   # maintains insertion order

    def get(self, key):
        if key not in self._cache:
            return None
        self._cache.move_to_end(key)  # ← mark as most recently used
        return self._cache[key]

    def put(self, key, value):
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self.capacity:
            self._cache.popitem(last=False)  # ← evict least recently used
```

```
cache = LRUCache(3)
cache.put("a", 1)   # [a]
cache.put("b", 2)   # [a, b]
cache.put("c", 3)   # [a, b, c]
cache.get("a")      # [b, c, a]  ← a moves to front (MRU)
cache.put("d", 4)   # [c, a, d]  ← b evicted (LRU)
```

> 📝 **Practice:** [Q2 — @lru_cache](./practice.md#q2--lru_cache---apply-lru_cache-to-expensive-function-) · [Q3 — LRU from scratch](./practice.md#q3--lru-cache-implementation---implement-lru-cache-using-ordereddict-)

---

## 3. Rate Limiter Patterns

A rate limiter is a bouncer: it lets through N requests per time window, then blocks the rest.

### Token bucket

The most popular algorithm. Imagine a bucket that holds tokens. Each request takes 1 token. Tokens refill over time. If the bucket is empty, request is denied.

```
capacity = 5 tokens (max burst)
refill   = 2 tokens/second (long-run rate)

t=0:  bucket=5  → req1 ALLOW (bucket=4)
t=0:  bucket=4  → req2 ALLOW (bucket=3)
...
t=0:  bucket=1  → req5 ALLOW (bucket=0)
t=0:  bucket=0  → req6 DENY  (wait for refill)
t=1:  bucket=2  → req7 ALLOW (tokens refilled)
```

```python
import time

class TokenBucket:
    def __init__(self, capacity: float, refill_rate: float):
        self.capacity    = capacity
        self.refill_rate = refill_rate        # tokens per second
        self._tokens     = float(capacity)    # start full
        self._last       = time.time()

    def consume(self) -> bool:
        now = time.time()
        # Refill tokens based on elapsed time
        self._tokens = min(
            self.capacity,
            self._tokens + (now - self._last) * self.refill_rate
        )
        self._last = now
        if self._tokens >= 1:
            self._tokens -= 1
            return True    # ← allowed
        return False       # ← denied
```

### Sliding window

Instead of buckets, log every request timestamp. Count how many are within the last N seconds.

```python
import time, collections

class SlidingWindowLimiter:
    def __init__(self, max_requests: int, window_secs: float):
        self.max_requests = max_requests
        self.window_secs  = window_secs
        self._log         = collections.deque()

    def is_allowed(self) -> bool:
        now    = time.time()
        cutoff = now - self.window_secs
        while self._log and self._log[0] <= cutoff:
            self._log.popleft()           # ← slide window forward
        if len(self._log) < self.max_requests:
            self._log.append(now)
            return True
        return False
```

| | Token Bucket | Sliding Window |
|---|---|---|
| Allows short bursts | Yes (up to capacity) | No |
| Memory per client | O(1) | O(max_requests) |
| Used by | AWS, Stripe, GitHub | Strict SLA enforcement |

> 📝 **Practice:** [Q4 — Token bucket](./practice.md#q4--token-bucket---implement-token-bucket-rate-limiter-) · [Q5 — Sliding window](./practice.md#q5--sliding-window-rate-limiter---implement-sliding-window-rate-limiter-)

---

## 4. Connection Pooling

Every database query needs a connection. Opening a connection takes ~20-100ms. If you open a new connection for every request, you waste that time on every call.

**Connection pooling** keeps a pool of open connections ready to use. A request borrows one, uses it, returns it. Like reusable shopping baskets at a supermarket.

```
Request 1 → borrow conn → query → return conn
Request 2 → borrow conn → query → return conn  (reused from pool)
```

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@host/db",
    pool_size=10,        # ← permanent connections always open
    max_overflow=20,     # ← extra connections allowed under load
    pool_timeout=30,     # ← wait max 30s before raising error
    pool_recycle=1800,   # ← recycle connections every 30min
)

# Each request borrows a connection from the pool
with engine.connect() as conn:
    result = conn.execute("SELECT * FROM users WHERE id = 42")
```

Without pooling on a busy server: 1000 req/s × 50ms connection open = 50 seconds wasted per second.

> 📝 **Practice:** [Q7 — Connection pool](./practice.md#q7--connection-pooling---implement-connection-pool-using-queuequeue-)

---

## 5. Circuit Breaker Pattern

When a downstream service (database, third-party API) is failing, keep hammering it = make it worse. A **circuit breaker** detects failure and stops trying for a while — like an electrical circuit breaker that trips when there's too much current.

```
         ┌──────────────────────────────────────────────┐
         │                                              │
    ┌────▼─────┐  failures >= threshold    ┌────────────┴─────┐
    │  CLOSED  │ ──────────────────────►   │      OPEN        │
    │ (normal) │                           │  (fast fail all) │
    └──────────┘                           └──────────┬───────┘
         ▲                                            │
         │  test request succeeds                     │ timeout elapsed
         │                                            ▼
         │                                  ┌─────────────────┐
         └──────────────────────────────────│   HALF-OPEN     │
                                            │ (test 1 request)│
                                            └─────────────────┘
```

```python
import time
from enum import Enum

class State(Enum):
    CLOSED    = "closed"     # normal, calls pass through
    OPEN      = "open"       # failing, reject all calls
    HALF_OPEN = "half_open"  # testing if service recovered

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.state             = State.CLOSED
        self.failure_count     = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout  = recovery_timeout
        self._last_failure     = None

    def call(self, func, *args, **kwargs):
        if self.state == State.OPEN:
            elapsed = time.time() - self._last_failure
            if elapsed > self.recovery_timeout:
                self.state = State.HALF_OPEN   # ← try one request
            else:
                raise Exception("Circuit OPEN — fast fail")
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = State.CLOSED       # ← back to normal

    def _on_failure(self):
        self.failure_count += 1
        self._last_failure = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = State.OPEN     # ← trip the breaker
```

> 📝 **Practice:** [Q6 — Circuit breaker](./practice.md#q6--circuit-breaker---write-circuit-breaker-class-3-states-)

---

## 6. Horizontal Scaling Concepts

**Vertical scaling** = buying a bigger machine (faster CPU, more RAM). Has a ceiling.

**Horizontal scaling** = adding more machines. No ceiling.

```
Vertical:
  [Server 1: 4 CPU, 8GB RAM]
  [Server 1: 8 CPU, 32GB RAM]   ← upgrade, expensive, limit

Horizontal:
  [Server 1: 4 CPU] ─┐
  [Server 2: 4 CPU] ─┤─ Load Balancer → clients
  [Server 3: 4 CPU] ─┘
```

Key requirement: **stateless design**. If Server 1 handles your login but Server 2 handles your next request, Server 2 must also know you're logged in.

```python
# Bad — session stored in-process (breaks with multiple servers)
sessions = {}   # ← only on THIS server

# Good — session stored in Redis (shared across all servers)
import redis
r = redis.Redis()

def create_session(user_id: int) -> str:
    import secrets
    token = secrets.token_hex(16)
    r.setex(f"session:{token}", 3600, str(user_id))  # ← shared
    return token
```

> 📝 **Practice:** [Q11 — Stateless session with JWT](./practice.md#q11--stateless-session---design-stateless-session-using-jwt-)

---

## 7. Async Task Queues

Some work shouldn't happen in the API request itself. Sending an email, resizing an image, generating a PDF — these take seconds. The API response should be instant.

A **task queue** lets the API say "do this later" and return immediately.

```
Client → POST /send-email → API → push job → Queue → Worker processes → sends email
                          ↓
                     return 202 Accepted   (immediately)
```

```python
# Celery basics
from celery import Celery

app = Celery("tasks", broker="redis://localhost:6379/0")

@app.task
def send_welcome_email(user_email: str):
    # This runs in a background worker, not in the API
    email_service.send(to=user_email, subject="Welcome!")

# In your FastAPI handler:
@api.post("/register")
def register(user: UserIn):
    new_user = create_user(user)
    send_welcome_email.delay(user.email)   # ← non-blocking
    return {"status": "registered"}       # ← returns immediately
```

When to use a task queue:
- Sending emails/notifications
- Generating reports
- Processing uploads
- Calling slow third-party APIs
- Any work > 500ms

> 📝 **Practice:** [Q12 — Rate-limited cached API client](./practice.md#q12--capstone---build-rate-limited-cached-api-client-)

---

## 8. Common Mistakes

```
Mistake                              Fix
──────────────────────────────────────────────────────────────
Cache everything forever             Always set a TTL
No connection pool                   Use SQLAlchemy pool_size/max_overflow
Retry infinitely on failure          Use circuit breaker + max retries
Store session in-process             Use Redis for shared session
No rate limiter in production        Add token bucket at API gateway
Synchronous email sending in API     Use Celery or similar task queue
Retry without jitter                 Add random jitter to avoid thundering herd
LRU cache with unhashable args       @lru_cache args must be hashable
```

---

## 🧭 Navigation

| | |
|---|---|
| ⬆️ Root Theory | [../theory.md](../theory.md) |
| 💻 Practice | [practice.md](./practice.md) |
| 🔌 API Design | [../01_api_design_patterns/theory.md](../01_api_design_patterns/theory.md) |

---

**[🏠 Back to README](../../README.md)**

**Prev:** [← API Design Patterns](../01_api_design_patterns/theory.md) | **Next:** [Root Interview Q&A →](../interview.md)

**Related Topics:** [Root Theory](../theory.md) · [API Design Patterns](../01_api_design_patterns/theory.md) · [Interview Q&A](../interview.md)
