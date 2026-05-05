# Descriptors — Theory + Practice

# =============================================================================
# THEORY: The Descriptor Protocol
# =============================================================================
#
# A descriptor is any object whose class defines one or more of:
#   __get__(self, obj, objtype=None)  → read access
#   __set__(self, obj, value)         → write access
#   __delete__(self, obj)             → delete access
#
# Descriptors live as CLASS attributes. They intercept attribute access
# on INSTANCES of that class.
#
# TWO TYPES:
#   Data Descriptor:      defines __get__ + __set__ (and/or __delete__)
#   Non-Data Descriptor:  defines __get__ only
#
# ATTRIBUTE LOOKUP PRIORITY (when you do obj.name):
#   1. Data descriptor in type(obj).__mro__     ← HIGHEST
#   2. obj.__dict__["name"]
#   3. Non-data descriptor in type(obj).__mro__  ← LOWEST
#
# This priority order is why @property (a data descriptor) works even though
# self.__dict__ is right there. And why cached lazy properties (non-data
# descriptors) can be overridden by instance __dict__ after first access.
#
# __set_name__(self, owner, name) — called at class creation time:
#   owner = the class that owns this descriptor
#   name  = the attribute name in that class
# =============================================================================

import re
import math
from typing import Any, Callable


# =============================================================================
# SECTION 1: Minimal descriptor example
# =============================================================================

class Celsius:
    """
    Simple data descriptor: validates temperature is >= -273.15 (absolute zero).
    """

    def __set_name__(self, owner, name):
        self.public_name  = name
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self   # accessed via class: Temperature.temp → descriptor object
        return getattr(obj, self.private_name, None)

    def __set__(self, obj, value: float):
        value = float(value)
        if value < -273.15:
            raise ValueError(
                f"{self.public_name} = {value} is below absolute zero (-273.15°C)"
            )
        setattr(obj, self.private_name, value)

    def __delete__(self, obj):
        delattr(obj, self.private_name)

class Temperature:
    celsius = Celsius()   # __set_name__ called: public_name="celsius"

    def __init__(self, celsius: float):
        self.celsius = celsius   # triggers Celsius.__set__

    @property
    def fahrenheit(self) -> float:
        return self.celsius * 9/5 + 32

    @property
    def kelvin(self) -> float:
        return self.celsius + 273.15

t = Temperature(100)
print(f"{t.celsius}°C = {t.fahrenheit}°F = {t.kelvin}K")

try:
    Temperature(-300)    # raises ValueError
except ValueError as e:
    print(f"Caught: {e}")


# =============================================================================
# SECTION 2: Non-data descriptor — lazy property (cached)
# =============================================================================

class cached_property:
    """
    Non-data descriptor that computes a value once and caches it in
    instance __dict__. On second access, instance __dict__ (priority 2)
    takes over from the non-data descriptor (priority 3).
    """

    def __init__(self, func: Callable):
        self.func = func
        self.__doc__ = func.__doc__
        self.__name__ = func.__name__

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        # Compute and cache in instance __dict__:
        value = self.func(obj)
        obj.__dict__[self.name] = value   # bypasses descriptor next time
        return value

class HeavyModel:
    def __init__(self, data: list):
        self.data = data

    @cached_property
    def sorted_data(self) -> list:
        """Expensive sort — done only once."""
        print("  Sorting...")
        return sorted(self.data)

    @cached_property
    def statistics(self) -> dict:
        """Stats — computed once."""
        d = self.sorted_data
        return {
            "min": d[0],
            "max": d[-1],
            "mean": sum(d) / len(d),
            "median": d[len(d)//2],
        }

model = HeavyModel([5, 3, 1, 4, 2])
print(model.sorted_data)   # "Sorting..."  → [1, 2, 3, 4, 5]
print(model.sorted_data)   # No "Sorting..." — cached
print(model.statistics)    # Uses cached sorted_data


# =============================================================================
# SECTION 3: Range validator descriptor (with class-level access)
# =============================================================================

class RangeValidator:
    """
    Validates numeric values within [min_val, max_val].
    Demonstrates accessing the descriptor from the class itself.
    """

    def __init__(self, min_val=None, max_val=None, type_=None):
        self.min_val = min_val
        self.max_val = max_val
        self.type_   = type_

    def __set_name__(self, owner, name):
        self.name    = name
        self.private = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            # Allow: MyClass.field → returns descriptor with metadata
            return self
        val = obj.__dict__.get(self.private)
        if val is None:
            raise AttributeError(f"{self.name!r} not set")
        return val

    def __set__(self, obj, value):
        if self.type_ is not None:
            try:
                value = self.type_(value)
            except (TypeError, ValueError):
                raise TypeError(f"{self.name} must be convertible to {self.type_.__name__}")

        if self.min_val is not None and value < self.min_val:
            raise ValueError(f"{self.name} = {value!r} below minimum {self.min_val!r}")
        if self.max_val is not None and value > self.max_val:
            raise ValueError(f"{self.name} = {value!r} above maximum {self.max_val!r}")
        obj.__dict__[self.private] = value

    def __delete__(self, obj):
        obj.__dict__.pop(self.private, None)

    def __repr__(self):
        return (
            f"RangeValidator(name={self.name!r}, "
            f"min={self.min_val}, max={self.max_val}, type={self.type_})"
        )

class NetworkConfig:
    port    = RangeValidator(min_val=1,    max_val=65535, type_=int)
    timeout = RangeValidator(min_val=0.1,  max_val=300.0, type_=float)
    retries = RangeValidator(min_val=0,    max_val=10,    type_=int)

    def __init__(self, port, timeout=30.0, retries=3):
        self.port    = port
        self.timeout = timeout
        self.retries = retries

cfg = NetworkConfig(port=8080, timeout=10.0, retries=5)
print(f"Config: port={cfg.port}, timeout={cfg.timeout}, retries={cfg.retries}")

# Access via class returns descriptor (useful for introspection):
print(NetworkConfig.port)   # RangeValidator(name='port', ...)

try:
    NetworkConfig(port=0)   # below minimum
except ValueError as e:
    print(f"Caught: {e}")


# =============================================================================
# SECTION 4: Logging descriptor (access tracking)
# =============================================================================

class Audited:
    """
    Records every read and write to an attribute.
    Shows how descriptors can add cross-cutting concerns without modifying
    the class logic.
    """

    def __init__(self):
        self._log: list[tuple] = []

    def __set_name__(self, owner, name):
        self.name    = name
        self.private = f"_audited_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.private)
        self._log.append(("READ",  id(obj), self.name, value))
        return value

    def __set__(self, obj, value):
        old = obj.__dict__.get(self.private)
        self._log.append(("WRITE", id(obj), self.name, value, "was", old))
        obj.__dict__[self.private] = value

    def get_log(self) -> list:
        return list(self._log)

class BankAccount:
    balance = Audited()

    def __init__(self, initial_balance: float):
        self.balance = initial_balance

    def deposit(self, amount: float):
        self.balance += amount

    def withdraw(self, amount: float):
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount

acc = BankAccount(1000.0)
acc.deposit(500.0)
acc.withdraw(200.0)
print(f"Balance: {acc.balance}")

print("\nAudit log:")
for entry in BankAccount.balance.get_log():
    print(f"  {entry}")


# =============================================================================
# SECTION 5: Unit conversion descriptor
# =============================================================================

class Unit:
    """
    Descriptor that stores a value in a canonical unit (e.g., meters)
    but allows setting/getting in any unit.
    """

    def __init__(self, to_canonical: float, from_canonical: float = None):
        """
        to_canonical: multiply to convert user value → canonical
        from_canonical: multiply to convert canonical → user value
        """
        self.to_canonical   = to_canonical
        self.from_canonical = from_canonical or (1.0 / to_canonical)
        self.name = None

    def __set_name__(self, owner, name):
        self.name    = name
        self.private = f"_canonical_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        canonical = obj.__dict__.get(self.private, 0.0)
        return canonical * self.from_canonical

    def __set__(self, obj, value: float):
        obj.__dict__[self.private] = float(value) * self.to_canonical

class Distance:
    meters     = Unit(to_canonical=1.0)
    kilometers = Unit(to_canonical=1000.0)
    miles      = Unit(to_canonical=1609.344)
    feet       = Unit(to_canonical=0.3048)

    def __init__(self, **kwargs):
        if len(kwargs) != 1:
            raise ValueError("Provide exactly one unit")
        unit, value = next(iter(kwargs.items()))
        setattr(self, unit, value)

d = Distance(miles=26.2)        # Marathon distance
print(f"Marathon: {d.miles:.2f} miles")
print(f"        = {d.kilometers:.3f} km")
print(f"        = {d.meters:.0f} m")
print(f"        = {d.feet:.0f} feet")


# =============================================================================
# PRACTICE PROBLEMS
# =============================================================================

# ── Problem 1 ──────────────────────────────────────────────────────────────
# Create a TypedList descriptor that stores a list but enforces that all
# elements are of a specified type. Support:
#   - obj.items = [1, 2, 3]     → validates each element
#   - obj.items.append(4)        → TRICKY: need to return a guarded list
#   Hint: return a special subclass of list that validates on append/extend

# ── Problem 2 ──────────────────────────────────────────────────────────────
# Build a Bounded descriptor that clamps values to [lo, hi] rather than
# raising an error. It should also support read-only mode (no setter) and
# write-only mode (getter raises AttributeError).
# Tests:
#   class Slider:
#       value = Bounded(0, 100)
#   s = Slider(); s.value = 150  → s.value == 100 (clamped)
#   s.value = -10  → s.value == 0

# ── Problem 3 ──────────────────────────────────────────────────────────────
# Implement a Once descriptor: allows setting the value exactly once.
# After the first set, further sets raise AttributeError.
# Tests:
#   class Config:
#       host = Once()
#   c = Config()
#   c.host = "localhost"   # OK
#   c.host = "other"       # raises AttributeError: host already set


# =============================================================================
# SOLUTIONS
# =============================================================================

# Solution: Once descriptor
class Once:
    """Allows setting a value exactly once."""

    def __set_name__(self, owner, name):
        self.name    = name
        self.private = f"_once_{name}"
        self.flag    = f"_once_set_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        try:
            return obj.__dict__[self.private]
        except KeyError:
            raise AttributeError(f"{self.name!r} not yet set")

    def __set__(self, obj, value):
        if obj.__dict__.get(self.flag, False):
            raise AttributeError(f"{self.name!r} is already set and cannot be changed")
        obj.__dict__[self.private] = value
        obj.__dict__[self.flag]    = True

class ImmutableConfig:
    host = Once()
    port = Once()

    def __init__(self, host, port):
        self.host = host
        self.port = port

cfg = ImmutableConfig("localhost", 8080)
print(cfg.host, cfg.port)

try:
    cfg.host = "other"
except AttributeError as e:
    print(f"Caught: {e}")

print("Descriptor tests passed!")
