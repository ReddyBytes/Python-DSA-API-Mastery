# Concurrency — Practice

35 survey-depth exercises covering threading, multiprocessing, asyncio, concurrent.futures, and decision-making patterns. For deep dives see the subfolder practice files.

---

## Quick Index

| # | Difficulty | Chapter | Concept |
|---|---|---|---|
| Q1 | 🟢 | Threading | Thread creation and join |
| Q2 | 🟢 | Threading | GIL: I/O-bound vs CPU-bound |
| Q3 | 🟡 | Threading | ThreadPoolExecutor basics |
| Q4 | 🟡 | Threading | Lock: protect shared counter |
| Q5 | 🟡 | Threading | Queue: producer-consumer |
| Q6 | 🟡 | Threading | threading.Event: stop signal |
| Q7 | 🟢 | Multiprocessing | mp.Process basics |
| Q8 | 🟢 | Multiprocessing | ProcessPoolExecutor: CPU work |
| Q9 | 🟡 | Multiprocessing | __name__ guard requirement |
| Q10 | 🟡 | Multiprocessing | Pool.map and Pool.starmap |
| Q11 | 🟡 | Multiprocessing | mp.Queue: cross-process IPC |
| Q12 | 🟡 | Multiprocessing | mp.Value shared counter |
| Q13 | 🟢 | Asyncio | Basic coroutine + asyncio.run() |
| Q14 | 🟢 | Asyncio | asyncio.sleep vs time.sleep |
| Q15 | 🟡 | Asyncio | asyncio.gather: concurrent fetches |
| Q16 | 🟡 | Asyncio | asyncio.create_task |
| Q17 | 🟡 | Asyncio | asyncio.wait_for: timeout |
| Q18 | 🟡 | Asyncio | async with context manager |
| Q19 | 🟡 | Asyncio | Async generator + async for |
| Q20 | 🟡 | concurrent.futures | as_completed: arrival order |
| Q21 | 🟡 | concurrent.futures | Future API: result, exception, done |
| Q22 | 🟡 | concurrent.futures | Thread vs Process executor swap |
| Q23 | 🟡 | concurrent.futures | map with timeout |
| Q24 | 🟡 | concurrent.futures | Exception propagation from future |
| Q25 | 🟡 | Decision | Choosing the right concurrency model |
| Q26 | 🟡 | Decision | run_in_executor: bridge sync to async |
| Q27 | 🟠 | Advanced | asyncio.Semaphore: rate limiting |
| Q28 | 🟠 | Advanced | Deadlock: diagnose and prevent |
| Q29 | 🟡 | Advanced | Daemon thread vs non-daemon |
| Q30 | 🟡 | Advanced | TaskGroup (Python 3.11+) |
| Q31 | 🟠 | Capstone | Thread-safe counter with Lock |
| Q32 | 🟠 | Capstone | Parallel prime finder |
| Q33 | 🟠 | Capstone | Async batch URL fetcher |
| Q34 | 🟠 | Capstone | Mixed: CPU workers + async I/O |
| Q35 | 🟠 | Capstone | Concurrency decision tree |

---

## ## Threading Basics (Q1–Q6)

### Q1 🟢 · Threading — Thread creation, start, and join

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

**Problem:** Write a `task(name, delay)` function that prints start/done messages. Create 3 threads with delays 0.3s, 0.2s, 0.1s. Start all three before joining any. Show total time is ~0.3s not 0.6s.

<details>
<summary>💡 Hint</summary>
Start ALL threads before calling `join()` on any of them. Calling `join()` on T1 before `start()`-ing T2 makes them sequential.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading, time

def task(name: str, delay: float) -> None:
    print(f"{name}: start")
    time.sleep(delay)
    print(f"{name}: done")

threads = [
    threading.Thread(target=task, args=(f"T{i}", d))
    for i, d in enumerate([0.3, 0.2, 0.1], 1)
]
start = time.perf_counter()
for t in threads: t.start()   # start all first
for t in threads: t.join()    # then wait for all
print(f"Total: {time.perf_counter()-start:.2f}s")  # ~0.3s
```

**Why:** Threads overlap because they're all started before any join. Time = max(delays).
</details>

---

### Q2 🟢 · GIL — I/O-bound threads speed up, CPU-bound don't

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

**Problem:** Demonstrate the GIL effect. Run `io_work()` (10x `time.sleep(0.01)`) sequentially and in 2 threads. Then run `cpu_work()` (sum-of-squares loop) sequentially and in 2 threads. Show threads help I/O work but not CPU work.

<details>
<summary>💡 Hint</summary>
The GIL is released during `time.sleep()` (I/O simulation), allowing both threads to run concurrently. For pure Python computation, threads take turns holding the GIL.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading, time

def io_work():
    for _ in range(10): time.sleep(0.01)

def cpu_work():
    sum(i*i for i in range(500_000))

def run_two(fn):
    t1 = threading.Thread(target=fn)
    t2 = threading.Thread(target=fn)
    t1.start(); t2.start(); t1.join(); t2.join()

# I/O-bound:
start = time.perf_counter(); io_work(); io_work(); seq_io = time.perf_counter()-start
start = time.perf_counter(); run_two(io_work);      thr_io = time.perf_counter()-start
print(f"I/O  sequential={seq_io:.2f}s threaded={thr_io:.2f}s")  # ~2x speedup

# CPU-bound:
start = time.perf_counter(); cpu_work(); cpu_work(); seq_cpu = time.perf_counter()-start
start = time.perf_counter(); run_two(cpu_work);       thr_cpu = time.perf_counter()-start
print(f"CPU  sequential={seq_cpu:.2f}s threaded={thr_cpu:.2f}s")  # no speedup
```

**Why:** The GIL is released during I/O operations — threads truly run concurrently. For pure Python computation, only one thread runs at a time.
</details>

---

### Q3 🟡 · ThreadPoolExecutor — submit, map, context manager

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

**Problem:** Use `ThreadPoolExecutor(max_workers=3)` to run `process(n)` (returns `n**2` after sleeping `n*0.01s`) over `[1,2,3,4,5]`. Collect results with `map()`. Then repeat with `submit()` and print results with `future.result()`.

<details>
<summary>💡 Hint</summary>
`executor.map()` returns results in input order. `submit()` returns futures immediately; call `.result()` to block and get the value.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time
from concurrent.futures import ThreadPoolExecutor

def process(n: int) -> int:
    time.sleep(n * 0.01)
    return n ** 2

# map version:
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(process, [1, 2, 3, 4, 5]))
print("map:", results)  # [1, 4, 9, 16, 25]

# submit version:
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(process, n) for n in [1, 2, 3, 4, 5]]
    results = [f.result() for f in futures]
print("submit:", results)  # [1, 4, 9, 16, 25]
```

**Why:** `map()` is simpler for uniform work. `submit()` gives you `Future` objects for more control (cancel, callbacks, exceptions).
</details>

---

### Q4 🟡 · Lock — protect shared counter from race conditions

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

**Problem:** 10 threads each increment a shared counter 1000 times. Show it gives wrong results without a lock. Fix with `threading.Lock`.

<details>
<summary>💡 Hint</summary>
`counter += 1` is three bytecodes — not atomic. Protect with `with lock: counter += 1`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading

def run_threads(increment_fn, n_threads=10, n_each=1000):
    counter = [0]   # mutable container for shared state
    lock = threading.Lock()

    def safe_inc():
        for _ in range(n_each):
            with lock:
                counter[0] += 1

    def unsafe_inc():
        for _ in range(n_each):
            counter[0] += 1

    fn = safe_inc if increment_fn == "safe" else unsafe_inc
    threads = [threading.Thread(target=fn) for _ in range(n_threads)]
    for t in threads: t.start()
    for t in threads: t.join()
    return counter[0]

print(run_threads("unsafe"))  # often < 10000
print(run_threads("safe"))    # always 10000
```

**Why:** `with lock:` ensures only one thread executes the increment at a time, making it atomic.
</details>

---

### Q5 🟡 · Queue — thread-safe producer-consumer

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

**Problem:** Producer puts items 1–5 on `queue.Queue`. Consumer reads until sentinel `None`. Run them in threads. Use `task_done()` and `queue.join()` to confirm all items processed.

<details>
<summary>💡 Hint</summary>
`q.join()` blocks until every item put on the queue has had `task_done()` called. Use it instead of joining the consumer thread.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading, queue, time

def producer(q):
    for i in range(1, 6):
        time.sleep(0.02)
        q.put(i)
    q.put(None)   # sentinel

def consumer(q):
    while True:
        item = q.get()
        if item is None:
            q.task_done()
            break
        print(f"consumed: {item**2}")
        q.task_done()

q = queue.Queue()
t = threading.Thread(target=consumer, args=(q,), daemon=True)
t.start()
producer(q)
q.join()   # wait until all task_done() calls match all put() calls
print("All items processed")
```

**Why:** `queue.Queue` is thread-safe — no lock needed. `task_done()` / `queue.join()` gives a clean synchronization point.
</details>

---

### Q6 🟡 · Event — cooperative thread stop signal

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

**Problem:** A worker loops printing "tick" every 0.1s until a `threading.Event` is set. Main thread sets the event after 0.35s. Worker stops cleanly.

<details>
<summary>💡 Hint</summary>
Check `event.is_set()` as the loop condition. The worker exits cleanly without being killed.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading, time

stop = threading.Event()

def worker():
    while not stop.is_set():
        print("tick")
        time.sleep(0.1)
    print("worker stopped")

t = threading.Thread(target=worker)
t.start()
time.sleep(0.35)
stop.set()
t.join()
```

**Why:** Event-based stopping is cleaner than `t.daemon = True` (which kills the thread without cleanup).
</details>

---

## ## Multiprocessing Basics (Q7–Q12)

### Q7 🟢 · Process — mp.Process basics

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

**Problem:** Spawn two processes running `worker(n)` (computes sum-of-squares up to n, prints PID). Start both, join both, print exit codes.

<details>
<summary>💡 Hint</summary>
Always use `if __name__ == '__main__':`. `p.exitcode` is 0 on success.
</details>

<details>
<summary>✅ Answer</summary>

```python
import multiprocessing as mp, os

def worker(n: int) -> None:
    print(f"PID={os.getpid()}, sum={sum(i*i for i in range(n))}")

if __name__ == '__main__':
    p1 = mp.Process(target=worker, args=(100_000,))
    p2 = mp.Process(target=worker, args=(200_000,))
    p1.start(); p2.start()
    p1.join();  p2.join()
    print(f"Exit codes: {p1.exitcode}, {p2.exitcode}")
```

**Why:** Each process is a separate Python interpreter with its own GIL — true parallel CPU execution.
</details>

---

### Q8 🟢 · ProcessPoolExecutor — parallel CPU work

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

**Problem:** Use `ProcessPoolExecutor` to compute `sum(range(n))` for `n in [1M, 2M, 3M, 4M]` in parallel. Print results and elapsed time. Compare to sequential.

<details>
<summary>💡 Hint</summary>
`executor.map(fn, items)` distributes items across workers. Use `os.cpu_count()` for max workers.
</details>

<details>
<summary>✅ Answer</summary>

```python
import os, time
from concurrent.futures import ProcessPoolExecutor

def cpu_sum(n: int) -> int:
    return sum(range(n))

inputs = [1_000_000, 2_000_000, 3_000_000, 4_000_000]

if __name__ == '__main__':
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
        results = list(ex.map(cpu_sum, inputs))
    print(f"Parallel: {time.perf_counter()-start:.2f}s → {results}")
```

**Why:** Each worker process has its own GIL — four `sum(range(n))` calls run on four separate cores simultaneously.
</details>

---

### Q9 🟡 · Guard — if __name__ == '__main__' requirement

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

**Problem:** Write a script that uses `multiprocessing.Pool`. Show the correct placement of the guard. Explain in comments what the `spawn` start method does and why the guard prevents infinite recursion.

<details>
<summary>✅ Answer</summary>

```python
from multiprocessing import Pool

def square(x): return x ** 2

# On Windows/macOS, 'spawn' re-imports this script in each worker.
# Without the guard, workers also execute Pool(4) → spawn more workers → infinite loop.
# The guard ensures only the ORIGINAL script execution creates the pool.

if __name__ == '__main__':
    with Pool(4) as pool:
        print(pool.map(square, range(10)))
```

</details>

---

### Q10 🟡 · Pool — map and starmap

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

**Problem:** Use `Pool.map` to square numbers 1–10. Use `Pool.starmap` to compute `pow(base, exp)` for pairs `[(2,3),(3,4),(4,5)]`. Explain why `starmap` is needed for multi-arg functions.

<details>
<summary>✅ Answer</summary>

```python
from multiprocessing import Pool

def square(x): return x ** 2
def power(base, exp): return base ** exp

if __name__ == '__main__':
    with Pool(4) as pool:
        print(pool.map(square, range(1, 11)))
        print(pool.starmap(power, [(2,3),(3,4),(4,5)]))  # unpacks tuples
```

**Why:** `map` passes one argument per call. `starmap` unpacks each tuple as positional arguments — equivalent to `pool.map(lambda args: power(*args), pairs)` but without the unpicklable lambda.
</details>

---

### Q11 🟡 · IPC — mp.Queue cross-process

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

**Problem:** Child process computes `[n**2 for n in range(5)]` and puts results on `mp.Queue`. Parent collects and prints them.

<details>
<summary>✅ Answer</summary>

```python
import multiprocessing as mp

def worker(q, n):
    for i in range(n): q.put(i ** 2)
    q.put(None)

if __name__ == '__main__':
    q = mp.Queue()
    p = mp.Process(target=worker, args=(q, 5))
    p.start()
    results = []
    while True:
        item = q.get()
        if item is None: break
        results.append(item)
    p.join()
    print(results)
```

</details>

---

### Q12 🟡 · Shared Memory — mp.Value safe increment

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

**Problem:** 4 processes each increment `mp.Value('i', 0)` by 500 using `mp.Lock`. Verify result is 2000.

<details>
<summary>✅ Answer</summary>

```python
import multiprocessing as mp

def inc(counter, lock, n):
    for _ in range(n):
        with lock: counter.value += 1

if __name__ == '__main__':
    counter = mp.Value('i', 0)
    lock = mp.Lock()
    procs = [mp.Process(target=inc, args=(counter, lock, 500)) for _ in range(4)]
    for p in procs: p.start()
    for p in procs: p.join()
    print(counter.value)  # 2000
```

</details>

---

## ## Asyncio Basics (Q13–Q19)

### Q13 🟢 · Coroutine — define and run with asyncio.run()

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)

**Problem:** Write `async def hello(name)` that prints "Hello {name}", awaits 0.1s, prints "Bye {name}", returns "done". Run with `asyncio.run()`.

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def hello(name: str) -> str:
    print(f"Hello {name}")
    await asyncio.sleep(0.1)
    print(f"Bye {name}")
    return "done"

result = asyncio.run(hello("World"))
print(result)
```

</details>

---

### Q14 🟢 · Sleep — asyncio.sleep vs time.sleep

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)

**Problem:** Run 3 tasks of 0.5s each with `asyncio.gather` using `asyncio.sleep`. Total should be ~0.5s. Then replace with `time.sleep` in one task and show it blocks others.

<details>
<summary>✅ Answer</summary>

```python
import asyncio, time

async def good(name): await asyncio.sleep(0.5); print(f"{name} done")
async def bad(name):  time.sleep(0.5); print(f"{name} done")  # blocks loop!

start = time.perf_counter()
asyncio.run(asyncio.gather(good("A"), good("B"), good("C")))
print(f"asyncio.sleep: {time.perf_counter()-start:.2f}s")  # ~0.5s
```

</details>

---

### Q15 🟡 · gather — concurrent API fetches

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)

**Problem:** Three simulated APIs with delays 1.0s, 0.8s, 0.6s. Run sequentially (3 separate awaits) then with `gather`. Print elapsed for both.

<details>
<summary>✅ Answer</summary>

```python
import asyncio, time

async def api(n, delay):
    await asyncio.sleep(delay)
    return n

async def main():
    # Sequential:
    start = time.perf_counter()
    r1 = await api(1, 1.0); r2 = await api(2, 0.8); r3 = await api(3, 0.6)
    print(f"Sequential: {time.perf_counter()-start:.2f}s")

    # Concurrent:
    start = time.perf_counter()
    r1, r2, r3 = await asyncio.gather(api(1,1.0), api(2,0.8), api(3,0.6))
    print(f"Concurrent: {time.perf_counter()-start:.2f}s")

asyncio.run(main())
```

</details>

---

### Q16 🟡 · create_task — background scheduling

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)

**Problem:** Create two tasks with `create_task`. Do sync work in between. Then await both. Show total time is ~max(delays).

<details>
<summary>✅ Answer</summary>

```python
import asyncio, time

async def fetch(name, delay):
    await asyncio.sleep(delay)
    return f"{name} result"

async def main():
    t1 = asyncio.create_task(fetch("A", 0.4))
    t2 = asyncio.create_task(fetch("B", 0.3))
    total = sum(range(10_000))   # sync work while tasks run
    r1, r2 = await t1, await t2
    print(r1, r2)

start = time.perf_counter()
asyncio.run(main())
print(f"{time.perf_counter()-start:.2f}s")  # ~0.4s
```

</details>

---

### Q17 🟡 · wait_for — timeout coroutine

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)

**Problem:** Use `asyncio.wait_for(slow_op(), timeout=0.3)` where `slow_op` takes 1 second. Catch `TimeoutError` and print a message.

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def slow_op():
    await asyncio.sleep(1.0)
    return "done"

async def main():
    try:
        result = await asyncio.wait_for(slow_op(), timeout=0.3)
    except asyncio.TimeoutError:
        print("Timed out after 0.3s")

asyncio.run(main())
```

</details>

---

### Q18 🟡 · async with — async context manager

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)

**Problem:** Create an `AsyncResource` class with `__aenter__` (prints "opened", awaits 0.01s) and `__aexit__` (prints "closed", awaits 0.01s). Use it with `async with`.

<details>
<summary>✅ Answer</summary>

```python
import asyncio

class AsyncResource:
    async def __aenter__(self):
        await asyncio.sleep(0.01)
        print("opened")
        return self
    async def __aexit__(self, *_):
        await asyncio.sleep(0.01)
        print("closed")
        return False

async def main():
    async with AsyncResource() as r:
        print("using resource")

asyncio.run(main())
```

</details>

---

### Q19 🟡 · async for — async generator

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)

**Problem:** Write `async def countdown(n)` that yields n, n-1, ..., 1, awaiting 0.05s between each. Consume with `async for` and print each value.

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def countdown(n: int):
    for i in range(n, 0, -1):
        await asyncio.sleep(0.05)
        yield i

async def main():
    async for value in countdown(5):
        print(value)

asyncio.run(main())
```

</details>

---

## ## concurrent.futures (Q20–Q24)

### Q20 🟡 · as_completed — process in arrival order

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)

**Problem:** Submit 5 tasks with random delays to `ThreadPoolExecutor`. Use `as_completed` to print each result as it arrives. Show arrival order differs from submission order.

<details>
<summary>✅ Answer</summary>

```python
import time, random
from concurrent.futures import ThreadPoolExecutor, as_completed

def task(n):
    time.sleep(random.uniform(0.05, 0.3))
    return n * 10

with ThreadPoolExecutor(max_workers=5) as ex:
    futures = {ex.submit(task, i): i for i in range(1, 6)}
    for f in as_completed(futures):
        print(f"Task {futures[f]}: {f.result()}")
```

</details>

---

### Q21 🟡 · Future API — result, exception, done

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)

**Problem:** Submit a task that raises `ValueError`. Show `f.exception()` returns the exception without re-raising. Show `f.done()` is True. Show `f.result()` re-raises.

<details>
<summary>✅ Answer</summary>

```python
from concurrent.futures import ThreadPoolExecutor

def broken(): raise ValueError("oops")

with ThreadPoolExecutor() as ex:
    f = ex.submit(broken)

print(f.done())           # True
print(f.exception())      # ValueError: oops (doesn't raise)
try:
    f.result()            # raises ValueError
except ValueError as e:
    print(f"result() raised: {e}")
```

</details>

---

### Q22 🟡 · Executor Swap — Thread vs Process

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)

**Problem:** Write code that uses `ThreadPoolExecutor` for I/O work and `ProcessPoolExecutor` for CPU work. Show how swapping executor classes requires changing only one line.

<details>
<summary>✅ Answer</summary>

```python
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def io_task(n): time.sleep(0.1); return n
def cpu_task(n): return sum(i*i for i in range(n))

# For I/O: use Thread (low overhead, GIL released)
with ThreadPoolExecutor(max_workers=4) as ex:
    print(list(ex.map(io_task, range(4))))

# For CPU: swap to Process (each process has own GIL)
if __name__ == '__main__':
    with ProcessPoolExecutor(max_workers=4) as ex:
        print(list(ex.map(cpu_task, [100_000]*4)))
```

</details>

---

### Q23 🟡 · map with timeout

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)

**Problem:** Use `executor.map(fn, items, timeout=0.5)` where one task takes 1 second. Catch the `TimeoutError` raised when iterating results.

<details>
<summary>✅ Answer</summary>

```python
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError

def task(n):
    time.sleep(n)
    return n

with ThreadPoolExecutor(max_workers=3) as ex:
    result_iter = ex.map(task, [0.1, 1.5, 0.2], timeout=0.5)
    try:
        for r in result_iter:
            print(r)
    except TimeoutError:
        print("A task exceeded the 0.5s timeout")
```

</details>

---

### Q24 🟡 · Exception propagation

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)

**Problem:** Submit 3 tasks where the middle one raises. Use `as_completed` and `try/except future.result()` to handle the error and continue processing the others.

<details>
<summary>✅ Answer</summary>

```python
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def task(n):
    time.sleep(0.05)
    if n == 2: raise RuntimeError("task 2 failed")
    return n * 10

with ThreadPoolExecutor() as ex:
    futures = {ex.submit(task, n): n for n in [1, 2, 3]}
    for f in as_completed(futures):
        try:
            print(f"Task {futures[f]}: {f.result()}")
        except RuntimeError as e:
            print(f"Task {futures[f]} error: {e}")
```

</details>

---

## ## Mixed and Advanced (Q25–Q30)

### Q25 🟡 · Decision — choosing the right concurrency model

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)

**Problem:** For each scenario, choose the best tool and explain why:
1. Fetch 100 URLs simultaneously
2. Compress 1,000 image files using Pillow (CPU-bound)
3. A web server handling 10,000 simultaneous connections
4. Run a slow synchronous library from an async app

<details>
<summary>✅ Answer</summary>

```python
# 1. Fetch 100 URLs → asyncio (aiohttp) or ThreadPoolExecutor
#    Pure I/O — asyncio is most scalable (single thread, thousands of connections)
#    ThreadPoolExecutor also works with `requests`

# 2. Compress 1,000 images → ProcessPoolExecutor
#    CPU-bound (image processing), needs true parallelism across cores

# 3. Web server 10,000 connections → asyncio (FastAPI, aiohttp)
#    Each connection spends most time waiting for client data
#    Threads would require 10,000 stacks (~80GB RAM)

# 4. Blocking sync library from async → loop.run_in_executor / asyncio.to_thread
#    Offloads blocking call to thread pool; event loop stays responsive
```

</details>

---

### Q26 🟡 · Bridge — run_in_executor in async code

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)

**Problem:** Write a synchronous `read_csv(path)` that sleeps 0.2s. Call it from an async function without blocking the event loop. Show another coroutine runs concurrently.

<details>
<summary>✅ Answer</summary>

```python
import asyncio, time

def read_csv(path: str) -> list:
    time.sleep(0.2)
    return [{"row": i} for i in range(3)]

async def background():
    await asyncio.sleep(0.1)
    print("background done")

async def main():
    loop = asyncio.get_event_loop()
    csv_task = loop.run_in_executor(None, read_csv, "data.csv")
    await background()         # runs while read_csv blocks in thread
    data = await csv_task
    print(f"Got {len(data)} rows")

asyncio.run(main())
```

</details>

---

### Q27 🟠 · Semaphore — rate-limit async requests

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)

**Problem:** Fetch 12 URLs with `asyncio.Semaphore(4)` limiting to 4 concurrent. Each "fetch" takes 0.1s. Show total time is ~`ceil(12/4) * 0.1 = 0.3s`.

<details>
<summary>✅ Answer</summary>

```python
import asyncio, time

async def fetch(url: str, sem: asyncio.Semaphore) -> str:
    async with sem:
        await asyncio.sleep(0.1)
        return f"ok: {url}"

async def main():
    sem = asyncio.Semaphore(4)
    start = time.perf_counter()
    results = await asyncio.gather(*[fetch(f"url_{i}", sem) for i in range(12)])
    print(f"{len(results)} done in {time.perf_counter()-start:.2f}s")  # ~0.3s

asyncio.run(main())
```

</details>

---

### Q28 🟠 · Deadlock — diagnose and prevent

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)

**Problem:** Create a deadlock: Thread A holds lock_1, waits for lock_2. Thread B holds lock_2, waits for lock_1. Explain the diagnosis. Show the fix: always acquire locks in the same order.

<details>
<summary>✅ Answer</summary>

```python
import threading

lock1 = threading.Lock()
lock2 = threading.Lock()

# DEADLOCK: inconsistent lock ordering
def thread_a_bad():
    with lock1:
        with lock2: pass   # A waits for lock2 held by B

def thread_b_bad():
    with lock2:
        with lock1: pass   # B waits for lock1 held by A

# FIX: consistent lock ordering (always lock1 before lock2)
def thread_a_fixed():
    with lock1:
        with lock2: pass   # both acquire in same order

def thread_b_fixed():
    with lock1:            # same order as A
        with lock2: pass

t1 = threading.Thread(target=thread_a_fixed)
t2 = threading.Thread(target=thread_b_fixed)
t1.start(); t2.start(); t1.join(); t2.join()
print("No deadlock with consistent ordering")
```

**Why:** Deadlock requires a cycle in the lock-wait graph. Consistent ordering breaks all cycles.
</details>

---

### Q29 🟡 · Daemon — daemon vs non-daemon thread behavior

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)

**Problem:** Start a non-daemon thread that sleeps 5 seconds. Show the program waits for it. Then make it daemon — show the program exits immediately without the thread finishing.

<details>
<summary>✅ Answer</summary>

```python
import threading, time

def sleeper(name, delay):
    time.sleep(delay)
    print(f"{name} done")

# Non-daemon: program waits
t = threading.Thread(target=sleeper, args=("non-daemon", 0.2))
t.start(); t.join()
print("after non-daemon join")

# Daemon: program exits without waiting
t = threading.Thread(target=sleeper, args=("daemon", 5.0), daemon=True)
t.start()
print("main done — daemon thread killed on exit")
```

</details>

---

### Q30 🟡 · TaskGroup — structured cancellation (3.11+)

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)

**Problem:** Use `asyncio.TaskGroup` to run 3 tasks. One raises at 0.1s. Show the group cancels the others and raises `ExceptionGroup`.

<details>
<summary>✅ Answer</summary>

```python
import asyncio

async def ok_task(n, delay):
    await asyncio.sleep(delay)
    return n

async def fail_task():
    await asyncio.sleep(0.1)
    raise ValueError("task failed")

async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(ok_task(1, 0.5))
            t2 = tg.create_task(fail_task())
            t3 = tg.create_task(ok_task(3, 0.3))
    except* ValueError as eg:
        print(f"Caught: {eg.exceptions}")

asyncio.run(main())
```

</details>

---

## ## Capstone (Q31–Q35)

### Q31 🟠 · Capstone — Thread-safe counter with full test

> 🛠️ **Solve locally:** [practice_local.py → Q31](./practice_local.py)

**Problem:** Build `ThreadSafeCounter` with `increment()`, `decrement()`, `value` property. Run 5 threads each doing 1000 increments and 500 decrements. Verify final value = 5 * (1000 - 500) = 2500.

<details>
<summary>✅ Answer</summary>

```python
import threading

class ThreadSafeCounter:
    def __init__(self):
        self._val = 0
        self._lock = threading.Lock()
    def increment(self):
        with self._lock: self._val += 1
    def decrement(self):
        with self._lock: self._val -= 1
    @property
    def value(self): return self._val

c = ThreadSafeCounter()
def worker():
    for _ in range(1000): c.increment()
    for _ in range(500):  c.decrement()

threads = [threading.Thread(target=worker) for _ in range(5)]
for t in threads: t.start()
for t in threads: t.join()
print(c.value)  # 2500
```

</details>

---

### Q32 🟠 · Capstone — Parallel prime finder

> 🛠️ **Solve locally:** [practice_local.py → Q32](./practice_local.py)

**Problem:** Find all primes below 500,000 using `ProcessPoolExecutor`. Split range into `cpu_count` chunks, find primes in each chunk, merge. Compare to sequential time.

<details>
<summary>✅ Answer</summary>

```python
import os, math, time
from concurrent.futures import ProcessPoolExecutor

def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(math.sqrt(n))+1, 2):
        if n % i == 0: return False
    return True

def find_in_range(start, end):
    return [n for n in range(start, end) if is_prime(n)]

if __name__ == '__main__':
    N = 500_000
    cores = os.cpu_count()
    chunk = N // cores
    ranges = [(i*chunk, (i+1)*chunk) for i in range(cores-1)] + [((cores-1)*chunk, N)]

    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=cores) as ex:
        chunks = list(ex.map(lambda r: find_in_range(*r), ranges))
    all_primes = [p for c in chunks for p in c]
    print(f"{len(all_primes)} primes in {time.perf_counter()-start:.2f}s")
```

</details>

---

### Q33 🟠 · Capstone — Async batch URL fetcher

> 🛠️ **Solve locally:** [practice_local.py → Q33](./practice_local.py)

**Problem:** Fetch 20 simulated URLs with `asyncio.gather`, semaphore(5), retry on failure (10% failure rate), collect results with `return_exceptions=True`.

<details>
<summary>✅ Answer</summary>

```python
import asyncio, random

sem = asyncio.Semaphore(5)

async def fetch(url: str) -> dict:
    async with sem:
        await asyncio.sleep(random.uniform(0.05, 0.15))
        if random.random() < 0.1:
            raise ConnectionError(f"Failed: {url}")
        return {"url": url, "ok": True}

async def main():
    urls = [f"https://example.com/{i}" for i in range(20)]
    results = await asyncio.gather(*[fetch(u) for u in urls], return_exceptions=True)
    ok = [r for r in results if isinstance(r, dict)]
    fail = [r for r in results if isinstance(r, Exception)]
    print(f"{len(ok)} ok, {len(fail)} failed")

asyncio.run(main())
```

</details>

---

### Q34 🟠 · Capstone — Mixed CPU workers and async I/O

> 🛠️ **Solve locally:** [practice_local.py → Q34](./practice_local.py)

**Problem:** From an async context, run 4 CPU-bound tasks (`sum(range(1M))`) using `loop.run_in_executor(ProcessPoolExecutor())`. Simultaneously run 3 async I/O tasks (sleep 0.2s). Show both complete concurrently.

<details>
<summary>✅ Answer</summary>

```python
import asyncio, time
from concurrent.futures import ProcessPoolExecutor

def cpu_work(n): return sum(range(n))

async def io_task(name, delay):
    await asyncio.sleep(delay)
    return f"{name} done"

async def main():
    loop = asyncio.get_event_loop()
    pool = ProcessPoolExecutor(max_workers=4)

    start = time.perf_counter()
    cpu_futures = [loop.run_in_executor(pool, cpu_work, 1_000_000) for _ in range(4)]
    io_tasks    = [io_task(f"io_{i}", 0.2) for i in range(3)]

    cpu_results, io_results = await asyncio.gather(
        asyncio.gather(*cpu_futures),
        asyncio.gather(*io_tasks),
    )
    print(f"Done in {time.perf_counter()-start:.2f}s")
    pool.shutdown()

asyncio.run(main())
```

</details>

---

### Q35 🟠 · Capstone — Concurrency decision tree

> 🛠️ **Solve locally:** [practice_local.py → Q35](./practice_local.py)

**Problem:** Write a `choose_executor(task_type, n_tasks, uses_async_lib)` function that returns a recommendation string. Cover: CPU-bound, I/O-bound with sync library, I/O-bound with async library, mixed.

<details>
<summary>✅ Answer</summary>

```python
def choose_executor(task_type: str, n_tasks: int, uses_async_lib: bool) -> str:
    if task_type == "cpu":
        return (
            "ProcessPoolExecutor — each process has own GIL, true parallelism. "
            f"Use max_workers=os.cpu_count(). {'chunksize helpful' if n_tasks > 100 else ''}"
        )
    elif task_type == "io" and uses_async_lib:
        return (
            "asyncio.gather / asyncio.create_task — single thread, "
            f"scales to {'thousands' if n_tasks > 100 else 'hundreds'} of concurrent ops. "
            "Use asyncio.Semaphore to cap concurrency."
        )
    elif task_type == "io" and not uses_async_lib:
        return (
            "ThreadPoolExecutor — GIL released during I/O, good enough for sync libraries. "
            f"max_workers=min(32, n_tasks) for {n_tasks} tasks."
        )
    elif task_type == "mixed":
        return (
            "asyncio + loop.run_in_executor(ProcessPoolExecutor) — "
            "event loop handles I/O; CPU work offloaded to process pool. "
            "Bridge: asyncio.to_thread for sync libs."
        )
    return "Unknown task type"

print(choose_executor("cpu", 1000, False))
print(choose_executor("io", 500, True))
print(choose_executor("io", 20, False))
print(choose_executor("mixed", 100, True))
```

**Why:** The right tool depends on whether bottleneck is CPU or waiting, whether libraries are async-native, and scale requirements.
</details>

---

## Deep Dives

| Subfolder | Focus |
|---|---|
| [01_threading/practice.md](./01_threading/practice.md) | 15 threading exercises (Lock, Queue, Event, RLock, daemon, cache) |
| [02_multiprocessing/practice.md](./02_multiprocessing/practice.md) | 15 multiprocessing exercises (Pool, IPC, shared memory, error handling) |
| [03_asyncio/practice.md](./03_asyncio/practice.md) | 15 asyncio exercises (gather, TaskGroup, Semaphore, async generators) |

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 💻 Practice Local | [practice_local.py](./practice_local.py) |
| 🧵 Threading Deep Dive | [01_threading/practice.md](./01_threading/practice.md) |
| 🔥 Multiprocessing Deep Dive | [02_multiprocessing/practice.md](./02_multiprocessing/practice.md) |
| ⚡ Asyncio Deep Dive | [03_asyncio/practice.md](./03_asyncio/practice.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🔥 Interview Q&A | [interview.md](./interview.md) |

---

**[Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) | **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md) · [Threading](./01_threading/theory.md) · [Multiprocessing](./02_multiprocessing/theory.md) · [Asyncio](./03_asyncio/theory.md)
