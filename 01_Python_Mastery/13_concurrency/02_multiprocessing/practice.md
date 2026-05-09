# Multiprocessing — Practice

15 focused exercises from process basics through parallel map-reduce patterns.

---

## Quick Index

| # | Difficulty | Concept |
|---|---|---|
| [Q1](#q1) | 🟢 Easy | mp.Process basics: spawn, start, join |
| [Q2](#q2) | 🟢 Easy | ProcessPoolExecutor: parallelize CPU function |
| [Q3](#q3) | 🟡 Medium | __name__ guard: why required |
| [Q4](#q4) | 🟡 Medium | mp.Queue: pass results from child to parent |
| [Q5](#q5) | 🟡 Medium | Pool.map vs Pool.starmap: difference |
| [Q6](#q6) | 🟡 Medium | Pool.imap: process results lazily |
| [Q7](#q7) | 🟡 Medium | Shared memory: mp.Value and mp.Array |
| [Q8](#q8) | 🟡 Medium | mp.Manager: shared dict across processes |
| [Q9](#q9) | 🟡 Medium | Pickling: which objects cannot be pickled |
| [Q10](#q10) | 🟡 Medium | ProcessPoolExecutor vs ThreadPoolExecutor: choose |
| [Q11](#q11) | 🟠 Hard | Fan-out: parallelize across all CPU cores |
| [Q12](#q12) | 🟠 Hard | Error handling: capture exceptions from child |
| [Q13](#q13) | 🟡 Medium | mp.Pipe: bidirectional communication |
| [Q14](#q14) | 🟡 Medium | chunksize: optimize Pool.map for large inputs |
| [Q15](#q15) | 🟠 Hard | Capstone: parallel word count across N files |

---

<a id="q1"></a>

### Q1 🟢 · Process Basics — mp.Process, start, join

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)



**Problem:** Write a `worker(name, n)` function that prints its PID and computes `sum(range(n))`. Spawn two `mp.Process` objects targeting it with different arguments. Start both and join both. Print the PIDs to show they are different from the parent.

<details>
<summary>💡 Hint</summary>
`import os; os.getpid()` returns the current process PID. Wrap everything under `if __name__ == '__main__':`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import multiprocessing as mp
import os

def worker(name: str, n: int) -> None:
    result = sum(range(n))
    print(f"[{name}] PID={os.getpid()}, sum={result}")

if __name__ == '__main__':
    print(f"Parent PID={os.getpid()}")
    p1 = mp.Process(target=worker, args=("A", 1000))
    p2 = mp.Process(target=worker, args=("B", 2000))
    p1.start(); p2.start()
    p1.join();  p2.join()
    print(f"Both done. Exit codes: {p1.exitcode}, {p2.exitcode}")
```

**Why:** Each `Process` gets a fresh Python interpreter with its own PID. `join()` blocks until the child exits. `exitcode=0` means success.
</details>

---

<a id="q2"></a>

### Q2 🟢 · ProcessPoolExecutor — parallelize a CPU-bound function

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)



**Problem:** Write `is_prime(n)` that checks primality by trial division. Use `ProcessPoolExecutor` to test all integers from 2 to 50 in parallel. Print the primes found.

<details>
<summary>💡 Hint</summary>
`executor.map(is_prime, range(2, 51))` returns booleans in input order. Zip with the input to filter primes.
</details>

<details>
<summary>✅ Answer</summary>

```python
import math
from concurrent.futures import ProcessPoolExecutor

def is_prime(n: int) -> bool:
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0: return False
    return True

if __name__ == '__main__':
    nums = list(range(2, 51))
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(is_prime, nums))
    primes = [n for n, ok in zip(nums, results) if ok]
    print(primes)
```

**Why:** `ProcessPoolExecutor` distributes primality checks across CPU cores. Each process has its own GIL — true parallel computation.
</details>

---

<a id="q3"></a>

### Q3 🟡 · Guards — the if __name__ == '__main__' requirement

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)



**Problem:** Write a script that creates a `Pool(2)` and calls `pool.map(square, [1,2,3])`. Show it works correctly with the guard. Explain in comments what happens on Windows/macOS without the guard.

<details>
<summary>💡 Hint</summary>
On Windows, the `spawn` start method re-imports the script in each child process. Without the guard, children hit `Pool(2)` again and spawn more children — infinite recursion.
</details>

<details>
<summary>✅ Answer</summary>

```python
from multiprocessing import Pool

def square(x: int) -> int:
    return x ** 2

# WITHOUT guard (Windows/macOS with spawn):
# When Pool(2) starts, it imports this script in each worker.
# Each worker hits Pool(2) again → spawns 2 more → infinite processes
# Result: RecursionError or system freeze

# WITH guard (correct):
if __name__ == '__main__':
    with Pool(2) as pool:
        results = pool.map(square, [1, 2, 3])
    print(results)  # [1, 4, 9]

# The guard ensures only the original script execution (not worker re-imports)
# reaches the Pool creation code.
```

**Why:** On Linux with `fork`, children don't re-import the script so the guard isn't strictly required. But it's always required on Windows, and writing it makes your code portable.
</details>

---

<a id="q4"></a>

### Q4 🟡 · IPC — mp.Queue: pass results from child to parent

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)



**Problem:** Spawn a child process that computes the squares of `[1, 2, 3, 4, 5]` and puts each result onto an `mp.Queue`. In the parent, collect all results and print them.

<details>
<summary>💡 Hint</summary>
Pass the queue as an argument to the child function. The parent drains the queue after `p.join()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import multiprocessing as mp

def compute_squares(q: mp.Queue, items: list) -> None:
    for n in items:
        q.put(n ** 2)
    q.put(None)   # sentinel to signal done

if __name__ == '__main__':
    q = mp.Queue()
    p = mp.Process(target=compute_squares, args=(q, [1, 2, 3, 4, 5]))
    p.start()

    results = []
    while True:
        item = q.get()
        if item is None:
            break
        results.append(item)

    p.join()
    print(results)  # [1, 4, 9, 16, 25]
```

**Why:** `mp.Queue` serializes objects with pickle and sends them via OS IPC. It is both process-safe and thread-safe. The sentinel pattern signals when the child is done producing.
</details>

---

<a id="q5"></a>

### Q5 🟡 · Pool Methods — Pool.map vs Pool.starmap

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)



**Problem:** Write a `power(base, exp)` function. Use `Pool.starmap` to compute `[(2,3), (3,4), (4,5)]` in parallel. Explain in comments why `Pool.map` cannot be used directly here.

<details>
<summary>💡 Hint</summary>
`map` takes a single-argument function. `starmap` unpacks each tuple as multiple positional arguments.
</details>

<details>
<summary>✅ Answer</summary>

```python
from multiprocessing import Pool

def power(base: int, exp: int) -> int:
    return base ** exp

if __name__ == '__main__':
    pairs = [(2, 3), (3, 4), (4, 5)]

    with Pool(3) as pool:
        # starmap: unpacks each tuple → power(2,3), power(3,4), power(4,5)
        results = pool.starmap(power, pairs)

    print(results)  # [8, 81, 1024]

    # Pool.map can only call single-argument functions:
    # pool.map(power, pairs) → power((2,3)) → TypeError: expects 2 args
    # Fix with partial: pool.map(partial(power, exp=3), [2,3,4])
```

**Why:** `starmap(fn, [(a1,b1), (a2,b2)])` is equivalent to `[fn(*args) for args in items]`. Use it whenever your function takes more than one positional argument.
</details>

---

<a id="q6"></a>

### Q6 🟡 · Lazy Processing — Pool.imap

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)



**Problem:** Use `Pool.imap` to compute squares of integers 0–9 lazily. Print each result as it comes without waiting for all to complete. Use `chunksize=3`. Show that `imap` returns an iterator, not a list.

<details>
<summary>💡 Hint</summary>
`pool.imap(fn, iterable)` returns a lazy iterator. Iterate over it with `for result in pool.imap(...)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from multiprocessing import Pool

def square(x: int) -> int:
    return x ** 2

if __name__ == '__main__':
    with Pool(4) as pool:
        # imap returns a lazy iterator — results come in as they complete
        it = pool.imap(square, range(10), chunksize=3)
        # Sends 3 items at a time to each worker to reduce IPC overhead
        for result in it:
            print(result, end=" ")
    print()
    # For huge inputs, imap avoids loading all results into memory at once
    # contrast: pool.map() builds the entire results list before returning
```

**Why:** `imap` is memory-efficient for large inputs — process results one at a time as they arrive. `imap_unordered` is faster (no ordering overhead) when result order doesn't matter.
</details>

---

<a id="q7"></a>

### Q7 🟡 · Shared Memory — mp.Value and mp.Array

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)



**Problem:** Create an `mp.Value('i', 0)` counter. Spawn 4 processes each incrementing it 250 times (total: 1000). Use `mp.Lock` to avoid race conditions. Verify the final value is 1000. Also create an `mp.Array('d', 5)` and show two processes can read from it.

<details>
<summary>💡 Hint</summary>
`Value.get_lock()` returns a built-in lock for the Value, or pass an explicit `mp.Lock`. Do `with lock: counter.value += 1`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import multiprocessing as mp

def increment(counter: mp.Value, lock: mp.Lock, n: int) -> None:
    for _ in range(n):
        with lock:
            counter.value += 1

def read_array(arr: mp.Array, idx: int) -> None:
    print(f"Process reading arr[{idx}] = {arr[idx]}")

if __name__ == '__main__':
    counter = mp.Value('i', 0)
    lock    = mp.Lock()

    procs = [mp.Process(target=increment, args=(counter, lock, 250))
             for _ in range(4)]
    for p in procs: p.start()
    for p in procs: p.join()
    print(f"Counter: {counter.value}")  # 1000

    arr = mp.Array('d', [1.1, 2.2, 3.3, 4.4, 5.5])
    readers = [mp.Process(target=read_array, args=(arr, i)) for i in range(3)]
    for p in readers: p.start()
    for p in readers: p.join()
```

**Why:** `mp.Value`/`mp.Array` use OS shared memory — no pickle overhead. But they require explicit locking. For complex objects (dicts, lists) use `mp.Manager()`.
</details>

---

<a id="q8"></a>

### Q8 🟡 · Manager — shared dict across processes

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)



**Problem:** Use `mp.Manager()` to create a shared dict. Spawn 3 processes each writing a different key to the dict. After all finish, print the full dict in the parent.

<details>
<summary>💡 Hint</summary>
`with Manager() as m: d = m.dict()`. Pass `d` as an argument to each process. Changes made in child processes are visible in the parent.
</details>

<details>
<summary>✅ Answer</summary>

```python
from multiprocessing import Manager, Process

def worker(shared_dict: dict, key: str, value: int) -> None:
    shared_dict[key] = value * 2

if __name__ == '__main__':
    with Manager() as manager:
        d = manager.dict()

        procs = [
            Process(target=worker, args=(d, f"key_{i}", i))
            for i in range(3)
        ]
        for p in procs: p.start()
        for p in procs: p.join()

        print(dict(d))  # {'key_0': 0, 'key_1': 2, 'key_2': 4}
```

**Why:** Manager creates a server process that holds the dict. Child processes access it via proxy objects over a socket. Slower than `mp.Value`/`Array` but supports arbitrary Python objects.
</details>

---

<a id="q9"></a>

### Q9 🟡 · Pickling — which objects cannot be pickled

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)



**Problem:** Try passing a lambda to `Pool.map`. Show the `PicklingError`. Then fix it using a named top-level function. Also show that a local (nested) function cannot be pickled. Explain in comments why.

<details>
<summary>💡 Hint</summary>
Pickle serializes by module path + name. Lambdas and nested functions have no importable path — they can't be found by the unpickling process.
</details>

<details>
<summary>✅ Answer</summary>

```python
from multiprocessing import Pool
import pickle

# Named top-level function — picklable (has stable module path)
def double(x: int) -> int:
    return x * 2

if __name__ == '__main__':
    # Works: named function
    with Pool(2) as pool:
        print(pool.map(double, [1, 2, 3]))  # [2, 4, 6]

    # Fails: lambda
    fn = lambda x: x * 2
    try:
        pickle.dumps(fn)
    except AttributeError as e:
        print(f"Lambda pickle error: {e}")

    # Fails: local/nested function
    def local_fn(x): return x * 2
    try:
        pickle.dumps(local_fn)
    except AttributeError as e:
        print(f"Local fn pickle error: {e}")

    # Pickle finds objects by looking up __module__.__qualname__ at unpickling time.
    # Lambdas and local functions don't have a stable importable path.
    # Fix: always use top-level module functions as targets for Pool/ProcessPoolExecutor.
```

**Why:** When a worker process unpickles arguments, it imports the object by module path. Lambdas (`<lambda>`) and nested functions can't be found this way.
</details>

---

<a id="q10"></a>

### Q10 🟡 · Decision — ProcessPoolExecutor vs ThreadPoolExecutor

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)



**Problem:** Write two benchmark functions — `cpu_task(n)` (sum of squares) and `io_task(delay)` (time.sleep). Run each with both `ThreadPoolExecutor` and `ProcessPoolExecutor` (4 workers, 4 tasks). Print timings and explain which executor is better for each case.

<details>
<summary>💡 Hint</summary>
Threads release the GIL during sleep (I/O). Processes each have their own GIL (CPU). So threads win for I/O, processes win for CPU.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def cpu_task(n: int) -> int:
    return sum(i * i for i in range(n))

def io_task(delay: float) -> str:
    time.sleep(delay)
    return "done"

def benchmark(executor_class, fn, args_list):
    start = time.perf_counter()
    with executor_class(max_workers=4) as ex:
        list(ex.map(fn, args_list))
    return time.perf_counter() - start

if __name__ == '__main__':
    N = 500_000
    print("CPU-bound (sum of squares):")
    print(f"  Threads:   {benchmark(ThreadPoolExecutor,   cpu_task, [N]*4):.2f}s")
    print(f"  Processes: {benchmark(ProcessPoolExecutor,  cpu_task, [N]*4):.2f}s")
    # Processes should be ~4x faster — each runs on a separate core

    print("I/O-bound (sleep 0.5s):")
    print(f"  Threads:   {benchmark(ThreadPoolExecutor,   io_task, [0.5]*4):.2f}s")
    print(f"  Processes: {benchmark(ProcessPoolExecutor,  io_task, [0.5]*4):.2f}s")
    # Both ~0.5s — but Threads have lower overhead
```

**Why:** GIL is released during I/O, so threads truly run concurrently for I/O tasks. For CPU work, processes bypass the GIL entirely via separate interpreters.
</details>

---

<a id="q11"></a>

### Q11 🟠 · Fan-out — parallelize across all CPU cores

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)



**Problem:** Given a list of 1000 numbers, write `process_item(x)` that does some CPU work (compute x^3 + sqrt(x) + log(x+1)). Split the list into `cpu_count()` chunks and process each chunk in a separate process using `ProcessPoolExecutor`. Collect and merge results.

<details>
<summary>💡 Hint</summary>
`os.cpu_count()` gives the number of cores. Split the list into equal chunks and use `executor.map(process_chunk, chunks)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import os, math, time
from concurrent.futures import ProcessPoolExecutor

def process_chunk(items: list) -> list:
    return [x**3 + math.sqrt(x) + math.log(x + 1) for x in items]

def chunk_list(lst: list, n: int) -> list:
    size = len(lst) // n
    return [lst[i*size:(i+1)*size] for i in range(n-1)] + [lst[(n-1)*size:]]

if __name__ == '__main__':
    data = list(range(1, 1001))
    n_cores = os.cpu_count()
    chunks = chunk_list(data, n_cores)

    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=n_cores) as executor:
        partial_results = list(executor.map(process_chunk, chunks))
    elapsed = time.perf_counter() - start

    all_results = [x for chunk in partial_results for x in chunk]
    print(f"Processed {len(all_results)} items in {elapsed:.3f}s on {n_cores} cores")
```

**Why:** Distributing work across all cores and merging results is the map-reduce pattern. Each chunk is processed in isolation — no IPC during processing, only at the merge step.
</details>

---

<a id="q12"></a>

### Q12 🟠 · Error Handling — capture exceptions from child processes

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)



**Problem:** Write `risky(x)` that raises `ValueError("bad!")` when `x == 3`. Use `ProcessPoolExecutor.submit` on values 1–5. Catch the exception from the future and continue processing the others. Print which values succeeded and which failed.

<details>
<summary>💡 Hint</summary>
`future.result()` re-raises the exception from the child process. Wrap in `try/except` per future.
</details>

<details>
<summary>✅ Answer</summary>

```python
from concurrent.futures import ProcessPoolExecutor

def risky(x: int) -> int:
    if x == 3:
        raise ValueError(f"bad value: {x}")
    return x * 2

if __name__ == '__main__':
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(risky, i): i for i in range(1, 6)}

        for future, input_val in futures.items():
            try:
                result = future.result()
                print(f"  {input_val} → {result}")
            except ValueError as e:
                print(f"  {input_val} → ERROR: {e}")
```

**Why:** The exception from the child process is pickled, sent back to the parent, and stored in the `Future`. Calling `.result()` unpickles and re-raises it. This is why exceptions must be picklable.
</details>

---

<a id="q13"></a>

### Q13 🟡 · IPC — mp.Pipe bidirectional communication

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)



**Problem:** Use `mp.Pipe(duplex=True)` to set up bidirectional communication between a parent and a child process. Parent sends a list of numbers; child squares each and sends the results back.

<details>
<summary>💡 Hint</summary>
`parent_conn, child_conn = mp.Pipe(duplex=True)`. Pass `child_conn` to the child process. After starting the child, close the `child_conn` in the parent.
</details>

<details>
<summary>✅ Answer</summary>

```python
import multiprocessing as mp

def child_worker(conn: mp.connection.Connection) -> None:
    data = conn.recv()           # receive list from parent
    result = [x ** 2 for x in data]
    conn.send(result)            # send squares back
    conn.close()

if __name__ == '__main__':
    parent_conn, child_conn = mp.Pipe(duplex=True)

    p = mp.Process(target=child_worker, args=(child_conn,))
    p.start()
    child_conn.close()           # parent doesn't need child's end

    parent_conn.send([1, 2, 3, 4, 5])
    result = parent_conn.recv()
    parent_conn.close()

    p.join()
    print(result)  # [1, 4, 9, 16, 25]
```

**Why:** `Pipe` is faster than `Queue` for point-to-point communication — it uses OS pipe primitives directly. Close the unused end in each process to avoid resource leaks.
</details>

---

<a id="q14"></a>

### Q14 🟡 · Performance — chunksize optimization

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)



**Problem:** Apply `square(x)` (returns `x**2`) to a list of 10,000 integers using `Pool.map` with `chunksize=1`, `chunksize=100`, and `chunksize=1000`. Time each and explain the tradeoff.

<details>
<summary>💡 Hint</summary>
`chunksize=1` means one pickle+IPC call per item. `chunksize=1000` means 10 pickle+IPC calls total.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time
from multiprocessing import Pool

def square(x: int) -> int:
    return x ** 2

if __name__ == '__main__':
    data = list(range(10_000))

    for cs in [1, 100, 1000]:
        start = time.perf_counter()
        with Pool(4) as pool:
            results = pool.map(square, data, chunksize=cs)
        elapsed = time.perf_counter() - start
        print(f"chunksize={cs:5d}: {elapsed:.3f}s")

    # chunksize=1:    many small IPC messages → high overhead
    # chunksize=100:  100 items per message → 100 messages total → balanced
    # chunksize=1000: 10 items per message → very low overhead
    # For trivial functions (square), overhead dominates — large chunksize wins
    # For slow functions, chunksize matters less (IPC is small vs compute time)
```

**Why:** Each IPC round-trip (pickle + OS message) has fixed overhead regardless of item count. Batching more items per message reduces the number of round-trips.
</details>

---

<a id="q15"></a>

### Q15 🟠 · Capstone — Parallel word count across N files

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)



**Problem:** Create 4 in-memory text strings (simulate files). Write `count_words(text)` that returns a `Counter` of word frequencies. Use `ProcessPoolExecutor` to count words in all texts in parallel. Merge the partial counters in the parent to get a global word count.

<details>
<summary>💡 Hint</summary>
Return a `Counter` from each worker. Merge with `total.update(partial)` or `total += partial`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

TEXTS = [
    "the quick brown fox jumps over the lazy dog",
    "the dog barked at the fox near the river",
    "a quick brown dog outran the lazy fox today",
    "the river fox and the dog became fast friends",
]

def count_words(text: str) -> Counter:
    return Counter(text.lower().split())

if __name__ == '__main__':
    with ProcessPoolExecutor(max_workers=4) as executor:
        partial_counts = list(executor.map(count_words, TEXTS))

    # Merge all partial counters
    total = Counter()
    for partial in partial_counts:
        total.update(partial)

    print("Top 5 words:")
    for word, count in total.most_common(5):
        print(f"  {word!r}: {count}")
```

**Why:** This is the map-reduce pattern: map (count per chunk) then reduce (merge all counters). Each process does its counting independently — no shared state needed. The merge step is sequential but fast.
</details>

---

## 🔁 Navigation

| | |
|---|---|
| ⬆️ Multiprocessing Theory | [theory.md](./theory.md) |
| 💻 Practice Local | [practice_local.py](./practice_local.py) |
| 🧵 Threading Practice | [../01_threading/practice.md](../01_threading/practice.md) |
| ⚡ Asyncio Practice | [../03_asyncio/practice.md](../03_asyncio/practice.md) |
| 🗂️ Root Practice | [../practice.md](../practice.md) |

---

**[Back to README](../../README.md)**

**Prev:** [Threading Practice](../01_threading/practice.md) | **Next:** [Asyncio Practice →](../03_asyncio/practice.md)

**Related Topics:** [Multiprocessing Theory](./theory.md) · [Threading Practice](../01_threading/practice.md) · [Asyncio Practice](../03_asyncio/practice.md) · [Root Practice](../practice.md)
