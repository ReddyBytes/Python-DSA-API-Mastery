<a id="top"></a>
# 🎁 Decorators — Theory

> *"A decorator is a function that takes a function, wraps new behavior around it,*
> *and returns the enhanced version. One of Python's most elegant ideas."*

## 📖 Table of Contents

- [🎬 The Problem That Made Decorators Inevitable](#the-problem-that-made-decorators-inevitable)
- [📌 Learning Priority](#learning-priority)
- [1. Functions Are First-Class Objects](#1-functions-are-first-class-objects)
- [2. Closures — The Engine Inside Decorators](#2-closures-the-engine-inside-decorators)
  - [Closure Internals — Where Captured Variables Live](#closure-internals-where-captured-variables-live)
- [3. Your First Decorator — Manual Form](#3-your-first-decorator-manual-form)
- [4. The @ Syntax — Syntactic Sugar](#4-the-syntax-syntactic-sugar)
- [5. functools.wraps — Preserving Identity](#5-functoolswraps-preserving-identity)
- [6. Decorators with Arguments — Decorator Factories](#6-decorators-with-arguments-decorator-factories)
- [7. Class Decorators](#7-class-decorators)
  - [Class as a Decorator](#class-as-a-decorator)
  - [Decorating a Class](#decorating-a-class)
- [8. Built-in Decorators — @property, @classmethod, @staticmethod](#8-built-in-decorators-property-classmethod-staticmethod)
  - [@property — Computed Attributes with Validation](#property-computed-attributes-with-validation)
  - [@classmethod — Factory Constructors](#classmethod-factory-constructors)
  - [@staticmethod — Utility Functions](#staticmethod-utility-functions)
- [9. Stacking Decorators — Order and Interaction](#9-stacking-decorators-order-and-interaction)
- [10. Production Decorator Patterns](#10-production-decorator-patterns)
  - [Timing](#timing)
  - [Retry with Exponential Backoff](#retry-with-exponential-backoff)
  - [Memoization / TTL Cache](#memoization--ttl-cache)
  - [Input Validation](#input-validation)
- [11. Decorators for Async Functions](#11-decorators-for-async-functions)
- [12. Decorators with Optional Arguments](#12-decorators-with-optional-arguments)
- [13. Introspection — Looking Inside Decorators](#13-introspection-looking-inside-decorators)
- [14. Anti-Patterns and Gotchas](#14-anti-patterns-and-gotchas)
  - [Gotcha: Missing @functools.wraps](#gotcha-missing-functoolswraps)
  - [Gotcha: Mutable Default in Decorator Factory](#gotcha-mutable-default-in-decorator-factory)
  - [Gotcha: Decorator Applied at Import Time](#gotcha-decorator-applied-at-import-time)
  - [Gotcha: Missing Return Value](#gotcha-missing-return-value)
  - [Gotcha: Methods and self](#gotcha-methods-and-self)
- [15. functools Utilities — cache, cached_property, singledispatch](#15-functools-utilities-cache-cached_property-singledispatch)
  - [functools.lru_cache and functools.cache](#functoolslru_cache-and-functoolscache)
  - [functools.cached_property](#functoolscached_property)
  - [functools.singledispatch](#functoolssingledispatch)
- [16. How Python Executes Decorators — The Full Mental Model](#16-how-python-executes-decorators-the-full-mental-model)
- [Summary](#summary)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
Basic decorator pattern · `@functools.wraps` · `functools.lru_cache` · Class decorators · Decorator factories (with arguments)

**Should Learn** — Important for real projects, comes up regularly:
`functools.cache` (Python 3.9+) · `functools.cached_property` · Stacked decorators · `@property` / `@classmethod` / `@staticmethod`

**Good to Know** — Useful in specific situations:
`functools.singledispatch` · `__wrapped__` and `inspect.unwrap()` · Decorator performance overhead

**Reference** — Know it exists, look up when needed:
`@decorator.decorator` (third-party) · Decorators that modify signatures (`wrapt`)

---

<a id="the-problem-that-made-decorators-inevitable"></a>
# 🎬 The Problem That Made Decorators Inevitable

It's sprint review day. Your team just shipped a payment service with 40 endpoints. Now the product manager says:

> 🔍 **Good to know:** This module assumes you understand closures. Not familiar with them? Start here first: [04_functions — Closures](../04_functions/02_closures_decorators/01_closures_theory.md)

> *"We need to log every function call — what was called, with what arguments, how long it took, and whether it succeeded or failed."*

You look at your codebase:

```python
def create_order(user_id, items):
    ...

def process_payment(order_id, amount):
    ...

def send_confirmation(order_id, email):
    ...

# ... 37 more functions
```

**Option A — Copy-paste logging into every function:**
```python
def create_order(user_id, items):
    logger.info("create_order called: user_id=%s", user_id)
    start = time.time()
    try:
        result = _create_order_impl(user_id, items)
        logger.info("create_order succeeded in %.3fs", time.time() - start)
        return result
    except Exception:
        logger.exception("create_order failed")
        raise
```

Now do that 40 times. Then the manager says: *"Also add timing to all API calls."* You repeat.

**Option B — Decorators:**
```python
@logged
@timed
def create_order(user_id, items):
    ...

@logged
@timed
def process_payment(order_id, amount):
    ...
```

Two lines per function. The behavior is defined once, reused everywhere. That's the decorator philosophy: **separate the what from the how**.

---

<a id="1-functions-are-first-class-objects"></a>
# 1. Functions Are First-Class Objects

Before decorators make sense, you need to deeply understand this:

**In Python, functions are objects — like integers, strings, or lists.** You can assign them to variables, store them in data structures, pass them as arguments, and return them from other functions. This property is called **first-class functions**.

```python
def greet(name):
    return f"Hello, {name}!"

# Functions have a type:
print(type(greet))   # <class 'function'>

# You can assign them to variables:
say_hi = greet
print(say_hi("Alice"))   # "Hello, Alice!" — same function, different name

# You can store them in data structures:
actions = [greet, str.upper, len]
for action in actions:
    print(action("hello"))   # "Hello, hello!", "HELLO", 5

# You can pass them as arguments:
def apply(func, value):
    return func(value)

print(apply(greet, "Bob"))   # "Hello, Bob!"
print(apply(len, "Bob"))     # 3

# You can return them from functions:
def make_multiplier(n):
    def multiply(x):
        return x * n
    return multiply   # ← returns the function object, not the result

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5))   # 10
print(triple(5))   # 15
```

⚠️ **Common mistake — calling vs referencing:** `apply(greet, "Bob")` passes the function object. `apply(greet("Bob"), ...)` passes the *result* of calling it. The `()` is what triggers a call — without it, you're working with the object itself.

💡 **Hint:** `make_multiplier` above is the building block for understanding closures and decorators. The inner function `multiply` "remembers" `n` even after `make_multiplier` finishes — that memory is what a closure is.

📝 **Practice:** [first-class functions / pass a function as argument →](./practice.md#q1--first-class-functions--pass-a-function-as-argument)

> [↑ Back to Top](#top)

---

<a id="2-closures-the-engine-inside-decorators"></a>
# 2. Closures — The Engine Inside Decorators

A **[closure](../04_functions/theory.md#closure-cell-internals--how-captured-variables-actually-work)** is a function that captures variables from its enclosing scope, even after that scope has finished executing. Think of it as a function that carries a backpack — the backpack holds the variables from the scope where the function was created, and the function can reach into that backpack whenever it needs them.

```python
def make_counter():
    count = 0          # ← this variable lives in make_counter's scope

    def counter():
        nonlocal count
        count += 1
        return count

    return counter     # ← counter captures 'count' from make_counter

c1 = make_counter()
c2 = make_counter()

print(c1())   # 1  — c1 has its own 'count'
print(c1())   # 2
print(c1())   # 3
print(c2())   # 1  — c2 has a SEPARATE 'count'
```

**What the closure captures:**
```
make_counter() finishes → its local scope would normally be destroyed
BUT counter() still holds a reference to 'count'
→ Python keeps the scope alive as a "cell" inside the closure
→ c1.__closure__[0].cell_contents == 3  (after the calls above)
```

**Why closures matter for decorators:**
A decorator wraps a function. The wrapper function needs to remember the original function to call it. That "remembering" is a closure — the wrapper closes over the original function object.

```python
def make_greeting(prefix):
    def greet(name):           # 'prefix' is captured from make_greeting
        return f"{prefix}, {name}!"
    return greet

hello = make_greeting("Hello")
hey   = make_greeting("Hey")

print(hello("Alice"))   # "Hello, Alice!"
print(hey("Bob"))       # "Hey, Bob!"
```

---

<a id="closure-internals-where-captured-variables-live"></a>
## Closure Internals — Where Captured Variables Live

When a closure captures a variable, Python creates a **cell object** on the heap. The outer function's stack frame is destroyed on return, but the cell object survives because the inner function holds a reference to it.

```
make_greeting("Hello") call:

Stack (during call):
┌──────────────────────────────────────────┐
│  make_greeting() frame                   │
│    prefix → cell_object (on heap)        │
└──────────────────────────────────────────┘

Stack (after return): frame DESTROYED

Heap:
  ┌─────────────────────────────────────────┐
  │  cell object                            │
  │    cell_contents: "Hello"               │  ← prefix value lives here
  └─────────────────────────────────────────┘
          ↑
  ┌─────────────────────────────────────────┐
  │  function object: greet                 │
  │    __closure__: (cell_object,)          │  ← keeps cell alive
  └─────────────────────────────────────────┘
          ↑
  hello → points to this function object
```

You can inspect this:

```python
def make_greeting(prefix):
    def greet(name):
        return f"{prefix}, {name}!"
    return greet

hello = make_greeting("Hello")

print(hello.__closure__)                       # (<cell at 0x10f3b5d30>,)
print(hello.__closure__[0].cell_contents)      # "Hello"
```

**Each call to `make_greeting` creates a SEPARATE cell object:**

```
hello = make_greeting("Hello")   →  cell_contents: "Hello"
hey   = make_greeting("Hey")     →  cell_contents: "Hey"   (different cell)
```

This is why `c1` and `c2` from the counter example above have independent state — they each close over a different cell.

**Why `nonlocal` works:**
`nonlocal count` tells the inner function: "Don't create a new local `count` — modify the existing cell object." Both inner functions sharing the same cell will see each other's updates.

```python
def make_counter():
    count = 0           # cell object: count=0

    def inc():
        nonlocal count  # writes to cell
        count += 1

    def get():
        return count    # reads from same cell

    return inc, get

inc, get = make_counter()
inc(); inc(); inc()
print(get())    # 3 — same cell shared by inc and get
```

⚠️ **Common mistake — the late-binding trap:** If you create closures in a loop, all of them capture the *same* variable (not a copy of its value at each iteration). The classic bug: `funcs = [lambda: i for i in range(3)]` — all three lambdas return `2` because they all reference the same `i`. Fix: `lambda i=i: i` (default argument forces early binding). Full explanation in [04_functions — Late-Binding Trap](../04_functions/02_closures_decorators/01_closures_theory.md).

🔍 **Good to know:** `__closure__` is `None` for functions that don't capture anything. You can use this to check whether a function is actually a closure: `bool(func.__closure__)`.

📝 **Practice:** [closures / make_counter closure →](./practice.md#q2--closures--make_counter-closure)

> [↑ Back to Top](#top)

---

<a id="3-your-first-decorator-manual-form"></a>
# 3. Your First Decorator — Manual Form

A decorator is just a function that:
1. Takes a function as its argument
2. Defines a wrapper function inside
3. The wrapper adds behavior before/after calling the original
4. Returns the wrapper (not the result of calling the wrapper)

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):       # accepts any arguments
        print(f"Before {func.__name__}")
        result = func(*args, **kwargs)  # call the original function
        print(f"After {func.__name__}")
        return result                   # return the original's result
    return wrapper                      # return the wrapper, not wrapper()

# Manual application:
def greet(name):
    print(f"Hello, {name}!")

greet = my_decorator(greet)   # ← this is EXACTLY what @my_decorator does

greet("Alice")
# Before greet
# Hello, Alice!
# After greet
```

**Memory model — what happens to the name `greet`:**
```
Before decoration:
  greet ──→ <function greet at 0x100>

After  greet = my_decorator(greet):
  greet ──→ <function wrapper at 0x200>  ← now points to wrapper
              └── closure contains: func ──→ <function greet at 0x100>
```

The original function isn't gone — it's captured in the wrapper's closure as `func`. Every time you call `greet("Alice")`, you're actually calling `wrapper("Alice")`, which then calls the original via `func("Alice")`.

⚠️ **Common mistake — `return wrapper()` instead of `return wrapper`:** Returning `wrapper()` calls the wrapper immediately and returns its result. The decorator would execute once at decoration time and `greet` would be bound to whatever `wrapper()` returns (probably `None`). Always `return wrapper` — the function object, not a call.

📝 **Practice:** [manual decorator / write from scratch →](./practice.md#q3--manual-decorator--write-manual-form-from-scratch)

> [↑ Back to Top](#top)

---

<a id="4-the-syntax-syntactic-sugar"></a>
# 4. The @ Syntax — Syntactic Sugar

The `@` symbol is purely syntactic sugar — Python rewrites `@decorator` above a function definition into the manual form you saw in section 3. These two are **identical**:

```python
# Using @:
@my_decorator
def greet(name):
    print(f"Hello, {name}!")

# Equivalent without @:
def greet(name):
    print(f"Hello, {name}!")
greet = my_decorator(greet)
```

The `@decorator` line runs **at definition time** (when the module is imported), not at call time. By the time you call `greet("Alice")`, the name `greet` already refers to the wrapper.

**Multiple decorators — applied bottom-up, run top-down:**

```python
@A
@B
@C
def func():
    pass

# Equivalent to:
func = A(B(C(func)))

# CALL ORDER when func() is called:
# A's wrapper runs first (outermost)
#   → B's wrapper runs second
#     → C's wrapper runs third (innermost)
#       → original func() runs
#     ← C's after-code
#   ← B's after-code
# ← A's after-code
```

💡 **Hint:** Because decorators run at import time, any expensive setup inside a decorator factory (DB connections, file reads) runs when the module is first imported — not when the function is first called. Keep decorator setup lightweight.

📝 **Practice:** [@ syntax / convert manual to @syntax →](./practice.md#q4---syntax--convert-manual-to--syntax)

> [↑ Back to Top](#top)

---

<a id="5-functoolswraps-preserving-identity"></a>
# 5. functools.wraps — Preserving Identity

Without `@wraps`, your wrapper loses the original function's identity. This breaks help systems, logging, debugging tools, and introspection:

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name):
    """Greet someone by name."""
    return f"Hello, {name}!"

print(greet.__name__)   # 'wrapper'     ← WRONG
print(greet.__doc__)    # None          ← WRONG
```

This breaks:
- Help systems (`help(greet)` shows wrapper's docs, not greet's)
- Logging (logs show `wrapper` not `greet`)
- `inspect.signature(greet)` shows wrapper's signature
- pytest fixture resolution and test output

**Fix — always use `@functools.wraps`:**

```python
import functools

def my_decorator(func):
    @functools.wraps(func)          # ← copies __name__, __doc__, __module__,
    def wrapper(*args, **kwargs):   #   __qualname__, __annotations__, __dict__
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name):
    """Greet someone by name."""
    return f"Hello, {name}!"

print(greet.__name__)     # 'greet'           ← correct
print(greet.__doc__)      # 'Greet someone'   ← correct
print(greet.__wrapped__)  # original function ← @wraps adds this too
```

**`@functools.wraps(func)` copies these attributes from `func` to `wrapper`:**

```
__name__       → function name
__doc__        → docstring
__module__     → module where func was defined
__qualname__   → qualified name (e.g. "MyClass.method")
__annotations__→ type hints
__dict__       → any custom attributes on the function
__wrapped__    → reference to the original (added by wraps itself)
```

**Rule: Every wrapper function must have `@functools.wraps(func)`. No exceptions.**

⚠️ **Common mistake — forgetting @wraps in decorator factories:** When you have three nested functions (factory → decorator → wrapper), `@functools.wraps(func)` goes on the innermost `wrapper`, not on `decorator`. The `decorator` function is never returned to the outside world — `wrapper` is.

📝 **Practice:** [functools.wraps / show what breaks without it →](./practice.md#q5--functoolswraps--show-what-breaks-without-wraps)

> [↑ Back to Top](#top)

---

<a id="6-decorators-with-arguments-decorator-factories"></a>
# 6. Decorators with Arguments — Decorator Factories

What if you want `@retry(max_attempts=3)` instead of just `@retry`? A plain decorator takes one argument (the function). To pass configuration, you need a **decorator factory** — a function that takes arguments and *returns* a decorator.

This creates three nested levels: the factory receives configuration, the decorator wraps the function, and the wrapper runs at call time.

```python
import functools

def retry(max_attempts=3, exceptions=(Exception,)):
    """Decorator factory — returns a decorator configured with these settings."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    print(f"Attempt {attempt}/{max_attempts} failed: {e}")
            raise last_error
        return wrapper
    return decorator

@retry(max_attempts=5, exceptions=(ConnectionError, TimeoutError))
def fetch_data(url):
    return requests.get(url).json()

@retry(max_attempts=2)   # uses default exceptions=(Exception,)
def save_record(data):
    db.save(data)
```

**Three-layer structure:**

```
retry(max_attempts=3)                 ← LEVEL 1: factory — takes config, returns decorator
  └── decorator(func)                 ← LEVEL 2: decorator — takes function, returns wrapper
        └── wrapper(*args, **kwargs)  ← LEVEL 3: wrapper — runs each time func is called
```

**The call chain at decoration vs call time:**
```
retry(max_attempts=5)     → returns decorator          (at import time, factory called)
decorator(fetch_data)     → returns wrapper            (at import time, @ applied)
wrapper(url)              → runs on every call         (at call time)
```

🔍 **Good to know:** The factory level (level 1) runs once when the module loads. The decorator level (level 2) runs once per decorated function. The wrapper level (level 3) runs on every function call. Keep levels 1 and 2 as lightweight as possible.

📝 **Practice:** [decorator factory / repeat N times →](./practice.md#q6--decorator-factory--repeat-n-times)

> [↑ Back to Top](#top)

---

<a id="7-class-decorators"></a>
# 7. Class Decorators

Python offers two directions for class + decorator interaction: using a **class as the decorator** (the class wraps a function), and applying a **decorator to a class** (the decorator modifies the class itself). They're different tools for different jobs.

---

<a id="class-as-a-decorator"></a>
## Class as a Decorator

Instead of a closure-based wrapper function, you implement the decorator as a class with `__init__` (receives configuration or the function) and `__call__` (runs on each function call). Class decorators shine when the decorator needs to **maintain state across calls** — something a simple closure can do but a class makes explicit and readable.

```python
import functools

class retry:
    def __init__(self, max_attempts=3):
        self.max_attempts = max_attempts   # ← state stored on the instance

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, self.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == self.max_attempts:
                        raise
                    print(f"Attempt {attempt} failed: {e}")
        return wrapper

@retry(max_attempts=3)     # retry(3).__call__(fetch_data) → wrapper
def fetch_data(url):
    ...
```

**When the class itself IS the decorator (no parentheses):**

```python
class call_counter:
    def __init__(self, func):
        functools.update_wrapper(self, func)   # equivalent to @functools.wraps
        self.func = func
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)

@call_counter   # no parentheses — __init__ takes the function directly
def greet(name):
    return f"Hello, {name}!"

greet("Alice")
greet("Bob")
print(greet.calls)   # 2  ← state is on the decorator object itself
```

💡 **Hint:** When your decorator needs persistent state (a call counter, a cache, an error log), a class decorator makes the state structure explicit. When it's stateless logic, a function decorator is simpler. If the state is just one variable, either works — choose based on readability.

---

<a id="decorating-a-class"></a>
## Decorating a Class

Decorators can be applied to **classes** as well as functions. Instead of receiving a function and returning a wrapper, the decorator receives a class and returns a modified (or replaced) class.

```python
def singleton(cls):
    """Ensure only one instance of the class can exist."""
    instances = {}

    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class DatabaseConnection:
    def __init__(self, url):
        self.url = url
        print(f"Connecting to {url}")

db1 = DatabaseConnection("postgres://...")   # "Connecting to postgres://..."
db2 = DatabaseConnection("postgres://...")   # (no output — returns cached instance)
print(db1 is db2)   # True
```

**`@dataclass` is the most widely-used built-in class decorator** — it auto-generates `__init__`, `__repr__`, `__eq__`, and optionally `__hash__` based on the annotated fields. See [05_oops — Dataclasses](../05_oops/14_dataclasses.md) for a deep dive.

```python
from dataclasses import dataclass

@dataclass                  # ← class decorator: reads field annotations,
class Order:                #   generates __init__, __repr__, __eq__
    order_id: int
    user_id: int
    total: float
    status: str = "pending"

o = Order(1, 42, 99.99)
print(o)   # Order(order_id=1, user_id=42, total=99.99, status='pending')
```

🔍 **Good to know:** When you apply `@singleton` to a class, the name `DatabaseConnection` no longer refers to the class — it refers to `get_instance` (a function). This means `isinstance(db1, DatabaseConnection)` will raise `TypeError`. If you need `isinstance` to work, implement the singleton pattern differently (e.g., via `__new__`).

📝 **Practice:** [class decorator / call_counter →](./practice.md#q7--class-decorator--callcounter-class) · [decorating a class / singleton →](./practice.md#q8--decorating-classes--singleton-class-decorator)

**Deep dive:** Class decorator patterns, `__init_subclass__`, metaclasses →
[`./01_class_decorators/theory.md`](./01_class_decorators/theory.md)

> [↑ Back to Top](#top)

---

<a id="8-built-in-decorators-property-classmethod-staticmethod"></a>
# 8. Built-in Decorators — @property, @classmethod, @staticmethod

Python ships three essential decorators for class design. They don't add behavior around a function — they change how Python handles attribute and method access on the class itself.

---

<a id="property-computed-attributes-with-validation"></a>
## @property — Computed Attributes with Validation

`@property` turns a method into a computed attribute — you access it like a field (`obj.value`) but it runs a function under the hood. This lets you add validation, lazy computation, or derived values without changing the public API. See [05_oops — Properties](../05_oops/11_properties.md) for full descriptor internals.

```python
class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius

    @property
    def celsius(self):                    # read as: temp.celsius
        return self._celsius

    @celsius.setter
    def celsius(self, value):             # write as: temp.celsius = 25
        if value < -273.15:
            raise ValueError(f"Temperature {value}°C below absolute zero")
        self._celsius = value

    @celsius.deleter
    def celsius(self):                    # del temp.celsius
        del self._celsius

    @property
    def fahrenheit(self):                 # computed — no setter (read-only)
        return self._celsius * 9/5 + 32

t = Temperature(25)
print(t.fahrenheit)   # 77.0
t.celsius = -300      # ValueError: Temperature -300°C below absolute zero
```

⚠️ **Common mistake — recomputing on every access:** A plain `@property` runs its function every time you access the attribute. If the computation is expensive (a DB query, complex math), use `@functools.cached_property` instead — it computes once and caches the result on the instance. Covered in section 15.

---

<a id="classmethod-factory-constructors"></a>
## @classmethod — Factory Constructors

A regular method receives the instance as `self`. A `@classmethod` receives the **class** itself as `cls`. This makes it the right tool for **alternative constructors** — ways to create an instance from different input formats. See [05_oops — Class Methods](../05_oops/09_class_instance_static_methods.md) for comparison with instance methods.

```python
class Order:
    def __init__(self, order_id, items, total):
        self.order_id = order_id
        self.items = items
        self.total = total

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        """Alternative constructor — create from API response dict."""
        return cls(
            order_id=data["id"],
            items=data["items"],
            total=sum(i["price"] for i in data["items"])
        )

    @classmethod
    def empty(cls) -> "Order":
        """Create an empty order — useful for testing."""
        return cls(order_id=None, items=[], total=0.0)

order = Order.from_dict({"id": 1, "items": [{"price": 9.99}]})
```

💡 **Hint:** Because `@classmethod` receives `cls` instead of a hard-coded class name, it works correctly with inheritance — a subclass calling `SubOrder.from_dict(...)` creates a `SubOrder` instance, not an `Order`.

---

<a id="staticmethod-utility-functions"></a>
## @staticmethod — Utility Functions

A `@staticmethod` receives neither `self` nor `cls`. It's a plain function that lives on the class namespace for organisational reasons — it's conceptually related to the class but doesn't need access to instance or class state. See [05_oops — Static Methods](../05_oops/09_class_instance_static_methods.md).

```python
class Order:
    @staticmethod
    def validate_status(status: str) -> bool:
        """Pure validation — needs no instance or class state."""
        return status in {"pending", "processing", "shipped", "delivered", "cancelled"}

Order.validate_status("shipped")   # True — callable on class or instance
```

**Comparison — when to use each:**
```
Method type       First param    Can access          Typical use
─────────────────────────────────────────────────────────────────────
Regular method    self           instance + class    Behaviour that reads/modifies instance
@classmethod      cls            class only          Alternative constructors, class-wide ops
@staticmethod     (none)         nothing             Utility / pure functions tied to the class
```

🔍 **Good to know:** `@staticmethod` can also be called on an instance (`order.validate_status("shipped")`). Python just ignores `self` and calls the function directly. Calling on the class (`Order.validate_status(...)`) is clearer — it signals that no instance state is involved.

📝 **Practice:** [@property / convert attribute to property →](./practice.md#q9--property--convert-attribute-to-property) · [@classmethod + @staticmethod →](./practice.md#q10--classmethod-and-staticmethod)

> [↑ Back to Top](#top)

---

<a id="9-stacking-decorators-order-and-interaction"></a>
# 9. Stacking Decorators — Order and Interaction

When you stack decorators, the order in which you write them determines both how they wrap and how they execute. The rule is simple but easy to get backwards:

**Applied bottom-up (innermost first). Executed top-down (outermost first).**

```python
@timer          # applied third (outermost wrapper)
@logger         # applied second
@retry(3)       # applied first (innermost wrapper, closest to original)
def fetch_data(url):
    ...

# Equivalent to:
fetch_data = timer(logger(retry(3)(fetch_data)))
```

**Execution order when `fetch_data(url)` is called:**

```
timer's before-code      (outermost — runs first)
  logger's before-code
    retry's logic
      original fetch_data(url)
    retry handles exception if needed
  logger's after-code
timer's after-code       (outermost — runs last)
```

**Practical example — order matters for correctness:**

```python
# ✅ CORRECT: @retry inside @logger
# Logger sees the final outcome after all retries are exhausted
@logger
@retry(3)
def fetch_user(user_id):
    ...
# → Logger logs ONE result: either success or the final failure after 3 attempts

# ❌ Usually WRONG: @retry outside @logger
# Logger wraps retry — logs "starting", then retry runs 3 times internally,
# then logger logs "done" — you lose visibility into individual retry attempts
@retry(3)
@logger
def fetch_user(user_id):
    ...
```

```python
# ✅ CORRECT: @timed outside @logged
# You time the whole thing including logging overhead (usually negligible)
@timed
@logged
def process():
    ...

# This is a matter of what you want to measure — be intentional
```

⚠️ **Common mistake — `@cache` on top of `@retry`:** If `@cache` is outside `@retry`, a failed call gets cached and subsequent calls return the cached exception — they never retry. `@cache` must be inside `@retry` (closer to the original function) so that retried calls can still be cached on success.

💡 **Hint:** When in doubt about stacking order, think from the outside in: "What does the caller see?" The outermost decorator is what the caller interacts with. Work inward from there.

📝 **Practice:** [stacking / stack timer and retry →](./practice.md#q11--stacking--stack-timer-and-retry)

> [↑ Back to Top](#top)

---

<a id="10-production-decorator-patterns"></a>
# 10. Production Decorator Patterns

These are the decorator patterns you'll actually write in production services — not toy examples, but battle-tested wrappers that handle edge cases, integrate with logging, and compose cleanly with other decorators.

---

<a id="timing"></a>
## Timing

Wrap any function to measure and log its execution time. Using `time.perf_counter()` (not `time.time()`) gives you the highest-resolution clock available on the platform.

```python
import functools, time, logging

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
def process_batch(items):
    return [transform(item) for item in items]
```

💡 **Hint:** Use `finally` instead of logging after the return. If the function raises, `finally` still fires — so you log the elapsed time even for failed calls. Logging *before* the raise gives you timing data you can cross-reference with the exception log.

---

<a id="retry-with-exponential-backoff"></a>
## Retry with Exponential Backoff

Network calls fail. Database connections drop. The retry decorator absorbs transient failures without the caller knowing. Exponential backoff prevents hammering an already-struggling service.

```python
import functools, time, logging

def retry(max_attempts=3, delay=1.0, backoff=2.0, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise
                    logging.warning("%s attempt %d/%d failed: %s — retrying in %.1fs",
                                    func.__name__, attempt, max_attempts, e, wait)
                    time.sleep(wait)
                    wait *= backoff   # ← each retry waits longer
        return wrapper
    return decorator

@retry(max_attempts=5, delay=0.5, backoff=2.0, exceptions=(ConnectionError,))
def fetch_user(user_id):
    return db.get(user_id)
# Waits: 0.5s → 1.0s → 2.0s → 4.0s before final attempt
```

⚠️ **Common mistake — retrying non-retryable errors:** Retrying a `ValueError` or `KeyError` (programming errors) wastes time and masks bugs. Always specify the `exceptions` tuple explicitly — only retry errors that are genuinely transient (network timeouts, connection resets, rate limit responses).

---

<a id="memoization--ttl-cache"></a>
## Memoization / TTL Cache

Cache a function's return value so repeated calls with the same arguments return instantly. For production use, a TTL (time-to-live) cache avoids serving stale data indefinitely.

```python
import functools

# Built-in — use this for pure functions with no TTL requirement:
@functools.lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Custom TTL cache — expires entries after N seconds:
import time

def ttl_cache(ttl_seconds=60):
    def decorator(func):
        cache = {}   # {args: (result, timestamp)}

        @functools.wraps(func)
        def wrapper(*args):
            now = time.time()
            if args in cache:
                result, ts = cache[args]
                if now - ts < ttl_seconds:
                    return result         # ← cache hit, still fresh
            result = func(*args)
            cache[args] = (result, now)   # ← store with timestamp
            return result
        return wrapper
    return decorator

@ttl_cache(ttl_seconds=300)   # cache for 5 minutes
def get_config(key):
    return config_service.fetch(key)
```

🔍 **Good to know:** `lru_cache` and `ttl_cache` only work with **hashable arguments** — you can't cache calls that take `list`, `dict`, or other mutable types as arguments. Convert to tuple before caching, or use a different keying strategy.

---

<a id="input-validation"></a>
## Input Validation

Validate argument types at the boundary without cluttering function bodies with `isinstance` checks. Useful for public APIs where you want clear `TypeError` messages.

```python
import functools, inspect

def validate(**type_checks):
    """@validate(price=float, user_id=int) — raises TypeError on bad types."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            for param, expected_type in type_checks.items():
                if param in bound.arguments:
                    value = bound.arguments[param]
                    if not isinstance(value, expected_type):
                        raise TypeError(
                            f"{func.__name__}: '{param}' expected {expected_type.__name__}, "
                            f"got {type(value).__name__}"
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@validate(price=float, user_id=int)
def create_order(user_id, price, notes=""):
    ...

create_order(42, 9.99)        # ✅
create_order("42", 9.99)      # TypeError: create_order: 'user_id' expected int, got str
```

📝 **Practice:** [timer decorator →](./practice.md#q12--production-patterns--timer-decorator) · [retry with backoff →](./practice.md#q13--production-patterns--retry-with-backoff)

**Deep dive:** Rate limiting, circuit breaker, audit logging, async retry patterns →
[`./02_production_patterns/theory.md`](./02_production_patterns/theory.md)

> [↑ Back to Top](#top)

---

<a id="11-decorators-for-async-functions"></a>
# 11. Decorators for Async Functions

A regular decorator wrapper is a synchronous function. If you apply it to an `async def` function, calling the decorated function returns a coroutine — but `wrapper` runs synchronously, which means it can't `await` the original. The fix: make the wrapper `async` too.

```python
import functools, asyncio

def async_timed(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):       # ← async wrapper for async func
        start = asyncio.get_event_loop().time()
        result = await func(*args, **kwargs)  # ← await the original
        elapsed = asyncio.get_event_loop().time() - start
        print(f"{func.__name__} took {elapsed:.3f}s")
        return result
    return wrapper

@async_timed
async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()
```

**Decorator that works on BOTH sync and async functions:**

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
                print(f"{func.__name__} took {time.perf_counter() - start:.3f}s")
        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                print(f"{func.__name__} took {time.perf_counter() - start:.3f}s")
        return sync_wrapper
```

⚠️ **Common mistake — applying a sync wrapper to an async function:** If `wrapper` is not `async`, calling `await decorated_func()` will raise `TypeError: object NoneType can't be used in 'await' expression` — because a sync wrapper doesn't return a coroutine. Use `asyncio.iscoroutinefunction()` to detect and handle both cases.

📝 **Practice:** [async decorator / works on sync and async →](./practice.md#q14--async-decorator--works-on-sync-and-async)

> [↑ Back to Top](#top)

---

<a id="12-decorators-with-optional-arguments"></a>
# 12. Decorators with Optional Arguments

The challenge: make `@retry` and `@retry(max=3)` both work with the same decorator. The trick is the `_func` sentinel parameter — if it's set, the decorator was called without parentheses (function passed directly); if it's `None`, parentheses were used and you return a decorator.

```python
import functools

def retry(_func=None, *, max_attempts=3):
    """
    Works as:
      @retry               ← _func is the decorated function
      @retry()             ← _func is None, max_attempts=3
      @retry(max_attempts=5) ← _func is None, max_attempts=5
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt == max_attempts - 1:
                        raise
        return wrapper

    if _func is not None:
        # Called as @retry (no parentheses) — _func IS the function
        return decorator(_func)
    else:
        # Called as @retry() or @retry(max_attempts=5) — return decorator
        return decorator

@retry                    # ✅ works
def op1(): ...

@retry()                  # ✅ works
def op2(): ...

@retry(max_attempts=5)    # ✅ works
def op3(): ...
```

🔍 **Good to know:** The `*` in `def retry(_func=None, *, max_attempts=3)` forces `max_attempts` to be keyword-only. This prevents `@retry(5)` (positional) from accidentally being interpreted as `_func=5` — which would fail silently and use default `max_attempts`.

📝 **Practice:** [optional arguments / validate with or without parens →](./practice.md#q15--optional-arguments--validate-with-or-without-parens)

> [↑ Back to Top](#top)

---

<a id="13-introspection-looking-inside-decorators"></a>
# 13. Introspection — Looking Inside Decorators

`@functools.wraps` preserves identity, and `__wrapped__` lets you (and tools like pytest, IDEs, and `inspect`) see through the decorator stack to the original function.

```python
import functools, inspect

def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name: str) -> str:
    """Greet by name."""
    return f"Hello, {name}!"

# With @functools.wraps:
print(greet.__name__)            # 'greet'
print(greet.__doc__)             # 'Greet by name.'
print(greet.__wrapped__)         # <function greet> — original function
print(inspect.signature(greet))  # (name: str) -> str

# Unwrap the full decorator stack:
print(inspect.unwrap(greet))     # original function, all wrappers removed
```

**`__wrapped__` is the key** — it lets tools like pytest, IDEs, and `inspect` see through decorators. Without it, `inspect.signature()` would show the wrapper's `(*args, **kwargs)` signature instead of the original's type-annotated signature.

```python
# inspect.unwrap() follows the __wrapped__ chain all the way to the original
original = inspect.unwrap(greet)

# Check whether something is decorated:
is_decorated = hasattr(greet, "__wrapped__")
```

💡 **Hint:** When writing libraries, preserve `__wrapped__` (use `@functools.wraps` always). Library consumers who want to patch or inspect your functions need this chain to work.

📝 **Practice:** [introspection / use inspect.unwrap →](./practice.md#q16--introspection--use-inspectunwrap)

> [↑ Back to Top](#top)

---

<a id="14-anti-patterns-and-gotchas"></a>
# 14. Anti-Patterns and Gotchas

These are the five decorator mistakes that appear most often in code reviews. Knowing them by name means catching them instantly.

---

<a id="gotcha-missing-functoolswraps"></a>
## Gotcha: Missing @functools.wraps

```python
# ❌ Breaks introspection, help(), logging, pytest:
def timer(func):
    def wrapper(*args, **kwargs):       # no @wraps!
        return func(*args, **kwargs)
    return wrapper

@timer
def process():
    """Process data."""
    pass

print(process.__name__)  # 'wrapper'   ← wrong name in logs/errors
print(process.__doc__)   # None        ← docstring lost
```

✅ Fix: add `@functools.wraps(func)` on the `wrapper` function inside every decorator you write.

---

<a id="gotcha-mutable-default-in-decorator-factory"></a>
## Gotcha: Mutable Default in Decorator Factory

```python
# ❌ All decorated functions share the same results list:
def collect_results(results=[]):    # mutable default — created once at def time!
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            r = func(*args, **kwargs)
            results.append(r)
            return r
        return wrapper
    return decorator

# ✅ Fix: use None as sentinel, create fresh list each call:
def collect_results(results=None):
    if results is None:
        results = []
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            r = func(*args, **kwargs)
            results.append(r)
            return r
        return wrapper
    return decorator
```

This is the same mutable default argument trap that applies to regular functions — see [04_functions — Mutable Default Argument](../04_functions/theory.md#️-type-3-edge-case--the-mutable-default-argument-trap).

---

<a id="gotcha-decorator-applied-at-import-time"></a>
## Gotcha: Decorator Applied at Import Time

```python
# ❌ This runs expensive_setup() when the module is imported:
@expensive_setup()
def my_function():
    ...

# The decorator factory runs immediately at import time — be careful with
# decorators that do I/O, DB calls, or heavy computation in their factory.
# If the DB isn't available at import time, the entire module fails to load.
```

✅ Fix: keep decorator factories lightweight. Move expensive setup into the `wrapper` (lazy, runs at call time) or use `@cached_property` to defer initialization.

---

<a id="gotcha-missing-return-value"></a>
## Gotcha: Missing Return Value

```python
# ❌ Silently swallows the return value — caller gets None:
def logger_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)    # ← forgot 'return'!
    return wrapper

# ✅ Always return the result:
def logger_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)  # ← return!
    return wrapper
```

⚠️ **Common mistake:** This is silent — no error, just `None` where a value is expected. Use `try/finally` when you need code after the call: `finally` runs even if the function raises, and you still `return` in the `try` block.

---

<a id="gotcha-methods-and-self"></a>
## Gotcha: Methods and self

```python
# Applying a decorator to a class method — does it work?
def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

class MyClass:
    @my_decorator
    def my_method(self):   # 'self' comes through *args — works fine
        pass
```

Standard decorators using `*args, **kwargs` work fine with methods — `self` is just the first positional argument. The issue arises when your decorator tries to access `self` explicitly inside `wrapper`, or when using descriptors. In those cases, use the `wrapt` library which handles the descriptor protocol correctly.

🔍 **Good to know:** `@classmethod` and `@staticmethod` must be the **innermost** decorators (closest to the `def`). Applying them on top of another decorator breaks the descriptor protocol. Always: `@your_decorator` first (outer), then `@classmethod` / `@staticmethod` second (inner).

📝 **Practice:** [anti-patterns / fix decorator missing return and wraps →](./practice.md#q17--anti-patterns--fix-decorator-missing-return-and-wraps)

> [↑ Back to Top](#top)

---

<a id="15-functools-utilities-cache-cached_property-singledispatch"></a>
# 15. functools Utilities — cache, cached_property, singledispatch

These are the high-value tools in `functools` beyond `wraps`. They're decorators Python gives you for free — you don't write the wrapper, you just apply the label. Each one solves a specific, common problem.

---

<a id="functoolslru_cache-and-functoolscache"></a>
## functools.lru_cache and functools.cache

`lru_cache` memoizes a function — caches its return value keyed by arguments. On cache hit, the function body doesn't run at all. **LRU** (Least Recently Used) eviction drops the oldest entries when the cache is full.

`functools.cache` (Python 3.9+) is `lru_cache(maxsize=None)` — same behaviour, no size limit, simpler syntax.

```python
import functools

@functools.lru_cache(maxsize=128)    # keeps the 128 most recently used results
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

fibonacci(50)             # computes once, caches all sub-results
fibonacci(50)             # instant — cache hit
fibonacci.cache_info()    # CacheInfo(hits=48, misses=51, maxsize=128, currsize=51)
fibonacci.cache_clear()   # flush the cache
```

```python
from functools import cache

@cache   # no size limit — grows until process exits
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

fibonacci(100)   # instant — each sub-result computed once, cached forever
```

**`cache` vs `lru_cache`:**

```
@cache                           @lru_cache(maxsize=128)
────────────────────────────── ────────────────────────────────────
No size limit                  Evicts oldest when maxsize reached
Slightly less memory overhead  Slightly more memory per entry
Simpler syntax                 More control over memory usage
Use when: input space bounded  Use when: memory budget matters
```

⚠️ **Common mistake — caching functions with mutable arguments:** `lru_cache` requires hashable arguments. Calling `fibonacci([1,2,3])` raises `TypeError: unhashable type: 'list'`. Convert mutable inputs to tuples before caching, or use a custom cache keying strategy.

---

<a id="functoolscached_property"></a>
## functools.cached_property

A regular `@property` re-runs its function every time you access the attribute. `@cached_property` runs once, then stores the result directly in the instance's `__dict__` — subsequent accesses bypass the descriptor entirely (just a dict lookup).

```python
from functools import cached_property
import math

class Circle:
    def __init__(self, radius):
        self.radius = radius

    @cached_property
    def area(self):
        print("computing area...")         # only prints on first access
        return math.pi * self.radius ** 2

    @cached_property
    def circumference(self):
        return 2 * math.pi * self.radius

c = Circle(5)
print(c.area)    # "computing area..." → 78.53...
print(c.area)    # no print — returns cached value from c.__dict__

c.__dict__       # {'radius': 5, 'area': 78.53...}  ← value stored there
```

**When to use:** computation is expensive, input won't change after creation, lazy evaluation is desired.

**How it works:** On first access, `cached_property` calls the function, stores the result in `instance.__dict__` under the same name. Instance `__dict__` takes priority over non-data descriptors — subsequent accesses go directly to the dict, bypassing the descriptor.

⚠️ **Common mistake — `cached_property` is NOT thread-safe:** Two threads accessing the property simultaneously may both compute it. For concurrent access, protect with a lock or use `@property` + explicit locking.

---

<a id="functoolssingledispatch"></a>
## functools.singledispatch

Python doesn't allow function overloading by type. `singledispatch` solves this — it routes to different implementations based on the **type of the first argument**.

```python
from functools import singledispatch

@singledispatch
def process(value):
    """Default — handles anything not specifically registered."""
    print(f"Processing unknown type: {type(value).__name__}")

@process.register(int)
def _(value):
    print(f"Integer: {value * 2}")

@process.register(str)
def _(value):
    print(f"String: {value.upper()}")

@process.register(list)
def _(value):
    print(f"List with {len(value)} items")

process(42)           # Integer: 84
process("hello")      # String: HELLO
process([1, 2, 3])    # List with 3 items
process(3.14)         # Processing unknown type: float
```

**Real production use — custom JSON serializer:**

```python
from functools import singledispatch
from datetime import datetime, date
from decimal import Decimal

@singledispatch
def to_json_value(obj):
    raise TypeError(f"Cannot serialize {type(obj)}")

@to_json_value.register(datetime)
def _(obj): return obj.isoformat()

@to_json_value.register(Decimal)
def _(obj): return float(obj)

@to_json_value.register(date)
def _(obj): return obj.isoformat()

# Usage:
json.dumps(data, default=to_json_value)
```

**`singledispatchmethod`** (Python 3.8+) — same idea for class methods:

```python
from functools import singledispatchmethod

class Processor:
    @singledispatchmethod
    def process(self, value):
        raise NotImplementedError

    @process.register(int)
    def _(self, value):
        return value * 2

    @process.register(str)
    def _(self, value):
        return value.upper()
```

🔍 **Good to know:** `singledispatch` dispatches on the type of the **first argument only**. For multi-argument dispatch, the `multipledispatch` third-party library handles this — but it's rarely needed in practice.

📝 **Practice:** [lru_cache on fibonacci →](./practice.md#q27--ch16--lru_cache-on-fibonacci) · [cached_property →](./practice.md#q28--cached_property)

> [↑ Back to Top](#top)

---

<a id="16-how-python-executes-decorators-the-full-mental-model"></a>
# 16. How Python Executes Decorators — The Full Mental Model

Understanding exactly when each layer runs — and what the name refers to at each moment — eliminates the confusion that trips up most developers when decorators behave unexpectedly.

```
IMPORT TIME (when module is loaded):
─────────────────────────────────────
1. def statements define function objects (don't execute the body)
2. @decorator lines run the decorator function → wrap and replace the name
3. Class bodies execute (methods are defined, decorators applied)

CALL TIME (when decorated function is called):
──────────────────────────────────────────────
4. wrapper() executes (the outermost layer)
5. wrapper calls func() → the next layer or original runs
6. results propagate back out
```

```python
import functools
print("Module loading:")

def timer(func):
    print(f"  timer: wrapping {func.__name__}")    # runs at import time
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"  timer: timing {func.__name__}")  # runs at call time
        return func(*args, **kwargs)
    return wrapper

@timer
def process():
    print("  Processing")

print("Calling:")
process()

# Output:
# Module loading:
#   timer: wrapping process
# Calling:
#   timer: timing process
#   Processing
```

**Full mental model — stacked decorators:**

```python
@A
@B
@C
def func(): ...

# AT IMPORT TIME (bottom-up):
step1 = C(func)    # C wraps func        → step1 is C's wrapper
step2 = B(step1)   # B wraps C's wrapper → step2 is B's wrapper
step3 = A(step2)   # A wraps B's wrapper → step3 is A's wrapper
func = step3       # name 'func' now points to A's wrapper

# AT CALL TIME: func() → A's wrapper → B's wrapper → C's wrapper → original
```

💡 **Hint:** This mental model explains why `@classmethod` must be the innermost decorator — Python needs to see a plain function to create the descriptor. If `@classmethod` is on the outside, it receives a wrapper object (not the function) and can't create the descriptor correctly.

📝 **Practice:** [full mental model / trace execution →](./practice.md#q21--full-mental-model--trace-python-decorator-execution)

> [↑ Back to Top](#top)

---

<a id="summary"></a>
# Summary

```
CONCEPT                    DESCRIPTION
──────────────────────────────────────────────────────────────────────
First-class functions      Functions are objects — pass, return, assign
Closure                    Inner function captures outer scope variables
Decorator                  Function that wraps another function
@syntax                    func = decorator(func) — at definition time
@functools.wraps           Preserves __name__, __doc__, __wrapped__
Decorator factory          Factory → Decorator → Wrapper (3 layers)
Class as decorator         __init__ takes func/config, __call__ wraps
Decorating a class         Applied to class itself (@dataclass, @singleton)
@property                  Getter/setter/deleter as computed attribute
@classmethod               Factory constructors — gets cls not self
@staticmethod              Utility — gets neither cls nor self
Stacking                   Bottom-up application, top-down execution
Async decorators           wrapper must be async if func is async
functools.lru_cache        Memoize with LRU eviction + size limit
functools.cache            Memoize with no size limit (Python 3.9+)
functools.cached_property  Compute once, cache on instance dict
functools.singledispatch   Route to implementation by argument type
```

---

<a id="navigation"></a>
# 🔁 Navigation

**[🏠 Back to Python Mastery README](../README.md)**

| | |
|---|---|
| ⬅ Prev Module | [09 — Logging & Debugging](../09_logging_debugging/theory.md) |
| ➡ Next Module | [11 — Generators & Iterators](../11_generators_iterators/theory.md) |

**This folder:**
[theory.md](./theory.md) · [cheetsheet.md](./cheetsheet.md) · [interview.md](./interview.md) · [practice.md](./practice.md)

**Subfolders:**
[01 — Class Decorators](./01_class_decorators/theory.md) · [02 — Production Patterns](./02_production_patterns/theory.md)

**Related modules:**
[04 — Functions (Closures)](../04_functions/02_closures_decorators/01_closures_theory.md) · [05 — OOP (Properties)](../05_oops/11_properties.md) · [11 — Generators & Iterators](../11_generators_iterators/theory.md) · [13 — Concurrency](../13_concurrency/theory.md)

**Jump to specific topics:**
[Decorator Factory (3-layer)](#6-decorators-with-arguments-decorator-factories) · [functools.wraps](#5-functoolswraps-preserving-identity) · [Stacking Order](#9-stacking-decorators-order-and-interaction) · [Async Decorators](#11-decorators-for-async-functions) · [lru_cache / cache](#functoolslru_cache-and-functoolscache) · [cached_property](#functoolscached_property) · [singledispatch](#functoolssingledispatch) · [Anti-Patterns](#14-anti-patterns-and-gotchas)
