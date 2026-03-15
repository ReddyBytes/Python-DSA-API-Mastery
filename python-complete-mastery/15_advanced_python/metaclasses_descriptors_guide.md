# 🏭 metaclasses_descriptors_guide.md — Metaclasses & Descriptors, Deep Dive

> Complete reference for Python's metaclass system and descriptor protocol:
> how classes are created, how attribute access works, and production patterns.

---

## 📋 Contents

```
1.  What metaclasses are — classes that create classes
2.  type() — the default metaclass
3.  Custom metaclass — __new__ and __init__
4.  Metaclass use cases — registries, validation, ORMs
5.  __init_subclass__ — the modern lightweight alternative
6.  __class_getitem__ — generic type syntax (cls[T])
7.  Descriptor protocol — __get__, __set__, __delete__
8.  Data vs non-data descriptors — attribute lookup priority
9.  __set_name__ — descriptor knows its own name
10. Property — the built-in descriptor (and how it works)
11. Custom validator descriptor
12. Class-level caching descriptor
13. Slots — how they use descriptors under the hood
14. ABCs and abstractmethod — how they work internally
15. Common pitfalls
```

---

## 1. What Metaclasses Are

In Python, **everything is an object** — including classes. A class is an
instance of its metaclass. The default metaclass is `type`.

```
Instance relationship:
  42           is an instance of  int
  int          is an instance of  type
  type         is an instance of  type  (type is its own metaclass!)

Class relationship:
  42.__class__   → int
  int.__class__  → type
  type.__class__ → type
```

So when you write:

```python
class Dog:
    def bark(self): return "Woof!"
```

Python actually calls `type("Dog", (object,), {"bark": <function>})`.
The metaclass controls **class creation** — not instance creation.

```
You write:          Python executes:
─────────────────────────────────────────────
class Dog:          metaclass = type (default)
    ...             Dog = type.__new__(type, "Dog", (object,), namespace)
                    type.__init__(Dog, "Dog", (object,), namespace)
```

---

## 2. `type()` — The Default Metaclass

```python
# Three-argument type() creates a class dynamically:
Dog = type(
    "Dog",                      # class name
    (object,),                  # base classes (tuple)
    {                           # class namespace
        "species": "Canis lupus",
        "__init__": lambda self, name: setattr(self, "name", name),
        "bark": lambda self: f"{self.name} says Woof!",
    }
)

d = Dog("Rex")
print(d.bark())            # Rex says Woof!
print(type(d))             # <class '__main__.Dog'>
print(type(Dog))           # <class 'type'>
print(isinstance(Dog, type))  # True
```

This is equivalent to a normal class statement. Dynamic class creation is
useful for generating classes from schemas, DB models, config files, etc.

---

## 3. Custom Metaclass

A metaclass customizes the class creation process. You define one by
subclassing `type`:

```python
class SingletonMeta(type):
    """
    Metaclass that makes every class using it a singleton.
    __call__ controls what happens when cls() is called.
    """
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # __call__ on type creates instances:
            # 1. cls.__new__(cls, *args) → create
            # 2. instance.__init__(*args) → initialize
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self, url):
        self.url = url
        print(f"Connecting to {url}")

db1 = Database("postgresql://localhost/app")  # "Connecting..."
db2 = Database("postgresql://localhost/app2") # NOT printed — same instance
print(db1 is db2)  # True
```

### Metaclass `__new__` — Modify the Class Itself

```python
class AutoPropertyMeta(type):
    """
    Any attribute ending in '_' becomes a property that validates
    it's non-None before returning.
    """

    def __new__(mcs, name, bases, namespace):
        # mcs = the metaclass itself
        # name, bases, namespace = same as type.__new__ args

        new_namespace = {}
        validators = {}

        for key, value in namespace.items():
            if key.endswith('_') and not key.startswith('_'):
                attr_name = key.rstrip('_')
                validators[attr_name] = value   # store default
                # Create a validated property:
                def make_prop(k, default):
                    private = f"_{k}"
                    def getter(self):
                        val = getattr(self, private, default)
                        if val is None:
                            raise ValueError(f"{k} is not set")
                        return val
                    def setter(self, v):
                        setattr(self, private, v)
                    return property(getter, setter)
                new_namespace[attr_name] = make_prop(attr_name, value)
            else:
                new_namespace[key] = value

        return super().__new__(mcs, name, bases, new_namespace)
```

### Metaclass `__init_subclass__` Alternative (Preferred)

For most use cases, `__init_subclass__` is simpler than a full metaclass:

```python
class Plugin:
    _registry: dict[str, type] = {}

    def __init_subclass__(cls, /, name: str = "", **kwargs):
        """
        Called automatically when Plugin is subclassed.
        Equivalent to a metaclass __new__ but much simpler.
        """
        super().__init_subclass__(**kwargs)
        if name:
            Plugin._registry[name] = cls
            print(f"Registered plugin: {name!r} → {cls}")

class JSONPlugin(Plugin, name="json"):
    def serialize(self, data):
        import json
        return json.dumps(data)

class CSVPlugin(Plugin, name="csv"):
    def serialize(self, data):
        return ",".join(str(x) for x in data)

print(Plugin._registry)
# {'json': <class 'JSONPlugin'>, 'csv': <class 'CSVPlugin'>}
```

---

## 4. Metaclass Use Cases

### Registry Pattern

```python
class ModelMeta(type):
    """SQLAlchemy-style model registry."""
    _models: dict[str, type] = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if any(isinstance(b, ModelMeta) for b in bases):
            # Don't register the base Model class itself
            mcs._models[name] = cls
        return cls

class Model(metaclass=ModelMeta):
    pass   # base class

class User(Model):
    pass   # auto-registered

class Post(Model):
    pass   # auto-registered

print(ModelMeta._models)   # {'User': User, 'Post': Post}
```

### Validation at Class Definition Time

```python
class StrictMeta(type):
    """
    Enforces that all public methods have type annotations.
    Catches documentation issues at import time, not runtime.
    """

    def __new__(mcs, name, bases, namespace):
        for attr, value in namespace.items():
            if attr.startswith('_'):
                continue
            if callable(value) and not getattr(value, '__annotations__', {}):
                raise TypeError(
                    f"{name}.{attr}: public methods must have type annotations"
                )
        return super().__new__(mcs, name, bases, namespace)

# This would raise TypeError at class definition:
# class BadAPI(metaclass=StrictMeta):
#     def get_user(self, user_id):   # missing annotations!
#         pass
```

### ORM-Style Field Collection

```python
class Field:
    def __init__(self, field_type: type, required: bool = True):
        self.field_type = field_type
        self.required   = required
        self.name       = None   # set by metaclass

class ORMMeta(type):
    def __new__(mcs, name, bases, namespace):
        fields = {}
        for key, value in namespace.items():
            if isinstance(value, Field):
                value.name = key
                fields[key] = value

        # Inherit fields from parent classes:
        for base in reversed(bases):
            for key, value in vars(base).items():
                if isinstance(value, Field) and key not in fields:
                    fields[key] = value

        namespace['_fields'] = fields
        return super().__new__(mcs, name, bases, namespace)

class BaseModel(metaclass=ORMMeta):
    def __init__(self, **kwargs):
        for name, field in self._fields.items():
            value = kwargs.get(name)
            if field.required and value is None:
                raise ValueError(f"{name} is required")
            if value is not None and not isinstance(value, field.field_type):
                raise TypeError(f"{name} must be {field.field_type.__name__}")
            setattr(self, name, value)

class UserModel(BaseModel):
    username = Field(str)
    age      = Field(int)
    email    = Field(str, required=False)

u = UserModel(username="alice", age=30)
print(u.username, u.age)   # alice 30
```

---

## 5. Descriptor Protocol

A descriptor is any object whose class defines `__get__`, `__set__`, or
`__delete__`. Descriptors are the machinery behind `@property`, `classmethod`,
`staticmethod`, and many frameworks.

### The Two Types

```
Data Descriptor          Non-Data Descriptor
────────────────────────────────────────────
Defines __get__ AND      Defines __get__ only
__set__ (or __delete__)

Takes PRIORITY over      Instance __dict__ takes
instance __dict__        PRIORITY over it
```

### Attribute Lookup Order (Crucial!)

```python
# When you access obj.name:
#
#   1. type(obj).__mro__ → search for DATA DESCRIPTOR (has __get__ + __set__)
#      If found → call descriptor.__get__(obj, type(obj))
#
#   2. obj.__dict__["name"]
#      If found → return it
#
#   3. type(obj).__mro__ → search for NON-DATA DESCRIPTOR or class variable
#      If descriptor → call descriptor.__get__(obj, type(obj))
#      Else → return value
#
#   4. type(obj).__getattr__(obj, "name")  [if defined]
#
#   5. raise AttributeError
```

### Basic Descriptor

```python
class Typed:
    """
    A data descriptor that enforces type on assignment.
    Demonstrates the minimal descriptor interface.
    """

    def __init__(self, expected_type: type):
        self.expected_type = expected_type
        self.name = None   # will be set by __set_name__

    def __set_name__(self, owner: type, name: str):
        """
        Called automatically when the descriptor is assigned to a class attr.
        owner = the class, name = attribute name.
        """
        self.name = name
        self.private = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self   # accessed via class, not instance
        return getattr(obj, self.private, None)

    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name} must be {self.expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
        setattr(obj, self.private, value)

    def __delete__(self, obj):
        delattr(obj, self.private)

class Person:
    name = Typed(str)    # __set_name__ called: self.name = "name"
    age  = Typed(int)    # __set_name__ called: self.name = "age"

    def __init__(self, name, age):
        self.name = name   # calls Typed.__set__
        self.age  = age    # calls Typed.__set__

p = Person("Alice", 30)
print(p.name)            # calls Typed.__get__ → "Alice"
print(p.age)             # 30

try:
    p.age = "thirty"     # calls Typed.__set__ → TypeError
except TypeError as e:
    print(e)   # age must be int, got str
```

### `__set_name__` in Detail

Before Python 3.6, descriptors had to be told their own name manually or
use a metaclass. `__set_name__` fixed this elegantly:

```python
class MyDescriptor:
    def __set_name__(self, owner, name):
        # owner: the class where this descriptor is defined
        # name: the attribute name used in that class
        print(f"  Assigned to {owner.__name__}.{name}")

class MyClass:
    x = MyDescriptor()   # prints: "Assigned to MyClass.x"
    y = MyDescriptor()   # prints: "Assigned to MyClass.y"
```

---

## 6. `@property` — The Built-In Descriptor

`property` is just a descriptor class in pure Python. Here's how it works
internally (simplified):

```python
class property_:
    """Simplified property implementation — shows the descriptor pattern."""

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc or (fget.__doc__ if fget else None)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self   # descriptor accessed via class
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def getter(self, fget): return type(self)(fget, self.fset, self.fdel, self.__doc__)
    def setter(self, fset): return type(self)(self.fget, fset, self.fdel, self.__doc__)
    def deleter(self, fdel): return type(self)(self.fget, self.fset, fdel, self.__doc__)

# property is a data descriptor (has __get__ and __set__)
# This means it takes priority over instance __dict__
# Which is why @property works even though self.__dict__ is right there

class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

    @property
    def area(self):
        import math
        return math.pi * self._radius ** 2

    @property
    def diameter(self):
        return self._radius * 2

    @diameter.setter
    def diameter(self, value):
        self.radius = value / 2   # reuses radius validation

c = Circle(5)
print(c.area)       # 78.53...
c.diameter = 20
print(c.radius)     # 10.0
```

---

## 7. Advanced Descriptor: Validated Attribute

```python
import re

class ValidatedAttribute:
    """
    Descriptor with pluggable validators.
    Shows how production frameworks build field validation.
    """

    def __init__(self, *validators):
        self.validators = validators
        self.name = None

    def __set_name__(self, owner, name):
        self.name    = name
        self.private = f"_validated_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            return getattr(obj, self.private)
        except AttributeError:
            raise AttributeError(f"{self.name!r} not set")

    def __set__(self, obj, value):
        for validator in self.validators:
            value = validator(self.name, value)
        setattr(obj, self.private, value)

    def __delete__(self, obj):
        try:
            delattr(obj, self.private)
        except AttributeError:
            pass

# Validator functions:
def not_none(name, value):
    if value is None:
        raise ValueError(f"{name} cannot be None")
    return value

def min_length(n):
    def validator(name, value):
        if isinstance(value, str) and len(value) < n:
            raise ValueError(f"{name} must be at least {n} characters")
        return value
    return validator

def max_length(n):
    def validator(name, value):
        if isinstance(value, str) and len(value) > n:
            raise ValueError(f"{name} must be at most {n} characters")
        return value
    return validator

def matches_pattern(pattern):
    compiled = re.compile(pattern)
    def validator(name, value):
        if isinstance(value, str) and not compiled.match(value):
            raise ValueError(f"{name} must match pattern {pattern!r}")
        return value
    return validator

def strip_whitespace(name, value):
    return value.strip() if isinstance(value, str) else value

class User:
    username = ValidatedAttribute(
        not_none,
        strip_whitespace,
        min_length(3),
        max_length(20),
        matches_pattern(r"^[a-zA-Z0-9_]+$"),
    )
    email = ValidatedAttribute(
        not_none,
        strip_whitespace,
        matches_pattern(r"^[^@]+@[^@]+\.[^@]+$"),
    )

    def __init__(self, username, email):
        self.username = username
        self.email    = email

u = User("alice_99", "alice@example.com")
print(u.username, u.email)

try:
    User("a!", "not-an-email")
except ValueError as e:
    print(f"Caught: {e}")
```

---

## 8. Lazy-Loading Descriptor

```python
class lazy:
    """
    Non-data descriptor: computes value once, caches in instance __dict__.
    On second access, instance __dict__ is found first (non-data descriptor
    has lower priority than instance __dict__).
    """

    def __init__(self, func):
        self.func = func
        self.__doc__ = func.__doc__
        self.name = func.__name__

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = self.func(obj)
        # Cache in instance __dict__ — next access skips descriptor entirely
        obj.__dict__[self.name] = value
        return value

class DataProcessor:
    def __init__(self, raw_data):
        self.raw_data = raw_data

    @lazy
    def processed(self):
        """Expensive computation — done only once."""
        print("  Running expensive computation...")
        return [x ** 2 for x in self.raw_data]

    @lazy
    def statistics(self):
        """Computed from processed data."""
        data = self.processed   # uses cached value
        return {
            "min": min(data),
            "max": max(data),
            "mean": sum(data) / len(data),
        }

dp = DataProcessor(range(1000))
print(dp.processed[:5])    # "Running expensive computation..."  → [0, 1, 4, 9, 16]
print(dp.processed[:5])    # NO print — served from instance __dict__
print(dp.statistics)       # uses cached processed
```

---

## 9. How `__slots__` Uses Descriptors

When you define `__slots__`, Python creates **member descriptors** (data
descriptors) for each slot. These descriptors store values in a compact C-level
array, not in `__dict__`.

```python
class Compact:
    __slots__ = ('x', 'y', 'z')

    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

# After class creation:
print(type(Compact.x))   # <class 'member_descriptor'>
print(Compact.x)         # <member 'x' of 'Compact' objects>

# The member_descriptor is a DATA descriptor — it has both __get__ and __set__
# When you do obj.x, Python calls Compact.x.__get__(obj, Compact)
# When you do obj.x = 5, Python calls Compact.x.__set__(obj, 5)
# The value is stored in the instance's C-level slot array, not __dict__

# Memory comparison (approximate):
import sys

class WithDict:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

class WithSlots:
    __slots__ = ('x', 'y', 'z')
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

d = WithDict(1, 2, 3)
s = WithSlots(1, 2, 3)
print(f"With __dict__: {sys.getsizeof(d) + sys.getsizeof(d.__dict__)} bytes")
print(f"With __slots__: {sys.getsizeof(s)} bytes")
# Slots are significantly smaller — no dict overhead
```

---

## 10. ABCs and `abstractmethod`

ABCs use a metaclass (`ABCMeta`) to enforce that abstract methods are
implemented in subclasses. The enforcement happens in `type.__call__`:

```python
from abc import ABC, abstractmethod, ABCMeta

class Shape(ABC):
    """Abstract base class — cannot be instantiated."""

    @abstractmethod
    def area(self) -> float:
        """Return the area."""
        ...

    @abstractmethod
    def perimeter(self) -> float:
        """Return the perimeter."""
        ...

    def describe(self) -> str:
        return f"{type(self).__name__}: area={self.area():.2f}, perimeter={self.perimeter():.2f}"

# Shape() → TypeError: Can't instantiate abstract class Shape
# with abstract methods area, perimeter

class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        import math
        return 2 * math.pi * self.radius

c = Circle(5)
print(c.describe())   # Circle: area=78.54, perimeter=31.42

# How ABCMeta enforces abstract methods (simplified):
class ABCMeta_(type):
    def __call__(cls, *args, **kwargs):
        abstract = set()
        for name in dir(cls):
            if getattr(getattr(cls, name, None), '__isabstractmethod__', False):
                abstract.add(name)
        if abstract:
            raise TypeError(
                f"Can't instantiate abstract class {cls.__name__} "
                f"with abstract methods {', '.join(sorted(abstract))}"
            )
        return super().__call__(*args, **kwargs)

# Virtual subclasses (register without inheriting):
class SupportsArea:
    @abstractmethod
    def area(self) -> float: ...

@SupportsArea.register
class CustomShape:
    def area(self): return 42.0

print(isinstance(CustomShape(), SupportsArea))  # True — even without inheritance
```

---

## 11. Common Pitfalls

### Pitfall 1: Metaclass Conflicts

```python
# If a class has two metaclasses that aren't related, Python raises:
# TypeError: metaclass conflict: the metaclass of a derived class
#            must be a (non-strict) subclass of the metaclasses of all its bases

class Meta1(type): pass
class Meta2(type): pass

class Base1(metaclass=Meta1): pass
class Base2(metaclass=Meta2): pass

# class Combined(Base1, Base2): pass   # TypeError!

# Fix: create a combined metaclass:
class CombinedMeta(Meta1, Meta2): pass
class Combined(Base1, Base2, metaclass=CombinedMeta): pass   # OK
```

### Pitfall 2: Descriptor Shared State

```python
# WRONG: storing state on the descriptor (shared across ALL instances!):
class BadDescriptor:
    def __init__(self):
        self.value = None   # shared state!

    def __get__(self, obj, objtype=None):
        return self.value

    def __set__(self, obj, value):
        self.value = value   # WRONG: all instances share this!

class Broken:
    x = BadDescriptor()

b1 = Broken(); b2 = Broken()
b1.x = 42
print(b2.x)   # 42!!! — wrong, should be None

# CORRECT: store state in obj.__dict__ using the name:
class GoodDescriptor:
    def __set_name__(self, owner, name):
        self.name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        obj.__dict__[self.name] = value   # per-instance storage
```

### Pitfall 3: `__init_subclass__` with `super()`

```python
# Always call super().__init_subclass__() to support multiple inheritance:

class A:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)   # MUST call super!
        print(f"A saw: {cls.__name__}")

class B:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)   # MUST call super!
        print(f"B saw: {cls.__name__}")

class C(A, B): pass   # Both A and B's __init_subclass__ are called correctly
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🔮 Dunder Methods Guide | [dunder_guide.md](./dunder_guide.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Dunder Methods Guide](./dunder_guide.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Dunder Methods Guide](./dunder_guide.md) · [Interview Q&A](./interview.md)
