# 🔁 Control Flow — Practice Problems

> 37 problems · All concepts from the theory file  
> Write your answer in `practice_local.py` first, then use the dropdowns.

---

## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| Q1–Q3 | `if` statement | 🟢 |
| Q4–Q6 | `if-else` | 🟢 |
| Q7–Q9 | `if-elif-else` | 🟢 |
| Q10–Q11 | Nested conditions | 🟡 |
| Q12–Q13 | Ternary operator | 🟡 |
| Q14 | `match-case` | 🟡 |
| Q15 | Walrus operator `:=` | 🟠 |
| Q16–Q18 | `for` loop | 🟢 |
| Q19–Q21 | `while` loop | 🟢 |
| Q22–Q23 | `break` | 🟡 |
| Q24–Q25 | `continue` | 🟡 |
| Q26 | `pass` | 🟢 |
| Q27–Q28 | Loop `else` | 🟠 |
| Q29–Q30 | `enumerate()` | 🟡 |
| Q31–Q32 | `zip()` | 🟡 |
| Q33–Q35 | List comprehension | 🟡 |
| Q36–Q37 | Dict comprehension | 🟡 |

---

### Q1 · if statement — Age Check

**Problem:**
Write an `if` statement that prints `"You can vote"` only if `age` is 18 or more.

```python
age = 20
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use the `>=` operator to check if age is 18 or above. You only need one line inside the `if` block.

</details>

<details>
<summary>✅ Answer</summary>

```python
age = 20
if age >= 18:
    print("You can vote")
```

**Why:** `>=` means "greater than or equal to". Since 20 is greater than 18, the condition is `True` and the print runs.

</details>

---

### Q2 · if statement — Password Check

**Problem:**
Write an `if` that prints `"Access granted"` only if `password` equals `"secret123"`.

```python
password = "secret123"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `==` to compare two strings. Make sure both sides have the exact same spelling and case.

</details>

<details>
<summary>✅ Answer</summary>

```python
password = "secret123"
if password == "secret123":
    print("Access granted")
```

**Why:** `==` checks if two values are identical. Since `password` holds `"secret123"`, the condition is `True` and the message prints.

</details>

---

### Q3 · if statement — Multiple Conditions

**Problem:**
Write an `if` that prints `"Welcome admin"` only if `username` is `"admin"` AND `password` is `"1234"`. Both must be true at the same time.

```python
username = "admin"
password = "1234"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use the `and` keyword to combine two conditions. Both conditions must be `True` for the whole thing to be `True`.

</details>

<details>
<summary>✅ Answer</summary>

```python
username = "admin"
password = "1234"
if username == "admin" and password == "1234":
    print("Welcome admin")
```

**Why:** `and` means both sides must be `True`. If either one fails, the whole condition is `False` and nothing prints.

</details>

---

### Q4 · if-else — Even or Odd

**Problem:**
Given `number = 7`, print `"Even"` if it is divisible by 2, otherwise print `"Odd"`.

```python
number = 7
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

The `%` operator gives you the remainder after division. If `number % 2 == 0`, there is no remainder, so it is even.

</details>

<details>
<summary>✅ Answer</summary>

```python
number = 7
if number % 2 == 0:
    print("Even")
else:
    print("Odd")
```

**Why:** `7 % 2` equals `1` (not `0`), so the `if` block is skipped and `else` runs, printing `"Odd"`.

</details>

---

### Q5 · if-else — Temperature

**Problem:**
`temp = 35`. Print `"Hot"` if `temp` is greater than 30, otherwise print `"Cool"`.

```python
temp = 35
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

A simple `if-else` is all you need here. No extra conditions required.

</details>

<details>
<summary>✅ Answer</summary>

```python
temp = 35
if temp > 30:
    print("Hot")
else:
    print("Cool")
```

**Why:** `35 > 30` is `True`, so the `if` block runs and prints `"Hot"`. The `else` is ignored.

</details>

---

### Q6 · if-else — Positive or Negative

**Problem:**
`number = -5`. Print `"Positive"` if greater than 0, else print `"Negative"`. You can ignore zero for now.

```python
number = -5
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Compare the number directly with `0` using the `>` operator.

</details>

<details>
<summary>✅ Answer</summary>

```python
number = -5
if number > 0:
    print("Positive")
else:
    print("Negative")
```

**Why:** `-5 > 0` is `False`, so Python skips the `if` block and runs `else`, printing `"Negative"`.

</details>

---

### Q7 · if-elif-else — Grade Checker

**Problem:**
`marks = 72`. Print `"A"` if marks are 90 or above, `"B"` if 75 or above, `"C"` if 50 or above, otherwise print `"Fail"`.

```python
marks = 72
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Order matters — put the highest threshold first. Python checks each condition in order and stops at the first `True` one.

</details>

<details>
<summary>✅ Answer</summary>

```python
marks = 72
if marks >= 90:
    print("A")
elif marks >= 75:
    print("B")
elif marks >= 50:
    print("C")
else:
    print("Fail")
```

**Why:** `72` is not `>= 90` or `>= 75`, but it is `>= 50`, so `"C"` prints. If you put the lowest threshold first, everyone would get `"C"` — order is critical.

</details>

---

### Q8 · if-elif-else — Day Name

**Problem:**
`day = 3`. Print the matching day name: 1 = Monday, 2 = Tuesday, 3 = Wednesday, 4 = Thursday, 5 = Friday, 6 = Saturday, 7 = Sunday. Any other number should print `"Invalid"`.

```python
day = 3
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Each day number gets its own `elif` branch. The final `else` handles any number outside 1–7.

</details>

<details>
<summary>✅ Answer</summary>

```python
day = 3
if day == 1:
    print("Monday")
elif day == 2:
    print("Tuesday")
elif day == 3:
    print("Wednesday")
elif day == 4:
    print("Thursday")
elif day == 5:
    print("Friday")
elif day == 6:
    print("Saturday")
elif day == 7:
    print("Sunday")
else:
    print("Invalid")
```

**Why:** Python checks each condition top to bottom. `day == 3` matches the third branch, so `"Wednesday"` prints.

</details>

---

### Q9 · if-elif-else — Positive / Negative / Zero

**Problem:**
`number = 0`. Print `"Positive"` if greater than 0, `"Negative"` if less than 0, or `"Zero"` if it equals 0.

```python
number = 0
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

You need exactly three branches: one for each case. Think `if`, `elif`, `else`.

</details>

<details>
<summary>✅ Answer</summary>

```python
number = 0
if number > 0:
    print("Positive")
elif number < 0:
    print("Negative")
else:
    print("Zero")
```

**Why:** `0` is not `> 0` and not `< 0`, so both `if` and `elif` are skipped. The `else` block runs and prints `"Zero"`.

</details>

---

### Q10 · Nested conditions — Voter Eligibility

**Problem:**
`age = 20`, `citizen = True`. Print `"Can vote"` only if age is 18 or more AND citizen is `True`. Use nested `if` statements (not the `and` keyword).

```python
age = 20
citizen = True
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

First check the age condition. Inside that block, add a second `if` to check citizenship. One `if` lives inside the other.

</details>

<details>
<summary>✅ Answer</summary>

```python
age = 20
citizen = True
if age >= 18:
    if citizen:
        print("Can vote")
```

**Why:** The outer `if` checks age. Only if that passes does Python even look at the inner `if` for citizenship. Both must pass for the message to print.

</details>

---

### Q11 · Nested conditions — Login + Role

**Problem:**
`logged_in = True`, `role = "admin"`. Print `"Admin panel"` only if the user is logged in AND their role is `"admin"`. Use nested `if` statements.

```python
logged_in = True
role = "admin"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Check `logged_in` first in the outer `if`. Then check `role` inside that block.

</details>

<details>
<summary>✅ Answer</summary>

```python
logged_in = True
role = "admin"
if logged_in:
    if role == "admin":
        print("Admin panel")
```

**Why:** The inner `if` only runs when the outer `if` is already `True`. This mimics real login checks — no point checking the role if the user isn't even logged in.

</details>

---

### Q12 · Ternary operator — Even/Odd one-liner

**Problem:**
Rewrite the code below as a single line using the ternary operator. `number = 8`.

```python
if number % 2 == 0:
    result = "Even"
else:
    result = "Odd"
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

The ternary format is: `value_if_true if condition else value_if_false`. The whole thing goes on the right side of `result =`.

</details>

<details>
<summary>✅ Answer</summary>

```python
number = 8
result = "Even" if number % 2 == 0 else "Odd"
print(result)  # Even
```

**Why:** The ternary is a compact way to assign one of two values based on a condition. Since `8 % 2 == 0` is `True`, `result` gets `"Even"`.

</details>

---

### Q13 · Ternary operator — Max of Two

**Problem:**
`a = 10`, `b = 25`. Use a ternary operator to set `max_val` to whichever number is larger.

```python
a = 10
b = 25
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

The condition to check is `a > b`. If that is `True`, pick `a`; otherwise pick `b`.

</details>

<details>
<summary>✅ Answer</summary>

```python
a = 10
b = 25
max_val = a if a > b else b
print(max_val)  # 25
```

**Why:** `10 > 25` is `False`, so the `else` side runs and `max_val` is set to `b`, which is `25`.

</details>

---

### Q14 · match-case — HTTP Status

**Problem:**
`status = 404`. Use `match-case` to print a message for each status code: `200` → `"OK"`, `404` → `"Not Found"`, `500` → `"Server Error"`. Any other code should print `"Unknown"`.

```python
status = 404
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`match-case` uses `_` as the wildcard (catch-all) case, like `else` in an if-chain.

</details>

<details>
<summary>✅ Answer</summary>

```python
status = 404
match status:
    case 200:
        print("OK")
    case 404:
        print("Not Found")
    case 500:
        print("Server Error")
    case _:
        print("Unknown")
```

**Why:** Python checks each `case` in order. `status` is `404`, so the second case matches and prints `"Not Found"`. The `_` case catches anything that did not match above.

</details>

---

### Q15 · Walrus operator — Length Check

**Problem:**
Rewrite the code below so `len(data)` is only called once. Use the walrus operator (`:=`).

```python
data = [1, 2, 3, 4, 5]
if len(data) > 3:
    print(f"List is long: {len(data)} items")
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`:=` assigns a value AND uses it in the same expression. Wrap it in parentheses inside the `if` condition.

</details>

<details>
<summary>✅ Answer</summary>

```python
data = [1, 2, 3, 4, 5]
if (n := len(data)) > 3:
    print(f"List is long: {n} items")
```

**Why:** `:=` assigns `len(data)` to `n` and checks `> 3` in one step. Inside the block, `n` already holds the value so we do not need to call `len()` again.

</details>

---

### Q16 · for loop — Print 1 to 10

**Problem:**
Use a `for` loop to print every number from 1 through 10, one per line.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`range(1, 11)` generates numbers starting at 1 and stopping before 11, so you get 1 through 10.

</details>

<details>
<summary>✅ Answer</summary>

```python
for i in range(1, 11):
    print(i)
```

**Why:** `range(start, stop)` stops one before the `stop` value. So `range(1, 11)` gives you 1, 2, 3 … 10.

</details>

---

### Q17 · for loop — Sum of a List

**Problem:**
`numbers = [10, 20, 30, 40, 50]`. Use a `for` loop to add up all the numbers and print the total.

```python
numbers = [10, 20, 30, 40, 50]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Start with `total = 0` before the loop. On each iteration, add the current number to `total`.

</details>

<details>
<summary>✅ Answer</summary>

```python
numbers = [10, 20, 30, 40, 50]
total = 0
for n in numbers:
    total += n
print(total)  # 150
```

**Why:** `total += n` is shorthand for `total = total + n`. The loop runs five times, adding each number to the running total.

</details>

---

### Q18 · for loop — Even Numbers Only

**Problem:**
Use a `for` loop over `range(1, 21)` and print only the even numbers.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Add an `if` inside the loop. Check `i % 2 == 0` — if there is no remainder, the number is even.

</details>

<details>
<summary>✅ Answer</summary>

```python
for i in range(1, 21):
    if i % 2 == 0:
        print(i)
```

**Why:** The loop visits every number 1–20. The `if` filters out odd numbers so only 2, 4, 6 … 20 get printed.

</details>

---

### Q19 · while loop — Countdown

**Problem:**
Print numbers from 10 down to 1 using a `while` loop.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Start with `count = 10`. Print `count`, then subtract 1. Keep looping as long as `count >= 1`.

</details>

<details>
<summary>✅ Answer</summary>

```python
count = 10
while count >= 1:
    print(count)
    count -= 1
```

**Why:** Each iteration prints the current value and then decreases it by 1. When `count` reaches `0`, the condition `>= 1` becomes `False` and the loop stops.

</details>

---

### Q20 · while loop — Sum Until Zero

**Problem:**
Keep asking the user for a number. Add each number to a running total. Stop when the user enters `0`. Print the total at the end.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `while True:` to loop forever, then `break` when the user enters `0`. Wrap `input()` with `int()` to convert the text to a number.

</details>

<details>
<summary>✅ Answer</summary>

```python
total = 0
while True:
    n = int(input("Enter a number (0 to stop): "))
    if n == 0:
        break
    total += n
print(f"Total: {total}")
```

**Why:** `while True` creates a loop that only ends when `break` is hit. We only break when the user types `0`, so every other number gets added to `total`.

</details>

---

### Q21 · while loop — Repeat Until Valid

**Problem:**
Keep asking for a password until the user types `"open123"`. Once they get it right, print `"Access granted"` and stop.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `while True:` and check the input. When it matches, print the message and `break` out of the loop.

</details>

<details>
<summary>✅ Answer</summary>

```python
while True:
    pw = input("Enter password: ")
    if pw == "open123":
        print("Access granted")
        break
```

**Why:** The loop keeps running until the correct password is entered. `break` exits the loop as soon as the condition is met.

</details>

---

### Q22 · break — Find First Negative

**Problem:**
`numbers = [4, 7, 2, -3, 8, -1]`. Loop through the list, print the first negative number you find, then stop immediately.

```python
numbers = [4, 7, 2, -3, 8, -1]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Check `if n < 0` inside the loop. When that is `True`, print `n` and then `break`.

</details>

<details>
<summary>✅ Answer</summary>

```python
numbers = [4, 7, 2, -3, 8, -1]
for n in numbers:
    if n < 0:
        print(n)
        break
```

**Why:** The loop visits `4`, `7`, `2`, then hits `-3`. The condition `n < 0` is `True`, so `-3` prints and `break` stops the loop before it reaches `-1`.

</details>

---

### Q23 · break — Stop at Keyword

**Problem:**
`words = ["apple", "banana", "STOP", "cherry", "date"]`. Print each word, but stop as soon as you reach `"STOP"`. Do not print `"STOP"` itself.

```python
words = ["apple", "banana", "STOP", "cherry", "date"]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Check `if word == "STOP": break` before you print. The order matters — check first, then print.

</details>

<details>
<summary>✅ Answer</summary>

```python
words = ["apple", "banana", "STOP", "cherry", "date"]
for word in words:
    if word == "STOP":
        break
    print(word)
```

**Why:** By checking the condition before printing, we exit the loop the moment `"STOP"` is seen — without printing it. `"cherry"` and `"date"` are never reached.

</details>

---

### Q24 · continue — Skip Negatives

**Problem:**
`numbers = [1, -2, 3, -4, 5]`. Print only the positive numbers. Use `continue` to skip the negatives.

```python
numbers = [1, -2, 3, -4, 5]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`continue` skips the rest of the loop body for the current iteration. Use `if n < 0: continue` before the print.

</details>

<details>
<summary>✅ Answer</summary>

```python
numbers = [1, -2, 3, -4, 5]
for n in numbers:
    if n < 0:
        continue
    print(n)
```

**Why:** When `n` is negative, `continue` jumps straight to the next iteration, skipping the `print`. The loop still runs for every item — it just skips the print step for negatives.

</details>

---

### Q25 · continue — Skip Vowels

**Problem:**
`word = "python"`. Print each letter on its own line, but skip any vowels (`a, e, i, o, u`). Use `continue`.

```python
word = "python"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `if letter in "aeiou": continue`. The `in` keyword checks if a character is inside a string.

</details>

<details>
<summary>✅ Answer</summary>

```python
word = "python"
for letter in word:
    if letter in "aeiou":
        continue
    print(letter)
```

**Why:** `"python"` has one vowel: `"o"`. Every other letter prints. `continue` skips `print` only when a vowel is found.

</details>

---

### Q26 · pass — Placeholder

**Problem:**
You are planning logic for three times of day but only have the morning part ready. Write the structure for all three cases using `pass` for the ones not yet implemented, so the code runs without errors.

```python
time = "morning"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`pass` is a valid Python statement that does nothing. It keeps a block from being empty, which would cause a syntax error.

</details>

<details>
<summary>✅ Answer</summary>

```python
time = "morning"
if time == "morning":
    print("Good morning")
elif time == "afternoon":
    pass  # TODO: add afternoon logic
elif time == "evening":
    pass  # TODO: add evening logic
```

**Why:** Python requires at least one statement inside every `if`/`elif` block. `pass` satisfies that requirement without doing anything, acting as a placeholder for future code.

</details>

---

### Q27 · loop else — Search in List

**Problem:**
`fruits = ["apple", "banana", "cherry"]`. Search for `"mango"`. Print `"Found it"` if it is in the list. If the loop finishes without finding it, print `"Not in list"`. Use `for-else`.

```python
fruits = ["apple", "banana", "cherry"]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

The `else` block on a `for` loop only runs if the loop was never interrupted by a `break`. Use `break` when you find the item and `else` to handle the not-found case.

</details>

<details>
<summary>✅ Answer</summary>

```python
fruits = ["apple", "banana", "cherry"]
for f in fruits:
    if f == "mango":
        print("Found it")
        break
else:
    print("Not in list")
```

**Why:** `"mango"` is not in the list, so `break` is never triggered. The loop completes normally and Python runs the `else` block, printing `"Not in list"`.

</details>

---

### Q28 · loop else — All Positive Check

**Problem:**
`numbers = [3, 7, 2, 5]`. Check if all numbers are positive. Print `"All positive"` if they are. Print `"Found a non-positive"` as soon as you find one that is not. Use `for-else`.

```python
numbers = [3, 7, 2, 5]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`break` early when you find a non-positive number. If you never break, the `else` runs, meaning all numbers passed the check.

</details>

<details>
<summary>✅ Answer</summary>

```python
numbers = [3, 7, 2, 5]
for n in numbers:
    if n <= 0:
        print("Found a non-positive")
        break
else:
    print("All positive")
```

**Why:** All four numbers are positive, so the `if` never triggers and `break` never runs. The loop finishes cleanly and the `else` block prints `"All positive"`.

</details>

---

### Q29 · enumerate() — Index and Value

**Problem:**
`fruits = ["apple", "banana", "cherry"]`. Print each item with its position number, starting from 1 (not 0). Output should look like:
```
1. apple
2. banana
3. cherry
```

```python
fruits = ["apple", "banana", "cherry"]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`enumerate(fruits, start=1)` gives you a counter that begins at 1. Unpack it as `i, fruit` in your loop.

</details>

<details>
<summary>✅ Answer</summary>

```python
fruits = ["apple", "banana", "cherry"]
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}. {fruit}")
```

**Why:** `enumerate()` adds an automatic counter to any iterable. The `start=1` argument makes the counter begin at 1 instead of the default 0.

</details>

---

### Q30 · enumerate() — Find Index of Item

**Problem:**
`colours = ["red", "green", "blue", "yellow"]`. Find and print the index of `"blue"` using `enumerate`.

```python
colours = ["red", "green", "blue", "yellow"]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Loop with `enumerate`, check if the item matches `"blue"`, print `i`, then `break` so you stop after the first match.

</details>

<details>
<summary>✅ Answer</summary>

```python
colours = ["red", "green", "blue", "yellow"]
for i, c in enumerate(colours):
    if c == "blue":
        print(i)
        break
```

**Why:** `enumerate` gives each item an index starting from `0`. `"blue"` is at position `2`, so `2` prints. The `break` stops the loop immediately after finding it.

</details>

---

### Q31 · zip() — Pair Two Lists

**Problem:**
`names = ["Alice", "Bob", "Charlie"]` and `scores = [85, 92, 78]`. Print each name with their score on one line, like `"Alice: 85"`.

```python
names = ["Alice", "Bob", "Charlie"]
scores = [85, 92, 78]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`zip(names, scores)` combines both lists into pairs. Unpack each pair as `name, score` in the loop.

</details>

<details>
<summary>✅ Answer</summary>

```python
names = ["Alice", "Bob", "Charlie"]
scores = [85, 92, 78]
for name, score in zip(names, scores):
    print(f"{name}: {score}")
```

**Why:** `zip` locks two lists together element by element — first items together, second items together, and so on. No index needed.

</details>

---

### Q32 · zip() — Compare Lists

**Problem:**
`predicted = [1, 0, 1, 1]` and `actual = [1, 1, 1, 0]`. Count how many positions have the same value in both lists. Print the count.

```python
predicted = [1, 0, 1, 1]
actual    = [1, 1, 1, 0]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`zip` both lists together. Compare each pair with `==`, and add 1 to a counter each time they match.

</details>

<details>
<summary>✅ Answer</summary>

```python
predicted = [1, 0, 1, 1]
actual    = [1, 1, 1, 0]
matches = 0
for p, a in zip(predicted, actual):
    if p == a:
        matches += 1
print(matches)  # 2
```

**Why:** Position 0 matches (both `1`), position 2 matches (both `1`). Positions 1 and 3 differ. So the total is `2`.

</details>

---

### Q33 · List comprehension — Squares

**Problem:**
Create a list of the squares of numbers 1 to 10 using a list comprehension. The result should be `[1, 4, 9, 16, 25, 36, 49, 64, 81, 100]`.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

List comprehension format: `[expression for item in iterable]`. Use `n**2` for squaring.

</details>

<details>
<summary>✅ Answer</summary>

```python
squares = [n**2 for n in range(1, 11)]
print(squares)
```

**Why:** The comprehension loops through 1–10 and applies `n**2` to each number, collecting the results into a new list — all in one readable line.

</details>

---

### Q34 · List comprehension — Filter Evens

**Problem:**
`numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`. Use a list comprehension to create a new list containing only the even numbers.

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Add an `if` condition at the end of the comprehension: `[n for n in numbers if n % 2 == 0]`.

</details>

<details>
<summary>✅ Answer</summary>

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = [n for n in numbers if n % 2 == 0]
print(evens)  # [2, 4, 6, 8, 10]
```

**Why:** The `if` at the end acts as a filter. Only numbers that pass the `% 2 == 0` check are included in the new list.

</details>

---

### Q35 · List comprehension — Uppercase

**Problem:**
`words = ["hello", "world", "python"]`. Use a list comprehension to create a new list where every word is in uppercase.

```python
words = ["hello", "world", "python"]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`word.upper()` converts a single string to uppercase. Use that as the expression in your comprehension.

</details>

<details>
<summary>✅ Answer</summary>

```python
words = ["hello", "world", "python"]
upper_words = [word.upper() for word in words]
print(upper_words)  # ['HELLO', 'WORLD', 'PYTHON']
```

**Why:** The comprehension calls `.upper()` on each word as it loops. The result is a brand-new list — the original `words` list is unchanged.

</details>

---

### Q36 · Dict comprehension — Number Squares

**Problem:**
Create a dictionary where the keys are numbers 1 to 5 and the values are their squares. Expected result: `{1: 1, 2: 4, 3: 9, 4: 16, 5: 25}`.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Dict comprehension format: `{key: value for item in iterable}`. Use `n` as the key and `n**2` as the value.

</details>

<details>
<summary>✅ Answer</summary>

```python
squares = {n: n**2 for n in range(1, 6)}
print(squares)  # {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
```

**Why:** Dict comprehensions work the same as list comprehensions but use `{}` and require both a key and a value separated by `:`.

</details>

---

### Q37 · Dict comprehension — Invert a Dict

**Problem:**
`original = {"a": 1, "b": 2, "c": 3}`. Create a new dictionary with the keys and values swapped: `{1: "a", 2: "b", 3: "c"}`.

```python
original = {"a": 1, "b": 2, "c": 3}
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `.items()` to loop over both keys and values at once. In the comprehension, swap their positions — put the value as the key and the key as the value.

</details>

<details>
<summary>✅ Answer</summary>

```python
original = {"a": 1, "b": 2, "c": 3}
inverted = {v: k for k, v in original.items()}
print(inverted)  # {1: 'a', 2: 'b', 3: 'c'}
```

**Why:** `.items()` gives you each key-value pair. By writing `{v: k}` instead of `{k: v}`, you flip which side becomes the key and which becomes the value.

</details>
