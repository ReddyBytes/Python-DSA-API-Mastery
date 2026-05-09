<a id="top"></a>
# 🔄 Iterators & Generators — Theory

> *"A generator doesn't compute the next value until you ask for it.*
> *That's the entire secret to processing infinite data in constant memory."*

## 📖 Table of Contents

- [🎬 The Problem: 50 Million Records, 4GB RAM](#the-problem-50-million-records-4gb-ram)
- [📌 Learning Priority](#learning-priority)
- [1. The Iteration Protocol](#1-the-iteration-protocol)
- [2. Building a Custom Iterator Class](#2-building-a-custom-iterator-class)
- [3. Generator Functions — yield](#3-generator-functions--yield)
- [4. How yield Suspends Execution — The Frame Model](#4-how-yield-suspends-execution--the-frame-model)
  - [Why Generators Are Lazy — The Memory Story](#why-generators-are-lazy--the-memory-story)
  - [Generator vs Iterator vs List — When to Use Each](#generator-vs-iterator-vs-list--when-to-use-each)
- [5. Generator Expressions](#5-generator-expressions)
- [6. yield from — Delegation](#6-yield-from--delegation)
- [7. send() — Generators as Coroutines](#7-send--generators-as-coroutines)
- [8. Generator Pipelines — Streaming ETL](#8-generator-pipelines--streaming-etl)
- [9. itertools — The Standard Library Power Tools](#9-itertools--the-standard-library-power-tools)
  - [Infinite Iterators](#infinite-iterators)
  - [Terminating Iterators](#terminating-iterators)
  - [zip_longest — Zip Unequal Sequences](#zip_longest--zip-unequal-sequences)
  - [Combinatoric Iterators](#combinatoric-iterators)
- [10. Infinite Sequences](#10-infinite-sequences)
- [11. return Inside a Generator](#11-return-inside-a-generator)
- [12. Async Generators (Python 3.6+)](#12-async-generators-python-36)
- [13. Gotchas and Anti-Patterns](#13-gotchas-and-anti-patterns)
  - [Gotcha: Generators Exhaust After One Pass](#gotcha-generators-exhaust-after-one-pass)
  - [Gotcha: Generator Returns Without Processing](#gotcha-generator-returns-without-processing)
  - [Gotcha: Late Binding in Generator Expressions](#gotcha-late-binding-in-generator-expressions)
  - [Gotcha: No len() or Indexing](#gotcha-no-len-or-indexing)
  - [Gotcha: Closing a Generator Early](#gotcha-closing-a-generator-early)
- [14. The Iterator Protocol in the Standard Library](#14-the-iterator-protocol-in-the-standard-library)
- [Summary](#summary)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`__iter__` / `__next__` protocol · Generator functions (`yield`) · Generator expressions · Lazy evaluation (why generators save memory)

**Should Learn** — Important for real projects, comes up regularly:
`yield from` · `generator.send()` · `generator.throw()` / `.close()` · `itertools` (chain, islice, groupby, takewhile, zip_longest)

**Good to Know** — Useful in specific situations:
Infinite iterators (`itertools.count`, `cycle`) · Async generators (`async def` + `yield`) · Generator pipelines

**Reference** — Know it exists, look up when needed:
`itertools.starmap` · `itertools.accumulate` · `itertools.tee`

---

<a id="the-problem-50-million-records-4gb-ram"></a>
# 🎬 The Problem: 50 Million Records, 4GB RAM

Your manager asks you to process an analytics export — 50 million user events, 8GB on disk.

**Naive approach:**

```python
def process_events(filepath):
    events = open(filepath).readlines()   # loads 8GB into RAM
    for event in events:
        process(event)
```

Result: your 4GB server crashes after 30 seconds.

**Generator approach:**

```python
def process_events(filepath):
    with open(filepath) as f:
        for line in f:                   # reads one line at a time
            process(line)
```

Memory used: ~4KB regardless of file size. The file never fully enters RAM.

This is **lazy evaluation** — compute only what you need, only when you need it. Generators are Python's mechanism for building lazy evaluation into any data source.

---

<a id="1-the-iteration-protocol"></a>
# 1. The Iteration Protocol

When you write `for x in something`, Python runs a precise protocol under the hood. Understanding it is the foundation for everything else in this module — generators, custom iterators, and why `for` loops "just work" on so many different types.

```
Step 1: Python calls iter(something)
        → calls something.__iter__()
        → returns an iterator object

Step 2: Python calls next(iterator) repeatedly
        → calls iterator.__next__()
        → each call returns the next value

Step 3: When exhausted, __next__() raises StopIteration
        → for loop catches it and stops cleanly
```

```python
# What the for loop actually does:
numbers = [10, 20, 30]

iterator = iter(numbers)           # calls numbers.__iter__()
print(next(iterator))   # 10      # calls iterator.__next__()
print(next(iterator))   # 20
print(next(iterator))   # 30
print(next(iterator))   # raises StopIteration

# The for loop is exactly equivalent to:
iterator = iter(numbers)
while True:
    try:
        x = next(iterator)
        print(x)
    except StopIteration:
        break
```

**Two roles, two interfaces:**

```
ITERABLE  — has __iter__() → returns an iterator
             Examples: list, str, dict, tuple, set, file, range

ITERATOR  — has __iter__() AND __next__()
             __iter__() returns self
             __next__() returns next value or raises StopIteration
             Examples: list_iterator, file object, generator

KEY: All iterators are iterables. Not all iterables are iterators.
```

```python
lst = [1, 2, 3]
it  = iter(lst)

# list is iterable but NOT an iterator:
hasattr(lst, '__iter__')   # True
hasattr(lst, '__next__')   # False  ← no __next__

# list_iterator is BOTH:
hasattr(it, '__iter__')    # True
hasattr(it, '__next__')    # True

# An iterator's __iter__ returns itself:
it is iter(it)             # True  ← idempotent
```

⚠️ **Common mistake — confusing iterable and iterator:** A `list` is iterable but not an iterator. Calling `next([1,2,3])` raises `TypeError`. You must call `iter([1,2,3])` first to get a `list_iterator`, then `next()` on that.

💡 **Hint:** The idempotency rule (`iter(iterator) is iterator`) is what makes iterators safe to use in `for` loops — the loop always calls `iter()` first, and for an iterator that just returns itself.

📝 **Practice:** [iteration protocol / countdown class →](./practice.md#q1--iteration-protocol--countdown-class)

> [↑ Back to Top](#top)

---

<a id="2-building-a-custom-iterator-class"></a>
# 2. Building a Custom Iterator Class

Before generators existed, all custom iteration was done with classes implementing `__iter__` and `__next__`. This is still useful when your iterator needs multiple methods, persistent configuration, or state that maps cleanly to object attributes.

```python
class CountUp:
    """Iterator that counts from start to stop, inclusive."""

    def __init__(self, start: int, stop: int):
        self.current = start
        self.stop    = stop

    def __iter__(self):
        return self           # the object IS its own iterator

    def __next__(self):
        if self.current > self.stop:
            raise StopIteration
        value = self.current
        self.current += 1
        return value

counter = CountUp(1, 5)
for n in counter:
    print(n)   # 1 2 3 4 5

# Can use next() manually:
c2 = CountUp(10, 12)
print(next(c2))   # 10
print(next(c2))   # 11
print(next(c2))   # 12
print(next(c2))   # StopIteration
```

**A useful pattern — separating the Iterable from the Iterator:**

When the same object is both iterable and iterator (as above), it can only be looped once — state is consumed. If you need a reusable iterable (loop it multiple times), separate the roles:

```python
class NumberRange:
    """Iterable — can be looped multiple times."""
    def __init__(self, start, stop):
        self.start = start
        self.stop  = stop

    def __iter__(self):
        return NumberRangeIterator(self.start, self.stop)  # ← fresh iterator each time

class NumberRangeIterator:
    """Iterator — single-use, tracks position."""
    def __init__(self, start, stop):
        self.current = start
        self.stop    = stop

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > self.stop:
            raise StopIteration
        val = self.current
        self.current += 1
        return val

r = NumberRange(1, 3)
list(r)   # [1, 2, 3]
list(r)   # [1, 2, 3]  ← works again! NumberRange creates a fresh iterator each time
```

💡 **Hint:** In practice, generator functions do all of this automatically — the generator object is the iterator, and calling the generator function again creates a fresh one. Use class-based iterators only when you need additional methods beyond iteration, or when the object's state management is complex enough to warrant a class.

📝 **Practice:** [iterator class / NumberRange with step →](./practice.md#q3--iterator-class--numberrange-with-step)

> [↑ Back to Top](#top)

---

<a id="3-generator-functions--yield"></a>
# 3. Generator Functions — yield

Writing custom iterators as classes requires `__iter__`, `__next__`, state tracking, and `StopIteration`. **Generator functions** compress all of that into a function with `yield` — Python handles the iterator protocol machinery automatically.

```python
def count_up(start, stop):
    """A generator function — contains yield."""
    current = start
    while current <= stop:
        yield current        # ← pause here, return value, resume later
        current += 1

gen = count_up(1, 5)
print(type(gen))   # <class 'generator'>

for n in gen:
    print(n)   # 1 2 3 4 5
```

**The generator IS both iterable and iterator:**
```python
gen = count_up(1, 3)
gen is iter(gen)   # True — generator is its own iterator
```

**Generator functions vs regular functions — the critical difference:**

```python
def regular():
    return 1    # body executes immediately, returns 1

def generator():
    yield 1     # body NOT executed at call time
    yield 2

# Calling:
regular()      # → 1                     (runs the body)
generator()    # → <generator object>    (body NOT run yet!)

g = generator()
next(g)   # → 1   (runs until first yield, pauses)
next(g)   # → 2   (resumes from after first yield, pauses)
next(g)   # → StopIteration (fell off the end)
```

⚠️ **Common mistake — calling a generator function and expecting immediate execution:** `result = my_generator()` does NOT run the body. It creates a generator object. The body runs only when you iterate it (`next()`, `for`, `list()`). This is the most common source of "my generator does nothing" bugs.

📝 **Practice:** [yield / squares generator →](./practice.md#q5--yield--squares-generator)

> [↑ Back to Top](#top)

---

<a id="4-how-yield-suspends-execution--the-frame-model"></a>
# 4. How yield Suspends Execution — The Frame Model

This is the critical conceptual piece. When a generator is suspended at a `yield`, Python preserves the entire execution state as a **heap-allocated frame** — unlike regular function frames which live on the call stack and are destroyed on return. See [memory layout → stack frame lifecycle](../01.1_memory_management/theory.md#-stack-frame--what-happens-on-each-call).

```
GENERATOR FRAME (suspended at yield):
┌────────────────────────────────────────┐
│ code pointer → line after the yield   │
│ local variables: current=3, stop=5    │
│ value stack: (empty)                  │
│ status: SUSPENDED                     │
└────────────────────────────────────────┘
```

```python
def demonstrate():
    print("A: start")
    x = 10
    print("B: before first yield")
    yield 1                    # ← SUSPEND. 'x' and print state preserved.
    print("C: resumed after first yield")
    x += 5
    print(f"D: x is now {x}")
    yield 2                    # ← SUSPEND again.
    print("E: final")

g = demonstrate()

print("Calling next(g) first time:")
val = next(g)    # runs A, B, yields 1, suspends
print(f"Got: {val}")

print("Calling next(g) second time:")
val = next(g)    # resumes at C, runs C, D, yields 2, suspends
print(f"Got: {val}")

print("Calling next(g) third time:")
try:
    next(g)      # resumes at E, runs E, falls off end → StopIteration
except StopIteration:
    print("Generator exhausted")

# Output:
# Calling next(g) first time:
# A: start
# B: before first yield
# Got: 1
# Calling next(g) second time:
# C: resumed after first yield
# D: x is now 15
# Got: 2
# Calling next(g) third time:
# E: final
# Generator exhausted
```

🔍 **Good to know:** The generator frame lives on the **heap**, not the call stack. This is why it survives between `next()` calls — the frame is a Python object with a reference count, just like any other object. When the generator is garbage collected, the frame is too.

---

<a id="why-generators-are-lazy--the-memory-story"></a>
## Why Generators Are Lazy — The Memory Story

Lazy evaluation means: **compute only when asked, not all at once**. A list evaluates everything immediately and stores all values in memory. A generator evaluates one item at a time and stores nothing except its suspended frame.

```
EAGER (list):                        LAZY (generator):

range_list = [0,1,2,...,999999]      range_gen = (x for x in range(1_000_000))

Memory:                              Memory:
┌─────────────────────────────┐      ┌────────────────────────────┐
│ [0][1][2][3]...[999999]     │      │ code pointer: line 1       │
│  8 MB in RAM                │      │ local: x = (current value) │
│  all at once                │      │ ~200 bytes                 │
└─────────────────────────────┘      └────────────────────────────┘
                                     generates next value on demand
```

**Concrete numbers:**

```python
import sys

# Eager: all 1 million numbers in RAM immediately
eager = [x for x in range(1_000_000)]
print(sys.getsizeof(eager))      # ~8,056,952 bytes ≈ 8 MB

# Lazy: same sequence, but ~200 bytes total
lazy = (x for x in range(1_000_000))
print(sys.getsizeof(lazy))       # ~112 bytes
```

**Why it matters in production:**

```python
# Problem: log file is 10 GB. Read all lines into memory?
lines = open("server.log").readlines()   # ← loads 10 GB into RAM. OOM crash.

# Solution: generator — process one line at a time
def read_lines(path):
    with open(path) as f:
        for line in f:
            yield line               # yields one line, then suspends

for line in read_lines("server.log"):  # never more than one line in memory
    if "ERROR" in line:
        process(line)
```

🔍 **Good to know:** `sys.getsizeof()` only measures the object itself, not the objects it references. For a list, it measures the array of pointers + a small header — the actual integers are separate objects. For a generator, it measures the frame object — which is tiny because no values are stored.

---

<a id="generator-vs-iterator-vs-list--when-to-use-each"></a>
## Generator vs Iterator vs List — When to Use Each

```
┌────────────────┬──────────────────────────────┬──────────────────────────┐
│                │  Use when                    │  Avoid when              │
├────────────────┼──────────────────────────────┼──────────────────────────┤
│  list          │  Need random access (by idx) │  Large datasets          │
│                │  Need to iterate multiple    │  Memory is constrained   │
│                │  times                       │                          │
│                │  Need len(), slicing         │                          │
├────────────────┼──────────────────────────────┼──────────────────────────┤
│  generator     │  Large/infinite sequences    │  Need random access      │
│  (lazy)        │  One-pass processing         │  Need multiple passes    │
│                │  Stream processing           │  Need len()              │
│                │  Memory-constrained systems  │                          │
├────────────────┼──────────────────────────────┼──────────────────────────┤
│  iterator      │  Custom iteration logic      │  When generator syntax   │
│  (class-based) │  Stateful with multiple      │  would be simpler        │
│                │  methods                     │                          │
└────────────────┴──────────────────────────────┴──────────────────────────┘
```

**The one-pass caveat — a common bug:**

```python
gen = (x * 2 for x in range(5))

first_pass  = list(gen)    # [0, 2, 4, 6, 8]
second_pass = list(gen)    # []  ← generator is exhausted!

# Fix: if you need multiple passes, convert to list first
data = list(gen_function())  # materialize once, reuse freely
```

⚠️ **Common mistake — passing a generator to a function and then iterating it again:** Once a generator is consumed, it's gone. If you pass a generator to `max()`, you can't also pass it to `min()` — the first call exhausted it. Wrap in `list()` if you need multiple passes.

📝 **Practice:** [frame suspension / tracing yield →](./practice.md#q7--frame-suspension--tracing-yield) · [memory benchmark / sys.getsizeof comparison →](./practice.md#q8--memory-benchmark--sysgetsizeof-comparison)

> [↑ Back to Top](#top)

---

<a id="5-generator-expressions"></a>
# 5. Generator Expressions

Generator expressions are the lazy equivalent of list comprehensions — same syntax, parentheses instead of brackets, zero memory footprint until iterated.

```python
# List comprehension — evaluates eagerly, stores all in RAM:
squares_list = [x**2 for x in range(1_000_000)]   # ~8MB in memory

# Generator expression — evaluates lazily, no storage:
squares_gen  = (x**2 for x in range(1_000_000))   # ~200 bytes

# Syntax: parentheses instead of brackets
# Behavior: identical to a generator function that yields each value

# Common patterns:
total = sum(x**2 for x in range(1000))              # no extra () needed inside sum()!
large = any(x > 100 for x in data)                 # short-circuits on first True
filtered = list(x for x in data if x.active)

# With multiple for clauses:
pairs = ((x, y) for x in range(3) for y in range(3) if x != y)
```

**Memory comparison (real numbers):**

```
Data: 1 million integers

list:   [x*2 for x in range(1_000_000)]  → sys.getsizeof ≈ 8.5 MB
gen:    (x*2 for x in range(1_000_000))  → sys.getsizeof ≈ 200 bytes

Processing 50GB CSV file:
  list(csv.reader(f))               → crashes at ~10GB RAM
  (row for row in csv.reader(f))    → ~1KB RAM constant
```

💡 **Hint:** When passing a generator expression as the sole argument to a function (`sum(...)`, `any(...)`, `max(...)`), you don't need an extra set of parentheses — `sum(x**2 for x in range(10))` not `sum((x**2 for x in range(10)))`. Both work, the extra parens are just noise.

📝 **Practice:** [generator expression / rewrite a list comprehension →](./practice.md#q9--gen-expression--rewrite-a-list-comprehension)

> [↑ Back to Top](#top)

---

<a id="6-yield-from--delegation"></a>
# 6. `yield from` — Delegation

`yield from` delegates iteration to another iterable, forwarding every value the sub-iterable produces. It's cleaner than a manual `for x in sub: yield x` loop, and it does much more than that under the hood.

```python
def chain_them(a, b, c):
    for x in a: yield x    # verbose — manual forwarding
    for x in b: yield x
    for x in c: yield x

# Identical using yield from — cleaner, more expressive:
def chain_them(a, b, c):
    yield from a
    yield from b
    yield from c

# Works with any iterable — including recursive generators:
def flatten(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)   # ← recursive delegation
        else:
            yield item

list(flatten([1, [2, [3, 4], 5], 6]))
# [1, 2, 3, 4, 5, 6]
```

**`yield from` also transparently forwards `send()`, `throw()`, and `close()`** — critical for coroutine chaining. When you `send(value)` into a delegating generator, `yield from` passes it through to the sub-generator automatically. The same for exceptions thrown via `.throw()`.

🔍 **Good to know:** `yield from sub_gen` also captures the sub-generator's `return` value: `result = yield from sub_gen`. This is how `asyncio` coroutines chain results — each `await` is syntactic sugar over `yield from`.

📝 **Practice:** [yield from / flatten a nested list →](./practice.md#q10--yield-from--flatten-a-nested-list)

> [↑ Back to Top](#top)

---

<a id="7-send--generators-as-coroutines"></a>
# 7. `send()` — Generators as Coroutines

A regular generator is a one-way channel: it produces values, you consume them. With `send()`, a generator becomes a **two-way channel** — it can both produce values (via `yield`) and receive values (via the value of the `yield` expression).

```python
def accumulator():
    """Receive numbers, yield running total."""
    total = 0
    while True:
        value = yield total    # ← yield sends total OUT, receives new value IN
        if value is None:
            break
        total += value

acc = accumulator()
next(acc)       # ← MUST prime the generator first (advance to first yield)
                #   returns 0 (initial total)

acc.send(10)    # sends 10 in, total becomes 10, yields 10
acc.send(20)    # sends 20 in, total becomes 30, yields 30
acc.send(5)     # sends 5  in, total becomes 35, yields 35
```

**Rules:**
```
next(gen)      ← equivalent to gen.send(None)
gen.send(val)  ← must call next() first to prime (advance to first yield)
gen.throw(exc) ← inject an exception at the yield point
gen.close()    ← throw GeneratorExit into the generator
```

**Using `send()` for a streaming averager:**

```python
def streaming_average():
    count = 0
    total = 0.0
    avg   = None
    while True:
        value = yield avg
        if value is None:
            return avg
        count += 1
        total += value
        avg    = total / count

avg = streaming_average()
next(avg)            # prime
avg.send(10)   # → 10.0
avg.send(20)   # → 15.0
avg.send(30)   # → 20.0
```

⚠️ **Common mistake — calling `send()` before `next()`:** `gen.send(value)` before the generator has been primed raises `TypeError: can't send non-None value to a just-started generator`. Always call `next(gen)` (or `gen.send(None)`) first to advance to the first `yield`. If you write generator-based coroutines frequently, wrap them in a `@coroutine` decorator that primes automatically.

💡 **Hint:** In modern Python, `async def` / `await` coroutines (section 12) handle the priming and chaining automatically. `send()`-based generators are still useful for pure-Python coroutine patterns and streaming data processors, but `asyncio` is the preferred model for I/O concurrency.

📝 **Practice:** [send() / running_average coroutine →](./practice.md#q12--send--running_average-coroutine)

> [↑ Back to Top](#top)

---

<a id="8-generator-pipelines--streaming-etl"></a>
# 8. Generator Pipelines — Streaming ETL

The true power of generators comes from **composition** — chaining generators into pipelines where each stage processes one item at a time. Memory usage is O(1) at every stage regardless of the total dataset size.

```
DATA SOURCE → FILTER → TRANSFORM → AGGREGATE
Each arrow is a generator. Memory is O(1) at every stage.
```

```python
from pathlib import Path


# Stage 1: Read lines from file (source)
def read_lines(filepath):
    with open(filepath, encoding="utf-8") as f:
        yield from f   # one line at a time

# Stage 2: Parse JSON per line
def parse_json(lines):
    import json
    for line in lines:
        try:
            yield json.loads(line.strip())
        except json.JSONDecodeError:
            pass   # skip malformed lines

# Stage 3: Filter
def only_errors(events):
    for event in events:
        if event.get("level") == "ERROR":
            yield event

# Stage 4: Extract fields
def extract_fields(events):
    for event in events:
        yield {
            "timestamp": event["ts"],
            "service":   event["service"],
            "message":   event["msg"],
        }

# Compose the pipeline:
def process_log(filepath):
    pipeline = extract_fields(
                   only_errors(
                       parse_json(
                           read_lines(filepath)
                       )
                   )
               )
    for record in pipeline:
        insert_to_db(record)
```

**What happens in memory at any given moment:**
```
read_lines:     reads 1 line → yields 1 line (string, ~200 bytes)
parse_json:     receives 1 string → yields 1 dict (~500 bytes)
only_errors:    receives 1 dict → either yields it or drops it
extract_fields: receives 1 dict → yields 1 smaller dict

TOTAL MEMORY: ~2KB regardless of whether the file is 1MB or 100GB
```

💡 **Hint:** Each generator in the pipeline only runs when the consumer (the `for record in pipeline` loop) calls `next()`. The pull propagates backward: consuming from `extract_fields` pulls from `only_errors`, which pulls from `parse_json`, which pulls from `read_lines`. One item flows through all stages before the next item is fetched from the source.

📝 **Practice:** [pipeline / 3-stage CSV pipeline →](./practice.md#q14--pipeline--3-stage-csv-pipeline)

> [↑ Back to Top](#top)

---

<a id="9-itertools--the-standard-library-power-tools"></a>
# 9. itertools — The Standard Library Power Tools

`itertools` is the standard library module for composable iterator building blocks. Every function returns a lazy iterator — no computation happens until you pull values. Think of them as LEGO pieces: small, efficient, and designed to snap together.

---

<a id="infinite-iterators"></a>
## Infinite Iterators

These never stop producing values — always pair with `islice`, `takewhile`, or a `break` condition:

```python
from itertools import count, cycle, repeat

count(10)          # 10, 11, 12, 13, ... (infinite, integer by default)
count(0, 0.5)      # 0, 0.5, 1.0, 1.5, ... (with step)
cycle([1, 2, 3])   # 1, 2, 3, 1, 2, 3, ... (infinite cycle over iterable)
repeat(42)         # 42, 42, 42, ... (infinite)
repeat(42, 5)      # 42, 42, 42, 42, 42 (exactly 5 times)
```

⚠️ **Common mistake — iterating `count()` or `cycle()` directly:** `list(count(10))` runs forever and exhausts memory. Always wrap with `islice(count(10), N)` or `takewhile(condition, count(10))`.

---

<a id="terminating-iterators"></a>
## Terminating Iterators

These consume finite iterables and produce a transformed or filtered result — all lazily:

```python
from itertools import (
    chain, islice,
    takewhile, dropwhile,
    groupby, accumulate, pairwise,
    batched,  # Python 3.12+
)

# chain: concatenate iterables without materializing
list(chain([1, 2], [3, 4], [5]))              # [1, 2, 3, 4, 5]
list(chain.from_iterable([[1,2],[3,4]]))       # [1, 2, 3, 4]

# islice: slice without materializing — works on infinite iterators
list(islice(count(0), 5))                     # [0, 1, 2, 3, 4]
list(islice(range(100), 10, 20, 2))           # [10, 12, 14, 16, 18]

# takewhile / dropwhile — predicate-based slice
list(takewhile(lambda x: x < 5, [1, 2, 3, 7, 1]))  # [1, 2, 3]
list(dropwhile(lambda x: x < 5, [1, 2, 3, 7, 1]))  # [7, 1]

# groupby: group consecutive equal elements
# *** MUST sort first — groupby only groups consecutive runs ***
data = sorted([("a", 1), ("b", 2), ("a", 3)], key=lambda x: x[0])
for key, group in groupby(data, key=lambda x: x[0]):
    print(key, list(group))
# a [('a', 1), ('a', 3)]
# b [('b', 2)]

# accumulate: running aggregation
list(accumulate([1, 2, 3, 4]))              # [1, 3, 6, 10]  (running sum)
list(accumulate([1, 2, 3, 4], max))         # [1, 2, 3, 4]  (running max)

# pairwise (Python 3.10+): overlapping pairs
list(pairwise([1, 2, 3, 4]))               # [(1,2), (2,3), (3,4)]

# batched (Python 3.12+): fixed-size non-overlapping chunks
list(batched([1,2,3,4,5], 2))              # [(1,2), (3,4), (5,)]
```

⚠️ **Common mistake — `groupby` without sorting:** `groupby` groups only **consecutive** equal elements. If equal elements are scattered throughout the input, you get multiple separate groups for them. Always `sorted(data, key=keyfunc)` before `groupby(data, key=keyfunc)`.

---

<a id="zip_longest--zip-unequal-sequences"></a>
## zip_longest — Zip Unequal Sequences

Regular `zip()` stops at the shortest sequence — elements from the longer sequence are silently dropped. `zip_longest` continues to the end of the longest, filling missing values with a `fillvalue`.

```python
from itertools import zip_longest

names  = ["Alice", "Bob", "Charlie"]
scores = [95, 87]   # shorter!

# Regular zip — stops at length 2, Charlie is silently dropped:
list(zip(names, scores))
# [('Alice', 95), ('Bob', 87)]

# zip_longest — fills missing with fillvalue:
list(zip_longest(names, scores, fillvalue=0))
# [('Alice', 95), ('Bob', 87), ('Charlie', 0)]

list(zip_longest(names, scores, fillvalue="N/A"))
# [('Alice', 95), ('Bob', 87), ('Charlie', 'N/A')]
```

💡 **Hint:** Use `zip_longest` whenever pairing sequences that might have different lengths and you can't afford to silently drop data — e.g., pairing database rows with configuration defaults, merging time series with different date ranges.

---

<a id="combinatoric-iterators"></a>
## Combinatoric Iterators

These generate all possible combinations, permutations, or products of input elements — lazily:

```python
from itertools import product, permutations, combinations, combinations_with_replacement

list(product('AB', repeat=2))                   # [AA, AB, BA, BB]
list(permutations('ABC', 2))                    # [AB, AC, BA, BC, CA, CB]
list(combinations('ABC', 2))                    # [AB, AC, BC]
list(combinations_with_replacement('AB', 2))    # [AA, AB, BB]
```

🔍 **Good to know:** These combinatoric iterators can produce enormous numbers of results — `permutations('ABCDEFGHIJ')` generates 3,628,800 tuples. Because they're lazy, you won't run out of memory building the full list (unless you materialise it). Use `islice` to sample just the first N.

📝 **Practice:** [itertools.chain / combine two lists lazily →](./practice.md#q16--itertoolschain--combine-two-lists-lazily)

> [↑ Back to Top](#top)

---

<a id="10-infinite-sequences"></a>
# 10. Infinite Sequences

Because generators produce values on demand, they can represent sequences with no end — as long as the consumer controls how many values to take. This is impossible with lists but trivial with generators.

```python
def naturals():
    """Infinite sequence: 1, 2, 3, 4, ..."""
    n = 1
    while True:
        yield n
        n += 1

def fibonacci():
    """Infinite Fibonacci sequence."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

def primes():
    """Infinite prime generator (Sieve of Eratosthenes variant)."""
    composites = {}
    n = 2
    while True:
        if n not in composites:
            yield n
            composites[n * n] = [n]
        else:
            for p in composites[n]:
                composites.setdefault(p + n, []).append(p)
            del composites[n]
        n += 1

# Safely consume infinite generators with islice:
from itertools import islice

list(islice(fibonacci(), 10))   # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
list(islice(primes(), 10))      # [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

💡 **Hint:** `islice` is the safe way to take the first N items from any infinite generator. `next(gen)` takes exactly one. `takewhile(condition, gen)` takes until the condition fails. Never pass an infinite generator directly to `list()`, `sum()`, `max()`, or any function that tries to consume it fully.

📝 **Practice:** [infinite generator / fibonacci with islice →](./practice.md#q19--infinite-generator--fibonacci-with-islice)

> [↑ Back to Top](#top)

---

<a id="11-return-inside-a-generator"></a>
# 11. `return` Inside a Generator

A generator function can contain `return`. It doesn't return a value in the normal sense — instead it raises `StopIteration` with the returned value attached as `StopIteration.value`. The `for` loop and most consumers silently discard this value, but you can capture it manually.

```python
def bounded_count(start, stop):
    n = start
    while n <= stop:
        yield n
        n += 1
    return "finished"   # ← raises StopIteration(value="finished")

gen = bounded_count(1, 3)
list(gen)   # [1, 2, 3]  — StopIteration.value is "finished" but list() ignores it

# To capture the return value, catch StopIteration manually:
gen = bounded_count(1, 3)
while True:
    try:
        val = next(gen)
        print(val)
    except StopIteration as e:
        print(f"Generator finished with: {e.value}")   # "finished"
        break
```

**`yield from` captures the return value automatically:**

```python
def delegating():
    result = yield from bounded_count(1, 3)  # ← captures "finished"
    print(f"Sub-generator returned: {result}")
    yield 99

g = delegating()
list(g)   # [1, 2, 3, 99]  — also prints "Sub-generator returned: finished"
```

🔍 **Good to know:** This is the mechanism `asyncio` uses to pass values between coroutines — when an `async def` function `return`s a value, it becomes the result of the `await` expression in the caller. The machinery is `return` → `StopIteration.value` → captured by `yield from`.

📝 **Practice:** [return value / StopIteration.value →](./practice.md#q20--return-value--stopiterationvalue)

> [↑ Back to Top](#top)

---

<a id="12-async-generators-python-36"></a>
# 12. Async Generators (Python 3.6+)

An **async generator** is an `async def` function that contains `yield`. It combines the lazy iteration of generators with the non-blocking I/O of coroutines — ideal for streaming data from async sources (databases, APIs, message queues) one item at a time.

```python
import asyncio

async def async_range(start, stop):
    """Async generator — yields values with async operations between."""
    for i in range(start, stop):
        await asyncio.sleep(0)   # simulate async I/O (DB fetch, API call, etc.)
        yield i

async def main():
    async for n in async_range(0, 5):   # async for — awaits each yield
        print(n)

    # Or use async comprehension:
    result = [n async for n in async_range(0, 5)]
    print(result)   # [0, 1, 2, 3, 4]

asyncio.run(main())
```

**Real use: async database cursor — one row at a time:**

```python
async def fetch_in_batches(query, batch_size=100):
    """Yield one row at a time from an async DB cursor."""
    async with db.transaction():
        cursor = await db.execute(query)
        while True:
            row = await cursor.fetchone()
            if row is None:
                return
            yield row

async def process_all_users():
    async for user in fetch_in_batches("SELECT * FROM users"):
        await send_email(user)   # memory: O(1) at any time
```

⚠️ **Common mistake — using `async for` outside `async def`:** Async generators must be consumed with `async for` inside an `async def` function. You can't use them in a regular synchronous context. Use `asyncio.run(main())` to enter an async context from synchronous code.

🔍 **Good to know:** Async generators don't support `send()` or `throw()` in the same way as synchronous generators — they're designed for one-way streaming (producing values). For full two-way async communication, use `asyncio.Queue`.

📝 **Practice:** [async generator / paginated API results →](./practice.md#q21--async-generator--paginated-api-results)

> [↑ Back to Top](#top)

---

<a id="13-gotchas-and-anti-patterns"></a>
# 13. Gotchas and Anti-Patterns

These five mistakes appear regularly in generator-related code reviews. Each one is subtle enough to slip through without an obvious error message.

---

<a id="gotcha-generators-exhaust-after-one-pass"></a>
## Gotcha: Generators Exhaust After One Pass

```python
gen = (x**2 for x in range(5))

list(gen)   # [0, 1, 4, 9, 16]   ← consumed
list(gen)   # []                  ← EMPTY! generator exhausted

# Fix: wrap in a function so each call produces a fresh generator:
def squares():
    return (x**2 for x in range(5))

list(squares())   # [0, 1, 4, 9, 16]
list(squares())   # [0, 1, 4, 9, 16]  ← fresh generator each call
```

⚠️ **Common mistake:** Storing a generator in a variable and using it in two places. The second use silently gets nothing. If you need to iterate multiple times, materialise with `list()` once.

---

<a id="gotcha-generator-returns-without-processing"></a>
## Gotcha: Generator Returns Without Processing

```python
# ❌ Looks like it returns a list but returns a generator:
def get_even_numbers(data):
    return (x for x in data if x % 2 == 0)   # generator, data NOT processed yet

result = get_even_numbers([1, 2, 3, 4])
# data is NOT processed at this point! The caller must iterate result.
for n in result:   # processing happens here, not above
    print(n)
```

💡 **Hint:** This is a feature, not a bug — but it's surprising until you internalise lazy evaluation. Document generator-returning functions clearly so callers know they must iterate the result.

---

<a id="gotcha-late-binding-in-generator-expressions"></a>
## Gotcha: Late Binding in Generator Expressions

```python
# ❌ Classic late-binding trap:
fns = [lambda: i for i in range(3)]
[f() for f in fns]   # [2, 2, 2]  ← all captured the SAME 'i' variable!

# ✅ Fix: bind at creation time using default argument:
fns = [lambda i=i: i for i in range(3)]
[f() for f in fns]   # [0, 1, 2]  ← each lambda has its own 'i'
```

This is the same late-binding trap covered in [04_functions — Closures](../04_functions/02_closures_decorators/01_closures_theory.md). All lambdas in the list share a reference to the same `i` cell — which holds `2` by the time any of them are called.

---

<a id="gotcha-no-len-or-indexing"></a>
## Gotcha: No len() or Indexing

```python
gen = (x for x in range(10))
len(gen)       # TypeError: object of type 'generator' has no len()
gen[3]         # TypeError: 'generator' object is not subscriptable

# Fix: convert if you need random access (accepting memory cost):
items = list(gen)
len(items)     # 10
items[3]       # 3
```

🔍 **Good to know:** If you just need a count without materialising, use `sum(1 for _ in gen)` — it consumes the generator without storing anything. But note: this exhausts the generator.

---

<a id="gotcha-closing-a-generator-early"></a>
## Gotcha: Closing a Generator Early

```python
def with_cleanup():
    try:
        yield 1
        yield 2
        yield 3
    finally:
        print("Cleanup!")   # runs when generator is closed or GC'd

gen = with_cleanup()
next(gen)       # → 1
gen.close()     # → prints "Cleanup!"  (injects GeneratorExit exception)
# Without gen.close(), Python calls it on GC — but timing is unpredictable.
# Use try/finally in generators that hold resources (file handles, locks).
```

💡 **Hint:** If a generator holds a resource (open file, database connection, lock), put cleanup in `finally`. Python guarantees `finally` runs when the generator is closed via `.close()` or garbage collected — but GC timing in CPython can be unpredictable in complex object graphs. Explicit `gen.close()` or a `with` statement is safer.

📝 **Practice:** [generator exhaustion demo →](./practice.md#q22--exhaustion--generator-exhaustion-demo)

> [↑ Back to Top](#top)

---

<a id="14-the-iterator-protocol-in-the-standard-library"></a>
# 14. The Iterator Protocol in the Standard Library

Understanding the protocol reveals why so many built-in types "just work" in `for` loops — some are iterables (have `__iter__` but not `__next__`), and some are full iterators (have both):

```
TYPE              __iter__   __next__   Notes
──────────────────────────────────────────────────────────────────
list              ✅          ❌         creates list_iterator on iter()
list_iterator     ✅          ✅
tuple             ✅          ❌
str               ✅          ❌         iterates characters
dict              ✅          ❌         iterates keys; iter(d) → dict_keyiterator
dict_keyiterator  ✅          ✅
file object       ✅          ✅         already an iterator (iter(f) returns self)
range             ✅          ❌         range_iterator on iter()
generator         ✅          ✅         already an iterator
zip               ✅          ✅         zip_iterator
enumerate         ✅          ✅
map               ✅          ✅
filter            ✅          ✅
```

**Why some types are iterable but not iterators (list, tuple, str, range):** These can be iterated many times. If they were their own iterators, the first `for` loop would exhaust them and a second `for` loop would yield nothing. By returning a new iterator object on each `iter()` call, they stay reusable.

**Why file objects and generators are their own iterators:** They represent one-pass streams — consuming position advances permanently. `iter(f)` returns `f` itself (already an iterator), reinforcing that you get one pass.

```python
from collections.abc import Iterator, Iterable

# Check at runtime:
isinstance([1,2,3], Iterable)    # True
isinstance([1,2,3], Iterator)    # False
isinstance(iter([1,2,3]), Iterator)  # True

# Any class implementing both __iter__ and __next__ satisfies Iterator
```

🔍 **Good to know:** `collections.abc.Iterator` and `collections.abc.Iterable` are the abstract base classes for the protocol. You can use `isinstance(obj, Iterator)` to check if something is a full iterator, or register your own class as a virtual subclass if it implements the protocol without inheriting.

📝 **Practice:** [collections.abc / classify iterables and iterators →](./practice.md#q23--collectionsabc--classify-iterables-and-iterators)

> [↑ Back to Top](#top)

---

<a id="summary"></a>
# Summary

```
CONCEPT            DESCRIPTION
──────────────────────────────────────────────────────────────────────
Iterable           Has __iter__() → returns an iterator
Iterator           Has __iter__() + __next__() → raises StopIteration when done
Generator function Contains yield → returns a generator object on call
Generator object   Lazy iterator: frame suspended on heap, computes on demand
yield              Suspend function, produce value, wait for next()
yield from         Delegate to sub-iterable, forward send/throw/return
send(val)          Send value INTO generator at current yield point
Generator pipeline Chain generators for O(1) memory streaming ETL
Generator expr     (expr for x in it if cond) — lazy comprehension
itertools          Standard library of composable lazy iterator utilities
Async generator    async def with yield — for async one-pass streaming
```

---

<a id="navigation"></a>
# 🔁 Navigation

**[🏠 Back to Python Mastery README](../README.md)**

| | |
|---|---|
| ⬅ Prev Module | [10 — Decorators](../10_decorators/theory.md) |
| ➡ Next Module | [12 — Context Managers](../12_context_managers/theory.md) |

**This folder:**
[theory.md](./theory.md) · [cheetsheet.md](./cheetsheet.md) · [interview.md](./interview.md) · [practice.md](./practice.md) · [04_generator_patterns.md](./04_generator_patterns.md)

**Related modules:**
[10 — Decorators](../10_decorators/theory.md) · [12 — Context Managers](../12_context_managers/theory.md) · [13 — Concurrency](../13_concurrency/theory.md) · [24 — Async Python](../24_async_python_for_ai/theory.md)

**Jump to specific topics:**
[Why Generators Are Lazy](#why-generators-are-lazy--the-memory-story) · [Generator Pipelines](#8-generator-pipelines--streaming-etl) · [yield from](#6-yield-from--delegation) · [send() coroutines](#7-send--generators-as-coroutines) · [itertools groupby](#terminating-iterators) · [Async Generators](#12-async-generators-python-36) · [Gotchas](#13-gotchas-and-anti-patterns)
