# 🧩 18 — Mixins: Reusable Behavior Without Full Inheritance

> *"Inheritance says 'I am a kind of X.'*
> *Mixins say 'I have this ability.'*
> *The difference changes how you design entire systems."*

---

## 🎬 The Story

You're building a system with many different classes:
- `User`, `Product`, `Order`, `Report`, `LogEntry`

All of them need to:
- Be serializable to JSON
- Log every change they make
- Have a `to_dict()` method

You could add these methods to each class individually — that's 5× the code and 5× the bugs.
You could make them all inherit from a giant `BaseModel` — but they're not really the same *kind of* thing.

**Mixins solve this** — write the behaviour once, drop it into any class that needs it.

---

## 🔑 What Is a Mixin?

A **Mixin** is a class that:
- Provides a specific, reusable set of methods
- Is NOT meant to be instantiated on its own
- Is designed to be combined with other classes via multiple inheritance
- Does NOT represent a full concept (it's not a "thing" — it's an "ability")

```
INHERITANCE asks:   "What IS this?"        → use for IS-A relationships
MIXIN asks:         "What can this DO?"    → use for HAS-A-ABILITY relationships

User                IS-A     Person          (inheritance)
User                HAS      serialization   (mixin)
User                HAS      logging         (mixin)
```

---

## 🔧 Your First Mixin

```python
class JSONMixin:
    """Add JSON serialization to any class."""

    def to_json(self):
        import json
        return json.dumps(self.__dict__, default=str)

    @classmethod
    def from_json(cls, json_str):
        import json
        data = json.loads(json_str)
        obj = cls.__new__(cls)   # create without calling __init__
        obj.__dict__.update(data)
        return obj


class User:
    def __init__(self, name, email, age):
        self.name  = name
        self.email = email
        self.age   = age


# Mix it in — User now gains JSON abilities:
class User(JSONMixin, User):
    pass

# OR just define it directly:
class Product(JSONMixin):
    def __init__(self, name, price):
        self.name  = name
        self.price = price


p = Product("Laptop", 80000)
print(p.to_json())
# {"name": "Laptop", "price": 80000}

p2 = Product.from_json('{"name": "Phone", "price": 30000}')
print(p2.name)    # Phone
```

---

## 🏗️ Multiple Mixins — Stacking Abilities

The real power: stack multiple mixins to compose behaviour.

```python
import json
from datetime import datetime


class JSONMixin:
    """Serialize/deserialize to JSON."""

    def to_json(self):
        return json.dumps(self.__dict__, default=str)

    def to_dict(self):
        return dict(self.__dict__)


class TimestampMixin:
    """Track creation and update times automatically."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)          # cooperatively pass args up
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def touch(self):
        self.updated_at = datetime.now().isoformat()


class LogMixin:
    """Log every attribute change."""
    _log = []

    def __setattr__(self, name, value):
        if not name.startswith('_'):
            LogMixin._log.append(
                f"[{self.__class__.__name__}] {name} = {value!r}"
            )
        super().__setattr__(name, value)

    @classmethod
    def get_log(cls):
        return cls._log


class ValidateMixin:
    """Validate required fields before saving."""
    REQUIRED_FIELDS = []

    def validate(self):
        missing = [f for f in self.REQUIRED_FIELDS if not getattr(self, f, None)]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        return True


# ─── Now compose them freely ───

class User(JSONMixin, TimestampMixin, LogMixin, ValidateMixin):
    REQUIRED_FIELDS = ['name', 'email']

    def __init__(self, name, email):
        super().__init__()   # triggers TimestampMixin.__init__
        self.name  = name
        self.email = email


class Order(JSONMixin, TimestampMixin, LogMixin):
    def __init__(self, user_id, total):
        super().__init__()
        self.user_id = user_id
        self.total   = total


# ─── Using the composed classes ───

u = User("Alice", "alice@mail.com")
print(u.to_json())
# {"name": "Alice", "email": "alice@mail.com", "created_at": "...", "updated_at": "..."}

u.validate()    # ✓ passes

u.name = "Alice Updated"
u.touch()

print(LogMixin.get_log()[:3])
# ['[User] name = "Alice"', '[User] email = "alice@mail.com"', ...]

o = Order(user_id=1, total=5000)
print(o.to_dict())
# {'user_id': 1, 'total': 5000, 'created_at': '...', 'updated_at': '...'}
```

---

## 🔍 Real-World Mixin Patterns

### Pattern 1 — Repr Mixin

```python
class ReprMixin:
    """Auto-generate __repr__ from all public attributes."""

    def __repr__(self):
        attrs = ', '.join(
            f"{k}={v!r}"
            for k, v in self.__dict__.items()
            if not k.startswith('_')
        )
        return f"{self.__class__.__name__}({attrs})"


class Product(ReprMixin):
    def __init__(self, name, price):
        self.name  = name
        self.price = price


p = Product("Laptop", 80000)
print(p)    # Product(name='Laptop', price=80000)
```

---

### Pattern 2 — Equality Mixin

```python
class EqualityMixin:
    """Compare objects by their __dict__."""

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))


class Point(EqualityMixin):
    def __init__(self, x, y):
        self.x = x
        self.y = y


p1 = Point(1, 2)
p2 = Point(1, 2)
p3 = Point(3, 4)

print(p1 == p2)    # True
print(p1 == p3)    # False
print({p1, p2})    # {Point} — hashable, deduped
```

---

### Pattern 3 — Singleton Mixin

```python
class SingletonMixin:
    """Only one instance allowed per class."""
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]


class DatabaseConnection(SingletonMixin):
    def __init__(self, url):
        if not hasattr(self, '_initialized'):
            self.url  = url
            self._initialized = True


db1 = DatabaseConnection("postgresql://localhost/mydb")
db2 = DatabaseConnection("postgresql://localhost/other")

print(db1 is db2)    # True — same instance!
print(db1.url)       # postgresql://localhost/mydb  (first one wins)
```

---

### Pattern 4 — Observable / Event Mixin

```python
class ObservableMixin:
    """Emit events when attributes change."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._listeners = {}

    def on(self, event, callback):
        self._listeners.setdefault(event, []).append(callback)

    def emit(self, event, data=None):
        for cb in self._listeners.get(event, []):
            cb(data)

    def __setattr__(self, name, value):
        if not name.startswith('_'):
            old = getattr(self, name, None)
            super().__setattr__(name, value)
            if old != value:
                self.emit(f"{name}_changed", {"old": old, "new": value})
        else:
            super().__setattr__(name, value)


class UserProfile(ObservableMixin):
    def __init__(self, name, status):
        super().__init__()
        self.name   = name
        self.status = status


profile = UserProfile("Alice", "active")

# Register listeners:
profile.on("status_changed", lambda d: print(f"Status changed: {d}"))
profile.on("name_changed",   lambda d: print(f"Name changed: {d}"))

profile.status = "inactive"   # → Status changed: {'old': 'active', 'new': 'inactive'}
profile.name   = "Alice B."   # → Name changed: {'old': 'Alice', 'new': 'Alice B.'}
```

---

## 🗂️ Mixin Rules and Conventions

```
NAMING CONVENTION:
  Always end mixin class names with "Mixin"
  → JSONMixin, LogMixin, ReprMixin, CacheMixin
  → This signals: "this is not a standalone class"

PLACEMENT IN INHERITANCE:
  Mixins should come BEFORE the main class in the inheritance list
  ✓  class User(LogMixin, JSONMixin, BaseUser)  ← mixins first
  ✗  class User(BaseUser, LogMixin, JSONMixin)  ← main class first

WHY ORDER MATTERS:
  Python's MRO processes left to right.
  Mixins first ensures their __get__/__set__/__init__ run before the main class.

COOPERATIVE SUPER():
  Every mixin that has __init__ MUST call super().__init__(*args, **kwargs)
  This ensures the full MRO chain initializes properly.
```

---

## 📊 MRO With Mixins

```python
class JSONMixin:
    def to_json(self): ...

class LogMixin:
    def __setattr__(self, name, value): ...
    def __init__(self, *a, **kw): super().__init__(*a, **kw)

class BaseModel:
    def __init__(self, id):
        self.id = id

class User(JSONMixin, LogMixin, BaseModel):
    def __init__(self, id, name):
        super().__init__(id)
        self.name = name


print([c.__name__ for c in User.__mro__])
# ['User', 'JSONMixin', 'LogMixin', 'BaseModel', 'object']
```

```
When User is created:
  User.__init__
    → super().__init__(id)   → LogMixin.__init__
      → super().__init__(id) → BaseModel.__init__
                               self.id = id  ✓
```

---

## ⚠️ Mixin Traps

### Trap 1 — Mixin Forgetting `super()`

```python
# ❌ BAD — LogMixin breaks the chain:
class LogMixin:
    def __init__(self, *args, **kwargs):
        self._log = []
        # ← forgot super().__init__() — BaseModel.__init__ never called!

class User(LogMixin, BaseModel):
    def __init__(self, id, name):
        super().__init__(id)
        self.name = name

u = User(1, "Alice")
# BaseModel.__init__ never ran — self.id was never set!
```

```python
# ✅ GOOD — cooperative super() ensures full chain:
class LogMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   # ← passes ALL args forward!
        self._log = []
```

---

### Trap 2 — Mixin Ordering Bug

```python
# ❌ WRONG: main class first, mixins override nothing:
class User(BaseModel, LogMixin, JSONMixin):
    pass

# ✅ RIGHT: mixins first, they get priority:
class User(LogMixin, JSONMixin, BaseModel):
    pass
```

---

### Trap 3 — Mixin Knows Too Much

```python
# ❌ BAD — mixin is tightly coupled to specific class:
class BadMixin:
    def greet(self):
        return f"Hello, I am {self.first_name} {self.last_name}"   # ← assumes attributes exist!

# ✅ GOOD — mixin uses getattr with defaults:
class GoodMixin:
    def greet(self):
        name = getattr(self, 'name', getattr(self, 'username', 'Unknown'))
        return f"Hello, I am {name}"
```

---

### Trap 4 — Mixin with Class-Level State

```python
# ❌ DANGEROUS — all classes share the same list!
class LogMixin:
    _log = []    # ← class variable shared across ALL users of this mixin!

class User(LogMixin): pass
class Order(LogMixin): pass

User._log.append("u1")
Order._log.append("o1")

print(User._log)    # ['u1', 'o1']  ← polluted!

# ✅ SAFE — use instance variable in __init__:
class LogMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._log = []    # ← instance-level, isolated per object
```

---

## 🆚 Mixin vs Inheritance vs Composition

```
┌─────────────────────────────────────────────────────────────────────┐
│                    WHEN TO USE WHAT                                  │
├──────────────────┬──────────────────────────────────────────────────┤
│  Inheritance     │  IS-A relationship                               │
│                  │  Dog IS-A Animal                                  │
│                  │  SavingsAccount IS-A BankAccount                 │
├──────────────────┼──────────────────────────────────────────────────┤
│  Mixin           │  HAS-AN-ABILITY relationship                     │
│                  │  User HAS serialization                           │
│                  │  Model HAS logging                                │
│                  │  Cross-cutting concerns (any class can use it)   │
├──────────────────┼──────────────────────────────────────────────────┤
│  Composition     │  HAS-A relationship (object containment)         │
│                  │  Car HAS-A Engine                                 │
│                  │  User HAS-A Address                               │
│                  │  Complex behavior requiring its own state        │
└──────────────────┴──────────────────────────────────────────────────┘
```

---

## 🎯 Key Takeaways

```
• Mixin = class that adds specific abilities, not a full concept
• Always name mixins with "Mixin" suffix (JSONMixin, LogMixin)
• Place mixins BEFORE the main class in inheritance list
• Every mixin __init__ MUST call super().__init__(*args, **kwargs)
• Don't let mixins have class-level mutable state (causes shared bugs)
• Mixins should be loosely coupled — don't assume specific attributes exist
• Use getattr(self, 'attr', default) for safety in mixin methods
• Mixin vs Inheritance: ability vs identity
• Mixin vs Composition: multiple inheritance trick vs object containment
• Real use: logging, serialization, validation, caching, events, repr
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [17 — Descriptors](./17_descriptors.md) |
| 📖 Index | [README.md](./README.md) |
| ➡️ Next | [19 — SOLID Principles](./19_solid_principles.md) |
