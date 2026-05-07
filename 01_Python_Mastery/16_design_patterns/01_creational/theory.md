# Creational Patterns — Singleton & Factory

A country has exactly one president at a time. A car factory builds different models on demand. Creational patterns answer one question: **who is responsible for creating objects, and how many can exist?**

---

## 📌 Learning Priority

**Must Learn:** Singleton via module · Factory method · Registration pattern (dict dispatch)

**Should Learn:** Thread-safe singleton · Abstract factory

**Good to Know:** Borg pattern · Factory with ABC

**Reference:** Class-level Singleton with `__new__`

---

## 1. Singleton Pattern

Think of the Oval Office. The building exists once. Every visitor to "the president" gets the same person — there is no second president running in parallel. **Singleton** enforces that a class has exactly one instance and provides a global access point to it.

### 1.1 Module-Level Singleton (the Pythonic way)

Python modules are imported once and cached. The simplest singleton is a module-level object.

```python
# config.py
class _AppConfig:
    def __init__(self):
        self.env   = "production"
        self.debug = False
        self.db_url = "postgresql://localhost/prod_db"

config = _AppConfig()   # created once when module is imported  # ← singleton lives here
```

```python
# anywhere else in the codebase
from config import config   # always the SAME object
config.env  # "production"
```

**Why it works:** Python caches `sys.modules` — the module body runs exactly once. No boilerplate needed.

### 1.2 Class-Based Singleton via `__new__`

`__new__` is called before `__init__`. Intercepting it lets you return the same instance every time.

```python
class AppConfig:
    _instance = None            # ← class attribute, shared across all calls

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance    # ← always the same object

    def __init__(self, env: str = "development"):
        if self._initialized:
            return              # ← skip re-init on subsequent calls
        self.env = env
        self._initialized = True

    @classmethod
    def reset(cls):
        cls._instance = None    # ← for tests only
```

```python
a = AppConfig("production")
b = AppConfig("staging")   # __init__ args ignored — already initialized
a is b                     # True
b.env                      # "production"
```

**Common mistake:** Forgetting the `_initialized` guard. Without it, `__init__` runs again on every call even though `__new__` returns the same object, resetting attributes.

### 1.3 Thread-Safe Singleton (Double-Checked Locking)

Two threads can both pass the `_instance is None` check before either creates the instance — a race condition. **Double-checked locking** minimizes contention: check without a lock first (cheap in the common case), then check again inside the lock.

```python
import threading

class ThreadSafeSingleton:
    _instance = None
    _lock      = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:           # fast path — no lock if already created
            with cls._lock:                 # only one thread enters at a time
                if cls._instance is None:   # second check INSIDE the lock
                    cls._instance = super().__new__(cls)
        return cls._instance
```

**Why two checks?** After the first check passes, another thread may have already created the instance before this thread acquires the lock. The inner check catches that.

### 1.4 Borg Pattern (Monostate)

Think of a shared whiteboard. Multiple people (instances) exist independently, but every change any person makes appears on the same board (shared state). **Borg** does not share identity — it shares `__dict__`.

```python
class Logger:
    _shared_state: dict = {}   # ← ALL instances share this exact dictionary

    def __init__(self):
        self.__dict__ = Logger._shared_state   # ← point this instance at shared dict
        if not hasattr(self, "_ready"):
            self._log_entries = []
            self._level       = "INFO"
            self._ready       = True

    def log(self, level: str, msg: str) -> None:
        self._log_entries.append(f"[{level}] {msg}")

    def set_level(self, level: str) -> None:
        self._level = level
```

```python
log1 = Logger()
log2 = Logger()
log1 is log2        # False — different objects
log1.log("INFO", "started")
log2._log_entries   # ["[INFO] started"] — shared state!
log1.set_level("DEBUG")
log2._level         # "DEBUG" — set by log1!
```

**Borg vs classic Singleton:**

| Aspect | Singleton (`__new__`) | Borg |
|---|---|---|
| Identity (`is`) | Same object | Different objects |
| State | Shared | Shared |
| Testing | Harder (need `reset()`) | Easier (create fresh instance) |
| Subclassing | Breaks without care | Works naturally |

### 1.5 When to Use vs Avoid

**Use Singleton when:**
- The resource is truly global and lifecycle-spanning (DB connection pool, app config, logger)
- Creating multiple instances would cause incorrect behavior (two config objects with different env values)
- The resource is expensive to create (connection pools)

**Avoid Singleton when:**
- The class is testable without global state (use DI instead)
- You find yourself calling `reset()` in every test (signal that DI is better)
- The "singleton" value changes between environments (config should be injected)

**Common mistakes:**
- Using singleton for services that should be injected (makes unit testing painful)
- Forgetting `reset()` for tests, causing test pollution
- Not using double-checked locking in threaded code

---

## 2. Factory Pattern

Imagine a car factory. You call the factory and say "I want an SUV." You do not weld metal, install engines, or paint cars. The factory knows how to build each model. You just get back the finished car. **Factory patterns** separate object creation from object use.

### 2.1 Simple Factory Function

The most common pattern in Python. A function takes a type string and returns the right object.

```python
from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def send(self, message: str, recipient: str) -> dict: ...

class EmailNotification(Notification):
    def send(self, message, recipient):
        return {"channel": "email", "to": recipient, "body": message}

class SMSNotification(Notification):
    def send(self, message, recipient):
        return {"channel": "sms", "to": recipient, "text": message[:160]}

def create_notification(channel: str) -> Notification:
    factories = {
        "email": EmailNotification,
        "sms":   SMSNotification,
    }
    if channel not in factories:
        raise ValueError(f"Unknown channel: {channel!r}")
    return factories[channel]()   # ← dict lookup replaces if/elif chain
```

**Why dict over if/elif:** Adding a new channel means adding one key to the dict and one class. The function body never changes.

### 2.2 Factory Method Pattern (GoF)

The **factory method** pattern defines an interface for creating an object but lets subclasses decide which class to instantiate. The creator class has a `create_X()` method that each subclass overrides.

```python
from abc import ABC, abstractmethod

class DataParser(ABC):
    """Creator — defines the algorithm, delegates creation to subclasses."""

    @abstractmethod
    def create_reader(self) -> "DataReader": ...    # ← factory method

    def process(self, raw: str) -> dict:
        reader = self.create_reader()               # ← calls subclass factory
        data   = reader.read(raw)
        return {"rows": len(data), "data": data}

class JSONParser(DataParser):
    def create_reader(self):
        return JSONReader()    # ← this subclass knows JSON

class CSVParser(DataParser):
    def create_reader(self):
        return CSVReader()     # ← this subclass knows CSV
```

**When to use:** Framework-style code where the base class defines a pipeline and plugins provide implementations.

### 2.3 Registration Pattern (Dict-Based Dispatch)

The most extensible factory in Python. Classes register themselves via a decorator. The factory never changes when new types are added.

```python
class ReportFactory:
    _registry: dict[str, type] = {}

    @classmethod
    def register(cls, name: str):
        """@ReportFactory.register("pdf") — registers the decorated class."""
        def decorator(report_cls):
            cls._registry[name] = report_cls
            return report_cls
        return decorator

    @classmethod
    def create(cls, report_type: str, **kwargs):
        if report_type not in cls._registry:
            raise KeyError(f"Unknown type: {report_type!r}. "
                           f"Available: {list(cls._registry)}")
        return cls._registry[report_type](**kwargs)
```

```python
@ReportFactory.register("csv")
class CSVReport:
    def render(self, data): ...

@ReportFactory.register("json")
class JSONReport:
    def render(self, data): ...

# Adding pdf? Just add the class and @register. Nothing else changes.
report = ReportFactory.create("csv")
```

**Why this matters:** Open/Closed Principle — open for extension (add new types), closed for modification (factory code unchanged).

### 2.4 Abstract Factory (Families of Objects)

A car platform does not just produce cars — it produces matching parts: wheels, engines, interiors, all coordinated. **Abstract Factory** creates families of related objects that must be consistent with each other.

```python
from abc import ABC, abstractmethod

class UIFactory(ABC):
    @abstractmethod
    def create_button(self, label: str) -> "Button": ...
    @abstractmethod
    def create_dialog(self, title: str) -> "Dialog": ...

class LightThemeFactory(UIFactory):
    def create_button(self, label): return LightButton(label)
    def create_dialog(self, title): return LightDialog(title)

class DarkThemeFactory(UIFactory):
    def create_button(self, label): return DarkButton(label)
    def create_dialog(self, title): return DarkDialog(title)

def build_login_form(factory: UIFactory) -> None:
    dialog = factory.create_dialog("Login")
    submit = factory.create_button("Sign In")
    # client code never knows if it's light or dark
```

**Change the factory → change the whole family atomically.**

### 2.5 Choosing the Right Factory

| Pattern | When to Use |
|---|---|
| Simple factory function | Most cases — straightforward mapping, internal use |
| Registration pattern | Extensible systems, plugins, multiple teams adding types |
| Factory Method | Framework base classes, subclasses customize creation |
| Abstract Factory | Must create a consistent family of objects (UI themes, DB drivers) |

**Common mistakes:**
- Building a complex Abstract Factory when a simple function suffices
- Using a class when a function is enough (Python does not need `new PaymentFactory().create()`)
- Forgetting to validate the type string and letting `KeyError` leak to callers

---

## 📂 Navigation

**[🏠 Back to README](../../README.md)**

**Prev:** [← Design Patterns — Theory](../theory.md) &nbsp;|&nbsp; **Next:** [02 Behavioral →](../02_behavioral/theory.md)

**Related Topics:** [02 Behavioral](../02_behavioral/theory.md) · [03 Dependency Injection](../03_dependency_injection/theory.md) · [Root Theory](../theory.md)
