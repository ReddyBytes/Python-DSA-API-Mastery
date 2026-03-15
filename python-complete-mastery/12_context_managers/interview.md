# 🎯 Context Managers — Interview Questions

> *"Context manager questions reveal whether you understand resource safety,*
> *exception flow, and whether you've built systems that must be reliable."*

---

## 📊 Question Map

```
LEVEL 1 — Junior (0–2 years)
  • What is a context manager?
  • What does 'with' do internally?
  • __enter__ and __exit__ roles
  • Why not just use try/finally?

LEVEL 2 — Mid-Level (2–5 years)
  • __exit__ parameters and suppression
  • @contextmanager generator approach
  • Multiple context managers in one with
  • contextlib tools (suppress, ExitStack, nullcontext)

LEVEL 3 — Senior (5+ years)
  • ExitStack for dynamic composition
  • Async context managers
  • Designing transactional patterns
  • Gotchas: __enter__ raising, accidental suppression
  • Class-based vs generator-based trade-offs
```

---

## 🟢 Level 1 — Junior Questions

---

### Q1: What is a context manager and why do we need it?

**Weak answer:** "It's used with `with open()` to close files."

**Strong answer:**

> A context manager is any object that implements `__enter__` and `__exit__`. It guarantees that cleanup code runs **unconditionally** — even if an exception occurs, even if you `return` early, even if the process receives a signal.
>
> Without context managers, resource management is fragile:

```python
# ❌ Fragile — exception in validate() leaks the file handle:
def load_config(path):
    f = open(path)
    data = json.load(f)
    validate(data)    # ← if this raises, f.close() never runs
    f.close()
    return data

# ✅ Safe — file closes no matter what:
def load_config(path):
    with open(path) as f:
        data = json.load(f)
    validate(data)   # exception here is fine — file already closed
    return data
```

> The value is in the **guarantee**, not just the convenience.

---

### Q2: What does `with EXPR as VAR` actually do under the hood?

**Strong answer:**

> Python translates `with` into a precise sequence:

```python
with open("file.txt") as f:
    data = f.read()

# ↓ Equivalent to:
_cm = open("file.txt")
f   = _cm.__enter__()        # setup; returns the file handle
try:
    data = f.read()          # your block
except:
    if not _cm.__exit__(*sys.exc_info()):
        raise                # re-raise if __exit__ returns falsy
else:
    _cm.__exit__(None, None, None)  # no exception
```

> Key: `__exit__` is **always** called, with or without an exception. The `as f` variable receives whatever `__enter__()` returns.

---

### Q3: What are `__enter__` and `__exit__`?

**Strong answer:**

```python
class ManagedResource:
    def __enter__(self):
        """
        Called at the TOP of the with block.
        - Perform setup (open connection, acquire lock, start timer)
        - Return value goes to the 'as' variable
        - If this raises, __exit__ is NOT called
        """
        self.resource = acquire()
        return self.resource   # ← 'as' variable

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called at the BOTTOM of the with block — always.

        exc_type: exception class, or None
        exc_val:  exception instance, or None
        exc_tb:   traceback, or None

        Return True  → suppress the exception
        Return False → let it propagate
        """
        release(self.resource)
        return False   # don't suppress
```

---

### Q4: Why use context managers instead of `try/finally`?

**Strong answer:**

> `try/finally` works but is verbose and error-prone at scale. Context managers encapsulate the pattern so it can be **reused**, **composed**, and **named**.

```python
# try/finally — must repeat for every use:
conn = db.connect()
try:
    conn.execute(query)
    conn.commit()
except Exception:
    conn.rollback()
    raise
finally:
    conn.close()   # must remember this every time

# Context manager — define once, reuse everywhere:
with db_transaction() as conn:
    conn.execute(query)
# commit/rollback/close handled by the context manager

# Additional advantages:
# - Composable (with A() as a, B() as b:)
# - Testable (can mock __enter__/__exit__)
# - Readable (named abstractions)
# - Prevents forgetting cleanup
```

---

## 🔵 Level 2 — Mid-Level Questions

---

### Q5: What are the three parameters of `__exit__` and what do they mean?

**Strong answer:**

```python
def __exit__(self, exc_type, exc_val, exc_tb):
    #              │          │        │
    #              │          │        └── traceback.TracebackType or None
    #              │          └── the exception instance (e.g., ValueError("bad"))
    #              └── the exception class (e.g., ValueError)
    ...
```

> All three are `None` when no exception occurred. If an exception did occur, all three carry the full exception info (same as `sys.exc_info()`).

```python
def __exit__(self, exc_type, exc_val, exc_tb):
    self.cleanup()

    # Suppress only specific exceptions:
    if exc_type is not None and issubclass(exc_type, (KeyError, ValueError)):
        logging.warning("Suppressed %s: %s", exc_type.__name__, exc_val)
        return True   # suppress

    return False   # let everything else propagate

# Check if any exception occurred:
if exc_type is not None:
    log_error(exc_val)

# Inspect the traceback:
if exc_tb is not None:
    import traceback
    traceback.print_tb(exc_tb)
```

---

### Q6: How do you write a context manager using `@contextmanager`?

**Weak answer:** "Use yield instead of `__enter__`/`__exit__`."

**Strong answer:**

> `@contextmanager` turns a generator function into a context manager. Code before `yield` = `__enter__`. Code after `yield` = `__exit__`. You **must** use `try/finally` to guarantee cleanup.

```python
from contextlib import contextmanager

@contextmanager
def db_transaction(conn):
    """Begin/commit/rollback a transaction."""
    conn.execute("BEGIN")
    try:
        yield conn           # ← body of 'with' runs here
        conn.execute("COMMIT")   # only if no exception
    except Exception:
        conn.execute("ROLLBACK")
        raise               # ← re-raise after cleanup

    # Note: finally always runs, but commit/rollback logic requires try/except

# Usage:
with db_transaction(db) as conn:
    conn.execute("INSERT ...")
    conn.execute("UPDATE ...")
# Commits if both succeed, rolls back if either fails
```

> **Common mistake:** forgetting `try/finally` — if an exception occurs at `yield`, code after `yield` never runs.

```python
@contextmanager
def leaky():
    resource = acquire()
    yield resource
    release(resource)   # ← NOT called if exception in with-block!

@contextmanager
def safe():
    resource = acquire()
    try:
        yield resource
    finally:
        release(resource)   # ← guaranteed
```

---

### Q7: What does `contextlib.suppress()` do and when would you use it?

**Strong answer:**

> `suppress(*exceptions)` is a context manager that silently absorbs specific exception types. It's clean and expressive for "best-effort" operations.

```python
from contextlib import suppress

# Without suppress:
try:
    os.remove("temp.txt")
except FileNotFoundError:
    pass

# With suppress — cleaner:
with suppress(FileNotFoundError):
    os.remove("temp.txt")

# Multiple exception types:
with suppress(KeyError, AttributeError):
    value = data["key"]["nested"]["deep"]

# Use when:
# - Cleanup operations that might fail non-fatally
# - Cache invalidation that might already be clear
# - Optional file deletion
# DON'T use when failure should be logged or handled
```

---

### Q8: How do multiple context managers in one `with` work?

**Strong answer:**

> Multiple context managers in a single `with` are entered left-to-right and exited right-to-left (LIFO). Each is independent — an exception in one's `__exit__` doesn't prevent others from running.

```python
with open("a.txt") as a, open("b.txt", "w") as b:
    b.write(a.read())
# Exit order: b.__exit__() first, then a.__exit__()

# Parenthesized form (Python 3.10+) for readability:
with (
    get_db_connection() as conn,
    acquire_lock(resource_lock) as _,
    timer("operation") as _,
):
    perform_operation(conn)
# Exits in reverse: timer → lock → conn
```

> **If one `__exit__` raises:** Python still calls the remaining `__exit__` methods before propagating the exception.

---

## 🔴 Level 3 — Senior Questions

---

### Q9: What is `ExitStack` and when do you need it?

**Weak answer:** "It lets you use multiple context managers."

**Strong answer:**

> `ExitStack` manages a **dynamic** number of context managers determined at runtime. It's essential when you can't write a fixed number of `with` statements at code-writing time.

```python
from contextlib import ExitStack

# Open N files dynamically:
def merge_csv_files(input_paths, output_path):
    with ExitStack() as stack:
        # Number of files not known at write time:
        readers = [stack.enter_context(open(p)) for p in input_paths]
        writer  = stack.enter_context(open(output_path, "w"))
        for reader in readers:
            writer.write(reader.read())
    # All files closed here, even if an exception occurred

# Register arbitrary cleanup callbacks:
def process(data):
    with ExitStack() as stack:
        conn = db.connect()
        stack.callback(conn.close)            # always close
        stack.callback(metrics.record, "op")  # always record

        if data.needs_lock:
            stack.enter_context(acquire_lock(data.id))

        return transform(data)

# Transfer ownership out of the stack:
def open_resources(paths):
    stack = ExitStack()
    files = [stack.enter_context(open(p)) for p in paths]
    return files, stack   # caller is responsible for stack.close()
```

---

### Q10: How do you implement an async context manager?

**Strong answer:**

> Implement `__aenter__` and `__aexit__` (both `async def`), or use `@asynccontextmanager` with an async generator:

```python
from contextlib import asynccontextmanager
import asyncpg

# Class-based:
class AsyncTransaction:
    def __init__(self, dsn):
        self.dsn  = dsn
        self.conn = None

    async def __aenter__(self):
        self.conn = await asyncpg.connect(self.dsn)
        await self.conn.execute("BEGIN")
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.conn.execute("ROLLBACK")
        else:
            await self.conn.execute("COMMIT")
        await self.conn.close()
        return False

# Generator-based (simpler):
@asynccontextmanager
async def async_transaction(dsn):
    conn = await asyncpg.connect(dsn)
    await conn.execute("BEGIN")
    try:
        yield conn
        await conn.execute("COMMIT")
    except Exception:
        await conn.execute("ROLLBACK")
        raise
    finally:
        await conn.close()

# Usage:
async def main():
    async with async_transaction("postgres://...") as conn:
        await conn.execute("INSERT INTO orders ...")
```

---

### Q11: Design a context manager for a distributed lock.

**Strong answer:**

```python
import uuid, time, logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DistributedLock:
    """
    Acquire a lock in Redis. Guaranteed release on exit.
    Uses SET NX EX (atomic acquire with TTL).
    """
    def __init__(self, redis_client, key: str, ttl: int = 30):
        self.redis  = redis_client
        self.key    = f"lock:{key}"
        self.ttl    = ttl
        self.token  = str(uuid.uuid4())   # unique token prevents release by others

    def __enter__(self):
        acquired = self.redis.set(
            self.key, self.token,
            nx=True,     # only set if NOT exists
            ex=self.ttl  # expire after ttl seconds
        )
        if not acquired:
            raise RuntimeError(f"Could not acquire lock: {self.key}")
        logger.debug("Acquired lock: %s", self.key)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Lua script ensures atomic check-and-delete (only release OUR lock):
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        self.redis.eval(script, 1, self.key, self.token)
        logger.debug("Released lock: %s", self.key)
        return False

# Usage:
with DistributedLock(redis, "order-4892", ttl=60):
    process_order(4892)
```

---

## ⚠️ Trap Questions

---

### Trap 1 — Returning `True` from `__exit__` accidentally

```python
class BadManager:
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return True   # ← SWALLOWS ALL EXCEPTIONS silently!

# Any bug in the with-block is hidden:
with BadManager():
    raise ValueError("critical bug")   # silently disappeared!

# Fix: only suppress exceptions you intend to suppress:
def __exit__(self, exc_type, exc_val, exc_tb):
    self.cleanup()
    # Only suppress expected non-critical errors:
    if exc_type is not None and issubclass(exc_type, ExpectedTransientError):
        logger.warning("Suppressed transient error: %s", exc_val)
        return True
    return False  # everything else propagates
```

---

### Trap 2 — `__exit__` NOT called if `__enter__` raises

```python
class Resource:
    def __enter__(self):
        self.conn = db.connect()   # step 1
        self.lock = lock.acquire() # step 2 ← if THIS raises, __exit__ NOT called
        return self

    def __exit__(self, *args):
        self.conn.close()   # ← never runs if __enter__ raised at step 2!
        self.lock.release()

# Fix: protect setup inside __enter__:
def __enter__(self):
    self.conn = db.connect()
    try:
        self.lock = lock.acquire()
    except Exception:
        self.conn.close()   # clean up what we already acquired
        raise
    return self
```

---

### Trap 3 — Missing `try/finally` in `@contextmanager`

```python
@contextmanager
def connects(dsn):
    conn = db.connect(dsn)
    yield conn
    conn.close()   # ← NOT called if with-block raises!

# Fix:
@contextmanager
def connects(dsn):
    conn = db.connect(dsn)
    try:
        yield conn
    finally:
        conn.close()   # guaranteed
```

---

### Trap 4 — Reusing an exhausted `@contextmanager`

```python
@contextmanager
def my_cm():
    yield 42

cm = my_cm()   # create generator-based context manager

with cm as val:
    print(val)   # 42

with cm as val:  # ← reusing same generator object!
    print(val)   # RuntimeError: generator already exhausted

# Fix: always call the function (create fresh generator) each time:
with my_cm() as val:   # ← fresh generator each time
    print(val)
```

---

## 🔥 Rapid-Fire Revision

```
Q: What does __enter__ return?
A: The value assigned to the 'as' variable. Can be self, a new object, or None.

Q: When is __exit__ NOT called?
A: If __enter__ itself raises. Always called if __enter__ succeeds.

Q: What does returning True from __exit__ do?
A: Suppresses the exception — it does not propagate.

Q: @contextmanager — where is setup code? cleanup code?
A: Setup: before yield. Cleanup: after yield (in finally block).

Q: What does ExitStack do?
A: Manages a dynamic number of context managers decided at runtime.
   Registers them with enter_context(); exits all in LIFO order.

Q: contextlib.suppress() equivalent in try/except?
A: try: ... except ExceptionType: pass

Q: Async context manager protocol?
A: __aenter__ (async) and __aexit__ (async). Use 'async with'.

Q: What does contextlib.nullcontext() do?
A: No-op context manager. Used when a context manager is optional.

Q: Multiple context managers in one with — exit order?
A: LIFO (last entered, first exited).

Q: What is contextlib.closing() for?
A: Wraps any object with .close() as a context manager.
   with closing(urlopen(url)) as response: ...
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🛠️ contextlib Guide | [contextlib_guide.md](./contextlib_guide.md) |
| ➡️ Next | [13 — Concurrency](../13_concurrency/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Contextlib Guide](./contextlib_guide.md) &nbsp;|&nbsp; **Next:** [Concurrency — Theory →](../13_concurrency/theory.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Contextlib Guide](./contextlib_guide.md)
