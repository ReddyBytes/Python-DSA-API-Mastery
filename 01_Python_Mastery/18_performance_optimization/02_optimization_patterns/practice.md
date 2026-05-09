# 💻 Practice — Optimization Patterns (12 Questions)

> Covers: dict vs list O(1), generators, local variables, `__slots__`, `lru_cache`, string building, NumPy vectorization

---

## Quick Index

| # | Concept | Difficulty |
|---|---------|-----------|
| [Q1](#q1) | Convert list search to dict lookup (O(n) → O(1)) | 🟢 Basic |
| [Q2](#q2) | Rewrite list comprehension as generator expression | 🟢 Basic |
| [Q3](#q3) | Local variable optimization in hot loop | 🟡 Intermediate |
| [Q4](#q4) | Add `__slots__` to a class | 🟡 Intermediate |
| [Q5](#q5) | Apply `lru_cache` to recursive fibonacci | 🟡 Intermediate |
| [Q6](#q6) | Fix string concatenation in loop → use join() | 🟡 Intermediate |
| [Q7](#q7) | Explain why generator beats list for large pipeline | 🟡 Intermediate |
| [Q8](#q8) | Replace Python for-loop sum with NumPy vectorized op | 🟡 Intermediate |
| [Q9](#q9) | Design a cache with TTL using lru_cache + wrapper | 🟠 Advanced |
| [Q10](#q10) | Identify bottleneck in provided code and fix it | 🟠 Advanced |
| [Q11](#q11) | Rewrite class with `__slots__` and compare memory | 🟠 Advanced |
| [Q12](#q12) | Capstone: profile slow function, fix top hotspot | 🟠 Advanced |

---

<a id="q1"></a>

### Q1 · Convert List Search to Dict Lookup 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


You have a list of user records: `users = [{"id": 1, "name": "Alice"}, ...]`. You look up users by id in a hot loop. Rewrite the lookup to use O(1) instead of O(n).


<details>
<summary>💡 Hint</summary>
Build a dict keyed by `id` before the loop. Then `users_by_id[target_id]` is O(1).
</details>

<details>
<summary>✅ Answer</summary>

```python
users = [{"id": i, "name": f"User{i}"} for i in range(10_000)]

# Before: O(n) scan on every lookup
def find_user_slow(users, target_id):
    for u in users:           # scans up to 10,000 records
        if u["id"] == target_id:
            return u
    return None

# After: O(1) dict lookup
users_by_id = {u["id"]: u for u in users}  # build once

def find_user_fast(target_id):
    return users_by_id.get(target_id)      # one hash lookup
```

**Why:** A list scan is O(n) per lookup. A dict keyed by the search field turns every lookup into O(1) — regardless of how many records exist.
</details>

---

<a id="q2"></a>

### Q2 · Rewrite List Comprehension as Generator Expression 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


You have `squared = [x*x for x in range(1_000_000)]` and then do `total = sum(squared)`. Rewrite this so the full list is never held in memory.


<details>
<summary>💡 Hint</summary>
Change `[...]` to `(...)` inside the `sum()` call.
</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

# Before: builds full list in memory (~8 MB for 1M ints)
squared_list = [x * x for x in range(1_000_000)]
total_list = sum(squared_list)

# After: generator expression — O(1) memory
total_gen = sum(x * x for x in range(1_000_000))

# Memory comparison
gen = (x * x for x in range(1_000_000))
print(sys.getsizeof(squared_list))  # ~8 MB
print(sys.getsizeof(gen))           # ~200 bytes
```

**Why:** `sum()` only needs one value at a time. The generator expression produces each value on demand without ever storing the full million-element list.
</details>

---

<a id="q3"></a>

### Q3 · Local Variable Optimization in Hot Loop 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


Rewrite this function to avoid the repeated global attribute lookup of `math.sqrt` inside the loop:

```python
import math
def compute(points):
    return [math.sqrt(x*x + y*y) for x, y in points]
```


<details>
<summary>💡 Hint</summary>
Assign `sqrt = math.sqrt` before the comprehension. Python will use `LOAD_FAST` instead of `LOAD_GLOBAL` + attribute lookup.
</details>

<details>
<summary>✅ Answer</summary>

```python
import math, timeit

def compute_slow(points):
    return [math.sqrt(x*x + y*y) for x, y in points]

def compute_fast(points):
    sqrt = math.sqrt  # ← one global lookup at function entry
    return [sqrt(x*x + y*y) for x, y in points]

pts = [(i*0.1, i*0.2) for i in range(50_000)]
t_slow = min(timeit.repeat(lambda: compute_slow(pts), repeat=3, number=10))
t_fast = min(timeit.repeat(lambda: compute_fast(pts), repeat=3, number=10))
print(f"Speedup: {t_slow/t_fast:.2f}x")
```

**Why:** Inside a loop, `math.sqrt` triggers two lookups each iteration: `math` (global dict) + `.sqrt` (attribute). Binding to a local variable replaces both with a single `LOAD_FAST` array index.
</details>

---

<a id="q4"></a>

### Q4 · Add `__slots__` to a Class 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


Rewrite this class to use `__slots__`. Confirm that `__dict__` is no longer present on instances.

```python
class Particle:
    def __init__(self, x, y, mass):
        self.x = x
        self.y = y
        self.mass = mass
```


<details>
<summary>💡 Hint</summary>
Add `__slots__ = ("x", "y", "mass")` as a class-level attribute. Then check `hasattr(p, "__dict__")`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Particle:
    __slots__ = ("x", "y", "mass")   # ← fixed attribute declarations

    def __init__(self, x, y, mass):
        self.x = x
        self.y = y
        self.mass = mass

p = Particle(1.0, 2.0, 9.1e-31)
print(hasattr(p, "__dict__"))   # False — __dict__ eliminated
print(p.x, p.y, p.mass)         # attributes still work normally
```

**Why:** `__slots__` replaces the per-instance `__dict__` (a hash map) with fixed C-level memory slots. For a million `Particle` objects, this typically saves 40–60% memory.
</details>

---

<a id="q5"></a>

### Q5 · Apply lru_cache to Recursive Fibonacci 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


The naive recursive `fibonacci(n)` recomputes the same subproblems exponentially. Add one decorator to make it O(n). Then use `cache_info()` to show how many cache hits occurred.


<details>
<summary>💡 Hint</summary>
`from functools import lru_cache`. Then check `fibonacci.cache_info()` after calling it.
</details>

<details>
<summary>✅ Answer</summary>

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

result = fibonacci(35)
info = fibonacci.cache_info()
print(f"fibonacci(35) = {result}")
print(f"Cache hits: {info.hits}, misses: {info.misses}")
# hits >> misses: most subproblems were served from cache
```

**Why:** Without caching, `fibonacci(35)` makes ~29 million function calls. With `lru_cache`, it makes exactly 36 unique calls and serves the rest from memory — O(n) total.
</details>

---

<a id="q6"></a>

### Q6 · Fix String Concatenation in Loop 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


This function has an O(n²) string building bug. Rewrite it to be O(n):

```python
def make_csv(rows):
    result = ""
    for row in rows:
        result += ",".join(str(x) for x in row) + "\n"
    return result
```


<details>
<summary>💡 Hint</summary>
Collect all lines into a list, then `"\n".join(lines)` at the end.
</details>

<details>
<summary>✅ Answer</summary>

```python
def make_csv_slow(rows):
    result = ""
    for row in rows:
        result += ",".join(str(x) for x in row) + "\n"  # O(n²)
    return result

def make_csv_fast(rows):
    lines = [",".join(str(x) for x in row) for row in rows]
    return "\n".join(lines) + "\n"   # one allocation at the end

# Both produce the same output
rows = [[i, i*2, i*3] for i in range(1000)]
assert make_csv_slow(rows) == make_csv_fast(rows)
```

**Why:** Every `+=` on a string copies the entire accumulated string. Collecting parts in a list and calling `join()` once makes a single allocation proportional to the total output size.
</details>

---

<a id="q7"></a>

### Q7 · Explain Why Generator Beats List for Large Pipelines 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


A data pipeline applies three steps to one million records: filter even numbers → square them → sum. Explain why chaining generator expressions uses O(1) memory while chaining list comprehensions uses O(n) memory. No code needed — write the explanation.


<details>
<summary>💡 Hint</summary>
Think about what is stored between each step when using lists vs generators.
</details>

<details>
<summary>✅ Answer</summary>

```python
# List pipeline: three full arrays in memory simultaneously
data     = [x for x in range(1_000_000)]         # ~8 MB
evens    = [x for x in data if x % 2 == 0]       # ~4 MB
squares  = [x * x for x in evens]                # ~4 MB
total    = sum(squares)                           # peak: ~16 MB

# Generator pipeline: at most ONE value in memory at a time
data     = (x for x in range(1_000_000))
evens    = (x for x in data if x % 2 == 0)
squares  = (x * x for x in evens)
total    = sum(squares)                           # peak: O(1) bytes

# Each generator pulls one value from the previous when asked.
# No intermediate results are stored.
```

**Why:** Generators are lazy. `sum()` pulls one value from `squares`, which pulls one from `evens`, which pulls one from `data`. Each value is processed and discarded before the next is requested — zero intermediate storage.
</details>

---

<a id="q8"></a>

### Q8 · Replace Python for-loop with NumPy Vectorized Operation 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


Rewrite this function using NumPy so the loop runs in C rather than Python:

```python
def sum_of_squares(n):
    total = 0.0
    for i in range(n):
        total += i * i
    return total
```


<details>
<summary>💡 Hint</summary>
`np.arange(n)` creates an array. `np.sum(arr * arr)` is vectorized element-wise multiply then reduce.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np, timeit

def sum_of_squares_python(n):
    total = 0.0
    for i in range(n):
        total += i * i
    return total

def sum_of_squares_numpy(n):
    arr = np.arange(n, dtype=np.float64)
    return float(np.sum(arr * arr))

N = 1_000_000
t_py  = min(timeit.repeat(lambda: sum_of_squares_python(N), repeat=3, number=5))
t_np  = min(timeit.repeat(lambda: sum_of_squares_numpy(N),  repeat=3, number=5))
print(f"Python: {t_py/5*1000:.1f} ms  NumPy: {t_np/5*1000:.1f} ms  "
      f"Speedup: {t_py/t_np:.0f}x")
```

**Why:** NumPy's `arr * arr` dispatches a single C function call that processes all million elements in contiguous memory with no Python bytecode overhead per element. Typical speedup is 50–200x.
</details>

---

<a id="q9"></a>

### Q9 · Design a Cache with TTL Using lru_cache + Wrapper 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


`lru_cache` has no built-in TTL (time-to-live). Write a decorator `ttl_cache(seconds)` that wraps a function with caching that expires entries after the given number of seconds.


<details>
<summary>💡 Hint</summary>
Wrap the function so the cache key includes `time.time() // ttl_seconds` — this makes the key change (and the cache miss) each time a new TTL window starts.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time, functools

def ttl_cache(seconds):
    def decorator(func):
        @functools.lru_cache(maxsize=None)
        def cached(ttl_slot, *args, **kwargs):  # ttl_slot is the time window
            return func(*args, **kwargs)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ttl_slot = int(time.time() // seconds)  # changes every `seconds`
            return cached(ttl_slot, *args, **kwargs)

        wrapper.cache_clear = cached.cache_clear
        wrapper.cache_info  = cached.cache_info
        return wrapper
    return decorator

@ttl_cache(seconds=5)
def get_price(symbol):
    print(f"  Fetching {symbol}...")   # only runs on cache miss
    return {"AAPL": 189.50}.get(symbol, 0.0)

print(get_price("AAPL"))  # fetches
print(get_price("AAPL"))  # cached
```

**Why:** By including the time window as part of the cache key, entries automatically become stale when the window advances — no need to manually invalidate the cache.
</details>

---

<a id="q10"></a>

### Q10 · Identify Bottleneck and Fix It 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


Profile this code, identify the top hotspot, and fix it:

```python
def find_common(list1, list2):
    return [x for x in list1 if x in list2]

list1 = list(range(10_000))
list2 = list(range(5_000, 15_000))
result = find_common(list1, list2)
```


<details>
<summary>💡 Hint</summary>
Profile with `cProfile`. The bottleneck is `x in list2` — it is O(n) per element. What data structure makes membership O(1)?
</details>

<details>
<summary>✅ Answer</summary>

```python
import cProfile, timeit

def find_common_slow(list1, list2):
    return [x for x in list1 if x in list2]  # x in list = O(n) × O(n) = O(n²)

def find_common_fast(list1, list2):
    set2 = set(list2)                          # O(n) once
    return [x for x in list1 if x in set2]    # O(1) per check = O(n) total

list1 = list(range(10_000))
list2 = list(range(5_000, 15_000))

# Profile to confirm
cProfile.run("find_common_slow(list1, list2)", sort="tottime")

t_slow = min(timeit.repeat(lambda: find_common_slow(list1, list2), repeat=3, number=50))
t_fast = min(timeit.repeat(lambda: find_common_fast(list1, list2), repeat=3, number=50))
print(f"Speedup: {t_slow/t_fast:.0f}x")
```

**Why:** Converting `list2` to a `set` before the loop changes the membership test from O(n) to O(1). Total complexity drops from O(n²) to O(n).
</details>

---

<a id="q11"></a>

### Q11 · Rewrite Class with `__slots__` and Compare Memory 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


Create two versions of a `Vector3D` class (with and without `__slots__`). Create 500,000 instances of each, measure memory usage with `tracemalloc`, and report the difference.


<details>
<summary>💡 Hint</summary>
Use `tracemalloc.start()`, create all instances, call `tracemalloc.get_traced_memory()` for peak usage, then `tracemalloc.stop()`. Do this twice — once per class.
</details>

<details>
<summary>✅ Answer</summary>

```python
import tracemalloc, gc

class Vector3D:
    def __init__(self, x, y, z):
        self.x = x; self.y = y; self.z = z

class Vector3DSlots:
    __slots__ = ("x", "y", "z")
    def __init__(self, x, y, z):
        self.x = x; self.y = y; self.z = z

N = 500_000

gc.collect()
tracemalloc.start()
objs_normal = [Vector3D(i*0.1, i*0.2, i*0.3) for i in range(N)]
_, peak_normal = tracemalloc.get_traced_memory()
tracemalloc.stop()

gc.collect()
tracemalloc.start()
objs_slots = [Vector3DSlots(i*0.1, i*0.2, i*0.3) for i in range(N)]
_, peak_slots = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"Without __slots__: {peak_normal/1024/1024:.1f} MB peak")
print(f"With    __slots__: {peak_slots/1024/1024:.1f} MB peak")
print(f"Savings: {(1 - peak_slots/peak_normal)*100:.0f}%")
```

**Why:** Each normal instance carries a `__dict__` hash map (~200–400 bytes overhead). `__slots__` replaces it with direct C-level struct fields. At 500k objects, this is a significant real-world saving.
</details>

---

<a id="q12"></a>

### Q12 · Capstone: Profile Slow Function, Fix Top Hotspot 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


Profile the function below, identify the single biggest hotspot from the `tottime` column, fix it, and verify the speedup:

```python
def process_records(records):
    results = ""
    for r in records:
        if r["score"] in [10, 20, 30, 40, 50]:
            results += f"match:{r['id']},"
    return results

records = [{"id": i, "score": i % 60} for i in range(50_000)]
```


<details>
<summary>💡 Hint</summary>
There are two bugs: list membership (`in [...]`) and string concatenation (`+=`). Profile first — which one shows up highest in `tottime`? Fix both.
</details>

<details>
<summary>✅ Answer</summary>

```python
import cProfile, timeit

records = [{"id": i, "score": i % 60} for i in range(50_000)]

def process_slow(records):
    results = ""
    for r in records:
        if r["score"] in [10, 20, 30, 40, 50]:   # creates list on every check
            results += f"match:{r['id']},"         # O(n²) string build
    return results

# Fix 1: use set for O(1) membership (created once outside loop)
# Fix 2: collect parts, join once
VALID_SCORES = {10, 20, 30, 40, 50}   # set literal: O(1) lookup

def process_fast(records):
    parts = []
    for r in records:
        if r["score"] in VALID_SCORES:   # O(1) set lookup
            parts.append(f"match:{r['id']}")
    return ",".join(parts)               # O(n) single join

assert process_slow(records).rstrip(",") == process_fast(records)

cProfile.run("process_slow(records)", sort="tottime")

t_slow = min(timeit.repeat(lambda: process_slow(records), repeat=3, number=10))
t_fast = min(timeit.repeat(lambda: process_fast(records), repeat=3, number=10))
print(f"Speedup: {t_slow/t_fast:.1f}x")
```

**Why:** The profiler reveals `str.__iadd__` and the list literal creation as the top consumers. Replacing with a set constant and `join()` removes both O(n²) patterns, achieving a large speedup.
</details>

---

## 📂 Navigation

| | |
|---|---|
| ⬆️ Root Theory | [../theory.md](../theory.md) |
| 📖 Optimization Patterns Theory | [theory.md](./theory.md) |
| 🔍 Profiling Tools Practice | [../01_profiling_tools/practice.md](../01_profiling_tools/practice.md) |

---

**[🏠 Back to README](../../README.md)**

**Prev:** [← Profiling Tools Practice](../01_profiling_tools/practice.md) &nbsp;|&nbsp; **Next:** [Root Theory →](../theory.md)
