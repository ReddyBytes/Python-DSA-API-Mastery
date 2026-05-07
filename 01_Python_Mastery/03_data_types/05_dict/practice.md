# 🗂️ dict — Practice Problems

> 15 problems · Dictionaries from basics to production patterns
> Write your answer in `practice_local.py` first, then use the dropdowns.

---

## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| Q1–Q3 | Creating · accessing · `.get()` | 🟢 |
| Q4–Q6 | Add · update · delete · iterate | 🟢 |
| Q7–Q9 | Nested · comprehension · counting | 🟡 |
| Q10–Q12 | Real-world patterns | 🟡 |
| Q13–Q15 | Interview patterns | 🟠 |

---

### Q1 · dict — Create a Book Dict

**Problem:**
Create a dictionary for a book with keys: `title`, `author`, `year`, `pages`. Use values: `"Python Crash Course"`, `"Eric Matthes"`, `2019`, `544`. Print the author and the year.

```python
# create the book dict
# print author and year
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `{}` with `"key": value` pairs. Access values with `dict["key"]`.

</details>

<details>
<summary>✅ Answer</summary>

```python
book = {
    "title":  "Python Crash Course",
    "author": "Eric Matthes",
    "year":   2019,
    "pages":  544
}
print(book["author"])   # Eric Matthes
print(book["year"])     # 2019
```

**Why:** Dictionary keys act like labels. You look up values by their name instead of by a number position, which makes the code self-documenting.

</details>

---

### Q2 · dict — Safe Access

**Problem:**
`config = {"host": "localhost", "port": 5432}`. Get `"timeout"` safely with a default of `30`. Also get `"port"` safely. Print both results.

```python
config = {"host": "localhost", "port": 5432}
# get "timeout" with default 30
# get "port" safely
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `.get("key", default)`. If the key exists, you get its value. If not, you get the default.

</details>

<details>
<summary>✅ Answer</summary>

```python
config = {"host": "localhost", "port": 5432}
print(config.get("timeout", 30))   # 30   ← key missing, returns default
print(config.get("port", 0))       # 5432 ← key exists, returns value
```

**Why:** `.get()` never crashes. It is the safe alternative to `dict["key"]` when a key might not exist — which is common for optional config values.

</details>

---

### Q3 · dict — The KeyError Trap

**Problem:**
Show what happens when you access a missing key with `dict["missing_key"]`. Then show how `.get()` handles the same situation gracefully.

```python
person = {"name": "Alice", "age": 25}
# try: person["phone"]  — what error?
# then use .get() for the same lookup
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Square bracket access raises `KeyError` if the key is missing. `.get()` returns `None` (or a default you provide).

</details>

<details>
<summary>✅ Answer</summary>

```python
person = {"name": "Alice", "age": 25}

# person["phone"]  → KeyError: 'phone'

# Safe version:
print(person.get("phone"))              # None
print(person.get("phone", "Not set"))   # Not set
```

**Why:** Use `dict["key"]` only when you are certain the key exists (e.g. you just set it). Use `.get()` whenever there is any chance the key is absent — configuration values, user inputs, API responses.

</details>

---

### Q4 · dict — Add, Update, Delete

**Problem:**
`user = {"name": "Alice", "age": 25, "city": "Delhi"}`. Do three things:
1. Update age to `26`.
2. Add a new key `"email"` with value `"alice@gmail.com"`.
3. Delete `"city"`.

Print the final dict.

```python
user = {"name": "Alice", "age": 25, "city": "Delhi"}
# update age
# add email
# delete city
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`dict["key"] = value` updates or adds. `del dict["key"]` removes.

</details>

<details>
<summary>✅ Answer</summary>

```python
user = {"name": "Alice", "age": 25, "city": "Delhi"}
user["age"] = 26
user["email"] = "alice@gmail.com"
del user["city"]
print(user)
# {'name': 'Alice', 'age': 26, 'email': 'alice@gmail.com'}
```

**Why:** Dicts are mutable — the same syntax (`dict["key"] = value`) both adds new keys and updates existing ones. Python checks if the key already exists and acts accordingly.

</details>

---

### Q5 · dict — Iterate

**Problem:**
`scores = {"Alice": 92, "Bob": 78, "Charlie": 85, "Diana": 96}`.
1. Print all key-value pairs as `"Alice: 92"`.
2. Print only the names where score is above `85`.

```python
scores = {"Alice": 92, "Bob": 78, "Charlie": 85, "Diana": 96}
# print all pairs
# print names with score > 85
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `.items()` to get both key and value in each loop step. Add an `if` condition to filter.

</details>

<details>
<summary>✅ Answer</summary>

```python
scores = {"Alice": 92, "Bob": 78, "Charlie": 85, "Diana": 96}

for name, score in scores.items():
    print(f"{name}: {score}")

print("Above 85:")
for name, score in scores.items():
    if score > 85:
        print(name)
# Alice
# Diana
```

**Why:** `.items()` is the most common way to iterate over a dict because it gives you both the key and value at once. Use `.keys()` or `.values()` when you only need one of them.

</details>

---

### Q6 · dict — Check Key Existence

**Problem:**
`inventory = {"apple": 50, "banana": 30}`. Check if `"mango"` exists before accessing it. Show both the `in` approach and the `.get()` approach.

```python
inventory = {"apple": 50, "banana": 30}
# check "mango" using 'in'
# check "mango" using .get()
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`"key" in dict` returns `True` or `False`. `.get("key")` returns `None` if missing, which is also falsy.

</details>

<details>
<summary>✅ Answer</summary>

```python
inventory = {"apple": 50, "banana": 30}

# Using 'in':
if "mango" in inventory:
    print(inventory["mango"])
else:
    print("mango not found")

# Using .get():
count = inventory.get("mango", 0)
print(f"mango count: {count}")   # mango count: 0
```

**Why:** Use `in` when you want to branch on existence. Use `.get()` when you want a fallback value directly — it is more compact for simple cases.

</details>

---

### Q7 · dict — Nested Dict

**Problem:**
`student = {"name": "Alice", "grades": {"math": 90, "science": 85}}`.
1. Access the science grade.
2. Add `"history": 88` to the grades.

```python
student = {"name": "Alice", "grades": {"math": 90, "science": 85}}
# access science grade
# add history: 88
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Chain the keys: `student["grades"]["science"]`. Adding to a nested dict works the same way.

</details>

<details>
<summary>✅ Answer</summary>

```python
student = {"name": "Alice", "grades": {"math": 90, "science": 85}}
print(student["grades"]["science"])       # 85
student["grades"]["history"] = 88
print(student["grades"])
# {'math': 90, 'science': 85, 'history': 88}
```

**Why:** Nested dicts are accessed by chaining keys — like opening a folder inside a folder. This pattern is everywhere in real data: API responses, config files, JSON.

</details>

---

### Q8 · dict — Dict Comprehension

**Problem:**
`names = ["Alice", "Bob", "Charlie"]`, `scores = [92, 78, 85]`. Create `{"Alice": 92, "Bob": 78, "Charlie": 85}` using `zip` and a dict comprehension.

```python
names = ["Alice", "Bob", "Charlie"]
scores = [92, 78, 85]
# build the dict in one line
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`zip(names, scores)` pairs the two lists. Wrap it in `{k: v for k, v in zip(...)}`.

</details>

<details>
<summary>✅ Answer</summary>

```python
names = ["Alice", "Bob", "Charlie"]
scores = [92, 78, 85]
result = {name: score for name, score in zip(names, scores)}
print(result)
# {'Alice': 92, 'Bob': 78, 'Charlie': 85}
```

**Why:** Dict comprehension is the Pythonic one-liner for building dicts from iterables. `zip()` pairs up the two lists item by item, and the comprehension turns each pair into a key-value entry.

</details>

---

### Q9 · dict — Word Counter

**Problem:**
`text = "the cat sat on the mat the cat"`. Count how many times each word appears. Use the `.get()` counting pattern (not `Counter`).

```python
text = "the cat sat on the mat the cat"
# count word frequency using .get()
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Split the text with `.split()`. For each word: `freq[word] = freq.get(word, 0) + 1`.

</details>

<details>
<summary>✅ Answer</summary>

```python
text = "the cat sat on the mat the cat"
freq = {}
for word in text.split():
    freq[word] = freq.get(word, 0) + 1
print(freq)
# {'the': 3, 'cat': 2, 'sat': 1, 'on': 1, 'mat': 1}
```

**Why:** `.get(word, 0)` returns `0` for the first occurrence of any new word. Adding `1` gives the first count. Every repeat increments it. This is the most common dict pattern in interviews.

</details>

---

### Q10 · dict — Phone Book

**Problem:**
Store 5 contacts in a dict `{name: number}`. Look up `"Alice"`. Then look up `"Eve"`, who does not exist, and handle it gracefully — print `"Contact not found"` instead of crashing.

```python
contacts = {
    "Alice": "9876543210",
    "Bob":   "9123456789",
    "Charlie": "9012345678",
    "Diana": "9988776655",
    "Eve is not here": "—"
}
# look up Alice
# look up Eve safely
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `.get()` with a fallback string, or use `if "name" in contacts` before accessing.

</details>

<details>
<summary>✅ Answer</summary>

```python
contacts = {
    "Alice":   "9876543210",
    "Bob":     "9123456789",
    "Charlie": "9012345678",
    "Diana":   "9988776655",
    "Frank":   "9001122334"
}

# Look up Alice:
print(contacts["Alice"])   # 9876543210

# Look up Eve safely:
number = contacts.get("Eve", "Contact not found")
print(number)   # Contact not found
```

**Why:** A phone book lookup is one of the clearest real-world cases for `.get()` — you cannot know in advance whether a contact exists, so you must handle the missing case.

</details>

---

### Q11 · dict — Group By

**Problem:**
`students = [("Alice","A"),("Bob","B"),("Charlie","A"),("Diana","B"),("Eve","A")]`

Build a dict that groups names by grade: `{"A": ["Alice", "Charlie", "Eve"], "B": ["Bob", "Diana"]}`.

```python
students = [("Alice","A"),("Bob","B"),("Charlie","A"),("Diana","B"),("Eve","A")]
# group names by grade
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

For each `(name, grade)` pair, use `.get(grade, [])` to fetch the existing list (or start with an empty one), append the name, then store it back.

</details>

<details>
<summary>✅ Answer</summary>

```python
students = [("Alice","A"),("Bob","B"),("Charlie","A"),("Diana","B"),("Eve","A")]
groups = {}
for name, grade in students:
    groups[grade] = groups.get(grade, []) + [name]
print(groups)
# {'A': ['Alice', 'Charlie', 'Eve'], 'B': ['Bob', 'Diana']}
```

**Why:** Grouping is one of the most common real-world dict operations. The `.get(key, [])` pattern safely initialises a new group the first time a grade is seen.

</details>

---

### Q12 · dict — Invert a Dict

**Problem:**
`original = {"a": 1, "b": 2, "c": 3}`. Create a new dict with keys and values swapped: `{1: "a", 2: "b", 3: "c"}`. Use a dict comprehension.

```python
original = {"a": 1, "b": 2, "c": 3}
# invert it in one line
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Swap `k` and `v` in the comprehension: `{v: k for k, v in original.items()}`.

</details>

<details>
<summary>✅ Answer</summary>

```python
original = {"a": 1, "b": 2, "c": 3}
inverted = {v: k for k, v in original.items()}
print(inverted)
# {1: 'a', 2: 'b', 3: 'c'}
```

**Why:** Dict comprehension makes inversion a one-liner. Note: this only works correctly when all values in the original dict are unique — duplicate values would cause collisions.

</details>

---

### Q13 · dict — Most Frequent Element

**Problem:**
`nums = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]`. Find and print the most frequent element using a dict counter. Do not use `Counter`.

```python
nums = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
# count frequencies, then find the max
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Build the frequency dict first. Then use `max(freq, key=freq.get)` to find the key with the highest count.

</details>

<details>
<summary>✅ Answer</summary>

```python
nums = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]

freq = {}
for n in nums:
    freq[n] = freq.get(n, 0) + 1

most_common = max(freq, key=freq.get)
print(most_common)   # 5
print(freq)
# {3: 2, 1: 2, 4: 1, 5: 3, 9: 1, 2: 1, 6: 1}
```

**Why:** `max(freq, key=freq.get)` iterates over the keys and uses each key's count as the comparison value. This is a classic interview pattern — know it cold.

</details>

---

### Q14 · dict — Merge Two Dicts

**Problem:**
`d1 = {"a": 1, "b": 2}`, `d2 = {"b": 3, "c": 4}`. Merge them using three different approaches. What happens to the duplicate key `"b"` in each case?

```python
d1 = {"a": 1, "b": 2}
d2 = {"b": 3, "c": 4}
# method 1: .update()
# method 2: | operator (Python 3.9+)
# method 3: {**d1, **d2}
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

In all three methods, the second dict wins for duplicate keys — `d2` overwrites `d1` for key `"b"`.

</details>

<details>
<summary>✅ Answer</summary>

```python
d1 = {"a": 1, "b": 2}
d2 = {"b": 3, "c": 4}

# Method 1: .update() — modifies d1 in place
merged1 = d1.copy()
merged1.update(d2)
print(merged1)   # {'a': 1, 'b': 3, 'c': 4}

# Method 2: | operator (Python 3.9+) — creates a new dict
merged2 = d1 | d2
print(merged2)   # {'a': 1, 'b': 3, 'c': 4}

# Method 3: {**d1, **d2} — unpacking, works on Python 3.5+
merged3 = {**d1, **d2}
print(merged3)   # {'a': 1, 'b': 3, 'c': 4}
```

**Why:** All three produce the same result — the right-hand dict wins on duplicate keys. The `|` operator is the clearest modern syntax. Use `{**d1, **d2}` for compatibility below Python 3.9.

</details>

---

### Q15 · dict — List of Dicts to Single Dict

**Problem:**
`data = [{"name": "Alice", "score": 92}, {"name": "Bob", "score": 78}, {"name": "Charlie", "score": 85}]`

Convert to a single dict: `{"Alice": 92, "Bob": 78, "Charlie": 85}`.

```python
data = [
    {"name": "Alice",   "score": 92},
    {"name": "Bob",     "score": 78},
    {"name": "Charlie", "score": 85}
]
# convert to {name: score}
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use a dict comprehension. Each item `d` in the list has `d["name"]` and `d["score"]`.

</details>

<details>
<summary>✅ Answer</summary>

```python
data = [
    {"name": "Alice",   "score": 92},
    {"name": "Bob",     "score": 78},
    {"name": "Charlie", "score": 85}
]
result = {d["name"]: d["score"] for d in data}
print(result)
# {'Alice': 92, 'Bob': 78, 'Charlie': 85}
```

**Why:** Converting a list of records to a lookup dict is extremely common when processing API responses or database results. Dict comprehension makes it a single readable line.

</details>

---

**[🏠 Back to Data Types](../theory.md)**

**Related:** [Theory](./theory.md) · [Exercises](../dict_practice.py) · [Interview Q&A](../interview.md)
