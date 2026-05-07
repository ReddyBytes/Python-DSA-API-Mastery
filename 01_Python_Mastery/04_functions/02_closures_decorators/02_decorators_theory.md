# Decorators — The Complete Guide

A decorator is a function that takes a function, wraps it with extra behavior, and returns the enhanced version — the `@` syntax is just shorthand for `func = decorator(func)`.

---

## 📌 Learning Priority

**Must Learn:** decorator anatomy · @syntax as sugar · functools.wraps · timing/logging decorators

**Should Learn:** decorators with arguments (3 layers) · stacking decorators · execution order · retry/validate decorators

**Good to Know:** class-based decorators · preserving function metadata · parameterized class decorators

**Reference:** `functools.wraps` source · `__wrapped__` attribute

---

## Chapter 1: Decorator Anatomy — Building One From Scratch

A decorator is like a gift wrapper. The gift (original function) stays the same inside. The wrapper adds the bow and the paper. The recipient (caller) only sees the wrapped version — same shape, new behavior.

### Step-by-step: 3-function structure

```python
# Step 1: write the decorator (the outer function)
def my_decorator(func):             # ← receives the original function

    # Step 2: define the wrapper (the replacement function)
    def wrapper(*args, **kwargs):
        print("Before the call")    # ← extra behavior added before
        result = func(*args, **kwargs)  # ← call the original
        print("After the call")     # ← extra behavior added after
        return result               # ← pass the result through

    # Step 3: return the wrapper
    return wrapper                  # ← caller will use this instead
```

### Without @syntax (explicit form)

```python
def greet(name):
    return f"Hello, {name}"

greet = my_decorator(greet)         # ← manually wrapping

print(greet("Alice"))
# Before the call
# After the call
# Hello, Alice
```

### With @syntax (shorthand)

```python
@my_decorator                       # ← exactly equivalent to: greet = my_decorator(greet)
def greet(name):
    return f"Hello, {name}"

print(greet("Alice"))               # same output
```

The `@` line is evaluated at function definition time. Python immediately calls `my_decorator(greet)` and rebinds the name `greet` to whatever the decorator returns.

### Flow diagram

```
DECORATION TIME (when Python reads the @line):

  original greet ──→ my_decorator() ──→ wrapper function
                                              │
                          greet now points to ┘

CALL TIME (when you call greet("Alice")):

  greet("Alice")
      │
      ▼
  wrapper("Alice")          ← this runs
      │  calls func("Alice")
      │      │
      │      ▼
      │  original greet runs
      │      │
      │  result returned
      │
      ▼
  wrapper returns result
```

---

## Chapter 2: The @wraps Problem

Without `@wraps`, your decorator lies about its identity. `func.__name__` returns `'wrapper'`, not the original name. This breaks `help()`, logging, and debugging tools.

### Before — broken identity

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name):
    """Say hello to someone."""
    return f"Hello, {name}"

print(greet.__name__)    # wrapper       ← wrong
print(greet.__doc__)     # None          ← lost
help(greet)              # shows wrapper's signature, not greet's
```

### After — fixed with @wraps

```python
import functools

def my_decorator(func):
    @functools.wraps(func)              # ← add this line, always
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name):
    """Say hello to someone."""
    return f"Hello, {name}"

print(greet.__name__)    # greet        ← correct
print(greet.__doc__)     # Say hello to someone.
print(greet.__wrapped__) # <function greet at 0x...>  ← points to original
```

### What `@functools.wraps` copies

`functools.wraps` copies these attributes from the original function to the wrapper:

| Attribute | What it holds |
|---|---|
| `__name__` | function name (`"greet"`) |
| `__qualname__` | qualified name (`"module.greet"`) |
| `__doc__` | docstring |
| `__annotations__` | type hints |
| `__module__` | module where defined |
| `__dict__` | any custom attributes |
| `__wrapped__` | reference to the original (added by wraps) |

**Production rule: always use `@functools.wraps` in every decorator. No exceptions.**

---

## Chapter 3: Decorators With Arguments — The 3-Layer Pattern

To pass arguments TO a decorator, you need one extra layer: a function that accepts the arguments and returns a decorator.

```
@retry(max_attempts=3)
def call_api(): ...

# is equivalent to:
call_api = retry(max_attempts=3)(call_api)
#              └─ layer 1 ─┘└─ layer 2 ─┘└─ layer 3: wrapper called on each use ─┘
```

### The 3 layers

```python
import functools
import time

def retry(max_attempts=3, delay=0.1):          # LAYER 1: argument receiver
    def decorator(func):                        # LAYER 2: actual decorator
        @functools.wraps(func)
        def wrapper(*args, **kwargs):           # LAYER 3: wrapper (runs each call)
            last_error = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    print(f"Attempt {attempt}/{max_attempts} failed: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise last_error                    # ← re-raise after all attempts fail
        return wrapper
    return decorator
```

### Usage

```python
@retry(max_attempts=3, delay=0.5)
def fetch_data(url):
    # simulating flaky network
    import random
    if random.random() < 0.7:
        raise ConnectionError("Network timeout")
    return f"data from {url}"
```

### Visualizing the 3 layers

```
retry(max_attempts=3)         ← layer 1 called at decoration time
      │
      returns decorator        ← layer 2: a plain decorator
               │
               decorator(fetch_data)  ← layer 2 called at decoration time
                        │
                        returns wrapper  ← layer 3: what fetch_data is now
                                 │
                                 wrapper(url)  ← layer 3 called on each fetch_data() call
```

---

## Chapter 4: Stacking Multiple Decorators

Stacking `@decorators` is like dressing in layers — the innermost decorator (closest to `def`) wraps first, the outermost wraps last. But calling runs outermost first.

```python
@bold
@italic
def hello():
    return "hello"

# equivalent to:
hello = bold(italic(hello))
```

### Decoration order vs call order

```
DECORATION ORDER (bottom-up, at definition time):
  italic wraps hello first  → italic_hello
  bold wraps italic_hello   → bold_italic_hello

CALL ORDER (top-down, at call time):
  bold's wrapper runs first
      calls italic's wrapper
          calls original hello
          returns "hello"
      italic wraps → "<i>hello</i>"
  bold wraps → "<b><i>hello</i></b>"
```

### Concrete example

```python
import functools

def bold(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return f"<b>{func(*args, **kwargs)}</b>"
    return wrapper

def italic(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return f"<i>{func(*args, **kwargs)}</i>"
    return wrapper

@bold
@italic
def hello():
    return "hello"

print(hello())    # <b><i>hello</i></b>
```

### ASCII diagram

```
              ┌─── bold wrapper ─────────────────────────────┐
              │    ┌─── italic wrapper ──────────────────┐   │
              │    │    ┌─── original hello ──────────┐  │   │
call hello()  │    │    │  return "hello"              │  │   │
              │    │    └─────────────────────────────-┘  │   │
              │    │  wraps in <i>...</i>                  │   │
              │    └─────────────────────────────────────--┘   │
              │  wraps in <b>...</b>                            │
              └────────────────────────────────────────────────┘
                result: "<b><i>hello</i></b>"
```

---

## Chapter 5: Real-World Decorator Patterns

### 5.1 Timer — Measure Execution Time

```python
import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()          # ← high-resolution timer
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.4f}s")
        return result
    return wrapper

@timer
def slow_sum(n):
    return sum(range(n))

@timer
def fast_pow(base, exp):
    return base ** exp

slow_sum(1_000_000)     # slow_sum took 0.0412s
fast_pow(2, 100)        # fast_pow took 0.0000s
```

The function behavior is unchanged — `timer` only observes, never alters the result.

### 5.2 Retry — Resilient API Calls

```python
import functools
import time

def retry(max_attempts=3, delay=0.5, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    print(f"[retry] {func.__name__} attempt {attempt}/{max_attempts}: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.1, exceptions=(ConnectionError,))
def call_api(endpoint):
    import random
    if random.random() < 0.6:
        raise ConnectionError("timeout")
    return {"status": "ok", "endpoint": endpoint}
```

### 5.3 Cache / Memoize — Roll Your Own

```python
import functools

def memoize(func):
    cache = {}                              # ← captured by wrapper via closure
    @functools.wraps(func)
    def wrapper(*args):
        if args not in cache:
            print(f"  [cache miss] {func.__name__}{args}")
            cache[args] = func(*args)
        else:
            print(f"  [cache hit]  {func.__name__}{args}")
        return cache[args]
    return wrapper

@memoize
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(6))
# [cache miss] fibonacci(6)
# [cache miss] fibonacci(5)
# ... (misses on first call)
# [cache hit]  fibonacci(2)  ← hits on repeated sub-problems
```

Compare to `functools.lru_cache` — the stdlib version with size limits and thread safety:

```python
@functools.lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

Use `lru_cache` in production. Roll your own only when you need custom cache logic (TTL, per-user, distributed).

### 5.4 Validate Input — Type Checking

```python
import functools
import inspect

def validate_types(**expected_types):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # bind args to parameter names
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            for param_name, expected_type in expected_types.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    if not isinstance(value, expected_type):
                        raise TypeError(
                            f"{param_name} must be {expected_type.__name__}, "
                            f"got {type(value).__name__}"
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@validate_types(name=str, age=int)
def register_user(name, age):
    return f"Registered {name}, age {age}"

register_user("Alice", 30)       # "Registered Alice, age 30"
register_user("Bob", "thirty")   # TypeError: age must be int, got str
```

### 5.5 Logging Decorator

```python
import functools

def log_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_str = ", ".join(repr(a) for a in args)
        kwargs_str = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
        all_args = ", ".join(filter(None, [args_str, kwargs_str]))
        print(f"[LOG] Calling {func.__name__}({all_args})")
        result = func(*args, **kwargs)
        print(f"[LOG] {func.__name__} returned {result!r}")
        return result
    return wrapper

@log_calls
def add(a, b):
    return a + b

add(3, 5)
# [LOG] Calling add(3, 5)
# [LOG] add returned 8
```

---

## Chapter 6: Class-Based Decorators

When a decorator needs persistent state across calls (like a call counter), a class can be cleaner than a closure.

```python
import functools

class CallCounter:
    def __init__(self, func):
        functools.update_wrapper(self, func)   # ← equivalent of @wraps for classes
        self.func = func
        self.call_count = 0

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        print(f"[counter] {self.func.__name__} called {self.call_count}x")
        return self.func(*args, **kwargs)

@CallCounter
def process(data):
    return data.upper()

process("hello")    # [counter] process called 1x
process("world")    # [counter] process called 2x
print(process.call_count)   # 2  ← accessible as an attribute
```

### Class-based vs closure-based: when to use each

| | Closure-based | Class-based |
|---|---|---|
| State needed | yes (`nonlocal`) | yes (instance attributes) |
| Multiple pieces of state | gets messy | clean |
| Inspect state from outside | awkward | natural (`dec.count`) |
| Parameterized | add a layer | use `__init__` |
| Most decorators | preferred | use only when needed |

Class-based decorators are most useful when you need to inspect or reset the decorator's state from outside (e.g., `func.call_count = 0` in tests).

---

## Chapter 7: Common Mistakes

### Mistake 1: forgetting @functools.wraps

```python
def decorator(func):
    def wrapper(*args, **kwargs):         # ← no @wraps
        return func(*args, **kwargs)
    return wrapper

@decorator
def my_func():
    """Does something important."""
    pass

print(my_func.__name__)   # wrapper   ← breaks logging, help(), introspection
print(my_func.__doc__)    # None      ← docstring lost
```

Fix: always add `@functools.wraps(func)` above the `wrapper` definition.

### Mistake 2: calling decorator wrong — `@decorator()` vs `@decorator`

```python
# If your decorator takes NO arguments:
def simple_dec(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@simple_dec        # ← correct: no parentheses
def my_func(): pass

@simple_dec()      # ← TypeError: simple_dec() takes 1 argument but got 0
def my_func(): pass
```

```python
# If your decorator TAKES arguments:
def parameterized_dec(n):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

@parameterized_dec(3)    # ← correct: parentheses required
def my_func(): pass

@parameterized_dec       # ← wrong: parameterized_dec receives my_func, not a number
def my_func(): pass
```

### Mistake 3: wrong layer count for parameterized decorators

A plain decorator has 2 layers (decorator + wrapper). A parameterized decorator needs 3 layers (argument receiver + decorator + wrapper). Adding or removing a layer causes subtle bugs — the decorator returns a decorator instead of a function, or vice versa.

### Mistake 4: mutable default in decorator — shared state between calls

```python
def accumulate(func):
    results = []                    # ← defined once, shared across ALL calls
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        results.append(result)      # ← every call adds to the same list
        return results              # ← caller gets the growing list
    return wrapper

@accumulate
def double(n):
    return n * 2

print(double(1))   # [2]
print(double(2))   # [2, 4]   ← growing! caller 1's reference also changed
print(double(3))   # [2, 4, 6]
```

Fix: if you need per-call isolation, do not store state in the decorator scope. If you intend shared history, document it clearly.

---

## 🚀 Ready for Production? — Advanced Decorator Patterns

You now know the fundamentals. When you're ready to use decorators in real systems:

**[10_decorators — Production Patterns →](../../10_decorators/theory.md)**
- 15 battle-tested patterns: @circuit_breaker, @ttl_cache, @rate_limit, @timeout, @validate_types
- Class-based decorators with @dataclass
- Async decorator support
- Interview Q&A (junior / mid / senior)

---

**[← Closures](./01_closures_theory.md)** | **[Back to Functions](../theory.md)**

**Related:** [Practice Problems](./practice.md) · [Itertools & Functools](../03_itertools_functools/theory.md) · [Advanced Patterns →](../../10_decorators/theory.md)
