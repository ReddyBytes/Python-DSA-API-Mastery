# Mocking — Practice Questions

12 questions from basic Mock to full payment service capstone.

> Navigation: [theory.md](./theory.md) · [practice_local.py](./practice_local.py) · [Root practice](../practice.md)

---

### Q1 🟢 · basics — Verify a Method Was Called

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

**Problem:** Create a `Mock` object. Call `m.connect("localhost", 5432)` twice and `m.query("SELECT 1")` once. Assert: `connect` was called, `connect` was called with `("localhost", 5432)`, `connect.call_count == 2`, `query` was called with `"SELECT 1"`, and `close` was never called.

<details>
<summary>💡 Hint</summary>

`from unittest.mock import Mock`. Use `assert_called()`, `assert_called_with(args)`, `call_count`, and `assert_not_called()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import Mock

m = Mock()
m.connect("localhost", 5432)
m.connect("localhost", 5432)
m.query("SELECT 1")

m.connect.assert_called()                          # was called at all
m.connect.assert_called_with("localhost", 5432)    # last call args
assert m.connect.call_count == 2                   # exactly 2 times
m.query.assert_called_with("SELECT 1")             # last call args
m.close.assert_not_called()                        # never called
```

**Why:** Mock records every attribute access and method call automatically. The `assert_called_*` methods inspect this history. `assert_not_called()` verifies a method was never invoked — useful for proving that error-handling code doesn't proceed when it shouldn't.
</details>

---

### Q2 🟡 · MagicMock vs Mock — Dunder Methods

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

**Problem:** Demonstrate the difference: show that `len(Mock())` raises `TypeError` but `len(MagicMock())` returns `0`. Then configure a `MagicMock` so that `len(m) == 5`, `list(m) == [1, 2, 3]`, and using it as a context manager (`with m:`) calls `__enter__` and `__exit__`.

<details>
<summary>💡 Hint</summary>

Set `m.__len__.return_value = 5` and `m.__iter__.return_value = iter([1, 2, 3])`. Use `with m as ctx:` and then `m.__enter__.assert_called_once()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import Mock, MagicMock
import pytest

# Mock does NOT support dunder methods
plain = Mock()
with pytest.raises(TypeError):
    len(plain)

# MagicMock does
magic = MagicMock()
assert len(magic) == 0          # __len__ returns 0 by default

# Configure dunder behavior
m = MagicMock()
m.__len__.return_value = 5
assert len(m) == 5              # __len__ configured

m.__iter__.return_value = iter([1, 2, 3])
assert list(m) == [1, 2, 3]    # __iter__ configured

# Context manager support
with m as ctx:
    ctx.do_something()

m.__enter__.assert_called_once()
m.__exit__.assert_called_once()
```

**Why:** `Mock` gives you full control — it doesn't implement magic methods so accidental dunder calls fail loudly. `MagicMock` is the pragmatic default for mocking objects that act like containers or context managers.
</details>

---

### Q3 🟡 · patch decorator — Mock a Function in Another Module

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

**Problem:** Given a `get_weather(city)` function in `mymodule` that calls `requests.get(url)`, write a test using `@patch("mymodule.requests.get")` that: (1) sets up the mock response, (2) calls `get_weather("London")`, (3) asserts the correct URL was called, (4) asserts the return value is the mocked data.

<details>
<summary>💡 Hint</summary>

The `@patch` decorator injects the mock as the last positional parameter to the test function. Set `mock_get.return_value.json.return_value = {...}` and `mock_get.return_value.raise_for_status.return_value = None`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import patch, Mock

# Production code (mymodule.py)
def get_weather(city):
    import requests
    response = requests.get(f"https://api.example.com/weather/{city}")
    response.raise_for_status()
    return response.json()

# Test
@patch("mymodule.requests.get")             # patch WHERE IT'S USED
def test_get_weather(mock_get):
    # Arrange
    mock_response = Mock()
    mock_response.json.return_value = {"temp": 22, "condition": "sunny"}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Act
    result = get_weather("London")

    # Assert
    mock_get.assert_called_once_with("https://api.example.com/weather/London")
    assert result["temp"] == 22
    assert result["condition"] == "sunny"
```

**Why:** Patch WHERE the name is used (in `mymodule`), not where it's defined (in `requests`). This is the most common mocking mistake. If `mymodule.py` does `from requests import get`, you'd patch `"mymodule.get"` instead.
</details>

---

### Q4 🟡 · return_value — Control What a Mock Returns

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

**Problem:** Write a `NotificationService` with `notify_user(user_id, message)` that calls `repo.find_by_id(user_id)` and `emailer.send(to=..., subject=..., body=...)`. Write a test using `Mock` objects for both dependencies where `find_by_id` returns a user dict and `send` returns `True`. Assert the return value and that `send` was called with the right arguments.

<details>
<summary>💡 Hint</summary>

Set `mock_repo.find_by_id.return_value = {"id": 1, "email": "alice@example.com", "name": "Alice"}` and `mock_emailer.send.return_value = True`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import Mock

class NotificationService:
    def __init__(self, repo, emailer):
        self._repo = repo
        self._emailer = emailer

    def notify_user(self, user_id, message):
        user = self._repo.find_by_id(user_id)
        if user is None:
            return False
        return self._emailer.send(
            to=user["email"],
            subject="Notification",
            body=message
        )

def test_notify_user():
    mock_repo = Mock()
    mock_emailer = Mock()

    mock_repo.find_by_id.return_value = {
        "id": 1, "email": "alice@example.com", "name": "Alice"
    }
    mock_emailer.send.return_value = True

    service = NotificationService(mock_repo, mock_emailer)
    result = service.notify_user(1, "Your order is ready")

    assert result is True
    mock_repo.find_by_id.assert_called_once_with(1)
    mock_emailer.send.assert_called_once_with(
        to="alice@example.com",
        subject="Notification",
        body="Your order is ready"
    )
```

**Why:** Injecting mocks via the constructor is the cleanest approach — no `@patch` needed when the class receives its dependencies. `return_value` controls what the mock returns without running real code.
</details>

---

### Q5 🟡 · side_effect — Raise an Exception from a Mock

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

**Problem:** Write a test for `notify_user` where `repo.find_by_id` raises a `DatabaseError` (custom exception). Assert that `notify_user` propagates the exception and that `emailer.send` is never called.

<details>
<summary>💡 Hint</summary>

Set `mock_repo.find_by_id.side_effect = DatabaseError("connection lost")`. The mock will raise this exception when called.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import Mock
import pytest

class DatabaseError(Exception):
    pass

def test_notify_user_propagates_db_error():
    mock_repo = Mock()
    mock_emailer = Mock()

    mock_repo.find_by_id.side_effect = DatabaseError("connection lost")

    service = NotificationService(mock_repo, mock_emailer)

    with pytest.raises(DatabaseError, match="connection lost"):
        service.notify_user(1, "message")

    mock_emailer.send.assert_not_called()   # email not sent if DB fails
```

**Why:** `side_effect = ExceptionClass(...)` makes the mock raise that exception when called. This tests error handling code without a real database going down. `assert_not_called()` proves the code path stops correctly.
</details>

---

### Q6 🟡 · side_effect as list — Return Different Values Each Call

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

**Problem:** Write `send_welcome_emails(repo, emailer, user_ids)` that loops over `user_ids`, calls `repo.find_by_id(uid)` for each, and emails those found. Write a test where `find_by_id` returns `user_data` for id 1, `None` for id 2, and `user_data` for id 3 (using `side_effect` as a list). Assert that only 2 emails were sent.

<details>
<summary>💡 Hint</summary>

`mock.side_effect = [val1, val2, val3]` returns the next value from the list on each call. `None` means user not found. The email mock's `call_count` should equal the number of found users.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import Mock

def send_welcome_emails(repo, emailer, user_ids):
    sent = 0
    for uid in user_ids:
        user = repo.find_by_id(uid)
        if user:
            emailer.send(to=user["email"], subject="Welcome!", body=f"Hi {user['name']}")
            sent += 1
    return sent

def test_welcome_emails_skips_missing_users():
    mock_repo = Mock()
    mock_emailer = Mock()

    mock_repo.find_by_id.side_effect = [
        {"email": "a@ex.com", "name": "Alice"},  # uid=1 found
        None,                                      # uid=2 not found
        {"email": "c@ex.com", "name": "Charlie"}, # uid=3 found
    ]
    mock_emailer.send.return_value = True

    count = send_welcome_emails(mock_repo, mock_emailer, [1, 2, 3])

    assert count == 2                         # 2 emails sent
    assert mock_emailer.send.call_count == 2  # not 3
```

**Why:** `side_effect` as a list is perfect for testing loops — the mock returns the next item from the list on each call. This lets you simulate different database responses for different user IDs without complex logic.
</details>

---

### Q7 🟡 · patch.object — Patch a Method on a Class Instance

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

**Problem:** Given a `Counter` class with `increment()` and `reset()` methods, write a test that uses `patch.object` to patch the `reset` method on an instance, verifies it was called, then verifies the real method works after the context exits.

<details>
<summary>💡 Hint</summary>

`with patch.object(instance, "method_name") as mock_method:` patches the method on that specific instance. The real method is restored when the context exits.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import patch

class Counter:
    def __init__(self, start=0):
        self.value = start

    def increment(self):
        self.value += 1
        return self.value

    def reset(self):
        self.value = 0

def test_patch_object():
    counter = Counter(10)

    # Patch the instance method
    with patch.object(counter, "reset") as mock_reset:
        counter.reset()                    # calls mock, not real method
        mock_reset.assert_called_once()
        assert counter.value == 10         # value unchanged — mock didn't run real code

    # Real method restored after context
    counter.reset()
    assert counter.value == 0             # now real reset runs
```

**Why:** `patch.object` patches a specific object or class, not a module-level name. Use it when you have the object in hand and want to patch one of its methods. After the `with` block, the original method is restored.
</details>

---

### Q8 🟡 · assert_called_once_with — Verify Exact Arguments

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

**Problem:** Build a comprehensive test for `notify_user` that verifies: `find_by_id` was called once with `user_id=1`, `send` was called once with exactly `to="alice@example.com"`, `subject="Notification"`, `body="Order ready"`. Show the difference between `assert_called_with` and `assert_called_once_with`.

<details>
<summary>💡 Hint</summary>

`assert_called_with` checks the LAST call. `assert_called_once_with` checks that there was exactly one call AND it had these arguments. Use `from unittest.mock import call` to inspect `call_args_list`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import Mock, call

def test_exact_arguments():
    mock_repo = Mock()
    mock_emailer = Mock()

    mock_repo.find_by_id.return_value = {
        "id": 1, "email": "alice@example.com", "name": "Alice"
    }
    mock_emailer.send.return_value = True

    service = NotificationService(mock_repo, mock_emailer)
    service.notify_user(1, "Order ready")

    # assert_called_once_with: exactly ONE call with THESE args
    mock_repo.find_by_id.assert_called_once_with(1)
    mock_emailer.send.assert_called_once_with(
        to="alice@example.com",
        subject="Notification",
        body="Order ready"
    )

    # assert_called_with: checks LAST call (passes even if called 5 times)
    mock_emailer.send.assert_called_with(
        to="alice@example.com",
        subject="Notification",
        body="Order ready"
    )

    # Full call history:
    assert mock_emailer.send.call_args_list == [
        call(to="alice@example.com", subject="Notification", body="Order ready")
    ]
```

**Why:** `assert_called_once_with` is stricter — it fails if the mock was called more than once. `assert_called_with` only checks the last call. Use `assert_called_once_with` when exactly one call is part of the contract.
</details>

---

### Q9 🟡 · spec — Mock That Respects the Real Interface

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

**Problem:** Define a `UserRepository` class with methods `find_by_id(user_id)`, `save(user)`, `count()`. Write a test that: (1) creates `Mock(spec=UserRepository)`, (2) shows a valid method works, (3) shows that calling a non-existent method raises `AttributeError`, (4) creates `create_autospec(UserRepository, instance=True)` and shows it raises `TypeError` on wrong argument count.

<details>
<summary>💡 Hint</summary>

`Mock(spec=Class)` restricts attribute access to what `Class` has. `create_autospec` also checks method signatures. These catch refactoring drift — if `UserRepository` changes, tests fail.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import Mock, create_autospec
import pytest

class UserRepository:
    def find_by_id(self, user_id: int) -> dict: ...
    def save(self, user: dict) -> dict: ...
    def count(self) -> int: ...

def test_spec_restricts_interface():
    m = Mock(spec=UserRepository)

    # Valid methods work
    m.find_by_id.return_value = {"id": 1, "name": "Alice"}
    result = m.find_by_id(1)
    assert result["id"] == 1

    # Typos raise AttributeError
    with pytest.raises(AttributeError):
        m.fidn_by_id(1)       # typo — not in UserRepository

    # Non-existent method raises AttributeError
    with pytest.raises(AttributeError):
        m.nonexistent()


def test_autospec_checks_signatures():
    m = create_autospec(UserRepository, instance=True)
    m.find_by_id.return_value = None

    # Correct signature — works
    m.find_by_id(user_id=1)

    # Wrong number of args — TypeError
    with pytest.raises(TypeError):
        m.find_by_id(1, 2)    # too many positional arguments
```

**Why:** `spec` catches typos in mock method names — essential in large codebases where interfaces change. Without `spec`, `m.fidn_by_id(1)` returns a `MagicMock` silently. `create_autospec` goes further by also validating argument signatures.
</details>

---

### Q10 🟠 · patch.dict — Mock os.environ Safely

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

**Problem:** Write `get_database_config()` that reads `os.environ["DB_HOST"]`, `os.environ["DB_PORT"]`, `os.environ["DB_NAME"]` and returns a dict. Write two tests: one using `patch.dict` to set all three env vars and verify the config, another verifying that after the test the environment is restored to its original state.

<details>
<summary>💡 Hint</summary>

`with patch.dict(os.environ, {"KEY": "VALUE"}, clear=False):` adds/overrides the specified keys. They're removed/restored after the `with` block. `clear=True` replaces the entire env dict.
</details>

<details>
<summary>✅ Answer</summary>

```python
import os
from unittest.mock import patch

def get_database_config():
    return {
        "host": os.environ["DB_HOST"],
        "port": int(os.environ["DB_PORT"]),
        "name": os.environ["DB_NAME"],
    }

def test_database_config():
    with patch.dict(os.environ, {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "testdb",
    }):
        config = get_database_config()

    assert config["host"] == "localhost"
    assert config["port"] == 5432
    assert config["name"] == "testdb"

def test_env_restored_after_test():
    original_host = os.environ.get("DB_HOST")

    with patch.dict(os.environ, {"DB_HOST": "patched-host"}):
        assert os.environ["DB_HOST"] == "patched-host"

    # Restored after context:
    assert os.environ.get("DB_HOST") == original_host
```

**Why:** `patch.dict` is the safest way to test environment variable reading — it restores the original env after each test. Without it, env var mutations from one test pollute subsequent tests, causing ordering-dependent failures.
</details>

---

### Q11 🟠 · patch the right target — Where to Patch

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

**Problem:** Demonstrate the "patch where it's used" rule with two examples: (1) `mymodule.py` does `import requests` — show the correct and wrong patch target, (2) `mymodule.py` does `from os.path import exists` — show the correct and wrong patch target. Explain why each is right or wrong.

<details>
<summary>💡 Hint</summary>

When you do `import requests`, your module holds a reference to the `requests` module. Patching `mymodule.requests.get` replaces the attribute on the module object your code holds. When you do `from os.path import exists`, `mymodule.exists` is a direct reference — you must patch it there.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import patch, Mock

# ─── Case 1: import requests ───────────────────────────────

# In mymodule.py:
#   import requests
#   def fetch(url): return requests.get(url).json()

# WRONG: patches requests in the requests package, but mymodule
#        already holds a reference to the requests module object
@patch("requests.get")
def test_fetch_wrong(mock_get):
    pass   # mock may not intercept calls from mymodule

# RIGHT: patch the attribute on the module that uses it
@patch("mymodule.requests.get")
def test_fetch_right(mock_get):
    mock_get.return_value.json.return_value = {"data": 1}
    result = mymodule.fetch("https://example.com")
    assert result == {"data": 1}


# ─── Case 2: from os.path import exists ──────────────────────

# In mymodule.py:
#   from os.path import exists
#   def check_file(path): return exists(path)

# WRONG: patches the original, but mymodule.exists is already bound
@patch("os.path.exists")
def test_check_file_wrong(mock_exists):
    pass   # mymodule.check_file still calls the real exists

# RIGHT: patch the name as it lives in mymodule
@patch("mymodule.exists")
def test_check_file_right(mock_exists):
    mock_exists.return_value = True
    assert mymodule.check_file("/any/path") is True
```

**Why:** Python's import system binds names at import time. When you do `from x import y`, you get your own local reference to `y`. Patching the original `x.y` doesn't affect your local reference. Always patch WHERE the name is used.
</details>

---

### Q12 🟠 · Capstone — Test a Payment Service with Mocked External API

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

**Problem:** Implement `PaymentService` with `charge(user_id, amount)` that: (1) fetches the user from `UserRepository.find_by_id(user_id)`, (2) calls `PaymentGateway.charge(card_token, amount)`, (3) returns `{"status": "ok", "transaction_id": tx_id}` on success, (4) returns `{"status": "failed"}` if user not found, (5) propagates `PaymentError` from the gateway. Write a complete test suite using `Mock(spec=...)` for both dependencies covering all 3 scenarios.

<details>
<summary>💡 Hint</summary>

Use `Mock(spec=UserRepository)` and `Mock(spec=PaymentGateway)` for type-safe mocks. Write one test per scenario (happy path, user not found, payment error). Use `setup_method` or a fixture to create fresh mocks per test.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import Mock
import pytest

class PaymentError(Exception):
    pass

class UserRepository:
    def find_by_id(self, user_id: int): ...

class PaymentGateway:
    def charge(self, card_token: str, amount: float): ...

class PaymentService:
    def __init__(self, repo: UserRepository, gateway: PaymentGateway):
        self._repo = repo
        self._gateway = gateway

    def charge(self, user_id: int, amount: float) -> dict:
        user = self._repo.find_by_id(user_id)
        if user is None:
            return {"status": "failed", "reason": "user not found"}

        result = self._gateway.charge(user["card_token"], amount)
        return {"status": "ok", "transaction_id": result["id"]}


class TestPaymentService:

    def setup_method(self):
        self.mock_repo = Mock(spec=UserRepository)
        self.mock_gateway = Mock(spec=PaymentGateway)
        self.service = PaymentService(self.mock_repo, self.mock_gateway)

    def test_successful_charge(self):
        self.mock_repo.find_by_id.return_value = {
            "id": 1, "name": "Alice", "card_token": "tok_abc123"
        }
        self.mock_gateway.charge.return_value = {"id": "tx_001", "status": "approved"}

        result = self.service.charge(user_id=1, amount=99.99)

        assert result["status"] == "ok"
        assert result["transaction_id"] == "tx_001"
        self.mock_gateway.charge.assert_called_once_with("tok_abc123", 99.99)

    def test_user_not_found(self):
        self.mock_repo.find_by_id.return_value = None

        result = self.service.charge(user_id=999, amount=50.0)

        assert result["status"] == "failed"
        self.mock_gateway.charge.assert_not_called()   # never reached gateway

    def test_payment_gateway_error_propagates(self):
        self.mock_repo.find_by_id.return_value = {
            "id": 1, "card_token": "tok_abc123"
        }
        self.mock_gateway.charge.side_effect = PaymentError("card declined")

        with pytest.raises(PaymentError, match="card declined"):
            self.service.charge(user_id=1, amount=200.0)
```

**Why:** `spec=` makes mocks type-safe. `setup_method` creates fresh mocks per test — call history doesn't bleed between tests. Three tests cover the three code paths: success, early return, and exception propagation. This is the AAA pattern (Arrange-Act-Assert) in full.
</details>

---

## Navigation

| | |
|---|---|
| Deep dive | [theory.md](./theory.md) |
| Local practice | [practice_local.py](./practice_local.py) |
| Root practice (35 Qs) | [../practice.md](../practice.md) |
| Sibling: pytest | [../01_pytest/practice.md](../01_pytest/practice.md) |
| Sibling: unittest | [../02_unittest/practice.md](../02_unittest/practice.md) |

**[Back to README](../../README.md)**
