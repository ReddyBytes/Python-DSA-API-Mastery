<a id="top"></a>
# 🏗 Design Patterns in Python

> *"Design patterns are not rules. They are proven solutions to recurring problems.*
> *Good engineers know patterns. Great engineers know when to use them."*

## 📖 Table of Contents

- [1. Singleton Pattern](#1-singleton-pattern)
  - [Problem](#problem)
  - [Basic Implementation](#basic-implementation)
  - [Thread-Safe Singleton](#thread-safe-singleton)
  - [When to Use / When NOT to Use](#when-to-use--when-not-to-use)
- [2. Factory Pattern](#2-factory-pattern)
  - [Problem](#problem-1)
  - [Example](#example)
- [3. Strategy Pattern](#3-strategy-pattern)
  - [Problem](#problem-2)
  - [Structure](#structure)
- [4. Observer Pattern](#4-observer-pattern)
  - [Problem](#problem-3)
  - [Basic Structure](#basic-structure)
- [5. Dependency Injection (DI)](#5-dependency-injection-di)
  - [Problem](#problem-4)
  - [Better Approach](#better-approach)
- [6. Why Patterns Improve Architecture](#6-why-patterns-improve-architecture)
- [7. Real Production Examples](#7-real-production-examples)
  - [📂 Subfolder Deep Dives](#-subfolder-deep-dives)
  - [🔥 Summary](#-summary)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
Singleton · Factory (Factory Method) · Strategy · Observer · Decorator (structural)

**Should Learn** — Important for real projects, comes up regularly:
Repository · Dependency Injection · Command · Adapter · SOLID principles (all 5)

**Good to Know** — Useful in specific situations:
Builder · Composite · Facade · State · Template Method · Proxy

**Reference** — Know it exists, look up when needed:
Abstract Factory · Flyweight · Mediator · Memento · Visitor · Interpreter · CQRS · Event Sourcing

---

<a id="why-design-patterns-exist"></a>
## 🎬 Why Design Patterns Exist

Imagine you're building a house. Every time you reach a door, you don't invent a new way to hang it — you use hinges, the same solution that's worked for centuries. Design patterns are the hinges of software. They're not copy-paste code. They're **named solutions to recurring structural problems** that generations of engineers have already worked out. When you say "let's use a Strategy here," every engineer in the room immediately understands the shape of the solution.

Over time in large systems:
- Code becomes messy
- Classes depend on each other tightly
- Adding new features becomes risky
- Testing becomes hard
- Changing one thing breaks many things

Design patterns help you:
- Reduce duplication
- Improve flexibility and maintainability
- Scale systems cleanly
- Communicate design intent instantly across a team

---

<a id="1-singleton-pattern"></a>
# 1. Singleton Pattern

Think of a single printer in an office. Everyone in the building sends jobs to that one printer — you don't buy a new printer for each person who wants to print. A Singleton works the same way: no matter how many times you ask for the object, you always get back the exact same one. Useful for shared resources where having multiple copies would cause conflicts or waste.

<a id="problem"></a>
## Problem

You need only ONE instance of a class. Examples:
- Database connection pool
- Logger
- Configuration manager

You don't want multiple conflicting instances each holding separate state.

<a id="basic-implementation"></a>
## Basic Implementation

```python
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

a = Singleton()
b = Singleton()
print(a is b)   # True — same object every time
```

```
┌──────────────────── Singleton Flow ────────────────────────┐
│                                                             │
│  Singleton()                                                │
│      │                                                      │
│      ▼                                                      │
│  _instance is None?                                         │
│      ├── Yes → create new instance → store in _instance    │
│      └── No  → return existing _instance                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

<a id="thread-safe-singleton"></a>
## Thread-Safe Singleton

The basic version has a race condition: two threads can both pass the `is None` check simultaneously and both create an instance. Fix with a lock:

```python
import threading

class ThreadSafeSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:               # ← acquire lock before checking again
                if cls._instance is None: # ← double-checked locking pattern
                    cls._instance = super().__new__(cls)
        return cls._instance
```

**Simpler alternative — module-level singleton:**

```python
# config.py
class Config:
    def __init__(self):
        self.debug = False
        self.db_url = "postgresql://localhost/mydb"

# Module is only imported once — this IS a singleton:
config = Config()

# usage: from config import config
```

<a id="when-to-use--when-not-to-use"></a>
## When to Use / When NOT to Use

```
✅ USE SINGLETON for:             ❌ DON'T USE when:
──────────────────────────────    ────────────────────────────────────
Shared configuration object       Global state causes hidden coupling
Logging service                   Makes unit testing hard (can't mock)
DB connection pool manager        Multiple environments need diff instances
Hardware device interface         Concurrency creates deadlock risk
```

⚠️ **Common Mistake:** Using Singleton everywhere for "convenience." It's the most overused pattern. Singletons create hidden global state that makes code hard to test and reason about. Prefer dependency injection in most cases.

💡 **Hint:** In Python, the **module** is already a singleton — it's only initialized once. A module-level instance (`config = Config()`) is often all you need instead of implementing `__new__`.

📝 **Practice:** [Q86 · rate-limiter-scenario](../python_practice_questions_100.md#q86--design--rate-limiter-scenario)

> [↑ Back to Top](#top)

---

<a id="2-factory-pattern"></a>
# 2. Factory Pattern

Think of a staffing agency. You tell the agency "I need a Python developer" — you don't interview and hire them yourself. The agency handles the creation and returns someone who fits the role. A Factory works the same way: you ask for an object by type, and the factory handles the creation details. Your code never needs to know which specific class was instantiated.

📖 **Deep Dive:** [01_creational/theory.md](./01_creational/theory.md) — simple factory, factory method, registration pattern, abstract factory

<a id="problem-1"></a>
## Problem

You need to create objects but don't want to tightly couple object creation logic to business logic.

```python
# WITHOUT factory — tightly coupled:
if payment_type == "card":
    payment = CreditCardPayment()
elif payment_type == "paypal":
    payment = PayPalPayment()
elif payment_type == "crypto":
    payment = CryptoPayment()
# Adding a new payment type means editing this block everywhere it appears
```

<a id="example"></a>
## Example

```python
# WITH factory — creation logic in one place:
class PaymentFactory:
    @staticmethod
    def create(payment_type: str):
        if payment_type == "card":
            return CreditCardPayment()
        elif payment_type == "paypal":
            return PayPalPayment()
        elif payment_type == "crypto":
            return CryptoPayment()
        raise ValueError(f"Unknown payment type: {payment_type}")

# Usage — caller knows nothing about concrete classes:
payment = PaymentFactory.create("card")
payment.process(amount=99.99)
```

**Registration pattern (more extensible):**

```python
class PaymentFactory:
    _registry = {}

    @classmethod
    def register(cls, name):
        def decorator(payment_cls):
            cls._registry[name] = payment_cls
            return payment_cls
        return decorator

    @classmethod
    def create(cls, name, **kwargs):
        if name not in cls._registry:
            raise ValueError(f"Unknown payment type: {name}")
        return cls._registry[name](**kwargs)

@PaymentFactory.register("card")
class CreditCardPayment:
    def process(self, amount): ...

@PaymentFactory.register("paypal")
class PayPalPayment:
    def process(self, amount): ...

# Adding new types never requires touching existing code:
payment = PaymentFactory.create("card")
```

```
┌──────────────────── Factory Pattern Flow ──────────────────────────┐
│                                                                     │
│  Caller                  Factory                 Concrete Class    │
│    │                        │                         │            │
│    │── create("card") ──►   │                         │            │
│    │                        │── CreditCardPayment() ──►            │
│    │                        │◄── instance ────────────│            │
│    │◄── instance ───────────│                                       │
│    │                                                               │
│  Caller doesn't know WHICH class was created — just the interface  │
└─────────────────────────────────────────────────────────────────────┘
```

💡 **Hint:** The registration pattern is the "open/closed" version — open for extension (add new types by registering), closed for modification (existing factory code never changes).

📝 **Practice:** [Q70 · factory-pattern](../python_practice_questions_100.md#q70--normal--factory-pattern)

> [↑ Back to Top](#top)

---

<a id="3-strategy-pattern"></a>
# 3. Strategy Pattern

Think of a GPS navigation app. You can choose "fastest route," "shortest route," or "avoid highways" — the destination doesn't change, but the algorithm for getting there does. You swap strategies at runtime without changing the rest of the app. That's exactly what the Strategy pattern does: it wraps interchangeable algorithms in a common interface so they can be swapped without touching the caller.

📖 **Deep Dive:** [02_behavioral/theory.md](./02_behavioral/theory.md) — function-based strategy, registry, sort and payment examples, Command, Template Method

<a id="problem-2"></a>
## Problem

You have multiple algorithms and want to switch between them dynamically without if-else blocks scattered through your code.

```python
# WITHOUT strategy — hard to extend:
def sort_data(data, method):
    if method == "quick":
        return quicksort(data)
    elif method == "merge":
        return mergesort(data)
    elif method == "bubble":
        return bubblesort(data)
    # Adding new sort = editing this function
```

<a id="structure"></a>
## Structure

```python
# Class-based Strategy:
from abc import ABC, abstractmethod

class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: list) -> list: ...

class QuickSort(SortStrategy):
    def sort(self, data): return sorted(data)   # simplified

class MergeSort(SortStrategy):
    def sort(self, data): return sorted(data, key=lambda x: x)  # simplified

class Sorter:
    def __init__(self, strategy: SortStrategy):
        self.strategy = strategy

    def sort(self, data):
        return self.strategy.sort(data)

# Swap strategy at runtime:
sorter = Sorter(QuickSort())
sorter.sort([3, 1, 2])

sorter.strategy = MergeSort()   # ← change algorithm without changing Sorter
sorter.sort([3, 1, 2])
```

**Python-idiomatic: strategy as callable (simpler):**

```python
from typing import Callable

class PaymentProcessor:
    def __init__(self, strategy: Callable[[float], bool]):
        self._strategy = strategy

    def process(self, amount: float) -> bool:
        return self._strategy(amount)

def charge_card(amount: float) -> bool:
    print(f"Charging card: ${amount}")
    return True

def charge_paypal(amount: float) -> bool:
    print(f"Charging PayPal: ${amount}")
    return True

processor = PaymentProcessor(charge_card)
processor.process(99.99)

processor._strategy = charge_paypal   # swap strategy
processor.process(49.99)
```

💡 **Hint:** In Python, functions are first-class objects. For simple strategies (single method), just pass a callable — no need for a full class hierarchy. Use the class-based approach when strategies need their own state.

⚠️ **Common Mistake:** Using Strategy when a simple parameter would do. If you only ever have 2-3 fixed algorithms and they never change at runtime, a plain if-else is more readable. Strategy adds value when you have many algorithms or need runtime swapping.

📝 **Practice:** [Q100 · open-ended-system](../python_practice_questions_100.md#q100--critical--open-ended-system)

> [↑ Back to Top](#top)

---

<a id="4-observer-pattern"></a>
# 4. Observer Pattern

Think of a newspaper subscription. You subscribe once and the paper arrives at your door every morning — you don't call the publisher each day asking if there's news. The Observer pattern works the same way: objects (subscribers) register interest in an event source (publisher), and whenever something changes, the publisher notifies all subscribers automatically. No polling, no tight coupling.

📖 **Deep Dive:** [02_behavioral/theory.md](./02_behavioral/theory.md) — event bus, weak refs, Command, Template Method

<a id="problem-3"></a>
## Problem

You want objects to be notified automatically when something changes, without the publisher needing to know who its subscribers are.

Examples:
- Stock price updates → notify trading dashboards, alert systems, logs
- User action in UI → notify multiple widgets
- Database change → notify caches, search index, audit log

<a id="basic-structure"></a>
## Basic Structure

```python
from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, event: str, data) -> None: ...

class Subject:
    def __init__(self):
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self, event: str, data=None) -> None:
        for observer in self._observers:
            observer.update(event, data)

# Concrete subject:
class StockMarket(Subject):
    def __init__(self):
        super().__init__()
        self._prices = {}

    def update_price(self, symbol: str, price: float) -> None:
        self._prices[symbol] = price
        self.notify("price_update", {"symbol": symbol, "price": price})

# Concrete observers:
class TradingDashboard(Observer):
    def update(self, event, data):
        print(f"Dashboard: {data['symbol']} = ${data['price']}")

class AlertSystem(Observer):
    def __init__(self, threshold: float):
        self.threshold = threshold

    def update(self, event, data):
        if data["price"] > self.threshold:
            print(f"ALERT: {data['symbol']} exceeded ${self.threshold}!")

# Usage:
market = StockMarket()
market.attach(TradingDashboard())
market.attach(AlertSystem(threshold=200.0))

market.update_price("AAPL", 175.0)   # → Dashboard + no alert
market.update_price("AAPL", 210.0)   # → Dashboard + alert fires
```

```
┌──────────────── Observer Pattern Flow ──────────────────────────────┐
│                                                                      │
│  Subject (StockMarket)                                               │
│  ├── attach(dashboard)      ← register                              │
│  ├── attach(alert_system)   ← register                              │
│  │                                                                   │
│  └── update_price("AAPL", 210) ──► notify() ──► dashboard.update() │
│                                             └──► alert.update()     │
│                                                                      │
│  Subject knows nothing about concrete observer types — just the     │
│  Observer interface                                                  │
└──────────────────────────────────────────────────────────────────────┘
```

💡 **Hint:** Python's built-in event libraries (like `tkinter` events or `asyncio` event loops) are built on Observer. In production, you often reach for a message broker (Redis pub/sub, Kafka) instead of in-process Observer — same conceptual pattern, different infrastructure.

⚠️ **Common Mistake:** Keeping strong references to observers inside the subject. If an observer is "deleted," its reference in the subject's list keeps it alive. Use `weakref` for observers if their lifetime should be independent of the subject.

📝 **Practice:** [Q71 · observer-pattern](../python_practice_questions_100.md#q71--thinking--observer-pattern)

> [↑ Back to Top](#top)

---

<a id="5-dependency-injection-di"></a>
# 5. Dependency Injection (DI)

Think of a chef who either buys their own ingredients every time (tightly coupled) vs. a chef who receives pre-selected ingredients from a supplier (dependency injected). The second chef can cook the same recipe with different ingredients — fresh tomatoes today, canned tomorrow — without changing how they cook. Dependency Injection means a class receives the objects it needs from the outside, instead of creating them internally.

📖 **Deep Dive:** [03_dependency_injection/theory.md](./03_dependency_injection/theory.md) — constructor injection, service locator, testing with DI, Protocol-based injection

<a id="problem-4"></a>
## Problem

Class directly creates its dependencies — hard to test and impossible to swap:

```python
# TIGHTLY COUPLED — bad:
class OrderService:
    def __init__(self):
        self.db = PostgreSQLDatabase()    # ← creates dependency internally
        self.email = SMTPEmailService()   # ← hardcoded concrete class

# To test OrderService, you must have a real PostgreSQL DB running.
# You can't swap to an in-memory DB for tests.
```

<a id="better-approach"></a>
## Better Approach

Inject dependencies from the outside:

```python
# DEPENDENCY INJECTED — testable and flexible:
from typing import Protocol

class Database(Protocol):
    def query(self, sql: str) -> list: ...
    def execute(self, sql: str) -> None: ...

class EmailService(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...

class OrderService:
    def __init__(self, db: Database, email: EmailService):
        self.db = db          # ← injected, not created
        self.email = email    # ← injected, not created

    def place_order(self, user_id: int, items: list) -> None:
        self.db.execute(f"INSERT INTO orders ...")
        self.email.send(to=f"user_{user_id}@example.com",
                        subject="Order Confirmed", body="...")

# Production:
service = OrderService(
    db=PostgreSQLDatabase(url="postgresql://..."),
    email=SMTPEmailService(host="smtp.gmail.com"),
)

# Testing — swap to in-memory fakes, no real services needed:
class FakeDB:
    def query(self, sql): return []
    def execute(self, sql): pass

class FakeEmail:
    def __init__(self): self.sent = []
    def send(self, to, subject, body): self.sent.append((to, subject))

service = OrderService(db=FakeDB(), email=FakeEmail())
service.place_order(user_id=1, items=["widget"])
```

```
┌──────────────── DI vs Tight Coupling ──────────────────────────────┐
│                                                                     │
│  TIGHT COUPLING:                DEPENDENCY INJECTION:              │
│  ─────────────────              ─────────────────────              │
│  OrderService                   OrderService                       │
│  ├── creates PostgreSQLDB()     ├── receives db (any Database)     │
│  └── creates SMTPEmail()        └── receives email (any Email)     │
│                                                                     │
│  Hard to test                   Easy to test (swap with fakes)     │
│  Hard to swap DB                Easy to swap (new DI only)         │
│  Imports concrete class         Depends on Protocol/ABC only       │
└─────────────────────────────────────────────────────────────────────┘
```

💡 **Hint:** DI frameworks (like Python's `dependency-injector` or FastAPI's `Depends()`) automate the wiring. But the pattern itself needs no framework — constructor injection with Protocols is all you need in most cases.

⚠️ **Common Mistake:** Injecting everything, including utilities and primitives. DI is valuable for services that have side effects (DB, email, HTTP). Don't inject a `string_formatter` — that's over-engineering.

📝 **Practice:** [Q88 · retry-scenario](../python_practice_questions_100.md#q88--design--retry-scenario)

> [↑ Back to Top](#top)

---

<a id="6-why-patterns-improve-architecture"></a>
# 6. Why Patterns Improve Architecture

Every design pattern is a specific tool for reducing one type of structural problem. Together, they enforce the SOLID principles — the five rules that keep large codebases maintainable.

```
┌──────────────────── SOLID Principles ───────────────────────────────────┐
│                                                                          │
│  S — Single Responsibility   A class should have ONE reason to change   │
│  O — Open/Closed             Open for extension, closed for modification│
│  L — Liskov Substitution     Subclasses must be substitutable for base  │
│  I — Interface Segregation   Many small interfaces > one large one      │
│  D — Dependency Inversion    Depend on abstractions, not concretions    │
│                                                                          │
│  Pattern → SOLID principle it enforces:                                  │
│  ─────────────────────────────────────                                   │
│  Singleton    → S (centralizes shared state responsibility)              │
│  Factory      → O (extend by adding new types, don't modify factory)    │
│  Strategy     → O + D (open for new algos, depends on abstract strategy)│
│  Observer     → S + O (subject & observers each have 1 responsibility)  │
│  DI           → D (high-level modules depend on abstractions)           │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

Design patterns:
- Reduce tight coupling between classes
- Improve testability (swap implementations easily)
- Improve extensibility (add new behavior without editing existing code)
- Encourage clean abstractions and separation of concerns
- Make design intent readable at a glance ("we use Strategy here")

> [↑ Back to Top](#top)

---

<a id="7-real-production-examples"></a>
# 7. Real Production Examples

These patterns aren't academic — they appear in every major Python framework and library:

```
┌──────────────────────── Patterns in Production ──────────────────────────┐
│                                                                           │
│  Django ORM                                                               │
│  → Metaclasses + Factory-like model registry                             │
│  → Every Model subclass auto-registers via __init_subclass__             │
│                                                                           │
│  Python logging module                                                    │
│  → Logger is effectively a Singleton per name (logging.getLogger)        │
│  → Handlers are Observers (attached to logger, notified on log events)   │
│                                                                           │
│  Payment gateways (Stripe, PayPal integrations)                          │
│  → Strategy pattern: swap payment providers without changing app logic   │
│                                                                           │
│  Event systems (Django signals, asyncio events, Celery)                  │
│  → Observer pattern: sender notifies receivers, knows nothing about them │
│                                                                           │
│  FastAPI dependency system                                                │
│  → Dependency Injection via Depends() — wires services at request time  │
│  → Testable: swap DB/auth service with fakes in test client              │
│                                                                           │
│  pytest fixtures                                                          │
│  → DI pattern: test functions declare what they need, pytest wires it   │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

> [↑ Back to Top](#top)

---

<a id="-subfolder-deep-dives"></a>
## 📂 Subfolder Deep Dives

This theory file is an overview. Each subfolder contains a full deep-dive with advanced patterns, edge cases, and production examples:

| Subfolder | What's Inside |
|---|---|
| [01_creational/theory.md](./01_creational/theory.md) | **Creational patterns** — Simple Factory, Factory Method, Abstract Factory, Builder, registration pattern with decorators, when to use each |
| [02_behavioral/theory.md](./02_behavioral/theory.md) | **Behavioral patterns** — Strategy (function-based + class-based), Observer (event bus, weak refs), Command, Template Method, sort and payment examples |
| [03_dependency_injection/theory.md](./03_dependency_injection/theory.md) | **DI deep dive** — Constructor injection, property injection, service locator, Protocol-based injection, testing with DI, FastAPI Depends() pattern |

---

<a id="-summary"></a>
## 🔥 Summary

**Common mistakes:**
- Overusing patterns — forcing them unnecessarily makes code MORE complex, not less
- Copying patterns without understanding the problem they solve
- Not adapting to Python's dynamic nature (functions are first-class — often simpler than a full Strategy class hierarchy)
- Singleton everywhere for "convenience" — it creates hidden global state

**Engineering maturity levels:**
```
Beginner   → Writes working code
Intermediate → Understands basic patterns
Advanced   → Applies patterns appropriately
Senior     → Designs scalable architecture using patterns wisely
Architect  → Knows WHEN NOT to use patterns
```

**When to reach for each pattern:**
```
┌─────────────────────────────────────────────────────────────────────┐
│  PATTERN      WHEN TO USE IT                                        │
│  ──────────── ───────────────────────────────────────────────────── │
│  Singleton    One shared resource (config, logger, connection pool) │
│  Factory      Object creation logic needs to be centralized         │
│  Strategy     Multiple interchangeable algorithms, runtime swapping │
│  Observer     One event → multiple independent reactions            │
│  DI           Class needs services it shouldn't create itself       │
│                                                                     │
│  DEFAULT: don't use a pattern until the problem it solves appears.  │
│  Patterns emerge from real pain — don't impose them upfront.        │
└─────────────────────────────────────────────────────────────────────┘
```

---

<a id="-navigation"></a>
## 🔁 Navigation

**This folder:**
[theory.md](./theory.md) · [cheetsheet.md](./cheetsheet.md) · [interview.md](./interview.md) · [practice.md](./practice.md)

**Subfolders:**
[01_creational/theory.md](./01_creational/theory.md) · [02_behavioral/theory.md](./02_behavioral/theory.md) · [03_dependency_injection/theory.md](./03_dependency_injection/theory.md)

**Related modules:**
[15 — Advanced Python (metaclasses, descriptors)](../15_advanced_python/theory.md) · [05 — OOP (inheritance, SOLID)](../05_oops/theory.md) · [17 — Testing (mock/DI patterns)](../17_testing/theory.md)

**Jump to specific topics:**
[Singleton](#1-singleton-pattern) · [Thread-Safe Singleton](#thread-safe-singleton) · [Factory Registration Pattern](#example) · [Strategy as Callable](#structure) · [DI with Protocol](#better-approach) · [SOLID Principles](#6-why-patterns-improve-architecture)

---

| | |
|---|---|
| ⬅ Prev Module | [15 — Advanced Python](../15_advanced_python/theory.md) |
| ➡ Next Module | [17 — Testing](../17_testing/theory.md) |

**[🏠 Back to README](../../README.md)**
