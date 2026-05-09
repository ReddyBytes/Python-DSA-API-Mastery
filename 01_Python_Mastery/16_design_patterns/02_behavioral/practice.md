# Behavioral Patterns — Practice Questions

10 questions covering Observer, Strategy, Command, and Template Method.

---


## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| [Q1](#q1) | observer · Basic Event System | 🟢 |
| [Q2](#q2) | observer · Multiple Event Types | 🟡 |
| [Q3](#q3) | observer · Weak References | 🟡 |
| [Q4](#q4) | strategy · Function-Based Strategy | 🟡 |
| [Q5](#q5) | strategy · Sort Algorithm Selector | 🟡 |
| [Q6](#q6) | strategy · Discount Calculator | 🟡 |
| [Q7](#q7) | command · Text Editor with Undo | 🟡 |
| [Q8](#q8) | template method · Report Generator | 🟡 |
| [Q9](#q9) | behavioral · Chain of Responsibility: Middleware Pipeline | 🟠 |
| [Q10](#q10) | observer + command · Capstone: Event Bus with Command Queue | 🟠 |

---

<a id="q1"></a>

### Q1 🟢 · observer · Basic Event System

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)



**Problem:** Build a simple `EventBus` with `subscribe(event, handler)`, `unsubscribe(event, handler)`, and `emit(event, **kwargs)`. Demonstrate: two handlers subscribed to "order.placed", one unsubscribed, only the remaining one fires on the next emit.

<details>
<summary>💡 Hint</summary>
Use `defaultdict(list)` to store handlers per event name. `emit` iterates the list and calls each handler with `**kwargs`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import defaultdict
from typing import Callable

class EventBus:
    def __init__(self):
        self._handlers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, handler: Callable) -> None:
        self._handlers[event].append(handler)

    def unsubscribe(self, event: str, handler: Callable) -> None:
        self._handlers[event].remove(handler)

    def emit(self, event: str, **kwargs) -> None:
        for handler in list(self._handlers.get(event, [])):
            handler(**kwargs)

fired = []
def handler_a(**kw): fired.append(("A", kw))
def handler_b(**kw): fired.append(("B", kw))

bus = EventBus()
bus.subscribe("order.placed", handler_a)
bus.subscribe("order.placed", handler_b)
bus.unsubscribe("order.placed", handler_b)
bus.emit("order.placed", order_id=1)
assert fired == [("A", {"order_id": 1})]
```

**Why:** The subscriber list per event allows multiple handlers. `list()` copy in emit prevents issues if a handler mutates the list.
</details>

---

<a id="q2"></a>

### Q2 🟡 · observer · Multiple Event Types

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)



**Problem:** Extend `EventBus` with an `@bus.on(*events)` decorator that registers a function as a handler for one or more event names. Register `audit_log` for both `"user.created"` and `"user.updated"`. Verify it fires for both.

<details>
<summary>💡 Hint</summary>
`on()` is a method that returns a decorator. The decorator calls `self.subscribe(event, func)` for each event name.
</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import defaultdict

class EventBus:
    def __init__(self):
        self._handlers = defaultdict(list)

    def subscribe(self, event, handler): self._handlers[event].append(handler)

    def emit(self, event, **kwargs):
        for h in self._handlers.get(event, []):
            h(**kwargs)

    def on(self, *events):
        def decorator(func):
            for event in events:
                self.subscribe(event, func)
            return func
        return decorator

bus    = EventBus()
called = []

@bus.on("user.created", "user.updated")
def audit_log(user_id: int, **_):
    called.append(user_id)

bus.emit("user.created", user_id=1)
bus.emit("user.updated", user_id=2)
assert called == [1, 2]
```

**Why:** `@bus.on("a", "b")` registers the same function for multiple events in one decorator call. Useful for audit logging, caching invalidation, or any cross-cutting concern.
</details>

---

<a id="q3"></a>

### Q3 🟡 · observer · Weak References

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)



**Problem:** Build a `WeakEventBus` that holds weak references to handlers. Create a handler object, subscribe it, delete it, then emit. Verify the emit does not crash and the dead handler is silently pruned.

<details>
<summary>💡 Hint</summary>
Use `weakref.WeakMethod` for bound methods, `weakref.ref` for plain functions. In `emit`, check `ref()` is not None before calling.
</details>

<details>
<summary>✅ Answer</summary>

```python
import weakref
from collections import defaultdict

class WeakEventBus:
    def __init__(self):
        self._handlers = defaultdict(list)

    def subscribe(self, event: str, handler) -> None:
        if hasattr(handler, "__self__"):
            ref = weakref.WeakMethod(handler)
        else:
            ref = weakref.ref(handler)
        self._handlers[event].append(ref)

    def emit(self, event: str, **kwargs) -> None:
        alive = []
        for ref in self._handlers.get(event, []):
            handler = ref()
            if handler is not None:
                handler(**kwargs)
                alive.append(ref)
        self._handlers[event] = alive   # prune dead refs

class Handler:
    def __init__(self, name): self.name = name
    def handle(self, **kw): print(f"{self.name} got {kw}")

bus = WeakEventBus()
h   = Handler("h1")
bus.subscribe("event", h.handle)
bus.emit("event", x=1)   # fires
del h
bus.emit("event", x=2)   # no crash — dead ref pruned silently
```

**Why:** Weak references allow the garbage collector to collect the handler object when no other strong references exist. The bus does not extend the handler's lifetime.
</details>

---

<a id="q4"></a>

### Q4 🟡 · strategy · Function-Based Strategy

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)



**Problem:** Implement an `Order` dataclass with a `_shipping_fn` callable field. Write three shipping strategies as plain functions: `standard_shipping`, `express_shipping`, `free_shipping`. Demonstrate swapping strategies at runtime via `order.set_shipping(fn)`.

<details>
<summary>💡 Hint</summary>
Use `dataclasses.field(default=standard_shipping)` for the callable field. `set_shipping` just replaces `self._shipping_fn`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass, field
from typing import Callable

def standard_shipping(weight: float, distance: float) -> float:
    return weight * 0.5 + distance * 0.01

def express_shipping(weight: float, distance: float) -> float:
    return (weight * 1.2 + distance * 0.05) * 1.5

def free_shipping(weight: float, distance: float) -> float:
    return 0.0

@dataclass
class Order:
    item:     str
    weight:   float
    distance: float
    _shipping_fn: Callable = field(default=standard_shipping, repr=False)

    def set_shipping(self, fn: Callable) -> "Order":
        self._shipping_fn = fn
        return self

    def shipping_cost(self) -> float:
        return self._shipping_fn(self.weight, self.distance)

order = Order("Laptop", weight=2.5, distance=500)
assert order.shipping_cost() == standard_shipping(2.5, 500)
order.set_shipping(free_shipping)
assert order.shipping_cost() == 0.0
```

**Why:** Functions are first-class in Python. No class hierarchy is needed when strategies are stateless. Swapping is a simple attribute assignment.
</details>

---

<a id="q5"></a>

### Q5 🟡 · strategy · Sort Algorithm Selector

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)



**Problem:** Build a `Sorter` class that accepts a `SortStrategy` ABC. Implement `BubbleSortStrategy` and `TimSortStrategy`. Verify that swapping strategies via `set_strategy()` produces identical sorted output.

<details>
<summary>💡 Hint</summary>
Both strategies must sort without mutating the input. Compare final results with `==`.
</details>

<details>
<summary>✅ Answer</summary>

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
        return sorted(data)

class Sorter:
    def __init__(self, strategy: SortStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: SortStrategy) -> None:
        self._strategy = strategy

    def sort(self, data: list) -> list:
        return self._strategy.sort(data)

data   = [5, 2, 8, 1, 9, 3]
sorter = Sorter(BubbleSortStrategy())
r1     = sorter.sort(data)
sorter.set_strategy(TimSortStrategy())
r2 = sorter.sort(data)
assert r1 == r2 == [1, 2, 3, 5, 8, 9]
```

**Why:** The Sorter does not care which algorithm runs — it delegates to `_strategy.sort()`. Identical output from both confirms correctness.
</details>

---

<a id="q6"></a>

### Q6 🟡 · strategy · Discount Calculator

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)



**Problem:** Build a `calculate_price(price, tier)` function that applies the right discount based on customer tier. Use a dict of functions: `gold` = 20% off, `silver` = 10% off, `free` = 0% off. Unknown tiers default to no discount.

<details>
<summary>💡 Hint</summary>
Store discount functions in a dict. Use `.get(tier, no_discount)` to handle unknown tiers gracefully.
</details>

<details>
<summary>✅ Answer</summary>

```python
def gold_discount(price: float) -> float:   return round(price * 0.80, 2)
def silver_discount(price: float) -> float: return round(price * 0.90, 2)
def no_discount(price: float) -> float:     return price

DISCOUNT_STRATEGIES = {
    "gold":   gold_discount,
    "silver": silver_discount,
    "free":   no_discount,
}

def calculate_price(price: float, tier: str) -> float:
    strategy = DISCOUNT_STRATEGIES.get(tier, no_discount)
    return strategy(price)

assert calculate_price(100.0, "gold")    == 80.0
assert calculate_price(100.0, "silver")  == 90.0
assert calculate_price(100.0, "unknown") == 100.0
```

**Why:** A dict of callables is cleaner than an if/elif chain. Adding a new tier means adding one function and one dict entry.
</details>

---

<a id="q7"></a>

### Q7 🟡 · command · Text Editor with Undo

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)



**Problem:** Implement a `TextEditor` with `InsertTextCommand` and `DeleteTextCommand`. The editor should maintain a history stack. `execute(command)` runs the command and pushes it. `undo()` pops and reverses the last command.

<details>
<summary>💡 Hint</summary>
`DeleteTextCommand.execute()` must save the deleted text in `self._deleted` so `undo()` can restore it.
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
    def __init__(self, buf: TextBuffer, pos: int, text: str):
        self._buf = buf; self._pos = pos; self._text = text

    def execute(self) -> None:
        b = self._buf.text
        self._buf.text = b[:self._pos] + self._text + b[self._pos:]

    def undo(self) -> None:
        b = self._buf.text
        self._buf.text = b[:self._pos] + b[self._pos + len(self._text):]

class DeleteTextCommand(Command):
    def __init__(self, buf: TextBuffer, pos: int, length: int):
        self._buf = buf; self._pos = pos; self._length = length
        self._deleted = ""

    def execute(self) -> None:
        b = self._buf.text
        self._deleted  = b[self._pos:self._pos + self._length]
        self._buf.text = b[:self._pos] + b[self._pos + self._length:]

    def undo(self) -> None:
        b = self._buf.text
        self._buf.text = b[:self._pos] + self._deleted + b[self._pos:]

class TextEditor:
    def __init__(self):
        self._buf     = TextBuffer()
        self._history: list[Command] = []

    def execute(self, command: Command) -> None:
        command.execute()
        self._history.append(command)

    def undo(self) -> None:
        if self._history:
            self._history.pop().undo()

    @property
    def text(self) -> str: return self._buf.text

editor = TextEditor()
buf    = editor._buf
editor.execute(InsertTextCommand(buf, 0, "Hello"))
editor.execute(InsertTextCommand(buf, 5, " World"))
assert editor.text == "Hello World"
editor.undo()
assert editor.text == "Hello"
editor.undo()
assert editor.text == ""
```

**Why:** Each command encapsulates both how to do and how to undo an operation. The history stack enables multi-level undo without the editor knowing the details of any operation.
</details>

---

<a id="q8"></a>

### Q8 🟡 · template method · Report Generator

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)



**Problem:** Implement a `ReportGenerator` abstract class with a `generate(data)` template method. It calls `build_header()`, `build_body(data)`, and `build_footer()` in sequence. Provide a default `build_footer()`. Implement `HTMLReport` and `TextReport` subclasses.

<details>
<summary>💡 Hint</summary>
`generate()` is not abstract — it defines the fixed algorithm. Only `build_header` and `build_body` must be abstract.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class ReportGenerator(ABC):
    def generate(self, data: list) -> str:
        """Template method — fixed pipeline."""
        return "\n".join([
            self.build_header(),
            self.build_body(data),
            self.build_footer(),
        ])

    @abstractmethod
    def build_header(self) -> str: ...

    @abstractmethod
    def build_body(self, data: list) -> str: ...

    def build_footer(self) -> str:
        return "--- End of Report ---"   # default hook

class HTMLReport(ReportGenerator):
    def build_header(self) -> str:
        return "<html><body>"
    def build_body(self, data: list) -> str:
        rows = "".join(f"<tr><td>{r}</td></tr>" for r in data)
        return f"<table>{rows}</table>"
    def build_footer(self) -> str:
        return "</body></html>"

class TextReport(ReportGenerator):
    def build_header(self) -> str:
        return "=" * 30
    def build_body(self, data: list) -> str:
        return "\n".join(str(r) for r in data)

data = ["Alice", "Bob"]
html = HTMLReport().generate(data)
text = TextReport().generate(data)
assert "<table>" in html
assert "=" * 30 in text
assert "--- End of Report ---" in text   # default footer used
```

**Why:** The algorithm structure (`generate`) is defined once. Subclasses only fill in the pieces that differ. `build_footer` is a hook — optional override.
</details>

---

<a id="q9"></a>

### Q9 🟠 · behavioral · Chain of Responsibility: Middleware Pipeline

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)



**Problem:** Build a `MiddlewarePipeline` where each middleware is a callable that receives `(request, next_handler)`. Chain: `AuthMiddleware` (checks `request["token"]`) → `LoggingMiddleware` (prints request) → `HandlerMiddleware` (returns response). If auth fails, short-circuit and return an error.

<details>
<summary>💡 Hint</summary>
Each middleware calls `next_handler(request)` to pass the request down the chain. The last handler does not call `next_handler`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from typing import Callable

def auth_middleware(request: dict, next_handler: Callable) -> dict:
    if not request.get("token"):
        return {"status": 401, "error": "Unauthorized"}
    return next_handler(request)

def logging_middleware(request: dict, next_handler: Callable) -> dict:
    print(f"[LOG] {request.get('method', 'GET')} {request.get('path', '/')}")
    response = next_handler(request)
    print(f"[LOG] Response status: {response.get('status')}")
    return response

def final_handler(request: dict) -> dict:
    return {"status": 200, "body": f"Hello, {request.get('user', 'world')}"}

def build_pipeline(*middlewares, handler: Callable) -> Callable:
    def _chain(request, mw_list, final):
        if not mw_list:
            return final(request)
        current = mw_list[0]
        rest    = mw_list[1:]
        return current(request, lambda req: _chain(req, rest, final))
    return lambda request: _chain(request, list(middlewares), handler)

pipeline = build_pipeline(auth_middleware, logging_middleware, handler=final_handler)
r1 = pipeline({"token": "abc", "user": "Alice"})
assert r1["status"] == 200
r2 = pipeline({"path": "/secret"})   # no token
assert r2["status"] == 401
```

**Why:** Each middleware wraps the next, forming a chain. Any middleware can short-circuit by not calling `next_handler`.
</details>

---

<a id="q10"></a>

### Q10 🟠 · observer + command · Capstone: Event Bus with Command Queue

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)



**Problem:** Build an `EventBus` where handlers are `Command` objects (with `execute()`) instead of plain functions. The bus queues commands and `flush()` executes them all. This allows deferred execution and batching.

<details>
<summary>💡 Hint</summary>
Store commands in a queue list. `emit(event, **kwargs)` creates command objects and appends them. `flush()` executes and clears the queue.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Callable

class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...

class FunctionCommand(Command):
    """Wraps a callable + kwargs into a Command object."""
    def __init__(self, fn: Callable, kwargs: dict):
        self._fn     = fn
        self._kwargs = kwargs

    def execute(self) -> None:
        self._fn(**self._kwargs)

class CommandEventBus:
    def __init__(self):
        self._handlers: dict[str, list[Callable]] = defaultdict(list)
        self._queue:    list[Command]              = []

    def subscribe(self, event: str, handler: Callable) -> None:
        self._handlers[event].append(handler)

    def emit(self, event: str, **kwargs) -> None:
        """Queue commands — do not execute yet."""
        for handler in self._handlers.get(event, []):
            self._queue.append(FunctionCommand(handler, kwargs))

    def flush(self) -> int:
        """Execute all queued commands and return count executed."""
        count = len(self._queue)
        for cmd in self._queue:
            cmd.execute()
        self._queue.clear()
        return count

executed = []
def handler_a(**kw): executed.append(("A", kw))
def handler_b(**kw): executed.append(("B", kw))

bus = CommandEventBus()
bus.subscribe("order.placed", handler_a)
bus.subscribe("order.placed", handler_b)

bus.emit("order.placed", order_id=1)
bus.emit("order.placed", order_id=2)
assert executed == []   # not yet executed
count = bus.flush()
assert count == 4       # 2 events × 2 handlers
assert len(executed) == 4
```

**Why:** Wrapping handlers in Command objects decouples emission from execution. The bus can accumulate events during a transaction and flush them atomically after commit.
</details>

---

## 📂 Navigation

**[🏠 Back to README](../../README.md)**

**Prev:** [← 01 Creational — Practice](../01_creational/practice.md) &nbsp;|&nbsp; **Next:** [03 Dependency Injection — Practice →](../03_dependency_injection/practice.md)

**Related Topics:** [Theory](./theory.md) · [01 Creational](../01_creational/practice.md) · [Root Practice](../practice.md)
