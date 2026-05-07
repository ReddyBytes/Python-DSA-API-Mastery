# Production Error Handling Patterns

Catching an exception is the easy part — deciding what to do next is what separates fragile scripts from production systems. Retry, degrade gracefully, or fail loudly: each choice has a cost.

---

## Learning Priority

| Priority | Topics |
|---|---|
| **Must Learn** | Retry with backoff · anti-patterns (bare except, silent pass) · `logger.exception()` |
| **Should Learn** | Circuit breaker · graceful degradation · exception translation |
| **Good to Know** | Exceptions in threads (silently lost) · `concurrent.futures` |
| **Reference** | `tenacity` library · async exception handling |

---

## Table of Contents

1. [Retry with Exponential Backoff](#1-retry-with-exponential-backoff)
2. [The Thundering Herd Problem](#2-the-thundering-herd-problem)
3. [Circuit Breaker](#3-circuit-breaker)
4. [Graceful Degradation](#4-graceful-degradation)
5. [Exception Translation](#5-exception-translation)
6. [Logging Correctly](#6-logging-correctly)
7. [Anti-Patterns](#7-anti-patterns)
8. [Exceptions in Threads](#8-exceptions-in-threads)

---

## 1. Retry with Exponential Backoff

When a remote call fails, the instinct is to try again immediately. But slamming a struggling service with instant retries makes it worse. **Exponential backoff** spaces retries out — each attempt waits twice as long as the last.

**Formula:**

```
delay = base_delay * (2 ** attempt)
```

| Attempt | base=1s | Delay |
|---------|---------|-------|
| 0 | 1 | 1s |
| 1 | 1 | 2s |
| 2 | 1 | 4s |
| 3 | 1 | 8s |

**ASCII timeline:**

```
Attempt 0 → FAIL
|--1s--|
Attempt 1 → FAIL
|----2s----|
Attempt 2 → FAIL
|--------4s--------|
Attempt 3 → SUCCESS
```

**Implementation:**

```python
import time
import functools

def retry(max_attempts=3, base_delay=1.0, exceptions=(Exception,)):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=3, base_delay=1.0, exceptions=(ConnectionError,))
def fetch_data(url):
    ...
```

Key rules:
- Always set a `max_retries` cap — never retry forever
- Only retry on **transient** errors (network timeouts, 429, 503) — never on 400 Bad Request
- Track the attempt number so you can log it

---

## 2. The Thundering Herd Problem

Imagine 500 servers all fail at the same instant and all start retrying with identical delays. At t=2s, 500 requests slam the backend simultaneously. This is the **thundering herd** — synchronized retries that overwhelm the service you're trying to recover.

**Without jitter:**

```
t=0s    [FAIL FAIL FAIL FAIL FAIL]  ← all 500 fail
t=2s    [RETRY RETRY RETRY RETRY]   ← all 500 retry at same moment
t=4s    [RETRY RETRY RETRY RETRY]   ← still synchronized
```

**With jitter** (random offset added to each delay):

```
delay = base * (2 ** attempt) + random.uniform(0, base)

t=0s    [FAIL FAIL FAIL FAIL FAIL]
t=2.1s  [retry]
t=2.4s        [retry]
t=2.7s              [retry]         ← spread out, load distributed
t=3.2s                    [retry]
```

```python
import random
import time

def retry_with_jitter(max_attempts=3, base_delay=1.0):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    delay = base_delay * (2 ** attempt)
                    jitter = random.uniform(0, base_delay)
                    time.sleep(delay + jitter)
        return wrapper
    return decorator
```

Rule of thumb: always add jitter when multiple clients share the same retry target.

---

## 3. Circuit Breaker

A **circuit breaker** wraps calls to an external service and tracks failure rate. If failures exceed a threshold, it "opens" the circuit and stops making calls entirely — giving the downstream system time to recover.

Think of it like a fuse in your house: a power surge trips the fuse, protecting your appliances. You don't keep plugging things in while the surge is happening.

**Three states:**

```
                  failures > threshold
     CLOSED ─────────────────────────────► OPEN
       ▲                                     │
       │         reset_timeout elapsed       │
       │                                     ▼
    success ◄──────────────────────── HALF-OPEN
    (reclose)           (one test call allowed)
```

| State | Behavior |
|---|---|
| **CLOSED** | Normal operation. Calls go through. Failure counter tracked. |
| **OPEN** | All calls blocked immediately. No network traffic. Fail fast. |
| **HALF-OPEN** | One test call allowed. Success → CLOSED. Failure → OPEN again. |

```python
import time
from enum import Enum

class State(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=30):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = State.CLOSED

    def call(self, fn, *args, **kwargs):
        if self.state == State.OPEN:
            elapsed = time.time() - self.last_failure_time
            if elapsed > self.reset_timeout:
                self.state = State.HALF_OPEN
            else:
                raise RuntimeError("Circuit is OPEN — call blocked")

        try:
            result = fn(*args, **kwargs)
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

When to use it: any call to an external service that can cascade failures into your system (databases, third-party APIs, microservices).

---

## 4. Graceful Degradation

**Graceful degradation** means your system keeps working when a dependency fails — just with reduced functionality, not a crash.

The pattern is a **fallback hierarchy**: try the best source first, then progressively simpler ones.

```
Live API call
    │ fails?
    ▼
Cached result (Redis / in-memory)
    │ cache miss?
    ▼
Hardcoded default / empty response
    │ even that fails?
    ▼
Explicit error response (never silent crash)
```

```python
def get_user_recommendations(user_id):
    # Tier 1: live ML service
    try:
        return recommendation_service.get(user_id)
    except ServiceUnavailableError:
        pass

    # Tier 2: cached result from last successful call
    cached = cache.get(f"recs:{user_id}")
    if cached:
        return cached

    # Tier 3: safe default
    return DEFAULT_RECOMMENDATIONS
```

Key rule: the caller should not need to know which tier was used. Return the same shape of data from every tier.

---

## 5. Exception Translation

In a **layered architecture**, lower layers (database, HTTP clients) throw infrastructure-specific exceptions. Upper layers (business logic, API handlers) should not leak those details.

**Exception translation** catches a low-level exception and raises a domain-specific one:

```
Infrastructure layer:   psycopg2.IntegrityError (constraint violation)
                            │
                            ▼  (translation layer)
Domain layer:           UserAlreadyExistsError
                            │
                            ▼  (API layer)
HTTP response:          409 Conflict
```

```python
# Without translation — leaks DB details to callers
def create_user(email):
    db.execute("INSERT INTO users ...")  # raises psycopg2.IntegrityError

# With translation
def create_user(email):
    try:
        db.execute("INSERT INTO users ...")
    except psycopg2.IntegrityError as e:
        raise UserAlreadyExistsError(f"User {email} already exists") from e
```

The `from e` preserves the original exception as `__cause__` — visible in tracebacks, but the caller only needs to handle `UserAlreadyExistsError`.

---

## 6. Logging Correctly

The single most common logging mistake: using `logger.error(str(e))` which loses the traceback.

**`logger.error(str(e))`** — logs only the message string. No traceback. No line numbers. Nearly useless in production.

**`logger.exception(msg)`** — logs the message AND the full traceback. Must be called inside an `except` block.

**`logger.error(msg, exc_info=True)`** — same as `logger.exception()`, but lets you control the level.

```python
import logging
logger = logging.getLogger(__name__)

# BAD — traceback lost
try:
    result = fetch_data()
except requests.Timeout as e:
    logger.error(f"Timeout: {e}")  # only "Timeout: HTTPSConnectionPool..."

# GOOD — full traceback preserved
try:
    result = fetch_data()
except requests.Timeout:
    logger.exception("Timeout fetching data")  # includes full stack trace

# ALSO GOOD — same output, explicit level control
try:
    result = fetch_data()
except requests.Timeout:
    logger.error("Timeout fetching data", exc_info=True)
```

Rule: in a `except` block, always use `logger.exception()` unless you have a specific reason not to.

---

## 7. Anti-Patterns

### Anti-pattern 1: Bare `except` with `pass`

```python
# BAD — swallows everything silently, including KeyboardInterrupt
try:
    process()
except:
    pass

# GOOD — catch specific, log it
try:
    process()
except ValueError as e:
    logger.exception("Invalid input during process()")
    return None
```

### Anti-pattern 2: Catching `Exception` too broadly

```python
# BAD — catches programming errors (AttributeError, TypeError) you should fix
try:
    result = complex_pipeline(data)
except Exception:
    return fallback

# GOOD — only catch errors you expect and can handle
try:
    result = complex_pipeline(data)
except (NetworkError, TimeoutError):
    return fallback
```

### Anti-pattern 3: Losing the original exception (exception chaining broken)

```python
# BAD — original traceback destroyed
try:
    db.query(sql)
except psycopg2.Error as e:
    raise DatabaseError("Query failed")  # where did it come from?

# GOOD — chain preserved with 'from e'
try:
    db.query(sql)
except psycopg2.Error as e:
    raise DatabaseError("Query failed") from e
```

### Anti-pattern 4: Exception for normal control flow

```python
# BAD — exceptions are slow and semantically wrong for "not found"
def get_user(user_id):
    try:
        return users[user_id]
    except KeyError:
        return None

# GOOD — use .get() for expected absence
def get_user(user_id):
    return users.get(user_id)  # returns None naturally
```

### Anti-pattern 5: Swallowing in a library function

```python
# BAD — library silently absorbs errors, callers can't react
def parse_config(path):
    try:
        return json.load(open(path))
    except Exception:
        return {}  # caller has no idea config failed to load

# GOOD — let it propagate, or re-raise with context
def parse_config(path):
    try:
        return json.load(open(path))
    except FileNotFoundError as e:
        raise ConfigError(f"Config file not found: {path}") from e
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config: {path}") from e
```

---

## 8. Exceptions in Threads

Python threads **silently swallow exceptions**. If a thread raises an unhandled exception, it dies quietly — no crash, no log, nothing.

```python
import threading

def broken():
    raise ValueError("something went wrong")

t = threading.Thread(target=broken)
t.start()
t.join()

print("Main thread continues")  # prints fine — exception silently lost
```

The fix is to use `concurrent.futures.ThreadPoolExecutor`, which preserves exceptions and re-raises them when you call `.result()`:

```python
from concurrent.futures import ThreadPoolExecutor

def broken():
    raise ValueError("something went wrong")

with ThreadPoolExecutor() as executor:
    future = executor.submit(broken)
    try:
        future.result()   # re-raises the ValueError here
    except ValueError as e:
        logger.exception("Worker thread failed")
```

If you must use raw threads, wrap the target to capture exceptions manually:

```python
import threading

result = {"error": None}

def safe_target():
    try:
        broken()
    except Exception as e:
        result["error"] = e

t = threading.Thread(target=safe_target)
t.start()
t.join()

if result["error"]:
    raise result["error"]
```

Rule: prefer `concurrent.futures` over raw threads for any work where exceptions must be caught.

---

## Navigation

**[⬆ Back to 06_exceptions](../theory.md)**

**Prev:** [02 Custom Exceptions ←](../02_custom_exceptions/theory.md) &nbsp;|&nbsp;

**Practice:** [practice.md](./practice.md) · [Master →](../practice.md)
