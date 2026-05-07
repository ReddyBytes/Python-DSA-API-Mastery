# Interview

# 🧠 Memory Management in Python — Interview Questions & Deep Answers

> This file prepares you for 3–10 year experience level interviews.
> Not just definitions — but thinking clarity.

If you can explain these confidently with diagrams in mind,
you are no longer a beginner.

---

# 🔹 Basic Level (0–2 Years)

**Q1: How does Python manage memory?**

<details>
<summary>💡 Show Answer</summary>

Python automatically manages memory using:

- Reference Counting (primary mechanism)
- Cyclic Garbage Collector (secondary mechanism)

Objects are stored in heap memory.
Variables store references to those objects.

When reference count becomes zero,
the object is deleted.

</details>

<br>

**Q2: What is reference counting?**

<details>
<summary>💡 Show Answer</summary>

Each object keeps track of how many references point to it.

Example:

```python
a = [1, 2]
b = a
```

Reference count = 2

If:

```python
del b
```

Reference count = 1

If it becomes 0 → object is removed.

</details>

<br>

**Q3: What is garbage collection in Python?**

<details>
<summary>💡 Show Answer</summary>

Garbage collection is the process of removing unused objects from memory.

Python uses:

- Reference counting
- Generational cyclic garbage collector

</details>

<br>

**Q4: What is the difference between stack and heap in Python?**

<details>
<summary>💡 Show Answer</summary>

Stack:
- Stores function calls
- Stores references (local variables)

Heap:
- Stores objects (lists, dicts, numbers, class instances)

Python abstracts stack/heap details,
but conceptually this separation exists.

</details>


# 🔹 Intermediate Level (2–5 Years)

**Q5: What is circular reference? Why is it a problem?**

<details>
<summary>💡 Show Answer</summary>

Circular reference happens when:

Object A references Object B  
Object B references Object A  

Example:

```python
a = []
b = []

a.append(b)
b.append(a)
```

Reference count never becomes zero,
even if both variables are deleted.

Reference counting alone cannot clean this.

That’s why Python has cyclic GC.

</details>

<br>

**Q6: How does Python handle circular references?**

<details>
<summary>💡 Show Answer</summary>

Python has a cyclic garbage collector that:

- Periodically scans objects
- Detects unreachable cycles
- Frees them

It works alongside reference counting.

</details>

<br>

**Q7: What are generations in garbage collection?**

<details>
<summary>💡 Show Answer</summary>

Python divides objects into:

- Generation 0 (young objects)
- Generation 1
- Generation 2 (long-living objects)

Most objects die young.
So Python checks younger generations more frequently.

This improves performance.

</details>

<br>

**Q8: What is small integer interning?**

<details>
<summary>💡 Show Answer</summary>

Python pre-creates small integers
(typically -5 to 256).

Example:

```python
a = 100
b = 100
print(a is b)  # True
```

This saves memory and improves performance.

Never rely on `is` for value comparison.

</details>

<br>

**Q9: What is the difference between `is` and `==`?**

<details>
<summary>💡 Show Answer</summary>

`==` → compares values  
`is` → compares identity (memory location)

Example:

```python
a = [1]
b = [1]

a == b  # True
a is b  # False
```

</details>

<br>

**Q10: Can Python have memory leaks?**

<details>
<summary>💡 Show Answer</summary>

Yes.

Common causes:

- Circular references with custom objects
- Global variables holding large objects
- C extensions not releasing memory
- Large caches not cleared
- Long-running services accumulating objects

Even with GC, memory leaks are possible.

</details>


# 🔹 Advanced Level (5–10 Years)

**Q11: Explain how Python allocates memory internally.**

<details>
<summary>💡 Show Answer</summary>

In CPython:

- Every object is a PyObject structure.
- Objects are allocated in heap.
- Python uses a private heap.
- Memory allocator (pymalloc) manages small objects efficiently.
- OS-level memory allocation happens in chunks (arenas, pools, blocks).

Small objects are optimized using pymalloc.

</details>

<br>

**Q12: What is pymalloc?**

<details>
<summary>💡 Show Answer</summary>

Pymalloc is Python’s specialized memory allocator for small objects.

It reduces fragmentation and improves performance.

It manages memory in:

- Arenas (large chunks)
- Pools
- Blocks

This avoids frequent OS calls.

</details>

<br>

**Q13: Why does memory usage not immediately drop after deleting objects?**

<details>
<summary>💡 Show Answer</summary>

Because:

- Python may keep memory for reuse.
- OS memory is not always returned immediately.
- Fragmentation can occur.

Deleting object ≠ returning memory to OS instantly.

This confuses many developers in production.

</details>

<br>

**Q14: How do you debug memory issues in production?**

<details>
<summary>💡 Show Answer</summary>

Tools professionals use:

- tracemalloc
- gc module
- memory_profiler
- objgraph
- Heapy

Example:

```python
import tracemalloc
tracemalloc.start()
```

Then compare snapshots.

</details>

<br>

**Q15: What happens when you pass a large object to a function?**

<details>
<summary>💡 Show Answer</summary>

Python passes reference,
not a copy.

Example:

```python
def modify(lst):
    lst.append(10)
```

If you pass a list,
original list may change.

Important in APIs and pipelines.

</details>

<br>

**Q16: How does mutability impact memory?**

<details>
<summary>💡 Show Answer</summary>

Immutable objects:
- New object created on change.

Mutable objects:
- Same object modified.

Mutable objects can cause shared state bugs.

</details>

<br>

**Q17: What is reference cycle detection threshold?**

<details>
<summary>💡 Show Answer</summary>

Python does not check cycles continuously.

It runs cyclic GC based on thresholds.

You can inspect:

```python
import gc
gc.get_threshold()
```

This is rarely asked,
but mentioning it shows depth.

</details>


# 🔥 Scenario-Based Questions

## Scenario 1:

Memory increases slowly in a long-running service. Why?

<details>
<summary>💡 Show Answer</summary>

Possible reasons:

- Circular references
- Growing global cache
- Objects stored in class-level variables
- Unclosed file handles
- Large lists accumulating data

</details>
---

## Scenario 2:

You delete a large list but memory usage does not reduce. Why?

<details>
<summary>💡 Show Answer</summary>

Because:

- Python keeps memory for reuse
- Fragmentation
- Memory not returned to OS immediately

</details>
---

## Scenario 3:

Why is `a is b` sometimes True for integers?

<details>
<summary>💡 Show Answer</summary>

Because of small integer interning.

</details>
---

# 🧠 Senior-Level Summary Answer

If interviewer asks:

“How does Python manage memory?”

Professional answer:

Python primarily uses reference counting to track object lifetimes.  
To handle circular references, it uses a generational cyclic garbage collector.  
Memory allocation for small objects is optimized using pymalloc, which manages arenas, pools, and blocks.  
Although Python automatically manages memory, memory leaks can still occur due to circular references, global state, or external C extensions.

That answer sounds like 5+ years experience.

---

# 🔬 Deep-Dive Additions

**Q18: What does `gc.get_count()` return and how do you interpret it?**

<details>
<summary>💡 Show Answer</summary>

`gc.get_count()` returns a tuple `(n0, n1, n2)` — the number of tracked objects allocated since the last collection at each generation level.

```python
import gc
gc.collect()
print(gc.get_count())   # e.g. (45, 3, 0)
# n0: new objects since last gen-0 collection
# n1: how many times gen-0 was collected since last gen-1 collection
# n2: how many times gen-1 was collected since last gen-2 collection
```

When `n0` reaches the threshold (default 700), gen 0 is scanned. When `n1` reaches 10, gen 1 is scanned. This tells you how close the GC is to triggering.

</details>

<br>

**Q19: How does `tracemalloc` help find memory leaks in production?**

<details>
<summary>💡 Show Answer</summary>

`tracemalloc` records which file and line number allocated each block of memory. The workflow is:

```python
import tracemalloc

tracemalloc.start()
baseline = tracemalloc.take_snapshot()

# ... run suspect code ...

after = tracemalloc.take_snapshot()
diff = after.compare_to(baseline, "lineno")

for stat in diff[:5]:
    print(stat)   # shows file:line, count, size delta
```

The diff is sorted by size increase — the top entries are exactly the lines leaking memory. No guessing, no profiling overhead except when running.

</details>

<br>

**Q20: What is `weakref.ref()` and when would you use it?**

<details>
<summary>💡 Show Answer</summary>

`weakref.ref()` creates a reference to an object that does NOT increment its reference count. If all strong references are removed, the object is garbage collected even while weak references exist — they return `None` after collection.

```python
import weakref

obj = SomeHeavyObject()
weak = weakref.ref(obj)

print(weak())        # the object, if still alive
del obj
print(weak())        # None — object was collected
```

Primary use case: caches. A `weakref.WeakValueDictionary` lets cached objects be collected when nothing else needs them, without the cache itself being the reason they live forever. Prevents the "cache that never shrinks" memory leak pattern.

</details>

<br>

**Q21: What is the memory difference between `__slots__` and `__dict__` in a class?**

<details>
<summary>💡 Show Answer</summary>

Every normal Python class instance carries a `__dict__` — a hash table mapping attribute names to values. This adds ~200–400 bytes of overhead per instance.

`__slots__` replaces `__dict__` with pre-allocated fixed slots:

```python
class RegularUser:
    def __init__(self, name, age):
        self.name = name; self.age = age
# Each instance: object (48B) + __dict__ (232B) = ~280B

class SlottedUser:
    __slots__ = ['name', 'age']
    def __init__(self, name, age):
        self.name = name; self.age = age
# Each instance: ~112B — no __dict__
```

Trade-off: slotted objects cannot have arbitrary attributes added after creation (`AttributeError`). Use `__slots__` for value objects created in large quantities (embeddings, sensor readings, user records in data pipelines).

</details>

<br>

**Q22: What is the `sys.getrefcount()` gotcha?**

<details>
<summary>💡 Show Answer</summary>

`sys.getrefcount(obj)` always returns at least 1 more than you expect:

```python
import sys
x = [1, 2, 3]
print(sys.getrefcount(x))  # 2, not 1
```

The extra reference is the temporary reference created by passing `x` as the function argument. The call itself holds a reference during execution. Always subtract 1 from the result to get the "real" count.

This is a common source of confusion when debugging reference counting behavior.

</details>

---

# 🎯 Rapid-Fire Quick Checks

- Variables store references, not values.
- Reference count zero → object deleted.
- Circular references need cyclic GC.
- Small integers are interned.
- `is` checks identity.
- Python uses private heap.
- Memory not always returned to OS immediately.

If these are clear,
your foundation is strong.

---

# 🔁 Navigation

[Fundamentals](/01_Python_Mastery/01_python_fundamentals/theory.md)  
[Memory Management Theory](/01_Python_Mastery/memory_management/theory.md)  
[Data Types](/01_Python_Mastery/03_data_types/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheetsheet.md) &nbsp;|&nbsp; **Next:** [Python Fundamentals — Theory →](../01_python_fundamentals/theory.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheetsheet.md)
