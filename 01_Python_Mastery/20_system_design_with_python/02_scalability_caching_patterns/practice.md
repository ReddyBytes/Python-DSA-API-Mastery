# Scalability & Caching Patterns — Practice

> 12 questions covering LRU cache, TTL cache, token bucket, sliding window, circuit breaker, connection pooling, retry backoff, and capstone.

---

### Q1 · Simple TTL Cache — Implement simple dict-based cache with TTL 🟢

Write a `SimpleCache` class with `get(key)` and `set(key, value, ttl)` methods. `get` should return `None` if the key has expired or doesn't exist.

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

<details><summary>💡 Hint</summary>Store (value, expiry_timestamp). In get, check time.time() < expiry.</details>

<details><summary>✅ Answer</summary>

```python
import time

class SimpleCache:
    def __init__(self):
        self._store = {}   # key → (value, expiry)

    def set(self, key: str, value, ttl: float):
        self._store[key] = (value, time.time() + ttl)

    def get(self, key: str):
        if key not in self._store:
            return None
        value, expiry = self._store[key]
        if time.time() > expiry:
            del self._store[key]
            return None       # ← expired
        return value

cache = SimpleCache()
cache.set("user:1", {"name": "Alice"}, ttl=2)
print(cache.get("user:1"))   # {'name': 'Alice'}
```
**Why:** TTL caches are the foundation of every production caching layer — simple but powerful.
</details>

---

### Q2 · @lru_cache — Apply @lru_cache to expensive function 🟢

Write a function `fib(n)` that computes Fibonacci numbers using `@lru_cache`. Print cache info after calling `fib(30)` twice. Then clear the cache and print info again.

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

<details><summary>💡 Hint</summary>from functools import lru_cache; @lru_cache(maxsize=None) for unlimited cache</details>

<details><summary>✅ Answer</summary>

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

fib(30)
fib(30)   # cache hit
print(fib.cache_info())   # CacheInfo(hits=1, misses=31, ...)

fib.cache_clear()
print(fib.cache_info())   # CacheInfo(hits=0, misses=0, currsize=0)
```
**Why:** @lru_cache turns an O(2^n) recursive function into O(n) with one decorator.
</details>

---

### Q3 · LRU Cache Implementation — Implement LRU cache using OrderedDict 🟡

Implement a `LRUCache` class with `get(key)` and `put(key, value)` methods. When capacity is exceeded, evict the least recently used item. Both methods must be O(1).

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

<details><summary>💡 Hint</summary>OrderedDict.move_to_end(key) marks as MRU; popitem(last=False) evicts LRU</details>

<details><summary>✅ Answer</summary>

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self._cache   = OrderedDict()

    def get(self, key):
        if key not in self._cache:
            return None
        self._cache.move_to_end(key)   # ← mark most recently used
        return self._cache[key]

    def put(self, key, value):
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self.capacity:
            self._cache.popitem(last=False)   # ← evict LRU

lru = LRUCache(3)
lru.put("a", 1); lru.put("b", 2); lru.put("c", 3)
lru.get("a")        # a is now MRU
lru.put("d", 4)     # b is evicted (LRU)
print(lru.get("b")) # None — evicted
```
**Why:** This is a classic interview question. OrderedDict + move_to_end = O(1) LRU.
</details>

---

### Q4 · Token Bucket — Implement token bucket rate limiter 🟡

Implement a `TokenBucket` class with `consume() -> bool`. Capacity = 5, refill_rate = 2 tokens/second. Show that 5 requests pass, the 6th fails, and after 1 second 2 more pass.

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

<details><summary>💡 Hint</summary>On each consume(), calculate elapsed time and add tokens. Never exceed capacity.</details>

<details><summary>✅ Answer</summary>

```python
import time

class TokenBucket:
    def __init__(self, capacity: float, refill_rate: float):
        self.capacity    = capacity
        self.refill_rate = refill_rate
        self._tokens     = float(capacity)
        self._last       = time.time()

    def consume(self) -> bool:
        now = time.time()
        self._tokens = min(
            self.capacity,
            self._tokens + (now - self._last) * self.refill_rate
        )
        self._last = now
        if self._tokens >= 1:
            self._tokens -= 1
            return True
        return False

bucket = TokenBucket(capacity=5, refill_rate=2)
for i in range(7):
    print(f"req {i+1}: {'ALLOW' if bucket.consume() else 'DENY'}")
time.sleep(1.0)
for i in range(2):
    print(f"after refill: {'ALLOW' if bucket.consume() else 'DENY'}")
```
**Why:** Token bucket is used by AWS API Gateway, Stripe, and GitHub — allows short bursts within a long-run rate.
</details>

---

### Q5 · Sliding Window Rate Limiter — Implement sliding window rate limiter 🟡

Implement a `SlidingWindowLimiter(max_requests, window_secs)` with `is_allowed() -> bool`. Show 3 requests pass in a 1-second window, then the 4th fails, then after 1 second more pass.

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

<details><summary>💡 Hint</summary>Use collections.deque. Remove timestamps older than window on each call.</details>

<details><summary>✅ Answer</summary>

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
            self._log.popleft()            # ← slide window forward
        if len(self._log) < self.max_requests:
            self._log.append(now)
            return True
        return False

limiter = SlidingWindowLimiter(max_requests=3, window_secs=1.0)
for i in range(5):
    print(f"req {i+1}: {'ALLOW' if limiter.is_allowed() else 'DENY'}")
```
**Why:** Sliding window has no boundary burst problem — it's accurate to the millisecond.
</details>

---

### Q6 · Circuit Breaker — Write circuit breaker class (3 states) 🟡

Implement `CircuitBreaker(failure_threshold, recovery_timeout)` with a `call(func, *args)` method. Test it: make it trip after 3 failures, verify fast-fail, wait for recovery timeout, verify HALF_OPEN allows one test call.

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

<details><summary>💡 Hint</summary>States: CLOSED (normal) → OPEN (fast fail) → HALF_OPEN (test one). Success in HALF_OPEN → CLOSED.</details>

<details><summary>✅ Answer</summary>

```python
import time
from enum import Enum

class State(Enum):
    CLOSED    = "closed"
    OPEN      = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=5):
        self.state             = State.CLOSED
        self.failure_count     = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout  = recovery_timeout
        self._last_failure     = None

    def call(self, func, *args, **kwargs):
        if self.state == State.OPEN:
            if time.time() - self._last_failure > self.recovery_timeout:
                self.state = State.HALF_OPEN
            else:
                raise Exception("Circuit OPEN")
        try:
            result = func(*args, **kwargs)
            self.failure_count = 0
            self.state = State.CLOSED
            return result
        except Exception:
            self.failure_count += 1
            self._last_failure = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = State.OPEN
            raise
```
**Why:** Circuit breaker prevents cascading failures — when downstream is down, fast-fail immediately instead of queuing thousands of slow timeouts.
</details>

---

### Q7 · Connection Pooling — Implement connection pool using queue.Queue 🟡

Implement a `ConnectionPool(max_size)` class using `queue.Queue`. Provide `acquire()` and `release(conn)` methods. Simulate 5 workers acquiring and releasing connections.

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

<details><summary>💡 Hint</summary>queue.Queue(maxsize=N) — put() to release, get(timeout=...) to acquire</details>

<details><summary>✅ Answer</summary>

```python
import queue
import threading

class FakeConnection:
    def __init__(self, cid): self.id = cid
    def __repr__(self): return f"Conn({self.id})"

class ConnectionPool:
    def __init__(self, max_size: int):
        self._pool = queue.Queue(maxsize=max_size)
        for i in range(max_size):
            self._pool.put(FakeConnection(i))   # ← fill pool

    def acquire(self, timeout: float = 5.0) -> FakeConnection:
        return self._pool.get(timeout=timeout)  # ← blocks until available

    def release(self, conn: FakeConnection):
        self._pool.put(conn)                    # ← return to pool

pool = ConnectionPool(max_size=3)

def worker(name):
    conn = pool.acquire()
    print(f"{name} got {conn}")
    import time; time.sleep(0.1)
    pool.release(conn)
    print(f"{name} released {conn}")

threads = [threading.Thread(target=worker, args=(f"W{i}",)) for i in range(5)]
for t in threads: t.start()
for t in threads: t.join()
```
**Why:** Connection pools eliminate the cost of opening a new DB connection on every request.
</details>

---

### Q8 · Cache-Aside Pattern — Cache-aside pattern with Redis mock 🟡

Write a `get_product(product_id)` function using cache-aside pattern. Use a `MockRedis` dict as the cache store. Cache hit should avoid calling `fetch_from_db()`. TTL = 60 seconds (store expiry timestamp alongside value).

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

<details><summary>💡 Hint</summary>Cache stores (value, expiry). On miss, fetch DB, store in cache with expiry = now + 60.</details>

<details><summary>✅ Answer</summary>

```python
import time

_cache = {}   # mock Redis

def fetch_from_db(product_id: int) -> dict:
    print(f"  [DB] fetching product {product_id}")
    return {"id": product_id, "name": f"Product_{product_id}", "price": 9.99}

def get_product(product_id: int) -> dict:
    key = f"product:{product_id}"
    if key in _cache:
        value, expiry = _cache[key]
        if time.time() < expiry:
            print(f"  [cache HIT] {key}")
            return value
        del _cache[key]

    product = fetch_from_db(product_id)
    _cache[key] = (product, time.time() + 60)
    return product

get_product(1)   # DB call
get_product(1)   # cache hit
get_product(2)   # DB call
```
**Why:** Cache-aside is the default caching pattern — simple, explicit, and widely understood.
</details>

---

### Q9 · Cache Decorator — Write cache decorator with TTL + key function 🟠

Write a `@cached(ttl, key_fn=None)` decorator that caches function return values with a TTL. The optional `key_fn` maps args to a cache key string. Default key = str(args).

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

<details><summary>💡 Hint</summary>Use a closure dict for storage. key_fn(*args, **kwargs) → string. Store (result, expiry).</details>

<details><summary>✅ Answer</summary>

```python
import time
from functools import wraps

def cached(ttl: float, key_fn=None):
    def decorator(func):
        _store = {}
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = key_fn(*args, **kwargs) if key_fn else str(args)
            if key in _store:
                value, expiry = _store[key]
                if time.time() < expiry:
                    return value
            result = func(*args, **kwargs)
            _store[key] = (result, time.time() + ttl)
            return result
        wrapper.cache_clear = lambda: _store.clear()
        return wrapper
    return decorator

@cached(ttl=5, key_fn=lambda user_id: f"user:{user_id}")
def get_user(user_id: int) -> dict:
    print(f"  [DB fetch] user {user_id}")
    return {"id": user_id, "name": f"User_{user_id}"}

get_user(1)   # DB fetch
get_user(1)   # cached
get_user(2)   # DB fetch
```
**Why:** A generic cache decorator is reusable across any function and avoids boilerplate.
</details>

---

### Q10 · Retry with Exponential Backoff — Implement retry with exponential backoff 🟠

Write a `@retry(max_attempts, base_delay, exceptions)` decorator. Delay doubles on each attempt (1s, 2s, 4s). Add random jitter of up to 10% to avoid thundering herd.

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

<details><summary>💡 Hint</summary>delay = base_delay * (2 ** attempt); jitter = random.uniform(0, delay * 0.1)</details>

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
                    if attempt == max_attempts - 1:
                        raise
                    delay  = base_delay * (2 ** attempt)
                    jitter = random.uniform(0, delay * 0.1)   # ← thundering herd prevention
                    print(f"  attempt {attempt+1} failed, retry in {delay:.2f}s")
                    time.sleep(delay + jitter)
        return wrapper
    return decorator

@retry(max_attempts=3, base_delay=0.1, exceptions=(ConnectionError,))
def call_flaky_service():
    import random
    if random.random() < 0.7:
        raise ConnectionError("timeout")
    return "success"
```
**Why:** Exponential backoff prevents retry storms. Jitter spreads load when many clients retry simultaneously.
</details>

---

### Q11 · Stateless Session — Design stateless session using JWT 🟠

Write `create_token(user_id)` and `decode_token(token)` functions using PyJWT. The token should include `user_id` and `exp` (expiry 1 hour). Decode should raise on expired/invalid tokens.

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

<details><summary>💡 Hint</summary>import jwt; jwt.encode(payload, SECRET, algorithm="HS256"); jwt.decode(..., algorithms=["HS256"])</details>

<details><summary>✅ Answer</summary>

```python
import jwt
import time

SECRET = "my-secret-key"

def create_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp":     int(time.time()) + 3600,   # ← 1 hour expiry
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")

def decode_token(token: str) -> dict:
    # Raises jwt.ExpiredSignatureError or jwt.InvalidTokenError
    return jwt.decode(token, SECRET, algorithms=["HS256"])

token = create_token(42)
print(decode_token(token))   # {'user_id': 42, 'exp': ...}
```
**Why:** JWT stores session data in the token itself — no server-side session store needed, enabling true stateless horizontal scaling.
</details>

---

### Q12 · Capstone — Build rate-limited cached API client 🟠

Build a `APIClient` class that:
1. Caches GET responses with 30-second TTL
2. Enforces a token bucket rate limit (10 req/sec)
3. Retries on failure (3 attempts, exponential backoff)
4. Returns cached response on rate limit hit (stale-while-revalidate)

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

<details><summary>💡 Hint</summary>Compose: SimpleCache + TokenBucket + retry logic in a single fetch() method</details>

<details><summary>✅ Answer</summary>

```python
import time, random

class APIClient:
    def __init__(self):
        self._cache   = {}           # key → (value, expiry)
        self._tokens  = 10.0
        self._last    = time.time()
        self._rate    = 10.0         # tokens/sec
        self._cap     = 10.0

    def _refill(self):
        now = time.time()
        self._tokens = min(self._cap, self._tokens + (now - self._last) * self._rate)
        self._last = now

    def _rate_limited(self) -> bool:
        self._refill()
        if self._tokens >= 1:
            self._tokens -= 1
            return False
        return True    # ← rate limited

    def _fetch_with_retry(self, url: str) -> dict:
        for attempt in range(3):
            try:
                # simulate HTTP call
                return {"url": url, "data": "..."}
            except Exception:
                if attempt == 2: raise
                time.sleep(0.1 * (2 ** attempt))

    def get(self, url: str) -> dict:
        if url in self._cache:
            value, expiry = self._cache[url]
            if time.time() < expiry:
                return {"source": "cache", "data": value}

        if self._rate_limited():
            if url in self._cache:   # stale-while-revalidate
                return {"source": "stale", "data": self._cache[url][0]}
            raise RuntimeError("Rate limited, no cached fallback")

        result = self._fetch_with_retry(url)
        self._cache[url] = (result, time.time() + 30)
        return {"source": "network", "data": result}
```
**Why:** Production API clients combine caching, rate limiting, and retry — this capstone shows how they compose.
</details>

---

## 🧭 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 💻 Practice Local | [practice_local.py](./practice_local.py) |
| ⬆️ Root Practice | [../practice.md](../practice.md) |
| 🔌 API Design Practice | [../01_api_design_patterns/practice.md](../01_api_design_patterns/practice.md) |

---

**[🏠 Back to README](../../README.md)**

**Prev:** [← API Design Practice](../01_api_design_patterns/practice.md) | **Next:** [Root Practice →](../practice.md)

**Related Topics:** [Scalability Theory](./theory.md) · [Root Theory](../theory.md) · [Interview Q&A](../interview.md)
