# ⚡ System Design with Python — Cheetsheet

> Quick reference: caching patterns, rate limiters, circuit breaker, Redis commands, connection pooling, retry backoff.

---

## 🗂️ Caching Patterns

| Pattern | Read Flow | Write Flow | Best For |
|---|---|---|---|
| **Cache-Aside** | check cache → miss → read DB → populate cache | write DB directly, invalidate or expire cache | Read-heavy, tolerate stale |
| **Write-Through** | check cache → miss → read DB | write cache + DB simultaneously | Read-heavy, always-fresh |
| **Write-Behind** | check cache → miss → read DB | write cache → async write DB later | Write-heavy, eventual consistency ok |

### Cache-Aside (Lazy Loading)

```python
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def get_user(user_id: int) -> dict:
    key = f"user:{user_id}"
    cached = r.get(key)
    if cached:
        return json.loads(cached)         # cache HIT

    user = db.query("SELECT * FROM users WHERE id=%s", user_id)
    r.setex(key, 3600, json.dumps(user))  # populate with TTL
    return user                           # cache MISS
```

### Write-Through

```python
def update_user(user_id: int, data: dict):
    db.execute("UPDATE users SET ... WHERE id=%s", user_id)   # DB first
    key = f"user:{user_id}"
    r.setex(key, 3600, json.dumps(data))   # then cache — always consistent
```

---

## ⏱️ Rate Limiter Implementations

### Token Bucket (smooths bursts)

```python
import time
import redis

def token_bucket(user_id: str, rate: float = 10, capacity: int = 20) -> bool:
    """rate = tokens/sec, capacity = max burst size"""
    r = redis.Redis()
    key = f"bucket:{user_id}"
    now = time.time()

    pipe = r.pipeline()
    pipe.hgetall(key)
    tokens_data, = pipe.execute()

    tokens = float(tokens_data.get(b"tokens", capacity))
    last   = float(tokens_data.get(b"last",   now))

    # refill based on elapsed time
    elapsed = now - last
    tokens = min(capacity, tokens + elapsed * rate)

    if tokens >= 1:
        tokens -= 1
        r.hset(key, mapping={"tokens": tokens, "last": now})
        r.expire(key, 3600)
        return True     # allowed
    return False        # rejected
```

### Sliding Window Counter

```python
def sliding_window(user_id: str, limit: int = 100, window: int = 60) -> bool:
    """limit requests per window seconds"""
    r = redis.Redis()
    now = time.time()
    key = f"ratelimit:{user_id}"

    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, now - window)   # remove old entries
    pipe.zadd(key, {str(now): now})               # add current request
    pipe.zcard(key)                               # count in window
    pipe.expire(key, window)
    _, _, count, _ = pipe.execute()

    return count <= limit
```

---

## 🔌 Circuit Breaker States

```
         ┌─────────────────────────────────────────┐
         │                                         │
    ┌────▼─────┐  failures >= threshold    ┌───────┴──────┐
    │  CLOSED  │ ─────────────────────────► │     OPEN     │
    │ (normal) │                            │ (rejecting)  │
    └──────────┘                            └──────┬───────┘
         ▲                                         │
         │  all test requests succeed              │ timeout elapsed
         │                                         ▼
         │                               ┌─────────────────┐
         └──────────────────────────────── │  HALF-OPEN      │
                                           │ (test 1 request)│
                                           └─────────────────┘
```

```python
import time
from enum import Enum

class State(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.state = State.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        if self.state == State.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = State.HALF_OPEN
            else:
                raise Exception("Circuit OPEN — fast fail")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = State.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = State.OPEN
```

---

## 🔴 Redis Patterns

### Core Commands

```python
import redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# String — cache a value with TTL
r.set("key", "value")
r.setex("key", 3600, "value")   # expires in 3600s
r.get("key")                    # "value" or None
r.delete("key")

# Counter — atomic increment (rate limiting, view counts)
r.incr("page_views")            # 1, 2, 3 ...
r.incrby("page_views", 10)

# List — queue / recent items
r.lpush("events", "e1", "e2")  # push left
r.rpop("events")               # pop right (FIFO queue)
r.lrange("events", 0, -1)      # get all

# Sorted Set — leaderboard / sliding window
r.zadd("scores", {"alice": 100, "bob": 95})
r.zrevrange("scores", 0, 9, withscores=True)   # top 10

# Hash — object fields
r.hset("user:42", mapping={"name": "Alice", "age": "30"})
r.hgetall("user:42")
r.hget("user:42", "name")

# Expire / TTL
r.expire("key", 300)            # 5 min TTL
r.ttl("key")                    # seconds remaining
```

### Pipeline (batch commands — reduces round trips)

```python
pipe = r.pipeline()
pipe.set("a", 1)
pipe.set("b", 2)
pipe.incr("a")
results = pipe.execute()    # [True, True, 2] — single round trip
```

---

## 🔗 Connection Pooling

```python
# SQLAlchemy — always use connection pool in production
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@host/db",
    pool_size=10,           # permanent connections
    max_overflow=20,        # extra connections under load
    pool_timeout=30,        # wait before error
    pool_recycle=1800,      # recycle connections every 30min
)

# Redis — pool is built-in
pool = redis.ConnectionPool(host="localhost", port=6379, max_connections=50)
r = redis.Redis(connection_pool=pool)

# asyncpg — async connection pool
import asyncpg

pool = await asyncpg.create_pool(
    dsn="postgresql://user:pass@host/db",
    min_size=5,
    max_size=20,
)
async with pool.acquire() as conn:
    result = await conn.fetch("SELECT * FROM users")
```

---

## 🔄 Retry with Exponential Backoff

```python
import time
import random
from functools import wraps

def retry(max_attempts=3, base_delay=1.0, max_delay=60.0, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    jitter = random.uniform(0, delay * 0.1)   # avoid thundering herd
                    time.sleep(delay + jitter)
        return wrapper
    return decorator

@retry(max_attempts=5, base_delay=0.5, exceptions=(ConnectionError, TimeoutError))
def call_external_api(url):
    ...
```

```
Attempt 1 → fail → wait 0.5s
Attempt 2 → fail → wait 1.0s
Attempt 3 → fail → wait 2.0s
Attempt 4 → fail → wait 4.0s
Attempt 5 → fail → raise
```

---

## 📌 Learning Priority

**Must Learn** — daily use, interview essential:
REST principles · HTTP status codes · Rate limiting · Caching (cache-aside) · Pagination · Retry with backoff

**Should Learn** — real projects:
Circuit breaker · Redis patterns · Connection pooling · Idempotency keys · API versioning · Graceful shutdown

**Good to Know** — specific situations:
GraphQL basics · Distributed tracing · Bulkhead pattern · gRPC vs REST

**Reference** — know it exists:
HATEOAS · CQRS · Consensus algorithms · Multi-region strategies

---

## 🔥 Rapid-Fire

```
Q: Cache-aside vs write-through difference?
A: Cache-aside: app manages cache explicitly. Write-through: writes go to cache + DB together.

Q: Token bucket vs sliding window?
A: Token bucket: allows short bursts up to capacity. Sliding window: strict count in rolling window.

Q: When does circuit breaker trip?
A: When failure count >= threshold. Moves to OPEN, rejects calls. After timeout: HALF_OPEN to test.

Q: Why pipeline in Redis?
A: Sends multiple commands in one network round trip — major latency reduction.

Q: Why jitter in backoff?
A: Prevents thundering herd — all retrying clients hitting server at exactly the same time.

Q: pool_recycle in SQLAlchemy?
A: Recycles connections older than N seconds to avoid using stale DB connections.
```

---

## 🧭 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🔌 API Design | [api_design_principles.md](./api_design_principles.md) |
| 📐 Scalable Design | [scalable_app_design.md](./scalable_app_design.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| ⬅️ Previous | [19 — Production Best Practices](../19_production_best_practices/packaging.md) |
| ➡️ Next | [21 — Data Engineering Applications](../21_data_engineering_applications/cheetsheet.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Production Best Practices](../19_production_best_practices/packaging.md) &nbsp;|&nbsp; **Next:** [Data Engineering →](../21_data_engineering_applications/cheetsheet.md)

**Related Topics:** [Theory](./theory.md) · [API Design Principles](./api_design_principles.md) · [Interview Q&A](./interview.md)
