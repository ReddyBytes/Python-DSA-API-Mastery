# Practice — Dataclasses

| Q | Difficulty | Topic |
|---|-----------|-------|
| [Q1](#q1--basic-dataclass) | 🟢 | Basic `@dataclass` with defaults |
| [Q2](#q2--frozen) | 🟢 | `frozen=True` — make immutable |
| [Q3](#q3--default-factory) | 🟡 | `field()` with `default_factory` |
| [Q4](#q4--post_init) | 🟡 | `__post_init__` — derive fields |
| [Q5](#q5--ordering) | 🟡 | `order=True` — sortable instances |
| [Q6](#q6--classvar-and-initvar) | 🟡 | `ClassVar` and `InitVar` |
| [Q7](#q7--inheritance) | 🟡 | Subclass a dataclass |
| [Q8](#q8--slots) | 🟠 | `slots=True` — memory savings |
| [Q9](#q9--asdict-and-astuple) | 🟠 | `asdict()` and `astuple()` |
| [Q10](#q10--capstone) | 🟠 | Capstone: config system with validation |

---

### Q1 🟢 · basics — basic `@dataclass` with 3 fields and default values

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

**Problem:** Create a `Product` dataclass with `name: str`, `price: float`, and `in_stock: bool = True`. Demonstrate auto-generated `__init__`, `__repr__`, and `__eq__`.

<details>
<summary>💡 Hint</summary>
Just add `@dataclass` and declare fields with type annotations. Fields with defaults must come after fields without defaults. You get `__init__`, `__repr__`, and `__eq__` for free.
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass

@dataclass
class Product:
    name:     str
    price:    float
    in_stock: bool = True

p1 = Product("Widget", 9.99)
p2 = Product("Widget", 9.99)
p3 = Product("Gadget", 29.99, in_stock=False)

print(p1)           # Product(name='Widget', price=9.99, in_stock=True)
print(p1 == p2)     # True   — field-by-field comparison (auto __eq__)
print(p1 == p3)     # False
print(p1.name)      # Widget
print(p3.in_stock)  # False
```

**Why:** `@dataclass` generates `__init__` from field declarations, `__repr__` showing all fields, and `__eq__` comparing fields in order. Without it, you'd write ~15 lines of boilerplate.
</details>

---

### Q2 🟢 · immutability — `frozen=True` — make immutable, try to modify

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

**Problem:** Create a `Coordinate` dataclass with `lat: float` and `lon: float`, frozen. Demonstrate that it's hashable (can be in a set), and that attempting to modify it raises `FrozenInstanceError`.

<details>
<summary>💡 Hint</summary>
`frozen=True` generates `__setattr__` and `__delattr__` that raise `FrozenInstanceError`. It also generates `__hash__` based on the fields (since the object is immutable).
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Coordinate:
    lat: float
    lon: float

c1 = Coordinate(51.5074, -0.1278)   # London
c2 = Coordinate(48.8566,  2.3522)   # Paris

# frozen=True → __hash__ generated → can use in set/dict
visited = {c1, c2}
cache = {c1: "London", c2: "Paris"}
print(cache[Coordinate(51.5074, -0.1278)])  # London — same hash+eq

# Attempt to modify:
try:
    c1.lat = 0.0
except Exception as e:
    print(type(e).__name__, e)   # FrozenInstanceError: cannot assign to field 'lat'
```

**Why:** `frozen=True` makes instances immutable and automatically adds `__hash__`. Mutable dataclasses (default) do NOT get `__hash__` because mutable objects shouldn't be hashable.
</details>

---

### Q3 🟡 · defaults — `field()` with `default_factory` for mutable defaults

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

**Problem:** Create a `Task` dataclass with `title: str`, `tags: list[str]` defaulting to an empty list, and `metadata: dict` defaulting to an empty dict. Show that each instance gets its own list/dict (not shared).

<details>
<summary>💡 Hint</summary>
Using `tags: list = []` raises `ValueError`. Use `field(default_factory=list)` instead. This calls `list()` for each new instance.
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass, field

@dataclass
class Task:
    title:    str
    tags:     list[str] = field(default_factory=list)   # ← new list each time
    metadata: dict      = field(default_factory=dict)   # ← new dict each time

t1 = Task("Build feature")
t2 = Task("Write tests")

t1.tags.append("backend")
t2.tags.append("testing")

print(t1.tags)    # ['backend']
print(t2.tags)    # ['testing']  — NOT shared!

# Prove they're different objects:
print(t1.tags is t2.tags)   # False
```

**Why:** Python evaluates default values once at class definition time. A raw `[]` would be shared across all instances. `default_factory=list` creates a fresh list for each instance.
</details>

---

### Q4 🟡 · computed fields — `__post_init__` to derive a field from others

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

**Problem:** Create a `Rectangle` dataclass with `width` and `height`. Use `__post_init__` to compute `area` and `perimeter` as derived fields (use `field(init=False)`). Validate that width and height are positive.

<details>
<summary>💡 Hint</summary>
`field(init=False)` means the field is NOT in `__init__` — it gets set in `__post_init__`. `__post_init__` runs at the end of the auto-generated `__init__`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass, field

@dataclass
class Rectangle:
    width:     float
    height:    float
    area:      float = field(init=False, repr=False)
    perimeter: float = field(init=False, repr=False)

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")
        self.area      = self.width * self.height
        self.perimeter = 2 * (self.width + self.height)

r = Rectangle(4.0, 5.0)
print(r)            # Rectangle(width=4.0, height=5.0)  — area/perimeter repr=False
print(r.area)       # 20.0
print(r.perimeter)  # 18.0

try:
    Rectangle(-1, 5)  # ValueError
except ValueError as e:
    print(e)
```

**Why:** `field(init=False)` keeps derived values out of the constructor signature (callers don't pass them) while still storing them as instance attributes. `__post_init__` is the right place for computed fields and validation.
</details>

---

### Q5 🟡 · sorting — `order=True` to sort a list of dataclass instances

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

**Problem:** Create a `Task` dataclass with `priority: int`, `created_at: float`, and `title: str`. Use `order=True`. Mark `title` with `field(compare=False)` so sorting ignores it. Sort a list of tasks.

<details>
<summary>💡 Hint</summary>
`order=True` generates `__lt__`, `__le__`, `__gt__`, `__ge__` based on fields in declaration order (fields with `compare=False` are excluded). Lower `priority` integer should sort first.
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass, field

@dataclass(order=True)
class Task:
    priority:   int     # compared first (lower = more urgent)
    created_at: float   # compared second (earlier = higher priority within same level)
    title:      str = field(compare=False)   # not used in comparisons

tasks = [
    Task(2, 1000.0, "Write docs"),
    Task(1, 2000.0, "Fix critical bug"),
    Task(2,  500.0, "Update config"),
    Task(1, 1500.0, "Deploy hotfix"),
]

for t in sorted(tasks):
    print(f"  [P{t.priority}] {t.title}")
# [P1] Deploy hotfix   (priority=1, created=1500)
# [P1] Fix critical bug (priority=1, created=2000)
# [P2] Update config   (priority=2, created=500)
# [P2] Write docs      (priority=2, created=1000)
```

**Why:** `order=True` makes instances work with `sorted()`, `min()`, `max()`, and `heapq`. Fields are compared left to right in declaration order — so field order matters.
</details>

---

### Q6 🟡 · special fields — `ClassVar` and `InitVar`

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

**Problem:** Create an `Employee` dataclass with `name: str`, `salary: float`, a `ClassVar[str]` called `company` (shared class-level attribute), and an `InitVar[float]` called `tax_rate`. Compute `net_salary` in `__post_init__` using `tax_rate`.

<details>
<summary>💡 Hint</summary>
`ClassVar` is excluded from `__init__`, `__repr__`, `__eq__`. `InitVar` appears in `__init__` and `__post_init__` but is NOT stored on the instance.
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass, field, InitVar
from typing import ClassVar

@dataclass
class Employee:
    name:       str
    salary:     float
    company:    ClassVar[str] = "Acme Corp"    # class variable, not a field
    tax_rate:   InitVar[float] = 0.30          # init param only, not stored
    net_salary: float = field(init=False, repr=False)

    def __post_init__(self, tax_rate: float):
        self.net_salary = self.salary * (1 - tax_rate)

e1 = Employee("Alice", 100_000.0, tax_rate=0.35)
e2 = Employee("Bob",   80_000.0)   # uses default tax_rate=0.30

print(e1)                     # Employee(name='Alice', salary=100000.0)
print(e1.net_salary)          # 65000.0
print(e2.net_salary)          # 56000.0
print(Employee.company)       # Acme Corp

# tax_rate is NOT stored on the instance:
print(hasattr(e1, 'tax_rate'))  # False
```

**Why:** `ClassVar` signals "this is a class attribute, not a per-instance field". `InitVar` signals "I need this during construction but don't store it". Both help type checkers understand your intent.
</details>

---

### Q7 🟡 · inheritance — subclass a dataclass

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

**Problem:** Create a base `Animal` dataclass with `name: str` and `weight: float`. Create a `Dog` subclass that adds `breed: str`. Verify that the auto-generated `__init__` includes all fields from both classes.

<details>
<summary>💡 Hint</summary>
Fields from parent classes come first in the generated `__init__`. All child fields that have no default must come before fields with defaults in the combined signature.
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass

@dataclass
class Animal:
    name:   str
    weight: float

@dataclass
class Dog(Animal):
    breed: str   # added after parent fields in __init__

    def speak(self):
        return f"Woof! I'm {self.name}"

d = Dog(name="Rex", weight=30.0, breed="Husky")
print(d)            # Dog(name='Rex', weight=30.0, breed='Husky')
print(d.speak())    # Woof! I'm Rex

# __init__ signature: (name, weight, breed) — parent fields first
import inspect
print(inspect.signature(Dog.__init__))   # (self, name: str, weight: float, breed: str)
```

**Why:** Dataclass inheritance works naturally. Parent fields come first in `__init__`. The inheritance rule: if a parent field has a default, all child fields must also have defaults (to avoid non-default-after-default errors).
</details>

---

### Q8 🟠 · memory — `slots=True` memory savings (Python 3.10+)

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

**Problem:** Create two versions of a `Particle` dataclass — with and without `slots=True`. Compare memory usage for 100,000 instances using `sys.getsizeof`.

<details>
<summary>💡 Hint</summary>
`@dataclass(slots=True)` requires Python 3.10+. For the `__dict__` version, total size includes `sys.getsizeof(obj) + sys.getsizeof(obj.__dict__)`. Slots version has no `__dict__`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import sys
from dataclasses import dataclass

@dataclass
class ParticleDict:
    x: float
    y: float
    z: float

try:
    @dataclass(slots=True)
    class ParticleSlots:
        x: float
        y: float
        z: float

    p1 = ParticleDict(1.0, 2.0, 3.0)
    p2 = ParticleSlots(1.0, 2.0, 3.0)

    size_dict  = sys.getsizeof(p1) + sys.getsizeof(p1.__dict__)
    size_slots = sys.getsizeof(p2)

    print(f"With __dict__: {size_dict} bytes")
    print(f"With __slots__: {size_slots} bytes")
    print(f"Savings: {size_dict - size_slots} bytes ({(size_dict-size_slots)/size_dict*100:.0f}%)")

    print(f"Has __slots__: {hasattr(ParticleSlots, '__slots__')}")
    print(f"Slots: {ParticleSlots.__slots__}")

except TypeError:
    print("@dataclass(slots=True) requires Python 3.10+")
    print("On older Python, add __slots__ manually.")
```

**Why:** `slots=True` removes the `__dict__` overhead. For classes instantiated millions of times (particles, events, records), this can save 3-5x memory and improve attribute access speed.
</details>

---

### Q9 🟠 · conversion — `asdict()` and `astuple()` convert to plain Python types

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

**Problem:** Create nested dataclasses `Address` (street, city, country) and `Person` (name, age, address). Use `asdict()` to convert to a JSON-serializable dict and `astuple()` for tuple form. Also demonstrate `replace()`.

<details>
<summary>💡 Hint</summary>
`asdict()` and `astuple()` are recursive — nested dataclasses become nested dicts/tuples. `replace()` creates a modified copy (important for `frozen=True` instances).
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass, asdict, astuple, replace
import json

@dataclass
class Address:
    street:  str
    city:    str
    country: str = "US"

@dataclass
class Person:
    name:    str
    age:     int
    address: Address

person = Person("Alice", 30, Address("123 Main St", "Springfield"))

# asdict — recursively converts nested dataclasses to dicts:
d = asdict(person)
print(json.dumps(d, indent=2))
# {"name": "Alice", "age": 30, "address": {"street": "123 Main St", ...}}

# astuple — recursively converts to nested tuples:
t = astuple(person)
print(t)   # ('Alice', 30, ('123 Main St', 'Springfield', 'US'))

# replace — create modified copy:
older = replace(person, age=31)
moved = replace(person, address=replace(person.address, city="Shelbyville"))
print(older)         # Person(name='Alice', age=31, ...)
print(person.age)    # 30 — original unchanged
```

**Why:** `asdict()` is the standard way to serialize dataclasses to JSON. `replace()` is essential for frozen instances (can't modify in place) and for functional-style "update" patterns.
</details>

---

### Q10 🟠 · capstone — dataclass-based config system with validation

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

**Problem:** Build a `ServerConfig` frozen dataclass with `host: str`, `port: int`, `debug: bool = False`, and `allowed_origins: tuple[str, ...] = ()`. Validate in `__post_init__` that port is 1-65535 and host is non-empty. Add a `with_port(new_port)` method using `replace()`. Make it JSON-serializable via `asdict()`.

<details>
<summary>💡 Hint</summary>
Use `tuple` (not `list`) for `allowed_origins` since the dataclass is frozen. Use `object.__setattr__` if you need to set computed fields inside `__post_init__` of a frozen dataclass.
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass, field, asdict, replace

@dataclass(frozen=True)
class ServerConfig:
    host:            str
    port:            int
    debug:           bool          = False
    allowed_origins: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.host.strip():
            raise ValueError("host cannot be empty")
        if not (1 <= self.port <= 65535):
            raise ValueError(f"port must be 1-65535, got {self.port}")

    def with_port(self, new_port: int) -> "ServerConfig":
        return replace(self, port=new_port)

    def with_origin(self, origin: str) -> "ServerConfig":
        return replace(self, allowed_origins=self.allowed_origins + (origin,))

    def to_dict(self) -> dict:
        return asdict(self)

cfg = ServerConfig("api.example.com", 443, debug=False)
cfg2 = cfg.with_port(8443)
cfg3 = cfg.with_origin("https://app.example.com")

print(cfg)
print(cfg2.port)                  # 8443
print(cfg3.allowed_origins)       # ('https://app.example.com',)
print(cfg.port)                   # 443 — original unchanged

import json
print(json.dumps(cfg.to_dict()))

try:
    ServerConfig("", 80)   # ValueError: host cannot be empty
except ValueError as e:
    print(e)

try:
    cfg.port = 9999        # FrozenInstanceError
except Exception as e:
    print(type(e).__name__)
```

**Why:** Frozen dataclasses are perfect for config objects — immutable, hashable, type-annotated, and JSON-serializable. The `with_X` pattern using `replace()` provides a clean functional update API.
</details>

---

## Navigation

| | |
|---|---|
| Root theory | [../theory.md](../theory.md) |
| Subfolder theory | [theory.md](./theory.md) |
| Prev subfolder | [../03_metaclasses/practice.md](../03_metaclasses/practice.md) |
| Next subfolder | [../05_advanced_patterns/practice.md](../05_advanced_patterns/practice.md) |
| Root practice | [../practice.md](../practice.md) |
