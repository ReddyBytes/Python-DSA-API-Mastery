# 🏷️ Class-Based Decorators — State, Registry, and @dataclass

Think of a function decorator as a sticky note you slap on a function — it runs once and moves on. A class decorator is more like a security badge reader: it sits at the door, remembers every person who walked through, and can enforce rules based on history. That persistent memory is the whole point.

**Key fact:** Every decorator you use daily — `@dataclass`, `@property`, `@classmethod`, `@staticmethod` — is a class decorator. Understanding the pattern unlocks all of them.

---

## 📌 Learning Priority

**Must Learn** — Class decorator anatomy (`__init__` + `__call__`), `@dataclass` basics
**Should Learn** — Singleton pattern, plugin registry, `frozen`/`order` dataclass options
**Good to Know** — `@validated` with `@dataclass`, `field()` defaults, `__post_init__`
**Reference** — Hashable dataclass as dict key, combining 3+ class decorators

---

## 1. Class AS a Decorator

Imagine you are a barista tracking how many coffees you have made this shift, and how many orders you had to throw out. You can't do that with a sticky note — you need a scoreboard on the wall that persists across every order. That is exactly what a class decorator does: the instance lives between calls, accumulating state.

A class becomes a decorator by implementing two dunders:

- `__init__` — called once at decoration time, receives the function being decorated
- `__call__` — called every time the wrapped function is invoked

```python
import functools

class CallCounter:
    def __init__(self, func):
        functools.update_wrapper(self, func)  # preserves __name__, __doc__
        self.func   = func
        self.count  = 0
        self.errors = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        try:
            return self.func(*args, **kwargs)
        except Exception:
            self.errors += 1
            raise

    def stats(self) -> dict:
        return {
            "function":    self.func.__name__,
            "total_calls": self.count,
            "errors":      self.errors,
            "success_rate": f"{(self.count - self.errors) / max(self.count, 1) * 100:.1f}%",
        }

@CallCounter
def process_order(order_id: int, amount: float) -> str:
    if amount <= 0:
        raise ValueError(f"Invalid amount: {amount}")
    return f"Order {order_id} processed: ${amount:.2f}"

process_order(1, 99.99)
process_order(2, 149.99)
print(process_order.stats())
# {'function': 'process_order', 'total_calls': 2, 'errors': 0, 'success_rate': '100.0%'}
```

`functools.update_wrapper(self, func)` does the same job as `@functools.wraps` — it copies `__name__`, `__doc__`, and `__wrapped__` from the original function onto the class instance so introspection tools see the right metadata.

### Decorator with configuration — the two-step `__init__`

When the decorator itself needs parameters (like `@RateLimit(max_calls=3)`), the two-step shifts:

- `__init__` — receives the **config**, not the function
- `__call__` — receives the **function**, returns a wrapper closure

```python
import time

class RateLimit:
    def __init__(self, max_calls: int, period: float = 1.0):
        self.max_calls = max_calls
        self.period    = period
        self._calls    = []   # timestamps of recent calls

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            self._calls = [t for t in self._calls if now - t < self.period]
            if len(self._calls) >= self.max_calls:
                raise RuntimeError(
                    f"Rate limit exceeded: {self.max_calls} calls per {self.period}s"
                )
            self._calls.append(now)
            return func(*args, **kwargs)
        return wrapper

@RateLimit(max_calls=3, period=1.0)
def send_sms(number: str, message: str) -> str:
    return f"SMS sent to {number}: {message[:20]}"
```

The `_calls` list lives on the `RateLimit` instance — persists across every call to `send_sms`, enabling accurate sliding-window enforcement.

**Pattern summary:**

| Decorator style | `__init__` receives | `__call__` receives | Returns |
|---|---|---|---|
| No config (`@CallCounter`) | the function | `*args, **kwargs` | result |
| With config (`@RateLimit(n)`) | config params | the function | wrapper closure |

---

## 2. Decorators That Modify Classes

Think of a building permit office: once your blueprint (class definition) is stamped (decorated), it gets registered, renamed, or modified before anyone is allowed to use it. Decorators applied to entire classes follow the same logic — they receive the class object, do something to it, and return a (possibly modified) class or replacement callable.

### Singleton

The singleton pattern guarantees a class has exactly one instance — like the one central logger for an entire application. A decorator implementation keeps the class body clean:

```python
def singleton(cls):
    instances = {}  # closure: survives the function, private to this decorator

    @functools.wraps(cls, updated=[])
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class AppConfig:
    def __init__(self, env: str = "development"):
        self.env   = env
        self.debug = env != "production"

cfg1 = AppConfig("production")
cfg2 = AppConfig("staging")   # ignored — returns existing instance
print(cfg1 is cfg2)   # True
print(cfg2.env)       # "production"
```

`updated=[]` in `functools.wraps` prevents it from trying to merge `__dict__` — necessary when wrapping a class rather than a function.

### Plugin Registry

Real frameworks (Flask, Airflow, pytest) discover handlers at import time without the core code knowing about them. A registry decorator enables this pattern:

```python
class Registry:
    _handlers: dict = {}

    @classmethod
    def register(cls, name: str):
        def decorator(handler_class):
            cls._handlers[name] = handler_class
            return handler_class   # class returned unchanged
        return decorator

    @classmethod
    def get(cls, name: str):
        return cls._handlers[name]()

    @classmethod
    def all_names(cls) -> list:
        return list(cls._handlers.keys())

@Registry.register("csv")
class CSVHandler:
    def process(self, data): return f"CSV: {data}"

@Registry.register("json")
class JSONHandler:
    def process(self, data): return f"JSON: {data}"

# Use any handler by name — no if/elif chain needed
handler = Registry.get("csv")
print(handler.process("row1,row2"))   # CSV: row1,row2
```

The key insight: the decorator returns `handler_class` unchanged — it only registers a reference. The class itself is untouched, which makes it easy to test and extend independently.

---

## 3. @dataclass — Auto-generated Methods

Writing `__init__`, `__repr__`, and `__eq__` by hand for every data class is like filling in the same form ten times with identical information. `@dataclass` reads your type annotations and fills in all three automatically.

### Basic dataclass

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        import math
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

p1 = Point(3.0, 4.0)
print(p1)                    # Point(x=3.0, y=4.0)   — auto __repr__
print(p1 == Point(3.0, 4.0)) # True                   — auto __eq__
```

### frozen=True and order=True

`frozen=True` makes the instance immutable — assignment to any field after creation raises `FrozenInstanceError`. As a side-effect, Python can auto-generate `__hash__`, making the object usable as a dict key or set member.

`order=True` generates `__lt__`, `__le__`, `__gt__`, `__ge__` by comparing fields in declaration order — like comparing tuples.

```python
from dataclasses import dataclass, field

@dataclass(order=True, frozen=True)
class Version:
    major: int
    minor: int
    patch: int = 0
    description: str = field(default="", compare=False)  # excluded from ordering

v1 = Version(2, 1, 3)
v2 = Version(2, 0, 5)
v3 = Version(3, 0, 0, description="Major release")

print(sorted([v1, v2, v3]))   # [Version(2,0,5), Version(2,1,3), Version(3,0,0)]
print(v1 > v2)                # True — (2,1,3) > (2,0,5)

# Hashable — usable as dict key
release_notes = {Version(1, 0): "Initial release", Version(2, 0): "API revamp"}
print(release_notes[Version(1, 0)])   # Initial release
```

`field(compare=False)` tells `@dataclass` to skip `description` when generating comparison methods — it still shows in `__repr__` and `__init__`.

### field() — avoiding the mutable default trap

A classic Python bug: using `[]` as a default argument shares a single list across all instances. `field(default_factory=list)` creates a fresh list per instance:

```python
@dataclass
class Playlist:
    name: str
    tracks: list = field(default_factory=list)  # safe — new list per instance

p1 = Playlist("Morning")
p2 = Playlist("Evening")
p1.tracks.append("Song A")
print(p2.tracks)   # [] — not affected
```

### __post_init__ — validation after auto-generated __init__

`@dataclass` calls `__post_init__` immediately after `__init__` completes. Use it for derived fields or validation:

```python
@dataclass
class Coordinate:
    x: float
    y: float

    def __post_init__(self):
        if self.x < 0 or self.y < 0:
            raise ValueError(f"Coordinates must be non-negative: ({self.x}, {self.y})")

Coordinate(3.0, 4.0)   # ok
Coordinate(-1.0, 2.0)  # ValueError
```

---

## 4. Combining Class Decorators

Decorators stack from bottom to top — `@dataclass` runs first and generates `__init__`, then `@validated` wraps `__post_init__` to inject validation logic. Think of it like assembly line QA: one station auto-builds the object, the next station inspects it before it ships.

```python
def validated(cls):
    """Ensures validate() is always called after __init__ in a dataclass."""
    original_post_init = getattr(cls, "__post_init__", None)

    def new_post_init(self):
        if original_post_init:
            original_post_init(self)
        if hasattr(self, "validate"):
            self.validate()

    cls.__post_init__ = new_post_init
    return cls

@validated
@dataclass
class User:
    name:  str
    email: str
    age:   int
    role:  str = "user"

    def validate(self):
        if len(self.name.strip()) < 2:
            raise ValueError("Name must be at least 2 characters")
        if "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email}")
        if not 0 <= self.age <= 150:
            raise ValueError(f"Age out of range: {self.age}")

alice = User("Alice", "alice@example.com", 30)
print(alice)  # User(name='Alice', email='alice@example.com', age=30, role='user')

try:
    User("A", "not-an-email", -5)
except ValueError as e:
    print(e)  # Name must be at least 2 characters
```

**Decorator order matters:**
- `@dataclass` generates `__init__` and `__post_init__` hook
- `@validated` injects into `__post_init__` — must run AFTER `@dataclass` has set it up
- Stacking order (bottom-up) ensures this: `@validated` sees the already-dataclassed class

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Back to Module | [../theory.md](../theory.md) |
| 💻 Practice | [practice.md](./practice.md) |
| ➡️ Next Subfolder | [../02_production_patterns/theory.md](../02_production_patterns/theory.md) |

**Related:** [Decorator Theory](../theory.md) · [Production Patterns →](../02_production_patterns/theory.md)
