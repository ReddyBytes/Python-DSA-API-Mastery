# 🛑 06 — Exceptions & Error Handling
## From "Please Don't Crash" to Production-Grade Reliability

> *"Writing code that works when everything goes right is easy.*
> *Writing code that survives when everything goes wrong — that's engineering."*

---

## 🎬 The Story

It's 2 AM. Your company's payment API is down.
Every failed payment costs real money and customer trust.
The on-call engineer opens the logs:

```
Traceback (most recent call last):
  File "payment.py", line 47, in process_payment
    result = gateway.charge(card, amount)
  File "gateway.py", line 23, in charge
    return self._client.post(url, data)
requests.exceptions.ConnectionError: HTTPSConnectionPool(host='api.stripe.com', port=443):
Max retries exceeded with url: /v1/charges
```

The service crashed. No retry logic. No fallback. Just crash.

This story plays out every day in systems worldwide.
The difference between a resilient system and a fragile one is almost entirely in how it handles the unexpected.

That's what this chapter is about.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`try`/`except`/`finally` · Specific exception types · `raise` · Custom exceptions · Context managers for cleanup

**Should Learn** — Important for real projects, comes up regularly:
`raise X from Y` / `raise X from None` · Exception hierarchy · `else` clause on try · Retry patterns

**Good to Know** — Useful in specific situations:
`warnings` module · `sys.exc_info()` · `atexit` module

**Reference** — Know it exists, look up when needed:
`ExceptionGroup` (Python 3.11+) · Signal handlers · `warnings.filterwarnings`

---

## 🧠 Chapter 1 — What Actually Happens When Python Raises an Exception

When Python encounters an error (like dividing by zero), here's the exact sequence:

```
1. Python creates an exception OBJECT (e.g., ZeroDivisionError instance)
2. Execution STOPS at the exact line
3. Python looks for a handler by walking UP the call stack
4. If a handler is found → execute it, resume after the try/except block
5. If no handler found → program crashes, prints traceback
```

```python
def level3():
    return 10 / 0              # ← exception RAISED here

def level2():
    return level3()            # ← propagates up (no handler here)

def level1():
    return level2()            # ← propagates up (no handler here)

level1()                       # ← no handler here either → CRASH
```

```
CALL STACK AT CRASH:
┌─────────────────────────────────────────────┐
│  level3()  ← ZeroDivisionError raised HERE  │
│  level2()  ← no handler, propagates up      │
│  level1()  ← no handler, propagates up      │
│  <module>  ← no handler → CRASH             │
└─────────────────────────────────────────────┘

Traceback (most recent call last):
  File "main.py", line 9, in <module>
    level1()
  File "main.py", line 7, in level1
    return level2()
  File "main.py", line 4, in level2
    return level3()
  File "main.py", line 1, in level3
    return 10 / 0
ZeroDivisionError: division by zero
```

> **Key insight:** Exceptions are **objects** — instances of exception classes.
> They carry data: message, traceback, cause chain.
> They're not just error messages.

---

## 🗺️ Chapter 2 — The Exception Hierarchy

Understanding the tree tells you exactly what you're catching.

```
BaseException
 ├── SystemExit              ← sys.exit() — don't catch unless needed
 ├── KeyboardInterrupt       ← Ctrl+C — don't swallow this!
 ├── GeneratorExit           ← generator .close() called
 └── Exception               ← parent of almost all catchable errors
      ├── ArithmeticError
      │    ├── ZeroDivisionError      10 / 0
      │    ├── OverflowError          math.exp(1000)
      │    └── FloatingPointError
      │
      ├── LookupError
      │    ├── IndexError             [1,2,3][9]
      │    └── KeyError               {}["missing"]
      │
      ├── ValueError                 int("abc"), wrong value (right type)
      ├── TypeError                  "hello" + 5
      ├── AttributeError             obj.no_such_attr
      ├── NameError                  undefined_var
      │    └── UnboundLocalError     used before assignment in scope
      │
      ├── OSError                    I/O errors
      │    ├── FileNotFoundError     open("no.txt")
      │    ├── PermissionError       can't read/write
      │    ├── IsADirectoryError
      │    └── TimeoutError
      │
      ├── RuntimeError
      │    ├── RecursionError         hit sys.getrecursionlimit()
      │    └── NotImplementedError    abstract method not overridden
      │
      ├── StopIteration              iterator exhausted
      ├── GeneratorExit
      ├── MemoryError
      ├── ImportError
      │    └── ModuleNotFoundError   import missing_module
      └── AssertionError             assert condition failed
```

```python
# NEVER do this:
try:
    risky()
except BaseException:   # ← catches SystemExit, KeyboardInterrupt!
    pass                # ← prevents Ctrl+C from working!

# Don't do this either:
try:
    risky()
except Exception:       # ← still too broad for most cases
    pass

# DO this:
try:
    risky()
except (ValueError, TypeError) as e:   # ← specific, intentional
    handle(e)
```

---

## 🔧 Chapter 3 — Full try/except/else/finally Anatomy

```python
try:
    # ── THE TRY BLOCK ────────────────────────────────────────────
    # Code that might raise an exception.
    # Keep it MINIMAL — only the code that can actually fail.
    result = risky_operation()

except ValueError as e:
    # ── EXCEPT BLOCK ─────────────────────────────────────────────
    # Runs ONLY if a ValueError was raised in the try block.
    # `e` is the exception object.
    print(f"Value error: {e}")

except (TypeError, AttributeError) as e:
    # ── MULTIPLE TYPES ────────────────────────────────────────────
    # Catch multiple exception types with a tuple.
    print(f"Type/Attribute error: {e}")

except Exception as e:
    # ── CATCH-ALL (use sparingly) ─────────────────────────────────
    # Catches anything that wasn't caught above.
    # Log it — don't silently swallow.
    import logging
    logging.exception("Unexpected error")
    raise    # ← re-raise! don't hide it.

else:
    # ── ELSE BLOCK ───────────────────────────────────────────────
    # Runs ONLY if the try block succeeded (no exception raised).
    # This is the "success path" — cleaner than putting it in try.
    process(result)

finally:
    # ── FINALLY BLOCK ────────────────────────────────────────────
    # ALWAYS runs — whether exception occurred or not.
    # Use for: closing files, releasing locks, DB connections.
    cleanup()
```

### Why `else` Exists — It Matters

```python
# WITHOUT else — ambiguous:
try:
    data = fetch_data()
    process(data)    # ← if THIS raises ValueError, we catch it — but why?
except ValueError:
    print("something went wrong")

# WITH else — crystal clear:
try:
    data = fetch_data()    # ← only this can raise ValueError
except ValueError:
    print("fetch failed — invalid data format")
else:
    process(data)          # ← only runs if fetch succeeded
```

---

## `finally` Edge Cases — Tricky Behavior

`finally` always runs. But some edge cases surprise even experienced developers.

---

### Edge Case 1: `return` Inside `finally` Swallows Exceptions

```python
def dangerous():
    try:
        raise ValueError("something bad")
    finally:
        return 42   # ← this silently discards the ValueError!

result = dangerous()
print(result)    # 42 — no exception raised, no error, nothing
# The ValueError was SWALLOWED by the return in finally
```

This is a silent bug. Never `return` from `finally` unless you intend to suppress exceptions.

---

### Edge Case 2: `return` in `try` vs `return` in `finally`

```python
def which_return():
    try:
        return "from try"
    finally:
        return "from finally"   # this wins!

print(which_return())   # "from finally"
# finally's return OVERRIDES try's return
```

The `finally` block always executes — even when `try` hits a `return`.
`finally`'s `return` replaces the one from `try`.

---

### Edge Case 3: `continue` and `break` in `finally`

```python
for i in range(3):
    try:
        if i == 1:
            raise ValueError()
    except ValueError:
        print(f"caught at i={i}")
        break               # ← try to break
    finally:
        if i == 1:
            continue        # ← finally's continue OVERRIDES the break!

# Output: caught at i=1
# The loop CONTINUES because finally's continue beats except's break
```

---

### Edge Case 4: `finally` Runs Even with `sys.exit()`

```python
import sys

def cleanup():
    try:
        sys.exit(1)
    finally:
        print("cleanup runs even on sys.exit!")
        # ← this WILL print before the program exits

cleanup()
```

The only way to prevent `finally` from running: `os._exit()` (hard kill, bypasses Python runtime).

---

### The Safe Rule

```
✓ Use finally for: cleanup, closing files, releasing locks — side effects
✗ Avoid in finally: return, raise, break, continue
  → They silently override the exception/flow control from try/except
```

---

## 🔧 Chapter 4 — Handling Exceptions: Patterns and Pitfalls

### Catching the Exception Object

```python
try:
    int("abc")
except ValueError as e:
    print(type(e))          # <class 'ValueError'>
    print(e)                # invalid literal for int() with base 10: 'abc'
    print(e.args)           # ("invalid literal for int() with base 10: 'abc'",)
    print(str(e))           # same as print(e)
    print(repr(e))          # ValueError("invalid literal for int() with base 10: 'abc'")
```

### Catching Multiple Exception Types

```python
# ✅ Tuple syntax — both exceptions share the same handler:
try:
    x = int(input("Enter a number: "))
    result = 10 / x
except (ValueError, ZeroDivisionError) as e:
    print(f"Input error: {e}")

# ✅ Separate handlers — different recovery logic:
try:
    x = int(input("Enter a number: "))
    result = 10 / x
except ValueError:
    print("That's not a valid number.")
except ZeroDivisionError:
    print("Can't divide by zero.")
```

### ⚠️ The Order of Except Clauses Matters

```python
# ❌ WRONG — parent before child catches everything:
try:
    int("abc")
except Exception:           # ← this catches ValueError first!
    print("some error")
except ValueError:          # ← this NEVER runs (dead code)
    print("value error")

# ✅ CORRECT — specific before general:
try:
    int("abc")
except ValueError:          # ← specific first
    print("value error")
except Exception:           # ← generic fallback
    print("some other error")
```

---

## 🔥 Chapter 5 — `raise`: Throwing Exceptions

### Basic raise

```python
def withdraw(balance: float, amount: float) -> float:
    if amount <= 0:
        raise ValueError(f"Amount must be positive, got {amount}")
    if amount > balance:
        raise ValueError(f"Insufficient funds: balance={balance}, requested={amount}")
    return balance - amount
```

### Re-raise the Same Exception

```python
try:
    risky_call()
except ValueError as e:
    logging.error("Validation failed: %s", e)
    raise    # ← re-raises the SAME exception, preserves full traceback
```

### ⭐ Exception Chaining — `raise ... from`

This is one of Python's most underused but critical features.

```python
class DatabaseError(Exception): pass
class ServiceError(Exception): pass

def get_user(user_id: int):
    try:
        return db.query(f"SELECT * FROM users WHERE id = {user_id}")
    except ConnectionError as e:
        # Without from: original traceback LOST
        # raise ServiceError("Database unavailable")

        # With from: PRESERVES original cause — gold for debugging!
        raise ServiceError("Cannot fetch user: database unavailable") from e


# When you call get_user(1) and it fails:
# ServiceError: Cannot fetch user: database unavailable
#
# The above exception was the direct cause of the following exception:
# ← shows ConnectionError's full traceback too!
```

```python
# To suppress the original exception chain (explicit suppression):
raise NewError("context-free message") from None
```

---

## 🏗️ Chapter 6 — Custom Exceptions: Design Like a Pro

### The Basics

```python
# ❌ Don't do this — tells nothing about the domain:
raise Exception("something went wrong with payment")

# ✅ Do this:
class PaymentError(Exception): pass
raise PaymentError("Card declined: insufficient funds")
```

### Full Professional Exception Hierarchy

```python
# ── Base domain exception ──────────────────────────────────────────
class AppError(Exception):
    """Base class for all application-level errors."""

    def __init__(self, message: str, code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.code    = code or "UNKNOWN_ERROR"
        self.details = details or {}

    def __str__(self):
        return f"[{self.code}] {self.message}"

    def to_dict(self) -> dict:
        return {
            "error":   self.code,
            "message": self.message,
            "details": self.details
        }


# ── Domain-specific exceptions ─────────────────────────────────────
class ValidationError(AppError):
    """Input validation failed."""
    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Validation failed on '{field}': {message}",
            code="VALIDATION_ERROR",
            details={"field": field}
        )

class NotFoundError(AppError):
    """Resource not found."""
    def __init__(self, resource: str, resource_id):
        super().__init__(
            message=f"{resource} with id={resource_id} not found",
            code="NOT_FOUND",
            details={"resource": resource, "id": resource_id}
        )

class PaymentError(AppError):
    """Payment processing failed."""
    pass

class InsufficientFundsError(PaymentError):
    """Specific payment failure."""
    def __init__(self, balance: float, required: float):
        super().__init__(
            message=f"Insufficient funds: has {balance}, needs {required}",
            code="INSUFFICIENT_FUNDS",
            details={"balance": balance, "required": required}
        )

class ExternalServiceError(AppError):
    """Third-party API failure."""
    pass


# ── Usage ──────────────────────────────────────────────────────────
def get_product(product_id: int):
    product = db.find(product_id)
    if not product:
        raise NotFoundError("Product", product_id)
    return product

def process_payment(account, amount):
    if account.balance < amount:
        raise InsufficientFundsError(account.balance, amount)
    account.balance -= amount


# ── Handling hierarchy ─────────────────────────────────────────────
try:
    process_payment(account, 500)
except InsufficientFundsError as e:
    print(f"Not enough money: {e.details}")        # specific handling
except PaymentError as e:
    print(f"Payment failed: {e.message}")          # catches all payment errors
except AppError as e:
    print(f"App error: {e.to_dict()}")             # catches all app errors
except Exception as e:
    logging.exception("Unexpected failure")        # unexpected — log + re-raise
    raise
```

---

## 🔒 Chapter 7 — Context Managers: The Right Way to Handle Resources

### The Problem Without Context Managers

```python
# ❌ DANGEROUS — what if an exception happens before file.close()?
file = open("data.txt")
data = file.read()
process(data)        # ← if THIS raises, file.close() never runs → resource leak!
file.close()
```

### [`with` Statement](../12_context_managers/theory.md) — The Solution

```python
# ✅ SAFE — always closes, even if an exception is raised:
with open("data.txt") as file:
    data = file.read()
    process(data)
# file.close() called automatically here, exception or not
```

### How It Works Internally

```python
# with block calls __enter__ and __exit__:
class ManagedResource:
    def __enter__(self):
        print("Acquiring resource")
        return self     # ← this is bound to the `as` variable

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Releasing resource")
        # exc_type, exc_val, exc_tb are None if no exception
        # Return True to SUPPRESS the exception
        # Return False/None to PROPAGATE the exception
        if exc_type is not None:
            print(f"Exception occurred: {exc_val}")
        return False    # ← don't suppress


with ManagedResource() as r:
    print("Using resource")
    raise ValueError("oops")
# Output:
# Acquiring resource
# Using resource
# Releasing resource
# Exception occurred: oops
# ValueError: oops  ← propagated (return False)
```

### `contextlib.contextmanager` — The Easy Way

```python
from contextlib import contextmanager


@contextmanager
def database_transaction(conn):
    """Context manager for DB transactions with auto-rollback."""
    try:
        yield conn                # ← everything in the with block runs here
        conn.commit()             # ← runs after with block if no exception
    except Exception:
        conn.rollback()           # ← runs if exception occurred
        raise                     # ← re-raise after rollback


@contextmanager
def timer(label: str):
    import time
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"{label}: {elapsed:.4f}s")


# Usage:
with database_transaction(conn) as db:
    db.execute("INSERT INTO orders VALUES (...)")
    db.execute("UPDATE inventory SET qty = qty - 1 WHERE id = 5")
    # if anything raises → rollback happens automatically

with timer("Data processing"):
    process_large_dataset()    # Prints: "Data processing: 3.2415s"
```

### Multiple Context Managers

```python
# Python 3.10+ — parenthesized:
with (
    open("input.txt") as infile,
    open("output.txt", "w") as outfile
):
    outfile.write(infile.read())

# Older syntax:
with open("input.txt") as infile, open("output.txt", "w") as outfile:
    outfile.write(infile.read())
```

---

## 🐍 Chapter 8 — LBYL vs EAFP: Python's Philosophy

Two styles of handling potential errors:

```
LBYL — Look Before You Leap      → check BEFORE the operation
EAFP — Easier to Ask Forgiveness → try first, handle failure after
        than Permission
```

```python
# LBYL (more like Java/C):
if key in my_dict:
    value = my_dict[key]
    process(value)

# EAFP (Pythonic):
try:
    value = my_dict[key]
    process(value)
except KeyError:
    handle_missing()
```

```
PREFER LBYL WHEN:
  ✓ Check is cheap and atomic (key in dict, os.path.exists)
  ✓ The "normal" case is often the failing case

PREFER EAFP WHEN:
  ✓ Failure is rare and expensive to pre-check
  ✓ Race conditions exist between check and use
  ✓ Multiple conditions would need checking

EXAMPLE OF RACE CONDITION WITH LBYL:
  if os.path.exists("file.txt"):   ← file exists at this moment
      open("file.txt")             ← but another process deleted it here!
  # EAFP avoids this: just try open(), handle FileNotFoundError
```

---

## 🔄 Chapter 9 — Production Patterns

### Pattern 1 — Retry with Exponential Backoff

For transient failures: network blips, rate limits, temporary DB outages. Uses the [decorator pattern](../10_decorators/theory.md#-chapter-5-functoolswraps--preserving-identity) with `@functools.wraps`.

```python
import time
import random
import functools


def retry(max_attempts=3, exceptions=(Exception,), backoff_factor=2.0, jitter=True):
    """Decorator for automatic retry with exponential backoff."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = 1.0
            last_exc = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exc = e
                    if attempt == max_attempts:
                        break

                    wait = delay + (random.random() if jitter else 0)
                    print(f"Attempt {attempt} failed ({e}). Retrying in {wait:.2f}s...")
                    time.sleep(wait)
                    delay *= backoff_factor

            raise last_exc    # ← all retries exhausted, raise last error

        return wrapper
    return decorator


# Usage:
@retry(max_attempts=3, exceptions=(ConnectionError, TimeoutError), backoff_factor=2.0)
def call_payment_api(payload):
    return requests.post("https://api.stripe.com/v1/charges", data=payload)


# Attempt 1 failed (ConnectionError). Retrying in 1.23s...
# Attempt 2 failed (ConnectionError). Retrying in 2.45s...
# Attempt 3 failed (ConnectionError).
# ConnectionError raised
```

---

### Pattern 2 — Circuit Breaker

When a service is consistently failing, stop hammering it — wait for it to recover.

```python
import time
from enum import Enum


class CircuitState(Enum):
    CLOSED   = "closed"    # normal operation
    OPEN     = "open"      # failing — reject requests immediately
    HALF_OPEN = "half_open" # testing if service recovered


class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout  = recovery_timeout
        self.failure_count     = 0
        self.last_failure_time = None
        self.state             = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                print("Circuit half-open — testing recovery")
            else:
                raise RuntimeError("Circuit is OPEN — service unavailable")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count  += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print(f"Circuit OPEN after {self.failure_count} failures")


breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=10)

def fetch_user(user_id):
    return breaker.call(requests.get, f"https://api.service.com/users/{user_id}")
```

---

### Pattern 3 — Graceful Degradation

When a non-critical feature fails, keep the core service running.

```python
def get_product_page(product_id: int) -> dict:
    product = product_service.get(product_id)   # critical — must work

    # Non-critical: personalized recommendations
    try:
        recommendations = recommendation_engine.get(product_id)
    except Exception:
        logging.warning("Recommendation service unavailable", exc_info=True)
        recommendations = []    # ← fallback: empty list, not crash

    # Non-critical: pricing analytics
    try:
        price_history = analytics.get_price_history(product_id)
    except Exception:
        logging.warning("Analytics service unavailable", exc_info=True)
        price_history = None    # ← fallback: no chart, not crash

    return {
        "product":          product,
        "recommendations":  recommendations,
        "price_history":    price_history,
    }
```

---

### Pattern 4 — Exception Translation (Layered Architecture)

Translate low-level exceptions into domain exceptions at layer boundaries.

```python
# ── Repository Layer ─────────────────────────────────────
class UserRepository:
    def find(self, user_id: int) -> User:
        try:
            return self._db.query("SELECT * FROM users WHERE id=?", user_id)
        except psycopg2.OperationalError as e:
            raise DatabaseUnavailableError("Cannot reach database") from e
        except psycopg2.ProgrammingError as e:
            raise DataIntegrityError(f"Query error: {e}") from e


# ── Service Layer ─────────────────────────────────────────
class UserService:
    def get_user(self, user_id: int) -> User:
        try:
            user = self.repo.find(user_id)
        except DatabaseUnavailableError:
            raise ServiceUnavailableError("User service temporarily down") from None

        if not user:
            raise UserNotFoundError(user_id)
        return user


# ── API Layer ──────────────────────────────────────────────
@app.route("/users/<int:user_id>")
def get_user_endpoint(user_id: int):
    try:
        user = user_service.get_user(user_id)
        return jsonify(user.to_dict())
    except UserNotFoundError:
        return jsonify({"error": "User not found"}), 404
    except ServiceUnavailableError:
        return jsonify({"error": "Service temporarily unavailable"}), 503
    except Exception:
        logging.exception("Unexpected error in GET /users/%s", user_id)
        return jsonify({"error": "Internal server error"}), 500
        # ← NEVER expose the real exception to the client!
```

---

## 📋 Chapter 10 — Logging Exceptions Correctly

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── logging.exception() ──────────────────────────────────
# Use INSIDE an except block.
# Automatically includes the full traceback.
try:
    risky()
except ValueError as e:
    logger.exception("Validation failed")    # logs ERROR + full traceback
    # equivalent to:
    # logger.error("Validation failed", exc_info=True)


# ── logging.error() with exc_info ────────────────────────
try:
    risky()
except Exception as e:
    logger.error("Something failed: %s", e, exc_info=True)


# ── Log + re-raise ────────────────────────────────────────
try:
    risky()
except Exception:
    logger.exception("Unexpected failure — re-raising")
    raise    # ← preserves original exception AND logs it


# ── DON'T do this ─────────────────────────────────────────
try:
    risky()
except Exception as e:
    print(f"Error: {e}")    # ← lost in stdout, no traceback, not searchable
    pass                    # ← NEVER silently ignore exceptions
```

---

## ⚠️ Chapter 11 — Anti-Patterns (Don't Do These)

### ❌ Anti-Pattern 1 — Bare `except` / Silent `pass`

```python
# WORST possible code:
try:
    do_something()
except:          # catches SystemExit, KeyboardInterrupt, everything!
    pass         # hides every error silently — debugging nightmare
```

### ❌ Anti-Pattern 2 — Catching Too Broadly

```python
# BAD — which exception are you actually expecting?
try:
    user = get_user(id)
    order = create_order(user)
    send_email(user, order)
except Exception as e:
    print("Error")   # you have no idea which of the 3 lines failed!
```

### ❌ Anti-Pattern 3 — Using Exceptions for Normal Control Flow

```python
# BAD — exceptions are expensive:
for item in large_list:
    try:
        result = process(item)
    except KeyError:
        result = default_value   # using exception as an if/else

# GOOD — check first:
for item in large_list:
    result = item.get("key", default_value)
```

### ❌ Anti-Pattern 4 — Losing the Original Exception

```python
# BAD — original cause lost:
try:
    db.connect()
except ConnectionError:
    raise RuntimeError("Service failed")   # ← ConnectionError traceback gone!

# GOOD — chain it:
try:
    db.connect()
except ConnectionError as e:
    raise RuntimeError("Service failed") from e   # ← full chain preserved
```

### ❌ Anti-Pattern 5 — `except Exception` Without Re-raise

```python
# BAD — you caught it but gave no information:
try:
    fetch_data()
except Exception as e:
    logger.error("Error!")   # ← no traceback logged, no re-raise
    return None              # ← caller has no idea what failed

# GOOD:
try:
    fetch_data()
except Exception:
    logger.exception("fetch_data failed")   # ← logs traceback
    raise                                    # ← OR return default AND document why
```

---

## 🧵 Chapter 12 — Exceptions in Threads and Async

### Threads — Exceptions Are Silently Lost!

```python
import threading   # → [13_concurrency](../13_concurrency/theory.md) for full threading guide

def worker():
    raise ValueError("Something went wrong in thread!")

t = threading.Thread(target=worker)
t.start()
t.join()
# The ValueError is printed to stderr but your main thread doesn't know!

# FIX — capture in the thread:
result = {"error": None, "value": None}

def safe_worker():
    try:
        result["value"] = risky_work()
    except Exception as e:
        result["error"] = e

t = threading.Thread(target=safe_worker)
t.start()
t.join()

if result["error"]:
    raise result["error"]   # propagate to main thread
```

### `concurrent.futures` — The Better Way

```python
from concurrent.futures import ThreadPoolExecutor, as_completed


def risky_task(n):
    if n == 3:
        raise ValueError(f"Task {n} failed!")
    return n * 2


with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {executor.submit(risky_task, i): i for i in range(6)}

    for future in as_completed(futures):
        n = futures[future]
        try:
            result = future.result()    # ← re-raises the exception here!
            print(f"Task {n}: {result}")
        except ValueError as e:
            print(f"Task {n} raised: {e}")
```

### Async — [`asyncio`](../13_concurrency/theory.md)

```python
import asyncio


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise ValueError(f"Bad status: {response.status}")
            return await response.json()


async def main():
    try:
        data = await fetch("https://api.example.com/data")
    except ValueError as e:
        print(f"Fetch failed: {e}")
    except aiohttp.ClientConnectionError as e:
        print(f"Connection error: {e}")


# Gather with exception handling:
results = await asyncio.gather(
    fetch("url1"),
    fetch("url2"),
    return_exceptions=True    # ← don't cancel other tasks on failure
)
for r in results:
    if isinstance(r, Exception):
        print(f"Failed: {r}")
    else:
        process(r)
```

---

## 🎯 Chapter 13 — Reading Tracebacks Like a Pro

```
Traceback (most recent call last):     ← read from BOTTOM up for root cause
  File "app.py", line 42, in main      ← outermost call
    run_payment(order_id=123)
  File "payment.py", line 15, in run_payment
    result = gateway.charge(order)
  File "gateway.py", line 8, in charge
    return self._client.post(data)     ← innermost call (root cause here)
ConnectionError: Failed to connect     ← THE ACTUAL ERROR


CHAINED EXCEPTION:
  During handling of the above exception, another exception occurred:

  File "service.py", line 31, in process
    raise ServiceError("Payment unavailable") from conn_error
ServiceError: Payment unavailable     ← this is what YOUR code raised
```

```
READING STRATEGY:
  1. Bottom line = the exception type + message (what crashed)
  2. The line just above = where in YOUR code it happened
  3. "The above exception was the direct cause of..." = chained exception
  4. Top of traceback = the entry point (where the call chain started)
```

---

## Exception Propagation — How Exceptions Travel Up the Call Stack

When an exception is raised, Python unwinds the call stack frame by frame, looking for a handler (`try/except`). If none is found, the program crashes with a traceback.

```
def level3():
    raise ValueError("something went wrong")   # ← exception born here

def level2():
    level3()    # no try/except — exception propagates UP

def level1():
    level2()    # no try/except — exception propagates UP

def main():
    try:
        level1()           # ← exception caught here
    except ValueError as e:
        print(f"Caught: {e}")

main()
```

Stack unwinding visualization:

```
CALL STACK (before exception):

  ┌──────────────────────────────────────────────┐  ← top
  │  level3() frame                              │
  │    raise ValueError("something went wrong")  │
  │    → EXCEPTION BORN HERE                    │
  ├──────────────────────────────────────────────┤
  │  level2() frame                              │
  │    no try/except → PROPAGATES UP            │
  ├──────────────────────────────────────────────┤
  │  level1() frame                              │
  │    no try/except → PROPAGATES UP            │
  ├──────────────────────────────────────────────┤
  │  main() frame                                │
  │    try: level1()  ← HANDLER FOUND HERE      │
  │    except ValueError → CAUGHT               │
  └──────────────────────────────────────────────┘

UNWINDING ORDER:
  1. level3() frame destroyed  (no handler)
  2. level2() frame destroyed  (no handler)
  3. level1() frame destroyed  (no handler)
  4. main() try/except catches it ✓
```

Each frame is **destroyed** as the exception propagates through it (unless that frame has a `try/except` that catches it). If the exception reaches the bottom of the stack without being caught, Python prints the traceback and exits.

**What the traceback shows:**

The traceback is the unwind path in reverse — bottom (closest to the error) to top (entry point). That's why you read tracebacks from bottom to top.

```
Traceback (most recent call last):    ← this means BOTTOM is most recent
  File "app.py", line 15, in main     ← outermost (first call, farthest from error)
    level1()
  File "app.py", line 10, in level1
    level2()
  File "app.py", line 6, in level2
    level3()
  File "app.py", line 2, in level3
    raise ValueError("something went wrong")   ← innermost (closest to error)
ValueError: something went wrong
```

---

## ⚠️ `warnings` Module — Non-Fatal Alerts

Exceptions stop execution. But sometimes you want to **alert** the caller about a problem without crashing — a deprecated API, a performance issue, an unusual input.

That's what `warnings` is for.

```python
import warnings

# Issue a warning (does not raise, does not stop):
warnings.warn("This function is deprecated", DeprecationWarning)

# Warning categories:
warnings.warn("Low disk space", ResourceWarning)
warnings.warn("Result may be inaccurate", UserWarning)
warnings.warn("Internal change ahead", FutureWarning)
```

**Warning categories:**

```
UserWarning        — general purpose (default when no category given)
DeprecationWarning — API is deprecated (shown in dev, hidden in prod)
FutureWarning      — behavior will change in a future version
RuntimeWarning     — suspicious runtime behavior
ResourceWarning    — resource usage issues (file not closed, etc.)
SyntaxWarning      — dubious syntax
```

**Filtering warnings — control what gets shown:**

```python
import warnings

# Suppress all deprecation warnings:
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Turn warnings into errors (great for CI/CD):
warnings.filterwarnings("error", category=DeprecationWarning)
# Now DeprecationWarning raises an exception

# Show each unique warning only once:
warnings.filterwarnings("once")
```

**Practical use — deprecating your own functions:**

```python
import warnings

def old_function(x):
    warnings.warn(
        "old_function() is deprecated. Use new_function() instead.",
        DeprecationWarning,
        stacklevel=2   # ← points warning to CALLER, not here
    )
    return new_function(x)
```

`stacklevel=2` is important — it makes the warning point to the caller's line, not inside your function.

**Testing warnings:**

```python
import warnings
import pytest

def test_deprecation_warning():
    with pytest.warns(DeprecationWarning, match="deprecated"):
        old_function(42)
```

---

## 🎯 Key Takeaways

```
• Exceptions are OBJECTS — instances of exception classes, not just messages
• Exception hierarchy: BaseException → Exception → specific types
• Never catch BaseException or bare except — you'll swallow Ctrl+C, sys.exit()
• Keep try blocks MINIMAL — only the line that can actually fail
• else block = success path (runs only if no exception)
• finally block = always runs — guaranteed cleanup
• raise from e — chains exceptions, preserves root cause for debugging
• raise (no args) — re-raises current exception with original traceback
• Custom exception hierarchy = domain clarity + better debugging
• Context managers (with) — the right way to handle resources
• EAFP is Pythonic — try first, handle failure (vs LBYL: check first)
• Production patterns: retry, circuit breaker, graceful degradation
• Layer exceptions: translate low-level errors at architectural boundaries
• Always log exceptions: logging.exception() inside except block
• NEVER silently pass exceptions — a hidden bug is worse than a crash
• Exceptions in threads are silently lost — use concurrent.futures instead
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [05 — OOP](../05_oops/README.md) |
| 📖 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ➡️ Next | [07 — Modules & Packages](../07_modules_packages/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Oops — Interview Q&A](../05_oops/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
