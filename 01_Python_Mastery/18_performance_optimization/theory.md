# 🚀 Performance Optimization in Python  

From Profiling to Scalable Systems

> 📝 **Practice:** [Q74 · performance-bug](../python_practice_questions_100.md#q74--debug--performance-bug)

---

# 🎯 Why Performance Optimization Matters

Imagine:

Your API takes 200ms.
Users are happy.

After new feature:
It takes 3 seconds.

Now:

- Users complain
- CPU usage spikes
- Server cost increases
- Scaling becomes expensive

Performance matters in:

- APIs
- Data pipelines
- ML systems
- High-traffic systems
- Real-time systems

But remember:

> Premature optimization is the root of all evil.

Measure first.
Then optimize.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`cProfile` / `profile` · `timeit` · Algorithmic complexity (choose right data structure) · Generator vs list tradeoff

**Should Learn** — Important for real projects, comes up regularly:
`memory_profiler` · `tracemalloc` · `__slots__` · `functools.lru_cache` / `cache` · `dis` module (bytecode inspection)

**Good to Know** — Useful in specific situations:
`py-spy` sampling profiler · Flamegraph interpretation · `scalene` · Numba JIT basics

**Reference** — Know it exists, look up when needed:
NUMA awareness · SIMD vectorization · `numexpr` · Escape analysis

---

# 🧠 1️⃣ First Rule: Measure Before Optimizing

Never guess performance issues.

Use tools.

Optimization without profiling leads to:

- Wasted time
- Wrong assumptions
- Complex code without benefit

> 📝 **Practice:** [practice.md → Q1 cProfile basics](./practice.md#q1--cprofile-basics-)

---

# 🧪 2️⃣ timeit Module

Used to measure small code snippets.

Example:

```python
import timeit

timeit.timeit("sum(range(1000))", number=1000)
```

Measures execution time.

Useful for:

- Comparing small implementations
- Micro-optimizations

---

## 🔹 Why timeit Is Reliable

- Runs multiple iterations
- Reduces noise
- Isolates execution

Always use `min()` from `timeit.repeat()`, not the mean. The minimum reflects best available CPU time; higher values are OS noise and GC pauses.

> 📝 **Practice:** [practice.md → Q5 timeit repeat](./practice.md#q5--timeit-repeat-and-min-)

---

# 🔍 3️⃣ cProfile — Function-Level Profiling

Used to analyze entire program.

Example:

```python
import cProfile
cProfile.run("my_function()")
```

Shows:

- Function call count
- Time spent in each function
- Cumulative time

Helps identify bottlenecks.

> 📝 **Practice:** [Q72 · profiling](../python_practice_questions_100.md#q72--normal--profiling)

> 📝 **Practice:** [practice.md → Q2 pstats output](./practice.md#q2--read-pstats-output-)

---

# 📊 4️⃣ Understanding Profiling Output

Important metrics:

- ncalls → number of calls
- tottime → time spent inside function (excluding subcalls)
- cumtime → total time including subcalls

Focus on:

High cumulative time functions.

> 📝 **Practice:** [practice.md → Q3 pstats sorting](./practice.md#q3--sort-pstats-output-)

---

# 🧠 5️⃣ Line-by-Line Profiling

Use:

- line_profiler (external tool)

Helps find exact slow lines.

Useful for:

Heavy loops
Data processing

> 📝 **Practice:** [practice.md → Q7 line_profiler](./practice.md#q7--line_profiler-)

---

# 🧠 6️⃣ Memory Profiling

Performance is not only CPU.

Memory matters.

Use:

- tracemalloc
- memory_profiler

Helps detect:

- Large object allocations
- Memory leaks
- Inefficient structures

`tracemalloc` takes before/after snapshots and shows which lines caused the most memory growth — the essential tool for finding memory leaks.

> 📝 **Practice:** [practice.md → Q9 tracemalloc](./practice.md#q9--tracemalloc-)

---

# ⚡ 7️⃣ Algorithm Optimization

Before optimizing code:

Check algorithm complexity.

Example:

O(n²) vs O(n log n)

Algorithm choice often gives biggest performance improvement.

> 📝 **Practice:** [practice.md → Q15 dict vs list lookup](./practice.md#q15--dict-vs-list-lookup-)

---

# 🧠 8️⃣ Common Optimization Techniques

---

## 🔹 Use Built-in Functions

Built-ins are written in C.
Faster than Python loops.

Example:

```python
sum(list)
```

Instead of manual loop.

---

## 🔹 Use List Comprehensions

Faster than traditional loops.

---

## 🔹 Use [Generator Expressions](../11_generators_iterators/theory.md)

Reduce memory usage.

> 📝 **Practice:** [practice.md → Q16 generator expressions](./practice.md#q16--generator-expressions-)

---

## 🔹 Avoid Repeated Computation

Cache results if reused.

Use:

- [functools.lru_cache](../04_functions/theory.md#functoolslru_cache--memoization-made-easy)

Example:

```python
from functools import lru_cache

@lru_cache
def compute(x):
    ...
```

`cache_info()` shows hits, misses, and current cache size — useful to verify the cache is working.

> 📝 **Practice:** [practice.md → Q21 lru_cache](./practice.md#q21--lru_cache-)

---

# 🧠 9️⃣ CPU vs Memory Trade-off

Sometimes:

Using more memory reduces CPU time.

Example:

Caching results.

Trade-off decision required.

Engineering is about balance.

---

# 🧠 🔟 Avoid Premature Optimization

Optimize when:

- You have measurable bottleneck
- Performance is business-critical
- Scalability required

Do not optimize:

- Early prototypes
- Small scripts
- Unmeasured assumptions

---

# ⚙️ 1️⃣1️⃣ Concurrency for Performance

For I/O-bound:

Use async or threading.

For CPU-bound:

Use multiprocessing.

Optimization sometimes requires architecture change.

> 📝 **Practice:** [practice.md → Q26 run_in_executor](./practice.md#q26--run_in_executor-)

---

# 🧠 1️⃣2️⃣ Efficient Data Structures

Choosing right data structure improves performance.

Examples:

- Use set for membership check (O(1))
- Use dict for fast lookups
- Use deque for fast queue operations

Algorithm + Data structure = Performance.

---

# 🧠 1️⃣3️⃣ Avoid Global Lookups in Loops

Example:

Instead of:

```python
for i in range(1000000):
    math.sqrt(i)
```

Store locally:

```python
sqrt = math.sqrt
for i in range(1000000):
    sqrt(i)
```

Reduces lookup overhead.

Micro-optimization.

> 📝 **Practice:** [practice.md → Q20 local variable fast path](./practice.md#q20--local-variable-fast-path-)

---

# 🧠 1️⃣4️⃣ Using C Extensions or Cython

For extreme performance:

- Use C libraries
- Use NumPy
- Use Cython
- Use PyPy

When Python alone is not enough.

> 📝 **Practice:** [practice.md → Q27 numpy vectorization](./practice.md#q27--numpy-vectorization-)

---

# 🏗 1️⃣5️⃣ Real Production Scenarios

> 📝 **Practice:** [Q87 · caching-scenario](../python_practice_questions_100.md#q87--design--caching-scenario)

---

## 🔹 Slow API Response

Profile code.
Find slow DB call.
Optimize query.
Add caching.

---

## 🔹 Data Pipeline Too Slow

Check algorithm complexity.
Switch to generator.
Parallelize CPU tasks.

---

## 🔹 Memory Usage Too High

Replace lists with [generators](../11_generators_iterators/theory.md#why-generators-are-lazy--the-memory-story).
Use [`__slots__`](../05_oops/15_slots.md).
Clear unused references.

> 📝 **Practice:** [practice.md → Q22 __slots__ memory](./practice.md#q22--slots-memory-)

---

# ⚠️ 1️⃣6️⃣ Common Performance Mistakes

❌ Optimizing without profiling  
❌ Micro-optimizing trivial code  
❌ Ignoring algorithm complexity  
❌ Ignoring memory impact  
❌ Overusing caching  
❌ Blocking async event loop  

Optimization requires discipline.

---

# 🏆 1️⃣7️⃣ Engineering Maturity Levels

Beginner:
Writes working code.

Intermediate:
Uses built-ins and good structures.

Advanced:
Profiles before optimizing.

Senior:
Balances CPU, memory, scalability.

Architect:
Optimizes system architecture.

---

# 🧠 Final Mental Model

Performance optimization is:

Measure → Analyze → Optimize → Verify.

Focus on:

- Algorithm complexity
- Profiling data
- Real bottlenecks
- Clean architecture
- Scalability trade-offs

Fast code is good.
Correct and maintainable code is better.
Balanced code is best.

---

## 📝 Practice Questions

> 📝 **Practice:** [Q97 · design-decision-cache](../python_practice_questions_100.md#q97--design--design-decision-cache)

> 📝 **Practice:** [Q73 · complexity-in-practice](../python_practice_questions_100.md#q73--thinking--complexity-in-practice)

---

## 📂 Navigation

| | |
|---|---|
| 💻 Practice | [practice.md](./practice.md) |
| 🔍 Profiling Tools | [01_profiling_tools/theory.md](./01_profiling_tools/theory.md) |
| ⚡ Optimization | [02_optimization_patterns/theory.md](./02_optimization_patterns/theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🔥 Interview | [interview.md](./interview.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Testing — Interview Q&A](../17_testing/interview.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Interview Q&A](./interview.md) · [Profiling Tools](./01_profiling_tools/theory.md) · [Optimization Patterns](./02_optimization_patterns/theory.md)
