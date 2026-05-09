<a id="top"></a>

# Clean Architecture

> How to structure code so business logic stays independent of frameworks,
> databases, and delivery mechanisms. Covers layered architecture, hexagonal,
> Clean Architecture, and Domain-Driven Design (DDD).

*Leela is a Telugu architect who obsesses over clean boundaries. She treats every codebase like a well-designed temple — the sanctum (domain logic) must never be polluted by the outer walls (frameworks, databases). Her mantra: "If your business logic needs a database to run, you have already lost."*

## 📖 Table of Contents

- [1. Why Architecture Matters](#1-why-architecture-matters)
- [2. Layered (N-Tier) Architecture](#2-layered-n-tier-architecture)
  - [Layered Architecture in Code](#layered-architecture-in-code)
- [3. Hexagonal Architecture (Ports and Adapters)](#3-hexagonal-architecture-ports-and-adapters)
  - [Testing Benefit of Hexagonal](#testing-benefit-of-hexagonal)
- [4. Clean Architecture (Uncle Bob)](#4-clean-architecture-uncle-bob)
  - [The Four Layers](#the-four-layers)
- [5. Domain-Driven Design (DDD) Overview](#5-domain-driven-design-ddd-overview)
- [6. Bounded Contexts](#6-bounded-contexts)
  - [Context Map Relationships](#context-map-relationships)
- [7. Aggregates, Entities, Value Objects](#7-aggregates-entities-value-objects)
  - [Value Object](#value-object)
  - [Entity](#entity)
  - [Aggregate](#aggregate)
- [8. Repository Pattern](#8-repository-pattern)
- [9. CQRS as Architectural Pattern](#9-cqrs-as-architectural-pattern)
- [10. Choosing an Architecture](#10-choosing-an-architecture)
- [Summary](#summary)

## Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
dependency rule, layered vs hexagonal vs Clean Architecture, domain-centric design

**Should Learn** — Important for real projects, comes up regularly:
DDD tactical patterns (Aggregates/Value Objects/Entities), bounded contexts, repository pattern

**Good to Know** — Useful in specific situations, not always tested:
architecture selection criteria, anti-corruption layer, CQRS as architectural pattern

**Reference** — Know it exists, look up syntax when needed:
cyclic dependency detection, DTO mapping, legacy integration patterns

<a id="1-why-architecture-matters"></a>

# 1. Why Architecture Matters

Leela once inherited a codebase where changing a database column required editing 47 files. "It was like rewiring the entire temple just to replace one lamp," she recalls. The business logic was tangled with SQL queries, HTTP handlers, and email sending code — all in the same functions. That experience taught her the value of architectural boundaries.

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

  UI --> Application --> Domain <-- (knows nothing about UI/DB)
  DB adapters --> Domain <-- (knows nothing about DB)
```

```
Leela's analogy — The Temple Layers:

  Outer courtyard (anyone enters)   = Frameworks, UI, HTTP
  Inner hall (restricted)            = Application services
  Sanctum (purest core)             = Domain / Business rules

  Rule: The sanctum NEVER reaches out to the courtyard.
        The courtyard knows about the sanctum's interface,
        but the sanctum doesn't know the courtyard exists.
```

> [↑ Back to Top](#top)

<a id="2-layered-n-tier-architecture"></a>

# 2. Layered (N-Tier) Architecture

"Think of a four-story building," Leela explains to her juniors. "Each floor has a specific purpose — ground floor reception, second floor offices, third floor management, basement is storage. People on each floor only talk to the floor directly above or below them. That is layered architecture."

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
Presentation --> Application (OK)
Application  --> Domain     (OK)
Domain       --> Nothing    (pure)
Infrastructure --> Domain   (implements domain interfaces)

Presentation --> Domain     (bypassing application — debated, OK for reads)
Domain       --> Infrastructure (NEVER — inversion of control)
```

<a id="layered-architecture-in-code"></a>

## Layered Architecture in Code

Leela demonstrates with a real e-commerce order flow — the domain layer knows nothing about SQL or HTTP:

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

```
Common mistake — leaking infrastructure into domain:

  WRONG: class Order:
             def save(self):
                 db.session.add(self)  # domain knows about DB!

  RIGHT: class Order:
             # pure domain — no DB awareness
             def confirm(self): ...

         class SQLRepo(OrderRepository):
             def save(self, order): ...  # infrastructure handles persistence
```

> [↑ Back to Top](#top)

<a id="3-hexagonal-architecture-ports-and-adapters"></a>

# 3. Hexagonal Architecture (Ports and Adapters)

Leela uses a kitchen analogy: "Imagine a chef in a rental kitchen. The chef defines what equipment she needs — an oven, a sink, a fridge (these are ports). She does not care which brand provides them. You can swap the Samsung fridge for an LG — the recipes do not change. The chef's recipes are the business logic; the equipment brands are the adapters."

Alistair Cockburn (2005). Also called "Ports and Adapters."

```
          ┌─────────────────────────────────┐
          │                                 │
  HTTP ──>│  Port (InputPort interface)     │
  CLI ───>│  |                              │
  Tests ─>│  APPLICATION CORE               │<── Port (OutputPort interface) <── MySQL
          │  (Business Logic + Domain)      │<── Port (OutputPort interface) <── Redis
          │                                 │<── Port (OutputPort interface) <── SMTP
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

<a id="testing-benefit-of-hexagonal"></a>

## Testing Benefit of Hexagonal

"The real payoff," Leela says, "is that your tests run in milliseconds. No Docker containers, no test databases, no network calls. Just pure logic being verified."

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

```
Hexagonal vs Layered — When to choose which:

  Layered Architecture          Hexagonal Architecture
  ─────────────────────         ──────────────────────
  Simpler mental model          Explicit port/adapter contracts
  Good for CRUD apps            Good for complex domains
  1 delivery mechanism          Multiple delivery mechanisms
  Team knows the pattern        Testability is critical
  Quick to build                Long-lived systems
```

> [↑ Back to Top](#top)

<a id="4-clean-architecture-uncle-bob"></a>

# 4. Clean Architecture (Uncle Bob)

Leela describes it as "concentric circles — like a fortress with multiple walls. The innermost chamber holds the crown jewels (your entities). Each outer wall provides protection but knows nothing about what lies deeper inside. Robert C. Martin formalized this in 2012."

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

<a id="the-four-layers"></a>

## The Four Layers

```
Entities:       Core business objects + enterprise-wide rules
                These exist in the domain of the business.
                Example: Order, Customer, Money, Invoice

Use Cases:      Application-specific business rules
                Orchestrate entities to fulfill user goals.
                Example: PlaceOrder, CancelOrder, ProcessRefund

Interface Adapters: Convert data between use cases and frameworks
                    Controllers (HTTP --> use case command)
                    Presenters (use case response --> HTTP/JSON)
                    Repositories (use case interface --> DB query)

Frameworks:     Web frameworks, databases, UI, external services
                The most volatile — should be swappable
```

```
Leela's decision flow — "Which layer does this code belong to?"

  Does it express a business rule that exists
  even without software?
       YES --> Entities

  Does it orchestrate entities to fulfill a
  specific user story?
       YES --> Use Cases

  Does it translate between the outside world
  and the use case format?
       YES --> Interface Adapters

  Is it a specific technology (Django, Postgres,
  Redis, SMTP)?
       YES --> Frameworks & Drivers
```

> [↑ Back to Top](#top)

<a id="5-domain-driven-design-ddd-overview"></a>

# 5. Domain-Driven Design (DDD) Overview

"Before writing code," Leela tells her team, "talk to the domain experts for a week. If you are building banking software, sit with bankers. If e-commerce, sit with merchants. The words THEY use should become your class names. That is the essence of DDD — the code mirrors the business, not the other way around."

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

```
Strategic vs Tactical DDD — When you need each:

  Strategic (bounded contexts, context maps):
    Use when: system has multiple sub-domains, teams > 5 devs
    Skip when: single team, single model is sufficient

  Tactical (entities, value objects, aggregates):
    Use when: complex business rules, not just CRUD
    Skip when: simple data entry, thin logic layer
```

> [↑ Back to Top](#top)

<a id="6-bounded-contexts"></a>

# 6. Bounded Contexts

Leela uses a family analogy: "In my family, 'account' means a bank savings account. In my husband's IT company, 'account' means a customer they service. Same word, completely different meaning depending on context. Bounded contexts make this explicit in code — each context owns its own definition of shared terms."

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

<a id="context-map-relationships"></a>

## Context Map Relationships

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

```
Common mistake — Shared Database:

  WRONG: Orders BC and Payments BC both read/write
         the same "products" table directly.
         Result: coupling, cascading schema changes.

  RIGHT: Each BC owns its DB. Communication happens
         through events or well-defined APIs.
         Result: independent deployability.
```

> [↑ Back to Top](#top)

<a id="7-aggregates-entities-value-objects"></a>

# 7. Aggregates, Entities, Value Objects

Leela explains the distinction with a simple analogy: "A person (entity) has identity — even if they change their name or address, they are still the same person. A 100-rupee note (value object) has no identity — any 100-rupee note is interchangeable. An aggregate is like a family unit — the parents are the root, and you interact with the family through the parents, not by reaching in to talk to their children directly."

<a id="value-object"></a>

## Value Object

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

<a id="entity"></a>

## Entity

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

```
Entity vs Value Object — Quick decision:

  Question                         Entity    Value Object
  ──────────────────────────────   ──────    ────────────
  Does it have a lifecycle?        Yes       No
  Can two instances be swapped?    No        Yes
  Is equality based on ID?         Yes       No (by value)
  Is it mutable?                   Usually   Never
  Example                          Customer  Money, Address
```

<a id="aggregate"></a>

## Aggregate

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

```
Aggregate design rules:

  1. Keep aggregates SMALL — prefer one entity + value objects
  2. Reference other aggregates by ID, not by object reference
  3. One transaction = one aggregate (consistency boundary)
  4. Use domain events for cross-aggregate communication
  5. The aggregate root is the ONLY entry point for modifications
```

> [↑ Back to Top](#top)

<a id="8-repository-pattern"></a>

# 8. Repository Pattern

"Think of a repository like a library catalog," Leela says. "You ask the catalog for a book by title or author. You do not need to know whether the library uses Dewey Decimal, shelves, or a digital scanner to find it. The catalog is the interface; the physical library is the implementation."

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

```
Repository pattern — common mistakes:

  WRONG: Repository returns ORM models to the application layer
         (leaks infrastructure details upward)

  RIGHT: Repository converts ORM models to domain objects internally
         (application layer only sees domain types)

  WRONG: Repository has business logic (filtering by status, validation)
         (that belongs in the domain layer)

  RIGHT: Repository only does CRUD — find, save, delete
         (business logic lives in domain services/entities)
```

> [↑ Back to Top](#top)

<a id="9-cqrs-as-architectural-pattern"></a>

# 9. CQRS as Architectural Pattern

"In a restaurant," Leela explains, "placing an order goes through the kitchen (complex, stateful, validated). But checking the menu? That is a simple read from a printed card. You would never route menu-browsing through the kitchen. CQRS applies the same idea — separate the write path (complex) from the read path (simple, optimized)."

Separate read model from write model at architectural level.

```
Write side (Commands):
  HTTP POST /orders
       |
  PlaceOrderHandler (command handler)
       |
  Order aggregate (domain logic + validation)
       |
  OrderRepository.save() --> write DB + events

Read side (Queries):
  HTTP GET /orders/{id}
       |
  GetOrderQueryHandler
       |
  Read-optimized view (denormalized, may be different DB)
  Returns DTO (no domain logic, just data)

Read model built from events:
  OrderConfirmed event --> update order_summary table
  OrderShipped event   --> update order_summary table

  Read model optimized for query: flat, indexed, pre-joined
  Write model optimized for invariants: normalized, validated

Benefits:
  + Read and write models can evolve independently
  + Read model can be scaled separately (read replicas, caching)
  + Complex queries don't need to go through domain model
  + Event sourcing fits naturally (events --> rebuild read model)

Costs:
  - Eventual consistency (read model may lag)
  - More code (separate read/write paths)
  - More complexity

Use when: different scale needs for reads vs writes, complex domains
```

```
CQRS decision matrix:

  Situation                              CQRS?
  ────────────────────────────────────   ─────
  Simple CRUD app, reads ~ writes        No
  Read-heavy app (100:1 read:write)      Yes — read model can be cached
  Complex write validation + simple UI   Yes — separate concerns
  Multiple read formats (API, report)    Yes — multiple read models
  Audit trail / event replay needed      Yes — pairs with event sourcing
  Small team, simple domain              No — overhead not justified
```

> [↑ Back to Top](#top)

<a id="10-choosing-an-architecture"></a>

# 10. Choosing an Architecture

"There is no single best architecture," Leela concludes. "It depends on your team size, domain complexity, and how long the system will live. Starting with hexagonal for a weekend hackathon is over-engineering. Starting with a big-ball-of-mud for a banking system is negligence. Know where you are on the spectrum."

```
Start with: Layered Architecture
  Simple, well-understood, works for most applications.
  Teams understand it without explanation.
  Good for: CRUD-heavy apps, small-medium teams.

Upgrade to: Hexagonal + Clean Architecture
  When: you need testability, multiple delivery mechanisms (HTTP + CLI + tests),
        or need to swap infrastructure (MySQL --> Postgres, SMTP --> SendGrid).
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
```

```
Decision matrix:

  Simple app, small team:               --> Layered, 3-tier
  Testability needed, medium complexity: --> Hexagonal
  Complex domain logic:                  --> Clean + DDD Tactical
  Large system, many teams:             --> Bounded Contexts + DDD Strategic
  High read/write asymmetry:            --> Add CQRS
  Audit trail, event replay needed:     --> Event Sourcing
```

```
Architecture evolution path (most systems follow this):

  Startup Phase:      Monolith + Layered Architecture
                      (move fast, single deploy, shared DB)
                          |
  Growth Phase:       Modular Monolith + DDD
                      (bounded contexts within monolith)
                          |
  Scale Phase:        Microservices + Hexagonal + CQRS
                      (independent deploy, separate DBs)
                          |
  Maturity Phase:     Event-Driven + Event Sourcing
                      (full audit trail, async communication)
```

> [↑ Back to Top](#top)

<a id="summary"></a>

## 🔥 Summary

```
Architecture Patterns at a Glance:

  Pattern                Key Idea                      When to Use
  ─────────────────────  ────────────────────────────  ──────────────────────
  Layered (N-Tier)       Vertical stack of layers      Simple/medium apps
  Hexagonal (Ports)      Core + replaceable adapters   Testability critical
  Clean Architecture     Concentric dependency rule    Long-lived systems
  DDD Tactical           Rich domain model             Complex business rules
  DDD Strategic          Bounded contexts              Multi-team systems
  CQRS                   Separate read/write paths     Read/write asymmetry
  Repository Pattern     Abstract data access          Any layered system

Leela's golden rules:
  1. Dependencies always point INWARD
  2. Domain layer has ZERO external imports
  3. Infrastructure implements domain interfaces (not the reverse)
  4. Start simple, add complexity only when earned
  5. If you can't test business logic without a database, refactor
```

## 📂 Navigation

| | |
|---|---|
| 📘 README | [Back to System Design README](../README.md) |

| ⬅ Previous | ➡ Next |
|---|---|
| [18 — Design Patterns](../18_design_patterns/theory.md) | [20 — Data Systems](../20_data_systems/theory.md) |

**This folder:** [theory.md](./theory.md) | [cheetsheet.md](./cheetsheet.md) | [interview.md](./interview.md) | [practice_local.py](./practice_local.py)

**Related modules:** [04 — Backend Architecture](../04_backend_architecture/theory.md) | [12 — Microservices](../12_microservices/theory.md) | [18 — Design Patterns](../18_design_patterns/theory.md) | [17 — Low Level Design](../17_low_level_design/theory.md)

**Jump to topics:** [Hexagonal Architecture](#3-hexagonal-architecture-ports-and-adapters) | [DDD Overview](#5-domain-driven-design-ddd-overview) | [Repository Pattern](#8-repository-pattern) | [CQRS](#9-cqrs-as-architectural-pattern)
