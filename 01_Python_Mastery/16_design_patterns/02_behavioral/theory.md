# Behavioral Patterns — Observer, Strategy, Command, Template Method

A newspaper publishes once and everyone who subscribed gets it. A GPS navigates you to the same destination via different routes depending on your preference. Behavioral patterns define **how objects communicate and distribute responsibility** at runtime.

---

## 📌 Learning Priority

**Must Learn:** Observer (callback lists) · Strategy (function-based) · Command (execute/undo)

**Should Learn:** Template method · Weak references in Observer

**Good to Know:** Mediator · Chain of responsibility

**Reference:** Python's `functools.singledispatch` as Strategy variant

---

## 1. Observer Pattern

Think of a newspaper subscription service. The publisher prints one edition and sends it to every subscriber. Subscribers can join or cancel at any time. The publisher does not track what each subscriber does with the news — it just delivers it. **Observer** decouples publishers from the code that reacts to their events.

### 1.1 Basic Event System (Callback Lists)

```python
from collections import defaultdict
from typing import Callable, Any

class EventBus:
    def __init__(self):
        self._handlers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, handler: Callable) -> None:
        self._handlers[event].append(handler)

    def unsubscribe(self, event: str, handler: Callable) -> None:
        self._handlers[event].remove(handler)

    def emit(self, event: str, **kwargs) -> None:
        for handler in self._handlers.get(event, []):
            handler(**kwargs)           # ← each subscriber called in turn

    def on(self, *events: str):
        """Decorator: @bus.on("user.created")"""
        def decorator(func: Callable) -> Callable:
            for event in events:
                self.subscribe(event, func)
            return func
        return decorator
```

```python
bus = EventBus()

@bus.on("user.created")
def send_welcome_email(user_id: int, email: str, **_):
    print(f"Sending welcome to {email}")

@bus.on("user.created")
def create_default_settings(user_id: int, **_):
    print(f"Creating defaults for user {user_id}")

bus.emit("user.created", user_id=42, email="alice@example.com")
# Both handlers are called — publisher emits once
```

### 1.2 Classic Observer with ABC

For tighter contracts, define an `Observer` interface that all observers implement.

```python
from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, event: str, data: Any) -> None: ...

class Subject:
    def __init__(self):
        self._observers: list[Observer] = []

    def subscribe(self, observer: Observer) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self, event: str, data: Any = None) -> None:
        for observer in self._observers:
            observer.update(event, data)
```

### 1.3 Weak References — Preventing Memory Leaks

By default, an observer list holds **strong references**. If a widget is destroyed, the event bus still holds a reference to it, preventing garbage collection. **Weak references** let the GC collect dead observers automatically.

```python
import weakref
from collections import defaultdict

class WeakEventBus:
    def __init__(self):
        self._handlers: dict[str, list] = defaultdict(list)

    def subscribe(self, event: str, handler: Callable) -> None:
        if hasattr(handler, "__self__"):
            ref = weakref.WeakMethod(handler)   # ← bound methods need WeakMethod
        else:
            ref = weakref.ref(handler)
        self._handlers[event].append(ref)

    def emit(self, event: str, **kwargs) -> None:
        alive = []
        for ref in self._handlers.get(event, []):
            handler = ref()                     # ← dereference; None if collected
            if handler is not None:
                handler(**kwargs)
                alive.append(ref)
        self._handlers[event] = alive           # ← prune dead refs
```

```python
bus = WeakEventBus()
h = SomeHandler()
bus.subscribe("data.ready", h.handle)
del h               # h is garbage collected
bus.emit("data.ready", payload="x")   # no error, handler silently gone
```

**When to use weak refs:** Long-lived subjects (app-wide bus) with short-lived observers (UI widgets, request-scoped handlers).

**Common mistakes:**
- Subscribing a lambda or local function with weak refs (they are immediately collected — use strong refs or store the function)
- Forgetting to unsubscribe, causing memory leaks in non-weak-ref buses
- Calling `notify()` while iterating `_observers` and mutating the list inside a handler

---

## 2. Strategy Pattern

A GPS offers three routes to the same destination: fastest, shortest, avoid tolls. You pick a route and the GPS navigates you. Switching routes does not change your destination or the GPS hardware — only the algorithm. **Strategy** encapsulates interchangeable algorithms behind a uniform interface.

### 2.1 Function-Based Strategy (Pythonic)

In Python, functions are first-class objects. A strategy does not need a class — a callable is enough.

```python
from typing import Callable
from dataclasses import dataclass, field

def standard_shipping(weight_kg: float, distance_km: float) -> float:
    return weight_kg * 0.5 + distance_km * 0.01

def express_shipping(weight_kg: float, distance_km: float) -> float:
    return (weight_kg * 1.2 + distance_km * 0.05) * 1.5

def free_shipping(weight_kg: float, distance_km: float) -> float:
    return 0.0

@dataclass
class Order:
    item:     str
    weight:   float
    distance: float
    _shipping_fn: Callable = field(default=standard_shipping, repr=False)

    def set_shipping(self, fn: Callable) -> "Order":
        self._shipping_fn = fn
        return self                         # ← fluent interface

    def shipping_cost(self) -> float:
        return self._shipping_fn(self.weight, self.distance)
```

```python
order = Order("Laptop", weight=2.5, distance=500)
order.set_shipping(express_shipping)
order.shipping_cost()   # calculated with express strategy
```

**Use callable strategy when:** algorithms are stateless pure functions.

### 2.2 Class-Based Strategy with ABC

Use when strategies need state, shared helpers, or multiple methods.

```python
from abc import ABC, abstractmethod

class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: list) -> list: ...

class BubbleSortStrategy(SortStrategy):
    def sort(self, data: list) -> list:
        result = list(data)
        n = len(result)
        for i in range(n):
            for j in range(0, n - i - 1):
                if result[j] > result[j + 1]:
                    result[j], result[j + 1] = result[j + 1], result[j]
        return result

class TimSortStrategy(SortStrategy):
    def sort(self, data: list) -> list:
        return sorted(data)             # ← delegates to Python's built-in

class Sorter:
    def __init__(self, strategy: SortStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: SortStrategy) -> None:
        self._strategy = strategy       # ← swap at runtime

    def sort(self, data: list) -> list:
        return self._strategy.sort(data)
```

### 2.3 Registration Pattern for Strategy Selection

Combine Strategy with a registry to select algorithms from config strings.

```python
class PaymentRegistry:
    _strategies: dict[str, type] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(strategy_cls):
            cls._strategies[name] = strategy_cls
            return strategy_cls
        return decorator

    @classmethod
    def get(cls, name: str):
        return cls._strategies[name]()

@PaymentRegistry.register("stripe")
class StripeStrategy:
    FEE_RATE = 0.029
    def process(self, amount: float) -> dict:
        fee = round(amount * self.FEE_RATE + 0.30, 2)
        return {"processor": "Stripe", "fee": fee, "net": amount - fee}
```

### 2.4 Discount Calculator — Real Scenario

```python
def gold_discount(price: float) -> float:    return price * 0.80   # 20% off
def silver_discount(price: float) -> float:  return price * 0.90   # 10% off
def no_discount(price: float) -> float:      return price

DISCOUNT_STRATEGIES = {
    "gold":   gold_discount,
    "silver": silver_discount,
    "free":   no_discount,
}

def calculate_price(price: float, tier: str) -> float:
    strategy = DISCOUNT_STRATEGIES.get(tier, no_discount)
    return strategy(price)
```

**Common mistakes:**
- Building a Strategy class hierarchy when a dict of functions suffices
- Mutating the context from inside a strategy (strategies should be side-effect-free on context)
- Forgetting to handle unknown strategy names gracefully

---

## 3. Command Pattern

Think of a restaurant. You tell the waiter your order. The waiter writes it on a slip and passes it to the kitchen. The kitchen executes the order. The slip (command object) encapsulates the request — it can be queued, logged, delayed, or undone (bring the wrong dish back). **Command** turns a request into a standalone object.

### 3.1 Command Object with Execute and Undo

```python
from abc import ABC, abstractmethod
from typing import Any

class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...

class TextBuffer:
    def __init__(self):
        self.text = ""

class InsertTextCommand(Command):
    def __init__(self, buffer: TextBuffer, position: int, text: str):
        self._buffer   = buffer
        self._position = position
        self._text     = text

    def execute(self) -> None:
        self._buffer.text = (
            self._buffer.text[:self._position]
            + self._text
            + self._buffer.text[self._position:]
        )

    def undo(self) -> None:
        self._buffer.text = (
            self._buffer.text[:self._position]
            + self._buffer.text[self._position + len(self._text):]
        )

class DeleteTextCommand(Command):
    def __init__(self, buffer: TextBuffer, position: int, length: int):
        self._buffer   = buffer
        self._position = position
        self._length   = length
        self._deleted  = ""        # ← saved for undo

    def execute(self) -> None:
        self._deleted = self._buffer.text[self._position:self._position + self._length]
        self._buffer.text = (
            self._buffer.text[:self._position]
            + self._buffer.text[self._position + self._length:]
        )

    def undo(self) -> None:
        self._buffer.text = (
            self._buffer.text[:self._position]
            + self._deleted
            + self._buffer.text[self._position:]
        )
```

### 3.2 Command History (Undo Stack)

```python
class TextEditor:
    def __init__(self):
        self._buffer  = TextBuffer()
        self._history: list[Command] = []

    def execute(self, command: Command) -> None:
        command.execute()
        self._history.append(command)

    def undo(self) -> None:
        if self._history:
            self._history.pop().undo()  # ← undo last command

    @property
    def text(self) -> str:
        return self._buffer.text
```

```python
editor = TextEditor()
buf = editor._buffer

c1 = InsertTextCommand(buf, 0, "Hello")
c2 = InsertTextCommand(buf, 5, " World")
editor.execute(c1)   # "Hello"
editor.execute(c2)   # "Hello World"
editor.undo()        # "Hello"
editor.undo()        # ""
```

**Common mistakes:**
- Not saving enough state in `undo()` to reverse the operation
- Sharing mutable state between commands (each command should capture its own snapshot)
- Building Command when a simple function call or callback suffices

---

## 4. Template Method Pattern

A recipe template says: preheat oven, prepare ingredients, mix, bake, cool. The steps are fixed. What varies is the specific ingredients and timing for chocolate cake vs vanilla cake. **Template Method** defines the skeleton of an algorithm in a base class, letting subclasses fill in specific steps.

### 4.1 Abstract Base with Template Method

```python
from abc import ABC, abstractmethod

class ReportGenerator(ABC):
    """Template method: generate() defines the fixed pipeline."""

    def generate(self, data: list) -> str:
        """Template method — DO NOT override this."""
        header  = self.build_header()
        body    = self.build_body(data)
        footer  = self.build_footer()
        return f"{header}\n{body}\n{footer}"

    @abstractmethod
    def build_header(self) -> str: ...    # ← subclass fills in

    @abstractmethod
    def build_body(self, data: list) -> str: ...

    def build_footer(self) -> str:
        return "--- End of Report ---"    # ← default implementation (hook)
```

```python
class HTMLReport(ReportGenerator):
    def build_header(self) -> str:
        return "<html><body>"

    def build_body(self, data: list) -> str:
        rows = "".join(f"<tr><td>{row}</td></tr>" for row in data)
        return f"<table>{rows}</table>"

    def build_footer(self) -> str:
        return "</body></html>"           # ← override the hook

class TextReport(ReportGenerator):
    def build_header(self) -> str:
        return "=" * 40

    def build_body(self, data: list) -> str:
        return "\n".join(str(row) for row in data)
```

### 4.2 Hook Methods

A **hook** is a method with a default (often empty) implementation. Subclasses can override hooks to inject behavior at specific points without being forced to.

```python
class DataProcessor(ABC):
    def process(self, data: list) -> list:
        data = self.validate(data)
        self.before_transform()        # ← hook: do nothing by default
        data = self.transform(data)
        self.after_transform(data)     # ← hook: do nothing by default
        return data

    @abstractmethod
    def transform(self, data: list) -> list: ...

    def validate(self, data: list) -> list:
        return [x for x in data if x is not None]

    def before_transform(self) -> None: pass   # ← hook
    def after_transform(self, data: list) -> None: pass   # ← hook
```

**Template Method vs Strategy:**

| Aspect | Template Method | Strategy |
|---|---|---|
| Mechanism | Inheritance | Composition |
| Flexibility | Fixed pipeline, variable steps | Entirely replaceable algorithm |
| When | Framework pipeline, many shared steps | Completely different algorithms |

**Common mistakes:**
- Overriding the template method itself (it should be `final` in intent)
- Too many abstract methods (subclasses become heavy to implement)
- Using Template Method when Strategy with composition would be cleaner

---

## 📂 Navigation

**[🏠 Back to README](../../README.md)**

**Prev:** [← 01 Creational](../01_creational/theory.md) &nbsp;|&nbsp; **Next:** [03 Dependency Injection →](../03_dependency_injection/theory.md)

**Related Topics:** [01 Creational](../01_creational/theory.md) · [03 Dependency Injection](../03_dependency_injection/theory.md) · [Root Theory](../theory.md)
