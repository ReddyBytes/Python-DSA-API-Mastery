"""
18_performance_optimization/timeit_examples.py
================================================
CONCEPT: timeit — Python's standard library for micro-benchmarking code.
WHY THIS MATTERS: "Measure, don't guess." Before optimizing anything, you must
know what's slow and by how much. timeit isolates timing from startup noise by
running code thousands of times and taking the minimum (not average — minimum
reflects best-case CPU availability, not GC pauses or OS scheduling).

Prerequisite: Modules 01–12
"""

import timeit
import time

# =============================================================================
# SECTION 1: timeit basics — the three ways to use it
# =============================================================================

# CONCEPT: timeit has three usage modes:
# 1. timeit.timeit(stmt, number=N) → total time for N runs
# 2. timeit.repeat(stmt, repeat=R, number=N) → R measurements of N runs each
# 3. Command line: python -m timeit "stmt"
# Always use the MINIMUM of repeat() — minimum = best-case, unaffected by GC.

print("=== Section 1: timeit Basics ===")

# Mode 1: simple timing — total time for `number` repetitions
total = timeit.timeit(
    stmt="sum(range(1000))",
    number=10_000,
)
print(f"sum(range(1000)) × 10,000: {total:.4f}s  "
      f"({total / 10_000 * 1e6:.2f} µs/call)")

# Mode 2: repeat — get multiple measurements, use min()
# WHY MIN not AVERAGE: other processes can interrupt runs; min is most reliable
measurements = timeit.repeat(
    stmt="'-'.join(str(i) for i in range(100))",
    repeat=5,
    number=10_000,
)
best = min(measurements)
print(f"\njoin via generator × 10,000 (5 runs):")
print(f"  All measurements: {[f'{m:.3f}s' for m in measurements]}")
print(f"  Best (use this):  {best:.4f}s = {best / 10_000 * 1e6:.2f} µs/call")

# Mode 3: setup parameter — import and prepare without timing it
setup_code = "data = list(range(10_000))"
stmt = "42 in data"

total = timeit.timeit(stmt=stmt, setup=setup_code, number=100_000)
print(f"\n'42 in list(range(10k))' × 100k: {total:.4f}s  "
      f"({total / 100_000 * 1e6:.2f} µs/call)")


# =============================================================================
# SECTION 2: Comparing alternatives — the main use case of timeit
# =============================================================================

# CONCEPT: timeit shines when comparing two implementations of the same thing.
# Run them with the same `number` and compare the minimum of repeat().

print("\n=== Section 2: Comparing Alternatives ===")

def compare(label_a: str, stmt_a: str, label_b: str, stmt_b: str,
            setup: str = "", number: int = 100_000, repeat: int = 5) -> None:
    """Run both statements and print a side-by-side comparison."""
    time_a = min(timeit.repeat(stmt_a, setup=setup, repeat=repeat, number=number))
    time_b = min(timeit.repeat(stmt_b, setup=setup, repeat=repeat, number=number))
    faster, ratio = (label_a, time_b / time_a) if time_a < time_b else (label_b, time_a / time_b)
    print(f"  {label_a:35}: {time_a / number * 1e6:.2f} µs/call")
    print(f"  {label_b:35}: {time_b / number * 1e6:.2f} µs/call")
    print(f"  → {faster} is {ratio:.1f}x faster")


# 1. String concatenation vs join
print("String building:")
compare(
    "+= concatenation (loop)",   "result = ''; [result := result + str(i) for i in range(50)]",
    "str.join (correct pattern)", "result = ''.join(str(i) for i in range(50))",
    number=10_000,
)

# 2. List vs set membership
print("\nMembership test (n=10,000):")
compare(
    "42 in list",  "42 in data_list",
    "42 in set",   "42 in data_set",
    setup="data_list = list(range(10_000)); data_set = set(range(10_000))",
    number=1_000_000,
)

# 3. Dict get vs try/except for key lookup
print("\nDict key access (key exists 90% of time):")
compare(
    "dict.get(key, default)",   "d.get(42, -1)",
    "try/except KeyError",       "try:\n  v = d[42]\nexcept KeyError:\n  v = -1",
    setup="d = {i: i*2 for i in range(100)}",
    number=1_000_000,
)

# 4. List comprehension vs map()
print("\nTransform 1000 items:")
compare(
    "list comprehension",  "[x*x for x in data]",
    "map()",               "list(map(lambda x: x*x, data))",
    setup="data = list(range(1000))",
    number=10_000,
)

# 5. f-string vs % formatting
print("\nString formatting:")
compare(
    "f-string",     "f'Hello, {name}! You are {age} years old.'",
    "% formatting", "'Hello, %s! You are %d years old.' % (name, age)",
    setup="name = 'Alice'; age = 30",
    number=1_000_000,
)


# =============================================================================
# SECTION 3: Using globals/locals to benchmark your own code
# =============================================================================

# CONCEPT: When benchmarking code that references local functions or variables,
# pass them via the `globals` parameter. Otherwise timeit can't find them.

print("\n=== Section 3: Benchmarking Your Own Functions ===")

def recursive_fib(n: int) -> int:
    if n <= 1: return n
    return recursive_fib(n - 1) + recursive_fib(n - 2)


_memo: dict = {}
def memo_fib(n: int) -> int:
    if n in _memo: return _memo[n]
    if n <= 1: return n
    _memo[n] = memo_fib(n - 1) + memo_fib(n - 2)
    return _memo[n]


from functools import lru_cache

@lru_cache(maxsize=None)
def cached_fib(n: int) -> int:
    if n <= 1: return n
    return cached_fib(n - 1) + cached_fib(n - 2)


N = 20

# Pass `globals()` so timeit can see our functions
t_recursive = min(timeit.repeat(
    f"recursive_fib({N})", globals=globals(), repeat=3, number=1000
))
t_memo = min(timeit.repeat(
    f"memo_fib({N})", globals=globals(), repeat=3, number=1000
))
t_cache = min(timeit.repeat(
    f"cached_fib({N})", globals=globals(), repeat=3, number=1000
))

print(f"fibonacci({N}):")
print(f"  Recursive (no cache): {t_recursive / 1000 * 1e6:.2f} µs/call")
print(f"  Manual memoize:       {t_memo / 1000 * 1e6:.2f} µs/call  "
      f"({t_recursive / max(t_memo, 1e-9):.0f}x faster)")
print(f"  @lru_cache:           {t_cache / 1000 * 1e6:.2f} µs/call  "
      f"({t_recursive / max(t_cache, 1e-9):.0f}x faster)")


# =============================================================================
# SECTION 4: time.perf_counter for wall-clock benchmarks
# =============================================================================

# CONCEPT: timeit is for micro-benchmarks (µs–ms range, repeated N times).
# For larger operations (file I/O, network, DB, multi-step workflows),
# use time.perf_counter() for single-run wall-clock timing.
# time.perf_counter() — highest resolution monotonic clock on the system.
# time.process_time() — CPU time only (excludes sleep / waiting).

print("\n=== Section 4: perf_counter for Larger Benchmarks ===")

def generate_and_process(n: int) -> dict:
    """Multi-step operation: generate, filter, aggregate."""
    data    = [i ** 2 for i in range(n)]
    evens   = [x for x in data if x % 2 == 0]
    total   = sum(evens)
    maximum = max(evens)
    return {"count": len(evens), "sum": total, "max": maximum}


N = 100_000
wall_start = time.perf_counter()
cpu_start  = time.process_time()

result = generate_and_process(N)

wall_elapsed = time.perf_counter() - wall_start
cpu_elapsed  = time.process_time() - cpu_start

print(f"  N={N:,}: count={result['count']:,}, sum={result['sum']:,}")
print(f"  Wall clock: {wall_elapsed * 1000:.2f} ms")
print(f"  CPU time:   {cpu_elapsed * 1000:.2f} ms")
print(f"  Overhead (wall - CPU) ≈ OS/GC: {(wall_elapsed - cpu_elapsed) * 1000:.2f} ms")


# =============================================================================
# SECTION 5: Benchmark helper — reusable timing decorator
# =============================================================================

print("\n=== Section 5: Benchmark Decorator ===")

def benchmark(repeat: int = 5, number: int = 1000):
    """
    Decorator that prints timing stats when the function is called.
    Reports: min, max, mean across `repeat` rounds of `number` calls each.
    """
    def decorator(func):
        import functools
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            times = []
            for _ in range(repeat):
                start = time.perf_counter()
                for _ in range(number):
                    result = func(*args, **kwargs)
                times.append(time.perf_counter() - start)

            per_call_us = [(t / number) * 1e6 for t in times]
            print(f"  {func.__name__}({', '.join(str(a) for a in args)}):")
            print(f"    best={min(per_call_us):.3f} µs  "
                  f"mean={sum(per_call_us)/len(per_call_us):.3f} µs  "
                  f"worst={max(per_call_us):.3f} µs  "
                  f"(n={number:,} × {repeat} rounds)")
            return result
        return wrapper
    return decorator


@benchmark(repeat=3, number=10_000)
def count_vowels_loop(text: str) -> int:
    count = 0
    for char in text.lower():
        if char in "aeiou":
            count += 1
    return count

@benchmark(repeat=3, number=10_000)
def count_vowels_sum(text: str) -> int:
    return sum(1 for c in text.lower() if c in "aeiou")

text = "The quick brown fox jumps over the lazy dog"
count_vowels_loop(text)
count_vowels_sum(text)


print("\n=== timeit examples complete ===")
print("Benchmarking rules of thumb:")
print("  1. Always use min() from repeat(), not mean — min = best CPU availability")
print("  2. Run enough iterations for the total to be >100ms (reduces noise)")
print("  3. Use setup= for imports and data preparation — don't time those")
print("  4. Use globals= when benchmarking your own functions")
print("  5. Microbenchmark → timeit; larger flows → perf_counter")
print("  6. Benchmark on TARGET hardware — laptop ≠ production server")
