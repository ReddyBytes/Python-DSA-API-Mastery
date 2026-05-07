# 🔍 Profiling Tools

Before a doctor prescribes medicine, they check your vitals. Before you optimize code, you profile it — measure exactly where time is actually going, not where you guess it is.

---

## 📌 Learning Priority

**Must Learn**: `cProfile`, `timeit.timeit`, `pstats` sorting by cumtime/tottime
**Should Learn**: `line_profiler` (`@profile`), `memory_profiler`, `snakeviz`
**Good to Know**: `py-spy`, `time.perf_counter_ns`, `tracemalloc`
**Reference**: `yappi`, `pyflame`, Austin

---

## 1. Why Measure First

> Guessing what is slow is like fixing a car blindfolded — you will almost certainly touch the wrong part.

The classic trap is **premature optimization**: spending hours speeding up code that runs 0.1% of the time while the real bottleneck sits elsewhere untouched.

The workflow that actually works:

```
Profile → Identify real hotspot → Fix it → Profile again → Confirm speedup
```

Never skip the first step. Never skip the last step.

> 📝 Practice: [practice.md → Q1](./practice.md#q1--run-cprofile-on-a-function-)

---

## 2. cProfile — Function-Level Profiling

> Think of cProfile as a time-tracking app that logs every function call your program makes, noting how long each one took.

**cProfile** is Python's built-in deterministic profiler. It hooks into every function call and return, recording timing for every function in the program.

```python
import cProfile

def slow_work():
    return sum(i * i for i in range(100_000))

cProfile.run("slow_work()")  # ← prints profile table to stdout
```

### Reading pstats Output

| Column | Meaning |
|--------|---------|
| `ncalls` | How many times the function was called |
| `tottime` | Time spent **inside** this function (excludes subcalls) |
| `cumtime` | **Total** time: this function + everything it called |
| `percall` | tottime / ncalls (or cumtime / ncalls) |

**Rule**: sort by `tottime` to find pure CPU hotspots. Sort by `cumtime` to find expensive call trees.

```python
import cProfile, pstats, io

profiler = cProfile.Profile()
profiler.enable()
slow_work()
profiler.disable()

stream = io.StringIO()
stats = pstats.Stats(profiler, stream=stream)
stats.strip_dirs()           # ← removes long path prefixes
stats.sort_stats("cumtime")  # ← sort by cumulative time
stats.print_stats(10)        # ← show top 10 functions
print(stream.getvalue())
```

> 📝 Practice: [practice.md → Q2](./practice.md#q2--read-pstats-output-tottime-vs-cumtime-)

---

## 3. timeit — Micro-Benchmarks

> timeit is like running a race 1000 times and taking the fastest lap — one bad run (from a background process) doesn't ruin your measurement.

**timeit** measures small code snippets by running them many times. It eliminates startup noise and GC interruptions.

```python
import timeit

# Basic: total time for 10,000 runs
t = timeit.timeit("sum(range(1000))", number=10_000)
print(f"{t / 10_000 * 1e6:.2f} µs per call")

# With setup (setup is NOT timed)
t = timeit.timeit(
    stmt="42 in data",
    setup="data = list(range(10_000))",
    number=100_000,
)
```

### Why use `min()` not `mean()`

```python
measurements = timeit.repeat(
    "'-'.join(str(i) for i in range(100))",
    repeat=5,
    number=10_000,
)
best = min(measurements)  # ← use min, not mean
```

The minimum reflects the best available CPU time. Higher runs are caused by OS interrupts and GC pauses — they are noise, not signal.

> 📝 Practice: [practice.md → Q4](./practice.md#q4--timeit-list-comprehension-vs-for-loop-)

---

## 4. line_profiler — Line-by-Line Profiling

> cProfile tells you WHICH function is slow. line_profiler tells you WHICH LINE inside that function.

**line_profiler** is an external tool that decorates individual functions and times each line.

Install: `pip install line-profiler`

```python
# In a .py file — decorate the function you want to inspect
@profile  # ← added by kernprof at runtime, not imported
def process(data):
    result = []
    for item in data:           # line 1
        result.append(item * 2) # line 2 — is this the bottleneck?
    return sorted(result)       # line 3
```

Run with:
```
kernprof -l -v my_script.py
```

Output shows `% Time` per line — immediately shows which line eats the most time inside the function.

> 📝 Practice: [practice.md → Q7](./practice.md#q7--profile-decorator-with-line_profiler-)

---

## 5. memory_profiler — Memory Usage Per Line

> If cProfile is a stopwatch, memory_profiler is a scale — it weighs your program's memory at each line.

**memory_profiler** tracks RAM allocation line by line inside decorated functions.

Install: `pip install memory-profiler`

```python
from memory_profiler import profile

@profile
def load_data():
    data = [i for i in range(1_000_000)]  # ← how much memory does this use?
    return data
```

Run with:
```
python -m memory_profiler my_script.py
```

Output shows `Mem usage` and `Increment` per line in MiB.

For sustained memory tracking across a process, use `mprof`:
```
mprof run my_script.py
mprof plot
```

> 📝 Practice: [practice.md → Q8](./practice.md#q8--memory_profiler-trace-peak-memory-)

---

## 6. snakeviz — Visualizing Profiles

> A raw pstats table is like reading a phone book. snakeviz turns it into a map.

**snakeviz** reads a `.prof` file saved by cProfile and renders it as an interactive **icicle chart** (flamegraph style).

```python
# Step 1: save profile to file
import cProfile
cProfile.run("my_function()", "output.prof")
```

```
# Step 2: open in browser
pip install snakeviz
snakeviz output.prof
```

Reading the chart:
- Each box is a function call
- Width = cumulative time (wider = slower)
- Inner boxes = functions called from the outer function
- Click a box to zoom in on that subtree

Focus on wide boxes near the top — those are the expensive call trees.

> 📝 Practice: [practice.md → Q10](./practice.md#q10--interpret-a-snakeviz-flamegraph-)

---

## 7. tracemalloc — Finding Memory Leaks

> tracemalloc takes two memory snapshots and shows you exactly which lines of code allocated the most memory between them.

**tracemalloc** is built into Python's standard library (no install needed).

```python
import tracemalloc

tracemalloc.start()
# ... code to inspect ...
snapshot = tracemalloc.take_snapshot()
tracemalloc.stop()

top_stats = snapshot.statistics("lineno")
for stat in top_stats[:5]:
    print(stat)  # file:line: size_KB KiB (count allocations)
```

Compare two snapshots to find a leak:

```python
tracemalloc.start()
snap1 = tracemalloc.take_snapshot()
run_suspicious_code()
snap2 = tracemalloc.take_snapshot()
tracemalloc.stop()

top_diff = snap2.compare_to(snap1, "lineno")
for stat in top_diff[:5]:
    print(stat)  # shows what grew between snap1 and snap2
```

> 📝 Practice: [practice.md → Q11](./practice.md#q11--tracemalloc-to-find-memory-leak-)

---

## 8. Common Profiling Mistakes

**Do not benchmark inside loops** — the first run is always slower (Python compilation, cache misses). Use `timeit.repeat` and take `min()`.

**Do not trust the mean** — a single GC pause can skew the average. Mean is misleading for micro-benchmarks.

**Use best-of-N** — `min(timeit.repeat(stmt, repeat=5, number=1000))` gives the cleanest signal.

**Benchmark on target hardware** — a laptop benchmark does not predict production server behavior. Run on hardware that matches prod.

**Profile the real workload** — synthetic data can hide the real bottleneck. Use representative inputs.

> 📝 Practice: [practice.md → Q12](./practice.md#q12--decorator-that-logs-timing-and-memory-)

---

## 📂 Navigation

| | |
|---|---|
| ⬆️ Root Theory | [../theory.md](../theory.md) |
| 💻 Practice | [practice.md](./practice.md) |
| ⚡ Optimization Patterns | [../02_optimization_patterns/theory.md](../02_optimization_patterns/theory.md) |

---

**[🏠 Back to README](../../README.md)**

**Prev:** [← Root Theory](../theory.md) &nbsp;|&nbsp; **Next:** [Optimization Patterns →](../02_optimization_patterns/theory.md)

**Related Topics:** [Root Theory](../theory.md) · [Optimization Patterns](../02_optimization_patterns/theory.md) · [Cheatsheet](../cheetsheet.md)
