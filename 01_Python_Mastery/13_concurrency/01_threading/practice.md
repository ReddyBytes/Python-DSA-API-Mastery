# Threading — Practice

15 focused exercises from thread creation through thread-safe data structures.

---

## Quick Index

| # | Difficulty | Concept |
|---|---|---|
| Q1 | 🟢 Easy | Create two threads, start + join |
| Q2 | 🟢 Easy | ThreadPoolExecutor with 4 workers |
| Q3 | 🟡 Medium | Race condition: bug + fix with Lock |
| Q4 | 🟡 Medium | Producer-consumer with Queue |
| Q5 | 🟡 Medium | threading.Event: signal worker to stop |
| Q6 | 🟡 Medium | RLock vs Lock: recursive method |
| Q7 | 🟡 Medium | Daemon thread: auto-stop on main exit |
| Q8 | 🟡 Medium | as_completed: process results in arrival order |
| Q9 | 🟡 Medium | GIL: why threading doesn't help CPU work |
| Q10 | 🟡 Medium | ThreadPoolExecutor context manager shutdown |
| Q11 | 🟠 Hard | join() with timeout — detect hung thread |
| Q12 | 🟠 Hard | Bound max_workers for I/O-bound pool |
| Q13 | 🟡 Medium | threading.local() per-thread storage |
| Q14 | 🟠 Hard | Concurrent URL fetch, results in input order |
| Q15 | 🟠 Hard | Capstone: thread-safe cache with RLock |

---

### Q1 🟢 · Thread Basics — Create two threads, start + join

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

**Problem:** Write a `download(url, delay)` function that prints start/done messages and sleeps for `delay` seconds. Create two threads targeting it with different URLs and delays. Start both, join both. Print total elapsed time and show it is less than the sum of delays.

<details>
<summary>💡 Hint</summary>
`threading.Thread(target=fn, args=(...))`, then `.start()` on both before calling `.join()` on either.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading, time

def download(url: str, delay: float) -> None:
    print(f"Starting {url}")
    time.sleep(delay)
    print(f"Done {url}")

t1 = threading.Thread(target=download, args=("file_a.zip", 0.3), name="T1")
t2 = threading.Thread(target=download, args=("file_b.zip", 0.2), name="T2")

start = time.perf_counter()
t1.start()
t2.start()
t1.join()
t2.join()
print(f"Total: {time.perf_counter()-start:.2f}s")  # ~0.3s not 0.5s
```

**Why:** Both threads start before either is joined. While T1 waits 0.3s, T2 completes its 0.2s wait concurrently. Total time is the maximum, not the sum.
</details>

---

### Q2 🟢 · ThreadPoolExecutor — 4 workers, 6 tasks

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

**Problem:** Use `ThreadPoolExecutor(max_workers=4)` to run `process(n)` (which sleeps `n * 0.05` seconds and returns `n ** 2`) over the list `[1, 2, 3, 4, 5, 6]`. Print results in input order.

<details>
<summary>💡 Hint</summary>
`executor.map(fn, items)` returns results in input order. Use the context manager form.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time
from concurrent.futures import ThreadPoolExecutor

def process(n: int) -> int:
    time.sleep(n * 0.05)
    return n ** 2

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process, [1, 2, 3, 4, 5, 6]))

print(results)  # [1, 4, 9, 16, 25, 36]
```

**Why:** `map()` submits all 6 tasks, up to 4 run simultaneously, results come back in submission order regardless of completion order.
</details>

---

### Q3 🟡 · Thread Safety — Race condition: bug then fix with Lock

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

**Problem:** Create an `UnsafeCounter` with `increment(n)` that loops `n` times doing `self.value += 1`. Run 10 threads each calling `increment(1000)`. Show the result is often less than 10,000 (race condition). Then create `SafeCounter` that fixes it with `threading.Lock`.

<details>
<summary>💡 Hint</summary>
`counter += 1` is three bytecodes: LOAD, ADD, STORE. A thread can be interrupted between any two. Wrap with `with self._lock:`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading

class UnsafeCounter:
    def __init__(self): self.value = 0
    def increment(self, n):
        for _ in range(n): self.value += 1  # LOAD+ADD+STORE: not atomic

class SafeCounter:
    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()
    def increment(self, n):
        for _ in range(n):
            with self._lock: self.value += 1

def run(counter, n_threads=10, n_each=1000):
    threads = [threading.Thread(target=counter.increment, args=(n_each,))
               for _ in range(n_threads)]
    for t in threads: t.start()
    for t in threads: t.join()
    return counter.value

print(run(UnsafeCounter()))   # often < 10000
print(run(SafeCounter()))     # always 10000
```

**Why:** `with self._lock:` makes the read-modify-write atomic: only one thread can be inside that block at a time.
</details>

---

### Q4 🟡 · Thread Communication — Producer-consumer with Queue

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

**Problem:** Write a producer that puts integers 1–5 onto a `queue.Queue`, followed by a sentinel `None`. Write a consumer that reads until `None`, printing each item squared. Run them in separate threads.

<details>
<summary>💡 Hint</summary>
`queue.Queue` is thread-safe — no lock needed. Use a sentinel value (`None`) to signal the consumer to stop.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading, queue, time

def producer(q: queue.Queue) -> None:
    for i in range(1, 6):
        time.sleep(0.02)
        q.put(i)
    q.put(None)   # sentinel

def consumer(q: queue.Queue) -> None:
    while True:
        item = q.get()
        if item is None:
            break
        print(f"Consumer: {item} → {item ** 2}")
        q.task_done()

q = queue.Queue()
t_prod = threading.Thread(target=producer, args=(q,))
t_cons = threading.Thread(target=consumer, args=(q,))
t_prod.start(); t_cons.start()
t_prod.join(); t_cons.join()
```

**Why:** `queue.Queue` handles all locking internally. `task_done()` pairs with `q.join()` if you want to wait until all items are processed.
</details>

---

### Q5 🟡 · Signaling — threading.Event to stop a worker

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

**Problem:** Write a worker thread that loops, printing "working..." every 0.1s, and checks a `threading.Event` stop signal. In the main thread, start the worker, wait 0.35s, then set the stop event. Show the worker stops cleanly.

<details>
<summary>💡 Hint</summary>
`event.is_set()` returns `True` after `event.set()`. Use it as the loop condition.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading, time

stop_event = threading.Event()

def worker():
    while not stop_event.is_set():
        print("working...")
        time.sleep(0.1)
    print("Worker stopped cleanly")

t = threading.Thread(target=worker)
t.start()
time.sleep(0.35)
stop_event.set()
t.join()
```

**Why:** `Event` is a thread-safe flag. `.set()` wakes any thread blocked on `.wait()` and causes `.is_set()` to return `True`.
</details>

---

### Q6 🟡 · Locking — RLock for recursive methods

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

**Problem:** Create a `TreeNode` class with `_lock = threading.RLock()` and a `process(depth)` method that acquires the lock and calls itself recursively (depth times). Show it works with RLock. Then swap to `threading.Lock` and show it deadlocks (or explain why without running it).

<details>
<summary>💡 Hint</summary>
A `Lock` deadlocks when the same thread tries to acquire it twice. `RLock` tracks the owning thread and a count, allowing re-entry.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading

class TreeNode:
    def __init__(self):
        self._lock = threading.RLock()   # re-entrant: same thread can re-acquire

    def process(self, depth: int) -> None:
        with self._lock:                 # count += 1 on each entry
            print(f"  depth {depth}")
            if depth > 0:
                self.process(depth - 1)  # same thread re-acquires lock safely
            # count -= 1 on exit; released when count reaches 0

node = TreeNode()
node.process(3)   # works fine

# With threading.Lock: the second 'with lock:' blocks waiting for the
# same thread to release it — deadlock, hangs forever.
```

**Why:** RLock tracks the owning thread. The same thread can acquire it multiple times; each acquisition increments a count, each release decrements it. Only fully released when count reaches zero.
</details>

---

### Q7 🟡 · Daemon Threads — auto-stop on main exit

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

**Problem:** Create a background monitor thread that prints "heartbeat" every 0.2s. Make it daemon so the program exits without waiting for it. Show the difference: run once with `daemon=True` (program exits quickly) and explain what `daemon=False` would do.

<details>
<summary>💡 Hint</summary>
Set `daemon=True` **before** calling `.start()`. Daemon threads are killed when the last non-daemon thread finishes.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading, time

def heartbeat():
    while True:
        print("heartbeat")
        time.sleep(0.2)

monitor = threading.Thread(target=heartbeat, daemon=True)  # set BEFORE start()
monitor.start()

time.sleep(0.5)
print("Main done — program exits, daemon thread killed")
# With daemon=False: program would hang here indefinitely
```

**Why:** Non-daemon threads keep the process alive. Daemon threads are killed when all non-daemon threads finish. Use `daemon=True` for background monitors, heartbeats, and cleanup tasks.
</details>

---

### Q8 🟡 · Futures — as_completed: process in arrival order

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

**Problem:** Submit 5 tasks to a `ThreadPoolExecutor` where each task sleeps for a random delay (0.05–0.3s) and returns its task ID. Use `as_completed` to print results as each finishes. Show they arrive out of submission order.

<details>
<summary>💡 Hint</summary>
Build a `futures = {executor.submit(fn, arg): arg for arg in items}` dict to map futures back to their inputs.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time, random
from concurrent.futures import ThreadPoolExecutor, as_completed

def task(task_id: int) -> str:
    delay = random.uniform(0.05, 0.3)
    time.sleep(delay)
    return f"task_{task_id} done in {delay:.2f}s"

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(task, i): i for i in range(1, 6)}
    for future in as_completed(futures):
        task_id = futures[future]
        print(f"Task {task_id}: {future.result()}")
```

**Why:** `as_completed` yields futures as they complete, not in submission order. Use this for dashboards, early-result processing, or when you want to react to each result immediately.
</details>

---

### Q9 🟡 · GIL — why threading doesn't speed up CPU work

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

**Problem:** Write a CPU-bound function `cpu_sum(n)` that sums squares from 0 to n. Time running it twice sequentially vs running it in two threads concurrently. Show threads give no speedup (or are slower). Explain in a comment why.

<details>
<summary>💡 Hint</summary>
The GIL ensures only one thread executes Python bytecode at a time. Two threads on CPU work don't run in parallel — they take turns.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading, time

def cpu_sum(n: int) -> int:
    return sum(i * i for i in range(n))

N = 2_000_000

# Sequential
start = time.perf_counter()
cpu_sum(N); cpu_sum(N)
seq = time.perf_counter() - start

# Threaded
start = time.perf_counter()
t1 = threading.Thread(target=cpu_sum, args=(N,))
t2 = threading.Thread(target=cpu_sum, args=(N,))
t1.start(); t2.start(); t1.join(); t2.join()
thr = time.perf_counter() - start

print(f"Sequential: {seq:.3f}s")
print(f"Threaded:   {thr:.3f}s  (same or slower)")
# The GIL serializes Python bytecode execution.
# Two threads compete for the lock rather than running on separate cores.
# Fix: ProcessPoolExecutor for true CPU parallelism.
```

**Why:** CPython's GIL prevents two threads from executing Python bytecode simultaneously. For CPU-bound work, use `ProcessPoolExecutor` — each process has its own GIL.
</details>

---

### Q10 🟡 · Resource Management — context manager ensures shutdown

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

**Problem:** Use `ThreadPoolExecutor` as a context manager. Inside it, submit 3 tasks. Show that exiting the `with` block waits for all tasks to complete before continuing. Then show what happens if you forget the `with` and call `executor.shutdown(wait=True)` manually.

<details>
<summary>💡 Hint</summary>
The `with` block calls `shutdown(wait=True)` automatically on exit, blocking until all submitted futures complete.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time
from concurrent.futures import ThreadPoolExecutor

def slow_task(n: int) -> int:
    time.sleep(0.1)
    return n * 2

# With context manager (preferred):
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(slow_task, i) for i in range(1, 4)]
# All tasks guaranteed complete here

results = [f.result() for f in futures]
print(results)  # [2, 4, 6]

# Without context manager (manual shutdown):
executor = ThreadPoolExecutor(max_workers=3)
futures = [executor.submit(slow_task, i) for i in range(1, 4)]
executor.shutdown(wait=True)   # same effect as exiting 'with'
results = [f.result() for f in futures]
```

**Why:** `shutdown(wait=True)` blocks until all running futures complete. The context manager calls this automatically, preventing resource leaks.
</details>

---

### Q11 🟠 · Timeouts — join() with timeout to detect hung thread

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

**Problem:** Start a thread that sleeps for 5 seconds (simulating a hung operation). Join it with a 0.5-second timeout. Detect that it is still alive after the timeout. Log a warning and continue without waiting.

<details>
<summary>💡 Hint</summary>
`t.join(timeout=N)` returns after at most N seconds. Check `t.is_alive()` to see if the timeout expired.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading, time

def hung_operation():
    time.sleep(5)   # simulates a stuck/slow thread

t = threading.Thread(target=hung_operation, daemon=True)
t.start()

t.join(timeout=0.5)   # wait at most 0.5 seconds

if t.is_alive():
    print("WARNING: thread still running after timeout — possible hang")
    # t is daemon=True, so it won't prevent program exit
else:
    print("Thread completed within timeout")
```

**Why:** `join(timeout=N)` always returns after N seconds regardless of thread state. The thread is NOT cancelled — check `is_alive()` to distinguish timeout from normal completion. Mark as `daemon=True` so a stuck thread doesn't block program exit.
</details>

---

### Q12 🟠 · Pool Sizing — bound max_workers for I/O-bound work

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

**Problem:** Write a function that simulates an HTTP GET (sleeps 0.1s). Time running 20 requests sequentially, with `max_workers=4`, and with `max_workers=20`. Show the speedup at each level and explain the diminishing returns.

<details>
<summary>💡 Hint</summary>
For I/O-bound work with uniform 0.1s tasks: with N workers and 20 tasks, time ≈ ceil(20/N) * 0.1s.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time
from concurrent.futures import ThreadPoolExecutor

def http_get(url: str) -> str:
    time.sleep(0.1)   # simulate network latency
    return f"response from {url}"

urls = [f"https://api.example.com/item/{i}" for i in range(20)]

for n_workers in [1, 4, 10, 20]:
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        results = list(executor.map(http_get, urls))
    elapsed = time.perf_counter() - start
    print(f"workers={n_workers:2d}: {elapsed:.2f}s  ({len(results)} results)")
# workers=1:  ~2.0s
# workers=4:  ~0.5s  (4 batches of 5)
# workers=10: ~0.2s  (2 batches of 10)
# workers=20: ~0.1s  (all at once)
```

**Why:** I/O-bound tasks spend most of their time waiting (GIL released). More workers = more concurrent waits. But beyond the number of tasks, extra workers add overhead without benefit.
</details>

---

### Q13 🟡 · Thread-Local — per-thread storage with threading.local()

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)

**Problem:** Use `threading.local()` to give each thread its own `worker_id` and `connection` (simulated). Run 3 threads and show that reading `_local.worker_id` in one thread never sees another thread's value.

<details>
<summary>💡 Hint</summary>
Assign to `_local.attr = value` inside the thread function. Each thread has a completely independent copy of all attributes on the `local()` object.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading, time

_local = threading.local()

def worker(worker_id: int) -> None:
    _local.worker_id = worker_id
    _local.conn = f"conn_for_worker_{worker_id}"   # simulated per-thread connection
    time.sleep(0.05)
    # This thread only sees ITS OWN values
    print(f"Thread {worker_id}: id={_local.worker_id}, conn={_local.conn}")

threads = [threading.Thread(target=worker, args=(i,)) for i in range(1, 4)]
for t in threads: t.start()
for t in threads: t.join()
```

**Why:** `threading.local()` is like a dictionary keyed by thread identity. Each thread's writes are invisible to others. Classic use: per-thread DB connections, Flask's `g` object, Django's request context.
</details>

---

### Q14 🟠 · Patterns — Concurrent URL fetch, results in input order

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)

**Problem:** Fetch 6 URLs concurrently using `ThreadPoolExecutor`. Each "fetch" sleeps a random delay and returns `{"url": url, "status": 200}`. Return results in the **same order as input**, not completion order.

<details>
<summary>💡 Hint</summary>
`executor.map()` returns results in input order. Alternatively, build a list of futures in order and call `.result()` on each sequentially.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time, random
from concurrent.futures import ThreadPoolExecutor

def fetch(url: str) -> dict:
    time.sleep(random.uniform(0.05, 0.3))
    return {"url": url, "status": 200}

urls = [f"https://api.example.com/item/{i}" for i in range(6)]

# Option 1: map() — always returns in input order
with ThreadPoolExecutor(max_workers=6) as executor:
    results = list(executor.map(fetch, urls))

for r in results:
    print(r["url"], r["status"])

# Option 2: submit + ordered result retrieval
with ThreadPoolExecutor(max_workers=6) as executor:
    futures = [executor.submit(fetch, url) for url in urls]
    results = [f.result() for f in futures]  # iterate futures in submission order
```

**Why:** `map()` guarantees input order. With `submit()`, iterating futures in submission order and calling `.result()` also gives input order (but blocks on each sequentially if not done).
</details>

---

### Q15 🟠 · Capstone — Thread-safe cache with RLock

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)

**Problem:** Build a `ThreadSafeCache` class with:
- `get(key)` — returns cached value or `None`
- `set(key, value)` — stores value
- `get_or_compute(key, compute_fn)` — returns cached value if present; otherwise calls `compute_fn()`, stores result, returns it

Protect with `threading.RLock` (so `get_or_compute` can call `get` and `set` internally without deadlock). Test with 5 threads all calling `get_or_compute("x", expensive_fn)` and verify `expensive_fn` is called only once.

<details>
<summary>💡 Hint</summary>
`RLock` allows the same thread to acquire the lock multiple times. Use it so `get_or_compute` can call `get()` and `set()` — both of which also acquire the lock — without deadlocking.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading, time

class ThreadSafeCache:
    def __init__(self):
        self._data = {}
        self._lock = threading.RLock()   # re-entrant: get_or_compute can call get/set

    def get(self, key: str):
        with self._lock:
            return self._data.get(key)

    def set(self, key: str, value) -> None:
        with self._lock:
            self._data[key] = value

    def get_or_compute(self, key: str, compute_fn) -> object:
        with self._lock:                  # outer acquire
            value = self.get(key)         # inner acquire (RLock: same thread, OK)
            if value is None:
                value = compute_fn()
                self.set(key, value)      # inner acquire (still same thread, OK)
            return value

compute_calls = 0

def expensive_fn():
    global compute_calls
    compute_calls += 1
    time.sleep(0.1)
    return 42

cache = ThreadSafeCache()
threads = [threading.Thread(target=cache.get_or_compute, args=("x", expensive_fn))
           for _ in range(5)]
for t in threads: t.start()
for t in threads: t.join()

print(f"Compute calls: {compute_calls}")  # should be 1, not 5
print(f"Cached value: {cache.get('x')}")  # 42
```

**Why:** `RLock` allows `get_or_compute` to hold the lock while calling `get` and `set`, preventing concurrent threads from entering the compute block. The double-checked locking pattern (check cache, compute, store) is only safe under a lock.
</details>

---

## 🔁 Navigation

| | |
|---|---|
| ⬆️ Threading Theory | [theory.md](./theory.md) |
| 💻 Practice Local | [practice_local.py](./practice_local.py) |
| 🔥 Multiprocessing Practice | [../02_multiprocessing/practice.md](../02_multiprocessing/practice.md) |
| ⚡ Asyncio Practice | [../03_asyncio/practice.md](../03_asyncio/practice.md) |
| 🗂️ Root Practice | [../practice.md](../practice.md) |

---

**[Back to README](../../README.md)**

**Prev:** [Threading Theory](./theory.md) | **Next:** [Multiprocessing Practice →](../02_multiprocessing/practice.md)

**Related Topics:** [Threading Theory](./theory.md) · [Multiprocessing Practice](../02_multiprocessing/practice.md) · [Asyncio Practice](../03_asyncio/practice.md) · [Root Practice](../practice.md)
