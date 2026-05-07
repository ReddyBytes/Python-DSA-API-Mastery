"""
10_decorators/class_decorators.py
====================================
CONCEPT: Class decorators — decorators that work with classes, and
decorators implemented as classes.
WHY THIS MATTERS: @dataclass, @property, @classmethod, @staticmethod are
all class decorators you use every day. Understanding them unlocks custom
data modeling, plugin systems, and advanced framework patterns.

Prerequisite: Modules 01–10 function_decorators.py
"""

import functools
import time
import inspect
from dataclasses import dataclass, field

# =============================================================================
# SECTION 1: A class-based decorator
# =============================================================================

# CONCEPT: A decorator can also be a CLASS. The class implements:
# __init__: receives the decorated function
# __call__: called when the decorated function is invoked
# WHY use a class: when the decorator needs to maintain STATE across calls
# (e.g., call counter, circuit breaker state, connection pool).

print("=== Section 1: Class-Based Decorators ===")

class CallCounter:
    """
    Class decorator that counts how many times a function has been called.
    WHY CLASS vs FUNCTION: we need to store and update `count` across calls.
    A class naturally holds this state in `self.count`.
    """

    def __init__(self, func):
        functools.update_wrapper(self, func)   # same as @functools.wraps
        self.func   = func
        self.count  = 0
        self.errors = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        try:
            return self.func(*args, **kwargs)
        except Exception as e:
            self.errors += 1
            raise

    def stats(self) -> dict:
        return {
            "function":    self.func.__name__,
            "total_calls": self.count,
            "errors":      self.errors,
            "success_rate": f"{(self.count - self.errors) / max(self.count, 1) * 100:.1f}%",
        }


@CallCounter
def process_order(order_id: int, amount: float) -> str:
    if amount <= 0:
        raise ValueError(f"Invalid amount: {amount}")
    return f"Order {order_id} processed: ${amount:.2f}"


process_order(1, 99.99)
process_order(2, 149.99)
try:
    process_order(3, -5.00)
except ValueError:
    pass

print(f"Call stats: {process_order.stats()}")

# Class decorator with configuration (needs __init__ with params)
class RateLimit:
    """
    Class decorator that enforces a rate limit (max N calls per second).
    State (call timestamps) is stored in the instance.
    """

    def __init__(self, max_calls: int, period: float = 1.0):
        self.max_calls = max_calls
        self.period    = period
        self._calls    = []   # list of timestamps for recent calls

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove calls older than `period` seconds
            self._calls = [t for t in self._calls if now - t < self.period]

            if len(self._calls) >= self.max_calls:
                raise RuntimeError(
                    f"Rate limit exceeded: {self.max_calls} calls per {self.period}s"
                )
            self._calls.append(now)
            return func(*args, **kwargs)
        return wrapper


rate_limiter = RateLimit(max_calls=3, period=1.0)

@rate_limiter
def send_sms(number: str, message: str) -> str:
    return f"SMS sent to {number}: {message[:20]}"

print("\nRate limit:")
for i in range(5):
    try:
        result = send_sms(f"+1555{i:04d}", f"Message {i}")
        print(f"  ✓ {result}")
    except RuntimeError as e:
        print(f"  ✗ {e}")


# =============================================================================
# SECTION 2: Decorating classes — adding behavior at class level
# =============================================================================

# CONCEPT: A decorator applied to a CLASS receives the class itself.
# It can add methods, modify attributes, register the class, or return
# a completely different object. @dataclass is the most famous example.

print("\n=== Section 2: Decorators That Modify Classes ===")

# Singleton decorator — ensures only one instance
def singleton(cls):
    """
    Class decorator that makes a class a singleton.
    The first call creates the instance; subsequent calls return the same one.
    WHY decorator: clean, reusable, doesn't pollute the class body.
    """
    instances = {}   # class → instance mapping (closure)

    @functools.wraps(cls, updated=[])
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class AppConfig:
    """Global application configuration — one instance only."""
    def __init__(self, env: str = "development"):
        self.env = env
        self.debug = env != "production"
        print(f"  AppConfig created: env={env}")

cfg1 = AppConfig("production")
cfg2 = AppConfig("staging")   # config already created — returns same instance
print(f"cfg1 is cfg2: {cfg1 is cfg2}")   # True
print(f"cfg2.env: {cfg2.env}")           # "production" — cfg2 is cfg1!


# Auto-register decorator — plugin/extension registration pattern
class Registry:
    """Central registry for all registered handlers."""
    _handlers: dict = {}

    @classmethod
    def register(cls, name: str):
        """Decorator factory: @Registry.register("my_handler")"""
        def decorator(handler_class):
            cls._handlers[name] = handler_class
            print(f"  Registered handler: {name}")
            return handler_class   # return the class unchanged
        return decorator

    @classmethod
    def get(cls, name: str):
        if name not in cls._handlers:
            raise KeyError(f"No handler registered: {name}")
        return cls._handlers[name]()

    @classmethod
    def all_names(cls) -> list:
        return list(cls._handlers.keys())


@Registry.register("csv")
class CSVHandler:
    def process(self, data): return f"CSV: {data}"

@Registry.register("json")
class JSONHandler:
    def process(self, data): return f"JSON: {data}"

@Registry.register("xml")
class XMLHandler:
    def process(self, data): return f"XML: {data}"

print(f"\nRegistered handlers: {Registry.all_names()}")
for name in Registry.all_names():
    handler = Registry.get(name)
    print(f"  {name}: {handler.process('sample_data')}")


# =============================================================================
# SECTION 3: @dataclass — Python's most powerful built-in class decorator
# =============================================================================

# CONCEPT: @dataclass auto-generates __init__, __repr__, __eq__,
# and optionally __hash__, __lt__, etc. from type-annotated class attributes.
# This eliminates the boilerplate of writing __init__ for every data class.
# WHY: A 5-attribute class needs 20+ lines of __init__ boilerplate —
# @dataclass reduces it to 5 clean lines.

print("\n=== Section 3: @dataclass ===")

@dataclass
class Point:
    """__init__, __repr__, __eq__ auto-generated."""
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        import math
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

p1 = Point(3.0, 4.0)
p2 = Point(6.0, 8.0)
print(f"p1 = {p1}")                               # auto __repr__
print(f"p1 == Point(3.0, 4.0): {p1 == Point(3.0, 4.0)}")  # auto __eq__
print(f"distance: {p1.distance_to(p2):.2f}")

# @dataclass with defaults, field(), frozen, and ordering
@dataclass(order=True, frozen=True)
class Version:
    """
    frozen=True: immutable, hashable (can be used as dict key / in sets)
    order=True:  auto-generates __lt__, __le__, __gt__, __ge__
    field(compare=False): exclude `description` from comparisons
    """
    major: int
    minor: int
    patch: int = 0
    description: str = field(default="", compare=False)

v1 = Version(2, 1, 3)
v2 = Version(2, 0, 5)
v3 = Version(3, 0, 0, description="Major release")

versions = [v1, v2, v3]
print(f"\nSorted versions: {sorted(versions)}")
print(f"Latest: {max(versions)}")
print(f"v1 > v2: {v1 > v2}")
print(f"v3.description: {v3.description}")

# Frozen dataclass as dict key
release_notes = {Version(1, 0): "Initial release", Version(2, 0): "API revamp"}
print(f"v1.0 notes: {release_notes[Version(1, 0)]}")


# =============================================================================
# SECTION 4: Combining class decorators for clean data models
# =============================================================================

# CONCEPT: Stack decorators to compose behavior.
# @dataclass provides __init__/__repr__/__eq__.
# A custom @validated decorator adds input validation.

print("\n=== Section 4: Combining Decorators ===")

def validated(cls):
    """
    Class decorator that runs `validate()` in __post_init__ (dataclass hook).
    Combines with @dataclass to add validation to generated __init__.
    """
    original_post_init = getattr(cls, "__post_init__", None)

    def new_post_init(self):
        if original_post_init:
            original_post_init(self)
        if hasattr(self, "validate"):
            self.validate()

    cls.__post_init__ = new_post_init
    return cls


@validated
@dataclass
class User:
    """Validated data model — @validated runs after @dataclass generates __init__."""
    name: str
    email: str
    age: int
    role: str = "user"

    def validate(self):
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("Name must be at least 2 characters")
        if "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email}")
        if not 0 <= self.age <= 150:
            raise ValueError(f"Age out of range: {self.age}")

# Valid user
alice = User("Alice", "alice@example.com", 30)
print(f"Valid user: {alice}")

# Invalid user — validated at creation
try:
    bad = User("A", "not-an-email", -5)
except ValueError as e:
    print(f"Validation error: {e}")


print("\n=== Class decorators complete ===")
print("Key class decorator patterns:")
print("  Class AS decorator: use when you need state across multiple calls")
print("  @singleton:  class-level pattern, one instance per process")
print("  @Registry:   plugin registration without touching the registry code")
print("  @dataclass:  eliminates __init__, __repr__, __eq__ boilerplate")
print("  @validated:  combine with @dataclass for validated data models")
