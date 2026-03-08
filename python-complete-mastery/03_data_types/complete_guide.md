# 🎭 Data Types — The Complete Journey

> *You don't learn data types by memorizing them.*
> *You learn them by needing them.*
> *This guide takes you through that need — story first, code second, mastery guaranteed.*

---

## 🗺️ How to Read This Guide

Every chapter follows the same rhythm:

```
🎬 A story creates the need
💡 The concept clicks naturally
💻 Code makes it concrete
🧠 Expert insight levels you up
⚠️  A trap is avoided before you fall in
```

By the end, you won't just know the 9 data types.
You'll *think* in them.

---

## 🌍 The Big Picture — Before We Dive In

Imagine you just started building a small app.
Your first task: collect information about students.

A student has:
- A name → text
- An age → whole number
- A GPA → decimal number
- Whether they've paid fees → yes or no
- A list of subjects → multiple values
- Their marks per subject → labeled pairs
- Favourite subjects → unique values only
- Whether they have an address on file → maybe nothing there

Python has exactly one type for each of these situations.
That's not a coincidence. That's design.

```
int    → whole numbers          25, -7, 1000
float  → decimal numbers        9.4, 3.14, -0.5
bool   → yes or no              True, False
str    → text                   "Alice", "hello"
list   → ordered collection     ["Math", "Science"]
tuple  → sealed collection      (10.5, 25.3)
set    → unique items only      {"Alice", "Bob"}
dict   → labeled pairs          {"name": "Alice", "age": 25}
None   → intentional emptiness  None
```

Now let's meet each one properly.

---

# 📖 Chapter 1 — `int` · The Whole Number

## 🎬 The Story

You're building an election counter.
Votes come in one by one.
You need to count them.
You can't have 3.7 votes. Votes are whole. They're integers.

```python
total_votes = 0
total_votes = total_votes + 1    # one vote came in
total_votes = total_votes + 1    # another
total_votes += 1                 # shorthand for the same thing
print(total_votes)               # 3
```

Simple. Clean. Exactly what you need.

## 💡 The Concept

`int` is a whole number — no decimal, no fraction.
Positive, negative, or zero.

```python
age      = 25
floors   = -3          # basement floors
score    = 0
students = 1_000_000   # underscores are just for readability — Python ignores them
```

## 💻 The Code You'll Actually Use

```python
a = 17
b = 5

print(a + b)    # 22   addition
print(a - b)    # 12   subtraction
print(a * b)    # 85   multiplication
print(a ** b)   # 1419857  power: 17 to the power of 5

# Division — this is where it gets interesting:
print(a / b)    # 3.4  → always gives a float!
print(a // b)   # 3    → floor division: whole number only
print(a % b)    # 2    → modulo: the remainder
```

**The apple box trick:**
```
You have 17 apples and want to pack them in boxes of 5.

17 // 5 = 3  → you fill 3 complete boxes
17 %  5 = 2  → 2 apples left over

Check: 3×5 = 15 + 2 leftover = 17 ✓
```

Modulo (`%`) is surprisingly powerful:
```python
# Is a number even?
10 % 2 == 0    # True  → even
11 % 2 == 0    # False → odd

# Last digit of any number:
12345 % 10     # 5   → always the last digit!

# Does it divide cleanly?
100 % 4 == 0   # True → 100 is divisible by 4
```

## 🧠 Expert Insight

> In C, Java, and most other languages, integers have a size limit — usually around 2 billion.
> Go over that, and the number silently wraps to a wrong value.
>
> Python integers have **no limit at all**.
> They grow as large as your RAM allows.
> This is why Python is trusted for financial systems and scientific computing.

```python
# This would crash in C. In Python, it just works:
x = 999_999_999_999_999_999_999_999_999_999
print(x + 1)    # 1000000000000000000000000000000  ← no crash
```

## ⚠️ The Trap

```python
# / (division) ALWAYS gives a float — even when the answer is perfectly whole:
print(10 / 2)      # 5.0  ← float, not 5!
print(type(10/2))  # <class 'float'>

# Use // when you want a whole number result:
print(10 // 2)     # 5  ← int ✓
```

---

# 📖 Chapter 2 — `float` · The Decimal Number

## 🎬 The Story

Your election counter is working great.
Now someone asks: "What percentage of total votes did each candidate get?"

Percentages are never whole numbers.
56.3% can't be an `int`.
You need `float`.

```python
candidate_a  = 530
total_votes  = 942
percentage   = (candidate_a / total_votes) * 100
print(f"{percentage:.1f}%")    # 56.3%
```

## 💡 The Concept

`float` handles any number with a decimal point.
Prices, temperatures, percentages, measurements, coordinates.

```python
pi          = 3.14159265358979
temperature = 36.6
price       = 999.99
latitude    = 28.6139      # New Delhi
tiny        = 1.5e-4       # scientific notation: 0.00015
big         = 1.5e10       # 15,000,000,000
```

## 💻 The Code You'll Actually Use

```python
# Rounding:
print(round(3.14159, 2))    # 3.14   → 2 decimal places
print(round(3.14159, 0))    # 3.0    → 0 decimal places (still a float!)
print(round(2.5))           # 2      → banker's rounding! rounds to nearest EVEN
print(round(3.5))           # 4      → rounds to nearest EVEN

# Useful float checks:
print((7.0).is_integer())   # True   → 7.0 is mathematically whole
print((7.5).is_integer())   # False

# Special values:
infinity = float('inf')
not_a_number = float('nan')  # result of invalid math
print(1.8e308)               # inf   → beyond float's limit
```

## 🧠 Expert Insight

> The most famous Python shock for beginners:

```python
print(0.1 + 0.2)    # 0.30000000000000004
```

Not a bug. A fundamental truth about computers.

`0.1` in binary is an infinite repeating number — just like `1/3` in decimal (0.333...).
The computer stores an approximation. Small errors accumulate when you do math on approximations.

**How professionals handle it:**
```python
# ❌ Never compare floats directly:
0.1 + 0.2 == 0.3              # False

# ✅ Round before comparing:
round(0.1 + 0.2, 10) == 0.3   # True

# ✅ For financial calculations — use the decimal module:
from decimal import Decimal
Decimal("0.1") + Decimal("0.2")   # Decimal('0.3') — exact!
```

> Banks and trading systems never use `float` for money.
> They use `Decimal` or store amounts in integer paise/cents.

## ⚠️ The Trap

```python
# int + float always gives float:
print(5 + 2.0)    # 7.0  ← float, not 7

# int() truncates — it does NOT round:
int(3.9)   # 3    ← not 4!
int(3.1)   # 3
int(-3.9)  # -3   ← not -4!

# Use round() if you want rounding:
round(3.9)  # 4  ✓
```

---

# 📖 Chapter 3 — `bool` · True or False

## 🎬 The Story

Your app now has login.
Either the password matches, or it doesn't.
Either the user is an admin, or they're not.
Either the session is active, or it's expired.

There's no in-between.
You need `bool`.

```python
is_logged_in    = True
is_admin        = False
session_active  = True

if is_logged_in and is_admin:
    print("Welcome, admin!")
elif is_logged_in:
    print("Welcome, user!")
else:
    print("Please log in.")
```

## 💡 The Concept

`bool` has exactly two values: `True` and `False`.
Every decision in your program eventually comes down to one of these.

## 💻 The Code You'll Actually Use

```python
# Comparison operators all return bool:
print(10 > 5)      # True
print(10 == 5)     # False
print(10 != 5)     # True
print("a" < "b")   # True   (alphabetical order)

# Logic:
print(True and False)   # False  → both must be True
print(True or False)    # True   → at least one must be True
print(not True)         # False  → flip it

# Short-circuit evaluation (very important):
# Python stops as early as it can:
x = None
if x is not None and x > 0:    # safe! — if x is None, it stops after "is not None"
    print("positive")
```

## 🧠 Expert Insight

> **The surprising truth: `bool` is a subtype of `int`.**
>
> Under the hood, `True == 1` and `False == 0`.
> This is not a coincidence — it's intentional.

```python
print(True == 1)      # True
print(False == 0)     # True
print(True + True)    # 2   ← yes, you can add booleans!
print(True * 10)      # 10
print(False * 10)     # 0
```

This is actually **useful in real code:**
```python
exam_results = [True, False, True, True, False, True]
passed = sum(exam_results)    # counts True as 1
print(f"{passed} out of {len(exam_results)} passed")
# 4 out of 6 passed
```

**Truthiness — Python's silent superpower:**

```
Falsy  (behaves like False):  0  0.0  ""  []  {}  ()  set()  None  False
Truthy (behaves like True):   everything else
```

```python
username = ""
if username:                # "" is falsy — condition is False
    print("Hello,", username)
else:
    print("Please enter a username")    # this runs

cart = [1, 2, 3]
if cart:                    # non-empty list is truthy
    print("Items in cart:", len(cart))  # this runs
```

## ⚠️ The Trap

```python
# "0" (string) is TRUTHY — only the empty string "" is falsy!
bool("0")       # True   ← surprising!
bool("False")   # True   ← yes, the string "False" is truthy!

# A list containing False is truthy:
bool([False])   # True   ← the list has one item, so it's truthy

# None is falsy, but 0 and None are different:
0 == False      # True
None == False   # False
```

---

# 📖 Chapter 4 — `str` · Text

## 🎬 The Story

Your app now sends welcome messages, shows usernames, formats reports.
All of this is text.
Text is everywhere in software.
Learning to work with strings well separates good developers from great ones.

```python
name    = "Alice"
message = f"Welcome back, {name}! You have 3 new notifications."
print(message)   # Welcome back, Alice! You have 3 new notifications.
```

## 💡 The Concept

`str` (string) holds any sequence of characters: letters, digits, spaces, symbols, emojis.
Strings are **immutable** — once created, they cannot be changed.
Every string operation creates a new string.

## 💻 The Code You'll Actually Use

**Creating strings:**
```python
single   = 'hello'
double   = "hello"                  # same thing
multi    = """This spans
multiple lines."""

name = "Alice"
age  = 25

# f-strings — the cleanest way to embed values:
print(f"Name: {name}, Age: {age}")                  # Name: Alice, Age: 25
print(f"Next year: {age + 1}")                      # any expression works
print(f"Pi: {3.14159:.2f}")                         # Pi: 3.14  (format specifier)
print(f"Amount: {1_234_567:,}")                     # Amount: 1,234,567
```

**Indexing and slicing (strings are sequences):**
```
  "P  y  t  h  o  n"
   0  1  2  3  4  5      ← forward index
  -6 -5 -4 -3 -2 -1      ← backward index
```

```python
s = "Python"

print(s[0])      # 'P'       first character
print(s[-1])     # 'n'       last character
print(s[0:3])    # 'Pyt'     index 0 to 2 (stop is excluded!)
print(s[2:])     # 'thon'    from index 2 to end
print(s[::-1])   # 'nohtyP'  reversed
print(s[::2])    # 'Pto'     every 2nd character
```

**The most useful string methods:**
```python
s = "  Hello, World!  "

# Cleaning:
s.strip()               # "Hello, World!"    remove whitespace from both sides
s.lstrip()              # "Hello, World!  "  left only
s.rstrip()              # "  Hello, World!"  right only

# Case:
"hello".upper()         # "HELLO"
"HELLO".lower()         # "hello"
"hello world".title()   # "Hello World"

# Searching:
"hello world".find("world")     # 6   → starting index, -1 if not found
"hello world".count("l")        # 3
"hello".startswith("hel")       # True
"world" in "hello world"        # True   ← easiest membership check

# Splitting and joining:
"a,b,c".split(",")              # ['a', 'b', 'c']
" ".join(["hello", "world"])    # "hello world"   ← opposite of split!
"a-b-c".replace("-", "/")       # "a/b/c"
```

## 🧠 Expert Insight

> Strings are immutable. Every method *returns* a new string — it never changes the original.
> This trips up almost every beginner.

```python
original = "hello"
result   = original.upper()

print(original)   # "hello"  ← untouched!
print(result)     # "HELLO"  ← new string

# This is a very common mistake:
name = "  alice  "
name.strip()          # ← this does NOTHING useful — you discarded the result!
name = name.strip()   # ← this is correct
```

> **String concatenation in a loop is slow.**
> Every `+` creates a new string in memory.
> For joining many pieces, use `join()` — it's dramatically faster:

```python
# ❌ Slow — creates a new string in every iteration:
result = ""
for word in words:
    result = result + word + " "

# ✅ Fast — builds once at the end:
result = " ".join(words)
```

## ⚠️ The Trap

```python
# You CANNOT change a character:
s = "hello"
# s[0] = "H"   ← TypeError! Strings are immutable!

# Create a new string instead:
s = "H" + s[1:]       # "Hello"  ✓

# count() is case-sensitive:
"Hello World".count("l")          # 2   (finds 2 l's)
"Hello World".lower().count("l")  # 3   (finds 3 l's — the L in World too)
```

---

# 📖 Chapter 5 — `list` · The Ordered Collection

## 🎬 The Story

Your app now has a shopping cart.
A user adds items. Removes items. Reorders them.
One container that holds multiple things and lets you change it.

You need a `list`.

```python
cart = ["laptop", "mouse", "keyboard"]
cart.append("USB hub")           # user adds an item
cart.remove("mouse")             # user removes one
print(f"Cart has {len(cart)} items")   # Cart has 3 items
```

## 💡 The Concept

A list is an **ordered, changeable** collection.
It can hold any types of data, even mixed types, even other lists.
Think of it as a numbered locker row — each locker has an index, and you can open, fill, or empty any locker.

## 💻 The Code You'll Actually Use

```python
fruits = ["apple", "banana", "cherry"]

# Accessing (same as strings):
print(fruits[0])      # "apple"
print(fruits[-1])     # "cherry"
print(fruits[0:2])    # ["apple", "banana"]

# Unlike strings — you CAN change items:
fruits[0] = "avocado"
print(fruits)   # ["avocado", "banana", "cherry"]

# Adding:
fruits.append("date")           # add ONE item to the end
fruits.insert(1, "blueberry")   # insert at a specific index
fruits.extend(["elderberry", "fig"])  # add MULTIPLE items

# Removing:
fruits.remove("banana")    # remove by VALUE (first match)
last = fruits.pop()        # remove & return the last item
first = fruits.pop(0)      # remove & return item at index 0

# Useful operations:
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
print(len(numbers))          # 8   → how many items
print(sum(numbers))          # 31  → total
print(min(numbers))          # 1   → smallest
print(max(numbers))          # 9   → largest
print(numbers.count(1))      # 2   → how many times 1 appears

# Sorting:
numbers.sort()               # sorts IN PLACE — changes the original!
sorted_copy = sorted(numbers)  # creates a NEW sorted list — original unchanged
```

## 🧠 Expert Insight

> **The difference between `append` and `extend` confuses everyone once.**

```python
a = [1, 2, 3]
b = [1, 2, 3]

a.append([4, 5])    # a = [1, 2, 3, [4, 5]]  ← adds the LIST itself as one item
b.extend([4, 5])    # b = [1, 2, 3, 4, 5]    ← adds each item separately
```

> **`sort()` vs `sorted()` — know the difference:**

```python
original = [3, 1, 4, 1, 5]

original.sort()         # modifies original, returns None
copy = sorted(original) # leaves original alone, returns new list

# sort() returning None is a common trap:
result = original.sort()
print(result)   # None  ← not the sorted list!
```

> List comprehensions — the most Pythonic way to build lists:

```python
# Old way:
squares = []
for x in range(1, 6):
    squares.append(x ** 2)

# Pythonic way — one clean line:
squares = [x ** 2 for x in range(1, 6)]   # [1, 4, 9, 16, 25]

# With a filter:
evens = [x for x in range(10) if x % 2 == 0]  # [0, 2, 4, 6, 8]
```

## ⚠️ The Trap — The Copy Trap That Causes Production Bugs

```python
a = [1, 2, 3]
b = a           # ← this is NOT a copy! Both names point to the SAME list!

b.append(4)
print(a)   # [1, 2, 3, 4]  ← a changed! You never touched a!

# This has caused real bugs in production systems.

# How to actually copy a list:
b = a.copy()   # ✅ method 1
b = a[:]       # ✅ method 2
b = list(a)    # ✅ method 3
```

---

# 📖 Chapter 6 — `tuple` · The Sealed Package

## 🎬 The Story

Your app now stores GPS coordinates for delivery locations.
Once a delivery address is set, it should never change mid-journey.
A wrong coordinate update could send the driver to the wrong city.

You need something like a list, but **sealed**.
That's a `tuple`.

```python
delivery_location = (28.6139, 77.2090)   # New Delhi — lat, long — sealed!

# If you try:
# delivery_location[0] = 19.0760   ← TypeError! Cannot change it.
```

## 💡 The Concept

A tuple is exactly like a list, **except it cannot be changed after creation.**
No adding, no removing, no modifying.
Once sealed, it stays sealed.

## 💻 The Code You'll Actually Use

```python
coordinates = (10.5, 25.3)
rgb         = (255, 128, 0)

# Accessing — same as list:
print(coordinates[0])    # 10.5
print(coordinates[-1])   # 25.3
print(len(coordinates))  # 2

# Parentheses are optional — the comma makes it a tuple:
point = 10, 20        # still a tuple!

# Single-item tuple — the comma is MANDATORY:
single = (42,)        # tuple ✓
not_tuple = (42)      # just the number 42 — parentheses don't make tuples!
print(type(single))   # <class 'tuple'>
print(type(not_tuple)) # <class 'int'>  ← surprise!
```

**Tuple unpacking — the real power:**
```python
# Instead of:
point = (10, 20)
x = point[0]
y = point[1]

# Do this — clean and readable:
x, y = point         # x=10, y=20

# Works with any structure:
r, g, b = (255, 128, 0)
first, *rest = (1, 2, 3, 4, 5)   # first=1, rest=[2,3,4,5]

# Swapping variables — the most elegant Python trick:
a, b = 10, 20
a, b = b, a          # swap! Python creates a tuple (b,a) then unpacks
print(a, b)          # 20 10
```

## 🧠 Expert Insight

> **When to choose tuple over list:**
>
> - Data that should never be modified (coordinates, colors, dates)
> - Returning multiple values from a function (functions naturally return tuples)
> - Dictionary keys — lists can't be dict keys, but tuples can!
> - Slightly faster and uses less memory than lists

```python
# Tuples as dict keys — very common in real systems:
cache = {}
cache[(40.7128, -74.0060)] = "New York"   # ✓ works!
cache[(28.6139, 77.2090)]  = "New Delhi"  # ✓ works!

# [40.7128, -74.0060] would fail as a dict key — lists are unhashable!
```

> **Functions naturally return tuples when returning multiple values:**

```python
def get_min_max(numbers):
    return min(numbers), max(numbers)   # returns a tuple (min, max)

low, high = get_min_max([3, 1, 4, 1, 5])
print(low, high)   # 1 5
```

## ⚠️ The Trap

```python
# A tuple CAN contain mutable objects — and those CAN be changed!
t = ([1, 2], [3, 4])
t[0].append(99)      # ← this works! The list inside the tuple changed.
print(t)             # ([1, 2, 99], [3, 4])

# The tuple still points to the same two lists — it didn't change.
# But the lists themselves are mutable and can still be modified.
# This surprises people who think "tuple = fully frozen."
```

---

# 📖 Chapter 7 — `set` · Only Unique Items

## 🎬 The Story

Your app tracks which students attended today's class.
Students scan their card. Some scan twice by mistake.
You don't want duplicates in your attendance record.
And at the end of the day, you want to know who attended both Monday AND Tuesday.

You need a `set`.

```python
monday    = {"Alice", "Bob", "Charlie", "Alice"}  # Alice scanned twice
print(monday)    # {'Alice', 'Bob', 'Charlie'}    ← duplicate gone automatically!

tuesday   = {"Bob", "Charlie", "Diana"}
both_days = monday & tuesday    # who came both days?
print(both_days)   # {'Bob', 'Charlie'}
```

## 💡 The Concept

A set is a collection of **unique items with no duplicates**.
It has no guaranteed order — items are stored in a way that makes lookup extremely fast.

## 💻 The Code You'll Actually Use

```python
s = {1, 2, 3, 4}
s = {1, 2, 2, 3, 3, 3}    # → {1, 2, 3}  — duplicates removed automatically!

# From a list (great for deduplication):
tags = ["python", "backend", "python", "api", "backend"]
unique_tags = set(tags)    # {'python', 'backend', 'api'}

# IMPORTANT: empty set must use set(), not {}:
empty_set  = set()    # ✅ empty set
empty_dict = {}       # ← this is an empty DICTIONARY

# Adding / removing:
colors = {"red", "green", "blue"}
colors.add("yellow")         # add one
colors.discard("purple")     # remove — NO error if item doesn't exist
colors.remove("red")         # remove — KeyError if missing!
random_item = colors.pop()   # remove & return a random item
```

**Set math — the most powerful feature:**
```python
python_devs = {"Alice", "Bob", "Charlie", "Diana"}
java_devs   = {"Bob", "Eve", "Charlie", "Frank"}

# Union — everyone in either team:
all_devs = python_devs | java_devs
# {'Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank'}

# Intersection — in both teams:
fullstack = python_devs & java_devs
# {'Bob', 'Charlie'}

# Difference — Python devs who don't know Java:
python_only = python_devs - java_devs
# {'Alice', 'Diana'}

# Symmetric difference — in one team but not both:
exclusive = python_devs ^ java_devs
# {'Alice', 'Diana', 'Eve', 'Frank'}
```

## 🧠 Expert Insight

> **Sets are O(1) for membership checks — this changes everything.**

```python
# With a list — Python checks every item one by one:
big_list = list(range(1_000_000))
999_999 in big_list     # slow — checks up to 1 million items!

# With a set — Python uses a hash to jump straight to the answer:
big_set = set(range(1_000_000))
999_999 in big_set      # instant — doesn't matter if there's 10 or 10 million items!
```

> In real systems, sets are used to track visited URLs (web crawlers),
> seen user IDs (deduplication), or blacklisted tokens (auth systems).
> The speed difference at scale is enormous.

## ⚠️ The Trap

```python
# Sets have no order — you cannot index them:
s = {3, 1, 4, 1, 5}
print(s[0])    # ← TypeError! Sets don't support indexing.

# If you need unique items AND order, use a list + dict trick:
seen = {}
ordered_unique = [seen.setdefault(x, x) for x in [3,1,4,1,5] if x not in seen]
# Or simpler — convert to set, then sort:
sorted(set([3, 1, 4, 1, 5]))   # [1, 3, 4, 5]

# Sets can only contain hashable (immutable) items:
{[1, 2], [3, 4]}   # ← TypeError! Lists can't be in a set!
{(1, 2), (3, 4)}   # ✓ Tuples are immutable, so they can be in a set.
```

---

# 📖 Chapter 8 — `dict` · Labeled Storage

## 🎬 The Story

Your app now has user profiles.
Each profile has a name, email, age, city, plan, and subscription status.
You could store this in a list: `["Alice", "alice@mail.com", 25, "Mumbai", "premium", True]`

But then `profile[2]` means... age? plan? Nobody knows.

You need something where you look things up by **name**, not by position.
That's a `dict`.

```python
profile = {
    "name":     "Alice",
    "email":    "alice@mail.com",
    "age":      25,
    "city":     "Mumbai",
    "plan":     "premium",
    "active":   True
}

print(profile["name"])    # "Alice"    ← clear, readable, obvious
print(profile["plan"])    # "premium"
```

## 💡 The Concept

A dictionary stores **key-value pairs**.
You look up a key, you instantly get its value.
Like a real dictionary — look up the word, get the definition.

```
List  → you look things up by POSITION (0, 1, 2...)
Dict  → you look things up by NAME (any key you choose)
```

## 💻 The Code You'll Actually Use

```python
person = {"name": "Alice", "age": 25, "city": "Mumbai"}

# Reading values:
print(person["name"])                        # "Alice"   → KeyError if key missing!
print(person.get("phone"))                   # None      → safe, no crash
print(person.get("phone", "Not provided"))   # "Not provided"  → with default

# Adding and updating:
person["email"] = "alice@mail.com"    # add new key
person["age"]   = 26                  # update existing key
person.update({"age": 27, "city": "Delhi"})  # update multiple at once

# Removing:
del person["email"]                   # delete — KeyError if missing
age = person.pop("age")               # remove and return value
age = person.pop("phone", None)       # safe pop — returns None if missing

# Checking existence:
"name" in person          # True   → checks KEYS
"Alice" in person         # False  → keys, not values!
"Alice" in person.values() # True  → check values explicitly

# Looping:
for key in person:
    print(key)                  # just keys

for value in person.values():
    print(value)                # just values

for key, value in person.items():
    print(f"{key}: {value}")    # both — most common
```

## 🧠 Expert Insight

> **`dict.get()` is the professional's choice.**
> Using `dict[key]` when the key might be missing will crash your app.
> Using `dict.get(key)` returns `None` gracefully.
> Using `dict.get(key, default)` lets you specify a fallback.

```python
# Counting items — the classic dict pattern:
sentence = "the cat sat on the mat"
word_count = {}

for word in sentence.split():
    word_count[word] = word_count.get(word, 0) + 1
    # get current count (default 0) and add 1

print(word_count)   # {'the': 2, 'cat': 1, 'sat': 1, 'on': 1, 'mat': 1}
```

> **Nested dicts are everywhere in real systems.**
> APIs return JSON, which maps directly to nested dicts in Python.

```python
api_response = {
    "status": "success",
    "user": {
        "id": 42,
        "name": "Alice",
        "preferences": {
            "theme": "dark",
            "language": "en"
        }
    }
}

# Accessing nested data:
print(api_response["user"]["name"])                     # "Alice"
print(api_response["user"]["preferences"]["theme"])     # "dark"

# Safe access for nested keys that might be missing:
theme = api_response.get("user", {}).get("preferences", {}).get("theme", "light")
```

> **Dict comprehensions — clean and fast:**

```python
# Old way:
squared = {}
for x in range(1, 6):
    squared[x] = x ** 2

# Pythonic way:
squared = {x: x**2 for x in range(1, 6)}
# {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
```

## ⚠️ The Trap

```python
# Keys must be immutable (hashable):
{[1,2]: "value"}    # ← TypeError! Lists can't be keys.
{(1,2): "value"}    # ✓ tuples can be keys.

# Looping and deleting at the same time will crash:
d = {"a": 1, "b": 2, "c": 3}
for key in d:
    del d[key]        # ← RuntimeError! Can't change dict size during iteration

# Safe way — iterate over a copy of keys:
for key in list(d.keys()):
    del d[key]        # ✓ works
```

---

# 📖 Chapter 9 — `None` · The Intentional Blank

## 🎬 The Story

Your app has a user registration form.
Phone number is optional.
Some users skip it.

What do you store for their phone?
Not `""` — that suggests they entered an empty string.
Not `0` — that's a number, not "missing."
Not `False` — that means something different.

You need a special value that says: **"Nothing here, intentionally."**
That's `None`.

```python
profile = {
    "name":  "Alice",
    "email": "alice@mail.com",
    "phone": None              # ← phone not provided — intentionally empty
}

if profile["phone"] is None:
    print("Phone not on file")
else:
    print("Phone:", profile["phone"])
```

## 💡 The Concept

`None` is Python's way of representing **the absence of a value**.
It's not zero, not empty string, not False.
It's nothing — on purpose.

## 💻 The Code You'll Actually Use

```python
# When does None appear?

# 1. You set it deliberately:
result = None

# 2. A function with no return statement:
def greet():
    print("hello")        # no return

output = greet()          # prints "hello"
print(output)             # None ← function returned nothing

# 3. .get() on a missing dict key:
d = {"a": 1}
print(d.get("b"))         # None

# Checking for None — ALWAYS use 'is', not '==':
if result is None:
    print("No result yet")

if result is not None:
    print("Got:", result)
```

## 🧠 Expert Insight

> **`None` is a singleton.** There is exactly one `None` object in all of Python.
> `is None` checks if you have *that exact object*.
> `== None` also works technically, but `is None` is more precise and is PEP 8 style.

> **None as a sentinel value — the professional pattern:**

```python
# Distinguish between "not passed" and "passed as None":
def create_user(name, phone=None):
    user = {"name": name}
    if phone is not None:          # explicitly provided
        user["phone"] = phone
    return user

# "I don't have a phone" (explicit None) vs "I didn't say" (default None)
# This lets you build optional-field APIs cleanly.
```

## ⚠️ The Trap

```python
# None is falsy — be careful with this:
value = None
if not value:
    print("no value")   # ← this runs for BOTH None AND 0, "" etc.!

# If you specifically mean None, check for None specifically:
if value is None:
    print("value is None")     # ← precise
```

---

# 📖 Chapter 10 — Type Conversion · The Bridge

## 🎬 The Story

Your app reads user input.
The user types their age: `"25"`.
Python sees a string.
You need an integer.

The data is right.
The type is wrong.
You need to convert it.

```python
age_input = input("Enter your age: ")   # user types: 25
print(type(age_input))                  # <class 'str'>

age = int(age_input)                    # convert to int
print(age + 1)                          # 26  ✓
```

## 💡 The Concept

Python lets you explicitly convert between types.
This is called **type casting** or **type conversion**.

## 💻 The Conversion Map

```python
# → int
int("42")         # 42      string that looks like a number
int(3.9)          # 3       truncates — does NOT round!
int(True)         # 1
int(False)        # 0
# int("hello")    # ❌ ValueError!
# int("3.14")     # ❌ ValueError — convert to float first!
int(float("3.14")) # 3  ✓

# → float
float("3.14")     # 3.14
float(42)         # 42.0
float("inf")      # inf   (special value!)

# → str
str(42)           # "42"
str(3.14)         # "3.14"
str(True)         # "True"
str([1, 2, 3])    # "[1, 2, 3]"  (list representation)

# → bool
bool(0)           # False
bool(1)           # True
bool("")          # False
bool("0")         # True  ← "0" is a non-empty string!
bool([])          # False
bool([False])     # True  ← non-empty list!

# → list
list("Python")    # ['P','y','t','h','o','n']
list((1, 2, 3))   # [1, 2, 3]   tuple → list
list({1, 2, 3})   # [1, 2, 3]   set → list (order may vary)

# → tuple
tuple([1, 2, 3])  # (1, 2, 3)
tuple("abc")      # ('a', 'b', 'c')

# → set (removes duplicates!)
set([1, 2, 2, 3]) # {1, 2, 3}
set("hello")      # {'h', 'e', 'l', 'o'}  (one 'l')
```

## 🧠 Expert Insight

> **The most common real-world conversion — user input:**

```python
# input() ALWAYS returns str — no matter what:
name = input("Name: ")               # str — correct
age  = int(input("Age: "))           # convert immediately ✓
gpa  = float(input("GPA: "))         # convert immediately ✓

# Handling invalid input safely:
raw = input("Enter a number: ")
try:
    number = int(raw)
except ValueError:
    print(f"'{raw}' is not a valid number")
```

## ⚠️ The Trap

```python
# int() truncates, doesn't round:
int(3.9)    # 3  ← not 4!
int(3.1)    # 3
int(-3.9)   # -3 ← not -4!

# Use round() when you want proper rounding:
round(3.9)   # 4  ✓

# int("3.14") fails — string must look exactly like an int:
int("3.14")        # ❌ ValueError
int(float("3.14")) # ✓ two-step conversion
```

---

# 🏆 Expert Chapter — Choosing the Right Type

## The Decision Matrix

```
I need a single value...
  └─ whole number?          → int
  └─ decimal number?        → float
  └─ text?                  → str
  └─ yes/no?                → bool
  └─ maybe nothing?         → None

I need multiple values...
  └─ ordered + changeable?   → list
  └─ ordered + sealed?       → tuple
  └─ unique items only?      → set
  └─ look up by name?        → dict
```

## Real Structures You'll Build in Production

```python
# API response — nested dict + list:
users = [
    {"id": 1, "name": "Alice", "tags": ["admin", "active"]},
    {"id": 2, "name": "Bob",   "tags": ["user"]},
]

# Config — dict of mixed types:
config = {
    "debug":       False,
    "max_retries": 3,
    "timeout":     30.0,
    "allowed_ips": {"192.168.1.1", "10.0.0.1"},
    "db_url":      "postgresql://localhost/mydb",
    "secret":      None,     # not set yet
}

# Immutable record — tuple in dict:
locations = {
    "hq":      (28.6139, 77.2090),   # New Delhi
    "branch1": (19.0760, 72.8777),   # Mumbai
}
```

## The Mental Shortcuts Seniors Use

```
Need fast lookup?          → dict or set
Need to preserve order?    → list or tuple
Need to prevent changes?   → tuple
Need unique items?         → set
Need to label data?        → dict
Working with sequences?    → list or str or tuple
Working with "maybe"?      → None
```

---

# 🎯 Final — The 9 Things You Now Know

```
int    → whole numbers, no size limit, use // and % heavily
float  → decimals, precision trap is real, never == floats directly
bool   → True/False, subtype of int, truthiness is everywhere
str    → immutable, methods return new strings, f-strings are gold
list   → mutable ordered collection, the copy trap is real
tuple  → immutable ordered collection, unpack it, use as dict keys
set    → unique items, O(1) lookup, set math is powerful
dict   → labeled storage, use .get() always, nest freely
None   → intentional emptiness, always check with 'is'
```

> These nine types are not just containers.
> They are the vocabulary of Python.
> Once you think in them naturally — choosing the right one without hesitation —
> you stop being someone who codes in Python
> and start being a Python developer.

---

# 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [02 — Control Flow](../02_control_flow/theory.md) |
| 📖 Deep Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview Prep | [interview.md](./interview.md) |
| 💻 Practice | [practice.py](./practice.py) |
| ➡️ Next | [04 — Functions](../04_functions/theory.md) |
