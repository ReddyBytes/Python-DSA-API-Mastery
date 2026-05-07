# 📋 list — Python Lists Deep Dive

> Every web app, every data pipeline, every API response is full of lists.
> Master this data structure completely — not just the syntax, but the mental model.

---

## 📌 Learning Priority

**Must Learn (core — used daily):**
creating lists · indexing · slicing · `.append()` `.remove()` `.pop()` · `len()` · iterating · `in` operator · the copy trap

**Should Learn (production-ready):**
`.sort()` vs `sorted()` · `.count()` `.index()` · list comprehension · shallow vs deep copy · `enumerate()` with lists

**Good to Know (interview + advanced):**
two-pointer patterns · dynamic array internals · `[[]] * 3` aliasing trap · `bisect` module

**Reference (lookup when needed):**
`array` module · `collections.deque` for O(1) inserts at both ends

---

## 🧠 The Opening Story

Picture a warehouse with a long row of numbered shelves: shelf 0, shelf 1, shelf 2, and so on. You can put anything on any shelf — a book, a box, even another shelf-row. You can add a new shelf at the end in seconds. Inserting a shelf in the middle takes longer because every shelf after it has to shift one position to the right. Removing the last shelf is instant. Removing one from the middle requires the same shift. This is exactly how a Python list works.

A Python list is the most used data structure in the language. Every web app has a list of users. Every API returns a list of records. Every data pipeline builds lists of events, rows, and batches. Unlike arrays in C or Java, a Python list has no fixed size — it grows and shrinks automatically. You never declare a capacity upfront.

Under the hood, Python's list is a **dynamic array**. When the list fills up its reserved memory block, Python quietly allocates a new, larger block — typically 1.5x to 2x the old capacity — copies everything over, and frees the old block. This resize is invisible to you, but it explains two fundamental facts: appending to the end is fast (O(1) amortized), and inserting at position 0 is slow (O(n)) because every element must shift.

Understanding the memory model — references, not values — is the single most important thing to internalize about Python lists. Every bug involving the copy trap, shallow copy, and aliasing comes from not understanding this one thing.

---

## 🔬 Memory Model — How Lists Actually Work

### Lists store references, not values

Imagine a pegboard on the wall with numbered hooks. Each hook doesn't hold the object itself — it holds a string (a pointer) tied to an object sitting somewhere else in memory. The list is just the pegboard and the hooks. The actual values live elsewhere.

This is the mental model that explains everything:

```
lst = ["apple", 42, True]

Memory layout:
                                           Python heap (object pool)
list object (the pegboard)
┌──────────────────────────┐
│ len      = 3             │
│ capacity = 4             │           ┌─────────────────────┐
│ ptr[0] ──────────────────┼──────────▶│ "apple"  (str obj)  │
│ ptr[1] ──────────────────┼──────┐    └─────────────────────┘
│ ptr[2] ──────────────────┼───┐  │    ┌─────────────────────┐
└──────────────────────────┘   │  └───▶│ 42       (int obj)  │
                                │       └─────────────────────┘
                                │       ┌─────────────────────┐
                                └──────▶│ True     (bool obj) │
                                        └─────────────────────┘
```

The list holds POINTERS. When you do `lst[0]`, Python follows the pointer at slot 0 to find the actual string object.

### The alias trap — two names, one list

This is the number one source of list-related bugs:

```python
a = [1, 2, 3]
b = a          # ← b is NOT a copy. b is a second name for the SAME object.

b.append(4)
print(a)       # [1, 2, 3, 4]  ← a "changed" — because a and b ARE the same list
```

In memory:

```
variable table
┌───┬──────┐
│ a │ ─────┼──────┐
├───┼──────┤      ▼
│ b │ ─────┼────▶ [1, 2, 3]  (one list object)
└───┴──────┘
```

Both `a` and `b` are arrows pointing at the same object. Mutating through `b` mutates what `a` sees too — because they are the same thing.

Prove it with `id()`:

```python
a = [1, 2, 3]
b = a
print(id(a) == id(b))   # True  ← same memory address, same object
```

> 📝 **Practice:** [Q8 — Copy Trap](./practice.md#q8--list--copy-trap)

---

## 🏗️ Creating Lists — All 5 Ways

Knowing all the creation patterns matters because each has a different use case in production code.

### Method 1 — literal syntax

The most common way. Direct, readable, fast.

```python
fruits  = ["apple", "banana", "cherry"]
numbers = [10, 20, 30]
mixed   = ["Alice", 25, True, 3.14]   # ← any types, even mixed
empty   = []
```

### Method 2 — `list()` constructor

Converts any iterable into a list. Useful when you get a tuple, a range, or a generator from somewhere else.

```python
from_tuple  = list((1, 2, 3))           # (1,2,3) → [1, 2, 3]
from_string = list("hello")             # → ['h', 'e', 'l', 'l', 'o']
```

### Method 3 — `list(range())`

The standard way to create a list of sequential numbers.

```python
zero_to_nine = list(range(10))          # [0, 1, 2, ..., 9]
evens        = list(range(0, 20, 2))    # [0, 2, 4, ..., 18]
countdown    = list(range(5, 0, -1))    # [5, 4, 3, 2, 1]
```

### Method 4 — list comprehension

The Pythonic way to build a list from a transformation or filter. Full coverage in its own section.

```python
squares    = [x ** 2 for x in range(6)]          # [0, 1, 4, 9, 16, 25]
even_sq    = [x ** 2 for x in range(6) if x % 2 == 0]   # [0, 4, 16]
```

### Method 5 — `*` unpacking

Less common but elegant for combining lists.

```python
a = [1, 2, 3]
b = [4, 5, 6]
combined = [*a, *b]   # [1, 2, 3, 4, 5, 6]  ← flat combination
```

### The `[[]] * n` aliasing trap

Creating a list of lists with `*` is a classic bug. It looks like it creates independent inner lists, but it doesn't:

```python
# WRONG — looks like a 3x3 grid, but it's 3 references to THE SAME inner list
grid = [[0] * 3] * 3
grid[0][0] = 99
print(grid)  # [[99, 0, 0], [99, 0, 0], [99, 0, 0]]  ← ALL rows changed!
```

Why? Because `* 3` copies the pointer three times, not the object:

```
grid = [[0, 0, 0]] * 3

variable table
┌──────────┐
│ grid[0] ─┼──────┐
│ grid[1] ─┼──────┤──▶ [0, 0, 0]  (ONE inner list)
│ grid[2] ─┼──────┘
└──────────┘

All three slots point to the same inner list object.
Mutating via grid[0] mutates what grid[1] and grid[2] see too.
```

The correct way uses a comprehension, which calls `[0] * 3` fresh each iteration:

```python
# CORRECT — each row is a separate, independent list
grid = [[0] * 3 for _ in range(3)]
grid[0][0] = 99
print(grid)  # [[99, 0, 0], [0, 0, 0], [0, 0, 0]]  ← only row 0 changed
```

`[None] * 3` is fine for immutables because you can't mutate `None` in place. The trap only bites with mutable inner objects like lists, dicts, or sets.

> 📝 **Practice:** [Q1 — Create and Append](./practice.md#q1--list--create-and-append)

---

## 🔍 Indexing and Slicing

### Indexing — the same model as strings

Python lists use the same zero-based indexing as strings. Positive indices count from the front; negative indices count from the back.

```
fruits = ["apple", "banana", "cherry", "date", "elderberry"]
index:     0         1          2         3          4
neg:      -5        -4         -3        -2         -1
```

```python
fruits[0]    # "apple"        first item
fruits[-1]   # "elderberry"   last item — always works regardless of list length
fruits[2]    # "cherry"
fruits[-2]   # "date"
```

### Slicing — creates a SHALLOW COPY

Slicing syntax is `[start : stop : step]`. Omitting `start` means the beginning; omitting `stop` means the end.

```python
fruits = ["apple", "banana", "cherry", "date", "elderberry"]

fruits[1:3]    # ["banana", "cherry"]   — stop is exclusive
fruits[:3]     # ["apple", "banana", "cherry"]
fruits[2:]     # ["cherry", "date", "elderberry"]
fruits[::2]    # ["apple", "cherry", "elderberry"]  — every other item
fruits[::-1]   # ["elderberry", "date", "cherry", "banana", "apple"]  — reversed
```

**Critical difference from strings:** slicing a list returns a **shallow copy** — a new list object, but the inner elements are still shared references.

For flat lists (strings, numbers, booleans), shallow copy is perfectly safe. The trap comes with nested lists:

```python
a = [[1, 2], [3, 4]]
b = a[:]          # ← shallow copy: b is a new list, but inner lists are shared

b[0].append(99)   # ← mutating the inner list through b
print(a)          # [[1, 2, 99], [3, 4]]  ← a is affected too!
```

Why? The shallow copy diagram:

```
a = [[1, 2], [3, 4]]
b = a[:]  (shallow copy)

a object                        inner list objects
┌────────┐
│ ptr[0] ┼──────────────────────▶ [1, 2]
│ ptr[1] ┼──────────────────┐    (shared)
└────────┘                  │
                             ▼
b object                   [3, 4]
┌────────┐                  ▲
│ ptr[0] ┼─────────────────/   ← b[0] points to SAME inner list as a[0]
│ ptr[1] ┼─────────────────/
└────────┘

b is a new outer container, but the inner lists are the same objects.
Mutating an inner list via b[0] is the same as mutating it via a[0].
```

> 📝 **Practice:** [Q4 — Slicing](./practice.md#q4--list--slicing)

---

## ✏️ Modifying a List — CRUD Operations

Lists are designed to be changed. This is their defining property — unlike tuples which are immutable. Here's every modification operation you'll use in production, grouped by what they do.

### Adding items

Think of three tools: a hammer that nails one item to the end, a needle that threads one item anywhere, and a staple gun that attaches a whole batch.

```python
items = ["a", "b", "c"]

items.append("d")           # ← O(1) amortized — adds ONE item to the end
print(items)                # ["a", "b", "c", "d"]

items.insert(1, "X")        # ← O(n) — inserts at position 1, shifts everything right
print(items)                # ["a", "X", "b", "c", "d"]

items.extend(["e", "f"])    # ← O(k) — adds each item from another iterable individually
print(items)                # ["a", "X", "b", "c", "d", "e", "f"]
```

**Why `.append()` is fast and `.insert(0, x)` is slow:**

```
Before insert(0, "NEW"):       After insert(0, "NEW"):
┌─────┬─────┬─────┬─────┐     ┌─────┬─────┬─────┬─────┬─────┐
│  a  │  b  │  c  │  d  │     │ NEW │  a  │  b  │  c  │  d  │
└─────┴─────┴─────┴─────┘     └─────┴─────┴─────┴─────┴─────┘
 ptr[0] ptr[1] ptr[2] ptr[3]    Every existing pointer shifted one slot right.
                                That's O(n) pointer moves.
```

If you frequently need to add items to the FRONT, use `collections.deque` instead — it's O(1) for both ends.

**`.append()` vs `.extend()`:**

```python
a = [1, 2, 3]
b = [1, 2, 3]

a.append([4, 5])    # a = [1, 2, 3, [4, 5]]  ← the list itself is one item
b.extend([4, 5])    # b = [1, 2, 3, 4, 5]    ← each item from [4, 5] added flat
```

### Removing items

```python
fruits = ["apple", "banana", "cherry", "banana", "date"]

fruits.remove("banana")   # ← removes FIRST occurrence by VALUE — O(n) scan
print(fruits)             # ["apple", "cherry", "banana", "date"]
                          # notice: second "banana" is still there

last = fruits.pop()       # ← removes and RETURNS the last item — O(1)
print(last)               # "date"

second = fruits.pop(1)    # ← removes and RETURNS item at index 1 — O(n)
print(second)             # "cherry"

del fruits[0]             # ← deletes by index, no return value — O(n)
print(fruits)             # ["banana"]

fruits.clear()            # ← empties the list — O(n) to release references
print(fruits)             # []
```

**When to use which:**
- `.pop()` from the end — implementing a stack (LIFO)
- `.pop(0)` — don't; use `deque.popleft()` instead (O(1) vs O(n))
- `.remove(value)` — when you have the value, not the index
- `del` — clean index-based deletion when you don't need the item back

> 📝 **Practice:** [Q7 — Remove Items](./practice.md#q7--list--remove-items) · [Q3 — Modify](./practice.md#q3--list--modify)

---

## 🔎 Searching and Sorting

### Searching — `in` vs `.index()`

These two tools answer different questions:

```python
fruits = ["apple", "banana", "cherry", "apple"]

# Does it exist? Use `in` — returns bool, doesn't raise exceptions
print("banana" in fruits)    # True
print("mango" in fruits)     # False

# Where is it? Use .index() — returns first position, raises ValueError if missing
print(fruits.index("cherry"))  # 2
print(fruits.index("apple"))   # 0  ← first occurrence only

# Safe pattern for .index() — guard with `in` first
item = "mango"
if item in fruits:
    print(fruits.index(item))
else:
    print("not found")
```

Both `in` and `.index()` do a linear scan — O(n). For large lists where you check membership repeatedly, convert to a `set` for O(1) lookups.

### Sorting — the `.sort()` vs `sorted()` distinction

This is the most common source of a subtle bug: `a = a.sort()`.

```python
scores = [88, 92, 75, 96, 83]

# .sort() — in-place, returns None
scores.sort()
print(scores)               # [75, 83, 88, 92, 96]

# THE BUG: sort returns None, not a list
wrong = scores.sort()
print(wrong)                # None  ← you just lost your sorted list!

# sorted() — returns a NEW sorted list, original unchanged
original = [88, 92, 75, 96, 83]
new_sorted = sorted(original)
print(original)             # [88, 92, 75, 96, 83]  ← untouched
print(new_sorted)           # [75, 83, 88, 92, 96]
```

### Sorting with a key function

The `key` parameter is powerful. It lets you sort by any attribute or derived value:

```python
# Sort list of dicts by a field — real-world API response processing
users = [
    {"name": "Charlie", "age": 35},
    {"name": "Alice",   "age": 28},
    {"name": "Bob",     "age": 41},
]

by_age  = sorted(users, key=lambda u: u["age"])    # youngest first
by_name = sorted(users, key=lambda u: u["name"])   # alphabetical

# Sort a list of tuples by second element
pairs = [(1, "banana"), (3, "apple"), (2, "cherry")]
sorted(pairs, key=lambda x: x[1])  # [( 3, "apple"), (1, "banana"), (2, "cherry")]

# Sort strings by length
words = ["fig", "banana", "apple", "kiwi"]
sorted(words, key=len)              # ["fig", "kiwi", "apple", "banana"]
```

### Reversing

```python
numbers = [1, 2, 3, 4, 5]

numbers.reverse()           # ← in-place, mutates the list, returns None
print(numbers)              # [5, 4, 3, 2, 1]

reversed_copy = numbers[::-1]  # ← creates a new reversed list, original untouched
```

**Rule:** use `.reverse()` when you want to mutate in place. Use `[::-1]` when you want a new reversed copy without touching the original.

> 📝 **Practice:** [Q5 — Sort](./practice.md#q5--list--sort) · [Q6 — Search](./practice.md#q6--list--search)

---

## 🧬 The Copy Trap — Full Explanation

This deserves its own section because most Python list bugs come from here. There are three distinct behaviors depending on how you copy.

### Level 1 — not a copy at all

```python
a = [1, 2, 3]
b = a              # b is an alias — same object, second name
b.append(4)
print(a)           # [1, 2, 3, 4]  ← a changed
print(id(a) == id(b))  # True
```

### Level 2 — shallow copy (works for flat lists, traps nested lists)

```python
a = [1, 2, 3]
b = a.copy()       # or b = a[:] or b = list(a) — all produce a shallow copy

b.append(4)
print(a)           # [1, 2, 3]     ← a is safe
print(id(a) == id(b))  # False — different list objects now
```

But shallow copy only protects the outer container:

```python
a = [[1, 2], [3, 4]]
b = a.copy()        # new outer list, shared inner lists

b[0].append(99)     # mutating the INNER list through b
print(a)            # [[1, 2, 99], [3, 4]]  ← a is damaged
```

### Level 3 — deep copy (fully independent, all levels)

```python
import copy

a = [[1, 2], [3, 4]]
b = copy.deepcopy(a)    # ← recursively copies all nested objects

b[0].append(99)
print(a)                # [[1, 2], [3, 4]]   ← a is fully protected
print(b)                # [[1, 2, 99], [3, 4]]
```

### The three-way comparison diagram

```
a = [[1, 2], [3, 4]]

──────────────────────────────────────────────────────────────
Case 1: b = a            (alias — no copy)

  a ──▶ [ptr0, ptr1]
  b ──▶ [ptr0, ptr1]   ← same outer list
         │      │
         ▼      ▼
       [1,2]  [3,4]    same inner lists

──────────────────────────────────────────────────────────────
Case 2: b = a.copy()     (shallow copy)

  a ──▶ [ptr0, ptr1]    ← different outer list
  b ──▶ [ptr0, ptr1]
         │      │
         ▼      ▼
       [1,2]  [3,4]    STILL same inner lists (shared)

──────────────────────────────────────────────────────────────
Case 3: b = copy.deepcopy(a)   (deep copy)

  a ──▶ [ptr0, ptr1]    ← different outer list
  b ──▶ [ptr0, ptr1]    ← different outer list
         │      │              │      │
         ▼      ▼              ▼      ▼
       [1,2]  [3,4]          [1,2]  [3,4]   DIFFERENT inner lists
```

**Rule for choosing:**
- Flat list (contains only numbers, strings, booleans)? → `.copy()` or `[:]` is sufficient.
- Nested list (contains lists, dicts, objects)? → Use `copy.deepcopy()`.
- Performance matters and you know the structure? → Reconstruct manually.

> 📝 **Practice:** [Q8 — Copy Trap](./practice.md#q8--list--copy-trap) · [Q10 — Nested](./practice.md#q10--list--nested-list)

---

## ⚡ List Comprehensions — The Pythonic Way

Think of a list comprehension as a sentence in English: "Give me X for every Y in Z, but only if condition." That's exactly how the syntax reads.

```
[expression   for item in iterable   if condition]
 ──────────   ─────────────────────  ────────────
 what to keep   where to get items   optional filter
```

### Side-by-side: loop vs comprehension

```python
# for loop version
squares = []
for x in range(1, 6):
    squares.append(x ** 2)
# squares = [1, 4, 9, 16, 25]

# comprehension version — same result, one line
squares = [x ** 2 for x in range(1, 6)]

# with a filter
even_squares = [x ** 2 for x in range(1, 11) if x % 2 == 0]
# [4, 16, 36, 64, 100]
```

### Working with strings

```python
words = ["hello", "world", "python"]
upper = [w.upper() for w in words]              # ["HELLO", "WORLD", "PYTHON"]
long_words = [w for w in words if len(w) > 4]   # ["hello", "world", "python"]
```

### Nested comprehension for flattening a matrix

Read nested comprehensions left to right — the outermost loop comes first:

```python
matrix = [[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]]

flat = [num for row in matrix for num in row]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]

# The loop order matches how you'd write a nested for:
# for row in matrix:
#     for num in row:
#         flat.append(num)
```

### Processing a list of dicts (production pattern)

```python
# API response — list of user records
users = [
    {"name": "Alice", "active": True,  "score": 92},
    {"name": "Bob",   "active": False, "score": 88},
    {"name": "Carol", "active": True,  "score": 79},
]

# Extract names of active users
active_names = [u["name"] for u in users if u["active"]]
# ["Alice", "Carol"]

# Normalize scores to 0–1 range
max_score = max(u["score"] for u in users)
normalized = [u["score"] / max_score for u in users]
```

### Performance note

Comprehensions are slightly faster than equivalent `for` loops with `.append()` because the list object's size grows in one controlled operation rather than incrementally. For very large lists, also consider generator expressions `()` instead of `[]` to avoid building the whole list in memory at once.

**Readability rule:** if a comprehension requires more than one condition and a complex expression, break it into a regular loop. The goal is clarity, not brevity for its own sake.

> 📝 **Practice:** [Q9 — List Comprehension](./practice.md#q9--list--list-comprehension) · [Q14 — Flatten](./practice.md#q14--list--flatten-interview)

---

## ⚠️ Common Mistakes

### 1. `a.sort()` returns None — never assign it

```python
a = [3, 1, 2]
a = a.sort()    # ← BUG: a is now None
print(a)        # None

# Correct: either mutate in place OR use sorted()
a = [3, 1, 2]
a.sort()        # ← mutate in place, don't capture return value
# OR
a = sorted([3, 1, 2])   # ← sorted() returns a new list
```

### 2. Modifying a list while iterating over it

```python
numbers = [1, 2, 3, 4, 5, 6]

# WRONG — skips elements because indices shift during deletion
for n in numbers:
    if n % 2 == 0:
        numbers.remove(n)
print(numbers)  # [1, 3, 5]  ← looks right by accident, but logic is flawed

# CORRECT — iterate over a copy, or use comprehension
numbers = [n for n in numbers if n % 2 != 0]   # ← build a new list
```

### 3. `[[]] * 3` — all rows are the same object

```python
grid = [[]] * 3
grid[0].append(1)
print(grid)     # [[1], [1], [1]]  ← all three changed

# Fix: use a comprehension
grid = [[] for _ in range(3)]
grid[0].append(1)
print(grid)     # [[1], [], []]   ← only the first changed
```

### 4. Shallow copy doesn't protect nested objects

```python
original = [[1, 2], [3, 4]]
copy = original[:]          # shallow copy
copy[0].append(99)
print(original)             # [[1, 2, 99], [3, 4]]  ← damaged

# Fix: use deepcopy for nested structures
import copy
safe_copy = copy.deepcopy(original)
```

### 5. `.remove()` only removes the FIRST occurrence

```python
items = [1, 2, 3, 2, 2]
items.remove(2)
print(items)    # [1, 3, 2, 2]  ← only the first 2 is gone

# Remove ALL occurrences
items = [x for x in items if x != 2]
```

### 6. `.index()` raises `ValueError` for missing items

```python
fruits = ["apple", "banana"]
fruits.index("mango")   # ValueError: 'mango' is not in list

# Safe pattern
if "mango" in fruits:
    pos = fruits.index("mango")
```

> 📝 **Practice:** [Q5 — Sort](./practice.md#q5--list--sort) · [Q8 — Copy Trap](./practice.md#q8--list--copy-trap)

---

## 🔥 Production Patterns

### Pattern 1 — Shopping cart

```python
class ShoppingCart:
    def __init__(self):
        self.items = []

    def add(self, item, price):
        self.items.append({"name": item, "price": price})

    def remove(self, item_name):
        self.items = [i for i in self.items if i["name"] != item_name]  # ← removes ALL matching

    def total(self):
        return sum(i["price"] for i in self.items)

    def contains(self, item_name):
        return any(i["name"] == item_name for i in self.items)

cart = ShoppingCart()
cart.add("Apples", 1.99)
cart.add("Bread", 3.49)
cart.add("Milk", 2.29)
cart.remove("Milk")
print(cart.total())        # 5.48
print(cart.contains("Bread"))  # True
```

### Pattern 2 — Filter active users from an API response

This is a daily task in backend services. Never modify the original response list:

```python
def get_active_users(api_response: list[dict]) -> list[dict]:
    """
    Filter to active users, sort by most recently joined.
    Returns a new list — does not mutate the input.
    """
    active = [u for u in api_response if u.get("active", False)]
    return sorted(active, key=lambda u: u.get("joined_at", ""), reverse=True)

response = [
    {"id": 1, "name": "Alice", "active": True,  "joined_at": "2024-01-15"},
    {"id": 2, "name": "Bob",   "active": False, "joined_at": "2023-08-20"},
    {"id": 3, "name": "Carol", "active": True,  "joined_at": "2024-03-10"},
]

active_users = get_active_users(response)
# [{"id": 3, "name": "Carol", ...}, {"id": 1, "name": "Alice", ...}]
```

### Pattern 3 — Chunk a list into batches

Common in data pipelines when sending API requests or writing database rows in batches:

```python
def chunk(lst: list, size: int) -> list[list]:
    """Split a list into sublists of at most `size` items."""
    return [lst[i:i + size] for i in range(0, len(lst), size)]

records = list(range(1, 23))   # 22 items
batches = chunk(records, 5)
# [[1,2,3,4,5], [6,7,8,9,10], [11,12,13,14,15], [16,17,18,19,20], [21, 22]]

for batch in batches:
    # process_batch(batch)  ← call DB or API in groups of 5
    print(f"Processing {len(batch)} items: {batch}")
```

> 📝 **Practice:** [Q11 — Shopping Cart](./practice.md#q11--list--shopping-cart) · [Q12 — Top and Bottom](./practice.md#q12--list--top-and-bottom) · [Q13 — Deduplicate](./practice.md#q13--list--deduplicate-order-preserved)

---

## 🎯 Interview Angles

### Pattern 1 — Two-pointer: reverse a list in place

Two pointers start at opposite ends and walk toward each other. O(n) time, O(1) space.

```python
def reverse_in_place(lst: list) -> None:
    left, right = 0, len(lst) - 1
    while left < right:
        lst[left], lst[right] = lst[right], lst[left]   # ← swap
        left  += 1
        right -= 1

items = [1, 2, 3, 4, 5]
reverse_in_place(items)
print(items)   # [5, 4, 3, 2, 1]
```

### Pattern 2 — Two-pointer: check palindrome

```python
def is_palindrome(lst: list) -> bool:
    left, right = 0, len(lst) - 1
    while left < right:
        if lst[left] != lst[right]:
            return False
        left  += 1
        right -= 1
    return True

print(is_palindrome([1, 2, 3, 2, 1]))   # True
print(is_palindrome([1, 2, 3]))          # False
```

### Pattern 3 — Sliding window: maximum subarray sum of size k

```python
def max_subarray_sum(nums: list[int], k: int) -> int:
    """Find the maximum sum of any contiguous subarray of length k."""
    if len(nums) < k:
        return 0

    window_sum = sum(nums[:k])          # ← sum the first window
    max_sum    = window_sum

    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]   # ← slide: add new, drop old
        max_sum     = max(max_sum, window_sum)

    return max_sum

print(max_subarray_sum([2, 1, 5, 1, 3, 2], k=3))   # 9  (5 + 1 + 3)
```

### Pattern 4 — Remove duplicates while preserving order

The idiomatic Python one-liner uses `dict.fromkeys()`, which preserves insertion order (Python 3.7+):

```python
items = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
unique = list(dict.fromkeys(items))
print(unique)   # [3, 1, 4, 5, 9, 2, 6]
```

For very large lists, use a `set` for O(1) membership checks:

```python
def deduplicate(lst: list) -> list:
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
```

### Pattern 5 — Flatten a nested list

```python
nested = [[1, 2], [3, 4], [5, 6]]

# One-liner comprehension
flat = [item for sublist in nested for item in sublist]

# For arbitrarily deep nesting, use recursion
def flatten(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))    # ← recurse into sublists
        else:
            result.append(item)
    return result

print(flatten([1, [2, [3, [4]]], 5]))   # [1, 2, 3, 4, 5]
```

### Pattern 6 — Rotate a list by k positions

```python
def rotate(lst: list, k: int) -> list:
    """Rotate list to the right by k positions."""
    if not lst:
        return lst
    k = k % len(lst)            # ← handle k > len(lst) gracefully
    return lst[-k:] + lst[:-k]

print(rotate([1, 2, 3, 4, 5], k=2))    # [4, 5, 1, 2, 3]
print(rotate([1, 2, 3, 4, 5], k=7))    # [4, 5, 1, 2, 3]  (7 % 5 = 2)
```

> 📝 **Practice:** [Q14 — Flatten](./practice.md#q14--list--flatten-interview) · [Q15 — Common Elements](./practice.md#q15--list--common-elements-interview)

---

## 📊 Big-O Quick Reference

| Operation | Time complexity | Notes |
|---|---|---|
| `lst[i]` — index access | O(1) | Direct pointer lookup |
| `lst.append(x)` | O(1) amortized | Occasional O(n) resize, rare |
| `lst.insert(0, x)` | O(n) | Every element shifts right |
| `lst.pop()` — from end | O(1) | No shift needed |
| `lst.pop(i)` — from middle | O(n) | Elements after i shift left |
| `x in lst` | O(n) | Linear scan |
| `lst.index(x)` | O(n) | Linear scan, stops at first match |
| `lst.remove(x)` | O(n) | Scan + shift |
| `lst.sort()` | O(n log n) | Timsort — stable sort |
| `lst[a:b]` — slice | O(k) | k = b - a, copies k references |
| `lst.reverse()` | O(n) | Swaps n/2 pointer pairs |
| `len(lst)` | O(1) | Stored as an attribute |

---

## 📂 Navigation

**[Back to Data Types README](../theory.md)**

| Prev | Next |
|---|---|
| [str — Strings](../01_str/theory.md) | [dict — Dictionaries](../05_dict/theory.md) |

**Related:**
[Practice Problems](./practice.md) · [Cheatsheet](../cheetsheet.md) · [Data Types Overview](../theory.md)
