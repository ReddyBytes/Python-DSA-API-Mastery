# Python Practice — 100 Questions

> From basics to critical thinking — work through all 100 without skipping.

---

## How to Use This File

1. **Read the question. Stop. Think for at least 60 seconds** before clicking the answer. If you reveal immediately, you learn nothing.
2. **Use the "How to think through this" block** — it teaches the reasoning pattern, not just the answer. The goal is to internalise the mental model so you never need the hint again.
3. **Do not rush.** Finishing all 100 with real thought is worth more than skimming 300 questions passively.

---

## How to Think: The 5-Step Framework

Apply this to every question before revealing the answer:

1. **Restate** — What is actually being asked? Strip the noise.
2. **Identify the concept** — Which Python feature or rule is this testing?
3. **Recall the rule** — What is the exact behaviour of that feature?
4. **Apply** — Trace through the specific code or scenario step by step.
5. **Sanity check** — Does your answer make sense? Test it with a simpler example mentally.

---

## Progress Tracker

- [ ] Tier 1 — Basics (Q1–Q25)
- [ ] Tier 2 — Intermediate (Q26–Q50)
- [ ] Tier 3 — Advanced (Q51–Q75)
- [ ] Tier 4 — Interview & Scenario (Q76–Q90)
- [ ] Tier 5 — Critical Thinking (Q91–Q100)

---

## Question Types

| Tag | What it tests |
|---|---|
| `[Normal]` | Recall and apply — straightforward |
| `[Thinking]` | Requires reasoning about Python internals |
| `[Logical]` | Predict output or trace execution |
| `[Critical]` | Edge case or tricky gotcha |
| `[Interview]` | Explain or compare in interview style |
| `[Debug]` | Find and fix the bug in the code |
| `[Design]` | Architecture or approach decision |

---

## Tier 1 — Basics · Q1–Q25

> Focus: Variables, types, control flow, functions, basic OOP, strings, exceptions

---

### Q1 · [Normal] · `variable-binding`

> **In Python, what does it mean that variables are "names bound to objects" rather than boxes that hold values? Why does this matter?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
In Python, a variable is a label (name) that points to an object in memory — not a container that holds a value. When you write `x = 5`, you are not storing 5 in x; you are making the name `x` point to the integer object `5`. Multiple names can point to the same object. When you reassign `x = 10`, you are not changing the object — you are making x point to a new object.

This matters because:
- Assigning one variable to another (`b = a`) does not copy the value — both names point to the same object.
- For mutable objects (lists, dicts), changes through one name are visible through all names pointing to that object.
- For immutable objects (int, str, tuple), this is safe because the object cannot be changed in-place.

**How to think through this:**
1. Visualise each object living in memory with a unique id. Names are arrows pointing at objects.
2. Assignment (`=`) moves the arrow — it does not copy the object.
3. For mutable objects, two arrows pointing at the same target means mutations are shared.

**Key takeaway:** Python variables are references (pointers), not value containers — this is the root cause of most "why did my list change?" bugs.

</details>

> 📖 **Theory:** [Variable Binding](./01_python_fundamentals/theory.md#variables--memory-model-in-python)

---

### Q2 · [Logical] · `identity-vs-equality`

> **What is the output of this code?**

```python
a = [1, 2, 3]
b = a
c = [1, 2, 3]
print(a == c)
print(a is c)
print(a is b)
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
True
False
True
```

- `a == c` → `True` because `==` compares values (contents are the same).
- `a is c` → `False` because `is` compares identity (they are two different list objects in memory).
- `a is b` → `True` because `b = a` made both names point to the same object.

**How to think through this:**
1. `==` asks: do they have the same value? Lists compare element by element.
2. `is` asks: are they the literally the same object? Check with `id(a) == id(c)` — they differ.
3. `b = a` is not a copy — b and a are the same object, so `is` returns True.

**Key takeaway:** Use `==` to compare values; use `is` only to check identity — typically for `None`, `True`, `False`.

</details>

> 📖 **Theory:** [Identity vs Equality](./01_python_fundamentals/theory.md#is-vs--interview-favorite)

---

### Q3 · [Critical] · `mutability`

> **What is the difference between mutable and immutable types in Python? Give two examples of each and explain why the distinction matters.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- **Immutable** — the object's value cannot be changed after creation. Examples: `int`, `str`, `tuple`, `frozenset`.
- **Mutable** — the object can be changed in-place after creation. Examples: `list`, `dict`, `set`, custom class instances.

Why it matters:
1. **Safety in sharing** — if you pass an immutable object to a function, you know it cannot be modified. With mutable objects, the function can change it.
2. **Dict keys** — only immutable (hashable) objects can be dict keys or set members. Lists cannot be dict keys.
3. **Default arguments** — using a mutable default argument is a classic bug (the same object is reused across calls).
4. **Concurrency** — immutable objects are inherently thread-safe; mutable ones require synchronisation.

**How to think through this:**
1. Ask: can I change this object's contents after I create it, or do I get a new object?
2. `s = "hello"; s[0] = "H"` → TypeError. Strings are immutable.
3. `lst = [1,2]; lst[0] = 9` → works fine. Lists are mutable.

**Key takeaway:** Immutability = safe to share; mutability = powerful but requires care when passing around.

</details>

> 📖 **Theory:** [Mutability](./03_data_types/theory.md#strings-are-immutable--what-that-means)

---

### Q4 · [Logical] · `list-operations`

> **What does this print and why?**

```python
x = [1, 2, 3]
y = x
y.append(4)
print(x)
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
[1, 2, 3, 4]
```

`y = x` does not copy the list — both `y` and `x` point to the same list object. When `y.append(4)` mutates the list in-place, `x` sees the change because it is the same object.

**How to think through this:**
1. `y = x` → two names, one list object in memory.
2. `.append()` is an in-place mutation — it does not create a new list.
3. Since both names point to the same object, printing `x` shows the mutation.

**Key takeaway:** To get an independent copy use `y = x[:]` or `y = x.copy()` or `y = list(x)`.

</details>

> 📖 **Theory:** [List Operations](./03_data_types/theory.md#append45-adds-the-list-itself-as-one-item--123-45)

---

### Q5 · [Normal] · `dict-basics`

> **What happens when you access a key that does not exist in a dict using `d[key]` vs `d.get(key)`? When would you use each?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- `d[key]` raises a `KeyError` if the key does not exist.
- `d.get(key)` returns `None` by default (or a custom default: `d.get(key, default_value)`).

When to use each:
- Use `d[key]` when the key **must** exist — the KeyError is a useful signal that something is wrong.
- Use `d.get(key)` when the key is optional and you want to handle absence gracefully without a try/except.

**How to think through this:**
1. Ask: is a missing key an error condition or an expected possibility?
2. If it is an error → `d[key]` gives you a loud failure.
3. If absence is normal → `d.get(key, fallback)` is cleaner than wrapping in try/except.

**Key takeaway:** `d[key]` is assertive (must exist); `d.get(key)` is defensive (might not exist).

</details>

> 📖 **Theory:** [Dictionary Basics](./03_data_types/theory.md#empty-dictionary)

---

### Q6 · [Thinking] · `set-operations`

> **You have two lists and want to find elements in list A that are NOT in list B. What is the most Pythonic and efficient way to do this?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
a = [1, 2, 3, 4, 5]
b = [3, 4, 5, 6, 7]
result = list(set(a) - set(b))  # [1, 2]
```

Or using a set for O(1) lookups:
```python
b_set = set(b)
result = [x for x in a if x not in b_set]
```

The second form preserves order and avoids duplicates being collapsed. The key efficiency insight: checking `x not in list` is O(n) per element; checking `x not in set` is O(1).

**How to think through this:**
1. Naive: `[x for x in a if x not in b]` — works but O(n²) for large lists.
2. Convert b to a set first → membership check becomes O(1).
3. Set difference `set(a) - set(b)` is even cleaner but loses order and deduplicates a.

**Key takeaway:** Convert to set before repeated membership checks — it turns O(n²) into O(n).

</details>

> 📖 **Theory:** [Set Operations](./03_data_types/theory.md#set-math--union-intersection-difference)

---

### Q7 · [Logical] · `loop-else`

> **What does the `else` clause on a `for` loop do? What does this print?**

```python
for i in range(5):
    if i == 3:
        break
else:
    print("completed")
print("done")
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
done
```

The `else` block on a `for` loop runs **only if the loop completed without hitting a `break`**. Since `i == 3` triggers `break`, the else block is skipped. `"done"` always prints because it is outside the loop.

**How to think through this:**
1. Read `for...else` as: "run else only if the loop was NOT broken out of early."
2. i reaches 3, break fires → else is skipped.
3. Execution continues to `print("done")` which is unconditional.

**Key takeaway:** `for...else` is perfect for "search and report if not found" patterns — `else` means "exhausted without breaking."

</details>

> 📖 **Theory:** [Loop Else](./02_control_flow/theory.md#1--while-loops-reading-chunks-classic-pattern)

---

### Q8 · [Normal] · `list-comprehension`

> **Rewrite this using a list comprehension:**

```python
result = []
for x in range(10):
    if x % 2 == 0:
        result.append(x ** 2)
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
result = [x ** 2 for x in range(10) if x % 2 == 0]
# [0, 4, 16, 36, 64]
```

Structure: `[expression for item in iterable if condition]`

**How to think through this:**
1. Identify the expression applied to each element: `x ** 2`.
2. Identify the iterable: `range(10)`.
3. Identify the filter condition: `if x % 2 == 0`.
4. Assemble: `[expr for item in iterable if condition]`.

**Key takeaway:** List comprehensions are faster than equivalent for-loops (single bytecode instruction) and more readable when kept to one condition.

</details>

> 📖 **Theory:** [List Comprehension](./02_control_flow/theory.md#12-comprehensions-controlled-expression-loops)

---

### Q9 · [Thinking] · `dict-comprehension`

> **What does this produce and what is a real use case for dict comprehensions?**

```python
words = ["apple", "bat", "cherry"]
result = {w: len(w) for w in words}
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
{"apple": 5, "bat": 3, "cherry": 6}
```

Real use cases:
- Build a word-frequency map: `{word: text.count(word) for word in vocab}`
- Invert a dict: `{v: k for k, v in original.items()}`
- Filter a dict: `{k: v for k, v in d.items() if v > 0}`

**How to think through this:**
1. Structure is `{key_expr: value_expr for item in iterable}`.
2. Here key = the word itself, value = its length.
3. Iterating `words` produces each string, which becomes both key and input to `len()`.

**Key takeaway:** Dict comprehensions are the go-to for transforming or filtering existing mappings in one readable line.

</details>

> 📖 **Theory:** [Dict Comprehension](./02_control_flow/theory.md#dict-comprehension--same-rule)

---

### Q10 · [Critical] · `mutable-default-argument`

> **What is wrong with this function? What does it print on the second call?**

```python
def add_item(item, lst=[]):
    lst.append(item)
    return lst

print(add_item(1))
print(add_item(2))
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
[1]
[1, 2]
```

The default value `[]` is evaluated **once** when the function is defined, not each time it is called. The same list object is reused across all calls that use the default. So after the first call, the default list contains `[1]`, and the second call appends to it.

**How to think through this:**
1. Default argument objects are created at function definition time and stored on the function object (`add_item.__defaults__`).
2. Each call that omits `lst` gets the same list — not a fresh one.
3. `.append()` mutates it in place, accumulating across calls.

**Key takeaway:** Never use mutable objects (list, dict, set) as default arguments. Use `None` and create a new object inside the function body.

</details>

> 📖 **Theory:** [Mutable Default Argument](./04_functions/theory.md#type-3-edge-case--the-mutable-default-argument-trap)

---

### Q11 · [Normal] · `args-kwargs`

> **What is the difference between `*args` and `**kwargs`? Write a function that accepts any number of positional and keyword arguments and prints them.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- `*args` collects extra positional arguments into a **tuple**.
- `**kwargs` collects extra keyword arguments into a **dict**.

```python
def show_all(*args, **kwargs):
    print("Positional:", args)
    print("Keyword:", kwargs)

show_all(1, 2, 3, name="Alice", age=30)
# Positional: (1, 2, 3)
# Keyword: {'name': 'Alice', 'age': 30}
```

**How to think through this:**
1. `*` in a parameter means "collect remaining positional args into a tuple."
2. `**` means "collect remaining keyword args into a dict."
3. Order in signature: normal params → `*args` → keyword-only params → `**kwargs`.

**Key takeaway:** `*args` = variable positional (tuple), `**kwargs` = variable keyword (dict).

</details>

> 📖 **Theory:** [*args & **kwargs](./04_functions/theory.md#type-5--kwargs-variable-keyword-arguments)

---

### Q12 · [Thinking] · `return-none`

> **What does a function return if it has no return statement? What does this print?**

```python
def greet(name):
    message = f"Hello {name}"

result = greet("Alice")
print(result)
print(type(result))
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
None
<class 'NoneType'>
```

Every Python function returns something. If there is no `return` statement (or a bare `return`), Python implicitly returns `None`.

**How to think through this:**
1. `greet()` builds the message string but never returns it — it just falls off the end.
2. Python inserts an implicit `return None` at the end of any function without an explicit return.
3. `result` is bound to `None`, so `print(result)` prints `None` and `type(None)` is `NoneType`.

**Key takeaway:** A function that does not explicitly return a value always returns `None` — forgetting to `return` is a common bug when you expect a value back.

</details>

> 📖 **Theory:** [Return None](./04_functions/theory.md#scenario-2-return-nothing-implicit-none)

---

### Q13 · [Normal] · `class-basics`

> **What is the difference between an instance variable and a class variable? Write a short class example showing both.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- **Class variable** — defined in the class body, shared by all instances.
- **Instance variable** — defined with `self.` inside a method, unique to each instance.

```python
class Dog:
    species = "Canis lupus"      # class variable — shared

    def __init__(self, name):
        self.name = name         # instance variable — unique per dog

d1 = Dog("Rex")
d2 = Dog("Bella")
print(d1.species)   # "Canis lupus"
print(d2.species)   # "Canis lupus"
print(d1.name)      # "Rex"
print(d2.name)      # "Bella"
```

**How to think through this:**
1. Class variables live on the class object itself — one copy, all instances read from it.
2. Instance variables live on the instance's `__dict__` — one copy per instance.
3. Assigning `self.species = "X"` on an instance creates a new instance attribute shadowing the class variable — it does not change the class variable.

**Key takeaway:** Class variables are shared state; instance variables are per-object state.

</details>

> 📖 **Theory:** [Class Basics](./05_oops/theory_part1.md)

---

### Q14 · [Logical] · `class-variable-trap`

> **What does this print and why is it surprising?**

```python
class Counter:
    count = 0
    def increment(self):
        self.count += 1

a = Counter()
b = Counter()
a.increment()
print(a.count)
print(b.count)
print(Counter.count)
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
1
0
0
```

`self.count += 1` is equivalent to `self.count = self.count + 1`. The right side reads `Counter.count` (0) through the instance. The assignment then creates a **new instance variable** `a.count = 1`, shadowing the class variable. The class variable `Counter.count` remains 0. `b.count` also still reads from the class variable (0).

**How to think through this:**
1. Python attribute lookup: check instance `__dict__` first, then class.
2. On read: `self.count` finds `Counter.count = 0` (no instance attribute yet).
3. On write: `self.count = 1` creates an instance attribute on `a` — does not touch the class variable.

**Key takeaway:** Augmented assignment (`+=`) on an instance creates an instance variable shadowing the class variable — it does NOT modify the class variable.

</details>

> 📖 **Theory:** [Class Variable Trap](./05_oops/theory_part2.md)

---

### Q15 · [Interview] · `oop-basics`

> **Explain inheritance in Python. When should you use inheritance vs composition?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Inheritance** — a subclass inherits attributes and methods from a parent class. Use it for "is-a" relationships.

```python
class Animal:
    def breathe(self): return "breathing"

class Dog(Animal):
    def bark(self): return "woof"

d = Dog()
d.breathe()  # inherited
```

**Composition** — a class holds instances of other classes as attributes. Use it for "has-a" relationships.

```python
class Engine:
    def start(self): return "vroom"

class Car:
    def __init__(self):
        self.engine = Engine()  # Car HAS-AN Engine
```

**When to use each:**
- Inheritance: when the subclass genuinely IS a specialised version of the parent and you need to reuse/override behaviour.
- Composition: when you want to reuse functionality without tight coupling. Favoured in modern design ("composition over inheritance") because it is more flexible and avoids deep inheritance hierarchies.

**How to think through this:**
1. Ask: "Is a Dog an Animal?" → yes → inheritance makes sense.
2. Ask: "Is a Car an Engine?" → no → use composition.
3. Inheritance creates tight coupling; composition keeps classes independent and swappable.

**Key takeaway:** Prefer composition when in doubt — deep inheritance trees are hard to maintain.

</details>

> 📖 **Theory:** [OOP Basics](./05_oops/theory_part1.md)

---

### Q16 · [Normal] · `string-methods`

> **What do `strip()`, `split()`, `join()`, and `replace()` do? Give one practical use case for each.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- `strip()` — removes leading/trailing whitespace (or specified chars). Use case: cleaning user input from a form.
- `split(sep)` — splits a string into a list by separator. Use case: parsing a CSV line `"a,b,c".split(",")`.
- `join(iterable)` — joins an iterable of strings with a separator. Use case: building a comma-separated string `", ".join(["a","b","c"])`.
- `replace(old, new)` — replaces all occurrences of old with new. Use case: sanitising a filename `name.replace(" ", "_")`.

**How to think through this:**
1. `strip/lstrip/rstrip` are for whitespace trimming.
2. `split` goes string → list; `join` goes list → string. They are inverses.
3. `replace` is a simple find-and-replace — for complex patterns use `re.sub()`.

**Key takeaway:** `split` and `join` are inverses — memorise `separator.join(list)` not `list.join(separator)`.

</details>

> 📖 **Theory:** [String Methods](./03_data_types/theory.md#string-methods--the-toolbox)

---

### Q17 · [Logical] · `string-slicing`

> **What does each line print?**

```python
s = "Python"
print(s[1:4])
print(s[::-1])
print(s[::2])
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
yth
nohtyP
Pto
```

- `s[1:4]` → characters at indices 1, 2, 3 → `"yth"`.
- `s[::-1]` → all characters, step -1 (reversed) → `"nohtyP"`.
- `s[::2]` → every second character starting at 0 → indices 0, 2, 4 → `"Pto"`.

**How to think through this:**
1. Slice syntax: `[start:stop:step]`. Omitting start/stop defaults to beginning/end.
2. Step -1 means traverse backwards → reverses the string.
3. Step 2 skips every other character.

**Key takeaway:** `[::-1]` is the idiomatic Python way to reverse any sequence.

</details>

> 📖 **Theory:** [String Slicing](./03_data_types/theory.md#strings-are-sequences--indexing--slicing)

---

### Q18 · [Normal] · `f-strings`

> **What are f-strings and what are two advantages over `.format()` or `%` formatting? Show an example with a calculation inside the f-string.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
f-strings (formatted string literals, Python 3.6+) embed expressions directly in string literals using `{}`.

```python
name = "Alice"
score = 87
print(f"{name} scored {score * 1.1:.1f} after bonus")
# "Alice scored 95.7 after bonus"
```

Advantages over `.format()` and `%`:
1. **Readable** — the variable/expression sits right where it will appear in the output.
2. **Faster** — f-strings are evaluated at parse time and are the fastest string formatting method.
3. **Powerful** — support format specs (`.2f`, `>10`, etc.) and arbitrary expressions including function calls.

**How to think through this:**
1. `f"..."` evaluates `{expr}` at runtime, converting to string.
2. `{score * 1.1:.1f}` → first evaluates `score * 1.1`, then formats as float with 1 decimal.

**Key takeaway:** Use f-strings for all new code — they are the clearest and fastest option.

</details>

> 📖 **Theory:** [F-Strings](./03_data_types/theory.md#f-strings--the-best-way-to-embed-values-in-text-python-36)

---

### Q19 · [Normal] · `try-except-finally`

> **What is the execution order of try/except/else/finally? In which block does `else` run?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Full structure:
```python
try:
    # 1. Run this
except SomeError:
    # 2. Run ONLY if try raised SomeError
else:
    # 3. Run ONLY if try completed WITHOUT exception
finally:
    # 4. ALWAYS runs — exception or not
```

Order:
- No exception: `try` → `else` → `finally`
- Exception caught: `try` → `except` → `finally`
- Exception not caught: `try` → `finally` → exception propagates

The `else` block runs when the `try` block completes successfully without any exception. It is useful for code that should only run on success but should not be inside `try` (to avoid accidentally catching errors from that code).

**How to think through this:**
1. `finally` is the guarantee — it runs no matter what.
2. `else` is the "clean path" — only runs if try succeeded.
3. Think: try=attempt, except=handle error, else=on success, finally=cleanup.

**Key takeaway:** `finally` = always runs (use for cleanup); `else` = runs only on success (use to separate success logic from error handling).

</details>

> 📖 **Theory:** [Try/Except/Finally](./06_exceptions_error_handling/theory.md)

---

### Q20 · [Logical] · `exception-flow`

> **What does this print?**

```python
def risky():
    try:
        return 1
    finally:
        return 2

print(risky())
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
2
```

Even though `try` block has `return 1`, the `finally` block executes before the function actually returns. The `return 2` in `finally` overrides the pending `return 1`.

**How to think through this:**
1. `return 1` is encountered — Python prepares to return 1, but first must run `finally`.
2. `finally` runs and hits `return 2` — this becomes the actual return value, discarding the pending 1.
3. This is a known gotcha: a `return` or `raise` inside `finally` silently overrides the original.

**Key takeaway:** Never put a `return` statement inside a `finally` block — it silently swallows exceptions and overrides return values.

</details>

> 📖 **Theory:** [Exception Flow](./06_exceptions_error_handling/theory.md)

---

### Q21 · [Critical] · `exception-types`

> **What is the difference between `except Exception` and `except BaseException`? When would catching `BaseException` be dangerous?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- `Exception` is the base class for all "normal" errors (ValueError, KeyError, IOError, etc.).
- `BaseException` is the root of the entire hierarchy and also catches `SystemExit`, `KeyboardInterrupt`, and `GeneratorExit`.

Catching `BaseException` is dangerous because:
- `KeyboardInterrupt` (Ctrl+C) will be swallowed — the user cannot stop your program.
- `SystemExit` (from `sys.exit()`) will be caught — the program won't exit when it should.

```python
# BAD — user can't Ctrl+C out of this
try:
    run_forever()
except BaseException:
    pass
```

**How to think through this:**
1. Most of the time you want `except Exception` — catches real errors, lets signals through.
2. `except BaseException` is almost never correct unless you are writing a framework-level cleanup handler that needs to catch everything and then re-raises.

**Key takeaway:** Use `except Exception`; avoid `except BaseException` unless you immediately re-raise with `raise`.

</details>

> 📖 **Theory:** [Exception Types](./06_exceptions_error_handling/theory.md)

---

### Q22 · [Normal] · `type-conversion`

> **What is the difference between implicit and explicit type conversion in Python? Give an example where implicit conversion does NOT happen (unlike in some other languages).**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- **Explicit** (casting) — you call a function to convert: `int("42")`, `str(3.14)`, `list((1,2,3))`.
- **Implicit** — Python automatically converts without you asking.

Python is strongly typed — implicit conversions are very limited. For example:
```python
print(1 + "1")  # TypeError — no implicit int→str or str→int
```

In JavaScript this gives `"11"`. Python refuses. You must be explicit:
```python
print(str(1) + "1")  # "11"
print(1 + int("1"))  # 2
```

Python does allow a few implicit conversions: `int + float → float`, `bool` treated as 0/1 in arithmetic.

**How to think through this:**
1. Python does not silently convert between unrelated types.
2. When in doubt, be explicit — `int()`, `str()`, `float()`, `list()`, `tuple()`.

**Key takeaway:** Python is strongly typed — you must explicitly convert between types; it will not do it silently.

</details>

> 📖 **Theory:** [Type Conversion](./01_python_fundamentals/theory.md#is-vs--interview-favorite)

---

### Q23 · [Thinking] · `none-checks`

> **What is the difference between `if x == None` and `if x is None`? Which should you always use and why?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Always use `if x is None`.

- `x is None` checks object identity — is `x` literally the `None` singleton?
- `x == None` calls `__eq__` on `x`, which a custom class can override to return `True` for non-None values.

```python
class Tricky:
    def __eq__(self, other):
        return True  # compares equal to everything, including None

t = Tricky()
print(t == None)   # True  ← misleading
print(t is None)   # False ← correct
```

Since `None` is a singleton (only one `None` object exists in Python), identity check is both correct and faster.

**How to think through this:**
1. `is` = same object in memory. There is exactly one `None` object.
2. `==` = calls `__eq__`. Custom objects can lie.
3. PEP 8 explicitly says: use `is` / `is not` when comparing to None.

**Key takeaway:** Always `if x is None:` — it is faster, safer, and PEP 8 mandated.

</details>

> 📖 **Theory:** [None Checks](./01_python_fundamentals/theory.md#1-what-is-python)

---

### Q24 · [Normal] · `truthiness`

> **Which of the following are falsy in Python: `0`, `""`, `[]`, `{}`, `None`, `0.0`, `False`, `"0"`, `[0]`?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Falsy: `0`, `""`, `[]`, `{}`, `None`, `0.0`, `False`

Truthy: `"0"` (non-empty string), `[0]` (non-empty list)

Python's falsy values: `None`, `False`, zero of any numeric type (`0`, `0.0`, `0j`), empty sequences (`""`, `[]`, `()`), empty mappings (`{}`), empty sets (`set()`), and objects whose `__bool__` returns `False` or `__len__` returns 0.

**How to think through this:**
1. Rule of thumb: empty = falsy, zero = falsy, None = falsy.
2. Any non-empty container is truthy regardless of what it contains — `[0]` has one element so it is truthy.
3. `"0"` is a non-empty string — its content does not matter, only its length.

**Key takeaway:** Falsy = empty, zero, None, or False. Non-empty containers and non-zero numbers are always truthy.

</details>

> 📖 **Theory:** [Truthiness](./01_python_fundamentals/theory.md)

---

### Q25 · [Thinking] · `unpacking`

> **What does this print? What is the `*` doing in the unpacking?**

```python
first, *middle, last = [1, 2, 3, 4, 5]
print(first, middle, last)
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
1 [2, 3, 4] 5
```

`*middle` uses "extended unpacking" (Python 3+). It acts as a catch-all that collects all elements not consumed by the other names into a list. `first` gets 1, `last` gets 5, and `middle` gets everything in between as a list.

**How to think through this:**
1. Non-starred names on the left consume one element each from the ends.
2. The starred name gets everything remaining as a list.
3. You can use `*_` to discard the middle: `first, *_, last = [1,2,3,4,5]`.

**Key takeaway:** `*name` in unpacking is a greedy catch-all — it collects all remaining elements into a list.

</details>

> 📖 **Theory:** [Unpacking](./01_python_fundamentals/theory.md)

---

## Tier 2 — Intermediate · Q26–Q50

> Focus: Closures, decorators, generators, context managers, OOP advanced, copy, exceptions

---

### Q26 · [Thinking] · `closures`

> **What is a closure? What does this print and why does the inner function "remember" x?**

```python
def outer(x):
    def inner(y):
        return x + y
    return inner

add5 = outer(5)
print(add5(3))
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
8
```

A closure is a function that captures and remembers variables from its enclosing scope even after that scope has finished executing. `inner` closes over `x` from `outer`. When `outer(5)` returns `inner`, the value `x=5` is kept alive in a "cell object" attached to the inner function. Calling `add5(3)` computes `5 + 3 = 8`.

**How to think through this:**
1. Normally, when `outer` returns, its local variables are gone. But `inner` holds a reference to `x` in a closure cell.
2. The closure cell keeps `x` alive as long as `inner` exists.
3. `add5.__closure__[0].cell_contents` would show `5`.

**Key takeaway:** A closure = a function + the variables it captured from its enclosing scope. Used heavily in decorators and factory functions.

</details>

> 📖 **Theory:** [Closures](./04_functions/theory.md#but-n5-still-lives-in-a-cell-on-the-heap-referenced-by-add5__closure__)

---

### Q27 · [Critical] · `closure-loop-trap`

> **What does this print? Why is it surprising and how do you fix it?**

```python
funcs = []
for i in range(3):
    funcs.append(lambda: i)
print([f() for f in funcs])
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
[2, 2, 2]
```

All three lambdas close over the **same variable `i`**, not its value at the time of creation. By the time the lambdas are called, the loop has finished and `i` is `2`. All three functions return `2`.

Fix — capture the current value as a default argument:
```python
funcs = [lambda i=i: i for i in range(3)]
print([f() for f in funcs])  # [0, 1, 2]
```

Default arguments are evaluated at definition time, so `i=i` captures the current value of `i` each iteration.

**How to think through this:**
1. Closures capture the variable (a reference), not the value at that moment.
2. The loop variable `i` keeps changing. All lambdas share the same `i`.
3. Fix: convert the variable reference into a value by binding it to a default parameter.

**Key takeaway:** Closures capture variables by reference — use a default argument `(i=i)` to capture the value at the time of creation.

</details>

> 📖 **Theory:** [Closure Loop Trap](./04_functions/theory.md#the-late-binding-closure-trap)

---

### Q28 · [Normal] · `nonlocal`

> **What does `nonlocal` do? When do you need it inside a nested function?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
`nonlocal` declares that a variable inside a nested function refers to the nearest enclosing scope (not global, not local). Without it, assigning to a name inside a nested function creates a new local variable.

```python
def counter():
    count = 0
    def increment():
        nonlocal count   # refers to outer count
        count += 1
        return count
    return increment

c = counter()
print(c())  # 1
print(c())  # 2
```

Without `nonlocal count`, `count += 1` would raise `UnboundLocalError` because Python would treat `count` as a new local variable in `increment`.

**How to think through this:**
1. Reading a variable from an outer scope works without `nonlocal`.
2. Assigning (or augmenting `+=`) creates a new local unless you declare `nonlocal`.
3. `nonlocal` is to nested scopes what `global` is to module scope.

**Key takeaway:** Use `nonlocal` when a nested function needs to modify (not just read) a variable from the enclosing scope.

</details>

> 📖 **Theory:** [nonlocal](./04_functions/theory.md#the-nonlocal-keyword)

---

### Q29 · [Normal] · `decorators-basics`

> **What is a decorator? Write a simple decorator that prints "before" and "after" around any function call.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A decorator is a function that takes another function as input, wraps it with extra behaviour, and returns the new function. `@decorator` is syntactic sugar for `func = decorator(func)`.

```python
import functools

def log_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("before")
        result = func(*args, **kwargs)
        print("after")
        return result
    return wrapper

@log_calls
def greet(name):
    print(f"Hello {name}")

greet("Alice")
# before
# Hello Alice
# after
```

**How to think through this:**
1. `@log_calls` above `greet` is equivalent to `greet = log_calls(greet)` after the function definition.
2. `wrapper` replaces `greet` — but `@functools.wraps` preserves the original name/docstring.
3. `wrapper` calls the original function inside and adds behaviour around it.

**Key takeaway:** A decorator wraps a function — always use `@functools.wraps(func)` to preserve metadata.

</details>

> 📖 **Theory:** [Decorator Basics](./10_decorators/theory.md#chapter-9-built-in-decorators--property-classmethod-staticmethod)

---

### Q30 · [Thinking] · `functools-wraps`

> **Why should you use `@functools.wraps(func)` inside a decorator? What breaks if you don't?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Without `@functools.wraps(func)`, the wrapper function replaces the original and loses its identity:

```python
def my_dec(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_dec
def greet():
    """Says hello."""
    pass

print(greet.__name__)   # "wrapper"  ← wrong
print(greet.__doc__)    # None       ← lost
```

With `@functools.wraps(func)`, `wrapper.__name__`, `wrapper.__doc__`, `wrapper.__module__`, and `wrapper.__wrapped__` are all copied from the original.

This matters for: debugging stack traces, documentation tools, `help()`, testing frameworks that inspect function names, and introspection.

**How to think through this:**
1. `wrapper` is a new function — by default it has its own name and no docstring.
2. `functools.wraps` copies the dunder attributes from `func` onto `wrapper`.
3. It also sets `wrapper.__wrapped__ = func` so you can unwrap programmatically.

**Key takeaway:** Always add `@functools.wraps(func)` inside every decorator wrapper — it is a two-character fix that prevents confusing bugs.

</details>

> 📖 **Theory:** [functools.wraps](./10_decorators/theory.md#chapter-5-functoolswraps--preserving-identity)

---

### Q31 · [Logical] · `stacked-decorators`

> **In what order are stacked decorators applied? What does this print?**

```python
def a(f):
    print("A wrapping")
    return f

def b(f):
    print("B wrapping")
    return f

@a
@b
def hello():
    pass
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
B wrapping
A wrapping
```

Stacked decorators are applied **bottom-up**. `@b` is applied first (innermost), then `@a` wraps the result. This is equivalent to: `hello = a(b(hello))`. So `b` runs first, then `a`.

**How to think through this:**
1. Decorators are applied from the decorator closest to the function outward.
2. `@a` over `@b` → `a(b(hello))` → b wraps first, then a wraps b's result.
3. When the module loads, both wrapping print statements execute at definition time.

**Key takeaway:** Stacked decorators apply bottom-up (innermost first). Think of them as nested function calls reading inside-out.

</details>

> 📖 **Theory:** [Stacked Decorators](./10_decorators/theory.md#chapter-10-stacking-decorators--order-and-interaction)

---

### Q32 · [Design] · `parametrized-decorator`

> **How do you write a decorator that accepts arguments (e.g. `@retry(times=3)`)? Sketch the structure.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
You need three levels of nesting — a factory function that returns the decorator:

```python
import functools, time

def retry(times=3, delay=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == times - 1:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(times=3, delay=2)
def call_api():
    ...
```

`@retry(times=3)` calls `retry(times=3)` which returns `decorator`, which then wraps `call_api`.

**How to think through this:**
1. `@retry(times=3)` is NOT `@retry` — the parentheses mean `retry(times=3)` is called first.
2. The call must return a normal decorator (a function that takes `func`).
3. So: outer function accepts decorator args → returns decorator → decorator accepts func → returns wrapper.

**Key takeaway:** Parametrised decorators need 3 levels: `factory(args)` → `decorator(func)` → `wrapper(*args, **kwargs)`.

</details>

> 📖 **Theory:** [Parametrized Decorators](./10_decorators/theory.md#chapter-6-decorators-with-arguments--decorator-factories)

---

### Q33 · [Normal] · `generators-basics`

> **What is the difference between a list comprehension and a generator expression? When would you choose a generator?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
lst = [x**2 for x in range(1000000)]   # list — all values in memory now
gen = (x**2 for x in range(1000000))   # generator — lazy, one value at a time
```

Differences:
- List comprehension: eager — builds the entire list in memory immediately.
- Generator expression: lazy — produces values one at a time on demand, using O(1) memory.

Choose a generator when:
1. The dataset is large (or infinite) and you don't need all values at once.
2. You only iterate once (generators are exhausted after one pass).
3. You are chaining operations in a pipeline (generators compose efficiently).

**How to think through this:**
1. `[]` vs `()` is the only syntax difference.
2. If you need random access or multiple passes → list. If you stream once → generator.
3. Generators are especially valuable in data pipelines processing millions of rows.

**Key takeaway:** Generators are memory-efficient lazy iterators — use them when you process large data sequentially and don't need to store all results.

</details>

> 📖 **Theory:** [Generator Basics](./11_generators_iterators/theory.md#chapter-3-generator-functions--yield)

---

### Q34 · [Thinking] · `yield`

> **What does `yield` do? Trace through this and explain what happens step by step:**

```python
def counter(n):
    i = 0
    while i < n:
        yield i
        i += 1

gen = counter(3)
print(next(gen))
print(next(gen))
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
0
1
```

Step by step:
1. `counter(3)` creates a generator object — the function body does NOT run yet.
2. `next(gen)` resumes the function from the start. It runs until `yield i` (i=0), pauses there, and returns 0.
3. The function is suspended mid-execution with all local state preserved.
4. `next(gen)` resumes from after the `yield`. `i += 1` makes i=1, loops back, hits `yield i` (i=1), pauses and returns 1.

**How to think through this:**
1. `yield` is a pause point — the function suspends and hands a value back to the caller.
2. Local variables (like `i`) are preserved in the generator's frame between `next()` calls.
3. Unlike `return`, `yield` does not end the function — it resumes from the same spot next time.

**Key takeaway:** `yield` turns a function into a generator — it suspends execution, preserves state, and resumes where it left off on the next `next()` call.

</details>

> 📖 **Theory:** [yield](./11_generators_iterators/theory.md#chapter-3-generator-functions--yield)

---

### Q35 · [Critical] · `generator-exhaustion`

> **What happens when you call `next()` on a generator that has finished? How do you iterate a generator safely?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
When a generator is exhausted, calling `next()` raises `StopIteration`. If you call `next()` directly you must handle this:

```python
gen = (x for x in range(2))
print(next(gen))  # 0
print(next(gen))  # 1
print(next(gen))  # raises StopIteration
```

Safe ways to iterate:
1. **`for` loop** — handles `StopIteration` automatically, cleanest.
2. **`next(gen, default)`** — returns `default` instead of raising.
3. **`list(gen)`** — consumes everything into a list.

Generators are also **single-pass** — once exhausted, they cannot be reset. Iterating an exhausted generator with a `for` loop simply produces nothing.

**How to think through this:**
1. `for` loops call `next()` internally and catch `StopIteration` to stop.
2. Direct `next()` calls need a default or a try/except.
3. Always remember: generators can only be iterated once.

**Key takeaway:** Use `for` loops to iterate generators safely — or `next(gen, None)` if you want one value with a fallback.

</details>

> 📖 **Theory:** [Generator Exhaustion](./11_generators_iterators/theory.md#generator-exhausted)

---

### Q36 · [Normal] · `context-managers`

> **What does the `with` statement do? What two methods must a class implement to be used as a context manager?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The `with` statement ensures setup and teardown happen reliably — even if an exception is raised inside the block.

```python
with open("file.txt") as f:
    data = f.read()
# file is always closed here, even if read() raised
```

A class must implement:
1. `__enter__(self)` — called on entry, its return value is bound to the `as` variable.
2. `__exit__(self, exc_type, exc_val, exc_tb)` — called on exit (normal or exception). Return `True` to suppress the exception, `False`/`None` to let it propagate.

```python
class Timer:
    def __enter__(self):
        import time; self.start = time.time(); return self
    def __exit__(self, *args):
        print(f"Elapsed: {time.time() - self.start:.3f}s")
```

**How to think through this:**
1. `with X as y:` → calls `X.__enter__()`, binds result to `y`, runs block, then calls `X.__exit__()`.
2. `__exit__` receives exception info if one occurred — return True to suppress it.

**Key takeaway:** Context managers = guaranteed cleanup. Implement `__enter__` and `__exit__` for any resource that needs to be acquired and released.

</details>

> 📖 **Theory:** [Context Managers](./12_context_managers/theory.md#chapter-6-multiple-context-managers-in-one-with)

---

### Q37 · [Thinking] · `context-manager-exception`

> **If an exception is raised inside a `with` block, does `__exit__` still run? How can `__exit__` suppress the exception?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Yes — `__exit__` **always** runs, even if an exception occurred. This is the entire point of context managers: guaranteed cleanup.

If an exception occurred, `__exit__` receives:
- `exc_type` — the exception class
- `exc_val` — the exception instance
- `exc_tb` — the traceback

To suppress the exception, return a truthy value from `__exit__`:

```python
class Suppress:
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is ValueError:
            return True   # suppress ValueError, let others propagate
        return False      # re-raise all other exceptions
```

Returning `False` or `None` lets the exception propagate normally.

**How to think through this:**
1. `__exit__` is called regardless — exception or not. If no exception, all three args are `None`.
2. The return value of `__exit__` controls whether the exception is swallowed.
3. `contextlib.suppress(ValueError)` is the built-in way to do this cleanly.

**Key takeaway:** `__exit__` always runs. Return `True` to suppress an exception, `False`/`None` to let it propagate.

</details>

> 📖 **Theory:** [Exception Handling in CM](./12_context_managers/theory.md#chapter-3-suppressing-exceptions-with-__exit__)

---

### Q38 · [Normal] · `contextlib`

> **How do you turn a generator function into a context manager using `contextlib.contextmanager`? Write a simple example.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
from contextlib import contextmanager

@contextmanager
def managed_resource(name):
    print(f"Acquiring {name}")   # setup (like __enter__)
    try:
        yield name               # value bound to "as" variable
    finally:
        print(f"Releasing {name}")  # teardown (like __exit__)

with managed_resource("DB connection") as conn:
    print(f"Using {conn}")

# Acquiring DB connection
# Using DB connection
# Releasing DB connection
```

The `yield` splits setup (above) from teardown (below). The `try/finally` ensures cleanup even on exception.

**How to think through this:**
1. Everything before `yield` = `__enter__`.
2. The yielded value = what `as` receives.
3. Everything after `yield` (in `finally`) = `__exit__`.

**Key takeaway:** `@contextmanager` lets you write context managers as simple generator functions — much less boilerplate than a full class.

</details>

> 📖 **Theory:** [contextlib](./12_context_managers/theory.md#chapter-4-contextmanager--generator-based-context-managers)

---

### Q39 · [Normal] · `imports`

> **What is the difference between `import module`, `from module import name`, and `from module import *`? What are the risks of `import *`?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- `import module` — imports the module object. Access names via `module.name`. Namespace stays clean.
- `from module import name` — imports a specific name directly into the current namespace.
- `from module import *` — imports all public names (or all names in `__all__` if defined).

Risks of `import *`:
1. **Namespace pollution** — you don't know what names you just imported; they can shadow existing variables silently.
2. **Hard to trace** — readers can't tell which module `some_function` came from.
3. **Breaks tools** — IDEs, linters, and `grep` can't find where names come from.

```python
from os.path import *   # imported exists, join, dirname, ... who knows what else?
join = "my string"       # accidentally shadowed by the import above
```

**How to think through this:**
1. `import module` is explicit and safe — always know the source.
2. `from module import name` is fine for frequently used names.
3. `import *` is acceptable only in `__init__.py` re-exports and interactive sessions.

**Key takeaway:** Never use `import *` in production code — it pollutes the namespace and makes code impossible to reason about.

</details>

> 📖 **Theory:** [Imports](./07_modules_packages/theory.md#chapter-4--packages-organizing-modules-into-a-system)

---

### Q40 · [Critical] · `circular-imports`

> **What causes a circular import error in Python? How do you fix it?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A circular import occurs when module A imports from module B, and module B imports from module A. When Python starts importing A, it begins executing A's top-level code. When A hits `import B`, Python starts executing B. B then hits `import A` — but A is only partially initialised, so names defined later in A are not yet available. This causes an `ImportError` or `AttributeError`.

**Fixes:**
1. **Restructure** — extract shared code to a third module C that both A and B can import without creating a cycle.
2. **Lazy import** — move the import inside a function or method (deferred until it is actually called):
```python
def use_b():
    from module_b import something  # imported only when function runs
    return something()
```
3. **Import the module, not the name** — `import module_b` instead of `from module_b import name` (works if B is partially loaded).

**How to think through this:**
1. Python caches partially-loaded modules in `sys.modules` — circular imports find a half-built module there.
2. The cleanest fix is architecture (no circular dependencies). Lazy imports are the quick fix.

**Key takeaway:** Circular imports signal a design problem — restructure dependencies or use lazy imports as a last resort.

</details>

> 📖 **Theory:** [Circular Imports](./07_modules_packages/theory.md#chapter-8--circular-imports-the-design-warning)

---

### Q41 · [Normal] · `__all__`

> **What does `__all__` do in a module? If you don't define it, what gets exported with `from module import *`?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
`__all__` is a list of strings that defines the public API of a module — specifically, what gets exported when someone does `from module import *`.

```python
# mymodule.py
__all__ = ["public_func"]

def public_func(): pass
def _private_func(): pass    # won't be exported
def helper(): pass           # won't be exported (not in __all__)
```

If `__all__` is **not** defined, `from module import *` exports all names that do **not** start with an underscore.

**How to think through this:**
1. `__all__` is the explicit whitelist for `import *`.
2. Without it, the implicit rule is: export anything not starting with `_`.
3. Best practice: always define `__all__` in reusable modules so the public API is explicit.

**Key takeaway:** Define `__all__` to explicitly control your module's public API — it also documents intent.

</details>

> 📖 **Theory:** [__all__](./07_modules_packages/theory.md#or-use-the-packages-public-api-if-__init__py-exports-it)

---

### Q42 · [Normal] · `custom-exceptions`

> **How do you create a custom exception class? Why should custom exceptions inherit from `Exception` and not `BaseException`?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
class PaymentError(Exception):
    """Raised when a payment fails."""
    def __init__(self, message, amount=None):
        super().__init__(message)
        self.amount = amount

class InsufficientFundsError(PaymentError):
    """Raised when balance is too low."""
    pass

try:
    raise InsufficientFundsError("Not enough funds", amount=100)
except PaymentError as e:
    print(f"Payment failed: {e}, amount={e.amount}")
```

Inherit from `Exception` (not `BaseException`) because:
- `except Exception` (used by virtually all catch-all handlers) will catch your exception.
- `except BaseException` would also catch it, but inheriting from `BaseException` directly means your exception looks like a system-level signal (KeyboardInterrupt, SystemExit), which is misleading.

**How to think through this:**
1. Create a base for your domain (e.g. `PaymentError`), then subclass for specific cases.
2. Add attributes for extra context — not just a message.
3. Always call `super().__init__(message)` so the exception message works correctly.

**Key takeaway:** Custom exceptions form a hierarchy — base class for the domain, subclasses for specific cases. Always inherit from `Exception`.

</details>

> 📖 **Theory:** [Custom Exceptions](./06_exceptions_error_handling/theory.md)

---

### Q43 · [Thinking] · `exception-chaining`

> **What is the difference between `raise NewError() from original_error` and just `raise NewError()`? When does chaining help?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- `raise NewError() from original_error` — explicit chaining. Sets `NewError.__cause__` to `original_error`. The traceback shows both exceptions with "The above exception was the direct cause of..."
- `raise NewError()` inside an `except` block — implicit chaining. Python automatically sets `__context__`. The traceback shows "During handling of the above exception, another exception occurred..."
- `raise NewError() from None` — suppresses the context entirely. Only the new exception is shown.

```python
try:
    int("abc")
except ValueError as e:
    raise RuntimeError("Config parse failed") from e
```

Chaining helps because:
1. It preserves the original error for debugging — you see the root cause and the high-level error.
2. Catching code can inspect `exc.__cause__` to handle the original error type.

**How to think through this:**
1. "From" = "this new error was caused by the original." Use when you are intentionally wrapping a lower-level error.
2. `from None` = "I handled the original, just show my error." Use when the original is an implementation detail.

**Key takeaway:** Use `raise NewError() from original` when translating low-level exceptions to domain exceptions — it preserves the full debug chain.

</details>

> 📖 **Theory:** [Exception Chaining](./06_exceptions_error_handling/theory.md)

---

### Q44 · [Critical] · `bare-except`

> **What is wrong with using `except:` (bare except) in production code? What does it catch that you usually don't want to catch?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
`except:` (bare except) catches **everything**, including:
- `KeyboardInterrupt` — the user can't Ctrl+C to stop the program.
- `SystemExit` — `sys.exit()` won't work.
- `GeneratorExit` — generator cleanup is broken.
- Memory errors, recursion errors — things you cannot recover from.

```python
# BAD
try:
    do_something()
except:
    pass  # silently eats Ctrl+C, sys.exit(), and everything else

# GOOD
try:
    do_something()
except Exception:
    logger.exception("Something went wrong")
```

Bare except also:
- Hides bugs (you never know what you caught).
- Makes debugging nearly impossible.
- Is flagged by every linter as an error.

**How to think through this:**
1. Always name the exception: `except ValueError`, `except Exception`, never bare.
2. If you truly want a catch-all, use `except Exception` — it still lets signals through.

**Key takeaway:** Never use bare `except:` — always name the exception type. Use `except Exception` as the widest acceptable catch-all.

</details>

> 📖 **Theory:** [Bare Except](./06_exceptions_error_handling/theory.md)

---

### Q45 · [Thinking] · `mro`

> **What is MRO (Method Resolution Order)? What order does Python use to resolve methods in multiple inheritance?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
MRO is the order in which Python searches classes for a method or attribute when inheritance is involved. Python uses the **C3 linearisation algorithm** (also called C3 MRO), which guarantees:
1. A subclass is always checked before its parents.
2. Parents are checked in the order listed in the class definition.
3. No class appears before any of its subclasses.

```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass

print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)
```

So `D → B → C → A → object`. This is the "diamond problem" — D inherits from both B and C which both inherit from A. C3 ensures A is only visited once.

**How to think through this:**
1. MRO = the search path for attribute/method lookup.
2. Use `ClassName.__mro__` or `ClassName.mro()` to inspect it.
3. The order is: self → left parent → right parent → common ancestor → object.

**Key takeaway:** Python's C3 MRO ensures consistent, predictable method resolution in multiple inheritance — left-to-right, depth-first, no repeats.

</details>

> 📖 **Theory:** [MRO](./05_oops/theory_part2.md)

---

### Q46 · [Normal] · `super`

> **What does `super()` do? Why is `super().__init__()` preferred over `ParentClass.__init__(self)`?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
`super()` returns a proxy object that delegates method calls to the next class in the MRO — not necessarily the direct parent.

Why prefer `super()`:
1. **MRO-aware** — in multiple inheritance, `super()` follows the full MRO chain, ensuring every `__init__` in the hierarchy is called exactly once in the right order.
2. **Maintainable** — if you rename the parent class, `super()` still works. Hardcoding `ParentClass.__init__` breaks when the class hierarchy changes.

```python
class A:
    def __init__(self):
        print("A init")

class B(A):
    def __init__(self):
        super().__init__()  # calls A.__init__ via MRO
        print("B init")
```

In cooperative multiple inheritance, each class in the MRO passes `__init__` up the chain via `super()`, ensuring all `__init__` methods run.

**How to think through this:**
1. `super()` in Python 3 automatically knows the current class and instance.
2. It finds the next class in the MRO after the current one.
3. Hardcoding the parent breaks cooperative multiple inheritance.

**Key takeaway:** Always use `super()` — it respects the MRO and makes your class safe to use in multiple inheritance.

</details>

> 📖 **Theory:** [super()](./05_oops/theory_part2.md)

---

### Q47 · [Logical] · `dunder-methods`

> **What does this print and which dunder method is Python calling?**

```python
class Box:
    def __init__(self, val):
        self.val = val
    def __repr__(self):
        return f"Box({self.val})"
    def __add__(self, other):
        return Box(self.val + other.val)

a = Box(3)
b = Box(4)
print(a + b)
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
Box(7)
```

`a + b` calls `a.__add__(b)`. This returns `Box(3 + 4)` = `Box(7)`. When `print()` calls `str()` on the result, Python falls back to `__repr__` (since no `__str__` is defined), producing `"Box(7)"`.

**How to think through this:**
1. `+` operator → Python calls `left.__add__(right)`.
2. `__add__` returns a new `Box(7)`.
3. `print()` converts the object to string → calls `__str__`, falls back to `__repr__` → `"Box(7)"`.

**Key takeaway:** Dunder methods let your objects behave like built-in types. `__repr__` is the fallback string representation — always define it for debugging.

</details>

> 📖 **Theory:** [Dunder Methods](./05_oops/theory_part2.md)

---

### Q48 · [Critical] · `shallow-vs-deep-copy`

> **What is the difference between assignment, shallow copy, and deep copy? What does this print?**

```python
import copy
original = [[1, 2], [3, 4]]
shallow = copy.copy(original)
shallow[0].append(99)
print(original)
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
[[1, 2, 99], [3, 4]]
```

- **Assignment** (`b = a`) — no copy; both names point to the same object.
- **Shallow copy** (`copy.copy()`, `list[:]`, `list.copy()`) — creates a new outer container, but inner objects are still shared references.
- **Deep copy** (`copy.deepcopy()`) — recursively copies all nested objects. Fully independent.

`shallow` is a new list, but `shallow[0]` points to the same inner list as `original[0]`. Appending 99 to `shallow[0]` mutates the shared inner list, so `original` reflects the change.

**How to think through this:**
1. Shallow = new box, same contents (same inner references).
2. Deep = new box AND new copies of all inner objects.
3. For nested mutable structures, always use `deepcopy` if you need full independence.

**Key takeaway:** Shallow copy creates a new container but shares inner objects — use `deepcopy` when you need a truly independent clone of a nested structure.

</details>

> 📖 **Theory:** [Shallow vs Deep Copy](./01.1_memory_management/theory.md)

---

### Q49 · [Thinking] · `mutable-default-fix`

> **What is the correct fix for the mutable default argument trap? Explain why the fix works.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
# BROKEN
def add_item(item, lst=[]):
    lst.append(item)
    return lst

# FIXED
def add_item(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

Why it works: `None` is immutable — it is safe as a default. The function creates a fresh `[]` on each call when no list is passed. The new list is a local variable, not shared across calls.

Alternative using `__defaults__` manipulation: don't. The `None` sentinel pattern is the accepted idiom.

**How to think through this:**
1. The bug: default values are evaluated once at definition time, so a mutable default is shared.
2. `None` is a safe sentinel — immutable, unambiguous "not provided."
3. Creating `lst = []` inside the function body runs on every call → fresh list every time.

**Key takeaway:** Use `None` as the default for any parameter that should default to a mutable value, then create the mutable inside the function.

</details>

> 📖 **Theory:** [Mutable Default Fix](./04_functions/theory.md#type-3-edge-case--the-mutable-default-argument-trap)

---

### Q50 · [Design] · `dataclass`

> **What problem does `@dataclass` solve? When would you use a dataclass instead of a regular class or a named tuple?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
`@dataclass` (Python 3.7+) auto-generates boilerplate methods based on annotated fields: `__init__`, `__repr__`, `__eq__`, and optionally `__hash__`, `__lt__`, etc.

```python
from dataclasses import dataclass, field

@dataclass
class Point:
    x: float
    y: float
    label: str = "origin"

p = Point(1.0, 2.0)
print(p)           # Point(x=1.0, y=2.0, label='origin')
print(p == Point(1.0, 2.0))  # True
```

Choose:
- **Dataclass** — when you want a mutable data-holding class with clean syntax, type hints, and auto-generated methods. Good for configs, DTOs, domain objects.
- **Regular class** — when you need custom `__init__` logic, inheritance complexity, or heavy methods.
- **Named tuple** — when you want immutability, tuple unpacking, and memory efficiency (immutable records).

**How to think through this:**
1. If you are writing `__init__` and `__repr__` by hand for a simple data holder → use `@dataclass`.
2. Need immutability → use `NamedTuple` or `@dataclass(frozen=True)`.
3. Need complex logic beyond data holding → regular class.

**Key takeaway:** `@dataclass` eliminates boilerplate for data-holding classes — use it whenever you'd otherwise write a manual `__init__` + `__repr__` + `__eq__`.

</details>

> 📖 **Theory:** [dataclass](./05_oops/14_dataclasses.md)

---

## Tier 3 — Advanced · Q51–Q75

> Focus: GIL, concurrency, memory, metaclasses, descriptors, type hints, design patterns, performance

---

### Q51 · [Interview] · `gil`

> **What is the Python GIL and why does it exist? What does it prevent and what does it not prevent?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The **Global Interpreter Lock (GIL)** is a mutex in CPython that ensures only one thread executes Python bytecode at a time — even on multi-core CPUs.

**Why it exists:** CPython's memory management (reference counting) is not thread-safe. Without the GIL, two threads could simultaneously modify an object's reference count, causing memory corruption or double-free errors.

**What it prevents:** True CPU parallelism in threads. Multiple threads running Python code cannot execute simultaneously on different cores.

**What it does NOT prevent:**
- I/O-bound parallelism — threads release the GIL during I/O operations (network, disk), so threading works well for I/O-bound tasks.
- Parallelism in C extensions — NumPy, pandas, and other C extensions can release the GIL during computation.
- Multiprocessing — each process has its own GIL and interpreter.

**How to think through this:**
1. GIL = one thread runs Python at a time. Others wait.
2. I/O releases the GIL → threads still help with I/O-bound work.
3. CPU-bound → use multiprocessing to bypass the GIL entirely.

**Key takeaway:** GIL prevents CPU parallelism in threads — use `multiprocessing` for CPU-bound tasks and `threading`/`asyncio` for I/O-bound tasks.

</details>

> 📖 **Theory:** [The GIL](./13_concurrency/theory.md#the-gil--global-interpreter-lock)

---

### Q52 · [Thinking] · `threading-vs-gil`

> **If the GIL prevents true parallelism, why is threading still useful in Python? Give a concrete example.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Threading is useful because threads release the GIL during **blocking I/O operations** — waiting for network responses, disk reads, database queries, etc. While one thread waits, another can run.

Concrete example — fetching 10 URLs:
```python
import threading, requests

def fetch(url):
    r = requests.get(url)   # releases GIL while waiting for response
    print(len(r.content))

threads = [threading.Thread(target=fetch, args=(url,)) for url in urls]
for t in threads: t.start()
for t in threads: t.join()
```

Without threading: 10 sequential requests take 10× the time. With threading: all 10 requests are in-flight simultaneously — total time ≈ slowest single request.

**How to think through this:**
1. "Waiting for network" is the bottleneck, not CPU.
2. During `requests.get()`, the thread blocks on a socket — the GIL is released.
3. Other threads run freely during that wait.

**Key takeaway:** Threading shines for I/O-bound tasks (HTTP, DB, files) where threads spend most of their time waiting, not computing.

</details>

> 📖 **Theory:** [Threading & GIL](./13_concurrency/theory.md#the-gil-protects-individual-bytecodes-but-not-compound-operations)

---

### Q53 · [Design] · `threading-vs-multiprocessing`

> **When do you choose threading over multiprocessing, and vice versa? What is the main tradeoff?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

| | Threading | Multiprocessing |
|---|---|---|
| Best for | I/O-bound tasks | CPU-bound tasks |
| GIL impact | Limited by GIL for CPU work | Each process has own GIL |
| Memory | Shared memory (fast, but risky) | Separate memory (safe, but copying needed) |
| Startup cost | Low | High (fork/spawn overhead) |
| Communication | Shared state (use locks) | Queues, Pipes, shared memory |

Choose threading when: making API calls, reading files, running database queries — anything that waits on I/O.
Choose multiprocessing when: crunching numbers, image processing, ML inference, anything CPU-intensive.

Also consider `asyncio` for I/O-bound work — single-threaded, no GIL concerns, handles thousands of concurrent connections efficiently.

**How to think through this:**
1. Ask: what is the bottleneck? CPU → multiprocessing. I/O → threading or asyncio.
2. Shared state is easy with threads but requires locks. Processes share nothing by default (safer).
3. `concurrent.futures` gives a clean unified API for both: `ThreadPoolExecutor` vs `ProcessPoolExecutor`.

**Key takeaway:** I/O-bound → threading or asyncio. CPU-bound → multiprocessing. The GIL is the deciding factor.

</details>

> 📖 **Theory:** [Threading vs Multiprocessing](./13_concurrency/theory.md#chapter-3-threading--io-bound-concurrency)

---

### Q54 · [Normal] · `asyncio-basics`

> **What does `async def` define? What is the difference between a coroutine and a regular function?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
`async def` defines a **coroutine function**. Calling it does not run the body — it returns a coroutine object. The body runs when the coroutine is awaited or passed to the event loop.

```python
async def fetch_data():
    return 42

# Calling it does NOT execute the body:
coro = fetch_data()         # just a coroutine object
result = await fetch_data() # THIS runs the body and returns 42
```

Key differences:
- A regular function runs to completion when called.
- A coroutine can **pause** (`await`) to yield control back to the event loop while waiting for something (I/O, sleep, another coroutine).
- Coroutines are cooperative — they explicitly give up control at `await` points.

**How to think through this:**
1. `async def` = "this function can be paused."
2. `await expr` = "pause here until `expr` completes, let others run meanwhile."
3. The event loop manages which coroutine runs — no threads, no GIL issues.

**Key takeaway:** A coroutine is a function that can pause and resume — enabling concurrency without threads through cooperative multitasking.

</details>

> 📖 **Theory:** [asyncio Basics](./13_concurrency/theory.md#asyncio-event-loop--cooperative-not-preemptive)

---

### Q55 · [Logical] · `asyncio-await`

> **What does this print and in what order?**

```python
import asyncio

async def task(name, delay):
    await asyncio.sleep(delay)
    print(f"{name} done")

async def main():
    await asyncio.gather(task("A", 2), task("B", 1))

asyncio.run(main())
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
B done
A done
```

`asyncio.gather` starts both coroutines concurrently. Task B sleeps for 1 second, task A sleeps for 2. B finishes first and prints, then A finishes. Total time ≈ 2 seconds (not 3), because they run concurrently.

**How to think through this:**
1. `gather` starts all tasks and waits for all to complete.
2. Both `asyncio.sleep()` calls begin simultaneously — neither blocks the other.
3. The event loop resumes B after 1 second, then A after 2 seconds.

**Key takeaway:** `asyncio.gather()` runs coroutines concurrently — total time = max(individual times), not sum.

</details>

> 📖 **Theory:** [await](./13_concurrency/theory.md#coroutine-an-async-function-doesnt-run-immediately-when-called)

---

### Q56 · [Critical] · `blocking-in-async`

> **What happens if you call a blocking function (like `time.sleep()`) inside an async function? How do you run blocking code without freezing the event loop?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Calling `time.sleep()` inside an async function **blocks the entire event loop** — all other coroutines are frozen for the duration. This defeats the purpose of asyncio.

```python
async def bad():
    time.sleep(5)   # blocks event loop for 5s — nothing else can run
    
async def good():
    await asyncio.sleep(5)  # yields control; others run while waiting
```

For blocking I/O or CPU-bound code:
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def run_blocking():
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, blocking_function, arg)
```

`run_in_executor` runs the blocking function in a thread pool and awaits it without blocking the event loop.

**How to think through this:**
1. The event loop is single-threaded. A blocking call freezes it.
2. `await asyncio.sleep()` = pause cooperatively. `time.sleep()` = freeze everything.
3. Use `run_in_executor` to offload blocking work to threads.

**Key takeaway:** Never call blocking functions directly in async code — use `await asyncio.sleep()` or `run_in_executor` to keep the event loop responsive.

</details>

> 📖 **Theory:** [Blocking in Async](./13_concurrency/theory.md#asyncio-has-its-own-sync-primitives-non-blocking)

---

### Q57 · [Thinking] · `reference-counting`

> **How does Python's primary garbage collection mechanism work? What does `sys.getrefcount()` tell you?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Python uses **reference counting** as its primary memory management mechanism. Every object has a counter tracking how many references point to it. When the count drops to zero, the object is immediately deallocated.

```python
import sys
x = [1, 2, 3]
print(sys.getrefcount(x))   # 2 (x + the argument to getrefcount)
y = x
print(sys.getrefcount(x))   # 3 (x, y, argument)
del y
print(sys.getrefcount(x))   # 2 again
```

Note: `getrefcount` always shows at least 1 extra — the function argument itself is a temporary reference.

Reference counting is fast and deterministic (objects die immediately when unused), but it cannot handle **reference cycles** (A → B → A). Python's cyclic garbage collector handles those separately.

**How to think through this:**
1. Every `=` assignment, function call, container membership increments the count.
2. Every `del`, scope exit, container removal decrements it.
3. Count hits zero → memory freed immediately.

**Key takeaway:** Reference counting is Python's primary GC — fast and deterministic, but requires a separate cycle collector for circular references.

</details>

> 📖 **Theory:** [Reference Counting](./01.1_memory_management/theory.md#3-reference-counting)

---

### Q58 · [Normal] · `gc-cycles`

> **What type of memory leak does Python's cyclic garbage collector handle that reference counting cannot?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Reference cycles** — when a group of objects reference each other in a cycle such that no external references remain, but the counts never reach zero.

```python
a = []
b = []
a.append(b)   # a references b
b.append(a)   # b references a
del a
del b
# a and b still reference each other — refcount never reaches 0
# Only the cyclic GC can collect these
```

Python's `gc` module runs periodically to find and collect these "islands" of objects that are only reachable from each other.

```python
import gc
gc.collect()  # force a collection cycle
```

**How to think through this:**
1. After `del a` and `del b`, no external references exist.
2. But `a.__refcount__` is still 1 (b points to it) and `b.__refcount__` is 1 (a points to it).
3. The cyclic GC traces object graphs to find isolated cycles.

**Key takeaway:** Reference counting fails for cycles — Python's cyclic GC runs periodically to clean them up. Avoid circular references in long-running applications.

</details>

> 📖 **Theory:** [GC Cycles](./01.1_memory_management/theory.md#6-garbage-collector-gc)

---

### Q59 · [Design] · `__slots__`

> **What does `__slots__` do? When should you use it and what do you give up by using it?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
`__slots__` replaces the per-instance `__dict__` with a fixed set of slots (C-level arrays), saving memory and slightly speeding up attribute access.

```python
class Point:
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
# p.z = 3  → AttributeError — can't add arbitrary attributes
```

Memory savings: a regular instance `__dict__` uses ~200–400 bytes overhead. With `__slots__`, the overhead is minimal — critical when you have millions of instances.

**What you give up:**
- Cannot add arbitrary attributes dynamically.
- `__dict__` and `__weakref__` are not created (unless you include them in `__slots__`).
- Multiple inheritance with slots requires careful handling.

**When to use:** Classes with many instances and a fixed, known set of attributes (e.g. Point, Coordinate, record-style objects).

**How to think through this:**
1. Normal class: instance has a `__dict__` — a hash map that can hold any attribute.
2. `__slots__`: replaces `__dict__` with fixed named slots — much smaller memory footprint.
3. The tradeoff: flexibility vs memory/speed.

**Key takeaway:** Use `__slots__` for classes that will have millions of instances with a fixed attribute set — can reduce memory usage by 40–60%.

</details>

> 📖 **Theory:** [__slots__](./01.1_memory_management/theory.md#use-__slots__05_oops15_slotsmd-in-classes)

---

### Q60 · [Interview] · `metaclass`

> **What is a metaclass in Python? Give a one-line analogy and one real use case where you would actually use one.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A metaclass is the class of a class — just as a class defines how instances behave, a metaclass defines how classes behave.

**Analogy:** If a class is a blueprint for objects, a metaclass is a blueprint for blueprints.

In Python, every class is an instance of `type`. `type` is the default metaclass. You can subclass `type` to customise class creation.

```python
class Meta(type):
    def __new__(mcs, name, bases, namespace):
        # Force all method names to be lowercase
        for key in list(namespace):
            if callable(namespace[key]) and key.upper() == key:
                raise TypeError(f"Method {key} must be lowercase")
        return super().__new__(mcs, name, bases, namespace)

class MyClass(metaclass=Meta):
    def valid_method(self): pass
```

**Real use cases:**
1. **ORMs** (Django/SQLAlchemy) — auto-generate database columns from class attributes.
2. **API frameworks** — auto-register routes or validators.
3. **Enforcing coding standards** — require all subclasses to implement certain methods.

In most cases, class decorators or `__init_subclass__` are simpler alternatives. Only reach for metaclasses when you need to control class creation itself.

**How to think through this:**
1. `class MyClass:` → Python calls `type("MyClass", bases, namespace)` to build the class object.
2. Custom metaclass intercepts this call.
3. You can modify the namespace, validate structure, add methods — before the class even exists.

**Key takeaway:** A metaclass controls how classes are created — powerful but complex. Prefer `__init_subclass__` or class decorators for most use cases.

</details>

> 📖 **Theory:** [Metaclasses](./15_advanced_python/theory.md#chapter-8-metaclasses--classes-of-classes)

---

### Q61 · [Logical] · `type-as-metaclass`

> **What does this print?**

```python
MyClass = type("MyClass", (object,), {"x": 10, "greet": lambda self: "hello"})
obj = MyClass()
print(obj.x)
print(obj.greet())
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
10
hello
```

`type(name, bases, namespace)` called with three arguments creates a new class dynamically. This is exactly what `class MyClass(object): x=10` does internally. `MyClass` gets attribute `x=10` and method `greet`. Instances of `MyClass` can access both.

**How to think through this:**
1. `type("MyClass", (object,), {...})` is the dynamic equivalent of writing a `class` block.
2. The third argument is the class namespace (attributes and methods).
3. `obj = MyClass()` creates an instance. `obj.x` reads the class attribute. `obj.greet()` calls the lambda with `self=obj`.

**Key takeaway:** `type(name, bases, dict)` is how Python creates every class — the `class` keyword is syntactic sugar for this call.

</details>

> 📖 **Theory:** [type() as Metaclass](./15_advanced_python/theory.md#chapter-8-metaclasses--classes-of-classes)

---

### Q62 · [Thinking] · `__new__-vs-__init__`

> **What is the difference between `__new__` and `__init__`? When would you override `__new__`?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- `__new__(cls, ...)` — creates and returns the new instance. Class method (receives the class, not self). Called first.
- `__init__(self, ...)` — initialises the already-created instance. Called second, after `__new__`.

Normal flow: `obj = MyClass(args)` → `MyClass.__new__(MyClass, args)` returns an instance → `__init__(instance, args)` sets it up.

Override `__new__` when:
1. **Implementing a Singleton** — return the existing instance instead of creating a new one.
2. **Immutable types** — `str`, `int`, `tuple` are immutable; you must use `__new__` to set their value since `__init__` runs after the object is already created (and immutable).
3. **Returning a different type** — `__new__` can return an instance of a different class (unusual).

```python
class Singleton:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**How to think through this:**
1. `__new__` = the factory. `__init__` = the setup.
2. For most classes, only `__init__` is needed.
3. `__new__` matters when you need to control object creation itself, not just initialisation.

**Key takeaway:** Override `__init__` to initialise; override `__new__` only when you need to control object creation (Singletons, immutable subclasses).

</details>

> 📖 **Theory:** [__new__ vs __init__](./15_advanced_python/theory.md#total-288-bytes-per-instance)

---

### Q63 · [Normal] · `descriptors`

> **What is a descriptor in Python? What three methods make up the descriptor protocol?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A descriptor is any object that defines one or more of the three descriptor protocol methods. When a descriptor is assigned as a class attribute, Python calls these methods automatically on attribute access/assignment/deletion on instances.

The three methods:
1. `__get__(self, obj, objtype=None)` — called on attribute access (`instance.attr`).
2. `__set__(self, obj, value)` — called on attribute assignment (`instance.attr = value`).
3. `__delete__(self, obj)` — called on `del instance.attr`.

```python
class PositiveNumber:
    def __set_name__(self, owner, name):
        self.name = name
    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return obj.__dict__.get(self.name)
    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError(f"{self.name} must be positive")
        obj.__dict__[self.name] = value

class Circle:
    radius = PositiveNumber()

c = Circle()
c.radius = 5    # calls PositiveNumber.__set__
c.radius = -1   # raises ValueError
```

**How to think through this:**
1. A descriptor lives on the class, but intercepts attribute access on instances.
2. `__get__` alone = non-data descriptor (read-only). `__get__` + `__set__` = data descriptor (can control reads and writes).

**Key takeaway:** Descriptors let you attach reusable attribute validation or transformation logic to class attributes — `@property` is a built-in descriptor.

</details>

> 📖 **Theory:** [Descriptors](./15_advanced_python/theory.md#descriptor-protocol)

---

### Q64 · [Thinking] · `property-decorator`

> **How does `@property` work under the hood? Rewrite a simple property without using the decorator.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
`@property` is a built-in descriptor class. `@property` creates a data descriptor that calls your getter function on `__get__`, the setter function on `__set__`, and the deleter on `__delete__`.

With `@property`:
```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0: raise ValueError
        self._radius = value
```

Without `@property` (using `property()` directly):
```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    def _get_radius(self): return self._radius
    def _set_radius(self, v):
        if v < 0: raise ValueError
        self._radius = v

    radius = property(_get_radius, _set_radius)
```

Both are equivalent. `@property` is just cleaner syntax.

**How to think through this:**
1. `property(fget, fset, fdel, doc)` creates a descriptor object stored as a class attribute.
2. On `obj.radius`, Python finds `radius` on the class (a descriptor) and calls `radius.__get__(obj, type(obj))` → calls your getter.
3. `@property` is `radius = property(radius)` — replaces the function with a property descriptor.

**Key takeaway:** `@property` is a descriptor — it intercepts attribute access and routes it through your getter/setter functions.

</details>

> 📖 **Theory:** [property](./15_advanced_python/theory.md#implementing-property-from-scratch)

---

### Q65 · [Critical] · `descriptor-vs-property`

> **When would you write a full descriptor class instead of using `@property`? What does a descriptor give you that property doesn't?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Use a full descriptor class when you need **reusable validation or behaviour across multiple attributes or multiple classes**.

`@property` is per-attribute on a specific class — you can't reuse it. A descriptor class can be instantiated multiple times on different attributes:

```python
class TypeChecked:
    def __init__(self, expected_type):
        self.expected_type = expected_type
    def __set_name__(self, owner, name):
        self.name = name
    def __get__(self, obj, objtype=None):
        return obj.__dict__.get(self.name) if obj else self
    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(f"{self.name} must be {self.expected_type}")
        obj.__dict__[self.name] = value

class Person:
    name = TypeChecked(str)    # reused
    age = TypeChecked(int)     # reused on different attribute
    height = TypeChecked(float)
```

With `@property` you'd have to write three separate property definitions with nearly identical logic.

**How to think through this:**
1. `@property` = one-off logic for one specific attribute.
2. Descriptor class = reusable attribute behaviour shared across many attributes and classes.

**Key takeaway:** Use `@property` for simple one-off logic; write a descriptor class when the same validation/transformation is needed on multiple attributes.

</details>

> 📖 **Theory:** [Descriptor vs Property](./15_advanced_python/theory.md#descriptors--the-protocol-behind-property)

---

### Q66 · [Normal] · `type-hints`

> **What are type hints in Python? Are they enforced at runtime? What tool actually checks them?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Type hints are annotations that declare the expected types of variables, function parameters, and return values:

```python
def greet(name: str, times: int = 1) -> str:
    return (f"Hello {name}! " * times).strip()
```

**Are they enforced at runtime?** No. Python completely ignores type hints at runtime — you can pass the wrong type and Python will not raise an error (unless the code itself fails for other reasons).

Type hints are checked by **static analysis tools**:
- **mypy** — the standard Python type checker
- **pyright** / **pylance** — used by VS Code
- **Pydantic** — does enforce types at runtime for data validation

**How to think through this:**
1. Type hints = documentation that tools can check.
2. At runtime, they are stored in `__annotations__` but not enforced.
3. Run `mypy myfile.py` to catch type errors before they become runtime bugs.

**Key takeaway:** Type hints are not enforced by Python — they are for static checkers (mypy, pyright) and documentation. Use them for all production code.

</details>

> 📖 **Theory:** [Type Hints](./14_type_hints_and_pydantic/theory.md#type-hints--pydantic--theory)

---

### Q67 · [Thinking] · `protocol`

> **What is `typing.Protocol`? How is it different from ABC (Abstract Base Class)?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
`Protocol` enables **structural subtyping** (duck typing with static checking) — a class is compatible with a Protocol if it has the required methods/attributes, without needing to explicitly inherit from it.

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:       # does NOT inherit from Drawable
    def draw(self): print("O")

class Square:       # does NOT inherit from Drawable
    def draw(self): print("□")

def render(shape: Drawable) -> None:
    shape.draw()

render(Circle())   # type checker: OK — Circle has draw()
render(Square())   # type checker: OK
```

**ABC (Nominal subtyping):** A class must explicitly inherit from the ABC to be considered a subtype. `isinstance(obj, MyABC)` checks inheritance.

**Protocol (Structural subtyping):** A class just needs to have the right methods. No explicit inheritance. The type checker verifies structure.

**How to think through this:**
1. ABC = "officially declare you support this interface" (nominal — name matters).
2. Protocol = "if you have the right methods, you're compatible" (structural — structure matters).
3. Protocol is better for integrating third-party classes you can't modify.

**Key takeaway:** Use `Protocol` when you want duck typing with static type checking — no inheritance needed. Use ABC when you want to enforce explicit registration and runtime `isinstance` checks.

</details>

> 📖 **Theory:** [Protocol](./14_type_hints_and_pydantic/theory.md#typingprotocol--duck-typing-with-type-hints)

---

### Q68 · [Normal] · `pydantic`

> **What does Pydantic do that plain type hints don't? Give a use case where Pydantic prevents a real bug.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Pydantic **enforces types at runtime** and automatically validates/coerces input data. Plain type hints are ignored at runtime.

```python
from pydantic import BaseModel, validator

class UserCreate(BaseModel):
    name: str
    age: int
    email: str

# Valid
u = UserCreate(name="Alice", age=30, email="alice@example.com")

# Pydantic coerces: age="25" → 25
u2 = UserCreate(name="Bob", age="25", email="bob@example.com")

# Pydantic raises ValidationError
u3 = UserCreate(name="Charlie", age="not-a-number", email="x")
```

Real bug prevented: An API receives JSON where `age` is a string `"25"`. With plain type hints, `user.age + 1` raises `TypeError`. With Pydantic, `"25"` is automatically coerced to `int` 25, or a validation error is raised early with a clear message.

**How to think through this:**
1. Plain type hints: `def f(x: int)` — Python ignores this. You can pass `"hello"`.
2. Pydantic: `class M(BaseModel): x: int` — passing `"hello"` raises `ValidationError` immediately.
3. Use Pydantic at system boundaries: API inputs, config files, database rows.

**Key takeaway:** Pydantic moves type checking from static analysis to runtime validation — essential for untrusted input (API requests, config files, CSV data).

</details>

> 📖 **Theory:** [Pydantic](./14_type_hints_and_pydantic/theory.md#7-pydantic-basemodel--defining-models)

---

### Q69 · [Design] · `singleton-pattern`

> **Implement a thread-safe Singleton in Python. What problem does the Singleton pattern solve and what are its downsides?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
import threading

class Singleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:   # double-checked locking
                    cls._instance = super().__new__(cls)
        return cls._instance
```

**Problem it solves:** Ensures exactly one instance of a class exists globally — useful for database connections, config managers, logging handlers.

**Downsides:**
1. Global state — makes testing hard (hard to reset between tests).
2. Hidden dependencies — code that uses the singleton doesn't declare its dependency explicitly.
3. Thread-safety complexity — requires careful locking.
4. Violates Single Responsibility — the class manages both its own logic and its own instantiation.

**How to think through this:**
1. Double-checked locking: first check without lock (fast path), then check again inside lock (safe path).
2. Module-level variables in Python are natural singletons — `import module` and the module object is cached.
3. Dependency injection is often better than Singleton for testability.

**Key takeaway:** Singletons solve global shared resource access but introduce hidden global state — prefer dependency injection for testable code.

</details>

> 📖 **Theory:** [Singleton](./16_design_patterns/theory.md#2-singleton-pattern)

---

### Q70 · [Normal] · `factory-pattern`

> **What is the Factory pattern? Write a simple factory function that returns different animal objects based on a string input.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The Factory pattern centralises object creation — callers say "give me a Dog" without knowing how to build one. The factory decides which class to instantiate.

```python
class Dog:
    def speak(self): return "Woof"

class Cat:
    def speak(self): return "Meow"

class Bird:
    def speak(self): return "Tweet"

def animal_factory(kind: str):
    animals = {"dog": Dog, "cat": Cat, "bird": Bird}
    cls = animals.get(kind.lower())
    if cls is None:
        raise ValueError(f"Unknown animal: {kind}")
    return cls()

pet = animal_factory("dog")
print(pet.speak())  # Woof
```

**Why use it:**
- Decouples creation from usage — callers don't need to import or know about concrete classes.
- Adding a new type only requires updating the factory, not all call sites.
- Easy to mock in tests.

**How to think through this:**
1. The dict maps string → class. This is cleaner than a chain of if/elif.
2. The factory returns an instance, not a class.
3. For more complex creation logic, use a class with a `create` method.

**Key takeaway:** Factory pattern centralises object creation behind a single function/class, decoupling callers from concrete implementations.

</details>

> 📖 **Theory:** [Factory](./16_design_patterns/theory.md#3-factory-pattern)

---

### Q71 · [Thinking] · `observer-pattern`

> **What is the Observer pattern? Describe how you would implement it in Python using a simple event system.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The Observer pattern defines a one-to-many relationship: when a subject changes state, all registered observers are notified automatically.

```python
class EventEmitter:
    def __init__(self):
        self._listeners: dict[str, list] = {}

    def on(self, event: str, callback):
        self._listeners.setdefault(event, []).append(callback)

    def emit(self, event: str, *args, **kwargs):
        for cb in self._listeners.get(event, []):
            cb(*args, **kwargs)

# Usage
emitter = EventEmitter()
emitter.on("user_created", lambda u: print(f"Send welcome email to {u}"))
emitter.on("user_created", lambda u: print(f"Log new user: {u}"))

emitter.emit("user_created", "alice@example.com")
# Send welcome email to alice@example.com
# Log new user: alice@example.com
```

**Real use cases:** GUI events, webhook systems, domain event propagation, plugin hooks.

**How to think through this:**
1. Subject (EventEmitter) maintains a list of subscribers per event.
2. `.on()` registers a callback. `.emit()` calls all registered callbacks.
3. Observers are decoupled from each other and from the subject.

**Key takeaway:** Observer decouples event producers from event consumers — adding a new reaction requires only registering a new listener, not changing the producer.

</details>

> 📖 **Theory:** [Observer](./16_design_patterns/theory.md#5-observer-pattern)

---

### Q72 · [Normal] · `profiling`

> **What tools does Python have for profiling code performance? What is the difference between `cProfile` and `timeit`?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- **`cProfile`** — a deterministic profiler. Instruments every function call and reports: number of calls, total time, time per call, cumulative time. Use to find which function is the bottleneck in a real program.

```python
import cProfile
cProfile.run("my_function()")
```

- **`timeit`** — measures the execution time of a small code snippet, running it many times to get a stable average. Use to benchmark and compare small pieces of code.

```python
import timeit
timeit.timeit("[x**2 for x in range(1000)]", number=10000)
```

- **`line_profiler`** (third-party) — profiles line by line inside a function.
- **`memory_profiler`** (third-party) — measures memory usage line by line.
- **`py-spy`** (third-party) — sampling profiler, attaches to running process.

**How to think through this:**
1. `cProfile`: "Which function is eating all my time?" → use on a full program run.
2. `timeit`: "Is list comprehension faster than a for loop for this?" → use for micro-benchmarks.
3. Always profile before optimising — never guess.

**Key takeaway:** Use `cProfile` to find bottlenecks in real code; use `timeit` to benchmark specific implementations.

</details>

> 📖 **Theory:** [Profiling](./18_performance_optimization/profiling.md)

---

### Q73 · [Thinking] · `complexity-in-practice`

> **You have a list of 1 million items and need to check membership frequently. Should you use a list or a set? Explain why in terms of time complexity.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Use a **set**. `x in set` is O(1) average; `x in list` is O(n).

For 1 million items:
- List membership check: scans up to 1,000,000 elements → extremely slow.
- Set membership check: computes `hash(x)` and looks up the bucket → constant time.

```python
data_list = list(range(1_000_000))
data_set = set(data_list)

# Timing (approximate):
# 999999 in data_list  →  ~10ms
# 999999 in data_set   →  ~0.05ms  (200× faster)
```

Convert once, query many times:
```python
allowed = set(load_from_db())    # O(n) once to build
for item in stream:
    if item in allowed:           # O(1) each check
        process(item)
```

**How to think through this:**
1. List = sequential scan = O(n) per check.
2. Set = hash table = O(1) average per check.
3. Building the set is O(n) — pay that cost once, then amortise over all queries.

**Key takeaway:** Always convert to a set before repeated membership checks — O(1) vs O(n) is the difference between fast and unusable at scale.

</details>

> 📖 **Theory:** [Complexity in Practice](./18_performance_optimization/profiling.md)

---

### Q74 · [Debug] · `performance-bug`

> **This code is very slow for large inputs. What is wrong and how do you fix it?**

```python
def find_duplicates(items):
    duplicates = []
    for item in items:
        if items.count(item) > 1:
            if item not in duplicates:
                duplicates.append(item)
    return duplicates
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Two performance bugs:
1. `items.count(item)` — O(n) scan inside an O(n) loop → **O(n²)** total.
2. `item not in duplicates` — O(n) scan of the duplicates list on every iteration.

**Fix using a Counter:**
```python
from collections import Counter

def find_duplicates(items):
    counts = Counter(items)         # O(n)
    return [item for item, c in counts.items() if c > 1]  # O(n)
# Total: O(n)
```

Or with sets:
```python
def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)
# O(n), O(n) space
```

**How to think through this:**
1. Spot the nested O(n) operations: loop × `.count()` × `not in list`.
2. Replace `.count()` with a pre-computed Counter.
3. Replace the duplicates list with a set for O(1) membership.

**Key takeaway:** Any `.count()` or `in list` inside a loop is a hidden O(n²) — replace with Counter or set.

</details>

> 📖 **Theory:** [Performance Bug](./18_performance_optimization/profiling.md)

---

### Q75 · [Design] · `slots-optimization`

> **You are building a class that will have millions of instances (e.g. a Point class for coordinates). What two optimizations should you apply and why?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
1. **`__slots__`** — eliminates the per-instance `__dict__`. Each instance's attributes are stored in a fixed C-level array instead. Saves ~100–300 bytes per instance.

2. **`__slots__` + no inheritance from dict/list** — keeps the class lightweight. Also consider `@dataclass(slots=True)` (Python 3.10+) for the cleanest syntax.

```python
class Point:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Python 3.10+ — even cleaner:
from dataclasses import dataclass

@dataclass(slots=True)
class Point:
    x: float
    y: float
```

For extreme cases (read-only coordinate data): consider `__slots__` + `__weakref__` removal + `namedtuple` for even lower overhead.

Memory comparison for 1 million instances:
- Regular class: ~56 bytes/object + 200-byte `__dict__` = ~256MB total
- With `__slots__`: ~56 bytes/object = ~56MB total (~4.5× reduction)

**How to think through this:**
1. Each regular instance carries a hash-map (`__dict__`) for arbitrary attributes — expensive when you have millions.
2. `__slots__` tells Python: "these are the only attributes, ever" — store them efficiently.
3. Pair with `@dataclass(slots=True)` for type hints and auto-generated methods.

**Key takeaway:** For high-volume instances: `__slots__` eliminates `__dict__` overhead, cutting memory usage by 3–5×.

</details>

> 📖 **Theory:** [__slots__](./01.1_memory_management/theory.md#use-__slots__05_oops15_slotsmd-in-classes)

---

## Tier 4 — Interview & Scenario · Q76–Q90

> Focus: Explain concepts clearly, compare approaches, reason through production problems

---

### Q76 · [Interview] · `explain-generators`

> **Explain generators to a junior developer who only knows lists. Why would you ever not use a list?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
"Imagine you're reading a 10GB log file. A list would load the whole file into RAM — your machine grinds to a halt. A generator reads one line at a time, processes it, discards it, and moves to the next. At any moment, only one line is in memory.

A list is like printing all pages of a book before you start reading. A generator is like reading one page, then the next, never holding more than one page at once."

Technical points to cover:
- Generators use `yield` to produce values lazily, one at a time.
- They pause execution at `yield` and resume where they left off.
- Memory usage is O(1) vs O(n) for lists.
- Generators are single-pass — you can't index them or iterate them twice.
- Use lists when you need random access, multiple passes, or `len()`. Use generators for streaming/pipeline processing.

**How to think through this:**
1. Start with an analogy the junior dev can picture.
2. Show the memory implication concretely (10GB file → list crash vs generator fine).
3. State the limitation: single-pass, no indexing.

**Key takeaway:** Generators = lazy, memory-efficient, single-pass. Lists = eager, in-memory, reusable. Choose based on whether you need to hold all data or stream it.

</details>

> 📖 **Theory:** [Generators](./11_generators_iterators/theory.md#why-generators-are-lazy--the-memory-story)

---

### Q77 · [Interview] · `explain-decorators`

> **A non-technical colleague asks what decorators do. Give a real-world analogy and then the technical explanation.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Analogy:** Think of a decorator like a coffee sleeve on a cup. The coffee (your function) stays the same — you haven't changed what's inside. The sleeve (the decorator) adds something around it: insulation, a logo, a handle. You still drink the same coffee; you just get extra features with it.

**Technical explanation:**
A decorator is a function that wraps another function to add behaviour before, after, or around it — without modifying the original function's code.

```python
@timer           # equivalent to: greet = timer(greet)
def greet(name):
    print(f"Hello {name}")
```

Common uses in production:
- `@login_required` — check authentication before running a view
- `@retry(times=3)` — automatically retry on failure
- `@cache` — store results and return them on repeat calls
- `@log_calls` — record every function call for debugging

**How to think through this:**
1. The analogy first — meet the audience where they are.
2. Then the one-liner: "a function that wraps another function."
3. Concrete real-world examples they'd recognise from Django/Flask.

**Key takeaway:** Decorators add reusable cross-cutting behaviour (logging, auth, retry) to functions without touching the function's code.

</details>

> 📖 **Theory:** [Decorators](./10_decorators/theory.md#decorators--theory)

---

### Q78 · [Interview] · `explain-gil`

> **Your team lead asks: "Should we use threading or multiprocessing for our CPU-heavy data processing pipeline?" Walk through your reasoning out loud.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
"Great question — the answer depends on what the bottleneck is, but for CPU-heavy work, my recommendation is multiprocessing.

Here is my reasoning:

The GIL — Python's Global Interpreter Lock — means that even if we spin up 8 threads on an 8-core machine, only one thread can execute Python bytecode at a time. For CPU-bound work (number crunching, parsing, transformations), threads queue up on the GIL. We get no speedup from multiple threads.

Multiprocessing bypasses this entirely: each process has its own Python interpreter and its own GIL. On an 8-core machine we can run 8 processes genuinely in parallel.

The tradeoffs to be aware of:
1. Processes don't share memory — we need to serialise data passed between them (pickle overhead).
2. Process startup is heavier than thread startup.
3. For this pipeline, if the data can be chunked and processed independently, `ProcessPoolExecutor` from `concurrent.futures` is the cleanest solution.

If any part of the pipeline is I/O-bound (reading from S3, writing to a database), we might use a mix: asyncio or threading for I/O, multiprocessing for CPU stages."

**How to think through this:**
1. Identify the bottleneck: CPU-bound → multiprocessing.
2. Explain the GIL clearly — it is the technical reason.
3. Cover tradeoffs (serialisation cost, startup overhead).
4. Mention `concurrent.futures` as the practical tool.

**Key takeaway:** CPU-bound → multiprocessing (bypasses GIL). I/O-bound → threading or asyncio (GIL released during waits). Always profile before deciding.

</details>

> 📖 **Theory:** [GIL Explanation](./13_concurrency/theory.md#chapter-2-the-gil--pythons-most-misunderstood-feature)

---

### Q79 · [Interview] · `explain-async`

> **When would you choose `asyncio` over threading? Give a scenario where asyncio is clearly the right choice.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Choose asyncio when you have **many concurrent I/O-bound operations** that spend most of their time waiting, and you want high throughput with low memory overhead.

**Scenario where asyncio wins:**
A web scraper that fetches 10,000 pages. With threading, 10,000 threads would use ~100MB just for thread stacks. Threads involve OS context switches. With asyncio, a single thread manages 10,000 connections cooperatively — `await` yields control while waiting for each response. Memory is a fraction, and no OS context switch overhead.

```python
async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

**When to prefer threading over asyncio:**
- When using libraries that are not async-compatible (requests, most DB drivers are synchronous).
- When the concurrency level is low (< 100 tasks) — threading is simpler.
- When you have legacy synchronous code you cannot rewrite.

**How to think through this:**
1. asyncio: single thread, explicit cooperative yields, zero context-switch overhead.
2. threading: multiple OS threads, implicit preemptive scheduling, GIL limits CPU parallelism.
3. For 10,000+ concurrent I/O tasks, asyncio scales better.

**Key takeaway:** asyncio shines for high-concurrency I/O (thousands of connections). Threading is simpler for low-concurrency or when libraries aren't async-compatible.

</details>

> 📖 **Theory:** [asyncio Explained](./13_concurrency/theory.md#asyncio-event-loop--cooperative-not-preemptive)

---

### Q80 · [Interview] · `explain-memory`

> **How would you investigate a Python process that is using more memory than expected? Name the tools and the steps.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Step 1 — Confirm the problem:** Use `top`, `htop`, or `psutil` to measure RSS (Resident Set Size). Get a baseline and check how it grows over time.

**Step 2 — Find the big objects:** Use `tracemalloc` (built-in) to trace where allocations happen:
```python
import tracemalloc
tracemalloc.start()
# ... run code ...
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")
for stat in top_stats[:10]:
    print(stat)
```

**Step 3 — Find object counts:** Use `gc` and `objgraph` (third-party) to see what types are accumulating:
```python
import gc, objgraph
objgraph.show_most_common_types(limit=10)
objgraph.show_growth()
```

**Step 4 — Check for cycles:** Run `gc.collect()` and see if the RSS drops. If it does, you have reference cycles accumulating.

**Step 5 — Profile per line:** Install `memory_profiler` and use `@profile` decorator for line-by-line memory usage.

**Common causes:** Caching without eviction, unbounded list accumulation, reference cycles, large DataFrames not released, global variables holding references.

**How to think through this:**
1. Measure first — confirm it is actually growing.
2. Localise — which type of object? Which file and line?
3. Fix — add eviction, break cycles, delete references, use generators.

**Key takeaway:** Investigate memory issues in order: measure → find object type → find allocation site → fix the root cause.

</details>

> 📖 **Theory:** [Memory Management](./01.1_memory_management/theory.md#memory-management-in-python)

---

### Q81 · [Interview] · `compare-list-tuple`

> **Compare lists and tuples — when do you reach for each? Is "tuples are immutable lists" a complete answer?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
"Tuples are immutable lists" is correct but **incomplete**. The semantic difference matters more than the mutability difference.

**The real distinction:**
- **List** — a homogeneous sequence of items of the same type. The number of items can change. Used for collections you iterate over.
- **Tuple** — a heterogeneous record of fixed length. Each position has a specific meaning. Used for structured data.

```python
# List: multiple items of the same kind
temperatures = [22.1, 23.5, 19.8, 25.0]

# Tuple: fixed-position record (name, age, city)
person = ("Alice", 30, "London")
lat_lng = (51.5074, -0.1278)   # two related but different things
```

Additional differences:
- Tuples are hashable (can be dict keys/set members) if their contents are.
- Tuples are slightly faster to create and access.
- `namedtuple` / `typing.NamedTuple` make tuple fields named and self-documenting.
- Python uses tuples for function return values and `*args` internally.

**How to think through this:**
1. Ask: "Are these the same type of thing (list) or different fields of a record (tuple)?"
2. `[1, 2, 3]` — three integers of the same kind → list.
3. `("Alice", 30, "London")` — three different fields describing one entity → tuple.

**Key takeaway:** Lists = homogeneous collections that may change. Tuples = heterogeneous records with fixed structure and meaning per position.

</details>

> 📖 **Theory:** [List vs Tuple](./03_data_types/theory.md#part-6-tuple--the-sealed-list)

---

### Q82 · [Interview] · `compare-dict-defaultdict`

> **What is the difference between `dict`, `defaultdict`, and `Counter`? Give one use case where each is the best choice.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- **`dict`** — standard mapping. `d[key]` raises `KeyError` for missing keys. Use when every key is expected to exist or you want explicit handling of missing keys.
  *Use case:* Configuration mapping where missing keys should be an error.

- **`defaultdict(factory)`** — like dict but returns `factory()` for missing keys instead of raising. `factory` is called once per new key.
  ```python
  from collections import defaultdict
  groups = defaultdict(list)
  for name, team in data:
      groups[team].append(name)   # no need to check if key exists first
  ```
  *Use case:* Grouping items — building a list/set per key without initialisation code.

- **`Counter`** — a dict subclass for counting hashable items. Has special methods: `.most_common(n)`, arithmetic between counters, `.update()`.
  ```python
  from collections import Counter
  word_freq = Counter(text.split())
  print(word_freq.most_common(5))
  ```
  *Use case:* Counting occurrences of anything — words, events, characters.

**How to think through this:**
1. Need to count? → Counter.
2. Need to group or accumulate? → defaultdict.
3. Need strict control over what keys exist? → dict.

**Key takeaway:** `Counter` for counting, `defaultdict` for grouping, `dict` when missing keys are errors.

</details>

> 📖 **Theory:** [dict vs defaultdict](./03_data_types/theory.md#defaultdict--dictionary-that-never-raises-keyerror)

---

### Q83 · [Interview] · `compare-abc-protocol`

> **Compare ABC (Abstract Base Class) and `typing.Protocol`. What is "structural subtyping" and when is it better than nominal subtyping?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Nominal subtyping (ABC):** A class must explicitly declare it implements an interface by inheriting from the ABC. The type checker and `isinstance` verify the class name is in the hierarchy.

```python
from abc import ABC, abstractmethod
class Drawable(ABC):
    @abstractmethod
    def draw(self): ...

class Circle(Drawable):     # explicit declaration required
    def draw(self): ...
```

**Structural subtyping (Protocol):** A class is compatible if it has the right methods — no explicit inheritance needed. The type checker verifies structure, not class names.

```python
from typing import Protocol
class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:               # no inheritance — just has draw()
    def draw(self): ...
```

**When Protocol is better:**
1. Integrating third-party classes you cannot modify.
2. Informal "duck typing" interfaces where explicit registration is overkill.
3. Retrofitting type checking onto existing code.

**When ABC is better:**
1. You want `isinstance()` checks at runtime.
2. You want to enforce that subclasses implement abstract methods.
3. You want to provide default implementations in the base class.


**How to think through this:**
1. **Nominal subtyping** (ABC): class must explicitly declare the relationship — the type system checks names/hierarchy.
2. **Structural subtyping** (Protocol): class is compatible if it has the right shape (methods/attributes) — no explicit declaration needed.
3. Protocol wins when you can't modify the class (third-party), or when duck typing is the right semantic — "if it quacks like a duck."

**Key takeaway:** ABC = explicit opt-in, runtime enforceable. Protocol = implicit structural matching, no inheritance needed. Use Protocol for type hints; use ABC when runtime enforcement matters.

</details>

> 📖 **Theory:** [ABC vs Protocol](./14_type_hints_and_pydantic/theory.md#typingprotocol--duck-typing-with-type-hints)

---

### Q84 · [Interview] · `compare-process-thread-coroutine`

> **Compare processes, threads, and coroutines in Python. What resource does each share or isolate?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

| | Process | Thread | Coroutine |
|---|---|---|---|
| Memory | Separate (isolated) | Shared | Shared (single thread) |
| GIL | Own GIL | Shared GIL | No GIL issue (single thread) |
| Parallelism | True (multi-core) | Concurrent (GIL limits CPU) | Cooperative (one at a time) |
| Overhead | High (fork/spawn, IPC) | Medium (OS scheduler) | Very low (function call level) |
| Best for | CPU-bound tasks | I/O-bound, moderate concurrency | High-concurrency I/O |
| Communication | Queue, Pipe, shared memory | Shared variables (need locks) | Shared variables (no locks needed*) |

*Coroutines are single-threaded so no race conditions from preemption — but logic bugs still possible at await points.

**How to think through this:**
1. Processes = fully isolated workers. Safe but expensive to spawn and communicate between.
2. Threads = lightweight workers sharing memory. Fast communication, but require locks.
3. Coroutines = cooperative tasks on one thread. Zero overhead, no race conditions from preemption, but blocking one blocks all.

**Key takeaway:** Processes for CPU isolation, threads for moderate I/O concurrency, coroutines for massive I/O concurrency with minimal overhead.

</details>

> 📖 **Theory:** [Process vs Thread vs Coroutine](./13_concurrency/theory.md#process-vs-thread)

---

### Q85 · [Interview] · `compare-deepcopy-pickle`

> **When would you use `copy.deepcopy()` vs `pickle`? What are the limitations of each?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- **`copy.deepcopy()`** — creates an independent in-memory copy of an object graph. Fast, stays in the same process.
  *Use when:* You need a clone of a complex nested object to mutate independently, within the same program run.
  *Limitations:* Cannot cross process boundaries. Cannot save to disk. Some objects (locks, file handles, database connections) cannot be deep-copied.

- **`pickle`** — serialises an object to bytes (disk or network), can be deserialised later in a different process or time.
  *Use when:* Saving model state to disk, passing data between processes via `Queue`, caching objects.
  *Limitations:* Security risk — never unpickle data from untrusted sources (arbitrary code execution). Slower than deepcopy. Not all objects are picklable. Pickle format can break across Python versions.

```python
import pickle, copy

# deepcopy: in-memory clone
clone = copy.deepcopy(original)

# pickle: serialise to bytes / file
data = pickle.dumps(original)
restored = pickle.loads(data)
```

**How to think through this:**
1. Same process, need a copy? → deepcopy.
2. Need to save to disk or send to another process? → pickle (or json for simple data).

**Key takeaway:** `deepcopy` = in-memory clone. `pickle` = serialise for storage/IPC. Never unpickle untrusted data.

</details>

> 📖 **Theory:** [deepcopy vs pickle](./01.1_memory_management/theory.md)

---

### Q86 · [Design] · `rate-limiter-scenario`

> **You are building an API and need to limit each user to 100 requests per minute. How would you implement this in pure Python (no external libraries)?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Use a **sliding window** approach with a `deque` of timestamps per user:

```python
from collections import deque, defaultdict
import time

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self._calls: dict[str, deque] = defaultdict(deque)

    def is_allowed(self, user_id: str) -> bool:
        now = time.time()
        user_calls = self._calls[user_id]

        # Remove timestamps outside the window
        while user_calls and user_calls[0] < now - self.window:
            user_calls.popleft()

        if len(user_calls) < self.max_requests:
            user_calls.append(now)
            return True
        return False

limiter = RateLimiter(max_requests=100, window_seconds=60)
```

In production: store timestamps in Redis (for multi-server environments). Use Redis' ZADD + ZRANGEBYSCORE for atomic sliding window operations.

**How to think through this:**
1. Track the timestamps of recent calls per user in a sliding window.
2. On each request: remove old timestamps outside the window, count what remains.
3. If count < limit: allow and record the new timestamp. Otherwise: reject.

**Key takeaway:** Rate limiter = per-user sliding window of timestamps. deque for efficient prefix removal. Redis for distributed environments.

</details>

> 📖 **Theory:** [Rate Limiter](./16_design_patterns/theory.md#design-patterns-in-python)

---

### Q87 · [Design] · `caching-scenario`

> **A function is called thousands of times with the same inputs and is slow. How do you cache its results? Show two approaches — one built-in, one manual.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Built-in: `@functools.lru_cache`**
```python
from functools import lru_cache

@lru_cache(maxsize=256)
def expensive(n: int) -> int:
    # slow computation
    return sum(range(n))

expensive(1000)   # computed
expensive(1000)   # returned from cache instantly
```

Works for functions with hashable arguments. `maxsize=None` for unlimited cache (`@functools.cache` in Python 3.9+).

**Manual: dict cache**
```python
_cache: dict = {}

def expensive(n: int) -> int:
    if n in _cache:
        return _cache[n]
    result = sum(range(n))
    _cache[n] = result
    return result
```

Manual gives you control over eviction, TTL, and serialisation. Use when you need cache expiry, shared cache across processes, or persistence.

**When to use which:**
- `lru_cache`: simple, automatic, bounded, thread-safe. 90% of cases.
- Manual dict: when you need TTL, custom eviction, or cache inspection.
- Redis/Memcached: when cache must survive restarts or be shared across servers.

**How to think through this:**
1. Is the function pure (same input always gives same output)? → safe to cache.
2. `lru_cache` first — zero boilerplate.
3. Need TTL or persistence? → manual or Redis.

**Key takeaway:** `@lru_cache` is the fastest path to memoisation. Go manual or Redis when you need TTL, shared state, or persistence.

</details>

> 📖 **Theory:** [Caching](./18_performance_optimization/profiling.md)

---

### Q88 · [Design] · `retry-scenario`

> **You are calling an external API that occasionally fails with a 503 error. Write a retry decorator with exponential backoff.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
import functools, time, random

def retry(max_attempts=3, base_delay=1.0, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    jitter = random.uniform(0, delay * 0.1)
                    print(f"Attempt {attempt} failed: {e}. Retrying in {delay:.1f}s...")
                    time.sleep(delay + jitter)
        return wrapper
    return decorator

@retry(max_attempts=3, base_delay=1.0, exceptions=(IOError, ConnectionError))
def call_api(url):
    ...
```

Key design decisions:
1. **Exponential backoff** — delays double each attempt (1s, 2s, 4s) to avoid thundering herd.
2. **Jitter** — small random offset prevents all retrying clients hitting the server simultaneously.
3. **Specific exceptions** — only retry on expected transient errors, not logic errors.
4. **Re-raise on final attempt** — don't swallow the error silently.

**How to think through this:**
1. Three levels: factory(config) → decorator(func) → wrapper(call).
2. Loop up to max_attempts. On the last attempt, re-raise.
3. Exponential backoff: `base * 2^(attempt-1)`.

**Key takeaway:** Retry with exponential backoff + jitter is the industry standard for transient failures — always specify which exceptions to retry and re-raise after max attempts.

</details>

> 📖 **Theory:** [Retry Pattern](./16_design_patterns/theory.md)

---

### Q89 · [Design] · `pipeline-scenario`

> **You have a large file (10GB) of log lines. You need to filter lines containing "ERROR", parse each into a dict, and write the results to a new file. How do you do this without loading the whole file into memory?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Use a **generator pipeline** — each stage processes one line at a time:

```python
import json

def read_lines(filepath):
    with open(filepath) as f:
        yield from f            # one line at a time

def filter_errors(lines):
    for line in lines:
        if "ERROR" in line:
            yield line

def parse_log(lines):
    for line in lines:
        parts = line.strip().split(" | ")
        yield {
            "timestamp": parts[0],
            "level": parts[1],
            "message": parts[2] if len(parts) > 2 else ""
        }

def write_results(records, output_path):
    with open(output_path, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

# Pipeline — memory usage = O(1) regardless of file size
lines = read_lines("app.log")
errors = filter_errors(lines)
records = parse_log(errors)
write_results(records, "errors.jsonl")
```

At any moment, only one line is in memory. This handles a 10TB file just as well as a 10GB file.

**How to think through this:**
1. Generator pipeline: each function takes an iterable and yields processed items.
2. No stage buffers the full dataset — values flow through one at a time.
3. Composition is lazy — nothing runs until `write_results` starts iterating.

**Key takeaway:** Generator pipelines process arbitrarily large data in O(1) memory — chain `yield from` stages for clean, composable data processing.

</details>

> 📖 **Theory:** [Generator Pipeline](./11_generators_iterators/theory.md#chapter-8-generator-pipelines--streaming-etl)

---

### Q90 · [Design] · `thread-safe-counter`

> **Two threads increment a shared counter 100,000 times each. Without any synchronisation, the final count is often less than 200,000. Why? How do you fix it?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Why it happens — race condition:**
`counter += 1` is NOT atomic. It compiles to three bytecode instructions:
1. `LOAD` — read current value of `counter`
2. `BINARY_ADD` — compute value + 1
3. `STORE` — write back

The GIL can switch threads between any two of these steps. Thread A reads `counter = 5`, then Thread B also reads `counter = 5`, both compute 6, both store 6. One increment is lost.

**Fix — use a threading.Lock:**
```python
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(100000):
        with lock:
            counter += 1
```

**Alternative — use `threading.local` if each thread needs its own count, or use `queue.Queue` for producer-consumer patterns.**

For a simpler counter without explicit locks, use `threading.Semaphore` or atomic types from the `atomics` library.

**How to think through this:**
1. Read-modify-write operations are never atomic unless explicitly protected.
2. The GIL helps (bytecode can't interleave mid-operation), but `+=` spans multiple bytecodes.
3. `Lock` ensures only one thread is in the critical section at a time.

**Key takeaway:** `counter += 1` is not thread-safe despite the GIL — always protect shared mutable state with `threading.Lock`.

</details>

> 📖 **Theory:** [Thread-Safe Counter](./13_concurrency/theory.md#regular-lock-deadlocks-if-the-same-thread-tries-to-acquire-it-twice)

---

## Tier 5 — Critical Thinking · Q91–Q100

> No hints. Think it through. These test whether you can reason, not just recall.

---

### Q91 · [Logical] · `predict-output-scope`

> **What does this print? Think carefully about scope.**

```python
x = 10

def foo():
    print(x)
    x = 20

foo()
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
UnboundLocalError: local variable 'x' referenced before assignment
```

This is one of Python's most surprising scope rules. Because `x = 20` appears anywhere in the function body, Python marks `x` as a **local variable** for the entire function — even before the assignment. So `print(x)` tries to read a local `x` that hasn't been assigned yet.

Python determines scope at compile time, not at runtime. The presence of `x = 20` makes `x` local throughout `foo`, even on the line before the assignment.

**Fix:**
```python
x = 10
def foo():
    global x     # or: read without assigning (no x = 20)
    print(x)
    x = 20
```

**How to think through this:**
1. Python scans the function body at compile time: "does this function assign to `x`?"
2. Answer: yes (`x = 20`). Therefore `x` is local throughout the function.
3. At runtime, `print(x)` tries to read local `x` before it's been assigned → `UnboundLocalError`.

**Key takeaway:** If a function assigns to a variable anywhere in its body, Python treats it as local throughout — even lines before the assignment. Use `global` or `nonlocal` to refer to outer scope variables you also assign.

</details>

> 📖 **Theory:** [Scope Prediction](./04_functions/theory.md#chapter-6--scope--the-legb-rule)

---

### Q92 · [Logical] · `predict-output-class`

> **What does this print?**

```python
class A:
    def method(self):
        return "A"

class B(A):
    pass

class C(A):
    def method(self):
        return "C"

class D(B, C):
    pass

print(D().method())
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
C
```

MRO for D: `D → B → C → A → object`. Python's C3 linearisation places B before C (left-to-right), then C before their common ancestor A.

`D` has no `method`. `B` has no `method`. `C` has `method` → Python finds it here and returns `"C"`.

Check: `print(D.__mro__)` → `(<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)`

**How to think through this:**
1. Build the MRO: D first, then left parent (B), then right parent (C), then common ancestor (A).
2. Search the MRO left to right for `method`.
3. B doesn't define it, C does → return "C".

**Key takeaway:** MRO is left-to-right, depth-first, with each class appearing only once. When in doubt: `ClassName.__mro__`.

</details>

> 📖 **Theory:** [Class Variables](./05_oops/theory_part2.md)

---

### Q93 · [Logical] · `predict-output-generator`

> **What does this print and why?**

```python
def gen():
    yield 1
    yield 2
    yield 3

g = gen()
print(list(g))
print(list(g))
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```
[1, 2, 3]
[]
```

The first `list(g)` consumes all values from the generator. Once a generator is exhausted, it raises `StopIteration` immediately on the next call. The second `list(g)` sees an already-exhausted generator and immediately gets an empty sequence.

Generators are **single-pass** — you cannot reset or rewind them. To iterate twice, you either:
1. Recreate the generator: `g2 = gen()`
2. Store results in a list first: `values = list(gen()); list(values); list(values)` (both work)
3. Use `itertools.tee()` (creates two independent iterators from one, but buffers internally)

**How to think through this:**
1. `list(g)` calls `next(g)` until `StopIteration` — exhausts `g`.
2. After that, `g` is spent. The generator function has returned.
3. `list(g)` again → immediately gets `StopIteration` → empty list.

**Key takeaway:** Generators are single-use. Once exhausted, they return nothing — you must create a new generator to iterate again.

</details>

> 📖 **Theory:** [Generator Output](./11_generators_iterators/theory.md#chapter-3-generator-functions--yield)

---

### Q94 · [Debug] · `debug-decorator`

> **This decorator is broken — it does not preserve the original function's name or docstring. Fix it.**

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("calling")
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet():
    """Says hello."""
    print("hello")

print(greet.__name__)
print(greet.__doc__)
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Currently prints:
```
wrapper
None
```

Fix — add `@functools.wraps(func)`:
```python
import functools

def my_decorator(func):
    @functools.wraps(func)    # ← this line fixes it
    def wrapper(*args, **kwargs):
        print("calling")
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet():
    """Says hello."""
    print("hello")

print(greet.__name__)   # greet
print(greet.__doc__)    # Says hello.
```

`functools.wraps` copies `__name__`, `__doc__`, `__module__`, `__qualname__`, `__annotations__`, and `__dict__` from `func` to `wrapper`. It also sets `wrapper.__wrapped__ = func`.

**How to think through this:**
1. `@my_decorator` replaces `greet` with `wrapper`. `wrapper.__name__` is `"wrapper"` by default.
2. `@functools.wraps(func)` copies the original function's metadata to the wrapper.
3. This is why every decorator tutorial ends with "always add `@functools.wraps`."

**Key takeaway:** Every decorator wrapper must have `@functools.wraps(func)` — it is a one-line fix that prevents confusing bugs in logging, testing, and documentation.

</details>

> 📖 **Theory:** [Decorator Debug](./10_decorators/theory.md#decorators--theory)

---

### Q95 · [Debug] · `debug-thread-race`

> **This code has a race condition. Identify exactly where the race occurs and fix it.**

```python
import threading

counter = 0

def increment():
    global counter
    for _ in range(100000):
        counter += 1

threads = [threading.Thread(target=increment) for _ in range(2)]
for t in threads: t.start()
for t in threads: t.join()
print(counter)
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The race condition is in `counter += 1`. This decompiles to:
1. `LOAD_GLOBAL counter` — read current value
2. `LOAD_CONST 1`
3. `BINARY_ADD` — compute sum
4. `STORE_GLOBAL counter` — write back

The GIL can switch between threads between instructions 1 and 4. Both threads can read the same value, add 1, and both write back the same result — losing one increment.

**Fix:**
```python
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(100000):
        with lock:
            counter += 1

threads = [threading.Thread(target=increment) for _ in range(2)]
for t in threads: t.start()
for t in threads: t.join()
print(counter)  # always 200000
```

**How to think through this:**
1. `+=` = read → compute → write. Three steps the GIL can interrupt between.
2. Lock ensures only one thread executes the critical section at a time.
3. `with lock:` is cleaner than `lock.acquire()/release()` — guarantees release even on exception.

**Key takeaway:** Any read-modify-write operation on shared state requires a lock — even `+= 1` is not atomic.

</details>

> 📖 **Theory:** [Thread Race Debug](./13_concurrency/theory.md#another-thread-can-run-between-load-and-store--race-condition)

---

### Q96 · [Debug] · `debug-generator-send`

> **This code raises a TypeError. Why? Fix it.**

```python
def accumulator():
    total = 0
    while True:
        value = yield total
        total += value

gen = accumulator()
print(gen.send(10))
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The error is: `TypeError: can't send non-None value to a just-started generator`

A generator must be **primed** with `next()` (or `send(None)`) before you can send a non-None value. The generator needs to run up to the first `yield` before it can receive a sent value.

**Fix:**
```python
def accumulator():
    total = 0
    while True:
        value = yield total
        total += value

gen = accumulator()
print(next(gen))       # prime: runs to first yield, outputs 0
print(gen.send(10))    # sends 10, value=10, total=10, yields 10
print(gen.send(5))     # sends 5, value=5, total=15, yields 15
```

Or wrap the generator in a helper that auto-primes:
```python
def primed(gen_func):
    @functools.wraps(gen_func)
    def wrapper(*args, **kwargs):
        g = gen_func(*args, **kwargs)
        next(g)
        return g
    return wrapper

@primed
def accumulator(): ...
```

**How to think through this:**
1. A fresh generator hasn't started — there is no `yield` expression waiting to receive a value.
2. `next(gen)` advances to the first `yield`, which can now receive a `send`.
3. `send(None)` is equivalent to `next()` and is also valid for priming.

**Key takeaway:** Before `send(value)`, always prime the generator with `next()` or `send(None)` — the generator must be positioned at a yield expression to receive a value.

</details>

> 📖 **Theory:** [Generator send() Debug](./11_generators_iterators/theory.md#chapter-7-send--generators-as-coroutines)

---

### Q97 · [Design] · `design-decision-cache`

> **You need to cache results of a function. You have three options: (1) `@functools.lru_cache`, (2) a manual dict cache, (3) Redis. Walk through when you would pick each and what factors drive the decision.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The decision hinges on four questions:
1. **Does the cache need to survive process restarts?**
2. **Does the cache need to be shared across multiple processes or servers?**
3. **Do cache entries need to expire (TTL)?**
4. **How complex is the cache key?**

**`@functools.lru_cache`** — choose when:
- Same process, in-memory, function is pure (deterministic).
- No TTL needed. No multi-process sharing needed.
- Arguments are hashable.
- Zero infrastructure — one decorator, done.
```python
@lru_cache(maxsize=512)
def compute(n): ...
```

**Manual dict cache** — choose when:
- Need TTL: store `(value, expiry_timestamp)` and check on get.
- Need custom eviction logic (LRU, LFU, size-based).
- Need to inspect or clear the cache programmatically.
- Cache key involves non-hashable arguments (convert to a tuple/string).

**Redis** — choose when:
- Cache must be shared across multiple API servers (horizontal scaling).
- Cache must survive process restarts.
- Need atomic operations (e.g. rate limiting with `INCR`).
- Need distributed TTL management.
- Need cache size control across the whole system.

**How to think through this:**
1. Start with `lru_cache` — it costs nothing and solves 80% of cases.
2. If you need TTL → manual dict.
3. If you need multi-process/multi-server or persistence → Redis.

**Key takeaway:** `lru_cache` → simplest. Manual dict → control. Redis → distributed. Choose the simplest option that satisfies your constraints.

</details>

> 📖 **Theory:** [Cache Design Decision](./18_performance_optimization/profiling.md)

---

### Q98 · [Design] · `design-decision-inheritance`

> **You are designing a system with `Dog`, `Cat`, and `Bird` classes. All can `eat()` and `sleep()`, but only `Dog` and `Bird` can `fetch()`, and only `Bird` can `fly()`. Design the class hierarchy — what do you inherit, what do you use mixins for, and what do you compose?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
class Animal:
    def eat(self): ...
    def sleep(self): ...

class FetchMixin:
    def fetch(self): ...

class FlyMixin:
    def fly(self): ...

class Dog(FetchMixin, Animal): pass
class Cat(Animal): pass
class Bird(FlyMixin, FetchMixin, Animal): pass
```

**Design rationale:**
- `Animal` is the base for all — `eat` and `sleep` are universal.
- `fetch` and `fly` are cross-cutting capabilities that don't fit a single-inheritance chain. Mixins provide them without creating false "is-a" relationships.
- `Dog IS-A Animal that CAN fetch` → mixin is correct.
- Avoid: `class Fetcher(Animal)` with `Dog(Fetcher)` and `Bird(Fetcher)` — this creates a deep hierarchy and forces `Bird` into `Fetcher` which implies it's primarily a fetching animal.

**Alternatives and tradeoffs:**
- Composition: give each animal a set of `capabilities = {Fetch(), Fly()}`. More flexible, less Pythonic for simple cases.
- Protocol: define `Fetchable` and `Flyable` protocols for type-safe duck typing.

**How to think through this:**
1. Shared universal behaviour → base class.
2. Behaviour shared by some but not all, cutting across the hierarchy → mixin.
3. Behaviour owned by a contained object → composition.

**Key takeaway:** Use mixins for cross-cutting capabilities (things some subclasses can do), base classes for fundamental "is-a" identity, and composition for "has-a" relationships.

</details>

> 📖 **Theory:** [Inheritance vs Composition](./05_oops/theory_part2.md)

---

### Q99 · [Critical] · `open-ended-logging`

> **Write a production-grade logging setup for a Python application. It should: log to both console and a rotating file, include timestamps and log levels, not break if the log directory doesn't exist, and be importable from any module. No starter code — design it from scratch.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
# logger.py — import this from any module
import logging
import logging.handlers
from pathlib import Path

def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger   # avoid adding duplicate handlers on re-import

    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler — INFO and above
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)
    logger.addHandler(console)

    # File handler — DEBUG and above, rotating
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)   # create if missing

    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,   # 10MB per file
        backupCount=5                 # keep last 5 rotated files
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger


# Usage in any module:
# from logger import get_logger
# log = get_logger(__name__)
# log.info("Server started")
# log.error("Something failed", exc_info=True)
```

Key decisions:
1. `if logger.handlers: return logger` — prevents duplicate handlers when module is imported multiple times.
2. `Path.mkdir(exist_ok=True)` — silently creates the log directory.
3. `RotatingFileHandler` — caps file size, keeps history.
4. Different log levels per handler — verbose to file, clean to console.
5. `%(name)s` in format — shows which module logged the message.

**How to think through this:**
1. What handlers do I need? Console + rotating file.
2. What format? Timestamp + level + module + message.
3. What safety checks? Dir creation, duplicate handler guard.
4. How to share? Module-level function returning a named logger.

**Key takeaway:** Production logging needs: formatter with timestamp, rotating file handler, console handler at INFO, idempotent setup (check handlers before adding), and automatic directory creation.

</details>

> 📖 **Theory:** [Logging System](./07_modules_packages/theory.md#initialize-logging-for-the-whole-package)

---

### Q100 · [Critical] · `open-ended-system`

> **Design a Python class that behaves like a dictionary but automatically expires keys after a TTL (time-to-live) in seconds. It should support `set(key, value, ttl)`, `get(key)`, and `delete(key)`. Keys that have expired should return `None` on `get`. No external libraries. Think through the full implementation before writing any code.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
import time
from threading import Lock
from typing import Any, Optional

class TTLCache:
    """
    Dict-like cache where entries expire after their individual TTL.
    Thread-safe for concurrent reads and writes.
    """

    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}
        # value: (data, expiry_timestamp)
        self._lock = Lock()

    def set(self, key: str, value: Any, ttl: float) -> None:
        expiry = time.monotonic() + ttl
        with self._lock:
            self._store[key] = (value, expiry)

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._store:
                return None
            value, expiry = self._store[key]
            if time.monotonic() > expiry:
                del self._store[key]   # lazy expiry
                return None
            return value

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def cleanup(self) -> int:
        """Remove all expired keys. Returns count of removed keys."""
        now = time.monotonic()
        with self._lock:
            expired = [k for k, (_, exp) in self._store.items() if now > exp]
            for k in expired:
                del self._store[k]
        return len(expired)

    def __len__(self) -> int:
        self.cleanup()
        return len(self._store)


# Usage
cache = TTLCache()
cache.set("token", "abc123", ttl=60)
print(cache.get("token"))   # "abc123"
time.sleep(61)
print(cache.get("token"))   # None — expired
```

**Design decisions explained:**
1. **`time.monotonic()`** not `time.time()` — monotonic clock never goes backward (safe against system clock adjustments).
2. **Lazy expiry** in `get()` — no background thread needed. Expired items are removed on next access.
3. **`cleanup()` method** — allows explicit purging of expired keys to prevent unbounded memory growth.
4. **Lock on all operations** — prevents race conditions in multi-threaded use.
5. **`store.pop(key, None)`** in delete — no KeyError if key doesn't exist.

**Trade-offs:**
- Lazy expiry means expired items occupy memory until accessed — add a background cleanup thread for long-lived caches.
- For high-concurrency, consider per-shard locks.
- Production use: prefer Redis with its native TTL support.

**How to think through this:**
1. What data structure? Dict mapping key → (value, expiry_time).
2. When to expire? On access (lazy) — simplest, no background thread.
3. How to handle concurrency? Lock on get/set/delete.
4. What clock? `time.monotonic()` for correctness.

**Key takeaway:** TTL cache = dict storing (value, expiry). Lazy expiry on read is the simplest approach. Add a cleanup thread for memory-bounded caches. Thread safety requires a lock on all mutations.

</details>

> 📖 **Theory:** [System Design](./16_design_patterns/theory.md#design-patterns-in-python)

---

*100 questions complete · Python-DSA-API-Mastery · Last updated: 2026-04-23*
