# Exception Mechanics — How Python Raises, Catches, and Re-raises

An exception is not a crash — it's a signal that travels up the call stack looking for a handler. Understanding how Python propagates, catches, and re-raises that signal is the foundation of every resilient system.

---

## 📌 Learning Priority

**Must Learn** — Core, used daily:
try/except/else/finally · specific exception types · raise · re-raise

**Should Learn** — Important for real projects:
raise X from Y · raise X from None · EAFP vs LBYL · traceback reading

**Good to Know** — Situational:
sys.exc_info() · warnings module

**Reference** — Know it exists:
ExceptionGroup (3.11+) · signal handlers

---

## Chapter 1: What Happens When Python Raises

Think of the call stack as a stack of plates. Each function call adds a plate on top. When an exception fires, Python picks up the plate on top, looks at it, and asks: "Does this frame have a handler?" If yes — caught. If no — that plate gets thrown away and Python checks the next one down. This keeps going until either a handler is found or the stack is empty, at which point Python prints a traceback and exits.

```
main()          ← plate 1 (bottom)
  └─ parse()    ← plate 2
       └─ int() ← plate 3 (top) — raises ValueError here

Python checks plate 3 → no handler → discard
Python checks plate 2 → no handler → discard
Python checks plate 1 → handler found → except block runs
```

The exception object itself is a regular Python object. It carries:
- `args` — the message(s) passed to it
- `__traceback__` — the traceback chain
- `__cause__` — set by `raise X from Y`
- `__context__` — the exception active when this one was raised (implicit chaining)

```python
try:
    int("oops")
except ValueError as e:
    print(type(e))          # <class 'ValueError'>
    print(e.args)           # ('invalid literal for int() with base 10: \'oops\'',)
    print(e.__traceback__)  # <traceback object at 0x...>
```

---

## Chapter 2: Exception Hierarchy

Python's exception system is a class tree. Every exception is an instance of a class, and `except` clauses match using `isinstance` — so catching a parent class catches all its children.

```
BaseException
├── SystemExit              ← sys.exit() raises this
├── KeyboardInterrupt       ← Ctrl+C
├── GeneratorExit           ← generator.close()
└── Exception               ← almost everything you care about
    ├── StopIteration       ← for loops rely on this
    ├── ArithmeticError
    │   ├── ZeroDivisionError
    │   ├── OverflowError
    │   └── FloatingPointError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── AttributeError
    ├── ImportError
    │   └── ModuleNotFoundError
    ├── OSError
    │   ├── FileNotFoundError
    │   ├── PermissionError
    │   └── TimeoutError
    ├── RuntimeError
    │   └── RecursionError
    ├── TypeError
    ├── ValueError
    │   └── UnicodeError
    ├── NameError
    │   └── UnboundLocalError
    └── ... (many more)
```

Key rule: **never catch `BaseException` unless you have a very specific reason** (like a shutdown hook). `KeyboardInterrupt` and `SystemExit` live there intentionally — swallowing them breaks Ctrl+C and `sys.exit()`.

```python
# BAD — swallows Ctrl+C and sys.exit()
try:
    risky()
except BaseException:
    pass

# GOOD — catches only user-defined errors
try:
    risky()
except Exception:
    pass
```

---

## Chapter 3: try/except/else/finally — Full Anatomy

Four clauses, each with a distinct job. Think of it like a medical triage:
- `try` — the operating room (attempt the risky work)
- `except` — the crash team (handle what went wrong)
- `else` — the recovery room (runs only if the operation succeeded)
- `finally` — the cleanup crew (runs no matter what — success, failure, or even return)

```python
def divide(a, b):
    try:
        result = a / b          # ← risky work
    except ZeroDivisionError:
        print("can't divide by zero")
        return None
    else:
        print(f"success: {result}")   # ← only if try succeeded
        return result
    finally:
        print("cleanup always runs")  # ← always
```

Execution flow table:

| Scenario | try | except | else | finally |
|---|---|---|---|---|
| No exception | runs | skipped | runs | runs |
| Exception raised, caught | partial | runs | skipped | runs |
| Exception raised, not caught | partial | skipped | skipped | runs, then propagates |

**Why `else` matters.** Without `else`, you'd put the success-path code inside `try`, which accidentally catches exceptions raised by that success code. `else` scopes your `except` precisely.

```python
# BAD — process() errors are silently caught by the same except
try:
    data = fetch()
    result = process(data)   # ← this ValueError would be swallowed too
except ValueError:
    log("fetch failed")

# GOOD — except only covers fetch(), not process()
try:
    data = fetch()
except ValueError:
    log("fetch failed")
else:
    result = process(data)   # ← ValueError here propagates normally
```

Multiple `except` clauses are checked top to bottom, first match wins:

```python
try:
    risky()
except FileNotFoundError:
    handle_missing()
except OSError:
    handle_os_error()     # catches all other OSErrors
except Exception:
    handle_anything_else()
```

---

## Chapter 4: finally Edge Cases

`finally` has one surprising behavior: **a `return` inside `finally` swallows any active exception**, and it also overrides any `return` in `try` or `except`.

### Edge case 1: return in finally swallows the exception

```python
def risky():
    try:
        raise ValueError("something broke")
    finally:
        return 42        # ← exception is silently discarded!

result = risky()
print(result)   # 42 — no exception raised, no traceback
```

The exception vanished. This is almost always a bug. Never put a bare `return` in `finally` unless you intentionally want to suppress exceptions.

### Edge case 2: return in try vs return in finally — which wins?

```python
def which_return():
    try:
        return "try"
    finally:
        return "finally"   # ← this wins

print(which_return())  # "finally"
```

`finally` always runs before the function actually returns, so its `return` replaces the earlier one.

### Edge case 3: finally still runs even through continue/break

```python
for i in range(3):
    try:
        if i == 1:
            continue
    finally:
        print(f"finally for i={i}")   # runs on every iteration including the continue
```

Output:
```
finally for i=0
finally for i=1
finally for i=2
```

---

## Chapter 5: raise — Basic, Re-raise, Chaining, Suppression

### Basic raise

```python
raise ValueError("age must be positive")
raise ValueError           # raises with no message (valid, rarely useful)
```

### Re-raise

Inside an `except` block, bare `raise` re-raises the current exception unchanged — traceback and all.

```python
def process(data):
    try:
        return parse(data)
    except ValueError:
        log.error("parse failed")
        raise               # ← re-raises the original ValueError, not a new one
```

This is the correct pattern for "log and re-raise." Do **not** write `raise e` — that resets the traceback to the current line, losing the original location.

```python
# BAD — resets traceback origin
except ValueError as e:
    raise e

# GOOD — preserves original traceback
except ValueError:
    raise
```

### raise X from Y — explicit chaining

Use this when you catch one exception and raise a different one. It attaches the original as `__cause__` and the traceback shows both.

```python
def load_config(path):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise RuntimeError(f"config file missing: {path}") from e
```

Traceback output:
```
FileNotFoundError: [Errno 2] No such file or directory: 'config.json'

The above exception was the direct cause of the following exception:

RuntimeError: config file missing: config.json
```

### raise X from None — suppress the chain

Sometimes you're translating an internal/implementation exception into a clean public-facing one. Showing the original exception leaks internals. `from None` suppresses it.

```python
class DatabaseError(Exception):
    pass

def get_user(user_id):
    try:
        return db.query(f"SELECT * FROM users WHERE id={user_id}")
    except psycopg2.OperationalError:
        raise DatabaseError("database unavailable") from None
```

Callers see only `DatabaseError: database unavailable` — no psycopg2 internals leaked.

---

## Chapter 6: LBYL vs EAFP

Two philosophies for handling uncertainty. Python strongly favors EAFP.

**LBYL — Look Before You Leap**: check conditions before attempting the operation.

```python
# LBYL
if os.path.exists(path):
    with open(path) as f:
        data = f.read()
```

**EAFP — Easier to Ask Forgiveness than Permission**: just attempt the operation and handle what goes wrong.

```python
# EAFP
try:
    with open(path) as f:
        data = f.read()
except FileNotFoundError:
    data = None
```

Python's standard library is designed for EAFP. It's more idiomatic and often faster (one operation instead of two). But LBYL has a legitimate use case: **race conditions**.

```
LBYL race condition:

Thread A: os.path.exists("file") → True
Thread B: os.remove("file")
Thread A: open("file") → FileNotFoundError  ← check was useless
```

EAFP avoids this class of bug because the existence check and the operation are atomic from the perspective of your code.

Rule of thumb: use EAFP by default. Use LBYL only when the pre-check is cheap, atomic, and required for clarity (e.g., validating user input before any I/O).

---

## Chapter 7: Reading Tracebacks

Python tracebacks read **bottom-up**. The last line is the exception. The lines above it are the call chain from outermost (top) to innermost (bottom) — and the actual error is at the bottom.

```
Traceback (most recent call last):
  File "app.py", line 42, in main         ← 3. main called parse_config
    config = parse_config("settings.json")
  File "app.py", line 18, in parse_config ← 2. parse_config called json.load
    return json.load(f)
  File "/usr/lib/python3.11/json/__init__.py", line 293, in load
    return loads(fp.read(),              ← 1. json.load called loads
  File "/usr/lib/python3.11/json/decoder.py", line 337, in JSONDecodeError
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
^--- START HERE — this is the root cause
```

Reading protocol:
1. Read the last line first — that's the exception type and message.
2. Look at the frame just above it — that's where the exception was raised in your code.
3. Work upward to understand the call path.

**Chained exceptions** show multiple blocks separated by "The above exception was the direct cause of the following exception:" — read each block bottom-up, then read the blocks in order (cause first, effect last).

---

## Navigation

**[⬆ Back to 06_exceptions](../theory.md)**

**Prev:** — &nbsp;|&nbsp; **Next:** [02 Custom Exceptions →](../02_custom_exceptions/theory.md)

**Practice:** [practice.md](./practice.md) · [Master →](../practice.md)
