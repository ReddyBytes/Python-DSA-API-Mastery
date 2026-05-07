# Testing in Python — Practice Questions

35 questions from first test to full end-to-end suite capstone.

> Subfolders: [01_pytest/practice.md](./01_pytest/practice.md) · [02_unittest/practice.md](./02_unittest/practice.md) · [03_mocking/practice.md](./03_mocking/practice.md)

---

## pytest Basics (Q1–Q5)

### Q1 🟢 · pytest · Write a Test Function

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

**Problem:** Write `add(a, b)`. Write `test_add` using plain `assert` to verify three cases: (2,3)→5, (-1,1)→0, (0,0)→0.

<details>
<summary>💡 Hint</summary>

pytest discovers any function named `test_*`. No class or imports needed.
</details>

<details>
<summary>✅ Answer</summary>

```python
def add(a, b): return a + b

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
```

**Why:** Plain `assert` — pytest rewrites it to show rich diffs on failure.
</details>

---

### Q2 🟢 · pytest · assert with Multiple Types

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

**Problem:** Write `test_various_assertions` that uses plain `assert` to check: a list contains an item, a variable is None, a float is approximately 0.3, and a string starts with a prefix.

<details>
<summary>💡 Hint</summary>

Use `pytest.approx` for the float check. Use `str.startswith()` for the prefix check.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pytest

def test_various_assertions():
    items = [1, 2, 3]
    result = None
    total = 0.1 + 0.2
    message = "Hello, World"

    assert 2 in items
    assert result is None
    assert total == pytest.approx(0.3)
    assert message.startswith("Hello")
```

**Why:** pytest's assert rewriting gives meaningful failure messages for all these patterns without needing named assertion methods.
</details>

---

### Q3 🟡 · pytest · Fixtures as Setup

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

**Problem:** Write a `@pytest.fixture` called `empty_cart` that returns a `ShoppingCart()`. Write two tests using it: one checks `is_empty()` is True, another adds an item and checks `total()`.

<details>
<summary>💡 Hint</summary>

The fixture function name is the parameter name in the test. Each test gets a fresh instance.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pytest

class ShoppingCart:
    def __init__(self): self._items = {}
    def add_item(self, name, price): self._items[name] = price
    def total(self): return sum(self._items.values())
    def is_empty(self): return len(self._items) == 0

@pytest.fixture
def empty_cart():
    return ShoppingCart()

def test_new_cart_is_empty(empty_cart):
    assert empty_cart.is_empty()

def test_add_item_updates_total(empty_cart):
    empty_cart.add_item("apple", 1.50)
    assert empty_cart.total() == pytest.approx(1.50)
```

**Why:** Fixtures replace setUp — injected by name, scoped to the test, fresh per call.
</details>

---

### Q4 🟡 · pytest · parametrize Basics

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

**Problem:** Write `is_prime(n)`. Use `@pytest.mark.parametrize` to test it with at least 6 cases (primes and non-primes).

<details>
<summary>💡 Hint</summary>

Format: `@pytest.mark.parametrize("n, expected", [(2, True), ...])`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pytest

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True

@pytest.mark.parametrize("n, expected", [
    (2,   True),
    (3,   True),
    (4,   False),
    (17,  True),
    (100, False),
    (1,   False),
    (0,   False),
    (-1,  False),
])
def test_is_prime(n, expected):
    assert is_prime(n) == expected
```

**Why:** 8 independent test cases from one function. One failure doesn't stop the rest.
</details>

---

### Q5 🟡 · pytest · pytest.raises

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

**Problem:** Write `divide(a, b)` that raises `ZeroDivisionError` with message "cannot divide by zero". Write two tests: one checks the exception type, one checks the message with `match`.

<details>
<summary>💡 Hint</summary>

`with pytest.raises(ExcType, match="pattern"):`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pytest

def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("cannot divide by zero")
    return a / b

def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_divide_by_zero_message():
    with pytest.raises(ZeroDivisionError, match="cannot divide by zero"):
        divide(10, 0)
```

**Why:** `pytest.raises` is cleaner than try/except — if no exception is raised, the test fails automatically.
</details>

---

## pytest Advanced (Q6–Q9)

### Q6 🟡 · pytest · Fixture Scope

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

**Problem:** Explain and demonstrate the four main fixture scopes: `function`, `class`, `module`, `session`. Write one example fixture for each scope with a comment explaining when to use it.

<details>
<summary>💡 Hint</summary>

`@pytest.fixture(scope="module")` — the fixture is created once per file. The wider the scope, the cheaper but less isolated.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pytest

@pytest.fixture(scope="function")   # default: fresh per test — for mutable state
def fresh_db():
    return {"users": []}

@pytest.fixture(scope="class")      # once per test class — for class-level shared state
def class_config():
    return {"env": "test"}

@pytest.fixture(scope="module")     # once per file — for expensive read-only setup
def shared_user():
    return {"name": "Alice", "age": 25}

@pytest.fixture(scope="session")    # once per entire run — for server/DB startup
def app_server():
    server = {"url": "http://localhost:8000"}
    yield server
    # server.stop() if real server
```

**Why:** Scope balances test isolation vs setup cost. Use narrow scope (function) for mutable objects, wider scope (session) only for expensive read-only resources.
</details>

---

### Q7 🟡 · pytest · conftest.py

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

**Problem:** Write the content of a `conftest.py` that provides: a `db` fixture (in-memory SQLite), a `sample_user` fixture that depends on `db` and inserts a user. Show how both are used in a test file without any imports.

<details>
<summary>💡 Hint</summary>

Fixtures in `conftest.py` are available to all tests in the same directory tree. No `import` needed — pytest injects them by name.
</details>

<details>
<summary>✅ Answer</summary>

```python
# conftest.py
import pytest
import sqlite3

@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    yield conn
    conn.close()

@pytest.fixture
def sample_user(db):   # depends on db fixture
    db.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')")
    db.commit()
    return {"id": 1, "name": "Alice", "email": "alice@example.com"}


# test_users.py  ← no import of conftest needed
def test_user_in_db(sample_user, db):
    row = db.execute("SELECT name FROM users WHERE id=1").fetchone()
    assert row[0] == "Alice"
```

**Why:** `conftest.py` is pytest's dependency injection container. Fixtures compose — `sample_user` gets `db` automatically.
</details>

---

### Q8 🟡 · pytest · Custom Markers and skip

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

**Problem:** Write tests marked with `@pytest.mark.slow`, `@pytest.mark.skip`, and `@pytest.mark.xfail`. Show the `pytest.ini` registration for custom markers. Show the commands to run only slow tests and to exclude them.

<details>
<summary>💡 Hint</summary>

Custom markers need to be registered in `pytest.ini` under `[pytest] markers =` to avoid warnings. Run with `pytest -m slow` or `pytest -m "not slow"`.
</details>

<details>
<summary>✅ Answer</summary>

```ini
# pytest.ini
[pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests requiring external services
```

```python
import sys
import pytest

@pytest.mark.slow
def test_heavy_computation():
    result = sum(range(10_000_000))
    assert result > 0

@pytest.mark.skip(reason="Cache layer not yet implemented")
def test_cache_hit():
    assert False   # never runs

@pytest.mark.xfail(reason="Known precision bug — issue #99")
def test_float_precision():
    assert 0.1 + 0.2 == 0.3   # expected failure

# Run:  pytest -m slow
# Skip: pytest -m "not slow"
```

**Why:** Markers let you categorize and filter tests. `skip` for unimplemented, `xfail` for known broken. Always register custom markers to get warnings when typos create undefined markers.
</details>

---

### Q9 🟡 · pytest · Async Testing

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

**Problem:** Write `async def fetch_data(repo, key)` that calls `await repo.get(key)`. Write an async test using `pytest-asyncio` and `AsyncMock` that verifies the function returns the mocked value and calls `repo.get` with the correct key.

<details>
<summary>💡 Hint</summary>

`pip install pytest-asyncio`. Mark the test `@pytest.mark.asyncio`. Use `AsyncMock` for the repo. Use `assert_awaited_once_with` not `assert_called_once_with`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pytest
from unittest.mock import AsyncMock

async def fetch_data(repo, key):
    return await repo.get(key)

@pytest.mark.asyncio
async def test_fetch_data():
    mock_repo = AsyncMock()
    mock_repo.get.return_value = {"value": 42}

    result = await fetch_data(mock_repo, "mykey")

    assert result["value"] == 42
    mock_repo.get.assert_awaited_once_with("mykey")
```

**Why:** `AsyncMock` wraps return values in coroutines so they can be awaited. `assert_awaited_once_with` verifies the mock was awaited (not just called) with the right args.
</details>

---

## unittest (Q10–Q14)

### Q10 🟡 · unittest · TestCase and setUp

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

**Problem:** Write a `TestCase` for a `BankAccount` class with `deposit`, `withdraw`, and `balance`. Use `setUp` to create a fresh account before each test.

<details>
<summary>💡 Hint</summary>

`setUp` is called before every test method. Use `self.account = BankAccount(...)`. Use `assertEqual`, `assertAlmostEqual`, `assertRaises`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import unittest

class BankAccount:
    def __init__(self, balance=0):
        self._balance = balance
    @property
    def balance(self): return self._balance
    def deposit(self, amount):
        if amount <= 0: raise ValueError("Must be positive")
        self._balance += amount
    def withdraw(self, amount):
        if amount > self._balance: raise ValueError("Insufficient funds")
        self._balance -= amount

class TestBankAccount(unittest.TestCase):
    def setUp(self):
        self.account = BankAccount(100)

    def test_initial_balance(self):
        self.assertEqual(self.account.balance, 100)

    def test_deposit(self):
        self.account.deposit(50)
        self.assertEqual(self.account.balance, 150)

    def test_withdraw(self):
        self.account.withdraw(30)
        self.assertEqual(self.account.balance, 70)

    def test_overdraft_raises(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(200)
```

**Why:** `setUp` guarantees each test starts with a fresh `BankAccount(100)` — mutations in one test don't affect others.
</details>

---

### Q11 🟡 · unittest · assertRaises and assertRaisesRegex

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

**Problem:** Write `parse_int(s)` that raises `ValueError` with "invalid literal" for non-numeric strings. Write two unittest tests: one checks the exception type, one checks the message.

<details>
<summary>💡 Hint</summary>

`assertRaisesRegex(ExcType, "pattern")` is unittest's equivalent of `pytest.raises(ExcType, match="pattern")`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import unittest

def parse_int(s):
    try:
        return int(s)
    except ValueError:
        raise ValueError(f"invalid literal: {s!r}")

class TestParseInt(unittest.TestCase):
    def test_invalid_raises(self):
        with self.assertRaises(ValueError):
            parse_int("abc")

    def test_invalid_message(self):
        with self.assertRaisesRegex(ValueError, "invalid literal"):
            parse_int("not-a-number")
```

**Why:** `assertRaisesRegex` is more specific — it fails if the right exception is raised but with the wrong message, catching bugs where exception handling swallows the real error.
</details>

---

### Q12 🟡 · unittest · setUpClass for Expensive Resources

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

**Problem:** Write a `TestCase` with `setUpClass` that initializes a `FakeDatabase` dict once. Write three tests that all read from it. Show that the database is created only once across all tests.

<details>
<summary>💡 Hint</summary>

`@classmethod` + `setUpClass(cls)`. Store data on `cls.db`. Tests access it as `self.db`. Never mutate class-level state in tests.
</details>

<details>
<summary>✅ Answer</summary>

```python
import unittest

class TestSharedSetup(unittest.TestCase):
    _setup_count = 0   # to prove it runs once

    @classmethod
    def setUpClass(cls):
        cls._setup_count += 1
        cls.db = {
            1: {"name": "Alice", "role": "admin"},
            2: {"name": "Bob",   "role": "user"},
        }

    def test_setup_runs_once(self):
        self.assertEqual(self._setup_count, 1)

    def test_find_alice(self):
        self.assertEqual(self.db[1]["name"], "Alice")

    def test_admin_role(self):
        self.assertEqual(self.db[1]["role"], "admin")
```

**Why:** `setUpClass` runs once before all tests in the class — good for expensive, read-only initialization. `setUp` would create the database 3 times for 3 tests.
</details>

---

### Q13 🟡 · unittest · subTest

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)

**Problem:** Write a `TestCase` that tests `is_palindrome` with 5 cases using `subTest`. Demonstrate that all 5 run even if one fails.

<details>
<summary>💡 Hint</summary>

`with self.subTest(label=label, input=word):` in a loop. Each `subTest` block is reported independently.
</details>

<details>
<summary>✅ Answer</summary>

```python
import unittest

def is_palindrome(s):
    s = s.lower().replace(" ", "")
    return s == s[::-1]

class TestPalindrome(unittest.TestCase):
    def test_palindrome_cases(self):
        cases = [
            ("racecar", True,  "simple"),
            ("hello",   False, "non-palindrome"),
            ("A man a plan a canal Panama", True, "famous"),
            ("",        True,  "empty"),
            ("Madam",   True,  "case-insensitive"),
        ]
        for word, expected, label in cases:
            with self.subTest(label=label, word=word):
                self.assertEqual(is_palindrome(word), expected)
```

**Why:** Without `subTest`, the loop stops at the first failure. With `subTest`, all 5 cases run independently and all failures are reported.
</details>

---

### Q14 🟡 · unittest · Migration to pytest

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)

**Problem:** Given a `unittest.TestCase` with `setUp`, `assertEqual`, and `assertRaises`, rewrite it as pytest functions using a fixture and plain `assert` / `pytest.raises`.

<details>
<summary>💡 Hint</summary>

Replace `setUp` with `@pytest.fixture`. Replace `self.assertEqual(a, b)` with `assert a == b`. Replace `with self.assertRaises(E):` with `with pytest.raises(E):`.
</details>

<details>
<summary>✅ Answer</summary>

```python
# Original unittest
import unittest
class TestCalc(unittest.TestCase):
    def setUp(self): self.calc = Calculator()
    def test_add(self): self.assertEqual(self.calc.add(2,3), 5)
    def test_div_zero(self):
        with self.assertRaises(ZeroDivisionError): self.calc.divide(1, 0)

# Pytest equivalent
import pytest
@pytest.fixture
def calc(): return Calculator()

def test_add(calc): assert calc.add(2, 3) == 5

def test_div_zero(calc):
    with pytest.raises(ZeroDivisionError):
        calc.divide(1, 0)
```

**Why:** pytest style is less ceremony — no class needed, no named assertion methods. pytest also runs existing `unittest.TestCase` subclasses unchanged if you prefer gradual migration.
</details>

---

## Mock Basics (Q15–Q19)

### Q15 🟡 · mock · Basic Mock and return_value

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)

**Problem:** Create a `Mock` for a `DatabaseClient` with a `find_user(user_id)` method. Set `return_value` to return a user dict. Call it and assert the result and that it was called with the right argument.

<details>
<summary>💡 Hint</summary>

`m = Mock()`. `m.find_user.return_value = {...}`. `m.find_user.assert_called_once_with(1)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import Mock

m = Mock()
m.find_user.return_value = {"id": 1, "name": "Alice", "email": "a@ex.com"}

result = m.find_user(1)

assert result["name"] == "Alice"
m.find_user.assert_called_once_with(1)
```

**Why:** `return_value` controls what the mock returns without running real code. The call is recorded and can be verified with `assert_called_once_with`.
</details>

---

### Q16 🟡 · mock · @patch Decorator

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)

**Problem:** Write a function `get_current_user()` that calls `os.environ.get("USER_ID")`. Write a test using `@patch` that makes it return "42" and verifies the function returns the correct value.

<details>
<summary>💡 Hint</summary>

`@patch("module.os.environ.get")` or use `patch.dict(os.environ, {...})`. Remember to patch WHERE the name is used.
</details>

<details>
<summary>✅ Answer</summary>

```python
import os
from unittest.mock import patch

def get_current_user():
    user_id = os.environ.get("USER_ID")
    if not user_id:
        return None
    return {"id": user_id}

def test_get_current_user():
    with patch.dict(os.environ, {"USER_ID": "42"}):
        result = get_current_user()
    assert result["id"] == "42"
```

**Why:** `patch.dict` is the cleanest way to mock environment variables — it restores the original env after the `with` block.
</details>

---

### Q17 🟡 · mock · return_value on Chained Calls

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)

**Problem:** Mock `requests.get(url)` where the result is `response.json()`. Show how to chain `return_value` to mock both the `get` call and the `.json()` call on the response.

<details>
<summary>💡 Hint</summary>

`mock_get.return_value.json.return_value = {...}`. The `.return_value` is itself a Mock, so you can chain further `.method.return_value` on it.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import patch, Mock

def fetch_user(user_id):
    import requests
    response = requests.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()
    return response.json()

@patch("requests.get")
def test_fetch_user(mock_get):
    # Chain return_values for the response object
    mock_get.return_value.json.return_value = {"id": 1, "name": "Alice"}
    mock_get.return_value.raise_for_status.return_value = None

    result = fetch_user(1)
    assert result["name"] == "Alice"
    mock_get.assert_called_once_with("https://api.example.com/users/1")
```

**Why:** `mock_get.return_value` is the Mock returned when `requests.get()` is called. You chain `.json.return_value` to set what `response.json()` returns.
</details>

---

### Q18 🟡 · mock · side_effect

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)

**Problem:** Write a test where a mock's `side_effect` is: (1) a list `[10, 20, 30]` returning successive values, (2) an exception, (3) a lambda function that doubles its input.

<details>
<summary>💡 Hint</summary>

`m.method.side_effect = [1, 2, 3]` for list. `m.method.side_effect = ValueError("err")` for exception. `m.method.side_effect = lambda x: x*2` for callable.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import Mock
import pytest

def test_side_effect_list():
    m = Mock()
    m.get_next.side_effect = [10, 20, 30]
    assert m.get_next() == 10
    assert m.get_next() == 20
    assert m.get_next() == 30

def test_side_effect_exception():
    m = Mock()
    m.connect.side_effect = ConnectionError("server down")
    with pytest.raises(ConnectionError, match="server down"):
        m.connect()

def test_side_effect_callable():
    m = Mock()
    m.double.side_effect = lambda x: x * 2
    assert m.double(5) == 10
    assert m.double(7) == 14
```

**Why:** `side_effect` overrides `return_value` — when set, the mock calls it (if callable), raises it (if an exception), or returns the next item (if a list).
</details>

---

### Q19 🟡 · mock · assert_called_once_with

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)

**Problem:** Write a mock test that verifies a `send_email(to, subject, body)` call was made exactly once with specific keyword arguments. Also show `assert_called_with`, `assert_any_call`, and `call_args_list`.

<details>
<summary>💡 Hint</summary>

`from unittest.mock import Mock, call`. Use `mock.method.call_args_list` to see the full history.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import Mock, call

def test_email_assertions():
    m = Mock()
    m.send("alice@ex.com", subject="Hello", body="Hi there")

    # Exact: called once with exactly these args
    m.send.assert_called_once_with("alice@ex.com", subject="Hello", body="Hi there")

    # Last call check (passes even if called multiple times):
    m.send.assert_called_with("alice@ex.com", subject="Hello", body="Hi there")

    m.send("bob@ex.com", subject="Bye", body="Goodbye")

    # Any call in history:
    m.send.assert_any_call("alice@ex.com", subject="Hello", body="Hi there")
    assert m.send.call_count == 2

    # Full history:
    assert m.send.call_args_list == [
        call("alice@ex.com", subject="Hello", body="Hi there"),
        call("bob@ex.com", subject="Bye", body="Goodbye"),
    ]
```

**Why:** Use `assert_called_once_with` when exactly one call is part of the contract. Use `assert_any_call` when the call order doesn't matter. Use `call_args_list` for full audit.
</details>

---

## Mock Advanced (Q20–Q24)

### Q20 🟡 · mock · patch.object

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)

**Problem:** Use `patch.object` to patch the `increment` method on a `Counter` instance. Verify the mock is called, then verify the real method works after the context exits.

<details>
<summary>💡 Hint</summary>

`with patch.object(instance, "method_name", return_value=99) as mock_method:`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import patch

class Counter:
    def __init__(self): self.value = 0
    def increment(self): self.value += 1; return self.value

def test_patch_object():
    c = Counter()
    with patch.object(c, "increment", return_value=99) as mock_inc:
        result = c.increment()
        assert result == 99           # mock returned 99, not real value
        mock_inc.assert_called_once()

    # Real method restored:
    result = c.increment()
    assert result == 1
```

**Why:** `patch.object` patches a specific instance or class, not a module-level name. The original is restored after the `with` block.
</details>

---

### Q21 🟡 · mock · spec for Type Safety

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)

**Problem:** Create a `Mock(spec=EmailSender)` where `EmailSender` has a `send(to, subject, body)` method. Show that valid methods work, typos raise `AttributeError`, and explain why spec is important.

<details>
<summary>💡 Hint</summary>

`Mock(spec=RealClass)` raises `AttributeError` for any attribute not on `RealClass`. Use `create_autospec` to also check signatures.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import Mock
import pytest

class EmailSender:
    def send(self, to: str, subject: str, body: str) -> bool: ...

def test_spec_mock():
    m = Mock(spec=EmailSender)
    m.send.return_value = True

    # Valid method — works
    result = m.send("a@b.com", "Hi", "Hello")
    assert result is True

    # Typo — raises AttributeError
    with pytest.raises(AttributeError):
        m.sned("a@b.com", "Hi", "Hello")   # typo
```

**Why:** Without `spec`, `m.sned(...)` silently returns a MagicMock — the typo is invisible. With `spec`, it raises immediately. This catches API drift when `EmailSender` is refactored.
</details>

---

### Q22 🟠 · mock · patch.dict for Config

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)

**Problem:** Write `get_config()` that reads from `os.environ`. Use `patch.dict(os.environ, {...})` in a test to override specific keys. Verify the original environment is restored after the test.

<details>
<summary>💡 Hint</summary>

`patch.dict(os.environ, {"KEY": "val"}, clear=False)` only overrides the listed keys. `clear=True` replaces the entire dict.
</details>

<details>
<summary>✅ Answer</summary>

```python
import os
from unittest.mock import patch

def get_config():
    return {
        "host": os.environ.get("DB_HOST", "localhost"),
        "debug": os.environ.get("DEBUG", "false") == "true",
    }

def test_config_with_env_override():
    original = os.environ.get("DB_HOST")

    with patch.dict(os.environ, {"DB_HOST": "testhost", "DEBUG": "true"}):
        config = get_config()
        assert config["host"] == "testhost"
        assert config["debug"] is True

    # Restored after context
    assert os.environ.get("DB_HOST") == original
```

**Why:** `patch.dict` is the safest pattern for env var testing — automatic restoration prevents cross-test contamination.
</details>

---

### Q23 🟠 · mock · AsyncMock

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)

**Problem:** Write `async def process_items(repo, items)` that calls `await repo.save(item)` for each item. Write an async test using `AsyncMock` that verifies `save` was awaited once per item.

<details>
<summary>💡 Hint</summary>

`AsyncMock` creates a mock that returns a coroutine when called. Use `await_count` or `assert_awaited_once_with` to verify awaits.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pytest
from unittest.mock import AsyncMock

async def process_items(repo, items):
    for item in items:
        await repo.save(item)

@pytest.mark.asyncio
async def test_process_items():
    mock_repo = AsyncMock()
    mock_repo.save.return_value = True

    await process_items(mock_repo, ["a", "b", "c"])

    assert mock_repo.save.await_count == 3
    mock_repo.save.assert_any_await("a")
    mock_repo.save.assert_any_await("c")
```

**Why:** `AsyncMock` wraps the return value in a coroutine so `await` works. Use `await_count` and `assert_any_await` (note: `assert_any_await` is the async equivalent of `assert_any_call`).
</details>

---

### Q24 🟠 · mock · MagicMock as Context Manager

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)

**Problem:** Write a function `open_and_read(path)` that uses `open(path)` as a context manager and reads the file. Mock `open` using `mock_open` and verify the function returns the expected content.

<details>
<summary>💡 Hint</summary>

`from unittest.mock import mock_open, patch`. `m = mock_open(read_data="content")`. `with patch("builtins.open", m):`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import patch, mock_open

def open_and_read(path):
    with open(path) as f:
        return f.read()

def test_open_and_read():
    m = mock_open(read_data="hello world")
    with patch("builtins.open", m):
        result = open_and_read("/any/path.txt")

    assert result == "hello world"
    m.assert_called_once_with("/any/path.txt")
```

**Why:** `mock_open` creates a `MagicMock` that supports the context manager protocol (`__enter__`, `__exit__`) and `read()`. It's the standard way to test file I/O without touching the real filesystem.
</details>

---

## Test Doubles (Q25–Q28)

### Q25 🟡 · doubles · Mock vs Stub vs Fake

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)

**Problem:** Implement and use all three test doubles for a `WeatherService` dependency: a Stub (returns fixed data), a Fake (simple real implementation), and a Mock (unittest.mock). Show when you'd choose each.

<details>
<summary>💡 Hint</summary>

Stub — canned return, no verification. Fake — real logic, simplified. Mock — records calls, verifies interactions.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import Mock

# Stub — always returns the same data, no assertions
class StubWeatherService:
    def get_temp(self, city): return 22.5   # always sunny

# Fake — real logic, simplified storage
class FakeWeatherService:
    def __init__(self, data): self._data = data
    def get_temp(self, city): return self._data.get(city, 20.0)

# Mock — verifies interactions
mock_weather = Mock()
mock_weather.get_temp.return_value = 35.0

# Usage:
# Stub — for tests where the temperature value doesn't matter
alert = AlertService(weather=StubWeatherService())

# Fake — for tests that need realistic data variance
alert = AlertService(weather=FakeWeatherService({"Madrid": 35, "Oslo": 5}))

# Mock — for tests that verify the service was called with correct arguments
alert = AlertService(weather=mock_weather)
alert.check_city("London")
mock_weather.get_temp.assert_called_once_with("London")
```

**Why:** Stub = simplicity, Fake = realistic logic, Mock = interaction verification. Over-using Mock leads to brittle tests that test implementation, not behavior.
</details>

---

### Q26 🟡 · doubles · When Not to Mock

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)

**Problem:** List three situations where you should NOT mock, and write a test for each that demonstrates using the real object instead.

<details>
<summary>💡 Hint</summary>

Don't mock: pure functions, your own domain logic, simple data structures. Use mocks only at external boundaries.
</details>

<details>
<summary>✅ Answer</summary>

```python
# 1. Pure functions — no side effects, no mocking needed
def calculate_tax(amount, rate):
    return amount * rate

def test_calculate_tax():
    assert calculate_tax(100, 0.1) == 10.0   # no mock needed

# 2. In-memory data structures — use the real thing
class InMemoryCartRepository:
    def __init__(self): self._carts = {}
    def save(self, cart_id, items): self._carts[cart_id] = items
    def find(self, cart_id): return self._carts.get(cart_id)

def test_cart_repository():
    repo = InMemoryCartRepository()    # real implementation, simplified
    repo.save("cart-1", ["apple", "bread"])
    assert repo.find("cart-1") == ["apple", "bread"]

# 3. Your own domain classes — use real objects
class Order:
    def __init__(self, items): self.items = items
    def total(self): return sum(i["price"] for i in self.items)

def test_order_total():
    order = Order([{"price": 10}, {"price": 20}])
    assert order.total() == 30   # no mock needed
```

**Why:** Mocking your own domain objects makes tests brittle and circular — you're testing mock behavior, not real behavior. Reserve mocks for external I/O that you can't control.
</details>

---

### Q27 🟡 · doubles · Spy Pattern

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)

**Problem:** Implement a `SpyNotifier` that wraps a real `Notifier`, calls it for real, and records the calls. Use it in a test that verifies both the real side effect and the call record.

<details>
<summary>💡 Hint</summary>

A spy wraps the real object, delegates to it, and records calls. Use `wraps=real_object` in `Mock` to create a spy automatically.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import Mock

class RealNotifier:
    def __init__(self): self.sent = []
    def notify(self, msg): self.sent.append(msg)

# Manual spy — wraps real implementation
class SpyNotifier:
    def __init__(self, real):
        self._real = real
        self.calls = []

    def notify(self, msg):
        self.calls.append(msg)
        self._real.notify(msg)   # delegate to real

def test_spy_notifier():
    real = RealNotifier()
    spy = SpyNotifier(real)

    spy.notify("alert-1")
    spy.notify("alert-2")

    assert len(spy.calls) == 2          # call record
    assert spy.calls[0] == "alert-1"
    assert len(real.sent) == 2          # real side effect


# pytest/mock: use wraps= for automatic spy
def test_mock_spy():
    real = RealNotifier()
    spy = Mock(wraps=real)   # spy that delegates to real

    spy.notify("hello")

    spy.notify.assert_called_once_with("hello")  # mock verification
    assert real.sent == ["hello"]                 # real side effect
```

**Why:** Spies are useful when you need to verify both that the code called a method AND that the real method worked. `wraps=` makes `unittest.mock` do this automatically.
</details>

---

### Q28 🟡 · doubles · AAA Pattern

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)

**Problem:** Write a test for `checkout(cart, payment_service)` that clearly demonstrates the Arrange-Act-Assert pattern with labeled comments. The test should cover the happy path with a mocked payment service.

<details>
<summary>💡 Hint</summary>

Three clear sections: Arrange (set up all objects and mocks), Act (one call), Assert (verify results and calls). Each section should be separated visually.
</details>

<details>
<summary>✅ Answer</summary>

```python
from unittest.mock import Mock

class ShoppingCart:
    def __init__(self, items): self.items = items
    def total(self): return sum(i["price"] for i in self.items)
    def checkout(self, payment_service):
        if not self.items: raise ValueError("Empty cart")
        return payment_service.charge(self.total())

def test_checkout_charges_correct_amount():
    # ARRANGE — set up objects and configure mocks
    cart = ShoppingCart([{"name": "Book", "price": 15.99},
                         {"name": "Pen",  "price": 1.99}])
    mock_payment = Mock()
    mock_payment.charge.return_value = {"status": "ok", "tx_id": "abc123"}

    # ACT — single action being tested
    result = cart.checkout(mock_payment)

    # ASSERT — verify outcome and interactions
    assert result["status"] == "ok"
    assert result["tx_id"] == "abc123"
    mock_payment.charge.assert_called_once_with(pytest.approx(17.98))
```

**Why:** The AAA pattern makes test intent immediately clear. One Act per test means one reason to fail. The structure makes it easy to see what changed when a test breaks.
</details>

---

## Testing Patterns (Q29–Q32)

### Q29 🟡 · patterns · TDD Red-Green-Refactor

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)

**Problem:** Apply TDD to build a `PasswordValidator` that rejects passwords shorter than 8 characters and passwords without an uppercase letter. Write: (1) the failing test (RED), (2) minimal code (GREEN), (3) refactored code (still GREEN).

<details>
<summary>💡 Hint</summary>

Write the test first — `PasswordValidator` doesn't exist yet. Make it fail. Write minimum code. Add the next requirement, repeat.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pytest

# RED: tests written first — PasswordValidator doesn't exist yet
def test_password_too_short():
    with pytest.raises(ValueError, match="8 characters"):
        validate_password("short")

def test_password_no_uppercase():
    with pytest.raises(ValueError, match="uppercase"):
        validate_password("alllower1")

def test_valid_password():
    assert validate_password("SecurePass1") is True

# GREEN: minimum implementation
def validate_password(pwd):
    if len(pwd) < 8:
        raise ValueError("Password must be at least 8 characters")
    if not any(c.isupper() for c in pwd):
        raise ValueError("Password must contain an uppercase letter")
    return True

# REFACTOR: clean up — tests still pass
RULES = [
    (lambda p: len(p) >= 8,        "Password must be at least 8 characters"),
    (lambda p: any(c.isupper() for c in p), "Password must contain an uppercase letter"),
]

def validate_password(pwd):
    for check, message in RULES:
        if not check(pwd):
            raise ValueError(message)
    return True
```

**Why:** TDD forces you to define the interface before writing code. The refactor step is safe because the tests cover the behavior — you can restructure the implementation freely.
</details>

---

### Q30 🟡 · patterns · Testing Edge Cases

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)

**Problem:** Write a comprehensive test suite for `calculate_discount(price, quantity)` that applies: 10% off for qty >= 10, 20% off for qty >= 50. Test the happy paths, boundaries (qty 9, 10, 49, 50), and invalid inputs.

<details>
<summary>💡 Hint</summary>

Boundary values (one below, at, one above a threshold) catch off-by-one errors. Test both thresholds and both edges of each.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pytest

def calculate_discount(price, quantity):
    if price < 0 or quantity < 1:
        raise ValueError("Invalid price or quantity")
    if quantity >= 50: return price * 0.80
    if quantity >= 10: return price * 0.90
    return price

@pytest.mark.parametrize("qty, expected_rate", [
    (1,  1.00),   # no discount
    (9,  1.00),   # just below 10% threshold
    (10, 0.90),   # exactly at 10% threshold
    (49, 0.90),   # just below 20% threshold
    (50, 0.80),   # exactly at 20% threshold
    (100, 0.80),  # well above
])
def test_discount_boundaries(qty, expected_rate):
    assert calculate_discount(100, qty) == pytest.approx(100 * expected_rate)

def test_invalid_price():
    with pytest.raises(ValueError):
        calculate_discount(-10, 5)

def test_invalid_quantity():
    with pytest.raises(ValueError):
        calculate_discount(100, 0)
```

**Why:** Boundary value testing catches off-by-one errors. Testing (threshold-1, threshold, threshold+1) gives confidence the condition is `>=` not `>`. Parametrize makes this clean.
</details>

---

### Q31 🟡 · patterns · Test Isolation

> 🛠️ **Solve locally:** [practice_local.py → Q31](./practice_local.py)

**Problem:** Show a test that FAILS due to shared mutable state between tests, then fix it using fixtures.

<details>
<summary>💡 Hint</summary>

Global lists or module-level objects mutated by tests cause ordering-dependent failures. Fixtures reset the state per test.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pytest

# BROKEN: shared mutable state — tests depend on each other
SHARED_CART = []   # module-level!

def test_add_item_broken():
    SHARED_CART.append("apple")
    assert len(SHARED_CART) == 1

def test_add_another_broken():
    SHARED_CART.append("bread")
    assert len(SHARED_CART) == 1   # FAILS if test_add_item ran first!

# FIXED: fresh state per test via fixture
@pytest.fixture
def cart():
    return []   # brand new list per test

def test_add_item(cart):
    cart.append("apple")
    assert len(cart) == 1

def test_add_another(cart):
    cart.append("bread")
    assert len(cart) == 1   # always 1 — fresh cart
```

**Why:** Tests must be independent — any order should give the same results. Use fixtures (not module-level globals) for state that tests need. The `function` scope (default) creates fresh state per test.
</details>

---

### Q32 🟠 · patterns · Property-Based Testing with Hypothesis

> 🛠️ **Solve locally:** [practice_local.py → Q32](./practice_local.py)

**Problem:** Use `hypothesis` to test invariants of `sorted()`: the output length equals input length, the output is ordered, and the output contains the same elements. Show what a regular unit test misses that Hypothesis finds.

<details>
<summary>💡 Hint</summary>

`from hypothesis import given, strategies as st`. `@given(st.lists(st.integers()))`. Hypothesis generates hundreds of inputs including edge cases (empty list, duplicates, huge numbers) automatically.
</details>

<details>
<summary>✅ Answer</summary>

```python
from hypothesis import given, strategies as st

# Hand-picked test: only tests what you thought of
def test_sort_manual():
    assert sorted([3, 1, 2]) == [1, 2, 3]

# Property-based: Hypothesis tries hundreds of inputs automatically
@given(st.lists(st.integers()))
def test_sort_length_preserved(lst):
    """Sorted list has same length as original."""
    assert len(sorted(lst)) == len(lst)

@given(st.lists(st.integers()))
def test_sort_is_ordered(lst):
    """Adjacent elements in sorted output are non-decreasing."""
    result = sorted(lst)
    for i in range(len(result) - 1):
        assert result[i] <= result[i + 1]

@given(st.lists(st.integers()))
def test_sort_same_elements(lst):
    """Sorting doesn't add or remove elements."""
    assert sorted(sorted(lst)) == sorted(lst)   # idempotent

# Hypothesis also tests: empty list, single element, all same values,
# very large integers, negative numbers — without you writing any of those
```

**Why:** Hypothesis generates edge cases you'd never think of: empty list, duplicates, `sys.maxsize`, `-0`. Use it for functions where you can state invariants that must hold for ALL inputs.
</details>

---

## Capstone (Q33–Q35)

### Q33 🟠 · capstone · Coverage Analysis

> 🛠️ **Solve locally:** [practice_local.py → Q33](./practice_local.py)

**Problem:** Write a `PaymentProcessor` with three code paths: success, declined, and error. Write a test suite that achieves 100% line coverage. Use `pytest --cov` to verify. Explain what coverage does NOT guarantee.

<details>
<summary>💡 Hint</summary>

Install: `pip install pytest-cov`. Run: `pytest --cov=mymodule --cov-report=term-missing`. One test per code path for 100% coverage.
</details>

<details>
<summary>✅ Answer</summary>

```python
class PaymentProcessor:
    def process(self, amount, card_token):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if card_token == "declined":
            return {"status": "declined"}
        return {"status": "approved", "tx_id": f"tx_{amount}"}

# Tests: one per code path
import pytest

def test_approved():
    p = PaymentProcessor()
    result = p.process(99.99, "tok_valid")
    assert result["status"] == "approved"

def test_declined():
    p = PaymentProcessor()
    result = p.process(50.0, "declined")
    assert result["status"] == "declined"

def test_invalid_amount():
    p = PaymentProcessor()
    with pytest.raises(ValueError):
        p.process(0, "tok_valid")

# pytest --cov=mymodule --cov-report=term-missing → 100%
# Coverage does NOT guarantee:
# - Correct logic (assert 42 would give 100% but test nothing)
# - Edge cases within a branch
# - Race conditions or concurrency bugs
```

**Why:** 100% line coverage means every line was executed. A test that calls `process(99, "tok")` and doesn't assert anything gives 100% coverage but proves nothing. Coverage is a floor, not a measure of quality.
</details>

---

### Q34 🟠 · capstone · Test Organization

> 🛠️ **Solve locally:** [practice_local.py → Q34](./practice_local.py)

**Problem:** Design the test file structure for a small FastAPI service with `UserService`, `OrderService`, and an HTTP client. Show: directory layout, `conftest.py` content, naming conventions for test files and functions.

<details>
<summary>💡 Hint</summary>

Mirror the source structure in `tests/`. Use `conftest.py` for shared fixtures. Name tests `test_<unit>_<scenario>_<expected>`.
</details>

<details>
<summary>✅ Answer</summary>

```
myservice/
├── src/
│   └── myservice/
│       ├── services/
│       │   ├── user_service.py
│       │   └── order_service.py
│       └── api/
│           └── endpoints.py
└── tests/
    ├── conftest.py           ← shared fixtures (db, client, app)
    ├── unit/
    │   ├── services/
    │   │   ├── test_user_service.py
    │   │   └── test_order_service.py
    ├── integration/
    │   └── test_api_endpoints.py
    └── e2e/
        └── test_checkout_flow.py
```

```python
# tests/conftest.py
import pytest
from myservice import create_app

@pytest.fixture(scope="session")
def app():
    return create_app(testing=True)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    from myservice.database import Database
    db = Database(":memory:")
    db.create_tables()
    yield db
    db.drop_tables()

# Naming convention:
# test_<method>_<scenario>_<expected_outcome>
def test_create_user_valid_data_returns_user_id(): ...
def test_create_user_duplicate_email_raises_conflict(): ...
def test_create_user_missing_name_raises_validation_error(): ...
```

**Why:** Mirror source structure in tests. Shared fixtures in `conftest.py`. Explicit test names that read like sentences — when a test fails, the name tells you exactly what broke.
</details>

---

### Q35 🟠 · capstone — End-to-End Test Suite

> 🛠️ **Solve locally:** [practice_local.py → Q35](./practice_local.py)

**Problem:** Write a complete test suite for an `OrderService` that: creates orders, fetches orders by id, and deletes orders. Use: a pytest fixture with `yield` for the service + in-memory DB, `parametrize` for multiple order types, `Mock(spec=...)` for the payment gateway, and `pytest.raises` for error cases.

<details>
<summary>💡 Hint</summary>

This is a synthesis question — combine fixtures, parametrize, mocks, and exception testing in one cohesive suite. Aim for ~8-10 tests total covering happy paths and error cases.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pytest
from unittest.mock import Mock

class OrderNotFoundError(Exception):
    pass

class PaymentGateway:
    def charge(self, amount: float) -> dict: ...

class OrderService:
    def __init__(self, gateway: PaymentGateway):
        self._gateway = gateway
        self._orders = {}
        self._next_id = 1

    def create_order(self, items, customer_email):
        total = sum(i["price"] * i["qty"] for i in items)
        result = self._gateway.charge(total)
        order = {
            "id": self._next_id,
            "items": items,
            "total": total,
            "customer": customer_email,
            "tx_id": result["tx_id"],
        }
        self._orders[self._next_id] = order
        self._next_id += 1
        return order

    def get_order(self, order_id):
        if order_id not in self._orders:
            raise OrderNotFoundError(f"Order {order_id} not found")
        return self._orders[order_id]

    def delete_order(self, order_id):
        if order_id not in self._orders:
            raise OrderNotFoundError(f"Order {order_id} not found")
        del self._orders[order_id]


@pytest.fixture
def gateway():
    m = Mock(spec=PaymentGateway)
    m.charge.return_value = {"tx_id": "tx_001", "status": "approved"}
    return m

@pytest.fixture
def service(gateway):
    return OrderService(gateway=gateway)


VALID_ORDERS = [
    ([{"price": 10.0, "qty": 1}],  "alice@ex.com", 10.0),
    ([{"price": 5.0,  "qty": 3}],  "bob@ex.com",   15.0),
    ([{"price": 99.99,"qty": 2}],  "carol@ex.com", 199.98),
]

@pytest.mark.parametrize("items, email, expected_total", VALID_ORDERS)
def test_create_order(service, gateway, items, email, expected_total):
    order = service.create_order(items, email)
    assert order["total"] == pytest.approx(expected_total)
    assert order["customer"] == email
    assert order["tx_id"] == "tx_001"
    gateway.charge.assert_called_once_with(pytest.approx(expected_total))

def test_get_order(service):
    created = service.create_order([{"price": 10, "qty": 1}], "a@ex.com")
    found = service.get_order(created["id"])
    assert found["id"] == created["id"]

def test_get_order_not_found(service):
    with pytest.raises(OrderNotFoundError, match="Order 999 not found"):
        service.get_order(999)

def test_delete_order(service):
    created = service.create_order([{"price": 10, "qty": 1}], "a@ex.com")
    service.delete_order(created["id"])
    with pytest.raises(OrderNotFoundError):
        service.get_order(created["id"])

def test_delete_nonexistent_order(service):
    with pytest.raises(OrderNotFoundError):
        service.delete_order(42)
```

**Why:** This covers all techniques: fixtures with dependencies, `Mock(spec=...)` for type-safe mocking, `parametrize` for data-driven cases, `pytest.raises` for error paths, and `pytest.approx` for float comparisons. Real-world test suites look exactly like this.
</details>

---

## Navigation

| | |
|---|---|
| Root theory | [theory.md](./theory.md) |
| Local practice | [practice_local.py](./practice_local.py) |
| pytest deep dive | [01_pytest/theory.md](./01_pytest/theory.md) |
| pytest practice | [01_pytest/practice.md](./01_pytest/practice.md) |
| unittest deep dive | [02_unittest/theory.md](./02_unittest/theory.md) |
| unittest practice | [02_unittest/practice.md](./02_unittest/practice.md) |
| mocking deep dive | [03_mocking/theory.md](./03_mocking/theory.md) |
| mocking practice | [03_mocking/practice.md](./03_mocking/practice.md) |

**[Back to README](../README.md)**
