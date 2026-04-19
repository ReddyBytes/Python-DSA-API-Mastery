# 📦 14 — Dataclasses: Modern Python OOP

> *"Dataclasses eliminate the boilerplate.*
> *You describe what your data looks like — Python writes the plumbing."*

---

## 🎬 The Story

Every time you build a class to hold data, you write the same patterns:
```python
class User:
    def __init__(self, name, email, age):
        self.name  = name
        self.email = email
        self.age   = age

    def __repr__(self):
        return f"User(name={self.name!r}, email={self.email!r}, age={self.age!r})"

    def __eq__(self, other):
        return (self.name, self.email, self.age) == (other.name, other.email, other.age)
```

You write this for every data class. 15 lines of boilerplate. Always the same.

With `@dataclass`:
```python
from dataclasses import dataclass

@dataclass
class User:
    name:  str
    email: str
    age:   int
```

4 lines. Python auto-generates `__init__`, `__repr__`, and `__eq__`.

---

## 🔧 The Basics

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

p1 = Point(1.0, 2.0)
p2 = Point(1.0, 2.0)
p3 = Point(3.0, 4.0)

print(p1)            # Point(x=1.0, y=2.0)   ← __repr__ auto-generated
print(p1 == p2)      # True                   ← __eq__ auto-generated
print(p1 == p3)      # False
print(p1.x)          # 1.0
```

**What `@dataclass` auto-generates:**

| Method | What it does |
|--------|-------------|
| `__init__` | Takes all fields as parameters |
| `__repr__` | Returns `ClassName(field=value, ...)` |
| `__eq__` | Compares all fields for equality |

---

## ⚙️ Default Values

```python
from dataclasses import dataclass, field

@dataclass
class Product:
    name:     str
    price:    float
    category: str   = "General"       # simple default
    in_stock: bool  = True

p1 = Product("Laptop", 80000)
p2 = Product("Pen", 20, "Stationery", True)

print(p1)    # Product(name='Laptop', price=80000, category='General', in_stock=True)
print(p2)    # Product(name='Pen', price=20, category='Stationery', in_stock=True)
```

### ⚠️ Mutable Default — Use `field(default_factory=...)`

You cannot use mutable objects (list, dict, set) as direct defaults.
Python would share one instance across all objects — the same [mutable default trap](../04_functions/theory.md#️-type-3-edge-case--the-mutable-default-argument-trap)!

```python
from dataclasses import dataclass, field

# ❌ This raises a TypeError:
@dataclass
class Cart:
    items: list = []    # ValueError: mutable default not allowed

# ✅ Use field(default_factory=...):
@dataclass
class Cart:
    items: list = field(default_factory=list)    # creates new [] for each instance
    tags:  dict = field(default_factory=dict)    # creates new {} for each instance

c1 = Cart()
c2 = Cart()
c1.items.append("apple")
print(c1.items)    # ['apple']
print(c2.items)    # []   ← independent list!
```

---

## 🔒 Frozen Dataclasses (Immutable)

`frozen=True` makes the dataclass immutable — like a tuple with named fields.

```python
@dataclass(frozen=True)
class Coordinates:
    lat: float
    lon: float

c = Coordinates(28.6139, 77.2090)
print(c)           # Coordinates(lat=28.6139, lon=77.2090)

# c.lat = 0.0    # ← FrozenInstanceError: cannot assign to field 'lat'

# Frozen dataclasses are HASHABLE — can be used as dict keys or in sets!
locations = {
    Coordinates(28.6139, 77.2090): "New Delhi",
    Coordinates(19.0760, 72.8777): "Mumbai",
}
print(locations[Coordinates(28.6139, 77.2090)])    # "New Delhi"
```

---

## 📊 Ordering (`order=True`)

`order=True` generates `__lt__`, `__le__`, `__gt__`, `__ge__` based on field order.

```python
@dataclass(order=True)
class Student:
    gpa:  float         # compared first (first field)
    name: str           # compared second if gpa is equal

students = [
    Student(8.5, "Charlie"),
    Student(9.2, "Alice"),
    Student(8.9, "Bob"),
]

print(sorted(students))
# [Student(gpa=8.5, name='Charlie'), Student(gpa=8.9, name='Bob'), Student(gpa=9.2, name='Alice')]

# For specific sort field — exclude from comparison with field(compare=False):
@dataclass(order=True)
class Employee:
    sort_index: float = field(init=False, repr=False)
    name:       str   = field(compare=False)
    salary:     float

    def __post_init__(self):
        self.sort_index = self.salary    # sort by salary
```

---

## 🔁 `__post_init__` — Validation and Derived Fields

`__post_init__` runs automatically after `__init__`. Use it for validation or computing derived attributes.

```python
import math
from dataclasses import dataclass, field

@dataclass
class Circle:
    radius: float
    area:   float = field(init=False, repr=True)   # not passed in, auto-computed

    def __post_init__(self):
        if self.radius < 0:
            raise ValueError(f"Radius cannot be negative: {self.radius}")
        self.area = math.pi * self.radius ** 2    # compute derived field

c = Circle(5)
print(c)           # Circle(radius=5, area=78.53981633974483)
print(c.area)      # 78.53...

# Circle(-1)       # ← ValueError: Radius cannot be negative
```

---

## 🎛️ `field()` — Fine-Grained Control

```python
from dataclasses import dataclass, field

@dataclass
class Config:
    host:     str
    port:     int  = 8080
    secret:   str  = field(default="", repr=False)   # hidden in repr
    _id:      int  = field(default=0, init=False)     # not in __init__
    tags:     list = field(default_factory=list)      # mutable default
    metadata: dict = field(default_factory=dict, compare=False)  # skip in ==

c = Config("localhost")
print(c)
# Config(host='localhost', port=8080, _id=0, tags=[])
# Notice: secret is hidden (repr=False)
```

**`field()` parameters:**

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `default` | MISSING | Default value |
| `default_factory` | MISSING | Callable to create default |
| `init` | True | Include in `__init__`? |
| `repr` | True | Include in `__repr__`? |
| `compare` | True | Include in `__eq__` and ordering? |
| `hash` | None | Include in `__hash__`? |

---

## 🧬 Inheritance With Dataclasses

```python
@dataclass
class Person:
    name: str
    age:  int

@dataclass
class Employee(Person):
    department: str
    salary:     float

emp = Employee("Alice", 30, "Engineering", 90000)
print(emp)    # Employee(name='Alice', age=30, department='Engineering', salary=90000)
print(emp.name)     # Alice  ← from Person
print(emp.salary)   # 90000  ← from Employee
```

> **Gotcha with inheritance:** If the parent has fields with defaults, the child cannot have fields without defaults (same rule as regular `__init__`).

```python
@dataclass
class Parent:
    name: str
    role: str = "user"

@dataclass
class Child(Parent):
    # age: int   ← TypeError! Non-default field 'age' after default field 'role'
    level: int = 1    # must also have default
```

---

## 🆚 Dataclass vs NamedTuple vs Regular Class

```
┌─────────────────────────────────────────────────────────────────────┐
│             COMPARISON                                               │
├─────────────────┬──────────────┬──────────────┬────────────────────┤
│  Feature        │  @dataclass  │  NamedTuple  │  Regular Class     │
├─────────────────┼──────────────┼──────────────┼────────────────────┤
│  Mutable        │  Yes         │  No          │  Yes               │
│  Hashable       │  No*         │  Yes         │  No*               │
│  auto __init__  │  Yes         │  Yes         │  No                │
│  auto __repr__  │  Yes         │  Yes         │  No                │
│  auto __eq__    │  Yes         │  Yes (tuple) │  No                │
│  Validation     │  __post_init__│ No          │  __init__          │
│  Ordering       │  opt-in      │  tuple-based │  manual            │
│  Inheritance    │  Yes         │  Limited     │  Full              │
│  Frozen         │  Yes         │  Always      │  Manual            │
└─────────────────┴──────────────┴──────────────┴────────────────────┘
* Unless frozen=True (dataclass) or defined explicitly
```

---

## 🎯 Key Takeaways

```
• @dataclass auto-generates __init__, __repr__, __eq__
• frozen=True → immutable + hashable (usable as dict key or in set)
• order=True → auto-generates comparison operators
• Mutable defaults MUST use field(default_factory=...)
• __post_init__ → validation and derived fields after __init__
• field(repr=False) → hide sensitive data from repr
• field(init=False) → computed/injected fields, not from constructor
• Dataclasses work with inheritance but mind the default ordering rule
• Use @dataclass for data containers, not for complex business logic
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [13 — MRO & super()](./13_mro_and_super.md) |
| 📖 Index | [README.md](./README.md) |
| ➡️ Next | [15 — `__slots__`](./15_slots.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory Part 3](./theory_part3.md) &nbsp;|&nbsp; **Next:** [Slots →](./15_slots.md)

**Related Topics:** [Why Oop](./01_why_oop.md) · [Classes And Objects](./02_classes_and_objects.md) · [Init And Self](./03_init_and_self.md) · [Encapsulation](./04_encapsulation.md) · [Inheritance](./05_inheritance.md) · [Polymorphism](./06_polymorphism.md) · [Abstraction](./07_abstraction.md) · [Dunder Methods](./08_dunder_methods.md) · [Class Instance Static Methods](./09_class_instance_static_methods.md) · [Class Vs Instance Variables](./10_class_vs_instance_variables.md) · [Properties](./11_properties.md) · [Theory Part 1](./theory_part1.md) · [Composition Vs Inheritance](./12_composition_vs_inheritance.md) · [Theory Part 2](./theory_part2.md) · [Mro And Super](./13_mro_and_super.md) · [Theory Part 3](./theory_part3.md) · [Slots](./15_slots.md) · [Metaclasses](./16_metaclasses.md) · [Descriptors](./17_descriptors.md) · [Mixins](./18_mixins.md) · [Solid Principles](./19_solid_principles.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
