# 🧪 Testing in Python — Deep Dive

> Complete reference for Python testing: unit tests, pytest, mocking, fixtures,
> parameterization, coverage, async testing, and production testing strategy.

---

## 📋 Contents

```
1.  Why testing? The safety net mental model
2.  Test types and the testing pyramid
3.  unittest — the stdlib framework
4.  pytest — the modern way
5.  Fixtures — setup, teardown, scope
6.  Parametrize — data-driven tests
7.  Mocking — unittest.mock in depth
8.  Patching — where and how to patch
9.  Test doubles — mock vs stub vs fake vs spy
10. Testing exceptions and edge cases
11. Testing classes and stateful objects
12. Async testing — pytest-asyncio
13. Coverage — measuring and interpreting
14. Test organization and naming
15. TDD — test-driven development workflow
16. Property-based testing — hypothesis
17. Integration and contract testing
18. CI/CD and test pipelines
19. Common pitfalls and antipatterns
```

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`pytest` basics (test discovery, `assert`, fixtures) · `unittest.mock.patch` / `MagicMock` · `pytest.mark.parametrize` · Test isolation (setup/teardown)

**Should Learn** — Important for real projects, comes up regularly:
`pytest.fixtures` scope (function/class/module/session) · `caplog` / `capsys` fixtures · `pytest.raises` · `monkeypatch` · Code coverage (`pytest-cov`)

**Good to Know** — Useful in specific situations:
`pytest-mock` · Snapshot testing · `tox` for multi-environment · Contract testing

**Reference** — Know it exists, look up when needed:
`pytest-benchmark` · `pytest-subprocess` · `doctest` integration · `nox`

---

## 1. Why Testing? The Safety Net Mental Model

Imagine a high-wire acrobat. Without a safety net, every step is terrifying.
With one: the act is still skillful, but the cost of a slip is recovery —
not catastrophe.

Tests are your safety net. Without them:

```
Change line 47 in payments.py
→ Bug in user_profile.py
→ Found in production at 2am
→ $50,000 in lost transactions
→ Your fault. No test caught it.
```

With a proper test suite:

```
Change line 47 in payments.py
→ Run test suite: 3 tests fail immediately
→ Fix in 10 minutes before merge
→ Deploy with confidence
```

**What tests give you:**

| Benefit | What it means |
|---------|--------------|
| Regression safety | Old code stays working after changes |
| Refactor confidence | Restructure code without fear |
| Documentation | Tests show how code is meant to be used |
| Design pressure | Hard-to-test code = badly designed code |
| Deployment speed | CI gates prevent bad code reaching prod |

---

## 2. Test Types and the Testing Pyramid

```
              /\
             /  \
            / E2E\        ← Few, slow, expensive
           /──────\
          /        \
         /Integration\    ← Some, medium speed
        /────────────\
       /              \
      /   Unit Tests   \  ← Many, fast, cheap
     /──────────────────\

     FAST ←────────────→ SLOW
     CHEAP ←───────────→ EXPENSIVE
     ISOLATED ←────────→ REALISTIC
```

| Type | Scope | Speed | What it tests |
|------|-------|-------|--------------|
| **Unit** | Single function/class | Milliseconds | Logic in isolation |
| **Integration** | Multiple components | Seconds | Components wired together |
| **E2E** | Entire system | Minutes | Real user flows |
| **Contract** | Service boundaries | Seconds | API contracts |
| **Property** | Edge cases via generation | Seconds | Invariants at scale |

**Practical split for a production service:**
```
Unit:        ~70% of tests  → fast feedback during development
Integration: ~20% of tests  → catch wiring bugs
E2E:         ~10% of tests  → smoke test critical user journeys
```

---

## 3. `unittest` — The Standard Library Framework

```python
import unittest

def add(a, b): return a + b
def divide(a, b):
    if b == 0: raise ZeroDivisionError("cannot divide by zero")
    return a / b

class TestMath(unittest.TestCase):

    # --- Setup/teardown ---
    @classmethod
    def setUpClass(cls):
        """Runs ONCE before any tests in this class."""
        cls.shared_resource = expensive_setup()

    @classmethod
    def tearDownClass(cls):
        """Runs ONCE after all tests in this class."""
        cls.shared_resource.cleanup()

    def setUp(self):
        """Runs before EACH test method."""
        self.result = None

    def tearDown(self):
        """Runs after EACH test method."""
        self.result = None

    # --- Test methods (must start with test_) ---
    def test_add_positive(self):
        self.assertEqual(add(2, 3), 5)

    def test_add_negative(self):
        self.assertEqual(add(-1, -1), -2)

    def test_add_zero(self):
        self.assertEqual(add(5, 0), 5)

    def test_divide_normal(self):
        self.assertAlmostEqual(divide(10, 3), 3.333, places=3)

    def test_divide_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            divide(10, 0)

    def test_divide_by_zero_message(self):
        with self.assertRaises(ZeroDivisionError) as ctx:
            divide(10, 0)
        self.assertIn("cannot divide by zero", str(ctx.exception))

# --- All assertion methods ---
# self.assertEqual(a, b)          a == b
# self.assertNotEqual(a, b)       a != b
# self.assertTrue(x)              bool(x) is True
# self.assertFalse(x)             bool(x) is False
# self.assertIsNone(x)            x is None
# self.assertIsNotNone(x)         x is not None
# self.assertIn(a, b)             a in b
# self.assertNotIn(a, b)          a not in b
# self.assertIs(a, b)             a is b
# self.assertIsNot(a, b)          a is not b
# self.assertAlmostEqual(a, b)    round(a-b, 7) == 0
# self.assertGreater(a, b)        a > b
# self.assertLess(a, b)           a < b
# self.assertRaises(Exc)          [context manager](../12_context_managers/theory.md)
# self.assertLogs(logger, level)  context manager for log output
# self.assertRegex(text, regexp)  re.search(regexp, text)

if __name__ == "__main__":
    unittest.main()
```

### Running unittest

```bash
python -m unittest test_module             # run one module
python -m unittest test_module.TestClass  # run one class
python -m unittest discover               # discover all test_*.py files
python -m unittest -v                     # verbose output
```

---

## 4. pytest — The Modern Way

pytest is the industry standard. It's more expressive, has better output,
and integrates with hundreds of plugins.

```python
# test_math.py  (no class needed!)
def add(a, b): return a + b
def divide(a, b):
    if b == 0: raise ZeroDivisionError("cannot divide by zero")
    return a / b

# Plain assert — pytest rewrites assertions for rich failure messages
def test_add():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, -1) == -2

def test_divide_by_zero():
    import pytest
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_divide_by_zero_message():
    import pytest
    with pytest.raises(ZeroDivisionError, match="cannot divide by zero"):
        divide(10, 0)

def test_approximate():
    import pytest
    assert divide(1, 3) == pytest.approx(0.333, abs=1e-3)
```

### Running pytest

```bash
pytest                          # discover and run all tests
pytest test_math.py             # run specific file
pytest test_math.py::test_add   # run specific test
pytest -v                       # verbose
pytest -x                       # stop on first failure
pytest -k "add"                 # run tests matching keyword
pytest -k "add and not negative"
pytest --tb=short               # shorter traceback
pytest --tb=no                  # no traceback (just pass/fail)
pytest -s                       # show print/stdout
pytest -n 4                     # parallel (requires pytest-xdist)
pytest --lf                     # rerun only last-failed tests
pytest --ff                     # run failed tests first
```

### pytest assertion introspection

One of pytest's killer features — when an assertion fails, it shows exactly
what went wrong without any special assertion methods:

```python
def test_list():
    expected = [1, 2, 3]
    actual   = [1, 2, 4]
    assert actual == expected
# Output:
#   AssertionError: assert [1, 2, 4] == [1, 2, 3]
#     At index 2 diff: 4 != 3

def test_dict():
    d = {"a": 1, "b": 2}
    assert d == {"a": 1, "b": 3}
# Output:
#   AssertionError: assert {'a': 1, 'b': 2} == {'a': 1, 'b': 3}
#   Left contains:  {'b': 2}
#   Right contains: {'b': 3}
```

---

## 5. Fixtures — The Heart of pytest

Fixtures provide reusable setup/teardown. They're injected by name into test
functions as parameters.

```python
import pytest
import sqlite3
import tempfile
import os

# --- Basic fixture ---
@pytest.fixture
def sample_user():
    return {"id": 1, "name": "Alice", "email": "alice@example.com"}

def test_user_name(sample_user):
    assert sample_user["name"] == "Alice"

def test_user_email(sample_user):
    assert "@" in sample_user["email"]

# --- Fixture with teardown (yield) ---
@pytest.fixture
def temp_file():
    """Creates a temp file, yields its path, then removes it."""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path       # test runs HERE
    os.remove(path)  # cleanup AFTER test

def test_write_file(temp_file):
    with open(temp_file, "w") as f:
        f.write("hello")
    with open(temp_file) as f:
        assert f.read() == "hello"

# --- Fixture scope ---
@pytest.fixture(scope="function")  # default: run once per test
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    yield conn
    conn.close()

@pytest.fixture(scope="module")    # run once per module file
def shared_client():
    client = create_heavy_client()
    yield client
    client.teardown()

@pytest.fixture(scope="session")   # run once for entire test session
def app_server():
    server = start_test_server()
    yield server
    server.stop()

# scope options: "function" | "class" | "module" | "package" | "session"

# --- Fixture dependencies ---
@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE items (id INT, name TEXT)")
    yield conn
    conn.close()

@pytest.fixture
def populated_db(db):   # depends on db fixture
    db.execute("INSERT INTO items VALUES (1, 'Widget')")
    db.execute("INSERT INTO items VALUES (2, 'Gadget')")
    db.commit()
    return db

def test_item_count(populated_db):
    count = populated_db.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    assert count == 2

# --- autouse fixtures (run for every test automatically) ---
@pytest.fixture(autouse=True)
def reset_global_state():
    """Runs before every test in the module, no need to request it."""
    yield
    some_module.reset()   # cleanup after each test

# --- Fixture parametrize ---
@pytest.fixture(params=["sqlite", "postgres"])
def database(request):
    if request.param == "sqlite":
        return SQLiteDatabase()
    elif request.param == "postgres":
        return PostgresDatabase(test_url)
```

### conftest.py — Shared Fixtures

```
project/
├── conftest.py        ← fixtures available to ALL tests
├── tests/
│   ├── conftest.py    ← fixtures for tests/ subtree
│   ├── test_users.py
│   └── api/
│       ├── conftest.py  ← fixtures for api/ subtree only
│       └── test_endpoints.py
```

```python
# conftest.py
import pytest

@pytest.fixture(scope="session")
def app():
    """App available to all tests without importing."""
    from myapp import create_app
    app = create_app(testing=True)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()
```

---

## 6. Parametrize — Data-Driven Tests

```python
import pytest

def is_palindrome(s):
    s = s.lower().replace(" ", "")
    return s == s[::-1]

# Single parameter:
@pytest.mark.parametrize("word,expected", [
    ("racecar",   True),
    ("hello",     False),
    ("A man a plan a canal Panama", True),
    ("",          True),
    ("a",         True),
])
def test_palindrome(word, expected):
    assert is_palindrome(word) == expected

# Multiple axes — creates all combinations:
@pytest.mark.parametrize("a", [1, 2, 3])
@pytest.mark.parametrize("b", [10, 20])
def test_multiply(a, b):
    assert a * b == b * a   # commutativity

# Mark individual cases:
@pytest.mark.parametrize("x,y,expected", [
    (1, 1, 2),
    (0, 0, 0),
    pytest.param(-1, -1, -2, id="both-negative"),
    pytest.param(1e308, 1e308, float("inf"), marks=pytest.mark.xfail),
])
def test_add_cases(x, y, expected):
    assert x + y == expected
```

---

## 7. Mocking — `unittest.mock` in Depth

### The Problem Mocking Solves

```
Your function calls:
  - External API    → slow, costs money, can be down
  - Database        → requires setup, modifies real data
  - File system     → leaves debris, platform-dependent
  - Time/random     → non-deterministic, makes tests flaky
  - Email/SMS       → sends real messages!

Mocking replaces these with controllable fakes.
```

### Mock Object

```python
from unittest.mock import Mock, MagicMock, patch, call

# Basic Mock:
m = Mock()
m.method()           # returns Mock() — doesn't raise
m.method.return_value = 42
print(m.method())    # 42

# Configure at creation:
m = Mock(return_value=42)
print(m())           # 42

m = Mock(side_effect=ValueError("bad input"))
m()   # raises ValueError

# side_effect as list (returns next item each call):
m = Mock(side_effect=[1, 2, 3])
print(m(), m(), m())   # 1 2 3
# m()  # StopIteration

# side_effect as function:
m = Mock(side_effect=lambda x: x * 2)
print(m(5))   # 10

# MagicMock — like Mock but also implements magic methods:
m = MagicMock()
len(m)     # 0 (not AttributeError)
m[0]       # MagicMock()
str(m)     # some string representation

# Verify calls:
m = Mock()
m.connect("localhost", 5432)
m.query("SELECT 1")

m.connect.assert_called_once()
m.connect.assert_called_once_with("localhost", 5432)
m.query.assert_called_with("SELECT 1")
m.query.assert_called()
m.connect.call_count         # 1
m.connect.call_args          # call("localhost", 5432)
m.connect.call_args_list     # [call("localhost", 5432)]

# Assert NOT called:
m.close.assert_not_called()
```

### `patch` — The Standard Tool

```python
from unittest.mock import patch
import requests

def get_user(user_id: int) -> dict:
    """Fetches user from external API."""
    response = requests.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()
    return response.json()

# patch as decorator:
@patch("requests.get")
def test_get_user(mock_get):
    mock_get.return_value.json.return_value = {"id": 1, "name": "Alice"}
    mock_get.return_value.raise_for_status = Mock()

    user = get_user(1)
    assert user["name"] == "Alice"
    mock_get.assert_called_once_with("https://api.example.com/users/1")

# patch as context manager:
def test_get_user_error():
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()
        with pytest.raises(requests.exceptions.ConnectionError):
            get_user(1)

# CRITICAL: patch WHERE IT'S USED, not where it's defined!
# If your_module.py imports: from requests import get
# Then patch: "your_module.get"  NOT "requests.get"

# patch object attribute:
with patch.object(MyClass, "expensive_method", return_value=99) as mock:
    result = MyClass().use_expensive_method()

# patch dictionary:
with patch.dict(os.environ, {"API_KEY": "test-key"}):
    result = function_that_reads_env()

# patch multiple things:
@patch("module.ClassA")
@patch("module.ClassB")
def test_multi(mock_b, mock_a):   # decorators applied bottom-up, args reversed!
    ...
```

### pytest's `monkeypatch`

```python
def test_with_monkeypatch(monkeypatch):
    # Patch attribute:
    monkeypatch.setattr("requests.get", lambda url: MockResponse())

    # Patch environment variable:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")

    # Delete attribute:
    monkeypatch.delattr("module.SomeClass.method")

    # Patch dict:
    monkeypatch.setitem(config_dict, "debug", True)

    # All patches are automatically undone after the test!
    # (No cleanup needed — unlike manual patch.stop())
```

---

## 8. Test Doubles — Mock vs Stub vs Fake vs Spy

These terms come from Gerard Meszaros's *xUnit Test Patterns*:

```
Dummy    — passed but never used (just fills a parameter slot)
Stub     — returns canned answers; doesn't verify interactions
Fake     — real implementation, but simplified (in-memory DB)
Mock     — pre-programmed with expectations; verifies calls
Spy      — real implementation that records how it was called
```

```python
# Stub — returns pre-set data, no verification:
class StubEmailService:
    def send(self, to, subject, body) -> bool:
        return True   # always succeeds, no actual send

# Fake — real implementation, simplified:
class FakeDatabase:
    def __init__(self):
        self._store = {}

    def save(self, key, value):
        self._store[key] = value

    def get(self, key):
        if key not in self._store:
            raise KeyError(f"Not found: {key}")
        return self._store[key]

# Spy — wraps real implementation, records calls:
class SpyEmailService:
    def __init__(self, real_service):
        self._real = real_service
        self.sent_messages = []

    def send(self, to, subject, body):
        self.sent_messages.append({"to": to, "subject": subject})
        return self._real.send(to, subject, body)

# In tests:
def test_registration_sends_welcome_email():
    spy = SpyEmailService(real_service=NoopEmail())
    service = UserService(email=spy)
    service.register("alice@example.com")

    assert len(spy.sent_messages) == 1
    assert spy.sent_messages[0]["to"] == "alice@example.com"
    assert "Welcome" in spy.sent_messages[0]["subject"]
```

---

## 9. Testing Exceptions and Edge Cases

```python
import pytest

# Test exception type:
def test_key_error():
    d = {}
    with pytest.raises(KeyError):
        d["missing"]

# Test exception message:
def test_value_error_message():
    with pytest.raises(ValueError, match=r"must be positive"):
        validate_age(-1)

# Test exact exception:
def test_custom_exception():
    exc = pytest.raises(InsufficientFundsError, withdraw, amount=1000, balance=100)
    assert exc.value.shortfall == 900

# Edge cases to always test:
def test_empty_input():
    assert process([]) == []

def test_single_item():
    assert process([42]) == [42]

def test_none_input():
    with pytest.raises(TypeError):
        process(None)

def test_boundary_values():
    assert is_valid_age(0)    == True   # boundary
    assert is_valid_age(-1)   == False  # just below
    assert is_valid_age(150)  == True   # high boundary
    assert is_valid_age(151)  == False  # just above
    assert is_valid_age(75)   == True   # middle

def test_type_errors():
    with pytest.raises(TypeError):
        add("1", 2)  # string + int

def test_overflow():
    result = add(float("inf"), 1)
    assert result == float("inf")
```

---

## 10. Testing Classes and Stateful Objects

```python
import pytest
from unittest.mock import Mock

class ShoppingCart:
    def __init__(self):
        self.items  = []
        self.total  = 0.0

    def add_item(self, name, price, qty=1):
        self.items.append({"name": name, "price": price, "qty": qty})
        self.total += price * qty

    def remove_item(self, name):
        before = len(self.items)
        self.items = [i for i in self.items if i["name"] != name]
        removed = before - len(self.items)
        self.total -= sum(i["price"] * i["qty"] for i in self.items
                          if i["name"] == name)
        if removed == 0:
            raise KeyError(f"Item not found: {name!r}")

    def checkout(self, payment_service):
        if not self.items:
            raise ValueError("Cart is empty")
        return payment_service.charge(self.total)

@pytest.fixture
def cart():
    return ShoppingCart()

@pytest.fixture
def populated_cart(cart):
    cart.add_item("Apple", 0.99, qty=3)
    cart.add_item("Banana", 0.49, qty=2)
    return cart

class TestShoppingCart:
    def test_empty_cart_total(self, cart):
        assert cart.total == 0.0

    def test_add_single_item(self, cart):
        cart.add_item("Apple", 1.99)
        assert len(cart.items) == 1
        assert cart.total == pytest.approx(1.99)

    def test_add_multiple_items(self, populated_cart):
        assert len(populated_cart.items) == 2
        assert populated_cart.total == pytest.approx(0.99*3 + 0.49*2)

    def test_remove_item(self, populated_cart):
        populated_cart.remove_item("Apple")
        assert len(populated_cart.items) == 1
        assert all(i["name"] != "Apple" for i in populated_cart.items)

    def test_remove_nonexistent_item(self, populated_cart):
        with pytest.raises(KeyError, match="not found"):
            populated_cart.remove_item("Mango")

    def test_checkout_calls_payment(self, populated_cart):
        mock_payment = Mock()
        mock_payment.charge.return_value = {"status": "ok", "transaction_id": "tx123"}

        result = populated_cart.checkout(mock_payment)

        mock_payment.charge.assert_called_once_with(populated_cart.total)
        assert result["status"] == "ok"

    def test_checkout_empty_cart(self, cart):
        mock_payment = Mock()
        with pytest.raises(ValueError, match="empty"):
            cart.checkout(mock_payment)
        mock_payment.charge.assert_not_called()
```

---

## 11. Async Testing — pytest-asyncio

```bash
pip install pytest-asyncio
```

```python
import pytest
import asyncio
from unittest.mock import AsyncMock, patch

# Mark test as async:
@pytest.mark.asyncio
async def test_async_function():
    result = await fetch_data(url="https://example.com/api")
    assert result["status"] == "ok"

# Async fixture:
@pytest.fixture
async def async_client():
    client = AsyncHttpClient()
    await client.connect()
    yield client
    await client.close()

# Mock async functions with AsyncMock:
@pytest.mark.asyncio
async def test_async_with_mock():
    with patch("module.fetch", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {"data": [1, 2, 3]}

        result = await process_remote_data()

        assert result == [1, 2, 3]
        mock_fetch.assert_awaited_once()

# pytest.ini or pyproject.toml configuration:
# [pytest]
# asyncio_mode = auto    ← auto-marks all async tests (pytest-asyncio 0.19+)
```

---

## 12. Code Coverage

```bash
pip install pytest-cov

# Run with coverage:
pytest --cov=mypackage --cov-report=term-missing

# Generate HTML report:
pytest --cov=mypackage --cov-report=html

# Set coverage threshold (fail if below 80%):
pytest --cov=mypackage --cov-fail-under=80

# .coveragerc or pyproject.toml:
# [coverage:run]
# source = mypackage
# omit = mypackage/migrations/*
#
# [coverage:report]
# show_missing = True
# fail_under = 80
```

**Coverage types:**

```
Line coverage:    was this line executed?      (most common)
Branch coverage:  was each if/else branch hit?  (more thorough)
Condition:        was each boolean sub-expr True AND False?
```

**Interpreting coverage numbers:**

```
90% coverage is often a goal — but it's a proxy, not a guarantee.
100% coverage can still miss:
  - Wrong algorithm (passes tests but wrong logic)
  - Missing edge cases (test doesn't cover all paths through logic)
  - Race conditions (concurrent code hard to cover)

Low coverage (<50%) is a clear warning sign.
High coverage (>80%) is table stakes for production code.
Coverage alone is not a quality metric — what matters is what you assert.
```

---

## 13. Test Organization and Naming

### File structure

```
project/
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── services/
│       │   ├── user_service.py
│       │   └── payment_service.py
│       └── models/
│           └── user.py
├── tests/
│   ├── conftest.py         ← shared fixtures
│   ├── unit/
│   │   ├── services/
│   │   │   ├── test_user_service.py
│   │   │   └── test_payment_service.py
│   │   └── models/
│   │       └── test_user.py
│   ├── integration/
│   │   └── test_user_registration_flow.py
│   └── e2e/
│       └── test_checkout_journey.py
└── pytest.ini
```

### Naming conventions

```python
# File:     test_<module_name>.py
# Class:    Test<ClassName>
# Method:   test_<method>_<scenario>_<expected>

def test_calculate_discount_zero_items_returns_zero():      # explicit
def test_calculate_discount_above_threshold_applies_20():   # explicit
def test_user_register_duplicate_email_raises_conflict():   # explicit
```

### Marks

```python
import pytest

@pytest.mark.slow              # mark as slow (skip in fast runs: -m "not slow")
@pytest.mark.integration       # integration test
@pytest.mark.skip(reason="needs DB")
@pytest.mark.skipif(sys.platform == "win32", reason="unix only")
@pytest.mark.xfail(reason="known bug #123", strict=True)  # expect failure

# pytest.ini:
# [pytest]
# markers =
#     slow: marks tests as slow
#     integration: marks tests as integration tests
```

---

## 14. TDD — Test-Driven Development

The Red-Green-Refactor cycle:

```
RED:    Write a failing test for the feature you're about to build
GREEN:  Write the MINIMUM code to make it pass
REFACTOR: Clean up the code while keeping tests green
```

```python
# Step 1: RED — write test first (FizzBuzz example)
def test_fizzbuzz_multiples_of_3():
    assert fizzbuzz(3)  == "Fizz"
    assert fizzbuzz(6)  == "Fizz"
    assert fizzbuzz(9)  == "Fizz"

def test_fizzbuzz_multiples_of_5():
    assert fizzbuzz(5)  == "Buzz"
    assert fizzbuzz(10) == "Buzz"

def test_fizzbuzz_multiples_of_15():
    assert fizzbuzz(15) == "FizzBuzz"
    assert fizzbuzz(30) == "FizzBuzz"

def test_fizzbuzz_other_numbers():
    assert fizzbuzz(1)  == "1"
    assert fizzbuzz(7)  == "7"

# Step 2: GREEN — minimal implementation
def fizzbuzz(n):
    if n % 15 == 0: return "FizzBuzz"
    if n % 3  == 0: return "Fizz"
    if n % 5  == 0: return "Buzz"
    return str(n)

# Step 3: REFACTOR — all tests still pass after cleanup
```

**TDD benefits:**
- Forces you to think about the interface before implementation
- Each feature is testable by design (loosely coupled)
- Provides a regression suite automatically
- Small, incremental changes — easier to debug

---

## 15. Property-Based Testing — Hypothesis

Standard tests use hand-picked examples. Hypothesis generates thousands of
inputs automatically, finding edge cases you'd never think of.

```bash
pip install hypothesis
```

```python
from hypothesis import given, strategies as st, settings, assume

def sort_list(lst):
    return sorted(lst)

# Instead of:
def test_sort_specific():
    assert sort_list([3, 1, 2]) == [1, 2, 3]

# Use property-based:
@given(st.lists(st.integers()))
def test_sort_length_preserved(lst):
    """Sorted list has same length as original."""
    assert len(sort_list(lst)) == len(lst)

@given(st.lists(st.integers()))
def test_sort_output_ordered(lst):
    """Every adjacent pair in sorted output is ordered."""
    result = sort_list(lst)
    for i in range(len(result) - 1):
        assert result[i] <= result[i + 1]

@given(st.lists(st.integers()))
def test_sort_contains_same_elements(lst):
    """Sorted list contains exact same elements."""
    assert sorted(sort_list(lst)) == sorted(lst)   # order-independent compare

# Strategies:
st.integers(min_value=0, max_value=100)
st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll")))
st.lists(st.integers(), min_size=1, max_size=50)
st.floats(allow_nan=False, allow_infinity=False)
st.builds(User, name=st.text(min_size=1), age=st.integers(18, 99))
st.one_of(st.none(), st.integers())

# assume() — filter invalid inputs:
@given(st.integers(), st.integers())
def test_divide(a, b):
    assume(b != 0)   # skip when b is zero
    result = a / b
    assert result * b == pytest.approx(a)
```

---

## 16. Common Pitfalls and Anti-Patterns

```python
# ❌ ANTI-PATTERN 1: Testing implementation, not behavior
def test_user_service_calls_repository():
    repo = Mock()
    service = UserService(repo)
    service.get_user(1)
    repo.find_by_id.assert_called_once_with(1)   # ← tests internal impl

# ✅ BETTER: test the observable behavior
def test_get_user_returns_correct_data():
    repo = FakeUserRepository({"1": User(id=1, name="Alice")})
    service = UserService(repo)
    user = service.get_user(1)
    assert user.name == "Alice"   # ← tests what we care about

# ❌ ANTI-PATTERN 2: Tests depend on each other
test_order_global_db = []

def test_create_order():
    test_order_global_db.append(Order(id=1))
    assert len(test_order_global_db) == 1

def test_list_orders():
    assert len(test_order_global_db) == 1   # depends on previous test!

# ✅ BETTER: each test is self-contained via fixtures

# ❌ ANTI-PATTERN 3: Over-mocking (mock everything)
def test_process_data():
    mock_parser   = Mock()
    mock_validator= Mock()
    mock_db       = Mock()
    mock_cache    = Mock()
    mock_logger   = Mock()
    # ... all logic mocked → test proves nothing about actual behavior!

# ✅ BETTER: use fakes for infrastructure, only mock at system boundaries

# ❌ ANTI-PATTERN 4: No negative/edge case testing
def test_login():
    assert login("alice", "correct") == True  # only happy path!

# ✅ BETTER:
def test_login_wrong_password():
    assert login("alice", "wrong") == False
def test_login_unknown_user():
    with pytest.raises(UserNotFoundError):
        login("nobody", "password")
def test_login_empty_password():
    with pytest.raises(ValueError):
        login("alice", "")

# ❌ ANTI-PATTERN 5: Using time.sleep in tests
def test_scheduled_job():
    schedule_job(run_after=1.0)
    time.sleep(1.1)   # flaky! slow!
    assert job_ran()

# ✅ BETTER: use freezegun or mock time
from freezegun import freeze_time
def test_scheduled_job():
    with freeze_time("2024-01-01 10:00:00"):
        schedule_job(run_after=1.0)
    with freeze_time("2024-01-01 10:00:02"):
        assert job_ran()
```

---

## 17. CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        pip install -e ".[dev]"

    - name: Run tests with coverage
      run: |
        pytest --cov=myapp --cov-report=xml --cov-fail-under=80 -x

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

```ini
# pytest.ini
[pytest]
testpaths = tests
addopts = -v --tb=short
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks integration tests
    e2e: marks end-to-end tests
```

---

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🧪 pytest Guide | [pytest_guide.md](./pytest_guide.md) |
| ⬅️ Previous | [16 — Design Patterns](../16_design_patterns/theory.md) |
| ➡️ Next | [18 — Performance Optimization](../18_performance_optimization/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Design Patterns — Interview Q&A](../16_design_patterns/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
