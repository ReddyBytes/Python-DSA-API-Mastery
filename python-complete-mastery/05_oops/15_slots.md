# ⚡ 15 — `__slots__`: Memory Optimization

> *"When you have millions of objects, every byte matters.*
> *`__slots__` can cut memory usage by 40–70%.*
> *It's a production tool that most beginners have never heard of."*

---

## 🎬 The Story

You're building a real-time trading system.
At peak time, 2 million `Order` objects exist in memory simultaneously.
Each object normally uses ~400 bytes (because of `__dict__`).
Total: 2,000,000 × 400 bytes = **800 MB** just for orders.

With `__slots__`, each object uses ~120 bytes.
Total: 2,000,000 × 120 bytes = **240 MB** — you saved 560 MB.

That's the difference between the system running and crashing.

---

## 🧠 Why Normal Objects Are "Heavy"

Every Python object normally has a `__dict__` — a dictionary storing all instance attributes.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
print(p.__dict__)    # {'x': 1, 'y': 2}

import sys
print(sys.getsizeof(p))            # ~48 bytes (object overhead)
print(sys.getsizeof(p.__dict__))   # ~232 bytes (dict overhead!)
# Total: ~280 bytes per Point object
```

The problem: `__dict__` is a full Python dictionary with hashing tables, empty buckets, and overhead — even for objects with only 2 attributes.

---

## 🔧 `__slots__` — Declare Attributes Upfront

```python
class Point:
    __slots__ = ('x', 'y')   # declare allowed attributes

    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
print(p.x)    # 1  ← still works
print(p.y)    # 2  ← still works

import sys
print(sys.getsizeof(p))    # ~56 bytes — NO __dict__ overhead!
```

**Memory comparison:**

```
WITHOUT __slots__:
┌──────────────────────────────────────────────────────┐
│  Object overhead  ~48 bytes                          │
│  __dict__         ~232 bytes (empty dict)            │
│  Actual data      ~16 bytes (2 int references)       │
│  TOTAL:           ~296 bytes per object              │
└──────────────────────────────────────────────────────┘

WITH __slots__:
┌──────────────────────────────────────────────────────┐
│  Object overhead  ~48 bytes                          │
│  Slot descriptors ~8 bytes each × 2 = 16 bytes       │
│  TOTAL:           ~64 bytes per object               │
└──────────────────────────────────────────────────────┘

SAVINGS: ~230 bytes per object (78% reduction!)
```

---

## 📊 Benchmark — Real Numbers

```python
import sys, tracemalloc

class Regular:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

class Slotted:
    __slots__ = ('x', 'y', 'z')
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

# Memory for 1 million objects:
tracemalloc.start()
regular_objects = [Regular(i, i+1, i+2) for i in range(1_000_000)]
r_mem = tracemalloc.get_traced_memory()[1]
tracemalloc.stop()

tracemalloc.start()
slotted_objects = [Slotted(i, i+1, i+2) for i in range(1_000_000)]
s_mem = tracemalloc.get_traced_memory()[1]
tracemalloc.stop()

print(f"Regular: {r_mem / 1024 / 1024:.1f} MB")   # ~280+ MB
print(f"Slotted: {s_mem / 1024 / 1024:.1f} MB")   # ~80 MB
```

---

## ⚠️ What `__slots__` Prevents

```python
class Point:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x, self.y = x, y

p = Point(1, 2)

# 1. Cannot add new attributes:
p.z = 3    # ← AttributeError: 'Point' object has no attribute 'z'

# 2. No __dict__:
p.__dict__    # ← AttributeError: 'Point' object has no attribute '__dict__'

# 3. No __weakref__ (unless added to slots):
# (relevant for weak reference support)
```

---

## 🧬 `__slots__` With Inheritance — The Trap

```python
# ✅ Correct: both parent and child define __slots__
class Animal:
    __slots__ = ('name', 'age')
    def __init__(self, name, age):
        self.name, self.age = name, age

class Dog(Animal):
    __slots__ = ('breed',)     # only NEW slots here — inherited slots still exist!
    def __init__(self, name, age, breed):
        super().__init__(name, age)
        self.breed = breed

d = Dog("Rex", 3, "Labrador")
print(d.name, d.age, d.breed)   # Rex 3 Labrador
```

```python
# ❌ If parent does NOT have __slots__, child's __slots__ is useless:
class Animal:           # no __slots__ → has __dict__
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    __slots__ = ('breed',)    # ← meaningless! Animal's __dict__ still exists!

d = Dog("Rex")
d.anything = "works"    # no restriction because Animal has __dict__
```

> **Rule:** For `__slots__` to be effective, ALL classes in the hierarchy must define `__slots__`.

---

## 🔧 Keeping `__dict__` While Using `__slots__`

If you need both the memory savings for known attributes AND the flexibility to add dynamic attributes:

```python
class FlexPoint:
    __slots__ = ('x', 'y', '__dict__')   # ← include __dict__ explicitly!

    def __init__(self, x, y):
        self.x, self.y = x, y

p = FlexPoint(1, 2)
p.label = "origin"    # works! (stored in __dict__)
print(p.label)        # "origin"
```

---

## 🏗️ `__slots__` With `__weakref__`

```python
import weakref

class Node:
    __slots__ = ('value', 'next', '__weakref__')   # include __weakref__ for weak refs

    def __init__(self, value):
        self.value = value
        self.next  = None

n = Node(42)
ref = weakref.ref(n)    # works because __weakref__ is in slots
```

---

## 📊 When to Use `__slots__`

```
┌──────────────────────────────────────────────────────────────────────┐
│  USE __slots__ WHEN:                                                 │
│    ✓ Creating millions of instances (data points, game entities)    │
│    ✓ Memory is a constraint                                          │
│    ✓ Attributes are fixed and known at design time                  │
│    ✓ You want to prevent accidental attribute creation              │
│    ✓ Speed matters (slot access is slightly faster than dict lookup)│
│                                                                      │
│  AVOID __slots__ WHEN:                                               │
│    ✗ You need dynamic attribute addition (monkey-patching, mocking) │
│    ✗ You're not creating huge numbers of instances                  │
│    ✗ Classes use complex multiple inheritance (tricky to get right) │
│    ✗ Code uses pickling or deep copy extensively                    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Takeaways

```
• __slots__ replaces __dict__ with fixed C-level slots per attribute
• Memory savings: 40-70% reduction for attribute-heavy objects
• Prevents adding undeclared attributes (strict attribute contract)
• For inheritance: every class in chain must define __slots__
• Include '__dict__' in __slots__ if you need both savings + flexibility
• Include '__weakref__' if weak references are needed
• Use for: high-volume data objects, performance-critical code
• Not needed for: normal application classes with few instances
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [14 — Dataclasses](./14_dataclasses.md) |
| 📖 Index | [README.md](./README.md) |
| ➡️ Next | [16 — Metaclasses](./16_metaclasses.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Dataclasses](./14_dataclasses.md) &nbsp;|&nbsp; **Next:** [Metaclasses →](./16_metaclasses.md)

**Related Topics:** [Why Oop](./01_why_oop.md) · [Classes And Objects](./02_classes_and_objects.md) · [Init And Self](./03_init_and_self.md) · [Encapsulation](./04_encapsulation.md) · [Inheritance](./05_inheritance.md) · [Polymorphism](./06_polymorphism.md) · [Abstraction](./07_abstraction.md) · [Dunder Methods](./08_dunder_methods.md) · [Class Instance Static Methods](./09_class_instance_static_methods.md) · [Class Vs Instance Variables](./10_class_vs_instance_variables.md) · [Properties](./11_properties.md) · [Theory Part 1](./theory_part1.md) · [Composition Vs Inheritance](./12_composition_vs_inheritance.md) · [Theory Part 2](./theory_part2.md) · [Mro And Super](./13_mro_and_super.md) · [Theory Part 3](./theory_part3.md) · [Dataclasses](./14_dataclasses.md) · [Metaclasses](./16_metaclasses.md) · [Descriptors](./17_descriptors.md) · [Mixins](./18_mixins.md) · [Solid Principles](./19_solid_principles.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
