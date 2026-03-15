# 🎯 Exceptions & Error Handling — Interview Questions

> *"Exception handling questions are reliability tests.*
> *They reveal whether you think about systems that survive the real world."*

---

## 📊 Question Map

```
LEVEL 1 — Junior (0–2 years)
  • Basic try/except syntax
  • Exception hierarchy
  • finally vs except
  • Common exceptions

LEVEL 2 — Mid-Level (2–5 years)
  • Exception propagation
  • Exception chaining (raise from)
  • Custom exception design
  • Context managers
  • LBYL vs EAFP

LEVEL 3 — Senior (5+ years)
  • Production patterns (retry, circuit breaker)
  • Exception architecture in layered systems
  • Logging strategy
  • Async/threading exceptions
  • API design with exceptions
```

---

## 🟢 Level 1 — Junior Questions

---

### Q1: What is an exception in Python? How is it different from a syntax error?

**Weak answer:** "Exception is when code breaks."

**Strong answer:**

> An **exception** is an object — an instance of an exception class — that represents an error condition detected at **runtime**. When one is raised, normal execution stops and Python walks up the call stack looking for a handler.
>
> A **SyntaxError** is detected before execution even starts, during the parsing phase. It can never be caught with `try/except`.

```python
# SyntaxError — detected before runtime, cannot be caught:
if True       # ← missing colon: SyntaxError before program runs

# RuntimeError/Exception — detected during execution, CAN be caught:
int("abc")    # ← ValueError at runtime → catchable
```

---

### Q2: What is the full structure of a try block? What does each part do?

**Strong answer:**

```python
try:
    result = risky_operation()     # code that might fail

except ValueError as e:            # runs if ValueError raised
    handle_value_error(e)

except (TypeError, AttributeError):  # catches either type
    handle_type_issues()

else:
    use(result)        # runs ONLY if NO exception was raised in try

finally:
    cleanup()          # ALWAYS runs — exception or not

# Key insight: else separates "success logic" from "error recovery"
# Key insight: finally is for guaranteed resource release
```

---

### Q3: What is `finally` and why is it critical?

**Weak answer:** "It always runs."

**Strong answer:**

> `finally` is the cleanup guarantee. It runs whether the try block succeeded, raised an exception, or even hit a `return` or `break` statement.

```python
def read_config(path):
    file = open(path)     # what if we return early below?
    try:
        data = file.read()
        if not data:
            return {}      # ← without finally, file never closed!
        return parse(data)
    finally:
        file.close()       # ← always runs, even if we return early

# Better modern style — context manager handles this automatically:
def read_config(path):
    with open(path) as file:
        data = file.read()
        return parse(data) if data else {}
```

---

### Q4: Why should you never use a bare `except:`?

**Strong answer:**

> A bare `except:` catches **BaseException** — which includes `SystemExit` (from `sys.exit()`), `KeyboardInterrupt` (Ctrl+C), and `GeneratorExit`. This prevents the user from stopping the program with Ctrl+C and can silently swallow critical errors.

```python
# ❌ DANGEROUS:
try:
    process()
except:              # catches EVERYTHING including Ctrl+C
    pass             # error silently disappears

# ❌ Still too broad:
try:
    process()
except Exception:    # at least doesn't swallow SystemExit/KeyboardInterrupt
    pass             # but still hides bugs

# ✅ Specific and intentional:
try:
    value = int(user_input)
except ValueError:
    print("Please enter a valid number")
```

---

### Q5: Name 8 common built-in exceptions and when each occurs.

```python
# ValueError    — right type, wrong value:
int("abc")            # ValueError: invalid literal
range(-1)             # ValueError: step argument must not be zero

# TypeError     — wrong type:
"hello" + 5           # TypeError: can only concatenate str (not "int") to str
len(42)               # TypeError: object of type 'int' has no len()

# KeyError      — dict key doesn't exist:
{}["missing"]         # KeyError: 'missing'

# IndexError    — list index out of range:
[1, 2, 3][9]          # IndexError: list index out of range

# AttributeError — attribute doesn't exist:
None.strip()          # AttributeError: 'NoneType' object has no attribute 'strip'

# NameError     — variable not defined:
print(undefined_var)  # NameError: name 'undefined_var' is not defined

# FileNotFoundError — file doesn't exist:
open("ghost.txt")     # FileNotFoundError: No such file or directory

# ZeroDivisionError — divide by zero:
10 / 0                # ZeroDivisionError: division by zero
```

---

## 🔵 Level 2 — Mid-Level Questions

---

### Q6: What is exception propagation? How does the call stack affect it?

**Strong answer:**

> When an exception is raised and NOT caught in the current function, it **propagates** — travels up the call stack to the caller. This continues until a handler is found or the program crashes.

```python
def level3():
    return 10 / 0           # ZeroDivisionError raised here

def level2():
    return level3()         # no handler — propagates up

def level1():
    return level2()         # no handler — propagates up

try:
    level1()                # caught here
except ZeroDivisionError:
    print("Caught at top level")

# IMPORTANT for architecture: don't catch too early (hides problems)
# and don't catch too late (coarse error handling).
# Catch at the layer that can meaningfully handle the error.
```

---

### Q7: What is exception chaining? Why does `raise X from Y` matter?

**Weak answer:** "It re-raises with a message."

**Strong answer:**

> Exception chaining preserves the **root cause** of an error while wrapping it in a higher-level exception. This is critical for debugging — without it, you lose the original traceback.

```python
# WITHOUT chaining — root cause lost:
try:
    connect_db()
except ConnectionError:
    raise ServiceError("DB unavailable")   # ← ConnectionError traceback GONE

# WITH chaining — full context preserved:
try:
    connect_db()
except ConnectionError as e:
    raise ServiceError("DB unavailable") from e
# Output shows BOTH: ServiceError AND the original ConnectionError that caused it

# TO SUPPRESS the chain (explicit intention):
raise ServiceError("DB unavailable") from None
# Output: only ServiceError — says "I intentionally suppressed the cause"
```

---

### Q8: How would you design a custom exception hierarchy for a domain?

**Strong answer:**

> I'd create a base exception for the domain, then sub-exceptions for categories, then specific exceptions for concrete failures. This lets callers choose how broadly to catch.

```python
class PaymentError(Exception):
    """Base for all payment domain errors."""
    pass

class CardError(PaymentError):
    """Card-related failures."""
    pass

class InsufficientFundsError(CardError):
    def __init__(self, balance, required):
        super().__init__(f"Balance {balance} < required {required}")
        self.balance  = balance
        self.required = required

class CardExpiredError(CardError):
    pass

class GatewayError(PaymentError):
    """Third-party gateway failures."""
    pass

# Caller flexibility:
try:
    process_payment()
except InsufficientFundsError as e:
    prompt_top_up(e.balance, e.required)   # very specific handling
except CardError:
    ask_for_new_card()                     # all card errors
except PaymentError:
    show_generic_payment_failure()         # all payment errors
```

---

### Q9: What is a context manager and how does it relate to exception handling?

**Strong answer:**

> A context manager is a class (or function) that wraps a block of code with setup and teardown logic, guaranteeing cleanup even if an exception occurs. It's the Pythonic replacement for `try/finally` blocks for resource management.

```python
# Behind the scenes, with open(...) does this:
# __enter__: opens file, returns file object
# __exit__:  closes file regardless of exception

# Custom context manager using contextlib:
from contextlib import contextmanager

@contextmanager
def managed_db_connection(url):
    conn = create_connection(url)
    try:
        yield conn              # everything inside 'with' block runs here
        conn.commit()
    except Exception:
        conn.rollback()         # ← guaranteed on any exception
        raise
    finally:
        conn.close()            # ← guaranteed always

with managed_db_connection("postgres://localhost/mydb") as conn:
    conn.execute("INSERT INTO orders VALUES (...)")
    # If anything raises here → rollback + close happens automatically
```

---

### Q10: What is LBYL vs EAFP? Which is more Pythonic?

**Strong answer:**

> LBYL (Look Before You Leap) checks conditions before performing an operation. EAFP (Easier to Ask Forgiveness than Permission) tries the operation and handles failures.
>
> Python generally favors **EAFP** because:
> 1. It avoids race conditions (between check and operation)
> 2. It's often faster for the "happy path"
> 3. It's cleaner for duck typing

```python
# LBYL:
if "key" in data:
    value = data["key"]
    process(value)

# EAFP (Pythonic):
try:
    process(data["key"])
except KeyError:
    handle_missing()

# RACE CONDITION EXAMPLE — LBYL loses:
if os.path.exists("file.txt"):     # file exists NOW
    open("file.txt")               # file DELETED by another process here → crash!
# EAFP wins: just open(), catch FileNotFoundError
```

---

### Q11: What's the difference between `raise` and `raise e`?

**Strong answer — this is a common trap:**

```python
try:
    risky()
except Exception as e:
    raise       # ← re-raises ORIGINAL exception with ORIGINAL traceback

try:
    risky()
except Exception as e:
    raise e     # ← creates a NEW exception object, LOSES the original traceback
                # The traceback will point to THIS line, not where it actually happened!

# ALWAYS use bare raise inside except blocks when re-raising.
```

---

## 🔴 Level 3 — Senior Questions

---

### Q12: How do you design exception handling in a layered architecture?

**Strong answer:**

> In a layered architecture (Repository → Service → API), exceptions should be translated at each layer boundary:

```
Repository Layer:   catches psycopg2.OperationalError
                    raises DatabaseError (domain exception)
                    reason: hides infrastructure details from service

Service Layer:      catches DatabaseError
                    raises ServiceUnavailableError
                    reason: hides internal database knowledge from API

API Layer:          catches domain exceptions
                    returns HTTP status codes (404, 503, 500)
                    reason: translates domain to HTTP protocol
                    NEVER exposes internal stack traces to clients!
```

```python
# API layer — always sanitize outbound errors:
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, NotFoundError):
        return {"error": "Resource not found"}, 404
    if isinstance(e, ServiceUnavailableError):
        return {"error": "Service temporarily unavailable"}, 503

    # Unexpected — log full details internally, return generic response:
    logger.exception("Unhandled exception")
    return {"error": "Internal server error"}, 500
    # ← NEVER return str(e) or traceback to the client!
```

---

### Q13: How would you implement a retry mechanism for an unreliable service?

**Strong answer:**

```python
import time, random, functools

def retry(max_attempts=3, exceptions=(Exception,), backoff_factor=2.0, jitter=True):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay, last_exc = 1.0, None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt == max_attempts:
                        break
                    wait = delay * (1 + random.random() * 0.1 if jitter else 1)
                    time.sleep(wait)
                    delay *= backoff_factor
            raise last_exc
        return wrapper
    return decorator

@retry(max_attempts=3, exceptions=(ConnectionError, TimeoutError))
def call_api(payload): ...
```

> Key points to mention:
> - **Exponential backoff** — prevents hammering a struggling service
> - **Jitter** — randomizes wait to avoid thundering herd
> - Only retry **transient** exceptions (ConnectionError, TimeoutError) — not ValueError
> - **Max attempts** — don't retry forever

---

### Q14: How do exceptions work in threads? What's the danger?

**Strong answer:**

> Exceptions raised inside a thread are NOT propagated to the main thread automatically. They print to stderr but the main thread continues unaware of the failure.

```python
import threading

def dangerous_worker():
    raise ValueError("Thread failed!")   # ← printed to stderr, main thread unaware

t = threading.Thread(target=dangerous_worker)
t.start()
t.join()
# Main thread continues! The ValueError is silently dropped.

# SOLUTION: use concurrent.futures which properly propagates:
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor() as executor:
    future = executor.submit(dangerous_worker)
    try:
        future.result()   # ← this RE-RAISES the thread's exception here!
    except ValueError as e:
        print(f"Worker failed: {e}")
```

---

### Q15: How would you log exceptions correctly in production?

**Strong answer:**

```python
import logging
logger = logging.getLogger(__name__)

# ✅ logging.exception() — use inside except block:
# automatically includes the full traceback
try:
    risky()
except Exception:
    logger.exception("Unexpected failure in risky()")
    raise   # or handle

# ✅ Structured logging with context:
try:
    process_order(order_id)
except PaymentError as e:
    logger.error(
        "Payment failed",
        extra={
            "order_id": order_id,
            "error_code": e.code,
            "user_id": current_user.id,
        }
    )

# ❌ NEVER:
except Exception as e:
    print(e)       # lost in stdout, no traceback, no searchability
    pass           # silently swallowed
    return None    # caller has no idea what failed
```

---

### Q16: What's the difference between `logging.error()` and `logging.exception()`?

```python
try:
    risky()
except Exception as e:
    logging.error("Failed: %s", e)         # logs ERROR level, message only
                                           # NO traceback included!

    logging.exception("Failed")            # logs ERROR level + FULL traceback
                                           # equivalent to:
                                           # logging.error("Failed", exc_info=True)

    logging.warning("Failed: %s", e)       # logs WARNING level, message only
    logging.critical("Failed", exc_info=True)  # CRITICAL level + traceback

# Rule: inside except blocks, always use logging.exception()
# so the full traceback is captured for debugging.
```

---

## ⚠️ Trap Questions

---

### Trap 1 — The `else` Misunderstanding

```python
try:
    result = int("42")
except ValueError:
    print("failed")
else:
    print("success")    # This prints "success"
    result = result + 1

# QUESTION: When does else run?
# ANSWER: ONLY when NO exception was raised in try.
# It does NOT run if the except block ran.
# Purpose: separate "things that must not fail" (try)
# from "things to do on success" (else) clearly.
```

---

### Trap 2 — `raise e` vs `raise`

```python
try:
    risky()
except Exception as e:
    raise e     # ← WRONG: creates new exception, traceback points to HERE
                # you lose information about WHERE the original error happened

try:
    risky()
except Exception as e:
    raise       # ← CORRECT: re-raises original with FULL original traceback
```

---

### Trap 3 — `finally` With a `return`

```python
def tricky():
    try:
        return "try"
    finally:
        return "finally"    # ← finally's return OVERRIDES try's return!

print(tricky())    # "finally" — NOT "try"!

# This is a well-known Python gotcha.
# Avoid return/break/continue inside finally blocks.
```

---

### Trap 4 — Catching Too Broadly Hides Bugs

```python
# This code has a bug — can you spot it?
class User:
    pass

try:
    user = User()
    user.send_welcome_email()   # ← AttributeError: User has no send_welcome_email!
except Exception:
    pass                        # ← BUG HIDDEN! Looks like it works, email never sent.

# The fix is not just narrowing the except — it's being precise about
# WHICH operation you expect to fail AND what exception it raises.
```

---

### Trap 5 — Exception Object Cleared After `except` Block

```python
try:
    risky()
except ValueError as e:
    err = e     # capture it if you need it later

# After the except block, `e` is deleted by Python:
print(e)    # NameError! `e` no longer exists after except block

# Why? Python deletes the loop variable to break reference cycles
# (exception objects hold tracebacks, tracebacks hold frames, frames hold locals)

# Solution: assign to another name inside the except block:
try:
    risky()
except ValueError as e:
    captured = e    # ← save before block ends

print(captured)    # ✓ works
```

---

## 🔥 Rapid-Fire Revision

```
Q: What is exception propagation?
A: Unhandled exception travels up the call stack until caught or program crashes.

Q: What does `raise` (no args) do?
A: Re-raises the current active exception with its original traceback. NEVER use `raise e`.

Q: What is the purpose of `raise X from Y`?
A: Chains exceptions. Y is the "cause" — shown in traceback. Preserves debugging context.

Q: What does `raise X from None` do?
A: Creates new exception but explicitly suppresses the cause chain.

Q: What's wrong with `except Exception: pass`?
A: Silently swallows ALL errors including legitimate bugs. Debugging nightmare.

Q: What's the difference between `finally` and `__exit__`?
A: finally is syntax; __exit__ is the context manager protocol method.
   Both guarantee cleanup. `with` statement calls __exit__ automatically.

Q: Can you have try/finally without except?
A: Yes! Very common: ensure cleanup without catching exceptions.

Q: What exception does `with open("missing.txt")` raise?
A: FileNotFoundError (subclass of OSError).

Q: What's the BaseException hierarchy?
A: BaseException → Exception → most errors.
   BaseException also has: SystemExit, KeyboardInterrupt, GeneratorExit.

Q: What is EAFP?
A: "Easier to Ask Forgiveness than Permission" — Python's idiomatic style:
   try the operation, catch exceptions, rather than pre-checking conditions.

Q: What happens to exceptions in threads?
A: Printed to stderr but NOT propagated to main thread. Use concurrent.futures
   to get exception re-raising via future.result().

Q: How do you log an exception with full traceback?
A: logger.exception("message") inside an except block.
   Equivalent to logger.error("message", exc_info=True).

Q: What does the `else` in try/except/else do?
A: Runs only if the try block completed without raising any exception.
   Separates success logic from error handling.

Q: What is the traceback reading order?
A: Bottom to top for root cause. The LAST entry is where the error originated.
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🏠 Home | [python-complete-mastery](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Modules Packages — Theory →](../07_modules_packages/theory.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md)
