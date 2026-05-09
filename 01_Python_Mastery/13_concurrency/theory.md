<a id="top"></a>
# ⚙️ Concurrency — Theory

> *"Concurrency is about dealing with multiple things at once.*
> *Parallelism is about doing multiple things at once.*
> *Python supports both — but the GIL means you must choose the right tool."*

## 📖 Table of Contents

- [1. Concurrency vs Parallelism — The Critical Distinction](#1-concurrency-vs-parallelism--the-critical-distinction)
- [2. The GIL — Python's Most Misunderstood Feature](#2-the-gil--pythons-most-misunderstood-feature)
  - [The GIL — Global Interpreter Lock](#the-gil--global-interpreter-lock)
  - [Decision Tree: Which Concurrency Model?](#decision-tree-which-concurrency-model)
  - [asyncio Event Loop — Cooperative, Not Preemptive](#asyncio-event-loop--cooperative-not-preemptive)
- [3. Threading — I/O-Bound Concurrency](#3-threading--io-bound-concurrency)
  - [Basic Thread](#basic-thread)
  - [ThreadPoolExecutor — The Modern Way](#threadpoolexecutor--the-modern-way)
  - [Thread Lifecycle](#thread-lifecycle)
- [4. Race Conditions — When Threads Collide](#4-race-conditions--when-threads-collide)
- [5. Thread Synchronization](#5-thread-synchronization)
  - [Lock — Mutual Exclusion](#lock--mutual-exclusion)
  - [RLock — Re-Entrant Lock](#rlock--re-entrant-lock)
  - [Semaphore — Rate Limiting / Pool](#semaphore--rate-limiting--pool)
  - [Event — Signal Between Threads](#event--signal-between-threads)
  - [Condition — Notify Specific Waiters](#condition--notify-specific-waiters)
  - [Barrier — Synchronize N Threads at a Point](#barrier--synchronize-n-threads-at-a-point)
- [6. Thread-Safe Communication — `queue.Queue`](#6-thread-safe-communication--queuequeue)
- [7. Multiprocessing — CPU-Bound Parallelism](#7-multiprocessing--cpu-bound-parallelism)
  - [Process vs Thread](#process-vs-thread)
  - [Sharing Data Between Processes](#sharing-data-between-processes)
- [8. asyncio — Cooperative Concurrency](#8-asyncio--cooperative-concurrency)
  - [Core Concepts](#core-concepts)
  - [The Event Loop](#the-event-loop)
  - [Running Multiple Coroutines Concurrently](#running-multiple-coroutines-concurrently)
  - [asyncio Synchronization](#asyncio-synchronization)
- [9. `concurrent.futures` — Unified Interface](#9-concurrentfutures--unified-interface)
- [10. Choosing the Right Model](#10-choosing-the-right-model)
- [11. Producer-Consumer Pattern](#11-producer-consumer-pattern)
- [12. Deadlock — When Threads Block Forever](#12-deadlock--when-threads-block-forever)
- [13. Common Gotchas](#13-common-gotchas)
  - [Gotcha 1 — CPU-bound threads don't speed up](#gotcha-1--cpu-bound-threads-dont-speed-up)
  - [Gotcha 2 — Mutable default arguments in threaded code](#gotcha-2--mutable-default-arguments-in-threaded-code)
  - [Gotcha 3 — Starting event loop from inside event loop](#gotcha-3--starting-event-loop-from-inside-event-loop)
  - [Gotcha 4 — Blocking call in async code](#gotcha-4--blocking-call-in-async-code)
  - [Gotcha 5 — Thread-local state vs shared state](#gotcha-5--thread-local-state-vs-shared-state)
  - [🔥 Summary](#-summary)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
GIL and its implications · `threading.Thread` · `ThreadPoolExecutor` · `asyncio` basics (`async def`, `await`, `asyncio.gather`) · I/O-bound vs CPU-bound decision

**Should Learn** — Important for real projects, comes up regularly:
`ProcessPoolExecutor` · `asyncio.create_task` · `asyncio.Queue` · `threading.Lock` · `asyncio.Semaphore`

**Good to Know** — Useful in specific situations:
`asyncio.TaskGroup` (Python 3.11+) · `asyncio.timeout()` · Task cancellation · `asyncio.shield()`

**Reference** — Know it exists, look up when needed:
Event loop policies · `asyncio.Barrier` · Multiprocessing managers · Zombie processes · Distributed task queues (Celery)

---

<a id="the-problem-10-api-calls-20-seconds"></a>
# 🎬 The Problem: 10 API Calls, 20 Seconds

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

<a id="1-concurrency-vs-parallelism--the-critical-distinction"></a>
# 1. Concurrency vs Parallelism — The Critical Distinction

Think of a single chef preparing a multi-course meal. While the pasta is boiling (waiting — I/O), they chop vegetables (another task). The boiling and chopping overlap in time — that's **concurrency**: one person, multiple tasks interleaved. Now a second chef arrives and makes the sauce at the exact same moment — that's **parallelism**: two people actually cooking simultaneously. Concurrency is about managing overlap; parallelism is about true simultaneity.

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

💡 **Hint:** The biggest mistake in Python concurrency is using threads for CPU-heavy work. Due to the GIL (next section), Python threads cannot truly parallelize computation — they can only overlap I/O waits.

> [↑ Back to Top](#top)

---

<a id="2-the-gil--pythons-most-misunderstood-feature"></a>
# 2. The GIL — Python's Most Misunderstood Feature

Imagine a shared notepad in a library with only one pen. Even if 8 people sit at 8 desks, only the person holding the pen can write at any given moment. Python's GIL (Global Interpreter Lock) is that rule: only one thread can execute Python bytecode at a time, even on an 8-core machine. This shocks people who expect threads to speed up everything — they do speed up I/O waits, but not CPU computation.

```
Without GIL (conceptual):
  Core 1: Thread A executes Python
  Core 2: Thread B executes Python simultaneously
  → Both modifying same object → reference count corrupted → crash

With GIL (reality in CPython):
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
- Every ~5ms (`sys.getswitchinterval()`) — forced context switch

⚠️ **Common mistake — assuming threads parallelize Python CPU work:** Threads in Python do NOT make heavy computation faster. They make I/O-bound work faster by overlapping waits. For computation, you need multiprocessing.

📝 **Practice:** [Q2 — GIL: I/O-bound vs CPU-bound](./practice.md#q2--gil--io-bound-threads-speed-up-cpu-bound-dont) · [Q9 — GIL explanation](./practice.md#q9--threading--gil-why-threading-doesnt-help-cpu-work)

<a id="the-gil--global-interpreter-lock"></a>
## The GIL — Global Interpreter Lock

The GIL exists because CPython's memory management uses [reference counting](../01.1_memory_management/theory.md) — every Python object tracks how many things point to it. Without the GIL, two threads could simultaneously modify a reference count, causing the count to go negative and free memory that's still in use. The GIL is the blunt but effective fix: serialize all bytecode execution, eliminating the race on reference counts entirely.

```
With GIL (reality in CPython):
  Core 1: Thread A ████░░░░████░░░░████░░░░████░░░░
  Core 2: Thread B ░░░░████░░░░████░░░░████░░░░████
                        ↑
                   Only one holds GIL at a time
                   Other waits, even on separate core
```

**What the GIL means for you:**

```
CPU-bound task (heavy computation):
  threading → NOT faster (GIL prevents parallel execution)
  multiprocessing → FASTER (each process has its own GIL)

I/O-bound task (network, disk, sleep):
  threading → FASTER (GIL is released during I/O waits)
  asyncio   → FASTER (no GIL needed — single thread, no context switch)
```

🔍 **Good to Know:** Python 3.13 introduced an experimental "no-GIL" build (`--disable-gil`). It's not the default yet, but it signals Python is moving toward true thread-level parallelism for CPU work in the future.

<a id="decision-tree-which-concurrency-model"></a>
## Decision Tree: Which Concurrency Model?

Before writing any concurrent code, ask one question: is my bottleneck **waiting** (I/O-bound) or **calculating** (CPU-bound)? The answer determines everything else.

```
START: What is your task?
         │
         ├─ I/O-bound (network, file, DB, sleep)?
         │       │
         │       ├─ Many connections, high concurrency needed?
         │       │       └─ asyncio  (single thread, event loop, no context switch overhead)
         │       │
         │       └─ Simpler use case, already using blocking libraries?
         │               └─ threading  (simpler, GIL released during I/O)
         │
         └─ CPU-bound (heavy math, image processing, ML inference)?
                 │
                 ├─ Task is parallelizable across data?
                 │       └─ multiprocessing  (each process = own GIL, true parallel)
                 │
                 └─ Mix of CPU-bound and I/O-bound?
                         └─ asyncio + ProcessPoolExecutor
                            (async event loop + separate processes for CPU work)
```

**Quick reference:**

```
┌──────────────────┬──────────────────────┬──────────────────────┐
│                  │  I/O-bound           │  CPU-bound           │
├──────────────────┼──────────────────────┼──────────────────────┤
│  threading       │  ✓ Good              │  ✗ GIL blocks        │
│  multiprocessing │  ✗ Overkill          │  ✓ True parallel     │
│  asyncio         │  ✓ Best for scale    │  ✗ Single thread     │
└──────────────────┴──────────────────────┴──────────────────────┘
```

📝 **Deep dive →** [01_threading/theory.md](./01_threading/theory.md)

<a id="asyncio-event-loop--cooperative-not-preemptive"></a>
## asyncio Event Loop — Cooperative, Not Preemptive

There are two ways to share a single worker between multiple tasks. The first is **preemptive**: a boss (OS) taps the worker on the shoulder mid-sentence and says "stop, someone else's turn." The second is **cooperative**: the worker finishes their sentence, then says "I'm waiting for a reply — go help someone else." Threads are preemptive (the OS interrupts them). asyncio is cooperative (tasks voluntarily yield at `await`).

```
THREADING (preemptive):
  Task A: ────────────┤OS interrupt├────────────
  Task B:             ────────────┤OS interrupt├─

  OS decides when to switch. Can happen in the middle of anything.

ASYNCIO (cooperative):
  Task A: ──────────── await ──────────────────
  Task B:              ──────── await ──────────

  Task A runs until it hits 'await'.
  Then the event loop gives control to Task B.
  Task A resumes when its awaited operation completes.
```

**Key insight:** With asyncio, context switches only happen at `await` points. No surprise interruptions. No race conditions from switching mid-operation. This is why asyncio can handle thousands of connections with very low overhead — no thread stacks, no context switch cost, no locking needed.

```python
import asyncio

async def fetch(url):
    # Runs until it hits 'await' — then event loop runs other tasks
    response = await aiohttp.get(url)   # ← yields control here
    return await response.text()        # ← yields again

async def main():
    # These run CONCURRENTLY — not sequentially
    results = await asyncio.gather(
        fetch("http://example.com/1"),
        fetch("http://example.com/2"),
        fetch("http://example.com/3"),
    )
```

⚠️ **Common mistake — a task that never awaits blocks everything:** If a coroutine does heavy CPU work without any `await`, it holds the event loop hostage. No other task runs until it finishes. Always `await asyncio.sleep(0)` periodically in long CPU loops, or offload CPU work to a thread pool.

> [↑ Back to Top](#top)

---

<a id="3-threading--io-bound-concurrency"></a>
# 3. Threading — I/O-Bound Concurrency

Think of a restaurant with multiple waiters covering different tables. Each waiter takes an order, sends it to the kitchen (I/O operation — waiting for the food), and while waiting doesn't stand frozen at that table — they go serve another. Threads work the same way: each thread handles one task, and while it's blocked waiting for I/O (network, disk, database), Python can run other threads. The key word is "waiting" — threads only help when your code spends time waiting, not calculating.

<a id="basic-thread"></a>
## Basic Thread

The lowest-level way to run a function in a separate thread. You create a `Thread` object, give it a target function, and call `start()`. Use `join()` to wait for it to finish before continuing.

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

💡 **Hint:** `daemon=True` means the thread will be killed automatically when the main program exits. Without it, your program won't exit until all threads finish — which can cause hangs if a thread is stuck.

<a id="threadpoolexecutor--the-modern-way"></a>
## ThreadPoolExecutor — The Modern Way

Managing individual threads manually (start, join, handle exceptions) gets messy fast. `ThreadPoolExecutor` manages a pool of reusable threads for you. You submit work, and the pool handles scheduling, reuse, and cleanup. This is what you should use in production.

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

# executor.map — simple parallel map:
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(download, urls))
```

⚠️ **Common mistake — ignoring exceptions from futures:** If a thread raises an exception, `f.result()` re-raises it. If you never call `f.result()`, the exception is silently swallowed. Always handle `future.result()` in a try/except.

<a id="thread-lifecycle"></a>
## Thread Lifecycle

Understanding how to start, check, and stop threads prevents hanging programs and zombie threads.

```python
t = threading.Thread(target=func, args=(arg1,), kwargs={"key": val})
t.daemon = True    # daemon threads die when main thread exits (don't block shutdown)
t.start()          # schedule for execution
t.is_alive()       # True if running
t.join(timeout=5)  # wait up to 5 seconds
```

🔍 **Good to Know:** There is no safe way to forcefully kill a Python thread from outside — you can only signal it to stop (via an Event or a flag). Design threads to check a stop condition regularly rather than running forever.

📝 **Practice:** [Q1 — basic-thread](./practice.md#q1--threading--start-join-daemon) · [Q3 — ThreadPoolExecutor](./practice.md#q3--threadpoolexecutor--submit-map-context-manager)

> [↑ Back to Top](#top)

---

<a id="4-race-conditions--when-threads-collide"></a>
# 4. Race Conditions — When Threads Collide

Two people are on a bank's website at the same moment, both withdrawing from the same account that has $800. Person A checks: "Is $500 available? Yes." Person B checks: "Is $700 available? Yes." Both get approved. Both get their money. But $500 + $700 = $1,200 — the account only had $800. Neither check was wrong in isolation; the problem is the interleaving. That's a race condition: the outcome depends on the unpredictable timing of thread execution.

```python
import threading

balance = 1000

def withdraw(amount):
    global balance
    if balance >= amount:    # thread A checks: 1000 >= 500 → True
                             # thread B checks: 1000 >= 700 → True
        balance -= amount    # thread A: 1000 - 500 = 500
                             # thread B: 1000 - 700 = 300  ← WRONG!

threads = [
    threading.Thread(target=withdraw, args=(500,)),
    threading.Thread(target=withdraw, args=(700,)),
]
for t in threads: t.start()
for t in threads: t.join()

print(balance)   # could be 500, 300, or -200 depending on timing
```

**The compound operation problem — why even `counter += 1` is not safe:**
```
counter += 1  compiles to:
  LOAD_GLOBAL counter   ← Thread A loaded 0
                        ← CONTEXT SWITCH: Thread B runs
                        ← Thread B: LOAD=0, ADD=1, STORE → counter=1
                        ← CONTEXT SWITCH back to Thread A
  BINARY_ADD 1          ← Thread A: ADD 0+1 = 1
  STORE_GLOBAL counter  ← Thread A: STORE 1  ← lost Thread B's increment!
```

⚠️ **Common mistake — assuming the GIL makes your code thread-safe:** The GIL prevents crashes from reference count corruption, but it does NOT prevent race conditions in your application logic. Compound operations (`+=`, `dict[key] += 1`, check-then-act) are still unsafe.

💡 **Hint:** To test for race conditions, run your code with many threads and many iterations. Race conditions are timing-dependent — they may not show up until production load.

📝 **Practice:** [Q5 — race-condition](./practice.md#q5--race-condition--spot-and-fix-the-bug)

> [↑ Back to Top](#top)

---

<a id="5-thread-synchronization"></a>
# 5. Thread Synchronization

Going back to the bank — the fix is a "one customer at a time" teller window. Lock the door while serving a customer, unlock when they leave. Python's synchronization primitives are exactly these coordination tools: door locks, numbered tickets, waiting rooms, and signal lights that control how threads take turns accessing shared resources.

<a id="lock--mutual-exclusion"></a>
## Lock — Mutual Exclusion

The most basic synchronization tool. Only one thread can hold the lock at a time. All others block and wait. Use it to protect any shared state that multiple threads read and write.

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
lock.acquire()             # blocks until lock is available
lock.acquire(timeout=5)   # blocks for at most 5 seconds; returns False if timeout
lock.release()
lock.locked()              # True if currently held
```

💡 **Hint:** Always use `with lock:` — it's a [context manager](../12_context_managers/theory.md) that guarantees `release()` even if an exception fires inside the block. Never call `lock.acquire()` / `lock.release()` manually — forgetting the release causes a deadlock.

<a id="rlock--re-entrant-lock"></a>
## RLock — Re-Entrant Lock

A regular `Lock` deadlocks if the same thread tries to acquire it twice (a recursive function calling a locked helper, for example). `RLock` (re-entrant lock) allows the same thread to acquire it multiple times without blocking — it just increments an internal counter, and requires the same number of releases to fully unlock.

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

<a id="semaphore--rate-limiting--pool"></a>
## Semaphore — Rate Limiting / Pool

A lock allows ONE thread at a time. A semaphore allows N threads at a time. Think of it as a parking lot with N spaces — the gate lets you in only if there's a free space, and releases a space when you leave. Use it to cap concurrent access to a limited resource pool (database connections, API rate limits, file handles).

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

⚠️ **Common mistake — using a regular Semaphore when BoundedSemaphore is safer:** A regular `Semaphore` allows releasing more times than acquired, silently inflating its counter past the intended limit. `BoundedSemaphore` raises `ValueError` on over-release, catching bugs early.

<a id="event--signal-between-threads"></a>
## Event — Signal Between Threads

Sometimes one thread needs to wait for another thread to finish some preparation before proceeding — like a runner waiting for the starting pistol. A threading `Event` is that signal: one thread calls `set()` to fire the signal, and all threads waiting on `wait()` are unblocked simultaneously.

```python
ready = threading.Event()

def producer():
    time.sleep(2)
    data = load_data()
    ready.set()   # signal that data is ready

def consumer():
    ready.wait()            # blocks until ready.set() is called
    ready.wait(timeout=10)  # blocks up to 10 seconds
    process(data)

# Event methods:
event.set()          # signal (unblock all waiting threads)
event.clear()        # reset (threads will block again on wait)
event.is_set()       # check current state
event.wait(timeout)  # block until set
```

<a id="condition--notify-specific-waiters"></a>
## Condition — Notify Specific Waiters

An `Event` wakes up ALL waiting threads at once. A `Condition` lets you wake ONE specific waiter (`notify()`) or ALL (`notify_all()`). It also bundles a lock with the wait logic, so you can atomically "check state and wait if not ready" without a separate lock.

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

💡 **Hint:** Always check the condition in a `while` loop, not an `if`. A thread can be woken spuriously (OS-level), so you must re-verify the condition after waking.

<a id="barrier--synchronize-n-threads-at-a-point"></a>
## Barrier — Synchronize N Threads at a Point

A barrier is a meeting point: all N threads must arrive before any of them can continue. Think of a relay race where all runners must reach the exchange zone before the next leg begins.

```python
# All threads wait until N have reached the barrier:
barrier = threading.Barrier(parties=5)

def worker(n):
    prepare_phase(n)
    barrier.wait()    # blocks until all 5 threads reach this point
    execute_phase(n)  # all 5 start execute_phase at approximately the same time
```

📝 **Practice:** [Q6 — synchronization](./practice.md#q6--synchronization--lock-semaphore-event) · [Q90 — thread-safe-counter](../python_practice_questions_100.md#q90--design--thread-safe-counter)

> [↑ Back to Top](#top)

---

<a id="6-thread-safe-communication--queuequeue"></a>
# 6. Thread-Safe Communication — `queue.Queue`

Imagine a post office: a loader piles parcels onto a conveyor belt (producer), and multiple clerks each grab a parcel to process (consumers). The belt is the neutral handoff point — the loader doesn't hand parcels directly to a clerk, and clerks don't fight over the same parcel. `queue.Queue` is that conveyor belt. It's built-in thread safety means you don't need any manual locks — the queue handles all the synchronization internally.

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

⚠️ **Common mistake — forgetting `task_done()`:** If you call `queue.join()` to wait for all work to finish but never call `task_done()` after processing each item, `join()` blocks forever. Every `get()` must be paired with exactly one `task_done()`.

💡 **Hint:** For the sentinel pattern (passing `None` to stop workers), send one `None` per worker thread — not one total. Otherwise the first worker to receive it passes it on, but other workers never get the stop signal.

📝 **Practice:** [Q10 — queue-producer-consumer](./practice.md#q10--queue--producer-consumer-with-sentinel)

> [↑ Back to Top](#top)

---

<a id="7-multiprocessing--cpu-bound-parallelism"></a>
# 7. Multiprocessing — CPU-Bound Parallelism

Threading is one chef juggling multiple tasks — but the GIL means only one task gets CPU time at any moment, no matter how many cores your machine has. Multiprocessing is like hiring eight entirely separate chefs, each with their own kitchen, ingredients, and recipe card. No sharing, no GIL, true simultaneous cooking. The tradeoff: each kitchen is expensive to set up (process startup time) and communicating between kitchens requires passing messages over a wall (IPC), not just handing something across a table.

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

<a id="process-vs-thread"></a>
## Process vs Thread

Choosing between processes and threads comes down to one question: do you need the GIL bypassed (CPU work) or just I/O overlap (waiting work)? Processes are heavier but truly parallel; threads are lighter but GIL-constrained for CPU tasks.

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

⚠️ **Common mistake — spawning too many processes:** More processes than CPU cores does not help and often hurts (context switching overhead). A good starting point is `cpu_count()` processes for CPU-bound work. For I/O-bound work, use threads or asyncio instead — processes are overkill.

<a id="sharing-data-between-processes"></a>
## Sharing Data Between Processes

Processes don't share memory by default — each has its own copy. To share data, you must use explicit IPC mechanisms. `Value` and `Array` use shared memory (fast, limited to simple C types). `Manager` creates a server process that proxies shared objects (flexible, slower).

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

⚠️ **Common mistake — passing non-picklable objects to processes:** Multiprocessing uses `pickle` to serialize data sent between processes. Lambda functions, file handles, database connections, and many class instances cannot be pickled. If your worker function needs one of these, you must reconstruct it inside the worker.

🔍 **Good to Know:** On Unix, `multiprocessing` defaults to `fork` (copies parent process memory). On Windows and macOS (Python 3.8+), it defaults to `spawn` (starts a fresh Python interpreter). This means the `if __name__ == "__main__":` guard is required on those platforms.

📝 **Practice:** [Q8 — ProcessPoolExecutor](./practice.md#q8--processpoolexecutor--parallel-cpu-work) · [Q84 — compare-process-thread-coroutine](../python_practice_questions_100.md#q84--interview--compare-process-thread-coroutine)

> [↑ Back to Top](#top)

---

<a id="8-asyncio--cooperative-concurrency"></a>
# 8. asyncio — Cooperative Concurrency

Imagine a maître d' at a busy restaurant. They take table 1's order, send it to the kitchen (I/O operation — waiting), then immediately walk to table 2, take their order, send it, then check back on table 1. One person, multiple conversations in flight at the same time — but they're never simultaneously at two tables. That's asyncio: a single thread, many tasks, each one voluntarily pausing at an `await` point to let the others run. No threads, no GIL concerns, no context switch overhead.

📝 **Deep dive →** [03_asyncio/theory.md](./03_asyncio/theory.md)

<a id="core-concepts"></a>
## Core Concepts

Three things to understand before writing any async code: a **coroutine** is an async function that doesn't run when you call it — it returns a coroutine object. A **task** is a coroutine that has been scheduled on the event loop. `asyncio.run()` is the entry point that creates the event loop and runs your top-level coroutine.

```python
import asyncio

# coroutine: an async function (doesn't run immediately when called)
async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# calling fetch(url) returns a coroutine OBJECT, not the result:
coro = fetch("http://api.com/data")   # nothing runs yet

# run the coroutine — creates event loop, runs it, closes it:
result = asyncio.run(fetch("http://api.com/data"))

# create a Task (schedules coroutine on event loop, starts immediately):
task = asyncio.create_task(fetch("http://api.com/data"))
result = await task
```

⚠️ **Common mistake — calling a coroutine without `await`:** `fetch("http://api.com")` returns a coroutine object. Nothing runs. If you forget `await`, you get a `RuntimeWarning: coroutine was never awaited` and your function silently does nothing.

<a id="the-event-loop"></a>
## The Event Loop

The event loop is asyncio's engine — a single thread that keeps looping, picking up tasks that are ready to run, suspending them when they hit `await`, and resuming them when their I/O completes. Understanding this loop explains why blocking calls (like `time.sleep()`) are so dangerous in async code: they freeze the loop and starve every other task.

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

💡 **Hint:** `asyncio.run()` is the correct entry point in Python 3.7+. Avoid manually creating and managing event loops with `asyncio.get_event_loop()` — it's the old API and has subtle issues in nested contexts.

<a id="running-multiple-coroutines-concurrently"></a>
## Running Multiple Coroutines Concurrently

The power of asyncio is running many coroutines at once. `asyncio.gather()` is the most common tool — it starts all coroutines simultaneously and waits for all of them to finish. `create_task()` starts a coroutine in the background so you can do other work and await it later.

```python
import asyncio, aiohttp

# gather: run all concurrently, wait for all:
async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in urls]
        results = await asyncio.gather(*tasks)   # all start immediately
        return results

# gather with error handling (returns exceptions instead of raising):
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

# wait: fine-grained control over completion:
done, pending = await asyncio.wait(tasks, timeout=5.0)
for task in pending:
    task.cancel()   # cancel tasks that didn't finish in time
```

⚠️ **Common mistake — `gather` vs sequential `await`:** `await coro1(); await coro2()` runs them one after the other (sequential). `await asyncio.gather(coro1(), coro2())` runs them concurrently. This is the single most common asyncio performance mistake.

<a id="asyncio-synchronization"></a>
## asyncio Synchronization

asyncio has its own versions of all the threading synchronization primitives — but these are non-blocking. They yield to the event loop instead of blocking the thread, so other coroutines can run while one is waiting.

```python
# asyncio sync primitives (non-blocking — yield to event loop):
lock      = asyncio.Lock()
event     = asyncio.Event()
semaphore = asyncio.Semaphore(10)
queue     = asyncio.Queue(maxsize=100)

# Lock (same semantics as threading.Lock):
async with lock:
    await critical_section()

# Semaphore (rate limiting — max 10 concurrent):
async with semaphore:
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

⚠️ **Common mistake — using `threading.Lock` inside async code:** `threading.Lock` blocks the entire thread. Inside an async function, `async with asyncio.Lock()` is correct — it yields to the event loop when waiting, not blocks it.

📝 **Practice:** [Q13–Q19 — asyncio fundamentals](./practice.md#asyncio-basics-q13q19) · [Q55 — asyncio-await](../python_practice_questions_100.md#q55--logical--asyncio-await) · [Q56 — blocking-in-async](../python_practice_questions_100.md#q56--critical--blocking-in-async)

> [↑ Back to Top](#top)

---

<a id="9-concurrentfutures--unified-interface"></a>
# 9. `concurrent.futures` — Unified Interface

You have two types of workers: I/O workers (waiters who spend time waiting for the kitchen) and CPU workers (chefs doing actual cooking). Historically, you'd use different code for threads vs processes. `concurrent.futures` gives you one standardized "hire workers" interface that works for both — you just switch between `ThreadPoolExecutor` and `ProcessPoolExecutor`, and the entire API stays the same.

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed, wait, FIRST_COMPLETED

def process(item):
    return item * 2

# Thread pool (I/O-bound) — identical API to ProcessPoolExecutor:
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(process, i) for i in range(100)]
    for f in as_completed(futures):
        result = f.result()   # raises exception if task failed

# Process pool (CPU-bound) — just swap the class:
with ProcessPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(process, range(100)))

# Future methods:
f = executor.submit(func, arg)
f.result(timeout=5)      # block and return result; re-raises exception if failed
f.exception()            # return exception if failed, None if succeeded
f.done()                 # True if completed (success or failure)
f.cancel()               # cancel if not yet running
f.add_done_callback(fn)  # callback when future completes

# Wait for subset of futures:
done, not_done = wait(futures, timeout=10, return_when=FIRST_COMPLETED)
```

💡 **Hint:** `executor.map(fn, items)` is the simplest API — behaves like `map()` but runs in parallel. Results come back in the same order as inputs. Use `as_completed()` when you want to process results as they finish (unordered but faster to start acting on).

🔍 **Good to Know:** `executor.map()` raises the first exception it encounters when you iterate the results. `executor.submit()` + `f.result()` lets you handle each future's exception individually.

📝 **Practice:** [Q20–Q24 — concurrent.futures](./practice.md#concurrentfutures-q20q24)

> [↑ Back to Top](#top)

---

<a id="10-choosing-the-right-model"></a>
# 10. Choosing the Right Model

Choosing the wrong concurrency tool is like hiring delivery drivers to run a marathon — technically possible, but you're wasting their strengths and getting worse results. The right choice depends entirely on whether your bottleneck is **waiting** (I/O) or **calculating** (CPU). Get this question wrong and you'll add complexity without gaining speed.

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
  Simple scripts   → concurrent.futures (auto-selects)
```

> [↑ Back to Top](#top)

---

<a id="11-producer-consumer-pattern"></a>
# 11. Producer-Consumer Pattern

Think of a factory assembly line: a stamping machine (producer) stamps out parts at a steady rate, and several assembly workers (consumers) each grab a part and build it into the final product. The machine doesn't wait for a worker to be free before stamping — it drops the part onto a conveyor belt. Workers grab from the belt when ready. The belt (queue) **decouples** their speeds — the producer can run faster or slower than consumers without either blocking the other directly.

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

💡 **Hint:** The number of workers is a tuning parameter. For I/O-bound consumers, you can often set it to 20–100. For CPU-bound consumers, cap it at `cpu_count()` (and consider using processes instead of threads).

📝 **Practice:** [Q11 — producer-consumer](./practice.md#q11--producer-consumer--threading-queue)

> [↑ Back to Top](#top)

---

<a id="12-deadlock--when-threads-block-forever"></a>
# 12. Deadlock — When Threads Block Forever

Two people meet on a narrow bridge going opposite directions. Person A says "I'll move when you move." Person B says "I'll move when you move." Neither moves. Forever. That's a deadlock: Thread A holds Lock 1 and wants Lock 2, Thread B holds Lock 2 and wants Lock 1 — both frozen, waiting for the other to release. No exceptions, no errors, just a silent hang.

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
# 1. Consistent lock ordering — ALWAYS acquire in same order everywhere:
def thread_1():
    with lock_a:   # always A before B
        with lock_b:
            ...

def thread_2():
    with lock_a:   # always A before B — same order as thread_1
        with lock_b:
            ...

# 2. Lock timeout — surface deadlocks as explicit errors:
acquired = lock.acquire(timeout=5)
if not acquired:
    raise TimeoutError("Could not acquire lock")

# 3. Try-lock (non-blocking) — fail fast instead of waiting:
if lock.acquire(blocking=False):
    try:
        ...
    finally:
        lock.release()
else:
    # couldn't acquire — back off and retry
```

⚠️ **Common mistake — lock ordering inconsistency:** Deadlocks only occur when threads acquire the same locks in different orders. Audit your entire codebase for lock acquisition order — one function acquiring A then B and another acquiring B then A is all it takes.

💡 **Hint:** Python's `threading` module doesn't detect deadlocks. Use lock timeouts and monitoring (`threading.enumerate()`) in production to surface hangs as actionable errors rather than frozen processes.

📝 **Practice:** [Q12 — deadlock](./practice.md#q12--deadlock--identify-and-fix)

> [↑ Back to Top](#top)

---

<a id="13-common-gotchas"></a>
# 13. Common Gotchas

Concurrency bugs are some of the hardest to reproduce — they depend on timing, only surface under load, and often disappear when you add logging (which changes timing). These five gotchas appear repeatedly in production Python and in technical interviews.

<a id="gotcha-1--cpu-bound-threads-dont-speed-up"></a>
## Gotcha 1 — CPU-bound threads don't speed up

⚠️ The GIL prevents Python threads from running Python bytecode in parallel. Four CPU-bound threads on a 4-core machine still run on a single core's worth of Python execution.

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

<a id="gotcha-2--mutable-default-arguments-in-threaded-code"></a>
## Gotcha 2 — Mutable default arguments in threaded code

⚠️ Mutable default arguments are shared across all calls. In threaded code, multiple threads appending to the same default list creates a race condition and data corruption that's very hard to trace.

```python
# ❌ results accumulates across ALL calls and is not thread-safe:
def worker(items, results=[]):
    results.append(process(items))
    return results

# ✅ Use None and create fresh list each call:
def worker(items, results=None):
    if results is None:
        results = []
    results.append(process(items))
    return results
```

<a id="gotcha-3--starting-event-loop-from-inside-event-loop"></a>
## Gotcha 3 — Starting event loop from inside event loop

⚠️ `asyncio.run()` creates a new event loop. If you're already inside a running event loop (e.g., in a Jupyter notebook or an async function), calling `asyncio.run()` again raises `RuntimeError: This event loop is already running`.

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

💡 **Hint:** In Jupyter notebooks, use `await coro()` directly (Jupyter runs its own event loop) or install `nest_asyncio` to patch this behavior.

<a id="gotcha-4--blocking-call-in-async-code"></a>
## Gotcha 4 — Blocking call in async code

⚠️ Any synchronous blocking call inside an async function freezes the entire event loop. No other coroutine can run until it completes. This is the number one asyncio performance killer — a single `time.sleep(2)` in a coroutine stalls all concurrent connections.

```python
# ❌ Blocks the ENTIRE event loop:
async def bad():
    time.sleep(2)                   # ← synchronous sleep freezes everything
    data = open("huge.txt").read()  # ← synchronous I/O freezes everything

# ✅ Use async equivalents:
async def good():
    await asyncio.sleep(2)                    # yields to event loop
    async with aiofiles.open("huge.txt") as f:
        data = await f.read()

# ✅ Run blocking code in a thread pool (offloads it from event loop):
async def also_good():
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, blocking_read, "huge.txt")
```

<a id="gotcha-5--thread-local-state-vs-shared-state"></a>
## Gotcha 5 — Thread-local state vs shared state

⚠️ Module-level variables and instance variables are shared between all threads. If you store per-request state (user ID, request ID, database session) in a global or class variable, threads will overwrite each other's state under concurrent load.

```python
# ❌ Shared state — all threads see it and overwrite each other:
current_user = None   # ← race condition

# ✅ Thread-local state — each thread has its own copy:
local = threading.local()

def worker():
    local.user_id = get_current_user()   # each thread has its own .user_id
    process_request()

def process_request():
    print(local.user_id)   # reads THIS thread's value, not another thread's
```

🔍 **Good to Know:** In asyncio, use `contextvars.ContextVar` instead of `threading.local()` — it provides task-local storage that works correctly with async context switches.

📝 **Practice:** [Q25 — concurrency-gotchas](./practice.md#q25--concurrency-gotchas--identify-and-fix)

<a id="-summary"></a>
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

> [↑ Back to Top](#top)

---

## 🔁 Navigation

**[🏠 Back to README](../../README.md)**

| | |
|---|---|
| ⬅ Prev Module | [12 — Context Managers](../12_context_managers/theory.md) |
| ➡ Next Module | [14 — Type Hints & Pydantic](../14_type_hints_and_pydantic/theory.md) |

**This folder:**
[theory.md](./theory.md) · [cheetsheet.md](./cheetsheet.md) · [interview.md](./interview.md) · [practice.md](./practice.md)

**Subfolders:**
[01_threading/theory.md](./01_threading/theory.md) · [02_multiprocessing/theory.md](./02_multiprocessing/theory.md) · [03_asyncio/theory.md](./03_asyncio/theory.md)

**Related modules:**
[12 — Context Managers](../12_context_managers/theory.md) · [11 — Generators & Iterators](../11_generators_iterators/theory.md) · [01.1 — Memory Management](../01.1_memory_management/theory.md) · [24 — Async Python for AI](../24_async_python_for_ai/theory.md)

**Jump to specific topics:**
[GIL deep dive](../01.1_memory_management/theory.md) · [Context managers with locks](../12_context_managers/theory.md#2-the-context-manager-protocol) · [asyncio deep dive](./03_asyncio/theory.md) · [threading deep dive](./01_threading/theory.md)

