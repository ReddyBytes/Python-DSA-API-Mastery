# ⚡ Iterators & Generators — Cheatsheet

> Quick reference: iteration protocol, yield, generator expressions, yield from, send, itertools, gotchas.

---

## 🔗 Iteration Protocol

```
ITERABLE  → has __iter__() → returns an iterator
ITERATOR  → has __iter__() + __next__() → raises StopIteration when done

All iterators are iterables. Not all iterables are iterators.

for x in obj:         →  _it = iter(obj)
    body                 while True:
                             try: x = next(_it); body
                             except StopIteration: break
```

---

## ⚙️ Custom Iterator Class

```python
class CountUp:
    def __init__(self, start, stop):
        self.cur  = start
        self.stop = stop

    def __iter__(self):
        return self       # iterator IS its own iterator

    def __next__(self):
        if self.cur > self.stop:
            raise StopIteration
        val = self.cur
        self.cur += 1
        return val

list(CountUp(1, 5))   # [1, 2, 3, 4, 5]
```

---

## ✨ Generator Function

```python
import functools

def count_up(start, stop):
    while start <= stop:
        yield start         # suspend, return value, resume later
        start += 1

gen = count_up(1, 5)
next(gen)   # 1  (runs until yield, pauses)
next(gen)   # 2  (resumes, runs until next yield)
list(gen)   # [3, 4, 5]  (consumes remainder)
next(gen)   # StopIteration

# Generator IS its own iterator:
gen is iter(gen)   # True
```

---

## 🧩 Generator Expressions

```python
# Syntax: (expr for x in iterable if condition)
gen   = (x**2 for x in range(1_000_000))   # ~200 bytes — nothing computed yet
lst   = [x**2 for x in range(1_000_000)]   # ~8.5MB — all computed immediately

# Use generators directly in built-ins (no extra [] needed):
total = sum(x**2 for x in range(1000))
found = any(x > 100 for x in data)
big   = all(x > 0 for x in data)
first = next(x for x in data if x > 10)   # first match (or StopIteration)
first = next((x for x in data if x > 10), None)  # with default

# When to use list vs generator:
# list  → multiple passes, len(), index access, append
# gen   → single pass, large data, pipeline composition
```

---

## 🔀 `yield from`

```python
# Delegate to sub-iterable:
def chain(a, b):
    yield from a   # yields each item from a
    yield from b   # then each from b

# Recursive delegation:
def flatten(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item

list(flatten([1, [2, [3]], 4]))   # [1, 2, 3, 4]

# Captures sub-generator return value:
result = yield from sub_gen()   # result = sub_gen()'s return value
```

---

## 📡 `send()` — Two-Way Communication

```python
def running_total():
    total = 0
    while True:
        n = yield total   # yield sends OUT, receives IN
        if n is None:
            break
        total += n

acc = running_total()
next(acc)       # MUST prime first (advance to first yield)
acc.send(10)    # → 10
acc.send(20)    # → 30
acc.send(5)     # → 35
acc.close()     # inject GeneratorExit

# Generator methods:
next(gen)           # advance, same as gen.send(None)
gen.send(value)     # resume + inject value
gen.throw(exc)      # inject exception at yield point
gen.close()         # throw GeneratorExit
```

---

## 🔧 Generator Pipeline

```python
# Each stage is a generator — O(1) memory total:
def read_lines(path):
    with open(path) as f:
        yield from f

def parse_json(lines):
    import json
    for line in lines:
        try: yield json.loads(line.strip())
        except: pass

def filter_level(records, level="ERROR"):
    for r in records:
        if r.get("level") == level:
            yield r

# Compose:
pipeline = filter_level(parse_json(read_lines("app.log")))
for record in pipeline:   # one record in memory at any time
    insert_to_db(record)
```

---

## 🛠️ `itertools` Quick Reference

```python
from itertools import (
    count, cycle, repeat,               # infinite
    chain, chain.from_iterable,         # concatenate
    islice,                             # slice generators
    takewhile, dropwhile, filterfalse,  # filter
    groupby,                            # group consecutive
    accumulate,                         # running aggregate
    product, combinations, permutations, # combinatorics
    zip_longest,                        # zip with fill
    pairwise,                           # overlapping pairs (3.10+)
    batched,                            # fixed chunks (3.12+)
)

count(10)                      # 10, 11, 12, ... (infinite)
cycle([1, 2, 3])               # 1, 2, 3, 1, 2, 3, ... (infinite)
repeat(42, 5)                  # 42 five times

list(chain([1,2], [3,4]))      # [1, 2, 3, 4]
list(islice(count(0), 5))      # [0, 1, 2, 3, 4]
list(takewhile(lambda x: x<5, [1,3,5,7]))  # [1, 3]
list(accumulate([1,2,3,4]))    # [1, 3, 6, 10]  running sum
list(pairwise([1,2,3,4]))      # [(1,2),(2,3),(3,4)]
list(batched([1,2,3,4,5], 2))  # [(1,2),(3,4),(5,)]

# groupby — sort first!
data = sorted([("a",1),("b",2),("a",3)], key=lambda x: x[0])
{k: list(g) for k, g in groupby(data, key=lambda x: x[0])}
# {'a': [('a',1),('a',3)], 'b': [('b',2)]}
```

---

## ♾️ Infinite Sequences

```python
def naturals():
    n = 1
    while True:
        yield n
        n += 1

def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Always consume with islice or takewhile:
from itertools import islice
list(islice(fibonacci(), 10))   # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

---

## ⚡ Async Generator

```python
async def async_range(n):
    for i in range(n):
        await asyncio.sleep(0)
        yield i

# Consume with async for:
async for item in async_range(10):
    process(item)

# Async comprehension:
result = [x async for x in async_range(10)]
```

---

## 💾 Memory Comparison

```
OPERATION                         MEMORY
──────────────────────────────────────────────────────────────
[x**2 for x in range(1_000_000)]  ~8.5 MB  (all at once)
(x**2 for x in range(1_000_000))  ~200 B   (one at a time)

read().splitlines()  on 50GB file → crash
for line in file:    on 50GB file → ~4KB constant

list(csv.DictReader(f)) on 10GB   → crash
(row for row in csv.DictReader(f)) → ~1KB constant
```

---

## 🔴 Gotchas

```python
# 1 — Generators exhaust after one pass:
gen = (x for x in range(5))
list(gen)   # [0, 1, 2, 3, 4]
list(gen)   # []  ← EMPTY!

# 2 — Must prime before send():
g = gen_func()
g.send(10)   # TypeError! Must call next(g) first.

# 3 — return in generator is NOT yielded:
def f():
    yield 1
    return 42   # raises StopIteration(42), not yielded!
list(f())   # [1]  not [1, 42]

# 4 — Generator expression in function — body not called at creation:
gen = (expensive(x) for x in data)   # expensive() not called yet!
# Called only when you iterate

# 5 — Can't len() or index a generator:
gen = (x for x in range(10))
len(gen)   # TypeError
gen[3]     # TypeError

# 6 — Generator created inside loop closes over shared variable:
# Be careful with closures in generator factories
```

---

## 🔥 Rapid-Fire

```
Q: Iterable vs Iterator?
A: Iterable: has __iter__. Iterator: has __iter__ + __next__.

Q: What is a generator function?
A: A function containing yield. Returns a generator object when called.

Q: Generator expression syntax?
A: (expr for x in it if cond) — parens not brackets.

Q: yield from?
A: Delegates to sub-iterable. Forwards send/throw/close.
   Captures sub-generator return value.

Q: How to prime send()?
A: Call next(gen) first.

Q: Can you iterate a generator twice?
A: No. Single-use. Use a factory function to restart.

Q: islice() purpose?
A: Safely take N items from infinite/large generator.

Q: Memory of generator vs list?
A: Generator: O(1). List: O(n). For 1M ints: ~200B vs ~8.5MB.
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| 🔧 Pipeline Patterns | [generator_patterns.md](./generator_patterns.md) |
| ➡️ Next | [12 — Context Managers](../12_context_managers/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Generator Patterns →](./generator_patterns.md)

**Related Topics:** [Theory](./theory.md) · [Generator Patterns](./generator_patterns.md) · [Interview Q&A](./interview.md)
