"""
04_functions/functional_programming.py
=========================================
CONCEPT: Functional programming in Python — treating functions as data,
avoiding side effects, and building programs from composable transformations.
WHY THIS MATTERS: Python is multi-paradigm but has strong FP support.
map/filter/reduce, pure functions, and immutability principles lead to code
that is easier to test, parallelize, and reason about. Data science, ML
preprocessing, and ETL pipelines heavily use FP patterns.
"""

import functools
from itertools import chain, islice, takewhile, dropwhile, groupby, product, combinations, permutations

# =============================================================================
# SECTION 1: Pure functions — no side effects, same input → same output
# =============================================================================

# CONCEPT: A pure function:
# 1. Always returns the same result for the same arguments
# 2. Has no side effects (doesn't modify external state, print, write to DB)
# Pure functions are easy to test (no mocking needed), composable, and safe
# to parallelize. Strive for pure functions; isolate impure ones.

print("=== Section 1: Pure vs Impure Functions ===")

# IMPURE — reads external state, modifies external list
discount_rate = 0.1   # external state!
applied_discounts = []  # mutable external state

def apply_discount_impure(price):
    """
    WHY THIS IS PROBLEMATIC:
    - Test result changes if discount_rate changes
    - Side effect: modifies applied_discounts
    - Can't safely parallelize (shared mutable state)
    """
    discounted = price * (1 - discount_rate)   # reads external variable
    applied_discounts.append(discounted)        # modifies external list
    return discounted

# PURE — all inputs explicit, no side effects
def apply_discount_pure(price: float, rate: float) -> float:
    """
    WHY THIS IS BETTER:
    - Given same price and rate, always same result
    - No external dependencies — easy to test in isolation
    - Can run 10,000 of these in parallel without conflicts
    """
    return price * (1 - rate)

prices = [10.0, 25.0, 50.0, 100.0]
print("Impure results:", [apply_discount_impure(p) for p in prices])
print("Pure results:  ", [apply_discount_pure(p, 0.1) for p in prices])
print(f"Side effect: applied_discounts = {applied_discounts}")


# =============================================================================
# SECTION 2: map, filter, reduce — the FP trinity
# =============================================================================

# CONCEPT: These three operations describe what to DO to data, not HOW to
# loop over it. They're lazy (map/filter return iterators) and composable.
# In Python, list comprehensions are often preferred over map/filter,
# but reduce/functools have specific powerful uses.

print("\n=== Section 2: map, filter, reduce ===")

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# map(func, iterable) — apply func to every element
# Returns an ITERATOR — lazy, only computes when consumed
squared = list(map(lambda x: x**2, numbers))
print(f"Squared: {squared}")

# Same as comprehension (preferred in most Python code):
squared_comp = [x**2 for x in numbers]

# filter(predicate, iterable) — keep elements where predicate returns True
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(f"Evens: {evens}")

# Same as comprehension:
evens_comp = [x for x in numbers if x % 2 == 0]

# reduce(func, iterable) — fold left, accumulating a single result
# This is the most powerful of the three — can implement map and filter!
total = functools.reduce(lambda acc, x: acc + x, numbers)
product_result = functools.reduce(lambda acc, x: acc * x, numbers, 1)
print(f"Sum via reduce: {total}")
print(f"Product via reduce: {product_result}")

# reduce for building data structures
words = ["the", "quick", "brown", "fox"]
# Build frequency map using reduce
word_count = functools.reduce(
    lambda acc, word: {**acc, word: acc.get(word, 0) + 1},
    words,
    {}   # initial value
)
print(f"Word counts: {word_count}")

# Chain map + filter + reduce: total revenue from large orders
orders = [
    {"id": 1, "amount": 150.0, "status": "paid"},
    {"id": 2, "amount": 30.0,  "status": "paid"},
    {"id": 3, "amount": 500.0, "status": "paid"},
    {"id": 4, "amount": 200.0, "status": "refunded"},
    {"id": 5, "amount": 75.0,  "status": "paid"},
]

large_paid_revenue = functools.reduce(
    lambda acc, amt: acc + amt,
    map(lambda o: o["amount"],
        filter(lambda o: o["status"] == "paid" and o["amount"] > 100, orders)),
    0
)
print(f"Revenue from large paid orders: ${large_paid_revenue:.2f}")


# =============================================================================
# SECTION 3: List, dict, and set comprehensions — Pythonic FP
# =============================================================================

# CONCEPT: Comprehensions are Python's preferred syntax for map/filter.
# They're more readable than chained map(lambda...) calls.
# Nested comprehensions replace nested loops.
# Generator expressions (parens) are lazy — use for large data.

print("\n=== Section 3: Comprehensions ===")

# Flat transformation + filter
products = [
    {"name": "Widget", "price": 9.99,  "in_stock": True},
    {"name": "Gadget", "price": 49.99, "in_stock": True},
    {"name": "Doohickey", "price": 2.99, "in_stock": False},
    {"name": "Thingamajig", "price": 19.99, "in_stock": True},
]

# Complex comprehension: filter, transform, and extract in one line
available_names = [
    p["name"].upper()
    for p in products
    if p["in_stock"] and p["price"] > 5.0
]
print(f"Available premium products: {available_names}")

# Dict comprehension: invert a mapping
code_to_name = {"US": "United States", "UK": "United Kingdom", "DE": "Germany"}
name_to_code = {v: k for k, v in code_to_name.items()}
print(f"Name to code: {name_to_code}")

# Nested comprehension: flatten a 2D matrix
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [cell for row in matrix for cell in row]  # outer loop first!
print(f"Flattened matrix: {flat}")

# Nested comprehension: matrix multiplication (builds intuition for ML)
# C[i][j] = sum(A[i][k] * B[k][j] for k in range(len(B)))
A = [[1, 2], [3, 4]]
B = [[5, 6], [7, 8]]
n = len(A)
C = [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
print(f"Matrix multiply A×B: {C}")   # [[19,22],[43,50]]

# Generator expression — lazy, O(1) memory for any size input
large_sum = sum(x**2 for x in range(1_000_000))   # computed one item at a time
print(f"Sum of squares 0-999,999: {large_sum:,}")


# =============================================================================
# SECTION 4: functools toolkit — FP utilities
# =============================================================================

# CONCEPT: functools provides essential FP utilities. lru_cache for memoization,
# partial for currying, reduce for folding, wraps for decorator metadata.

print("\n=== Section 4: functools Toolkit ===")

# --- total_ordering: define __eq__ and ONE comparison, get the rest free ---
from functools import total_ordering

@total_ordering
class Version:
    """
    Software version with semantic comparison.
    total_ordering fills in __gt__, __le__, __ge__ from __eq__ and __lt__.
    WHY: Don't implement 6 comparison methods when 2 define them all.
    """
    def __init__(self, major, minor, patch):
        self.v = (major, minor, patch)

    def __eq__(self, other):
        return self.v == other.v

    def __lt__(self, other):
        return self.v < other.v   # tuple comparison lexicographically

    def __repr__(self):
        return f"v{'.'.join(map(str, self.v))}"

versions = [Version(2,0,0), Version(1,9,3), Version(2,0,1), Version(1,0,0)]
print(f"Versions sorted: {sorted(versions)}")
print(f"Latest: {max(versions)}")

# --- cached_property: compute once, cache on the instance ---
from functools import cached_property

class DataProcessor:
    def __init__(self, raw_data):
        self.raw_data = raw_data

    @cached_property
    def processed(self):
        """
        Computed lazily on first access, then cached as an instance attribute.
        WHY: Expensive transformations shouldn't re-run on every access.
        Subsequent accesses are instant dict lookups, not recomputations.
        """
        print("  (computing processed data...)")
        return [x * 2 for x in self.raw_data]   # expensive operation

processor = DataProcessor([1, 2, 3, 4, 5])
print("First access:")
print(f"  {processor.processed}")   # triggers computation
print("Second access:")
print(f"  {processor.processed}")   # returns cached value, no recomputation


# =============================================================================
# SECTION 5: itertools — lazy iterators for efficient data processing
# =============================================================================

# CONCEPT: itertools provides composable lazy iterators.
# They never build intermediate lists — memory use is O(1) regardless
# of input size. Essential for data pipelines, combinatorics, and chunking.

print("\n=== Section 5: itertools ===")

# --- chain: flatten multiple iterables without creating a combined list ---
batch1 = [1, 2, 3]
batch2 = [4, 5, 6]
batch3 = [7, 8, 9]
combined = list(chain(batch1, batch2, batch3))
print(f"chain: {combined}")

# --- islice: take N items from any iterator (like slice but lazy) ---
# Useful for paginating a generator without loading everything
def infinite_counter(start=0):
    n = start
    while True:
        yield n
        n += 1

first_10 = list(islice(infinite_counter(0), 10))
print(f"islice first 10: {first_10}")

# --- takewhile / dropwhile: take/skip based on condition ---
data = [1, 3, 5, 2, 7, 4, 6]   # mixed, not sorted
ascending = list(takewhile(lambda x: x < 6, data))  # stop when x >= 6
after_5   = list(dropwhile(lambda x: x < 5, data))  # drop until x >= 5
print(f"takewhile(<6): {ascending}")
print(f"dropwhile(<5): {after_5}")

# --- groupby: group consecutive elements by a key ---
# NOTE: Data must be SORTED by the key first for correct grouping
students = [
    {"name": "Alice", "grade": "A"},
    {"name": "Bob",   "grade": "B"},
    {"name": "Carol", "grade": "A"},
    {"name": "Diana", "grade": "B"},
    {"name": "Eve",   "grade": "A"},
]
students.sort(key=lambda s: s["grade"])   # sort first!
by_grade = {grade: [s["name"] for s in group]
            for grade, group in groupby(students, key=lambda s: s["grade"])}
print(f"Grouped by grade: {by_grade}")

# --- combinations and permutations: combinatorics ---
items = ["A", "B", "C", "D"]
combs = list(combinations(items, 2))   # all pairs, no repeats, order doesn't matter
perms = list(permutations(items, 2))   # all pairs, order matters

print(f"Combinations(4,2): {len(combs)} pairs: {combs}")
print(f"Permutations(4,2): {len(perms)} arrangements")

# product: Cartesian product (all combinations across multiple iterables)
colors = ["red", "blue"]
sizes  = ["S", "M", "L"]
variants = list(product(colors, sizes))
print(f"Product (color × size): {variants}")


# =============================================================================
# SECTION 6: Immutability patterns for safe data sharing
# =============================================================================

# CONCEPT: FP favors immutable data. Python doesn't enforce this like Haskell,
# but we can use: tuples (over lists), frozensets, namedtuples, frozen dataclasses.
# Immutable data is safe to share across threads and closures without locking.

print("\n=== Section 6: Immutability Patterns ===")

from dataclasses import dataclass, field

@dataclass(frozen=True)   # frozen=True makes the dataclass immutable
class Config:
    """
    Frozen dataclass: all fields are read-only after creation.
    Can be used as a dict key (it's hashable).
    WHY: Configuration objects should not be accidentally mutated after creation.
    Use .replace() (via dataclasses.replace) to create modified copies.
    """
    host: str
    port: int
    timeout: int = 30
    max_retries: int = 3

import dataclasses

prod_config = Config("db.prod.com", 5432)
dev_config  = dataclasses.replace(prod_config, host="localhost", port=5433)
# Creates a NEW Config — prod_config is unchanged

print(f"Prod: {prod_config}")
print(f"Dev:  {dev_config}")

try:
    prod_config.port = 9999   # TypeError — frozen!
except Exception as e:
    print(f"Frozen config: {type(e).__name__}: {e}")

# Frozen dataclasses are hashable → can be dict keys or set members
config_cache = {prod_config: "production_connection_pool"}
print(f"Config as dict key: {config_cache[prod_config][:20]}...")


print("\n=== Functional programming complete ===")
print("FP principles in Python:")
print("  1. Pure functions: same input → same output, no side effects")
print("  2. map/filter/reduce: describe WHAT, not HOW (declarative)")
print("  3. Comprehensions: Pythonic map/filter, prefer over explicit loops")
print("  4. functools: lru_cache, partial, total_ordering, cached_property")
print("  5. itertools: lazy combinators, O(1) memory for any-size pipeline")
print("  6. Immutability: frozen dataclass, tuple, frozenset → safe sharing")
