<a id="top"></a>
# 🛑 06 — Exceptions & Error Handling

> *"Writing code that works when everything goes right is easy.*
> *Writing code that survives when everything goes wrong — that's engineering."*

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

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. What Actually Happens When Python Raises an Exception](#1-what-actually-happens-when-python-raises-an-exception)
- [2. The Exception Hierarchy](#2-the-exception-hierarchy)
- [3. Full try/except/else/finally Anatomy](#3-full-tryexceptelsefinally-anatomy)
  - [Why else Exists](#why-else-exists)
  - [finally Edge Cases — Tricky Behavior](#finally-edge-cases)
- [4. Handling Exceptions: Patterns and Pitfalls](#4-handling-exceptions-patterns-and-pitfalls)
  - [Catching the Exception Object](#catching-the-exception-object)
  - [Catching Multiple Exception Types](#catching-multiple-exception-types)
- [5. raise: Throwing Exceptions](#5-raise-throwing-exceptions)
  - [Exception Chaining — raise ... from](#exception-chaining)
- [6. Custom Exceptions: Design Like a Pro](#6-custom-exceptions-design-like-a-pro)
  - [Full Professional Exception Hierarchy](#full-professional-exception-hierarchy)
- [7. Context Managers: The Right Way to Handle Resources](#7-context-managers-the-right-way-to-handle-resources)
  - [with Statement — The Solution](#with-statement)
  - [How It Works Internally](#how-it-works-internally)
  - [contextlib.contextmanager — The Easy Way](#contextlib-contextmanager)
  - [Multiple Context Managers](#multiple-context-managers)
- [8. LBYL vs EAFP: Python's Philosophy](#8-lbyl-vs-eafp-pythons-philosophy)
- [9. Retry & Exponential Backoff — The Full Picture](#9-retry-exponential-backoff)
  - [The Math](#the-math)
  - [Why Jitter Matters — The Thundering Herd Problem](#why-jitter-matters)
  - [Hand-Rolled Implementation](#hand-rolled-implementation)
  - [Production Approach — tenacity](#production-approach-tenacity)
  - [Async Version](#async-version)
  - [When NOT to Retry](#when-not-to-retry)
- [10. Production Patterns](#10-production-patterns)
  - [Pattern 1 — Retry with Exponential Backoff](#pattern-1-retry)
  - [Pattern 2 — Circuit Breaker](#pattern-2-circuit-breaker)
  - [Pattern 3 — Graceful Degradation](#pattern-3-graceful-degradation)
  - [Pattern 4 — Exception Translation](#pattern-4-exception-translation)
- [11. Logging Exceptions Correctly](#11-logging-exceptions-correctly)
- [12. Anti-Patterns (Don't Do These)](#12-anti-patterns)
  - [Anti-Pattern 1 — Bare except / Silent pass](#anti-pattern-1)
  - [Anti-Pattern 2 — Catching Too Broadly](#anti-pattern-2)
  - [Anti-Pattern 3 — Exceptions for Control Flow](#anti-pattern-3)
  - [Anti-Pattern 4 — Losing the Original Exception](#anti-pattern-4)
  - [Anti-Pattern 5 — except Exception Without Re-raise](#anti-pattern-5)
- [13. Exceptions in Threads and Async](#13-exceptions-in-threads-and-async)
  - [Threads — Exceptions Are Silently Lost!](#threads-exceptions-silently-lost)
  - [concurrent.futures — The Better Way](#concurrent-futures)
  - [Async — asyncio](#async-asyncio)
- [14. Reading Tracebacks Like a Pro](#14-reading-tracebacks-like-a-pro)
  - [Exception Propagation — How Exceptions Travel Up the Call Stack](#exception-propagation)
- [15. warnings Module — Non-Fatal Alerts](#15-warnings-module)
- [🎯 Key Takeaways](#key-takeaways)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`try`/`except`/`finally` · Specific exception types · `raise` · Custom exceptions · Context managers for cleanup

**Should Learn** — Important for real projects, comes up regularly:
`raise X from Y` / `raise X from None` · Exception hierarchy · `else` clause on try · Retry patterns

**Good to Know** — Useful in specific situations:
`warnings` module · `sys.exc_info()` · `atexit` module

**Reference** — Know it exists, look up when needed:
`ExceptionGroup` (Python 3.11+) · Signal handlers · `warnings.filterwarnings`

> 📝 **Practice:** [Q1 — Trace exception propagation](./practice.md#q1--call-stack--trace-exception-propagation-through-3-nested-calls)

<a id="1-what-actually-happens-when-python-raises-an-exception"></a>
# 1. What Actually Happens When Python Raises an Exception

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

> 📝 **Practice:** [Q7 — Exception hierarchy matching](./practice.md#q7--exception-hierarchy--which-except-clause-catches-what) · [Deep dive →](./01_exception_mechanics/theory.md)

> [↑ Back to Top](#top)

<a id="2-the-exception-hierarchy"></a>
# 2. The Exception Hierarchy

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

> 📝 **Practice:** [Q2 — Full try/except anatomy](./practice.md#q2--tryexceptelsefinally--write-the-full-four-block-pattern) · [Q3 — When does else run?](./practice.md#q3--else-clause--when-does-it-run)

> [↑ Back to Top](#top)

<a id="3-full-tryexceptelsefinally-anatomy"></a>
# 3. Full try/except/else/finally Anatomy

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

> 📝 **Practice:** [Q19 · try-except-finally](../python_practice_questions_100.md#q19--normal--try-except-finally)

<a id="why-else-exists"></a>
## Why else Exists

The `else` clause runs only when no exception was raised in the `try` block. It exists to separate "the code that might fail" from "the code that should run on success" — making it clear which line you're actually guarding against.

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

<a id="finally-edge-cases"></a>
## finally Edge Cases — Tricky Behavior

`finally` always runs. But some edge cases surprise even experienced developers.

**Edge Case 1: `return` Inside `finally` Swallows Exceptions**

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

**Edge Case 2: `return` in `try` vs `return` in `finally`**

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

**Edge Case 3: `continue` and `break` in `finally`**

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

**Edge Case 4: `finally` Runs Even with `sys.exit()`**

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

**The Safe Rule**

```
✓ Use finally for: cleanup, closing files, releasing locks — side effects
✗ Avoid in finally: return, raise, break, continue
  → They silently override the exception/flow control from try/except
```

> 📝 **Practice:** [Q5 — Catch specific types](./practice.md#q5--specific-exception-types--catch-each-with-different-messages) · [Q8 — Tuple syntax](./practice.md#q8--tuple-catch-syntax--multiple-exceptions-one-handler) · [Q9 — Order bug](./practice.md#q9--except-order-bug--broad-before-specific)

> [↑ Back to Top](#top)

<a id="4-handling-exceptions-patterns-and-pitfalls"></a>
# 4. Handling Exceptions: Patterns and Pitfalls

<a id="catching-the-exception-object"></a>
## Catching the Exception Object

The `as e` syntax binds the raised exception instance to a variable, letting you inspect its type, message, and args. This is how you get diagnostic detail — not just "something failed" but exactly what and why.

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

<a id="catching-multiple-exception-types"></a>
## Catching Multiple Exception Types

There are two patterns: a tuple in a single `except` clause when both exceptions share the same recovery logic, and separate `except` clauses when each needs different handling. Use whichever makes the intent clearer.

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

> 📝 **Practice:** [Q21 · exception-types](../python_practice_questions_100.md#q21--critical--exception-types)

**The Order of Except Clauses Matters**

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

> [↑ Back to Top](#top)

<a id="5-raise-throwing-exceptions"></a>
# 5. raise: Throwing Exceptions

**Basic raise:**

```python
def withdraw(balance: float, amount: float) -> float:
    if amount <= 0:
        raise ValueError(f"Amount must be positive, got {amount}")
    if amount > balance:
        raise ValueError(f"Insufficient funds: balance={balance}, requested={amount}")
    return balance - amount
```

**Re-raise the same exception:**

```python
try:
    risky_call()
except ValueError as e:
    logging.error("Validation failed: %s", e)
    raise    # ← re-raises the SAME exception, preserves full traceback
```

<a id="exception-chaining"></a>
## Exception Chaining — raise ... from

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

> 📝 **Practice:** [Q43 · exception-chaining](../python_practice_questions_100.md#q43--thinking--exception-chaining)

```python
# To suppress the original exception chain (explicit suppression):
raise NewError("context-free message") from None
```

> 📝 **Practice:** [Q13 — Custom AppError](./practice.md#q13--custom-exceptions--define-apperror-with-message-and-code) · [Q14 — Hierarchy design](./practice.md#q14--exception-hierarchy--paymentinsufficientfunds-inheritance) · [Deep dive →](./02_custom_exceptions/theory.md)

> [↑ Back to Top](#top)

<a id="6-custom-exceptions-design-like-a-pro"></a>
# 6. Custom Exceptions: Design Like a Pro

> 📝 **Practice:** [Q42 · custom-exceptions](../python_practice_questions_100.md#q42--normal--custom-exceptions)

```python
# ❌ Don't do this — tells nothing about the domain:
raise Exception("something went wrong with payment")

# ✅ Do this:
class PaymentError(Exception): pass
raise PaymentError("Card declined: insufficient funds")
```

<a id="full-professional-exception-hierarchy"></a>
## Full Professional Exception Hierarchy

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

> 📝 **Practice:** [Q15 — Why use with?](./practice.md#q15--context-managers--why-with-beats-tryfinally) · [Q16 — __enter__/__exit__](./practice.md#q16--context-manager-class--database-transaction-with-__enter__--__exit__) · [Q17 — @contextmanager](./practice.md#q17--contextlibcontextmanager--timing-context-manager)

> [↑ Back to Top](#top)

<a id="7-context-managers-the-right-way-to-handle-resources"></a>
# 7. Context Managers: The Right Way to Handle Resources

**The Problem Without Context Managers**

```python
# ❌ DANGEROUS — what if an exception happens before file.close()?
file = open("data.txt")
data = file.read()
process(data)        # ← if THIS raises, file.close() never runs → resource leak!
file.close()
```

<a id="with-statement"></a>
## with Statement — The Solution

The `with` statement guarantees that `__exit__` is called on the context manager whether or not an exception occurs — so resources are always released cleanly without manual `try/finally` boilerplate.

```python
# ✅ SAFE — always closes, even if an exception is raised:
with open("data.txt") as file:
    data = file.read()
    process(data)
# file.close() called automatically here, exception or not
```

For a full deep dive into context managers: [12_context_managers/theory.md](../12_context_managers/theory.md)

<a id="how-it-works-internally"></a>
## How It Works Internally

`with` is syntactic sugar for the `__enter__` / `__exit__` protocol: Python calls `__enter__` before the block and `__exit__` after it, passing exception info if one was raised. Any class that implements both methods is a valid context manager.

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

<a id="contextlib-contextmanager"></a>
## contextlib.contextmanager — The Easy Way

Writing a full class with `__enter__` and `__exit__` is verbose for simple cases. The `@contextmanager` decorator lets you write a generator function instead — everything before `yield` is `__enter__`, everything after is `__exit__`.

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

<a id="multiple-context-managers"></a>
## Multiple Context Managers

Python supports opening multiple context managers in a single `with` statement — they nest left-to-right on entry and close right-to-left on exit, the same as nested `with` blocks but without the indentation pyramid.

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

> 📝 **Practice:** [Q18 — LBYL → EAFP rewrite](./practice.md#q18--lbyl-vs-eafp--rewrite-the-lbyl-version-as-eafp)

> [↑ Back to Top](#top)

<a id="8-lbyl-vs-eafp-pythons-philosophy"></a>
# 8. LBYL vs EAFP: Python's Philosophy

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

> 📝 **Practice:** [Q21 — Retry decorator](./practice.md#q21--retry-decorator--exponential-backoff-3-attempts) · [Deep dive →](./03_production_patterns/theory.md)

> [↑ Back to Top](#top)

<a id="9-retry-exponential-backoff"></a>
# 9. Retry & Exponential Backoff — The Full Picture

> You knock on a door. No answer. You wait 1 second and knock again. Still nothing.
> You wait 2 seconds. Then 4. Then 8. You're not hammering the door down — you're
> giving the person inside time to get up. That's exponential backoff.

Networks blip. APIs rate-limit. Databases hiccup. The wrong response is to retry
immediately in a tight loop — you'll overwhelm a struggling service and make things
worse. **Exponential backoff** spaces retries out with increasing delays, giving
the upstream system room to recover.

<a id="the-math"></a>
## The Math

```
attempt 1 fails → wait base_delay * factor^0  = 1s
attempt 2 fails → wait base_delay * factor^1  = 2s
attempt 3 fails → wait base_delay * factor^2  = 4s
attempt 4 fails → wait base_delay * factor^3  = 8s
attempt 5 fails → wait base_delay * factor^4  = 16s  (capped at max_delay)
```

```
Timeline (no jitter):

t=0s   ───[attempt 1]──── FAIL
t=1s   ───[attempt 2]──── FAIL
t=3s   ───[attempt 3]──── FAIL
t=7s   ───[attempt 4]──── OK ✓

Timeline (with jitter):

t=0s   ───[attempt 1]──── FAIL
t=1.3s ───[attempt 2]──── FAIL   ← 1s + 0.3s random
t=3.7s ───[attempt 3]──── FAIL   ← 2s + 0.7s random (delays overlap less)
t=8.1s ───[attempt 4]──── OK ✓
```

<a id="why-jitter-matters"></a>
## Why Jitter Matters — The Thundering Herd Problem

Without jitter, every client that hit the same failure retries at the exact same
moment — 100 services all wake up at t=1s, hammer the API in sync, cause the same
failure again. **Jitter** adds random noise to spread retry storms across time.

```
WITHOUT jitter (100 clients all retry at t=1s):
    t=1s  ████████████████████████████████ (100 requests hit simultaneously)
    t=3s  ████████████████████████████████ (still synchronized)

WITH jitter (each client adds random(0, delay)):
    t=0.8-1.9s  ░░░█░░██░█░░░█░░░██░░█░ (spread out — service breathes)
    t=2.1-4.3s  ░█░░░█░░░░█░░░██░░░█░░░ (no spike)
```

<a id="hand-rolled-implementation"></a>
## Hand-Rolled Implementation

```python
import time
import random
import functools


def retry(max_attempts=3, exceptions=(Exception,), base_delay=1.0,
          backoff_factor=2.0, max_delay=60.0, jitter=True):
    """Retry decorator with exponential backoff and optional jitter."""

    def decorator(func):
        @functools.wraps(func)     # ← preserves __name__, __doc__ on wrapped func
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exc = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exc = e
                    if attempt == max_attempts:
                        break                      # ← exhausted, fall through to raise

                    wait = min(delay, max_delay)
                    if jitter:
                        wait += random.uniform(0, wait * 0.1)   # ← ±10% noise
                    print(f"Attempt {attempt}/{max_attempts} failed: {e}. "
                          f"Retrying in {wait:.2f}s...")
                    time.sleep(wait)
                    delay *= backoff_factor        # ← double the wait each round

            raise last_exc    # ← all attempts exhausted

        return wrapper
    return decorator
```

Usage:

```python
@retry(max_attempts=4, exceptions=(ConnectionError, TimeoutError), base_delay=1.0)
def fetch_user(user_id: int):
    return requests.get(f"https://api.example.com/users/{user_id}", timeout=5)

# Attempt 1/4 failed: ConnectionError. Retrying in 1.07s...
# Attempt 2/4 failed: ConnectionError. Retrying in 2.14s...
# Attempt 3/4 failed: ConnectionError. Retrying in 4.02s...
# Attempt 4/4 failed: ConnectionError.
# ConnectionError raised  ← caller handles it
```

<a id="production-approach-tenacity"></a>
## Production Approach — tenacity

For production code, use **`tenacity`** — battle-tested, handles edge cases,
composable stop/wait/retry conditions.

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import logging

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(5),                    # ← max 5 tries
    wait=wait_exponential(multiplier=1, min=1, max=60),  # ← 1s, 2s, 4s... capped at 60s
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    before_sleep=before_sleep_log(logger, logging.WARNING),  # ← logs each retry
)
def call_payment_api(payload: dict):
    return requests.post("https://api.stripe.com/v1/charges", data=payload)
```

<a id="async-version"></a>
## Async Version

When using `asyncio`, `time.sleep()` blocks the event loop — use `asyncio.sleep()`.

```python
import asyncio
import random

async def with_backoff(coro_func, *args, max_retries=5, base_delay=1.0):
    """Async retry with exponential backoff."""
    delay = base_delay

    for attempt in range(1, max_retries + 1):
        try:
            return await coro_func(*args)          # ← await the coroutine

        except (ConnectionError, TimeoutError) as e:
            if attempt == max_retries:
                raise
            jitter = random.uniform(0, delay * 0.1)
            await asyncio.sleep(delay + jitter)    # ← non-blocking sleep
            delay *= 2

# Usage:
result = await with_backoff(fetch_user_async, user_id=42)
```

<a id="when-not-to-retry"></a>
## When NOT to Retry

Not every error is transient. Retrying these makes things worse, not better:

```
RETRY these (transient):          DON'T RETRY these (permanent):
────────────────────────────────  ──────────────────────────────────
ConnectionError                   400 Bad Request  (your data is wrong)
TimeoutError                      401 Unauthorized (fix your auth)
503 Service Unavailable           403 Forbidden    (you don't have access)
429 Too Many Requests             404 Not Found    (resource doesn't exist)
network blips                     ValidationError  (your input is invalid)
```

```python
# Check HTTP status before deciding to retry:
def should_retry(exc: Exception) -> bool:
    if isinstance(exc, requests.HTTPError):
        return exc.response.status_code in {429, 500, 502, 503, 504}  # ← transient
    return isinstance(exc, (ConnectionError, TimeoutError))
```

> 📝 **Practice:** [Q22 — Circuit breaker states](./practice.md#q22--circuit-breaker--explain-the-3-states) · [Q23 — Graceful degradation](./practice.md#q23--graceful-degradation--fallback-to-cache-on-failure) · [Deep dive →](./03_production_patterns/theory.md)

> [↑ Back to Top](#top)

<a id="10-production-patterns"></a>
# 10. Production Patterns

<a id="pattern-1-retry"></a>
## Pattern 1 — Retry with Exponential Backoff

See [# 9. Retry & Exponential Backoff](#9-retry-exponential-backoff) for the complete treatment — math, jitter, hand-rolled implementation, `tenacity`, async, and when not to retry.

Quick reference:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=30))
def unreliable_api_call():
    return requests.get("https://api.example.com/data")
```

<a id="pattern-2-circuit-breaker"></a>
## Pattern 2 — Circuit Breaker

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

<a id="pattern-3-graceful-degradation"></a>
## Pattern 3 — Graceful Degradation

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

<a id="pattern-4-exception-translation"></a>
## Pattern 4 — Exception Translation (Layered Architecture)

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

> 📝 **Practice:** [Q19 — logger.exception() vs logger.error()](./practice.md#q19--logging-exceptions--loggerexception-vs-loggererror)

> [↑ Back to Top](#top)

<a id="11-logging-exceptions-correctly"></a>
# 11. Logging Exceptions Correctly

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

> 📝 **Practice:** [Q24 — Fix bare except](./practice.md#q24--anti-pattern--fix-bare-except-with-pass) · [Q25 — Catching too broadly](./practice.md#q25--anti-pattern--catching-too-broadly-masks-bugs) · [Deep dive →](./03_production_patterns/theory.md)

> [↑ Back to Top](#top)

<a id="12-anti-patterns"></a>
# 12. Anti-Patterns (Don't Do These)

<a id="anti-pattern-1"></a>
## Anti-Pattern 1 — Bare except / Silent pass

Silently swallowing every exception is the most dangerous pattern in Python — it hides bugs, prevents Ctrl+C from working, and makes debugging nearly impossible because you lose all information about what went wrong.

```python


# WORST possible code:
try:
    do_something()
except:          # catches SystemExit, KeyboardInterrupt, everything!
    pass         # hides every error silently — debugging nightmare
```

> 📝 **Practice:** [Q44 · bare-except](../python_practice_questions_100.md#q44--critical--bare-except)

<a id="anti-pattern-2"></a>
## Anti-Pattern 2 — Catching Too Broadly

Catching `Exception` across a large block makes it impossible to know which line actually failed or why — every error looks the same, and you can't write targeted recovery logic.

```python
# BAD — which exception are you actually expecting?
try:
    user = get_user(id)
    order = create_order(user)
    send_email(user, order)
except Exception as e:
    print("Error")   # you have no idea which of the 3 lines failed!
```

<a id="anti-pattern-3"></a>
## Anti-Pattern 3 — Using Exceptions for Normal Control Flow

Exceptions have overhead — they capture a full traceback on every raise. Using them for expected branching in a tight loop is measurably slower than a simple `if` check or `.get()` call.

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

> 📝 **Practice:** [Q20 · exception-flow](../python_practice_questions_100.md#q20--logical--exception-flow)

<a id="anti-pattern-4"></a>
## Anti-Pattern 4 — Losing the Original Exception

Raising a new exception without `from e` destroys the original traceback — the root cause is permanently lost, leaving only the re-wrapped error with no context about what triggered it.

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

<a id="anti-pattern-5"></a>
## Anti-Pattern 5 — except Exception Without Re-raise

Catching broadly and returning `None` silently converts an error into unexpected behavior for the caller — they get back a `None` with no exception raised and no way to diagnose what went wrong.

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

> 📝 **Practice:** [Q28 — Thread exception loss](./practice.md#q28--thread-exceptions--silently-swallowed-show-and-fix)

> [↑ Back to Top](#top)

<a id="13-exceptions-in-threads-and-async"></a>
# 13. Exceptions in Threads and Async

<a id="threads-exceptions-silently-lost"></a>
## Threads — Exceptions Are Silently Lost!

Exceptions raised inside a thread do NOT propagate to the parent thread — they are printed to stderr and discarded unless you explicitly capture them. The main thread has no way to know the worker failed.

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

<a id="concurrent-futures"></a>
## concurrent.futures — The Better Way

`ThreadPoolExecutor` solves the exception problem by storing exceptions inside `Future` objects — calling `future.result()` re-raises them in the calling thread, so errors are never silently lost.

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

<a id="async-asyncio"></a>
## Async — asyncio

In async code, exceptions in coroutines behave like synchronous ones — they propagate up the `await` chain normally. When using `asyncio.gather`, pass `return_exceptions=True` to prevent one task's failure from cancelling all other running tasks.

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

> 📝 **Practice:** [Q29 — Read a traceback](./practice.md#q29--reading-tracebacks--identify-root-cause-and-propagation-path)

> [↑ Back to Top](#top)

<a id="14-reading-tracebacks-like-a-pro"></a>
# 14. Reading Tracebacks Like a Pro

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

<a id="exception-propagation"></a>
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

> [↑ Back to Top](#top)

<a id="15-warnings-module"></a>
# 15. warnings Module — Non-Fatal Alerts

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

> [↑ Back to Top](#top)

<a id="key-takeaways"></a>
# 🎯 Key Takeaways

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

<a id="navigation"></a>
# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [05 — OOP → theory.md](../05_oops/theory.md) |
| ➡ Next Module | [07 — Modules & Packages → theory.md](../07_modules_packages/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Practice Local](./practice_local.py) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[01 Exception Mechanics →](./01_exception_mechanics/theory.md) · [02 Custom Exceptions →](./02_custom_exceptions/theory.md) · [03 Production Patterns →](./03_production_patterns/theory.md) · [12 Context Managers →](../12_context_managers/theory.md) · [13 Concurrency →](../13_concurrency/theory.md)

**Jump to specific topics:**
- Exception chaining (`raise from`) → [#exception-chaining](#exception-chaining)
- LBYL vs EAFP → [#8-lbyl-vs-eafp-pythons-philosophy](#8-lbyl-vs-eafp-pythons-philosophy)
- Retry & backoff deep dive → [#9-retry-exponential-backoff](#9-retry-exponential-backoff)
- Context managers deep dive → [12_context_managers/theory.md](../12_context_managers/theory.md)
- Threading exceptions → [13_concurrency/theory.md](../13_concurrency/theory.md)

> [↑ Back to Top](#top)
