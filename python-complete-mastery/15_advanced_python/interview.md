# 🎯 Advanced Python — Interview Questions

> 13 questions + 5 trap questions. Three-level coverage: Junior → Mid-Level → Senior.
> Every answer includes the conceptual explanation AND code that proves it.

---

## 📋 Contents

```
Junior   (1–4):   dunders, __slots__, @dataclass, property
Mid-Level(5–9):   descriptor protocol, metaclasses, __new__, callable objects, class creation
Senior  (10–13):  attribute lookup order, metaclass conflicts, ABCs, Protocol
Traps    (5):     subtle mistakes every senior gets asked
```

---

## Junior Level

---

### Q1. What is a "dunder method" and why does Python use them?

**Intent:** Understand the protocol system and why it was chosen.

**Answer:**

Dunder (double-underscore) methods are Python's **protocol system** — they let
user-defined objects integrate with Python's syntax and built-in functions
without inheritance.

```python
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __len__(self):    return 2              # len(v)
    def __repr__(self):   return f"Vector({self.x}, {self.y})"
    def __add__(self, o): return Vector(self.x + o.x, self.y + o.y)
    def __iter__(self):   return iter((self.x, self.y))  # for n in v

v = Vector(1, 2)
len(v)            # 2  — calls type(v).__len__(v)
v + Vector(3, 4)  # Vector(4, 6)
list(v)           # [1, 2]
```

**Why not just use method names like `.add()` or `.length()`?**

The dunder system provides a **uniform interface across all types**. `len()`
works on lists, strings, dicts, and your custom class — all via `__len__`.
No base class needed. This is duck typing at the protocol level.

**Critical subtlety:** Python calls dunders on the **class**, not the instance:

```python
class Tricky:
    def __len__(self): return 5

t = Tricky()
t.__len__ = lambda: 999   # monkey-patch instance

len(t)        # 5  — calls type(t).__len__(t), ignores instance patch!
t.__len__()   # 999 — direct call bypasses the protocol
```

This is intentional — it prevents security exploits and improves performance.

---

### Q2. What is `__slots__` and when should you use it?

**Intent:** Understand the default instance storage model and the optimization.

**Answer:**

By default, Python stores instance attributes in a per-instance `__dict__`.
Dicts are flexible but expensive: ~200–300 bytes of overhead per instance.

`__slots__` replaces `__dict__` with a fixed compact array of C-level
member descriptors:

```python
import sys

class PointDict:
    def __init__(self, x, y): self.x, self.y = x, y

class PointSlots:
    __slots__ = ("x", "y")
    def __init__(self, x, y): self.x, self.y = x, y

d = PointDict(1, 2)
s = PointSlots(1, 2)

# Memory:
print(sys.getsizeof(d) + sys.getsizeof(d.__dict__))  # ~360 bytes
print(sys.getsizeof(s))                               # ~72 bytes (5x smaller)

# Behavior difference:
d.z = 3       # OK — dict is there
# s.z = 3     # AttributeError — no __dict__

# Slots ARE descriptors:
print(type(PointSlots.x))   # <class 'member_descriptor'>
```

**When to use:**
- Classes with millions of instances (Points, Events, Records)
- Performance-critical inner loops
- When the attribute set is truly fixed

**Costs:**
- No dynamic attribute assignment
- Multiple inheritance requires all parents to also use `__slots__`
- Need `__getstate__`/`__setstate__` for pickling in some cases

---

### Q3. What does `@dataclass` generate, and when is it preferable to a plain class?

**Intent:** Know the automation, the field configuration, and the trade-offs.

**Answer:**

`@dataclass` auto-generates boilerplate based on annotated fields:

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int = 0
    patch: int = 0
    pre_release: str = field(default="", compare=False)

    def __post_init__(self):
        # Validation runs after __init__:
        for v in (self.major, self.minor, self.patch):
            if v < 0:
                raise ValueError(f"Version components must be ≥ 0, got {v}")

v1 = Version(1, 2, 3)
v2 = Version(1, 2, 3, pre_release="beta")
print(v1 == v2)     # True — pre_release excluded from compare
print(v1 > Version(1, 0, 0))   # True — order=True gives __lt__, __gt__ etc.
print(hash(v1))     # works — frozen=True makes it hashable
```

| Flag | Generated | Default |
|------|-----------|---------|
| `init=True` | `__init__` from fields | on |
| `repr=True` | `__repr__` from fields | on |
| `eq=True` | `__eq__` field-by-field | on |
| `order=True` | All 4 comparison methods | off |
| `frozen=True` | Immutable + hashable | off |
| `slots=True` | `__slots__` (3.10+) | off |

**Prefer `@dataclass` when:**
- Primarily data container with little logic
- You'd write `__init__` and `__repr__` yourself anyway
- Need sortability or immutability

**Prefer plain class when:**
- Complex initialization requiring private state
- Heavy method-rich classes where boilerplate is minimal
- Need custom `__init__` logic that doesn't fit the field model

---

### Q4. What is `@property` and how does it work under the hood?

**Intent:** Understand it as a descriptor, not just convenient syntax.

**Answer:**

`@property` is a **built-in descriptor class** — not magic syntax.
It's a regular Python object that implements `__get__`, `__set__`, `__delete__`:

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):               # radius = property(fget=this_function)
        """Radius in meters."""
        return self._radius

    @radius.setter                  # radius = radius.setter(this_function)
    def radius(self, value):        # returns new property with fset added
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

    @property
    def area(self):
        import math
        return math.pi * self._radius ** 2

c = Circle(5)
print(c.area)      # 78.53... — computed on demand
c.radius = -1      # ValueError
```

**Why does `@property` work even though `self.__dict__` is right there?**

Because `property` is a **data descriptor** (has both `__get__` and `__set__`).
The attribute lookup order puts data descriptors BEFORE instance `__dict__`.
So `c.radius` → finds `property` descriptor → calls its `__get__` → calls `fget(c)`.

**`obj is None` check in `__get__`:**

```python
# Inside property.__get__:
def __get__(self, obj, objtype=None):
    if obj is None:
        return self   # Circle.radius → returns property object
    return self.fget(obj)   # c.radius → calls fget(c)
```

---

## Mid-Level

---

### Q5. Explain the descriptor protocol. Data vs non-data descriptors?

**Intent:** Core Python internals for framework design.

**Answer:**

A descriptor is any object whose class defines one or more of:
- `__get__(self, obj, objtype)` — intercept read
- `__set__(self, obj, value)` — intercept write
- `__delete__(self, obj)` — intercept delete

Descriptors live as **class attributes** and intercept access on **instances**.

```python
class Typed:
    """Data descriptor — validates type on write."""

    def __set_name__(self, owner, name):
        self.name    = name
        self.private = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None: return self   # class access → return descriptor
        return getattr(obj, self.private, None)

    def __set__(self, obj, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"{self.name} must be numeric, got {type(value).__name__}")
        setattr(obj, self.private, value)

class Point:
    x = Typed()   # __set_name__ called: self.name = "x"
    y = Typed()

p = Point()
p.x = 1.5    # Typed.__set__ called
p.y = "bad"  # TypeError: y must be numeric
```

**Attribute lookup priority:**

```
1. Data descriptor from type(obj).__mro__      ← HIGHEST priority
2. obj.__dict__["name"]
3. Non-data descriptor from type(obj).__mro__  ← LOWEST priority
4. type(obj).__getattr__() if defined
```

**Why does this order matter?**

- `@property` (data descriptor) → **always** calls fget, never serves stale cache
- `cached_property` (non-data descriptor) → instance `__dict__` wins after first
  computation → that IS the caching mechanism:

```python
class lazy:
    def __set_name__(self, owner, name): self.name = name
    def __get__(self, obj, objtype=None):
        if obj is None: return self
        value = self.func(obj)
        obj.__dict__[self.name] = value   # cache in instance dict
        return value                      # next access: __dict__ found first → descriptor skipped
```

---

### Q6. Walk me through what happens when Python executes `class Foo(Bar): pass`

**Intent:** Deep class creation machinery.

**Answer:**

```python
class Foo(Bar):
    x = 10
    def method(self): pass
```

Python does this:

1. **Find the metaclass:** check `metaclass=` kwarg → check base classes' metaclasses → default to `type`

2. **Prepare namespace:** call `metaclass.__prepare__("Foo", (Bar,))` → returns `{}`
   (or custom mapping for some metaclasses, e.g. `OrderedDict`)

3. **Execute class body** in that namespace:
   After execution: `namespace = {"x": 10, "method": <function>}`

4. **Create class object:** call `metaclass("Foo", (Bar,), namespace)`:
   - `type.__new__(mcs, "Foo", (Bar,), namespace)` allocates class object
   - Sets `__dict__`, `__bases__`, `__mro__` etc.
   - For each value in namespace: if it has `__set_name__`, calls `v.__set_name__(Foo, attr_name)`
   - `type.__init__(cls, "Foo", (Bar,), namespace)` initializes

5. **Call `__init_subclass__`** on the parent: `Bar.__init_subclass__(Foo)`
   (this is where `__init_subclass__` hooks run)

6. Bind class object to `Foo` in enclosing scope

**Practical consequence:** `__set_name__` is called at step 4, which is why
descriptors know their own name without you passing it:

```python
class Descriptor:
    def __set_name__(self, owner, name):
        print(f"  Assigned: {owner.__name__}.{name}")

class MyClass:
    x = Descriptor()   # prints: Assigned: MyClass.x
```

---

### Q7. What is a metaclass and what are real use cases?

**Intent:** Know when to use metaclasses vs simpler alternatives.

**Answer:**

A metaclass is a class whose **instances are classes**. The default metaclass
is `type`. A custom metaclass intercepts the class creation process.

```python
class RegistryMeta(type):
    _registry = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases:   # skip the abstract base itself
            mcs._registry[name] = cls
        return cls

class Serializer(metaclass=RegistryMeta): pass

class JSONSerializer(Serializer): pass    # auto-registered
class XMLSerializer(Serializer):  pass    # auto-registered

print(RegistryMeta._registry)
# {'JSONSerializer': JSONSerializer, 'XMLSerializer': XMLSerializer}
```

**Real production use cases:**
- Django's `ModelBase` metaclass: collects `Field` objects, sets up DB table names
- SQLAlchemy's `DeclarativeMeta`: maps Python classes to database tables
- Django REST Framework's `SerializerMetaclass`: collects field declarations
- Enum's `EnumMeta`: creates the enum value → member mapping
- Pytest's `pytest.mark` system

**When NOT to use a metaclass (prefer these instead):**

| Simpler alternative | When |
|---------------------|------|
| `__init_subclass__` | Need to run code when subclassed |
| Class decorator | Need to post-process a class |
| Descriptor | Need attribute-level interception |
| `@dataclass` | Need auto-generated methods |

---

### Q8. What is a callable object? How does it differ from a plain function?

**Answer:**

Any object with `__call__` is callable:

```python
class MovingAverage:
    """Callable with state — not possible with a plain lambda/function."""

    def __init__(self, window: int):
        self.window  = window
        self._values = []

    def __call__(self, value: float) -> float:
        self._values.append(value)
        if len(self._values) > self.window:
            self._values.pop(0)
        return sum(self._values) / len(self._values)

    def reset(self):
        self._values.clear()

ma = MovingAverage(window=3)
for v in [10, 20, 30, 40, 50]:
    print(f"{v} → avg: {ma(v):.1f}")
```

**How callable objects differ:**

| | Function/Lambda | Callable Object |
|--|----------------|----------------|
| State | Closure only (awkward) | Clean instance attrs |
| Introspect | `f.some_attr` awkward | `obj.count`, `obj.reset()` |
| Config | `functools.partial` | `__init__` parameters |
| Inheritance | No | Yes — full class hierarchy |
| Reset | Not possible | Define `reset()` |

**Use cases:** counters, accumulators, memoization wrappers with stats,
retry policies with state, configurable predicates, pipelines.

---

### Q9. What is `__new__` and when would you override it?

**Answer:**

`__new__` creates the instance. `__init__` initializes it.
Call sequence: `cls()` → `cls.__new__(cls)` → `instance.__init__()`.

**When to override `__new__`:**

**1. Subclassing immutable types** — must set the value in `__new__` because
immutable objects can't be modified after creation:

```python
class AlwaysPositive(int):
    def __new__(cls, value):
        return super().__new__(cls, abs(value))   # value set here

n = AlwaysPositive(-42)
print(n)         # 42
print(n + 1)     # 43  (still an int)
```

**2. Singleton / flyweight patterns:**

```python
class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, value):
        if hasattr(self, "_initialized"):
            return                # IMPORTANT: guard re-init
        self.value = value
        self._initialized = True

a = Singleton(1)
b = Singleton(2)
print(a is b)      # True
print(a.value)     # 1 — not overwritten
```

**Common pitfall:** `__init__` is called every time `cls()` is called —
even if `__new__` returns an existing instance. Always guard.

---

## Senior Level

---

### Q10. Explain the full attribute lookup order including descriptors and `__getattr__`

**Answer:**

For `obj.name`:

```
Step 1: Search type(obj).__mro__ for a DATA DESCRIPTOR
        (class that has __get__ AND __set__ or __delete__)
        → Found? Call descriptor.__get__(obj, type(obj))  → RETURN

Step 2: Check obj.__dict__["name"]
        → Found? Return it  → RETURN

Step 3: Search type(obj).__mro__ for NON-DATA DESCRIPTOR or class variable
        → Found descriptor? Call descriptor.__get__(obj, type(obj))  → RETURN
        → Found class variable? Return it  → RETURN

Step 4: Call type(obj).__getattr__(name)   if defined  → RETURN

Step 5: raise AttributeError
```

**Concrete consequences:**

```python
class Frozen:
    """Demonstrates data descriptor vs __dict__ priority."""
    @property
    def x(self):   # data descriptor
        return 999

f = Frozen()
f.__dict__["x"] = 42      # bypass normal assignment
print(f.x)                 # 999 — property (data descriptor) wins over __dict__!

# Non-data descriptor (lazy cache) — __dict__ wins after first access:
class lazy:
    def __set_name__(self, owner, name): self.name = name
    def __get__(self, obj, objtype=None):
        if obj is None: return self
        value = expensive()
        obj.__dict__[self.name] = value   # instance dict set
        return value

class Obj:
    result = lazy()

o = Obj()
o.result   # calls lazy.__get__ → computes and caches in obj.__dict__
o.result   # reads from obj.__dict__ (non-data descriptor has lower priority)
```

**`__getattr__` vs `__getattribute__`:**

| | When called | Risk |
|--|------------|------|
| `__getattr__` | Only on failure (last resort) | Safe |
| `__getattribute__` | EVERY attribute access | Infinite recursion if you access `self.anything` inside it |

```python
class Safe:
    def __getattr__(self, name):   # only fallback
        return f"<missing: {name}>"

class Risky:
    def __getattribute__(self, name):
        print(self.name)   # RECURSION! calls __getattribute__ again
        # Fix: object.__getattribute__(self, "name")
```

---

### Q11. What is the metaclass conflict problem and how do you resolve it?

**Answer:**

When a class inherits from two bases with incompatible metaclasses:

```python
class Meta1(type): pass
class Meta2(type): pass

class Base1(metaclass=Meta1): pass
class Base2(metaclass=Meta2): pass

class Both(Base1, Base2): pass
# TypeError: metaclass conflict: the metaclass of a derived class
#   must be a (non-strict) subclass of the metaclasses of all its bases
```

**Why this restriction exists:**

Python must pick ONE metaclass to create `Both`. That metaclass must be a
subclass of ALL metaclasses involved. `type` isn't a subclass of Meta1 or Meta2.
Only a combined metaclass that inherits from both satisfies the constraint.

**Resolution:**

```python
class CombinedMeta(Meta1, Meta2): pass

class Both(Base1, Base2, metaclass=CombinedMeta): pass   # OK
```

**Real-world occurrence:** Combining `ABCMeta` with a custom metaclass.
Since `ABCMeta` subclasses `type`, your custom metaclass must also subclass
`ABCMeta` (not `type`) to be compatible:

```python
from abc import ABCMeta

class MyMeta(ABCMeta):   # inherit from ABCMeta, not type!
    def __new__(mcs, name, bases, namespace):
        ...
        return super().__new__(mcs, name, bases, namespace)
```

**Prevention:** Use `__init_subclass__` instead of metaclasses when possible —
it composes perfectly across multiple inheritance with no conflict risk.

---

### Q12. How do ABCs enforce abstract methods? What are virtual subclasses?

**Answer:**

ABCs use `ABCMeta` as their metaclass. The enforcement happens in
`ABCMeta.__call__` — before creating an instance, it checks for unimplemented
abstract methods:

```python
# Simplified internals of ABCMeta:
class ABCMeta(type):
    def __call__(cls, *args, **kwargs):
        # Collect all still-abstract methods:
        abstract = {
            name
            for name in dir(cls)
            if getattr(getattr(cls, name, None), "__isabstractmethod__", False)
        }
        if abstract:
            raise TypeError(
                f"Can't instantiate abstract class {cls.__name__} "
                f"with abstract methods {', '.join(sorted(abstract))}"
            )
        return super().__call__(*args, **kwargs)
```

`@abstractmethod` sets `func.__isabstractmethod__ = True`.
A concrete subclass that overrides it provides a method where this is absent/False.

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

class Circle(Shape):
    def __init__(self, r): self.r = r
    def area(self): return 3.14 * self.r ** 2

# Shape()   → TypeError
# Circle(5) → OK
```

**Virtual subclasses** — register without inheriting:

```python
@Shape.register
class LegacyTriangle:
    def area(self): return 0.5 * 3 * 4

isinstance(LegacyTriangle(), Shape)   # True — even without inheritance!
issubclass(LegacyTriangle, Shape)     # True
```

Virtual subclasses are useful for retrofitting existing/third-party classes
into an abstract hierarchy without modifying their source code.

---

### Q13. Protocol vs ABC — explain the difference and when to use each

**Answer:**

```python
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

# ABC: NOMINAL typing — must explicitly inherit or register
class Drawable(ABC):
    @abstractmethod
    def draw(self) -> None: ...

class Circle(Drawable):   # MUST inherit
    def draw(self): print("○")

# Protocol: STRUCTURAL typing — any class with the right methods qualifies
@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:             # NO inheritance needed
    def draw(self): print("○")

isinstance(Circle(), Drawable)   # True — has the method → qualifies
```

**Decision matrix:**

| Use ABC when... | Use Protocol when... |
|-----------------|---------------------|
| Framework base: want subclasses to inherit mixin methods | Library/utility code used by unrelated types |
| Runtime enforcement of abstract methods is needed | Type checking only (mypy, pyright) |
| `isinstance(obj, MyABC)` in core logic | Public API — don't want to force inheritance |
| Want `abstractmethod` enforcement at instantiation | "has this method" is sufficient |

**Examples from stdlib:**
- `ABC` for real: `collections.abc.Mapping` — inheriting gives `__contains__`, `keys()`, etc.
- `Protocol` style: `os.PathLike` — any class with `__fspath__` works with `os.path.*`

**Summary:**
- ABC: "you must claim membership by inheriting"
- Protocol: "if you look like it, you are it"

---

## 🔴 Trap Questions

---

### Trap 1: Why return `NotImplemented` instead of `False` from `__eq__`?

```python
class Celsius:
    def __init__(self, c): self.c = c
    def __eq__(self, other):
        if isinstance(other, Celsius): return self.c == other.c
        return False      # ← WRONG
        # return NotImplemented  ← correct
```

**Answer:** When `a == b` is evaluated:
1. Python calls `a.__eq__(b)` first
2. If it returns `NotImplemented`, Python tries `b.__eq__(a)` (reflected)
3. If that also returns `NotImplemented`, falls back to identity

If `Celsius.__eq__` returns `False` for non-Celsius types, the reflected check
never happens. A `Fahrenheit` subclass that knows how to compare with `Celsius`
can never return `True` — the parent short-circuits with `False` first.

---

### Trap 2: What's wrong with this dataclass?

```python
@dataclass
class Config:
    tags: list = []   # problem!
```

**Answer:** Python's `@dataclass` raises `ValueError: mutable default <class 'list'>`
at class definition time. If it were allowed, ALL instances would share the SAME list:

```python
# Without @dataclass protection:
class Config:
    tags = []   # shared class attribute!
a, b = Config(), Config()
a.tags.append("x")
print(b.tags)   # ["x"] — corrupted!
```

Fix: `tags: list = field(default_factory=list)`

---

### Trap 3: Does this object work in a set? Why/why not?

```python
@dataclass
class Point:
    x: float
    y: float
```

**Answer:** No. When `@dataclass` generates `__eq__`, Python automatically sets
`__hash__ = None` (makes it unhashable) to prevent hash/equality inconsistency
for mutable objects.

```python
{Point(1, 2), Point(1, 2)}   # TypeError: unhashable type: 'Point'
```

Fixes:
- `@dataclass(frozen=True)` — immutable + auto hash
- `@dataclass(unsafe_hash=True)` — hash based on fields (risky if mutated)
- Define `__hash__` manually

---

### Trap 4: What does `__getattribute__` infinite recursion look like?

```python
class Logger:
    def __getattribute__(self, name):
        print(f"Accessing: {self.name}")   # ← PROBLEM
        return object.__getattribute__(self, name)
```

**Answer:** `self.name` inside `__getattribute__` triggers another call to
`__getattribute__` → infinite recursion → `RecursionError`.

Fix: use `object.__getattribute__` for accessing your own attributes:

```python
class Logger:
    def __getattribute__(self, name):
        # Access own name via object's implementation:
        own_name = object.__getattribute__(self, "name")
        print(f"Accessing: {own_name}")
        return object.__getattribute__(self, name)
```

---

### Trap 5: What is the output?

```python
class Meta(type):
    def __new__(mcs, name, bases, ns):
        print(f"Meta.__new__: {name}")
        return super().__new__(mcs, name, bases, ns)

class A(metaclass=Meta): pass
class B(A):               pass
class C(B):               pass
```

**Answer:**
```
Meta.__new__: A
Meta.__new__: B
Meta.__new__: C
```

`Meta.__new__` is called for EVERY class in the hierarchy, not just `A`.
`B` and `C` inherit `Meta` as their metaclass through inheritance. This is
why metaclasses are "viral" — they propagate down the entire hierarchy.

**Practical consequence:** if you add side effects in your metaclass (registrations,
validations, DB connections), they run for every single subclass. Guard against
the base class: `if bases:` or `if name == "MyBase": return`.

---

## 🔥 Rapid-Fire

```
Q: Return type of __eq__ when types are incompatible?
A: NotImplemented (not False) — allows Python to try reflected check

Q: What makes an object hashable?
A: __hash__ defined + consistent with __eq__ (equal objects → same hash)

Q: What does @dataclass(eq=True, frozen=False) do to __hash__?
A: Sets __hash__ = None → object is unhashable

Q: Data vs non-data descriptor priority?
A: Data descriptor > instance __dict__ > non-data descriptor

Q: How to call parent's dunder from subclass?
A: super().__dunder__(args)  — same as any other method

Q: What __slots__ does to __dict__?
A: Removes __dict__ unless you explicitly add "__dict__" to __slots__

Q: What does __set_name__ receive?
A: (owner_class, attribute_name) — called at class creation time

Q: How do you store per-instance state in a descriptor?
A: obj.__dict__[self.name] = value — NEVER self.value = value (shared state!)

Q: When is __new__ called vs __init__?
A: __new__ creates → returns instance → __init__ initializes (both called on cls())

Q: Can @abstractmethod be combined with @property?
A: Yes: @property @abstractmethod — subclass must define it as a property

Q: Protocol vs isinstance?
A: @runtime_checkable Protocol supports isinstance(); plain Protocol is type-hint only

Q: What is __init_subclass__ and why prefer it over metaclasses?
A: Simpler hook run when class is subclassed; composes cleanly; no metaclass conflicts
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🔮 Dunder Guide | [dunder_guide.md](./dunder_guide.md) |
| 🏭 Metaclasses & Descriptors | [metaclasses_descriptors_guide.md](./metaclasses_descriptors_guide.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ➡️ Next | [16 — Design Patterns](../16_design_patterns/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Metaclasses & Descriptors](./metaclasses_descriptors_guide.md) &nbsp;|&nbsp; **Next:** [Design Patterns — Theory →](../16_design_patterns/theory.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Dunder Methods Guide](./dunder_guide.md) · [Metaclasses & Descriptors](./metaclasses_descriptors_guide.md)
