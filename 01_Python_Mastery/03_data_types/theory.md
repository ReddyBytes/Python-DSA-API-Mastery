<a id="top"></a>
# 📦 Data Types in Python

> *"Before you can write programs, you need to understand what kind of information you're working with. Every piece of data in Python has a type — and that type determines everything about how you can use it."*

Think about your phone's contact app. It stores a name (text), an age (whole number), a balance (decimal), notification status (yes/no), phone numbers (a list), and social links (labeled pairs). Python has a distinct type for each of these — because what you can do with a name is completely different from what you can do with a number.

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [Why Do Data Types Exist?](#why-do-data-types-exist)
- [The Big Picture — All Data Types at a Glance](#the-big-picture--all-data-types-at-a-glance)
- [1. int — Whole Numbers](#1-int--whole-numbers)
  - [What Makes Python's int Special?](#what-makes-pythons-int-special)
  - [int in Different Number Systems](#int-in-different-number-systems)
  - [int Arithmetic](#int-arithmetic)
  - [Useful int Operations](#useful-int-operations)
- [2. float — Decimal Numbers](#2-float--decimal-numbers)
  - [The Float Precision Problem](#the-float-precision-problem)
  - [Important float Facts](#important-float-facts)
  - [Float Rounding](#float-rounding)
- [3. bool — True or False](#3-bool--true-or-false)
  - [bool is an Integer!](#bool-is-an-integer)
  - [Truthiness](#truthiness)
- [4. str — Text](#4-str--text)
- [5. list — Ordered Collection](#5-list--ordered-collection)
- [6. tuple — The Sealed List](#6-tuple--the-sealed-list)
- [7. set — Only Unique Items](#7-set--only-unique-items)
- [8. dict — Key-Value Pairs](#8-dict--key-value-pairs)
- [9. None — The Intentional Blank](#9-none--the-intentional-blank)
  - [None vs Empty Values](#none-vs-empty-values)
- [10. Type Conversion](#10-type-conversion)
  - [Common Conversions](#common-conversions)
  - [Input Conversion — The input() Trap](#input-conversion)
- [How to Choose the Right Type](#how-to-choose-the-right-type)
- [Chapter Summary](#chapter-summary)
- [bytes and bytearray — Binary Data](#bytes-and-bytearray--binary-data)
- [collections Module — Smarter Data Structures](#collections-module--smarter-data-structures)
  - [defaultdict](#defaultdict)
  - [Counter](#counter)
  - [deque](#deque)
  - [frozenset](#frozenset)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`list` · `dict` · `str` · `int` / `float` / `bool` · Type conversion · `None` · Truthiness · `collections.defaultdict` · `collections.Counter` · `collections.deque`

**Should Learn** — Important for real projects, comes up regularly:
`tuple` · `set` · `bytes` / `bytearray` · `frozenset` · Float precision trap · String methods (`.split`, `.join`, `.strip`, `.format`)

**Good to Know** — Useful in specific situations:
`collections.OrderedDict` · `str.encode()` / `bytes.decode()` · `slice()` objects · String validation methods (`.isdigit()`, `.isalpha()`)

**Reference** — Know it exists, look up when needed:
`complex` type · `memoryview` · Old `%` string formatting

<a id="why-do-data-types-exist"></a>
# 🌍 Why Do Data Types Exist?

Imagine Python has to store a person's name, their age, their account balance, whether they're active, their phone numbers, and their social links. It can't treat all of them the same way:

- You can do math on an age — but math on a name makes no sense
- You can search through a list of phone numbers — but a single number has nothing to search
- A balance needs decimal precision — an age doesn't

**Data types tell Python: "what is this, and what can you do with it?"**

Every type has:
- A **set of allowed values** (int: whole numbers; bool: only True or False)
- A **set of operations** (you can sort a list, not a number; you can do arithmetic on a number, not a list)
- A **memory representation** (int stores differently from str)

> [↑ Back to Top](#top)

<a id="the-big-picture--all-data-types-at-a-glance"></a>
# 🗺️ The Big Picture — All Data Types at a Glance

```
PYTHON DATA TYPES
│
├── NUMBERS ──────── int        → 25, -7, 1000
│                    float      → 3.14, -0.5
│                    complex    → 3+4j
│                    bool       → True, False
│
├── TEXT ─────────── str        → "hello", 'world'
│
├── COLLECTIONS ──── list       → [1, 2, 3]        ordered, changeable
│                    tuple      → (1, 2, 3)        ordered, fixed
│                    set        → {1, 2, 3}        unordered, unique only
│                    dict       → {"name": "Ali"}  key → value pairs
│
└── NOTHING ──────── None       → None             absence of value
```

```
┌───────────────────────────────────────────────────────────────────┐
│  TYPE       EXAMPLE           CHANGEABLE?   KEEPS ORDER?  UNIQUE? │
├───────────────────────────────────────────────────────────────────┤
│  int        42                ✗             –             –       │
│  float      3.14              ✗             –             –       │
│  bool       True              ✗             –             –       │
│  str        "hello"           ✗             ✓             ✗       │
│  list       [1, 2, 3]         ✓             ✓             ✗       │
│  tuple      (1, 2, 3)         ✗             ✓             ✗       │
│  set        {1, 2, 3}         ✓             ✗             ✓       │
│  dict       {"a": 1}          ✓             ✓ (Py 3.7+)   keys ✓  │
│  None       None              ✗             –             –       │
└───────────────────────────────────────────────────────────────────┘
```

**How to check the type of anything:**

```python
print(type(42))         # <class 'int'>
print(type(3.14))       # <class 'float'>
print(type("hello"))    # <class 'str'>
print(type(True))       # <class 'bool'>
print(type([1,2,3]))    # <class 'list'>
print(type(None))       # <class 'NoneType'>
```

> [↑ Back to Top](#top)

<a id="1-int--whole-numbers"></a>
# 1. int — Whole Numbers

`int` stands for **integer** — a whole number with no decimal point. It can be positive, negative, or zero.

```python
age       = 25
floors    = -3        # basement floors
score     = 0
students  = 1000
big_num   = 9_999_999 # underscores make big numbers readable — Python ignores them
```

> 📝 **Practice:** [Q1 — Leap Year Check](./practice.md#q1--int--leap-year-check) · [Q2 — Even or Odd](./practice.md#q2--int--even-or-odd) · [Q3 — Floor Division](./practice.md#q3--int--floor-division-and-remainder) · [Q4 — Power & abs()](./practice.md#q4--int--power-and-absolute-value)

<a id="what-makes-pythons-int-special"></a>
## What Makes Python's int Special?

In most languages (like C or Java), an integer has a size limit — usually about 2 billion. Go over that, and the program crashes or wraps around to the wrong number.

**Python integers have no limit.** They can be as big as your RAM allows.

```python
# This works perfectly in Python:
really_big = 999_999_999_999_999_999_999_999_999_999
print(really_big + 1)
# 1000000000000000000000000000000  ← no crash, no wrong answer!
```

```
C / Java int:           Python int:
  ┌──────────────┐        ┌─────────────────────────────────────┐
  │  max ~2 bil  │        │  any size — limited only by RAM     │
  │  overflow!   │        │  9_999_999_999_999_999_999_999 ✓   │
  └──────────────┘        └─────────────────────────────────────┘
```

<a id="int-in-different-number-systems"></a>
## int in Different Number Systems

Humans count in base 10 (decimal). Computers use base 2 (binary). Python lets you write numbers in different bases:

```python
decimal = 255           # base 10  — normal numbers
binary  = 0b11111111   # base 2   — starts with 0b
octal   = 0o377        # base 8   — starts with 0o
hexa    = 0xFF         # base 16  — starts with 0x

# All four are the same number — 255:
print(decimal == binary == octal == hexa)   # True

# Convert TO different bases:
print(bin(255))    # '0b11111111'   → binary string
print(oct(255))    # '0o377'        → octal string
print(hex(255))    # '0xff'         → hex string
```

```
255 in different bases:
  decimal (base 10)  →  255
  binary  (base 2)   →  11111111   (8 bits, all 1s = max for 1 byte)
  octal   (base 8)   →  377
  hex     (base 16)  →  FF
```

<a id="int-arithmetic"></a>
## int Arithmetic

```python
a = 17
b = 5

print(a + b)    # 22      → addition
print(a - b)    # 12      → subtraction
print(a * b)    # 85      → multiplication
print(a ** b)   # 1419857 → power (17 to the 5th)

# Division is where it gets interesting:
print(a / b)    # 3.4  → TRUE division  → always returns float
print(a // b)   # 3    → FLOOR division → whole number, decimal cut off
print(a % b)    # 2    → MODULO         → remainder after dividing
```

**Floor division and modulo — a real example:**

```
You have 17 apples. Pack them into boxes of 5.

17 // 5 = 3   → you fill 3 complete boxes
17 %  5 = 2   → 2 apples left over

Check: 3 × 5 = 15 used + 2 leftover = 17 ✓
```

**Modulo is incredibly useful:**

```python
# Is a number even or odd?
10 % 2   # 0 → even (no remainder)
11 % 2   # 1 → odd

# Does a number divide evenly?
100 % 4  # 0 → 100 is divisible by 4

# What's the last digit of a number?
12345 % 10  # 5 → last digit is always: n % 10

# Wrap around (circular indexing):
index = (current + 1) % len(items)  # never goes out of bounds
```

<a id="useful-int-operations"></a>
## Useful int Operations

```python
abs(-42)         # 42     → absolute value (makes negative → positive)
pow(2, 10)       # 1024   → same as 2**10
divmod(17, 5)    # (3, 2) → both floor division AND remainder at once
```

> [↑ Back to Top](#top)

<a id="2-float--decimal-numbers"></a>
# 2. float — Decimal Numbers

`float` is for numbers that have a decimal point — measurements, prices, percentages, coordinates, anything that isn't a whole number.

```python
pi          = 3.14159265358979
temperature = 36.6
price       = 999.99
percentage  = 0.18          # 18%
tiny        = 0.000001
big         = 1.5e10        # scientific notation: 1.5 × 10¹⁰ = 15,000,000,000
very_small  = 2.5e-4        # 2.5 × 10⁻⁴ = 0.00025
```

<a id="the-float-precision-problem"></a>
## The Float Precision Problem

This is one of the first things that shocks every Python beginner. Try this:

```python
print(0.1 + 0.2)
# Expected: 0.3
# Actual:   0.30000000000000004
```

**Why does this happen?**

Computers store numbers in binary (base 2 — only 0s and 1s). The number `0.1` looks simple in decimal, but in binary it's an infinite repeating pattern:

```
0.1 in decimal:   0.1            (looks simple)

0.1 in binary:    0.000110011001100110011...  (infinite repeating — like 1/3 in decimal)
                          ┌────────────────┐
stored as:        0.00011001100110011010    (truncated — tiny error locked in forever)

When you add:
  stored(0.1) ≈  0.1000000000000000055511...
  stored(0.2) ≈  0.2000000000000000111022...
               ─────────────────────────────
  result      ≈  0.3000000000000000444089...
  Python shows:  0.30000000000000004
```

It's the same reason you can't write `1/3` exactly in decimal — you write `0.333...` and there's always a tiny inaccuracy.

**How to handle it:**

```python
# Never compare floats directly with ==
print(0.1 + 0.2 == 0.3)        # False  ← wrong!

# Use round() when displaying
print(round(0.1 + 0.2, 2))     # 0.3    ← correct display

# Use round() for comparisons
print(round(0.1 + 0.2, 10) == 0.3)   # True

# For financial calculations — use the decimal module
from decimal import Decimal
print(Decimal("0.1") + Decimal("0.2"))   # 0.3 exactly
```

<a id="important-float-facts"></a>
## Important float Facts

```python
# Division always gives a float — even if the result is whole:
print(10 / 2)     # 5.0  ← float, not 5!
print(type(10/2)) # <class 'float'>

# Mixing int and float → result is always float:
print(5 + 2.0)    # 7.0  ← int + float = float

# Check if a float is actually a whole number:
(7.0).is_integer()   # True
(7.5).is_integer()   # False

# Float limits:
print(1.8e308)     # inf   → beyond float's maximum → becomes infinity
print(-1.8e308)    # -inf  → negative infinity

# Special float values:
positive_infinity = float('inf')
negative_infinity = float('-inf')
not_a_number      = float('nan')   # result of invalid operations
```

<a id="float-rounding"></a>
## Float Rounding

```python
round(3.14159, 2)    # 3.14   → 2 decimal places
round(3.14159, 0)    # 3.0    → 0 decimal places (still float)
round(2.5)           # 2      → banker's rounding — rounds to nearest EVEN!
round(3.5)           # 4      → rounds to nearest even (4 is even, 2 is even)

# Negative decimal places:
round(1234, -2)      # 1200   → round to nearest hundred
round(1678, -2)      # 1700
```

**Common mistake — banker's rounding surprises:**
`round(0.5)` returns `0`, not `1`. `round(2.5)` returns `2`, not `3`. Python rounds to the nearest **even** number to reduce statistical bias in accumulated rounding. Use `math.ceil()` or `math.floor()` if you need classic rounding.

> 📝 **Practice:** [Q5 — Restaurant Bill](./practice.md#q5--float--restaurant-bill) · [Q6 — BMI Calculator](./practice.md#q6--float--bmi-calculator) · [Q7 — Precision Trap](./practice.md#q7--float--precision-trap) · [Q8 — Temperature](./practice.md#q8--float--temperature-conversion)

> [↑ Back to Top](#top)

<a id="3-bool--true-or-false"></a>
# 3. bool — True or False

`bool` (short for Boolean) has exactly two values: `True` or `False`. It's used for yes/no decisions — is the user logged in? Is the password correct? Is the list empty?

```python
is_logged_in    = True
is_admin        = False
has_permission  = True
is_raining      = False
```

<a id="bool-is-an-integer"></a>
## bool is an Integer!

This is a fascinating Python fact. `bool` is actually a **subtype of `int`**. Under the hood, `True == 1` and `False == 0`.

```python
True  == 1    # True
False == 0    # True

print(True + True)      # 2   ← you can add booleans!
print(True + False)     # 1
print(True * 10)        # 10
print(False * 10)       # 0
```

**This is actually useful — counting True values:**

```python
exam_results = [True, False, True, True, False, True]
passed = sum(exam_results)   # counts True as 1, False as 0
print(passed)                # 4  ← 4 students passed!

# Count how many items pass a condition:
scores = [85, 42, 90, 67, 55, 78]
above_passing = sum(s >= 60 for s in scores)   # 4
```

```
bool inheritance:
  int
   └── bool
         ├── True  (stores as 1)
         └── False (stores as 0)

isinstance(True, int)   # True  ← bool IS an int
isinstance(True, bool)  # True
```

<a id="truthiness"></a>
## Truthiness

Python doesn't just use `True` and `False` literally. Any value can be used in a boolean context — Python checks its **truthiness**.

```
┌───────────────────────────────────────────────────────────┐
│  FALSY — these all behave like False in conditions        │
│                                                           │
│   0        the number zero (int)                         │
│   0.0      the number zero (float)                       │
│   ""       an empty string                               │
│   []       an empty list                                 │
│   {}       an empty dict                                 │
│   ()       an empty tuple                               │
│   set()    an empty set                                 │
│   None     the absence of value                         │
│   False    False itself                                 │
│                                                           │
│  TRUTHY — everything else, including:                     │
│   1  -1  42    any non-zero number                       │
│   "a"  " "     any non-empty string (even just a space!) │
│   [0]          a list with items (even if items are 0)   │
│   {"a": 1}     a non-empty dict                          │
└───────────────────────────────────────────────────────────┘
```

```python
# Python checks truthiness in if conditions:
username = ""
if username:
    print("Hello,", username)
else:
    print("Please enter a username")   # ← runs, "" is falsy

items = [1, 2, 3]
if items:
    print("Cart has items")    # ← runs, non-empty list is truthy

# Explicitly convert to bool:
bool(0)      # False
bool(42)     # True
bool("")     # False
bool("hi")   # True
bool([])     # False
bool([0])    # True  ← list has one item — even if that item is 0!
```

> 📝 **Practice:** [Q9 — Truthiness](./practice.md#q9--bool--truthiness) · [Q10 — Bool Arithmetic](./practice.md#q10--bool--bool-arithmetic) · [Q11 — and/or Shortcuts](./practice.md#q11--bool--and--or-shortcuts)

> [↑ Back to Top](#top)

<a id="4-str--text"></a>
# 4. str — Text

> Full deep-dive: [01_str/theory.md](./01_str/theory.md)

Strings are immutable sequences of characters. Key operations: indexing · slicing · f-strings · `.strip()` `.split()` `.join()` `.replace()` `.lower()` `.upper()`

| Order | Subfolder | Deep-dive |
|---|---|---|
| 1st — learn first | `01_str/` | [theory](./01_str/theory.md) · [practice](./01_str/practice.md) |

> 📝 **Practice:** [str/practice.md](./01_str/practice.md) · [Q12–Q18 in master practice](./practice.md#q12--str--string-methods)

> [↑ Back to Top](#top)

<a id="5-list--ordered-collection"></a>
# 5. list — Ordered Collection

> Full deep-dive: [02_list/theory.md](./02_list/theory.md)

Lists are ordered, mutable sequences. Key operations: indexing · slicing · `.append()` `.remove()` `.sort()` · list comprehensions · copy trap.

| Order | Subfolder | Deep-dive |
|---|---|---|
| 2nd — learn after str | `02_list/` | [theory](./02_list/theory.md) · [practice](./02_list/practice.md) |

> 📝 **Practice:** [list/practice.md](./02_list/practice.md) · [Q19–Q25 in master practice](./practice.md#q19--list--crud-operations)

**Common mistake — assignment is not a copy:** `b = a` makes both `b` and `a` point to the same list. Changing `b` changes `a`. Use `b = a.copy()` or `b = list(a)` for a real copy.

**Common mistake — sort() returns None:** `result = my_list.sort()` → `result` is `None`. `sort()` modifies the list in place and returns nothing. Use `sorted(my_list)` when you need a new sorted list.

> [↑ Back to Top](#top)

<a id="6-tuple--the-sealed-list"></a>
# 6. tuple — The Sealed List

> Full deep-dive: [03_tuple/theory.md](./03_tuple/theory.md)

Tuples are ordered, immutable sequences. Use when data should never change: coordinates, RGB values, DB rows. Supports unpacking, can be used as dict keys and set members.

| Order | Subfolder | Deep-dive |
|---|---|---|
| 3rd — learn after list | `03_tuple/` | [theory](./03_tuple/theory.md) · [practice](./03_tuple/practice.md) |

> 📝 **Practice:** [tuple/practice.md](./03_tuple/practice.md) · [Q26–Q30 in master practice](./practice.md#q26--tuple--immutability)

**Common mistake — single-item tuple:** `(42)` is just the number 42 in parentheses — not a tuple. You must add a trailing comma: `(42,)` is a tuple.

> [↑ Back to Top](#top)

<a id="7-set--only-unique-items"></a>
# 7. set — Only Unique Items

> Full deep-dive: [04_set/theory.md](./04_set/theory.md)

Sets are unordered collections of unique, hashable items. Use for: deduplication, fast membership checks (O(1)), set math (intersection, union, difference).

| Order | Subfolder | Deep-dive |
|---|---|---|
| 4th — learn after tuple | `04_set/` | [theory](./04_set/theory.md) · [practice](./04_set/practice.md) |

> 📝 **Practice:** [set/practice.md](./04_set/practice.md) · [Q31–Q35 in master practice](./practice.md#q31--set--remove-duplicates)

**Common mistake — empty set:** `{}` creates an empty **dict**, not an empty set. Use `set()` to create an empty set.

> [↑ Back to Top](#top)

<a id="8-dict--key-value-pairs"></a>
# 8. dict — Key-Value Pairs

> Full deep-dive: [05_dict/theory.md](./05_dict/theory.md)

Dicts are ordered (Python 3.7+) key-value stores. The most-used complex type in Python. Key operations: `.get()` · `.items()` · `.update()` · dict comprehensions · `collections.defaultdict`.

| Order | Subfolder | Deep-dive |
|---|---|---|
| 5th — learn last | `05_dict/` | [theory](./05_dict/theory.md) · [practice](./05_dict/practice.md) |

> 📝 **Practice:** [dict/practice.md](./05_dict/practice.md) · [Q36–Q42 in master practice](./practice.md#q36--dict--create-and-access)

> [↑ Back to Top](#top)

<a id="9-none--the-intentional-blank"></a>
# 9. None — The Intentional Blank

`None` represents **the absence of a value** — not zero, not an empty string, not False. It's Python's way of saying "nothing here, intentionally."

```python
result = None          # no result yet
phone  = None          # person has no phone number on file

# Always check for None with 'is', not '==':
if result is None:
    print("No result available")

if phone is not None:
    print("Phone:", phone)
```

**Why `is` instead of `==`?**

`None` is a special **singleton** — there's only ONE `None` object in all of Python. `is` checks if two variables point to that exact same object. It's more precise and is the Pythonic convention.

```python
# When does a variable become None?

# 1. You set it explicitly:
x = None

# 2. A function with no return statement returns None:
result = print("hello")   # print() returns nothing
print(result)              # None

# 3. .get() on a missing dict key:
d = {"a": 1}
print(d.get("b"))   # None  ← no KeyError, just None
```

<a id="none-vs-empty-values"></a>
## None vs Empty Values

Beginners often confuse `None` with other "empty-looking" values. They are all different:

```
┌──────────┬──────────┬─────────────────────────────────────┐
│  Value   │  Type    │  Meaning                            │
├──────────┼──────────┼─────────────────────────────────────┤
│  None    │ NoneType │ No value — intentionally absent     │
│  False   │ bool     │ The boolean value "no / off"        │
│  0       │ int      │ The number zero                     │
│  ""      │ str      │ Empty text (text exists, just empty)│
│  []      │ list     │ Empty list (list exists, no items)  │
│  {}      │ dict     │ Empty dict (dict exists, no pairs)  │
└──────────┴──────────┴─────────────────────────────────────┘
```

```python
# All are falsy — but they are NOT equal to each other:
bool(None) == bool(False) == bool(0) == bool("") == bool([])
# True — all falsy

None == False    # False   ← completely different things
None == 0        # False
None == ""       # False

# Correct way to distinguish:
x = None
x is None        # True   ← correct None check
x == None        # True   ← works but not idiomatic
x is False       # False  ← None is not False
```

> 📝 **Practice:** [Q43 — Identity Check](./practice.md#q43--none--identity-check) · [Q44 — Optional Value](./practice.md#q44--none--optional-value)

> [↑ Back to Top](#top)

<a id="10-type-conversion"></a>
# 10. Type Conversion

Sometimes data comes in one form and you need it in another. User types a number with `input()` → it comes as a string, you need an int. You want to display a number inside a sentence → number to string. A list has duplicates and you want them removed → list to set.

**Two kinds of conversion:**
- **Explicit (casting)** — you call a function: `int("42")`, `str(3.14)`, `list({1,2,3})`
- **Implicit (coercion)** — Python converts automatically: `5 + 2.0` → `7.0` (int promoted to float)

<a id="common-conversions"></a>
## Common Conversions

```python
# → int
int("42")        # 42    string to int
int(3.9)         # 3     float to int — TRUNCATES (cuts, doesn't round!)
int(True)        # 1     bool to int
int(False)       # 0

# These CRASH:
# int("hello")   → ValueError: invalid literal
# int("3.14")    → ValueError — use float("3.14") first, then int()

# → float
float("3.14")    # 3.14  string to float
float(42)        # 42.0  int to float
float(True)      # 1.0

# → str
str(42)          # "42"       int to string
str(3.14)        # "3.14"     float to string
str(True)        # "True"     bool to string
str([1,2,3])     # "[1, 2, 3]" list to string representation

# → bool
bool(0)          # False
bool(1)          # True
bool("")         # False
bool("hello")    # True
bool([])         # False
bool([1,2])      # True

# → list
list("Python")   # ['P','y','t','h','o','n']  string → chars
list((1,2,3))    # [1, 2, 3]                  tuple → list
list({1,2,3})    # [1, 2, 3]  (order varies)  set → list

# → tuple
tuple([1,2,3])   # (1, 2, 3)   list → tuple
tuple("abc")     # ('a','b','c')

# → set (removes duplicates)
set([1,2,2,3])   # {1, 2, 3}
set("hello")     # {'h','e','l','o'}
```

```
Safe conversions (no data loss):      Lossy conversions:
  int  →  float  →  str               float → int    (3.9 → 3, lost .9)
  bool → int → float → str            str → int      (fails if not numeric)
                                       set → list     (order not guaranteed)
```

<a id="input-conversion"></a>
## Input Conversion — The input() Trap

`input()` **always returns a string** — no matter what the user types. This is the #1 beginner bug.

```python
age = input("Enter your age: ")   # user types 25 → age = "25" (string!)

# This CRASHES:
next_year = age + 1   # TypeError: can't add str and int

# Fix — convert immediately:
age = int(input("Enter your age: "))   # now it's an integer
next_year = age + 1   # works!

# Safe pattern — handle invalid input:
try:
    age = int(input("Enter your age: "))
except ValueError:
    print("Please enter a whole number")
```

> 📝 **Practice:** [Q45 — int and float](./practice.md#q45--type-conversion--int-and-float) · [Q46 — input() Trap](./practice.md#q46--type-conversion--the-input-trap) · [Q47 — bool conversion](./practice.md#q47--type-conversion--bool-conversion)

**Common mistake — int() truncates, it does not round:** `int(3.9)` returns `3`, not `4`. Use `round(3.9)` when you need rounding.

> [↑ Back to Top](#top)

<a id="how-to-choose-the-right-type"></a>
# 🔄 How to Choose the Right Type

```
Is the data a single value?
   │
   ├── Whole number?                        → int
   ├── Number with decimals?                → float
   ├── Yes / No ?                           → bool
   ├── Text?                                → str
   └── "Nothing" / not set yet?             → None

Is the data multiple values?
   │
   ├── Order matters AND you'll modify it?  → list
   ├── Order matters, never changes?        → tuple  (can be dict key)
   ├── Need unique items / fast O(1) check? → set
   └── Need to look up by label/name?       → dict
```

```
Quick cheat:
  [1, 2, 3]         → list   (ordered, mutable)
  (1, 2, 3)         → tuple  (ordered, fixed)
  {1, 2, 3}         → set    (unique, unordered)
  {"a": 1, "b": 2}  → dict   (labeled, key→value)
  {}                → dict!  (NOT a set — empty {} is always dict)
  set()             → empty set (you must write it this way)
```

> [↑ Back to Top](#top)

<a id="chapter-summary"></a>
# 🎬 Chapter Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  int     Whole numbers, any size, floor div //, modulo %
  float   Decimals, precision trap, use round() wisely
  bool    True/False, subtype of int, truthiness concept
  str     Text, immutable, indexing/slicing, 20+ methods
  list    Ordered, mutable, any types, append/pop/sort
  tuple   Ordered, immutable, unpacking, use as dict key
  set     Unique items, fast O(1) search, set math
  dict    Key-value pairs, .get() is your friend, nested dicts
  None    Intentional emptiness, use 'is' to check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

> [↑ Back to Top](#top)

<a id="bytes-and-bytearray--binary-data"></a>
# bytes and bytearray — Binary Data

When you work with files, network sockets, or encoding text, you deal with **raw binary data** — not strings.

**`bytes`** — immutable sequence of integers (0–255)
**`bytearray`** — mutable version of bytes

```python
# Creating bytes:
b1 = b"hello"               # literal
b2 = bytes([72, 101, 108])  # from list of ints
b3 = "hello".encode("utf-8")  # from string

# Creating bytearray (mutable):
ba = bytearray(b"hello")
ba[0] = 72    # can modify individual bytes
ba.append(33) # can append

# Key operations:
b = b"hello world"
b[0]              # 104  (int, not char)
b[0:5]            # b'hello'
len(b)            # 11
b.decode("utf-8") # "hello world"  ← back to string
```

```
str  ──encode("utf-8")──►  bytes  ──decode("utf-8")──►  str
"café"                     b'caf\xc3\xa9'               "café"
```

**When you need this:**

```python
# Reading binary files:
with open("image.png", "rb") as f:   # "rb" = read binary
    data = f.read()                   # bytes object

# Network sockets:
sock.send(b"GET / HTTP/1.1\r\n")     # must be bytes, not str

# Checking file headers (magic bytes):
with open("file", "rb") as f:
    header = f.read(4)
    if header == b"\x89PNG":
        print("This is a PNG file")
```

**`bytes` vs `str` — you cannot mix them:**

```python
type(b"hello")   # <class 'bytes'>
type("hello")    # <class 'str'>

b"hello" + " world"    # TypeError — must be bytes + bytes
b"hello" + b" world"   # b'hello world' ✓
```

> [↑ Back to Top](#top)

<a id="collections-module--smarter-data-structures"></a>
# collections Module — Smarter Data Structures

Python's `collections` module gives you specialized containers that solve common problems better than plain dicts and lists.

```
defaultdict  → grouping, counting, graph adjacency lists
Counter      → frequency analysis, most common items, bag operations
deque        → queues, BFS/DFS, sliding windows, recent-N items
frozenset    → set as dict key, immutable set membership
```

<a id="defaultdict"></a>
## defaultdict — Dictionary That Never Raises KeyError

A regular dict raises `KeyError` when you access a missing key. `defaultdict` instead creates a default value automatically.

```python
from collections import defaultdict

# Regular dict — KeyError on missing key:
counts = {}
counts["apple"] += 1    # KeyError: 'apple'

# defaultdict — creates default value automatically:
counts = defaultdict(int)   # default: 0 (int() returns 0)
counts["apple"] += 1        # starts at 0, increments to 1
counts["apple"] += 1
print(counts["apple"])      # 2
print(counts["banana"])     # 0 — created automatically, no KeyError

# Group items by key (common real-world use):
groups = defaultdict(list)
for item in ["a", "b", "a", "c", "b", "a"]:
    groups[item].append(item)
# {'a': ['a', 'a', 'a'], 'b': ['b', 'b'], 'c': ['c']}
```

```
defaultdict(int)  → missing key starts at 0
defaultdict(list) → missing key starts at []
defaultdict(set)  → missing key starts at set()
defaultdict(str)  → missing key starts at ""
```

<a id="counter"></a>
## Counter — Frequency Counting

`Counter` counts how many times each item appears. One line replaces a manual counting loop.

```python
from collections import Counter

# Count in one line:
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
count = Counter(words)
# Counter({'apple': 3, 'banana': 2, 'cherry': 1})

count["apple"]         # 3
count["missing"]       # 0  ← no KeyError (like defaultdict)
count.most_common(2)   # [('apple', 3), ('banana', 2)]

# Counter arithmetic:
c1 = Counter(a=3, b=2)
c2 = Counter(a=1, b=4)
c1 + c2   # Counter({'b': 6, 'a': 4})
c1 - c2   # Counter({'a': 2})  ← only positive counts kept

# Count characters:
Counter("mississippi")
# Counter({'s': 4, 'i': 4, 'p': 2, 'm': 1})
```

<a id="deque"></a>
## deque — Double-Ended Queue

A regular list is slow (`O(n)`) when inserting or removing at the front. `deque` is `O(1)` at **both** ends.

```python
from collections import deque

d = deque([1, 2, 3])
d.append(4)        # add right:  [1, 2, 3, 4]
d.appendleft(0)    # add left:   [0, 1, 2, 3, 4]
d.pop()            # remove right: returns 4
d.popleft()        # remove left:  returns 0
```

**Fixed-size sliding window with `maxlen`:**

```python
recent = deque(maxlen=3)
for x in range(6):
    recent.append(x)
    print(list(recent))
# [0]
# [0, 1]
# [0, 1, 2]
# [1, 2, 3]  ← oldest dropped automatically
# [2, 3, 4]
# [3, 4, 5]
```

Use `deque` when: implementing queues, BFS algorithms, sliding windows, or any pattern needing fast front-insertion.

```
list append/pop:              deque append/pop:
  right end → O(1) ✓           right end → O(1) ✓
  left end  → O(n) ✗           left end  → O(1) ✓
```

<a id="frozenset"></a>
## frozenset — Immutable Set

A `frozenset` is a set that cannot be modified after creation — it's hashable, which means it can be used as a dict key or placed inside another set (regular sets cannot).

```python
fs = frozenset([1, 2, 3])
fs.add(4)   # AttributeError — immutable

# Use as dict key (regular set can't do this):
cache = {}
cache[frozenset([1, 2, 3])] = "result"   # ✓

# Use as element in a set of sets:
seen = set()
seen.add(frozenset([1, 2]))   # frozenset is hashable, set is not
```

> [↑ Back to Top](#top)

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [02_control_flow → theory.md](../02_control_flow/theory.md) |
| ➡ Next Module | [04_functions → theory.md](../04_functions/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[Control Flow →](../02_control_flow/theory.md) · [Functions →](../04_functions/theory.md) · [OOP →](../05_oops/theory.md) · [Memory Management →](../01.1_memory_management/theory.md)

**Jump to specific topics in other files:**
- Mutable default argument trap → [04_functions/theory.md](../04_functions/theory.md)
- List comprehensions → [02_control_flow/theory.md#9-comprehensions](../02_control_flow/theory.md#9-comprehensions)
- Reference counting (why immutables are safer) → [01.1_memory_management/theory.md#2-objects-and-references](../01.1_memory_management/theory.md#2-objects-and-references)
- Generator expressions (lazy alternative to list) → [02_control_flow/theory.md#generator-expressions](../02_control_flow/theory.md#generator-expressions)
