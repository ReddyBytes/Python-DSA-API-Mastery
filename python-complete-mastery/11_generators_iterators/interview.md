# 🎯 Iterators & Generators — Interview Questions

> *"Generator questions test whether you understand lazy evaluation, Python's memory model,*
> *and whether you can design scalable data pipelines."*

---

## 📊 Question Map

```
LEVEL 1 — Junior (0–2 years)
  • Iterable vs Iterator distinction
  • What does yield do?
  • Generator vs list comprehension
  • How for loops work internally

LEVEL 2 — Mid-Level (2–5 years)
  • yield from delegation
  • send() and generators as coroutines
  • Generator pipelines
  • itertools
  • Memory comparison

LEVEL 3 — Senior (5+ years)
  • Custom iterator classes
  • Async generators
  • Generator return value and StopIteration
  • Pipeline architecture design
  • Gotchas: exhaustion, late binding, close()
```

---

## 🟢 Level 1 — Junior Questions

---

### Q1: What is the difference between an iterable and an iterator?

**Weak answer:** "Both can be used in for loops."

**Strong answer:**

> An **iterable** is any object that implements `__iter__()` and returns an iterator. A list, string, and dict are all iterables.
>
> An **iterator** implements both `__iter__()` AND `__next__()`. Calling `next()` returns the next value; when exhausted it raises `StopIteration`.
>
> All iterators are iterables. Not all iterables are iterators.

```python
lst = [1, 2, 3]
it  = iter(lst)   # creates a list_iterator

# list is iterable but NOT an iterator:
hasattr(lst, '__iter__')   # True
hasattr(lst, '__next__')   # False  ← no __next__

# list_iterator is BOTH:
hasattr(it, '__iter__')    # True
hasattr(it, '__next__')    # True

# Iterators are their own iterators:
it is iter(it)             # True  ← __iter__ returns self
```

> **Practical consequence:** you can loop over a list multiple times; you can loop over an iterator only once.

---

### Q2: What does `yield` do? How does it differ from `return`?

**Weak answer:** "yield returns a value without ending the function."

**Strong answer:**

> `return` terminates the function and returns a single value. `yield` **suspends** the function, returns a value, and preserves the entire execution state (local variables, instruction pointer). The next call to `next()` resumes execution from exactly where it stopped.

```python
def demonstrate():
    print("A")
    yield 1          # suspend here, return 1
    print("B")
    yield 2          # suspend here, return 2
    print("C")
    # implicit return → raises StopIteration

g = demonstrate()
next(g)   # prints "A", returns 1
next(g)   # prints "B", returns 2
next(g)   # prints "C", raises StopIteration
```

> Calling a generator function does **not** execute its body — it returns a generator object immediately. The body only runs when you call `next()`.

---

### Q3: What is a generator expression and when should you use it over a list comprehension?

**Strong answer:**

> A generator expression has the same syntax as a list comprehension but uses parentheses instead of brackets. It evaluates **lazily** — values are produced one at a time on demand, never all stored in memory simultaneously.

```python
# List comprehension — all 1M values in RAM immediately:
squares = [x**2 for x in range(1_000_000)]   # ~8MB

# Generator expression — zero values stored:
squares = (x**2 for x in range(1_000_000))   # ~200 bytes

# Use generators when:
# 1. You only need to iterate once
# 2. The dataset is large
# 3. You want to compose with other iterators

total = sum(x**2 for x in range(1_000_000))       # no intermediate list!
found = any(x > 100 for x in data)                # short-circuits early
```

> **Rule:** if you're passing directly to `sum()`, `any()`, `all()`, `max()`, `min()`, or a `for` loop — use a generator expression. Only use a list comprehension if you need the list itself (index access, multiple passes, `len()`).

---

### Q4: How does Python's `for` loop work internally?

**Strong answer:**

> Python's `for` loop calls the iteration protocol:
> 1. `iter(obj)` to get an iterator
> 2. `next(iterator)` in a loop until `StopIteration` is raised

```python
# for x in data: body
# ↓ is exactly equivalent to:

_iter = iter(data)
while True:
    try:
        x = next(_iter)
        # body
    except StopIteration:
        break
```

> This means **any object** that implements `__iter__` and `__next__` works in a `for` loop — lists, files, generators, custom classes, database cursors, network streams.

---

## 🔵 Level 2 — Mid-Level Questions

---

### Q5: What does `yield from` do?

**Weak answer:** "It yields from another iterable."

**Strong answer:**

> `yield from iterable` delegates to a sub-iterable, forwarding each value it produces. It also transparently passes through `send()`, `throw()`, and `close()` calls, and captures the sub-generator's `return` value.

```python
# Without yield from — verbose:
def chain(a, b):
    for x in a: yield x
    for x in b: yield x

# With yield from — clean:
def chain(a, b):
    yield from a
    yield from b

# Deep use: recursive flattening:
def flatten(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)   # recursive delegation
        else:
            yield item

list(flatten([1, [2, [3, 4]], 5]))   # [1, 2, 3, 4, 5]
```

> **Captures return value:**
> ```python
> result = yield from sub_generator()   # receives sub-generator's return value
> ```

---

### Q6: Explain `generator.send()`. When would you use it?

**Strong answer:**

> `send(value)` resumes a suspended generator and injects `value` as the result of the current `yield` expression. It makes generators two-way communication channels (coroutines).

```python
def accumulator():
    total = 0
    while True:
        value = yield total    # yield sends total OUT, receive new value IN
        if value is None:
            break
        total += value

acc = accumulator()
next(acc)        # MUST prime first (advance to first yield)
acc.send(10)     # → 10  (total = 10)
acc.send(20)     # → 30  (total = 30)
acc.send(5)      # → 35  (total = 35)
```

> **Rules:**
> - Must call `next(gen)` (or `gen.send(None)`) first to prime the generator
> - Sending a non-None value to an unprimed generator raises `TypeError`
> - Used in asyncio (Python's async is built on generators + send)

---

### Q7: How would you design a streaming pipeline for processing a 10GB log file?

**Weak answer:** "Read line by line and process each."

**Strong answer:**

> I'd chain generator functions where each stage processes one record at a time. Memory stays constant regardless of file size.

```python
def read_lines(path):
    """Stage 1: Source."""
    with open(path, encoding="utf-8") as f:
        yield from f

def parse_log(lines):
    """Stage 2: Parse."""
    import json
    for line in lines:
        try:
            yield json.loads(line.strip())
        except json.JSONDecodeError:
            pass

def filter_errors(records):
    """Stage 3: Filter."""
    for r in records:
        if r.get("level") == "ERROR":
            yield r

def enrich(records):
    """Stage 4: Transform."""
    for r in records:
        yield {**r, "host": socket.gethostname()}

# Wire pipeline — nothing runs yet:
pipeline = enrich(filter_errors(parse_log(read_lines("app.log"))))

# Trigger execution — one record in memory at any time:
for record in pipeline:
    insert_to_db(record)
```

> **Each stage:** reads 1 item from upstream, produces 0 or 1 items downstream. Total RAM used: O(1 record). Throughput: limited only by I/O speed.

---

### Q8: What are the most useful `itertools` functions?

**Strong answer:**

```python
from itertools import (
    chain, islice, takewhile, dropwhile,
    groupby, accumulate, product,
    combinations, permutations, count, cycle
)

# chain: concatenate iterables without building a list:
list(chain([1, 2], [3, 4], [5]))          # [1, 2, 3, 4, 5]

# islice: slice an infinite or large generator:
list(islice(count(0), 5))                 # [0, 1, 2, 3, 4]

# takewhile: consume until condition fails:
list(takewhile(lambda x: x < 5, [1,3,5,7]))  # [1, 3]

# groupby: group consecutive elements (sort first!):
data = [("a",1),("a",2),("b",3)]
for k, g in groupby(data, key=lambda x: x[0]):
    print(k, list(g))

# accumulate: running sum/max/product:
list(accumulate([1, 2, 3, 4]))            # [1, 3, 6, 10]

# product: cartesian product (nested loops replaced):
list(product("AB", repeat=2))            # AA AB BA BB

# combinations: choose k from n:
list(combinations([1,2,3], 2))           # [(1,2),(1,3),(2,3)]
```

---

### Q9: What is the memory difference between a list and a generator for large data?

**Strong answer:**

```python
import sys

# List: stores all N results immediately
squares_list = [x**2 for x in range(1_000_000)]
sys.getsizeof(squares_list)   # ~8.5 MB

# Generator: stores zero results (just the generator object)
squares_gen  = (x**2 for x in range(1_000_000))
sys.getsizeof(squares_gen)    # ~200 bytes

# For 50GB CSV file:
# list(csv.DictReader(f))              → crashes RAM
# (row for row in csv.DictReader(f))  → ~1KB constant

# Real production rule:
# If you process once, top-to-bottom → generator
# If you need multiple passes, random access, or len() → list
```

---

## 🔴 Level 3 — Senior Questions

---

### Q10: Write a custom iterator class that pages through an API.

**Strong answer:**

```python
import requests

class PaginatedAPI:
    """Iterator that fetches paginated results one page at a time."""

    def __init__(self, base_url, page_size=100):
        self.base_url  = base_url
        self.page_size = page_size
        self._page     = 1
        self._buffer   = []
        self._done     = False

    def __iter__(self):
        return self

    def __next__(self):
        if not self._buffer:
            if self._done:
                raise StopIteration
            self._fetch_page()

        if not self._buffer:
            raise StopIteration

        return self._buffer.pop(0)

    def _fetch_page(self):
        response = requests.get(
            self.base_url,
            params={"page": self._page, "per_page": self.page_size}
        ).json()

        self._buffer = response.get("items", [])
        self._done   = len(self._buffer) < self.page_size
        self._page  += 1

# Usage:
for user in PaginatedAPI("https://api.example.com/users"):
    process(user)   # never loads all users into memory
```

---

### Q11: How does Python's async machinery relate to generators?

**Strong answer:**

> Python's `asyncio` is built on top of generators. A coroutine (`async def`) is internally implemented as a generator that yields control to the event loop. `await expr` is equivalent to `yield from expr.__await__()`.

```python
# Simplified view of how asyncio works:

# async def fetch():
#     await asyncio.sleep(1)
#     return "result"

# Is roughly equivalent to:
def fetch():
    yield from asyncio.sleep(1).__await__()   # yield to event loop, resume when done
    return "result"

# The event loop calls next() on each coroutine.
# When a coroutine yields, the loop can run other coroutines.
# When the I/O completes, the loop sends() the result back.
```

> **Async generators** let you yield values from async functions:
> ```python
> async def stream_rows():
>     async for row in db.cursor.fetch():
>         yield row   # yield inside async def = async generator
> ```

---

### Q12: What is a generator's `return` value and how do you capture it?

**Strong answer:**

> A `return value` in a generator function raises `StopIteration(value)`. Normally `for` loops and `list()` silently discard this. To capture it:

```python
def bounded(n):
    for i in range(n):
        yield i
    return f"generated {n} values"   # raises StopIteration("generated 3 values")

# for loop discards return value:
for x in bounded(3):
    print(x)   # 0 1 2 — "generated 3 values" lost

# Capture manually:
gen = bounded(3)
while True:
    try:
        print(next(gen))
    except StopIteration as e:
        print(f"Done: {e.value}")   # "Done: generated 3 values"
        break

# yield from captures it:
def delegator():
    result = yield from bounded(3)   # captures "generated 3 values"
    print(f"Sub-generator said: {result}")
    yield 99

list(delegator())   # [0, 1, 2, 99], prints "Sub-generator said: generated 3 values"
```

---

### Q13: How would you make a pipeline restartable?

**Strong answer:**

> A generator is single-use. To restart, you need to either store results (defeats the purpose for large data) or use a **generator factory** — a callable that creates a fresh generator each time.

```python
# ❌ Single-use — can't restart:
gen = (x**2 for x in range(100))
list(gen)   # [0, 1, 4, ...]
list(gen)   # []  ← exhausted

# ✅ Factory — creates fresh generator on each call:
def squares():
    return (x**2 for x in range(100))

list(squares())   # [0, 1, 4, ...]
list(squares())   # [0, 1, 4, ...]  ← fresh each time

# For pipelines — wrap in a class with __iter__:
class Pipeline:
    def __init__(self, source_factory):
        self.source_factory = source_factory

    def __iter__(self):
        yield from self._process(self.source_factory())   # fresh source each time

    def _process(self, source):
        for item in source:
            if item % 2 == 0:
                yield item * 2

p = Pipeline(lambda: range(10))
list(p)   # [0, 4, 8, 12, 16]  first pass
list(p)   # [0, 4, 8, 12, 16]  second pass — works!
```

---

## ⚠️ Trap Questions

---

### Trap 1 — Generator exhaustion (used twice)

```python
gen = (x**2 for x in range(5))

result1 = list(gen)   # [0, 1, 4, 9, 16] ✓
result2 = list(gen)   # []  ← EMPTY! already exhausted

# Common mistake in tests:
def get_evens(data):
    return (x for x in data if x % 2 == 0)

gen = get_evens([1, 2, 3, 4])
print(sum(gen))   # 6 ✓
print(list(gen))  # [] ← same generator, already consumed by sum()

# Fix: use a function that creates a fresh generator:
def get_evens(data):
    return [x for x in data if x % 2 == 0]   # list: reusable
```

---

### Trap 2 — Forgetting to prime `send()`

```python
def my_gen():
    value = yield 0
    yield value * 2

g = my_gen()
g.send(10)   # TypeError: can't send non-None value to a just-started generator

# Must prime first:
g = my_gen()
next(g)       # ← prime: advances to first yield, returns 0
g.send(10)    # → 20  (resumes, value=10, yields 10*2)
```

---

### Trap 3 — `return` in generator doesn't work like you think

```python
def gen_with_return():
    yield 1
    return 42    # ← doesn't return 42 to the caller of next()!
    yield 2      # ← unreachable

g = gen_with_return()
next(g)   # → 1
next(g)   # → StopIteration: 42   ← 42 is in StopIteration.value, NOT returned!

# Common mistake:
result = list(gen_with_return())   # [1]
# result is [1], not [1, 42] — the return value is NOT yielded
```

---

### Trap 4 — Late binding in loops

```python
# ❌ All generators capture the SAME variable 'i':
gens = [count_from(i) for i in range(3)]   # i is a shared variable!
# When you consume gens[0] later, i might have changed

# ✅ Fix — capture the current value:
gens = [count_from(start=i) for i in range(3)]  # pass as argument (bound at creation)
```

---

### Trap 5 — Generator inside `if __name__ == "__main__"` vs module level

```python
# ❌ Generator created at module level but never consumed:
import mymodule   # mymodule.py has:  gen = (compute(x) for x in data)
# gen is created (tiny), but compute() never runs until iteration
# This is actually fine! But confuses people who expect side effects to run.

# ❌ Worse: generator with side effects silently never runs:
gen = (print(x) for x in range(3))   # nothing printed yet!
# Only prints when you iterate:
list(gen)   # 0  1  2
```

---

## 🔥 Rapid-Fire Revision

```
Q: Iterable vs Iterator?
A: Iterable has __iter__(). Iterator has __iter__() + __next__().
   All iterators are iterables. Not vice versa.

Q: What does a generator function return when called?
A: A generator object (immediately, without executing the body).

Q: When does the body of a generator function execute?
A: When next() is called on the generator object.

Q: What raises StopIteration?
A: __next__() when exhausted, or 'return' in a generator function.

Q: Generator expression syntax?
A: (expr for x in iterable if condition) — parens not brackets.

Q: What does yield from do?
A: Delegates to sub-iterable, forwards send/throw/close,
   captures sub-generator's return value.

Q: How to prime a generator for send()?
A: Call next(gen) or gen.send(None) first.

Q: Can you iterate a generator twice?
A: No. Generators are single-use. Create a factory function to restart.

Q: What is islice() for?
A: Safely slice infinite or large generators without materializing.
   from itertools import islice; list(islice(gen, 10))

Q: How does async/await relate to generators?
A: Coroutines are implemented on top of generators.
   'await expr' ≈ 'yield from expr.__await__()'
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🔧 Pipeline Patterns | [generator_patterns.md](./generator_patterns.md) |
| ➡️ Next | [12 — Context Managers](../12_context_managers/theory.md) |
