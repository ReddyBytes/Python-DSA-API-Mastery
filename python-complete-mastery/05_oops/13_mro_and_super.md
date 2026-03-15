# 🗺️ 13 — MRO & super(): Method Resolution Order Deep Dive

> *"Most developers use super() without understanding it.*
> *In simple single inheritance, that's fine.*
> *In multiple inheritance, misunderstanding super() causes silent, hard-to-debug errors."*

---

## 🎬 The Story

```python
class A:
    def greet(self): print("A")

class B(A):
    def greet(self): print("B")

class C(A):
    def greet(self): print("C")

class D(B, C):
    pass

D().greet()    # Which one runs? A? B? C?
```

Without knowing MRO, you're guessing.
With MRO, you know exactly. Every time.

---

## 🔑 What Is MRO?

**Method Resolution Order (MRO)** is the order Python searches through classes when looking for a method or attribute.

When you call `obj.method()`, Python searches:
1. The object's class
2. Parent classes — in MRO order
3. Stops at the first class where the method is found

```python
class D(B, C): pass

print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)

# Or more readable:
print([cls.__name__ for cls in D.__mro__])
# ['D', 'B', 'C', 'A', 'object']
```

---

## 📐 C3 Linearization — The Algorithm Python Uses

Python computes MRO using the **C3 Linearization** algorithm (introduced in Python 2.3).

**The rules:**
1. A class always appears before its parents
2. If a class has multiple parents, they appear in the order listed
3. The order is consistent across all subclasses (no contradictions)

**Step-by-step for `D(B, C)` where `B(A)` and `C(A)`:**

```
Classes: D, B, C, A, object

Start: [D] + merge( MRO(B), MRO(C), [B, C] )
MRO(B) = [B, A, object]
MRO(C) = [C, A, object]
List   = [B, C]

Step 1: Take head of first list (B). Is B in the TAIL of any list?
        Tails: [A, object], [A, object], [C]
        B is not in any tail → take B.
        Result so far: [D, B]

Step 2: Remaining: [A, object], [C, A, object], [C]
        Head of first = A. Is A in tail of [C, A, object]? YES (position 1)
        Skip. Try next list. Head = C. Is C in any tail? No.
        Take C.
        Result so far: [D, B, C]

Step 3: Remaining: [A, object], [A, object], []
        Head = A. Not in any tail. Take A.
        Result so far: [D, B, C, A]

Step 4: Take object.
        Final MRO: [D, B, C, A, object]
```

---

## 🎨 Visual MRO Examples

### Single Inheritance (simple):
```
    object
      │
      A
      │
      B
      │
      C

MRO(C) = [C, B, A, object]
```

### Diamond Inheritance:
```
      object
        │
        A
       / \
      B   C
       \ /
        D

MRO(D) = [D, B, C, A, object]
(B and C both before A — A appears only ONCE at the end)
```

```python
class A:
    def method(self): print("A")

class B(A):
    def method(self): print("B")

class C(A):
    def method(self): print("C")

class D(B, C): pass

D().method()    # "B"  ← B comes first in MRO

print(D.__mro__)
# D → B → C → A → object
```

### More Complex:
```python
class X: pass
class Y: pass
class Z: pass
class A(X, Y): pass
class B(Y, Z): pass
class C(A, B): pass

print([cls.__name__ for cls in C.__mro__])
# ['C', 'A', 'X', 'B', 'Y', 'Z', 'object']
```

---

## 🔁 `super()` — Not "Parent Class", But "Next in MRO"

This is the most critical insight about `super()`.

> `super()` does NOT mean "call my parent class."
> It means: "call the NEXT class in the MRO chain."

In simple single inheritance, "next in MRO" happens to be the parent.
But in multiple inheritance, it might not be.

```python
class A:
    def method(self):
        print("A.method")

class B(A):
    def method(self):
        print("B.method")
        super().method()    # calls NEXT in MRO — not necessarily A directly!

class C(A):
    def method(self):
        print("C.method")
        super().method()    # calls NEXT in MRO

class D(B, C):
    def method(self):
        print("D.method")
        super().method()    # calls next in MRO of D

D().method()
# D.method
# B.method       ← super() in D called B (next in MRO: D→B→C→A)
# C.method       ← super() in B called C (next in MRO: B→C→A)
# A.method       ← super() in C called A (next in MRO: C→A)
```

**Every class cooperates by calling `super()` — the chain propagates.**
This is called **Cooperative Multiple Inheritance**.

---

## 🧩 `super()` With Arguments (Python 2 vs 3)

```python
# Python 3 — no arguments needed (magic: knows current class + self):
class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)    # Python 3 style ✓

# Python 2 — required explicit arguments:
class Dog(Animal):
    def __init__(self, name, breed):
        super(Dog, self).__init__(name)    # Python 2 style

# Both work in Python 3. Use the shorter form.
```

---

## 🏦 Practical Example: Cooperative `__init__` in Multiple Inheritance

```python
class Timestamped:
    def __init__(self, *args, **kwargs):
        from datetime import datetime
        super().__init__(*args, **kwargs)    # pass remaining args along chain!
        self.created_at = datetime.now()

class Validated:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f"Validation complete for {self.__class__.__name__}")

class User:
    def __init__(self, name, email, **kwargs):
        super().__init__(**kwargs)           # consume only what you need
        self.name  = name
        self.email = email

class TimestampedValidatedUser(Timestamped, Validated, User):
    pass

# MRO: TimestampedValidatedUser → Timestamped → Validated → User → object
u = TimestampedValidatedUser(name="Alice", email="alice@mail.com")
# Validation complete for TimestampedValidatedUser

print(u.name)          # Alice
print(u.email)         # alice@mail.com
print(u.created_at)    # datetime object
```

> **Key:** Each `__init__` passes `*args, **kwargs` to `super().__init__()`.
> This lets the chain propagate naturally — each class takes what it needs.

---

## ⚠️ MRO Conflict — Impossible Hierarchy

```python
class A: pass
class B(A): pass

# This is IMPOSSIBLE — contradicts MRO rules:
class C(A, B): pass
# TypeError: Cannot create a consistent method resolution order (MRO)
# for bases A, B

# Why? A must come before B (A listed first).
# But B inherits A, so B must come before A in MRO.
# A before B AND B before A = contradiction!

# Fix: swap the order:
class C(B, A): pass   # B before A ✓ (consistent with B inheriting A)
```

---

## 🔍 Inspecting MRO

```python
class Animal: pass
class Mammal(Animal): pass
class Dog(Mammal): pass

# Three ways to see MRO:
print(Dog.__mro__)              # tuple of class objects
print(Dog.mro())                # list of class objects
import inspect
print(inspect.getmro(Dog))      # same as __mro__

# Readable version:
print([c.__name__ for c in Dog.__mro__])
# ['Dog', 'Mammal', 'Animal', 'object']
```

---

## 🎯 Key Takeaways

```
• MRO = the search order Python uses to find methods and attributes
• Python uses C3 Linearization algorithm to compute MRO
• Check it: ClassName.__mro__ or ClassName.mro()
• super() = "call the NEXT class in MRO", not "call my parent"
• In multiple inheritance, super() enables cooperative chaining
• Each class passes *args/**kwargs to super() for cooperative __init__
• Left parent has higher priority than right parent in MRO
• MRO conflict → TypeError: cannot create consistent MRO
• Fix MRO conflicts by reordering base classes or restructuring hierarchy
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [12 — Composition vs Inheritance](./12_composition_vs_inheritance.md) |
| 📖 Index | [README.md](./README.md) |
| ➡️ Next | [14 — Dataclasses](./14_dataclasses.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory Part 2](./theory_part2.md) &nbsp;|&nbsp; **Next:** [Theory Part 3 →](./theory_part3.md)

**Related Topics:** [Why Oop](./01_why_oop.md) · [Classes And Objects](./02_classes_and_objects.md) · [Init And Self](./03_init_and_self.md) · [Encapsulation](./04_encapsulation.md) · [Inheritance](./05_inheritance.md) · [Polymorphism](./06_polymorphism.md) · [Abstraction](./07_abstraction.md) · [Dunder Methods](./08_dunder_methods.md) · [Class Instance Static Methods](./09_class_instance_static_methods.md) · [Class Vs Instance Variables](./10_class_vs_instance_variables.md) · [Properties](./11_properties.md) · [Theory Part 1](./theory_part1.md) · [Composition Vs Inheritance](./12_composition_vs_inheritance.md) · [Theory Part 2](./theory_part2.md) · [Theory Part 3](./theory_part3.md) · [Dataclasses](./14_dataclasses.md) · [Slots](./15_slots.md) · [Metaclasses](./16_metaclasses.md) · [Descriptors](./17_descriptors.md) · [Mixins](./18_mixins.md) · [Solid Principles](./19_solid_principles.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
