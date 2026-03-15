# ⚡ async_guide.md — Python asyncio, Deep Dive

> Complete guide to async/await in Python: how the event loop works,
> coroutines, tasks, patterns, and real production usage.
> Theory-first, code second.

---

## 🎬 Why asyncio Exists — The C10K Problem

In 1999, Dan Kegel posed the "C10K problem": how do you handle 10,000 simultaneous network connections on a single server?

**Traditional approach — one thread per connection:**
```
10,000 connections → 10,000 threads
Each thread: ~8MB stack = 80GB RAM
Plus: OS scheduler context-switching between 10,000 threads
Result: server crawls, crashes
```

**The insight:** most of that time, threads are just **waiting**. Waiting for a client to send data. Waiting for a database to respond. Waiting for a file to load. If you could have one thread handle ALL the waiting intelligently — switch to the next task when one is blocked — you'd get massive efficiency.

This is asyncio: **one thread, many tasks, zero wasted waits.**

---

## 🧠 Chapter 1: The Mental Model — Cooperative Multitasking

asyncio is **cooperative** (not preemptive like threads). Tasks voluntarily yield control:

```
PREEMPTIVE (threading):
  The OS can interrupt your thread at any time — you have no control.
  → Need locks to protect shared state.

COOPERATIVE (asyncio):
  A task runs until IT decides to yield (at an 'await' point).
  → No interruption between awaits → no race conditions on shared state!
```

**The single-threaded event loop:**

```
EVENT LOOP DIAGRAM:

  ┌─────────────────────────────────────────────────────┐
  │                   EVENT LOOP                        │
  │                                                     │
  │  ready_queue: [Task A, Task C]                      │
  │  waiting: {Task B: "DB response", Task D: "timer"}  │
  │                                                     │
  │  1. Take Task A from ready_queue                    │
  │  2. Run Task A until it hits 'await db.query()'     │
  │  3. Register Task A in waiting set                  │
  │  4. Take Task C from ready_queue                    │
  │  5. Run Task C until it hits 'await sleep(1)'       │
  │  6. Register Task C in waiting set                  │
  │  7. Poll I/O: DB responded → move Task A to ready   │
  │  8. Run Task A (resumed from where it paused)       │
  │  ...                                                │
  └─────────────────────────────────────────────────────┘
```

**Key insight:** between any two `await` points, your code runs **atomically** — no other task can interrupt. This means no race conditions on simple state, but it also means a task that never `await`s blocks everyone.

---

## 🔑 Chapter 2: Coroutines — The Foundation

A **coroutine** is a function that can be paused and resumed. In Python, it's an `async def` function.

```python
# Regular function — runs to completion immediately:
def regular():
    result = compute()
    return result           # done, one call

# Coroutine function — returns a coroutine object when called:
async def coro():
    result = await async_compute()  # can pause here
    return result
```

**Critical distinction — calling vs running a coroutine:**

```python
async def greet(name):
    print(f"Hello, {name}!")
    return f"greeted {name}"

# CALLING the function returns a coroutine object — nothing runs:
coro = greet("Alice")
print(coro)   # <coroutine object greet at 0x...>
# "Hello, Alice!" was NOT printed!

# You must either await it or schedule it:
result = await greet("Alice")   # inside async def
# OR
result = asyncio.run(greet("Alice"))  # at top level
```

**The `await` keyword:**

```
await expr  means:
  1. Evaluate expr to get an awaitable (coroutine, Future, or Task)
  2. Start running it
  3. If it needs to wait for I/O → suspend THIS coroutine, yield to event loop
  4. When the awaited operation completes → resume THIS coroutine
  5. The result of the awaited operation becomes the value of the await expression

await does NOT block the thread — it only suspends the current coroutine.
The event loop can run other coroutines while this one waits.
```

---

## 🔄 Chapter 3: Tasks — Concurrent Scheduling

A **Task** wraps a coroutine and schedules it to run on the event loop. Multiple tasks run concurrently:

```python
import asyncio

async def fetch(url, delay):
    print(f"Starting {url}")
    await asyncio.sleep(delay)   # simulates I/O wait
    print(f"Done {url}")
    return f"result from {url}"

# Sequential (WRONG for concurrency — one at a time):
async def sequential():
    r1 = await fetch("api1.com", 2)   # 2 seconds
    r2 = await fetch("api2.com", 3)   # 3 seconds
    # Total: 5 seconds

# Concurrent with gather (CORRECT — all start simultaneously):
async def concurrent():
    r1, r2 = await asyncio.gather(
        fetch("api1.com", 2),
        fetch("api2.com", 3),
    )
    # Total: 3 seconds (longest single call)

# How it works:
# gather() creates two Tasks and schedules both.
# fetch("api1.com") starts, hits await sleep(2), suspends.
# fetch("api2.com") starts, hits await sleep(3), suspends.
# After 2s: api1 resumes, prints "Done", returns result.
# After 3s: api2 resumes, prints "Done", returns result.
# gather() returns when ALL tasks complete.
```

**create_task vs gather:**

```python
# create_task: explicitly schedule a coroutine as a background task:
async def main():
    task1 = asyncio.create_task(fetch("api1.com", 2))  # starts immediately!
    task2 = asyncio.create_task(fetch("api2.com", 3))  # starts immediately!

    # Both tasks are now running in background.
    # Do other work here if needed.

    r1 = await task1   # wait for task1's result
    r2 = await task2   # wait for task2's result

# gather: shorthand for create_task + await all:
r1, r2 = await asyncio.gather(fetch("api1.com", 2), fetch("api2.com", 3))
```

---

## 🏗️ Chapter 4: The Event Loop — How It Works Internally

```python
# Simplified event loop implementation:

class EventLoop:
    def __init__(self):
        self.ready     = deque()   # tasks ready to run
        self.scheduled = []        # tasks scheduled for future time (heap)
        self.io_tasks  = {}        # fd → task (waiting for I/O)

    def run_until_complete(self, coro):
        task = Task(coro)
        self.ready.append(task)

        while self.ready or self.scheduled or self.io_tasks:
            # 1. Run all ready tasks:
            while self.ready:
                task = self.ready.popleft()
                task.step()        # advance coroutine to next yield/await

            # 2. Poll I/O (select/epoll/kqueue):
            timeout = self._get_next_timeout()
            events  = self._poll_io(timeout)
            for fd, event in events:
                task = self.io_tasks.pop(fd)
                self.ready.append(task)  # I/O ready → move to ready queue

            # 3. Process scheduled timers:
            now = time.monotonic()
            while self.scheduled and self.scheduled[0].when <= now:
                _, task = heapq.heappop(self.scheduled)
                self.ready.append(task)
```

**What actually happens when you `await asyncio.sleep(5)`:**

```
1. asyncio.sleep(5) creates a Future
2. The Future registers a timer callback (5 seconds from now)
3. The current coroutine's frame is stored → suspended
4. Control returns to event loop
5. Event loop runs other ready coroutines
6. After 5 seconds: timer fires → Future marked "done"
7. Coroutine is added back to ready queue
8. Event loop runs coroutine again from where it paused
```

---

## 🛠️ Chapter 5: Running Coroutines — All the Ways

```python
import asyncio

async def my_coro():
    return 42

# 1. asyncio.run() — top-level entry point (Python 3.7+):
result = asyncio.run(my_coro())
# Creates NEW event loop, runs coroutine, closes loop.
# Use this in __main__ only.

# 2. await — inside another coroutine:
async def main():
    result = await my_coro()

# 3. asyncio.create_task() — schedule for concurrent execution:
async def main():
    task = asyncio.create_task(my_coro())
    # task is running concurrently NOW
    result = await task

# 4. asyncio.gather() — run multiple concurrently, wait for all:
async def main():
    r1, r2, r3 = await asyncio.gather(coro1(), coro2(), coro3())
    # If any raises: gather raises. Use return_exceptions=True to collect:
    results = await asyncio.gather(coro1(), coro2(), return_exceptions=True)
    for r in results:
        if isinstance(r, Exception): handle_error(r)
        else: process(r)

# 5. asyncio.wait() — more control:
async def main():
    tasks = [asyncio.create_task(coro()) for _ in range(5)]
    done, pending = await asyncio.wait(
        tasks,
        timeout=5.0,
        return_when=asyncio.ALL_COMPLETED   # or FIRST_COMPLETED, FIRST_EXCEPTION
    )
    for task in pending:
        task.cancel()   # cancel those that didn't finish in time

# 6. asyncio.wait_for() — single coroutine with timeout:
try:
    result = await asyncio.wait_for(my_coro(), timeout=3.0)
except asyncio.TimeoutError:
    print("Timed out")
```

---

## ⚡ Chapter 6: asyncio Synchronization Primitives

asyncio provides its own sync primitives that work with the event loop (non-blocking — they yield to the event loop while waiting, unlike threading primitives which block the thread):

### Lock

```python
import asyncio

lock = asyncio.Lock()

async def critical_section():
    async with lock:          # acquires lock without blocking event loop
        await do_work()       # other coroutines can run while we await inside!
    # lock released here

# Lock is NOT re-entrant:
async def deadlock():
    async with lock:
        async with lock:      # DEADLOCK — same coroutine can't re-acquire

# Use asyncio.Lock when:
# - Multiple coroutines share state
# - You need mutual exclusion without blocking the event loop
```

### Semaphore — Limit Concurrency

```python
# Limit to N concurrent HTTP requests:
semaphore = asyncio.Semaphore(10)   # max 10 concurrent

async def rate_limited_fetch(session, url):
    async with semaphore:           # waits if 10 requests already active
        async with session.get(url) as response:
            return await response.json()

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [rate_limited_fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

### Event — Signal Between Coroutines

```python
ready = asyncio.Event()

async def producer():
    await asyncio.sleep(2)   # simulate setup
    data = load_data()
    ready.set()               # signal all waiting coroutines

async def consumer(name):
    print(f"{name} waiting...")
    await ready.wait()        # yields to event loop until set()
    print(f"{name} processing")

async def main():
    await asyncio.gather(
        producer(),
        consumer("C1"),
        consumer("C2"),
    )
```

### Queue — Async Producer/Consumer

```python
async def producer(queue):
    for item in data_source():
        await queue.put(item)   # waits if queue full (non-blocking to event loop)
    await queue.put(None)       # sentinel

async def consumer(queue):
    while True:
        item = await queue.get()   # waits if empty
        if item is None:
            break
        await process(item)
        queue.task_done()

async def main():
    q = asyncio.Queue(maxsize=100)
    await asyncio.gather(
        producer(q),
        consumer(q),
        consumer(q),   # two consumers
    )
```

---

## 🌐 Chapter 7: Real HTTP Client — aiohttp

```python
import asyncio, aiohttp

async def fetch_one(session, url):
    """Fetch a single URL and return the JSON body."""
    try:
        async with session.get(
            url,
            timeout=aiohttp.ClientTimeout(total=10, connect=3)
        ) as response:
            response.raise_for_status()   # raise for 4xx/5xx
            return await response.json()
    except aiohttp.ClientError as e:
        return {"error": str(e), "url": url}

async def fetch_many(urls, max_concurrent=20):
    """Fetch many URLs concurrently with concurrency limit."""
    sem = asyncio.Semaphore(max_concurrent)

    async def bounded_fetch(session, url):
        async with sem:
            return await fetch_one(session, url)

    connector = aiohttp.TCPConnector(limit=100)   # global connection pool
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [bounded_fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

# Usage:
results = asyncio.run(fetch_many(urls, max_concurrent=20))
```

---

## 🗄️ Chapter 8: Async Database Access

```python
import asyncio, asyncpg   # pip install asyncpg

# Connection pool (shared across all coroutines):
_pool = None

async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            "postgresql://user:pass@localhost/mydb",
            min_size=5,
            max_size=20,
        )
    return _pool

async def get_user(user_id: int) -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:   # borrows a connection from pool
        row = await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1", user_id
        )
        return dict(row) if row else None

async def create_user(name: str, email: str) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():   # async transaction
            user_id = await conn.fetchval(
                "INSERT INTO users(name, email) VALUES($1, $2) RETURNING id",
                name, email
            )
            await conn.execute(
                "INSERT INTO audit_log(user_id, action) VALUES($1, $2)",
                user_id, "created"
            )
            return user_id   # commits on exit, rolls back on exception
```

---

## 🔄 Chapter 9: Running Blocking Code in async Context

Sometimes you must call a blocking (synchronous) function from async code. Doing so directly freezes the event loop:

```python
# ❌ WRONG — blocks event loop for duration of call:
async def handler():
    data = requests.get("http://api.com").json()   # synchronous! blocks!
    compressed = gzip.compress(large_data)          # CPU-bound! blocks!

# ✅ CORRECT — offload to thread pool:
import asyncio
from concurrent.futures import ThreadPoolExecutor

_thread_pool = ThreadPoolExecutor(max_workers=10)

async def handler():
    loop = asyncio.get_event_loop()

    # Run I/O-blocking call in thread (event loop stays responsive):
    data = await loop.run_in_executor(
        _thread_pool,
        lambda: requests.get("http://api.com").json()
    )

    # Python 3.9+ — cleaner:
    data = await asyncio.to_thread(blocking_get, "http://api.com")

# When to use run_in_executor / asyncio.to_thread:
# - Calling synchronous library functions (PIL, pandas, boto3 sync)
# - CPU-bound work (won't parallelize due to GIL, but won't block loop)
# - For true CPU parallelism: ProcessPoolExecutor:
async def parallel_cpu():
    loop = asyncio.get_event_loop()
    process_pool = ProcessPoolExecutor()
    result = await loop.run_in_executor(process_pool, cpu_heavy_func, data)
```

---

## 🏭 Chapter 10: Async Context Managers and Iterators

```python
# Async context manager:
class AsyncDB:
    async def __aenter__(self):
        self.conn = await db.connect()
        return self.conn

    async def __aexit__(self, *args):
        await self.conn.close()
        return False

async with AsyncDB() as conn:
    await conn.execute("SELECT ...")

# Generator-based async context manager:
from contextlib import asynccontextmanager

@asynccontextmanager
async def db_transaction(dsn):
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

async with db_transaction("postgres://...") as conn:
    await conn.execute("INSERT ...")

# Async iterator:
class AsyncRange:
    def __init__(self, n):
        self.n = n
        self.i = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.i >= self.n:
            raise StopAsyncIteration
        await asyncio.sleep(0)   # yield to event loop
        val = self.i
        self.i += 1
        return val

async for n in AsyncRange(5):
    print(n)

# Async generator (simpler):
async def async_range(n):
    for i in range(n):
        await asyncio.sleep(0)
        yield i

async for n in async_range(5):
    print(n)

# Async comprehension:
results = [x async for x in async_range(10)]
results = {x: x**2 async for x in async_range(5)}
```

---

## 🛡️ Chapter 11: Error Handling and Cancellation

```python
import asyncio

# Task cancellation:
async def long_running():
    try:
        while True:
            await asyncio.sleep(1)   # CancelledError raised here on cancel()
            do_work()
    except asyncio.CancelledError:
        print("Task cancelled — cleaning up")
        await cleanup()
        raise   # MUST re-raise CancelledError!

async def main():
    task = asyncio.create_task(long_running())
    await asyncio.sleep(5)
    task.cancel()           # schedule cancellation
    try:
        await task          # wait for it to actually cancel
    except asyncio.CancelledError:
        print("Task was cancelled")

# Shielding from cancellation:
async def critical():
    # Even if outer task is cancelled, this continues:
    result = await asyncio.shield(must_complete())
    return result

# Timeout:
async def with_timeout():
    try:
        result = await asyncio.wait_for(slow_operation(), timeout=5.0)
    except asyncio.TimeoutError:
        # slow_operation was automatically cancelled
        use_default()

# TaskGroup (Python 3.11+) — structured concurrency:
async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(coro1())
        task2 = tg.create_task(coro2())
    # All tasks complete (or all cancelled on first exception)
    r1, r2 = task1.result(), task2.result()
```

---

## 📊 Chapter 12: asyncio Performance Patterns

### Connection Pooling

```python
# Always reuse connections — creating new ones is expensive:
# Bad:
async def bad_handler(request):
    conn = await asyncpg.connect(...)   # new connection per request!
    result = await conn.fetch(query)
    await conn.close()
    return result

# Good:
pool = await asyncpg.create_pool(dsn, min_size=5, max_size=20)

async def good_handler(request):
    async with pool.acquire() as conn:  # reuse from pool
        return await conn.fetch(query)
```

### Batching for Efficiency

```python
async def fetch_users(ids):
    # ❌ N+1 problem:
    return [await get_user(id) for id in ids]   # sequential!

    # ✅ Gather:
    return await asyncio.gather(*[get_user(id) for id in ids])

    # ✅ Even better: single batched query:
    async with pool.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM users WHERE id = ANY($1)", ids
        )
```

---

## 🔴 Chapter 13: Gotchas

```python
# 1 — Calling coroutine without await:
async def main():
    fetch("http://api.com")   # RuntimeWarning: coroutine was never awaited!
# Fix: await fetch("http://api.com")

# 2 — Running asyncio.run() inside running loop:
async def outer():
    asyncio.run(inner())   # RuntimeError: This event loop is already running
# Fix: await inner() or use create_task

# 3 — Blocking call in async code:
async def handler():
    time.sleep(5)   # blocks EVERYTHING for 5 seconds!
# Fix: await asyncio.sleep(5) or await asyncio.to_thread(time.sleep, 5)

# 4 — Not re-raising CancelledError:
async def worker():
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("cancelled")
        # forgetting 'raise' — task appears to complete normally!
# Fix: always re-raise CancelledError

# 5 — Creating tasks outside an async function:
task = asyncio.create_task(coro())   # RuntimeError: no running event loop
# Fix: create tasks inside async functions

# 6 — Thread-safety: asyncio objects are NOT thread-safe:
# Don't call coroutines or modify queues from non-async threads directly.
# Use: asyncio.run_coroutine_threadsafe(coro, loop)
```

---

## 🔥 Quick Reference

```python
# Top-level:
asyncio.run(coro())                  # run coroutine in new event loop

# Inside async def:
result = await coro()                # run and wait
task   = asyncio.create_task(coro()) # schedule concurrently
results= await asyncio.gather(*coros)          # concurrent, wait all
results= await asyncio.gather(*coros, return_exceptions=True)
done, pending = await asyncio.wait(tasks, timeout=5)
result = await asyncio.wait_for(coro(), timeout=5)
await asyncio.sleep(0)              # yield to event loop (no actual delay)
await asyncio.to_thread(sync_func, arg)   # run blocking fn in thread (3.9+)

# Task management:
task.cancel()
task.result()
task.exception()
task.done()
task.cancelled()

# Sync primitives:
lock  = asyncio.Lock()
sem   = asyncio.Semaphore(n)
event = asyncio.Event()
q     = asyncio.Queue(maxsize=n)

async with lock: ...
async with sem:  ...
await event.wait(); event.set(); event.clear()
await q.put(item); item = await q.get(); q.task_done()
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🧵 Threading Guide | [threading_guide.md](./threading_guide.md) |
| 🔥 Multiprocessing Guide | [multiprocessing_guide.md](./multiprocessing_guide.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Threading Guide →](./threading_guide.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Threading Guide](./threading_guide.md) · [Multiprocessing Guide](./multiprocessing_guide.md) · [Interview Q&A](./interview.md)
