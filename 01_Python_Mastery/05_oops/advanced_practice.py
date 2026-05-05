"""
05_oops/advanced_practice.py
==============================
CONCEPT: Advanced OOP patterns — dunder methods, MRO, descriptors, mixins.
WHY THIS MATTERS: These patterns appear in Django ORM, SQLAlchemy, Pydantic,
NumPy, and virtually every mature Python library. Understanding them lets you
write code that integrates naturally with Python's ecosystem.

Prerequisite: 05_oops/practice.py (basic OOP concepts)
"""

from abc import ABC, abstractmethod
from functools import total_ordering
import math

# =============================================================================
# SECTION 1: Dunder (magic) methods — making objects behave like builtins
# =============================================================================

# CONCEPT: Dunder methods (double underscore) let your objects integrate with
# Python's built-in operations. When you write `a + b`, Python calls `a.__add__(b)`.
# When you write `len(obj)`, Python calls `obj.__len__()`.
# WHY: This is how NumPy arrays support +, *, @. How Pandas Series support slicing.
# How pathlib.Path supports / for joining paths. Python's "operator overloading."

print("=== Section 1: Dunder Methods ===")

@total_ordering   # gives us __gt__, __le__, __ge__ for free from __eq__ + __lt__
class Vector:
    """2D vector with full operator support — like a mini NumPy array."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    # --- Representation ---
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

    def __str__(self):
        return f"({self.x}, {self.y})"

    # --- Arithmetic operators ---
    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector":
        """Scalar multiplication: v * 2"""
        return Vector(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vector":
        """Reverse multiplication: 2 * v (when left side doesn't know Vector)"""
        return self.__mul__(scalar)

    def __neg__(self) -> "Vector":
        """Unary negation: -v"""
        return Vector(-self.x, -self.y)

    def __abs__(self) -> float:
        """abs(v) returns the magnitude (length of vector)"""
        return math.sqrt(self.x**2 + self.y**2)

    # --- Comparison ---
    def __eq__(self, other) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented   # let Python try the reverse
        return self.x == other.x and self.y == other.y

    def __lt__(self, other) -> bool:
        return abs(self) < abs(other)   # compare by magnitude

    # --- Container-like behavior ---
    def __len__(self) -> int:
        return 2   # a 2D vector always has 2 components

    def __getitem__(self, index: int) -> float:
        """v[0] returns x, v[1] returns y"""
        if index == 0: return self.x
        if index == 1: return self.y
        raise IndexError(f"Vector index {index} out of range (0-1)")

    def __iter__(self):
        """for component in v: yields x, then y"""
        yield self.x
        yield self.y

    def __bool__(self) -> bool:
        """False if zero vector, True otherwise"""
        return self.x != 0 or self.y != 0

    # --- Utility ---
    def dot(self, other: "Vector") -> float:
        return self.x * other.x + self.y * other.y

    def normalize(self) -> "Vector":
        mag = abs(self)
        if mag == 0:
            raise ValueError("Cannot normalize zero vector")
        return Vector(self.x / mag, self.y / mag)

# Demonstrating operator overloading in action:
v1 = Vector(3, 4)
v2 = Vector(1, 2)

print(f"v1 = {v1}, v2 = {v2}")
print(f"v1 + v2 = {v1 + v2}")
print(f"v1 - v2 = {v1 - v2}")
print(f"v1 * 3  = {v1 * 3}")
print(f"3 * v1  = {3 * v1}")          # uses __rmul__
print(f"abs(v1) = {abs(v1)}")          # magnitude = 5.0
print(f"-v1     = {-v1}")              # uses __neg__
print(f"v1[0]   = {v1[0]}, v1[1] = {v1[1]}")  # uses __getitem__
print(f"v1 components: {list(v1)}")    # uses __iter__
print(f"v1 > v2: {v1 > v2}")          # from @total_ordering + __lt__
print(f"v1 == Vector(3,4): {v1 == Vector(3,4)}")
print(f"dot product: {v1.dot(v2)}")
print(f"normalized: {v1.normalize()}")


# =============================================================================
# SECTION 2: Abstract Base Classes — enforcing interfaces
# =============================================================================

# CONCEPT: ABC makes certain methods REQUIRED in subclasses.
# If a subclass doesn't implement an abstract method, instantiating it raises TypeError.
# WHY: Ensures that all subclasses provide the required interface. Better than
# `raise NotImplementedError` in base class (ABCs enforce this at class creation).

print("\n=== Section 2: Abstract Base Classes ===")

class DataStore(ABC):
    """
    Abstract interface for any data storage backend.
    All subclasses MUST implement get, set, and delete.
    WHY: code that uses a DataStore doesn't need to know if it's Redis,
    a file, a database, or an in-memory dict.
    """

    @abstractmethod
    def get(self, key: str):
        """Retrieve value by key. Returns None if not found."""
        ...

    @abstractmethod
    def set(self, key: str, value) -> None:
        """Store value under key."""
        ...

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key. Returns True if it existed."""
        ...

    # Concrete method (not abstract) — works for ALL subclasses
    def get_or_default(self, key: str, default=None):
        """Provided for free: any DataStore gets this method."""
        value = self.get(key)
        return value if value is not None else default

    def exists(self, key: str) -> bool:
        return self.get(key) is not None


class InMemoryStore(DataStore):
    """In-memory implementation — for testing and development."""

    def __init__(self):
        self._store = {}

    def get(self, key: str):
        return self._store.get(key)

    def set(self, key: str, value) -> None:
        self._store[key] = value

    def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False


class FileStore(DataStore):
    """File-based implementation — simulated here."""

    def __init__(self, path: str):
        self.path = path
        self._cache = {}   # in-memory cache for simulation

    def get(self, key: str):
        return self._cache.get(key)   # simulated file read

    def set(self, key: str, value) -> None:
        self._cache[key] = value   # simulated file write

    def delete(self, key: str) -> bool:
        return bool(self._cache.pop(key, None))


def cache_user(store: DataStore, user_id: int, user_data: dict):
    """
    Works with ANY DataStore implementation.
    Polymorphism via ABC — same code, multiple backends.
    """
    key = f"user:{user_id}"
    store.set(key, user_data)
    return store.get(key)

# Test with both implementations — same function, different backends
mem_store  = InMemoryStore()
file_store = FileStore("/tmp/users")

for store in [mem_store, file_store]:
    result = cache_user(store, 42, {"name": "Alice", "email": "alice@x.com"})
    print(f"{type(store).__name__}: {result}")

# Abstract class cannot be instantiated
try:
    store = DataStore()   # TypeError!
except TypeError as e:
    print(f"\nABC prevents direct instantiation: {e}")

# Subclass without implementing abstract method also fails
try:
    class IncompleteStore(DataStore):
        def get(self, key): return None
        # Missing set() and delete()

    IncompleteStore()   # TypeError
except TypeError as e:
    print(f"Incomplete subclass error: {e}")


# =============================================================================
# SECTION 3: Multiple inheritance and Method Resolution Order (MRO)
# =============================================================================

# CONCEPT: Python supports multiple inheritance. The MRO (C3 linearization)
# determines which class's method gets called when multiple parent classes
# define the same method. Understanding MRO prevents subtle bugs.
# Check MRO with: ClassName.__mro__

print("\n=== Section 3: MRO and Multiple Inheritance ===")

class Flyable:
    def move(self):
        return "flying"

    def describe(self):
        return f"I can fly (speed: 100)"

class Swimmable:
    def move(self):
        return "swimming"

    def describe(self):
        return f"I can swim (depth: 50m)"

class Duck(Flyable, Swimmable):
    """Duck inherits from both. MRO: Duck → Flyable → Swimmable."""

    def describe(self):
        # super() follows MRO — calls Flyable.describe first
        fly_desc  = Flyable.describe(self)
        swim_desc = Swimmable.describe(self)
        return f"Duck: {fly_desc} AND {swim_desc}"

duck = Duck()
print(f"duck.move(): '{duck.move()}'")     # Flyable.move (first in MRO)
print(f"duck.describe(): {duck.describe()}")

# Inspect MRO
print(f"\nDuck MRO: {[c.__name__ for c in Duck.__mro__]}")
# Duck → Flyable → Swimmable → object

# super() in multiple inheritance chains through MRO
class A:
    def greet(self):
        print(f"  A.greet (calling super)")
        super().greet() if hasattr(super(), 'greet') else None

class B(A):
    def greet(self):
        print(f"  B.greet (calling super)")
        super().greet()

class C(A):
    def greet(self):
        print(f"  C.greet (calling super)")
        super().greet()

class D(B, C):
    def greet(self):
        print(f"  D.greet (calling super)")
        super().greet()

print("\nD MRO:", [c.__name__ for c in D.__mro__])
print("D().greet():")
D().greet()   # D → B → C → A → object (cooperative multiple inheritance!)


# =============================================================================
# SECTION 4: Mixins — reusable behavior without full inheritance
# =============================================================================

# CONCEPT: A mixin is a class that provides methods to be mixed into other
# classes via multiple inheritance, without being a standalone base class.
# Mixins are small, focused, and combined like Lego blocks.
# WHY: Django uses mixins extensively (LoginRequiredMixin, PermissionMixin).

print("\n=== Section 4: Mixins ===")

class JSONMixin:
    """Add JSON serialization to any class that has a to_dict() method."""

    def to_json(self) -> str:
        import json
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str):
        import json
        data = json.loads(json_str)
        return cls(**data)


class ValidationMixin:
    """Add validation to any class that defines _required_fields."""
    _required_fields: list = []

    def validate(self) -> bool:
        for field in self._required_fields:
            value = getattr(self, field, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValueError(f"Field '{field}' is required and cannot be empty")
        return True


class TimestampMixin:
    """Add created_at / updated_at tracking."""
    import datetime as _dt

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    def touch(self):
        import datetime
        self.updated_at = datetime.datetime.utcnow()
        if not hasattr(self, 'created_at'):
            self.created_at = self.updated_at


# Combining mixins into a class
class User(JSONMixin, ValidationMixin):
    _required_fields = ['name', 'email']

    def __init__(self, name: str, email: str, role: str = "user"):
        self.name = name
        self.email = email
        self.role = role

    def to_dict(self) -> dict:
        return {"name": self.name, "email": self.email, "role": self.role}

user = User("Alice", "alice@example.com", "admin")
user.validate()   # ValidationMixin
print(f"JSON from mixin:\n{user.to_json()}")

# Round-trip: JSON → instance
user2 = User.from_json('{"name": "Bob", "email": "bob@example.com", "role": "user"}')
print(f"\nFrom JSON: {user2.to_dict()}")

# Validation failure
try:
    bad_user = User("", "alice@x.com")
    bad_user.validate()
except ValueError as e:
    print(f"\nValidation error: {e}")


print("\n=== Advanced OOP practice complete ===")
print("Patterns used in major Python frameworks:")
print("  1. Dunder methods → NumPy arrays, Pandas Series, pathlib.Path")
print("  2. @total_ordering → any object that needs sorting/comparison")
print("  3. ABC + @abstractmethod → Django views, SQLAlchemy base classes")
print("  4. MRO → Django's class-based views, cooperative super() calls")
print("  5. Mixins → Django REST Framework, Flask extensions, test helpers")
