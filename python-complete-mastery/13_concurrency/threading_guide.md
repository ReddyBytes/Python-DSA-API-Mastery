# 🧵 threading_guide.md — Python Threading, Deep Dive

> Complete reference for Python's threading module: Thread lifecycle,
> synchronization, thread pools, patterns, and common pitfalls.

---

## 📋 Contents

```
1.  Thread basics — create, start, join, daemon
2.  Thread lifecycle states
3.  Threading with return values
4.  Thread-local storage
5.  Lock — mutual exclusion
6.  RLock — re-entrant lock
7.  Semaphore — N-at-a-time control
8.  Event — thread signalling
9.  Condition — wait for state change
10. Barrier — synchronize N threads
11. Timer — delayed execution
12. ThreadPoolExecutor — managed pools
13. concurrent.futures.Future API
14. Producer/consumer with Queue
15. Common threading patterns
16. Debugging threads
```

---

## 1. Thread Basics

```python
import threading

def download(url, results, index):
    response = requests.get(url)
    results[index] = response.content

# Create:
t = threading.Thread(
    target=download,
    args=("http://example.com", results, 0),
    kwargs={},
    name="downloader-0",
    daemon=False,       # daemon=True → dies when main thread exits
)

# Lifecycle:
t.start()              # schedule for execution (non-blocking)
t.is_alive()           # True if thread is running
t.join()               # wait for completion (blocks caller)
t.join(timeout=5.0)    # wait at most 5 seconds
if t.is_alive():
    print("Thread still running after 5s!")

# Thread identity:
t.name                 # thread name (settable)
t.ident                # OS thread ID (set after start)
t.native_id            # native OS thread ID (Python 3.8+)
threading.current_thread()   # thread object of caller
threading.main_thread()      # the main thread
threading.active_count()     # number of alive threads
threading.enumerate()        # list of all alive Thread objects
```

---

## 2. Thread Lifecycle

```
State transitions:

  NEW          → created, not yet started
  RUNNABLE     → start() called, waiting for CPU
  RUNNING      → currently executing on CPU
  BLOCKED      → waiting for lock, I/O, or join()
  TERMINATED   → run() returned or exception raised

Daemon threads:
  daemon=True  → thread is killed when main thread exits
                 Use for background workers, monitoring
  daemon=False → (default) program waits for ALL non-daemon threads

Important: set daemon BEFORE start(), not after
```

---

## 3. Getting Return Values from Threads

Python's `Thread` doesn't have a built-in return value mechanism. Common patterns:

```python
import threading

# Pattern 1: mutable container
results = [None]
def task():
    results[0] = compute()

t = threading.Thread(target=task)
t.start(); t.join()
print(results[0])

# Pattern 2: queue
import queue
q = queue.Queue()
def task():
    q.put(compute())

t = threading.Thread(target=task)
t.start(); t.join()
result = q.get()

# Pattern 3: ThreadPoolExecutor (cleanest)
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor() as executor:
    future = executor.submit(compute)
    result = future.result()   # blocks and returns value, re-raises exceptions

# Pattern 4: subclass Thread
class ResultThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result    = None
        self.exception = None

    def run(self):
        try:
            self.result = self._target(*self._args, **self._kwargs)
        except Exception as e:
            self.exception = e

    def get_result(self):
        self.join()
        if self.exception:
            raise self.exception
        return self.result
```

---

## 4. Thread-Local Storage

Each thread gets its own independent copy of thread-local variables:

```python
import threading

# Create thread-local storage:
local = threading.local()

def worker(n):
    local.worker_id = n          # each thread has its own .worker_id
    local.db_conn   = db.connect()
    process(local.db_conn, local.worker_id)
    local.db_conn.close()

threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
for t in threads: t.start()
for t in threads: t.join()
# local.worker_id in one thread never interferes with another

# Common use: per-thread DB connections, request context, logging context
# Django's request object uses thread-local storage!
```

---

## 5. Lock — Mutual Exclusion

```python
import threading

lock = threading.Lock()

# Usage — always use with statement:
with lock:
    # only one thread here at a time
    shared_dict["key"] = compute_value()

# Manual acquire/release:
acquired = lock.acquire(blocking=True, timeout=5.0)
if acquired:
    try:
        modify_shared()
    finally:
        lock.release()   # MUST release in finally!
else:
    # couldn't get lock within 5 seconds
    raise TimeoutError("Lock timeout")

# Non-blocking check:
if lock.acquire(blocking=False):
    try:
        do_if_possible()
    finally:
        lock.release()
else:
    skip_or_retry()

# Check state (informational only — do not use for logic):
lock.locked()   # True if currently held
```

### Protecting Multiple Related Variables

```python
class BankAccount:
    def __init__(self, balance):
        self._balance = balance
        self._lock    = threading.Lock()

    def deposit(self, amount):
        with self._lock:
            self._balance += amount

    def withdraw(self, amount):
        with self._lock:
            if self._balance < amount:
                raise ValueError("Insufficient funds")
            self._balance -= amount

    @property
    def balance(self):
        with self._lock:
            return self._balance   # even reads need the lock for consistency
```

---

## 6. RLock — Re-Entrant Lock

```python
# Regular Lock deadlocks if the same thread acquires it twice:
lock = threading.Lock()
with lock:
    with lock:   # DEADLOCK — waiting for itself

# RLock tracks the owning thread and acquisition count:
rlock = threading.RLock()
with rlock:          # acquired: count=1
    with rlock:      # re-entered: count=2
        do_work()
    # count=1 (one release)
# count=0 (released)

# Use case: recursive functions that need a lock:
class Tree:
    def __init__(self):
        self._lock = threading.RLock()

    def process(self, node):
        with self._lock:
            work(node)
            for child in node.children:
                self.process(child)   # recursive — same thread re-acquires lock
```

---

## 7. Semaphore — Limit Concurrent Access

```python
import threading

# Allow at most N concurrent accesses:
db_semaphore = threading.Semaphore(5)   # max 5 concurrent DB connections

def query_db(sql):
    with db_semaphore:      # blocks if 5 connections already active
        conn = db.connect()
        result = conn.execute(sql).fetchall()
        conn.close()
        return result

# BoundedSemaphore — raises ValueError if released more than acquired:
sem = threading.BoundedSemaphore(3)

# Use cases:
# - Connection pool limits
# - Rate limiting (with time-based reset)
# - Controlling concurrent file opens
# - Throttling API calls
```

---

## 8. Event — Thread Signalling

```python
import threading, time

ready = threading.Event()

def producer():
    time.sleep(2)             # simulate setup
    data = load_data()
    ready.set()               # signal to all waiting threads

def consumer_1():
    print("Consumer 1 waiting...")
    ready.wait()              # blocks here until set()
    print("Consumer 1 processing")

def consumer_2():
    print("Consumer 2 waiting...")
    ready.wait(timeout=5.0)   # blocks up to 5 seconds
    if not ready.is_set():
        print("Consumer 2 timed out!")
        return
    print("Consumer 2 processing")

t_p = threading.Thread(target=producer)
t_c1 = threading.Thread(target=consumer_1)
t_c2 = threading.Thread(target=consumer_2)

t_c1.start(); t_c2.start(); t_p.start()
t_p.join(); t_c1.join(); t_c2.join()

# Event methods:
event.set()          # set flag to True, wake all waiters
event.clear()        # reset flag to False
event.is_set()       # check flag state
event.wait(timeout)  # block until flag is True or timeout
```

---

## 9. Condition — Wait for State Change

```python
import threading

condition = threading.Condition()
buffer    = []
MAX_SIZE  = 10

def producer():
    for item in data_source():
        with condition:
            while len(buffer) >= MAX_SIZE:
                condition.wait()   # release lock and block; re-acquire on notify
            buffer.append(item)
            condition.notify()     # wake one waiting consumer

def consumer():
    while True:
        with condition:
            while not buffer:
                condition.wait()   # release lock and block; re-acquire on notify
            item = buffer.pop(0)
            condition.notify()     # wake producer if it was waiting

# Condition wraps a Lock:
# condition.acquire() / condition.release() manage the underlying lock
# wait() atomically releases lock and blocks until notified
# notify(n=1) / notify_all() wake n (or all) waiting threads

# Use over Event when: consumers need to check a condition, not just a flag
```

---

## 10. Barrier — Synchronize N Threads at a Point

```python
import threading

NUM_WORKERS = 4
barrier = threading.Barrier(parties=NUM_WORKERS)

def worker(n):
    print(f"Worker {n}: preparing")
    time.sleep(n * 0.1)   # different prep times
    print(f"Worker {n}: ready, waiting at barrier")

    barrier.wait()         # ALL workers block here until all NUM_WORKERS arrive

    print(f"Worker {n}: starting execution")   # all start together

threads = [threading.Thread(target=worker, args=(i,)) for i in range(NUM_WORKERS)]
for t in threads: t.start()
for t in threads: t.join()

# Barrier with action (runs once when all parties arrive):
def kick_off():
    print("All workers ready! Starting...")

barrier = threading.Barrier(4, action=kick_off)

# barrier.wait() returns the "arrival index" (0 to parties-1)
# Use for: parallel algorithms with synchronization points, game rounds
```

---

## 11. Timer — Delayed Execution

```python
import threading

def cleanup():
    print("Running cleanup after delay")

# Run cleanup() after 5 seconds:
timer = threading.Timer(interval=5.0, function=cleanup, args=(), kwargs={})
timer.start()

# Cancel before it fires:
timer.cancel()

# Repeating timer (using recursion):
def repeating_task():
    do_work()
    timer = threading.Timer(60.0, repeating_task)
    timer.daemon = True
    timer.start()

repeating_task()   # first call, then repeats every 60s
```

---

## 12. ThreadPoolExecutor — Managed Thread Pools

```python
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED

# Context manager (auto-shutdown on exit):
with ThreadPoolExecutor(max_workers=10) as executor:

    # map — like built-in map, but parallel:
    results = list(executor.map(process, items))
    results = list(executor.map(process, items, timeout=30))

    # submit — non-blocking, returns Future:
    future = executor.submit(process, item)

    # Multiple submits:
    futures = [executor.submit(process, item) for item in items]

    # Process in COMPLETION order (fastest first):
    for future in as_completed(futures):
        result = future.result()   # raises if task raised

    # Process in SUBMISSION order:
    for future in futures:
        result = future.result()

    # Wait for subset:
    done, not_done = wait(futures, timeout=10, return_when=FIRST_COMPLETED)

    # Callbacks:
    def on_complete(future):
        print(future.result())
    executor.submit(process, item).add_done_callback(on_complete)

# Future API:
f.result(timeout=5)    # block until done; re-raises exception
f.exception()          # exception if failed, None if success
f.done()               # True if completed
f.cancel()             # cancel if not yet running
f.cancelled()          # True if successfully cancelled
f.running()            # True if currently executing
```

---

## 13. Producer/Consumer Pattern (Complete Example)

```python
import threading, queue, logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

def run_pipeline(
    data_source,
    process_fn,
    num_workers: int = 4,
    queue_size: int = 100,
):
    task_queue = queue.Queue(maxsize=queue_size)
    results    = []
    errors     = []
    results_lock = threading.Lock()

    def producer():
        try:
            for item in data_source:
                task_queue.put(item)                 # blocks if queue full
        finally:
            for _ in range(num_workers):
                task_queue.put(None)                 # sentinel per worker

    def worker():
        while True:
            item = task_queue.get()
            if item is None:
                task_queue.task_done()
                break
            try:
                result = process_fn(item)
                with results_lock:
                    results.append(result)
            except Exception as e:
                logger.error("Failed on %r: %s", item, e)
                with results_lock:
                    errors.append((item, e))
            finally:
                task_queue.task_done()

    # Start producer thread:
    prod_thread = threading.Thread(target=producer, daemon=True)
    prod_thread.start()

    # Start worker threads:
    workers = [threading.Thread(target=worker, daemon=True) for _ in range(num_workers)]
    for w in workers: w.start()

    # Wait for all tasks to be processed:
    task_queue.join()
    prod_thread.join()

    return results, errors

# Usage:
results, errors = run_pipeline(
    data_source=read_csv("data.csv"),
    process_fn=transform_row,
    num_workers=8,
)
```

---

## 14. Debugging Threads

```python
import threading, sys, traceback

# List all alive threads:
for t in threading.enumerate():
    print(f"{t.name}: alive={t.is_alive()}, daemon={t.daemon}")

# Print all thread stacks (diagnose deadlocks/hangs):
def dump_thread_stacks():
    for thread_id, frame in sys._current_frames().items():
        thread = next(
            (t for t in threading.enumerate() if t.ident == thread_id),
            None
        )
        name = thread.name if thread else f"Thread-{thread_id}"
        print(f"\n=== {name} ===")
        traceback.print_stack(frame)

# Detect likely deadlock (all threads blocked):
import time, signal

def deadlock_watchdog(interval=30):
    """Periodically check if all threads are alive but blocked."""
    while True:
        time.sleep(interval)
        threads = [t for t in threading.enumerate() if t != threading.current_thread()]
        alive   = [t for t in threads if t.is_alive()]
        if alive:
            dump_thread_stacks()

watchdog = threading.Thread(target=deadlock_watchdog, daemon=True)
watchdog.start()

# faulthandler — dump stacks on SIGABRT or crash:
import faulthandler
faulthandler.enable()
# Send SIGABRT to dump all thread stacks to stderr
```

---

## 🔴 Common Mistakes

```python
# 1 — Using threading for CPU-heavy pure Python:
# GIL means no speedup. Use ProcessPoolExecutor.

# 2 — Forgetting to call join():
t = Thread(target=work)
t.start()
# program exits — thread may not finish!
t.join()   # ← add this

# 3 — Not using daemon=True on background threads:
# Program hangs on exit waiting for non-daemon thread

# 4 — Assuming compound operations are atomic:
counter += 1   # read + add + write — NOT atomic!
# Fix: use a lock

# 5 — Lock inside try without finally:
lock.acquire()
do_risky_work()   # raises!
lock.release()    # never reached → deadlock

# Fix: always use 'with lock:' or try/finally

# 6 — Sharing non-thread-safe objects:
# list.append() is thread-safe (GIL + single bytecode)
# list.extend() is NOT (multiple bytecodes)
# dict operations — mostly thread-safe in CPython, but don't rely on it
# Always use a lock or queue.Queue for shared mutable state
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🔥 Multiprocessing Guide | [multiprocessing_guide.md](./multiprocessing_guide.md) |
| ⚡ Async Guide | [async_guide.md](./async_guide.md) |
