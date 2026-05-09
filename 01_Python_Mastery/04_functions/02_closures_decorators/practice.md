# 🎯 Closures & Decorators — Practice Problems

> 15 problems · Closures, factories, decorator internals, real-world patterns
> Write your answer in `practice_local.py` first, then use the dropdowns.

---

## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| [Q1](#q1) | Closure — make_multiplier factory | 🟢 |
| [Q2](#q2) | Closure — make_counter with shared state | 🟢 |
| [Q3](#q3) | Closure — make_adder + compose | 🟢 |
| [Q4](#q4) | Closure — late-binding bug (show it) | 🟡 |
| [Q5](#q5) | Closure — late-binding fix (wrapper fn) | 🟡 |
| [Q6](#q6) | Decorator — @logger (name + result) | 🟢 |
| [Q7](#q7) | Decorator — add @functools.wraps | 🟢 |
| [Q8](#q8) | Decorator — @timer (verify no behavior change) | 🟡 |
| [Q9](#q9) | Decorator — stack @timer + @logger, trace order | 🟡 |
| [Q10](#q10) | Decorator args — @retry(max_attempts=3) | 🟡 |
| [Q11](#q11) | Decorator args — @repeat(n) | 🟡 |
| [Q12](#q12) | Decorator args — @validate_input(min_val, max_val) | 🟡 |
| [Q13](#q13) | Decorator args — @cache_result(ttl_seconds) | 🔴 |
| [Q14](#q14) | Real-world — @rate_limit(calls_per_second) | 🔴 |
| [Q15](#q15) | Real-world — @singleton for classes | 🔴 |

---

<a id="q1"></a>

### Q1 · Closure — make_multiplier factory

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


**Problem:**
Write `make_multiplier(factor)` that returns a function. The returned function takes a number and multiplies it by `factor`. Create `double` and `triple` from the factory and verify them.

```python
def make_multiplier(factor):
    # your code here
    pass

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5))   # 10
print(triple(5))   # 15
print(double(7))   # 14
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Define an inner function inside `make_multiplier` that uses `factor` from the enclosing scope. Return the inner function (not its result — no parentheses on the return).

</details>

<details>
<summary>✅ Answer</summary>

```python
def make_multiplier(factor):
    def multiply(n):
        return n * factor    # ← factor captured from make_multiplier's scope
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))   # 10
print(triple(5))   # 15
print(double(7))   # 14
```

**Why:** Each call to `make_multiplier` creates a fresh closure cell for `factor`. `double` and `triple` are completely independent functions — each has its own cell holding its own value of `factor`.

</details>

---

<a id="q2"></a>

### Q2 · Closure — make_counter with shared state

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


**Problem:**
Write `make_counter()` that returns three functions: `increment`, `decrement`, and `reset`. All three share the same `count` variable. Each function should return the new count value.

```python
inc, dec, rst = make_counter()
print(inc())   # 1
print(inc())   # 2
print(dec())   # 1
print(rst())   # 0
print(inc())   # 1
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Declare `count = 0` inside `make_counter`. Each inner function needs `nonlocal count` before it modifies `count`. Return all three functions as a tuple.

</details>

<details>
<summary>✅ Answer</summary>

```python
def make_counter():
    count = 0

    def increment():
        nonlocal count
        count += 1
        return count

    def decrement():
        nonlocal count
        count -= 1
        return count

    def reset():
        nonlocal count
        count = 0
        return count

    return increment, decrement, reset

inc, dec, rst = make_counter()
print(inc())   # 1
print(inc())   # 2
print(dec())   # 1
print(rst())   # 0
print(inc())   # 1
```

**Why:** All three functions share the same closure cell for `count`. Without `nonlocal`, Python treats `count += 1` as a local assignment, which causes `UnboundLocalError` because there is no local `count` yet. The `nonlocal` keyword tells Python to look in the enclosing scope instead.

</details>

---

<a id="q3"></a>

### Q3 · Closure — make_adder + compose

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


**Problem:**
Write `make_adder(n)` that returns a function adding `n` to its argument. Then create `add5` and `add10`. Finally, create `add15` by composing them — without writing a new factory.

```python
add5 = make_adder(5)
add10 = make_adder(10)

print(add5(3))    # 8
print(add10(3))   # 13
print(add5(add10(0)))   # 15  ← composition
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`make_adder` follows the same pattern as `make_multiplier`. For composition, call one function with the result of the other: `add5(add10(x))`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def make_adder(n):
    def add(x):
        return x + n
    return add

add5 = make_adder(5)
add10 = make_adder(10)

print(add5(3))           # 8
print(add10(3))          # 13
print(add5(add10(0)))    # 15

# Using a lambda for a composed add15:
add15 = lambda x: add5(add10(x))
print(add15(7))          # 22
```

**Why:** Closures make composition natural — each adder is just a value-carrying function. `add5(add10(x))` chains them: `add10(x)` runs first, then `add5` adds 5 more.

</details>

---

<a id="q4"></a>

### Q4 · Closure — Late-binding trap: show the bug

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


**Problem:**
Write a list comprehension that creates 3 lambdas — one for each value `i` in `range(3)`. Each lambda should return its corresponding `i`. Print the results. Show the bug (all return the same value), then explain why.

```python
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])   # what does this actually print?
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Run the code exactly as written. The output is NOT `[0, 1, 2]`. Think about what value `i` holds after the loop finishes, and remember that all lambdas share the same reference to `i`.

</details>

<details>
<summary>✅ Answer</summary>

```python
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])   # [2, 2, 2]  ← all print 2!
```

**Why:** All three lambdas capture a reference to the same variable `i` — not a copy of its value at the time the lambda was created. The loop runs to completion, leaving `i = 2`. When the lambdas are called later, they all look up the current value of `i`, which is `2`. This is the **late-binding** behavior of closures.

</details>

---

<a id="q5"></a>

### Q5 · Closure — Late-binding trap: fix with wrapper function

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


**Problem:**
Fix the late-binding bug from Q4 using a wrapper function (not the default-argument trick). Each lambda must correctly return 0, 1, and 2.

```python
# fix this:
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])   # should print [0, 1, 2]
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Write a helper function `make_f(i)` that takes `i` as a parameter and returns `lambda: i`. Each call to `make_f(i)` creates a new scope with its own local `i`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def make_f(i):
    return lambda: i           # ← i is now a local parameter in make_f's scope

funcs = [make_f(i) for i in range(3)]
print([f() for f in funcs])   # [0, 1, 2]

# Alternative fix using default argument (both are valid):
funcs2 = [lambda i=i: i for i in range(3)]
print([f() for f in funcs2])  # [0, 1, 2]
```

**Why:** `make_f(i)` is called once per iteration with the current value of `i`. Inside `make_f`, `i` is a local parameter (not the loop variable). The lambda returned captures that local `i`, which is frozen at the value passed in. Each call to `make_f` creates a completely new scope with its own `i`.

</details>

---

<a id="q6"></a>

### Q6 · Decorator — Build @logger

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


**Problem:**
Write a `logger` decorator that prints `"Calling {function_name}"` before the call and `"Done: {result}"` after. Apply it to an `add(a, b)` function.

```python
@logger
def add(a, b):
    return a + b

add(3, 4)
# Calling add
# Done: 7
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Your decorator takes `func` as its argument. The inner `wrapper` takes `*args, **kwargs` and calls `func(*args, **kwargs)` to get the result. Print before and after. Use `func.__name__` to get the function's name.

</details>

<details>
<summary>✅ Answer</summary>

```python
def logger(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Done: {result}")
        return result
    return wrapper

@logger
def add(a, b):
    return a + b

add(3, 4)
# Calling add
# Done: 7
```

**Why:** `func.__name__` gives the original function's name. `*args, **kwargs` forwards all arguments through unchanged. Always return the result — otherwise callers get `None`.

</details>

---

<a id="q7"></a>

### Q7 · Decorator — Add @functools.wraps

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


**Problem:**
Take the `logger` decorator from Q6. Before adding `@functools.wraps`, print `add.__name__` and `add.__doc__`. Then add `@functools.wraps(func)` to the wrapper and print again. Show the difference.

```python
def add(a, b):
    """Add two numbers."""
    return a + b
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Without `@functools.wraps`, `add.__name__` returns `'wrapper'` because the decorator replaced `add` with the `wrapper` function. `import functools` then add `@functools.wraps(func)` immediately above `def wrapper`.

</details>

<details>
<summary>✅ Answer</summary>

```python
import functools

# Without @wraps
def logger_broken(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Done: {result}")
        return result
    return wrapper

@logger_broken
def add(a, b):
    """Add two numbers."""
    return a + b

print(add.__name__)   # wrapper   ← wrong
print(add.__doc__)    # None      ← lost

# With @wraps
def logger(func):
    @functools.wraps(func)           # ← copies __name__, __doc__, etc.
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Done: {result}")
        return result
    return wrapper

@logger
def add(a, b):
    """Add two numbers."""
    return a + b

print(add.__name__)   # add            ← correct
print(add.__doc__)    # Add two numbers.
```

**Why:** `@functools.wraps(func)` copies key attributes (`__name__`, `__doc__`, `__qualname__`, etc.) from the original function to the wrapper. Without it, tools like `help()`, logging frameworks, and debuggers see `wrapper` instead of `add`.

</details>

---

<a id="q8"></a>

### Q8 · Decorator — Build @timer

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


**Problem:**
Write a `timer` decorator that measures and prints execution time. Verify that the decorated function still returns the correct result — the timer must not change behavior, only observe it.

```python
@timer
def slow_sum(n):
    return sum(range(n))

result = slow_sum(1_000_000)
print(result)   # should still print the correct sum
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Use `time.perf_counter()` for high-resolution timing — call it before and after `func(*args, **kwargs)`. Store the function's return value in a variable, print the time, then return the value.

</details>

<details>
<summary>✅ Answer</summary>

```python
import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)          # ← store result before printing
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.4f}s")
        return result                           # ← return it unchanged
    return wrapper

@timer
def slow_sum(n):
    return sum(range(n))

result = slow_sum(1_000_000)
# slow_sum took 0.0412s
print(result)   # 499999500000  ← correct sum, behavior unchanged
```

**Why:** Saving the result before printing ensures the function's return value passes through. A timer that eats the return value would be a breaking change — callers expecting a result would get `None`.

</details>

---

<a id="q9"></a>

### Q9 · Decorator — Stack @timer + @logger, trace execution order

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


**Problem:**
Apply both `@timer` (from Q8) and `@logger` (from Q7) to a `multiply(a, b)` function, with `@timer` on top. Trace exactly which wrapper runs first when `multiply(3, 4)` is called and why.

```python
@timer
@logger
def multiply(a, b):
    return a * b
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>✅ Answer</summary>

```python
import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[timer] {func.__name__} took {elapsed:.6f}s")
        return result
    return wrapper

def logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[log] Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[log] Done: {result}")
        return result
    return wrapper

@timer
@logger
def multiply(a, b):
    return a * b

multiply(3, 4)
# [log] Calling multiply
# [log] Done: 12
# [timer] multiply took 0.000012s
```

**Why:** `@timer` on top means `multiply = timer(logger(multiply))`. Call order is outermost first: `timer`'s wrapper runs, starts the clock, then calls `logger`'s wrapper, which prints before/after, then calls the original. The timer wraps everything including the logger's prints — so the timing includes logging overhead.

</details>

---

<a id="q10"></a>

### Q10 · Decorator args — @retry(max_attempts=3)

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


**Problem:**
Write `@retry(max_attempts=3)` that retries a function up to `max_attempts` times if it raises an exception. Print the attempt number on each failure. After all attempts are exhausted, re-raise the last exception.

Test with a function that fails the first 2 times and succeeds on the 3rd.

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

You need 3 layers: `retry(max_attempts)` returns `decorator(func)` returns `wrapper(*args, **kwargs)`. Inside `wrapper`, use a `for` loop with a try/except. Keep track of the last exception and re-raise it after the loop.

</details>

<details>
<summary>✅ Answer</summary>

```python
import functools

def retry(max_attempts=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    print(f"[retry] attempt {attempt}/{max_attempts} failed: {e}")
            raise last_exc
        return wrapper
    return decorator

# Test: function that fails first 2 times
call_count = 0

@retry(max_attempts=3)
def flaky_service():
    global call_count
    call_count += 1
    if call_count < 3:
        raise ConnectionError(f"timeout (call {call_count})")
    return "success"

result = flaky_service()
print(result)
# [retry] attempt 1/3 failed: timeout (call 1)
# [retry] attempt 2/3 failed: timeout (call 2)
# success
```

**Why:** The 3-layer structure is required for parameterized decorators. Layer 1 captures `max_attempts`. Layer 2 captures `func`. Layer 3 is what runs on every call. Re-raising `last_exc` after the loop gives callers the actual exception (not a generic one).

</details>

---

<a id="q11"></a>

### Q11 · Decorator args — @repeat(n)

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


**Problem:**
Write `@repeat(n)` that calls the decorated function `n` times when invoked. The decorator should work with any function signature.

```python
@repeat(3)
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")
# Hello, Alice!
# Hello, Alice!
# Hello, Alice!
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

3-layer pattern: `repeat(n)` → `decorator(func)` → `wrapper(*args, **kwargs)`. Inside `wrapper`, call `func(*args, **kwargs)` inside a `for _ in range(n)` loop.

</details>

<details>
<summary>✅ Answer</summary>

```python
import functools

def repeat(n):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(n):
                result = func(*args, **kwargs)
            return result                    # ← return result of last call
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")
# Hello, Alice!
# Hello, Alice!
# Hello, Alice!
```

**Why:** Returning the result of the last call is a reasonable choice — callers who care about the return value get something meaningful. Functions that return `None` (like `greet`) are unaffected.

</details>

---

<a id="q12"></a>

### Q12 · Decorator args — @validate_input(min_val, max_val)

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


**Problem:**
Write `@validate_input(min_val, max_val)` that checks the first positional argument. If it is outside `[min_val, max_val]`, raise `ValueError` with a descriptive message. Otherwise call the function normally.

```python
@validate_input(0, 100)
def set_volume(level):
    return f"Volume set to {level}"

set_volume(50)    # "Volume set to 50"
set_volume(150)   # ValueError: 150 is out of range [0, 100]
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Inside `wrapper`, check `args[0]` against `min_val` and `max_val`. Raise `ValueError` if the check fails. Use `@functools.wraps`.

</details>

<details>
<summary>✅ Answer</summary>

```python
import functools

def validate_input(min_val, max_val):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if args:
                value = args[0]
                if not (min_val <= value <= max_val):
                    raise ValueError(
                        f"{value} is out of range [{min_val}, {max_val}]"
                    )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@validate_input(0, 100)
def set_volume(level):
    return f"Volume set to {level}"

print(set_volume(50))    # Volume set to 50
print(set_volume(0))     # Volume set to 0
set_volume(150)          # ValueError: 150 is out of range [0, 100]
```

**Why:** Checking `if args` guards against calls with zero positional arguments. Capturing `min_val` and `max_val` in the `validate_input` closure and using them in `wrapper` is the 3-layer parameterized decorator pattern.

</details>

---

<a id="q13"></a>

### Q13 · Decorator args — @cache_result(ttl_seconds)

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


**Problem:**
Write `@cache_result(ttl_seconds)` that caches the return value of a function. If the same arguments are passed again within `ttl_seconds`, return the cached result without calling the function. After the TTL expires, call the function again and refresh the cache.

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Store a dict in the wrapper's enclosing scope: `cache = {}`. Keys are `args` tuples. Values are `(result, timestamp)` tuples. Use `time.time()` to check if the entry is still fresh.

</details>

<details>
<summary>✅ Answer</summary>

```python
import functools
import time

def cache_result(ttl_seconds):
    def decorator(func):
        cache = {}                          # ← captured by wrapper (closure)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = args + tuple(sorted(kwargs.items()))
            now = time.time()
            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < ttl_seconds:
                    print(f"[cache hit]  {func.__name__}{args}")
                    return result
                else:
                    print(f"[cache expired] {func.__name__}{args}")
            print(f"[cache miss] {func.__name__}{args}")
            result = func(*args, **kwargs)
            cache[key] = (result, now)
            return result
        return wrapper
    return decorator

@cache_result(ttl_seconds=2)
def fetch_price(symbol):
    print(f"  (calling real fetch for {symbol})")
    return 42.0

fetch_price("AAPL")   # cache miss → calls function
fetch_price("AAPL")   # cache hit  → returns 42.0 immediately
time.sleep(3)
fetch_price("AAPL")   # cache expired → calls function again
```

**Why:** The `cache` dict lives in the decorator closure, persisting across calls. The TTL check compares the current time against the stored timestamp. For kwargs, we sort items to ensure `f(a=1, b=2)` and `f(b=2, a=1)` hit the same cache key.

</details>

---

<a id="q14"></a>

### Q14 · Real-world — @rate_limit(calls_per_second)

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


**Problem:**
Write `@rate_limit(calls_per_second)` that enforces a maximum call rate. If the function is called faster than the limit, block (sleep) until the minimum interval has passed. Use `time.time()` and `time.sleep()`.

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Calculate `min_interval = 1.0 / calls_per_second`. Track `last_called` time in the wrapper's enclosing scope. On each call, check how long ago the function was last called. If less than `min_interval`, sleep the difference.

</details>

<details>
<summary>✅ Answer</summary>

```python
import functools
import time

def rate_limit(calls_per_second):
    min_interval = 1.0 / calls_per_second   # ← seconds between allowed calls

    def decorator(func):
        last_called = [0.0]                  # ← list so we can mutate without nonlocal
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            elapsed = now - last_called[0]
            if elapsed < min_interval:
                wait = min_interval - elapsed
                print(f"[rate_limit] sleeping {wait:.3f}s")
                time.sleep(wait)
            last_called[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(calls_per_second=2)   # max 2 calls per second
def ping(host):
    return f"pong from {host}"

for _ in range(4):
    print(ping("server1"))
# first call: immediate
# subsequent calls: sleep ~0.5s between each
```

**Why:** `last_called` is stored as a list `[0.0]` so we can mutate its contents without needing `nonlocal` — mutating a list element is not a rebinding. An alternative is to use `nonlocal last_called` with a plain float.

</details>

---

<a id="q15"></a>

### Q15 · Real-world — @singleton for classes

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


**Problem:**
Write a `@singleton` decorator that can be applied to a class. After the first instantiation, every subsequent call to the class constructor returns the same instance.

```python
@singleton
class DatabaseConnection:
    def __init__(self, url):
        self.url = url

db1 = DatabaseConnection("postgres://localhost/mydb")
db2 = DatabaseConnection("postgres://localhost/mydb")
print(db1 is db2)   # True
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

The decorator receives a class (not a function). Store the single instance in the closure. Return a wrapper function that checks for the existing instance before creating a new one.

</details>

<details>
<summary>✅ Answer</summary>

```python
import functools

def singleton(cls):
    instances = {}                      # ← dict keyed by class, captured in closure

    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)   # ← create once
        return instances[cls]           # ← always return the same instance

    return get_instance

@singleton
class DatabaseConnection:
    def __init__(self, url):
        self.url = url
        print(f"  (creating connection to {url})")

db1 = DatabaseConnection("postgres://localhost/mydb")   # creates instance
db2 = DatabaseConnection("postgres://localhost/mydb")   # returns same instance
db3 = DatabaseConnection("different-url")               # still returns first instance

print(db1 is db2)   # True
print(db1 is db3)   # True
print(db1.url)      # postgres://localhost/mydb
```

**Why:** Decorators work on classes too — `cls` is just an object like any other. Using a dict (`instances = {}`) instead of a single variable supports decorating multiple classes with the same `singleton` decorator (each class gets its own entry in the dict).

</details>

---

**[← Back to Functions](../theory.md)** | **[Closures Theory](./01_closures_theory.md)** | **[Decorators Theory](./02_decorators_theory.md)**
