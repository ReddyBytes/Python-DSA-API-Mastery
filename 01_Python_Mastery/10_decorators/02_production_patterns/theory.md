# 🏭 Production Decorator Patterns — 15 Battle-Tested Recipes

Every production codebase is just a set of cross-cutting concerns (timing, logging, retrying, gating) bolted onto business logic — decorators are how Python lets you attach those concerns without touching the logic itself. Master these 15 patterns and you will recognize them everywhere: in Django, FastAPI, Celery, and every internal framework you will ever use.

---

## 📌 Learning Priority

**Must Learn** — `@timed`, `@logged`, `@retry` with backoff, `@validate_types`
**Should Learn** — `@circuit_breaker`, `@ttl_cache`, `@rate_limit`, `@require_auth`, `@deprecated`
**Good to Know** — `@singleton`, `@once`, `@memoize`, `@timeout`, `@suppress`
**Reference** — `@trace` (debugging aid, not for production code)

---

## Chapter 1: Observability

> Imagine you deploy a service and the CEO calls at 2 AM saying "the checkout is slow." Without observability decorators, you are staring at 50,000 lines of code with no clue where the time went. With `@timed` and `@logged` wrapped around your key functions, every request writes its own story to the log file before you even open your laptop.

### 1. `@timed` — Execution Timer

A stopwatch you snap around any function. When the function returns (or crashes), it writes how long it took to the log. Production engineers wrap slow I/O — DB queries, API calls, file reads — with this immediately when investigating latency.

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

**Gotcha:** `time.perf_counter()` is the right clock here — it is monotonic and high-resolution. Never use `time.time()` for elapsed measurements; it can jump backward when the system clock is adjusted (NTP sync, DST).

---

### 2. `@logged` — Call Logger

Where `@timed` measures duration, `@logged` records intent: what was called, with what arguments, and what came back. The configurable flags (`log_args`, `log_result`) mean you can be verbose in development and quiet in production by toggling a single parameter.

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

**Gotcha:** Never log raw args in production if they contain passwords, tokens, or PII. Use `log_args=False` (the default) at the call site for sensitive functions.

---

### 3. `@trace` — Deep Call Tracing for Debugging

A surgeon's loupe: far more detail than `@logged` — every argument by name, the return value, the exact time to microsecond. You reach for `@trace` when you are debugging a gnarly interaction and need the full picture, then you remove it before merging.

```python
import functools, inspect, logging, time

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
                "EXIT  %s -> %r  (%.4fs)", func.__qualname__, result, elapsed
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

# Enable only during debugging:
# logging.getLogger("trace").setLevel(logging.DEBUG)

@trace
def calculate_tax(amount, rate):
    return amount * rate
```

**Gotcha:** `@trace` uses `func.__qualname__` (e.g. `MyClass.method`) not just `__name__`, which is essential for tracing methods on classes where multiple classes might have the same method name.

---

## Chapter 2: Reliability

> Think of reliability decorators as the shock absorbers in a car. The road (the network, external APIs, user inputs) is full of bumps. Without shock absorbers your users feel every one. With `@retry`, `@circuit_breaker`, and `@timeout` in place, transient failures are absorbed silently and catastrophic failures are contained before they cascade.

### 4. `@retry` — Retry with Exponential Backoff

The real world is flaky: database connections timeout, third-party APIs return 503, S3 has momentary hiccups. A bare retry loop works but hammers the failing service with a thundering herd the moment it recovers. Exponential backoff with jitter is the industry solution: wait longer after each failure, add a small random offset so thousands of clients do not all retry at the same millisecond.

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

    delay:      initial wait time in seconds
    backoff:    multiplier applied after each failure (2.0 = double each time)
    jitter:     random seconds added to prevent thundering herd
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

**Gotcha:** Always pass a specific `exceptions` tuple. Retrying on bare `Exception` will retry `ValueError` and `KeyError` — pure bugs that no amount of waiting will fix.

---

### 5. `@circuit_breaker` — Stop Hammering a Failing Service

The circuit breaker is the fuse box of microservices. When a downstream dependency (payment gateway, ML inference service, external API) starts failing, you do not want every request to wait for a 30-second timeout before giving up. The circuit breaker counts failures and after a threshold, "trips open" — immediately rejecting requests rather than waiting. After a recovery window, it lets one test request through. If that succeeds, the circuit closes again.

```python
import functools, time, threading

class CircuitBreaker:
    """
    Three states:
    CLOSED    -> normal, requests flow through
    OPEN      -> failing, requests immediately rejected
    HALF-OPEN -> one test request allowed to check if service recovered
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

**Gotcha:** One `CircuitBreaker` instance wraps one function. If you need to protect multiple functions that share the same dependency (e.g., all calls to the payment gateway), create one shared `CircuitBreaker` instance and apply it to all of them — they will share the failure count.

---

### 6. `@timeout` — Abort Long-Running Functions

A hung function is worse than a failed one: it holds a thread, a DB connection, or a lock indefinitely. `@timeout` puts a hard ceiling on how long any function is allowed to run. The POSIX version uses `SIGALRM` (cheapest, zero overhead); the cross-platform version uses a thread (works on Windows).

```python
import functools, signal

def timeout(seconds: float):
    """
    Raise TimeoutError if function runs longer than `seconds`.
    POSIX only (Linux/Mac) — uses SIGALRM.
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

# Cross-platform alternative using concurrent.futures:
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

**Gotcha:** The `SIGALRM` version only works in the main thread — Python delivers signals only there. For functions called from worker threads, use `timeout_safe` instead.

---

### 7. `@suppress` — Silently Ignore Exceptions

Sometimes the right answer to an exception is "log it and move on." Metrics enrichment, optional cache warming, analytics side-effects — these should never crash the main request. `@suppress` makes the contract explicit: this function is best-effort.

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

**Gotcha:** Never suppress `Exception` or `BaseException` — you will hide actual bugs. Always specify the exact exception types you expect and are prepared to ignore.

---

## Chapter 3: Performance

> Performance decorators are like hiring a secretary who remembers every answer you have ever given, tells salespeople to call back later if you are too busy, and refuses to schedule the same meeting twice. The function itself does not change — the decorator intercepts calls before they even reach the function.

### 8. `@ttl_cache` — Cache with Time-To-Live

`functools.lru_cache` is great but it caches forever. For feature flags, config values, or any data that changes over time, you need results to expire. `@ttl_cache` adds a timestamp to each cached entry and treats it as stale after N seconds.

```python
import functools, time

def ttl_cache(seconds: float = 60, maxsize: int = 128):
    """Cache function results for `seconds` before expiring."""
    def decorator(func):
        cache: dict = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
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

**Gotcha:** The cache dict is shared across all callers for the lifetime of the process — it is not per-request. If you need per-user or per-request caching, this is the wrong tool.

---

### 9. `@memoize` — Infinite Memoization

The simplest possible cache: every unique set of arguments maps to exactly one stored result, forever. No eviction, no expiry. Perfect for pure mathematical functions (Fibonacci, factorials, hash computations) where the same input always yields the same output.

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

# Preferred built-in alternative (thread-safe):
@functools.lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2: return n
    return fibonacci(n-1) + fibonacci(n-2)
```

**Gotcha:** This only works for functions whose arguments are hashable (ints, strings, tuples). Pass a list and you get `TypeError: unhashable type`. For mutable args, convert to a tuple before calling.

---

### 10. `@rate_limit` — Calls Per Time Window

APIs charge per call, SMTP servers block you for spamming, and external services have rate limits enforced by IP. `@rate_limit` enforces a maximum call count within a sliding time window — at the function level, before any HTTP request is made. The sliding window implementation (track timestamps, evict old ones) is the most accurate approach.

```python
import functools, time, threading

def rate_limit(max_calls: int, period: float = 1.0):
    """
    Allow at most `max_calls` per `period` seconds.
    Raises RuntimeError when limit exceeded. Thread-safe.
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

**Gotcha:** This is a per-process rate limiter — each worker process has its own counter. In a multi-process deployment (Gunicorn with 4 workers), the effective rate limit is `max_calls * num_workers`. For distributed rate limiting, use Redis with a sliding-window Lua script.

---

### 11. `@once` — Run Function Exactly Once

Initialization code — loading a config file, warming a model, seeding a random number generator — should run exactly once no matter how many times the function is called. `@once` captures the first result and returns it on all subsequent calls without re-executing the function body.

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

initialize_database()   # "Connecting to DB..." — runs
initialize_database()   # (silent — returns cached connection)
```

**Gotcha:** Arguments on the second call are silently ignored — the cached result from the first call is always returned regardless of what you pass. If this function should behave differently for different arguments, use `@memoize` instead.

---

## Chapter 4: Safety and Access

> Safety decorators are the bouncers, ID checkers, and "out of service" signs of your codebase. They intercept calls before the function body runs and decide: are the inputs valid? does this caller have permission? should this function even exist? Getting these right at the decorator layer means your business logic stays clean — it never needs to know about auth rules or type checking.

### 12. `@validate_types` — Runtime Type Enforcement

Python's type annotations are hints by default — the interpreter ignores them at runtime. `@validate_types` makes them enforced: it reads the function's `__annotations__`, binds the actual arguments, and raises `TypeError` immediately if any annotated parameter receives the wrong type. This catches a whole class of bugs at the boundary layer before they corrupt deeper state.

```python
import functools, inspect, typing

def validate_types(func):
    """
    Validate that arguments match Python type annotations.
    Only checks annotated parameters; ignores unannotated ones.
    Skips 'return' annotation.
    """
    hints = {k: v for k, v in func.__annotations__.items() if k != "return"}
    sig   = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        for name, value in bound.arguments.items():
            if name in hints:
                expected = hints[name]
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

create_order(1, 99.99)       # OK
create_order("1", 99.99)     # TypeError: 'user_id' expected int, got str
```

**Gotcha:** This does not handle generic types like `List[int]` or `Dict[str, Any]` — it only checks the container type, not the element types. For deep validation of structured data, use Pydantic instead.

---

### 13. `@require_auth` — Authentication Guard

Every protected endpoint needs to answer two questions: "Are you logged in?" and "Do you have permission?" `@require_auth` answers both at the decorator layer, before the business logic ever runs. The `roles` parameter lets you express fine-grained access control in a single line at the definition site.

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

**Gotcha:** The `current_user` import here is a stub — in practice you thread the user through a context variable (`contextvars.ContextVar`) or a framework-provided request context (Flask's `g`, FastAPI's `Depends`). The decorator pattern stays the same regardless.

---

### 14. `@deprecated` — Deprecation Warning

When you replace a function with a better version, you cannot just delete the old one — other code depends on it. `@deprecated` buys you a migration window: the old function still works, but every call emits a `DeprecationWarning` pointing callers to the replacement. Python's warning system lets teams enable these as errors in CI (`-W error::DeprecationWarning`) to catch stragglers.

```python
import functools, warnings

def deprecated(reason: str = "", replacement: str = ""):
    """Mark a function as deprecated. Emits DeprecationWarning on every call."""
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
@deprecated(reason="slow O(n^2) algorithm", replacement="process_orders_v2")
def process_orders(orders):
    ...
```

**Gotcha:** `stacklevel=2` is critical — it makes the warning point to the call site (where the deprecated function was called from), not to the line inside the decorator wrapper. Without it, every warning would point to the same line in `decorator_patterns.py`, which is useless.

---

### 15. `@singleton` — Class Decorator: Single Instance

A singleton ensures that no matter how many times you instantiate a class, you always get the same object back. Database connection pools, config loaders, and logger registries are classic singletons: expensive to create, safe to share, wrong to duplicate.

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

**Gotcha:** This implementation is not thread-safe — two threads could both pass the `if cls not in instances` check simultaneously and create two instances. Add a `threading.Lock()` around the check-and-set if the class is first instantiated in a multi-threaded context (e.g., at request time rather than at startup).

---

## 🔁 Navigation

| | |
|---|---|
| Back to Module | [../theory.md](../theory.md) |
| Practice | [practice.md](./practice.md) |
| Prev Subfolder | [../01_class_decorators/theory.md](../01_class_decorators/theory.md) |

**Related:** [Decorator Theory](../theory.md) · [Class Decorators](../01_class_decorators/theory.md)
