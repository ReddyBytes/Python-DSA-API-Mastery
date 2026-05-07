# 💻 Context Managers — Practice Questions

> 30 questions covering Chapters 1–12 of theory.md.
> Difficulty: 🟢 Beginner · 🟡 Intermediate · 🟠 Advanced

---

## Quick Index

| # | Difficulty | Topic | Skill |
|---|---|---|---|
| [Q1](#q1--with-statement-anatomy--trace-the-5-steps) | 🟢 | with statement | Protocol anatomy |
| [Q2](#q2--open-as-cm--why-files-close-on-exception) | 🟢 | open() as CM | Exception safety |
| [Q3](#q3--__exit__-params--three-params-and-return-true) | 🟢 | __exit__ params | Return True behavior |
| [Q4](#q4--class-based-cm--write-managedfile) | 🟡 | class-based CM | __enter__ / __exit__ |
| [Q5](#q5--suppress-exceptions--write-suppresserrors) | 🟡 | suppress exceptions | Custom suppressor |
| [Q6](#q6--contextlibsuppress--rewrite-tryexceptpass) | 🟢 | contextlib.suppress | Idiomatic rewrite |
| [Q7](#q7--contextmanager--timer-using-generator) | 🟡 | @contextmanager | Generator-based CM |
| [Q8](#q8--contextmanager-resource-leak--spot-and-fix) | 🟡 | @contextmanager | Missing try/finally |
| [Q9](#q9--transaction-cm--commit-on-success-rollback-on-exception) | 🟡 | transaction CM | Exception handling |
| [Q10](#q10--temp_dir-cm--create-and-clean-up-temp-directory) | 🟢 | temp_dir CM | Real-world pattern |
| [Q11](#q11--timing-cm--measure-and-log-elapsed-time) | 🟡 | timing CM | Production pattern |
| [Q12](#q12--acquire_lock-cm--lock-with-timeout) | 🟡 | acquire_lock CM | Timeout pattern |
| [Q13](#q13--redirect_stdout--capture-print-output-to-buffer) | 🟡 | redirect_stdout | Output capture |
| [Q14](#q14--database-connection-cm--auto-commitrollback) | 🟡 | database CM | sqlite3 lifecycle |
| [Q15](#q15--multiple-cms--nested-vs-one-liner) | 🟢 | multiple CMs | Composition styles |
| [Q16](#q16--exit-order--trace-lifo-for-a-b-c) | 🟡 | exit order | LIFO tracing |
| [Q17](#q17--exitstack--merge-n-files-at-runtime) | 🟡 | ExitStack | Dynamic files |
| [Q18](#q18--exitstack-callbacks--register-cleanup-functions) | 🟡 | ExitStack | callback() |
| [Q19](#q19--exitstack-conditional--use-transaction-if-flag-set) | 🟠 | ExitStack | Conditional CM |
| [Q20](#q20--nullcontext--optional-lock-pattern) | 🟡 | nullcontext | Optional CM |
| [Q21](#q21--async-cm--write-asyncdbconnection) | 🟡 | async CM | __aenter__ / __aexit__ |
| [Q22](#q22--asynccontextmanager--write-async_timer) | 🟡 | @asynccontextmanager | Async generator CM |
| [Q23](#q23--gotcha-return-true--fix-accidental-suppression) | 🟡 | gotcha | return True scope |
| [Q24](#q24--gotcha-missing-tryfinal--show-leak-add-fix) | 🟡 | gotcha | try/finally leak |
| [Q25](#q25--gotcha-__enter__-raises--protect-setup) | 🟠 | gotcha | __enter__ safety |
| [Q26](#q26--contextlibclosing--wrap-legacy-object) | 🟡 | contextlib.closing | .close() wrapping |
| [Q27](#q27--audit_log-cm--wrap-with-startenderror-logging) | 🟡 | audit_log CM | Logging pattern |
| [Q28](#q28--exitstack-ownership-transfer--return-stack-to-caller) | 🟠 | ExitStack | Ownership transfer |
| [Q29](#q29--debug-wrong-suppress-scope--fix-overly-broad-suppress) | 🟡 | debug | Suppress scope |
| [Q30](#q30--capstone--build-connectionpool-with-exitstack) | 🟠 | capstone | ConnectionPool class |

---

### Q1 🟢 · with statement anatomy — trace the 5 steps

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

**Problem:** Given the following code:

```python
with open("config.json") as f:
    data = json.load(f)
```

Write out the exact 5-step sequence Python executes under the hood, including what happens when an exception occurs in the body.

<details>
<summary>💡 Hint</summary>

Think about what gets called before the body runs, what happens during the body, and what happens after — both in the success case and the exception case.
</details>

<details>
<summary>✅ Answer</summary>

```python
# Step 1: evaluate the expression to get the context manager object
_cm = open("config.json")

# Step 2: call __enter__() — setup phase; result goes to 'as f'
f = _cm.__enter__()

# Step 3: run the with-block body
# Step 4a (exception): if body raises, call __exit__(type, val, tb)
#   - if __exit__ returns True  → exception is suppressed
#   - if __exit__ returns False → re-raise the exception
# Step 4b (no exception): call __exit__(None, None, None)

try:
    data = json.load(f)       # Step 3
except:
    if not _cm.__exit__(*sys.exc_info()):   # Step 4a
        raise
else:
    _cm.__exit__(None, None, None)          # Step 4b

# Step 5: execution continues after the with block
```

**Why:** `__exit__` is always called regardless of outcome. The only time it is NOT called is if `__enter__` itself raises — because the "with block" never started.
</details>

---

### Q2 🟢 · open() as CM — why files close on exception

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

**Problem:** Explain why the file `f` is guaranteed to be closed in the code below, even if `process(f)` raises a `ValueError`. Then show the fragile version (without a context manager) and explain the difference.

```python
with open("data.txt") as f:
    process(f)
```

<details>
<summary>💡 Hint</summary>

Consider what `open()` returns and what protocol that object implements. What does the file object's `__exit__` do?
</details>

<details>
<summary>✅ Answer</summary>

```python
# Safe version — file.close() is ALWAYS called:
with open("data.txt") as f:
    process(f)   # even if this raises, __exit__ calls f.close()

# Fragile version — f.close() is skipped on exception:
f = open("data.txt")
process(f)       # ← if this raises ValueError...
f.close()        # ← this line is never reached — file handle leaked!

# Manual fix using try/finally (equivalent to what 'with' does):
f = open("data.txt")
try:
    process(f)
finally:
    f.close()    # always runs, but must be written every time
```

**Why:** Python's built-in file objects implement `__exit__`, which calls `self.close()`. When a `ValueError` propagates out of the `with` body, Python calls `f.__exit__(ValueError, ..., ...)` before re-raising, so `close()` runs unconditionally.
</details>

---

### Q3 🟢 · __exit__ params — three params and return True

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

**Problem:** Write the signature of `__exit__` and describe each of its three parameters. Then show what happens when you return `True` vs `False`/`None`. Include a concrete example demonstrating the difference.

<details>
<summary>💡 Hint</summary>

All three parameters are `None` in the no-exception case. What does Python do with the return value?
</details>

<details>
<summary>✅ Answer</summary>

```python
def __exit__(self, exc_type, exc_val, exc_tb):
    #              │          │        └── traceback.TracebackType or None
    #              │          └── the exception instance, e.g. ValueError("bad")
    #              └── the exception class, e.g. ValueError

    # No exception: all three are None
    # Exception raised in with-block: all three are populated

    pass  # return None (falsy) → exception propagates

# Return True → suppress (exception disappears):
class Silencer:
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        return True   # swallows ALL exceptions — use with care!

with Silencer():
    raise ValueError("gone")  # no error raised after the with block

# Return False/None → propagate:
class Tracer:
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f"Exception was: {exc_type.__name__}: {exc_val}")
        return False  # still propagates

try:
    with Tracer():
        raise KeyError("missing")
except KeyError:
    pass  # exception propagated and caught here
```

**Why:** Python uses the truthiness of `__exit__`'s return value to decide whether to re-raise. `True` means "I handled it, don't re-raise." `False` or `None` means "let it propagate normally."
</details>

---

### Q4 🟡 · class-based CM — write ManagedFile

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

**Problem:** Write a class `ManagedFile` that wraps file open/close as a context manager. It should accept `path` and `mode` arguments. The `as` variable should be the file handle. Exceptions must not be suppressed.

<details>
<summary>💡 Hint</summary>

`__enter__` should open the file and return the handle. `__exit__` should close it and return `False`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class ManagedFile:
    def __init__(self, path, mode="r", encoding="utf-8"):
        self.path     = path
        self.mode     = mode
        self.encoding = encoding
        self.file     = None

    def __enter__(self):
        self.file = open(self.path, self.mode, encoding=self.encoding)
        return self.file   # ← 'as' variable receives the file handle

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        return False       # don't suppress exceptions

# Usage:
with ManagedFile("data.txt") as f:
    content = f.read()
# f.close() guaranteed even if f.read() raises
```

**Why:** Separating `__init__` (store config) from `__enter__` (open resource) is important — the resource should only be acquired when the `with` block starts, not when the object is created.
</details>

---

### Q5 🟡 · suppress exceptions — write SuppressErrors

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

**Problem:** Write a class `SuppressErrors` that accepts one or more exception types and silently swallows them. Other exception types must still propagate. Demonstrate it with a `KeyError` and a `ValueError`.

<details>
<summary>💡 Hint</summary>

Use `issubclass(exc_type, self.exception_types)` to check whether the raised exception is one of the types to suppress. Return `True` only in that case.
</details>

<details>
<summary>✅ Answer</summary>

```python
class SuppressErrors:
    def __init__(self, *exception_types):
        self.exception_types = exception_types

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and issubclass(exc_type, self.exception_types):
            return True   # suppress: exception does not propagate
        return False      # let everything else propagate

# KeyError is suppressed:
cache = {"a": 1}
with SuppressErrors(KeyError):
    del cache["nonexistent"]   # no error
print("continued normally")

# ValueError still propagates:
try:
    with SuppressErrors(KeyError):
        raise ValueError("not suppressed")
except ValueError as e:
    print(f"correctly propagated: {e}")
```

**Why:** `issubclass` handles inheritance correctly — if `exc_type` is a subclass of a suppressed type, it is also suppressed. This mirrors exactly how `contextlib.suppress()` works internally.
</details>

---

### Q6 🟢 · contextlib.suppress — rewrite try/except/pass

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

**Problem:** Rewrite the following verbose try/except/pass blocks using `contextlib.suppress()`:

```python
# Block A:
try:
    os.remove("temp.txt")
except FileNotFoundError:
    pass

# Block B:
try:
    value = data["missing"]["nested"]
except (KeyError, TypeError):
    pass
```

<details>
<summary>💡 Hint</summary>

`suppress()` accepts multiple exception types as positional arguments.
</details>

<details>
<summary>✅ Answer</summary>

```python
from contextlib import suppress
import os

# Block A:
with suppress(FileNotFoundError):
    os.remove("temp.txt")

# Block B:
with suppress(KeyError, TypeError):
    value = data["missing"]["nested"]
```

**Why:** `suppress()` communicates intent more clearly — "I expect this might fail and that's acceptable" — versus `try/except: pass` which looks like silently swallowing an error. Use it only for narrow, expected exception types.
</details>

---

### Q7 🟡 · @contextmanager — timer using generator

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

**Problem:** Write a `timer(label)` context manager using `@contextmanager` that measures elapsed time for the `with` block and prints `"{label} completed in {elapsed:.4f}s"` on exit. Use `time.perf_counter()`.

<details>
<summary>💡 Hint</summary>

Record start time before `yield`. Use `try/finally` so elapsed time is always printed even if the body raises.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time
from contextlib import contextmanager

@contextmanager
def timer(label):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{label} completed in {elapsed:.4f}s")

# Usage:
with timer("sorting"):
    data = sorted(range(100_000), reverse=True)
# prints: sorting completed in 0.0123s
```

**Why:** `yield` with no value is correct here — we are not passing a resource to the block. `try/finally` ensures the elapsed time is printed even if the body raises an exception.
</details>

---

### Q8 🟡 · @contextmanager resource leak — spot and fix

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

**Problem:** The following context manager has a resource leak. Identify the problem and fix it.

```python
from contextlib import contextmanager

@contextmanager
def open_connection(host):
    conn = connect(host)
    yield conn
    conn.close()
```

<details>
<summary>💡 Hint</summary>

What happens to the line after `yield` if the body of the `with` block raises an exception?
</details>

<details>
<summary>✅ Answer</summary>

```python
# PROBLEM: if the with-block raises, conn.close() is never reached.
# The generator is aborted at the yield point — lines after yield do not run.

# BROKEN:
@contextmanager
def open_connection_broken(host):
    conn = connect(host)
    yield conn
    conn.close()   # NOT called if with-block raises!

# FIXED: wrap in try/finally:
@contextmanager
def open_connection(host):
    conn = connect(host)
    try:
        yield conn
    finally:
        conn.close()   # always called, even on exception
```

**Why:** When an exception occurs in the `with` body, `@contextmanager`'s machinery calls `gen.throw(exc)` to inject the exception at the `yield` point. Without `try/finally`, the generator exits immediately and any cleanup after `yield` is skipped.
</details>

---

### Q9 🟡 · transaction CM — commit on success, rollback on exception

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

**Problem:** Write a `transaction(conn)` context manager using `@contextmanager` that:
- Executes `conn.execute("BEGIN")` on entry
- Executes `conn.execute("COMMIT")` if the block succeeds
- Executes `conn.execute("ROLLBACK")` if an exception occurs and then re-raises the exception

<details>
<summary>💡 Hint</summary>

Use `try/except/raise` not just `try/finally` — you need to distinguish the success path (COMMIT) from the failure path (ROLLBACK).
</details>

<details>
<summary>✅ Answer</summary>

```python
from contextlib import contextmanager

@contextmanager
def transaction(conn):
    conn.execute("BEGIN")
    try:
        yield conn
        conn.execute("COMMIT")    # only reached if no exception
    except Exception:
        conn.execute("ROLLBACK")  # exception path
        raise                     # re-raise — don't suppress

# Usage:
with transaction(db) as conn:
    conn.execute("INSERT INTO orders VALUES (1, 'widget')")
    conn.execute("UPDATE inventory SET qty = qty - 1")
# COMMIT runs if both succeed

# On error:
try:
    with transaction(db) as conn:
        conn.execute("INSERT INTO orders VALUES (2, 'gadget')")
        raise RuntimeError("payment declined")
except RuntimeError:
    pass  # ROLLBACK ran before re-raise
```

**Why:** `except Exception: ... raise` is the correct pattern for cleanup-then-propagate. Using `finally` alone would not let you distinguish between commit and rollback paths.
</details>

---

### Q10 🟢 · temp_dir CM — create and clean up temp directory

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

**Problem:** Write a `temp_dir()` context manager using `@contextmanager` that creates a temporary directory, yields its `Path`, and removes the entire directory tree on exit (even on exception).

<details>
<summary>💡 Hint</summary>

Use `tempfile.mkdtemp()` to create the directory and `shutil.rmtree()` to remove it. The `ignore_errors=True` argument is useful to avoid errors if the directory was already removed.
</details>

<details>
<summary>✅ Answer</summary>

```python
import tempfile, shutil
from pathlib import Path
from contextlib import contextmanager

@contextmanager
def temp_dir():
    path = Path(tempfile.mkdtemp())
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)

# Usage:
with temp_dir() as d:
    (d / "output.csv").write_text("name,score\nAlice,95\n")
    (d / "report.txt").write_text("Q4: 42\n")
    files = [f.name for f in d.iterdir()]
    print(files)   # ['output.csv', 'report.txt']
# directory and all files deleted here
```

**Why:** `shutil.rmtree` removes the entire directory tree in one call. `ignore_errors=True` prevents a secondary exception if the directory was already cleaned up by the test body.
</details>

---

### Q11 🟡 · timing CM — measure and log elapsed time

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

**Problem:** Extend the `timer` context manager from Q7 to also accept an optional `logger` argument. If `logger` is provided, use `logger.info()` to log the elapsed time. If not, fall back to `print()`. The log message format should be `"{name} completed in {elapsed:.3f}s"`.

<details>
<summary>💡 Hint</summary>

Default `logger=None` in the function signature. Check `if logger` to decide which output method to use.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time, logging
from contextlib import contextmanager

@contextmanager
def timer(name: str, logger=None):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        msg = f"{name} completed in {elapsed:.3f}s"
        if logger:
            logger.info(msg)
        else:
            print(msg)

# Usage without logger:
with timer("list build"):
    result = list(range(100_000))

# Usage with logger:
log = logging.getLogger(__name__)
with timer("db query", logger=log):
    # rows = db.execute("SELECT ...")
    pass
# INFO: db query completed in 0.042s
```

**Why:** This pattern — accepting an optional logger and falling back to print — is common in libraries that want to integrate with application logging without requiring it.
</details>

---

### Q12 🟡 · acquire_lock CM — lock with timeout

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

**Problem:** Write an `acquire_lock(lock, timeout=5.0)` context manager using `@contextmanager`. It should:
- Try to acquire the lock with the given timeout
- Raise `TimeoutError` if it cannot be acquired
- Always release the lock on exit (only if it was acquired)

<details>
<summary>💡 Hint</summary>

`lock.acquire(timeout=timeout)` returns `True` if acquired, `False` if it timed out. Use `try/finally` to ensure release only if acquisition succeeded.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading
from contextlib import contextmanager

@contextmanager
def acquire_lock(lock, timeout=5.0):
    acquired = lock.acquire(timeout=timeout)
    if not acquired:
        raise TimeoutError(f"Could not acquire lock within {timeout}s")
    try:
        yield
    finally:
        lock.release()

# Usage:
lock = threading.Lock()

with acquire_lock(lock, timeout=2.0):
    # critical section
    pass
# lock released here

# Timeout case:
try:
    with acquire_lock(lock, timeout=0.001):
        pass
except TimeoutError as e:
    print(f"Lock unavailable: {e}")
```

**Why:** Checking the return value of `acquire()` before `yield` is important — if we raise `TimeoutError` before `yield`, we never enter the `try` block, so `finally` is never reached and `release()` is not called (which is correct — we never acquired it).
</details>

---

### Q13 🟡 · redirect_stdout — capture print() output to buffer

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)

**Problem:** You have a legacy function `report()` that uses `print()` to emit output. You need to capture its output as a string without modifying `report()`. Use `contextlib.redirect_stdout` to capture the output into an `io.StringIO` buffer and return the string.

<details>
<summary>💡 Hint</summary>

Create an `io.StringIO()` buffer, use `redirect_stdout(buffer)` as the context manager, then call `buffer.getvalue()` after the block.
</details>

<details>
<summary>✅ Answer</summary>

```python
import io
from contextlib import redirect_stdout

def report():
    print("Sales: $42,000")
    print("Units: 1,024")
    print("Region: APAC")

# Capture:
buffer = io.StringIO()
with redirect_stdout(buffer):
    report()

output = buffer.getvalue()
print(repr(output))
# 'Sales: $42,000\nUnits: 1,024\nRegion: APAC\n'

# Parse lines:
lines = output.strip().splitlines()
# ['Sales: $42,000', 'Units: 1,024', 'Region: APAC']
```

**Why:** `redirect_stdout` temporarily replaces `sys.stdout` for the duration of the block. This is the canonical way to capture print-based output from code you cannot modify, and is used extensively in testing frameworks.
</details>

---

### Q14 🟡 · database connection CM — auto-commit/rollback

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)

**Problem:** Write a `get_connection(db_path)` context manager using `@contextmanager` for `sqlite3`. It should:
- Open the connection with `row_factory = sqlite3.Row`
- Yield the connection
- Commit on clean exit
- Rollback on exception (and re-raise)
- Always close the connection in a `finally` block

<details>
<summary>💡 Hint</summary>

The `finally` block for `conn.close()` should be separate from the `except` block for rollback. Nest `try/except` inside `try/finally`, or use two `try` layers.
</details>

<details>
<summary>✅ Answer</summary>

```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_connection(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()   # always close, even after rollback

# Usage:
with get_connection("app.db") as conn:
    conn.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER, data TEXT)")
    conn.execute("INSERT INTO events VALUES (1, 'login')")
# auto-committed and closed

# On error:
try:
    with get_connection("app.db") as conn:
        conn.execute("INSERT INTO events VALUES (2, 'purchase')")
        raise RuntimeError("payment failed")
except RuntimeError:
    pass   # rollback ran, connection closed
```

**Why:** `finally: conn.close()` runs regardless of whether commit or rollback was called. This three-layer pattern (yield → commit → except rollback → finally close) is the standard DB context manager pattern.
</details>

---

### Q15 🟢 · multiple CMs — nested vs one-liner

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)

**Problem:** Write the same file copy operation (read `input.txt`, write `output.txt`) in two styles:
1. Nested `with` blocks (old style)
2. Single `with` using comma-separated context managers (modern style)

Then write the parenthesized form for three context managers (Python 3.10+).

<details>
<summary>💡 Hint</summary>

All three styles are semantically equivalent. The parenthesized form allows a trailing comma and is useful for long lines.
</details>

<details>
<summary>✅ Answer</summary>

```python
# Style 1 — nested (verbose, Python 2-compatible):
with open("input.txt") as fin:
    with open("output.txt", "w") as fout:
        fout.write(fin.read())

# Style 2 — one-liner (preferred in modern Python):
with open("input.txt") as fin, open("output.txt", "w") as fout:
    fout.write(fin.read())

# Style 3 — parenthesized form (Python 3.10+, allows trailing comma):
with (
    open("a.txt") as a,
    open("b.txt") as b,
    open("c.txt", "w") as c,
):
    c.write(a.read() + b.read())

# Exit order for all styles is LIFO:
# Style 2: fout.__exit__() first, then fin.__exit__()
```

**Why:** All three are semantically identical. The parenthesized form (3.10+) is useful when you have 3+ context managers and want a trailing comma for clean diffs.
</details>

---

### Q16 🟡 · exit order — trace LIFO for A, B, C

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)

**Problem:** Given three context managers `A`, `B`, `C` used in a single `with` statement, write code that demonstrates the LIFO (last-in, first-out) exit order by printing `ENTER` and `EXIT` events. Verify your answer by running the code mentally.

<details>
<summary>💡 Hint</summary>

Build a simple `Tracked` class whose `__enter__` and `__exit__` each print a message with the instance name.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Tracked:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        print(f"ENTER: {self.name}")
        return self

    def __exit__(self, *args):
        print(f"EXIT:  {self.name}")
        return False

with Tracked("A") as a, Tracked("B") as b, Tracked("C") as c:
    print("(inside with block)")

# Output:
# ENTER: A
# ENTER: B
# ENTER: C
# (inside with block)
# EXIT:  C    ← last entered, first exited
# EXIT:  B
# EXIT:  A    ← first entered, last exited
```

**Why:** Python enters context managers left-to-right but unwinds them right-to-left, the same way a call stack unwinds. This LIFO order ensures that dependent resources are released in the correct dependency order.
</details>

---

### Q17 🟡 · ExitStack — merge N files at runtime

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)

**Problem:** Write a function `merge_files(input_paths, output_path)` that opens a dynamic number of input files (the count is not known at write time), reads them all, and writes their contents concatenated into `output_path`. All files must be closed on exit, even if an exception occurs.

<details>
<summary>💡 Hint</summary>

Use `ExitStack` and `stack.enter_context(open(p))` in a list comprehension to register each file.
</details>

<details>
<summary>✅ Answer</summary>

```python
from contextlib import ExitStack

def merge_files(input_paths, output_path):
    with ExitStack() as stack:
        readers = [stack.enter_context(open(p)) for p in input_paths]
        with open(output_path, "w") as out:
            for reader in readers:
                out.write(reader.read())
    # all readers closed here regardless of how many

# Usage:
merge_files(["a.txt", "b.txt", "c.txt"], "merged.txt")

# Works for any N:
paths = [f"chunk_{i}.txt" for i in range(100)]
merge_files(paths, "combined.txt")
```

**Why:** `ExitStack` is the correct tool when you need to open an unknown number of resources. Writing `with open(p1) as f1, open(p2) as f2, ...` would require knowing N at code-writing time, which is not always possible.
</details>

---

### Q18 🟡 · ExitStack callbacks — register cleanup functions

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)

**Problem:** Using `ExitStack`, register three cleanup callbacks in order: `print("cleanup A")`, `print("cleanup B")`, `print("cleanup C")`. Demonstrate that they run in LIFO order (C first, A last).

<details>
<summary>💡 Hint</summary>

`stack.callback(fn, *args)` registers a callable that is invoked with `args` on exit. Order of registration determines LIFO unwind order.
</details>

<details>
<summary>✅ Answer</summary>

```python
from contextlib import ExitStack

with ExitStack() as stack:
    stack.callback(print, "cleanup A")   # registered first → runs last
    stack.callback(print, "cleanup B")
    stack.callback(print, "cleanup C")   # registered last → runs first
    print("(inside block)")

# Output:
# (inside block)
# cleanup C
# cleanup B
# cleanup A

# Real-world example — register multiple cleanups dynamically:
def process(data):
    with ExitStack() as stack:
        conn = db.connect()
        stack.callback(conn.close)
        stack.callback(metrics.record, "process.complete")

        if data.needs_temp_file:
            tmp = create_temp_file()
            stack.callback(tmp.unlink)

        return transform(data)
```

**Why:** `callback()` is more flexible than `enter_context()` — it works with any callable, not just context managers. It is useful for registering cleanup for objects that have a `.close()` method but do not implement `__enter__`/`__exit__`.
</details>

---

### Q19 🟠 · ExitStack conditional — use transaction if flag set

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)

**Problem:** Write a function `do_work(db, use_transaction=True)` that conditionally wraps its database operations in a transaction context manager. If `use_transaction` is `True`, all operations run inside a transaction (commit on success, rollback on failure). If `False`, operations run directly on `db` with no transaction management. Use `ExitStack`.

<details>
<summary>💡 Hint</summary>

When `use_transaction` is True, call `stack.enter_context(transaction(db))` to get `conn`. Otherwise, set `conn = db` directly without entering any context manager.
</details>

<details>
<summary>✅ Answer</summary>

```python
from contextlib import ExitStack, contextmanager

@contextmanager
def transaction(conn):
    conn.execute("BEGIN")
    try:
        yield conn
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise

def do_work(db, use_transaction=True):
    with ExitStack() as stack:
        if use_transaction:
            conn = stack.enter_context(transaction(db))
        else:
            conn = db   # no transaction — use db directly

        conn.execute("INSERT INTO events VALUES (1, 'start')")
        conn.execute("UPDATE counters SET n = n + 1 WHERE id = 1")

# With transaction (default):
do_work(db)

# Without transaction:
do_work(db, use_transaction=False)
```

**Why:** This pattern avoids duplicating the `do_work` logic into two code paths. `ExitStack` is the right tool here because it lets you conditionally push a context manager without changing the structure of the code that follows.
</details>

---

### Q20 🟡 · nullcontext — optional lock pattern

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)

**Problem:** Write a `process_data(data, use_lock=True)` function that optionally acquires a `threading.Lock` before processing. Use `contextlib.nullcontext` so there is only one `with` statement in the function body regardless of the `use_lock` flag.

<details>
<summary>💡 Hint</summary>

Assign `ctx = lock if use_lock else nullcontext()` before the `with` statement.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading
from contextlib import nullcontext

lock = threading.Lock()

def process_data(data, use_lock=True):
    ctx = lock if use_lock else nullcontext()
    with ctx:
        return [x * 2 for x in data]

# Both call paths use a single 'with':
result_locked   = process_data([1, 2, 3], use_lock=True)
result_unlocked = process_data([1, 2, 3], use_lock=False)

# nullcontext with a value (Python 3.10+):
from contextlib import nullcontext

def open_file(path=None, default=""):
    ctx = open(path) if path else nullcontext(default)
    with ctx as content:
        process(content)
```

**Why:** `nullcontext()` exists precisely to avoid `if/else` branching around `with` statements. It is a no-op that satisfies the context manager protocol without doing anything, keeping code paths unified.
</details>

---

### Q21 🟡 · async CM — write AsyncDBConnection

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)

**Problem:** Write a class `AsyncDBConnection` with `__aenter__` and `__aexit__`. On entry, it should simulate connecting (`await asyncio.sleep(0)` as a stand-in). On clean exit, it should commit. On exception, it should rollback. Always close the connection. The `as` variable should be the connection object itself.

<details>
<summary>💡 Hint</summary>

Both `__aenter__` and `__aexit__` must be `async def`. Use `async with` to invoke the context manager.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

class AsyncDBConnection:
    def __init__(self, dsn: str):
        self.dsn  = dsn
        self.conn = None

    async def __aenter__(self):
        await asyncio.sleep(0)   # simulate async connect
        self.conn = self          # stand-in for real connection object
        print(f"connected to {self.dsn}")
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print("rollback")
        else:
            print("commit")
        print(f"closed {self.dsn}")
        return False   # don't suppress exceptions

async def main():
    async with AsyncDBConnection("postgres://localhost/app") as conn:
        print("running query")

asyncio.run(main())
# connected to postgres://localhost/app
# running query
# commit
# closed postgres://localhost/app
```

**Why:** The async context manager protocol (`__aenter__`/`__aexit__`) is identical to the sync protocol except both methods are coroutines. `async with` is required — `with` alone would not `await` the setup and teardown.
</details>

---

### Q22 🟡 · @asynccontextmanager — write async_timer

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)

**Problem:** Write `async_timer(name)` using `@asynccontextmanager`. It should measure wall-clock elapsed time using `time.perf_counter()` and print `"{name}: {elapsed:.3f}s"` on exit. Demonstrate it with a simulated async operation.

<details>
<summary>💡 Hint</summary>

Use `from contextlib import asynccontextmanager`. The function must be `async def` with a single `yield`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio, time
from contextlib import asynccontextmanager

@asynccontextmanager
async def async_timer(name: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{name}: {elapsed:.3f}s")

async def main():
    async with async_timer("data fetch"):
        await asyncio.sleep(0.1)   # simulate async I/O
    # prints: data fetch: 0.101s

asyncio.run(main())
```

**Why:** `@asynccontextmanager` is the async equivalent of `@contextmanager`. It transforms an async generator function into an async context manager, so `async with` can be used instead of building a full class with `__aenter__` and `__aexit__`.
</details>

---

### Q23 🟡 · gotcha return True — fix accidental suppression

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)

**Problem:** The following context manager has a dangerous bug. Identify it and fix it so that only `KeyError` is suppressed and all other exceptions propagate normally.

```python
class CleanupManager:
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return True
```

<details>
<summary>💡 Hint</summary>

`return True` unconditionally suppresses every exception. Add a condition that only returns `True` for the specific exception type you intend to suppress.
</details>

<details>
<summary>✅ Answer</summary>

```python
# BROKEN — swallows ALL exceptions silently:
class CleanupManagerBroken:
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return True   # ← hides every exception including serious bugs!

# FIXED — only suppress KeyError:
class CleanupManager:
    def cleanup(self):
        pass  # placeholder

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        # Only suppress KeyError; let everything else propagate:
        if exc_type is not None and issubclass(exc_type, KeyError):
            return True
        return False

# Verify:
cm = CleanupManager()

with cm:
    raise KeyError("suppressed")  # no error — suppressed correctly
print("KeyError was suppressed")

try:
    with cm:
        raise ValueError("not suppressed")  # propagates
except ValueError:
    print("ValueError propagated correctly")
```

**Why:** `return True` is equivalent to `except Exception: pass` around the entire `with` block — it silently hides every exception, including bugs that should crash the program. Always check `exc_type` before suppressing.
</details>

---

### Q24 🟡 · gotcha missing try/finally — show the leak, add fix

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)

**Problem:** Show two versions of a `managed_resource()` context manager: the leaky version (without `try/finally`) and the fixed version. Demonstrate that the leaky version does NOT call `release()` when the body raises, but the fixed version always does.

<details>
<summary>💡 Hint</summary>

Use a simple `Resource` class with a `release()` method that prints a message, so you can observe whether it was called.
</details>

<details>
<summary>✅ Answer</summary>

```python
from contextlib import contextmanager

class Resource:
    def __init__(self, name):
        self.name = name
        print(f"  acquired: {self.name}")

    def release(self):
        print(f"  released: {self.name}")


# LEAKY — release() skipped on exception:
@contextmanager
def leaky(name):
    r = Resource(name)
    yield r
    r.release()   # never reached if body raises!

print("Leaky version:")
try:
    with leaky("r1") as r:
        raise RuntimeError("boom")
except RuntimeError:
    pass
# Output: acquired: r1
# (release: r1 is MISSING — resource leaked!)


# FIXED — release() always called:
@contextmanager
def safe(name):
    r = Resource(name)
    try:
        yield r
    finally:
        r.release()   # guaranteed

print("\nSafe version:")
try:
    with safe("r2") as r:
        raise RuntimeError("boom")
except RuntimeError:
    pass
# Output: acquired: r2
#         released: r2  ← always called
```

**Why:** Without `try/finally`, any exception at the `yield` point causes the generator to be aborted without running cleanup code. The `finally` block is the only reliable guarantee.
</details>

---

### Q25 🟠 · gotcha __enter__ raises — protect setup

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)

**Problem:** The following `__enter__` acquires two resources in sequence. If `step_two()` raises, `__exit__` is never called, leaking the resource from `step_one()`. Fix `__enter__` to guarantee cleanup of partially acquired resources.

```python
class Resource:
    def __enter__(self):
        self.conn  = step_one()   # succeeds
        self.lock  = step_two()   # may raise
        return self

    def __exit__(self, *args):
        self.conn.close()
        self.lock.release()
        return False
```

<details>
<summary>💡 Hint</summary>

Wrap the second acquisition in `try/except`. If it fails, clean up `self.conn` before re-raising.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Resource:
    def __enter__(self):
        self.conn = None
        self.lock = None

        self.conn = step_one()   # acquire first resource
        try:
            self.lock = step_two()   # acquire second resource
        except Exception:
            self.conn.close()    # clean up what we already acquired
            raise                # re-raise original exception

        return self

    def __exit__(self, *args):
        if self.lock:
            self.lock.release()
        if self.conn:
            self.conn.close()
        return False

# Why this matters:
# If step_two() raises, Python does NOT call __exit__ —
# the with block never started. The only way to clean up
# partial setup is to do it inside __enter__ itself.
```

**Why:** `__exit__` is only called if `__enter__` returns successfully. If `__enter__` raises, the context manager's cleanup contract is broken — the caller never entered the `with` block. Partial resource cleanup must happen within `__enter__` itself.
</details>

---

### Q26 🟡 · contextlib.closing — wrap legacy object

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)

**Problem:** You have a `LegacyDB` class that has a `.close()` method but does not implement `__enter__`/`__exit__`. Use `contextlib.closing` to use it safely in a `with` statement. Show both the manual pattern (without `closing`) and the idiomatic pattern.

<details>
<summary>💡 Hint</summary>

`closing(obj)` wraps any object with a `.close()` method and calls it on `__exit__`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from contextlib import closing

class LegacyDB:
    def connect(self):
        print("  connected")
        return self

    def query(self, sql):
        print(f"  query: {sql}")
        return []

    def close(self):
        print("  closed")


# Manual — must remember close():
db = LegacyDB().connect()
try:
    results = db.query("SELECT 1")
finally:
    db.close()   # must write this every time

# Idiomatic — closing() handles it:
with closing(LegacyDB().connect()) as db:
    results = db.query("SELECT 1")
# db.close() called automatically

# Real-world use case:
from urllib.request import urlopen
with closing(urlopen("http://example.com")) as response:
    data = response.read()
# response.close() guaranteed
```

**Why:** `closing` is a compatibility shim for legacy APIs that predate the context manager protocol. It is cleaner than wrapping in `try/finally` and communicates that the object has a `.close()` method that needs calling.
</details>

---

### Q27 🟡 · audit_log CM — wrap operation with start/end/error logging

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)

**Problem:** Write an `audit_log(operation_name)` context manager using `@contextmanager`. It should:
- Print `"START: {operation_name}"` on entry
- Print `"END: {operation_name}"` on clean exit
- Print `"ERROR: {operation_name} — {exc_type.__name__}: {exc_val}"` on exception (then re-raise)

<details>
<summary>💡 Hint</summary>

Use `try/except/else` inside the generator: `else` runs only if `yield` completed without exception.
</details>

<details>
<summary>✅ Answer</summary>

```python
from contextlib import contextmanager

@contextmanager
def audit_log(operation_name):
    print(f"START: {operation_name}")
    try:
        yield
    except Exception as e:
        print(f"ERROR: {operation_name} — {type(e).__name__}: {e}")
        raise   # re-raise after logging
    else:
        print(f"END: {operation_name}")

# Clean exit:
with audit_log("user.login"):
    pass  # simulate work
# START: user.login
# END: user.login

# Exception case:
try:
    with audit_log("payment.charge"):
        raise ValueError("card declined")
except ValueError:
    pass
# START: payment.charge
# ERROR: payment.charge — ValueError: card declined
```

**Why:** `try/except/else` in a generator is the clean way to distinguish success from failure paths without using a flag variable. The `else` clause runs when `yield` completes without exception.
</details>

---

### Q28 🟠 · ExitStack ownership transfer — return stack to caller

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)

**Problem:** Write a function `open_connections(dsns)` that opens a list of database connections (simulate with `io.StringIO` objects) and returns them to the caller along with the `ExitStack`. The caller is responsible for closing everything. Demonstrate the caller using the returned stack in a `with` statement.

<details>
<summary>💡 Hint</summary>

Do not use `with ExitStack() as stack:` inside the function — create `stack = ExitStack()` without a `with`, register the connections, and return `(connections, stack)`. The caller uses `with stack:` or calls `stack.close()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import io
from contextlib import ExitStack

def open_connections(dsns):
    """Open connections and return them with the stack.
    Caller is responsible for closing via stack.close() or 'with stack'."""
    stack = ExitStack()
    try:
        connections = [
            stack.enter_context(io.StringIO(dsn)) for dsn in dsns
        ]
    except Exception:
        stack.close()   # clean up any already-opened connections
        raise
    return connections, stack

# Caller manages lifetime:
connections, stack = open_connections(["dsn1", "dsn2", "dsn3"])
with stack:
    for conn in connections:
        print(conn.read())   # 'dsn1', 'dsn2', 'dsn3'
# all connections closed when 'with stack' exits

# Alternative: explicit close
connections, stack = open_connections(["dsn1", "dsn2"])
try:
    for conn in connections:
        print(conn.read())
finally:
    stack.close()
```

**Why:** Ownership transfer is a common pattern when a factory function opens resources but the caller controls the lifecycle. The `ExitStack` travels with the resources, giving the caller a single handle to close everything. The `try/except` in the factory guards against partial failures during setup.
</details>

---

### Q29 🟡 · debug wrong suppress scope — fix overly broad suppress

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)

**Problem:** The following code has a suppression bug: it suppresses `FileNotFoundError` but the scope of the `suppress` block is too broad, potentially hiding a `FileNotFoundError` raised by `process_content(content)` that should not be suppressed. Refactor to suppress only the specific operation that can legitimately raise `FileNotFoundError`.

```python
from contextlib import suppress

with suppress(FileNotFoundError):
    with open("config.json") as f:
        content = f.read()
    process_content(content)   # this could also raise FileNotFoundError!
    save_results(content)
```

<details>
<summary>💡 Hint</summary>

Narrow the `suppress` scope to only the `open()` call. Everything else should be outside the `suppress` block.
</details>

<details>
<summary>✅ Answer</summary>

```python
from contextlib import suppress

# BROKEN — suppress scope is too broad:
# If process_content() raises FileNotFoundError (e.g., tries to open
# another file internally), it is silently swallowed — a hidden bug.
with suppress(FileNotFoundError):
    with open("config.json") as f:
        content = f.read()
    process_content(content)   # FileNotFoundError here would be hidden!
    save_results(content)

# FIXED — suppress only the specific open() call:
content = None
with suppress(FileNotFoundError):
    with open("config.json") as f:
        content = f.read()

if content is not None:
    process_content(content)   # FileNotFoundError here will propagate
    save_results(content)

# Alternative — check file existence first:
import os
if os.path.exists("config.json"):
    with open("config.json") as f:
        content = f.read()
    process_content(content)
    save_results(content)
```

**Why:** The scope of `suppress()` should be as narrow as possible — only the exact operation that is expected to fail non-fatally. Broad suppress scopes are a form of the "Pokemon exception handler" anti-pattern.
</details>

---

### Q30 🟠 · capstone — build ConnectionPool with ExitStack

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)

**Problem:** Build a `ConnectionPool` class that manages a pool of connections using `ExitStack` internally. It should:
- Accept a list of DSNs in `__init__`
- Implement `__enter__` to open all connections and return `self`
- Implement `__exit__` to close all connections via `ExitStack.close()`
- Expose a `get(i)` method to retrieve connection `i`
- Handle partial failures during setup (if connection `i` fails, connections `0..i-1` must be closed)

Use `io.StringIO` as a stand-in for real connections.

<details>
<summary>💡 Hint</summary>

Create an `ExitStack` as an instance variable in `__init__`. In `__enter__`, open each connection and register it with the stack. In `__exit__`, call `self._stack.close()`. For partial failure protection, wrap the setup loop in `try/except` and call `self._stack.close()` on failure.
</details>

<details>
<summary>✅ Answer</summary>

```python
import io
from contextlib import ExitStack

class ConnectionPool:
    def __init__(self, dsns):
        self._dsns        = dsns
        self._stack       = ExitStack()
        self._connections = []

    def __enter__(self):
        try:
            for dsn in self._dsns:
                conn = self._stack.enter_context(io.StringIO(dsn))
                self._connections.append(conn)
        except Exception:
            self._stack.close()   # close any already-opened connections
            raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stack.close()   # closes all registered connections in LIFO order
        return False

    def get(self, i):
        return self._connections[i]

# Usage:
dsns = ["postgres://host1/db", "postgres://host2/db", "postgres://host3/db"]

with ConnectionPool(dsns) as pool:
    conn0 = pool.get(0)
    conn1 = pool.get(1)
    print(conn0.read())   # 'postgres://host1/db'
    print(conn1.read())   # 'postgres://host2/db'
# all 3 connections closed here via ExitStack

# Exception safety:
try:
    with ConnectionPool(dsns) as pool:
        raise RuntimeError("processing error")
except RuntimeError:
    pass
# all connections still closed correctly
```

**Why:** Embedding `ExitStack` inside a class is a powerful pattern for managing multiple resources whose count is determined at runtime. The `__exit__` delegates entirely to `stack.close()`, which handles LIFO cleanup and exception safety automatically.
</details>

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🛠️ contextlib Guide | [contextlib_guide.md](./contextlib_guide.md) |
| 💻 Practice Local | [practice_local.py](./practice_local.py) |

---

**Related:** [contextlib_guide.md](./contextlib_guide.md) · [custom_context_manager.py](./custom_context_manager.py)
