"""
05_oops/real_world_examples.py
================================
CONCEPT: Real-world OOP systems that combine all patterns together.
WHY THIS MATTERS: Interviews and real projects don't test patterns in isolation.
They test whether you can design a system. These examples model the kinds of
systems you'd build in actual jobs.

Prerequisite: 05_oops/practice.py, advanced_practice.py, design_patterns.py
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import datetime
import uuid

# =============================================================================
# EXAMPLE 1: E-commerce order system
# =============================================================================

# WHY THIS DESIGN: Shows encapsulation (order state is controlled through
# methods), inheritance (different order types), and status state machine.

print("=== Example 1: E-Commerce Order System ===")

class OrderStatus:
    """Enumeration of valid order states."""
    PENDING    = "pending"
    CONFIRMED  = "confirmed"
    SHIPPED    = "shipped"
    DELIVERED  = "delivered"
    CANCELLED  = "cancelled"
    REFUNDED   = "refunded"

    # Define valid transitions: from_status → set of allowed next statuses
    TRANSITIONS = {
        PENDING:   {CONFIRMED, CANCELLED},
        CONFIRMED: {SHIPPED, CANCELLED},
        SHIPPED:   {DELIVERED},
        DELIVERED: {REFUNDED},
        CANCELLED: set(),
        REFUNDED:  set(),
    }

    @classmethod
    def can_transition(cls, current: str, new: str) -> bool:
        return new in cls.TRANSITIONS.get(current, set())


@dataclass
class OrderItem:
    product_id: str
    name: str
    unit_price: float
    quantity: int

    @property
    def subtotal(self) -> float:
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.name} × {self.quantity} = ${self.subtotal:.2f}"


class Order:
    """
    An order that transitions through valid states.
    State machine pattern: only valid transitions are allowed.
    WHY: Prevents impossible states like "shipped but not confirmed first."
    """

    def __init__(self, customer_id: str):
        self.order_id = str(uuid.uuid4())[:8]   # short ID for readability
        self.customer_id = customer_id
        self._items: list[OrderItem] = []
        self._status = OrderStatus.PENDING
        self.created_at = datetime.datetime.utcnow()
        self._history: list[tuple] = [(OrderStatus.PENDING, self.created_at)]

    def add_item(self, product_id: str, name: str, price: float, qty: int) -> "Order":
        """Returns self for fluent/chaining API."""
        if self._status != OrderStatus.PENDING:
            raise ValueError(f"Cannot add items to a {self._status} order")
        self._items.append(OrderItem(product_id, name, price, qty))
        return self   # enables method chaining

    def _transition(self, new_status: str) -> None:
        """Enforce state machine rules."""
        if not OrderStatus.can_transition(self._status, new_status):
            raise ValueError(
                f"Invalid transition: {self._status} → {new_status}"
            )
        self._status = new_status
        self._history.append((new_status, datetime.datetime.utcnow()))

    def confirm(self):   self._transition(OrderStatus.CONFIRMED)
    def ship(self):      self._transition(OrderStatus.SHIPPED)
    def deliver(self):   self._transition(OrderStatus.DELIVERED)
    def cancel(self):    self._transition(OrderStatus.CANCELLED)
    def refund(self):    self._transition(OrderStatus.REFUNDED)

    @property
    def status(self) -> str:
        return self._status

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self._items)

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self._items)

    def summary(self) -> str:
        lines = [
            f"Order #{self.order_id} | Status: {self.status.upper()}",
            f"Customer: {self.customer_id} | Items: {self.item_count}",
        ]
        for item in self._items:
            lines.append(f"  {item}")
        lines.append(f"  TOTAL: ${self.total:.2f}")
        return "\n".join(lines)

    def audit_trail(self) -> str:
        lines = [f"Order #{self.order_id} audit trail:"]
        for status, timestamp in self._history:
            lines.append(f"  {timestamp.strftime('%H:%M:%S')} → {status}")
        return "\n".join(lines)


# Build and process an order
order = (Order("customer-42")
         .add_item("PROD-001", "Laptop Stand", 29.99, 1)
         .add_item("PROD-002", "USB Hub", 19.99, 2)
         .add_item("PROD-003", "Mouse Pad", 9.99, 1))

print(order.summary())
print()

order.confirm()
print(f"Status after confirm: {order.status}")

order.ship()
print(f"Status after ship: {order.status}")

# Try invalid transition
try:
    order.cancel()   # can't cancel a shipped order
except ValueError as e:
    print(f"Invalid transition blocked: {e}")

order.deliver()
print(f"\n{order.audit_trail()}")


# =============================================================================
# EXAMPLE 2: Plugin system with registry
# =============================================================================

# WHY THIS DESIGN: Shows how frameworks like Flask, pytest, and Django load
# extensions. The registry pattern + abstract base class = open-ended extensibility.

print("\n=== Example 2: Plugin/Extension System ===")

class DataTransformer(ABC):
    """Base for all data transformation plugins."""

    @abstractmethod
    def transform(self, data: list) -> list:
        ...

    @abstractmethod
    def name(self) -> str:
        ...


class TransformerRegistry:
    """Registry for all available transformers. Plugins self-register."""

    _transformers: dict[str, type] = {}

    @classmethod
    def register(cls, transformer_class: type) -> type:
        """
        Decorator that registers a transformer class.
        Use as: @TransformerRegistry.register
        Returns the class unchanged — pure registration side effect.
        """
        instance = transformer_class()
        cls._transformers[instance.name()] = transformer_class
        return transformer_class

    @classmethod
    def get(cls, name: str) -> "DataTransformer":
        if name not in cls._transformers:
            raise KeyError(f"Unknown transformer: {name}. Available: {list(cls._transformers)}")
        return cls._transformers[name]()

    @classmethod
    def available(cls) -> list[str]:
        return list(cls._transformers.keys())


@TransformerRegistry.register
class UpperCaseTransformer(DataTransformer):
    def name(self): return "uppercase"
    def transform(self, data): return [str(x).upper() for x in data]

@TransformerRegistry.register
class DeduplicateTransformer(DataTransformer):
    def name(self): return "deduplicate"
    def transform(self, data): return list(dict.fromkeys(data))   # order-preserving

@TransformerRegistry.register
class SortTransformer(DataTransformer):
    def name(self): return "sort"
    def transform(self, data): return sorted(data)


# Pipeline that applies transformers by name
class Pipeline:
    def __init__(self, steps: list[str]):
        self._steps = [TransformerRegistry.get(name) for name in steps]

    def run(self, data: list) -> list:
        for step in self._steps:
            data = step.transform(data)
        return data


raw_data = ["banana", "apple", "cherry", "banana", "apple", "mango"]
print(f"Raw data: {raw_data}")
print(f"Available transformers: {TransformerRegistry.available()}")

pipeline = Pipeline(["deduplicate", "sort", "uppercase"])
result = pipeline.run(raw_data)
print(f"After pipeline: {result}")


# =============================================================================
# EXAMPLE 3: Repository pattern — abstract data access
# =============================================================================

# WHY THIS DESIGN: Separates business logic from data storage.
# Tests use InMemoryRepository. Production uses a real DB.
# Switching storage backends doesn't touch any business logic.

print("\n=== Example 3: Repository Pattern ===")

@dataclass
class User:
    name: str
    email: str
    role: str = "user"
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email, "role": self.role}


class UserRepository(ABC):
    """Abstract data access layer — business logic depends on THIS interface."""

    @abstractmethod
    def save(self, user: User) -> User: ...

    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]: ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    def find_all(self) -> list[User]: ...

    @abstractmethod
    def delete(self, user_id: str) -> bool: ...


class InMemoryUserRepository(UserRepository):
    """In-memory implementation for testing."""

    def __init__(self):
        self._users: dict[str, User] = {}

    def save(self, user: User) -> User:
        self._users[user.id] = user
        return user

    def find_by_id(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def find_by_email(self, email: str) -> Optional[User]:
        return next((u for u in self._users.values() if u.email == email), None)

    def find_all(self) -> list[User]:
        return list(self._users.values())

    def delete(self, user_id: str) -> bool:
        return bool(self._users.pop(user_id, None))


class UserService:
    """
    Business logic — depends only on the abstract UserRepository interface.
    Can be tested with InMemoryUserRepository, deployed with SQL/NoSQL.
    """

    def __init__(self, repository: UserRepository):
        self._repo = repository   # inject the dependency!

    def register(self, name: str, email: str) -> User:
        # Business rule: no duplicate emails
        if self._repo.find_by_email(email):
            raise ValueError(f"Email already registered: {email}")
        user = User(name=name, email=email)
        return self._repo.save(user)

    def get_user(self, user_id: str) -> User:
        user = self._repo.find_by_id(user_id)
        if not user:
            raise KeyError(f"User not found: {user_id}")
        return user

    def list_users(self) -> list[dict]:
        return [u.to_dict() for u in self._repo.find_all()]

    def remove_user(self, user_id: str) -> None:
        if not self._repo.delete(user_id):
            raise KeyError(f"User not found: {user_id}")


# Wire together using in-memory repo (production would use a DB repo)
repo    = InMemoryUserRepository()
service = UserService(repo)

alice = service.register("Alice", "alice@example.com")
bob   = service.register("Bob",   "bob@example.com")
carol = service.register("Carol", "carol@example.com")

print(f"Registered users: {[u['name'] for u in service.list_users()]}")

# Business rule enforcement
try:
    service.register("Alice Duplicate", "alice@example.com")
except ValueError as e:
    print(f"Duplicate email blocked: {e}")

alice_found = service.get_user(alice.id)
print(f"Found user: {alice_found.name} ({alice_found.email})")

service.remove_user(bob.id)
print(f"After removing Bob: {[u['name'] for u in service.list_users()]}")


print("\n=== Real-world OOP examples complete ===")
print("Key design principles demonstrated:")
print("  1. Encapsulation: Order state changed ONLY through methods (not directly)")
print("  2. State machines: only valid status transitions allowed")
print("  3. Registry + decorator: plugins self-register, extensible without changes")
print("  4. Repository pattern: business logic is independent of storage backend")
print("  5. Dependency injection: service gets its repo — easy to test and swap")
