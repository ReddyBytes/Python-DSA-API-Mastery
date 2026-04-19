# ⚡ OOP Cheatsheet — Python

> Quick reference for syntax, patterns, and gotchas. One glance to remember everything.

---

## 🔧 Class Syntax

```python
class ClassName(ParentClass):

    class_var = "shared"          # class variable (shared across all instances)

    def __init__(self, x, y):
        self.x   = x              # instance variable (per object)
        self._y  = y              # convention: protected (don't touch from outside)
        self.__z = 0              # name-mangled: becomes _ClassName__z

    def instance_method(self):    # regular method — has self
        return self.x

    @classmethod
    def class_method(cls):        # class method — has cls, not self
        return cls.class_var

    @staticmethod
    def static_method():          # no self, no cls — pure utility function
        return "utility"

    def __repr__(self):           # for developers / REPL
        return f"ClassName(x={self.x!r})"

    def __str__(self):            # for end users / print()
        return f"x={self.x}"
```

---

## 🔑 Access Modifiers

```python
class Example:
    def __init__(self):
        self.public    = "anyone"        # accessible everywhere
        self._protected = "by convention"  # don't access outside (just a hint)
        self.__private  = "name mangled"   # Python renames to _Example__private

e = Example()
e.public             # ✓
e._protected         # ✓ (works, but shouldn't outside the class)
e.__private          # AttributeError!
e._Example__private  # ✓ (Python's actual name — don't use this either)
```

---

## 📦 Inheritance

```python
class Parent:
    def greet(self): return "Parent"

class Child(Parent):
    def greet(self):
        parent_result = super().greet()   # call parent version
        return f"Child + {parent_result}"

# Multiple inheritance:
class C(A, B):          # [MRO](./13_mro_and_super.md): C → A → B → object (left-to-right, then shared base last)
    pass

# Check MRO:
print(C.__mro__)
print([c.__name__ for c in C.__mro__])

# Check relationships:
isinstance(obj, ClassName)     # is obj an instance of ClassName (or subclass)?
issubclass(Child, Parent)      # is Child a subclass of Parent?
```

---

## 🌀 super()

```python
# In single inheritance:
super().__init__(args)         # calls Parent.__init__

# In multiple inheritance — calls NEXT IN MRO, not necessarily parent:
class Mixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   # MUST pass args along chain!

# Rule: every class in a cooperative MI chain calls super().__init__(*args, **kwargs)
```

---

## 🎭 The 4 Pillars

```python
# ── ENCAPSULATION ──────────────────────────────────────────
class BankAccount:
    def __init__(self, balance):
        self.__balance = balance   # private

    def deposit(self, amt):
        if amt > 0: self.__balance += amt

    @property
    def balance(self): return self.__balance

# ── INHERITANCE ────────────────────────────────────────────
class Animal:
    def speak(self): raise NotImplementedError
class Dog(Animal):
    def speak(self): return "Woof"

# ── POLYMORPHISM ───────────────────────────────────────────
animals = [Dog(), Cat(), Bird()]
for a in animals:
    print(a.speak())   # each behaves differently via same interface

# ── ABSTRACTION ────────────────────────────────────────────
from abc import ABC, abstractmethod
class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...   # must be implemented by subclasses

class Circle(Shape):
    def __init__(self, r): self.r = r
    def area(self): return 3.14 * self.r ** 2
```

---

## 🏠 `@property`

```python
class Temperature:
    @property
    def celsius(self):                # getter
        return self._celsius

    @celsius.setter
    def celsius(self, value):         # setter — same name as property!
        if value < -273.15:
            raise ValueError("Below absolute zero")
        self._celsius = value

    @celsius.deleter
    def celsius(self):                # deleter
        del self._celsius

    @property
    def fahrenheit(self):             # read-only computed property
        return self._celsius * 9/5 + 32
```

---

## 🪄 Essential Dunder Methods

```python
class MyClass:
    def __init__(self, x):     self.x = x        # construction
    def __repr__(self):        return f"MyClass({self.x!r})"  # repr()
    def __str__(self):         return str(self.x)              # str(), print()
    def __len__(self):         return self.x                   # len()
    def __bool__(self):        return self.x != 0              # bool(), if obj:
    def __eq__(self, other):   return self.x == other.x        # ==
    def __lt__(self, other):   return self.x < other.x         # <
    def __hash__(self):        return hash(self.x)             # dict key, set member
    def __add__(self, other):  return MyClass(self.x + other.x)  # +
    def __getitem__(self, i):  return self.x[i]                # obj[i]
    def __setitem__(self, i, v): self.x[i] = v                 # obj[i] = v
    def __contains__(self, v): return v in self.x              # in operator
    def __iter__(self):        return iter(self.x)             # for item in obj
    def __call__(self, *args): return self.x(*args)            # obj()
    def __enter__(self):       return self                     # with obj as x:
    def __exit__(self, *exc):  return False                    # end of with block

# Context manager shortcut:
from contextlib import contextmanager
@contextmanager
def managed():
    print("enter")
    yield value
    print("exit")
```

---

## 📊 Dataclasses

```python
from dataclasses import dataclass, field

@dataclass
class Product:
    name:     str
    price:    float
    tags:     list  = field(default_factory=list)  # mutable default
    _secret:  str   = field(default="", repr=False, init=False)

    def __post_init__(self):
        if self.price < 0: raise ValueError("price must be positive")

@dataclass(frozen=True)      # immutable + hashable
class Coordinate:
    lat: float
    lon: float

@dataclass(order=True)       # adds __lt__, __le__, __gt__, __ge__
class Employee:
    salary: float
    name:   str = field(compare=False)   # exclude name from ordering
```

---

## ⚡ [`__slots__`](./15_slots.md)

```python
class Point:
    __slots__ = ('x', 'y')     # no __dict__, ~5x less memory
    def __init__(self, x, y):
        self.x, self.y = x, y

# Cannot add new attributes:
p = Point(1, 2)
p.z = 3     # AttributeError!

# Inheritance: both parent AND child must define __slots__:
class Point3D(Point):
    __slots__ = ('z',)      # only NEW slots here — x, y inherited
    def __init__(self, x, y, z):
        super().__init__(x, y)
        self.z = z

# Include __dict__ to allow dynamic attrs AND slots:
class Flex:
    __slots__ = ('x', '__dict__')
```

---

## 🔬 Descriptors

```python
class Validator:
    def __set_name__(self, owner, name):      # auto-captures attr name
        self.name = name
        self.private = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None: return self           # accessed on class itself
        return getattr(obj, self.private, None)

    def __set__(self, obj, value):
        if not isinstance(value, int):
            raise TypeError(f"{self.name} must be int")
        setattr(obj, self.private, value)

class MyModel:
    count = Validator()   # descriptor placed as CLASS attribute

# Data descriptor (has __set__): beats instance __dict__
# Non-data descriptor (only __get__): instance __dict__ wins
```

---

## 🧬 [Metaclasses](./16_metaclasses.md)

```python
class MyMeta(type):
    def __new__(mcs, name, bases, namespace):
        # Intercept class creation
        cls = super().__new__(mcs, name, bases, namespace)
        cls._registered_at = "created"
        return cls

class Base(metaclass=MyMeta): pass
class Child(Base): pass    # MyMeta.__new__ is called for Child too

# Simpler alternative for most cases:
class Base:
    def __init_subclass__(cls, plugin_type=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if plugin_type:
            Base._registry[plugin_type] = cls

class Audio(Base, plugin_type="audio"): pass
```

---

## 🧩 Mixins

```python
class JSONMixin:
    def to_json(self):
        import json
        return json.dumps(self.__dict__, default=str)

class LogMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   # MUST call super!
        self._changes = []

    def __setattr__(self, name, value):
        if not name.startswith('_'):
            if hasattr(self, '_changes'):
                self._changes.append(f"{name}={value!r}")
        super().__setattr__(name, value)

# Mixins BEFORE the main class in the inheritance list:
class User(JSONMixin, LogMixin, BaseUser):
    pass
```

---

## 🏛️ SOLID Quick Reference

```
S — Single Responsibility  One class = one reason to change
                           "UserRepository saves. EmailService sends."

O — Open/Closed            Add via new classes, not by editing old ones
                           Strategy pattern, ABC subclasses

L — Liskov Substitution    Subclass is safely usable wherever parent is used
                           Don't break parent contracts / raise new exceptions

I — Interface Segregation  Small focused interfaces > one fat interface
                           typing.Protocol for flexible structural typing

D — Dependency Inversion   Depend on ABC/Protocol, not on MySQLDatabase()
                           Inject dependencies from outside (for testability)
```

---

## 🔴 Gotchas Quick Reference

```python
# 1 — Mutable class variable trap
class Bad:
    items = []           # shared! all instances mutate the same list
class Good:
    def __init__(self): self.items = []   # per-instance

# 2 — Property recursion
class Bad:
    @property
    def x(self): return self.x    # ← infinite recursion!
class Good:
    @property
    def x(self): return self._x   # ← backing store with underscore

# 3 — __eq__ without __hash__
class Incomplete:
    def __eq__(self, other): ...  # Python sets __hash__ = None automatically!
    # Add: def __hash__(self): return hash(self.id)

# 4 — __slots__ broken by parent without slots
class Parent:           # no __slots__ → has __dict__
    def __init__(self, name): self.name = name
class Child(Parent):
    __slots__ = ('age',)    # useless! Parent's __dict__ still exists

# 5 — super() in cooperative MI must pass args along
class Mixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   # ← don't forget!

# 6 — isinstance checks full MRO
class D(B, C): pass   # isinstance(D(), A) = True if A is parent of B or C
```

---

## 🗂️ Comparison Tables

### When To Use What

```
┌──────────────────┬──────────────────────────────────────────────────┐
│  Tool            │  When to use                                     │
├──────────────────┼──────────────────────────────────────────────────┤
│  @property       │  Computed attribute, validated setter, lazy load │
│  Descriptor      │  Reusable validation/logic across multiple class  │
│  @classmethod    │  Alternative constructors, class-level factories  │
│  @staticmethod   │  Utility function logically related to the class  │
│  Mixin           │  Cross-cutting ability (logging, JSON, equality)  │
│  ABC             │  Enforce interface contracts on subclasses        │
│  Protocol        │  Duck-typed interface, no inheritance required   │
│  @dataclass      │  Data container with auto __init__/__repr__/__eq__│
│  __slots__       │  Millions of instances, memory-critical code     │
│  Metaclass       │  Framework-level class creation hooks            │
│  __init_subclass__│ Simpler subclass hook without full metaclass    │
└──────────────────┴──────────────────────────────────────────────────┘
```

### Dataclass vs NamedTuple vs Regular Class

```
┌───────────────┬──────────────┬──────────────┬────────────────────┐
│  Feature      │  @dataclass  │  NamedTuple  │  Regular Class     │
├───────────────┼──────────────┼──────────────┼────────────────────┤
│  Mutable      │  Yes         │  No          │  Yes               │
│  Hashable     │  frozen=True │  Yes         │  Manual __hash__   │
│  Auto __init__│  Yes         │  Yes         │  No                │
│  Auto __repr__│  Yes         │  Yes         │  No                │
│  Ordering     │  opt-in      │  tuple-based │  Manual            │
│  Validation   │  __post_init__│  No         │  __init__          │
│  Inheritance  │  Yes         │  Limited     │  Full              │
└───────────────┴──────────────┴──────────────┴────────────────────┘
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Index | [README.md](./README.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| 🏠 Home | [python-complete-mastery](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Solid Principles](./19_solid_principles.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Why Oop](./01_why_oop.md) · [Classes And Objects](./02_classes_and_objects.md) · [Init And Self](./03_init_and_self.md) · [Encapsulation](./04_encapsulation.md) · [Inheritance](./05_inheritance.md) · [Polymorphism](./06_polymorphism.md) · [Abstraction](./07_abstraction.md) · [Dunder Methods](./08_dunder_methods.md) · [Class Instance Static Methods](./09_class_instance_static_methods.md) · [Class Vs Instance Variables](./10_class_vs_instance_variables.md) · [Properties](./11_properties.md) · [Theory Part 1](./theory_part1.md) · [Composition Vs Inheritance](./12_composition_vs_inheritance.md) · [Theory Part 2](./theory_part2.md) · [Mro And Super](./13_mro_and_super.md) · [Theory Part 3](./theory_part3.md) · [Dataclasses](./14_dataclasses.md) · [Slots](./15_slots.md) · [Metaclasses](./16_metaclasses.md) · [Descriptors](./17_descriptors.md) · [Mixins](./18_mixins.md) · [Solid Principles](./19_solid_principles.md) · [Interview Q&A](./interview.md)
