# 🎯 Functions — Interview Preparation Guide

> *"Interviewers don't test whether you can write functions.*
> *They test whether you understand what Python is actually doing."*

---

## 🧠 What Interviewers Actually Evaluate

```
┌──────────────────────────────────────────────────────────────────────┐
│  Level        What They Want to See                                  │
├──────────────────────────────────────────────────────────────────────┤
│  0–2 years    Basic syntax, parameters, return vs print              │
│  2–5 years    Scope, closures, decorators, *args/**kwargs            │
│  5+ years     Memory model, design principles, edge cases, patterns  │
└──────────────────────────────────────────────────────────────────────┘

Strong fundamentals + edge case awareness = professional signal.
```

---

# 🟢 Level 1 — 0 to 2 Years

---

## 1️⃣ What is a function in Python?

**Weak answer:**
> "A function is a block of code you can reuse."

**Strong answer:**
> "A function is a named, isolated execution unit with its own memory frame.
> It accepts inputs (parameters), processes logic, and optionally returns a value.
> When called, Python creates a new stack frame for it — giving it fully isolated memory.
> When it returns, that frame is destroyed.
> This makes functions both reusable and safe — they can't accidentally affect each other's state."

---

## 2️⃣ What is the difference between parameters and arguments?

**Strong answer:**
> "Parameters are the placeholders defined in the function signature.
> Arguments are the actual values passed when the function is called.
> For example, in `def add(a, b)`, `a` and `b` are parameters.
> In `add(10, 5)`, `10` and `5` are arguments.
> Internally, Python assigns arguments to parameters as local variables in the new stack frame."

```python
def add(a, b):         # a, b = parameters
    return a + b

add(10, 5)             # 10, 5 = arguments
```

---

## 3️⃣ What is the difference between `return` and `print`?

**Strong answer:**
> "`print()` sends output to the console but the calling code gets nothing back — the function returns `None`.
> `return` sends the actual value back to the caller so it can be stored, chained, or further processed.
> In production code, you almost always want `return`. `print()` is for debugging only."

```python
def add_bad(a, b):
    print(a + b)          # prints 7, but returns None!

def add_good(a, b):
    return a + b           # returns 7 — usable by caller

result = add_bad(3, 4)    # result = None  ← can't use it further!
result = add_good(3, 4)   # result = 7     ← can chain, calculate, store
```

---

## 4️⃣ What does Python do when a function has no return statement?

**Strong answer:**
> "Python implicitly returns `None`. Every function in Python has a return value —
> if you don't provide one, it's `None` by default."

```python
def greet(name):
    print(f"Hello, {name}")
    # no return

result = greet("Alice")    # prints "Hello, Alice"
print(result)               # None  ← implicit return
print(type(result))         # <class 'NoneType'>
```

**Follow-up trap question:** *"Can a function have multiple return statements?"*
```python
def describe(n):
    if n > 0:
        return "positive"     # exits here if n > 0
    elif n < 0:
        return "negative"     # exits here if n < 0
    return "zero"             # exits here if n == 0
```
> "Yes. Each `return` immediately exits the function. This is the 'early return' or 'guard clause' pattern — very common in production code to avoid deep nesting."

---

## 5️⃣ What are default arguments?

**Strong answer:**
> "Default arguments are values given to parameters in the function definition.
> They're used when the caller doesn't pass that argument.
> One critical rule: parameters with defaults must come AFTER parameters without defaults."

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

greet("Alice")              # Hello, Alice!
greet("Alice", "Hi")        # Hi, Alice!
greet("Alice", greeting="Hey")  # Hey, Alice!
```

> "There's a famous gotcha: never use mutable objects (lists, dicts, sets) as default values. I'll explain in the next question."

---

## 6️⃣ What is the mutable default argument trap? ⚠️

> This question alone can decide an interview. Know this cold.

**Strong answer:**
> "Default argument values are evaluated ONCE — when the function is defined, not every time it's called.
> If you use a mutable object like a list as a default, all calls share the same object.
> So modifications accumulate across calls, causing unexpected behavior."

```python
# ❌ The trap:
def add_item(item, cart=[]):
    cart.append(item)
    return cart

add_item("apple")    # ['apple']       — looks fine
add_item("banana")   # ['apple', 'banana']   — wait, what?!
add_item("cherry")   # ['apple', 'banana', 'cherry']   — the list is shared!
```

```python
# ✅ The fix — always use None:
def add_item(item, cart=None):
    if cart is None:
        cart = []       # new list created each call
    cart.append(item)
    return cart

add_item("apple")    # ['apple']
add_item("banana")   # ['banana']   ← correct!
```

> "This applies to all mutable defaults: lists, dicts, sets, custom objects."

---

## 7️⃣ What are `*args` and `**kwargs`?

**Strong answer:**
> "`*args` collects any number of positional arguments into a **tuple** inside the function.
> `**kwargs` collects any number of keyword arguments into a **dict** inside the function.
> They let you write functions that accept flexible inputs — very common in frameworks and decorators."

```python
def demo(*args, **kwargs):
    print(args)      # tuple: (1, 2, 3)
    print(kwargs)    # dict:  {'name': 'Alice', 'age': 25}

demo(1, 2, 3, name="Alice", age=25)
```

**Follow-up:** *"What is the required order if you combine all parameter types?"*
```python
def full(positional_only, /, regular, default=10, *args, kw_only, **kwargs):
    ...
# Order: positional-only (/) → regular → defaults → *args → keyword-only → **kwargs
```

---

# 🟡 Level 2 — 2 to 5 Years

---

## 8️⃣ Explain the LEGB scope rule.

**Strong answer:**
> "When Python resolves a variable name, it searches in this exact order:
> **L**ocal (current function), **E**nclosing (outer function if nested), **G**lobal (module level), **B**uilt-in (Python's built-ins like `print`, `len`).
> The first match wins. Understanding this explains why the `global` and `nonlocal` keywords exist."

```python
x = "global"

def outer():
    x = "enclosing"

    def inner():
        x = "local"
        print(x)        # "local" — L found first

    def inner2():
        print(x)        # "enclosing" — L not found, E found

    inner()     # "local"
    inner2()    # "enclosing"

outer()
print(x)    # "global"
```

**Follow-up:** *"What's the difference between `global` and `nonlocal`?"*

```python
count = 0

def using_global():
    global count    # reach into module-level scope
    count += 1

def outer():
    count = 0
    def inner():
        nonlocal count   # reach into outer() scope, not module level
        count += 1
    inner()
    return count

# global = module scope
# nonlocal = nearest enclosing function scope
```

---

## 9️⃣ What are first-class functions?

**Strong answer:**
> "In Python, functions are objects — the same kind as integers or strings.
> First-class means they can be: stored in variables, passed as arguments to other functions,
> returned from functions, and stored in data structures like lists or dicts.
> This is the foundation of decorators, callbacks, and functional programming in Python."

```python
def greet():
    return "Hello!"

# Store in variable:
f = greet

# Pass as argument:
def execute(func):
    return func()

execute(greet)    # "Hello!"

# Return from function:
def make_greeter():
    return greet

fn = make_greeter()
fn()    # "Hello!"
```

**Critical distinction:**
```python
x = greet      # stores the function OBJECT — nothing runs
x = greet()    # CALLS the function — runs immediately, stores result
```

---

## 🔟 What is a closure? Give a real-world example.

**Strong answer:**
> "A closure is an inner function that remembers variables from its enclosing scope,
> even after the outer function has finished execution.
> The inner function 'closes over' those variables — they're stored as part of the function object.
> Closures are used to create stateful functions, implement data hiding, and build decorators."

```python
def make_multiplier(factor):
    def multiply(x):
        return x * factor    # factor is from outer scope
    return multiply          # outer function ends, but multiply remembers factor!

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))    # 10   — factor=2 remembered
print(triple(5))    # 15   — factor=3 remembered
print(double.__closure__[0].cell_contents)  # 2  — you can inspect it!
```

**Real-world use case:**
> "Closures are used to create customized loggers, rate limiters, or validators — any time you want a function that's pre-configured with some state without using a full class."

---

## 1️⃣1️⃣ What is the late binding closure trap? ⚠️

> This is one of the top 5 Python interview traps.

**Strong answer:**
> "Closures bind to the VARIABLE in the enclosing scope, not the VALUE at the time of creation.
> This means if the variable changes later, the closure sees the new value when called."

```python
# Classic trap in a loop:
functions = []
for i in range(5):
    def f():
        return i        # binds to variable 'i', not its current value
    functions.append(f)

# After loop, i = 4
print(functions[0]())    # 4   ← expected 0!
print(functions[1]())    # 4   ← expected 1!
print(functions[4]())    # 4   ← only this is "correct"
```

> "All 5 functions reference the same `i` variable. When called after the loop, `i` is 4."

**The fix:**
```python
# Fix 1 — default argument (captures value at definition time):
functions = [lambda i=i: i for i in range(5)]

# Fix 2 — factory function:
def make_func(val):
    def f():
        return val     # val is a new variable for each call to make_func
    return f

functions = [make_func(i) for i in range(5)]

print(functions[0]())    # 0  ✓
print(functions[1]())    # 1  ✓
```

---

## 1️⃣2️⃣ What is a decorator and how does it work internally?

**Strong answer:**
> "A decorator is a function that takes another function as input, wraps it with additional behavior, and returns the new function.
> The `@name` syntax is pure syntactic sugar — `@timer` before a function is exactly `function = timer(function)`.
> Internally, a decorator works because functions are first-class objects."

```python
import time
from functools import wraps

def timer(func):          # receives the function to wrap
    @wraps(func)          # preserves __name__, __doc__
    def wrapper(*args, **kwargs):   # *args/**kwargs to match any signature
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time()-start:.4f}s")
        return result     # must return the original result!
    return wrapper        # returns the new behavior

@timer
def slow_function():
    time.sleep(0.1)

# Equivalent to: slow_function = timer(slow_function)
slow_function()    # slow_function took 0.1001s
```

**Follow-up:** *"Why do you need `@wraps(func)`?"*
> "Without `@wraps`, the decorator replaces the function's `__name__` and `__doc__` with the wrapper's. Debugging becomes confusing because function names show as 'wrapper' everywhere — in tracebacks, logs, and introspection."

---

## 1️⃣3️⃣ What are keyword-only arguments? Why would you use them?

**Strong answer:**
> "Keyword-only arguments are parameters that MUST be passed by name — you cannot pass them positionally.
> You create them by placing a bare `*` before them in the signature.
> They're used to force callers to be explicit about what they're passing — especially for boolean or similar flags where position would be ambiguous."

```python
def connect(host, port, *, timeout=30, secure=False):
    ...

# ✓ Clear:
connect("localhost", 8080, timeout=60, secure=True)

# ✗ Ambiguous and rejected:
connect("localhost", 8080, 60, True)   # TypeError!

# Which is better to read in code review?
# Option 1: connect("db", 5432, 30, True, False)  ← what are these?
# Option 2: connect("db", 5432, timeout=30, secure=True)  ← crystal clear
```

---

## 1️⃣4️⃣ How does `*args` unpacking work when calling a function?

**Strong answer:**
> "The `*` operator can both collect (in a definition) and unpack (at a call site).
> When used in a function call, it unpacks an iterable into separate positional arguments."

```python
def add(a, b, c):
    return a + b + c

nums = [1, 2, 3]
add(*nums)          # same as add(1, 2, 3)  → 6

# ** unpacks a dict into keyword arguments:
def greet(name, greeting):
    return f"{greeting}, {name}!"

data = {"name": "Alice", "greeting": "Hello"}
greet(**data)       # same as greet(name="Alice", greeting="Hello")
```

---

# 🔵 Level 3 — 5+ Years

---

## 1️⃣5️⃣ How are functions stored in memory?

**Strong answer:**
> "Functions are objects stored in heap memory, just like any other Python object.
> The function object contains: compiled bytecode, the function's name, default argument values, type annotations, the `__closure__` tuple (if it's a closure), and a reference to its global namespace.
> When called, a new execution frame is pushed onto the call stack in stack memory.
> This frame contains local variables and a reference back to the function object.
> When the function returns, the frame is popped and destroyed."

```python
def greet(name):
    """Says hello."""
    return f"Hello, {name}"

# The function object on the heap:
print(greet.__code__)           # compiled bytecode object
print(greet.__name__)           # 'greet'
print(greet.__doc__)            # 'Says hello.'
print(greet.__globals__)        # reference to module's global namespace
print(greet.__annotations__)    # {}
print(greet.__defaults__)       # None (no defaults)
```

---

## 1️⃣6️⃣ What is a pure function and why does it matter in production?

**Strong answer:**
> "A pure function always returns the same output for the same input and has no side effects.
> In production, pure functions are valuable because:
> they're trivially unit-testable (no mocking needed),
> they're safe to cache with memoization,
> they're parallelizable without race conditions,
> and they're predictable — no 'action at a distance' bugs."

```python
# Pure:
def add(a, b):
    return a + b     # always a+b, no side effects

# Impure — depends on external state:
discount = 0.1
def calculate_price(amount):
    return amount * (1 - discount)    # depends on global!

# Impure — modifies external state:
history = []
def record(value):
    history.append(value)   # side effect!
    return value
```

---

## 1️⃣7️⃣ Explain `functools.lru_cache` — how it works and when to use it.

**Strong answer:**
> "`lru_cache` is a decorator that memoizes function results.
> LRU stands for Least Recently Used — when the cache is full, the oldest unused entries are discarded.
> It works by using the function's arguments as a cache key (stored in a dict internally).
> It requires that ALL arguments be hashable.
> Use it when a function is pure, called repeatedly with the same arguments, and computationally expensive."

```python
from functools import lru_cache

@lru_cache(maxsize=128)    # cache up to 128 unique argument combinations
def expensive_query(user_id: int):
    # simulate DB query
    return f"User {user_id} data"

expensive_query(42)    # runs the query
expensive_query(42)    # returns cached result instantly!
expensive_query(43)    # new query for different arg

# Inspect cache performance:
print(expensive_query.cache_info())
# CacheInfo(hits=1, misses=2, maxsize=128, currsize=2)

# Clear cache:
expensive_query.cache_clear()

# ⚠️ lru_cache requires hashable args:
@lru_cache
def process(data: list):   # ← TypeError! Lists are not hashable
    ...

# Fix — use tuple:
process(tuple(data))
```

---

## 1️⃣8️⃣ What is the difference between a generator function and a regular function?

**Strong answer:**
> "A regular function runs to completion and returns all data at once.
> A generator function uses `yield` to pause execution and produce values one at a time.
> Each call to `next()` resumes from where it left off.
> This makes generators ideal for large datasets — they use O(1) memory instead of O(n)."

```python
# Regular — loads everything into memory:
def get_squares(n):
    return [x**2 for x in range(n)]   # list of n items in memory

# Generator — one value at a time:
def gen_squares(n):
    for x in range(n):
        yield x**2    # pause here, resume later

import sys
regular = get_squares(1_000_000)
gen     = gen_squares(1_000_000)

print(sys.getsizeof(regular))    # ~8,000,056 bytes
print(sys.getsizeof(gen))        # 200 bytes
```

---

## 1️⃣9️⃣ How do decorators with arguments work internally?

**Strong answer:**
> "A decorator with arguments needs three layers instead of two.
> The outermost function receives the decorator arguments and returns the actual decorator.
> The middle function receives the target function.
> The innermost wrapper runs on each call.
> `@decorator(arg)` is equivalent to `func = decorator(arg)(func)`."

```python
from functools import wraps

def repeat(times):                    # layer 1: receives decorator argument
    def decorator(func):              # layer 2: receives function
        @wraps(func)
        def wrapper(*args, **kwargs): # layer 3: runs on each call
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def say_hi():
    print("Hi!")

# Equivalent to: say_hi = repeat(3)(say_hi)
say_hi()    # prints "Hi!" three times
```

---

## 2️⃣0️⃣ What is the difference between shallow and deep function design?

**Strong answer:**
> "A shallow understanding treats functions as just syntax — define, call, done.
> A deep understanding means knowing:
> how the call stack works (so you can reason about recursion depth and stack overflows),
> how closures capture state (so you avoid the late binding trap),
> how scope works (so you know exactly which variable Python resolves to),
> how default arguments are evaluated once (to avoid the mutable default trap),
> and how decorators preserve or lose metadata (so logs and tracebacks are useful).
> Interviewers can tell the difference within two questions."

---

# 🔴 Scenario-Based Questions

---

## Scenario 1: Unexpected Shared State

```python
def append_to(value, to=[]):
    to.append(value)
    return to

print(append_to(1))    # ?
print(append_to(2))    # ?
print(append_to(3))    # ?
```

**Answer expected:**
> "`[1]`, `[1, 2]`, `[1, 2, 3]` — because `[]` is created once and shared across calls.
> Fix: use `to=None` and create `[]` inside the function."

---

## Scenario 2: Closure in a Loop

```python
adders = [lambda x: x + i for i in range(5)]
print(adders[0](10))    # ?
print(adders[3](10))    # ?
```

**Answer expected:**
> "Both print `14`. All lambdas share the same `i` variable.
> After the loop, `i = 4`. So `x + i = 10 + 4 = 14` for all of them.
> Fix: `lambda x, i=i: x + i` to capture the value."

---

## Scenario 3: Decorator Loses Metadata

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def calculate():
    """Important calculation."""
    pass

print(calculate.__name__)    # ?
print(calculate.__doc__)     # ?
```

**Answer expected:**
> "`'wrapper'` and `None`. The decorator replaced the function with `wrapper` without preserving metadata.
> Fix: add `@wraps(func)` from `functools` to the wrapper."

---

## Scenario 4: Recursion Depth

```python
def countdown(n):
    return countdown(n-1)

countdown(10000)    # What happens?
```

**Answer expected:**
> "`RecursionError: maximum recursion depth exceeded`.
> Python's default limit is 1000 frames.
> This function has no base case — it recurses forever.
> Fix: add `if n <= 0: return 0` as the base case."

---

## Scenario 5: `global` Trap

```python
x = 10

def modify():
    x += 1       # What happens?
    return x

modify()
```

**Answer expected:**
> "`UnboundLocalError: local variable 'x' referenced before assignment`.
> Python sees the assignment `x += 1` (which is `x = x + 1`) and classifies `x` as local.
> Then it tries to read the local `x` before it's assigned — error!
> Fix: add `global x` inside the function."

---

# 🔥 Common Candidate Mistakes in Interviews

```
┌────────────────────────────────────────────────────────────────────────┐
│  MISTAKE                              HOW TO AVOID IT                  │
├────────────────────────────────────────────────────────────────────────┤
│  Mutable default argument             Always use None + create inside   │
│  Confusing func vs func()             No parens = object, parens = call │
│  Not using @wraps                     Always wrap with @wraps(func)     │
│  Late binding in closures             Use default arg trick: i=i        │
│  Using global when you shouldn't      Pass values in/out explicitly     │
│  No base case in recursion            Always define the stop condition  │
│  Using == None instead of is None     Use `if x is None`               │
│  Forgetting return in decorator       Must return result from wrapper   │
│  Not knowing *args is a tuple         args is ALWAYS a tuple inside     │
│  Not knowing **kwargs is a dict       kwargs is ALWAYS a dict inside    │
└────────────────────────────────────────────────────────────────────────┘
```

---

# ⚡ Rapid-Fire Revision

```
• def creates a function object in memory — nothing runs yet
• Parameters = definition placeholders; Arguments = call values
• return sends value + exits; no return → implicit None
• *args → tuple inside function; **kwargs → dict inside function
• LEGB: Local → Enclosing → Global → Built-in
• global to modify module-level; nonlocal to modify outer function's variable
• Functions are objects: store, pass, return like any value
• func = reference to object; func() = call it
• lambda = anonymous one-liner, auto-returns expression
• Closure = inner function + captured outer variables
• Late binding: closures see current value, not value at creation
• Late binding fix: default arg trick (i=i in lambda)
• @decorator == func = decorator(func)
• @wraps(func) — ALWAYS use it to preserve metadata
• Mutable default trap — ALWAYS use None instead
• Recursion needs a base case or it will crash
• Generator yield pauses and resumes; memory = O(1)
• lru_cache memoizes results; requires hashable args
• Pure function = same input → same output, no side effects
```

---

# 🏆 Final Interview Mindset

```
When asked about functions, the signal interviewers look for:

BEGINNER signals:    "A function is a reusable block of code."
INTERMEDIATE signal: Explains *args, scope, closures with examples.
SENIOR signal:       Talks about memory frames, explains gotchas unprompted,
                     connects concepts (closures → decorators → frameworks).

The difference between a ₹6LPA offer and a ₹18LPA offer is often
just this depth of explanation on fundamentals.

Functions are asked in every Python interview.
Know them like you know your own name.
```

---

# 🔁 Navigation

| | |
|---|---|
| ⬅️ Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 💻 Practice | [practice.py](./practice.py) |
| ➡️ Next Topic | [05 — OOP](../05_oops/theory.md) |
