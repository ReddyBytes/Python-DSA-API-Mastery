Functional programming treats functions as first-class values — things you pass around, store, and compose just like numbers or strings.

---

## 📌 Learning Priority

**Must Learn:** first-class functions · functions stored in variables/lists/dicts · higher-order functions · map() · filter() · list comprehensions as FP

**Should Learn:** reduce() · pure vs impure functions · side effects · function composition · partial application basics

**Good to Know:** functools.partial · compose patterns · currying · referential transparency

**Reference:** itertools as FP toolkit (covered in 03_itertools_functools/)

---

## Chapter 1: Functions Are First-Class Citizens

In Python, a function is just a value. Like an integer or a string, you can put it in a variable, put it in a list, pass it to another function, or return it from a function. The function object lives in memory just like any other object — its name is just a label pointing to it.

```
Memory
──────────────────────────────────────
  "hello"  →  str object at 0x1a2b
  42       →  int object at 0x3c4d
  greet    →  function object at 0x5e6f   ← same idea
──────────────────────────────────────
```

**Assign a function to a variable:**

```python
def greet(name):
    return f"Hello, {name}"

say_hi = greet          # ← assign the function object (no parentheses)
print(say_hi("Alice"))  # Hello, Alice
```

**Store functions in a list:**

```python
def double(x): return x * 2
def square(x): return x ** 2
def negate(x): return -x

transforms = [double, square, negate]   # ← list of function objects

for fn in transforms:
    print(fn(4))   # 8, 16, -4
```

**Store functions in a dict (dispatch table pattern):**

```python
def add(a, b): return a + b
def sub(a, b): return a - b
def mul(a, b): return a * b

ops = {
    "+": add,
    "-": sub,
    "*": mul,
}

result = ops["+"](10, 3)   # ← look up and call by name
print(result)              # 13
```

### `func` vs `func()` — the most common confusion

This trips up almost every beginner. The parentheses are the **call operator** — they execute the function and give you back its return value.

```python
def greet():
    return "Hello"

greet    # ← the function object itself  → <function greet at 0x...>
greet()  # ← call it, get the result    → "Hello"

x = greet    # x holds the function (useful for HOFs)
y = greet()  # y holds "Hello" (you already ran it)
```

The rule: if you want to pass a function somewhere, **no parentheses**. If you want its result, **add parentheses**.

---

## Chapter 2: Higher-Order Functions

Think of a factory assembly line. The **machine** (conveyor belt, stamper, sorter) does not care what tool is loaded into it — you swap in the right tool for the job. The machine is the **higher-order function (HOF)**; the tool is the function you pass in.

A **higher-order function** is any function that either:
- takes one or more functions as arguments, or
- returns a function as its result

**The simplest HOF — `apply_twice`:**

```python
def apply_twice(func, value):   # ← takes a function as argument
    return func(func(value))    # apply func, then apply it again

def double(x):
    return x * 2

print(apply_twice(double, 3))   # double(double(3)) → double(6) → 12
```

**Sorting with `key=` — a HOF you use every day:**

```python
words = ["banana", "fig", "apple", "date"]

# key= takes a function that extracts a sort key from each element
sorted_by_length = sorted(words, key=len)        # ['fig', 'fig'... by len
sorted_alpha     = sorted(words, key=str.lower)  # alphabetical, case-insensitive

people = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
by_age = sorted(people, key=lambda p: p["age"])  # ← lambda as the tool
```

**Functions that return functions (factory pattern):**

```python
def make_multiplier(n):       # ← takes a value
    def multiply(x):          # ← defines a new function inside
        return x * n
    return multiply           # ← returns the function (no call!)

triple = make_multiplier(3)
print(triple(7))   # 21
print(triple(10))  # 30
```

The inner function "remembers" `n` even after `make_multiplier` returns. This is a **closure** — covered in full depth in `02_closures_decorators/`.

---

## Chapter 3: Pure Functions and Side Effects

A **pure function** is like a calculator: same input, same output, every time, no side effects. No global state. No network calls. No mutation. You feed it numbers, it gives you a number back — it has no memory of previous calls and changes nothing outside itself.

**Pure — predictable, testable, safe:**

```python
def add(a, b):
    return a + b   # depends only on its inputs, changes nothing

add(2, 3)  # always 5, no matter what else is happening in the program
```

**Impure — output depends on external state:**

```python
total = 0

def add_to_total(n):   # ← reads AND modifies a global variable
    global total
    total += n
    return total

add_to_total(5)   # 5
add_to_total(5)   # 10 ← same input, different output!
```

**Why pure functions matter:**

- **Testability** — no setup, no teardown, no mocking. Just call and assert.
- **Parallelism** — safe to run on multiple threads; no shared state to corrupt.
- **Reasoning** — you can read a pure function in isolation and understand it completely.
- **Caching** — same input always gives same output, so results can be memoized.

**Side effects taxonomy — what counts as a side effect:**

```
Modifying a global variable      ← side effect
Modifying a mutable argument     ← side effect
Printing to the console          ← side effect (I/O)
Writing to a file                ← side effect (I/O)
Making a network request         ← side effect (I/O)
Raising an exception             ← side effect
Reading from a database          ← side effect (external state)
```

Note: I/O is always a side effect. Real programs need I/O — the goal is to push side effects to the edges and keep core logic pure.

**⚠️ Common mistake: mutating a list argument**

```python
# IMPURE — modifies the caller's list
def add_tax_impure(prices, rate):
    for i in range(len(prices)):
        prices[i] *= (1 + rate)      # ← mutates the original list
    return prices

# PURE — returns a new list, original untouched
def add_tax_pure(prices, rate):
    return [p * (1 + rate) for p in prices]   # ← creates new list

original = [10, 20, 30]
add_tax_impure(original, 0.1)
print(original)   # [11.0, 22.0, 33.0] ← surprise! original changed

original2 = [10, 20, 30]
result = add_tax_pure(original2, 0.1)
print(original2)  # [10, 20, 30] ← untouched
print(result)     # [11.0, 22.0, 33.0]
```

---

## Chapter 4: map() and filter()

Picture an assembly line. **`map()`** is the transformation station — every item passes through and gets modified. **`filter()`** is the quality control gate — items either pass or get rejected.

### map()

`map(function, iterable)` applies a function to every item and returns a **lazy iterator**.

```python
prices = [10.0, 20.0, 30.0]

# with a named function
def add_tax(p): return p * 1.1
taxed = list(map(add_tax, prices))    # [11.0, 22.0, 33.0]

# with a lambda (common shorthand)
taxed = list(map(lambda p: p * 1.1, prices))

# with two iterables — applies function to matching pairs
a = [1, 2, 3]
b = [10, 20, 30]
sums = list(map(lambda x, y: x + y, a, b))   # [11, 22, 33]
```

### filter()

`filter(function, iterable)` keeps items where the function returns **truthy**.

```python
numbers = [1, -2, 3, -4, 5, 0]

positives = list(filter(lambda n: n > 0, numbers))   # [1, 3, 5]
```

### Why list comprehension is often preferred

**Readability rule:** if the logic fits cleanly on one line, a comprehension is usually clearer. `map`/`filter` shine when you already have a named function.

| Approach | Code | Readable? |
|---|---|---|
| `map` + lambda | `list(map(lambda n: n**2, nums))` | OK |
| comprehension | `[n**2 for n in nums]` | Cleaner |
| `filter` + lambda | `list(filter(lambda n: n > 0, nums))` | OK |
| comprehension | `[n for n in nums if n > 0]` | Cleaner |
| `map` + named fn | `list(map(double, nums))` | Very clean |
| loop | `result = []; for n in nums: result.append(...)` | Verbose |

**The rule of thumb:** use a named function with `map`/`filter` when the transformation is non-trivial and already has a name. Use a comprehension for simple inline logic.

---

## Chapter 5: reduce() — Folding a Sequence into One Value

`reduce` collapses a list into a single value by repeatedly applying a 2-argument function: start with the first two elements, apply the function, take the result, apply to the next element, and keep going until one value remains.

```
[1, 2, 3, 4, 5]  with  add(a, b)

Step 1: add(1, 2) = 3
Step 2: add(3, 3) = 6
Step 3: add(6, 4) = 10
Step 4: add(10, 5) = 15
```

`reduce` lives in `functools` (moved out of builtins in Python 3 — Guido considered it too easy to abuse).

```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]

# Running total
total = reduce(lambda acc, n: acc + n, numbers)   # 15

# Running product
product = reduce(lambda acc, n: acc * n, numbers)  # 120

# Building a dict from a list of (key, value) pairs
pairs = [("a", 1), ("b", 2), ("c", 3)]
d = reduce(lambda acc, pair: {**acc, pair[0]: pair[1]}, pairs, {})
# {"a": 1, "b": 2, "c": 3}
```

The third argument to `reduce` is the **initial value** — crucial when the list might be empty:

```python
reduce(lambda acc, n: acc + n, [], 0)   # 0  ← safe
reduce(lambda acc, n: acc + n, [])      # TypeError: reduce() of empty iterable with no initial value
```

**When NOT to use reduce:**

`reduce` becomes hard to read as soon as the lambda gets complex. Prefer a simple loop or `sum()` / `max()` / `min()` for the common cases:

```python
# Don't
total = reduce(lambda acc, n: acc + n, numbers)

# Do
total = sum(numbers)
```

Use `reduce` when there is no built-in for your specific fold operation.

---

## Chapter 6: Function Composition

In Unix, you chain commands with pipes: `ls | grep .py | wc -l`. The output of one becomes the input of the next. **Function composition** is the same idea — chain functions so data flows through a pipeline.

There are two conventions:

- **compose** (right-to-left, mathematical notation): `compose(f, g)(x)` = `f(g(x))`
- **pipe** (left-to-right, more readable): `pipe(g, f)(x)` = `f(g(x))`

```python
# compose — applies right-to-left
def compose(*funcs):
    def composed(x):
        result = x
        for fn in reversed(funcs):   # ← reversed: apply last arg first
            result = fn(result)
        return result
    return composed

# pipe — applies left-to-right (usually more readable)
def pipe(*funcs):
    def piped(x):
        result = x
        for fn in funcs:              # ← in order: apply first arg first
            result = fn(result)
        return result
    return piped
```

**Real-world: text normalization pipeline**

```python
import string

def strip_whitespace(s): return s.strip()
def to_lower(s):         return s.lower()
def remove_punctuation(s):
    return s.translate(str.maketrans("", "", string.punctuation))
def split_words(s):      return s.split()

normalize = pipe(
    strip_whitespace,    # "  Hello, World!  " → "Hello, World!"
    to_lower,            # → "hello, world!"
    remove_punctuation,  # → "hello world"
    split_words,         # → ["hello", "world"]
)

print(normalize("  Hello, World!  "))  # ['hello', 'world']
```

**⚠️ Gotcha: type compatibility**

Each function's output must be a valid input for the next function. The pipeline above works because every step takes and returns a string — until `split_words`, which terminates the chain with a list.

```python
# This would break:
bad_pipe = pipe(split_words, to_lower)   # split_words returns a list
# to_lower receives a list → AttributeError: 'list' object has no attribute 'lower'
```

Design your pipeline so types flow cleanly from stage to stage.

---

## Chapter 7: Common Mistakes

**1. Calling the function instead of passing it**

```python
items = ["hello", "world", "python"]

# WRONG — len() calls len with no arguments → TypeError
result = list(map(len(), items))

# RIGHT — pass the function object
result = list(map(len, items))   # [5, 5, 6]
```

**2. Mutating a list argument (impure function)**

```python
# WRONG — modifies the caller's data silently
def append_zero(lst):
    lst.append(0)   # ← mutates in place
    return lst

data = [1, 2, 3]
new = append_zero(data)
print(data)   # [1, 2, 3, 0] ← original changed — surprise!

# RIGHT — return a new list
def append_zero_pure(lst):
    return lst + [0]   # ← creates new list, original untouched
```

**3. Confusing `filter(None, items)` — what it actually does**

```python
items = [0, 1, None, 2, "", "hello", False, True]

# filter(None, items) keeps only TRUTHY values — not "items that are not None"
result = list(filter(None, items))   # [1, 2, 'hello', True]
# 0, None, "", False are all falsy and get dropped

# To filter ONLY None values:
no_nones = [x for x in items if x is not None]   # [0, 1, 2, "", "hello", False, True]
```

**4. `reduce` over an empty sequence with no initial value**

```python
from functools import reduce

# WRONG — crashes on empty list
total = reduce(lambda acc, n: acc + n, [])   # TypeError!

# RIGHT — always provide an initial value when the list might be empty
total = reduce(lambda acc, n: acc + n, [], 0)   # 0
```

---

**[Back to Functions](../theory.md)**

**Related:** [Practice Problems](./practice.md) · [Closures & Decorators](../02_closures_decorators/01_closures_theory.md) · [Itertools & Functools](../03_itertools_functools/theory.md)
