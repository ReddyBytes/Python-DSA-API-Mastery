# Metaclasses — Deep Dive

In Python, everything is an object — including classes. A class is an instance of its **metaclass**. The default metaclass is `type`. Think of a metaclass as a **factory that builds factories**: regular factories (classes) build instances, but metaclasses build classes. This is the mechanism that powers Django models, SQLAlchemy, Pydantic, and ABCs.

> Key fact: when you write `class Dog: ...`, Python actually calls `type("Dog", (object,), namespace)`. A custom metaclass intercepts that call and can modify or validate the class before it exists.

---

## Learning Priority

**Must Learn:** `type()` as metaclass · class creation flow · `__new__` vs `__init__` on metaclass

**Should Learn:** custom metaclass · `__prepare__` · ABC metaclass pattern

**Good to Know:** metaclass for singleton · metaclass for auto-registration

**Reference:** `__instancecheck__` · `__subclasscheck__`

---

## Chapter 1: The Class Creation Flow

```
Instance relationship:
  42           is an instance of  int
  int          is an instance of  type
  type         is an instance of  type  (type is its own metaclass!)

You write:              Python executes:
--------------------------------------------------------------------
class Dog:              metaclass = type  (default)
    ...                 1. Execute class body in a fresh namespace dict
                        2. Call type("Dog", (object,), namespace)
                        3. type.__new__(type, "Dog", (object,), namespace)  → creates Dog
                        4. type.__init__(Dog, "Dog", (object,), namespace) → initializes Dog
```

---

## Chapter 2: `type()` — The Default Metaclass

Three-argument `type()` creates a class at runtime:

```python
Dog = type(
    "Dog",             # class name
    (object,),         # base classes (must be a tuple)
    {                  # class namespace
        "species": "Canis lupus",
        "__init__": lambda self, name: setattr(self, "name", name),
        "bark":     lambda self: f"{self.name} says Woof!",
    }
)

d = Dog("Rex")
print(d.bark())             # Rex says Woof!
print(type(d))              # <class '__main__.Dog'>
print(type(Dog))            # <class 'type'>
print(isinstance(Dog, type))  # True
```

This is identical to writing a normal class statement. Dynamic class creation is useful for generating classes from schemas, config files, or database models.

---

## Chapter 3: Custom Metaclass — `__new__` and `__init__`

A metaclass subclasses `type`. Its `__new__` intercepts class creation:

```python
class RegistryMeta(type):
    """Auto-registers every concrete subclass."""
    _registry = {}

    def __new__(mcs, name, bases, namespace):
        # mcs = the metaclass itself (like cls in regular __new__)
        # name, bases, namespace = same args as type.__new__
        cls = super().__new__(mcs, name, bases, namespace)

        if bases:   # ← skip the root base class itself
            mcs._registry[name] = cls
            print(f"Registered: {name}")

        return cls

class Handler(metaclass=RegistryMeta):
    """Abstract base — not registered (no bases before metaclass)."""
    def handle(self, data): raise NotImplementedError

class JSONHandler(Handler):      # prints: Registered: JSONHandler
    def handle(self, data):
        import json; return json.dumps(data)

class XMLHandler(Handler):       # prints: Registered: XMLHandler
    def handle(self, data):
        return f"<data>{data}</data>"

print(RegistryMeta._registry)   # {'JSONHandler': ..., 'XMLHandler': ...}
```

**`__new__` vs `__init__` on a metaclass:**

```
Metaclass.__new__(mcs, name, bases, namespace) → creates the class object
Metaclass.__init__(cls, name, bases, namespace) → initializes it

Use __new__ when you need to modify the namespace BEFORE the class exists.
Use __init__ when you just want to do something AFTER the class is created.
```

```python
class LogMeta(type):
    def __new__(mcs, name, bases, namespace):
        # Modify namespace before class creation:
        namespace['_created_by'] = 'LogMeta'
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace):
        # Run code after class exists:
        super().__init__(name, bases, namespace)
        print(f"Class {name} created with bases {[b.__name__ for b in bases]}")
```

---

## Chapter 4: Singleton Metaclass

```python
class SingletonMeta(type):
    """Makes every class using this metaclass a singleton."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        # __call__ on the metaclass controls what cls(*args) does
        if cls not in cls._instances:
            # super().__call__ runs cls.__new__ + cls.__init__:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self, url):
        self.url = url
        print(f"Connecting to {url}")

db1 = Database("postgresql://localhost/app")  # "Connecting..."
db2 = Database("postgresql://other")          # NOT printed — same instance returned
print(db1 is db2)   # True
```

---

## Chapter 5: Validation Metaclass

```python
class StrictMeta(type):
    """Enforces all public methods have docstrings — caught at import time."""

    def __new__(mcs, name, bases, namespace):
        for attr, value in namespace.items():
            if attr.startswith('_'):
                continue
            if callable(value) and not value.__doc__:
                raise TypeError(
                    f"{name}.{attr}: public methods must have a docstring"
                )
        return super().__new__(mcs, name, bases, namespace)

class GoodAPI(metaclass=StrictMeta):
    def get_user(self, user_id):
        """Retrieve user by ID."""
        return {}

# This would raise TypeError at class definition, not at call time:
# class BadAPI(metaclass=StrictMeta):
#     def get_user(self, user_id):   # ← no docstring
#         return {}
```

---

## Chapter 6: `__prepare__` — Custom Class Namespace

`__prepare__` is called before the class body executes. It returns the namespace dict for collecting the class body. Use it to return an `OrderedDict`, a custom mapping, or a dict with pre-populated values.

```python
from collections import OrderedDict

class OrderedMeta(type):
    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        # Return an OrderedDict — methods will be collected in definition order
        return OrderedDict()   # ← Python 3.7+ dicts are ordered anyway, but explicit here

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        cls._method_order = [k for k in namespace if not k.startswith('_')]
        return cls

class MyClass(metaclass=OrderedMeta):
    def first(self): pass
    def second(self): pass
    def third(self): pass

print(MyClass._method_order)   # ['first', 'second', 'third']
```

---

## Chapter 7: `__init_subclass__` — The Lightweight Alternative

For most use cases, `__init_subclass__` is simpler and cleaner than a full metaclass. It's a classmethod hook that fires whenever the class is subclassed.

```python
class Plugin:
    _registry = {}

    def __init_subclass__(cls, name="", **kwargs):
        super().__init_subclass__(**kwargs)   # ← MUST call super for cooperative MRO
        if name:
            Plugin._registry[name] = cls
            print(f"Registered plugin: {name!r} → {cls}")

class JSONPlugin(Plugin, name="json"):
    def serialize(self, data):
        import json; return json.dumps(data)

class CSVPlugin(Plugin, name="csv"):
    def serialize(self, data):
        return ",".join(str(x) for x in data)

print(Plugin._registry)   # {'json': JSONPlugin, 'csv': CSVPlugin}
```

**When to use metaclass vs `__init_subclass__`:**

```
Prefer __init_subclass__ when:          Prefer metaclass when:
------------------------------          -------------------------
You just want to run code on subclass   You need to modify the namespace
No need to change namespace             BEFORE class creation
No multiple metaclass conflicts         You need __prepare__
Simpler, more readable                  Framework-level plumbing
```

---

## Chapter 8: ABCMeta — Abstract Base Classes

ABCs use `ABCMeta` (a metaclass) to enforce that abstract methods are implemented. The enforcement happens in `type.__call__` at instantiation time.

```python
from abc import ABC, abstractmethod, ABCMeta

class Shape(ABC):
    """Abstract base class — cannot be instantiated."""

    @abstractmethod
    def area(self) -> float:
        """Return the area."""
        ...

    @abstractmethod
    def perimeter(self) -> float:
        """Return the perimeter."""
        ...

    def describe(self) -> str:
        return f"{type(self).__name__}: area={self.area():.2f}"

# Shape()  → TypeError: Can't instantiate abstract class Shape with abstract methods area, perimeter

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        import math; return math.pi * self.radius ** 2

    def perimeter(self):
        import math; return 2 * math.pi * self.radius

c = Circle(5)
print(c.describe())   # Circle: area=78.54
```

**Virtual subclasses — register without inheriting:**

```python
from abc import ABC

class Serializable(ABC):
    @abstractmethod
    def serialize(self): ...

@Serializable.register   # ← register without inheritance
class ExternalClass:
    def serialize(self):
        return "{}"

print(isinstance(ExternalClass(), Serializable))   # True — even without inheritance
```

---

## Chapter 9: ORM-Style Field Collection

```python
class Field:
    def __init__(self, field_type, required=True):
        self.field_type, self.required = field_type, required
        self.name = None

class ORMMeta(type):
    def __new__(mcs, name, bases, namespace):
        fields = {}
        for key, value in namespace.items():
            if isinstance(value, Field):
                value.name = key
                fields[key] = value

        # Inherit fields from parent classes:
        for base in reversed(bases):
            for key, value in vars(base).items():
                if isinstance(value, Field) and key not in fields:
                    fields[key] = value

        namespace['_fields'] = fields
        return super().__new__(mcs, name, bases, namespace)

class BaseModel(metaclass=ORMMeta):
    def __init__(self, **kwargs):
        for name, field in self._fields.items():
            value = kwargs.get(name)
            if field.required and value is None:
                raise ValueError(f"{name} is required")
            setattr(self, name, value)

class User(BaseModel):
    username = Field(str)
    age      = Field(int)
    email    = Field(str, required=False)

u = User(username="alice", age=30)
print(u.username, u.age)   # alice 30
```

---

## Common Mistakes

**Metaclass conflict:**
```python
class Meta1(type): pass
class Meta2(type): pass
class Base1(metaclass=Meta1): pass
class Base2(metaclass=Meta2): pass
# class Combined(Base1, Base2): pass  # TypeError: metaclass conflict!

# Fix: create a combined metaclass:
class CombinedMeta(Meta1, Meta2): pass
class Combined(Base1, Base2, metaclass=CombinedMeta): pass  # OK
```

**Forgetting `super().__init_subclass__(**kwargs)`:**
```python
class A:
    def __init_subclass__(cls, **kwargs):
        # If you forget super() here, B's __init_subclass__ never runs!
        super().__init_subclass__(**kwargs)  # ← ALWAYS call super

class B:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

class C(A, B): pass   # Both run correctly only if both call super()
```

**Modifying `namespace` after calling `super().__new__`:**
```python
class Meta(type):
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        # WRONG: namespace mutations here have no effect — class is already created
        namespace['new_attr'] = 42   # ← too late
        # CORRECT: modify namespace BEFORE calling super():
        # namespace['new_attr'] = 42
        # cls = super().__new__(mcs, name, bases, namespace)
```

---

## Navigation

| | |
|---|---|
| Root theory | [../theory.md](../theory.md) |
| Root practice | [../practice.md](../practice.md) |
| Practice | [practice.md](./practice.md) |
| Prev: Descriptors | [../02_descriptors/theory.md](../02_descriptors/theory.md) |
| Next: Dataclasses | [../04_dataclasses/theory.md](../04_dataclasses/theory.md) |

**[Back to 15_advanced_python](../theory.md)**
