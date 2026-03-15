# 🔥 multiprocessing_guide.md — Python Multiprocessing, Deep Dive

> Complete reference for Python's multiprocessing module: processes, pools,
> IPC, shared memory, and parallel patterns for CPU-bound work.

---

## 📋 Contents

```
1.  Why multiprocessing — the GIL problem
2.  Process basics — create, start, join
3.  ProcessPoolExecutor — the modern way
4.  multiprocessing.Pool — the classic way
5.  Inter-process communication (Queue, Pipe)
6.  Shared memory (Value, Array)
7.  Manager — shared Python objects
8.  Process synchronization (Lock, Semaphore, Event, Barrier)
9.  Initializer functions — per-process setup
10. Chunk strategies for parallel work
11. Handling exceptions in processes
12. CPU-bound patterns (image processing, data crunching)
13. spawn vs fork vs forkserver
14. Common pitfalls
```

---

## 1. Why Multiprocessing? The GIL Problem

```python
import time, threading, multiprocessing

def cpu_work(n):
    """Pure Python CPU work — GIL prevents true thread parallelism."""
    return sum(i**2 for i in range(n))

N = 5_000_000

# Sequential:
start = time.time()
[cpu_work(N) for _ in range(4)]
print(f"Sequential: {time.time()-start:.2f}s")   # ~4.0s

# Threading (GIL prevents parallel execution):
start = time.time()
threads = [threading.Thread(target=cpu_work, args=(N,)) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print(f"Threading:  {time.time()-start:.2f}s")   # ~4.0s (same! GIL)

# Multiprocessing (each process has own GIL — true parallelism):
start = time.time()
with multiprocessing.Pool(4) as pool:
    pool.map(cpu_work, [N]*4)
print(f"Processes:  {time.time()-start:.2f}s")   # ~1.2s (4x faster!)
```

---

## 2. Process Basics

```python
from multiprocessing import Process
import os

def worker(name, value):
    print(f"Process {name}: PID={os.getpid()}, value={value}")

# Create and start:
p = Process(target=worker, args=("Alice", 42), kwargs={}, name="worker-1")
p.start()

# Wait for completion:
p.join()              # blocks until process exits
p.join(timeout=5.0)   # blocks up to 5 seconds
if p.is_alive():
    p.terminate()     # SIGTERM — graceful shutdown
    p.join(timeout=2)
    if p.is_alive():
        p.kill()      # SIGKILL — force kill

# Properties:
p.name       # process name
p.pid        # OS process ID (set after start)
p.exitcode   # return code (0=success, negative=signal, None=still running)
p.is_alive() # True while running
p.daemon     # daemon processes die when parent exits

# Current process info:
os.getpid()                       # current process PID
os.getppid()                      # parent process PID
multiprocessing.current_process() # Process object
multiprocessing.parent_process()  # parent Process object
multiprocessing.active_children() # list of alive child processes
```

---

## 3. ProcessPoolExecutor — The Modern Way

Preferred over `multiprocessing.Pool` for new code:

```python
from concurrent.futures import ProcessPoolExecutor, as_completed, wait
import os

def compress(filepath):
    """CPU-bound: compresses a file."""
    import gzip, shutil
    with open(filepath, 'rb') as f_in:
        with gzip.open(filepath + '.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    return filepath

files = [f"data_{i}.csv" for i in range(16)]

# map — blocking, returns results in order:
with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
    results = list(executor.map(compress, files))

# submit — non-blocking, returns Future:
with ProcessPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(compress, f): f for f in files}

    for future in as_completed(futures):
        filepath = futures[future]
        try:
            result = future.result()
            print(f"Compressed: {result}")
        except Exception as e:
            print(f"Failed: {filepath} — {e}")

# map with multiple args (use starmap alternative via partial):
from functools import partial

def process(filepath, quality):
    return encode_video(filepath, quality)

process_hq = partial(process, quality="high")
with ProcessPoolExecutor() as executor:
    results = list(executor.map(process_hq, files))

# Chunked map for large iterables:
with ProcessPoolExecutor() as executor:
    results = list(executor.map(transform, data, chunksize=100))
    # chunksize: how many items to send to each process at once
    # Larger chunksize = less IPC overhead but coarser granularity
```

---

## 4. multiprocessing.Pool — The Classic Way

```python
from multiprocessing import Pool
import os

def square(x):
    return x ** 2

with Pool(processes=os.cpu_count()) as pool:

    # map — like built-in map, parallel, blocking:
    results = pool.map(square, range(100))

    # starmap — for functions with multiple args:
    results = pool.starmap(pow, [(2,3), (3,4), (4,5)])   # [8, 81, 1024]

    # map_async — non-blocking:
    async_result = pool.map_async(square, range(100))
    # ... do other work ...
    results = async_result.get(timeout=30)

    # apply — single function call (blocking):
    result = pool.apply(square, args=(5,))

    # apply_async — single call (non-blocking):
    ar = pool.apply_async(square, args=(5,), callback=print)
    result = ar.get()

    # imap — lazy iterator (memory efficient for huge inputs):
    for result in pool.imap(square, range(1_000_000), chunksize=1000):
        store(result)

    # imap_unordered — like imap but results come in completion order:
    for result in pool.imap_unordered(square, range(1_000_000)):
        store(result)

# Pool without context manager:
pool = Pool()
results = pool.map(square, data)
pool.close()   # no new tasks
pool.join()    # wait for all tasks to complete
pool.terminate()  # immediate shutdown
```

---

## 5. Inter-Process Communication

### Queue (multi-producer, multi-consumer)

```python
from multiprocessing import Process, Queue

def producer(q):
    for i in range(10):
        q.put(i)           # serializes with pickle and sends
    q.put(None)            # sentinel

def consumer(q):
    while True:
        item = q.get()     # blocks until item available
        if item is None:
            break
        print(f"Got: {item}")

q = Queue(maxsize=50)   # bounded — blocks if full

p = Process(target=producer, args=(q,))
c = Process(target=consumer, args=(q,))
p.start(); c.start()
p.join();  c.join()

# Queue methods:
q.put(item, block=True, timeout=None)
q.get(block=True, timeout=None)
q.put_nowait(item)   # raises queue.Full if full
q.get_nowait()       # raises queue.Empty if empty
q.empty()            # unreliable in multiprocessing context
q.qsize()            # approximate size
```

### Pipe (two-process point-to-point)

```python
from multiprocessing import Pipe, Process

def child_func(conn):
    message = conn.recv()       # receive from parent
    print(f"Child got: {message}")
    conn.send(message.upper())  # send back
    conn.close()

parent_conn, child_conn = Pipe(duplex=True)  # duplex=True: both ends can send/recv
                                              # duplex=False: parent sends, child recvs

p = Process(target=child_func, args=(child_conn,))
p.start()

parent_conn.send("hello world")
response = parent_conn.recv()   # "HELLO WORLD"
print(f"Parent got: {response}")
parent_conn.close()

p.join()

# Pipe methods:
conn.send(obj)        # pickle and send (blocks if buffer full)
conn.recv()           # unpickle and return (blocks until data)
conn.poll(timeout)    # True if data available (timeout=None → block)
conn.send_bytes(b)    # send raw bytes
conn.recv_bytes()     # receive raw bytes
conn.close()
```

---

## 6. Shared Memory — Value and Array

Fast shared memory using C types (no pickling):

```python
from multiprocessing import Value, Array, Process

# Value — single value:
counter = Value('i', 0)    # 'i'=signed int, 'd'=double, 'c'=char, 'b'=byte

def increment(counter, n):
    for _ in range(n):
        with counter.get_lock():   # MUST use lock for thread/process safety!
            counter.value += 1

processes = [Process(target=increment, args=(counter, 10000)) for _ in range(4)]
for p in processes: p.start()
for p in processes: p.join()
print(counter.value)   # 40000

# Array — fixed-length array of C types:
arr = Array('d', [1.0, 2.0, 3.0, 4.0, 5.0])   # 'd'=double
arr = Array('i', 10)                            # 10 integers, initialized to 0

def fill_array(arr, start, end, value):
    for i in range(start, end):
        arr[i] = value

# Array supports indexing, slicing, iteration:
print(list(arr))
arr[0] = 99.0
arr[1:3] = [10.0, 20.0]

# Type codes:
# 'b' = signed char    'B' = unsigned char
# 'h' = short          'H' = unsigned short
# 'i' = int            'I' = unsigned int
# 'l' = long           'L' = unsigned long
# 'f' = float          'd' = double
# 'c' = char           'u' = Py_UNICODE (deprecated)
```

### multiprocessing.shared_memory (Python 3.8+)

```python
from multiprocessing import shared_memory
import numpy as np

# Create shared memory:
shm = shared_memory.SharedMemory(create=True, size=1024*1024*100)  # 100MB

# Access as numpy array (zero-copy!):
arr = np.ndarray((1000, 1000), dtype=np.float64, buffer=shm.buf)
arr[:] = np.random.rand(1000, 1000)

# In child process, attach by name:
def worker(shm_name, shape, dtype):
    shm = shared_memory.SharedMemory(name=shm_name)
    arr = np.ndarray(shape, dtype=dtype, buffer=shm.buf)
    result = arr.sum()   # zero-copy read!
    shm.close()
    return result

p = Process(target=worker, args=(shm.name, (1000,1000), np.float64))
p.start(); p.join()

shm.close()
shm.unlink()   # actually free the memory (must call once)
```

---

## 7. Manager — Shared Python Objects

For sharing arbitrary Python objects between processes (slower than shared memory but flexible):

```python
from multiprocessing import Manager, Process

def worker(shared_dict, shared_list, n):
    shared_dict[f"key_{n}"] = n * 2
    shared_list.append(n)

with Manager() as manager:
    d = manager.dict()       # dict accessible across processes
    l = manager.list()       # list accessible across processes
    lock = manager.Lock()
    queue = manager.Queue()
    event = manager.Event()
    value = manager.Value('i', 0)

    processes = [Process(target=worker, args=(d, l, i)) for i in range(5)]
    for p in processes: p.start()
    for p in processes: p.join()

    print(dict(d))    # {'key_0': 0, 'key_1': 2, ...}
    print(list(l))    # [0, 1, 2, 3, 4] (order may vary)
```

**Performance warning:** Manager objects communicate via sockets internally (even on same machine). For high-frequency access, use `Value`/`Array` or `shared_memory` instead.

---

## 8. Process Synchronization

```python
from multiprocessing import Lock, Semaphore, Event, Barrier, Condition

lock      = Lock()
sem       = Semaphore(5)
event     = Event()
barrier   = Barrier(parties=4)
condition = Condition()

# Same interface as threading equivalents, but work across processes:
with lock:
    shared_counter.value += 1

with sem:
    use_limited_resource()

event.wait(); event.set(); event.clear()
barrier.wait()
```

---

## 9. Initializer Functions — Per-Process Setup

```python
from multiprocessing import Pool
import sqlite3

# Global connection per process (can't pass connections between processes):
_conn = None

def init_worker(db_path):
    """Called once per worker process at startup."""
    global _conn
    _conn = sqlite3.connect(db_path)
    print(f"Worker {os.getpid()} initialized")

def query(sql):
    return _conn.execute(sql).fetchall()

with Pool(
    processes=4,
    initializer=init_worker,
    initargs=("app.db",)
) as pool:
    results = pool.map(query, queries)

# Use for: DB connections, loading large models, seeding RNG
```

---

## 10. Chunking Strategies

```python
import os

data = list(range(1_000_000))
n_cores = os.cpu_count()

# Equal chunks:
def chunk_list(lst, n):
    size = len(lst) // n
    return [lst[i*size:(i+1)*size] for i in range(n-1)] + [lst[(n-1)*size:]]

chunks = chunk_list(data, n_cores)

with ProcessPoolExecutor(max_workers=n_cores) as executor:
    partial_results = list(executor.map(sum, chunks))
total = sum(partial_results)

# Or use map's chunksize parameter (for large iterables):
with ProcessPoolExecutor() as executor:
    results = list(executor.map(process, data, chunksize=10_000))
    # Sends 10,000 items at a time to each process
    # Smaller chunksize: more IPC overhead, better load balancing
    # Larger chunksize: less IPC overhead, potentially uneven load
```

---

## 11. Handling Exceptions in Processes

```python
from concurrent.futures import ProcessPoolExecutor

def risky(x):
    if x == 5:
        raise ValueError(f"Bad value: {x}")
    return x * 2

# Exception is stored in Future, raised on .result():
with ProcessPoolExecutor() as executor:
    futures = [executor.submit(risky, i) for i in range(10)]
    for f in futures:
        try:
            print(f.result())
        except ValueError as e:
            print(f"Caught: {e}")

# With gather (return_exceptions=True equivalent):
with ProcessPoolExecutor() as executor:
    futures = [executor.submit(risky, i) for i in range(10)]
    results = []
    for f in futures:
        try:
            results.append(f.result())
        except Exception as e:
            results.append(e)   # store exception as result

# Note: exceptions must be picklable to cross process boundary!
class MyError(Exception):
    pass   # picklable by default if no unpicklable fields
```

---

## 12. CPU-Bound Patterns

### Parallel Map-Reduce

```python
import os
from functools import reduce
from concurrent.futures import ProcessPoolExecutor

def word_count(text_chunk):
    from collections import Counter
    return Counter(text_chunk.lower().split())

def merge_counts(a, b):
    a.update(b)
    return a

# Map: count words in each chunk
with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
    partial_counts = list(executor.map(word_count, text_chunks))

# Reduce: merge all counts
total = reduce(merge_counts, partial_counts)
```

### Parallel Image Processing

```python
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from PIL import Image   # pip install pillow

def resize_image(input_path, output_path, size=(800, 600)):
    img = Image.open(input_path)
    img.thumbnail(size, Image.LANCZOS)
    img.save(output_path)
    return output_path

images = list(Path("photos").glob("*.jpg"))
outputs = [Path("resized") / img.name for img in images]

with ProcessPoolExecutor() as executor:
    list(executor.map(resize_image, images, outputs))
```

---

## 13. spawn vs fork vs forkserver

```python
import multiprocessing

# start_method affects how child processes are created:
# 'fork'       — default on Unix: child is a fork of parent (copies memory)
#                Fast. But: copies ALL parent state including locks, sockets.
#                Dangerous with: threads + fork (known to cause deadlocks in C libs)
# 'spawn'      — default on Windows/macOS 3.8+: fresh Python interpreter
#                Safe. Slower (imports modules). Must pickle everything.
# 'forkserver' — starts a server process, requests forks from it
#                Compromise: fork safety without spawn's import overhead

multiprocessing.set_start_method('spawn')   # set globally (call once, before any Process)

# Or per-context:
ctx = multiprocessing.get_context('spawn')
p = ctx.Process(target=worker)

# Best practice: write code that works with 'spawn' (most portable):
# - Don't rely on globals being available in child
# - Make sure all arguments are picklable
# - Use if __name__ == '__main__': guard on Windows
```

---

## 14. Common Pitfalls

```python
# 1 — Forgetting if __name__ == '__main__': on Windows:
# Without it, each worker re-runs the script and spawns more workers → infinite recursion
if __name__ == '__main__':
    with Pool(4) as pool:
        pool.map(func, data)

# 2 — Non-picklable objects in process args:
# lambda, nested functions, sockets, file handles — can't be pickled
pool.map(lambda x: x*2, data)   # PicklingError!
# Fix: use a named top-level function

# 3 — Modifying global state (forked copy, not shared):
global_dict = {}
def worker():
    global_dict["key"] = "value"   # only modifies THIS process's copy!
# Parent's global_dict is unchanged. Use Manager.dict() if sharing needed.

# 4 — Spawning processes in a tight loop:
for item in data:
    Process(target=func, args=(item,)).start()   # 1000 processes!
# Fix: use a pool with bounded workers

# 5 — Not joining processes → zombie processes:
p = Process(target=func)
p.start()
# program exits — p is orphaned
p.join()   # always join!

# 6 — Shared Value without lock:
counter = Value('i', 0)
counter.value += 1   # NOT atomic! use with counter.get_lock()
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🧵 Threading Guide | [threading_guide.md](./threading_guide.md) |
| ⚡ Async Guide | [async_guide.md](./async_guide.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Threading Guide](./threading_guide.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Async Guide](./async_guide.md) · [Threading Guide](./threading_guide.md) · [Interview Q&A](./interview.md)
