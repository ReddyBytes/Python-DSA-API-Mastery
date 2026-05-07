# 🗂️ dict — The Most Important Data Structure in Python

A dict lets you find data by **name** instead of position — `user["email"]` beats `user[3]` every time, and nearly everything in Python (JSON, kwargs, object attributes) is backed by one.

---

## 📌 Learning Priority

**Must Learn:**
creating dicts · `d["key"]` access · `.get()` safe access · `.keys()` `.values()` `.items()` · adding · updating · deleting · iterating · dict comprehension

**Should Learn:**
`collections.defaultdict` · `collections.Counter` · `.setdefault()` · dict unpacking `**d` · nested dicts

**Good to Know:**
insertion order guarantee (Python 3.7+) · `|` merge operator (Python 3.9+) · `.pop()` with default · `.popitem()`

**Reference:**
`collections.OrderedDict` · `collections.ChainMap`

---

## 🔬 How Dicts Work — The Hash Table Story

Imagine a phone book with 10 million entries. If you want "Alice Zhang's number", you do not start
at page 1 and read every name. You jump straight to the "Z" section — the alphabetical index acts
as a shortcut. Python dicts use the same idea, but with math instead of letters. Every key is run
through a **hash function** that converts it to a number. That number points directly to the memory
slot (called a **bucket**) where the value lives. No scanning, no looping — one calculation, one
lookup. That is why dict access is `O(1)` regardless of dict size.

A **hash table** is the underlying data structure. Python maintains an array of buckets. When you
write `d["name"] = "Alice"`, Python computes `hash("name")`, takes that number modulo the array
size, and drops `"Alice"` into that bucket. When you later read `d["name"]`, Python does the same
hash computation and jumps directly to the right bucket.

```
d = {"name": "Alice", "age": 25, "city": "Mumbai"}

Hash table internals (simplified, 8 buckets):
┌─────────────────────────────────────────────────────┐
│  bucket 0:  [empty]                                 │
│  bucket 1:  key="city"   hash=...1  → value="Mumbai"│
│  bucket 2:  [empty]                                 │
│  bucket 3:  key="name"   hash=...3  → value="Alice" │
│  bucket 4:  [empty]                                 │
│  bucket 5:  key="age"    hash=...5  → value=25      │
│  bucket 6:  [empty]                                 │
│  bucket 7:  [empty]                                 │
└─────────────────────────────────────────────────────┘

d["name"]:  hash("name") % 8 → bucket 3 → "Alice"    O(1)
d["phone"]: hash("phone") % 8 → bucket 6 → empty → KeyError
```

### Key Collision

Sometimes two different keys hash to the same bucket — a **collision**. Python resolves this with
**open addressing**: it probes nearby buckets until it finds an empty slot or the matching key.
Collisions are rare and handled automatically. You never see them in normal code.

```
hash("name")  % 8 = 3   → bucket 3: store "Alice"
hash("mane")  % 8 = 3   → bucket 3: occupied! → probe bucket 4 → store "lion mane"

Lookup:
d["name"] → bucket 3 → key matches "name" → return "Alice"   ✓
d["mane"] → bucket 3 → key is "name" not "mane" → probe 4 → key matches → return "lion mane"  ✓
```

### What Can Be a Key?

**Keys must be hashable** — their hash value must never change during their lifetime. Immutable
objects are hashable. Mutable objects are not.

```
Hashable (valid keys):    strings, ints, floats, tuples, frozensets, bool
Not hashable (invalid):   lists, dicts, sets

d["name"] = "Alice"       # ✓  string key
d[42]     = "answer"      # ✓  int key
d[(1, 2)] = "point"       # ✓  tuple key
d[[1, 2]] = "point"       # ✗  TypeError: unhashable type: 'list'
```

**Values can be anything** — strings, lists, other dicts, functions, class instances.

### Insertion Order Guarantee (Python 3.7+)

Python 3.7 made insertion order a language guarantee. Keys are returned in the order they were
added.

```python
d = {}
d["c"] = 3
d["a"] = 1
d["b"] = 2

list(d.keys())   # ["c", "a", "b"]  ← insertion order, not sorted
```

> 📝 **Practice:** [Q1 — Create a dict](./practice.md#q1--dict--create-a-book-dict)

---

## 🏗️ Creating Dicts — 4 Ways

```python
# ── 1. Dict literal — most common ─────────────────────────────
person = {
    "name": "Alice",
    "age":  25,
    "city": "Mumbai"
}

# ── 2. dict() constructor — readable for simple cases ─────────
person = dict(name="Alice", age=25, city="Mumbai")
# Note: keys become strings automatically. No quotes needed.

# ── 3. dict.fromkeys() — create a dict with identical defaults ─
keys = ["math", "science", "english"]
scores = dict.fromkeys(keys, 0)      # ← all values start at 0
# {"math": 0, "science": 0, "english": 0}

# Common use: initialising counters or flags for a fixed set of keys.

# ── 4. Dict comprehension — build from a sequence ──────────────
squares = {x: x**2 for x in range(1, 6)}
# {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
```

> 📝 **Practice:** [Q1 — Create a book dict](./practice.md#q1--dict--create-a-book-dict)

---

## 🔑 Accessing Values — `[]` vs `.get()`

This is one of the most important habits in Python. The wrong choice crashes production; the right
choice makes your code robust.

Think of a config file. Not every deployment has every config key. A development environment might
omit `LOG_LEVEL` entirely. If your code does `config["LOG_LEVEL"]`, it crashes on that deployment.
If it does `config.get("LOG_LEVEL", "INFO")`, it silently uses a sensible default and keeps
running. One character difference; enormous operational difference.

```python
person = {"name": "Alice", "age": 25}

# ── Square brackets: use only when key MUST exist ──────────────
print(person["name"])       # "Alice"
print(person["phone"])      # KeyError: 'phone'  ← crash!

# ── .get(): returns None if key is missing — never crashes ─────
print(person.get("name"))           # "Alice"
print(person.get("phone"))          # None        ← safe
print(person.get("phone", "N/A"))   # "N/A"       ← with default

# ── Production-grade config reading ────────────────────────────
config = {"host": "db.prod.local", "port": 5432}

timeout    = config.get("timeout", 30)        # ← default 30 seconds
log_level  = config.get("log_level", "INFO")  # ← default INFO
debug_mode = config.get("debug", False)       # ← default off
```

Rule: use `d["key"]` when you wrote the dict yourself and you know the key exists. Use `.get()`
whenever the dict comes from outside your code (API response, config file, user input, database
row).

> 📝 **Practice:** [Q2 — Safe access with .get()](./practice.md#q2--dict--safe-access)

---

## ✏️ Adding, Updating, and Deleting

```python
person = {"name": "Alice", "age": 25}

# ── Adding a new key ────────────────────────────────────────────
person["email"] = "alice@example.com"   # ← creates key if absent

# ── Updating an existing key ────────────────────────────────────
person["age"] = 26                       # ← overwrites silently

# ── update() — merge another dict in ───────────────────────────
person.update({"age": 27, "city": "Delhi"})
# Overwrites "age", adds "city". Original keys not in update() are untouched.

# ── setdefault() — add only if key is absent ───────────────────
person.setdefault("country", "India")   # ← adds "country"
person.setdefault("name", "Bob")        # ← does nothing — "name" exists
print(person["name"])                   # still "Alice"

# ── del — remove a key ─────────────────────────────────────────
del person["email"]                     # ← KeyError if key is missing

# ── .pop() — remove AND return value ───────────────────────────
age = person.pop("age")                 # ← returns 27, removes key
val = person.pop("phone", None)         # ← safe: returns None if missing

# ── .popitem() — remove and return last inserted pair ──────────
last_pair = person.popitem()            # ← returns ("country", "India")
# Useful for processing a dict like a stack.

# ── .clear() — empty the dict ──────────────────────────────────
person.clear()                          # ← {} but same object in memory
```

> 📝 **Practice:** [Q4 — Add, update, delete](./practice.md#q4--dict--add-update-delete)

---

## 🔄 Iterating — `.keys()`, `.values()`, `.items()`

Most beginners loop over a dict like `for k in d:` which only gives keys. In real code, you almost
always want both the key and the value. Reaching for `.items()` should be automatic.

Think of a report card. You do not just want the subject names. You want "Math: 95, Science: 88".
That is `.items()` — paired, side by side, every time.

```python
scores = {"Alice": 95, "Bob": 87, "Charlie": 92}

# ── Keys only ──────────────────────────────────────────────────
for name in scores:           # ← same as for name in scores.keys()
    print(name)
# Alice
# Bob
# Charlie

# ── Values only ────────────────────────────────────────────────
for score in scores.values():
    print(score)
# 95  87  92

# ── Keys AND values — use this in production ───────────────────
for name, score in scores.items():
    print(f"{name}: {score}")
# Alice: 95
# Bob: 87
# Charlie: 92

# ── Filtering while iterating ──────────────────────────────────
high_scorers = {k: v for k, v in scores.items() if v >= 90}
# {"Alice": 95, "Charlie": 92}
```

### Views vs Lists

`.keys()`, `.values()`, and `.items()` return **view objects**, not lists. A view is a live window
into the dict — if you modify the dict, the view reflects the change instantly.

```python
d = {"a": 1, "b": 2}
keys = d.keys()          # ← view object
d["c"] = 3
print(list(keys))        # ["a", "b", "c"]  ← picked up the new key!

# To get a static snapshot:
keys_snapshot = list(d.keys())   # ← real list, won't update
```

> 📝 **Practice:** [Q5 — Iterate](./practice.md#q5--dict--iterate)

---

## ⚡ Dict Comprehension — The Pythonic Shortcut

Dict comprehension is the dict equivalent of a list comprehension. It builds a new dict in one
expression instead of three lines of for-loop boilerplate. Once you see the pattern, you reach for
it instinctively.

```python
# Syntax:
# { key_expression : value_expression  for item in iterable  if condition }

# ── Side-by-side comparison ────────────────────────────────────
# For-loop version:
squares = {}
for x in range(1, 6):
    squares[x] = x**2

# Comprehension version — identical result:
squares = {x: x**2 for x in range(1, 6)}
# {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

# ── Real example 1: invert a dict ──────────────────────────────
country_code = {"India": "IN", "USA": "US", "Germany": "DE"}
code_country  = {v: k for k, v in country_code.items()}
# {"IN": "India", "US": "USA", "DE": "Germany"}

# ── Real example 2: filter — keep only passing scores ──────────
scores = {"Alice": 75, "Bob": 45, "Charlie": 92, "Diana": 38}
passing = {name: score for name, score in scores.items() if score >= 60}
# {"Alice": 75, "Charlie": 92}

# ── Real example 3: zip two lists into a dict ──────────────────
names  = ["Alice", "Bob", "Charlie"]
scores = [95, 87, 92]
result = {name: score for name, score in zip(names, scores)}
# {"Alice": 95, "Bob": 87, "Charlie": 92}
```

> 📝 **Practice:** [Q8 — Dict comprehension](./practice.md#q8--dict--dict-comprehension)

---

## 🗄️ Nested Dicts — The Real-World Structure

Every JSON API response is a nested dict. When you call a REST API, parse a config file, or
deserialise a database row, you get dicts inside dicts. Knowing how to read, write, and safely
navigate them is non-negotiable production knowledge.

```python
# Building a nested dict:
students = {
    "alice": {
        "grade": 10,
        "gpa":   9.2,
        "subjects": ["Math", "Science", "English"]
    },
    "bob": {
        "grade": 11,
        "gpa":   8.5,
        "subjects": ["Commerce", "Economics"]
    }
}

# ── Accessing nested values ─────────────────────────────────────
print(students["alice"]["gpa"])              # 9.2
print(students["bob"]["subjects"][0])        # "Commerce"

# ── The danger ─────────────────────────────────────────────────
print(students["alice"]["phone"])            # KeyError: 'phone'
print(students["charlie"]["gpa"])            # KeyError: 'charlie'

# ── Safe access pattern — chain .get() with empty dict fallback ─
phone = students.get("alice", {}).get("phone", "N/A")
# students.get("alice", {}) → returns alice's dict or {} if "alice" missing
# .get("phone", "N/A")      → returns phone or "N/A" if key missing
# Result: "N/A"  — never crashes

# ── Real-world API response ─────────────────────────────────────
api_response = {
    "status": "success",
    "data": {
        "user": {
            "id":    1042,
            "name":  "Alice",
            "email": "alice@example.com"
        }
    }
}

user_email = api_response.get("data", {}).get("user", {}).get("email", "unknown")
# "alice@example.com"
```

> 📝 **Practice:** [Q7 — Nested dict](./practice.md#q7--dict--nested-dict)

---

## 🔢 The Counting Pattern — `.get(key, 0) + 1`

This is the most common dict pattern in interviews and production. Word frequency counters, event
counters, inventory management, log aggregation — the problem is always the same: you have a
sequence of items and you want to know how many times each one appears. The pattern is always the
same too.

```python
text = "the quick brown fox jumps over the lazy dog the"

# ── Manual counting — the foundational pattern ─────────────────
freq = {}
for word in text.split():
    freq[word] = freq.get(word, 0) + 1
    # freq.get(word, 0) → returns current count, or 0 if first time seen
    # + 1               → increment

print(freq)
# {"the": 3, "quick": 1, "brown": 1, "fox": 1, ...}

# ── collections.Counter — the one-liner ────────────────────────
from collections import Counter

freq = Counter(text.split())
# Counter({"the": 3, "quick": 1, "brown": 1, ...})

# Counter extras:
print(freq.most_common(3))   # [("the", 3), ("quick", 1), ("brown", 1)]
print(freq["the"])            # 3
print(freq["missing"])        # 0  ← never KeyError (returns 0 for missing)
```

> 📝 **Practice:** [Q9 — Word counter](./practice.md#q9--dict--word-counter)

---

## 🗂️ `defaultdict` — Never Check Before Adding

The most annoying dict pattern in Python is this:

```python
# The verbose way — you see this everywhere in beginner code:
groups = {}
for student, grade in data:
    if student not in groups:         # ← checking existence before every write
        groups[student] = []
    groups[student].append(grade)
```

You check if the key exists, create a list, then append. Every time. `defaultdict` eliminates the
check by automatically creating a default value the first time a new key is accessed.

```python
from collections import defaultdict

# ── defaultdict(list) — auto-creates [] for new keys ───────────
groups = defaultdict(list)
for student, grade in [("Alice", 95), ("Bob", 87), ("Alice", 88)]:
    groups[student].append(grade)    # ← no existence check needed

print(dict(groups))
# {"Alice": [95, 88], "Bob": [87]}

# ── defaultdict(int) — auto-creates 0 for new keys ─────────────
counter = defaultdict(int)
for word in "the quick brown fox the".split():
    counter[word] += 1               # ← no .get(word, 0) needed

# ── defaultdict(set) — auto-creates set() for new keys ─────────
tags = defaultdict(set)
tags["python"].add("language")
tags["python"].add("scripting")
tags["sql"].add("database")

# ── Real-world: grouping employees by department ────────────────
employees = [
    ("Engineering", "Alice"),
    ("Marketing",   "Bob"),
    ("Engineering", "Charlie"),
    ("Marketing",   "Diana"),
]

by_dept = defaultdict(list)
for dept, name in employees:
    by_dept[dept].append(name)

# {"Engineering": ["Alice", "Charlie"], "Marketing": ["Bob", "Diana"]}
```

> 📝 **Practice:** [Q11 — defaultdict grouping](./practice.md#q11--dict--defaultdict)

---

## 🔀 Merging Dicts — 3 Ways

```python
defaults = {"timeout": 30, "retries": 3, "log_level": "INFO"}
overrides = {"timeout": 60, "debug": True}

# ── 1. .update() — mutates the original dict ───────────────────
config = defaults.copy()          # ← copy first, then mutate
config.update(overrides)
# {"timeout": 60, "retries": 3, "log_level": "INFO", "debug": True}
# overrides["timeout"] = 60 wins — later dict always wins on conflict

# ── 2. {**d1, **d2} — creates a NEW dict (Python 3.5+) ─────────
config = {**defaults, **overrides}
# Same result. Non-destructive — defaults and overrides unchanged.
# Order matters: {**overrides, **defaults} would keep timeout=30

# ── 3. d1 | d2 — cleanest syntax (Python 3.9+) ─────────────────
config = defaults | overrides
# Same result. Reads like "defaults merged with overrides".

# ── |= for in-place merge ───────────────────────────────────────
defaults |= overrides             # ← mutates defaults in place
```

> 📝 **Practice:** [Q12 — Merge dicts](./practice.md#q12--dict--merge-dicts)

---

## ⚠️ Common Mistakes

### 1. `d["key"]` on a possibly missing key

```python
user = {"name": "Alice"}
print(user["email"])          # KeyError — crashes in production
print(user.get("email", ""))  # "" — safe
```

### 2. Modifying a dict while iterating over it

```python
d = {"a": 1, "b": 2, "c": 3}

# This crashes:
for key in d:
    if d[key] < 2:
        del d[key]            # RuntimeError: dictionary changed size during iteration

# Safe: iterate over a copy of keys
for key in list(d.keys()):    # ← list() takes a snapshot
    if d[key] < 2:
        del d[key]            # ✓ works
```

### 3. Using a mutable object as a key

```python
d = {}
d[[1, 2]] = "value"           # TypeError: unhashable type: 'list'
d[(1, 2)] = "value"           # ✓ tuple is hashable
```

### 4. Confusing `.keys()` view with a list

```python
d = {"a": 1}
keys = d.keys()               # view object, not a list
d["b"] = 2
print(keys)                   # dict_keys(["a", "b"]) — live update!

# If you need a static snapshot:
keys = list(d.keys())
```

### 5. `{}` is an empty dict, not an empty set

```python
empty_dict = {}               # ← dict
empty_set  = set()            # ← set (use set(), never {})
type({})                      # <class 'dict'>
```

### 6. Shallow copy gotcha with nested dicts

```python
original = {"name": "Alice", "scores": [95, 87]}
copy     = original.copy()    # ← shallow copy

copy["name"] = "Bob"          # ← safe: only changes copy
copy["scores"].append(100)    # ← mutates the SAME list in both!

print(original["scores"])     # [95, 87, 100]  ← original changed!

# Fix: use copy.deepcopy() for nested structures
import copy
deep = copy.deepcopy(original)
```

---

## 🔥 Production Patterns

### 1. Config object with `.get()` defaults

```python
import os

config = {
    "host":      os.getenv("DB_HOST", "localhost"),
    "port":      int(os.getenv("DB_PORT", "5432")),
    "pool_size": int(os.getenv("POOL_SIZE", "10")),
}

# Reading config safely:
timeout    = config.get("timeout", 30)
log_level  = config.get("log_level", "INFO").upper()
```

### 2. Grouping/aggregating with defaultdict

```python
from collections import defaultdict

# Group log lines by severity:
logs = [
    ("ERROR",   "DB connection failed"),
    ("INFO",    "Server started"),
    ("WARNING", "High memory usage"),
    ("ERROR",   "Timeout on request /api/users"),
]

by_severity = defaultdict(list)
for level, message in logs:
    by_severity[level].append(message)

# {"ERROR": ["DB connection failed", "Timeout ..."], "INFO": [...], ...}
```

### 3. Memoisation / caching — store computed results by input

```python
# Manual memoisation:
_cache = {}

def expensive_compute(n):
    if n in _cache:               # ← O(1) cache hit
        return _cache[n]
    result = sum(range(n))        # ← slow computation
    _cache[n] = result            # ← store for next time
    return result

# Production: use functools.lru_cache instead:
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_compute(n):
    return sum(range(n))          # ← automatic dict-based cache
```

### 4. Parsing a JSON API response

```python
import json, urllib.request

# Typical API response (simplified):
raw = '{"status": "ok", "data": {"user_id": 42, "name": "Alice", "roles": ["admin", "user"]}}'
response = json.loads(raw)       # ← JSON becomes a Python dict

user_id  = response.get("data", {}).get("user_id")
name     = response.get("data", {}).get("name", "Unknown")
is_admin = "admin" in response.get("data", {}).get("roles", [])
```

---

## 🎯 Interview Angles

### 1. Two Sum — O(n) with a dict

The brute force is O(n²) — nested loops. The dict solution is O(n) — one pass.

```python
def two_sum(nums, target):
    seen = {}                          # ← value → index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:         # ← O(1) lookup
            return [seen[complement], i]
        seen[num] = i
    return []

# [2, 7, 11, 15], target=9 → [0, 1]  (nums[0]+nums[1] = 9)
```

### 2. Group Anagrams

Sort each word to get a canonical form → use it as the dict key.

```python
from collections import defaultdict

def group_anagrams(words):
    groups = defaultdict(list)
    for word in words:
        key = "".join(sorted(word))    # ← "eat" and "tea" both sort to "aet"
        groups[key].append(word)
    return list(groups.values())

# ["eat","tea","tan","ate","nat","bat"]
# → [["eat","tea","ate"], ["tan","nat"], ["bat"]]
```

### 3. Most Frequent Element

```python
from collections import Counter

def most_frequent(nums):
    return Counter(nums).most_common(1)[0][0]

most_frequent([1, 3, 3, 2, 3, 1])   # 3
```

### 4. Check if Two Dicts Have the Same Keys

```python
d1 = {"a": 1, "b": 2, "c": 3}
d2 = {"b": 9, "c": 7, "a": 0}

set(d1) == set(d2)    # True  ← set(d) gives set of keys
d1.keys() == d2.keys()  # also True — key views support set comparisons
```

### 5. LRU Cache Concept

An **LRU (Least Recently Used) cache** keeps the N most recently accessed items. Classic approach:
`dict` for O(1) lookup + doubly linked list for O(1) eviction. In an interview, explain the concept
then show the Python shortcut:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)   # ← repeated calls hit the cache instantly

# The decorator maintains an internal dict: {args_tuple: return_value}
```

### 6. Frequency-Based Problems — Template

Many interview problems reduce to "count occurrences, then reason about counts":

```python
from collections import Counter

def has_duplicate_within_k(nums, k):
    """True if any value repeats within k positions."""
    window = {}
    for i, num in enumerate(nums):
        if num in window and i - window[num] <= k:
            return True
        window[num] = i             # ← always update to latest index
    return False
```

> 📝 **Practice:** [Q13–Q15 — Interview patterns](./practice.md#q13--dict--two-sum)

---

## 🗺️ Quick Reference

```
Create:     d = {}  |  d = dict()  |  dict.fromkeys(keys, val)  |  {k: v for ...}
Access:     d["key"]  →  KeyError if missing
            d.get("key")  →  None if missing
            d.get("key", default)  →  default if missing
Add/Update: d["key"] = val  |  d.update(other)  |  d.setdefault("key", val)
Delete:     del d["key"]  |  d.pop("key")  |  d.pop("key", default)  |  d.clear()
Iterate:    for k in d  |  for v in d.values()  |  for k,v in d.items()
Merge:      d.update(other)  |  {**d1, **d2}  |  d1 | d2  (3.9+)
Count:      Counter(iterable)  |  d.get(k, 0) + 1
Group:      defaultdict(list)
```

---

**[Back to Data Types](../theory.md)**

**Related:** [Practice Problems](./practice.md) · [Cheatsheet](../cheetsheet.md) · [Interview Q&A](../interview.md)
