# 💻 Practice — Class-Based Decorators

12 questions ranging from green (basic mechanics) to orange (production patterns).
Each question links to a stub in `practice_local.py` for hands-on solving.

---


## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| [Q1](#q1) | `__call__` — Add call_count to decorated function | 🟢 |
| [Q2](#q2) | `__init__` — RateLimit class decorator | 🟢 |
| [Q3](#q3) | stateful — Track total AND failed calls separately | 🟡 |
| [Q4](#q4) | singleton — One instance only | 🟡 |
| [Q5](#q5) | registry — Plugin registry with register() method | 🟡 |
| [Q6](#q6) | `@dataclass` basics — Point with auto-methods | 🟡 |
| [Q7](#q7) | frozen — Config as dict key | 🟡 |
| [Q8](#q8) | order — Sortable Version | 🟡 |
| [Q9](#q9) | `field()` — Avoid mutable default trap | 🟡 |
| [Q10](#q10) | `__post_init__` — Validate after init | 🟡 |
| [Q11](#q11) | combined — @validated on top of @dataclass | 🟠 |
| [Q12](#q12) | Capstone — @retry_config with state tracking | 🟠 |

---

<a id="q1"></a>

### Q1 🟢 · `__call__` — Add call_count to decorated function

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


Write a class decorator `CountCalls` that wraps any function and exposes a `.call_count` attribute on the wrapper, incremented each time the function is called.

```python
@CountCalls
def greet(name):
    return f"Hello, {name}"

greet("Alice")
greet("Bob")
print(greet.call_count)   # 2
```


<details>
<summary>Hint</summary>

`__init__` receives the function. `__call__` increments `self.call_count` then delegates to `self.func`. Use `functools.update_wrapper(self, func)` to preserve metadata.

</details>

<details>
<summary>Answer</summary>

```python
import functools

class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func       = func
        self.call_count = 0

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        return self.func(*args, **kwargs)
```

</details>

---

<a id="q2"></a>

### Q2 🟢 · `__init__` — RateLimit class decorator

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


Write a `RateLimit(max_calls, period=1.0)` class decorator. When a decorated function is called more than `max_calls` times within `period` seconds, raise `RuntimeError("Rate limit exceeded")`.

```python
@RateLimit(max_calls=2, period=1.0)
def ping():
    return "pong"

ping()   # ok
ping()   # ok
ping()   # RuntimeError: Rate limit exceeded
```


<details>
<summary>Hint</summary>

`__init__` stores config. `__call__` receives `func` and returns a wrapper. The wrapper keeps a `_calls` list of timestamps; filter it to the current window before checking the count.

</details>

<details>
<summary>Answer</summary>

```python
import functools, time

class RateLimit:
    def __init__(self, max_calls: int, period: float = 1.0):
        self.max_calls = max_calls
        self.period    = period
        self._calls    = []

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now          = time.time()
            self._calls  = [t for t in self._calls if now - t < self.period]
            if len(self._calls) >= self.max_calls:
                raise RuntimeError("Rate limit exceeded")
            self._calls.append(now)
            return func(*args, **kwargs)
        return wrapper
```

</details>

---

<a id="q3"></a>

### Q3 🟡 · stateful — Track total AND failed calls separately

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


Extend the `CallCounter` pattern. Build a `CallTracker` class decorator that stores `total_calls`, `failed_calls`, and a `success_rate` property (float 0.0–1.0). If the wrapped function raises any exception, increment `failed_calls` and re-raise.

```python
@CallTracker
def divide(a, b):
    return a / b

divide(10, 2)
try:
    divide(1, 0)
except ZeroDivisionError:
    pass

print(divide.total_calls)   # 2
print(divide.failed_calls)  # 1
print(divide.success_rate)  # 0.5
```


<details>
<summary>Hint</summary>

Add `self.failed_calls = 0` in `__init__`. In `__call__`, wrap the function call in `try/except Exception`, increment `self.failed_calls` in the `except` block, and `raise`. Add a `@property` for `success_rate`.

</details>

<details>
<summary>Answer</summary>

```python
import functools

class CallTracker:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func         = func
        self.total_calls  = 0
        self.failed_calls = 0

    def __call__(self, *args, **kwargs):
        self.total_calls += 1
        try:
            return self.func(*args, **kwargs)
        except Exception:
            self.failed_calls += 1
            raise

    @property
    def success_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return (self.total_calls - self.failed_calls) / self.total_calls
```

</details>

---

<a id="q4"></a>

### Q4 🟡 · singleton — One instance only

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


Write a `@singleton` function decorator for classes. The first instantiation creates the object; every subsequent call returns the same instance, ignoring new arguments.

```python
@singleton
class DatabasePool:
    def __init__(self, url: str):
        self.url = url

db1 = DatabasePool("postgres://localhost/app")
db2 = DatabasePool("postgres://prod/app")   # ignored
print(db1 is db2)    # True
print(db2.url)       # postgres://localhost/app
```


<details>
<summary>Hint</summary>

Use a closure dict `instances = {}`. The inner `get_instance(*args, **kwargs)` checks `if cls not in instances` before creating. Use `functools.wraps(cls, updated=[])` to copy class metadata.

</details>

<details>
<summary>Answer</summary>

```python
import functools

def singleton(cls):
    instances = {}

    @functools.wraps(cls, updated=[])
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
```

</details>

---

<a id="q5"></a>

### Q5 🟡 · registry — Plugin registry with register() method

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Build a `PluginRegistry` class with a `@PluginRegistry.register("name")` class decorator. The decorator stores the class in an internal dict and returns the class unchanged. Add `get(name)` and `all_names()` class methods.

```python
@PluginRegistry.register("pdf")
class PDFExporter:
    def export(self, data): return f"PDF: {data}"

@PluginRegistry.register("html")
class HTMLExporter:
    def export(self, data): return f"HTML: {data}"

print(PluginRegistry.all_names())   # ["pdf", "html"]
exp = PluginRegistry.get("pdf")
print(exp.export("report"))         # PDF: report
```


<details>
<summary>Hint</summary>

`register(name)` is a `@classmethod` that returns a `decorator(handler_class)` closure. The closure stores `handler_class` in `cls._handlers[name]` and returns `handler_class` untouched. `get(name)` instantiates and returns.

</details>

<details>
<summary>Answer</summary>

```python
class PluginRegistry:
    _handlers: dict = {}

    @classmethod
    def register(cls, name: str):
        def decorator(handler_class):
            cls._handlers[name] = handler_class
            return handler_class
        return decorator

    @classmethod
    def get(cls, name: str):
        if name not in cls._handlers:
            raise KeyError(f"No plugin: {name}")
        return cls._handlers[name]()

    @classmethod
    def all_names(cls) -> list:
        return list(cls._handlers.keys())
```

</details>

---

<a id="q6"></a>

### Q6 🟡 · `@dataclass` basics — Point with auto-methods

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


Create a `Point(x: float, y: float)` dataclass. Show that `__init__`, `__repr__`, and `__eq__` are auto-generated. Add a `distance_to(other)` method manually.

```python
p1 = Point(3.0, 4.0)
p2 = Point(6.0, 8.0)
print(p1)                    # Point(x=3.0, y=4.0)
print(p1 == Point(3.0, 4.0)) # True
print(p1.distance_to(p2))    # 5.0
```


<details>
<summary>Hint</summary>

Apply `@dataclass` from `dataclasses`. Declare `x: float` and `y: float` as class body annotations — no `__init__` needed. Add the `distance_to` method as you would in any class.

</details>

<details>
<summary>Answer</summary>

```python
import math
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
```

</details>

---

<a id="q7"></a>

### Q7 🟡 · frozen — Config as dict key

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


Create a `Config(host: str, port: int, debug: bool = False)` dataclass with `frozen=True`. Demonstrate that it is immutable and can be used as a dictionary key.

```python
cfg = Config("localhost", 8080)
print(cfg)   # Config(host='localhost', port=8080, debug=False)

lookup = {Config("prod", 443): "production", Config("dev", 8080): "development"}
print(lookup[Config("prod", 443)])   # production

cfg.host = "other"   # FrozenInstanceError
```


<details>
<summary>Hint</summary>

Pass `frozen=True` to `@dataclass`. Frozen dataclasses are automatically hashable because Python can safely generate `__hash__` for immutable objects. Try assigning to a field to confirm the error.

</details>

<details>
<summary>Answer</summary>

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    host:  str
    port:  int
    debug: bool = False
```

</details>

---

<a id="q8"></a>

### Q8 🟡 · order — Sortable Version

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


Create a `Version(major: int, minor: int, patch: int = 0)` dataclass with `order=True` and `frozen=True`. Show it can be sorted and compared with `>`.

```python
versions = [Version(2, 1, 3), Version(2, 0, 5), Version(3, 0, 0)]
print(sorted(versions))   # [Version(2,0,5), Version(2,1,3), Version(3,0,0)]
print(Version(2, 1) > Version(2, 0))   # True
```


<details>
<summary>Hint</summary>

Pass `order=True, frozen=True` to `@dataclass`. Comparison is done field-by-field in declaration order — equivalent to comparing tuples `(major, minor, patch)`.

</details>

<details>
<summary>Answer</summary>

```python
from dataclasses import dataclass

@dataclass(order=True, frozen=True)
class Version:
    major: int
    minor: int
    patch: int = 0
```

</details>

---

<a id="q9"></a>

### Q9 🟡 · `field()` — Avoid mutable default trap

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


Create a `Playlist(name: str, tracks: list)` dataclass where `tracks` defaults to an empty list. Show that each instance gets its own list (not shared). Use `field(default_factory=list)`.

```python
p1 = Playlist("Morning")
p2 = Playlist("Evening")
p1.tracks.append("Song A")
print(p1.tracks)   # ["Song A"]
print(p2.tracks)   # []  — not affected
```


<details>
<summary>Hint</summary>

`tracks: list = []` would raise `ValueError` in a dataclass (mutable defaults are blocked). Use `tracks: list = field(default_factory=list)` instead — `default_factory` is called fresh for each new instance.

</details>

<details>
<summary>Answer</summary>

```python
from dataclasses import dataclass, field

@dataclass
class Playlist:
    name:   str
    tracks: list = field(default_factory=list)
```

</details>

---

<a id="q10"></a>

### Q10 🟡 · `__post_init__` — Validate after init

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


Create a `Coordinate(x: float, y: float)` dataclass that rejects negative values. Use `__post_init__` to raise `ValueError` if either coordinate is negative.

```python
Coordinate(3.0, 4.0)    # ok
Coordinate(-1.0, 2.0)   # ValueError: x must be non-negative, got -1.0
```


<details>
<summary>Hint</summary>

Define `def __post_init__(self):` inside the dataclass body. `@dataclass` calls it automatically at the end of `__init__`. Access `self.x` and `self.y` normally.

</details>

<details>
<summary>Answer</summary>

```python
from dataclasses import dataclass

@dataclass
class Coordinate:
    x: float
    y: float

    def __post_init__(self):
        for name, val in [("x", self.x), ("y", self.y)]:
            if val < 0:
                raise ValueError(f"{name} must be non-negative, got {val}")
```

</details>

---

<a id="q11"></a>

### Q11 🟠 · combined — @validated on top of @dataclass

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


Write a `@validated` class decorator that hooks into `__post_init__` to call a `validate()` method (if present) after `@dataclass` generates `__init__`. Apply both to a `Product(name: str, price: float)` that validates price is positive.

```python
@validated
@dataclass
class Product:
    name:  str
    price: float

    def validate(self):
        if self.price <= 0:
            raise ValueError(f"Price must be positive, got {self.price}")

Product("Widget", 9.99)     # ok
Product("Free", 0.0)        # ValueError: Price must be positive, got 0.0
```


<details>
<summary>Hint</summary>

In `validated(cls)`: save the existing `__post_init__` (if any) with `getattr(cls, "__post_init__", None)`. Replace it with a `new_post_init` that calls the original first, then calls `self.validate()` if the method exists. Assign `cls.__post_init__ = new_post_init` and return `cls`.

</details>

<details>
<summary>Answer</summary>

```python
from dataclasses import dataclass

def validated(cls):
    original = getattr(cls, "__post_init__", None)

    def new_post_init(self):
        if original:
            original(self)
        if hasattr(self, "validate"):
            self.validate()

    cls.__post_init__ = new_post_init
    return cls

@validated
@dataclass
class Product:
    name:  str
    price: float

    def validate(self):
        if self.price <= 0:
            raise ValueError(f"Price must be positive, got {self.price}")
```

</details>

---

<a id="q12"></a>

### Q12 🟠 · Capstone — @retry_config with state tracking

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


Build a `@retry_config(attempts=3, delay=0.0)` class decorator. It should:
1. Retry the wrapped function up to `attempts` times on any exception
2. Track `total_calls`, `total_retries`, and `total_failures` on the wrapper
3. Raise the last exception if all attempts are exhausted

```python
import random

@retry_config(attempts=3, delay=0.0)
def flaky_api():
    if random.random() < 0.7:
        raise ConnectionError("timeout")
    return "ok"

try:
    result = flaky_api()
except ConnectionError:
    pass

print(flaky_api.total_calls)    # >= 1
print(flaky_api.total_retries)  # >= 0
```


<details>
<summary>Hint</summary>

`__init__` stores config (no function yet). `__call__` receives `func` and returns a wrapper. The wrapper uses a `for attempt in range(self.attempts)` loop; on success it breaks, on final failure it re-raises. Use `time.sleep(self.delay)` between retries. Store counters on `self` (the `retry_config` instance) so they persist across calls.

</details>

<details>
<summary>Answer</summary>

```python
import functools, time

class retry_config:
    def __init__(self, attempts: int = 3, delay: float = 0.0):
        self.attempts       = attempts
        self.delay          = delay
        self.total_calls    = 0
        self.total_retries  = 0
        self.total_failures = 0

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.total_calls += 1
            last_exc = None
            for attempt in range(self.attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < self.attempts - 1:
                        self.total_retries += 1
                        if self.delay:
                            time.sleep(self.delay)
            self.total_failures += 1
            raise last_exc
        # expose counters on the wrapper via the enclosing instance
        wrapper.__self__ = self
        functools.update_wrapper(wrapper, func)
        return wrapper
```

</details>

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Back to Module | [../theory.md](../theory.md) |
| 📖 Theory | [theory.md](./theory.md) |
| 💻 Solve Locally | [practice_local.py](./practice_local.py) |
| ➡️ Next Subfolder | [../02_production_patterns/practice.md](../02_production_patterns/practice.md) |

**Related:** [Decorator Theory](../theory.md) · [Production Patterns →](../02_production_patterns/practice.md)
