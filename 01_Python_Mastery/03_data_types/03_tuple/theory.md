# 📦 Tuple — Python's Immutable Sequence

A tuple is a **sealed list** — same sequence syntax as a list, but immutable, which lets Python hash it and use it as a dict key or set member.

---

## 📌 Learning Priority

**Must Learn:**
creating tuples · single-element tuple (trailing comma) · unpacking · packing · tuple as dict key · when to use tuple vs list

**Should Learn:**
named tuples · `*rest` unpacking · swap idiom · tuple in sets

**Good to Know:**
`sys.getsizeof` comparison · `namedtuple` vs `dataclass` · interning behaviour

**Reference:**
`collections.namedtuple` API · `typing.NamedTuple` (class-based syntax)

---

## 🧱 What Makes Tuples Different — The Immutability Story

Imagine a contract signed in ink. Once the ink dries, the words cannot be edited. A list is a whiteboard — anyone can walk up and erase or add items at any time. A tuple is the signed contract. The immutability is not a restriction; it is a **guarantee**. And guarantees are valuable.

Because a tuple's contents cannot change, Python can answer the question "what is the hash of this object?" once — at creation time — and reuse that answer forever. A list must refuse to answer that question entirely, because the next line of code might mutate it and invalidate any previously computed hash. This is why tuples can be dictionary keys and list members cannot.

**Immutability** means: after creation, you cannot add, remove, or replace any element.

### ASCII Memory Layout — List vs Tuple

```
list [1, 2, 3]:                     tuple (1, 2, 3):
┌──────────────────┐                ┌──────────────────┐
│ ob_size  = 3     │                │ ob_size  = 3     │
│ capacity = 4     │  ← extra slot  │ (no capacity     │
│ ptr[0]  ──► 1    │    reserved    │  field at all)   │
│ ptr[1]  ──► 2    │                │ ptr[0]  ──► 1    │
│ ptr[2]  ──► 3    │                │ ptr[1]  ──► 2    │
│ ptr[3]  = NULL   │  ← wasted      │ ptr[2]  ──► 3    │
└──────────────────┘                └──────────────────┘

   List over-allocates to make                Tuple allocates exactly
   append O(1) amortized.                     what it needs. Nothing more.
```

The list reserves extra capacity so that future `.append()` calls don't trigger a memory reallocation every time. The tuple has no concept of future growth — it never needs extra room.

```python
import sys

lst   = [1, 2, 3]
tup   = (1, 2, 3)

print(sys.getsizeof(lst))   # 88 bytes  (extra allocation + list overhead)
print(sys.getsizeof(tup))   # 64 bytes  (exact fit)
```

The gap grows wider with more elements, and creation time is measurably faster for tuples. In tight loops processing millions of records — common in data engineering — this difference matters.

> 📝 **Practice:** [Q9 — Memory comparison with sys.getsizeof](./practice.md#q9)

---

## ✏️ Creating Tuples — The Trailing Comma Trap

Here is the most common beginner mistake in all of Python's data types. Repeat it until it is automatic: **parentheses do not make a tuple. The comma does.**

Parentheses in Python serve many purposes: grouping arithmetic, calling functions, multi-line expressions. A lone pair of parentheses around a value changes nothing about its type.

```python
# These are ALL tuples:
t1 = (1, 2, 3)        # ← parentheses + commas: obvious tuple
t2 = 1, 2, 3          # ← no parentheses: still a tuple (packing)
t3 = (42,)            # ← one element: the comma is mandatory
t4 = 42,              # ← one element, no parens: also a tuple

# This is NOT a tuple:
not_a_tuple = (42)    # ← just the integer 42 in grouping parens

print(type(t1))           # <class 'tuple'>
print(type(t2))           # <class 'tuple'>
print(type(t3))           # <class 'tuple'>
print(type(not_a_tuple))  # <class 'int'>   ← the trap
```

### ASCII — The Trailing Comma Rule

```
(42)   →  just 42    No comma = no tuple
(42,)  →  (42,)      One comma = one-element tuple
42,    →  (42,)      Parens optional, comma required
```

```python
# Practical gotcha: function that seems to return a tuple but doesn't
def get_score():
    return (95)    # ← returns int 95, NOT a tuple

def get_score_correct():
    return (95,)   # ← returns (95,), a proper one-element tuple

# More realistic case where this bites you:
data = (100)              # you think: "a tuple of one item"
for x in data:            # TypeError: 'int' object is not iterable
    print(x)
```

### Creating from Other Sequences

```python
# Convert any iterable to tuple
from_list   = tuple([1, 2, 3])     # (1, 2, 3)
from_string = tuple("abc")         # ('a', 'b', 'c')
from_range  = tuple(range(5))      # (0, 1, 2, 3, 4)
empty       = ()                   # empty tuple
also_empty  = tuple()              # also empty tuple
```

> 📝 **Practice:** [Q1 — Creating tuples, Q2 — Trailing comma](./practice.md#q1)

---

## 🔍 Accessing Tuples — Same Interface, Read-Only

Think of a tuple as a read-only database record. You can SELECT any field by index or slice. You cannot UPDATE, INSERT, or DELETE. The interface for reading is identical to a list, and this is intentional — anywhere you read from a list, you can swap in a tuple with zero changes.

```python
months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

# Indexing
print(months[0])      # "Jan"        ← zero-based
print(months[-1])     # "Dec"        ← negative: count from end

# Slicing
print(months[0:3])    # ("Jan", "Feb", "Mar")
print(months[::3])    # ("Jan", "Apr", "Jul", "Oct")  ← every 3rd

# Length and membership
print(len(months))    # 12
print("Jun" in months)  # True
print("Jul" not in months)  # False

# Methods (tuples have only two)
scores = (88, 95, 72, 95, 88, 95)
print(scores.count(95))   # 3       ← how many times 95 appears
print(scores.index(72))   # 2       ← index of first 72
```

### What You CANNOT Do

```python
point = (10, 20)

point[0] = 99       # TypeError: 'tuple' object does not support item assignment
point.append(30)    # AttributeError: 'tuple' object has no attribute 'append'
del point[0]        # TypeError: 'tuple' object doesn't support item deletion
```

The error is not a runtime check that blocks you — it is a fundamental property of the object. Tuples do not carry the machinery for mutation at all.

> 📝 **Practice:** [Q3 — Immutability and TypeError](./practice.md#q3)

---

## 🔓 Unpacking — The Superpower of Tuples

If immutability is what makes tuples trustworthy, **unpacking** is what makes them addictive. Unpacking assigns each element of a tuple to a separate variable in a single expression. It is the cleanest multi-variable assignment in any mainstream language.

### Basic Unpacking

```python
# Assign all elements to named variables at once
name, age, city = ("Alice", 25, "Mumbai")  # ← left side matches shape of right side
print(name)   # "Alice"
print(age)    # 25
print(city)   # "Mumbai"

# Works with any sequence — not just tuples
r, g, b = (255, 128, 0)          # RGB colour components
lat, lng = (37.7749, -122.4194)  # GPS coordinate
```

### `*rest` Unpacking (Python 3)

When you don't know how many elements come after the first few, use `*` to capture the remainder. The `*` variable always collects into a **list** (not a tuple — see Gotchas).

```python
first, *rest = (1, 2, 3, 4, 5)
print(first)   # 1
print(rest)    # [2, 3, 4, 5]   ← NOTE: rest is a list, not a tuple

head, *middle, tail = (10, 20, 30, 40, 50)
print(head)    # 10
print(middle)  # [20, 30, 40]
print(tail)    # 50

# Real-world: grab the first API result, ignore the rest
top_result, *_ = fetch_search_results(query)  # ← _ is a conventional "discard" name
```

### The Swap Idiom

This is a Python classic. To swap two variables, most languages require a temporary variable:

```c
// C / Java
int temp = a;
a = b;
b = temp;
```

Python does it in one line:

```python
a = 10
b = 20
a, b = b, a     # ← Python evaluates the right side FIRST
print(a)  # 20
print(b)  # 10
```

Why does this work? Python evaluates the entire right-hand side before any assignment begins. `b, a` is evaluated as a tuple `(20, 10)`, stored temporarily, then unpacked into `a` and `b` from left to right. No explicit temporary variable needed because the tuple itself is the temporary storage.

```
Step 1: evaluate right side   →   (b, a)  →  (20, 10)   [temporary tuple]
Step 2: unpack left to right  →   a = 20, b = 10
```

### Unpacking in For Loops

This is one of the most common patterns in production Python. Any time you iterate over a sequence of pairs or tuples, unpack directly in the loop header.

```python
results = [("Alice", 92), ("Bob", 85), ("Carol", 97)]

# Without unpacking — noisy
for item in results:
    print(item[0], item[1])    # ← works but opaque

# With unpacking — clean and readable
for name, score in results:    # ← immediately clear what each variable means
    print(f"{name}: {score}")
```

### Functions Returning Multiple Values

In Python, a function that `return`s multiple comma-separated values is returning a single tuple. The parentheses are optional.

```python
def minmax(lst):
    return min(lst), max(lst)   # ← returns a tuple: (min_val, max_val)

result = minmax([3, 1, 4, 1, 5, 9, 2, 6])
print(result)         # (1, 9)
print(type(result))   # <class 'tuple'>

# Unpack the return value directly at the call site
lo, hi = minmax([3, 1, 4, 1, 5, 9, 2, 6])
print(lo, hi)   # 1 9
```

> 📝 **Practice:** [Q4 — Basic unpacking, Q5 — Swap idiom, Q6 — Packing](./practice.md#q4)

---

## 🗝️ Tuple as Dict Key — Why This Matters

Imagine you are building a 2D grid cache. You want to store the computed value for every `(x, y)` coordinate you have already visited, so you don't recompute it. You need to use the coordinate as a dictionary key.

With a list, Python refuses:

```python
cache = {}
cache[[3, 7]] = compute_value(3, 7)   # TypeError: unhashable type: 'list'
```

With a tuple, it works perfectly:

```python
cache = {}
cache[(3, 7)] = compute_value(3, 7)   # ← (3, 7) is hashable: valid key
cache[(0, 0)] = compute_value(0, 0)
cache[(3, 7)]  # retrieve previously computed result

# Common shorthand — the outer parens are optional in dict subscript context:
cache[3, 7] = compute_value(3, 7)     # ← Python sees this as cache[(3, 7)]
```

### Why Hashing Requires Immutability

A dictionary key must produce the same hash value for the lifetime of the key. If a list `[3, 7]` could change to `[3, 8]` after being inserted as a key, Python would look for it in the wrong hash bucket and the dictionary would be silently corrupted. Python's solution: refuse to hash mutable objects entirely.

```
hash([1, 2, 3])   # TypeError: unhashable type: 'list'
hash((1, 2, 3))   # 2528502973977326415  ← stable, cacheable
```

### Tuples in Sets

The same logic applies to sets. Set membership relies on hashing, so only hashable objects can be stored in a set.

```python
# Storing coordinate pairs as a set (e.g. "visited" in a pathfinding algorithm)
visited = set()
visited.add((0, 0))      # ← works: tuple is hashable
visited.add((3, 7))
visited.add([1, 2])      # TypeError: unhashable type: 'list'

print((3, 7) in visited)  # True   ← O(1) lookup
```

### Important Caveat: Nested Mutability

A tuple is only hashable if ALL of its elements are hashable. A tuple containing a list is not hashable:

```python
t = (1, [2, 3])         # tuple containing a list
hash(t)                 # TypeError: unhashable type: 'list'
t in {(1, 2)}           # TypeError — can't check set membership
```

> 📝 **Practice:** [Q7 — Tuple as dict key, Q8 — Tuple in sets](./practice.md#q7)

---

## ⚖️ When to Use Tuple vs List — The Decision Rule

The clearest decision rule in Python: use a **tuple** when the meaning of the data is fixed by position (coordinates, a database row, an RGB value), use a **list** when the collection itself grows or changes over time (search results, a queue, a shopping cart).

The distinction is semantic, not just mechanical. A tuple communicates intent: "these N things belong together and none of them will change." A list communicates: "this is a mutable collection."

| Scenario | Use | Reason |
|---|---|---|
| GPS coordinate `(lat, lng)` | tuple | Fixed pair of facts |
| List of cities to visit | list | Will be reordered / items added |
| RGB colour `(255, 0, 0)` | tuple | Fixed three-channel value |
| Student grades over a semester | list | Grows as grades are recorded |
| Function returning `name + age` | tuple | Two related values, returned together |
| Active users in a session | list | Joins and leaves over time |
| Database row from `cursor.fetchone()` | tuple | Row is a fact; don't mutate DB results |
| Config keys used as a cache key | tuple | Needs to be hashable |

### Quick Decision Flowchart

```
Does this data represent a fixed group of related values?
        │
       YES                            NO
        │                              │
Will it ever grow,                 → Use a list
change, or be reordered?
        │
       NO
        │
Does it need to be a dict key or in a set?
        │
  YES / NO
        │
   → Use a tuple
```

---

## 🏷️ Named Tuples — Readable Tuples

A regular tuple forces you to remember what each position means. Index 0 is latitude, index 1 is longitude — but nothing in the code says so. **`collections.namedtuple`** gives each position a name.

```python
# Before namedtuple: positional access is opaque
point = (10, 20)
print(point[0])    # what does index 0 mean?
print(point[1])    # is this x or y?

# After namedtuple: self-documenting
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])    # ← define the type
p = Point(x=10, y=20)                     # ← create an instance

print(p.x)        # 10   ← named access
print(p.y)        # 20
print(p[0])       # 10   ← positional access still works
print(p)          # Point(x=10, y=20)  ← readable repr
```

### A Richer Example

```python
from collections import namedtuple

Employee = namedtuple("Employee", ["name", "department", "salary"])

# Imagine this row comes from a database query
row = Employee("Alice", "Engineering", 145000)

print(row.name)          # "Alice"
print(row.department)    # "Engineering"
print(row.salary)        # 145000
print(row._asdict())     # OrderedDict([('name', 'Alice'), ...])  ← useful for JSON

# Named tuples are still tuples — immutable, hashable
emp_set = {row}          # valid: can be added to a set
```

### namedtuple vs dataclass — When to Use Which

```
namedtuple:
  ✓ Simple, read-only data containers
  ✓ Need tuple behaviour (indexing, unpacking, hashing)
  ✓ Minimal memory overhead
  ✗ Cannot have default values easily (Python < 3.6.1)
  ✗ No methods beyond what tuple provides

dataclass (Python 3.7+):
  ✓ Need methods or custom behaviour
  ✓ Need mutable fields
  ✓ Need default values and type hints natively
  ✓ Need __post_init__ validation
  ✗ Not hashable by default (mutable)
  ✗ Slightly more overhead

Rule of thumb: read-only record with no logic → namedtuple
              needs methods, defaults, or mutation → dataclass
```

> 📝 **Practice:** [Q10 — namedtuple for a database record](./practice.md#q10)

---

## ⚠️ Common Mistakes

### 1. `(1)` is not a tuple

```python
t = (1)
print(type(t))    # <class 'int'>  ← NOT a tuple

t = (1,)          # ← add the trailing comma
print(type(t))    # <class 'tuple'>
```

### 2. Trying to mutate a tuple

```python
point = (10, 20)
point[0] = 99    # TypeError: 'tuple' object does not support item assignment

# Workaround: create a new tuple
point = (99, point[1])   # ← produces a new tuple (99, 20)
```

### 3. Tuple of lists — the mutability gotcha

The tuple itself cannot be reassigned, but the objects it points to are not frozen.

```python
t = ([1, 2], [3, 4])     # tuple of two lists
t[0].append(99)          # ← this WORKS — you're mutating the list, not the tuple
print(t)                 # ([1, 2, 99], [3, 4])
hash(t)                  # TypeError — now t is not hashable (contains a list)
```

```
t = ( [1, 2] , [3, 4] )
      │            │
      ▼            ▼
  list obj      list obj      ← these can still be mutated
  [1, 2, 99]   [3, 4]

The tuple's slot still points to the same list — the slot didn't change.
But the list itself changed. Python considers this legal.
```

### 4. `*rest` gives a list, not a tuple

```python
first, *rest = (1, 2, 3, 4)
print(type(rest))    # <class 'list'>  ← list, not tuple!

# If you need a tuple:
rest = tuple(rest)
```

### 5. Confusing `.count()` with `.remove()`

```python
t = (1, 2, 2, 3)
t.count(2)     # 2   ← returns HOW MANY times 2 appears (does NOT remove anything)
               #        lists have .remove() but tuples do not
```

### 6. Empty tuple `()` vs single-element `(x,)`

```python
empty  = ()         # zero elements
single = (42,)      # one element — the comma is not decoration
print(len(empty))   # 0
print(len(single))  # 1
```

---

## 🔥 Production Patterns

### Pattern 1 — Database Rows

Every database cursor in Python returns results as tuples. `cursor.fetchall()` gives a list of tuples. Treat these as immutable records — do not convert them to lists unless you have a reason.

```python
import sqlite3

conn = sqlite3.connect("app.db")
cursor = conn.cursor()
cursor.execute("SELECT name, email, role FROM users WHERE active = 1")

rows = cursor.fetchall()   # List[tuple]

for name, email, role in rows:   # ← unpack directly in the loop
    print(f"{name} ({role}): {email}")
```

### Pattern 2 — Function Returning Multiple Values

This is the idiomatic Python way to return several related values. The caller can either capture the whole tuple or unpack immediately.

```python
def parse_header(raw_header: str):
    """Returns (status_code, content_type, content_length)."""
    parts = raw_header.split("|")
    return int(parts[0]), parts[1].strip(), int(parts[2])

# Caller unpacks:
status, ctype, length = parse_header("200 | application/json | 1048")

# Or captures the whole tuple for later:
header_info = parse_header("200 | application/json | 1048")
```

### Pattern 3 — Location-Based Caching

GPS coordinates as dictionary keys — a direct application of tuple hashing.

```python
from functools import lru_cache

# Manual cache using tuple keys
_elevation_cache: dict[tuple[float, float], float] = {}

def get_elevation(lat: float, lng: float) -> float:
    key = (lat, lng)                        # ← tuple as cache key
    if key not in _elevation_cache:
        _elevation_cache[key] = fetch_from_api(lat, lng)
    return _elevation_cache[key]

# Or use lru_cache — it hashes the arguments (which must be hashable)
@lru_cache(maxsize=1024)
def get_elevation_cached(lat: float, lng: float) -> float:   # floats are hashable
    return fetch_from_api(lat, lng)
```

### Pattern 4 — Unpacking API Response Fields

APIs often return arrays of fixed-structure records. Unpack at point of use to keep code self-documenting.

```python
# Hypothetical API response: list of [timestamp, metric_name, value]
metrics = [
    ["2024-01-15T10:00:00", "cpu_usage", 72.4],
    ["2024-01-15T10:00:00", "memory_mb", 1842.0],
    ["2024-01-15T10:00:00", "request_count", 1503],
]

for ts, metric, value in metrics:          # ← unpack 3-element list as if it were a tuple
    print(f"[{ts}] {metric} = {value}")
```

### Pattern 5 — Compound Dictionary Keys

When your lookup requires multiple dimensions, use a tuple key instead of nested dicts.

```python
# Nested dict (verbose, harder to query)
price_table = {"USD": {"large": 9.99, "small": 4.99}}
price = price_table["USD"]["large"]

# Tuple key (flat, queryable, hashable)
price_table = {
    ("USD", "large"): 9.99,
    ("USD", "small"): 4.99,
    ("EUR", "large"): 8.99,
}
price = price_table[("USD", "large")]   # direct O(1) lookup
```

> 📝 **Practice:** [Q11 — Production database pattern, Q12 — Compound key cache](./practice.md#q11)

---

## 🎯 Interview Angles

These are the angles interviewers take on tuples. Know the answers cold.

**"Why can't a list be a dictionary key?"**
Lists are mutable and therefore unhashable. A dictionary key must produce a stable hash for its lifetime. Mutating a list after inserting it as a key would place it in the wrong hash bucket, silently corrupting the dictionary. Python prevents this by refusing to hash mutable types.

**"What is the difference between `(1)` and `(1,)`?"**
`(1)` is the integer 1 — parentheses here are just grouping. `(1,)` is a one-element tuple. The comma is what signals "tuple" to the parser.

**"Is a tuple of lists immutable?"**
The tuple itself is immutable — its slots (pointers) cannot be reassigned. But if a slot points to a mutable object like a list, that list can still be mutated. The tuple is not deeply immutable. A tuple of lists is also not hashable.

**"When would you choose a tuple over a namedtuple?"**
When the number of fields is small (2–3), the field names are obvious from context, or the code is low-level and you want minimal overhead. Use namedtuple when the tuple will be passed around and readers need to know what `point[0]` means without checking the source.

**"How does the swap idiom `a, b = b, a` work?"**
Python evaluates the right-hand side completely before any assignment. `b, a` becomes a temporary tuple `(old_b, old_a)`. That tuple is then unpacked into `a` and `b` in order.

---

**[Back to Data Types](../theory.md)** | **[Practice Problems](./practice.md)** | **[Cheatsheet](../cheetsheet.md)**

**Related Topics:** [Lists](../02_list/theory.md) · [Dictionaries](../05_dict/theory.md) · [Sets](../04_set/theory.md)
