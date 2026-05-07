# 🐍 Python Fundamentals

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
Variables and types · Mutability (list vs tuple vs str) · `is` vs `==` · `None` handling · Dynamic typing · LEGB scope rule

**Should Learn** — Important for real projects, comes up regularly:
Integer caching · String interning · `pass` / `assert` · Augmented assignment (`+=`, `-=`)

**Good to Know** — Useful in specific situations:
`divmod()` · `hex()` / `oct()` / `bin()` · Raw strings (`r"..."`) · Escape sequences

**Reference** — Know it exists, look up when needed:
`complex` type · Old-style `%` string formatting

---

# 1️⃣ What is Python?

Imagine you want to talk to a computer.

The computer only understands 0s and 1s. But we are humans — we think in English.

Python is like a translator friend.

You say:
"Add two numbers"

Python converts that into something the computer understands.

That’s it.

Python is:
- High-level (human readable)
- Interpreted (runs line by line)
- Dynamically typed
- Object-oriented
- Very powerful

Python was created by Guido van Rossum in 1991.

> 📝 **Practice:** [Q23 · none-checks](../python_practice_questions_100.md#q23--thinking--none-checks)

---

# 2️⃣ How Python Actually Runs Your Code

Let’s say you write:

print("Hello")

Here’s what happens internally:

1. You write code in `.py` file
2. Python converts it to bytecode
3. Bytecode runs inside Python Virtual Machine (PVM)
4. Output is printed

So Python is not directly running your code.
It runs bytecode inside its virtual machine.

Think of it like:

You speak English → Translator converts → Computer understands

---

# 3️⃣ Your First Line of Code — print()

> Every Python journey starts here.

When you want Python to show you something — a word, a number, a result — you use `print()`.

That's it. That's the job. `print()` displays output on the screen.

```python
print("Hello, world!")
```

Run that. You will see:

```
Hello, world!
```

---

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

---

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

---

## The Most Common Beginner Mistake

```python
name = "Alice"

print(name)     # ✅ prints the VALUE stored in name → Alice
print("name")   # ❌ prints the WORD "name" → name
```

When you write `print(name)` — no quotes — Python looks up the variable called `name` and prints its value.

When you write `print("name")` — with quotes — Python treats it as text and prints the word literally.

Quotes = text.
No quotes = variable.

This confusion trips up almost every beginner at least once.

---

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
print(type(age))  # <class 'str'>  ← but it's actually text!
```

Even if the user types `25`, Python stores it as `"25"` (text), not `25` (number).

To use it as a number, you must convert it:

```python
age = input("How old are you? ")
age = int(age)          # convert text → whole number
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

---

# 4️⃣ Programming vs Scripting — What's the Difference?

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

## Where Does Python Sit?

Python is **both** — and that is very rare.

You can use Python to:
- Build a full website (like Instagram — yes, it runs on Python)
- Automate boring tasks on your computer
- Analyse data and build AI models
- Write a simple 5-line script that does one job

Most languages force you to pick a lane. Python lets you do everything.

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

---

# 5️⃣ Python's Key Features — What Makes It Special

> These are the things that make Python different from other languages.
> You don't need to memorise them — just understand the ideas.

## 1. You Just Run It — No Waiting Step

With some languages like C or Java, you have to "build" your code before you can run it.
It is like baking a cake before you can eat it.

Python is different. You write code → you run it → you see the result. Immediately.

```python
print("Hello, world!")
```

Save that in a file. Run it. Done. No build step.

## 2. You Don't Declare Types

In many languages, you must tell the computer: "this is a number" or "this is text".

In Python, you just write it. Python figures out the type itself.

```python
name = "Alice"   # Python knows this is text
age  = 25        # Python knows this is a number
score = 98.5     # Python knows this is a decimal number
```

You never wrote "text" or "number" anywhere. Python understood on its own.

## 3. Everything Is an Object

In Python, every piece of data is an **object** — a thing with properties and behaviours.

A number is an object. A word is an object. A list is an object.

You don't need to understand this deeply right now. You will see it naturally as you learn more.

For now, just know: Python treats all data the same way. This makes the language consistent and predictable.

## 4. Python Cleans Up After Itself

In some older languages, you manually had to tell the computer "I'm done with this data, delete it".

Python does this automatically. When data is no longer needed, Python removes it from memory on its own.

You never have to think about it. Python handles it.

## 5. Python Comes With Tools Already Installed

When you install Python, you get hundreds of built-in tools for free.

Need to read a file? There's a tool.
Need to work with dates? There's a tool.
Need to send a web request? There's a tool.

```python
import datetime
print(datetime.date.today())   # prints today's date — no extra install needed
```

It is like buying a Swiss Army knife — it already has a blade, scissors, and a screwdriver. You didn't have to buy them separately.

## 6. Same Code Works Everywhere

Write your Python code once on a Windows computer.
Send it to someone on a Mac or Linux.
It runs exactly the same.

No changes needed.

## 7. Code That Reads Like a Sentence

Python was designed to look like plain English.

```python
name = "Alice"
age = 25
print("My name is", name, "and I am", age, "years old")
```

You can almost read that out loud and it makes sense.
That is not an accident — Python was built this way on purpose.

---

# 6️⃣ Python Basics — Comments, Quotes, and Indentation

> These are the three things you must understand before writing any Python code.
> None of them are complicated. Let's go through them one by one.

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

---

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
# If your text contains an apostrophe, use double quotes on the outside:
msg = "It's a great day"       # ✅ clean and easy to read

# If your text contains double quotes, use single quotes on the outside:
msg = 'He said "hello"'        # ✅ clean and easy to read

# If you use the same quote type inside and outside, you get an error:
msg = 'It's a great day'       # ❌ Python gets confused — where does the string end?
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

Use triple quotes when your text is long and needs to go across several lines — like an email, a paragraph, or a block of instructions.

**Raw strings (r"...")** — when you need backslashes to be treated as normal characters:

```python
# Normal string — backslash has special meaning:
path = "C:
ew_folder	asks"
# Python reads 
 as "new line" and 	 as "tab" — not what you wanted!

# Raw string — backslash is just a backslash:
path = r"C:
ew_folder	asks"   # ← r before the quote = raw string
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
# → Hello Alice, you are 25 years old
```

Put an `f` before the opening quote. Then put any variable name inside `{ }`.
Python will replace it with the actual value.

---

## Indentation — The Rule That Makes Python Unique

Most programming languages use `{` and `}` curly braces to group lines of code together.

Python does something different. It uses **indentation** — how far a line is pushed to the right.

```
x = 10

if x > 5:
    print("x is big")    ← this line is indented (pushed right by 4 spaces)
    print("still big")   ← same indent = still inside the if block

print("always runs")     ← no indent = outside the if block, always runs
```

The 4 spaces on lines 3 and 4 tell Python: "these lines belong to the `if` block".
The line with no indent tells Python: "this is outside the block".

**The rules are simple:**
- Use **4 spaces** for each level of indent (most editors do this automatically)
- Every line in the same block must have exactly the same indent
- Never mix tabs and spaces — Python 3 will give you an error

**What happens if you get it wrong:**

```python
# ❌ Forgot to indent — Python expects it here:
if x > 5:
print("big")      # IndentationError: expected an indented block

# ❌ Extra indent where Python didn't expect one:
name = "Alice"
    age = 25      # IndentationError: unexpected indent

# ❌ Mixed tabs and spaces — looks the same to your eyes, error to Python:
if x > 5:
	print("tab")       # ← pressed Tab key
    print("spaces")    # ← pressed Space 4 times
    # TabError: inconsistent use of tabs and spaces
```

**Why does Python use indentation instead of braces?**

Because indentation makes code easier to read at a glance.
You can immediately see which lines belong together, just by looking at the shape of the code.
Python's creator decided: if good programmers indent anyway, let's make it the rule.

---

# 🧠 Variables & Memory Model in Python

> If you misunderstand this chapter, Python will confuse you for years.  
> If you understand this deeply, Python becomes predictable.

This chapter is not about syntax.  
It is about how Python *thinks*.

If you understand this once, clearly, you will avoid:
- 70% of beginner confusion
- 50% of production bugs
- Most tricky interview traps

Let’s build this properly.

> 📝 **Practice:** [Q1 · variable-binding](../python_practice_questions_100.md#q1--normal--variable-binding)

---

# 🚫 The Biggest Lie Beginners Believe

Most people are taught:

> “A variable is a box that stores a value.”

This is wrong in Python.

Python does NOT use a box model.

If you continue thinking like that:
- Lists will confuse you
- Functions will confuse you
- Object-oriented programming will confuse you
- Memory bugs will confuse you

So forget the box model.

---

# 🏷 What a Variable REALLY Is

In Python:

> A variable is just a name that points to an object.

It does not store data.  
It does not contain data.  
It does not own data.

It only references data.

---

# 🧃 Story: The Juice Bottle Model (10-Year-Old Version)

Imagine a table.

On the table is a juice bottle.

Now you put a sticker on it that says:

```
mango
```

That sticker is a variable.

Now you put another sticker:

```
drink
```

Both stickers are pointing to the SAME bottle.

If someone drinks from the bottle,
both stickers still point to that bottle.

The bottle did not duplicate.
The labels just refer to it.

That is exactly how Python variables work.

Label → Variable  
Bottle → Object  

Simple.

---

# 🧪 Let’s See It in Code

```python
a = [1, 2, 3]
b = a
```

What happens internally?

1. Python creates a list object `[1, 2, 3]` in memory.
2. The name `a` points to that object.
3. The name `b` also points to the same object.

Check:

```python
print(id(a))
print(id(b))
```

The memory address (identity) will be the same.

Because there is only ONE object.

---

# 💥 The Classic Production Bug

```python
a = [1, 2, 3]
b = a

b.append(4)

print(a)
```

Output:
```
[1, 2, 3, 4]
```

Why did `a` change?

Because:

There were not two lists.  
There were two names pointing to one list.

This misunderstanding has caused real production outages.

---

# 🏗 What Actually Exists in Memory?

In Python:

- Objects live in heap memory.
- Variables live in namespaces.
- Names map to object references.

Internally it looks like:

```
Namespace:
    a  →  0x103abc
    b  →  0x103abc
```

Both names pointing to the same object in memory.

---

# 🔁 Rebinding (Very Important Concept)

```python
x = 10
x = 20
```

Did Python change 10 into 20?

No.

It created a new object `20`.
Then moved the label `x` to point to 20.

The object `10` still exists (if referenced elsewhere).

Variables don’t modify objects.
They rebind references.

This is critical to understand.

---

# 🧊 Mutable vs Immutable (Where Things Get Serious)

Immutable objects:
- int
- float
- str
- tuple
- bool
- frozenset

Mutable objects:
- list
- dict
- set
- most custom objects

If object is immutable:
Changing it creates a new object.

If object is mutable:
Changing it modifies the same object in memory.

Example:

```python
x = 10
y = x
x = x + 1
```

`y` is still 10.

Because integers are immutable.
`x + 1` created a new object.

Now:

```python
a = [1, 2]
b = a
a.append(3)
```

Both `a` and `b` change.

Because list is mutable.

---

# ⚖️ "is" vs "==" (Interview Favorite)

`==` checks value.  
`is` checks identity (memory location).

Example:

```python
a = [1]
b = [1]

print(a == b)  # True
print(a is b)  # False
```

Different objects.
Same value.

Never use `is` for value comparison.

Use `==`.

> 📝 **Practice:** [Q2 · identity-vs-equality](../python_practice_questions_100.md#q2--logical--identity-vs-equality) · [Q22 · type-conversion](../python_practice_questions_100.md#q22--normal--type-conversion)

---

# 🔍 Small Integer Interning (Advanced Understanding)

```python
a = 10
b = 10

print(a is b)  # True
```

Python pre-creates small integers (usually -5 to 256) for performance.

So they share memory.

But:

```python
a = 1000
b = 1000
```

May or may not be same object.

Never rely on this behavior.

---

# 📦 Shallow Copy vs Deep Copy (Real Production Issue)

Copying an object seems simple until you hit the bug:
you "copy" a list, modify the copy, and the original changes too.

```python
import copy

a = [[1, 2], [3, 4]]
b = copy.copy(a)      # shallow copy
c = copy.deepcopy(a)  # deep copy

b[0][0] = 999
print(a)   # [[999, 2], [3, 4]]  ← original changed!
print(c)   # [[1, 2], [3, 4]]   ← deep copy is independent
```

**Why does shallow copy change the original?**

```
SHALLOW COPY — copies the outer container, shares inner objects:

  a ──► [ ref0, ref1 ]
              │      │
  b ──► [ ref0, ref1 ]   ← same inner list objects!
              │
            [1, 2]   ← modifying b[0][0] modifies THIS object
                        which both a[0] and b[0] point to

DEEP COPY — copies everything recursively:

  a ──► [ ref0, ref1 ]
              │      │
            [1,2]  [3,4]

  c ──► [ ref2, ref3 ]   ← completely new inner objects
              │      │
            [1,2]  [3,4]   ← independent copies
```

**Three ways to make a shallow copy:**

```python
import copy

original = [[1, 2], [3, 4]]

b = copy.copy(original)      # explicit shallow copy
c = original[:]              # slice syntax (lists only)
d = list(original)           # list constructor
e = original.copy()          # .copy() method (list, dict, set)

# All four are shallow — inner objects still shared
```

**When you actually need deep copy:**

```python
import copy

# Config that gets modified per-request:
base_config = {"limits": {"rate": 100, "burst": 200}, "enabled": True}

# Shallow copy — limits dict is still shared:
request_config = copy.copy(base_config)
request_config["limits"]["rate"] = 50   # modifies base_config too!

# Deep copy — fully independent:
request_config = copy.deepcopy(base_config)
request_config["limits"]["rate"] = 50   # only affects request_config
```

**Performance note:** `deepcopy` is significantly slower — it must recursively copy every nested object. Only use it when you actually need independence. For flat structures (no nesting), shallow copy is safe and fast.

```python
flat = [1, 2, 3, 4, 5]
copy_flat = flat[:]    # shallow copy is fine — ints are immutable
                       # no nested mutables to worry about
```

This is extremely important in:
- Data pipelines
- API response manipulation
- Configuration management

---

# 🧹 Garbage Collection (High-Level View)

When no variable references an object anymore,
Python deletes it from memory.

Python primarily uses:
- Reference counting
- Cyclic garbage collector

Example:

```python
a = [1, 2, 3]
a = None
```

The list now has no references.
It becomes eligible for garbage collection.

Understanding this helps when dealing with:
- Memory leaks
- Large datasets
- Long-running services

---

# 🚀 Real-World System Example

Imagine you load default configuration:

```python
default_config = {"timeout": 30}
user_config = default_config
```

Now modify:

```python
user_config["timeout"] = 60
```

Suddenly:
Default configuration changed globally.

System behaves unpredictably.

Why?

Shared reference.

This is not theory.
This happens in real companies.

---

# 🧠 Senior-Level Mental Model

Think of memory as a warehouse.

Objects = Boxes in warehouse  
Variables = Labels attached to boxes  

You can:
- Add labels
- Remove labels
- Move labels

But boxes stay until no label points to them.

Once no label exists,
Garbage collector removes the box.

---

# 🎯 Interview Questions You Should Now Answer Confidently

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

If you can answer these clearly,
you are not a beginner anymore.

---

# 🧠 Final Understanding Check

If someone says:

> “Python variables store values.”

You should confidently say:

No.  
Python variables store references to objects.

That one sentence separates beginners from professionals.

---

# 🔁 Navigation

⬅ Previous: `01_python_fundamentals/theory.md`  
➡ Next: `03_data_types/theory.md`

---

## 📝 Practice Questions

> 📝 **Practice:** [Q25 · unpacking](../python_practice_questions_100.md#q25--thinking--unpacking)

> 📝 **Practice:** [Q24 · truthiness](../python_practice_questions_100.md#q24--normal--truthiness)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Memory Management — Interview Q&A](../01.1_memory_management/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)
