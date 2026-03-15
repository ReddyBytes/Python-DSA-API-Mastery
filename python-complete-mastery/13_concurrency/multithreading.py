"""
13_concurrency/multithreading.py
==================================
CONCEPT: Multithreading — running multiple threads within one process.
WHY THIS MATTERS: Threads share memory and are ideal for I/O-bound work
(network calls, file reads, DB queries) where the bottleneck is waiting,
not CPU. Python's GIL means only ONE thread executes Python bytecode at a time,
so threads do NOT speed up CPU-bound code. Understanding this distinction
prevents a very common performance mistake.

Prerequisite: Modules 01–12
"""

import threading
import time
import queue
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# =============================================================================
# SECTION 1: Thread basics — creating and starting threads
# =============================================================================

# CONCEPT: threading.Thread wraps a callable and runs it in a new OS thread.
# .start() schedules the thread; .join() blocks until it finishes.
# Threads share the process's memory — same variables, objects, heap.

print("=== Section 1: Thread Basics ===")

def download_file(url: str, delay: float) -> str:
    """Simulate downloading a file (I/O-bound — mostly waiting)."""
    print(f"  [Thread {threading.current_thread().name}] Starting download: {url}")
    time.sleep(delay)   # simulate network latency
    print(f"  [Thread {threading.current_thread().name}] Done: {url}")
    return f"content_of_{url}"


# Sequential — total time = sum of all delays
print("Sequential downloads:")
start = time.perf_counter()
for url, delay in [("file_a.zip", 0.3), ("file_b.zip", 0.2), ("file_c.zip", 0.1)]:
    download_file(url, delay)
print(f"  Sequential time: {time.perf_counter() - start:.2f}s")

# Threaded — total time ≈ max(delays) because they run concurrently
print("\nConcurrent downloads:")
start = time.perf_counter()
threads = []
for url, delay in [("file_a.zip", 0.3), ("file_b.zip", 0.2), ("file_c.zip", 0.1)]:
    t = threading.Thread(
        target=download_file,
        args=(url, delay),
        name=f"Worker-{url[:6]}",    # give threads meaningful names for debugging
        daemon=True,                  # daemon threads die when main thread exits
    )
    threads.append(t)
    t.start()   # schedule on OS; main thread continues immediately

for t in threads:
    t.join()    # wait for all threads to complete before proceeding

print(f"  Concurrent time: {time.perf_counter() - start:.2f}s  (should be ~0.3s)")


# =============================================================================
# SECTION 2: The GIL — why threads don't help CPU-bound code
# =============================================================================

# CONCEPT: Python's Global Interpreter Lock (GIL) ensures only ONE thread
# runs Python bytecode at a time. It's released during I/O (sleep, network,
# file read) — that's why threads help I/O-bound code. But for pure Python
# computation, two threads share the lock and can't truly parallelize.
# Use multiprocessing (separate GIL per process) for CPU-bound work.

print("\n=== Section 2: GIL — I/O vs CPU Bound ===")

def cpu_work(n: int) -> int:
    """Pure CPU computation — blocked by GIL."""
    total = 0
    for i in range(n):
        total += i * i
    return total

def io_work(n: int) -> None:
    """I/O simulation — releases GIL during sleep."""
    for _ in range(n):
        time.sleep(0.001)   # GIL is released during sleep!

N = 500_000

# CPU-bound: threading is slower than sequential (GIL contention + overhead)
start = time.perf_counter()
cpu_work(N)
cpu_work(N)
seq_cpu = time.perf_counter() - start

start = time.perf_counter()
t1 = threading.Thread(target=cpu_work, args=(N,))
t2 = threading.Thread(target=cpu_work, args=(N,))
t1.start(); t2.start(); t1.join(); t2.join()
threaded_cpu = time.perf_counter() - start

print(f"CPU-bound sequential: {seq_cpu:.3f}s")
print(f"CPU-bound threaded:   {threaded_cpu:.3f}s  (no speedup — GIL!)")

# I/O-bound: threading helps because GIL is released during I/O
n_io = 10
start = time.perf_counter()
io_work(n_io); io_work(n_io)
seq_io = time.perf_counter() - start

start = time.perf_counter()
t1 = threading.Thread(target=io_work, args=(n_io,))
t2 = threading.Thread(target=io_work, args=(n_io,))
t1.start(); t2.start(); t1.join(); t2.join()
threaded_io = time.perf_counter() - start

print(f"\nI/O-bound sequential: {seq_io:.3f}s")
print(f"I/O-bound threaded:   {threaded_io:.3f}s  (2x speedup — GIL released!)")


# =============================================================================
# SECTION 3: Race conditions and thread safety with Locks
# =============================================================================

# CONCEPT: Threads share memory. If two threads read-modify-write the same
# variable without coordination, the result is unpredictable (race condition).
# A Lock ensures only one thread can execute the protected block at a time.
# RULE: if two threads access the same mutable state, protect it with a Lock.

print("\n=== Section 3: Race Conditions and Locks ===")

# UNSAFE counter — demonstrates race condition
class UnsafeCounter:
    def __init__(self):
        self.value = 0

    def increment(self, times: int):
        for _ in range(times):
            # BUG: read → compute → write is NOT atomic. Another thread can
            # run between the read and write, causing lost updates.
            self.value += 1   # 3 bytecode operations: LOAD, ADD, STORE


# SAFE counter — Lock makes increment atomic
class SafeCounter:
    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()   # reentrant: use RLock if same thread re-acquires

    def increment(self, times: int):
        for _ in range(times):
            with self._lock:   # only ONE thread executes this block at a time
                self.value += 1


def run_counter_threads(counter, n_threads: int = 10, n_each: int = 1000):
    threads = [threading.Thread(target=counter.increment, args=(n_each,))
               for _ in range(n_threads)]
    for t in threads: t.start()
    for t in threads: t.join()
    return counter.value


expected = 10 * 1000

unsafe = UnsafeCounter()
result = run_counter_threads(unsafe)
print(f"Unsafe counter: expected={expected:,}, got={result:,}  {'OK' if result == expected else 'RACE CONDITION LOST UPDATES!'}")

safe = SafeCounter()
result = run_counter_threads(safe)
print(f"Safe counter:   expected={expected:,}, got={result:,}  {'OK' if result == expected else 'BUG'}")


# =============================================================================
# SECTION 4: Threading with return values — using Queue
# =============================================================================

# CONCEPT: Thread.run() returns None — you can't get results directly.
# Solution 1: write results to a shared list/dict (needs a lock or use thread-safe Queue).
# Solution 2: use Queue — thread-safe FIFO, no manual locking needed.
# Solution 3: use ThreadPoolExecutor (see Section 5) — cleanest for most cases.

print("\n=== Section 4: Thread-Safe Queue ===")

def fetch_and_process(task_id: int, result_queue: queue.Queue) -> None:
    """Worker: does I/O work, puts result in the queue."""
    time.sleep(random.uniform(0.05, 0.15))   # simulate variable latency
    result = {"task_id": task_id, "value": task_id * task_id}
    result_queue.put(result)   # Queue.put() is thread-safe; no lock needed


results_q: queue.Queue = queue.Queue()
task_ids = list(range(1, 8))

threads = [
    threading.Thread(target=fetch_and_process, args=(tid, results_q))
    for tid in task_ids
]
for t in threads: t.start()
for t in threads: t.join()

# Drain queue (all threads done, so queue is complete and safe to read)
results = []
while not results_q.empty():
    results.append(results_q.get())

results.sort(key=lambda r: r["task_id"])
print(f"Collected {len(results)} results:")
for r in results:
    print(f"  task {r['task_id']}: {r['value']}")


# =============================================================================
# SECTION 5: ThreadPoolExecutor — the right way for most I/O-bound work
# =============================================================================

# CONCEPT: ThreadPoolExecutor manages a pool of worker threads.
# .submit(fn, *args) → Future: non-blocking, returns immediately.
# .map(fn, items) → iterator of results in submission order.
# as_completed() → yields futures as they finish (fastest first).
# Context manager ensures all threads are cleaned up on exit.

print("\n=== Section 5: ThreadPoolExecutor ===")

def scrape_page(url: str) -> dict:
    """Simulate scraping a web page with variable latency."""
    delay = random.uniform(0.05, 0.2)
    time.sleep(delay)
    return {"url": url, "status": 200, "words": random.randint(100, 5000)}


urls = [f"https://example.com/page/{i}" for i in range(1, 9)]

# .map() — simple, returns results in INPUT order
print("ThreadPoolExecutor.map (ordered results):")
start = time.perf_counter()
with ThreadPoolExecutor(max_workers=4, thread_name_prefix="Scraper") as pool:
    results = list(pool.map(scrape_page, urls))
elapsed = time.perf_counter() - start

for r in results[:3]:
    print(f"  {r['url']}: {r['words']} words")
print(f"  ... fetched {len(results)} pages in {elapsed:.2f}s")


# as_completed() — process results as soon as each finishes (better for dashboards)
print("\nas_completed (arrival order — fastest first):")
start = time.perf_counter()
with ThreadPoolExecutor(max_workers=4) as pool:
    futures = {pool.submit(scrape_page, url): url for url in urls[:4]}

    for future in as_completed(futures):
        url = futures[future]
        result = future.result()   # raises if the thread raised an exception
        print(f"  Finished: {url.split('/')[-1]} → {result['words']} words")

elapsed = time.perf_counter() - start
print(f"  Done in {elapsed:.2f}s")


# =============================================================================
# SECTION 6: Thread-local storage — per-thread state
# =============================================================================

# CONCEPT: threading.local() creates a namespace where each attribute is
# INDEPENDENT per thread. Used for: database connections, request contexts,
# transaction state — anything that should not be shared between threads.

print("\n=== Section 6: Thread-Local Storage ===")

_thread_local = threading.local()

def request_handler(request_id: int) -> None:
    """Each thread gets its own 'current_user' — no sharing, no lock needed."""
    _thread_local.request_id   = request_id
    _thread_local.current_user = f"user_{request_id}"

    time.sleep(random.uniform(0.01, 0.05))   # simulate async work

    # Each thread reads ITS OWN values — not another thread's
    print(f"  Thread-{request_id}: request={_thread_local.request_id}, "
          f"user={_thread_local.current_user}")


threads = [threading.Thread(target=request_handler, args=(i,)) for i in range(1, 6)]
for t in threads: t.start()
for t in threads: t.join()


print("\n=== Multithreading complete ===")
print("Key rules:")
print("  1. Use threads for I/O-bound work (network, disk, DB queries)")
print("  2. Don't use threads for CPU-bound work — GIL prevents parallelism")
print("  3. Protect shared mutable state with Lock / RLock")
print("  4. Prefer ThreadPoolExecutor over manual thread management")
print("  5. Use Queue for safe inter-thread communication")
print("  6. Use threading.local() for per-thread state (DB connections, contexts)")
