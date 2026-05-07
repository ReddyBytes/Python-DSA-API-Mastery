# Asyncio — Theory

A single chef can cook twenty dishes at once — not by moving supernaturally fast, but by never standing idle at the stove. The moment a pot needs to simmer for five minutes, they start chopping the next ingredient. That is asyncio: one thread, many tasks, no wasted waits.

---

## 📌 Learning Priority

**Must Learn** — Core use, interview essential:
`async def` · `await` · `asyncio.run()` · `asyncio.gather()` · `asyncio.create_task()`

**Should Learn** — Important for real projects:
`async with` · `async for` · `asyncio.sleep` · `TaskGroup` (3.11+) · `asyncio.wait_for`

**Good to Know** — Useful in specific situations:
`asyncio.Queue` · `asyncio.Event` · `asyncio.Semaphore`

**Reference** — Know it exists, look up when needed:
`asyncio.get_event_loop()` · `loop.run_until_complete()` · `loop.run_in_executor()` · `asyncio.shield()`

---

## Chapter 1: The Mental Model — Cooperative Multitasking

Asyncio is **cooperative**, not preemptive. A task runs until it voluntarily yields control at an `await` point. No other task can interrupt it between two `await` statements.

```
THREADING (preemptive):
  OS can interrupt thread A at any time
  → Must protect shared state with locks
  → Context switches happen at unpredictable moments

ASYNCIO (cooperative):
  Task A runs until it hits `await`
  → Control returns to event loop
  → Event loop picks next ready task
  → Between two awaits: code is effectively atomic, no interruption possible
```

**The event loop diagram:**

```
EVENT LOOP

  ready_queue:  [Task A, Task C]
  waiting:      {Task B: "DB reply", Task D: "timer 5s"}

  1. Take Task A from ready_queue
  2. Run Task A until it hits `await db.query()`
  3. Register Task A in waiting set (waiting on DB socket)
  4. Take Task C from ready_queue
  5. Run Task C until it hits `await asyncio.sleep(1)`
  6. Register Task C in waiting set (waiting on timer)
  7. Poll I/O (epoll/kqueue): DB socket ready → move Task A to ready_queue
  8. Run Task A from where it paused
  ...repeat...
```

One thread — but thousands of concurrent tasks all making progress. The key insight: **between any two `await` points your code runs atomically**. This means no race conditions on simple shared state. But it also means a task that never yields blocks every other task.

---

## Chapter 2: Coroutines — async def and await

A **coroutine** is a function that can be paused and resumed. Define one with `async def`.

```python
# Regular function — runs to completion on each call
def regular():
    result = compute()
    return result

# Coroutine function — calling it returns a coroutine object, nothing runs yet
async def fetch(url: str) -> dict:
    result = await http.get(url)   # ← pause here until HTTP reply arrives
    return result
```

**Critical:** calling an `async def` function does NOT run it:

```python
async def greet(name: str) -> str:
    print(f"Hello, {name}!")
    return f"greeted {name}"

coro = greet("Alice")
# "Hello, Alice!" was NOT printed — coro is just a coroutine object

# To actually run it:
result = asyncio.run(greet("Alice"))      # at the top level
# or inside another async def:
result = await greet("Alice")
```

**What `await` does:**

```
await expr:
  1. Evaluate expr → get an awaitable (coroutine, Future, or Task)
  2. Start running it
  3. If it needs to wait for I/O → suspend THIS coroutine, yield to event loop
  4. Event loop runs other ready coroutines
  5. When the awaited operation finishes → resume THIS coroutine
  6. The result of expr is returned as the value of the await expression

await does NOT block the thread.
It only suspends the current coroutine.
```

---

## Chapter 3: The Event Loop — asyncio.run()

`asyncio.run()` is your entry point for all async code at the top level:

```python
import asyncio

async def main():
    print("hello from async main")
    await asyncio.sleep(1)
    print("done")

asyncio.run(main())
# Creates a new event loop, runs main() to completion, closes the loop
```

`asyncio.run()` is the only correct way to start an event loop from synchronous code (Python 3.7+). Do not call it from inside an already-running async context — that raises `RuntimeError`.

**How the event loop works internally (simplified):**

```python
class EventLoop:
    def __init__(self):
        self.ready    = deque()   # tasks ready to run now
        self.waiting  = {}        # tasks waiting for I/O or timer

    def run_until_complete(self, coro):
        task = Task(coro)
        self.ready.append(task)
        while self.ready or self.waiting:
            while self.ready:
                task = self.ready.popleft()
                task.step()             # advance coroutine to next await
            events = poll_io(timeout=next_timer_deadline)
            for event in events:
                task = self.waiting.pop(event.fd)
                self.ready.append(task)  # I/O ready → back to run queue
```

---

## Chapter 4: Concurrent Coroutines — gather() and create_task()

Running coroutines sequentially with `await` one at a time gives no concurrency benefit:

```python
# SEQUENTIAL — waits 2s then 3s = 5s total
async def main():
    r1 = await fetch("api1.com", 2)
    r2 = await fetch("api2.com", 3)
```

Two tools to run coroutines concurrently:

**asyncio.gather() — fan out, wait for all:**

```python
async def main():
    r1, r2, r3 = await asyncio.gather(
        fetch("api1.com", 2),
        fetch("api2.com", 3),
        fetch("api3.com", 1),
    )
    # All three start simultaneously
    # Total time ≈ 3s (longest single call), not 2+3+1=6s
```

`gather()` returns results in the **same order as input**, regardless of which finishes first.

**asyncio.create_task() — schedule explicitly:**

```python
async def main():
    # create_task() schedules the coroutine immediately — it starts running now
    task1 = asyncio.create_task(fetch("api1.com", 2))
    task2 = asyncio.create_task(fetch("api2.com", 3))

    # Both tasks are already running. Do other work here if needed.
    compute_something_local()

    r1 = await task1   # wait for result
    r2 = await task2

# TaskGroup (Python 3.11+) — structured concurrency, safer cancellation:
async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch("api1.com", 2))
        task2 = tg.create_task(fetch("api2.com", 3))
    # Both complete (or both cancelled if one raises)
    r1, r2 = task1.result(), task2.result()
```

**gather vs create_task — when to use which:**

```
asyncio.gather():
  + Simple — one line to run N coroutines and get N results
  + Results in input order
  - Less control over individual task lifecycle

asyncio.create_task():
  + Can start tasks and do other work before awaiting
  + Can cancel individual tasks
  + Can check task status mid-flight

TaskGroup (3.11+):
  + Structured: if one task fails, others are cancelled
  + Cleaner resource management than gather
```

---

## Chapter 5: asyncio.sleep vs time.sleep

This is the single most common asyncio mistake. `time.sleep()` blocks the **entire thread** — the event loop stops dead. `asyncio.sleep()` only suspends the current coroutine; the event loop continues serving others.

```python
import asyncio, time

# WRONG — blocks the event loop for 2 seconds:
async def bad_handler():
    time.sleep(2)           # everything stops for 2 seconds!

# CORRECT — suspends only this coroutine:
async def good_handler():
    await asyncio.sleep(2)  # event loop keeps running; other tasks proceed

# Demonstration:
async def demonstrate():
    async def task(name, delay):
        print(f"{name}: starting")
        await asyncio.sleep(delay)   # non-blocking
        print(f"{name}: done")

    # Run three tasks concurrently:
    await asyncio.gather(
        task("A", 1.0),
        task("B", 0.5),
        task("C", 0.7),
    )
    # Prints: A,B,C start, then B done (0.5s), C done (0.7s), A done (1.0s)
    # Total: ~1.0s not 2.2s
```

**`await asyncio.sleep(0)`** — yield to the event loop for zero seconds. Use this in long CPU loops to let other tasks run occasionally:

```python
async def cpu_heavy():
    for i in range(1_000_000):
        do_work(i)
        if i % 1000 == 0:
            await asyncio.sleep(0)  # ← let event loop check for I/O
```

---

## Chapter 6: async for and async with

Libraries that do I/O (HTTP sessions, DB connections, file handles) provide async context managers and iterators that must be used with `async with` / `async for`.

**async with:**

```python
# async context manager: __aenter__ and __aexit__ are coroutines
async with aiohttp.ClientSession() as session:
    async with session.get("https://api.example.com/data") as response:
        data = await response.json()
# session and response are properly closed even if exceptions occur
```

**Define your own async context manager:**

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def db_transaction(dsn: str):
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
    await conn.execute("INSERT INTO users(name) VALUES($1)", "Alice")
```

**async for:**

```python
# async generator — yield inside async def
async def paginated_results(endpoint: str):
    page = 1
    while True:
        data = await fetch_page(endpoint, page)
        if not data:
            return
        for item in data:
            yield item
        page += 1

async def process_all():
    async for record in paginated_results("/products"):
        await save(record)   # process lazily, never load all into memory
```

---

## Chapter 7: Real Patterns — Async HTTP and Async DB

**Async HTTP with aiohttp:**

```python
import asyncio, aiohttp

async def fetch_one(session: aiohttp.ClientSession, url: str) -> dict:
    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
        resp.raise_for_status()
        return await resp.json()

async def fetch_many(urls: list, max_concurrent: int = 20) -> list:
    sem = asyncio.Semaphore(max_concurrent)   # ← limit concurrency

    async def bounded_fetch(session, url):
        async with sem:                        # at most N at a time
            return await fetch_one(session, url)

    async with aiohttp.ClientSession() as session:
        tasks = [bounded_fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

results = asyncio.run(fetch_many(urls, max_concurrent=20))
```

**Async DB with asyncpg:**

```python
import asyncio, asyncpg

async def main():
    pool = await asyncpg.create_pool(
        "postgresql://user:pass@localhost/mydb",
        min_size=5, max_size=20,
    )

    async with pool.acquire() as conn:          # borrow a connection from pool
        row = await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1", user_id
        )

    await pool.close()
```

**run_in_executor — calling blocking code from async:**

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

_thread_pool = ThreadPoolExecutor(max_workers=10)

async def handler():
    loop = asyncio.get_event_loop()

    # Run a synchronous/blocking function without blocking the event loop:
    data = await loop.run_in_executor(
        _thread_pool,
        lambda: requests.get("https://api.example.com").json()
    )

    # Python 3.9+ — cleaner syntax:
    data = await asyncio.to_thread(blocking_function, arg1, arg2)
```

---

## Chapter 8: Common Mistakes

```python
# 1 — Calling a coroutine without await
async def main():
    fetch("http://api.com")   # RuntimeWarning: coroutine never awaited
# Fix: result = await fetch("http://api.com")

# 2 — Calling asyncio.run() inside a running event loop
async def outer():
    asyncio.run(inner())   # RuntimeError: event loop already running
# Fix: result = await inner()

# 3 — Using time.sleep instead of asyncio.sleep
async def handler():
    time.sleep(2)           # blocks the entire event loop for 2 seconds!
# Fix: await asyncio.sleep(2)

# 4 — Blocking call in async code (requests, pandas, PIL, boto3 sync)
async def bad():
    data = requests.get(url).json()   # blocks everything
# Fix: await asyncio.to_thread(requests.get, url)
#   or: use aiohttp instead

# 5 — Swallowing CancelledError
async def worker():
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("cancelled")
        # forgetting raise → task appears to complete normally!
# Fix: always re-raise CancelledError

# 6 — Creating tasks outside async context
task = asyncio.create_task(coro())   # RuntimeError: no running event loop
# Fix: create tasks only inside async functions

# 7 — Mixing sync and async code incorrectly
# asyncio objects (Lock, Queue, Event) are NOT thread-safe
# Don't access them from non-async threads directly
# Use asyncio.run_coroutine_threadsafe(coro, loop) to bridge
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬆️ Root Theory | [../theory.md](../theory.md) |
| 💻 Practice | [practice.md](./practice.md) |
| 🧵 Threading | [../01_threading/theory.md](../01_threading/theory.md) |
| 🔥 Multiprocessing | [../02_multiprocessing/theory.md](../02_multiprocessing/theory.md) |
| ⚡ Cheatsheet | [../cheetsheet.md](../cheetsheet.md) |
| 🔥 Interview Q&A | [../interview.md](../interview.md) |

---

**[Back to README](../../README.md)**

**Prev:** [Multiprocessing Theory](../02_multiprocessing/theory.md) | **Next:** [Root Cheat Sheet →](../cheetsheet.md)

**Related Topics:** [Root Theory](../theory.md) · [Threading](../01_threading/theory.md) · [Multiprocessing](../02_multiprocessing/theory.md) · [Cheat Sheet](../cheetsheet.md) · [Interview Q&A](../interview.md)
