# Dependency Injection — Practice Questions

8 questions covering constructor injection, service locator, testing with DI, and advanced patterns.

---

### Q1 🟢 · di · Constructor Injection: Decouple Database from Service

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

**Problem:** Refactor this tightly coupled code to use constructor injection:

```python
class UserService:
    def __init__(self):
        self.db = PostgresDatabase()  # hardcoded

    def get_user(self, user_id): return self.db.query(user_id)
```

Define a `Database` ABC. Inject the database via `__init__`. Write a `MockDatabase` for testing.

<details>
<summary>💡 Hint</summary>
The constructor becomes `__init__(self, db: Database)`. The caller passes either a real or mock DB.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def query(self, user_id: int) -> dict: ...

class UserService:
    def __init__(self, db: Database):   # ← injected
        self.db = db

    def get_user(self, user_id: int) -> dict:
        return self.db.query(user_id)

# Test double
class MockDatabase(Database):
    def query(self, user_id: int) -> dict:
        return {"id": user_id, "name": "Alice"}

service = UserService(db=MockDatabase())
result  = service.get_user(1)
assert result == {"id": 1, "name": "Alice"}
```

**Why:** The service no longer imports or instantiates `PostgresDatabase`. Tests pass a mock. Production code passes the real DB.
</details>

---

### Q2 🟡 · di · Method Injection: Inject Logger Per Call

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

**Problem:** Build a `DataProcessor.process(data, logger)` where the logger is injected per call (method injection). Define a `Logger` ABC with `log(message)`. Write a `CapturingLogger` that stores messages for assertions.

<details>
<summary>💡 Hint</summary>
The logger is a parameter of the method, not the constructor. Different callers can pass different loggers.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class Logger(ABC):
    @abstractmethod
    def log(self, message: str) -> None: ...

class CapturingLogger(Logger):
    def __init__(self):
        self.messages: list[str] = []

    def log(self, message: str) -> None:
        self.messages.append(message)

class DataProcessor:
    def process(self, data: list, logger: Logger) -> list:   # ← injected per call
        logger.log(f"Processing {len(data)} items")
        result = [x * 2 for x in data if isinstance(x, (int, float))]
        logger.log(f"Produced {len(result)} results")
        return result

logger    = CapturingLogger()
processor = DataProcessor()
result    = processor.process([1, 2, "skip", 3], logger)
assert result == [2, 4, 6]
assert len(logger.messages) == 2
assert "Processing 4 items" in logger.messages[0]
```

**Why:** Method injection is appropriate when the dependency varies per call. The processor can use different loggers for different operations.
</details>

---

### Q3 🟡 · di · Service Locator: Simple Registry

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

**Problem:** Build a `ServiceLocator` with `register(name, instance)` and `get(name)`. Raise `KeyError` for unregistered services. Register a `database` and `logger` service. Retrieve and use them.

<details>
<summary>💡 Hint</summary>
A class-level `_services = {}` dict stores name → instance mappings.
</details>

<details>
<summary>✅ Answer</summary>

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

    @classmethod
    def reset(cls) -> None:
        cls._services = {}   # for tests

class InMemoryDB:
    def query(self, sql): return [{"id": 1}]

class PrintLogger:
    def log(self, msg): print(msg)

ServiceLocator.register("db",     InMemoryDB())
ServiceLocator.register("logger", PrintLogger())

db     = ServiceLocator.get("db")
logger = ServiceLocator.get("logger")
assert db.query("SELECT 1") == [{"id": 1}]

try:
    ServiceLocator.get("cache")
except KeyError as e:
    assert "cache" in str(e)
```

**Why:** The locator acts as a central registry. Components pull dependencies by name. The downside: dependencies are hidden inside method bodies rather than visible in signatures.
</details>

---

### Q4 🟡 · di · DI for Testing: Inject Mock vs Real DB

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

**Problem:** Build a `UserRepository` that takes a `Database` dependency. Write a full test scenario: `MockDatabase` returns a fixed user, spy on how many queries were made, and assert the `UserRepository.find_by_email(email)` method returns the right result.

<details>
<summary>💡 Hint</summary>
Add a `query_count` attribute to the mock. Increment it in `query()`. Assert `query_count == 1` after one call.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def fetch(self, query: str, params: dict) -> list: ...

class MockDatabase(Database):
    def __init__(self, rows: list):
        self.rows        = rows
        self.query_count = 0

    def fetch(self, query: str, params: dict) -> list:
        self.query_count += 1
        email = params.get("email")
        return [r for r in self.rows if r.get("email") == email]

class UserRepository:
    def __init__(self, db: Database):
        self._db = db

    def find_by_email(self, email: str) -> dict | None:
        rows = self._db.fetch(
            "SELECT * FROM users WHERE email = :email",
            {"email": email}
        )
        return rows[0] if rows else None

mock_db = MockDatabase([
    {"id": 1, "email": "alice@example.com", "name": "Alice"},
    {"id": 2, "email": "bob@example.com",   "name": "Bob"},
])

repo = UserRepository(db=mock_db)
user = repo.find_by_email("alice@example.com")
assert user["name"]        == "Alice"
assert mock_db.query_count == 1

missing = repo.find_by_email("nobody@example.com")
assert missing is None
assert mock_db.query_count == 2
```

**Why:** The mock lets you test the repository's logic (query construction, result mapping) without a real database. The spy (query_count) verifies behavior at the call level.
</details>

---

### Q5 🟡 · di · Parameter Injection: Inject Config at Call Time

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

**Problem:** Build an `EmailSender.send(to, subject, config)` where `config` is injected per call. `config` is a dict with `smtp_host`, `smtp_port`, `from_address`. Write a test that verifies the sender uses the injected config values.

<details>
<summary>💡 Hint</summary>
The method stores the config values it used for inspection. A `CapturingSender` can record calls for assertions.
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass

@dataclass
class EmailConfig:
    smtp_host:    str
    smtp_port:    int
    from_address: str

class EmailSender:
    def send(self, to: str, subject: str, config: EmailConfig) -> dict:
        # In production: use config to connect to SMTP
        return {
            "to":        to,
            "subject":   subject,
            "from":      config.from_address,
            "smtp_host": config.smtp_host,
            "smtp_port": config.smtp_port,
            "sent":      True,
        }

prod_config = EmailConfig("smtp.sendgrid.com", 587, "noreply@myapp.com")
test_config = EmailConfig("localhost",          1025, "test@localhost")

sender = EmailSender()
prod_result = sender.send("alice@example.com", "Welcome!", prod_config)
test_result = sender.send("alice@example.com", "Welcome!", test_config)

assert prod_result["smtp_host"] == "smtp.sendgrid.com"
assert test_result["smtp_host"] == "localhost"
assert test_result["from"]      == "test@localhost"
```

**Why:** Injecting config per call is useful when the same service is used with different configurations in the same run (e.g., different email providers for different tenants).
</details>

---

### Q6 🟠 · di · DI with ABC: Interface-Based Injection

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

**Problem:** Define `StorageBackend` and `CompressionStrategy` ABCs. Build a `FileUploader` that accepts both via constructor injection. Implement `S3Backend`, `LocalBackend`, `GzipCompression`, and `NoCompression`. Wire them up in two configurations: prod (S3 + Gzip) and test (Local + NoCompression).

<details>
<summary>💡 Hint</summary>
`FileUploader.__init__` takes `storage: StorageBackend` and `compression: CompressionStrategy`. The upload method calls both in sequence.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class StorageBackend(ABC):
    @abstractmethod
    def save(self, path: str, data: bytes) -> str: ...

class CompressionStrategy(ABC):
    @abstractmethod
    def compress(self, data: bytes) -> bytes: ...

class S3Backend(StorageBackend):
    def save(self, path: str, data: bytes) -> str:
        return f"s3://my-bucket/{path}"

class LocalBackend(StorageBackend):
    def __init__(self):
        self.stored: dict[str, bytes] = {}
    def save(self, path: str, data: bytes) -> str:
        self.stored[path] = data
        return f"/tmp/{path}"

class GzipCompression(CompressionStrategy):
    def compress(self, data: bytes) -> bytes:
        import gzip
        return gzip.compress(data)

class NoCompression(CompressionStrategy):
    def compress(self, data: bytes) -> bytes:
        return data

class FileUploader:
    def __init__(self, storage: StorageBackend, compression: CompressionStrategy):
        self._storage     = storage
        self._compression = compression

    def upload(self, path: str, data: bytes) -> str:
        compressed = self._compression.compress(data)
        return self._storage.save(path, compressed)

# Production config
s3_uploader    = FileUploader(S3Backend(), GzipCompression())
url            = s3_uploader.upload("data.csv", b"col1,col2\n1,2")
assert url.startswith("s3://")

# Test config
local_backend  = LocalBackend()
test_uploader  = FileUploader(local_backend, NoCompression())
path           = test_uploader.upload("data.csv", b"col1,col2\n1,2")
assert path.startswith("/tmp/")
assert b"col1,col2" in local_backend.stored["data.csv"]
```

**Why:** Two ABCs define the contracts. `FileUploader` works with any combination of storage and compression. Swapping one changes behavior without modifying the uploader.
</details>

---

### Q7 🟠 · di · Compare Tight vs Loose Coupling

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

**Problem:** You are given tightly coupled code. Identify the problems, then rewrite it with constructor injection. Show that the refactored version is testable without external dependencies.

```python
# Tightly coupled — fix this
class OrderService:
    def __init__(self):
        self.db    = MySQLDatabase(host="prod-db", port=3306)
        self.email = SMTPEmailer(host="smtp.sendgrid.com")

    def place_order(self, user_id, items):
        order = self.db.insert("orders", {"user_id": user_id, "items": items})
        self.email.send(f"user_{user_id}@example.com", "Order confirmed")
        return order
```

<details>
<summary>💡 Hint</summary>
Define `Database` and `Emailer` ABCs. Change `__init__` to accept them as parameters.
</details>

<details>
<summary>✅ Answer</summary>

```python
# Problems with original:
# 1. Cannot test without a real MySQL database running
# 2. Cannot test without a real SMTP server
# 3. Changing DB engine requires editing OrderService
# 4. Dependencies are invisible to callers

from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def insert(self, table: str, data: dict) -> dict: ...

class Emailer(ABC):
    @abstractmethod
    def send(self, to: str, subject: str) -> bool: ...

# Fixed
class OrderService:
    def __init__(self, db: Database, emailer: Emailer):
        self._db      = db
        self._emailer = emailer

    def place_order(self, user_id: int, items: list) -> dict:
        order = self._db.insert("orders", {"user_id": user_id, "items": items})
        self._emailer.send(f"user_{user_id}@example.com", "Order confirmed")
        return order

# Test doubles
class MockDB(Database):
    def __init__(self):
        self.inserts = []
    def insert(self, table, data):
        entry = {**data, "id": len(self.inserts) + 1}
        self.inserts.append(entry)
        return entry

class MockEmailer(Emailer):
    def __init__(self):
        self.sent = []
    def send(self, to, subject):
        self.sent.append({"to": to, "subject": subject})
        return True

db      = MockDB()
emailer = MockEmailer()
service = OrderService(db=db, emailer=emailer)
order   = service.place_order(user_id=42, items=["widget"])

assert order["id"]         == 1
assert len(emailer.sent)   == 1
assert emailer.sent[0]["to"] == "user_42@example.com"
```

**Why:** Constructor injection makes all dependencies explicit and replaceable. Tests run instantly with no external services.
</details>

---

### Q8 🟠 · di · Capstone: Data Pipeline with Injected Source and Sink

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

**Problem:** Build a `DataPipeline` with injected `DataSource` (has `read() -> list`) and `DataSink` (has `write(data: list) -> int`). Add an optional `transform` callable parameter (default: identity). Run the pipeline and return a summary `{"rows_read": N, "rows_written": M}`.

<details>
<summary>💡 Hint</summary>
The pipeline reads from source, optionally transforms, writes to sink. All three are injected. Write a `CollectingSink` that stores rows for test assertions.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod
from typing import Callable

class DataSource(ABC):
    @abstractmethod
    def read(self) -> list: ...

class DataSink(ABC):
    @abstractmethod
    def write(self, data: list) -> int: ...

class DataPipeline:
    def __init__(
        self,
        source:    DataSource,
        sink:      DataSink,
        transform: Callable[[list], list] = None,
    ):
        self._source    = source
        self._sink      = sink
        self._transform = transform or (lambda x: x)

    def run(self) -> dict:
        data         = self._source.read()
        rows_read    = len(data)
        transformed  = self._transform(data)
        rows_written = self._sink.write(transformed)
        return {"rows_read": rows_read, "rows_written": rows_written}

# Test doubles
class FixedSource(DataSource):
    def __init__(self, rows: list):
        self._rows = rows
    def read(self) -> list:
        return list(self._rows)

class CollectingSink(DataSink):
    def __init__(self):
        self.written: list = []
    def write(self, data: list) -> int:
        self.written.extend(data)
        return len(data)

source    = FixedSource([{"value": 1}, {"value": 2}, {"value": None}])
sink      = CollectingSink()
pipeline  = DataPipeline(
    source    = source,
    sink      = sink,
    transform = lambda rows: [r for r in rows if r["value"] is not None],
)

summary = pipeline.run()
assert summary["rows_read"]    == 3
assert summary["rows_written"] == 2
assert len(sink.written)       == 2
assert all(r["value"] is not None for r in sink.written)
```

**Why:** All three components (source, sink, transform) are injected. The pipeline orchestrates them without knowing their concrete types. Swapping source from CSV file to API or sink from DB to S3 requires only changing what is injected.
</details>

---

## 📂 Navigation

**[🏠 Back to README](../../README.md)**

**Prev:** [← 02 Behavioral — Practice](../02_behavioral/practice.md) &nbsp;|&nbsp; **Next:** [Root Theory →](../theory.md)

**Related Topics:** [Theory](./theory.md) · [02 Behavioral](../02_behavioral/practice.md) · [Root Practice](../practice.md)
