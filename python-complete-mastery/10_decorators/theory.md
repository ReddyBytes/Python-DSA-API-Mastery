# 🎁 Decorators in Python  
From Simple Wrappers to Production-Grade Function Engineering

---

# 🎯 Why Decorators Exist

Imagine you have 50 functions.

You want to:

- Log every function call
- Measure execution time
- Add authentication check
- Add retry logic
- Validate inputs

You do NOT want to rewrite each function.

Decorators allow you to:

Add behavior to a function
Without modifying its original code.

That is extremely powerful.

---

# 🧠 1️⃣ Step Back — Functions Are Objects

Before decorators,
you must understand this:

In Python, functions are objects.

Example:

```python
def greet():
    print("Hello")

print(type(greet))
```

Output:

```
<class 'function'>
```

That means:

- You can pass functions as arguments
- You can return functions
- You can assign them to variables

Example:

```python
say_hello = greet
say_hello()
```

This prints:
Hello

This is foundation of decorators.

---

# 🧠 2️⃣ Higher-Order Functions

A higher-order function is:

A function that:

- Takes another function as argument
OR
- Returns a function

Example:

```python
def wrapper(func):
    def inner():
        print("Before function")
        func()
        print("After function")
    return inner
```

This is almost a decorator.

---

# 🧱 3️⃣ Manual Decoration (Without @ Syntax)

Example:

```python
def greet():
    print("Hello")

greet = wrapper(greet)
greet()
```

Output:

```
Before function
Hello
After function
```

What happened?

We replaced greet with wrapped version.

Decorator = syntactic sugar for this.

---

# 🎯 4️⃣ Actual Decorator Syntax

Python provides:

```python
@decorator_name
def function():
    ...
```

Equivalent to:

```python
function = decorator_name(function)
```

Example:

```python
def decorator(func):
    def inner():
        print("Before")
        func()
        print("After")
    return inner

@decorator
def greet():
    print("Hello")
```

---

# 🧠 5️⃣ Handling Function Arguments

If decorated function takes arguments:

Wrong version:

```python
def inner():
    func()
```

This fails.

Correct version:

```python
def inner(*args, **kwargs):
    return func(*args, **kwargs)
```

Always use:

*args and **kwargs

To make decorator generic.

---

# 🔍 6️⃣ What Is a Closure?

Inner function remembers outer variables.

Example:

```python
def outer():
    x = 10
    def inner():
        print(x)
    return inner
```

Even after outer finishes,
inner still remembers x.

Decorators rely on closures.

---

# 🧠 7️⃣ Why Function Name Changes After Decoration?

Example:

```python
print(greet.__name__)
```

You may see:

```
inner
```

Because wrapper replaces original function.

To fix:

Use functools.wraps.

```python
from functools import wraps

def decorator(func):
    @wraps(func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs)
    return inner
```

This preserves:

- Function name
- Docstring
- Metadata

Important in production.

---

# 🏗 8️⃣ Real Production Use Cases

---

## 🔹 Logging Decorator

```python
def log_decorator(func):
    def inner(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return inner
```

---

## 🔹 Timing Decorator

```python
import time

def timer(func):
    def inner(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print("Time taken:", end - start)
        return result
    return inner
```

Used in performance analysis.

---

## 🔹 Authentication Decorator

```python
def require_auth(func):
    def inner(user, *args, **kwargs):
        if not user.is_authenticated:
            raise Exception("Unauthorized")
        return func(user, *args, **kwargs)
    return inner
```

Used in web frameworks.

---

## 🔹 Retry Decorator

```python
def retry(func):
    def inner(*args, **kwargs):
        for _ in range(3):
            try:
                return func(*args, **kwargs)
            except Exception:
                continue
        raise Exception("Failed after retries")
    return inner
```

Used in network calls.

---

# 🧠 9️⃣ Decorators With Arguments

Sometimes decorator itself needs argument.

Example:

```python
def repeat(n):
    def decorator(func):
        def inner(*args, **kwargs):
            for _ in range(n):
                func(*args, **kwargs)
        return inner
    return decorator
```

Usage:

```python
@repeat(3)
def greet():
    print("Hello")
```

This is:

Decorator factory.

---

# 🧠 🔟 Class-Based Decorators

Instead of function:

```python
class Decorator:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        print("Before")
        return self.func(*args, **kwargs)
```

Usage:

```python
@Decorator
def greet():
    print("Hello")
```

Advanced but useful.

---

# ⚡ 1️⃣1️⃣ Decorators Stack (Multiple Decorators)

Example:

```python
@decorator1
@decorator2
def func():
    pass
```

Equivalent to:

```python
func = decorator1(decorator2(func))
```

Order matters.

---

# 🧠 1️⃣2️⃣ Decorators in Frameworks

Real examples:

Flask:

```python
@app.route("/home")
def home():
    pass
```

Django:

```python
@login_required
def dashboard():
    pass
```

These are decorators.

They modify behavior of functions.

---

# 🧠 1️⃣3️⃣ Common Mistakes

❌ Forgetting *args, **kwargs  
❌ Not returning result  
❌ Not using functools.wraps  
❌ Modifying function signature incorrectly  
❌ Confusing decorator vs function call  

---

# 🏆 1️⃣4️⃣ Engineering Maturity Levels

Beginner:
Understands @ syntax.

Intermediate:
Writes reusable decorators.

Advanced:
Uses decorators for logging, caching, validation.

Senior:
Designs decorator-based architecture cleanly.

---

# 🧠 Final Mental Model

Decorator is:

A function that takes a function,
wraps it,
returns a new function.

That’s it.

But power comes from:

- Closures
- First-class functions
- Abstraction

Decorators allow behavior injection
without modifying original logic.

They are clean architecture tools.

---

# 🔁 Navigation

Previous:  
[09_logging_debugging/interview.md](../09_logging_debugging/interview.md)

Next:  
[10_decorators/interview.md](./interview.md)

