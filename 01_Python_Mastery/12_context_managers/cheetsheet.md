# ⚡ Context Managers — Cheatsheet

> Quick reference: protocol, class-based, @contextmanager, contextlib, async, gotchas.

---

## 🔗 The Protocol

```
with EXPR as VAR:
    BODY

Equivalent to:
  _cm = EXPR
  VAR = _cm.__enter__()        ← setup; VAR = returned value
  try:
      BODY
  except:
      if not _cm.__exit__(*sys.exc_info()):
          raise
  else:
      _cm.__exit__(None, None, None)
```

---

## 🏗️ Class-Based Context Manager

```python
class ManagedResource:
    def __enter__(self):
        self.r = acquire()
        return self.r          # ← 'as' variable receives this

    def __exit__(self, exc_type, exc_val, exc_tb):
        release(self.r)
        # exc_type: exception class or None
        # exc_val:  exception instance or None
        # exc_tb:   traceback or None
        return False           # False/None = propagate; True = suppress
```

---

## 🌿 `@contextmanager` (Generator-Based)

```python
from contextlib import contextmanager

@contextmanager
def managed(resource):
    r = acquire(resource)   # setup (before yield)
    try:
        yield r             # ← 'as' variable = r; with-block runs here
    finally:
        release(r)          # cleanup (always runs — MUST use try/finally)

# Handle exceptions:
@contextmanager
def transaction(conn):
    conn.execute("BEGIN")
    try:
        yield conn
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise               # re-raise after cleanup
```

---

## 📚 `contextlib` Quick Reference

```python
from contextlib import (
    contextmanager,        # generator → context manager
    asynccontextmanager,   # async generator → async context manager
    suppress,              # silently ignore exception types
    nullcontext,           # no-op (for optional context managers)
    ExitStack,             # dynamic stack of context managers
    AsyncExitStack,        # async version of ExitStack
    redirect_stdout,       # redirect sys.stdout
    redirect_stderr,       # redirect sys.stderr
    closing,               # call .close() on exit
)

# suppress:
with suppress(FileNotFoundError, OSError):
    os.remove("temp.txt")

# nullcontext:
ctx = lock if need_lock else nullcontext()
with ctx:
    do_work()

# closing:
with closing(urlopen("http://example.com")) as resp:
    data = resp.read()

# redirect_stdout:
import io
buf = io.StringIO()
with redirect_stdout(buf):
    print("captured")
output = buf.getvalue()
```

---

## 📚 `ExitStack` — Dynamic Context Managers

```python
from contextlib import ExitStack

# Open dynamic number of files:
with ExitStack() as stack:
    files = [stack.enter_context(open(p)) for p in paths]
    process(files)   # all files closed on exit

# Register arbitrary cleanup:
with ExitStack() as stack:
    conn = db.connect()
    stack.callback(conn.close)          # always called
    stack.callback(log.info, "done")    # always called

# Conditional context manager:
with ExitStack() as stack:
    if use_lock:
        stack.enter_context(lock)
    do_work()

# Transfer responsibility to caller:
stack = ExitStack()
files = [stack.enter_context(open(p)) for p in paths]
return files, stack   # caller calls stack.close()
```

---

## ⚡ Async Context Manager

```python
# Class-based:
class AsyncResource:
    async def __aenter__(self):
        self.r = await connect()
        return self.r

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.r.close()
        return False

async with AsyncResource() as r:
    await r.query()

# Generator-based:
from contextlib import asynccontextmanager

@asynccontextmanager
async def async_transaction(conn):
    await conn.execute("BEGIN")
    try:
        yield conn
        await conn.execute("COMMIT")
    except:
        await conn.execute("ROLLBACK")
        raise
    finally:
        await conn.close()
```

---

## 🔗 Multiple Context Managers

```python
# Single line:
with open("in.txt") as fin, open("out.txt", "w") as fout:
    fout.write(fin.read())

# Parenthesized (Python 3.10+):
with (
    open("a.txt") as a,
    open("b.txt") as b,
    timer("merge"),
):
    merge(a, b)

# Exit order: LIFO (last entered, first exited)
# with A() as a, B() as b → exits: b first, then a
```

---

## 🎯 Common Production Patterns

```python
# Timer:
@contextmanager
def timer(name):
    start = time.perf_counter()
    try: yield
    finally:
        logger.info("%s: %.3fs", name, time.perf_counter() - start)

# Temp directory:
@contextmanager
def temp_dir():
    path = Path(tempfile.mkdtemp())
    try: yield path
    finally: shutil.rmtree(path, ignore_errors=True)

# DB transaction:
@contextmanager
def transaction(conn):
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

# Suppress + log:
@contextmanager
def best_effort(label):
    try:
        yield
    except Exception as e:
        logger.warning("%s failed (suppressed): %s", label, e)
```

---

## 🔴 Gotchas

```python
# 1 — Return True accidentally suppresses ALL exceptions:
def __exit__(self, exc_type, exc_val, exc_tb):
    self.cleanup()
    return True   # ← DANGER: swallows everything silently!

# 2 — Missing try/finally in @contextmanager:
@contextmanager
def leaky():
    r = acquire()
    yield r
    release(r)    # NOT called if with-block raises!
# Fix: wrap in try/finally

# 3 — __exit__ NOT called if __enter__ raises:
def __enter__(self):
    self.a = step_one()
    self.b = step_two()  # ← if this raises, __exit__ never called!
# Fix: use try/except in __enter__ to clean up partial setup

# 4 — Reusing generator-based context manager:
cm = my_contextmanager()
with cm: ...
with cm: ...   # RuntimeError: generator already exhausted
# Fix: call the function each time: with my_contextmanager(): ...

# 5 — contextlib.suppress() hides bugs:
with suppress(Exception):   # ← too broad! hides all errors
    do_important_work()
# Use: suppress only narrow, expected exception types
```

---

## 🔥 Rapid-Fire

```
Q: __enter__ return value?
A: Assigned to 'as' variable. Can return self, a resource, or None.

Q: When is __exit__ NOT called?
A: Only if __enter__ itself raises an exception.

Q: Return True from __exit__?
A: Suppresses the exception.

Q: try/finally required in @contextmanager?
A: Yes — without it, exception in with-block skips cleanup.

Q: Exit order with multiple context managers?
A: LIFO — last entered, first exited.

Q: ExitStack use case?
A: When number of context managers is dynamic (decided at runtime).

Q: contextlib.nullcontext() use?
A: When a context manager is optional (conditional usage).
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| 🛠️ contextlib Guide | [contextlib_guide.md](./contextlib_guide.md) |
| ➡️ Next | [13 — Concurrency](../13_concurrency/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Contextlib Guide →](./contextlib_guide.md)

**Related Topics:** [Theory](./theory.md) · [Contextlib Guide](./contextlib_guide.md) · [Interview Q&A](./interview.md)
