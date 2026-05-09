# ⚡ Functional Programming — Practice Problems

> 15 problems · First-class functions, pure/impure, map/filter/reduce, composition  
> Write your answer in `practice_local.py` first, then use the dropdowns.

---

## 📋 Quick Index

| # | Concept | Title | Level |
|---|---------|-------|-------|
| [Q1](#q1) | First-class | Assign to variable, store in list, call from list | 🟢 |
| [Q2](#q2) | First-class | `func` vs `func()` bug: predict and fix | 🟢 |
| [Q3](#q3) | First-class | Store 4 math functions in a dict, call by name | 🟢 |
| [Q4](#q4) | Higher-order | Write `apply_twice(func, value)` | 🟡 |
| [Q5](#q5) | Higher-order | Write `apply_n(func, value, n)` | 🟡 |
| [Q6](#q6) | Pure/impure | Classify 5 functions and explain why | 🟡 |
| [Q7](#q7) | Pure/impure | Rewrite an impure (mutating) function as pure | 🟡 |
| [Q8](#q8) | map() | Apply tax calculation to a list of prices | 🟢 |
| [Q9](#q9) | map() | Use map with two lists | 🟡 |
| [Q10](#q10) | filter() | Filter a list of users by `active=True` | 🟢 |
| [Q11](#q11) | filter() | Filter out `None` and empty strings | 🟡 |
| [Q12](#q12) | reduce() | Sum a list, then find max using reduce | 🟡 |
| [Q13](#q13) | Composition | Build a text normalization pipeline | 🟠 |
| [Q14](#q14) | Composition | Write `pipe(*funcs)` left-to-right applicator | 🟠 |
| [Q15](#q15) | Real-world | Data transform pipeline: filter → map → reduce | 🟠 |

---

<a id="q1"></a>

### Q1 · First-class — Assign, Store, Call

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


**Problem:**
1. Define a function `shout(text)` that returns `text.upper() + "!"`.
2. Assign `shout` to a variable called `loud`.
3. Store `shout` in a list called `actions`.
4. Call `shout` from the list using its index and print the result for `"hello"`.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

To store a function in a variable or list, write the name **without** parentheses. Parentheses mean "call it now".

</details>

<details>
<summary>✅ Answer</summary>

```python
def shout(text):
    return text.upper() + "!"

loud = shout              # assign — no ()
actions = [shout]         # store in list — no ()

print(loud("hello"))      # HELLO!
print(actions[0]("hello"))  # HELLO! — call via index
```

**Why:** `shout` is the function object. `shout("hello")` is its return value. By storing the object, not the result, you can call it later from anywhere — a variable, a list, a dict, or an argument.

</details>

---

<a id="q2"></a>

### Q2 · First-class — `func` vs `func()` Bug

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


**Problem:**
The code below has a bug. Predict what error you will get and fix it.

```python
numbers = [3, 1, 4, 1, 5]
result = sorted(numbers, key=len())
print(result)
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`len()` with no arguments tries to call `len` immediately. What does `len()` return? Can `sorted` use that as a key?

</details>

<details>
<summary>✅ Answer</summary>

```python
numbers = [3, 1, 4, 1, 5]

# Buggy: len() calls len with no args → TypeError: len expected at least 1 argument
# result = sorted(numbers, key=len())

# Fixed: pass the function object, not its result
result = sorted(numbers, key=lambda x: x)   # or just: sorted(numbers)
print(result)   # [1, 1, 3, 4, 5]
```

**Why:** `key=` expects a function to call on each element. `len()` calls `len` immediately (with no argument) and crashes. `len` — no parentheses — passes the function itself, which `sorted` can then call on each item.

</details>

---

<a id="q3"></a>

### Q3 · First-class — Function Dispatch Dict

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


**Problem:**
Store these four functions in a dict: `add`, `subtract`, `multiply`, `divide`. The keys should be `"+"`, `"-"`, `"*"`, `"/"`. Then write a `calculate(op, a, b)` function that looks up the operation and calls it.

```python
def add(a, b):      return a + b
def subtract(a, b): return a - b
def multiply(a, b): return a * b
def divide(a, b):   return a / b

# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Build a `ops = {...}` dict with function objects as values. In `calculate`, do `ops[op](a, b)`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def add(a, b):      return a + b
def subtract(a, b): return a - b
def multiply(a, b): return a * b
def divide(a, b):   return a / b

ops = {
    "+": add,
    "-": subtract,
    "*": multiply,
    "/": divide,
}

def calculate(op, a, b):
    return ops[op](a, b)   # look up function, then call it

print(calculate("+", 10, 3))   # 13
print(calculate("*", 4, 5))    # 20
print(calculate("/", 10, 2))   # 5.0
```

**Why:** This is the **dispatch table** pattern — a dict of functions replaces a long if/elif chain. It is extensible (add new ops by adding dict entries) and clean.

</details>

---

<a id="q4"></a>

### Q4 · Higher-order — apply_twice

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


**Problem:**
Write a higher-order function `apply_twice(func, value)` that applies `func` to `value` twice. Test it with a `double` function.

```python
def double(x):
    return x * 2

# your code here — write apply_twice and test it
# apply_twice(double, 3) should return 12
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Call `func(value)` to get an intermediate result, then call `func(intermediate)` to get the final result.

</details>

<details>
<summary>✅ Answer</summary>

```python
def double(x):
    return x * 2

def apply_twice(func, value):
    return func(func(value))   # func applied once, then again on the result

print(apply_twice(double, 3))    # double(double(3)) → double(6) → 12
print(apply_twice(double, 5))    # double(double(5)) → double(10) → 20
```

**Why:** `apply_twice` does not know or care what `func` does — it just applies it twice. This is the power of HOFs: the logic (apply twice) is separated from the operation (doubling).

</details>

---

<a id="q5"></a>

### Q5 · Higher-order — apply_n

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


**Problem:**
Generalise Q4. Write `apply_n(func, value, n)` that applies `func` to `value` exactly `n` times.

```python
def increment(x):
    return x + 1

# apply_n(increment, 0, 5) should return 5
# apply_n(double, 1, 4) should return 16
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use a loop that runs `n` times. On each pass, replace `value` with `func(value)`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def increment(x): return x + 1
def double(x):    return x * 2

def apply_n(func, value, n):
    result = value
    for _ in range(n):        # ← run n times
        result = func(result) # ← each pass feeds output into next input
    return result

print(apply_n(increment, 0, 5))   # 5
print(apply_n(double, 1, 4))      # 16  (1→2→4→8→16)
print(apply_n(double, 3, 0))      # 3   (zero applications → unchanged)
```

**Why:** When `n=0`, the loop never runs and `result` is returned as-is. This is the correct identity behaviour — applying a function zero times should leave the value unchanged.

</details>

---

<a id="q6"></a>

### Q6 · Pure/impure — Classify These Functions

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


**Problem:**
Classify each function below as **pure** or **impure**. For each impure function, state what makes it impure.

```python
import random

counter = 0

def f1(a, b):
    return a + b

def f2(x):
    print(x)
    return x * 2

def f3(lst):
    lst.append(99)
    return lst

def f4():
    return random.randint(1, 10)

def f5(x):
    global counter
    counter += 1
    return x * counter
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Ask for each function: does it always return the same output for the same input? Does it change anything outside itself?

</details>

<details>
<summary>✅ Answer</summary>

```
f1 — PURE
  Same inputs always produce the same output. No external state touched.

f2 — IMPURE
  print() is a side effect (I/O). Even though the return value is deterministic,
  the function changes the outside world (the console).

f3 — IMPURE
  Mutates the caller's list (lst.append modifies in place).
  The caller's data is changed without them expecting it.

f4 — IMPURE
  Non-deterministic — returns a different value each call for the same "input"
  (no input at all). Depends on hidden external state (the RNG).

f5 — IMPURE
  Reads and modifies a global variable (counter).
  Same input x returns different results on each call.
```

**Why these distinctions matter:** `f1` can be memoized, tested in isolation, and safely run in parallel. The others require careful handling — mocking for tests, sequencing for correctness.

</details>

---

<a id="q7"></a>

### Q7 · Pure/impure — Rewrite as Pure

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


**Problem:**
The function below mutates its argument. Rewrite it as a pure function that returns a new list with all negative numbers replaced by 0, leaving the original untouched.

```python
def zero_out_negatives(numbers):
    for i in range(len(numbers)):
        if numbers[i] < 0:
            numbers[i] = 0   # ← mutates in place
    return numbers

data = [-1, 2, -3, 4]
result = zero_out_negatives(data)
print(data)    # [-1, 2, -3, 4] should still be original — but it's not!
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Build a new list instead of modifying the existing one. A list comprehension with a conditional expression works cleanly here.

</details>

<details>
<summary>✅ Answer</summary>

```python
# Pure version — does not touch the original
def zero_out_negatives(numbers):
    return [0 if n < 0 else n for n in numbers]   # ← new list, original untouched

data = [-1, 2, -3, 4]
result = zero_out_negatives(data)

print(data)    # [-1, 2, -3, 4] ← unchanged
print(result)  # [0, 2, 0, 4]
```

**Why:** The list comprehension `[0 if n < 0 else n for n in numbers]` builds a brand new list. The original `numbers` binding is never written to. This makes the function safe to call anywhere without worrying about side effects.

</details>

---

<a id="q8"></a>

### Q8 · map() — Tax Calculation

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


**Problem:**
`prices = [9.99, 24.99, 4.49, 14.00]`. Use `map()` to apply a 15% tax to every price and return a new list rounded to 2 decimal places.

```python
prices = [9.99, 24.99, 4.49, 14.00]
# your code here
# expected: [11.49, 28.74, 5.16, 16.1]
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

The tax transformation is `price * 1.15`. Use a lambda or a named function. Wrap `round(..., 2)` around it.

</details>

<details>
<summary>✅ Answer</summary>

```python
prices = [9.99, 24.99, 4.49, 14.00]

with_tax = list(map(lambda p: round(p * 1.15, 2), prices))
print(with_tax)   # [11.49, 28.74, 5.16, 16.1]

# Equivalent with a named function (cleaner for complex logic)
def apply_tax(price):
    return round(price * 1.15, 2)

with_tax = list(map(apply_tax, prices))
```

**Why:** `map` is lazy — it returns an iterator. Wrapping it in `list()` forces evaluation. The named function version is preferred when the logic grows beyond a simple expression.

</details>

---

<a id="q9"></a>

### Q9 · map() — Two Lists

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


**Problem:**
`quantities = [2, 5, 1, 3]` and `unit_prices = [4.99, 1.50, 9.99, 2.00]`. Use `map()` with two iterables to compute the total cost for each item (quantity × price).

```python
quantities  = [2, 5, 1, 3]
unit_prices = [4.99, 1.50, 9.99, 2.00]
# expected: [9.98, 7.5, 9.99, 6.0]
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`map(func, list1, list2)` passes one element from each list to `func` as separate arguments on each step.

</details>

<details>
<summary>✅ Answer</summary>

```python
quantities  = [2, 5, 1, 3]
unit_prices = [4.99, 1.50, 9.99, 2.00]

totals = list(map(lambda q, p: round(q * p, 2), quantities, unit_prices))
print(totals)   # [9.98, 7.5, 9.99, 6.0]
```

**Why:** When you pass two iterables to `map`, it zips them together internally and passes each pair as separate positional arguments to the function. It stops at the end of the shorter iterable.

</details>

---

<a id="q10"></a>

### Q10 · filter() — Active Users

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


**Problem:**
`users` is a list of dicts. Use `filter()` to return only users where `active` is `True`.

```python
users = [
    {"name": "Alice", "active": True},
    {"name": "Bob",   "active": False},
    {"name": "Carol", "active": True},
    {"name": "Dave",  "active": False},
]
# expected: [{"name": "Alice", ...}, {"name": "Carol", ...}]
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

The filter function should take one user (a dict) and return `user["active"]`.

</details>

<details>
<summary>✅ Answer</summary>

```python
users = [
    {"name": "Alice", "active": True},
    {"name": "Bob",   "active": False},
    {"name": "Carol", "active": True},
    {"name": "Dave",  "active": False},
]

active_users = list(filter(lambda u: u["active"], users))
for u in active_users:
    print(u["name"])   # Alice, Carol
```

**Why:** `filter` keeps items where the function returns a truthy value. `u["active"]` is already a boolean, so it acts as the test directly — no need for `== True`.

</details>

---

<a id="q11"></a>

### Q11 · filter() — Remove None and Empty Strings

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


**Problem:**
`items = [1, None, "hello", "", 0, False, "world", None, ""]`. Use `filter()` to keep only items that are not `None` and not empty strings. `0` and `False` should be kept.

```python
items = [1, None, "hello", "", 0, False, "world", None, ""]
# expected: [1, "hello", 0, False, "world"]
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`filter(None, items)` would drop `0` and `False` too — it filters by truthiness. You need an explicit condition: keep item if it is not `None` AND it is not an empty string.

</details>

<details>
<summary>✅ Answer</summary>

```python
items = [1, None, "hello", "", 0, False, "world", None, ""]

cleaned = list(filter(lambda x: x is not None and x != "", items))
print(cleaned)   # [1, 'hello', 0, False, 'world']
```

**Why:** `filter(None, items)` uses truthiness — it would remove `0` and `False` because they are falsy. An explicit condition lets us keep falsy-but-valid values while targeting only `None` and `""`.

</details>

---

<a id="q12"></a>

### Q12 · reduce() — Sum Then Max

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


**Problem:**
1. Use `reduce` to sum `[3, 1, 4, 1, 5, 9, 2, 6]`.
2. Use `reduce` to find the maximum value in the same list (without using `max()`).

```python
from functools import reduce

numbers = [3, 1, 4, 1, 5, 9, 2, 6]
# part 1: sum → 31
# part 2: max → 9
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

For sum: `acc + n`. For max: the lambda should return whichever of `acc` or `n` is larger — use a ternary.

</details>

<details>
<summary>✅ Answer</summary>

```python
from functools import reduce

numbers = [3, 1, 4, 1, 5, 9, 2, 6]

total = reduce(lambda acc, n: acc + n, numbers)
print(total)   # 31

maximum = reduce(lambda acc, n: acc if acc > n else n, numbers)
print(maximum)  # 9
```

**Why:** Both work by building up a result one element at a time. The accumulator (`acc`) carries the running result. For max, we keep whichever of the current accumulator or the new element is larger.

</details>

---

<a id="q13"></a>

### Q13 · Composition — Text Normalization Pipeline

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


**Problem:**
Build a text normalization pipeline using function composition. Given raw text `"  Python is GREAT!!  "`, produce a clean lowercase word list: `['python', 'is', 'great']`.

Write individual functions: `strip_text`, `to_lower`, `remove_non_alpha`, `split_words`. Then compose them into a single `normalize` function using a `pipe` utility.

```python
import string

# your code here
# normalize("  Python is GREAT!!  ") → ['python', 'is', 'great']
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Write `pipe(*funcs)` first — it returns a function that applies each fn in order. Then define the four steps and pipe them together.

</details>

<details>
<summary>✅ Answer</summary>

```python
import string

def pipe(*funcs):
    def piped(x):
        result = x
        for fn in funcs:
            result = fn(result)
        return result
    return piped

def strip_text(s):       return s.strip()
def to_lower(s):         return s.lower()
def remove_non_alpha(s):
    # keep letters and spaces, drop everything else
    return "".join(c for c in s if c.isalpha() or c.isspace())
def split_words(s):      return s.split()

normalize = pipe(strip_text, to_lower, remove_non_alpha, split_words)

print(normalize("  Python is GREAT!!  "))   # ['python', 'is', 'great']
print(normalize("  Hello, World!  "))       # ['hello', 'world']
```

**Why:** Each function has one job. `pipe` chains them so data flows left to right. Adding a new cleaning step is just appending one more function to the pipe — no conditionals, no loops, no rewriting the orchestration logic.

</details>

---

<a id="q14"></a>

### Q14 · Composition — Write pipe(*funcs)

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


**Problem:**
Write `pipe(*funcs)` that returns a function applying each function left-to-right. Then verify it with a chain of: `add_one` → `double` → `square`.

```python
def add_one(x): return x + 1
def double(x):  return x * 2
def square(x):  return x ** 2

# pipe(add_one, double, square)(3) should return:
# add_one(3) = 4 → double(4) = 8 → square(8) = 64
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`pipe` takes `*funcs` (variadic). The inner function loops over `funcs` in order, passing the output of each as the input to the next.

</details>

<details>
<summary>✅ Answer</summary>

```python
def add_one(x): return x + 1
def double(x):  return x * 2
def square(x):  return x ** 2

def pipe(*funcs):
    def piped(x):
        result = x
        for fn in funcs:         # ← left to right
            result = fn(result)
        return result
    return piped                 # ← return the composed function, not a result

transform = pipe(add_one, double, square)
print(transform(3))    # (3+1=4) → (4*2=8) → (8**2=64) → 64
print(transform(0))    # (0+1=1) → (1*2=2) → (2**2=4)  → 4
```

**Why:** `pipe` returns a **new function**, not a value. The returned `piped` function is the composed pipeline — it can be stored, reused, and tested like any other function.

</details>

---

<a id="q15"></a>

### Q15 · Real-world — Data Transform Pipeline

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


**Problem:**
You have a list of orders. Each order is a dict with `status`, `quantity`, and `price`.

1. **Filter** — keep only `"completed"` orders
2. **Map** — compute the revenue for each order (`quantity * price`)
3. **Reduce** — sum all revenues into a single total

```python
from functools import reduce

orders = [
    {"status": "completed", "quantity": 3, "price": 10.00},
    {"status": "pending",   "quantity": 2, "price": 15.00},
    {"status": "completed", "quantity": 1, "price": 50.00},
    {"status": "cancelled", "quantity": 4, "price": 5.00},
    {"status": "completed", "quantity": 2, "price": 25.00},
]
# expected total: 30.0 + 50.0 + 50.0 = 130.0
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Chain the three steps: `filter` on status, `map` to revenue, `reduce` to sum. Convert `filter` and `map` to lists so you can inspect intermediate results.

</details>

<details>
<summary>✅ Answer</summary>

```python
from functools import reduce

orders = [
    {"status": "completed", "quantity": 3, "price": 10.00},
    {"status": "pending",   "quantity": 2, "price": 15.00},
    {"status": "completed", "quantity": 1, "price": 50.00},
    {"status": "cancelled", "quantity": 4, "price": 5.00},
    {"status": "completed", "quantity": 2, "price": 25.00},
]

# Step 1 — filter: keep completed orders only
completed = list(filter(lambda o: o["status"] == "completed", orders))

# Step 2 — map: compute revenue per order
revenues = list(map(lambda o: o["quantity"] * o["price"], completed))
# [30.0, 50.0, 50.0]

# Step 3 — reduce: sum all revenues
total = reduce(lambda acc, r: acc + r, revenues, 0)
print(total)   # 130.0

# One-liner version (less readable, but shows composability)
total = reduce(
    lambda acc, r: acc + r,
    map(lambda o: o["quantity"] * o["price"],
        filter(lambda o: o["status"] == "completed", orders)),
    0
)
```

**Why:** This filter-map-reduce pattern is the backbone of data processing pipelines. In production you would often use pandas or SQL — but understanding the underlying pattern lets you apply it anywhere and reason about what each stage is doing.

</details>

---

**[Back to Theory](./theory.md)** · **[Back to Functions](../theory.md)**

**Related:** [Closures & Decorators](../02_closures_decorators/01_closures_theory.md) · [Itertools & Functools](../03_itertools_functools/theory.md)
