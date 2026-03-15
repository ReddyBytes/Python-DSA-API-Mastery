# ⚡ Advanced Python — Cheatsheet

> Quick reference: dunders, descriptors, metaclasses, dataclasses, slots, callables, introspection.

---

## 🔮 Dunder Methods — Quick Reference

```python
# Lifecycle
__new__(cls, ...)       # creates instance (before __init__)
__init__(self, ...)     # initializes instance
__del__(self)           # finalizer (unreliable — prefer context managers)

# Representation
__repr__(self)          # repr(obj), f"{obj!r}" — developer view
__str__(self)           # str(obj), print(obj)  — user view (fallback: __repr__)
__format__(self, spec)  # f"{obj:spec}", format(obj, spec)
__bytes__(self)         # bytes(obj)

# Comparison
__eq__(self, other)     # ==  (define __hash__ too if you define __eq__!)
__ne__(self, other)     # !=  (default: not __eq__)
__lt__(self, other)     # <
__le__(self, other)     # <=
__gt__(self, other)     # >
__ge__(self, other)     # >=
__hash__(self)          # hash(obj), dict key, set member

# Arithmetic
__add__(self, other)    # a + b     __radd__: b + a  __iadd__: a += b
__sub__(self, other)    # a - b
__mul__(self, other)    # a * b
__truediv__(self, other)# a / b
__floordiv__(self, o)   # a // b
__mod__(self, other)    # a % b
__pow__(self, other)    # a ** b
__matmul__(self, other) # a @ b  (matrix mul, Python 3.5+)
__neg__(self)           # -a
__pos__(self)           # +a
__abs__(self)           # abs(a)

# Container
__len__(self)           # len(obj)
__getitem__(self, key)  # obj[key]
__setitem__(self, k, v) # obj[key] = val
__delitem__(self, key)  # del obj[key]
__contains__(self, item)# item in obj
__iter__(self)          # iter(obj), for x in obj
__next__(self)          # next(obj)
__reversed__(self)      # reversed(obj)

# Callable
__call__(self, *a, **k) # obj(args)

# Attribute
__getattr__(self, name)     # fallback only (when normal lookup fails)
__getattribute__(self, name)# intercepts ALL access — use carefully!
__setattr__(self, n, v)     # obj.name = val
__delattr__(self, name)     # del obj.name
__dir__(self)               # dir(obj)

# Context manager
__enter__(self)             # with obj: entry
__exit__(self, et, ev, tb)  # with obj: exit (return True to suppress exception)

# Descriptor
__get__(self, obj, objtype) # descriptor read
__set__(self, obj, value)   # descriptor write (→ becomes DATA descriptor)
__delete__(self, obj)       # descriptor delete
__set_name__(self, owner, n)# called at class creation (owner=class, n=attr name)
```

---

## 🔑 Key Rules

```python
# 1. NotImplemented vs False in __eq__:
def __eq__(self, other):
    if isinstance(other, MyType): return self.x == other.x
    return NotImplemented   # NOT False — allows reflected check by other

# 2. __eq__ → must define __hash__ (or lose hashability):
def __hash__(self): return hash(self.x)   # consistent with __eq__

# 3. __radd__ exists for mixed-type operations:
#    a + b → a.__add__(b) → if NotImplemented → b.__radd__(a)

# 4. total_ordering — define __eq__ + ONE of __lt__/__le__/__gt__/__ge__:
from functools import total_ordering
@total_ordering
class Version:
    def __eq__(self, other): ...
    def __lt__(self, other): ...
    # Python derives <=, >, >= automatically
```

---

## 📦 Descriptor Protocol

```python
# Data descriptor (has __set__ → takes priority over instance __dict__):
class Validated:
    def __set_name__(self, owner, name):
        self.name = name
        self.private = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None: return self          # accessed via class
        return getattr(obj, self.private)

    def __set__(self, obj, value):
        if not isinstance(value, int):
            raise TypeError(f"{self.name} must be int")
        setattr(obj, self.private, value)

class MyModel:
    count = Validated()   # __set_name__ called automatically

# Non-data descriptor (no __set__ → instance __dict__ wins after first set):
class lazy:
    """Compute once, cache in instance __dict__."""
    def __set_name__(self, owner, name): self.name = name
    def __get__(self, obj, objtype=None):
        if obj is None: return self
        value = self.func(obj)          # compute
        obj.__dict__[self.name] = value  # cache (hides descriptor next time)
        return value

# Attribute lookup order:
# 1. Data descriptor from type(obj).__mro__    ← HIGHEST
# 2. obj.__dict__
# 3. Non-data descriptor from type(obj).__mro__ ← LOWEST
# 4. __getattr__ (last resort)
```

---

## 🏭 Metaclasses

```python
# Metaclass = class of a class. Default: type
# type(42)  → int
# type(int) → type

# Dynamic class creation with type():
Dog = type("Dog", (object,), {
    "sound": "Woof",
    "speak": lambda self: self.sound,
})

# Custom metaclass:
class RegistryMeta(type):
    _registry = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases:   # skip root class itself
            mcs._registry[name] = cls
        return cls

class Handler(metaclass=RegistryMeta): pass
class JSONHandler(Handler): pass   # auto-registered

# Lighter alternative — __init_subclass__:
class Plugin:
    _registry = {}

    def __init_subclass__(cls, /, name="", **kwargs):
        super().__init_subclass__(**kwargs)   # ALWAYS call super
        if name:
            Plugin._registry[name] = cls

class JSONPlugin(Plugin, name="json"): pass   # auto-registered
```

---

## 🗂️ @dataclass

```python
from dataclasses import dataclass, field, fields, asdict, astuple, replace

@dataclass(frozen=True, order=True)
class Point:
    x: float
    y: float
    label: str = field(default="", compare=False, repr=False)

    def __post_init__(self):   # called after __init__ — validation here
        if not isinstance(self.x, (int, float)):
            raise TypeError("x must be numeric")

# Mutable default — MUST use field(default_factory=...):
@dataclass
class Config:
    tags: list = field(default_factory=list)  # NOT tags: list = []!

# Computed fields (init=False):
@dataclass
class Box:
    width: float
    height: float
    area: float = field(init=False)    # not a constructor param
    def __post_init__(self): self.area = self.width * self.height

# Utility functions:
p = Point(1.0, 2.0)
asdict(p)           # {"x": 1.0, "y": 2.0, "label": ""}
astuple(p)          # (1.0, 2.0, "")
replace(p, x=99)    # new Point(99.0, 2.0) — original unchanged
fields(Point)       # tuple of Field objects with metadata
```

---

## 🔌 __slots__

```python
class Event:
    __slots__ = ("id", "type", "data")   # no __dict__!

    def __init__(self, id_, type_, data):
        self.id, self.type, self.data = id_, type_, data

# Memory: ~5× smaller than dict-based class

# Inheritance — only add NEW slots:
class SpecialEvent(Event):
    __slots__ = ("priority",)   # inherits Event's slots, adds own

# Keep __dict__ + __weakref__ if needed:
class Hybrid:
    __slots__ = ("x", "y", "__dict__", "__weakref__")

# Pickling with __slots__:
class Pickled:
    __slots__ = ("x", "y")
    def __getstate__(self): return {"x": self.x, "y": self.y}
    def __setstate__(self, s): self.x, self.y = s["x"], s["y"]
```

---

## 📞 Callable Objects

```python
class Multiplier:
    def __init__(self, factor): self.factor = factor
    def __call__(self, x): return x * self.factor

double = Multiplier(2)
double(5)    # 10
callable(double)  # True

# Callable with state — counter/accumulator
class Counter:
    def __init__(self): self.n = 0
    def __call__(self): self.n += 1; return self.n
    def reset(self): self.n = 0

# Check callability:
callable(obj)   # True if type(obj) has __call__
# Note: instance monkey-patching __call__ does NOT make object callable!
```

---

## 🔍 Introspection

```python
import inspect

# Built-ins:
type(obj)                    # obj's class
isinstance(obj, T)           # T or subclass of T?
issubclass(A, B)             # A subclass of B?
dir(obj)                     # all accessible names
vars(obj)                    # obj.__dict__ or class namespace
hasattr(obj, "name")         # safe attribute check
getattr(obj, "name", default)# get with fallback
setattr(obj, "name", value)
delattr(obj, "name")
callable(obj)

# inspect module:
inspect.signature(func)      # parameter signature
inspect.getmembers(obj, pred)# (name, value) pairs filtered by predicate
inspect.isclass(obj)         # True if obj is a class
inspect.isfunction(obj)      # True if plain function
inspect.ismethod(obj)        # True if bound method
inspect.getdoc(obj)          # cleaned docstring
inspect.getsource(obj)       # source code as string
inspect.getmro(cls)          # MRO tuple
inspect.Parameter.empty      # sentinel for "no default" / "no annotation"

# Common pattern: auto-repr from __init__ signature:
def auto_repr(cls):
    params = [p for p in inspect.signature(cls.__init__).parameters if p != "self"]
    cls.__repr__ = lambda self: (
        f"{type(self).__name__}("
        + ", ".join(f"{p}={getattr(self, p)!r}" for p in params)
        + ")"
    )
    return cls
```

---

## 🔴 Common Pitfalls

```python
# 1. Return NotImplemented (not False) from comparison:
def __eq__(self, other):
    if isinstance(other, MyType): ...
    return NotImplemented   # NOT False

# 2. Never use mutable default in @dataclass:
tags: list = []             # ValueError!
tags: list = field(default_factory=list)   # correct

# 3. __eq__ without __hash__ = unhashable:
# @dataclass generates __hash__ = None when eq=True, frozen=False
# Fix: @dataclass(frozen=True) or explicit __hash__

# 4. Descriptor shared state bug:
class BadDesc:
    def __set__(self, obj, value):
        self.value = value   # WRONG — shared across ALL instances!

class GoodDesc:
    def __set_name__(self, owner, name): self.private = f"_{name}"
    def __set__(self, obj, value):
        obj.__dict__[self.private] = value   # per-instance storage

# 5. __getattribute__ recursion:
class Bad:
    def __getattribute__(self, name):
        print(self.name)   # RECURSION!
# Fix: object.__getattribute__(self, "name")

# 6. Metaclass viral propagation:
class Meta(type):
    def __new__(mcs, name, bases, ns):
        # Called for EVERY subclass, not just the class that declares it!
        if not bases: return super().__new__(mcs, name, bases, ns)
        # ... your logic ...

# 7. Forgetting super().__init_subclass__(**kwargs):
class A:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)   # MUST call super!
```

---

## 🔥 Rapid-Fire

```
Q: __repr__ vs __str__ fallback?
A: str() tries __str__, falls back to __repr__. repr() only calls __repr__.

Q: Data descriptor vs non-data priority?
A: Data > instance.__dict__ > non-data

Q: frozen=True effect?
A: Makes fields immutable (FrozenInstanceError), enables __hash__

Q: __set_name__ parameters?
A: (owner_class, attribute_name) — called when descriptor is assigned to class

Q: Why does lazy cached_property work?
A: It's non-data (no __set__). After first call it writes to obj.__dict__.
   Next access: __dict__ found at priority 2, before non-data descriptor at priority 3.

Q: @runtime_checkable Protocol?
A: Enables isinstance() checks without inheritance

Q: __new__ vs __init__?
A: __new__ creates (returns instance), __init__ initializes it

Q: How to avoid metaclass conflicts?
A: Use __init_subclass__ instead; or create CombinedMeta(Meta1, Meta2)

Q: How slots work internally?
A: Each slot is a member_descriptor (data descriptor) created by the metaclass

Q: @dataclass(slots=True)?
A: Python 3.10+ — generates __slots__ automatically
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| 🔮 Dunder Guide | [dunder_guide.md](./dunder_guide.md) |
| 🏭 Metaclasses & Descriptors | [metaclasses_descriptors_guide.md](./metaclasses_descriptors_guide.md) |
| ➡️ Next | [16 — Design Patterns](../16_design_patterns/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Dunder Methods Guide →](./dunder_guide.md)

**Related Topics:** [Theory](./theory.md) · [Dunder Methods Guide](./dunder_guide.md) · [Metaclasses & Descriptors](./metaclasses_descriptors_guide.md) · [Interview Q&A](./interview.md)
