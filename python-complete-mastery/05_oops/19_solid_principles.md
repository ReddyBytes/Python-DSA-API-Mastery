# 🏛️ 19 — SOLID Principles: Architecture Rules with Python

> *"SOLID is not a rulebook — it's a compass.*
> *It doesn't tell you exactly what to build.*
> *It tells you which direction leads to code that doesn't rot."*

---

## 🎬 The Story

Six months after launch, your codebase is in pain:
- Adding a new payment method breaks the existing ones
- A tiny bug fix requires changing 8 files
- A new developer is afraid to touch anything
- Tests are fragile — one change, 50 test failures

This is **software rot** — and it happens to every system that grows without design principles.

SOLID is the set of 5 principles that, when followed, prevent this rot.
They were defined by Robert C. Martin ("Uncle Bob") and are considered the foundation of good OOP design.

---

## 🔑 The 5 SOLID Principles — Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│  S — Single Responsibility  Each class does ONE thing                   │
│  O — Open/Closed            Open to extension, closed to modification   │
│  L — Liskov Substitution    Subclasses can replace parent anywhere      │
│  I — Interface Segregation  Don't force classes to implement unused API │
│  D — Dependency Inversion   Depend on abstractions, not concrete impl.  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🅢 S — Single Responsibility Principle (SRP)

> **"A class should have only one reason to change."**

A class that does too many things will break for too many reasons.

### ❌ Violation — One Class Does Everything

```python
class User:
    def __init__(self, name, email):
        self.name  = name
        self.email = email

    def get_user_data(self):
        return {"name": self.name, "email": self.email}

    def save_to_db(self):
        # Reason to change: database structure changes
        print(f"INSERT INTO users VALUES ('{self.name}', '{self.email}')")

    def send_welcome_email(self):
        # Reason to change: email template changes, SMTP provider changes
        print(f"Sending welcome email to {self.email}")

    def validate_email(self):
        # Reason to change: validation rules change
        return "@" in self.email and "." in self.email

    def generate_report(self):
        # Reason to change: report format changes
        return f"User Report: {self.name} ({self.email})"
```

**Problem:** This class has 5 different reasons to change. A database migration shouldn't affect email sending. An email template change shouldn't affect validation logic.

---

### ✅ Fixed — Each Class Has One Job

```python
class User:
    """Represents user data. That's ALL it does."""
    def __init__(self, name, email):
        self.name  = name
        self.email = email


class UserRepository:
    """Handles database persistence for users."""

    def save(self, user: User):
        print(f"INSERT INTO users VALUES ('{user.name}', '{user.email}')")

    def find_by_email(self, email: str) -> User:
        # query database and return User
        pass


class EmailValidator:
    """Validates email addresses."""

    def is_valid(self, email: str) -> bool:
        return "@" in email and "." in email


class EmailService:
    """Sends emails to users."""

    def send_welcome(self, user: User):
        print(f"Sending welcome email to {user.email}")


class UserReportGenerator:
    """Generates user reports."""

    def generate(self, user: User) -> str:
        return f"User Report: {user.name} ({user.email})"
```

Now:
- Adding a new email provider? Edit `EmailService` only.
- Changing the DB schema? Edit `UserRepository` only.
- New report format? Edit `UserReportGenerator` only.

---

### 🧠 How to Recognize SRP Violation

```
Ask these questions about your class:
  ✗  "This class handles ___ AND ___"  (two responsibilities = violation)
  ✗  "I need to change this because the DB changed AND the email template changed"
  ✓  "This class has exactly one job: ___"
  ✓  "I only need to change this class when ___ changes"
```

---

## 🅞 O — Open/Closed Principle (OCP)

> **"Software entities should be open for extension, but closed for modification."**

You should be able to add new behaviour **without editing existing code.**

### ❌ Violation — Modifying Code To Add Features

```python
class DiscountCalculator:
    def calculate(self, order, customer_type):
        if customer_type == "regular":
            return order.total * 0.0

        elif customer_type == "vip":
            return order.total * 0.1

        elif customer_type == "employee":
            return order.total * 0.3

        # EVERY TIME a new customer type is added,
        # you must MODIFY this class.
        # This breaks existing tests, risks regressions.
```

---

### ✅ Fixed — Extend Without Modifying

```python
from abc import ABC, abstractmethod


class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, total: float) -> float:
        ...


class NoDiscount(DiscountStrategy):
    def calculate(self, total: float) -> float:
        return 0.0


class VIPDiscount(DiscountStrategy):
    def calculate(self, total: float) -> float:
        return total * 0.1


class EmployeeDiscount(DiscountStrategy):
    def calculate(self, total: float) -> float:
        return total * 0.3


# New customer type? Add a new class — don't touch anything existing!
class BlackFridayDiscount(DiscountStrategy):
    def calculate(self, total: float) -> float:
        return total * 0.5


class Order:
    def __init__(self, total: float, discount: DiscountStrategy):
        self.total    = total
        self.discount = discount

    def final_price(self):
        return self.total - self.discount.calculate(self.total)


# Usage:
order1 = Order(10000, VIPDiscount())
order2 = Order(10000, BlackFridayDiscount())

print(order1.final_price())    # 9000.0
print(order2.final_price())    # 5000.0

# Adding "StudentDiscount" tomorrow?
# → Just create a new class. Zero existing code changes.
```

---

### 🧠 OCP In Practice

```
CLOSED for modification:  existing classes rarely touched after they work
OPEN for extension:       new behavior added through new subclasses/modules

This is why:
  • Strategy pattern (like above) is everywhere
  • Django's form fields are extensible without editing core code
  • pytest plugins don't require modifying pytest itself
```

---

## 🅛 L — Liskov Substitution Principle (LSP)

> **"If S is a subtype of T, then objects of type T can be replaced by objects of type S without altering the correctness of the program."**

In plain English: **A subclass should be fully usable wherever the parent class is used.**

### ❌ Violation — Subclass Breaks Parent Contract

```python
class Rectangle:
    def set_width(self, w):
        self.width = w

    def set_height(self, h):
        self.height = h

    def area(self):
        return self.width * self.height


class Square(Rectangle):
    # Square has equal sides — so setting width also sets height
    def set_width(self, w):
        self.width  = w
        self.height = w   # ← violates Rectangle's contract!

    def set_height(self, h):
        self.width  = h   # ← violates Rectangle's contract!
        self.height = h


def test_rectangle(rect: Rectangle):
    rect.set_width(5)
    rect.set_height(10)
    assert rect.area() == 50   # 5 × 10 = 50


r = Rectangle()
test_rectangle(r)    # ✓ passes

s = Square()
test_rectangle(s)    # ✗ FAILS! area = 100 (10×10), not 50
# Square is NOT safely substitutable for Rectangle
```

**The Problem:** Square IS-A Rectangle mathematically, but NOT in software terms because it changes the expected behaviour of `set_width` and `set_height`.

---

### ✅ Fixed — Separate the Hierarchy

```python
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width  = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height


class Square(Shape):
    def __init__(self, side: float):
        self.side = side

    def area(self) -> float:
        return self.side ** 2


def print_area(shape: Shape):
    print(f"Area: {shape.area()}")


# Both safely substitutable for Shape:
print_area(Rectangle(5, 10))    # Area: 50
print_area(Square(7))           # Area: 49
```

---

### 🧠 LSP Quick Checklist

```
Your subclass violates LSP if:
  ✗  It raises exceptions that the parent doesn't raise
  ✗  It ignores a parameter that the parent uses
  ✗  It returns a different type than the parent declares
  ✗  It has stronger preconditions (more restrictive inputs)
  ✗  It has weaker postconditions (weaker output guarantees)
  ✗  It changes the meaning of inherited methods

Your subclass follows LSP if:
  ✓  You can pass it to any function expecting the parent — without changes
  ✓  All parent method contracts are preserved or strengthened
```

---

## 🅘 I — Interface Segregation Principle (ISP)

> **"No client should be forced to depend on methods it does not use."**

Don't create fat interfaces that force implementors to add irrelevant methods.

### ❌ Violation — Fat Interface

```python
from abc import ABC, abstractmethod


class Worker(ABC):
    @abstractmethod
    def work(self): ...

    @abstractmethod
    def eat(self): ...

    @abstractmethod
    def sleep(self): ...


class HumanWorker(Worker):
    def work(self):  print("Human working")
    def eat(self):   print("Human eating")
    def sleep(self): print("Human sleeping")


class RobotWorker(Worker):
    def work(self):  print("Robot working")

    def eat(self):
        raise NotImplementedError("Robots don't eat!")   # ← FORCED to implement!

    def sleep(self):
        raise NotImplementedError("Robots don't sleep!")  # ← FORCED to implement!
```

**Problem:** `RobotWorker` is forced to implement methods that make no sense for it. This is ISP violation.

---

### ✅ Fixed — Segregated Interfaces

```python
from abc import ABC, abstractmethod


class Workable(ABC):
    @abstractmethod
    def work(self): ...


class Eatable(ABC):
    @abstractmethod
    def eat(self): ...


class Sleepable(ABC):
    @abstractmethod
    def sleep(self): ...


# Human needs all three:
class HumanWorker(Workable, Eatable, Sleepable):
    def work(self):  print("Human working")
    def eat(self):   print("Human eating")
    def sleep(self): print("Human sleeping")


# Robot only needs work:
class RobotWorker(Workable):
    def work(self):  print("Robot working")


# A function that only needs workers — accepts both:
def run_shift(worker: Workable):
    worker.work()


run_shift(HumanWorker())    # Human working
run_shift(RobotWorker())    # Robot working
```

---

### 🧠 ISP in Python — Using Protocols (Python 3.8+)

Python's `Protocol` class (structural subtyping / duck typing) is the modern Pythonic way to handle ISP:

```python
from typing import Protocol


class Serializable(Protocol):
    def to_json(self) -> str: ...


class Persistable(Protocol):
    def save(self) -> None: ...
    def load(self, id: int) -> None: ...


# A function only cares about serialization:
def export(item: Serializable) -> str:
    return item.to_json()


# No inheritance needed — any class with to_json() satisfies the protocol:
class User:
    def __init__(self, name): self.name = name
    def to_json(self): import json; return json.dumps({"name": self.name})

class Order:
    def __init__(self, total): self.total = total
    def to_json(self): import json; return json.dumps({"total": self.total})


# Both work — no forced inheritance:
print(export(User("Alice")))    # {"name": "Alice"}
print(export(Order(5000)))      # {"total": 5000}
```

---

## 🅓 D — Dependency Inversion Principle (DIP)

> **"High-level modules should not depend on low-level modules.**
> **Both should depend on abstractions.**
> **Abstractions should not depend on details.**
> **Details should depend on abstractions."**

In plain English: **Depend on interfaces, not concrete implementations.**

### ❌ Violation — High-Level Code Hardwired to Low-Level

```python
class MySQLDatabase:
    def query(self, sql):
        print(f"MySQL executing: {sql}")
        return []


class UserService:
    def __init__(self):
        # ← Directly creates a concrete class!
        # UserService is TIGHTLY COUPLED to MySQLDatabase.
        # Want to switch to PostgreSQL? Edit UserService.
        # Want to test with a mock? Impossible without patching.
        self.db = MySQLDatabase()

    def get_user(self, user_id):
        return self.db.query(f"SELECT * FROM users WHERE id={user_id}")
```

---

### ✅ Fixed — Depend On Abstractions

```python
from abc import ABC, abstractmethod


# The ABSTRACTION (interface):
class Database(ABC):
    @abstractmethod
    def query(self, sql: str) -> list: ...

    @abstractmethod
    def execute(self, sql: str) -> None: ...


# Low-level modules implement the abstraction:
class MySQLDatabase(Database):
    def query(self, sql: str) -> list:
        print(f"MySQL: {sql}")
        return []

    def execute(self, sql: str) -> None:
        print(f"MySQL execute: {sql}")


class PostgreSQLDatabase(Database):
    def query(self, sql: str) -> list:
        print(f"PostgreSQL: {sql}")
        return []

    def execute(self, sql: str) -> None:
        print(f"PostgreSQL execute: {sql}")


class MockDatabase(Database):
    """For testing — no real database needed."""
    def __init__(self):
        self._data = {}

    def query(self, sql: str) -> list:
        return list(self._data.values())

    def execute(self, sql: str) -> None:
        pass


# High-level module depends on ABSTRACTION, not concrete:
class UserService:
    def __init__(self, db: Database):   # ← injected from outside
        self.db = db

    def get_user(self, user_id):
        return self.db.query(f"SELECT * FROM users WHERE id={user_id}")

    def create_user(self, name, email):
        self.db.execute(f"INSERT INTO users VALUES ('{name}', '{email}')")


# Production: inject real DB
service_prod = UserService(MySQLDatabase())
service_prod.get_user(1)    # MySQL: SELECT * FROM users WHERE id=1

# Switching DB: no changes to UserService!
service_pg = UserService(PostgreSQLDatabase())
service_pg.get_user(1)      # PostgreSQL: SELECT * FROM users WHERE id=1

# Testing: inject mock
service_test = UserService(MockDatabase())
service_test.get_user(1)    # → [] (no I/O, no database needed!)
```

---

### 🧠 DIP Is The Foundation of Testability

```
WITHOUT DIP:
  UserService creates its own MySQLDatabase
  → Tests hit the real database
  → Tests are slow, fragile, require DB setup
  → No isolation

WITH DIP (Dependency Injection):
  Database is injected from outside
  → Tests inject MockDatabase
  → Tests are fast, isolated, no external dependencies
  → Easy to swap implementations later
```

---

## 🔁 All 5 Together — A Real Example

```python
# Putting it all together: a payment processing system
from abc import ABC, abstractmethod
from typing import Protocol


# ── Abstractions (D) ──────────────────────────────────────

class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount: float, token: str) -> bool: ...


class NotificationService(Protocol):
    def notify(self, message: str) -> None: ...


# ── Payment strategies (O + S) ─────────────────────────────

class StripeGateway(PaymentGateway):
    def charge(self, amount: float, token: str) -> bool:
        print(f"Stripe charging {amount} with token {token}")
        return True


class PayPalGateway(PaymentGateway):
    def charge(self, amount: float, token: str) -> bool:
        print(f"PayPal charging {amount} with token {token}")
        return True


# Add new gateway without touching anything above ↑
class RazorpayGateway(PaymentGateway):
    def charge(self, amount: float, token: str) -> bool:
        print(f"Razorpay charging {amount} with token {token}")
        return True


# ── Small, focused notification classes (I) ────────────────

class EmailNotifier:
    def notify(self, message: str) -> None:
        print(f"EMAIL: {message}")


class SMSNotifier:
    def notify(self, message: str) -> None:
        print(f"SMS: {message}")


# ── Order — single responsibility (S) ──────────────────────

class Order:
    def __init__(self, order_id: str, amount: float):
        self.order_id = order_id
        self.amount   = amount
        self.paid     = False


# ── Payment processor — depends on abstractions (D) ────────

class PaymentProcessor:
    """
    Single job: process payments.  (S)
    Open to new gateways/notifiers.  (O)
    Works with any PaymentGateway subclass.  (L)
    Only needs gateway + notifier, nothing else.  (I)
    Depends on abstractions, not MySQL/Stripe/etc.  (D)
    """
    def __init__(self, gateway: PaymentGateway, notifier: NotificationService):
        self.gateway  = gateway
        self.notifier = notifier

    def process(self, order: Order, token: str) -> bool:
        success = self.gateway.charge(order.amount, token)
        if success:
            order.paid = True
            self.notifier.notify(f"Payment of ₹{order.amount} for {order.order_id} successful")
        else:
            self.notifier.notify(f"Payment FAILED for {order.order_id}")
        return success


# ── Wire it up (Dependency Injection) ──────────────────────

stripe_processor = PaymentProcessor(
    gateway=StripeGateway(),
    notifier=EmailNotifier()
)

razorpay_processor = PaymentProcessor(
    gateway=RazorpayGateway(),
    notifier=SMSNotifier()
)

order = Order("ORD-001", 4999.0)
stripe_processor.process(order, "tok_abc123")
# Stripe charging 4999.0 with token tok_abc123
# EMAIL: Payment of ₹4999.0 for ORD-001 successful
```

---

## 📊 SOLID Violation Symptoms

```
┌─────────┬──────────────────────────────────────────────────────────────┐
│ Princ.  │  Symptom of Violation                                        │
├─────────┼──────────────────────────────────────────────────────────────┤
│  S      │  "This class does X, Y, Z, AND sends emails AND saves to DB" │
│         │  Class has more than ~200-300 lines                           │
│         │  Multiple unrelated reasons to change                        │
├─────────┼──────────────────────────────────────────────────────────────┤
│  O      │  Giant if/elif chains checking type                          │
│         │  Adding a feature requires modifying existing files          │
│         │  "Just add an elif here for the new type"                    │
├─────────┼──────────────────────────────────────────────────────────────┤
│  L      │  Subclass raises NotImplementedError for inherited methods   │
│         │  Functions check isinstance() before calling methods         │
│         │  Subclass overrides method to do something completely diff.  │
├─────────┼──────────────────────────────────────────────────────────────┤
│  I      │  Abstract method implementations that just say "pass" or     │
│         │  raise NotImplementedError                                   │
│         │  "I don't need this method but the interface forces me"      │
├─────────┼──────────────────────────────────────────────────────────────┤
│  D      │  Class creates its own dependencies with MySQLDatabase()      │
│         │  Impossible to test without a real database/API/file         │
│         │  Changing a low-level class requires changing high-level     │
└─────────┴──────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Takeaways

```
S — Single Responsibility
  • One class = one reason to change
  • If you say "and" describing a class, split it

O — Open/Closed
  • Add features with new code, not by editing old code
  • Use Strategy, Decorator, or subclassing to extend

L — Liskov Substitution
  • Subclass must be fully usable wherever parent is expected
  • Don't raise unexpected exceptions or ignore parent contracts
  • If subclass breaks parent assumptions, rethink the hierarchy

I — Interface Segregation
  • Don't force classes to implement methods they don't need
  • Many small, focused interfaces > one fat interface
  • Python's Protocol enables structural typing without forced inheritance

D — Dependency Inversion
  • High-level code should not create its own dependencies
  • Inject dependencies from outside (Dependency Injection)
  • Depend on abstractions (ABC, Protocol), not concrete classes
  • Result: code is testable, swappable, maintainable

OVERALL:
  SOLID doesn't mean 5 tiny classes for everything.
  It means: design so the system can GROW without BREAKING.
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [18 — Mixins](./18_mixins.md) |
| 📖 Index | [README.md](./README.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Mixins](./18_mixins.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Why Oop](./01_why_oop.md) · [Classes And Objects](./02_classes_and_objects.md) · [Init And Self](./03_init_and_self.md) · [Encapsulation](./04_encapsulation.md) · [Inheritance](./05_inheritance.md) · [Polymorphism](./06_polymorphism.md) · [Abstraction](./07_abstraction.md) · [Dunder Methods](./08_dunder_methods.md) · [Class Instance Static Methods](./09_class_instance_static_methods.md) · [Class Vs Instance Variables](./10_class_vs_instance_variables.md) · [Properties](./11_properties.md) · [Theory Part 1](./theory_part1.md) · [Composition Vs Inheritance](./12_composition_vs_inheritance.md) · [Theory Part 2](./theory_part2.md) · [Mro And Super](./13_mro_and_super.md) · [Theory Part 3](./theory_part3.md) · [Dataclasses](./14_dataclasses.md) · [Slots](./15_slots.md) · [Metaclasses](./16_metaclasses.md) · [Descriptors](./17_descriptors.md) · [Mixins](./18_mixins.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
