# 💻 Practice — Performance Optimization (30 Questions)

> Master file covering the whole module. Deeper dives in subfolder practice files.

---

## Quick Index

| # | Concept | Difficulty |
|---|---------|-----------|
| Q1 | cProfile basics: run and read output | 🟢 Basic |
| Q2 | Read pstats output | 🟢 Basic |
| Q3 | Sort pstats output | 🟢 Basic |
| Q4 | cProfile programmatic (Profile object) | 🟡 Intermediate |
| Q5 | timeit repeat and min() | 🟡 Intermediate |
| Q6 | timeit setup parameter | 🟡 Intermediate |
| Q7 | timeit: compare two implementations | 🟡 Intermediate |
| Q8 | timeit: why min not mean | 🟡 Intermediate |
| Q9 | tracemalloc: memory snapshot | 🟡 Intermediate |
| Q10 | line_profiler: @profile decorator | 🟡 Intermediate |
| Q11 | memory_profiler: peak memory | 🟡 Intermediate |
| Q12 | tracemalloc: compare snapshots | 🟡 Intermediate |
| Q13 | Profile context manager | 🟠 Advanced |
| Q14 | Timing decorator | 🟡 Intermediate |
| Q15 | Dict vs list lookup: O(1) | 🟢 Basic |
| Q16 | Generator expressions: memory savings | 🟢 Basic |
| Q17 | Generator vs list: when to choose | 🟡 Intermediate |
| Q18 | Generator pipeline: O(1) memory | 🟡 Intermediate |
| Q19 | String building: join vs += | 🟡 Intermediate |
| Q20 | Local variable fast path | 🟡 Intermediate |
| Q21 | lru_cache: apply and inspect | 🟡 Intermediate |
| Q22 | `__slots__`: memory saving | 🟡 Intermediate |
| Q23 | `__slots__`: when to avoid | 🟡 Intermediate |
| Q24 | lru_cache: when to avoid | 🟡 Intermediate |
| Q25 | String building: io.StringIO | 🟡 Intermediate |
| Q26 | run_in_executor for blocking calls | 🟠 Advanced |
| Q27 | NumPy vectorization over loops | 🟡 Intermediate |
| Q28 | NumPy: when not worth it | 🟡 Intermediate |
| Q29 | Capstone: profile + fix O(n²) | 🟠 Advanced |
| Q30 | Capstone: full optimization workflow | 🟠 Advanced |

---

### Q1 · cProfile Basics 🟢

Write a function `slow_sum(n)` that does `sum(i*i for i in range(n))`. Profile it with `cProfile.run()` using `n=200_000`. What does the output tell you?

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Pass the call as a string to `cProfile.run()`. The sort defaults to standard call order — pass `sort="cumulative"` for the most useful ordering.
</details>

<details>
<summary>✅ Answer</summary>

```python
import cProfile

def slow_sum(n):
    return sum(i * i for i in range(n))

cProfile.run("slow_sum(200_000)", sort="cumulative")
```

**Why:** `cProfile.run()` is the simplest profiling entry point. The output shows every function called, how many times, and how long each took.
</details>

---

### Q2 · Read pstats Output 🟢

In a cProfile report, one row shows: `ncalls=5000, tottime=2.1, cumtime=8.4`. What does each number mean? Which column indicates this function is calling expensive helpers?

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`tottime` = own work. `cumtime` = own work + all callees.
</details>

<details>
<summary>✅ Answer</summary>

```python
# ncalls=5000:  the function was called 5,000 times
# tottime=2.1:  2.1s spent INSIDE this function (not counting subcalls)
# cumtime=8.4:  8.4s total including all functions it called

# The large gap (8.4 - 2.1 = 6.3s) is in subcalls → check what this
# function calls. Sort by cumtime to see the full call tree cost.
# Sort by tottime to find where CPU is actually burned.
```

**Why:** `cumtime >> tottime` means this function is mostly a wrapper — the real work is in the functions it calls. Drill down by examining those callee functions.
</details>

---

### Q3 · Sort pstats Output 🟢

Explain when you would sort by `tottime` versus `cumtime` when reading a pstats report. Give one example use case for each.

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Think about "where is the CPU burning" vs "what is the root cause of slowness".
</details>

<details>
<summary>✅ Answer</summary>

```python
# Sort by tottime:
# → Find functions doing actual CPU work
# → Use when you want to find the leaf function that is hot
# → Example: math-heavy inner loop

# Sort by cumtime:
# → Find the root of an expensive call tree
# → Use when you want to know which top-level function is responsible
# → Example: "api_handler() takes 5s — now I know to drill into it"

import pstats, io, cProfile

def target():
    return sum(x*x for x in range(100_000))

p = cProfile.Profile()
p.enable(); target(); p.disable()

buf = io.StringIO()
s = pstats.Stats(p, stream=buf)
s.sort_stats("tottime").print_stats(5)   # CPU hotspots
s.sort_stats("cumtime").print_stats(5)   # call tree roots
```

**Why:** Profiling reports are most useful when sorted for your specific question. `tottime` answers "what is working hardest?" and `cumtime` answers "what is costing the most overall?"
</details>

---

### Q4 · cProfile Programmatic (Profile Object) 🟡

Profile only a specific code section (not a full function call) using `cProfile.Profile()` with `.enable()` and `.disable()`. Capture output to a string.

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Create `profiler = cProfile.Profile()`. Call `.enable()` before your code section and `.disable()` after. Then use `pstats.Stats(profiler, stream=io.StringIO())`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import cProfile, pstats, io

profiler = cProfile.Profile()
profiler.enable()

# Only this section is profiled:
result = [x * x for x in range(500_000)]

profiler.disable()

buf = io.StringIO()
pstats.Stats(profiler, stream=buf).strip_dirs().sort_stats("tottime").print_stats(5)
print(buf.getvalue())
```

**Why:** `enable()`/`disable()` gives surgical control — you profile only the suspected hot section without profiling setup or teardown code that would add noise.
</details>

---

### Q5 · timeit repeat and min() 🟡

Use `timeit.repeat()` with `repeat=5, number=10_000` to benchmark `sorted(range(100))`. Take the minimum and convert to microseconds per call.

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`timeit.repeat()` returns a list of total times (one per repeat round). Divide `min(results)` by `number` for per-call time, then multiply by 1e6 for µs.
</details>

<details>
<summary>✅ Answer</summary>

```python
import timeit

results = timeit.repeat(
    "sorted(range(100))",
    repeat=5,
    number=10_000,
)
best = min(results)
print(f"Best total: {best:.4f}s")
print(f"Per call:   {best / 10_000 * 1e6:.2f} µs")
```

**Why:** `repeat=5` gives five independent measurements. Taking `min()` filters out OS interrupts and GC pauses, giving the most reliable per-call timing.
</details>

---

### Q6 · timeit setup Parameter 🟡

Benchmark `[x**2 for x in data]` where `data = list(range(1000))`. The `data` creation must go in `setup`, not `stmt`. Show the correct usage.

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`setup` runs once before the timing loop starts. `stmt` runs `number` times and is what gets timed.
</details>

<details>
<summary>✅ Answer</summary>

```python
import timeit

t = timeit.timeit(
    stmt="[x**2 for x in data]",
    setup="data = list(range(1000))",  # ← runs once, not timed
    number=10_000,
)
print(f"Per call: {t / 10_000 * 1e6:.2f} µs")
```

**Why:** If `data = list(range(1000))` were in `stmt`, every iteration would re-create the list. The benchmark would measure list creation, not the comprehension you care about.
</details>

---

### Q7 · timeit: Compare Two Implementations 🟡

Compare `42 in list(range(10_000))` vs `42 in set(range(10_000))`. Use `timeit.repeat` with the data created in `setup`, not inside `stmt`.

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Create both `data_list` and `data_set` in the same `setup` string. Then benchmark each stmt separately.
</details>

<details>
<summary>✅ Answer</summary>

```python
import timeit

setup = "data_list = list(range(10_000)); data_set = set(range(10_000))"

t_list = min(timeit.repeat("42 in data_list", setup=setup, repeat=5, number=1_000_000))
t_set  = min(timeit.repeat("42 in data_set",  setup=setup, repeat=5, number=1_000_000))

print(f"list: {t_list/1e6*1e6:.3f} µs/call")
print(f"set:  {t_set/1e6*1e6:.3f} µs/call")
print(f"set is {t_list/t_set:.0f}x faster")
```

**Why:** List membership is O(n) — it scans until it finds the value. Set membership is O(1) — it computes a hash and checks one bucket. For n=10,000, set wins by orders of magnitude.
</details>

---

### Q8 · timeit: Why min Not mean 🟡

You run `timeit.repeat` and get `[0.15, 0.16, 0.44, 0.15, 0.16]`. Calculate both min and mean. Explain why the 0.44 result should be excluded from your benchmark.

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

<details>
<summary>💡 Hint</summary>
What external events could cause one run to be 3x slower than the others?
</details>

<details>
<summary>✅ Answer</summary>

```python
results = [0.15, 0.16, 0.44, 0.15, 0.16]
print(f"min:  {min(results):.3f}s")              # 0.15 — use this
print(f"mean: {sum(results)/len(results):.3f}s")  # 0.212 — skewed by outlier

# The 0.44 run was caused by an OS scheduling interrupt, garbage
# collection pause, or another process stealing CPU time.
# These events are NOISE — they do not reflect the code's performance.
# min() = the best the CPU could do when uninterrupted = true speed.
```

**Why:** The minimum represents best-case CPU availability for your code. Higher results are caused by external interference — including them in your benchmark makes the code appear slower than it actually is.
</details>

---

### Q9 · tracemalloc: Memory Snapshot 🟡

Use `tracemalloc` to measure how much memory `[float(i) for i in range(100_000)]` allocates. Print the peak memory in MB.

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`tracemalloc.start()` → do work → `tracemalloc.get_traced_memory()` returns `(current, peak)` in bytes → `tracemalloc.stop()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import tracemalloc

tracemalloc.start()

data = [float(i) for i in range(100_000)]

current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"Current: {current / 1024 / 1024:.2f} MB")
print(f"Peak:    {peak / 1024 / 1024:.2f} MB")
```

**Why:** `tracemalloc.get_traced_memory()` gives a live current and peak reading. The peak shows the maximum memory in use at any single point during the tracked block.
</details>

---

### Q10 · line_profiler: @profile Decorator 🟡

Describe how to use `line_profiler` on a function `process(data)`. What command runs it, and what does the `% Time` column show?

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`kernprof -l -v script.py`. The `@profile` decorator is injected by kernprof at runtime.
</details>

<details>
<summary>✅ Answer</summary>

```python
# In script.py — kernprof injects @profile, no import needed:
@profile
def process(data):
    filtered = [x for x in data if x > 0]
    mapped = [x * x for x in filtered]
    return sum(mapped)

if __name__ == "__main__":
    process(list(range(-5000, 5000)))
```

```
kernprof -l -v script.py
```

Output columns:
- `Hits` — how many times this line executed
- `Time` — microseconds spent on this line total
- `% Time` — this line's share of the total function time

**Why:** `% Time` immediately shows which specific line is the bottleneck inside the function — something cProfile alone cannot tell you.
</details>

---

### Q11 · memory_profiler: Peak Memory 🟡

Decorate a function with `@profile` from `memory_profiler`. The function creates a 500k-element list. Show the decorator import and how to run it.

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Unlike line_profiler, with memory_profiler you DO import `from memory_profiler import profile`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from memory_profiler import profile   # ← import required for memory_profiler

@profile
def big_allocation():
    data = [float(i) for i in range(500_000)]
    return sum(data)

big_allocation()
```

```
python -m memory_profiler script.py
```

Output shows `Mem usage` (total RSS) and `Increment` (change from previous line) in MiB per line.

**Why:** The `Increment` column directly shows where memory grows. A large positive increment on a specific line tells you exactly which operation to optimize.
</details>

---

### Q12 · tracemalloc: Compare Snapshots 🟡

Use `tracemalloc` to compare two snapshots — before and after calling a function 10 times — to identify which line allocates the most memory. Print the top 3 growers.

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`snap2.compare_to(snap1, "lineno")` returns a list of `StatisticDiff` objects sorted by size difference.
</details>

<details>
<summary>✅ Answer</summary>

```python
import tracemalloc

def accumulate(n):
    return [i * 2 for i in range(n)]  # allocates each call

tracemalloc.start()
snap1 = tracemalloc.take_snapshot()

for _ in range(10):
    result = accumulate(10_000)

snap2 = tracemalloc.take_snapshot()
tracemalloc.stop()

top = snap2.compare_to(snap1, "lineno")
for stat in top[:3]:
    print(stat)
```

**Why:** `compare_to()` shows the memory delta between snapshots, pinpointing which lines allocated memory that was not freed — the exact signature of a memory leak or unexpectedly large allocation.
</details>

---

### Q13 · Profile Context Manager 🟠

Write a reusable `profile_block(label)` context manager using `@contextmanager` that profiles any `with` block and prints the top 5 by `tottime`.

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Use `cProfile.Profile()` with `enable()` in `try` and `disable()` in `finally`. See the pattern in `01_profiling_tools/practice.md Q9`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import cProfile, pstats, io
from contextlib import contextmanager

@contextmanager
def profile_block(label, top_n=5, sort_by="tottime"):
    p = cProfile.Profile()
    p.enable()
    try:
        yield
    finally:
        p.disable()
        buf = io.StringIO()
        pstats.Stats(p, stream=buf).strip_dirs().sort_stats(sort_by).print_stats(top_n)
        print(f"--- Profile: {label} ---")
        print(buf.getvalue())

with profile_block("list building"):
    data = [i * i for i in range(100_000)]
```

**Why:** A context manager makes profiling any code block a one-line change — `with profile_block("label"):` — without restructuring code into separate functions.
</details>

---

### Q14 · Timing Decorator 🟡

Write a decorator `@timed` that prints elapsed milliseconds every time the decorated function is called. Use `time.perf_counter`.

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Store `t0 = time.perf_counter()` before calling the function, then compute `(time.perf_counter() - t0) * 1000` after.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time, functools

def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - t0) * 1000
        print(f"{func.__name__}: {elapsed:.2f} ms")
        return result
    return wrapper

@timed
def process(n):
    return sum(i * i for i in range(n))

process(500_000)
```

**Why:** `time.perf_counter()` is the highest-resolution monotonic clock available on all platforms. It is ideal for wall-clock timing of function calls.
</details>

---

### Q15 · Dict vs List Lookup: O(1) 🟢

You have 10,000 product records. You repeatedly look up products by their SKU. Show the slow (list scan) vs fast (dict lookup) approach and explain the complexity difference.

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Build a dict keyed by SKU once. Then `products_by_sku[sku]` is O(1) for every lookup.
</details>

<details>
<summary>✅ Answer</summary>

```python
products = [{"sku": f"SKU-{i}", "price": i * 1.5} for i in range(10_000)]

# O(n) per lookup: scans up to 10k records
def find_slow(products, sku):
    for p in products:
        if p["sku"] == sku:
            return p

# Build index once: O(n). Then each lookup is O(1)
sku_index = {p["sku"]: p for p in products}

def find_fast(sku):
    return sku_index.get(sku)

print(find_fast("SKU-9999"))
```

**Why:** Dictionary lookup is O(1) because Python hashes the key and goes directly to the right bucket. List scan is O(n) because it must check each element in sequence.
</details>

---

### Q16 · Generator Expressions: Memory Savings 🟢

Show the memory size difference between `[x*x for x in range(1_000_000)]` and `(x*x for x in range(1_000_000))` using `sys.getsizeof`.

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`sys.getsizeof()` on a list returns the memory used by the list object and its pointers. On a generator it returns just the generator object size (~200 bytes).
</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

lst = [x * x for x in range(1_000_000)]  # eagerly computes all values
gen = (x * x for x in range(1_000_000))  # lazy: nothing computed yet

print(f"List size:      {sys.getsizeof(lst) / 1024 / 1024:.1f} MB")
print(f"Generator size: {sys.getsizeof(gen)} bytes")
```

**Why:** A generator object stores only its state (current position, local variables) — roughly 200 bytes regardless of how many values it can produce. The list stores every computed value in memory simultaneously.
</details>

---

### Q17 · Generator vs List: When to Choose 🟡

List three situations where you should use a generator instead of a list, and one situation where a list is better.

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Think about: do you need random access? Do you need to iterate more than once? Is the dataset huge?
</details>

<details>
<summary>✅ Answer</summary>

```python
# Use generator when:
# 1. You only iterate ONCE (no need to store all results)
# 2. The sequence is very large (millions of items — list would exhaust RAM)
# 3. You are chaining operations (filter → map → reduce in one pass)

# Example of all three:
total = sum(x * x for x in range(10_000_000) if x % 3 == 0)  # O(1) memory

# Use a LIST when:
# 1. You need random access: data[42]
# 2. You need len() before iterating
# 3. You need to iterate more than once (generator is exhausted after one pass)
# 4. You need to sort, reverse, or index

data = list(range(100))
print(data[42])           # must be a list
print(len(data))          # must be a list
data.sort()               # must be a list
```

**Why:** Generators are not a universal replacement for lists. The key question is: "do I need to access any element more than once, or by index?" If yes — use a list.
</details>

---

### Q18 · Generator Pipeline: O(1) Memory 🟡

Rewrite this eager pipeline to use generator expressions throughout, keeping O(1) peak memory:

```python
data = [x for x in range(500_000)]
evens = [x for x in data if x % 2 == 0]
squares = [x * x for x in evens]
total = sum(squares)
```

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Change every `[...]` to `(...)`. Chain them — each generator pulls from the previous one.
</details>

<details>
<summary>✅ Answer</summary>

```python
# O(n) memory — three full lists stored simultaneously
data    = [x for x in range(500_000)]
evens   = [x for x in data if x % 2 == 0]
squares = [x * x for x in evens]
total   = sum(squares)

# O(1) memory — at most one value exists at a time
data    = (x for x in range(500_000))
evens   = (x for x in data if x % 2 == 0)
squares = (x * x for x in evens)
total   = sum(squares)

# Even more concise:
total = sum(x * x for x in range(500_000) if x % 2 == 0)
```

**Why:** Each generator is lazy — `sum()` pulls one value from `squares`, which pulls one from `evens`, which pulls one from `data`. No intermediate list is ever fully materialized.
</details>

---

### Q19 · String Building: join vs += 🟡

Why does `result += chunk` inside a loop have O(n²) behavior? Rewrite a CSV row builder to use `join()` instead.

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Python strings are immutable. Every `+=` creates a new string and copies all previous content into it.
</details>

<details>
<summary>✅ Answer</summary>

```python
# O(n²): each += copies the entire accumulated string
def build_csv_slow(values):
    result = ""
    for v in values:
        result += str(v) + ","
    return result.rstrip(",")

# O(n): collect all parts, one allocation at the end
def build_csv_fast(values):
    return ",".join(str(v) for v in values)

# Both produce same output
row = list(range(1000))
assert build_csv_slow(row) == build_csv_fast(row)
```

**Why:** Strings are immutable in Python. `s += chunk` does not modify `s` in place — it creates a brand-new string object that is `len(s) + len(chunk)` bytes long and copies everything. After n iterations, you have copied roughly n²/2 characters total.
</details>

---

### Q20 · Local Variable Fast Path 🟡

Explain why `LOAD_FAST` is faster than `LOAD_GLOBAL`, and write a function that demonstrates the optimization by pulling `math.sqrt` into a local variable before a hot loop.

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Use `dis.dis()` to see the bytecode difference. `LOAD_FAST` uses an array index; `LOAD_GLOBAL` does a dict hash lookup.
</details>

<details>
<summary>✅ Answer</summary>

```python
import math, dis

def slow_version(pts):
    return [math.sqrt(x * x + y * y) for x, y in pts]

def fast_version(pts):
    sqrt = math.sqrt      # ← LOAD_FAST from here on
    return [sqrt(x * x + y * y) for x, y in pts]

# LOAD_FAST = array index (1-2 ns)
# LOAD_GLOBAL + LOAD_ATTR = dict lookup + attribute lookup (~5-10 ns)
# In a 1M-iteration loop this adds up to milliseconds

# See bytecode difference:
print("=== slow ==="); dis.dis(slow_version)
print("=== fast ==="); dis.dis(fast_version)
```

**Why:** Local variables are stored in a fixed-size array indexed by position. Global lookup requires a hash table lookup in the module's `__dict__`, plus an attribute lookup on the module object — roughly 3-5x more work per access.
</details>

---

### Q21 · lru_cache: Apply and Inspect 🟡

Apply `@lru_cache(maxsize=256)` to a function `fib(n)`. After calling `fib(30)`, print the cache info. Then clear the cache and verify it is empty.

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`fib.cache_info()` returns `CacheInfo(hits, misses, maxsize, currsize)`. `fib.cache_clear()` evicts all entries.
</details>

<details>
<summary>✅ Answer</summary>

```python
from functools import lru_cache

@lru_cache(maxsize=256)
def fib(n):
    if n < 2: return n
    return fib(n - 1) + fib(n - 2)

fib(30)
info = fib.cache_info()
print(f"hits={info.hits}, misses={info.misses}, "
      f"maxsize={info.maxsize}, currsize={info.currsize}")

fib.cache_clear()
info_after = fib.cache_info()
print(f"After clear: currsize={info_after.currsize}")  # 0
```

**Why:** `cache_info()` helps you verify the cache is actually being hit (hits >> misses = working well). `cache_clear()` is essential in tests to avoid state leaking between test runs.
</details>

---

### Q22 · `__slots__`: Memory Saving 🟡

Create a `Sensor` class with three float attributes. Make two versions — with and without `__slots__`. Create 100,000 instances of each and compare memory using `sys.getsizeof` on a single instance.

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`sys.getsizeof(instance)` shows the object's immediate memory. For the version without slots, add `sys.getsizeof(instance.__dict__)` to get the true total.
</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

class SensorNormal:
    def __init__(self, x, y, z):
        self.x = x; self.y = y; self.z = z

class SensorSlots:
    __slots__ = ("x", "y", "z")
    def __init__(self, x, y, z):
        self.x = x; self.y = y; self.z = z

n = SensorNormal(1.0, 2.0, 3.0)
s = SensorSlots(1.0, 2.0, 3.0)

# Object + __dict__ overhead for normal
print(f"Normal: {sys.getsizeof(n) + sys.getsizeof(n.__dict__)} bytes")
print(f"Slots:  {sys.getsizeof(s)} bytes")
print(f"No __dict__ on slots: {not hasattr(s, '__dict__')}")
```

**Why:** A normal instance has a `__dict__` that itself consumes ~200–300 bytes regardless of how many attributes are stored. `__slots__` eliminates the `__dict__` entirely, replacing it with fixed C-level slots.
</details>

---

### Q23 · `__slots__`: When to Avoid 🟡

Name three situations where adding `__slots__` would cause problems or offer no benefit.

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Think about: dynamic attributes, pickling, inheritance, small object counts.
</details>

<details>
<summary>✅ Answer</summary>

```python
# 1. Dynamic attribute assignment — slots block it entirely:
class Rigid:
    __slots__ = ("x", "y")
    def __init__(self, x, y): self.x = x; self.y = y

r = Rigid(1, 2)
# r.z = 3   # AttributeError — cannot set z

# 2. Inheritance — subclass gets __dict__ back unless it also declares __slots__:
class RigidChild(Rigid):
    pass  # no __slots__ → __dict__ returns, wasting the effort

# 3. Only a few instances — __slots__ saves ~200 bytes per instance.
#    For 100 instances, that is 20 KB. Not worth the code complexity.

# 4. Pickle/copy issues — slots require careful __getstate__/__setstate__
#    if you need to serialize the object.
```

**Why:** `__slots__` is a surgical optimization for high-count objects. Applied carelessly to classes with inheritance or dynamic use, it breaks functionality without providing meaningful benefit.
</details>

---

### Q24 · lru_cache: When to Avoid 🟡

Name three cases where `@lru_cache` would cause bugs or be inappropriate.

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Think about: unhashable arguments, side effects, functions that depend on external state that changes.
</details>

<details>
<summary>✅ Answer</summary>

```python
from functools import lru_cache

# 1. Unhashable arguments — lists and dicts cannot be cache keys:
# @lru_cache  # TypeError: unhashable type: 'list'
# def process(items: list): ...

# 2. Functions with side effects — cached result means side effect
#    only happens on the FIRST call for each unique input:
# @lru_cache
# def send_email(to, subject): ...  # would only send once per (to, subject)!

# 3. Functions that read from external state that changes:
import time
# @lru_cache
# def get_price(symbol): return fetch_from_db(symbol)
# → cache returns stale price even after DB update

# 4. Memory-constrained environments with large/diverse inputs —
#    unbounded cache grows without limit:
@lru_cache(maxsize=128)  # bounded is safer than maxsize=None in production
def compute(n: int): return n * n
```

**Why:** `lru_cache` assumes the function is **pure** (same inputs → same output, no side effects). Applying it to impure functions causes stale results or missed side effects that are extremely difficult to debug.
</details>

---

### Q25 · String Building: io.StringIO 🟡

Show how `io.StringIO` can be used as an alternative to `+=` for building large strings. Compare it to `join()`.

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`io.StringIO` acts like a mutable string buffer. Use `.write()` to append, `.getvalue()` to get the final string.
</details>

<details>
<summary>✅ Answer</summary>

```python
import io, timeit

N = 1000

def build_concat(n):
    result = ""
    for i in range(n):
        result += str(i) + ","
    return result

def build_join(n):
    return ",".join(str(i) for i in range(n))

def build_stringio(n):
    buf = io.StringIO()
    for i in range(n):
        buf.write(str(i))
        buf.write(",")
    return buf.getvalue()

# All three produce the same output
assert build_concat(N) == build_join(N) == build_stringio(N)

# join() is typically fastest. StringIO is useful when you need
# to conditionally write different content (if/else inside the loop)
# and cannot easily use a list comprehension.
```

**Why:** `io.StringIO` is a mutable buffer that appends without copying — O(n) like `join()`. It is most useful when your string assembly logic is complex enough that a list-of-parts approach is awkward.
</details>

---

### Q26 · run_in_executor for Blocking Calls 🟠

In an `async` function, you have a blocking `time.sleep(1)` call that would freeze the event loop. Show how to wrap it with `run_in_executor` to prevent blocking.

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`loop.run_in_executor(None, func, *args)` runs a blocking function in a thread pool without blocking the event loop. `asyncio.get_event_loop()` or use `asyncio.get_running_loop()` inside an async function.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio, time

def blocking_work(duration):
    time.sleep(duration)          # blocks its thread, not the event loop
    return f"done after {duration}s"

async def main():
    loop = asyncio.get_running_loop()

    # Run blocking_work in a thread pool — does not block event loop
    result = await loop.run_in_executor(None, blocking_work, 0.5)
    print(result)

asyncio.run(main())
```

**Why:** `time.sleep()` and other blocking calls inside `async` functions freeze the entire event loop, preventing all other coroutines from running. `run_in_executor` offloads the blocking call to a thread, keeping the event loop responsive.
</details>

---

### Q27 · NumPy Vectorization 🟡

Rewrite a Python loop that computes `sqrt(x^2 + y^2)` for 1 million (x, y) pairs using NumPy. Compare speed with `timeit`.

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Use `np.sqrt(xs**2 + ys**2)` where `xs` and `ys` are NumPy arrays. Element-wise operations on arrays are vectorized C code.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np, timeit, random

N = 1_000_000
xs_list = [random.random() for _ in range(N)]
ys_list = [random.random() for _ in range(N)]
xs_arr = np.array(xs_list)
ys_arr = np.array(ys_list)

def python_loop():
    import math
    sqrt = math.sqrt
    return [sqrt(x*x + y*y) for x, y in zip(xs_list, ys_list)]

def numpy_vec():
    return np.sqrt(xs_arr**2 + ys_arr**2)

t_py = min(timeit.repeat(python_loop, repeat=3, number=3))
t_np = min(timeit.repeat(numpy_vec,  repeat=3, number=3))
print(f"Python: {t_py/3*1000:.1f} ms  NumPy: {t_np/3*1000:.1f} ms  "
      f"Speedup: {t_py/t_np:.0f}x")
```

**Why:** NumPy's element-wise operations dispatch a single C function call that processes all million elements in a tight loop over contiguous memory — no Python bytecode overhead per element. Typical speedup: 50–150x.
</details>

---

### Q28 · NumPy: When Not Worth It 🟡

For what input sizes and use cases is NumPy NOT faster than plain Python? Give a concrete example.

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)

<details>
<summary>💡 Hint</summary>
NumPy has fixed overhead per operation (array creation, dispatch). For tiny arrays this overhead dominates.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np, timeit

# For tiny arrays, NumPy overhead > savings
def python_tiny():
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    return sum(x * x for x in data)

def numpy_tiny():
    arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    return float(np.sum(arr * arr))

t_py = min(timeit.repeat(python_tiny, repeat=5, number=100_000))
t_np = min(timeit.repeat(numpy_tiny,  repeat=5, number=100_000))
print(f"Python (n=5): {t_py/100_000*1e6:.2f} µs")
print(f"NumPy  (n=5): {t_np/100_000*1e6:.2f} µs")
# NumPy is often SLOWER here due to array allocation overhead

# NumPy is not worth it when:
# - Array has fewer than ~1000 elements
# - Data is non-numeric (strings, mixed types)
# - You only access the data once and spend more time creating the array
```

**Why:** `np.array()` creation has fixed overhead (~1-5 µs). For 5 elements, this overhead is larger than the computation savings. The crossover point is typically around 1,000–10,000 elements.
</details>

---

### Q29 · Capstone: Profile and Fix O(n²) 🟠

Profile the function below, identify the algorithmic problem from the pstats output, and fix it:

```python
def count_pairs(nums, target):
    count = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                count += 1
    return count

nums = list(range(5000))
result = count_pairs(nums, 7500)
```

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Profile first — look at `tottime` for `count_pairs`. The nested loop is O(n²). Can you solve it in one pass with a dict (complement lookup)?
</details>

<details>
<summary>✅ Answer</summary>

```python
import cProfile, timeit

nums = list(range(5000))
target = 7500

def count_pairs_slow(nums, target):
    count = 0
    for i in range(len(nums)):         # O(n)
        for j in range(i + 1, len(nums)):  # O(n) inner
            if nums[i] + nums[j] == target:
                count += 1
    return count                       # total: O(n²)

def count_pairs_fast(nums, target):
    seen = {}
    count = 0
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:         # O(1) dict lookup
            count += seen[complement]
        seen[num] = seen.get(num, 0) + 1
    return count                       # total: O(n)

assert count_pairs_slow(nums, target) == count_pairs_fast(nums, target)

cProfile.run("count_pairs_slow(nums, target)", sort="tottime")

t_slow = min(timeit.repeat(lambda: count_pairs_slow(nums, target), repeat=3, number=5))
t_fast = min(timeit.repeat(lambda: count_pairs_fast(nums, target), repeat=3, number=100))
print(f"Speedup: {(t_slow/5) / (t_fast/100):.0f}x")
```

**Why:** The profiler shows `count_pairs` consuming nearly all tottime — the nested loop is the problem. Dict-based complement lookup reduces O(n²) to O(n). For n=5000, this is a ~5000x speedup.
</details>

---

### Q30 · Capstone: Full Optimization Workflow 🟠

You are given a slow data processing function. Apply the complete workflow: profile → identify top two hotspots → fix both → verify speedup:

```python
def process(records):
    names = ""
    for r in records:
        if r["active"] == True:
            names += r["name"] + ","
    active = [r for r in records if r["active"] == True]
    scores = {r["name"]: r["score"] for r in active if r["name"] in names}
    return names, scores

import random, string
records = [
    {"name": "".join(random.choices(string.ascii_lowercase, k=6)),
     "score": random.randint(0, 100),
     "active": random.choice([True, False])}
    for _ in range(10_000)
]
```

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Run cProfile first. Hotspot 1: `names += ...` is O(n²) string concat. Hotspot 2: `r["name"] in names` is O(len(names)) substring search — should be set membership.
</details>

<details>
<summary>✅ Answer</summary>

```python
import cProfile, timeit, random, string

records = [
    {"name": "".join(random.choices(string.ascii_lowercase, k=6)),
     "score": random.randint(0, 100),
     "active": random.choice([True, False])}
    for _ in range(10_000)
]

def process_slow(records):
    names = ""
    for r in records:
        if r["active"] == True:
            names += r["name"] + ","           # O(n²) string build
    active = [r for r in records if r["active"]]
    scores = {r["name"]: r["score"]
              for r in active if r["name"] in names}  # O(len(names)) membership
    return names, scores

# Fix 1: collect names in a list, join once
# Fix 2: use a set for O(1) membership check
def process_fast(records):
    active = [r for r in records if r["active"]]
    name_list = [r["name"] for r in active]
    names = ",".join(name_list)
    name_set = set(name_list)                   # O(1) membership
    scores = {r["name"]: r["score"] for r in active if r["name"] in name_set}
    return names, scores

cProfile.run("process_slow(records)", sort="tottime")

t_slow = min(timeit.repeat(lambda: process_slow(records), repeat=3, number=20))
t_fast = min(timeit.repeat(lambda: process_fast(records), repeat=3, number=20))
print(f"Speedup: {t_slow/t_fast:.1f}x")
```

**Why:** The profiler reveals two independent O(n²) patterns. Fixing both with join() and a set drops the function from O(n²) to O(n), giving a large combined speedup on real input.
</details>

---

## 📂 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🔍 Profiling Tools | [01_profiling_tools/practice.md](./01_profiling_tools/practice.md) |
| ⚡ Optimization Patterns | [02_optimization_patterns/practice.md](./02_optimization_patterns/practice.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🔥 Interview | [interview.md](./interview.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Profiling Tools Practice](./01_profiling_tools/practice.md) · [Optimization Patterns Practice](./02_optimization_patterns/practice.md)
