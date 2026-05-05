"""
11_generators_iterators/generators.py
========================================
CONCEPT: Generators — functions that produce values lazily using `yield`.
WHY THIS MATTERS: Generators are the foundation of memory-efficient Python.
Instead of building an entire list in memory, a generator produces values
one at a time — on demand. A function that yields 1 billion items uses
the same memory as one that yields 1 item.
Used in: data pipelines, streaming APIs, infinite sequences, coroutines.

Prerequisite: Modules 01–10
"""

import sys
import time
from typing import Generator, Iterator

# =============================================================================
# SECTION 1: What generators are and how they work
# =============================================================================

# CONCEPT: A function with `yield` is a generator function.
# Calling it returns a generator object — no code runs yet.
# Calling next() on it runs until the next `yield`, pauses, and returns the value.
# State is suspended between yields: local variables are preserved.
# This is fundamentally different from return, which destroys the frame.

print("=== Section 1: Generator Basics ===")

def count_up(start: int, stop: int):
    """
    Generator function — notice the `yield` keyword.
    State (n) is preserved between yields.
    The function is paused at each yield and resumed by next().
    """
    n = start
    while n <= stop:
        print(f"  (yielding {n})")
        yield n           # suspend execution, return n to caller
        n += 1            # resumed here when caller calls next()
    print("  (generator exhausted)")

gen = count_up(1, 3)     # NO code runs here — just creates the generator
print(f"Generator object: {gen}")
print(f"Type: {type(gen)}")

# Manually advance with next()
print("\nManually calling next():")
print(f"next() → {next(gen)}")   # runs until first yield
print(f"next() → {next(gen)}")   # runs from after last yield to next yield
print(f"next() → {next(gen)}")   # runs to end

try:
    next(gen)   # generator is exhausted
except StopIteration:
    print("StopIteration: generator exhausted")

# Generators work with for loops naturally (for calls next() automatically)
print("\nfor loop (creates fresh generator):")
for value in count_up(1, 4):
    print(f"  Got: {value}")


# =============================================================================
# SECTION 2: Generator expressions — inline lazy sequences
# =============================================================================

# CONCEPT: Just like list comprehensions use [], generator expressions use ().
# They're lazy — items computed on demand.
# Use () when you'll consume once (loop, sum, etc.)
# Use [] when you need to: index, slice, reuse, or check length.

print("\n=== Section 2: Generator Expressions ===")

n = 1_000_000

# List comprehension — allocates ALL 1M items immediately
list_all  = [x**2 for x in range(n)]         # ~8MB
gen_all   = (x**2 for x in range(n))          # ~200 bytes

print(f"List of {n:,} squares: {sys.getsizeof(list_all):,} bytes")
print(f"Generator for same:    {sys.getsizeof(gen_all):,} bytes")

# Consuming a generator expression
squares_sum = sum(x**2 for x in range(100))   # sum consumes the generator
print(f"\nSum of squares 0-99: {squares_sum:,}")

# Chaining generator expressions (pipeline!)
words = "the quick brown fox jumps over the lazy dog".split()

# Each step is lazy — no intermediate lists created
words_long    = (w for w in words if len(w) > 3)         # filter
words_upper   = (w.upper() for w in words_long)           # transform
words_encoded = (w.encode() for w in words_upper)         # another transform

# Only when we consume do any items flow through the whole pipeline
for encoded in words_encoded:
    print(f"  {encoded}", end=" ")
print()


# =============================================================================
# SECTION 3: Real-world generator patterns
# =============================================================================

# CONCEPT: Generators shine in data pipeline scenarios.
# Each generator yields one item, the next generator consumes it.
# No intermediate lists → O(1) memory regardless of dataset size.

print("\n=== Section 3: Data Pipeline Generators ===")

def read_log_lines(num_lines: int) -> Generator[str, None, None]:
    """Simulate reading a large log file line by line."""
    for i in range(num_lines):
        yield f"2024-01-15 10:{i%60:02d}:00 {'ERROR' if i%20==0 else 'INFO'} Request {i} processed in {10+i%50}ms"

def parse_log_lines(lines: Iterator[str]) -> Generator[dict, None, None]:
    """Parse each log line into a structured dict."""
    for line in lines:
        parts = line.split(" ", 3)
        if len(parts) >= 4:
            yield {
                "date":     parts[0],
                "time":     parts[1],
                "level":    parts[2],
                "message":  parts[3],
            }

def filter_errors(records: Iterator[dict]) -> Generator[dict, None, None]:
    """Yield only ERROR records."""
    for record in records:
        if record["level"] == "ERROR":
            yield record

def enrich_records(records: Iterator[dict]) -> Generator[dict, None, None]:
    """Add derived fields to each record."""
    for i, record in enumerate(records):
        record["error_id"] = f"ERR-{i+1:04d}"
        yield record

# Wire the pipeline — O(1) memory for ANY number of log lines
raw_lines = read_log_lines(1000)
parsed    = parse_log_lines(raw_lines)
errors    = filter_errors(parsed)
enriched  = enrich_records(errors)

# Only now does data flow through the pipeline, one line at a time
first_5_errors = list(item for _, item in zip(range(5), enriched))
print(f"First 5 errors (from 1000 log lines, O(1) memory):")
for e in first_5_errors:
    print(f"  [{e['error_id']}] {e['time']} {e['message'][:40]}")


# =============================================================================
# SECTION 4: yield from — delegating to sub-generators
# =============================================================================

# CONCEPT: `yield from iterable` delegates yielding to another iterable.
# It's equivalent to: `for item in iterable: yield item` but more efficient
# and correctly propagates StopIteration, send(), and throw().
# Essential for recursive generators and generator composition.

print("\n=== Section 4: yield from ===")

def flatten(nested):
    """
    Recursively flatten arbitrarily nested iterables.
    `yield from` delegates to the recursive call — cleaner than for+yield.
    """
    for item in nested:
        if hasattr(item, "__iter__") and not isinstance(item, (str, bytes)):
            yield from flatten(item)   # recurse — yield from handles the delegation
        else:
            yield item

data = [1, [2, 3, [4, 5]], 6, [7, [8, [9, 10]]]]
print(f"Flattened: {list(flatten(data))}")

# yield from for combining multiple generators
def all_products():
    """Combine multiple data sources into one stream."""
    yield from ["Widget A", "Widget B"]      # from a list
    yield from (f"Gadget {i}" for i in range(3))   # from a generator
    yield from {f"Item {c}" for c in "ABC"}  # from a set (unordered!)

print(f"\nAll products: {list(all_products())}")


# =============================================================================
# SECTION 5: Infinite generators — sequences with no end
# =============================================================================

# CONCEPT: Generators can produce infinite sequences because they're lazy.
# A list of infinite items would crash immediately — a generator is fine.
# You consume only what you need using itertools.islice or take patterns.

print("\n=== Section 5: Infinite Generators ===")

def fibonacci() -> Generator[int, None, None]:
    """
    Infinite Fibonacci sequence.
    Runs forever — but callers only take what they need.
    """
    a, b = 0, 1
    while True:       # infinite loop — fine because generator is lazy!
        yield a
        a, b = b, a + b

def take(n: int, iterable) -> list:
    """Take first n items from any iterable."""
    result = []
    for i, item in enumerate(iterable):
        if i >= n:
            break
        result.append(item)
    return result

first_15 = take(15, fibonacci())
print(f"First 15 Fibonacci: {first_15}")

# Find first Fibonacci number > 1000
gen = fibonacci()
for fib in gen:
    if fib > 1000:
        print(f"First Fibonacci > 1000: {fib}")
        break

# Infinite counter for generating IDs
def id_generator(prefix: str = "ID", start: int = 1):
    """Generate sequential IDs: ID-001, ID-002, ..."""
    n = start
    while True:
        yield f"{prefix}-{n:03d}"
        n += 1

gen_id = id_generator("ORDER")
ids = [next(gen_id) for _ in range(5)]
print(f"Generated IDs: {ids}")


# =============================================================================
# SECTION 6: send() — two-way communication with generators
# =============================================================================

# CONCEPT: Generators can RECEIVE values via send(). The yield expression
# RETURNS the value sent from outside. This enables coroutine-like patterns
# where the generator is driven by data sent from the outside.
# This is the foundation of how Python's async/await works internally.

print("\n=== Section 6: Generator.send() ===")

def accumulator():
    """
    A generator that accumulates values sent to it.
    send(value) resumes the generator AND passes value as the yield expression.
    """
    total = 0
    while True:
        # Execution suspends here, waiting for the next send()
        # The value passed to send() becomes the value of the yield expression
        value = yield total   # yield current total, receive next value
        if value is None:
            break
        total += value
        print(f"  Received {value}, running total: {total}")

gen = accumulator()
next(gen)   # prime the generator — must call next() first before send()

gen.send(10)    # total becomes 10
gen.send(25)    # total becomes 35
gen.send(15)    # total becomes 50
final = gen.send(None)  # send None to stop, get final total... but this raises


print("\n=== Generators complete ===")
print("Generator mental model:")
print("  1. yield = pause execution, remember state, return value to caller")
print("  2. next() = resume from last yield")
print("  3. Generator expressions: () instead of [] → lazy, O(1) memory")
print("  4. Data pipelines: chain generators for O(1) memory ETL")
print("  5. yield from: delegate to sub-generator, handles all edge cases")
print("  6. Infinite generators: perfectly fine because of lazy evaluation")
print("  7. send(): two-way communication — how async/await works internally")
