# 🔩 Low Level Design (LLD)

> LLD is about designing the internals of a component — class structure, responsibilities,
> relationships, and how objects collaborate to fulfill a requirement.
> Where HLD answers "what services exist?", LLD answers "how is each service built internally?"

---

## 📋 Contents

```
1.  What is LLD and when does it matter?
2.  OOP pillars applied to design
3.  SOLID principles — the design compass
4.  Design patterns — reusable solutions
5.  Class diagrams & relationships
6.  Modeling real-world entities
7.  State machines
8.  Designing a parking lot (step by step)
9.  Designing a chess game (step by step)
10. Designing an elevator system
11. Designing a library management system
12. Designing a notification service
13. LLD interview approach
```

---

## 1. What is LLD?

Low Level Design bridges the gap between architecture and code.

```
HLD (High Level Design):
  "We need a notification service, a user service, a payment service"
  "The notification service uses Kafka for async delivery"

LLD (Low Level Design):
  "How does the notification service work internally?"
  "What classes exist? What are their responsibilities?"
  "How does NotificationService interact with EmailSender, SMSSender?"
  "What's the interface? What design patterns apply?"
```

**When LLD matters:**
- System design interviews (FAANG, Stripe, etc.)
- Code reviews for new features
- Team design discussions before implementation
- Greenfield services: designing before writing

**LLD vs Coding:**
```
Coding:  "Implement the feature"
LLD:     "Design the classes that make the feature work"
```

---

## 2. OOP Pillars Applied to Design

### Encapsulation

Hide implementation, expose only what's needed.

```python
# Bad — exposes internals
class BankAccount:
    balance = 0  # public

# Good — encapsulated
class BankAccount:
    def __init__(self):
        self._balance = 0.0          # private

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self._balance += amount

    def get_balance(self) -> float:
        return self._balance
```

**Rule:** Make fields private. Expose through methods that enforce invariants.

---

### Abstraction

Expose what, not how.

```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def charge(self, amount: float, token: str) -> bool: ...

    @abstractmethod
    def refund(self, transaction_id: str) -> bool: ...

class StripeProcessor(PaymentProcessor):
    def charge(self, amount, token):
        # Stripe-specific impl
        ...

class PayPalProcessor(PaymentProcessor):
    def charge(self, amount, token):
        # PayPal-specific impl
        ...
```

**Rule:** Program to interfaces. Callers don't know which processor they're using.

---

### Inheritance

Use for IS-A relationships. Prefer composition over inheritance.

```python
# IS-A: a SavingsAccount IS-A BankAccount
class BankAccount:
    def deposit(self, amount): ...
    def withdraw(self, amount): ...

class SavingsAccount(BankAccount):
    def __init__(self, interest_rate: float):
        super().__init__()
        self._rate = interest_rate

    def apply_interest(self) -> None:
        self.deposit(self._balance * self._rate)
```

**Pitfall:** Deep inheritance hierarchies are fragile. More than 2–3 levels → use composition.

---

### Polymorphism

Different implementations, same interface.

```python
def process_payment(processor: PaymentProcessor, amount: float, token: str):
    success = processor.charge(amount, token)  # works with any processor
    if not success:
        raise PaymentFailed("charge returned false")
```

---

## 3. SOLID Principles

The five principles that prevent design rot.

### S — Single Responsibility Principle

A class should have ONE reason to change.

```python
# Bad: OrderService does too much
class OrderService:
    def create_order(self, items): ...
    def calculate_tax(self, order): ...     # tax logic = different responsibility
    def send_confirmation_email(self, order): ...  # email = different responsibility
    def save_to_db(self, order): ...         # persistence = different responsibility

# Good: separated concerns
class OrderService:
    def __init__(self, tax_calc, emailer, repo):
        self._tax = tax_calc
        self._email = emailer
        self._repo = repo

    def create_order(self, items):
        order = Order(items)
        order.tax = self._tax.calculate(order)
        self._repo.save(order)
        self._email.send_confirmation(order)
        return order

class TaxCalculator:
    def calculate(self, order) -> float: ...

class OrderEmailer:
    def send_confirmation(self, order) -> None: ...

class OrderRepository:
    def save(self, order) -> None: ...
```

---

### O — Open/Closed Principle

Open for extension, closed for modification.

```python
# Bad: adding new discount type requires modifying DiscountCalculator
class DiscountCalculator:
    def calculate(self, order, discount_type):
        if discount_type == "percentage":
            return order.total * 0.10
        elif discount_type == "fixed":
            return 5.0
        # Every new type requires modifying this method!

# Good: extend without modifying
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, order) -> float: ...

class PercentageDiscount(DiscountStrategy):
    def __init__(self, pct): self._pct = pct
    def apply(self, order): return order.total * self._pct

class FixedDiscount(DiscountStrategy):
    def __init__(self, amount): self._amount = amount
    def apply(self, order): return self._amount

class FreeShippingDiscount(DiscountStrategy):  # new type — no existing code touched
    def apply(self, order): return order.shipping_cost

class DiscountCalculator:
    def calculate(self, order, strategy: DiscountStrategy) -> float:
        return strategy.apply(order)
```

---

### L — Liskov Substitution Principle

Subclasses must be substitutable for their base class.

```python
# Violation: Square breaks Rectangle's contract
class Rectangle:
    def set_width(self, w): self._w = w
    def set_height(self, h): self._h = h
    def area(self): return self._w * self._h

class Square(Rectangle):  # LSP VIOLATION
    def set_width(self, w):
        self._w = self._h = w  # changes height too!
    def set_height(self, h):
        self._w = self._h = h  # changes width too!

def resize_and_measure(rect: Rectangle):
    rect.set_width(5)
    rect.set_height(4)
    assert rect.area() == 20  # fails for Square!

# Fix: don't force inheritance — use composition or separate abstractions
class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

class Rectangle(Shape):
    def __init__(self, w, h): self._w, self._h = w, h
    def area(self): return self._w * self._h

class Square(Shape):
    def __init__(self, side): self._side = side
    def area(self): return self._side ** 2
```

---

### I — Interface Segregation Principle

Clients should not depend on interfaces they don't use.

```python
# Bad: fat interface forces unneeded implementation
class Worker(ABC):
    @abstractmethod
    def work(self): ...
    @abstractmethod
    def eat(self): ...    # robots don't eat!
    @abstractmethod
    def sleep(self): ...  # robots don't sleep!

class Robot(Worker):
    def work(self): ...
    def eat(self): raise NotImplementedError  # forced stub
    def sleep(self): raise NotImplementedError

# Good: segregated interfaces
class Workable(ABC):
    @abstractmethod
    def work(self): ...

class Restable(ABC):
    @abstractmethod
    def eat(self): ...
    @abstractmethod
    def sleep(self): ...

class Human(Workable, Restable):
    def work(self): ...
    def eat(self): ...
    def sleep(self): ...

class Robot(Workable):  # only implements what it needs
    def work(self): ...
```

---

### D — Dependency Inversion Principle

High-level modules should not depend on low-level modules. Both depend on abstractions.

```python
# Bad: OrderService directly creates MySQLRepository
class OrderService:
    def __init__(self):
        self._repo = MySQLRepository()  # tightly coupled

# Good: depend on abstraction, inject concrete implementation
class OrderRepository(ABC):
    @abstractmethod
    def save(self, order) -> None: ...
    @abstractmethod
    def find_by_id(self, order_id: str): ...

class MySQLOrderRepository(OrderRepository):
    def save(self, order): ...
    def find_by_id(self, order_id): ...

class InMemoryOrderRepository(OrderRepository):  # for testing
    def __init__(self): self._store = {}
    def save(self, order): self._store[order.id] = order
    def find_by_id(self, order_id): return self._store.get(order_id)

class OrderService:
    def __init__(self, repo: OrderRepository):  # injected
        self._repo = repo
```

---

## 4. Design Patterns in LLD

### Creational Patterns

**Singleton** — one instance, globally accessible:
```python
class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connected = False
        return cls._instance

    def connect(self, url):
        if not self._connected:
            # expensive init once
            self._connected = True
```

**Factory Method** — delegate object creation:
```python
class NotificationFactory:
    @staticmethod
    def create(channel: str) -> Notification:
        match channel:
            case "email": return EmailNotification()
            case "sms":   return SMSNotification()
            case "push":  return PushNotification()
            case _: raise ValueError(f"Unknown channel: {channel}")
```

**Builder** — construct complex objects step by step:
```python
class QueryBuilder:
    def __init__(self):
        self._table = None
        self._conditions = []
        self._limit = None

    def from_table(self, table: str) -> "QueryBuilder":
        self._table = table
        return self

    def where(self, condition: str) -> "QueryBuilder":
        self._conditions.append(condition)
        return self

    def limit(self, n: int) -> "QueryBuilder":
        self._limit = n
        return self

    def build(self) -> str:
        q = f"SELECT * FROM {self._table}"
        if self._conditions:
            q += " WHERE " + " AND ".join(self._conditions)
        if self._limit:
            q += f" LIMIT {self._limit}"
        return q

# Usage:
query = (QueryBuilder()
    .from_table("orders")
    .where("status = 'pending'")
    .where("total > 100")
    .limit(50)
    .build())
```

---

### Structural Patterns

**Adapter** — bridge incompatible interfaces:
```python
class LegacyPaymentGateway:
    def make_payment(self, card_number, expiry, amount): ...

class PaymentAdapter(PaymentProcessor):  # implements our interface
    def __init__(self, legacy: LegacyPaymentGateway):
        self._legacy = legacy

    def charge(self, amount: float, token: str) -> bool:
        card, expiry = self._parse_token(token)
        return self._legacy.make_payment(card, expiry, amount)
```

**Decorator** — add behavior without changing the class:
```python
class LoggingPaymentProcessor(PaymentProcessor):
    def __init__(self, processor: PaymentProcessor, logger):
        self._inner = processor
        self._log = logger

    def charge(self, amount, token):
        self._log.info(f"Charging ${amount}")
        result = self._inner.charge(amount, token)
        self._log.info(f"Charge {'succeeded' if result else 'failed'}")
        return result

# Stack decorators:
processor = LoggingPaymentProcessor(
    RetryingPaymentProcessor(StripeProcessor(), max_retries=3),
    logger
)
```

**Facade** — simplify a complex subsystem:
```python
class HomeAutomationFacade:
    def __init__(self, lights, ac, alarm, tv):
        self._lights = lights
        self._ac = ac
        self._alarm = alarm
        self._tv = tv

    def leave_home(self):
        self._lights.turn_off_all()
        self._ac.set_temperature(28)
        self._alarm.arm()
        self._tv.turn_off()

    def arrive_home(self):
        self._lights.turn_on_entrance()
        self._ac.set_temperature(22)
        self._alarm.disarm()
```

**Composite** — tree structures where single and group are treated the same:
```python
class FileSystemItem(ABC):
    @abstractmethod
    def size(self) -> int: ...
    @abstractmethod
    def display(self, indent: int = 0) -> None: ...

class File(FileSystemItem):
    def __init__(self, name, size):
        self._name, self._size = name, size
    def size(self): return self._size
    def display(self, indent=0): print(" " * indent + self._name)

class Directory(FileSystemItem):
    def __init__(self, name):
        self._name = name
        self._children: list[FileSystemItem] = []

    def add(self, item: FileSystemItem): self._children.append(item)
    def size(self): return sum(c.size() for c in self._children)
    def display(self, indent=0):
        print(" " * indent + f"[{self._name}]")
        for child in self._children:
            child.display(indent + 2)
```

---

### Behavioral Patterns

**Observer** — notify dependents of state changes (event system):
```python
from typing import Callable

class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = {}

    def subscribe(self, event: str, handler: Callable) -> None:
        self._subscribers.setdefault(event, []).append(handler)

    def publish(self, event: str, data=None) -> None:
        for handler in self._subscribers.get(event, []):
            handler(data)

# Usage:
bus = EventBus()
bus.subscribe("order.created", send_confirmation_email)
bus.subscribe("order.created", update_inventory)
bus.subscribe("order.created", notify_warehouse)

bus.publish("order.created", order)  # triggers all 3 handlers
```

**Strategy** — swap algorithms at runtime:
```python
class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: list) -> list: ...

class QuickSort(SortStrategy):
    def sort(self, data): ...

class MergeSort(SortStrategy):
    def sort(self, data): ...

class DataProcessor:
    def __init__(self, strategy: SortStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: SortStrategy):
        self._strategy = strategy

    def process(self, data):
        return self._strategy.sort(data)
```

**Command** — encapsulate requests as objects (undo/redo):
```python
class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...
    @abstractmethod
    def undo(self) -> None: ...

class TransferCommand(Command):
    def __init__(self, from_acc, to_acc, amount):
        self._from = from_acc
        self._to = to_acc
        self._amount = amount

    def execute(self):
        self._from.withdraw(self._amount)
        self._to.deposit(self._amount)

    def undo(self):
        self._to.withdraw(self._amount)
        self._from.deposit(self._amount)

class TransactionHistory:
    def __init__(self):
        self._history: list[Command] = []

    def execute(self, cmd: Command):
        cmd.execute()
        self._history.append(cmd)

    def undo_last(self):
        if self._history:
            self._history.pop().undo()
```

**State** — change behavior based on internal state:
```python
class OrderState(ABC):
    @abstractmethod
    def confirm(self, order): ...
    @abstractmethod
    def ship(self, order): ...
    @abstractmethod
    def cancel(self, order): ...

class PendingState(OrderState):
    def confirm(self, order): order.set_state(ConfirmedState())
    def ship(self, order): raise InvalidTransition("Cannot ship unconfirmed order")
    def cancel(self, order): order.set_state(CancelledState())

class ConfirmedState(OrderState):
    def confirm(self, order): raise InvalidTransition("Already confirmed")
    def ship(self, order): order.set_state(ShippedState())
    def cancel(self, order): order.set_state(CancelledState())

class ShippedState(OrderState):
    def confirm(self, order): raise InvalidTransition("Already shipped")
    def ship(self, order): raise InvalidTransition("Already shipped")
    def cancel(self, order): raise InvalidTransition("Cannot cancel shipped order")

class Order:
    def __init__(self):
        self._state: OrderState = PendingState()

    def set_state(self, state: OrderState):
        self._state = state

    def confirm(self): self._state.confirm(self)
    def ship(self):    self._state.ship(self)
    def cancel(self):  self._state.cancel(self)
```

---

## 5. Class Diagrams & Relationships

```
Relationships (weakest to strongest):
  Dependency   ----→    A uses B (method parameter)
  Association  ——→      A has a reference to B
  Aggregation  ◇——→     A "has" B (B can exist without A)
  Composition  ◆——→     A "owns" B (B dies with A)
  Inheritance  ——▷      A IS-A B
  Realization  - - ▷    A implements interface B

Notation:
  + public
  - private
  # protected
  ~package

  ClassName
  ──────────
  - field: Type
  ──────────
  + method(): ReturnType
```

**Example — Parking Lot:**
```
ParkingLot                 ParkingFloor
─────────────              ────────────────
- floors: List[Floor] ◆──→ - spots: List[Spot]
- entry_gates: List[Gate]  - floor_num: int
─────────────              + get_available()
+ park(vehicle)            + find_spot(type)
+ leave(ticket)
+ get_available_count()

                    ParkingSpot
                    ──────────────
                    - id: str
                    - type: SpotType  ←── <<enum>> SpotType
                    - is_occupied: bool     COMPACT
                    + occupy(vehicle)       LARGE
                    + vacate()              MOTORCYCLE
```

---

## 6. Modeling Real-World Entities

**Step-by-step approach:**

```
1. Identify entities (nouns) → classes
2. Identify behaviors (verbs) → methods
3. Identify relationships → associations/compositions
4. Apply design patterns
5. Define interfaces/abstractions
6. Consider edge cases
```

**Example — Food delivery system:**
```
Nouns:     Customer, Restaurant, Menu, MenuItem, Order, OrderItem,
           DeliveryDriver, Payment, Review

Behaviors: place order, assign driver, track delivery,
           process payment, leave review

Relationships:
  Customer ——→ Order (places many)
  Order ◆——→ OrderItems (owns)
  Order ——→ Restaurant (ordered from)
  Order ——→ DeliveryDriver (assigned)
  Order ——→ Payment (has one)
  Restaurant ◆——→ Menu ◆——→ MenuItems
```

---

## 7. State Machines

Many real-world entities have explicit state transitions.

```
Order States:
  PENDING ──confirm──→ CONFIRMED ──assign──→ PREPARING
                                                  │
                              CANCELLED ←─cancel──┘
                                                  │
                                             pick_up
                                                  ▼
                                            OUT_FOR_DELIVERY
                                                  │
                                              deliver
                                                  ▼
                                            DELIVERED
```

**Implementation pattern:**
```python
from enum import Enum, auto

class OrderStatus(Enum):
    PENDING = auto()
    CONFIRMED = auto()
    PREPARING = auto()
    OUT_FOR_DELIVERY = auto()
    DELIVERED = auto()
    CANCELLED = auto()

VALID_TRANSITIONS = {
    OrderStatus.PENDING:          {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED:        {OrderStatus.PREPARING, OrderStatus.CANCELLED},
    OrderStatus.PREPARING:        {OrderStatus.OUT_FOR_DELIVERY},
    OrderStatus.OUT_FOR_DELIVERY: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED:        set(),
    OrderStatus.CANCELLED:        set(),
}

def transition(order, new_status: OrderStatus):
    if new_status not in VALID_TRANSITIONS[order.status]:
        raise InvalidTransition(f"{order.status} → {new_status} not allowed")
    order.status = new_status
```

---

## 8. Designing a Parking Lot (Step by Step)

### Requirements gathering
```
Functional:
  - Multiple floors, each with multiple spots
  - Spot types: compact, large, motorcycle, handicapped
  - Entry and exit gates
  - Ticketing: record entry time, spot
  - Payment: calculate based on duration

Non-functional:
  - Should handle concurrent entries/exits
  - Support multiple payment methods
```

### Classes identified
```python
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod

class SpotType(Enum):
    COMPACT = "compact"
    LARGE = "large"
    MOTORCYCLE = "motorcycle"
    HANDICAPPED = "handicapped"

class VehicleType(Enum):
    CAR = "car"
    TRUCK = "truck"
    MOTORCYCLE = "motorcycle"

class Vehicle:
    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        self.license_plate = license_plate
        self.type = vehicle_type

class ParkingSpot:
    def __init__(self, spot_id: str, spot_type: SpotType, floor: int):
        self.id = spot_id
        self.type = spot_type
        self.floor = floor
        self._vehicle: Vehicle | None = None

    @property
    def is_occupied(self) -> bool:
        return self._vehicle is not None

    def can_fit(self, vehicle: Vehicle) -> bool:
        fit_map = {
            SpotType.MOTORCYCLE: {VehicleType.MOTORCYCLE},
            SpotType.COMPACT:    {VehicleType.CAR},
            SpotType.LARGE:      {VehicleType.CAR, VehicleType.TRUCK},
            SpotType.HANDICAPPED:{VehicleType.CAR},
        }
        return vehicle.type in fit_map.get(self.type, set())

    def park(self, vehicle: Vehicle) -> None:
        if self.is_occupied:
            raise ValueError(f"Spot {self.id} is occupied")
        self._vehicle = vehicle

    def vacate(self) -> Vehicle:
        v = self._vehicle
        self._vehicle = None
        return v

class Ticket:
    def __init__(self, ticket_id: str, vehicle: Vehicle, spot: ParkingSpot):
        self.id = ticket_id
        self.vehicle = vehicle
        self.spot = spot
        self.entry_time = datetime.now()
        self.exit_time: datetime | None = None

class PricingStrategy(ABC):
    @abstractmethod
    def calculate(self, duration_hours: float) -> float: ...

class HourlyPricing(PricingStrategy):
    def __init__(self, rate_per_hour: float):
        self._rate = rate_per_hour

    def calculate(self, duration_hours: float) -> float:
        return max(1.0, duration_hours) * self._rate  # min 1 hour

class ParkingFloor:
    def __init__(self, floor_num: int, spots: list[ParkingSpot]):
        self.floor_num = floor_num
        self._spots = spots

    def find_available(self, vehicle: Vehicle) -> ParkingSpot | None:
        return next(
            (s for s in self._spots if not s.is_occupied and s.can_fit(vehicle)),
            None
        )

    def available_count(self) -> int:
        return sum(1 for s in self._spots if not s.is_occupied)

class ParkingLot:
    def __init__(self, name: str, floors: list[ParkingFloor],
                 pricing: PricingStrategy):
        self.name = name
        self._floors = floors
        self._pricing = pricing
        self._active_tickets: dict[str, Ticket] = {}  # ticket_id → ticket
        self._ticket_counter = 0

    def park_vehicle(self, vehicle: Vehicle) -> Ticket:
        spot = self._find_spot(vehicle)
        if spot is None:
            raise Exception("No available spot for this vehicle type")
        spot.park(vehicle)
        ticket = self._create_ticket(vehicle, spot)
        self._active_tickets[ticket.id] = ticket
        return ticket

    def release_vehicle(self, ticket_id: str) -> float:
        ticket = self._active_tickets.pop(ticket_id, None)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")
        ticket.exit_time = datetime.now()
        ticket.spot.vacate()
        hours = (ticket.exit_time - ticket.entry_time).seconds / 3600
        return self._pricing.calculate(hours)

    def _find_spot(self, vehicle: Vehicle) -> ParkingSpot | None:
        for floor in self._floors:
            spot = floor.find_available(vehicle)
            if spot:
                return spot
        return None

    def _create_ticket(self, vehicle, spot) -> Ticket:
        self._ticket_counter += 1
        return Ticket(f"T{self._ticket_counter:06d}", vehicle, spot)

    def available_spots(self) -> int:
        return sum(f.available_count() for f in self._floors)
```

---

## 9. Designing a Chess Game

```python
from enum import Enum

class Color(Enum):
    WHITE = "white"
    BLACK = "black"

class Position:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def is_valid(self) -> bool:
        return 0 <= self.row < 8 and 0 <= self.col < 8

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

class Piece(ABC):
    def __init__(self, color: Color, position: Position):
        self.color = color
        self.position = position

    @abstractmethod
    def get_valid_moves(self, board: "Board") -> list[Position]: ...

class King(Piece):
    def get_valid_moves(self, board):
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_pos = Position(self.position.row + dr, self.position.col + dc)
                if new_pos.is_valid() and not board.has_same_color(new_pos, self.color):
                    moves.append(new_pos)
        return moves

class Rook(Piece):
    def get_valid_moves(self, board):
        moves = []
        for direction in [(0,1),(0,-1),(1,0),(-1,0)]:
            r, c = self.position.row, self.position.col
            while True:
                r += direction[0]
                c += direction[1]
                pos = Position(r, c)
                if not pos.is_valid():
                    break
                if board.has_same_color(pos, self.color):
                    break
                moves.append(pos)
                if board.has_piece(pos):
                    break  # blocked after capture
        return moves

class Board:
    def __init__(self):
        self._grid: dict[tuple[int,int], Piece] = {}

    def place(self, piece: Piece) -> None:
        self._grid[(piece.position.row, piece.position.col)] = piece

    def has_piece(self, pos: Position) -> bool:
        return (pos.row, pos.col) in self._grid

    def has_same_color(self, pos: Position, color: Color) -> bool:
        piece = self._grid.get((pos.row, pos.col))
        return piece is not None and piece.color == color

    def move(self, from_pos: Position, to_pos: Position) -> None:
        piece = self._grid.pop((from_pos.row, from_pos.col))
        self._grid.pop((to_pos.row, to_pos.col), None)  # capture
        piece.position = to_pos
        self._grid[(to_pos.row, to_pos.col)] = piece

class Game:
    def __init__(self):
        self._board = Board()
        self._current_turn = Color.WHITE
        self._setup_board()

    def _setup_board(self):
        # Place pieces in starting positions
        ...

    def make_move(self, from_pos: Position, to_pos: Position) -> bool:
        piece = self._board._grid.get((from_pos.row, from_pos.col))
        if not piece or piece.color != self._current_turn:
            return False
        valid_moves = piece.get_valid_moves(self._board)
        if to_pos not in valid_moves:
            return False
        self._board.move(from_pos, to_pos)
        self._current_turn = (Color.BLACK if self._current_turn == Color.WHITE
                              else Color.WHITE)
        return True
```

---

## 10. Designing an Elevator System

```python
from enum import Enum
from dataclasses import dataclass, field

class Direction(Enum):
    UP = "up"
    DOWN = "down"
    IDLE = "idle"

class ElevatorState(Enum):
    MOVING = "moving"
    STOPPED = "stopped"
    MAINTENANCE = "maintenance"

@dataclass
class Request:
    floor: int
    direction: Direction | None = None  # None for internal requests

class Elevator:
    def __init__(self, elevator_id: int, total_floors: int):
        self.id = elevator_id
        self.current_floor = 1
        self.direction = Direction.IDLE
        self.state = ElevatorState.STOPPED
        self._destinations: set[int] = set()

    def add_destination(self, floor: int) -> None:
        self._destinations.add(floor)
        self._update_direction()

    def step(self) -> None:
        if not self._destinations:
            self.direction = Direction.IDLE
            return
        if self.direction == Direction.UP:
            self.current_floor += 1
        elif self.direction == Direction.DOWN:
            self.current_floor -= 1
        if self.current_floor in self._destinations:
            self._destinations.discard(self.current_floor)
            self._update_direction()

    def _update_direction(self):
        above = {d for d in self._destinations if d > self.current_floor}
        below = {d for d in self._destinations if d < self.current_floor}
        if self.direction == Direction.UP and above:
            return  # keep going up
        if self.direction == Direction.DOWN and below:
            return  # keep going down
        if above:
            self.direction = Direction.UP
        elif below:
            self.direction = Direction.DOWN
        else:
            self.direction = Direction.IDLE

class ElevatorController:
    """SCAN (elevator) algorithm for dispatch"""
    def __init__(self, elevators: list[Elevator]):
        self._elevators = elevators

    def request(self, floor: int, direction: Direction) -> None:
        best = self._find_best_elevator(floor, direction)
        best.add_destination(floor)

    def _find_best_elevator(self, floor: int, direction: Direction) -> Elevator:
        def score(e: Elevator) -> int:
            # Lower score = better choice
            if e.state == ElevatorState.MAINTENANCE:
                return 10_000
            if e.direction == Direction.IDLE:
                return abs(e.current_floor - floor)
            if e.direction == direction:
                if (direction == Direction.UP and e.current_floor <= floor):
                    return abs(e.current_floor - floor)  # on the way
                if (direction == Direction.DOWN and e.current_floor >= floor):
                    return abs(e.current_floor - floor)
            return 1000 + abs(e.current_floor - floor)  # going wrong way

        return min(self._elevators, key=score)
```

---

## 11. Designing a Library Management System

```python
from datetime import datetime, timedelta
from dataclasses import dataclass, field

@dataclass
class Book:
    isbn: str
    title: str
    author: str
    total_copies: int
    available_copies: int = field(init=False)

    def __post_init__(self):
        self.available_copies = self.total_copies

    def is_available(self) -> bool:
        return self.available_copies > 0

class Member:
    MAX_BORROW_LIMIT = 5
    BORROW_DAYS = 14

    def __init__(self, member_id: str, name: str):
        self.id = member_id
        self.name = name
        self._borrowed: dict[str, datetime] = {}  # isbn → due_date

    def can_borrow(self) -> bool:
        return len(self._borrowed) < self.MAX_BORROW_LIMIT

    def borrow(self, isbn: str) -> datetime:
        if not self.can_borrow():
            raise Exception("Borrow limit reached")
        due = datetime.now() + timedelta(days=self.BORROW_DAYS)
        self._borrowed[isbn] = due
        return due

    def return_book(self, isbn: str) -> float:
        due = self._borrowed.pop(isbn, None)
        if not due:
            raise Exception(f"Member didn't borrow {isbn}")
        overdue_days = max(0, (datetime.now() - due).days)
        return overdue_days * 1.0  # $1/day fine

class Library:
    def __init__(self):
        self._books: dict[str, Book] = {}
        self._members: dict[str, Member] = {}
        self._waitlist: dict[str, list[str]] = {}  # isbn → [member_id]

    def add_book(self, book: Book) -> None:
        self._books[book.isbn] = book

    def register_member(self, member: Member) -> None:
        self._members[member.id] = member

    def checkout(self, member_id: str, isbn: str) -> datetime:
        member = self._get_member(member_id)
        book = self._get_book(isbn)
        if not book.is_available():
            raise Exception("No copies available — join waitlist?")
        due = member.borrow(isbn)
        book.available_copies -= 1
        return due

    def return_book(self, member_id: str, isbn: str) -> float:
        member = self._get_member(member_id)
        book = self._get_book(isbn)
        fine = member.return_book(isbn)
        book.available_copies += 1
        self._notify_next_in_waitlist(isbn)
        return fine

    def join_waitlist(self, member_id: str, isbn: str) -> None:
        self._waitlist.setdefault(isbn, []).append(member_id)

    def _notify_next_in_waitlist(self, isbn: str) -> None:
        waitlist = self._waitlist.get(isbn, [])
        if waitlist:
            next_member_id = waitlist.pop(0)
            # notify next_member_id that book is available
            print(f"Notifying member {next_member_id}: {isbn} is available")

    def _get_member(self, member_id: str) -> Member:
        m = self._members.get(member_id)
        if not m: raise ValueError(f"Member {member_id} not found")
        return m

    def _get_book(self, isbn: str) -> Book:
        b = self._books.get(isbn)
        if not b: raise ValueError(f"Book {isbn} not found")
        return b
```

---

## 12. Designing a Notification Service

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

class NotificationChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"

@dataclass
class NotificationRequest:
    recipient_id: str
    subject: str
    body: str
    channels: list[NotificationChannel]
    priority: str = "normal"  # "high" | "normal" | "low"

class NotificationSender(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> bool: ...

class EmailSender(NotificationSender):
    def __init__(self, smtp_host: str):
        self._smtp = smtp_host

    def send(self, to, subject, body) -> bool:
        print(f"[EMAIL] To: {to}, Subject: {subject}")
        return True  # actual SMTP call

class SMSSender(NotificationSender):
    def __init__(self, twilio_client):
        self._client = twilio_client

    def send(self, to, subject, body) -> bool:
        print(f"[SMS] To: {to}: {body[:160]}")
        return True

class PushSender(NotificationSender):
    def send(self, to, subject, body) -> bool:
        print(f"[PUSH] To: {to}: {subject}")
        return True

class UserContactRepository(ABC):
    @abstractmethod
    def get_email(self, user_id: str) -> str | None: ...
    @abstractmethod
    def get_phone(self, user_id: str) -> str | None: ...
    @abstractmethod
    def get_push_token(self, user_id: str) -> str | None: ...

class NotificationService:
    def __init__(self, contact_repo: UserContactRepository):
        self._repo = contact_repo
        self._senders: dict[NotificationChannel, NotificationSender] = {}

    def register_sender(self, channel: NotificationChannel,
                        sender: NotificationSender) -> None:
        self._senders[channel] = sender

    def notify(self, request: NotificationRequest) -> dict[str, bool]:
        results = {}
        contact_map = {
            NotificationChannel.EMAIL: self._repo.get_email,
            NotificationChannel.SMS:   self._repo.get_phone,
            NotificationChannel.PUSH:  self._repo.get_push_token,
        }
        for channel in request.channels:
            sender = self._senders.get(channel)
            if not sender:
                results[channel.value] = False
                continue
            get_contact = contact_map.get(channel)
            to = get_contact(request.recipient_id) if get_contact else None
            if not to:
                results[channel.value] = False
                continue
            results[channel.value] = sender.send(to, request.subject, request.body)
        return results
```

---

## 13. LLD Interview Approach

```
Step 1 — Requirements (5 min)
  Ask: functional requirements (what it must do)
  Ask: non-functional (scale, concurrent users, consistency needs)
  Clarify: scope — what's in, what's out

Step 2 — Core Entities (5 min)
  List the main nouns → initial classes
  Identify key verbs → methods on those classes
  Draw simple class list on whiteboard

Step 3 — Class Diagram (10 min)
  Define relationships (composition vs association)
  Define interfaces/ABCs for key abstractions
  Apply SOLID — especially SRP and DIP

Step 4 — Core Implementation (15 min)
  Write key classes with method signatures
  Implement the most complex method fully
  Show design patterns where applicable

Step 5 — Edge Cases & Extensions (5 min)
  Concurrency: where do race conditions occur?
  Error handling: what can go wrong?
  Extensibility: how to add new features?
  Testing: what would unit tests look like?
```

**Signals interviewers look for:**
```
✓ Clean interface definitions (ABC / abstract methods)
✓ Dependency injection (not hardcoded dependencies)
✓ Single responsibility in each class
✓ Polymorphism for extensibility
✓ State machine for entities with lifecycle
✓ Asking clarifying questions before designing
✗ God classes (one class doing everything)
✗ Deep inheritance trees (> 3 levels)
✗ Hardcoded dependencies (new ConcreteClass() inside business logic)
✗ Anemic models (classes with only getters/setters, no behavior)
```

---

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ← Previous | [16 — High Level Design](../16_high_level_design/theory.md) |
| ➡️ Next | [18 — Design Patterns](../18_design_patterns/theory.md) |
| 🏠 Home | [README.md](../README.md) |
