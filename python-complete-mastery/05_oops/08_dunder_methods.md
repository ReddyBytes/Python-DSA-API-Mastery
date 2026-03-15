# 🪄 08 — Dunder Methods: Making Objects Feel Built-in

> *"Dunder methods are Python's way of saying:*
> *'Your objects deserve to behave like first-class citizens.'"*

---

## 🎬 The Story

When you type `len([1,2,3])`, Python calls `list.__len__([1,2,3])` internally.
When you type `[1,2] + [3,4]`, Python calls `list.__add__([1,2], [3,4])`.
When you type `print(42)`, Python calls `int.__str__(42)`.

These are **dunder methods** (double underscore on both sides).
Every operator, every built-in function, every `for` loop — all of them work by calling dunder methods.

Define them in your class and your objects integrate seamlessly into Python's ecosystem.

---

## 🗺️ The Complete Dunder Map

```
┌────────────────────────────────────────────────────────────────────────┐
│  CATEGORY           DUNDER           TRIGGERED BY                     │
├────────────────────────────────────────────────────────────────────────┤
│  Construction       __new__          class() before __init__           │
│  Initialization     __init__         class()                           │
│  Destruction        __del__          when object garbage collected     │
├────────────────────────────────────────────────────────────────────────┤
│  String repr        __str__          str(obj), print(obj)              │
│                     __repr__         repr(obj), REPL display           │
│                     __format__       format(obj, spec), f"{obj:spec}"  │
├────────────────────────────────────────────────────────────────────────┤
│  Math operators     __add__          a + b                             │
│                     __sub__          a - b                             │
│                     __mul__          a * b                             │
│                     __truediv__      a / b                             │
│                     __floordiv__     a // b                            │
│                     __mod__          a % b                             │
│                     __pow__          a ** b                            │
│  Reflected math     __radd__         b + a  (when a doesn't handle +) │
│  In-place           __iadd__         a += b                            │
├────────────────────────────────────────────────────────────────────────┤
│  Comparison         __eq__           a == b                            │
│                     __ne__           a != b                            │
│                     __lt__           a < b                             │
│                     __le__           a <= b                            │
│                     __gt__           a > b                             │
│                     __ge__           a >= b                            │
├────────────────────────────────────────────────────────────────────────┤
│  Container          __len__          len(obj)                          │
│                     __getitem__      obj[key]                          │
│                     __setitem__      obj[key] = val                    │
│                     __delitem__      del obj[key]                      │
│                     __contains__     item in obj                       │
│                     __iter__         for x in obj                      │
│                     __next__         next(obj)                         │
├────────────────────────────────────────────────────────────────────────┤
│  Callable           __call__         obj()                             │
├────────────────────────────────────────────────────────────────────────┤
│  Context Manager    __enter__        with obj as x                     │
│                     __exit__         end of with block                 │
├────────────────────────────────────────────────────────────────────────┤
│  Attribute Access   __getattr__      obj.missing_attr                  │
│                     __setattr__      obj.attr = val                    │
│                     __delattr__      del obj.attr                      │
│                     __getattribute__ obj.any_attr (always called)      │
├────────────────────────────────────────────────────────────────────────┤
│  Hashing            __hash__         hash(obj), dict key, set member   │
│  Boolean            __bool__         bool(obj), if obj:                │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📝 `__str__` vs `__repr__` — The Most Confused Pair

```
__str__   → for HUMANS. Called by print(), str(). Should be readable.
__repr__  → for DEVELOPERS. Called by repr(), REPL display. Should be unambiguous.

Rule of thumb:
  __repr__ should ideally produce code that could recreate the object.
  __str__ should produce a pretty, readable description.

If only __repr__ is defined, __str__ falls back to __repr__.
If only __str__ is defined, __repr__ still shows the default <ClassName object>.
```

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"    # dev-facing: recreatable

    def __str__(self):
        return f"({self.x}, {self.y})"          # user-facing: pretty

p = Point(3, 4)

print(p)          # (3, 4)          ← calls __str__
print(repr(p))    # Point(3, 4)     ← calls __repr__
print(str(p))     # (3, 4)          ← calls __str__

# In a list, __repr__ is used:
points = [Point(1, 2), Point(3, 4)]
print(points)     # [Point(1, 2), Point(3, 4)]  ← each uses __repr__!
```

---

## ➕ Arithmetic Operator Overloading

```python
class Money:
    def __init__(self, amount, currency="INR"):
        self.amount   = amount
        self.currency = currency

    def __add__(self, other):
        if isinstance(other, Money):
            if self.currency != other.currency:
                raise ValueError(f"Currency mismatch: {self.currency} vs {other.currency}")
            return Money(self.amount + other.amount, self.currency)
        return Money(self.amount + other, self.currency)    # add plain number

    def __sub__(self, other):
        if isinstance(other, Money):
            return Money(self.amount - other.amount, self.currency)
        return Money(self.amount - other, self.currency)

    def __mul__(self, factor):
        return Money(self.amount * factor, self.currency)

    def __rmul__(self, factor):      # factor * money (factor on left)
        return self.__mul__(factor)

    def __iadd__(self, other):       # += (in-place add)
        self.amount += other.amount if isinstance(other, Money) else other
        return self

    def __eq__(self, other):
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other):
        return self.amount < other.amount

    def __repr__(self):
        return f"Money({self.amount}, '{self.currency}')"

    def __str__(self):
        return f"₹{self.amount:,.2f}" if self.currency == "INR" else f"${self.amount:,.2f}"

salary    = Money(50000)
bonus     = Money(10000)
tax       = Money(5000)

total     = salary + bonus     # Money(60000)
after_tax = total - tax        # Money(55000)
doubled   = salary * 2         # Money(100000)

print(total)       # ₹60,000.00
print(after_tax)   # ₹55,000.00
print(salary < bonus)   # False
print(salary == Money(50000))   # True

salary += bonus    # uses __iadd__
print(salary)      # ₹60,000.00
```

---

## 📦 Container Protocol — Making Objects Act Like Lists/Dicts

```python
class Playlist:
    def __init__(self, name):
        self.name   = name
        self._songs = []

    def __len__(self):
        return len(self._songs)

    def __getitem__(self, index):
        return self._songs[index]

    def __setitem__(self, index, value):
        self._songs[index] = value

    def __delitem__(self, index):
        del self._songs[index]

    def __contains__(self, song):
        return song in self._songs

    def __iter__(self):
        return iter(self._songs)    # makes it iterable!

    def append(self, song):
        self._songs.append(song)

    def __repr__(self):
        return f"Playlist('{self.name}', {len(self)} songs)"

pl = Playlist("Chill Vibes")
pl.append("Blinding Lights")
pl.append("Levitating")
pl.append("Watermelon Sugar")

print(len(pl))                        # 3
print(pl[0])                          # Blinding Lights
print("Levitating" in pl)             # True
print("Song I Don't Have" in pl)      # False

for song in pl:                       # __iter__ makes this work!
    print(f"  ♪ {song}")

pl[0] = "Shape of You"                # __setitem__
del pl[1]                             # __delitem__
print(pl)                             # Playlist('Chill Vibes', 2 songs)
```

---

## 📞 `__call__` — Making Objects Callable

```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor

    def __call__(self, value):          # allows obj(value)
        return value * self.factor

double = Multiplier(2)
triple = Multiplier(3)

print(double(5))     # 10   ← calling an OBJECT like a function!
print(triple(7))     # 21

# Callable objects are great for:
# - Configurable function-like objects
# - Stateful callbacks
# - Replacing functions when you need state
```

**Real use case — a configurable logger:**
```python
class Logger:
    def __init__(self, prefix, enabled=True):
        self.prefix  = prefix
        self.enabled = enabled

    def __call__(self, message):
        if self.enabled:
            print(f"[{self.prefix}] {message}")

debug = Logger("DEBUG", enabled=True)
info  = Logger("INFO",  enabled=True)
prod  = Logger("DEBUG", enabled=False)    # disabled in production

debug("Connecting to database...")   # [DEBUG] Connecting to database...
info("User logged in")               # [INFO] User logged in
prod("Internal trace data")          # (prints nothing)
```

---

## 🚪 Context Manager Protocol — `__enter__` and `__exit__`

```python
class DatabaseConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connection = None

    def __enter__(self):
        print(f"Connecting to {self.host}:{self.port}")
        self.connection = f"conn_{self.host}"   # simulate connection
        return self.connection    # this becomes the `as` variable

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Closing connection to {self.host}")
        self.connection = None
        # return True to suppress exceptions, False/None to propagate
        if exc_type is not None:
            print(f"Error occurred: {exc_val}")
        return False    # don't suppress exceptions

with DatabaseConnection("localhost", 5432) as conn:
    print(f"Using connection: {conn}")
    # do database operations

# Output:
# Connecting to localhost:5432
# Using connection: conn_localhost
# Closing connection to localhost
# (connection closed even if an error happened!)
```

---

## 🔁 Iterator Protocol — `__iter__` and `__next__`

```python
class Countdown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self         # this object IS the iterator

    def __next__(self):
        if self.current < 0:
            raise StopIteration    # signal that iteration is done
        value = self.current
        self.current -= 1
        return value

for n in Countdown(5):
    print(n, end=" ")    # 5 4 3 2 1 0

# You can also use next() manually:
cd = Countdown(3)
print(next(cd))    # 3
print(next(cd))    # 2
print(next(cd))    # 1
print(next(cd))    # 0
# print(next(cd)) # StopIteration!
```

---

## 🔢 `__bool__` and `__hash__`

```python
class BankAccount:
    def __init__(self, balance):
        self.balance = balance

    def __bool__(self):
        return self.balance > 0    # account is "truthy" only if it has money!

    def __hash__(self):
        # Need __hash__ if you want to use object as dict key or in set
        # If you define __eq__, Python sets __hash__ = None unless you define it
        return hash(id(self))

acc1 = BankAccount(500)
acc2 = BankAccount(0)

if acc1:    # True — has money
    print("Account has funds")

if not acc2:    # False — empty
    print("Account is empty")

# Using in a set (requires __hash__):
accounts = {acc1, acc2}
```

> **Rule:** If you define `__eq__`, you should also define `__hash__`.
> Python automatically sets `__hash__ = None` if you define `__eq__` without `__hash__`,
> making your objects unhashable (can't be used as dict keys or in sets).

---

## 🎯 Key Takeaways

```
• Dunder methods = hooks into Python's built-in operations
• __str__ = human-readable; __repr__ = developer-reconstructable
• In lists, __repr__ is used for each element, not __str__
• __add__ → a+b; __radd__ → b+a when a doesn't support +
• __call__ makes an object callable like a function
• __enter__/__exit__ = context manager (with statement)
• __iter__/__next__ = iterator protocol (for loops, next())
• If you define __eq__, also define __hash__
• __bool__ controls truthiness of your object
• Always use @functools.total_ordering when implementing comparisons
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [07 — Abstraction](./07_abstraction.md) |
| 📖 Index | [README.md](./README.md) |
| ➡️ Next | [09 — Class, Instance & Static Methods](./09_class_instance_static_methods.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Abstraction](./07_abstraction.md) &nbsp;|&nbsp; **Next:** [Class Instance Static Methods →](./09_class_instance_static_methods.md)

**Related Topics:** [Why Oop](./01_why_oop.md) · [Classes And Objects](./02_classes_and_objects.md) · [Init And Self](./03_init_and_self.md) · [Encapsulation](./04_encapsulation.md) · [Inheritance](./05_inheritance.md) · [Polymorphism](./06_polymorphism.md) · [Abstraction](./07_abstraction.md) · [Class Instance Static Methods](./09_class_instance_static_methods.md) · [Class Vs Instance Variables](./10_class_vs_instance_variables.md) · [Properties](./11_properties.md) · [Theory Part 1](./theory_part1.md) · [Composition Vs Inheritance](./12_composition_vs_inheritance.md) · [Theory Part 2](./theory_part2.md) · [Mro And Super](./13_mro_and_super.md) · [Theory Part 3](./theory_part3.md) · [Dataclasses](./14_dataclasses.md) · [Slots](./15_slots.md) · [Metaclasses](./16_metaclasses.md) · [Descriptors](./17_descriptors.md) · [Mixins](./18_mixins.md) · [Solid Principles](./19_solid_principles.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
