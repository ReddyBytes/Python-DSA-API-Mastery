# 📦 Data Types — Practice Problems

> 45 problems · All concepts from the theory file  
> Write your answer in `practice_local.py` first, then use the dropdowns.

---

## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| [Q1](#q1)–Q4 | `int` | 🟢 |
| [Q5](#q5)–Q8 | `float` | 🟢 |
| [Q9](#q9)–Q11 | `bool` | 🟢 |
| [Q12](#q12)–Q18 | `str` | 🟢 |
| [Q19](#q19)–Q25 | `list` | 🟡 |
| [Q26](#q26)–Q30 | `tuple` | 🟡 |
| [Q31](#q31)–Q35 | `set` | 🟡 |
| [Q36](#q36)–Q42 | `dict` | 🟡 |
| [Q43](#q43)–Q44 | `None` | 🟢 |
| [Q45](#q45)–Q47 | Type Conversion | 🟡 |

---

<a id="q1"></a>

### Q1 · int — Leap Year Check

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


**Problem:**
`year = 2024`. Print `"Leap year"` if the year is divisible by 4, otherwise print `"Not a leap year"`.

```python
year = 2024
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use the `%` operator. If `year % 4 == 0`, it is a leap year.

</details>

<details>
<summary>✅ Answer</summary>

```python
year = 2024
if year % 4 == 0:
    print("Leap year")
else:
    print("Not a leap year")
```

**Why:** `%` gives the remainder after division. If a number divides evenly by 4, the remainder is 0.

</details>

---

<a id="q2"></a>

### Q2 · int — Even or Odd

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


**Problem:**
`number = 37`. Print `"Even"` if it is divisible by 2, otherwise print `"Odd"`.

```python
number = 37
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `number % 2`. If the result is 0, the number is even.

</details>

<details>
<summary>✅ Answer</summary>

```python
number = 37
if number % 2 == 0:
    print("Even")
else:
    print("Odd")
```

**Why:** Any number divisible by 2 has a remainder of 0. 37 % 2 = 1, so it is odd.

</details>

---

<a id="q3"></a>

### Q3 · int — Floor Division and Remainder

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


**Problem:**
`total_minutes = 145`. Print how many full hours and remaining minutes are in that total. Expected output: `"2 hours and 25 minutes"`.

```python
total_minutes = 145
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `//` for full hours and `%` for leftover minutes.

</details>

<details>
<summary>✅ Answer</summary>

```python
total_minutes = 145
hours = total_minutes // 60
mins = total_minutes % 60
print(f"{hours} hours and {mins} minutes")
```

**Why:** `//` gives the whole-number part of the division. `%` gives the remainder. Together they split any number of minutes into hours and minutes.

</details>

---

<a id="q4"></a>

### Q4 · int — Power and Absolute Value

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


**Problem:**
`base = 2`, `exponent = 8`. Print the result of 2 to the power of 8. Then print the absolute value of `-42`.

```python
base = 2
exponent = 8
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `**` for power and `abs()` for absolute value.

</details>

<details>
<summary>✅ Answer</summary>

```python
base = 2
exponent = 8
print(base ** exponent)   # 256
print(abs(-42))           # 42
```

**Why:** `**` is Python's exponent operator. `abs()` removes the negative sign from any number.

</details>

---

<a id="q5"></a>

### Q5 · float — Restaurant Bill

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


**Problem:**
`price = 250.00`, `gst_rate = 0.18` (18% GST). Calculate and print the total bill rounded to 2 decimal places.

```python
price = 250.00
gst_rate = 0.18
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

GST amount = price × rate. Total = price + GST amount. Use `round(value, 2)` to round to 2 decimal places.

</details>

<details>
<summary>✅ Answer</summary>

```python
price = 250.00
gst_rate = 0.18
gst = price * gst_rate
total = price + gst
print(round(total, 2))   # 295.0
```

**Why:** Multiplying by 0.18 gives 18% of the price. `round()` keeps the result tidy.

</details>

---

<a id="q6"></a>

### Q6 · float — BMI Calculator

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


**Problem:**
`weight = 70.0` kg, `height = 1.75` m. Calculate BMI using the formula `weight / height²`. Print it rounded to 1 decimal place.

```python
weight = 70.0
height = 1.75
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

BMI formula: `weight / (height ** 2)`. Use `round(bmi, 1)` to round to one decimal.

</details>

<details>
<summary>✅ Answer</summary>

```python
weight = 70.0
height = 1.75
bmi = weight / (height ** 2)
print(round(bmi, 1))   # 22.9
```

**Why:** Height must be squared in the formula — that is what `** 2` does. Without the brackets, only the division would happen first.

</details>

---

<a id="q7"></a>

### Q7 · float — Precision Trap

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


**Problem:**
Run `print(0.1 + 0.2 == 0.3)`. What does it print? Then fix the comparison using `round()`.

```python
print(0.1 + 0.2 == 0.3)   # what does this print?
# now fix it so the comparison returns True
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Floats have precision issues in computers. Compare rounded versions instead.

</details>

<details>
<summary>✅ Answer</summary>

```python
print(0.1 + 0.2 == 0.3)                     # False
print(round(0.1 + 0.2, 1) == round(0.3, 1)) # True
```

**Why:** Computers store floats in binary, which cannot represent 0.1 exactly. So `0.1 + 0.2` actually equals `0.30000000000000004` internally.

</details>

---

<a id="q8"></a>

### Q8 · float — Temperature Conversion

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


**Problem:**
`celsius = 100.0`. Convert it to Fahrenheit using the formula `F = (C × 9/5) + 32`. Print the result.

```python
celsius = 100.0
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Multiply celsius by 9, divide by 5, then add 32.

</details>

<details>
<summary>✅ Answer</summary>

```python
celsius = 100.0
fahrenheit = (celsius * 9 / 5) + 32
print(fahrenheit)   # 212.0
```

**Why:** This is the standard Celsius-to-Fahrenheit conversion formula. The brackets make the order of operations clear.

</details>

---

<a id="q9"></a>

### Q9 · bool — Truthiness

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


**Problem:**
For each value below, predict `True` or `False` before running. Then run the code to check.

```python
print(bool(0))
print(bool(""))
print(bool([]))
print(bool("hello"))
print(bool(42))
print(bool(None))
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`0`, empty string, empty list, and `None` are all falsy. Everything else is truthy.

</details>

<details>
<summary>✅ Answer</summary>

```python
print(bool(0))       # False
print(bool(""))      # False
print(bool([]))      # False
print(bool("hello")) # True
print(bool(42))      # True
print(bool(None))    # False
```

**Why:** Python treats "empty" or "zero" values as falsy. Any non-empty, non-zero value is truthy.

</details>

---

<a id="q10"></a>

### Q10 · bool — Bool Arithmetic

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


**Problem:**
`answers = [True, False, True, True, False]`. Use `sum()` to count how many are `True`. Print `"3 out of 5 correct"`.

```python
answers = [True, False, True, True, False]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`True` equals 1 and `False` equals 0 in Python. `sum()` adds them all up.

</details>

<details>
<summary>✅ Answer</summary>

```python
answers = [True, False, True, True, False]
correct = sum(answers)
print(f"{correct} out of {len(answers)} correct")
```

**Why:** Because `True == 1`, summing a list of booleans counts how many are `True`.

</details>

---

<a id="q11"></a>

### Q11 · bool — and / or Shortcuts

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


**Problem:**
`name = ""`. Use `or` to print the name if it is set, or `"Anonymous"` if it is empty.

```python
name = ""
# your code here — print either name or "Anonymous"
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`name or "Anonymous"` returns `name` if it is truthy, otherwise it returns `"Anonymous"`.

</details>

<details>
<summary>✅ Answer</summary>

```python
name = ""
print(name or "Anonymous")   # Anonymous
```

**Why:** An empty string is falsy, so `or` moves on to the second value and returns it.

</details>

---

<a id="q12"></a>

### Q12 · str — String Methods

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


**Problem:**
`email = "  Alice.SHARMA@Gmail.Com  "`. Clean it up: strip the whitespace from both ends and convert everything to lowercase. Print the result.

```python
email = "  Alice.SHARMA@Gmail.Com  "
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `.strip()` to remove whitespace, then `.lower()` to convert to lowercase. You can chain them together.

</details>

<details>
<summary>✅ Answer</summary>

```python
email = "  Alice.SHARMA@Gmail.Com  "
print(email.strip().lower())
# alice.sharma@gmail.com
```

**Why:** Methods can be chained. `.strip()` runs first, then `.lower()` runs on the cleaned result.

</details>

---

<a id="q13"></a>

### Q13 · str — Slicing

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


**Problem:**
`text = "Hello, World!"`. Print just `"World"` using slicing.

```python
text = "Hello, World!"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Count the character positions. `W` is at index 7, and you want 5 characters.

</details>

<details>
<summary>✅ Answer</summary>

```python
text = "Hello, World!"
print(text[7:12])   # World
```

**Why:** `text[7:12]` means start at index 7 and stop before index 12, giving you 5 characters.

</details>

---

<a id="q14"></a>

### Q14 · str — f-strings

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


**Problem:**
`name = "Alice"`, `age = 25`, `city = "Mumbai"`. Print: `"Alice is 25 years old and lives in Mumbai"` using an f-string.

```python
name = "Alice"
age = 25
city = "Mumbai"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

f-strings use curly braces `{}` to embed variables directly inside a string. Start the string with `f"..."`.

</details>

<details>
<summary>✅ Answer</summary>

```python
name = "Alice"
age = 25
city = "Mumbai"
print(f"{name} is {age} years old and lives in {city}")
```

**Why:** f-strings let you embed any variable or expression inside `{}` without using `+` to join strings.

</details>

---

<a id="q15"></a>

### Q15 · str — split and join

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


**Problem:**
`sentence = "apple,banana,cherry,date"`. Split it into a list, then join it back together with ` | ` as the separator.

```python
sentence = "apple,banana,cherry,date"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `.split(",")` to break it apart, then `" | ".join(list)` to put it back together.

</details>

<details>
<summary>✅ Answer</summary>

```python
sentence = "apple,banana,cherry,date"
parts = sentence.split(",")
print(" | ".join(parts))
# apple | banana | cherry | date
```

**Why:** `.split()` breaks a string into a list. `.join()` puts it back together with a new separator in between each item.

</details>

---

<a id="q16"></a>

### Q16 · str — Immutability

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


**Problem:**
`word = "hello"`. Try to change the first letter to `"H"` using `word[0] = "H"`. What error do you get? Then fix it the correct way.

```python
word = "hello"
# try: word[0] = "H"  — what happens?
# then fix it
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Strings cannot be changed in place. Create a new string instead by combining parts.

</details>

<details>
<summary>✅ Answer</summary>

```python
word = "hello"
# word[0] = "H"  → TypeError: 'str' object does not support item assignment

# Fix:
word = "H" + word[1:]
print(word)   # Hello
```

**Why:** Strings are immutable — you cannot change individual characters. You must build a new string from the parts you want.

</details>

---

<a id="q17"></a>

### Q17 · str — find and replace

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


**Problem:**
`message = "I love cats. Cats are amazing!"`. Replace all occurrences of `"cats"` with `"dogs"` and `"Cats"` with `"Dogs"`. Print the result.

```python
message = "I love cats. Cats are amazing!"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Call `.replace()` twice — once for the lowercase version and once for the capitalized version.

</details>

<details>
<summary>✅ Answer</summary>

```python
message = "I love cats. Cats are amazing!"
message = message.replace("cats", "dogs").replace("Cats", "Dogs")
print(message)
# I love dogs. Dogs are amazing!
```

**Why:** `.replace()` only matches exact text, so you need a separate call for each case you want to handle.

</details>

---

<a id="q18"></a>

### Q18 · str — Checking Content

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


**Problem:**
`phone = "9876543210"`. Check if it is a valid phone number: it must be all digits and exactly 10 characters long. Print `"Valid"` or `"Invalid"`.

```python
phone = "9876543210"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `.isdigit()` to check all characters are numbers, and `len()` to check the length. Combine them with `and`.

</details>

<details>
<summary>✅ Answer</summary>

```python
phone = "9876543210"
if phone.isdigit() and len(phone) == 10:
    print("Valid")
else:
    print("Invalid")
```

**Why:** `.isdigit()` returns `True` only if every character is a digit. `len()` checks the count. Both must be true.

</details>

---

<a id="q19"></a>

### Q19 · list — CRUD Operations

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


**Problem:**
Start with `cart = []`. Add `"Apples"`, `"Milk"`, and `"Bread"` to it. Then remove `"Milk"`. Print the cart and its length.

```python
cart = []
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `.append()` to add items one at a time. Use `.remove()` to delete an item by its value.

</details>

<details>
<summary>✅ Answer</summary>

```python
cart = []
cart.append("Apples")
cart.append("Milk")
cart.append("Bread")
cart.remove("Milk")
print(cart)       # ['Apples', 'Bread']
print(len(cart))  # 2
```

**Why:** `.append()` adds to the end of the list. `.remove()` finds the first matching item and deletes it.

</details>

---

<a id="q20"></a>

### Q20 · list — Slicing

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


**Problem:**
`scores = [88, 92, 75, 96, 83, 70, 91]`. Print the first 3 scores, the last 2 scores, and a reversed copy — all using slicing.

```python
scores = [88, 92, 75, 96, 83, 70, 91]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`list[:3]` is the first 3, `list[-2:]` is the last 2, and `list[::-1]` reverses the list.

</details>

<details>
<summary>✅ Answer</summary>

```python
scores = [88, 92, 75, 96, 83, 70, 91]
print(scores[:3])    # [88, 92, 75]
print(scores[-2:])   # [70, 91]
print(scores[::-1])  # [91, 70, 83, 96, 75, 92, 88]
```

**Why:** Negative indices count from the end of the list. `[::-1]` uses a step of -1, which walks through the list backwards.

</details>

---

<a id="q21"></a>

### Q21 · list — Sort and Find

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)


**Problem:**
`temps = [34, 28, 39, 22, 31, 41, 27]`. Find and print the highest temperature, the lowest, and the average.

```python
temps = [34, 28, 39, 22, 31, 41, 27]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `max()`, `min()`, and `sum() / len()` for the average.

</details>

<details>
<summary>✅ Answer</summary>

```python
temps = [34, 28, 39, 22, 31, 41, 27]
print(max(temps))                    # 41
print(min(temps))                    # 22
print(round(sum(temps) / len(temps), 1))  # 31.7
```

**Why:** Python has built-in functions for these common tasks — no need to write a loop manually.

</details>

---

<a id="q22"></a>

### Q22 · list — Copy Trap

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)


**Problem:**
`a = [1, 2, 3]`. Do `b = a`, then append `4` to `b`. Print both `a` and `b`. What happens? Then fix it so that `a` does not change.

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

`b = a` makes both variables point to the same list. Use `b = a.copy()` or `b = a[:]` to make a real copy.

</details>

<details>
<summary>✅ Answer</summary>

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)   # [1, 2, 3, 4]  ← a changed too!
print(b)   # [1, 2, 3, 4]

# Fix:
a = [1, 2, 3]
b = a.copy()
b.append(4)
print(a)   # [1, 2, 3]  ← a is safe now
print(b)   # [1, 2, 3, 4]
```

**Why:** Lists are mutable. Assignment does not copy — it just gives the same list a second name. `.copy()` creates a brand new list.

</details>

---

<a id="q23"></a>

### Q23 · list — List Comprehension

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)


**Problem:**
`numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`. Create a new list containing only the even numbers using a list comprehension.

```python
numbers = list(range(1, 11))
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

The pattern is `[x for x in numbers if x % 2 == 0]`.

</details>

<details>
<summary>✅ Answer</summary>

```python
numbers = list(range(1, 11))
evens = [x for x in numbers if x % 2 == 0]
print(evens)   # [2, 4, 6, 8, 10]
```

**Why:** A list comprehension is a compact way to filter or transform a list in a single line — no need for a separate `for` loop and `.append()`.

</details>

---

<a id="q24"></a>

### Q24 · list — Nested List

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)


**Problem:**
`matrix = [[1,2,3],[4,5,6],[7,8,9]]`. Print the value `6` by accessing it using its row and column index.

```python
matrix = [[1,2,3],[4,5,6],[7,8,9]]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Row 1 (index 1) contains `[4, 5, 6]`. Column 2 (index 2) is `6`.

</details>

<details>
<summary>✅ Answer</summary>

```python
matrix = [[1,2,3],[4,5,6],[7,8,9]]
print(matrix[1][2])   # 6
```

**Why:** `matrix[1]` gets the second row `[4, 5, 6]`. Then `[2]` gets the third item in that row.

</details>

---

<a id="q25"></a>

### Q25 · list — Count and Index

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)


**Problem:**
`fruits = ["apple", "banana", "apple", "cherry", "apple"]`. Count how many times `"apple"` appears, and find the index of `"cherry"`.

```python
fruits = ["apple", "banana", "apple", "cherry", "apple"]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `.count()` to count occurrences and `.index()` to find the position.

</details>

<details>
<summary>✅ Answer</summary>

```python
fruits = ["apple", "banana", "apple", "cherry", "apple"]
print(fruits.count("apple"))    # 3
print(fruits.index("cherry"))   # 3
```

**Why:** `.count()` counts how many times a value appears. `.index()` returns the position of the first match.

</details>

---

<a id="q26"></a>

### Q26 · tuple — Immutability

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)


**Problem:**
`coords = (19.07, 72.87)`. Try to change the first value to `18.0`. What error do you get? Then show the correct way to update a tuple.

```python
coords = (19.07, 72.87)
# try: coords[0] = 18.0  — what happens?
# then show the fix
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

You cannot change a tuple. Create a new one instead, reusing the parts you want to keep.

</details>

<details>
<summary>✅ Answer</summary>

```python
coords = (19.07, 72.87)
# coords[0] = 18.0  → TypeError: 'tuple' object does not support item assignment

# Fix: create a new tuple
coords = (18.0, coords[1])
print(coords)   # (18.0, 72.87)
```

**Why:** Tuples are immutable by design — they are meant to hold data that should never change. You must build a new tuple if you need different values.

</details>

---

<a id="q27"></a>

### Q27 · tuple — Unpacking

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)


**Problem:**
`person = ("Alice", 25, "Engineer", "Mumbai")`. Unpack all 4 values into separate variables and print each one.

```python
person = ("Alice", 25, "Engineer", "Mumbai")
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

You can unpack a tuple like this: `name, age, job, city = person`.

</details>

<details>
<summary>✅ Answer</summary>

```python
person = ("Alice", 25, "Engineer", "Mumbai")
name, age, job, city = person
print(name)   # Alice
print(age)    # 25
print(job)    # Engineer
print(city)   # Mumbai
```

**Why:** Tuple unpacking assigns each item in the tuple to a variable in one clean line, in order.

</details>

---

<a id="q28"></a>

### Q28 · tuple — Swap Variables

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)


**Problem:**
`a = 10`, `b = 20`. Swap their values using Python's tuple unpacking in a single line. Print both after the swap.

```python
a = 10
b = 20
# swap in one line
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Python allows `a, b = b, a` — it evaluates the right side first, then unpacks.

</details>

<details>
<summary>✅ Answer</summary>

```python
a = 10
b = 20
a, b = b, a
print(a)   # 20
print(b)   # 10
```

**Why:** Python evaluates the right side first, packs the values into a temporary tuple, then unpacks them into `a` and `b` in one step.

</details>

---

<a id="q29"></a>

### Q29 · tuple — When to Use Tuple

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)


**Problem:**
`rgb_red = [255, 0, 0]` is stored as a list. Is this the right type? Convert it to a tuple and explain why a tuple is better here.

```python
rgb_red = [255, 0, 0]
# convert to the correct type
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

RGB values never change. Use `tuple()` to convert. A tuple signals "this data is fixed".

</details>

<details>
<summary>✅ Answer</summary>

```python
rgb_red = [255, 0, 0]
rgb_red = tuple(rgb_red)
print(rgb_red)   # (255, 0, 0)
```

**Why:** RGB values are fixed constants — they represent a specific color and should never be modified. Using a tuple makes that intention clear, and tuples use slightly less memory than lists.

</details>

---

<a id="q30"></a>

### Q30 · tuple — Tuple in a Set

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)


**Problem:**
Try adding a list `[1, 2]` to a set. Then try adding a tuple `(1, 2)`. Which one works? Why?

```python
s = set()
# try s.add([1, 2])
# try s.add((1, 2))
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Sets require items that are hashable. Lists are mutable and not hashable. Tuples are immutable and hashable.

</details>

<details>
<summary>✅ Answer</summary>

```python
s = set()
# s.add([1, 2])   → TypeError: unhashable type: 'list'
s.add((1, 2))     # works fine
print(s)          # {(1, 2)}
```

**Why:** Sets store items using hash values. Tuples are immutable so they can be hashed; lists can change so they cannot.

</details>

---

<a id="q31"></a>

### Q31 · set — Remove Duplicates

> 🛠️ **Solve locally:** [practice_local.py → Q31](./practice_local.py)


**Problem:**
`emails = ["a@x.com","b@x.com","a@x.com","c@x.com","b@x.com"]`. Remove duplicates and print the unique emails as a list.

```python
emails = ["a@x.com", "b@x.com", "a@x.com", "c@x.com", "b@x.com"]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Convert the list to a set to remove duplicates, then convert back to a list.

</details>

<details>
<summary>✅ Answer</summary>

```python
emails = ["a@x.com", "b@x.com", "a@x.com", "c@x.com", "b@x.com"]
unique = list(set(emails))
print(unique)
# ['a@x.com', 'b@x.com', 'c@x.com']  (order may vary)
```

**Why:** Sets automatically discard duplicates. Converting back to a list makes it easier to use with other code.

</details>

---

<a id="q32"></a>

### Q32 · set — Membership Check

> 🛠️ **Solve locally:** [practice_local.py → Q32](./practice_local.py)


**Problem:**
`valid_countries = {"India", "USA", "UK", "Germany", "Japan"}`. Check if `"Australia"` and `"India"` are in the set. Print `True` or `False` for each.

```python
valid_countries = {"India", "USA", "UK", "Germany", "Japan"}
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use the `in` keyword to check membership.

</details>

<details>
<summary>✅ Answer</summary>

```python
valid_countries = {"India", "USA", "UK", "Germany", "Japan"}
print("Australia" in valid_countries)   # False
print("India" in valid_countries)       # True
```

**Why:** Checking membership in a set is very fast — it takes the same amount of time whether the set has 5 items or 5 million.

</details>

---

<a id="q33"></a>

### Q33 · set — Set Math

> 🛠️ **Solve locally:** [practice_local.py → Q33](./practice_local.py)


**Problem:**
`python_students = {"Alice","Bob","Charlie","Diana"}`, `sql_students = {"Bob","Eve","Charlie","Frank"}`. Find: who is in both classes, who is in either class, and who is only in the Python class.

```python
python_students = {"Alice", "Bob", "Charlie", "Diana"}
sql_students = {"Bob", "Eve", "Charlie", "Frank"}
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `&` for intersection (both), `|` for union (either), `-` for difference (only in the first).

</details>

<details>
<summary>✅ Answer</summary>

```python
python_students = {"Alice", "Bob", "Charlie", "Diana"}
sql_students = {"Bob", "Eve", "Charlie", "Frank"}

print(python_students & sql_students)   # {'Bob', 'Charlie'}
print(python_students | sql_students)   # all 6 students
print(python_students - sql_students)   # {'Alice', 'Diana'}
```

**Why:** Set operators mirror mathematical set theory. `&` is AND, `|` is OR, `-` is MINUS.

</details>

---

<a id="q34"></a>

### Q34 · set — discard vs remove

> 🛠️ **Solve locally:** [practice_local.py → Q34](./practice_local.py)


**Problem:**
`tags = {"python", "web", "api", "ml"}`. Remove `"ml"` safely. Also try to remove `"java"` safely even though it does not exist. Which method should you use?

```python
tags = {"python", "web", "api", "ml"}
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`.remove()` raises an error if the item is not found. `.discard()` does nothing — no error.

</details>

<details>
<summary>✅ Answer</summary>

```python
tags = {"python", "web", "api", "ml"}
tags.discard("ml")     # removes it
tags.discard("java")   # does nothing, no error
print(tags)            # {'python', 'web', 'api'}
```

**Why:** Use `.discard()` when you are not sure if the item exists. It is the safe option — `.remove()` would crash if the item is missing.

</details>

---

<a id="q35"></a>

### Q35 · set — frozenset

> 🛠️ **Solve locally:** [practice_local.py → Q35](./practice_local.py)


**Problem:**
Create a `frozenset` from `["red", "green", "blue"]`. Try to add `"yellow"` to it. What error do you get? When would you use a frozenset?

```python
colors = frozenset(["red", "green", "blue"])
# try: colors.add("yellow")  — what happens?
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

A frozenset is immutable — you cannot add or remove items once it is created.

</details>

<details>
<summary>✅ Answer</summary>

```python
colors = frozenset(["red", "green", "blue"])
# colors.add("yellow")  → AttributeError: 'frozenset' object has no attribute 'add'

print(colors)   # frozenset({'red', 'green', 'blue'})
```

**Why:** A frozenset is hashable because it is immutable, which means you can use it as a dictionary key or put it inside another set — things you cannot do with a regular set.

</details>

---

<a id="q36"></a>

### Q36 · dict — Create and Access

> 🛠️ **Solve locally:** [practice_local.py → Q36](./practice_local.py)


**Problem:**
Create a dictionary for a book with these fields: title `"Python Crash Course"`, author `"Eric Matthes"`, year `2019`, pages `544`. Print the author and the year.

```python
# create the dict and print author and year
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `{}` to define the dict. Use `dict["key"]` to access values by their key name.

</details>

<details>
<summary>✅ Answer</summary>

```python
book = {
    "title": "Python Crash Course",
    "author": "Eric Matthes",
    "year": 2019,
    "pages": 544
}
print(book["author"])   # Eric Matthes
print(book["year"])     # 2019
```

**Why:** Dictionary keys act like labels. You look up values by their name instead of by a number position.

</details>

---

<a id="q37"></a>

### Q37 · dict — Safe Access with .get()

> 🛠️ **Solve locally:** [practice_local.py → Q37](./practice_local.py)


**Problem:**
`config = {"host": "localhost", "port": 5432}`. Get the value of `"timeout"` without crashing — return a default of `30` if it does not exist.

```python
config = {"host": "localhost", "port": 5432}
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `.get("key", default)` instead of `dict["key"]`.

</details>

<details>
<summary>✅ Answer</summary>

```python
config = {"host": "localhost", "port": 5432}
print(config.get("timeout", 30))   # 30
```

**Why:** `dict["key"]` raises a `KeyError` if the key is missing. `.get()` returns the default value instead — much safer for optional settings.

</details>

---

<a id="q38"></a>

### Q38 · dict — Update and Delete

> 🛠️ **Solve locally:** [practice_local.py → Q38](./practice_local.py)


**Problem:**
`user = {"name": "Alice", "age": 25, "city": "Delhi"}`. Update the age to `26`. Add a new key `"email"` with value `"alice@gmail.com"`. Delete the `"city"` key. Print the final dict.

```python
user = {"name": "Alice", "age": 25, "city": "Delhi"}
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`dict["key"] = value` updates or adds a key. `del dict["key"]` removes a key.

</details>

<details>
<summary>✅ Answer</summary>

```python
user = {"name": "Alice", "age": 25, "city": "Delhi"}
user["age"] = 26
user["email"] = "alice@gmail.com"
del user["city"]
print(user)
# {'name': 'Alice', 'age': 26, 'email': 'alice@gmail.com'}
```

**Why:** Dicts are mutable — you can freely add, update, or remove keys at any time.

</details>

---

<a id="q39"></a>

### Q39 · dict — Iterating

> 🛠️ **Solve locally:** [practice_local.py → Q39](./practice_local.py)


**Problem:**
`scores = {"Alice": 92, "Bob": 78, "Charlie": 85, "Diana": 96}`. Loop through and print each name and score. Then print only the names where the score is above 85.

```python
scores = {"Alice": 92, "Bob": 78, "Charlie": 85, "Diana": 96}
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `.items()` to get key-value pairs. Use an `if` condition to filter.

</details>

<details>
<summary>✅ Answer</summary>

```python
scores = {"Alice": 92, "Bob": 78, "Charlie": 85, "Diana": 96}

for name, score in scores.items():
    print(f"{name}: {score}")

print("Above 85:")
for name, score in scores.items():
    if score > 85:
        print(name)
```

**Why:** `.items()` gives you both the key and the value in each step of the loop, which is exactly what you need when working with dicts.

</details>

---

<a id="q40"></a>

### Q40 · dict — Word Counter

> 🛠️ **Solve locally:** [practice_local.py → Q40](./practice_local.py)


**Problem:**
`text = "the cat sat on the mat the cat"`. Count how many times each word appears and store the counts in a dict. Print the result.

```python
text = "the cat sat on the mat the cat"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Split the text into words. For each word, use `.get(word, 0) + 1` to safely increment the count.

</details>

<details>
<summary>✅ Answer</summary>

```python
text = "the cat sat on the mat the cat"
freq = {}
for word in text.split():
    freq[word] = freq.get(word, 0) + 1
print(freq)
# {'the': 3, 'cat': 2, 'sat': 1, 'on': 1, 'mat': 1}
```

**Why:** `.get(word, 0)` returns `0` if the word has not been seen yet. Adding `1` gives us the first count, and every time we see the word again we add another `1`.

</details>

---

<a id="q41"></a>

### Q41 · dict — Nested Dict

> 🛠️ **Solve locally:** [practice_local.py → Q41](./practice_local.py)


**Problem:**
`student = {"name": "Alice", "grades": {"math": 90, "science": 85, "english": 92}}`. Print the science grade. Then add `"history": 88` to the grades.

```python
student = {"name": "Alice", "grades": {"math": 90, "science": 85, "english": 92}}
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `student["grades"]["science"]` to access a value inside a nested dict.

</details>

<details>
<summary>✅ Answer</summary>

```python
student = {"name": "Alice", "grades": {"math": 90, "science": 85, "english": 92}}
print(student["grades"]["science"])       # 85
student["grades"]["history"] = 88
print(student["grades"])
# {'math': 90, 'science': 85, 'english': 92, 'history': 88}
```

**Why:** Nested dicts are accessed by chaining keys — like opening a folder inside a folder.

</details>

---

<a id="q42"></a>

### Q42 · dict — Dict Comprehension

> 🛠️ **Solve locally:** [practice_local.py → Q42](./practice_local.py)


**Problem:**
`names = ["Alice", "Bob", "Charlie"]`, `scores = [92, 78, 85]`. Create a dict `{name: score}` using a dict comprehension and `zip`.

```python
names = ["Alice", "Bob", "Charlie"]
scores = [92, 78, 85]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`zip(names, scores)` pairs the two lists together. Then use a dict comprehension: `{k: v for k, v in zip(...)}`.

</details>

<details>
<summary>✅ Answer</summary>

```python
names = ["Alice", "Bob", "Charlie"]
scores = [92, 78, 85]
result = {name: score for name, score in zip(names, scores)}
print(result)
# {'Alice': 92, 'Bob': 78, 'Charlie': 85}
```

**Why:** `zip()` pairs up the two lists item by item. The dict comprehension then builds the dict in one clean line.

</details>

---

<a id="q43"></a>

### Q43 · None — Identity Check

> 🛠️ **Solve locally:** [practice_local.py → Q43](./practice_local.py)


**Problem:**
`result = None`. Check if it is `None` using both `==` and `is`. Which is the correct way? Print the result of both checks.

```python
result = None
# check using == and is
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

For `None`, always use `is None` rather than `== None`. Both work here, but `is` is more correct.

</details>

<details>
<summary>✅ Answer</summary>

```python
result = None
print(result == None)   # True
print(result is None)   # True  ← prefer this
```

**Why:** `is` checks if two variables point to the exact same object in memory. `None` is a singleton — there is only one `None` in all of Python — so `is None` is the correct and Pythonic way to check for it.

</details>

---

<a id="q44"></a>

### Q44 · None — Optional Value

> 🛠️ **Solve locally:** [practice_local.py → Q44](./practice_local.py)


**Problem:**
`middle_name = None`. Print `"No middle name"` if it is `None`, otherwise print the name.

```python
middle_name = None
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `if middle_name is None` to check.

</details>

<details>
<summary>✅ Answer</summary>

```python
middle_name = None
if middle_name is None:
    print("No middle name")
else:
    print(middle_name)
```

**Why:** `None` is the standard way to represent "no value" in Python — like an empty box. Checking for it explicitly makes the code easy to read.

</details>

---

<a id="q45"></a>

### Q45 · Type Conversion — int and float

> 🛠️ **Solve locally:** [practice_local.py → Q45](./practice_local.py)


**Problem:**
`price_str = "199.99"`. Convert it to a float, add 18% GST, and print the total rounded to 2 decimal places.

```python
price_str = "199.99"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `float(price_str)` to convert the string. Then multiply by `1.18` to add 18% in one step.

</details>

<details>
<summary>✅ Answer</summary>

```python
price_str = "199.99"
price = float(price_str)
total = price * 1.18
print(round(total, 2))   # 235.99
```

**Why:** Data from files, forms, and `input()` always comes as a string. You must convert it before doing any maths.

</details>

---

<a id="q46"></a>

### Q46 · Type Conversion — The input() Trap

> 🛠️ **Solve locally:** [practice_local.py → Q46](./practice_local.py)


**Problem:**
Ask for a number using `input()` and try to add 10 to it. Show the error first, then fix it.

```python
# number = input("Enter a number: ")
# print(number + 10)  ← what error?
# now fix it
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`input()` always returns a string, even if the user types a number. Convert with `int()` before doing arithmetic.

</details>

<details>
<summary>✅ Answer</summary>

```python
# Without fix:
# number = input("Enter a number: ")
# print(number + 10)  → TypeError: can only concatenate str (not "int") to str

# Fix:
number = int(input("Enter a number: "))
print(number + 10)
```

**Why:** Python will not silently convert strings to numbers — you must do it explicitly. This is a very common beginner mistake.

</details>

---

<a id="q47"></a>

### Q47 · Type Conversion — bool conversion

> 🛠️ **Solve locally:** [practice_local.py → Q47](./practice_local.py)


**Problem:**
Convert each value in the list to `bool` and print the result. Predict first, then verify by running it.

```python
values = [0, 1, "", "hello", [], [1, 2, 3], None]
# print bool() of each value
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Zero, empty, and `None` are `False`. Everything else is `True`.

</details>

<details>
<summary>✅ Answer</summary>

```python
values = [0, 1, "", "hello", [], [1, 2, 3], None]
for v in values:
    print(v, "→", bool(v))

# 0 → False
# 1 → True
# "" → False
# hello → True
# [] → False
# [1, 2, 3] → True
# None → False
```

**Why:** Knowing which values are truthy and which are falsy is essential for writing clean `if` statements without needing to compare to `0`, `""`, or `None` explicitly.

</details>
