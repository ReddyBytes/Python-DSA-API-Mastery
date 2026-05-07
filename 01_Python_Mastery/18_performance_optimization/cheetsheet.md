# ⚡ Performance Optimization — Cheetsheet

> Quick reference: profiling tools, timeit syntax, complexity table, __slots__, bottlenecks, optimization checklist, Numba/Cython.

---

## 🔍 Profiling Tools Comparison

| Tool | Level | What It Shows | Install |
|---|---|---|---|
| `cProfile` | Function | Call count, tottime, cumtime | stdlib |
| `line_profiler` | Line | Time per line (annotate with `@profile`) | `pip install line-profiler` |
| `memory_profiler` | Line | Memory delta per line | `pip install memory-profiler` |
| `tracemalloc` | Object | Allocation snapshots, top offenders | stdlib |
| `py-spy` | Sampling | Flamegraph, attaches to running process | `pip install py-spy` |
| `scalene` | Combined | CPU + memory + GPU in one tool | `pip install scalene` |

---

## 🕐 timeit Syntax

```python
import timeit

# One-liner
timeit.timeit("sum(range(1000))", number=10_000)

# Multi-line with setup
timeit.timeit(
    stmt="[x**2 for x in data]",
    setup="data = list(range(1000))",
    number=1000
)

# In Jupyter / IPython
%timeit sum(range(1000))
%%timeit
result = [x**2 for x in range(1000)]

# Timer object (reusable)
t = timeit.Timer("sorted(data)", setup="data = list(range(1000, 0, -1))")
print(min(t.repeat(5, 1000)))   # best of 5 runs
```

---

## 📊 cProfile Usage

```python
import cProfile
import pstats

# Profile a function
cProfile.run("my_function()")

# Save to file, then analyze
cProfile.run("my_function()", "profile_output")
stats = pstats.Stats("profile_output")
stats.sort_stats("cumulative")
stats.print_stats(10)    # top 10 functions

# As context manager
with cProfile.Profile() as prof:
    my_function()
prof.print_stats(sort="cumulative")
```

Key columns: `ncalls` · `tottime` (own time) · `cumtime` (incl. subcalls) · `percall`

---

## ⏱️ Complexity Cheatsheet

| Operation | Data Structure | Complexity |
|---|---|---|
| Index access | list, tuple | O(1) |
| Append | list | O(1) amortized |
| Insert/delete middle | list | O(n) |
| Membership test | list | O(n) |
| Membership test | set, dict | O(1) |
| Add/remove | set, dict | O(1) average |
| Sort | list | O(n log n) |
| deque append/pop left | deque | O(1) |
| heappush/heappop | heapq | O(log n) |
| Binary search | sorted list | O(log n) |

```
O(1)      constant   → dict lookup, set membership
O(log n)  log        → binary search, heapq
O(n)      linear     → list scan, sum, max
O(n log n)           → sorted(), timsort
O(n²)     quadratic  → naive nested loops
```

---

## 🔧 `__slots__` — Before vs After

```python
# Without __slots__  — uses __dict__ per instance (large overhead)
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# With __slots__ — fixed attributes, no __dict__, ~30-50% less memory
class Point:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

# When beneficial: millions of small objects
import sys
p_normal = type("P", (), {"__init__": lambda s,x,y: setattr(s,"x",x) or setattr(s,"y",y)})()
# slots saves ~200 bytes per object at scale
```

| | Without `__slots__` | With `__slots__` |
|---|---|---|
| Memory | `__dict__` (~200–400B) | fixed slots (~50B) |
| Attribute access | slightly slower | slightly faster |
| Dynamic attributes | allowed | blocked |
| Inheritance | straightforward | must redeclare slots |

---

## 🐌 Common Bottlenecks Table

| Bottleneck | Symptom | Fix |
|---|---|---|
| List membership in loop | `x in big_list` repeatedly | Convert to `set` |
| Repeated function calls in loop | `math.sqrt` every iteration | Cache: `sqrt = math.sqrt` |
| String concatenation in loop | `s += chunk` n times | `"".join(parts)` |
| N+1 query | DB call per item | Batch query / prefetch |
| Loading full file | `f.read()` on large file | Iterate line-by-line / chunked |
| No caching | Same computation repeated | `@functools.lru_cache` |
| Global variable lookup | global in hot loop | Assign to local |
| List where deque needed | `pop(0)` on list | `collections.deque` |

---

## ✅ Optimization Checklist

```
[ ] Profile first — never guess (cProfile → find top cumtime)
[ ] Algorithm complexity correct? (O(n²) → O(n log n) beats micro-opts)
[ ] Right data structure? (set for lookup, deque for queue)
[ ] Avoid re-computation (lru_cache, pre-compute outside loops)
[ ] Generators instead of lists where full list not needed
[ ] __slots__ for millions of small objects
[ ] str.join() not += for string building
[ ] Batch I/O operations (DB, file, network)
[ ] Local variable instead of global/attribute in tight loops
[ ] Consider concurrency: asyncio (I/O-bound) / multiprocessing (CPU-bound)
```

---

## 🚀 lru_cache / cache

```python
from functools import lru_cache, cache

@lru_cache(maxsize=128)     # bounded LRU cache
def fibonacci(n):
    if n < 2: return n
    return fibonacci(n-1) + fibonacci(n-2)

@cache                      # unbounded (Python 3.9+), simpler
def expensive(key):
    return slow_computation(key)

fibonacci.cache_info()      # CacheInfo(hits=..., misses=..., maxsize=128, currsize=...)
fibonacci.cache_clear()     # evict all
```

---

## 🔥 Numba / Cython — When to Reach

| Tool | When | Speedup | Effort |
|---|---|---|---|
| `numba` JIT | Numpy/array loops, math-heavy functions | 10–200x | Low — just add `@jit` |
| `Cython` | Complex Python to C, production libs | 5–100x | Medium — rewrite in .pyx |
| `PyPy` | General Python (non-CPython) | 3–10x | Low — just run with PyPy |
| `C extension` | Maximum control, library integration | Custom | High |

```python
# Numba — minimal change, massive gain for numeric loops
from numba import jit
import numpy as np

@jit(nopython=True)
def sum_array(arr):
    total = 0.0
    for x in arr:
        total += x
    return total

arr = np.arange(1_000_000, dtype=np.float64)
sum_array(arr)    # first call compiles; subsequent calls are C-speed
```

Reach for Numba when: pure Python loop over large array, no easy vectorization.
Reach for Cython when: building a library, need type declarations, embedding in C project.

---

## 📌 Learning Priority

**Must Learn** — daily use, interview essential:
`cProfile` · `timeit` · Algorithm complexity table · generator vs list tradeoff

**Should Learn** — real projects:
`memory_profiler` · `tracemalloc` · `__slots__` · `lru_cache` · `dis` module

**Good to Know** — specific situations:
`py-spy` · flamegraph reading · `scalene` · Numba basics

**Reference** — know it exists:
`numexpr` · NUMA awareness · SIMD vectorization

---

## 🔬 tracemalloc — Memory Leak Detection

```python
import tracemalloc

# Single snapshot: measure peak memory of a block
tracemalloc.start()
result = [float(i) for i in range(100_000)]
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(f"Peak: {peak / 1024:.1f} KiB")

# Compare two snapshots: find what grew (leak detection)
tracemalloc.start()
snap1 = tracemalloc.take_snapshot()
run_suspicious_code()
snap2 = tracemalloc.take_snapshot()
tracemalloc.stop()

top_diff = snap2.compare_to(snap1, "lineno")
for stat in top_diff[:5]:
    print(stat)   # file:line: size_KB KiB (+N allocations)
```

---

## 🐍 snakeviz — Flamegraph Visualization

```python
# Step 1: save profile to file
import cProfile
cProfile.run("my_function()", "profile_output.prof")

# Step 2: visualize in browser
# pip install snakeviz
# snakeviz profile_output.prof
```

Reading the icicle chart:
- Width = cumulative time (wider = slower)
- Inner boxes = functions called from the outer function
- Follow the widest box down to find the actual hotspot leaf
- Click any box to zoom in on that call subtree

---

## ⏱️ timeit Best Practices

```python
import timeit

# Always use min() not mean() — min = best CPU availability
best = min(timeit.repeat("sorted(range(100))", repeat=5, number=10_000))
per_call_us = best / 10_000 * 1e6

# Pass globals for benchmarking your own functions
def my_func(n): return sum(range(n))
t = min(timeit.repeat("my_func(1000)", globals=globals(), repeat=5, number=1000))

# Rule of thumb: enough iterations for total time > 100ms (reduces noise)
```

---

## 🔥 Rapid-Fire

```
Q: Measure a code snippet 1000 times?
A: timeit.timeit("snippet", number=1000)

Q: Find which function is slowest?
A: cProfile — sort by cumtime, look at top entries

Q: tottime vs cumtime?
A: tottime = time in function only. cumtime = function + all it calls.

Q: When does __slots__ hurt?
A: Inheritance — subclasses must redeclare slots or get __dict__ anyway.

Q: Generator vs list comprehension?
A: Generator: lazy, O(1) memory. List: eager, O(n) memory. Use generator when iterating once.

Q: list.pop(0) is slow — why?
A: O(n) — shifts all elements. Use collections.deque.popleft() → O(1).

Q: When NOT to optimize?
A: When not measured, in early prototypes, when it adds complexity without clear gain.
Q: lru_cache.cache_info() — what does it show?
A: CacheInfo(hits, misses, maxsize, currsize) — check hits >> misses for effectiveness.

Q: tracemalloc to find a leak?
A: Take snap1, run suspicious code, take snap2. snap2.compare_to(snap1, "lineno") shows growth.

Q: snakeviz — what does width represent?
A: Cumulative time. Follow the widest box downward to find the real hotspot leaf.

Q: timeit — use mean or min?
A: Always min(timeit.repeat(...)). Mean is skewed by OS interrupts and GC pauses.
```

---

## 🧭 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 💻 Practice | [practice.md](./practice.md) |
| 🔍 Profiling Tools | [01_profiling_tools/theory.md](./01_profiling_tools/theory.md) |
| ⚡ Optimization Patterns | [02_optimization_patterns/theory.md](./02_optimization_patterns/theory.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| ⬅️ Previous | [17 — Testing](../17_testing/cheetsheet.md) |
| ➡️ Next | [19 — Production Best Practices](../19_production_best_practices/packaging.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Testing](../17_testing/cheetsheet.md) &nbsp;|&nbsp; **Next:** [Production Best Practices →](../19_production_best_practices/packaging.md)

**Related Topics:** [Theory](./theory.md) · [Practice](./practice.md) · [Interview Q&A](./interview.md)
