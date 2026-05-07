# Multiprocessing — Theory

Multiple offices, each with their own whiteboard: that is multiprocessing. Each process runs its own Python interpreter, so the GIL no longer matters — two processes doing heavy math truly run at the same instant on separate CPU cores.

---

## 📌 Learning Priority

**Must Learn** — Core use, interview essential:
`ProcessPoolExecutor` · `mp.Process` · `if __name__ == '__main__'` guard · `Pool.map`

**Should Learn** — Important for real projects:
`Queue` / `Pipe` for IPC · `Pool.starmap` · `Pool.imap` · `chunksize`

**Good to Know** — Useful in specific situations:
`mp.Manager` · shared memory · `mp.Value` / `mp.Array`

**Reference** — Know it exists, look up when needed:
`mp.cpu_count()` · `mp.current_process()` · spawn vs fork vs forkserver · `mp.Pool.initializer`

---

## Chapter 1: Why Multiprocessing — The GIL Problem

Picture three warehouses (processes) each run by their own crew: they never step on each other's toes because they work in completely separate buildings. That is multiprocessing. Contrast this with threading: three workers in one warehouse, competing for one key to the stockroom (the GIL).

```python
import time, threading, multiprocessing

def cpu_work(n):
    return sum(i * i for i in range(n))

N = 5_000_000

# Sequential: ~4s
start = time.time()
[cpu_work(N) for _ in range(4)]
print(f"Sequential:      {time.time()-start:.2f}s")

# Threading: still ~4s — GIL prevents real parallelism on CPU work
start = time.time()
threads = [threading.Thread(target=cpu_work, args=(N,)) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print(f"Threading:       {time.time()-start:.2f}s   (no speedup, GIL!)")

# Multiprocessing: ~1s — 4 processes on 4 cores, each has its own GIL
start = time.time()
with multiprocessing.Pool(4) as pool:
    pool.map(cpu_work, [N]*4)
print(f"Multiprocessing: {time.time()-start:.2f}s   (~4x faster!)")
```

**When to use multiprocessing:** CPU-bound tasks — data transforms, image processing, ML inference on large batches, cryptography, compression, any pure Python computation that maxes out one core.

**The cost you pay:**
- Process startup: ~50–100ms per process (avoid spawning per request)
- All arguments and return values must be **picklable** (serializable)
- IPC overhead on every Queue/Pipe message (objects are pickled and unpickled)
- Each process copies the parent's memory on fork, or re-imports everything on spawn

---

## Chapter 2: Process Basics — mp.Process, start(), join()

`mp.Process` is the low-level primitive, analogous to `threading.Thread` but spawning a full process:

```python
import multiprocessing as mp
import os

def worker(name: str, value: int) -> None:
    print(f"Process {name}: PID={os.getpid()}, value={value}")

# Create a process object
p = mp.Process(
    target=worker,
    args=("Alice", 42),
    name="worker-1",    # ← meaningful name for debugging
)

p.start()              # fork or spawn a new OS process
p.join()               # wait for it to complete

# After join():
print(p.exitcode)      # 0 = success, negative = killed by signal
print(p.is_alive())    # False

# Timeout + force kill pattern:
p.join(timeout=5.0)
if p.is_alive():
    p.terminate()   # SIGTERM — graceful
    p.join(timeout=2)
    if p.is_alive():
        p.kill()    # SIGKILL — force
```

```
PROCESS vs THREAD MEMORY MODEL

  Threading (shared memory):          Multiprocessing (separate memory):
  ┌─────────────────────────────┐     ┌─────────────┐   ┌─────────────┐
  │ PROCESS                     │     │  Process A  │   │  Process B  │
  │  Heap (shared)              │     │  Own heap   │   │  Own heap   │
  │  Thread A ─┐                │     │  Own GIL    │   │  Own GIL    │
  │  Thread B ─┤─ compete GIL   │     │  Own stack  │   │  Own stack  │
  │  Thread C ─┘                │     └─────────────┘   └─────────────┘
  └─────────────────────────────┘       communicate via IPC (Queue, Pipe)
```

---

## Chapter 3: ProcessPoolExecutor — The Modern Way

`ProcessPoolExecutor` from `concurrent.futures` is the preferred interface for most new code. Same API as `ThreadPoolExecutor`, making it easy to swap when you realize your work is CPU-bound:

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
import os

def compress_file(filepath: str) -> str:
    import gzip, shutil
    with open(filepath, 'rb') as f_in:
        with gzip.open(filepath + '.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    return filepath

files = [f"data_{i}.csv" for i in range(16)]

# map — simplest, blocks until all done, returns in input order
with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
    results = list(executor.map(compress_file, files))

# submit + as_completed — process results as each finishes
with ProcessPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(compress_file, f): f for f in files}

    for future in as_completed(futures):
        filepath = futures[future]
        try:
            result = future.result()
            print(f"Compressed: {result}")
        except Exception as e:
            print(f"Failed {filepath}: {e}")

# map with chunksize — reduces IPC overhead for large iterables
with ProcessPoolExecutor() as executor:
    results = list(executor.map(transform, large_dataset, chunksize=500))
    # Sends 500 items at a time per process rather than 1 at a time
```

---

## Chapter 4: The if __name__ == '__main__' Guard

On Windows and macOS (with `spawn` start method), when you create a child process Python re-imports the entire script in that child. Without the guard, the child also hits the `Pool(4)` line and spawns 4 more children — who each spawn 4 more — infinite recursion that crashes fast.

```python
# WRONG — on Windows this causes infinite process spawning:
from multiprocessing import Pool

def work(x):
    return x * 2

pool = Pool(4)           # runs in child process too!
results = pool.map(work, range(100))

# CORRECT:
from multiprocessing import Pool

def work(x):
    return x * 2

if __name__ == '__main__':
    with Pool(4) as pool:
        results = pool.map(work, range(100))
```

**Rule:** any code that creates processes (Pool, ProcessPoolExecutor, Process.start()) must be inside `if __name__ == '__main__':`.

On Linux with the `fork` start method, this isn't required — child processes fork before the module is imported again. But writing the guard makes your code portable to all platforms.

---

## Chapter 5: IPC — Queue, Pipe, Shared Memory

Processes have separate memory. To exchange data, you must use **Inter-Process Communication**:

**mp.Queue — multi-producer, multi-consumer:**

```python
from multiprocessing import Process, Queue

def producer(q: Queue, items: list) -> None:
    for item in items:
        q.put(item)       # pickles item and sends
    q.put(None)           # sentinel

def consumer(q: Queue) -> None:
    while True:
        item = q.get()    # blocks until item available
        if item is None:
            break
        process(item)

q = Queue(maxsize=50)     # bounded — blocks producer when full
p = Process(target=producer, args=(q, data))
c = Process(target=consumer, args=(q,))
p.start(); c.start()
p.join();  c.join()
```

**mp.Pipe — point-to-point between exactly two processes:**

```python
from multiprocessing import Pipe, Process

def child_func(conn) -> None:
    msg = conn.recv()          # receive from parent
    conn.send(msg.upper())     # send back
    conn.close()

parent_conn, child_conn = Pipe(duplex=True)   # both ends can send/recv
p = Process(target=child_func, args=(child_conn,))
p.start()

parent_conn.send("hello world")
response = parent_conn.recv()   # "HELLO WORLD"
p.join()
```

**mp.Value and mp.Array — shared memory (no pickle cost):**

```python
from multiprocessing import Value, Array, Process, Lock

counter = Value('i', 0)   # 'i' = C int, initial value 0

def increment(counter: Value, lock: Lock, n: int) -> None:
    for _ in range(n):
        with lock:                    # ← MUST lock; Value is not atomic
            counter.value += 1

lock = Lock()
procs = [Process(target=increment, args=(counter, lock, 1000)) for _ in range(4)]
for p in procs: p.start()
for p in procs: p.join()
print(counter.value)   # 4000

# Array — fixed-length C array in shared memory:
arr = Array('d', [1.0, 2.0, 3.0])   # 'd' = C double
```

---

## Chapter 6: Pool Patterns — map, starmap, imap

`multiprocessing.Pool` is the classic interface and has more variants than `ProcessPoolExecutor`:

```python
from multiprocessing import Pool
import os

def square(x): return x ** 2
def power(base, exp): return base ** exp

with Pool(processes=os.cpu_count()) as pool:

    # map — parallel map, blocks, returns in input order
    results = pool.map(square, range(100))

    # starmap — like map but unpacks tuples as multiple args
    results = pool.starmap(power, [(2, 3), (3, 4), (4, 5)])
    # equivalent to: [power(2,3), power(3,4), power(4,5)]

    # imap — lazy iterator, memory-efficient for huge inputs
    for result in pool.imap(square, range(1_000_000), chunksize=1000):
        store(result)   # process one at a time, never load all into memory

    # imap_unordered — like imap but results come in completion order
    for result in pool.imap_unordered(square, range(1_000_000)):
        store(result)
```

**chunksize strategy:**
```
Small chunksize (e.g. 1):
  + Better load balancing (idle workers get more tasks)
  - More IPC messages → higher overhead

Large chunksize (e.g. 10,000):
  + Less IPC overhead
  - Uneven load if some chunks take much longer
```

---

## Chapter 7: Manager — Shared Python Objects

When you need to share a full Python `dict`, `list`, or other object across processes (not just primitives), use `mp.Manager`. It starts a server process that holds the objects and proxies access:

```python
from multiprocessing import Manager, Process

def worker(shared_dict: dict, shared_list: list, n: int) -> None:
    shared_dict[f"key_{n}"] = n * 2
    shared_list.append(n)

with Manager() as manager:
    d = manager.dict()    # dict proxy
    l = manager.list()    # list proxy

    procs = [Process(target=worker, args=(d, l, i)) for i in range(5)]
    for p in procs: p.start()
    for p in procs: p.join()

    print(dict(d))   # {'key_0': 0, 'key_1': 2, ...}
    print(list(l))   # [0, 1, 2, 3, 4]
```

**Performance warning:** Manager objects communicate via sockets even on the same machine. Each access is a network round-trip to the manager server. For high-frequency access, use `Value`/`Array` or `shared_memory` instead. Use Manager for low-frequency coordination between processes.

---

## Chapter 8: Common Mistakes

```python
# 1 — Missing if __name__ == '__main__' guard on Windows/macOS
# Infinite process spawning → immediate crash
# Fix: always use the guard

# 2 — Non-picklable objects in process args
pool.map(lambda x: x*2, data)   # PicklingError! lambda can't be pickled
# Fix: use named top-level functions (not lambdas, not nested functions)

# 3 — Assuming globals are shared
global_result = []
def worker():
    global_result.append(42)   # modifies THIS process's copy only!
# Parent's global_result stays empty
# Fix: return values, use Queue, or Manager

# 4 — Spawning too many processes in a loop
for item in huge_list:
    Process(target=func, args=(item,)).start()   # 10,000 processes!
# Fix: use Pool or ProcessPoolExecutor with bounded workers

# 5 — Not joining processes → zombie processes
p = Process(target=func)
p.start()
# exits without join → p becomes a zombie (holds OS resources until parent dies)
p.join()   # always join

# 6 — Shared Value without lock
counter = Value('i', 0)
counter.value += 1   # NOT atomic; two processes can race
# Fix: with counter.get_lock(): counter.value += 1

# 7 — Sending large objects through Queue frequently
# Each put/get pickles and unpickles the object — expensive for large arrays
# Fix: use shared_memory for large numpy arrays, or redesign to reduce IPC
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬆️ Root Theory | [../theory.md](../theory.md) |
| 💻 Practice | [practice.md](./practice.md) |
| 🧵 Threading | [../01_threading/theory.md](../01_threading/theory.md) |
| ⚡ Asyncio | [../03_asyncio/theory.md](../03_asyncio/theory.md) |
| ⚡ Cheatsheet | [../cheetsheet.md](../cheetsheet.md) |
| 🔥 Interview Q&A | [../interview.md](../interview.md) |

---

**[Back to README](../../README.md)**

**Prev:** [Threading Theory](../01_threading/theory.md) | **Next:** [Asyncio Theory →](../03_asyncio/theory.md)

**Related Topics:** [Root Theory](../theory.md) · [Threading](../01_threading/theory.md) · [Asyncio](../03_asyncio/theory.md) · [Cheat Sheet](../cheetsheet.md) · [Interview Q&A](../interview.md)
