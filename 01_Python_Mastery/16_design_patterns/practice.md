# Design Patterns — Practice Questions

25 questions surveying all patterns: Singleton, Factory, Observer, Strategy, Command, Template Method, and Dependency Injection.

**Deep dives:** [01 Creational](./01_creational/practice.md) · [02 Behavioral](./02_behavioral/practice.md) · [03 Dependency Injection](./03_dependency_injection/practice.md)

---

## Singleton (Q1–Q5)


## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| [Q1](#q1) | singleton · Module-Level Singleton | 🟢 |
| [Q2](#q2) | singleton · `__new__`-Based Singleton | 🟡 |
| [Q3](#q3) | singleton · Thread-Safe Singleton | 🟡 |
| [Q4](#q4) | singleton · Borg Pattern | 🟡 |
| [Q5](#q5) | singleton · Singleton Decorator | 🟡 |
| [Q6](#q6) | factory · Simple Factory with Dict Dispatch | 🟡 |
| [Q7](#q7) | factory · Factory Method Pattern | 🟡 |
| [Q8](#q8) | factory · Registration Factory | 🟡 |
| [Q9](#q9) | observer · Basic Event Subscription | 🟢 |
| [Q10](#q10) | observer · `@bus.on` Decorator | 🟡 |
| [Q11](#q11) | observer · Classic Observer with ABC | 🟡 |
| [Q12](#q12) | observer · Weak Reference Bus | 🟡 |
| [Q13](#q13) | strategy · Class-Based Strategy | 🟡 |
| [Q14](#q14) | strategy · Function-Based Strategy | 🟡 |
| [Q15](#q15) | strategy · Payment Processor with Registry | 🟡 |
| [Q16](#q16) | strategy · Sort Strategy Comparison | 🟡 |
| [Q17](#q17) | command · Basic Command Execute/Undo | 🟡 |
| [Q18](#q18) | command · Text Editor with Undo Stack | 🟡 |
| [Q19](#q19) | command · Macro Command (Batch) | 🟠 |
| [Q20](#q20) | template method · Data Processor | 🟡 |
| [Q21](#q21) | template method · Report Generator | 🟡 |
| [Q22](#q22) | chain · Middleware Pipeline | 🟠 |
| [Q23](#q23) | di · Constructor Injection Basics | 🟢 |
| [Q24](#q24) | di · Service Locator | 🟡 |
| [Q25](#q25) | di · Capstone: Testable Data Pipeline | 🟠 |

---

<a id="q1"></a>

### Q1 🟢 · singleton · Module-Level Singleton

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)



**Problem:** Create a module-level `config` singleton with `env="production"` and `debug=False`. Show that two variables assigned from the same import point to the same object (`a is b == True`).

<details>
<summary>💡 Hint</summary>
Create the object at module scope. Python's import cache ensures the module body runs once.
</details>

<details>
<summary>✅ Answer</summary>

```python
class _Config:
    def __init__(self):
        self.env   = "production"
        self.debug = False

config = _Config()   # module-level singleton

# In usage:
from this_module import config as a
from this_module import config as b
assert a is b   # True
```

**Why:** Module-level objects are the most Pythonic singleton. No `__new__` boilerplate needed.
</details>

---

<a id="q2"></a>

### Q2 🟡 · singleton · `__new__`-Based Singleton

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)



**Problem:** Implement a `Config` class using `__new__`. Include `_initialized` guard. `Config("prod")` followed by `Config("staging")` should both return the same instance with `env="prod"`.

<details>
<summary>💡 Hint</summary>
`__new__` returns the cached instance; `__init__` is still called but must guard with `if self._initialized: return`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, env: str = "development"):
        if self._initialized:
            return
        self.env = env
        self._initialized = True

    @classmethod
    def reset(cls): cls._instance = None

a = Config("prod")
b = Config("staging")
assert a is b
assert b.env == "prod"
```

**Why:** `__new__` controls instance creation. The `_initialized` guard prevents `__init__` from overwriting attributes on subsequent calls.
</details>

---

<a id="q3"></a>

### Q3 🟡 · singleton · Thread-Safe Singleton

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)



**Problem:** Add double-checked locking to a singleton. Launch 5 threads that call the constructor simultaneously. Assert only one instance is ever created.

<details>
<summary>💡 Hint</summary>
Check `_instance is None` both outside and inside the lock.
</details>

<details>
<summary>✅ Answer</summary>

```python
import threading

class SafeSingleton:
    _instance = None
    _lock      = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

ids = []
def create(): ids.append(id(SafeSingleton()))
threads = [threading.Thread(target=create) for _ in range(5)]
for t in threads: t.start()
for t in threads: t.join()
assert len(set(ids)) == 1
```

**Why:** Without the inner check, two threads both passing the outer check could create two instances. The inner check (inside the lock) closes that race window.
</details>

---

<a id="q4"></a>

### Q4 🟡 · singleton · Borg Pattern

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)



**Problem:** Implement a `Settings` Borg class. Create two instances. Writing an attribute via one should be immediately visible through the other, but `s1 is s2` should be `False`.

<details>
<summary>💡 Hint</summary>
`self.__dict__ = Settings._shared_state` makes all instances share the same dictionary.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Settings:
    _shared_state: dict = {}

    def __init__(self):
        self.__dict__ = Settings._shared_state

s1 = Settings()
s2 = Settings()
s1.theme = "dark"
assert s2.theme == "dark"
assert s1 is not s2
```

**Why:** All `Settings` instances share one `__dict__`. Any attribute change appears on every instance.
</details>

---

<a id="q5"></a>

### Q5 🟡 · singleton · Singleton Decorator

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)



**Problem:** Write a `@singleton` decorator that turns any class into a singleton. Apply it to a `Cache` class. Include a `_reset` helper for tests.

<details>
<summary>💡 Hint</summary>
The decorator wraps the class in a `get_instance()` closure. `instances = {}` stores the singleton per class.
</details>

<details>
<summary>✅ Answer</summary>

```python
def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    get_instance.__name__ = cls.__name__
    get_instance._reset   = lambda: instances.pop(cls, None)
    return get_instance

@singleton
class Cache:
    def __init__(self):
        self._store = {}
    def set(self, k, v): self._store[k] = v
    def get(self, k):    return self._store.get(k)

c1 = Cache()
c2 = Cache()
assert c1 is c2
c1.set("x", 42)
assert c2.get("x") == 42
```

**Why:** The decorator stores the instance in a closure dict. Each decorated class gets its own storage. Cleaner than inheriting a singleton base class.
</details>

---

## Factory (Q6–Q8)

<a id="q6"></a>

### Q6 🟡 · factory · Simple Factory with Dict Dispatch

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)



**Problem:** Write `create_serializer(format)` that returns a JSON, CSV, or YAML serializer. Use dict dispatch. Raise `ValueError` for unknown formats. Each serializer has a `.serialize(data)` method.

<details>
<summary>💡 Hint</summary>
`{"json": JSONSerializer, "csv": CSVSerializer}[format]()` with a guard for missing keys.
</details>

<details>
<summary>✅ Answer</summary>

```python
import json

class JSONSerializer:
    def serialize(self, data): return json.dumps(data)

class CSVSerializer:
    def serialize(self, data):
        if not data: return ""
        headers = ",".join(data[0].keys())
        rows    = [",".join(str(v) for v in row.values()) for row in data]
        return "\n".join([headers] + rows)

def create_serializer(format: str):
    factories = {"json": JSONSerializer, "csv": CSVSerializer}
    if format not in factories:
        raise ValueError(f"Unknown format: {format!r}")
    return factories[format]()

s = create_serializer("json")
assert s.serialize({"key": "val"}) == '{"key": "val"}'
```

**Why:** Dict dispatch is cleaner than if/elif. Adding a new format requires one new class and one dict entry.
</details>

---

<a id="q7"></a>

### Q7 🟡 · factory · Factory Method Pattern

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)



**Problem:** Build a `NotificationSender` abstract class with `create_transport()` factory method and a `send(message, recipient)` template method. Implement `EmailSender` and `SMSSender`.

<details>
<summary>💡 Hint</summary>
`send()` calls `self.create_transport()` to get the transport object, then uses it. Subclasses only override `create_transport`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class Transport(ABC):
    @abstractmethod
    def deliver(self, message: str, recipient: str) -> dict: ...

class EmailTransport(Transport):
    def deliver(self, message, recipient):
        return {"via": "email", "to": recipient, "body": message}

class SMSTransport(Transport):
    def deliver(self, message, recipient):
        return {"via": "sms", "to": recipient, "text": message[:160]}

class NotificationSender(ABC):
    @abstractmethod
    def create_transport(self) -> Transport: ...

    def send(self, message: str, recipient: str) -> dict:
        transport = self.create_transport()
        return transport.deliver(message, recipient)

class EmailSender(NotificationSender):
    def create_transport(self): return EmailTransport()

class SMSSender(NotificationSender):
    def create_transport(self): return SMSTransport()

result = EmailSender().send("Hello", "alice@example.com")
assert result["via"] == "email"
```

**Why:** The base class defines the `send` algorithm. Subclasses only decide which transport to create.
</details>

---

<a id="q8"></a>

### Q8 🟡 · factory · Registration Factory

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)



**Problem:** Build a `ParserFactory` with `@ParserFactory.register("json")` decorator. Implement `JSONParser` and `CSVParser`. `ParserFactory.create("json")` returns an instance.

<details>
<summary>💡 Hint</summary>
`register` is a classmethod returning a decorator that stores the class in `_registry[name]`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import json

class ParserFactory:
    _registry = {}

    @classmethod
    def register(cls, name: str):
        def decorator(parser_cls):
            cls._registry[name] = parser_cls
            return parser_cls
        return decorator

    @classmethod
    def create(cls, name: str):
        if name not in cls._registry:
            raise KeyError(f"Unknown parser: {name!r}")
        return cls._registry[name]()

@ParserFactory.register("json")
class JSONParser:
    def parse(self, raw: str) -> list:
        return json.loads(raw)

@ParserFactory.register("csv")
class CSVParser:
    def parse(self, raw: str) -> list:
        lines   = raw.strip().split("\n")
        headers = lines[0].split(",")
        return [dict(zip(headers, l.split(","))) for l in lines[1:]]

parser = ParserFactory.create("json")
result = parser.parse('[{"id": 1}]')
assert result == [{"id": 1}]
```

**Why:** The factory never changes when new parsers are added. New parsers self-register via the decorator.
</details>

---

## Observer (Q9–Q12)

<a id="q9"></a>

### Q9 🟢 · observer · Basic Event Subscription

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)



**Problem:** Build `EventBus` with `subscribe`, `unsubscribe`, `emit`. Subscribe two handlers to `"data.ready"`. Unsubscribe one. Emit and verify only the remaining handler fires.

<details>
<summary>💡 Hint</summary>
Use `defaultdict(list)`. `emit` calls each handler with `**kwargs`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import defaultdict

class EventBus:
    def __init__(self):
        self._h = defaultdict(list)

    def subscribe(self, event, handler):   self._h[event].append(handler)
    def unsubscribe(self, event, handler): self._h[event].remove(handler)
    def emit(self, event, **kw):
        for h in list(self._h.get(event, [])): h(**kw)

fired = []
def ha(**kw): fired.append("A")
def hb(**kw): fired.append("B")

bus = EventBus()
bus.subscribe("data.ready", ha)
bus.subscribe("data.ready", hb)
bus.unsubscribe("data.ready", hb)
bus.emit("data.ready")
assert fired == ["A"]
```

**Why:** The subscriber list per event supports multiple handlers. Unsubscribe removes by identity.
</details>

---

<a id="q10"></a>

### Q10 🟡 · observer · `@bus.on` Decorator

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)



**Problem:** Add an `on(*events)` decorator method to `EventBus`. Register a single function for `"user.login"` and `"user.logout"`. Emit both and verify the function is called twice total.

<details>
<summary>💡 Hint</summary>
`on(*events)` returns a decorator that calls `self.subscribe(event, func)` for each event.
</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import defaultdict

class EventBus:
    def __init__(self):
        self._h = defaultdict(list)

    def subscribe(self, event, handler): self._h[event].append(handler)
    def emit(self, event, **kw):
        for h in self._h.get(event, []): h(**kw)

    def on(self, *events):
        def decorator(func):
            for e in events:
                self.subscribe(e, func)
            return func
        return decorator

bus   = EventBus()
calls = []

@bus.on("user.login", "user.logout")
def audit(**kw): calls.append(kw)

bus.emit("user.login",  user_id=1)
bus.emit("user.logout", user_id=1)
assert len(calls) == 2
```

**Why:** The `@bus.on` decorator registers the function for multiple events in one statement.
</details>

---

<a id="q11"></a>

### Q11 🟡 · observer · Classic Observer with ABC

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)



**Problem:** Implement `Subject` and `Observer` ABC. Create `StockPrice(Subject)` that notifies observers when `.price` is set via a property setter. Create `AlertObserver` that prints when price moves more than 5%.

<details>
<summary>💡 Hint</summary>
The property setter calculates `change_pct` and calls `self.notify("PRICE_CHANGED", data)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod
from typing import Any

class Observer(ABC):
    @abstractmethod
    def update(self, event: str, data: Any) -> None: ...

class Subject:
    def __init__(self):
        self._observers = []
    def subscribe(self, o): self._observers.append(o)
    def notify(self, event, data=None):
        for o in self._observers: o.update(event, data)

class StockPrice(Subject):
    def __init__(self, symbol, price):
        super().__init__()
        self.symbol = symbol
        self._price = price

    @property
    def price(self): return self._price

    @price.setter
    def price(self, new):
        old = self._price; self._price = new
        pct = (new - old) / old * 100
        self.notify("PRICE_CHANGED", {"symbol": self.symbol, "pct": pct, "new": new})

class AlertObserver(Observer):
    def __init__(self): self.alerts = []
    def update(self, event, data):
        if event == "PRICE_CHANGED" and abs(data["pct"]) >= 5:
            self.alerts.append(data)

stock = StockPrice("AAPL", 100.0)
alert = AlertObserver()
stock.subscribe(alert)
stock.price = 103.0   # 3% — no alert
stock.price = 90.0    # -13% — alert
assert len(alert.alerts) == 1
```

**Why:** The property setter automatically notifies all observers. They filter events they care about.
</details>

---

<a id="q12"></a>

### Q12 🟡 · observer · Weak Reference Bus

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)



**Problem:** Build a `WeakEventBus`. Subscribe a handler object. Delete it. Emit and verify no crash and the dead handler is pruned from the internal list.

<details>
<summary>💡 Hint</summary>
Use `weakref.WeakMethod` for bound methods. In `emit`, filter out refs where `ref()` returns `None`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import weakref
from collections import defaultdict

class WeakEventBus:
    def __init__(self): self._h = defaultdict(list)

    def subscribe(self, event, handler):
        ref = weakref.WeakMethod(handler) if hasattr(handler, "__self__") else weakref.ref(handler)
        self._h[event].append(ref)

    def emit(self, event, **kw):
        alive = []
        for ref in self._h.get(event, []):
            h = ref()
            if h is not None:
                h(**kw); alive.append(ref)
        self._h[event] = alive

class H:
    def handle(self, **kw): pass

bus = WeakEventBus()
h   = H()
bus.subscribe("x", h.handle)
del h
bus.emit("x")   # no crash
assert len(bus._h["x"]) == 0   # pruned
```

**Why:** Weak references do not prevent garbage collection. The bus silently removes dead handlers on the next emit.
</details>

---

## Strategy (Q13–Q16)

<a id="q13"></a>

### Q13 🟡 · strategy · Class-Based Strategy

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)



**Problem:** Build `CompressionStrategy` ABC with `compress(data: bytes) -> bytes`. Implement `GzipStrategy` and `NoOpStrategy`. Build a `Compressor` that swaps strategies via `set_strategy`.

<details>
<summary>💡 Hint</summary>
`import gzip; gzip.compress(data)` for the Gzip implementation.
</details>

<details>
<summary>✅ Answer</summary>

```python
import gzip
from abc import ABC, abstractmethod

class CompressionStrategy(ABC):
    @abstractmethod
    def compress(self, data: bytes) -> bytes: ...

class GzipStrategy(CompressionStrategy):
    def compress(self, data: bytes) -> bytes: return gzip.compress(data)

class NoOpStrategy(CompressionStrategy):
    def compress(self, data: bytes) -> bytes: return data

class Compressor:
    def __init__(self, strategy: CompressionStrategy):
        self._strategy = strategy
    def set_strategy(self, s): self._strategy = s
    def compress(self, data): return self._strategy.compress(data)

c    = Compressor(NoOpStrategy())
data = b"hello world"
assert c.compress(data) == data
c.set_strategy(GzipStrategy())
compressed = c.compress(data)
assert compressed != data
assert gzip.decompress(compressed) == data
```

**Why:** The compressor delegates to whatever strategy is currently set. Swapping algorithms at runtime is a single `set_strategy` call.
</details>

---

<a id="q14"></a>

### Q14 🟡 · strategy · Function-Based Strategy

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)



**Problem:** Write three tax calculation functions: `us_tax(price)` = 8%, `eu_tax(price)` = 20%, `no_tax(price)` = 0%. Build a `checkout(price, tax_fn)` function that applies the injected strategy.

<details>
<summary>💡 Hint</summary>
Each strategy is a plain function `(float) -> float`. `checkout` calls `tax_fn(price)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
def us_tax(price: float) -> float: return round(price * 0.08, 2)
def eu_tax(price: float) -> float: return round(price * 0.20, 2)
def no_tax(price: float) -> float: return 0.0

def checkout(price: float, tax_fn) -> dict:
    tax   = tax_fn(price)
    total = price + tax
    return {"price": price, "tax": tax, "total": total}

assert checkout(100.0, us_tax)["tax"] == 8.0
assert checkout(100.0, eu_tax)["tax"] == 20.0
assert checkout(100.0, no_tax)["tax"] == 0.0
```

**Why:** Functions are first-class. No class hierarchy needed for stateless algorithms.
</details>

---

<a id="q15"></a>

### Q15 🟡 · strategy · Payment Processor with Registry

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)



**Problem:** Build a `PaymentRegistry` with `@register("stripe")` decorator. Implement `StripeStrategy` (2.9% + $0.30) and `PayPalStrategy` (3.4% + $0.30). `Checkout(method).pay(amount)` selects the right strategy.

<details>
<summary>💡 Hint</summary>
The registry stores strategy classes. `Checkout.__init__` looks up and instantiates the strategy.
</details>

<details>
<summary>✅ Answer</summary>

```python
class PaymentRegistry:
    _strategies = {}

    @classmethod
    def register(cls, name):
        def dec(cls_): cls._strategies[name] = cls_; return cls_
        return dec

    @classmethod
    def get(cls, name): return cls._strategies[name]()

@PaymentRegistry.register("stripe")
class StripeStrategy:
    def process(self, amount):
        fee = round(amount * 0.029 + 0.30, 2)
        return {"processor": "Stripe", "fee": fee, "net": round(amount - fee, 2)}

@PaymentRegistry.register("paypal")
class PayPalStrategy:
    def process(self, amount):
        fee = round(amount * 0.034 + 0.30, 2)
        return {"processor": "PayPal", "fee": fee, "net": round(amount - fee, 2)}

class Checkout:
    def __init__(self, method): self._strategy = PaymentRegistry.get(method)
    def pay(self, amount): return self._strategy.process(amount)

stripe_result = Checkout("stripe").pay(100.0)
assert stripe_result["processor"] == "Stripe"
assert stripe_result["fee"]       == 3.19
```

**Why:** The registry decouples strategy selection from the Checkout class. New payment methods require only a new class with `@register`.
</details>

---

<a id="q16"></a>

### Q16 🟡 · strategy · Sort Strategy Comparison

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)



**Problem:** Implement `BubbleSortStrategy` and `TimSortStrategy`. Build `Sorter`. Sort the same list with both strategies and assert the results are identical.

<details>
<summary>💡 Hint</summary>
Both must return a new sorted list without mutating the input.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: list) -> list: ...

class BubbleSortStrategy(SortStrategy):
    def sort(self, data):
        r = list(data); n = len(r)
        for i in range(n):
            for j in range(0, n - i - 1):
                if r[j] > r[j+1]: r[j], r[j+1] = r[j+1], r[j]
        return r

class TimSortStrategy(SortStrategy):
    def sort(self, data): return sorted(data)

class Sorter:
    def __init__(self, s): self._s = s
    def set_strategy(self, s): self._s = s
    def sort(self, data): return self._s.sort(data)

data   = [5, 1, 8, 2, 9]
sorter = Sorter(BubbleSortStrategy())
r1     = sorter.sort(data)
sorter.set_strategy(TimSortStrategy())
r2 = sorter.sort(data)
assert r1 == r2 == [1, 2, 5, 8, 9]
```

**Why:** Both strategies produce identical output despite different algorithms. The Sorter never knows which algorithm ran.
</details>

---

## Command (Q17–Q19)

<a id="q17"></a>

### Q17 🟡 · command · Basic Command Execute/Undo

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)



**Problem:** Implement a `Counter` with `IncrementCommand` and `DecrementCommand`. Each has `execute()` and `undo()`. Build an `invoker` list. Execute 3 increments and 1 decrement. Undo twice. Verify final state.

<details>
<summary>💡 Hint</summary>
Commands hold a reference to the counter. `undo` of `IncrementCommand` decrements; `undo` of `DecrementCommand` increments.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...
    @abstractmethod
    def undo(self) -> None: ...

class Counter:
    def __init__(self): self.value = 0

class IncrementCommand(Command):
    def __init__(self, c, n=1): self._c = c; self._n = n
    def execute(self): self._c.value += self._n
    def undo(self):    self._c.value -= self._n

class DecrementCommand(Command):
    def __init__(self, c, n=1): self._c = c; self._n = n
    def execute(self): self._c.value -= self._n
    def undo(self):    self._c.value += self._n

counter = Counter()
history = []

def execute(cmd):
    cmd.execute(); history.append(cmd)

execute(IncrementCommand(counter))
execute(IncrementCommand(counter))
execute(IncrementCommand(counter))
execute(DecrementCommand(counter))
assert counter.value == 2

history.pop().undo(); assert counter.value == 3
history.pop().undo(); assert counter.value == 2
```

**Why:** Each command knows how to reverse itself. The history stack enables multi-level undo.
</details>

---

<a id="q18"></a>

### Q18 🟡 · command · Text Editor with Undo Stack

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)



**Problem:** Build a `TextEditor` with `InsertTextCommand`. `execute(cmd)` runs the command and pushes to history. `undo()` pops and reverses. Show "Hello World" → undo " World" → "Hello".

<details>
<summary>💡 Hint</summary>
`InsertTextCommand.undo()` removes the inserted slice using position + length.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...
    @abstractmethod
    def undo(self) -> None: ...

class TextBuffer:
    def __init__(self): self.text = ""

class InsertTextCommand(Command):
    def __init__(self, buf, pos, text):
        self._buf = buf; self._pos = pos; self._text = text

    def execute(self):
        b = self._buf.text
        self._buf.text = b[:self._pos] + self._text + b[self._pos:]

    def undo(self):
        b = self._buf.text
        self._buf.text = b[:self._pos] + b[self._pos + len(self._text):]

class TextEditor:
    def __init__(self):
        self._buf     = TextBuffer()
        self._history = []

    def execute(self, cmd):
        cmd.execute(); self._history.append(cmd)

    def undo(self):
        if self._history: self._history.pop().undo()

    @property
    def text(self): return self._buf.text

editor = TextEditor()
buf    = editor._buf
editor.execute(InsertTextCommand(buf, 0, "Hello"))
editor.execute(InsertTextCommand(buf, 5, " World"))
assert editor.text == "Hello World"
editor.undo()
assert editor.text == "Hello"
```

**Why:** Insert commands store position and text. Undo removes the exact inserted slice.
</details>

---

<a id="q19"></a>

### Q19 🟠 · command · Macro Command (Batch)

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)



**Problem:** Implement a `MacroCommand` that holds a list of commands and executes/undoes them as a unit. Build a batch of 3 counter increments as a single macro. Execute and undo the macro atomically.

<details>
<summary>💡 Hint</summary>
`MacroCommand.execute()` iterates and executes each sub-command. `undo()` iterates in reverse.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...
    @abstractmethod
    def undo(self) -> None: ...

class MacroCommand(Command):
    def __init__(self, commands: list[Command]):
        self._commands = commands

    def execute(self) -> None:
        for cmd in self._commands:
            cmd.execute()

    def undo(self) -> None:
        for cmd in reversed(self._commands):
            cmd.undo()

class Counter:
    def __init__(self): self.value = 0

class IncrementCommand(Command):
    def __init__(self, c, n=1): self._c = c; self._n = n
    def execute(self): self._c.value += self._n
    def undo(self):    self._c.value -= self._n

counter = Counter()
macro   = MacroCommand([
    IncrementCommand(counter),
    IncrementCommand(counter),
    IncrementCommand(counter),
])

macro.execute()
assert counter.value == 3
macro.undo()
assert counter.value == 0
```

**Why:** `MacroCommand` treats a group of commands as a single unit. Undo reverses them in LIFO order to maintain consistency.
</details>

---

## Template Method and Chain of Responsibility (Q20–Q22)

<a id="q20"></a>

### Q20 🟡 · template method · Data Processor

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)



**Problem:** Build `DataProcessor` ABC with `process(data)` template method that calls `validate(data)` then `transform(data)`. Provide a default `validate` (removes Nones). Implement `DoubleTransformer` that doubles each value.

<details>
<summary>💡 Hint</summary>
`process()` is not abstract. `transform()` is abstract. `validate()` is a hook with a default.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class DataProcessor(ABC):
    def process(self, data: list) -> list:
        clean = self.validate(data)
        return self.transform(clean)

    def validate(self, data: list) -> list:
        return [x for x in data if x is not None]   # default hook

    @abstractmethod
    def transform(self, data: list) -> list: ...

class DoubleTransformer(DataProcessor):
    def transform(self, data: list) -> list:
        return [x * 2 for x in data]

processor = DoubleTransformer()
result    = processor.process([1, None, 2, 3, None])
assert result == [2, 4, 6]
```

**Why:** `process()` defines the fixed pipeline. `validate` is a hook (overridable default). `transform` is a required extension point.
</details>

---

<a id="q21"></a>

### Q21 🟡 · template method · Report Generator

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)



**Problem:** Build `ReportGenerator` with `generate(data)` template method. Abstract: `build_header`, `build_body`. Default hook: `build_footer` returns `"--- End ---"`. Implement `HTMLReport` that overrides footer too.

<details>
<summary>💡 Hint</summary>
`generate` joins `build_header()`, `build_body(data)`, `build_footer()` with newlines.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class ReportGenerator(ABC):
    def generate(self, data: list) -> str:
        return "\n".join([self.build_header(), self.build_body(data), self.build_footer()])

    @abstractmethod
    def build_header(self) -> str: ...

    @abstractmethod
    def build_body(self, data: list) -> str: ...

    def build_footer(self) -> str:
        return "--- End ---"

class HTMLReport(ReportGenerator):
    def build_header(self) -> str:
        return "<html><body>"
    def build_body(self, data: list) -> str:
        return "<ul>" + "".join(f"<li>{x}</li>" for x in data) + "</ul>"
    def build_footer(self) -> str:
        return "</body></html>"

class TextReport(ReportGenerator):
    def build_header(self) -> str: return "=" * 20
    def build_body(self, data: list) -> str: return "\n".join(str(x) for x in data)

html = HTMLReport().generate(["A", "B"])
text = TextReport().generate(["A", "B"])
assert "</body></html>" in html
assert "--- End ---" in text   # default footer used
```

**Why:** The template method `generate` calls hooks in fixed order. Subclasses override only what differs.
</details>

---

<a id="q22"></a>

### Q22 🟠 · chain · Middleware Pipeline

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)



**Problem:** Build a three-stage middleware pipeline: `auth_middleware` (checks `request["token"]`), `rate_limit_middleware` (checks `request["calls"] < 10`), `handler` (returns 200). If any middleware fails, return an error without calling later stages.

<details>
<summary>💡 Hint</summary>
Each middleware takes `(request, next_fn)`. Call `next_fn(request)` to continue. Return error dict to short-circuit.
</details>

<details>
<summary>✅ Answer</summary>

```python
from typing import Callable

def auth_middleware(request: dict, next_fn: Callable) -> dict:
    if not request.get("token"):
        return {"status": 401, "error": "Unauthorized"}
    return next_fn(request)

def rate_limit_middleware(request: dict, next_fn: Callable) -> dict:
    if request.get("calls", 0) >= 10:
        return {"status": 429, "error": "Rate limit exceeded"}
    return next_fn(request)

def final_handler(request: dict) -> dict:
    return {"status": 200, "body": "OK"}

def build_pipeline(*middlewares, handler):
    def run(req, mws, final):
        if not mws: return final(req)
        return mws[0](req, lambda r: run(r, mws[1:], final))
    return lambda req: run(req, list(middlewares), handler)

pipeline = build_pipeline(auth_middleware, rate_limit_middleware, handler=final_handler)

assert pipeline({"token": "abc", "calls": 5})["status"] == 200
assert pipeline({"calls": 0})["status"] == 401
assert pipeline({"token": "abc", "calls": 15})["status"] == 429
```

**Why:** Each middleware can short-circuit by returning without calling `next_fn`. The chain is composable and each stage is independently testable.
</details>

---

## Dependency Injection (Q23–Q25)

<a id="q23"></a>

### Q23 🟢 · di · Constructor Injection Basics

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)



**Problem:** Refactor a `ReportService` that creates its own `Database` internally. Use constructor injection. Write a `MockDatabase` that returns a fixed dataset. Assert the service works with the mock.

<details>
<summary>💡 Hint</summary>
Move `Database()` from `__init__` body to `__init__` parameter.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def fetch_all(self, table: str) -> list: ...

class ReportService:
    def __init__(self, db: Database):
        self._db = db

    def generate_report(self, table: str) -> dict:
        rows = self._db.fetch_all(table)
        return {"table": table, "rows": len(rows), "data": rows}

class MockDatabase(Database):
    def fetch_all(self, table: str) -> list:
        return [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

service = ReportService(db=MockDatabase())
report  = service.generate_report("users")
assert report["rows"] == 2
assert report["data"][0]["name"] == "Alice"
```

**Why:** The service never imports or instantiates a concrete database. Tests pass a mock; production passes a real implementation.
</details>

---

<a id="q24"></a>

### Q24 🟡 · di · Service Locator

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)



**Problem:** Build `ServiceLocator` with `register(name, instance)` and `get(name)`. Register a `"cache"` and `"db"` service. Retrieve them. Raise `KeyError` for unregistered names.

<details>
<summary>💡 Hint</summary>
Class-level `_services = {}` dict. `get` raises `KeyError` if name not found.
</details>

<details>
<summary>✅ Answer</summary>

```python
class ServiceLocator:
    _services: dict = {}

    @classmethod
    def register(cls, name, instance): cls._services[name] = instance

    @classmethod
    def get(cls, name):
        if name not in cls._services:
            raise KeyError(f"Not registered: {name!r}")
        return cls._services[name]

    @classmethod
    def reset(cls): cls._services = {}

class FakeCache:
    def get(self, k): return None
    def set(self, k, v): pass

class FakeDB:
    def query(self, sql): return []

ServiceLocator.register("cache", FakeCache())
ServiceLocator.register("db",    FakeDB())

cache = ServiceLocator.get("cache")
db    = ServiceLocator.get("db")
assert db.query("SELECT 1") == []

try:
    ServiceLocator.get("missing")
    assert False, "should raise"
except KeyError:
    pass
```

**Why:** The locator centralizes dependency lookup. Unlike constructor injection, dependencies are pulled on demand — but they are hidden from callers.
</details>

---

<a id="q25"></a>

### Q25 🟠 · di · Capstone: Testable Data Pipeline

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)



**Problem:** Build `DataPipeline(source, sink, transform=None)`. `source` has `read() -> list`. `sink` has `write(data) -> int`. `transform` is an optional callable. `pipeline.run()` returns `{"rows_read": N, "rows_written": M}`. Test with stubs.

<details>
<summary>💡 Hint</summary>
`transform` defaults to identity (`lambda x: x`). `sink.write` returns the count written.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod
from typing import Callable

class DataSource(ABC):
    @abstractmethod
    def read(self) -> list: ...

class DataSink(ABC):
    @abstractmethod
    def write(self, data: list) -> int: ...

class DataPipeline:
    def __init__(self, source: DataSource, sink: DataSink, transform: Callable = None):
        self._source    = source
        self._sink      = sink
        self._transform = transform or (lambda x: x)

    def run(self) -> dict:
        data    = self._source.read()
        result  = self._transform(data)
        written = self._sink.write(result)
        return {"rows_read": len(data), "rows_written": written}

class StubSource(DataSource):
    def __init__(self, rows): self._rows = rows
    def read(self): return list(self._rows)

class CollectSink(DataSink):
    def __init__(self): self.data = []
    def write(self, data): self.data.extend(data); return len(data)

source = StubSource([1, 2, None, 3, None])
sink   = CollectSink()
pipe   = DataPipeline(source, sink, transform=lambda rows: [r for r in rows if r is not None])

summary = pipe.run()
assert summary["rows_read"]    == 5
assert summary["rows_written"] == 3
assert sink.data               == [1, 2, 3]
```

**Why:** All three dependencies (source, sink, transform) are injected. The pipeline is fully testable with stubs and works in production with real implementations.
</details>

---

## 📂 Navigation

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Deep Dives:** [01 Creational](./01_creational/practice.md) · [02 Behavioral](./02_behavioral/practice.md) · [03 DI](./03_dependency_injection/practice.md)

**Related Topics:** [Theory](./theory.md) · [Cheetsheet](./cheetsheet.md) · [Interview Q&A](./interview.md)
