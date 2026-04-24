# 🧠 Memory Management in Python

From Reference Counting to Garbage Collection Internals

> 📝 **Practice:** [Q80 · explain-memory](../python_practice_questions_100.md#q80--interview--explain-memory)

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
Stack vs heap · Reference counting · Garbage collection (cyclic GC) · Object identity (`id()`)

**Should Learn** — Important for real projects, comes up regularly:
`__slots__` memory optimization · Generators vs lists (memory) · `sys.getsizeof()` · `weakref`

**Good to Know** — Useful in specific situations:
Memory layout (arenas → pools → blocks) · Small integer caching internals

**Reference** — Know it exists, look up when needed:
`weakref` callbacks · `gc` module API · Frame introspection

---

# 🎯 Why Memory Management Matters

Imagine:

Your application runs fine for 10 minutes.
Then memory keeps increasing.
Then server crashes.

Why?

Memory not released properly.

In large systems:

- Memory leaks kill servers
- Inefficient objects slow performance
- Large data structures consume GBs
- Poor design increases GC overhead

Understanding memory makes you better engineer.

---

# 🧠 1️⃣ Where Does Python Store Data?

Two main areas:

1️⃣ Stack
2️⃣ Heap

---

## 🔹 Stack

- Stores function calls
- Stores local variable references
- Fast access
- Automatically cleaned when function returns

---

## 🔹 Heap

- Stores objects
- Dynamic memory allocation
- Managed by Python runtime

Almost all objects live in heap.

---

# 🧱 2️⃣ Objects and References

In Python:

Variables do NOT store actual values.

They store references to objects.

Example:

```python
x = 10
```

Internally:

- Integer object 10 created in heap.
- Variable x stores reference to that object.

If:

```python
y = x
```

Now:

x and y both refer to same object.

---

# 🔍 3️⃣ Reference Counting

Python primarily uses:

Reference counting.

Each object keeps count of:

How many references point to it.

When reference count becomes zero:

Object is immediately deleted.

> 📝 **Practice:** [Q57 · reference-counting](../python_practice_questions_100.md#q57--thinking--reference-counting)

---

## 🔹 Example

```python
x = [1, 2, 3]
y = x
```

Reference count = 2

If:

```python
del x
```

Reference count = 1

If:

```python
del y
```

Reference count = 0

Object removed.

---

# 🧠 4️⃣ How to Check Reference Count

```python
import sys
sys.getrefcount(obj)
```

Note:

Returns one extra reference (temporary).

Used for debugging.

---

# ⚠️ 5️⃣ Problem: Circular References

Example:

```python
a = []
b = []
a.append(b)
b.append(a)
```

Now:

- a references b
- b references a

Even if:

```python
del a
del b
```

Reference count not zero.

They still reference each other.

Memory leak.

---

# ♻️ 6️⃣ Garbage Collector (GC)

To solve circular reference issue,
Python has:

Garbage collector.

Module:

```python
import gc
```

GC detects cycles.

Deletes unreachable cyclic objects.

> 📝 **Practice:** [Q58 · gc-cycles](../python_practice_questions_100.md#q58--normal--gc-cycles)

---

# 🧠 7️⃣ How Garbage Collection Works

Python uses:

Generational garbage collection.

Objects divided into generations:

- Generation 0 (new objects)
- Generation 1
- Generation 2 (long-lived)

New objects go to Gen 0.

If survive multiple collections:
Move to older generation.

Older generation scanned less frequently.

Improves performance.

---

# 🔍 8️⃣ GC Control Methods

```python
gc.collect()
```

Manually trigger GC.

```python
gc.get_count()
```

Check collection stats.

```python
gc.disable()
```

Disable automatic GC (rarely needed).

---

# 🧠 9️⃣ Memory Leaks in Python

Memory leaks happen when:

- Objects remain referenced unintentionally
- Global variables store large data
- C extensions mismanage memory
- Circular references with __del__ method
- Caching grows indefinitely

Python does not guarantee automatic memory efficiency.

Design matters.

---

# ⚡ 1️⃣0️⃣ __del__ Method (Destructor)

```python
class A:
    def __del__(self):
        print("Deleted")
```

Runs when object is destroyed.

Be careful:

If used in circular references,
GC may not collect properly.

Avoid heavy logic inside __del__.

---

# 🧠 1️⃣1️⃣ Memory Optimization Techniques

---

## 🔹 Use [Generators](../11_generators_iterators/theory.md) Instead of Lists

Instead of:

```python
[x for x in range(1_000_000)]
```

Use:

```python
(x for x in range(1_000_000))
```

---

## 🔹 Use [`__slots__`](../05_oops/15_slots.md) in Classes

Normal class:

Each object has __dict__.

Consumes memory.

Using __slots__:

```python
class User:
    __slots__ = ['name', 'age']
```

Prevents dynamic attribute creation.
Reduces memory usage.

> 📝 **Practice:** [Q59 · __slots__](../python_practice_questions_100.md#q59--design--__slots__) · [Q75 · slots-optimization](../python_practice_questions_100.md#q75--design--slots-optimization)

---

## 🔹 Avoid Large Global Variables

Global large data persists forever.

Prefer local scoping.

---

## 🔹 Use Weak References

Module:

```python
import weakref
```

Allows reference without increasing reference count.

Used in caching systems.

---

# 🧠 1️⃣2️⃣ Object Interning

Small integers and short strings may be reused.

Example:

```python
a = 5
b = 5
```

Both may reference same object.

Optimization by Python.

---

# 🔍 1️⃣3️⃣ Memory Profiling Tools

Useful tools:

- tracemalloc
- memory_profiler
- objgraph

Example:

```python
import tracemalloc
tracemalloc.start()
```

Used in debugging memory leaks.

---

# ⚠️ 1️⃣4️⃣ Common Memory Mistakes

❌ Loading huge file into list
❌ Storing unnecessary references
❌ Growing caches indefinitely
❌ Using global variables excessively
❌ Not clearing large data structures
❌ Keeping objects alive unintentionally

---

# 🏗 1️⃣5️⃣ Real Production Scenarios

---

## 🔹 Web Server Memory Growth

Cause:

- Storing request data globally
- Leaking references

Fix:

- Clear references
- Use weak references
- Profile memory

---

## 🔹 Data Pipeline Crash

Cause:

- Using list instead of generator
- Loading entire dataset

Fix:

- Stream processing
- Chunk-based loading

---

# 🏆 1️⃣6️⃣ Engineering Maturity Levels

Beginner:
Does not think about memory.

Intermediate:
Understands reference counting.

Advanced:
Uses GC tools and profiling.

Senior:
Designs memory-efficient architectures.

---

# 🗺️ 1️⃣7️⃣ Memory Layout: Stack, Heap, and Scope

Understanding WHERE variables live explains performance, lifetimes, and [closures](../04_functions/theory.md#closure-cell-internals--how-captured-variables-actually-work).

---

## 🔹 The Three Memory Regions

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

---

## 🔹 Stack Frame — What Happens on Each Call

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
  heap objects survive if something else holds them
```

Key insight:

Variable names live in the frame.
Objects always live in the heap.
When frame is destroyed, name bindings disappear.
Objects survive if their reference count is still > 0.

---

## 🔹 Variable Lifetime by Scope

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

---

## 🔹 Enclosing Scope — The Closure Cell on the Heap

Normal rule: local variable → dies when function returns.
Closure exception: if an inner function captures it, Python promotes it to a cell object on the heap.

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

---

## 🔹 Global Variables — NOT on the Stack

Common misconception: globals are stored somewhere "global" and special.

Reality: globals live in the module's `__dict__` object — which is on the heap.

```python
config = {"debug": True}   # heap → module.__dict__["config"]
MAX_RETRIES = 3             # heap → module.__dict__["MAX_RETRIES"]
```

They persist for the entire program lifetime.
This is why large globals are a memory concern.

---

## 🔹 Stack is Faster Than Heap

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

---

# 🧠 Final Mental Model

Memory management in Python involves:

1️⃣ Reference counting
2️⃣ Garbage collection
3️⃣ Generational cleanup
4️⃣ Scope determines variable lifetime
5️⃣ Closures use heap cell objects to survive function return

Important ideas:

- Variables store references
- Objects live in heap
- GC handles cycles
- Design impacts memory usage
- Memory leaks still possible
- Local scope is stack-fast; global scope is heap-resident
- Enclosing variables escape the stack via cell objects

Understanding memory management improves:

Performance
Scalability
Reliability

Memory knowledge makes you senior-level engineer.

---

# 🔁 Navigation

Previous:
[13_concurrency/interview.md](../13_concurrency/interview.md)

Next:
[14_memory_management/interview.md](./interview.md)

---

## 📝 Practice Questions

> 📝 **Practice:** [Q85 · compare-deepcopy-pickle](../python_practice_questions_100.md#q85--interview--compare-deepcopy-pickle)

> 📝 **Practice:** [Q48 · shallow-vs-deep-copy](../python_practice_questions_100.md#q48--critical--shallow-vs-deep-copy)

---

**[🏠 Back to README](../README.md)**

**Prev:** — &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
