# Metaclasses — Theory + Practice

# =============================================================================
# THEORY: How classes are created in Python
# =============================================================================
#
# In Python, EVERYTHING is an object — including classes. A class is an
# instance of its metaclass. The default metaclass is `type`.
#
#   42           is an instance of  int
#   int          is an instance of  type
#   type         is an instance of  type  (type is its own metaclass)
#
# When you write:
#   class Dog:
#       def bark(self): ...
#
# Python executes:
#   1. Execute the class body in a fresh namespace (dict)
#   2. Call metaclass("Dog", (object,), namespace) to create the class object
#
# This is equivalent to:
#   Dog = type("Dog", (object,), {"bark": <function>})
#
# A custom metaclass lets you intercept and modify STEP 2.
#
# WHEN TO USE METACLASSES:
#   - Auto-registering subclasses (plugin systems, ORM models)
#   - Enforcing class-level constraints (abstract interface checkers)
#   - Injecting class-level methods or attributes automatically
#   - Framework plumbing (Django, SQLAlchemy, Pydantic all use metaclasses)
#
# WHEN TO PREFER __init_subclass__ (simpler):
#   - You only need to run code when a class is subclassed
#   - You don't need to modify the class namespace before creation
# =============================================================================

from __future__ import annotations
from abc import ABCMeta, abstractmethod
import functools
import inspect


# =============================================================================
# SECTION 1: type() — the default metaclass
# =============================================================================

# Three-argument type() creates a class at runtime:
Point = type(
    "Point",            # name
    (object,),          # bases
    {
        "__init__": lambda self, x, y: (
            setattr(self, "x", x) or setattr(self, "y", y)
        ),
        "distance": lambda self: (self.x**2 + self.y**2) ** 0.5,
        "__repr__": lambda self: f"Point({self.x}, {self.y})",
    }
)

p = Point(3, 4)
print(p)                  # Point(3, 4)
print(p.distance())       # 5.0
print(type(p))            # <class '__main__.Point'>
print(isinstance(p, type("object", (), {}).__class__))  # demonstrates it's all objects


# =============================================================================
# SECTION 2: Custom metaclass — registry pattern
# =============================================================================

class RegistryMeta(type):
    """
    Metaclass that auto-registers every concrete subclass.
    Classic plugin / handler registration pattern.
    """

    _registry: dict[str, type] = {}

    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        cls = super().__new__(mcs, name, bases, namespace)

        # Don't register the abstract base itself — only concrete subclasses:
        if bases:   # has at least one parent (not the root class)
            mcs._registry[name] = cls
            print(f"  Registered: {name}")

        return cls

    @classmethod
    def get(mcs, name: str) -> type:
        return mcs._registry[name]

    @classmethod
    def all_handlers(mcs) -> dict:
        return dict(mcs._registry)


class Handler(metaclass=RegistryMeta):
    """Abstract base — not registered (no bases before metaclass)."""

    def handle(self, data: dict) -> str:
        raise NotImplementedError

class JSONHandler(Handler):      # prints: Registered: JSONHandler
    def handle(self, data):
        import json
        return json.dumps(data)

class XMLHandler(Handler):       # prints: Registered: XMLHandler
    def handle(self, data):
        pairs = " ".join(f'{k}="{v}"' for k,v in data.items())
        return f"<data {pairs}/>"

# Route by name:
def dispatch(format: str, data: dict) -> str:
    handler_cls = RegistryMeta.get(f"{format.upper()}Handler")
    return handler_cls().handle(data)

print(dispatch("JSON", {"name": "Alice", "age": 30}))
print(dispatch("XML",  {"name": "Alice", "age": 30}))


# =============================================================================
# SECTION 3: Validation metaclass
# =============================================================================

class InterfaceMeta(type):
    """
    Enforces that all public methods in concrete classes have docstrings
    and return type annotations. Catches missing documentation at import time.
    """

    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        is_abstract = namespace.get("__abstract__", False)

        if not is_abstract:
            for attr, value in namespace.items():
                if attr.startswith("_"):
                    continue
                if not callable(value):
                    continue

                # Check docstring:
                if not value.__doc__:
                    raise TypeError(
                        f"{name}.{attr}: public methods require a docstring"
                    )

                # Check return annotation:
                hints = getattr(value, "__annotations__", {})
                if "return" not in hints:
                    raise TypeError(
                        f"{name}.{attr}: public methods require a return type annotation"
                    )

        return super().__new__(mcs, name, bases, namespace)


class ServiceBase(metaclass=InterfaceMeta):
    __abstract__ = True   # skip validation for base itself

class UserService(ServiceBase):
    def get_user(self, user_id: int) -> dict:
        """Retrieve a user by ID."""
        return {"id": user_id, "name": "Alice"}

    def list_users(self) -> list:
        """List all users."""
        return []

# This would raise TypeError at class definition time:
# class BadService(ServiceBase):
#     def get_user(self, user_id):   # no annotation, no docstring
#         pass

print("UserService passed validation!")


# =============================================================================
# SECTION 4: ORM metaclass — field collection
# =============================================================================

class FieldDescriptor:
    """Simple field with type enforcement."""

    def __init__(self, type_: type, default=None, required: bool = True):
        self.type_    = type_
        self.default  = default
        self.required = required
        self.name     = None

    def __set_name__(self, owner, name):
        self.name    = name
        self.private = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return obj.__dict__.get(self.private, self.default)

    def __set__(self, obj, value):
        if value is None and self.required:
            raise ValueError(f"{self.name} is required")
        if value is not None and not isinstance(value, self.type_):
            raise TypeError(
                f"{self.name} must be {self.type_.__name__}, got {type(value).__name__}"
            )
        obj.__dict__[self.private] = value


class ModelMeta(type):
    """
    Metaclass that collects all FieldDescriptor attributes into _fields dict
    and generates __init__, __repr__, __eq__ automatically.
    """

    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        # Collect fields defined in THIS class:
        fields = {
            k: v
            for k, v in namespace.items()
            if isinstance(v, FieldDescriptor)
        }

        # Inherit parent fields:
        inherited = {}
        for base in reversed(bases):
            if hasattr(base, "_fields"):
                inherited.update(base._fields)

        all_fields = {**inherited, **fields}
        namespace["_fields"] = all_fields

        # Auto-generate __init__:
        def __init__(self, **kwargs):
            for fname, fdesc in self._fields.items():
                value = kwargs.get(fname, fdesc.default)
                setattr(self, fname, value)
            if hasattr(self, "__post_init__"):
                self.__post_init__()

        # Auto-generate __repr__:
        def __repr__(self):
            pairs = ", ".join(
                f"{k}={getattr(self, k)!r}"
                for k in self._fields
            )
            return f"{type(self).__name__}({pairs})"

        # Auto-generate __eq__:
        def __eq__(self, other):
            if type(self) is not type(other):
                return NotImplemented
            return all(
                getattr(self, k) == getattr(other, k)
                for k in self._fields
            )

        if "__init__" not in namespace:
            namespace["__init__"] = __init__
        if "__repr__" not in namespace:
            namespace["__repr__"] = __repr__
        if "__eq__" not in namespace:
            namespace["__eq__"] = __eq__

        return super().__new__(mcs, name, bases, namespace)


class Model(metaclass=ModelMeta):
    pass   # base model — no fields

class User(Model):
    username = FieldDescriptor(str)
    age      = FieldDescriptor(int)
    email    = FieldDescriptor(str, required=False)

class AdminUser(User):
    # Inherits username, age, email from User:
    permissions = FieldDescriptor(list, default=[])

u1 = User(username="alice", age=30)
u2 = User(username="alice", age=30)
u3 = User(username="bob",   age=25)

print(u1)          # User(username='alice', age=30, email=None)
print(u1 == u2)    # True
print(u1 == u3)    # False

admin = AdminUser(username="root", age=40, permissions=["read", "write"])
print(admin)


# =============================================================================
# SECTION 5: __init_subclass__ — the lighter alternative
# =============================================================================

class Event:
    """
    Event system using __init_subclass__.
    Each subclass registers its event_type automatically.
    Simpler than a metaclass for this use case.
    """
    _handlers: dict[str, type] = {}
    event_type: str = ""

    def __init_subclass__(cls, event_type: str = "", **kwargs):
        super().__init_subclass__(**kwargs)
        if event_type:
            cls.event_type = event_type
            Event._handlers[event_type] = cls

    @classmethod
    def dispatch(cls, event_type: str, **data):
        handler_cls = cls._handlers.get(event_type)
        if handler_cls is None:
            raise KeyError(f"No handler for event type: {event_type!r}")
        return handler_cls(**data).process()

    def process(self):
        raise NotImplementedError

class UserCreated(Event, event_type="user.created"):
    def __init__(self, user_id, username):
        self.user_id  = user_id
        self.username = username

    def process(self):
        return f"Welcome email sent to {self.username} (id={self.user_id})"

class OrderPlaced(Event, event_type="order.placed"):
    def __init__(self, order_id, total):
        self.order_id = order_id
        self.total    = total

    def process(self):
        return f"Order #{self.order_id} confirmed, total=${self.total}"

print(Event.dispatch("user.created", user_id=42, username="alice"))
print(Event.dispatch("order.placed", order_id=101, total=99.99))


# =============================================================================
# SECTION 6: Singleton metaclass
# =============================================================================

class SingletonMeta(type):
    """
    Makes any class using this metaclass a singleton.
    __call__ controls what happens when cls(...) is invoked.
    """
    _instances: dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class AppConfig(metaclass=SingletonMeta):
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.db_url = "postgresql://localhost/app"

config1 = AppConfig(debug=True)
config2 = AppConfig()            # returns SAME instance
print(config1 is config2)        # True
print(config1.debug)             # True (not reset by second call)


# =============================================================================
# PRACTICE PROBLEMS
# =============================================================================

# ── Problem 1 ──────────────────────────────────────────────────────────────
# Write a CachingMeta metaclass that wraps all public methods with an LRU cache.
# Any class with this metaclass should have its public methods memoized.
# Tests:
#   class Fibonacci(metaclass=CachingMeta):
#       def fib(self, n):
#           if n <= 1: return n
#           return self.fib(n-1) + self.fib(n-2)
#   f = Fibonacci()
#   f.fib(35)   # should be fast due to caching

# ── Problem 2 ──────────────────────────────────────────────────────────────
# Build a CountMeta metaclass that adds a call_count attribute to every
# public method. After calling method N times, method.call_count == N.
# Tests:
#   class Calculator(metaclass=CountMeta):
#       def add(self, a, b): return a + b
#       def mul(self, a, b): return a * b
#   c = Calculator()
#   c.add(1, 2); c.add(3, 4)
#   Calculator.add.call_count == 2

# ── Problem 3 ──────────────────────────────────────────────────────────────
# Use __init_subclass__ to build a state machine framework:
#   - Base class StateMachine defines states and transitions
#   - Each method decorated with @transition(from_state, to_state) is only
#     callable when the machine is in from_state
#   - Calling it transitions to to_state
#   - Calling from wrong state raises InvalidTransition


# =============================================================================
# SOLUTION: CachingMeta (simplified)
# =============================================================================

from functools import lru_cache

class CachingMeta(type):
    def __new__(mcs, name, bases, namespace):
        new_ns = {}
        for key, value in namespace.items():
            if not key.startswith("_") and callable(value):
                # Wrap with lru_cache (max 128 entries):
                value = lru_cache(maxsize=128)(value)
            new_ns[key] = value
        return super().__new__(mcs, name, bases, new_ns)

class Fibonacci(metaclass=CachingMeta):
    def fib(self, n: int) -> int:
        if n <= 1:
            return n
        return self.fib(n - 1) + self.fib(n - 2)

import time
f = Fibonacci()
start = time.perf_counter()
result = f.fib(35)
elapsed = time.perf_counter() - start
print(f"fib(35) = {result}, elapsed: {elapsed*1000:.2f}ms (cached!)")
