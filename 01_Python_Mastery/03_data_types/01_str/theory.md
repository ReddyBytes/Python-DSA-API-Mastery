# 🔤 str — Python Strings: The Deep Dive

A string is an **immutable** sequence of characters — think of it as a printed label on a jar: you can read it and copy it, but you cannot erase and rewrite a single letter in place.

---

## 📌 Learning Priority

**Must Learn** — Core, used daily:
string creation · indexing · slicing · f-strings · `.strip()` `.split()` `.join()` `.replace()` `.lower()` `.upper()`

**Should Learn** — Important for real projects:
`.find()` `.count()` `.startswith()` `.endswith()` `.isdigit()` `.isalpha()` · immutability · string interning · Unicode basics

**Good to Know** — Situational:
string multiplication · raw strings `r""` · multiline strings · `.zfill()` · format specifiers

**Reference** — Know it exists:
`.encode()` `.decode()` · `str.format()` (use f-strings instead) · `%` formatting (legacy — avoid)

---

## 🧬 What Is a String, Really?

Before you can use strings well, you need to understand what they actually are under the hood. Most beginners think a string is "just text." The reality is more interesting — and more useful.

### Unicode: Every Character Is a Number

Python 3 strings are **Unicode** sequences. Under the hood, every character is stored as an integer called a **code point**. When you type `'A'`, Python stores the number `65`. When you type `'€'`, Python stores `8364`. When you type `'😀'`, Python stores `128512`.

```
Character → Code Point (integer)

'A'  →   65
'Z'  →   90
'a'  →   97
'0'  →   48
'€'  → 8364
'😀' → 128512
```

Two built-in functions let you cross the bridge between characters and numbers:

```python
ord('A')        # 65       ← character → code point
ord('€')        # 8364
ord('😀')       # 128512

chr(65)         # 'A'      ← code point → character
chr(8364)       # '€'
chr(128512)     # '😀'
```

### Why This Matters in Production

- **Internationalization bugs**: A function that assumes `ord(c) < 128` will silently break on non-ASCII input from users in France, Japan, or anywhere outside the English-speaking world.
- **Database storage**: MySQL's `utf8` charset only stores 3-byte codepoints. Emoji (4-byte) silently gets truncated. You need `utf8mb4`. Knowing that characters are numbers helps you debug this class of bug.
- **Sorting**: Python sorts strings by code point order, so `'Z' < 'a'` is `True` (90 < 97). This surprises developers who expect alphabetical order across cases.

```python
sorted(['banana', 'Apple', 'cherry'])
# ['Apple', 'banana', 'cherry']   ← 'A'=65 sorts before 'b'=98
```

> 📝 **Practice:** [Q1 · creating strings](./practice.md#q1--str--creating-strings)

---

## ✍️ Creating Strings — Four Ways

### Single Quotes vs Double Quotes

Python treats them identically. Convention is consistency — pick one and stick to it. The only time you need to switch is to avoid escaping:

```python
single = 'hello'
double = "hello"          # identical to single

# Switching quotes avoids the backslash:
msg1 = "It's a beautiful day"     # ← no backslash needed
msg2 = 'She said "hello" to me'   # ← no backslash needed

# Alternatively, escape with backslash:
msg3 = 'It\'s a beautiful day'    # works but harder to read
```

### Triple Quotes — For Multiline and Docstrings

**Triple-quoted strings** (`"""` or `'''`) span multiple lines and preserve newlines literally. They are the standard for **docstrings** (function/class documentation):

```python
description = """This string
spans multiple
lines."""

def calculate_area(radius):
    """
    Calculate the area of a circle.

    Args:
        radius: The radius of the circle.

    Returns:
        float: The area.
    """
    return 3.14159 * radius ** 2
```

### f-strings — The Right Way to Embed Values

Introduced in Python 3.6, **f-strings** (formatted string literals) are the modern, readable, and fastest way to build strings with dynamic values. Prefix the string with `f` and put any Python expression inside `{}`:

```python
name  = "Alice"
score = 98.5
items = 1234567

# Basic embedding:
print(f"Hello, {name}!")                    # Hello, Alice!

# Expressions inside {}:
print(f"Next year she'll be {25 + 1}")      # Next year she'll be 26
print(f"Squared: {4 ** 2}")                 # Squared: 16

# Format specifiers — the `:` inside {} controls display format:
print(f"Score: {score:.2f}")                # Score: 98.50    ← 2 decimal places
print(f"Score: {score:.0f}")                # Score: 99       ← 0 decimal places (rounds)
print(f"Total: {items:,}")                  # Total: 1,234,567 ← comma separator
print(f"Total: {items:_}")                  # Total: 1_234_567 ← underscore separator

# Alignment and padding — great for log output:
print(f"{'ERROR':<10} something broke")     # 'ERROR     ' ← left-align in 10 chars
print(f"{'ERROR':>10} something broke")     # '     ERROR' ← right-align in 10 chars
print(f"{'ERROR':^10} something broke")     # '  ERROR   ' ← center in 10 chars
print(f"{'ERROR':*^10} something broke")    # '**ERROR***' ← fill char before alignment

# Debug shortcut (Python 3.8+): variable=value format
x = 42
print(f"{x=}")    # x=42   ← prints both name and value — great for debugging
```

### Raw Strings — When Backslash Should Not Escape

Normally, `\n` means newline and `\t` means tab. A **raw string** (`r"..."`) turns off all backslash interpretation. Every backslash is literal:

```python
# Normal string — backslash escapes:
path1 = "C:\new_folder\test.txt"   # \n = newline, \t = tab — WRONG on Windows!
path1 = "C:\\new_folder\\test.txt" # correct but ugly

# Raw string — backslash is literal:
path2 = r"C:\new_folder\test.txt"  # ← exactly what you typed, no surprises

# Essential for regex patterns:
import re
pattern = re.compile(r"\d{3}-\d{4}")   # \d means "digit" in regex, not escape
```

Use raw strings for: Windows file paths, regular expressions, and any string where backslashes are data, not escape sequences.

> 📝 **Practice:** [Q2 · f-strings](./practice.md#q2--str--f-strings) · [Q3 · raw-strings](./practice.md#q3--str--raw-strings)

---

## 🚂 Strings Are Sequences — The Mental Model

A string is a sequence of characters. Python treats it exactly like a read-only list of one-character strings. Every concept that applies to lists — indexing, slicing, iteration, `len()`, `in` membership — applies to strings too.

The best mental model is a **train of carriages**. Each carriage holds exactly one character. Each carriage has a number starting at 0 from the left, and a negative number counting back from the right.

```
String:  "Python"

Carriage:   P      y      t      h      o      n
           ----   ----   ----   ----   ----   ----
Pos index:   0      1      2      3      4      5
Neg index:  -6     -5     -4     -3     -2     -1

len("Python") = 6
Valid indices: 0 through 5 (positive)  OR  -1 through -6 (negative)
```

### Indexing — Getting One Character

```python
s = "Python"

print(s[0])     # 'P'   ← first character
print(s[1])     # 'y'
print(s[5])     # 'n'   ← last character (index = len - 1)

# Negative indices count from the RIGHT:
print(s[-1])    # 'n'   ← last character (easier than s[len(s)-1])
print(s[-2])    # 'o'   ← second from last
print(s[-6])    # 'P'   ← same as s[0]

# Out of range → IndexError:
# print(s[10])  ← IndexError: string index out of range
# print(s[-7])  ← IndexError: string index out of range
```

> 📝 **Practice:** [Q4 · indexing](./practice.md#q4--str--indexing)

---

## ✂️ Slicing — The Deep Dive

Slicing is one of Python's most powerful features. It extracts a substring by specifying a start and stop position. The syntax is `s[start:stop:step]`.

### The Fence-Post Mental Model

This is the definitive way to understand why `s[0:3]` gives you characters at index 0, 1, 2 — not 0, 1, 2, 3. Think of indices as markers placed *between* characters (like fence posts), not *on* characters:

```
 P    y    t    h    o    n
|    |    |    |    |    |    |
0    1    2    3    4    5    6
^                   ^
|                   |
start=0           stop=3

s[0:3] = everything between post 0 and post 3
       = 'P', 'y', 't'
       = "Pyt"
```

The stop index is **excluded**. This makes two things elegant:
- `len(s) = 6` is a valid stop (gives the whole string)
- `s[0:3]` + `s[3:6]` = `s[0:6]` — slices partition cleanly, no overlap or gap

### All Seven Common Slicing Patterns

```python
s = "Python"
#    0123456  (len = 6)

s[0:3]    # 'Pyt'    ← from index 0, up to (not including) 3
s[2:5]    # 'tho'    ← from index 2, up to (not including) 5
s[2:]     # 'thon'   ← from index 2 to the END (omitting stop = go to end)
s[:4]     # 'Pyth'   ← from the START to index 3 (omitting start = begin at 0)
s[:]      # 'Python' ← full copy (both omitted = entire string)
s[::-1]   # 'nohtyP' ← reversed (step of -1 walks backwards)
s[::2]    # 'Pto'    ← every 2nd character (step=2 skips one)
```

### Slicing With Negative Indices

```python
s = "Python"

s[-3:]     # 'hon'   ← last 3 characters (from -3 to end)
s[:-2]     # 'Pyth'  ← everything except the last 2
s[-4:-1]   # 'tho'   ← from -4 up to (not including) -1
```

### Two Critical Slicing Rules

**Rule 1: Slicing never raises IndexError.** Out-of-bounds stops are silently clipped to the valid range:

```python
s = "Python"   # len = 6
s[0:100]    # 'Python'  ← stop=100 clipped to 6, no error
s[50:60]    # ''        ← entirely out of range, returns empty string
```

**Rule 2: Slicing always returns a new string.** The original is untouched:

```python
s = "Python"
sub = s[2:5]       # 'tho'
print(s)           # 'Python' ← unchanged
print(sub)         # 'tho'    ← brand new string object
print(id(s) == id(sub))  # False ← different objects in memory
```

> 📝 **Practice:** [Q5 · slicing](./practice.md#q5--str--slicing) · [Q6 · slicing-with-step](./practice.md#q6--str--slicing-with-step)

---

## 🔧 String Methods — The Toolbox

Python ships with dozens of string methods. These are grouped below by purpose. Think of them as a toolbox: cleaning tools, measurement tools, search tools, transformation tools.

### CLEANING — Strip Whitespace

When data comes in from users, files, or APIs, it almost always has stray whitespace. Cleaning methods save you hours of debugging mysterious mismatches.

```python
s = "  Hello, World!  "

s.strip()           # "Hello, World!"      ← removes both sides
s.lstrip()          # "Hello, World!  "    ← left side only
s.rstrip()          # "  Hello, World!"    ← right side only

# strip() also removes specific characters (not just spaces):
"***hello***".strip("*")    # "hello"
"---title---".strip("-")    # "title"
```

Visualizing the difference:

```
Input:  "  Hello  "
         ^^     ^^  ← these spaces are removed

strip()  →  "Hello"       both ends
lstrip() →  "Hello  "     left only
rstrip() →  "  Hello"     right only
```

### CASE — Transforming Capitalization

```python
"hello".upper()          # "HELLO"
"HELLO".lower()          # "hello"
"hello world".title()    # "Hello World"   ← first letter of EACH word
"hello world".capitalize() # "Hello world" ← first letter of string only
"Hello World".swapcase() # "hELLO wORLD"  ← flips upper/lower
```

### SEARCHING — Finding Substrings

```python
s = "hello world"

s.find("world")       # 6    ← index where "world" starts
s.find("xyz")         # -1   ← not found (never raises error)
s.index("world")      # 6    ← same as find BUT raises ValueError if missing
s.count("l")          # 3    ← number of non-overlapping occurrences
s.startswith("hel")   # True
s.endswith("rld")     # True

# The `in` operator — simplest membership check:
"world" in s          # True
"xyz" in s            # False
```

The difference between `.find()` and `.index()` matters in production: use `.find()` when "not found" is a normal outcome (it returns -1), use `.index()` when "not found" is a bug (it raises an exception so nothing silently passes through).

### REPLACING AND SPLITTING

```python
# replace — replaces ALL occurrences by default:
"aabbaa".replace("a", "X")          # "XXbbXX"  ← all 4 'a's replaced
"aabbaa".replace("a", "X", 2)       # "XXbbaa"  ← limit to first 2 replacements

# split — string to list:
"a,b,c,d".split(",")                # ['a', 'b', 'c', 'd']
"hello world".split()               # ['hello', 'world']  ← no arg = any whitespace
"a  b\tc\n d".split()               # ['a', 'b', 'c', 'd'] ← tabs, newlines, multi-space

# split with maxsplit:
"a:b:c:d".split(":", 2)             # ['a', 'b', 'c:d']  ← stops after 2 splits

# join — the OPPOSITE of split, and its syntax is counterintuitive:
words = ["hello", "world", "python"]
" ".join(words)     # "hello world python"
",".join(words)     # "hello,world,python"
"-".join(words)     # "hello-world-python"
"".join(words)      # "helloworldpython"   ← concatenate with no separator
```

The **`join` gotcha**: `join` is a method on the *separator string*, not on the list. New Python developers expect `words.join(",")` but the actual syntax is `",".join(words)`. The reason: `join` is defined on `str`, and the separator is a string, so it lives on the string class. Once you accept this, the pattern is natural — the separator goes first.

### CHECKING CONTENT

```python
"abc".isalpha()     # True   ← all characters are letters
"123".isdigit()     # True   ← all characters are digits
"abc123".isalnum()  # True   ← all characters are letters OR digits
"   ".isspace()     # True   ← all characters are whitespace
"abc".islower()     # True   ← all cased characters are lowercase
"ABC".isupper()     # True   ← all cased characters are uppercase

# Note: "123".isalpha() = False, "abc".isdigit() = False
```

### ZERO-PADDING WITH `.zfill()`

**`.zfill(width)`** pads a numeric string with leading zeros to reach the target width. Common for IDs, ticket numbers, timestamps:

```python
"42".zfill(5)       # "00042"
"7".zfill(3)        # "007"
"123".zfill(5)      # "00123"
"12345".zfill(3)    # "12345"  ← already wider than 3, no truncation
```

### METHOD CHAINING

Because every method returns a new string, you can chain calls. The result of one method becomes the input to the next:

```python
email = "  Alice.Smith@Example.COM  "

# Chain: strip whitespace → lowercase → done
clean = email.strip().lower()
# "alice.smith@example.com"

# Longer chain for URL slug generation:
title = "  My Blog Post Title  "
slug = title.strip().lower().replace(" ", "-")
# "my-blog-post-title"
```

> 📝 **Practice:** [Q7 · string-methods](./practice.md#q7--str--string-methods) · [Q8 · split-and-join](./practice.md#q8--str--split-and-join) · [Q9 · find-and-replace](./practice.md#q9--str--find-and-replace) · [Q10 · string-checking](./practice.md#q10--str--string-checking)

---

## 🔒 Immutability — The Deep Explanation

Immutability is the single most important concept to internalize about Python strings. It is not just an academic fact — it drives performance, correctness, and design decisions.

### What Immutability Means

Once a string object is created, its contents can never be changed. Period. Every method that appears to "modify" a string is actually creating and returning a brand new string object.

```
original = "hello"          id: 0x7f...a1   ← object lives here in memory
result   = original.upper() id: 0x7f...b2   ← DIFFERENT address — new object!

original is still "hello" at 0x7f...a1
result   is "HELLO" at 0x7f...b2
```

```python
original = "hello"
result   = original.upper()

print(original)              # "hello"  ← UNCHANGED
print(result)                # "HELLO"  ← brand new string
print(id(original) == id(result))  # False ← different objects
```

This means a common beginner mistake is to call a method and throw away the result:

```python
# WRONG — calling upper() and discarding the return value:
name = "alice"
name.upper()         # ← result is discarded immediately!
print(name)          # "alice"  ← unchanged

# CORRECT — assign the result back:
name = "alice"
name = name.upper()
print(name)          # "ALICE"
```

### String Interning — Python's Memory Optimization

Python **interns** (reuses) certain string objects to save memory. Short strings, identifiers, and string literals that look like identifiers are often the same object in memory:

```python
a = "hello"
b = "hello"
print(a is b)    # True  ← Python reused the same object (interned)

c = "hello world"
d = "hello world"
print(c is d)    # True in CPython for short literals (implementation-specific)

e = "hello" + " " + "world"
f = "hello world"
print(e is f)    # False ← runtime-created strings may NOT be interned
```

The critical lesson: **never use `is` to compare string values**. `is` checks object identity (same address in memory). Use `==` to compare content:

```python
# ALWAYS use == to compare string content:
password_input == stored_password   # correct
password_input is stored_password   # WRONG — might fail for non-interned strings
```

### The `+=` Loop Trap — O(n²) Performance

Because strings are immutable, `s += "x"` creates a brand new string each time. In a loop, this means every iteration copies the entire accumulated string:

```
Iteration 1:  "x"           ← 1 char copy
Iteration 2:  "xx"          ← 2 char copy
Iteration 3:  "xxx"         ← 3 char copy
...
Iteration n:  n chars copy  ← total: 1+2+3+...+n = O(n²) ← QUADRATIC!
```

```python
# WRONG — O(n²) — creates a new string on every iteration:
result = ""
for i in range(10000):
    result += str(i)    # ← copies the whole accumulated string each time!

# CORRECT — O(n) — collect parts in a list, join once at the end:
parts = []
for i in range(10000):
    parts.append(str(i))
result = "".join(parts)   # ← single pass to build final string
```

For small loops (< ~100 iterations) the difference is negligible. For large loops — parsing files, building reports, processing logs — the difference is dramatic.

### Strings Are Hashable

Because strings are immutable, Python can safely compute a stable hash value for them. This is why strings can be used as **dictionary keys** and stored in **sets**. Mutable objects (like lists) cannot be dict keys because their hash would change if the object changed:

```python
d = {}
d["username"] = "alice"    # string as dict key — works fine
d[["a", "b"]] = "value"   # list as dict key — TypeError: unhashable type: 'list'
```

> 📝 **Practice:** [Q11 · immutability](./practice.md#q11--str--immutability) · [Q12 · count-and-find](./practice.md#q12--str--count-and-find)

---

## ⚠️ Common Mistakes

### 1. Concatenating a String and a Number

Python does not auto-convert types in `+`. You must explicitly call `str()`:

```python
age = 25

# WRONG:
msg = "Age: " + age        # TypeError: can only concatenate str (not "int") to str

# CORRECT:
msg = "Age: " + str(age)   # "Age: 25"
msg = f"Age: {age}"        # even better — f-strings handle this automatically
```

### 2. Using `is` Instead of `==` for String Comparison

```python
a = input("Enter your name: ")   # "alice"
b = "alice"

a == b   # True  ← correct content comparison
a is b   # False ← different objects! input() creates a new string not interned
```

### 3. Forgetting That `replace()` Replaces ALL Occurrences

```python
s = "banana"
s.replace("a", "X")         # "bXnXnX"  ← all 3 'a's replaced

# Limit replacements with the count argument:
s.replace("a", "X", 1)      # "bXnana"  ← only the first 'a'
s.replace("a", "X", 2)      # "bXnXna"  ← only the first two
```

### 4. Case-Sensitive Comparisons on User Input

User input is unpredictable. Always normalize case before comparing:

```python
role = input("Enter role: ")   # could be "Admin", "ADMIN", "admin"

# WRONG — will only match if user types exactly "admin":
if role == "admin":
    pass

# CORRECT — normalize first:
if role.lower() == "admin":
    pass
```

### 5. The `+=` Loop Performance Trap

Already covered in depth above. The pattern to remember:

```python
# O(n²) — DO NOT do this in loops:
result = ""
for item in large_list:
    result += item

# O(n) — DO this instead:
result = "".join(large_list)
```

---

## 🔥 Production Patterns

These are real patterns used in production Python code every day.

### Pattern 1 — Email Normalization

User-submitted emails come in all shapes. Normalize before storing or comparing:

```python
def normalize_email(raw: str) -> str:
    return raw.strip().lower()

normalize_email("  Alice.Smith@Example.COM  ")
# "alice.smith@example.com"
```

### Pattern 2 — URL Slug Generation

Content management systems convert titles to URL-safe slugs:

```python
def to_slug(title: str) -> str:
    return title.strip().lower().replace(" ", "-")

to_slug("  My Blog Post Title  ")
# "my-blog-post-title"

# Production version also strips punctuation:
import re
def to_slug_pro(title: str) -> str:
    slug = title.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)   # ← remove non-word chars
    slug = re.sub(r"\s+", "-", slug)       # ← spaces to hyphens
    return slug
```

### Pattern 3 — CSV Line Parsing

Quick parsing of a simple CSV line from a file:

```python
line = "  alice,25,engineer  \n"
parts = line.strip().split(",")
# ['alice', '25', 'engineer']

name, age, role = parts              # unpack directly
age = int(age)                       # convert numeric field
```

### Pattern 4 — Aligned Log Messages with f-strings

Padding format specifiers make log output column-aligned and readable:

```python
def log(level: str, message: str) -> str:
    return f"[{level:<8}] {message}"   # ← left-align level in 8-char field

print(log("INFO",    "Server started"))
print(log("WARNING", "High memory usage"))
print(log("ERROR",   "Connection failed"))

# Output (columns aligned):
# [INFO    ] Server started
# [WARNING ] High memory usage
# [ERROR   ] Connection failed
```

> 📝 **Practice:** [Q13 · real-world-csv](./practice.md#q13--str--real-world-csv-parsing) · [Q14 · real-world-email](./practice.md#q14--str--real-world-email-validation) · [Q15 · real-world-words](./practice.md#q15--str--real-world-word-manipulation)

---

## 🎯 Interview Angles

These are the five string questions that appear most often in coding interviews. Know them cold.

### 1. Reverse a String

The Pythonic one-liner:

```python
s = "Python"
reversed_s = s[::-1]    # "nohtyP"

# Alternatively, for explicit understanding:
reversed_s = "".join(reversed(s))
```

### 2. Check Palindrome

A palindrome reads the same forwards and backwards. Normalize case first for robustness:

```python
def is_palindrome(s: str) -> bool:
    s = s.lower()
    return s == s[::-1]

is_palindrome("racecar")     # True
is_palindrome("Racecar")     # True  ← normalization handles mixed case
is_palindrome("python")      # False
```

### 3. Count Character Frequency

Two approaches: manual dict, or `Counter` from `collections`:

```python
from collections import Counter

s = "hello world"

# Using Counter (preferred in interviews for its clarity):
freq = Counter(s)
# Counter({'l': 3, 'o': 2, 'h': 1, 'e': 1, ' ': 1, 'w': 1, 'r': 1, 'd': 1})

# Manual dict approach (shows understanding of fundamentals):
freq = {}
for char in s:
    freq[char] = freq.get(char, 0) + 1
```

### 4. Anagram Check

Two strings are **anagrams** if they contain the same characters in any order. Sorting reduces both to a canonical form:

```python
def is_anagram(s1: str, s2: str) -> bool:
    return sorted(s1.lower()) == sorted(s2.lower())

is_anagram("listen", "silent")   # True
is_anagram("hello", "world")     # False

# O(n) alternative using Counter:
from collections import Counter
def is_anagram_fast(s1: str, s2: str) -> bool:
    return Counter(s1.lower()) == Counter(s2.lower())
```

### 5. Find All Substrings of Length k

A common sliding window warm-up that tests slicing and loop thinking:

```python
def all_substrings(s: str, k: int) -> list:
    return [s[i:i+k] for i in range(len(s) - k + 1)]

all_substrings("abcde", 3)
# ['abc', 'bcd', 'cde']
```

### Interview Tip: String Complexity

| Operation | Time Complexity | Why |
|---|---|---|
| `s[i]` — indexing | O(1) | Direct memory offset |
| `len(s)` | O(1) | Length is cached |
| `s[i:j]` — slicing | O(k) where k = j-i | Must copy k characters |
| `s + t` — concatenation | O(n+m) | Must copy both strings |
| `"".join(list)` — join | O(n) | Single allocation |
| `s += t` in a loop | O(n²) total | New string each iteration |
| `s.find(t)` | O(n*m) naive | Compare at each position |

---

## 📐 Quick Reference — String Escape Sequences

```python
"\n"    # newline
"\t"    # tab
"\\"    # literal backslash
"\'"    # literal single quote
"\""    # literal double quote
"\r"    # carriage return
"\0"    # null character
"\uXXXX"  # Unicode character by 4-digit hex code point
"\UXXXXXXXX"  # Unicode character by 8-digit hex code point
```

---

## 📋 String Length and `len()`

```python
s = "Python"
print(len(s))            # 6

sentence = "The quick brown fox"
print(len(sentence))     # 19   ← spaces count!

# count() is case-sensitive:
print(sentence.count("the"))          # 0   ← 'The' ≠ 'the'
print(sentence.lower().count("the"))  # 1   ← normalize first
```

`len()` is O(1) for strings because Python caches the length when the object is created. You can call it in a tight loop without performance concern.

---

**[Back to Data Types](../theory.md)**

**Related:** [Practice Problems](./practice.md) · [Interview Q&A](../interview.md) · [Cheatsheet](../cheetsheet.md)
