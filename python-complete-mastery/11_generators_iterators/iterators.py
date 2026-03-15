"""
11_generators_iterators/iterators.py
========================================
CONCEPT: The iterator protocol — what makes Python's `for` loop work.
WHY THIS MATTERS: Everything you iterate over (list, dict, file, range,
generator, custom object) implements the iterator protocol.
Understanding it lets you make your own objects iterable — and work
with any existing iterator uniformly.

Prerequisite: Modules 01–11 generators.py
"""

import sys
from typing import Iterator

# =============================================================================
# SECTION 1: The iterator protocol — __iter__ and __next__
# =============================================================================

# CONCEPT: An "iterable" is anything with __iter__() that returns an iterator.
# An "iterator" has __next__() that returns the next item or raises StopIteration.
# The for loop calls iter(obj) then calls next() repeatedly until StopIteration.
# Lists, tuples, dicts, files, generators all implement this protocol.

print("=== Section 1: Iterator Protocol ===")

# SEE what for loop does under the hood:
my_list = [10, 20, 30]

# Python's for loop is EXACTLY this:
iterator = iter(my_list)          # calls my_list.__iter__()
while True:
    try:
        value = next(iterator)    # calls iterator.__next__()
        print(f"  Got: {value}")
    except StopIteration:
        break                     # for loop ends here

# Any class implementing __iter__ and __next__ is iterable in for loops
class Countdown:
    """
    Custom iterator that counts down from n to 1.
    Implements the full iterator protocol manually.
    WHY: understand what Python is doing for you with built-in iterables.
    """

    def __init__(self, start: int):
        self.current = start

    def __iter__(self):
        """
        Return the iterator object.
        When the class IS its own iterator, return self.
        WHY: allows `for x in countdown_obj` to work.
        """
        return self

    def __next__(self):
        """
        Return the next value, or raise StopIteration when done.
        This is called by next() and by the for loop.
        """
        if self.current <= 0:
            raise StopIteration   # signals the for loop to stop
        value = self.current
        self.current -= 1
        return value


countdown = Countdown(5)
print("\nCountdown from 5:")
for n in countdown:    # Python calls __iter__, then __next__ repeatedly
    print(f"  {n}")

# Works with all iteration contexts
print(f"\nAll at once: {list(Countdown(5))}")
print(f"sum: {sum(Countdown(5))}")
print(f"max: {max(Countdown(5))}")
print(f"In comprehension: {[n*2 for n in Countdown(4)]}")


# =============================================================================
# SECTION 2: Iterable vs Iterator — important distinction
# =============================================================================

# CONCEPT:
# Iterable: has __iter__(), can be iterated MULTIPLE times (list, tuple, set)
# Iterator: has __next__(), can only be iterated ONCE (exhaustible)
# Generators are iterators (single-use).
# Lists are iterables (reusable) — iter(list) creates a fresh iterator each time.

print("\n=== Section 2: Iterable vs Iterator ===")

my_list = [1, 2, 3]

# Lists are iterables — each for loop gets a fresh iterator
for x in my_list:
    pass
for x in my_list:
    pass   # works! list is not exhausted
print(f"List can be iterated multiple times: {list(my_list)}")

# Generators (iterators) are single-use
gen = (x**2 for x in range(5))
print(f"First iteration: {list(gen)}")
print(f"Second iteration: {list(gen)}")  # empty! generator exhausted

# Check if something is iterable vs iterator
from collections.abc import Iterable, Iterator

print(f"\nlist is Iterable: {isinstance(my_list, Iterable)}")
print(f"list is Iterator: {isinstance(my_list, Iterator)}")

list_iter = iter(my_list)
print(f"iter(list) is Iterator: {isinstance(list_iter, Iterator)}")
print(f"generator is Iterator: {isinstance(gen, Iterator)}")

# Separation of iterable vs iterator
class NumberRange:
    """
    Iterable (NOT an iterator itself) — can be iterated multiple times.
    Each iteration creates a fresh RangeIterator.
    WHY: separate iterable from iterator allows re-use.
    """

    def __init__(self, start: int, stop: int):
        self.start = start
        self.stop  = stop

    def __iter__(self):
        """Returns a NEW iterator each time — allows multiple concurrent loops."""
        return RangeIterator(self.start, self.stop)

    def __len__(self):
        return max(0, self.stop - self.start)

    def __contains__(self, value: int) -> bool:
        return self.start <= value < self.stop


class RangeIterator:
    """The actual iterator — maintains position state."""

    def __init__(self, start: int, stop: int):
        self.current = start
        self.stop    = stop

    def __iter__(self):
        return self   # iterator returns self

    def __next__(self):
        if self.current >= self.stop:
            raise StopIteration
        value = self.current
        self.current += 1
        return value


r = NumberRange(5, 10)
print(f"\nNumberRange(5, 10):")
print(f"  len: {len(r)}")
print(f"  7 in r: {7 in r}")
print(f"  First pass: {list(r)}")
print(f"  Second pass: {list(r)}")   # fresh iterator each time!


# =============================================================================
# SECTION 3: Making existing classes iterable — the __iter__ shortcut
# =============================================================================

# CONCEPT: If your class stores items in a collection, the easiest way to
# make it iterable is to delegate __iter__ to that collection's __iter__.

print("\n=== Section 3: Delegating Iteration ===")

class Library:
    """A library that manages a collection of books."""

    def __init__(self):
        self._books = []

    def add(self, title: str, author: str) -> "Library":
        self._books.append({"title": title, "author": author})
        return self   # method chaining

    def __iter__(self):
        """Delegate iteration to the internal list — the simplest approach."""
        return iter(self._books)   # delegate to list.__iter__

    def __len__(self):
        return len(self._books)

    def __contains__(self, title: str) -> bool:
        return any(b["title"] == title for b in self._books)


library = (Library()
           .add("Clean Code", "Robert Martin")
           .add("The Pragmatic Programmer", "David Thomas")
           .add("Python Cookbook", "David Beazley"))

print("Library books:")
for book in library:
    print(f"  '{book['title']}' by {book['author']}")

print(f"Count: {len(library)}")
print(f"Has 'Clean Code': {'Clean Code' in library}")


# =============================================================================
# SECTION 4: Generator-based iterators — the pythonic way
# =============================================================================

# CONCEPT: Instead of writing __iter__/__next__ manually, define __iter__
# as a generator function. Python handles the iterator protocol for you.
# This is the PREFERRED pattern for most cases — cleaner and more readable.

print("\n=== Section 4: Generator-Based Iterator ===")

class FileProcessor:
    """Processes a data store, yielding transformed records."""

    def __init__(self, records: list):
        self._records = records

    def __iter__(self):
        """
        Generator-based iterator — much simpler than writing __next__.
        Each `yield` automatically handles the iterator protocol.
        """
        for record in self._records:
            # Validate
            if not record.get("name"):
                continue   # skip invalid records

            # Transform
            yield {
                "name":     record["name"].strip().title(),
                "email":    record.get("email", "").lower(),
                "active":   record.get("active", True),
            }

raw_records = [
    {"name": "  alice smith  ", "email": "ALICE@EXAMPLE.COM"},
    {"name": "",                "email": "invalid"},          # skipped
    {"name": "bob jones",       "email": "BOB@EXAMPLE.COM", "active": False},
    {"name": "carol white"},
]

processor = FileProcessor(raw_records)
print("Processed records:")
for rec in processor:
    print(f"  {rec}")

# Still re-iterable (each for loop calls __iter__ which creates fresh generator)
count = sum(1 for _ in processor)
print(f"Second iteration count: {count}")


# =============================================================================
# SECTION 5: itertools — battle-tested iterator utilities
# =============================================================================

# CONCEPT: itertools provides high-performance, memory-efficient iterator
# building blocks. All lazy — no intermediate data structures.

print("\n=== Section 5: itertools ===")

from itertools import (
    chain, islice, takewhile, dropwhile,
    cycle, repeat, count,
    zip_longest, groupby, starmap,
    accumulate
)
import operator

# chain — combine multiple iterables as one stream
a = [1, 2, 3]
b = [4, 5, 6]
c = [7, 8, 9]
combined = list(chain(a, b, c))
print(f"chain: {combined}")

# islice — lazy slicing of any iterator
gen = (x**2 for x in range(100))
first_5  = list(islice(gen, 5))          # take first 5
gen = (x**2 for x in range(100))
skip_take = list(islice(gen, 3, 8))      # items 3-7 (0-indexed)
print(f"islice first 5: {first_5}")
print(f"islice 3-8: {skip_take}")

# cycle — repeat an iterable forever (for round-robin scheduling)
colors = cycle(["red", "green", "blue"])
pattern = [next(colors) for _ in range(7)]
print(f"cycle: {pattern}")

# repeat — repeat a value N times (or forever)
defaults = list(repeat(0, 5))
print(f"repeat: {defaults}")

# count — infinite counter (like range but infinite)
counter = count(100, 5)   # start=100, step=5
first_4 = [next(counter) for _ in range(4)]
print(f"count(100,5): {first_4}")

# zip_longest — zip but fill shorter iterables with fillvalue
names  = ["Alice", "Bob", "Carol"]
scores = [95, 87]        # shorter!
result = list(zip_longest(names, scores, fillvalue=0))
print(f"zip_longest: {result}")

# accumulate — running totals (or any binary operation)
data = [10, 5, 20, 3, 15]
running_sum  = list(accumulate(data))
running_max  = list(accumulate(data, max))
running_prod = list(accumulate(data, operator.mul))
print(f"accumulate (sum): {running_sum}")
print(f"accumulate (max): {running_max}")
print(f"accumulate (product): {running_prod}")

# groupby — group consecutive items by key (data MUST be sorted first!)
transactions = [
    ("Alice", 100), ("Alice", 200), ("Bob", 50),
    ("Bob", 150), ("Carol", 300),
]
totals = {
    user: sum(amount for _, amount in group)
    for user, group in groupby(transactions, key=lambda t: t[0])
}
print(f"totals by user: {totals}")


print("\n=== Iterators complete ===")
print("Iterator protocol summary:")
print("  Iterable: __iter__() returns an iterator — can iterate multiple times")
print("  Iterator: __next__() returns items — single-use, maintains state")
print("  for loop = iter(obj) + while next() until StopIteration")
print("  Cleanest way: define __iter__ as a generator function (yield inside)")
print("  itertools: lazy utilities for common iterator patterns")
