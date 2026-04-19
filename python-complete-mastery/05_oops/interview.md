# 🎯 OOP Interview Questions — Python

> *"An interview doesn't test what you know.*
> *It tests whether you understand why things work the way they do.*
> *That's the difference between a coder and an engineer."*

---

## 📊 Question Map

```
LEVEL 1 — Junior (0–2 years)
  • Core OOP definitions
  • Basic class syntax
  • 4 OOP pillars
  • __init__, self, methods

LEVEL 2 — Mid-Level (2–5 years)
  • [MRO](./13_mro_and_super.md) and super()
  • Dunder methods
  • @property vs attribute
  • Composition vs inheritance
  • Class vs instance variables trap

LEVEL 3 — Senior (5+ years)
  • [Metaclasses](./16_metaclasses.md) and [descriptors](./17_descriptors.md)
  • SOLID principles
  • [`__slots__`](./15_slots.md) and memory optimization
  • Design patterns with OOP
  • Abstract Base Classes
```

---

## 🟢 Level 1 — Junior Questions

---

### Q1: What is the difference between a class and an object?

**Weak answer:** "A class is like a blueprint and an object is an instance of it."

**Strong answer:**

> A **class** is a definition — it describes what attributes and methods objects of that type will have. It exists only in code; no memory is allocated for the data yet.
>
> An **object** (instance) is a concrete realization of that blueprint in memory. When you call `User("Alice", 25)`, Python allocates memory, calls `__init__`, and returns a live object with its own state.

```python
class User:
    def __init__(self, name, age):
        self.name = name
        self.age  = age

# Class: User (the template, in code)
# Objects: u1, u2 (live, in memory, each with own state)
u1 = User("Alice", 25)
u2 = User("Bob",   30)

print(u1 is u2)      # False — different objects
print(type(u1))      # <class 'User'>
print(type(User))    # <class 'type'>  ← class itself is an object of 'type'
```

---

### Q2: What are the 4 pillars of OOP and what does each mean?

**Weak answer:** Lists the names without a concrete example.

**Strong answer:**

```
ENCAPSULATION
  Bundle data + methods that operate on that data into one unit.
  Control access to internal state using public/protected/private.

  class BankAccount:
      def __init__(self):
          self.__balance = 0      # private
      def deposit(self, amt):     # controlled access
          if amt > 0:
              self.__balance += amt
      def get_balance(self):
          return self.__balance

INHERITANCE
  A child class inherits attributes and methods from a parent class.
  Promotes code reuse. Represents IS-A relationships.

  class Animal:
      def breathe(self): print("breathing")
  class Dog(Animal):
      def bark(self): print("Woof")
  d = Dog()
  d.breathe()    # inherited — no duplication

POLYMORPHISM
  Different classes can be treated through a common interface.
  Same method name → different behavior based on the actual object type.

  class Cat:
      def speak(self): print("Meow")
  class Dog:
      def speak(self): print("Woof")
  for animal in [Cat(), Dog()]:
      animal.speak()   # same call, different result

ABSTRACTION
  Expose WHAT an object does, hide HOW it does it.
  Abstract classes define interfaces; subclasses provide implementations.

  from abc import ABC, abstractmethod
  class Shape(ABC):
      @abstractmethod
      def area(self) -> float: ...   # interface, no implementation
  class Circle(Shape):
      def area(self): return 3.14 * self.radius ** 2
```

---

### Q3: What is `self` and why is it needed?

**Weak answer:** "It refers to the current object."

**Strong answer:**

> `self` is the first parameter in every instance method. It's how Python passes the instance to the method — connecting the method call to the specific object's data.
>
> When you write `u.greet()`, Python internally calls `User.greet(u)` — `self` is just the object `u` passed explicitly.

```python
class User:
    def __init__(self, name):
        self.name = name   # stores on THIS instance

    def greet(self):
        return f"Hi, I'm {self.name}"

u1 = User("Alice")
u2 = User("Bob")

# These are identical:
u1.greet()            # Python's shorthand
User.greet(u1)        # Explicit form — same thing!

# Without self, Python can't know WHICH instance's name to use:
print(u1.name)   # Alice
print(u2.name)   # Bob   ← different data, same class
```

---

### Q4: What is the difference between `__init__` and `__new__`?

**Weak answer:** "`__init__` is the constructor."

**Strong answer:**

> `__new__` is called first — it **creates** the object (allocates memory, returns a new instance).
>
> `__init__` is called second — it **initializes** the created object (sets attributes).
>
> In practice, you almost never override `__new__`. The most common use cases are: implementing the Singleton pattern, or creating immutable objects (subclassing `str`, `int`, `tuple`).

```python
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance   # always returns the same object

    def __init__(self):
        pass

a = Singleton()
b = Singleton()
print(a is b)    # True — same object
```

---

### Q5: What is the difference between `@classmethod`, `@staticmethod`, and a regular method?

**Strong answer:**

```python
class MyClass:
    class_var = 0

    def instance_method(self):
        # Has access to self (instance) AND class via self.__class__
        # Use for: behavior that reads/modifies instance state
        return self.class_var

    @classmethod
    def class_method(cls):
        # Has access to cls (the class itself), NOT the instance
        # Use for: alternative constructors, class-level operations
        return cls.class_var

    @staticmethod
    def static_method():
        # Has access to NEITHER self nor cls
        # It's a regular function that lives in the class namespace
        # Use for: utility logic related to the class but not dependent on it
        return "utility"

# All three ways to call:
obj = MyClass()
obj.instance_method()      # ✓
MyClass.class_method()     # ✓ (also obj.class_method())
MyClass.static_method()    # ✓ (also obj.static_method())
```

```
Decision tree:
  Needs self (instance state)?  → instance method
  Needs cls (class state)?      → @classmethod
  Needs neither?                → @staticmethod
```

---

## 🔵 Level 2 — Mid-Level Questions

---

### Q6: Explain Python's [MRO](./13_mro_and_super.md) and how `super()` actually works.

**Weak answer:** "`super()` calls the parent class."

**Strong answer:**

> Python's **MRO (Method Resolution Order)** defines the exact search order when looking up a method. It's computed by the **C3 Linearization** algorithm.
>
> `super()` does NOT call "the parent class" — it calls **the next class in the MRO chain**. In multiple inheritance, that may not be the parent at all.

```python
class A:
    def method(self): print("A")

class B(A):
    def method(self):
        print("B")
        super().method()    # calls NEXT in MRO, not necessarily A

class C(A):
    def method(self):
        print("C")
        super().method()

class D(B, C):
    def method(self):
        print("D")
        super().method()

D().method()
# D → B → C → A  (every super() calls the NEXT in this chain)
print([c.__name__ for c in D.__mro__])
# ['D', 'B', 'C', 'A', 'object']
```

> Why this matters: cooperative multiple inheritance only works if every class in the chain calls `super()`. If any class breaks the chain, later classes in the MRO never get called.

---

### Q7: What is the difference between a class variable and an instance variable? What's the notorious trap?

**Weak answer:** "Class variables are shared, instance variables are per-object."

**Strong answer:**

> Class variables live in `ClassName.__dict__`. Instance variables live in each object's own `__dict__`. Reading an attribute first checks the instance dict, then the class dict.

**The Trap:**

```python
class Team:
    members = []      # ← class variable (shared!)
    count   = 0       # ← class variable

    def __init__(self, name):
        self.name = name   # ← instance variable (safe)

t1 = Team("Team A")
t2 = Team("Team B")

# TRAP: mutable class variable is shared across ALL instances!
t1.members.append("Alice")
print(t2.members)    # ['Alice']  ← WRONG! t2 is polluted!

# WHY: t1.members.append() MUTATES the shared list.
# It doesn't create a new list on t1 — it modifies the class-level list.

# CONTRAST: immutable "mutation" (assignment) creates an instance variable:
t1.count = 10         # creates t1's OWN count, shadows class count
print(t2.count)       # 0  ← t2 still sees class-level count
print(Team.count)     # 0  ← class count unchanged

# FIX for the mutable trap: use __init__
class Team:
    def __init__(self, name):
        self.name    = name
        self.members = []   # ← each instance gets its own list
```

---

### Q8: What are dunder methods? Name 5 important ones and explain them.

**Strong answer:**

> Dunder (double underscore) methods are Python's hook into the language's built-in operations. They let your custom objects behave like built-in types.

```python
class Vector:
    def __init__(self, x, y):       # construction
        self.x, self.y = x, y

    def __repr__(self):             # unambiguous string (for devs)
        return f"Vector({self.x}, {self.y})"

    def __str__(self):              # readable string (for users)
        return f"({self.x}, {self.y})"

    def __add__(self, other):       # v1 + v2
        return Vector(self.x + other.x, self.y + other.y)

    def __eq__(self, other):        # v1 == v2
        return self.x == other.x and self.y == other.y

    def __len__(self):              # len(v)
        return int((self.x**2 + self.y**2) ** 0.5)

    def __getitem__(self, idx):     # v[0], v[1]
        return (self.x, self.y)[idx]

    def __contains__(self, val):    # 3 in v
        return val in (self.x, self.y)

    def __bool__(self):             # bool(v)
        return self.x != 0 or self.y != 0


v1 = Vector(3, 4)
v2 = Vector(1, 2)
print(v1 + v2)     # Vector(4, 6)
print(len(v1))     # 5  (magnitude)
print(v1[0])       # 3
print(3 in v1)     # True
```

---

### Q9: When would you use `@property` instead of a plain attribute?

**Weak answer:** "`@property` is for getter and setter."

**Strong answer:**

> Use `@property` when you need:
> 1. **Computed attributes** — value derived from other attributes
> 2. **Validation on write** — enforce constraints when setting
> 3. **Lazy computation** — expensive calculation on first access
> 4. **API backwards compatibility** — replace a public attribute with logic without changing call sites

```python
class Circle:
    def __init__(self, radius):
        self.radius = radius   # calls the setter below

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError(f"Radius must be non-negative, got {value}")
        self._radius = value

    @property
    def area(self):
        return 3.14159 * self._radius ** 2   # computed, no storage needed

    @property
    def diameter(self):
        return self._radius * 2


c = Circle(5)
print(c.area)      # 78.53...  ← computed on the fly
print(c.diameter)  # 10
c.radius = -1      # ← ValueError  (validation enforced)

# The caller syntax stays clean — they just write c.area, c.radius
# They don't know (or care) whether it's stored or computed
```

---

### Q10: What is the difference between `__str__` and `__repr__`?

**Strong answer:**

> `__repr__` should return an **unambiguous** string that could ideally be used to recreate the object (for developers, for debugging).
>
> `__str__` should return a **human-readable** string (for end users, for display).
>
> When you call `print(obj)` → Python uses `__str__`. When you type `obj` in the REPL → Python uses `__repr__`. If only `__repr__` is defined, Python uses it as fallback for `__str__` too.

```python
from datetime import datetime

class Meeting:
    def __init__(self, title, start):
        self.title = title
        self.start = start

    def __repr__(self):
        return f"Meeting(title={self.title!r}, start={self.start!r})"

    def __str__(self):
        return f"{self.title} at {self.start.strftime('%I:%M %p')}"

m = Meeting("Team Sync", datetime(2025, 3, 8, 14, 30))
print(str(m))     # Team Sync at 02:30 PM    ← for users
print(repr(m))    # Meeting(title='Team Sync', start=datetime.datetime(2025, 3, 8, 14, 30))
```

---

### Q11: When should you use composition over inheritance?

**Strong answer:**

> Use inheritance when there is a genuine **IS-A** relationship that remains stable.
> Use composition when:
> - The relationship is **HAS-A** (contains a thing, doesn't define what it IS)
> - The relationship might change at runtime
> - You'd need multiple inheritance to combine behaviours
> - The "parent" class has many methods the "child" doesn't need

```python
# WRONG — inheritance for HAS-A:
class Engine: ...
class Car(Engine): ...   # ← Car IS-A Engine? No. Car HAS-A Engine.

# RIGHT — composition:
class Car:
    def __init__(self, engine: Engine):
        self.engine = engine   # HAS-A relationship

# Composition advantage: swap engines at runtime, mock in tests:
racing_car  = Car(engine=RacingEngine())
electric    = Car(engine=ElectricEngine())
test_car    = Car(engine=MockEngine())
```

---

### Q12: What is a Mixin? How is it different from regular inheritance?

**Strong answer:**

> A Mixin is a class that provides a **specific ability** — not a full identity. It's not meant to be instantiated alone; it's meant to be mixed into other classes via multiple inheritance.

```python
class JSONMixin:
    def to_json(self):
        import json
        return json.dumps(self.__dict__, default=str)

class LogMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._changes = []

    def __setattr__(self, name, value):
        if not name.startswith('_'):
            self._changes.append(f"{name}={value!r}")
        super().__setattr__(name, value)

class User(JSONMixin, LogMixin):
    def __init__(self, name, email):
        super().__init__()
        self.name, self.email = name, email

u = User("Alice", "alice@mail.com")
print(u.to_json())     # {"name": "Alice", "email": "alice@mail.com", "_changes": [...]}
```

> **Key difference:** Inheritance says "what this IS." Mixin says "what this CAN DO." Mixins always come first in the class definition, and every mixin `__init__` MUST call `super().__init__(*args, **kwargs)` for cooperative chaining.

---

## 🔴 Level 3 — Senior Questions

---

### Q13: What are [descriptors](./17_descriptors.md)? How do they work?

**Strong answer:**

> A descriptor is any object that implements `__get__`, `__set__`, or `__delete__`. When a descriptor is placed as a **class attribute**, Python calls these methods instead of doing regular attribute access.

```python
class Positive:
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self          # accessed on class, not instance
        return getattr(obj, self.private_name, None)

    def __set__(self, obj, value):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"{self.name} must be a positive number")
        setattr(obj, self.private_name, value)


class Product:
    price    = Positive()   # descriptor as class attribute
    quantity = Positive()

    def __init__(self, name, price, qty):
        self.name     = name
        self.price    = price     # calls Positive.__set__()
        self.quantity = qty

p = Product("Laptop", 80000, 5)
p.price = -100   # ValueError: price must be a positive number
```

> **Data vs Non-data descriptors:**
> - **Data descriptor** (has `__set__`): takes priority over instance `__dict__`
> - **Non-data descriptor** (only `__get__`): instance `__dict__` wins
>
> This is why `@property` (a data descriptor) can't be bypassed by setting an instance attribute directly.

---

### Q14: Explain [`__slots__`](./15_slots.md). When would you use it?

**Strong answer:**

> Normally, every Python object has a `__dict__` — a dictionary storing all instance attributes. This is flexible but expensive (~200+ bytes overhead per object just for the empty dict).
>
> `__slots__` replaces `__dict__` with fixed C-level slots, dramatically reducing memory usage.

```python
class Regular:
    def __init__(self, x, y): self.x, self.y = x, y

class Slotted:
    __slots__ = ('x', 'y')
    def __init__(self, x, y): self.x, self.y = x, y

import sys
r = Regular(1, 2)
s = Slotted(1, 2)

print(sys.getsizeof(r) + sys.getsizeof(r.__dict__))  # ~280 bytes
print(sys.getsizeof(s))                               # ~56 bytes — 5× smaller!
```

> **When to use:** only when creating millions of instances and memory is a constraint (game entities, trading systems, ML data points).
>
> **Gotcha:** For `__slots__` to be effective, ALL classes in the inheritance chain must define `__slots__`. If any parent lacks it, that parent's `__dict__` still exists.

---

### Q15: What is a Metaclass? Give a real use case.

**Strong answer:**

> Every class in Python is an instance of `type` — the root metaclass. A metaclass is a class that inherits from `type` and customizes how new classes are created (intercepting the class definition itself).

```python
class PluginMeta(type):
    registry = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases:    # skip the base class itself
            mcs.registry[name] = cls
        return cls


class Plugin(metaclass=PluginMeta):
    def run(self): raise NotImplementedError


class AudioPlugin(Plugin):
    def run(self): print("Processing audio")   # auto-registered!


class VideoPlugin(Plugin):
    def run(self): print("Processing video")   # auto-registered!


print(PluginMeta.registry)
# {'AudioPlugin': <class 'AudioPlugin'>, 'VideoPlugin': <class 'VideoPlugin'>}

# Load any plugin by name:
PluginMeta.registry["AudioPlugin"]().run()   # Processing audio
```

> **Rule of thumb:** Try `__init_subclass__` first — it's simpler for 80% of metaclass use cases. Use metaclasses only when you need to deeply modify the class creation process.

---

### Q16: Explain the SOLID principles with Python examples.

**Strong answer:**

> SOLID is five design principles for writing maintainable OOP code:

```
S — Single Responsibility
    Each class has one reason to change.
    UserRepository saves users. EmailService sends emails.
    Not one giant User class that does both.

O — Open/Closed
    Open for extension, closed for modification.
    Add new payment gateways by creating new classes,
    not by editing the existing PaymentProcessor.
    → Use Strategy pattern, ABC subclassing.

L — Liskov Substitution
    Subclasses must be safely substitutable for the parent.
    Any function accepting a Shape should work identically
    whether given a Circle or a Rectangle.
    → Don't raise unexpected errors or ignore parent contracts.

I — Interface Segregation
    Don't force classes to implement methods they don't need.
    RobotWorker should not be forced to implement eat() and sleep().
    → Split fat interfaces into focused small ones.
    → Python's typing.Protocol is perfect for this.

D — Dependency Inversion
    Depend on abstractions, not concrete implementations.
    UserService should accept a Database(ABC), not MySQLDatabase().
    → Dependency Injection: pass the concrete class from outside.
    → This makes testing (with mocks) and swapping easy.
```

---

### Q17: You have a class hierarchy where `super()` seems to call the wrong method. How do you debug this?

**Strong answer:**

> The first step is always to inspect the MRO — Python is transparent about it.

```python
# 1. Print the full MRO:
print([c.__name__ for c in YourClass.__mro__])

# 2. Add debug prints to each super() call:
class B(A):
    def method(self):
        print(f"B.method — next in MRO will be: "
              f"{type(self).__mro__[type(self).__mro__.index(B)+1].__name__}")
        super().method()

# 3. Remember: super() in B doesn't call B's parent — it calls
#    the NEXT class in the MRO of the INSTANCE being used.
#    If D(B, C) and you call D().method():
#      super() in B calls C, not A — because D's MRO is [D, B, C, A]

# 4. Common fix: ensure every class in the chain calls super():
class LogMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   # don't break the chain!
        self._log = []
```

---

## 🔥 Rapid-Fire Revision

```
Q: What does __dunder__ stand for?
A: Double underscore on both sides. Also called "magic methods."

Q: What happens when you access ClassName.attribute?
A: Python returns the class attribute directly, not a descriptor-bound value.
   Descriptor's __get__ is called with obj=None.

Q: What is the difference between @property and a descriptor?
A: @property IS a descriptor — it's a built-in descriptor class.
   Custom descriptors are reusable across many classes; @property is per-class.

Q: Can you call a @staticmethod on an instance?
A: Yes. Python just ignores the instance.

Q: What is __call__?
A: Makes an instance callable like a function: instance(args) → __call__(args).
   Used for function objects, decorators as classes, callable strategies.

Q: How do you make a dataclass immutable?
A: @dataclass(frozen=True) — raises FrozenInstanceError on assignment.

Q: What does NotImplemented (not NotImplementedError) return mean in __eq__?
A: Tells Python: "I can't compare this — try the other operand's __eq__."
   This enables symmetric operations between different types.

Q: What is the MRO of object?
A: (object,) — it's the root of all classes.

Q: What is __init_subclass__ and why is it simpler than metaclasses?
A: Hook called on the parent class whenever a subclass is created.
   Simpler because it's a regular method, no metaclass magic needed.

Q: How does [`@functools.lru_cache`](../04_functions/theory.md#functoolslru_cache--memoization-made-easy) relate to descriptors?
A: lru_cache wraps a function. But on class methods, it can cause issues
   because it caches based on self — which holds a reference, preventing GC.
   Use functools.cached_property instead for instance-level caching.

Q: What is __set_name__?
A: Called on a descriptor when it's assigned in a class body.
   Receives owner (the class) and name (the attribute name).
   Used to auto-capture the attribute name without passing it manually.

Q: When does __new__ need to be overridden?
A: Singletons, immutable types (subclassing str/int/tuple),
   custom object allocation/pooling. Rarely needed in application code.
```

---

## ⚠️ Common Trap Questions

---

### Trap 1 — Mutable Default Class Variable

```python
class Config:
    allowed_users = []   # ← What's wrong?

c1 = Config()
c2 = Config()
c1.allowed_users.append("alice")
print(c2.allowed_users)   # ['alice'] — unexpected!

# WHY: allowed_users is a class variable — shared across all instances.
# append() mutates the shared list, not a per-instance list.

# FIX:
class Config:
    def __init__(self):
        self.allowed_users = []   # ← per-instance now
```

---

### Trap 2 — `isinstance` with Multiple Inheritance

```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass

d = D()
print(isinstance(d, A))    # True  ← d IS-A A through multiple paths
print(isinstance(d, B))    # True
print(isinstance(d, C))    # True

# isinstance() follows the full MRO, so a D instance is an instance
# of every class in its MRO.
```

---

### Trap 3 — `super()` Doesn't Always Call Your Parent

```python
class A:
    def method(self): print("A")

class B(A):
    def method(self):
        print("B")
        super().method()   # What does this call when D().method() is invoked?

class C(A):
    def method(self):
        print("C")
        super().method()

class D(B, C): pass

# MRO of D: [D, B, C, A, object]
# When D().method() → calls B.method()
# super() inside B.method() → calls C.method() (NEXT in D's MRO)
# super() inside C.method() → calls A.method()
D().method()
# B
# C
# A
```

---

### Trap 4 — Property Recursion

```python
class Circle:
    @property
    def radius(self):
        return self.radius   # ← RecursionError! calls itself infinitely!

    @radius.setter
    def radius(self, value):
        self.radius = value   # ← Same trap! calls setter forever!

# FIX: use a private backing attribute:
class Circle:
    @property
    def radius(self):
        return self._radius    # ← underscore = backing store

    @radius.setter
    def radius(self, value):
        self._radius = value   # ← write to backing store, not to property
```

---

### Trap 5 — `__eq__` Without `__hash__`

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    # ← No __hash__ defined!

p = Point(1, 2)
# Python automatically sets __hash__ = None when __eq__ is defined
# without __hash__.
# This means Point objects are UNHASHABLE:
s = {p}    # TypeError: unhashable type: 'Point'

# FIX: define __hash__ too:
class Point:
    def __init__(self, x, y): self.x, self.y = x, y
    def __eq__(self, other): return self.x == other.x and self.y == other.y
    def __hash__(self): return hash((self.x, self.y))
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Index | [README.md](./README.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🏠 Home | [python-complete-mastery](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Exceptions Error Handling — Theory →](../06_exceptions_error_handling/theory.md)

**Related Topics:** [Why Oop](./01_why_oop.md) · [Classes And Objects](./02_classes_and_objects.md) · [Init And Self](./03_init_and_self.md) · [Encapsulation](./04_encapsulation.md) · [Inheritance](./05_inheritance.md) · [Polymorphism](./06_polymorphism.md) · [Abstraction](./07_abstraction.md) · [Dunder Methods](./08_dunder_methods.md) · [Class Instance Static Methods](./09_class_instance_static_methods.md) · [Class Vs Instance Variables](./10_class_vs_instance_variables.md) · [Properties](./11_properties.md) · [Theory Part 1](./theory_part1.md) · [Composition Vs Inheritance](./12_composition_vs_inheritance.md) · [Theory Part 2](./theory_part2.md) · [Mro And Super](./13_mro_and_super.md) · [Theory Part 3](./theory_part3.md) · [Dataclasses](./14_dataclasses.md) · [Slots](./15_slots.md) · [Metaclasses](./16_metaclasses.md) · [Descriptors](./17_descriptors.md) · [Mixins](./18_mixins.md) · [Solid Principles](./19_solid_principles.md) · [Cheat Sheet](./cheatsheet.md)
