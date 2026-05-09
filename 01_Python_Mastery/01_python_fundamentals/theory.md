<a id="top"></a>
# 🐍 Python Fundamentals

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. print() and Basic I/O](#1-print-and-basic-io)
  - [What Can You Print?](#what-can-you-print)
  - [The sep= and end= Options](#the-sep-and-end-options)
  - [The Most Common Beginner Mistake](#the-most-common-beginner-mistake)
  - [Getting Input from the User](#getting-input-from-the-user)
- [2. Programming vs Scripting](#2-programming-vs-scripting)
  - [Where Does Python Sit?](#where-does-python-sit)
  - [What Kind of Language Is Python?](#what-kind-of-language-is-python)
- [3. Python's Key Features](#3-pythons-key-features)
  - [1. You Just Run It — No Waiting Step](#you-just-run-it)
  - [2. You Don't Declare Types](#you-dont-declare-types)
  - [3. Everything Is an Object](#everything-is-an-object)
  - [4. Python Cleans Up After Itself](#python-cleans-up-after-itself)
  - [5. Python Comes With Tools Already Installed](#python-comes-with-tools)
  - [6. Same Code Works Everywhere](#same-code-works-everywhere)
  - [7. Code That Reads Like a Sentence](#code-that-reads-like-a-sentence)
- [4. Python Basics — Comments, Quotes, and Indentation](#4-python-basics)
  - [Comments — Notes for Humans, Ignored by Python](#comments)
  - [String Quotes — Single, Double, and Triple](#string-quotes)
  - [Indentation — The Rule That Makes Python Unique](#indentation)
- [5. Variables & Memory Model in Python](#5-variables-memory-model)
  - [The Biggest Lie Beginners Believe](#the-biggest-lie)
  - [What a Variable REALLY Is](#what-a-variable-really-is)
  - [The Juice Bottle Model (10-Year-Old Version)](#the-juice-bottle-model)
  - [Let's See It in Code](#lets-see-it-in-code)
  - [The Classic Production Bug](#the-classic-production-bug)
  - [What Actually Exists in Memory?](#what-actually-exists-in-memory)
  - [Rebinding (Very Important Concept)](#rebinding)
  - [Mutable vs Immutable (Where Things Get Serious)](#mutable-vs-immutable)
  - ["is" vs "==" (Interview Favorite)](#is-vs)
  - [Small Integer Interning (Advanced Understanding)](#small-integer-interning)
  - [Shallow Copy vs Deep Copy (Real Production Issue)](#shallow-copy-vs-deep-copy)
  - [Garbage Collection (High-Level View)](#garbage-collection)
  - [Real-World System Example](#real-world-system-example)
  - [Senior-Level Mental Model](#senior-level-mental-model)
  - [Interview Questions You Should Now Answer Confidently](#interview-questions)
  - [Final Understanding Check](#final-understanding-check)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
Variables and types · Mutability (list vs tuple vs str) · `is` vs `==` · `None` handling · Dynamic typing · LEGB scope rule

**Should Learn** — Important for real projects, comes up regularly:
Integer caching · String interning · `pass` / `assert` · Augmented assignment (`+=`, `-=`)

**Good to Know** — Useful in specific situations:
`divmod()` · `hex()` / `oct()` / `bin()` · Raw strings (`r"..."`) · Escape sequences

**Reference** — Know it exists, look up when needed:
`complex` type · Old-style `%` string formatting

<a id="1-print-and-basic-io"></a>
# 1. print() and Basic I/O

<a id="what-can-you-print"></a>
## What Can You Print?

**Text:**

```python
print("Hello")
print("My name is Alice")
print("Python is fun")
```

**Numbers:**

```python
print(42)
print(3.14)
```

**A variable (a named value):**

```python
name = "Alice"
age  = 25

print(name)    # → Alice
print(age)     # → 25
```

**Multiple things at once — separate them with commas:**

```python
name = "Alice"
age  = 25

print("Name:", name, "Age:", age)
# → Name: Alice Age: 25
```

When you use commas, Python automatically puts a space between each item.

<a id="the-sep-and-end-options"></a>
## The sep= and end= Options

By default, `print()` separates items with a space and adds a new line at the end.
You can change both of these.

**sep= — change what goes between items:**

```python
print("Alice", "Bob", "Charlie")
# → Alice Bob Charlie          (default: space between)

print("Alice", "Bob", "Charlie", sep=", ")
# → Alice, Bob, Charlie        (comma + space between)

print("Alice", "Bob", "Charlie", sep=" | ")
# → Alice | Bob | Charlie      (custom separator)
```

**end= — change what goes at the end of the line:**

```python
print("Hello")
print("World")
# → Hello
# → World         (each print on its own line — default)

print("Hello", end=" ")
print("World")
# → Hello World   (stays on the same line)
```

You don't need to memorise these. Just know they exist.
You'll reach for them naturally when you need them.

<a id="the-most-common-beginner-mistake"></a>
## The Most Common Beginner Mistake

```python
name = "Alice"

print(name)     # prints the VALUE stored in name: Alice
print("name")   # prints the WORD "name" literally
```

When you write `print(name)` — no quotes — Python looks up the variable called `name` and prints its value.

When you write `print("name")` — with quotes — Python treats it as text and prints the word literally.

Quotes = text.
No quotes = variable.

This confusion trips up almost every beginner at least once.

<a id="getting-input-from-the-user"></a>
## Getting Input from the User — input()

So far your programs just run and finish.
But real programs talk to the user.

`input()` pauses your program and waits for the user to type something.

```python
name = input("What is your name? ")
print("Hello,", name)
```

When this runs:
```
What is your name? Alice
Hello, Alice
```

The text inside `input("...")` is the prompt — what the user sees.
Whatever they type gets stored in the variable.

**Important rule — input() always gives you text:**

```python
age = input("How old are you? ")
print(age)        # looks like a number
print(type(age))  # <class 'str'>  but it's actually text!
```

Even if the user types `25`, Python stores it as `"25"` (text), not `25` (number).

To use it as a number, you must convert it:

```python
age = input("How old are you? ")
age = int(age)          # convert text to whole number
print(age + 1)          # now you can do maths with it
```

Or in one line:

```python
age = int(input("How old are you? "))
print(age + 1)
```

**The three most common input patterns:**

```python
name = input("Enter name: ")           # text — no conversion needed
age  = int(input("Enter age: "))       # whole number
price = float(input("Enter price: "))  # decimal number
```

You will use `input()` in almost every beginner exercise.
Always remember: convert it before doing any maths.

> [↑ Back to Top](#top)

<a id="2-programming-vs-scripting"></a>
# 2. Programming vs Scripting — What's the Difference?

> You've heard both words. Let's clear up the confusion once and for all.

Imagine two people working in a kitchen.

One person **built the kitchen** — designed the stoves, installed the pipes, wired the electricity.
That is a **programmer**. They build the thing from scratch.

The other person **uses the kitchen** — they follow a recipe, press buttons, make coffee.
That is a **scripter**. They automate tasks using tools someone else built.

| | Programming | Scripting |
|---|---|---|
| **What you do** | Build the tool | Use the tool |
| **Examples** | Build WhatsApp, build YouTube | Send 100 emails automatically, rename 1000 files |
| **Difficulty** | Harder to learn | Easier to learn |
| **Languages** | C, C++, Java | Bash, Python |

<a id="where-does-python-sit"></a>
## Where Does Python Sit?

Python is **both** — and that is very rare.

You can use Python to:
- Build a full website (like Instagram — yes, it runs on Python)
- Automate boring tasks on your computer
- Analyse data and build AI models
- Write a simple 5-line script that does one job

Most languages force you to pick a lane. Python lets you do everything.

<a id="what-kind-of-language-is-python"></a>
## What Kind of Language Is Python?

Python is described in many ways. Here is what each label means in plain English:

| Label | Plain English meaning |
|---|---|
| **Interpreted** | Python reads and runs your code line by line, like reading a recipe step by step. You don't need to do anything before running it. |
| **High-level** | You write words that look like English. Python handles the low-level machine details for you. |
| **Dynamically typed** | You never have to say "this is a number" or "this is text". Python figures it out on its own. |
| **General-purpose** | Not built for one thing. Works for websites, AI, data, automation, scripts — all of it. |
| **Multi-paradigm** | Python supports many different coding styles. You can write it in whatever way makes sense to you. |

Python is not the fastest language in the world. But it is the most versatile and readable. That is why it became the most popular language on earth.

> [↑ Back to Top](#top)

<a id="3-pythons-key-features"></a>
# 3. Python's Key Features — What Makes It Special

> These are the things that make Python different from other languages.
> You don't need to memorise them — just understand the ideas.

<a id="you-just-run-it"></a>
## 1. You Just Run It — No Waiting Step

With some languages like C or Java, you have to "build" your code before you can run it.
It is like baking a cake before you can eat it.

Python is different. You write code, you run it, you see the result. Immediately.

```python
print("Hello, world!")
```

Save that in a file. Run it. Done. No build step.

**How Python runs your code — what actually happens:**

```
  your_script.py
       |
       v
  Python Interpreter reads source line by line
       |
       v
  Compiles to Bytecode  (.pyc  stored in __pycache__/)
       |
       v
  CPython VM executes bytecode instruction by instruction
       |
       v
  Output / Result on your screen

  Compare:
  C/Java:  source --> [compile step: seconds/minutes] --> binary --> run
  Python:  source -->                                               run
                      (compile happens internally, invisibly)
```

This is what "interpreted" means: no separate compile step from your perspective.

<a id="you-dont-declare-types"></a>
## 2. You Don't Declare Types

In many languages, you must tell the computer: "this is a number" or "this is text".

In Python, you just write it. Python figures out the type itself.

```python
name = "Alice"   # Python knows this is text
age  = 25        # Python knows this is a number
score = 98.5     # Python knows this is a decimal number
```

You never wrote "text" or "number" anywhere. Python understood on its own.

<a id="everything-is-an-object"></a>
## 3. Everything Is an Object

In Python, every piece of data is an **object** — a thing with properties and behaviours.

A number is an object. A word is an object. A list is an object.

You don't need to understand this deeply right now. You will see it naturally as you learn more.

For now, just know: Python treats all data the same way. This makes the language consistent and predictable.

<a id="python-cleans-up-after-itself"></a>
## 4. Python Cleans Up After Itself

In some older languages, you manually had to tell the computer "I'm done with this data, delete it".

Python does this automatically. When data is no longer needed, Python removes it from memory on its own.

You never have to think about it. Python handles it.

<a id="python-comes-with-tools"></a>
## 5. Python Comes With Tools Already Installed

When you install Python, you get hundreds of built-in tools for free.

Need to read a file? There's a tool.
Need to work with dates? There's a tool.
Need to send a web request? There's a tool.

```python
import datetime
print(datetime.date.today())   # prints today's date — no extra install needed
```

It is like buying a Swiss Army knife — it already has a blade, scissors, and a screwdriver.

<a id="same-code-works-everywhere"></a>
## 6. Same Code Works Everywhere

Write your Python code once on a Windows computer.
Send it to someone on a Mac or Linux.
It runs exactly the same.

No changes needed.

<a id="code-that-reads-like-a-sentence"></a>
## 7. Code That Reads Like a Sentence

Python was designed to look like plain English.

```python
name = "Alice"
age = 25
print("My name is", name, "and I am", age, "years old")
```

You can almost read that out loud and it makes sense.
That is not an accident — Python was built this way on purpose.

> [↑ Back to Top](#top)

<a id="4-python-basics"></a>
# 4. Python Basics — Comments, Quotes, and Indentation

> These are the three things you must understand before writing any Python code.
> None of them are complicated. Let's go through them one by one.

<a id="comments"></a>
## Comments — Notes for Humans, Ignored by Python

A **comment** is a line in your code that Python completely ignores.
It is a note you write for yourself (or other developers) to explain what the code does.

```python
# This is a comment. Python will not run this line.

name = "Alice"   # You can also put a comment at the end of a line
```

The `#` symbol tells Python: "everything after this is a comment, skip it."

**Why write comments?**

Imagine you write 100 lines of code today. You come back 3 months later.
Without comments, you will have no idea what you were doing.
Comments are your future self's best friend.

```python
# Store the user's name
name = "Alice"

# Store the user's age
age = 25

# Show a greeting message
print("Hello", name)
```

**Multi-line notes** — if you want to write a longer note across multiple lines:

```python
"""
This block of text is a longer note.
Python ignores it because we didn't store it anywhere.
You can write as many lines as you want here.
"""
```

Note: You will learn more about these triple-quote blocks in the functions chapter.
For now, just know they exist and Python skips them when they are not stored.

<a id="string-quotes"></a>
## String Quotes — Single, Double, and Triple

A **string** is how you write text in Python.
Text must always be wrapped in quotes so Python knows where it starts and ends.

Python gives you three ways to write text:

```python
greeting = 'Hello'       # single quotes
greeting = "Hello"       # double quotes — exactly the same thing
```

Single and double quotes do the same job. Use whichever you prefer.

**But there is one practical difference — apostrophes and quote marks inside text:**

```python
msg = "It's a great day"       # apostrophe inside: use double quotes outside
msg = 'He said "hello"'        # quote inside: use single quotes outside
```

**Triple quotes** — for text that spans multiple lines:

```python
message = """
Hello Alice,

Welcome to Python.
We are glad you are here.
"""

print(message)
```

**Raw strings (r"...")** — when you need backslashes to be treated as normal characters:

```python
# Without raw string — backslash has special meaning:
# \n = new line, \t = tab — NOT what you want for file paths

# With raw string:
path = r"C:\new_folder\tasks"   # r before the quote = raw string
# Now Python reads it exactly as written
```

You will mostly use raw strings for file paths on Windows.

**f-strings — putting variables directly inside text:**

```python
name = "Alice"
age = 25

# Without f-string (old way, harder to read):
print("Hello " + name + ", you are " + str(age) + " years old")

# With f-string (modern way, clean):
print(f"Hello {name}, you are {age} years old")
# Hello Alice, you are 25 years old
```

Put an `f` before the opening quote. Then put any variable name inside `{ }`.
Python will replace it with the actual value.

<a id="indentation"></a>
## Indentation — The Rule That Makes Python Unique

Most programming languages use `{` and `}` curly braces to group lines of code together.

Python uses **indentation** — how far a line is pushed to the right.

```
x = 10

if x > 5:
    print("x is big")    <- this line is indented (4 spaces)
    print("still big")   <- same indent = still inside the if block

print("always runs")     <- no indent = outside the if block
```

**The rules are simple:**
- Use **4 spaces** for each level of indent (most editors do this automatically)
- Every line in the same block must have exactly the same indent
- Never mix tabs and spaces — Python 3 will give you an error

**What happens if you get it wrong:**

```python
if x > 5:
print("big")      # IndentationError: expected an indented block

name = "Alice"
    age = 25      # IndentationError: unexpected indent
```

**Why does Python use indentation instead of braces?**

Because indentation makes code easier to read at a glance.
Python's creator decided: if good programmers indent anyway, let's make it the rule.

> [↑ Back to Top](#top)

<a id="5-variables-memory-model"></a>
# 5. Variables & Memory Model in Python

> If you misunderstand this chapter, Python will confuse you for years.
> If you understand this deeply, Python becomes predictable.

This chapter is not about syntax. It is about how Python *thinks*.

If you understand this once, clearly, you will avoid:
- 70% of beginner confusion
- 50% of production bugs
- Most tricky interview traps

Let's build this properly.

> 📝 **Practice:** [Q1 · variable-binding](../python_practice_questions_100.md#q1--normal--variable-binding)

<a id="the-biggest-lie"></a>
## The Biggest Lie Beginners Believe

Most people are taught:

> "A variable is a box that stores a value."

This is wrong in Python. Python does NOT use a box model.

If you continue thinking like that:
- Lists will confuse you
- Functions will confuse you
- Object-oriented programming will confuse you
- Memory bugs will confuse you

So forget the box model.

<a id="what-a-variable-really-is"></a>
## What a Variable REALLY Is

In Python:

> A variable is just a name that points to an object.

It does not store data.
It does not contain data.
It does not own data.

It only references data.

<a id="the-juice-bottle-model"></a>
## The Juice Bottle Model (10-Year-Old Version)

Imagine a table. On the table is a juice bottle.

Now you put a sticker on it that says:

```
mango
```

That sticker is a variable. Now you put another sticker: `drink`.

Both stickers are pointing to the SAME bottle. If someone drinks from the bottle, both stickers still point to that bottle. The bottle did not duplicate. The labels just refer to it.

That is exactly how Python variables work:

```
  Label  →  Variable
  Bottle →  Object
```

<a id="lets-see-it-in-code"></a>
## Let's See It in Code

```python
a = [1, 2, 3]
b = a
```

What happens internally?

1. Python creates a list object `[1, 2, 3]` in memory.
2. The name `a` points to that object.
3. The name `b` also points to the same object.

```python
print(id(a))
print(id(b))
# Both print the SAME address — there is only ONE object
```

<a id="the-classic-production-bug"></a>
## The Classic Production Bug

```python
a = [1, 2, 3]
b = a

b.append(4)

print(a)   # [1, 2, 3, 4]  — why did a change?
```

Because there were not two lists. There were two names pointing to one list.

This misunderstanding has caused real production outages.

<a id="what-actually-exists-in-memory"></a>
## What Actually Exists in Memory?

```
  NAMESPACE (variables)        HEAP (objects)
  ---------------------        -------------------------
  a  ----------------------->  [ list: 1, 2, 3 ]
                               refcount = 2
  b  ----------------------->  (same object, same address)

  After: b.append(4)

  a  ----------------------->  [ list: 1, 2, 3, 4 ]
  b  ----------------------->  (still the same object — both see the change)
```

In Python:
- Objects live in heap memory.
- Variables live in namespaces.
- Names map to object references.

<a id="rebinding"></a>
## Rebinding (Very Important Concept)

```python
x = 10
x = 20
```

Did Python change 10 into 20? No.

It created a new object `20`, then moved the label `x` to point to 20.
The object `10` still exists (if referenced elsewhere).

```
  Before:   x --> [10]   refcount=1

  After x=20:
            x --> [20]   refcount=1
                  [10]   refcount=0  <- eligible for garbage collection
```

Variables don't modify objects. They rebind references.

<a id="mutable-vs-immutable"></a>
## Mutable vs Immutable (Where Things Get Serious)

**Immutable** — changing creates a NEW object: `int`, `float`, `str`, `tuple`, `bool`, `frozenset`

**Mutable** — changing modifies the SAME object: `list`, `dict`, `set`, custom objects

```
IMMUTABLE (int):
  x = 10
  y = x
  x = x + 1

  Before:  x --> [10] <-- y     (shared)
  After:   x --> [11]
                 [10] <-- y     (y unchanged, 10 still exists)

MUTABLE (list):
  a = [1, 2]
  b = a
  a.append(3)

  Before:  a --> [1, 2] <-- b
  After:   a --> [1, 2, 3] <-- b   (same object mutated, b sees the change)
```

<a id="is-vs"></a>
## "is" vs "==" (Interview Favorite)

`==` checks **value**. `is` checks **identity** (memory address).

```python
a = [1]
b = [1]

print(a == b)  # True  — same value
print(a is b)  # False — different objects in memory
```

```
  a --> [ list: 1 ]   address: 0x1000
  b --> [ list: 1 ]   address: 0x2000

  a == b  compares contents  --> True
  a is b  compares addresses --> False
```

Never use `is` for value comparison. Use `==`.

**Common mistake — using `is` for string/int equality:** `if x is "hello"` sometimes works due to interning, sometimes fails. Always use `==` for values.

> 📝 **Practice:** [Q2 · identity-vs-equality](../python_practice_questions_100.md#q2--logical--identity-vs-equality) · [Q22 · type-conversion](../python_practice_questions_100.md#q22--normal--type-conversion)

<a id="small-integer-interning"></a>
## Small Integer Interning (Advanced Understanding)

```python
a = 10
b = 10
print(a is b)  # True  — Python caches small ints (-5 to 256)

a = 1000
b = 1000
print(a is b)  # False — large ints get separate objects
```

```
  Small integers (cached, shared):
    a = 10 --> [10]  (pre-existing CPython object)
    b = 10 --> [10]  (same pre-existing object)
    a is b  --> True

  Large integers (not cached):
    a = 1000 --> [1000]  (new object)
    b = 1000 --> [1000]  (another new object)
    a is b  --> False
```

Never rely on this behavior in your code.

<a id="shallow-copy-vs-deep-copy"></a>
## Shallow Copy vs Deep Copy (Real Production Issue)

Copying an object seems simple until you hit the bug:
you "copy" a list, modify the copy, and the original changes too.

```python
import copy

a = [[1, 2], [3, 4]]
b = copy.copy(a)      # shallow copy
c = copy.deepcopy(a)  # deep copy

b[0][0] = 999
print(a)   # [[999, 2], [3, 4]]  original changed!
print(c)   # [[1, 2], [3, 4]]   deep copy is independent
```

```
SHALLOW COPY — copies outer container, shares inner objects:

  a --> [ ref0, ref1 ]
             |      |
  b --> [ ref0, ref1 ]   <- same inner list objects!
             |
           [1, 2]   <- modifying b[0][0] modifies THIS shared object

DEEP COPY — copies everything recursively:

  a --> [ ref0, ref1 ]          c --> [ ref2, ref3 ]
             |      |                       |      |
           [1,2]  [3,4]                   [1,2]  [3,4]   <- independent copies
```

**Three ways to make a shallow copy:**

```python
b = copy.copy(original)  # explicit
c = original[:]          # slice (lists only)
d = list(original)       # constructor
e = original.copy()      # .copy() method
# All four are shallow — inner objects still shared
```

**When you need deep copy:**

```python
import copy
base_config = {"limits": {"rate": 100, "burst": 200}}

request_config = copy.copy(base_config)
request_config["limits"]["rate"] = 50   # also modifies base_config!

request_config = copy.deepcopy(base_config)
request_config["limits"]["rate"] = 50   # only affects request_config
```

**Performance:** `deepcopy` is significantly slower. Use shallow copy for flat structures (no nested mutables).

<a id="garbage-collection"></a>
## Garbage Collection (High-Level View)

When no variable references an object anymore, Python deletes it from memory.

Python uses two mechanisms:

```
Reference counting:

  a = [1, 2, 3]   list refcount = 1
  b = a           list refcount = 2
  del a           list refcount = 1
  b = None        list refcount = 0  <- Python frees memory immediately

Cyclic references (refcounting alone cannot catch):

  a = {}
  b = {}
  a["ref"] = b    b refcount = 2
  b["ref"] = a    a refcount = 2
  del a, b        both still refcount = 1 (cycle!)
                  CPython's cyclic GC detects and clears these periodically
```

Understanding this helps with memory leaks, large datasets, and long-running services.

For a deep dive: [01.1_memory_management/theory.md](../01.1_memory_management/theory.md)

<a id="real-world-system-example"></a>
## Real-World System Example

```python
default_config = {"timeout": 30}
user_config = default_config      # shared reference!

user_config["timeout"] = 60
print(default_config)   # {"timeout": 60}  — oops!
```

Shared reference silently modified the "default" config. This happens in real production code.
Fix: `user_config = copy.deepcopy(default_config)` to make a fully independent copy.

<a id="senior-level-mental-model"></a>
## Senior-Level Mental Model

Think of memory as a warehouse:

```
  Objects  =  Boxes in warehouse
  Variables =  Labels (stickers) attached to boxes

  You can: add labels, remove labels, move labels to different boxes
  But boxes stay until NO label points to them
  Once no label exists: Garbage Collector removes the box
```

<a id="interview-questions"></a>
## Interview Questions You Should Now Answer Confidently

1. What is a variable in Python?
2. Do variables have types?
3. Difference between mutable and immutable objects?
4. Explain `is` vs `==`.
5. What happens in `a = b`?
6. What is shallow copy vs deep copy?
7. How does Python manage memory?
8. What is reference counting?
9. Why do small integers share memory?
10. What happens when you pass a list to a function?

If you can answer these clearly, you are not a beginner anymore.

<a id="final-understanding-check"></a>
## Final Understanding Check

If someone says:

> "Python variables store values."

You should confidently say:

No. Python variables store **references** to objects.

That one sentence separates beginners from professionals.

> [↑ Back to Top](#top)

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | *(first module — no previous)* |
| ➡ Next Module | [02_control_flow → theory.md](../02_control_flow/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[01.1 Memory Management →](../01.1_memory_management/theory.md) · [02 Control Flow →](../02_control_flow/theory.md) · [03 Data Types →](../03_data_types/theory.md)

**Jump to specific topics in other files:**
- Mutable default arg trap → [04_functions § Parameters — Type 3: Default Args](../04_functions/theory.md#4-parameters--arguments--all-7-types)
- LEGB scope rules → [04_functions § Scope — The LEGB Rule](../04_functions/theory.md#6-scope--the-legb-rule)
- Reference counting deep dive → [01.1_memory_management § Reference Counting](../01.1_memory_management/theory.md#3-reference-counting)
- Garbage collection deep dive → [01.1_memory_management § Garbage Collector (GC)](../01.1_memory_management/theory.md#4-garbage-collector-gc)

**Practice:** [Q25 · unpacking](../python_practice_questions_100.md#q25--thinking--unpacking) · [Q24 · truthiness](../python_practice_questions_100.md#q24--normal--truthiness)

> [↑ Back to Top](#top)
