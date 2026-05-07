# 🎯 set — Python's Most Underused Data Structure

> Every time you need to check "is this item in a collection?", your first instinct is probably to reach for a list. That instinct will cost you dearly at scale.

---

Python's **set** stores items in a hash table — which makes membership checks O(1) whether the set has 10 items or 10 million.

---

## 📌 Learning Priority

**Must Learn:**
creating sets · `{}` vs `set()` · `.add()` `.discard()` `.remove()` · `in` operator · removing duplicates · `|` `&` `-` `^` operations

**Should Learn:**
`.issubset()` `.issuperset()` `.isdisjoint()` · `frozenset` · set comprehension · `|=` `&=` `-=` `^=` in-place operators

**Good to Know:**
set performance vs list benchmark · when to choose set vs dict · sorted iteration pattern

**Reference:**
`symmetric_difference_update()` · `copy()` · `update()` with multiple iterables

---

## 🧠 How Sets Work — The Hash Table Story

This is the section that separates someone who uses sets from someone who understands them. If you skip one section, do not let it be this one.

Imagine a massive filing cabinet with 1,000 numbered drawers. You need to store the word `"apple"`. Instead of picking a random drawer, you run `"apple"` through a formula — a **hash function** — that converts it to a number. `hash("apple")` might return `2647501404539973989`. You then take that number modulo the cabinet size to get a drawer number: `2647501404539973989 % 1000 = 989`. You store `"apple"` in drawer 989.

Later, someone asks: "Is `'apple'` in the cabinet?" You do not open every drawer. You run the same formula: `hash("apple") → 989`. Open drawer 989. It is there. Done.

That is exactly what Python does internally every time you use `in` with a set.

```
set = {"apple", "banana", "cherry"}

Hash function maps each value to a bucket index:

┌─────────────────────────────────────────────────────┐
│  bucket   0: [empty]                                │
│  bucket   1: [empty]                                │
│  bucket   2: [empty]                                │
│  bucket  14: → "banana"                             │
│  bucket  15: [empty]                                │
│  ...                                                │
│  bucket  47: → "apple"                              │
│  ...                                                │
│  bucket 312: → "cherry"                             │
│  ...                                                │
│  bucket 999: [empty]                                │
└─────────────────────────────────────────────────────┘

Lookup "apple":  hash("apple") → 47 → check bucket 47 → FOUND!  O(1)
Lookup "mango":  hash("mango") → 61 → check bucket 61 → EMPTY!  O(1)
Lookup "apple" with 10 items:      same speed
Lookup "apple" with 10,000,000:    same speed
```

### Why items must be hashable

The hash is how Python finds items again. If an item could change after being stored, its hash would change, and Python could never locate it in the cabinet. The drawer it is stored in and the drawer the hash now points to would be different. The item would be permanently lost.

This is why **mutable objects cannot go in a set**:

```
Mutable → hash can change → cannot be in a set
  └── list   [1, 2, 3]  → TypeError: unhashable type: 'list'
  └── dict   {"a": 1}   → TypeError: unhashable type: 'dict'
  └── set    {1, 2}     → TypeError: unhashable type: 'set'

Immutable → hash is stable → can be in a set
  └── int        42
  └── float      3.14
  └── string     "hello"
  └── tuple      (1, 2, 3)       ← only if contents are also immutable
  └── frozenset  frozenset({1})
```

The same rule applies to **dictionary keys** — because dicts use the same hash table mechanism internally.

> 📝 **Practice:** [Q3 — Immutable Elements](./practice.md#q3--set--immutable-elements)

---

## 🔨 Creating Sets — And the `{}` Trap

Python uses curly braces for two completely different things. This is one of the most common beginner mistakes.

```python
# The {} trap — this is a DICT, not a set:
mystery = {}
print(type(mystery))   # <class 'dict'>  ← NOT a set!

# A set LITERAL requires at least one item:
s = {1, 2, 3}
print(type(s))         # <class 'set'>  ✅

# The only safe way to create an EMPTY set:
empty = set()
print(type(empty))     # <class 'set'>  ✅
```

Why did Python do this? Curly braces were already reserved for dicts before sets were added as literals. When Python added set literals, `{1, 2, 3}` works because the comma-separated values make it unambiguous. But `{}` has no items — Python cannot distinguish it from an empty dict, so it defaults to dict.

**Three ways to create a set:**

```python
# 1 — Set literal (values known upfront):
permissions = {"read", "write", "execute"}

# 2 — Convert a list (great for removing duplicates):
raw = [1, 2, 2, 3, 3, 3, 4]
unique = set(raw)               # → {1, 2, 3, 4}

# 3 — Convert a string (unique characters only):
chars = set("hello")            # → {'h', 'e', 'l', 'o'}  — one 'l', not two
```

The `set("hello")` trick is more useful than it looks. Note that `"ll"` becomes a single `'l'` — sets apply deduplication as they consume the iterable, character by character.

> 📝 **Practice:** [Q1 — Creating Sets](./practice.md#q1--set--creating-sets)

---

## ➕ Adding and Removing

Think of a set as a **guest list** with strict rules: every name appears exactly once, and the list does not have a fixed order.

```python
tags = {"python", "backend", "api"}

# .add() — adds one item; silently does nothing if already present:
tags.add("ml")
tags.add("python")     # ← already there, set stays the same
print(tags)            # {'python', 'backend', 'api', 'ml'}  (order not guaranteed)

# .remove() — removes item; raises KeyError if not found:
tags.remove("api")     # works fine
# tags.remove("java")  # ← KeyError: 'java'  — it is not in the set

# .discard() — removes item; SILENTLY does nothing if not found:
tags.discard("backend")   # works fine
tags.discard("java")      # ← no error, no drama — safest option

# .pop() — removes and returns an ARBITRARY item:
item = tags.pop()
print(item)            # could be anything — sets have no order
                       # do NOT use this when you need a specific item

# .clear() — empties the set entirely:
tags.clear()
print(tags)            # set()
```

**Rule of thumb:** use `.discard()` when you are not certain the item is present. Use `.remove()` only when you expect it to be there and want an error if it is not — treating its absence as a bug.

> 📝 **Practice:** [Q2 — Add and Remove](./practice.md#q2--set--add-and-remove)

---

## ⚡ Membership Testing — Why Sets Beat Lists

The performance difference between `in` on a list versus `in` on a set is one of the most dramatic in Python. It is not a minor improvement. It is an algorithmic class difference.

```
List lookup: O(n) — linear time
┌──────────────────────────────────────────────────────┐
│  [0, 1, 2, 3, 4, 5, 6, 7, .............. 999_999]   │
│   ^  check  check  check  check  ............^ found │
│   Start here and scan every item until you find it   │
│   1 item:        1 comparison                        │
│   1,000 items:   up to 1,000 comparisons             │
│   1,000,000:     up to 1,000,000 comparisons         │
└──────────────────────────────────────────────────────┘

Set lookup: O(1) — constant time
┌──────────────────────────────────────────────────────┐
│  hash(999_999) → bucket 47                           │
│  Open bucket 47 → found (or not found)               │
│  1 item:        1 hash + 1 check                     │
│  1,000 items:   1 hash + 1 check                     │
│  1,000,000:     1 hash + 1 check                     │
└──────────────────────────────────────────────────────┘
```

This is not theoretical. You can measure it directly:

```python
import time

data_list = list(range(1_000_000))
data_set  = set(range(1_000_000))

# List — must scan up to 1,000,000 items:
start = time.time()
_ = 999_999 in data_list
print(f"List: {time.time() - start:.6f}s")   # typically ~0.015s–0.025s

# Set — computes hash and jumps directly:
start = time.time()
_ = 999_999 in data_set
print(f"Set:  {time.time() - start:.6f}s")   # typically ~0.000001s
```

The set is roughly 10,000–25,000x faster at this task, and the gap grows linearly as the list grows. The set stays flat.

**Production rule:** if you are checking membership in a collection more than once, convert it to a set first. This is especially true for whitelists, blacklists, valid IDs, and permission lists that are checked on every request.

> 📝 **Practice:** [Q4 — Membership Check](./practice.md#q4--set--membership-check)

---

## 🔁 Deduplication — The One-Liner Pattern

Removing duplicates from a list is one of the most common operations in data processing. Sets make it a single expression.

```python
# Raw event log with repeated page names:
visits = ["home", "about", "home", "contact", "about", "home", "pricing"]

# One-liner deduplication:
unique_pages = list(set(visits))
print(unique_pages)       # ['home', 'about', 'contact', 'pricing']  (order not guaranteed)
print(len(unique_pages))  # 4

# Preserving original order (Python 3.7+ dict trick):
ordered_unique = list(dict.fromkeys(visits))
print(ordered_unique)     # ['home', 'about', 'contact', 'pricing']  ← preserves order
```

Note the tradeoff: `set()` is faster and simpler, but it does not preserve insertion order. If order matters, use `dict.fromkeys()`. If order does not matter, `set()` is the cleanest choice.

> 📝 **Practice:** [Q5 — Deduplication](./practice.md#q5--set--deduplication)

---

## 🔀 Iteration — What You Give Up

Sets are iterable. You can loop over them with `for`, pass them to `len()`, and use them in comprehensions. What you cannot do is predict the order.

```python
colors = {"red", "green", "blue", "yellow"}

# Iteration works — but order is unpredictable:
for color in colors:
    print(color)
# Might print: blue, red, yellow, green
# Or:          green, yellow, blue, red
# Order is determined by hash values, not insertion order

# No indexing — sets are not sequences:
# colors[0]    → TypeError: 'set' object is not subscriptable
# colors[1:3]  → TypeError: 'set' object is not subscriptable

# If you need order + uniqueness:
for color in sorted(colors):    # ← sorted() returns a list, predictable order
    print(color)
# Always: blue, green, red, yellow
```

The reason sets have no order is their hash table structure. Items live in buckets determined by their hash values, not by when they were inserted. There is no index 0 because there is no "first" item in a hash table.

> 📝 **Practice:** [Q6 — Iteration](./practice.md#q6--set--iteration)

---

## ➗ Set Operations — Mathematical Power

Sets implement **set theory** directly. These operations are not just convenient — they map exactly to mathematical set algebra, which means they come with a rich vocabulary and well-understood behavior.

The scenario: you run a platform and you know which users are enrolled in two courses.

```python
python_students  = {"Alice", "Bob", "Charlie", "Diana"}
js_students      = {"Bob", "Eve", "Charlie", "Frank"}
```

### Venn diagram

```
        python_students          js_students
      ┌──────────────────────────────────────┐
      │  Alice   ┌───────────────┐  Eve      │
      │  Diana   │  Bob          │  Frank    │
      │          │  Charlie      │           │
      └──────────┴───────────────┴───────────┘
        A only        both            B only
```

### Union — everyone in either group

```python
# All students enrolled in any course:
everyone = python_students | js_students
# Equivalent: python_students.union(js_students)
print(everyone)
# {'Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank'}

# In-place (modifies python_students):
# python_students |= js_students
```

### Intersection — only what is in both

```python
# Students taking both courses simultaneously:
both_courses = python_students & js_students
# Equivalent: python_students.intersection(js_students)
print(both_courses)
# {'Bob', 'Charlie'}

# In-place:
# python_students &= js_students
```

### Difference — left minus overlap

```python
# Python students who are NOT in the JS course:
python_only = python_students - js_students
# Equivalent: python_students.difference(js_students)
print(python_only)
# {'Alice', 'Diana'}

# JS students who are NOT in the Python course:
js_only = js_students - python_students
print(js_only)
# {'Eve', 'Frank'}

# In-place:
# python_students -= js_students
```

### Symmetric difference — exactly one group, not both

```python
# Students in one course only — not the overlap:
exclusive = python_students ^ js_students
# Equivalent: python_students.symmetric_difference(js_students)
print(exclusive)
# {'Alice', 'Diana', 'Eve', 'Frank'}

# In-place:
# python_students ^= js_students
```

### Full picture

```
A = {1, 2, 3, 4}    B = {3, 4, 5, 6}

      A only │  both  │ B only
      ────────┼────────┼────────
       1, 2   │  3, 4  │  5, 6

A | B  = {1, 2, 3, 4, 5, 6}   union            — everything
A & B  = {3, 4}                intersection     — overlap only
A - B  = {1, 2}                difference       — A minus the overlap
B - A  = {5, 6}                difference       — B minus the overlap
A ^ B  = {1, 2, 5, 6}          sym. difference  — non-overlap from both sides
```

### Subset, superset, disjoint

```python
admins   = {"read", "write", "delete", "admin"}
viewers  = {"read"}
editors  = {"read", "write"}
billing  = {"billing", "export"}

# Is viewers a subset of admins? (every viewer perm exists in admins?)
print(viewers <= admins)            # True  — ← can also use .issubset()
print(viewers.issubset(admins))     # True

# Is admins a superset of editors? (admins has everything editors have, and more?)
print(admins >= editors)            # True  — ← can also use .issuperset()
print(admins.issuperset(editors))   # True

# Do admins and billing share nothing?
print(admins.isdisjoint(billing))   # True  — no overlap at all
```

> 📝 **Practice:** [Q7 — Union](./practice.md#q7--set--union) · [Q8 — Intersection](./practice.md#q8--set--intersection) · [Q9 — Difference and Symmetric Difference](./practice.md#q9--set--difference-and-symmetric-difference)

---

## ❄️ frozenset — The Immutable Set

A `frozenset` is to a `set` what a `tuple` is to a `list`. Same operations, same performance, but **immutable** — which means it is also **hashable**.

```python
# Regular set — mutable, not hashable:
s = {1, 2, 3}
# hash(s)        → TypeError: unhashable type: 'set'
# {s: "value"}   → TypeError: unhashable type: 'set'

# frozenset — immutable, hashable:
fs = frozenset({1, 2, 3})
print(hash(fs))            # some integer — it works
print({fs: "value"})       # {frozenset({1, 2, 3}): 'value'}  ← valid dict key
```

**Where frozenset is useful:**

```python
# 1 — As a dict key where the key is a group of items:
palettes = {
    frozenset({"red", "blue"}):   "purple-ish",
    frozenset({"red", "yellow"}): "orange-ish",
}
combo = frozenset({"blue", "red"})   # order does not matter
print(palettes[combo])               # purple-ish

# 2 — As an element in another set (set of sets):
valid_permission_groups = {
    frozenset({"read"}),
    frozenset({"read", "write"}),
    frozenset({"read", "write", "delete"}),
}
user_perms = frozenset({"read", "write"})
print(user_perms in valid_permission_groups)   # True

# 3 — Constant permission sets that should never change at runtime:
READ_ONLY  = frozenset({"read"})
READ_WRITE = frozenset({"read", "write"})
ADMIN      = frozenset({"read", "write", "delete", "admin"})
```

All set operations (union, intersection, difference, subset checks) work on frozensets exactly like regular sets.

> 📝 **Practice:** [Q12 — frozenset as Dict Key](./practice.md#q12--set--frozenset-as-dict-key)

---

## 🔧 Set Comprehension

Set comprehensions use the same syntax as list comprehensions but produce a set — meaning duplicates are automatically removed.

```python
# List comprehension — keeps duplicates:
squares_list = [x**2 for x in range(-5, 6)]
print(squares_list)   # [25, 16, 9, 4, 1, 0, 1, 4, 9, 16, 25]

# Set comprehension — unique values only:
squares_set = {x**2 for x in range(-5, 6)}
print(squares_set)    # {0, 1, 4, 9, 16, 25}  ← 5² and (-5)² are both 25
```

**Deduplication + transformation in one step:**

```python
# Raw emails with mixed casing from a signup form:
raw_emails = ["Alice@Gmail.COM", "bob@yahoo.com", "ALICE@gmail.com", "carol@outlook.com"]

# Normalize and deduplicate in one expression:
unique_emails = {email.lower() for email in raw_emails}
print(unique_emails)
# {'alice@gmail.com', 'bob@yahoo.com', 'carol@outlook.com'}
# ← the two Alice variants collapsed into one after lowercasing
```

This pattern — normalize then deduplicate — is extremely common in data ingestion pipelines.

---

## ⚠️ Common Mistakes

These are the gotchas that trip up experienced developers, not just beginners.

**1. `{}` creates a dict, not a set**

```python
empty = {}
print(type(empty))   # <class 'dict'>  ← wrong!
empty = set()        # ← correct for empty set
```

**2. Relying on iteration order**

```python
# WRONG assumption:
tags = {"python", "web", "api"}
first_tag = list(tags)[0]   # could be "python", "web", or "api" — unpredictable
                             # the order may change between Python versions or runs

# RIGHT approach when order matters:
first_tag = sorted(tags)[0]  # "api" — alphabetically first, deterministic
```

**3. Trying to store mutable items**

```python
# This fails at the moment you try to add the list:
s = set()
s.add([1, 2, 3])   # TypeError: unhashable type: 'list'

# Fix: use a tuple if the contents are fixed:
s.add((1, 2, 3))   # works — tuple is immutable
```

**4. Using `.pop()` when you need a specific item**

```python
# This removes an ARBITRARY element — not the "first" or "last":
s = {"a", "b", "c"}
x = s.pop()   # could be any of the three — sets have no order
              # do not use pop() when you need a predictable item
```

**5. Assuming set operations modify in place**

```python
a = {1, 2, 3}
b = {3, 4, 5}

# These return NEW sets — they do NOT modify a or b:
result = a | b
print(a)   # {1, 2, 3}  ← unchanged

# To modify in place, use augmented assignment:
a |= b
print(a)   # {1, 2, 3, 4, 5}  ← now modified
```

**6. Nested mutable containers fail silently until you actually try**

```python
# This works at creation but explodes when you try to iterate:
# {{"inner": 1}}  → TypeError at evaluation time

# frozenset is the correct inner container:
s = {frozenset({1, 2}), frozenset({3, 4})}  # works correctly
```

---

## 🔥 Production Patterns

These are the four patterns you will encounter most often in real codebases.

**Pattern 1: One-line deduplication**

```python
def get_unique_user_ids(event_log: list[int]) -> list[int]:
    return list(set(event_log))   # ← single expression, O(n) time

# Used everywhere: IDs, emails, tags, URLs, IP addresses
```

**Pattern 2: High-performance whitelist / blacklist**

```python
# Load once at startup — O(n) to build:
BLOCKED_IPS: set[str] = set(load_blocked_ips_from_db())

# Check on every request — O(1):
def is_allowed(ip: str) -> bool:
    return ip not in BLOCKED_IPS   # ← constant time regardless of blocklist size
```

**Pattern 3: Finding common tags between two content items**

```python
def shared_tags(post_a: dict, post_b: dict) -> set[str]:
    return set(post_a["tags"]) & set(post_b["tags"])   # intersection

post_a = {"title": "Python tips", "tags": ["python", "tutorial", "beginner"]}
post_b = {"title": "Advanced Python", "tags": ["python", "advanced", "tutorial"]}

print(shared_tags(post_a, post_b))   # {'python', 'tutorial'}
# Used in: content recommendation, "related posts", tag-based routing
```

**Pattern 4: Permission check using issubset**

```python
def can_perform(action_requires: set[str], user_has: set[str]) -> bool:
    return action_requires.issubset(user_has)   # are all required perms present?

user_permissions  = {"read", "write", "comment"}
delete_requires   = {"read", "write", "delete"}
comment_requires  = {"read", "comment"}

print(can_perform(delete_requires, user_permissions))    # False — missing "delete"
print(can_perform(comment_requires, user_permissions))   # True
```

**Pattern 5: Finding missing items in a pipeline**

```python
def find_missing_ids(expected: list[int], received: list[int]) -> set[int]:
    return set(expected) - set(received)   # difference: expected but not received

expected_records = [1, 2, 3, 4, 5, 6, 7, 8]
received_records = [1, 2, 4, 6, 8]

missing = find_missing_ids(expected_records, received_records)
print(missing)   # {3, 5, 7}  ← these records need to be re-fetched
```

> 📝 **Practice:** [Q10 — Permission Check](./practice.md#q10--set--permission-check) · [Q11 — Unique Characters](./practice.md#q11--set--unique-characters) · [Q12 — frozenset as Dict Key](./practice.md#q12--set--frozenset-as-dict-key)

---

## 🎯 Interview Angles

These are the angles that come up in Python interviews when sets are the topic.

**"Why is set membership O(1)?"**
The hash function converts any value to a bucket index in constant time. Checking if a key is in that bucket is also constant time. The total work does not grow with the number of items in the set.

**"What makes an object hashable?"**
It must implement `__hash__()` and `__eq__()`. For built-in types: immutable = hashable (int, str, tuple, frozenset). Mutable = not hashable (list, dict, set). User-defined classes are hashable by default (using `id()` for hash), but if you override `__eq__` you must also override `__hash__`.

**"What is the difference between `.discard()` and `.remove()`?"**
Both remove an item. `.remove()` raises `KeyError` if the item is not present. `.discard()` does nothing if the item is absent. Use `.discard()` when absence is acceptable. Use `.remove()` when absence indicates a bug.

**"When would you use frozenset over set?"**
When you need to use a set as a dictionary key, store a set inside another set, or represent a group of items that should never be modified after creation (e.g., a role's permissions).

**"How do you deduplicate a list while preserving order?"**
`list(set(items))` removes duplicates but does not preserve order. `list(dict.fromkeys(items))` removes duplicates and preserves insertion order (Python 3.7+).

**"What is symmetric difference and when is it useful?"**
`A ^ B` returns items in A or B but not both. Useful for detecting changes: `old_tags ^ new_tags` gives you exactly what was added and what was removed in one operation.

---

## 📂 Navigation

**[Back to Data Types](../theory.md)**

| Previous | Current | Next |
|---|---|---|
| [dict](../05_dict/theory.md) | **set** | [tuple](../03_tuple/theory.md) |

**Related:** [Practice Problems](./practice.md) · [Interview Q&A](../interview.md) · [Cheatsheet](../cheetsheet.md)
