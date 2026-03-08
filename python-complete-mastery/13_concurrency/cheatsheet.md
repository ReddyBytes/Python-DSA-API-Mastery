# ⚡ Concurrency — Cheatsheet

> Quick reference: threading, multiprocessing, asyncio, sync primitives, patterns, gotchas.

---

## 🗺️ Decision Matrix

```
TASK TYPE         BOTTLENECK     USE
──────────────────────────────────────────────────────────
HTTP / API calls  Network I/O    asyncio + aiohttp
DB queries        Network I/O    asyncio or ThreadPoolExecutor
File I/O          Disk I/O       asyncio (aiofiles) or threads
CPU math          Computation    ProcessPoolExecutor
Data pipelines    CPU            multiprocessing.Pool
Web server        Mixed          asyncio (FastAPI) or threads (Django)

QUICK RULE:
  Waiting → asyncio or threading
  Computing → multiprocessing
```

---

## 🧵 Threading

```python
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Basic thread:
t = threading.Thread(target=func, args=(a,), kwargs={"k": v})
t.daemon = True    # dies with main thread
t.start()
t.join(timeout=5)  # wait up to 5s
t.is_alive()

# ThreadPoolExecutor (preferred):
with ThreadPoolExecutor(max_workers=10) as executor:
    # Map (blocking, preserves order):
    results = list(executor.map(func, items))

    # Submit (non-blocking, returns Future):
    futures = [executor.submit(func, item) for item in items]

    # Process in completion order:
    for f in as_completed(futures):
        result = f.result()   # raises if task failed

# Thread-local storage (each thread has own copy):
local = threading.local()
local.value = 42   # only visible to this thread
```

---

## 🔐 Synchronization Primitives

```python
import threading, queue

# Lock — mutual exclusion:
lock = threading.Lock()
with lock:
    modify_shared()
lock.acquire(timeout=5)   # returns False on timeout
lock.release()

# RLock — re-entrant (same thread can acquire multiple times):
rlock = threading.RLock()

# Semaphore — N concurrent:
sem = threading.Semaphore(5)   # max 5 at a time
with sem:
    use_resource()

# Event — signal:
event = threading.Event()
event.set()           # signal all waiters
event.wait(timeout=5) # block until set
event.clear()         # reset
event.is_set()

# Queue — thread-safe producer/consumer:
q = queue.Queue(maxsize=100)
q.put(item)           # blocks if full
q.get()               # blocks if empty
q.task_done()         # signal item processed
q.join()              # wait for all task_done()

queue.Queue()         # FIFO
queue.LifoQueue()     # LIFO
queue.PriorityQueue() # min-heap (priority, item)
```

---

## 🔥 Multiprocessing

```python
from multiprocessing import Process, Pool, Value, Array, Queue as MPQ
from concurrent.futures import ProcessPoolExecutor
import os

# ProcessPoolExecutor (preferred):
with ProcessPoolExecutor(max_workers=os.cpu_count()) as exc:
    results = list(exc.map(cpu_func, chunks))
    futures = [exc.submit(cpu_func, chunk) for chunk in chunks]

# Pool (classic):
with Pool(processes=os.cpu_count()) as pool:
    results = pool.map(func, items)       # blocking
    result  = pool.apply_async(func, (a,)) # non-blocking Future-like

# Basic Process:
p = Process(target=func, args=(arg,))
p.start()
p.join()
p.terminate()   # send SIGTERM
p.kill()        # send SIGKILL

# Shared memory (fast, C types):
counter = Value('i', 0)     # i=int, d=double, c=char
with counter.get_lock():
    counter.value += 1
arr = Array('d', 10)        # 10 doubles

# Manager (any type, slower):
from multiprocessing import Manager
with Manager() as m:
    d = m.dict()
    l = m.list()

# Inter-process queue:
q = MPQ()   # pickle-based
q.put(item)
item = q.get()

# Pipe (two-process point-to-point):
from multiprocessing import Pipe
parent, child = Pipe()
parent.send("hello"); child.recv()
```

---

## ⚡ asyncio

```python
import asyncio, aiohttp

# Define coroutine:
async def fetch(url):
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            return await r.json()

# Run top-level:
result = asyncio.run(fetch(url))

# Concurrent execution:
results = await asyncio.gather(fetch(u1), fetch(u2), fetch(u3))
results = await asyncio.gather(*tasks, return_exceptions=True)

# Background task:
task = asyncio.create_task(fetch(url))
# ... other work ...
result = await task

# Timeout:
try:
    result = await asyncio.wait_for(fetch(url), timeout=5.0)
except asyncio.TimeoutError:
    pass

# Wait with control:
done, pending = await asyncio.wait(tasks, timeout=5.0,
                                   return_when=asyncio.FIRST_COMPLETED)
for t in pending: t.cancel()

# Run blocking code without freezing event loop:
result = await asyncio.to_thread(blocking_func, arg)   # Python 3.9+
# or:
loop = asyncio.get_event_loop()
result = await loop.run_in_executor(None, blocking_func, arg)

# asyncio sync primitives (non-blocking):
lock  = asyncio.Lock()
sem   = asyncio.Semaphore(10)
event = asyncio.Event()
q     = asyncio.Queue(maxsize=100)

async with lock: ...
async with sem:  ...
await event.wait()
await q.put(item)
item = await q.get()
```

---

## 🔄 Producer/Consumer Pattern

```python
import queue, threading

task_q  = queue.Queue(maxsize=50)
NUM_W   = 4

def producer(items):
    for item in items:
        task_q.put(item)
    for _ in range(NUM_W):
        task_q.put(None)   # sentinel per worker

def worker():
    while True:
        item = task_q.get()
        if item is None:
            break
        try:
            process(item)
        finally:
            task_q.task_done()

threads = [threading.Thread(target=worker) for _ in range(NUM_W)]
for t in threads: t.daemon = True; t.start()
producer(data)
task_q.join()
```

---

## 🔴 Gotchas

```python
# 1 — Threading doesn't speed up CPU work (GIL):
# Fix: use ProcessPoolExecutor for CPU-bound

# 2 — Blocking call in async function freezes event loop:
async def bad():
    time.sleep(2)          # blocks!
    requests.get(url)      # blocks!
async def good():
    await asyncio.sleep(2)
    await asyncio.to_thread(requests.get, url)

# 3 — counter += 1 is not atomic:
# Fix: use threading.Lock() around it

# 4 — asyncio.run() inside running loop:
asyncio.run(coro())   # RuntimeError inside async def
await coro()          # correct

# 5 — Forgetting daemon=True on worker threads:
# Non-daemon threads prevent program from exiting

# 6 — Deadlock: inconsistent lock ordering:
# Fix: always acquire locks in same global order
```

---

## 🔥 Rapid-Fire

```
Q: Threading vs multiprocessing for CPU work?
A: Multiprocessing — threads share GIL, no speedup for pure Python CPU work.

Q: GIL released when?
A: I/O, time.sleep(), C extensions that release it explicitly.

Q: asyncio single or multi-threaded?
A: Single-threaded. Cooperative — tasks yield at await points.

Q: Thread-safe data structure for producer/consumer?
A: queue.Queue (or asyncio.Queue for async code).

Q: gather vs create_task?
A: gather: wait for all, returns list. create_task: fire-and-forget.

Q: How to run blocking code in async?
A: await asyncio.to_thread(func, arg)  or  run_in_executor

Q: Lock vs RLock?
A: RLock: same thread can acquire multiple times without deadlock.
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| 🧵 Threading Guide | [threading_guide.md](./threading_guide.md) |
| 🔥 Multiprocessing Guide | [multiprocessing_guide.md](./multiprocessing_guide.md) |
| ⚡ Async Guide | [async_guide.md](./async_guide.md) |
| ➡️ Next | [15 — Advanced Python](../15_advanced_python/theory.md) |
