# 💻 Practice — 10_decorators

> Master file — covers all 16 chapters at survey depth.
> For deep dives: [Class Decorators →](./01_class_decorators/practice.md) · [Production Patterns →](./02_production_patterns/practice.md)

---

## Quick Index

| # | Difficulty | Topic | Skill |
|---|---|---|---|
| [Q1](#q1) | 🟢 Easy | First-class functions | Pass and return functions |
| [Q2](#q2) | 🟢 Easy | Closures | make_counter() + captured variable |
| [Q3](#q3) | 🟢 Easy | Manual decorator | Write decorator manually |
| [Q4](#q4) | 🟢 Easy | @ syntax | Convert manual → @ sugar |
| [Q5](#q5) | 🟢 Easy | functools.wraps | Broken vs fixed identity |
| [Q6](#q6) | 🟡 Medium | Decorator factory | @repeat(n) |
| [Q7](#q7) | 🟡 Medium | Class decorator | CallCounter with __init__ + __call__ |
| [Q8](#q8) | 🟡 Medium | Decorating classes | @singleton class decorator |
| [Q9](#q9) | 🟡 Medium | @property | Getter + setter + validation |
| [Q10](#q10) | 🟢 Easy | @classmethod / @staticmethod | When to use each |
| [Q11](#q11) | 🟡 Medium | Stacking | @timer + @retry order and execution |
| [Q12](#q12) | 🟡 Medium | Production: timing | @timer with logging |
| [Q13](#q13) | 🟡 Medium | Production: retry | @retry(max_attempts=3) |
| [Q14](#q14) | 🟡 Medium | Async decorator | Works on sync + async |
| [Q15](#q15) | 🟡 Medium | Optional arguments | @validate works both ways |
| [Q16](#q16) | 🟡 Medium | Introspection | inspect.unwrap() |
| [Q17](#q17) | 🟠 Hard | Anti-patterns | Fix missing return + missing @wraps |
| [Q18](#q18) | 🟡 Medium | @lru_cache | Fibonacci benchmark |
| [Q19](#q19) | 🟡 Medium | @cached_property | Expensive computed attribute |
| [Q20](#q20) | 🟡 Medium | @singledispatch | format_value() by type |
| [Q21](#q21) | 🟠 Hard | Full mental model | Trace import vs call time |
| [Q22](#q22) | 🟠 Hard | Circuit breaker | Concept + when to use |
| [Q23](#q23) | 🟠 Hard | Capstone | @require_auth(roles=["admin"]) |

---

<a id="q1"></a>

### Q1 🟢 · first-class functions — Pass and Return Functions

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)



**Problem:** Write a function `apply_twice(func, value)` that calls `func(value)` twice, feeding the output of the first call into the second. Then write a second function `make_adder(n)` that returns a function which adds `n` to its argument. Demonstrate both.

<details>
<summary>💡 Hint</summary>

`apply_twice` just calls `func(func(value))`. `make_adder` defines and returns an inner function — the returned function is an object, not a call result.
</details>

<details>
<summary>✅ Answer</summary>

```python
def apply_twice(func, value):
    return func(func(value))

def make_adder(n):
    def adder(x):
        return x + n
    return adder   # return the function object, not adder()

add5 = make_adder(5)
print(apply_twice(add5, 10))   # 20 → add5(10)=15, add5(15)=20

# Functions are objects — you can store them, pass them, return them
print(type(add5))              # <class 'function'>
print(apply_twice(str.upper, "hello"))  # TypeError — str.upper returns a str
# apply_twice works on any callable
```

**Why:** In Python, functions are first-class objects — they have a type, can be assigned to variables, passed as arguments, and returned from other functions. This is the foundation that makes decorators possible.
</details>

---

<a id="q2"></a>

### Q2 🟢 · closures — Write make_counter() and explain captured variables

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)



**Problem:** Write `make_counter()` that returns a counter function. Each call to the returned function should increment and return a count starting at 1. Create two independent counters `c1` and `c2` and show they do not share state. Then inspect `c1.__closure__` to see where the count lives.

<details>
<summary>💡 Hint</summary>

Use `nonlocal count` inside the inner function so it modifies the outer scope's variable rather than creating a new local one. Each call to `make_counter()` creates a fresh scope with its own `count` variable.
</details>

<details>
<summary>✅ Answer</summary>

```python
def make_counter():
    count = 0                    # lives in a "cell object" on the heap

    def counter():
        nonlocal count           # modify the cell, not a new local
        count += 1
        return count

    return counter

c1 = make_counter()
c2 = make_counter()

print(c1())   # 1
print(c1())   # 2
print(c1())   # 3
print(c2())   # 1  — c2 has its OWN count cell, independent of c1

# Inspect the closure:
print(c1.__closure__)                        # (<cell at 0x...>,)
print(c1.__closure__[0].cell_contents)       # 3
```

**Why:** A closure is a function that "closes over" variables from its enclosing scope. Python keeps those variables alive in a `cell` object on the heap even after `make_counter()` returns. Each call to `make_counter()` creates a brand-new cell — that's why `c1` and `c2` have independent state. `nonlocal` tells Python to write to the existing cell rather than creating a shadowing local.
</details>

---

<a id="q3"></a>

### Q3 🟢 · manual decorator — Write the manual form from scratch

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)



**Problem:** Write a decorator `shout` that uppercases the string returned by any decorated function. Apply it to `greet(name)` using the **manual form** — no `@` syntax. Show the memory model comment.

<details>
<summary>💡 Hint</summary>

The pattern: `def shout(func): def wrapper(*args, **kwargs): result = func(*args, **kwargs); return result.upper(); return wrapper`. Then `greet = shout(greet)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import functools

def shout(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)    # call the original
        return result.upper()             # add behavior
    return wrapper                        # return the wrapper, NOT wrapper()

def greet(name):
    return f"Hello, {name}!"

# Manual application — this is EXACTLY what @shout does:
greet = shout(greet)

print(greet("alice"))    # "HELLO, ALICE!"
print(greet.__name__)    # "greet" — preserved by @wraps

# Memory model:
# Before:  greet ──→ <function greet at 0x100>
# After:   greet ──→ <function wrapper at 0x200>
#                        └── closure: func ──→ <function greet at 0x100>
```

**Why:** A decorator is just a function that takes a function, wraps it, and returns the new version. `greet = shout(greet)` is the desugared form — it rebinds the name `greet` to the wrapper. The original function object still exists, captured in the wrapper's closure.
</details>

---

<a id="q4"></a>

### Q4 🟢 · @ syntax — Convert manual form to @ syntax

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)



**Problem:** Take the `shout` decorator from Q3. Rewrite the application using `@` syntax. Then demonstrate that `@decorator` runs **at definition time** (import time), not at call time, by printing inside the decorator's outer body.

<details>
<summary>💡 Hint</summary>

`@shout` placed above `def greet` is 100% identical to writing `greet = shout(greet)` after. To prove it runs at definition time, add a `print` in the `shout` function itself (not inside `wrapper`).
</details>

<details>
<summary>✅ Answer</summary>

```python
import functools

def shout(func):
    print(f"  [shout] wrapping {func.__name__}")   # runs at definition time
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"  [shout] calling {func.__name__}") # runs at call time
        return func(*args, **kwargs).upper()
    return wrapper

print("--- defining greet ---")

@shout                       # equivalent to: greet = shout(greet)
def greet(name):
    return f"Hello, {name}!"

print("--- calling greet ---")
print(greet("alice"))

# Output:
# --- defining greet ---
#   [shout] wrapping greet        ← runs at DEFINITION TIME (when module loads)
# --- calling greet ---
#   [shout] calling greet         ← runs at CALL TIME
# HELLO, ALICE!
```

**Why:** The `@` line is syntactic sugar evaluated when Python parses the `def` statement. The decorator factory/outer body executes once at import time; only the wrapper body runs each time the function is called. This distinction matters for decorators that do expensive work in their outer body.
</details>

---

<a id="q5"></a>

### Q5 🟢 · functools.wraps — Show what breaks without @wraps, fix it

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)



**Problem:** Write a `timer` decorator WITHOUT `@functools.wraps`. Apply it to `process()`. Show that `__name__` and `__doc__` are wrong. Then fix it by adding `@functools.wraps(func)` and show the corrected output, including `__wrapped__`.

<details>
<summary>💡 Hint</summary>

Without `@wraps`, `process.__name__` returns `'wrapper'` and `process.__doc__` returns `None`. `@functools.wraps(func)` copies `__name__`, `__doc__`, `__module__`, `__qualname__`, `__annotations__`, and also sets `__wrapped__` on the wrapper.
</details>

<details>
<summary>✅ Answer</summary>

```python
import functools, time

# ❌ BROKEN — missing @wraps:
def timer_broken(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"Elapsed: {time.perf_counter() - start:.4f}s")
        return result
    return wrapper

@timer_broken
def process():
    """Process the data."""
    time.sleep(0.01)

print(process.__name__)   # 'wrapper'   ← WRONG
print(process.__doc__)    # None        ← WRONG

# ✅ FIXED — with @wraps:
def timer(func):
    @functools.wraps(func)          # copies __name__, __doc__, sets __wrapped__
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"Elapsed: {time.perf_counter() - start:.4f}s")
        return result
    return wrapper

@timer
def process():
    """Process the data."""
    time.sleep(0.01)

print(process.__name__)     # 'process'        ← correct
print(process.__doc__)      # 'Process the data.'  ← correct
print(process.__wrapped__)  # <function process> ← original function
```

**Why:** Without `@wraps`, your wrapper masquerades as itself — logs show `wrapper`, `help()` shows nothing, and `inspect.signature` gives the wrapper's signature. `@functools.wraps(func)` is a one-line fix that preserves the full identity of the original function. The `__wrapped__` attribute it adds lets tools like pytest and IDEs see through the decoration.
</details>

---

<a id="q6"></a>

### Q6 🟡 · decorator factory — Write @repeat(n)

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)



**Problem:** Write a `@repeat(n)` decorator factory that calls the decorated function `n` times. The wrapper should collect all return values into a list and return it. Show the three-layer structure in a comment.

<details>
<summary>💡 Hint</summary>

You need three layers: `repeat(n)` returns `decorator`, `decorator(func)` returns `wrapper`, `wrapper(*args, **kwargs)` runs each time. The key insight: `repeat(n)` is called first, and its job is to capture `n` and return a real decorator.
</details>

<details>
<summary>✅ Answer</summary>

```python
import functools

def repeat(n):
    """
    Three-layer structure:
    repeat(n)              ← LEVEL 1: factory — takes config, returns decorator
      decorator(func)      ← LEVEL 2: decorator — takes function, returns wrapper
        wrapper(*a, **kw)  ← LEVEL 3: wrapper — runs each time the function is called
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(n):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    return f"Hello, {name}!"

print(greet("Alice"))
# ['Hello, Alice!', 'Hello, Alice!', 'Hello, Alice!']

# Call chain at decoration time:
# repeat(3) → returns decorator
# decorator(greet) → returns wrapper
# greet is now wrapper (with greet's identity via @wraps)
```

**Why:** When you need to pass arguments to a decorator, you add an outer layer — a factory — that captures those arguments and returns a proper decorator. The three-layer pattern (`factory → decorator → wrapper`) is the standard Python decorator factory shape. Each layer has a single responsibility.
</details>

---

<a id="q7"></a>

### Q7 🟡 · class decorator — Build CallCounter with __init__ + __call__

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)



**Problem:** Implement a `CallCounter` class-based decorator. It should track how many times the decorated function has been called and expose that count via a `.calls` attribute. Use `functools.update_wrapper` to preserve the original function's identity. Show `@CallCounter` without parentheses.

<details>
<summary>💡 Hint</summary>

When used without parentheses (`@CallCounter`), `__init__` receives the function directly. Use `functools.update_wrapper(self, func)` instead of `@functools.wraps` since you're inside a class. State goes on `self`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import functools

class CallCounter:
    def __init__(self, func):
        functools.update_wrapper(self, func)   # copies __name__, __doc__, etc.
        self.func = func
        self.calls = 0                          # state lives on the instance

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)

@CallCounter   # no parentheses — __init__ receives greet directly
def greet(name):
    """Greet someone."""
    return f"Hello, {name}!"

greet("Alice")
greet("Bob")
greet("Charlie")

print(greet.calls)     # 3
print(greet.__name__)  # 'greet' — preserved by update_wrapper
print(greet.__doc__)   # 'Greet someone.'
```

**Why:** Class-based decorators are ideal when the decorator needs to maintain state across calls — the state lives naturally on `self`. `__init__` runs at decoration time (captures the function), `__call__` runs each time the decorated function is invoked. `functools.update_wrapper(self, func)` is the class equivalent of `@functools.wraps`.
</details>

---

<a id="q8"></a>

### Q8 🟡 · decorating classes — Write a @singleton class decorator

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)



**Problem:** Write a `@singleton` decorator that can be applied to a **class** to ensure only one instance ever exists. Calling the class a second time should return the cached instance, not create a new one. Prove it works with `is`.

<details>
<summary>💡 Hint</summary>

A class decorator takes a class as its argument and returns something callable. Use a `dict` to store instances keyed by class. `@functools.wraps(cls)` preserves `cls.__name__` and `cls.__doc__` on the returned function.
</details>

<details>
<summary>✅ Answer</summary>

```python
import functools

def singleton(cls):
    instances = {}               # shared across all calls to the returned function

    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)   # create once
        return instances[cls]                        # always return cached

    return get_instance

@singleton
class DatabaseConnection:
    def __init__(self, url):
        self.url = url
        print(f"Connecting to {url}")   # should print only once

db1 = DatabaseConnection("postgres://localhost/mydb")
# "Connecting to postgres://localhost/mydb"

db2 = DatabaseConnection("postgres://localhost/mydb")
# (no output — returns cached instance)

print(db1 is db2)    # True — same object
print(id(db1) == id(db2))  # True
```

**Why:** Class decorators follow the same pattern as function decorators — take the target, wrap behavior around instantiation, return the new callable. The `instances` dict acts as the registry, persisting across all calls because it lives in the closure. This is the classic Singleton pattern implemented cleanly with a decorator.
</details>

---

<a id="q9"></a>

### Q9 🟡 · @property — Convert attribute to property with validation

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)



**Problem:** Write a `BankAccount` class with a `balance` attribute. Convert `balance` to a `@property` with: a getter that returns the balance, a setter that raises `ValueError` if the new balance is negative, and a read-only `status` computed property that returns `"positive"`, `"zero"`, or `"overdrawn"` depending on the balance.

<details>
<summary>💡 Hint</summary>

Store the real value in `self._balance`. The getter is decorated with `@property`. The setter is decorated with `@balance.setter`. No setter on `status` makes it read-only — assignment will raise `AttributeError`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class BankAccount:
    def __init__(self, initial_balance: float = 0.0):
        self._balance = initial_balance   # private backing field

    @property
    def balance(self) -> float:           # read as: account.balance
        return self._balance

    @balance.setter
    def balance(self, value: float):      # write as: account.balance = 100
        if value < 0:
            raise ValueError(f"Balance cannot be negative: {value}")
        self._balance = value

    @property
    def status(self) -> str:              # read-only — no setter
        if self._balance > 0:
            return "positive"
        elif self._balance == 0:
            return "zero"
        return "overdrawn"                # unreachable via setter, but possible via _balance

account = BankAccount(100.0)
print(account.balance)   # 100.0
print(account.status)    # 'positive'

account.balance = 0
print(account.status)    # 'zero'

try:
    account.balance = -50
except ValueError as e:
    print(e)             # Balance cannot be negative: -50

# account.status = "something"  →  AttributeError (no setter)
```

**Why:** `@property` lets you expose attributes with a clean `obj.attr` interface while hiding validation logic behind the scenes. The setter pattern enforces invariants at assignment time rather than requiring separate `set_balance()` method calls. Read-only computed properties (no setter) give you derived values that stay in sync automatically.
</details>

---

<a id="q10"></a>

### Q10 🟢 · @classmethod / @staticmethod — Write both and explain when to use each

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)



**Problem:** Write an `Order` class with: a regular `__init__`, a `@classmethod from_dict(cls, data)` that constructs an Order from a dictionary, and a `@staticmethod is_valid_status(status)` that returns True/False without needing the class or instance. Show all three in a table comment explaining when to use each.

<details>
<summary>💡 Hint</summary>

`@classmethod` receives `cls` as its first parameter — use it when you need to call `cls(...)` to create an instance (alternative constructor). `@staticmethod` receives no implicit argument — use it for pure utility functions that happen to live on the class namespace.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Order:
    VALID_STATUSES = {"pending", "processing", "shipped", "delivered", "cancelled"}

    def __init__(self, order_id: int, total: float, status: str = "pending"):
        self.order_id = order_id
        self.total = total
        self.status = status

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        """Alternative constructor — receives cls so it works in subclasses too."""
        return cls(
            order_id=data["id"],
            total=data["total"],
            status=data.get("status", "pending"),
        )

    @staticmethod
    def is_valid_status(status: str) -> bool:
        """Pure utility — doesn't need self or cls."""
        return status in Order.VALID_STATUSES

    def __repr__(self):
        return f"Order(id={self.order_id}, total={self.total}, status={self.status})"

# Usage:
o1 = Order(1, 99.99)
o2 = Order.from_dict({"id": 2, "total": 49.99, "status": "shipped"})
print(o1)                              # Order(id=1, total=99.99, status=pending)
print(o2)                              # Order(id=2, total=49.99, status=shipped)
print(Order.is_valid_status("shipped")) # True
print(Order.is_valid_status("lost"))    # False

# When to use each:
# ─────────────────────────────────────────────────────────────────
# Regular method   → needs instance state (self.total, self.status)
# @classmethod     → needs class itself (alternative constructors, factory methods)
# @staticmethod    → pure utility that logically belongs to the class namespace
```

**Why:** `@classmethod` is the standard Python pattern for alternative constructors (e.g. `datetime.fromtimestamp()`). It's subclass-safe because `cls` refers to the subclass when called on a subclass. `@staticmethod` avoids the overhead of passing `self`/`cls` and signals clearly: "this function has no side effects on the object."
</details>

---

<a id="q11"></a>

### Q11 🟡 · stacking — Stack @timer and @retry, predict order

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)



**Problem:** Write minimal `timer` and `retry` decorators. Stack them as `@timer` over `@retry(3)` on a `fetch_data` function. Draw the wrapper nesting in a comment. Then describe exactly what happens when `fetch_data()` is called: which layer runs first, which runs last.

<details>
<summary>💡 Hint</summary>

Decorators are applied bottom-up: `@retry(3)` wraps `fetch_data` first, then `@timer` wraps that result. At call time it's the reverse: `timer`'s wrapper runs first (outermost), eventually reaching `retry`'s wrapper, then the original function.
</details>

<details>
<summary>✅ Answer</summary>

```python
import functools, time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[timer] start")
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"[timer] {func.__name__} took {time.perf_counter() - start:.4f}s")
        return result
    return wrapper

def retry(max_attempts):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    print(f"[retry] attempt {attempt}/{max_attempts}")
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"[retry] failed: {e}")
        return wrapper
    return decorator

# Application order (bottom-up):
#   step 1: retry(3)(fetch_data)   → retry_wrapper
#   step 2: timer(retry_wrapper)   → timer_wrapper
#   fetch_data now points to:  timer_wrapper
#                                 └── retry_wrapper
#                                       └── original fetch_data

@timer
@retry(3)
def fetch_data(url):
    return f"data from {url}"

fetch_data("https://api.example.com")
# [timer] start
# [retry] attempt 1/3
# [timer] fetch_data took 0.0001s

# Call order: timer's before-code → retry's logic → original → retry's after → timer's after
```

**Why:** The rule is "applied bottom-up, executed top-down." The decorator closest to `def` wraps the original first — it becomes the inner layer. `@timer` sits outermost, so it starts and ends the overall call. This matters for correctness: `@timer` measuring `@retry` means you time the full retry budget, not just one attempt.
</details>

---

<a id="q12"></a>

### Q12 🟡 · production patterns — Write @timer with logging

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)



**Problem:** Write a production-grade `@timed` decorator that uses the `logging` module (not `print`) to log execution time. Use `time.perf_counter()` for accuracy. The log message should include the function name and elapsed time in seconds with 3 decimal places. Use `try/finally` so timing is recorded even if the function raises.

<details>
<summary>💡 Hint</summary>

Use `logging.getLogger(__name__)` outside the decorator. The `try/finally` block ensures `elapsed` is always logged — put the start time capture before `try`, and the `logger.info` call inside `finally`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import functools
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            logger.info("%s completed in %.3fs", func.__name__, elapsed)
    return wrapper

@timed
def process_records(records):
    """Simulate some work."""
    time.sleep(0.05)
    return [r.upper() for r in records]

result = process_records(["alpha", "beta", "gamma"])
print(result)
# INFO __main__: process_records completed in 0.051s
# ['ALPHA', 'BETA', 'GAMMA']

# Even if the function raises, timing is still logged:
@timed
def failing_op():
    time.sleep(0.02)
    raise RuntimeError("something went wrong")

try:
    failing_op()
except RuntimeError:
    pass
# INFO __main__: failing_op completed in 0.021s
```

**Why:** `try/finally` guarantees the timing log fires whether the function succeeds or raises — a critical pattern in production observability. `time.perf_counter()` is the right clock for elapsed-time measurement (monotonic, high resolution). Using `logging` instead of `print` means the output level can be controlled by log config without changing decorator code.
</details>

---

<a id="q13"></a>

### Q13 🟡 · production patterns — Write @retry(max_attempts=3)

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)



**Problem:** Write a `@retry(max_attempts=3, delay=0.1, backoff=2.0, exceptions=(Exception,))` decorator factory. On each failure it should log a warning with the attempt number and wait time, then sleep before the next attempt. On the final failure it should re-raise. Show it working with a function that fails twice then succeeds.

<details>
<summary>💡 Hint</summary>

Use a `wait` variable that starts at `delay` and multiplies by `backoff` each loop. Re-raise on `attempt == max_attempts` instead of after the loop to preserve the original traceback. Use `logging.warning`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import functools, time, logging

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

def retry(max_attempts=3, delay=0.1, backoff=2.0, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise                     # re-raises original exception
                    logging.warning(
                        "%s attempt %d/%d failed: %s — retrying in %.2fs",
                        func.__name__, attempt, max_attempts, e, wait
                    )
                    time.sleep(wait)
                    wait *= backoff               # exponential backoff
        return wrapper
    return decorator

# Simulate a function that fails twice then succeeds:
_call_count = 0

@retry(max_attempts=3, delay=0.05, backoff=2.0, exceptions=(ConnectionError,))
def fetch_user(user_id: int):
    global _call_count
    _call_count += 1
    if _call_count < 3:
        raise ConnectionError(f"timeout on attempt {_call_count}")
    return {"id": user_id, "name": "Alice"}

result = fetch_user(42)
print(result)   # {'id': 42, 'name': 'Alice'}
# WARNING: fetch_user attempt 1/3 failed: timeout on attempt 1 — retrying in 0.05s
# WARNING: fetch_user attempt 2/3 failed: timeout on attempt 2 — retrying in 0.10s
```

**Why:** Exponential backoff (multiplying wait time each retry) prevents hammering a failing service. Catching specific `exceptions` avoids masking bugs — a `TypeError` should not be retried, only transient errors like `ConnectionError`. Re-raising on the final attempt preserves the original stack trace for debugging.
</details>

---

<a id="q14"></a>

### Q14 🟡 · async decorator — Works on both sync and async functions

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)



**Problem:** Write a `timed` decorator that works transparently on **both** synchronous and asynchronous functions. Use `asyncio.iscoroutinefunction(func)` to branch between an async wrapper and a sync wrapper. Demonstrate on one sync function and one async function.

<details>
<summary>💡 Hint</summary>

Check `asyncio.iscoroutinefunction(func)` inside the decorator body (before returning the wrapper). Return an `async def` wrapper for coroutines, a regular `def` wrapper for sync functions. Both wrappers should use `@functools.wraps(func)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import functools, asyncio, time

def timed(func):
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return await func(*args, **kwargs)
            finally:
                print(f"[async] {func.__name__} took {time.perf_counter() - start:.4f}s")
        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                print(f"[sync]  {func.__name__} took {time.perf_counter() - start:.4f}s")
        return sync_wrapper

@timed
def compute(n: int) -> int:
    return sum(range(n))

@timed
async def fetch(url: str) -> str:
    await asyncio.sleep(0.05)
    return f"response from {url}"

# Sync:
print(compute(1_000_000))
# [sync]  compute took 0.023s
# 499999500000

# Async:
async def main():
    result = await fetch("https://api.example.com")
    print(result)

asyncio.run(main())
# [async] fetch took 0.051s
# response from https://api.example.com
```

**Why:** A sync decorator applied to an async function returns a coroutine but never awaits it — the function appears to run but does nothing. The `iscoroutinefunction` branch ensures the wrapper type matches the wrapped function type, making the decorator universally applicable without the caller needing to know.
</details>

---

<a id="q15"></a>

### Q15 🟡 · optional arguments — Write @validate that works both ways

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)



**Problem:** Write a `@validate` decorator that can be used as both `@validate` (no parens) and `@validate(strict=True)` (with parens). When `strict=True`, raise `TypeError` if any argument is `None`. When `strict=False` (default), just print a warning.

<details>
<summary>💡 Hint</summary>

Use the `_func=None` trick: if `_func is not None`, the decorator was used without parentheses (Python passed the function as the first arg). If `_func is None`, it was called with arguments — return the decorator. Use a keyword-only argument (`*`) to force keyword-only usage.
</details>

<details>
<summary>✅ Answer</summary>

```python
import functools

def validate(_func=None, *, strict=False):
    """
    Supports:
      @validate                  — _func is the decorated function
      @validate()                — _func is None, strict=False
      @validate(strict=True)     — _func is None, strict=True
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            all_args = list(args) + list(kwargs.values())
            none_args = [i for i, a in enumerate(all_args) if a is None]
            if none_args:
                msg = f"{func.__name__}: argument(s) at position(s) {none_args} are None"
                if strict:
                    raise TypeError(msg)
                else:
                    print(f"WARNING: {msg}")
            return func(*args, **kwargs)
        return wrapper

    if _func is not None:
        # Used as @validate — _func IS the decorated function
        return decorator(_func)
    else:
        # Used as @validate() or @validate(strict=True) — return the decorator
        return decorator

@validate
def process(user_id, data):
    return f"processing {user_id}"

@validate(strict=True)
def create_order(user_id, item):
    return f"order for {user_id}"

process(None, "data")          # WARNING: process: argument(s) at position(s) [0] are None
process(1, "data")             # OK

try:
    create_order(None, "item")
except TypeError as e:
    print(f"TypeError: {e}")   # TypeError: create_order: argument(s) at position(s) [0] are None
```

**Why:** The `_func=None` pattern is the canonical Python trick for optional-argument decorators. The `*` forces `strict` to be keyword-only, preventing `@validate(True)` positional confusion. This is the same pattern used by `functools.lru_cache` in Python 3.8+ (which also works as both `@lru_cache` and `@lru_cache(maxsize=128)`).
</details>

---

<a id="q16"></a>

### Q16 🟡 · introspection — Use inspect.unwrap() to reach the original

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)



**Problem:** Stack three decorators on a single function. Use `inspect.unwrap()` to retrieve the original undecorated function. Show that `__wrapped__` forms a chain you can follow manually, and that `inspect.unwrap()` traverses the entire chain automatically.

<details>
<summary>💡 Hint</summary>

Each `@functools.wraps(func)` call sets `wrapper.__wrapped__ = func`. So three stacked decorators create a chain: `outer.__wrapped__ → middle.__wrapped__ → original`. `inspect.unwrap()` follows this chain all the way to the end.
</details>

<details>
<summary>✅ Answer</summary>

```python
import functools, inspect

def decorator_a(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def decorator_b(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def decorator_c(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@decorator_a
@decorator_b
@decorator_c
def greet(name: str) -> str:
    """Greet by name."""
    return f"Hello, {name}!"

# The __wrapped__ chain:
print(greet.__name__)                    # 'greet' (copied by @wraps all the way)
print(greet.__wrapped__)                 # wrapper from decorator_b
print(greet.__wrapped__.__wrapped__)     # wrapper from decorator_c
print(greet.__wrapped__.__wrapped__.__wrapped__)  # original greet

# inspect.unwrap() traverses the full chain automatically:
original = inspect.unwrap(greet)
print(original)              # <function greet at 0x...>
print(original.__name__)     # 'greet'
print(original(name="Bob"))  # 'Hello, Bob!' — called directly, no wrappers
```

**Why:** `__wrapped__` is a pointer to the function one layer inward. `inspect.unwrap()` follows these pointers until there are no more — giving you the raw original function. This is how pytest reaches your actual test function body, and how IDEs show you the real signature instead of `*args, **kwargs`.
</details>

---

<a id="q17"></a>

### Q17 🟠 · anti-patterns — Fix a broken decorator

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)



**Problem:** The decorator below has two bugs. Identify both, explain what each breaks, and write the corrected version.

```python
def logger_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        func(*args, **kwargs)    # bug 1
    return wrapper               # bug 2 is elsewhere — look at the whole decorator
```

<details>
<summary>💡 Hint</summary>

Bug 1: the return value is swallowed. Bug 2: `wrapper`'s identity (name, docstring) doesn't match `func` — `@functools.wraps` is missing.
</details>

<details>
<summary>✅ Answer</summary>

```python
import functools

# ❌ BROKEN — two bugs:
def logger_decorator_broken(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        func(*args, **kwargs)    # BUG 1: missing 'return' — swallows the return value
    return wrapper               # BUG 2: missing @functools.wraps — loses __name__, __doc__

@logger_decorator_broken
def add(a, b):
    """Add two numbers."""
    return a + b

print(add(2, 3))     # None  ← BUG 1: should be 5, but return value is swallowed
print(add.__name__)  # 'wrapper'  ← BUG 2: should be 'add'
print(add.__doc__)   # None       ← BUG 2: should be 'Add two numbers.'

# ✅ FIXED:
def logger_decorator(func):
    @functools.wraps(func)       # FIX 2: preserve identity
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)   # FIX 1: return the result
    return wrapper

@logger_decorator
def add(a, b):
    """Add two numbers."""
    return a + b

print(add(2, 3))     # 5
print(add.__name__)  # 'add'
print(add.__doc__)   # 'Add two numbers.'
```

**Why:** Missing `return` is the most common decorator bug — it silently converts your function into one that always returns `None`. It's invisible until a caller expects a real value. Missing `@wraps` is subtler but breaks help systems, logging, pytest introspection, and any tool that reads `__name__` or `__doc__`. Both are required in every production decorator.
</details>

---

<a id="q18"></a>

### Q18 🟡 · @lru_cache — Apply to recursive fibonacci, measure the difference

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)



**Problem:** Write a naive recursive `fibonacci_slow(n)` without caching. Write `fibonacci(n)` with `@functools.lru_cache(maxsize=128)`. Time both for `n=35` using `time.perf_counter()`. Then call `fibonacci.cache_info()` to inspect hits and misses, and `fibonacci.cache_clear()` to reset it.

<details>
<summary>💡 Hint</summary>

`lru_cache` memoizes based on arguments. For `fibonacci(35)`, the naive version makes ~29 million recursive calls; the cached version makes exactly 35 unique calls (one per distinct `n`). The cache stats show this directly.
</details>

<details>
<summary>✅ Answer</summary>

```python
import functools, time

def fibonacci_slow(n: int) -> int:
    """Naive recursion — exponential O(2^n) time."""
    if n < 2:
        return n
    return fibonacci_slow(n - 1) + fibonacci_slow(n - 2)

@functools.lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    """Cached recursion — O(n) time, O(n) space."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Benchmark:
start = time.perf_counter()
result_slow = fibonacci_slow(35)
slow_time = time.perf_counter() - start

start = time.perf_counter()
result_fast = fibonacci(35)
fast_time = time.perf_counter() - start

print(f"Result (slow): {result_slow} in {slow_time:.4f}s")
print(f"Result (fast): {result_fast} in {fast_time:.6f}s")
# Result (slow): 9227465 in ~2.5s
# Result (fast): 9227465 in 0.000020s  ← ~100,000x faster

# Inspect the cache:
info = fibonacci.cache_info()
print(info)
# CacheInfo(hits=33, misses=36, maxsize=128, currsize=36)

# Clear the cache:
fibonacci.cache_clear()
print(fibonacci.cache_info())
# CacheInfo(hits=0, misses=0, maxsize=128, currsize=0)
```

**Why:** `lru_cache` turns an exponential-time recursion into linear time by storing results for each unique argument. The LRU (Least Recently Used) eviction policy keeps the most recently needed results in memory. For an unbounded cache, use `@functools.cache` (Python 3.9+), which is identical to `lru_cache(maxsize=None)` with less overhead.
</details>

---

<a id="q19"></a>

### Q19 🟡 · @cached_property — Expensive computed attribute cached on instance

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)



**Problem:** Write a `Document` class that has a `content` attribute (a large string). Add a `@cached_property` called `word_count` that counts words by splitting the content. Show that it only computes once (add a `print` inside). Then inspect `instance.__dict__` to confirm the cached value is stored there directly.

<details>
<summary>💡 Hint</summary>

After the first access, `cached_property` stores the result in `instance.__dict__[property_name]`. Since instance `__dict__` lookup takes priority over non-data descriptors, subsequent accesses bypass the descriptor entirely — pure dict lookup.
</details>

<details>
<summary>✅ Answer</summary>

```python
from functools import cached_property

class Document:
    def __init__(self, content: str):
        self.content = content

    @cached_property
    def word_count(self) -> int:
        print("  [computing word_count]")   # should only print once
        return len(self.content.split())

    @cached_property
    def unique_words(self) -> set:
        print("  [computing unique_words]")
        return set(self.content.lower().split())

doc = Document("the quick brown fox jumps over the lazy dog")

print(doc.word_count)   # [computing word_count] → 9
print(doc.word_count)   # (no print) → 9   ← served from __dict__
print(doc.word_count)   # (no print) → 9

# Inspect: value is stored directly on the instance:
print(doc.__dict__)
# {'content': 'the quick brown...', 'word_count': 9, 'unique_words': ...}

print(doc.unique_words)  # [computing unique_words] → {'the', 'quick', ...}
print(doc.unique_words)  # (no print) → same set

# To invalidate: delete the attribute
del doc.word_count
print(doc.word_count)   # [computing word_count] → 9 (recomputes)
```

**Why:** `@cached_property` is ideal for expensive computations where the input (instance attributes) won't change — parsing, heavy math, DB-derived values. It's lazily evaluated (only computed on first access) and invalidatable (delete the attribute). The implementation is elegant: it writes to `instance.__dict__`, which Python checks before descriptors on non-data descriptors, making subsequent access a raw dict lookup with zero overhead.
</details>

---

<a id="q20"></a>

### Q20 🟡 · @singledispatch — Write format_value() that handles multiple types

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)



**Problem:** Write a `format_value(value)` function using `@functools.singledispatch` that handles: `int` (formats as `"integer: N"`), `str` (formats as `"text: 'S'"`), `list` (formats as `"list[N items]: [...]"`), and falls back to `"unknown: TYPE"` for any other type. Register `float` to use the same handler as `int`.

<details>
<summary>💡 Hint</summary>

The base `@singledispatch` function is the fallback. Register implementations with `@format_value.register(type)`. For registering the same handler for multiple types, stack the `.register` decorators. Use `type(value).__name__` in the fallback.
</details>

<details>
<summary>✅ Answer</summary>

```python
from functools import singledispatch

@singledispatch
def format_value(value) -> str:
    """Fallback for unregistered types."""
    return f"unknown: {type(value).__name__}"

@format_value.register(int)
@format_value.register(float)   # same handler for both numeric types
def _(value) -> str:
    return f"integer: {value}"

@format_value.register(str)
def _(value) -> str:
    return f"text: '{value}'"

@format_value.register(list)
def _(value) -> str:
    preview = str(value[:3])[:-1] + ("..." if len(value) > 3 else str(value[3:])[-1])
    return f"list[{len(value)} items]: {value}"

# Usage:
print(format_value(42))              # integer: 42
print(format_value(3.14))            # integer: 3.14
print(format_value("hello"))         # text: 'hello'
print(format_value([1, 2, 3, 4, 5])) # list[5 items]: [1, 2, 3, 4, 5]
print(format_value({"key": "val"}))  # unknown: dict
print(format_value(True))            # integer: True  ← bool is a subclass of int!

# Inspect registered implementations:
print(format_value.registry.keys())
# dict_keys([object, int, float, str, list])
```

**Why:** `singledispatch` is Python's approach to function overloading — one function name, multiple implementations dispatched by type. It's cleaner than a long `if isinstance(value, int)` chain and is extensible: third-party code can register new type handlers without modifying your function. Subclasses are handled via MRO — `bool` dispatches to `int`'s handler because `bool` inherits from `int`.
</details>

---

<a id="q21"></a>

### Q21 🟠 · full mental model — Trace what Python does when it sees @decorator

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)



**Problem:** Write a module that demonstrates the full execution timeline — what happens at **import time** versus **call time**. Include a decorator factory that prints when it runs each phase. Then write out the six-step execution order as a comment tracing each phase from module load to function call.

<details>
<summary>💡 Hint</summary>

At import time: (1) `def` statements create function objects (no body execution), (2) `@decorator` lines call the decorator, (3) class bodies execute. At call time: (4) the outermost wrapper runs, (5) calls through to the original, (6) results propagate back out.
</details>

<details>
<summary>✅ Answer</summary>

```python
import functools

# ── IMPORT TIME: this code runs when the module is first imported ──

print("[import] module loading")

def timer(func):
    print(f"[import]   timer: wrapping '{func.__name__}'")  # step 2
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[call]     timer: before '{func.__name__}'")  # step 4
        result = func(*args, **kwargs)
        print(f"[call]     timer: after  '{func.__name__}'")  # step 6
        return result
    return wrapper

def retry(n):
    print(f"[import]   retry({n}): factory called")         # step 1 (factory)
    def decorator(func):
        print(f"[import]   retry({n}): wrapping '{func.__name__}'") # step 2
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"[call]     retry({n}): running")        # step 5
            return func(*args, **kwargs)
        return wrapper
    return decorator

print("[import] defining fetch_data:")

@timer
@retry(3)
def fetch_data(url: str) -> str:
    print(f"[call]     fetch_data: executing")              # step 5 (innermost)
    return f"data from {url}"

print("[import] module loaded")
print()
print("[call] calling fetch_data:")
result = fetch_data("https://api.example.com")
print(f"[call] result: {result}")

# Full execution order:
# ─────────────────────────────────────────────────────────────
# IMPORT TIME:
#   1. retry(3)           — factory called, returns decorator
#   2. decorator(fetch_data) — innermost wrap, then timer(result)
#   2. timer(...)         — outermost wrap
#   fetch_data now → timer_wrapper → retry_wrapper → original
#
# CALL TIME (fetch_data("...")):
#   4. timer_wrapper starts  (outermost: before-code)
#   5. retry_wrapper runs
#   5. original fetch_data executes
#   6. results propagate: retry_wrapper → timer_wrapper → caller
```

**Why:** The import-time / call-time distinction is critical. Expensive operations in the factory body (like `retry(3)`) run once at import time — not per call. The wrapper body runs per call. Stacking means the last applied decorator is the outermost wrapper, and it runs first. Understanding this model lets you predict performance, debug unexpected execution order, and reason about state initialization.
</details>

---

<a id="q22"></a>

### Q22 🟠 · circuit breaker — Explain and sketch the concept

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)



**Problem:** Explain what a circuit breaker decorator does, what problem it solves, and sketch a minimal implementation outline (state machine with states: CLOSED, OPEN, HALF-OPEN). When would you use it over a `@retry` decorator?

> Survey depth — for full implementation see [02_production_patterns →](./02_production_patterns/practice.md)

<details>
<summary>💡 Hint</summary>

A circuit breaker is a state machine. CLOSED = normal operation. OPEN = fast-fail (skip the call entirely). HALF-OPEN = probe with one call to see if the downstream service recovered. Think about what triggers each transition.
</details>

<details>
<summary>✅ Answer</summary>

```python
import functools, time
from enum import Enum

class State(Enum):
    CLOSED    = "closed"     # normal — calls pass through
    OPEN      = "open"       # failing — calls fast-fail immediately
    HALF_OPEN = "half_open"  # recovering — one probe call allowed

# State machine transitions:
#
#  CLOSED ──[failures >= threshold]──→ OPEN
#  OPEN   ──[timeout elapsed]───────→ HALF_OPEN
#  HALF_OPEN ──[success]────────────→ CLOSED
#  HALF_OPEN ──[failure]────────────→ OPEN
#
#   ┌──────────┐   N failures    ┌──────┐
#   │  CLOSED  │ ─────────────→ │ OPEN │
#   │ (normal) │                 │(fail)│
#   └──────────┘                 └──────┘
#        ↑                           │
#     success                   timeout
#        │                           │
#   ┌──────────┐                     ▼
#   │HALF_OPEN │ ←─────────────── probe
#   └──────────┘

class circuit_breaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = State.CLOSED
        self.failure_count = 0
        self.last_failure_time = None

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == State.OPEN:
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = State.HALF_OPEN
                else:
                    raise RuntimeError(f"Circuit OPEN — {func.__name__} fast-failing")

            try:
                result = func(*args, **kwargs)
                # Success — reset
                self.failure_count = 0
                self.state = State.CLOSED
                return result
            except Exception:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    self.state = State.OPEN
                raise

        return wrapper

# Use circuit_breaker INSTEAD OF retry when:
# - Downstream service is completely down (retrying just adds load)
# - You want fast-fail rather than waiting through retry delays
# - You need system-wide protection, not just per-request retrying
#
# Use retry when:
# - Failures are transient (network blip, momentary overload)
# - The service recovers quickly
# - You can afford the wait between attempts

@circuit_breaker(failure_threshold=3, recovery_timeout=10)
def call_payment_service(amount):
    # raises on failure
    pass
```

**Why:** `@retry` is optimistic — it assumes failures are temporary and tries again. A circuit breaker is pessimistic after a threshold — it stops trying entirely to protect the system from cascading failures. When a service is down, retrying adds load on top of the failing service. The circuit breaker pattern comes from electrical engineering: when too much current flows, the breaker opens to protect the circuit. In software it protects the caller, the failing service, and the whole system.
</details>

---

<a id="q23"></a>

### Q23 🟠 · Capstone — Build @require_auth(roles=["admin"])

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)



**Problem:** Build a `@require_auth(roles=["admin"])` decorator factory for a Flask-style web application. It should: accept a `roles` list, check the current user's role (passed via a `current_user` keyword argument or a global context), raise `PermissionError` if the role is not in the allowed list, and pass through to the original function if authorized. Write a complete working example with multiple role checks.

<details>
<summary>💡 Hint</summary>

The factory captures `roles`. The wrapper checks `kwargs.get("current_user")` or falls back to a module-level `_current_user`. Use `@functools.wraps`. Raise `PermissionError` with a descriptive message naming the required roles and the user's actual role.
</details>

<details>
<summary>✅ Answer</summary>

```python
import functools
from dataclasses import dataclass
from typing import List

@dataclass
class User:
    username: str
    role: str

# Simulated request context (in real Flask/FastAPI this would be request-local):
_current_user: User | None = None

def require_auth(roles: List[str]):
    """
    Decorator factory — checks that the current user has one of the required roles.

    Usage:
        @require_auth(roles=["admin"])
        def delete_user(user_id): ...

        @require_auth(roles=["admin", "moderator"])
        def edit_post(post_id): ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Allow current_user to be passed explicitly (testable) or from context:
            user: User | None = kwargs.pop("current_user", _current_user)

            if user is None:
                raise PermissionError(
                    f"{func.__name__}: authentication required (no user in context)"
                )

            if user.role not in roles:
                raise PermissionError(
                    f"{func.__name__}: role '{user.role}' is not in required roles {roles}"
                )

            return func(*args, **kwargs)
        return wrapper
    return decorator

# ── Endpoints ──

@require_auth(roles=["admin"])
def delete_user(user_id: int) -> str:
    return f"User {user_id} deleted"

@require_auth(roles=["admin", "moderator"])
def edit_post(post_id: int) -> str:
    return f"Post {post_id} edited"

@require_auth(roles=["admin", "moderator", "viewer"])
def read_report(report_id: int) -> str:
    return f"Report {report_id} contents"

# ── Tests ──

admin     = User("alice",   "admin")
moderator = User("bob",     "moderator")
viewer    = User("charlie", "viewer")

# Admin can do everything:
print(delete_user(1,  current_user=admin))      # User 1 deleted
print(edit_post(10,   current_user=admin))      # Post 10 edited
print(read_report(5,  current_user=admin))      # Report 5 contents

# Moderator cannot delete:
try:
    delete_user(1, current_user=moderator)
except PermissionError as e:
    print(f"PermissionError: {e}")
    # PermissionError: delete_user: role 'moderator' is not in required roles ['admin']

# Viewer can only read:
print(read_report(5, current_user=viewer))      # Report 5 contents
try:
    edit_post(10, current_user=viewer)
except PermissionError as e:
    print(f"PermissionError: {e}")
    # PermissionError: edit_post: role 'viewer' is not in required roles ['admin', 'moderator']

# No user at all:
try:
    delete_user(1)  # no current_user arg, _current_user is None
except PermissionError as e:
    print(f"PermissionError: {e}")
    # PermissionError: delete_user: authentication required (no user in context)
```

**Why:** This capstone combines everything: a three-layer factory structure, `@functools.wraps` for identity preservation, `kwargs.pop` for the dual-source user lookup (context or explicit argument), and meaningful error messages. The `roles` list makes the decorator declarative — reading `@require_auth(roles=["admin"])` tells you the access rule without reading the function body. This is exactly how Flask-Login, FastAPI dependencies, and Django's `@permission_required` work under the hood.
</details>

---

## Navigation

| | |
|---|---|
| Back to Module | [theory.md](./theory.md) |
| Theory | [theory.md](./theory.md) |
| Class Decorators | [01_class_decorators/practice.md](./01_class_decorators/practice.md) |
| Production Patterns | [02_production_patterns/practice.md](./02_production_patterns/practice.md) |
| Next Module | [11_generators_iterators](../11_generators_iterators/practice.md) |

---

**Related:** [Class Decorators →](./01_class_decorators/theory.md) · [Production Patterns →](./02_production_patterns/theory.md) · [Prerequisite: Closures](../04_functions/02_closures_decorators/01_closures_theory.md)
