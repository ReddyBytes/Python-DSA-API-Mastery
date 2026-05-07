# Dependency Injection

Your laptop does not care which power plant generates the electricity — it plugs into a standard outlet and gets power. The component (laptop) does not own its dependencies (electricity source); it **receives** them through a standard interface. **Dependency Injection (DI)** means a component's dependencies are provided from outside rather than created internally.

---

## 📌 Learning Priority

**Must Learn:** Constructor injection · why DI helps testing · parameter injection

**Should Learn:** Service locator · interface-based injection

**Good to Know:** DI containers (Dependency Injector library) · Provider pattern

**Reference:** Abstract factory as DI

---

## 1. The Problem: Tight Coupling

When a class creates its own dependencies, it becomes tightly coupled to them. Changing the dependency means changing the class. Testing the class means using the real dependency.

```python
# Tightly coupled — bad
class UserService:
    def __init__(self):
        self.db = PostgresDatabase()    # ← hardcoded concrete class
        self.logger = FileLogger()      # ← hardcoded concrete class

    def get_user(self, user_id: int) -> dict:
        self.logger.log(f"Fetching user {user_id}")
        return self.db.query(f"SELECT * FROM users WHERE id = {user_id}")
```

Problems:
- To test `get_user`, you need a real Postgres database running
- Switching to MySQL means editing `UserService`
- You cannot test the logger behavior without checking real files

---

## 2. Constructor Injection

The most common and recommended form of DI. Dependencies are declared as constructor parameters.

```python
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def query(self, sql: str) -> list: ...

class Logger(ABC):
    @abstractmethod
    def log(self, message: str) -> None: ...

# Loosely coupled — good
class UserService:
    def __init__(self, db: Database, logger: Logger):   # ← injected
        self.db     = db
        self.logger = logger

    def get_user(self, user_id: int) -> dict:
        self.logger.log(f"Fetching user {user_id}")
        return self.db.query(f"SELECT * FROM users WHERE id = {user_id}")
```

```python
# Production
from postgres_db import PostgresDatabase
from file_logger import FileLogger

service = UserService(db=PostgresDatabase(), logger=FileLogger())

# Test — no real DB, no real files
class MockDatabase(Database):
    def query(self, sql: str) -> list:
        return [{"id": 1, "name": "Alice"}]

class MockLogger(Logger):
    def __init__(self):
        self.messages = []
    def log(self, message: str) -> None:
        self.messages.append(message)

mock_db  = MockDatabase()
mock_log = MockLogger()
test_service = UserService(db=mock_db, logger=mock_log)
result = test_service.get_user(1)
assert result[0]["name"] == "Alice"
assert "Fetching user 1" in mock_log.messages
```

**Why constructor injection is preferred:**
- Dependencies are visible at construction time (no hidden surprises)
- The class is immutable once constructed (no half-initialized state)
- Makes required dependencies explicit (if you do not pass them, you get a `TypeError`)

### 2.1 Constructor Injection vs Method Injection

```python
# Method injection — dependency provided per-call
class ReportService:
    def generate(self, data: list, renderer) -> str:   # ← injected per call
        return renderer.render(data)

# Use when: the dependency varies per call, not per instance
report = ReportService()
output = report.generate(data, HTMLRenderer())
output = report.generate(data, PDFRenderer())
```

Use method injection when the dependency changes with each invocation. Use constructor injection when the dependency is stable for the lifetime of the object.

---

## 3. Service Locator Pattern

A **service locator** is a registry that maps service names to instances. Components look up their dependencies from the locator instead of having them injected.

```python
class ServiceLocator:
    _services: dict = {}

    @classmethod
    def register(cls, name: str, instance) -> None:
        cls._services[name] = instance

    @classmethod
    def get(cls, name: str):
        if name not in cls._services:
            raise KeyError(f"Service not registered: {name!r}")
        return cls._services[name]
```

```python
# Registration (done at startup)
ServiceLocator.register("db",     PostgresDatabase())
ServiceLocator.register("logger", FileLogger())

# Usage inside a component
class UserService:
    def get_user(self, user_id: int):
        db     = ServiceLocator.get("db")       # ← pull dependency from locator
        logger = ServiceLocator.get("logger")
        logger.log(f"Fetching {user_id}")
        return db.query(f"SELECT * FROM users WHERE id = {user_id}")
```

### Service Locator vs Constructor Injection

| Aspect | Constructor Injection | Service Locator |
|---|---|---|
| Dependencies visible? | Yes — in `__init__` signature | No — hidden inside method body |
| Testability | High — pass mocks to constructor | Moderate — must configure locator for tests |
| Flexibility | Explicit, clear | Flexible but hidden |
| Recommended? | Preferred | Use for late-binding or framework bootstrapping |

**The main criticism of Service Locator:** dependencies are hidden. Reading the class signature does not tell you what it needs. Constructor injection is more honest.

---

## 4. Testing with DI — Why It Matters

DI is not about abstraction for its own sake. The primary practical benefit is **testability**.

```python
# Scenario: email service that charges money
class EmailGateway(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> bool: ...

class SendGridGateway(EmailGateway):
    def send(self, to, subject, body) -> bool:
        # makes real HTTP call, costs money in production
        ...

class NotificationService:
    def __init__(self, gateway: EmailGateway):
        self._gateway = gateway

    def notify_user(self, user_email: str, event: str) -> bool:
        return self._gateway.send(
            to=user_email,
            subject=f"Event: {event}",
            body=f"You have a new event: {event}"
        )
```

```python
# Test — no HTTP calls, no cost, fully inspectable
class MockEmailGateway(EmailGateway):
    def __init__(self):
        self.sent_emails: list[dict] = []

    def send(self, to, subject, body) -> bool:
        self.sent_emails.append({"to": to, "subject": subject})
        return True

def test_notify_user():
    mock_gateway = MockEmailGateway()
    service      = NotificationService(gateway=mock_gateway)

    result = service.notify_user("alice@example.com", "login")

    assert result is True
    assert len(mock_gateway.sent_emails) == 1
    assert mock_gateway.sent_emails[0]["to"] == "alice@example.com"
```

**The pattern:** swap the real dependency for a **test double** (mock, stub, or spy) by injecting it at construction time.

---

## 5. Python-Specific Patterns

Python does not need a DI framework for most use cases. Constructor injection with ABCs or duck typing is usually sufficient.

### 5.1 Protocol-Based Injection (Python 3.8+)

`Protocol` from `typing` lets you define structural interfaces without inheritance. Any class with the right methods satisfies the protocol.

```python
from typing import Protocol

class DatabaseProtocol(Protocol):
    def query(self, sql: str) -> list: ...   # ← structural interface

class UserService:
    def __init__(self, db: DatabaseProtocol):   # ← any object with .query() works
        self.db = db

# Works with any class that has a .query() method — no inheritance needed
class InMemoryDB:
    def query(self, sql: str) -> list:
        return [{"id": 1, "name": "Test"}]

service = UserService(db=InMemoryDB())   # ← valid despite no explicit inheritance
```

### 5.2 Default Dependency with Override

A common pragmatic pattern: provide a sensible default but allow override in tests.

```python
class EmailService:
    def send(self, to: str, subject: str) -> bool:
        # real implementation
        return True

class UserRegistration:
    def __init__(self, email_service: EmailService = None):
        self._email = email_service or EmailService()   # ← default to real impl

    def register(self, email: str) -> dict:
        user = {"email": email, "active": True}
        self._email.send(email, "Welcome!")
        return user
```

**Trade-off:** Slightly hidden default, but reduces boilerplate for callers who want the default behavior.

### 5.3 When DI Containers Make Sense

For large applications with many services, wiring dependencies manually becomes tedious. A **DI container** auto-wires dependencies based on type annotations.

```python
# Using the `dependency_injector` library (pip install dependency-injector)
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    db              = providers.Singleton(PostgresDatabase, url="postgresql://...")
    logger          = providers.Singleton(FileLogger, path="/var/log/app.log")
    user_service    = providers.Factory(UserService, db=db, logger=logger)

# Auto-wired — Container resolves the dependency graph
container = Container()
service   = container.user_service()
```

**Use a DI container when:** you have 10+ services with complex dependency graphs and manual wiring becomes error-prone.

---

## 6. Common Mistakes

- **Not using DI and regretting it at test time.** The most common mistake is realizing you cannot test a class because it creates its own DB connection internally.
- **Over-abstracting for DI's sake.** You do not need an ABC for every dependency. If a class will only ever have one implementation, skip the interface.
- **Service Locator as a crutch.** It hides dependencies. Prefer constructor injection when possible.
- **Injecting too many dependencies.** If a constructor takes 8 parameters, the class is doing too much. Break it up.
- **Confusing DI with a framework.** DI is a pattern, not a library. `UserService(db=db)` is dependency injection.

---

## 📂 Navigation

**[🏠 Back to README](../../README.md)**

**Prev:** [← 02 Behavioral](../02_behavioral/theory.md) &nbsp;|&nbsp; **Next:** [Root Theory →](../theory.md)

**Related Topics:** [01 Creational](../01_creational/theory.md) · [02 Behavioral](../02_behavioral/theory.md) · [Root Theory](../theory.md)
