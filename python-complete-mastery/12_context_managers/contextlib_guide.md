# 🛠️ contextlib_guide.md — The contextlib Module, Deep Dive

> Every tool in Python's `contextlib` module with practical examples,
> when to use each, and common mistakes.

---

## 📋 Module Overview

```python
from contextlib import (
    # Function decorators:
    contextmanager,        # generator → context manager
    asynccontextmanager,   # async generator → async context manager

    # Ready-made context managers:
    suppress,              # ignore specific exceptions
    nullcontext,           # no-op placeholder
    redirect_stdout,       # redirect sys.stdout
    redirect_stderr,       # redirect sys.stderr
    closing,               # call .close() on exit

    # Stack-based composition:
    ExitStack,             # dynamically compose context managers
    AsyncExitStack,        # async version

    # Base classes:
    AbstractContextManager,
    AbstractAsyncContextManager,
)
```

---

## 1. `@contextmanager` — Generator-Based Context Managers

**The most-used tool.** Converts a generator function into a context manager without writing a class.

### Basic Pattern

```python
from contextlib import contextmanager

@contextmanager
def managed_connection(dsn):
    conn = db.connect(dsn)
    try:
        yield conn          # ← 'as' variable = conn
    finally:
        conn.close()        # ← runs even on exception

with managed_connection("postgres://...") as conn:
    conn.execute("SELECT ...")
```

### Handling Exceptions

```python
@contextmanager
def transaction(conn):
    """Commit on success, rollback on failure."""
    conn.begin()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise           # always re-raise unless you intend to suppress

@contextmanager
def suppress_transient(conn):
    """Selectively suppress specific errors."""
    try:
        yield conn
    except TransientError as e:
        logger.warning("Transient error suppressed: %s", e)
        # don't re-raise → suppressed
    except Exception:
        raise           # everything else propagates
```

### Setup Code That Can Fail

```python
@contextmanager
def safe_acquire(resource):
    """Handle errors during setup."""
    r = None
    try:
        r = resource.acquire()
        yield r
    except AcquisitionError:
        # __enter__ equivalent raised → clean up anything partially done
        raise
    finally:
        if r is not None:
            r.release()
```

### Wrapping Existing Objects

```python
@contextmanager
def timed(label):
    """Time any block of code."""
    import time
    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"{label}: {time.perf_counter() - start:.3f}s")

with timed("database query"):
    results = db.fetchall("SELECT ...")
```

---

## 2. `@asynccontextmanager` — Async Generator Context Managers

Same as `@contextmanager` but for `async def`:

```python
from contextlib import asynccontextmanager
import asyncpg

@asynccontextmanager
async def async_db(dsn):
    conn = await asyncpg.connect(dsn)
    try:
        yield conn
    finally:
        await conn.close()

@asynccontextmanager
async def async_transaction(dsn):
    async with async_db(dsn) as conn:
        await conn.execute("BEGIN")
        try:
            yield conn
            await conn.execute("COMMIT")
        except Exception:
            await conn.execute("ROLLBACK")
            raise

# Usage:
async def process():
    async with async_transaction("postgres://...") as conn:
        await conn.execute("INSERT INTO orders ...")
```

---

## 3. `suppress(*exceptions)` — Ignore Specific Exceptions

```python
from contextlib import suppress

# Replace verbose try/except/pass:
try:
    os.remove("temp.txt")
except FileNotFoundError:
    pass

# With suppress — same thing, cleaner:
with suppress(FileNotFoundError):
    os.remove("temp.txt")

# Multiple exception types:
with suppress(FileNotFoundError, PermissionError):
    os.remove("protected.txt")

# Real production uses:
# 1. Delete files that might not exist:
with suppress(FileNotFoundError):
    cache_path.unlink()

# 2. Pop from dict that might not have key:
with suppress(KeyError):
    del cache[stale_key]

# 3. Registry cleanup that might already be gone:
with suppress(KeyError, AttributeError):
    self._registry.deregister(self.name)
```

**When NOT to use suppress:**
```python
# ❌ Too broad — hides real bugs:
with suppress(Exception):
    process_payment(order)   # payment might silently fail!

# ✅ Narrow — only suppress what you expect and intend:
with suppress(CacheKeyNotFound):
    return cache.get(key)
```

---

## 4. `nullcontext(enter_result=None)` — Optional Context Managers

Use when you need a context manager but don't always want one:

```python
from contextlib import nullcontext

# ❌ Awkward conditional:
if use_lock:
    with lock:
        do_work()
else:
    do_work()   # duplicated!

# ✅ nullcontext:
ctx = lock if use_lock else nullcontext()
with ctx:
    do_work()

# With a value:
def process(data, conn=None):
    ctx = nullcontext(conn) if conn else get_connection()
    with ctx as c:
        c.execute("SELECT ...")

# In tests — replace real context managers with no-ops:
@patch("myapp.get_lock", return_value=nullcontext())
def test_process(mock_lock):
    process_data()   # runs without actually acquiring a lock
```

---

## 5. `redirect_stdout` / `redirect_stderr`

Capture or redirect output streams:

```python
from contextlib import redirect_stdout, redirect_stderr
import io

# Capture print() output:
buf = io.StringIO()
with redirect_stdout(buf):
    print("Hello, World!")
    some_legacy_function_with_print_debugging()

captured = buf.getvalue()   # "Hello, World!\n..."

# Redirect to file:
with open("output.log", "w") as f, redirect_stdout(f):
    run_verbose_script()

# Suppress stderr from noisy libraries:
with open(os.devnull, "w") as devnull, redirect_stderr(devnull):
    noisy_library.run()

# In tests — assert on output:
def test_report():
    buf = io.StringIO()
    with redirect_stdout(buf):
        generate_report()
    assert "Total: 42" in buf.getvalue()
```

---

## 6. `closing(thing)` — Auto-Close Any Object

Wraps any object with a `.close()` method as a context manager, even if it doesn't implement `__enter__`/`__exit__`:

```python
from contextlib import closing
from urllib.request import urlopen

# Objects without context manager support:
with closing(urlopen("http://example.com")) as resp:
    data = resp.read()
# resp.close() called on exit

# Database cursor:
with closing(conn.cursor()) as cursor:
    cursor.execute("SELECT ...")
    rows = cursor.fetchall()
# cursor.close() called on exit

# Any object with .close():
class LegacyResource:
    def close(self):
        print("closed!")
    def use(self):
        print("using")

with closing(LegacyResource()) as r:
    r.use()
# "using"
# "closed!"
```

---

## 7. `ExitStack` — Dynamic Composition

The most powerful contextlib tool for production code.

### Pattern 1: Dynamic Number of Resources

```python
from contextlib import ExitStack

def merge_files(input_paths, output_path):
    """Merge N CSV files into one. N determined at runtime."""
    with ExitStack() as stack:
        readers = [
            stack.enter_context(open(p, newline=""))
            for p in input_paths
        ]
        writer = stack.enter_context(open(output_path, "w", newline=""))
        # All files open here, all guaranteed to close at exit
        for reader in readers:
            writer.write(reader.read())
```

### Pattern 2: Callback Registration

```python
def process_job(job_id):
    with ExitStack() as stack:
        # Register cleanup callbacks (run in LIFO order on exit):
        stack.callback(metrics.record, "job.completed", job_id)
        stack.callback(logger.info, "Job %s finished", job_id)

        conn = db.connect()
        stack.callback(conn.close)   # not a context manager but has cleanup

        return run_job(job_id, conn)
```

### Pattern 3: Conditional Stack

```python
def export_data(data, compress=False, encrypt=False):
    with ExitStack() as stack:
        fh = stack.enter_context(open("output.dat", "wb"))

        if compress:
            import gzip
            fh = stack.enter_context(gzip.open(fh, "wb"))

        if encrypt:
            fh = stack.enter_context(encrypt_stream(fh))

        serialize(data, fh)
```

### Pattern 4: Transfer Ownership

```python
def open_connections(hosts):
    """
    Open connections and return them. Caller is responsible for cleanup.
    """
    stack = ExitStack()
    try:
        conns = [stack.enter_context(connect(h)) for h in hosts]
    except Exception:
        stack.close()   # clean up on failure
        raise
    return conns, stack   # caller calls stack.close() or uses it as context manager

# Caller:
conns, stack = open_connections(["host1", "host2"])
with stack:
    process(conns)
```

### Pattern 5: ExitStack in a Class

```python
class ConnectionPool:
    def __init__(self, hosts):
        self._stack = ExitStack()
        self._conns = [
            self._stack.enter_context(connect(h))
            for h in hosts
        ]

    def close(self):
        self._stack.close()   # closes all connections

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
        return False
```

---

## 8. `AsyncExitStack` — Async Dynamic Composition

Same as `ExitStack` but for async context managers:

```python
from contextlib import AsyncExitStack

async def open_async_connections(dsns):
    async with AsyncExitStack() as stack:
        conns = [
            await stack.enter_async_context(AsyncDB(dsn))
            for dsn in dsns
        ]
        results = await asyncio.gather(*[c.query("SELECT ...") for c in conns])
    # All connections closed here
    return results
```

---

## 9. `AbstractContextManager` — Base Class

For type hints and enforcing the protocol:

```python
from contextlib import AbstractContextManager

class MyManager(AbstractContextManager):
    """Subclass gets default __enter__ (returns self) and forces __exit__ override."""

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return False

# AbstractContextManager provides:
# - __enter__(self) → return self  (can be overridden)
# - __exit__(self, ...) → abstract, must be implemented
# - classmethod __subclasshook__ for isinstance() checks
```

---

## 🎯 Decision Guide: Which Tool to Use?

```
SITUATION                                    USE
──────────────────────────────────────────────────────────────────────────────
Simple resource (acquire → use → release)   @contextmanager
Need state between __enter__ and __exit__   class with __enter__/__exit__
Suppress specific exceptions                contextlib.suppress()
Optionally use a context manager            contextlib.nullcontext()
Open N files determined at runtime          contextlib.ExitStack
Mix of context managers and callbacks       contextlib.ExitStack
Redirect print() to capture output          contextlib.redirect_stdout
Close a non-context-manager object          contextlib.closing
Async resource management                   @asynccontextmanager
Async dynamic composition                   AsyncExitStack
```

---

## 🔴 Common Mistakes

```python
# 1 — Forgetting try/finally in @contextmanager:
@contextmanager
def bad():
    r = acquire()
    yield r
    release(r)   # NOT called on exception!

# 2 — Swallowing all exceptions in @contextmanager:
@contextmanager
def dangerous():
    try:
        yield
    except Exception:
        pass   # silently hides ALL errors from the with-block

# 3 — Reusing a @contextmanager instance:
cm = my_cm()
with cm: ...
with cm: ...   # RuntimeError

# 4 — Using suppress too broadly:
with suppress(Exception):   # hides ALL bugs
    critical_operation()

# 5 — Forgetting to call stack.close() if ExitStack escapes the with:
stack = ExitStack()
resources = [stack.enter_context(open(p)) for p in paths]
# If you return resources without returning stack, nothing gets cleaned up!
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ➡️ Next | [13 — Concurrency](../13_concurrency/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
