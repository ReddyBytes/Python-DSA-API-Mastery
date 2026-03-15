"""
13_concurrency/multiprocessing.py
====================================
CONCEPT: Multiprocessing — spawning separate OS processes, each with its OWN
Python interpreter and memory space.
WHY THIS MATTERS: Each process has its own GIL. True parallel CPU execution is
possible with multiprocessing. Pay the cost: process startup (~50ms), IPC
(inter-process communication) overhead, and no shared memory by default.
Use for: CPU-bound tasks (image processing, data transforms, ML inference,
crypto), anything that needs to max out all CPU cores.

Prerequisite: Modules 01–12
"""

import multiprocessing as mp
import time
import math
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

# Guard required for Windows + "spawn" start method — any code that creates
# processes MUST be inside `if __name__ == "__main__":`.
# On macOS/Linux with "fork", it runs fine without the guard, but the guard
# is always required for portable, production-safe code.

# =============================================================================
# SECTION 1: Process basics — why processes beat threads for CPU work
# =============================================================================

# CONCEPT: multiprocessing.Process is like threading.Thread but creates a
# NEW Python interpreter. The GIL is per-interpreter, so two processes truly
# run Python bytecodes in parallel on separate CPU cores.

print("=== Section 1: Process Basics ===")

def cpu_heavy(n: int) -> int:
    """CPU-bound: compute sum of squares. Maxes out one CPU core."""
    return sum(i * i for i in range(n))


def show_process_info(label: str) -> None:
    print(f"  [{label}] PID={os.getpid()}, parent={os.getppid()}")


if __name__ == "__main__":
    N = 3_000_000

    # Sequential — one core at a time
    start = time.perf_counter()
    r1 = cpu_heavy(N)
    r2 = cpu_heavy(N)
    seq_time = time.perf_counter() - start
    print(f"Sequential: {seq_time:.3f}s")

    # Parallel — two processes on two cores simultaneously
    start = time.perf_counter()
    with mp.Pool(processes=2) as pool:
        results = pool.starmap(cpu_heavy, [(N,), (N,)])
    par_time = time.perf_counter() - start
    print(f"Parallel:   {par_time:.3f}s  (speedup: {seq_time / par_time:.1f}x)")

    # Each process has its own PID
    p1 = mp.Process(target=show_process_info, args=("child-1",))
    p2 = mp.Process(target=show_process_info, args=("child-2",))
    show_process_info("main")
    p1.start(); p2.start()
    p1.join();  p2.join()


# =============================================================================
# SECTION 2: Process Pool — the right tool for parallel CPU work
# =============================================================================

# CONCEPT: mp.Pool manages N worker processes and distributes work items.
# .map(fn, items)        — results in input order; blocks until all done
# .starmap(fn, pairs)    — like map but unpacks tuples as multiple args
# .imap(fn, items)       — lazy iterator of results (memory efficient)
# .apply_async(fn, args) — async single call, returns AsyncResult

print("\n=== Section 2: Process Pool ===")

def is_prime(n: int) -> bool:
    """CPU-bound primality test."""
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def find_primes_in_range(start: int, end: int) -> list:
    """Find all primes in [start, end]. One chunk of work per process."""
    return [n for n in range(start, end) if is_prime(n)]


if __name__ == "__main__":
    LIMIT = 500_000
    CPU_COUNT = mp.cpu_count()
    print(f"  CPU cores available: {CPU_COUNT}")

    # Split work into chunks — one per core
    chunk_size = LIMIT // CPU_COUNT
    ranges = [(i * chunk_size, (i + 1) * chunk_size) for i in range(CPU_COUNT)]
    ranges[-1] = (ranges[-1][0], LIMIT)   # last chunk covers remainder

    start = time.perf_counter()
    with mp.Pool(processes=CPU_COUNT) as pool:
        chunks = pool.starmap(find_primes_in_range, ranges)
    elapsed = time.perf_counter() - start

    # Flatten results from all processes
    all_primes = [p for chunk in chunks for p in chunk]
    print(f"  Primes below {LIMIT:,}: {len(all_primes):,}  (in {elapsed:.2f}s)")
    print(f"  Last 5 primes: {all_primes[-5:]}")


# =============================================================================
# SECTION 3: ProcessPoolExecutor — modern Future-based API
# =============================================================================

# CONCEPT: concurrent.futures.ProcessPoolExecutor is the "modern" process pool.
# Same API as ThreadPoolExecutor — submit() returns Futures.
# Easier to compose with ThreadPoolExecutor in mixed I/O+CPU pipelines.

print("\n=== Section 3: ProcessPoolExecutor ===")

def transform_chunk(data: list) -> dict:
    """CPU-intensive transformation on a data chunk."""
    processed = [math.sqrt(abs(x)) * math.pi for x in data]
    return {
        "input_size":  len(data),
        "output_sum":  sum(processed),
        "output_max":  max(processed),
        "worker_pid":  os.getpid(),
    }


if __name__ == "__main__":
    import random
    random.seed(42)
    full_dataset = [random.uniform(-1000, 1000) for _ in range(200_000)]

    # Split into chunks
    n_workers = min(4, mp.cpu_count())
    chunk_sz   = len(full_dataset) // n_workers
    chunks     = [full_dataset[i*chunk_sz:(i+1)*chunk_sz] for i in range(n_workers)]

    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = [executor.submit(transform_chunk, chunk) for chunk in chunks]
        results = [f.result() for f in as_completed(futures)]

    elapsed = time.perf_counter() - start
    total   = sum(r["output_sum"] for r in results)
    workers = {r["worker_pid"] for r in results}
    print(f"  Processed {len(full_dataset):,} items in {elapsed:.3f}s")
    print(f"  Worker PIDs: {workers}")
    print(f"  Total output sum: {total:,.2f}")


# =============================================================================
# SECTION 4: Inter-process communication — Pipe and Queue
# =============================================================================

# CONCEPT: Processes have SEPARATE memory. To share data you must use IPC:
# mp.Queue  — thread + process safe queue (uses pickle internally)
# mp.Pipe   — bidirectional communication between exactly 2 processes
# mp.Value/Array — shared memory for primitives (no pickling needed)
# NOTE: everything sent through Queue/Pipe is pickled → unpickled. Large
# objects are expensive. Design to minimize IPC (send tasks, return results).

print("\n=== Section 4: Inter-Process Communication ===")

def producer(q: mp.Queue, items: list) -> None:
    """Produce items and put them on the queue."""
    for item in items:
        time.sleep(0.01)   # simulate producing work
        q.put(item)
        print(f"  [Producer] queued: {item}")
    q.put(None)   # sentinel — signals consumer that work is done


def consumer(q: mp.Queue, results: list) -> None:
    """Consume items from the queue until sentinel."""
    while True:
        item = q.get()
        if item is None:
            break
        result = item ** 2   # process the item
        print(f"  [Consumer PID={os.getpid()}] processed: {item} → {result}")


if __name__ == "__main__":
    work_queue: mp.Queue = mp.Queue()
    items = list(range(1, 6))

    p_prod = mp.Process(target=producer, args=(work_queue, items))
    p_cons = mp.Process(target=consumer, args=(work_queue, []))

    p_prod.start(); p_cons.start()
    p_prod.join();  p_cons.join()

    # Pipe example: bidirectional channel between two processes
    parent_conn, child_conn = mp.Pipe(duplex=True)

    def worker_with_pipe(conn: mp.connection.Connection) -> None:
        msg = conn.recv()
        conn.send(f"Worker processed: {msg.upper()}")
        conn.close()

    p = mp.Process(target=worker_with_pipe, args=(child_conn,))
    p.start()
    parent_conn.send("hello from main process")
    reply = parent_conn.recv()
    p.join()
    print(f"\n  Pipe reply: {reply}")


# =============================================================================
# SECTION 5: Shared memory — mp.Value and mp.Array
# =============================================================================

# CONCEPT: Shared memory avoids the pickle overhead of Queue/Pipe.
# mp.Value wraps a single C scalar. mp.Array wraps a C array.
# Both live in shared memory — writes in one process are visible in another.
# BUT: they need explicit locking (Value has a built-in lock; Array uses ctypes).
# For complex structures, use multiprocessing.Manager() (slower, but flexible).

print("\n=== Section 5: Shared Memory ===")

def increment_shared(counter: mp.Value, lock: mp.Lock, n: int) -> None:
    """Safely increment shared counter n times."""
    for _ in range(n):
        with lock:   # explicit lock prevents race conditions between processes
            counter.value += 1


if __name__ == "__main__":
    shared_counter = mp.Value("i", 0)   # "i" = C int, initial value 0
    lock = mp.Lock()
    n_procs, n_each = 4, 1000

    procs = [
        mp.Process(target=increment_shared, args=(shared_counter, lock, n_each))
        for _ in range(n_procs)
    ]
    for p in procs: p.start()
    for p in procs: p.join()

    expected = n_procs * n_each
    print(f"  Expected: {expected:,}, got: {shared_counter.value:,}  "
          f"{'OK' if shared_counter.value == expected else 'BUG'}")

    # mp.Array for bulk data — direct C array in shared memory
    arr = mp.Array("d", [1.0, 2.0, 3.0, 4.0, 5.0])   # "d" = C double
    print(f"  Shared array: {list(arr)}")


# =============================================================================
# SECTION 6: When to use threads vs processes vs async
# =============================================================================

print("\n=== Section 6: Decision Guide ===")
guide = """
┌─────────────────────────────────────────────────────────────────────────┐
│ Task type           │ Best tool              │ Why                      │
├─────────────────────┼────────────────────────┼──────────────────────────┤
│ I/O-bound           │ asyncio (single thread) │ No overhead, scales best │
│ I/O-bound (sync lib)│ ThreadPoolExecutor      │ Easy, GIL released on I/O│
│ CPU-bound           │ ProcessPoolExecutor     │ True parallelism, own GIL│
│ Mixed I/O + CPU     │ asyncio + executor      │ run_in_executor() bridges│
│ Large data parallel │ multiprocessing.Pool    │ Chunked starmap          │
│ Real-time streaming │ Queue + processes       │ Producer/consumer pattern│
└─────────────────────┴────────────────────────┴──────────────────────────┘

Costs to be aware of:
  Process startup:   ~50-100ms — avoid spawning per request
  Pickling objects:  CPU overhead on every Queue.put/get
  IPC bandwidth:     Shared memory > Pipe > Queue > network
  Memory:            Each process copies the parent's memory (fork) or
                     reimports everything (spawn — Windows default)
"""
print(guide)

print("=== Multiprocessing complete ===")
