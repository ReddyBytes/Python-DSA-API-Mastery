# 🧹 Clean Architecture

> How to structure code so business logic stays independent of frameworks,
> databases, and delivery mechanisms. Covers layered architecture, hexagonal,
> Clean Architecture, and Domain-Driven Design (DDD).

---

## 📋 Contents

```
1.  Why architecture matters
2.  Layered (N-Tier) architecture
3.  Hexagonal architecture (ports & adapters)
4.  Clean architecture (Uncle Bob)
5.  Domain-Driven Design (DDD) overview
6.  Bounded contexts
7.  Aggregates, entities, value objects
8.  Repository pattern
9.  CQRS as architectural pattern
10. Choosing an architecture
```

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
dependency rule · layered vs hexagonal vs Clean Architecture · domain-centric design

**Should Learn** — Important for real projects, comes up regularly:
DDD tactical patterns (Aggregates/Value Objects/Entities) · bounded contexts · repository pattern

**Good to Know** — Useful in specific situations, not always tested:
architecture selection criteria · anti-corruption layer · CQRS as architectural pattern

**Reference** — Know it exists, look up syntax when needed:
cyclic dependency detection · DTO mapping · legacy integration patterns

---

## 1. Why Architecture Matters

```
Bad architecture symptoms:
  - "I can't test this without a database"
  - "Changing the DB breaks the business logic"
  - "To add a feature I have to touch 10 files"
  - "Nobody understands what this service does"
  - "The framework is everywhere — can't replace it"

Good architecture:
  + Business logic can be tested without any infrastructure
  + Database, framework, UI are swappable with minimal impact
  + New developers understand boundaries quickly
  + Changes are localized — modify one layer, others unaffected
```

The fundamental principle:
```
Dependency Rule:
  Source code dependencies must point INWARD only.
  Outer layers depend on inner layers.
  Inner layers know NOTHING about outer layers.

  UI → Application → Domain ← (knows nothing about UI/DB)
  DB adapters → Domain ← (knows nothing about DB)
```

---

## 2. Layered (N-Tier) Architecture

The classic approach. Most codebases use some form of this.

```
┌─────────────────────────────────────┐
│         Presentation Layer          │  HTTP controllers, CLI, GraphQL resolvers
│         (Controllers/Views)         │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│         Application Layer           │  Use cases, orchestration, DTOs
│         (Services/Use Cases)        │  No business rules here — coordinates
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│          Domain Layer               │  Business rules, entities, value objects
│      (Entities/Business Rules)      │  Pure Python — zero dependencies
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│       Infrastructure Layer          │  DB, cache, email, external APIs
│   (Repositories/Adapters/ORM)       │  Implements domain interfaces
└─────────────────────────────────────┘
```

**Rules:**
```
Presentation → Application (OK)
Application  → Domain     (OK)
Domain       → Nothing    (pure)
Infrastructure → Domain   (implements domain interfaces)

Presentation → Domain     (bypassing application — debated, OK for reads)
Domain       → Infrastructure (NEVER — inversion of control)
```

**In code:**
```python
# Domain layer — pure business logic, no imports from outer layers
class Order:
    def __init__(self, order_id: str, customer_id: str):
        self.id = order_id
        self.customer_id = customer_id
        self._items: list[OrderItem] = []
        self.status = OrderStatus.PENDING

    def add_item(self, product_id: str, quantity: int, price: Money) -> None:
        if self.status != OrderStatus.PENDING:
            raise DomainError("Cannot modify confirmed order")
        self._items.append(OrderItem(product_id, quantity, price))

    def confirm(self) -> None:
        if not self._items:
            raise DomainError("Cannot confirm empty order")
        self.status = OrderStatus.CONFIRMED
        self._events.append(OrderConfirmedEvent(self.id))

# Application layer — orchestrates, no business rules
class PlaceOrderUseCase:
    def __init__(self, repo: OrderRepository, emailer: Emailer):
        self._repo = repo
        self._emailer = emailer

    def execute(self, command: PlaceOrderCommand) -> OrderId:
        order = Order(generate_id(), command.customer_id)
        for item in command.items:
            order.add_item(item.product_id, item.quantity, item.price)
        order.confirm()
        self._repo.save(order)
        self._emailer.send_confirmation(order)
        return order.id

# Infrastructure layer — implements domain interfaces
class SQLOrderRepository(OrderRepository):
    def __init__(self, session):
        self._session = session

    def save(self, order: Order) -> None:
        self._session.add(OrderModel.from_domain(order))
        self._session.commit()
```

---

## 3. Hexagonal Architecture (Ports & Adapters)

Alistair Cockburn (2005). Also called "Ports and Adapters."

```
          ┌─────────────────────────────────┐
          │                                 │
  HTTP ──→│  Port (InputPort interface)     │
  CLI ───→│  ↓                              │
  Tests ─→│  APPLICATION CORE               │←── Port (OutputPort interface) ←── MySQL
          │  (Business Logic + Domain)      │←── Port (OutputPort interface) ←── Redis
          │                                 │←── Port (OutputPort interface) ←── SMTP
          └─────────────────────────────────┘

Left side (Driving/Primary):
  Adapters that DRIVE the application (HTTP, CLI, tests)
  They call the application's input ports (interfaces)

Right side (Driven/Secondary):
  Adapters that the application DRIVES (DB, email, queue)
  They implement the application's output ports (interfaces)
```

**Key insight:** The application core defines interfaces (ports).
Adapters on the outside implement or use those interfaces.
The core has zero knowledge of adapters.

```python
# Input port — driven by HTTP adapter
class OrderService(Protocol):
    def place_order(self, command: PlaceOrderCommand) -> OrderId: ...
    def get_order(self, order_id: OrderId) -> OrderDTO: ...

# Output ports — implemented by infrastructure adapters
class OrderRepository(Protocol):
    def save(self, order: Order) -> None: ...
    def find_by_id(self, order_id: OrderId) -> Order | None: ...

class PaymentGateway(Protocol):
    def charge(self, customer_id: str, amount: Money) -> ChargeId: ...

# Core — knows only about its own ports
class OrderServiceImpl:
    def __init__(self, repo: OrderRepository, payments: PaymentGateway):
        self._repo = repo
        self._payments = payments

    def place_order(self, command: PlaceOrderCommand) -> OrderId:
        order = Order.create(command.customer_id, command.items)
        charge = self._payments.charge(command.customer_id, order.total)
        order.attach_charge(charge)
        self._repo.save(order)
        return order.id

# HTTP adapter — primary (driving)
class OrderHTTPAdapter:
    def __init__(self, service: OrderService):
        self._service = service

    def post_order(self, request):
        command = PlaceOrderCommand.from_request(request)
        order_id = self._service.place_order(command)
        return {"order_id": str(order_id)}, 201

# DB adapter — secondary (driven)
class PostgresOrderRepository(OrderRepository):
    def save(self, order: Order) -> None: ...
    def find_by_id(self, order_id: OrderId) -> Order | None: ...

# Fake adapter — for testing (also secondary)
class InMemoryOrderRepository(OrderRepository):
    def __init__(self): self._store: dict = {}
    def save(self, order): self._store[order.id] = order
    def find_by_id(self, order_id): return self._store.get(order_id)
```

**Testing benefit:**
```python
# Test with in-memory adapters — no DB, no HTTP, no email
def test_place_order():
    repo = InMemoryOrderRepository()
    payments = FakePaymentGateway(always_succeeds=True)
    service = OrderServiceImpl(repo, payments)

    order_id = service.place_order(PlaceOrderCommand(...))

    order = repo.find_by_id(order_id)
    assert order.status == OrderStatus.CONFIRMED
```

---

## 4. Clean Architecture (Uncle Bob)

Robert C. Martin's formalization. Concentric circles.

```
              ┌─────────────────────────────┐
              │        Frameworks           │  Spring, Django, Rails
              │  & Drivers                  │  MySQL, Redis, HTTP
              │   ┌─────────────────────┐   │
              │   │  Interface Adapters  │   │  Controllers, Presenters
              │   │   ┌─────────────┐   │   │  Gateways, Repositories
              │   │   │  Use Cases  │   │   │  (infrastructure code)
              │   │   │   ┌─────┐   │   │   │
              │   │   │   │Ent- │   │   │   │  Application Business Rules
              │   │   │   │ity  │   │   │   │
              │   │   │   └─────┘   │   │   │  Enterprise Business Rules
              │   │   └─────────────┘   │   │  (most stable, innermost)
              │   └─────────────────────┘   │
              └─────────────────────────────┘

Dependency Rule: dependencies point INWARD only
Entities are most stable — change least
Frameworks are most unstable — change most
```

**The four layers:**
```
Entities:       Core business objects + enterprise-wide rules
                These exist in the domain of the business.
                Example: Order, Customer, Money, Invoice

Use Cases:      Application-specific business rules
                Orchestrate entities to fulfill user goals.
                Example: PlaceOrder, CancelOrder, ProcessRefund

Interface Adapters: Convert data between use cases and frameworks
                    Controllers (HTTP → use case command)
                    Presenters (use case response → HTTP/JSON)
                    Repositories (use case interface → DB query)

Frameworks:     Web frameworks, databases, UI, external services
                The most volatile — should be swappable
```

---

## 5. Domain-Driven Design (DDD) Overview

DDD (Eric Evans, 2003) is both an analysis approach and architectural pattern.

```
Strategic DDD — dividing the problem:
  Ubiquitous Language:  Use domain expert's words in code
                        "Invoice", not "BillingDocument"
  Bounded Context:      Explicit boundary around a model
  Context Map:          How bounded contexts relate

Tactical DDD — building the solution:
  Entity:           Object with identity (Order, Customer)
  Value Object:     Defined by value, not identity (Money, Address)
  Aggregate:        Cluster of entities with one root (Order + OrderItems)
  Domain Event:     Something that happened (OrderPlaced, PaymentFailed)
  Repository:       Abstract collection of aggregates
  Domain Service:   Logic that doesn't belong to an entity
  Application Service: Orchestrates use cases (thin layer)
```

---

## 6. Bounded Contexts

A bounded context is an explicit boundary within which a domain model applies.

```
E-commerce system:

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   Catalog BC     │  │   Orders BC      │  │  Payments BC     │
│                  │  │                  │  │                  │
│ Product:         │  │ Product:         │  │ Payment:         │
│   id, name,      │  │   product_id,    │  │   amount,        │
│   description,   │  │   name, price    │  │   currency,      │
│   category,      │  │   (snapshot!)    │  │   method,        │
│   images, tags   │  │                  │  │   status         │
└──────────────────┘  └──────────────────┘  └──────────────────┘

"Product" means different things in each context!
  Catalog:  full product details, SEO, variants, images
  Orders:   snapshot of name + price at time of purchase
  Payments: just an amount to charge — no product concept

Key insight:
  Don't try to build one universal Product model.
  Let each context own its model.
  Communicate through events or APIs, not shared DB tables.
```

**Context Map relationships:**
```
Upstream / Downstream:
  Catalog publishes ProductUpdated events
  Orders consumes them (updates price snapshots)

Anti-Corruption Layer (ACL):
  If upstream is legacy/messy,
  add translation layer to protect your clean model

Shared Kernel:
  Two contexts share a small, explicitly co-owned part
  (dangerous — use sparingly)

Published Language:
  Upstream publishes a formal schema (OpenAPI, Protobuf)
  Downstream translates to its own model
```

---

## 7. Aggregates, Entities, Value Objects

### Value Object
Defined by its value, not identity. Immutable.

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)  # immutable!
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def multiply(self, factor: Decimal) -> "Money":
        return Money(self.amount * factor, self.currency)

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"

# Two Money objects with same value are equal — no identity needed
assert Money(Decimal("100"), "USD") == Money(Decimal("100"), "USD")
```

### Entity
Defined by identity, not value. Mutable.

```python
class Customer:
    def __init__(self, customer_id: str, name: str, email: str):
        self._id = customer_id  # identity
        self._name = name
        self._email = email

    @property
    def id(self) -> str:
        return self._id

    def change_email(self, new_email: str) -> None:
        self._validate_email(new_email)
        self._email = new_email

    def __eq__(self, other) -> bool:
        if not isinstance(other, Customer):
            return NotImplemented
        return self._id == other._id  # identity comparison!

    def _validate_email(self, email: str) -> None: ...
```

### Aggregate
A cluster of entities + value objects. One entity is the Aggregate Root.
All external access goes through the root. Root enforces invariants.

```python
class Order:  # Aggregate Root
    def __init__(self, order_id: str, customer_id: str):
        self._id = order_id
        self._customer_id = customer_id
        self._items: list[OrderItem] = []  # child entities
        self._status = OrderStatus.PENDING
        self._total = Money(Decimal("0"), "USD")
        self._domain_events: list = []

    def add_item(self, product_id: str, qty: int, price: Money) -> None:
        # Invariant: can only modify pending orders
        if self._status != OrderStatus.PENDING:
            raise DomainError("Order is already confirmed")
        # Invariant: max 100 items per order
        if len(self._items) >= 100:
            raise DomainError("Order cannot have more than 100 items")
        self._items.append(OrderItem(product_id, qty, price))
        self._total = self._total.add(price.multiply(Decimal(qty)))

    def confirm(self) -> None:
        if not self._items:
            raise DomainError("Cannot confirm empty order")
        self._status = OrderStatus.CONFIRMED
        self._domain_events.append(OrderConfirmedEvent(self._id, self._total))

    def pop_domain_events(self) -> list:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events

    # External code NEVER touches OrderItem directly
    # Only Order aggregate root exposes item operations
```

---

## 8. Repository Pattern

Abstract away data access. Domain knows the interface; infrastructure implements it.

```python
from abc import ABC, abstractmethod

class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: str) -> Order | None: ...

    @abstractmethod
    def find_by_customer(self, customer_id: str) -> list[Order]: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def delete(self, order_id: str) -> None: ...

# Infrastructure implementation:
class SQLAlchemyOrderRepository(OrderRepository):
    def __init__(self, session):
        self._session = session

    def find_by_id(self, order_id: str) -> Order | None:
        row = self._session.query(OrderRow).filter_by(id=order_id).first()
        return OrderMapper.to_domain(row) if row else None

    def save(self, order: Order) -> None:
        row = OrderMapper.to_row(order)
        self._session.merge(row)
        self._session.flush()

# Test implementation — in-memory, no DB needed
class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self._store: dict[str, Order] = {}

    def find_by_id(self, order_id: str) -> Order | None:
        return self._store.get(order_id)

    def find_by_customer(self, customer_id: str) -> list[Order]:
        return [o for o in self._store.values()
                if o.customer_id == customer_id]

    def save(self, order: Order) -> None:
        self._store[order.id] = order

    def delete(self, order_id: str) -> None:
        self._store.pop(order_id, None)
```

---

## 9. CQRS as Architectural Pattern

Separate read model from write model at architectural level.

```
Write side (Commands):
  HTTP POST /orders
       ↓
  PlaceOrderHandler (command handler)
       ↓
  Order aggregate (domain logic + validation)
       ↓
  OrderRepository.save() → write DB + events

Read side (Queries):
  HTTP GET /orders/{id}
       ↓
  GetOrderQueryHandler
       ↓
  Read-optimized view (denormalized, may be different DB)
  Returns DTO (no domain logic, just data)

Read model built from events:
  OrderConfirmed event → update order_summary table
  OrderShipped event   → update order_summary table

  Read model optimized for query: flat, indexed, pre-joined
  Write model optimized for invariants: normalized, validated

Benefits:
  + Read and write models can evolve independently
  + Read model can be scaled separately (read replicas, caching)
  + Complex queries don't need to go through domain model
  + Event sourcing fits naturally (events → rebuild read model)

Costs:
  - Eventual consistency (read model may lag)
  - More code (separate read/write paths)
  - More complexity

Use when: different scale needs for reads vs writes, complex domains
```

---

## 10. Choosing an Architecture

```
Start with: Layered Architecture
  Simple, well-understood, works for most applications.
  Teams understand it without explanation.
  Good for: CRUD-heavy apps, small-medium teams.

Upgrade to: Hexagonal + Clean Architecture
  When: you need testability, multiple delivery mechanisms (HTTP + CLI + tests),
        or need to swap infrastructure (MySQL → Postgres, SMTP → SendGrid).
  Good for: complex domains, long-lived systems, large teams.

Layer on: DDD Tactical Patterns
  When: complex business rules that don't map cleanly to CRUD.
  Use Value Objects, Aggregates, Domain Events.
  Good for: financial systems, complex e-commerce, healthcare.

Add: DDD Strategic Patterns (Bounded Contexts)
  When: system is large enough to have distinct sub-domains.
  Split into contexts: catalog, orders, payments, shipping.
  Each context has its own model, team, and deployment.
  Good for: large systems (>50 engineers), microservices.

Combine with: CQRS
  When: read and write load differ significantly,
        or you need multiple read models for different clients.
  Good for: high-traffic systems, analytics, multi-client APIs.

Decision matrix:
  Simple app, small team:               → Layered, 3-tier
  Testability needed, medium complexity: → Hexagonal
  Complex domain logic:                  → Clean + DDD Tactical
  Large system, many teams:              → Bounded Contexts + DDD Strategic
  High read/write asymmetry:             → Add CQRS
  Audit trail, event replay needed:      → Event Sourcing
```

---

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ← Previous | [18 — Design Patterns](../18_design_patterns/theory.md) |
| ➡️ Next | [20 — Data Systems](../20_data_systems/theory.md) |
| 🏠 Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Design Patterns — Interview Q&A](../18_design_patterns/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
