# 💻 Advanced Python — Practice
# Run with: python3 practice.py

# =============================================================================
# SECTION 1: __slots__ — Memory Optimization
# =============================================================================

# By default every Python object stores its attributes in a __dict__ (a hash
# table). __slots__ replaces that with a fixed C-level array — smaller, faster,
# and prevents accidental typo-attributes.

import sys

print("=" * 60)
print("SECTION 1: __slots__")
print("=" * 60)

class PointDict:
    """Normal class — uses __dict__ for attribute storage."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

class PointSlots:
    """Same class with __slots__ — no __dict__, fixed attribute set."""
    __slots__ = ('x', 'y')  # only these attribute names are allowed

    def __init__(self, x, y):
        self.x = x
        self.y = y

p_dict  = PointDict(1, 2)
p_slots = PointSlots(1, 2)

# sys.getsizeof only measures the object header; add __dict__ size for full picture
dict_size  = sys.getsizeof(p_dict) + sys.getsizeof(p_dict.__dict__)
slots_size = sys.getsizeof(p_slots)

print(f"  PointDict  size: {dict_size} bytes (object + __dict__)")
print(f"  PointSlots size: {slots_size} bytes (no __dict__)")
print(f"  Saving: {dict_size - slots_size} bytes per instance")
print(f"  At 1M instances: ~{(dict_size - slots_size) * 1_000_000 // 1024 // 1024} MB saved")

# __slots__ prevents adding new attributes — good for catching typos
try:
    p_slots.z = 99  # not in __slots__ — raises AttributeError
except AttributeError as e:
    print(f"  Blocked typo-attribute: {e}")

# __dict__ is gone
print(f"  hasattr(p_slots, '__dict__'): {hasattr(p_slots, '__dict__')}")
print()


# =============================================================================
# SECTION 2: __getattr__, __setattr__, __delattr__ — Attribute Interception
# =============================================================================

# __getattr__      called ONLY when normal lookup fails (last resort)
# __getattribute__ called for EVERY attribute access (use with care)
# __setattr__      called on EVERY attribute assignment
# __delattr__      called on every del obj.attr

print("=" * 60)
print("SECTION 2: __getattr__ / __setattr__ / __delattr__")
print("=" * 60)

class TrackedObject:
    """Records every set/delete; uses __getattr__ as a fallback for missing attrs."""

    def __init__(self):
        # Use object.__setattr__ to bypass our own __setattr__ for internal state
        object.__setattr__(self, '_data', {})
        object.__setattr__(self, '_access_log', [])

    def __setattr__(self, name, value):
        # Intercept every assignment — log it, then store in _data
        self._access_log.append(f"SET   {name} = {value!r}")
        self._data[name] = value

    def __getattr__(self, name):
        # Only called when normal lookup fails (not in instance or class dict)
        if name in self._data:
            self._access_log.append(f"GET   {name}")
            return self._data[name]
        raise AttributeError(f"No attribute {name!r}")

    def __delattr__(self, name):
        if name in self._data:
            self._access_log.append(f"DEL   {name}")
            del self._data[name]
        else:
            raise AttributeError(f"No attribute {name!r} to delete")

obj = TrackedObject()
obj.name  = "Alice"
obj.score = 99
_ = obj.name
del obj.score

print("  Access log:")
for entry in obj._access_log:
    print(f"    {entry}")
print()


# Lazy attribute computation using __getattr__
class LazyConfig:
    """Computes expensive values only on first access, then caches them."""

    def __getattr__(self, name):
        # This only runs when normal lookup fails — perfect for lazy init
        if name == "heavy_data":
            print("  [LazyConfig] Computing heavy_data for the first time...")
            value = list(range(100))  # imagine this is expensive
            # Store in instance __dict__ directly — next access hits __dict__ first
            # so __getattr__ won't be called again (it's only a fallback)
            object.__setattr__(self, 'heavy_data', value)
            return value
        raise AttributeError(f"No lazy attr {name!r}")

cfg = LazyConfig()
print("  First access (computed):")
_ = cfg.heavy_data
print("  Second access (cached, __getattr__ NOT called):")
_ = cfg.heavy_data
print()


# =============================================================================
# SECTION 3: Descriptors — Data and Non-Data
# =============================================================================

# A descriptor is any class with __get__, __set__, or __delete__.
# DATA descriptor:     has __set__ (or __delete__) → overrides instance __dict__
# NON-DATA descriptor: only __get__                → instance __dict__ wins

print("=" * 60)
print("SECTION 3: Descriptors")
print("=" * 60)

class ValidatedNumber:
    """Data descriptor: validates and stores a numeric attribute."""

    def __set_name__(self, owner, name):
        # Called when descriptor is assigned to a class body attribute.
        # Gives us the attribute name without needing to pass it manually.
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self  # class-level access returns the descriptor itself
        return obj.__dict__.get(self.name, 0)

    def __set__(self, obj, value):
        # Validation runs on every assignment
        if not isinstance(value, (int, float)):
            raise TypeError(f"{self.name}: expected number, got {type(value).__name__}")
        if value < 0:
            raise ValueError(f"{self.name}: must be >= 0, got {value}")
        obj.__dict__[self.name] = value  # store directly to avoid recursion

    def __delete__(self, obj):
        obj.__dict__.pop(self.name, None)


class Product:
    price    = ValidatedNumber()  # descriptor instance as class attribute
    quantity = ValidatedNumber()

    def __init__(self, name, price, quantity):
        self.name     = name      # normal attribute — goes to __dict__
        self.price    = price     # triggers ValidatedNumber.__set__
        self.quantity = quantity

    def total(self):
        return self.price * self.quantity

    def __repr__(self):
        return f"Product({self.name!r}, price={self.price}, qty={self.quantity})"

p = Product("Widget", 9.99, 100)
print(f"  {p}")
print(f"  Total: {p.total():.2f}")

try:
    p.price = -1.0
except ValueError as e:
    print(f"  Caught: {e}")

try:
    p.quantity = "lots"
except TypeError as e:
    print(f"  Caught: {e}")

# Accessing descriptor on the CLASS returns the descriptor object itself
print(f"  Product.price is: {Product.price!r}")
print()


# Non-data descriptor — functions are non-data descriptors
# This is how methods work: func.__get__(instance, class) returns a bound method
class NonDataDescriptor:
    """Only __get__ — instance __dict__ takes priority."""

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return f"descriptor value for {obj!r}"

class Demo:
    x = NonDataDescriptor()

d = Demo()
print(f"  Non-data descriptor: {d.x}")
# Override by writing directly to instance __dict__
d.__dict__['x'] = "instance wins!"
print(f"  After instance assignment: {d.x}")  # instance dict takes priority
print()


# =============================================================================
# SECTION 4: Metaclasses — type() and Custom Metaclasses
# =============================================================================

# type(name, bases, namespace) is the built-in metaclass — it creates all classes.
# Custom metaclasses run code at class-creation time (not instance-creation time).

print("=" * 60)
print("SECTION 4: Metaclasses")
print("=" * 60)

# Dynamic class creation with type()
# Equivalent to: class Point: x = 0; y = 0
PointDynamic = type('PointDynamic', (object,), {'x': 0, 'y': 0,
                    '__repr__': lambda self: f"PointDynamic({self.x}, {self.y})"})
pt = PointDynamic()
pt.x, pt.y = 3, 4
print(f"  Dynamically created class: {pt}")


# Metaclass for auto-registering subclasses (plugin registry pattern)
class PluginMeta(type):
    """Every class created with this metaclass is auto-registered."""
    registry = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases:  # skip the base class itself
            mcs.registry[name] = cls
            print(f"  [PluginMeta] Registered: {name}")
        return cls

class Plugin(metaclass=PluginMeta):
    """Base class — all subclasses auto-registered."""
    def execute(self):
        raise NotImplementedError

class CSVPlugin(Plugin):
    def execute(self):
        return "processing CSV"

class JSONPlugin(Plugin):
    def execute(self):
        return "processing JSON"

print(f"\n  Registry: {list(PluginMeta.registry.keys())}")

# Use registry to instantiate by name
plugin = PluginMeta.registry["CSVPlugin"]()
print(f"  CSVPlugin.execute(): {plugin.execute()}")
print()


# =============================================================================
# SECTION 5: __init_subclass__ — Modern Alternative to Metaclasses
# =============================================================================

# __init_subclass__ was added in Python 3.6.
# It's a classmethod hook on the base class that fires whenever a subclass
# is defined — cleaner than metaclasses for most registration use cases.

print("=" * 60)
print("SECTION 5: __init_subclass__")
print("=" * 60)

class Command:
    """Base class — auto-registers subclasses by their command name."""
    _registry: dict = {}

    def __init_subclass__(cls, name=None, **kwargs):
        super().__init_subclass__(**kwargs)  # cooperate with MRO
        if name:
            Command._registry[name] = cls
            print(f"  [Command] Registered command: {name!r} → {cls.__name__}")

    @classmethod
    def run(cls, name, *args):
        if name not in cls._registry:
            raise ValueError(f"Unknown command: {name!r}")
        return cls._registry[name]().execute(*args)


class RunCommand(Command, name="run"):
    def execute(self, *args):
        return f"running with args: {args}"

class StopCommand(Command, name="stop"):
    def execute(self, *args):
        return "stopping"

print(f"\n  All commands: {list(Command._registry.keys())}")
print(f"  {Command.run('run', 'arg1', 'arg2')}")
print(f"  {Command.run('stop')}")
print()


# =============================================================================
# SECTION 6: Abstract Base Classes (ABCs)
# =============================================================================

# ABCs let you define an interface: a contract that subclasses MUST fulfill.
# Attempting to instantiate a class with unimplemented abstract methods raises
# TypeError at instantiation time — not at call time.

from abc import ABC, abstractmethod

print("=" * 60)
print("SECTION 6: Abstract Base Classes (ABCs)")
print("=" * 60)

class StorageBackend(ABC):
    """Interface: any concrete storage must implement save, load, delete."""

    @abstractmethod
    def save(self, key: str, value: str) -> None:
        """Store a value under key."""
        ...

    @abstractmethod
    def load(self, key: str) -> str:
        """Retrieve value by key; raise KeyError if not found."""
        ...

    def exists(self, key: str) -> bool:
        """Optional — has a default implementation."""
        try:
            self.load(key)
            return True
        except KeyError:
            return False

# Can't instantiate an abstract class:
try:
    StorageBackend()
except TypeError as e:
    print(f"  Can't instantiate ABC: {e}")

# Concrete implementation satisfies the contract
class InMemoryStorage(StorageBackend):
    def __init__(self):
        self._store = {}

    def save(self, key, value):
        self._store[key] = value

    def load(self, key):
        if key not in self._store:
            raise KeyError(key)
        return self._store[key]

store = InMemoryStorage()
store.save("config", "debug=true")
print(f"  load('config') = {store.load('config')!r}")
print(f"  exists('config') = {store.exists('config')}")
print(f"  exists('missing') = {store.exists('missing')}")
print()


# =============================================================================
# SECTION 7: Protocol — Structural Typing (Duck Typing + Type Safety)
# =============================================================================

# Protocol defines an interface by structure, not inheritance.
# A class satisfies a Protocol simply by having the right methods/attributes —
# no import of the Protocol class required. This is "duck typing for type checkers."

from typing import Protocol, runtime_checkable

print("=" * 60)
print("SECTION 7: Protocol (structural typing)")
print("=" * 60)

@runtime_checkable  # enables isinstance() checks at runtime
class Drawable(Protocol):
    """Any class with a draw() method satisfies this protocol."""
    def draw(self) -> str:
        ...

class Circle:
    def draw(self) -> str:
        return "drawing a circle O"

class Square:
    def draw(self) -> str:
        return "drawing a square []"

class Triangle:
    # No draw() method — does NOT satisfy Drawable
    def render(self):
        return "rendering a triangle"

def render_all(shapes: list) -> None:
    for shape in shapes:
        if isinstance(shape, Drawable):
            print(f"  {shape.draw()}")
        else:
            print(f"  {type(shape).__name__} is not Drawable — skipped")

shapes = [Circle(), Square(), Triangle()]
render_all(shapes)

print(f"\n  isinstance(Circle(), Drawable):   {isinstance(Circle(), Drawable)}")
print(f"  isinstance(Triangle(), Drawable): {isinstance(Triangle(), Drawable)}")
print()


# =============================================================================
# SECTION 8: __class_getitem__ — Generic Class Subscripting
# =============================================================================

# __class_getitem__ is called when you write MyClass[T].
# Used to support generic type hints: list[int], dict[str, int], Stack[str].

print("=" * 60)
print("SECTION 8: __class_getitem__")
print("=" * 60)

class TypedStack:
    """A stack that remembers its declared element type for type hints."""

    def __init__(self):
        self._items = []

    def __class_getitem__(cls, item):
        # Called when someone writes TypedStack[int]
        # Return a parameterized version (here we keep it simple)
        print(f"  [TypedStack] Subscripted with: {item}")
        return cls

    def push(self, value):
        self._items.append(value)

    def pop(self):
        return self._items.pop()

    def __repr__(self):
        return f"TypedStack({self._items})"

# This is how type checkers know TypedStack[int] means "stack of ints"
IntStack = TypedStack[int]        # triggers __class_getitem__
s = TypedStack()
s.push(1)
s.push(2)
print(f"  {s}")
print(f"  pop: {s.pop()}")
print()


# =============================================================================
# SECTION 9: Putting It Together — A Validated Dataclass-Style Class
# =============================================================================

# Combines: __slots__, descriptor validation, __repr__, __eq__, __hash__

print("=" * 60)
print("SECTION 9: Putting it all together — validated record type")
print("=" * 60)

class TypedField:
    """Descriptor: validates type on assignment."""

    def __set_name__(self, owner, name):
        self.name = name

    def __init__(self, expected_type):
        self.expected_type = expected_type
        self.name = None  # set by __set_name__

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name}: expected {self.expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
        obj.__dict__[self.name] = value


class User:
    __slots__ = ('__dict__', '__weakref__')  # allow __dict__ alongside __slots__

    name  = TypedField(str)
    age   = TypedField(int)
    email = TypedField(str)

    def __init__(self, name, age, email):
        self.name  = name
        self.age   = age
        self.email = email

    def __repr__(self):
        return f"User(name={self.name!r}, age={self.age}, email={self.email!r})"

    def __eq__(self, other):
        if not isinstance(other, User):
            return NotImplemented
        return (self.name, self.age, self.email) == (other.name, other.age, other.email)

    def __hash__(self):
        return hash((self.name, self.age, self.email))


alice = User("Alice", 30, "alice@example.com")
alice2 = User("Alice", 30, "alice@example.com")

print(f"  {alice}")
print(f"  alice == alice2: {alice == alice2}")
print(f"  hash(alice) == hash(alice2): {hash(alice) == hash(alice2)}")
print(f"  In a set: {len({alice, alice2})} unique user(s)")

try:
    alice.age = "thirty"
except TypeError as e:
    print(f"  Type enforcement: {e}")

print()
print("All advanced Python examples complete.")
