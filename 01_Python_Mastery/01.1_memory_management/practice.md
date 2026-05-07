# Memory Management — Practice

## Quick Index

| Q | Topic | Difficulty |
|---|---|---|
| [Q1](#q1) | stack vs heap — where Python stores variables | 🟢 |
| [Q2](#q2) | stack frame lifecycle — what happens on function call/return | 🟢 |
| [Q3](#q3) | heap allocation — multiple labels, one object | 🟢 |
| [Q4](#q4) | sys.getrefcount() — read and explain the count | 🟢 |
| [Q5](#q5) | reference counting — increment and decrement | 🟢 |
| [Q6](#q6) | reference counting — when is an object freed? | 🟢 |
| [Q7](#q7) | circular references — the problem reference counting can't solve | 🟡 |
| [Q8](#q8) | gc.collect() — manually trigger garbage collection | 🟡 |
| [Q9](#q9) | gc.get_count() and generations — reading GC state | 🟡 |
| [Q10](#q10) | generators vs lists — memory comparison | 🟡 |
| [Q11](#q11) | generator pipeline — O(1) memory chain | 🟡 |
| [Q12](#q12) | __slots__ — add to a class and explain savings | 🟡 |
| [Q13](#q13) | __slots__ vs __dict__ — measure the difference | 🟡 |
| [Q14](#q14) | weakref.ref() — reference without holding the object alive | 🟡 |
| [Q15](#q15) | WeakValueDictionary — self-cleaning cache | 🟡 |
| [Q16](#q16) | local vs global lifetime — variable scope and memory | 🟢 |
| [Q17](#q17) | closure cell on heap — why enclosing variables survive | 🟠 |
| [Q18](#q18) | nonlocal — mutating an enclosing variable | 🟡 |
| [Q19](#q19) | tracemalloc snapshot — before/after comparison | 🟠 |
| [Q20](#q20) | sys.getsizeof() — measuring object sizes | 🟢 |
| [Q21](#q21) | memory_profiler @profile — line-by-line memory | 🟡 |
| [Q22](#q22) | avoid large globals — prefer local scope | 🟡 |
| [Q23](#q23) | chunked processing — bounded memory over large data | 🟠 |
| [Q24](#q24) | del + gc.collect() — explicit cleanup between heavy phases | 🟡 |
| [Q25](#q25) | capstone — diagnose and fix a memory leak scenario | 🟠 |

---

### Q1 · stack vs heap — where Python stores variables 🟢

You write three lines of Python:

```python
name = "Alice"
age  = 25
city = "London"
```

Describe where `name`, `age`, and `city` live versus where `"Alice"`, `25`, and `"London"` live. Draw the relationship.

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Think whiteboard (stack) vs drawer (heap) — labels vs the actual things.
</details>

<details>
<summary>✅ Answer</summary>

```
STACK (labels/references)    HEAP (actual objects)
──────────────────────────   ──────────────────────
name ──────────────────────► "Alice"
age  ──────────────────────► 25
city ──────────────────────► "London"
```

The variable names `name`, `age`, `city` live in the current stack frame.
The actual values `"Alice"`, `25`, `"London"` are objects stored in the heap.

**Why:** Python variables are references (labels), not containers. Objects always live in the heap; the stack just holds the pointers to them.
</details>

---

### Q2 · stack frame lifecycle — what happens on function call/return 🟢

Trace what happens in memory when this code runs:

```python
def greet(name):
    msg = "Hello, " + name
    return msg

result = greet("Alice")
```

What exists on the stack during `greet()`? What is destroyed when it returns? What survives?

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

<details>
<summary>💡 Hint</summary>
When a function returns, its frame is destroyed — but heap objects survive if something still holds a reference to them.
</details>

<details>
<summary>✅ Answer</summary>

```
DURING greet("Alice"):
  STACK
  ├── greet() frame
  │     name → "Alice"   (heap)
  │     msg  → "Hello, Alice"  (heap)
  └── global frame (paused)
        result → ???

AFTER return:
  STACK
  └── global frame
        result → "Hello, Alice"  (heap)
  greet() frame DESTROYED — name and msg bindings gone
```

**Why:** Frame destruction removes name bindings, not the heap objects. `"Hello, Alice"` survives because `result` in the global frame still holds a reference to it.
</details>

---

### Q3 · heap allocation — multiple labels, one object 🟢

What does Python do in memory when you write:

```python
a = "Alice"
b = a
```

Is `b` a copy of `"Alice"` or a second label pointing to the same object? How would you verify?

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Use `id()` to check identity — if two names point to the same object, `id(a) == id(b)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
a = "Alice"
b = a
print(id(a) == id(b))  # True — same object
print(a is b)          # True — same object

# STACK     HEAP
# a ──────► "Alice"
# b ──────► (same "Alice", no copy)
```

**Why:** Python stores one value in the heap and lets multiple labels point to it. No copy is made. This is why mutable objects shared between names can cause surprises.
</details>

---

### Q4 · sys.getrefcount() — read and explain the count 🟢

Run this code and explain why the count is higher than you might expect:

```python
import sys
obj = [1, 2, 3]
print(sys.getrefcount(obj))
```

Why is the result always at least 2, not 1?

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Passing `obj` to `getrefcount()` itself creates a temporary reference during the call.
</details>

<details>
<summary>✅ Answer</summary>

```python
import sys
obj = [1, 2, 3]
print(sys.getrefcount(obj))  # 2 (at minimum)
# Reference 1: the variable `obj`
# Reference 2: the temporary reference created by the getrefcount() call argument
```

**Why:** `sys.getrefcount()` always returns count + 1 because passing the object as an argument creates a temporary reference inside the function call. Always subtract 1 from the result to get the "real" count.
</details>

---

### Q5 · reference counting — increment and decrement 🟢

Show the reference count of a list as you: create it, assign a second name, add it to a container, then remove each reference. Explain each step.

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Count goes up with: assignment, passing to function, added to container. Down with: `del`, reassignment, removed from container, out of scope.
</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

x = [1, 2, 3]
print(sys.getrefcount(x))  # 2 (x + call arg)

y = x
print(sys.getrefcount(x))  # 3 (x, y, call arg)

container = [x]
print(sys.getrefcount(x))  # 4 (x, y, container[0], call arg)

del y
print(sys.getrefcount(x))  # 3

container.clear()
print(sys.getrefcount(x))  # 2 — back to just x + call arg
```

**Why:** Every binding — variable, container slot, function argument — increments the count. Every removal decrements it. When it hits zero, the object is freed immediately.
</details>

---

### Q6 · reference counting — when is an object freed? 🟢

Write a class with a `__del__` method. Create an instance, add a second reference, then delete them one by one. Observe exactly when the object is destroyed.

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`__del__` is called the instant the reference count hits zero — not at the end of the program.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Tracked:
    def __init__(self, name):
        self.name = name
        print(f"[CREATED] {self.name}")

    def __del__(self):
        print(f"[DELETED] {self.name}")  # fires when refcount → 0

obj = Tracked("obj_A")   # [CREATED] obj_A
ref2 = obj               # refcount = 2, nothing deleted yet
del ref2                 # refcount = 1, no deletion yet
del obj                  # refcount = 0 → [DELETED] obj_A immediately
```

**Why:** Reference counting frees objects immediately when the last reference is removed — no GC scan needed. This handles ~95% of Python memory management.
</details>

---

### Q7 · circular references — the problem reference counting can't solve 🟡

Create two objects that reference each other. Delete the external names. Show that `__del__` is NOT called. Then use `gc.collect()` to fix it.

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Disable the GC first with `gc.disable()` so you can prove the problem before fixing it.
</details>

<details>
<summary>✅ Answer</summary>

```python
import gc

class Node:
    def __init__(self, name):
        self.name = name
        self.partner = None
    def __del__(self):
        print(f"[DELETED] {self.name}")

gc.disable()

a = Node("A")
b = Node("B")
a.partner = b   # A holds B
b.partner = a   # B holds A — cycle!

del a
del b
# Notice: [DELETED] NOT printed — both stuck with refcount > 0

collected = gc.collect()
print(f"GC freed {collected} objects")  # [DELETED] A and B appear here
gc.enable()
```

**Why:** The cycle keeps both objects' reference counts at 1 even after external names are deleted. Only the cyclic GC can detect and break this cycle.
</details>

---

### Q8 · gc.collect() — manually trigger garbage collection 🟡

Demonstrate `gc.collect()` with per-generation control. Show:
- `gc.collect(0)` — gen 0 only
- `gc.collect(1)` — gen 0 and 1
- `gc.collect(2)` — full collection

Also show `gc.get_threshold()` and explain the default `(700, 10, 10)`.

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

<details>
<summary>💡 Hint</summary>
The threshold tuple means: collect gen0 after 700 allocations, gen1 after gen0 runs 10 times, gen2 after gen1 runs 10 times.
</details>

<details>
<summary>✅ Answer</summary>

```python
import gc

print(gc.get_threshold())  # (700, 10, 10)
# Gen 0 collected when 700 new objects allocated since last gen0 run
# Gen 1 collected when gen0 has run 10 times
# Gen 2 collected when gen1 has run 10 times

print(gc.get_count())   # (n0, n1, n2) — allocations since last collection

gc.collect(0)   # scan gen 0 only — cheapest
gc.collect(1)   # scan gen 0 + 1
gc.collect(2)   # full scan all generations — most thorough

print(gc.get_count())   # resets after collect
```

**Why:** Generational GC is an optimization. Most objects die young (gen 0). Scanning long-lived gen 2 objects rarely keeps overhead low.
</details>

---

### Q9 · gc.get_count() and generations — reading GC state 🟡

Read and interpret `gc.get_count()` before and after creating 1000 objects and then deleting them. What do the three numbers mean?

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

<details>
<summary>💡 Hint</summary>
The three numbers are (gen0_allocations, gen1_allocations, gen2_allocations) since the last collection at each level.
</details>

<details>
<summary>✅ Answer</summary>

```python
import gc

gc.collect()
print("Before:", gc.get_count())   # (low_n, low_n, low_n)

objects = [object() for _ in range(1000)]
print("After creating 1000:", gc.get_count())  # gen0 count increased

del objects
gc.collect()
print("After del + collect:", gc.get_count())  # (0, 0, 0) or near

# Tuple meaning: (new_since_last_gen0, gen0_runs_since_gen1, gen1_runs_since_gen2)
```

**Why:** Gen 0 count climbs with every allocation. When it hits the threshold (700 by default), gen 0 is scanned. Surviving objects promote to gen 1, incrementing that counter.
</details>

---

### Q10 · generators vs lists — memory comparison 🟡

Compare the memory used by a list comprehension versus a generator expression for 1,000,000 squared values. Use `sys.getsizeof()`. What is the ratio?

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

<details>
<summary>💡 Hint</summary>
The generator object is ~112 bytes regardless of how many items it will produce.
</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

n = 1_000_000
list_size = sys.getsizeof([x * x for x in range(n)])
gen_size  = sys.getsizeof((x * x for x in range(n)))

print(f"List:      {list_size / 1024 / 1024:.1f} MB")   # ~8 MB
print(f"Generator: {gen_size} bytes")                    # ~112 bytes
print(f"Ratio:     {list_size // gen_size:,}x")          # ~70,000x
```

**Why:** A list allocates all N items at once. A generator holds only the recipe for producing one item at a time — constant memory regardless of N. For pipelines processing millions of records, this is the difference between running and crashing.
</details>

---

### Q11 · generator pipeline — O(1) memory chain 🟡

Write a three-stage generator pipeline: `read_records()` → `filter_active()` → `enrich()`. Each stage is a generator. Show that no intermediate lists are created and memory stays O(1) regardless of record count.

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Each stage yields one item at a time. The previous stage is only advanced when the next stage asks for an item.
</details>

<details>
<summary>✅ Answer</summary>

```python
def read_records():
    for i in range(100):
        yield {"id": i, "value": i * 10,
               "status": "active" if i % 2 == 0 else "inactive"}

def filter_active(records):
    for record in records:
        if record["status"] == "active":
            yield record

def enrich(records):
    for record in records:
        record["doubled"] = record["value"] * 2
        yield record

# O(1) memory — one item in flight at any time
pipeline = enrich(filter_active(read_records()))
result = list(pipeline)   # only materialize at the very end
print(f"Processed {len(result)} active records")
print(result[0])   # {"id": 0, "value": 0, "status": "active", "doubled": 0}
```

**Why:** Each `yield` suspends the generator until the consumer asks for the next item. The whole chain processes one record at a time — no intermediate lists exist in memory. Data pipeline crash fix: use this pattern instead of loading the full dataset.
</details>

---

### Q12 · __slots__ — add to a class and explain savings 🟡

Convert a `RegularUser` class (4 attributes: user_id, name, email, age) to use `__slots__`. Verify that:
1. The slotted version has no `__dict__`
2. You cannot add arbitrary attributes to it
3. Use `sys.getsizeof()` to compare sizes

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Normal classes carry a `__dict__` per instance — typically 200–400 bytes overhead. `__slots__` removes it.
</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

class RegularUser:
    def __init__(self, user_id, name, email, age):
        self.user_id = user_id; self.name = name
        self.email = email; self.age = age

class SlottedUser:
    __slots__ = ['user_id', 'name', 'email', 'age']
    def __init__(self, user_id, name, email, age):
        self.user_id = user_id; self.name = name
        self.email = email; self.age = age

r = RegularUser(1, "Alice", "a@x.com", 30)
s = SlottedUser(1, "Alice", "a@x.com", 30)

print(sys.getsizeof(r) + sys.getsizeof(r.__dict__))  # ~360B
print(sys.getsizeof(s))                               # ~120B

try:
    s.extra = "nope"
except AttributeError as e:
    print(e)   # 'SlottedUser' object has no attribute 'extra'
```

**Why:** `__slots__` replaces the per-instance `__dict__` hash table with fixed pre-allocated slots — typically 40–60% memory savings. Critical when creating millions of instances (embeddings, user objects, sensor readings).
</details>

---

### Q13 · __slots__ vs __dict__ — measure the difference 🟡

Create 100,000 instances of both `RegularUser` and `SlottedUser` using `tracemalloc`. Print total MB used by each. What is the real-world savings?

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Use `tracemalloc.start()`, create the list, take snapshot, delete, repeat for the other class.
</details>

<details>
<summary>✅ Answer</summary>

```python
import tracemalloc, gc

# (Using RegularUser and SlottedUser from Q12)

tracemalloc.start()
regular_list = [RegularUser(i, f"U{i}", f"u{i}@x.com", 25) for i in range(100_000)]
s1 = tracemalloc.take_snapshot()
del regular_list; gc.collect()

slotted_list = [SlottedUser(i, f"U{i}", f"u{i}@x.com", 25) for i in range(100_000)]
s2 = tracemalloc.take_snapshot()
del slotted_list; gc.collect()
tracemalloc.stop()

reg_mb = sum(s.size for s in s1.statistics("lineno")) / 1024 / 1024
slt_mb = sum(s.size for s in s2.statistics("lineno")) / 1024 / 1024
print(f"Regular: ~{reg_mb:.1f} MB")   # ~40 MB
print(f"Slotted: ~{slt_mb:.1f} MB")   # ~16 MB  (~60% savings)
```

**Why:** At 100k instances, the difference is tens of megabytes. At millions of instances (common in ML preprocessing or data pipelines), this is the difference between fitting in RAM or not.
</details>

---

### Q14 · weakref.ref() — reference without holding the object alive 🟡

Create an object. Create a `weakref.ref()` to it. Access it through the weak reference while the object is alive. Then delete the original — show the weak reference returns `None`.

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)

<details>
<summary>💡 Hint</summary>
A weak reference does NOT increment the reference count. When the last strong reference is deleted, the object is collected and the weak ref returns `None`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import weakref

class HeavyDocument:
    def __init__(self, doc_id):
        self.doc_id = doc_id
        self.data = list(range(1000))
    def __del__(self):
        print(f"[DELETED] Document {self.doc_id}")

doc = HeavyDocument(42)
weak = weakref.ref(doc)   # does NOT increment ref count

print(weak())          # <HeavyDocument object> — alive
print(weak().doc_id)   # 42

del doc                # refcount → 0 → [DELETED] Document 42
print(weak())          # None — object is gone
```

**Why:** Weak references let you "peek" at an object without keeping it alive. The key use case is caches: you want to reuse the object if it's still in memory, but you don't want the cache to prevent garbage collection.
</details>

---

### Q15 · WeakValueDictionary — self-cleaning cache 🟡

Build a simple document cache using `weakref.WeakValueDictionary`. Store two documents. Delete one. Show the cache shrinks automatically without any manual cleanup code.

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`WeakValueDictionary` automatically removes entries when the value object is garbage collected.
</details>

<details>
<summary>✅ Answer</summary>

```python
import weakref

class HeavyDocument:
    def __init__(self, doc_id):
        self.doc_id = doc_id

cache = weakref.WeakValueDictionary()

doc1 = HeavyDocument(1)
doc2 = HeavyDocument(2)
cache[1] = doc1
cache[2] = doc2

print(f"Cache size: {len(cache)}")       # 2

del doc1   # refcount → 0 → auto-removed from cache
print(f"After del doc1: {len(cache)}")   # 1 — cleaned automatically

print(cache.get(1))   # None — entry gone
print(cache[2].doc_id)  # 2 — still alive
```

**Why:** In web servers and caching systems, a `WeakValueDictionary` prevents the cache from being the reason objects live forever. It acts like a cache that says: "I'll hold onto this as long as someone else cares about it too."
</details>

---

### Q16 · local vs global lifetime — variable scope and memory 🟢

Explain the lifetime of local, global, and built-in variables using this table as a guide. Write code that demonstrates a local variable disappearing after a function returns.

```
Scope      | Lifetime
-----------|----------------------------------
Local      | Destroyed when function returns
Global     | Lives for entire program run
Built-in   | Lives for entire interpreter session
```

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Use `locals()` inside and outside a function to see what variables are in scope.
</details>

<details>
<summary>✅ Answer</summary>

```python
CONFIG = {"debug": True}    # global — lives in module.__dict__ on heap

def process():
    temp = [1, 2, 3]        # local — lives only in this stack frame
    print(f"Inside: temp exists = {'temp' in locals()}")   # True
    return sum(temp)
    # temp is destroyed when function returns — frame gone

result = process()
print(f"Outside: result = {result}")   # 6
# temp is gone — no way to access it outside process()
# CONFIG persists as long as the module is loaded
```

**Why:** Local variables have minimal lifetime — perfect for temporary work. Globals are in `module.__dict__` on the heap and persist for the program's lifetime. Large globals are a memory concern precisely because they never get freed.
</details>

---

### Q17 · closure cell on heap — why enclosing variables survive 🟠

Write a `make_counter()` function that returns an `increment()` closure. After `make_counter()` returns, its local variable `count` should normally be destroyed — but it isn't. Explain why, using `__closure__` to inspect it.

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Python promotes captured variables to a "cell object" on the heap, held alive by the inner function's `__closure__` attribute.
</details>

<details>
<summary>✅ Answer</summary>

```python
def make_counter():
    count = 0    # would normally die with make_counter's frame

    def increment():
        nonlocal count
        count += 1
        return count

    return increment

c = make_counter()
# make_counter's frame is DESTROYED — but count lives on!

print(c.__closure__)                         # (<cell at 0x...>,)
print(c.__closure__[0].cell_contents)        # 0  — count is here, on heap

print(c())   # 1
print(c.__closure__[0].cell_contents)        # 1  — updated in place
print(c())   # 2
```

**Why:** Python detects that `count` is referenced by the inner function and promotes it from a stack variable to a "cell object" on the heap. The inner function's `__closure__` holds a reference to that cell, keeping it alive even after `make_counter()` returns. This is exactly why closures work.
</details>

---

### Q18 · nonlocal — mutating an enclosing variable 🟡

Write a function that uses `nonlocal` to modify a variable in the enclosing scope. Show what happens WITHOUT `nonlocal` (gets UnboundLocalError) and then fix it with `nonlocal`.

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Python treats any assigned-to name as local to that function unless told otherwise. Reading is fine; writing requires `nonlocal`.
</details>

<details>
<summary>✅ Answer</summary>

```python
def make_accumulator():
    total = 0

    def add(n):
        # Without nonlocal:
        # total += n  → UnboundLocalError: Python sees 'total =' and makes it local
        nonlocal total   # tell Python: use the cell object from make_accumulator
        total += n
        return total

    return add

acc = make_accumulator()
print(acc(10))  # 10
print(acc(5))   # 15
print(acc(3))   # 18
```

**Why:** `nonlocal` tells Python that `total` lives in the enclosing cell object (on the heap) rather than being a new local variable. Without it, any assignment to `total` inside `add` creates a fresh local variable, and reading it before assigning raises `UnboundLocalError`.
</details>

---

### Q19 · tracemalloc snapshot — before/after comparison 🟠

Write code that:
1. Starts `tracemalloc`
2. Takes a baseline snapshot
3. Simulates a memory leak (stores 2,000 dicts in a global list)
4. Takes a second snapshot
5. Prints the top 3 lines that allocated the most memory

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Use `snapshot_after.compare_to(baseline, "lineno")` to get a diff sorted by allocation size.
</details>

<details>
<summary>✅ Answer</summary>

```python
import tracemalloc, gc

tracemalloc.start()
baseline = tracemalloc.take_snapshot()

# Simulate leak: storing objects globally without cleanup
leaky_cache = []
for i in range(2_000):
    leaky_cache.append({"id": i, "data": list(range(50))})

after_leak = tracemalloc.take_snapshot()
diff = after_leak.compare_to(baseline, "lineno")

print("Top 3 memory growth lines:")
for stat in diff[:3]:
    print(f"  {stat}")

tracemalloc.stop()

# Fix: clean up
del leaky_cache
gc.collect()
```

**Why:** `tracemalloc` records the file and line number of every allocation. The `compare_to()` diff shows exactly which lines grew the most memory between snapshots — the production standard tool for diagnosing leaks.
</details>

---

### Q20 · sys.getsizeof() — measuring object sizes 🟢

Measure and compare the sizes of: `None`, `True`, `0`, `"a"`, `[]`, `[1]`, `{}`, `set()`. Then explain the key gotcha with `sys.getsizeof()` and nested objects.

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`sys.getsizeof()` only measures the container itself — not the objects inside it.
</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

objects = [None, True, 0, "a", [], [1], {}, set()]
for obj in objects:
    print(f"  {repr(obj):20s}  {sys.getsizeof(obj)} bytes")

# None     16 bytes | []      56 bytes
# True     28 bytes | [1]     64 bytes
# 0        24 bytes | {}      64 bytes
# "a"      50 bytes | set()  216 bytes

# GOTCHA: getsizeof does NOT count nested objects
nested = [[1, 2, 3], [4, 5, 6]]
print(sys.getsizeof(nested))         # ~72 bytes — just the list wrapper
# Does NOT include the inner [1,2,3] or [4,5,6] objects
```

**Why:** `sys.getsizeof()` is a shallow measurement — it counts only the object's own memory, not what it references. For a true deep size, you need `tracemalloc` or a recursive `total_size()` function.
</details>

---

### Q21 · memory_profiler @profile — line-by-line memory 🟡

Describe how to use `memory_profiler`'s `@profile` decorator. Write a function that allocates and frees a large list, and explain what the output would show.

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Run with `python -m memory_profiler script.py` — it shows memory usage line by line in MiB increments.
</details>

<details>
<summary>✅ Answer</summary>

```python
# Install: pip install memory-profiler
# Run with: python -m memory_profiler this_script.py

from memory_profiler import profile

@profile
def allocate_and_free():
    # Line-by-line memory tracking
    big = list(range(1_000_000))   # ~8 MB allocated here
    total = sum(big)
    del big                         # memory released here
    return total

allocate_and_free()

# Output looks like:
# Line    Mem usage    Increment   Line Contents
# 7       50.0 MiB    +0.0 MiB    big = list(range(1_000_000))
# 8       57.6 MiB    +7.6 MiB    total = sum(big)
# 9       57.6 MiB    +0.0 MiB    del big
# 10      50.0 MiB    -7.6 MiB    return total
```

**Why:** `@profile` shows exactly which line caused memory to grow or shrink. Use it when `tracemalloc` confirms a leak but you need per-line attribution in a specific function.
</details>

---

### Q22 · avoid large globals — prefer local scope 🟡

Demonstrate why a large global variable is a memory problem. Then show the fix: scope the data locally and release it when done.

Also show the performance tip: caching a global function reference in a local variable for tight loops.

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Globals live in `module.__dict__` on the heap for the entire program lifetime — they are never freed unless explicitly deleted.
</details>

<details>
<summary>✅ Answer</summary>

```python
import math

# BAD: global holds large data forever
LARGE_DATASET = list(range(1_000_000))   # 8 MB, lives forever

# GOOD: local scope — freed when function returns
def process():
    data = list(range(1_000_000))
    result = sum(data)
    return result   # data freed when function exits

# PERFORMANCE TIP: cache global lookups locally
# Slower: `math` looked up in globals dict every iteration
for i in range(1_000_000):
    result = math.sqrt(i)   # globals → math.__dict__ → sqrt (2 dict lookups)

# Faster: one lookup, then local frame access
sqrt = math.sqrt
for i in range(1_000_000):
    result = sqrt(i)   # local frame lookup — ~200x faster on cache miss
```

**Why:** Globals persist for the program's lifetime. Keeping large datasets in global scope is a memory leak by design. Local variables get freed when the function returns. The local caching trick also exploits that local variable lookup is faster than two chained global dict lookups.
</details>

---

### Q23 · chunked processing — bounded memory over large data 🟠

Write a `chunked(iterable, size)` generator that yields successive fixed-size chunks. Use it to process 1,000,000 items in batches of 10,000. Prove that at most 10,000 items are in memory at any time.

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Release the previous chunk before yielding the next — Python's GC will reclaim it between iterations.
</details>

<details>
<summary>✅ Answer</summary>

```python
import gc

def chunked(iterable, size):
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []   # release — allows GC to reclaim previous chunk
    if chunk:
        yield chunk      # remainder

total = 0
chunk_count = 0
for chunk in chunked(range(1_000_000), 10_000):
    total += sum(chunk)
    chunk_count += 1

print(f"Processed {chunk_count} chunks, total = {total:,}")
# Peak memory: always <= 10,000 items, never 1,000,000

# Real-world: database batch inserts
def batch_insert(records, batch_size=1000):
    for batch in chunked(records, batch_size):
        pass  # db.bulk_insert(batch)
```

**Why:** Data pipeline crash fix — loading an entire dataset into memory causes OOM on large files. Chunked processing keeps memory bounded at O(chunk_size) regardless of how large the total data is. Standard pattern for DB batch inserts, ML dataset loading, CSV processing.
</details>

---

### Q24 · del + gc.collect() — explicit cleanup between heavy phases 🟡

Write a multi-phase processing function. After each phase, explicitly `del` the work data and call `gc.collect()`. Explain when this pattern matters versus when Python handles it automatically.

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Python's automatic GC runs on a schedule. When you're about to allocate another large block, explicitly clearing first ensures memory is available.
</details>

<details>
<summary>✅ Answer</summary>

```python
import gc

def process_phase(name, data_size):
    print(f"[{name}] allocating {data_size:,} items...")
    work_data = list(range(data_size))   # ~4 MB per 500k ints
    result = sum(work_data)

    # Explicit cleanup before returning
    del work_data
    gc.collect()   # force immediate reclaim
    print(f"[{name}] done, memory released")
    return result

# Each phase runs with bounded memory — no accumulation
r1 = process_phase("Phase 1", 500_000)
r2 = process_phase("Phase 2", 500_000)
r3 = process_phase("Phase 3", 500_000)
print(f"Total: {r1 + r2 + r3:,}")

# When this matters: total data > 50% RAM, or multiple large allocations in sequence
# When Python handles it: small objects, short-lived functions, normal scripts
```

**Why:** Python's GC runs asynchronously on thresholds. In memory-intensive scripts (ML training, large ETL jobs), explicitly releasing before the next large allocation guarantees memory is available instead of relying on GC timing.
</details>

---

### Q25 · capstone — diagnose and fix a memory leak scenario 🟠

A web server accumulates memory over time. Here is a simplified version:

```python
request_log = []

def handle_request(data):
    request_log.append({"data": data, "processed": list(range(10_000))})
    return "ok"

# Simulating 1000 requests
for i in range(1000):
    handle_request(f"request_{i}")
```

Identify all memory problems. Rewrite `handle_request` and the surrounding code to fix them. Use `tracemalloc` to verify the fix works.

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Count how many problems exist: (1) global growing forever, (2) large objects per entry, (3) no cleanup. Fix each one.
</details>

<details>
<summary>✅ Answer</summary>

```python
import tracemalloc, gc, weakref

# PROBLEMS IN ORIGINAL:
# 1. `request_log` is a global — lives forever
# 2. Each entry stores `list(range(10_000))` — 10k ints per request
# 3. After 1000 requests: 10,000,000 integers in memory, never freed

# --- DIAGNOSIS ---
tracemalloc.start()
baseline = tracemalloc.take_snapshot()

request_log = []
for i in range(1000):
    request_log.append({"data": f"request_{i}", "processed": list(range(10_000))})

after = tracemalloc.take_snapshot()
diff = after.compare_to(baseline, "lineno")
print("Leak identified:", diff[0])   # points at the append line
tracemalloc.stop()

# --- FIX 1: don't store large computed data, only metadata ---
request_log_fixed = []

def handle_request_fixed(data):
    # Process locally — result is all we need, not the intermediate list
    result = sum(range(10_000))           # no list stored
    request_log_fixed.append({"data": data, "result": result})  # tiny
    return "ok"

# --- FIX 2: bounded log with cap ---
from collections import deque
MAX_LOG = 100
request_log_bounded = deque(maxlen=MAX_LOG)   # auto-drops oldest entries

def handle_request_bounded(data):
    result = sum(range(10_000))
    request_log_bounded.append({"data": data, "result": result})
    return "ok"

for i in range(1000):
    handle_request_bounded(f"request_{i}")

print(f"Bounded log size: {len(request_log_bounded)}")  # 100, not 1000
gc.collect()
```

**Why:** Three compounding problems — a growing global, large objects per entry, and no eviction. Fix 1 avoids storing computed intermediate data. Fix 2 caps the log with a `deque(maxlen=N)` — the idiomatic Python solution for bounded history. Real web server fix: use weak references or bounded caches, never unbounded globals.
</details>

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)
