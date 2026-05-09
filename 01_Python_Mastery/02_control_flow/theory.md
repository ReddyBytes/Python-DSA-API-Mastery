<a id="top"></a>
# 🔁 Control Flow in Python

> Control flow decides HOW your program thinks.
> Not what it stores. Not how it looks.
> But how it makes decisions.

If memory is about storage,
control flow is about intelligence.

This chapter builds decision-making ability into your programs.

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [Big Picture: What is Control Flow?](#big-picture-what-is-control-flow)
- [Default Execution Flow](#default-execution-flow)
- [1. Conditional Statements (Decision Making)](#1-conditional-statements-decision-making)
  - [if Statement](#if-statement)
  - [if-else](#if-else)
  - [if-elif-else](#if-elif-else)
- [2. Nested Conditions](#2-nested-conditions)
  - [Guard Clauses — Flatten Nesting](#guard-clauses)
- [3. Ternary Operator (Inline Condition)](#3-ternary-operator-inline-condition)
- [4. match-case (Python 3.10+)](#4-match-case-python-310)
  - [OR Patterns and Guards](#or-patterns-and-guards)
  - [Structural Pattern Matching](#structural-pattern-matching)
- [5. Walrus Operator :=](#5-walrus-operator)
- [6. Loops (Repetition)](#6-loops-repetition)
  - [for Loop](#for-loop)
  - [range() Variants](#range-variants)
  - [Iterating Dictionaries](#iterating-dictionaries)
  - [while Loop](#while-loop)
  - [break Statement](#break-statement)
  - [continue Statement](#continue-statement)
  - [pass Statement](#pass-statement)
  - [Loop else (Advanced & Rarely Understood)](#loop-else)
- [7. enumerate()](#7-enumerate)
- [8. zip()](#8-zip)
  - [zip Recipes](#zip-recipes)
- [9. Comprehensions (Controlled Expression Loops)](#9-comprehensions)
  - [Comprehension Scoping — Variables Don't Leak](#comprehension-scoping)
  - [Generator Expressions — Lazy Comprehensions](#generator-expressions)
- [Real-World Production Thinking](#real-world-production-thinking)
- [Truthy and Falsy (Important for Interviews)](#truthy-and-falsy)
  - [Short-Circuit Evaluation](#short-circuit-evaluation)
- [Common Mistakes](#common-mistakes)
- [Interview Questions](#interview-questions)
- [Final Mental Model](#final-mental-model)
- [The random Module — Adding Chance to Your Code](#the-random-module)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`if`/`elif`/`else` · `for` loop · `while` loop · `break` / `continue` / `pass` / `else` on loops · List/dict/set comprehensions · Truthy and falsy · Guard clauses

**Should Learn** — Important for real projects, comes up regularly:
Walrus operator `:=` · `match`/`case` pattern matching · Short-circuit evaluation · `enumerate()` · `zip()` · Generator expressions

**Good to Know** — Useful in specific situations:
Comprehension scoping rules · `reversed()` · Ternary expression · Structural pattern matching · `zip_longest`

**Reference** — Know it exists, look up when needed:
`itertools` (covered in generators module)

<a id="big-picture-what-is-control-flow"></a>
# 🧠 Big Picture: What is Control Flow?

Control Flow means: the order in which statements execute in a program.

By default, Python runs top → bottom.

But real programs don't work linearly. They:
- Make decisions
- Repeat tasks
- Break early
- Skip steps
- Handle unexpected errors

```
Top-down (default)        With control flow

  line 1                    line 1
  line 2                    line 2
  line 3                    if condition?
  line 4                      yes → line 3a
  line 5                      no  → line 3b
                            line 4
                            loop → line 5 (repeated)
```

> [↑ Back to Top](#top)

<a id="default-execution-flow"></a>
# 🛣 Default Execution Flow

```python
print("Start")
print("Processing")
print("End")
```

Flow:

```
Start
  ↓
Processing
  ↓
End
```

Simple. Top to bottom.

Now let's make it intelligent.

> [↑ Back to Top](#top)

<a id="1-conditional-statements-decision-making"></a>
# 1. Conditional Statements (Decision Making)

<a id="if-statement"></a>
## if Statement

Imagine a 10-year-old: "If it rains, take umbrella."

That's an `if` statement.

```python
age = 18

if age >= 18:
    print("You can vote")
```

Flow:

```
Check condition
      |
      v
Is True?
  /       \
Yes        No
 |          |
Run block   Skip block
```

- Condition must evaluate to True or False.
- Indentation defines the block.

> 📝 **Practice:** [Q1 — Age Check](./practice.md#q1--if-statement--age-check) · [Q2 — Password Check](./practice.md#q2--if-statement--password-check) · [Q3 — Multiple Conditions](./practice.md#q3--if-statement--multiple-conditions)

<a id="if-else"></a>
## if-else

```python
age = 16

if age >= 18:
    print("You can vote")
else:
    print("You cannot vote")
```

Flow:

```
Condition?
   |
True? ---- Yes → Block A
   |
   No → Block B
```

Only one block runs.

> 📝 **Practice:** [Q4 — Even or Odd](./practice.md#q4--if-else--even-or-odd) · [Q5 — Temperature](./practice.md#q5--if-else--temperature) · [Q6 — Positive or Negative](./practice.md#q6--if-else--positive-or-negative)

<a id="if-elif-else"></a>
## if-elif-else

Used when multiple conditions exist.

```python
marks = 75

if marks >= 90:
    print("A")
elif marks >= 75:
    print("B")
elif marks >= 50:
    print("C")
else:
    print("Fail")
```

Flow:

```
Condition 1?
   |
True → Stop, run block
   |
False
   ↓
Condition 2?
   |
True → Stop, run block
   |
False
   ↓
...
   ↓
else block
```

Python stops at the first `True` condition.

Professional tip: place most specific conditions first.

> 📝 **Practice:** [Q7 — Grade Checker](./practice.md#q7--if-elif-else--grade-checker) · [Q8 — Day Name](./practice.md#q8--if-elif-else--day-name) · [Q9 — Positive/Negative/Zero](./practice.md#q9--if-elif-else--positive--negative--zero)

> [↑ Back to Top](#top)

<a id="2-nested-conditions"></a>
# 2. Nested Conditions

You can place `if` inside another `if`.

```python
age = 25
citizen = True

if age >= 18:
    if citizen:
        print("Eligible to vote")
```

Flow:

```
Check age
   |
age >= 18?
   |
  True
   |
Check citizenship
   |
citizen?
   |
  True
   |
Eligible
```

Avoid too much nesting — it reduces readability and is a known code smell.

**When deep nesting becomes a problem:**

```python
# Hard to follow — 3 levels deep
def process_order(order):
    if order is not None:
        if order.is_paid:
            if order.has_stock:
                ship(order)
            else:
                print("Out of stock")
        else:
            print("Not paid")
    else:
        print("No order")
```

This is the **arrow anti-pattern** — code drifts right and becomes unreadable.

> 📝 **Practice:** [Q10 — Voter Eligibility](./practice.md#q10--nested-conditions--voter-eligibility) · [Q11 — Login + Role](./practice.md#q11--nested-conditions--login--role)

<a id="guard-clauses"></a>
## Guard Clauses — Flatten Nesting

A **guard clause** checks failure conditions first and returns early. The happy path runs at the bottom, un-nested.

Think of it as a bouncer at the door: reject the invalid cases first, so the rest of the function deals only with valid input.

```python
# Same logic as above — but flat:
def process_order(order):
    if order is None:
        print("No order")
        return

    if not order.is_paid:
        print("Not paid")
        return

    if not order.has_stock:
        print("Out of stock")
        return

    ship(order)   # ← happy path — no nesting
```

```
Guard clause pattern:

  check failure condition 1? → return early
  check failure condition 2? → return early
  check failure condition 3? → return early
  ...
  [happy path — runs here, un-nested]
```

Why guard clauses are the professional choice:
- Each failure condition is isolated and easy to read
- The happy path is at the same indent level as everything else
- Adding a new condition means adding one more guard — not going deeper
- Easier to test each branch independently

**Common mistake:** Nesting `if` blocks instead of using early returns.

```python
# Wrong:
def validate_age(age):
    if isinstance(age, int):
        if age >= 0:
            if age <= 150:
                return True
    return False

# Right:
def validate_age(age):
    if not isinstance(age, int):
        return False
    if age < 0:
        return False
    if age > 150:
        return False
    return True
```

> [↑ Back to Top](#top)

<a id="3-ternary-operator-inline-condition"></a>
# 3. Ternary Operator (Inline Condition)

Short-hand decision — value A if condition else value B:

```python
age = 20
status = "Adult" if age >= 18 else "Minor"
```

```
status = "Adult" if age >= 18 else "Minor"
          |              |              |
        value A       condition      value B
     (when True)                  (when False)
```

Readable when simple. Avoid complex nested ternaries.

> 📝 **Practice:** [Q12 — Even/Odd one-liner](./practice.md#q12--ternary-operator--evenodd-one-liner) · [Q13 — Max of Two](./practice.md#q13--ternary-operator--max-of-two)

> [↑ Back to Top](#top)

<a id="4-match-case-python-310"></a>
# 4. match-case (Python 3.10+)

Cleaner alternative to multiple `elif` when matching against specific values.

```python
day = "Monday"

match day:
    case "Monday":
        print("Start of week")
    case "Friday":
        print("Weekend coming")
    case _:
        print("Regular day")
```

```
match day:
   │
   ├── "Monday"  → "Start of week"
   ├── "Friday"  → "Weekend coming"
   └── _         → "Regular day"  (wildcard — matches anything)
```

Use when:
- Matching specific values
- Cleaner than many `elif`

Not a replacement for all if-else logic — `match-case` matches patterns/values, `if-else` evaluates arbitrary conditions.

> 📝 **Practice:** [Q14 — HTTP Status](./practice.md#q14--match-case--http-status)

<a id="or-patterns-and-guards"></a>
## OR Patterns and Guards

**OR patterns** — match multiple values with `|`:

```python
day = "Saturday"

match day:
    case "Monday" | "Tuesday" | "Wednesday" | "Thursday" | "Friday":
        print("Weekday")
    case "Saturday" | "Sunday":
        print("Weekend")
    case _:
        print("Unknown")
```

**Guards** — add an `if` condition after a case:

```python
score = 87

match score:
    case n if n >= 90:
        print("A")
    case n if n >= 75:
        print("B")
    case n if n >= 50:
        print("C")
    case _:
        print("Fail")
```

The variable `n` captures the matched value, and the guard `if n >= 90` is an additional filter. Equivalent to `elif` but reads naturally inside a match block.

<a id="structural-pattern-matching"></a>
## Structural Pattern Matching

`match-case` can also **match against the structure** of a value — not just its value. This is where it goes beyond `if-elif`.

**Matching sequences (lists/tuples):**

```python
point = (1, 0)

match point:
    case (0, 0):
        print("Origin")
    case (x, 0):
        print(f"On X-axis at {x}")   # x is captured
    case (0, y):
        print(f"On Y-axis at {y}")   # y is captured
    case (x, y):
        print(f"Point at ({x}, {y})")
```

```
point = (1, 0)
   │
   ├── (0, 0)? No
   ├── (x, 0)? Yes — x captures 1 → "On X-axis at 1"
   └── done
```

**Matching dicts:**

```python
command = {"action": "move", "direction": "north"}

match command:
    case {"action": "move", "direction": direction}:
        print(f"Moving {direction}")
    case {"action": "attack", "target": target}:
        print(f"Attacking {target}")
    case _:
        print("Unknown command")
```

Dict patterns check that the keys exist and match — extra keys are allowed and ignored.

```
Structural match-case:             if-elif:
  matching exact values/shapes       arbitrary conditions
  multiple values per case (|)       computed expressions
  capturing sub-values               complex boolean logic
  readable for protocol dispatch     simpler for 1-2 conditions
```

> [↑ Back to Top](#top)

<a id="5-walrus-operator"></a>
# 5. Walrus Operator :=

Python 3.8 introduced the **walrus operator** `:=` — officially called an **assignment expression**.

It assigns a value AND returns it in a single expression. This eliminates computing the same value twice.

```
Without walrus:              With walrus:
data = get_data()            if (n := len(data)) > 10:
if len(data) > 10:               print(n, "items")
    print(len(data), "items")
                             # len() called ONCE, n reused
```

```
(n := len(data)) > 10
  │      │           │
  │   expression     │
  │   evaluates to   comparison
  │   len(data)
  │
  assigns to n (and returns value)
```

**Where it genuinely helps:**

```python
# 1 — while loops reading chunks:
import io
f = io.BytesIO(b"hello world data")
while chunk := f.read(4):          # assign + check in one step
    process(chunk)

# 2 — filtering with computed value (avoid double call):
results = [y for x in data if (y := expensive(x)) > 0]

# 3 — regex match + use:
import re
text = "Order: 12345"
if m := re.search(r"\d+", text):
    print(f"Found: {m.group()}")   # m already bound, no second search
```

**The rule:** Use walrus when you'd otherwise compute the same value twice.
Don't use it just to be clever — if it makes code harder to read, use two lines.

> 📝 **Practice:** [Q15 — Length Check](./practice.md#q15--walrus-operator--length-check)

> [↑ Back to Top](#top)

<a id="6-loops-repetition"></a>
# 6. Loops (Repetition)

Loops repeat code. Two core types: `for` and `while`. Both support `break`, `continue`, `pass`, and `else` — they all live in the world of loops.

```
for loop                     while loop
────────────────             ────────────────────
iterate a sequence           repeat until condition False
knows when to stop           YOU define the stop condition
```

<a id="for-loop"></a>
## for Loop

Used for iterating over sequences.

```python
for i in range(5):
    print(i)
```

Flow:

```
Start
  ↓
Get next item from sequence
  ↓
Run loop body
  ↓
More items?
  /     \
Yes      No
 |        |
Repeat    Exit loop
```

Used with: lists · tuples · strings · dictionaries · sets · [generators](../11_generators_iterators/theory.md#-chapter-3-generator-functions--yield)

> 📝 **Practice:** [Q16 — Print 1 to 10](./practice.md#q16--for-loop--print-1-to-10) · [Q17 — Sum of a List](./practice.md#q17--for-loop--sum-of-a-list) · [Q18 — Even Numbers Only](./practice.md#q18--for-loop--even-numbers-only)

<a id="range-variants"></a>
## range() Variants

`range()` generates a sequence of integers. Three forms:

```python
range(stop)              # 0 to stop-1
range(start, stop)       # start to stop-1
range(start, stop, step) # start to stop-1, step at a time
```

```python
range(5)          # 0, 1, 2, 3, 4
range(2, 8)       # 2, 3, 4, 5, 6, 7
range(0, 10, 2)   # 0, 2, 4, 6, 8       (even numbers)
range(10, 0, -1)  # 10, 9, 8, 7, ... 1  (count down)
range(5, 0, -1)   # 5, 4, 3, 2, 1
```

```
range(start=0, stop=10, step=2):

  0 ──(+2)──► 2 ──(+2)──► 4 ──(+2)──► 6 ──(+2)──► 8  →  stop (10 not included)
```

`range()` is **lazy** — it doesn't generate all values at once. Even `range(10_000_000)` uses the same tiny amount of memory as `range(5)`.

```python
# Iterate backwards:
for i in range(len(items)-1, -1, -1):
    print(items[i])

# Every other item:
for i in range(0, len(items), 2):
    print(items[i])
```

<a id="iterating-dictionaries"></a>
## Iterating Dictionaries

A dictionary gives you three ways to iterate:

```python
person = {"name": "Alice", "age": 30, "city": "NYC"}

# Keys only (default):
for key in person:
    print(key)        # name, age, city

# Values only:
for value in person.values():
    print(value)      # Alice, 30, NYC

# Keys AND values together:
for key, value in person.items():
    print(key, "→", value)
    # name → Alice
    # age  → 30
    # city → NYC
```

```
person.items() produces:
  ("name",  "Alice")
  ("age",   30)
  ("city",  "NYC")

for key, value in person.items():
   ↑     ↑
   unpacks each tuple automatically
```

**Common mistake:** Modifying a dict while iterating raises `RuntimeError`. Iterate over a copy instead:

```python
# Wrong:
for key in d:
    if condition(key):
        del d[key]    # RuntimeError: dictionary changed size during iteration

# Right:
for key in list(d.keys()):   # snapshot of keys
    if condition(key):
        del d[key]
```

<a id="while-loop"></a>
## while Loop

Runs until condition becomes False.

```python
count = 0

while count < 5:
    print(count)
    count += 1
```

Flow:

```
Check condition
   |
Condition True?
  /           \
Yes            No → exit loop
 |
Run body
 |
Back to condition check
```

Danger: infinite loop if condition never becomes False.

> 📝 **Practice:** [Q19 — Countdown](./practice.md#q19--while-loop--countdown) · [Q21 — Repeat Until Valid](./practice.md#q21--while-loop--repeat-until-valid)

<a id="break-statement"></a>
## break Statement

Stops the loop immediately — exits and continues after the loop.

```python
for i in range(10):
    if i == 5:
        break
    print(i)
# prints 0, 1, 2, 3, 4 — stops at 5
```

Used when: early exit needed · search result found · error condition met

**Breaking out of nested loops:**

`break` only exits the **innermost** loop it's in.

```python
for i in range(3):
    for j in range(3):
        if j == 1:
            break           # exits j loop only — i loop continues
    print(f"i={i}")         # prints i=0, i=1, i=2
```

```
Outer loop (i):  0 ──────────────────────────────────► 1 ──────────────────────────────────► 2
                  │                                      │                                      │
Inner loop (j):  0 → 1 → break                         0 → 1 → break                         0 → 1 → break
                      ↑                                      ↑                                      ↑
                  exits inner only                      exits inner only                      exits inner only
```

**Pattern 1 — flag variable:**

```python
found = False
for i in range(rows):
    for j in range(cols):
        if grid[i][j] == target:
            found = True
            break
    if found:
        break
```

**Pattern 2 — function with `return`** *(covered in Module 04 — Functions)*

```python
def find_in_grid(grid, target):
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == target:
                return (i, j)   # return exits ALL loops at once
    return None
```

`return` is the cleanest way to break out of all nested loops.

> 📝 **Practice:** [Q22 — Find First Negative](./practice.md#q22--break--find-first-negative) · [Q23 — Stop at Keyword](./practice.md#q23--break--stop-at-keyword)

<a id="continue-statement"></a>
## continue Statement

Skips the rest of the current iteration and jumps to the next one.

```python
for i in range(5):
    if i == 2:
        continue    # skip i==2, go to i==3
    print(i)
# prints 0, 1, 3, 4 — 2 is skipped
```

Flow:

```
Get next item
      ↓
condition True?
  /           \
Yes            No
 │              │
continue        run body
(jump to        (print i)
 next item)
      │
      └──────────────────────► Get next item
```

```
i=0: print 0          ✓
i=1: print 1          ✓
i=2: continue hit     ↩ skip to next
i=3: print 3          ✓
i=4: print 4          ✓
```

> 📝 **Practice:** [Q24 — Skip Negatives](./practice.md#q24--continue--skip-negatives) · [Q21 — Repeat Until Valid](./practice.md#q21--while-loop--repeat-until-valid)

<a id="pass-statement"></a>
## pass Statement

Does nothing. Used as a placeholder when a statement is syntactically required but you have no code yet.

```python
if True:
    pass       # valid — Python needs at least one statement in a block

class Empty:
    pass       # valid empty class

def future_feature():
    pass       # placeholder — implement later
```

Useful in: empty functions · class definitions · future implementations

> 📝 **Practice:** [Q26 — Placeholder](./practice.md#q26--pass--placeholder)

<a id="loop-else"></a>
## Loop else (Advanced & Rarely Understood)

Python's `else` on a loop runs **only if the loop completed without hitting `break`**.

```python
for i in range(5):
    if i == 10:
        break
else:
    print("Loop completed normally")   # prints — no break was hit
```

```
Loop starts
    │
    ├── iteration runs
    │
    ├── break hit?
    │     │
    │   Yes → EXIT (skip else)
    │
    └── No break → loop finishes naturally
                        │
                    else block runs
```

Real use — search loop:

```python
# Did we find the target?
for item in collection:
    if item == target:
        print("Found!")
        break
else:
    print("Not found")   # only runs if loop finished without break
```

```
break hit         →  "Found!"   (else skipped)
loop exhausted    →  "Not found" (else runs)
```

This is cleaner than a flag variable:

```python
# Without loop else (needs flag):
found = False
for item in collection:
    if item == target:
        found = True
        break
if not found:
    print("Not found")

# With loop else (no flag needed):
for item in collection:
    if item == target:
        print("Found!")
        break
else:
    print("Not found")
```

> 📝 **Practice:** [Q27 — Search in List](./practice.md#q27--loop-else--search-in-list) · [Q28 — All Positive Check](./practice.md#q28--loop-else--all-positive-check)

> [↑ Back to Top](#top)

<a id="7-enumerate"></a>
# 7. enumerate()

Professional way to get index + value together — no manual counter needed.

```python
names = ["Alice", "Bob", "Carol"]

for index, name in enumerate(names):
    print(index, name)
```

```
Without enumerate:          With enumerate:
  i = 0                       for i, name in enumerate(names):
  for name in names:
    print(i, name)
    i += 1

Both produce:
  0  Alice
  1  Bob
  2  Carol
```

What `enumerate` returns:

```
names = ["Alice", "Bob", "Carol"]

enumerate(names):
  (0, "Alice")
  (1, "Bob")
  (2, "Carol")
```

Custom start index:

```python
for i, name in enumerate(names, start=1):
    print(i, name)
# 1 Alice, 2 Bob, 3 Carol
```

> 📝 **Practice:** [Q29 — Index and Value](./practice.md#q29--enumerate--index-and-value) · [Q30 — Find Index of Item](./practice.md#q30--enumerate--find-index-of-item)

> [↑ Back to Top](#top)

<a id="8-zip"></a>
# 8. zip()

Iterate two (or more) sequences in parallel — pairing items by position.

```python
names  = ["Alice", "Bob"]
scores = [90, 85]

for name, score in zip(names, scores):
    print(name, score)
```

What `zip` does:

```
names:   ["Alice",  "Bob" ]
scores:  [  90,      85  ]
          ──────    ──────
zip:     ("Alice", 90)
         ("Bob",   85)
```

Stops at the shortest list:

```python
a = [1, 2, 3]
b = ["x", "y"]
list(zip(a, b))   # [(1, 'x'), (2, 'y')] — 3 is dropped
```

<a id="zip-recipes"></a>
## zip Recipes

**Create a dict from two lists:**

```python
keys   = ["name", "age", "city"]
values = ["Alice", 30, "NYC"]

person = dict(zip(keys, values))
# {"name": "Alice", "age": 30, "city": "NYC"}
```

This is the idiomatic way to build a dict from two parallel lists. No loop needed.

**Unzip (transpose) — split pairs back into two lists:**

```python
pairs = [(1, "a"), (2, "b"), (3, "c")]

numbers, letters = zip(*pairs)
# numbers = (1, 2, 3)
# letters = ("a", "b", "c")
```

`zip(*pairs)` unpacks the list into individual arguments, then zips them back column-wise — effectively a transpose.

**zip with three or more sequences:**

```python
names  = ["Alice", "Bob"]
scores = [90, 85]
grades = ["A", "B"]

for name, score, grade in zip(names, scores, grades):
    print(f"{name}: {score} ({grade})")
```

**When lists have different lengths — use `zip_longest`:**

```python
from itertools import zip_longest

a = [1, 2, 3]
b = ["x", "y"]

for x, y in zip_longest(a, b, fillvalue=None):
    print(x, y)
# 1 x
# 2 y
# 3 None   ← fills missing value with None
```

```
zip:             zip_longest(fillvalue=None):
  1 → x            1 → x
  2 → y            2 → y
  (3 dropped)      3 → None
```

Use `zip_longest` when you cannot afford to silently lose items.

> 📝 **Practice:** [Q31 — Pair Two Lists](./practice.md#q31--zip--pair-two-lists) · [Q32 — Compare Lists](./practice.md#q32--zip--compare-lists)

> [↑ Back to Top](#top)

<a id="9-comprehensions"></a>
# 9. Comprehensions (Controlled Expression Loops)

Compact way to build a list (or dict/set) from a loop in one line.

```python
# List comprehension:
squares = [x*x for x in range(5)]           # [0, 1, 4, 9, 16]

# With condition:
evens = [x for x in range(10) if x % 2 == 0]  # [0, 2, 4, 6, 8]

# Dict comprehension:
lengths = {word: len(word) for word in ["cat", "horse"]}   # {'cat': 3, 'horse': 5}

# Set comprehension:
unique_lens = {len(word) for word in ["cat", "dog", "horse"]}  # {3, 5}
```

```
[expression  for  variable  in  iterable  if  condition]
     │              │               │            │
  what to keep   loop var        data source   filter (optional)
```

**Comprehension with transformation in the expression:**

```python
# Transform AND filter in one line:
upper_long = [w.upper() for w in words if len(w) > 3]
#              ↑ transform          ↑ filter

# Conditional expression in the value part (ternary):
labels = ["even" if x % 2 == 0 else "odd" for x in range(6)]
# ["even", "odd", "even", "odd", "even", "odd"]
```

**Nested comprehension — flatten a 2D list:**

```python
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

flat = [num for row in matrix for num in row]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

```
[num  for row in matrix  for num in row]
  │        │                   │
value    outer loop         inner loop
         (rows)              (items in row)
```

Read left-to-right: "give me `num`, for each `row` in `matrix`, for each `num` in that `row`."

Readable when simple. Avoid very complex ones — use a regular loop instead.

> 📝 **Practice:** [Q33 — Squares](./practice.md#q33--list-comprehension--squares) · [Q34 — Filter Evens](./practice.md#q34--list-comprehension--filter-evens) · [Q35 — Uppercase](./practice.md#q35--list-comprehension--uppercase)

<a id="comprehension-scoping"></a>
## Comprehension Scoping — Variables Don't Leak

In Python 3, comprehension loop variables are **local to the comprehension** — they don't leak into the surrounding scope.

```python
squares = [x**2 for x in range(5)]
print(x)   # NameError — x does not exist outside the comprehension
```

Contrast with a regular `for` loop — that DOES leak:

```python
for i in range(5):
    pass
print(i)   # 4 — loop variable persists after loop ends
```

```
Comprehension scope:            Regular for loop scope:
  [x**2 for x in range(5)]       for x in range(5):
  ┌─────────────────────┐             pass
  │  x lives here only  │
  └─────────────────────┘         x = 4  ← leaks into surrounding scope
  x gone after ] closes
```

Why this matters:

```python
# Bug if you expected Python 2 behavior:
result = [n for n in range(3)]
# Python 2: n would be 2 here
# Python 3: n doesn't exist — prevents accidentally shadowing outer variables
```

> 📝 **Practice:** [Q36 — Number Squares](./practice.md#q36--dict-comprehension--number-squares) · [Q37 — Invert a Dict](./practice.md#q37--dict-comprehension--invert-a-dict)

<a id="generator-expressions"></a>
## Generator Expressions — Lazy Comprehensions

A **generator expression** looks like a list comprehension but uses `()` instead of `[]`. The key difference: it is **lazy** — it does not build the list in memory, it yields one item at a time.

```python
# List comprehension — builds full list immediately:
squares_list = [x*x for x in range(1_000_000)]   # 8 MB in memory

# Generator expression — yields one at a time, no memory buildup:
squares_gen  = (x*x for x in range(1_000_000))   # ~100 bytes
```

```
List comprehension:              Generator expression:
  [x*x for x in range(5)]         (x*x for x in range(5))
  ┌───────────────────┐           ┌────────────────────┐
  │ [0, 1, 4, 9, 16]  │           │ lazy — not built   │
  │ all in memory now │           │ yields: 0, 1, 4... │
  └───────────────────┘           └────────────────────┘
```

**When to use generator expressions:**

```python
# Summing — don't need the list, just the total:
total = sum(x*x for x in range(1000))   # no [] needed — sum() accepts any iterable

# Passing to any function that accepts an iterable:
max_val = max(abs(x) for x in [-3, 1, -7, 2])   # 7

# Filtering before processing:
first_even = next(x for x in range(100) if x % 2 == 0)   # 0
```

**Common mistake — using `[]` when you only need iteration:**

```python
# Wrong (wastes memory):
total = sum([x*x for x in range(1_000_000)])

# Right (no intermediate list):
total = sum(x*x for x in range(1_000_000))
```

Generator expressions are the right tool when:
- You're feeding data into `sum()`, `max()`, `min()`, `any()`, `all()`, `next()`
- You only need to iterate once
- The dataset is large and memory matters

Use a list comprehension when you need to iterate multiple times or need indexing.

> [↑ Back to Top](#top)

<a id="real-world-production-thinking"></a>
# 🔥 Real-World Production Thinking

Control flow in production is used for:

- Validations — guard clauses before business logic
- Authorization logic — if not authenticated, return early
- Data filtering — comprehensions to select/transform
- Retry mechanisms — while loop with counter
- Error handling decisions — if/else based on error type
- Workflow branching — match-case on status codes
- State machines — if/elif chains on current state

Example:

```python
if not user.is_authenticated:
    return "Access Denied"
```

Security depends on correct control flow.

> [↑ Back to Top](#top)

<a id="truthy-and-falsy"></a>
# 🧠 Truthy and Falsy (Important for Interviews)

In Python, any value can be used in a boolean context. **Falsy** values evaluate to `False`; everything else is **truthy**.

```
Falsy values:
  None · False · 0 · 0.0 · "" · [] · {} · set() · b""

Truthy values:
  Everything else — non-zero numbers, non-empty strings/lists/dicts, etc.
```

```python
if []:
    print("True")    # not printed — empty list is falsy
else:
    print("False")   # prints

if [0]:
    print("True")    # prints — non-empty list is truthy, even if it contains 0
```

<a id="short-circuit-evaluation"></a>
## Short-Circuit Evaluation

Python's `and` / `or` operators **stop as soon as the result is determined** — they don't evaluate the right side if they don't need to.

```
x and y:
  evaluate x
      │
  x is falsy? ── Yes ──► return x  (y never evaluated)
      │
      No
      │
  evaluate y ──────────► return y

x or y:
  evaluate x
      │
  x is truthy? ── Yes ──► return x  (y never evaluated)
      │
      No
      │
  evaluate y ───────────► return y
```

```python
def is_valid_user(user_id):
    return db.query(...)   # expensive!

# BAD: always calls is_valid_user, even if user_id is None
if user_id != None and is_valid_user(user_id):
    process(user_id)

# GOOD: if user_id is falsy, is_valid_user never runs
if user_id and is_valid_user(user_id):
    process(user_id)
```

**The `or` default pattern:**

```python
name   = user_input or "Anonymous"      # empty string → use default
config = loaded_config or DEFAULT_CONFIG
```

> [↑ Back to Top](#top)

<a id="common-mistakes"></a>
# 🧠 Common Mistakes

1. Using `==` instead of `is` (or vice versa) — `is` checks identity, `==` checks value
2. Forgetting indentation — Python uses indent for blocks, not braces
3. Infinite loops — `while True` with no `break`
4. Deep nested conditions — use guard clauses / early returns instead
5. Complex unreadable comprehensions — use a regular loop if it's more than one line
6. Wrong condition order in `elif` — specific conditions must come before general ones
7. Misunderstanding loop `else` — it runs when no `break`, not when condition is False
8. Modifying a dict while iterating — iterate over `list(d.keys())` instead
9. Using `zip` when lists have different lengths — use `zip_longest` if you can't drop items

> [↑ Back to Top](#top)

<a id="interview-questions"></a>
# 🎯 Interview Questions

1. Difference between `for` and `while`?
2. When would you use `while` instead of `for`?
3. Explain loop `else` — when does it run?
4. What is `match-case`? How is it different from `if-elif`?
5. Difference between `break` and `continue`?
6. How does Python evaluate conditions (truthy/falsy)?
7. What is short-circuit evaluation? Give a real example.
8. How to break out of nested loops cleanly?
9. What is a walrus operator? When would you use it?
10. Performance difference between loop and comprehension?
11. What is a guard clause? Why is it preferred over deep nesting?
12. Difference between list comprehension and generator expression?
13. How does `zip()` handle lists of different lengths?
14. What is structural pattern matching in `match-case`?

> [↑ Back to Top](#top)

<a id="final-mental-model"></a>
# 🏁 Final Mental Model

Control Flow is like traffic signals.

Green → execute
Red → stop
Yellow → check condition

Loops are like circular roads.
`break` is the exit ramp.
`continue` is skipping a lane.
`else` on a loop is the "completed the full circuit" sign.
`pass` is the placeholder cone — "construction coming."

Guard clauses are the bouncers at the door — reject invalid cases up front,
let valid requests flow through cleanly.

Generator expressions are lazy pipelines — build the conveyor belt,
but only move items when someone asks.

If you understand this, you understand how programs think.

> [↑ Back to Top](#top)

<a id="the-random-module"></a>
# 🎲 The random Module — Adding Chance to Your Code

> Sometimes you want your program to make a random decision — like a computer opponent in a game.
> Python's built-in `random` module does exactly that.

```python
import random
```

## The Two Functions You'll Use Most

**Pick a random whole number between two values:**

```python
number = random.randint(1, 6)   # like rolling a dice — gives 1, 2, 3, 4, 5, or 6
```

`randint(a, b)` includes both `a` and `b`.

**Pick a random item from a list:**

```python
colours = ["red", "green", "blue", "yellow"]
picked = random.choice(colours)   # picks one at random
```

## Quick Reference

```python
random.randint(1, 10)          # random int from 1 to 10 (inclusive)
random.choice(["a", "b", "c"]) # random item from a list
random.random()                # random float between 0.0 and 1.0
random.shuffle(my_list)        # shuffle a list in place
```

## Used in Rock Paper Scissors

```python
choices = ["rock", "paper", "scissors"]
computer_pick = random.choice(choices)
print("Computer chose:", computer_pick)
```

> 📝 **Practice:** [Q21 — Repeat Until Valid](./practice.md#q21--while-loop--repeat-until-valid)

> [↑ Back to Top](#top)

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [01.1_memory_management → theory.md](../01.1_memory_management/theory.md) |
| ➡ Next Module | [03_data_types → theory.md](../03_data_types/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[Python Fundamentals →](../01_python_fundamentals/theory.md) · [Memory Management →](../01.1_memory_management/theory.md) · [Functions →](../04_functions/theory.md) · [Generators →](../11_generators_iterators/theory.md)

**Jump to specific topics in other files:**
- Generator protocol → [11_generators_iterators/theory.md#-chapter-3-generator-functions--yield](../11_generators_iterators/theory.md#-chapter-3-generator-functions--yield)
- Closures and scope → [04_functions/theory.md#9-closures--functions-that-remember](../04_functions/theory.md#9-closures--functions-that-remember)
- LEGB scope rules → [04_functions/theory.md#6-scope--the-legb-rule](../04_functions/theory.md#6-scope--the-legb-rule)
- Reference counting → [01.1_memory_management/theory.md#3-reference-counting](../01.1_memory_management/theory.md#3-reference-counting)
