# Threading — Theory

Think of threads as workers sharing one office: they all see the same whiteboard (memory), can hand each other sticky notes instantly, but only one person can write on the whiteboard at a time — that rule is the GIL.

---

## 📌 Learning Priority

**Must Learn** — Core use, interview essential:
`threading.Thread` · `ThreadPoolExecutor` · `Lock` / `RLock` · `join()` · GIL mental model

**Should Learn** — Important for real projects:
`Queue` for thread communication · `Event` · daemon threads · `as_completed`

**Good to Know** — Useful in specific situations:
`Semaphore` · `Barrier` · `Condition`

**Reference** — Know it exists, look up when needed:
`threading.local()` · `Timer` · weakref patterns · `faulthandler`

---

## Chapter 1: What Threads Are

Imagine ten customer service agents working in a single open-plan office. They share the same filing cabinets, the same printer, the same phone system. When one agent needs a file, they walk to the cabinet — that takes time. While they walk, the other agents keep working. This overlap of waiting and working is exactly what threads do for I/O-bound code.

A **thread** is a unit of execution that lives inside a process. All threads in one process share:
- the same heap (variables, objects)
- the same open file handles and network sockets
- the same loaded modules

They each have their own:
- call stack (function call chain)
- program counter (which instruction to run next)
- local variables

```
PROCESS MEMORY MAP

  ┌─────────────────────────────────────────────────────┐
  │  CODE (shared)   │  HEAP (shared)                   │
  │  modules         │  your dict, list, objects here   │
  ├──────────────────┴──────────────────────────────────┤
  │  Thread 1 stack  │  Thread 2 stack  │  Thread 3 ... │
  │  frame → frame   │  frame → frame   │               │
  └──────────────────┴──────────────────┴───────────────┘
```

Because they share memory, threads can communicate cheaply (just read/write shared variables), but that same sharing creates **race conditions** if uncoordinated.

**When to use threads:** I/O-bound work — HTTP calls, database queries, reading files. The bottleneck is waiting, not computing. While one thread waits for a network response, others can run.

**When NOT to use threads:** CPU-bound work — pure Python computation. The GIL prevents true parallel execution. Use `ProcessPoolExecutor` instead.

---

## Chapter 2: Creating Threads — Thread, start(), join()

The most direct way: wrap a callable in `threading.Thread`, call `start()`, then `join()` to wait.

```python
import threading
import time

def download(url: str, delay: float) -> None:
    print(f"Starting {url}")
    time.sleep(delay)                    # ← simulates network I/O
    print(f"Done {url}")

# Create thread objects
t1 = threading.Thread(
    target=download,
    args=("file_a.zip", 0.3),
    name="Worker-A",                     # ← meaningful names help debugging
    daemon=False,                        # ← False: program waits for this thread
)
t2 = threading.Thread(target=download, args=("file_b.zip", 0.2))

# start() schedules the thread — non-blocking, returns immediately
t1.start()
t2.start()

# join() blocks the caller until the thread completes
t1.join()
t2.join()
# Both downloads ran concurrently — total time ≈ max(0.3, 0.2) = 0.3s
```

```
SEQUENTIAL vs THREADED TIMELINE

Sequential:
  Main ──[A: 0.3s]──────────[B: 0.2s]────── done at 0.5s

Threaded:
  Main ──────────────────────────────────── join, done at 0.3s
    T1 ──[A: 0.3s]──────────
    T2 ──[B: 0.2s]────
```

Key thread attributes and methods:

```python
t.name          # thread name (settable, useful for logs)
t.ident         # OS thread ID (set after start())
t.native_id     # native OS thread ID (Python 3.8+)
t.is_alive()    # True while running
t.join()        # wait forever
t.join(timeout=5.0)   # wait at most 5 seconds
if t.is_alive():
    print("Thread still running after 5s — possibly hung")

threading.current_thread()    # Thread object of the caller
threading.main_thread()       # the main thread
threading.active_count()      # number of alive threads
threading.enumerate()         # list of all alive Thread objects
```

**Getting return values from threads:**

`Thread.run()` returns `None`. Three common patterns:

```python
# Pattern 1 — shared list (simple, needs care with large output)
results = [None]
def task():
    results[0] = compute()
t = threading.Thread(target=task)
t.start(); t.join()
print(results[0])

# Pattern 2 — Queue (thread-safe, no lock needed)
import queue
q = queue.Queue()
def task():
    q.put(compute())
t = threading.Thread(target=task)
t.start(); t.join()
result = q.get()

# Pattern 3 — ThreadPoolExecutor (cleanest, see Chapter 4)
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor() as executor:
    future = executor.submit(compute)
    result = future.result()   # ← blocks, re-raises exceptions automatically
```

---

## Chapter 3: The GIL — Python's Most Misunderstood Rule

The **Global Interpreter Lock** (GIL) is a mutex inside CPython that ensures only one thread executes Python bytecode at any moment.

Why does it exist? CPython's memory management (reference counting for garbage collection) is not thread-safe. The GIL is a simple solution: serialize all Python bytecode execution to avoid corruption.

```
WITHOUT GIL (hypothetical):
  Thread A: reading refcount of object X → 5
  Thread B: reading refcount of object X → 5
  Thread A: writes refcount = 5 - 1 = 4
  Thread B: writes refcount = 5 - 1 = 4  ← WRONG! Should be 3
  Object never freed (or freed too early) → memory corruption

WITH GIL:
  Thread A holds GIL → reads 5, writes 4, releases GIL
  Thread B acquires GIL → reads 4, writes 3
  Correct!
```

**What the GIL allows:** The GIL is **released during I/O operations** — reading a file, waiting on a network socket, sleeping. During those pauses, other threads can acquire the GIL and run Python code. This is why threading genuinely helps I/O-bound work.

**What the GIL prevents:** True parallel execution of Python bytecode on multiple cores. Two CPU-bound threads do not run simultaneously — they take turns holding the GIL, providing no speedup and adding context-switch overhead.

```
GIL BEHAVIOR DIAGRAM

I/O-bound threads:
  Thread A: [Python]─────────[waiting for network]──────[Python]
  Thread B:       [Python]───────────[waiting for DB]───────[Python]
                  ↑ GIL switches here (A releases on I/O wait)
  → Threads truly overlap. ~2x speedup on 2 threads.

CPU-bound threads:
  Thread A: [Python][GIL wait][Python][GIL wait]
  Thread B: [GIL wait][Python][GIL wait][Python]
  → Sequential execution with extra overhead. No speedup.
```

**Practical rules:**
- I/O-bound? Use threads (or asyncio).
- CPU-bound pure Python? Use `ProcessPoolExecutor`.
- CPU-bound C extension (NumPy, OpenCV)? Threads work — these extensions release the GIL.

---

## Chapter 4: ThreadPoolExecutor — The Modern Way

Managing individual `Thread` objects is verbose. `ThreadPoolExecutor` manages a pool of worker threads for you, provides `Future` objects for results, and handles exceptions cleanly.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch(url: str) -> dict:
    import time, random
    time.sleep(random.uniform(0.05, 0.2))
    return {"url": url, "status": 200}

urls = [f"https://api.example.com/item/{i}" for i in range(8)]

# map() — simplest, returns results in INPUT order
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(fetch, urls))
# context manager calls shutdown(wait=True) on exit — all threads finish

# submit() + as_completed() — process results as they arrive (fastest first)
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {executor.submit(fetch, url): url for url in urls}

    for future in as_completed(futures):
        url = futures[future]
        try:
            result = future.result()     # ← re-raises any exception from thread
            print(f"{url}: {result['status']}")
        except Exception as e:
            print(f"{url} failed: {e}")
```

**Future API:**

```python
f.result(timeout=5)  # block until done; raises exception if thread raised
f.exception()        # the exception if failed, None if success
f.done()             # True if completed (success or failure)
f.cancel()           # cancel if not yet started
f.cancelled()        # True if successfully cancelled
f.running()          # True if currently executing
f.add_done_callback(fn)  # call fn(future) when complete
```

**Choosing max_workers:**

```python
import os
# For I/O-bound work: more threads than cores is fine
# Rule of thumb: 2–4× CPU count for network I/O
max_workers = min(32, (os.cpu_count() or 1) + 4)   # Python 3.8+ default formula

# For CPU-bound work (rare with threads — prefer processes):
max_workers = os.cpu_count()
```

---

## Chapter 5: Thread Safety — Race Conditions, Lock, RLock

Two threads reading and writing the same variable without coordination produce a **race condition** — the final result depends on timing, not logic.

```
RACE CONDITION ON counter += 1

counter += 1 compiles to three bytecodes:
  LOAD_FAST   counter     # read current value
  LOAD_CONST  1
  INPLACE_ADD             # compute new value
  STORE_FAST  counter     # write result back

If Thread A is interrupted between LOAD and STORE:
  Thread A reads counter = 5
  Thread B reads counter = 5, writes 6
  Thread A writes 6  ← incremented twice, result only 6 not 7!
```

**Fix: `threading.Lock`** — mutual exclusion ensures only one thread is in the critical section:

```python
import threading

lock = threading.Lock()
counter = 0

def safe_increment(n: int) -> None:
    global counter
    for _ in range(n):
        with lock:           # ← only one thread here at a time
            counter += 1

threads = [threading.Thread(target=safe_increment, args=(1000,)) for _ in range(10)]
for t in threads: t.start()
for t in threads: t.join()
print(counter)  # always 10000, never less
```

Always use `with lock:` — it guarantees release even if an exception occurs. Never call `lock.acquire()` without a matching `lock.release()` in a `finally` block.

**Thread-safe class pattern:**

```python
class BankAccount:
    def __init__(self, balance: float):
        self._balance = balance
        self._lock    = threading.Lock()

    def deposit(self, amount: float) -> None:
        with self._lock:
            self._balance += amount

    def withdraw(self, amount: float) -> None:
        with self._lock:
            if self._balance < amount:
                raise ValueError("Insufficient funds")
            self._balance -= amount

    @property
    def balance(self) -> float:
        with self._lock:
            return self._balance   # ← reads need the lock too for consistency
```

**RLock — re-entrant lock:** A regular `Lock` deadlocks if the same thread tries to acquire it twice. `RLock` tracks ownership and counts:

```python
# Regular Lock → deadlock:
lock = threading.Lock()
with lock:
    with lock:   # blocks forever waiting for itself

# RLock → fine:
rlock = threading.RLock()
with rlock:          # count = 1
    with rlock:      # count = 2, same thread
        do_work()
    # count = 1
# count = 0, released

# Use case: recursive methods that need a lock
class Tree:
    _lock = threading.RLock()
    def process(self, node):
        with self._lock:
            work(node)
            for child in node.children:
                self.process(child)   # ← same thread re-acquires lock safely
```

---

## Chapter 6: Thread Communication — Queue, Event, Condition

**queue.Queue — the right way to pass work between threads:**

```python
import threading, queue

task_q: queue.Queue = queue.Queue(maxsize=100)

def producer(items: list) -> None:
    for item in items:
        task_q.put(item)        # blocks if queue is full
    task_q.put(None)            # sentinel signals worker to stop

def worker() -> None:
    while True:
        item = task_q.get()     # blocks if queue is empty
        if item is None:
            task_q.task_done()
            break
        process(item)
        task_q.task_done()      # signal item is fully handled

t_prod = threading.Thread(target=producer, args=(items,))
t_work = threading.Thread(target=worker)
t_prod.start(); t_work.start()
task_q.join()   # wait for all task_done() calls
```

**threading.Event — signal a condition:**

```python
ready = threading.Event()

def setup_worker():
    time.sleep(1)
    ready.set()             # ← wake all waiting threads

def dependent_worker():
    ready.wait()            # ← blocks until set()
    # or with timeout:
    if not ready.wait(timeout=5.0):
        raise TimeoutError("Setup took too long")
    do_work()
```

**threading.Condition — wait for a state change:**

```python
condition = threading.Condition()
buffer = []
MAX = 10

def producer():
    for item in source():
        with condition:
            while len(buffer) >= MAX:
                condition.wait()       # release lock + block; re-acquire on notify
            buffer.append(item)
            condition.notify()         # wake one waiter

def consumer():
    while True:
        with condition:
            while not buffer:
                condition.wait()
            item = buffer.pop(0)
            condition.notify()
```

---

## Chapter 7: Daemon Threads

A **daemon thread** is automatically killed when the main thread exits — no join needed. Use for background tasks that should not prevent program shutdown.

```python
import threading, time

def heartbeat():
    while True:
        print("still alive")
        time.sleep(10)

monitor = threading.Thread(target=heartbeat, daemon=True)  # ← set BEFORE start()
monitor.start()
# Program exits without waiting for monitor thread
```

Non-daemon threads (the default): the program stays alive until all non-daemon threads finish. Forgetting to join a non-daemon thread can cause your script to hang after `main()` returns.

```
PROGRAM EXIT BEHAVIOR

  Non-daemon:  program waits for thread to finish → safe for important work
  Daemon:      thread killed immediately when main exits → for background tasks

  RULE: background monitors, heartbeats → daemon=True
        threads doing important work → daemon=False (and join them)
```

---

## Chapter 8: Thread-Local Storage

Sometimes each thread needs its own private copy of a variable — for example, each thread should have its own database connection, not share one. `threading.local()` provides this:

```python
import threading

_local = threading.local()

def worker(worker_id: int) -> None:
    _local.conn     = db.connect()      # each thread gets its OWN .conn
    _local.user_id  = worker_id
    # another thread reading _local.conn sees ITS connection, not this one
    use(_local.conn, _local.user_id)
    _local.conn.close()
```

Classic use cases: per-thread DB connections, request context in web frameworks (Django uses this for `request`), per-thread logging context.

---

## Chapter 9: Common Mistakes

```python
# 1 — Using threads for CPU-bound pure Python
# GIL means two threads compete for one lock. No speedup, adds overhead.
# Fix: ProcessPoolExecutor

# 2 — Forgetting join()
t = threading.Thread(target=work)
t.start()
# main() returns — thread may not finish!
t.join()   # ← add this

# 3 — Not using daemon=True on background threads
# Program hangs on exit waiting for non-daemon threads
monitor = threading.Thread(target=background, daemon=True)

# 4 — Assuming compound operations are atomic
counter += 1   # NOT atomic: LOAD + ADD + STORE can be interrupted
# Fix: with lock: counter += 1

# 5 — Lock without finally (manual acquire/release)
lock.acquire()
risky()        # raises!
lock.release() # never reached → deadlock forever
# Fix: always use 'with lock:' statement

# 6 — Sharing non-thread-safe objects without a lock
# list.append() is safe in CPython (GIL + single bytecode)
# list.extend() is NOT (multiple bytecodes)
# dict operations: mostly safe in CPython, but don't rely on implementation detail
# Safe rule: if two threads write to the same mutable object, protect with a lock

# 7 — Setting daemon after start()
t = threading.Thread(target=work)
t.start()
t.daemon = True  # RuntimeError: cannot set daemon status after start
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬆️ Root Theory | [../theory.md](../theory.md) |
| 💻 Practice | [practice.md](./practice.md) |
| 🔥 Multiprocessing | [../02_multiprocessing/theory.md](../02_multiprocessing/theory.md) |
| ⚡ Asyncio | [../03_asyncio/theory.md](../03_asyncio/theory.md) |
| ⚡ Cheatsheet | [../cheetsheet.md](../cheetsheet.md) |
| 🔥 Interview Q&A | [../interview.md](../interview.md) |

---

**[Back to README](../../README.md)**

**Prev:** [Root Theory](../theory.md) | **Next:** [Multiprocessing Theory →](../02_multiprocessing/theory.md)

**Related Topics:** [Root Theory](../theory.md) · [Multiprocessing](../02_multiprocessing/theory.md) · [Asyncio](../03_asyncio/theory.md) · [Cheat Sheet](../cheetsheet.md) · [Interview Q&A](../interview.md)
