# Practice — 01 Python Fundamentals

> 🟢 Basic · 🟡 Intermediate · 🟠 Advanced  
> Work these in order — earlier questions build mental models for later ones.

---

## Quick Index

| # | Concept | Difficulty |
|---|---------|-----------|
| [Q1](#q1) | print() — sep= and end= | 🟢 |
| [Q2](#q2) | input() and type conversion | 🟢 |
| [Q3](#q3) | Indentation and syntax | 🟢 |
| [Q4](#q4) | Variables as references (labels, not boxes) | 🟢 |
| [Q5](#q5) | Shared reference — spot the mutation | 🟢 |
| [Q6](#q6) | Rebinding vs mutation — predict output | 🟡 |
| [Q7](#q7) | Shallow copy vs deep copy | 🟡 |
| [Q8](#q8) | Config mutation bug — find and fix | 🟡 |
| [Q9](#q9) | Reference counting and del | 🟡 |
| [Q10](#q10) | Mutable default argument trap | 🟡 |
| [Q11](#q11) | Pass-by-assignment — mutate vs rebind | 🟡 |
| [Q12](#q12) | += on mutable vs immutable | 🟡 |
| [Q13](#q13) | is vs == — object identity trap | 🟡 |
| [Q14](#q14) | Single-element tuple — trailing comma | 🟢 |
| [Q15](#q15) | Falsy values — when 0 and "" are valid data | 🟡 |
| [Q16](#q16) | Exception variable scope | 🟡 |
| [Q17](#q17) | Chained comparisons | 🟢 |
| [Q18](#q18) | Multiple assignment and swap | 🟢 |
| [Q19](#q19) | Extended unpacking (*args) | 🟡 |
| [Q20](#q20) | Mutable objects inside tuples | 🟡 |
| [Q21](#q21) | Late binding closures — predict output | 🟠 |
| [Q22](#q22) | Late binding closure — fix the bug | 🟠 |
| [Q23](#q23) | UnboundLocalError — why it happens | 🟡 |
| [Q24](#q24) | Truthiness — classify values | 🟢 |
| [Q25](#q25) | Deep copy necessity | 🟡 |
| [Q26](#q26) | String interning — is vs == | 🟡 |
| [Q27](#q27) | Tuple mutability paradox | 🟡 |
| [Q28](#q28) | Multiple return + unpack | 🟢 |
| [Q29](#q29) | Augmented assignment and shared reference | 🟠 |
| [Q30](#q30) | Capstone — reference model trace | 🟠 |

---

<a id="q1"></a>

### Q1 · print-options — print() with sep= and end= 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


What does this print? Explain what `sep=` and `end=` do.

```python
print("a", "b", "c", sep="-", end="!")
print("done")
```

<details>
<summary>Hint</summary>

`sep` is placed between each argument. `end` replaces the default newline `\n`.

</details>

<details>
<summary>Answer</summary>

```
a-b-c!done
```

`sep="-"` joins the three arguments with `-`.  
`end="!"` replaces the trailing newline, so `"done"` runs on immediately after.

**Why:** `print` is actually a function with default `sep=" "` and `end="\n"`. Changing them controls output formatting without string concatenation.

</details>

---

<a id="q2"></a>

### Q2 · input-conversion — input() and type conversion 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


What is wrong here, and how do you fix it?

```python
age = input("Enter your age: ")
if age > 18:
    print("Adult")
```

<details>
<summary>Hint</summary>

`input()` always returns a string.

</details>

<details>
<summary>Answer</summary>

```python
age = int(input("Enter your age: "))   # convert to int before comparing
if age > 18:
    print("Adult")
```

`input()` returns `str`. Comparing a string to an integer with `>` raises `TypeError: '>' not supported between instances of 'str' and 'int'`.

**Why:** Python won't silently coerce types. You must convert explicitly with `int()`, `float()`, etc.

</details>

---

<a id="q3"></a>

### Q3 · indentation — why this crashes 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


What error does Python raise and why?

```python
def greet(name):
print(f"Hello, {name}!")
```

<details>
<summary>Hint</summary>

Python uses indentation as syntax, not style.

</details>

<details>
<summary>Answer</summary>

`IndentationError: expected an indented block`. The `print` line must be indented to be inside the function body. Python uses whitespace to define code blocks — unlike Java/C which use `{}`.

</details>

---

<a id="q4"></a>

### Q4 · references — variables as labels 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


Run this in your head. What does `a` print?

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)
```

<details>
<summary>Hint</summary>

`b = a` does NOT create a copy.

</details>

<details>
<summary>Answer</summary>

```
[1, 2, 3, 4]
```

`b = a` makes `b` point to the **same list object** as `a`. Calling `b.append(4)` mutates that shared object. Both names see the change because there is only one list.

**Why:** Python variables are labels (pointers) to objects. `=` binds a name to an object, never copies the object.

</details>

---

<a id="q5"></a>

### Q5 · shared-reference — spot the mutation 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Predict each print output:

```python
x = [10, 20]
y = x
z = x

y[0] = 99
z.append(30)
x = [1, 2]   # rebind x to a new list

print(y)
print(z)
print(x)
```

<details>
<summary>Hint</summary>

Rebinding `x` with `=` doesn't change the original list. Only mutation methods (`.append`, item assignment) change the object.

</details>

<details>
<summary>Answer</summary>

```
[99, 20, 30]
[99, 20, 30]
[1, 2]
```

`y`, `z`, and the original `x` all pointed to the same list. `y[0] = 99` and `z.append(30)` both mutate that shared object — so both `y` and `z` see all changes. `x = [1, 2]` just rebinds `x` to a new list; `y` and `z` still point to the original.

</details>

---

<a id="q6"></a>

### Q6 · rebinding-vs-mutation — predict output 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


What is the final value of `items` after this code?

```python
def add_default(lst):
    lst = lst + [99]   # creates a new list, rebinds local `lst`
    return lst

items = [1, 2, 3]
add_default(items)
print(items)
```

<details>
<summary>Hint</summary>

`+` on lists creates a new list. `lst = ...` rebinds the local parameter. The caller's `items` is never touched.

</details>

<details>
<summary>Answer</summary>

```
[1, 2, 3]
```

Inside `add_default`, `lst + [99]` creates a brand-new list and `lst = ...` rebinds the local name to it. The original `items` list is never mutated. To affect the caller, you'd use `lst.append(99)` or `lst.extend([99])`.

</details>

---

<a id="q7"></a>

### Q7 · shallow-deep-copy — fix the mutation 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


This code is supposed to keep `original` unchanged. It doesn't work. Fix it.

```python
import copy

original = [[1, 2], [3, 4]]
clone = original.copy()   # or: clone = original[:]

original[0].append(99)
print(clone[0])   # expected [1, 2] but prints [1, 2, 99]
```

<details>
<summary>Hint</summary>

Shallow copy copies the outer list but shares the inner list objects.

</details>

<details>
<summary>Answer</summary>

```python
clone = copy.deepcopy(original)
```

`original.copy()` creates a new outer list but the inner lists (`[1, 2]`, `[3, 4]`) are still **shared**. Mutating `original[0]` changes the same inner list that `clone[0]` points to. `deepcopy` recursively copies every nested object.

**Rule:** Use `copy()` when the object contains only primitives. Use `deepcopy()` when it contains mutable nested objects.

</details>

---

<a id="q8"></a>

### Q8 · config-mutation — find and fix the bug 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


The default config is getting corrupted. Explain why and fix it.

```python
DEFAULT = {"timeout": 30, "retries": 3}

def get_config(overrides=None):
    config = DEFAULT          # ← problem here
    if overrides:
        config.update(overrides)
    return config

get_config({"timeout": 60})
print(DEFAULT)  # prints {"timeout": 60, "retries": 3} — corrupted!
```

<details>
<summary>Hint</summary>

`config = DEFAULT` is a reference assignment, not a copy.

</details>

<details>
<summary>Answer</summary>

```python
def get_config(overrides=None):
    config = DEFAULT.copy()   # work on a fresh copy
    if overrides:
        config.update(overrides)
    return config
```

`config = DEFAULT` makes `config` an alias for the same dict. `config.update(...)` mutates that dict — which IS `DEFAULT`. Always work with `DEFAULT.copy()` to protect global state.

</details>

---

<a id="q9"></a>

### Q9 · ref-counting — predict when memory is freed 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


```python
a = [1, 2, 3]
b = a
c = a

del a
del b
# Is the list freed here?
print(c)
```

What does `print(c)` output? When is the list freed?

<details>
<summary>Hint</summary>

Python frees an object only when its reference count reaches 0.

</details>

<details>
<summary>Answer</summary>

```
[1, 2, 3]
```

After `del a` and `del b`, `c` still holds a reference to the list — reference count is 1, not 0. The list is only freed when `c` also goes out of scope or is deleted. `del` removes a name binding, not the object itself.

</details>

---

<a id="q10"></a>

### Q10 · mutable-default — classic gotcha 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


Why does this produce surprising output? Fix it.

```python
def add_item(item, history=[]):
    history.append(item)
    return history

print(add_item("a"))
print(add_item("b"))
print(add_item("c"))
```

<details>
<summary>Hint</summary>

Default argument values are evaluated **once** at function definition, not on each call.

</details>

<details>
<summary>Answer</summary>

Output (surprising):
```
['a']
['a', 'b']
['a', 'b', 'c']
```

`history=[]` creates one list when the `def` line executes. Every call that doesn't pass `history` shares **that same list object** — it accumulates across calls.

Fix:
```python
def add_item(item, history=None):
    if history is None:
        history = []    # fresh list every call
    history.append(item)
    return history
```

**Why:** `None` is immutable and safe as a sentinel. Create the mutable default inside the function body.

</details>

---

<a id="q11"></a>

### Q11 · pass-by-assignment — mutate vs rebind 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


Predict what each function call does to `my_list`:

```python
def mutate(lst):
    lst.append(99)

def rebind(lst):
    lst = [1, 2, 3]

my_list = [10, 20]
mutate(my_list)
print(my_list)   # A

my_list = [10, 20]
rebind(my_list)
print(my_list)   # B
```

<details>
<summary>Hint</summary>

Python passes references. Mutating the object affects the caller. Rebinding the local name does not.

</details>

<details>
<summary>Answer</summary>

```
A: [10, 20, 99]
B: [10, 20]
```

`mutate` calls `.append` on the shared list — the caller sees the change. `rebind` assigns `lst` to a new list — this only affects the local name `lst`; the caller's `my_list` still points to the original.

</details>

---

<a id="q12"></a>

### Q12 · augmented-assignment — mutable vs immutable 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


```python
x = [1, 2]
y = x
x += [3]

a = (1, 2)
b = a
a += (3,)

print(y)   # A
print(b)   # B
```

Predict A and B. Why are they different?

<details>
<summary>Hint</summary>

`+=` on a list calls `__iadd__` (in-place). `+=` on a tuple creates a new object (tuples are immutable).

</details>

<details>
<summary>Answer</summary>

```
A: [1, 2, 3]   ← y sees the change
B: (1, 2)      ← b is unchanged
```

`list.__iadd__` mutates the existing list in-place and returns it — `x` and `y` still point to the same object. `tuple.__iadd__` creates a new tuple and rebinds `a` to it — `b` still points to the original `(1, 2)`.

</details>

---

<a id="q13"></a>

### Q13 · is-vs-equals — identity trap 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


Why does this give inconsistent results? What's the rule?

```python
a = 100
b = 100
print(a is b)    # True

c = 1000
d = 1000
print(c is d)    # Often False
```

<details>
<summary>Hint</summary>

CPython caches small integers from -5 to 256.

</details>

<details>
<summary>Answer</summary>

CPython pre-creates ("interns") integer objects from -5 to 256. Any variable assigned 100 points to the same cached object. For values outside that range, each assignment creates a new object — so `is` may return `False` even when the values are equal.

**Rule:** Never use `is` for value comparison. `is` tests object identity (same memory address).  
- Use `==` for value equality  
- Use `is` only for: `None`, `True`, `False`

</details>

---

<a id="q14"></a>

### Q14 · tuple-comma — single-element tuple 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


What is the type of each variable?

```python
a = (42)
b = (42,)
c = 42,
d = ()
```

<details>
<summary>Hint</summary>

The comma creates a tuple, not the parentheses.

</details>

<details>
<summary>Answer</summary>

```
a → int (42)        — parens are just grouping
b → tuple (42,)     — trailing comma makes it a tuple
c → tuple (42,)     — parentheses optional, comma is enough
d → tuple ()        — empty tuple (exception: () works without comma)
```

**Why:** The comma is the tuple constructor. Parentheses are just for grouping/readability. This trips people when creating a single-item tuple: `("hello")` is a string, `("hello",)` is a tuple.

</details>

---

<a id="q15"></a>

### Q15 · falsy-values — when 0 and "" are valid 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


This function has a logic bug when `count` is 0 or `name` is `""`. Find and fix it.

```python
def display(name, count):
    if not name:
        name = "Unknown"
    if not count:
        count = 1
    print(f"{name}: {count}")

display("", 0)   # should print ': 0' but overwrites both
```

<details>
<summary>Hint</summary>

0 and `""` are falsy but valid values. Use `is None` to check for "missing".

</details>

<details>
<summary>Answer</summary>

```python
def display(name, count):
    if name is None:
        name = "Unknown"
    if count is None:
        count = 1
    print(f"{name}: {count}")
```

`if not name` is `True` for both `None` (missing) AND `""` (valid empty string). `if not count` fires for both `None` and `0` (a valid score). Use `is None` when the only "missing" sentinel is `None`, not any falsy value.

</details>

---

<a id="q16"></a>

### Q16 · exception-scope — variable deleted after except 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


Why does this raise `NameError`? Fix it to save the error message.

```python
try:
    raise ValueError("connection refused")
except ValueError as e:
    pass

print(e)   # NameError!
```

<details>
<summary>Hint</summary>

Python 3 deletes the `as e` variable when the `except` block exits.

</details>

<details>
<summary>Answer</summary>

```python
try:
    raise ValueError("connection refused")
except ValueError as e:
    error_msg = str(e)   # save to a regular variable

print(error_msg)   # works fine
```

In Python 3, the `as e` variable is explicitly deleted when the `except` block ends. This prevents reference cycles. If you need the exception text later, assign it to a regular variable inside the block.

</details>

---

<a id="q17"></a>

### Q17 · chained-comparisons — predict output 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


```python
x = 5
print(1 < x < 10)
print(10 > x > 1)
print(1 < x < 4)
print(x == 5 == 5)
```

<details>
<summary>Hint</summary>

`a < b < c` means `(a < b) and (b < c)` — each middle term is evaluated once.

</details>

<details>
<summary>Answer</summary>

```
True
True
False
True
```

Python chained comparisons evaluate as `(a < b) and (b < c)` — not `((a < b) < c)`. Works left-to-right in any direction. `x == 5 == 5` is `(x == 5) and (5 == 5)` = `True and True`.

</details>

---

<a id="q18"></a>

### Q18 · swap — multiple assignment 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


Swap `a` and `b` without a temp variable. How does Python guarantee this works?

```python
a = 10
b = 20
# your one-liner here
print(a, b)   # should print: 20 10
```

<details>
<summary>Hint</summary>

Python evaluates the **entire right side** before any assignment happens.

</details>

<details>
<summary>Answer</summary>

```python
a, b = b, a
```

Python evaluates the right side `(b, a)` as a tuple `(20, 10)` fully before assigning. Then it unpacks: `a = 20`, `b = 10`. This atomicity is why the swap works without needing a temporary variable.

</details>

---

<a id="q19"></a>

### Q19 · extended-unpacking — star operator 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


Unpack `data` so that `first = 1`, `last = 5`, and `middle = [2, 3, 4]`.

```python
data = [1, 2, 3, 4, 5]
# your unpacking here
```

<details>
<summary>Hint</summary>

Python 3 supports `*name` in unpacking to capture remaining items as a list.

</details>

<details>
<summary>Answer</summary>

```python
first, *middle, last = data
# first=1, middle=[2, 3, 4], last=5
```

The `*middle` catches everything not claimed by positional names. Works at start, middle, or end. `*_` for values you want to discard:

```python
_, important, *_ = [10, 99, 30, 40, 50]
# important=99
```

</details>

---

<a id="q20"></a>

### Q20 · tuple-mutability — paradox 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


A tuple is "immutable" — so why does this succeed?

```python
t = ([1, 2], [3, 4])
t[0].append(99)
print(t)    # ([1, 2, 99], [3, 4])
```

And why does this fail?

```python
t[0] = [99]   # TypeError
```

<details>
<summary>Hint</summary>

A tuple stores references to objects. Immutability means you can't change WHICH objects the tuple holds — but not what those objects contain.

</details>

<details>
<summary>Answer</summary>

The tuple's "slots" (the references) are immutable — `t[0] = [99]` would change which object slot 0 points to, so it raises `TypeError`. But `t[0].append(99)` mutates the list **object that slot 0 already points to** — the slot itself doesn't change. The tuple still holds references to the same two list objects; those lists just have different contents now.

**Bonus:** This means tuples containing mutable objects are **not hashable** and can't be dict keys.

</details>

---

<a id="q21"></a>

### Q21 · late-binding — predict output 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)


```python
funcs = [lambda: i for i in range(5)]
print([f() for f in funcs])
```

What does this print, and why?

<details>
<summary>Hint</summary>

Closures capture the variable `i`, not the value of `i` at creation time.

</details>

<details>
<summary>Answer</summary>

```
[4, 4, 4, 4, 4]
```

Each lambda closes over the variable `i` — not a snapshot of its value. By the time any lambda is called, the loop has finished and `i == 4`. All five lambdas read the same `i` which is now 4.

</details>

---

<a id="q22"></a>

### Q22 · late-binding-fix — two ways to fix it 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)


Fix Q21 so the list prints `[0, 1, 2, 3, 4]`. Show two approaches.

<details>
<summary>Hint</summary>

You need to capture the value of `i` at creation time, not the variable.

</details>

<details>
<summary>Answer</summary>

**Fix 1 — default argument (captures value at creation):**
```python
funcs = [lambda i=i: i for i in range(5)]
print([f() for f in funcs])   # [0, 1, 2, 3, 4]
```

`i=i` evaluates `i` at lambda creation time and binds it as a default arg.

**Fix 2 — factory function:**
```python
def make_func(n):
    return lambda: n   # n is a local variable, its value is captured here

funcs = [make_func(i) for i in range(5)]
print([f() for f in funcs])   # [0, 1, 2, 3, 4]
```

Each call to `make_func` creates a new scope with its own `n`. Clean and readable for complex closures.

</details>

---

<a id="q23"></a>

### Q23 · unbound-local — explain the error 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)


```python
counter = 10

def increment():
    counter += 1   # UnboundLocalError!

increment()
```

Why does this fail even though `counter` exists in global scope?

<details>
<summary>Hint</summary>

Any assignment to a variable inside a function makes Python treat that variable as local **for the entire function**.

</details>

<details>
<summary>Answer</summary>

When Python compiles `increment`, it sees `counter = ...` (via `+=`) and marks `counter` as a **local variable** for the whole function. When the function runs, it tries to read `counter` (right side of `+=`) before it's been assigned locally — `UnboundLocalError`.

Fix 1 — `global` keyword:
```python
def increment():
    global counter
    counter += 1
```

Fix 2 (preferred) — pure function, no shared state:
```python
def increment(n):
    return n + 1

counter = increment(counter)
```

</details>

---

<a id="q24"></a>

### Q24 · truthiness — classify 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)


Which of these are falsy in Python?

```
0    0.0    ""    "0"    []    [0]    {}    {0}    None    False    0j
```

<details>
<summary>Hint</summary>

A value is falsy if `bool(value)` returns `False`.

</details>

<details>
<summary>Answer</summary>

**Falsy:** `0`, `0.0`, `""`, `[]`, `{}`, `None`, `False`, `0j`

**Truthy:** `"0"` (non-empty string), `[0]` (non-empty list), `{0}` (non-empty set)

The pattern: **empty or zero = falsy**. A container with any element is truthy, even if that element itself is falsy.

</details>

---

<a id="q25"></a>

### Q25 · deep-copy-need — when is shallow copy enough? 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)


You have a list of user dicts. You want a "backup" before modifying one user's nested settings. Which copy do you need?

```python
import copy

users = [
    {"name": "Alice", "prefs": {"theme": "dark"}},
    {"name": "Bob",   "prefs": {"theme": "light"}},
]

backup = ???
users[0]["prefs"]["theme"] = "system"
# backup[0]["prefs"]["theme"] should still be "dark"
```

<details>
<summary>Hint</summary>

`users[0]["prefs"]` is a nested dict two levels deep.

</details>

<details>
<summary>Answer</summary>

```python
backup = copy.deepcopy(users)
```

`users.copy()` → only outer list is copied, inner dicts still shared.  
`[u.copy() for u in users]` → outer list + each top-level dict copied, but `"prefs"` dicts still shared.  
`copy.deepcopy(users)` → fully independent copy of all nested objects. Required when you need to modify any nested mutable value without affecting the original.

</details>

---

<a id="q26"></a>

### Q26 · string-interning — is vs == with strings 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)


Predict True or False. Explain the rule.

```python
s1 = "hello"
s2 = "hello"
print(s1 is s2)       # A

s3 = "hello world"
s4 = "hello world"
print(s3 is s4)       # B

print(s1 == s2)       # C
```

<details>
<summary>Hint</summary>

CPython interns short identifier-like strings automatically.

</details>

<details>
<summary>Answer</summary>

```
A: True   (usually — CPython interns short identifier-like strings)
B: False  (usually — longer strings or strings with spaces not interned by default)
C: True   (always — == compares values)
```

**Rule:** Never rely on `is` for string comparison. String interning is a CPython implementation detail that can change. Always use `==` to compare string values.

</details>

---

<a id="q27"></a>

### Q27 · tuple-hashability — why can't this be a dict key? 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)


```python
t = ([1, 2], [3, 4])
d = {t: "value"}   # TypeError: unhashable type
```

Rewrite `t` so it CAN be used as a dict key. What's the rule?

<details>
<summary>Hint</summary>

For an object to be hashable, it must be both immutable AND contain only hashable elements.

</details>

<details>
<summary>Answer</summary>

```python
t = ((1, 2), (3, 4))   # tuple of tuples — all hashable
d = {t: "value"}       # works
```

A tuple is only hashable if ALL its elements are hashable. `[1, 2]` is a list — mutable, not hashable. Converting inner lists to tuples makes the whole structure hashable. **Rule:** Dict keys must be hashable (immutable + recursively hashable).

</details>

---

<a id="q28"></a>

### Q28 · multiple-return — unpack safely 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)


Write a function `min_max(numbers)` that returns both the minimum and maximum in one call. Unpack the result into two variables.

<details>
<summary>Hint</summary>

Return a tuple. Python unpacks it automatically on assignment.

</details>

<details>
<summary>Answer</summary>

```python
def min_max(numbers):
    return min(numbers), max(numbers)   # returns a tuple

lo, hi = min_max([3, 1, 4, 1, 5, 9])
print(lo, hi)   # 1 9
```

Python functions can "return multiple values" by returning a tuple. Tuple unpacking on the left side splits them into separate variables.

</details>

---

<a id="q29"></a>

### Q29 · aug-assign-shared — advanced trace 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)


```python
a = [1, 2]
b = a
a += [3]    # line A

x = (1, 2)
y = x
x += (3,)   # line B

print(a is b)   # C
print(x is y)   # D
```

Predict C and D. Explain the difference between lines A and B.

<details>
<summary>Hint</summary>

List `+=` calls `list.__iadd__` (mutates in place). Tuple `+=` creates a new object.

</details>

<details>
<summary>Answer</summary>

```
C: True
D: False
```

**Line A:** `list.__iadd__([3])` extends the list in-place and returns `a` (same object). `a` and `b` still point to the same list. `a is b` → `True`.

**Line B:** Tuples are immutable. `x += (3,)` is `x = x.__add__((3,))` — creates a new `(1, 2, 3)` tuple and rebinds `x`. `y` still points to the original `(1, 2)`. `x is y` → `False`.

</details>

---

<a id="q30"></a>

### Q30 · capstone — full reference model trace 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)


Trace this code from top to bottom. Write the final value of every variable.

```python
import copy

original = {"data": [1, 2, 3], "count": 0}
alias    = original
shallow  = original.copy()
deep     = copy.deepcopy(original)

alias["count"] += 1          # line 1
alias["data"].append(4)      # line 2
shallow["data"].append(5)    # line 3
deep["data"].append(6)       # line 4
```

What are the final values of `original`, `shallow`, `deep`?

<details>
<summary>Hint</summary>

`alias` is the same object as `original`. `shallow` has its own dict but shares the `data` list. `deep` is fully independent.

</details>

<details>
<summary>Answer</summary>

```
original: {"data": [1, 2, 3, 4, 5], "count": 1}
shallow:  {"data": [1, 2, 3, 4, 5], "count": 0}
deep:     {"data": [1, 2, 3, 6],    "count": 0}
```

- Line 1: `alias["count"] += 1` mutates `original` (same object). `shallow` and `deep` are separate dicts — their `count` stays 0.
- Line 2: `alias["data"].append(4)` mutates the list in `original`. `shallow["data"]` is the **same list object** — it also sees `4`. `deep["data"]` is independent.
- Line 3: `shallow["data"].append(5)` mutates the shared list again. `original` sees `5` too.
- Line 4: `deep["data"].append(6)` only affects `deep`'s independent copy.

</details>

---

## Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 💻 Practice Local | [practice_local.py](./practice_local.py) |
| ⚡ Cheat Sheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| ➡️ Next Module | [../01.1_memory_management/practice.md](../01.1_memory_management/practice.md) |

**[Back to README](../README.md)**
