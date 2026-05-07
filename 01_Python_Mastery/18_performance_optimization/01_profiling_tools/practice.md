# 💻 Practice — Profiling Tools (12 Questions)

> Covers: cProfile, pstats, timeit, line_profiler, memory_profiler, tracemalloc, snakeviz

---

## Quick Index

| # | Concept | Difficulty |
|---|---------|-----------|
| Q1 | Run cProfile on a function | 🟢 Basic |
| Q2 | Read pstats output: tottime vs cumtime | 🟢 Basic |
| Q3 | Sort pstats by cumtime, show top 5 | 🟡 Intermediate |
| Q4 | timeit: benchmark list comprehension vs for loop | 🟡 Intermediate |
| Q5 | timeit: use setup param to import before timing | 🟡 Intermediate |
| Q6 | timeit: why use min() not mean() | 🟡 Intermediate |
| Q7 | @profile with line_profiler | 🟡 Intermediate |
| Q8 | memory_profiler: trace peak memory of a function | 🟡 Intermediate |
| Q9 | Write a context manager that profiles any block | 🟠 Advanced |
| Q10 | Interpret a snakeviz flamegraph | 🟠 Advanced |
| Q11 | Use tracemalloc to find a memory leak | 🟡 Intermediate |
| Q12 | Write a decorator that logs timing + memory | 🟠 Advanced |

---

### Q1 · Run cProfile on a Function 🟢

Write a function `compute(n)` that does `sum(i*i for i in range(n))`. Use `cProfile.run()` to profile a call with `n=100_000`. Print the output sorted by cumulative time.

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Pass the call as a string to `cProfile.run()`. Use the `sort` argument.
</details>

<details>
<summary>✅ Answer</summary>

```python
import cProfile

def compute(n):
    return sum(i * i for i in range(n))

cProfile.run("compute(100_000)", sort="cumulative")
```

**Why:** `cProfile.run()` is the simplest entry point — pass the call as a string and it profiles the entire execution, printing results to stdout.
</details>

---

### Q2 · Read pstats Output: tottime vs cumtime 🟢

Given a profile of a function that calls helper functions, explain: which column tells you where the CPU is actually burned (excluding callees), and which tells you the cost of the whole call tree?

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Think about "inside only" vs "inside plus everything called from inside".
</details>

<details>
<summary>✅ Answer</summary>

```python
# tottime: time spent INSIDE this function only (not counting subcalls)
# cumtime: time spent in this function + ALL functions it called

# Example: if process() calls helper() which is slow:
# - process() tottime might be 0.01s (fast itself)
# - process() cumtime might be 5.00s (because helper is slow)
# → sort by tottime to find functions doing real CPU work
# → sort by cumtime to find the root of slow call trees
```

**Why:** `tottime` pinpoints the actual hotspot. `cumtime` identifies which high-level function is responsible for slowness, even if it delegates to many helpers.
</details>

---

### Q3 · Sort pstats by cumtime, Show Top 5 🟡

Profile a function using `cProfile.Profile()` (not `cProfile.run()`). Capture the output to a string using `io.StringIO`. Sort by `cumtime` and show only the top 5 functions.

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Use `pstats.Stats(profiler, stream=buffer)`. Chain `.strip_dirs().sort_stats().print_stats(5)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import cProfile, pstats, io

def target():
    return sum(i * i for i in range(50_000))

profiler = cProfile.Profile()
profiler.enable()
target()
profiler.disable()

buf = io.StringIO()
stats = pstats.Stats(profiler, stream=buf)
stats.strip_dirs()
stats.sort_stats("cumtime")
stats.print_stats(5)
print(buf.getvalue())
```

**Why:** Capturing to `io.StringIO` lets you process or store the profile output programmatically rather than printing directly to stdout.
</details>

---

### Q4 · timeit: Benchmark List Comprehension vs for Loop 🟡

Use `timeit.repeat()` to compare building a list of squares two ways: list comprehension vs manual for loop appending. Use `repeat=5, number=10_000`. Report the best time for each.

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Use `min()` on the result of `timeit.repeat()`. Express the result per call in microseconds.
</details>

<details>
<summary>✅ Answer</summary>

```python
import timeit

lc = min(timeit.repeat(
    "[x*x for x in range(1000)]",
    repeat=5, number=10_000,
))
loop = min(timeit.repeat(
    "r=[]\nfor x in range(1000): r.append(x*x)",
    repeat=5, number=10_000,
))
print(f"List comp: {lc/10_000*1e6:.2f} µs/call")
print(f"For loop:  {loop/10_000*1e6:.2f} µs/call")
```

**Why:** List comprehensions are consistently faster because they avoid the overhead of repeated `list.append` attribute lookup and Python bytecode dispatch per iteration.
</details>

---

### Q5 · timeit: Use setup Param to Import Before Timing 🟡

Benchmark `json.dumps({"key": "value"})` using `timeit.timeit()`. The `import json` must go in the `setup` parameter, not in the `stmt`. Explain why.

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

<details>
<summary>💡 Hint</summary>
The `setup` runs once before all iterations. The `stmt` runs `number` times. If import is in `stmt`, you time the import, not the operation.
</details>

<details>
<summary>✅ Answer</summary>

```python
import timeit

t = timeit.timeit(
    stmt='json.dumps({"key": "value"})',
    setup="import json",          # ← runs once, not timed
    number=100_000,
)
print(f"{t / 100_000 * 1e6:.2f} µs per call")
```

**Why:** `setup` runs exactly once before the timing loop begins. Placing imports in `stmt` would measure import overhead (which is cached after the first call anyway, producing misleading numbers).
</details>

---

### Q6 · timeit: Why Use min() Not mean() 🟡

You run `timeit.repeat("sum(range(1000))", repeat=7, number=10_000)` and get results: `[0.21, 0.22, 0.31, 0.20, 0.22, 0.45, 0.21]`. Which value do you report, and why is the 0.45 not representative?

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

<details>
<summary>💡 Hint</summary>
What could cause one run to be more than twice as slow as the others?
</details>

<details>
<summary>✅ Answer</summary>

```python
import timeit

results = timeit.repeat(
    "sum(range(1000))",
    repeat=7,
    number=10_000,
)
# Report the minimum:
best = min(results)
# [0.21, 0.22, 0.31, 0.20, 0.22, 0.45, 0.21] → best = 0.20

# The 0.45 was caused by: OS process scheduling interrupt,
# garbage collection pause, or another process stealing CPU.
# These are noise — the minimum represents best available CPU time.
print(f"Best: {best:.3f}s = {best/10_000*1e6:.2f} µs/call")
```

**Why:** Higher values represent interference from the OS, GC, or background processes — not the true speed of the code. The minimum is the cleanest signal.
</details>

---

### Q7 · @profile with line_profiler 🟡

Write a function `process(data)` that filters even numbers and squares them. Add the `@profile` decorator for `line_profiler`. Show the command to run it with `kernprof` and explain what the output columns mean.

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`kernprof` injects the `@profile` decorator at runtime. You do not import it.
</details>

<details>
<summary>✅ Answer</summary>

```python
# In process_q7.py:
@profile   # ← kernprof injects this — no import needed
def process(data):
    evens = [x for x in data if x % 2 == 0]
    squares = [x * x for x in evens]
    return squares

if __name__ == "__main__":
    process(list(range(100_000)))
```

```
# Run:
kernprof -l -v process_q7.py
```

Output columns:
- `Line #` — line number in source
- `Hits` — how many times the line executed
- `Time` — total time on that line
- `% Time` — percentage of function time on that line
- `Line Contents` — the actual code

**Why:** line_profiler identifies which specific line inside a function is the bottleneck — cProfile only tells you the function, not the line.
</details>

---

### Q8 · memory_profiler: Trace Peak Memory of a Function 🟡

Write a function that builds a large list of floats, then sorts it. Decorate it with `@profile` from `memory_profiler`. Show how to run it and what the output tells you.

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Import `from memory_profiler import profile` (this time you DO import it, unlike line_profiler).
</details>

<details>
<summary>✅ Answer</summary>

```python
from memory_profiler import profile

@profile
def build_and_sort():
    data = [float(i) for i in range(500_000)]  # large allocation
    data.sort()
    return data

if __name__ == "__main__":
    build_and_sort()
```

```
python -m memory_profiler memory_q8.py
```

Output columns:
- `Mem usage` — current RSS memory in MiB at that line
- `Increment` — memory change from previous line (+ = allocated, - = freed)

**Why:** `Increment` shows you exactly which line causes a large allocation, so you know where to apply generators or chunked processing.
</details>

---

### Q9 · Context Manager That Profiles Any Block 🟠

Write a context manager `profile_block(label)` using `@contextmanager` that profiles any code block inside a `with` statement. It should print the top 5 functions sorted by `tottime` when the block exits.

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Use `cProfile.Profile()` with `.enable()` in the `try` and `.disable()` in the `finally`. Use `contextlib.contextmanager`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import cProfile, pstats, io
from contextlib import contextmanager

@contextmanager
def profile_block(label, top_n=5, sort_by="tottime"):
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        yield
    finally:
        profiler.disable()
        buf = io.StringIO()
        pstats.Stats(profiler, stream=buf).strip_dirs()\
              .sort_stats(sort_by).print_stats(top_n)
        print(f"--- Profile: {label} ---")
        print(buf.getvalue())

# Usage:
with profile_block("my operation"):
    result = sum(i * i for i in range(100_000))
```

**Why:** The context manager pattern is useful in production code to profile specific code sections without restructuring the code into separate functions.
</details>

---

### Q10 · Interpret a snakeviz Flamegraph 🟠

A snakeviz icicle chart shows: the top-level call `main()` takes 8.2s total. Inside it, `load_data()` occupies 70% of the width. Inside `load_data()`, `json.loads()` takes 60% of its width. Where is the real bottleneck and what would you investigate?

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Width = cumulative time. Follow the widest box down the call tree to find the leaf that is actually slow.
</details>

<details>
<summary>✅ Answer</summary>

```python
# Analysis (no code needed for this question):
# - main() takes 8.2s total
# - load_data() = 70% of 8.2s = ~5.7s (this is the root of slowness)
# - json.loads() = 60% of load_data() = ~3.4s (actual bottleneck)

# What to investigate:
# 1. Why is json.loads() being called so much?
#    → Check ncalls: is it being called in a loop?
# 2. Is the JSON payload large?
#    → Could switch to orjson (C-based, 3–5x faster) or msgpack
# 3. Is load_data() called repeatedly with the same data?
#    → Add @lru_cache or a pre-load step

# The flamegraph told us: json parsing inside load_data is the hotspot.
# Not main(). Not anything else.
```

**Why:** Always follow the widest boxes downward in the icicle chart. The deepest wide box is the real consumer of time — everything above it is just the call path.
</details>

---

### Q11 · Use tracemalloc to Find a Memory Leak 🟡

You suspect a function `accumulate(data)` is leaking memory. Use `tracemalloc` to take a snapshot before and after 10 calls, then print the top 3 lines by memory growth.

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Use `tracemalloc.start()`, take two snapshots with `take_snapshot()`, then use `snap2.compare_to(snap1, "lineno")`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import tracemalloc

_cache = []   # simulated leak: list grows and is never cleared

def accumulate(data):
    _cache.extend(data)   # ← leak: always grows, never freed
    return sum(data)

tracemalloc.start()
snap1 = tracemalloc.take_snapshot()

for i in range(10):
    accumulate(list(range(10_000)))

snap2 = tracemalloc.take_snapshot()
tracemalloc.stop()

top_diff = snap2.compare_to(snap1, "lineno")
for stat in top_diff[:3]:
    print(stat)   # shows file, line, size growth, count growth
```

**Why:** `compare_to()` shows the delta between snapshots, isolating lines that allocated memory and never freed it — exactly the signature of a memory leak.
</details>

---

### Q12 · Decorator That Logs Timing and Memory 🟠

Write a decorator `@timed_and_traced` that wraps any function and prints: elapsed wall time in ms, and peak memory increment during the call in KiB. Use `time.perf_counter` for timing and `tracemalloc` for memory.

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Use `tracemalloc.start()`, call the function, use `tracemalloc.get_traced_memory()` which returns `(current, peak)`, then `tracemalloc.stop()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time, tracemalloc, functools

def timed_and_traced(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        t0 = time.perf_counter()

        result = func(*args, **kwargs)

        elapsed_ms = (time.perf_counter() - t0) * 1000
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"{func.__name__}: {elapsed_ms:.2f} ms | "
              f"peak memory: {peak_bytes / 1024:.1f} KiB")
        return result
    return wrapper

@timed_and_traced
def build_list(n):
    return [i * i for i in range(n)]

build_list(100_000)
```

**Why:** Combining timing and memory measurement in one decorator gives a complete performance snapshot for any function without modifying its code or running a separate profiler tool.
</details>

---

## 📂 Navigation

| | |
|---|---|
| ⬆️ Root Theory | [../theory.md](../theory.md) |
| 📖 Profiling Tools Theory | [theory.md](./theory.md) |
| ⚡ Optimization Patterns | [../02_optimization_patterns/practice.md](../02_optimization_patterns/practice.md) |

---

**[🏠 Back to README](../../README.md)**

**Prev:** [← Profiling Tools Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Optimization Patterns Practice →](../02_optimization_patterns/practice.md)
