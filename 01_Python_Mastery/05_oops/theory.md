<a id="top"></a>
# 🏗 Object-Oriented Programming in Python

> *"OOP is not about classes and syntax.*
> *It is about modeling reality, controlling complexity, and building systems that scale."*

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    OOP LEARNING ARCHITECTURE                             │
│                                                                          │
│   PILLAR 1         PILLAR 2          PILLAR 3         PILLAR 4          │
│   Foundations      4 OOP Pillars     Python-Specific  Advanced          │
│   ──────────       ────────────      ───────────────  ────────          │
│   Why OOP          Inheritance       Dunder Methods   Dataclasses       │
│   Classes          Polymorphism      3 Method Types   __slots__         │
│   Objects          Abstraction       Properties       Metaclasses       │
│   __init__                           Class vs Inst.   Descriptors       │
│   Encapsulation                      Composition      Mixins            │
│                                                       SOLID             │
└──────────────────────────────────────────────────────────────────────────┘
```

## 📖 Table of Contents

- [1. What Is OOP and Why It Exists](#1-what-is-oop-and-why-it-exists)
- [2. Core Building Blocks](#2-core-building-blocks)
  - [Classes & Objects](#classes-and-objects)
  - [__init__ and self](#init-and-self)
  - [Method Types — Instance, Class, Static](#method-types)
  - [Class vs Instance Variables](#class-vs-instance-variables)
  - [Properties](#properties)
- [3. The 4 OOP Pillars](#3-the-4-oop-pillars)
  - [Encapsulation](#encapsulation)
  - [Inheritance](#inheritance)
  - [Polymorphism](#polymorphism)
  - [Abstraction](#abstraction)
- [4. Python-Specific OOP](#4-python-specific-oop)
  - [Dunder / Magic Methods](#dunder-methods)
  - [Composition vs Inheritance](#composition-vs-inheritance)
  - [MRO and super()](#mro-and-super)
- [5. Advanced & Production OOP](#5-advanced-and-production-oop)
  - [Dataclasses](#dataclasses)
  - [__slots__](#slots)
  - [Metaclasses](#metaclasses)
  - [Descriptors](#descriptors)
  - [Mixins](#mixins)
  - [SOLID Principles](#solid-principles)
  - [Enum Module](#enum-module)
- [6. When to Use OOP — The Decision](#6-when-to-use-oop--the-decision)
- [7. Recommended Learning Path](#7-recommended-learning-path)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
Classes and objects · `__init__` and `self` · Inheritance · Method types (instance/class/static) · `@property` · `__repr__` / `__str__`

**Should Learn** — Important for real projects, comes up regularly:
Multiple inheritance · MRO and `super()` · `@dataclass` · Encapsulation (`_` / `__`) · Dunder methods (`__eq__`, `__hash__`, `__len__`)

**Good to Know** — Useful in specific situations:
`__slots__` · Mixins · `@abstractmethod` / ABC · Descriptors · Metaclasses (basic concept)

**Reference** — Know it exists, look up when needed:
Metaclass advanced patterns · `__reduce__` / pickle protocol · `__init_subclass__`

<a id="1-what-is-oop-and-why-it-exists"></a>
# 1. What Is OOP and Why It Exists

When you write small scripts, functions and variables work fine. But when a manager says "build an e-commerce system" — users, orders, products, payments, inventory — flat variables collapse. For 10 million users you'd need 70 million loose variables. One schema change touches every file. OOP was invented to solve this: bundle data and behavior together into a single unit that represents a real-world entity.

```
WITHOUT OOP                          WITH OOP
────────────────────                 ────────────────────────────
user1_name = "Alice"                 class User:
user1_email = "a@mail.com"               def __init__(self, name, email):
user1_age = 25                               self.name = name
                                             self.email = email
user2_name = "Bob"
user2_email = "b@mail.com"           u1 = User("Alice", "a@mail.com", 25)
user2_age = 30                       u2 = User("Bob",   "b@mail.com", 30)

→ 1 million users = chaos            → 1 million users = User objects
→ No structure, no safety            → Structured, validated, maintainable
```

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PROBLEM OOP SOLVES         WHY IT MATTERS                              │
├─────────────────────────────────────────────────────────────────────────┤
│  1. Data grouping           Thousands of loose variables → one object   │
│  2. Data protection         Anyone can set balance=-1M → encapsulation  │
│  3. Code reuse              Copy-paste logic → inherit + extend         │
│  4. Modeling reality        "A User" represented as 1 thing, not 7 vars │
│  5. Scaling teams           5 devs editing same 3000-line file → modules│
└─────────────────────────────────────────────────────────────────────────┘
```

**[→ Deep dive: 01_why_oop.md](./01_why_oop.md)** — full story, OOP vs procedural side-by-side, when NOT to use OOP, expert insight.

> [↑ Back to Top](#top)

<a id="2-core-building-blocks"></a>
# 2. Core Building Blocks

<a id="classes-and-objects"></a>
## Classes & Objects

A **class** is a blueprint — no memory, no data, just a definition. An **object** is an instance of that blueprint, allocated on the heap. The variable that holds it is just a reference, not the object itself.

```python
class BankAccount:        # blueprint — nothing exists yet
    pass

account1 = BankAccount()  # object created on heap; account1 is a reference
account2 = BankAccount()  # separate object, separate memory
```

**[→ Deep dive: 02_classes_and_objects.md](./02_classes_and_objects.md)**

<a id="init-and-self"></a>
## `__init__` and `self`

`__init__` is not the constructor — `__new__` creates the object, `__init__` configures it. `self` is not magic: it is just the reference to the current instance, passed automatically by Python on every method call.

```python
class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner        # instance attribute — unique per object
        self.balance = balance

account = BankAccount("Alice", 5000)
# Python internally calls: BankAccount.__init__(account, "Alice", 5000)
```

**[→ Deep dive: 03_init_and_self.md](./03_init_and_self.md)**

<a id="method-types"></a>
## Method Types — Instance, Class, Static

Three distinct types of methods serve three distinct purposes:

```python
class User:
    count = 0                          # class variable

    def greet(self):                   # instance method — accesses self
        return f"Hi, I'm {self.name}"

    @classmethod
    def get_count(cls):                # class method — accesses class state
        return cls.count

    @staticmethod
    def validate_email(email):         # static method — no self or cls
        return "@" in email
```

```
Instance method  → operates on the object        (self)
Class method     → operates on the class         (cls)  — alternative constructors
Static method    → utility, belongs to class     (neither) — no state access
```

**[→ Deep dive: 09_class_instance_static_methods.md](./09_class_instance_static_methods.md)**

<a id="class-vs-instance-variables"></a>
## Class vs Instance Variables

Class variables are shared across ALL instances — mutating one through the class affects every object. Instance variables are unique to each object. This difference is one of the most common sources of bugs in Python OOP.

```python
class Counter:
    total = 0           # class variable — shared by ALL instances

    def __init__(self):
        self.count = 0  # instance variable — unique per object
```

**[→ Deep dive: 10_class_vs_instance_variables.md](./10_class_vs_instance_variables.md)**

<a id="properties"></a>
## `@property` — Controlled Attribute Access

`@property` lets you expose an attribute with getter/setter/deleter logic while keeping the call-site syntax clean (`obj.balance` instead of `obj.get_balance()`). Use it to validate on write, compute on read, or protect internal state.

```python
class BankAccount:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):               # read: account.balance
        return self._balance

    @balance.setter
    def balance(self, value):        # write: account.balance = 500
        if value < 0:
            raise ValueError("Balance cannot be negative")
        self._balance = value
```

**[→ Deep dive: 11_properties.md](./11_properties.md)**

> [↑ Back to Top](#top)

<a id="3-the-4-oop-pillars"></a>
# 3. The 4 OOP Pillars

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  ENCAPSULATION   Bundle data + behavior, hide internal details         │
│                  "A BankAccount controls who can change its balance"   │
│                                                                         │
│  INHERITANCE     Child class reuses and extends parent class           │
│                  "SavingsAccount IS-A BankAccount"                     │
│                                                                         │
│  POLYMORPHISM    Same method name, different behavior per class        │
│                  "Every Animal can speak(), but each speaks different" │
│                                                                         │
│  ABSTRACTION     Hide complexity, show only what's needed              │
│                  "You press Accelerate — don't know about fuel inject" │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

<a id="encapsulation"></a>
## Encapsulation

Protect internal state by hiding it and providing controlled access. Python uses naming conventions: `_name` (one underscore) = internal by convention; `__name` (two underscores) = name-mangled, harder to access directly.

```python
class BankAccount:
    def __init__(self, balance):
        self.__balance = balance        # name-mangled → _BankAccount__balance

    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount    # controlled mutation through method
```

**[→ Deep dive: 04_encapsulation.md](./04_encapsulation.md)**

<a id="inheritance"></a>
## Inheritance

A child class inherits all attributes and methods from its parent and can override or extend them. Use it for **IS-A** relationships. Python supports multiple inheritance — combined with MRO to resolve method lookup order.

```python
class SavingsAccount(BankAccount):    # SavingsAccount IS-A BankAccount
    def apply_interest(self, rate):
        self.deposit(self.balance * rate)
```

**[→ Deep dive: 05_inheritance.md](./05_inheritance.md)**

<a id="polymorphism"></a>
## Polymorphism

The same interface behaves differently depending on the type. Allows writing code that works on any object that implements a given method — no `isinstance` checks needed.

```python
class Dog:
    def speak(self): return "Bark"

class Cat:
    def speak(self): return "Meow"

for animal in [Dog(), Cat()]:
    print(animal.speak())    # same call, different behavior
```

**[→ Deep dive: 06_polymorphism.md](./06_polymorphism.md)**

<a id="abstraction"></a>
## Abstraction

Define a contract (interface) that subclasses must implement. Abstract base classes (`ABC`) enforce this at instantiation time — you cannot create an instance of an abstract class, only of its concrete subclasses.

```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def pay(self, amount): ...     # subclasses MUST implement this

class StripeProcessor(PaymentProcessor):
    def pay(self, amount):
        print(f"Charging ${amount} via Stripe")
```

**[→ Deep dive: 07_abstraction.md](./07_abstraction.md)**

> [↑ Back to Top](#top)

<a id="4-python-specific-oop"></a>
# 4. Python-Specific OOP

<a id="dunder-methods"></a>
## Dunder / Magic Methods

Dunder (double-underscore) methods let your objects respond to built-in operations: `+`, `len()`, `str()`, `==`, `[]`, `with`, iteration, and more. They are how all Python built-in types work internally.

```python
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):               # enables: v1 + v2
        return Vector(self.x + other.x, self.y + other.y)

    def __repr__(self):                     # enables: repr(v) and debugging
        return f"Vector({self.x}, {self.y})"

    def __len__(self):                      # enables: len(v)
        return 2
```

**[→ Deep dive: 08_dunder_methods.md](./08_dunder_methods.md)**

<a id="composition-vs-inheritance"></a>
## Composition vs Inheritance

Inheritance = **IS-A** (tight coupling). Composition = **HAS-A** (flexible). Senior engineers prefer composition — it avoids the fragile base class problem and makes code easier to change.

```python
# Inheritance (tight coupling):
class ElectricCar(Car): ...           # ElectricCar IS-A Car

# Composition (flexible):
class Car:
    def __init__(self):
        self.engine = Engine()        # Car HAS-A Engine
        self.battery = Battery()      # Car HAS-A Battery
```

**[→ Deep dive: 12_composition_vs_inheritance.md](./12_composition_vs_inheritance.md)**

<a id="mro-and-super"></a>
## MRO and `super()`

When a method is called, Python searches the class hierarchy in a specific order called the **Method Resolution Order (MRO)**, computed using the C3 Linearization algorithm. `super()` does NOT mean "parent class" — it means "next class in MRO order," which matters critically in multiple inheritance.

```python
class C(A, B):
    pass

print(C.__mro__)    # (C, A, B, object) — the search order

class B(A):
    def __init__(self):
        super().__init__()    # calls next in MRO, not necessarily A directly
```

**[→ Deep dive: 13_mro_and_super.md](./13_mro_and_super.md)**

> [↑ Back to Top](#top)

<a id="5-advanced-and-production-oop"></a>
# 5. Advanced & Production OOP

<a id="dataclasses"></a>
## Dataclasses

`@dataclass` auto-generates `__init__`, `__repr__`, and `__eq__` from field annotations. Use it whenever a class is primarily a data container — eliminates boilerplate while keeping full OOP control.

```python
from dataclasses import dataclass, field

@dataclass
class User:
    name: str
    email: str
    age: int = 0
    tags: list = field(default_factory=list)
```

**[→ Deep dive: 14_dataclasses.md](./14_dataclasses.md)**

<a id="slots"></a>
## `__slots__`

By default, every object stores its attributes in a `__dict__` (a hash map). `__slots__` replaces this with a fixed-size array — lower memory usage (20–50% less per object) and faster attribute access. Critical when creating millions of instances.

```python
class Point:
    __slots__ = ("x", "y")    # no __dict__ — only x and y allowed
    def __init__(self, x, y):
        self.x, self.y = x, y
```

**[→ Deep dive: 15_slots.md](./15_slots.md)**

<a id="metaclasses"></a>
## Metaclasses

A metaclass is the class of a class. Just as `BankAccount()` creates a `BankAccount` instance, `type(...)` creates a class. Metaclasses let you intercept and customize class creation — used by ORMs, frameworks, and validation libraries.

```python
class Meta(type):
    def __new__(mcs, name, bases, namespace):
        # runs when a class using this metaclass is DEFINED
        return super().__new__(mcs, name, bases, namespace)
```

**[→ Deep dive: 16_metaclasses.md](./16_metaclasses.md)**

<a id="descriptors"></a>
## Descriptors

A descriptor is an object that defines `__get__`, `__set__`, or `__delete__`. It is the protocol that powers `@property`, `@classmethod`, `@staticmethod`, and ORM field definitions. Understanding descriptors demystifies how Python attribute access really works.

```python
class Validator:
    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, obj, value):
        if value < 0:
            raise ValueError(f"{self.name} cannot be negative")
        obj.__dict__[self.name] = value
```

**[→ Deep dive: 17_descriptors.md](./17_descriptors.md)**

<a id="mixins"></a>
## Mixins

A mixin is a class that provides reusable behavior to be mixed into other classes via multiple inheritance — but it is not meant to stand alone as an object. Used heavily in Django (LoginRequiredMixin), DRF, and Flask.

```python
class JsonMixin:
    def to_json(self):
        import json
        return json.dumps(self.__dict__)

class User(JsonMixin, BaseModel):    # User gains to_json() without changing BaseModel
    ...
```

**[→ Deep dive: 18_mixins.md](./18_mixins.md)**

<a id="solid-principles"></a>
## SOLID Principles

Five architecture rules that make OOP systems maintainable and extensible at scale:

```
S — Single Responsibility   One class, one reason to change
O — Open/Closed             Open for extension, closed for modification
L — Liskov Substitution     Subclass must be usable wherever parent is used
I — Interface Segregation   Many small interfaces > one large interface
D — Dependency Inversion    Depend on abstractions, not concrete classes
```

**[→ Deep dive: 19_solid_principles.md](./19_solid_principles.md)**

<a id="enum-module"></a>
## Enum Module

`Enum` creates named constants that are type-safe and iterable. Use instead of magic strings or int flags — prevents typos, enables IDE autocomplete, and makes code self-documenting.

```python
from enum import Enum, auto

class Status(Enum):
    PENDING  = auto()
    ACTIVE   = auto()
    INACTIVE = auto()

order.status = Status.PENDING    # not "pending" — no typo risk
```

**[→ Deep dive: 20_enum_module.md](./20_enum_module.md)**

> [↑ Back to Top](#top)

<a id="6-when-to-use-oop--the-decision"></a>
# 6. When to Use OOP — The Decision

```
USE OOP WHEN:                          DON'T USE OOP WHEN:
──────────────────────────────         ──────────────────────────────
• You model real-world entities        • Simple script or one-off task
• Data + behavior belong together      • Pure data transformation
• Multiple instances of same type      • Functional pipeline (map/filter)
• Complex state management needed      • Small utility functions
• Large teams building one system      • Performance-critical low-level code
```

```python
# ❌ Over-engineered — just use a function:
class NumberAdder:
    def add(self, a, b):
        return a + b

result = NumberAdder().add(3, 4)

# ✅ Correct:
result = 3 + 4
```

## ⚠️ The 5 Most Common OOP Mistakes

```
1. Using inheritance when composition is better
2. Making everything a class (sometimes functions are enough)
3. Confusing class variables and instance variables → shared state bugs
4. Not using @property — directly exposing attributes
5. Overriding methods without calling super() — breaks parent initialization
```

> **Python is multi-paradigm.** Use OOP where entities with state make sense, and simple functions everywhere else. Forcing OOP on everything is not Pythonic.

> [↑ Back to Top](#top)

<a id="7-recommended-learning-path"></a>
# 7. Recommended Learning Path

```
BEGINNER — learn the 4 pillars first:
  01 → 02 → 03 → 04 → 05 → 06 → 07

INTERMEDIATE — Python-specific mechanics:
  08 → 09 → 10 → 11 → 12 → 13

INTERVIEW PREP:
  Pillars 1–2 (01–07) → interview.md → cheetsheet.md

SENIOR / PRODUCTION level:
  Pillar 3 complete (08–13) → 14 → 15 → 19 (SOLID) → 16 → 17 → 18
```

> [↑ Back to Top](#top)

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [04_functions → theory.md](../04_functions/theory.md) |
| ➡ Next Module | [06_exceptions_error_handling → theory.md](../06_exceptions_error_handling/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md) · [practice_local.py](./practice_local.py)

**All concept files:**
[01 Why OOP](./01_why_oop.md) · [02 Classes & Objects](./02_classes_and_objects.md) · [03 init & self](./03_init_and_self.md) · [04 Encapsulation](./04_encapsulation.md) · [05 Inheritance](./05_inheritance.md) · [06 Polymorphism](./06_polymorphism.md) · [07 Abstraction](./07_abstraction.md) · [08 Dunder Methods](./08_dunder_methods.md) · [09 Method Types](./09_class_instance_static_methods.md) · [10 Class vs Instance Vars](./10_class_vs_instance_variables.md) · [11 Properties](./11_properties.md) · [12 Composition vs Inheritance](./12_composition_vs_inheritance.md) · [13 MRO & super()](./13_mro_and_super.md) · [14 Dataclasses](./14_dataclasses.md) · [15 __slots__](./15_slots.md) · [16 Metaclasses](./16_metaclasses.md) · [17 Descriptors](./17_descriptors.md) · [18 Mixins](./18_mixins.md) · [19 SOLID](./19_solid_principles.md) · [20 Enum](./20_enum_module.md)

**Related modules:**
[04_functions →](../04_functions/theory.md) · [10_decorators →](../10_decorators/theory.md) · [15_advanced_python →](../15_advanced_python/theory.md)

**Jump to specific topics in other files:**
- Closures → [04_functions/theory.md#8-closures--functions-that-remember](../04_functions/theory.md#8-closures--functions-that-remember)
- Decorators → [04_functions/theory.md#9-decorators--functions-that-wrap-functions](../04_functions/theory.md#9-decorators--functions-that-wrap-functions)
- Metaclasses deep dive → [15_advanced_python →](../15_advanced_python/theory.md)

> [↑ Back to Top](#top)
