# Practice — Data Types Complexity Analysis

Ten questions that move from recognition to rewriting. Each question is self-contained: read the
problem, attempt it, then open the hint or answer.

---


## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| [Q1](#q1) | pick-structure — Pick the Right Structure for O(1) Membership | 🟢 |
| [Q2](#q2) | hash-vs-scan — Why `in` is O(n) for list but O(1) for set | 🟡 |
| [Q3](#q3) | find-the-slow-op — Predict Which Operation is O(n) | 🟡 |
| [Q4](#q4) | swap-to-set — Fix Slow Code by Swapping list → set | 🟡 |
| [Q5](#q5) | string-concat-loop — Why `+=` in a Loop is O(n²) and How to Fix It | 🟡 |
| [Q6](#q6) | key-in-dict — `key in dict` vs `key in dict.keys()` | 🟡 |
| [Q7](#q7) | benchmark-timeit — Benchmark Set vs List Membership | 🟡 |
| [Q8](#q8) | amortized-append — When is list.append Actually O(n)? | 🟡 |
| [Q9](#q9) | frequency-counter — Pick the Right Structure for a Frequency Counter | 🟢 |
| [Q10](#q10) | o-n-squared-to-o-n — Rewrite Duplicate Detection from O(n²) to O(n) | 🟠 |

---

<a id="q1"></a>

### Q1 · pick-structure — Pick the Right Structure for O(1) Membership 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


You receive a list of 2 million banned user IDs. Your API must check whether an incoming request ID
is banned on every single request. Which Python data structure gives you O(1) lookup? Show the
construction and the membership check.

<details>
<summary>Hint</summary>
Think about which structures use a hash table internally. Lists scan sequentially; hash-based
structures do not.
</details>

<details>
<summary>Answer</summary>

```python
banned_ids_raw = [1001, 1002, 1003, ...]   # original list
banned_ids = set(banned_ids_raw)           # ← convert once, O(n) cost, paid once

def is_banned(user_id: int) -> bool:
    return user_id in banned_ids           # O(1) average — hash table lookup
```

A **dict** also works if you need metadata per ID:

```python
banned = {uid: True for uid in banned_ids_raw}
"user_id" in banned   # O(1)
```

**Why:** `set` and `dict` store a hash of each element. Membership check computes the hash of
the query and jumps directly to the right bucket — no scanning.
</details>

---

<a id="q2"></a>

### Q2 · hash-vs-scan — Why `in` is O(n) for list but O(1) for set 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


Explain, in plain terms, why `x in my_list` is O(n) while `x in my_set` is O(1). No code
required — a clear written explanation or a diagram is the goal.

<details>
<summary>Hint</summary>
How are the two structures laid out in memory? How does Python locate element `x` in each case?
</details>

<details>
<summary>Answer</summary>

**List** stores elements in order in a contiguous block of memory. To find `x`, Python starts at
index 0 and compares each element against `x` until it either finds a match or exhausts the list.
In the worst case (x is missing or at the end) it checks every single element: **O(n)**.

**Set** computes `hash(x)` — a single integer — then uses that integer to calculate which "bucket"
in the hash table to look in. It jumps directly to that bucket and compares only the element(s)
there. With a good hash function and low collision rate, that is **one comparison: O(1)**.

```
List lookup for 99:
[10, 42, 7, 88, 55, 3, 99]   ← must walk until we find 99
  ↑   ↑   ↑   ↑   ↑  ↑  ↑   6 comparisons before match

Set lookup for 99:
hash(99) → bucket 4 → compare one element → found.  1 comparison.
```

**Why:** Sets pay an upfront cost at insert time (compute and store the hash). Membership tests
redeem that investment — O(1) lookup in exchange for extra memory.
</details>

---

<a id="q3"></a>

### Q3 · find-the-slow-op — Predict Which Operation is O(n) 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


Each snippet below contains one operation. Identify which one is O(n) and explain why. All others
are O(1).

```python
# Snippet A
d = {"a": 1, "b": 2}
val = d["a"]

# Snippet B
my_list = [1, 2, 3, 4, 5]
my_list.insert(0, 99)

# Snippet C
my_set = {1, 2, 3}
my_set.add(42)

# Snippet D
t = (10, 20, 30)
result = t[1]
```

<details>
<summary>Hint</summary>
One of these forces Python to move existing elements in memory.
</details>

<details>
<summary>Answer</summary>

**Snippet B is O(n).**

`my_list.insert(0, 99)` inserts at the front. Python must shift every existing element one position
to the right to make room at index 0. With 5 elements that is 5 moves; with 5 million elements it
is 5 million moves.

- Snippet A: dict key lookup → O(1) hash table access.
- Snippet C: set.add → O(1) hash table insert.
- Snippet D: tuple index access → O(1) direct memory offset.

**Why:** Lists are contiguous arrays. Insertion in the middle or at the front requires shifting all
elements after the insertion point — cost grows linearly with list length.
</details>

---

<a id="q4"></a>

### Q4 · swap-to-set — Fix Slow Code by Swapping list → set 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


The function below checks which items in `cart` are out-of-stock. It is slow when `out_of_stock`
is large. Rewrite it to run in O(n) instead of O(n²).

```python
def get_unavailable(cart: list, out_of_stock: list) -> list:
    return [item for item in cart if item in out_of_stock]
```

<details>
<summary>Hint</summary>
The inner `in` check is the bottleneck. What conversion costs O(n) once but makes every subsequent
check O(1)?
</details>

<details>
<summary>Answer</summary>

```python
def get_unavailable(cart: list, out_of_stock: list) -> list:
    oos_set = set(out_of_stock)              # ← one-time O(n) conversion
    return [item for item in cart if item in oos_set]  # ← O(1) per check
```

**Before:** `item in out_of_stock` scans the list each time — O(m) per item, O(n*m) total.

**After:** `set(out_of_stock)` is built once in O(m). Each `item in oos_set` is O(1). Total cost:
O(m) + O(n) = **O(n + m)**.

**Why:** One-time conversion from list to set pays for itself the moment you perform more than one
membership check against the same collection.
</details>

---

<a id="q5"></a>

### Q5 · string-concat-loop — Why `+=` in a Loop is O(n²) and How to Fix It 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Explain why this code is O(n²) in time complexity, then rewrite it correctly.

```python
def build_report(lines: list[str]) -> str:
    result = ""
    for line in lines:
        result += line + "\n"   # ← what's wrong here?
    return result
```

<details>
<summary>Hint</summary>
Strings are immutable in Python. What happens to the old string object every time you do `+=`?
</details>

<details>
<summary>Answer</summary>

```python
# WRONG — O(n²)
def build_report_slow(lines: list[str]) -> str:
    result = ""
    for line in lines:
        result += line + "\n"   # ← new string object created every iteration
    return result

# CORRECT — O(n)
def build_report(lines: list[str]) -> str:
    return "\n".join(lines) + "\n"   # ← one allocation, one copy
```

**Why the loop is O(n²):** Strings are immutable. Each `+=` creates a brand-new string by copying
all characters from the old string plus the new characters. At iteration k, the string has k lines
— copying it costs O(k). Summing over all iterations: 1 + 2 + ... + n = **O(n²)**.

**Why `join` is O(n):** `str.join` pre-calculates the total length of all strings, allocates a
single buffer of exactly that size, and fills it in one pass. One allocation, one copy: **O(n)**.
</details>

---

<a id="q6"></a>

### Q6 · key-in-dict — `key in dict` vs `key in dict.keys()` 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


Which is faster: `"age" in my_dict` or `"age" in my_dict.keys()`? Why? Does it matter in practice?

<details>
<summary>Hint</summary>
What does `dict.keys()` return? Is it a separate data structure, or a view?
</details>

<details>
<summary>Answer</summary>

```python
d = {"name": "Alice", "age": 30}

# Option A — direct key check
"age" in d            # O(1) — checks the dict's hash table directly

# Option B — keys view check
"age" in d.keys()     # O(1) — dict_keys also supports O(1) membership via hash table
```

Both are **O(1)** because `dict.keys()` returns a **dict_keys view** — a lightweight object backed
by the same underlying hash table. It does not create a copy of the keys.

In practice, **`key in dict` is preferred** — it is more readable and marginally faster (no
attribute lookup for `.keys()`). Avoid `key in list(dict.keys())` — `list(...)` forces O(n) copy.

```python
# AVOID — O(n) conversion + O(n) scan
"age" in list(d.keys())
```

**Why:** Dictionary views (`keys()`, `values()`, `items()`) are always O(1) for membership on keys
because they share the hash table. Values views are O(n) because values are not indexed by hash.
</details>

---

<a id="q7"></a>

### Q7 · benchmark-timeit — Benchmark Set vs List Membership 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


Write a script using `timeit` that measures the difference in membership-check speed between a list
and a set for n = 100, 10_000, and 1_000_000 elements. The target element should be one that does
NOT exist (worst case).

<details>
<summary>Hint</summary>
Use `timeit.timeit(stmt, setup, number)`. Build the list and set in the setup string so the timer
only measures the `in` check.
</details>

<details>
<summary>Answer</summary>

```python
import timeit

for n in [100, 10_000, 1_000_000]:
    setup = f"data = list(range({n})); s = set(data); target = {n} + 1"

    list_time = timeit.timeit("target in data", setup=setup, number=10_000)
    set_time  = timeit.timeit("target in s",    setup=setup, number=10_000)

    print(f"n={n:>9,}  list={list_time:.4f}s  set={set_time:.6f}s  "
          f"ratio={list_time/set_time:.0f}x")
```

Sample output:
```
n=      100  list=0.0003s  set=0.000060s  ratio=5x
n=   10,000  list=0.0280s  set=0.000061s  ratio=459x
n=1,000,000  list=2.7500s  set=0.000062s  ratio=44000x
```

**Why:** Set lookup time stays flat (constant hash computation regardless of n). List lookup grows
linearly. The gap widens as n grows — this is O(1) vs O(n) made visible.
</details>

---

<a id="q8"></a>

### Q8 · amortized-append — When is list.append Actually O(n)? 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


`list.append` is described as O(1) average. Explain the edge case where a single `append` call
costs O(n), why this still gives O(1) amortized, and what "amortized" means in plain terms.

<details>
<summary>Hint</summary>
What happens to the underlying array when the list runs out of allocated capacity?
</details>

<details>
<summary>Answer</summary>

**The edge case:** Python lists are backed by a C array. When you `append` and the array is full,
Python allocates a new, larger array (typically 1.125x to 2x the current size), copies all existing
elements to the new array, then adds the new element. That copy is **O(n)**.

**Why it is still O(1) amortized:**

Think of it like a rechargeable battery. You pay a big charge (O(n) copy) once, then get many
cheap appends (O(1) each) before the next charge. Spreading the big cost across all the cheap
operations gives an average cost of O(1) per append.

Formally: if a list doubles in size at each resize, starting from 1:
- Copies at sizes 1, 2, 4, 8, 16, ... n → total copies = 1+2+4+...+n = 2n
- Total appends = n
- Cost per append = 2n / n = **O(1) amortized**

```python
import sys

lst = []
prev_size = sys.getsizeof(lst)
for i in range(20):
    lst.append(i)
    curr_size = sys.getsizeof(lst)
    if curr_size != prev_size:
        print(f"Resized at len={len(lst)}: {prev_size} → {curr_size} bytes")
        prev_size = curr_size
```

**Why:** "Amortized O(1)" means: average cost per operation over a long sequence of operations,
even if individual operations occasionally cost more.
</details>

---

<a id="q9"></a>

### Q9 · frequency-counter — Pick the Right Structure for a Frequency Counter 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


You need to count how many times each word appears in a document (a list of strings). What is the
cleanest and most Pythonic solution? Write it.

<details>
<summary>Hint</summary>
Python's standard library has a type purpose-built for exactly this. It also handles missing keys
without any `if` guards.
</details>

<details>
<summary>Answer</summary>

```python
from collections import Counter

words = ["apple", "banana", "apple", "cherry", "banana", "apple"]

freq = Counter(words)
# Counter({'apple': 3, 'banana': 2, 'cherry': 1})

freq["apple"]          # 3
freq["missing"]        # 0  ← no KeyError
freq.most_common(2)    # [('apple', 3), ('banana', 2)]
```

Without `Counter`, the dict approach is also O(n) and perfectly valid:

```python
freq = {}
for word in words:
    freq[word] = freq.get(word, 0) + 1
```

**Why `Counter` wins:** It is a `dict` subclass — all operations are O(1) insert and O(1) lookup.
It adds `most_common()`, missing-key-returns-0 behavior, and arithmetic on counts. Zero extra
complexity cost compared to a plain dict.
</details>

---

<a id="q10"></a>

### Q10 · o-n-squared-to-o-n — Rewrite Duplicate Detection from O(n²) to O(n) 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


The function below detects duplicate values in a list. It runs in O(n²). Rewrite it in O(n).

```python
def has_duplicate(items: list) -> bool:
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                return True
    return False
```

Then extend it to: `find_first_duplicate(items) -> any` — return the first value that appears more
than once (or `None`).

<details>
<summary>Hint</summary>
A set tracks what you have already seen. One pass through the list, checking membership in the
seen-set, is O(n) total.
</details>

<details>
<summary>Answer</summary>

```python
# O(n) — has_duplicate
def has_duplicate(items: list) -> bool:
    seen = set()
    for item in items:
        if item in seen:    # O(1) set membership
            return True
        seen.add(item)      # O(1) set insert
    return False


# O(n) — find_first_duplicate
def find_first_duplicate(items: list):
    seen = set()
    for item in items:
        if item in seen:
            return item     # first item seen for the second time
        seen.add(item)
    return None
```

**Complexity breakdown:**
- Space: O(n) for the `seen` set — trade memory for speed.
- Time: n iterations × O(1) per iteration = **O(n)**.
- Original: n × n comparisons = **O(n²)**.

**Why:** The nested loop compares every pair. The set-based version remembers what it has seen
using O(1) hash lookups — no repeated scanning of the earlier portion of the list.
</details>

---

## Navigation

- [Back to theory](./theory.md)
- [Practice locally](./practice_local.py)
- [Parent folder practice](../practice.md)
