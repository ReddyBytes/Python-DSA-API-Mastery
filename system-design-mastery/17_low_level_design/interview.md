# 🎯 Low Level Design — Interview Questions

> LLD questions test your ability to model real systems as classes.
> Junior: basic OOP and SOLID. Mid: design patterns and state machines.
> Senior: complex class hierarchies, concurrency, extensibility trade-offs.

---

## Junior Level

### Q1. What is the SOLID principle? Explain each with one line.

**Answer:**

```
S — Single Responsibility:  One class, one reason to change
O — Open/Closed:            Open for extension, closed for modification
L — Liskov Substitution:    Subclasses must be substitutable for base class
I — Interface Segregation:  Clients should not depend on methods they don't use
D — Dependency Inversion:   Depend on abstractions, not concrete implementations
```

**SRP example:**
```python
# Bad: one class does too much
class User:
    def get_name(self): ...
    def save_to_db(self): ...        # persistence
    def send_welcome_email(self): ... # email

# Good: each class has one job
class User:
    def get_name(self): ...

class UserRepository:
    def save(self, user): ...

class UserEmailer:
    def send_welcome(self, user): ...
```

---

### Q2. What is the difference between composition and inheritance? When do you use each?

**Answer:**

```
Inheritance: IS-A relationship
  class SavingsAccount(BankAccount): ...
  Use when: subtype genuinely IS-A base type,
            behavior is shared and rarely overridden

Composition: HAS-A relationship
  class OrderService:
      def __init__(self, repo: Repository, emailer: Emailer): ...
  Use when: mixing behaviors, multiple "capabilities",
            behavior may change at runtime

Rule: "Favor composition over inheritance"
  Reason: composition is more flexible, less fragile
  Inheritance creates tight coupling — parent changes break all subclasses
```

**Bad inheritance (fragile):**
```python
class Logger:
    def log(self, msg): print(msg)

class TimestampLogger(Logger):
    def log(self, msg): super().log(f"[{datetime.now()}] {msg}")

class FileLogger(TimestampLogger):  # now coupled to both!
    def log(self, msg):
        with open("log.txt", "a") as f: f.write(msg)
        # Does this also write the timestamp? Easy to break!
```

**Better (composition):**
```python
class Logger:
    def __init__(self, formatters: list, writers: list):
        self._formatters = formatters
        self._writers = writers

    def log(self, msg: str) -> None:
        for fmt in self._formatters:
            msg = fmt.format(msg)
        for writer in self._writers:
            writer.write(msg)
```

---

### Q3. Design a Stack class. What methods should it have?

**Answer:**

```python
class StackEmptyError(Exception):
    pass

class Stack:
    def __init__(self, capacity: int | None = None):
        self._data: list = []
        self._capacity = capacity

    def push(self, item) -> None:
        if self._capacity and len(self._data) >= self._capacity:
            raise OverflowError("Stack is full")
        self._data.append(item)

    def pop(self):
        if self.is_empty():
            raise StackEmptyError("Stack is empty")
        return self._data.pop()

    def peek(self):
        if self.is_empty():
            raise StackEmptyError("Stack is empty")
        return self._data[-1]

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def size(self) -> int:
        return len(self._data)

    def __len__(self) -> int:
        return self.size()

    def __repr__(self) -> str:
        return f"Stack({self._data})"
```

**Key points to mention:**
- Custom exception (not just IndexError)
- Optional bounded capacity
- `peek` doesn't remove
- LIFO order guaranteed

---

## Mid Level

### Q4. Design a vending machine. What classes do you need?

**Answer:**

**Step 1 — Identify entities:**
```
Nouns:     VendingMachine, Product, Slot, Coin, Display
Verbs:     select product, insert coin, dispense, give change, cancel
States:    IDLE → ITEM_SELECTED → PAYMENT_PENDING → DISPENSING → IDLE
```

**Step 2 — State machine:**
```
IDLE ──select()──→ ITEM_SELECTED ──insert_coin()──→ PAYMENT_PENDING
                                        │
                              (if total >= price)
                                        │
                                  DISPENSING ──→ IDLE
                                        │
                                    give_change
```

**Step 3 — Implementation:**
```python
from enum import Enum, auto
from dataclasses import dataclass

class VMState(Enum):
    IDLE = auto()
    ITEM_SELECTED = auto()
    PAYMENT_PENDING = auto()
    DISPENSING = auto()

@dataclass
class Product:
    product_id: str
    name: str
    price: float
    quantity: int

class VendingMachine:
    def __init__(self):
        self._state = VMState.IDLE
        self._slots: dict[str, Product] = {}
        self._selected: str | None = None
        self._inserted: float = 0.0

    def load_product(self, slot_id: str, product: Product) -> None:
        self._slots[slot_id] = product

    def select(self, slot_id: str) -> str:
        if self._state != VMState.IDLE:
            return "Cancel current transaction first"
        product = self._slots.get(slot_id)
        if not product or product.quantity == 0:
            return "Product unavailable"
        self._selected = slot_id
        self._state = VMState.ITEM_SELECTED
        return f"Selected: {product.name} (${product.price:.2f})"

    def insert_coin(self, amount: float) -> str:
        if self._state not in (VMState.ITEM_SELECTED, VMState.PAYMENT_PENDING):
            return "Select a product first"
        self._inserted += amount
        self._state = VMState.PAYMENT_PENDING
        product = self._slots[self._selected]
        if self._inserted >= product.price:
            return self._dispense()
        remaining = product.price - self._inserted
        return f"Inserted: ${self._inserted:.2f}. Need: ${remaining:.2f} more"

    def cancel(self) -> float:
        refund = self._inserted
        self._reset()
        return refund

    def _dispense(self) -> str:
        product = self._slots[self._selected]
        change = self._inserted - product.price
        product.quantity -= 1
        self._state = VMState.DISPENSING
        result = f"Dispensing: {product.name}. Change: ${change:.2f}"
        self._reset()
        return result

    def _reset(self) -> None:
        self._selected = None
        self._inserted = 0.0
        self._state = VMState.IDLE
```

---

### Q5. Explain the Dependency Inversion Principle with a real example.

**Answer:**

DIP says: high-level modules should not depend on low-level modules. Both should depend on abstractions.

```python
# VIOLATION: high-level depends on low-level
class OrderService:
    def __init__(self):
        self._db = PostgresDatabase()  # tightly coupled to Postgres
        self._email = SMTPEmailer()    # tightly coupled to SMTP

# Fix: both depend on abstractions
from abc import ABC, abstractmethod

class OrderRepository(ABC):
    @abstractmethod
    def save(self, order) -> None: ...

class Emailer(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> None: ...

class OrderService:
    def __init__(self, repo: OrderRepository, emailer: Emailer):
        self._repo = repo      # abstraction injected
        self._email = emailer  # abstraction injected

# Now you can swap implementations:
service = OrderService(
    repo=PostgresOrderRepo(db_url),  # production
    emailer=SMTPEmailer(host)
)

test_service = OrderService(
    repo=InMemoryOrderRepo(),  # test — no DB needed
    emailer=MockEmailer()
)
```

**Why it matters:**
1. Tests don't need real infrastructure
2. Swap PostgreSQL → MongoDB without changing OrderService
3. Swap SMTP → SendGrid without changing OrderService
4. Each piece is independently testable

---

### Q6. Design a notification service that supports email, SMS, and push. How do you make it extensible?

**Answer:**

**Use Factory + Strategy + Open/Closed:**

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

class Channel(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"

@dataclass
class Notification:
    recipient_id: str
    subject: str
    body: str
    channels: list[Channel]

class NotificationSender(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> bool: ...

class EmailSender(NotificationSender):
    def send(self, to, subject, body):
        print(f"[EMAIL] → {to}: {subject}")
        return True

class SMSSender(NotificationSender):
    def send(self, to, subject, body):
        print(f"[SMS] → {to}: {body[:160]}")
        return True

class PushSender(NotificationSender):
    def send(self, to, subject, body):
        print(f"[PUSH] → {to}: {subject}")
        return True

class ContactRepository(ABC):
    @abstractmethod
    def get_contact(self, user_id: str, channel: Channel) -> str | None: ...

class NotificationService:
    def __init__(self, contacts: ContactRepository):
        self._contacts = contacts
        self._senders: dict[Channel, NotificationSender] = {}

    def register_sender(self, channel: Channel, sender: NotificationSender) -> None:
        """Add new channels without modifying NotificationService (OCP)."""
        self._senders[channel] = sender

    def notify(self, notification: Notification) -> dict[str, bool]:
        results = {}
        for channel in notification.channels:
            sender = self._senders.get(channel)
            if not sender:
                results[channel.value] = False
                continue
            to = self._contacts.get_contact(notification.recipient_id, channel)
            if not to:
                results[channel.value] = False
                continue
            results[channel.value] = sender.send(to, notification.subject, notification.body)
        return results

# Usage:
service = NotificationService(contacts_repo)
service.register_sender(Channel.EMAIL, EmailSender())
service.register_sender(Channel.SMS, SMSSender(twilio_client))

# To add Slack — no changes to NotificationService:
class SlackSender(NotificationSender):
    def send(self, to, subject, body):
        print(f"[SLACK] → {to}: {body}")
        return True

service.register_sender(Channel.SLACK, SlackSender(slack_token))
```

---

## Senior Level

### Q7. Design a thread-safe LRU cache.

**Answer:**

```python
from threading import RLock
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self._capacity = capacity
        self._cache: OrderedDict = OrderedDict()
        self._lock = RLock()

    def get(self, key) -> object | None:
        with self._lock:
            if key not in self._cache:
                return None
            self._cache.move_to_end(key)  # mark as recently used
            return self._cache[key]

    def put(self, key, value) -> None:
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                self._cache[key] = value
            else:
                if len(self._cache) >= self._capacity:
                    self._cache.popitem(last=False)  # evict LRU
                self._cache[key] = value

    def size(self) -> int:
        with self._lock:
            return len(self._cache)

    def __repr__(self) -> str:
        with self._lock:
            return f"LRUCache(capacity={self._capacity}, size={len(self._cache)})"
```

**Follow-up — what about distributed LRU?**
```
Single machine: threading.RLock + OrderedDict (above)
Multi-process:  Redis with ZADD (score = access time) + ZREMRANGEBYRANK
Distributed:    Redis + Lua script for atomic get-and-update
```

---

### Q8. Design an in-memory file system.

**Answer:**

```python
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

class FileSystemNode(ABC):
    def __init__(self, name: str):
        self.name = name
        self.created_at = datetime.now()
        self.modified_at = datetime.now()

    @abstractmethod
    def size(self) -> int: ...

    @abstractmethod
    def is_directory(self) -> bool: ...

class File(FileSystemNode):
    def __init__(self, name: str, content: str = ""):
        super().__init__(name)
        self._content = content

    def read(self) -> str:
        return self._content

    def write(self, content: str) -> None:
        self._content = content
        self.modified_at = datetime.now()

    def append(self, content: str) -> None:
        self._content += content
        self.modified_at = datetime.now()

    def size(self) -> int:
        return len(self._content.encode("utf-8"))

    def is_directory(self) -> bool:
        return False

class Directory(FileSystemNode):
    def __init__(self, name: str):
        super().__init__(name)
        self._children: dict[str, FileSystemNode] = {}

    def add(self, node: FileSystemNode) -> None:
        if node.name in self._children:
            raise FileExistsError(f"'{node.name}' already exists")
        self._children[node.name] = node

    def remove(self, name: str) -> None:
        if name not in self._children:
            raise FileNotFoundError(f"'{name}' not found")
        del self._children[name]

    def get(self, name: str) -> FileSystemNode | None:
        return self._children.get(name)

    def list_contents(self) -> list[str]:
        return sorted(self._children.keys())

    def size(self) -> int:
        return sum(child.size() for child in self._children.values())

    def is_directory(self) -> bool:
        return True

class FileSystem:
    def __init__(self):
        self._root = Directory("/")

    def _resolve(self, path: str) -> tuple[Directory, str]:
        """Returns (parent directory, node name) for a path."""
        if path == "/":
            return None, "/"
        parts = [p for p in path.split("/") if p]
        current = self._root
        for part in parts[:-1]:
            child = current.get(part)
            if not child or not child.is_directory():
                raise FileNotFoundError(f"Directory not found: /{'/'.join(parts[:-1])}")
            current = child
        return current, parts[-1]

    def mkdir(self, path: str) -> None:
        parent, name = self._resolve(path)
        parent.add(Directory(name))

    def touch(self, path: str) -> None:
        parent, name = self._resolve(path)
        parent.add(File(name))

    def write(self, path: str, content: str) -> None:
        parent, name = self._resolve(path)
        node = parent.get(name)
        if node is None:
            f = File(name, content)
            parent.add(f)
        elif not node.is_directory():
            node.write(content)
        else:
            raise IsADirectoryError(f"'{path}' is a directory")

    def read(self, path: str) -> str:
        parent, name = self._resolve(path)
        node = parent.get(name)
        if node is None:
            raise FileNotFoundError(f"'{path}' not found")
        if node.is_directory():
            raise IsADirectoryError(f"'{path}' is a directory")
        return node.read()

    def ls(self, path: str = "/") -> list[str]:
        if path == "/":
            return self._root.list_contents()
        parent, name = self._resolve(path)
        node = parent.get(name)
        if not node or not node.is_directory():
            raise NotADirectoryError(f"'{path}' is not a directory")
        return node.list_contents()
```

---

## 🔥 Rapid-Fire

```
Q: What does "program to an interface, not an implementation" mean?
A: Accept abstract types (ABC/Protocol), not concrete classes.
   Caller code works with any implementation.

Q: What's wrong with deep inheritance (5+ levels)?
A: Changes to parent break all subclasses. Hard to reason about.
   Use composition instead.

Q: What is the Law of Demeter?
A: "Don't talk to strangers." obj.method() OK.
   obj.getA().getB().doSomething() BAD — depends on chain.

Q: God class vs. anemic model — which is worse?
A: Both are bad. God class: one class does everything.
   Anemic model: classes have no behavior, just data — logic scattered in services.

Q: How do you test a class that creates its own DB connection?
A: You can't (easily). Fix: inject the DB via constructor (DIP).

Q: What pattern would you use for undo/redo?
A: Command pattern — each operation is a Command object with execute() and undo().

Q: When would you choose State over a series of if/elif?
A: When you have multiple states with different behaviors per state,
   and transitions between them. If/elif becomes unmaintainable.

Q: How do you enforce that only one instance of a class exists?
A: Singleton pattern via __new__. But prefer dependency injection.
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ← Previous | [16 — High Level Design](../16_high_level_design/theory.md) |
| ➡️ Next | [18 — Design Patterns](../18_design_patterns/theory.md) |
| 🏠 Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Design Patterns — Theory →](../18_design_patterns/theory.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md)
