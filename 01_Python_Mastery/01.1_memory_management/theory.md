<a id="top"></a>
# 🧠 Memory Management in Python

From Reference Counting to Garbage Collection Internals

> 📝 **Practice:** [Q80 · explain-memory](../python_practice_questions_100.md#q80--interview--explain-memory)

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. Stack and Heap — Where Python Stores Things](#1-stack-and-heap)
  - [Stack — The Whiteboard](#stack-the-whiteboard)
  - [Heap — The Drawer](#heap-the-drawer)
  - [Why Two Areas?](#why-two-areas)
  - [The Three Memory Regions](#three-memory-regions)
  - [Stack Frame — What Happens on Each Call](#stack-frame)
  - [Variable Lifetime by Scope](#variable-lifetime-by-scope)
  - [Enclosing Scope — The Closure Cell on the Heap](#enclosing-scope)
  - [Global Variables — NOT on the Stack](#global-variables)
  - [Stack is Faster Than Heap](#stack-vs-heap-speed)
- [2. Objects and References](#2-objects-and-references)
  - [What Is a Python Object?](#what-is-a-python-object)
  - [Variables Are References, Not Values](#variables-are-references)
  - [Object Identity — id() and is vs ==](#object-identity)
  - [Mutable vs Immutable Objects](#mutable-vs-immutable)
  - [Reference Counting](#reference-counting)
  - [How to Check Reference Count](#how-to-check-reference-count)
  - [Circular References](#circular-references)
  - [__del__ Method (Destructor)](#del-method-destructor)
  - [Object Interning](#object-interning)
- [3. Garbage Collector (GC)](#3-garbage-collector-gc)
  - [How Garbage Collection Works](#how-garbage-collection-works)
  - [GC Control Methods](#gc-control-methods)
- [4. Memory Optimization Techniques](#4-memory-optimization-techniques)
  - [Memory Leaks in Python](#memory-leaks)
  - [Use Generators Instead of Lists](#use-generators)
  - [Use __slots__ in Classes](#use-slots)
  - [Avoid Large Global Variables](#avoid-large-globals)
  - [Use Weak References](#use-weak-references)
  - [Memory Profiling Tools](#memory-profiling-tools)
  - [Common Memory Mistakes](#common-memory-mistakes)
- [5. Real Production Scenarios](#5-real-production-scenarios)
  - [Web Server Memory Growth](#web-server-memory-growth)
  - [Data Pipeline Crash](#data-pipeline-crash)
- [Final Mental Model](#final-mental-model)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
Stack vs heap · Reference counting · Garbage collection (cyclic GC) · Object identity (`id()`) · `is` vs `==`

**Should Learn** — Important for real projects, comes up regularly:
`__slots__` memory optimization · Generators vs lists (memory) · `sys.getsizeof()` · `weakref` · Mutable vs immutable

**Good to Know** — Useful in specific situations:
Memory layout (arenas → pools → blocks) · Small integer caching internals · `tracemalloc`

**Reference** — Know it exists, look up when needed:
`weakref` callbacks · `gc` module API · Frame introspection

<a id="1-stack-and-heap"></a>
# 1. Stack and Heap — Where Python Stores Things

Imagine you are sitting at a desk doing homework.

Your desk has two areas:

**Your whiteboard** — you scribble things here while you work. Quick notes, current calculations, temporary reminders. When you finish a task, you wipe it clean. It is fast to write on, but temporary.

**Your drawer** — this is where you store the actual documents, books, and papers. Things that need to stick around longer. It takes slightly more effort to find something in there, but it holds much more.

Python works the same way:

```
WHITEBOARD (Stack)     DRAWER (Heap)
──────────────────     ─────────────────
Holds variable names   Holds the actual values
Fast access            Stores everything
Cleared often          Kept until no longer needed
```

<a id="stack-the-whiteboard"></a>
## Stack — The Whiteboard

The **stack** holds the **names** of your variables — the labels that point to your data.

When you write:

```python
name = "Alice"
age  = 25
city = "London"
```

Python puts the labels `name`, `age`, and `city` on the stack (the whiteboard).

The stack is:
- **Fast** — looking up a label is instant
- **Organised** — each label points to where the real data lives
- **Temporary** — when labels are no longer needed, they are cleaned up

<a id="heap-the-drawer"></a>
## Heap — The Drawer

The **heap** is where the actual **values** live — the real data.

When you write `name = "Alice"`:
- The text `"Alice"` is stored in the heap (the drawer)
- The label `name` on the stack points to it

```
STACK (labels)          HEAP (actual values)
──────────────          ──────────────────────
name ──────────────────► "Alice"
age  ──────────────────► 25
city ──────────────────► "London"
```

The stack holds the arrows (labels).
The heap holds the boxes (values).

<a id="why-two-areas"></a>
## Why Two Areas?

The same value can have many labels pointing to it:

```python
a = "Alice"
b = a          # b points to the same "Alice" — not a copy
```

```
STACK          HEAP
──────         ──────────────
a ─────────►  "Alice"  ← stored ONCE
b ─────────►  (same object, ref_count = 2)
```

Two areas means: store once in the heap, point from as many labels as needed. No wasted copies.

Almost all objects live in heap.

> 📝 **Practice:** [Q1–Q3 — stack vs heap, frame lifecycle, heap allocation](./practice.md#q1)

<a id="three-memory-regions"></a>
## The Three Memory Regions

```
┌─────────────────────────────────────────────────┐
│                 STACK                           │
│  - function call frames (per function call)     │
│  - local variable name → reference pairs        │
│  - fast (CPU L1 cache-friendly)                 │
│  - automatically cleaned when function returns  │
├─────────────────────────────────────────────────┤
│                 HEAP                            │
│  - ALL Python objects (int, list, dict, func)   │
│  - managed by reference count + GC              │
│  - survives across function calls               │
│  - slower (RAM access on cache miss)            │
├─────────────────────────────────────────────────┤
│              DATA SEGMENT                       │
│  - module-level globals (__dict__ on heap)      │
│  - lives for entire program lifetime            │
└─────────────────────────────────────────────────┘
```

<a id="stack-frame"></a>
## Stack Frame — What Happens on Each Call

When Python calls a function, it pushes a stack frame.
When the function returns, that frame is destroyed.

```python
def greet(name):
    msg = "Hello, " + name
    return msg

result = greet("Alice")
```

```
DURING greet("Alice"):

STACK (top)
┌──────────────────────────────────────────┐
│  greet() frame                           │
│    name → ──────────────────────────────── ─→ "Alice"  (heap)
│    msg  → ──────────────────────────────── ─→ "Hello, Alice" (heap)
├──────────────────────────────────────────┤
│  global frame (paused)                   │
│    greet  → ─→  function object (heap)   │
│    result → ???                          │
└──────────────────────────────────────────┘

AFTER return:

STACK
┌──────────────────────────────────────────┐
│  global frame                            │
│    result → ─→ "Hello, Alice" (heap)     │
└──────────────────────────────────────────┘
  greet() frame DESTROYED
  name and msg references gone
  heap objects survive if ref_count > 0
```

Key insight: Variable names live in the frame. Objects always live in the heap.

<a id="variable-lifetime-by-scope"></a>
## Variable Lifetime by Scope

```
┌─────────────────────────────────────────────────────────────────────┐
│  Scope     │  Where it lives           │  Lifetime                  │
├────────────┼───────────────────────────┼────────────────────────────┤
│  Local     │  Current stack frame      │  Destroyed when function   │
│            │                           │  returns                   │
├────────────┼───────────────────────────┼────────────────────────────┤
│  Enclosing │  Heap (cell object)       │  Survives — kept alive by  │
│            │  pointed to by            │  closure's __closure__     │
│            │  __closure__ attribute    │  attribute                 │
├────────────┼───────────────────────────┼────────────────────────────┤
│  Global    │  Module __dict__ (heap)   │  Lives for entire program  │
│            │                           │  run                       │
├────────────┼───────────────────────────┼────────────────────────────┤
│  Built-in  │  builtins module (heap)   │  Lives for entire          │
│            │                           │  interpreter session       │
└─────────────────────────────────────────────────────────────────────┘
```

> 📝 **Practice:** [Q16–Q18 — local vs global lifetime, closure cell, nonlocal](./practice.md#q16)

<a id="enclosing-scope"></a>
## Enclosing Scope — The Closure Cell on the Heap

Normal rule: local variable → dies when function returns.
Closure exception: if an inner function captures it, Python promotes it to a **cell object** on the heap.

```python
def make_counter():
    count = 0       # normally would die with make_counter()

    def increment():
        nonlocal count
        count += 1
        return count

    return increment
```

```
AFTER make_counter() returns:

Stack: make_counter() frame DESTROYED

Heap:
  ┌──────────────────────────────┐
  │  Cell object                 │
  │    cell_contents: 0          │  ← count lives here, not on stack
  └──────────────────────────────┘
          ↑
  ┌──────────────────────────────┐
  │  Function object: increment  │
  │    __closure__: (cell,)      │  ← holds the cell alive
  └──────────────────────────────┘
```

Inspect it:

```python
c = make_counter()
print(c.__closure__[0].cell_contents)   # 0
c()
print(c.__closure__[0].cell_contents)   # 1
```

<a id="global-variables"></a>
## Global Variables — NOT on the Stack

Common misconception: globals are stored somewhere "global" and special.

Reality: globals live in the module's `__dict__` object — which is on the heap.

```python
config = {"debug": True}   # heap → module.__dict__["config"]
MAX_RETRIES = 3             # heap → module.__dict__["MAX_RETRIES"]
```

They persist for the entire program lifetime.
This is why large globals are a memory concern.

<a id="stack-vs-heap-speed"></a>
## Stack is Faster Than Heap

```
Local variable access:   ~0.5 ns    (CPU register / L1 cache)
Heap object access:      ~100 ns    (RAM lookup on cache miss)
                         200× slower
```

Practical tip:

```python
# Slower: repeated global dict lookup
for i in range(1_000_000):
    result = math.sqrt(i)   # looks up 'math' in globals → then 'sqrt' in its __dict__

# Faster: cache lookup in local variable
sqrt = math.sqrt            # one heap lookup, stored locally
for i in range(1_000_000):
    result = sqrt(i)        # local frame lookup → fast
```

> [↑ Back to Top](#top)

<a id="2-objects-and-references"></a>
# 2. Objects and References

In Python, **everything is an object** — integers, strings, functions, classes, even `None`.

Every object lives on the heap and has three things:

```
┌──────────────────────────────────────┐
│  Python Object (on the heap)         │
│                                      │
│  type      → what kind of object     │
│  value     → the actual data         │
│  ref_count → how many labels point   │
│              to this object          │
└──────────────────────────────────────┘
```

A **variable** is just a name (label) in a namespace — it points to an object, it does not contain the value itself.

<a id="what-is-a-python-object"></a>
## What Is a Python Object?

```python
x = 42
```

This creates:
1. An `int` object on the heap with value `42`
2. A name `x` in the current namespace pointing to that object

```python
# Every common value is an object:
type(42)          # <class 'int'>
type("hello")     # <class 'str'>
type([1, 2, 3])   # <class 'list'>
type(len)         # <class 'builtin_function_or_method'>
type(None)        # <class 'NoneType'>
```

Even functions, classes, and modules are objects on the heap.

<a id="variables-are-references"></a>
## Variables Are References, Not Values

```python
x = 10
y = x       # y does NOT copy the value — it points to the same object
```

```
STACK              HEAP
─────              ──────────────────────────
x ────────────►   ┌─────────────────────┐
                  │  int object: 10     │
y ──────────��─►   │  ref_count = 2      │
                  │  id = 0x7f3d2b4c    │
                  └─────────────────────┘
```

Both `x` and `y` point to the **same** object. There is only one `10` in memory.

```python
print(x is y)   # True  — same object in memory
print(id(x))    # e.g. 140732...
print(id(y))    # same number — same address on the heap
```

> 📝 **Practice:** [Q4–Q6 — sys.getrefcount(), increment/decrement, object freed](./practice.md#q4)

<a id="object-identity"></a>
## Object Identity — id() and is vs ==

```
id(obj)    → memory address of the object (unique identifier)
x is y     → True if x and y point to the SAME object (same id)
x == y     → True if x and y have the SAME VALUE (can be different objects)
```

```python
a = [1, 2, 3]
b = [1, 2, 3]   # same values, different objects

print(a == b)    # True  — same values
print(a is b)    # False — different objects in memory
print(id(a))     # e.g. 140512...
print(id(b))     # different address

c = a            # c points to same object as a
print(a is c)    # True — same object
```

```
a ──►  [ list: [1,2,3]  id=0xAAA ]
b ──►  [ list: [1,2,3]  id=0xBBB ]   ← different objects, same value
c ──►  [ list: [1,2,3]  id=0xAAA ]   ← same object as a
```

**Common mistake:** Using `is` to compare values — works for small interned objects but breaks in general. Always use `==` for value comparison.

<a id="mutable-vs-immutable"></a>
## Mutable vs Immutable Objects

```
Immutable — value cannot change after creation:
  int, float, bool, str, tuple, frozenset, bytes

Mutable — value can change in-place:
  list, dict, set, bytearray, custom classes (usually)
```

Why this matters for references:

```python
# Immutable — reassignment creates a NEW object:
x = 10
x = 20    # x now points to a NEW int(20) — the old int(10) may be freed

# Mutable — in-place change affects ALL references:
a = [1, 2, 3]
b = a             # both point to same list
b.append(4)
print(a)          # [1, 2, 3, 4] ← a changed! same object was modified
```

```
After b.append(4):

a ──►  [ list: [1,2,3,4] ]  ← mutated in-place
b ──►  (same object)
```

**Common mistake:** Passing a list to a function and being surprised that the original changed — the function received a reference to the same object.

<a id="reference-counting"></a>
## Reference Counting

Every Python object has a hidden **ref_count** — a counter tracking how many variables (or containers) point to it.

```
Assign variable      →  ref_count += 1
Add to container     →  ref_count += 1
Reassign / del       →  ref_count -= 1
ref_count reaches 0  →  object freed immediately (no GC needed)
```

```
ref_count lifecycle:

  x = [1, 2, 3]          ref_count = 1
        │
  y = x                   ref_count = 2
        │
  del x                   ref_count = 1
        │
  del y                   ref_count = 0  →  freed immediately
```

> 📝 **Practice:** [Q57 · reference-counting](../python_practice_questions_100.md#q57--thinking--reference-counting)

<a id="how-to-check-reference-count"></a>
## How to Check Reference Count

```python
import sys
sys.getrefcount(obj)   # returns ref_count + 1 (the call itself holds a temp ref)

# Example:
x = []
print(sys.getrefcount(x))   # 2 — one for x, one for getrefcount's argument
y = x
print(sys.getrefcount(x))   # 3 — x, y, and getrefcount's argument
```

Used for debugging and understanding object lifetimes.

<a id="circular-references"></a>
## Circular References

Reference counting fails when objects reference each other in a cycle:

```python
a = []
b = []
a.append(b)   # a holds reference to b
b.append(a)   # b holds reference to a
```

```
  a ──────────────► [ list A ]
                        │
                        ▼
  b ──────────────► [ list B ]
                        │
                        └──────────────► [ list A ]  ← cycle!
```

```python
del a   # ref_count[A] = 1  (B still refs A)
del b   # ref_count[B] = 1  (A still refs B)
```

Neither object reaches ref_count = 0. Neither is freed. **Memory leaked.**

This is the case where ref counting alone fails — the cyclic GC (section 3) handles it.

<a id="del-method-destructor"></a>
## __del__ Method (Destructor)

`__del__` runs when an object's ref_count reaches zero — just before it is freed.

```python
class Connection:
    def __del__(self):
        print("Connection closed")

conn = Connection()
del conn   # prints "Connection closed"
```

Be careful: if objects with `__del__` form a cycle, the GC may not be able to collect them — `__del__` complicates cycle-breaking. Avoid heavy logic inside `__del__`.

<a id="object-interning"></a>
## Object Interning

Small integers (-5 to 256) and short strings are **interned** — Python reuses the same object instead of creating a new one.

```python
a = 5
b = 5
print(a is b)   # True — same object (interned)

a = 1000
b = 1000
print(a is b)   # False — large ints NOT interned, two separate objects
```

```
Interned (small int):
  a ──►  [ int: 5, ref_count = 2 ]  ◄── b     ← ONE object, two labels

Not interned (large int):
  a ──►  [ int: 1000, ref_count = 1 ]
  b ──►  [ int: 1000, ref_count = 1 ]           ← TWO separate objects
```

> [↑ Back to Top](#top)

<a id="3-garbage-collector-gc"></a>
# 3. Garbage Collector (GC)

To solve the circular reference problem, Python has a garbage collector.

```python
import gc
```

The GC detects cycles — groups of objects that reference each other but are unreachable from any live variable — and frees them. It runs automatically in the background.

> 📝 **Practice:** [Q58 · gc-cycles](../python_practice_questions_100.md#q58--normal--gc-cycles)

<a id="how-garbage-collection-works"></a>
## How Garbage Collection Works

Python uses **generational garbage collection** — the idea that most objects die young.

```
Generation 0  (new objects — checked most often)
┌─────────────────────────────────────────────┐
│  obj1  obj2  obj3  obj4  ...                │  ← new allocations land here
└─────────────────────────────────────────────┘
         │  survived one GC pass
         ▼
Generation 1
┌─────────────────────────────────────────────┐
│  obj_a  obj_b  obj_c  ...                   │
└─────────────────────────────────────────────┘
         │  survived again
         ▼
Generation 2  (long-lived — checked rarely)
┌─────────────────────────────────────────────┐
│  module globals  class objects  long caches │
└────────────────────────────────────────────��┘
```

- New objects → Generation 0
- Survive a collection → promoted to Generation 1, then 2
- Older generations scanned less frequently → better performance
- GC only runs on objects that CAN form cycles (not integers, strings, etc.)

<a id="gc-control-methods"></a>
## GC Control Methods

```python
gc.collect()      # manually trigger GC — forces cycle detection
gc.get_count()    # (count0, count1, count2) — objects in each generation
gc.disable()      # disable automatic GC (use only if you manage memory manually)
gc.isenabled()    # check if GC is running
```

> 📝 **Practice:** [Q7–Q9 — circular references, gc.collect(), gc.get_count()](./practice.md#q7)

> [↑ Back to Top](#top)

<a id="4-memory-optimization-techniques"></a>
# 4. Memory Optimization Techniques

<a id="memory-leaks"></a>
## Memory Leaks in Python

Memory leaks happen when objects remain referenced unintentionally — their ref_count never reaches zero.

Common causes:

- **Circular references** with `__del__` — GC struggles to break cycles
- **Growing caches** with no eviction policy — dict keeps accumulating entries
- **Global variables** storing large data — they persist for the program lifetime
- **Event listeners / callbacks** holding references to objects that should be freed
- **C extensions** mismanaging memory

```python
# Classic growing cache leak:
_cache = {}

def process(key, value):
    _cache[key] = value   # never cleared — grows forever
```

Fix: use `weakref.WeakValueDictionary` or a bounded cache like `functools.lru_cache`.

<a id="use-generators"></a>
## Use Generators Instead of Lists

```python
# List: entire 1 million items in memory at once
big_list = [x for x in range(1_000_000)]   # ~8 MB

# Generator: produces one value at a time, ~200 bytes total
big_gen  = (x for x in range(1_000_000))   # ~200 bytes
```

```
List comprehension:
HEAP  ┌───────────────────────────────────────────────┐
      │  [0, 1, 2, 3, ..., 999999]   (~8 MB)          │
      └───────────────────────────────────────────────┘

Generator expression:
HEAP  ┌────────────────────┐
      │  generator object  │  (~200 bytes — yields one value at a time)
      └────────────────────┘
```

> 📝 **Practice:** [Q10–Q11 — generator vs list memory, yield-based pipeline](./practice.md#q10)

<a id="use-slots"></a>
## Use __slots__ in Classes

Normal class: each instance has a `__dict__` (a full dictionary for attributes) — heavy.

Using `__slots__`:

```python
class User:
    __slots__ = ['name', 'age']   # fixed attribute set — no __dict__
```

Prevents dynamic attribute creation.
Reduces per-instance memory by 40–60% for large numbers of instances.

> 📝 **Practice:** [Q59 · __slots__](../python_practice_questions_100.md#q59--design--__slots__) · [Q12–Q13 — add __slots__, measure savings](./practice.md#q12)

<a id="avoid-large-globals"></a>
## Avoid Large Global Variables

Global data persists for the entire program lifetime. Loading a large dataset into a global variable keeps it in memory even after you no longer need it.

Prefer:
- Local variables (freed when the function returns)
- Pass data as arguments
- Use `del` explicitly if you must use a global

> 📝 **Practice:** [Q22 — avoid large globals, cache lookups locally](./practice.md#q22)

<a id="use-weak-references"></a>
## Use Weak References

A **weak reference** points to an object without incrementing its ref_count.
The object can still be freed normally — the weak reference becomes `None` when that happens.

```python
import weakref

class Cache:
    pass

obj = Cache()
weak = weakref.ref(obj)   # does NOT increment ref_count

del obj                    # ref_count → 0, object freed
print(weak())              # None — the object is gone
```

Used in caching systems where you want to "suggest" an object is cached but not prevent it from being freed.

> 📝 **Practice:** [Q14–Q15 — weakref.ref(), WeakValueDictionary cache](./practice.md#q14)

<a id="memory-profiling-tools"></a>
## Memory Profiling Tools

Use these to find actual memory problems — don't optimize blindly.

```python
import tracemalloc

tracemalloc.start()
# ... your code ...
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:5]:
    print(stat)   # shows file, line, memory size
```

| Tool | What it shows |
|---|---|
| `tracemalloc` | Per-line memory allocation (built-in) |
| `sys.getsizeof(obj)` | Size of one object in bytes |
| `memory_profiler` | Line-by-line memory usage (`@profile`) |
| `objgraph` | Object count by type — find what's accumulating |

> 📝 **Practice:** [Q19–Q21 — tracemalloc snapshot, sys.getsizeof(), @profile decorator](./practice.md#q19)

<a id="common-memory-mistakes"></a>
## Common Memory Mistakes

❌ Loading entire file into a list — use a generator or chunked reading instead
❌ Storing large objects in global scope — they never get freed
❌ Building a cache dict with no size limit — use `lru_cache` or `weakref`
❌ Keeping references in long-lived lists/dicts you never clean up
❌ `__del__` on objects in cycles — prevents GC from collecting them
❌ Using `sys.getsizeof` on a container — it only counts the container, not its contents

> [↑ Back to Top](#top)

<a id="5-real-production-scenarios"></a>
# 5. Real Production Scenarios

<a id="web-server-memory-growth"></a>
## Web Server Memory Growth

Cause:

- Storing request data in a global dict that is never cleared
- Leaking references in middleware that holds request objects

Fix:

- Use `weakref.WeakValueDictionary` for request caches
- Add TTL-based eviction
- Profile with `tracemalloc` after load testing

<a id="data-pipeline-crash"></a>
## Data Pipeline Crash

Cause:

- Reading entire CSV/Parquet into a list
- Keeping all intermediate results in memory

Fix:

- Stream processing with generators
- Chunk-based loading (`pd.read_csv(chunksize=...)`)
- `del` intermediate results and call `gc.collect()` between stages

> 📝 **Practice:** [Q22–Q24 — avoid large globals, chunked processing, del + gc.collect()](./practice.md#q22)

> [↑ Back to Top](#top)

<a id="final-mental-model"></a>
# 🧠 Final Mental Model

Memory management in Python involves:

1. **Stack and heap** — variables are labels on the stack; objects live on the heap
2. **Objects and references** — every variable is a reference; assignment never copies
3. **Reference counting** — primary memory management; immediate deallocation at ref_count = 0
4. **Garbage collection** — catches cycles that ref counting misses; generational, runs in background
5. **Scope determines lifetime** — locals on stack (fast, temporary); globals on heap (persistent)
6. **Closures** — captured variables escape the stack via cell objects on the heap

Engineering progression:

- **Beginner** — does not think about memory
- **Intermediate** — understands reference counting, avoids obvious leaks
- **Advanced** — uses GC tools, profiles with tracemalloc
- **Senior** — designs memory-efficient architectures (generators, bounded caches, __slots__)

Understanding memory management improves performance, scalability, and reliability.

> [↑ Back to Top](#top)

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [01_python_fundamentals → theory.md](../01_python_fundamentals/theory.md) |
| ➡ Next Module | [02_control_flow → theory.md](../02_control_flow/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[01_python_fundamentals →](../01_python_fundamentals/theory.md) · [04_functions — closures →](../04_functions/theory.md#9-closures--functions-that-remember) · [11_generators_iterators →](../11_generators_iterators/theory.md)

**Jump to specific topics in other files:**
- Variable reference model → [01_python_fundamentals § Variables & Memory Model](../01_python_fundamentals/theory.md#5-variables-memory-model)
- Closures and cell objects → [04_functions § Closures](../04_functions/theory.md#9-closures--functions-that-remember)
- Generators vs list memory → [11_generators_iterators § Why Generators Are Lazy](../11_generators_iterators/theory.md#why-generators-are-lazy--the-memory-story)
- __slots__ reference → [05_oops/15_slots.md](../05_oops/15_slots.md)

**Practice:** [Q80 · explain-memory](../python_practice_questions_100.md#q80--interview--explain-memory) · [Q57 · reference-counting](../python_practice_questions_100.md#q57--thinking--reference-counting) · [Q85 · compare-deepcopy-pickle](../python_practice_questions_100.md#q85--interview--compare-deepcopy-pickle)

> [↑ Back to Top](#top)
