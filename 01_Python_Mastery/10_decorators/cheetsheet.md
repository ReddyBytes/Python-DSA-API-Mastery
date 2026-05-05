# ⚡ Decorators — Cheatsheet

> Quick reference: syntax, patterns, built-ins, stacking order, gotchas.

---

## 🔧 Basic Decorator

```python
import functools

def my_decorator(func):
    @functools.wraps(func)                   # ALWAYS include — preserves metadata
    def wrapper(*args, **kwargs):
        # code before
        result = func(*args, **kwargs)       # call original — ALWAYS return result!
        # code after
        return result
    return wrapper

@my_decorator
def greet(name):
    return f"Hello, {name}!"

# Equivalent to: greet = my_decorator(greet)
```

---

## ⚙️ Decorator Factory (with Arguments)

```python
def retry(max_attempts=3, delay=1.0):        # LEVEL 1: factory — takes config
    def decorator(func):                     # LEVEL 2: decorator — takes function
        @functools.wraps(func)
        def wrapper(*args, **kwargs):        # LEVEL 3: wrapper — runs on each call
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=5, delay=0.5)
def fetch_data(url):
    ...

# Equivalent to: fetch_data = retry(max_attempts=5, delay=0.5)(fetch_data)
```

---

## 🏭 Class-Based Decorator

```python
class CallCounter:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)

@CallCounter           # no parens — __init__ receives function directly
def process():
    pass

process()
process()
print(process.calls)   # 2 — state on the decorator object
```

---

## 📦 Optional Arguments (works with or without parens)

```python
def retry(_func=None, *, max_attempts=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    pass
            raise RuntimeError("All attempts failed")
        return wrapper

    if _func is not None:
        return decorator(_func)   # @retry — called without parens
    return decorator              # @retry() or @retry(max_attempts=5)

@retry               # ✅
@retry()             # ✅
@retry(max_attempts=5)   # ✅
```

---

## 🔄 Stacking Order

```
@A          applied last (outermost)
@B          applied second
@C          applied first (innermost, closest to original)
def func(): ...

Equivalent to: func = A(B(C(func)))

CALL ORDER:
  A's before-code
    B's before-code
      C's before-code
        original func()
      C's after-code
    B's after-code
  A's after-code
```

---

## 🔑 Built-in Class Decorators

```python
class MyClass:
    # @property — computed attribute with getter/setter/deleter
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        if v < 0:
            raise ValueError("negative")
        self._value = v

    @value.deleter
    def value(self):
        del self._value

    # @classmethod — gets cls, used for factory constructors
    @classmethod
    def from_string(cls, s: str) -> "MyClass":
        return cls(int(s))

    # @staticmethod — gets nothing, pure utility
    @staticmethod
    def is_valid(v) -> bool:
        return isinstance(v, int) and v >= 0

obj = MyClass()
obj.value = 42          # calls setter
print(obj.value)        # calls getter
MyClass.from_string("5")   # classmethod
MyClass.is_valid(-1)       # False
```

---

## ⚡ Async Decorator

```python
def timed(func):
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return await func(*args, **kwargs)   # await the original!
            finally:
                print(f"{func.__name__}: {time.perf_counter()-start:.3f}s")
        return async_wrapper
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            print(f"{func.__name__}: {time.perf_counter()-start:.3f}s")
    return sync_wrapper
```

---

## 🏷️ functools.wraps — What It Copies

```python
@functools.wraps(func)   # copies these attributes from func to wrapper:
# __name__          'process'
# __qualname__      'MyClass.process'
# __doc__           docstring
# __module__        module name
# __annotations__   type hints dict
# __dict__          function attributes
# __wrapped__       reference to original func  ← unwrap chain
```

---

## 🎯 Common Production Decorators (quick syntax)

```python
# Timer:
def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            logger.info("%s: %.3fs", func.__name__, time.perf_counter() - start)
    return wrapper

# Memoize (built-in):
@functools.lru_cache(maxsize=128)
def expensive(n):
    ...

# Cache with TTL (roll your own):
def ttl_cache(seconds=60):
    def decorator(func):
        cache = {}
        @functools.wraps(func)
        def wrapper(*args):
            now = time.time()
            if args in cache:
                val, ts = cache[args]
                if now - ts < seconds:
                    return val
            val = func(*args)
            cache[args] = (val, now)
            return val
        return wrapper
    return decorator

# Deprecation warning:
def deprecated(msg=""):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated. {msg}",
                DeprecationWarning, stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

---

## 🌳 Introspection

```python
@A
@B
def func(): ...

func.__name__      # original name (if @wraps used)
func.__wrapped__   # the function B wrapped (one layer)
inspect.unwrap(func)  # fully unwrapped original function
inspect.signature(func)  # signature (follows __wrapped__)
```

---

## 🔴 Gotchas

```python
# 1 — Missing return in wrapper swallows result:
def wrapper(*args, **kwargs):
    func(*args, **kwargs)    # ← forgot return → always returns None!

# 2 — Missing @functools.wraps breaks metadata:
def wrapper(*args, **kwargs):   # no @wraps → __name__ = 'wrapper'

# 3 — Mutable default in factory:
def collect(results=[]):        # shared across ALL decorated functions!
def collect(results=None):
    if results is None: results = []    # ← correct

# 4 — Sync wrapper on async function:
def wrapper(*args, **kwargs):
    return func(*args, **kwargs)  # returns coroutine, doesn't await it!
# Fix: check asyncio.iscoroutinefunction(func)

# 5 — Wrong lru_cache + staticmethod order:
@functools.lru_cache  # ← WRONG: caches the staticmethod descriptor
@staticmethod
def compute(n): ...

@staticmethod         # ← CORRECT: staticmethod outermost
@functools.lru_cache
def compute(n): ...

# 6 — Decorator runs at import time:
@register_in_database  # ← runs when module is imported, not when function is called
def my_func(): ...
# Ensure decorator factories don't do I/O at import time
```

---

## 🔥 Rapid-Fire

```
Q: @decorator equivalent?
A: func = decorator(func)

Q: Three levels of parametrized decorator?
A: factory(config) → decorator(func) → wrapper(*args, **kwargs)

Q: Stacking: applied bottom-up or top-down?
A: Applied bottom-up. Executed top-down (outermost first).

Q: @functools.wraps does what?
A: Copies __name__, __doc__, __qualname__, __annotations__,
   __dict__ from wrapped to wrapper. Adds __wrapped__.

Q: Class-based vs function-based decorator?
A: Class-based: use when decorator needs persistent state.
   Function-based: simpler, most use cases.

Q: How to detect async function in decorator?
A: asyncio.iscoroutinefunction(func)

Q: __wrapped__ attribute?
A: Added by @functools.wraps. Points to the original function.
   inspect.unwrap() follows the chain to the root.
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| 🏭 Pattern Library | [decorator_patterns.md](./decorator_patterns.md) |
| ➡️ Next | [11 — Iterators & Generators](../11_iterators_generators/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Decorator Patterns →](./decorator_patterns.md)

**Related Topics:** [Theory](./theory.md) · [Decorator Patterns](./decorator_patterns.md) · [Interview Q&A](./interview.md)
