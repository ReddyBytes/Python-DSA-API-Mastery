# ⚡ Design Patterns — Cheetsheet

> Quick reference: pattern categories, Python implementations, when-to-use, ASCII structure diagrams, common mistakes.

---

## 🗂️ Pattern Category Table

| Category | Purpose | Patterns |
|---|---|---|
| **Creational** | Control object creation | Singleton, Factory, Builder, Prototype |
| **Structural** | Compose objects/classes | Decorator, Adapter, Facade, Proxy, Composite |
| **Behavioral** | Manage object communication | Strategy, Observer, Command, Iterator, State |

---

## 🔒 Singleton — One Instance Only

```python
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

a = Singleton()
b = Singleton()
assert a is b    # True — same object
```

```
┌─────────────────────┐
│  Singleton          │
│─────────────────────│
│ _instance = None    │
│─────────────────────│
│ __new__(cls)        │  ← returns existing or creates one
└─────────────────────┘
```

| Use when | Avoid when |
|---|---|
| Shared config, logger, DB connection pool | State isolation needed, testing with mocks |

---

## 🏭 Factory — Centralized Object Creation

```python
class PaymentFactory:
    @staticmethod
    def create(payment_type: str):
        if payment_type == "card":
            return CreditCardPayment()
        elif payment_type == "paypal":
            return PayPalPayment()
        raise ValueError(f"Unknown type: {payment_type}")

# Client never imports concrete classes
payment = PaymentFactory.create("card")
payment.process(100)
```

```
Client ──► PaymentFactory.create("card")
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
  CreditCardPayment     PayPalPayment
```

| Use when | Avoid when |
|---|---|
| Object creation logic is complex or varies, multiple concrete types | Only one type ever, trivial `__init__` |

---

## 👀 Observer — Event Notification

```python
class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self, event):
        for obs in self._observers:
            obs.update(event)

class EmailAlert:
    def update(self, event):
        print(f"Email: {event}")

subject = Subject()
subject.attach(EmailAlert())
subject.notify("price_changed")   # notifies all subscribers
```

```
Subject ──notify()──► Observer1.update()
                  ├──► Observer2.update()
                  └──► Observer3.update()
```

| Use when | Avoid when |
|---|---|
| Event systems, UI frameworks, pub/sub messaging | Observer count is large and order matters critically |

---

## 🎯 Strategy — Swappable Algorithms

```python
from abc import ABC, abstractmethod

class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: list) -> list: ...

class QuickSort(SortStrategy):
    def sort(self, data):
        return sorted(data)          # simplified

class BubbleSort(SortStrategy):
    def sort(self, data):
        data = data[:]
        for i in range(len(data)):
            for j in range(len(data)-i-1):
                if data[j] > data[j+1]:
                    data[j], data[j+1] = data[j+1], data[j]
        return data

class Sorter:
    def __init__(self, strategy: SortStrategy):
        self.strategy = strategy

    def run(self, data):
        return self.strategy.sort(data)

s = Sorter(QuickSort())
s.strategy = BubbleSort()          # swap at runtime
```

```
Context ──► strategy.execute()
            ┌────────────────┐
            │  <<Strategy>>  │
            └───────┬────────┘
           ┌────────┴────────┐
    ConcreteA          ConcreteB
```

| Use when | Avoid when |
|---|---|
| Multiple algorithms for same task, behavior switchable at runtime | Only one algorithm ever used |

---

## 🎨 Decorator (Structural) — Wrap Behavior

```python
from abc import ABC, abstractmethod

class Notifier(ABC):
    @abstractmethod
    def send(self, msg): ...

class EmailNotifier(Notifier):
    def send(self, msg):
        print(f"Email: {msg}")

class SMSDecorator(Notifier):
    def __init__(self, wrapped: Notifier):
        self._wrapped = wrapped

    def send(self, msg):
        self._wrapped.send(msg)       # delegate
        print(f"SMS: {msg}")          # add behavior

n = SMSDecorator(EmailNotifier())
n.send("Alert!")    # Email + SMS
```

Note: this is the structural Decorator pattern — distinct from Python's `@decorator` syntax.

---

## 📋 Command — Encapsulate Actions

```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self): ...
    @abstractmethod
    def undo(self): ...

class AddItemCommand(Command):
    def __init__(self, cart, item):
        self.cart = cart
        self.item = item

    def execute(self):
        self.cart.append(self.item)

    def undo(self):
        self.cart.remove(self.item)

history = []
cart = []
cmd = AddItemCommand(cart, "apple")
cmd.execute();  history.append(cmd)
history.pop().undo()    # undo last action
```

```
Invoker ──execute()──► Command.execute()
                               │
                       Receiver.action()
```

| Use when | Avoid when |
|---|---|
| Undo/redo, queued operations, macro recording | Simple one-off calls with no undo requirement |

---

## 🔄 Iterator — Traverse Without Exposing Structure

```python
class NumberRange:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __iter__(self):
        current = self.start
        while current <= self.end:
            yield current
            current += 1

for n in NumberRange(1, 5):
    print(n)    # 1 2 3 4 5
```

Built-in: any class with `__iter__` + `__next__` is an iterator. Prefer generators.

---

## 💉 Dependency Injection — Inject, Don't Create

```python
# Bad — tightly coupled
class Service:
    def __init__(self):
        self.db = PostgresDB()      # hard to mock

# Good — inject dependency
class Service:
    def __init__(self, db):         # pass in from outside
        self.db = db

# Test
service = Service(db=MockDB())      # easily mockable
# Production
service = Service(db=PostgresDB())
```

---

## 📌 Learning Priority

**Must Learn** — interview essential, daily use:
Singleton · Factory · Strategy · Observer · Dependency Injection

**Should Learn** — real projects, comes up regularly:
Decorator (structural) · Command · Adapter · Repository

**Good to Know** — specific situations:
Builder · Facade · State · Template Method · Proxy

**Reference** — know it exists:
Abstract Factory · Flyweight · Mediator · Visitor · CQRS

---

## ⚠️ Common Mistakes

```
1. Overusing Singleton → global state, hard to test
   Fix: prefer DI; use Singleton only for truly shared resources

2. Confusing structural Decorator with Python @decorator syntax
   Fix: structural Decorator wraps object, not function

3. Forcing patterns on simple code
   Fix: patterns are for when complexity demands them

4. Ignoring SOLID — especially Open/Closed
   Fix: Strategy + Factory = extend without modifying

5. Tight coupling in Strategy — context knows concrete type
   Fix: always program to an interface/ABC

6. Observer memory leaks — never detaching observers
   Fix: always provide detach() and call it on cleanup
```

---

## 🔥 Rapid-Fire

```
Q: Creational vs Behavioral?
A: Creational = how objects are made. Behavioral = how they communicate.

Q: Singleton thread-safety in Python?
A: CPython GIL helps, but use threading.Lock for certainty.

Q: Strategy vs State?
A: Strategy = client chooses algorithm. State = object changes behavior based on internal state.

Q: When does Observer cause coupling?
A: When observers know too much about the subject — keep update() generic.

Q: DI vs Service Locator?
A: DI = dependencies pushed in. Service Locator = dependencies pulled via lookup (harder to test).
```

---

## 🧭 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 💉 Dependency Injection | [dependency_injection.md](./dependency_injection.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| ⬅️ Previous | [15 — Advanced Python](../15_advanced_python/cheatsheet.md) |
| ➡️ Next | [17 — Testing](../17_testing/cheatsheet.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Advanced Python](../15_advanced_python/cheatsheet.md) &nbsp;|&nbsp; **Next:** [Testing →](../17_testing/cheatsheet.md)

**Related Topics:** [Theory](./theory.md) · [Dependency Injection](./dependency_injection.md) · [Interview Q&A](./interview.md)
