# Practice — Production Decorator Patterns

12 questions covering all 4 chapters. Green = warm-up, Yellow = core skill, Orange = production-grade challenge.

---

### Q1 🟢 · @timed — Log execution time with perf_counter

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

Write a `@timed` decorator that prints `"func_name took X.XXXs"` using `time.perf_counter()` for high-resolution timing. The message should still appear if the function raises an exception (log the time, then re-raise).

<details>
<summary>Hint</summary>

Capture `start = time.perf_counter()` before the call, compute `elapsed = time.perf_counter() - start` in both the success path and inside the `except` block, then re-raise.
</details>

<details>
<summary>Answer</summary>

```python
import functools, time

def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            print(f"{func.__name__} took {elapsed:.3f}s")
            return result
        except Exception:
            elapsed = time.perf_counter() - start
            print(f"{func.__name__} failed after {elapsed:.3f}s")
            raise
    return wrapper

@timed
def slow_add(a, b):
    time.sleep(0.1)
    return a + b

slow_add(2, 3)   # slow_add took 0.100s
```
</details>

---

### Q2 🟢 · @logged — Log name, args, and return value

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

Write a `@logged` decorator that prints:
1. `"Calling func_name with args=(...) kwargs={...}"` before the call
2. `"func_name returned: <value>"` after the call

<details>
<summary>Hint</summary>

Use `functools.wraps`. Print before calling `func(*args, **kwargs)`, capture the result, print it, then return it.
</details>

<details>
<summary>Answer</summary>

```python
import functools

def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with args={args} kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned: {result!r}")
        return result
    return wrapper

@logged
def add(a, b):
    return a + b

add(3, 4)
# Calling add with args=(3, 4) kwargs={}
# add returned: 7
```
</details>

---

### Q3 🟡 · @retry — Fixed delay between attempts

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

Write `@retry(max_attempts=3, delay=1.0)` that retries the function up to `max_attempts` times with a fixed `delay` (seconds) between attempts. If all attempts fail, raise the last exception.

<details>
<summary>Hint</summary>

Loop `range(1, max_attempts + 1)`. On the last attempt, re-raise instead of sleeping. Track the exception to re-raise after the loop completes.
</details>

<details>
<summary>Answer</summary>

```python
import functools, time

def retry(max_attempts=3, delay=1.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < max_attempts:
                        print(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator

attempts = 0

@retry(max_attempts=3, delay=0.1)
def flaky():
    global attempts
    attempts += 1
    if attempts < 3:
        raise ConnectionError("not yet")
    return "ok"

print(flaky())   # "ok" after 3 attempts
```
</details>

---

### Q4 🟡 · @retry backoff — Exponential delay with jitter

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

Enhance `@retry` to use exponential backoff: the wait doubles after each failure. Add a `jitter` parameter (e.g. `0.1`) that adds a random offset between 0 and `jitter` seconds to each wait. Signature: `@retry(max_attempts=5, delay=0.5, backoff=2.0, jitter=0.1)`.

<details>
<summary>Hint</summary>

Start with `wait = delay`. After each failed attempt, compute `actual_wait = wait + random.uniform(0, jitter)`, sleep for `actual_wait`, then `wait *= backoff`.
</details>

<details>
<summary>Answer</summary>

```python
import functools, time, random

def retry(max_attempts=3, delay=1.0, backoff=2.0, jitter=0.1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    actual_wait = wait + random.uniform(0, jitter)
                    print(f"Attempt {attempt} failed — retrying in {actual_wait:.2f}s")
                    time.sleep(actual_wait)
                    wait *= backoff
        return wrapper
    return decorator
```

Wait sequence for `delay=0.5, backoff=2.0`: ~0.5s → ~1.0s → ~2.0s → ~4.0s. Jitter prevents thundering herd.
</details>

---

### Q5 🟡 · @circuit_breaker — States and basic implementation

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

Explain the three circuit breaker states in your own words, then implement a `CircuitBreaker` class that:
- Tracks `failure_count` and opens the circuit after `failure_threshold` failures
- Rejects calls immediately when `OPEN`, raising `RuntimeError`
- Transitions to `HALF_OPEN` after `recovery_timeout` seconds and allows one test call through
- Resets to `CLOSED` on any successful call

<details>
<summary>Hint</summary>

Three states: `CLOSED` (normal), `OPEN` (rejecting), `HALF_OPEN` (testing recovery). Use `time.time()` and a stored `opened_at` timestamp to decide when to transition from `OPEN` to `HALF_OPEN`.
</details>

<details>
<summary>Answer</summary>

```python
import functools, time, threading

class CircuitBreaker:
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(self, failure_threshold=5, recovery_timeout=60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = self.CLOSED
        self.opened_at = None
        self._lock = threading.Lock()

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self._lock:
                if self.state == self.OPEN:
                    if time.time() - self.opened_at > self.recovery_timeout:
                        self.state = self.HALF_OPEN
                    else:
                        raise RuntimeError(f"Circuit OPEN — {func.__name__} unavailable")
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
                        self.state = self.OPEN
                        self.opened_at = time.time()
                raise
        return wrapper

# States:
# CLOSED   — everything normal, requests pass through
# OPEN     — too many failures, requests rejected immediately (fail fast)
# HALF_OPEN — recovery window elapsed, one probe request allowed through
```
</details>

---

### Q6 🟡 · @validate_types — Enforce type annotations

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

Write `@validate_types` that reads a function's `__annotations__`, binds the call arguments using `inspect.signature`, and raises `TypeError` with a clear message if any annotated argument receives the wrong type. Skip the `return` annotation. Skip unannotated parameters.

<details>
<summary>Hint</summary>

Use `inspect.signature(func)`, then `sig.bind(*args, **kwargs)` followed by `bound.apply_defaults()`. Iterate `bound.arguments.items()` and check `isinstance(value, expected_type)`.
</details>

<details>
<summary>Answer</summary>

```python
import functools, inspect

def validate_types(func):
    hints = {k: v for k, v in func.__annotations__.items() if k != "return"}
    sig = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        for name, value in bound.arguments.items():
            if name in hints:
                expected = hints[name]
                if not isinstance(value, expected):
                    raise TypeError(
                        f"{func.__name__}(): '{name}' expected "
                        f"{expected.__name__}, got {type(value).__name__}"
                    )
        return func(*args, **kwargs)
    return wrapper

@validate_types
def create_order(user_id: int, total: float) -> dict:
    return {"user": user_id, "total": total}

create_order(1, 9.99)     # OK
create_order("1", 9.99)   # TypeError: 'user_id' expected int, got str
```
</details>

---

### Q7 🟡 · @require_auth — Role-based access control

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

Write `@require_auth(roles=["admin"])` that checks a `current_user` object (passed as a context variable or as the first argument — your choice). Raise `PermissionError` if the user is `None` (unauthenticated) or if their role is not in the allowed roles list.

<details>
<summary>Hint</summary>

For simplicity in this exercise, accept `current_user` as a keyword argument to the wrapped function. Check `if current_user is None` first, then `if roles and current_user.role not in roles`.
</details>

<details>
<summary>Answer</summary>

```python
import functools

def require_auth(roles=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user = kwargs.get("current_user")
            if user is None:
                raise PermissionError(f"{func.__name__}: authentication required")
            if roles and getattr(user, "role", None) not in roles:
                raise PermissionError(
                    f"{func.__name__}: requires {roles}, user has '{user.role}'"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator

from types import SimpleNamespace

@require_auth(roles=["admin"])
def delete_user(user_id, current_user=None):
    return f"Deleted {user_id}"

admin = SimpleNamespace(role="admin")
guest = SimpleNamespace(role="guest")

delete_user(42, current_user=admin)   # OK
delete_user(42, current_user=guest)   # PermissionError
delete_user(42)                        # PermissionError: authentication required
```
</details>

---

### Q8 🟡 · @deprecated — Emit DeprecationWarning with migration hint

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

Write `@deprecated(reason="...", replacement="...")` that emits a `DeprecationWarning` on every call. The warning message should include the function name, the reason, and the replacement name. Use `stacklevel=2` so the warning points to the caller's line, not inside the decorator.

<details>
<summary>Hint</summary>

`warnings.warn(msg, DeprecationWarning, stacklevel=2)`. Build the message string from the function name, reason, and replacement before the wrapper runs (at decoration time).
</details>

<details>
<summary>Answer</summary>

```python
import functools, warnings

def deprecated(reason="", replacement=""):
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

@deprecated(reason="O(n^2) complexity", replacement="fast_search")
def slow_search(items, target):
    return target in items

import warnings
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    slow_search([1, 2, 3], 2)
    print(w[0].message)
    # slow_search is deprecated: O(n^2) complexity. Use fast_search instead.
```
</details>

---

### Q9 🟡 · @ttl_cache — Cache with automatic expiry

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

Write `@ttl_cache(seconds=60)` that caches function results and returns the cached value on subsequent calls — but only if the entry is younger than `seconds`. After expiry, the function is called again and the cache is refreshed. Build a hashable key from `args` and `kwargs`.

<details>
<summary>Hint</summary>

Store `cache[key] = (result, time.monotonic())`. On lookup, check `time.monotonic() - stored_ts < seconds` before returning the cached value.
</details>

<details>
<summary>Answer</summary>

```python
import functools, time

def ttl_cache(seconds=60):
    def decorator(func):
        cache = {}

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
            return result

        wrapper.cache_clear = lambda: cache.clear()
        return wrapper
    return decorator

call_count = 0

@ttl_cache(seconds=1)
def expensive(x):
    global call_count
    call_count += 1
    return x * 2

expensive(5)   # call_count = 1
expensive(5)   # call_count = 1 (cached)
time.sleep(1.1)
expensive(5)   # call_count = 2 (expired)
```
</details>

---

### Q10 🟡 · @rate_limit — Sliding window enforcer

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

Write `@rate_limit(max_calls=10, period=1.0)` using a sliding window: keep a list of timestamps of recent calls, discard those older than `period`, and raise `RuntimeError` if the remaining count is at or above `max_calls`. Make it thread-safe with a `threading.Lock`.

<details>
<summary>Hint</summary>

Use `calls: list = []` and `lock = threading.Lock()` in the outer decorator scope (not inside `wrapper` — they need to persist across calls). Inside `wrapper`, acquire the lock, evict old timestamps, check the count, append the new timestamp.
</details>

<details>
<summary>Answer</summary>

```python
import functools, time, threading

def rate_limit(max_calls, period=1.0):
    calls = []
    lock = threading.Lock()

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                now = time.monotonic()
                while calls and now - calls[0] > period:
                    calls.pop(0)
                if len(calls) >= max_calls:
                    raise RuntimeError(
                        f"{func.__name__}: rate limit {max_calls}/{period}s exceeded"
                    )
                calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_calls=3, period=1.0)
def ping():
    return "pong"

ping()   # OK
ping()   # OK
ping()   # OK
ping()   # RuntimeError: rate limit 3/1.0s exceeded
```
</details>

---

### Q11 🟠 · @timeout — Raise TimeoutError after N seconds

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

Write `@timeout(seconds=5)` with two implementations:
1. POSIX version using `signal.SIGALRM` (Linux/Mac only)
2. Cross-platform version using `concurrent.futures.ThreadPoolExecutor`

Both must raise `TimeoutError` with a message including the function name and the time limit.

<details>
<summary>Hint</summary>

POSIX: `signal.setitimer(signal.ITIMER_REAL, seconds)` before calling the function, clear it in a `finally` block. Cross-platform: `executor.submit(func, *args, **kwargs)` then `future.result(timeout=seconds)`.
</details>

<details>
<summary>Answer</summary>

```python
import functools, signal
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

# POSIX version (Linux/Mac only):
def timeout(seconds):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            def _handler(signum, frame):
                raise TimeoutError(f"{func.__name__} timed out after {seconds}s")
            old = signal.signal(signal.SIGALRM, _handler)
            signal.setitimer(signal.ITIMER_REAL, seconds)
            try:
                return func(*args, **kwargs)
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, old)
        return wrapper
    return decorator

# Cross-platform version:
def timeout_safe(seconds):
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

@timeout_safe(seconds=0.5)
def slow():
    import time; time.sleep(2)

try:
    slow()
except TimeoutError as e:
    print(e)   # slow timed out after 0.5s
```
</details>

---

### Q12 🟠 · Capstone — @resilient combining retry + circuit breaker + timeout

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

Build `@resilient(retries=3, circuit_break_after=5, timeout=10)` that combines all three patterns:
- Wraps the function with `@timeout` first (innermost)
- Wraps that with a `CircuitBreaker` (middle)
- Wraps that with `@retry` (outermost)

The circuit breaker should count both timeout failures and genuine exceptions. Write the implementation and show a usage example.

<details>
<summary>Hint</summary>

Apply the decorators in reverse order of desired execution: innermost first. Create a `CircuitBreaker` instance per `@resilient` application, then chain: `func -> timeout_wrapper -> circuit_wrapper -> retry_wrapper`.
</details>

<details>
<summary>Answer</summary>

```python
import functools, time, random, threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

# --- timeout_safe ---
def _apply_timeout(func, seconds):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args, **kwargs)
            try:
                return future.result(timeout=seconds)
            except FuturesTimeout:
                raise TimeoutError(f"{func.__name__} timed out after {seconds}s")
    return wrapper

# --- circuit breaker ---
class _CB:
    CLOSED = "closed"; OPEN = "open"; HALF_OPEN = "half_open"
    def __init__(self, threshold, recovery=30.0):
        self.threshold = threshold; self.count = 0
        self.state = self.CLOSED; self.opened_at = None
        self._lock = threading.Lock()
    def wrap(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self._lock:
                if self.state == self.OPEN:
                    if time.time() - self.opened_at > 30:
                        self.state = self.HALF_OPEN
                    else:
                        raise RuntimeError(f"Circuit OPEN: {func.__name__}")
            try:
                r = func(*args, **kwargs)
                with self._lock:
                    self.count = 0; self.state = self.CLOSED
                return r
            except Exception:
                with self._lock:
                    self.count += 1
                    if self.count >= self.threshold:
                        self.state = self.OPEN; self.opened_at = time.time()
                raise
        return wrapper

# --- retry with backoff ---
def _apply_retry(func, attempts, delay=0.5, backoff=2.0):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wait = delay
        for attempt in range(1, attempts + 1):
            try:
                return func(*args, **kwargs)
            except RuntimeError:   # circuit open — don't retry
                raise
            except Exception as e:
                if attempt == attempts:
                    raise
                time.sleep(wait + random.uniform(0, 0.1))
                wait *= backoff
    return wrapper

# --- combined ---
def resilient(retries=3, circuit_break_after=5, timeout=10):
    def decorator(func):
        with_timeout  = _apply_timeout(func, timeout)
        cb            = _CB(circuit_break_after)
        with_circuit  = cb.wrap(with_timeout)
        with_retry    = _apply_retry(with_circuit, retries)
        return with_retry
    return decorator

# Usage:
@resilient(retries=3, circuit_break_after=5, timeout=2)
def call_service(endpoint):
    import requests
    return requests.get(endpoint).json()
```
</details>

---

## 🔁 Navigation

| | |
|---|---|
| Back to Module | [../theory.md](../theory.md) |
| Theory (this subfolder) | [theory.md](./theory.md) |
| Prev Subfolder Practice | [../01_class_decorators/practice.md](../01_class_decorators/practice.md) |

**Related:** [Decorator Theory](../theory.md) · [Production Patterns Theory](./theory.md)
