# Practice — Metaclasses

| Q | Difficulty | Topic |
|---|-----------|-------|
| [Q1](#q1--dynamic-class-creation) | 🟢 | `type()` to create a class dynamically |
| [Q2](#q2--auto-uppercase-methods) | 🟡 | Metaclass auto-converts method names |
| [Q3](#q3--new-vs-init-on-metaclass) | 🟡 | `__new__` vs `__init__` on metaclass |
| [Q4](#q4--singleton-via-metaclass) | 🟡 | Singleton metaclass |
| [Q5](#q5--auto-registration) | 🟡 | Auto-registration metaclass |
| [Q6](#q6--prepare) | 🟡 | `__prepare__` — ordered namespace |
| [Q7](#q7--enforce-docstrings) | 🟠 | Metaclass enforcing docstrings |
| [Q8](#q8--abcmeta) | 🟠 | ABCMeta and `@abstractmethod` |
| [Q9](#q9--metaclass-vs-init_subclass) | 🟠 | Metaclass vs `__init_subclass__` |
| [Q10](#q10--validate-class-attributes) | 🟠 | Metaclass validates class-level attributes |

---

### Q1 🟢 · dynamic class — call `type()` to create a class dynamically

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

**Problem:** Use `type()` (three-argument form) to create a `Rectangle` class dynamically, with `width` and `height` attributes, an `area()` method, and a `__repr__`. Do not write a class statement.

<details>
<summary>💡 Hint</summary>
`type(name, bases, namespace)` — `name` is a string, `bases` is a tuple of parent classes, `namespace` is a dict mapping attribute names to values/functions.
</details>

<details>
<summary>✅ Answer</summary>

```python
Rectangle = type(
    "Rectangle",         # class name
    (object,),           # bases
    {
        "__init__": lambda self, width, height: (
            setattr(self, "width", width) or setattr(self, "height", height)
        ),
        "area":     lambda self: self.width * self.height,
        "__repr__": lambda self: f"Rectangle(width={self.width}, height={self.height})",
    }
)

r = Rectangle(4, 5)
print(r)           # Rectangle(width=4, height=5)
print(r.area())    # 20
print(type(r))     # <class '__main__.Rectangle'>
print(type(Rectangle))  # <class 'type'>
```

**Why:** Every class statement ultimately calls `type(name, bases, namespace)`. Understanding this reveals that classes are just regular objects — instances of `type`.
</details>

---

### Q2 🟡 · name transformation — metaclass that auto-converts all method names to uppercase

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

**Problem:** Write a metaclass `UpperMethodMeta` that converts all method names to uppercase. A class using it where you define `def get_user(self)` should have that method accessible as `GET_USER`.

<details>
<summary>💡 Hint</summary>
In `__new__`, iterate over the namespace dict. For each callable value (that doesn't start with `_`), add it to the new namespace under the uppercased key.
</details>

<details>
<summary>✅ Answer</summary>

```python
class UpperMethodMeta(type):
    def __new__(mcs, name, bases, namespace):
        new_ns = {}
        for key, value in namespace.items():
            if callable(value) and not key.startswith('_'):
                new_ns[key.upper()] = value   # add uppercase version
            else:
                new_ns[key] = value
        return super().__new__(mcs, name, bases, new_ns)

class APIClient(metaclass=UpperMethodMeta):
    def get_user(self, user_id):
        return {"id": user_id}

    def list_users(self):
        return []

client = APIClient()
print(client.GET_USER(42))   # {'id': 42}
print(client.LIST_USERS())   # []
```

**Why:** Metaclasses intercept class creation and can reshape the namespace — adding, removing, or renaming methods before the class object is built.
</details>

---

### Q3 🟡 · creation flow — metaclass `__new__` vs `__init__`

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

**Problem:** Write a metaclass that has both `__new__` and `__init__`. Add a `_created` timestamp in `__new__` (to the namespace) and print a log message in `__init__`. Show which runs when and demonstrate the difference.

<details>
<summary>💡 Hint</summary>
`__new__` receives the namespace dict BEFORE the class is created — you can modify it. `__init__` receives the already-created class object — you can inspect it but namespace modifications have no effect.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time

class TimestampMeta(type):
    def __new__(mcs, name, bases, namespace):
        # Runs BEFORE the class exists — can modify namespace
        namespace['_created_at'] = time.time()
        namespace['_created_by'] = 'TimestampMeta'
        print(f"  __new__: creating {name}")
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace):
        # Runs AFTER the class exists — cls is the created class
        super().__init__(name, bases, namespace)
        print(f"  __init__: initialized {name}, has _created_at={hasattr(cls, '_created_at')}")

class MyService(metaclass=TimestampMeta):
    def process(self): pass

print(f"MyService._created_by = {MyService._created_by}")
# Output:
#   __new__: creating MyService
#   __init__: initialized MyService, has _created_at=True
#   MyService._created_by = TimestampMeta
```

**Why:** Use `__new__` when you need to modify the namespace before the class object is built. Use `__init__` when you just need to do something after the class is created. `__new__` is more powerful but also more complex.
</details>

---

### Q4 🟡 · singleton — singleton via metaclass

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

**Problem:** Write a `SingletonMeta` metaclass that ensures each class using it can only have one instance. Calling `MyClass()` a second time should return the same instance, not create a new one.

<details>
<summary>💡 Hint</summary>
Override `__call__` on the metaclass. `type.__call__` is what runs when you call `cls(...)` — it invokes `cls.__new__` and `cls.__init__`. Store instances in a dict keyed by class.
</details>

<details>
<summary>✅ Answer</summary>

```python
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # super().__call__ runs __new__ + __init__:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self, url):
        self.url = url
        print(f"  Connecting to {url}")

class Cache(metaclass=SingletonMeta):
    def __init__(self):
        self.data = {}

db1 = Database("postgresql://localhost/app")  # prints "Connecting..."
db2 = Database("postgresql://other")          # NOT printed — returns same instance
cache1 = Cache()
cache2 = Cache()

print(db1 is db2)       # True
print(cache1 is cache2) # True
print(db1 is cache1)    # False — different classes, different singletons
```

**Why:** The metaclass's `__call__` controls what happens when `cls()` is invoked. Intercepting it at the metaclass level is the cleanest singleton implementation.
</details>

---

### Q5 🟡 · registration — auto-registration metaclass tracks all subclasses

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

**Problem:** Write a `RegistryMeta` that automatically registers every concrete subclass in a class-level dict `_registry`. The root class itself should NOT be registered. Provide a `dispatch(name, *args)` classmethod that instantiates by name.

<details>
<summary>💡 Hint</summary>
In `__new__`, check if `bases` is non-empty to skip the root class. Register in `mcs._registry` keyed by class name.
</details>

<details>
<summary>✅ Answer</summary>

```python
class RegistryMeta(type):
    _registry = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases:   # skip root class (no bases)
            mcs._registry[name] = cls
        return cls

class Serializer(metaclass=RegistryMeta):
    def serialize(self, data): raise NotImplementedError

    @classmethod
    def dispatch(cls, name, data):
        handler = RegistryMeta._registry.get(name)
        if handler is None:
            raise KeyError(f"No serializer named {name!r}")
        return handler().serialize(data)

class JSONSerializer(Serializer):
    def serialize(self, data):
        import json; return json.dumps(data)

class CSVSerializer(Serializer):
    def serialize(self, data):
        return ",".join(str(v) for v in data)

print(RegistryMeta._registry)   # {'JSONSerializer': ..., 'CSVSerializer': ...}
print(Serializer.dispatch("JSONSerializer", {"key": "val"}))
print(Serializer.dispatch("CSVSerializer",  [1, 2, 3]))
```

**Why:** Auto-registration means adding a new subclass is the only step needed — no manual registration calls. This is the foundation of plugin architectures.
</details>

---

### Q6 🟡 · namespace — `__prepare__` return an OrderedDict to preserve method order

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

**Problem:** Write a metaclass with `__prepare__` that returns an `OrderedDict`. After class creation, store the list of method names (in definition order) as `cls._method_order`. Demonstrate that order is preserved.

<details>
<summary>💡 Hint</summary>
`__prepare__` is a classmethod on the metaclass. It's called before the class body executes and its return value is the namespace used for collecting the class body.
</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import OrderedDict

class OrderedMeta(type):
    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        return OrderedDict()   # class body collected into this

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        cls._method_order = [
            k for k in namespace
            if not k.startswith('_') and callable(namespace[k])
        ]
        return cls

class MyAPI(metaclass=OrderedMeta):
    def authenticate(self): pass
    def get_resource(self): pass
    def update_resource(self): pass
    def delete_resource(self): pass

print(MyAPI._method_order)
# ['authenticate', 'get_resource', 'update_resource', 'delete_resource']
```

**Why:** `__prepare__` lets you substitute a custom dict as the class namespace. This can be used to track definition order, intercept attribute creation, or pre-populate the namespace.
</details>

---

### Q7 🟠 · enforcement — metaclass that enforces all methods are documented

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

**Problem:** Write a `DocumentedMeta` metaclass that raises `TypeError` at class definition time if any public method lacks a docstring. Allow opting out with `__no_docs_check__ = True` on the class.

<details>
<summary>💡 Hint</summary>
In `__new__`, iterate namespace items. Check `callable(value) and not key.startswith('_')` for public methods. `value.__doc__` is `None` if no docstring.
</details>

<details>
<summary>✅ Answer</summary>

```python
class DocumentedMeta(type):
    def __new__(mcs, name, bases, namespace):
        if not namespace.get('__no_docs_check__', False):
            for attr, value in namespace.items():
                if attr.startswith('_'):
                    continue
                if callable(value) and not value.__doc__:
                    raise TypeError(
                        f"{name}.{attr}: public methods must have a docstring"
                    )
        return super().__new__(mcs, name, bases, namespace)

class GoodService(metaclass=DocumentedMeta):
    def get_user(self, user_id):
        """Retrieve user by ID."""
        return {}

    def list_users(self):
        """List all users."""
        return []

print("GoodService passed validation!")

# This would raise TypeError at class definition:
# class BadService(metaclass=DocumentedMeta):
#     def get_user(self, user_id):   # no docstring!
#         return {}
```

**Why:** Catching documentation issues at import time is far better than discovering them during code review or at runtime. The metaclass acts as a static analyzer baked into the class system.
</details>

---

### Q8 🟠 · ABCMeta — abstract base class with `@abstractmethod`

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

**Problem:** Create an abstract `StorageBackend` class using `ABC` with abstract methods `save(key, value)`, `load(key)`, and `delete(key)`. Create a concrete `MemoryBackend`. Show that `StorageBackend()` raises `TypeError`.

<details>
<summary>💡 Hint</summary>
`from abc import ABC, abstractmethod`. `ABC` is just `class ABC(metaclass=ABCMeta)`. Abstract methods use `@abstractmethod` decorator. Subclasses MUST implement all abstract methods before they can be instantiated.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class StorageBackend(ABC):
    """Abstract interface — any concrete storage must implement these."""

    @abstractmethod
    def save(self, key: str, value) -> None:
        """Store a value under key."""
        ...

    @abstractmethod
    def load(self, key: str):
        """Retrieve value by key; raise KeyError if not found."""
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove a key from storage."""
        ...

    def exists(self, key: str) -> bool:
        """Default implementation using load."""
        try:
            self.load(key)
            return True
        except KeyError:
            return False

# Can't instantiate abstract class:
try:
    StorageBackend()
except TypeError as e:
    print(f"Caught: {e}")

class MemoryBackend(StorageBackend):
    def __init__(self):
        self._store = {}

    def save(self, key, value):
        self._store[key] = value

    def load(self, key):
        if key not in self._store: raise KeyError(key)
        return self._store[key]

    def delete(self, key):
        del self._store[key]

store = MemoryBackend()
store.save("x", 42)
print(store.load("x"))      # 42
print(store.exists("x"))    # True
print(store.exists("y"))    # False
```

**Why:** ABCs enforce contracts at instantiation time. If you forget to implement `delete`, you get a clear `TypeError: Can't instantiate abstract class...` rather than an `AttributeError` buried in a call stack.
</details>

---

### Q9 🟠 · comparison — metaclass vs `__init_subclass__`

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

**Problem:** Implement the same plugin registry pattern twice: once using a metaclass and once using `__init_subclass__`. Both should auto-register subclasses by name. Compare the two approaches.

<details>
<summary>💡 Hint</summary>
`__init_subclass__` is simpler for cases where you only need to run code when a subclass is defined. You don't get access to the class namespace before creation though.
</details>

<details>
<summary>✅ Answer</summary>

```python
# Approach 1: Metaclass
class MetaPlugin(type):
    _registry = {}
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases:
            mcs._registry[name] = cls
        return cls

class PluginBase1(metaclass=MetaPlugin):
    def run(self): raise NotImplementedError

class PluginA(PluginBase1):
    def run(self): return "PluginA"

# Approach 2: __init_subclass__
class PluginBase2:
    _registry = {}

    def __init_subclass__(cls, name="", **kwargs):
        super().__init_subclass__(**kwargs)   # MUST call super
        if name:
            PluginBase2._registry[name] = cls
        else:
            PluginBase2._registry[cls.__name__] = cls

    def run(self): raise NotImplementedError

class PluginB(PluginBase2):
    def run(self): return "PluginB"

print(MetaPlugin._registry)    # {'PluginA': ...}
print(PluginBase2._registry)   # {'PluginB': ...}

# Key differences:
# Metaclass: can modify namespace BEFORE class creation
# __init_subclass__: simpler, no metaclass conflict risk
# Both work for registration; prefer __init_subclass__ unless you need namespace access
```

**Why:** `__init_subclass__` is the modern preferred approach for most registration use cases. Use a full metaclass only when you need `__prepare__` or namespace modification before class creation.
</details>

---

### Q10 🟠 · validation — metaclass that validates class-level attributes at definition time

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

**Problem:** Write a `ValidatedModelMeta` metaclass that requires every subclass to declare `__tablename__` (a non-empty string) and `__fields__` (a non-empty list). Raise `TypeError` at class definition if they're missing or wrong type.

<details>
<summary>💡 Hint</summary>
In `__new__`, skip validation for the root base class. For subclasses, check `namespace.get('__tablename__')` and `namespace.get('__fields__')`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class ValidatedModelMeta(type):
    def __new__(mcs, name, bases, namespace):
        # Skip validation for the root base class (no model bases)
        is_base = not any(isinstance(b, ValidatedModelMeta) for b in bases)
        if not is_base:
            tablename = namespace.get('__tablename__')
            fields    = namespace.get('__fields__')

            if not isinstance(tablename, str) or not tablename:
                raise TypeError(f"{name}: must define __tablename__ as a non-empty string")

            if not isinstance(fields, list) or not fields:
                raise TypeError(f"{name}: must define __fields__ as a non-empty list")

        return super().__new__(mcs, name, bases, namespace)

class Model(metaclass=ValidatedModelMeta):
    pass   # base — not validated

class User(Model):
    __tablename__ = "users"
    __fields__ = ["id", "name", "email"]

print(f"User table: {User.__tablename__}, fields: {User.__fields__}")

# This raises TypeError at class definition:
try:
    class BadModel(Model):
        __tablename__ = ""   # empty string
        __fields__ = ["id"]
except TypeError as e:
    print(f"Caught: {e}")
```

**Why:** Catching structural errors at class-definition time (import time) is far earlier than catching them at runtime. The metaclass acts as a compile-time check for your data model contracts.
</details>

---

## Navigation

| | |
|---|---|
| Root theory | [../theory.md](../theory.md) |
| Subfolder theory | [theory.md](./theory.md) |
| Prev subfolder | [../02_descriptors/practice.md](../02_descriptors/practice.md) |
| Next subfolder | [../04_dataclasses/practice.md](../04_dataclasses/practice.md) |
| Root practice | [../practice.md](../practice.md) |
