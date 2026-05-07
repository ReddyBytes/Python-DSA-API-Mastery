# Descriptors — Deep Dive

Think of descriptors as **smart attributes** — class-level objects that intercept every read, write, or delete of an attribute on any instance. `@property` is just one built-in descriptor. `classmethod`, `staticmethod`, and `__slots__` are all descriptors too. Once you understand the protocol, you can build validators, caches, loggers, and ORMs from first principles.

> Key fact: a descriptor is any object whose **class** defines `__get__`, `__set__`, or `__delete__`. It lives as a class attribute and intercepts access on instances of that class.

---

## Learning Priority

**Must Learn:** descriptor protocol · `__get__` · `__set__` · how `@property` uses descriptors

**Should Learn:** `__delete__` · data vs non-data descriptors · `__set_name__`

**Good to Know:** WeakValueDictionary for descriptor storage · classmethod/staticmethod internals

**Reference:** `__get__` on class vs instance · slot descriptors

---

## Chapter 1: The Descriptor Protocol

A descriptor is defined by which of these three methods its class implements:

```
Method                          Signature
---------------------------------------------------------------------------
__get__(self, obj, objtype)     obj.name  or  Class.name
__set__(self, obj, value)       obj.name = value
__delete__(self, obj)           del obj.name
__set_name__(self, owner, name) called at class creation — descriptor learns its name
```

**Data descriptor vs Non-data descriptor:**

```
Data Descriptor          Non-Data Descriptor
------------------------------------------------------------
Defines __get__ AND      Defines __get__ ONLY
__set__ (or __delete__)

Takes PRIORITY over      Instance __dict__ takes
instance __dict__        PRIORITY over it
```

**Attribute lookup order** when you access `obj.name`:

```
1. type(obj).__mro__ → search for DATA DESCRIPTOR
   → call descriptor.__get__(obj, type(obj))

2. obj.__dict__["name"]
   → return it if found

3. type(obj).__mro__ → NON-DATA DESCRIPTOR or class variable
   → call descriptor.__get__(obj, type(obj))

4. type(obj).__getattr__(obj, "name")  if defined

5. AttributeError
```

This order explains everything. It's why `@property` (a data descriptor) intercepts `self.x` even though `self.__dict__` is right there. And why cached lazy properties (non-data descriptors) can be overridden by writing to instance `__dict__`.

---

## Chapter 2: Minimal Descriptor Example

```python
class Celsius:
    """Data descriptor: validates temperature is >= absolute zero."""

    def __set_name__(self, owner, name):
        self.public_name  = name
        self.private_name = f"_{name}"   # ← store actual value under _celsius

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self   # ← accessed via class: Temperature.celsius → descriptor object
        return getattr(obj, self.private_name, None)

    def __set__(self, obj, value):
        value = float(value)
        if value < -273.15:
            raise ValueError(f"{self.public_name} below absolute zero")
        setattr(obj, self.private_name, value)   # ← store on instance, not descriptor

    def __delete__(self, obj):
        delattr(obj, self.private_name)

class Temperature:
    celsius = Celsius()   # ← __set_name__ called here: public_name="celsius"

    def __init__(self, celsius):
        self.celsius = celsius   # ← triggers Celsius.__set__

t = Temperature(100)
print(t.celsius)   # triggers Celsius.__get__ → 100
Temperature(-300)  # raises ValueError
```

**Critical pitfall — shared state:**

```python
# WRONG: storing value on the descriptor object itself
class BadDescriptor:
    def __get__(self, obj, objtype=None):
        return self.value   # ← shared across ALL instances!
    def __set__(self, obj, value):
        self.value = value  # ← WRONG: b1.x = 42 sets b2.x too!

# CORRECT: store value in obj.__dict__ keyed by name
class GoodDescriptor:
    def __set_name__(self, owner, name):
        self._key = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return obj.__dict__.get(self._key)

    def __set__(self, obj, value):
        obj.__dict__[self._key] = value   # ← per-instance storage
```

---

## Chapter 3: `__set_name__` — Descriptor Knows Its Own Name

Before Python 3.6, descriptors had to be told their name manually or use a metaclass. `__set_name__` fixed this:

```python
class MyDescriptor:
    def __set_name__(self, owner, name):
        # owner: the class where this descriptor is assigned
        # name: the attribute name used in that class
        self.name = name
        self.private = f"_{name}"
        print(f"Assigned to {owner.__name__}.{name}")

class MyClass:
    x = MyDescriptor()   # prints: "Assigned to MyClass.x"
    y = MyDescriptor()   # prints: "Assigned to MyClass.y"
```

---

## Chapter 4: Data vs Non-Data — Lookup Priority in Practice

```python
class DataDesc:
    """Has __set__ — takes priority over instance __dict__."""
    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return obj.__dict__.get('_x', 'from descriptor')
    def __set__(self, obj, value):
        obj.__dict__['_x'] = value

class NonDataDesc:
    """Only __get__ — instance __dict__ wins."""
    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return 'from descriptor'

class Demo:
    data    = DataDesc()
    nondata = NonDataDesc()

d = Demo()
# data descriptor — even after writing to __dict__ directly, descriptor wins:
d.__dict__['data'] = 'in dict'
print(d.data)      # 'from descriptor'  (DataDesc.__get__ still called!)

# non-data descriptor — instance __dict__ wins:
d.__dict__['nondata'] = 'in dict'
print(d.nondata)   # 'in dict'  (descriptor bypassed!)
```

---

## Chapter 5: `@property` — The Built-In Descriptor

`property` is just a descriptor class. Here is its Python equivalent:

```python
class property_:
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget, self.fset, self.fdel = fget, fset, fdel
        self.__doc__ = doc or (fget.__doc__ if fget else None)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self                        # ← class access: Circle.radius → property object
        if self.fget is None:
            raise AttributeError("unreadable")
        return self.fget(obj)                  # ← instance access: calls getter

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set")
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete")
        self.fdel(obj)

    def getter(self, fget): return type(self)(fget, self.fset, self.fdel, self.__doc__)
    def setter(self, fset): return type(self)(self.fget, fset, self.fdel, self.__doc__)
    def deleter(self, fdel): return type(self)(self.fget, self.fset, fdel, self.__doc__)

# property is a DATA descriptor (has __get__ and __set__)
# This is WHY @property intercepts self.x even though self.__dict__ is right there
```

Usage:

```python
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
```

---

## Chapter 6: Validator Descriptor

```python
class RangeValidator:
    """Validates numeric values within [min_val, max_val]."""

    def __init__(self, min_val=None, max_val=None, type_=None):
        self.min_val = min_val
        self.max_val = max_val
        self.type_   = type_

    def __set_name__(self, owner, name):
        self.name    = name
        self.private = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self   # ← class access returns descriptor (useful for introspection)
        val = obj.__dict__.get(self.private)
        if val is None:
            raise AttributeError(f"{self.name!r} not set")
        return val

    def __set__(self, obj, value):
        if self.type_ is not None:
            value = self.type_(value)   # ← coerce type first
        if self.min_val is not None and value < self.min_val:
            raise ValueError(f"{self.name} = {value!r} below minimum {self.min_val!r}")
        if self.max_val is not None and value > self.max_val:
            raise ValueError(f"{self.name} = {value!r} above maximum {self.max_val!r}")
        obj.__dict__[self.private] = value

    def __delete__(self, obj):
        obj.__dict__.pop(self.private, None)

class NetworkConfig:
    port    = RangeValidator(min_val=1,   max_val=65535, type_=int)
    timeout = RangeValidator(min_val=0.1, max_val=300.0, type_=float)

    def __init__(self, port, timeout=30.0):
        self.port    = port
        self.timeout = timeout

cfg = NetworkConfig(8080)
print(cfg.port)      # 8080
NetworkConfig(0)     # raises ValueError
print(NetworkConfig.port)  # → RangeValidator object (class access)
```

---

## Chapter 7: Non-Data Descriptor — Cached Lazy Property

```python
class cached_property:
    """
    Computes a value once, caches in instance __dict__.
    Non-data descriptor — no __set__ — so instance __dict__ takes priority
    on second access, bypassing the descriptor entirely.
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
        obj.__dict__[self.name] = value   # ← cache in instance __dict__
        return value                       # next access: __dict__ found first, skips descriptor

class HeavyModel:
    def __init__(self, data):
        self.data = data

    @cached_property
    def sorted_data(self):
        print("  Sorting...")
        return sorted(self.data)

model = HeavyModel([5, 3, 1, 4, 2])
print(model.sorted_data)   # "Sorting..."  → [1, 2, 3, 4, 5]
print(model.sorted_data)   # No print — served from instance __dict__
```

---

## Chapter 8: Logging Descriptor — Access Tracking

```python
class Audited:
    """Records every read and write to an attribute."""

    def __init__(self):
        self._log = []

    def __set_name__(self, owner, name):
        self.name    = name
        self.private = f"_audited_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        value = obj.__dict__.get(self.private)
        self._log.append(("READ", id(obj), self.name, value))
        return value

    def __set__(self, obj, value):
        old = obj.__dict__.get(self.private)
        self._log.append(("WRITE", id(obj), self.name, value, "was", old))
        obj.__dict__[self.private] = value

    def get_log(self):
        return list(self._log)

class BankAccount:
    balance = Audited()

    def __init__(self, initial):
        self.balance = initial

    def deposit(self, amount):
        self.balance += amount

acc = BankAccount(1000.0)
acc.deposit(500.0)
print(BankAccount.balance.get_log())
```

---

## Chapter 9: How `__slots__` Uses Descriptors

When you define `__slots__`, Python creates **member descriptors** — data descriptors — for each slot. They store values in a compact C-level array, not `__dict__`.

```python
class Compact:
    __slots__ = ('x', 'y', 'z')

    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

print(type(Compact.x))   # <class 'member_descriptor'>
# Each slot IS a data descriptor — has both __get__ and __set__
# obj.x calls Compact.x.__get__(obj, Compact)
# obj.x = 5 calls Compact.x.__set__(obj, 5)
```

---

## Common Mistakes

**Not handling `obj is None` in `__get__`:**
```python
def __get__(self, obj, objtype=None):
    # Missing obj is None check — breaks: MyClass.field (class access)
    return obj.__dict__[self.name]  # AttributeError: 'NoneType' has no attribute '__dict__'
```

**Using `setattr` instead of `obj.__dict__` — causes infinite recursion:**
```python
def __set__(self, obj, value):
    setattr(obj, self.name, value)   # ← WRONG: calls __set__ again → RecursionError
    # CORRECT:
    obj.__dict__[f"_{self.name}"] = value
```

**Sharing state on the descriptor (not on instances):**
```python
class Bad:
    def __init__(self):
        self.value = None   # ← one value shared by ALL instances using this descriptor!
```

---

## Navigation

| | |
|---|---|
| Root theory | [../theory.md](../theory.md) |
| Root practice | [../practice.md](../practice.md) |
| Practice | [practice.md](./practice.md) |
| Prev: Dunder Methods | [../01_dunder_methods/theory.md](../01_dunder_methods/theory.md) |
| Next: Metaclasses | [../03_metaclasses/theory.md](../03_metaclasses/theory.md) |

**[Back to 15_advanced_python](../theory.md)**
