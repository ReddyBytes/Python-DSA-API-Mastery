# 🏗 Object Oriented Programming (OOP) in Python
## Part 2 – Deep Internal Breakdown (How Python Actually Works)

---

# 🔬 Chapter 1 – What Really Happens When You Create an Object?

In Part 1, we saw this:

```python
account1 = BankAccount(1000)
```

Let’s slow this down like engineers.

Object creation in Python happens in TWO steps:

1. `__new__` → Creates the object
2. `__init__` → Initializes the object

Most beginners only know `__init__`.
Senior engineers understand both.

---

## 🧠 Step 1 – `__new__` (Memory Allocation Phase)

Before initialization happens:

- Python allocates memory
- Builds a blank object
- Returns reference

You rarely override `__new__`, but internally it always runs.

Execution flow:

```
Call BankAccount(1000)
        ↓
BankAccount.__new__()
        ↓
Empty object created in heap
        ↓
BankAccount.__init__(self, 1000)
```

Key insight:

`__new__` creates.
`__init__` configures.

---

# 🏗 Chapter 2 – The Python Object Model (Everything Is an Object)

Let’s break your mental model.

In Python:

- int is object
- str is object
- list is object
- function is object
- class is object

Even classes are instances of `type`.

Example:

```python
print(type(int))
```

Output:

```
<class 'type'>
```

This means:

Classes themselves are objects created by a metaclass (`type`).

Memory Model:

```
type → creates classes
class → creates objects
object → base of all classes
```

Hierarchy:

```
object
   ↑
YourClass
   ↑
YourObject
```

This layered architecture is what makes Python flexible.

---

# 🧬 Chapter 3 – Method Resolution Order (MRO)

Now things get interesting.

Consider:

```python
class A:
    def greet(self):
        print("A")

class B(A):
    pass
```

When you call:

```python
B().greet()
```

Python searches:

1. B
2. A
3. object

This search order is called MRO.

---

## 🧠 Why MRO Matters?

In multiple inheritance, order becomes critical.

Example:

```python
class A:
    def greet(self):
        print("A")

class B:
    def greet(self):
        print("B")

class C(A, B):
    pass
```

Now:

```python
C().greet()
```

Which one runs?

Python uses C3 Linearization algorithm.

Search order:

```
C → A → B → object
```

You can inspect:

```python
print(C.__mro__)
```

Understanding MRO prevents serious bugs in large systems.

---

# 🔁 Chapter 4 – super() Deep Explanation

Many developers misuse `super()`.

Let’s break it properly.

Example:

```python
class A:
    def __init__(self):
        print("A")

class B(A):
    def __init__(self):
        super().__init__()
        print("B")
```

Calling:

```python
B()
```

Flow:

```
B.__init__()
  ↓
super() finds next in MRO → A
  ↓
A.__init__()
  ↓
Back to B
```

Important:

`super()` does NOT mean "parent class".

It means:

> "Call next class in MRO order."

This matters in multiple inheritance.

---

# 🧩 Chapter 5 – Class Methods vs Static Methods

Let’s clarify properly.

## Instance Method

```python
def method(self):
```

Operates on object instance.

Has access to instance variables.

---

## Class Method

```python
@classmethod
def method(cls):
```

Operates on class.

Used for:
- Alternative constructors
- Class-level operations

Example:

```python
class Person:
    population = 0

    @classmethod
    def increment_population(cls):
        cls.population += 1
```

---

## Static Method

```python
@staticmethod
def method():
```

No access to self or cls.

Used when:
- Function logically belongs to class
- But does not depend on instance or class state

---

# 🧠 Engineering Insight

Use:

- Instance method → when behavior modifies object
- Class method → when behavior modifies class
- Static method → when behavior is utility-related

---

# 🧱 Chapter 6 – Composition vs Inheritance

This is critical in architecture.

Inheritance:
```
Car IS-A Vehicle
```

Composition:
```
Car HAS-A Engine
```

Example:

```python
class Engine:
    pass

class Car:
    def __init__(self):
        self.engine = Engine()
```

Composition is safer.

Why?

Because inheritance tightly couples classes.
Composition keeps them flexible.

Senior engineers prefer composition.

---

# 🎭 Chapter 7 – Dunder (Magic) Methods

Dunder = Double underscore.

Examples:

- `__init__`
- `__str__`
- `__repr__`
- `__len__`
- `__add__`

These allow operator overloading.

Example:

```python
class Point:
    def __init__(self, x):
        self.x = x

    def __add__(self, other):
        return Point(self.x + other.x)
```

Now:

```python
p1 + p2
```

Works because of `__add__`.

This is how built-in types work internally.

---

# 🧠 Chapter 8 – How Attribute Lookup Works Internally

When you do:

```python
obj.attribute
```

Python searches in order:

1. Instance dictionary (`obj.__dict__`)
2. Class dictionary (`Class.__dict__`)
3. Parent classes (MRO)
4. object base class

Understanding this explains:

- Why overriding works
- Why class variables behave differently
- Why dynamic attribute addition works

---

# 🧬 Chapter 9 – Dynamic Nature of Python Objects

In Python:

You can add attributes dynamically.

```python
obj.new_attribute = 10
```

Because objects store attributes in dictionary:

```python
obj.__dict__
```

This flexibility makes Python powerful.

But in large systems, uncontrolled dynamism can cause bugs.

---

# 🧠 Chapter 10 – Dataclasses (Modern Python OOP)

Instead of writing boilerplate:

```python
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age
```

You can use:

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
```

Dataclass automatically generates:
- __init__
- __repr__
- __eq__

Used in modern clean architecture.

---

# 🏗 Chapter 11 – The Big Picture (How Real Systems Use OOP)

Large systems use OOP to:

- Model domain entities
- Enforce boundaries
- Prevent invalid states
- Enable testing
- Scale development teams

OOP is not about classes.

It is about:

- Responsibility separation
- Controlled state mutation
- Predictable behavior

---

# 🏁 Part 2 Summary

You now understand:

- __new__ vs __init__
- Python object model
- MRO internals
- super() true meaning
- Class vs static vs instance methods
- Composition vs inheritance
- Magic methods
- Attribute lookup chain
- Dynamic object behavior
- Dataclasses

You are now thinking at senior developer level.

---

# 🔁 Navigation

[Back to OOP Part 1](/python-complete-mastery/05_oops/theory_part1.md)  
[Next: OOP Architecture & Design Principles – Part 3](/python-complete-mastery/05_oops/theory_part3.md)

---
