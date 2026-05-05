"""
11_generators_iterators/memory_comparison.py
==============================================
CONCEPT: Demonstrating the memory difference between eager (list) and
lazy (generator) approaches for the same computation.
WHY THIS MATTERS: Choosing between list and generator can mean the
difference between a program that works and one that crashes with OOM.
This file contains concrete benchmarks you can run to see the difference.

Prerequisite: Modules 01–11 generators.py and iterators.py
"""

import sys
import time
import gc
import tracemalloc

# =============================================================================
# SECTION 1: Side-by-side memory comparison
# =============================================================================

# CONCEPT: The core tradeoff:
# List (eager): stores ALL items in memory immediately. O(n) space.
# Generator (lazy): stores only the current item + generator state. O(1) space.
# Both produce the same results — the difference is WHEN items are computed.

print("=== Section 1: Memory Side-by-Side ===")

n = 1_000_000

# EAGER: list comprehension materializes all 1M items immediately
list_comp = [x ** 2 for x in range(n)]
list_size  = sys.getsizeof(list_comp)

# LAZY: generator expression - only metadata about the computation stored
gen_expr   = (x ** 2 for x in range(n))
gen_size   = sys.getsizeof(gen_expr)

print(f"List of {n:,} squares: {list_size / 1024 / 1024:.1f} MB")
print(f"Generator for same:    {gen_size:,} bytes ({gen_size / list_size * 100:.4f}% of list)")
print(f"Memory ratio: list uses {list_size // gen_size:,}x more memory")


# =============================================================================
# SECTION 2: tracemalloc benchmark — measure actual allocations
# =============================================================================

# CONCEPT: tracemalloc measures precise memory allocations.
# We use take_snapshot().compare_to() to see the DIFFERENCE between approaches.

print("\n=== Section 2: tracemalloc Benchmark ===")

def measure_peak(func) -> tuple:
    """Run a function and return (result, peak_bytes_allocated)."""
    gc.collect()
    tracemalloc.start()
    snap_before = tracemalloc.take_snapshot()

    result = func()

    snap_after = tracemalloc.take_snapshot()
    tracemalloc.stop()

    total_before = sum(s.size for s in snap_before.statistics("filename"))
    total_after  = sum(s.size for s in snap_after.statistics("filename"))
    peak_bytes   = max(0, total_after - total_before)
    return result, peak_bytes


def eager_sum(n: int) -> int:
    """Eager approach: build full list then sum."""
    return sum([x for x in range(n)])

def lazy_sum(n: int) -> int:
    """Lazy approach: generator expression, sum consumes one item at a time."""
    return sum(x for x in range(n))

n = 500_000
result_eager, bytes_eager = measure_peak(lambda: eager_sum(n))
result_lazy,  bytes_lazy  = measure_peak(lambda: lazy_sum(n))

print(f"Eager (list): result={result_eager:,}, peak={bytes_eager / 1024:.1f} KB")
print(f"Lazy (gen):   result={result_lazy:,},  peak={bytes_lazy  / 1024:.1f} KB")
print(f"Same result: {result_eager == result_lazy}")
print(f"Memory ratio: {max(bytes_eager, 1) / max(bytes_lazy, 1):.1f}x")


# =============================================================================
# SECTION 3: Time comparison — eager vs lazy for different access patterns
# =============================================================================

# CONCEPT: It's not always about memory. Sometimes lazy is SLOWER because
# generator overhead (function calls) adds up for simple computations.
# Know when to use each:
# - Huge data, process once → generator (memory wins)
# - Small data, used multiple times → list (speed wins)
# - Need index/len/random access → list (generators don't support these)

print("\n=== Section 3: Time Comparison ===")

import timeit

n = 100_000

# Sum — should be similar, generator has slight overhead
list_time = timeit.timeit(
    f"sum([x*x for x in range({n})])", number=10
)
gen_time = timeit.timeit(
    f"sum(x*x for x in range({n}))", number=10
)

print(f"sum via list: {list_time:.3f}s")
print(f"sum via gen:  {gen_time:.3f}s")
print(f"Overhead: {'list' if list_time < gen_time else 'gen'} is faster (for small n, list often wins)")

# But for large data where list causes GC pressure, generator wins overall
print("\nFor N=10_000_000 (too big for accurate timing here, but at scale):")
print("  List approach: allocates 80MB+, triggers GC, slows everything")
print("  Generator: allocates ~200 bytes, no GC, consistent speed")


# =============================================================================
# SECTION 4: Real-world scenario — processing a large dataset
# =============================================================================

# CONCEPT: In data engineering, files and datasets are often gigabytes.
# Loading entirely into memory is impossible. Processing in a stream is required.

print("\n=== Section 4: Large Dataset Processing ===")

import tempfile
from pathlib import Path

# Create a "large" test dataset
tmp = Path(tempfile.mkdtemp())
data_file = tmp / "data.csv"

with open(data_file, "w") as f:
    f.write("id,name,score,active\n")
    for i in range(100_000):
        f.write(f"{i},{chr(65 + i%26)}_{i},{ (i*7)%100},{i%3!=0}\n")

# EAGER approach — loads ALL records into memory
def process_eager(filepath: str) -> tuple:
    """Load all rows into memory, then filter/transform."""
    with open(filepath) as f:
        lines = f.readlines()   # ALL lines in memory simultaneously!

    records = []
    for line in lines[1:]:   # skip header
        parts = line.strip().split(",")
        if len(parts) == 4:
            records.append({
                "id": int(parts[0]),
                "name": parts[1],
                "score": int(parts[2]),
                "active": parts[3] == "True",
            })

    # Filter
    active = [r for r in records if r["active"]]
    high_score = [r for r in active if r["score"] > 80]
    return len(high_score), sum(r["score"] for r in high_score)

# LAZY approach — processes one line at a time, O(1) memory
def process_lazy(filepath: str) -> tuple:
    """Generator pipeline — only one line in memory at a time."""

    def read_records(path):
        with open(path) as f:
            next(f)   # skip header
            for line in f:   # file iterator is lazy!
                parts = line.strip().split(",")
                if len(parts) == 4:
                    yield {
                        "id": int(parts[0]),
                        "name": parts[1],
                        "score": int(parts[2]),
                        "active": parts[3] == "True",
                    }

    def filter_active(records):
        return (r for r in records if r["active"])

    def filter_high_score(records, threshold=80):
        return (r for r in records if r["score"] > threshold)

    # Pipeline — O(1) memory
    records    = read_records(filepath)
    active     = filter_active(records)
    high_score = filter_high_score(active)

    count = 0
    total = 0
    for r in high_score:
        count += 1
        total += r["score"]
    return count, total

# Run both and compare
_, bytes_eager = measure_peak(lambda: process_eager(str(data_file)))
_, bytes_lazy  = measure_peak(lambda: process_lazy(str(data_file)))

count_e, sum_e = process_eager(str(data_file))
count_l, sum_l = process_lazy(str(data_file))

print(f"Eager: count={count_e}, sum={sum_e}, memory={bytes_eager/1024:.1f}KB")
print(f"Lazy:  count={count_l}, sum={sum_l}, memory={bytes_lazy/1024:.1f}KB")
print(f"Same results: {count_e == count_l and sum_e == sum_l}")


# =============================================================================
# SECTION 5: When to use list vs generator — decision guide
# =============================================================================

print("\n=== Section 5: Decision Guide ===")

decision_guide = """
┌─────────────────────────────────────────────────────────────────────┐
│ Use LIST when:                    │ Use GENERATOR when:             │
├──────────────────────────────────┼──────────────────────────────────┤
│ • Need to iterate MULTIPLE times  │ • Iterate only ONCE             │
│ • Need random access (list[i])    │ • Data is too large for RAM     │
│ • Need len()                      │ • Part of a pipeline            │
│ • Need to sort the results        │ • Producing infinite sequences  │
│ • Need to reverse                 │ • Values are expensive to       │
│ • Sharing with other code         │   compute and may not all be    │
│ • Small data (< a few MB)         │   needed                        │
│ • Need index/slice                │ • Chaining transformations      │
└───────────────────────────────────┴─────────────────────────────────┘

Thumb rule: if you're doing sum(), any(), all(), max(), or a single
for loop — use a generator expression. If you need anything else — list.
"""
print(decision_guide)

# Concrete examples
print("Generator (correct):")
print("  total = sum(record['score'] for record in records)")
print("  has_error = any('ERROR' in line for line in log_file)")
print("  first_match = next((r for r in records if r['id'] == 42), None)")
print()
print("List (needed):")
print("  scores = [r['score'] for r in records]  # need to sort later")
print("  sorted_scores = sorted(r['score'] for r in records)  # sort forces list")
print("  unique = set(r['category'] for r in records)  # set forces evaluation")


print("\n=== Memory comparison complete ===")
