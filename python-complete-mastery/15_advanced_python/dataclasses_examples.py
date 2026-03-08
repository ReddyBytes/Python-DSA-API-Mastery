# Dataclasses Examples — Theory + Practice

# =============================================================================
# THEORY: @dataclass — Automatic class generation
# =============================================================================
#
# @dataclass is a class decorator (Python 3.7+) that auto-generates:
#   __init__     — from field declarations
#   __repr__     — from field declarations
#   __eq__       — compares field-by-field
#
# Optional (enabled via decorator flags):
#   __lt__/__le__/__gt__/__ge__  — with order=True
#   __hash__                     — with frozen=True (or explicit unsafe_hash=True)
#
# FIELD TYPES:
#   field_name: type = default_value
#   field_name: type = field(default=..., default_factory=...,
#                            repr=..., compare=..., hash=..., init=..., metadata=...)
#
# DECORATOR FLAGS:
#   @dataclass(init=True, repr=True, eq=True, order=False,
#              unsafe_hash=False, frozen=False, slots=False,  # Python 3.10+
#              kw_only=False, match_args=True)
#
# SPECIAL METHODS:
#   __post_init__: called after __init__ for custom validation/computation
#
# WHY DATACLASSES?
#   - Eliminate boilerplate __init__, __repr__, __eq__
#   - Better than NamedTuple for mutable data
#   - Better than plain dicts for structured data
#   - Better than hand-rolled classes for simple data containers
#   - Supports inheritance cleanly
#   - Works with static type checkers
# =============================================================================

from dataclasses import (
    dataclass, field, fields, asdict, astuple, replace, KW_ONLY
)
from typing import ClassVar, Optional
import math
import json


# =============================================================================
# SECTION 1: Basic @dataclass
# =============================================================================

@dataclass
class Point:
    """Simple 2D point."""
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def __post_init__(self):
        # Called after auto-generated __init__
        # Good place for validation:
        if not (isinstance(self.x, (int, float)) and isinstance(self.y, (int, float))):
            raise TypeError("x and y must be numeric")

p1 = Point(1.0, 2.0)
p2 = Point(4.0, 6.0)

print(p1)                    # Point(x=1.0, y=2.0)
print(p1 == Point(1.0, 2.0)) # True — field-by-field comparison
print(p1.distance_to(p2))   # 5.0

# What @dataclass generated:
# __init__(self, x: float, y: float)  ← with __post_init__ call at end
# __repr__(self)  → "Point(x=1.0, y=2.0)"
# __eq__(self, other)  → compares (x, y) tuples


# =============================================================================
# SECTION 2: field() — fine-grained control
# =============================================================================

@dataclass
class Student:
    name: str
    grade: int

    # Default value via default_factory (required for mutable defaults!):
    subjects: list[str] = field(default_factory=list)

    # Field excluded from repr:
    _password_hash: str = field(default="", repr=False)

    # Field excluded from comparison:
    created_at: float = field(default=0.0, compare=False)

    # ClassVar is NOT a dataclass field:
    student_count: ClassVar[int] = 0

    def __post_init__(self):
        type(self).student_count += 1
        if not self.name.strip():
            raise ValueError("Name cannot be empty")
        if not (1 <= self.grade <= 12):
            raise ValueError(f"Grade must be 1-12, got {self.grade}")

s1 = Student("Alice", 10, subjects=["Math", "Physics"])
s2 = Student("Bob",   11)

print(s1)                             # Student(name='Alice', grade=10, subjects=['Math', 'Physics'], created_at=0.0)
print(s1 == s2)                       # False — compares name+grade+subjects
print(Student.student_count)          # 2

# IMPORTANT: Never use mutable default directly!
# @dataclass
# class Bad:
#     items: list = []   # ValueError! Use field(default_factory=list)


# =============================================================================
# SECTION 3: frozen=True — immutable dataclasses
# =============================================================================

@dataclass(frozen=True)
class Color:
    """Immutable RGB color — hashable, can be used as dict key."""
    r: int = 0
    g: int = 0
    b: int = 0
    a: int = 255   # alpha

    def __post_init__(self):
        for name, val in [("r", self.r), ("g", self.g), ("b", self.b), ("a", self.a)]:
            if not (0 <= val <= 255):
                raise ValueError(f"{name} must be 0-255, got {val}")

    def to_hex(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    def blend(self, other: "Color", factor: float = 0.5) -> "Color":
        """Create a new blended color (frozen — can't modify in place)."""
        return Color(
            r=int(self.r * (1-factor) + other.r * factor),
            g=int(self.g * (1-factor) + other.g * factor),
            b=int(self.b * (1-factor) + other.b * factor),
        )

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        h = hex_str.lstrip("#")
        return cls(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

RED   = Color(255, 0, 0)
BLUE  = Color(0, 0, 255)
GREEN = Color(0, 255, 0)

print(RED.to_hex())                    # #ff0000
print(RED.blend(BLUE).to_hex())        # blended purple
print(hash(RED))                       # works! frozen → hashable

# Can be used in sets and as dict keys:
palette = {RED, GREEN, BLUE}
color_names = {RED: "red", GREEN: "green", BLUE: "blue"}
print(color_names[Color(255, 0, 0)])   # "red"

try:
    RED.r = 100    # raises FrozenInstanceError
except Exception as e:
    print(f"Caught: {type(e).__name__}: {e}")


# =============================================================================
# SECTION 4: order=True — sortable dataclasses
# =============================================================================

@dataclass(order=True)
class Priority:
    """Task with priority ordering. order=True generates all 6 comparison methods."""

    # Fields are compared in ORDER they're declared:
    level:   int     # 1 = highest priority
    created: float   # earlier timestamp = higher priority within same level

    # Fields with compare=False are excluded from ordering:
    description: str = field(compare=False)

    def __str__(self):
        return f"[P{self.level}] {self.description}"

import time
tasks = [
    Priority(level=2, created=1000.0, description="Send report"),
    Priority(level=1, created=2000.0, description="Fix critical bug"),
    Priority(level=2, created=500.0,  description="Update docs"),
    Priority(level=1, created=1500.0, description="Deploy hotfix"),
]

print("\nSorted tasks:")
for t in sorted(tasks):
    print(f"  {t}")


# =============================================================================
# SECTION 5: Inheritance with dataclasses
# =============================================================================

@dataclass
class Shape:
    """Abstract shape — base for all shapes."""
    color: str = "black"
    visible: bool = True

    def area(self) -> float:
        raise NotImplementedError

    def perimeter(self) -> float:
        raise NotImplementedError

@dataclass
class Circle(Shape):
    radius: float = 0.0

    def __post_init__(self):
        if self.radius < 0:
            raise ValueError("Radius cannot be negative")

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * math.pi * self.radius

@dataclass
class Rectangle(Shape):
    width:  float = 0.0
    height: float = 0.0

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

@dataclass
class Square(Rectangle):
    # Override: side = width = height
    # Use __post_init__ to sync them:
    side: float = field(default=0.0, init=True)

    def __post_init__(self):
        # Set both width and height from side:
        # Can't assign directly (might be frozen), use object.__setattr__ if frozen
        self.width  = self.side
        self.height = self.side
        if self.side < 0:
            raise ValueError("Side cannot be negative")

shapes = [Circle(radius=5.0, color="red"),
          Rectangle(width=4.0, height=3.0),
          Square(side=6.0, color="blue")]

for s in shapes:
    print(f"{s}: area={s.area():.2f}, perimeter={s.perimeter():.2f}")


# =============================================================================
# SECTION 6: Utility functions — asdict, astuple, replace, fields
# =============================================================================

@dataclass
class Address:
    street: str
    city:   str
    zip_:   str
    country: str = "US"

@dataclass
class Person:
    name:    str
    age:     int
    address: Address

person = Person(
    name="Alice",
    age=30,
    address=Address(street="123 Main St", city="Springfield", zip_="12345")
)

# asdict — recursively converts to nested dict:
d = asdict(person)
print("\nasdict:")
print(json.dumps(d, indent=2))

# astuple — recursively converts to nested tuple:
t = astuple(person)
print(f"\nastuple: {t}")

# replace — create modified copy (works like frozen copy):
older_alice = replace(person, age=31)
print(f"\nreplace: {older_alice}")
print(f"Original unchanged: {person.age}")  # 30

# fields() — inspect field metadata:
print("\nfields():")
for f_ in fields(Person):
    print(f"  {f_.name}: {f_.type}, default={f_.default!r}")


# =============================================================================
# SECTION 7: __post_init__ patterns
# =============================================================================

@dataclass
class BoundingBox:
    """Axis-aligned bounding box with auto-computed properties."""
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    # These are COMPUTED in __post_init__ — not init params:
    width:  float = field(init=False)
    height: float = field(init=False)
    area:   float = field(init=False)
    center: tuple = field(init=False)

    def __post_init__(self):
        if self.x_min > self.x_max or self.y_min > self.y_max:
            raise ValueError("min must be ≤ max")
        self.width  = self.x_max - self.x_min
        self.height = self.y_max - self.y_min
        self.area   = self.width * self.height
        self.center = ((self.x_min + self.x_max) / 2,
                       (self.y_min + self.y_max) / 2)

    def intersects(self, other: "BoundingBox") -> bool:
        return (self.x_min < other.x_max and self.x_max > other.x_min and
                self.y_min < other.y_max and self.y_max > other.y_min)

box1 = BoundingBox(0, 0, 10, 10)
box2 = BoundingBox(5, 5, 15, 15)
print(f"\nbox1: {box1}")
print(f"width={box1.width}, height={box1.height}, area={box1.area}")
print(f"center={box1.center}")
print(f"Intersects: {box1.intersects(box2)}")


# =============================================================================
# SECTION 8: Slots with dataclasses (Python 3.10+)
# =============================================================================

# Python 3.10+ supports @dataclass(slots=True):
# This generates __slots__ automatically — no need to manually define them.

try:
    @dataclass(slots=True)
    class FastPoint:
        x: float
        y: float

    fp = FastPoint(1.0, 2.0)
    print(f"\n@dataclass(slots=True): {fp}")
    print(f"Has __slots__: {hasattr(FastPoint, '__slots__')}")
    print(f"Slots: {FastPoint.__slots__}")

except TypeError:
    print("\n@dataclass(slots=True) requires Python 3.10+")


# =============================================================================
# PRACTICE PROBLEMS
# =============================================================================

# ── Problem 1 ──────────────────────────────────────────────────────────────
# Create a @dataclass Config with:
#   - host: str = "localhost"
#   - port: int = 8080
#   - debug: bool = False
#   - tags: list[str] = []  (careful with mutable default!)
#   - frozen=True (immutable)
#   - __post_init__: validate port is 1-65535
#   - A method with_port(new_port) that returns a new Config (use replace())

# ── Problem 2 ──────────────────────────────────────────────────────────────
# Build a @dataclass hierarchy for a simple invoice system:
#   LineItem(description, quantity, unit_price)
#     - property: total = quantity * unit_price
#   Invoice(number, customer, items: list[LineItem])
#     - property: subtotal = sum of line totals
#     - property: tax = subtotal * 0.1
#     - property: grand_total = subtotal + tax
#     - method: to_dict() using asdict()
#     - __str__: formatted invoice string

# ── Problem 3 ──────────────────────────────────────────────────────────────
# Create a @dataclass(frozen=True) for a Coordinate (lat, lon) that:
#   - validates lat ∈ [-90, 90] and lon ∈ [-180, 180]
#   - has a distance_to(other) method using Haversine formula
#   - is hashable (frozen=True guarantees this)
#   - can be used as a dict key (for caching distances)
# Haversine formula: https://en.wikipedia.org/wiki/Haversine_formula


# =============================================================================
# SOLUTIONS
# =============================================================================

# Solution: Config
@dataclass(frozen=True)
class Config:
    host:  str       = "localhost"
    port:  int       = 8080
    debug: bool      = False
    tags:  tuple[str,...] = ()   # use tuple for immutability with frozen=True

    def __post_init__(self):
        if not (1 <= self.port <= 65535):
            raise ValueError(f"Port must be 1-65535, got {self.port}")

    def with_port(self, new_port: int) -> "Config":
        return replace(self, port=new_port)

cfg = Config(host="example.com", port=443, tags=("prod", "api"))
print(f"\nConfig: {cfg}")
cfg2 = cfg.with_port(8443)
print(f"With new port: {cfg2}")
try:
    cfg.port = 9999   # FrozenInstanceError
except Exception as e:
    print(f"Immutable: {type(e).__name__}")
