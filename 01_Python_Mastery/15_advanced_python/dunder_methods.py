# Dunder Methods — Theory + Practice

# =============================================================================
# THEORY: What are dunder methods?
# =============================================================================
#
# Dunder methods (double underscore = "dunder") are Python's protocol system.
# They let your objects integrate seamlessly with Python syntax and built-ins.
#
# Instead of inheriting from a "Number" base class, you implement __add__.
# Instead of inheriting from "Container", you implement __len__ + __getitem__.
# Python calls these methods automatically when you use operators and syntax.
#
# Key insight: Python calls dunders on the TYPE, not the instance.
#   len(obj)  → type(obj).__len__(obj)   (not obj.__len__())
#
# This is intentional — it prevents monkey-patching the protocol.
# =============================================================================

from functools import total_ordering
import math


# =============================================================================
# SECTION 1: Lifecycle — __new__, __init__, __del__
# =============================================================================

class PluginRegistry:
    """
    Uses __init_subclass__ (a dunder on the metaclass level) to auto-register
    plugins when they're defined.
    """
    _registry: dict[str, type] = {}

    def __init_subclass__(cls, plugin_name: str = "", **kwargs):
        super().__init_subclass__(**kwargs)
        if plugin_name:
            PluginRegistry._registry[plugin_name] = cls

class JSONPlugin(PluginRegistry, plugin_name="json"):
    def serialize(self, data): import json; return json.dumps(data)

class CSVPlugin(PluginRegistry, plugin_name="csv"):
    def serialize(self, data): return ",".join(map(str, data))

# Auto-registered:
print(PluginRegistry._registry)
# {'json': <class 'JSONPlugin'>, 'csv': <class 'CSVPlugin'>}


class TrackedInstance:
    """Tracks all live instances using __new__ and __del__."""
    _instances: list = []

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        cls._instances.append(instance)
        print(f"Created: now {len(cls._instances)} instances")
        return instance

    def __del__(self):
        type(self)._instances.remove(self)
        print(f"Deleted: now {len(type(self)._instances)} instances")


# =============================================================================
# SECTION 2: Representation — __repr__, __str__, __format__
# =============================================================================

class Temperature:
    """Shows all three representation methods."""

    def __init__(self, celsius: float):
        self.celsius = celsius

    def __repr__(self) -> str:
        # For developers: unambiguous, ideally reconstructable
        return f"Temperature({self.celsius!r})"

    def __str__(self) -> str:
        # For users: readable
        return f"{self.celsius}°C"

    def __format__(self, spec: str) -> str:
        # Custom format specs: f"{t:F}" → Fahrenheit, f"{t:K}" → Kelvin
        if spec == "F":
            return f"{self.celsius * 9/5 + 32:.1f}°F"
        elif spec == "K":
            return f"{self.celsius + 273.15:.2f}K"
        elif spec == "":
            return str(self)
        else:
            return format(self.celsius, spec)   # delegate numeric specs

t = Temperature(100)
print(repr(t))       # Temperature(100)
print(str(t))        # 100°C
print(f"{t:F}")      # 212.0°F
print(f"{t:K}")      # 373.15K
print(f"{t:.3f}")    # 100.000


# =============================================================================
# SECTION 3: Comparison — __eq__, __hash__, __lt__, total_ordering
# =============================================================================

@total_ordering
class Card:
    """Playing card with full comparison support."""

    RANKS = "23456789TJQKA"
    SUITS = "cdhs"  # clubs diamonds hearts spades

    def __init__(self, rank: str, suit: str):
        if rank not in self.RANKS:
            raise ValueError(f"Invalid rank: {rank!r}")
        if suit not in self.SUITS:
            raise ValueError(f"Invalid suit: {suit!r}")
        self.rank = rank
        self.suit = suit

    def _rank_value(self) -> int:
        return self.RANKS.index(self.rank)

    def __eq__(self, other) -> bool:
        if isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        return NotImplemented   # NOT False — allows reflected check

    def __lt__(self, other) -> bool:
        if isinstance(other, Card):
            # Compare by rank, then suit (as tiebreaker)
            return (self._rank_value(), self.SUITS.index(self.suit)) < \
                   (other._rank_value(), other.SUITS.index(other.suit))
        return NotImplemented

    def __hash__(self) -> int:
        # Must be consistent with __eq__: equal cards → same hash
        return hash((self.rank, self.suit))

    def __repr__(self) -> str:
        return f"Card({self.rank!r}, {self.suit!r})"

    def __str__(self) -> str:
        suit_symbols = {"c": "♣", "d": "♦", "h": "♥", "s": "♠"}
        return f"{self.rank}{suit_symbols[self.suit]}"

# Sorting, sets, dicts all work:
hand = [Card("A","s"), Card("K","h"), Card("2","c"), Card("T","d")]
print(sorted(hand))         # [Card('2','c'), Card('T','d'), ...]
print(max(hand))            # Card('A','s')
seen = {Card("A","s"), Card("A","s")}
print(len(seen))            # 1 (hash + eq work correctly)


# =============================================================================
# SECTION 4: Arithmetic — __add__, __radd__, __iadd__
# =============================================================================

class Vector:
    """2D vector with full arithmetic support."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    # --- Arithmetic ---
    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        if isinstance(other, (int, float)):   # scalar addition
            return Vector(self.x + other, self.y + other)
        return NotImplemented

    def __radd__(self, other):
        # Called when: other + self (and other.__add__(self) → NotImplemented)
        return self.__add__(other)

    def __iadd__(self, other):
        # In-place: modifies self, returns self (more efficient)
        if isinstance(other, Vector):
            self.x += other.x
            self.y += other.y
            return self
        if isinstance(other, (int, float)):
            self.x += other
            self.y += other
            return self
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        return NotImplemented

    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector(self.x * scalar, self.y * scalar)
        return NotImplemented

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector(self.x / scalar, self.y / scalar)
        return NotImplemented

    # --- Unary ---
    def __neg__(self):   return Vector(-self.x, -self.y)
    def __pos__(self):   return Vector(self.x, self.y)   # copy
    def __abs__(self):   return math.sqrt(self.x**2 + self.y**2)  # magnitude

    # --- Comparison ---
    def __eq__(self, other):
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y
        return NotImplemented

    def __repr__(self): return f"Vector({self.x}, {self.y})"

v1 = Vector(1, 2)
v2 = Vector(3, 4)
print(v1 + v2)        # Vector(4, 6)
print(v1 + 10)        # Vector(11, 12)
print(10 + v1)        # Vector(11, 12)  — uses __radd__
print(3 * v1)         # Vector(3, 6)    — uses __rmul__
print(-v1)            # Vector(-1, -2)
print(abs(v1))        # 2.23...
v1 += v2
print(v1)             # Vector(4, 6)    — in-place


# =============================================================================
# SECTION 5: Container protocol
# =============================================================================

class SortedList:
    """
    A list that stays sorted. Demonstrates full container protocol:
    __len__, __getitem__, __setitem__, __delitem__, __contains__, __iter__.
    """

    def __init__(self, iterable=()):
        self._data = sorted(iterable)

    def add(self, value):
        import bisect
        bisect.insort(self._data, value)

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, index):
        return self._data[index]   # supports slices too

    def __delitem__(self, index):
        del self._data[index]

    def __contains__(self, value) -> bool:
        import bisect
        i = bisect.bisect_left(self._data, value)
        return i < len(self._data) and self._data[i] == value

    def __iter__(self):
        return iter(self._data)

    def __reversed__(self):
        return reversed(self._data)

    def __repr__(self):
        return f"SortedList({self._data!r})"

sl = SortedList([5, 1, 3, 8, 2])
print(sl)              # SortedList([1, 2, 3, 5, 8])
sl.add(4)
print(sl)              # SortedList([1, 2, 3, 4, 5, 8])
print(3 in sl)         # True
print(len(sl))         # 6
print(sl[2:4])         # [3, 4]
print(list(reversed(sl)))  # [8, 5, 4, 3, 2, 1]


# =============================================================================
# SECTION 6: Callable objects — __call__
# =============================================================================

class MovingAverage:
    """
    Callable object that computes a moving average.
    Maintains state between calls — something a lambda can't do.
    """

    def __init__(self, window: int):
        self.window = window
        self._history: list[float] = []

    def __call__(self, value: float) -> float:
        self._history.append(value)
        if len(self._history) > self.window:
            self._history.pop(0)
        return sum(self._history) / len(self._history)

    def reset(self):
        self._history.clear()

    def __repr__(self):
        return f"MovingAverage(window={self.window}, history={self._history})"

ma5 = MovingAverage(5)
data = [10, 20, 30, 15, 25, 35]
for d in data:
    print(f"{d:3d} → avg: {ma5(d):.1f}")


# =============================================================================
# SECTION 7: Context manager — __enter__, __exit__
# =============================================================================

import time

class Benchmark:
    """Context manager + re-usable timer."""

    def __init__(self, label: str = ""):
        self.label   = label
        self.elapsed = 0.0

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self._start
        label = f"[{self.label}] " if self.label else ""
        print(f"{label}Elapsed: {self.elapsed*1000:.2f}ms")
        return False   # don't suppress exceptions

with Benchmark("sum") as b:
    total = sum(range(1_000_000))
print(f"Result: {total}, took {b.elapsed:.4f}s")


# =============================================================================
# PRACTICE PROBLEMS
# =============================================================================

# ── Problem 1 ──────────────────────────────────────────────────────────────
# Implement a Fraction class with:
#   - __add__, __sub__, __mul__, __truediv__ (with GCD reduction)
#   - __eq__, __lt__ (with @total_ordering)
#   - __repr__, __str__
#   - __float__, __int__ type conversions
# Tests:
#   Fraction(1,2) + Fraction(1,3) == Fraction(5,6)
#   Fraction(3,4) > Fraction(1,2)
#   float(Fraction(1,4)) == 0.25

# ── Problem 2 ──────────────────────────────────────────────────────────────
# Build a Pipeline class that:
#   - stores a list of callable transforms
#   - supports pipe | operator to add transforms: pipeline | transform
#   - is itself callable: pipeline(data) applies all transforms
#   - supports len() → number of steps
# Tests:
#   p = Pipeline() | str.upper | str.strip
#   p("  hello  ") == "HELLO"
#   len(p) == 2

# ── Problem 3 ──────────────────────────────────────────────────────────────
# Create a LRUCache class that:
#   - is initialized with a capacity
#   - supports obj[key] = val, obj[key] (raises KeyError if missing)
#   - evicts least-recently-used item when capacity exceeded
#   - supports len(), 'key in cache', del cache[key]
# Test:
#   c = LRUCache(3)
#   c["a"] = 1; c["b"] = 2; c["c"] = 3
#   c["a"]        # access "a" (now most recent)
#   c["d"] = 4    # evicts "b" (least recently used)
#   "b" not in c  # True

# ── Problem 4 ──────────────────────────────────────────────────────────────
# Implement a Timestamp class wrapping a float (seconds since epoch) that:
#   - supports +/- with timedelta objects (return new Timestamp)
#   - supports - between two Timestamps (return timedelta)
#   - has __str__ in ISO format, __repr__ reconstructable
#   - is hashable and totally orderable
# from datetime import timedelta
# t1 = Timestamp(1_700_000_000.0)
# t2 = t1 + timedelta(hours=1)
# diff = t2 - t1  # timedelta of 1 hour


# =============================================================================
# SOLUTIONS (hidden in practice — try first!)
# =============================================================================

# Solution 1: Fraction
import math as _math

@total_ordering
class Fraction:
    def __init__(self, num: int, den: int = 1):
        if den == 0:
            raise ZeroDivisionError("denominator cannot be zero")
        g = _math.gcd(abs(num), abs(den))
        sign = -1 if den < 0 else 1
        self.num = sign * num // g
        self.den = sign * den // g

    def __add__(self, other):
        if isinstance(other, Fraction):
            return Fraction(self.num * other.den + other.num * self.den,
                            self.den * other.den)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Fraction):
            return Fraction(self.num * other.den - other.num * self.den,
                            self.den * other.den)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, Fraction):
            return Fraction(self.num * other.num, self.den * other.den)
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, Fraction):
            return Fraction(self.num * other.den, self.den * other.num)
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, Fraction):
            return self.num == other.num and self.den == other.den
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Fraction):
            return self.num * other.den < other.num * self.den
        return NotImplemented

    def __float__(self): return self.num / self.den
    def __int__(self):   return int(self.num / self.den)
    def __repr__(self):  return f"Fraction({self.num}, {self.den})"
    def __str__(self):   return f"{self.num}/{self.den}" if self.den != 1 else str(self.num)
    def __hash__(self):  return hash((self.num, self.den))

assert Fraction(1,2) + Fraction(1,3) == Fraction(5,6)
assert Fraction(3,4) > Fraction(1,2)
assert float(Fraction(1,4)) == 0.25
print("Fraction tests passed!")
