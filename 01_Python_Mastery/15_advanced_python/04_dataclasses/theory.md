# Dataclasses — Deep Dive

Imagine having to write `__init__`, `__repr__`, and `__eq__` for every data container in your codebase — ten lines of boilerplate per class, every class. `@dataclass` is Python's answer: **declare fields once, get the boilerplate for free**. It's not magic — it generates those methods at class-definition time using Python's own dunder protocol.

> Key fact: `@dataclass` is a class decorator (Python 3.7+) that inspects your field annotations and injects `__init__`, `__repr__`, and `__eq__` at class creation time. No inheritance required.

---

## Learning Priority

**Must Learn:** `@dataclass` · `field()` · `__post_init__` · `frozen=True` · `slots=True`

**Should Learn:** `ordering` (`order=True`) · `ClassVar` · `InitVar` · inheritance

**Good to Know:** `@dataclass(eq=False)` · `default_factory` · `asdict` / `astuple`

**Reference:** `dataclasses.fields()` · `make_dataclass()`

---

## Chapter 1: Basic `@dataclass`

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

# What @dataclass generated:
# def __init__(self, x: float, y: float):
#     self.x = x
#     self.y = y
# def __repr__(self): return f"Point(x={self.x!r}, y={self.y!r})"
# def __eq__(self, other): return (self.x, self.y) == (other.x, other.y) if isinstance(other, Point) else NotImplemented

p1 = Point(1.0, 2.0)
p2 = Point(1.0, 2.0)
print(p1)           # Point(x=1.0, y=2.0)
print(p1 == p2)     # True
```

**Decorator flags:**

```python
@dataclass(
    init=True,       # generate __init__
    repr=True,       # generate __repr__
    eq=True,         # generate __eq__
    order=False,     # generate __lt__, __le__, __gt__, __ge__
    frozen=False,    # make immutable (generates __setattr__/__delattr__ that raise)
    slots=False,     # generate __slots__ (Python 3.10+)
    kw_only=False,   # all fields keyword-only
)
class MyClass:
    ...
```

---

## Chapter 2: `field()` — Fine-Grained Control

```python
from dataclasses import dataclass, field
from typing import ClassVar

@dataclass
class Student:
    name: str
    grade: int

    # Mutable defaults MUST use field(default_factory=...) — not a raw list!
    subjects: list[str] = field(default_factory=list)   # ← new list per instance

    # Excluded from repr:
    _password_hash: str = field(default="", repr=False)

    # Excluded from comparison:
    created_at: float = field(default=0.0, compare=False)

    # ClassVar is NOT a dataclass field — not included in __init__:
    student_count: ClassVar[int] = 0

    # field(init=False) — not a parameter, set in __post_init__:
    full_label: str = field(init=False)

    def __post_init__(self):
        type(self).student_count += 1
        self.full_label = f"Grade {self.grade}: {self.name}"  # ← computed field

# IMPORTANT: never use mutable default directly:
# @dataclass
# class Bad:
#     items: list = []   # ValueError: mutable default not allowed
```

**`field()` parameters:**

```
Parameter           Purpose
------------------------------------------------------------
default             simple default value
default_factory     callable that returns the default (for mutables)
repr                include in __repr__ (default True)
compare             include in __eq__ and ordering (default True)
hash                include in __hash__ (default None = follow compare)
init                include as __init__ parameter (default True)
metadata            arbitrary read-only mapping for tools/libraries
```

---

## Chapter 3: `__post_init__` — Validation and Derived Fields

`__post_init__` is called automatically at the end of the generated `__init__`. Use it for validation and computing derived fields.

```python
import math

@dataclass
class BoundingBox:
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    # Computed fields — not in __init__:
    width:  float = field(init=False)
    height: float = field(init=False)
    area:   float = field(init=False)

    def __post_init__(self):
        if self.x_min > self.x_max or self.y_min > self.y_max:
            raise ValueError("min must be <= max")
        self.width  = self.x_max - self.x_min
        self.height = self.y_max - self.y_min
        self.area   = self.width * self.height

box = BoundingBox(0, 0, 10, 10)
print(box.area)   # 100.0
```

**`InitVar`** — a parameter to `__init__` that is NOT stored as a field:

```python
from dataclasses import dataclass, field
from dataclasses import InitVar

@dataclass
class DatabaseConfig:
    host: str
    port: int
    # InitVar: passed to __init__ and __post_init__, but not stored:
    password_env_var: InitVar[str] = "DB_PASSWORD"
    password: str = field(init=False, repr=False)

    def __post_init__(self, password_env_var: str):
        import os
        self.password = os.environ.get(password_env_var, "")
```

---

## Chapter 4: `frozen=True` — Immutable Dataclasses

```python
@dataclass(frozen=True)
class Color:
    r: int = 0
    g: int = 0
    b: int = 0

    def __post_init__(self):
        for name, val in [("r", self.r), ("g", self.g), ("b", self.b)]:
            if not (0 <= val <= 255):
                raise ValueError(f"{name} must be 0-255")

    def to_hex(self):
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    def blend(self, other, factor=0.5):
        # frozen=True → can't modify in place, must return new instance
        return Color(
            r=int(self.r * (1-factor) + other.r * factor),
            g=int(self.g * (1-factor) + other.g * factor),
            b=int(self.b * (1-factor) + other.b * factor),
        )

RED  = Color(255, 0, 0)
BLUE = Color(0, 0, 255)

print(RED.to_hex())         # #ff0000
print(hash(RED))            # works! frozen → __hash__ generated
palette = {RED, BLUE}       # can be used in sets

try:
    RED.r = 100             # raises FrozenInstanceError
except Exception as e:
    print(type(e).__name__)
```

**Creating modified copies of frozen instances** — use `dataclasses.replace()`:

```python
from dataclasses import replace

cfg = Config(host="localhost", port=8080)
cfg2 = replace(cfg, port=443)   # ← returns new instance with port changed
print(cfg.port)   # 8080  — original unchanged
print(cfg2.port)  # 443
```

---

## Chapter 5: `order=True` — Sortable Dataclasses

```python
@dataclass(order=True)
class Priority:
    # Fields compared IN ORDER they are declared (left to right):
    level:   int     # 1 = highest
    created: float

    # compare=False — excluded from ordering:
    description: str = field(compare=False)

tasks = [
    Priority(2, 1000.0, "Write docs"),
    Priority(1, 2000.0, "Fix critical bug"),
    Priority(2,  500.0, "Update config"),
    Priority(1, 1500.0, "Deploy hotfix"),
]

for t in sorted(tasks):
    print(f"  [{t.level}] {t.description}")
# [1] Deploy hotfix   (level=1, created=1500)
# [1] Fix critical bug (level=1, created=2000)
# [2] Update config   (level=2, created=500)
# [2] Write docs      (level=2, created=1000)
```

---

## Chapter 6: `ClassVar` and `InitVar`

```
ClassVar[T]   — class variable, NOT a dataclass field, NOT in __init__
InitVar[T]    — passed to __init__ and __post_init__, but NOT stored as field
```

```python
from typing import ClassVar
from dataclasses import dataclass, field, InitVar

@dataclass
class Employee:
    name: str
    salary: float

    # Class variable — shared across all instances, not per-instance:
    company: ClassVar[str] = "Acme Corp"

    # InitVar — only needed during construction:
    tax_rate: InitVar[float] = 0.3
    net_salary: float = field(init=False)

    def __post_init__(self, tax_rate: float):
        self.net_salary = self.salary * (1 - tax_rate)

e = Employee("Alice", 100000.0, tax_rate=0.35)
print(e.net_salary)        # 65000.0
print(Employee.company)    # "Acme Corp"
# note: tax_rate is NOT stored on the instance
```

---

## Chapter 7: Inheritance

```python
@dataclass
class Shape:
    color: str = "black"
    visible: bool = True

@dataclass
class Circle(Shape):
    radius: float = 0.0   # ← added after parent fields

    def __post_init__(self):
        if self.radius < 0:
            raise ValueError("Radius cannot be negative")

    def area(self):
        import math; return math.pi * self.radius ** 2

c = Circle(color="red", radius=5.0)
print(c)   # Circle(color='red', visible=True, radius=5.0)
```

**Inheritance rule** — all fields with defaults must come after fields without defaults. This means if a parent has any field with a default, ALL child fields must also have defaults.

```python
@dataclass
class Base:
    name: str       # no default
    tag: str = ""   # has default

@dataclass
class Child(Base):
    value: int = 0  # must have default (because Base.tag has one)
    # value: int    # ← TypeError: non-default argument 'value' follows default argument
```

---

## Chapter 8: `slots=True` — Memory Savings (Python 3.10+)

```python
@dataclass(slots=True)   # Python 3.10+
class FastPoint:
    x: float
    y: float

fp = FastPoint(1.0, 2.0)
print(FastPoint.__slots__)   # ('x', 'y')
# No __dict__ — more compact, faster attribute access
```

On Python 3.9 and earlier, add `__slots__` manually (but cannot combine with class-level defaults for mutable fields):

```python
@dataclass
class ManualSlots:
    __slots__ = ('x', 'y')
    x: float
    y: float
    # Note: field() with default doesn't work directly with manual __slots__
    # Use @dataclass(slots=True) on 3.10+ for the clean version
```

---

## Chapter 9: Utility Functions — `asdict`, `astuple`, `replace`, `fields`

```python
from dataclasses import asdict, astuple, replace, fields
import json

@dataclass
class Address:
    street: str
    city: str
    country: str = "US"

@dataclass
class Person:
    name: str
    age: int
    address: Address

person = Person("Alice", 30, Address("123 Main St", "Springfield"))

# asdict — recursively converts to nested dict:
d = asdict(person)
print(json.dumps(d, indent=2))
# {"name": "Alice", "age": 30, "address": {"street": "123 Main St", ...}}

# astuple — recursively converts to nested tuple:
t = astuple(person)
print(t)   # ('Alice', 30, ('123 Main St', 'Springfield', 'US'))

# replace — create modified copy:
older = replace(person, age=31)
print(older)        # Person(name='Alice', age=31, ...)
print(person.age)   # 30 — original unchanged

# fields() — inspect field metadata:
for f in fields(Person):
    print(f"  {f.name}: {f.type}")
```

---

## Common Mistakes

**Mutable default — always raises `ValueError`:**
```python
@dataclass
class Bad:
    items: list = []        # ValueError!
    data: dict = {}         # ValueError!

@dataclass
class Good:
    items: list = field(default_factory=list)   # ← correct
    data: dict  = field(default_factory=dict)   # ← correct
```

**Modifying frozen instance fields in `__post_init__`:**
```python
@dataclass(frozen=True)
class Frozen:
    x: float
    y: float
    magnitude: float = field(init=False)

    def __post_init__(self):
        # self.magnitude = ...   # ← FrozenInstanceError!
        object.__setattr__(self, 'magnitude', (self.x**2 + self.y**2)**0.5)  # ← use this
```

**`order=True` without `eq=True`** — requires `eq=True` (default) — order without equality makes no sense.

**`ClassVar` fields don't appear in `asdict()` / `astuple()` / `fields()` — this is correct behavior** but can surprise you if you expect them.

---

## Navigation

| | |
|---|---|
| Root theory | [../theory.md](../theory.md) |
| Root practice | [../practice.md](../practice.md) |
| Practice | [practice.md](./practice.md) |
| Prev: Metaclasses | [../03_metaclasses/theory.md](../03_metaclasses/theory.md) |
| Next: Advanced Patterns | [../05_advanced_patterns/theory.md](../05_advanced_patterns/theory.md) |

**[Back to 15_advanced_python](../theory.md)**
