<a id="top"></a>
# 🚀 Performance Optimization in Python

> *"Measure first, then optimize. Premature optimization is the root of all evil.*
> *Fast code is good. Correct and maintainable code is better. Balanced code is best."*

## 📖 Table of Contents

- [1. timeit — Measuring Performance](#1-timeit--measuring-performance)
- [2. cProfile — Function-Level Profiling](#2-cprofile--function-level-profiling)
- [3. Understanding Profiling Output](#3-understanding-profiling-output)
- [4. Line-by-Line Profiling](#4-line-by-line-profiling)
- [5. Memory Profiling](#5-memory-profiling)
- [6. Algorithm Optimization](#6-algorithm-optimization)
- [7. Common Optimization Techniques](#7-common-optimization-techniques)
  - [Use Built-in Functions](#use-built-in-functions)
  - [List Comprehensions vs Loops](#list-comprehensions-vs-loops)
  - [Generator Expressions](#generator-expressions)
  - [Avoid Repeated Computation — lru_cache](#avoid-repeated-computation--lru_cache)
- [8. CPU vs Memory Trade-off](#8-cpu-vs-memory-trade-off)
- [9. Avoid Premature Optimization](#9-avoid-premature-optimization)
- [10. Concurrency for Performance](#10-concurrency-for-performance)
- [11. Efficient Data Structures](#11-efficient-data-structures)
- [12. Avoid Global Lookups in Loops](#12-avoid-global-lookups-in-loops)
- [13. C Extensions, NumPy, PyPy](#13-c-extensions-numpy-pypy)
- [14. Real Production Scenarios](#14-real-production-scenarios)
  - [Slow API Response](#slow-api-response)
  - [Data Pipeline Too Slow](#data-pipeline-too-slow)
  - [Memory Usage Too High](#memory-usage-too-high)
- [15. Common Performance Mistakes](#15-common-performance-mistakes)
  - [📂 Subfolder Deep Dives](#-subfolder-deep-dives)
  - [🔥 Summary](#-summary)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`cProfile` / `profile` · `timeit` · Algorithmic complexity (choose right data structure) · Generator vs list trade-off

**Should Learn** — Important for real projects, comes up regularly:
`memory_profiler` · `tracemalloc` · `__slots__` · `functools.lru_cache` / `cache` · `dis` module (bytecode inspection)

**Good to Know** — Useful in specific situations:
`py-spy` sampling profiler · Flamegraph interpretation · `scalene` · Numba JIT basics

**Reference** — Know it exists, look up when needed:
NUMA awareness · SIMD vectorization · `numexpr` · Escape analysis

---

<a id="why-performance-optimization-matters"></a>
## 🎬 Why Performance Optimization Matters

Imagine your pizza delivery app is running fine — orders arrive in 200ms, customers are happy. You add a new "track your driver" feature. Suddenly orders take 3 seconds. Customers start cancelling. Servers overheat. AWS bills double. The app didn't break — it just got slow, and slow is the silent killer of user experience and operating costs. Performance optimization is the discipline of finding exactly where the slowness lives and fixing it without breaking everything else.

Your API takes 200ms → users are happy.
After a new feature → it takes 3 seconds.

Now:
- Users complain, conversion rate drops
- CPU usage spikes → server costs increase
- Scaling becomes expensive
- Real-time systems miss SLA targets

Performance matters in: APIs · Data pipelines · ML systems · High-traffic services · Real-time systems

> **Premature optimization is the root of all evil — Knuth**
> Measure first. Then optimize. Never guess.

---

<a id="1-timeit--measuring-performance"></a>
# 1. timeit — Measuring Performance

Before you can fix a performance problem, you need to measure it accurately. Think of a doctor who can't guess a patient's temperature — they use a thermometer. `timeit` is your thermometer for Python code. It runs your code thousands of times and reports the best (most reliable) time, filtering out the noise from OS scheduling and garbage collection.

```python
import timeit

# Quick one-liner timing:
timeit.timeit("sum(range(1000))", number=10_000)
# → 0.123   (seconds for 10,000 runs)

# Multi-line setup:
timeit.timeit(
    stmt="[x**2 for x in data]",
    setup="data = list(range(1000))",
    number=10_000
)

# Use timeit.repeat() + min() for reliable results:
times = timeit.repeat(
    stmt="[x**2 for x in data]",
    setup="data = list(range(1000))",
    repeat=5,
    number=10_000
)
print(min(times))   # ← always use min(), not mean
# The minimum reflects best available CPU time.
# Higher values are OS noise and GC pauses — not your code's fault.

# Command-line:
# python -m timeit -s "data = list(range(1000))" "[x**2 for x in data]"
```

**Comparing two approaches head-to-head:**

```python
import timeit

def time_comparison(approaches: dict, setup="", number=100_000):
    results = {}
    for name, stmt in approaches.items():
        t = min(timeit.repeat(stmt, setup=setup, repeat=5, number=number))
        results[name] = t
    # Sort by speed:
    for name, t in sorted(results.items(), key=lambda x: x[1]):
        print(f"{name:30s} {t*1000:.3f} ms")

time_comparison({
    "list comprehension":   "[x**2 for x in data]",
    "map()":                "list(map(lambda x: x**2, data))",
    "for loop":             "r=[]\nfor x in data: r.append(x**2)",
}, setup="data = list(range(1000))")
# list comprehension          4.123 ms
# map()                       5.891 ms
# for loop                    7.234 ms
```

⚠️ **Common Mistake:** Using `time.time()` to benchmark micro-operations. `time.time()` has millisecond resolution and captures wall-clock time including OS scheduling. Use `timeit` for anything under ~1 second.

💡 **Hint:** Always use `min()` from `timeit.repeat()`, never the mean. The minimum is the closest to the true CPU cost. The mean includes garbage collection pauses and OS interrupts that aren't part of your code's performance.

📝 **Practice:** [Q5 — timeit repeat and min](./practice.md#q5--timeit-repeat-and-min-)

> [↑ Back to Top](#top)

---

<a id="2-cprofile--function-level-profiling"></a>
# 2. cProfile — Function-Level Profiling

`timeit` tells you how fast one expression runs. But in a real program with hundreds of functions, you don't know which one is slow. `cProfile` is like a spy that follows your entire program and takes notes on every function call: how many times it was called, how long it spent there, and how much time trickled down from its sub-calls. Run it once on a real workload and the bottleneck usually jumps out immediately.

```python
import cProfile
import pstats
from io import StringIO

# Simple run:
cProfile.run("my_function()")

# With pstats for sorted analysis:
profiler = cProfile.Profile()
profiler.enable()

my_function()   # ← code to profile

profiler.disable()

stream = StringIO()
stats = pstats.Stats(profiler, stream=stream)
stats.sort_stats("cumulative")   # sort by cumulative time
stats.print_stats(20)            # top 20 functions
print(stream.getvalue())

# As a decorator (reusable):
import functools

def profile(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        pr.print_stats(sort="cumulative")
        return result
    return wrapper

@profile
def expensive_function():
    return sum(i**2 for i in range(1_000_000))
```

**Command-line profiling:**

```bash
python -m cProfile -s cumulative my_script.py
python -m cProfile -o output.prof my_script.py   # save to file
python -m pstats output.prof                      # interactive viewer
```

⚠️ **Common Mistake:** Profiling your entire application including startup and imports. Profile only the specific operation that's slow — wrap just the hot path in `profiler.enable()` / `profiler.disable()`.

💡 **Hint:** `cProfile` adds overhead (it instruments every function call). For production profiling, use `py-spy` (sampling profiler — zero overhead, attaches to running processes without code changes).

📝 **Practice:** [Q2 — pstats output](./practice.md#q2--read-pstats-output-) · [Q72 · profiling](../python_practice_questions_100.md#q72--normal--profiling)

> [↑ Back to Top](#top)

---

<a id="3-understanding-profiling-output"></a>
# 3. Understanding Profiling Output

Reading a profiling report is like reading a restaurant bill — you need to know what each line item means before you know where to cut costs. The most important columns in cProfile output tell you not just how long a function ran, but whether that time was spent there directly or was accumulated from calling other functions.

```
ncalls  tottime  percall  cumtime  percall  filename:lineno(function)
──────  ───────  ───────  ───────  ───────  ────────────────────────────────
  1000    0.045    0.000    2.345    0.002  mymodule.py:42(process_records)
     1    0.001    0.001    2.300    2.300  mymodule.py:10(run_pipeline)
  1000    2.280    0.002    2.280    0.002  mymodule.py:67(slow_query)
```

**Column meanings:**

```
┌───────────────────────────────────────────────────────────────────────┐
│  ncalls   → how many times this function was called                   │
│  tottime  → time spent INSIDE this function (excluding sub-calls)     │
│  percall  → tottime / ncalls                                          │
│  cumtime  → TOTAL time including all sub-calls (the important one)    │
│  percall  → cumtime / ncalls                                          │
│                                                                       │
│  Where to look first:                                                 │
│  1. Sort by cumtime — highest cumtime = biggest bottleneck            │
│  2. Find functions with high tottime — they're slow themselves        │
│  3. Find functions with high ncalls × tottime — called too often      │
└───────────────────────────────────────────────────────────────────────┘
```

**pstats sorting options:**

```python
stats.sort_stats("cumulative")  # total time including sub-calls ← start here
stats.sort_stats("tottime")     # time inside function only
stats.sort_stats("ncalls")      # most called functions
stats.sort_stats("filename")    # alphabetical by file
```

💡 **Hint:** `cumtime` is usually your first filter — it tells you where overall time is being spent. Then drill into the high-`cumtime` functions using `stats.print_callers("slow_function")` to see what's calling it.

📝 **Practice:** [Q3 — sort pstats output](./practice.md#q3--sort-pstats-output-)

> [↑ Back to Top](#top)

---

<a id="4-line-by-line-profiling"></a>
# 4. Line-by-Line Profiling

`cProfile` tells you which function is slow. But a 50-line function might have 49 fast lines and 1 catastrophically slow one. `line_profiler` goes one level deeper — it shows you the time spent on every single line. Think of it like switching from a city-level map to a street-level view.

```bash
pip install line-profiler
```

```python
# Decorate the function you want to profile:
@profile   # added by line_profiler — not imported, injected at runtime
def process_data(records):
    result = []                          # line 1
    for record in records:               # line 2
        cleaned = record.strip()         # line 3
        parsed  = json.loads(cleaned)    # line 4  ← SLOW: 95% of time here
        result.append(parsed["value"])   # line 5
    return result

# Run with kernprof:
# kernprof -l -v my_script.py

# Output:
# Line #  Hits    Time   Per Hit  % Time  Line Contents
# ─────────────────────────────────────────────────────────
#      3  10000   1200    0.120     1.2   cleaned = record.strip()
#      4  10000  95000    9.500    95.0   parsed = json.loads(cleaned)  ← target
#      5  10000   3800    0.380     3.8   result.append(parsed["value"])
```

💡 **Hint:** Only decorate the function you suspect is slow — `line_profiler` adds significant overhead to every decorated line. Profile one function at a time.

🔍 **Good to Know:** `scalene` is a newer profiler that combines line-level CPU profiling with memory profiling in a single tool, with minimal overhead. Worth knowing for production use.

📝 **Practice:** [Q7 — line_profiler](./practice.md#q7--line_profiler-)

> [↑ Back to Top](#top)

---

<a id="5-memory-profiling"></a>
# 5. Memory Profiling

Performance isn't only CPU. A program that runs fast but gradually eats all available memory will eventually crash — or worse, slow to a crawl as the OS starts swapping. Memory profiling is like checking a water tank for leaks: you measure the level before and after operations, and anything that keeps growing unexpectedly is your leak.

**`tracemalloc` — built-in, no install needed:**

```python
import tracemalloc

tracemalloc.start()

# --- Code to profile ---
data = [{"id": i, "value": i * 2} for i in range(100_000)]
result = [d["value"] for d in data]
# --- End of code ---

snapshot = tracemalloc.take_snapshot()
stats = snapshot.statistics("lineno")

print("Top 5 memory allocations:")
for stat in stats[:5]:
    print(stat)
# output.py:7: size=7.6 MiB, count=100003, average=79 B
```

**`tracemalloc` before/after comparison:**

```python
import tracemalloc

tracemalloc.start()
snapshot1 = tracemalloc.take_snapshot()

# ... run operation ...
create_large_cache()

snapshot2 = tracemalloc.take_snapshot()
top_stats = snapshot2.compare_to(snapshot1, "lineno")

print("Memory growth:")
for stat in top_stats[:10]:
    print(stat)
```

**`memory_profiler` — line-by-line memory usage:**

```bash
pip install memory-profiler
```

```python
from memory_profiler import profile

@profile
def create_data():
    a = [1] * 1_000_000       # Line 3
    b = [2] * 5_000_000       # Line 4
    del a                      # Line 5
    return b

# Output:
# Line #   Mem usage   Increment   Line Contents
# ───────────────────────────────────────────────
#      3   50.0 MiB   +7.6 MiB   a = [1] * 1_000_000
#      4   88.3 MiB   +38.3 MiB  b = [2] * 5_000_000
#      5   80.7 MiB   -7.6 MiB   del a
```

⚠️ **Common Mistake:** Assuming a function is memory-efficient because it returns a small value. The peak memory during execution (before cleanup) is what can cause crashes. `memory_profiler` shows the peak, not just the final state.

💡 **Hint:** `tracemalloc` is the right tool for finding memory leaks in production — it's built-in and low overhead. Use `memory_profiler` during development when you need line-level visibility.

📝 **Practice:** [Q9 — tracemalloc](./practice.md#q9--tracemalloc-)

> [↑ Back to Top](#top)

---

<a id="6-algorithm-optimization"></a>
# 6. Algorithm Optimization

Before micro-optimizing any line of code, check your algorithm. A badly chosen algorithm is like taking a scenic route to a fire — no amount of speeding up your driving helps if you're going the wrong way. Switching from O(n²) to O(n log n) on 1 million items is a 50,000× speedup that no micro-optimization can match.

```python
# ❌ O(n²) — checking duplicates with nested loop:
def has_duplicates_slow(items):
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                return True
    return False

# ✅ O(n) — same result, set lookup:
def has_duplicates_fast(items):
    seen = set()
    for item in items:
        if item in seen:
            return True
        seen.add(item)
    return False

# Benchmark:
# n=10,000: slow=0.45s, fast=0.001s → 450x speedup

# ❌ O(n) per lookup — list membership test:
data = list(range(1_000_000))
if 999_999 in data:   # scans entire list
    pass

# ✅ O(1) per lookup — set membership:
data_set = set(range(1_000_000))
if 999_999 in data_set:   # instant hash lookup
    pass
```

```
┌────────────── Data Structure Time Complexity ──────────────────────┐
│                                                                     │
│  Operation          list      set       dict      deque            │
│  ──────────────────────────────────────────────────────────────    │
│  Membership (in)    O(n)      O(1)      O(1)      O(n)             │
│  Append             O(1)*     O(1)*     O(1)*     O(1)             │
│  Insert at front    O(n)      -         -         O(1)             │
│  Remove by value    O(n)      O(1)*     O(1)      O(n)             │
│  Access by index    O(1)      -         O(1)      O(1)             │
│  Sort               O(n logn) -         -         -                │
│  (* = amortized)                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

💡 **Hint:** The single highest-ROI optimization in Python: replace `list` with `set` for membership testing. If your code has `if item in some_list` in a loop, converting `some_list` to a `set` once can turn an O(n²) operation into O(n).

📝 **Practice:** [Q15 — dict vs list lookup](./practice.md#q15--dict-vs-list-lookup-) · [Q73 · complexity-in-practice](../python_practice_questions_100.md#q73--thinking--complexity-in-practice)

> [↑ Back to Top](#top)

---

<a id="7-common-optimization-techniques"></a>
# 7. Common Optimization Techniques

Think of these techniques like a mechanic's toolkit. You don't use every tool on every car — you reach for the right one based on what the diagnostic says is wrong. Each technique here targets a specific type of slowness: wrong data structure, redundant computation, slow Python loops, unnecessary memory allocation.

<a id="use-built-in-functions"></a>
## Use Built-in Functions

Built-in functions (`sum`, `map`, `filter`, `sorted`, `min`, `max`, `any`, `all`) are implemented in C and run significantly faster than equivalent Python loops. Prefer them whenever possible.

```python
data = list(range(1_000_000))

# ❌ Python loop:
total = 0
for x in data:
    total += x

# ✅ Built-in (C implementation):
total = sum(data)   # 3-5x faster

# ❌ Python loop for max:
result = data[0]
for x in data:
    if x > result:
        result = x

# ✅ Built-in:
result = max(data)
```

<a id="list-comprehensions-vs-loops"></a>
## List Comprehensions vs Loops

List comprehensions run faster than equivalent `for` loops because they're optimized at the bytecode level — the loop overhead is minimized and the list is pre-allocated.

```python
# ❌ for loop with append:
squares = []
for x in range(10_000):
    squares.append(x ** 2)

# ✅ List comprehension (~30-50% faster):
squares = [x ** 2 for x in range(10_000)]

# ✅ With filter:
evens = [x for x in range(10_000) if x % 2 == 0]
```

<a id="generator-expressions"></a>
## Generator Expressions

When you only need to iterate once and don't need the full list in memory, generator expressions give you the same data lazily — using a fraction of the memory.

```python
# List — creates full 10M integers in memory:
total = sum([x ** 2 for x in range(10_000_000)])   # ~400 MB

# Generator — computes one at a time, near-zero memory:
total = sum(x ** 2 for x in range(10_000_000))      # ~1 KB

# When to use list vs generator:
# List:      need random access (data[i]), need len(), iterate multiple times
# Generator: iterate once, memory-constrained, pipeline of transforms
```

<a id="avoid-repeated-computation--lru_cache"></a>
## Avoid Repeated Computation — lru_cache

If a pure function is called with the same arguments repeatedly, caching the result eliminates all repeated work. `functools.lru_cache` does this with one decorator.

```python
from functools import lru_cache, cache
import time

# Without cache — called 1024 times for fib(10):
def fib_slow(n):
    if n <= 1: return n
    return fib_slow(n-1) + fib_slow(n-2)

# With cache — called 11 times for fib(10):
@lru_cache(maxsize=128)   # or @cache for unlimited
def fib_fast(n):
    if n <= 1: return n
    return fib_fast(n-1) + fib_fast(n-2)

# Check cache performance:
fib_fast(30)
print(fib_fast.cache_info())
# CacheInfo(hits=28, misses=31, maxsize=128, currsize=31)
# hits=28 means 28 calls were served from cache
```

⚠️ **Common Mistake:** Applying `lru_cache` to functions with mutable arguments (lists, dicts). Cache keys must be hashable — passing a list raises `TypeError: unhashable type: 'list'`. Only works with immutable arguments.

💡 **Hint:** `@cache` (Python 3.9+) is `@lru_cache(maxsize=None)` — unlimited cache size. Use `@lru_cache(maxsize=N)` when memory is a concern and you only need the N most recent results.

📝 **Practice:** [Q16 — generator expressions](./practice.md#q16--generator-expressions-) · [Q21 — lru_cache](./practice.md#q21--lru_cache-)

> [↑ Back to Top](#top)

---

<a id="8-cpu-vs-memory-trade-off"></a>
# 8. CPU vs Memory Trade-off

In engineering, resources trade off against each other — you can buy speed by spending memory, or save memory by spending CPU cycles. A cache is the classic example: you use extra memory (store computed results) to avoid repeating CPU work. Understanding this trade-off lets you make conscious decisions instead of accidentally paying twice.

```
┌──────────────── CPU vs Memory Trade-off Examples ──────────────────┐
│                                                                     │
│  MORE MEMORY → LESS CPU:                                            │
│  - lru_cache: store results → skip recomputation                   │
│  - Precomputed lookup tables → O(1) instead of O(log n)            │
│  - Materialized views in DB → skip JOIN on every query             │
│  - Index structures → skip full scan                               │
│                                                                     │
│  MORE CPU → LESS MEMORY:                                            │
│  - Generator instead of list → compute on demand                   │
│  - Stream processing → don't load full file                        │
│  - Compress before storing → smaller footprint                     │
│  - Recompute instead of cache → when memory is scarce              │
│                                                                     │
│  Decision: where is your bottleneck?                                │
│  Out of memory? → reduce caching, use generators                   │
│  CPU bound?     → add caching, precompute, vectorize               │
└─────────────────────────────────────────────────────────────────────┘
```

💡 **Hint:** Profile first to know which resource is your bottleneck. Adding a cache when memory is already the problem makes things worse, not better.

> [↑ Back to Top](#top)

---

<a id="9-avoid-premature-optimization"></a>
# 9. Avoid Premature Optimization

Think of optimization like renovating a house. You don't tear out the plumbing before you know if it's actually leaking. The same logic applies to code: optimizing code that isn't actually a bottleneck wastes time, adds complexity, and makes code harder to read — all for zero measurable benefit. The discipline is knowing when to optimize, not how.

```
┌──────────────────── Optimization Decision Flow ────────────────────┐
│                                                                     │
│  Is there a performance problem?                                    │
│      NO  → don't optimize. Write clear, correct code.              │
│      YES ↓                                                          │
│                                                                     │
│  Do you have a profiling report?                                    │
│      NO  → measure first. Don't guess.                             │
│      YES ↓                                                          │
│                                                                     │
│  Is the hotspot in your code (not a dependency)?                   │
│      NO  → file a bug upstream or find a faster library.           │
│      YES ↓                                                          │
│                                                                     │
│  Optimize the specific bottleneck. Measure again.                  │
│  Was the improvement worth the code complexity?                    │
│      NO  → revert. Keep the clear version.                         │
│      YES → ship it.                                                 │
└─────────────────────────────────────────────────────────────────────┘
```

**Optimize when:**
- You have a measurable bottleneck from profiling
- Performance is business-critical (SLA, user experience, cost)
- The system needs to scale 10× and current approach won't hold

**Do NOT optimize:**
- Early prototypes (requirements will change)
- Trivial scripts that run once
- Based on assumptions without measurement
- Code that's already fast enough

⚠️ **Common Mistake:** Switching from a list comprehension to `map()` because "map is faster" — without measuring. In Python 3, `map()` returns an iterator and is not inherently faster than a list comprehension once you materialize it. Always measure the specific case.

> [↑ Back to Top](#top)

---

<a id="10-concurrency-for-performance"></a>
# 10. Concurrency for Performance

Some performance problems can't be solved by faster code — they need to be solved architecturally. If your program spends 80% of its time waiting for database responses, no amount of algorithmic optimization helps. The solution is doing multiple things at once. The right tool depends on what's slow: waiting for I/O, or burning CPU.

```
┌──────────────── Choosing the Right Concurrency Model ──────────────┐
│                                                                     │
│  I/O-bound (waiting for network, DB, disk):                        │
│  → asyncio:    single thread, many concurrent operations           │
│  → threading:  multiple threads, GIL released during I/O waits     │
│                                                                     │
│  CPU-bound (number crunching, data transformation):                │
│  → multiprocessing: bypass GIL, true parallelism                   │
│  → concurrent.futures.ProcessPoolExecutor                          │
│                                                                     │
│  Mixed workloads:                                                   │
│  → asyncio + run_in_executor (offload CPU to thread/process pool)  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

# I/O-bound: async + aiohttp
async def fetch_all(urls: list[str]) -> list[dict]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in urls]
        return await asyncio.gather(*tasks)   # all run concurrently

# CPU-bound: process pool
def cpu_heavy(data):
    return sum(x**2 for x in data)

with ProcessPoolExecutor(max_workers=4) as pool:
    chunks = [data[i::4] for i in range(4)]       # split work
    results = list(pool.map(cpu_heavy, chunks))    # parallel execution

# Mixed: offload CPU work from async event loop
async def process_request(data):
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, cpu_heavy, data)
    return result
```

💡 **Hint:** Profile first to confirm whether you're I/O-bound or CPU-bound. Adding threads to a CPU-bound program makes it slower (GIL contention). Adding async to a CPU-bound program makes no difference (async doesn't bypass the GIL).

📝 **Practice:** [Q26 — run_in_executor](./practice.md#q26--run_in_executor-)

> [↑ Back to Top](#top)

---

<a id="11-efficient-data-structures"></a>
# 11. Efficient Data Structures

Think of data structures like different types of storage at a warehouse. A pile on the floor (list) is fine for small amounts — you can find anything if you dig. But with 10,000 items, you want labeled shelves (dict) for instant retrieval, a sorted catalog (sorted list + bisect) for ordered searches, or a conveyor belt (deque) for fast front-and-back access. The choice of container is often more impactful than any code optimization.

```python
from collections import deque, defaultdict, Counter
import heapq

# Membership testing — O(n) vs O(1):
allowed_ids = [1, 2, 3, ...]    # ❌ O(n) membership test
allowed_ids = {1, 2, 3, ...}    # ✅ O(1) membership test

# Frequency counting — manual vs Counter:
# ❌ Manual:
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1

# ✅ Counter (C-optimized):
counts = Counter(words)
counts.most_common(10)   # top 10 words

# Fast queue (pop from front) — list vs deque:
# ❌ list.pop(0) is O(n) — shifts all elements:
queue = []
queue.pop(0)

# ✅ deque.popleft() is O(1):
queue = deque()
queue.appendleft(item)
queue.popleft()          # O(1) always

# Priority queue — sorted list vs heapq:
# heapq.heappush/heappop: O(log n) — correct tool for priority queues
import heapq
heap = []
heapq.heappush(heap, (priority, item))
priority, item = heapq.heappop(heap)

# Grouping — manual loop vs defaultdict:
# ❌ Manual:
groups = {}
for item in items:
    if item["category"] not in groups:
        groups[item["category"]] = []
    groups[item["category"]].append(item)

# ✅ defaultdict:
groups = defaultdict(list)
for item in items:
    groups[item["category"]].append(item)
```

⚠️ **Common Mistake:** Using a list for a queue (FIFO). `list.pop(0)` removes the first element by shifting all remaining elements left — O(n). For any queue with frequent front-removals, use `collections.deque`.

📝 **Practice:** [Q74 · performance-bug](../python_practice_questions_100.md#q74--debug--performance-bug)

> [↑ Back to Top](#top)

---

<a id="12-avoid-global-lookups-in-loops"></a>
# 12. Avoid Global Lookups in Loops

Every time Python evaluates `math.sqrt`, it performs two dictionary lookups: find `math` in the global namespace, then find `sqrt` in `math`'s namespace. In a tight loop that runs a million times, those two lookups happen a million times each. Storing the function reference in a local variable before the loop costs one lookup and pays for itself after the second iteration.

```python
import math

# ❌ Global lookup on every iteration:
def compute_slow(data):
    result = []
    for x in data:
        result.append(math.sqrt(x))   # 2 lookups per iteration
    return result

# ✅ Cache reference before loop:
def compute_fast(data):
    sqrt = math.sqrt           # 1 lookup — done
    append = [].append         # also cache append
    result = []
    for x in data:
        result.append(sqrt(x)) # local variable lookup only
    return result

# ✅ Even better — list comprehension (fastest for this case):
def compute_fastest(data):
    sqrt = math.sqrt
    return [sqrt(x) for x in data]

# Benchmark on 1,000,000 items:
# compute_slow:    0.42s
# compute_fast:    0.28s  (1.5x faster)
# compute_fastest: 0.19s  (2.2x faster)
```

🔍 **Good to Know:** This is a micro-optimization — it only matters in hot loops that run millions of times. Don't apply it preemptively; apply it after profiling confirms the loop is a bottleneck.

📝 **Practice:** [Q20 — local variable fast path](./practice.md#q20--local-variable-fast-path-)

> [↑ Back to Top](#top)

---

<a id="13-c-extensions-numpy-pypy"></a>
# 13. C Extensions, NumPy, PyPy

When pure Python optimization has taken you as far as it can go, the next step is to leave the Python runtime behind — at least for the hot path. NumPy moves numeric computation into C. Cython compiles Python-like code to C. PyPy JIT-compiles Python code to native machine code. Each approach has different trade-offs in complexity, compatibility, and speedup.

```python
# NumPy vectorization — replaces Python loops with C-level operations:
import numpy as np

data = list(range(1_000_000))

# ❌ Pure Python loop:
result = [x ** 2 for x in data]          # ~0.35s

# ✅ NumPy — operates on entire array at once (no Python loop):
arr = np.array(data)
result = arr ** 2                         # ~0.005s — 70x faster

# NumPy broadcasting:
matrix = np.random.rand(1000, 1000)
row_means = matrix.mean(axis=1)           # C loop over 1M values
normalized = matrix - row_means[:, np.newaxis]  # broadcast
```

```
┌──────────── When to Reach Beyond Pure Python ──────────────────────┐
│                                                                     │
│  Approach      Speedup   Complexity   Use Case                     │
│  ──────────────────────────────────────────────────────────────    │
│  NumPy         10-100x   Low          Numeric arrays, ML, science  │
│  Cython        10-100x   High         Hot loops, custom C types    │
│  PyPy          2-10x     Medium       General Python, no C exts    │
│  Numba JIT     10-100x   Medium       Numeric loops, GPU offload   │
│  C extension   Max       Very high    Absolute max perf needed     │
│                                                                     │
│  Start with NumPy. Only go deeper if NumPy isn't enough.           │
└─────────────────────────────────────────────────────────────────────┘
```

💡 **Hint:** The golden rule for NumPy performance: eliminate Python loops. Any `for x in array` loop should be a vectorized NumPy operation. If you can't express it as a vectorized operation, consider Numba (`@numba.jit`) which can JIT-compile the loop to native code.

📝 **Practice:** [Q27 — numpy vectorization](./practice.md#q27--numpy-vectorization-)

> [↑ Back to Top](#top)

---

<a id="14-real-production-scenarios"></a>
# 14. Real Production Scenarios

Performance problems in production rarely announce themselves clearly. They show up as slow API responses, user complaints, infrastructure bills, or mysterious timeouts. Each symptom points to a different root cause and a different optimization strategy. Here are the three most common patterns and how to diagnose and fix each.

<a id="slow-api-response"></a>
## Slow API Response

```
Symptom: API endpoint takes 2-3 seconds instead of < 200ms

Diagnosis workflow:
1. Add request timing middleware → confirm which endpoint
2. cProfile the endpoint handler → find the hot function
3. Usually: N+1 DB queries, missing index, no caching

Fixes:
- DB query optimization: add index, use SELECT only needed columns
- N+1 → use JOIN or bulk fetch
- Add Redis cache for expensive repeated queries
- Add response cache for rarely-changing data (TTL-based)
```

```python
# N+1 problem — classic API performance killer:
# ❌ N+1: 1 query for users + N queries for each user's orders:
users = db.query("SELECT * FROM users")
for user in users:
    user["orders"] = db.query(f"SELECT * FROM orders WHERE user_id={user['id']}")

# ✅ JOIN: 1 query:
users_with_orders = db.query("""
    SELECT u.*, o.id as order_id, o.total
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
""")
```

<a id="data-pipeline-too-slow"></a>
## Data Pipeline Too Slow

```
Symptom: ETL job that took 2 hours now takes 8 hours as data grew

Diagnosis:
1. Check algorithm complexity: O(n²) step hidden in pipeline?
2. Profile the pipeline: which stage is the bottleneck?
3. Check memory: is the process swapping to disk?

Fixes:
- Replace O(n²) deduplication with set-based O(n)
- Switch list → generator for streaming large files
- Parallelize independent stages with ProcessPoolExecutor
- Use pandas/numpy for bulk transformations instead of row-by-row loops
```

```python
# ❌ Loading entire 10GB file into memory:
with open("huge_file.csv") as f:
    all_rows = f.readlines()   # 10GB in RAM
    process(all_rows)

# ✅ Stream with generator:
def stream_csv(path):
    with open(path) as f:
        for line in f:             # reads one line at a time
            yield parse_line(line) # memory: one row at a time

for record in stream_csv("huge_file.csv"):
    process(record)
```

<a id="memory-usage-too-high"></a>
## Memory Usage Too High

```
Symptom: Process uses 8GB RAM for a task that should need 500MB

Diagnosis:
1. tracemalloc snapshot before/after → find growing allocations
2. Look for accidental references keeping large objects alive
3. Check for unbounded caches or accumulating lists

Fixes:
- Replace lists with generators where single-pass is enough
- Use __slots__ for classes with millions of instances
- Clear unused references explicitly (del large_obj)
- Use weakref for caches that shouldn't prevent GC
```

```python
import sys

# Check object sizes:
data = list(range(1_000_000))
gen  = (x for x in range(1_000_000))
print(sys.getsizeof(data))   # ~8.5 MB
print(sys.getsizeof(gen))    # ~112 bytes
```

💡 **Hint:** For API performance, add structured logging with timing at each major step (`time.perf_counter()` before and after DB calls, external service calls). In production this is far more useful than running cProfile — you get real traffic timing without overhead.

📝 **Practice:** [Q87 · caching-scenario](../python_practice_questions_100.md#q87--design--caching-scenario) · [Q97 · design-decision-cache](../python_practice_questions_100.md#q97--design--design-decision-cache) · [Q22 — __slots__ memory](./practice.md#q22--slots-memory-)

> [↑ Back to Top](#top)

---

<a id="15-common-performance-mistakes"></a>
# 15. Common Performance Mistakes

Every performance mistake follows the same pattern: making assumptions instead of measuring, applying the wrong tool for the bottleneck type, or introducing new problems while fixing old ones. Recognizing these patterns means you spend time on real problems, not imagined ones.

```
❌ Optimizing without profiling         → wastes time on non-bottlenecks
❌ Micro-optimizing trivial code        → saves nanoseconds, loses hours
❌ Ignoring algorithm complexity        → O(n²) will always beat O(n) optimization
❌ Blocking the async event loop        → turns async into sync
❌ Using list.pop(0) as a queue         → O(n) when deque.popleft() is O(1)
❌ Caching mutable objects              → cache returns stale/corrupted data
❌ Overusing lru_cache                  → memory leak if keys grow unboundedly
❌ Threading for CPU-bound work         → GIL prevents true parallelism
❌ Adding multiprocessing prematurely   → process spawn overhead > work saved
❌ Global variable lookups in hot loops → use local references
```

⚠️ **The worst mistake:** blocking the asyncio event loop with a synchronous operation (file read, CPU computation, `time.sleep()`). The entire server freezes for every user while the block runs. Always use `run_in_executor` for CPU/blocking work in async code.

📝 **Practice:** [Q74 · performance-bug](../python_practice_questions_100.md#q74--debug--performance-bug)

> [↑ Back to Top](#top)

---

<a id="-subfolder-deep-dives"></a>
## 📂 Subfolder Deep Dives

This theory file is an overview. Each subfolder contains a full deep-dive with real benchmarks, profiling walkthroughs, and production patterns:

| Subfolder | What's Inside |
|---|---|
| [01_profiling_tools/theory.md](./01_profiling_tools/theory.md) | **Profiling deep dive** — `cProfile` + `pstats` in depth, `line_profiler` step-by-step, `py-spy` (zero-overhead sampling profiler), `scalene`, flamegraph interpretation, profiling async code |
| [02_optimization_patterns/theory.md](./02_optimization_patterns/theory.md) | **Optimization patterns deep dive** — string concatenation patterns, attribute caching, slot classes, NumPy vectorization benchmarks, Cython basics, `dis` bytecode analysis, real before/after case studies |

---

<a id="-summary"></a>
## 🔥 Summary

**Engineering maturity in performance:**
```
Beginner      → Writes working code
Intermediate  → Uses built-ins and right data structures
Advanced      → Profiles before optimizing
Senior        → Balances CPU, memory, scalability, maintainability
Architect     → Optimizes system architecture, not just code
```

```
┌──────────── Performance Optimization Workflow ─────────────────────┐
│                                                                     │
│  1. MEASURE      timeit / cProfile / memory_profiler               │
│       ↓                                                             │
│  2. FIND         Sort by cumtime → identify the real bottleneck     │
│       ↓                                                             │
│  3. CLASSIFY     Algorithm? Data structure? I/O? Memory? CPU?      │
│       ↓                                                             │
│  4. OPTIMIZE     Apply the right tool for the bottleneck type       │
│       ↓                                                             │
│  5. VERIFY       Measure again — did it actually improve?           │
│       ↓                                                             │
│  6. REPEAT       Find the next bottleneck                           │
│                                                                     │
│  TOOLBOX:                                                           │
│  timeit         → micro-benchmark comparisons                      │
│  cProfile       → find slow functions                              │
│  line_profiler  → find slow lines inside functions                 │
│  tracemalloc    → find memory leaks                                │
│  memory_profiler→ line-by-line memory usage                        │
│  set/dict       → O(1) membership (replace O(n) list search)       │
│  lru_cache      → eliminate repeated computation                   │
│  generators     → reduce memory for large sequences                │
│  asyncio        → I/O concurrency                                  │
│  multiprocessing→ CPU parallelism                                  │
│  NumPy          → vectorized numeric operations                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

<a id="-navigation"></a>
## 🔁 Navigation

**This folder:**
[theory.md](./theory.md) · [cheetsheet.md](./cheetsheet.md) · [interview.md](./interview.md) · [practice.md](./practice.md)

**Subfolders:**
[01_profiling_tools/theory.md](./01_profiling_tools/theory.md) · [02_optimization_patterns/theory.md](./02_optimization_patterns/theory.md)

**Related modules:**
[17 — Testing (profiling in tests)](../17_testing/theory.md) · [13 — Concurrency (asyncio, GIL)](../13_concurrency/theory.md) · [11 — Generators (lazy evaluation)](../11_generators_iterators/theory.md) · [15 — Advanced Python (__slots__)](../15_advanced_python/theory.md)

**Jump to specific topics:**
[timeit](#1-timeit--measuring-performance) · [cProfile](#2-cprofile--function-level-profiling) · [Memory Profiling](#5-memory-profiling) · [Algorithm Optimization table](#6-algorithm-optimization) · [lru_cache](#avoid-repeated-computation--lru_cache) · [Real Production Scenarios](#14-real-production-scenarios)

---

| | |
|---|---|
| ⬅ Prev Module | [17 — Testing](../17_testing/theory.md) |
| ➡ Next Module | [19 — Production Best Practices](../19_production_best_practices/theory.md) |

**[🏠 Back to README](../../README.md)**
