# 🏗️ OOP Practice — Master Problem Set

> 50 questions covering all 20 OOP topics. For each question: attempt from memory first, then reveal the hint, then check the answer.

---

## Quick Index

| # | Concept | Difficulty |
|---|---------|------------|
| [Q1](#q1--classes--init--self--class-blueprint) | Classes, `__init__`, `self` — class blueprint | 🟢 |
| [Q2](#q2--class-vs-instance-attributes--shared-vs-per-object) | Class vs instance attributes — shared vs per-object | 🟢 |
| [Q3](#q3--classmethod--staticmethod--factory-constructors) | `@classmethod` / `@staticmethod` — factory constructors | 🟡 |
| [Q4](#q4--property--controlled-attribute-access) | `@property` — controlled attribute access | 🟡 |
| [Q5](#q5--inheritance--extending-a-base-class) | Inheritance — extending a base class | 🟡 |
| [Q6](#q6--super--calling-parent-methods) | `super()` — calling parent methods | 🟡 |
| [Q7](#q7--polymorphism--shape-hierarchy) | Polymorphism — shape hierarchy | 🟡 |
| [Q8](#q8--encapsulation--private-attributes-and-validation) | Encapsulation — private attributes and validation | 🟡 |
| [Q9](#q9--abstract-base-class--enforcing-interfaces) | Abstract base class — enforcing interfaces | 🟡 |
| [Q10](#q10--dunder-methods--repr-str-eq) | Dunder methods — `__repr__`, `__str__`, `__eq__` | 🟡 |
| [Q11](#q11--arithmetic-dunder-methods--operator-overloading) | Arithmetic dunder methods — operator overloading | 🟠 |
| [Q12](#q12--total_ordering--comparison-from-two-methods) | `@total_ordering` — comparison from two methods | 🟡 |
| [Q13](#q13--mro--method-resolution-order) | MRO — method resolution order | 🟠 |
| [Q14](#q14--super-in-multiple-inheritance--cooperative-calls) | `super()` in multiple inheritance — cooperative calls | 🟠 |
| [Q15](#q15--mixins--composable-behavior) | Mixins — composable behavior | 🟠 |
| [Q16](#q16--composition-vs-inheritance--when-to-use-which) | Composition vs inheritance — when to use which | 🟡 |
| [Q17](#q17--dataclass--reduce-boilerplate) | `@dataclass` — reduce boilerplate | 🟡 |
| [Q18](#q18--slots--memory-optimization) | `__slots__` — memory optimization | 🟡 |
| [Q19](#q19--descriptor--reusable-attribute-logic) | Descriptor — reusable attribute logic | 🟠 |
| [Q20](#q20--metaclass--class-creation-hook) | Metaclass — class creation hook | 🟠 |
| [Q21](#q21--singleton-pattern--one-instance) | Singleton pattern — one instance | 🟠 |
| [Q22](#q22--factory-pattern--decouple-creation-from-use) | Factory pattern — decouple creation from use | 🟠 |
| [Q23](#q23--observer-pattern--event-bus) | Observer pattern — event bus | 🟠 |
| [Q24](#q24--strategy-pattern--swappable-algorithms) | Strategy pattern — swappable algorithms | 🟠 |
| [Q25](#q25--enum-module--named-constants) | Enum module — named constants | 🟢 |
| [Q26](#q26--method-chaining--fluent-api) | Method chaining — fluent API | 🟡 |
| [Q27](#q27--isinstance--issubclass--type-checks) | `isinstance` / `issubclass` — type checks | 🟢 |
| [Q28](#q28--class-decorator--adding-behavior-to-a-class) | Class decorator — adding behavior to a class | 🟠 |
| [Q29](#q29--state-machine-pattern--valid-transitions) | State machine pattern — valid transitions | 🟠 |
| [Q30](#q30--plugin-registry-pattern--self-registering-classes) | Plugin/registry pattern — self-registering classes | 🟠 |
| [Q31](#q31--solid--single-responsibility-principle) | SOLID — Single Responsibility Principle | 🟡 |
| [Q32](#q32--solid--open-closed-principle) | SOLID — Open/Closed Principle | 🟡 |
| [Q33](#q33--solid--liskov-substitution-principle) | SOLID — Liskov Substitution Principle | 🟡 |
| [Q34](#q34--solid--dependency-inversion-principle) | SOLID — Dependency Inversion Principle | 🟠 |
| [Q35](#q35--why-oop--when-not-to-use-a-class) | Why OOP — when NOT to use a class | 🟢 |
| [Q36](#q36--trace-mro-predict-output) | Trace MRO — predict output | 🟠 |
| [Q37](#q37--property-vs-attribute--design-choice) | `@property` vs attribute — design choice | 🟡 |
| [Q38](#q38--dataclass-with-field-defaults-and-post_init) | Dataclass with `field()` defaults and `__post_init__` | 🟡 |
| [Q39](#q39--abc-plugin-system--open-for-extension) | ABC plugin system — open for extension | 🟠 |
| [Q40](#q40--fix-the-class-bug--common-oop-mistakes) | Fix the class bug — common OOP mistakes | 🟡 |
| [Q41](#q41--descriptor-protocol--get-set-delete) | Descriptor protocol — `__get__`, `__set__`, `__delete__` | 🟠 |
| [Q42](#q42--mixin-combination--json--validation) | Mixin combination — JSON + validation | 🟠 |
| [Q43](#q43--abstract-method-enforcement--subclass-contract) | Abstract method enforcement — subclass contract | 🟡 |
| [Q44](#q44--enum-with-methods-and-values) | Enum with methods and values | 🟡 |
| [Q45](#q45--capstone--design-a-notification-system) | Capstone — design a notification system | 🟠 |
| [Q46](#q46--capstone--e-commerce-order-state-machine) | Capstone — e-commerce order state machine | 🟠 |
| [Q47](#q47--capstone--data-store-abc-with-multiple-backends) | Capstone — data store ABC with multiple backends | 🟠 |
| [Q48](#q48--debug--fix-the-mro-diamond-problem) | Debug — fix the MRO diamond problem | 🟠 |
| [Q49](#q49--real-world--build-a-rate-limiter-class) | Real-world — build a rate limiter class | 🟠 |
| [Q50](#q50--mixed--full-oop-system-in-30-lines) | Mixed — full OOP system in 30 lines | 🟠 |

---

### Q1 · Classes / `__init__` / `self` — Class blueprint

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)
🟢 Basic

Write a `BankAccount` class:
- `__init__(self, owner: str, initial_balance: float = 0.0)` — store owner and balance as instance attributes
- `deposit(self, amount)` — add to balance
- `withdraw(self, amount)` — subtract from balance (raise `ValueError` if insufficient funds)
- `__str__` — return `"Alice's account: $1000.00"`

Test: create two accounts, deposit on one, print both.

<details>
<summary>💡 Hint</summary>

`self.owner = owner` stores the parameter on the instance. Each call to `deposit()` mutates `self.balance`. `__str__` is called by `print()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class BankAccount:
    def __init__(self, owner: str, initial_balance: float = 0.0):
        self.owner = owner
        self.balance = initial_balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount > self.balance:
            raise ValueError(f"Insufficient funds: {self.balance:.2f}")
        self.balance -= amount

    def __str__(self) -> str:
        return f"{self.owner}'s account: ${self.balance:.2f}"

alice = BankAccount("Alice", 1000.0)
bob   = BankAccount("Bob")
alice.deposit(500)
print(alice)   # Alice's account: $1500.00
print(bob)     # Bob's account: $0.00
```

**Why:** `self` is the specific instance being acted on — it's how Python passes the object into its own method. Without `self`, each method call would have no idea which account to modify.
</details>

---

### Q2 · Class vs Instance Attributes — Shared vs per-object

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)
🟢 Basic

Given this code, predict the output and explain why:

```python
class Counter:
    count = 0   # class attribute

    def __init__(self, name):
        self.name = name
        Counter.count += 1

c1 = Counter("Alice")
c2 = Counter("Bob")
print(Counter.count)       # ?
print(c1.count)            # ?
c1.count = 99              # what does this do?
print(Counter.count)       # ?
print(c2.count)            # ?
```

<details>
<summary>💡 Hint</summary>

Class attributes are shared. Assigning `c1.count = 99` creates a NEW instance attribute on `c1` — it shadows the class attribute for `c1` only, without touching `Counter.count`.
</details>

<details>
<summary>✅ Answer</summary>

```
2     # Counter.count was incremented twice by __init__
2     # c1.count reads the class attribute (no instance attr yet)
2     # Counter.count unchanged — c1.count = 99 creates an INSTANCE attr on c1
2     # c2.count still reads the class attribute
```

**Why:** `c1.count = 99` does NOT modify `Counter.count`. It creates a new instance attribute `c1.count` that shadows the class attribute for `c1` only. `Counter.count` and `c2.count` (which falls back to the class attr) stay at 2.

To modify the class attribute, write `Counter.count = 99` — not `c1.count = 99`.
</details>

---

### Q3 · `@classmethod` / `@staticmethod` — Factory constructors

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)
🟡 Intermediate

Add two factory class methods to `Temperature`:
- `from_fahrenheit(cls, f)` — convert Fahrenheit to Celsius and return a new `Temperature`
- `from_kelvin(cls, k)` — convert Kelvin to Celsius and return a new `Temperature`

Also add a static method `is_valid_celsius(value)` — returns `True` if value ≥ −273.15.

```python
class Temperature:
    def __init__(self, celsius: float):
        self._celsius = celsius

    def __repr__(self):
        return f"Temperature({self._celsius:.2f}°C)"
```

<details>
<summary>💡 Hint</summary>

`@classmethod` takes `cls` not `self`. Call `cls(...)` instead of `Temperature(...)` — this is how subclasses work correctly. `@staticmethod` takes no `self` or `cls`.
</details>

<details>
<summary>✅ Answer</summary>

```python
@classmethod
def from_fahrenheit(cls, f: float) -> "Temperature":
    return cls((f - 32) * 5/9)   # cls() works in subclasses too

@classmethod
def from_kelvin(cls, k: float) -> "Temperature":
    return cls(k - 273.15)

@staticmethod
def is_valid_celsius(value: float) -> bool:
    return value >= -273.15

# Usage
t1 = Temperature.from_fahrenheit(212)   # Temperature(100.00°C)
t2 = Temperature.from_kelvin(373.15)    # Temperature(100.00°C)
print(Temperature.is_valid_celsius(-300))  # False
```

**Why:** `cls()` instead of `Temperature()` means if you subclass `Temperature`, `SubTemp.from_fahrenheit()` returns a `SubTemp`, not a base `Temperature`. This is the main reason to use `@classmethod` for factories.
</details>

---

### Q4 · `@property` — Controlled attribute access

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)
🟡 Intermediate

Add a validated `price` property to `Product`:
- Reading `product.price` returns `self._price`
- Setting `product.price = x` raises `ValueError` if `x < 0`
- Add a read-only computed property `total_value` = `price × quantity`

```python
class Product:
    def __init__(self, name: str, price: float, quantity: int):
        self.name = name
        self.price = price        # should call the setter
        self.quantity = quantity
```

<details>
<summary>💡 Hint</summary>

Store the private value in `self._price` (not `self.price`) inside the setter — otherwise you get infinite recursion. A read-only property has only a getter, no setter.
</details>

<details>
<summary>✅ Answer</summary>

```python
@property
def price(self) -> float:
    return self._price

@price.setter
def price(self, value: float) -> None:
    if value < 0:
        raise ValueError(f"Price cannot be negative: {value}")
    self._price = value   # _price, not price (infinite recursion otherwise)

@property
def total_value(self) -> float:
    return self._price * self.quantity

# Test
p = Product("Widget", 9.99, 50)
print(p.total_value)   # 499.50
p.price = 12.99
try:
    p.price = -5       # ValueError
except ValueError as e:
    print(e)
try:
    p.total_value = 1  # AttributeError: read-only
except AttributeError as e:
    print(e)
```

**Why:** `@property` lets you keep the clean `product.price` access syntax while enforcing invariants. No `getPrice()`/`setPrice()` Java-style verbosity needed.
</details>

---

### Q5 · Inheritance — Extending a base class

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)
🟡 Intermediate

Build a `SavingsAccount` that extends a given `Account` base class:
- Add `rate` attribute (interest rate, default `0.05`)
- Add `withdrawal_limit = 3` class attribute
- Override `withdraw()` — raise `ValueError` if more than 3 withdrawals have been made this period; otherwise call `super().withdraw()`
- Add `add_interest()` — deposits `balance * rate` and returns the interest amount

```python
class Account:
    def __init__(self, owner: str, balance: float = 0.0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        return self

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        return self
```

<details>
<summary>💡 Hint</summary>

Always call `super().__init__(owner, balance)` first in your `__init__`. Track withdrawal count in `self._withdrawals_this_period`. Use `super().withdraw(amount)` after checking the limit.
</details>

<details>
<summary>✅ Answer</summary>

```python
class SavingsAccount(Account):
    WITHDRAWAL_LIMIT = 3

    def __init__(self, owner: str, balance: float = 0.0, rate: float = 0.05):
        super().__init__(owner, balance)   # always call parent first
        self.rate = rate
        self._withdrawals_this_period = 0

    def withdraw(self, amount: float):
        if self._withdrawals_this_period >= self.WITHDRAWAL_LIMIT:
            raise ValueError(f"Withdrawal limit ({self.WITHDRAWAL_LIMIT}) reached")
        super().withdraw(amount)
        self._withdrawals_this_period += 1
        return self

    def add_interest(self) -> float:
        interest = self.balance * self.rate
        self.deposit(interest)
        return interest

savings = SavingsAccount("Alice", 1000, rate=0.04)
savings.deposit(500)
print(savings.add_interest())   # 60.0 (4% of 1500)
```

**Why:** `super().__init__()` ensures the parent's initialization runs — without it, `self.owner` and `self.balance` would never be set. `super().withdraw()` reuses the parent's validation logic.
</details>

---

### Q6 · `super()` — Calling parent methods

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)
🟡 Intermediate

What does each `print` output? Explain why.

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return f"{self.name} makes a sound"

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed

    def speak(self):
        parent_result = super().speak()
        return f"{parent_result} — specifically: Woof!"

d = Dog("Rex", "Labrador")
print(d.speak())
print(isinstance(d, Animal))
print(type(d).__name__)
```

<details>
<summary>💡 Hint</summary>

`super().speak()` calls `Animal.speak(self)` using the same `self` (the `Dog` instance), so `self.name` is available.
</details>

<details>
<summary>✅ Answer</summary>

```
Rex makes a sound — specifically: Woof!
True
Dog
```

**Why:** `super()` returns a proxy to the parent class. `super().speak()` calls `Animal.speak(d)` — `d` is still the receiver, so `self.name = "Rex"` is visible. `isinstance(d, Animal)` is `True` because Dog IS-A Animal.
</details>

---

### Q7 · Polymorphism — Shape hierarchy

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)
🟡 Intermediate

Create a `Shape` base class and `Circle`, `Rectangle`, `Triangle` subclasses. Each must implement `area()` and `perimeter()`.

Write a `describe_all(shapes)` function that prints each shape's type, area, and perimeter — without using `if isinstance(...)` anywhere.

<details>
<summary>💡 Hint</summary>

The whole point of polymorphism: `describe_all` calls `shape.area()` on every shape without caring what type it is. Python dispatches to the right `area()` automatically.
</details>

<details>
<summary>✅ Answer</summary>

```python
import math

class Shape:
    def area(self) -> float:
        raise NotImplementedError
    def perimeter(self) -> float:
        raise NotImplementedError

class Circle(Shape):
    def __init__(self, r): self.r = r
    def area(self): return math.pi * self.r ** 2
    def perimeter(self): return 2 * math.pi * self.r

class Rectangle(Shape):
    def __init__(self, w, h): self.w = w; self.h = h
    def area(self): return self.w * self.h
    def perimeter(self): return 2 * (self.w + self.h)

class Triangle(Shape):
    def __init__(self, a, b, c): self.a = a; self.b = b; self.c = c
    def area(self):
        s = (self.a + self.b + self.c) / 2
        return math.sqrt(s*(s-self.a)*(s-self.b)*(s-self.c))
    def perimeter(self): return self.a + self.b + self.c

def describe_all(shapes):
    for s in shapes:
        print(f"{type(s).__name__}: area={s.area():.2f}, perimeter={s.perimeter():.2f}")

describe_all([Circle(5), Rectangle(4, 6), Triangle(3, 4, 5)])
```

**Why:** No `isinstance` needed — each shape knows its own formula. `describe_all` is written against the `Shape` interface and works for every current and future subclass.
</details>

---

### Q8 · Encapsulation — Private attributes and validation

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)
🟡 Intermediate

A `Person` class has `name` and `age`. Encapsulate `age`:
- Store internally as `_age`
- Raise `ValueError` for `age < 0` or `age > 150`
- Provide a `birthday()` method that increments age by 1
- Make `name` read-only (set once in `__init__`, no setter)

<details>
<summary>💡 Hint</summary>

A property with only a getter (no setter) is read-only. Trying to assign to it raises `AttributeError`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Person:
    def __init__(self, name: str, age: int):
        self._name = name    # private storage
        self.age = age       # goes through the setter

    @property
    def name(self) -> str:
        return self._name    # read-only: no setter

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        if not 0 <= value <= 150:
            raise ValueError(f"Invalid age: {value}")
        self._age = value

    def birthday(self) -> None:
        self._age += 1   # bypass setter (already valid)

p = Person("Alice", 30)
p.birthday()
print(p.age)   # 31
try:
    p.name = "Bob"   # AttributeError
except AttributeError as e:
    print(e)
```

**Why:** Encapsulation isn't about `__double_underscore` — single underscore convention signals "internal." The property setter is the enforcement point for invariants.
</details>

---

### Q9 · Abstract Base Class — Enforcing interfaces

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)
🟡 Intermediate

Create an abstract `DataStore` class with abstract methods `get(key)`, `set(key, value)`, `delete(key)`.

Add a concrete method `get_or_default(key, default=None)` that uses `self.get()`.

Implement `InMemoryStore` using a dict.

Show that trying to instantiate `DataStore` directly raises `TypeError`, and that an incomplete subclass also raises `TypeError`.

<details>
<summary>💡 Hint</summary>

Import `ABC` and `abstractmethod` from `abc`. Any class inheriting from `ABC` that doesn't implement all `@abstractmethod` methods cannot be instantiated.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class DataStore(ABC):
    @abstractmethod
    def get(self, key: str):
        ...

    @abstractmethod
    def set(self, key: str, value) -> None:
        ...

    @abstractmethod
    def delete(self, key: str) -> bool:
        ...

    def get_or_default(self, key: str, default=None):
        value = self.get(key)
        return value if value is not None else default


class InMemoryStore(DataStore):
    def __init__(self):
        self._store = {}

    def get(self, key): return self._store.get(key)
    def set(self, key, value): self._store[key] = value
    def delete(self, key):
        return bool(self._store.pop(key, None))

# ABC prevents instantiation
try:
    DataStore()
except TypeError as e:
    print(f"Cannot instantiate ABC: {e}")

# Incomplete subclass also fails
try:
    class Bad(DataStore):
        def get(self, key): return None
    Bad()
except TypeError as e:
    print(f"Incomplete subclass: {e}")

store = InMemoryStore()
store.set("x", 42)
print(store.get("x"))            # 42
print(store.get_or_default("y", "missing"))  # missing
```

**Why:** `@abstractmethod` enforces the contract at instantiation time — not at call time. You get a clear error when defining an incomplete subclass, not a confusing runtime error later.
</details>

---

### Q10 · Dunder Methods — `__repr__`, `__str__`, `__eq__`

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)
🟡 Intermediate

Add `__repr__`, `__str__`, and `__eq__` to this `Point` class:
- `__repr__` → `"Point(3, 4)"` (Python-evaluable)
- `__str__` → `"(3, 4)"` (human-friendly)
- `__eq__` → two points are equal if both `x` and `y` match

Also explain: when is `__repr__` called vs `__str__`?

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

<details>
<summary>💡 Hint</summary>

`print(obj)` calls `__str__`. The REPL, `repr(obj)`, and container displays call `__repr__`. If `__str__` is absent, Python falls back to `__repr__`. Return `NotImplemented` from `__eq__` when comparing to an incompatible type.
</details>

<details>
<summary>✅ Answer</summary>

```python
def __repr__(self) -> str:
    return f"Point({self.x}, {self.y})"   # evaluable: eval("Point(3,4)") works

def __str__(self) -> str:
    return f"({self.x}, {self.y})"   # human display

def __eq__(self, other) -> bool:
    if not isinstance(other, Point):
        return NotImplemented   # let Python try the reverse comparison
    return self.x == other.x and self.y == other.y

p1 = Point(3, 4)
p2 = Point(3, 4)
print(p1)           # (3, 4)  — calls __str__
print(repr(p1))     # Point(3, 4) — calls __repr__
print([p1])         # [Point(3, 4)] — container uses __repr__
print(p1 == p2)     # True
```

**Why:** `__repr__` is for developers (debug output, REPL). `__str__` is for end users. When `__str__` is missing, Python falls back to `__repr__` — so always define `__repr__` first.
</details>

---

### Q11 · Arithmetic Dunder Methods — Operator overloading

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)
🟠 Advanced

Implement a `Vector` class where `+`, `-`, `*` (scalar), and `abs()` work naturally:

```python
v1 = Vector(3, 4)
v2 = Vector(1, 2)
print(v1 + v2)   # Vector(4, 6)
print(v1 - v2)   # Vector(2, 2)
print(v1 * 3)    # Vector(9, 12)
print(3 * v1)    # Vector(9, 12)  — note: scalar on left!
print(abs(v1))   # 5.0  — magnitude
```

<details>
<summary>💡 Hint</summary>

`3 * v1` calls `int.__mul__(3, v1)` which returns `NotImplemented`, so Python then tries `v1.__rmul__(3)`. Implement `__rmul__` to handle scalar-on-left. Magnitude = `sqrt(x² + y²)` → implement with `__abs__`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import math

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self): return f"Vector({self.x}, {self.y})"

    def __add__(self, other): return Vector(self.x + other.x, self.y + other.y)
    def __sub__(self, other): return Vector(self.x - other.x, self.y - other.y)
    def __mul__(self, scalar): return Vector(self.x * scalar, self.y * scalar)
    def __rmul__(self, scalar): return self.__mul__(scalar)  # 3 * v

    def __abs__(self):
        return math.sqrt(self.x**2 + self.y**2)   # magnitude

    def __neg__(self): return Vector(-self.x, -self.y)

v1, v2 = Vector(3, 4), Vector(1, 2)
print(v1 + v2)    # Vector(4, 6)
print(v1 * 3)     # Vector(9, 12)
print(3 * v1)     # Vector(9, 12) — uses __rmul__
print(abs(v1))    # 5.0
```

**Why:** `__rmul__` is the "reflected" version — called when the left operand doesn't know how to handle the right operand. This is how NumPy arrays support `2 * array`.
</details>

---

### Q12 · `@total_ordering` — Comparison from two methods

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)
🟡 Intermediate

Use `@total_ordering` to give a `Temperature` class full comparison support (`<`, `<=`, `>`, `>=`, `==`) by only defining `__eq__` and `__lt__`.

Verify that `sort()` works on a list of temperatures.

<details>
<summary>💡 Hint</summary>

`from functools import total_ordering`. Decorate the class. Provide `__eq__` and `__lt__` — the decorator derives the other four comparison methods automatically.
</details>

<details>
<summary>✅ Answer</summary>

```python
from functools import total_ordering

@total_ordering
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def __eq__(self, other):
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.celsius == other.celsius

    def __lt__(self, other):
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.celsius < other.celsius

    def __repr__(self):
        return f"Temperature({self.celsius}°C)"

temps = [Temperature(100), Temperature(0), Temperature(37)]
temps.sort()
print(temps)   # [Temperature(0°C), Temperature(37°C), Temperature(100°C)]
print(Temperature(100) > Temperature(37))   # True — from @total_ordering
```

**Why:** Defining all six comparison methods manually is repetitive and error-prone. `@total_ordering` provides the other four for free, derived from `__eq__` + `__lt__`.
</details>

---

### Q13 · MRO — Method resolution order

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)
🟠 Advanced

What is the MRO of `D`? Predict the output:

```python
class A:
    def greet(self): return "A"

class B(A):
    def greet(self): return "B → " + super().greet()

class C(A):
    def greet(self): return "C → " + super().greet()

class D(B, C):
    def greet(self): return "D → " + super().greet()

print(D().greet())
print([c.__name__ for c in D.__mro__])
```

<details>
<summary>💡 Hint</summary>

Python uses C3 linearization. For `D(B, C)`: D first, then B's chain, then C's chain, then the shared base A. `super()` in each class follows the MRO chain, not just "my parent."
</details>

<details>
<summary>✅ Answer</summary>

```
D → B → C → A
['D', 'B', 'C', 'A', 'object']
```

**Why:** C3 linearization for `D(B, C)` produces `D → B → C → A → object`. When `B.greet` calls `super().greet()`, it doesn't call `A.greet` — it follows the MRO and calls `C.greet` next. This is "cooperative multiple inheritance."
</details>

---

### Q14 · `super()` in Multiple Inheritance — Cooperative calls

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)
🟠 Advanced

Build a mixin chain where `super()` chains correctly through multiple classes. Three mixins (LogMixin, TimerMixin, CacheMixin) each override `process()`. Compose them so all three run when `process()` is called on a combined class.

<details>
<summary>💡 Hint</summary>

Each mixin must call `super().process()` at the right point. The order they're listed in the class definition controls the MRO — and thus the call chain.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Base:
    def process(self, data):
        return data

class LogMixin:
    def process(self, data):
        print(f"  [LOG] Processing: {data!r}")
        return super().process(data)

class CacheMixin:
    _cache = {}
    def process(self, data):
        if data in self._cache:
            print(f"  [CACHE] Hit: {data}")
            return self._cache[data]
        result = super().process(data)
        self._cache[data] = result
        return result

class Processor(LogMixin, CacheMixin, Base):
    pass

p = Processor()
p.process("hello")   # LogMixin logs, CacheMixin misses and calls Base
p.process("hello")   # LogMixin logs, CacheMixin hits (no Base call)
```

**Why:** `super()` in mixin context follows MRO: `Processor → LogMixin → CacheMixin → Base`. Each mixin calls `super()` so the chain continues. Remove any `super()` call and the chain breaks.
</details>

---

### Q15 · Mixins — Composable behavior

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)
🟠 Advanced

Create two mixins:
1. `JSONMixin` — adds `to_json()` and `from_json(cls, json_str)` (requires subclass to implement `to_dict()`)
2. `ValidationMixin` — adds `validate()` that checks all fields in `_required_fields` are non-empty

Combine them in a `User` class with `name`, `email`, `role` attributes.

<details>
<summary>💡 Hint</summary>

`JSONMixin.to_json()` calls `self.to_dict()` — the mixin assumes the combined class implements `to_dict()`. `ValidationMixin` uses `getattr(self, field, None)` to check each required field.
</details>

<details>
<summary>✅ Answer</summary>

```python
import json

class JSONMixin:
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str):
        return cls(**json.loads(json_str))

class ValidationMixin:
    _required_fields: list = []

    def validate(self) -> bool:
        for field in self._required_fields:
            value = getattr(self, field, None)
            if not value or (isinstance(value, str) and not value.strip()):
                raise ValueError(f"Field '{field}' is required")
        return True

class User(JSONMixin, ValidationMixin):
    _required_fields = ["name", "email"]

    def __init__(self, name, email, role="user"):
        self.name = name
        self.email = email
        self.role = role

    def to_dict(self):
        return {"name": self.name, "email": self.email, "role": self.role}

user = User("Alice", "alice@example.com")
user.validate()
print(user.to_json())

# Round-trip
user2 = User.from_json('{"name": "Bob", "email": "b@x.com", "role": "admin"}')
print(user2.name)
```

**Why:** Mixins provide opt-in behavior. Any class that has a `to_dict()` gets `to_json()` for free. No inheritance hierarchy needed — just mix in what you need.
</details>

---

### Q16 · Composition vs Inheritance — When to use which

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)
🟡 Intermediate

Refactor this inheritance design to use composition instead:

```python
class EmailSender:
    def send(self, to, body):
        print(f"Sending email to {to}: {body}")

class OrderConfirmation(EmailSender):  # IS-A EmailSender? No — HAS-A
    def confirm(self, order_id, customer_email):
        self.send(customer_email, f"Order {order_id} confirmed!")
```

Explain when to prefer composition over inheritance.

<details>
<summary>💡 Hint</summary>

"IS-A" test: Is `OrderConfirmation` a type of `EmailSender`? No — it uses one. That's a HAS-A relationship → use composition: accept an `EmailSender` in `__init__`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class EmailSender:
    def send(self, to, body):
        print(f"Sending email to {to}: {body}")

class OrderConfirmation:
    def __init__(self, sender: EmailSender):
        self._sender = sender   # HAS-A, not IS-A

    def confirm(self, order_id, customer_email):
        self._sender.send(customer_email, f"Order {order_id} confirmed!")

# Now we can swap out the sender without touching OrderConfirmation
confirmation = OrderConfirmation(EmailSender())
confirmation.confirm("ORD-001", "alice@example.com")
```

**Composition vs Inheritance:**
- Use **inheritance** when there's a clear IS-A relationship and you want polymorphism
- Use **composition** when you're reusing behavior (HAS-A), or when the relationship might change
- Rule of thumb: "Favor composition over inheritance" — Django's class-based views use mixins (thin inheritance) + composition for the heavy lifting
</details>

---

### Q17 · `@dataclass` — Reduce boilerplate

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)
🟡 Intermediate

Rewrite this class as a `@dataclass`. Include:
- Default values
- `__post_init__` to validate that `price > 0`
- A field computed from others (hint: use `field(default_factory=...)`)

```python
class Product:
    def __init__(self, name: str, price: float, tags: list = None):
        self.name = name
        self.price = price
        self.tags = tags or []
        if price <= 0:
            raise ValueError("Price must be positive")
```

<details>
<summary>💡 Hint</summary>

Use `field(default_factory=list)` for mutable defaults — never `tags: list = []` in a dataclass. `__post_init__` runs after `__init__` for custom validation.
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass, field

@dataclass
class Product:
    name: str
    price: float
    tags: list = field(default_factory=list)  # NEVER use tags: list = []

    def __post_init__(self):
        if self.price <= 0:
            raise ValueError(f"Price must be positive, got {self.price}")

p1 = Product("Widget", 9.99)
p2 = Product("Gadget", 24.99, tags=["electronics", "sale"])
print(p1)   # Product(name='Widget', price=9.99, tags=[])
print(p2)   # Product(name='Gadget', price=24.99, tags=['electronics', 'sale'])

try:
    Product("Bad", -1)
except ValueError as e:
    print(e)
```

**Why:** `@dataclass` generates `__init__`, `__repr__`, and `__eq__` automatically. `field(default_factory=list)` ensures each instance gets its own list — using `[]` directly would share one list across all instances (the mutable default argument trap).
</details>

---

### Q18 · `__slots__` — Memory optimization

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)
🟡 Intermediate

Add `__slots__` to this class. Explain what changes and what breaks:

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

What happens if you try `p.__dict__`? What happens if you add `p.z = 5` without `z` in `__slots__`?

<details>
<summary>💡 Hint</summary>

`__slots__` replaces the per-instance `__dict__` with fixed-size slots. No `__dict__` means no arbitrary attribute assignment and lower memory per instance. Trade-off: less flexible.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Point:
    __slots__ = ("x", "y")   # only these attributes allowed

    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(3, 4)
print(p.x)   # 3

try:
    print(p.__dict__)    # AttributeError — no __dict__ with __slots__
except AttributeError as e:
    print(f"No __dict__: {e}")

try:
    p.z = 5    # AttributeError — z not in __slots__
except AttributeError as e:
    print(f"Can't add z: {e}")
```

**Why:** `__slots__` saves ~40–60 bytes per instance by eliminating `__dict__`. Critical when creating millions of objects (e.g. coordinate objects in a GIS system). Trade-off: can't add new attributes dynamically.
</details>

---

### Q19 · Descriptor — Reusable attribute logic

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)
🟠 Advanced

Write a `Validator` descriptor that enforces a minimum value for any attribute:

```python
class Product:
    price    = Validator(min_value=0.0)
    quantity = Validator(min_value=0)

p = Product()
p.price = 9.99    # OK
p.price = -1.0    # ValueError: must be >= 0.0
```

<details>
<summary>💡 Hint</summary>

A descriptor implements `__get__`, `__set__`, `__set_name__`. Store values in the instance's `__dict__` using the attribute name (passed to `__set_name__` via `self.name`). Use `instance.__dict__[self.name]` to avoid triggering the descriptor's own `__get__`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Validator:
    def __init__(self, min_value):
        self.min_value = min_value
        self.name = None   # set by __set_name__

    def __set_name__(self, owner, name):
        self.name = name   # Python calls this automatically

    def __get__(self, instance, owner):
        if instance is None:
            return self   # accessed on class, not instance
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        if value < self.min_value:
            raise ValueError(f"{self.name} must be >= {self.min_value}, got {value}")
        instance.__dict__[self.name] = value


class Product:
    price    = Validator(min_value=0.0)
    quantity = Validator(min_value=0)

    def __init__(self, price, quantity):
        self.price = price
        self.quantity = quantity

p = Product(9.99, 10)
try:
    p.price = -1
except ValueError as e:
    print(e)   # price must be >= 0.0, got -1
```

**Why:** Descriptors put the validation logic in ONE place (the descriptor class) instead of repeating it in every setter. Django model fields, SQLAlchemy columns, and Pydantic fields are all implemented as descriptors.
</details>

---

### Q20 · Metaclass — Class creation hook

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)
🟠 Advanced

Write a metaclass `SingletonMeta` that ensures only one instance of any class using it can be created:

```python
class Config(metaclass=SingletonMeta):
    pass

a = Config()
b = Config()
print(a is b)   # True
```

<details>
<summary>💡 Hint</summary>

A metaclass's `__call__` is invoked when you call `Config()`. Override `__call__` to check if an instance already exists. Store the instance in a dict keyed by class.
</details>

<details>
<summary>✅ Answer</summary>

```python
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Config(metaclass=SingletonMeta):
    def __init__(self, value="default"):
        self.value = value

a = Config("first")
b = Config("second")   # ignored — returns the same instance
print(a is b)          # True
print(a.value)         # "first"
```

**Why:** Metaclasses control class *creation* — they're the "class of a class." `type` is the default metaclass. Overriding `__call__` intercepts every `Config()` call. Simpler alternatives: module-level singleton or `__new__` override in the class itself.
</details>

---

### Q21 · Singleton Pattern — One instance

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)
🟠 Advanced

Implement a Singleton using `__new__` (not a metaclass):

```python
class DatabasePool:
    # should return the same instance every time
    pool1 = DatabasePool("postgres://localhost/app", 5)
    pool2 = DatabasePool("postgres://other/db", 20)
    print(pool1 is pool2)   # True
    print(pool2.url)        # postgres://localhost/app
```

<details>
<summary>💡 Hint</summary>

`__new__` creates the object before `__init__` runs. Store `_instance` as a class attribute. Check if it exists before creating. Use a `_initialized` flag to skip re-running `__init__` on subsequent calls.
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
        return cls._instance   # always the same object

    def __init__(self, url: str, pool_size: int = 10):
        if self._initialized:
            return   # skip re-initialization
        self.url = url
        self.pool_size = pool_size
        self._initialized = True

pool1 = DatabasePool("postgres://localhost/app", 5)
pool2 = DatabasePool("postgres://other/db", 20)
print(pool1 is pool2)   # True
print(pool2.url)        # postgres://localhost/app
```

**Why:** `__new__` controls object creation. The `_initialized` guard prevents `__init__` from overwriting the first instance's data when called again. In practice, a module-level instance is simpler and often preferred.
</details>

---

### Q22 · Factory Pattern — Decouple creation from use

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)
🟠 Advanced

Build a `NotificationFactory` that creates the right notification type from a string:

```python
factory = NotificationFactory()
notif = factory.create("email")
notif.send("alice@x.com", "Your order shipped!")
```

Support `"email"`, `"sms"`, `"push"`. Add a `register(channel, class)` method to extend the factory without modifying it.

<details>
<summary>💡 Hint</summary>

Store a `_registry` dict mapping channel names to classes. `create(channel)` looks up the class and instantiates it. `register()` adds new entries — this is the Open/Closed principle in action.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def send(self, user: str, message: str) -> str: ...

class EmailNotification(Notification):
    def send(self, user, message): return f"[EMAIL] To: {user} | {message}"

class SMSNotification(Notification):
    def send(self, user, message): return f"[SMS] To: {user} | {message[:160]}"

class PushNotification(Notification):
    def send(self, user, message): return f"[PUSH] To: {user} | {message[:50]}"

class NotificationFactory:
    _registry = {"email": EmailNotification, "sms": SMSNotification, "push": PushNotification}

    @classmethod
    def create(cls, channel: str) -> Notification:
        if channel not in cls._registry:
            raise ValueError(f"Unknown channel: {channel}")
        return cls._registry[channel]()

    @classmethod
    def register(cls, channel: str, notification_class: type):
        cls._registry[channel] = notification_class

# Extend without modifying the factory
class SlackNotification(Notification):
    def send(self, user, message): return f"[SLACK] @{user}: {message}"

NotificationFactory.register("slack", SlackNotification)

for ch in ["email", "sms", "slack"]:
    n = NotificationFactory.create(ch)
    print(n.send("alice", "Hello!"))
```

**Why:** The factory decouples callers from concrete classes. Adding a new notification type is one `register()` call — no changes to existing code. This is the Open/Closed principle.
</details>

---

### Q23 · Observer Pattern — Event bus

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)
🟠 Advanced

Build a simple `EventBus` where components can:
- `subscribe(event, handler)` — register a callback
- `publish(event, **data)` — call all registered handlers
- `unsubscribe(event, handler)` — remove a specific handler

Test: subscribe 3 handlers to `"user_registered"`, publish the event, verify all 3 fire.

<details>
<summary>💡 Hint</summary>

Store `_subscribers: dict[str, list[Callable]]`. `publish()` iterates the list for that event key. `unsubscribe()` rebuilds the list excluding the target handler.
</details>

<details>
<summary>✅ Answer</summary>

```python
from typing import Callable

class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = {}

    def subscribe(self, event: str, handler: Callable) -> None:
        self._subscribers.setdefault(event, []).append(handler)

    def unsubscribe(self, event: str, handler: Callable) -> None:
        if event in self._subscribers:
            self._subscribers[event] = [h for h in self._subscribers[event] if h is not handler]

    def publish(self, event: str, **data) -> None:
        for handler in self._subscribers.get(event, []):
            handler(**data)

bus = EventBus()

def send_email(user_id, email, **_):   print(f"  [EMAIL] Welcome to {email}")
def track_signup(user_id, **_):        print(f"  [ANALYTICS] Tracking user {user_id}")
def provision(user_id, **_):           print(f"  [PROVISIONING] Setting up user {user_id}")

bus.subscribe("user_registered", send_email)
bus.subscribe("user_registered", track_signup)
bus.subscribe("user_registered", provision)

bus.publish("user_registered", user_id=42, email="alice@example.com")
```

**Why:** The publisher knows nothing about its subscribers — complete decoupling. Adding a new handler (audit log, Slack notification) is one `subscribe()` call, no changes to the publishing code.
</details>

---

### Q24 · Strategy Pattern — Swappable algorithms

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)
🟠 Advanced

Create a `Sorter` class that accepts a sorting strategy function and uses it in a `sort(data)` method. Support at least: bubble sort, Python's built-in sort, and a reverse sort — all swappable at runtime.

<details>
<summary>💡 Hint</summary>

Strategy pattern in Python is just passing a function. Store `self._strategy = strategy_fn` in `__init__`. Call `self._strategy(data)` in `sort()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from typing import Callable

def bubble_sort(data: list) -> list:
    arr = data[:]
    for i in range(len(arr)):
        for j in range(len(arr) - i - 1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def builtin_sort(data: list) -> list:
    return sorted(data)

def reverse_sort(data: list) -> list:
    return sorted(data, reverse=True)

class Sorter:
    def __init__(self, strategy: Callable = builtin_sort):
        self._strategy = strategy

    def set_strategy(self, strategy: Callable):
        self._strategy = strategy

    def sort(self, data: list) -> list:
        return self._strategy(data)

data = [3, 1, 4, 1, 5, 9, 2, 6]
sorter = Sorter(bubble_sort)
print(sorter.sort(data))   # [1, 1, 2, 3, 4, 5, 6, 9]

sorter.set_strategy(reverse_sort)
print(sorter.sort(data))   # [9, 6, 5, 4, 3, 2, 1, 1]
```

**Why:** Strategies are just callables in Python — no Strategy ABC needed (unlike Java). Swapping algorithms at runtime without changing the calling code is the point.
</details>

---

### Q25 · Enum Module — Named constants

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)
🟢 Basic

Replace these magic string constants with a proper `OrderStatus` enum:

```python
# Before
status = "pending"
if status == "confirmed":   ...
if status in ["shipped", "delivered"]:   ...
```

Use `enum.Enum`. Add a class method `can_transition(current, new)` that encodes valid transitions.

<details>
<summary>💡 Hint</summary>

`from enum import Enum`. Compare enum members with `is` or `==`. Never with bare string comparison after defining the enum.
</details>

<details>
<summary>✅ Answer</summary>

```python
from enum import Enum

class OrderStatus(Enum):
    PENDING   = "pending"
    CONFIRMED = "confirmed"
    SHIPPED   = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

    TRANSITIONS = {
        "pending":   {"confirmed", "cancelled"},
        "confirmed": {"shipped", "cancelled"},
        "shipped":   {"delivered"},
        "delivered": set(),
        "cancelled": set(),
    }

    @classmethod
    def can_transition(cls, current: "OrderStatus", new: "OrderStatus") -> bool:
        return new.value in cls.TRANSITIONS.value.get(current.value, set())

status = OrderStatus.PENDING
print(status)          # OrderStatus.PENDING
print(status.value)    # pending
print(status == OrderStatus.PENDING)   # True
```

**Why:** Enums give you auto-completion, typo-proof constants, and iteration. `status == "pending"` fails silently if you typo it. `status == OrderStatus.PENDING` raises `AttributeError` on typos — caught immediately.
</details>

---

### Q26 · Method Chaining — Fluent API

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)
🟡 Intermediate

Add method chaining to a `QueryBuilder` class so this works:

```python
query = (QueryBuilder("users")
    .where("age > 18")
    .where("active = true")
    .order_by("name")
    .limit(10)
    .build())
# → SELECT * FROM users WHERE age > 18 AND active = true ORDER BY name LIMIT 10
```

<details>
<summary>💡 Hint</summary>

Each method must `return self` at the end. This lets the next method call chain onto the same object.
</details>

<details>
<summary>✅ Answer</summary>

```python
class QueryBuilder:
    def __init__(self, table: str):
        self._table = table
        self._conditions = []
        self._order = None
        self._limit = None

    def where(self, condition: str) -> "QueryBuilder":
        self._conditions.append(condition)
        return self   # enables chaining

    def order_by(self, column: str) -> "QueryBuilder":
        self._order = column
        return self

    def limit(self, n: int) -> "QueryBuilder":
        self._limit = n
        return self

    def build(self) -> str:
        sql = f"SELECT * FROM {self._table}"
        if self._conditions:
            sql += " WHERE " + " AND ".join(self._conditions)
        if self._order:
            sql += f" ORDER BY {self._order}"
        if self._limit:
            sql += f" LIMIT {self._limit}"
        return sql

q = (QueryBuilder("users")
     .where("age > 18")
     .where("active = true")
     .order_by("name")
     .limit(10)
     .build())
print(q)
```

**Why:** Fluent APIs (Django ORM, SQLAlchemy) all use `return self`. Each call returns the same object — the next call operates on that same builder. The final `.build()` or `.all()` terminates the chain.
</details>

---

### Q27 · `isinstance` / `issubclass` — Type checks

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)
🟢 Basic

For this class hierarchy, predict ALL outputs:

```python
class Vehicle: pass
class Car(Vehicle): pass
class ElectricCar(Car): pass

tesla = ElectricCar()

print(isinstance(tesla, ElectricCar))
print(isinstance(tesla, Car))
print(isinstance(tesla, Vehicle))
print(isinstance(tesla, object))
print(issubclass(ElectricCar, Vehicle))
print(issubclass(Car, ElectricCar))
print(type(tesla) is Car)
print(type(tesla) is ElectricCar)
```

<details>
<summary>💡 Hint</summary>

`isinstance` checks the entire inheritance chain. `type(x) is Y` is an exact type match — no inheritance considered.
</details>

<details>
<summary>✅ Answer</summary>

```
True   # tesla IS-A ElectricCar (direct)
True   # tesla IS-A Car (via ElectricCar)
True   # tesla IS-A Vehicle (two levels up)
True   # everything IS-A object (root of all Python classes)
True   # ElectricCar IS-A subclass of Vehicle (two levels up)
False  # Car is NOT a subclass of ElectricCar (wrong direction)
False  # type(tesla) is Car: exact type is ElectricCar, not Car
True   # exact type match
```

**Why:** Use `isinstance` for normal checks (respects inheritance). Use `type(x) is Y` only when you need exact type matching (no subclasses allowed). In most real code, `isinstance` is the right tool.
</details>

---

### Q28 · Class Decorator — Adding behavior to a class

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)
🟠 Advanced

Write a `@register` class decorator that adds every decorated class to a central registry dict, keyed by the class name.

```python
registry = {}

@register(registry)
class Dog: pass

@register(registry)
class Cat: pass

print(registry)   # {"Dog": <class 'Dog'>, "Cat": <class 'Cat'>}
```

<details>
<summary>💡 Hint</summary>

A class decorator takes a class and returns a class. To pass an argument (`registry`), you need an outer function that returns the actual decorator. Pattern: `decorator_factory → decorator → class`.
</details>

<details>
<summary>✅ Answer</summary>

```python
def register(registry: dict):
    def decorator(cls):
        registry[cls.__name__] = cls
        return cls   # return the class unchanged
    return decorator

registry = {}

@register(registry)
class Dog: pass

@register(registry)
class Cat: pass

print(registry)   # {'Dog': <class '__main__.Dog'>, 'Cat': <class '__main__.Cat'>}
print(registry["Dog"]())   # <__main__.Dog object>
```

**Why:** Class decorators are used to auto-register classes into frameworks (Flask routes, pytest plugins, Django admin). Same 3-layer pattern as decorators with arguments — the outer layer accepts config, the inner accepts the class.
</details>

---

### Q29 · State Machine Pattern — Valid transitions

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)
🟠 Advanced

Build an `Order` class whose status can only transition through valid states:
- `PENDING → CONFIRMED → SHIPPED → DELIVERED`
- `PENDING or CONFIRMED → CANCELLED`
- Any invalid transition raises `ValueError`

<details>
<summary>💡 Hint</summary>

Define the valid transitions as a dict. A private `_transition(new_status)` method does the check and update. Public methods (`confirm()`, `ship()`, etc.) just call `_transition()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class OrderStatus:
    PENDING   = "pending"
    CONFIRMED = "confirmed"
    SHIPPED   = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

    TRANSITIONS = {
        PENDING:   {CONFIRMED, CANCELLED},
        CONFIRMED: {SHIPPED, CANCELLED},
        SHIPPED:   {DELIVERED},
        DELIVERED: set(),
        CANCELLED: set(),
    }

    @classmethod
    def can_transition(cls, current, new):
        return new in cls.TRANSITIONS.get(current, set())


class Order:
    def __init__(self, customer_id: str):
        self.customer_id = customer_id
        self._status = OrderStatus.PENDING

    def _transition(self, new_status: str):
        if not OrderStatus.can_transition(self._status, new_status):
            raise ValueError(f"Cannot go from {self._status} → {new_status}")
        self._status = new_status

    def confirm(self):  self._transition(OrderStatus.CONFIRMED)
    def ship(self):     self._transition(OrderStatus.SHIPPED)
    def deliver(self):  self._transition(OrderStatus.DELIVERED)
    def cancel(self):   self._transition(OrderStatus.CANCELLED)

    @property
    def status(self): return self._status

order = Order("cust-42")
order.confirm()
order.ship()
try:
    order.cancel()   # invalid: can't cancel a shipped order
except ValueError as e:
    print(e)
order.deliver()
print(order.status)   # delivered
```

**Why:** Encoding transitions as data (a dict) means adding a new state is one dict change. Centralizing the check in `_transition()` means invalid states are impossible — not just unlikely.
</details>

---

### Q30 · Plugin/Registry Pattern — Self-registering classes

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)
🟠 Advanced

Build a `TransformerRegistry` where transformer classes self-register using a decorator:

```python
@TransformerRegistry.register
class UppercaseTransformer:
    name = "uppercase"
    def transform(self, data: list) -> list:
        return [str(x).upper() for x in data]

t = TransformerRegistry.get("uppercase")
print(t.transform(["hello", "world"]))   # ['HELLO', 'WORLD']
```

<details>
<summary>💡 Hint</summary>

`TransformerRegistry.register` is a classmethod that stores the class in a dict and returns the class unchanged. Self-registration means the class declares its own name and the decorator wires it in.
</details>

<details>
<summary>✅ Answer</summary>

```python
class TransformerRegistry:
    _transformers: dict = {}

    @classmethod
    def register(cls, transformer_class):
        """Decorator — registers the class using its .name attribute."""
        cls._transformers[transformer_class.name] = transformer_class
        return transformer_class   # return unchanged

    @classmethod
    def get(cls, name: str):
        if name not in cls._transformers:
            raise KeyError(f"Unknown transformer: {name}")
        return cls._transformers[name]()

@TransformerRegistry.register
class UppercaseTransformer:
    name = "uppercase"
    def transform(self, data): return [str(x).upper() for x in data]

@TransformerRegistry.register
class ReverseTransformer:
    name = "reverse"
    def transform(self, data): return data[::-1]

t = TransformerRegistry.get("uppercase")
print(t.transform(["hello", "world"]))   # ['HELLO', 'WORLD']
print(list(TransformerRegistry._transformers.keys()))   # ['uppercase', 'reverse']
```

**Why:** Plugin systems (pytest plugins, Flask extensions) use this pattern. Classes opt-in by using the decorator. The registry never needs to know the class name in advance.
</details>

---

### Q31 · SOLID — Single Responsibility Principle

> 🛠️ **Solve locally:** [practice_local.py → Q31](./practice_local.py)
🟡 Intermediate

This class violates SRP. Identify the problem and refactor:

```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def save_to_db(self, db_conn):
        db_conn.execute(f"INSERT INTO users VALUES ('{self.name}', '{self.email}')")

    def send_welcome_email(self):
        print(f"Sending welcome email to {self.email}")

    def generate_report(self):
        return f"User Report: {self.name} ({self.email})"
```

<details>
<summary>💡 Hint</summary>

`User` has three responsibilities: data model, database persistence, email sending, reporting. SRP says one class = one reason to change. Separate each responsibility.
</details>

<details>
<summary>✅ Answer</summary>

```python
class User:
    """Data model only — one responsibility."""
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

class UserRepository:
    """Database persistence — separate responsibility."""
    def save(self, user: User, db_conn):
        db_conn.execute(f"INSERT INTO users VALUES (?, ?)", (user.name, user.email))

class EmailService:
    """Email sending — separate responsibility."""
    def send_welcome(self, user: User):
        print(f"Sending welcome email to {user.email}")

class UserReporter:
    """Reporting — separate responsibility."""
    def generate(self, user: User) -> str:
        return f"User Report: {user.name} ({user.email})"
```

**Why:** Each class has one reason to change. If the database schema changes, only `UserRepository` changes. If the email template changes, only `EmailService` changes. Mixing them means a template change could break database logic.
</details>

---

### Q32 · SOLID — Open/Closed Principle

> 🛠️ **Solve locally:** [practice_local.py → Q32](./practice_local.py)
🟡 Intermediate

This discount calculator violates OCP. Refactor it:

```python
def calculate_discount(price, customer_type):
    if customer_type == "regular":
        return price * 0.0
    elif customer_type == "premium":
        return price * 0.1
    elif customer_type == "vip":
        return price * 0.2
    # Adding "employee" requires editing this function ← violates OCP
```

<details>
<summary>💡 Hint</summary>

Open for extension, closed for modification. Use a strategy dict or ABC so adding a new discount type is a new class/entry — not an `elif` change.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, price: float) -> float: ...

class NoDiscount(DiscountStrategy):
    def calculate(self, price): return 0.0

class PremiumDiscount(DiscountStrategy):
    def calculate(self, price): return price * 0.1

class VIPDiscount(DiscountStrategy):
    def calculate(self, price): return price * 0.2

# Adding employee discount = new class, no existing code changes
class EmployeeDiscount(DiscountStrategy):
    def calculate(self, price): return price * 0.3

_DISCOUNTS = {
    "regular": NoDiscount(),
    "premium": PremiumDiscount(),
    "vip":     VIPDiscount(),
    "employee": EmployeeDiscount(),
}

def calculate_discount(price: float, customer_type: str) -> float:
    strategy = _DISCOUNTS.get(customer_type, NoDiscount())
    return strategy.calculate(price)

print(calculate_discount(100, "vip"))       # 20.0
print(calculate_discount(100, "employee")) # 30.0
```

**Why:** Adding a new discount type is a new `DiscountStrategy` subclass + one dict entry. The `calculate_discount` function never changes. This is "open for extension, closed for modification."
</details>

---

### Q33 · SOLID — Liskov Substitution Principle

> 🛠️ **Solve locally:** [practice_local.py → Q33](./practice_local.py)
🟡 Intermediate

Does this subclass violate LSP? Fix it:

```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)

    @Rectangle.width.setter  # type: ignore
    def width(self, value):
        self._width = self._height = value   # keeps width == height

def stretch(rect: Rectangle):
    rect.width = 10
    assert rect.area() == 10 * rect.height, "Area mismatch!"

r = Rectangle(5, 4)
stretch(r)   # OK

s = Square(5)
stretch(s)   # Fails LSP — area mismatch
```

<details>
<summary>💡 Hint</summary>

LSP: subclasses must be substitutable for the parent without breaking behavior. A Square IS-NOT-A Rectangle in OOP terms (because Square's width/height constraint violates Rectangle's contract). Fix: separate classes or use composition.
</details>

<details>
<summary>✅ Answer</summary>

```python
# Fix: Don't make Square inherit from Rectangle.
# Both implement a Shape interface instead.

from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    def area(self): return self.width * self.height

class Square(Shape):
    def __init__(self, side):
        self.side = side
    def area(self): return self.side ** 2

# Now stretch only works with Rectangle (as intended)
def stretch(rect: Rectangle):
    rect.width = 10
    assert rect.area() == 10 * rect.height

r = Rectangle(5, 4)
stretch(r)   # OK

s = Square(5)
# stretch(s) — would be a type error: Square is not a Rectangle
```

**Why:** The classic LSP violation. The real problem: a Square IS-A Rectangle mathematically, but NOT in OOP — because Square's invariant (width == height) breaks Rectangle's behavior when width is changed independently. Model them as siblings sharing a `Shape` interface.
</details>

---

### Q34 · SOLID — Dependency Inversion Principle

> 🛠️ **Solve locally:** [practice_local.py → Q34](./practice_local.py)
🟠 Advanced

This code violates DIP. Refactor:

```python
class OrderProcessor:
    def __init__(self):
        self.db = MySQLDatabase()   # hardcoded dependency
        self.email = SMTPEmailService()   # hardcoded dependency

    def process(self, order):
        self.db.save(order)
        self.email.send(order.customer_email, "Order confirmed")
```

<details>
<summary>💡 Hint</summary>

DIP: depend on abstractions, not concretions. Inject dependencies through `__init__`. Define ABCs for `Database` and `EmailService`. The caller decides which implementations to use.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def save(self, order): ...

class EmailService(ABC):
    @abstractmethod
    def send(self, to: str, body: str): ...

# Concrete implementations
class MySQLDatabase(Database):
    def save(self, order): print(f"MySQL: saving order {order}")

class SMTPEmailService(EmailService):
    def send(self, to, body): print(f"SMTP: sending to {to}: {body}")

# Testable stub
class InMemoryDatabase(Database):
    def __init__(self): self.saved = []
    def save(self, order): self.saved.append(order)

class OrderProcessor:
    def __init__(self, db: Database, email: EmailService):
        self.db = db       # injected — no hardcoded dependency
        self.email = email

    def process(self, order):
        self.db.save(order)
        self.email.send(order["customer_email"], "Order confirmed")

# Production
processor = OrderProcessor(MySQLDatabase(), SMTPEmailService())
processor.process({"id": 1, "customer_email": "alice@x.com"})

# Testing — swap in stubs without touching OrderProcessor
test_db = InMemoryDatabase()
processor_test = OrderProcessor(test_db, SMTPEmailService())
```

**Why:** High-level modules (`OrderProcessor`) should not depend on low-level modules (`MySQLDatabase`). Both should depend on abstractions. This makes `OrderProcessor` testable, swappable, and decoupled from infrastructure choices.
</details>

---

### Q35 · Why OOP — When NOT to use a class

> 🛠️ **Solve locally:** [practice_local.py → Q35](./practice_local.py)
🟢 Basic

Which of these should be a class vs a module-level function? Explain:

```python
# Option A
class TemperatureConverter:
    @staticmethod
    def to_fahrenheit(c): return c * 9/5 + 32
    @staticmethod
    def to_kelvin(c): return c + 273.15

# Option B
def celsius_to_fahrenheit(c): return c * 9/5 + 32
def celsius_to_kelvin(c): return c + 273.15
```

<details>
<summary>💡 Hint</summary>

Classes are for things that have **state** (attributes) and **behavior** that operates on that state. A bag of static methods with no state is just a namespace — use a module instead.
</details>

<details>
<summary>✅ Answer</summary>

**Option B is better here.**

A class with only `@staticmethod` methods and no instance state is a namespace disguised as a class. Python already has modules as namespaces — use them.

**Use a class when:**
- There's state to track (BankAccount has `balance`)
- Multiple instances with different states are needed
- You want inheritance or polymorphism

**Don't use a class when:**
- It's just a collection of unrelated utility functions
- There's no instance state
- You're just grouping things for organization — use a module

```python
# Even simpler: just a module (temperature.py)
def to_fahrenheit(c): return c * 9/5 + 32
def to_kelvin(c): return c + 273.15
```

**Why:** The Zen of Python — "Simple is better than complex." If you don't need instances, don't force a class.
</details>

---

### Q36 · Trace MRO — Predict output

> 🛠️ **Solve locally:** [practice_local.py → Q36](./practice_local.py)
🟠 Advanced

Trace the MRO and predict the exact output:

```python
class A:
    def method(self): return "A"

class B(A):
    def method(self): return "B+" + super().method()

class C(A):
    def method(self): return "C+" + super().method()

class D(B, C):
    pass

print(D().method())
print([c.__name__ for c in D.__mro__])
```

<details>
<summary>💡 Hint</summary>

`D` inherits `method` from `B` (first in MRO). `B.method` calls `super().method()` — which in `D`'s context is `C.method()`, not `A.method()`. C3 linearization: `D → B → C → A → object`.
</details>

<details>
<summary>✅ Answer</summary>

```
B+C+A
['D', 'B', 'C', 'A', 'object']
```

**Step-by-step:**
1. `D().method()` — `D` has no `method`, MRO goes to `B.method`
2. `B.method()` returns `"B+" + super().method()`
3. `super()` in `B` when called on `D` → follows D's MRO → calls `C.method`
4. `C.method()` returns `"C+" + super().method()`
5. `super()` in `C` → calls `A.method`
6. `A.method()` returns `"A"`
7. Build up: `"A"` → `"C+A"` → `"B+C+A"`
</details>

---

### Q37 · `@property` vs Attribute — Design choice

> 🛠️ **Solve locally:** [practice_local.py → Q37](./practice_local.py)
🟡 Intermediate

When should you use `@property` vs a plain attribute? Refactor this code appropriately:

```python
class Circle:
    def __init__(self, radius):
        self.radius = radius
        self.diameter = radius * 2   # problem: can get out of sync
        self.area = 3.14159 * radius ** 2   # problem: same
```

<details>
<summary>💡 Hint</summary>

Values that can be derived from other attributes should be computed properties — not stored attributes. Stored derived attributes can get out of sync when the source changes.
</details>

<details>
<summary>✅ Answer</summary>

```python
import math

class Circle:
    def __init__(self, radius):
        self.radius = radius   # only store the source of truth

    @property
    def diameter(self) -> float:
        return self.radius * 2   # always current

    @property
    def area(self) -> float:
        return math.pi * self.radius ** 2   # always current

c = Circle(5)
print(c.diameter)   # 10
print(c.area)       # 78.53...

c.radius = 10
print(c.diameter)   # 20 — automatically updated
print(c.area)       # 314.15... — automatically updated
```

**When to use `@property`:**
- Computed/derived values (always use property — avoids sync bugs)
- Validated setters (range checks, type checks)
- Lazy computation (expensive to compute, compute once on first access)

**When to use plain attribute:**
- Independently settable values with no derivation
- Performance-critical code where property overhead matters
</details>

---

### Q38 · Dataclass with `field()` Defaults and `__post_init__`

> 🛠️ **Solve locally:** [practice_local.py → Q38](./practice_local.py)
🟡 Intermediate

Create an `Employee` dataclass with:
- `name: str`, `salary: float`, `department: str = "General"`
- `reports: list` — mutable default (use `field(default_factory=list)`)
- `__post_init__` validation: salary ≥ 30,000
- A `give_raise(amount)` method

<details>
<summary>💡 Hint</summary>

`field(default_factory=list)` creates a new list for each instance. `__post_init__` runs after `__init__` — raise there for validation. Regular methods work normally in dataclasses.
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass, field

@dataclass
class Employee:
    name: str
    salary: float
    department: str = "General"
    reports: list = field(default_factory=list)   # new list per instance

    def __post_init__(self):
        if self.salary < 30_000:
            raise ValueError(f"Salary {self.salary} below minimum 30,000")

    def give_raise(self, amount: float) -> None:
        self.salary += amount

e1 = Employee("Alice", 75_000, "Engineering")
e2 = Employee("Bob", 65_000)
e1.give_raise(5_000)
print(e1)   # Employee(name='Alice', salary=80000, department='Engineering', reports=[])

try:
    Employee("Intern", 10_000)
except ValueError as e:
    print(e)
```
</details>

---

### Q39 · ABC Plugin System — Open for extension

> 🛠️ **Solve locally:** [practice_local.py → Q39](./practice_local.py)
🟠 Advanced

Build a report generator that supports multiple formats (CSV, JSON, HTML) using an ABC. New formats should be addable without changing the core generator.

<details>
<summary>💡 Hint</summary>

`ReportFormatter` is the ABC with an abstract `format(data)` method. `ReportGenerator` takes a `formatter: ReportFormatter` — no hardcoded format logic.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod
import json, csv, io

class ReportFormatter(ABC):
    @abstractmethod
    def format(self, data: list[dict]) -> str: ...

class CSVFormatter(ReportFormatter):
    def format(self, data):
        output = io.StringIO()
        if not data: return ""
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()

class JSONFormatter(ReportFormatter):
    def format(self, data):
        return json.dumps(data, indent=2)

class HTMLFormatter(ReportFormatter):
    def format(self, data):
        rows = "".join(f"<tr>{''.join(f'<td>{v}</td>' for v in row.values())}</tr>" for row in data)
        return f"<table>{rows}</table>"

class ReportGenerator:
    def __init__(self, formatter: ReportFormatter):
        self._formatter = formatter

    def generate(self, data: list[dict]) -> str:
        return self._formatter.format(data)

data = [{"name": "Alice", "score": 95}, {"name": "Bob", "score": 87}]
for fmt in [CSVFormatter(), JSONFormatter(), HTMLFormatter()]:
    gen = ReportGenerator(fmt)
    print(type(fmt).__name__ + ":")
    print(gen.generate(data)[:80])
```
</details>

---

### Q40 · Fix the Class Bug — Common OOP mistakes

> 🛠️ **Solve locally:** [practice_local.py → Q40](./practice_local.py)
🟡 Intermediate

Each snippet has a subtle bug. Identify and fix all three:

**Bug 1:**
```python
class Logger:
    messages = []   # class attribute

    def log(self, msg):
        self.messages.append(msg)

l1 = Logger()
l2 = Logger()
l1.log("hello")
print(l2.messages)   # should be [] but shows ["hello"]
```

**Bug 2:**
```python
class Config:
    def __init__(self, settings={}):   # bug here
        self.settings = settings
```

**Bug 3:**
```python
class Node:
    def __init__(self, value, children=[]):   # bug here
        self.value = value
        self.children = children
```

<details>
<summary>💡 Hint</summary>

Mutable class attributes are shared. Mutable default arguments are evaluated once at function definition — not per call.
</details>

<details>
<summary>✅ Answer</summary>

**Bug 1 — Shared mutable class attribute:**
```python
class Logger:
    def __init__(self):
        self.messages = []   # instance attribute — each Logger gets its own list
```

**Bug 2 — Mutable default argument:**
```python
class Config:
    def __init__(self, settings=None):
        self.settings = settings if settings is not None else {}
```

**Bug 3 — Same mutable default argument trap:**
```python
class Node:
    def __init__(self, value, children=None):
        self.value = value
        self.children = children if children is not None else []
```

**Why:** `messages = []` at class level creates ONE list shared by ALL instances. `children=[]` in the default creates ONE list shared by ALL calls where `children` isn't passed. The fix in both cases: initialize in `__init__` or use `None` as the default sentinel.
</details>

---

### Q41 · Descriptor Protocol — `__get__`, `__set__`, `__delete__`

> 🛠️ **Solve locally:** [practice_local.py → Q41](./practice_local.py)
🟠 Advanced

Implement a `TypedAttribute` descriptor that enforces a specific type on assignment:

```python
class Point:
    x = TypedAttribute(int)
    y = TypedAttribute(int)

p = Point()
p.x = 3     # OK
p.x = "hi"  # TypeError: x must be int, got str
```

<details>
<summary>💡 Hint</summary>

The descriptor's `__set_name__` receives the attribute name. `__set__` validates the type before storing. Store the value in `instance.__dict__[self.name]` to avoid recursive calls.
</details>

<details>
<summary>✅ Answer</summary>

```python
class TypedAttribute:
    def __init__(self, expected_type):
        self.expected_type = expected_type
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name} must be {self.expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
        instance.__dict__[self.name] = value


class Point:
    x = TypedAttribute(int)
    y = TypedAttribute(int)

p = Point()
p.x = 3
p.y = 4
print(p.x, p.y)   # 3 4

try:
    p.x = "oops"
except TypeError as e:
    print(e)   # x must be int, got str
```
</details>

---

### Q42 · Mixin Combination — JSON + Validation

> 🛠️ **Solve locally:** [practice_local.py → Q42](./practice_local.py)
🟠 Advanced

Use `JSONMixin` and `ValidationMixin` (from Q15) to create a `Product` model. Add a `@classmethod from_dict(cls, data)` method and show a round-trip: `Product → JSON string → new Product`.

<details>
<summary>💡 Hint</summary>

`from_json` already handles the round-trip if `to_dict` and `__init__` are consistent. Test that `validate()` catches a missing `name` field.
</details>

<details>
<summary>✅ Answer</summary>

```python
import json

class JSONMixin:
    def to_json(self): return json.dumps(self.to_dict(), indent=2)
    @classmethod
    def from_json(cls, s): return cls(**json.loads(s))

class ValidationMixin:
    _required_fields = []
    def validate(self):
        for f in self._required_fields:
            if not getattr(self, f, None):
                raise ValueError(f"'{f}' is required")
        return True

class Product(JSONMixin, ValidationMixin):
    _required_fields = ["name", "sku"]

    def __init__(self, name, sku, price=0.0):
        self.name = name
        self.sku = sku
        self.price = price

    def to_dict(self): return {"name": self.name, "sku": self.sku, "price": self.price}

p = Product("Widget", "WGT-001", 9.99)
p.validate()
json_str = p.to_json()
print(json_str)

p2 = Product.from_json(json_str)   # round-trip
print(p2.name, p2.sku, p2.price)

try:
    Product("", "SKU-001").validate()
except ValueError as e:
    print(e)
```
</details>

---

### Q43 · Abstract Method Enforcement — Subclass contract

> 🛠️ **Solve locally:** [practice_local.py → Q43](./practice_local.py)
🟡 Intermediate

Create an `Animal` ABC with abstract methods `speak()` and `move()`. Create 3 concrete animals. Show that trying to instantiate an incomplete subclass fails at instantiation — not at the method call.

<details>
<summary>💡 Hint</summary>

Python raises `TypeError` when you try to instantiate a class that inherits from `ABC` but doesn't implement all `@abstractmethod` methods — regardless of whether you call those methods.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self) -> str: ...

    @abstractmethod
    def move(self) -> str: ...

    def describe(self):
        return f"{type(self).__name__}: '{self.speak()}' while {self.move()}"

class Dog(Animal):
    def speak(self): return "Woof"
    def move(self): return "running"

class Bird(Animal):
    def speak(self): return "Tweet"
    def move(self): return "flying"

class Fish(Animal):
    def speak(self): return "..."
    def move(self): return "swimming"

for animal in [Dog(), Bird(), Fish()]:
    print(animal.describe())

# Incomplete subclass — fails at instantiation, not method call
try:
    class PartialAnimal(Animal):
        def speak(self): return "?"
        # Missing move()
    PartialAnimal()   # TypeError here, before any method is called
except TypeError as e:
    print(f"\nCannot instantiate: {e}")
```
</details>

---

### Q44 · Enum with Methods and Values

> 🛠️ **Solve locally:** [practice_local.py → Q44](./practice_local.py)
🟡 Intermediate

Create a `Color` enum with RGB values. Add a `to_hex()` method and a `brighten()` method. Show iteration over all enum members.

```python
Color.RED.to_hex()       # "#FF0000"
Color.BLUE.to_hex()      # "#0000FF"
Color.GREEN.brighten()   # lighter green
```

<details>
<summary>💡 Hint</summary>

Enum values can be tuples. Access tuple components via `self.value[0]`, `self.value[1]`, etc. Methods on enums work exactly like class methods.
</details>

<details>
<summary>✅ Answer</summary>

```python
from enum import Enum

class Color(Enum):
    RED   = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE  = (0, 0, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    @property
    def r(self): return self.value[0]
    @property
    def g(self): return self.value[1]
    @property
    def b(self): return self.value[2]

    def to_hex(self) -> str:
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"

    def brighten(self, amount: int = 50) -> "Color":
        """Returns closest color after brightening (simplified)."""
        return Color(tuple(min(255, c + amount) for c in self.value))

print(Color.RED.to_hex())     # #FF0000
print(Color.BLUE.to_hex())    # #0000FF

for color in Color:
    print(f"{color.name}: {color.to_hex()}")
```
</details>

---

### Q45 · Capstone — Design a notification system

> 🛠️ **Solve locally:** [practice_local.py → Q45](./practice_local.py)
🟠 Advanced

Design and implement a complete notification system with:
- Abstract `NotificationChannel` base class
- At least 3 concrete channels (Email, SMS, Slack)
- `NotificationService` that accepts multiple channels and sends to all
- Each channel has a rate limit (max sends per hour)
- Method chaining: `service.add_channel(email).add_channel(sms).send("Message")`

<details>
<summary>💡 Hint</summary>

`NotificationService` holds a list of channels. Each channel tracks its own send count. `add_channel()` appends and returns `self` for chaining. `send()` iterates all channels.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod
import time

class NotificationChannel(ABC):
    def __init__(self, rate_limit: int = 100):
        self._rate_limit = rate_limit
        self._send_count = 0
        self._reset_time = time.time() + 3600

    def _check_rate_limit(self) -> bool:
        if time.time() > self._reset_time:
            self._send_count = 0
            self._reset_time = time.time() + 3600
        return self._send_count < self._rate_limit

    @abstractmethod
    def _deliver(self, message: str) -> str: ...

    def send(self, message: str) -> str:
        if not self._check_rate_limit():
            return f"[{type(self).__name__}] Rate limit exceeded"
        self._send_count += 1
        return self._deliver(message)

class EmailChannel(NotificationChannel):
    def __init__(self, address: str):
        super().__init__(rate_limit=200)
        self.address = address
    def _deliver(self, msg): return f"[EMAIL → {self.address}] {msg}"

class SMSChannel(NotificationChannel):
    def __init__(self, phone: str):
        super().__init__(rate_limit=50)
        self.phone = phone
    def _deliver(self, msg): return f"[SMS → {self.phone}] {msg[:160]}"

class SlackChannel(NotificationChannel):
    def __init__(self, channel: str):
        super().__init__(rate_limit=500)
        self.channel = channel
    def _deliver(self, msg): return f"[SLACK #{self.channel}] {msg}"

class NotificationService:
    def __init__(self):
        self._channels: list[NotificationChannel] = []

    def add_channel(self, channel: NotificationChannel) -> "NotificationService":
        self._channels.append(channel)
        return self   # enables method chaining

    def send(self, message: str) -> list[str]:
        return [ch.send(message) for ch in self._channels]

service = (NotificationService()
    .add_channel(EmailChannel("alice@example.com"))
    .add_channel(SMSChannel("+1-555-0100"))
    .add_channel(SlackChannel("engineering")))

results = service.send("Deployment complete!")
for r in results:
    print(r)
```
</details>

---

### Q46 · Capstone — E-commerce order state machine

> 🛠️ **Solve locally:** [practice_local.py → Q46](./practice_local.py)
🟠 Advanced

Build an `Order` class that:
- Accepts items via `add_item(product_id, name, price, qty)` with method chaining
- Has a state machine: `PENDING → CONFIRMED → SHIPPED → DELIVERED`, cancellation from PENDING/CONFIRMED
- Computes `total` and `item_count` as properties
- Has an `audit_trail()` showing status transitions with timestamps

<details>
<summary>💡 Hint</summary>

Keep `_items` and `_history` as instance lists. Each `_transition()` call appends to `_history`. Properties sum over `_items`. Return `self` from `add_item()` for chaining.
</details>

<details>
<summary>✅ Answer</summary>

```python
import datetime
from dataclasses import dataclass

@dataclass
class OrderItem:
    name: str
    price: float
    qty: int

    @property
    def subtotal(self): return self.price * self.qty

class Order:
    TRANSITIONS = {
        "pending":   {"confirmed", "cancelled"},
        "confirmed": {"shipped", "cancelled"},
        "shipped":   {"delivered"},
        "delivered": set(),
        "cancelled": set(),
    }

    def __init__(self, customer_id: str):
        self.customer_id = customer_id
        self._items: list[OrderItem] = []
        self._status = "pending"
        self._history = [("pending", datetime.datetime.utcnow())]

    def add_item(self, name: str, price: float, qty: int) -> "Order":
        if self._status != "pending":
            raise ValueError(f"Cannot add items to a {self._status} order")
        self._items.append(OrderItem(name, price, qty))
        return self

    def _transition(self, new_status: str):
        if new_status not in self.TRANSITIONS.get(self._status, set()):
            raise ValueError(f"Invalid: {self._status} → {new_status}")
        self._status = new_status
        self._history.append((new_status, datetime.datetime.utcnow()))

    def confirm(self):  self._transition("confirmed")
    def ship(self):     self._transition("shipped")
    def deliver(self):  self._transition("delivered")
    def cancel(self):   self._transition("cancelled")

    @property
    def total(self): return sum(i.subtotal for i in self._items)
    @property
    def item_count(self): return sum(i.qty for i in self._items)

    def audit_trail(self):
        return "\n".join(f"  {ts.strftime('%H:%M:%S')} → {s}" for s, ts in self._history)

order = (Order("cust-42")
    .add_item("Laptop Stand", 29.99, 1)
    .add_item("USB Hub", 19.99, 2))

print(f"Total: ${order.total:.2f}, Items: {order.item_count}")
order.confirm()
order.ship()
order.deliver()
print(order.audit_trail())
```
</details>

---

### Q47 · Capstone — Data store ABC with multiple backends

> 🛠️ **Solve locally:** [practice_local.py → Q47](./practice_local.py)
🟠 Advanced

Extend the `DataStore` ABC from Q9 with two more methods:
- `get_many(keys: list)` — retrieve multiple keys (implement in ABC using `self.get()`)
- `set_many(pairs: dict)` — store multiple pairs (implement in ABC using `self.set()`)

Implement `InMemoryStore` and `FileStore` (dict-backed simulation). Show that both backends get `get_many` and `set_many` for free.

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class DataStore(ABC):
    @abstractmethod
    def get(self, key: str): ...

    @abstractmethod
    def set(self, key: str, value) -> None: ...

    @abstractmethod
    def delete(self, key: str) -> bool: ...

    # Concrete methods — all subclasses get these for free
    def get_many(self, keys: list) -> dict:
        return {k: self.get(k) for k in keys}

    def set_many(self, pairs: dict) -> None:
        for k, v in pairs.items():
            self.set(k, v)

    def get_or_default(self, key, default=None):
        return self.get(key) if self.get(key) is not None else default


class InMemoryStore(DataStore):
    def __init__(self): self._store = {}
    def get(self, key): return self._store.get(key)
    def set(self, key, value): self._store[key] = value
    def delete(self, key): return bool(self._store.pop(key, None))

store = InMemoryStore()
store.set_many({"user:1": "Alice", "user:2": "Bob", "user:3": "Carol"})
print(store.get_many(["user:1", "user:2", "user:99"]))
# {'user:1': 'Alice', 'user:2': 'Bob', 'user:99': None}
```
</details>

---

### Q48 · Debug — Fix the MRO diamond problem

> 🛠️ **Solve locally:** [practice_local.py → Q48](./practice_local.py)
🟠 Advanced

This code fails with a `TypeError`. Explain why and fix it:

```python
class Base:
    def __init__(self, value):
        self.value = value

class Left(Base):
    def __init__(self, value):
        Base.__init__(self, value)   # bug: should use super()
        self.left_attr = "left"

class Right(Base):
    def __init__(self, value):
        Base.__init__(self, value)   # bug: same
        self.right_attr = "right"

class Diamond(Left, Right):
    def __init__(self, value):
        Left.__init__(self, value)   # calls Base twice!
        Right.__init__(self, value)
```

<details>
<summary>💡 Hint</summary>

Direct `ClassName.__init__()` calls bypass MRO — `Base.__init__` gets called twice, which may cause bugs or in certain cases a `TypeError`. Use `super().__init__()` everywhere for cooperative inheritance.
</details>

<details>
<summary>✅ Answer</summary>

```python
# Problem: Base.__init__ called TWICE (once via Left, once via Right)
# Fix: use super() throughout — it follows MRO and calls each class once

class Base:
    def __init__(self, value):
        super().__init__()   # cooperative — passes to object
        self.value = value

class Left(Base):
    def __init__(self, value):
        super().__init__(value)   # follows MRO: Left → Right → Base → object
        self.left_attr = "left"

class Right(Base):
    def __init__(self, value):
        super().__init__(value)   # called by Left via MRO
        self.right_attr = "right"

class Diamond(Left, Right):
    def __init__(self, value):
        super().__init__(value)   # triggers the whole cooperative chain

d = Diamond(42)
print(d.value)       # 42
print(d.left_attr)   # left
print(d.right_attr)  # right
print([c.__name__ for c in Diamond.__mro__])
# ['Diamond', 'Left', 'Right', 'Base', 'object']
```

**Why:** With direct calls (`Base.__init__(self, value)`), `Base.__init__` runs twice. With `super()`, each class in the MRO runs exactly once — "cooperative multiple inheritance."
</details>

---

### Q49 · Real-world — Build a rate limiter class

> 🛠️ **Solve locally:** [practice_local.py → Q49](./practice_local.py)
🟠 Advanced

Implement a `RateLimiter` class:
- `__init__(self, max_calls: int, window_seconds: int)`
- `allow(self, user_id: str) -> bool` — returns `True` if the user is under the limit
- Each user gets their own call counter + window

```python
limiter = RateLimiter(max_calls=3, window_seconds=60)
print(limiter.allow("alice"))   # True
print(limiter.allow("alice"))   # True
print(limiter.allow("alice"))   # True
print(limiter.allow("alice"))   # False — limit reached
print(limiter.allow("bob"))     # True — separate counter
```

<details>
<summary>💡 Hint</summary>

Store per-user data in a dict: `{user_id: {"count": N, "reset_at": timestamp}}`. Check if the window has expired and reset if so. Then check count against limit.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time

class RateLimiter:
    def __init__(self, max_calls: int, window_seconds: int):
        self.max_calls = max_calls
        self.window = window_seconds
        self._users: dict[str, dict] = {}

    def allow(self, user_id: str) -> bool:
        now = time.time()
        if user_id not in self._users:
            self._users[user_id] = {"count": 0, "reset_at": now + self.window}

        user = self._users[user_id]

        # Reset window if expired
        if now > user["reset_at"]:
            user["count"] = 0
            user["reset_at"] = now + self.window

        if user["count"] >= self.max_calls:
            return False

        user["count"] += 1
        return True

limiter = RateLimiter(max_calls=3, window_seconds=60)
print(limiter.allow("alice"))   # True
print(limiter.allow("alice"))   # True
print(limiter.allow("alice"))   # True
print(limiter.allow("alice"))   # False
print(limiter.allow("bob"))     # True — separate counter
```
</details>

---

### Q50 · Mixed — Full OOP system in 30 lines

> 🛠️ **Solve locally:** [practice_local.py → Q50](./practice_local.py)
🟠 Advanced

Design and implement a minimal task management system in ≤30 lines using:
- A `Task` dataclass (id, title, status)
- A `TaskManager` class with `add()`, `complete()`, `pending()`, `__repr__`
- An enum for `TaskStatus`
- Method chaining where it makes sense

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class TaskStatus(Enum):
    PENDING   = "pending"
    DONE      = "done"
    CANCELLED = "cancelled"

@dataclass
class Task:
    id: int
    title: str
    status: TaskStatus = TaskStatus.PENDING

class TaskManager:
    def __init__(self):
        self._tasks: list[Task] = []
        self._next_id = 1

    def add(self, title: str) -> "TaskManager":
        self._tasks.append(Task(self._next_id, title))
        self._next_id += 1
        return self

    def complete(self, task_id: int) -> "TaskManager":
        for t in self._tasks:
            if t.id == task_id:
                t.status = TaskStatus.DONE
        return self

    def pending(self) -> list[Task]:
        return [t for t in self._tasks if t.status == TaskStatus.PENDING]

    def __repr__(self):
        return f"TaskManager({len(self._tasks)} tasks, {len(self.pending())} pending)"

manager = (TaskManager()
    .add("Write tests")
    .add("Review PR")
    .add("Deploy to staging"))

manager.complete(1)
print(manager)            # TaskManager(3 tasks, 2 pending)
print(manager.pending())  # [Task(id=2, ...), Task(id=3, ...)]
```
</details>

---

## Navigation

**[🏠 Back to README](./theory.md)**

**Related Topics:**
[01_why_oop.md](./01_why_oop.md) · [05_inheritance.md](./05_inheritance.md) · [08_dunder_methods.md](./08_dunder_methods.md) · [13_mro_and_super.md](./13_mro_and_super.md) · [14_dataclasses.md](./14_dataclasses.md) · [16_metaclasses.md](./16_metaclasses.md) · [17_descriptors.md](./17_descriptors.md) · [18_mixins.md](./18_mixins.md) · [19_solid_principles.md](./19_solid_principles.md)
