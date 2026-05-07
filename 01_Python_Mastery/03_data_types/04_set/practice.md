# 🎯 set — Practice Problems

> 12 problems · Sets from basics to real-world deduplication
> Write your answer in `practice_local.py` first, then use the dropdowns.

---

## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| Q1–Q3 | Creating · add/remove · {} trap | 🟢 |
| Q4–Q6 | Membership · deduplication · iteration | 🟢 |
| Q7–Q9 | Set math operations | 🟡 |
| Q10–Q12 | Real-world patterns | 🟡 |

---

### Q1 · set — Creating Sets

**Problem:**
Show 3 ways to create a set. Then demonstrate the `{}` trap — show that `{}` creates a dict, not a set. Show how to create an empty set correctly.

```python
# Way 1: set literal
# Way 2: from a list
# Way 3: from a string

# The {} trap:
# your code here

# Empty set:
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`{1, 2, 3}` is a set literal. `set([...])` converts a list. `set("text")` gives unique characters. An empty `{}` is a dict — use `set()` for an empty set.

</details>

<details>
<summary>✅ Answer</summary>

```python
# Way 1: set literal
s1 = {1, 2, 3, 4}
print(s1)           # {1, 2, 3, 4}

# Way 2: from a list (also removes duplicates)
s2 = set([1, 2, 2, 3, 3, 3])
print(s2)           # {1, 2, 3}

# Way 3: from a string (unique characters only)
s3 = set("hello")
print(s3)           # {'h', 'e', 'l', 'o'}  — only one 'l'

# The {} trap:
trap = {}
print(type(trap))   # <class 'dict'>  ← NOT a set!

# Empty set — must use set():
empty = set()
print(type(empty))  # <class 'set'>  ✅
```

**Why:** Python uses `{}` for dict literals. A set literal only works when you put items inside — `{1, 2}`. An empty `{}` has nothing to distinguish it from a dict, so Python defaults to dict. Always use `set()` for an empty set.

</details>

---

### Q2 · set — Add and Remove

**Problem:**
`tags = {"python", "web", "api"}`. Add `"ml"` to it. Remove `"web"` safely. Then try to remove `"java"` safely — it does not exist. Print the set after each step.

```python
tags = {"python", "web", "api"}
# add "ml"
# remove "web" safely
# try to remove "java" safely (it does not exist)
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`.add()` adds one item. `.discard()` removes without raising an error if the item is missing. `.remove()` raises a `KeyError` if the item is not found.

</details>

<details>
<summary>✅ Answer</summary>

```python
tags = {"python", "web", "api"}

tags.add("ml")
print(tags)            # {'python', 'web', 'api', 'ml'}  (order may vary)

tags.discard("web")
print(tags)            # {'python', 'api', 'ml'}

tags.discard("java")   # does nothing — no error
print(tags)            # {'python', 'api', 'ml'}
```

**Why:** Use `.discard()` when you are not sure if the item exists — it is the safe option. `.remove()` is only appropriate when you know the item is present and want an error if it is not.

</details>

---

### Q3 · set — Immutable Elements

**Problem:**
Why can you add `"hello"` and `42` to a set but not `[1, 2, 3]`? Show the error you get when you try to add a list. Then show what you can use instead.

```python
s = set()
s.add("hello")   # works?
s.add(42)        # works?
s.add([1, 2, 3]) # works?
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Sets use a hash table. Only hashable (immutable) types can be hashed. Lists are mutable so they cannot be hashed. A tuple works as a replacement.

</details>

<details>
<summary>✅ Answer</summary>

```python
s = set()
s.add("hello")    # works — strings are immutable and hashable
s.add(42)         # works — ints are immutable and hashable
print(s)          # {'hello', 42}

# s.add([1, 2, 3])  → TypeError: unhashable type: 'list'

# Fix: use a tuple instead
s.add((1, 2, 3))
print(s)          # {'hello', 42, (1, 2, 3)}
```

**Why:** A set computes a hash value to decide where to store each element. Lists are mutable — if the list changed after being added, its hash would change too, making it unfindable in the table. Tuples are immutable, so they have stable hashes and work fine.

</details>

---

### Q4 · set — Membership Check

**Problem:**
`valid_domains = {"gmail.com", "yahoo.com", "outlook.com"}`. Check if `"gmail.com"` and `"hotmail.com"` are valid. Then demonstrate in a comment why `in` on a set is much faster than `in` on a list.

```python
valid_domains = {"gmail.com", "yahoo.com", "outlook.com"}
# check gmail.com
# check hotmail.com
# explain the speed difference
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `"domain" in valid_domains`. For the speed comparison, think about what Python has to do to check membership in a list of 1 million items vs a set of 1 million items.

</details>

<details>
<summary>✅ Answer</summary>

```python
valid_domains = {"gmail.com", "yahoo.com", "outlook.com"}

print("gmail.com" in valid_domains)    # True
print("hotmail.com" in valid_domains)  # False

# Speed difference:
# List: Python checks every item one by one — O(n)
#   1 million items = up to 1 million comparisons
#
# Set: Python computes hash("hotmail.com"), jumps directly to that slot — O(1)
#   1 million items = same speed as 10 items

# Proof with timing (optional):
import time

big_list = list(range(1_000_000))
big_set  = set(range(1_000_000))

start = time.time()
999_999 in big_list
print(f"List: {time.time() - start:.6f}s")  # slow

start = time.time()
999_999 in big_set
print(f"Set:  {time.time() - start:.6f}s")  # nearly instant
```

**Why:** The `in` operator on a set is O(1) — constant time regardless of set size. On a list it is O(n) — it scans from the start until it finds a match. For membership checks, always prefer a set.

</details>

---

### Q5 · set — Deduplication

**Problem:**
`visits = ["home", "about", "home", "contact", "about", "home"]`. Remove all duplicates and print the unique pages. Print how many unique pages there are.

```python
visits = ["home", "about", "home", "contact", "about", "home"]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Convert the list to a set. Use `len()` on the set to count unique items. Convert back to a list if you need list behavior.

</details>

<details>
<summary>✅ Answer</summary>

```python
visits = ["home", "about", "home", "contact", "about", "home"]

unique_pages = set(visits)
print(unique_pages)            # {'home', 'about', 'contact'}  (order may vary)
print(f"Unique page count: {len(unique_pages)}")   # 3
```

**Why:** Converting to a set is the most concise way to deduplicate a list. Python automatically discards duplicates as it builds the set. This pattern appears constantly in real codebases — deduplicating IDs, emails, tags, and URLs.

</details>

---

### Q6 · set — Iteration

**Problem:**
`colors = {"red", "green", "blue", "yellow"}`. Iterate over the set and print each color. Note the important difference from iterating over a list.

```python
colors = {"red", "green", "blue", "yellow"}
# iterate and print each color
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

A `for` loop works on sets just like lists. The key difference: you cannot predict the order of the output.

</details>

<details>
<summary>✅ Answer</summary>

```python
colors = {"red", "green", "blue", "yellow"}

for color in colors:
    print(color)

# Output (order is NOT guaranteed — may differ every run):
# blue
# red
# yellow
# green
```

**Why:** Sets have no defined order — internally they are hash tables, not sequences. Python may produce the items in any order, and that order can change between runs or Python versions. If you need a consistent order, use `sorted(colors)` to iterate in alphabetical order.

</details>

---

### Q7 · set — Union

**Problem:**
`python_devs = {"Alice", "Bob", "Charlie"}` and `js_devs = {"Bob", "Diana", "Charlie", "Eve"}`. Find all unique developers across both teams.

```python
python_devs = {"Alice", "Bob", "Charlie"}
js_devs     = {"Bob", "Diana", "Charlie", "Eve"}
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use the `|` operator for union, or call `.union()`. Union means "everyone in either set" — duplicates are still discarded.

</details>

<details>
<summary>✅ Answer</summary>

```python
python_devs = {"Alice", "Bob", "Charlie"}
js_devs     = {"Bob", "Diana", "Charlie", "Eve"}

all_devs = python_devs | js_devs
print(all_devs)
# {'Alice', 'Bob', 'Charlie', 'Diana', 'Eve'}  — Bob and Charlie appear once

# Equivalent using method:
all_devs = python_devs.union(js_devs)
```

**Why:** Union combines two sets and keeps every element, but still enforces the "no duplicates" rule. Bob and Charlie are in both teams but appear only once in the result. This is useful for merging mailing lists, user pools, or feature flags.

</details>

---

### Q8 · set — Intersection

**Problem:**
Using the same `python_devs` and `js_devs` sets from Q7, find developers who know BOTH Python and JavaScript.

```python
python_devs = {"Alice", "Bob", "Charlie"}
js_devs     = {"Bob", "Diana", "Charlie", "Eve"}
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use the `&` operator for intersection, or call `.intersection()`. Intersection means "only what is in both sets".

</details>

<details>
<summary>✅ Answer</summary>

```python
python_devs = {"Alice", "Bob", "Charlie"}
js_devs     = {"Bob", "Diana", "Charlie", "Eve"}

both = python_devs & js_devs
print(both)
# {'Bob', 'Charlie'}

# Equivalent using method:
both = python_devs.intersection(js_devs)
```

**Why:** Intersection keeps only the overlap — elements present in every set you combine. This is useful for finding shared items: users with multiple roles, products in multiple categories, or IDs that appear in multiple datasets.

</details>

---

### Q9 · set — Difference and Symmetric Difference

**Problem:**
Using the same developer sets, find two things:
1. Developers who know Python only (not JavaScript).
2. Developers who know exactly one language (not both).

```python
python_devs = {"Alice", "Bob", "Charlie"}
js_devs     = {"Bob", "Diana", "Charlie", "Eve"}
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `-` for difference (items in the left set but not the right). Use `^` for symmetric difference (items in either set but not both).

</details>

<details>
<summary>✅ Answer</summary>

```python
python_devs = {"Alice", "Bob", "Charlie"}
js_devs     = {"Bob", "Diana", "Charlie", "Eve"}

# Python-only devs (in python_devs but not in js_devs):
python_only = python_devs - js_devs
print(python_only)   # {'Alice'}

# Devs who know exactly one language (in one set but not both):
one_language = python_devs ^ js_devs
print(one_language)  # {'Alice', 'Diana', 'Eve'}
```

**Why:** Difference (`-`) removes everything the right set has from the left. Symmetric difference (`^`) keeps what is exclusive to each side and discards the overlap. Think of it as "XOR for sets" — only the items that belong to exactly one group.

</details>

---

### Q10 · set — Permission Check

**Problem:**
`permissions_user = {"read", "write"}`, `permissions_role = {"read", "write", "delete", "admin"}`. A task requires `{"read", "write"}`. Check if the user has all the required permissions for the task.

```python
permissions_user     = {"read", "write"}
permissions_role     = {"read", "write", "delete", "admin"}
required_permissions = {"read", "write"}
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `.issubset()` or the `<=` operator to check if all required permissions are contained in what the user has.

</details>

<details>
<summary>✅ Answer</summary>

```python
permissions_user     = {"read", "write"}
permissions_role     = {"read", "write", "delete", "admin"}
required_permissions = {"read", "write"}

# Check if user has all required permissions:
has_access = required_permissions.issubset(permissions_user)
print(f"User can perform task: {has_access}")   # True

# Equivalent using <= operator:
has_access = required_permissions <= permissions_user
print(f"User can perform task: {has_access}")   # True

# The role can definitely perform the task:
role_access = required_permissions <= permissions_role
print(f"Role can perform task: {role_access}")  # True
```

**Why:** `issubset()` returns `True` if every element of the required set exists in the target set. This is the standard pattern for permission checks — compare required permissions against granted permissions without needing to loop manually.

</details>

---

### Q11 · set — Unique Characters

**Problem:**
Given the string `"hello world"`, find all unique characters using a set. Print them sorted. Count how many unique characters there are (including the space).

```python
text = "hello world"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`set(string)` gives you all unique characters automatically. Use `sorted()` to put them in a predictable order.

</details>

<details>
<summary>✅ Answer</summary>

```python
text = "hello world"

unique_chars = set(text)
print(unique_chars)           # {'h', 'e', 'l', 'o', ' ', 'w', 'r', 'd'}  (order varies)
print(sorted(unique_chars))   # [' ', 'd', 'e', 'h', 'l', 'o', 'r', 'w']
print(f"Unique characters: {len(unique_chars)}")   # 8
```

**Why:** Python iterates over each character in the string when you call `set(string)`, discarding duplicates automatically. `"hello world"` has 11 characters but only 8 unique ones — 'l' and 'o' appear multiple times, the space appears once. This pattern is used in anagram detection, character frequency analysis, and password validation.

</details>

---

### Q12 · set — frozenset as Dict Key

**Problem:**
Store color palettes using `frozenset` as dictionary keys. Create entries for `{"red", "blue"}` mapping to `"purple-ish"` and `{"red", "yellow"}` mapping to `"orange-ish"`. Then look up the palette for a given combination of colors.

```python
palettes = {
    frozenset({"red", "blue"}):   "purple-ish",
    frozenset({"red", "yellow"}): "orange-ish",
}
# look up what you get from red + blue
# look up what you get from yellow + red (same as red + yellow)
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

A `frozenset` is immutable and therefore hashable — it can be used as a dict key. Order does not matter: `frozenset({"red", "blue"})` and `frozenset({"blue", "red"})` are the same key.

</details>

<details>
<summary>✅ Answer</summary>

```python
palettes = {
    frozenset({"red", "blue"}):   "purple-ish",
    frozenset({"red", "yellow"}): "orange-ish",
}

# Look up red + blue:
combo = frozenset({"red", "blue"})
print(palettes[combo])                           # purple-ish

# Order does not matter — frozenset treats sets as equal regardless of order:
combo2 = frozenset({"yellow", "red"})
print(palettes[combo2])                          # orange-ish

# You can also look up directly:
print(palettes[frozenset({"blue", "red"})])      # purple-ish
```

**Why:** A regular `set` is mutable and cannot be hashed, so it cannot be a dict key. `frozenset` is the immutable version — same set operations, but hashable. This makes it useful as a dict key anywhere the key is a collection of items where order does not matter: color combinations, feature flags, permission groups, or graph edges.

</details>

---

**[🏠 Back to Data Types](../theory.md)**

**Related:** [Theory](./theory.md) · [Exercises](./set_practice.py) · [Interview Q&A](../interview.md)
