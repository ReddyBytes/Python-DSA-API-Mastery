# 📋 list — Practice Problems

> 15 problems · Lists from basics to interview patterns
> Write your answer in `practice_local.py` first, then use the dropdowns.

---

## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| [Q1](#q1)–Q3 | Creating · accessing · modifying | 🟢 |
| [Q4](#q4)–Q6 | Slicing · sort · search | 🟢 |
| [Q7](#q7)–Q10 | Copy trap · comprehension · nested | 🟡 |
| [Q11](#q11)–Q13 | Real-world patterns | 🟡 |
| [Q14](#q14)–Q15 | Interview patterns | 🟠 |

---

<a id="q1"></a>

### Q1 · list — Create and Append

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


**Problem:**
Start with an empty list. Append `"Python"`, `"is"`, and `"fun"` to it. Print the list and its length.

```python
words = []
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `.append()` to add one item at a time. Use `len()` to get the count.

</details>

<details>
<summary>✅ Answer</summary>

```python
words = []
words.append("Python")
words.append("is")
words.append("fun")
print(words)       # ['Python', 'is', 'fun']
print(len(words))  # 3
```

**Why:** `.append()` always adds to the end. `len()` counts how many items are in the list.

</details>

---

<a id="q2"></a>

### Q2 · list — Indexing

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


**Problem:**
`fruits = ["apple", "banana", "cherry"]`. Print the first item using a positive index and the last item using a negative index.

```python
fruits = ["apple", "banana", "cherry"]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Index 0 is the first item. Index -1 is always the last item, no matter the list length.

</details>

<details>
<summary>✅ Answer</summary>

```python
fruits = ["apple", "banana", "cherry"]
print(fruits[0])    # apple
print(fruits[-1])   # cherry
```

**Why:** Positive indices count from the front (starting at 0). Negative indices count from the back (-1 is last, -2 is second-to-last, etc.).

</details>

---

<a id="q3"></a>

### Q3 · list — Modify

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


**Problem:**
`fruits = ["apple", "banana", "cherry"]`. Change `"banana"` to `"mango"` using index assignment. Print the updated list.

```python
fruits = ["apple", "banana", "cherry"]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`"banana"` is at index 1. Assign directly: `fruits[1] = "mango"`.

</details>

<details>
<summary>✅ Answer</summary>

```python
fruits = ["apple", "banana", "cherry"]
fruits[1] = "mango"
print(fruits)   # ['apple', 'mango', 'cherry']
```

**Why:** Lists are mutable — you can change any item by assigning to its index. This is the key difference from tuples and strings.

</details>

---

<a id="q4"></a>

### Q4 · list — Slicing

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


**Problem:**
`scores = [88, 92, 75, 96, 83, 70, 91]`. Using slicing, print: the first 3 scores, the last 2 scores, and the list reversed.

```python
scores = [88, 92, 75, 96, 83, 70, 91]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`list[:3]` gives the first 3. `list[-2:]` gives the last 2. `list[::-1]` reverses.

</details>

<details>
<summary>✅ Answer</summary>

```python
scores = [88, 92, 75, 96, 83, 70, 91]
print(scores[:3])    # [88, 92, 75]
print(scores[-2:])   # [70, 91]
print(scores[::-1])  # [91, 70, 83, 96, 75, 92, 88]
```

**Why:** Slice syntax is `[start:stop:step]`. Omitting start/stop means "from the beginning" or "to the end". A step of -1 walks the list backwards.

</details>

---

<a id="q5"></a>

### Q5 · list — Sort

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


**Problem:**
`scores = [88, 92, 75, 96, 83, 70, 91]`. Sort the scores ascending and descending. Show both `.sort()` (in-place) and `sorted()` (returns new list). What is the key difference?

```python
scores = [88, 92, 75, 96, 83, 70, 91]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`.sort()` modifies the original list. `sorted()` returns a new list and leaves the original unchanged.

</details>

<details>
<summary>✅ Answer</summary>

```python
scores = [88, 92, 75, 96, 83, 70, 91]

# In-place sort — original list is changed
scores.sort()
print(scores)               # [70, 75, 83, 88, 91, 92, 96]

scores.sort(reverse=True)
print(scores)               # [96, 92, 91, 88, 83, 75, 70]

# sorted() — original is NOT changed
original = [88, 92, 75, 96, 83, 70, 91]
asc  = sorted(original)
desc = sorted(original, reverse=True)
print(original)   # [88, 92, 75, 96, 83, 70, 91]  ← unchanged
print(asc)        # [70, 75, 83, 88, 91, 92, 96]
print(desc)       # [96, 92, 91, 88, 83, 75, 70]
```

**Why:** Use `.sort()` when you want to sort in-place and don't need the original order. Use `sorted()` when you want to keep the original or need to sort a temporary copy.

</details>

---

<a id="q6"></a>

### Q6 · list — Search

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


**Problem:**
`fruits = ["apple", "banana", "apple", "cherry", "apple"]`. Count how many times `"apple"` appears. Find the index of `"cherry"`.

```python
fruits = ["apple", "banana", "apple", "cherry", "apple"]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`.count()` counts occurrences. `.index()` returns the position of the first match.

</details>

<details>
<summary>✅ Answer</summary>

```python
fruits = ["apple", "banana", "apple", "cherry", "apple"]
print(fruits.count("apple"))    # 3
print(fruits.index("cherry"))   # 3
```

**Why:** `.count()` scans the whole list and counts matches. `.index()` stops at the first match and returns its position. If the item is not found, `.index()` raises a `ValueError`.

</details>

---

<a id="q7"></a>

### Q7 · list — Remove Items

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


**Problem:**
Show the three ways to remove items from a list: `.remove()`, `.pop()`, and `del`. Use `items = ["a", "b", "c", "d", "e"]`. What is the key difference between each?

```python
items = ["a", "b", "c", "d", "e"]
# demonstrate .remove(), .pop(), and del
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`.remove()` deletes by value. `.pop()` deletes by index and returns the item. `del` deletes by index with no return value.

</details>

<details>
<summary>✅ Answer</summary>

```python
items = ["a", "b", "c", "d", "e"]

items.remove("c")         # remove by VALUE — removes first match
print(items)              # ['a', 'b', 'd', 'e']

popped = items.pop(1)     # remove by INDEX — returns the removed item
print(popped)             # b
print(items)              # ['a', 'd', 'e']

del items[0]              # remove by INDEX — no return value
print(items)              # ['d', 'e']
```

**Why:** Use `.remove()` when you know the value. Use `.pop()` when you need the removed value back (e.g. implementing a stack). Use `del` for a clean index-based delete when you don't need the item.

</details>

---

<a id="q8"></a>

### Q8 · list — Copy Trap

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


**Problem:**
`a = [1, 2, 3]`. Do `b = a`, then `b.append(4)`. Print both `a` and `b`. What happens? Fix it so `a` does not change.

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)   # what do you see?
print(b)
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`b = a` does not copy the list. Both `a` and `b` point to the same list in memory. Use `.copy()` or `[:]` to make an independent copy.

</details>

<details>
<summary>✅ Answer</summary>

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)   # [1, 2, 3, 4]  ← a changed too! Both names point to the same list.
print(b)   # [1, 2, 3, 4]

# Fix:
a = [1, 2, 3]
b = a.copy()   # creates a new, independent list
b.append(4)
print(a)   # [1, 2, 3]  ← safe now
print(b)   # [1, 2, 3, 4]
```

**Why:** Lists are mutable objects. `b = a` just gives the same object a second name — it does not create a new list. `.copy()` (or `a[:]` or `list(a)`) creates a genuinely separate list.

</details>

---

<a id="q9"></a>

### Q9 · list — List Comprehension

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


**Problem:**
`numbers = range(1, 11)`. Using a single list comprehension, create a list of the squares of all even numbers.

```python
numbers = range(1, 11)
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

The pattern is `[expression for item in iterable if condition]`. Filter with `if x % 2 == 0`, transform with `x ** 2`.

</details>

<details>
<summary>✅ Answer</summary>

```python
numbers = range(1, 11)
squares_of_evens = [x ** 2 for x in numbers if x % 2 == 0]
print(squares_of_evens)   # [4, 16, 36, 64, 100]
```

**Why:** A list comprehension combines filtering and transformation in one readable line. `if x % 2 == 0` keeps only even numbers, and `x ** 2` squares each one.

</details>

---

<a id="q10"></a>

### Q10 · list — Nested List

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


**Problem:**
`matrix = [[1,2,3],[4,5,6],[7,8,9]]`. Print the center value (`5`). Print the entire second row.

```python
matrix = [[1,2,3],[4,5,6],[7,8,9]]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`matrix[row][col]` — first index picks the row, second index picks the column within that row.

</details>

<details>
<summary>✅ Answer</summary>

```python
matrix = [[1,2,3],[4,5,6],[7,8,9]]
print(matrix[1][1])   # 5  — row 1 (middle), column 1 (middle)
print(matrix[1])      # [4, 5, 6]  — entire second row
```

**Why:** `matrix[1]` returns the second list `[4, 5, 6]`. Chaining `[1]` on that picks index 1 within it, giving `5`.

</details>

---

<a id="q11"></a>

### Q11 · list — Shopping Cart

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


**Problem:**
Build a shopping cart: start empty, add 5 items of your choice, remove 1, check if a specific item is in the cart, and print the total count.

```python
cart = []
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `.append()` to add, `.remove()` to delete, `in` to check, and `len()` for the count.

</details>

<details>
<summary>✅ Answer</summary>

```python
cart = []
cart.append("Apples")
cart.append("Bread")
cart.append("Milk")
cart.append("Eggs")
cart.append("Butter")

cart.remove("Milk")

print("Eggs" in cart)    # True
print("Milk" in cart)    # False
print(len(cart))         # 4
print(cart)              # ['Apples', 'Bread', 'Eggs', 'Butter']
```

**Why:** Lists are the natural choice for ordered, changeable collections like carts, queues, and to-do lists. `in` checks membership in O(n) time — fine for small lists.

</details>

---

<a id="q12"></a>

### Q12 · list — Top and Bottom

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


**Problem:**
`scores = [78, 92, 85, 96, 70, 88, 91, 76, 99, 83]`. Get the top 3 scores and the bottom 3 scores. Do not modify the original list.

```python
scores = [78, 92, 85, 96, 70, 88, 91, 76, 99, 83]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `sorted()` (not `.sort()`) so the original stays unchanged. Slice from the front for the bottom 3 and from the end for the top 3.

</details>

<details>
<summary>✅ Answer</summary>

```python
scores = [78, 92, 85, 96, 70, 88, 91, 76, 99, 83]
ranked = sorted(scores)
print(ranked[:3])    # [70, 76, 78]   — bottom 3
print(ranked[-3:])   # [92, 96, 99]   — top 3
print(scores)        # unchanged
```

**Why:** `sorted()` returns a new list without touching the original. Slicing the sorted result from either end gives the extremes cleanly.

</details>

---

<a id="q13"></a>

### Q13 · list — Deduplicate (Order Preserved)

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


**Problem:**
Deduplicate `[1, 2, 2, 3, 3, 3, 4]` while preserving the original order. You cannot use `set()` directly (it does not guarantee order).

```python
items = [1, 2, 2, 3, 3, 3, 4]
# your code here — keep order, remove duplicates
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Build a new list. Before appending each item, check if it is already in the new list using `not in`.

</details>

<details>
<summary>✅ Answer</summary>

```python
items = [1, 2, 2, 3, 3, 3, 4]
seen = []
for item in items:
    if item not in seen:
        seen.append(item)
print(seen)   # [1, 2, 3, 4]
```

**Why:** Checking `not in` against a growing list preserves the first-seen order. For large lists, a `seen` set is faster (O(1) lookup) but if you also need order, keep both a set for fast checks and a list for ordered results.

</details>

---

<a id="q14"></a>

### Q14 · list — Flatten (Interview)

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


**Problem:**
Flatten `[[1, 2], [3, 4], [5, 6]]` into `[1, 2, 3, 4, 5, 6]` using a single list comprehension.

```python
nested = [[1, 2], [3, 4], [5, 6]]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use a nested comprehension: `[item for sublist in nested for item in sublist]`.

</details>

<details>
<summary>✅ Answer</summary>

```python
nested = [[1, 2], [3, 4], [5, 6]]
flat = [item for sublist in nested for item in sublist]
print(flat)   # [1, 2, 3, 4, 5, 6]
```

**Why:** The nested comprehension reads as "for each sublist, for each item in that sublist, yield item." The outer loop comes first in the comprehension, matching how you would write a nested for loop.

</details>

---

<a id="q15"></a>

### Q15 · list — Common Elements (Interview)

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


**Problem:**
`a = [1, 2, 3, 4, 5]`, `b = [3, 4, 5, 6, 7]`. Find the elements that appear in both lists — without using `set`.

```python
a = [1, 2, 3, 4, 5]
b = [3, 4, 5, 6, 7]
# your code here — no set allowed
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use a list comprehension: keep items from `a` that also appear `in b`.

</details>

<details>
<summary>✅ Answer</summary>

```python
a = [1, 2, 3, 4, 5]
b = [3, 4, 5, 6, 7]
common = [x for x in a if x in b]
print(common)   # [3, 4, 5]
```

**Why:** `[x for x in a if x in b]` checks each element of `a` against `b`. This is O(n*m) — fine for small lists. In an interview, mention the set-based approach `list(set(a) & set(b))` is O(n+m) and faster for large inputs.

</details>

---

**[🏠 Back to Data Types](../theory.md)**

**Related:** [Theory](./theory.md) · [Exercises](./list_practice.py) · [Interview Q&A](../interview.md)
