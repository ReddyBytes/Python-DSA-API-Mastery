# Practice — Descriptors

| Q | Difficulty | Topic |
|---|-----------|-------|
| [Q1](#q1--property-under-the-hood) | 🟢 | How `@property` uses descriptors |
| [Q2](#q2--type-validator-descriptor) | 🟡 | Validator descriptor |
| [Q3](#q3--data-vs-non-data) | 🟡 | Data vs non-data descriptors |
| [Q4](#q4--set_name) | 🟡 | `__set_name__` auto-registration |
| [Q5](#q5--cached-descriptor) | 🟡 | Cached lazy descriptor |
| [Q6](#q6--typechecked-descriptor) | 🟡 | TypeChecked descriptor |
| [Q7](#q7--read-only-descriptor) | 🟠 | Read-only descriptor |
| [Q8](#q8--range-validation-descriptor) | 🟠 | Range validation descriptor |
| [Q9](#q9--rewrite-property) | 🟠 | Rewrite `@property` as a descriptor |
| [Q10](#q10--logging-descriptor) | 🟠 | Access logging descriptor |

---

### Q1 🟢 · property internals — How `@property` uses descriptors under the hood

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

**Problem:** Explain (in code) how `@property` is implemented as a descriptor. What does `Circle.radius` return when accessed on the class? What does `circle.radius` return when accessed on an instance?

<details>
<summary>💡 Hint</summary>
`property` has `__get__`, `__set__`, and `__delete__` — making it a data descriptor. When `obj is None` in `__get__`, return the descriptor object itself (class access). Otherwise call `fget(obj)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

c = Circle(5)
print(c.radius)           # 5 — calls property.__get__(c, Circle) → fget(c)
print(Circle.radius)      # <property object at 0x...> — obj is None, returns descriptor
print(type(Circle.radius)) # <class 'property'>

# property is a data descriptor: has __get__ AND __set__
# This is why @property intercepts access even when self.__dict__ exists
print(hasattr(type(Circle.radius), '__get__'))   # True
print(hasattr(type(Circle.radius), '__set__'))   # True
```

**Why:** `property` is a data descriptor — it has both `__get__` and `__set__`. Data descriptors take priority over instance `__dict__` (lookup step 1 beats step 2). That's why `self.radius` calls the property getter even though `self.__dict__` is right there.
</details>

---

### Q2 🟡 · validation — write a Validator descriptor that checks type on set

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

**Problem:** Write a `Typed` descriptor that enforces a specific type when an attribute is set. Use `__set_name__` to auto-configure the attribute name. Demonstrate it on a `Person` class with `name: str` and `age: int`.

<details>
<summary>💡 Hint</summary>
Store the value in `obj.__dict__` using a private key (e.g., `_name`). Handle the `obj is None` case in `__get__` to return the descriptor when accessed via the class.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Typed:
    def __init__(self, expected_type):
        self.expected_type = expected_type
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name
        self.private = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self   # class access returns descriptor
        return obj.__dict__.get(self.private)

    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name} must be {self.expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
        obj.__dict__[self.private] = value

class Person:
    name = Typed(str)
    age  = Typed(int)

    def __init__(self, name, age):
        self.name = name   # calls Typed.__set__
        self.age  = age

p = Person("Alice", 30)
print(p.name)        # Alice

try:
    p.age = "thirty"   # TypeError: age must be int, got str
except TypeError as e:
    print(e)
```

**Why:** The descriptor acts as a "smart attribute" — every assignment goes through `__set__`, which enforces the type constraint. Multiple classes can reuse the same descriptor.
</details>

---

### Q3 🟡 · lookup priority — data vs non-data descriptor

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

**Problem:** Demonstrate the difference between a data descriptor and a non-data descriptor. Show that a data descriptor (with `__set__`) takes priority over instance `__dict__`, while a non-data descriptor (only `__get__`) loses to instance `__dict__`.

<details>
<summary>💡 Hint</summary>
Data descriptor: define `__get__` + `__set__`. Non-data: define only `__get__`. Write directly to `obj.__dict__` to test which wins.
</details>

<details>
<summary>✅ Answer</summary>

```python
class DataDesc:
    """Data descriptor — has __set__, takes priority over instance __dict__."""
    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return obj.__dict__.get('_data_x', 'from descriptor')
    def __set__(self, obj, value):
        obj.__dict__['_data_x'] = value

class NonDataDesc:
    """Non-data descriptor — only __get__, instance __dict__ wins."""
    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return 'from descriptor'

class Demo:
    data    = DataDesc()
    nondata = NonDataDesc()

d = Demo()

# Data descriptor: write to __dict__ directly, but descriptor still wins on read:
d.__dict__['data'] = 'in dict'
print(d.data)      # 'from descriptor'  ← data descriptor has higher priority

# Non-data descriptor: write to __dict__ directly, instance wins:
d.__dict__['nondata'] = 'in dict'
print(d.nondata)   # 'in dict'  ← instance __dict__ beats non-data descriptor
```

**Why:** Attribute lookup order: (1) data descriptor, (2) instance `__dict__`, (3) non-data descriptor. This is why cached lazy properties work — they're non-data descriptors, so once you cache a value in `__dict__`, `__dict__` wins.
</details>

---

### Q4 🟡 · naming — `__set_name__` auto-register descriptor attribute name

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

**Problem:** Create a `LoggedAttribute` descriptor that prints every read and write, including the attribute name. Use `__set_name__` so the descriptor knows its name without you having to pass it manually.

<details>
<summary>💡 Hint</summary>
`__set_name__(self, owner, name)` is called at class-creation time. Store `name` on the descriptor. Use a private key in `obj.__dict__` to store the value per instance.
</details>

<details>
<summary>✅ Answer</summary>

```python
class LoggedAttribute:
    def __set_name__(self, owner, name):
        self.name    = name
        self.private = f"_logged_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        value = obj.__dict__.get(self.private)
        print(f"  READ  {self.name} = {value!r}")
        return value

    def __set__(self, obj, value):
        print(f"  WRITE {self.name} = {value!r}")
        obj.__dict__[self.private] = value

class Config:
    host = LoggedAttribute()
    port = LoggedAttribute()

    def __init__(self, host, port):
        self.host = host   # prints: WRITE host = 'localhost'
        self.port = port   # prints: WRITE port = 8080

cfg = Config("localhost", 8080)
_ = cfg.host   # prints: READ host = 'localhost'
```

**Why:** Before `__set_name__` (Python 3.6+), you had to pass the attribute name manually in `__init__` or use a metaclass. `__set_name__` makes descriptors self-aware.
</details>

---

### Q5 🟡 · caching — write a Cached descriptor that computes once and stores

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

**Problem:** Write a `cached_property` descriptor (non-data, no `__set__`) that computes an expensive value once and caches it in the instance's `__dict__`. Verify the computation only runs once.

<details>
<summary>💡 Hint</summary>
A non-data descriptor has lower priority than instance `__dict__`. So the first call computes and stores the value in `obj.__dict__[name]`. The second access finds it in `__dict__` and never calls `__get__` again.
</details>

<details>
<summary>✅ Answer</summary>

```python
class cached_property:
    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        print(f"  Computing {self.name}...")
        value = self.func(obj)
        obj.__dict__[self.name] = value   # cache in instance __dict__
        return value                       # next access: __dict__ wins (non-data descriptor)

class DataModel:
    def __init__(self, values):
        self.values = values

    @cached_property
    def sorted_values(self):
        return sorted(self.values)

    @cached_property
    def total(self):
        return sum(self.values)

m = DataModel([5, 3, 1, 4, 2])
print(m.sorted_values)   # "Computing sorted_values..." → [1, 2, 3, 4, 5]
print(m.sorted_values)   # No print — served from __dict__
print(m.total)           # "Computing total..." → 15
print(m.total)           # No print — cached
```

**Why:** Non-data descriptors (no `__set__`) lose to instance `__dict__`. So writing to `obj.__dict__[name]` effectively disables the descriptor for that instance on subsequent accesses.
</details>

---

### Q6 🟡 · type enforcement — TypeChecked descriptor using `__set__`

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

**Problem:** Write a `TypeChecked` descriptor that accepts a `type` in its constructor and validates every assignment. Also support type coercion: if `coerce=True`, call `type_(value)` instead of raising.

<details>
<summary>💡 Hint</summary>
Two modes: strict (raise `TypeError` if type doesn't match) and coerce (try to convert with `type_(value)`, raise only if that fails).
</details>

<details>
<summary>✅ Answer</summary>

```python
class TypeChecked:
    def __init__(self, type_, coerce=False):
        self.type_ = type_
        self.coerce = coerce

    def __set_name__(self, owner, name):
        self.name    = name
        self.private = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return obj.__dict__.get(self.private)

    def __set__(self, obj, value):
        if self.coerce:
            try:
                value = self.type_(value)
            except (TypeError, ValueError) as e:
                raise TypeError(f"{self.name}: cannot coerce {value!r} to {self.type_.__name__}: {e}")
        elif not isinstance(value, self.type_):
            raise TypeError(f"{self.name} must be {self.type_.__name__}, got {type(value).__name__}")
        obj.__dict__[self.private] = value

class Record:
    count = TypeChecked(int, coerce=True)
    label = TypeChecked(str)

    def __init__(self, count, label):
        self.count = count
        self.label = label

r = Record("42", "test")   # count coerced from str to int
print(r.count)   # 42 (int)
try:
    r.label = 123   # strict — raises TypeError
except TypeError as e:
    print(e)
```

**Why:** Coercion mode is useful for config parsing where values come in as strings. Strict mode is for enforcing contracts.
</details>

---

### Q7 🟠 · read-only — write a read-only descriptor (only `__get__`, no `__set__`)

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

**Problem:** Write a `ReadOnly` descriptor that stores a value at class definition time and raises `AttributeError` on any attempt to set it. Verify that it cannot be overwritten.

<details>
<summary>💡 Hint</summary>
A non-data descriptor (no `__set__`) can be bypassed via `obj.__dict__`. A true read-only descriptor must have `__set__` that raises — making it a data descriptor that blocks writes.
</details>

<details>
<summary>✅ Answer</summary>

```python
class ReadOnly:
    """Data descriptor — has __set__ that raises, so truly read-only."""

    def __init__(self, value):
        self.value = value

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        return self.value   # same value for class and instance access

    def __set__(self, obj, value):
        raise AttributeError(f"{self.name!r} is read-only")

    def __delete__(self, obj):
        raise AttributeError(f"{self.name!r} is read-only")

class Config:
    VERSION = ReadOnly("1.0.0")
    MAX_CONNECTIONS = ReadOnly(100)

cfg = Config()
print(cfg.VERSION)          # 1.0.0
print(Config.VERSION)       # 1.0.0

try:
    cfg.VERSION = "2.0.0"   # AttributeError
except AttributeError as e:
    print(e)

try:
    cfg.__dict__['VERSION'] = "2.0.0"
    print(cfg.VERSION)   # Still 1.0.0 — data descriptor beats instance __dict__!
except:
    pass
print(cfg.VERSION)  # 1.0.0  — data descriptor wins over __dict__
```

**Why:** A read-only descriptor MUST be a data descriptor (have `__set__`) — otherwise users could bypass it by writing directly to `obj.__dict__`. The data descriptor lookup takes priority over `__dict__`.
</details>

---

### Q8 🟠 · range validation — descriptor for range validation

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

**Problem:** Write a `Bounded` descriptor that accepts `min_val` and `max_val`. On set, clamp the value to `[min_val, max_val]` (no error, just clamp). Use it on a `Slider` class with `value` bounded to 0-100.

<details>
<summary>💡 Hint</summary>
Use `max(min_val, min(max_val, value))` to clamp. Store the clamped value in `obj.__dict__` using the private key.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Bounded:
    def __init__(self, min_val, max_val):
        self.min_val = min_val
        self.max_val = max_val

    def __set_name__(self, owner, name):
        self.name    = name
        self.private = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return obj.__dict__.get(self.private, self.min_val)

    def __set__(self, obj, value):
        clamped = max(self.min_val, min(self.max_val, value))
        obj.__dict__[self.private] = clamped

class Slider:
    value = Bounded(0, 100)

    def __init__(self, value=50):
        self.value = value

s = Slider()
print(s.value)   # 50

s.value = 150
print(s.value)   # 100  (clamped)

s.value = -10
print(s.value)   # 0    (clamped)

s.value = 75
print(s.value)   # 75   (within range)
```

**Why:** Clamping is a gentler approach than raising — useful for UI components (sliders, progress bars) where out-of-range values should silently snap to the boundary.
</details>

---

### Q9 🟠 · build from scratch — rewrite `@property` using a custom descriptor

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

**Problem:** Implement `MyProperty` — a full equivalent of Python's built-in `property`. It should support getter, setter, and deleter via chaining (`.getter()`, `.setter()`, `.deleter()` methods). Use it to wrap `Circle.radius`.

<details>
<summary>💡 Hint</summary>
Store `fget`, `fset`, `fdel` as instance attributes. Each of `.getter()`, `.setter()`, `.deleter()` returns a new `MyProperty` with the updated function. In `__get__`, call `fget(obj)` if `fget` is set.
</details>

<details>
<summary>✅ Answer</summary>

```python
class MyProperty:
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc or (fget.__doc__ if fget else None)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)

class Circle:
    def __init__(self, radius):
        self._radius = radius

    @MyProperty
    def radius(self):
        """The circle's radius."""
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

c = Circle(5)
print(c.radius)     # 5
c.radius = 10
print(c.radius)     # 10
```

**Why:** Building `property` yourself reveals that `@property` is just a descriptor with `fget`, `fset`, `fdel`. The decorator chaining syntax (`@radius.setter`) creates a new descriptor object with the setter added.
</details>

---

### Q10 🟠 · observability — descriptor that logs all access

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

**Problem:** Write an `Audited` descriptor that logs every read and write (with a timestamp and instance id) to an internal log. The log should be accessible via `MyClass.field.get_log()`. Apply it to a `BankAccount.balance` field.

<details>
<summary>💡 Hint</summary>
Store the log on the descriptor object itself (not per-instance). Use `id(obj)` to distinguish instances. Use `time.time()` for timestamps.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time

class Audited:
    def __init__(self):
        self._log = []

    def __set_name__(self, owner, name):
        self.name    = name
        self.private = f"_audited_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        value = obj.__dict__.get(self.private)
        self._log.append({
            "op": "READ", "time": time.time(),
            "instance": id(obj), "attr": self.name, "value": value
        })
        return value

    def __set__(self, obj, value):
        old = obj.__dict__.get(self.private)
        self._log.append({
            "op": "WRITE", "time": time.time(),
            "instance": id(obj), "attr": self.name, "value": value, "was": old
        })
        obj.__dict__[self.private] = value

    def get_log(self):
        return list(self._log)

class BankAccount:
    balance = Audited()

    def __init__(self, initial):
        self.balance = initial

    def deposit(self, amount):
        self.balance += amount

acc = BankAccount(1000.0)
acc.deposit(500.0)

for entry in BankAccount.balance.get_log():
    print(f"  {entry['op']:5} balance = {entry['value']}")
```

**Why:** Descriptors are perfect for cross-cutting concerns (logging, auditing) — they intercept access without modifying the class logic.
</details>

---

## Navigation

| | |
|---|---|
| Root theory | [../theory.md](../theory.md) |
| Subfolder theory | [theory.md](./theory.md) |
| Prev subfolder | [../01_dunder_methods/practice.md](../01_dunder_methods/practice.md) |
| Next subfolder | [../03_metaclasses/practice.md](../03_metaclasses/practice.md) |
| Root practice | [../practice.md](../practice.md) |
