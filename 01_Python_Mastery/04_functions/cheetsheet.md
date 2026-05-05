# ⚡ Functions — Cheatsheet

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     PYTHON FUNCTIONS — QUICK REFERENCE                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Basic Syntax

```python
def function_name(param1, param2):
    """Optional docstring."""
    # body
    return value

result = function_name(arg1, arg2)
```

```python
# No return statement → returns None implicitly
def no_return():
    print("hello")          # returns None

# Multiple return values → tuple under the hood
def min_max(lst):
    return min(lst), max(lst)   # actually returns (min, max)

low, high = min_max([3,1,4])    # tuple unpacking
```

---

## 📋 All 7 Parameter Types

```python
# 1. POSITIONAL — order matters
def f(a, b): ...
f(1, 2)            # a=1, b=2

# 2. KEYWORD — name matters, order doesn't
f(b=2, a=1)        # a=1, b=2

# 3. DEFAULT — value if not passed
def f(a, b=10): ...
f(5)               # a=5, b=10 (default)

# 4. *args — variable positionals → TUPLE inside function
def f(*args): print(args)
f(1, 2, 3)         # (1, 2, 3)

# 5. **kwargs — variable keywords → DICT inside function
def f(**kwargs): print(kwargs)
f(x=1, y=2)        # {'x': 1, 'y': 2}

# 6. KEYWORD-ONLY — must use name (after * or *args)
def f(a, *, b): ...
f(1, b=2)          # ✓
f(1, 2)            # ✗ TypeError

# 7. POSITIONAL-ONLY — must use position (before /)
def f(a, /, b): ...
f(1, 2)            # ✓
f(a=1, b=2)        # ✗ TypeError
```

**Complete ordering rule:**
```
def f(pos_only, /, normal, default=val, *args, kw_only, **kwargs):
     ←—————————————— positional ———————————→|←—— keyword ——→
```

---

## ⚠️ The 4 Big Gotchas

```python
# ── GOTCHA 1: Mutable Default Argument ──────────────────────────────────
def bad(items=[]):           # [] created ONCE at definition time!
    items.append(1)
    return items

bad()    # [1]
bad()    # [1, 1]  ← same list reused!

# ✅ Fix:
def good(items=None):
    if items is None: items = []   # fresh list every call
    items.append(1)
    return items

# ── GOTCHA 2: Late Binding Closure ──────────────────────────────────────
funcs = [lambda: i for i in range(5)]
funcs[0]()    # 4 ← NOT 0! All see i=4 (loop's final value)

# ✅ Fix:
funcs = [lambda i=i: i for i in range(5)]
funcs[0]()    # 0 ✓

# ── GOTCHA 3: func vs func() ─────────────────────────────────────────────
result = my_func      # stores FUNCTION OBJECT — nothing runs!
result = my_func()    # CALLS function — runs and stores result

# ── GOTCHA 4: global assignment trap ────────────────────────────────────
x = 10
def f():
    x += 1    # UnboundLocalError! Python sees assignment → treats as local
              # Local x never defined → error when trying to read it

# ✅ Fix:
def f():
    global x
    x += 1
```

---

## 🔭 Scope — LEGB Rule

```
L → Local       (current function)           searched first
E → Enclosing   (outer function if nested)
G → Global      (module level)
B → Built-in    (Python's builtins)          searched last
```

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print(x)        # "local"  — L found
    def inner2():
        print(x)        # "enclosing"  — L not found, E found
    inner()
    inner2()

# Modifying outer scopes:
count = 0
def inc():
    global count        # modify module-level variable
    count += 1

def outer():
    n = 0
    def inner():
        nonlocal n      # modify outer function's variable
        n += 1
    inner()
    return n            # 1
```

---

## 🔑 Lambda Functions

```python
# Syntax: lambda params: expression (auto-returned)
square     = lambda x: x**2
add        = lambda x, y: x + y
greet      = lambda name: f"Hello, {name}"
conditional = lambda x: "even" if x%2==0 else "odd"

# With sorted():
students = [{"name":"Bob","gpa":8.5}, {"name":"Ali","gpa":9.2}]
sorted(students, key=lambda s: s["gpa"])           # sort by gpa
sorted(students, key=lambda s: s["name"])          # sort by name
sorted(students, key=lambda s: s["gpa"], reverse=True)  # descending

# With map() and filter():
nums = [1,2,3,4,5,6]
list(map(lambda x: x**2, nums))         # [1,4,9,16,25,36]
list(filter(lambda x: x%2==0, nums))    # [2,4,6]
```

---

## 🎭 Closures

```python
def make_multiplier(factor):
    def multiply(x):
        return x * factor    # captures 'factor' from outer scope
    return multiply          # return function, not result!

double = make_multiplier(2)
double(5)    # 10

# Inspect closure:
double.__closure__[0].cell_contents    # 2

# With nonlocal to modify:
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

counter = make_counter()
counter()    # 1
counter()    # 2
```

---

## 🎨 [Decorators](../10_decorators/theory.md)

```python
from functools import wraps

# Basic decorator:
def my_decorator(func):
    @wraps(func)               # ALWAYS include — preserves __name__, __doc__
    def wrapper(*args, **kwargs):
        # before
        result = func(*args, **kwargs)
        # after
        return result          # ALWAYS return the result!
    return wrapper

@my_decorator
def my_func(): ...
# Equivalent to: my_func = my_decorator(my_func)

# Decorator with arguments (3 layers):
def repeat(times):             # layer 1: gets decorator args
    def decorator(func):       # layer 2: gets function
        @wraps(func)
        def wrapper(*a, **kw): # layer 3: runs each call
            for _ in range(times):
                result = func(*a, **kw)
            return result
        return wrapper
    return decorator

@repeat(3)
def say_hi(): print("Hi!")
# Equivalent to: say_hi = repeat(3)(say_hi)

# Stacking — applied bottom-up, executed top-down:
@bold       # applied second (outermost)
@italic     # applied first (innermost)
def text(): ...
# Equivalent to: text = bold(italic(text))
```

---

## 🔄 Recursion

```python
# Template:
def recursive(n):
    if n == BASE_CASE:    # ← MUST have base case!
        return BASE_VALUE
    return recursive(SMALLER_PROBLEM)

# Factorial:
def factorial(n):
    if n <= 1: return 1
    return n * factorial(n-1)

# Fibonacci (slow without cache):
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n < 2: return n
    return fib(n-1) + fib(n-2)

# Recursion limit:
import sys
sys.getrecursionlimit()      # 1000 (default)
sys.setrecursionlimit(5000)  # increase (use carefully!)
```

---

## ⚙️ Generator Functions

```python
def gen_squares(n):
    for x in range(n):
        yield x**2        # pause, send value, resume on next()

g = gen_squares(5)        # creates generator — nothing runs yet
next(g)    # 0
next(g)    # 1
next(g)    # 4
list(g)    # [9, 16]  ← remaining values

# Generator expression (compact):
gen = (x**2 for x in range(10))

# Memory: list=[...all...], generator=one-at-a-time
```

---

## 📦 functools Essentials

```python
from functools import lru_cache, partial, wraps, reduce

# lru_cache — memoize expensive pure functions:
@lru_cache(maxsize=128)
def expensive(n):
    ...    # computed once per unique n
expensive.cache_info()    # hits, misses, maxsize, currsize
expensive.cache_clear()   # reset cache

# partial — pre-fill arguments:
from functools import partial
power = lambda base, exp: base ** exp
square = partial(power, exp=2)
cube   = partial(power, exp=3)
square(5)    # 25
cube(3)      # 27

# reduce — fold a sequence:
from functools import reduce
reduce(lambda acc, x: acc + x, [1,2,3,4,5])    # 15
reduce(lambda acc, x: acc * x, [1,2,3,4,5])    # 120
```

---

## 📝 Type Annotations

```python
from typing import Optional, List, Dict, Tuple, Union, Callable

def add(a: int, b: int) -> int: ...
def greet(name: str) -> str: ...
def find(id: int) -> Optional[str]: ...      # str or None
def process(items: List[int]) -> int: ...
def lookup() -> Dict[str, int]: ...
def range_of(lst: List[int]) -> Tuple[int, int]: ...
def either(x: Union[str, int]) -> str: ...
def apply(f: Callable[[int], int], x: int) -> int: ...

# Python 3.10+ shorthand:
def find(id: int) -> str | None: ...
def either(x: str | int) -> str: ...

# Annotations are HINTS — not enforced at runtime!
```

---

## 📖 Docstring Format (Google Style)

```python
def divide(a: float, b: float) -> float:
    """
    Divide a by b.

    Args:
        a: Numerator.
        b: Denominator. Must not be zero.

    Returns:
        The result of a / b.

    Raises:
        ZeroDivisionError: If b is zero.

    Example:
        >>> divide(10, 2)
        5.0
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b
```

---

## 🏁 Function Design Quick Rules

```
✓  One function → one responsibility
✓  Prefer return over print
✓  Use None for mutable defaults
✓  Always @wraps(func) in decorators
✓  Base case first in recursion
✓  Use generators for large data
✓  lru_cache only on pure functions
✓  is None, not == None
✗  Avoid global state
✗  Avoid side effects when possible
✗  Avoid > 3-4 parameters (use dict/object)
✗  Avoid mutable default arguments
```

---

## 🧭 When to Use What

```
Regular def        → any reusable logic
Lambda             → short inline expression (sort keys, map/filter)
Closure            → stateful function, no class needed
Decorator          → add behavior without changing function
Recursion          → tree/graph problems, divide & conquer
Generator          → large/infinite sequences, streaming data
lru_cache          → expensive pure function called repeatedly
partial            → specialize a general function
*args/**kwargs     → flexible API, decorator wrappers
keyword-only (*)   → force explicit, self-documenting calls
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.py](./practice.py) |
| ⬅️ Data Types | [../03_data_types/cheetsheet.md](../03_data_types/cheetsheet.md) |
| ➡️ OOP | [../05_oops/theory.md](../05_oops/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Interview Q&A](./interview.md)
