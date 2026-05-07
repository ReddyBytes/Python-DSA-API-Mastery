# Advanced Patterns — Deep Dive

When a hammer is both a tool and a data record, you reach for `__slots__`, callable objects, and introspection. These three patterns form the **infrastructure layer** of Python — the machinery that powers decorators, ORMs, plugin systems, and testing frameworks. Understanding them is what separates library authors from library users.

> Key fact: `__slots__` replaces per-instance `__dict__` with a compact C-level array. Callable objects make functions out of instances. Introspection lets code examine and modify itself at runtime.

---

## Learning Priority

**Must Learn:** `__slots__` memory optimization · callable objects (`__call__`) · `dir` / `hasattr` / `getattr`

**Should Learn:** `inspect` module · `__all__` · `vars()` · `type()` at runtime

**Good to Know:** `__subclasses__()` · `__mro__` · `object.__dict__` vs instance `__dict__`

**Reference:** `sys.getrefcount` · `gc` module

---

## Chapter 1: `__slots__` — Memory Optimization

By default, every Python instance stores its attributes in a `__dict__` (a hash table). Dicts are flexible but carry significant memory overhead — ~200-300 bytes for the dict itself, plus per-entry overhead for each attribute.

`__slots__` replaces `__dict__` with a fixed C-level array:

```
Class with 3 attributes:
  Without __slots__:  ~360 bytes  (instance + dict + dict entries)
  With    __slots__:   ~72 bytes  (instance + 3 slots)
  Savings: ~5x smaller
```

```python
class PointDict:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class PointSlots:
    __slots__ = ("x", "y")   # ← declare slots here

    def __init__(self, x, y):
        self.x = x
        self.y = y

import sys
p1 = PointDict(1.0, 2.0)
p2 = PointSlots(1.0, 2.0)

# Full memory: dict instance + its __dict__ + slot instance (no __dict__)
print(sys.getsizeof(p1) + sys.getsizeof(p1.__dict__))   # ~360 bytes
print(sys.getsizeof(p2))                                 # ~72 bytes

# Slot attributes are member_descriptors — data descriptors on the class:
print(type(PointSlots.x))   # <class 'member_descriptor'>

# Can't add attributes not in __slots__:
p2.z = 3.0   # AttributeError: 'PointSlots' object has no attribute 'z'

# No __dict__ on slots instance:
hasattr(p2, '__dict__')   # False
```

**Memory impact at scale (100,000 instances):**

```python
import tracemalloc

def measure(cls, n=100_000):
    tracemalloc.start()
    before = tracemalloc.take_snapshot()
    objs = [cls(float(i), float(i)) for i in range(n)]
    after = tracemalloc.take_snapshot()
    tracemalloc.stop()
    return sum(s.size_diff for s in after.compare_to(before, "lineno")), objs

dict_mem, _ = measure(PointDict)
slot_mem, _ = measure(PointSlots)
print(f"PointDict:  {dict_mem / 1e6:.1f} MB")    # ~35 MB
print(f"PointSlots: {slot_mem / 1e6:.1f} MB")    # ~ 8 MB
print(f"Ratio: {dict_mem / slot_mem:.1f}x savings")
```

---

## Chapter 2: `__slots__` with Inheritance

```python
class Animal:
    __slots__ = ("name", "weight")

    def __init__(self, name, weight):
        self.name, self.weight = name, weight

class Dog(Animal):
    __slots__ = ("breed",)   # ← only NEW slots here; inherits parent slots

    def __init__(self, name, weight, breed):
        super().__init__(name, weight)
        self.breed = breed

d = Dog("Rex", 30.0, "Husky")
print(d.name, d.breed)   # works — slots from both classes available
```

**If a parent does NOT use `__slots__`**, the child still gets a `__dict__`:

```python
class WithDict:
    def __init__(self): self.x = 1

class ChildWithSlots(WithDict):
    __slots__ = ("y",)   # ← slot for y

c = ChildWithSlots()
c.y = 2
c.z = 3      # OK! — parent's __dict__ is still there
```

**Keep `__dict__` and `__weakref__` when you need flexibility:**

```python
class Flexible:
    __slots__ = ("x", "y", "__dict__", "__weakref__")   # ← explicit inclusion

    def __init__(self, x, y):
        self.x, self.y = x, y

f = Flexible(1, 2)
f.z = 3        # OK — __dict__ is back
```

---

## Chapter 3: Pickling `__slots__` Classes

Classes with `__slots__` and no `__dict__` need custom pickle support:

```python
import pickle

class PicklableSlots:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y

    def __getstate__(self):
        return {"x": self.x, "y": self.y}   # ← return slot values as dict

    def __setstate__(self, state):
        self.x = state["x"]                  # ← restore from dict
        self.y = state["y"]

    def __repr__(self):
        return f"PicklableSlots(x={self.x}, y={self.y})"

ps = PicklableSlots(10, 20)
restored = pickle.loads(pickle.dumps(ps))
print(restored)   # PicklableSlots(x=10, y=20)
```

---

## Chapter 4: Callable Objects — `__call__`

Any object with `__call__` can be called like a function. Callable objects are superior to plain functions when you need **state between calls** or **configurable behavior**:

```python
class MovingAverage:
    """Callable object that maintains state between calls."""

    def __init__(self, window):
        self.window = window
        self._history = []

    def __call__(self, value):
        self._history.append(value)
        if len(self._history) > self.window:
            self._history.pop(0)
        return sum(self._history) / len(self._history)

    def reset(self):
        self._history.clear()

ma5 = MovingAverage(5)
for v in [10, 20, 30, 15, 25, 35]:
    print(f"{v:3d} → avg: {ma5(v):.1f}")

callable(ma5)   # True — checks type(ma5).__call__
```

**Use case: configurable predicates:**

```python
class Threshold:
    def __init__(self, lo=None, hi=None):
        self.lo, self.hi = lo, hi

    def __call__(self, x):
        if self.lo is not None and x < self.lo: return False
        if self.hi is not None and x > self.hi: return False
        return True

is_valid_port = Threshold(lo=1, hi=65535)
print(list(filter(is_valid_port, [0, 80, 443, 65536])))   # [80, 443]
```

**Use case: memoization:**

```python
class Memoized:
    def __init__(self, func):
        self.func = func
        self._cache = {}
        self.hits = self.misses = 0
        self.__name__ = getattr(func, '__name__', str(func))

    def __call__(self, *args):
        if args in self._cache:
            self.hits += 1
            return self._cache[args]
        self.misses += 1
        result = self.func(*args)
        self._cache[args] = result
        return result

    def cache_info(self):
        return {"hits": self.hits, "misses": self.misses, "size": len(self._cache)}

@Memoized
def fibonacci(n):
    if n <= 1: return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(40))
print(fibonacci.cache_info())
```

---

## Chapter 5: Introspection Built-ins

Python's introspection built-ins let you examine any object at runtime:

```
Function             What it returns
---------------------------------------------------------------
type(obj)            obj's class
isinstance(obj, T)   True if obj is instance of T or T subclass
issubclass(A, B)     True if A is a subclass of B
dir(obj)             list of all accessible names
vars(obj)            obj's __dict__ (or class's namespace)
hasattr(obj, name)   True if obj has this attribute
getattr(obj, name)   get attribute; raises AttributeError if missing
getattr(obj, n, d)   get attribute; returns d if missing
setattr(obj, n, v)   set attribute
delattr(obj, name)   delete attribute
callable(obj)        True if type(obj) has __call__
id(obj)              unique object identity (memory address in CPython)
```

```python
class Animal:
    species = "Unknown"

    def __init__(self, name, weight):
        self.name, self.weight = name, weight

    def speak(self): raise NotImplementedError
    @classmethod
    def from_dict(cls, d): return cls(d["name"], d["weight"])

class Dog(Animal):
    species = "Canis lupus familiaris"
    def __init__(self, name, weight, breed):
        super().__init__(name, weight)
        self.breed = breed
    def speak(self): return f"Woof! I'm {self.name}"

dog = Dog("Rex", 30.0, "Husky")

print(type(dog))                  # <class '__main__.Dog'>
print(type(dog).__bases__)        # (<class '__main__.Animal'>,)
print(type(dog).__mro__)          # [Dog, Animal, object]
print(isinstance(dog, Animal))    # True  — works for inheritance
print(type(dog) is Animal)        # False — strict equality, misses inheritance

# dir() vs vars():
public = [n for n in dir(dog) if not n.startswith("_")]
print(public)             # ['breed', 'from_dict', 'name', 'speak', 'species', 'weight']
print(vars(dog))          # {'name': 'Rex', 'weight': 30.0, 'breed': 'Husky'}
print(vars(Dog))          # class namespace (mappingproxy)

# Dynamic attribute access:
print(getattr(dog, "breed", "unknown"))    # Husky
print(getattr(dog, "color", "not set"))   # not set  (default)
hasattr(dog, "speak")                      # True
```

---

## Chapter 6: The `inspect` Module

```python
import inspect

class Dog:
    """A dog that barks."""
    def __init__(self, name: str, weight: float, breed: str): ...
    def speak(self) -> str: ...

dog = Dog("Rex", 30.0, "Husky")

# Signature introspection:
sig = inspect.signature(Dog.__init__)
print(f"Dog.__init__ signature: {sig}")
for name, param in sig.parameters.items():
    print(f"  {name}: kind={param.kind.name}, default={param.default!r}")

# Type checks:
print(inspect.isfunction(Dog.speak))   # True
print(inspect.ismethod(dog.speak))     # True
print(inspect.isclass(Dog))           # True
print(inspect.isbuiltin(len))         # True

# MRO:
print(inspect.getmro(Dog))   # (Dog, Animal, object) — same as Dog.__mro__

# Docstring:
print(inspect.getdoc(Dog))   # "A dog that barks."

# Members filtered by predicate:
methods = [(n, v) for n, v in inspect.getmembers(dog, inspect.ismethod)
           if not n.startswith("_")]
print(methods)   # [('speak', <bound method ...>)]
```

---

## Chapter 7: `__all__` — Controlling Module Exports

`__all__` is a list of names that are exported when someone does `from module import *`. It also signals to IDEs and linters what the public API is.

```python
# mymodule.py
__all__ = ['PublicClass', 'public_function']   # ← only these are exported by *

class PublicClass:
    """Part of the public API."""
    pass

def public_function():
    """Part of the public API."""
    pass

def _internal_helper():
    """NOT exported — underscore signals internal use."""
    pass

class _InternalClass:
    """NOT exported."""
    pass
```

---

## Chapter 8: Runtime Type Discovery — `__subclasses__`, `__mro__`

```python
class Animal: pass
class Dog(Animal): pass
class Cat(Animal): pass
class Poodle(Dog): pass

# Direct subclasses only:
print(Animal.__subclasses__())   # [<class 'Dog'>, <class 'Cat'>]
print(Dog.__subclasses__())      # [<class 'Poodle'>]

# All subclasses (recursive):
def all_subclasses(cls):
    result = []
    for sub in cls.__subclasses__():
        result.append(sub)
        result.extend(all_subclasses(sub))
    return result

print(all_subclasses(Animal))   # [Dog, Cat, Poodle]

# MRO — method resolution order:
print(Poodle.__mro__)   # (Poodle, Dog, Animal, object)
```

**Plugin system using `__subclasses__`:**

```python
class Plugin:
    name = None

    @classmethod
    def all_plugins(cls):
        return {p.name: p for p in cls.__subclasses__() if p.name}

class JSONPlugin(Plugin):
    name = "json"
    def serialize(self, data): import json; return json.dumps(data)

class CSVPlugin(Plugin):
    name = "csv"
    def serialize(self, data): return ",".join(str(x) for x in data)

print(Plugin.all_plugins())   # {'json': JSONPlugin, 'csv': CSVPlugin}
```

---

## Chapter 9: `vars()` and `object.__dict__`

```python
class Config:
    debug = False   # class variable

    def __init__(self, host, port):
        self.host = host
        self.port = port

cfg = Config("localhost", 8080)

# Instance __dict__ — only instance attributes:
print(vars(cfg))         # {'host': 'localhost', 'port': 8080}
print(cfg.__dict__)      # same thing

# Class __dict__ — class attributes and methods:
print(vars(Config))      # mappingproxy({'debug': False, '__init__': ..., ...})

# Class variable NOT in instance __dict__:
print("debug" in vars(cfg))      # False — it's on the class
print("debug" in vars(Config))   # True
```

---

## Common Mistakes

**Using `__slots__` but forgetting it in subclass — silently re-enables `__dict__`:**
```python
class Base:
    __slots__ = ('x',)

class Child(Base):
    pass   # ← no __slots__ → child gets __dict__ back! Memory savings lost.
    # Fix: __slots__ = ('y',)  — even empty tuple matters
```

**Using `callable()` on instance attribute (not class attribute):**
```python
class Foo:
    pass

f = Foo()
f.__call__ = lambda: 42   # instance attribute — NOT the class's __call__
callable(f)               # False — callable checks type(f).__call__
f.__call__()              # 42  — but direct call works
```

**`vars()` on object without `__dict__` raises `TypeError`:**
```python
class Slots:
    __slots__ = ('x',)

s = Slots()
vars(s)   # TypeError: vars() argument must have __dict__ attribute
```

**`dir()` returns ALL names including inherited — use `vars()` for just the instance's own:**
```python
print(len(dir(dog)))        # 30+ (everything inherited too)
print(len(vars(dog)))       # 3  (just name, weight, breed)
```

---

## Navigation

| | |
|---|---|
| Root theory | [../theory.md](../theory.md) |
| Root practice | [../practice.md](../practice.md) |
| Practice | [practice.md](./practice.md) |
| Prev: Dataclasses | [../04_dataclasses/theory.md](../04_dataclasses/theory.md) |

**[Back to 15_advanced_python](../theory.md)**
