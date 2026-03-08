# Slots Example — Theory + Practice

# =============================================================================
# THEORY: __slots__ — Memory optimization through controlled attribute storage
# =============================================================================
#
# By default, every Python instance stores its attributes in a dict (__dict__).
# Dicts are flexible but carry significant memory overhead:
#   - ~200-300 bytes for the dict object itself
#   - Plus per-entry overhead for each attribute
#
# __slots__ replaces __dict__ with a fixed array of C-level slot descriptors:
#   - Each slot is a member_descriptor (data descriptor) on the class
#   - Values stored in a compact C-level struct instead of a Python dict
#   - No __dict__ (unless you add "__dict__" to __slots__)
#
# MEMORY SAVINGS:
#   Class with 3 attributes:
#     Without __slots__: ~360 bytes (instance + dict + dict entries)
#     With __slots__:    ~72 bytes  (instance + 3 slots)
#     Savings: ~5x smaller
#
# PERFORMANCE BENEFITS:
#   - Attribute access is faster (no hash lookup, direct index)
#   - Less GC pressure (fewer objects)
#
# RESTRICTIONS:
#   - Can't add attributes not listed in __slots__
#   - Can't pickle easily (need __getstate__/__setstate__)
#   - Multiple inheritance: all parents must use __slots__ OR
#     only ONE parent can have a non-empty __dict__
#   - Class dict (__class__.__dict__) is separate — not affected
#
# WHEN TO USE:
#   - Classes with many instances (Points, Records, Events)
#   - Performance-critical inner loops
#   - When the attribute set is truly fixed
#
# WHEN NOT TO USE:
#   - Dynamic attribute assignment needed
#   - Rapid prototyping
#   - Classes with complex multiple inheritance
# =============================================================================

import sys
import tracemalloc


# =============================================================================
# SECTION 1: Basic __slots__ usage and memory comparison
# =============================================================================

class PointDict:
    """Regular class — stores attributes in __dict__."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance_to(self, other: "PointDict") -> float:
        return ((self.x - other.x)**2 + (self.y - other.y)**2) ** 0.5


class PointSlots:
    """Same class with __slots__ — no __dict__, compact storage."""
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance_to(self, other: "PointSlots") -> float:
        return ((self.x - other.x)**2 + (self.y - other.y)**2) ** 0.5


# Demonstrate memory difference:
p1 = PointDict(1.0, 2.0)
p2 = PointSlots(1.0, 2.0)

print("=== Memory comparison ===")
print(f"PointDict  instance size: {sys.getsizeof(p1):5} bytes")
print(f"  + dict size:            {sys.getsizeof(p1.__dict__):5} bytes")
print(f"  TOTAL:                  {sys.getsizeof(p1) + sys.getsizeof(p1.__dict__):5} bytes")
print()
print(f"PointSlots instance size: {sys.getsizeof(p2):5} bytes")
print(f"  no __dict__!")

# Can't add arbitrary attributes to slots class:
p1.z = 3.0    # OK — dict is there
try:
    p2.z = 3.0  # AttributeError
except AttributeError as e:
    print(f"PointSlots: {e}")

# Slot attributes ARE class-level descriptors:
print(f"\ntype(PointSlots.x): {type(PointSlots.x)}")  # member_descriptor


# =============================================================================
# SECTION 2: Bulk memory measurement
# =============================================================================

N = 100_000

def measure_bulk_memory(cls, n: int) -> int:
    tracemalloc.start()
    snapshot_before = tracemalloc.take_snapshot()
    instances = [cls(i * 1.0, i * 2.0) for i in range(n)]
    snapshot_after = tracemalloc.take_snapshot()
    tracemalloc.stop()

    stats = snapshot_after.compare_to(snapshot_before, "lineno")
    total = sum(s.size_diff for s in stats)
    return total, instances  # keep instances alive for accurate measurement

print("\n=== Bulk memory: 100,000 instances ===")
tracemalloc.start()
before = tracemalloc.take_snapshot()
dict_instances = [PointDict(float(i), float(i)) for i in range(N)]
after = tracemalloc.take_snapshot()
tracemalloc.stop()
dict_mem = sum(s.size_diff for s in after.compare_to(before, "lineno"))

tracemalloc.start()
before = tracemalloc.take_snapshot()
slot_instances = [PointSlots(float(i), float(i)) for i in range(N)]
after = tracemalloc.take_snapshot()
tracemalloc.stop()
slot_mem = sum(s.size_diff for s in after.compare_to(before, "lineno"))

print(f"PointDict  × {N:,}:   {dict_mem / 1024 / 1024:.1f} MB")
print(f"PointSlots × {N:,}:   {slot_mem / 1024 / 1024:.1f} MB")
if slot_mem > 0:
    print(f"Ratio: {dict_mem / slot_mem:.1f}x savings")


# =============================================================================
# SECTION 3: __slots__ with inheritance
# =============================================================================

class Animal:
    __slots__ = ("name", "weight")

    def __init__(self, name: str, weight: float):
        self.name   = name
        self.weight = weight

    def __repr__(self):
        return f"{type(self).__name__}({self.name!r}, {self.weight}kg)"

class Dog(Animal):
    # Inherit Animal's slots, ADD breed slot:
    __slots__ = ("breed",)   # only NEW slots here

    def __init__(self, name: str, weight: float, breed: str):
        super().__init__(name, weight)
        self.breed = breed

    def __repr__(self):
        return f"Dog({self.name!r}, {self.weight}kg, {self.breed!r})"

d = Dog("Rex", 30.0, "Husky")
print(d)          # Dog('Rex', 30.0kg, 'Husky')
print(d.name)     # Rex
print(d.weight)   # 30.0

# If a parent has __dict__ (i.e. no __slots__), the child gets a __dict__:
class WithDict:
    def __init__(self): self.x = 1

class ChildWithSlots(WithDict):
    __slots__ = ("y",)   # adds a slot, but parent's __dict__ is still there

c = ChildWithSlots()
c.y = 2
c.z = 3      # OK — because parent has __dict__!
print(f"c.__dict__: {c.__dict__}")   # {'z': 3} — x is in __dict__ too


# =============================================================================
# SECTION 4: __slots__ with __dict__ and __weakref__
# =============================================================================

class Flexible:
    """
    Uses __slots__ for known attributes but keeps __dict__ for dynamic ones.
    Also includes __weakref__ for weak references.
    """
    __slots__ = ("x", "y", "__dict__", "__weakref__")

    def __init__(self, x, y):
        self.x = x
        self.y = y

f = Flexible(1, 2)
f.z = 3        # OK — __dict__ is back
print(f.__dict__)   # {"z": 3}

import weakref
ref = weakref.ref(f)   # OK — __weakref__ is there
print(ref())


# =============================================================================
# SECTION 5: Pickling with __slots__
# =============================================================================

import pickle

class NaiveSlots:
    """Slots class without pickle support — will fail!"""
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y

class PicklableSlots:
    """Slots class WITH correct pickle support."""
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y

    def __getstate__(self):
        return {"x": self.x, "y": self.y}

    def __setstate__(self, state):
        self.x = state["x"]
        self.y = state["y"]

    def __repr__(self):
        return f"PicklableSlots(x={self.x}, y={self.y})"

# Without __getstate__/__setstate__:
try:
    pickle.dumps(NaiveSlots(1, 2))
except Exception as e:
    # May or may not work depending on Python version — Python 3 handles it
    # automatically if ALL parent classes have either __dict__ or __slots__
    print(f"NaiveSlots pickle: {e}")

ps = PicklableSlots(10, 20)
restored = pickle.loads(pickle.dumps(ps))
print(f"Restored: {restored}")


# =============================================================================
# SECTION 6: Real-world use case — Event record
# =============================================================================

class Event:
    """
    High-volume event object. Using __slots__ because millions may be
    created during a single logging session.
    """
    __slots__ = (
        "event_id",
        "timestamp",
        "event_type",
        "source",
        "data",
        "severity",
    )

    SEVERITY_LEVELS = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}

    def __init__(
        self,
        event_id: int,
        timestamp: float,
        event_type: str,
        source: str,
        data: dict,
        severity: str = "INFO",
    ):
        self.event_id   = event_id
        self.timestamp  = timestamp
        self.event_type = event_type
        self.source     = source
        self.data       = data
        self.severity   = severity

    def is_error_or_above(self) -> bool:
        return self.SEVERITY_LEVELS.get(self.severity, 0) >= 3

    def __repr__(self):
        return (
            f"Event(id={self.event_id}, type={self.event_type!r}, "
            f"source={self.source!r}, severity={self.severity!r})"
        )

import time as _time
events = [
    Event(
        event_id   = i,
        timestamp  = _time.time(),
        event_type = "user_action",
        source     = "web_app",
        data       = {"action": f"click_{i}"},
        severity   = "INFO" if i % 10 != 0 else "ERROR",
    )
    for i in range(10_000)
]

errors = [e for e in events if e.is_error_or_above()]
print(f"Created {len(events):,} events")
print(f"Error events: {len(errors)}")
print(f"Memory per event: {sys.getsizeof(events[0])} bytes")


# =============================================================================
# PRACTICE PROBLEMS
# =============================================================================

# ── Problem 1 ──────────────────────────────────────────────────────────────
# Convert the following class to use __slots__ and verify that:
#   a) Memory usage drops significantly
#   b) Dynamic attribute assignment no longer works
#   c) Pickling still works correctly
#
# class Record:
#     def __init__(self, id_, name, value, tags):
#         self.id    = id_
#         self.name  = name
#         self.value = value
#         self.tags  = tags

# ── Problem 2 ──────────────────────────────────────────────────────────────
# Create a 3D vector hierarchy using __slots__:
#   Vector2D: __slots__ = ("x", "y")
#   Vector3D(Vector2D): adds "z"
#   ColorVector3D(Vector3D): adds "r", "g", "b" (RGB color)
# Verify each level adds only its own slots and inherits parents' correctly.

# ── Problem 3 ──────────────────────────────────────────────────────────────
# Build a SlotInspector utility that:
#   - Given any class, returns all slots including inherited ones
#   - Given an instance, returns {slot_name: slot_value} dict
# Tests:
#   slots_of(Dog)          → {"name", "weight", "breed"}
#   slot_values(my_dog)    → {"name": "Rex", "weight": 30.0, "breed": "Husky"}


# =============================================================================
# SOLUTIONS
# =============================================================================

# Solution: SlotInspector
def all_slots(cls: type) -> set:
    """Return all __slots__ including inherited ones."""
    slots = set()
    for klass in cls.__mro__:
        slots.update(getattr(klass, "__slots__", ()))
    return slots - {"__dict__", "__weakref__"}

def slot_values(obj) -> dict:
    """Return {slot: value} for all slots on an instance."""
    return {
        slot: getattr(obj, slot)
        for slot in all_slots(type(obj))
        if hasattr(obj, slot)
    }

d = Dog("Rex", 30.0, "Husky")
print(f"\nAll slots for Dog: {all_slots(Dog)}")
print(f"Slot values: {slot_values(d)}")
