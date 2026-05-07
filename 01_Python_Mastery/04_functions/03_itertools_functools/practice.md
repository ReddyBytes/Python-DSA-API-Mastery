# 🔧 Itertools & Functools — Practice Problems

> 12 problems · itertools combinators, functools tools, real-world pipelines
> Write your answer in `practice_local.py` first, then use the dropdowns.

---

## 📋 Quick Index

| # | Tool | Concept | Level |
|---|------|---------|-------|
| Q1 | `itertools.chain` | Flatten multiple iterables | 🟢 |
| Q2 | `itertools.islice` | Slice an infinite iterator | 🟢 |
| Q3 | `itertools.takewhile / dropwhile` | Split at a boundary condition | 🟢 |
| Q4 | `itertools.groupby` | Group sorted data by key | 🟡 |
| Q5 | `itertools.product` | Cartesian product of iterables | 🟡 |
| Q6 | `functools.lru_cache` | Memoize an expensive function | 🟡 |
| Q7 | `functools.partial` | Specialise a general function | 🟡 |
| Q8 | `functools.reduce` | Aggregate with a binary function | 🟡 |
| Q9 | `chain + islice + reduce` | Lazy data pipeline | 🟠 |
| Q10 | `combinations / permutations` | Combinatorics | 🟡 |
| Q11 | `islice` (real-world) | Lazy pagination generator | 🟠 |
| Q12 | `lru_cache` (real-world) | Memoized price calculator | 🟠 |

---

### Q1 · itertools.chain — Flatten 3 lists

**Problem:**
Flatten 3 separate lists into one iterable without creating a combined list. Use `chain` and print each item.

```python
from itertools import chain
list1 = [1, 2, 3]
list2 = [4, 5, 6]
list3 = [7, 8, 9]
# your code here — use chain, print each item
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`chain(list1, list2, list3)` stitches iterables together end-to-end without copying any data. Loop over the result with a `for` loop.

</details>

<details>
<summary>✅ Answer</summary>

```python
from itertools import chain
list1 = [1, 2, 3]
list2 = [4, 5, 6]
list3 = [7, 8, 9]
for item in chain(list1, list2, list3):
    print(item)
```

**Why:** `chain` is a lazy iterator — it yields from each argument in turn without allocating a new list. Unlike `list1 + list2 + list3`, no intermediate list is ever created in memory.

</details>

---

### Q2 · itertools.islice — First 5 items from an infinite counter

**Problem:**
`count()` produces 0, 1, 2, 3, … infinitely. Use `islice` to get only the first 5 items and print them.

```python
from itertools import islice, count
# count() produces 0, 1, 2, 3, ... infinitely
# your code here — get first 5 items using islice
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`islice(iterable, stop)` works like Python's slice notation but for any iterator. Pass the infinite `count()` as the iterable and `5` as the stop.

</details>

<details>
<summary>✅ Answer</summary>

```python
from itertools import islice, count
first_five = list(islice(count(), 5))
print(first_five)  # [0, 1, 2, 3, 4]
```

**Why:** You can never iterate a raw `count()` to the end — there is no end. `islice` gives you a safe window into an infinite stream, consuming only what you ask for.

</details>

---

### Q3 · itertools.takewhile / dropwhile — Split at a boundary

**Problem:**
Use `takewhile` to get all scores >= 70, and `dropwhile` to get all scores below 70.

```python
from itertools import takewhile, dropwhile
scores = [95, 88, 76, 72, 65, 58, 45, 30]
# Use takewhile to get all scores >= 70
# Use dropwhile to get all scores < 70
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`takewhile(predicate, iterable)` yields items as long as the predicate is `True`, then stops. `dropwhile` skips items while the predicate is `True`, then yields the rest. Both stop/start at the same boundary point.

</details>

<details>
<summary>✅ Answer</summary>

```python
from itertools import takewhile, dropwhile
scores = [95, 88, 76, 72, 65, 58, 45, 30]

passing = list(takewhile(lambda s: s >= 70, scores))
failing = list(dropwhile(lambda s: s >= 70, scores))

print(passing)  # [95, 88, 76, 72]
print(failing)  # [65, 58, 45, 30]
```

**Why:** Both functions scan from the left and change state exactly once at the first item that breaks the condition. This only works correctly on sorted input — on unsorted data they would stop/start at the wrong place.

</details>

---

### Q4 · itertools.groupby — Group employees by department

**Problem:**
Sort the employee list by department, then use `groupby` to group them. Print each department and its members.

```python
from itertools import groupby
employees = [
    {"name": "Alice", "dept": "eng"},
    {"name": "Bob", "dept": "sales"},
    {"name": "Carol", "dept": "eng"},
    {"name": "Dave", "dept": "sales"},
    {"name": "Eve", "dept": "hr"},
]
# Sort first (groupby requires sorted input!), then group by dept
# Print each dept and its members
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Sort with `sorted(employees, key=lambda e: e["dept"])` first. Then pass the sorted list and the same key function to `groupby`. Each iteration of `groupby` yields `(key, group_iterator)`.

</details>

<details>
<summary>✅ Answer</summary>

```python
from itertools import groupby
employees = [
    {"name": "Alice", "dept": "eng"},
    {"name": "Bob", "dept": "sales"},
    {"name": "Carol", "dept": "eng"},
    {"name": "Dave", "dept": "sales"},
    {"name": "Eve", "dept": "hr"},
]

key_fn = lambda e: e["dept"]
for dept, members in groupby(sorted(employees, key=key_fn), key=key_fn):
    names = [m["name"] for m in members]
    print(f"{dept}: {names}")
```

**Why:** `groupby` only groups consecutive equal keys. If the input is not sorted first, the same department can appear in multiple groups. The sort step is not optional.

</details>

---

### Q5 · itertools.product — All size/color combinations

**Problem:**
Generate every `(size, color)` pair using `product`. Print each pair, then print the total count.

```python
from itertools import product
sizes = ["S", "M", "L", "XL"]
colors = ["red", "blue", "green"]
# Generate all (size, color) pairs using product
# Print each pair, then print total count
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`product(sizes, colors)` is equivalent to a nested `for` loop over both lists. Wrap the result in `list()` if you need to iterate it twice (once to print, once to count).

</details>

<details>
<summary>✅ Answer</summary>

```python
from itertools import product
sizes = ["S", "M", "L", "XL"]
colors = ["red", "blue", "green"]

pairs = list(product(sizes, colors))
for pair in pairs:
    print(pair)
print(f"Total: {len(pairs)}")  # Total: 12
```

**Why:** 4 sizes × 3 colors = 12 combinations. `product` handles the nesting for you and reads much cleaner than two nested `for` loops. It also works for any number of iterables.

</details>

---

### Q6 · functools.lru_cache — Memoize an expensive function

**Problem:**
`nth_triangular(n)` computes 1+2+...+n recursively. Add `@lru_cache`, call it 5 times with the same argument, and use `cache_info()` to show cache hits.

```python
import functools
import time

def nth_triangular(n):
    if n <= 1:
        return n
    return n + nth_triangular(n - 1)
# your code here: add cache, time both versions
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Place `@functools.lru_cache(maxsize=None)` directly above the function definition. After calling it, `nth_triangular.cache_info()` returns a named tuple with `hits`, `misses`, `maxsize`, and `currsize`.

</details>

<details>
<summary>✅ Answer</summary>

```python
import functools
import time

@functools.lru_cache(maxsize=None)
def nth_triangular(n):
    if n <= 1:
        return n
    return n + nth_triangular(n - 1)

# Call 5 times with the same argument
for _ in range(5):
    result = nth_triangular(500)

print(f"Result: {result}")
print(nth_triangular.cache_info())
# CacheInfo(hits=4, misses=500, maxsize=None, currsize=500)
```

**Why:** The first call computes all 500 recursive steps (500 misses). The next 4 calls find `nth_triangular(500)` in the cache immediately (4 hits). Without the cache, 5 × 500 = 2500 recursive calls would run.

</details>

---

### Q7 · functools.partial — Specialised number formatters

**Problem:**
`format_number(value, prefix="", suffix="", decimal_places=2)` is the base function. Use `partial` to create `format_usd` ($10.00), `format_eur` (€10.00), and `format_pct` (10.00%). Test each with the value `10`.

```python
import functools
def format_number(value, prefix="", suffix="", decimal_places=2):
    return f"{prefix}{value:.{decimal_places}f}{suffix}"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`functools.partial(func, **kwargs)` creates a new callable with some arguments pre-filled. You can freeze any combination of positional or keyword arguments.

</details>

<details>
<summary>✅ Answer</summary>

```python
import functools

def format_number(value, prefix="", suffix="", decimal_places=2):
    return f"{prefix}{value:.{decimal_places}f}{suffix}"

format_usd = functools.partial(format_number, prefix="$")
format_eur = functools.partial(format_number, prefix="€")
format_pct = functools.partial(format_number, suffix="%")

print(format_usd(10))   # $10.00
print(format_eur(10))   # €10.00
print(format_pct(10))   # 10.00%
```

**Why:** `partial` captures the pre-filled arguments in a closure-like object. The resulting callables behave exactly like the original function but with fewer required arguments — ideal for configuration-heavy functions.

</details>

---

### Q8 · functools.reduce — Three aggregate calculations

**Problem:**
Use `reduce` to: (1) find the product of all numbers, (2) find the max without using `max()`, (3) merge a list of dicts into one.

```python
from functools import reduce
numbers = [2, 3, 4, 5, 6]
dicts = [{"a": 1}, {"b": 2}, {"c": 3}]
# your code here — 3 reduce operations
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`reduce(function, iterable)` applies the function cumulatively: `f(f(f(a, b), c), d)`. For the dict merge, use `{**acc, **cur}` as the reducing expression to merge two dicts at each step.

</details>

<details>
<summary>✅ Answer</summary>

```python
from functools import reduce

numbers = [2, 3, 4, 5, 6]
dicts = [{"a": 1}, {"b": 2}, {"c": 3}]

product = reduce(lambda acc, x: acc * x, numbers)
print(f"Product: {product}")  # 720

maximum = reduce(lambda acc, x: acc if acc > x else x, numbers)
print(f"Max: {maximum}")  # 6

merged = reduce(lambda acc, d: {**acc, **d}, dicts)
print(f"Merged: {merged}")  # {'a': 1, 'b': 2, 'c': 3}
```

**Why:** `reduce` is the general pattern behind `sum`, `max`, and `dict.update`. It collapses a sequence into a single value by repeatedly applying a binary function from left to right.

</details>

---

### Q9 · chain + islice + reduce — Lazy log pipeline

**Problem:**
Use `chain` to combine two log lists, `islice` to take only the first 10 entries, and `reduce` to count how many are at ERROR level.

```python
from itertools import chain, islice
from functools import reduce

logs_a = ["INFO login", "ERROR timeout", "INFO request", "ERROR crash", "DEBUG trace"]
logs_b = ["ERROR retry", "INFO success", "DEBUG verbose", "ERROR fail", "INFO logout"]
# your code here: chain → islice(10) → reduce to count ERRORs
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

The pipeline is three steps chained together: `islice(chain(logs_a, logs_b), 10)` gives you a lazy stream of 10 log lines. Then `reduce` on that stream with an accumulator that adds 1 when the line starts with `"ERROR"`.

</details>

<details>
<summary>✅ Answer</summary>

```python
from itertools import chain, islice
from functools import reduce

logs_a = ["INFO login", "ERROR timeout", "INFO request", "ERROR crash", "DEBUG trace"]
logs_b = ["ERROR retry", "INFO success", "DEBUG verbose", "ERROR fail", "INFO logout"]

pipeline = islice(chain(logs_a, logs_b), 10)
error_count = reduce(lambda acc, line: acc + (1 if line.startswith("ERROR") else 0), pipeline, 0)
print(f"ERROR count in first 10 lines: {error_count}")  # 4
```

**Why:** Each function in the pipeline is lazy — no full list is materialised at any step. The `0` at the end of `reduce` is the initial accumulator value, which is required when the iterable might be empty.

</details>

---

### Q10 · combinations / permutations — Card hands

**Problem:**
Given `cards = ["A", "K", "Q", "J"]`, find: (1) all 2-card hands (combinations), (2) all ways to arrange 2 cards (permutations). Print counts and the first 3 of each.

```python
from itertools import combinations, permutations
cards = ["A", "K", "Q", "J"]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`combinations(iterable, r)` returns r-length tuples with no repeated elements and order doesn't matter. `permutations(iterable, r)` returns r-length tuples where order matters. Use `list()` to materialise them.

</details>

<details>
<summary>✅ Answer</summary>

```python
from itertools import combinations, permutations
cards = ["A", "K", "Q", "J"]

hands = list(combinations(cards, 2))
arrangements = list(permutations(cards, 2))

print(f"Combinations (hands): {len(hands)} total")   # 6
print(f"First 3: {hands[:3]}")

print(f"Permutations (arrangements): {len(arrangements)} total")  # 12
print(f"First 3: {arrangements[:3]}")
```

**Why:** With 4 cards choosing 2: combinations = 4!/(2!×2!) = 6, permutations = 4!/2! = 12. Every combination has exactly 2 corresponding permutations (AK and KA are the same hand but different arrangements).

</details>

---

### Q11 · Real-world — Lazy pagination

**Problem:**
Write `paginate(iterable, page_size)` using `islice` that yields one page at a time as a list, stopping when the iterable is exhausted. Test with a 25-item list and `page_size=10`.

```python
from itertools import islice
# your code here

data = list(range(25))
# paginate(data, 10) should yield: [0..9], [10..19], [20..24]
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Convert the iterable to an `iter()` object first — that way each call to `islice` advances the same iterator (rather than always starting from the beginning). Loop with `while True` and `break` when `islice` returns an empty list.

</details>

<details>
<summary>✅ Answer</summary>

```python
from itertools import islice

def paginate(iterable, page_size):
    it = iter(iterable)
    while True:
        page = list(islice(it, page_size))
        if not page:
            break
        yield page

data = list(range(25))
for page_num, page in enumerate(paginate(data, 10), start=1):
    print(f"Page {page_num}: {page}")
# Page 1: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
# Page 2: [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
# Page 3: [20, 21, 22, 23, 24]
```

**Why:** Wrapping in `iter()` is the key insight. A list resets to the start on each call; an `iter` object maintains position. `islice` on the shared iterator naturally slices the next `page_size` items on every loop.

</details>

---

### Q12 · Real-world — Memoized price calculator

**Problem:**
Write `calculate_total(items_tuple, discount_rate)` where `items_tuple` is a tuple of `(name, price)` pairs. Apply the discount and return the total. Use `@functools.lru_cache`. Why must it take a tuple instead of a list?

```python
import functools
# your code here

items = (("apple", 1.5), ("banana", 0.75), ("cherry", 3.0))
print(calculate_total(items, 0.1))
print(calculate_total(items, 0.1))  # should be a cache hit
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`lru_cache` requires all arguments to be hashable so it can use them as dict keys. Lists are mutable and not hashable. Tuples are immutable and hashable. The discount rate (a float) is already hashable.

</details>

<details>
<summary>✅ Answer</summary>

```python
import functools

@functools.lru_cache(maxsize=128)
def calculate_total(items_tuple, discount_rate):
    subtotal = sum(price for _, price in items_tuple)
    return round(subtotal * (1 - discount_rate), 2)

items = (("apple", 1.5), ("banana", 0.75), ("cherry", 3.0))
print(calculate_total(items, 0.1))  # 4.73
print(calculate_total(items, 0.1))  # 4.73 — cache hit

print(calculate_total.cache_info())
# CacheInfo(hits=1, misses=1, maxsize=128, currsize=1)
```

**Why:** `lru_cache` stores results in a dictionary keyed by the function arguments. Dictionary keys must be hashable. A list can be mutated after the call, which would silently corrupt the cache — so Python simply refuses to hash them. Tuples are the correct type for hashable sequences.

</details>

---

**[Back to Functions](../theory.md)** | **[← Closures & Decorators](../02_closures_decorators/02_decorators_theory.md)**

**Related:** [Theory](./theory.md) · [practice_local.py](./practice_local.py) · [Functional Programming](../01_functional_programming/practice.md)
