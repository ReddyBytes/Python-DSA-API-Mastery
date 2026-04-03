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

---

# 🔹 3. Ternary Operator (Inline Condition)

Short-hand decision:

```python
age = 20
status = "Adult" if age >= 18 else "Minor"
```

Readable when simple.
Avoid complex nested ternaries.

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

**Pattern 2: Use a function with return**

```python
def find_in_grid(grid, target):
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == target:
                return (i, j)   # exits BOTH loops immediately
    return None
```

The function approach is the cleanest — `return` exits all loops at once.

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

---

# 🔹 10. enumerate()

Professional way to get index + value.

```python
names = ["A", "B", "C"]

for index, value in enumerate(names):
    print(index, value)
```

Cleaner than manual counter.

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

[Fundamentals](/python-complete-mastery/01_python_fundamentals/theory.md)  
[Memory Management](/python-complete-mastery/memory_management/theory.md)  
[Data Types](/python-complete-mastery/03_data_types/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Python Fundamentals — Interview Q&A](../01_python_fundamentals/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
