# 🎁 Decorators — Theory

> *"A decorator is a function that takes a function, wraps new behavior around it,*
> *and returns the enhanced version. One of Python's most elegant ideas."*

> 📝 **Practice:** [Q77 · explain-decorators](../python_practice_questions_100.md#q77--interview--explain-decorators) · [Q94 · debug-decorator](../python_practice_questions_100.md#q94--debug--debug-decorator)

---

## 🎬 The Problem That Made Decorators Inevitable

It's sprint review day. Your team just shipped a payment service with 40 endpoints. Now the product manager says:

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

## 📦 Chapter 1: Functions Are First-Class Objects

Before decorators make sense, you need to deeply understand this:

**In Python, functions are objects — like integers, strings, or lists.**

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

**This is called "first-class functions"** — functions are citizens of the language, not special syntax.

---

## 🔒 Chapter 2: Closures — The Engine Inside Decorators

A **[closure](../04_functions/theory.md#closure-cell-internals--how-captured-variables-actually-work)** is a function that captures variables from its enclosing scope, even after that scope has finished executing.

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
A decorator wraps a function. The wrapper function needs to remember the original function to call it. That "remembering" is a closure.

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

## 🔬 Closure Internals — Where Captured Variables Live

When a closure captures a variable, Python creates a **cell object** on the heap.
The outer function's stack frame is destroyed on return, but the cell object survives.

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

This is why `c1` and `c2` from the counter example above have independent state —
they each close over a different cell.

**Why `nonlocal` works:**

`nonlocal count` tells the inner function:
"Don't create a new local `count` — modify the existing cell object."
Both inner functions sharing the same cell will see each other's updates.

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

---

## 🎁 Chapter 3: Your First Decorator — Manual Form

A decorator is just a function that:
1. Takes a function as its argument
2. Defines a wrapper function inside
3. The wrapper adds behavior before/after calling the original
4. Returns the wrapper

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

**Memory model:**
```
Before decoration:
  greet ──→ <function greet at 0x100>

After  greet = my_decorator(greet):
  greet ──→ <function wrapper at 0x200>  ← now points to wrapper
              └── closure contains: func ──→ <function greet at 0x100>
```

---

## ✨ Chapter 4: The `@` Syntax — Syntactic Sugar

The `@` symbol is purely syntactic sugar. These two are **identical**:

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

The `@decorator` line runs **at definition time**, not at call time. By the time you call `greet("Alice")`, the name `greet` already refers to the wrapper.

**Multiple decorators — order matters (applied bottom-up, run top-down):**

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

---

## 🏷️ Chapter 5: `functools.wraps` — Preserving Identity

Without `@wraps`, your wrapper loses the original function's metadata:

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
- Help systems (`help(greet)` shows wrapper's docs)
- Logging (logs show `wrapper` not `greet`)
- Debugging tools
- `inspect.signature(greet)` shows wrapper's signature

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

print(greet.__name__)   # 'greet'           ← correct
print(greet.__doc__)    # 'Greet someone'   ← correct
print(greet.__wrapped__)  # original function ← @wraps adds this too
```

**Rule: Every wrapper function should have `@functools.wraps(func)`. No exceptions.**

> 📝 **Practice:** [Q30 · functools-wraps](../python_practice_questions_100.md#q30--thinking--functools-wraps)

---

## ⚙️ Chapter 6: Decorators with Arguments — Decorator Factories

What if you want `@retry(max_attempts=3)` instead of just `@retry`? You need a **decorator factory** — a function that takes arguments and *returns* a decorator.

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
retry(max_attempts=3)           ← LEVEL 1: factory — takes config, returns decorator
  └── decorator(func)           ← LEVEL 2: decorator — takes function, returns wrapper
        └── wrapper(*args, **kwargs)  ← LEVEL 3: wrapper — runs each time func is called
```

**The call chain when function is called:**
```
retry(max_attempts=5)   → returns decorator
decorator(fetch_data)   → returns wrapper  (at @-decoration time)
wrapper(url)            → runs each time you call fetch_data(url)
```

> 📝 **Practice:** [Q32 · parametrized-decorator](../python_practice_questions_100.md#q32--design--parametrized-decorator)

---

## 🏭 Chapter 7: Class-Based Decorators

You can also implement a decorator as a class by defining `__init__` and `__call__`:

```python
import functools

class retry:
    def __init__(self, max_attempts=3):
        self.max_attempts = max_attempts

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

**Class decorators are useful when the decorator needs to maintain state across calls:**

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

---

## 🏷️ Chapter 8: Decorating Classes

Decorators can be applied to **classes**, not just functions:

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

**`@dataclass` is a built-in class decorator** (deep dive: [05_oops → Dataclasses](../05_oops/14_dataclasses.md#-the-basics)):

```python
from dataclasses import dataclass

@dataclass                  # ← class decorator: auto-generates __init__,
class Order:                #   __repr__, __eq__, __hash__ based on fields
    order_id: int
    user_id: int
    total: float
    status: str = "pending"

o = Order(1, 42, 99.99)
print(o)   # Order(order_id=1, user_id=42, total=99.99, status='pending')
```

---

## 🔑 Chapter 9: Built-in Decorators — @property, @classmethod, @staticmethod

Python ships three essential decorators for classes:

> 📝 **Practice:** [Q29 · decorators-basics](../python_practice_questions_100.md#q29--normal--decorators-basics)

### [`@property`](../05_oops/11_properties.md#-what-property-actually-is) — Computed attributes with validation

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
    def fahrenheit(self):                 # computed — no setter
        return self._celsius * 9/5 + 32

t = Temperature(25)
print(t.fahrenheit)   # 77.0
t.celsius = -300      # ValueError: Temperature -300°C below absolute zero
```

### [`@classmethod`](../05_oops/09_class_instance_static_methods.md#2️⃣-class-methods--classmethod-and-cls) — Factory constructors

```python
class Order:
    def __init__(self, order_id, items, total):
        self.order_id = order_id
        self.items = items
        self.total = total

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        """Alternative constructor from a dictionary."""
        return cls(
            order_id=data["id"],
            items=data["items"],
            total=sum(i["price"] for i in data["items"])
        )

    @classmethod
    def empty(cls) -> "Order":
        return cls(order_id=None, items=[], total=0.0)

order = Order.from_dict({"id": 1, "items": [{"price": 9.99}]})
```

### [`@staticmethod`](../05_oops/09_class_instance_static_methods.md#3️⃣-static-methods--staticmethod) — Utility functions on the class

```python
class Order:
    @staticmethod
    def validate_status(status: str) -> bool:
        """Doesn't need self or cls — pure utility function."""
        return status in {"pending", "processing", "shipped", "delivered", "cancelled"}

Order.validate_status("shipped")   # True
```

**Comparison:**
```
Method type         First param    Can access     Called via
──────────────────────────────────────────────────────────────
Regular method      self           instance       instance.method()
@classmethod        cls            class          Class.method() or instance.method()
@staticmethod       (none)         nothing        Class.method() or instance.method()
```

---

## 🔄 Chapter 10: Stacking Decorators — Order and Interaction

When you stack decorators, order matters. A critical rule:

**Applied bottom-up. Executed top-down.**

```python
@timer          # applied third (outermost wrapper)
@logger         # applied second
@retry(3)       # applied first (innermost wrapper, closest to original)
def fetch_data(url):
    ...


# Equivalent to:
fetch_data = timer(logger(retry(3)(fetch_data)))
```

> 📝 **Practice:** [Q31 · stacked-decorators](../python_practice_questions_100.md#q31--logical--stacked-decorators)


**Execution order when `fetch_data(url)` is called:**

```
timer's before-code    (outermost)
  logger's before-code
    retry's logic
      original fetch_data(url)
    retry handles exception if needed
  logger's after-code
timer's after-code     (outermost)
```

**Practical example — order matters for logging and timing:**

```python
# ✅ CORRECT: timer wraps logger — you time the whole thing including logging overhead
@timer
@logger
def process():
    ...

# ❌ Usually WRONG: logger wraps timer — the log sees the timed wrapper, not the real function
@logger
@timer
def process():
    ...
```

**A real trap — `@functools.wraps` doesn't fix all introspection:**

```python
@logger
@timer
def process():
    """Process something."""
    ...

# Even with @wraps everywhere, the stacking changes behavior:
# logger's wrapper is the outermost — what the outside world sees
# timer's wrapper is inside logger
```

---

## 🏗️ Chapter 11: Production Decorator Patterns

### Timing

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
```

### Retry with Exponential Backoff

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
                    wait *= backoff
        return wrapper
    return decorator

@retry(max_attempts=5, delay=0.5, backoff=2.0, exceptions=(ConnectionError,))
def fetch_user(user_id):
    return db.get(user_id)
```

### Memoization / Cache

```python
import functools

# Built-in — use this:
@functools.lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Custom with TTL:
import time

def ttl_cache(ttl_seconds=60):
    def decorator(func):
        cache = {}

        @functools.wraps(func)
        def wrapper(*args):
            now = time.time()
            if args in cache:
                result, ts = cache[args]
                if now - ts < ttl_seconds:
                    return result
            result = func(*args)
            cache[args] = (result, now)
            return result
        return wrapper
    return decorator

@ttl_cache(ttl_seconds=300)   # cache for 5 minutes
def get_config(key):
    return config_service.fetch(key)
```

---

### `functools.cache` — Simpler Unlimited Cache (Python 3.9+)

`functools.cache` is `lru_cache(maxsize=None)` with a cleaner name.
No size limit — cached forever until the process exits.

```python
from functools import cache

@cache
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

fibonacci(100)   # instant — each sub-result computed once, cached forever

# Check cache stats:
fibonacci.cache_info()    # CacheInfo(hits=..., misses=..., maxsize=None, currsize=...)
fibonacci.cache_clear()   # clear the cache
```

**`cache` vs `lru_cache`:**

```
@cache                           @lru_cache(maxsize=128)
─────────────────────────────── ───────────────────────────────────
No size limit                   Evicts oldest when maxsize reached
Uses less memory overhead       Slightly more memory per entry
Simpler syntax                  More control
Use when: unlimited is fine     Use when: memory budget matters
```

---

### `functools.cached_property` — Compute Once, Cache on Instance

A regular `@property` re-runs its function every time you access it.
`@cached_property` runs once, then stores the result on the instance itself.

```python
from functools import cached_property
import math

class Circle:
    def __init__(self, radius):
        self.radius = radius

    @cached_property
    def area(self):
        print("computing area...")
        return math.pi * self.radius ** 2

    @cached_property
    def circumference(self):
        return 2 * math.pi * self.radius

c = Circle(5)
print(c.area)   # "computing area..." then 78.53...
print(c.area)   # no print — returns cached value from c.__dict__
print(c.area)   # same — always cached after first access
```

**How it works:**
On first access, `cached_property` calls the function, then stores the result directly in `instance.__dict__` under the same name. Since instance `__dict__` takes priority over descriptors for non-data descriptors, subsequent accesses bypass the descriptor entirely — just a dict lookup.

```python
c = Circle(5)
c.area          # computes and stores in c.__dict__['area']
c.__dict__       # {'radius': 5, 'area': 78.53...}  ← value is there
```

**When to use it:**
Use `@cached_property` when:
- The computation is expensive (DB query, complex math, parsing)
- The input (object attributes) won't change after creation
- You want lazy evaluation — don't compute until needed

**Note:** `cached_property` is NOT thread-safe. For concurrent access, use `@property` with explicit locking or `lru_cache`.

---

### `functools.singledispatch` — Function Overloading by Type

In Python you can't define two functions with the same name and different types.
`singledispatch` solves this — it routes to different implementations based on the type of the first argument.

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

**Register multiple types at once (Python 3.7+):**

```python
@process.register(float)
@process.register(complex)
def _(value):
    print(f"Numeric: {value}")
```

**Real use case — serialization:**

```python
from functools import singledispatch
import json
from datetime import datetime, date
from decimal import Decimal

@singledispatch
def to_json_value(obj):
    raise TypeError(f"Cannot serialize {type(obj)}")

@to_json_value.register(datetime)
def _(obj):
    return obj.isoformat()

@to_json_value.register(Decimal)
def _(obj):
    return float(obj)

@to_json_value.register(date)
def _(obj):
    return obj.isoformat()
```

**`singledispatchmethod`** — for methods on a class (Python 3.8+):

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

### Input Validation

```python
def validate(**type_checks):
    """@validate(price=float, user_id=int) — raises TypeError on bad types."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import inspect
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
```

---

## ⚡ Chapter 12: Decorators for Async Functions

If you decorate an async function, your wrapper must also be async:

```python
import functools, asyncio

def async_timed(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):       # ← async wrapper for async func!
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

---

## 🧩 Chapter 13: Decorators with Optional Arguments

The challenge: support `@retry` and `@retry(max=3)` with the same decorator.

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

---

## 🔍 Chapter 14: Introspection — Looking Inside Decorators

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
print(greet.__name__)       # 'greet'
print(greet.__doc__)        # 'Greet by name.'
print(greet.__wrapped__)    # <function greet> — original function
print(inspect.signature(greet))  # (name: str) -> str

# Unwrap the full stack:
print(inspect.unwrap(greet))    # original function, all wrappers removed
```

**`__wrapped__` is the key** — it lets tools like pytest, IDEs, and `inspect` see through decorators.

---

## ⚠️ Chapter 15: Anti-Patterns and Gotchas

### Gotcha 1 — Forgetting `@functools.wraps`

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

### Gotcha 2 — Mutable default in decorator factory

```python
# ❌ All decorated functions share the same results list:
def collect_results(results=[]):    # mutable default!
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            r = func(*args, **kwargs)
            results.append(r)
            return r
        return wrapper
    return decorator

# ✅ Fix: use None as default, create list inside:
def collect_results(results=None):
    if results is None:
        results = []
    ...
```

### Gotcha 3 — Decorator applied at import time

```python
# ❌ This runs expensive_setup() when the module is imported:
@expensive_setup()
def my_function():
    ...

# The decorator factory runs immediately — be careful with decorators
# that do I/O, DB calls, or heavy computation in their factory.
```

### Gotcha 4 — Not passing return value through

```python
# ❌ Swallows the return value:
def logger_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)    # ← forgot 'return'!
    return wrapper

# ✅ Always return:
def logger_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)  # ← return!
    return wrapper
```

### Gotcha 5 — Decorating a class method without accounting for `self`

```python
# ❌ Works for functions, breaks for methods:
def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

class MyClass:
    @my_decorator
    def my_method(self):   # ← 'self' comes through *args — actually fine!
        pass

# Actually this works — *args captures self automatically.
# The issue arises with descriptors or when you need to access self inside wrapper.
```

---

## 🧠 Chapter 16: How Python Executes Decorators — The Full Mental Model

Understanding the execution timeline:

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
print("Module loading:")

def timer(func):
    print(f"  Wrapping {func.__name__}")    # runs at import time
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"  Timing {func.__name__}")  # runs at call time
        return func(*args, **kwargs)
    return wrapper

@timer
def process():
    print("  Processing")

print("Calling:")
process()

# Output:
# Module loading:
#   Wrapping process
# Calling:
#   Timing process
#   Processing
```

---

## 🔥 Summary

```
CONCEPT                 DESCRIPTION
─────────────────────────────────────────────────────────────────────
First-class functions   Functions are objects — pass, return, assign
Closure                 Inner function captures outer scope variables
Decorator               Function that wraps another function
@syntax                 func = decorator(func) — at definition time
@functools.wraps        Preserves __name__, __doc__, __wrapped__
Decorator factory       Function → Decorator → Wrapper (3 layers)
Class decorator         __init__ takes func/config, __call__ wraps
Class-level decorator   Applied to classes (@dataclass, @singleton)
@property               Getter/setter/deleter as computed attribute
@classmethod            Factory constructors — gets cls not self
@staticmethod           Utility — gets neither cls nor self
Stacking                Bottom-up application, top-down execution
Async decorators        wrapper must be async if func is async
```

---

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🏭 Pattern Library | [decorator_patterns.md](./decorator_patterns.md) |
| ➡️ Next | [11 — Iterators & Generators](../11_iterators_generators/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Logging Debugging — Interview Q&A](../09_logging_debugging/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Decorator Patterns](./decorator_patterns.md) · [Interview Q&A](./interview.md)
