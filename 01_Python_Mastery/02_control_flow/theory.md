# 🔁 Control Flow in Python

> Control flow decides HOW your program thinks.
> Not what it stores. Not how it looks.
> But how it makes decisions.

If memory is about storage,
control flow is about intelligence.

This chapter builds decision-making ability into your programs.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`if`/`elif`/`else` · `for` loop · `while` loop · `break` / `continue` / `else` on loops · List/dict/set comprehensions

**Should Learn** — Important for real projects, comes up regularly:
Walrus operator `:=` · `match`/`case` pattern matching · Generator expressions

**Good to Know** — Useful in specific situations:
Comprehension scoping rules · `reversed()` · Ternary expression

**Reference** — Know it exists, look up when needed:
`itertools` (covered in generators module)

---

# 🧠 Big Picture: What is Control Flow?

Control Flow means:

> The order in which statements execute in a program.

By default, Python runs top → bottom.

But real programs don’t work linearly.

They:
- Make decisions
- Repeat tasks
- Break early
- Skip steps
- Handle unexpected errors

That’s control flow.

---

# 🛣 Default Execution Flow

Example:

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

Simple.
Top to bottom.

Now let’s make it intelligent.

---

# 🔹 1. Conditional Statements (Decision Making)

## if Statement

Imagine a 10-year-old:

“If it rains, take umbrella.”

That’s an `if` statement.

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

Important:

- Condition must evaluate to True or False.
- Indentation defines the block.
> 📝 **Practice:** [Q1 — Age Check](./practice.md#q1--if-statement--age-check) · [Q2 — Password Check](./practice.md#q2--if-statement--password-check) · [Q3 — Multiple Conditions](./practice.md#q3--if-statement--multiple-conditions)

---

## if-else

```python
age = 16

if age >= 18:
    print("You can vote")
else:
    print("You cannot vote")
```

Now program must choose one path.

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

---

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
True → Stop
   |
False
   ↓
Condition 2?
   |
True → Stop
   |
False
   ↓
Condition 3?
   |
...
```

Python stops checking once it finds True.

Professional Tip:
Order matters.
Place most specific conditions first.
> 📝 **Practice:** [Q7 — Grade Checker](./practice.md#q7--if-elif-else--grade-checker) · [Q8 — Day Name](./practice.md#q8--if-elif-else--day-name) · [Q9 — Positive/Negative/Zero](./practice.md#q9--if-elif-else--positive--negative--zero)

---

# 🔹 2. Nested Conditions

You can place if inside another if.

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
True?
   |
Check citizenship
   |
True?
   |
Eligible
```

Avoid too much nesting.
It reduces readability.

> 📝 **Practice:** [Q10 — Voter Eligibility](./practice.md#q10--nested-conditions--voter-eligibility) · [Q11 — Login + Role](./practice.md#q11--nested-conditions--login--role)

---

# 🔹 3. Ternary Operator (Inline Condition)

Short-hand decision:

```python
age = 20
status = "Adult" if age >= 18 else "Minor"
```

Readable when simple.
Avoid complex nested ternaries.

> 📝 **Practice:** [Q12 — Even/Odd one-liner](./practice.md#q12--ternary-operator--evenodd-one-liner) · [Q13 — Max of Two](./practice.md#q13--ternary-operator--max-of-two)

---

# 🔹 4. match-case (Python 3.10+)

Cleaner alternative to multiple elif.

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

Use when:
- Matching specific values
- Cleaner than many elif

Not replacement for all if-else logic.

> 📝 **Practice:** [Q14 — HTTP Status](./practice.md#q14--match-case--http-status)

---

## 🔗 The Walrus Operator `:=` — Assignment Expression

Python 3.8 introduced the **walrus operator** `:=` — officially called an **assignment expression**.

It assigns a value AND returns it in a single expression.
Without it, you sometimes compute a value twice:

```python
# Without walrus — compute len() twice:
data = get_data()
if len(data) > 10:
    print(f"Large dataset: {len(data)} items")   # computed again!

# With walrus — compute once, use in same expression:
if (n := len(data)) > 10:
    print(f"Large dataset: {n} items")           # n already assigned
```

**Where it genuinely helps:**

```python
# 1 — while loops reading chunks (classic pattern):

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
    print(f"Found number: {m.group()}")   # m is already bound
```

> 📝 **Practice:** [Q15 — Length Check](./practice.md#q15--walrus-operator--length-check)


**The rule:** Use walrus when you'd otherwise compute the same value twice.
Don't use it just to be clever — if it makes code harder to read, use two lines.

```python
# Fine:
while line := file.readline():
    process(line)

# Don't do this — hard to read:
print(y := f(x), y)
```

---

# 🔁 5. Loops (Repetition)

Loops repeat code.

Two types:

- for loop
- while loop

---

# 🔹 for Loop

Used for iterating over sequences.

```python
for i in range(5):
    print(i)
```

Flow:

```
Start
  ↓
Get next item
  ↓
Run block
  ↓
More items?
  /     \
Yes      No
 |        |
Repeat    Exit
```

Used with:
- lists
- tuples
- strings
- dictionaries
- sets
- [generators](../11_generators_iterators/theory.md#-chapter-3-generator-functions--yield)
> 📝 **Practice:** [Q16 — Print 1 to 10](./practice.md#q16--for-loop--print-1-to-10) · [Q17 — Sum of a List](./practice.md#q17--for-loop--sum-of-a-list) · [Q18 — Even Numbers Only](./practice.md#q18--for-loop--even-numbers-only)

---

# 🔹 while Loop

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
True?
   |
Run block
   |
Back to condition
```

Danger:

Infinite loop if condition never becomes False.
> 📝 **Practice:** [Q19 — Countdown](./practice.md#q19--while-loop--countdown) · [Q21 — Repeat Until Valid](./practice.md#q21--while-loop--repeat-until-valid)

---

# 🔹 6. break Statement

Stops loop immediately.

```python
for i in range(10):
    if i == 5:
        break
    print(i)
```

Used when:
- Early exit needed
- Search found
- Error condition met

> 📝 **Practice:** [Q22 — Find First Negative](./practice.md#q22--break--find-first-negative) · [Q23 — Stop at Keyword](./practice.md#q23--break--stop-at-keyword)

---

### Breaking Out of Nested Loops

`break` only exits the **innermost** loop it's in. This surprises many beginners.

```python
# break only exits the inner loop:
for i in range(3):
    for j in range(3):
        if j == 1:
            break           # exits j loop, i loop continues
    print(f"i={i}")         # prints i=0, i=1, i=2

# Output: i=0, i=1, i=2  ← outer loop ran all 3 times
```

**Pattern 1: Use a flag variable**

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

**Pattern 2: Use a function with return** *(covered in Module 04 — Functions)*

> If you haven't learned functions yet, skip this pattern and use Pattern 1. Come back after Module 04.

```python
def find_in_grid(grid, target):
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == target:
                return (i, j)   # exits BOTH loops immediately
    return None
```

The function approach is the cleanest — `return` exits all loops at once.
> 📝 **Practice:** [Q22 — Find First Negative](./practice.md#q22--break--find-first-negative) · [Q23 — Stop at Keyword](./practice.md#q23--break--stop-at-keyword)

---

# 🔹 7. continue Statement

Skips current iteration.

```python
for i in range(5):
    if i == 2:
        continue
    print(i)
```

Skips printing 2.
> 📝 **Practice:** [Q24 — Skip Negatives](./practice.md#q24--continue--skip-negatives) · [Q21 — Repeat Until Valid](./practice.md#q21--while-loop--repeat-until-valid)

---

# 🔹 8. pass Statement

Does nothing.

Used as placeholder.

```python
if True:
    pass
```

Useful in:
- Empty functions
- Class definitions
- Future implementations

> 📝 **Practice:** [Q26 — Placeholder](./practice.md#q26--pass--placeholder)

---

# 🔹 9. Loop else (Advanced & Rarely Understood)

Python allows:

```python
for i in range(5):
    if i == 10:
        break
else:
    print("Loop completed normally")
```

The `else` runs ONLY if loop did NOT break.

Professional Use:
Used in search algorithms.

> 📝 **Practice:** [Q27 — Search in List](./practice.md#q27--loop-else--search-in-list) · [Q28 — All Positive Check](./practice.md#q28--loop-else--all-positive-check)

---

# 🔹 10. enumerate()

Professional way to get index + value.

```python
names = ["A", "B", "C"]

for index, value in enumerate(names):
    print(index, value)
```

Cleaner than manual counter.

> 📝 **Practice:** [Q29 — Index and Value](./practice.md#q29--enumerate--index-and-value) · [Q30 — Find Index of Item](./practice.md#q30--enumerate--find-index-of-item)

---

# 🔹 11. zip()

Iterate multiple sequences together.

```python
names = ["A", "B"]
scores = [90, 80]

for name, score in zip(names, scores):
    print(name, score)
```

Stops at shortest list.

> 📝 **Practice:** [Q31 — Pair Two Lists](./practice.md#q31--zip--pair-two-lists) · [Q32 — Compare Lists](./practice.md#q32--zip--compare-lists)

---

# 🔹 12. Comprehensions (Controlled Expression Loops)

List comprehension:

```python
squares = [x*x for x in range(5)]
```

With condition:

```python
evens = [x for x in range(10) if x % 2 == 0]
```

Readable when simple.
Avoid very complex ones.

> 📝 **Practice:** [Q33 — Squares](./practice.md#q33--list-comprehension--squares) · [Q34 — Filter Evens](./practice.md#q34--list-comprehension--filter-evens) · [Q35 — Uppercase](./practice.md#q35--list-comprehension--uppercase)

---

### Comprehension Scoping — Variables Don't Leak

In Python 3, each comprehension has **its own scope**. The loop variable does not leak out.

```python
# In Python 3 — loop variable is LOCAL to the comprehension:
squares = [x**2 for x in range(5)]
print(x)   # NameError: name 'x' is not defined

# Generator expressions — also isolated:
gen = (x for x in range(5))
print(x)   # NameError

# Dict comprehension — same rule:

mapping = {k: v for k, v in pairs}
print(k)   # NameError
```

Contrast with a regular `for` loop — that DOES leak:

```python
for i in range(5):
    pass
print(i)   # 4 — the loop variable persists after a regular for loop
```

**Why this matters:**

```python


# Bug if you expected Python 2 behavior:
result = [n for n in range(3)]
# In Python 2, n would be 2 here — in Python 3, n doesn't exist
# This change prevents subtle bugs where comprehension variables
# accidentally shadow outer variables
```

> 📝 **Practice:** [Q36 — Number Squares](./practice.md#q36--dict-comprehension--number-squares) · [Q37 — Invert a Dict](./practice.md#q37--dict-comprehension--invert-a-dict)


---

# 🔥 Real-World Production Thinking

Control flow in production is used for:

- Validations
- Authorization logic
- Data filtering
- Retry mechanisms
- Error handling decisions
- Workflow branching
- State machines

Example:

```python
if not user.is_authenticated:
    return "Access Denied"
```

Security depends on correct control flow.

---

# 🧠 Common Mistakes

1. Using == instead of is (or vice versa)
2. Forgetting indentation
3. Infinite loops
4. Deep nested conditions
5. Complex unreadable comprehensions
6. Wrong condition order

---

# 🎯 Interview Questions

1. Difference between for and while?
2. When would you use while instead of for?
3. Explain loop else.
4. What is match-case?
5. Difference between break and continue?
6. How does Python evaluate conditions?
7. What is truthy and falsy?
8. How to avoid deep nesting?
9. What happens if indentation is wrong?
10. Performance difference between loop and comprehension?

If you can explain clearly with examples,
you’re thinking practically.

---

# 🧠 Truthy and Falsy (Important for Interviews)

Falsy values:
- None
- False
- 0
- 0.0
- ""
- []
- {}
- set()

Everything else is Truthy.

Example:

```python
if []:
    print("True")
else:
    print("False")
```

Prints False.

---

### Short-Circuit Evaluation

Python's `and` and `or` operators **stop evaluating as soon as the result is determined**.
This is called short-circuit evaluation.

```
x and y:
  If x is falsy → return x immediately (don't evaluate y)
  If x is truthy → return y

x or y:
  If x is truthy → return x immediately (don't evaluate y)
  If x is falsy → return y
```

**Why it matters — avoid expensive calls:**

```python
def is_valid_user(user_id):
    # expensive DB call
    return db.query(f"SELECT 1 FROM users WHERE id={user_id}")

# BAD: always calls is_valid_user, even if user_id is None
if user_id != None and is_valid_user(user_id):
    process(user_id)

# GOOD: if user_id is falsy, is_valid_user never runs
if user_id and is_valid_user(user_id):
    process(user_id)
```

**The `or` default pattern:**

```python
name = user_input or "Anonymous"   # if user_input is empty/None, use "Anonymous"
config = loaded_config or DEFAULT_CONFIG
```

**Short-circuit with side effects (careful):**

```python
# If condition1 is False, condition2 never runs
# Can be a bug if condition2 has side effects you expect to happen
if condition1 and condition2_with_side_effect():
    ...
```

---

# 🏁 Final Mental Model

Control Flow is like traffic signals.

Green → execute  
Red → stop  
Yellow → check condition  

Loops are like circular roads.
Break is exit.
Continue is skip lane.

If you understand this,
you understand how programs think.

---

# 🔁 Navigation

[Fundamentals](/01_Python_Mastery/01_python_fundamentals/theory.md)  
[Memory Management](/01_Python_Mastery/memory_management/theory.md)  
[Data Types](/01_Python_Mastery/03_data_types/theory.md)

---


# 🎲 The random Module — Adding Chance to Your Code

> Sometimes you want your program to make a random decision — like a computer opponent in a game.
> Python's built-in `random` module does exactly that.

You don't need to install anything. Just import it:

```python
import random
```

## The Two Functions You'll Use Most

**Pick a random whole number between two values:**

```python
import random

number = random.randint(1, 6)   # like rolling a dice — gives 1, 2, 3, 4, 5, or 6
print(number)
```

`randint(a, b)` includes both `a` and `b`. So `randint(1, 6)` can return 1, 2, 3, 4, 5, or 6.

**Pick a random item from a list:**

```python
import random

colours = ["red", "green", "blue", "yellow"]
picked = random.choice(colours)   # picks one at random
print(picked)
```

`random.choice()` picks one item from the list. Every item has an equal chance.

## Quick Reference

```python
import random

random.randint(1, 10)          # random whole number from 1 to 10 (inclusive)
random.choice(["a", "b", "c"]) # random item from a list
random.random()                # random decimal between 0.0 and 1.0
random.shuffle(my_list)        # shuffle a list in place
```

## Used in Rock Paper Scissors

```python
import random

choices = ["rock", "paper", "scissors"]
computer_pick = random.choice(choices)   # computer picks randomly
print("Computer chose:", computer_pick)
```

This is exactly how a computer opponent works in a simple game — it picks randomly from the options.
> 📝 **Practice:** [Q21 — Repeat Until Valid](./practice.md#q21--while-loop--repeat-until-valid)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Python Fundamentals — Interview Q&A](../01_python_fundamentals/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md) · [Practice Problems](./practice.md)
