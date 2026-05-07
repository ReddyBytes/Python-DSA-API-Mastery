# Creational Patterns — Practice Questions

10 questions covering Singleton variants and Factory patterns.

---

### Q1 🟢 · singleton · Module-Level Singleton

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

**Problem:** Create a module-level singleton for application configuration. The config object should have `env`, `debug`, and `db_url` attributes. Demonstrate that importing it from two places gives the same object.

<details>
<summary>💡 Hint</summary>
Create the instance at module level. Python caches modules in `sys.modules` — the body runs exactly once.
</details>

<details>
<summary>✅ Answer</summary>

```python
# config.py
class _AppConfig:
    def __init__(self):
        self.env    = "production"
        self.debug  = False
        self.db_url = "postgresql://localhost/prod_db"

config = _AppConfig()   # created once when module is imported

# usage
from config import config as cfg1
from config import config as cfg2
assert cfg1 is cfg2   # True — same object
```

**Why:** Python's import system runs a module body once and caches the result. Every `import config` returns the cached module, so `config` always refers to the same object.
</details>

---

### Q2 🟡 · singleton · Class-Based Singleton Using `__new__`

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

**Problem:** Implement a `DatabasePool` singleton using `__new__`. It should store `max_connections`. Calling `DatabasePool(20)` after `DatabasePool(5)` should return the original instance with `max_connections=5`. Include a `reset()` classmethod for testing.

<details>
<summary>💡 Hint</summary>
Store the instance as `_instance = None`. Use an `_initialized` flag to prevent `__init__` from running twice.
</details>

<details>
<summary>✅ Answer</summary>

```python
class DatabasePool:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, max_connections: int = 10):
        if self._initialized:
            return
        self.max_connections = max_connections
        self._connections    = []
        self._initialized    = True

    @classmethod
    def reset(cls):
        cls._instance = None

pool1 = DatabasePool(5)
pool2 = DatabasePool(20)
assert pool1 is pool2
assert pool2.max_connections == 5
```

**Why:** `__new__` returns the cached instance. The `_initialized` guard prevents `__init__` from resetting attributes on subsequent calls.
</details>

---

### Q3 🟡 · singleton · Thread-Safe Singleton

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

**Problem:** Implement a thread-safe singleton using double-checked locking. Launch 10 threads that all call the constructor simultaneously and verify that only one instance is ever created.

<details>
<summary>💡 Hint</summary>
Use `threading.Lock`. Check `_instance is None` both outside and inside the lock.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading

class ThreadSafeSingleton:
    _instance = None
    _lock      = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:           # fast path — no lock if already set
            with cls._lock:
                if cls._instance is None:   # second check inside the lock
                    cls._instance = super().__new__(cls)
        return cls._instance

results = []

def create_instance():
    inst = ThreadSafeSingleton()
    results.append(id(inst))

threads = [threading.Thread(target=create_instance) for _ in range(10)]
for t in threads: t.start()
for t in threads: t.join()

assert len(set(results)) == 1   # all threads got the same instance
```

**Why:** Without the inner check, two threads passing the outer `None` check simultaneously would both create instances. The inner check (inside the lock) prevents that.
</details>

---

### Q4 🟡 · singleton · Borg Pattern

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

**Problem:** Implement a `Logger` using the Borg (Monostate) pattern. Create two Logger instances and verify: `log1 is log2` is `False` (different objects), but a log entry written via `log1` is visible via `log2` (shared state).

<details>
<summary>💡 Hint</summary>
Set `self.__dict__ = Logger._shared_state` in `__init__`. The class-level `_shared_state = {}` is the single shared dictionary.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Logger:
    _shared_state: dict = {}

    def __init__(self):
        self.__dict__ = Logger._shared_state
        if not hasattr(self, "_ready"):
            self._entries  = []
            self._level    = "INFO"
            self._ready    = True

    def log(self, level: str, msg: str) -> None:
        self._entries.append(f"[{level}] {msg}")

    def set_level(self, level: str) -> None:
        self._level = level

log1 = Logger()
log2 = Logger()
assert log1 is not log2
log1.log("INFO", "started")
assert log2._entries == ["[INFO] started"]
log1.set_level("DEBUG")
assert log2._level == "DEBUG"
```

**Why:** All `Logger` instances share the same `__dict__` dictionary. Any attribute change is immediately visible through all instances.
</details>

---

### Q5 🟡 · factory · Simple Factory Function

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

**Problem:** Write a `create_notification(channel)` factory function that returns `EmailNotification`, `SMSNotification`, or `PushNotification` based on the string argument. Use a dict for dispatch. Raise `ValueError` for unknown channels.

<details>
<summary>💡 Hint</summary>
Use `{"email": EmailNotification, "sms": SMSNotification}` and call `factories[channel]()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def send(self, message: str, recipient: str) -> dict: ...

class EmailNotification(Notification):
    def send(self, message, recipient):
        return {"channel": "email", "to": recipient}

class SMSNotification(Notification):
    def send(self, message, recipient):
        return {"channel": "sms", "to": recipient}

class PushNotification(Notification):
    def send(self, message, recipient):
        return {"channel": "push", "device": recipient}

def create_notification(channel: str) -> Notification:
    factories = {
        "email": EmailNotification,
        "sms":   SMSNotification,
        "push":  PushNotification,
    }
    if channel not in factories:
        raise ValueError(f"Unknown channel: {channel!r}")
    return factories[channel]()
```

**Why:** Dict dispatch replaces an if/elif chain. Adding a new channel requires only adding a new class and one dict entry — no modification to the function.
</details>

---

### Q6 🟡 · factory · Factory Method with ABC

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

**Problem:** Implement a `DataParser` abstract class with a `create_reader()` factory method. Create `JSONParser` and `CSVParser` subclasses. The base `process(raw)` method calls `create_reader()` and uses the returned reader's `.read()` method.

<details>
<summary>💡 Hint</summary>
The abstract class defines `process()` which calls `self.create_reader()`. Each subclass overrides `create_reader()` to return the right reader type.
</details>

<details>
<summary>✅ Answer</summary>

```python
import json
from abc import ABC, abstractmethod

class DataReader(ABC):
    @abstractmethod
    def read(self, raw: str) -> list: ...

class JSONReader(DataReader):
    def read(self, raw: str) -> list:
        return json.loads(raw)

class CSVReader(DataReader):
    def read(self, raw: str) -> list:
        lines   = raw.strip().split("\n")
        headers = lines[0].split(",")
        return [dict(zip(headers, line.split(","))) for line in lines[1:]]

class DataParser(ABC):
    @abstractmethod
    def create_reader(self) -> DataReader: ...    # factory method

    def process(self, raw: str) -> dict:
        reader = self.create_reader()
        data   = reader.read(raw)
        return {"rows": len(data), "data": data}

class JSONParser(DataParser):
    def create_reader(self): return JSONReader()

class CSVParser(DataParser):
    def create_reader(self): return CSVReader()
```

**Why:** `process()` is defined once in the base class. Subclasses only override the factory method to plug in the right reader.
</details>

---

### Q7 🟡 · factory · Registration Factory (Dict-Based Dispatch)

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

**Problem:** Build a `ReportFactory` with a `@register(name)` class decorator. Implement `CSVReport` and `JSONReport` that self-register. Factory's `create(report_type)` should return the right instance without any if/elif.

<details>
<summary>💡 Hint</summary>
The `register` classmethod returns a decorator that stores the class in `_registry[name]`. `create()` looks up `_registry[report_type]()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import json
from abc import ABC, abstractmethod

class ReportFactory:
    _registry: dict = {}

    @classmethod
    def register(cls, name: str):
        def decorator(report_cls):
            cls._registry[name] = report_cls
            return report_cls
        return decorator

    @classmethod
    def create(cls, report_type: str, **kwargs):
        if report_type not in cls._registry:
            raise KeyError(f"Unknown: {report_type!r}. Available: {list(cls._registry)}")
        return cls._registry[report_type](**kwargs)

class Report(ABC):
    @abstractmethod
    def render(self, data: list) -> str: ...

@ReportFactory.register("csv")
class CSVReport(Report):
    def render(self, data: list) -> str:
        if not data: return ""
        headers = ",".join(data[0].keys())
        rows    = [",".join(str(v) for v in row.values()) for row in data]
        return "\n".join([headers] + rows)

@ReportFactory.register("json")
class JSONReport(Report):
    def render(self, data: list) -> str:
        return json.dumps(data, indent=2)
```

**Why:** Adding a new report type requires only creating the class and adding `@ReportFactory.register("new_type")`. The factory code never changes.
</details>

---

### Q8 🟠 · factory · Abstract Factory for Cross-Platform UI

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

**Problem:** Build a `UIFactory` abstract factory with `create_button(label)` and `create_dialog(title)` methods. Implement `LightThemeFactory` and `DarkThemeFactory`. Write a `build_login_form(factory)` function that uses only the factory interface.

<details>
<summary>💡 Hint</summary>
The abstract factory defines the interface. Each concrete factory returns consistent (same-theme) components. `build_login_form` never imports concrete classes.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class Button(ABC):
    @abstractmethod
    def render(self) -> str: ...

class Dialog(ABC):
    @abstractmethod
    def render(self) -> str: ...

class UIFactory(ABC):
    @abstractmethod
    def create_button(self, label: str) -> Button: ...
    @abstractmethod
    def create_dialog(self, title: str) -> Dialog: ...

class LightButton(Button):
    def __init__(self, label): self.label = label
    def render(self): return f"[  {self.label}  ] (light)"

class LightDialog(Dialog):
    def __init__(self, title): self.title = title
    def render(self): return f"╔══ {self.title} ══╗ (light)"

class DarkButton(Button):
    def __init__(self, label): self.label = label
    def render(self): return f"▓▓ {self.label} ▓▓ (dark)"

class DarkDialog(Dialog):
    def __init__(self, title): self.title = title
    def render(self): return f"█══ {self.title} ══█ (dark)"

class LightThemeFactory(UIFactory):
    def create_button(self, label): return LightButton(label)
    def create_dialog(self, title): return LightDialog(title)

class DarkThemeFactory(UIFactory):
    def create_button(self, label): return DarkButton(label)
    def create_dialog(self, title): return DarkDialog(title)

def build_login_form(factory: UIFactory) -> None:
    dialog = factory.create_dialog("Login")
    button = factory.create_button("Sign In")
    print(dialog.render())
    print(button.render())
```

**Why:** Client code (`build_login_form`) depends only on the abstract `UIFactory` interface. Swapping the entire theme requires changing one argument.
</details>

---

### Q9 🟡 · factory · When to Use Each Factory Variant

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

**Problem:** Given these three scenarios, choose the right factory variant and justify your answer:

1. A `create_parser(format)` function used internally in one file
2. A plugin system where third-party developers add new exporters
3. A cross-platform system that must produce matching DB connection + query builder + transaction manager

<details>
<summary>💡 Hint</summary>
Think about extensibility, who adds new types, and whether objects must be consistent with each other.
</details>

<details>
<summary>✅ Answer</summary>

```python
# Scenario 1: Simple factory function — internal, no extensibility needed
def create_parser(format: str):
    return {"json": JSONParser, "csv": CSVParser}[format]()

# Scenario 2: Registration factory — third-parties add types via decorator
class ExporterFactory:
    _registry = {}
    @classmethod
    def register(cls, name):
        def dec(exporter_cls):
            cls._registry[name] = exporter_cls
            return exporter_cls
        return dec
    @classmethod
    def create(cls, name): return cls._registry[name]()

@ExporterFactory.register("excel")
class ExcelExporter: ...

# Scenario 3: Abstract factory — entire family must be consistent
class PostgresFactory(DBFactory):
    def create_connection(self): return PgConnection()
    def create_query_builder(self): return PgQueryBuilder()
    def create_transaction(self): return PgTransaction()
```

**Why:**
1. Simple factory — internal use, one file, no external extension needed.
2. Registration — open/closed: new types added without modifying factory code.
3. Abstract factory — objects in the family must be mutually compatible (Postgres objects should not mix with SQLite objects).
</details>

---

### Q10 🟠 · factory + singleton · Capstone: Plugin Registry

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

**Problem:** Build a `PluginRegistry` that is a Singleton and acts as a registration factory. It should support `@PluginRegistry.register("name")` to register plugin classes. `PluginRegistry.get("name")` returns an instance. The registry itself must be the same object no matter how many times it is constructed.

<details>
<summary>💡 Hint</summary>
Combine `__new__`-based Singleton with a `_plugins` dict. The `register` classmethod is a decorator factory.
</details>

<details>
<summary>✅ Answer</summary>

```python
class PluginRegistry:
    _instance = None
    _plugins: dict = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, name: str):
        def decorator(plugin_cls):
            cls._plugins[name] = plugin_cls
            return plugin_cls
        return decorator

    @classmethod
    def get(cls, name: str):
        if name not in cls._plugins:
            raise KeyError(f"Plugin not found: {name!r}")
        return cls._plugins[name]()

    @classmethod
    def list_plugins(cls) -> list:
        return list(cls._plugins.keys())

    @classmethod
    def reset(cls):
        cls._instance = None
        cls._plugins  = {}

@PluginRegistry.register("csv_importer")
class CSVImporter:
    def run(self): return "importing CSV"

@PluginRegistry.register("json_importer")
class JSONImporter:
    def run(self): return "importing JSON"

r1 = PluginRegistry()
r2 = PluginRegistry()
assert r1 is r2
plugin = PluginRegistry.get("csv_importer")
assert plugin.run() == "importing CSV"
assert "json_importer" in PluginRegistry.list_plugins()
```

**Why:** The Singleton ensures the registry is the same object everywhere. The registration pattern keeps the registry open for extension — adding a plugin requires only creating the class and the decorator.
</details>

---

## 📂 Navigation

**[🏠 Back to README](../../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [02 Behavioral — Practice →](../02_behavioral/practice.md)

**Related Topics:** [Theory](./theory.md) · [02 Behavioral](../02_behavioral/practice.md) · [Root Practice](../practice.md)
