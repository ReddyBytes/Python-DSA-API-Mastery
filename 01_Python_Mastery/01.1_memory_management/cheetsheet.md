# ⚡ Cheatsheet: Memory Management

## 🏗️ Memory Layout
```
Stack: function frames, variable references (fast, auto-managed)
Heap:  actual objects (dynamic, GC-managed)
Variables = references (pointers), NOT containers
```

## ♻️ Garbage Collection
```python
import gc
gc.collect()           # manual GC
gc.collect(0)          # gen 0 only (cheapest)
gc.collect(1)          # gen 0 + 1
gc.collect(2)          # full — all generations
gc.enable() / gc.disable()
gc.get_count()         # (gen0, gen1, gen2) — allocations since last collection per gen
                       # gen0 triggers at 700, gen1 at 10 gen0-runs, gen2 at 10 gen1-runs
gc.get_threshold()     # (700, 10, 10) by default
gc.set_threshold(n0, n1, n2)
gc.get_objects()       # list of all GC-tracked objects (debugging)
gc.garbage             # list of uncollectable objects (normally empty)
# GC callbacks — production monitoring:
gc.callbacks.append(lambda phase, info: print(phase, info))
```

## 🔢 Object Interning
```
Integer cache:  -5 to 256  (always same object)
String interning: short identifiers (implementation dependent)
Force string intern: sys.intern("string")
```

## 🆚 is vs ==
```python
x is y      # same object in memory (same id)
x == y      # same value
# Use 'is' only for: None, True, False
# Use '==' for value comparisons
```

## 📋 Mutable vs Immutable
```
IMMUTABLE (new object on change):  int, float, str, bool, tuple, frozenset
MUTABLE (same object modified):    list, dict, set, bytearray
```

## 📋 Copy Types
```python
import copy
b = a                    # alias (same object!)
b = a.copy()             # shallow copy (one level deep)
b = a[:]                 # shallow copy (lists)
b = copy.copy(a)         # shallow copy
b = copy.deepcopy(a)     # deep copy (fully independent)
```

## 💾 Memory Optimization
```python
# __slots__ — saves ~40-60% memory per instance (removes __dict__)
class Point:
    __slots__ = ['x', 'y']
# Normal:  obj (~48B) + __dict__ (~232B) = ~280B total
# Slotted: ~112B total  (no __dict__, fixed slots only)
# Trade-off: cannot add arbitrary attributes after creation

# Generator vs list
gen = (x**2 for x in range(1_000_000))   # ~112 bytes (constant)
lst = [x**2 for x in range(1_000_000)]   # ~8 MB (all items allocated)

# Measure size (SHALLOW — does not count nested objects!)
sys.getsizeof(obj)

# Delete large objects explicitly + force GC between phases
del big_object
gc.collect()

# Chunked processing — keep memory bounded at O(chunk_size)
def chunked(iterable, size):
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk

# String interning — one object for all equal strings
import sys as _sys
s = _sys.intern("status_code")  # forces same object for all equal interns
```

## 🔍 Weak References
```python
import weakref
weak = weakref.ref(obj)           # doesn't increment refcount
obj_or_none = weak()              # None if object was GC'd
cache = weakref.WeakValueDictionary()  # auto-clears when values GC'd
# Weak ref with deletion callback:
def on_delete(ref):
    print("Object was collected!")
weak_with_cb = weakref.ref(obj, on_delete)
```

## 🧠 Memory Profiling
```python
# Built-in — tracemalloc (standard leak diagnosis workflow)
import tracemalloc
tracemalloc.start()
baseline = tracemalloc.take_snapshot()
# ... run suspect code ...
after = tracemalloc.take_snapshot()
diff = after.compare_to(baseline, "lineno")  # sorted by size increase
for stat in diff[:5]:
    print(stat)   # file:line — count — size delta
tracemalloc.stop()

# Per-line snapshot (no comparison)
snapshot = tracemalloc.take_snapshot()
for stat in snapshot.statistics('lineno')[:5]:
    print(stat)

# Third-party
# memory_profiler: @profile decorator, line-by-line MiB output
# objgraph: visualize reference graphs
```

## 🔗 Reference Counting — sys.getrefcount() Gotcha
```python
import sys
x = [1, 2, 3]
sys.getrefcount(x)     # ALWAYS +1 extra (the call argument is a temp ref)
id(x)                  # memory address / identity

# ref_count goes UP:  assignment, passed to func, in container
# ref_count goes DOWN: del x, reassign, out of scope, removed from container
# Real count = sys.getrefcount(x) - 1
```

## ⚠️ Common Memory Pitfalls
```
1. Circular references — use weakref to break cycles
2. Global containers growing forever — use WeakValueDictionary for caches
3. Large objects not deleted — use del + gc.collect()
4. Mutable default args — use None, create inside function
5. Aliasing — use copy.deepcopy() when you need independence
6. __del__ + cycles — Python 3.4+ handles it, but be aware
```

## 📊 Common Object Sizes
```
None     16 bytes    |   []      56 bytes
True     28 bytes    |   [1]     64 bytes
0        24 bytes    |   {}      64 bytes
"a"      50 bytes    |   set()   216 bytes
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Interview Q&A](./interview.md)
