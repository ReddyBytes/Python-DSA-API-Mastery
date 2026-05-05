# ⚡ Cheatsheet: Memory Management

## 🏗️ Memory Layout
```
Stack: function frames, variable references (fast, auto-managed)
Heap:  actual objects (dynamic, GC-managed)
Variables = references (pointers), NOT containers
```

## 🔗 Reference Counting
```python
import sys
sys.getrefcount(x)     # reference count (add 1 for func arg)
id(x)                  # memory address / identity

# ref_count goes UP:  assignment, passed to func, in container
# ref_count goes DOWN: del x, reassign, out of scope, removed from container
```

## ♻️ Garbage Collection
```python
import gc
gc.collect()           # manual GC
gc.enable() / gc.disable()
gc.get_count()         # (gen0, gen1, gen2) object counts
gc.get_threshold()     # (700, 10, 10) by default
gc.set_threshold(n0, n1, n2)
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
# __slots__ — saves ~40% memory for many instances
class Point:
    __slots__ = ['x', 'y']

# Generator vs list
gen = (x**2 for x in range(1M))   # ~200 bytes
lst = [x**2 for x in range(1M)]   # ~8 MB

# Measure size
sys.getsizeof(obj)    # bytes (doesn't count nested objects!)

# Delete large objects explicitly
del big_object
gc.collect()
```

## 🔍 Weak References
```python
import weakref
weak = weakref.ref(obj)           # doesn't increment refcount
obj_or_none = weak()              # None if object was GC'd
cache = weakref.WeakValueDictionary()  # auto-clears when values GC'd
```

## 🧠 Memory Profiling
```python
# Built-in
import tracemalloc
tracemalloc.start()
# ... code ...
snapshot = tracemalloc.take_snapshot()
for stat in snapshot.statistics('lineno')[:5]:
    print(stat)

# Third-party
# memory_profiler: @profile decorator, line-by-line
# objgraph: visualize reference graphs
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
