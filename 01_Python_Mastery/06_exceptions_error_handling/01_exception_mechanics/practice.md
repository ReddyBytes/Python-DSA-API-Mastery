# Exception Mechanics — Practice

> 15 problems · Deep dive on how Python raises, catches, and re-raises exceptions
> Write your answers in `practice_local.py` first, then use the dropdowns.

---

## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| [Q1](#q1) | Call stack propagation — trace where the handler is | 🟢 |
| [Q2](#q2) | Full try/except/else/finally for division with cleanup | 🟢 |
| [Q3](#q3) | Predict output — else only on no-exception path | 🟡 |
| [Q4](#q4) | Predict output — return in finally swallows exception | 🟡 |
| [Q5](#q5) | Predict output — return in try vs return in finally | 🟡 |
| [Q6](#q6) | Exception hierarchy — which clause catches int("x")? | 🟡 |
| [Q7](#q7) | Order bug — broad except before specific, fix it | 🟡 |
| [Q8](#q8) | Catch multiple exceptions in one clause | 🟡 |
| [Q9](#q9) | Log and re-raise without swallowing | 🟡 |
| [Q10](#q10) | raise ValueError from KeyError — traceback shape | 🟡 |
| [Q11](#q11) | raise X from None — when to suppress the chain | 🟡 |
| [Q12](#q12) | Rewrite LBYL as EAFP | 🟡 |
| [Q13](#q13) | When LBYL is actually better — race condition scenario | 🟡 |
| [Q14](#q14) | Read a traceback — root cause, path, fix | 🟠 |
| [Q15](#q15) | Multiple handlers — ZeroDivisionError, ValueError, fallthrough | 🟠 |

---

<a id="q1"></a>

### Q1 🟢 · propagation — Where does it land?

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)



**Problem:**
Three functions are nested: `main` calls `middle`, `middle` calls `inner`. `inner` raises a `ValueError`. A `try/except ValueError` block exists only in `main`. Trace the propagation path and explain where the exception is caught and why.

```python
def inner():
    raise ValueError("bad input")

def middle():
    inner()

def main():
    try:
        middle()
    except ValueError as e:
        print(f"caught in main: {e}")

main()
```

**Your answer:** *(write your trace in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Python checks the current frame first. If no handler there, it pops the frame and checks the caller. Repeat until a handler is found or the stack is empty.

</details>

<details>
<summary>✅ Answer</summary>

```
inner()  → raises ValueError — no handler here → frame popped
middle() → no handler here   → frame popped
main()   → try/except found  → except block runs
```

Output: `caught in main: bad input`

**Why:** Exception propagation walks the call stack from innermost to outermost. `inner` and `middle` both have no `try/except`, so their frames are discarded and the exception travels up. `main` has the matching handler, so the `except ValueError` block runs there.

</details>

---

<a id="q2"></a>

### Q2 🟢 · try/except/else/finally — Division with cleanup

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)



**Problem:**
Write a function `safe_divide(a, b)` that:
- Attempts `a / b`
- Catches `ZeroDivisionError` and returns `None`
- If division succeeds, prints `"result: {value}"` (in the `else` block)
- Always prints `"done"` in `finally`
- Returns the result on success

```python
def safe_divide(a, b):
    # your code here
    pass
```

<details>
<summary>💡 Hint</summary>

Use all four clauses. The `else` block runs only when `try` completes without raising. `finally` runs regardless of what happened.

</details>

<details>
<summary>✅ Answer</summary>

```python
def safe_divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("cannot divide by zero")
        return None
    else:
        print(f"result: {result}")
        return result
    finally:
        print("done")

safe_divide(10, 2)
# result: 10.0
# done

safe_divide(10, 0)
# cannot divide by zero
# done
```

**Why:** `else` scopes success-path code away from the `except` block — exceptions raised in `else` are not caught by this `except`. `finally` runs in both paths, making it the right place for cleanup (closing files, releasing locks, etc.).

</details>

---

<a id="q3"></a>

### Q3 🟡 · predict output — else only on success path

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)



**Problem:**
What does this print? Predict before running.

```python
for val in ["10", "bad", "5"]:
    try:
        n = int(val)
    except ValueError:
        print(f"skipped: {val}")
    else:
        print(f"parsed: {n}")
```

<details>
<summary>💡 Hint</summary>

`else` runs when `try` completes without raising. `except` runs when it does raise. They are mutually exclusive per iteration.

</details>

<details>
<summary>✅ Answer</summary>

```
parsed: 10
skipped: bad
parsed: 5
```

**Why:** For `"10"` — `int()` succeeds, no exception, `else` runs. For `"bad"` — `int()` raises `ValueError`, `except` runs, `else` is skipped. For `"5"` — `int()` succeeds again, `else` runs. `else` and `except` are mutually exclusive for each `try` block.

</details>

---

<a id="q4"></a>

### Q4 🟡 · predict output — return in finally swallows exception

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)



**Problem:**
What does this print? Does it raise?

```python
def tricky():
    try:
        raise RuntimeError("exploded")
    finally:
        return "survived"

print(tricky())
```

<details>
<summary>💡 Hint</summary>

`finally` always runs. What happens when `finally` contains a `return` and an exception is active?

</details>

<details>
<summary>✅ Answer</summary>

```
survived
```

No exception is raised. The `RuntimeError` is silently discarded.

**Why:** When `finally` executes a `return`, it takes precedence over everything — including an active exception. The exception is suppressed without any traceback or warning. This is almost always a bug. Avoid `return` in `finally` unless you explicitly want to swallow exceptions.

</details>

---

<a id="q5"></a>

### Q5 🟡 · predict output — return in try vs return in finally

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)



**Problem:**
Which `return` wins?

```python
def which_wins():
    try:
        print("try")
        return "from try"
    finally:
        print("finally")
        return "from finally"

print(which_wins())
```

<details>
<summary>💡 Hint</summary>

`finally` runs before the function actually returns, even if `try` already hit a `return`.

</details>

<details>
<summary>✅ Answer</summary>

```
try
finally
from finally
```

**Why:** Python evaluates `return "from try"` in `try`, but before actually returning, it runs `finally`. The `return "from finally"` in `finally` replaces the earlier return value. The caller receives `"from finally"`. This is rarely the intended behavior — it's a footgun.

</details>

---

<a id="q6"></a>

### Q6 🟡 · exception hierarchy — which clause catches int("x")?

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)



**Problem:**
`int("x")` raises an exception. Which of the following `except` clauses would catch it? Explain why using the hierarchy.

```python
# Option A
except TypeError: ...

# Option B
except ValueError: ...

# Option C
except LookupError: ...

# Option D
except Exception: ...
```

<details>
<summary>💡 Hint</summary>

`int("x")` receives a value of the wrong *value* (non-numeric string), not the wrong type. Check the hierarchy: where does `ValueError` sit under `Exception`?

</details>

<details>
<summary>✅ Answer</summary>

**B and D** both catch it. `int("x")` raises `ValueError`.

- A — `TypeError` is for wrong type (e.g., `int([])`). Doesn't catch it.
- B — `ValueError` is exact match. Catches it.
- C — `LookupError` is for `IndexError`/`KeyError`. Doesn't catch it.
- D — `Exception` is the base of all non-system exceptions. Catches it.

**Why:** `except` uses `isinstance` matching. `isinstance(ValueError("x"), Exception)` is `True` because `ValueError` is a subclass of `Exception`. Always catch the most specific exception you can handle — catching `Exception` blindly hides bugs.

</details>

---

<a id="q7"></a>

### Q7 🟡 · order bug — broad except before specific

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)



**Problem:**
This code has a bug. The specific handler never runs. Identify the bug and fix it.

```python
def parse(value):
    try:
        return int(value)
    except Exception:
        print("something went wrong")
    except ValueError:
        print("not a valid integer")   # this never runs — why?
```

<details>
<summary>💡 Hint</summary>

Python checks `except` clauses top to bottom and stops at the first match. What does `isinstance(ValueError(...), Exception)` return?

</details>

<details>
<summary>✅ Answer</summary>

```python
def parse(value):
    try:
        return int(value)
    except ValueError:               # ← specific first
        print("not a valid integer")
    except Exception:                # ← broad fallback last
        print("something went wrong")
```

**Why:** `ValueError` is a subclass of `Exception`, so the broad `except Exception` clause matches it first and `except ValueError` is never reached. Always order `except` clauses from most specific to most general. Python does not warn you about unreachable handlers.

</details>

---

<a id="q8"></a>

### Q8 🟡 · catch multiple in one clause — tuple syntax

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)



**Problem:**
Write a function `read_value(d, key)` that catches both `KeyError` (key not in dict) and `TypeError` (d is not subscriptable) in a single `except` clause and returns `None` for both cases.

```python
def read_value(d, key):
    # your code here
    pass
```

<details>
<summary>💡 Hint</summary>

Use a tuple of exception types in the `except` clause: `except (TypeA, TypeB)`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def read_value(d, key):
    try:
        return d[key]
    except (KeyError, TypeError):
        return None

print(read_value({"a": 1}, "a"))    # 1
print(read_value({"a": 1}, "z"))    # None  (KeyError)
print(read_value(None, "a"))        # None  (TypeError)
```

**Why:** `except (A, B)` catches either type. Use this when both errors represent the same failure mode and you'd handle them identically. Don't use it as a shortcut to avoid thinking — if the two errors require different handling, use separate clauses.

</details>

---

<a id="q9"></a>

### Q9 🟡 · re-raise — log and re-raise without swallowing

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)



**Problem:**
Write a function `fetch_data(url)` that calls `requests.get(url)`, logs any `requests.exceptions.RequestException` to stderr, and then re-raises it — without swallowing the original traceback. (You don't need to actually import requests — write the structure.)

```python
import sys

def fetch_data(url):
    try:
        # imagine: response = requests.get(url)
        raise requests.exceptions.RequestException("timeout")
    except Exception as e:
        # log it, then re-raise
        # your code here
        pass
```

<details>
<summary>💡 Hint</summary>

Bare `raise` re-raises the current exception with its original traceback intact. Do not write `raise e` — that resets the traceback origin.

</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

def fetch_data(url):
    try:
        response = requests.get(url)
        return response
    except Exception as e:
        print(f"ERROR: fetch failed for {url}: {e}", file=sys.stderr)
        raise    # ← bare raise, not raise e
```

**Why:** Bare `raise` preserves the original traceback, so the caller sees exactly where the error originated. `raise e` creates a new traceback starting at the current line, losing the original context. In production logging pipelines, this distinction matters for root-cause analysis.

</details>

---

<a id="q10"></a>

### Q10 🟡 · raise X from Y — what does the traceback look like?

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)



**Problem:**
Run this code mentally and describe the traceback output shape. What two exceptions appear, and in what order?

```python
def load_config(path):
    try:
        data = {}
        value = data[path]        # KeyError
    except KeyError as e:
        raise ValueError(f"config key not found: {path}") from e

load_config("timeout")
```

<details>
<summary>💡 Hint</summary>

`raise X from Y` sets `__cause__` on the new exception. Python prints both exceptions in the traceback, with the cause shown first.

</details>

<details>
<summary>✅ Answer</summary>

```
Traceback (most recent call last):
  File "...", line 4, in load_config
    value = data[path]
KeyError: 'timeout'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "...", line 9, in <module>
    load_config("timeout")
  File "...", line 6, in load_config
    raise ValueError(f"config key not found: {path}") from e
ValueError: config key not found: timeout
```

**Why:** `raise X from Y` creates explicit exception chaining. Python prints the original cause first, then the new exception, separated by "The above exception was the direct cause of the following exception:". Read bottom-up within each block, top-to-bottom across blocks: cause first, effect last.

</details>

---

<a id="q11"></a>

### Q11 🟡 · raise X from None — when to suppress the chain

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)



**Problem:**
You're building a database abstraction layer. Your internal implementation uses `psycopg2`. You want callers to see only your clean `DatabaseError`, not psycopg2 internals. Write the function and explain why `from None` is the right choice here.

```python
class DatabaseError(Exception):
    pass

def get_user(user_id):
    try:
        # imagine: result = db.execute(...)
        raise Exception("psycopg2.OperationalError: connection refused")
    except Exception as e:
        # your code here — raise DatabaseError without leaking the original
        pass
```

<details>
<summary>💡 Hint</summary>

`raise X from None` suppresses the `__context__` chain — callers see only the new exception with no "caused by" block.

</details>

<details>
<summary>✅ Answer</summary>

```python
class DatabaseError(Exception):
    pass

def get_user(user_id):
    try:
        result = db.execute(f"SELECT * FROM users WHERE id = {user_id}")
        return result
    except Exception:
        raise DatabaseError("database unavailable") from None
```

Traceback callers see:
```
DatabaseError: database unavailable
```

No psycopg2 details, no internal stack frames from the DB driver.

**Why:** `from None` sets `__suppress_context__ = True`, which hides the original exception from the traceback. Use it when the original exception is an implementation detail that would confuse callers or leak your internal dependencies. Never use it to hide bugs you haven't handled.

</details>

---

<a id="q12"></a>

### Q12 🟡 · LBYL → rewrite as EAFP

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)



**Problem:**
Rewrite this LBYL code as idiomatic Python EAFP style.

```python
import os

def read_config(path):
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    else:
        return None
```

<details>
<summary>💡 Hint</summary>

EAFP: just attempt the operation and handle what goes wrong. What exception does `open()` raise when the file doesn't exist?

</details>

<details>
<summary>✅ Answer</summary>

```python
def read_config(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return None
```

**Why:** The EAFP version is simpler and avoids a TOCTOU (Time Of Check Time Of Use) race condition: in the LBYL version, another process could delete the file between `os.path.exists()` and `open()`. EAFP handles the actual error atomically. It's also more Pythonic — the standard library is designed around this pattern.

</details>

---

<a id="q13"></a>

### Q13 🟡 · EAFP → when LBYL is actually better

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)



**Problem:**
You have a form that asks users to enter a port number (1–65535). Before making a network connection, you want to validate the input. A colleague wrote this:

```python
def connect(port_str):
    try:
        port = int(port_str)
        if not 1 <= port <= 65535:
            raise ValueError
        make_connection(port)
    except ValueError:
        print("invalid port")
    except OSError:
        print("connection failed")
```

Is there a problem with this EAFP-style approach for the validation step specifically? Would LBYL be better here? Explain.

<details>
<summary>💡 Hint</summary>

Think about what the `except ValueError` clause is now catching: both invalid input AND the `int()` conversion failure. Is that a problem? Also consider: is there any race condition risk in validation of user input?

</details>

<details>
<summary>✅ Answer</summary>

The code works but has a subtle issue: the single `except ValueError` catches both `int(port_str)` failures and the explicit `raise ValueError` for out-of-range ports. This makes it harder to give different error messages for "not a number" vs "out of range."

For user input validation, LBYL is cleaner and there's no race condition risk (unlike file checks):

```python
def connect(port_str):
    # LBYL validation for user input — no race condition possible
    if not port_str.isdigit():
        print("port must be a number")
        return
    port = int(port_str)
    if not 1 <= port <= 65535:
        print("port must be between 1 and 65535")
        return

    try:
        make_connection(port)
    except OSError:
        print("connection failed")
```

**Why:** LBYL is appropriate when: (1) the check is cheap, (2) there's no race condition, and (3) you want distinct feedback for distinct failure modes. Pure user-input validation — where you're checking a string before any I/O — is a good fit. Use EAFP for I/O and external state.

</details>

---

<a id="q14"></a>

### Q14 🟠 · read this traceback — root cause, path, fix

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)



**Problem:**
Read this traceback. Identify: (a) the root cause exception, (b) the propagation path from inner to outer, (c) the most likely fix.

```
Traceback (most recent call last):
  File "pipeline.py", line 52, in run_pipeline
    results = process_batch(records)
  File "pipeline.py", line 38, in process_batch
    return [transform(r) for r in records]
  File "pipeline.py", line 38, in <listcomp>
    return [transform(r) for r in records]
  File "pipeline.py", line 21, in transform
    return {"id": r["id"], "value": float(r["amount"])}
  File "pipeline.py", line 21, in transform
KeyError: 'amount'
```

<details>
<summary>💡 Hint</summary>

Read bottom-up: the last line is the exception. The frame above it is where it happened. Work upward to understand the call chain.

</details>

<details>
<summary>✅ Answer</summary>

**(a) Root cause:** `KeyError: 'amount'` — a record is missing the `'amount'` key.

**(b) Propagation path (bottom to top):**
1. `transform(r)` — tried to access `r["amount"]`, key missing → `KeyError` raised
2. List comprehension in `process_batch` — no handler → propagates
3. `process_batch` — no handler → propagates
4. `run_pipeline` — no handler shown → propagates to caller

**(c) Fix options:**

```python
# Option 1 — use .get() with a default
def transform(r):
    return {
        "id": r["id"],
        "value": float(r.get("amount", 0))
    }

# Option 2 — validate and raise a clearer error
def transform(r):
    if "amount" not in r:
        raise ValueError(f"record missing 'amount' field: {r!r}")
    return {"id": r["id"], "value": float(r["amount"])}

# Option 3 — skip bad records in the batch
def process_batch(records):
    results = []
    for r in records:
        try:
            results.append(transform(r))
        except (KeyError, ValueError) as e:
            log.warning(f"skipping record: {e}")
    return results
```

**Why:** The right fix depends on whether missing `amount` is expected (use default or skip) or a data quality bug that should fail loudly (raise with context). Never silently swallow errors unless you've logged them.

</details>

---

<a id="q15"></a>

### Q15 🟠 · multiple handlers — ZeroDivisionError, ValueError, fallthrough

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)



**Problem:**
Write a function `evaluate(expr_str)` that:
- Parses and evaluates a string like `"10 / 2"` or `"10 / 0"` or `"abc / 2"`
- Handles `ZeroDivisionError` → return `"division by zero"`
- Handles `ValueError` → return `"invalid number"`
- Handles any other `Exception` → return `f"unexpected error: {type(e).__name__}"`
- On success → return the float result

Use a simple split-and-parse approach (no `eval`). Demonstrate it catches each case correctly.

```python
def evaluate(expr_str):
    # your code here
    pass

print(evaluate("10 / 2"))    # 5.0
print(evaluate("10 / 0"))    # division by zero
print(evaluate("abc / 2"))   # invalid number
print(evaluate("10 / x"))    # invalid number
```

<details>
<summary>💡 Hint</summary>

Split the string on `" / "` to get left and right parts. Use `float()` to convert. Handle errors in order from specific to general.

</details>

<details>
<summary>✅ Answer</summary>

```python
def evaluate(expr_str):
    try:
        left, right = expr_str.split(" / ")
        a = float(left)
        b = float(right)
        return a / b
    except ZeroDivisionError:
        return "division by zero"
    except ValueError:
        return "invalid number"
    except Exception as e:
        return f"unexpected error: {type(e).__name__}"

print(evaluate("10 / 2"))    # 5.0
print(evaluate("10 / 0"))    # division by zero
print(evaluate("abc / 2"))   # invalid number
print(evaluate("10 / x"))    # invalid number
print(evaluate("10"))        # unexpected error: ValueError  ← split fails
```

**Why:** Order matters. `ZeroDivisionError` and `ValueError` are both subclasses of `Exception`, so they must come before the broad `except Exception` fallback. The fallback catches unexpected structural errors (like a malformed expression that can't be split). Note that `"10"` with no `" / "` actually triggers a `ValueError` from the unpacking — it would hit the `except ValueError` clause, not the fallback.

</details>

---

**[⬆ Back to 06_exceptions](../theory.md)** · **[Master Practice →](../practice.md)**
