# 🎯 Decorators — Interview Questions

> *"Decorator questions test whether you understand functions as objects, closures,*
> *and how Python executes code at import time vs call time."*

---

## 📊 Question Map

```
LEVEL 1 — Junior (0–2 years)
  • What is a decorator?
  • @ syntax and manual equivalence
  • *args and **kwargs in wrappers
  • functools.wraps and why it matters

LEVEL 2 — Mid-Level (2–5 years)
  • Decorator factories (decorators with arguments)
  • Class-based decorators
  • Stacking order and execution model
  • @property / @classmethod / @staticmethod
  • Decorating async functions

LEVEL 3 — Senior (5+ years)
  • Decorators with optional arguments
  • Introspection and __wrapped__
  • Decorating classes
  • Production patterns (retry, cache, rate limit)
  • Descriptor protocol and how @property works internally
```

---

## 🟢 Level 1 — Junior Questions

---

### Q1: What is a decorator in Python?

**Weak answer:** "It modifies a function."

**Strong answer:**

> A decorator is a callable that takes a function as input, wraps additional behavior around it, and returns the enhanced version. In Python, functions are first-class objects — they can be passed as arguments and returned from other functions — which makes decorators possible.

```python
import functools

def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result}")
        return result
    return wrapper

@logged
def add(a, b):
    return a + b

add(2, 3)
# Calling add
# add returned 5
```

> The `@logged` line is exactly equivalent to `add = logged(add)`. It runs at **definition time**, not at call time.

---

### Q2: What does `@decorator` actually do under the hood?

**Strong answer:**

> `@decorator` is pure syntactic sugar. These two are **identical**:

```python
# With @ syntax:
@my_decorator
def greet(name):
    return f"Hello, {name}!"

# Exact equivalent:
def greet(name):
    return f"Hello, {name}!"
greet = my_decorator(greet)
```

> After the `@` line executes, the name `greet` no longer refers to the original function — it refers to whatever `my_decorator` returned. Usually a wrapper function.

---

### Q3: Why do we use `*args` and `**kwargs` in the wrapper?

**Weak answer:** "So it accepts any arguments."

**Strong answer:**

> The wrapper must be able to forward **any** arguments that the original function accepts, without needing to know what those arguments are at decorator-writing time. Using `*args, **kwargs` makes the decorator generic and reusable across functions with different signatures.

```python
def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):   # collects ALL positional and keyword args
        return func(*args, **kwargs)  # unpacks and forwards them unchanged
    return wrapper

@my_decorator
def create_order(user_id, items, discount=0):
    ...

@my_decorator
def greet(name):
    ...

# Same decorator works on both — wrapper transparently forwards arguments
```

---

### Q4: What is `functools.wraps` and why is it important?

**Weak answer:** "It copies the function name."

**Strong answer:**

> Without `@functools.wraps(func)`, the wrapper replaces the original function's metadata with its own. This breaks logging, `help()`, `inspect`, pytest, and any tool that reads `__name__` or `__doc__`.

```python
def without_wraps(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def with_wraps(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@without_wraps
def process():
    """Process data."""
    pass

print(process.__name__)   # 'wrapper'  ← broken: logs show 'wrapper' not 'process'
print(process.__doc__)    # None       ← docstring lost

@with_wraps
def process():
    """Process data."""
    pass

print(process.__name__)   # 'process'       ← correct
print(process.__doc__)    # 'Process data.' ← correct
print(process.__wrapped__)  # <function process> ← bonus: points to original
```

> `@functools.wraps` copies: `__name__`, `__qualname__`, `__doc__`, `__module__`, `__annotations__`, `__dict__`, and adds `__wrapped__`. **Always use it. No exceptions.**

---

## 🔵 Level 2 — Mid-Level Questions

---

### Q5: How do you write a decorator that accepts arguments?

**Weak answer:** "Add parameters to the decorator function."

**Strong answer:**

> A decorator with arguments requires **three levels**: a factory function (takes the config), a decorator (takes the function), and a wrapper (runs on each call). The `@` line calls the factory first.

```python
import functools, time

def retry(max_attempts=3, delay=1.0):
    """Level 1: Factory — takes config, returns decorator."""
    def decorator(func):
        """Level 2: Decorator — takes function, returns wrapper."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Level 3: Wrapper — runs on each call."""
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator

@retry(max_attempts=5, delay=0.5)
def fetch_data(url):
    ...
```

> **Call chain:** `retry(max_attempts=5)` returns `decorator` → `decorator(fetch_data)` returns `wrapper` → each call to `fetch_data(url)` runs `wrapper(url)`.

---

### Q6: What is the execution order when decorators are stacked?

**Strong answer:**

> Decorators are **applied bottom-up** (closest to the function first) but **execute top-down** (outermost runs first on each call).

```python
def A(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("A before")
        result = func(*args, **kwargs)
        print("A after")
        return result
    return wrapper

def B(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("B before")
        result = func(*args, **kwargs)
        print("B after")
        return result
    return wrapper

@A
@B
def process():
    print("original")

process()
# A before   ← A runs first (outermost)
# B before
# original
# B after
# A after    ← A finishes last

# Equivalent to: process = A(B(process))
```

---

### Q7: What is the difference between `@property`, `@classmethod`, and `@staticmethod`?

**Strong answer:**

```python
class Order:
    _tax_rate = 0.10   # class variable

    def __init__(self, total):
        self._total = total

    @property
    def total_with_tax(self):
        """Computed attribute — access like obj.total_with_tax (no call)."""
        return self._total * (1 + self._tax_rate)

    @total_with_tax.setter
    def total_with_tax(self, value):
        self._total = value / (1 + self._tax_rate)

    @classmethod
    def from_cents(cls, cents: int) -> "Order":
        """Alternative constructor — gets cls, can create instances."""
        return cls(total=cents / 100)

    @staticmethod
    def is_valid_amount(amount: float) -> bool:
        """Utility function — gets neither self nor cls."""
        return 0 < amount < 1_000_000

# Usage:
order = Order(100.0)
print(order.total_with_tax)          # 110.0  (property)
Order.from_cents(9999)               # classmethod — factory pattern
Order.is_valid_amount(99.99)         # staticmethod — pure utility
```

> - `@property` — computed attribute with optional setter/deleter
> - `@classmethod` — gets `cls`; used for factory constructors and alternative constructors
> - `@staticmethod` — gets nothing; utility functions that belong to the class logically

---

### Q8: How do you decorate an async function?

**Strong answer:**

> If the decorated function is async, the wrapper must also be async and use `await`:

```python
import functools, asyncio

def async_retry(max_attempts=3):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):      # ← async wrapper!
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)   # ← await the original
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(1)
        return wrapper
    return decorator

@async_retry(max_attempts=3)
async def fetch_user(user_id):
    return await db.get(user_id)
```

> **What breaks if you forget `async`/`await`:** The wrapper returns a coroutine object without executing it. The decorated function appears to succeed but returns `<coroutine>` instead of the actual value.

---

### Q9: What is a class-based decorator and when would you use it?

**Strong answer:**

> A class-based decorator implements `__init__` and `__call__`. It's useful when the decorator needs **persistent state across calls** that belongs to the decorator itself.

```python
import functools

class RateLimiter:
    def __init__(self, max_calls_per_second):
        self.max_calls = max_calls_per_second
        self.calls = []

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            now = time.time()
            self.calls = [t for t in self.calls if now - t < 1.0]
            if len(self.calls) >= self.max_calls:
                raise Exception("Rate limit exceeded")
            self.calls.append(now)
            return func(*args, **kwargs)
        return wrapper

limiter = RateLimiter(max_calls_per_second=5)

@limiter
def call_api(endpoint):
    ...
```

> Class-based decorators are also useful for call counters, circuit breakers, and any decorator that accumulates statistics.

---

## 🔴 Level 3 — Senior Questions

---

### Q10: Write a decorator that works both with and without arguments.

**Strong answer:**

> This requires detecting whether the decorator was called with arguments or applied directly. The trick is checking if `_func` was passed as the first argument.

```python
import functools

def retry(_func=None, *, max_attempts=3):
    """
    Usage:
      @retry               ← no arguments
      @retry()             ← empty parens
      @retry(max_attempts=5)  ← with arguments
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
        # Called as @retry — _func IS the decorated function
        return decorator(_func)
    # Called as @retry() or @retry(max_attempts=5)
    return decorator
```

---

### Q11: How does `@property` work internally (the descriptor protocol)?

**Strong answer:**

> `@property` is a descriptor — an object that implements `__get__`, `__set__`, and/or `__delete__`. When Python sees `obj.attr`, it checks if the class's attribute is a descriptor and calls `__get__` instead of returning the attribute directly.

```python
class property:   # simplified implementation
    def __init__(self, fget=None, fset=None, fdel=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self       # accessed on the class → return descriptor
        return self.fget(obj) # accessed on instance → call getter

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def setter(self, fset):
        return property(self.fget, fset, self.fdel)
```

> This is why `@property` without `@name.setter` creates a read-only attribute — `__set__` raises `AttributeError`.

---

### Q12: How do you design a production-grade retry decorator?

**Strong answer:**

```python
import functools, time, logging, random

logger = logging.getLogger(__name__)

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    jitter: float = 0.1,
    exceptions: tuple = (Exception,),
    on_retry=None,
):
    """
    Retry with exponential backoff and jitter.
    on_retry: optional callback(attempt, exc) called before each retry.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error("%s failed after %d attempts: %s",
                                     func.__name__, max_attempts, e)
                        raise
                    actual_wait = wait + random.uniform(0, jitter)
                    logger.warning("%s attempt %d/%d failed: %s — retrying in %.2fs",
                                   func.__name__, attempt, max_attempts, e, actual_wait)
                    if on_retry:
                        on_retry(attempt, e)
                    time.sleep(actual_wait)
                    wait *= backoff
        return wrapper
    return decorator

@retry(max_attempts=5, delay=0.5, backoff=2, exceptions=(ConnectionError, TimeoutError))
def fetch_from_api(endpoint):
    ...
```

> Key production considerations: **jitter** (prevents thundering herd when many services retry simultaneously), **specific exception types** (don't retry `ValueError` or `PermissionError`), **logging at each attempt**, and **on_retry callback** for metrics.

---

### Q13: How would you implement a decorator that adds type checking?

**Strong answer:**

```python
import functools, inspect

def enforce_types(func):
    """Validate that passed arguments match annotated types."""
    hints = func.__annotations__
    sig = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        for param_name, value in bound.arguments.items():
            if param_name in hints:
                expected = hints[param_name]
                if not isinstance(value, expected):
                    raise TypeError(
                        f"{func.__name__}(): '{param_name}' expected "
                        f"{expected.__name__}, got {type(value).__name__}"
                    )
        return func(*args, **kwargs)
    return wrapper

@enforce_types
def create_order(user_id: int, total: float, notes: str = ""):
    ...

create_order(1, 99.99)          # ✅
create_order("bad", 99.99)      # TypeError: 'user_id' expected int, got str
```

---

## ⚠️ Trap Questions

---

### Trap 1 — Missing `return` in wrapper

```python
def logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)   # ← forgot return!
    return wrapper

@logger
def get_total(order):
    return order.total

result = get_total(order)
print(result)   # None — the return value was swallowed!

# FIX:
def wrapper(*args, **kwargs):
    return func(*args, **kwargs)   # ← always return
```

---

### Trap 2 — Import time side effects in decorator factory

```python
# ❌ This opens a DB connection at import time:
def cached_in_db(table=db.connect("postgres://...").cursor()):   # runs immediately!
    def decorator(func):
        ...
    return decorator

# ✅ Lazy initialization:
def cached_in_db(dsn):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            conn = db.connect(dsn)   # ← connect at call time, not import time
            ...
        return wrapper
    return decorator
```

---

### Trap 3 — Async function decorated with sync wrapper

```python
# ❌ Wraps coroutine function in sync wrapper — calling it returns a coroutine object:
def logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):       # sync wrapper
        return func(*args, **kwargs)    # returns coroutine, doesn't await it!
    return wrapper

@logger
async def fetch():
    return await db.query()

result = await fetch()   # returns coroutine object, not the actual result!

# ✅ Detect and handle both:
def logger(func):
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

---

### Trap 4 — Decorator applied to a function changes its class binding

```python
class API:
    @timer   # ← applied to unbound function, before class is fully created
    def fetch(self):
        ...

# timer wraps fetch BEFORE self is bound. The wrapper receives self as first positional arg.
# This usually works because *args captures self, BUT:
# If timer does something like func.__name__ binding with assumptions about the call...
# Always test decorators on class methods, not just standalone functions.
```

---

### Trap 5 — Stacking order for `@functools.lru_cache` and `@staticmethod`

```python
# ❌ WRONG order:
class Calculator:
    @functools.lru_cache(maxsize=128)
    @staticmethod
    def compute(n):
        return n * 2

# lru_cache wraps staticmethod descriptor → descriptor is cached, not the function
# Raises: TypeError: unhashable type: 'staticmethod'

# ✅ CORRECT order (staticmethod outermost):
class Calculator:
    @staticmethod
    @functools.lru_cache(maxsize=128)
    def compute(n):
        return n * 2
```

---

## 🔥 Rapid-Fire Revision

```
Q: What is a closure?
A: An inner function that captures variables from its enclosing scope,
   even after the outer function has returned.

Q: What is @functools.wraps?
A: Copies __name__, __doc__, __qualname__, __annotations__ from wrapped
   function to wrapper. Also adds __wrapped__ pointing to original.

Q: What does __wrapped__ do?
A: Points to the original unwrapped function.
   inspect.unwrap() follows the __wrapped__ chain to the original.

Q: Three levels of a parametrized decorator?
A: factory(config) → decorator(func) → wrapper(*args, **kwargs)

Q: Bottom-up or top-down for stacking decorators?
A: Applied bottom-up (@B closer to function applied first).
   Executed top-down (@A outermost runs first when called).

Q: How do you make a decorator work on async functions?
A: Check asyncio.iscoroutinefunction(func) and return async wrapper if True.

Q: What does @property return when accessed on the class (not instance)?
A: Returns the property descriptor object itself.
   Only on instances does __get__ call the getter function.

Q: What is the descriptor protocol?
A: Objects with __get__, __set__, __delete__ are descriptors.
   Python calls these automatically on attribute access.
   @property, @classmethod, @staticmethod are all descriptors.

Q: When does decorator code run vs wrapper code?
A: Decorator code runs at IMPORT TIME (when @decorator is processed).
   Wrapper code runs at CALL TIME (each time the function is called).
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🏭 Pattern Library | [decorator_patterns.md](./decorator_patterns.md) |
| ➡️ Next | [11 — Iterators & Generators](../11_iterators_generators/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Decorator Patterns](./decorator_patterns.md) &nbsp;|&nbsp; **Next:** [Generators Iterators — Theory →](../11_generators_iterators/theory.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Decorator Patterns](./decorator_patterns.md)
