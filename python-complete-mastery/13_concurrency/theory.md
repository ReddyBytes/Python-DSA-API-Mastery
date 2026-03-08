# ⚙️ Concurrency — Theory

> *"Concurrency is about dealing with multiple things at once.*
> *Parallelism is about doing multiple things at once.*
> *Python supports both — but the GIL means you must choose the right tool."*

---

## 🎬 The Problem: 10 API Calls, 20 Seconds

Your service needs to fetch data from 10 external APIs to build a dashboard. Each call takes ~2 seconds.

**Sequential — the naive approach:**
```python
def build_dashboard(user_id):
    weather  = fetch_weather(user_id)    # 2s
    stocks   = fetch_stocks(user_id)     # 2s
    news     = fetch_news(user_id)       # 2s
    calendar = fetch_calendar(user_id)   # 2s
    ...   # 10 calls × 2s = 20 seconds!
    return compile(weather, stocks, news, calendar, ...)
```

The user waits 20 seconds staring at a spinner.

**Concurrent — the right approach:**
```python
import asyncio

async def build_dashboard(user_id):
    results = await asyncio.gather(
        fetch_weather(user_id),
        fetch_stocks(user_id),
        fetch_news(user_id),
        fetch_calendar(user_id),
        ...   # all 10 start simultaneously
    )
    return compile(*results)
# Total time: ~2 seconds (longest single call)
```

This is the core promise of concurrency: **overlap the waiting**.

---

## 🧠 Chapter 1: Concurrency vs Parallelism — The Critical Distinction

These terms are often confused. They are **not** the same:

```
CONCURRENCY: Multiple tasks making progress during overlapping time periods.
             Only ONE task runs at any given CPU cycle (on a single core).
             Tasks interleave by taking turns.

PARALLELISM: Multiple tasks executing at EXACTLY the same moment.
             Requires multiple CPU cores.
             True simultaneous execution.
```

**The chef analogy:**
```
CONCURRENCY (one chef):
  Put pasta on to boil (2 min)
  While it boils → chop vegetables (1 min)
  While it boils → heat sauce (1 min)
  Drain pasta
  → Total: 2 min  (not 2+1+1=4 min)
  One person, overlapping tasks

PARALLELISM (two chefs):
  Chef 1: makes pasta simultaneously as Chef 2 makes sauce
  → True simultaneous execution
  Two people, same moment
```

**In Python:**
```
CONCURRENCY via asyncio/threading → for I/O-bound tasks (network, disk, DB)
             Use when most time is spent WAITING, not computing

PARALLELISM via multiprocessing  → for CPU-bound tasks (math, ML, compression)
             Use when most time is spent COMPUTING
```

---

## 🔒 Chapter 2: The GIL — Python's Most Misunderstood Feature

**The GIL (Global Interpreter Lock)** is a mutex that allows only **one Python thread to execute Python bytecode at a time**, even on multi-core machines.

```
Without GIL:
  Core 1: Thread A executes Python
  Core 2: Thread B executes Python simultaneously
  → Both modifying same object → reference count corrupted → crash

With GIL:
  Core 1: Thread A holds GIL → executes Python
  Core 2: Thread B waiting for GIL → blocked
  → Only one thread runs Python code at a time → safe
```

**What the GIL affects:**
```
Python threads DO get speedup for:   I/O operations, C extensions (NumPy, OpenCV)
  → GIL is released during I/O waits and most C extension calls

Python threads DO NOT get speedup for: pure Python CPU work
  → Adding numbers, parsing strings, sorting lists in Python
  → Two threads share one core's Python execution
```

**The GIL in practice:**

```python
import threading, time

counter = 0

def increment(n):
    global counter
    for _ in range(n):
        counter += 1   # NOT thread-safe despite GIL!

# The GIL protects individual bytecodes but NOT compound operations
# counter += 1 compiles to: LOAD counter → ADD 1 → STORE counter
# Another thread can run between LOAD and STORE → race condition
```

**GIL is released during:**
- Any I/O operation (file read/write, network, pipe)
- `time.sleep()`
- Calls into C extensions that release it (NumPy operations, sqlite3, etc.)
- Every ~5ms (sys.getswitchinterval()) — forced context switch

---

## 🧵 Chapter 3: Threading — I/O-Bound Concurrency

Use threads when your bottleneck is **waiting** (network, disk, DB, external APIs).

### Basic Thread

```python
import threading

def download(url):
    response = requests.get(url)
    return response.content

# Manual thread:
t = threading.Thread(target=download, args=("http://example.com",), daemon=True)
t.start()
t.join()   # wait for completion
```

### ThreadPoolExecutor — The Modern Way

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

urls = ["http://api1.com", "http://api2.com", "http://api3.com"]

# Submit and wait for all:
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(download, url) for url in urls]
    results = [f.result() for f in futures]

# Process as they complete (not in submission order):
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(download, url): url for url in urls}
    for future in as_completed(futures):
        url = futures[future]
        try:
            data = future.result()
            print(f"{url}: {len(data)} bytes")
        except Exception as e:
            print(f"{url} failed: {e}")

# Executor.map — simple parallel map:
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(download, urls))
```

### Thread Lifecycle

```python
t = threading.Thread(target=func, args=(arg1,), kwargs={"key": val})
t.daemon = True    # daemon threads die when main thread exits (don't block shutdown)
t.start()          # schedule for execution
t.is_alive()       # True if running
t.join(timeout=5)  # wait up to 5 seconds
```

---

## ⚠️ Chapter 4: Race Conditions — When Threads Collide

A race condition occurs when the outcome depends on the unpredictable order of thread execution:

```python
import threading

balance = 1000

def withdraw(amount):
    global balance
    if balance >= amount:    # thread A checks: 1000 >= 500 → True
                             # thread B checks: 1000 >= 700 → True
        balance -= amount    # thread A: 1000 - 500 = 500
                             # thread B: 1000 - 700 = 300  ← WRONG! should be 500-700 → error

threads = [
    threading.Thread(target=withdraw, args=(500,)),
    threading.Thread(target=withdraw, args=(700,)),
]
for t in threads: t.start()
for t in threads: t.join()

print(balance)   # could be 500, 300, or -200 depending on timing
```

**The compound operation problem:**
```
counter += 1  compiles to:
  LOAD_GLOBAL counter   ← Thread A loaded 0
                        ← CONTEXT SWITCH: Thread B runs
                        ← Thread B: LOAD=0, ADD=1, STORE → counter=1
                        ← CONTEXT SWITCH back to Thread A
  BINARY_ADD 1          ← Thread A: ADD 0+1 = 1
  STORE_GLOBAL counter  ← Thread A: STORE 1  ← lost Thread B's increment!
```

---

## 🔐 Chapter 5: Thread Synchronization

### Lock — Mutual Exclusion

```python
import threading

lock = threading.Lock()
balance = 1000

def withdraw(amount):
    global balance
    with lock:                   # acquire → only one thread at a time
        if balance >= amount:
            balance -= amount
        else:
            raise ValueError("Insufficient funds")
    # lock released here, even if exception

# Lock methods:
lock.acquire()         # blocks until lock is available
lock.acquire(timeout=5)  # blocks for at most 5 seconds; returns False if timeout
lock.release()
lock.locked()          # True if currently held

# Always use with statement — guarantees release on exception
```

### RLock — Re-Entrant Lock

```python
# Regular Lock deadlocks if the same thread tries to acquire it twice:
lock = threading.Lock()
with lock:
    with lock:   # DEADLOCK — thread blocks waiting for itself!
        ...

# RLock allows the same thread to acquire multiple times:
rlock = threading.RLock()
with rlock:
    with rlock:   # ← works! same thread can re-enter
        ...
# Must be released same number of times it was acquired
```

### Semaphore — Rate Limiting / Pool

```python
# Limit concurrent access to N at a time:
db_pool = threading.Semaphore(5)   # max 5 concurrent DB connections

def query_database(sql):
    with db_pool:           # blocks if 5 connections already active
        conn = db.connect()
        result = conn.execute(sql).fetchall()
        conn.close()
        return result

# BoundedSemaphore raises ValueError if released more than acquired:
sem = threading.BoundedSemaphore(3)
```

### Event — Signal Between Threads

```python
ready = threading.Event()

def producer():
    time.sleep(2)
    data = load_data()
    ready.set()   # signal that data is ready

def consumer():
    ready.wait()       # blocks until ready.set() is called
    ready.wait(timeout=10)  # blocks up to 10 seconds
    process(data)

# Event methods:
event.set()       # signal (unblock all waiting threads)
event.clear()     # reset
event.is_set()    # check
event.wait(timeout)  # block until set
```

### Condition — Notify Specific Waiters

```python
condition = threading.Condition()
queue = []

def producer():
    with condition:
        queue.append(item)
        condition.notify()      # wake one waiting thread
        # condition.notify_all()  # wake all waiting threads

def consumer():
    with condition:
        while not queue:
            condition.wait()    # release lock and block; re-acquire on notify
        item = queue.pop(0)

# Use Condition when: you need to wait for a state change, not just lock access
```

### Barrier — Synchronize N Threads at a Point

```python
# All threads wait until N have reached the barrier:
barrier = threading.Barrier(parties=5)

def worker(n):
    prepare_phase(n)
    barrier.wait()   # blocks until all 5 threads reach this point
    execute_phase(n)  # all 5 start execute_phase at approximately the same time
```

---

## 📬 Chapter 6: Thread-Safe Communication — `queue.Queue`

`queue.Queue` is the correct way to communicate between threads — no manual locks needed:

```python
import queue, threading

task_queue   = queue.Queue(maxsize=100)   # bounded — blocks producer if full
result_queue = queue.Queue()

def producer():
    for item in data_source():
        task_queue.put(item)         # blocks if queue full (maxsize reached)
    task_queue.put(None)             # sentinel value to stop workers

def worker():
    while True:
        item = task_queue.get()      # blocks until item available
        if item is None:
            task_queue.put(None)     # pass sentinel to next worker
            break
        result = process(item)
        result_queue.put(result)
        task_queue.task_done()       # signal item processed

# Wait for all items to be processed:
task_queue.join()   # blocks until every task_done() is called

# Queue variants:
queue.Queue()           # FIFO
queue.LifoQueue()       # LIFO (stack)
queue.PriorityQueue()   # min-heap (tuple: (priority, item))
```

---

## 🔥 Chapter 7: Multiprocessing — CPU-Bound Parallelism

When you need **true parallelism** (bypasses the GIL completely — each process has its own GIL):

```python
from multiprocessing import Process, Pool, cpu_count
import os

def compute_chunk(data):
    """CPU-heavy work that benefits from true parallelism."""
    return sum(x**2 for x in data)

# Basic Process:
p = Process(target=compute_chunk, args=(data,))
p.start()
p.join()

# ProcessPoolExecutor — modern preferred way:
from concurrent.futures import ProcessPoolExecutor

chunks = split_data(data, n=cpu_count())
with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    results = list(executor.map(compute_chunk, chunks))
total = sum(results)

# Pool.map — classic way:
with Pool(processes=cpu_count()) as pool:
    results = pool.map(compute_chunk, chunks)
```

### Process vs Thread

```
FEATURE              Thread              Process
─────────────────────────────────────────────────────────────────────
Memory               Shared              Separate (fork/spawn)
GIL                  Constrained         Bypassed (each has own)
Communication        Queue, shared vars  Queue, Pipe, Manager
Overhead             Low (~ms)           High (~50-100ms to start)
Crash isolation      No (kills all)      Yes (crash stays in process)
Best for             I/O-bound           CPU-bound
```

### Sharing Data Between Processes

```python
from multiprocessing import Value, Array, Manager

# Shared memory (fast, limited types):
counter  = Value('i', 0)    # 'i' = C int
buffer   = Array('d', 100)  # 'd' = C double, 100 elements

with counter.get_lock():    # must lock manually!
    counter.value += 1

# Manager (flexible, slower — uses network protocol internally):
with Manager() as manager:
    shared_dict  = manager.dict()
    shared_list  = manager.list()
    shared_lock  = manager.Lock()
    # Changes propagate across processes automatically

# Queue for inter-process communication:
from multiprocessing import Queue as MPQueue
q = MPQueue()
q.put(item)    # sends to queue (serializes with pickle)
q.get()        # receives from queue
```

---

## ⚡ Chapter 8: asyncio — Cooperative Concurrency

**asyncio** is the third model: single-threaded, event-driven, cooperative multitasking. No threads, no processes — just one thread that switches between tasks when they `await`.

### Core Concepts

```python
import asyncio

# coroutine: an async function (doesn't run immediately when called)
async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# calling fetch(url) returns a coroutine OBJECT, not the result:
coro = fetch("http://api.com/data")   # nothing runs yet

# run the coroutine:
result = asyncio.run(fetch("http://api.com/data"))

# create a Task (schedules coroutine on event loop):
task = asyncio.create_task(fetch("http://api.com/data"))
result = await task
```

### The Event Loop

```
EVENT LOOP (single thread, runs forever):

  1. Pop next ready task from ready queue
  2. Run it until it hits 'await'
  3. Task is suspended (added to waiting set)
  4. Pop next ready task...
  5. When awaited I/O completes: move task back to ready queue
  6. Repeat

No thread switching — pure cooperative multitasking.
Tasks only pause at 'await' points.
If a task never awaits → it blocks everything else!
```

### Running Multiple Coroutines Concurrently

```python
import asyncio, aiohttp

# gather: run all concurrently, wait for all:
async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in urls]
        results = await asyncio.gather(*tasks)   # all start immediately
        return results

# gather with error handling:
results = await asyncio.gather(*tasks, return_exceptions=True)
for r in results:
    if isinstance(r, Exception):
        logger.error("Task failed: %s", r)
    else:
        process(r)

# create_task: start a coroutine in the background:
async def main():
    task1 = asyncio.create_task(long_operation_1())   # starts immediately
    task2 = asyncio.create_task(long_operation_2())   # starts immediately
    # ... do other work while tasks run ...
    r1 = await task1
    r2 = await task2

# wait: more control over completion:
done, pending = await asyncio.wait(tasks, timeout=5.0)
for task in pending:
    task.cancel()   # cancel tasks that didn't finish in time
```

### asyncio Synchronization

```python
# asyncio has its own sync primitives (non-blocking):
lock      = asyncio.Lock()
event     = asyncio.Event()
semaphore = asyncio.Semaphore(10)
queue     = asyncio.Queue(maxsize=100)

# Lock (same semantics as threading.Lock):
async with lock:
    await critical_section()

# Semaphore (rate limiting):
async with semaphore:   # max 10 concurrent
    await fetch(url)

# Queue (producer/consumer):
await queue.put(item)
item = await queue.get()
queue.task_done()
await queue.join()

# Event:
await event.wait()   # non-blocking wait — yields to event loop
event.set()
```

---

## 🔧 Chapter 9: `concurrent.futures` — Unified Interface

`concurrent.futures` provides a single API for both threads and processes:

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed, wait

# Both executors have identical interface:
def process(item):
    return item * 2

# Thread pool (I/O-bound):
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(process, i) for i in range(100)]
    for f in as_completed(futures):
        result = f.result()   # raises exception if task failed

# Process pool (CPU-bound):
with ProcessPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(process, range(100)))

# Future methods:
f = executor.submit(func, arg)
f.result(timeout=5)    # block and return result; raises exception if failed
f.exception()          # return exception if failed, None if succeeded
f.done()               # True if completed (success or failure)
f.cancel()             # cancel if not yet running
f.add_done_callback(fn)  # callback when future completes

# Wait for subset:
done, not_done = wait(futures, timeout=10, return_when=FIRST_COMPLETED)
```

---

## 🗺️ Chapter 10: Choosing the Right Model

```
DECISION MATRIX:
──────────────────────────────────────────────────────────────────────
Task type         Bottleneck    Use                      Why
──────────────────────────────────────────────────────────────────────
HTTP requests     Network I/O   asyncio + aiohttp        Single thread,
API calls                       OR ThreadPoolExecutor    max throughput

File read/write   Disk I/O      asyncio (aiofiles)       Non-blocking I/O
                                OR ThreadPoolExecutor

Database queries  Network+lock  asyncio (asyncpg/aiosqlite)
                                OR ThreadPoolExecutor

CPU math          Computation   ProcessPoolExecutor      Bypasses GIL
                                OR multiprocessing.Pool

Machine learning  GPU/CPU       ProcessPoolExecutor      Parallel workers
data pipelines                  + joblib

Web server        Mixed         asyncio (FastAPI/Sanic)  Best concurrency
                                OR threads (Django)      for HTTP

Background jobs   Mixed         Celery + Redis/RabbitMQ  Distributed tasks
──────────────────────────────────────────────────────────────────────

QUICK RULE:
  Waiting for I/O → asyncio or threads
  Number crunching → multiprocessing
  Simple scripts  → concurrent.futures (auto-selects)
```

---

## 🔄 Chapter 11: Producer-Consumer Pattern

The most common concurrency pattern — one or more producers feed work to one or more consumers:

```python
import threading, queue, time

task_queue = queue.Queue(maxsize=50)

def producer(items):
    for item in items:
        task_queue.put(item)            # blocks if queue full
    for _ in range(NUM_WORKERS):
        task_queue.put(None)            # sentinel: one per worker

def worker():
    while True:
        item = task_queue.get()         # blocks until item available
        if item is None:
            break
        try:
            result = process(item)
            output_queue.put(result)
        except Exception as e:
            logger.error("Worker failed on %s: %s", item, e)
        finally:
            task_queue.task_done()

NUM_WORKERS = 5
threads = [threading.Thread(target=worker) for _ in range(NUM_WORKERS)]
for t in threads:
    t.daemon = True
    t.start()

producer(my_items)
task_queue.join()   # wait for all tasks to complete
```

---

## 🐛 Chapter 12: Deadlock — When Threads Block Forever

A deadlock occurs when Thread A waits for Lock B (held by Thread B), and Thread B waits for Lock A (held by Thread A):

```python
lock_a = threading.Lock()
lock_b = threading.Lock()

def thread_1():
    with lock_a:
        time.sleep(0.1)    # gives thread_2 time to acquire lock_b
        with lock_b:       # ← DEADLOCK: waiting for lock_b held by thread_2
            print("Thread 1 done")

def thread_2():
    with lock_b:
        time.sleep(0.1)
        with lock_a:       # ← DEADLOCK: waiting for lock_a held by thread_1
            print("Thread 2 done")
```

**Prevention strategies:**
```python
# 1. Consistent lock ordering — ALWAYS acquire in same order:
def thread_1():
    with lock_a:   # always A before B
        with lock_b:
            ...

def thread_2():
    with lock_a:   # always A before B
        with lock_b:
            ...

# 2. Lock timeout:
acquired = lock.acquire(timeout=5)
if not acquired:
    raise TimeoutError("Could not acquire lock")

# 3. Try-lock (non-blocking):
if lock.acquire(blocking=False):
    try:
        ...
    finally:
        lock.release()
else:
    # couldn't acquire — back off
```

---

## ⚠️ Chapter 13: Common Gotchas

### Gotcha 1 — CPU-bound threads don't speed up

```python
# ❌ WRONG: threading for CPU work:
def compute_pi(n):
    return sum((-1)**k / (2*k+1) for k in range(n))

threads = [Thread(target=compute_pi, args=(1_000_000,)) for _ in range(4)]
# GIL prevents true parallelism — 4 threads, still one core's speed

# ✅ CORRECT: multiprocessing for CPU work:
with ProcessPoolExecutor() as executor:
    results = list(executor.map(compute_pi, [1_000_000]*4))
```

### Gotcha 2 — Mutable default arguments in threaded code

```python
# ❌ results accumulates across ALL calls:
def worker(items, results=[]):
    results.append(process(items))
    return results
```

### Gotcha 3 — Starting event loop from inside event loop

```python
# ❌ RuntimeError: This event loop is already running
async def outer():
    asyncio.run(inner())   # can't nest event loops!

# ✅ Use await or create_task instead:
async def outer():
    await inner()
    # or:
    task = asyncio.create_task(inner())
```

### Gotcha 4 — Blocking call in async code

```python
# ❌ Blocks the ENTIRE event loop for 2 seconds:
async def bad():
    time.sleep(2)          # ← synchronous sleep blocks everything!
    data = open("huge.txt").read()  # ← synchronous I/O blocks everything!

# ✅ Use async equivalents:
async def good():
    await asyncio.sleep(2)  # yields to event loop
    async with aiofiles.open("huge.txt") as f:
        data = await f.read()

# ✅ Run blocking code in thread pool:
async def also_good():
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, blocking_read, "huge.txt")
```

### Gotcha 5 — Thread-local state vs shared state

```python
# Shared state — all threads see it:
shared_counter = 0   # ← race condition

# Thread-local state — each thread has its own:
local = threading.local()

def worker():
    local.counter = 0   # each thread has its own .counter
    local.counter += 1
    print(local.counter)   # always 1, never races
```

---

## 🔥 Summary

```
MODEL          BEST FOR          GIL         OVERHEAD    COMMUNICATION
────────────────────────────────────────────────────────────────────────
threading      I/O-bound         Constrained Low         Queue, Lock
multiprocessing CPU-bound         Bypassed    High        Queue, Pipe, Manager
asyncio        I/O-bound (many)  Irrelevant  Lowest      asyncio.Queue

SYNC PRIMITIVES:
  Lock         — mutual exclusion (one at a time)
  RLock        — re-entrant lock (same thread can re-acquire)
  Semaphore    — N at a time (rate limiting)
  Event        — signal/wait
  Condition    — wait for state change
  Barrier      — N threads sync at point
  Queue        — thread-safe message passing

PATTERNS:
  ThreadPoolExecutor   — manage pool of threads automatically
  ProcessPoolExecutor  — manage pool of processes automatically
  asyncio.gather       — run N coroutines concurrently, wait for all
  asyncio.create_task  — fire-and-forget background task
  queue.Queue          — producer/consumer between threads
```

---

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🔧 Async Guide | [async_guide.md](./async_guide.md) |
| ➡️ Next | [15 — Advanced Python](../15_advanced_python/theory.md) |
