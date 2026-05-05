"""
13_concurrency/async_programming.py
======================================
CONCEPT: async/await — cooperative multitasking in a single thread via an
event loop. Python's asyncio implementation of coroutines.
WHY THIS MATTERS: A single asyncio event loop can handle tens of thousands of
concurrent I/O operations without threads. HTTP servers, WebSocket services,
and database connection pools all use this model. Understanding it is required
for modern Python backend development.
KEY MENTAL MODEL: `await` yields control back to the event loop. While your
coroutine waits for I/O, the event loop runs OTHER coroutines — no blocking.

Prerequisite: Modules 01–12 (especially generators — async is built on them)
"""

import asyncio
import time
import random

# =============================================================================
# SECTION 1: Coroutines — the building block of async Python
# =============================================================================

# CONCEPT: `async def` creates a coroutine function. Calling it returns a
# coroutine OBJECT — no code runs yet (just like a generator).
# `await expr` suspends the current coroutine and hands control to the event
# loop until `expr` is ready. The event loop can run other coroutines in that
# suspension window.

print("=== Section 1: Coroutine Basics ===")

async def fetch_data(source: str, delay: float) -> dict:
    """
    Simulate an async I/O operation (HTTP request, DB query, etc.).
    `await asyncio.sleep()` releases control to the event loop for `delay`
    seconds — the loop runs other coroutines in that time.
    """
    print(f"  [→] Starting fetch: {source}")
    await asyncio.sleep(delay)   # non-blocking sleep — event loop runs others
    print(f"  [←] Done: {source}  ({delay:.2f}s)")
    return {"source": source, "data": f"result_of_{source}"}


async def main_sequential():
    """Sequential: waits for each before starting the next."""
    r1 = await fetch_data("users_db", 0.3)
    r2 = await fetch_data("products_db", 0.2)
    r3 = await fetch_data("orders_api", 0.1)
    return [r1, r2, r3]


async def main_concurrent():
    """Concurrent: all three run at the same time via gather()."""
    results = await asyncio.gather(
        fetch_data("users_db", 0.3),
        fetch_data("products_db", 0.2),
        fetch_data("orders_api", 0.1),
    )
    return results


start = time.perf_counter()
results = asyncio.run(main_sequential())
print(f"  Sequential time: {time.perf_counter() - start:.2f}s\n")

start = time.perf_counter()
results = asyncio.run(main_concurrent())
print(f"  Concurrent time: {time.perf_counter() - start:.2f}s  (≈0.3s max delay)")
print(f"  Results: {[r['source'] for r in results]}")


# =============================================================================
# SECTION 2: asyncio.gather vs asyncio.create_task
# =============================================================================

# CONCEPT:
# asyncio.gather(*coros)   — run multiple coroutines concurrently, wait for all.
#                            returns results in the SAME ORDER as inputs.
# asyncio.create_task(coro) — schedule a coroutine NOW, returns a Task.
#                             Task runs even if you don't immediately await it.
# asyncio.wait()           — like gather but with FIRST_COMPLETED/ALL_DONE modes.

print("\n=== Section 2: gather vs create_task ===")

async def demonstrate_tasks():
    # create_task schedules immediately — tasks are ALREADY running before we await
    task_a = asyncio.create_task(fetch_data("service_A", 0.3), name="TaskA")
    task_b = asyncio.create_task(fetch_data("service_B", 0.1), name="TaskB")
    task_c = asyncio.create_task(fetch_data("service_C", 0.2), name="TaskC")

    # do some sync work here while tasks run concurrently
    total = sum(range(10_000))   # quick CPU work

    # now await results
    results = await asyncio.gather(task_a, task_b, task_c)
    print(f"  All tasks done. Results: {[r['source'] for r in results]}")

    # Check task state
    print(f"  task_a done: {task_a.done()}, cancelled: {task_a.cancelled()}")


asyncio.run(demonstrate_tasks())


# =============================================================================
# SECTION 3: Handling errors in async code
# =============================================================================

# CONCEPT: asyncio.gather() by default cancels all tasks if one raises.
# Use return_exceptions=True to collect errors instead of raising immediately.
# Task exceptions must be awaited/retrieved — if you never await a failed Task,
# Python logs "Task exception was never retrieved" as a warning.

print("\n=== Section 3: Async Error Handling ===")

async def risky_fetch(url: str, should_fail: bool = False) -> dict:
    await asyncio.sleep(random.uniform(0.05, 0.15))
    if should_fail:
        raise ConnectionError(f"Failed to connect to {url}")
    return {"url": url, "status": 200}


async def gather_with_errors():
    tasks = [
        risky_fetch("https://api.example.com/users"),
        risky_fetch("https://api.example.com/broken", should_fail=True),
        risky_fetch("https://api.example.com/orders"),
    ]

    # return_exceptions=True: exceptions are returned as values, not raised
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            print(f"  Error: {type(result).__name__}: {result}")
        else:
            print(f"  Success: {result['url']} → {result['status']}")


asyncio.run(gather_with_errors())


# =============================================================================
# SECTION 4: Timeouts and cancellation
# =============================================================================

# CONCEPT: asyncio.wait_for(coro, timeout) raises asyncio.TimeoutError if the
# coroutine doesn't complete within the timeout. It CANCELS the underlying task.
# Task.cancel() injects asyncio.CancelledError at the next await point.
# Always use try/finally in coroutines that hold resources — cancellation will
# interrupt at any await, and finally runs even on cancellation.

print("\n=== Section 4: Timeouts and Cancellation ===")

async def slow_operation(label: str, duration: float) -> str:
    """Coroutine that may be cancelled."""
    try:
        print(f"  [{label}] starting (will take {duration:.1f}s)")
        await asyncio.sleep(duration)
        print(f"  [{label}] completed")
        return f"{label} result"
    except asyncio.CancelledError:
        print(f"  [{label}] was CANCELLED")
        raise   # always re-raise CancelledError — don't suppress it!
    finally:
        print(f"  [{label}] cleanup ran (finally always executes)")


async def timeout_demo():
    # wait_for: coroutine times out after 0.15s
    try:
        result = await asyncio.wait_for(
            slow_operation("timeout_test", duration=0.5),
            timeout=0.15,
        )
    except asyncio.TimeoutError:
        print("  Caught TimeoutError — slow_operation was cancelled")

    # Manual task cancellation
    task = asyncio.create_task(slow_operation("manual_cancel", duration=0.5))
    await asyncio.sleep(0.1)
    task.cancel()   # inject CancelledError at the next await in the task

    try:
        await task   # wait for cancellation to complete
    except asyncio.CancelledError:
        print("  Task was successfully cancelled")


asyncio.run(timeout_demo())


# =============================================================================
# SECTION 5: Async context managers and iterators
# =============================================================================

# CONCEPT: Many async libraries (aiohttp, asyncpg, aiofiles) use async context
# managers. `async with` calls __aenter__ and __aexit__ with await support.
# `async for` works with __aiter__ / __anext__ — lazy async streaming.

print("\n=== Section 5: Async Context Managers and Iterators ===")

class AsyncDBConnection:
    """
    Simulates an async database connection.
    async with connection ensures it's properly opened and closed.
    """

    def __init__(self, db_url: str):
        self.db_url   = db_url
        self._conn_id = None

    async def __aenter__(self):
        """Async enter: connects to DB (with await — could be a real network call)."""
        await asyncio.sleep(0.02)   # simulate handshake latency
        self._conn_id = random.randint(1000, 9999)
        print(f"  DB connected: {self.db_url} [conn_id={self._conn_id}]")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async exit: always closes connection, even if an exception occurred."""
        await asyncio.sleep(0.01)   # simulate graceful close
        print(f"  DB disconnected: [conn_id={self._conn_id}]")
        return False   # don't suppress exceptions

    async def query(self, sql: str) -> list:
        await asyncio.sleep(0.05)   # simulate query latency
        return [{"id": i, "sql": sql} for i in range(3)]


class AsyncRecordStream:
    """
    Async iterator that yields records one at a time.
    Models streaming a large result set without loading all into memory.
    """

    def __init__(self, total: int):
        self.total   = total
        self.current = 0

    def __aiter__(self):
        return self

    async def __anext__(self) -> dict:
        if self.current >= self.total:
            raise StopAsyncIteration   # signals async for to stop
        await asyncio.sleep(0.005)      # simulate fetching next row
        self.current += 1
        return {"row": self.current, "value": self.current ** 2}


async def async_patterns_demo():
    # Async context manager
    async with AsyncDBConnection("postgresql://localhost/mydb") as conn:
        rows = await conn.query("SELECT * FROM users LIMIT 3")
        print(f"  Query returned {len(rows)} rows")

    # Async generator / async for
    print("  Streaming records:")
    stream = AsyncRecordStream(total=4)
    async for record in stream:
        print(f"    row {record['row']}: {record['value']}")


asyncio.run(async_patterns_demo())


# =============================================================================
# SECTION 6: Running CPU-bound code from async — loop.run_in_executor
# =============================================================================

# CONCEPT: asyncio is single-threaded. A long CPU computation BLOCKS the event
# loop — no other coroutines can run while it's busy. Solution:
# loop.run_in_executor(None, fn, *args) — runs fn in a thread pool, returns
# an awaitable. The event loop is free while the thread runs.
# For true CPU parallelism, use ProcessPoolExecutor as the executor.

print("\n=== Section 6: CPU Work in Async Code ===")

def heavy_cpu_task(n: int) -> int:
    """Blocking CPU computation — must NOT be called with await directly."""
    return sum(i * i for i in range(n))


async def mixed_io_and_cpu():
    loop = asyncio.get_event_loop()

    # Schedule CPU work in thread pool — event loop stays responsive
    print("  Offloading CPU work to executor...")
    cpu_result = await loop.run_in_executor(
        None,                # None = default ThreadPoolExecutor
        heavy_cpu_task,
        500_000,
    )

    # These run concurrently with CPU work if started before awaiting
    io_result = await fetch_data("concurrent_io", 0.1)

    print(f"  CPU result: {cpu_result:,}")
    print(f"  I/O result: {io_result['source']}")


asyncio.run(mixed_io_and_cpu())


print("\n=== Async programming complete ===")
print("Mental model:")
print("  async def  → coroutine function (returns coroutine object when called)")
print("  await      → suspend current coroutine, event loop runs others")
print("  asyncio.run()  → create event loop, run one coroutine, tear down")
print("  asyncio.gather() → run multiple coroutines CONCURRENTLY")
print("  create_task()    → schedule now, run in background")
print("  wait_for()       → add timeout to any awaitable")
print("  run_in_executor()→ offload blocking code to thread pool")
