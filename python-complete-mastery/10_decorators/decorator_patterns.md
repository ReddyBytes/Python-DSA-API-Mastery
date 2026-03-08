# 🏭 decorator_patterns.md — Production Decorator Pattern Library

> A complete library of battle-tested decorators used in real production systems.
> Copy, adapt, and use directly.

---

## 📋 Pattern Index

```
1.  @timed             — measure and log execution time
2.  @logged            — log function calls with args and results
3.  @retry             — retry with exponential backoff + jitter
4.  @circuit_breaker   — stop hammering a failing dependency
5.  @ttl_cache         — cache with time-to-live expiry
6.  @rate_limit        — limit calls per time window
7.  @validate_types    — enforce type annotations at runtime
8.  @require_auth      — authentication guard
9.  @deprecated        — emit DeprecationWarning
10. @singleton         — class decorator: single instance
11. @once              — run function only once
12. @memoize           — infinite memoization (manual)
13. @timeout           — abort function if it takes too long
14. @suppress          — catch and ignore specified exceptions
15. @trace             — detailed call trace for debugging
```

---

## 1. `@timed` — Execution Timer

```python
import functools, time, logging

logger = logging.getLogger(__name__)

def timed(func):
    """Log execution time of any function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            logger.info("%s completed in %.3fs", func.__name__, elapsed)
            return result
        except Exception:
            elapsed = time.perf_counter() - start
            logger.error("%s failed after %.3fs", func.__name__, elapsed)
            raise
    return wrapper

# Usage:
@timed
def process_orders(orders):
    for order in orders:
        apply_discount(order)
```

---

## 2. `@logged` — Call Logger

```python
import functools, logging, inspect

logger = logging.getLogger(__name__)

def logged(level=logging.INFO, log_args=False, log_result=False):
    """Log function entry, exit, and optionally args/result."""
    def decorator(func):
        log = logger.log

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if log_args:
                sig = inspect.signature(func)
                bound = sig.bind(*args, **kwargs)
                bound.apply_defaults()
                log(level, "%s called with %s", func.__name__, dict(bound.arguments))
            else:
                log(level, "%s called", func.__name__)

            try:
                result = func(*args, **kwargs)
                if log_result:
                    log(level, "%s returned %r", func.__name__, result)
                return result
            except Exception as e:
                logger.exception("%s raised %s: %s", func.__name__, type(e).__name__, e)
                raise
        return wrapper
    return decorator

# Usage:
@logged(log_args=True)
def create_order(user_id, items):
    ...

@logged(level=logging.DEBUG, log_result=True)
def fetch_config(key):
    ...
```

---

## 3. `@retry` — Retry with Exponential Backoff

```python
import functools, time, logging, random

logger = logging.getLogger(__name__)

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    jitter: float = 0.1,
    exceptions: tuple = (Exception,),
):
    """
    Retry with exponential backoff and jitter.

    delay:    initial wait time in seconds
    backoff:  multiplier applied after each failure (2.0 = double each time)
    jitter:   random seconds added to prevent thundering herd
    exceptions: only retry on these exception types
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            "%s failed permanently after %d attempts: %s",
                            func.__name__, max_attempts, e
                        )
                        raise
                    actual_wait = wait + random.uniform(0, jitter)
                    logger.warning(
                        "%s attempt %d/%d failed: %s — retrying in %.2fs",
                        func.__name__, attempt, max_attempts, e, actual_wait
                    )
                    time.sleep(actual_wait)
                    wait *= backoff
        return wrapper
    return decorator

# Usage:
@retry(max_attempts=5, delay=0.5, backoff=2.0, exceptions=(ConnectionError, TimeoutError))
def fetch_from_api(endpoint: str) -> dict:
    return requests.get(endpoint).json()
```

---

## 4. `@circuit_breaker` — Stop Hammering a Failing Service

```python
import functools, time, threading

class CircuitBreaker:
    """
    Three states:
    CLOSED   → normal, requests flow through
    OPEN     → failing, requests immediately rejected
    HALF-OPEN → one test request allowed to check if service recovered
    """
    CLOSED    = "closed"
    OPEN      = "open"
    HALF_OPEN = "half_open"

    def __init__(self, failure_threshold=5, recovery_timeout=60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout  = recovery_timeout
        self.failure_count     = 0
        self.state             = self.CLOSED
        self.opened_at         = None
        self._lock             = threading.Lock()

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self._lock:
                if self.state == self.OPEN:
                    if time.time() - self.opened_at > self.recovery_timeout:
                        self.state = self.HALF_OPEN
                    else:
                        raise RuntimeError(
                            f"Circuit open for {func.__name__} — dependency is down"
                        )

            try:
                result = func(*args, **kwargs)
                with self._lock:
                    self.failure_count = 0
                    self.state = self.CLOSED
                return result
            except Exception:
                with self._lock:
                    self.failure_count += 1
                    if self.failure_count >= self.failure_threshold:
                        self.state     = self.OPEN
                        self.opened_at = time.time()
                raise
        return wrapper

# Usage:
payment_circuit = CircuitBreaker(failure_threshold=5, recovery_timeout=30.0)

@payment_circuit
def charge_card(amount, token):
    return payment_gateway.charge(amount, token)
```

---

## 5. `@ttl_cache` — Cache with Time-To-Live

```python
import functools, time

def ttl_cache(seconds: float = 60, maxsize: int = 128):
    """
    Cache function results for `seconds` before expiring.
    Unlike lru_cache, results auto-expire.
    """
    def decorator(func):
        cache: dict = {}
        cache_order: list = []

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Convert kwargs to hashable key
            key = args + tuple(sorted(kwargs.items()))
            now = time.monotonic()

            if key in cache:
                result, ts = cache[key]
                if now - ts < seconds:
                    return result

            result = func(*args, **kwargs)
            cache[key] = (result, now)

            # Evict oldest if over maxsize
            if len(cache) > maxsize:
                oldest = min(cache, key=lambda k: cache[k][1])
                del cache[oldest]

            return result

        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_info  = lambda: {"size": len(cache), "ttl": seconds}
        return wrapper
    return decorator

# Usage:
@ttl_cache(seconds=300)   # cache for 5 minutes
def get_feature_flags():
    return config_service.fetch_all_flags()
```

---

## 6. `@rate_limit` — Calls Per Time Window

```python
import functools, time, threading

def rate_limit(max_calls: int, period: float = 1.0):
    """
    Allow at most `max_calls` per `period` seconds.
    Raises RuntimeError when limit exceeded.
    Thread-safe.
    """
    calls: list = []
    lock = threading.Lock()

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                now = time.monotonic()
                # Remove calls outside the window
                while calls and now - calls[0] > period:
                    calls.pop(0)

                if len(calls) >= max_calls:
                    raise RuntimeError(
                        f"Rate limit: {func.__name__} exceeded "
                        f"{max_calls} calls per {period}s"
                    )
                calls.append(now)

            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage:
@rate_limit(max_calls=10, period=1.0)    # 10 calls/second
def call_external_api(endpoint):
    ...

@rate_limit(max_calls=100, period=60.0)  # 100 calls/minute
def send_email(to, subject, body):
    ...
```

---

## 7. `@validate_types` — Runtime Type Enforcement

```python
import functools, inspect

def validate_types(func):
    """
    Validate that arguments match Python type annotations.
    Only checks annotated parameters; ignores unannotated ones.
    Skips 'return' annotation.
    """
    hints  = {k: v for k, v in func.__annotations__.items() if k != "return"}
    sig    = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        for name, value in bound.arguments.items():
            if name in hints:
                expected = hints[name]
                # Handle Optional[X] = Union[X, None]
                import typing
                origin = getattr(expected, "__origin__", None)
                if origin is typing.Union:
                    if not isinstance(value, expected.__args__):
                        raise TypeError(
                            f"{func.__name__}(): '{name}' expected "
                            f"{expected}, got {type(value).__name__}"
                        )
                elif not isinstance(value, expected):
                    raise TypeError(
                        f"{func.__name__}(): '{name}' expected "
                        f"{expected.__name__}, got {type(value).__name__}"
                    )
        return func(*args, **kwargs)
    return wrapper

# Usage:
@validate_types
def create_order(user_id: int, total: float, notes: str = "") -> dict:
    return {"user": user_id, "total": total}

create_order(1, 99.99)          # ✅
create_order("1", 99.99)        # TypeError: 'user_id' expected int, got str
```

---

## 8. `@require_auth` — Authentication Guard

```python
import functools

def require_auth(roles=None):
    """
    Guard a function behind authentication.
    roles: list of allowed role strings, or None to allow any authenticated user.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get current user from context (Flask/FastAPI/custom)
            from myapp.context import current_user   # adjust to your framework
            if current_user is None:
                raise PermissionError(f"{func.__name__}: authentication required")
            if roles and current_user.role not in roles:
                raise PermissionError(
                    f"{func.__name__}: requires role in {roles}, "
                    f"user has '{current_user.role}'"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage:
@require_auth(roles=["admin", "superuser"])
def delete_user(user_id):
    ...

@require_auth()   # any authenticated user
def get_profile(user_id):
    ...
```

---

## 9. `@deprecated` — Deprecation Warning

```python
import functools, warnings

def deprecated(reason: str = "", replacement: str = ""):
    """
    Mark a function as deprecated. Emits DeprecationWarning on first call.
    """
    def decorator(func):
        msg = f"{func.__name__} is deprecated"
        if reason:
            msg += f": {reason}"
        if replacement:
            msg += f". Use {replacement} instead."

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage:
@deprecated(reason="slow O(n²) algorithm", replacement="process_orders_v2")
def process_orders(orders):
    ...
```

---

## 10. `@singleton` — Class Decorator: Single Instance

```python
import functools

def singleton(cls):
    """Ensure only one instance of the class exists."""
    instances = {}

    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

# Usage:
@singleton
class AppConfig:
    def __init__(self):
        self.data = load_config_from_disk()

cfg1 = AppConfig()
cfg2 = AppConfig()
assert cfg1 is cfg2   # True — same object
```

---

## 11. `@once` — Run Function Exactly Once

```python
import functools

def once(func):
    """
    Ensure function body runs only on the first call.
    Subsequent calls return the first result without re-executing.
    """
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if "result" not in cache:
            cache["result"] = func(*args, **kwargs)
        return cache["result"]

    wrapper.reset = lambda: cache.clear()
    return wrapper

# Usage:
@once
def initialize_database():
    print("Connecting to DB...")
    return db.connect()

initialize_database()   # "Connecting to DB..."
initialize_database()   # (silent — returns cached connection)
```

---

## 12. `@memoize` — Infinite Memoization

```python
import functools

def memoize(func):
    """Cache all results forever (no eviction). For pure functions only."""
    cache = {}

    @functools.wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]

    wrapper.cache = cache
    wrapper.cache_clear = lambda: cache.clear()
    return wrapper

# Alternative: use built-in (preferred for most cases):
@functools.lru_cache(maxsize=None)   # same as memoize but thread-safe
def fibonacci(n):
    if n < 2: return n
    return fibonacci(n-1) + fibonacci(n-2)
```

---

## 13. `@timeout` — Abort Long-Running Functions

```python
import functools, signal

def timeout(seconds: float):
    """
    Raise TimeoutError if function runs longer than `seconds`.
    POSIX only (Linux/Mac — uses SIGALRM).
    For Windows or threads, use concurrent.futures.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            def _handler(signum, frame):
                raise TimeoutError(
                    f"{func.__name__} timed out after {seconds}s"
                )
            old_handler = signal.signal(signal.SIGALRM, _handler)
            signal.setitimer(signal.ITIMER_REAL, seconds)
            try:
                return func(*args, **kwargs)
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, old_handler)
        return wrapper
    return decorator

# Cross-platform version using concurrent.futures:
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

def timeout_safe(seconds: float):
    """Cross-platform timeout using threads."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    return future.result(timeout=seconds)
                except FuturesTimeout:
                    raise TimeoutError(f"{func.__name__} timed out after {seconds}s")
        return wrapper
    return decorator

# Usage:
@timeout(seconds=5.0)
def fetch_external_data():
    ...
```

---

## 14. `@suppress` — Silently Ignore Exceptions

```python
import functools

def suppress(*exceptions, default=None, log=True):
    """
    Catch specified exceptions, return `default`, optionally log.
    Use carefully — swallowing exceptions hides bugs.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                if log:
                    import logging
                    logging.getLogger(__name__).warning(
                        "%s suppressed %s: %s", func.__name__, type(e).__name__, e
                    )
                return default
        return wrapper
    return decorator

# Usage:
@suppress(KeyError, ValueError, default={})
def parse_metadata(raw: str) -> dict:
    return json.loads(raw)   # returns {} if JSON is malformed
```

---

## 15. `@trace` — Deep Call Tracing for Debugging

```python
import functools, inspect, logging

trace_logger = logging.getLogger("trace")

def trace(func):
    """
    Detailed call trace: logs args, return value, execution time.
    For debugging only — remove from production.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        sig   = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        import time
        start = time.perf_counter()
        trace_logger.debug(
            "ENTER %s(%s)",
            func.__qualname__,
            ", ".join(f"{k}={v!r}" for k, v in bound.arguments.items())
        )
        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            trace_logger.debug(
                "EXIT  %s → %r  (%.4fs)", func.__qualname__, result, elapsed
            )
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start
            trace_logger.debug(
                "RAISE %s raised %s: %s  (%.4fs)",
                func.__qualname__, type(e).__name__, e, elapsed
            )
            raise
    return wrapper

# Usage (enable trace logger at DEBUG level during debugging):
# logging.getLogger("trace").setLevel(logging.DEBUG)

@trace
def calculate_tax(amount, rate):
    return amount * rate
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ➡️ Next | [11 — Iterators & Generators](../11_iterators_generators/theory.md) |
