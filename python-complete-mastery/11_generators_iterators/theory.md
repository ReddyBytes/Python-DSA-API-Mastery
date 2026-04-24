# 🔄 Iterators & Generators — Theory

> *"A generator doesn't compute the next value until you ask for it.*
> *That's the entire secret to processing infinite data in constant memory."*

---

## 🎬 The Problem: 50 Million Records, 4GB RAM

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

## 🔗 Chapter 1: The Iteration Protocol

When you write `for x in something`, Python runs a precise protocol:

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

# The for loop is equivalent to:
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

---

## 🏗️ Chapter 2: Building a Custom Iterator Class

Understanding the protocol from scratch:

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

```python
class NumberRange:
    """Iterable (can be looped multiple times)."""
    def __init__(self, start, stop):
        self.start = start
        self.stop  = stop

    def __iter__(self):
        return NumberRangeIterator(self.start, self.stop)  # ← new iterator each time

class NumberRangeIterator:
    """Iterator (single-use, tracks position)."""
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

---

## ✨ Chapter 3: Generator Functions — yield

Writing custom iterators as classes is verbose. **Generator functions** let you write the same logic with `yield`:

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

**Generator functions vs regular functions — the key difference:**

```python
def regular():
    return 1    # executes body, returns 1, done

def generator():
    yield 1     # body NOT executed at call time
    yield 2     # execution is suspended after each yield


# Calling:
regular()      # → 1          (runs the body)
generator()    # → <generator object>  (body NOT run yet!)

g = generator()
next(g)   # → 1   (runs until first yield, pauses)
next(g)   # → 2   (resumes from after first yield, pauses at second)
next(g)   # → StopIteration (fell off the end of the function)
```

> 📝 **Practice:** [Q33 · generators-basics](../python_practice_questions_100.md#q33--normal--generators-basics) · [Q34 · yield](../python_practice_questions_100.md#q34--thinking--yield) · [Q93 · predict-output-generator](../python_practice_questions_100.md#q93--logical--predict-output-generator)


---

## 🧠 Chapter 4: How yield Suspends Execution — The Frame Model

This is the critical conceptual piece. When a generator is suspended at a `yield`, Python preserves the entire execution state as a **heap-allocated frame** (see [memory layout → stack frame lifecycle](../01.1_memory_management/theory.md#-stack-frame--what-happens-on-each-call)):

```
GENERATOR FRAME (suspended):
┌────────────────────────────────────────┐
│ code pointer → line 4 (after yield)   │
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
    yield 1                    # ← SUSPEND here. 'x' and 'print state' preserved.
    print("C: resumed after first yield")
    x += 5
    print(f"D: x is now {x}")
    yield 2                    # ← SUSPEND here.
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

**Memory model — why this enables lazy evaluation:**

```
Regular list comprehension:
  [f(x) for x in range(1_000_000)]
  → all 1,000,000 results computed immediately
  → all stored in RAM simultaneously

Generator expression:
  (f(x) for x in range(1_000_000))
  → zero results computed at creation
  → each next() computes ONE result, uses it, discards it
  → constant memory regardless of input size
```

> 📝 **Practice:** [Q35 · generator-exhaustion](../python_practice_questions_100.md#q35--critical--generator-exhaustion)

---

## Why Generators Are Lazy — The Memory Story

Lazy evaluation means: **compute only when asked, not all at once**.

A list evaluates everything immediately and stores all values in memory.
A generator evaluates one item at a time and stores nothing except its suspended frame.

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

# Lazy: same sequence, but 200 bytes total
lazy = (x for x in range(1_000_000))
print(sys.getsizeof(lazy))       # ~112 bytes
```

> 📝 **Practice:** [Q76 · explain-generators](../python_practice_questions_100.md#q76--interview--explain-generators)


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

---

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
data = list(gen_function())  # materialize it once
```

---

## ⚡ Chapter 5: Generator Expressions

The generator equivalent of list comprehensions:

```python
# List comprehension — evaluates eagerly, stores all in RAM:
squares_list = [x**2 for x in range(1_000_000)]   # ~8MB in memory

# Generator expression — evaluates lazily, no storage:
squares_gen  = (x**2 for x in range(1_000_000))   # ~200 bytes

# Syntax: parentheses instead of brackets
# Behavior: identical to a generator function that yields each value

# Common patterns:
total = sum(x**2 for x in range(1000))              # no extra [] needed!
large = any(x > 100 for x in data)                 # short-circuits
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
  list(csv.reader(f))     → crashes at ~10GB RAM
  (row for row in csv.reader(f))  → ~1KB RAM constant
```

---

## 🔀 Chapter 6: `yield from` — Delegation

`yield from` delegates to another iterable, forwarding every value:

```python
def chain_them(a, b, c):
    for x in a: yield x    # verbose
    for x in b: yield x
    for x in c: yield x

# ↓ Identical using yield from:
def chain_them(a, b, c):
    yield from a
    yield from b
    yield from c

# Works with any iterable:
def flatten(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)   # recursive delegation!
        else:
            yield item

list(flatten([1, [2, [3, 4], 5], 6]))
# [1, 2, 3, 4, 5, 6]
```

**`yield from` also transparently forwards `send()` and `throw()`** — critical for coroutine chaining. More on this in Chapter 8.

---

## 📡 Chapter 7: `send()` — Generators as Coroutines

A generator can also **receive** values via `send()`. This makes generators two-way communication channels:

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
next(acc)       # ← MUST prime the generator (advance to first yield)
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

> 📝 **Practice:** [Q96 · debug-generator-send](../python_practice_questions_100.md#q96--debug--debug-generator-send)

---

## 🔧 Chapter 8: Generator Pipelines — Streaming ETL

The true power of generators: compose them into pipelines where each stage processes one item at a time.

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

> 📝 **Practice:** [Q89 · pipeline-scenario](../python_practice_questions_100.md#q89--design--pipeline-scenario)


**What happens in memory:**
```
read_lines:     reads 1 line → yields 1 line (string, ~200 bytes)
parse_json:     receives 1 string → yields 1 dict (~500 bytes)
only_errors:    receives 1 dict → either yields it or drops it
extract_fields: receives 1 dict → yields 1 smaller dict

TOTAL MEMORY: ~2KB regardless of whether the file is 1MB or 100GB
```

---

## 🛠️ Chapter 9: `itertools` — The Standard Library Power Tools

`itertools` gives you composable building blocks for iterators:

### Infinite iterators

```python
from itertools import count, cycle, repeat

count(10)          # 10, 11, 12, 13, ... (infinite)
count(0, 0.5)      # 0, 0.5, 1.0, 1.5, ... (with step)
cycle([1, 2, 3])   # 1, 2, 3, 1, 2, 3, ... (infinite cycle)
repeat(42)         # 42, 42, 42, ... (infinite)
repeat(42, 5)      # 42, 42, 42, 42, 42 (exactly 5 times)
```

### Terminating iterators

```python
from itertools import (
    chain, chain.from_iterable, islice,
    takewhile, dropwhile, filterfalse,
    starmap, compress, groupby,
    zip_longest, accumulate, pairwise,
    batched,  # Python 3.12+
)

# chain: concatenate iterables
list(chain([1, 2], [3, 4], [5]))      # [1, 2, 3, 4, 5]
list(chain.from_iterable([[1,2],[3,4]]))  # [1, 2, 3, 4]

# islice: slice without materializing
list(islice(count(0), 5))             # [0, 1, 2, 3, 4]
list(islice(range(100), 10, 20, 2))   # [10, 12, 14, 16, 18]

# takewhile / dropwhile
list(takewhile(lambda x: x < 5, [1, 2, 3, 7, 1]))  # [1, 2, 3]
list(dropwhile(lambda x: x < 5, [1, 2, 3, 7, 1]))  # [7, 1]

# groupby: group consecutive equal elements (sort first!)
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

# batched (Python 3.12+): fixed-size chunks
list(batched([1,2,3,4,5], 2))              # [(1,2), (3,4), (5,)]
```

---

### `itertools.zip_longest` — Zip Sequences of Different Lengths

Regular `zip()` stops at the shortest sequence.
`zip_longest` continues to the end of the longest, filling missing values.

```python
from itertools import zip_longest

names  = ["Alice", "Bob", "Charlie"]
scores = [95, 87]   # shorter!

# Regular zip — stops at length 2:
list(zip(names, scores))
# [('Alice', 95), ('Bob', 87)]  ← Charlie dropped!

# zip_longest — fills missing with fillvalue:
list(zip_longest(names, scores, fillvalue=0))
# [('Alice', 95), ('Bob', 87), ('Charlie', 0)]

# Custom fill value:
list(zip_longest(names, scores, fillvalue="N/A"))
# [('Alice', 95), ('Bob', 87), ('Charlie', 'N/A')]
```

Use `zip_longest` whenever pairing sequences that might have different lengths and you can't afford to silently drop data.

### Combinatoric iterators

```python
from itertools import product, permutations, combinations, combinations_with_replacement

list(product('AB', repeat=2))          # AA AB BA BB
list(permutations('ABC', 2))           # AB AC BA BC CA CB
list(combinations('ABC', 2))           # AB AC BC
list(combinations_with_replacement('AB', 2))  # AA AB BB
```

---

## ♾️ Chapter 10: Infinite Sequences

Generators can be infinite — they only produce as much as the consumer requests:

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
    """Infinite prime number generator (Sieve of Eratosthenes variant)."""
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

---

## 🔁 Chapter 11: `return` Inside a Generator

A generator function can have `return`. It raises `StopIteration` with the returned value:

```python
def bounded_count(start, stop):
    n = start
    while n <= stop:
        yield n
        n += 1
    return "finished"   # ← raises StopIteration(value="finished")

gen = bounded_count(1, 3)
list(gen)   # [1, 2, 3]  — StopIteration.value is "finished" but silently ignored by list()

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

**`yield from` captures the return value:**

```python
def delegating():
    result = yield from bounded_count(1, 3)  # ← captures "finished"
    print(f"Sub-generator returned: {result}")
    yield 99

g = delegating()
list(g)   # [1, 2, 3, 99]  — also prints "Sub-generator returned: finished"
```

---

## ⚡ Chapter 12: Async Generators (Python 3.6+)

For async iteration — reading from async sources one item at a time:

```python
import asyncio

async def async_range(start, stop):
    """Async generator — yields values with async operations between."""
    for i in range(start, stop):
        await asyncio.sleep(0)   # simulate async I/O
        yield i

async def main():
    async for n in async_range(0, 5):   # async for loop
        print(n)

    # Or use async comprehension:
    result = [n async for n in async_range(0, 5)]
    print(result)   # [0, 1, 2, 3, 4]

asyncio.run(main())
```

**Real use: async database cursor:**

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

---

## 🚧 Chapter 13: Gotchas and Anti-Patterns

### Gotcha 1 — Generators are exhausted after one pass

```python
gen = (x**2 for x in range(5))

list(gen)   # [0, 1, 4, 9, 16]   ← consumed
list(gen)   # []                  ← EMPTY! generator exhausted

# Fix: re-create or use a function:
def squares():
    return (x**2 for x in range(5))

list(squares())   # [0, 1, 4, 9, 16]
list(squares())   # [0, 1, 4, 9, 16]  ← fresh generator each call
```

### Gotcha 2 — Generator inside function returns immediately

```python
# ❌ Looks like it returns a list but returns a generator:
def get_even_numbers(data):
    return (x for x in data if x % 2 == 0)   # returns generator, data NOT processed yet

# The caller needs to iterate it. If they don't, nothing happens.
result = get_even_numbers([1, 2, 3, 4])
# data is NOT processed at this point!
for n in result:   # processing happens here
    print(n)
```

### Gotcha 3 — Late binding in generator expressions

```python
# ❌ Classic late-binding trap:
fns = [lambda: i for i in range(3)]
[f() for f in fns]   # [2, 2, 2]  ← all captured the SAME 'i'!

# ✅ Fix: bind at creation time:
fns = [lambda i=i: i for i in range(3)]
[f() for f in fns]   # [0, 1, 2]  ← each lambda has its own 'i'
```

### Gotcha 4 — Can't use `len()` or `__getitem__` on generators

```python
gen = (x for x in range(10))
len(gen)       # TypeError: object of type 'generator' has no len()
gen[3]         # TypeError: 'generator' object is not subscriptable

# Fix: convert if you need random access (accepting memory cost):
items = list(gen)
len(items)     # 10
items[3]       # 3
```

### Gotcha 5 — Closing a generator early

```python
def with_cleanup():
    try:
        yield 1
        yield 2
        yield 3
    finally:
        print("Cleanup!")   # ← runs when generator is garbage collected or .close() called

gen = with_cleanup()
next(gen)       # → 1
gen.close()     # → "Cleanup!"  (injects GeneratorExit)
# Without gen.close(), Python calls it on GC. Use try/finally for resources.
```

---

## 🧠 Chapter 14: The Iterator Protocol in the Standard Library

Understanding the protocol reveals why these all "just work" in `for` loops:

```
TYPE            __iter__    __next__    Notes
────────────────────────────────────────────────────────────────
list            ✅           ❌         creates list_iterator on iter()
list_iterator   ✅           ✅
tuple           ✅           ❌
str             ✅           ❌         iterates characters
dict            ✅           ❌         iterates keys; iter(d) → dict_keyiterator
file object     ✅           ✅         already an iterator (iter(f) returns self)
range           ✅           ❌         range_iterator on iter()
generator       ✅           ✅         already an iterator
zip             ✅           ✅         zip_iterator
enumerate       ✅           ✅
map             ✅           ✅
filter          ✅           ✅
```

---

## 🔥 Summary

```
CONCEPT            DESCRIPTION
──────────────────────────────────────────────────────────────────────
Iterable           Has __iter__() → returns an iterator
Iterator           Has __iter__() + __next__() → raises StopIteration when done
Generator function Contains yield → returns a generator object
Generator object   Lazy iterator: computes values on demand
yield              Suspend function, produce value, wait for next()
yield from         Delegate to sub-iterable, forward send/throw/return
send(val)          Send value INTO generator at current yield point
Generator pipeline Chain generators for O(1) memory streaming ETL
Generator expr     (expr for x in it if cond) — lazy comprehension
itertools          Standard library of composable iterator utilities
Async generator    async def with yield — for async iteration
```

---

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🔧 Pipeline Patterns | [generator_patterns.md](./generator_patterns.md) |
| ➡️ Next | [12 — Context Managers](../12_context_managers/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Decorators — Interview Q&A](../10_decorators/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Generator Patterns](./generator_patterns.md) · [Interview Q&A](./interview.md)
