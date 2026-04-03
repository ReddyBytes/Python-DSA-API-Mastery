# 🏠 11 — Properties: @property, getter, setter, deleter

> *"Properties let your objects lie beautifully.*
> *From the outside, it looks like a simple attribute.*
> *On the inside, it's running full validation logic."*

---

## 🎬 The Story

You're building a user profile system.
Age is stored as a number.
But what happens if someone sets `user.age = -5`? Or `user.age = 999`?

Option 1: Expose the attribute directly → no protection.
Option 2: Write `get_age()` / `set_age()` methods → ugly, Java-style.
Option 3: Use `@property` → attribute-style access + full control behind the scenes.

Python chose Option 3. And it's beautiful.

---

## 🔑 What `@property` Actually Is

`@property` turns a method into an attribute-style accessor.
The caller reads it like a variable — but Python runs your method.

```python
class Circle:
    def __init__(self, radius):
        self.__radius = radius

    @property
    def radius(self):           # getter — called on: circle.radius
        return self.__radius

c = Circle(5)
print(c.radius)     # 5     ← looks like attribute access
print(c.radius)     # 5     ← but actually calls the method!

# c.radius = 10    # ← AttributeError: can't set — no setter defined yet
```

---

## ✍️ Adding a Setter

```python
class Circle:
    def __init__(self, radius):
        self.radius = radius    # ← calls the SETTER! (validation happens here)

    @property
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"Radius must be a number, got {type(value).__name__}")
        if value < 0:
            raise ValueError(f"Radius cannot be negative, got {value}")
        self.__radius = value

c = Circle(5)
c.radius = 10        # ← calls setter, validates, stores
print(c.radius)      # 10

# c.radius = -3     # ← ValueError: Radius cannot be negative
# c.radius = "big"  # ← TypeError: Radius must be a number
```

> **Notice:** `self.radius = radius` in `__init__` calls the setter!
> This is the correct pattern — validation happens from the very first assignment.

---

## 🗑️ Adding a Deleter

```python
class UserSession:
    def __init__(self, user_id, token):
        self.user_id = user_id
        self.__token = token

    @property
    def token(self):
        return self.__token

    @token.setter
    def token(self, value):
        if not value or len(value) < 10:
            raise ValueError("Token too short")
        self.__token = value

    @token.deleter
    def token(self):
        print(f"Session for user {self.user_id} invalidated")
        self.__token = None

session = UserSession(42, "secure_token_xyz_abc_123")
print(session.token)     # secure_token_xyz_abc_123

del session.token        # ← calls deleter
# Session for user 42 invalidated
print(session.token)     # None
```

---

## 📐 Computed / Derived Properties (Read-Only)

Properties with only a getter are naturally read-only.
Use this for values that should be derived from other data — not stored separately.

```python
class Rectangle:
    def __init__(self, width, height):
        self.width  = width
        self.height = height

    @property
    def area(self):
        return self.width * self.height     # computed on-the-fly

    @property
    def perimeter(self):
        return 2 * (self.width + self.height)

    @property
    def is_square(self):
        return self.width == self.height

r = Rectangle(4, 6)
print(r.area)        # 24     ← no attribute stored, computed each time
print(r.perimeter)   # 20
print(r.is_square)   # False

r.width = 6
print(r.is_square)   # True   ← recomputed with new values!

# r.area = 100       # ← AttributeError: can't set attribute — no setter
```

---

## 💰 Real Production Example — Full Validation

```python
from datetime import date

class Employee:
    VALID_ROLES = {"engineer", "manager", "director", "intern"}

    def __init__(self, name, salary, role, birth_year):
        self.name       = name          # calls setter
        self.salary     = salary        # calls setter
        self.role       = role          # calls setter
        self.birth_year = birth_year    # calls setter

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name must be a non-empty string")
        self.__name = value.strip().title()

    @property
    def salary(self):
        return self.__salary

    @salary.setter
    def salary(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Salary must be numeric")
        if value < 0:
            raise ValueError("Salary cannot be negative")
        self.__salary = float(value)

    @salary.deleter
    def salary(self):
        self.__salary = 0.0

    @property
    def role(self):
        return self.__role

    @role.setter
    def role(self, value):
        if value.lower() not in self.VALID_ROLES:
            raise ValueError(f"Role must be one of {self.VALID_ROLES}")
        self.__role = value.lower()

    @property
    def birth_year(self):
        return self.__birth_year

    @birth_year.setter
    def birth_year(self, value):
        current = date.today().year
        if not (1900 < value <= current):
            raise ValueError(f"Birth year {value} is not valid")
        self.__birth_year = value

    @property
    def age(self):                          # computed — no setter
        return date.today().year - self.__birth_year

    @property
    def annual_salary(self):                # computed — no setter
        return self.__salary * 12

    def __repr__(self):
        return f"Employee({self.__name!r}, role={self.__role}, age={self.age})"

emp = Employee("alice smith", 80000, "Engineer", 1998)
print(emp)                  # Employee('Alice Smith', role=engineer, age=27)
print(emp.age)              # 27     ← computed
print(emp.annual_salary)    # 960000 ← computed

emp.salary = 90000          # updates via setter
print(emp.salary)           # 90000.0
```

---

## 💤 Lazy Property — Compute Once, Cache Forever

Some properties are expensive to compute (database queries, file reads, complex calculations).
You don't want to compute on every access, and you don't want to compute if never accessed.

```python
class DataAnalyzer:
    def __init__(self, filename):
        self.filename = filename
        self._data    = None       # not loaded yet

    @property
    def data(self):
        if self._data is None:
            print("Loading data from file...")   # only runs ONCE
            with open(self.filename) as f:
                self._data = f.read()
        return self._data          # subsequent calls return cached value

    @property
    def word_count(self):
        return len(self.data.split())    # uses cached self.data

analyzer = DataAnalyzer("report.txt")
# No file reading yet — lazy!

print(analyzer.word_count)   # "Loading data from file..."  then count
print(analyzer.word_count)   # Just the count — no loading (cached!)
```

---

## 🔬 How `@property` Works Internally (Descriptor Protocol)

`@property` is actually a **descriptor** — a class that implements `__get__`, `__set__`, `__delete__`.

```python
# The @property [decorator](../10_decorators/theory.md) is roughly equivalent to:
class property:
    def __init__(self, fget=None, fset=None, fdel=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel

    def __get__(self, obj, objtype=None):
        if obj is None: return self          # accessed on class
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

    def getter(self, fget): return type(self)(fget, self.fset, self.fdel)
    def setter(self, fset): return type(self)(self.fget, fset, self.fdel)
    def deleter(self, fdel): return type(self)(self.fget, self.fset, fdel)
```

This is why the pattern is:
```python
@property
def name(self): ...         # property(fget=name)

@name.setter
def name(self, val): ...    # property(fget=name, fset=name) — same property, adds setter
```

The decorator `@name.setter` creates a NEW property object with the same getter + the new setter.

---

## ⚠️ Common Mistakes

```python
# ❌ Mistake 1: Using same name for property and private attribute
class Bad:
    @property
    def name(self):
        return self.name    # ← RecursionError! calls itself forever!

# ✅ Use double underscore for the backing store:
class Good:
    @property
    def name(self):
        return self.__name   # different name — no recursion

# ❌ Mistake 2: Not calling setter from __init__
class Circle:
    def __init__(self, radius):
        self.__radius = radius    # bypasses validation!

    @property
    def radius(self): return self.__radius

    @radius.setter
    def radius(self, v):
        if v < 0: raise ValueError("negative!")
        self.__radius = v

# ✅ Use self.radius = radius in __init__ to go through the setter:
    def __init__(self, radius):
        self.radius = radius    # calls setter ✓

# ❌ Mistake 3: Computed property that modifies state (should be a method):
class Bad:
    @property
    def next_id(self):
        self._counter += 1    # side effect in property — confusing!
        return self._counter

# ✅ Use a method for operations with side effects:
    def get_next_id(self):
        self._counter += 1
        return self._counter
```

---

## 🎯 Key Takeaways

```
• @property = attribute access with method-level logic
• Getter: @property — read access
• Setter: @name.setter — write access with validation
• Deleter: @name.deleter — delete behavior
• No setter = read-only property (AttributeError on assignment)
• Use self.attr = value in __init__ to trigger setter validation
• Name backing store differently: self.__name vs property name
• Lazy property: compute on first access, cache in private attr
• @property is a descriptor under the hood
• Don't put side effects in property getters — use methods instead
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [10 — Class vs Instance Variables](./10_class_vs_instance_variables.md) |
| 📖 Index | [README.md](./README.md) |
| ➡️ Next | [12 — Composition vs Inheritance](./12_composition_vs_inheritance.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Class Vs Instance Variables](./10_class_vs_instance_variables.md) &nbsp;|&nbsp; **Next:** [Theory Part 1 →](./theory_part1.md)

**Related Topics:** [Why Oop](./01_why_oop.md) · [Classes And Objects](./02_classes_and_objects.md) · [Init And Self](./03_init_and_self.md) · [Encapsulation](./04_encapsulation.md) · [Inheritance](./05_inheritance.md) · [Polymorphism](./06_polymorphism.md) · [Abstraction](./07_abstraction.md) · [Dunder Methods](./08_dunder_methods.md) · [Class Instance Static Methods](./09_class_instance_static_methods.md) · [Class Vs Instance Variables](./10_class_vs_instance_variables.md) · [Theory Part 1](./theory_part1.md) · [Composition Vs Inheritance](./12_composition_vs_inheritance.md) · [Theory Part 2](./theory_part2.md) · [Mro And Super](./13_mro_and_super.md) · [Theory Part 3](./theory_part3.md) · [Dataclasses](./14_dataclasses.md) · [Slots](./15_slots.md) · [Metaclasses](./16_metaclasses.md) · [Descriptors](./17_descriptors.md) · [Mixins](./18_mixins.md) · [Solid Principles](./19_solid_principles.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
