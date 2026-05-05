"""
16_design_patterns/observer.py
=================================
CONCEPT: Observer (Event/Pub-Sub) — objects subscribe to events and are
notified automatically when those events occur. Decouples publishers from
subscribers: the publisher doesn't know who's listening.
WHY THIS MATTERS: Every event system, message bus, DOM event, Django signal,
asyncio event, and reactive framework is built on this pattern.
Understanding it unlocks building extensible, decoupled systems.

Prerequisite: Modules 01–10 (OOP, ABCs, decorators)
"""

from __future__ import annotations
import time
import weakref
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable

# =============================================================================
# SECTION 1: Classic Observer — __subject__ / __observer__ interface
# =============================================================================

# CONCEPT: Two roles:
# Subject (Observable): maintains a list of observers, notifies them on change.
# Observer: implements update() and registers with a subject.
# When subject state changes, it calls notify() → all observers' update() runs.

print("=== Section 1: Classic Observer Pattern ===")

class Observer(ABC):
    """Interface all observers must implement."""

    @abstractmethod
    def update(self, event: str, data: Any) -> None:
        """Called by the subject when something changes."""
        ...


class Subject:
    """
    Observable — anything that other objects want to watch.
    Observers register themselves and are called when state changes.
    """

    def __init__(self):
        self._observers: list[Observer] = []

    def subscribe(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self, event: str, data: Any = None) -> None:
        """Notify ALL registered observers."""
        for observer in self._observers:
            observer.update(event, data)


class StockPrice(Subject):
    """Observable stock — notifies observers when price changes."""

    def __init__(self, symbol: str, price: float):
        super().__init__()
        self.symbol = symbol
        self._price = price

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, new_price: float) -> None:
        old_price   = self._price
        self._price = new_price
        change_pct  = (new_price - old_price) / old_price * 100
        self.notify("PRICE_CHANGED", {
            "symbol":     self.symbol,
            "old_price":  old_price,
            "new_price":  new_price,
            "change_pct": change_pct,
        })


class AlertObserver(Observer):
    """Triggers an alert if price moves more than threshold%."""

    def __init__(self, threshold_pct: float = 5.0):
        self.threshold = threshold_pct

    def update(self, event: str, data: Any) -> None:
        if event == "PRICE_CHANGED" and abs(data["change_pct"]) >= self.threshold:
            direction = "UP" if data["change_pct"] > 0 else "DOWN"
            print(f"  [ALERT] {data['symbol']} moved {direction} "
                  f"{abs(data['change_pct']):.1f}% → ${data['new_price']:.2f}")


class LogObserver(Observer):
    """Logs every price change."""

    def __init__(self):
        self.history: list = []

    def update(self, event: str, data: Any) -> None:
        if event == "PRICE_CHANGED":
            self.history.append(data)
            print(f"  [LOG] {data['symbol']}: ${data['old_price']:.2f} "
                  f"→ ${data['new_price']:.2f} ({data['change_pct']:+.1f}%)")


stock = StockPrice("AAPL", 150.00)
alert = AlertObserver(threshold_pct=5.0)
log   = LogObserver()

stock.subscribe(alert)
stock.subscribe(log)

stock.price = 153.00   # +2% — only logged, no alert
stock.price = 142.50   # -7% — alert triggered + logged
stock.price = 142.60   # tiny move

print(f"\n  Log history: {len(log.history)} entries")
stock.unsubscribe(alert)
stock.price = 120.00   # big drop — alert unsubscribed, only logged


# =============================================================================
# SECTION 2: Event Bus — string-based pub/sub (decoupled)
# =============================================================================

# CONCEPT: Instead of observers directly registering with subjects, an EVENT BUS
# mediates. Publishers emit events by NAME; subscribers listen for event names.
# Publisher and subscriber don't know about each other — fully decoupled.
# This is how Django signals, Flask signals, and most frameworks work.

print("\n=== Section 2: Event Bus (Pub/Sub) ===")

class EventBus:
    """
    Central event dispatcher.
    Subscribers register handlers for event names.
    Publishers emit events by name — no direct coupling.
    """

    def __init__(self):
        self._handlers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, handler: Callable) -> None:
        """Register a callable to be called when `event` is emitted."""
        self._handlers[event].append(handler)

    def unsubscribe(self, event: str, handler: Callable) -> None:
        handlers = self._handlers.get(event, [])
        if handler in handlers:
            handlers.remove(handler)

    def emit(self, event: str, **kwargs) -> None:
        """Emit an event — all registered handlers are called with keyword args."""
        for handler in self._handlers.get(event, []):
            handler(**kwargs)

    def on(self, *events: str):
        """
        Decorator: @bus.on("user.created", "user.updated")
        Registers a function as a handler for one or more events.
        """
        def decorator(func: Callable) -> Callable:
            for event in events:
                self.subscribe(event, func)
            return func
        return decorator


bus = EventBus()

# Decorator-style registration
@bus.on("user.created")
def send_welcome_email(user_id: int, email: str, **_):
    print(f"  [Email Service] Sending welcome to {email} (user={user_id})")

@bus.on("user.created")
def create_default_settings(user_id: int, **_):
    print(f"  [Settings Service] Creating defaults for user={user_id}")

@bus.on("user.created", "user.updated")
def audit_log(event_type: str = "unknown", user_id: int = -1, **_):
    print(f"  [Audit] '{event_type}' for user={user_id}")

@bus.on("user.updated")
def invalidate_cache(user_id: int, **_):
    print(f"  [Cache] Invalidating cache for user={user_id}")


# Function-style subscription
def sms_verification(user_id: int, phone: str = None, **_):
    if phone:
        print(f"  [SMS] Sending verification to {phone} (user={user_id})")

bus.subscribe("user.created", sms_verification)

print("Emitting user.created:")
bus.emit("user.created", user_id=42, email="alice@example.com", phone="+15551234567")

print("\nEmitting user.updated:")
bus.emit("user.updated", event_type="user.updated", user_id=42, field="email")


# =============================================================================
# SECTION 3: Weak-reference observers — preventing memory leaks
# =============================================================================

# CONCEPT: If observers hold a hard reference, the subject keeps them alive even
# after all other references are gone — a memory leak. Using weakref allows
# the garbage collector to collect dead observers automatically.
# WHEN TO USE: long-lived subjects (app-wide event bus) with short-lived
# observers (widgets that can be destroyed, request-scoped handlers).

print("\n=== Section 3: Weak Reference Observers ===")

class WeakEventBus:
    """Event bus that holds WEAK references to handlers."""

    def __init__(self):
        self._handlers: dict[str, list[weakref.ref]] = defaultdict(list)

    def subscribe(self, event: str, handler: Callable) -> None:
        # weakref.ref can only wrap bound methods or regular objects, not lambdas/functions
        # For bound methods, use weakref.WeakMethod
        if hasattr(handler, "__self__"):
            ref = weakref.WeakMethod(handler)
        else:
            ref = weakref.ref(handler)
        self._handlers[event].append(ref)

    def emit(self, event: str, **kwargs) -> None:
        alive = []
        for ref in self._handlers.get(event, []):
            handler = ref()    # dereference — returns None if collected
            if handler is not None:
                handler(**kwargs)
                alive.append(ref)
        self._handlers[event] = alive   # prune dead refs


class ShortLivedHandler:
    def __init__(self, name: str):
        self.name = name

    def handle(self, **kwargs) -> None:
        print(f"  [{self.name}] received: {kwargs}")


weak_bus = WeakEventBus()

h1 = ShortLivedHandler("Handler-1")
h2 = ShortLivedHandler("Handler-2")
weak_bus.subscribe("data.ready", h1.handle)
weak_bus.subscribe("data.ready", h2.handle)

print("Before deletion:")
weak_bus.emit("data.ready", payload="batch_1")

del h1   # h1 goes out of scope — weak ref becomes None

print("\nAfter deleting h1:")
weak_bus.emit("data.ready", payload="batch_2")  # only h2 receives it


# =============================================================================
# SECTION 4: Reactive property — observer built into attribute access
# =============================================================================

# CONCEPT: Combine @property with observer notification. Any time an attribute
# changes, registered watchers are automatically notified.
# This is the model behind Vue.js reactivity and Python's tkinter StringVar.

print("\n=== Section 4: Reactive (Observable) Model ===")

class ObservableModel:
    """
    Base class for reactive data models.
    Subclasses declare fields; any __setattr__ triggers watchers.
    """

    def __init__(self):
        object.__setattr__(self, "_watchers", defaultdict(list))

    def watch(self, field: str, callback: Callable) -> None:
        """Register callback for when `field` changes."""
        self._watchers[field].append(callback)

    def __setattr__(self, name: str, value: Any) -> None:
        old = getattr(self, name, None)
        object.__setattr__(self, name, value)
        if old != value:
            for cb in self._watchers.get(name, []):
                cb(name, old, value)


@dataclass
class UserModel(ObservableModel):
    name:  str = ""
    email: str = ""
    role:  str = "viewer"

    def __post_init__(self):
        ObservableModel.__init__(self)


user = UserModel(name="Alice", email="alice@example.com")

# Register watchers
user.watch("role",  lambda f, old, new: print(f"  [Auth] role changed: {old!r} → {new!r}"))
user.watch("email", lambda f, old, new: print(f"  [Email] address changed → {new}"))

user.role  = "admin"    # triggers auth watcher
user.email = "alice2@example.com"   # triggers email watcher
user.name  = "Alice"    # no change — watchers not called


print("\n=== Observer patterns complete ===")
print("Pattern guide:")
print("  Classic Observer  → tightly coupled; observer registers with subject directly")
print("  Event Bus         → decoupled; string-based pub/sub; easy to add handlers")
print("  Weak References   → prevent memory leaks with short-lived observers")
print("  Reactive Model    → property-level observers; Vue.js / spreadsheet model")
