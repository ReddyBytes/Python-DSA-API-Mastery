# 🎯 Python Fundamentals — Interview Preparation Guide  
From Core Concepts to Confident Answers

---

# 🧠 What Interviewers Evaluate in Fundamentals

Even senior interviews start with fundamentals.

They test:

- Clarity of Python basics
- Understanding of data types
- Variable behavior
- Mutability awareness
- Memory understanding
- Edge case awareness

Strong fundamentals = strong engineer.

---

# 🔹 Level 1: 0–2 Years Experience

Basic clarity and syntax confidence expected.

---

## 1️⃣ What is Python?

Strong answer:

> Python is a high-level, interpreted, dynamically typed programming language known for readability, simplicity, and a large standard library.

Keep it simple.
Avoid over-explaining.

---

## 2️⃣ Is Python compiled or interpreted?

Strong answer:

> Python is interpreted, but internally it compiles code into bytecode before execution in the Python Virtual Machine (PVM).

This shows deeper understanding.

---

## 3️⃣ What are Python’s key features?

- Interpreted
- Dynamically typed
- Object-oriented
- Automatic memory management
- Large ecosystem
- Cross-platform

Mention only key points.

---

## 4️⃣ What are Python data types?

Built-in types:

- int
- float
- bool
- str
- list
- tuple
- set
- dict
- NoneType

Understand behavior of each.

---

## 5️⃣ Difference between list and tuple?

List:
- Mutable
- Uses []
- Slower than tuple

Tuple:
- Immutable
- Uses ()
- Hashable (if elements immutable)

Professional tip:
Tuple can be dictionary key (if immutable).

---

## 6️⃣ What is dynamic typing?

Strong answer:

> In Python, variable types are determined at runtime, not declared explicitly.

Example:

```python
x = 5
x = "hello"
```

---

## 7️⃣ What is None in Python?

None represents absence of value.

Important:

Use:

```python
if x is None:
```

Not:

```python
if x == None:
```

---

# 🔹 Level 2: 2–5 Years Experience

Now interviewer expects deeper clarity.

---

## 8️⃣ What is mutability?

Mutable objects:
Can be changed after creation.

Immutable objects:
Cannot be changed.

Immutable:
- int
- float
- str
- tuple

Mutable:
- list
- dict
- set

Explain clearly.

---

## 9️⃣ Why are strings immutable?

Strong answer:

> Strings are immutable to improve memory efficiency, hashing reliability, and performance optimizations like interning.

Shows deeper thinking.

---

## 🔟 Difference between == and is?

`==` → compares value  
`is` → compares memory identity  

Important:

Use `is` for None.

---

## 1️⃣1️⃣ What is variable scope?

Local scope:
Inside function.

Global scope:
Defined outside.

LEGB rule:

- Local
- Enclosing
- Global
- Built-in

Mention LEGB explicitly.

---

## 1️⃣2️⃣ What happens if you modify global variable inside function?

Must declare:

```python
global x
```

Otherwise:
UnboundLocalError.

---

## 1️⃣3️⃣ What is pass statement?

Placeholder.
Does nothing.
Prevents syntax error.

---

## 1️⃣4️⃣ What is indentation in Python?

Indentation defines code blocks.

Improper indentation causes:

- Syntax error
- Logical bugs

Python enforces structure via indentation.

---

# 🔹 Level 3: 5+ Years Experience

Even seniors get fundamentals wrong.

Now depth matters.

---

## 1️⃣5️⃣ How does Python manage memory?

Strong answer:

> Python uses reference counting for memory management, and a cyclic garbage collector to clean up reference cycles.

Mention:
gc module.

---

## 1️⃣6️⃣ What is object identity?

Every object has:

- Identity (memory address)
- Type
- Value

Check identity using:

```python
id(obj)
```

---

## 1️⃣7️⃣ What is small integer caching?

Python caches small integers (usually -5 to 256) for performance.

So:

```python
a = 100
b = 100
a is b  # True
```

But:

```python
a = 1000
b = 1000
a is b  # Might be False
```

Shows deeper understanding.

---

## 1️⃣8️⃣ What is string interning?

Python may reuse identical string objects to save memory.

Example:

```python
a = "hello"
b = "hello"
a is b  # Often True
```

Implementation detail, but good to know.

---

# 🔥 Common Traps in Fundamentals

---

## 🔹 Mutable Default Arguments

Already classic trap.

---

## 🔹 Shallow vs Deep Copy

Understand difference clearly.

---

## 🔹 Modifying List While Iterating

Leads to unpredictable behavior.

---

## 🔹 None vs False Confusion

Be explicit when checking None.

---

# 🔥 Scenario-Based Questions

---

## Scenario 1:
Code works differently when using tuple instead of list.

Possible cause:

Immutability.

---

## Scenario 2:
Function behaves unexpectedly due to shared list.

Likely cause:

Mutable default argument.

---

## Scenario 3:
Unexpected behavior when comparing values using `is`.

Likely cause:

Identity vs equality misunderstanding.

---

## Scenario 4:
Variable inside function not updating global variable.

Cause:

Missing `global` declaration.

---

# 🧠 How to Answer Fundamentals Like Professional

Weak:

“List is mutable and tuple is immutable.”

Strong:

> “List is a mutable ordered collection allowing modification after creation, whereas tuple is immutable and can be used as dictionary key if its elements are immutable.”

Clarity + detail.

---

# ⚠️ Common Candidate Mistakes

- Confusing is and ==
- Not understanding mutability
- Not knowing LEGB rule
- Not understanding memory basics
- Ignoring None handling
- Overcomplicating simple answers

Fundamentals require clarity, not complexity.

---

# 🎯 Rapid-Fire Revision

- Python is interpreted but compiled to bytecode
- Dynamic typing at runtime
- List mutable, tuple immutable
- == vs is difference
- LEGB scope rule
- global keyword for modification
- Reference counting memory model
- Small integer caching
- Strings immutable
- Use is None

---

# 🏆 Final Interview Mindset

Fundamentals test:

- Clarity
- Precision
- Depth
- Attention to detail

If you:

- Answer clearly
- Avoid over-talking
- Provide small examples
- Explain reasoning calmly

You appear confident and solid.

Strong fundamentals build strong career.

---

# 🔁 Navigation

Previous:  
[01_python_fundamentals/theory.md](./theory.md)

Next:  
[02_control_flow/theory.md](../02_control_flow/theory.md)

