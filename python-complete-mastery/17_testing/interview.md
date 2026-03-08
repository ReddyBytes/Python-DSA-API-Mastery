# 🎯 Testing in Python — Interview Questions

> 13 questions + 5 traps + rapid-fire. Junior → Senior coverage with code.

---

## 📋 Contents

```
Junior   (1–4):  test types, pytest basics, assertions, what to test
Mid-Level(5–9):  fixtures, parametrize, mocking, patching, coverage
Senior  (10–13): testable design, TDD, flaky tests, property-based, CI strategy
Traps    (5):    subtle mistakes every engineer gets asked
```

---

## Junior Level

---

### Q1. What is the difference between unit, integration, and end-to-end tests?

**Answer:**

```
Unit test:         Tests ONE function or class in complete isolation.
                   All dependencies are mocked or stubbed.
                   Runs in milliseconds.

Integration test:  Tests MULTIPLE real components wired together.
                   May use a real DB, real cache, but still controlled.
                   Catches "the components don't talk to each other correctly."

End-to-end test:   Tests the ENTIRE system from a user's perspective.
                   Real browser, real network, real DB.
                   Slowest, most brittle, highest confidence.
```

**The testing pyramid:**

```
         /\
        /E2E\          ← Few (10%) — slow, expensive, brittle
       /──────\
      /Integr.  \      ← Some (20%) — medium speed
     /────────────\
    /  Unit Tests  \   ← Many (70%) — fast, cheap, isolated
   /────────────────\
```

The pyramid shape reflects the trade-off: the more a test resembles real usage,
the slower and more brittle it is. Unit tests give fast feedback; E2E tests give
confidence in the real system.

---

### Q2. What is pytest and why do most Python teams use it over `unittest`?

**Answer:**

pytest is the de facto Python testing framework. Key advantages over `unittest`:

```python
# unittest:
class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
        self.assertIsNotNone(result)
        self.assertIn(5, [1, 2, 3, 4, 5])

# pytest (same tests, cleaner):
def test_add():
    assert add(2, 3) == 5
    assert result is not None
    assert 5 in [1, 2, 3, 4, 5]
```

**Why pytest wins:**
- Plain `assert` — no need to memorize `assertEqual` vs `assertIsNotNone` etc.
- Rich failure messages — shows exactly what was different on failure
- Fixtures — more powerful than setUp/tearDown
- Parametrize — built-in data-driven tests
- Plugin ecosystem — coverage, xdist (parallel), asyncio, faker, etc.
- Better test discovery and filtering (`-k`, `--lf`, `-x`)

---

### Q3. What does a good unit test look like? What should it test?

**Answer:**

A good unit test follows the **AAA pattern** — Arrange, Act, Assert:

```python
def test_calculate_discount_above_threshold():
    # Arrange: set up the system under test and its inputs
    cart = ShoppingCart()
    cart.add_item("Widget", price=10.0, qty=15)   # $150 total > $100 threshold

    # Act: call the thing you're testing (one action per test)
    discount = cart.calculate_discount()

    # Assert: verify exactly one behavior
    assert discount == pytest.approx(15.0)   # 10% of $150
```

**Properties of a good unit test:**
- **Fast** — runs in < 10ms (no I/O, no network, no sleep)
- **Isolated** — doesn't depend on other tests, global state, or external services
- **Deterministic** — same result every run
- **Tests behavior, not implementation** — if you refactor internals, tests shouldn't break
- **One assertion per test** (or closely related assertions) — one failure = one clear diagnosis
- **Readable name** — `test_calculate_discount_above_threshold` tells you everything

---

### Q4. How do you test that code raises an exception?

**Answer:**

```python
import pytest

def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("cannot divide by zero")
    return a / b

# Basic: just check exception type:
def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

# Check the message too:
def test_divide_by_zero_message():
    with pytest.raises(ZeroDivisionError, match="cannot divide by zero"):
        divide(10, 0)

# Inspect the exception object:
def test_divide_by_zero_details():
    exc_info = pytest.raises(ZeroDivisionError)
    with exc_info:
        divide(10, 0)
    assert "zero" in str(exc_info.value).lower()

# unittest equivalent:
class TestDivide(unittest.TestCase):
    def test_divide_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            divide(10, 0)

    def test_divide_by_zero_message(self):
        with self.assertRaisesRegex(ZeroDivisionError, "cannot divide by zero"):
            divide(10, 0)
```

---

## Mid-Level

---

### Q5. What are pytest fixtures? How do they differ from `setUp`/`tearDown`?

**Answer:**

Fixtures are reusable setup/teardown functions injected into tests by name.

```python
import pytest
import sqlite3

# Fixture with teardown:
@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INT, name TEXT)")
    yield conn    # test runs here
    conn.close()  # teardown after test

# Multiple tests share the same fixture:
def test_insert_user(db):
    db.execute("INSERT INTO users VALUES (1, 'Alice')")
    count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert count == 1

def test_empty_users(db):
    count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert count == 0    # fresh DB per test (function scope)
```

**Key differences from setUp/tearDown:**

| | setUp/tearDown | pytest fixture |
|--|---------------|----------------|
| Scope | Per class | function / class / module / session |
| Dependencies | Manual setup chain | Auto-injected by name, composable |
| Teardown | tearDown() separate | `yield` — setup and teardown in one function |
| Sharing | Only within class | conftest.py makes them global |
| Multiple | One setUp | Any number, composable |

**Fixture scope controls how often setup runs:**

```python
@pytest.fixture(scope="session")   # once for entire test run
def app_server():
    server = start_server()
    yield server
    server.stop()

@pytest.fixture(scope="function")  # default: once per test
def fresh_client(app_server):      # depends on session-scoped app_server
    return app_server.test_client()
```

---

### Q6. What is `@pytest.mark.parametrize`? When would you use it?

**Answer:**

`parametrize` runs the same test with different inputs, cleanly:

```python
import pytest

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True

@pytest.mark.parametrize("n,expected", [
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

This runs as 8 separate tests — each appears independently in output.
One failure doesn't stop the others.

**When to use:** Anytime you find yourself copy-pasting a test with different
input values. It's cleaner, produces clearer failure messages, and is easier
to extend.

**Alternative: table-driven approach for readability:**

```python
CASES = [
    pytest.param(2,   True,  id="smallest-prime"),
    pytest.param(4,   False, id="even-composite"),
    pytest.param(17,  True,  id="prime"),
    pytest.param(-1,  False, id="negative"),
]

@pytest.mark.parametrize("n,expected", CASES)
def test_is_prime(n, expected):
    assert is_prime(n) == expected
```

---

### Q7. What is mocking? When should you mock and when shouldn't you?

**Answer:**

Mocking replaces a real dependency with a controllable fake during testing.

```python
from unittest.mock import Mock, patch
import requests

def get_weather(city: str) -> dict:
    response = requests.get(f"https://api.weather.com/v1/{city}")
    response.raise_for_status()
    return response.json()

# Without mock: test makes real network call (slow, flaky, costs money)
# With mock:
@patch("requests.get")
def test_get_weather(mock_get):
    mock_get.return_value.json.return_value = {"temp": 22, "condition": "sunny"}
    mock_get.return_value.raise_for_status = Mock()

    result = get_weather("London")

    assert result["temp"] == 22
    mock_get.assert_called_once_with("https://api.weather.com/v1/London")
```

**Mock when the dependency:**
- Makes network calls (external APIs, microservices)
- Reads/writes to a database
- Touches the file system
- Has non-deterministic output (time, random numbers)
- Sends emails, SMS, or other side effects
- Is slow (>10ms for a unit test)

**Don't mock:**
- Pure functions (they're already isolated)
- Your own domain logic (testing implementation, not behavior)
- Simple data structures
- When an in-memory fake is available (SQLite instead of mocking the DB)

**The rule:** Mock at system **boundaries** (external I/O), not at the interior
of your own code.

---

### Q8. Explain the difference between `@patch` and `monkeypatch`. When do you use each?

**Answer:**

Both replace objects during testing. The key difference is **context**:

```python
# @patch (unittest.mock) — works as decorator or context manager:
from unittest.mock import patch

@patch("mymodule.requests.get")         # decorator style
def test_with_decorator(mock_get):
    mock_get.return_value.json.return_value = {"data": 1}
    result = mymodule.fetch_data()
    assert result == {"data": 1}

def test_with_context():
    with patch("mymodule.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"data": 1}
        result = mymodule.fetch_data()

# monkeypatch (pytest) — injected as fixture, auto-undone:
def test_with_monkeypatch(monkeypatch):
    monkeypatch.setattr("requests.get", lambda url: MockResponse())
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setitem(config, "debug", True)
    # ALL patches automatically undone after test — no cleanup needed
```

**CRITICAL rule for `@patch`:** patch where the name is **used**, not where
it's **defined**:

```python
# In mymodule.py:   from requests import get
# WRONG:  @patch("requests.get")
# RIGHT:  @patch("mymodule.get")   ← patch where it's imported into

# In mymodule.py:   import requests
# CORRECT: @patch("mymodule.requests.get")
```

**When to use each:**
- `monkeypatch` — prefer in pytest-only codebases; simpler, auto-cleanup
- `@patch` — when you also need `call_count`, `assert_called_with`, or other Mock verification

---

### Q9. What is code coverage? What are its limits?

**Answer:**

Code coverage measures what percentage of your code was executed during tests.

```bash
pytest --cov=myapp --cov-report=term-missing
# Shows: which lines were NOT hit by any test
```

**Types:**
- **Line coverage:** was this line executed?
- **Branch coverage:** was each if/else branch taken?
- **Condition coverage:** was each boolean sub-expression True AND False?

**The limit of coverage — it's a necessary but not sufficient metric:**

```python
def absolute_value(n):
    if n < 0:
        return -n
    return n

def test_absolute_value():
    assert absolute_value(-5) == 5   # 100% line coverage!

# But this test would also pass for a BROKEN implementation:
def absolute_value(n):
    return 5   # always returns 5 — 100% coverage, completely wrong
```

**What 80% coverage means:** 80% of your code runs. It says nothing about
whether you're asserting the right things.

**Rules for healthy coverage:**
- 80%+ is a reasonable minimum for production code
- 100% is possible but not always worth the effort
- Prioritize coverage on business-critical paths
- Never game the metric — coverage without assertions is worthless

---

## Senior Level

---

### Q10. How do you design code to be testable?

**Answer:**

Testability is a design quality, not an afterthought. Hard-to-test code is
usually also poorly designed.

**1. Dependency Injection — don't create, receive:**

```python
# Hard to test (hardwired dependency):
class OrderService:
    def __init__(self):
        self.db = PostgresDB(url=os.environ["DB_URL"])   # can't swap!

    def create_order(self, items):
        return self.db.insert("orders", items)

# Easy to test (injected dependency):
class OrderService:
    def __init__(self, db):   # inject any DB — real or fake
        self.db = db

    def create_order(self, items):
        return self.db.insert("orders", items)

# In production:
service = OrderService(db=PostgresDB(url=...))

# In tests:
service = OrderService(db=FakeDatabase())   # or Mock()
```

**2. Separate pure logic from I/O:**

```python
# Hard to test: logic mixed with I/O
def process_orders():
    orders = fetch_from_db()       # I/O
    result = [o for o in orders if o.total > 100]  # logic
    send_to_api(result)            # I/O

# Easy to test: logic is pure function, I/O is thin wrapper
def filter_large_orders(orders: list) -> list:
    return [o for o in orders if o.total > 100]   # pure → trivial to test

def process_orders():
    orders = fetch_from_db()          # I/O (test separately)
    filtered = filter_large_orders(orders)
    send_to_api(filtered)             # I/O (test separately)
```

**3. Avoid global state, singletons, and hidden dependencies:**

```python
# Problem:
def calculate_discount(cart):
    settings = GlobalConfig.instance()   # hidden dependency!
    ...

# Better:
def calculate_discount(cart, config: Config):   # explicit dependency
    ...
```

---

### Q11. Explain TDD. What does the Red-Green-Refactor cycle look like in practice?

**Answer:**

TDD is a design discipline: write a failing test **before** writing production code.

```
RED     → Write a test that fails (the feature doesn't exist yet)
GREEN   → Write the minimum code to make it pass (no more, no less)
REFACTOR→ Clean up — remove duplication, improve names, restructure
          (tests stay green throughout refactor)
Repeat
```

**Example — building a password validator:**

```python
# RED: test first — class doesn't exist yet
def test_password_must_be_8_chars():
    with pytest.raises(ValueError, match="8 characters"):
        validate_password("short")

# GREEN: minimum code to pass
def validate_password(pwd):
    if len(pwd) < 8:
        raise ValueError("Password must be at least 8 characters")

# RED: add next requirement
def test_password_must_have_uppercase():
    with pytest.raises(ValueError, match="uppercase"):
        validate_password("alllower1")

# GREEN: extend
def validate_password(pwd):
    if len(pwd) < 8:
        raise ValueError("Password must be at least 8 characters")
    if not any(c.isupper() for c in pwd):
        raise ValueError("Password must contain an uppercase letter")

# Continue for each requirement...

# REFACTOR: now that tests cover the behavior, clean up the implementation
```

**Why TDD improves design:**
- Forces you to think about the interface before writing code
- If something is hard to test, it's a design smell (too coupled, too complex)
- Each feature has a test from day one — no gaps

---

### Q12. What causes flaky tests? How do you diagnose and fix them?

**Answer:**

A flaky test passes sometimes and fails other times without any code change.
This is **worse than a consistently failing test** — it erodes trust in the
entire test suite.

**Common causes and fixes:**

| Cause | Symptom | Fix |
|-------|---------|-----|
| Time dependency | Fails occasionally at midnight, month boundaries | `freezegun`, mock `datetime.now()` |
| Random data | Fails with specific random seeds | Seed random, or parametrize |
| Test ordering | Fails when run in different order | Isolate state, use fresh fixtures |
| Async timing | Fails under load | Explicit waits, not `time.sleep()` |
| External service | Fails when service is slow/down | Mock the service |
| Shared global state | Fails when specific test runs before it | Use autouse fixture to reset |
| Resource leaks | Fails after many test runs | Proper teardown in fixtures |

**Debugging approach:**

```bash
# Run repeatedly to confirm flakiness:
pytest tests/test_scheduler.py --count=100   # pytest-repeat plugin

# Run in random order to find ordering dependencies:
pytest -p randomly

# Run in isolation:
pytest tests/test_scheduler.py::test_job_runs_at_midnight -v
```

---

### Q13. How do you structure a testing strategy for a production microservice?

**Answer:**

A production testing strategy has layers, each with a clear purpose:

```
┌────────────────────────────────────────────────────────────┐
│ LAYER          WHAT                 WHEN               HOW │
├────────────────────────────────────────────────────────────┤
│ Unit           Pure logic           Every commit      Fast  │
│ Component      Service in isolation PR + main branch  Medium│
│ Integration    Service + real DB    PR + main branch  Medium│
│ Contract       API between services Nightly           Medium│
│ E2E            Full user flow       Pre-deploy        Slow  │
│ Smoke          Critical paths       Post-deploy       Fast  │
└────────────────────────────────────────────────────────────┘
```

**In CI/CD pipeline:**

```yaml
On every commit:
  - pytest tests/unit/ -x --timeout=30   # fast, fail fast
  - pytest tests/integration/ --timeout=120

On merge to main:
  - Full suite + coverage gate (≥ 80%)
  - Contract tests

Pre-deploy:
  - E2E tests against staging
  - Performance tests if needed

Post-deploy:
  - Smoke tests against production
  - Synthetic monitoring (run tests against real traffic)
```

**Key decisions:**
- Where to draw the mock boundary (mock at DB? at HTTP? at service boundary?)
- What's in the contract suite vs integration suite
- Which tests are blocking (must pass to deploy) vs advisory
- How to handle DB migrations in integration tests (Docker + Alembic)

---

## 🔴 Trap Questions

---

### Trap 1: What's wrong with this test?

```python
def test_user_creation():
    db = create_test_db()
    service = UserService(db)

    service.create_user("alice@example.com")
    service.create_user("bob@example.com")

    users = db.get_all_users()
    assert len(users) == 2
```

**Answer:** The test assumes the DB starts empty. If another test ran before
and left data in the DB, this test fails. Fix: use a fixture that creates a fresh
DB per test (`scope="function"`), or truncate tables in setUp.

---

### Trap 2: Why might this mock test give false confidence?

```python
@patch("services.user_service.EmailClient")
def test_registration_sends_email(MockEmail):
    service = UserService()
    service.register("alice@example.com")
    MockEmail.return_value.send.assert_called_once()
```

**Answer:** The mock patches `EmailClient` in `services.user_service`. If the
import path changes (e.g., refactor to `services.email.EmailClient`), the patch
silently patches the wrong thing — the real `EmailClient` runs, but the mock
assertion still passes because `MockEmail.return_value.send` is a new mock
object that was "called" zero times — no, wait, this test would _fail_ if the
import path changes because the Mock won't intercept the real call.

Actually the deeper issue: this test is testing the mock, not behavior. If someone
changes the email sending to use a different mechanism entirely, the test still
passes if they mock the new mechanism correctly — but didn't test the actual sending.

Better: test an observable side effect (email in a test mailbox) or use a spy.

---

### Trap 3: What's the difference between `Mock` and `MagicMock`?

**Answer:**

`Mock` doesn't implement magic methods. `MagicMock` does:

```python
from unittest.mock import Mock, MagicMock

m = Mock()
len(m)    # TypeError: object of type 'Mock' has no len()

m = MagicMock()
len(m)    # 0 — MagicMock implements __len__
m[0]      # MagicMock() — implements __getitem__
str(m)    # some string
```

**Use `Mock` when:** you want explicit control over which magic methods exist.
**Use `MagicMock` when:** you're mocking objects that need to behave like
containers, context managers, or support iteration — which is most of the time.

---

### Trap 4: Why shouldn't you test private methods directly?

**Answer:**

Testing private methods (prefixed with `_` in Python) couples your tests to
the internal implementation. When you refactor internals, tests break even
though the behavior is unchanged.

```python
class PasswordHasher:
    def hash(self, password):          # public: test this
        return self._bcrypt_hash(self._normalize(password))

    def _normalize(self, pwd):         # private: don't test this directly
        return pwd.strip().lower()

    def _bcrypt_hash(self, pwd):       # private: don't test this directly
        import bcrypt
        return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt())
```

Test `hash()` with various inputs including ones that exercise normalization.
If `_normalize` has a bug, `hash()` tests will catch it. If you later replace
`bcrypt` with argon2, only `hash()` tests matter — `_bcrypt_hash` tests become
dead weight.

**Exception:** Very complex private logic that has many edge cases may warrant
its own tests. But if it's that complex, consider whether it should be its own
class.

---

### Trap 5: What's `pytest.approx` and why do you need it?

**Answer:**

Floating point arithmetic is not exact:

```python
assert 0.1 + 0.2 == 0.3   # AssertionError!
# 0.1 + 0.2 = 0.30000000000000004

assert 0.1 + 0.2 == pytest.approx(0.3)   # passes!
assert pytest.approx(1/3) == 0.333       # passes with default tolerance
assert pytest.approx(100, rel=0.01) == 101  # within 1%
assert pytest.approx(100, abs=2) == 101     # within ±2
```

Without `approx`, float comparisons in tests are unreliable and platform-
dependent. Always use `pytest.approx()` for float assertions.

---

## 🔥 Rapid-Fire

```
Q: What does AAA stand for?
A: Arrange, Act, Assert — the structure of a well-written test

Q: fixture scope order (most to least frequent)?
A: function → class → module → package → session

Q: How to run only tests matching "login" keyword?
A: pytest -k "login"

Q: How to re-run only last failed tests?
A: pytest --lf

Q: patch at definition or usage?
A: Usage — patch where the name is imported, not where it's defined

Q: Mock vs MagicMock?
A: MagicMock also implements magic methods (__len__, __getitem__, etc.)

Q: AsyncMock used for?
A: Mocking async functions (coroutines) — must await; assert_awaited_once()

Q: What is a test fixture scope "session"?
A: Fixture runs once for the entire pytest session (all tests across all files)

Q: Coverage 100% guarantees no bugs?
A: No — it only means every line was executed, not that every case was asserted

Q: What is conftest.py?
A: A pytest file that defines fixtures shared across multiple test files

Q: When to use property-based testing (hypothesis)?
A: When you want to verify invariants hold for arbitrary inputs — especially
   math functions, serializers, parsers, sort algorithms

Q: What makes a test "brittle"?
A: It tests implementation details — breaks on internal refactors even when
   observable behavior is unchanged
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🧪 pytest Guide | [pytest_guide.md](./pytest_guide.md) |
| ⬅️ Previous | [16 — Design Patterns](../16_design_patterns/theory.md) |
| ➡️ Next | [18 — Performance Optimization](../18_performance_optimization/theory.md) |
