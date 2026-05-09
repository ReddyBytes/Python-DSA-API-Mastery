# 📦 tuple — Practice Problems

> 12 problems · Tuples from basics to practical patterns
> Write your answer in `practice_local.py` first, then use the dropdowns.

---

## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| [Q1](#q1)–Q3 | Creating · trailing comma · immutability | 🟢 |
| [Q4](#q4)–Q6 | Unpacking · swap · packing | 🟡 |
| [Q7](#q7)–Q9 | Tuple as dict key · in sets · memory | 🟡 |
| [Q10](#q10)–Q12 | Real-world patterns | 🟡 |

---

<a id="q1"></a>

### Q1 · tuple — Creating and the Trailing Comma

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


**Problem:**
Create a tuple with 3 items: `"red"`, `"green"`, `"blue"`. Then try to create a single-item tuple containing just `42` — show the common mistake (without the comma) and the correct fix.

```python
# create a 3-item tuple
# then show the wrong way and right way to make a single-item tuple
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Parentheses alone do not make a tuple — the comma does. `(42)` is just the integer `42`. You need `(42,)` to make a single-item tuple.

</details>

<details>
<summary>✅ Answer</summary>

```python
colors = ("red", "green", "blue")
print(colors)          # ('red', 'green', 'blue')
print(type(colors))    # <class 'tuple'>

# Wrong — this is just an int!
not_a_tuple = (42)
print(type(not_a_tuple))   # <class 'int'>

# Right — trailing comma makes it a tuple
single = (42,)
print(type(single))   # <class 'tuple'>
```

**Why:** The comma is what creates a tuple, not the parentheses. Python uses parentheses for grouping expressions too, so `(42)` is simply `42`. The comma tells Python "this is a sequence with one item".

</details>

---

<a id="q2"></a>

### Q2 · tuple — Immutability

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


**Problem:**
`coords = (10, 20, 30)`. Try to change the first element to `99`. What error do you get? Then show the correct way to "update" a tuple when you genuinely need different values.

```python
coords = (10, 20, 30)
# try: coords[0] = 99  — what happens?
# then show the fix
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Tuples cannot be modified in place. To "update" one, build a new tuple using the parts you want to keep.

</details>

<details>
<summary>✅ Answer</summary>

```python
coords = (10, 20, 30)
# coords[0] = 99  → TypeError: 'tuple' object does not support item assignment

# Fix: build a new tuple with the updated value
coords = (99,) + coords[1:]
print(coords)   # (99, 20, 30)
```

**Why:** Immutability is the whole point of a tuple — it protects data from accidental changes. When you need different values, you create a new tuple rather than mutating the old one. `coords[1:]` gives you `(20, 30)` and concatenation joins the pieces.

</details>

---

<a id="q3"></a>

### Q3 · tuple — Tuple vs List

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


**Problem:**
Create `colors_list = ["red", "green", "blue"]` and `colors_tuple = ("red", "green", "blue")`. Demonstrate that you can change an item in the list but not in the tuple.

```python
colors_list = ["red", "green", "blue"]
colors_tuple = ("red", "green", "blue")
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Try assigning to index `[0]` on both. One will work, one will raise a `TypeError`.

</details>

<details>
<summary>✅ Answer</summary>

```python
colors_list = ["red", "green", "blue"]
colors_tuple = ("red", "green", "blue")

# List is mutable — this works
colors_list[0] = "purple"
print(colors_list)    # ['purple', 'green', 'blue']

# Tuple is immutable — this crashes
# colors_tuple[0] = "purple"
# → TypeError: 'tuple' object does not support item assignment
print(colors_tuple)   # ('red', 'green', 'blue')  — unchanged
```

**Why:** Use a list when the data will change over time (a shopping cart, a queue of tasks). Use a tuple when the data is fixed and should never be modified (RGB values, GPS coordinates, configuration constants).

</details>

---

<a id="q4"></a>

### Q4 · tuple — Unpacking

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


**Problem:**
`point = (10, 20, 30)`. Unpack it into three variables `x`, `y`, `z` and print each one on its own line.

```python
point = (10, 20, 30)
# unpack into x, y, z
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

The pattern is `x, y, z = point`. The number of variables on the left must match the number of items in the tuple.

</details>

<details>
<summary>✅ Answer</summary>

```python
point = (10, 20, 30)
x, y, z = point
print(x)   # 10
print(y)   # 20
print(z)   # 30
```

**Why:** Tuple unpacking assigns each position in the tuple to the matching variable on the left, in order. It is cleaner and more readable than `x = point[0]`, `y = point[1]`, etc.

</details>

---

<a id="q5"></a>

### Q5 · tuple — Swap Variables

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


**Problem:**
`a = 100`, `b = 200`. Swap their values using tuple unpacking in a single line. Print both variables after the swap.

```python
a = 100
b = 200
# swap in one line
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`a, b = b, a` — Python evaluates the right side first, packs the values into a temporary tuple, then unpacks into `a` and `b`.

</details>

<details>
<summary>✅ Answer</summary>

```python
a = 100
b = 200
a, b = b, a
print(a)   # 200
print(b)   # 100
```

**Why:** Python evaluates `b, a` on the right first — creating the tuple `(200, 100)` — then unpacks it into `a` and `b`. No temporary variable needed. This is one of Python's most elegant features and it works entirely through tuple mechanics.

</details>

---

<a id="q6"></a>

### Q6 · tuple — Extended Unpacking

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


**Problem:**
`data = (1, 2, 3, 4, 5)`. Unpack it so that `first` gets the first item, `last` gets the last item, and `middle` gets everything in between — all in one line using `*`.

```python
data = (1, 2, 3, 4, 5)
# unpack into first, middle, last
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

The `*` operator in unpacking collects "the rest" into a list. It can appear anywhere: `first, *middle, last = data`.

</details>

<details>
<summary>✅ Answer</summary>

```python
data = (1, 2, 3, 4, 5)
first, *middle, last = data
print(first)    # 1
print(middle)   # [2, 3, 4]
print(last)     # 5
```

**Why:** The `*` prefix tells Python to be greedy and collect all remaining items into a list. It adapts to any length — if `data` had 10 items, `middle` would have 8. This is called extended iterable unpacking and works on any sequence.

</details>

---

<a id="q7"></a>

### Q7 · tuple — Tuple as Dict Key

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


**Problem:**
`locations = {(0, 0): "origin", (1, 0): "right", (0, 1): "up"}`. Look up and print the label for the coordinate `(1, 0)`.

```python
locations = {(0, 0): "origin", (1, 0): "right", (0, 1): "up"}
# look up (1, 0)
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Access the dict the same way you always do: `locations[(1, 0)]`.

</details>

<details>
<summary>✅ Answer</summary>

```python
locations = {(0, 0): "origin", (1, 0): "right", (0, 1): "up"}
print(locations[(1, 0)])   # right
```

**Why:** Dict keys must be hashable — meaning their value can never change. Tuples are immutable and therefore hashable, so they work as keys. Lists are mutable and unhashable, so `{[1, 0]: "right"}` would raise a `TypeError`. This makes tuples the right choice for composite keys like coordinates, date ranges, or (row, column) pairs.

</details>

---

<a id="q8"></a>

### Q8 · tuple — Tuple in a Set

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


**Problem:**
Try to add `[1, 2]` (a list) to a set. Then try adding `(1, 2)` (a tuple). Which works? Why? Show both attempts and the error from the failing one.

```python
s = set()
# try s.add([1, 2])
# try s.add((1, 2))
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Sets use hash values internally. Only hashable objects can be stored in a set. Immutable = hashable, mutable = not hashable.

</details>

<details>
<summary>✅ Answer</summary>

```python
s = set()

# s.add([1, 2])   → TypeError: unhashable type: 'list'

s.add((1, 2))   # works — tuples are hashable
print(s)        # {(1, 2)}
```

**Why:** A set stores items by their hash value for fast lookup — the same mechanism as dict keys. Lists can be modified after creation, so their hash would change, breaking the set's internal structure. Python prevents this by making lists unhashable. Tuples are immutable so their hash never changes, making them safe to store in sets and use as dict keys.

</details>

---

<a id="q9"></a>

### Q9 · tuple — Named Data

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


**Problem:**
Store a person's information as a tuple: name `"Alice"`, age `30`, city `"London"`. Unpack the tuple and print a formatted sentence: `"Alice is 30 years old and lives in London"`.

```python
person = ("Alice", 30, "London")
# unpack and print the sentence
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Unpack with `name, age, city = person`, then use an f-string to build the sentence.

</details>

<details>
<summary>✅ Answer</summary>

```python
person = ("Alice", 30, "London")
name, age, city = person
print(f"{name} is {age} years old and lives in {city}")
# Alice is 30 years old and lives in London
```

**Why:** Tuple unpacking paired with f-strings is a clean, readable pattern for working with structured records. The tuple holds the data in a fixed shape; unpacking gives each field a meaningful name for use in the output.

</details>

---

<a id="q10"></a>

### Q10 · tuple — GPS Coordinates Loop

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


**Problem:**
You have GPS coordinates for 3 cities stored as a list of tuples. Loop through the list and print each city's name with its coordinates.

```python
cities = [
    ("New York", 40.71, -74.01),
    ("London",   51.51,  -0.13),
    ("Tokyo",    35.68, 139.69),
]
# loop and print each city
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Unpack directly in the `for` loop: `for name, lat, lon in cities`.

</details>

<details>
<summary>✅ Answer</summary>

```python
cities = [
    ("New York", 40.71, -74.01),
    ("London",   51.51,  -0.13),
    ("Tokyo",    35.68, 139.69),
]

for name, lat, lon in cities:
    print(f"{name}: lat={lat}, lon={lon}")

# New York: lat=40.71, lon=-74.01
# London: lat=51.51, lon=-0.13
# Tokyo: lat=35.68, lon=139.69
```

**Why:** Unpacking directly inside the `for` statement is one of Python's most practical patterns. Each iteration unpacks the 3-item tuple into three named variables, making the loop body clean and self-documenting. Lists of tuples are a very common data shape — returned by database queries, CSV readers, and API responses.

</details>

---

<a id="q11"></a>

### Q11 · tuple — enumerate with a Tuple

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


**Problem:**
`months = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec")`. Use `enumerate()` to print each month with its number: `"1: Jan"`, `"2: Feb"`, etc. Start counting from 1.

```python
months = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec")
# use enumerate to print month number and name
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`enumerate(months, start=1)` gives you `(1, "Jan")`, `(2, "Feb")`, etc. Unpack in the `for` loop.

</details>

<details>
<summary>✅ Answer</summary>

```python
months = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec")

for num, name in enumerate(months, start=1):
    print(f"{num}: {name}")

# 1: Jan
# 2: Feb
# ...
# 12: Dec
```

**Why:** `enumerate()` returns `(index, value)` pairs — a list of tuples under the hood. The `start=1` argument shifts the counter so it matches real-world month numbering. This pattern works on any iterable: lists, tuples, strings.

</details>

---

<a id="q12"></a>

### Q12 · tuple — Unpack into a Dict

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


**Problem:**
`pairs = [("Alice", 92), ("Bob", 78), ("Charlie", 85)]`. Convert this list of `(name, score)` tuples into a dictionary using a loop and tuple unpacking.

```python
pairs = [("Alice", 92), ("Bob", 78), ("Charlie", 85)]
# convert to dict using a loop
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Create an empty dict, then loop with `for name, score in pairs` and assign `result[name] = score`.

</details>

<details>
<summary>✅ Answer</summary>

```python
pairs = [("Alice", 92), ("Bob", 78), ("Charlie", 85)]
result = {}
for name, score in pairs:
    result[name] = score
print(result)
# {'Alice': 92, 'Bob': 78, 'Charlie': 85}
```

**Why:** This is a fundamental pattern in Python — turning a list of `(key, value)` tuples into a dict. You will see it constantly: database rows, CSV files, and API payloads often arrive as lists of tuples before being mapped to dicts. The built-in shortcut is `dict(pairs)`, but writing the loop explicitly shows exactly what is happening.

</details>

---

**[🏠 Back to Data Types](../theory.md)**

**Related:** [Theory](./theory.md) · [Exercises](./tuple_practice.py) · [Interview Q&A](../interview.md)
