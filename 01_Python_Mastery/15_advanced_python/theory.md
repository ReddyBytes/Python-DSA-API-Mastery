<a id="top"></a>
# 🧙 Advanced Python — Theory

> *"Most developers use Python. Advanced Python engineers understand how it works.*
> *Every operator, every built-in, every for-loop runs through a protocol.*
> *Once you see those protocols, the language becomes transparent."*

## 📖 Table of Contents

- [1. Dunder Methods — Python's Protocol System](#1-dunder-methods--pythons-protocol-system)
- [2. Representation — `__str__`, `__repr__`, `__format__`](#2-representation----__str__-__repr__-__format__)
- [3. Comparison and Hashing](#3-comparison-and-hashing)
  - [The Comparison Protocol](#the-comparison-protocol)
  - [__hash__ and Its Relationship with __eq__](#__hash__-and-its-relationship-with-__eq__)
- [4. Numeric and Operator Overloading](#4-numeric-and-operator-overloading)
- [5. Container Protocol](#5-container-protocol)
  - [__bool__ — Truthiness](#__bool__--truthiness)
- [6. `__slots__` — Memory Optimization](#6-__slots__--memory-optimization)
- [7. Descriptors — The Power Behind Properties](#7-descriptors--the-power-behind-properties)
  - [Data vs Non-Data Descriptors](#data-vs-non-data-descriptors)
  - [How @property Works Internally](#how-property-works-internally)
  - [Custom Validation Descriptor](#custom-validation-descriptor)
  - [How Functions Become Methods](#how-functions-become-methods)
- [8. Metaclasses — Classes of Classes](#8-metaclasses--classes-of-classes)
  - [Custom Metaclass — Registry Pattern](#custom-metaclass--registry-pattern)
  - [Enforcing Interface with Metaclass](#enforcing-interface-with-metaclass)
  - [__init_subclass__ — Modern Alternative](#__init_subclass__--modern-alternative)
- [9. Dataclasses — Generated Boilerplate](#9-dataclasses--generated-boilerplate)
- [10. Abstract Base Classes (ABCs)](#10-abstract-base-classes-abcs)
- [11. Enums — Named Constants](#11-enums--named-constants)
- [12. Introspection — Looking Inside Objects](#12-introspection--looking-inside-objects)
- [13. Typing and Protocols](#13-typing-and-protocols)
  - [🔥 Summary Table](#-summary-table)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
Dunder methods (`__repr__`, `__str__`, `__eq__`, `__hash__`, `__len__`, `__getitem__`) · Descriptor protocol (`__get__`, `__set__`, `__delete__`) · `@property` internals

**Should Learn** — Important for real projects, comes up regularly:
`__getattr__` vs `__getattribute__` · `__init_subclass__` · `__slots__` deep dive · `type()` for dynamic class creation · ABCs and `@abstractmethod`

**Good to Know** — Useful in specific situations:
`__class_getitem__` · `__missing__` · `__reduce__` / pickle protocol · Virtual subclasses (`ABC.register()`) · `__sizeof__`

**Reference** — Know it exists, look up when needed:
`__prepare__` · Metaclass conflicts · Buffer protocol / `memoryview` · `linecache` · Code object introspection

---

<a id="the-story-building-a-framework"></a>
## 🎬 The Story: Building a Framework

Imagine you're building a data analysis library. Users should be able to write:

```python
dataset = Dataset([1, 2, 3, 4, 5])

len(dataset)           # how many items?
dataset[2]             # get item by index
dataset + other        # merge two datasets
for item in dataset:   # iterate
if 3 in dataset:       # membership test
print(dataset)         # human-readable description
repr(dataset)          # developer-readable repr
with dataset:          # resource management
```

Without advanced Python, you'd need 8 separate, arbitrarily-named methods. **With advanced Python, each of these maps to a protocol** — a set of dunder methods that Python calls automatically. Your class plugs into the language itself.

This is what advanced Python is: **understanding and using the protocols that power Python's syntax**.

---

<a id="1-dunder-methods--pythons-protocol-system"></a>
# 1. Dunder Methods — Python's Protocol System

Think of dunder methods like electrical sockets on a wall. The socket shape is fixed (`__add__`, `__len__`, `__str__`) — Python defines the shape. You decide what your class plugs in. Write `__add__` and suddenly your object can use the `+` operator, just like built-in numbers do. You're not overriding Python — you're extending it by honoring its contracts.

**Dunder** = **D**ouble **under**score. Python's way of defining object behaviour through well-known method names that the interpreter calls automatically. When you write `a + b`, Python doesn't call a method named `add(a, b)`. Instead it calls `a.__add__(b)`. This means **any class can define what `+` means for its objects**.

```
┌──────────────────── Python Syntax → Dunder Call ─────────────────────┐
│                                                                       │
│  PYTHON SYNTAX       →    DUNDER CALL                                │
│  ──────────────────────────────────────────────────────              │
│  len(obj)            →    obj.__len__()                              │
│  obj[key]            →    obj.__getitem__(key)                       │
│  obj[key] = val      →    obj.__setitem__(key, val)                  │
│  del obj[key]        →    obj.__delitem__(key)                       │
│  x in obj            →    obj.__contains__(x)                        │
│  for x in obj        →    iter(obj).__next__() via obj.__iter__()    │
│  obj + other         →    obj.__add__(other)                         │
│  obj == other        →    obj.__eq__(other)                          │
│  str(obj)            →    obj.__str__()                              │
│  repr(obj)           →    obj.__repr__()                             │
│  bool(obj)           →    obj.__bool__()                             │
│  obj()               →    obj.__call__()                             │
│  with obj            →    obj.__enter__(), obj.__exit__()            │
│  abs(obj)            →    obj.__abs__()                              │
│  hash(obj)           →    obj.__hash__()                             │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

This table IS Python's object model. Learn it and Python becomes predictable.

⚠️ **Common Mistake:** Naming a method `add()` instead of `__add__()`. Python never calls `add()` automatically — it only honors the exact dunder names.

💡 **Hint:** When you're not sure which dunder Python calls for an operation, check `help(operator)` or the Python data model docs. Every operator has a documented dunder.

🔍 [Visual: Python data model dunder methods map](https://www.google.com/search?q=python+data+model+dunder+methods+protocol+diagram)

📝 **Practice:** [Q1–Q10 · dunder methods](./practice.md#q1--repr-and-str) | **Deep dive:** [01_dunder_methods/theory.md](./01_dunder_methods/theory.md)

> [↑ Back to Top](#top)

---

<a id="2-representation----__str__-__repr__-__format__"></a>
# 2. Representation — `__str__`, `__repr__`, `__format__`

Imagine you have a box and you need to describe it to two different people. To a customer, you say "a red shoebox, size 10." To a warehouse technician, you say "SKU-4421, 30cm × 15cm × 12cm, color=red." Same box, two different descriptions for two different audiences. That's exactly the difference between `__str__` and `__repr__` — same object, different descriptions for users vs developers.

```
__repr__  → developer-facing, unambiguous, ideally copy-paste runnable
__str__   → user-facing, human-readable, doesn't need to be precise
__format__ → how the object renders inside f-strings with format specs
```

The **fallback chain:**
```
┌────────────────────── Representation Fallback Chain ──────────────────┐
│                                                                        │
│  str(obj)   → obj.__str__()                                           │
│               → if not defined: falls back to obj.__repr__()          │
│               → if not defined: <ClassName at 0x...>                  │
│                                                                        │
│  repr(obj)  → obj.__repr__()                                          │
│               → if not defined: <ClassName at 0x...>                  │
│                                                                        │
│  f"{obj}"   → obj.__format__("")                                      │
│               → if not defined: falls back to str(obj)               │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

```python
from datetime import datetime

dt = datetime(2025, 3, 8, 14, 30)

repr(dt)    # datetime.datetime(2025, 3, 8, 14, 30)   ← copy-pasteable
str(dt)     # 2025-03-08 14:30:00                      ← readable

f"{dt:%Y/%m/%d}"   # 2025/03/08  ← custom format spec via __format__
```

**Implementing all three:**

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        # Must be unambiguous — eval(repr(v)) should recreate the object:
        return f"Vector({self.x!r}, {self.y!r})"

    def __str__(self):
        # Human-readable:
        return f"({self.x}, {self.y})"

    def __format__(self, spec):
        # Support format specs:
        if spec == "polar":
            import math
            r     = math.hypot(self.x, self.y)
            theta = math.atan2(self.y, self.x)
            return f"|{r:.2f}|∠{math.degrees(theta):.1f}°"
        return str(self)

v = Vector(3, 4)
repr(v)           # "Vector(3, 4)"
str(v)            # "(3, 4)"
f"{v}"            # "(3, 4)"
f"{v:polar}"      # "|5.00|∠53.1°"
```

**Rule:** Always implement `__repr__`. Implement `__str__` only when a different user-facing format makes sense.

⚠️ **Common Mistake:** Making `__repr__` the same as `__str__`. They serve different audiences. `repr` must be unambiguous and ideally eval-able; `str` should be readable.

💡 **Hint:** In the REPL and `print()` on a list of objects, Python calls `__repr__` on the items inside — not `__str__`. So `repr` is what you see in `[v1, v2, v3]`.

📝 **Practice:** [Q1 · repr and str](./practice.md#q1--repr-and-str)

> [↑ Back to Top](#top)

---

<a id="3-comparison-and-hashing"></a>
# 3. Comparison and Hashing

Think of comparing two employees at a company. HR says two employees are "the same" if they share the same employee ID — not the same name, same email, or same salary. How you define "same" is entirely up to you. Python lets you define exactly this: what makes two objects of your class equal, and how to generate a consistent fingerprint (hash) from that equality.

<a id="the-comparison-protocol"></a>
## The Comparison Protocol

```python
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    # Python calls __eq__ for ==:
    def __eq__(self, other):
        if not isinstance(other, Temperature):
            return NotImplemented   # ← not False! tells Python to try other.__eq__
        return self.celsius == other.celsius

    # Define ordering — Python can derive the rest with @functools.total_ordering:
    def __lt__(self, other):
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.celsius < other.celsius
```

**`functools.total_ordering` — define two, get all six:**

```python
import functools

@functools.total_ordering
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def __eq__(self, other):
        return isinstance(other, Temperature) and self.celsius == other.celsius

    def __lt__(self, other):
        return isinstance(other, Temperature) and self.celsius < other.celsius

    # __le__, __gt__, __ge__ are automatically derived!

t1 = Temperature(20)
t2 = Temperature(30)
t1 < t2    # True
t1 > t2    # False
t1 <= t2   # True
sorted([t2, t1])   # [Temperature(20), Temperature(30)]
```

⚠️ **Common Mistake:** Returning `False` instead of `NotImplemented` when the other operand is an unknown type. `NotImplemented` tells Python "try the other object's method." `False` silently says "they're not equal" — which can mask bugs.

<a id="__hash__-and-its-relationship-with-__eq__"></a>
## `__hash__` and Its Relationship with `__eq__`

The **critical rule:** objects that compare equal must have the same hash.

```python
# Python enforces this:
# If you define __eq__ without __hash__:
#   → __hash__ is set to None → object is NOT hashable → can't use in set/dict

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))   # hash from same fields used in __eq__

p = Point(1, 2)
{p}           # ✅ hashable
{p: "val"}    # ✅ usable as dict key
```

```
┌────────────────── __eq__ / __hash__ Compatibility Rules ──────────────┐
│                                                                        │
│  Define __eq__                    → __hash__ set to None (unhashable) │
│  Define __eq__ + __hash__         → fully hashable, usable in set/dict│
│  Define neither                   → uses default identity comparison  │
│  @dataclass(frozen=True)          → auto-generates both               │
│                                                                        │
│  Rule: if a == b then hash(a) == hash(b)  MUST hold always           │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

💡 **Hint:** Hash from immutable fields only. If a field can change after construction, don't include it in `__hash__` — the object would disappear from a set after mutation.

📝 **Practice:** [Q3 · eq and hash](./practice.md#q3--eq-and-hash) · [Q4 · ordering](./practice.md#q4--total-ordering)

> [↑ Back to Top](#top)

---

<a id="4-numeric-and-operator-overloading"></a>
# 4. Numeric and Operator Overloading

Imagine a currency class. You want to write `$10 + $5` and get `$15`. But what about `10 + $5` — where the left side is a plain number? Python has a fallback system: if the left operand doesn't know how to handle the right one, Python flips the operation and tries the right operand's "reflected" method. This is why Python has `__add__` AND `__radd__` — the reflected version catches the cases where your object is on the right side.

**Three versions of each arithmetic operator:**

```
__add__(self, other)    → self + other  (left operand)
__radd__(self, other)   → other + self  (right operand — called when left fails)
__iadd__(self, other)   → self += other (in-place)
```

**Why `__radd__` exists:**
```python
v = Vector(1, 2)
3 + v   # → 3.__add__(v) → int doesn't know Vector → returns NotImplemented
        # → Python tries v.__radd__(3) → calls your method!
```

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        return NotImplemented   # let Python try other.__radd__

    def __radd__(self, other):
        return self.__add__(other)   # addition is commutative

    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector(self.x * scalar, self.y * scalar)
        return NotImplemented

    def __rmul__(self, scalar):
        return self.__mul__(scalar)   # 3 * v == v * 3

    def __neg__(self):              # unary -v
        return Vector(-self.x, -self.y)

    def __abs__(self):              # abs(v)
        import math
        return math.hypot(self.x, self.y)

v1 = Vector(1, 2)
v2 = Vector(3, 4)
v1 + v2    # Vector(4, 6)
3 * v1     # Vector(3, 6)
v1 * 2     # Vector(2, 4)
-v1        # Vector(-1, -2)
abs(v1)    # 2.236...
```

⚠️ **Common Mistake:** Forgetting `__radd__` / `__rmul__`. If you only define `__add__`, then `3 + v` fails with `TypeError` even though `v + 3` works fine.

💡 **Hint:** For commutative operations (addition, multiplication), `__radd__` just delegates to `__add__`. For non-commutative ones (subtraction, division), implement separate logic.

📝 **Practice:** [Q6 · add/radd](./practice.md#q6--add-and-radd) · [Q7 · mul/rmul](./practice.md#q7--mul-and-rmul)

> [↑ Back to Top](#top)

---

<a id="5-container-protocol"></a>
# 5. Container Protocol

Think of a custom bookshelf class. You want users to ask "how many books?" with `len(shelf)`, find a book with `shelf[3]`, check membership with `"Python" in shelf`, and loop with `for book in shelf`. None of this requires inheriting from `list`. You just implement the right dunder methods and Python's built-in functions and syntax start working with your class automatically.

```python
class Dataset:
    def __init__(self, data):
        self._data = list(data)

    # Length:
    def __len__(self):
        return len(self._data)

    # Index access: ds[i], ds[a:b]:
    def __getitem__(self, key):
        return self._data[key]   # slicing works because list handles slice objects

    # Assignment: ds[i] = val:
    def __setitem__(self, key, value):
        self._data[key] = value

    # Deletion: del ds[i]:
    def __delitem__(self, key):
        del self._data[key]

    # Membership: x in ds:
    def __contains__(self, item):
        return item in self._data

    # Iteration: for x in ds:
    def __iter__(self):
        return iter(self._data)

    # Reversed: reversed(ds):
    def __reversed__(self):
        return reversed(self._data)

ds = Dataset([10, 20, 30, 40])
len(ds)         # 4
ds[1]           # 20
ds[1:3]         # [20, 30]
20 in ds        # True
list(ds)        # [10, 20, 30, 40]
for x in ds: print(x)
```

**What Python infers automatically from `__len__` + `__getitem__` alone:**
```
__iter__      → sequential integer indexing (0, 1, 2, ...)
__contains__  → linear search via iteration
__reversed__  → reverse indexing
```

⚠️ **Common Mistake:** Defining `__iter__` that returns `self` without a `__next__` method. The object returned by `__iter__` must have `__next__`. Either return `iter(self._data)` (delegate to list's iterator) or implement `__next__` and return `self`.

<a id="__bool__--truthiness"></a>
## `__bool__` — Truthiness

Python checks `__bool__` first. If not defined, it falls back to `__len__`. Only if neither exists does it default to `True`.

```python
class Container:
    def __len__(self):
        return self._count

    # __bool__ is optional — Python falls back to __len__:
    # if __len__() == 0 → False, else → True

    # Define __bool__ when truthiness ≠ emptiness:
    def __bool__(self):
        return self._active and len(self) > 0
```

```
┌─────────── Truthiness Resolution Order ────────────┐
│                                                     │
│  bool(obj)                                          │
│    1. obj.__bool__()    ← check first               │
│    2. obj.__len__()     ← fallback: 0=False         │
│    3. True              ← final fallback            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

💡 **Hint:** Empty containers should be falsy (`[]`, `{}`, `""` are all `False`). Your custom container should follow the same convention — implement `__len__` and Python handles the rest.

📝 **Practice:** [Q2 · len/bool](./practice.md#q2--len-and-bool) · [Q5 · contains/iter](./practice.md#q5--contains-and-iter) · [Q10 · getitem/setitem](./practice.md#q10--getitem-and-setitem)

> [↑ Back to Top](#top)

---

<a id="6-__slots__--memory-optimization"></a>
# 6. `__slots__` — Memory Optimization

By default, every Python object is like a person carrying a big expandable suitcase (`__dict__`) that can hold any number of belongings added at any time. That's flexible, but the suitcase itself weighs 200+ bytes even when empty. `__slots__` replaces the suitcase with a fixed-size backpack — you declare upfront exactly what you'll carry, and Python packs it more efficiently. When you have a million of these objects, the difference is enormous.

By default, every Python object stores its attributes in a `__dict__` (a hash table). This is flexible but uses ~200-300 bytes per instance. `__slots__` replaces `__dict__` with a fixed-size array of descriptors:

```python
# Without __slots__:
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

import sys
p = Point(1, 2)
sys.getsizeof(p)             # ~56 bytes (object overhead)
sys.getsizeof(p.__dict__)    # ~232 bytes (the dict itself)
# Total: ~288 bytes per instance


# With __slots__:
class PointSlotted:
    __slots__ = ('x', 'y')   # declare allowed attributes

    def __init__(self, x, y):
        self.x = x
        self.y = y

ps = PointSlotted(1, 2)
sys.getsizeof(ps)            # ~64 bytes — NO __dict__!
# hasattr(ps, '__dict__')    # False

# Impact at scale:
# 1,000,000 Point instances:
#   without __slots__: ~288 MB
#   with    __slots__: ~64 MB   ← 4.5x smaller
```

```
┌─────────────────── __slots__ Trade-offs ────────────────────────────┐
│                                                                      │
│  __slots__ GIVES you:        __slots__ TAKES AWAY:                  │
│  ─────────────────────       ────────────────────────               │
│  ✅ Memory savings            ❌ Dynamic attribute assignment        │
│  ✅ Faster attribute access   ❌ __dict__ (unless added to __slots__)│
│  ✅ Prevents typos            ❌ __weakref__ (unless added)          │
│                               ❌ Multiple inheritance with other     │
│                                  __slots__ classes                   │
└──────────────────────────────────────────────────────────────────────┘
```

⚠️ **Common Mistake:** Using `__slots__` in a subclass when the parent doesn't use it. If the parent has `__dict__`, the child inherits it — and you lose all the memory savings.

💡 **Hint:** Use `__slots__` when you'll create thousands (or millions) of instances of the same class. Good candidates: coordinate pairs, events, log entries, any small data-holder class.

🔍 **Good to Know:** Adding `'__dict__'` to `__slots__` gives you both the fixed slots AND dynamic attribute assignment — a compromise when you need flexibility in a few instances but want to save memory in most.

📝 **Practice:** [Q25 · slots memory](./practice.md#q25--slots-memory) · [Q26 · restriction](./practice.md#q26--slots-restriction) · [Q27 · inheritance](./practice.md#q27--slots-inheritance) | **Deep dive:** [05_advanced_patterns/theory.md](./05_advanced_patterns/theory.md)

> [↑ Back to Top](#top)

---

<a id="7-descriptors--the-power-behind-properties"></a>
# 7. Descriptors — The Power Behind Properties

Think of a descriptor like a smart lock on a door. When you turn the handle (read an attribute), the lock can run any code — check who you are, log the access, return a different key each time. When you set a new combination (write an attribute), the lock validates it before accepting. You program the lock once, attach it to any door (class attribute), and it watches over every access automatically.

A **descriptor** is any object that implements `__get__`, `__set__`, or `__delete__`. This protocol powers `@property`, `@classmethod`, `@staticmethod` — they're not special syntax. They're just descriptors.

**The descriptor protocol:**

```python
class MyDescriptor:
    def __get__(self, obj, objtype=None):
        """Called when attribute is READ.
        obj:     the instance (None if accessed on class)
        objtype: the class
        """

    def __set__(self, obj, value):
        """Called when attribute is WRITTEN."""

    def __delete__(self, obj):
        """Called when attribute is DELeted."""
```

**When Python accesses `obj.attr`:**
```
┌────────────── Python Attribute Lookup Order ─────────────────────┐
│                                                                   │
│  obj.attr                                                         │
│    │                                                              │
│    ▼                                                              │
│  1. Look in type(obj).__mro__ for 'attr'                         │
│    │                                                              │
│    ├─► Found + data descriptor (__set__ or __delete__)           │
│    │   → call descriptor.__get__(obj, type(obj))  ← wins always  │
│    │                                                              │
│    ├─► Not a data descriptor → check obj.__dict__['attr']        │
│    │   → found in instance dict → return it                      │
│    │                                                              │
│    ├─► Not in instance dict + non-data descriptor (__get__ only) │
│    │   → call descriptor.__get__(obj, type(obj))                 │
│    │                                                              │
│    └─► Nothing → raise AttributeError                            │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

<a id="data-vs-non-data-descriptors"></a>
## Data vs Non-Data Descriptors

```
Non-data descriptor: implements __get__ only
  → Instance __dict__ takes priority over it
  → Examples: functions (methods are non-data descriptors)

Data descriptor: implements __get__ AND __set__ (or __delete__)
  → Takes priority OVER instance __dict__
  → Examples: property, classmethod, staticmethod
```

**Why this matters:**

```python
class MyClass:
    x = NonDataDescriptor()   # only __get__

obj = MyClass()
obj.__dict__['x'] = 42        # instance __dict__ wins
print(obj.x)                  # 42 — instance dict, not descriptor

class MyClass2:
    x = DataDescriptor()      # __get__ + __set__

obj2 = MyClass2()
obj2.__dict__['x'] = 42       # this never gets stored in __dict__
print(obj2.x)                 # descriptor's __get__ is called, not dict
```

<a id="how-property-works-internally"></a>
## How @property Works Internally

`property` is a built-in class that implements `__get__`, `__set__`, `__delete__`. When you write `@property`, Python creates a descriptor object and assigns it as a class attribute:

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def area(self):
        return 3.14159 * self._radius ** 2

# Python translates the above to:
class Circle:
    def __init__(self, radius):
        self._radius = radius

    def _area_getter(self):
        return 3.14159 * self._radius ** 2

    area = property(_area_getter)   # ← property() creates a descriptor object
```

When you access `circle.area`, Python calls `area.__get__(circle, Circle)`.

**The full `property` implementation (simplified):**

```python
class property:
    """Simplified implementation showing how @property works."""

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc or (fget.__doc__ if fget else None)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self        # accessed on class → return descriptor itself
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)  # accessed on instance → call getter

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def setter(self, fset):
        return property(self.fget, fset, self.fdel)

    def deleter(self, fdel):
        return property(self.fget, self.fset, fdel)
```

<a id="custom-validation-descriptor"></a>
## Custom Validation Descriptor

```python
class ValidatedAttribute:
    """Descriptor that validates type and range."""

    def __init__(self, name, type_, min_val=None, max_val=None):
        self.name    = name
        self.type_   = type_
        self.min_val = min_val
        self.max_val = max_val

    def __set_name__(self, owner, name):
        """Called when descriptor is assigned to class attribute.
        Lets descriptor know its own name without being told explicitly."""
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        if not isinstance(value, self.type_):
            raise TypeError(f"{self.name}: expected {self.type_.__name__}, got {type(value).__name__}")
        if self.min_val is not None and value < self.min_val:
            raise ValueError(f"{self.name}: {value} < minimum {self.min_val}")
        if self.max_val is not None and value > self.max_val:
            raise ValueError(f"{self.name}: {value} > maximum {self.max_val}")
        obj.__dict__[self.name] = value

class Product:
    price    = ValidatedAttribute("price",    float, min_val=0.0)
    quantity = ValidatedAttribute("quantity", int,   min_val=0, max_val=10000)
    name     = ValidatedAttribute("name",     str)

    def __init__(self, name, price, quantity):
        self.name     = name      # triggers __set__ on descriptor
        self.price    = price
        self.quantity = quantity

p = Product("Widget", 9.99, 100)
p.price = -1.0     # ValueError: price: -1.0 < minimum 0.0
p.price = "free"   # TypeError: price: expected float, got str
```

💡 **Hint:** `__set_name__` was added in Python 3.6. It's called automatically when the descriptor is assigned as a class attribute. Before it existed, you had to pass the attribute name explicitly in `__init__`.

<a id="how-functions-become-methods"></a>
## How Functions Become Methods

Functions are **non-data descriptors**. When you access `obj.method`, Python calls `method.__get__(obj, type(obj))`. This returns a **bound method** — the function with `obj` pre-filled as `self`. This is the mechanism behind every method call.

```python
class Foo:
    def bar(self):
        return self

foo = Foo()
print(foo.bar)          # <bound method Foo.bar of <Foo object>>
print(Foo.bar)          # <function Foo.bar at 0x...>
print(foo.bar())        # <Foo object>    ← self = foo, auto-filled
```

The descriptor protocol is exactly why `foo.bar()` automatically passes `foo` as `self`. Without descriptors, Python would need special-case logic for methods — instead, it's just a `__get__` call.

⚠️ **Common Mistake:** Storing a descriptor as an instance attribute instead of a class attribute. Descriptors only work as class attributes. If you do `self.my_desc = ValidatedAttribute(...)` inside `__init__`, it's just a regular object stored in `__dict__` — the protocol never fires.

🔍 [Visual: Python descriptor protocol __get__ __set__ flow](https://www.google.com/search?q=python+descriptor+protocol+get+set+flow+diagram)

📝 **Practice:** [Q11–Q14 · descriptors](./practice.md#q11--descriptor-basics) | **Deep dive:** [02_descriptors/theory.md](./02_descriptors/theory.md)

> [↑ Back to Top](#top)

---

<a id="8-metaclasses--classes-of-classes"></a>
# 8. Metaclasses — Classes of Classes

In everyday life, a cookie cutter makes cookies. But what makes the cookie cutter? A machine at the factory. In Python, a class makes instances. But what makes the class? A metaclass. Most Python code never needs to worry about cookie-cutter factories — but if you're building a framework (like Django's ORM, or a plugin system), understanding the factory of factories gives you extraordinary power.

**Everything in Python is an object. Functions are objects. Modules are objects. And classes are objects too.** The "class" that creates class objects is called a **metaclass**.

```
┌─────────────── Python's Class Hierarchy ──────────────────┐
│                                                            │
│  NORMAL CREATION:                                          │
│  int        creates    42                                  │
│  str        creates    "hello"                             │
│  MyClass    creates    my_instance                         │
│                                                            │
│  METACLASS CREATION:                                       │
│  type       creates    MyClass                             │
│  type       creates    int, str, list, dict...             │
│  MyMeta     creates    any class with metaclass=MyMeta     │
│                                                            │
│  type(42)         → <class 'int'>                          │
│  type(int)        → <class 'type'>   (int made by type)   │
│  type(type)       → <class 'type'>   (type made itself!)  │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**How the `class` statement works internally:**

```python
class MyClass(Base):
    x = 10
    def method(self): ...

# Python executes this as:
namespace = {}
namespace['x'] = 10
namespace['method'] = lambda self: ...
MyClass = type('MyClass', (Base,), namespace)

# If metaclass is specified:
MyClass = MyMeta('MyClass', (Base,), namespace)
```

<a id="custom-metaclass--registry-pattern"></a>
## Custom Metaclass — Registry Pattern

```python
class PluginMeta(type):
    """Metaclass that automatically registers all subclasses."""

    registry = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        # Don't register the base class itself:
        if bases:
            mcs.registry[name] = cls
            print(f"Registered plugin: {name}")
        return cls

class Plugin(metaclass=PluginMeta):
    """Base class — all subclasses are auto-registered."""
    def run(self): ...

class CSVPlugin(Plugin):    # → registered automatically
    def run(self): return "csv"

class JSONPlugin(Plugin):   # → registered automatically
    def run(self): return "json"

PluginMeta.registry   # {'CSVPlugin': <class CSVPlugin>, 'JSONPlugin': <class JSONPlugin>}

# Instantiate any plugin by name:
plugin = PluginMeta.registry["CSVPlugin"]()
plugin.run()   # "csv"
```

<a id="enforcing-interface-with-metaclass"></a>
## Enforcing Interface with Metaclass

```python
class InterfaceMeta(type):
    """Metaclass that enforces required methods are implemented."""

    REQUIRED = set()

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases:  # skip the base class
            missing = mcs.REQUIRED - set(namespace)
            if missing:
                raise TypeError(
                    f"{name} must implement: {', '.join(missing)}"
                )
        return cls
```

<a id="__init_subclass__--modern-alternative"></a>
## `__init_subclass__` — Modern Alternative

Python 3.6+ introduced `__init_subclass__`, which handles the most common metaclass use case (subclass registration) with far less complexity:

```python
class Plugin:
    """Simpler registry using __init_subclass__ instead of metaclass."""
    _registry = {}

    def __init_subclass__(cls, plugin_type=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if plugin_type:
            Plugin._registry[plugin_type] = cls

class CSVPlugin(Plugin, plugin_type="csv"):
    def run(self): return "csv"

class JSONPlugin(Plugin, plugin_type="json"):
    def run(self): return "json"

Plugin._registry   # {'csv': CSVPlugin, 'json': JSONPlugin}
```

```
┌──────────────── When to Use Metaclasses ──────────────────────────┐
│                                                                    │
│  USE metaclasses for:                                              │
│  - Framework/library internals (Django ORM uses them heavily)     │
│  - Class registration + auto-discovery (plugin systems)           │
│  - Enforcing interface contracts at class-definition time         │
│  - Auto-generating class attributes at definition time            │
│                                                                    │
│  DON'T use metaclasses when:                                       │
│  - A class decorator would work (simpler, more readable)          │
│  - __init_subclass__ would work (Python 3.6+, much simpler)       │
│  - ABCs cover the interface-enforcement need                       │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

⚠️ **Common Mistake:** Using a metaclass when `__init_subclass__` would do the job. Metaclass conflicts (when two bases have different metaclasses) are notoriously painful. Prefer `__init_subclass__` for registration patterns.

💡 **Hint:** Django's `Model` class uses a metaclass to scan your model class definition and build SQL table schemas automatically. SQLAlchemy's `DeclarativeBase` does the same. Understanding metaclasses helps you understand these frameworks.

🔍 [Visual: Python metaclass type hierarchy diagram](https://www.google.com/search?q=python+metaclass+type+hierarchy+diagram)

📝 **Practice:** [Q15–Q18 · metaclasses](./practice.md#q15--dynamic-class-creation) | **Deep dive:** [03_metaclasses/theory.md](./03_metaclasses/theory.md)

> [↑ Back to Top](#top)

---

<a id="9-dataclasses--generated-boilerplate"></a>
# 9. Dataclasses — Generated Boilerplate

Think of dataclasses like a house blueprint service. Instead of manually drawing out every detail of each room (writing `__init__`, `__repr__`, `__eq__` by hand for every class), you hand the service your list of rooms and materials (type annotations), and it generates a complete blueprint automatically. You focus on what the data is; Python handles the boilerplate of how to create, display, and compare it.

`@dataclass` is a class decorator that inspects type annotations and auto-generates `__init__`, `__repr__`, `__eq__`, and optionally `__lt__`, `__hash__`, `__slots__`:

```python
from dataclasses import dataclass, field
from typing import ClassVar

@dataclass(order=True, frozen=True)
class Point:
    x: float
    y: float

    # Class variable — NOT included in __init__:
    DIMENSIONS: ClassVar[int] = 2

@dataclass
class Order:
    order_id:  int
    user_id:   int
    items:     list = field(default_factory=list)  # mutable default!
    discount:  float = 0.0
    _internal: str = field(default="", repr=False, compare=False, init=False)

    def __post_init__(self):
        """Called after __init__ — use for validation or derived fields."""
        if self.discount < 0 or self.discount > 1:
            raise ValueError(f"discount must be 0.0–1.0, got {self.discount}")

# Generated methods:
o = Order(1, 42, ["widget", "gadget"], discount=0.1)
repr(o)    # Order(order_id=1, user_id=42, items=['widget', 'gadget'], discount=0.1)
o == Order(1, 42, ["widget", "gadget"], 0.1)   # True (compares all fields)
```

**`field()` options:**
```python
field(default=None)          # default value
field(default_factory=list)  # factory for mutable defaults
field(repr=False)            # exclude from __repr__
field(compare=False)         # exclude from __eq__ and ordering
field(hash=False)            # exclude from __hash__
field(init=False)            # exclude from __init__
field(kw_only=True)          # keyword-only argument
```

```
┌──────────── @dataclass Parameters ──────────────────────┐
│                                                          │
│  @dataclass(                                             │
│      init=True,         ← generate __init__             │
│      repr=True,         ← generate __repr__             │
│      eq=True,           ← generate __eq__               │
│      order=False,       ← generate __lt__, __le__, etc  │
│      frozen=False,      ← make immutable (+ hashable)   │
│      slots=False,       ← generate __slots__ (3.10+)    │
│  )                                                       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

⚠️ **Common Mistake:** Using a mutable default (e.g., `items: list = []`) without `field(default_factory=list)`. Python will raise `ValueError: mutable default is not allowed`. Always use `field(default_factory=...)` for lists, dicts, and sets.

💡 **Hint:** `frozen=True` makes the dataclass immutable AND hashable (it generates `__hash__`). Use this for value objects that should be safe to use as dict keys or set members.

📝 **Practice:** [Q20–Q24 · dataclasses](./practice.md#q20--basic-dataclass) | **Deep dive:** [04_dataclasses/theory.md](./04_dataclasses/theory.md)

> [↑ Back to Top](#top)

---

<a id="10-abstract-base-classes-abcs"></a>
# 10. Abstract Base Classes (ABCs)

Think of ABCs like a job contract. The contract says "to work here, you must be able to do X, Y, and Z." It doesn't tell you HOW to do them — that's up to you. But if you sign the contract (inherit from the ABC) without implementing all the required methods, you get an error the moment someone tries to hire you (instantiate your class). ABCs enforce the contract at the right moment: when someone tries to use an incomplete implementation.

ABCs define interfaces — they declare what methods a class MUST implement:

```python
from abc import ABC, abstractmethod

class Storage(ABC):
    """Abstract base class — cannot be instantiated directly."""

    @abstractmethod
    def save(self, key: str, data: bytes) -> None:
        """Subclasses MUST implement this."""

    @abstractmethod
    def load(self, key: str) -> bytes:
        """Subclasses MUST implement this."""

    def exists(self, key: str) -> bool:
        """Optional method with default implementation."""
        try:
            self.load(key)
            return True
        except KeyError:
            return False

# Can't instantiate abstract class:
Storage()   # TypeError: Can't instantiate abstract class Storage

class S3Storage(Storage):
    def save(self, key, data):
        s3.put_object(Key=key, Body=data)

    def load(self, key):
        return s3.get_object(Key=key)["Body"].read()

# Works because all abstract methods are implemented:
storage = S3Storage()
```

**Virtual subclasses — register without modifying:**

```python
from collections.abc import Mapping

# Register an existing class as implementing an interface:
Mapping.register(MyLegacyDict)   # without modifying MyLegacyDict

isinstance(MyLegacyDict(), Mapping)   # True
```

```
┌──────────────────── ABC vs Protocol ──────────────────────────────┐
│                                                                    │
│  ABC (Abstract Base Class)           Protocol (typing.Protocol)  │
│  ──────────────────────────          ────────────────────────────│
│  Requires explicit inheritance       No inheritance needed        │
│  Checks at class-creation time       Structural (duck typing)     │
│  Can provide default implementations No default implementations   │
│  Part of collections.abc             Part of typing module        │
│  Use for: framework contracts        Use for: type-checker hints  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

⚠️ **Common Mistake:** Forgetting that a subclass with all abstract methods implemented can still be abstract if it introduces new `@abstractmethod` methods. A class is concrete only when ALL inherited + new abstract methods are implemented.

💡 **Hint:** `collections.abc` has ready-made ABCs for containers: `Sequence`, `Mapping`, `MutableMapping`, `Iterable`, `Iterator`, `Callable`. Inheriting from these gets you default method implementations for free.

📝 **Practice:** [Q19 · ABCMeta](./practice.md#q19--abcmeta) · [Q33 · ABC interface](./practice.md#q33--abc-interface)

> [↑ Back to Top](#top)

---

<a id="11-enums--named-constants"></a>
# 11. Enums — Named Constants

Imagine a traffic light system where the light state is stored as `0`, `1`, or `2`. Is `0` red or green? Is `2` yellow? Nobody remembers, and every bug looks like a mysterious number comparison. Enums replace magic numbers with named constants that read like plain English. Instead of `if state == 2`, you write `if state == TrafficLight.YELLOW` — and your code becomes self-documenting.

```python
from enum import Enum, IntEnum, Flag, auto

class OrderStatus(Enum):
    PENDING    = "pending"
    PROCESSING = "processing"
    SHIPPED    = "shipped"
    DELIVERED  = "delivered"
    CANCELLED  = "cancelled"

# Usage:
status = OrderStatus.PENDING
status.name      # "PENDING"
status.value     # "pending"
OrderStatus("pending")         # OrderStatus.PENDING  (lookup by value)
OrderStatus["PENDING"]         # OrderStatus.PENDING  (lookup by name)
list(OrderStatus)              # all members

# IntEnum — behaves as int (comparison with ints works):
class Priority(IntEnum):
    LOW    = 1
    MEDIUM = 2
    HIGH   = 3

Priority.HIGH > Priority.LOW   # True
Priority.HIGH > 2              # True  (IntEnum compares with int)

# auto() — auto-assign values:
class Color(Enum):
    RED   = auto()   # 1
    GREEN = auto()   # 2
    BLUE  = auto()   # 3

# Flag — for bitmask/combination enums:
class Permission(Flag):
    READ    = auto()   # 1
    WRITE   = auto()   # 2
    EXECUTE = auto()   # 4

user_perm = Permission.READ | Permission.WRITE
Permission.READ in user_perm     # True
Permission.EXECUTE in user_perm  # False
```

⚠️ **Common Mistake:** Comparing an `Enum` member with a raw string or int using `==`. `OrderStatus.PENDING == "pending"` is `False` (different types). Use `.value` if you need the raw value: `OrderStatus.PENDING.value == "pending"` is `True`. Exception: `IntEnum` members DO compare equal to plain ints.

💡 **Hint:** Use `Enum` for status codes and categories. Use `IntEnum` when you need integer comparison (like priority levels). Use `Flag` for permission bits that can be combined.

📝 **Practice:** [Q31 · Enum](./practice.md#q31--enum-basics) · [Q32 · IntEnum and Flag](./practice.md#q32--intenum)

> [↑ Back to Top](#top)

---

<a id="12-introspection--looking-inside-objects"></a>
# 12. Introspection — Looking Inside Objects

Imagine you could X-ray any package delivered to you — see exactly what's inside, how it's structured, and where it came from — without opening it. Python's introspection tools are that X-ray machine. You can look at any object at runtime and find out its type, its attributes, its methods, its source code, and its call signature. This is how frameworks like pytest, Django, and FastAPI work their magic: they inspect your code at runtime to understand its structure.

```python
import inspect

class MyClass:
    """A sample class."""
    class_var = 42

    def method(self, x: int) -> str:
        """A method."""
        return str(x)

obj = MyClass()

# Type inspection:
type(obj)             # <class '__main__.MyClass'>
isinstance(obj, MyClass)   # True
issubclass(MyClass, object)  # True

# Attribute inspection:
dir(obj)              # all attributes and methods (including inherited)
vars(obj)             # obj.__dict__ — instance attributes only
vars(MyClass)         # class namespace

hasattr(obj, "method")    # True
getattr(obj, "method")    # <bound method>
setattr(obj, "x", 10)     # obj.x = 10
delattr(obj, "x")          # del obj.x

# inspect module — deep inspection:
inspect.getmembers(MyClass)                  # all name/value pairs
inspect.getdoc(MyClass)                      # "A sample class."
inspect.getsource(MyClass)                   # source code as string
inspect.signature(MyClass.method)            # (self, x: int) -> str
inspect.isclass(MyClass)                     # True
inspect.isfunction(MyClass.method)           # True (unbound)
inspect.ismethod(obj.method)                 # True (bound)

# Signature:
sig = inspect.signature(MyClass.method)
for name, param in sig.parameters.items():
    print(name, param.annotation, param.default)
```

```
┌──────────────────── Common Introspection Tools ──────────────────────┐
│                                                                       │
│  type(obj)              → what class created this object             │
│  isinstance(obj, cls)   → is obj an instance of cls (or subclass)?   │
│  issubclass(cls, base)  → is cls a subclass of base?                 │
│  dir(obj)               → all attribute/method names (inherited too) │
│  vars(obj)              → instance __dict__ only                     │
│  hasattr(obj, name)     → does attribute exist?                      │
│  getattr(obj, name)     → get attribute by string name               │
│  setattr(obj, name, v)  → set attribute by string name               │
│  inspect.signature(fn)  → parameter names, annotations, defaults     │
│  inspect.getsource(obj) → source code as string                      │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

⚠️ **Common Mistake:** Using `dir()` and assuming all listed attributes exist on the instance. `dir()` includes inherited attributes from parent classes. Use `vars(obj)` or `obj.__dict__` for only the instance's own attributes.

💡 **Hint:** `getattr(obj, name, default)` accepts a third argument — the default value to return if the attribute doesn't exist. Use this instead of `hasattr` + `getattr` in sequence: `value = getattr(obj, "optional_field", None)`.

📝 **Practice:** [Q28 · dir/callable](./practice.md#q28--dir-and-callable) · [Q29 · dynamic attributes](./practice.md#q29--dynamic-attributes) · [Q30 · inspect.signature](./practice.md#q30--inspect-signature) | **Deep dive:** [05_advanced_patterns/theory.md](./05_advanced_patterns/theory.md)

> [↑ Back to Top](#top)

---

<a id="13-typing-and-protocols"></a>
# 13. Typing and Protocols

Think of a Protocol like a job posting that says "must know Python and SQL" — it doesn't care which university you went to or what companies you've worked for. It only cares about what you can DO. Any object that has the right methods satisfies a Protocol, regardless of inheritance. This is "structural typing" — shape matters, not lineage.

**`Protocol` enables structural subtyping (duck typing with type-checker support):**

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    """Any class with a draw() method satisfies this Protocol."""
    def draw(self) -> None: ...

class Circle:
    def draw(self):
        print("○")

class Square:
    def draw(self):
        print("□")

class NotDrawable:
    def something_else(self): ...

# Works at runtime (because @runtime_checkable):
isinstance(Circle(), Drawable)        # True
isinstance(NotDrawable(), Drawable)   # False

def render(shape: Drawable) -> None:
    shape.draw()   # type-safe!

render(Circle())   # ✅
render(Square())   # ✅
render(NotDrawable())  # TypeError at runtime, type error at check time
```

**Key typing features:**

```python
from typing import (
    Optional,      # X | None  (use X | None in Python 3.10+)
    Union,         # A | B
    List, Dict, Tuple, Set,  # use list, dict, tuple, set in Python 3.9+
    TypeVar,       # generic type variable
    Generic,       # generic class base
    Callable,      # callable with signature
    Any,           # disable type checking
    ClassVar,      # class-level variable
    Final,         # constant
    Literal,       # specific literal values
    TypedDict,     # dict with typed keys
    overload,      # multiple signatures
)

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

s: Stack[int] = Stack()
s.push(42)
x: int = s.pop()
```

⚠️ **Common Mistake:** Adding `@runtime_checkable` to every Protocol "just in case." Runtime checks only verify that the required methods exist — they don't check signatures or return types. For performance-sensitive code, avoid runtime Protocol checks in hot paths.

💡 **Hint:** Use `Protocol` instead of ABC when you don't control the classes that need to satisfy the interface. If you're writing a library and want users' existing classes to "just work," Protocol is more flexible than forcing inheritance from your ABC.

📝 **Practice:** [Q34 · Protocol](./practice.md#q34--protocol)

> [↑ Back to Top](#top)

---

<a id="-summary-table"></a>
## 🔥 Summary Table

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  FEATURE              WHAT IT IS                      WHEN TO USE            │
│  ──────────────────────────────────────────────────────────────────────────  │
│  Dunder methods       Hooks into Python syntax         Always — repr, eq, etc│
│  __repr__ / __str__   Object representation            Every custom class     │
│  __eq__ + __hash__    Equality + hashability           Sets/dicts/sorting     │
│  Operator overload    Define +, -, *, ==, etc.         Math/science classes   │
│  Container protocol   __len__, __getitem__, __iter__   Custom collection types│
│  __bool__             Truthiness                       When 0 ≠ False for you │
│  __slots__            Memory optimization              10k+ small instances   │
│  Descriptors          Managed attribute access         Validation, computed   │
│  @property            Computed attribute               Input validation       │
│  Metaclass            Factory for classes              Frameworks, plugins    │
│  __init_subclass__    Hook when class is subclassed    Simpler than metaclass │
│  @dataclass           Auto-generated boilerplate       Data container classes │
│  ABC                  Interface definition             Contracts in libraries │
│  Enum                 Named constants                  Status, flags, cats    │
│  Protocol             Structural typing                Duck typing + safety   │
│  Introspection        Runtime object inspection        Debug, frameworks      │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

<a id="-navigation"></a>
## 🔁 Navigation

**This folder:**
[theory.md](./theory.md) · [cheetsheet.md](./cheetsheet.md) · [interview.md](./interview.md) · [practice.md](./practice.md)

**Subfolders:**
[01_dunder_methods/theory.md](./01_dunder_methods/theory.md) · [02_descriptors/theory.md](./02_descriptors/theory.md) · [03_metaclasses/theory.md](./03_metaclasses/theory.md) · [04_dataclasses/theory.md](./04_dataclasses/theory.md) · [05_advanced_patterns/theory.md](./05_advanced_patterns/theory.md)

**Related modules:**
[14 — Type Hints & Pydantic](../14_type_hints_and_pydantic/theory.md) · [05 — OOP](../05_oops/theory.md) · [10 — Decorators](../10_decorators/theory.md)

**Jump to specific topics:**
[Dunder Methods Table](#1-dunder-methods--pythons-protocol-system) · [Descriptor Protocol](#7-descriptors--the-power-behind-properties) · [How @property Works](#how-property-works-internally) · [Metaclass Registry](#custom-metaclass--registry-pattern) · [__init_subclass__](#__init_subclass__--modern-alternative)

---

| | |
|---|---|
| ⬅ Prev Module | [14 — Type Hints & Pydantic](../14_type_hints_and_pydantic/theory.md) |
| ➡ Next Module | [16 — Design Patterns](../16_design_patterns/theory.md) |

**[🏠 Back to README](../../README.md)**

