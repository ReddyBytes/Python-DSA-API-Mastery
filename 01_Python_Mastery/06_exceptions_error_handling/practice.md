# 🛑 Exceptions & Error Handling Practice — Master Problem Set

> 35 questions covering all 13 chapters. Attempt from memory, then reveal hint, then check answer.

---

## Quick Index

| Q# | Concept | Chapter | Difficulty |
|----|---------|---------|------------|
| [Q1](#q1) | Exception propagation through nested calls | Ch1 | 🟢 Beginner |
| [Q2](#q2) | try/except/else/finally for file open | Ch3 | 🟢 Beginner |
| [Q3](#q3) | else vs except — when each runs | Ch3 | 🟢 Beginner |
| [Q4](#q4) | finally edge case: return swallows exception | Ch3 | 🟡 Intermediate |
| [Q5](#q5) | Catch ZeroDivisionError and ValueError separately | Ch4 | 🟢 Beginner |
| [Q6](#q6) | Fix bare except with pass | Ch11 | 🟡 Intermediate |
| [Q7](#q7) | Exception hierarchy — why ValueError catches int("x") | Ch2 | 🟡 Intermediate |
| [Q8](#q8) | Catch multiple exceptions in one clause | Ch4 | 🟡 Intermediate |
| [Q9](#q9) | Order of except clauses — fix shadowing bug | Ch4 | 🟡 Intermediate |
| [Q10](#q10) | Re-raise original exception after logging | Ch5 | 🟡 Intermediate |
| [Q11](#q11) | raise...from — exception chaining | Ch5 | 🟡 Intermediate |
| [Q12](#q12) | raise from None — suppress the chain | Ch5 | 🟡 Intermediate |
| [Q13](#q13) | Define AppError with message and code attributes | Ch6 | 🟡 Intermediate |
| [Q14](#q14) | Custom exception hierarchy (3 classes) | Ch6 | 🟡 Intermediate |
| [Q15](#q15) | Why use with open() instead of try/finally | Ch7 | 🟢 Beginner |
| [Q16](#q16) | Context manager with __enter__ / __exit__ | Ch7 | 🟡 Intermediate |
| [Q17](#q17) | @contextlib.contextmanager — timing manager | Ch7 | 🟡 Intermediate |
| [Q18](#q18) | LBYL vs EAFP — rewrite + trade-off | Ch8 | 🟡 Intermediate |
| [Q19](#q19) | logger.exception() vs logger.error() | Ch10 | 🟡 Intermediate |
| [Q20](#q20) | Include traceback in log without crashing | Ch10 | 🟡 Intermediate |
| [Q21](#q21) | Retry with exponential backoff decorator | Ch9 | 🟠 Advanced |
| [Q22](#q22) | Circuit breaker — 3 states | Ch9 | 🟠 Advanced |
| [Q23](#q23) | Graceful degradation — return cached result | Ch9 | 🟡 Intermediate |
| [Q24](#q24) | Fix silent except Exception: pass | Ch11 | 🟡 Intermediate |
| [Q25](#q25) | Catching too broadly masks a bug | Ch11 | 🟡 Intermediate |
| [Q26](#q26) | Exceptions for normal control flow anti-pattern | Ch11 | 🟡 Intermediate |
| [Q27](#q27) | Losing the original exception — raise from e fix | Ch11 | 🟡 Intermediate |
| [Q28](#q28) | Exception silently lost in a thread | Ch12 | 🟠 Advanced |
| [Q29](#q29) | Read a traceback — root cause vs propagation | Ch13 | 🟡 Intermediate |
| [Q30](#q30) | as e scope: when does the binding get cleared? | Ch4 | 🟡 Intermediate |
| [Q31](#q31) | Exception translation: HTTPError → ApiError | Ch5 | 🟠 Advanced |
| [Q32](#q32) | finally always runs — resource release example | Ch3 | 🟡 Intermediate |
| [Q33](#q33) | ExceptionGroup (Python 3.11+) | Ch12 | 🟡 Intermediate |
| [Q34](#q34) | Capstone: safe_api_call with retries and fallback | Ch9 | 🟠 Advanced |
| [Q35](#q35) | Capstone: payment system exception hierarchy | Ch6 | 🟠 Advanced |

---

<a id="q1"></a>

### Q1 · Exception Propagation — Trace the Call Stack

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)



🟢 Beginner

```python
def c():
    return 1 / 0

def b():
    return c()

def a():
    try:
        b()
    except ZeroDivisionError as e:
        print(f"Caught in a: {e}")

a()
```

What is printed? Draw the propagation path of the exception from where it is raised to where it is caught.

<details>
<summary>💡 Hint</summary>
Trace the call stack frame by frame: `a` calls `b`, `b` calls `c`, `c` raises. Python unwinds the stack looking for a matching `except` clause at each level.
</details>

<details>
<summary>✅ Answer</summary>

**Output:**
```
Caught in a: division by zero
```

**Propagation path:**

```
c() raises ZeroDivisionError
  ↓ no handler in c — unwind
b() has no try/except — unwind
  ↓ no handler in b — unwind
a() has except ZeroDivisionError — CAUGHT HERE
```

Think of the **call stack** as a stack of plates. When an exception is raised, Python starts popping plates from the top, checking each one for a matching `except` clause. The moment it finds one, it stops popping. If it reaches the bottom (the interpreter) with no match, Python prints the traceback and exits.

**Why:** Understanding propagation tells you why a `try` block at the top of your program can catch errors from deep inside library code — the exception bubbles all the way up until someone handles it.
</details>

---

<a id="q2"></a>

### Q2 · try/except/else/finally — File Open

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)



🟢 Beginner

Write a function `read_config(path)` that opens a file, reads its contents, and returns them. Use all four clauses: `try`, `except`, `else`, and `finally`. Print a message in each clause so the flow is visible.

<details>
<summary>💡 Hint</summary>
`else` runs when no exception occurred in `try`. `finally` runs no matter what.
</details>

<details>
<summary>✅ Answer</summary>

```python
def read_config(path):
    try:
        f = open(path, "r")         # ← only this line can raise here
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return None
    else:
        contents = f.read()         # ← runs only if open() succeeded
        print("File read successfully")
        return contents
    finally:
        print("Cleanup: closing file if open")
        try:
            f.close()
        except NameError:
            pass  # f was never assigned — open() failed before assignment
```

**Why:** Separating the `try` block to contain only the risky operation (`open`) makes the intent clear: `else` is the "happy path" code that depends on success, and `finally` is unconditional cleanup. This pattern avoids accidentally catching exceptions raised in your own success-path code.
</details>

---

<a id="q3"></a>

### Q3 · else vs except — When Each Runs

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)



🟢 Beginner

Fill in the blanks and predict the output for each call:

```python
def divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("except ran")
    else:
        print("else ran, result:", result)
    finally:
        print("finally ran")

divide(10, 2)
divide(10, 0)
```

<details>
<summary>💡 Hint</summary>
`else` runs when the `try` block completes without raising any exception. `except` runs when a matching exception is raised. `finally` always runs.
</details>

<details>
<summary>✅ Answer</summary>

```
# divide(10, 2):
else ran, result: 5.0
finally ran

# divide(10, 0):
except ran
finally ran
```

The rule: `else` and `except` are mutually exclusive — exactly one of them runs per execution (or neither, if a non-matching exception propagates). `finally` is never skipped.

Think of `else` as "the code that should only run if the risky operation actually worked." This is better than putting that code inside the `try` block, because if the success-path code raises, it would incorrectly trigger your `except` handler.

**Why:** Using `else` correctly narrows the `try` block to the minimum dangerous surface area, making bugs easier to isolate.
</details>

---

<a id="q4"></a>

### Q4 · finally Edge Case — return Inside finally

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)



🟡 Intermediate

What does this function return? Explain why.

```python
def tricky():
    try:
        raise ValueError("problem")
    finally:
        return 42
```

<details>
<summary>💡 Hint</summary>
`finally` runs even when an exception is in flight. A `return` statement inside `finally` has a side effect that surprises most developers.
</details>

<details>
<summary>✅ Answer</summary>

**It returns `42`. The ValueError is silently swallowed.**

```python
result = tricky()
print(result)   # 42 — no exception raised at the call site
```

When Python is unwinding the stack due to an active exception and it enters a `finally` block, a `return` (or `break`) statement inside that block **cancels the exception** and replaces it with the return value. The exception is gone — no traceback, no re-raise.

Think of the exception as a ball rolling toward the exit. `finally` is a room it must pass through. If someone catches the ball inside that room and doesn't throw it again, it never exits.

**Why:** This is a notorious footgun. Never put `return`, `break`, or `continue` inside a `finally` block unless you intentionally want to suppress exceptions. Static analysis tools like `flake8` warn about this (E722-adjacent patterns).
</details>

---

<a id="q5"></a>

### Q5 · Catching Multiple Exceptions Separately

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)



🟢 Beginner

Write a function `parse_and_divide(s, n)` that converts `s` to an integer and divides it by `n`. Catch `ValueError` (bad string) and `ZeroDivisionError` (n is zero) with separate `except` clauses, printing a distinct message for each.

<details>
<summary>💡 Hint</summary>
Two separate `except` blocks, each naming one exception type.
</details>

<details>
<summary>✅ Answer</summary>

```python
def parse_and_divide(s, n):
    try:
        value = int(s)          # ← raises ValueError if s is not numeric
        result = value / n      # ← raises ZeroDivisionError if n == 0
    except ValueError:
        print(f"Cannot convert '{s}' to integer")
        return None
    except ZeroDivisionError:
        print("Cannot divide by zero")
        return None
    return result

parse_and_divide("abc", 5)  # ValueError path
parse_and_divide("10", 0)   # ZeroDivisionError path
parse_and_divide("10", 2)   # success → 5.0
```

**Why:** Separate `except` clauses let you respond differently to each failure mode. The user who passes `"abc"` needs a different error message than the user who passes `n=0`. Combining them into one handler would force you to inspect `type(e)` manually — that's a code smell.
</details>

---

<a id="q6"></a>

### Q6 · Anti-pattern Fix — Bare except with pass

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)



🟡 Intermediate

The following code silently swallows every possible error, including `KeyboardInterrupt` and `SystemExit`. Rewrite it correctly.

```python
def load_data(path):
    try:
        with open(path) as f:
            return f.read()
    except:
        pass
```

<details>
<summary>💡 Hint</summary>
Bare `except:` catches `BaseException`, not just `Exception`. Name the exception, log it, and decide whether to return a sentinel value or re-raise.
</details>

<details>
<summary>✅ Answer</summary>

```python
import logging

logger = logging.getLogger(__name__)

def load_data(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        logger.warning("Config file not found: %s", path)
        return None                  # ← explicit sentinel — caller knows it failed
    except OSError as e:
        logger.error("Failed to read %s: %s", path, e)
        raise                        # ← re-raise unexpected OS errors
```

The original had three problems: it used bare `except:` (catches `KeyboardInterrupt`, `SystemExit`, `MemoryError`), it used `pass` (silent failure), and it gave the caller no signal that anything went wrong.

**Why:** Silent failures are the hardest bugs to diagnose. Always: name the exception, log it at an appropriate level, and either return an explicit sentinel value or re-raise. Never let errors disappear without a trace.
</details>

---

<a id="q7"></a>

### Q7 · Exception Hierarchy — Why ValueError Catches int("x")

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)



🟡 Intermediate

Explain why `except ValueError` catches the exception raised by `int("x")`. Draw the relevant portion of the exception hierarchy. Then show code that demonstrates catching a parent catches the child.

<details>
<summary>💡 Hint</summary>
Python's `except` clause uses `isinstance()` semantics. `int("x")` raises `ValueError`. Where does `ValueError` sit in the hierarchy?
</details>

<details>
<summary>✅ Answer</summary>

```
BaseException
└── Exception
    └── ValueError        ← int("x") raises this
```

`except SomeClass` catches the exception if the raised object is an **instance of** `SomeClass` or any of its subclasses. This is identical to `isinstance(exc, SomeClass)`.

```python
try:
    int("x")
except Exception as e:          # ← catches ValueError because ValueError is-a Exception
    print(type(e).__name__)     # ValueError

try:
    int("x")
except ValueError as e:         # ← also catches it directly
    print("caught as ValueError")
```

```python
# Demonstration: parent catches child
class Animal(Exception): pass
class Dog(Animal): pass

try:
    raise Dog("woof")
except Animal:                  # ← catches Dog because Dog is-a Animal
    print("caught by Animal handler")
```

**Why:** This hierarchy design lets you write broad handlers at the top level of an application (catch `Exception`) and specific handlers deeper in the call stack (catch `ValueError`). It also means the order of your `except` clauses matters — put the most specific first.
</details>

---

<a id="q8"></a>

### Q8 · Tuple Syntax for Multiple Exceptions

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)



🟡 Intermediate

Rewrite this with a single `except` clause that catches both `TypeError` and `ValueError`. Then explain when to use the tuple syntax vs separate clauses.

```python
try:
    result = int(user_input) * 2
except TypeError:
    print("wrong type")
except ValueError:
    print("wrong type")
```

<details>
<summary>💡 Hint</summary>
Use `except (ExcA, ExcB) as e:` when you want to handle multiple exception types the same way.
</details>

<details>
<summary>✅ Answer</summary>

```python
try:
    result = int(user_input) * 2
except (TypeError, ValueError) as e:   # ← tuple groups exceptions with identical handling
    print(f"Invalid input: {e}")
```

**When to use tuple syntax:** When the handling code is identical — same log message, same return value, same recovery action.

**When to use separate clauses:** When different exception types require different responses.

```python
# Separate — different handling
try:
    process(data)
except ValueError as e:
    logger.warning("Bad value, skipping: %s", e)
    return DEFAULT
except TypeError as e:
    logger.error("Type mismatch — programmer error: %s", e)
    raise   # ← re-raise; this is a bug, not user error
```

**Why:** The tuple form is a readability signal: "these errors are equivalent from this function's perspective." Separate clauses signal: "these errors mean different things."
</details>

---

<a id="q9"></a>

### Q9 · Order of except Clauses — Fix the Shadowing Bug

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)



🟡 Intermediate

The following code has a bug: `except Exception` always fires before `except ValueError`. Fix it and explain the rule.

```python
def convert(s):
    try:
        return int(s)
    except Exception as e:
        print(f"General error: {e}")
    except ValueError as e:
        print(f"ValueError: {e}")   # ← never reached
```

<details>
<summary>💡 Hint</summary>
Python tries `except` clauses top-to-bottom and stops at the first match. Since `ValueError` is a subclass of `Exception`, `Exception` matches first.
</details>

<details>
<summary>✅ Answer</summary>

```python
def convert(s):
    try:
        return int(s)
    except ValueError as e:         # ← specific first
        print(f"ValueError: {e}")
    except Exception as e:          # ← general last (catch-all)
        print(f"Unexpected error: {e}")
        raise
```

The rule: **specific exceptions before general ones**, always. Python evaluates `except` clauses in order, like `if/elif/else`. The first matching clause wins.

```
int("x") raises ValueError
  except ValueError  ← matches (ValueError is-a ValueError) ✓ STOP
  except Exception   ← never reached
```

**Why:** A misplaced broad `except Exception` silently swallows errors you intended to handle specifically. Python does not warn you — it is valid syntax. Code review and tests are the only safeguard.
</details>

---

<a id="q10"></a>

### Q10 · Re-raise — Log Then Re-raise

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)



🟡 Intermediate

Write a function `fetch_user(user_id)` that calls `db.get(user_id)`. If it raises any `DatabaseError`, log the error with the traceback, then re-raise the original exception unchanged. Do not wrap it in a new exception.

<details>
<summary>💡 Hint</summary>
A bare `raise` inside an `except` block re-raises the currently active exception, preserving its type, message, and original traceback.
</details>

<details>
<summary>✅ Answer</summary>

```python
import logging

logger = logging.getLogger(__name__)

def fetch_user(user_id):
    try:
        return db.get(user_id)
    except DatabaseError:
        logger.exception("Failed to fetch user %s", user_id)  # ← logs with traceback
        raise                                                   # ← bare raise: re-raises original
```

**Bare `raise`** is distinct from `raise e`: bare `raise` preserves the original traceback location (where it was first raised), while `raise e` resets the traceback to the current line, losing the original context.

```python
# Do this:
except SomeError:
    logger.exception("...")
    raise           # ← traceback points to original raise site

# Not this:
except SomeError as e:
    logger.exception("...")
    raise e         # ← traceback now points here, losing original location
```

**Why:** Preserving the original traceback is essential for debugging in production. When you see the error in your log aggregator, you want to know where it actually originated, not just where it was caught and re-raised.
</details>

---

<a id="q11"></a>

### Q11 · raise...from — Exception Chaining

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)



🟡 Intermediate

What does the `from` keyword do in a `raise` statement? Write an example that wraps a low-level `requests.ConnectionError` in a domain-specific `ServiceUnavailableError`, preserving the original as the cause.

<details>
<summary>💡 Hint</summary>
`raise NewError("msg") from original_error` sets `__cause__` on the new exception, and Python displays both in the traceback with "The above exception was the direct cause of the following exception."
</details>

<details>
<summary>✅ Answer</summary>

```python
import requests

class ServiceUnavailableError(Exception):
    pass

def call_payment_api(amount):
    try:
        response = requests.post("https://payments.example.com/charge", json={"amount": amount})
        response.raise_for_status()
    except requests.ConnectionError as e:
        raise ServiceUnavailableError("Payment service is down") from e  # ← explicit chain
```

**What the traceback shows:**
```
requests.exceptions.ConnectionError: ...

The above exception was the direct cause of the following exception:

ServiceUnavailableError: Payment service is down
```

`raise X from Y` sets `X.__cause__ = Y` and `X.__suppress_context__ = True`.

Think of it as a translation layer: you receive a low-level library error and hand back a domain error. The `from` clause keeps a paper trail — callers get a clean domain error, and engineers debugging the traceback can see exactly what library-level thing went wrong.

**Why:** Exception chaining is the right pattern for **exception translation** — converting infrastructure errors into domain errors without losing the root cause.
</details>

---

<a id="q12"></a>

### Q12 · raise from None — Suppress the Chain

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)



🟡 Intermediate

When and why would you use `raise SomeError("msg") from None`? Show a concrete example where suppressing the chain improves the user experience.

<details>
<summary>💡 Hint</summary>
`from None` sets `__suppress_context__ = True`. Use it when the original exception would expose internal implementation details that are irrelevant or confusing to the caller.
</details>

<details>
<summary>✅ Answer</summary>

```python
def get_config_value(key):
    _INTERNAL_CONFIG = {"timeout": 30, "retries": 3}
    try:
        return _INTERNAL_CONFIG[key]
    except KeyError:
        raise ValueError(f"Unknown config key: '{key}'") from None  # ← suppress chain
```

Without `from None`, the traceback would show:
```
KeyError: 'timeout_ms'

During handling of the above exception, another exception occurred:

ValueError: Unknown config key: 'timeout_ms'
```

With `from None`, the caller only sees:
```
ValueError: Unknown config key: 'timeout_ms'
```

The `KeyError` leaks the internal data structure (`_INTERNAL_CONFIG` is a `dict`). That is an implementation detail callers should not depend on. `from None` hides it.

**Why:** Use `from None` when the original exception reveals private implementation details that would confuse callers or create accidental coupling to your internals. Use `from e` (explicit chain) when the cause is genuinely useful context for debugging.
</details>

---

<a id="q13"></a>

### Q13 · Custom Exception with Attributes

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)



🟡 Intermediate

Define a custom `AppError` exception class that accepts a `message` string and an integer `code`. It should store both as instance attributes. Show how to raise it and how to access the attributes in the `except` block.

<details>
<summary>💡 Hint</summary>
Override `__init__`, call `super().__init__(message)`, and assign `self.code`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class AppError(Exception):
    def __init__(self, message: str, code: int):
        super().__init__(message)       # ← passes message to Exception.__init__
        self.message = message          # ← store for attribute access
        self.code = code

    def __repr__(self):
        return f"AppError(message={self.message!r}, code={self.code})"


# Raising
raise AppError("User not found", code=404)

# Catching
try:
    raise AppError("User not found", code=404)
except AppError as e:
    print(e.code)       # 404
    print(e.message)    # User not found
    print(str(e))       # User not found  ← from super().__init__(message)
```

Calling `super().__init__(message)` ensures that `str(e)` and `repr(e)` work as expected and that logging infrastructure that calls `str(exc)` will display the message.

**Why:** Custom exception attributes let callers extract structured information without parsing a string. An HTTP framework can read `e.code` to set the response status. A retry decorator can read `e.retryable` to decide whether to retry.
</details>

---

<a id="q14"></a>

### Q14 · Custom Exception Hierarchy

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)



🟡 Intermediate

Design a three-class hierarchy for a payment system. `PaymentError` is the base. `InsufficientFundsError` and `CardDeclinedError` both inherit from it. Show that catching `PaymentError` catches both children.

<details>
<summary>💡 Hint</summary>
A caller that `except PaymentError` can handle all payment failures generically. Internal code can be specific.
</details>

<details>
<summary>✅ Answer</summary>

```python
class PaymentError(Exception):
    """Base class for all payment-related errors."""
    pass

class InsufficientFundsError(PaymentError):
    def __init__(self, balance, amount):
        super().__init__(f"Need {amount}, have {balance}")
        self.balance = balance
        self.amount = amount

class CardDeclinedError(PaymentError):
    def __init__(self, reason: str):
        super().__init__(f"Card declined: {reason}")
        self.reason = reason


# Specific handling deep in the stack
def charge(account, amount):
    if account.balance < amount:
        raise InsufficientFundsError(account.balance, amount)

# Generic handling at the API layer
try:
    charge(account, 500)
except InsufficientFundsError as e:
    return {"error": "insufficient_funds", "balance": e.balance}
except CardDeclinedError as e:
    return {"error": "card_declined", "reason": e.reason}
except PaymentError as e:
    return {"error": "payment_failed", "detail": str(e)}  # ← catch-all for future subclasses
```

**Why:** A shared base class lets callers choose their level of specificity. An API endpoint might handle each type differently. A test helper might just `except PaymentError` to assert any payment error occurred. New payment error types added later automatically work with existing `except PaymentError` handlers.
</details>

---

<a id="q15"></a>

### Q15 · Why use with open() Instead of try/finally

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)



🟢 Beginner

Explain the advantage of the `with` statement over an explicit `try/finally` for file handling. Show both versions side by side.

<details>
<summary>💡 Hint</summary>
The `with` statement calls `__exit__` automatically, which handles closing even if an exception occurs or `return` is used.
</details>

<details>
<summary>✅ Answer</summary>

```python
# Manual try/finally — error-prone
f = None
try:
    f = open("data.txt")
    data = f.read()
finally:
    if f is not None:       # ← must guard against f never being assigned
        f.close()

# Context manager — clean and correct
with open("data.txt") as f:
    data = f.read()         # ← f.close() called automatically in __exit__
```

The `with` version is shorter, but more importantly it is **correct by construction**: you cannot forget to call `close()`, you cannot accidentally skip it with an early `return`, and you do not need the `if f is not None` guard.

`with open(...)` calls `f.__enter__()` on entry and `f.__exit__()` on exit — whether the block exits normally, via exception, or via `return`/`break`/`continue`.

**Why:** Manual `try/finally` for resource management requires careful discipline and is easy to get wrong (the `f = None` guard, handling assignment failure). Context managers encode the correct pattern once and reuse it everywhere.
</details>

---

<a id="q16"></a>

### Q16 · Context Manager with __enter__ / __exit__

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)



🟡 Intermediate

Write a `DatabaseTransaction` context manager class. On enter, print "BEGIN". On exit, print "COMMIT" if no exception occurred, or "ROLLBACK" if an exception occurred. Do not suppress the exception.

<details>
<summary>💡 Hint</summary>
`__exit__(self, exc_type, exc_val, exc_tb)` receives exception info (all `None` if no exception). Return `False` (or `None`) to let the exception propagate.
</details>

<details>
<summary>✅ Answer</summary>

```python
class DatabaseTransaction:
    def __enter__(self):
        print("BEGIN")
        return self                     # ← value bound to `as` variable

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            print("COMMIT")             # ← no exception: success path
        else:
            print(f"ROLLBACK (due to {exc_type.__name__})")
        return False                    # ← False means: do not suppress exception


# Usage
with DatabaseTransaction():
    print("doing work")

# Output:
# BEGIN
# doing work
# COMMIT

with DatabaseTransaction():
    raise ValueError("something went wrong")

# Output:
# BEGIN
# ROLLBACK (due to ValueError)
# ValueError: something went wrong   ← propagates because __exit__ returned False
```

`__exit__` returning `True` suppresses the exception. Returning `False` or `None` lets it propagate. Almost always return `False` — suppressing exceptions is a separate, deliberate decision.

**Why:** This pattern is how database drivers, lock managers, and file handles implement safe resource cleanup. Writing it from scratch once makes the magic of `with` transparent.
</details>

---

<a id="q17"></a>

### Q17 · @contextlib.contextmanager — Timing Context Manager

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)



🟡 Intermediate

Use `@contextlib.contextmanager` to write a `timer(label)` context manager. It should print how long the `with` block took to execute.

<details>
<summary>💡 Hint</summary>
The `yield` in a `@contextmanager` function marks the entry/exit boundary. Code before `yield` is `__enter__`, code after is `__exit__`. Use `try/finally` to ensure the timing always prints.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time
from contextlib import contextmanager

@contextmanager
def timer(label: str):
    start = time.perf_counter()         # ← __enter__ side
    try:
        yield                           # ← the with block runs here
    finally:
        elapsed = time.perf_counter() - start
        print(f"{label}: {elapsed:.4f}s")  # ← __exit__ side, always runs


with timer("data processing"):
    time.sleep(0.1)
    result = sum(range(1_000_000))

# Output: data processing: 0.1234s
```

The `@contextmanager` decorator turns a generator function into a context manager. Everything before `yield` is `__enter__`, everything after is `__exit__`. The `try/finally` ensures the elapsed time is printed even if the `with` block raises.

If you need to handle exceptions, you can `except` around the `yield`:

```python
@contextmanager
def managed():
    try:
        yield
    except SomeError:
        # handle it
        pass
```

**Why:** `@contextmanager` lets you write context managers in 5 lines instead of a full class. Use it for one-off resource management or instrumentation where a class would be overkill.
</details>

---

<a id="q18"></a>

### Q18 · LBYL vs EAFP

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)



🟡 Intermediate

Rewrite this LBYL code as EAFP. Then explain the trade-off: when is each style preferable?

```python
# LBYL (Look Before You Leap)
def get_value(d, key):
    if key in d:
        return d[key]
    return None
```

<details>
<summary>💡 Hint</summary>
EAFP (Easier to Ask Forgiveness than Permission) tries the operation and catches the exception. For `dict` access, the exception is `KeyError`.
</details>

<details>
<summary>✅ Answer</summary>

```python
# EAFP (Easier to Ask Forgiveness than Permission)
def get_value(d, key):
    try:
        return d[key]
    except KeyError:
        return None
```

**Trade-offs:**

| | LBYL | EAFP |
|---|---|---|
| Style | Check conditions before acting | Try and handle failure |
| Python idiom | Less idiomatic | More idiomatic in Python |
| Race conditions | Vulnerable (check then act can race) | Safe (the operation is atomic) |
| Performance | Extra check even on success | No check overhead; exception path is slower |
| Readability | Explicit preconditions | Intent-focused |

**LBYL is better when:** The check is cheap, the failure path is complex, or you are in a race-condition-free context (e.g., checking `if path.exists()` before reading — though EAFP is still preferred).

**EAFP is better when:** The success case is dominant, race conditions are possible (file system, concurrent dict access), or the "check" requires duplicating the operation.

**Why:** Python's standard library is EAFP-first. Iterators use `StopIteration`. `dict.get()` exists but `try/except KeyError` is idiomatic. EAFP aligns with Python's "it is easier to ask forgiveness than permission" philosophy.
</details>

---

<a id="q19"></a>

### Q19 · logger.exception() vs logger.error()

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)



🟡 Intermediate

What is the difference between `logger.exception("msg")` and `logger.error("msg")` when called inside an `except` block? Show both and explain when to use each.

<details>
<summary>💡 Hint</summary>
`logger.exception()` automatically includes the current exception's traceback in the log output. `logger.error()` only logs what you pass it.
</details>

<details>
<summary>✅ Answer</summary>

```python
import logging

logger = logging.getLogger(__name__)

try:
    int("not a number")
except ValueError:
    logger.error("Conversion failed")
    # Log output: ERROR:__main__:Conversion failed
    # (no traceback)

try:
    int("not a number")
except ValueError:
    logger.exception("Conversion failed")
    # Log output: ERROR:__main__:Conversion failed
    # Traceback (most recent call last):
    #   File "...", line 2, in <module>
    #     int("not a number")
    # ValueError: invalid literal for int() with base 10: 'not a number'
```

`logger.exception()` is equivalent to `logger.error(..., exc_info=True)`. You can also use `logger.error("msg", exc_info=True)` anywhere — including outside an `except` block if you have an exception object — via `logger.error("msg", exc_info=exc)`.

```python
# Equivalent:
logger.exception("Failed")
logger.error("Failed", exc_info=True)
```

**When to use each:**
- `logger.exception()`: inside `except` blocks when you want the full traceback in the log
- `logger.error()`: when you have already described the error fully in the message, or when logging at a higher level where tracebacks are noise

**Why:** In production, `logger.exception()` is the default correct choice inside `except` blocks. Tracebacks are what engineers need to debug. Omitting them means you will have to reproduce the issue to understand it.
</details>

---

<a id="q20"></a>

### Q20 · Include Traceback in Log Without Crashing

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)



🟡 Intermediate

Write code that catches any `Exception`, logs the full traceback as a string into a variable (not to a logger), and prints it. Use the `traceback` module.

<details>
<summary>💡 Hint</summary>
`traceback.format_exc()` returns the current exception's traceback as a string. It must be called inside an `except` block.
</details>

<details>
<summary>✅ Answer</summary>

```python
import traceback

try:
    result = 1 / 0
except Exception:
    tb_string = traceback.format_exc()   # ← returns traceback as a string
    print("Captured traceback:")
    print(tb_string)

# Output:
# Captured traceback:
# Traceback (most recent call last):
#   File "...", line 3, in <module>
#     result = 1 / 0
# ZeroDivisionError: division by zero
```

```python
# Alternative: format a specific exception object
try:
    1 / 0
except Exception as e:
    tb_lines = traceback.format_exception(type(e), e, e.__traceback__)
    tb_string = "".join(tb_lines)
```

`traceback.format_exc()` is the simplest form. The alternative `traceback.format_exception(type(e), e, e.__traceback__)` works when you have the exception object and need to format it outside the `except` block.

**Why:** Capturing the traceback as a string is useful when you need to store it in a database, include it in an API response payload for debugging, or pass it to a structured logging system that does not support `exc_info=True`.
</details>

---

<a id="q21"></a>

### Q21 · Retry with Exponential Backoff

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)



🟠 Advanced

Write a `retry` decorator that retries a function up to 3 times on any `Exception`. Use exponential backoff starting at 1 second (1s, 2s, 4s). After all retries are exhausted, re-raise the last exception.

<details>
<summary>💡 Hint</summary>
Use `functools.wraps` to preserve the wrapped function's metadata. Track the attempt number and multiply the delay by 2 on each retry.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time
import functools
import logging

logger = logging.getLogger(__name__)

def retry(max_attempts=3, base_delay=1.0, exceptions=(Exception,)):
    def decorator(fn):
        @functools.wraps(fn)                    # ← preserves __name__, __doc__
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)  # ← success: return immediately
                except exceptions as e:
                    last_exc = e
                    if attempt == max_attempts:
                        break                   # ← no more retries
                    delay = base_delay * (2 ** (attempt - 1))  # ← 1s, 2s, 4s
                    logger.warning(
                        "%s attempt %d/%d failed: %s. Retrying in %.1fs",
                        fn.__name__, attempt, max_attempts, e, delay
                    )
                    time.sleep(delay)
            raise last_exc                      # ← re-raise after exhausting retries
        return wrapper
    return decorator


@retry(max_attempts=3, base_delay=1.0)
def call_external_api():
    # raises on network failure
    ...
```

The `exceptions` parameter makes the decorator configurable: you can limit it to only retry on `ConnectionError` and `TimeoutError`, not on `ValueError` (which indicates a programmer error, not a transient failure).

**Why:** Exponential backoff prevents a thundering herd: if a downstream service is overloaded and 1000 clients all retry simultaneously, constant-delay retry makes the problem worse. Exponential backoff spreads the load across time.
</details>

---

<a id="q22"></a>

### Q22 · Circuit Breaker — The 3 States

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)



🟠 Advanced

Explain the three states of the circuit breaker pattern (`CLOSED`, `OPEN`, `HALF_OPEN`) and the transitions between them. Then write a minimal `CircuitBreaker` class that tracks failure count and trips open after 3 consecutive failures.

<details>
<summary>💡 Hint</summary>
The state machine: CLOSED (normal) → OPEN (tripped) → HALF_OPEN (testing recovery) → CLOSED or OPEN.
</details>

<details>
<summary>✅ Answer</summary>

**The 3 states:**

```
CLOSED ──(3 failures)──► OPEN ──(timeout elapsed)──► HALF_OPEN
  ▲                                                       │
  └────────────(1 success)───────────────────────────────┘
  ◄────────────(1 failure)── stays/returns to OPEN ───────┘
```

- `CLOSED`: Normal operation. Calls pass through. Failures are counted.
- `OPEN`: All calls fail immediately (no attempt). Saves the downstream service from being hammered while it recovers.
- `HALF_OPEN`: One trial call is allowed. Success → CLOSED. Failure → OPEN again.

```python
import time
from enum import Enum

class State(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=30):
        self.state = State.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._opened_at = None

    def call(self, fn, *args, **kwargs):
        if self.state == State.OPEN:
            if time.time() - self._opened_at >= self.recovery_timeout:
                self.state = State.HALF_OPEN  # ← time to test recovery
            else:
                raise RuntimeError("Circuit breaker is OPEN — call rejected")

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
        if self.failure_count >= self.failure_threshold:
            self.state = State.OPEN
            self._opened_at = time.time()
```

**Why:** The retry pattern keeps trying a failed service, which can make a struggling service worse. The circuit breaker adds a "stop trying" state that gives the service time to recover, then tests recovery cautiously with HALF_OPEN.
</details>

---

<a id="q23"></a>

### Q23 · Graceful Degradation — Return Cached Result

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)



🟡 Intermediate

Write a `get_recommendations(user_id)` function. It tries a live API call first. If the call raises any exception, it returns a cached fallback result instead of propagating the error.

<details>
<summary>💡 Hint</summary>
Catch the exception, log it, and return a pre-computed fallback. The key is that the caller gets a usable result even when the live service is down.
</details>

<details>
<summary>✅ Answer</summary>

```python
import logging

logger = logging.getLogger(__name__)

FALLBACK_RECOMMENDATIONS = ["Item A", "Item B", "Item C"]  # ← cached/default

def get_recommendations(user_id: str) -> list:
    try:
        return recommendations_api.fetch(user_id)       # ← live call
    except Exception as e:
        logger.warning(
            "Recommendations API failed for user %s, using fallback: %s",
            user_id, e
        )
        return FALLBACK_RECOMMENDATIONS                 # ← degrade gracefully
```

**Graceful degradation** means the system continues functioning at reduced quality rather than failing completely. The user sees generic recommendations instead of nothing.

```python
# More sophisticated: cache the last-known-good result
_cache: dict[str, list] = {}

def get_recommendations(user_id: str) -> list:
    try:
        result = recommendations_api.fetch(user_id)
        _cache[user_id] = result                        # ← update cache on success
        return result
    except Exception as e:
        logger.warning("Using stale cache for %s: %s", user_id, e)
        return _cache.get(user_id, FALLBACK_RECOMMENDATIONS)
```

**Why:** Graceful degradation is a production resilience pattern. A payment page that shows no recommendations is better than a payment page that crashes. Always decide: "what is the acceptable degraded experience?" and implement that as the fallback.
</details>

---

<a id="q24"></a>

### Q24 · Anti-pattern Fix — Silent except Exception: pass

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)



🟡 Intermediate

Why is the following code dangerous? Rewrite it with correct error handling.

```python
def save_record(record):
    try:
        db.insert(record)
    except Exception:
        pass
```

<details>
<summary>💡 Hint</summary>
What does the caller believe happened after `save_record` returns? What actually might have happened?
</details>

<details>
<summary>✅ Answer</summary>

```python
import logging

logger = logging.getLogger(__name__)

def save_record(record):
    try:
        db.insert(record)
    except Exception as e:
        logger.error("Failed to save record %s: %s", record.id, e, exc_info=True)
        raise   # ← or return False / raise a domain error — but never silently pass
```

**Why this is dangerous:** The caller calls `save_record(record)` and receives `None` (the default return). The caller assumes the record was saved. It was not. The data is lost. No log. No alert. No traceback. You will discover the bug weeks later when someone notices missing records, with no clue when or why it started.

The rule: **silent failures are worse than crashes.** A crash stops the system and demands attention. A silent failure lets the system continue in a broken state while data silently disappears.

Options in order of preference:
1. Re-raise (let the caller decide how to handle it)
2. Log and return a typed sentinel (`False`, `None`, a `Result` type) so the caller can check
3. Log and raise a domain exception (`RecordSaveError`)

Never option 4: `pass`.
</details>

---

<a id="q25"></a>

### Q25 · Catching Too Broadly Masks a Bug

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)



🟡 Intermediate

The following code has a bug hidden by a broad `except`. Identify the bug and show what happens when you narrow the `except` clause.

```python
def process_items(items):
    results = []
    for item in items:
        try:
            results.append(item["value"] * 2)
        except Exception:
            results.append(0)
    return results

process_items([{"value": 10}, {"vale": 5}, {"value": 20}])
# Returns [20, 0, 40] — looks fine?
```

<details>
<summary>💡 Hint</summary>
The second item has a typo in the key name. The broad `except` silently converts this programmer error into a `0`.
</details>

<details>
<summary>✅ Answer</summary>

```python
# The bug: {"vale": 5} — typo, should be "value"
# item["value"] raises KeyError, which is caught and silently replaced with 0

# With narrowed except:
def process_items(items):
    results = []
    for item in items:
        try:
            results.append(item["value"] * 2)
        except KeyError:
            # Still too broad if KeyError is a programmer error
            # Better: don't catch it at all if the schema should always have "value"
            raise ValueError(f"Item missing 'value' key: {item}") from None
    return results

# Or: don't try/except at all — let KeyError propagate and fail loudly
def process_items(items):
    return [item["value"] * 2 for item in items]   # ← KeyError propagates immediately
```

The original returned `[20, 0, 40]`. The caller sees a list of numbers and assumes success. The typo in the data is invisible.

**Why:** Broad exception handlers in data processing loops convert data errors into silently corrupted output. The corruption propagates downstream — stored in databases, sent to users, used in calculations — until someone notices the wrong numbers weeks later. Never swallow data errors in a loop; let them fail loudly.
</details>

---

<a id="q26"></a>

### Q26 · Anti-pattern — Exceptions for Control Flow

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)



🟡 Intermediate

The following code uses an exception to signal a normal condition (end of input). Rewrite it using a return value instead. Explain when exceptions are appropriate vs when they are not.

```python
def get_next_item(queue):
    if len(queue) == 0:
        raise StopIteration("Queue is empty")
    return queue.pop(0)

# Caller
while True:
    try:
        item = get_next_item(queue)
        process(item)
    except StopIteration:
        break
```

<details>
<summary>💡 Hint</summary>
An empty queue is a normal, expected condition — not an error. Use a sentinel return value or `None`.
</details>

<details>
<summary>✅ Answer</summary>

```python
def get_next_item(queue):
    if len(queue) == 0:
        return None             # ← normal condition, not an error
    return queue.pop(0)

# Caller
while True:
    item = get_next_item(queue)
    if item is None:            # ← check return value, no exception overhead
        break
    process(item)
```

**When exceptions are appropriate:** Genuinely exceptional, unexpected conditions — file not found, network timeout, invalid input that violates a contract.

**When exceptions are not appropriate:** Normal control flow — empty collections, "not found" in a lookup (use `None` or `Optional`), end of iteration (unless you are implementing the iterator protocol, where `StopIteration` is the correct mechanism).

The cost of raising and catching exceptions in Python is non-trivial (stack unwinding, frame inspection). Using them for loop control is a performance anti-pattern and a readability anti-pattern: readers expect exceptions to signal errors, not normal termination.

**Why:** Code that uses exceptions for normal control flow trains readers to ignore exceptions defensively, which leads to the exact opposite problem — exceptions that signal real errors going unnoticed.
</details>

---

<a id="q27"></a>

### Q27 · Anti-pattern — Losing the Original Exception

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)



🟡 Intermediate

Identify the problem in this code and fix it using `raise...from`.

```python
def load_user(user_id):
    try:
        raw = db.fetch_raw(user_id)
        return User.from_dict(raw)
    except Exception as e:
        raise RuntimeError("Failed to load user")   # ← problem here
```

<details>
<summary>💡 Hint</summary>
When you raise a new exception inside an `except` block without `from e`, Python sets `__context__` implicitly, but the link can be confusing. More importantly, you lose the type and details of the original error.
</details>

<details>
<summary>✅ Answer</summary>

```python
def load_user(user_id):
    try:
        raw = db.fetch_raw(user_id)
        return User.from_dict(raw)
    except Exception as e:
        raise RuntimeError("Failed to load user") from e   # ← explicit chain
```

Without `from e`, Python still implicitly chains (`__context__`), but the connection is shown as "During handling of the above exception, another exception occurred" rather than "The above exception was the direct cause." This is a weaker link and can be confusing.

More critically: the original `raise RuntimeError("Failed to load user")` swallows all type information. Was it a `DatabaseConnectionError`? A `ValidationError` in `User.from_dict`? The caller and the engineer reading the log have no idea.

With `from e`:
```
# Traceback shows both:
DatabaseConnectionError: connection refused   ← original cause
The above exception was the direct cause of the following exception:
RuntimeError: Failed to load user            ← translated error
```

**Why:** In production debugging, the original exception type and message are essential. Losing them means every error looks identical: "Failed to load user." With chaining, you know immediately whether it was a database connectivity issue, a data validation issue, or something else.
</details>

---

<a id="q28"></a>

### Q28 · Exceptions in Threads — Silently Lost

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)



🟠 Advanced

Explain why exceptions raised in a `threading.Thread` are silently lost by default. Then show how to capture and re-raise them in the main thread.

<details>
<summary>💡 Hint</summary>
Each thread has its own call stack. An unhandled exception in a thread does not propagate to the thread that called `.start()`. You must explicitly ferry it across.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading

# Silent failure — exception disappears
def bad_worker():
    raise ValueError("something broke")

t = threading.Thread(target=bad_worker)
t.start()
t.join()
# No exception in main thread. ValueError printed to stderr, then gone.
```

```python
# Fix: capture exception and re-raise in main thread
import threading

class ExceptionCapturingThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exception = None

    def run(self):
        try:
            super().run()
        except Exception as e:
            self.exception = e          # ← store the exception

    def join(self, *args, **kwargs):
        super().join(*args, **kwargs)
        if self.exception:
            raise self.exception        # ← re-raise in the calling thread


def worker():
    raise ValueError("something broke")

t = ExceptionCapturingThread(target=worker)
t.start()
t.join()   # ← raises ValueError here in the main thread
```

**Modern alternative: `concurrent.futures.ThreadPoolExecutor`**

```python
from concurrent.futures import ThreadPoolExecutor

def worker():
    raise ValueError("something broke")

with ThreadPoolExecutor() as executor:
    future = executor.submit(worker)
    future.result()   # ← raises ValueError here — exception is stored in the Future
```

**Why:** `ThreadPoolExecutor` and `asyncio` tasks both store exceptions and re-raise them when you retrieve the result. Prefer these over raw `threading.Thread` for work that can fail.
</details>

---

<a id="q29"></a>

### Q29 · Read a Traceback

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)



🟡 Intermediate

Given this traceback, identify: (a) where the exception was originally raised, (b) what the propagation path was, (c) what the root cause is.

```
Traceback (most recent call last):
  File "app.py", line 42, in handle_request
    result = process_payment(amount)
  File "payments.py", line 18, in process_payment
    charge = calculate_fee(amount)
  File "payments.py", line 31, in calculate_fee
    return amount / rate
ZeroDivisionError: division by zero
```

<details>
<summary>💡 Hint</summary>
Read tracebacks from bottom to top: the bottom is where it was raised, the top is where Python caught it (or where it propagated to).
</details>

<details>
<summary>✅ Answer</summary>

**(a) Where raised:** `payments.py`, line 31, inside `calculate_fee` — `return amount / rate`

**(b) Propagation path:**
```
calculate_fee (raised here)
  ↑ propagated to
process_payment (no handler)
  ↑ propagated to
handle_request (no handler, or this is where the traceback was printed)
```

**(c) Root cause:** `rate` is zero when `calculate_fee` is called. This is a division by zero. The root cause is either (1) `rate` was never initialized, (2) `rate` was set to 0 by a previous calculation, or (3) the caller passed `rate=0`.

**How to read a traceback:**
1. Bottom line: exception type and message — the `what`
2. Line above: the exact line of code that raised — the `where`
3. Read upward: each frame is one level of the call stack — the `how did we get here`
4. Top frame: the entry point (request handler, test, `if __name__ == "__main__"`)

**Why:** Reading tracebacks efficiently is the single most time-saving debugging skill. The most common mistake is reading only the top or only the bottom. You need both: the root cause (bottom) and the execution context (top frames) to understand why the bad state was reached.
</details>

---

<a id="q30"></a>

### Q30 · as e Scope — When Does the Binding Get Cleared?

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)



🟡 Intermediate

What does this code print, and why?

```python
try:
    raise ValueError("test")
except ValueError as e:
    print(e)

print(e)   # ← what happens here?
```

<details>
<summary>💡 Hint</summary>
Python has a specific scoping rule for the `as` variable in `except` clauses. It differs from normal variable assignment scope.
</details>

<details>
<summary>✅ Answer</summary>

```python
try:
    raise ValueError("test")
except ValueError as e:
    print(e)   # "test" — works fine inside the block

print(e)   # NameError: name 'e' is not defined
```

**Python explicitly deletes the `as` variable when the `except` block exits.** This is documented behavior (PEP 3110): the exception object is deleted at the end of the `except` clause to break reference cycles (exception objects hold references to stack frames, which hold references to local variables).

```python
# If you need e outside the block, save it first:
saved_exc = None
try:
    raise ValueError("test")
except ValueError as e:
    saved_exc = e           # ← copy the reference before it gets deleted

print(saved_exc)            # works: ValueError('test')
```

This also applies to the `except (TypeError, ValueError) as e` form — `e` is deleted in both cases.

**Why:** This is a common gotcha. Code that accesses `e` after the `except` block will always raise `NameError`, even though `e` was clearly defined a few lines above. Knowing why (reference cycle prevention) helps you remember the fix: assign to a different variable inside the block.
</details>

---

<a id="q31"></a>

### Q31 · Exception Translation

> 🛠️ **Solve locally:** [practice_local.py → Q31](./practice_local.py)



🟠 Advanced

Write a function `call_user_api(user_id)` that wraps a `requests.get()` call. Translate `requests.HTTPError` into a domain-specific `ApiError` (define it). Preserve the HTTP status code as an attribute. Chain the original exception.

<details>
<summary>💡 Hint</summary>
Catch `requests.HTTPError`, extract `e.response.status_code`, create `ApiError(message, status_code)`, and `raise ... from e`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import requests

class ApiError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code

def call_user_api(user_id: str) -> dict:
    url = f"https://api.example.com/users/{user_id}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()         # ← raises HTTPError for 4xx/5xx
        return response.json()
    except requests.HTTPError as e:
        status = e.response.status_code
        raise ApiError(
            f"User API returned {status} for user {user_id}",
            status_code=status
        ) from e                            # ← chain: preserves original HTTPError
    except requests.Timeout as e:
        raise ApiError("User API timed out", status_code=504) from e
    except requests.ConnectionError as e:
        raise ApiError("Cannot reach User API", status_code=503) from e
```

```python
# Caller
try:
    user = call_user_api("abc123")
except ApiError as e:
    if e.status_code == 404:
        return default_user()
    raise   # propagate unexpected errors
```

Exception translation is the **anti-corruption layer** pattern from DDD: the domain code never sees library-specific exceptions. If you swap `requests` for `httpx`, only `call_user_api` changes — callers remain untouched.

**Why:** Without translation, every caller that uses `call_user_api` must know about `requests.HTTPError`, import `requests`, and handle requests-specific error shapes. Translation centralizes that coupling to one place.
</details>

---

<a id="q32"></a>

### Q32 · finally Always Runs — Resource Release

> 🛠️ **Solve locally:** [practice_local.py → Q32](./practice_local.py)



🟡 Intermediate

Demonstrate a case where `finally` is essential for correctness: acquiring a lock. Show what goes wrong without it, and the correct version with `finally`.

<details>
<summary>💡 Hint</summary>
If an exception is raised while a lock is held, without `finally` the lock is never released and all other threads block forever.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading

lock = threading.Lock()
shared_data = []

# WRONG — lock never released on exception
def append_item_broken(item):
    lock.acquire()
    shared_data.append(int(item))   # ← raises ValueError if item is "bad"
    lock.release()                  # ← never reached if exception raised above

# CORRECT — finally guarantees release
def append_item(item):
    lock.acquire()
    try:
        shared_data.append(int(item))
    finally:
        lock.release()              # ← always runs, even if int(item) raises

# Best — use the lock as a context manager
def append_item_best(item):
    with lock:                      # ← __exit__ calls release() unconditionally
        shared_data.append(int(item))
```

Without `finally`, a single call with a bad `item` permanently deadlocks every thread waiting on the lock. The process must be restarted.

**Why:** This pattern applies to any resource that must be released: file handles, database connections, semaphores, network sockets, GPU memory. `finally` is the foundational primitive; context managers (`with`) are the ergonomic layer built on top of it.
</details>

---

<a id="q33"></a>

### Q33 · ExceptionGroup (Python 3.11+)

> 🛠️ **Solve locally:** [practice_local.py → Q33](./practice_local.py)



🟡 Intermediate

What problem does `ExceptionGroup` solve? When do multiple exceptions need to be raised simultaneously? Show a minimal example using `except*` syntax.

<details>
<summary>💡 Hint</summary>
`asyncio.gather()` can run multiple tasks concurrently. If several of them fail, you want to report all failures — not just the first one.
</details>

<details>
<summary>✅ Answer</summary>

**The problem:** Before Python 3.11, if you ran 5 async tasks concurrently and 3 of them failed, you could only raise one exception. The other 2 failures were lost or awkwardly attached.

`ExceptionGroup` is a container that holds multiple exceptions and propagates all of them together.

```python
# Python 3.11+

# Raising an ExceptionGroup
def validate_all(items):
    errors = []
    for item in items:
        if item < 0:
            errors.append(ValueError(f"negative value: {item}"))
        if item > 100:
            errors.append(ValueError(f"value too large: {item}"))
    if errors:
        raise ExceptionGroup("validation errors", errors)  # ← all errors at once

# Catching with except* (new syntax — note the asterisk)
try:
    validate_all([5, -1, 200, -3])
except* ValueError as eg:
    for exc in eg.exceptions:
        print(f"  - {exc}")

# Output:
#   - negative value: -1
#   - value too large: 200
#   - negative value: -3
```

`except*` is a new clause that matches all exceptions of the given type within the group, collecting them into a new `ExceptionGroup` bound to the `as` variable.

**Why:** `asyncio.TaskGroup` (also 3.11+) raises an `ExceptionGroup` when multiple tasks fail. Without `ExceptionGroup`, concurrent failure reporting required complex workarounds. Now it is a first-class language feature.
</details>

---

<a id="q34"></a>

### Q34 · Capstone — safe_api_call

> 🛠️ **Solve locally:** [practice_local.py → Q34](./practice_local.py)



🟠 Advanced

Write a `safe_api_call(fn, *args, retries=3, fallback=None, **kwargs)` function. It should: retry `fn` up to `retries` times on `Exception`, wait 1 second between retries, log each failure, and return `fallback` if all retries are exhausted.

<details>
<summary>💡 Hint</summary>
No decorator this time — it is a plain function that accepts a callable. Combine retry logic with graceful degradation.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time
import logging

logger = logging.getLogger(__name__)

def safe_api_call(fn, *args, retries=3, fallback=None, **kwargs):
    """
    Call fn(*args, **kwargs) with retry and graceful degradation.

    Returns the function's result on success, or `fallback` if all
    retries are exhausted.
    """
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            return fn(*args, **kwargs)          # ← success: return immediately
        except Exception as e:
            last_exc = e
            logger.warning(
                "safe_api_call: %s attempt %d/%d failed: %s",
                fn.__name__, attempt, retries, e
            )
            if attempt < retries:
                time.sleep(1)                   # ← wait before next attempt

    logger.error(
        "safe_api_call: %s exhausted %d retries. Returning fallback. Last error: %s",
        fn.__name__, retries, last_exc
    )
    return fallback                             # ← graceful degradation


# Usage
result = safe_api_call(
    fetch_user_profile,
    user_id="u123",
    retries=3,
    fallback={"name": "Unknown", "avatar": DEFAULT_AVATAR}
)
```

```python
# Test it locally:
def flaky():
    import random
    if random.random() < 0.7:
        raise ConnectionError("timeout")
    return {"data": 42}

result = safe_api_call(flaky, retries=5, fallback={"data": 0})
print(result)
```

**Why:** This function combines three production patterns: retry (handle transient failures), exponential-backoff-lite (fixed 1s delay here, easily extended), and graceful degradation (return fallback instead of crashing). It is a building block used in data pipelines, API gateways, and background workers.
</details>

---

<a id="q35"></a>

### Q35 · Capstone — Payment System Exception Hierarchy

> 🛠️ **Solve locally:** [practice_local.py → Q35](./practice_local.py)



🟠 Advanced

Design a complete exception hierarchy for a payment processing system. Requirements:
- A base `PaymentError` that all payment exceptions inherit from
- At least 3 levels of hierarchy
- Each leaf exception must carry relevant structured attributes
- Show how different layers of the application use each level

<details>
<summary>💡 Hint</summary>
Level 1: `PaymentError`. Level 2: categories (`ChargeError`, `FraudError`, `NetworkError`). Level 3: specific cases (`InsufficientFundsError`, `CardExpiredError`, `FraudSuspicionError`).
</details>

<details>
<summary>✅ Answer</summary>

```python
# ─── Level 1: Base ───────────────────────────────────────────────────────────
class PaymentError(Exception):
    """Base class for all payment domain errors."""
    def __init__(self, message: str, transaction_id: str | None = None):
        super().__init__(message)
        self.transaction_id = transaction_id


# ─── Level 2: Categories ─────────────────────────────────────────────────────
class ChargeError(PaymentError):
    """Card/account-level charge failures."""
    pass

class FraudError(PaymentError):
    """Fraud detection triggered."""
    pass

class NetworkError(PaymentError):
    """Infrastructure/connectivity failures — potentially retryable."""
    retryable = True


# ─── Level 3: Specific exceptions ────────────────────────────────────────────
class InsufficientFundsError(ChargeError):
    def __init__(self, balance: float, amount: float, transaction_id=None):
        super().__init__(
            f"Insufficient funds: balance={balance:.2f}, required={amount:.2f}",
            transaction_id
        )
        self.balance = balance
        self.amount = amount

class CardExpiredError(ChargeError):
    def __init__(self, expiry: str, transaction_id=None):
        super().__init__(f"Card expired: {expiry}", transaction_id)
        self.expiry = expiry

class CardDeclinedError(ChargeError):
    def __init__(self, decline_code: str, transaction_id=None):
        super().__init__(f"Card declined: {decline_code}", transaction_id)
        self.decline_code = decline_code

class FraudSuspicionError(FraudError):
    def __init__(self, risk_score: float, transaction_id=None):
        super().__init__(
            f"Transaction flagged: risk_score={risk_score:.2f}",
            transaction_id
        )
        self.risk_score = risk_score

class GatewayTimeoutError(NetworkError):
    def __init__(self, gateway: str, transaction_id=None):
        super().__init__(f"Gateway timeout: {gateway}", transaction_id)
        self.gateway = gateway
```

```python
# ─── Usage at different application layers ────────────────────────────────────

# Deep layer: payment processor raises specific exceptions
def charge_card(card, amount, tx_id):
    if card.is_expired():
        raise CardExpiredError(card.expiry, transaction_id=tx_id)
    if account.balance < amount:
        raise InsufficientFundsError(account.balance, amount, transaction_id=tx_id)

# API layer: handles categories
def payment_endpoint(request):
    try:
        charge_card(request.card, request.amount, request.tx_id)
    except InsufficientFundsError as e:
        return {"status": 402, "error": "insufficient_funds", "balance": e.balance}
    except CardExpiredError as e:
        return {"status": 400, "error": "card_expired", "expiry": e.expiry}
    except FraudError as e:
        return {"status": 403, "error": "fraud_detected"}
    except NetworkError as e:
        if e.retryable:
            return {"status": 503, "error": "try_again"}
        raise
    except PaymentError as e:
        # Catch-all for any new PaymentError subclasses added in the future
        logger.error("Unhandled payment error: %s", e, exc_info=True)
        return {"status": 500, "error": "payment_failed"}

# Monitoring layer: catches everything for alerting
def run_batch_payments(payments):
    for p in payments:
        try:
            process(p)
        except FraudError as e:
            alert_fraud_team(e)
        except PaymentError as e:
            increment_metric("payment.errors", tags={"type": type(e).__name__})
```

**Why:** This hierarchy gives every layer of the application exactly the right level of specificity. The API layer handles user-facing errors specifically. The monitoring layer catches all payment errors generically for metrics. New error types added later automatically integrate at the right level without changing existing handlers.
</details>

---

## Navigation

**[Back to theory.md](./theory.md)**

**Deep dives:** [01 Exception Mechanics](./01_exception_mechanics/theory.md) · [02 Custom Exceptions](./02_custom_exceptions/theory.md) · [03 Production Patterns](./03_production_patterns/theory.md)

**Related:** [cheetsheet.md](./cheetsheet.md) · [interview.md](./interview.md)
