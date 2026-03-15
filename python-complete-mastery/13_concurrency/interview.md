# 🎯 Concurrency — Interview Questions

> *"Concurrency questions reveal whether you understand Python's execution model,*
> *can design thread-safe systems, and know when to use which tool."*

---

## 📊 Question Map

```
LEVEL 1 — Junior (0–2 years)
  • Concurrency vs Parallelism
  • What is the GIL?
  • When to use threads vs multiprocessing vs asyncio
  • What is a race condition?

LEVEL 2 — Mid-Level (2–5 years)
  • Thread synchronization primitives
  • ThreadPoolExecutor / ProcessPoolExecutor
  • asyncio event loop and await
  • Deadlock — causes and prevention
  • queue.Queue for thread communication

LEVEL 3 — Senior (5+ years)
  • GIL internals and release conditions
  • Designing producer/consumer systems
  • asyncio vs threading for I/O — when each wins
  • Shared memory in multiprocessing
  • Diagnosing and fixing race conditions
```

---

## 🟢 Level 1 — Junior Questions

---

### Q1: What is the difference between concurrency and parallelism?

**Weak answer:** "They're basically the same — running things at the same time."

**Strong answer:**

> **Concurrency** means multiple tasks make progress during overlapping time periods. Only one runs at a given instant on a single CPU — tasks interleave by taking turns.
>
> **Parallelism** means multiple tasks execute at the exact same moment, requiring multiple CPU cores.

```
CONCURRENCY (single core):
  Task A: ████░░░░████░░░░████
  Task B: ░░░░████░░░░████░░░░
  Time:   ──────────────────→
  Tasks interleave. Total wall time < sum of task times.

PARALLELISM (multi-core):
  Core 1: Task A: ████████████
  Core 2: Task B: ████████████
  Time:   ──────────────────→
  True simultaneous execution.
```

> Python's `threading` is concurrent (GIL allows only one at a time). Python's `multiprocessing` is parallel (separate GILs, truly simultaneous).

---

### Q2: What is the GIL and why does it exist?

**Weak answer:** "It prevents multiple threads from running Python at the same time."

**Strong answer:**

> The **Global Interpreter Lock (GIL)** is a mutex in CPython that ensures only one thread executes Python bytecode at a time, even on multi-core machines.
>
> **Why it exists:** CPython's memory management (reference counting) is not thread-safe. Without the GIL, two threads could simultaneously modify an object's reference count, corrupting memory and causing crashes. The GIL was the simplest solution.
>
> **What it means in practice:**

```python
# ❌ Threading does NOT parallelize pure Python CPU work:
def cpu_work(n):
    return sum(i**2 for i in range(n))

# Running 4 threads → still ~1x speed (GIL serializes execution)

# ✅ Threading DOES help with I/O-bound work:
def api_call(url):
    return requests.get(url).json()

# Running 10 threads → ~10x speed (GIL released during network wait)

# ✅ Multiprocessing bypasses GIL entirely:
# Each process has its own GIL — true parallel execution
```

> **GIL is released during:** I/O operations, `time.sleep()`, most NumPy/C extension calls.

---

### Q3: When would you use threading vs multiprocessing vs asyncio?

**Strong answer:**

```
I/O-bound (waiting for network, disk, DB):
  asyncio   → best for very high concurrency (1000s of connections)
  threading → simpler, works well for moderate concurrency

CPU-bound (computing, parsing, math):
  multiprocessing → only option that gives true speedup
  (threading is not faster for CPU work due to GIL)

Rule of thumb:
  Waiting for external systems → asyncio or threads
  Number crunching            → multiprocessing
```

```python
# asyncio: 1000 HTTP requests concurrently:
async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# multiprocessing: compress 8 large files in parallel:
with ProcessPoolExecutor(max_workers=8) as exc:
    list(exc.map(compress_file, file_paths))
```

---

### Q4: What is a race condition? Give an example.

**Strong answer:**

> A race condition is when the correctness of a program depends on the relative timing of operations in multiple threads — and that timing is unpredictable.

```python
import threading

balance = 1000

def withdraw(amount):
    global balance
    # NOT ATOMIC: read + check + write can be interrupted between steps
    if balance >= amount:
        balance -= amount   # another thread may modify balance between check and write

t1 = threading.Thread(target=withdraw, args=(800,))
t2 = threading.Thread(target=withdraw, args=(800,))
t1.start(); t2.start()
t1.join();  t2.join()

# If both threads pass the 'if' check before either withdraws:
# Final balance could be 1000 - 800 - 800 = -600  ← impossible without race

# Fix: use a lock
lock = threading.Lock()
def safe_withdraw(amount):
    with lock:
        if balance >= amount:
            balance -= amount
```

---

## 🔵 Level 2 — Mid-Level Questions

---

### Q5: What synchronization primitives does Python provide and when do you use each?

**Strong answer:**

```python
import threading

# Lock — mutual exclusion (one thread at a time):
lock = threading.Lock()
with lock:
    shared_data.modify()

# RLock — re-entrant (same thread can acquire multiple times):
rlock = threading.RLock()
with rlock:
    with rlock:   # doesn't deadlock — same thread

# Semaphore — limit N concurrent accesses:
db_sem = threading.Semaphore(5)   # max 5 concurrent DB queries
with db_sem:
    result = db.query(sql)

# Event — signal between threads:
data_ready = threading.Event()
data_ready.set()      # signal
data_ready.wait()     # block until signalled

# Queue — thread-safe producer/consumer (most common):
q = queue.Queue()
q.put(item)           # blocks if maxsize reached
item = q.get()        # blocks until item available
q.task_done()
q.join()              # wait for all task_done() calls
```

---

### Q6: How does `ThreadPoolExecutor` work and what are its advantages?

**Strong answer:**

> `ThreadPoolExecutor` maintains a pool of reusable worker threads, avoiding the overhead of creating/destroying threads for each task. It provides a clean `Future`-based API:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

urls = [f"http://api.com/{i}" for i in range(50)]

# Submit tasks, get results in completion order:
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(fetch, url): url for url in urls}

    for future in as_completed(futures):
        url = futures[future]
        try:
            data = future.result()
            process(data)
        except Exception as e:
            logger.error("%s failed: %s", url, e)

# Or with map (preserves order, raises on first failure):
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(fetch, urls, timeout=30))
```

> **Advantages vs manual threads:** automatic pool management, `Future` API with exception propagation, works as context manager, `as_completed` for processing in completion order.

---

### Q7: Explain the asyncio event loop and what `await` does.

**Weak answer:** "asyncio runs async functions. await pauses them."

**Strong answer:**

> The **event loop** is a single-threaded scheduler that runs coroutines cooperatively. It maintains a queue of ready tasks and runs them one at a time. When a task hits `await`, it **voluntarily yields** control back to the event loop, which then runs other ready tasks.

```python
import asyncio

async def fetch(url):
    # 'await' means: "I'm waiting for I/O — run other tasks until it's ready"
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as resp:
            return await resp.json()   # yields here → event loop runs other tasks

async def main():
    # gather schedules all 3 coroutines as tasks — they run concurrently:
    results = await asyncio.gather(
        fetch("http://api1.com"),   # starts, immediately hits await
        fetch("http://api2.com"),   # starts, immediately hits await
        fetch("http://api3.com"),   # starts, immediately hits await
    )
    # All three I/O requests are in-flight simultaneously
    # Event loop processes responses as they arrive
```

> **Key:** `await` only suspends the current coroutine, not the whole thread. Other coroutines continue running.

---

### Q8: What is a deadlock and how do you prevent it?

**Strong answer:**

> A deadlock occurs when Thread A holds Lock 1 and waits for Lock 2, while Thread B holds Lock 2 and waits for Lock 1. Both block forever.

```python
lock_a = threading.Lock()
lock_b = threading.Lock()

def thread1():
    with lock_a:
        time.sleep(0.01)
        with lock_b:   # ← waiting for lock_b held by thread2 → DEADLOCK
            pass

def thread2():
    with lock_b:
        time.sleep(0.01)
        with lock_a:   # ← waiting for lock_a held by thread1 → DEADLOCK
            pass
```

> **Prevention strategies:**
> 1. **Lock ordering**: always acquire locks in the same global order
> 2. **Lock timeout**: `lock.acquire(timeout=5)` — give up if can't acquire
> 3. **Minimize lock scope**: hold locks for as short a time as possible
> 4. **Use higher-level primitives**: `queue.Queue` often eliminates need for manual locks

```python
# Fix 1: consistent ordering (both acquire A before B):
def thread1():
    with lock_a:
        with lock_b:
            pass

def thread2():
    with lock_a:   # same order
        with lock_b:
            pass
```

---

## 🔴 Level 3 — Senior Questions

---

### Q9: When does the GIL get released? How does this affect your threading strategy?

**Strong answer:**

> The GIL is released in three scenarios:

```python
# 1. I/O operations (file, network, socket, pipe):
with open("file.txt") as f:
    data = f.read()   # GIL released during the actual read syscall

# 2. time.sleep():
time.sleep(1)   # GIL released for the full second — other threads run

# 3. C extensions that explicitly release it:
import numpy as np
np.dot(a, b)   # NumPy releases GIL → true parallel execution with threads!

# 4. Periodic forced switch (~5ms):
# Even without explicit release, Python forces a context switch
# every sys.getswitchinterval() seconds (default 0.005)

# Strategic implications:
# If your "CPU work" is mostly NumPy/Pandas → threading works fine
# If your "CPU work" is pure Python loops → need multiprocessing
# If your work is mixed → profile first, then decide
```

---

### Q10: How do you share data between processes safely?

**Strong answer:**

> Processes have separate memory spaces — sharing requires explicit IPC mechanisms:

```python
from multiprocessing import Queue, Pipe, Value, Array, Manager

# 1. Queue — safe, general-purpose:
q = multiprocessing.Queue()
p = Process(target=worker, args=(q,))
p.start()
q.put("message")           # serialized via pickle
result = q.get()

# 2. Pipe — faster, two-process point-to-point:
parent_conn, child_conn = Pipe()
p = Process(target=worker, args=(child_conn,))
parent_conn.send("data")
result = parent_conn.recv()

# 3. Shared memory (fast, C types only):
counter = Value('i', 0)     # 'i'=int, 'd'=double, 'c'=char
with counter.get_lock():
    counter.value += 1

arr = Array('d', [1.0, 2.0, 3.0])

# 4. Manager (flexible, any Python type, slower):
with Manager() as manager:
    shared_dict = manager.dict()
    shared_list = manager.list()
    p = Process(target=worker, args=(shared_dict,))
    p.start()
    p.join()
    print(shared_dict)   # sees changes made by child process
```

---

### Q11: Design a concurrent web scraper with rate limiting.

**Strong answer:**

```python
import asyncio, aiohttp, time
from collections import deque

class RateLimiter:
    def __init__(self, calls_per_second: int):
        self.rate   = calls_per_second
        self.times  = deque()
        self._lock  = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            # Remove calls older than 1 second
            while self.times and now - self.times[0] > 1.0:
                self.times.popleft()
            if len(self.times) >= self.rate:
                wait_time = 1.0 - (now - self.times[0])
                await asyncio.sleep(wait_time)
            self.times.append(time.monotonic())

async def scrape_url(session, url, limiter, semaphore):
    await limiter.acquire()
    async with semaphore:   # also limit concurrent connections
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                return {"url": url, "status": r.status, "body": await r.text()}
        except Exception as e:
            return {"url": url, "error": str(e)}

async def scrape_all(urls, max_rps=10, max_concurrent=20):
    limiter   = RateLimiter(max_rps)
    semaphore = asyncio.Semaphore(max_concurrent)

    async with aiohttp.ClientSession() as session:
        tasks = [scrape_url(session, url, limiter, semaphore) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

results = asyncio.run(scrape_all(urls, max_rps=10))
```

---

### Q12: What is `asyncio.run_in_executor` and when do you need it?

**Strong answer:**

> Any blocking (synchronous) call inside an async function freezes the entire event loop. `run_in_executor` offloads blocking work to a thread pool, keeping the event loop responsive:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

thread_pool = ThreadPoolExecutor(max_workers=10)

async def process_image(image_bytes):
    loop = asyncio.get_event_loop()

    # ❌ Blocks event loop for the duration of compression:
    # compressed = compress(image_bytes)

    # ✅ Runs compression in a thread, event loop stays responsive:
    compressed = await loop.run_in_executor(
        thread_pool,
        compress,          # blocking function
        image_bytes        # arguments
    )
    return compressed

# asyncio.to_thread (Python 3.9+) — cleaner syntax:
async def process_image(image_bytes):
    compressed = await asyncio.to_thread(compress, image_bytes)
    return compressed
```

> **Use for:** legacy blocking I/O, CPU-bound operations in async code, calling synchronous libraries (PIL, pandas) from async functions.

---

## ⚠️ Trap Questions

---

### Trap 1 — Using threading for CPU work expecting speedup

```python
# ❌ Will be as slow as sequential (GIL serializes Python execution):
threads = [Thread(target=compute, args=(chunk,)) for chunk in chunks]
for t in threads: t.start()
for t in threads: t.join()

# ✅ For CPU work, use processes:
with ProcessPoolExecutor(max_workers=cpu_count()) as exc:
    results = list(exc.map(compute, chunks))
```

---

### Trap 2 — Blocking call inside async function

```python
# ❌ Freezes entire event loop for 5 seconds:
async def handler():
    time.sleep(5)          # synchronous! blocks everything
    data = requests.get(url).json()  # synchronous! blocks everything

# ✅ Use async equivalents:
async def handler():
    await asyncio.sleep(5)
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            data = await r.json()
```

---

### Trap 3 — Forgetting that `counter += 1` is not atomic

```python
counter = 0

def increment():
    global counter
    for _ in range(100_000):
        counter += 1   # NOT atomic — read + add + write can be interrupted

threads = [Thread(target=increment) for _ in range(10)]
# Expected: 1,000,000 — Actual: somewhere between 100,000 and 1,000,000

# Fix:
lock = threading.Lock()
def safe_increment():
    global counter
    with lock:
        counter += 1

# Or use: collections.Counter is thread-safe for some operations
# Or use: queue.Queue to accumulate and sum later
```

---

### Trap 4 — asyncio.run() inside an existing event loop

```python
# ❌ RuntimeError: this event loop is already running
async def outer():
    asyncio.run(inner())   # can't create nested event loop

# ✅ Use await:
async def outer():
    await inner()

# ✅ Or create task:
async def outer():
    task = asyncio.create_task(inner())
    await task
```

---

## 🔥 Rapid-Fire Revision

```
Q: GIL: what is it?
A: CPython mutex allowing only one thread to run Python bytecode at a time.
   Released during I/O, sleep, and most C extensions.

Q: Threading for CPU-bound → speedup?
A: No. GIL prevents true parallelism for pure Python code.
   Use multiprocessing for CPU-bound work.

Q: asyncio is multi-threaded?
A: No. Single-threaded, cooperative multitasking.
   Tasks yield at 'await' points.

Q: Difference between Lock and RLock?
A: Lock: one acquire per thread. RLock: same thread can acquire multiple times.

Q: What does queue.Queue.join() do?
A: Blocks until every item has had task_done() called.

Q: gather vs create_task?
A: gather: run N coroutines, wait for all, return list of results.
   create_task: schedule one coroutine, returns a Task you await later.

Q: run_in_executor / asyncio.to_thread use?
A: Run blocking (synchronous) code without freezing the event loop.

Q: How to detect deadlock?
A: Program hangs indefinitely. Use threading module's deadlock detection
   or add lock acquire timeouts.

Q: ProcessPoolExecutor vs Pool?
A: Both work. ProcessPoolExecutor has Future API, works as context manager.
   Pool.map/starmap/apply_async — older API, slightly more options.

Q: Default max_workers for ThreadPoolExecutor?
A: min(32, os.cpu_count() + 4) — Python 3.8+
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🧵 Threading Guide | [threading_guide.md](./threading_guide.md) |
| 🔥 Multiprocessing Guide | [multiprocessing_guide.md](./multiprocessing_guide.md) |
| ⚡ Async Guide | [async_guide.md](./async_guide.md) |
| ➡️ Next | [15 — Advanced Python](../15_advanced_python/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Multiprocessing Guide](./multiprocessing_guide.md) &nbsp;|&nbsp; **Next:** [Type Hints And Pydantic — Theory →](../14_type_hints_and_pydantic/theory.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Async Guide](./async_guide.md) · [Threading Guide](./threading_guide.md) · [Multiprocessing Guide](./multiprocessing_guide.md)
