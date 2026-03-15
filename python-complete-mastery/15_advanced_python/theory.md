# 🧙 Advanced Python — Theory

> *"Most developers use Python. Advanced Python engineers understand how it works.*
> *Every operator, every built-in, every for-loop runs through a protocol.*
> *Once you see those protocols, the language becomes transparent."*

---

## 🎬 The Story: Building a Framework

Imagine you're building a data analysis library. Users should be able to write:

```python
dataset = Dataset([1, 2, 3, 4, 5])

len(dataset)           # how many items?
dataset[2]             # get item by index
dataset + other        # merge two datasets
for item in dataset:   # iterate
if 3 in dataset:       # membership test
print(dataset)         # human-readable description
repr(dataset)          # developer-readable repr
with dataset:          # resource management
```

Without advanced Python, you'd need 8 separate, arbitrarily-named methods. **With advanced Python, each of these maps to a protocol** — a set of dunder methods that Python calls automatically. Your class plugs into the language itself.

This is what advanced Python is: **understanding and using the protocols that power Python's syntax**.

---

## 🔑 Chapter 1: Dunder Methods — Python's Protocol System

**Dunder** = **D**ouble **under**score. Python's way of defining object behaviour through well-known method names that the interpreter calls automatically.

### The Fundamental Insight

When you write `a + b`, Python doesn't call a method named `add(a, b)`. Instead it calls `a.__add__(b)`. This means **any class can define what `+` means for its objects**.

```
PYTHON SYNTAX     →    DUNDER CALL
──────────────────────────────────────────────────────────
len(obj)          →    obj.__len__()
obj[key]          →    obj.__getitem__(key)
obj[key] = val    →    obj.__setitem__(key, val)
del obj[key]      →    obj.__delitem__(key)
x in obj          →    obj.__contains__(x)
for x in obj      →    iter(obj).__next__() via obj.__iter__()
obj + other       →    obj.__add__(other)
obj == other      →    obj.__eq__(other)
str(obj)          →    obj.__str__()
repr(obj)         →    obj.__repr__()
bool(obj)         →    obj.__bool__()
obj()             →    obj.__call__()
with obj          →    obj.__enter__(), obj.__exit__()
abs(obj)          →    obj.__abs__()
hash(obj)         →    obj.__hash__()
```

This table IS Python's object model. Learn it and Python becomes predictable.

---

## 📝 Chapter 2: Representation — `__str__`, `__repr__`, `__format__`

These three serve different audiences:

```
__repr__  → developer-facing, unambiguous, should be copy-paste runnable
__str__   → user-facing, human-readable, doesn't need to be precise
__format__ → how the object renders inside f-strings with format specs
```

```python
from datetime import datetime

dt = datetime(2025, 3, 8, 14, 30)

repr(dt)    # datetime.datetime(2025, 3, 8, 14, 30)   ← copy-pasteable
str(dt)     # 2025-03-08 14:30:00                      ← readable

f"{dt:%Y/%m/%d}"   # 2025/03/08  ← custom format spec via __format__
```

**The fallback chain:**
```
str(obj)  → calls obj.__str__()
           → if not defined: falls back to obj.__repr__()
           → if not defined: falls back to object's default: <ClassName at 0x...>

repr(obj) → calls obj.__repr__()
           → if not defined: <ClassName at 0x...>

f"{obj}"  → calls obj.__format__("")
           → if not defined: falls back to str(obj)
```

**Implementing all three:**

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        # Must be unambiguous — eval(repr(v)) should recreate the object:
        return f"Vector({self.x!r}, {self.y!r})"

    def __str__(self):
        # Human-readable:
        return f"({self.x}, {self.y})"

    def __format__(self, spec):
        # Support format specs:
        if spec == "polar":
            import math
            r     = math.hypot(self.x, self.y)
            theta = math.atan2(self.y, self.x)
            return f"|{r:.2f}|∠{math.degrees(theta):.1f}°"
        return str(self)

v = Vector(3, 4)
repr(v)           # "Vector(3, 4)"
str(v)            # "(3, 4)"
f"{v}"            # "(3, 4)"
f"{v:polar}"      # "|5.00|∠53.1°"
```

**Rule:** Always implement `__repr__`. Implement `__str__` only when a different user-facing format makes sense.

---

## ⚖️ Chapter 3: Comparison and Hashing

### The Comparison Protocol

```python
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    # Python calls __eq__ for ==:
    def __eq__(self, other):
        if not isinstance(other, Temperature):
            return NotImplemented   # ← not False! tells Python to try other.__eq__
        return self.celsius == other.celsius

    # Define ordering — Python can derive the rest with @functools.total_ordering:
    def __lt__(self, other):
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.celsius < other.celsius

    def __le__(self, other): ...
    def __gt__(self, other): ...
    def __ge__(self, other): ...
```

**`functools.total_ordering` — define two, get all six:**

```python
import functools

@functools.total_ordering
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def __eq__(self, other):
        return isinstance(other, Temperature) and self.celsius == other.celsius

    def __lt__(self, other):
        return isinstance(other, Temperature) and self.celsius < other.celsius

    # __le__, __gt__, __ge__ are automatically derived!

t1 = Temperature(20)
t2 = Temperature(30)
t1 < t2    # True
t1 > t2    # False
t1 <= t2   # True
sorted([t2, t1])   # [Temperature(20), Temperature(30)]
```

### `__hash__` and Its Relationship with `__eq__`

**The critical rule:** objects that compare equal must have the same hash.

```python
# Python enforces this:
# If you define __eq__ without __hash__:
#   → __hash__ is set to None → object is NOT hashable → can't use in set/dict

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))   # hash from same fields used in __eq__

p = Point(1, 2)
{p}           # ✅ hashable
{p: "val"}    # ✅ usable as dict key
```

---

## ➕ Chapter 4: Numeric and Operator Overloading

### The Arithmetic Protocol — Three Versions of Each

```
__add__(self, other)    → self + other  (left operand)
__radd__(self, other)   → other + self  (right operand — called when left fails)
__iadd__(self, other)   → self += other (in-place)
```

**Why `__radd__` exists:**
```python
v = Vector(1, 2)
3 + v   # → 3.__add__(v) → int doesn't know Vector → returns NotImplemented
        # → Python tries v.__radd__(3) → calls your method!
```

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        return NotImplemented   # let Python try other.__radd__

    def __radd__(self, other):
        return self.__add__(other)   # addition is commutative

    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector(self.x * scalar, self.y * scalar)
        return NotImplemented

    def __rmul__(self, scalar):
        return self.__mul__(scalar)   # 3 * v == v * 3

    def __neg__(self):              # unary -v
        return Vector(-self.x, -self.y)

    def __abs__(self):              # abs(v)
        import math
        return math.hypot(self.x, self.y)

v1 = Vector(1, 2)
v2 = Vector(3, 4)
v1 + v2    # Vector(4, 6)
3 * v1     # Vector(3, 6)
v1 * 2     # Vector(2, 4)
-v1        # Vector(-1, -2)
abs(v1)    # 2.236...
```

---

## 📦 Chapter 5: Container Protocol

Make your class behave like a sequence or mapping:

```python
class Dataset:
    def __init__(self, data):
        self._data = list(data)

    # Length:
    def __len__(self):
        return len(self._data)

    # Index access: ds[i], ds[a:b]:
    def __getitem__(self, key):
        return self._data[key]   # slicing works because list handles slice objects

    # Assignment: ds[i] = val:
    def __setitem__(self, key, value):
        self._data[key] = value

    # Deletion: del ds[i]:
    def __delitem__(self, key):
        del self._data[key]

    # Membership: x in ds:
    def __contains__(self, item):
        return item in self._data

    # Iteration: for x in ds:
    def __iter__(self):
        return iter(self._data)

    # Reversed: reversed(ds):
    def __reversed__(self):
        return reversed(self._data)

ds = Dataset([10, 20, 30, 40])
len(ds)         # 4
ds[1]           # 20
ds[1:3]         # [20, 30]
20 in ds        # True
list(ds)        # [10, 20, 30, 40]
for x in ds: print(x)

# Python infers these from __len__ + __getitem__:
# __iter__ (sequential integer indexing)
# __contains__ (linear search)
# __reversed__
# Sequence protocol registration with collections.abc
```

### `__bool__` — Truthiness

```python
class Container:
    def __len__(self):
        return self._count

    # __bool__ is optional — Python falls back to __len__:
    # if __len__() == 0 → False, else → True

    # Define __bool__ when truthiness ≠ emptiness:
    def __bool__(self):
        return self._active and len(self) > 0
```

---

## 🔧 Chapter 6: `__slots__` — Memory Optimization

By default, every Python object stores its attributes in a `__dict__` (a hash table). This is flexible but uses ~200-300 bytes per instance.

`__slots__` replaces `__dict__` with a fixed-size array of descriptors:

```python
# Without __slots__:
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

import sys
p = Point(1, 2)
sys.getsizeof(p)             # ~56 bytes (object overhead)
sys.getsizeof(p.__dict__)    # ~232 bytes (the dict itself)
# Total: ~288 bytes per instance

# With __slots__:
class PointSlotted:
    __slots__ = ('x', 'y')   # declare allowed attributes

    def __init__(self, x, y):
        self.x = x
        self.y = y

ps = PointSlotted(1, 2)
sys.getsizeof(ps)            # ~64 bytes — NO __dict__!
# hasattr(ps, '__dict__')    # False

# Impact at scale:
# 1,000,000 Point instances:
#   without __slots__: ~288 MB
#   with    __slots__: ~64 MB   ← 4.5x smaller
```

**Trade-offs:**
```
__slots__ GIVES you:      __slots__ TAKES AWAY:
  ✅ Memory savings          ❌ Dynamic attribute assignment
  ✅ Faster attribute access  ❌ __dict__ (unless you add it to __slots__)
  ✅ Prevents typos          ❌ __weakref__ (unless you add it)
                             ❌ Multiple inheritance with other __slots__ classes
```

---

## 🔍 Chapter 7: Descriptors — The Power Behind Properties

A **descriptor** is an object that defines how attribute access works. It implements one or more of: `__get__`, `__set__`, `__delete__`.

**This is how `@property`, `@classmethod`, `@staticmethod` are all implemented** — they're just descriptors.

```python
# Descriptor protocol:
class MyDescriptor:
    def __get__(self, obj, objtype=None):
        """Called when attribute is READ.
        obj:     the instance (None if accessed on class)
        objtype: the class
        """

    def __set__(self, obj, value):
        """Called when attribute is WRITTEN."""

    def __delete__(self, obj):
        """Called when attribute is DELeted."""
```

**When Python accesses `obj.attr`:**
```
1. Look for 'attr' in type(obj).__mro__ (class and base classes)
2. If found AND it's a data descriptor (__set__ or __delete__):
   → call descriptor.__get__(obj, type(obj))
3. Else look in obj.__dict__
4. Else if found in class and it's non-data descriptor (__get__ only):
   → call descriptor.__get__(obj, type(obj))
5. Else raise AttributeError
```

**Data descriptor** (has `__set__` or `__delete__`): takes priority over instance `__dict__`.
**Non-data descriptor** (has only `__get__`): instance `__dict__` takes priority.

### Implementing `@property` from Scratch

```python
class property:
    """Simplified implementation showing how @property works."""

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc or (fget.__doc__ if fget else None)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self        # accessed on class → return descriptor itself
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)  # accessed on instance → call getter

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def setter(self, fset):
        return property(self.fget, fset, self.fdel)

    def deleter(self, fdel):
        return property(self.fget, self.fset, fdel)
```

### Custom Validation Descriptor

```python
class ValidatedAttribute:
    """Descriptor that validates type and range."""

    def __init__(self, name, type_, min_val=None, max_val=None):
        self.name    = name
        self.type_   = type_
        self.min_val = min_val
        self.max_val = max_val

    def __set_name__(self, owner, name):
        """Called when descriptor is assigned to class attribute.
        Lets descriptor know its own name without being told explicitly."""
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        if not isinstance(value, self.type_):
            raise TypeError(f"{self.name}: expected {self.type_.__name__}, got {type(value).__name__}")
        if self.min_val is not None and value < self.min_val:
            raise ValueError(f"{self.name}: {value} < minimum {self.min_val}")
        if self.max_val is not None and value > self.max_val:
            raise ValueError(f"{self.name}: {value} > maximum {self.max_val}")
        obj.__dict__[self.name] = value

class Product:
    price    = ValidatedAttribute("price",    float, min_val=0.0)
    quantity = ValidatedAttribute("quantity", int,   min_val=0, max_val=10000)
    name     = ValidatedAttribute("name",     str)

    def __init__(self, name, price, quantity):
        self.name     = name      # triggers __set__ on descriptor
        self.price    = price
        self.quantity = quantity

p = Product("Widget", 9.99, 100)
p.price = -1.0     # ValueError: price: -1.0 < minimum 0.0
p.price = "free"   # TypeError: price: expected float, got str
```

---

## 🏭 Chapter 8: Metaclasses — Classes of Classes

**The mental model:** Everything in Python is an object. Functions are objects. Modules are objects. And classes are objects too. The "class" that creates class objects is called a **metaclass**.

```
NORMAL:          int        creates    42
                 str        creates    "hello"
                 MyClass    creates    my_instance

METACLASS:       type       creates    MyClass
                 type       creates    int, str, list...
                 MyMeta     creates    any class whose metaclass=MyMeta
```

```python
# Verifying:
type(42)         # <class 'int'>
type(int)        # <class 'type'>    ← int was created by 'type'
type(type)       # <class 'type'>    ← type created itself!

class Foo: pass
type(Foo)        # <class 'type'>    ← Foo was created by 'type'
```

**How `class` statement works internally:**

```python
class MyClass(Base):
    x = 10
    def method(self): ...

# Python executes this as:
namespace = {}
namespace['x'] = 10
namespace['method'] = lambda self: ...
MyClass = type('MyClass', (Base,), namespace)

# If metaclass is specified:
MyClass = MyMeta('MyClass', (Base,), namespace)
```

### Custom Metaclass Example — Registry Pattern

```python
class PluginMeta(type):
    """Metaclass that automatically registers all subclasses."""

    registry = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        # Don't register the base class itself:
        if bases:
            mcs.registry[name] = cls
            print(f"Registered plugin: {name}")
        return cls

class Plugin(metaclass=PluginMeta):
    """Base class — all subclasses are auto-registered."""
    def run(self): ...

class CSVPlugin(Plugin):    # → registered automatically
    def run(self): return "csv"

class JSONPlugin(Plugin):   # → registered automatically
    def run(self): return "json"

PluginMeta.registry   # {'CSVPlugin': <class CSVPlugin>, 'JSONPlugin': <class JSONPlugin>}

# Instantiate any plugin by name:
plugin = PluginMeta.registry["CSVPlugin"]()
plugin.run()   # "csv"
```

### Metaclass for Enforcing Interface

```python
class InterfaceMeta(type):
    """Metaclass that enforces required methods are implemented."""

    REQUIRED = set()

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases:  # skip the base class
            missing = mcs.REQUIRED - set(namespace)
            if missing:
                raise TypeError(
                    f"{name} must implement: {', '.join(missing)}"
                )
        return cls

class StorageBackend(metaclass=InterfaceMeta):
    class Meta(InterfaceMeta):
        REQUIRED = {'save', 'load', 'delete'}
    metaclass = Meta
```

**When to use metaclasses:**
```
USE metaclasses for:
  - Framework/library internals (Django ORM uses them heavily)
  - Class registration patterns (plugins, commands)
  - Enforcing interface contracts
  - Auto-generating class attributes at definition time

DON'T use metaclasses when:
  - A class decorator would work (simpler)
  - __init_subclass__ would work (Python 3.6+, much simpler)
```

### `__init_subclass__` — The Modern Alternative

```python
class Plugin:
    """Simpler registry using __init_subclass__ instead of metaclass."""
    _registry = {}

    def __init_subclass__(cls, plugin_type=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if plugin_type:
            Plugin._registry[plugin_type] = cls

class CSVPlugin(Plugin, plugin_type="csv"):
    def run(self): return "csv"

class JSONPlugin(Plugin, plugin_type="json"):
    def run(self): return "json"

Plugin._registry   # {'csv': CSVPlugin, 'json': JSONPlugin}
```

---

## 🗂️ Chapter 9: Dataclasses — Generated Boilerplate

`@dataclass` is a class decorator that inspects type annotations and auto-generates `__init__`, `__repr__`, `__eq__`, and optionally `__lt__`, `__hash__`, `__slots__`:

```python
from dataclasses import dataclass, field, KW_ONLY
from typing import ClassVar

@dataclass(order=True, frozen=True)
class Point:
    x: float
    y: float

    # Class variable — NOT included in __init__:
    DIMENSIONS: ClassVar[int] = 2

@dataclass
class Order:
    order_id:  int
    user_id:   int
    items:     list = field(default_factory=list)  # mutable default!
    discount:  float = 0.0
    _internal: str = field(default="", repr=False, compare=False, init=False)

    def __post_init__(self):
        """Called after __init__ — use for validation or derived fields."""
        if self.discount < 0 or self.discount > 1:
            raise ValueError(f"discount must be 0.0–1.0, got {self.discount}")

# Generated methods:
o = Order(1, 42, ["widget", "gadget"], discount=0.1)
repr(o)    # Order(order_id=1, user_id=42, items=['widget', 'gadget'], discount=0.1)
o == Order(1, 42, ["widget", "gadget"], 0.1)   # True (compares all fields)
```

**`field()` options:**
```python
field(default=None)          # default value
field(default_factory=list)  # factory for mutable defaults
field(repr=False)            # exclude from __repr__
field(compare=False)         # exclude from __eq__ and ordering
field(hash=False)            # exclude from __hash__
field(init=False)            # exclude from __init__
field(kw_only=True)          # keyword-only argument
```

---

## 🧭 Chapter 10: Abstract Base Classes (ABCs)

ABCs define interfaces — they declare what methods a class MUST implement:

```python
from abc import ABC, abstractmethod

class Storage(ABC):
    """Abstract base class — cannot be instantiated directly."""

    @abstractmethod
    def save(self, key: str, data: bytes) -> None:
        """Subclasses MUST implement this."""

    @abstractmethod
    def load(self, key: str) -> bytes:
        """Subclasses MUST implement this."""

    def exists(self, key: str) -> bool:
        """Optional method with default implementation."""
        try:
            self.load(key)
            return True
        except KeyError:
            return False

# Can't instantiate abstract class:
Storage()   # TypeError: Can't instantiate abstract class Storage

class S3Storage(Storage):
    def save(self, key, data):
        s3.put_object(Key=key, Body=data)

    def load(self, key):
        return s3.get_object(Key=key)["Body"].read()

# Works because all abstract methods are implemented:
storage = S3Storage()
```

**Virtual subclasses (ABC registration):**

```python
from collections.abc import Mapping

# Register an existing class as implementing an interface:
Mapping.register(MyLegacyDict)   # without modifying MyLegacyDict

isinstance(MyLegacyDict(), Mapping)   # True
```

---

## 🎭 Chapter 11: Enums — Named Constants

Enums prevent magic strings and integers scattered throughout code:

```python
from enum import Enum, IntEnum, Flag, auto

class OrderStatus(Enum):
    PENDING    = "pending"
    PROCESSING = "processing"
    SHIPPED    = "shipped"
    DELIVERED  = "delivered"
    CANCELLED  = "cancelled"

# Usage:
status = OrderStatus.PENDING
status.name      # "PENDING"
status.value     # "pending"
OrderStatus("pending")         # OrderStatus.PENDING  (lookup by value)
OrderStatus["PENDING"]         # OrderStatus.PENDING  (lookup by name)
list(OrderStatus)              # all members

# IntEnum — behaves as int (comparison with ints works):
class Priority(IntEnum):
    LOW    = 1
    MEDIUM = 2
    HIGH   = 3

Priority.HIGH > Priority.LOW   # True
Priority.HIGH > 2              # True  (IntEnum compares with int)

# auto() — auto-assign values:
class Color(Enum):
    RED   = auto()   # 1
    GREEN = auto()   # 2
    BLUE  = auto()   # 3

# Flag — for bitmask/combination enums:
from enum import Flag, auto

class Permission(Flag):
    READ    = auto()   # 1
    WRITE   = auto()   # 2
    EXECUTE = auto()   # 4

user_perm = Permission.READ | Permission.WRITE
Permission.READ in user_perm   # True
Permission.EXECUTE in user_perm  # False
```

---

## 🔎 Chapter 12: Introspection — Looking Inside Objects

Python lets you inspect and modify objects at runtime:

```python
import inspect

class MyClass:
    """A sample class."""
    class_var = 42

    def method(self, x: int) -> str:
        """A method."""
        return str(x)

obj = MyClass()

# Type inspection:
type(obj)             # <class '__main__.MyClass'>
isinstance(obj, MyClass)   # True
issubclass(MyClass, object)  # True

# Attribute inspection:
dir(obj)              # all attributes and methods (including inherited)
vars(obj)             # obj.__dict__ — instance attributes only
vars(MyClass)         # class namespace

hasattr(obj, "method")    # True
getattr(obj, "method")    # <bound method>
setattr(obj, "x", 10)     # obj.x = 10
delattr(obj, "x")          # del obj.x

# inspect module — deep inspection:
inspect.getmembers(MyClass)                  # all name/value pairs
inspect.getdoc(MyClass)                      # "A sample class."
inspect.getsource(MyClass)                   # source code as string
inspect.signature(MyClass.method)            # (self, x: int) -> str
inspect.isclass(MyClass)                     # True
inspect.isfunction(MyClass.method)           # True (unbound)
inspect.ismethod(obj.method)                 # True (bound)

# Signature:
sig = inspect.signature(MyClass.method)
for name, param in sig.parameters.items():
    print(name, param.annotation, param.default)
```

---

## 📐 Chapter 13: Typing and Protocols

**Protocol** enables structural subtyping (duck typing with type-checker support):

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    """Any class with a draw() method satisfies this Protocol."""
    def draw(self) -> None: ...

class Circle:
    def draw(self):
        print("○")

class Square:
    def draw(self):
        print("□")

class NotDrawable:
    def something_else(self): ...

# Works at runtime (because @runtime_checkable):
isinstance(Circle(), Drawable)        # True
isinstance(NotDrawable(), Drawable)   # False

def render(shape: Drawable) -> None:
    shape.draw()   # type-safe!

render(Circle())   # ✅
render(Square())   # ✅
render(NotDrawable())  # TypeError at runtime, type error at check time
```

**Key typing features:**

```python
from typing import (
    Optional,      # X | None  (use X | None in Python 3.10+)
    Union,         # A | B
    List, Dict, Tuple, Set,  # use list, dict, tuple, set in Python 3.9+
    TypeVar,       # generic type variable
    Generic,       # generic class base
    Callable,      # callable with signature
    Any,           # disable type checking
    ClassVar,      # class-level variable
    Final,         # constant
    Literal,       # specific literal values
    TypedDict,     # dict with typed keys
    overload,      # multiple signatures
)

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

s: Stack[int] = Stack()
s.push(42)
x: int = s.pop()
```

---

## 🔥 Summary Table

```
FEATURE            WHAT IT IS                        WHEN TO USE
────────────────────────────────────────────────────────────────────────────
Dunder methods     Hooks into Python syntax          Always — define repr, eq, etc
__repr__ / __str__ Object representation             Every custom class
__eq__ + __hash__  Equality + hashability            When used in sets/dicts
Operator overload  Define +, -, *, ==, etc.          Math/science classes
Container protocol __len__, __getitem__, __iter__    Custom collection types
__bool__           Truthiness                        When 0 ≠ False for your type
__slots__          Memory optimization               10k+ instances of same class
Descriptors        Managed attribute access          Validation, computed attrs
@property          Computed attribute                Input validation, derived values
Metaclass          Factory for classes               Frameworks, plugin systems
__init_subclass__  Hook when class is subclassed     Simpler alternative to metaclass
@dataclass         Auto-generated boilerplate        Data container classes
ABC                Interface definition              Define contracts in libraries
Enum               Named constants                   Status codes, flags, categories
Protocol           Structural typing                 Duck typing with type safety
Introspection      Runtime object inspection         Debug, frameworks, serialization
```

---

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🔮 Dunder Methods Guide | [dunder_guide.md](./dunder_guide.md) |
| 🏭 Metaclasses & Descriptors | [metaclasses_descriptors_guide.md](./metaclasses_descriptors_guide.md) |
| ➡️ Next | [16 — Design Patterns](../16_design_patterns/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Type Hints And Pydantic — Interview Q&A](../14_type_hints_and_pydantic/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Dunder Methods Guide](./dunder_guide.md) · [Metaclasses & Descriptors](./metaclasses_descriptors_guide.md) · [Interview Q&A](./interview.md)
