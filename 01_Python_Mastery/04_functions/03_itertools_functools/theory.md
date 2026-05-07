# itertools & functools — Functional Programming Toolkit

> *"Built-in functions are individual LEGO bricks. itertools and functools are the connector*
> *pieces — they let you join, transform, and compose those bricks into complex structures*
> *without writing a single extra loop."*

---

## The Story

Python treats functions and iterators as **first-class objects** — you can pass them around, store them in variables, and return them from other functions. That design decision made an entire class of programming patterns possible.

Two modules unlock those patterns:

`itertools` gives you lazy combinators for sequences — tools that chain, slice, group, and generate iterables without loading everything into memory at once.

`functools` gives you tools for working with functions as objects — caching, partial application, composition, and metadata preservation.

The difference between a developer who knows these and one who doesn't is usually visible in code review: one reaches for a loop, the other reaches for a composable primitive that communicates intent, runs faster, and uses less memory.

---

```
┌─────────────────────────────────────────────────────────────────────────┐
│  itertools                         functools                             │
│  ─────────────────────────────     ─────────────────────────────────    │
│  • Infinite iterators              • lru_cache / cache (memoization)    │
│    count, cycle, repeat            • partial (pre-fill arguments)       │
│  • Finite sequence tools           • reduce (fold a sequence)           │
│    chain, islice, takewhile,       • wraps (preserve decorator meta)    │
│    dropwhile, filterfalse,         • total_ordering (fill comparisons)  │
│    compress, starmap               • cached_property (lazy attribute)   │
│  • Grouping: groupby                                                     │
│  • Combinatorics                                                         │
│    product, permutations,                                                │
│    combinations                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# Part 1 — itertools

## 1 — Infinite Iterators

These iterators never stop on their own. Always pair them with `islice` or a loop that breaks.

```python
from itertools import count, cycle, repeat, islice

# count — integers starting from start, stepping by step
for n in islice(count(10, 2), 5):      # ← islice takes first 5
    print(n)                            # 10, 12, 14, 16, 18

# cycle — repeats the sequence forever
status_icons = cycle(["⠋", "⠙", "⠹", "⠸"])   # spinner animation
for icon in islice(status_icons, 8):
    print(icon)                         # ⠋ ⠙ ⠹ ⠸ ⠋ ⠙ ⠹ ⠸

# repeat — emit a value N times (or forever if n omitted)
list(repeat("hello", 3))               # ["hello", "hello", "hello"]

# common use: pad map() calls
from itertools import starmap
list(starmap(pow, zip(range(5), repeat(2))))   # [0, 1, 4, 9, 16]
```

```
count(0)  →  0  1  2  3  4  5  ...  (never stops)
cycle("AB") →  A  B  A  B  A  B  ... (never stops)
repeat(7, 3) →  7  7  7             (stops after 3)
```

---

## 2 — Finite Sequence Tools

```python
from itertools import (chain, islice, takewhile, dropwhile,
                        filterfalse, compress, starmap)

# chain — join multiple iterables end-to-end (no nesting)
list(chain([1, 2], [3, 4], [5]))          # [1, 2, 3, 4, 5]
list(chain.from_iterable([[1, 2], [3, 4]]))  # [1, 2, 3, 4] ← flattens one level

# islice — lazy slice (does not load everything first)
list(islice("ABCDEFG", 3))               # ["A", "B", "C"]
list(islice("ABCDEFG", 2, 5))            # ["C", "D", "E"]
list(islice("ABCDEFG", 0, None, 2))      # ["A", "C", "E", "G"]

# takewhile — yield elements while predicate is True, stop at first False
list(takewhile(lambda x: x < 5, [1, 3, 4, 6, 2, 7]))   # [1, 3, 4]

# dropwhile — skip elements while predicate is True, then yield rest
list(dropwhile(lambda x: x < 5, [1, 3, 4, 6, 2, 7]))   # [6, 2, 7]

# filterfalse — opposite of filter(): yield elements where predicate is False
list(filterfalse(lambda x: x % 2, range(8)))             # [0, 2, 4, 6]

# compress — select elements where selector is True/truthy
list(compress("ABCDE", [1, 0, 1, 0, 1]))                 # ["A", "C", "E"]

# starmap — like map() but unpacks tuples as function arguments
list(starmap(pow, [(2, 3), (3, 2), (10, 2)]))            # [8, 9, 100]
```

The key difference between `islice` and list slicing: `islice` is **lazy** — it does not materialize the full iterable. This matters for large files, database cursors, and generator pipelines.

---

## 3 — Grouping with groupby

**`groupby`** groups consecutive elements that share the same key. Think of it as the SQL `GROUP BY` — but it only groups runs that are already adjacent.

```python
from itertools import groupby

data = [
    {"date": "2024-01-01", "event": "login"},
    {"date": "2024-01-01", "event": "view"},
    {"date": "2024-01-02", "event": "login"},
    {"date": "2024-01-02", "event": "purchase"},
    {"date": "2024-01-02", "event": "logout"},
]

# MUST be sorted by the same key first
data.sort(key=lambda x: x["date"])              # ← critical step

for date, group in groupby(data, key=lambda x: x["date"]):
    events = [item["event"] for item in group]  # ← consume group before next iteration
    print(f"{date}: {events}")

# 2024-01-01: ['login', 'view']
# 2024-01-02: ['login', 'purchase', 'logout']
```

The single most common `groupby` mistake: forgetting to sort first. If the data has non-consecutive runs of the same key, groupby creates a new group for each run:

```
Input unsorted: A A B A B B
groupby sees:   [A,A], [B], [A], [B,B]   ← four groups, not two
Input sorted:   A A A B B B
groupby sees:   [A,A,A], [B,B,B]         ← correct
```

Also: consume each group before advancing to the next key. The group object is a lazy iterator tied to the underlying data — once you call `next()` on the outer iterator, the previous group is exhausted.

---

## 4 — Combinatoric Iterators

These generate all possible arrangements or selections from an input.

```python
from itertools import product, permutations, combinations, combinations_with_replacement

# product — cartesian product (like nested for-loops)
list(product("AB", "12"))           # [('A','1'),('A','2'),('B','1'),('B','2')]
list(product(range(2), repeat=3))   # all 3-bit binary numbers: (0,0,0)...(1,1,1)

# permutations — ordered arrangements, no repeats
list(permutations("ABC", 2))        # [('A','B'),('A','C'),('B','A'),('B','C'),('C','A'),('C','B')]

# combinations — unordered selections, no repeats
list(combinations("ABC", 2))        # [('A','B'),('A','C'),('B','C')]

# combinations_with_replacement — unordered, repeats allowed
list(combinations_with_replacement("AB", 2))  # [('A','A'),('A','B'),('B','B')]
```

```
Size formulas:
─────────────────────────────────────────────────────────────────────
product(n items, repeat=r)              →  n^r   results
permutations(n items, r)                →  n!/(n-r)!  results
combinations(n items, r)                →  n!/(r!(n-r)!)  results
combinations_with_replacement(n, r)     →  (n+r-1)!/(r!(n-1)!)
─────────────────────────────────────────────────────────────────────

When to use each:
─────────────────────────────────────────────────────────────────────
product            Testing all combinations of settings (grid search)
permutations       All orderings of items (scheduling, anagrams)
combinations       Choosing a team, poker hands, feature subsets
comb_with_repl     Rolling dice (same face allowed), multisets
─────────────────────────────────────────────────────────────────────
```

---

## 5 — Real-World itertools Recipes

These patterns appear constantly in production code.

```python
from itertools import islice, chain, pairwise   # pairwise: Python 3.10+

# ── sliding window of size n ──────────────────────────────────────────────
def sliding_window(iterable, n):
    it = iter(iterable)
    window = tuple(islice(it, n))                # ← seed the first window
    if len(window) == n:
        yield window
    for item in it:
        window = window[1:] + (item,)            # ← slide by one
        yield window

list(sliding_window([1, 2, 3, 4, 5], 3))
# [(1,2,3), (2,3,4), (3,4,5)]

# ── batch into chunks of N ────────────────────────────────────────────────
def batched(iterable, n):
    it = iter(iterable)
    while chunk := tuple(islice(it, n)):         # ← Python 3.8+ walrus operator
        yield chunk

list(batched(range(10), 3))
# [(0,1,2), (3,4,5), (6,7,8), (9,)]

# ── flatten one level ─────────────────────────────────────────────────────
nested = [[1, 2], [3, 4], [5]]
list(chain.from_iterable(nested))                # [1, 2, 3, 4, 5]

# ── pairwise consecutive (Python 3.10+) ──────────────────────────────────
from itertools import pairwise
list(pairwise([1, 2, 3, 4]))                     # [(1,2), (2,3), (3,4)]

# ── round-robin from multiple iterables ──────────────────────────────────
def roundrobin(*iterables):
    pending = len(iterables)
    nexts = cycle(iter(it).__next__ for it in iterables)
    while pending:
        try:
            for next_ in nexts:
                yield next_()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))

list(roundrobin("ABC", "D", "EF"))               # ['A', 'D', 'E', 'B', 'F', 'C']
```

---

# Part 2 — functools

## 6 — functools.lru_cache — Memoization

**Memoization** is a technique where you cache a function's return value the first time it's called with a given set of arguments, and return the cached result on subsequent calls with the same arguments. It trades memory for speed.

```python
from functools import lru_cache, cache

@lru_cache(maxsize=128)                  # ← cache up to 128 unique argument sets
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Without cache: O(2^n) calls. With cache: O(n) calls.
fibonacci(50)           # fast

# Inspect cache performance
fibonacci.cache_info()  # CacheInfo(hits=48, misses=51, maxsize=128, currsize=51)
fibonacci.cache_clear() # ← invalidate all cached results

# Python 3.9+ shorthand: unbounded cache
@cache                  # ← equivalent to lru_cache(maxsize=None)
def fib(n):
    if n < 2: return n
    return fib(n-1) + fib(n-2)
```

Requirements and limits:

```
Arguments must be hashable:
  ✓ int, str, float, tuple, frozenset
  ✗ list, dict, set (unhashable → TypeError)

When NOT to use lru_cache:
  ✗ Functions with side effects (file writes, network calls)
  ✗ Functions that depend on external state (time, random, DB)
  ✗ Functions where arguments are never repeated (cache just wastes memory)
```

---

## 7 — functools.partial — Pre-fill Arguments

**`partial`** creates a new callable with some arguments already filled in. Like having a template for a function call.

```python
from functools import partial

# base function
def send_email(to, subject, body, priority="normal"):
    print(f"To: {to} | {priority} | {subject}")

# create specialized versions
send_alert = partial(send_email, priority="high")        # ← fix priority keyword
send_report = partial(send_email, subject="Weekly Report")  # ← fix subject

send_alert("ops@example.com", "Disk full", "Server has <1% disk space")
send_report("team@example.com", body="Sales up 12%")

# use case: adapting a two-arg function to fit a single-arg callback interface
import os
from functools import partial

join_to_base = partial(os.path.join, "/data/output")     # ← first arg pre-filled
list(map(join_to_base, ["a.csv", "b.csv", "c.csv"]))
# ['/data/output/a.csv', '/data/output/b.csv', '/data/output/c.csv']
```

When to use `partial` vs a lambda:
- `partial` is cleaner when you are just fixing some arguments of an existing function
- lambda is better when you need to transform or rearrange arguments: `lambda x: f(x * 2, extra)`

---

## 8 — functools.reduce — Fold a Sequence

**`reduce`** applies a function cumulatively to a sequence, collapsing it to a single value. It is the general form of sum, max, and any other aggregation.

```python
from functools import reduce
import operator

# reduce(function, iterable, initial)
reduce(operator.add, [1, 2, 3, 4, 5])          # 15  (same as sum())
reduce(operator.mul, [1, 2, 3, 4, 5], 1)        # 120 (factorial)
reduce(max, [3, 1, 4, 1, 5, 9, 2, 6])          # 9

# accumulator pattern — each step:
# step 1: f(1, 2) = 3
# step 2: f(3, 3) = 6
# step 3: f(6, 4) = 10
# step 4: f(10, 5) = 15

# practical: merge a list of dicts
dicts = [{"a": 1}, {"b": 2}, {"c": 3}]
reduce(lambda acc, d: {**acc, **d}, dicts)       # {"a": 1, "b": 2, "c": 3}
```

When reduce is appropriate vs when a loop is clearer:

```
Use reduce when:                        Use a loop or comprehension when:
─────────────────────────────────       ──────────────────────────────────────
Aggregating to a single value           The accumulation logic is complex
Function is a clean 2-arg callable      You need to inspect intermediate values
The reduction is well-known (sum, max)  Multiple passes or conditions are needed
```

---

## 9 — functools.wraps — Preserve Decorator Metadata

When you write a decorator, you replace the original function with a wrapper. Without `@wraps`, the wrapper's name and docstring overwrite the original's:

```python
from functools import wraps

# WITHOUT @wraps — metadata is lost
def bad_timer(func):
    def wrapper(*args, **kwargs):         # ← wrapper is a new function
        return func(*args, **kwargs)
    return wrapper

@bad_timer
def process():
    """Process data."""
    pass

process.__name__   # "wrapper"   ← wrong
process.__doc__    # None        ← lost

# WITH @wraps — metadata is preserved
def timer(func):
    @wraps(func)                          # ← copy metadata from func to wrapper
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@timer
def process():
    """Process data."""
    pass

process.__name__   # "process"   ← correct
process.__doc__    # "Process data."  ← preserved
```

`@wraps` copies: `__name__`, `__doc__`, `__module__`, `__qualname__`, `__annotations__`, `__dict__`, and `__wrapped__` (a reference back to the original function).

Rule: every decorator you write should have `@wraps(func)` on the inner wrapper. No exceptions.

---

## 10 — functools.total_ordering — Fill Out Comparison Methods

To make a class sortable, Python needs `__eq__` and at least one of `__lt__`, `__le__`, `__gt__`, `__ge__`. `@total_ordering` fills in the rest if you define just two.

```python
from functools import total_ordering

@total_ordering
class Version:
    def __init__(self, major, minor, patch):
        self.major = major
        self.minor = minor
        self.patch = patch

    def __eq__(self, other):
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __lt__(self, other):                           # ← define only __eq__ and __lt__
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    # total_ordering fills in: __le__, __gt__, __ge__

v1 = Version(1, 2, 3)
v2 = Version(2, 0, 0)

v1 < v2     # True   ← we defined this
v1 > v2     # False  ← total_ordering derived it
v1 <= v2    # True   ← total_ordering derived it
sorted([v2, v1])     # [Version(1,2,3), Version(2,0,0)]
```

---

## 11 — functools.cached_property (Python 3.8+)

**`@cached_property`** computes a value once per instance on first access, then stores it as an instance attribute. Subsequent accesses bypass the property and read the attribute directly — no re-computation.

```python
from functools import cached_property
import json

class Config:
    def __init__(self, path):
        self.path = path

    @cached_property
    def data(self):
        print("Reading file...")           # ← only prints on first access
        with open(self.path) as f:
            return json.load(f)

cfg = Config("config.json")
cfg.data   # prints "Reading file..." and returns parsed JSON
cfg.data   # returns same object instantly — no file read
cfg.data   # same
```

```
@property vs @cached_property:
────────────────────────────────────────────────────────────
@property           Called on every access. Good for cheap
                    computed values or values that can change.

@cached_property    Called once per instance. Stored as an
                    instance attribute after first call.
                    Good for expensive one-time computations.
────────────────────────────────────────────────────────────
```

Note: `cached_property` only works on classes that allow `__dict__` assignment (no `__slots__`).

---

## 12 — Common Mistakes

```
┌──────────────────────────────────────────┬────────────────────────────────────────────────────────┐
│ Mistake                                  │ Fix                                                    │
├──────────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ groupby without sorting first            │ Always sort by the same key before groupby. Unsorted   │
│ → multiple groups for the same key       │ input creates a new group per consecutive run.         │
├──────────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ Not consuming groupby group before next  │ group is a lazy iterator. Once you advance to the next │
│ key → empty or incorrect groups          │ key, the previous group is exhausted. Consume it first.│
├──────────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ lru_cache with unhashable args           │ lru_cache requires hashable arguments. Pass tuples     │
│ e.g. @cache on f(items: list) → error   │ instead of lists, or convert: tuple(items).            │
├──────────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ lru_cache on method with self            │ self is part of the cache key. Each instance gets its  │
│ → instance never garbage-collected       │ own cache entry holding a ref to self. Use             │
│                                          │ cached_property or cache per-instance instead.         │
├──────────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ partial vs lambda confusion              │ partial(f, a, b) is cleaner for simple argument fixing.│
│                                          │ lambda is better when you need to transform args:      │
│                                          │ lambda x: f(x*2, extra).                              │
├──────────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ reduce where sum/max is clearer          │ reduce(operator.add, items) → use sum(items).          │
│                                          │ Reserve reduce for non-standard aggregations.          │
├──────────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ Forgetting @wraps in decorators          │ Put @wraps(func) on every inner wrapper function.      │
│ → __name__, __doc__ are lost             │ Without it, debugging and introspection tools break.   │
└──────────────────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## Navigation

- Back to: [04 Functions — Theory](theory.md)
- Next topic: [11 Generators & Iterators — Theory](../11_generators_iterators/theory.md)
- Related: [collections module](../03_data_types/collections_module.md)
