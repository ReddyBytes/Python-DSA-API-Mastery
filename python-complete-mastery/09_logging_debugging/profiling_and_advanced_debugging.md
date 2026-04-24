# 🔬 Profiling & Advanced Debugging
## cProfile · tracemalloc · inspect · loguru · Async Debugging · Remote Debugging

> *"Every expert debugger has the same superpower: they measure first.*
> *Guessing where the bottleneck is — and being wrong — is the most expensive hobby in software."*

---

## 🎬 The Story

Two engineers get the same bug report: "The API is slow."

Engineer A opens the code, spots a loop that "looks inefficient," rewrites it.
Speed: unchanged. Three hours lost.

Engineer B runs `cProfile`. In 10 seconds she sees that 94% of CPU time is spent in
a single database helper — one nobody suspected. She fixes that function.
Speed: 8x improvement. Problem solved in 45 minutes.

The difference is not skill. It's discipline. **Measure. Then optimize.**

This file covers the tools that let you see what your code is actually doing at runtime —
how it performs, how much memory it consumes, what its call stack looks like,
and how to debug it even when it's running inside a container on a remote server.

---

## 📌 Learning Priority

**Must Learn** — used constantly in production debugging:
`cProfile` · `tracemalloc` · `loguru`

**Should Learn** — important for intermediate/senior work:
`line_profiler` · `inspect.stack()` · `inspect.signature()` · `asyncio` debug mode

**Good to Know** — situational but valuable:
`objgraph` · `memory_profiler` · `debugpy` · loguru `InterceptHandler`

**Reference** — know it exists, look up when needed:
`snakeviz` · `mprof` · `inspect.getsource()`

---

## 🩺 Section 1 — Performance Profiling: cProfile, pstats, line_profiler

Think of a doctor ordering a full blood panel before prescribing anything.
She doesn't guess which organ is struggling — she runs tests, reads the numbers,
and then targets the problem precisely. `cProfile` is your blood panel for CPU time.

### Running cProfile

There are three ways to profile. Each fits a different situation.

**Method 1: Command line (fastest for scripts)**

```bash
python -m cProfile -s cumtime my_script.py
# ↑ -s cumtime sorts output by cumulative time (slowest total callers at top)
```

**Method 2: `cProfile.run()` (embed in code)**

```python
import cProfile
import pstats

cProfile.run('my_function()', 'output.prof')  # ← saves raw stats to file

# Load and display results
stats = pstats.Stats('output.prof')
stats.strip_dirs()           # ← removes full file paths, keeps just filenames
stats.sort_stats('cumtime')  # ← sort by cumulative time
stats.print_stats(20)        # ← print top 20 rows only
```

**Method 3: `cProfile.Profile()` as context manager (most surgical)**

```python
import cProfile
import pstats
import io

def process_orders(orders):
    results = []
    for order in orders:
        results.append(validate_and_price(order))
    return results

# Profile only the section you care about
profiler = cProfile.Profile()
profiler.enable()

results = process_orders(large_order_list)  # ← only this block is profiled

profiler.disable()

# Print stats to stdout
stream = io.StringIO()
stats = pstats.Stats(profiler, stream=stream)
stats.strip_dirs()
stats.sort_stats('cumtime')
stats.print_stats(20)
print(stream.getvalue())
```

### Reading pstats Output

A typical `cProfile` output looks like this:

```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     5000    0.082    0.000    4.213    0.001 pricing.py:42(calculate_price)
     5000    0.031    0.000    3.891    0.001 db.py:17(fetch_discount)
        1    0.001    0.001    4.215    4.215 main.py:8(process_orders)
```

| Column | Meaning |
|--------|---------|
| **ncalls** | How many times this function was called |
| **tottime** | Time spent *inside* this function only (not counting sub-calls) |
| **percall** (1st) | tottime / ncalls — average cost per call |
| **cumtime** | Total time including all functions called from here |
| **percall** (2nd) | cumtime / ncalls — average cost including sub-calls |

Rule of thumb: high `cumtime` means the function is an expensive entry point.
High `tottime` means the work is happening *in* that function itself.

### pstats Programmatic Interface

```python
import pstats

stats = pstats.Stats('output.prof')

stats.strip_dirs()                   # clean up file paths
stats.sort_stats('tottime')          # sort by time spent inside (not sub-calls)
stats.print_stats(20)                # show top 20 entries
stats.print_callers('fetch_discount') # ← who is calling fetch_discount?
stats.print_callees('process_orders') # ← what does process_orders call?
```

### snakeviz — Visual Flamegraph

Sometimes a table isn't enough. `snakeviz` turns your `.prof` file into an
interactive sunburst diagram in the browser — each ring is a call level,
width = time.

```bash
pip install snakeviz

python -m cProfile -o output.prof my_script.py  # ← generate profile file
snakeviz output.prof                             # ← opens browser automatically
```

### line_profiler — Line-by-Line Timing

Once `cProfile` tells you *which function* is slow, `line_profiler` tells you
*which line* inside it. It's the zoom lens after the wide-angle shot.

```bash
pip install line_profiler
```

Decorate the function you want to profile:

```python
# my_script.py

@profile  # ← this decorator is injected by kernprof at runtime, not imported
def calculate_price(order):
    base = order['quantity'] * order['unit_price']   # line A
    tax = fetch_tax_rate(order['region'])             # line B — suspect
    discount = fetch_discount(order['user_id'])       # line C — suspect
    return base * (1 - discount) * (1 + tax)
```

Run with `kernprof`:

```bash
kernprof -l -v my_script.py
# ↑ -l writes line-level stats, -v prints them immediately
```

Output:

```
Line #   Hits    Time  Per Hit   % Time  Line Contents
==============================================================
     4   5000    82.0     0.0      1.9   base = order['quantity'] * order['unit_price']
     5   5000  3401.0     0.7     80.1   tax = fetch_tax_rate(order['region'])
     6   5000   762.0     0.2     18.0   discount = fetch_discount(order['user_id'])
```

Line 5 is consuming 80% of runtime. That's your target.

### Profiling Workflow

```
  Your code is slow
        │
        ▼
  python -m cProfile -s cumtime script.py
        │
        ▼
  Find the hot function (high cumtime)
        │
        ▼
  Add @profile to that function
  kernprof -l -v script.py
        │
        ▼
  Find the hot line
        │
        ▼
  Fix. Measure again to confirm improvement.
```

### Common Profiling Pitfalls

- **I/O-bound vs CPU-bound**: `cProfile` measures CPU time. If your function is slow because it waits on network/disk, `cProfile` will show near-zero time there. Use `asyncio` debug mode or request tracing for I/O bottlenecks.
- **Dev vs prod data**: always profile with production-scale data. A function that's fast on 100 rows may be O(n²) on 100,000.
- **Profiling overhead**: `cProfile` adds ~10-20% overhead. Use the context manager approach to profile only critical paths when overhead matters.
- **Micro-benchmark traps**: use `timeit` for isolated micro-benchmarks, not `cProfile`. Profile the real program with real data.

---

## 🚢 Section 2 — Memory Debugging: tracemalloc + memory_profiler

Picture a slow leak in a ship's hull. A single drop per second is invisible for hours.
By the time the crew notices water, it's already ankle-deep. Memory leaks in Python work
exactly like this — small allocations that are never freed, accumulating silently
until your pod gets OOM-killed at 3 AM.

### tracemalloc — Built-in Memory Tracing

`tracemalloc` is part of the Python standard library. No install needed.

**Basic usage: snapshot and inspect**

```python
import tracemalloc

tracemalloc.start()  # ← begin recording allocations

# --- your code runs here ---
process_large_dataset()

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')  # ← group by source line

print("Top 10 memory consumers:")
for stat in top_stats[:10]:
    print(stat)
```

Example output:

```
my_module.py:42: size=14.2 MiB, count=180423, average=82 B
my_module.py:87: size=3.1 MiB, count=12045, average=271 B
lib/cache.py:19: size=1.8 MiB, count=4200, average=450 B
```

**Comparing two snapshots to find the leak**

This is the most powerful tracemalloc pattern — take a snapshot before and after
a suspected leak window, then diff them:

```python
import tracemalloc

tracemalloc.start()

snapshot1 = tracemalloc.take_snapshot()  # ← before

for _ in range(1000):
    process_request()  # ← suspected leak here

snapshot2 = tracemalloc.take_snapshot()  # ← after

# Diff: what grew between snapshot1 and snapshot2?
top_stats = snapshot2.compare_to(snapshot1, 'lineno')

print("Memory growth (top 10):")
for stat in top_stats[:10]:
    print(stat)
```

Output:

```
+12.4 MiB: my_module.py:55 (count: +85000)
 +1.2 MiB: lib/parser.py:112 (count: +8200)
```

Lines with a `+` prefix are allocating more than they're freeing. That's your leak.

### memory_profiler — Line-by-Line Memory Usage

`memory_profiler` gives you the same line-by-line view as `line_profiler`, but for
memory instead of CPU time.

```bash
pip install memory_profiler
```

```python
# memory_example.py
from memory_profiler import profile

@profile  # ← decorator marks function for line-by-line memory tracking
def load_and_process(filepath):
    with open(filepath) as f:
        data = f.read()              # line A
    records = data.split('\n')       # line B
    parsed = [parse(r) for r in records]  # line C — watch this
    return parsed
```

Run with:

```bash
python -m memory_profiler memory_example.py
# or for time-series tracking:
mprof run memory_example.py    # ← records memory over time
mprof plot                     # ← plots the time series chart
```

Line-by-line output:

```
Line #    Mem usage    Increment   Line Contents
================================================
     6    45.2 MiB     45.2 MiB   def load_and_process(filepath):
     7    45.2 MiB      0.0 MiB       with open(filepath) as f:
     8   107.4 MiB     62.2 MiB           data = f.read()
     9   142.1 MiB     34.7 MiB       records = data.split('\n')
    10   289.3 MiB    147.2 MiB       parsed = [parse(r) for r in records]
```

Line 10 is the memory hog — allocating 147 MB for the parsed list.
Consider streaming / generator pattern instead.

### objgraph — Finding Reference Cycles

```bash
pip install objgraph
```

```python
import objgraph

# Show what object types grew the most since last call
objgraph.show_growth(limit=10)
# Output:
# MyCache        +1200
# dict           +840
# list           +210

# Visualize who is holding a reference to a specific object
# (requires graphviz: brew install graphviz)
import gc
gc.collect()
leaked = objgraph.by_type('MyCache')[0]       # ← grab one instance
objgraph.show_backrefs(leaked, max_depth=3)   # ← saves PNG of reference graph
```

### Common Memory Leak Patterns in Python

| Pattern | Why it leaks | Fix |
|--------|-------------|-----|
| **Circular references** | Object A holds ref to B, B holds ref to A — neither is collected unless `gc.collect()` runs | Use `weakref.ref()` for back-references |
| **Global caches** | `cache = {}` at module level grows forever | Use `functools.lru_cache(maxsize=N)` or set a TTL |
| **Unclosed files/connections** | File objects in scope stay open, holding memory | Use `with` statement always |
| **Large lists in closures** | A closure captures the entire list even if only one item is needed | Capture only the specific value, not the container |
| **Event listeners** | Callbacks registered but never deregistered | Always pair `register` with `unregister` in cleanup |

---

## 🔎 Section 3 — The `inspect` Module: Runtime Introspection

Imagine having X-ray vision for your own code — the ability to look inside any
function, any object, any call frame while the program is running.
That's the `inspect` module. It lets you see the structure of your own program
from inside the program itself.

### inspect.signature — Read Parameters and Annotations

```python
import inspect

def create_order(user_id: int, quantity: int = 1, promo_code: str = None):
    pass

sig = inspect.signature(create_order)
print(sig)  # → (user_id: int, quantity: int = 1, promo_code: str = None)

for name, param in sig.parameters.items():
    print(f"{name}: default={param.default}, annotation={param.annotation}")
# user_id:    default=<class 'inspect._empty'>, annotation=<class 'int'>
# quantity:   default=1, annotation=<class 'int'>
# promo_code: default=None, annotation=<class 'str'>
```

### inspect.stack — The Live Call Stack

```python
import inspect

def get_caller_info():
    """Return the name of the function that called this one."""
    stack = inspect.stack()
    # stack[0] = get_caller_info itself
    # stack[1] = direct caller
    # stack[2] = caller's caller
    caller_frame = stack[1]
    return {
        'function': caller_frame.function,   # ← function name
        'filename': caller_frame.filename,   # ← source file
        'lineno':   caller_frame.lineno,     # ← line number
    }

def process_payment():
    info = get_caller_info()
    print(f"process_payment was called from {info['function']} at line {info['lineno']}")
```

### inspect.getsource — Read Source Code at Runtime

```python
import inspect

def my_transform(x):
    return x ** 2 + 3 * x - 1

source = inspect.getsource(my_transform)
print(source)
# def my_transform(x):
#     return x ** 2 + 3 * x - 1
```

Useful in frameworks that need to serialize or document functions dynamically.

### inspect.getmembers — Explore Any Object

```python
import inspect

class PaymentProcessor:
    tax_rate = 0.08

    def charge(self, amount): ...
    def refund(self, amount): ...

members = inspect.getmembers(PaymentProcessor)
# Returns list of (name, value) tuples for every attribute and method

# Filter to just methods:
methods = inspect.getmembers(PaymentProcessor, predicate=inspect.isfunction)
# [('charge', <function ...>), ('refund', <function ...>)]
```

### Type-Check Predicates

```python
import inspect

inspect.isfunction(my_transform)  # → True  (pure def function)
inspect.isclass(PaymentProcessor) # → True
inspect.ismethod(obj.charge)      # → True  (bound to instance)
inspect.isbuiltin(len)            # → True  (C-level built-in)
inspect.iscoroutinefunction(fetch) # → True (async def function)
```

### Real-World Pattern 1: Auto-Logging Decorator

This decorator automatically logs every call to a function, including
all argument names and values — without you having to write `logger.info(...)` in every function:

```python
import inspect
import functools
import logging

log = logging.getLogger(__name__)

def auto_log(fn):
    sig = inspect.signature(fn)  # ← read once at decoration time, not every call

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        # Bind the actual call args to the signature parameter names
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        log.info(f"CALL {fn.__name__}({dict(bound.arguments)})")
        result = fn(*args, **kwargs)
        log.info(f"RETURN {fn.__name__} → {result!r}")
        return result

    return wrapper

@auto_log
def calculate_tax(amount: float, region: str = "US") -> float:
    return amount * 0.08

calculate_tax(100.0, region="CA")
# INFO CALL calculate_tax({'amount': 100.0, 'region': 'CA'})
# INFO RETURN calculate_tax → 8.0
```

### Real-World Pattern 2: Framework-Style Dependency Injection

This pattern — used by FastAPI, pytest, and others — inspects a function's
parameter names to automatically resolve and inject dependencies:

```python
import inspect

# Registry of available services
_services = {
    'db': lambda: DatabaseConnection(),
    'cache': lambda: RedisCache(),
    'mailer': lambda: EmailService(),
}

def inject(fn):
    """Automatically inject dependencies based on parameter names."""
    sig = inspect.signature(fn)

    def wrapper():
        kwargs = {}
        for name, param in sig.parameters.items():
            if name in _services:
                kwargs[name] = _services[name]()  # ← resolve service by name
        return fn(**kwargs)

    return wrapper

@inject
def send_welcome_email(db, mailer):  # ← parameter names match service registry
    user = db.get_latest_user()
    mailer.send(user.email, "Welcome!")

send_welcome_email()  # ← called with no arguments; injection handles it
```

---

## 🚗 Section 4 — loguru: Modern Logging

The standard library `logging` module is like a manual car:
powerful, totally under your control, but you have to manage every gear change yourself —
creating loggers, adding handlers, configuring formatters, wiring everything up.

`loguru` is an automatic — you step in, it works. Same road, same destination,
dramatically less friction.

### Zero-Config Default

```bash
pip install loguru
```

```python
from loguru import logger  # ← that's the entire setup

logger.debug("Processing started")
logger.info("Order received: {}", order_id)    # ← {} templating, no % or f-string needed
logger.warning("Retry attempt {}/3", attempt)
logger.error("Payment failed for user {}", user_id)
logger.critical("Database unreachable")
```

Out of the box, without any configuration, you get:
- Colored, human-readable output to stderr
- Timestamps with milliseconds
- File and line number in every message
- Exception tracebacks with local variable values

### logger.add() — Sinks, Rotation, Retention

A **sink** is anywhere a log message can go: a file, stdout, a URL, a function.
`logger.add()` registers a new sink.

```python
from loguru import logger

# Add a rotating file sink
logger.add(
    "logs/app_{time}.log",   # ← {time} creates timestamped filenames
    rotation="100 MB",       # ← new file when current hits 100 MB
    retention="30 days",     # ← delete files older than 30 days
    compression="zip",       # ← compress rotated files
    level="INFO",            # ← only INFO and above go to this file
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} | {message}",
)

# Add a separate sink for errors only
logger.add(
    "logs/errors.log",
    level="ERROR",
    rotation="10 MB",
)
```

### Log Levels in loguru

loguru has the standard 5 levels plus two extras:

| Level | Value | When to use |
|-------|-------|-------------|
| **TRACE** | 5 | Extremely verbose, internal machinery |
| **DEBUG** | 10 | Developer-facing detail |
| **INFO** | 20 | Normal operations, key events |
| **SUCCESS** | 25 | Explicit success (new in loguru) |
| **WARNING** | 30 | Unexpected but recoverable |
| **ERROR** | 40 | Failure, but app continues |
| **CRITICAL** | 50 | Severe, likely fatal |

```python
logger.success("Order {} processed successfully", order_id)  # ← green SUCCESS level
logger.trace("Entering loop iteration {}", i)                # ← very noisy, use sparingly
```

### logger.bind() — Structured Context

`logger.bind()` creates a child logger with extra context fields attached
to every message it emits — without repeating yourself:

```python
from loguru import logger

def handle_request(request_id, user_id):
    # Create a request-scoped logger with context baked in
    req_log = logger.bind(request_id=request_id, user_id=user_id)

    req_log.info("Request received")          # includes request_id and user_id
    req_log.info("Validating payload")        # same context, automatically
    req_log.error("Validation failed")        # still tagged with request context
```

### Exception Capturing

```python
from loguru import logger

# Method 1: logger.exception() inside an except block
try:
    result = risky_operation()
except Exception:
    logger.exception("Operation failed")  # ← logs full traceback + local vars

# Method 2: logger.catch() as context manager
with logger.catch():
    result = risky_operation()  # ← any exception is caught, logged, re-raised

# Method 3: @logger.catch decorator — wraps entire function
@logger.catch
def process_batch(orders):
    for order in orders:
        validate(order)   # ← if this raises, full traceback is logged automatically
```

The `@logger.catch` decorator is particularly valuable for worker functions,
background tasks, and anything running in a thread — uncaught exceptions that would
silently kill a thread are now captured and logged with full context.

### Serializing to JSON

For log aggregation systems (Datadog, Splunk, ELK), you want JSON output:

```python
from loguru import logger

logger.add("logs/structured.log", serialize=True)  # ← every message is a JSON line

logger.bind(order_id="ORD-123", amount=49.99).info("Payment processed")
# Output (formatted for readability):
# {
#   "text": "Payment processed",
#   "record": {
#     "level": {"name": "INFO", "no": 20},
#     "time": {"repr": "2026-04-24 09:15:22.341"},
#     "extra": {"order_id": "ORD-123", "amount": 49.99},
#     "file": {"name": "payments.py", "path": "/app/payments.py"},
#     "line": 42
#   }
# }
```

### Interop with stdlib: InterceptHandler

If you have a codebase that uses stdlib `logging` (including third-party libraries),
you can route all of it into loguru with a single handler:

```python
import logging
from loguru import logger

class InterceptHandler(logging.Handler):
    """Route all stdlib logging calls into loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        # Find the loguru level that matches the stdlib level name
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find the caller frame so loguru reports the correct file/line
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

# Install: replace the root logger's handlers with InterceptHandler
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# Now ALL stdlib logging (including sqlalchemy, requests, etc.) flows through loguru
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
```

### loguru vs stdlib Decision Table

| Situation | Reach for |
|-----------|-----------|
| New greenfield project | **loguru** — less boilerplate, better defaults |
| Adding to existing stdlib codebase | **stdlib** + `InterceptHandler` to bridge |
| Library you're publishing (PyPI) | **stdlib** — don't impose loguru on library users |
| Background workers, async tasks | **loguru** — `@logger.catch` is invaluable |
| Need extreme config flexibility | **stdlib** — `dictConfig` is more powerful |
| Teaching someone logging from scratch | **loguru** — clearer mental model |

---

## ⚡ Section 5 — Async Debugging

Debugging synchronous code is like watching one person work at a desk.
When something goes wrong, you watch what they did, step by step.

Debugging async code is like watching 50 people in an open office,
all sharing one phone line, passing it back and forth.
When something breaks, you need different tools — you need to see
which task had the phone, what it was doing, and what it was waiting for.

### asyncio Debug Mode

Python's `asyncio` has a built-in debug mode that surfaces common async bugs automatically.

**Enable at runtime:**

```python
import asyncio

async def main():
    await process_queue()

asyncio.run(main(), debug=True)  # ← enable debug mode
```

**Enable via environment variable (no code change):**

```bash
PYTHONASYNCIODEBUG=1 python my_service.py
```

**What debug mode enables:**

- **Slow callback warning**: logs a warning if any callback blocks the event loop for more than 100ms (the event loop should never be blocked)
- **Unawaited coroutine detection**: raises `RuntimeWarning` when you call `async_fn()` without `await`
- **ResourceWarning**: warns when asyncio objects (transports, streams) are not properly closed
- **Detailed task names** in tracebacks

```python
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)  # ← asyncio debug messages go to logging

async def slow_callback():
    import time
    time.sleep(0.5)   # ← WRONG: blocking call inside async code
    # In debug mode: "Executing <Task> took 0.500 seconds" warning fires

asyncio.run(slow_callback(), debug=True)
```

### breakpoint() Inside async def

`breakpoint()` works inside `async def` functions as of Python 3.8+ with no special setup:

```python
async def process_item(item):
    result = await fetch_data(item)
    breakpoint()   # ← execution pauses, pdb opens; all async context is available
    await save_result(result)
```

From the pdb prompt you can inspect `result`, call `await` expressions,
and step through normally.

### Inspecting Running Tasks

```python
import asyncio

async def monitor():
    # List all currently running tasks
    all_tasks = asyncio.all_tasks()
    for task in all_tasks:
        print(f"Task: {task.get_name()}, done={task.done()}, cancelled={task.cancelled()}")

    # Get just the current task
    current = asyncio.current_task()
    print(f"I am: {current.get_name()}")
```

### Naming Tasks for Correlation

When a crash happens, anonymous task names like `Task-47` are useless.
Name your tasks at creation time so logs tell you exactly which work unit failed:

```python
import asyncio
from loguru import logger

async def worker(order_id: str):
    logger.info("Starting work on order {}", order_id)
    await process_order(order_id)

async def main(orders):
    tasks = [
        asyncio.create_task(
            worker(order_id),
            name=f"worker-order-{order_id}"   # ← meaningful name
        )
        for order_id in orders
    ]
    await asyncio.gather(*tasks)
```

When an exception occurs, the traceback now says `Task worker-order-ORD-8821`
instead of `Task-47`.

### Common Async Bugs

```python
# Bug 1: Forgotten await — coroutine is created but never run
async def send_notification(user_id):
    await email_service.send(user_id)  # correct

async def handle_signup(user_id):
    send_notification(user_id)   # ← BUG: missing await; silently does nothing
    # asyncio debug mode raises RuntimeWarning here

# Bug 2: Blocking call in event loop — stalls ALL other tasks
async def fetch_data(url):
    import requests
    return requests.get(url).text  # ← BUG: blocking HTTP; blocks the whole loop
    # Fix: use aiohttp or httpx instead

# Bug 3: Fire-and-forget task leak — exception is swallowed silently
async def main():
    asyncio.create_task(risky_work())  # ← BUG: if risky_work() raises, exception is lost
    # Fix: keep a reference and add a done callback, or use asyncio.gather()
    task = asyncio.create_task(risky_work())
    task.add_done_callback(lambda t: t.exception())  # ← surface the exception
```

### Enabling Verbose HTTP Logging (aiohttp / httpx)

```python
import logging
import aiohttp

# Enable aiohttp debug logs (shows request/response headers and bodies)
logging.getLogger("aiohttp.client").setLevel(logging.DEBUG)
logging.getLogger("aiohttp.connector").setLevel(logging.DEBUG)

# For httpx:
import httpx
logging.getLogger("httpx").setLevel(logging.DEBUG)
logging.getLogger("httpcore").setLevel(logging.DEBUG)

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:  # ← request/response now logged
            return await response.text()
```

---

## 🔧 Section 6 — Remote Debugging with debugpy

Imagine a mechanic who can diagnose your car while it's still on the highway, running at speed.
They plug in remotely, see exactly what's happening inside the engine without stopping it,
fix the issue, and disconnect — the car never pulls over.

That's remote debugging. You attach your IDE to a running process inside a container
or on a remote server, set breakpoints, and step through live code.

### What Remote Debugging Solves

Some bugs only reproduce in specific environments:
- Inside a Docker container with a specific data volume
- Inside a Kubernetes pod where the bug requires real infrastructure
- On a remote server where you can't easily install an IDE

Remote debugging lets you use VS Code's full debugger against those environments.

### Basic debugpy Setup

```bash
pip install debugpy
```

Add this block at the **entry point** of your application:

```python
import debugpy

# Start listening for a debugger to attach on port 5678
debugpy.listen(("0.0.0.0", 5678))  # ← 0.0.0.0 accepts connections from any host

print("Waiting for debugger to attach...")
debugpy.wait_for_client()          # ← process PAUSES here until VS Code connects
print("Debugger attached. Resuming.")

# Now your normal application code runs, with VS Code able to set breakpoints
main()
```

### VS Code launch.json — Attach Configuration

Create or add to `.vscode/launch.json` in your project:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Attach to Remote debugpy",
            "type": "debugpy",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "/app"
                }
            ]
        }
    ]
}
```

`pathMappings` tells VS Code how to map your local source files to the paths
on the remote machine (or inside the container).

### Docker: Exposing the Debug Port

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt debugpy
COPY . .
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "main.py"]
```

```bash
# docker-compose.yml (relevant section)
services:
  api:
    build: .
    ports:
      - "8000:8000"   # ← application port
      - "5678:5678"   # ← debugpy port — expose it
    environment:
      - PYTHONDONTWRITEBYTECODE=1
```

Start the container, then in VS Code: Run → Start Debugging → "Attach to Remote debugpy".

### Kubernetes: kubectl port-forward

When the process is running inside a K8s pod:

```bash
# Step 1: Forward the debugpy port from the pod to your local machine
kubectl port-forward pod/my-api-pod-abc123 5678:5678

# Step 2: In VS Code, run the "Attach to Remote debugpy" configuration
# VS Code connects through the port-forward tunnel to the running pod
```

### Security Warning

`debugpy.wait_for_client()` blocks the process — your application will not start
until a debugger connects. This is intentional in development, but catastrophic in production.

Never leave `debugpy.listen()` or `debugpy.wait_for_client()` in production code.
Gate it behind an environment variable:

```python
import os
import debugpy

if os.getenv("ENABLE_DEBUGPY") == "1":
    debugpy.listen(("0.0.0.0", 5678))
    print("Waiting for debugger...")
    debugpy.wait_for_client()

main()
```

```bash
# Development only — never set this in production:
ENABLE_DEBUGPY=1 python app.py
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← pdb Guide](./pdb_guide.md) &nbsp;|&nbsp; **Next:** [Theory →](./theory.md)

**Related Topics:** [Theory](./theory.md) · [pdb Guide](./pdb_guide.md) · [Structured Logging](./structured_logging.py) · [Cheat Sheet](./cheatsheet.md)
