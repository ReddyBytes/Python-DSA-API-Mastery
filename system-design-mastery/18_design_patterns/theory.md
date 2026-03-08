# 🧩 Design Patterns for System Design

> Gang of Four patterns and how they appear in real distributed systems.
> Understanding patterns helps you design components that are maintainable,
> extensible, and communicate intent clearly.

---

## 📋 Contents

```
1.  Why patterns matter in system design
2.  Creational patterns
3.  Structural patterns
4.  Behavioral patterns
5.  Patterns in distributed systems
6.  Pattern combinations in real systems
7.  Anti-patterns
```

---

## 1. Why Patterns Matter

```
Design patterns are named solutions to recurring problems.
In system design, they help you:
  - Communicate intent quickly ("use a factory here")
  - Apply proven structures that others understand
  - Avoid common pitfalls

Caution:
  Patterns are tools, not requirements.
  Over-engineering with patterns adds complexity.
  Apply when the problem genuinely matches the pattern.
```

---

## 2. Creational Patterns

### Singleton
One instance, globally accessible.

```python
class Config:
    _instance: "Config | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data = {}
        return cls._instance

    def set(self, key: str, value) -> None:
        self._data[key] = value

    def get(self, key: str, default=None):
        return self._data.get(key, default)

# Config() always returns same instance
config = Config()
config.set("db_host", "localhost")
assert Config().get("db_host") == "localhost"  # same instance
```

**Real-world use:**
```
Database connection pool:   one pool per application
Logger instance:            one logger per module
Configuration manager:      loaded once at startup
Cache client:               one Redis client per process
```

**Caution:** Singletons are global state. They make testing harder.
Use dependency injection when possible.

---

### Factory Method
Define interface for object creation; let subclasses decide which class.

```python
from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def send(self, to: str, message: str) -> bool: ...

class EmailNotification(Notification):
    def send(self, to, message):
        print(f"Email → {to}: {message}")
        return True

class SMSNotification(Notification):
    def send(self, to, message):
        print(f"SMS → {to}: {message[:160]}")
        return True

class PushNotification(Notification):
    def send(self, to, message):
        print(f"Push → {to}: {message}")
        return True

class NotificationFactory:
    _creators = {
        "email": EmailNotification,
        "sms":   SMSNotification,
        "push":  PushNotification,
    }

    @classmethod
    def create(cls, channel: str) -> Notification:
        creator = cls._creators.get(channel)
        if not creator:
            raise ValueError(f"Unknown channel: {channel}")
        return creator()

    @classmethod
    def register(cls, channel: str, creator_cls) -> None:
        """Extension without modifying the factory (Open/Closed)."""
        cls._creators[channel] = creator_cls
```

**Real-world use:**
```
Payment processor factory:  Stripe, PayPal, Braintree
Storage driver factory:     LocalDisk, S3, GCS
Queue client factory:       RabbitMQ, SQS, Kafka
Logger factory:             FileLogger, CloudwatchLogger, JsonLogger
```

---

### Builder
Construct complex objects step by step.

```python
class HTTPRequestBuilder:
    def __init__(self):
        self._method = "GET"
        self._url = ""
        self._headers: dict[str, str] = {}
        self._body: bytes | None = None
        self._timeout: int = 30
        self._retries: int = 0

    def method(self, method: str) -> "HTTPRequestBuilder":
        self._method = method
        return self

    def url(self, url: str) -> "HTTPRequestBuilder":
        self._url = url
        return self

    def header(self, key: str, value: str) -> "HTTPRequestBuilder":
        self._headers[key] = value
        return self

    def bearer_token(self, token: str) -> "HTTPRequestBuilder":
        return self.header("Authorization", f"Bearer {token}")

    def json_body(self, data: dict) -> "HTTPRequestBuilder":
        import json
        self._body = json.dumps(data).encode()
        return self.header("Content-Type", "application/json")

    def timeout(self, seconds: int) -> "HTTPRequestBuilder":
        self._timeout = seconds
        return self

    def retries(self, count: int) -> "HTTPRequestBuilder":
        self._retries = count
        return self

    def build(self) -> dict:
        if not self._url:
            raise ValueError("URL is required")
        return {
            "method": self._method, "url": self._url,
            "headers": self._headers, "body": self._body,
            "timeout": self._timeout, "retries": self._retries
        }

# Usage:
request = (HTTPRequestBuilder()
    .method("POST")
    .url("https://api.example.com/orders")
    .bearer_token("my-jwt-token")
    .json_body({"item": "laptop", "qty": 1})
    .timeout(10)
    .retries(3)
    .build())
```

**Real-world:** Query builders (SQLAlchemy), test data builders, SDK configuration.

---

## 3. Structural Patterns

### Adapter
Convert interface of a class into another interface clients expect.

```python
# Legacy system we can't change
class LegacyUserDB:
    def fetch_user_by_id(self, id: int) -> tuple:
        return (id, "Alice", "alice@example.com", 25)

class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: int) -> dict | None: ...

class LegacyUserAdapter(UserRepository):
    def __init__(self, legacy_db: LegacyUserDB):
        self._db = legacy_db

    def find_by_id(self, user_id: int) -> dict | None:
        row = self._db.fetch_user_by_id(user_id)
        if row is None:
            return None
        id_, name, email, age = row
        return {"id": id_, "name": name, "email": email, "age": age}
```

**Real-world:** Wrapping third-party libraries, legacy system integration.

---

### Decorator
Add behavior to objects dynamically without changing their class.

```python
class CachingRepository(UserRepository):
    def __init__(self, inner: UserRepository, cache: dict):
        self._inner = inner
        self._cache = cache

    def find_by_id(self, user_id: int) -> dict | None:
        if user_id in self._cache:
            return self._cache[user_id]
        user = self._inner.find_by_id(user_id)
        if user:
            self._cache[user_id] = user
        return user

class LoggingRepository(UserRepository):
    def __init__(self, inner: UserRepository, logger):
        self._inner = inner
        self._log = logger

    def find_by_id(self, user_id: int) -> dict | None:
        self._log.info(f"Fetching user {user_id}")
        result = self._inner.find_by_id(user_id)
        self._log.info(f"Found: {result is not None}")
        return result

# Stack decorators:
repo = LoggingRepository(
    CachingRepository(real_repo, cache={}),
    logger=logger
)
```

**Real-world:** Caching, logging, retry, rate-limiting, tracing layers.

---

### Facade
Provide a simple interface to a complex subsystem.

```python
class OrderFacade:
    def __init__(self, inventory, payment, shipping, notification):
        self._inv = inventory
        self._pay = payment
        self._ship = shipping
        self._notify = notification

    def place_order(self, user_id: int, items: list, payment_token: str) -> dict:
        if not self._inv.reserve_all(items):
            raise ValueError("One or more items out of stock")
        try:
            charge_id = self._pay.charge(user_id, payment_token)
        except Exception:
            self._inv.release_all(items)
            raise
        tracking = self._ship.create_shipment(user_id, items)
        self._notify.send_confirmation(user_id, tracking)
        return {"charge_id": charge_id, "tracking": tracking}
```

**Real-world:** API gateway, service orchestrator in microservices.

---

### Proxy
Provide a surrogate to control access to another object.

```python
class UserServiceProxy(UserRepository):
    def __init__(self, real_service_factory, auth_context):
        self._service = None  # lazy init
        self._factory = real_service_factory
        self._auth = auth_context

    def find_by_id(self, user_id: int) -> dict | None:
        if not self._auth.can_read_user(user_id):
            raise PermissionError(f"Access denied to user {user_id}")
        if self._service is None:
            self._service = self._factory()
        return self._service.find_by_id(user_id)
```

**Proxy types:**
```
Virtual proxy:    lazy initialization (expensive object on demand)
Protection proxy: access control check before delegating
Remote proxy:     network call to remote object (gRPC stub IS a proxy)
Caching proxy:    cache results of expensive operations
Logging proxy:    record calls without changing original
```

---

### Composite
Tree structures where leaves and composites treated uniformly.

```python
class MenuItem(ABC):
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    @abstractmethod
    def total_price(self) -> float: ...

class Dish(MenuItem):
    def total_price(self) -> float:
        return self.price

class Combo(MenuItem):
    def __init__(self, name: str, discount: float = 0.0):
        super().__init__(name, 0)
        self._items: list[MenuItem] = []
        self._discount = discount

    def add(self, item: MenuItem) -> None:
        self._items.append(item)

    def total_price(self) -> float:
        subtotal = sum(i.total_price() for i in self._items)
        return subtotal * (1 - self._discount)
```

**Real-world:** File system trees, UI component hierarchies, menu systems, permission groups.

---

## 4. Behavioral Patterns

### Observer (Event Bus)
One-to-many dependency. When one object changes, dependents notified automatically.

```python
from typing import Callable, Any

class EventBus:
    def __init__(self):
        self._handlers: dict[str, list[Callable]] = {}

    def on(self, event: str, handler: Callable) -> None:
        self._handlers.setdefault(event, []).append(handler)

    def emit(self, event: str, data: Any = None) -> None:
        for handler in self._handlers.get(event, []):
            try:
                handler(data)
            except Exception as e:
                print(f"Handler error for {event}: {e}")

# Usage:
bus = EventBus()
bus.on("order.placed", send_confirmation_email)
bus.on("order.placed", update_inventory)
bus.on("order.placed", notify_warehouse)
bus.emit("order.placed", order)  # all 3 handlers called
```

**Real-world:** Domain events, UI event systems, webhook dispatchers, Kafka consumers.

---

### Strategy
Define family of algorithms, make them interchangeable.

```python
class PricingStrategy(ABC):
    @abstractmethod
    def calculate(self, base_price: float, customer) -> float: ...

class RegularPricing(PricingStrategy):
    def calculate(self, base_price, customer):
        return base_price

class PremiumPricing(PricingStrategy):
    def calculate(self, base_price, customer):
        return base_price * 0.85  # 15% discount

class SeasonalPricing(PricingStrategy):
    def __init__(self, multiplier: float):
        self._mult = multiplier
    def calculate(self, base_price, customer):
        return base_price * self._mult

class PricingEngine:
    def __init__(self, strategy: PricingStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: PricingStrategy) -> None:
        self._strategy = strategy

    def price(self, product, customer) -> float:
        return self._strategy.calculate(product.base_price, customer)
```

**Real-world:** Pricing, sorting, auth methods, routing algorithms, serialization.

---

### Command
Encapsulate a request as an object — supports undo, logging, queueing.

```python
class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...
    @abstractmethod
    def undo(self) -> None: ...

class TransferCommand(Command):
    def __init__(self, from_acc, to_acc, amount: float):
        self._from = from_acc
        self._to = to_acc
        self._amount = amount

    def execute(self) -> None:
        self._from.withdraw(self._amount)
        self._to.deposit(self._amount)

    def undo(self) -> None:
        self._to.withdraw(self._amount)
        self._from.deposit(self._amount)

class TransactionHistory:
    def __init__(self):
        self._history: list[Command] = []

    def execute(self, cmd: Command) -> None:
        cmd.execute()
        self._history.append(cmd)

    def undo_last(self) -> None:
        if self._history:
            self._history.pop().undo()
```

**Real-world:** Transaction systems, undo/redo, job queues, database migrations, macro recording.

---

### State
Object changes behavior based on internal state.

```python
from enum import Enum, auto

class Order:
    class Status(Enum):
        PENDING = auto()
        CONFIRMED = auto()
        SHIPPED = auto()
        DELIVERED = auto()
        CANCELLED = auto()

    VALID_TRANSITIONS = {
        Status.PENDING:    {Status.CONFIRMED, Status.CANCELLED},
        Status.CONFIRMED:  {Status.SHIPPED, Status.CANCELLED},
        Status.SHIPPED:    {Status.DELIVERED},
        Status.DELIVERED:  set(),
        Status.CANCELLED:  set(),
    }

    def __init__(self):
        self.status = self.Status.PENDING

    def transition(self, new_status: "Order.Status") -> None:
        if new_status not in self.VALID_TRANSITIONS[self.status]:
            raise ValueError(
                f"Cannot transition from {self.status.name} to {new_status.name}"
            )
        self.status = new_status
```

**Real-world:** Order/payment lifecycle, connection state, vending machine, traffic light.

---

### Chain of Responsibility
Pass request along handlers until one deals with it.

```python
class Middleware(ABC):
    def __init__(self):
        self._next: "Middleware | None" = None

    def set_next(self, m: "Middleware") -> "Middleware":
        self._next = m
        return m

    def process(self, request: dict) -> dict:
        if self._next:
            return self._next.process(request)
        return request  # pass through

class AuthMiddleware(Middleware):
    def process(self, request):
        if not request.get("token"):
            return {"error": "Unauthorized", "status": 401}
        request["user_id"] = 42  # decode token
        return super().process(request)

class RateLimitMiddleware(Middleware):
    def __init__(self, limit: int):
        super().__init__()
        self._counts: dict = {}
        self._limit = limit

    def process(self, request):
        uid = request.get("user_id", "anon")
        self._counts[uid] = self._counts.get(uid, 0) + 1
        if self._counts[uid] > self._limit:
            return {"error": "Rate limit exceeded", "status": 429}
        return super().process(request)

# Build chain:
auth = AuthMiddleware()
rate = RateLimitMiddleware(100)
auth.set_next(rate)
result = auth.process({"token": "valid", "path": "/api/data"})
```

**Real-world:** HTTP middleware pipeline, request validation, event processing.

---

### Template Method
Define skeleton of algorithm; subclasses fill in the steps.

```python
class DataExporter(ABC):
    def export(self, data: list) -> None:
        """Template method."""
        prepared = self._prepare(data)
        formatted = self._format(prepared)
        self._write(formatted)

    def _prepare(self, data: list) -> list:
        return [d for d in data if d is not None]  # default

    @abstractmethod
    def _format(self, data: list) -> str: ...

    @abstractmethod
    def _write(self, content: str) -> None: ...

class CSVExporter(DataExporter):
    def _format(self, data):
        return "\n".join(",".join(str(v) for v in row) for row in data)
    def _write(self, content):
        with open("output.csv", "w") as f: f.write(content)

class JSONExporter(DataExporter):
    def _format(self, data):
        import json
        return json.dumps(data, indent=2)
    def _write(self, content):
        with open("output.json", "w") as f: f.write(content)
```

**Real-world:** Test frameworks (setUp/tearDown), data pipelines, report generation.

---

## 5. Patterns in Distributed Systems

```
HTTP/gRPC client stub:    → Proxy pattern
                            Looks like a local object, calls remote service

Service discovery:        → Abstract Factory
                            Create correct client per environment (dev/staging/prod)

Circuit Breaker:          → State pattern
                            CLOSED → OPEN → HALF-OPEN based on failure rate

Retry + Backoff:          → Decorator
                            Wrap any callable with transparent retry behavior

Event Processing:         → Observer / Chain of Responsibility
                            Kafka consumer → validate → enrich → persist → notify

API Gateway:              → Facade
                            Single entry point routing to multiple services

Outbox Pattern:           → Command
                            Write to DB and outbox in one TX; worker executes later

CQRS:                     → Strategy
                            Different read strategy vs write strategy per path
```

---

## 6. Pattern Combinations in Real Systems

### E-Commerce Order System
```
Factory     → Create payment processor per provider
Builder     → Build complex Order with optional fields
Strategy    → Pricing, shipping cost, discount calculation
Observer    → Order events fan out to inventory, email, analytics
State       → Order lifecycle: pending → confirmed → shipped → delivered
Command     → Undo for cart operations; audit log
Chain       → HTTP middleware: auth → validate → rate-limit → business logic
Decorator   → Add logging, caching, retry to repositories
Facade      → OrderService hides inventory + payment + shipping coordination
```

### Notification System
```
Factory          → Create sender per channel (email, SMS, push, Slack)
Strategy         → Choose delivery channel based on priority / user preference
Observer         → Subscribe handlers to domain events
Decorator        → Add retry, fallback, deduplication behavior
Chain            → Filter pipeline (quiet hours → preferences → dedup → send)
Template Method  → Base sender (prepare → format → send → log)
```

---

## 7. Anti-Patterns

```
God Object:
  One class knows and does everything.
  Fix: SRP — split into focused, single-responsibility classes.

Anemic Domain Model:
  Classes with only getters/setters, no behavior ("data bags").
  Business logic lives in separate service classes.
  Fix: Put behavior where the data lives.

Golden Hammer:
  "We Kafka all the things" / "Everything is a microservice"
  Fix: Match tool to problem. Start simple. Measure first.

Premature Optimization:
  Over-engineering for 10M users when you have 100.
  Fix: Simplest design that works. Optimize measured bottlenecks.

Singleton Abuse:
  Using singletons as global variables everywhere.
  Makes testing impossible (can't swap implementations).
  Fix: Dependency injection. Accept interfaces, not singletons.

Shotgun Surgery:
  One change requires many small changes in many places.
  Fix: Consolidate related logic. Better encapsulation.

Primitive Obsession:
  Passing strings/ints everywhere instead of domain objects.
  Fix: Value objects (Email, Money, OrderId instead of str/float/int).

Magic Numbers:
  Hard-coded timeouts, limits, thresholds.
  Fix: Named constants or configuration.
```

---

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ← Previous | [17 — Low Level Design](../17_low_level_design/theory.md) |
| ➡️ Next | [19 — Clean Architecture](../19_clean_architecture/theory.md) |
| 🏠 Home | [README.md](../README.md) |
