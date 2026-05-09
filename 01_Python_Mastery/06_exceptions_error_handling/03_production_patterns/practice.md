# Practice — Production Error Handling Patterns

15 questions covering retry, circuit breaker, graceful degradation, exception translation, logging, and anti-patterns.

---

## Quick Index

| # | Topic | Difficulty |
|---|---|---|
| [Q1](#q1) | Basic retry decorator | 🟡 Medium |
| [Q2](#q2) | Exponential backoff | 🟡 Medium |
| [Q3](#q3) | Add jitter | 🟠 Hard |
| [Q4](#q4) | Retry on specific exceptions only | 🟡 Medium |
| [Q5](#q5) | CircuitBreaker class | 🟠 Hard |
| [Q6](#q6) | Graceful degradation (3-tier fallback) | 🟡 Medium |
| [Q7](#q7) | Exception translation | 🟡 Medium |
| [Q8](#q8) | logger.exception vs logger.error | 🟡 Medium |
| [Q9](#q9) | Fix bare except with pass | 🟡 Medium |
| [Q10](#q10) | Fix overly broad Exception catch | 🟡 Medium |
| [Q11](#q11) | Anti-pattern: exception for control flow | 🟡 Medium |
| [Q12](#q12) | Anti-pattern: losing original exception | 🟡 Medium |
| [Q13](#q13) | Thread exception silently swallowed | 🟠 Hard |
| [Q14](#q14) | Capstone: safe_call() | 🟠 Hard |
| [Q15](#q15) | Capstone: resilient API client | 🟠 Hard |

---

<a id="q1"></a>

### Q1 — Basic Retry Decorator 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)



Write a `@retry(max_attempts=3)` decorator that calls the wrapped function up to `max_attempts` times. On final failure, re-raise the last exception.

<details>
<summary>Hint</summary>

Use a `for attempt in range(max_attempts)` loop inside the wrapper. On the last attempt (`attempt == max_attempts - 1`), let the exception propagate with `raise`.

</details>

<details>
<summary>Answer</summary>

```python
import functools

def retry(max_attempts=3):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if attempt == max_attempts - 1:
                        raise
        return wrapper
    return decorator

@retry(max_attempts=3)
def flaky():
    raise ConnectionError("down")
```

**Why:** The `raise` with no argument re-raises the current exception, preserving the original traceback. Without `raise`, the exception would be silently swallowed after the last attempt.

</details>

---

<a id="q2"></a>

### Q2 — Exponential Backoff 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)



Extend the retry decorator to add exponential backoff between attempts: `delay = base_delay * (2 ** attempt)`.

<details>
<summary>Hint</summary>

Add a `base_delay` parameter to the decorator. Use `time.sleep(base_delay * (2 ** attempt))` before retrying, but not on the final attempt.

</details>

<details>
<summary>Answer</summary>

```python
import time
import functools

def retry(max_attempts=3, base_delay=1.0):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if attempt == max_attempts - 1:
                        raise
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
        return wrapper
    return decorator
```

**Why:** Attempt 0 sleeps 1s, attempt 1 sleeps 2s, attempt 2 sleeps 4s. This gives the remote service progressively more time to recover rather than hammering it repeatedly.

</details>

---

<a id="q3"></a>

### Q3 — Add Jitter 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)



Add jitter to the backoff: `delay = base * (2 ** attempt) + random.uniform(0, base_delay)`. Explain why jitter is needed.

<details>
<summary>Hint</summary>

Import `random`. Add `random.uniform(0, base_delay)` to the computed delay. The result should be unpredictable enough that 500 clients won't all retry at the same millisecond.

</details>

<details>
<summary>Answer</summary>

```python
import time
import random
import functools

def retry(max_attempts=3, base_delay=1.0):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if attempt == max_attempts - 1:
                        raise
                    delay = base_delay * (2 ** attempt)
                    jitter = random.uniform(0, base_delay)
                    time.sleep(delay + jitter)
        return wrapper
    return decorator
```

**Why jitter:** Without it, all clients that failed at the same time will retry at the same future time — the "thundering herd". Jitter randomizes the offset so retries spread across a window, distributing load instead of repeating the spike.

</details>

---

<a id="q4"></a>

### Q4 — Retry on Specific Exceptions 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)



Modify the retry decorator to accept an `exceptions` tuple. Only retry if the raised exception is one of those types. Propagate all others immediately.

<details>
<summary>Hint</summary>

Change `except Exception` to `except exceptions as e`. Any exception not in that tuple will not be caught and will propagate naturally.

</details>

<details>
<summary>Answer</summary>

```python
def retry(max_attempts=3, base_delay=1.0, exceptions=(Exception,)):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    if attempt == max_attempts - 1:
                        raise
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=3, exceptions=(ConnectionError, TimeoutError))
def fetch(url):
    ...
```

**Why:** Retrying on `ValueError` or `KeyError` is wrong — those are programming errors that won't resolve with time. Only retry on errors that are genuinely transient (network issues, rate limits, temporary service outages).

</details>

---

<a id="q5"></a>

### Q5 — Implement CircuitBreaker 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)



Implement a `CircuitBreaker` class with:
- `failure_threshold` — how many failures before opening
- `reset_timeout` — seconds before transitioning from OPEN to HALF-OPEN
- `call(fn, *args)` method — executes fn, manages state transitions

<details>
<summary>Hint</summary>

Use an `Enum` for the three states. Track `failure_count` and `last_failure_time`. In `call()`: if OPEN, check elapsed time to decide whether to switch to HALF-OPEN. On success, reset to CLOSED. On failure, increment counter and potentially open.

</details>

<details>
<summary>Answer</summary>

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
                raise RuntimeError(f"Circuit OPEN — call blocked (retry in {self.reset_timeout - elapsed:.0f}s)")

        try:
            result = fn(*args, **kwargs)
            self._on_success()
            return result
        except Exception:
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

**Why:** Without a circuit breaker, a slow/failing downstream service causes your threads to pile up waiting for timeouts. The circuit breaker short-circuits those calls immediately once you know the service is down — protecting your system's thread pool and response times.

</details>

---

<a id="q6"></a>

### Q6 — Graceful Degradation 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)



Write `get_product_price(product_id)` that:
1. Tries a live pricing service
2. Falls back to a local cache (`price_cache` dict)
3. Falls back to a hardcoded default of `0.00`

<details>
<summary>Hint</summary>

Use a try/except around each tier. Use `.get()` for the cache lookup to avoid a KeyError. Each tier should return the same type (a float).

</details>

<details>
<summary>Answer</summary>

```python
import logging
logger = logging.getLogger(__name__)

price_cache = {"SKU-001": 9.99, "SKU-002": 14.99}
DEFAULT_PRICE = 0.00

def get_product_price(product_id):
    # Tier 1: live pricing service
    try:
        return pricing_service.get_price(product_id)
    except Exception:
        logger.warning("Pricing service unavailable, falling back to cache")

    # Tier 2: local cache
    cached = price_cache.get(product_id)
    if cached is not None:
        return cached

    # Tier 3: safe default
    logger.warning("Cache miss for %s, returning default price", product_id)
    return DEFAULT_PRICE
```

**Why:** The caller gets a usable float every time. The degradation is logged so on-call engineers can see that tier 1 was skipped — without the system crashing or returning None into downstream calculations.

</details>

---

<a id="q7"></a>

### Q7 — Exception Translation 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)



Write `create_user(email)` that catches `psycopg2.IntegrityError` (simulated) and raises a `UserAlreadyExistsError`. Use `raise ... from e` to preserve the chain.

<details>
<summary>Hint</summary>

Define `UserAlreadyExistsError` as a custom exception. In the except block, use `raise UserAlreadyExistsError(...) from e` — not just `raise UserAlreadyExistsError(...)`.

</details>

<details>
<summary>Answer</summary>

```python
class UserAlreadyExistsError(Exception):
    pass

class IntegrityError(Exception):
    pass  # simulating psycopg2.IntegrityError

def db_insert(email):
    raise IntegrityError("duplicate key value violates unique constraint")

def create_user(email):
    try:
        db_insert(email)
    except IntegrityError as e:
        raise UserAlreadyExistsError(
            f"User with email '{email}' already exists"
        ) from e

# Caller
try:
    create_user("alice@example.com")
except UserAlreadyExistsError as e:
    print(e)
    print("Caused by:", e.__cause__)
```

**Why `from e`:** Without it, the original traceback is lost and you can't tell *which* database operation caused the conflict. With `from e`, the full chain is visible in logs, and `e.__cause__` is accessible programmatically.

</details>

---

<a id="q8"></a>

### Q8 — logger.exception vs logger.error 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)



Show the difference in log output between `logger.error(str(e))` and `logger.exception(msg)` for a `ValueError`. Which should you use inside an `except` block?

<details>
<summary>Hint</summary>

Set up a basic logger to stdout. Call both inside the same `except` block and observe the output. `logger.exception()` is equivalent to `logger.error(..., exc_info=True)`.

</details>

<details>
<summary>Answer</summary>

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def demonstrate():
    try:
        int("not_a_number")
    except ValueError as e:
        # BAD — only logs the message, traceback lost
        logger.error(f"Conversion failed: {e}")
        # Output: ERROR — Conversion failed: invalid literal for int()...

        # GOOD — logs message + full traceback
        logger.exception("Conversion failed")
        # Output: ERROR — Conversion failed
        #         Traceback (most recent call last):
        #           File "...", line X, in demonstrate
        #             int("not_a_number")
        #         ValueError: invalid literal for int() with base 10: 'not_a_number'

        # EQUIVALENT to logger.exception — explicit level control
        logger.error("Conversion failed", exc_info=True)
```

**Why:** In production, `logger.error(str(e))` makes debugging nearly impossible — you see the error message but not where it came from or what called it. `logger.exception()` must be called inside an `except` block; anywhere else it logs `NoneType: None`.

</details>

---

<a id="q9"></a>

### Q9 — Fix: Bare Except with Pass 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)



The following code silently swallows all errors including `KeyboardInterrupt`. Show three different ways to fix it depending on intent.

```python
try:
    result = process_record(record)
except:
    pass
```

<details>
<summary>Hint</summary>

Three options: (1) catch specific type + log + return sentinel, (2) catch specific type + re-raise, (3) catch specific type + log + continue. Which you choose depends on whether the caller needs to know about the failure.

</details>

<details>
<summary>Answer</summary>

```python
# Option 1: log + return sentinel (caller checks for None)
try:
    result = process_record(record)
except ValueError as e:
    logger.exception("Failed to process record %s", record.id)
    result = None

# Option 2: log + re-raise (crash loudly — for unrecoverable errors)
try:
    result = process_record(record)
except ValueError:
    logger.exception("Unrecoverable record processing failure")
    raise

# Option 3: log + continue (inside a loop — skip bad records)
for record in records:
    try:
        process_record(record)
    except ValueError:
        logger.exception("Skipping malformed record %s", record.id)
        continue
```

**Why:** `except: pass` is the single most dangerous Python pattern. It catches `SystemExit`, `KeyboardInterrupt`, and `GeneratorExit` — signals that are supposed to terminate the process. At minimum, use `except Exception` (which excludes BaseException subclasses), and always log.

</details>

---

<a id="q10"></a>

### Q10 — Fix: Catching Exception Too Broadly 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)



A library function catches `Exception` and returns a fallback, hiding bugs in the pipeline. Fix it.

```python
def run_pipeline(data):
    try:
        return complex_pipeline(data)
    except Exception:
        return {}
```

<details>
<summary>Hint</summary>

Identify which exceptions are expected (transient operational errors) vs which are programming errors. Catch only the expected ones. Let `TypeError`, `AttributeError`, etc. propagate.

</details>

<details>
<summary>Answer</summary>

```python
# BEFORE — hides bugs in complex_pipeline
def run_pipeline(data):
    try:
        return complex_pipeline(data)
    except Exception:
        return {}

# AFTER — only catches expected operational errors
def run_pipeline(data):
    try:
        return complex_pipeline(data)
    except (NetworkError, TimeoutError, ServiceUnavailableError) as e:
        logger.exception("Pipeline failed due to transient error")
        return {}
    # TypeError, AttributeError, KeyError etc. propagate — they're bugs, not runtime errors
```

**Why:** If `complex_pipeline` has a `KeyError` because someone changed a data schema, you need to know. Returning `{}` silently makes that bug invisible for weeks. Only suppress errors you understand and have a deliberate response to.

</details>

---

<a id="q11"></a>

### Q11 — Anti-pattern: Exception for Control Flow 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)



Rewrite the following to not use an exception for normal control flow.

```python
def find_index(lst, target):
    try:
        return lst.index(target)
    except ValueError:
        return -1
```

<details>
<summary>Hint</summary>

Python lists have a method that handles "not found" without raising — use it.

</details>

<details>
<summary>Answer</summary>

```python
# Using exception for control flow (not wrong, but semantically odd)
def find_index_exception(lst, target):
    try:
        return lst.index(target)
    except ValueError:
        return -1

# Better — use the language's built-in "not found" support
def find_index(lst, target):
    return lst.index(target) if target in lst else -1

# Or for dicts
def get_config(key):
    return config.get(key, default_value)  # never raises
```

**Why:** Exceptions have overhead and signal "something unexpected happened." Using them for "item not in list" (a completely normal outcome) makes code harder to read and slightly slower. Prefer `in`, `.get()`, and conditional expressions for expected absent values.

</details>

---

<a id="q12"></a>

### Q12 — Anti-pattern: Losing the Original Exception 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)



Fix the following so the original exception is preserved in the chain.

```python
try:
    connect_to_db()
except psycopg2.OperationalError:
    raise DatabaseConnectionError("Could not connect to database")
```

<details>
<summary>Hint</summary>

Add `from e` to the raise statement. Also, make sure the except clause binds the exception to a variable (`as e`).

</details>

<details>
<summary>Answer</summary>

```python
# BEFORE — original traceback and details destroyed
try:
    connect_to_db()
except psycopg2.OperationalError:
    raise DatabaseConnectionError("Could not connect to database")

# AFTER — chain preserved
try:
    connect_to_db()
except psycopg2.OperationalError as e:
    raise DatabaseConnectionError("Could not connect to database") from e
```

**Why:** With `from e`, the traceback shows both the `DatabaseConnectionError` and the original `psycopg2.OperationalError` with line numbers. This tells you not just that the connection failed but exactly which `psycopg2` operation failed and why. Without it, you're debugging with one hand tied behind your back.

</details>

---

<a id="q13"></a>

### Q13 — Thread Exception Silently Swallowed 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)



Show that a thread exception is silently lost. Then fix it using `concurrent.futures.ThreadPoolExecutor`.

<details>
<summary>Hint</summary>

First demonstrate the problem: create a `Thread` with a target that raises, call `start()` + `join()`, and show that the main thread continues without error. Then show `executor.submit(...).result()` which re-raises the exception in the calling thread.

</details>

<details>
<summary>Answer</summary>

```python
import threading
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

def broken_worker():
    raise ValueError("worker failed")

# PROBLEM — exception silently lost
t = threading.Thread(target=broken_worker)
t.start()
t.join()
print("Main thread continues — error was swallowed silently")

# FIX — concurrent.futures re-raises exceptions when .result() is called
with ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(broken_worker)
    try:
        future.result()   # raises ValueError here, in the main thread
    except ValueError:
        logger.exception("Worker thread failed")
        # Full traceback is preserved and logged

# FIX (raw threads, if you must) — capture exception manually
result = {"error": None, "value": None}

def safe_worker():
    try:
        broken_worker()
    except Exception as e:
        result["error"] = e

t = threading.Thread(target=safe_worker)
t.start()
t.join()

if result["error"]:
    raise result["error"]
```

**Why:** Python's `threading.Thread` has no mechanism to propagate exceptions to the parent thread. The thread dies silently and your program continues with corrupted or missing state. `concurrent.futures` stores the exception on the `Future` object and re-raises it on `.result()`, giving you proper error visibility.

</details>

---

<a id="q14"></a>

### Q14 — Capstone: safe_call() 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)



Implement `safe_call(fn, *args, retries=3, fallback=None, **kwargs)` that:
- Retries the function up to `retries` times with exponential backoff + jitter
- Returns `fallback` if all retries fail (does not raise)
- Logs each failure with `logger.exception()`

<details>
<summary>Hint</summary>

Combine the retry loop (Q2 + Q3) with a final fallback return. After the loop exhausts all attempts, catch the last exception and return `fallback`. Don't forget to log each failure separately so you have a record of all attempts.

</details>

<details>
<summary>Answer</summary>

```python
import time
import random
import logging

logger = logging.getLogger(__name__)

def safe_call(fn, *args, retries=3, base_delay=1.0, fallback=None, **kwargs):
    last_exception = None
    for attempt in range(retries):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            last_exception = e
            logger.exception(
                "safe_call: attempt %d/%d failed for %s",
                attempt + 1, retries, fn.__name__
            )
            if attempt < retries - 1:
                delay = base_delay * (2 ** attempt) + random.uniform(0, base_delay)
                time.sleep(delay)

    logger.error(
        "safe_call: all %d attempts exhausted for %s, returning fallback",
        retries, fn.__name__
    )
    return fallback

# Usage
result = safe_call(fetch_user, user_id=42, retries=3, fallback={"name": "Unknown"})
```

**Why `fallback=None` default:** The caller explicitly opts into degradation. A fallback of `None` is intentional — the caller must check for it and handle it. This avoids the anti-pattern of silently returning fake data that looks real.

</details>

---

<a id="q15"></a>

### Q15 — Capstone: Resilient API Client 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)



Build a `ResilientAPIClient` class that combines:
- Retry with exponential backoff + jitter
- Circuit breaker (opens after 3 failures, resets after 10s)
- `logger.exception()` on every failure

The class should have a `get(url)` method.

<details>
<summary>Hint</summary>

Compose the `CircuitBreaker` from Q5 inside the client. In `get()`, wrap the request inside `circuit_breaker.call(...)`. Add the retry loop around the circuit breaker call. Log at each failure tier.

</details>

<details>
<summary>Answer</summary>

```python
import time
import random
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class State(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=3, reset_timeout=10):
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
                raise RuntimeError("Circuit is OPEN")
        try:
            result = fn(*args, **kwargs)
            self.failure_count = 0
            self.state = State.CLOSED
            return result
        except Exception:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = State.OPEN
            raise

class ResilientAPIClient:
    def __init__(self, max_retries=3, base_delay=1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, reset_timeout=10)

    def get(self, url):
        for attempt in range(self.max_retries):
            try:
                return self.circuit_breaker.call(self._http_get, url)
            except RuntimeError as e:
                # Circuit is open — don't retry
                logger.error("Circuit open, aborting request to %s: %s", url, e)
                raise
            except Exception:
                logger.exception(
                    "Request attempt %d/%d failed for %s",
                    attempt + 1, self.max_retries, url
                )
                if attempt == self.max_retries - 1:
                    raise
                delay = self.base_delay * (2 ** attempt) + random.uniform(0, self.base_delay)
                time.sleep(delay)

    def _http_get(self, url):
        # Replace with requests.get(url) in real usage
        raise ConnectionError(f"Simulated failure for {url}")

# Usage
client = ResilientAPIClient(max_retries=3)
try:
    data = client.get("https://api.example.com/users")
except Exception:
    logger.exception("All retries exhausted")
```

**Why circuit breaker + retry together:** Retry without circuit breaker wastes time on a known-dead service. Circuit breaker without retry gives up too fast on transient blips. Together: retry handles momentary flickers, circuit breaker handles sustained outages.

</details>

---

**[⬆ Back to 06_exceptions](../theory.md)** · **[Master Practice →](../practice.md)**
