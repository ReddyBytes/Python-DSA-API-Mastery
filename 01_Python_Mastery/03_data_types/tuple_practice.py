"""
03_data_types/tuple_practice.py
==================================
CONCEPT: Python tuples — ordered, immutable sequences.
WHY THIS MATTERS: Tuples are not just "immutable lists." They carry semantic
meaning: a tuple's position matters (index 0 = x, index 1 = y).
Tuples signal "this is a fixed group of related items" — a coordinate,
a database row, a function return value. They're also hashable (can be
used as dict keys) and slightly faster than lists.

Understanding when to use tuples vs lists is a mark of Python fluency.

LEARNING PATH:
  Part 1 (this module): tuple creation, immutability, dict keys, namedtuple
  Part 2 (bottom):      revisit AFTER Module 04 (Functions) — multiple return
                        values and NamedTuple class-based style (Module 05)
"""

from collections import namedtuple
import sys
import timeit

# =============================================================================
# PART 1 — Requires only: Modules 01–03
# =============================================================================

# =============================================================================
# SECTION 1: Tuple basics and the critical trailing comma
# =============================================================================

# CONCEPT: Parentheses do NOT create a tuple — the comma does.
# This is the most common tuple mistake, especially in function returns.

print("=== Section 1: Tuple Creation ===")

# Single-element tuple REQUIRES trailing comma
not_a_tuple = (42)        # Just int 42 in parentheses
is_a_tuple  = (42,)       # The comma creates the tuple
also_tuple  = 42,         # Parentheses optional — comma alone is enough!

print(f"(42):   {type(not_a_tuple).__name__} = {not_a_tuple}")
print(f"(42,):  {type(is_a_tuple).__name__} = {is_a_tuple}")
print(f"42, :   {type(also_tuple).__name__} = {also_tuple}")

# Multi-element tuple
point = (3, 7)
rgb   = (255, 128, 0)
empty = ()

# Pack and unpack — tuples make this elegant
x, y = point           # unpacking — assigns 3→x, 7→y
r, g, b = rgb          # position-based unpacking
print(f"\nPoint: x={x}, y={y}")
print(f"Color: r={r}, g={g}, b={b}")

# Extended unpacking (Python 3)
first, *rest = (1, 2, 3, 4, 5)
*most, last  = (1, 2, 3, 4, 5)
head, *middle, tail = (1, 2, 3, 4, 5)
print(f"first={first}, rest={rest}")
print(f"most={most}, last={last}")
print(f"head={head}, middle={middle}, tail={tail}")


# =============================================================================
# SECTION 2: Immutability — what it means and what it doesn't
# =============================================================================

# CONCEPT: Tuples are immutable — you cannot change which objects the tuple
# holds. BUT if those objects are mutable (like lists), you can still mutate
# them in-place. The tuple's "pointer array" is frozen, not the objects.

print("\n=== Section 2: Immutability ===")

# Cannot reassign a position
coords = (10, 20)
try:
    coords[0] = 99   # TypeError
except TypeError as e:
    print(f"Can't reassign: {e}")

# But if the tuple contains mutable objects, those CAN be mutated
mixed = ([1, 2], [3, 4])   # tuple of two lists
mixed[0].append(99)         # mutates the LIST (not reassigning tuple position)
print(f"Tuple with mutated inner list: {mixed}")
# WHY: The tuple still holds the same two list objects.
# We didn't change WHICH lists it holds — we changed what's INSIDE one list.

# This is why tuples should ideally contain only immutable elements
# to get full immutability guarantees.


# =============================================================================
# SECTION 3: Tuples as dict keys — using hashability
# =============================================================================

# CONCEPT: Lists are unhashable (can't be dict keys or set members).
# Tuples are hashable (when they contain only hashable elements).
# This lets you use composite keys — like (x, y) for a 2D grid.

print("\n=== Section 3: Tuples as Dict Keys ===")

# 2D grid / coordinate system
grid_data = {}
grid_data[(0, 0)] = "origin"
grid_data[(1, 0)] = "right"
grid_data[(0, 1)] = "up"
grid_data[(3, 4)] = "treasure"

print(f"Origin: {grid_data[(0, 0)]}")
print(f"Treasure at (3,4): {grid_data[(3, 4)]}")

# Multi-part composite key — (table, year, quarter) as a natural primary key
db_records = {}
db_records[("users", 2024, "Q1")] = {"count": 1523, "active": 891}
db_records[("users", 2024, "Q2")] = {"count": 1748, "active": 1024}
print(f"\nQ1 2024 users: {db_records[('users', 2024, 'Q1')]}")

# Game board / memoization: (row, col) → cell value
board = {}
for r in range(3):
    for c in range(3):
        board[(r, c)] = r * 3 + c + 1   # 1..9

print(f"Board center (1,1): {board[(1,1)]}")
print(f"Board corner (2,2): {board[(2,2)]}")

# Try using a list as key — fails!
try:
    bad_dict = {[1, 2]: "value"}
except TypeError as e:
    print(f"List can't be dict key: {e}")


# =============================================================================
# SECTION 4: Tuple unpacking in loops — cleaner iteration
# =============================================================================

# CONCEPT: Tuple unpacking works directly in for loops.
# Instead of accessing index 0 and index 1 manually, unpack inline.
# This makes loop bodies self-documenting.

print("\n=== Section 4: Tuple Unpacking in Loops ===")

# Direct unpacking from a list of tuples
coordinates = [(1, 2), (3, 4), (5, 6), (7, 8)]

# Without unpacking (less readable):
for pair in coordinates:
    distance = (pair[0] ** 2 + pair[1] ** 2) ** 0.5
    # print(f"  Distance from origin to ({pair[0]}, {pair[1]}): {distance:.2f}")

# With unpacking (clean and readable):
for x, y in coordinates:
    distance = (x ** 2 + y ** 2) ** 0.5
    print(f"  Distance from origin to ({x}, {y}): {distance:.2f}")

# Enumerate returns (index, value) tuples — unpack directly
fruits = ["apple", "banana", "cherry"]
for i, fruit in enumerate(fruits, start=1):
    print(f"  {i}. {fruit}")

# .items() returns (key, value) tuples — unpack directly
scores = {"Alice": 95, "Bob": 87, "Carol": 92}
for name, score in scores.items():
    grade = "A" if score >= 90 else "B"
    print(f"  {name}: {score} ({grade})")

# Swap using tuple assignment
a, b = 10, 20
a, b = b, a   # right side evaluated fully before assignment
print(f"\nAfter swap: a={a}, b={b}")


# =============================================================================
# SECTION 5: namedtuple — tuples with named fields
# =============================================================================

# CONCEPT: namedtuple adds named field access to tuples while keeping all
# tuple properties (immutable, iterable, hashable, memory-efficient).
# It's the sweet spot between a plain tuple and a full class.
# Use it to make code self-documenting: point.x is clearer than point[0].

print("\n=== Section 5: namedtuple ===")

# Basic namedtuple
Point = namedtuple("Point", ["x", "y"])
p = Point(3, 7)

# Access by name (clear intent) or by index (backward-compatible)
print(f"By name:  p.x={p.x}, p.y={p.y}")
print(f"By index: p[0]={p[0]}, p[1]={p[1]}")
print(f"Is tuple: {isinstance(p, tuple)}")
print(f"Sum: {sum(p)}")

# _replace() — create modified copy (tuples are immutable)
p2 = p._replace(x=10)   # creates new Point with x=10, y unchanged
print(f"Original: {p}, Replaced x: {p2}")

# _asdict() — convert to dict (useful for JSON serialization)
print(f"As dict: {p._asdict()}")

# Real-world: representing structured data rows
Employee = namedtuple("Employee", ["id", "name", "department", "salary"])
employees = [
    Employee(1, "Alice", "Engineering", 95000),
    Employee(2, "Bob",   "Marketing",   75000),
    Employee(3, "Carol", "Engineering", 102000),
]

# Named access makes code readable — compare emp[3] vs emp.salary
for emp in employees:
    print(f"  {emp.name} ({emp.department}): ${emp.salary:,}")

# Sort by salary — no lambda: use a temp list of (salary, name) tuples
salary_name = [(emp.salary, emp.name) for emp in employees]
salary_name.sort(reverse=True)
print(f"Top earner: {salary_name[0][1]} (${salary_name[0][0]:,})")


# =============================================================================
# SECTION 6: Performance — tuples vs lists
# =============================================================================

# CONCEPT: Tuples are slightly faster to create and access than lists.
# They also use less memory. The difference matters at scale.

print("\n=== Section 6: Performance Comparison ===")

# Memory: tuples are more compact
list_100  = list(range(100))
tuple_100 = tuple(range(100))
print(f"List  of 100 ints: {sys.getsizeof(list_100)} bytes")
print(f"Tuple of 100 ints: {sys.getsizeof(tuple_100)} bytes")

# Creation speed
list_time  = timeit.timeit("list([1,2,3,4,5])", number=1_000_000)
tuple_time = timeit.timeit("tuple([1,2,3,4,5])", number=1_000_000)
print(f"List  creation (1M): {list_time:.3f}s")
print(f"Tuple creation (1M): {tuple_time:.3f}s")

# Constant tuple literal is even faster (CPython builds it at compile time)
tuple_literal_time = timeit.timeit("(1,2,3,4,5)", number=1_000_000)
list_literal_time  = timeit.timeit("[1,2,3,4,5]", number=1_000_000)
print(f"List  literal (1M):  {list_literal_time:.3f}s")
print(f"Tuple literal (1M):  {tuple_literal_time:.3f}s")
# WHY: Python compiles constant tuple literals as a single LOAD_CONST
# instruction. Lists always require building at runtime.


print("\n=== Part 1 complete ===")
print("When to use tuple vs list:")
print("  tuple: fixed structure (x,y coordinate), dict key, structured record")
print("  list:  ordered collection that grows/shrinks, needs mutation")
print("Key rules:")
print("  1. Trailing comma creates a tuple: (42,) not (42)")
print("  2. Tuples are hashable → usable as dict keys and in sets")
print("  3. namedtuple: add named access to any structured data")
print("  4. Unpack tuples directly in for loops: for x, y in coords")
print()
print(">>> Come back after Module 04 (Functions) for Part 2 below <<<")


# =============================================================================
# PART 2 — Requires: Module 04 (Functions) + Module 05 (OOP)
# =============================================================================

print("\n" + "="*60)
print("PART 2: Requires Module 04 (Functions) + Module 05 (OOP)")
print("="*60)

# =============================================================================
# SECTION 7: Multiple return values — the tuple function contract
# =============================================================================

# CONCEPT: When a Python function "returns multiple values," it actually
# returns a SINGLE tuple. The caller uses tuple unpacking to receive them.

print("\n=== Section 7: Multiple Return Values ===")

def divide_and_remainder(a, b):
    """Returns (quotient, remainder) as a tuple."""
    return a // b, a % b   # the comma makes it a tuple

quotient, remainder = divide_and_remainder(17, 5)
print(f"17 ÷ 5 = {quotient} remainder {remainder}")

# (success, data) pattern — common Python API convention
def fetch_user(user_id):
    if user_id == 1:
        return True, {"id": 1, "name": "Alice"}
    return False, f"User {user_id} not found"

success, data = fetch_user(1)
print(f"Fetch 1: success={success}, data={data}")

success, msg = fetch_user(99)
print(f"Fetch 99: success={success}, msg={msg}")

# Min-max in one pass — returns a tuple
def min_max(numbers):
    if not numbers:
        return None, None
    min_val = max_val = numbers[0]
    for n in numbers[1:]:
        if n < min_val: min_val = n
        if n > max_val: max_val = n
    return min_val, max_val

lo, hi = min_max([3, 1, 4, 1, 5, 9, 2, 6])
print(f"Min: {lo}, Max: {hi}")


# =============================================================================
# SECTION 8: typing.NamedTuple — modern class-based style (needs Module 05)
# =============================================================================

from typing import NamedTuple

print("\n=== Section 8: typing.NamedTuple (Modern Style) ===")

class HTTPResponse(NamedTuple):
    """Typed namedtuple — the modern way to define structured return values."""
    status_code: int
    body:        str
    headers:     dict = {}   # default value supported!

def mock_api_call(endpoint: str) -> HTTPResponse:
    if endpoint == "/users":
        return HTTPResponse(200, '{"users": []}', {"Content-Type": "application/json"})
    return HTTPResponse(404, "Not Found")

response = mock_api_call("/users")
print(f"Status: {response.status_code}")
print(f"Body:   {response.body}")

not_found = mock_api_call("/missing")
print(f"Missing: {not_found.status_code} {not_found.body}")


print("\n=== All sections complete ===")
