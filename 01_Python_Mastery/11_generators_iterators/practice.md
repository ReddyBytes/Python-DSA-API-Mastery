# 💻 Practice — 11_generators_iterators

> Master file — covers all 14 chapters.
> Reference files: [01_generators.py](./01_generators.py) · [02_iterators.py](./02_iterators.py) · [03_memory_comparison.py](./03_memory_comparison.py) · [Production Patterns](./04_generator_patterns.md)

---

## Quick Index

| # | Difficulty | Topic | Skill |
|---|---|---|---|
| Q1 | 🟢 Easy | Ch1 — Iteration Protocol | Implement `__iter__` and `__next__` on a Countdown class |
| Q2 | 🟡 Medium | Ch1 — StopIteration | When to raise StopIteration + example |
| Q3 | 🟡 Medium | Ch2 — Iterator Class | Write a NumberRange iterator (start, stop, step) |
| Q4 | 🟡 Medium | Ch2 — Iterable vs Iterator | Show lists are reusable, generators are exhausted |
| Q5 | 🟢 Easy | Ch3 — Generator Functions | Generator that yields squares of 1..n |
| Q6 | 🟡 Medium | Ch3 — Lazy Evaluation | Explain memory difference: list vs generator for 1M items |
| Q7 | 🟡 Medium | Ch4 — Frame Suspension | Trace exactly what Python does when it hits `yield` |
| Q8 | 🟡 Medium | Lazy Memory | Benchmark: sys.getsizeof() list vs generator |
| Q9 | 🟢 Easy | Ch5 — Generator Expressions | Rewrite list comprehension as gen expression |
| Q10 | 🟡 Medium | Ch6 — yield from | Flatten a nested list recursively with `yield from` |
| Q11 | 🟡 Medium | Ch6 — Delegation | Chain two generators with `yield from` instead of a loop |
| Q12 | 🟡 Medium | Ch7 — send() | Write a running_average() coroutine using send() |
| Q13 | 🟠 Hard | Ch7 — Priming | Explain why coroutines need next() before send() |
| Q14 | 🟡 Medium | Ch8 — Pipelines | Build a 3-stage pipeline: read_lines → parse_csv → filter_rows |
| Q15 | 🟠 Hard | Ch8 — Streaming ETL | Process a large file line-by-line, never fully in memory |
| Q16 | 🟢 Easy | Ch9 — itertools.chain | Combine two lists lazily with chain() |
| Q17 | 🟡 Medium | Ch9 — itertools.islice | Take first 10 items from an infinite generator |
| Q18 | 🟡 Medium | Ch9 — itertools.groupby | Group a sorted list of dicts by a key field |
| Q19 | 🟡 Medium | Ch10 — Infinite Sequences | Infinite fibonacci() + islice to take first 10 |
| Q20 | 🟡 Medium | Ch11 — return in generator | Show how `return value` becomes StopIteration.value |
| Q21 | 🟠 Hard | Ch12 — Async Generators | Async generator for paginated API results |
| Q22 | 🟡 Medium | Ch13 — Exhaustion | Demonstrate generator exhaustion iterating twice |
| Q23 | 🟡 Medium | Ch14 — collections.abc | Classify objects with isinstance(x, Iterator/Iterable) |
| Q24 | 🟠 Hard | Capstone — Production Pattern | paginated_api(url) generator with auto-fetch |
| Q25 | 🟠 Hard | Capstone — Full ETL | Streaming ETL pipeline: CSV → parse → filter → transform → write |

---

### Q1 🟢 · iteration protocol — Countdown Class

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

**Problem:** Implement a `Countdown` class that counts down from `n` to 0 (inclusive). It must implement `__iter__` and `__next__` so it works in a `for` loop and with `next()` directly.

<details>
<summary>💡 Hint</summary>

`__iter__` should return `self`. `__next__` should check if the current value is below 0 and raise `StopIteration` if so. Otherwise return current value and decrement.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Countdown:
    def __init__(self, n: int):
        self.current = n

    def __iter__(self):
        return self  # the object is its own iterator

    def __next__(self):
        if self.current < 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


# Usage:
for n in Countdown(5):
    print(n)   # 5 4 3 2 1 0

# Also works manually:
c = Countdown(3)
print(next(c))  # 3
print(next(c))  # 2
print(next(c))  # 1
print(next(c))  # 0
print(next(c))  # raises StopIteration
```

**Why:** Python's `for` loop calls `iter(obj)` to get an iterator, then calls `next()` repeatedly until `StopIteration` is raised. By implementing both dunder methods you plug directly into that protocol — no special registration needed.
</details>

---

### Q2 🟡 · StopIteration — When and How to Raise It

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

**Problem:** Explain in your own words: when should `__next__` raise `StopIteration`? Then write a `FiniteRange` class that counts from `start` to `stop` (exclusive) and raises `StopIteration` correctly when exhausted.

<details>
<summary>💡 Hint</summary>

`StopIteration` is the signal that there are no more items. It should be raised the first time `__next__` is called after the last valid item has been returned — never before. The `for` loop catches it automatically and exits cleanly.
</details>

<details>
<summary>✅ Answer</summary>

```python
class FiniteRange:
    """Counts from start to stop (exclusive), like range()."""

    def __init__(self, start: int, stop: int):
        self.current = start
        self.stop = stop

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.stop:
            raise StopIteration   # ← signal: no more items
        value = self.current
        self.current += 1
        return value


# Proof it works:
r = FiniteRange(0, 4)
print(list(r))   # [0, 1, 2, 3]

# Manual next() to see the boundary:
r2 = FiniteRange(0, 2)
print(next(r2))  # 0
print(next(r2))  # 1
try:
    print(next(r2))  # should raise
except StopIteration:
    print("Exhausted — StopIteration raised correctly")
```

**Why:** `StopIteration` is not an error — it is the agreed-upon handshake. When `__next__` raises it, the `for` loop (and `list()`, `sum()`, `zip()`, etc.) all treat it as a clean end. Raising it too early drops valid data; never raising it creates an infinite loop.
</details>

---

### Q3 🟡 · iterator class — NumberRange with step

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

**Problem:** Write a `NumberRange` iterator class that accepts `start`, `stop`, and `step` arguments and yields values just like `range(start, stop, step)`. It should work in a `for` loop.

<details>
<summary>💡 Hint</summary>

Handle the termination condition based on step direction: if `step > 0`, stop when `current >= stop`; if `step < 0`, stop when `current <= stop`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class NumberRange:
    def __init__(self, start: int, stop: int, step: int = 1):
        if step == 0:
            raise ValueError("step cannot be zero")
        self.current = start
        self.stop = stop
        self.step = step

    def __iter__(self):
        return self

    def __next__(self):
        # Determine exhaustion based on step direction
        if self.step > 0 and self.current >= self.stop:
            raise StopIteration
        if self.step < 0 and self.current <= self.stop:
            raise StopIteration
        value = self.current
        self.current += self.step
        return value


# Forward:
print(list(NumberRange(0, 10, 2)))    # [0, 2, 4, 6, 8]

# Backward:
print(list(NumberRange(10, 0, -3)))   # [10, 7, 4, 1]

# Matches built-in range:
print(list(range(0, 10, 2)))          # [0, 2, 4, 6, 8]
```

**Why:** A custom iterator with step logic shows you control exactly how `__next__` advances state. The built-in `range` works identically — this is how it thinks internally. Notice that `stop` is exclusive, matching Python convention.
</details>

---

### Q4 🟡 · iterable vs iterator — Reusable vs Exhausted

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

**Problem:** Demonstrate the difference between an iterable and an iterator. Specifically: show that a list can be iterated twice, but a generator is exhausted after one pass. Then show why this matters in practice.

<details>
<summary>💡 Hint</summary>

A list's `__iter__` creates a *new* iterator object each time. A generator's `__iter__` returns `self` — so `iter(gen) is gen` is True, and there is only one position pointer.
</details>

<details>
<summary>✅ Answer</summary>

```python
# --- ITERABLE: list ---
my_list = [1, 2, 3, 4, 5]

first_pass  = list(my_list)   # [1, 2, 3, 4, 5]
second_pass = list(my_list)   # [1, 2, 3, 4, 5]  ← works again!

# Each call to iter() creates a fresh list_iterator:
it1 = iter(my_list)
it2 = iter(my_list)
print(it1 is it2)   # False — two independent iterators

# --- ITERATOR: generator ---
gen = (x for x in range(1, 6))

first_pass  = list(gen)   # [1, 2, 3, 4, 5]
second_pass = list(gen)   # []  ← EMPTY! generator exhausted

# A generator's __iter__ returns itself — single position pointer:
print(gen is iter(gen))   # True

# --- Why it matters ---
def process_data(source):
    max_val = max(source)     # consumes all items
    min_val = min(source)     # source is exhausted — returns wrong result!
    return max_val, min_val

data_gen = (x for x in [3, 1, 4, 1, 5, 9, 2, 6])
print(process_data(data_gen))   # bug: min() sees empty sequence!

# Fix: convert to list first if multiple passes needed
data_list = list(x for x in [3, 1, 4, 1, 5, 9, 2, 6])
print(process_data(data_list))  # (9, 1) — correct
```

**Why:** Lists are **iterables** — they create a new iterator each time you call `iter()`. Generators are **iterators** — they ARE their own iterator, maintaining one internal position. This single-pass constraint is a fundamental property you must account for when passing generators to functions.
</details>

---

### Q5 🟢 · yield — Squares Generator

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

**Problem:** Write a generator function `squares(n)` that yields the square of each integer from 1 through n (inclusive). Use it with `for`, `list()`, and `sum()`.

<details>
<summary>💡 Hint</summary>

Any function containing `yield` becomes a generator function. Calling it returns a generator object — the body does not run until you iterate.
</details>

<details>
<summary>✅ Answer</summary>

```python
def squares(n: int):
    """Yield squares of 1, 2, ..., n."""
    for i in range(1, n + 1):
        yield i ** 2


# for loop:
for sq in squares(5):
    print(sq)   # 1 4 9 16 25

# list():
print(list(squares(5)))   # [1, 4, 9, 16, 25]

# sum() — never materializes the list:
print(sum(squares(100)))  # 338350

# Verify calling the function does NOT run the body:
gen = squares(3)
print(type(gen))          # <class 'generator'>
print(next(gen))          # 1  — body runs NOW, stops at first yield
print(next(gen))          # 4
print(next(gen))          # 9
# next(gen) here would raise StopIteration
```

**Why:** `yield` transforms a function into a lazy factory. The body is frozen at each `yield` and resumed on the next `next()` call. This is the most common generator pattern — cleaner than writing a class with `__iter__`/`__next__`.
</details>

---

### Q6 🟡 · lazy evaluation — Memory Numbers

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

**Problem:** Explain lazy evaluation using memory numbers. Then write code that proves a list comprehension uses ~8MB while a generator expression for 1 million items uses ~200 bytes.

<details>
<summary>💡 Hint</summary>

Use `sys.getsizeof()`. Remember: `getsizeof` on a list gives the container size but not the element objects themselves — use it to compare, not as an exact RAM count.
</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

# Eager: all 1 million integers computed and stored NOW
eager_list = [x for x in range(1_000_000)]
eager_size = sys.getsizeof(eager_list)
print(f"List size:      {eager_size:>12,} bytes  (~{eager_size // 1_048_576} MB)")

# Lazy: generator stores only its frame — no values computed yet
lazy_gen  = (x for x in range(1_000_000))
lazy_size = sys.getsizeof(lazy_gen)
print(f"Generator size: {lazy_size:>12,} bytes  (~{lazy_size} B)")

# Output (approximate):
# List size:       8,697,464 bytes  (~8 MB)
# Generator size:         112 bytes  (~112 B)

# The generator holds ONLY:
#   - a code pointer (where to resume)
#   - local variable state (current x)
# NOT the 1,000,000 computed values.

# Real-world impact:
def memory_safe_filter(filepath, keyword):
    """Process 10GB log file with ~1KB RAM."""
    with open(filepath) as f:
        matching = (line for line in f if keyword in line)
        for line in matching:
            process(line)   # one line at a time, never more

def memory_unsafe_filter(filepath, keyword):
    """Crashes on large files — loads everything into RAM first."""
    lines = [line for line in open(filepath)]   # 10GB in RAM!
    for line in lines:
        if keyword in line:
            process(line)
```

**Why:** A list stores every computed value. A generator stores only the suspended frame — roughly 112 bytes regardless of how many items it would produce. For 1M integers the ratio is 77,000:1. At 50M records it is the difference between a 4GB crash and a 4KB process.
</details>

---

### Q7 🟡 · frame suspension — Tracing yield

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

**Problem:** Write a generator function `tracer()` with print statements at each step. Run it step by step with explicit `next()` calls and explain exactly what Python saves/restores at each `yield`.

<details>
<summary>💡 Hint</summary>

Python saves the entire frame: code pointer (which line to resume at), all local variables, and the value stack. This frame is heap-allocated — it survives between `next()` calls.
</details>

<details>
<summary>✅ Answer</summary>

```python
def tracer():
    print("[tracer] Step 1: before first yield")
    x = 10
    result = yield "first"          # SUSPEND: frame saved with x=10, resume pointer=line 5
    print(f"[tracer] Step 2: resumed, x={x}, received={result}")
    x += 5
    yield "second"                  # SUSPEND: frame saved with x=15, resume pointer=line 8
    print(f"[tracer] Step 3: final, x={x}")
    # falls off end → StopIteration


g = tracer()

print("--- Calling next(g) #1 ---")
val = next(g)          # runs until first yield, suspends
print(f"Got: {val!r}")
# Output:
#   [tracer] Step 1: before first yield
#   Got: 'first'

print("--- Calling next(g) #2 ---")
val = next(g)          # resumes from line 5; send=None so result=None
print(f"Got: {val!r}")
# Output:
#   [tracer] Step 2: resumed, x=10, received=None
#   Got: 'second'

print("--- Calling next(g) #3 ---")
try:
    next(g)            # resumes, prints Step 3, then StopIteration
except StopIteration:
    print("Generator done")
# Output:
#   [tracer] Step 3: final, x=15
#   Generator done

# What Python saves at each yield:
# ┌──────────────────────────────────────┐
# │ SUSPENDED FRAME                      │
# │  code pointer → line after yield    │
# │  locals: x = 10 (or 15 after step2) │
# │  status: SUSPENDED                   │
# └──────────────────────────────────────┘
```

**Why:** The key insight is that a generator's frame is **heap-allocated**, not stack-allocated. Normal function frames are destroyed on return. Generator frames persist between `next()` calls — that is the entire mechanism that makes lazy evaluation possible.
</details>

---

### Q8 🟡 · memory benchmark — sys.getsizeof() comparison

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

**Problem:** Write a benchmark function that compares memory usage of list comprehension vs generator expression for increasing sizes (100, 1_000, 10_000, 1_000_000 items). Print a comparison table.

<details>
<summary>💡 Hint</summary>

`sys.getsizeof()` on a generator always returns a small constant. On a list it grows linearly with the number of elements.
</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

def memory_benchmark():
    sizes = [100, 1_000, 10_000, 100_000, 1_000_000]

    print(f"{'Size':>12} {'List (bytes)':>15} {'Generator (bytes)':>18} {'Ratio':>8}")
    print("-" * 58)

    for n in sizes:
        lst = [x * 2 for x in range(n)]
        gen = (x * 2 for x in range(n))

        list_size = sys.getsizeof(lst)
        gen_size  = sys.getsizeof(gen)
        ratio     = list_size / gen_size

        print(f"{n:>12,} {list_size:>15,} {gen_size:>18,} {ratio:>7.0f}x")


memory_benchmark()

# Sample output:
#          Size     List (bytes)   Generator (bytes)    Ratio
# ----------------------------------------------------------
#           100              920               112       8x
#         1,000            8,056               112      72x
#        10,000           85,176               112     760x
#       100,000          824,456               112   7,361x
#     1,000,000        8,448,728               112  75,435x

# Key observation:
# Generator size is CONSTANT (~112 bytes) regardless of n.
# List size grows linearly with n.
# At 1M items the generator is 75,000x more memory-efficient.
```

**Why:** The generator holds only its suspended frame — code pointer plus a handful of local variables. It is independent of how many items it will produce. The list must allocate a pointer slot for every element. This benchmark makes the O(1) vs O(n) memory difference concrete and measurable.
</details>

---

### Q9 🟢 · gen expression — Rewrite a List Comprehension

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

**Problem:** Rewrite the following list comprehension as a generator expression. Then explain when you should prefer each form:

```python
evens = [x for x in range(1_000_000) if x % 2 == 0]
total = sum(evens)
```

<details>
<summary>💡 Hint</summary>

Replace `[` with `(` and `]` with `)`. When passing directly to `sum()`, you can drop the outer parentheses entirely since the function call provides them.
</details>

<details>
<summary>✅ Answer</summary>

```python
# Original — list comprehension (eager, stores all even numbers in RAM):
evens_list = [x for x in range(1_000_000) if x % 2 == 0]
total_list = sum(evens_list)
print(total_list)  # 249999500000

# Rewritten — generator expression (lazy, O(1) memory):
evens_gen  = (x for x in range(1_000_000) if x % 2 == 0)
total_gen  = sum(evens_gen)
print(total_gen)   # 249999500000  ← same result

# Most concise — pass gen expression directly into sum():
total = sum(x for x in range(1_000_000) if x % 2 == 0)
print(total)       # 249999500000

# --- When to use each ---

# Use LIST when:
#   - You need random access:  evens[42]
#   - You need to iterate multiple times
#   - You need len():  len(evens)
#   - You need to pass to a function expecting a sequence

# Use GENERATOR when:
#   - One pass only: sum(), max(), any(), all(), for loop
#   - Large or infinite sequences
#   - Memory is constrained
#   - Composing a pipeline

import sys
print(sys.getsizeof([x for x in range(1_000_000) if x % 2 == 0]))  # ~4MB
print(sys.getsizeof((x for x in range(1_000_000) if x % 2 == 0)))  # ~112B
```

**Why:** The generator expression syntax `(expr for x in it if cond)` is identical in semantics to a generator function with `yield`. The only difference from a list comprehension is laziness. When your consumer only needs one pass (like `sum`, `max`, `any`, `all`), a generator expression is strictly better — same result, a fraction of the memory.
</details>

---

### Q10 🟡 · yield from — Flatten a Nested List

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

**Problem:** Write a `flatten(nested)` generator that recursively flattens a deeply nested list using `yield from`. It should handle arbitrary nesting depth.

<details>
<summary>💡 Hint</summary>

Check if each item is a list. If yes, `yield from flatten(item)` (recursive delegation). If no, `yield item` directly.
</details>

<details>
<summary>✅ Answer</summary>

```python
from typing import Any

def flatten(nested: Any):
    """Recursively flatten nested lists of any depth."""
    if isinstance(nested, list):
        for item in nested:
            yield from flatten(item)   # delegate to sub-generator
    else:
        yield nested                   # base case: yield the scalar


# Test cases:
print(list(flatten([1, 2, 3])))
# [1, 2, 3]

print(list(flatten([1, [2, 3], 4])))
# [1, 2, 3, 4]

print(list(flatten([1, [2, [3, [4, [5]]]]])))
# [1, 2, 3, 4, 5]

print(list(flatten([[1, 2], [3, [4, 5]], [6]])))
# [1, 2, 3, 4, 5, 6]

# Without yield from (verbose alternative):
def flatten_manual(nested):
    if isinstance(nested, list):
        for item in nested:
            for value in flatten_manual(item):   # explicit loop
                yield value
    else:
        yield nested

# Both produce identical results — yield from is cleaner
print(list(flatten_manual([1, [2, [3]]])))  # [1, 2, 3]
```

**Why:** `yield from iterable` is equivalent to `for x in iterable: yield x` but it also transparently forwards `send()` and `throw()` calls to the sub-generator. For recursive flattening it means the recursion composes cleanly without any extra looping boilerplate.
</details>

---

### Q11 🟡 · delegation — Chain Two Generators with yield from

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

**Problem:** Write a `chain_generators(gen1, gen2)` function that yields all items from `gen1` then all items from `gen2`, using `yield from` instead of a manual loop. Compare the two approaches side by side.

<details>
<summary>💡 Hint</summary>

`yield from gen1` exhausts gen1 entirely before moving to gen2. You can `yield from` any iterable, not just generators.
</details>

<details>
<summary>✅ Answer</summary>

```python
# --- Manual loop approach (verbose) ---
def chain_manual(gen1, gen2):
    for item in gen1:
        yield item
    for item in gen2:
        yield item


# --- yield from approach (clean) ---
def chain_generators(gen1, gen2):
    yield from gen1
    yield from gen2


# Works with any iterables:
def evens(n):
    for i in range(0, n, 2):
        yield i

def odds(n):
    for i in range(1, n, 2):
        yield i


result = list(chain_generators(evens(6), odds(6)))
print(result)   # [0, 2, 4, 1, 3, 5]

# Also works with lists, ranges, strings — any iterable:
def combined():
    yield from [10, 20, 30]
    yield from range(3)
    yield from "abc"

print(list(combined()))   # [10, 20, 30, 0, 1, 2, 'a', 'b', 'c']

# The standard library itertools.chain does this generically:
from itertools import chain
print(list(chain(evens(6), odds(6))))   # [0, 2, 4, 1, 3, 5]
```

**Why:** `yield from` collapses a delegation loop into a single statement. Beyond readability, it properly forwards `send()` and `throw()` from the outer generator to the inner one — something the manual loop version cannot do. This matters when building coroutine pipelines.
</details>

---

### Q12 🟡 · send() — running_average() Coroutine

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

**Problem:** Write a `running_average()` coroutine that accepts numbers via `send()` and yields the current running average after each value. The coroutine should run indefinitely until closed.

<details>
<summary>💡 Hint</summary>

The pattern is: `value = yield result`. This both sends `result` out and receives the next `value` in. You must prime the coroutine with `next()` before calling `send()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
def running_average():
    """
    Coroutine: send numbers in, receive running average out.
    Must prime with next() before first send().
    """
    count = 0
    total = 0.0
    average = None

    while True:
        value = yield average       # yield average OUT, receive value IN
        if value is None:
            return average          # generator.close() triggers GeneratorExit
        count += 1
        total += value
        average = total / count


# Usage:
avg = running_average()
next(avg)               # PRIME: advance to first yield, avg starts as None

result = avg.send(10)
print(f"After 10: {result}")   # 10.0

result = avg.send(20)
print(f"After 20: {result}")   # 15.0

result = avg.send(30)
print(f"After 30: {result}")   # 20.0

result = avg.send(40)
print(f"After 40: {result}")   # 25.0

avg.close()   # clean shutdown


# Helper to auto-prime (common pattern):
def coroutine(func):
    """Decorator that auto-primes a coroutine."""
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)   # advance to first yield
        return gen
    return wrapper

@coroutine
def running_average_primed():
    count = 0
    total = 0.0
    average = None
    while True:
        value = yield average
        if value is None:
            return average
        count += 1
        total += value
        average = total / count

avg2 = running_average_primed()   # no need to call next()
print(avg2.send(5))    # 5.0
print(avg2.send(15))   # 10.0
```

**Why:** `value = yield result` is a two-way channel: it yields `result` to the caller and suspends, then when the caller calls `send(x)`, execution resumes with `x` assigned to `value`. This turns a generator into a stateful stream processor — count and total persist across calls without any external state.
</details>

---

### Q13 🟠 · priming — Why Coroutines Need next() First

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)

**Problem:** Explain exactly why a coroutine must be primed with `next()` before the first `send(value)` call. Demonstrate what happens if you skip priming. Then write a `@coroutine` decorator that auto-primes.

<details>
<summary>💡 Hint</summary>

When a generator is first created, its body has not run at all. `send(value)` sends a value to the *current* yield expression, but there is no current yield yet — the generator hasn't reached the first `yield`. `next()` (equivalent to `send(None)`) advances the body to the first `yield` so it is ready to receive.
</details>

<details>
<summary>✅ Answer</summary>

```python
def my_coroutine():
    print("Coroutine started")
    value = yield "ready"     # first yield — must reach here before send()
    print(f"Received: {value}")
    yield "done"


# --- What happens without priming ---
gen = my_coroutine()
# At this point: body has NOT run. gen is at the START, before any yield.

try:
    gen.send(42)   # ERROR: can't send value to a just-started generator
except TypeError as e:
    print(f"TypeError: {e}")
# TypeError: can't send non-None value to a just-started generator


# --- Correct approach: prime first ---
gen = my_coroutine()

next(gen)          # advances to first yield; body prints "Coroutine started"
                   # equivalent to gen.send(None)
                   # returns "ready" — the yielded value

gen.send(42)       # NOW safe: sends 42 to the yield expression
                   # body resumes, prints "Received: 42"


# --- Why this happens (mental model) ---
# A generator body before the first yield:
#
#   [START]  ← generator is here when created
#      |
#   print("Coroutine started")
#      |
#   value = yield "ready"   ← first yield; next() takes us HERE
#      |
#   print(f"Received: {value}")
#
# send(x) means "resume AND inject x as the value of the yield expression"
# If the generator hasn't reached a yield yet, there is nowhere to inject x.


# --- @coroutine auto-primer decorator ---
import functools

def coroutine(func):
    """Decorator: auto-prime a coroutine on creation."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)   # prime: advance to first yield
        return gen
    return wrapper

@coroutine
def accumulator():
    total = 0
    while True:
        n = yield total
        total += n

acc = accumulator()       # no next() needed — decorator handles it
print(acc.send(10))       # 10
print(acc.send(20))       # 30
print(acc.send(5))        # 35
```

**Why:** A generator's frame starts before the first line of code. `next()` (i.e., `send(None)`) runs the body forward until the first `yield`, leaving the generator suspended at that yield point — ready to receive an injected value. `send(non_None)` without priming fails because there is no yield expression currently suspended and waiting for a value.
</details>

---

### Q14 🟡 · pipeline — 3-Stage CSV Pipeline

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)

**Problem:** Build a 3-stage generator pipeline:
1. `read_lines(filepath)` — yields raw lines from a file
2. `parse_csv(lines)` — yields each line split into a list of fields
3. `filter_rows(rows, col_index, value)` — yields only rows where `row[col_index] == value`

Compose them and print matching rows.

<details>
<summary>💡 Hint</summary>

Each stage takes the previous stage's generator as input. Memory at any point is one row — regardless of file size.
</details>

<details>
<summary>✅ Answer</summary>

```python
import csv
import io

# Stage 1: Source — read lines lazily from a file
def read_lines(filepath: str):
    with open(filepath, encoding="utf-8") as f:
        yield from f   # one line at a time


# Stage 2: Parse — convert each line to a list of CSV fields
def parse_csv(lines):
    reader = csv.reader(lines)
    for row in reader:
        yield row   # ['Alice', '30', 'Engineering']


# Stage 3: Filter — pass only rows matching a value in a column
def filter_rows(rows, col_index: int, value: str):
    for row in rows:
        if len(row) > col_index and row[col_index] == value:
            yield row


# --- Demo with an in-memory file (same pattern works with real files) ---
sample_csv = """name,age,department
Alice,30,Engineering
Bob,25,Marketing
Carol,35,Engineering
Dave,28,Marketing
Eve,32,Engineering
"""

def demo_pipeline():
    # Simulate a file using StringIO
    lines = io.StringIO(sample_csv)

    # Build the pipeline — no data flows yet, just connected generators
    parsed   = parse_csv(lines)
    filtered = filter_rows(parsed, col_index=2, value="Engineering")

    # Data flows HERE — one row at a time through all stages
    print("Engineering employees:")
    for row in filtered:
        print(row)


demo_pipeline()
# Engineering employees:
# ['name', 'age', 'department']  ← header also passes filter (col 2 = 'department' ≠ 'Engineering')
# ['Alice', '30', 'Engineering']
# ['Carol', '35', 'Engineering']
# ['Eve', '32', 'Engineering']

# Memory at any moment:
#   read_lines:  1 line (string, ~50 bytes)
#   parse_csv:   1 row  (list,   ~100 bytes)
#   filter_rows: 1 row  (same object)
# TOTAL: O(1) — constant regardless of file size
```

**Why:** Generator pipelines compose like Unix pipes. Each stage is a lazy transformer — it yields one item, the next stage processes it, and only then is the next item pulled. No intermediate collections are built. A 100GB CSV and a 100KB CSV use identical memory.
</details>

---

### Q15 🟠 · streaming ETL — Large File, O(1) Memory

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)

**Problem:** Write a streaming ETL pipeline that processes a large log file line by line. Each line is JSON. The pipeline should: read → parse JSON → filter for ERROR level → extract fields → write to output file. The entire pipeline must maintain O(1) memory.

<details>
<summary>💡 Hint</summary>

Each stage is a generator. Compose them. The output writer is the only stage that actually "pulls" — it drives the entire pipeline with a for loop.
</details>

<details>
<summary>✅ Answer</summary>

```python
import json
import io

# Stage 1: Read lines from input file
def read_lines(filepath: str):
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            yield line.rstrip("\n")


# Stage 2: Parse each line as JSON, skip malformed lines
def parse_json_lines(lines):
    for line in lines:
        if not line.strip():
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            pass   # silently skip malformed lines


# Stage 3: Filter to ERROR level only
def filter_errors(events):
    for event in events:
        if event.get("level") == "ERROR":
            yield event


# Stage 4: Extract only the fields we need
def extract_fields(events):
    for event in events:
        yield {
            "timestamp": event.get("ts", ""),
            "service":   event.get("service", "unknown"),
            "message":   event.get("msg", ""),
        }


# Stage 5: Write output (this stage DRIVES the pipeline)
def write_output(records, output_path: str):
    written = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for record in records:          # ← this pulls all upstream stages
            f.write(json.dumps(record) + "\n")
            written += 1
    return written


# Compose the full pipeline:
def run_etl(input_path: str, output_path: str) -> int:
    pipeline = extract_fields(
                   filter_errors(
                       parse_json_lines(
                           read_lines(input_path)
                       )
                   )
               )
    return write_output(pipeline, output_path)


# --- Demo with temp files ---
import tempfile, os

sample_logs = [
    json.dumps({"ts": "2024-01-01T10:00:00", "level": "INFO",  "service": "auth",    "msg": "User logged in"}),
    json.dumps({"ts": "2024-01-01T10:01:00", "level": "ERROR", "service": "payment", "msg": "Charge failed"}),
    json.dumps({"ts": "2024-01-01T10:02:00", "level": "INFO",  "service": "auth",    "msg": "Token refreshed"}),
    json.dumps({"ts": "2024-01-01T10:03:00", "level": "ERROR", "service": "db",      "msg": "Connection timeout"}),
    "not-valid-json",   # malformed — should be skipped
]

with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as inp:
    inp.write("\n".join(sample_logs))
    input_path = inp.name

output_path = input_path + ".out"

count = run_etl(input_path, output_path)
print(f"Wrote {count} error records")

with open(output_path) as f:
    for line in f:
        print(json.loads(line))

os.unlink(input_path)
os.unlink(output_path)

# Output:
# Wrote 2 error records
# {'timestamp': '2024-01-01T10:01:00', 'service': 'payment', 'message': 'Charge failed'}
# {'timestamp': '2024-01-01T10:03:00', 'service': 'db',      'message': 'Connection timeout'}
```

**Why:** The write_output stage is the only active consumer — it calls `next()` on each upstream generator through the `for record in records` loop. No stage buffers more than one item. A 100GB log file and a 1KB log file use the same ~2KB of working memory throughout.
</details>

---

### Q16 🟢 · itertools.chain — Combine Two Lists Lazily

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)

**Problem:** Use `itertools.chain` to combine two lists without creating a third list. Then show `chain.from_iterable` for combining a list of lists.

<details>
<summary>💡 Hint</summary>

`chain(a, b)` yields all items from `a` then all items from `b` — lazily. `chain.from_iterable([[a], [b], [c]])` is for when you have an iterable of iterables.
</details>

<details>
<summary>✅ Answer</summary>

```python
from itertools import chain

# Basic chain: combine two sequences lazily
first  = [1, 2, 3]
second = [4, 5, 6]

combined = chain(first, second)
print(type(combined))           # <class 'itertools.chain'>  ← lazy!
print(list(combined))           # [1, 2, 3, 4, 5, 6]

# No third list was created — iterates first then second in-place

# Chain more than two:
result = list(chain([1, 2], [3, 4], [5, 6], [7]))
print(result)   # [1, 2, 3, 4, 5, 6, 7]

# chain.from_iterable — when you have a list of lists:
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat   = list(chain.from_iterable(matrix))
print(flat)   # [1, 2, 3, 4, 5, 6, 7, 8, 9]

# Compare: sum with chain for partial aggregation
first_evens = (x for x in range(0, 10, 2))    # 0 2 4 6 8
more_evens  = (x for x in range(10, 20, 2))   # 10 12 14 16 18
total = sum(chain(first_evens, more_evens))
print(total)   # 90 — never materialized as a full list

# Without chain you'd have to build a list:
# total = sum([0,2,4,6,8] + [10,12,14,16,18])  ← creates intermediate list
```

**Why:** `chain` avoids allocating a merged list — it wraps multiple iterables into one lazy iterator that yields from each in sequence. For large sequences this saves both memory (no copy) and time (no merge step).
</details>

---

### Q17 🟡 · itertools.islice — First 10 from Infinite Generator

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)

**Problem:** Write an infinite `naturals()` generator that yields 1, 2, 3, 4, ... forever. Then use `itertools.islice` to safely take the first 10 values, the values from index 5 to 15, and every 3rd value in the first 30.

<details>
<summary>💡 Hint</summary>

`islice(iterable, stop)` or `islice(iterable, start, stop, step)`. Like `range()` but for any iterator. It does NOT index randomly — it consumes and discards up to `start`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from itertools import islice

def naturals():
    """Infinite generator: 1, 2, 3, 4, ..."""
    n = 1
    while True:
        yield n
        n += 1


# Take first 10:
first_10 = list(islice(naturals(), 10))
print(first_10)    # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Values at indices 5..14 (start=5, stop=15):
mid_10 = list(islice(naturals(), 5, 15))
print(mid_10)      # [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

# Every 3rd value in first 30 (start=0, stop=30, step=3):
every_3rd = list(islice(naturals(), 0, 30, 3))
print(every_3rd)   # [1, 4, 7, 10, 13, 16, 19, 22, 25, 28]

# NEVER do this with an infinite generator:
# list(naturals())   ← infinite loop! Never returns.

# islice is the safe way to "slice" any iterator — finite or infinite.
# It discards items up to start, yields up to stop, respects step.

# Common pattern: take until condition with takewhile instead:
from itertools import takewhile
under_100 = list(takewhile(lambda x: x < 100, naturals()))
print(f"Naturals under 100: {len(under_100)} items, last={under_100[-1]}")
# Naturals under 100: 99 items, last=99
```

**Why:** `islice` is the safe interface between infinite sequences and code that needs a bounded result. It never pulls more items than needed and uses O(1) memory — it does not materialize a slice, it just counts and yields.
</details>

---

### Q18 🟡 · itertools.groupby — Group Dicts by Key

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)

**Problem:** Given a list of employee dicts, use `itertools.groupby` to group them by department. Print each department and the employees in it. Demonstrate the critical requirement that the input must be sorted first.

<details>
<summary>💡 Hint</summary>

`groupby` groups **consecutive** equal-key items. If the data is not sorted by the grouping key first, employees in the same department will appear in separate groups.
</details>

<details>
<summary>✅ Answer</summary>

```python
from itertools import groupby

employees = [
    {"name": "Alice", "dept": "Engineering"},
    {"name": "Bob",   "dept": "Marketing"},
    {"name": "Carol", "dept": "Engineering"},
    {"name": "Dave",  "dept": "HR"},
    {"name": "Eve",   "dept": "Marketing"},
    {"name": "Frank", "dept": "Engineering"},
]

# --- WRONG: unsorted input — same dept appears in multiple groups ---
print("Without sorting:")
for dept, group in groupby(employees, key=lambda e: e["dept"]):
    print(f"  {dept}: {[e['name'] for e in group]}")
# Engineering: ['Alice']
# Marketing:   ['Bob']
# Engineering: ['Carol']   ← Engineering appears AGAIN!
# HR:          ['Dave']
# Marketing:   ['Eve']     ← Marketing appears AGAIN!
# Engineering: ['Frank']

# --- CORRECT: sort by key first ---
sorted_employees = sorted(employees, key=lambda e: e["dept"])

print("\nWith sorting:")
for dept, group in groupby(sorted_employees, key=lambda e: e["dept"]):
    names = [e["name"] for e in group]
    print(f"  {dept}: {names}")
# Engineering: ['Alice', 'Carol', 'Frank']
# HR:          ['Dave']
# Marketing:   ['Bob', 'Eve']

# IMPORTANT: consume each group before the next iteration
# (groups are lazy — the group iterator is invalidated on next groupby step)
grouped = {}
for dept, group in groupby(sorted_employees, key=lambda e: e["dept"]):
    grouped[dept] = list(group)   # ← materialize group immediately!

print("\nGrouped dict:", grouped)
```

**Why:** `groupby` works on consecutive runs, not the full sequence — it is intentionally O(1) memory. This means you must sort first (O(n log n)) if you want true grouping. Also: each group iterator shares state with the main groupby iterator, so you must `list(group)` before the next `for` iteration or the group disappears.
</details>

---

### Q19 🟡 · infinite generator — Fibonacci with islice

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)

**Problem:** Write an infinite `fibonacci()` generator that yields the Fibonacci sequence starting from 0. Use `islice` to print the first 10 values. Then show how to find the first Fibonacci number over 1000.

<details>
<summary>💡 Hint</summary>

Maintain two variables `a, b`. Each iteration: yield `a`, then advance `a, b = b, a + b`. Use `itertools.dropwhile` or a manual `next()` loop to find the first value over a threshold.
</details>

<details>
<summary>✅ Answer</summary>

```python
from itertools import islice, dropwhile

def fibonacci():
    """Infinite Fibonacci sequence: 0, 1, 1, 2, 3, 5, 8, 13, ..."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


# First 10:
first_10 = list(islice(fibonacci(), 10))
print(first_10)
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

# First 20:
first_20 = list(islice(fibonacci(), 20))
print(first_20)
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181]

# First Fibonacci number over 1000:
first_over_1000 = next(dropwhile(lambda x: x <= 1000, fibonacci()))
print(f"First Fibonacci > 1000: {first_over_1000}")   # 1597

# Alternative: manual search
for fib in fibonacci():
    if fib > 1000:
        print(f"Found: {fib}")   # 1597
        break

# Sum of first 100 Fibonacci numbers (never materializes the list):
total = sum(islice(fibonacci(), 100))
print(f"Sum of first 100 Fibonacci numbers: {total}")
# 927372692193078999175
```

**Why:** Infinite generators encode mathematical sequences cleanly — no upper bound needed. `islice` is the safe consumer. `dropwhile`/`takewhile` from itertools let you query into the sequence without random access. The generator holds only two integers (`a` and `b`) regardless of how many items have been produced.
</details>

---

### Q20 🟡 · return value — StopIteration.value

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)

**Problem:** Demonstrate that `return value` inside a generator raises `StopIteration` with `StopIteration.value` set to the returned value. Show how to capture it manually and how `yield from` captures it automatically.

<details>
<summary>💡 Hint</summary>

`list()`, `for`, and `sum()` all catch `StopIteration` but discard `.value`. To see the value you must catch `StopIteration` yourself in a `while True / try / except` loop, or use `yield from` in a delegating generator.
</details>

<details>
<summary>✅ Answer</summary>

```python
def bounded_counter(start: int, stop: int):
    """Counts from start to stop, returns a summary string."""
    n = start
    while n <= stop:
        yield n
        n += 1
    return f"Counted from {start} to {stop}"   # becomes StopIteration.value


# --- Method 1: list() swallows the return value ---
result = list(bounded_counter(1, 5))
print(result)   # [1, 2, 3, 4, 5]  — return value is LOST

# --- Method 2: catch StopIteration manually ---
gen = bounded_counter(1, 5)
while True:
    try:
        val = next(gen)
        print(f"Yielded: {val}")
    except StopIteration as e:
        print(f"Generator returned: {e.value!r}")
        break

# Output:
# Yielded: 1
# Yielded: 2
# Yielded: 3
# Yielded: 4
# Yielded: 5
# Generator returned: 'Counted from 1 to 5'


# --- Method 3: yield from captures the return value automatically ---
def delegating():
    summary = yield from bounded_counter(1, 5)   # summary = "Counted from 1 to 5"
    print(f"Sub-generator returned: {summary!r}")
    yield f"DONE: {summary}"

g = delegating()
print(list(g))
# (prints) Sub-generator returned: 'Counted from 1 to 5'
# ['DONE: Counted from 1 to 5']
# Note: [1,2,3,4,5] are consumed by list(g) first, then 'DONE...' is last item
print(list(delegating()))
# Sub-generator returned: 'Counted from 1 to 5'
# [1, 2, 3, 4, 5, 'DONE: Counted from 1 to 5']
```

**Why:** `return value` in a generator is not a shortcut for the last `yield` — it is a metadata channel. It is designed for coroutine sub-delegation: `result = yield from sub()` gives the outer coroutine the sub-coroutine's final return value without any extra yielded item. Standard consumers like `list()` and `for` ignore `.value` by design.
</details>

---

### Q21 🟠 · async generator — Paginated API Results

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)

**Problem:** Write an async generator `fetch_pages(base_url, max_pages)` that simulates fetching paginated API results one page at a time. Each "fetch" should use `await asyncio.sleep(0)` to simulate I/O. Consume it with `async for`.

<details>
<summary>💡 Hint</summary>

An async generator is `async def` + `yield`. It is consumed with `async for`. You cannot use `list()` directly — use `[x async for x in gen]` or accumulate in a loop.
</details>

<details>
<summary>✅ Answer</summary>

```python
import asyncio
from typing import AsyncGenerator

async def fetch_pages(
    base_url: str,
    max_pages: int = 5
) -> AsyncGenerator[dict, None]:
    """
    Async generator: fetches paginated API results one page at a time.
    Simulates network I/O with asyncio.sleep.
    """
    page = 1
    while page <= max_pages:
        # Simulate async HTTP fetch
        await asyncio.sleep(0.01)   # simulated I/O delay

        # Simulate parsed response
        yield {
            "page":  page,
            "items": [f"item_{page}_{i}" for i in range(3)],
            "total": max_pages * 3,
            "next":  page + 1 if page < max_pages else None,
        }
        page += 1


async def process_all_pages():
    """Consume the async generator, processing one page at a time."""
    all_items = []

    async for page_data in fetch_pages("https://api.example.com/items", max_pages=4):
        print(f"Processing page {page_data['page']}: {page_data['items']}")
        all_items.extend(page_data["items"])

        # Could also break early:
        # if some_condition:
        #     break

    print(f"\nTotal items collected: {len(all_items)}")
    return all_items


# Async comprehension alternative:
async def collect_all():
    pages = [page async for page in fetch_pages("https://api.example.com", max_pages=3)]
    return pages


asyncio.run(process_all_pages())

# Output:
# Processing page 1: ['item_1_0', 'item_1_1', 'item_1_2']
# Processing page 2: ['item_2_0', 'item_2_1', 'item_2_2']
# Processing page 3: ['item_3_0', 'item_3_1', 'item_3_2']
# Processing page 4: ['item_4_0', 'item_4_1', 'item_4_2']
# Total items collected: 12
```

**Why:** Async generators combine lazy evaluation with async I/O. Each `yield` suspends until the consumer asks for the next item via `async for`, and each `await` suspends the coroutine until I/O completes. Memory stays O(1) — you process one page at a time regardless of how many pages exist.
</details>

---

### Q22 🟡 · exhaustion — Generator Exhaustion Demo

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)

**Problem:** Write a demonstration that clearly shows generator exhaustion: create a generator, iterate it fully, then iterate it again and show the result is empty. Then show three fixes.

<details>
<summary>💡 Hint</summary>

Generators have no "rewind". Once `StopIteration` is raised, subsequent calls to `next()` keep raising `StopIteration`. There is no reset method.
</details>

<details>
<summary>✅ Answer</summary>

```python
# --- Demonstrating exhaustion ---
gen = (x ** 2 for x in range(5))

first_pass = list(gen)
print(f"First pass:  {first_pass}")   # [0, 1, 4, 9, 16]

second_pass = list(gen)
print(f"Second pass: {second_pass}")  # []  ← exhausted!

# Confirmed: next() on an exhausted generator:
gen2 = (x for x in range(3))
print(next(gen2))   # 0
print(next(gen2))   # 1
print(next(gen2))   # 2
try:
    print(next(gen2))   # StopIteration
except StopIteration:
    print("Exhausted!")
try:
    print(next(gen2))   # STILL raises — no auto-reset
except StopIteration:
    print("Still exhausted!")


# --- Fix 1: Wrap in a function — call it twice for a fresh generator ---
def squares(n):
    return (x ** 2 for x in range(n))

print(list(squares(5)))   # [0, 1, 4, 9, 16]
print(list(squares(5)))   # [0, 1, 4, 9, 16]  ← fresh generator each call


# --- Fix 2: Materialize to a list if you need multiple passes ---
data = list(x ** 2 for x in range(5))   # list is reusable
print(data)   # [0, 1, 4, 9, 16]
print(data)   # [0, 1, 4, 9, 16]  ← still there


# --- Fix 3: Use itertools.tee to fork a generator (use carefully) ---
from itertools import tee

gen3 = (x ** 2 for x in range(5))
copy1, copy2 = tee(gen3, 2)   # creates two independent iterators
print(list(copy1))   # [0, 1, 4, 9, 16]
print(list(copy2))   # [0, 1, 4, 9, 16]
# WARNING: tee buffers items — if one iterator is far ahead, memory grows
```

**Why:** A generator is a one-way ticket. Its `__iter__` returns `self`, not a new object — so every `iter()` call gives back the same exhausted generator. This is by design: generators are meant for single-pass streaming. When you need multiple passes, the clean pattern is wrapping in a function (Fix 1) or materializing (Fix 2).
</details>

---

### Q23 🟡 · collections.abc — Classify Iterables and Iterators

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)

**Problem:** Use `collections.abc.Iterator` and `collections.abc.Iterable` to classify various Python objects. Write a `classify(obj)` function that reports whether an object is an Iterable, an Iterator, both, or neither.

<details>
<summary>💡 Hint</summary>

`isinstance(x, Iterable)` checks for `__iter__`. `isinstance(x, Iterator)` checks for both `__iter__` and `__next__`. All iterators are iterables, but not all iterables are iterators.
</details>

<details>
<summary>✅ Answer</summary>

```python
from collections.abc import Iterable, Iterator

def classify(obj, label: str = ""):
    is_iterable = isinstance(obj, Iterable)
    is_iterator = isinstance(obj, Iterator)

    role = []
    if is_iterator:
        role.append("Iterator (has __iter__ + __next__)")
    elif is_iterable:
        role.append("Iterable only (has __iter__, no __next__)")
    else:
        role.append("Neither Iterable nor Iterator")

    name = label or type(obj).__name__
    print(f"{name:30s} → {', '.join(role)}")


# Test various types:
classify([1, 2, 3],              "list")
classify((1, 2, 3),              "tuple")
classify({1: "a"},               "dict")
classify({1, 2, 3},              "set")
classify("hello",                "str")
classify(range(5),               "range")

classify(iter([1, 2, 3]),        "list_iterator")
classify(iter(range(5)),         "range_iterator")
classify((x for x in range(5)), "generator expression")

def gen_func():
    yield 1
classify(gen_func(),             "generator function result")

classify(42,                     "int")
classify(None,                   "NoneType")

# Output:
# list                           → Iterable only (has __iter__, no __next__)
# tuple                          → Iterable only (has __iter__, no __next__)
# dict                           → Iterable only (has __iter__, no __next__)
# set                            → Iterable only (has __iter__, no __next__)
# str                            → Iterable only (has __iter__, no __next__)
# range                          → Iterable only (has __iter__, no __next__)
# list_iterator                  → Iterator (has __iter__ + __next__)
# range_iterator                 → Iterator (has __iter__ + __next__)
# generator expression           → Iterator (has __iter__ + __next__)
# generator function result      → Iterator (has __iter__ + __next__)
# int                            → Neither Iterable nor Iterator
# NoneType                       → Neither Iterable nor Iterator
```

**Why:** `collections.abc` provides the abstract base classes that define the protocol contracts. `isinstance` with ABC works via `__subclasshook__` — it checks for the presence of the required dunder methods, not class inheritance. This is Python's duck typing formalized: if it has `__next__`, it IS an iterator.
</details>

---

### Q24 🟠 · production pattern — paginated_api() Generator

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)

**Problem:** Implement a `paginated_api(url, params)` generator that auto-fetches next pages using a cursor. Each response contains `{"items": [...], "next_cursor": "..."}`. The generator should yield individual items (not pages), automatically fetching the next page when needed.

<details>
<summary>💡 Hint</summary>

Use `requests` (or simulate with a mock). After exhausting `items` from a page, check `next_cursor`. If it is `None` or absent, raise `StopIteration` by returning.
</details>

<details>
<summary>✅ Answer</summary>

```python
from typing import Iterator, Any
from unittest.mock import patch, MagicMock
import json

def paginated_api(url: str, params: dict = None) -> Iterator[Any]:
    """
    Generator that yields individual items from a paginated API.
    Automatically fetches next pages using cursor-based pagination.
    """
    import requests

    cursor = None

    while True:
        # Build request params
        req_params = dict(params or {})
        if cursor:
            req_params["cursor"] = cursor

        # Fetch one page
        response = requests.get(url, params=req_params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Yield individual items from this page
        items = data.get("items", [])
        if not items:
            return   # empty page — done

        for item in items:
            yield item

        # Check for next page
        cursor = data.get("next_cursor")
        if not cursor:
            return   # no more pages


# --- Demo with mocked HTTP ---
def make_mock_response(items, next_cursor=None):
    mock = MagicMock()
    mock.json.return_value = {"items": items, "next_cursor": next_cursor}
    mock.raise_for_status.return_value = None
    return mock

page_responses = [
    make_mock_response(["user_1", "user_2", "user_3"], next_cursor="cur_page2"),
    make_mock_response(["user_4", "user_5", "user_6"], next_cursor="cur_page3"),
    make_mock_response(["user_7", "user_8"],           next_cursor=None),   # last page
]

with patch("requests.get", side_effect=page_responses):
    all_users = list(paginated_api("https://api.example.com/users"))
    print(f"Total users: {len(all_users)}")
    print(f"Users: {all_users}")

# Output:
# Total users: 8
# Users: ['user_1', 'user_2', 'user_3', 'user_4', 'user_5', 'user_6', 'user_7', 'user_8']

# Consumer code is clean — no pagination logic exposed:
with patch("requests.get", side_effect=page_responses):
    # Re-create side_effect for second run
    pass

# Usage pattern in production:
# for user in paginated_api("https://api.example.com/users", {"limit": 100}):
#     process_user(user)   # memory: O(1) — one user at a time
```

**Why:** Encapsulating pagination in a generator is the cleanest API design pattern. The consumer calls `for item in paginated_api(url)` and gets a flat stream of items — unaware of pages, cursors, or HTTP. New pages are fetched only when the previous page's items are exhausted. Memory is O(1): one page worth of items at most.
</details>

---

### Q25 🟠 · Capstone — Full Streaming ETL Pipeline

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)

**Problem:** Build a complete streaming ETL pipeline with O(1) memory. The pipeline must:
1. Read a CSV file line by line
2. Parse each row into a typed dict
3. Filter out rows where `amount < 0`
4. Transform: add a `tax` field = `amount * 0.1`
5. Write transformed rows to an output CSV

All stages must be generators. The pipeline must never load the full file into memory. Demonstrate it works with a test file.

<details>
<summary>💡 Hint</summary>

5 generator stages + 1 writer that drives the pipeline. Use `csv.DictReader` for parsing and `csv.DictWriter` for output. Wrap `DictReader` in a generator to keep the pattern consistent.
</details>

<details>
<summary>✅ Answer</summary>

```python
import csv
import tempfile
import os
from typing import Iterator

# ─────────────────────────────────────────
# Stage 1: Source — read raw lines lazily
# ─────────────────────────────────────────
def read_csv_lines(filepath: str) -> Iterator[str]:
    """Yield raw lines from a CSV file one at a time."""
    with open(filepath, encoding="utf-8", newline="") as f:
        yield from f


# ─────────────────────────────────────────
# Stage 2: Parse — convert to typed dicts
# ─────────────────────────────────────────
def parse_csv_rows(lines: Iterator[str]) -> Iterator[dict]:
    """Parse CSV lines into dicts with typed fields."""
    reader = csv.DictReader(lines)
    for row in reader:
        yield {
            "id":       int(row["id"]),
            "name":     row["name"].strip(),
            "amount":   float(row["amount"]),
            "category": row["category"].strip(),
        }


# ─────────────────────────────────────────
# Stage 3: Filter — drop invalid rows
# ─────────────────────────────────────────
def filter_positive(rows: Iterator[dict]) -> Iterator[dict]:
    """Yield only rows where amount >= 0."""
    for row in rows:
        if row["amount"] >= 0:
            yield row


# ─────────────────────────────────────────
# Stage 4: Transform — enrich rows
# ─────────────────────────────────────────
def add_tax(rows: Iterator[dict], tax_rate: float = 0.1) -> Iterator[dict]:
    """Add a tax field to each row."""
    for row in rows:
        yield {
            **row,
            "tax":   round(row["amount"] * tax_rate, 2),
            "total": round(row["amount"] * (1 + tax_rate), 2),
        }


# ─────────────────────────────────────────
# Stage 5: Sink — write to output CSV
# ─────────────────────────────────────────
def write_csv(rows: Iterator[dict], output_path: str) -> int:
    """Write transformed rows to CSV. Returns row count. DRIVES the pipeline."""
    fieldnames = ["id", "name", "amount", "category", "tax", "total"]
    written = 0

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:           # ← this for loop pulls all upstream stages
            writer.writerow(row)
            written += 1

    return written


# ─────────────────────────────────────────
# Pipeline composer
# ─────────────────────────────────────────
def run_etl(input_path: str, output_path: str) -> int:
    """Compose and run the full streaming ETL pipeline."""
    pipeline = add_tax(
                   filter_positive(
                       parse_csv_rows(
                           read_csv_lines(input_path)
                       )
                   )
               )
    return write_csv(pipeline, output_path)


# ─────────────────────────────────────────
# Demo
# ─────────────────────────────────────────
sample_csv = """id,name,amount,category
1,Alice,100.00,food
2,Bob,-50.00,refund
3,Carol,250.00,electronics
4,Dave,0.00,misc
5,Eve,75.50,food
6,Frank,-10.00,refund
"""

# Write sample input
with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
    f.write(sample_csv)
    input_path = f.name

output_path = input_path.replace(".csv", "_output.csv")

count = run_etl(input_path, output_path)
print(f"Processed {count} rows (filtered out negatives)\n")

# Show output
with open(output_path) as f:
    print(f.read())

# Cleanup
os.unlink(input_path)
os.unlink(output_path)

# Output:
# Processed 4 rows (filtered out negatives)
#
# id,name,amount,category,tax,total
# 1,Alice,100.0,food,10.0,110.0
# 3,Carol,250.0,electronics,25.0,275.0
# 4,Dave,0.0,misc,0.0,0.0
# 5,Eve,75.5,food,7.55,83.05
```

**Why:** This is the canonical production generator pattern. Five generators are connected but none runs until `write_csv` pulls the first item. At any moment the pipeline holds at most one row — one dict of ~200 bytes — regardless of whether the file is 1KB or 100GB. Each stage has a single responsibility, is independently testable, and can be swapped without touching others. This is how real data engineering tools like Apache Beam and Luigi model their pipelines internally.
</details>

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Back to Module | [theory.md](./theory.md) |
| 📖 Theory | [theory.md](./theory.md) |
| 🔧 Production Patterns | [04_generator_patterns.md](./04_generator_patterns.md) |
| ➡️ Next Module | [12_context_managers →](../12_context_managers/practice.md) |

---

**Related:** [01_generators.py](./01_generators.py) · [02_iterators.py](./02_iterators.py) · [04_generator_patterns.md](./04_generator_patterns.md)
