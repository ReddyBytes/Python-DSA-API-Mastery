# Practice — Advanced Patterns

| Q | Difficulty | Topic |
|---|-----------|-------|
| [Q1](#q1) | 🟡 | `__slots__` memory savings |
| [Q2](#q2) | 🟡 | `__call__` with state |
| [Q3](#q3) | 🟡 | Introspect with `dir()` + `callable()` |
| [Q4](#q4) | 🟡 | `getattr` / `setattr` / `hasattr` / `delattr` |
| [Q5](#q5) | 🟡 | `vars()` — instance vs class `__dict__` |
| [Q6](#q6) | 🟠 | `inspect.signature` at runtime |
| [Q7](#q7) | 🟠 | `__all__` — control module exports |
| [Q8](#q8) | 🟠 | Capstone: plugin system using `__subclasses__()` |

---


## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| [Q1](#q1) | memory — `__slots__`: define a class with slots, measure memory savings | 🟡 |
| [Q2](#q2) | state — callable objects: `__call__` with state (function with memory) | 🟡 |
| [Q3](#q3) | discovery — introspection: list all methods of an object with `dir()` + `callable()` | 🟡 |
| [Q4](#q4) | dynamic access — `getattr` / `setattr` / `hasattr` / `delattr` | 🟡 |
| [Q5](#q5) | inspection — `vars()` — inspect `__dict__` of instance vs class | 🟡 |
| [Q6](#q6) | signatures — `inspect.signature` — get function signature at runtime | 🟠 |
| [Q7](#q7) | exports — `__all__` — control what gets exported from a module | 🟠 |
| [Q8](#q8) | capstone — plugin system using `__subclasses__()` | 🟠 |

---

<a id="q1"></a>

### Q1 🟡 · memory — `__slots__`: define a class with slots, measure memory savings

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)



**Problem:** Create two versions of a `Sensor` class (with and without `__slots__`), each with `sensor_id: int`, `value: float`, `unit: str`. Compare memory using `sys.getsizeof`. Try to add a new attribute to the slots version.

<details>
<summary>💡 Hint</summary>
For the dict version, total size = `sys.getsizeof(obj) + sys.getsizeof(obj.__dict__)`. For the slots version, there is no `__dict__`. Attempting to set an attribute not in `__slots__` raises `AttributeError`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

class SensorDict:
    def __init__(self, sensor_id, value, unit):
        self.sensor_id = sensor_id
        self.value     = value
        self.unit      = unit

class SensorSlots:
    __slots__ = ("sensor_id", "value", "unit")

    def __init__(self, sensor_id, value, unit):
        self.sensor_id = sensor_id
        self.value     = value
        self.unit      = unit

s1 = SensorDict(1, 23.5, "°C")
s2 = SensorSlots(1, 23.5, "°C")

size_dict  = sys.getsizeof(s1) + sys.getsizeof(s1.__dict__)
size_slots = sys.getsizeof(s2)

print(f"With __dict__:  {size_dict} bytes")
print(f"With __slots__: {size_slots} bytes")
print(f"Savings: {size_dict - size_slots} bytes ({(size_dict-size_slots)/size_dict*100:.0f}%)")

# Slot descriptors are on the class:
print(type(SensorSlots.sensor_id))   # <class 'member_descriptor'>

# Can't add new attributes:
try:
    s2.location = "floor_3"   # AttributeError
except AttributeError as e:
    print(e)
```

**Why:** `__slots__` replaces per-instance `__dict__` with a compact C-level array. For classes creating millions of instances (sensors, events, records), this saves 3-5x memory.
</details>

---

<a id="q2"></a>

### Q2 🟡 · state — callable objects: `__call__` with state (function with memory)

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)



**Problem:** Create a `Throttle` callable class that limits a function to at most N calls. After N calls, it raises `RuntimeError`. It should have a `.remaining` property and a `.reset()` method.

<details>
<summary>💡 Hint</summary>
Store a call count as an instance attribute. In `__call__`, increment it and check against the limit. A function or lambda can't do this — callable objects maintain state.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Throttle:
    def __init__(self, func, max_calls):
        self.func      = func
        self.max_calls = max_calls
        self._calls    = 0

    def __call__(self, *args, **kwargs):
        if self._calls >= self.max_calls:
            raise RuntimeError(
                f"{getattr(self.func, '__name__', 'func')!r} exceeded {self.max_calls} calls"
            )
        self._calls += 1
        return self.func(*args, **kwargs)

    @property
    def remaining(self):
        return self.max_calls - self._calls

    def reset(self):
        self._calls = 0

    def __repr__(self):
        return f"Throttle({getattr(self.func, '__name__', '?')!r}, {self.remaining}/{self.max_calls} remaining)"

@Throttle
def send_email(to, subject):
    return f"Sent to {to}: {subject}"

send_email.__self__ = send_email   # not needed for usage

t = Throttle(lambda x: x * 2, max_calls=3)
print(t(10))   # 20
print(t(20))   # 40
print(t(30))   # 60
print(t.remaining)  # 0

try:
    t(40)   # RuntimeError
except RuntimeError as e:
    print(e)

t.reset()
print(t.remaining)  # 3
```

**Why:** Callable objects maintain state between calls. A plain function or lambda has no memory — it executes statelessly. Callable classes bridge the gap between "configurable functions" and "objects with behavior".
</details>

---

<a id="q3"></a>

### Q3 🟡 · discovery — introspection: list all methods of an object with `dir()` + `callable()`

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)



**Problem:** Write a `list_methods(obj)` function that returns all public, callable attributes of an object (no dunder methods). Test it on a list, a dict, and a custom class.

<details>
<summary>💡 Hint</summary>
`dir(obj)` returns all names. Filter out names starting with `_`. Use `callable(getattr(obj, name))` to check if it's callable. Use `getattr` with a try/except in case any property raises.
</details>

<details>
<summary>✅ Answer</summary>

```python
def list_methods(obj):
    """Return all public callable attributes of obj."""
    result = []
    for name in dir(obj):
        if name.startswith('_'):
            continue
        try:
            attr = getattr(obj, name)
        except Exception:
            continue
        if callable(attr):
            result.append(name)
    return result

# Test on built-in types:
print("list methods:", list_methods([]))
# ['append', 'clear', 'copy', 'count', 'extend', 'index', 'insert', 'pop', 'remove', 'reverse', 'sort']

print("dict methods:", list_methods({}))
# ['clear', 'copy', 'fromkeys', 'get', 'items', 'keys', 'pop', 'popitem', 'setdefault', 'update', 'values']

class Service:
    def start(self): pass
    def stop(self): pass
    def status(self): return "running"
    _internal = lambda self: None

svc = Service()
print("Service methods:", list_methods(svc))   # ['start', 'status', 'stop']
```

**Why:** `dir()` + `callable()` is the standard pattern for discovering an object's interface at runtime. This is how interactive tools like `ipython` tab-completion works.
</details>

---

<a id="q4"></a>

### Q4 🟡 · dynamic access — `getattr` / `setattr` / `hasattr` / `delattr`

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)



**Problem:** Write a `ConfigLoader` class that takes `**kwargs` in `__init__` and stores each key as an attribute using `setattr`. Add `get(name, default)`, `has(name)`, `remove(name)`, and `to_dict()` methods.

<details>
<summary>💡 Hint</summary>
`setattr(obj, name, value)` is identical to `obj.name = value` but works with dynamic names. `getattr(obj, name, default)` is `obj.name` with a fallback.
</details>

<details>
<summary>✅ Answer</summary>

```python
class ConfigLoader:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get(self, name, default=None):
        return getattr(self, name, default)

    def has(self, name):
        return hasattr(self, name)

    def remove(self, name):
        if hasattr(self, name):
            delattr(self, name)
        else:
            raise KeyError(f"Config key {name!r} not found")

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return dict(vars(self))

    def __repr__(self):
        return f"ConfigLoader({vars(self)})"

cfg = ConfigLoader(host="localhost", port=8080, debug=True)
print(cfg.host)                    # localhost
print(cfg.get("timeout", 30))      # 30  (default)
print(cfg.has("port"))             # True
cfg.remove("debug")
print(cfg.has("debug"))            # False
cfg.update(ssl=True, timeout=60)
print(cfg.to_dict())               # {'host': 'localhost', 'port': 8080, 'ssl': True, 'timeout': 60}
```

**Why:** Dynamic attribute access powers configuration objects, proxy classes, and data loaders — anywhere the attribute names aren't known at class-definition time.
</details>

---

<a id="q5"></a>

### Q5 🟡 · inspection — `vars()` — inspect `__dict__` of instance vs class

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)



**Problem:** Create a class with a class variable, instance variables, and a class method. Use `vars()` to inspect both the instance's `__dict__` and the class's `__dict__`. Show what appears in each and explain the difference.

<details>
<summary>💡 Hint</summary>
`vars(instance)` returns only instance attributes. `vars(ClassName)` returns the class namespace (methods, class variables, etc.) as a `mappingproxy`. Class variables do NOT appear in instance `vars()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Counter:
    # Class variable — shared, appears in vars(Counter) not vars(instance)
    instances_created = 0

    def __init__(self, name, start=0):
        Counter.instances_created += 1
        self.name  = name       # instance attribute
        self.value = start      # instance attribute

    def increment(self):
        self.value += 1

    @classmethod
    def reset_count(cls):
        cls.instances_created = 0

c = Counter("my_counter", 10)

print("vars(c):")
print(vars(c))
# {'name': 'my_counter', 'value': 10}  — only instance attrs

print("\nvars(Counter) keys:")
print([k for k in vars(Counter) if not k.startswith('__')])
# ['instances_created', 'increment', 'reset_count']

# Class variable NOT in instance vars:
print("'instances_created' in vars(c):", "instances_created" in vars(c))   # False
print("'instances_created' in vars(Counter):", "instances_created" in vars(Counter))  # True
print("c.instances_created:", c.instances_created)   # 1 — found via class lookup
```

**Why:** `vars(obj)` is the same as `obj.__dict__` — only instance-level storage. Class-level attributes (class vars, methods) live in the class's namespace, accessible through the MRO but not in the instance's `__dict__`.
</details>

---

<a id="q6"></a>

### Q6 🟠 · signatures — `inspect.signature` — get function signature at runtime

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)



**Problem:** Write a `validate_call(func)` decorator that uses `inspect.signature` to check that all arguments match their type annotations at call time. Raise `TypeError` with a clear message if a type doesn't match.

<details>
<summary>💡 Hint</summary>
`inspect.signature(func).bind(*args, **kwargs)` binds actual call args to parameter names. `.apply_defaults()` fills in default values. Then check each bound argument against its annotation.
</details>

<details>
<summary>✅ Answer</summary>

```python
import inspect
from functools import wraps

def validate_call(func):
    sig = inspect.signature(func)
    annotations = {
        name: param.annotation
        for name, param in sig.parameters.items()
        if param.annotation is not inspect.Parameter.empty
    }

    @wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        for param_name, value in bound.arguments.items():
            if param_name in annotations:
                expected = annotations[param_name]
                if not isinstance(value, expected):
                    raise TypeError(
                        f"{param_name} must be {expected.__name__}, "
                        f"got {type(value).__name__}"
                    )
        return func(*args, **kwargs)

    return wrapper

@validate_call
def add(x: int, y: int) -> int:
    return x + y

@validate_call
def greet(name: str, times: int = 1) -> str:
    return (f"Hello, {name}! " * times).strip()

print(add(1, 2))           # 3
print(greet("Alice", 2))   # Hello, Alice! Hello, Alice!

try:
    add(1, "two")   # TypeError: y must be int, got str
except TypeError as e:
    print(e)
```

**Why:** `inspect.signature` gives you the full parameter metadata at runtime. Combined with annotations, you can build runtime type checking, API validation, and documentation tools.
</details>

---

<a id="q7"></a>

### Q7 🟠 · exports — `__all__` — control what gets exported from a module

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)



**Problem:** Demonstrate `__all__` by creating a module-like namespace using a class. Define `__all__` as a list and write a function that simulates `from module import *` by only returning names listed in `__all__`. Include both public and private items.

<details>
<summary>💡 Hint</summary>
`__all__` is a list of strings that defines the public API. `from module import *` only imports names in `__all__` (if defined). You can simulate this with `{name: getattr(module, name) for name in module.__all__}`.
</details>

<details>
<summary>✅ Answer</summary>

```python
# Simulate a module as a namespace object
class FakeModule:
    __all__ = ['PublicClass', 'public_function', 'CONSTANT']

    CONSTANT = 42
    _INTERNAL = "secret"

    class PublicClass:
        """Part of the public API."""
        def method(self): return "public"

    class _PrivateClass:
        """NOT exported."""
        pass

    @staticmethod
    def public_function():
        """Part of the public API."""
        return "public result"

    @staticmethod
    def _internal_helper():
        """NOT exported."""
        return "internal"

def star_import(module):
    """Simulate 'from module import *'."""
    if hasattr(module, '__all__'):
        return {name: getattr(module, name) for name in module.__all__}
    # Fallback: all public names (no leading _)
    return {name: getattr(module, name) for name in dir(module)
            if not name.startswith('_')}

exported = star_import(FakeModule)
print("Exported names:", list(exported.keys()))
# ['PublicClass', 'public_function', 'CONSTANT']

print("_INTERNAL exported?", "_INTERNAL" in exported)       # False
print("_internal_helper exported?", "_internal_helper" in exported)   # False
print("CONSTANT:", exported["CONSTANT"])   # 42
```

**Why:** `__all__` is the explicit contract for your module's public API. It helps IDEs, linters, and `from module import *` users know what's intended for external use.
</details>

---

<a id="q8"></a>

### Q8 🟠 · capstone — plugin system using `__subclasses__()`

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)



**Problem:** Build a plugin system where:
1. A `Formatter` base class uses `__subclasses__()` to auto-discover all subclasses.
2. Each subclass declares a `format_name` class attribute.
3. A `format(data, name)` function looks up the right formatter by `format_name`.
4. Adding a new formatter requires only defining a new subclass — no registration calls.

<details>
<summary>💡 Hint</summary>
`cls.__subclasses__()` returns direct subclasses only. For all descendants, recurse. Build the registry lazily from `__subclasses__()` at call time so newly defined classes are always found.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Formatter:
    format_name = None   # subclasses must set this

    @classmethod
    def _all_formatters(cls):
        """Recursively collect all subclasses with a format_name."""
        result = {}
        for sub in cls.__subclasses__():
            if sub.format_name:
                result[sub.format_name] = sub
            result.update(sub._all_formatters())   # recurse
        return result

    @classmethod
    def format(cls, data, name):
        registry = cls._all_formatters()
        if name not in registry:
            raise KeyError(f"No formatter named {name!r}. Available: {list(registry)}")
        return registry[name]().render(data)

    def render(self, data):
        raise NotImplementedError

class JSONFormatter(Formatter):
    format_name = "json"
    def render(self, data):
        import json; return json.dumps(data, indent=2)

class CSVFormatter(Formatter):
    format_name = "csv"
    def render(self, data):
        if isinstance(data, dict):
            return ",".join(f"{k}={v}" for k, v in data.items())
        return ",".join(str(x) for x in data)

class TextFormatter(Formatter):
    format_name = "text"
    def render(self, data):
        return str(data)

data = {"name": "Alice", "age": 30}
print(Formatter.format(data, "json"))
print(Formatter.format(data, "csv"))
print(Formatter.format(data, "text"))

# Add new formatter — no registration needed:
class XMLFormatter(Formatter):
    format_name = "xml"
    def render(self, data):
        if isinstance(data, dict):
            return "<record>" + "".join(f"<{k}>{v}</{k}>" for k, v in data.items()) + "</record>"
        return str(data)

print(Formatter.format(data, "xml"))   # works immediately!
print(list(Formatter._all_formatters().keys()))   # ['json', 'csv', 'text', 'xml']
```

**Why:** `__subclasses__()` provides auto-discovery without any explicit registration. Combining it with a class attribute convention creates a zero-registration plugin system.
</details>

---

## Navigation

| | |
|---|---|
| Root theory | [../theory.md](../theory.md) |
| Subfolder theory | [theory.md](./theory.md) |
| Prev subfolder | [../04_dataclasses/practice.md](../04_dataclasses/practice.md) |
| Root practice | [../practice.md](../practice.md) |
