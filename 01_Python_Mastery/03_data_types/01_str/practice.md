# 🔤 str — Practice Problems

> 15 problems · Strings from basics to real-world patterns
> Write your answer in `practice_local.py` first, then use the dropdowns.

---

## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| [Q1](#q1)–Q3 | Creating strings · f-strings | 🟢 |
| [Q4](#q4)–Q6 | Indexing · Slicing | 🟢 |
| [Q7](#q7)–Q10 | String methods | 🟡 |
| [Q11](#q11)–Q12 | Immutability · replace | 🟡 |
| [Q13](#q13)–Q15 | Real-world patterns | 🟡 |

---

<a id="q1"></a>

### Q1 · str — Creating Strings

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


**Problem:**
Create a string three different ways: using single quotes, double quotes, and triple quotes. Print all three.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Single and double quotes work identically for single-line strings. Triple quotes (`"""` or `'''`) allow the string to span multiple lines.

</details>

<details>
<summary>✅ Answer</summary>

```python
single = 'Hello, World!'
double = "Hello, World!"
triple = """This string
spans multiple
lines."""

print(single)
print(double)
print(triple)
```

**Why:** Python accepts all three. Single and double quotes are interchangeable — pick one and be consistent. Triple quotes are the go-to for multi-line strings, docstrings, and blocks of text that contain both `'` and `"` characters.

</details>

---

<a id="q2"></a>

### Q2 · str — f-strings

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


**Problem:**
`name = "Alice"`, `age = 25`. Print `"Alice is 25 years old"` using an f-string. Then also print `"Next year Alice will be 26"` — compute the age inside the f-string.

```python
name = "Alice"
age = 25
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

f-strings start with `f"..."`. Anything inside `{}` is evaluated as Python code, so you can put expressions like `age + 1` directly in there.

</details>

<details>
<summary>✅ Answer</summary>

```python
name = "Alice"
age = 25
print(f"{name} is {age} years old")
print(f"Next year {name} will be {age + 1}")
```

**Why:** f-strings let you embed any variable or expression inside `{}` without string concatenation. They are faster to read and write than `"Hello " + name` or `"Hello %s" % name`.

</details>

---

<a id="q3"></a>

### Q3 · str — Raw Strings

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


**Problem:**
Print `\n` literally (as two characters: backslash and n) without it being treated as a newline. Show two ways to do it.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Prefix the string with `r` to make it a raw string. Alternatively, escape the backslash with another backslash: `\\n`.

</details>

<details>
<summary>✅ Answer</summary>

```python
# Way 1: raw string — backslashes are treated as literal characters
print(r"\n")        # \n

# Way 2: escape the backslash
print("\\n")        # \n
```

**Why:** In a normal string, `\n` is a special sequence meaning "newline". A raw string `r"..."` tells Python to ignore all escape sequences — every `\` is just a `\`. This is especially useful for Windows file paths (`r"C:\Users\Alice"`) and regex patterns.

</details>

---

<a id="q4"></a>

### Q4 · str — Indexing

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


**Problem:**
`text = "Python"`. Print the first character, the last character, and the second-to-last character. Use both positive and negative indexing.

```python
text = "Python"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Index 0 is the first character. Index -1 is the last. Index -2 is the second-to-last.

</details>

<details>
<summary>✅ Answer</summary>

```python
text = "Python"
print(text[0])    # P   ← first character (positive index)
print(text[-1])   # n   ← last character (negative index)
print(text[5])    # n   ← last character (positive index)
print(text[-2])   # o   ← second-to-last
```

**Why:** Positive indices count from the left starting at 0. Negative indices count from the right starting at -1. Negative indexing is cleaner when you need characters from the end and do not want to calculate the length first.

</details>

---

<a id="q5"></a>

### Q5 · str — Slicing

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


**Problem:**
`text = "Hello, World!"`. Print `"World"` using slicing. Then print just `"Hello"` using slicing.

```python
text = "Hello, World!"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Count the character positions. `W` is at index 7. `H` is at index 0 and the comma is at index 5.

</details>

<details>
<summary>✅ Answer</summary>

```python
text = "Hello, World!"
print(text[7:12])   # World  → start at index 7, stop before 12
print(text[0:5])    # Hello  → start at 0, stop before 5
```

**Why:** Slicing syntax is `s[start:stop]`. The start index is included, the stop index is excluded. So `text[7:12]` gives characters at positions 7, 8, 9, 10, 11 — which spells "World".

</details>

---

<a id="q6"></a>

### Q6 · str — Slicing with Step

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


**Problem:**
`text = "abcdefgh"`. Print every other character (a, c, e, g). Then print the string reversed.

```python
text = "abcdefgh"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

The third argument in a slice is the step. `[::2]` means "every 2nd character". `[::-1]` means "step backwards by 1" which reverses the string.

</details>

<details>
<summary>✅ Answer</summary>

```python
text = "abcdefgh"
print(text[::2])    # aceg  → every other character
print(text[::-1])   # hgfedcba  → reversed
```

**Why:** The full slice syntax is `s[start:stop:step]`. Leaving start and stop empty means "the whole string". A step of 2 skips every other character. A step of -1 walks through the string backwards from end to start — the classic one-liner for reversing a string in Python.

</details>

---

<a id="q7"></a>

### Q7 · str — String Methods

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


**Problem:**
`email = "  Alice.SHARMA@Gmail.Com  "`. Strip the whitespace from both ends and convert everything to lowercase in a single chained expression. Print the result.

```python
email = "  Alice.SHARMA@Gmail.Com  "
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`.strip()` removes leading and trailing whitespace. `.lower()` converts all characters to lowercase. You can chain methods: `email.strip().lower()`.

</details>

<details>
<summary>✅ Answer</summary>

```python
email = "  Alice.SHARMA@Gmail.Com  "
print(email.strip().lower())
# alice.sharma@gmail.com
```

**Why:** Methods can be chained because each one returns a new string. `.strip()` runs first and returns a cleaned string; `.lower()` then runs on that result. This is a standard pattern for normalising user input before storing it in a database.

</details>

---

<a id="q8"></a>

### Q8 · str — split and join

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


**Problem:**
`sentence = "apple,banana,cherry"`. Split it by the comma into a list. Then join the list back together using ` - ` as the separator.

```python
sentence = "apple,banana,cherry"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`.split(",")` breaks the string on every comma. `" - ".join(list)` puts the items back together with ` - ` in between each one.

</details>

<details>
<summary>✅ Answer</summary>

```python
sentence = "apple,banana,cherry"
parts = sentence.split(",")
print(parts)                  # ['apple', 'banana', 'cherry']
print(" - ".join(parts))      # apple - banana - cherry
```

**Why:** `.split()` and `.join()` are inverses of each other. `.split()` turns a string into a list; `.join()` turns a list back into a string. Note that `.join()` is called on the separator, not on the list — this catches many beginners off-guard.

</details>

---

<a id="q9"></a>

### Q9 · str — find and replace

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


**Problem:**
`msg = "I love cats. Cats are great!"`. Replace `"cats"` with `"dogs"` and `"Cats"` with `"Dogs"`. Print the result.

```python
msg = "I love cats. Cats are great!"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`.replace()` is case-sensitive — it will only match the exact text you give it. Chain two calls: one for the lowercase version, one for the capitalised version.

</details>

<details>
<summary>✅ Answer</summary>

```python
msg = "I love cats. Cats are great!"
msg = msg.replace("cats", "dogs").replace("Cats", "Dogs")
print(msg)
# I love dogs. Dogs are great!
```

**Why:** `.replace(old, new)` returns a new string with all occurrences of `old` replaced by `new`. Because it is case-sensitive, `"cats"` and `"Cats"` are different matches and need separate calls.

</details>

---

<a id="q10"></a>

### Q10 · str — String Checking

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


**Problem:**
`phone = "9876543210"`. Check that it is a valid phone number: all digits and exactly 10 characters long. Print `"Valid"` or `"Invalid"`.

```python
phone = "9876543210"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`.isdigit()` returns `True` if every character is a digit. `len()` returns the length. Both conditions must be true.

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

**Why:** `.isdigit()` returns `True` only if every character is a digit 0–9. `len()` checks the count. Using `and` means both conditions must hold simultaneously — either one failing means the phone number is invalid.

</details>

---

<a id="q11"></a>

### Q11 · str — Immutability

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


**Problem:**
`word = "hello"`. Try to change the first character to `"H"` using `word[0] = "H"`. What error do you get? Then fix it the correct way and print `"Hello"`.

```python
word = "hello"
# try: word[0] = "H"  — what happens?
# then fix it
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Strings are immutable — you cannot change a character in place. Build a new string by combining the replacement character with a slice of the original.

</details>

<details>
<summary>✅ Answer</summary>

```python
word = "hello"
# word[0] = "H"  → TypeError: 'str' object does not support item assignment

# Fix — build a new string:
word = "H" + word[1:]
print(word)   # Hello
```

**Why:** Every string operation creates a new string; none of them modify the original. `word[1:]` gives `"ello"`, and `"H" + "ello"` gives a brand new string `"Hello"`. The variable `word` is then pointed at this new string.

</details>

---

<a id="q12"></a>

### Q12 · str — Count and Find

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


**Problem:**
`text = "banana"`. Count how many times the letter `"a"` appears. Find the index of the first occurrence of `"n"`.

```python
text = "banana"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`.count(sub)` returns how many times `sub` appears in the string. `.find(sub)` returns the index of the first match, or `-1` if not found.

</details>

<details>
<summary>✅ Answer</summary>

```python
text = "banana"
print(text.count("a"))   # 3
print(text.find("n"))    # 2
```

**Why:** `.count()` scans the whole string and tallies matches. `.find()` stops at the first match and returns its index. Both are case-sensitive. If `.find()` returns `-1` it means the substring was not found — useful for membership checks when you also need the position.

</details>

---

<a id="q13"></a>

### Q13 · str — Real-world CSV Parsing

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


**Problem:**
`line = "Alice,28,Mumbai,Engineer"`. Split this CSV line into exactly 4 variables: `name`, `age`, `city`, `role`. Print each one on its own line.

```python
line = "Alice,28,Mumbai,Engineer"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`.split(",")` returns a list. You can unpack a list directly into variables: `a, b, c, d = some_list`.

</details>

<details>
<summary>✅ Answer</summary>

```python
line = "Alice,28,Mumbai,Engineer"
name, age, city, role = line.split(",")
print(name)   # Alice
print(age)    # 28
print(city)   # Mumbai
print(role)   # Engineer
```

**Why:** `.split(",")` breaks the line into a list of 4 strings. Unpacking assigns each item to a named variable in one clean step. This pattern — split a delimited string and unpack — is the foundation of manual CSV parsing and comes up constantly when processing log lines, config files, and API responses.

</details>

---

<a id="q14"></a>

### Q14 · str — Real-world Email Validation

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


**Problem:**
Write a function that checks whether a string is a valid email address. It must contain `"@"` AND end with either `".com"` or `".in"`. Test it on `"user@example.com"`, `"bad-email"`, and `"user@site.in"`.

```python
def is_valid_email(email):
    # your code here
    pass

print(is_valid_email("user@example.com"))   # True
print(is_valid_email("bad-email"))          # False
print(is_valid_email("user@site.in"))       # True
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `"@" in email` to check for the at-sign. Use `.endswith((".com", ".in"))` — you can pass a tuple of suffixes to `.endswith()` and it will match any of them.

</details>

<details>
<summary>✅ Answer</summary>

```python
def is_valid_email(email):
    return "@" in email and email.endswith((".com", ".in"))

print(is_valid_email("user@example.com"))   # True
print(is_valid_email("bad-email"))          # False
print(is_valid_email("user@site.in"))       # True
```

**Why:** `"@" in email` is a membership check — it returns `True` if `"@"` appears anywhere in the string. `.endswith()` accepts a tuple of options and returns `True` if the string ends with any one of them. Together they form a lightweight validation rule that covers the most common invalid formats without needing regex.

</details>

---

<a id="q15"></a>

### Q15 · str — Real-world Word Manipulation

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


**Problem:**
`text = "the quick brown fox"`. Do two things:
1. Capitalise every word using a single method call.
2. Reverse the order of the words (so it reads `"fox brown quick the"`).

```python
text = "the quick brown fox"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`.title()` capitalises the first letter of every word. To reverse word order: `.split()` gives a list of words, reverse the list, then `.join()` puts it back together.

</details>

<details>
<summary>✅ Answer</summary>

```python
text = "the quick brown fox"

# Capitalise every word
print(text.title())                        # The Quick Brown Fox

# Reverse the word order
words = text.split()
words.reverse()
print(" ".join(words))                     # fox brown quick the

# One-liner version of the reverse:
print(" ".join(text.split()[::-1]))        # fox brown quick the
```

**Why:** `.title()` applies `.capitalize()` to each word in one pass. Reversing word order is a split → reverse → join pipeline — the same three-step pattern used to reverse CSV columns, reorder log fields, and flip name formats (first last → last first). The `[::-1]` slice on a list reverses it without modifying the original.

</details>

---

**[🏠 Back to Data Types](../theory.md)**

**Related:** [Theory](./theory.md) · [Interview Revision](../strings.py) · [Interview Q&A](../interview.md) · [Cheatsheet](../cheetsheet.md)
