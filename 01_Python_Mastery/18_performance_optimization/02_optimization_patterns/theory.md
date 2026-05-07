# ⚡ Optimization Patterns

A carpenter does not use a hammer for every job. Python performance is the same — choosing the right tool (data structure, algorithm, or technique) matters far more than tuning the wrong one.

---

## 📌 Learning Priority

**Must Learn**: list vs dict lookup O(1), generator expressions, local variable fast path
**Should Learn**: `__slots__`, `lru_cache`, NumPy vectorization over loops
**Good to Know**: `bytearray` for mutable bytes, `array` module, Cython basics
**Reference**: PyPy, Numba, ctypes

---

## 1. Algorithm and Data Structure Choices

> Before tuning the engine, make sure you are driving the right vehicle. An O(n) algorithm beats any amount of micro-optimization applied to O(n²) code.

The single biggest performance win is almost always at the **algorithm level**.

```python
# O(n) list membership — scans the entire list on every check
items = list(range(100_000))
if 99_999 in items:   # scans ~100k elements
    pass

# O(1) set membership — hash lookup, constant time regardless of size
items_set = set(range(100_000))
if 99_999 in items_set:  # one hash lookup
    pass
```

```python
# O(n²): find duplicates with nested scan
def find_dupes_slow(lst):
    seen = []
    for item in lst:
        if item in seen:   # ← O(n) scan on every iteration
            yield item
        seen.append(item)

# O(n): count in one pass with Counter
from collections import Counter
def find_dupes_fast(lst):
    return [k for k, v in Counter(lst).items() if v > 1]
```

Rule: always check complexity before writing any optimization code.

> 📝 Practice: [practice.md → Q1](./practice.md#q1--convert-list-search-to-dict-lookup-)

---

## 2. Generator Expressions

> A list loads all groceries into the cart at once. A generator hands you one item at a time — you never carry the whole store.

**Generator expressions** are lazy: they produce one value at a time and use O(1) memory regardless of input size. Lists are eager: they compute and store everything upfront.

```python
# Eager list — allocates all N elements in memory at once
squares_list = [x * x for x in range(1_000_000)]  # ~8 MB

# Lazy generator — computes on demand, no memory allocation
squares_gen = (x * x for x in range(1_000_000))   # ~200 bytes
```

When to use a generator instead of a list:
- You only need to iterate once (not index into it)
- The data is large and you do not need it all at once
- You are chaining operations (filter → map → reduce)

When NOT to use a generator:
- You need random access (`items[42]`)
- You need to iterate more than once
- You need `len()` before iterating

> 📝 Practice: [practice.md → Q2](./practice.md#q2--rewrite-list-comprehension-as-generator-)

---

## 3. Local Variables Are Faster Than Globals

> Every time Python sees a global name in a loop, it has to look it up in a dictionary. A local variable is just an array index — much faster.

Python's name lookup order is: **L**ocal → **E**nclosing → **G**lobal → **B**uilt-in (LEGB).

Local lookup uses `LOAD_FAST` (array index). Global lookup uses `LOAD_GLOBAL` (dictionary hash lookup). In a tight loop, this difference adds up.

```python
import math

# Slow: math.sqrt looked up in the global dict on every iteration
def compute_slow(points):
    return [math.sqrt(x * x + y * y) for x, y in points]

# Fast: one global lookup at function entry, then local array access
def compute_fast(points):
    sqrt = math.sqrt   # ← pull into local scope once
    return [sqrt(x * x + y * y) for x, y in points]
```

This is a micro-optimization — only matters in hot loops running millions of iterations.

> 📝 Practice: [practice.md → Q3](./practice.md#q3--local-variable-optimization-in-hot-loop-)

---

## 4. `__slots__` — Eliminating `__dict__` Overhead

> A normal Python object is like a suitcase — you can add anything but it is heavy. `__slots__` is like a wallet — fixed pockets, but much lighter.

Every normal Python instance stores its attributes in a `__dict__` — a hash map that costs ~200–400 bytes per object. **`__slots__`** replaces the dict with fixed C-level slots, saving 40–60% memory and slightly speeding up attribute access.

```python
class PointNormal:
    def __init__(self, x, y, z):
        self.x = x   # stored in self.__dict__
        self.y = y
        self.z = z

class PointSlots:
    __slots__ = ("x", "y", "z")  # ← declare fixed attributes
    def __init__(self, x, y, z):
        self.x = x   # stored in C-level slot, no __dict__
        self.y = y
        self.z = z

# Check: slots instances have no __dict__
p = PointSlots(1, 2, 3)
print(hasattr(p, "__dict__"))  # False
```

When `__slots__` helps: creating thousands or millions of small, fixed-attribute objects (geometry points, event records, parsed tokens).

When to avoid: if you need to add arbitrary attributes at runtime, or if the class has complex inheritance.

> 📝 Practice: [practice.md → Q4](./practice.md#q4--add-slots-to-a-class-)

---

## 5. `lru_cache` / `functools.cache` — Memoization

> If a function gives the same answer for the same inputs every time, just remember the answer and skip the work next time.

**Memoization** stores previous results and returns them immediately for repeated inputs. `functools.lru_cache` does this with one decorator line.

```python
from functools import lru_cache, cache

@lru_cache(maxsize=128)   # bounded: discards oldest entries when full
def fibonacci(n):
    if n < 2: return n
    return fibonacci(n - 1) + fibonacci(n - 2)

@cache                    # unbounded: keeps everything (Python 3.9+)
def expensive_lookup(key):
    return slow_database_call(key)

# Inspect cache performance
print(fibonacci.cache_info())
# CacheInfo(hits=34, misses=21, maxsize=128, currsize=21)

fibonacci.cache_clear()   # ← evict all cached results
```

When to avoid `lru_cache`:
- The function has side effects (mutates state, writes to DB)
- Inputs are unhashable (lists, dicts)
- Memory is tight and the cache would grow too large

> 📝 Practice: [practice.md → Q5](./practice.md#q5--apply-lru_cache-to-recursive-fibonacci-)

---

## 6. String Building — `join()` vs `+=` Loop

> Building a string with `+=` in a loop is like copying your essay by hand each time you add a sentence — every `+=` copies the whole thing.

Python strings are **immutable**. Every `+=` creates a brand-new string and copies all prior content into it — O(n²) total work for n concatenations. `str.join()` collects parts first and makes one copy at the end — O(n).

```python
# O(n²): 1000 items → ~500,000 character copies
def build_slow(items):
    result = ""
    for item in items:
        result += str(item) + ","  # ← copies entire string each time
    return result

# O(n): collect all parts, join once
def build_fast(items):
    return ",".join(str(item) for item in items)  # ← one allocation
```

The gap is small for 10 items. For 10,000 items, `join()` is typically 10–50x faster.

> 📝 Practice: [practice.md → Q6](./practice.md#q6--fix-string-concatenation-in-loop-)

---

## 7. NumPy Vectorization

> A Python `for` loop is a single worker doing one job at a time. NumPy vectorization is a factory floor — all elements processed simultaneously.

Python `for` loops over numbers are slow because each iteration is a full Python bytecode dispatch. **NumPy** moves the loop into compiled C code operating on contiguous memory blocks — no Python overhead per element.

```python
import numpy as np

# Python loop — slow: one Python dispatch per element
def sum_squares_python(n):
    total = 0.0
    for i in range(n):
        total += i * i
    return total

# NumPy vectorized — fast: C loop over contiguous array
def sum_squares_numpy(n):
    arr = np.arange(n, dtype=np.float64)
    return np.sum(arr * arr)   # ← element-wise multiply, then reduce
```

NumPy is best for: numeric computations, array math, signal processing, ML data pipelines.

Not worth it for: small arrays (<1000 elements), non-numeric data, code that is already fast enough.

> 📝 Practice: [practice.md → Q8](./practice.md#q8--replace-python-loop-with-numpy-vectorized-operation-)

---

## 8. Common Optimization Mistakes

**Micro-optimizing before profiling** — pulling globals into locals saves nanoseconds. An O(n²) algorithm costs seconds. Fix the algorithm first.

**Cache invalidation bugs** — `lru_cache` does not know when underlying data changes. If the function reads from a database or file, a stale cache returns wrong results silently.

**Over-using `__slots__`** — slots break pickling, `copy.copy`, and dynamic attribute assignment. Only add them when profiling confirms memory is the actual bottleneck.

**Vectorizing small arrays** — NumPy has overhead. For arrays with fewer than ~1000 elements, a plain Python list is often faster.

**Forgetting to profile after optimizing** — always confirm the speedup with numbers. Optimizations sometimes backfire.

> 📝 Practice: [practice.md → Q10](./practice.md#q10--identify-bottleneck-and-fix-)

---

## 📂 Navigation

| | |
|---|---|
| ⬆️ Root Theory | [../theory.md](../theory.md) |
| 💻 Practice | [practice.md](./practice.md) |
| 🔍 Profiling Tools | [../01_profiling_tools/theory.md](../01_profiling_tools/theory.md) |

---

**[🏠 Back to README](../../README.md)**

**Prev:** [← Profiling Tools](../01_profiling_tools/theory.md) &nbsp;|&nbsp; **Next:** [Root Theory →](../theory.md)

**Related Topics:** [Profiling Tools](../01_profiling_tools/theory.md) · [Root Theory](../theory.md) · [Cheatsheet](../cheetsheet.md)
