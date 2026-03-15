"""
05_oops/design_patterns.py
============================
CONCEPT: Classic OOP design patterns implemented in Pythonic style.
WHY THIS MATTERS: Design patterns are solutions to recurring design problems.
Knowing them means you can recognize them in codebases and apply them
when appropriate. Python's first-class functions and dynamic nature mean
many patterns look different (simpler) than their Java counterparts.

Prerequisite: 05_oops/practice.py, 05_oops/advanced_practice.py
"""

from abc import ABC, abstractmethod
from typing import Callable, Any

# =============================================================================
# PATTERN 1: Singleton — one instance only
# =============================================================================

# CONCEPT: Ensure a class has only ONE instance. Used for:
# - Database connection pools (one pool shared across all code)
# - Config managers (one source of truth)
# - Logger instances
# PYTHONIC: Module-level instances are a simpler Singleton alternative.
# Use the __new__ approach when you truly need class-level enforcement.

print("=== Pattern 1: Singleton ===")

class DatabasePool:
    """
    Connection pool — only ONE should exist for performance and correctness.
    Second call to DatabasePool() returns the SAME object as the first.
    """
    _instance = None   # class-level storage for the single instance

    def __new__(cls, *args, **kwargs):
        """
        __new__ creates the object. We override it to return the existing
        instance if one already exists instead of creating a new one.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance   # always return the same object

    def __init__(self, url: str = "postgres://localhost/mydb", pool_size: int = 10):
        if self._initialized:
            return   # already set up — don't re-initialize
        self.url = url
        self.pool_size = pool_size
        self._connections = []
        self._initialized = True
        print(f"  Pool created: {url} (size={pool_size})")

    def get_connection(self):
        return f"connection from {self.url}"


pool1 = DatabasePool("postgres://localhost/app", 5)
pool2 = DatabasePool("postgres://different-server/other", 20)   # ignored!

print(f"pool1 is pool2: {pool1 is pool2}")   # True — same object
print(f"pool2.url: {pool2.url}")             # Still the first URL
print(f"pool2.pool_size: {pool2.pool_size}") # Still 5


# =============================================================================
# PATTERN 2: Factory — create objects without specifying exact class
# =============================================================================

# CONCEPT: The factory pattern separates object creation from object use.
# Callers say WHAT they want, not HOW to build it.
# WHY: Adding a new product type means adding one block of code — not
# changing every place that creates objects.

print("\n=== Pattern 2: Factory ===")

class Notification(ABC):
    @abstractmethod
    def send(self, user: str, message: str) -> str:
        ...

class EmailNotification(Notification):
    def send(self, user: str, message: str) -> str:
        return f"[EMAIL] To: {user} | {message}"

class SMSNotification(Notification):
    def send(self, user: str, message: str) -> str:
        return f"[SMS] To: {user} | {message[:160]}"   # SMS character limit

class PushNotification(Notification):
    def send(self, user: str, message: str) -> str:
        return f"[PUSH] To: {user} | {message[:50]}"


class NotificationFactory:
    """
    Factory: takes a channel name string, returns the right Notification object.
    Callers write: factory.create("email").send(user, msg)
    Adding a new channel = adding one line to _registry.
    """
    _registry = {
        "email": EmailNotification,
        "sms":   SMSNotification,
        "push":  PushNotification,
    }

    @classmethod
    def create(cls, channel: str) -> Notification:
        creator = cls._registry.get(channel)
        if not creator:
            raise ValueError(f"Unknown channel: {channel}. Options: {list(cls._registry)}")
        return creator()

    @classmethod
    def register(cls, channel: str, notification_class: type):
        """Extend the factory without modifying it — Open/Closed principle."""
        cls._registry[channel] = notification_class


factory = NotificationFactory()
for channel in ["email", "sms", "push"]:
    notif = factory.create(channel)
    print(f"  {notif.send('Alice', 'Your order has shipped!')}")

# Registering a new type at runtime
class SlackNotification(Notification):
    def send(self, user: str, message: str) -> str:
        return f"[SLACK] @{user}: {message}"

NotificationFactory.register("slack", SlackNotification)
print(f"  {factory.create('slack').send('alice', 'Deployment complete')}")


# =============================================================================
# PATTERN 3: Observer — event-driven communication
# =============================================================================

# CONCEPT: The observer pattern decouples event publishers from their subscribers.
# The publisher (subject) doesn't know WHO is listening — it just fires events.
# Subscribers register themselves and handle events independently.
# Used in: event buses, UI frameworks, real-time dashboards, webhook systems.

print("\n=== Pattern 3: Observer ===")

class EventBus:
    """
    Simple event bus: components publish events, others subscribe.
    The publisher doesn't know or care who is listening — loose coupling.
    """

    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = {}

    def subscribe(self, event: str, handler: Callable) -> None:
        """Register a callback to be called when `event` is published."""
        self._subscribers.setdefault(event, []).append(handler)

    def unsubscribe(self, event: str, handler: Callable) -> None:
        if event in self._subscribers:
            self._subscribers[event] = [
                h for h in self._subscribers[event] if h is not handler
            ]

    def publish(self, event: str, **data) -> None:
        """Notify all subscribers of `event` with the given data."""
        for handler in self._subscribers.get(event, []):
            handler(**data)


# Components that react to events
bus = EventBus()

# Subscriber 1: email notifications
def send_welcome_email(user_id: int, email: str, **kwargs):
    print(f"  [EMAIL] Welcome email sent to {email}")

# Subscriber 2: analytics tracker
def track_signup(user_id: int, **kwargs):
    print(f"  [ANALYTICS] User {user_id} signup tracked")

# Subscriber 3: setup new user resources
def provision_user(user_id: int, **kwargs):
    print(f"  [PROVISIONING] Creating workspace for user {user_id}")

# Register all subscribers to the "user_registered" event
bus.subscribe("user_registered", send_welcome_email)
bus.subscribe("user_registered", track_signup)
bus.subscribe("user_registered", provision_user)

# Publisher — knows nothing about the 3 subscribers above
print("Publishing 'user_registered' event:")
bus.publish("user_registered", user_id=42, email="alice@example.com")

# Real-world: order system
def update_inventory(order_id: int, items: list, **kwargs):
    print(f"  [INVENTORY] Updated for order {order_id}")

def send_confirmation(order_id: int, **kwargs):
    print(f"  [CONFIRM] Email sent for order {order_id}")

def trigger_fulfillment(order_id: int, **kwargs):
    print(f"  [FULFILLMENT] Order {order_id} sent to warehouse")

bus.subscribe("order_placed", update_inventory)
bus.subscribe("order_placed", send_confirmation)
bus.subscribe("order_placed", trigger_fulfillment)

print("\nPublishing 'order_placed' event:")
bus.publish("order_placed", order_id=1001, items=["widget", "gadget"])


# =============================================================================
# PATTERN 4: Strategy — swappable algorithms
# =============================================================================

# CONCEPT: Define a family of algorithms, put each in its own class,
# and make them interchangeable. The context uses a strategy without
# knowing which one it is. Changing behavior = swapping the strategy object.
# Used in: sorting, pricing engines, authentication, payment processing.

print("\n=== Pattern 4: Strategy ===")

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, base_price: float, quantity: int) -> float:
        ...

    @abstractmethod
    def description(self) -> str:
        ...

class RegularPricing(PricingStrategy):
    def calculate_price(self, base_price, quantity):
        return base_price * quantity

    def description(self):
        return "Regular price"

class BulkPricing(PricingStrategy):
    """10% discount for orders of 10 or more."""
    def calculate_price(self, base_price, quantity):
        discount = 0.10 if quantity >= 10 else 0
        return base_price * quantity * (1 - discount)

    def description(self):
        return "Bulk pricing (10% off for 10+)"

class SeasonalPricing(PricingStrategy):
    def __init__(self, discount_rate: float):
        self.rate = discount_rate

    def calculate_price(self, base_price, quantity):
        return base_price * quantity * (1 - self.rate)

    def description(self):
        return f"Seasonal sale ({self.rate*100:.0f}% off)"


class ShoppingCart:
    """Uses a pricing strategy — strategy can be swapped at any time."""

    def __init__(self, strategy: PricingStrategy):
        self._strategy = strategy
        self._items = []

    def set_strategy(self, strategy: PricingStrategy):
        """Change strategy dynamically — useful for seasonal sales."""
        self._strategy = strategy

    def add_item(self, name: str, price: float, qty: int):
        self._items.append((name, price, qty))

    def total(self) -> float:
        return sum(
            self._strategy.calculate_price(price, qty)
            for _, price, qty in self._items
        )

    def receipt(self) -> str:
        lines = [f"Strategy: {self._strategy.description()}"]
        for name, price, qty in self._items:
            line_total = self._strategy.calculate_price(price, qty)
            lines.append(f"  {name}: ${price:.2f} × {qty} = ${line_total:.2f}")
        lines.append(f"  TOTAL: ${self.total():.2f}")
        return "\n".join(lines)


cart = ShoppingCart(RegularPricing())
cart.add_item("Widget", 10.0, 3)
cart.add_item("Gadget", 25.0, 2)
print(cart.receipt())

cart.set_strategy(SeasonalPricing(0.20))   # switch strategy — 20% off
print("\n" + cart.receipt())

# Bulk order
bulk_cart = ShoppingCart(BulkPricing())
bulk_cart.add_item("Widget", 10.0, 15)
print("\n" + bulk_cart.receipt())


print("\n=== Design patterns complete ===")
print("Pattern guide:")
print("  Singleton: use when only ONE instance should exist (config, pool)")
print("  Factory:   use when creation logic is complex or type varies by input")
print("  Observer:  use when multiple components react to the same event")
print("  Strategy:  use when the same operation can use different algorithms")
