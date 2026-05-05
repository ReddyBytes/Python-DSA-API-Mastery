"""
18_performance_optimization/optimization_patterns.py
======================================================
CONCEPT: Common Python optimization patterns — the techniques that give the
biggest gains in real code: local variable lookup, loop hoisting, slots,
algorithm complexity improvements, and memory-efficient data structures.
WHY THIS MATTERS: Writing fast Python isn't about tricks — it's about
understanding HOW Python executes code and choosing the right data structure
for each job. These patterns come up in every performance-sensitive codebase.

Prerequisite: Modules 01–12
"""

import sys
import time
import timeit
import math
from functools import lru_cache
from collections import defaultdict, Counter

# =============================================================================
# SECTION 1: Name lookup optimization — local > global > built-in
# =============================================================================

# CONCEPT: Python looks up names in order: L (local) → E (enclosing) → G (global)
# → B (built-ins). Local lookup is fastest (array index); global is a dict lookup.
# For hot loops, pulling globals/builtins into local variables speeds things up.

print("=== Section 1: Name Lookup Optimization ===")

import math as _math   # avoid module attribute lookup in tight loop

def compute_distances_slow(points: list) -> list:
    """Each call to math.sqrt and math.pi does a global dict lookup."""
    return [
        math.sqrt(x * x + y * y) * math.pi
        for x, y in points
    ]


def compute_distances_fast(points: list) -> list:
    """
    Pull globals into locals BEFORE the loop.
    sqrt and pi are now local variable lookups (LOAD_FAST — array index).
    """
    sqrt = math.sqrt   # local binding: one global lookup at setup, not per iteration
    pi   = math.pi     # same for constant
    return [
        sqrt(x * x + y * y) * pi
        for x, y in points
    ]


import random
random.seed(42)
points = [(random.random() * 100, random.random() * 100) for _ in range(50_000)]

t_slow = min(timeit.repeat(lambda: compute_distances_slow(points), repeat=3, number=5))
t_fast = min(timeit.repeat(lambda: compute_distances_fast(points), repeat=3, number=5))

print(f"  Without local binding: {t_slow/5*1000:.2f} ms")
print(f"  With local binding:    {t_fast/5*1000:.2f} ms  ({t_slow/t_fast:.2f}x faster)")


# =============================================================================
# SECTION 2: Loop optimization — avoid work inside the loop
# =============================================================================

# CONCEPT: Every expression inside a loop that doesn't change with the loop
# variable should be hoisted OUT of the loop. Python re-evaluates len(data)
# and calls to obj.method on every iteration if left inside.

print("\n=== Section 2: Loop Optimization ===")

def process_with_redundancy(items: list) -> list:
    """Bad: re-computes len(items) and calls append inside loop."""
    result = []
    for i in range(len(items)):    # len(items) evaluated every iteration!
        if items[i] > 0:
            result.append(items[i] * 2)
    return result


def process_optimized(items: list) -> list:
    """Good: hoist constant out, use direct iteration, list comprehension."""
    return [x * 2 for x in items if x > 0]   # one pass, no append overhead


data = [random.randint(-100, 100) for _ in range(100_000)]

t_slow = min(timeit.repeat(lambda: process_with_redundancy(data), repeat=3, number=20))
t_fast = min(timeit.repeat(lambda: process_optimized(data), repeat=3, number=20))
print(f"  Redundant loop:      {t_slow/20*1000:.2f} ms")
print(f"  Comprehension:       {t_fast/20*1000:.2f} ms  ({t_slow/t_fast:.2f}x faster)")


# =============================================================================
# SECTION 3: __slots__ — avoid per-instance __dict__
# =============================================================================

# CONCEPT: Normal Python instances store attributes in a __dict__ (a hash map).
# __slots__ replaces __dict__ with fixed-size C-level slots (like a C struct).
# Result: ~40-60% less memory per instance and faster attribute access.
# Use when: creating thousands+ of small, fixed-structure objects.

print("\n=== Section 3: __slots__ Memory Optimization ===")

class PointNoSlots:
    """Normal class — each instance has __dict__ overhead."""
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z


class PointSlots:
    """With __slots__ — no __dict__, fixed memory layout."""
    __slots__ = ("x", "y", "z")

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z


N = 100_000

# Memory comparison
import tracemalloc, gc

gc.collect()
tracemalloc.start()
points_no_slots = [PointNoSlots(i * 0.1, i * 0.2, i * 0.3) for i in range(N)]
snap1 = tracemalloc.take_snapshot()

gc.collect()
points_slots = [PointSlots(i * 0.1, i * 0.2, i * 0.3) for i in range(N)]
snap2 = tracemalloc.take_snapshot()
tracemalloc.stop()

size1 = sum(s.size for s in snap1.statistics("filename"))
size2 = sum(s.size for s in snap2.statistics("filename"))
print(f"  {N:,} instances WITHOUT __slots__: ~{size1/1024/1024:.1f} MB")
print(f"  {N:,} instances WITH    __slots__: ~{size2/1024/1024:.1f} MB")
print(f"  Memory ratio: {size1/max(size2, 1):.1f}x more without slots")

# Attribute access speed
t_no = min(timeit.repeat(
    "p.x + p.y + p.z",
    setup="from __main__ import PointNoSlots; p = PointNoSlots(1.0, 2.0, 3.0)",
    repeat=5, number=1_000_000
))
t_sl = min(timeit.repeat(
    "p.x + p.y + p.z",
    setup="from __main__ import PointSlots; p = PointSlots(1.0, 2.0, 3.0)",
    repeat=5, number=1_000_000
))
print(f"  Attribute access without slots: {t_no/1e6*1e9:.1f} ns/access")
print(f"  Attribute access with slots:    {t_sl/1e6*1e9:.1f} ns/access")


# =============================================================================
# SECTION 4: Algorithm complexity — the biggest wins
# =============================================================================

# CONCEPT: No amount of micro-optimization compensates for O(n²) vs O(n log n).
# Always fix algorithmic complexity BEFORE micro-optimizing.
# Here: find duplicates — O(n²) naive vs O(n) with set.

print("\n=== Section 4: Algorithm Complexity ===")

def find_duplicates_slow(items: list) -> list:
    """O(n²): for each item, scan the rest. Fine for n < 1000."""
    duplicates = []
    seen = []
    for item in items:
        if item in seen and item not in duplicates:   # 'in' on list = O(n)
            duplicates.append(item)
        seen.append(item)
    return duplicates


def find_duplicates_fast(items: list) -> list:
    """O(n): count occurrences in one pass, return items with count > 1."""
    return [item for item, count in Counter(items).items() if count > 1]


# Verify correctness first
test = [1, 2, 3, 2, 4, 1, 5]
slow_result = sorted(find_duplicates_slow(test))
fast_result = sorted(find_duplicates_fast(test))
assert slow_result == fast_result, f"{slow_result} != {fast_result}"

N = 5_000
data = [random.randint(0, N // 2) for _ in range(N)]

t_slow = min(timeit.repeat(lambda: find_duplicates_slow(data), repeat=3, number=10))
t_fast = min(timeit.repeat(lambda: find_duplicates_fast(data), repeat=3, number=10))
print(f"  find_duplicates (n={N}):")
print(f"    O(n²) naive:   {t_slow/10*1000:.2f} ms")
print(f"    O(n) Counter:  {t_fast/10*1000:.2f} ms  ({t_slow/t_fast:.0f}x faster)")


# Two sum: O(n²) vs O(n) with dict
def two_sum_slow(nums: list, target: int) -> tuple | None:
    """O(n²): check every pair."""
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return (i, j)
    return None


def two_sum_fast(nums: list, target: int) -> tuple | None:
    """O(n): track complements in a hash map."""
    seen = {}   # value → index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return (seen[complement], i)
        seen[num] = i
    return None


nums = list(range(10_000))
target = 9_997 + 9_999   # last two indices

r1 = two_sum_slow(nums, target)
r2 = two_sum_fast(nums, target)
print(f"\n  two_sum({target}) results match: {r1 == r2}")

t_slow = min(timeit.repeat(lambda: two_sum_slow(nums, target), repeat=3, number=5))
t_fast = min(timeit.repeat(lambda: two_sum_fast(nums, target), repeat=3, number=100))
print(f"  O(n²) two_sum: {t_slow/5*1000:.2f} ms")
print(f"  O(n)  two_sum: {t_fast/100*1000:.2f} ms  ({t_slow/5 / (t_fast/100):.0f}x faster)")


# =============================================================================
# SECTION 5: String performance — avoid += in loops
# =============================================================================

print("\n=== Section 5: String Building ===")

N = 1000

def build_concat(n: int) -> str:
    """O(n²): each += creates a NEW string object, copying all prior chars."""
    result = ""
    for i in range(n):
        result += str(i) + ","
    return result


def build_join(n: int) -> str:
    """O(n): collect all parts, join ONCE at the end."""
    return ",".join(str(i) for i in range(n))


def build_io(n: int) -> str:
    """O(n): io.StringIO — acts like a mutable string buffer."""
    import io
    buf = io.StringIO()
    for i in range(n):
        buf.write(str(i))
        buf.write(",")
    return buf.getvalue()


t_concat = min(timeit.repeat(lambda: build_concat(N), repeat=3, number=500))
t_join   = min(timeit.repeat(lambda: build_join(N),   repeat=3, number=500))
t_io     = min(timeit.repeat(lambda: build_io(N),     repeat=3, number=500))
print(f"  string += (n={N}): {t_concat/500*1000:.2f} ms")
print(f"  str.join (n={N}):  {t_join/500*1000:.2f} ms  ({t_concat/t_join:.1f}x faster)")
print(f"  StringIO (n={N}):  {t_io/500*1000:.2f} ms")


# =============================================================================
# SECTION 6: Generator vs list — memory for large pipelines
# =============================================================================

print("\n=== Section 6: Generator Pipelines ===")

def process_eager(n: int) -> float:
    """Build all lists in memory, then reduce."""
    data      = [x * x for x in range(n)]           # full list
    filtered  = [x for x in data if x % 3 == 0]     # full list
    mapped    = [math.sqrt(x) for x in filtered]     # full list
    return sum(mapped)


def process_lazy(n: int) -> float:
    """Generator pipeline — O(1) memory."""
    data     = (x * x for x in range(n))
    filtered = (x for x in data if x % 3 == 0)
    mapped   = (math.sqrt(x) for x in filtered)
    return sum(mapped)


N = 500_000

# Correctness
assert abs(process_eager(N) - process_lazy(N)) < 1e-6

gc.collect()
tracemalloc.start()
snap0 = tracemalloc.take_snapshot()
process_eager(N)
snap1 = tracemalloc.take_snapshot()
process_lazy(N)
snap2 = tracemalloc.take_snapshot()
tracemalloc.stop()

mem_eager = sum(s.size for s in snap1.statistics("filename")) - sum(s.size for s in snap0.statistics("filename"))
mem_lazy  = sum(s.size for s in snap2.statistics("filename")) - sum(s.size for s in snap1.statistics("filename"))
print(f"  Eager pipeline (n={N:,}): {max(mem_eager, 0)/1024:.1f} KB allocated")
print(f"  Lazy  pipeline (n={N:,}): {max(mem_lazy, 0)/1024:.1f} KB allocated")


print("\n=== Optimization patterns complete ===")
print("Priority order for optimization:")
print("  1. Fix algorithm complexity  — O(n) vs O(n²) dwarfs everything else")
print("  2. Use right data structure  — set/dict vs list for membership")
print("  3. Use generators            — O(1) memory for pipelines")
print("  4. __slots__                 — when creating millions of small objects")
print("  5. Local variable binding    — LOAD_FAST vs global dict lookup")
print("  6. Loop hoisting             — no repeated work inside tight loops")
print("  7. str.join over +=          — O(n) vs O(n²) string building")
print()
print("ALWAYS: profile first, then optimize the actual hotspot.")
