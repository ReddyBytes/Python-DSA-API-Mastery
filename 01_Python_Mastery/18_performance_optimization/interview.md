# 🎯 Performance Optimization — Interview Preparation Guide  
From Profiling to Scalability Decisions

---

# 🧠 What Interviewers Actually Test

Performance questions evaluate:

- Analytical thinking
- Profiling discipline
- Bottleneck identification
- Trade-off awareness
- System scalability understanding
- Real-world debugging experience

They are testing engineering maturity.

---

# 🔹 Level 1: 0–2 Years Experience

Basic understanding expected.

---

**Q1: What is performance optimization?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> Performance optimization is the process of improving the speed, efficiency, or memory usage of a program while maintaining correctness.

</details>

<br>

**Q2: What is time complexity?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> Time complexity measures how runtime grows relative to input size.

Example:
O(n), O(n²), O(log n)

Important:
Algorithm choice matters more than micro-optimizations.

</details>

<br>

**Q3: What is space complexity?**

<details>
<summary>💡 Show Answer</summary>

Space complexity measures how memory usage grows with input size.

Example:
Using list vs generator affects space complexity.

</details>

<br>

**Q4: What is profiling?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> Profiling is the process of measuring where a program spends time or memory to identify bottlenecks before optimizing.

Key phrase:
Measure before optimize.

</details>


# 🔹 Level 2: 2–5 Years Experience

Now interviewer expects:

- Tool awareness
- Practical optimization thinking
- CPU vs memory clarity
- Built-in usage reasoning

---

**Q5: What tools do you use for profiling?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

- timeit → micro benchmarking
- cProfile → function-level profiling
- line_profiler → line-level profiling
- tracemalloc → memory profiling

Mention specific use case for each.

</details>

<br>

**Q6: How do you identify a bottleneck?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

1. Run profiler.
2. Analyze cumulative time.
3. Identify heavy functions.
4. Optimize high-impact areas first.

Focus on:
Highest cumulative time.

</details>

<br>

**Q7: Why are built-in functions faster?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> Built-in functions are implemented in C, which runs faster than Python-level loops.

Example:
sum(), min(), max() are faster than manual loops.

</details>

<br>

**Q8: When would you use caching?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> I use caching when a function is expensive and called repeatedly with the same inputs. I typically use functools.lru_cache or external caching layers like Redis.

Mention memory trade-off.

</details>

<br>

**Q9: What is premature optimization?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> Premature optimization is optimizing code before identifying real performance issues, often leading to unnecessary complexity without measurable benefit.

Classic engineering wisdom.

</details>


# 🔹 Level 3: 5–10 Years Experience

Now discussion moves to system-level thinking.

---

**Q10: How do you optimize a slow API endpoint?**

<details>
<summary>💡 Show Answer</summary>

Strong structured answer:

1. Measure response time.
2. Profile backend code.
3. Analyze DB queries.
4. Check network latency.
5. Add caching if needed.
6. Consider async or concurrency.
7. Optimize algorithm if required.

System-level thinking matters.

</details>

<br>

**Q11: How do you decide between optimizing code and scaling infrastructure?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> If profiling shows algorithm inefficiency, I optimize code. If performance is acceptable but load is high, horizontal scaling or load balancing may be appropriate.

Engineering trade-off mindset.

</details>

<br>

**Q12: CPU-bound vs I/O-bound optimization strategy?**

<details>
<summary>💡 Show Answer</summary>

CPU-bound:
Use multiprocessing or optimize algorithm.

I/O-bound:
Use async or threading.

Clear classification required.

</details>

<br>

**Q13: How do you optimize memory-heavy data processing?**

<details>
<summary>💡 Show Answer</summary>

Possible approaches:

- Use [generators](../11_generators_iterators/theory.md#why-generators-are-lazy--the-memory-story) instead of lists
- Process data in chunks
- Use streaming
- Use [`__slots__`](../05_oops/15_slots.md) in classes
- Clear unused references
- Avoid storing unnecessary data

Structured answer shows experience.

</details>

<br>

**Q14: How do you optimize database-heavy applications?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

- Add indexes
- Optimize queries
- Use connection pooling
- Cache frequent results
- Avoid N+1 queries

Not all performance issues are Python-level.

</details>

<br>

**Q15: When would you use C extensions or external libraries?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> When Python-level optimization is insufficient and heavy computation is required, I use optimized libraries like NumPy or write performance-critical parts in C/Cython.

Shows practical awareness.

</details>


**Q16: How do you use `cache_info()` with `lru_cache`?**

<details>
<summary>💡 Show Answer</summary>

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fib(n):
    if n < 2: return n
    return fib(n-1) + fib(n-2)

fib(30)
print(fib.cache_info())
# CacheInfo(hits=28, misses=31, maxsize=128, currsize=31)
```

> `hits` = returned from cache. `misses` = actually computed.
> High hits/misses ratio = cache working well.
> Use `cache_clear()` in tests to avoid state leaking between test runs.

</details>

<br>

**Q17: What memory benefit does `__slots__` provide?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> A normal Python instance stores attributes in a `__dict__` (a hash map) that costs ~200–400 bytes per object regardless of how many attributes you have. `__slots__` replaces this with fixed C-level memory slots — like a C struct — saving 40–60% memory per instance. At a million objects, this can mean hundreds of MB saved.

Only use `__slots__` when creating thousands+ of small fixed-attribute objects. Avoid if you need dynamic attribute assignment or complex inheritance.

</details>

<br>

**Q18: How do you use `tracemalloc` to detect a memory leak?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

```python
import tracemalloc

tracemalloc.start()
snap1 = tracemalloc.take_snapshot()

run_suspicious_code()   # call the code multiple times

snap2 = tracemalloc.take_snapshot()
tracemalloc.stop()

top = snap2.compare_to(snap1, "lineno")
for stat in top[:5]:
    print(stat)   # shows file:line and how much memory grew
```

> Take a snapshot before and after. `compare_to()` shows which lines allocated memory that was not freed — the signature of a leak.

</details>

<br>

**Q19: What does snakeviz show and how do you read a flamegraph?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> snakeviz reads a `.prof` file saved by `cProfile.run("...", "output.prof")` and renders an interactive icicle chart. Each box represents a function call. **Width equals cumulative time** — wider boxes are slower. Inner boxes are functions called from the outer function. To find the real bottleneck: follow the widest box downward until you reach a leaf. That leaf is where CPU time is actually spent.

</details>

<br>

**Q20: Why should timeit benchmarks use `min()` instead of `mean()`?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> `timeit.repeat()` returns multiple timing measurements. The minimum represents the best-case CPU availability for your code — uninterrupted by OS scheduling, garbage collection, or background processes. Higher measurements are caused by those external events, which are noise, not your code's true performance. Using `mean()` includes this noise and makes code appear slower than it is.

```python
results = timeit.repeat("sum(range(1000))", repeat=7, number=10_000)
best = min(results)   # ← always use min
```

</details>

<br>

# 🔥 Scenario-Based Questions

---

## Scenario 1:

Your function runs in O(n²). How do you improve it?

<details>
<summary>💡 Show Answer</summary>

Answer:

- Analyze algorithm
- Use better data structure
- Reduce nested loops
- Possibly use hashing
- Consider divide-and-conquer

Algorithmic improvement > micro-optimization.

</details>
---

## Scenario 2:

Memory usage keeps increasing during batch processing.

<details>
<summary>💡 Show Answer</summary>

Possible causes:

- Large list accumulation
- Unreleased references
- Circular references
- Improper caching

Solution:

- Stream processing
- Profile memory
- Clear references

</details>
---

## Scenario 3:

API latency spikes under high traffic.

<details>
<summary>💡 Show Answer</summary>

Possible causes:

- Blocking calls
- DB bottleneck
- Missing caching
- Insufficient worker processes

Solution:
Analyze full request lifecycle.

</details>
---

## Scenario 4:

Async application still slow.

<details>
<summary>💡 Show Answer</summary>

Possible cause:

Blocking synchronous call inside async function.

Solution:
Move to thread pool or process pool.

</details>
---

## Scenario 5:

After optimization, code becomes unreadable.

<details>
<summary>💡 Show Answer</summary>

What do you do?

Strong answer:

> I balance performance and readability. If performance gain is minimal but complexity increases significantly, I prefer clean maintainable code.

Engineering maturity.

</details>
---

# 🧠 How to Answer Like a Strong Candidate

Weak:

“I try to make code faster.”

Strong:

> “I always profile before optimizing. I focus on high-impact bottlenecks, usually at the algorithm or I/O layer. I consider trade-offs between CPU, memory, and maintainability before implementing optimizations.”

Structured.
Calm.
Professional.

---

# ⚠️ Common Weak Candidate Mistakes

- Optimizing without measuring
- Ignoring algorithm complexity
- Micro-optimizing trivial code
- Overusing caching
- Ignoring memory trade-offs
- Not considering scalability

---

# 🎯 Rapid-Fire Revision

- Measure before optimizing
- Use cProfile for bottlenecks
- Use timeit for micro benchmarks
- Built-ins are faster
- Algorithm complexity matters most
- Cache wisely
- Avoid premature optimization
- Balance readability and speed
- CPU-bound vs I/O-bound decisions matter

---

# 🏆 Final Interview Mindset

Performance questions evaluate:

- Analytical discipline
- Structured debugging
- Trade-off awareness
- Scalability thinking
- Calm decision-making

If you demonstrate:

- Profiling-first mindset
- Algorithmic reasoning
- CPU vs memory trade-offs
- Practical system examples
- Balanced engineering thinking

You appear as senior engineer.

Performance engineering is about smart decisions.

Not speed at any cost.

---

# 🔁 Navigation

Previous:  
[18_performance_optimization/theory.md](./theory.md)

Next:  
[19_production_best_practices/theory.md](../19_production_best_practices/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Production Best Practices — Coding Standards →](../19_production_best_practices/coding_standards.md)

**Related Topics:** [Theory](./theory.md) · [Practice](./practice.md) · [Cheatsheet](./cheetsheet.md)
