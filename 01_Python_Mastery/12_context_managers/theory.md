<a id="top"></a>
# 🧩 Context Managers — Theory

> *"A context manager is a contract: 'I promise to clean up after myself,*
> *no matter what happens.' It is the foundation of resource-safe Python."*

## 📖 Table of Contents

- [1. The `with` Statement — What Actually Happens](#1-the-with-statement--what-actually-happens)
- [2. The Context Manager Protocol](#2-the-context-manager-protocol)
- [3. Suppressing Exceptions with `__exit__`](#3-suppressing-exceptions-with-__exit__)
- [4. `@contextmanager` — Generator-Based Context Managers](#4-contextmanager--generator-based-context-managers)
- [5. Real Production Patterns](#5-real-production-patterns)
  - [Timing Context Manager](#timing-context-manager)
  - [Temporary Directory](#temporary-directory)
  - [Thread Lock](#thread-lock)
  - [Database Connection](#database-connection)
  - [Redirecting stdout](#redirecting-stdout)
- [6. Multiple Context Managers in One `with`](#6-multiple-context-managers-in-one-with)
- [7. `contextlib.ExitStack` — Dynamic Context Managers](#7-contextlibexitstack--dynamic-context-managers)
- [8. `contextlib.nullcontext` — Conditional Context Managers](#8-contextlibnullcontext--conditional-context-managers)
- [9. Async Context Managers](#9-async-context-managers)
- [10. `contextlib` — The Full Toolkit](#10-contextlib--the-full-toolkit)
- [11. Gotchas and Anti-Patterns](#11-gotchas-and-anti-patterns)
  - [Gotcha 1 — Returning `True` suppresses all exceptions](#gotcha-1--returning-true-suppresses-all-exceptions)
  - [Gotcha 2 — Not re-raising in `@contextmanager`](#gotcha-2--not-re-raising-in-contextmanager)
  - [Gotcha 3 — Forgetting `try/finally` in `@contextmanager`](#gotcha-3--forgetting-tryfinally-in-contextmanager)
  - [Gotcha 4 — Using context manager as non-context](#gotcha-4--using-context-manager-as-non-context)
  - [Gotcha 5 — `__exit__` not called if `__enter__` raises](#gotcha-5--__exit__-not-called-if-__enter__-raises)
- [12. The Full Mental Model](#12-the-full-mental-model)
  - [🔥 Summary](#-summary)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`with` statement · `__enter__` / `__exit__` protocol · `@contextmanager` decorator · Resource cleanup guarantee

**Should Learn** — Important for real projects, comes up regularly:
`contextlib.ExitStack` · `contextlib.redirect_stdout` / `redirect_stderr` · `async with` / `__aenter__` / `__aexit__`

**Good to Know** — Useful in specific situations:
`contextlib.nullcontext` · `contextlib.asynccontextmanager` · `contextlib.suppress`

**Reference** — Know it exists, look up when needed:
`contextlib.AbstractContextManager` · `contextlib.redirect_stdin` · Context variables (`contextvars`)

---

<a id="the-problem-resource-leaks-in-the-wild"></a>
# 🎬 The Problem: Resource Leaks in the Wild

It's Tuesday afternoon. Your service has been running for 6 days. Suddenly:

```
OSError: [Errno 24] Too many open files
```

You SSH in. `lsof -p <pid>` shows 1,024 open file handles — the OS limit. You trace it back:

```python
def load_config(path):
    f = open(path)            # ← opens file handle
    data = json.load(f)
    validate(data)            # ← if this raises, f.close() never runs
    f.close()
    return data
```

When `validate()` raised a `ValidationError`, the `f.close()` on the last line was never reached. After 6 days of reloads, 1,024 handles are stranded open.

The same pattern appears with:
- Database connections left open during exceptions
- Lock files never released after crashes
- Temporary files surviving forever
- Network sockets that never disconnect

**Context managers are Python's answer to this entire class of bugs.** They make cleanup unconditional.

---

<a id="1-the-with-statement--what-actually-happens"></a>
# 1. The `with` Statement — What Actually Happens

Imagine borrowing a library book. You take it, read it, and return it — but what if you forget? You get a fine. Python's `with` statement is the library's automated return system. You borrow the resource (file, connection, lock), do your work, and Python guarantees it gets returned — even if you crash halfway through, forget to clean up, or an exception interrupts you. The guarantee is unconditional.

Under the hood, Python translates `with open("config.json") as f:` into a precise try/except/finally pattern that it generates automatically for you:

```python
_cm   = open("config.json")          # get the context manager
f     = _cm.__enter__()              # setup: open the file, return the handle
try:
    data = json.load(f)              # your with-block body
except:
    if not _cm.__exit__(*sys.exc_info()):  # cleanup: always called
        raise                             # re-raise if __exit__ returns falsy
else:
    _cm.__exit__(None, None, None)   # cleanup: no exception
```

**Key facts:**
```
1. __enter__() runs at the top of with — setup
2. __exit__() runs at the bottom — ALWAYS — even if an exception occurs
3. The 'as f' variable gets whatever __enter__() returns
4. __exit__() receives exception info (type, value, traceback)
5. If __exit__() returns True, the exception is suppressed
```

⚠️ **Common mistake — confusing the context manager with the `as` variable:** `open("file.txt")` is the context manager object, but `f` is what `__enter__` returns (the file handle). For `open()` they happen to be the same object, but this is not always true. A database connection pool is the context manager; `__enter__` might return one connection from that pool — two different objects.

💡 **Hint:** The `as` clause is optional. `with lock:`, `with suppress(...)`, `with timer("block"):` are all valid — you just don't need the value that `__enter__` returns.

📝 **Practice:** [Q1 — with-statement-anatomy](./practice.md#q1--with-statement-anatomy--trace-the-5-steps)

> [↑ Back to Top](#top)

---

<a id="2-the-context-manager-protocol"></a>
# 2. The Context Manager Protocol

Think of a restaurant hiring kitchen staff. They don't care what culinary school you attended or what family you come from — they just ask two questions: "Can you prep the station before service?" and "Can you clean up after?" If you answer yes to both, you're hired. Python applies the same logic: any object that has `__enter__` (prep) and `__exit__` (cleanup) automatically becomes a context manager. No inheritance, no registration, no forms to fill.

```python
class ManagedFile:
    """Explicit class-based context manager."""

    def __init__(self, path, mode="r", encoding="utf-8"):
        self.path     = path
        self.mode     = mode
        self.encoding = encoding
        self.file     = None

    def __enter__(self):
        """Setup: open the file, return the handle."""
        self.file = open(self.path, self.mode, encoding=self.encoding)
        return self.file          # ← value assigned to 'as' variable

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup: always runs, even on exception."""
        if self.file:
            self.file.close()
        return False   # don't suppress exceptions

with ManagedFile("data.txt") as f:
    content = f.read()
# f is closed here, guaranteed
```

**`__exit__` signature — memorize this:**

```
def __exit__(self, exc_type, exc_val, exc_tb):
                    │          │        └── traceback.TracebackType or None
                    │          └── the exception instance or None
                    └── the exception class or None

When no exception: all three are None
When exception:    all three are populated
Return True:       exception suppressed (swallowed)
Return False/None: exception propagates normally
```

⚠️ **Common mistake — assuming `__exit__` only runs on exceptions:** It always runs — on clean exits too. On a normal return, `return` statement inside the block, or `break` in a loop, `__exit__` is still called with all three arguments as `None`.

💡 **Hint:** `return False` and `return None` behave identically — both let exceptions propagate. Explicit `return False` is better style because it makes your intent clear: "I am not suppressing this."

📝 **Practice:** [Q4 — class-based-cm](./practice.md#q4--class-based-cm--write-managedfile)

> [↑ Back to Top](#top)

---

<a id="3-suppressing-exceptions-with-__exit__"></a>
# 3. Suppressing Exceptions with `__exit__`

Imagine asking your roommate to throw out the milk if it's expired. If the milk isn't in the fridge at all — that's fine. You don't want a panicked phone call at midnight. You want them to silently skip it and move on. That's exactly what returning `True` from `__exit__` does: "I expected this might fail, it's fine, don't bother the caller." The exception disappears and code continues after the `with` block as if nothing happened.

```python
class SuppressErrors:
    """Context manager that swallows specified exception types."""

    def __init__(self, *exception_types):
        self.exception_types = exception_types

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and issubclass(exc_type, self.exception_types):
            return True   # ← suppress: exception does NOT propagate
        return False      # ← let it propagate

with SuppressErrors(FileNotFoundError, PermissionError):
    content = open("optional_config.json").read()

# If file doesn't exist: no exception — execution continues normally
# If other IOError: propagates normally

# Real-world example:
with SuppressErrors(KeyError):
    del cache[key]   # silently skip if key not present
```

**The built-in equivalent — `contextlib.suppress()`** is cleaner for simple cases:

```python
from contextlib import suppress

with suppress(FileNotFoundError):
    os.remove("temp_file.txt")   # no error if file doesn't exist
```

⚠️ **Common mistake — silent suppression hides real bugs:** If you suppress `Exception` broadly instead of specific types, a `TypeError` or `AttributeError` caused by your own code will silently vanish. Always suppress only the exact exception you expect and consider logging it at DEBUG level before returning `True`.

💡 **Hint:** `contextlib.suppress` accepts multiple exception types in one call: `suppress(FileNotFoundError, PermissionError)`. No need to nest multiple suppress blocks.

📝 **Practice:** [Q5 — suppress-exceptions](./practice.md#q5--suppress-exceptions--write-suppresserrors)

> [↑ Back to Top](#top)

---

<a id="4-contextmanager--generator-based-context-managers"></a>
# 4. `@contextmanager` — Generator-Based Context Managers

Writing a full class with `__init__`, `__enter__`, and `__exit__` for every single resource feels like hiring a full-time employee just to make one sandwich. `@contextmanager` is the temp agency version: write a simple script (a generator function), mark the pause point with `yield`, and the decorator handles all the protocol wiring. Everything before `yield` is setup, everything after is cleanup, and the yielded value is what `as` receives.

```python
from contextlib import contextmanager

@contextmanager
def managed_file(path, mode="r", encoding="utf-8"):
    f = open(path, mode, encoding=encoding)   # setup (before yield)
    try:
        yield f                               # body runs here; f = 'as' variable
    finally:
        f.close()                             # cleanup (always runs)

with managed_file("data.txt") as f:
    content = f.read()
```

**The protocol under the hood:**

```
1. @contextmanager turns the generator into a _GeneratorContextManager object
2. __enter__() calls next(gen) → runs code before yield, returns yielded value
3. Your with-block body runs
4. __exit__() resumes the generator:
     - No exception: gen.send(None) → runs code after yield
     - Exception:    gen.throw(exc) → exception appears at yield point
                     if generator handles it (try/finally), cleanup runs
                     if generator re-raises or doesn't catch, exception propagates
```

**Handling exceptions inside `@contextmanager`:**

```python
@contextmanager
def transaction(conn):
    conn.execute("BEGIN")
    try:
        yield conn           # your code runs here
        conn.execute("COMMIT")   # only if no exception
    except Exception:
        conn.execute("ROLLBACK")
        raise                # re-raise after rollback
```

⚠️ **Common mistake — forgetting `try/finally`:** Code after `yield` only runs if the body exits cleanly. If the body raises, the generator is abandoned and cleanup never runs. Always wrap `yield` in `try/finally` when there is something to release.

⚠️ **Common mistake — yielding more than once:** A `@contextmanager` function must yield exactly once. Zero yields or two yields both raise `RuntimeError`. A `with` block has exactly one entry point and one exit.

💡 **Hint:** If your context manager doesn't need to hand back a value, just `yield` with nothing. The `as` variable will be `None`. `with timer("block"):` is a perfect example — there is no "resource" to return.

📝 **Practice:** [Q7 — contextmanager-generator](./practice.md#q7--contextmanager--timer-using-generator)

> [↑ Back to Top](#top)

---

<a id="5-real-production-patterns"></a>
# 5. Real Production Patterns

These are the context manager patterns you will actually write and recognize in production codebases. Each one solves a specific resource management problem that comes up repeatedly. Learn them by name — they will become second nature.

<a id="timing-context-manager"></a>
## Timing Context Manager

Your team lead asks "how long does the nightly batch job take?" You don't want to sprinkle `start = time.time()` and `elapsed = time.time() - start` manually before and after every block you care about. A timer context manager works like a stopwatch: it starts automatically when you enter the block, stops when you leave, and logs the time. Use it anywhere, zero boilerplate.

```python
import time, logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def timer(name: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info("%s completed in %.3fs", name, elapsed)

with timer("database query"):
    results = db.execute("SELECT ...")
# INFO: database query completed in 0.042s
```

💡 **Hint:** Always use `time.perf_counter()` for measuring short durations. `time.time()` reads the system clock and can jump backwards during NTP adjustments. `perf_counter()` is monotonic — it only goes forward.

<a id="temporary-directory"></a>
## Temporary Directory

You're cooking in a rental kitchen. You make a mess of intermediate ingredients (temp files), finish the dish, and the cleaning service wipes everything after you leave. Even if you burn something and have to evacuate early (exception), the kitchen gets cleaned. Without this pattern, every run of your pipeline leaves behind orphaned temp folders that silently fill up disk over weeks.

```python
import tempfile, shutil
from contextlib import contextmanager
from pathlib import Path

@contextmanager
def temp_dir():
    path = Path(tempfile.mkdtemp())
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)

with temp_dir() as d:
    (d / "output.csv").write_text("name,score\nAlice,95\n")
    process_files(d)
# Directory and all files deleted here, even if process_files raises
```

⚠️ **Common mistake — calling `tempfile.mkdtemp()` without cleanup:** `mkdtemp()` creates the directory but registers zero cleanup. If you call it outside a context manager and your code raises, the folder survives indefinitely. Python's built-in `tempfile.TemporaryDirectory()` is a ready-made context manager that handles this.

<a id="thread-lock"></a>
## Thread Lock

Imagine two chefs updating the same recipe card at the same time — one adds salt while the other removes it, and the final recipe makes no sense. A lock says "one chef at a time." Python's `threading.Lock` is already a context manager, so `with lock:` is the idiomatic way to use it. A lock-with-timeout variant surfaces deadlocks as a visible error instead of a silently frozen process.

```python
import threading

lock = threading.Lock()

with lock:
    shared_resource.modify()
# Lock released even on exception

@contextmanager
def acquire_lock(lock, timeout=5.0):
    acquired = lock.acquire(timeout=timeout)
    if not acquired:
        raise TimeoutError(f"Could not acquire lock within {timeout}s")
    try:
        yield
    finally:
        lock.release()
```

⚠️ **Common mistake — calling `lock.acquire()` manually without `with`:** If an exception fires between `acquire()` and `release()`, the lock is never released. Every thread waiting on it deadlocks. Always use `with lock:` — no exceptions.

<a id="database-connection"></a>
## Database Connection

Opening a database connection is like turning on a water tap. If you forget to turn it off — because an exception interrupted your code — the water runs forever and eventually floods the server (connection pool exhaustion). A connection context manager is the automatic shutoff valve: it commits on clean exit, rolls back on exception, and always closes the connection in `finally`.

```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_connection(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row   # dict-like row access
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()   # ALWAYS close

with get_connection("app.db") as conn:
    conn.execute("INSERT INTO events VALUES (?, ?)", (event_id, data))
```

💡 **Hint:** `conn.row_factory = sqlite3.Row` lets you access columns by name (`row["user_id"]`) instead of position (`row[0]`). Almost always the right choice.

⚠️ **Common mistake — only calling `close()` without `rollback()`:** If you skip `rollback()` after an exception, SQLite may auto-commit partial changes depending on isolation level. Always explicitly rollback before closing when an exception occurred.

<a id="redirecting-stdout"></a>
## Redirecting stdout

Some old library functions just shout everything to the terminal with `print()`. You can't stop them — the code isn't yours. `redirect_stdout` is like putting a bucket under a leaky faucet: you don't fix the leak, you just capture what drips out and decide what to do with it later. This is how `pytest` captures test output without touching the test code at all.

```python
import io
from contextlib import redirect_stdout

buffer = io.StringIO()
with redirect_stdout(buffer):
    print("This goes to buffer, not console")
    some_legacy_function_that_prints()

output = buffer.getvalue()   # "This goes to buffer, not console\n"
```

⚠️ **Common mistake — expecting it to redirect C-level output:** `redirect_stdout` only redirects Python's `sys.stdout`. C extensions that write directly to file descriptor 1 bypass Python entirely and are not captured. For OS-level capture you need `os.dup2()`.

🔍 **Good to Know:** `redirect_stderr` works identically for `sys.stderr`. You can use both together: `with redirect_stdout(out), redirect_stderr(err):`.

📝 **Practice:** [Q11 — timing-context-manager](./practice.md#q11--timing-cm--measure-and-log-elapsed-time)

> [↑ Back to Top](#top)

---

<a id="6-multiple-context-managers-in-one-with"></a>
# 6. Multiple Context Managers in One `with`

Making a sandwich: you need the bread bag open AND the deli container open at the same time. You could open the bread bag, then inside that step open the deli container (nested `with`) — but that's just putting boxes inside boxes for no reason. Python's comma syntax lets you open both side by side in one line, same indentation, same logical level.

```python
# Old nested style (works but verbose):
with open("input.txt") as fin:
    with open("output.txt", "w") as fout:
        fout.write(fin.read())

# Modern one-liner (preferred):
with open("input.txt") as fin, open("output.txt", "w") as fout:
    fout.write(fin.read())

# Three or more (Python 3.10+ parenthesized form):
with (
    open("a.txt") as a,
    open("b.txt") as b,
    open("c.txt", "w") as c,
):
    c.write(a.read() + b.read())
```

**Exit order is reverse of entry order (LIFO):**

```python
with A() as a, B() as b:
    ...
# Exit order: B.__exit__() first, then A.__exit__()
```

⚠️ **Common mistake — assuming left-to-right exit order:** The last context manager entered is the first to exit. If `B` depends on `A` still being open during its cleanup, you have a problem. Design cleanup to not depend on other managers still being alive.

💡 **Hint:** The parenthesized form (Python 3.10+) is the cleanest for 3+ managers — it supports trailing commas and reads like a regular list. For Python < 3.10, stick with the comma-separated single-line form.

📝 **Practice:** [Q15 — multiple-cms](./practice.md#q15--multiple-cms--nested-vs-one-liner)

> [↑ Back to Top](#top)

---

<a id="7-contextlibexitstack--dynamic-context-managers"></a>
# 7. `contextlib.ExitStack` — Dynamic Context Managers

You're helping a friend move house and you don't know how many boxes they have until you start packing. You can't reserve exactly 5 truck slots upfront — there might be 20. `ExitStack` is a moving truck that keeps accepting boxes as you load them, then unloads ALL of them when you arrive at the destination. In Python terms: you push context managers onto the stack at runtime with `enter_context()`, and when the outer `with ExitStack()` exits, every one of them is cleaned up in reverse order.

```python
from contextlib import ExitStack

# Open a dynamic number of files:
def merge_files(paths, output_path):
    with ExitStack() as stack:
        files = [stack.enter_context(open(p)) for p in paths]
        with open(output_path, "w") as out:
            for f in files:
                out.write(f.read())
    # All files closed here, regardless of how many

# Register arbitrary cleanup functions:
with ExitStack() as stack:
    conn = db.connect()
    stack.callback(conn.close)          # register cleanup
    stack.callback(logger.info, "done") # arbitrary callable
    data = conn.query("SELECT ...")
    process(data)
# conn.close() and logger.info("done") called on exit

# Conditionally use a context manager:
with ExitStack() as stack:
    if use_transaction:
        conn = stack.enter_context(transaction(db))
    else:
        conn = db
    do_work(conn)
```

⚠️ **Common mistake — using ExitStack when static `with` suffices:** ExitStack is for dynamic or unknown-count scenarios. If you know at write time you need exactly 2 resources, `with A() as a, B() as b:` is cleaner and more readable.

💡 **Hint:** `stack.callback(fn, *args, **kwargs)` registers any callable as cleanup — not just context managers. Perfect for objects with a `.close()` method that don't implement the context manager protocol.

🔍 **Good to Know:** If `stack.enter_context()` raises partway through a list of resources, all previously entered contexts are automatically cleaned up. ExitStack handles partial-failure rollback — no need for your own try/except around individual `enter_context` calls.

📝 **Practice:** [Q17 — exitstack-n-files](./practice.md#q17--exitstack--merge-n-files-at-runtime)

> [↑ Back to Top](#top)

---

<a id="8-contextlibnullcontext--conditional-context-managers"></a>
# 8. `contextlib.nullcontext` — Conditional Context Managers

Sometimes a seat belt is optional — on a slow carnival ride you might skip it, but you still want the same ride code either way. You don't want to duplicate the entire `with` block just to handle the "no lock needed" case. `nullcontext` is the invisible seat belt: it clips in, does nothing, unclips. Your code runs identically whether a real context manager or `nullcontext` is passed in.

```python
from contextlib import nullcontext

def process(data, lock=None):
    """Optionally use a lock."""
    ctx = lock if lock is not None else nullcontext()
    with ctx:
        do_work(data)

# With a return value:
def open_file(path=None):
    ctx = open(path) if path else nullcontext(default_content)
    with ctx as content:
        process(content)
```

💡 **Hint:** `nullcontext(enter_result)` takes an optional argument — that value becomes the `as` variable. `nullcontext()` with no argument gives `None` as the `as` value.

🔍 **Good to Know:** `nullcontext` was added in Python 3.7. For older code you may see `@contextmanager` with a trivial `yield` used as a workaround — `nullcontext` is the cleaner replacement.

📝 **Practice:** [Q20 — nullcontext-optional-lock](./practice.md#q20--nullcontext--optional-lock-pattern)

> [↑ Back to Top](#top)

---

<a id="9-async-context-managers"></a>
# 9. Async Context Managers

You already know sync context managers — async context managers are the same idea with one twist. In async Python, operations like connecting to a database or closing a connection take time and must be `await`ed. Regular `__enter__` and `__exit__` are normal methods — they can't `await` anything. So Python adds `__aenter__` and `__aexit__` as their async twins, and `async with` to call them. Same lifecycle, same cleanup guarantee, just async-friendly.

```python
class AsyncDBConnection:
    def __init__(self, dsn):
        self.dsn  = dsn
        self.conn = None

    async def __aenter__(self):
        self.conn = await asyncpg.connect(self.dsn)
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.conn.execute("ROLLBACK")
        else:
            await self.conn.execute("COMMIT")
        await self.conn.close()
        return False

async def main():
    async with AsyncDBConnection("postgres://...") as conn:
        await conn.execute("INSERT INTO ...")
```

**`@asynccontextmanager` — the generator shortcut for async:**

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def async_timer(name: str):
    import time
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{name}: {elapsed:.3f}s")

async with async_timer("fetch"):
    data = await fetch_data()
```

⚠️ **Common mistake — using `with` instead of `async with`:** Using `with` on an async context manager tries to call the sync `__enter__`, which may not exist. Inside `async def` functions, always use `async with` for async context managers.

💡 **Hint:** `AsyncExitStack` is the async counterpart to `ExitStack`. Use `await stack.enter_async_context(cm)` for dynamic async resource management — same API, fully awaitable.

🔍 **Good to Know:** Python 3.11 added `asyncio.timeout(seconds)` as a built-in async context manager: `async with asyncio.timeout(5.0): await slow_op()`. Clean way to add timeouts without manual task cancellation.

📝 **Practice:** [Q21 — async-context-manager](./practice.md#q21--async-cm--write-asyncdbconnection)

> [↑ Back to Top](#top)

---

<a id="10-contextlib--the-full-toolkit"></a>
# 10. `contextlib` — The Full Toolkit

Think of `contextlib` as a fully stocked kitchen drawer for context managers. Instead of building a cutting board from scratch every time you need one, you open the drawer and grab the right tool. It has a tool for almost every pattern: turning a generator into a context manager, suppressing exceptions, redirecting I/O, composing dynamic stacks, wrapping old objects. In day-to-day Python, you reach into this drawer far more often than you build context manager classes by hand.

```python
from contextlib import (
    contextmanager,       # generator → context manager
    asynccontextmanager,  # async generator → async context manager
    suppress,             # suppress specified exceptions
    nullcontext,          # no-op context manager
    ExitStack,            # dynamic stack of context managers
    AsyncExitStack,       # async version of ExitStack
    redirect_stdout,      # redirect sys.stdout
    redirect_stderr,      # redirect sys.stderr
    closing,              # call .close() on exit
    AbstractContextManager,  # base class for context managers
)

# suppress:
with suppress(FileNotFoundError, OSError):
    os.remove("temp.txt")

# closing — wrap any object with .close() that is not a context manager:
from urllib.request import urlopen
with closing(urlopen("http://example.com")) as response:
    data = response.read()

# nullcontext — conditional context:
with (lock if need_lock else nullcontext()):
    modify_shared_resource()
```

💡 **Hint:** `contextlib.closing(obj)` is the right tool when you're working with older libraries that return objects with a `.close()` method but predate the context manager protocol. Common when wrapping legacy network or file objects.

🔍 **Good to Know:** `contextlib.suppress` accepts multiple exception types in one call — `suppress(FileNotFoundError, PermissionError)`. You don't need to nest multiple suppress blocks.

📝 **Practice:** [Q26 — contextlib-closing](./practice.md#q26--contextlibclosing--wrap-legacy-object)

> [↑ Back to Top](#top)

---

<a id="11-gotchas-and-anti-patterns"></a>
# 11. Gotchas and Anti-Patterns

Context managers look deceptively simple. Most of the bugs below don't crash loudly — they silently swallow errors or leak resources, which makes them much harder to find than a plain `AttributeError`. These five patterns come up in code reviews again and again.

<a id="gotcha-1--returning-true-suppresses-all-exceptions"></a>
## Gotcha 1 — Returning `True` suppresses all exceptions

⚠️ Accidentally returning `True` from `__exit__` makes your context manager silently swallow every exception — `KeyboardInterrupt`, `SystemExit`, a `TypeError` from your own bug — everything. The caller gets no signal anything went wrong.

```python
class BadContextManager:
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return True   # ← DANGER: swallows ALL exceptions silently!

# Fix: only return True for specific, intended suppressions:
def __exit__(self, exc_type, exc_val, exc_tb):
    self.cleanup()
    return exc_type is not None and issubclass(exc_type, ExpectedError)
```

💡 **Hint:** If you're not intentionally suppressing, either `return False` explicitly or omit the return — `None` is falsy and lets exceptions propagate.

<a id="gotcha-2--not-re-raising-in-contextmanager"></a>
## Gotcha 2 — Not re-raising in `@contextmanager`

⚠️ A bare `except Exception: pass` inside a `@contextmanager` silently swallows everything the `with` block raises. Errors vanish without a traceback. This is the generator-based equivalent of Gotcha 1, and harder to spot.

```python
@contextmanager
def bad():
    try:
        yield
    except Exception:
        pass   # ← DANGER: swallows all exceptions from the with-block!

# Fix:
@contextmanager
def good():
    try:
        yield
    except SomeSpecificError as e:
        handle(e)   # intentional suppression
    except Exception:
        raise       # re-raise everything else
```

<a id="gotcha-3--forgetting-tryfinally-in-contextmanager"></a>
## Gotcha 3 — Forgetting `try/finally` in `@contextmanager`

⚠️ Code after `yield` only runs if the body exits cleanly. If the body raises, the generator is abandoned and cleanup code never runs. The resource leaks silently.

```python
@contextmanager
def leaky():
    resource = acquire()
    yield resource        # ← if exception here, release() never runs!
    release(resource)     # ← NOT reached on exception

# Fix:
@contextmanager
def safe():
    resource = acquire()
    try:
        yield resource
    finally:
        release(resource)  # ← guaranteed no matter what
```

<a id="gotcha-4--using-context-manager-as-non-context"></a>
## Gotcha 4 — Using context manager as non-context

⚠️ Calling `open()` gives you a file object — it does NOT call `__enter__`. The file is open but there is no cleanup guarantee. CPython's reference counting usually closes it quickly, but PyPy and Jython do not. Code that relies on CPython's GC for file cleanup is not portable.

```python
f = open("file.txt")   # risky — no cleanup guarantee
data = f.read()

# Always use 'with':
with open("file.txt") as f:
    data = f.read()
```

💡 **Hint:** Linters like `flake8` and `pylint` flag bare `open()` calls outside a `with` block. Turn on those warnings to catch this automatically.

<a id="gotcha-5--__exit__-not-called-if-__enter__-raises"></a>
## Gotcha 5 — `__exit__` not called if `__enter__` raises

⚠️ Python's guarantee: if `__enter__` completes successfully, `__exit__` will be called. But if `__enter__` itself raises, `__exit__` is never called. Any partial resource allocation before the raise leaks silently.

```python
class Broken:
    def __enter__(self):
        self.resource = acquire()
        raise RuntimeError("setup failed")   # ← __exit__ will NOT be called!

    def __exit__(self, *args):
        self.resource.release()   # ← never runs if __enter__ raised

# Fix: guard the setup and clean up manually if it fails:
def __enter__(self):
    try:
        self.resource = acquire()
        self.resource.setup()
        return self.resource
    except Exception:
        if self.resource:
            self.resource.release()
        raise
```

📝 **Practice:** [Q23 — gotcha-return-true](./practice.md#q23--gotcha-return-true--fix-accidental-suppression)

> [↑ Back to Top](#top)

---

<a id="12-the-full-mental-model"></a>
# 12. The Full Mental Model

Every `with` block — simple or complex — follows the same four steps. Think of it like a contractor: they show up (enter), do the work (body), and always clean up before leaving (exit) — whether the job went perfectly or something broke midway. The guarantee starts the moment `__enter__` returns successfully. Once that happens, `__exit__` will run no matter what.

```
FLOW DIAGRAM:
─────────────────────────────────────────────────────────────────

with EXPR as VAR:
    BODY

─────────────────────────────────────────────────────────────────
     │
     ▼
cm = EXPR                      ← evaluate the expression

     │
     ▼
VAR = cm.__enter__()           ← setup; VAR is the 'as' value
     │
     │  [if __enter__ raises → exception propagates, __exit__ NOT called]
     │
     ▼
try:
    BODY                       ← your with-block code
except:
    if cm.__exit__(type, val, tb):   ← cleanup on exception
        pass                         ← True: suppress
    else:
        raise                        ← False/None: propagate
else:
    cm.__exit__(None, None, None)    ← cleanup, no exception
─────────────────────────────────────────────────────────────────
```

💡 **Key insight:** The guarantee is not symmetric. If `__enter__` raises → `__exit__` does NOT run. If `__enter__` succeeds and the body raises → `__exit__` DOES run. The cleanup contract begins only after successful entry.

📝 **Practice:** [Q30 — capstone: ConnectionPool](./practice.md#q30--capstone--build-connectionpool-with-exitstack)

<a id="-summary"></a>
## 🔥 Summary

```
CONCEPT                     DESCRIPTION
────────────────────────────────────────────────────────────────────────
with statement              Guaranteed setup + cleanup around a block
__enter__(self)             Setup phase; return value goes to 'as' var
__exit__(self, t, v, tb)    Cleanup phase; return True to suppress exc
@contextmanager             Generator approach: code before yield = setup,
                            code after yield = cleanup, try/finally required
contextlib.suppress()       Suppress specific exception types
contextlib.ExitStack        Dynamically compose context managers
contextlib.nullcontext      No-op; used for optional context managers
contextlib.closing          Call .close() on any object
async with                  Calls __aenter__ / __aexit__
@asynccontextmanager        Generator approach for async
Multiple with               with A() as a, B() as b — exits in reverse order
```

> [↑ Back to Top](#top)

---

## 🔁 Navigation

**[🏠 Back to README](../../README.md)**

| | |
|---|---|
| ⬅ Prev Module | [11 — Generators & Iterators](../11_generators_iterators/theory.md) |
| ➡ Next Module | [13 — Concurrency](../13_concurrency/theory.md) |

**This folder:**
[theory.md](./theory.md) · [cheetsheet.md](./cheetsheet.md) · [interview.md](./interview.md) · [practice.md](./practice.md) · [contextlib_guide.md](./contextlib_guide.md)

**Related modules:**
[10 — Decorators](../10_decorators/theory.md) · [11 — Generators & Iterators](../11_generators_iterators/theory.md) · [13 — Concurrency](../13_concurrency/theory.md) · [06 — Exceptions](../06_exceptions_error_handling/theory.md)

**Jump to specific topics:**
[`@contextmanager` decorator](../10_decorators/theory.md) · [Generator functions & yield](../11_generators_iterators/theory.md#-chapter-3-generator-functions--yield) · [asyncio basics](../13_concurrency/theory.md) · [Exception handling](../06_exceptions_error_handling/theory.md)
