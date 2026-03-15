# 🐍 Python Fundamentals

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

```python
import copy

a = [[1, 2], [3, 4]]
b = copy.copy(a)
c = copy.deepcopy(a)
```

Shallow copy:
Copies outer structure only.

Deep copy:
Copies everything recursively.

If nested objects are modified:
Shallow copy may still reflect changes.

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

**[🏠 Back to README](../README.md)**

**Prev:** [← Memory Management — Interview Q&A](../01.1_memory_management/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
