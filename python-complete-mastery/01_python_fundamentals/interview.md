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

**Q1: What is Python?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> Python is a high-level, interpreted, dynamically typed programming language known for readability, simplicity, and a large standard library.

Keep it simple.
Avoid over-explaining.

</details>

<br>

**Q2: Is Python compiled or interpreted?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> Python is interpreted, but internally it compiles code into bytecode before execution in the Python Virtual Machine (PVM).

This shows deeper understanding.

</details>

<br>

**Q3: What are Python’s key features?**

<details>
<summary>💡 Show Answer</summary>

- Interpreted
- Dynamically typed
- Object-oriented
- Automatic memory management
- Large ecosystem
- Cross-platform

Mention only key points.

</details>

<br>

**Q4: What are Python data types?**

<details>
<summary>💡 Show Answer</summary>

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

</details>

<br>

**Q5: Difference between list and tuple?**

<details>
<summary>💡 Show Answer</summary>

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

</details>

<br>

**Q6: What is dynamic typing?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> In Python, variable types are determined at runtime, not declared explicitly.

Example:

```python
x = 5
x = "hello"
```

</details>

<br>

**Q7: What is None in Python?**

<details>
<summary>💡 Show Answer</summary>

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

</details>


# 🔹 Level 2: 2–5 Years Experience

Now interviewer expects deeper clarity.

---

**Q8: What is mutability?**

<details>
<summary>💡 Show Answer</summary>

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

</details>

<br>

**Q9: Why are strings immutable?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> Strings are immutable to improve memory efficiency, hashing reliability, and performance optimizations like interning.

Shows deeper thinking.

</details>

<br>

**Q10: Difference between == and is?**

<details>
<summary>💡 Show Answer</summary>

`==` → compares value  
`is` → compares memory identity  

Important:

Use `is` for None.

</details>

<br>

**Q11: What is variable scope?**

<details>
<summary>💡 Show Answer</summary>

Local scope:
Inside function.

Global scope:
Defined outside.

[LEGB rule](../04_functions/theory.md#the-legb-pyramid):

- Local
- Enclosing
- Global
- Built-in

Mention [LEGB](../04_functions/theory.md#the-legb-pyramid) explicitly.

</details>

<br>

**Q12: What happens if you modify global variable inside function?**

<details>
<summary>💡 Show Answer</summary>

Must declare:

```python
global x
```

Otherwise:
UnboundLocalError.

</details>

<br>

**Q13: What is pass statement?**

<details>
<summary>💡 Show Answer</summary>

Placeholder.
Does nothing.
Prevents syntax error.

</details>

<br>

**Q14: What is indentation in Python?**

<details>
<summary>💡 Show Answer</summary>

Indentation defines code blocks.

Improper indentation causes:

- Syntax error
- Logical bugs

Python enforces structure via indentation.

</details>


# 🔹 Level 3: 5+ Years Experience

Even seniors get fundamentals wrong.

Now depth matters.

---

**Q15: How does Python manage memory?**

<details>
<summary>💡 Show Answer</summary>

Strong answer:

> Python uses reference counting for memory management, and a cyclic garbage collector to clean up reference cycles.

Mention:
gc module.

</details>

<br>

**Q16: What is object identity?**

<details>
<summary>💡 Show Answer</summary>

Every object has:

- Identity (memory address)
- Type
- Value

Check identity using:

```python
id(obj)
```

</details>

<br>

**Q17: What is small integer caching?**

<details>
<summary>💡 Show Answer</summary>

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

</details>

<br>

**Q18: What is string interning?**

<details>
<summary>💡 Show Answer</summary>

Python may reuse identical string objects to save memory.

Example:

```python
a = "hello"
b = "hello"
a is b  # Often True
```

Implementation detail, but good to know.

</details>


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

<details>
<summary>💡 Show Answer</summary>

Possible cause:

Immutability.

</details>
---

## Scenario 2:

Function behaves unexpectedly due to shared list.

<details>
<summary>💡 Show Answer</summary>

Likely cause:

Mutable default argument.

</details>
---

## Scenario 3:

Unexpected behavior when comparing values using `is`.

<details>
<summary>💡 Show Answer</summary>

Likely cause:

Identity vs equality misunderstanding.

</details>
---

## Scenario 4:

Variable inside function not updating global variable.

<details>
<summary>💡 Show Answer</summary>

Cause:

Missing `global` declaration.

</details>
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

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Control Flow — Theory →](../02_control_flow/theory.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md)
