"""
18_performance_optimization/cProfile_examples.py
==================================================
CONCEPT: cProfile — Python's built-in deterministic profiler.
WHY THIS MATTERS: You cannot optimize what you haven't measured.
cProfile identifies which functions consume the most time in a real program run.
Without it, developers guess wrong about bottlenecks 90% of the time.
Workflow: profile → identify hotspot → optimize → profile again → confirm speedup.

Prerequisite: Modules 01–12
"""

import cProfile
import pstats
import io
import time
import math
from functools import lru_cache

# =============================================================================
# SECTION 1: cProfile basics — profiling a function
# =============================================================================

# CONCEPT: cProfile hooks into the Python interpreter's function call/return
# events. For every function call it records: call count, cumulative time
# (total time in function + callees), and per-call time.
# KEY COLUMNS in stats output:
#   ncalls     — number of times the function was called
#   tottime    — time IN THIS function (excluding callees)
#   cumtime    — cumulative time (this function + everything it called)
#   percall    — tottime / ncalls  OR  cumtime / ncalls
# Look for functions with HIGH tottime — those are the actual hotspots.

print("=== Section 1: cProfile Basics ===")

# A deliberately slow program to profile
def slow_fibonacci(n: int) -> int:
    """Intentionally unoptimized recursive Fibonacci — O(2^n)."""
    if n <= 1:
        return n
    return slow_fibonacci(n - 1) + slow_fibonacci(n - 2)


def process_data(items: list) -> dict:
    """Simulates a multi-step data processing pipeline."""
    # Step 1: expensive transformation
    transformed = [math.sqrt(abs(x) + 1) * math.pi for x in items]

    # Step 2: inefficient string concatenation inside loop (known anti-pattern)
    result_str = ""
    for val in transformed[:100]:
        result_str += f"{val:.4f},"   # O(n²) string building

    # Step 3: sorting
    sorted_vals = sorted(transformed, reverse=True)

    return {
        "first_10": sorted_vals[:10],
        "total":    sum(sorted_vals),
        "preview":  result_str[:50],
    }


def main_workload():
    """The function we want to profile."""
    # Fibonacci calls (CPU-bound recursion)
    fib_results = [slow_fibonacci(n) for n in range(20)]

    # Data processing (memory + CPU)
    import random
    random.seed(42)
    data = [random.randint(-1000, 1000) for _ in range(5000)]
    stats = process_data(data)

    return fib_results, stats


# METHOD 1: Profile with cProfile.run() — simplest, prints to stdout
print("Profile output (sorted by cumulative time):")
print("-" * 60)
cProfile.run("main_workload()", sort="cumulative")


# =============================================================================
# SECTION 2: Capturing profile output programmatically
# =============================================================================

# CONCEPT: cProfile.Profile() gives you an object you can start/stop and
# dump stats from. pstats.Stats processes the raw profile data into readable
# reports. This lets you embed profiling in code without printing everything.

print("\n=== Section 2: Programmatic Profiling with pstats ===")

def profile_and_report(func, *args, sort_by="cumulative", top_n=15, **kwargs):
    """
    Profile a function call and return a formatted report string.
    This pattern is used in production to conditionally profile slow requests.
    """
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()

    # Redirect stats output to a string buffer
    stream = io.StringIO()
    stats  = pstats.Stats(profiler, stream=stream)
    stats.strip_dirs()               # remove full path prefixes
    stats.sort_stats(sort_by)        # sort by: cumulative, tottime, ncalls
    stats.print_stats(top_n)         # show only top N functions

    return result, stream.getvalue()


result, report = profile_and_report(main_workload, top_n=10)
print(report)


# =============================================================================
# SECTION 3: Profiling specific code sections with enable()/disable()
# =============================================================================

# CONCEPT: You don't always want to profile an entire function. Use
# profiler.enable() and profiler.disable() to bracket the code of interest.
# This is useful for profiling just the inner loop of a larger function.

print("\n=== Section 3: Selective Section Profiling ===")

def application_with_setup():
    """Simulates an app where setup is fast but processing is slow."""
    # Fast setup — don't profile this
    config = {"batch_size": 100, "workers": 4}

    # === START profiling here ===
    profiler = cProfile.Profile()
    profiler.enable()

    # Slow processing — profile this
    results = []
    for i in range(50):
        fib = slow_fibonacci(15)
        results.append(fib)

    profiler.disable()
    # === END profiling here ===

    # Fast post-processing — don't profile this
    total = sum(results)

    # Report
    stream = io.StringIO()
    pstats.Stats(profiler, stream=stream).strip_dirs().sort_stats("tottime").print_stats(5)
    print(stream.getvalue())

    return total, config


total, config = application_with_setup()
print(f"  Total: {total:,}")


# =============================================================================
# SECTION 4: Profile → Optimize → Verify workflow
# =============================================================================

# CONCEPT: Profiling is only useful if it drives optimization.
# This section shows the complete workflow: identify the bottleneck,
# apply a fix, and verify the speedup with numbers.

print("\n=== Section 4: Profile → Optimize → Verify ===")

# BEFORE: unoptimized
def fib_slow(n: int) -> list:
    """Naive recursive fibonacci for 0..n-1. O(2^n) time."""
    def inner(k):
        if k <= 1: return k
        return inner(k-1) + inner(k-2)
    return [inner(i) for i in range(n)]


# AFTER: optimized with @lru_cache
@lru_cache(maxsize=None)
def _fib_cached(k: int) -> int:
    if k <= 1: return k
    return _fib_cached(k-1) + _fib_cached(k-2)

def fib_fast(n: int) -> list:
    """Memoized fibonacci for 0..n-1. O(n) time."""
    return [_fib_cached(i) for i in range(n)]


# ALSO BEFORE: O(n²) string building
def build_report_slow(values: list) -> str:
    result = ""
    for v in values:
        result += f"{v:.2f}, "    # string concat: copies the string every time
    return result.rstrip(", ")


# AFTER: O(n) join
def build_report_fast(values: list) -> str:
    return ", ".join(f"{v:.2f}" for v in values)


# Profile BOTH versions
N = 22   # keep small for slow version
vals = list(range(1, 101))

_, slow_report = profile_and_report(fib_slow, N, top_n=3)
_, fast_report = profile_and_report(fib_fast, N, top_n=3)

# Measure speedup with timeit
import timeit

t_slow_fib = timeit.timeit(lambda: fib_slow(N), number=5)
t_fast_fib = timeit.timeit(lambda: fib_fast(N), number=1000)

t_slow_str = timeit.timeit(lambda: build_report_slow(vals), number=10_000)
t_fast_str = timeit.timeit(lambda: build_report_fast(vals), number=10_000)

print(f"Fibonacci({N}) speedup:")
print(f"  Before (recursive): {t_slow_fib / 5 * 1000:.2f} ms/call")
print(f"  After  (@lru_cache): {t_fast_fib / 1000 * 1000:.4f} ms/call")
print(f"  Speedup: {(t_slow_fib/5) / (t_fast_fib/1000):.0f}x faster")

print(f"\nString building ({len(vals)} items) speedup:")
print(f"  Before (+=):  {t_slow_str / 10_000 * 1e6:.2f} µs/call")
print(f"  After  (join): {t_fast_str / 10_000 * 1e6:.2f} µs/call")
print(f"  Speedup: {t_slow_str / t_fast_str:.1f}x faster")


# =============================================================================
# SECTION 5: Context manager for profiling code blocks
# =============================================================================

print("\n=== Section 5: Profile Context Manager ===")

from contextlib import contextmanager

@contextmanager
def profile_block(label: str, top_n: int = 10, sort_by: str = "tottime"):
    """
    Context manager for profiling any code block.
    Usage:
        with profile_block("my operation"):
            do_something_expensive()
    """
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        yield profiler
    finally:
        profiler.disable()
        stream = io.StringIO()
        pstats.Stats(profiler, stream=stream).strip_dirs().sort_stats(sort_by).print_stats(top_n)
        print(f"\n--- Profile: {label} ---")
        print(stream.getvalue())


with profile_block("fibonacci batch", top_n=5):
    results = [slow_fibonacci(i) for i in range(18)]

print(f"  Results: {results[:5]}...")


print("\n=== cProfile examples complete ===")
print("Profiling workflow:")
print("  1. Profile: cProfile.run() or Profile().enable()/.disable()")
print("  2. Read stats: sort by 'tottime' to find pure hotspots")
print("              or 'cumulative' to find expensive call trees")
print("  3. Focus on ncalls × percall — high-frequency + slow functions first")
print("  4. Optimize the #1 hotspot")
print("  5. Re-profile to confirm improvement")
print("  6. Repeat until fast enough")
print()
print("Don't optimize prematurely — profile first, then act on data.")
