# Asyncio — Practice

15 focused exercises from basic coroutines through async web scraping with rate limiting.

---

## Quick Index

| # | Difficulty | Concept |
|---|---|---|
| Q1 | 🟢 Easy | Basic coroutine: define and run with asyncio.run() |
| Q2 | 🟢 Easy | asyncio.sleep vs time.sleep |
| Q3 | 🟡 Medium | gather: fetch 3 URLs concurrently vs sequential |
| Q4 | 🟡 Medium | create_task: start tasks without waiting immediately |
| Q5 | 🟡 Medium | async with: async context manager |
| Q6 | 🟡 Medium | async for: iterate an async generator |
| Q7 | 🟡 Medium | asyncio.Queue: async producer-consumer |
| Q8 | 🟡 Medium | asyncio.Event: signal between coroutines |
| Q9 | 🟡 Medium | TaskGroup (Python 3.11+): structured concurrency |
| Q10 | 🟡 Medium | run_in_executor: blocking function in async code |
| Q11 | 🟠 Hard | asyncio.wait_for() with cancellation |
| Q12 | 🟠 Hard | Semaphore: limit concurrent requests to N |
| Q13 | 🟡 Medium | gather error handling: return_exceptions=True |
| Q14 | 🟠 Hard | Async generator: lazy data stream |
| Q15 | 🟠 Hard | Capstone: async web scraper with rate limiting |

---

### Q1 🟢 · Coroutine Basics — define and run with asyncio.run()

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

**Problem:** Write an `async def greet(name)` coroutine that prints "Hello, {name}!", awaits `asyncio.sleep(0.1)`, then prints "Goodbye, {name}!". Run it using `asyncio.run()`. Then show what happens if you call `greet("Alice")` without `await` or `asyncio.run()`.

<details>
<summary>💡 Hint</summary>
Calling `greet("Alice")` without `await` creates a coroutine object — nothing runs. You'll see a `RuntimeWarning`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def greet(name: str) -> str:
    print(f"Hello, {name}!")
    await asyncio.sleep(0.1)
    print(f"Goodbye, {name}!")
    return f"greeted {name}"

# Correct: asyncio.run() creates an event loop and runs the coroutine
result = asyncio.run(greet("Alice"))
print(result)  # greeted Alice

# Wrong: this returns a coroutine object, nothing runs
coro = greet("Bob")
print(coro)    # <coroutine object greet at 0x...>
# RuntimeWarning: coroutine 'greet' was never awaited
coro.close()   # suppress the warning
```

**Why:** `async def` functions return a coroutine object when called. They only execute when you `await` them or hand them to the event loop via `asyncio.run()`.
</details>

---

### Q2 🟢 · Blocking — asyncio.sleep vs time.sleep

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

**Problem:** Write three concurrent tasks: A (1s), B (0.5s), C (0.7s). Run them with `asyncio.gather()` using `asyncio.sleep()`. Total time should be ~1s. Then replace with `time.sleep()` inside one task and show it blocks the others (total time increases).

<details>
<summary>💡 Hint</summary>
`time.sleep()` blocks the OS thread — the event loop cannot run any other task. `asyncio.sleep()` only suspends the current coroutine.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio, time

async def task_async(name: str, delay: float) -> None:
    print(f"{name}: start")
    await asyncio.sleep(delay)   # non-blocking: event loop continues
    print(f"{name}: done ({delay}s)")

async def task_blocking(name: str, delay: float) -> None:
    print(f"{name}: start")
    time.sleep(delay)            # BLOCKS entire event loop!
    print(f"{name}: done ({delay}s)")

# Using asyncio.sleep — concurrent, total ~1s:
start = time.perf_counter()
asyncio.run(asyncio.gather(
    task_async("A", 1.0),
    task_async("B", 0.5),
    task_async("C", 0.7),
))
print(f"Async sleep: {time.perf_counter()-start:.2f}s")  # ~1.0s

# Using time.sleep in task A — A blocks the loop:
start = time.perf_counter()
asyncio.run(asyncio.gather(
    task_blocking("A", 1.0),    # blocks for 1s; B and C can't start
    task_async("B", 0.5),
    task_async("C", 0.7),
))
print(f"Blocking A:  {time.perf_counter()-start:.2f}s")  # ~1.7s+
```

**Why:** `time.sleep()` occupies the thread — the event loop is stuck. Other coroutines cannot run. Always use `await asyncio.sleep()` in async code.
</details>

---

### Q3 🟡 · Concurrency — gather: concurrent vs sequential

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

**Problem:** Simulate fetching 3 URLs with delays of 1.0s, 0.8s, 0.6s. First run them sequentially (await each one). Then run them concurrently with `asyncio.gather()`. Print the elapsed time for both and the speedup factor.

<details>
<summary>💡 Hint</summary>
Sequential total: 1.0+0.8+0.6=2.4s. Concurrent total: max(1.0, 0.8, 0.6)=1.0s. Speedup: 2.4×.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio, time

async def fetch(url: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"data from {url}"

async def sequential():
    r1 = await fetch("api1.com", 1.0)
    r2 = await fetch("api2.com", 0.8)
    r3 = await fetch("api3.com", 0.6)
    return r1, r2, r3

async def concurrent():
    return await asyncio.gather(
        fetch("api1.com", 1.0),
        fetch("api2.com", 0.8),
        fetch("api3.com", 0.6),
    )

start = time.perf_counter()
asyncio.run(sequential())
seq_time = time.perf_counter() - start
print(f"Sequential:  {seq_time:.2f}s")  # ~2.4s

start = time.perf_counter()
asyncio.run(concurrent())
con_time = time.perf_counter() - start
print(f"Concurrent:  {con_time:.2f}s")  # ~1.0s
print(f"Speedup:     {seq_time/con_time:.1f}x")
```

**Why:** `gather()` wraps each coroutine in a Task and schedules all to start immediately. While one is suspended waiting for I/O, the others make progress.
</details>

---

### Q4 🟡 · Tasks — create_task: start background work

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

**Problem:** Use `asyncio.create_task()` to start two long-running tasks (sleep 0.5s each). While they run in the background, do some synchronous computation. Then await both tasks. Show the total time is ~0.5s, not 1s.

<details>
<summary>💡 Hint</summary>
`create_task()` schedules the coroutine immediately. The task starts running at the next `await` point. Awaiting it later just collects the result.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio, time

async def slow_fetch(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"result from {name}"

async def main():
    # Schedule both tasks — they start at the next await
    task1 = asyncio.create_task(slow_fetch("service_A", 0.5))
    task2 = asyncio.create_task(slow_fetch("service_B", 0.5))

    # Do sync work while tasks run in background
    total = sum(range(100_000))   # runs while tasks are sleeping

    # Now collect results — tasks may already be done
    r1 = await task1
    r2 = await task2
    print(r1, r2)

start = time.perf_counter()
asyncio.run(main())
print(f"Total: {time.perf_counter()-start:.2f}s")  # ~0.5s not 1.0s
```

**Why:** `create_task()` is useful when you want to start work and do other things before collecting results. Unlike `gather()`, you get handles to individual tasks and can cancel them selectively.
</details>

---

### Q5 🟡 · async with — async context manager for DB connection

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

**Problem:** Create an `AsyncDB` class with `__aenter__` (awaits a 0.05s "connection" delay, prints "connected") and `__aexit__` (awaits 0.01s "disconnect" delay, prints "disconnected"). Use it with `async with` to simulate a query.

<details>
<summary>💡 Hint</summary>
`__aenter__` and `__aexit__` must be `async def` methods. `async with` calls them with `await`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

class AsyncDB:
    def __init__(self, url: str):
        self.url = url
        self.conn_id = None

    async def __aenter__(self):
        await asyncio.sleep(0.05)   # simulate TCP handshake
        self.conn_id = 1234
        print(f"Connected to {self.url} [conn={self.conn_id}]")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await asyncio.sleep(0.01)   # simulate graceful close
        print(f"Disconnected [conn={self.conn_id}]")
        return False                # don't suppress exceptions

    async def query(self, sql: str) -> list:
        await asyncio.sleep(0.02)
        return [{"id": 1, "sql": sql}]

async def main():
    async with AsyncDB("postgresql://localhost/mydb") as db:
        rows = await db.query("SELECT * FROM users")
        print(f"Got {len(rows)} rows")
    # Connection guaranteed closed here

asyncio.run(main())
```

**Why:** `async with` ensures `__aexit__` runs even if an exception occurs inside the block. This is the correct pattern for any resource that needs async cleanup (network connections, file handles, transactions).
</details>

---

### Q6 🟡 · async for — iterate an async generator

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

**Problem:** Write an `async def paginated(total_pages)` generator that yields one page of data (a list of 3 items) per iteration, awaiting `asyncio.sleep(0.02)` between pages. Use `async for` to consume it and print each page.

<details>
<summary>💡 Hint</summary>
`async def` + `yield` = async generator. Consume with `async for item in gen():`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def paginated(total_pages: int):
    for page in range(1, total_pages + 1):
        await asyncio.sleep(0.02)   # simulate HTTP request per page
        yield {"page": page, "items": [f"item_{(page-1)*3+i}" for i in range(1, 4)]}

async def main():
    async for page_data in paginated(4):
        print(f"Page {page_data['page']}: {page_data['items']}")
        if page_data['page'] >= 3:
            break   # early exit — stop fetching

asyncio.run(main())
```

**Why:** Async generators allow lazy streaming from async sources. They never load all data into memory — the caller controls how many items to consume. Classic use: paginated APIs, database cursor streaming, WebSocket message streams.
</details>

---

### Q7 🟡 · Async Queue — async producer-consumer

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

**Problem:** Write an async producer that puts integers 1–6 onto an `asyncio.Queue(maxsize=3)`, one every 0.05s. Write two async consumer workers that each await items, print them squared, and call `queue.task_done()`. Run all three concurrently with `asyncio.gather()`.

<details>
<summary>💡 Hint</summary>
`await queue.put(item)` suspends if the queue is full. `await queue.get()` suspends if empty. Each consumer needs its own sentinel or you can use `queue.join()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def producer(q: asyncio.Queue, items: list) -> None:
    for item in items:
        await asyncio.sleep(0.05)
        await q.put(item)
    # Two sentinels — one per consumer
    await q.put(None)
    await q.put(None)

async def consumer(q: asyncio.Queue, worker_id: int) -> None:
    while True:
        item = await q.get()
        if item is None:
            q.task_done()
            break
        print(f"Worker-{worker_id}: {item} → {item**2}")
        q.task_done()

async def main():
    q = asyncio.Queue(maxsize=3)   # bounded: producer pauses when full
    await asyncio.gather(
        producer(q, list(range(1, 7))),
        consumer(q, 1),
        consumer(q, 2),
    )

asyncio.run(main())
```

**Why:** `asyncio.Queue` is the async equivalent of `queue.Queue`. `await put()` and `await get()` yield to the event loop rather than blocking the thread. Use this for async pipelines and job queues.
</details>

---

### Q8 🟡 · Signaling — asyncio.Event between coroutines

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

**Problem:** Use `asyncio.Event` to coordinate a server coroutine and two client coroutines. The server sleeps 0.2s (startup), then sets the event. Each client awaits the event before making requests. Show clients don't start until the server signals ready.

<details>
<summary>💡 Hint</summary>
`await event.wait()` suspends the coroutine until `event.set()` is called. All waiters are woken simultaneously.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def server(ready_event: asyncio.Event) -> None:
    print("Server: initializing...")
    await asyncio.sleep(0.2)   # simulate startup
    print("Server: ready!")
    ready_event.set()           # wake all waiting clients

async def client(name: str, ready_event: asyncio.Event) -> None:
    print(f"{name}: waiting for server...")
    await ready_event.wait()    # yields until event.set()
    print(f"{name}: server is up, sending requests")
    await asyncio.sleep(0.1)
    print(f"{name}: done")

async def main():
    ready = asyncio.Event()
    await asyncio.gather(
        server(ready),
        client("Client-A", ready),
        client("Client-B", ready),
    )

asyncio.run(main())
```

**Why:** `asyncio.Event` is the async equivalent of `threading.Event`. It's cooperative — `wait()` yields to the event loop rather than blocking the thread. All waiters are notified simultaneously when `set()` is called.
</details>

---

### Q9 🟡 · TaskGroup — structured concurrency (Python 3.11+)

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

**Problem:** Use `asyncio.TaskGroup` to run three tasks concurrently. Show that if one task raises an exception, the group cancels the remaining tasks. Catch the `ExceptionGroup` and print which task failed.

<details>
<summary>💡 Hint</summary>
`async with asyncio.TaskGroup() as tg: tg.create_task(coro())`. If any task raises, all others are cancelled and an `ExceptionGroup` is raised.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def task_ok(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"{name} done"

async def task_fail(name: str) -> None:
    await asyncio.sleep(0.1)
    raise ValueError(f"{name} failed!")

async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(task_ok("A", 0.5))
            t2 = tg.create_task(task_fail("B"))   # fails at 0.1s
            t3 = tg.create_task(task_ok("C", 0.3))
        # Reaches here only if all tasks succeed
    except* ValueError as eg:
        print(f"Caught errors: {eg.exceptions}")
        # t1 and t3 were cancelled when t2 failed

asyncio.run(main())
```

**Why:** `TaskGroup` provides structured concurrency — the group is the unit of lifetime. If any task fails, all others are cancelled and cleanup is guaranteed. This is safer than `gather()` which can leave tasks running after an exception.
</details>

---

### Q10 🟡 · Blocking Bridge — run_in_executor

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

**Problem:** Write a synchronous (blocking) `read_file(path)` function that sleeps 0.3s (simulating slow I/O). Call it from an async context using `loop.run_in_executor(None, ...)` so the event loop is not blocked. Show another coroutine runs concurrently while the executor task is waiting.

<details>
<summary>💡 Hint</summary>
`await loop.run_in_executor(None, fn, arg)` runs `fn(arg)` in a thread pool and yields to the event loop until it finishes.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio, time

def read_file(path: str) -> str:
    """Blocking — simulates slow synchronous I/O."""
    time.sleep(0.3)
    return f"contents of {path}"

async def background_task() -> None:
    print("Background task: running while file loads...")
    await asyncio.sleep(0.1)
    print("Background task: done")

async def main():
    loop = asyncio.get_event_loop()

    # Schedule blocking function in thread pool — event loop stays free
    file_future = loop.run_in_executor(None, read_file, "/data/file.txt")

    # This runs concurrently while read_file is blocking in a thread
    await background_task()

    # Now collect the file result
    content = await file_future
    print(f"File: {content}")

    # Python 3.9+ cleaner syntax:
    # content = await asyncio.to_thread(read_file, "/data/file.txt")

asyncio.run(main())
```

**Why:** `run_in_executor` offloads blocking calls to a thread pool, freeing the event loop to serve other coroutines. Essential when you must use synchronous libraries (requests, pandas, PIL) in async code.
</details>

---

### Q11 🟠 · Timeout — asyncio.wait_for() with cancellation

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

**Problem:** Write `slow_op()` that sleeps 2 seconds. Wrap it with `asyncio.wait_for()` with a 0.5s timeout. Catch `asyncio.TimeoutError`. Verify the underlying task was cancelled. Then show how to clean up inside the coroutine using `try/finally`.

<details>
<summary>💡 Hint</summary>
`asyncio.wait_for()` automatically cancels the wrapped coroutine when the timeout expires. Catch `asyncio.TimeoutError` in the caller.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def slow_op(label: str) -> str:
    try:
        print(f"[{label}] starting...")
        await asyncio.sleep(2.0)
        return "completed"
    except asyncio.CancelledError:
        print(f"[{label}] was cancelled")
        raise   # MUST re-raise CancelledError
    finally:
        print(f"[{label}] cleanup (always runs)")

async def main():
    # wait_for wraps slow_op in a Task and sets a timer
    try:
        result = await asyncio.wait_for(slow_op("A"), timeout=0.5)
        print(f"Result: {result}")
    except asyncio.TimeoutError:
        print("Timed out after 0.5s — slow_op was cancelled")

asyncio.run(main())
```

**Why:** `wait_for()` injects `CancelledError` into the coroutine at its next `await` point when the timeout expires. The `finally` block always runs — use it for resource cleanup. Always re-raise `CancelledError` to propagate the cancellation correctly.
</details>

---

### Q12 🟠 · Rate Limiting — Semaphore to cap concurrent requests

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

**Problem:** Simulate fetching 10 URLs where each request takes 0.1s. Without a semaphore, all 10 fire simultaneously. Use `asyncio.Semaphore(3)` to limit to 3 concurrent requests. Show that with the semaphore, total time is roughly `ceil(10/3) * 0.1 ≈ 0.4s` instead of 0.1s.

<details>
<summary>💡 Hint</summary>
`async with sem:` inside the fetch coroutine blocks (asynchronously) if the semaphore count is 0. At most N coroutines can hold the semaphore simultaneously.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio, time

async def fetch(session_id: int, sem: asyncio.Semaphore) -> str:
    async with sem:                        # blocks if 3 already active
        await asyncio.sleep(0.1)           # simulate HTTP request
        return f"response_{session_id}"

async def main():
    sem = asyncio.Semaphore(3)             # max 3 concurrent

    start = time.perf_counter()
    tasks = [fetch(i, sem) for i in range(10)]
    results = await asyncio.gather(*tasks)
    elapsed = time.perf_counter() - start

    print(f"{len(results)} results in {elapsed:.2f}s")
    # With sem(3): ~0.4s  (batches of 3: 0.1+0.1+0.1+0.1 = 0.4s)
    # Without sem: ~0.1s  (all 10 fire at once — fine for 10, bad for 10,000)

asyncio.run(main())
```

**Why:** Without a semaphore, 10,000 coroutines could each open a DB connection simultaneously, overwhelming the server. The semaphore is the async equivalent of a connection pool size limit.
</details>

---

### Q13 🟡 · Error Handling — gather with return_exceptions=True

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)

**Problem:** Create 5 tasks where task 2 and task 4 raise exceptions. Use `asyncio.gather(*tasks, return_exceptions=True)` to collect results. Show that exceptions are returned as values (not raised). Filter and count successes vs failures.

<details>
<summary>💡 Hint</summary>
With `return_exceptions=True`, exceptions are returned as exception objects in the results list instead of being raised. Check `isinstance(result, Exception)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def task(n: int) -> int:
    await asyncio.sleep(0.05)
    if n in (2, 4):
        raise ValueError(f"Task {n} failed")
    return n * 10

async def main():
    coros = [task(n) for n in range(1, 6)]

    # return_exceptions=True: exceptions returned as values, not raised
    results = await asyncio.gather(*coros, return_exceptions=True)

    successes = [(i+1, r) for i, r in enumerate(results) if not isinstance(r, Exception)]
    failures  = [(i+1, r) for i, r in enumerate(results) if isinstance(r, Exception)]

    for task_id, result in successes:
        print(f"Task {task_id}: {result}")
    for task_id, exc in failures:
        print(f"Task {task_id}: ERROR — {exc}")

    print(f"{len(successes)} succeeded, {len(failures)} failed")

asyncio.run(main())
```

**Why:** By default, `gather()` raises the first exception and cancels remaining tasks. `return_exceptions=True` is the "collect all results, handle errors individually" mode — useful for bulk operations where partial failure is acceptable.
</details>

---

### Q14 🟠 · Async Generator — lazy data stream

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)

**Problem:** Write an async generator `event_stream(n)` that yields `n` events, each after a random 0.02–0.08s delay. Each event is a dict `{"id": i, "value": i**2}`. Consume it with `async for`, stopping early after the first event where `value > 20`.

<details>
<summary>💡 Hint</summary>
`async def gen(): yield item` — use `break` inside `async for` to stop early. The generator is not exhausted.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio, random

async def event_stream(n: int):
    for i in range(1, n + 1):
        await asyncio.sleep(random.uniform(0.02, 0.08))
        yield {"id": i, "value": i ** 2}

async def main():
    events_consumed = 0
    async for event in event_stream(20):
        print(f"Event {event['id']}: value={event['value']}")
        events_consumed += 1
        if event["value"] > 20:
            print(f"Stopping early after {events_consumed} events")
            break   # generator is not exhausted — remaining events never fetched

asyncio.run(main())
```

**Why:** Async generators produce values on demand — they only fetch the next item when the consumer asks. Perfect for paginated APIs, database cursors, or WebSocket message streams where you don't want to load everything into memory.
</details>

---

### Q15 🟠 · Capstone — Async web scraper with rate limiting

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)

**Problem:** Build an async scraper that fetches 15 URLs concurrently with:
- Max 4 concurrent requests (semaphore)
- 10% random failure rate (raise `ConnectionError`)
- Retry failed URLs once
- Collect final results: successes and permanent failures
- Use `asyncio.gather(return_exceptions=True)` for the retry pass

<details>
<summary>💡 Hint</summary>
First pass: gather with return_exceptions=True. Separate successes from failures. Second pass: retry failures with gather again. Combine results.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio, random, time

sem = asyncio.Semaphore(4)   # max 4 concurrent

async def fetch(url: str) -> dict:
    async with sem:
        await asyncio.sleep(random.uniform(0.05, 0.15))
        if random.random() < 0.1:
            raise ConnectionError(f"Failed: {url}")
        return {"url": url, "status": 200, "items": random.randint(1, 100)}

async def scrape_with_retry(urls: list) -> tuple[list, list]:
    # First pass
    results = await asyncio.gather(*[fetch(u) for u in urls], return_exceptions=True)

    successes  = [(u, r) for u, r in zip(urls, results) if isinstance(r, dict)]
    to_retry   = [u for u, r in zip(urls, results) if isinstance(r, Exception)]

    # Second pass — retry failures once
    if to_retry:
        retry_results = await asyncio.gather(*[fetch(u) for u in to_retry], return_exceptions=True)
        for url, result in zip(to_retry, retry_results):
            if isinstance(result, dict):
                successes.append((url, result))
            else:
                pass  # permanent failure

    failures = [u for u in to_retry if all(u != s[0] for s in successes if u in to_retry)]
    return successes, failures

async def main():
    urls = [f"https://example.com/page/{i}" for i in range(15)]
    start = time.perf_counter()
    successes, failures = await scrape_with_retry(urls)
    elapsed = time.perf_counter() - start

    print(f"Scraped {len(successes)} successfully, {len(failures)} failed")
    print(f"Total time: {elapsed:.2f}s (15 URLs, max 4 concurrent)")

asyncio.run(main())
```

**Why:** This combines semaphore-based rate limiting, `return_exceptions=True` for resilient gathering, and a retry pattern — all common in production async scrapers and API clients.
</details>

---

## 🔁 Navigation

| | |
|---|---|
| ⬆️ Asyncio Theory | [theory.md](./theory.md) |
| 💻 Practice Local | [practice_local.py](./practice_local.py) |
| 🧵 Threading Practice | [../01_threading/practice.md](../01_threading/practice.md) |
| 🔥 Multiprocessing Practice | [../02_multiprocessing/practice.md](../02_multiprocessing/practice.md) |
| 🗂️ Root Practice | [../practice.md](../practice.md) |

---

**[Back to README](../../README.md)**

**Prev:** [Multiprocessing Practice](../02_multiprocessing/practice.md) | **Next:** [Root Practice →](../practice.md)

**Related Topics:** [Asyncio Theory](./theory.md) · [Threading Practice](../01_threading/practice.md) · [Multiprocessing Practice](../02_multiprocessing/practice.md) · [Root Practice](../practice.md)
