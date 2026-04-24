# 🧩 Context Managers — Theory

> *"A context manager is a contract: 'I promise to clean up after myself,*
> *no matter what happens.' It is the foundation of resource-safe Python."*

---

## 🎬 The Problem: Resource Leaks in the Wild

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

## 🔑 Chapter 1: The `with` Statement — What Actually Happens

```python
with open("config.json") as f:
    data = json.load(f)
```

Under the hood, Python runs **exactly this**:

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

---

## 🏗️ Chapter 2: The Context Manager Protocol

Any class that implements `__enter__` and `__exit__` is a context manager:

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
        """Cleanup: always runs, even on exception.

        Parameters:
          exc_type  — exception class (None if no exception)
          exc_val   — exception instance (None if no exception)
          exc_tb    — traceback object (None if no exception)

        Returns:
          True  → suppress the exception (it doesn't propagate)
          False/None → let the exception propagate
        """
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

---

## ✨ Chapter 3: Suppressing Exceptions with `__exit__`

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


# If file doesn't exist: no exception raised — execution continues normally
# If IOError: propagates normally

# Real-world example:
with SuppressErrors(KeyError):
    del cache[key]   # silently skip if key not present
```

> 📝 **Practice:** [Q37 · context-manager-exception](../python_practice_questions_100.md#q37--thinking--context-manager-exception)


**The built-in equivalent:** `contextlib.suppress()`:

```python
from contextlib import suppress

with suppress(FileNotFoundError):
    os.remove("temp_file.txt")   # no error if file doesn't exist
```

---

## 🌿 Chapter 4: `@contextmanager` — Generator-Based Context Managers

Writing a full class for every context manager is verbose. The [`@contextmanager`](../10_decorators/theory.md) decorator lets you use a [generator function](../11_generators_iterators/theory.md#-chapter-3-generator-functions--yield) instead:

```python
from contextlib import contextmanager

@contextmanager
def managed_file(path, mode="r", encoding="utf-8"):
    """Generator-based context manager."""
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
                     if generator handles it (try/finally), __exit__ runs
                     if generator re-raises or doesn't catch, exception propagates
```

**Handling exceptions inside `@contextmanager`:**

```python
@contextmanager
def transaction(conn):
    """Begin/commit/rollback a database transaction."""
    conn.execute("BEGIN")
    try:
        yield conn           # your code runs here
        conn.execute("COMMIT")   # only if no exception
    except Exception:
        conn.execute("ROLLBACK")
        raise                # re-raise after rollback

with transaction(db) as conn:
    conn.execute("INSERT INTO orders ...", data)
    conn.execute("UPDATE inventory ...", data)


# Commits if both succeed. Rolls back if either fails.
```

> 📝 **Practice:** [Q38 · contextlib](../python_practice_questions_100.md#q38--normal--contextlib)


---

## 🏭 Chapter 5: Real Production Patterns

### Timing Context Manager

```python
import time, logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def timer(name: str):
    """Measure and log elapsed time of a block."""
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

### Temporary Directory

```python
import tempfile, shutil
from contextlib import contextmanager
from pathlib import Path

@contextmanager
def temp_dir():
    """Create a temporary directory, clean it up on exit."""
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

### Thread Lock

```python
import threading

lock = threading.Lock()

# Python's threading.Lock() is already a context manager:
with lock:
    shared_resource.modify()
# Lock released even on exception

# Custom lock with timeout:
@contextmanager
def acquire_lock(lock, timeout=5.0):
    """Acquire lock with timeout. Raise if can't acquire."""
    acquired = lock.acquire(timeout=timeout)
    if not acquired:
        raise TimeoutError(f"Could not acquire lock within {timeout}s")
    try:
        yield
    finally:
        lock.release()
```

### Database Connection

```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_connection(db_path: str):
    """Manage DB connection lifecycle."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row   # dict-like row access
    try:
        yield conn
        conn.commit()   # auto-commit on clean exit
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()   # ALWAYS close

with get_connection("app.db") as conn:
    conn.execute("INSERT INTO events VALUES (?, ?)", (event_id, data))
```

### Redirecting stdout

```python
import io
from contextlib import redirect_stdout, redirect_stderr

# Capture print() output:
buffer = io.StringIO()
with redirect_stdout(buffer):
    print("This goes to buffer, not console")
    some_legacy_function_that_prints()

output = buffer.getvalue()   # "This goes to buffer, not console\n"
```

---

## 🔗 Chapter 6: Multiple Context Managers in One `with`

Python 3.1+ allows multiple context managers in a single `with`:

```python


# Old nested style (works but verbose):
with open("input.txt") as fin:
    with open("output.txt", "w") as fout:
        fout.write(fin.read())

# Modern one-liner (preferred):
with open("input.txt") as fin, open("output.txt", "w") as fout:
    fout.write(fin.read())

# Three or more:
with (   # parenthesized form (Python 3.10+) — supports trailing comma
    open("a.txt") as a,
    open("b.txt") as b,
    open("c.txt", "w") as c,
):
    c.write(a.read() + b.read())
```

> 📝 **Practice:** [Q36 · context-managers](../python_practice_questions_100.md#q36--normal--context-managers)


**Each context manager's `__exit__` is called in reverse order** (last opened, first closed — LIFO):

```python
with A() as a, B() as b:
    ...
# Exit order: B.__exit__() first, then A.__exit__()
```

---

## 📚 Chapter 7: `contextlib.ExitStack` — Dynamic Context Managers

When you don't know how many context managers you need at write time:

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
        conn = db   # no transaction
    do_work(conn)
```

---

## 🔄 Chapter 8: `contextlib.nullcontext` — Conditional Context Managers

Sometimes you want to optionally use a context manager:

```python
from contextlib import nullcontext

def process(data, lock=None):
    """Optionally use a lock."""
    ctx = lock if lock is not None else nullcontext()
    with ctx:
        do_work(data)

# Or with any value:
def open_file(path=None):
    ctx = open(path) if path else nullcontext(default_content)
    with ctx as content:
        process(content)
```

---

## ⚡ Chapter 9: Async Context Managers

For async code, implement `__aenter__` and `__aexit__`:

```python
import asyncio

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

**Generator-based async context manager:**

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

---

## 🧰 Chapter 10: `contextlib` — The Full Toolkit

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

# contextmanager:
@contextmanager
def managed(resource):
    r = acquire(resource)
    try: yield r
    finally: release(r)

# suppress:
with suppress(FileNotFoundError, OSError):
    os.remove("temp.txt")

# closing — wrap any object with .close():
from urllib.request import urlopen
with closing(urlopen("http://example.com")) as response:
    data = response.read()

# nullcontext — conditional context:
with (lock if need_lock else nullcontext()):
    modify_shared_resource()
```

---

## 🚧 Chapter 11: Gotchas and Anti-Patterns

### Gotcha 1 — Returning `True` accidentally suppresses exceptions

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

### Gotcha 2 — Not re-raising in `@contextmanager`

```python
@contextmanager
def bad():
    try:
        yield
    except Exception:
        pass   # ← DANGER: swallows all exceptions from the with-block!

# Fix: always re-raise unless you intend to suppress:
@contextmanager
def good():
    try:
        yield
    except SomeSpecificError as e:
        handle(e)
        # don't re-raise — intentional suppression
    except Exception:
        raise   # ← re-raise everything else
```

### Gotcha 3 — Forgetting `try/finally` in `@contextmanager`

```python
@contextmanager
def leaky():
    resource = acquire()
    yield resource           # ← if exception here, release() never runs!
    release(resource)        # ← NOT reached on exception

# Fix: always use try/finally:
@contextmanager
def safe():
    resource = acquire()
    try:
        yield resource
    finally:
        release(resource)   # ← guaranteed
```

### Gotcha 4 — Using context manager as non-context

```python
cm = open("file.txt")   # returns file object, does NOT call __enter__!
data = cm.read()        # risky — no guarantee of close

# File objects ARE their own context managers, but:
# You must use 'with' to trigger __enter__/__exit__
# Just calling open() is safe for file objects because CPython's reference
# counting closes them quickly, BUT it's not guaranteed in PyPy or other implementations.
```

### Gotcha 5 — `__exit__` not called if `__enter__` raises

```python
class Broken:
    def __enter__(self):
        self.resource = acquire()
        raise RuntimeError("setup failed")   # ← __exit__ will NOT be called!

    def __exit__(self, *args):
        self.resource.release()   # ← never runs if __enter__ raised

# Fix: protect the setup inside __enter__:
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

---

## 🧠 Chapter 12: The Full Mental Model

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

---

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

---

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🛠️ contextlib Guide | [contextlib_guide.md](./contextlib_guide.md) |
| ➡️ Next | [13 — Concurrency](../13_concurrency/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Generators Iterators — Interview Q&A](../11_generators_iterators/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Contextlib Guide](./contextlib_guide.md) · [Interview Q&A](./interview.md)
