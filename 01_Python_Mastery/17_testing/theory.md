<a id="top"></a>
# 🧪 Testing in Python — Deep Dive

> Complete reference for Python testing: unit tests, pytest, mocking, fixtures,
> parameterization, coverage, async testing, and production testing strategy.

## 📖 Table of Contents

- [1. Why Testing? The Safety Net Mental Model](#1-why-testing-the-safety-net-mental-model)
- [2. Test Types and the Testing Pyramid](#2-test-types-and-the-testing-pyramid)
- [3. `unittest` — The Standard Library Framework](#3-unittest--the-standard-library-framework)
  - [Running unittest](#running-unittest)
- [4. pytest — The Modern Way](#4-pytest--the-modern-way)
  - [Running pytest](#running-pytest)
  - [pytest Assertion Introspection](#pytest-assertion-introspection)
- [5. Fixtures — The Heart of pytest](#5-fixtures--the-heart-of-pytest)
  - [conftest.py — Shared Fixtures](#conftestpy--shared-fixtures)
- [6. Parametrize — Data-Driven Tests](#6-parametrize--data-driven-tests)
- [7. Mocking — `unittest.mock` in Depth](#7-mocking--unittestmock-in-depth)
  - [The Problem Mocking Solves](#the-problem-mocking-solves)
  - [Mock Object](#mock-object)
  - [patch — The Standard Tool](#patch--the-standard-tool)
  - [pytest's monkeypatch](#pytests-monkeypatch)
- [8. Test Doubles — Mock vs Stub vs Fake vs Spy](#8-test-doubles--mock-vs-stub-vs-fake-vs-spy)
- [9. Testing Exceptions and Edge Cases](#9-testing-exceptions-and-edge-cases)
- [10. Testing Classes and Stateful Objects](#10-testing-classes-and-stateful-objects)
- [11. Async Testing — pytest-asyncio](#11-async-testing--pytest-asyncio)
- [12. Code Coverage](#12-code-coverage)
- [13. Test Organization and Naming](#13-test-organization-and-naming)
  - [File Structure](#file-structure)
  - [Naming Conventions](#naming-conventions)
  - [Marks](#marks)
- [14. TDD — Test-Driven Development](#14-tdd--test-driven-development)
- [15. Property-Based Testing — Hypothesis](#15-property-based-testing--hypothesis)
- [16. Common Pitfalls and Anti-Patterns](#16-common-pitfalls-and-anti-patterns)
- [17. CI/CD Integration](#17-cicd-integration)
  - [📂 Subfolder Deep Dives](#-subfolder-deep-dives)
  - [🔥 Summary](#-summary)

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

<a id="1-why-testing-the-safety-net-mental-model"></a>
# 1. Why Testing? The Safety Net Mental Model

Imagine a high-wire acrobat. Without a safety net, every step is terrifying — one slip means catastrophe. With a net, the act is still skillful, but a slip means recovery, not disaster. Code without tests is the same walk without a net: every change is a gamble, every deployment a prayer. Tests don't make your code perfect — they make your mistakes survivable.

Without tests:

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

💡 **Hint:** "Hard to test" is a design smell, not a testing problem. If a function is hard to test, it usually does too much, has hidden dependencies, or lacks clear inputs/outputs. Tests improve your code's design.

📝 **Practice:** [Q1 — Write a test function](./practice.md#q1--pytest--write-a-test-function)

> [↑ Back to Top](#top)

---

<a id="2-test-types-and-the-testing-pyramid"></a>
# 2. Test Types and the Testing Pyramid

Think of building a house inspection system. You inspect every individual nail and beam (unit tests — fast, many). Then you check that walls and floors connect properly (integration tests — fewer, slower). Finally, you walk through the finished house as a real person would (E2E tests — few, slowest). You don't do the walk-through for every nail — that would take forever and tell you nothing extra. The testing pyramid is just this common sense applied to software.

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

⚠️ **Common Mistake:** Writing only E2E tests because "they test everything." They do test more, but they're 100x slower and break for unrelated reasons (network flakiness, timing). A slow test suite gets skipped — which defeats the entire purpose.

💡 **Hint:** The "ice cream cone anti-pattern" is an inverted pyramid: many E2E, some integration, few unit. This is what teams end up with when they skip unit testing early. It leads to slow, flaky CI and painful debugging.

📝 **Practice:** [Q2 — assert with multiple types](./practice.md#q2--pytest--assert-with-multiple-types)

> [↑ Back to Top](#top)

---

<a id="3-unittest--the-standard-library-framework"></a>
# 3. `unittest` — The Standard Library Framework

Think of `unittest` like a formal office building — everything has its own assigned desk, there's a strict dress code (methods must start with `test_`), and you check in (`setUp`) and check out (`tearDown`) for every meeting. It's structured and reliable, and it comes built into Python with no extra install. Most modern teams reach for pytest instead, but `unittest` is everywhere in legacy codebases and still perfectly valid for simple projects.

📖 **Deep dive →** [02_unittest/theory.md](./02_unittest/theory.md)

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
        cls.shared_resource = "expensive_setup"

    @classmethod
    def tearDownClass(cls):
        """Runs ONCE after all tests in this class."""
        pass  # cleanup shared resource

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
# self.assertRaises(Exc)          context manager for exceptions
# self.assertLogs(logger, level)  context manager for log output
# self.assertRegex(text, regexp)  re.search(regexp, text)

if __name__ == "__main__":
    unittest.main()
```

<a id="running-unittest"></a>
## Running unittest

```bash
python -m unittest test_module             # run one module
python -m unittest test_module.TestClass  # run one class
python -m unittest discover               # discover all test_*.py files
python -m unittest -v                     # verbose output
```

```
┌────────────── unittest lifecycle per test ─────────────────────────┐
│                                                                     │
│  setUpClass()      ← runs ONCE for the class                       │
│      │                                                              │
│  setUp()           ← runs before EACH test method                  │
│  test_method()     ← the actual test                               │
│  tearDown()        ← runs after EACH test method                   │
│      │                                                              │
│  tearDownClass()   ← runs ONCE after all tests in class            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

⚠️ **Common Mistake:** Putting expensive setup in `setUp()` (runs per-test) instead of `setUpClass()` (runs once). If you create a DB connection in `setUp`, you're creating it for every single test — potentially thousands of times.

📝 **Practice:** [Q10 — TestCase and setUp](./practice.md#q10--unittest--testcase-and-setup)

> [↑ Back to Top](#top)

---

<a id="4-pytest--the-modern-way"></a>
# 4. pytest — The Modern Way

Think of pytest as a modern co-working space vs. `unittest`'s formal office. No dress code — plain functions work, no class required. No check-in forms — just write `assert`. When something goes wrong, the output tells you exactly what failed and why, not just "AssertionError." pytest is the industry standard for a reason: it's faster to write, easier to read, and the failure output is genuinely helpful.

📖 **Deep dive →** [01_pytest/theory.md](./01_pytest/theory.md)

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

<a id="running-pytest"></a>
## Running pytest

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

<a id="pytest-assertion-introspection"></a>
## pytest Assertion Introspection

One of pytest's killer features — when an assertion fails, it shows exactly what went wrong without any special assertion methods:

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

💡 **Hint:** Use `pytest.approx()` for floating-point comparisons — never `==` with floats. `assert 0.1 + 0.2 == 0.3` fails due to floating-point representation; `assert 0.1 + 0.2 == pytest.approx(0.3)` passes.

📝 **Practice:** [Q1 — Write a test function](./practice.md#q1--pytest--write-a-test-function)

> [↑ Back to Top](#top)

---

<a id="5-fixtures--the-heart-of-pytest"></a>
# 5. Fixtures — The Heart of pytest

Think of fixtures like a restaurant mise en place — before the chef starts cooking (the test runs), everything is prepared and in its place: chopped vegetables (sample data), clean pans (fresh DB connection), preheated oven (server started). When the dish is served (test finishes), cleanup happens automatically. Fixtures let you describe *what your test needs*, and pytest wires everything together — no manual setup/teardown in every test.

Fixtures provide reusable setup/teardown. They're injected by name into test functions as parameters.

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

```
┌──────────── Fixture Scope — How Many Times Each Runs ──────────────┐
│                                                                     │
│  scope="function"  → once per test function  (default)             │
│  scope="class"     → once per test class                           │
│  scope="module"    → once per test file                            │
│  scope="package"   → once per package directory                    │
│  scope="session"   → once per entire pytest run                    │
│                                                                     │
│  Rule: wider scope = less teardown/setup = faster suite            │
│  Risk: wider scope = shared state between tests = harder isolation │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

<a id="conftestpy--shared-fixtures"></a>
## conftest.py — Shared Fixtures

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

⚠️ **Common Mistake:** Using `scope="session"` for fixtures that modify shared state (like inserting DB rows). Session-scoped fixtures run once and are reused — if one test modifies the fixture's state, the next test sees dirty data. Use `scope="function"` for anything stateful.

💡 **Hint:** Fixtures can depend on other fixtures — pytest handles the dependency graph automatically. `populated_db(db)` will automatically receive the `db` fixture, which will automatically set up and tear down in the right order.

📝 **Practice:** [Q3 — Fixtures as setup](./practice.md#q3--pytest--fixtures-as-setup)

> [↑ Back to Top](#top)

---

<a id="6-parametrize--data-driven-tests"></a>
# 6. Parametrize — Data-Driven Tests

Imagine testing a calculator with 20 different input pairs. Without parametrize, you'd write 20 separate test functions with almost identical code. With parametrize, you write the test once and provide a table of inputs — pytest runs it once for each row, labels each run, and reports failures per row. One function, 20 test cases.

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

# Multiple axes — creates all combinations (2×3 = 6 tests):
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

⚠️ **Common Mistake:** Stacking too many `@parametrize` decorators creating a combinatorial explosion. Two decorators with 5 items each = 25 tests. Three = 125. Check whether you really need all combinations or just specific pairs.

💡 **Hint:** Use `pytest.param(..., id="name")` to give meaningful names to complex test cases. Instead of `test_add_cases[1e308-1e308-inf]`, you get `test_add_cases[overflow]` in the output.

📝 **Practice:** [Q4 — parametrize basics](./practice.md#q4--pytest--parametrize-basics)

> [↑ Back to Top](#top)

---

<a id="7-mocking--unittestmock-in-depth"></a>
# 7. Mocking — `unittest.mock` in Depth

Think of mocking like a film set. The actors (your code) behave exactly as they would in real life, but the New York skyline behind them is a painted backdrop — not real. Mocks are the backdrops: they look and act like real databases, APIs, and services, but they're controlled fakes that never make network calls, never cost money, and always behave exactly as you program them. Without mocks, testing code that talks to external systems is slow, expensive, and unreliable.

📖 **Deep dive →** [03_mocking/theory.md](./03_mocking/theory.md)

<a id="the-problem-mocking-solves"></a>
## The Problem Mocking Solves

```
Your function calls:
  - External API    → slow, costs money, can be down
  - Database        → requires setup, modifies real data
  - File system     → leaves debris, platform-dependent
  - Time/random     → non-deterministic, makes tests flaky
  - Email/SMS       → sends real messages!

Mocking replaces these with controllable fakes.
```

<a id="mock-object"></a>
## Mock Object

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
m.connect.call_count         # 1
m.connect.call_args          # call("localhost", 5432)
m.connect.call_args_list     # [call("localhost", 5432)]

# Assert NOT called:
m.close.assert_not_called()
```

```
┌──────────────── Mock vs MagicMock ─────────────────────────────────┐
│                                                                     │
│  Mock          → basic mock, no magic methods pre-configured       │
│  MagicMock     → Mock + all dunder methods pre-configured          │
│                  (len, str, iter, getitem, enter/exit, etc.)        │
│                                                                     │
│  Use Mock when: you want explicit control, no implicit magic       │
│  Use MagicMock when: the code under test calls len(), [], with, etc│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

<a id="patch--the-standard-tool"></a>
## `patch` — The Standard Tool

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
# If your_module.py has: from requests import get
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

⚠️ **Common Mistake:** Patching the wrong location. `patch("requests.get")` patches the `get` attribute on the `requests` module. But if your code did `from requests import get`, then the name `get` in your module is a separate reference — you must patch `"your_module.get"` instead.

<a id="pytests-monkeypatch"></a>
## pytest's `monkeypatch`

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

💡 **Hint:** Prefer `monkeypatch` over `patch` for simple attribute replacements in pytest tests. It's cleaner (no decorator), automatically cleaned up, and works well with fixtures. Use `patch` when you need the mock object reference (for assertions) or are writing unittest-style tests.

📝 **Practice:** [Q15 — Basic Mock and return_value](./practice.md#q15--mock--basic-mock-and-return_value)

> [↑ Back to Top](#top)

---

<a id="8-test-doubles--mock-vs-stub-vs-fake-vs-spy"></a>
# 8. Test Doubles — Mock vs Stub vs Fake vs Spy

Think of test doubles like stunt doubles in film. You have five types: a dummy (just stands in a crowd scene — never used), a stub (says their line but does nothing else), a fake (acts the scene for real, but in a simplified way), a mock (acts AND checks that the director called on them correctly), and a spy (acts the real scene AND secretly films what happened). Each serves a different purpose and choosing the right one makes tests cleaner and more meaningful.

These terms come from Gerard Meszaros's *xUnit Test Patterns*:

```
┌──────────────────────── Test Double Types ─────────────────────────┐
│                                                                     │
│  Dummy   → passed but never used (fills a parameter slot)          │
│  Stub    → returns canned answers; doesn't verify interactions     │
│  Fake    → real implementation, but simplified (in-memory DB)      │
│  Mock    → pre-programmed with expectations; verifies calls        │
│  Spy     → real implementation that records how it was called      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
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

💡 **Hint:** In practice, "mock" is used loosely to mean any test double. What matters is the intent: are you verifying that something was called (mock/spy), or just providing a substitute return value (stub/fake)? Choose the simplest double that makes your test pass.

⚠️ **Common Mistake:** Using Mocks (which verify calls) when you just need a Stub (which provides data). Over-specifying call behavior (`assert_called_once_with` every method) makes tests fragile — they break when implementation details change even if behavior is correct.

📝 **Practice:** [Q25 — Mock vs Stub vs Fake](./practice.md#q25--doubles--mock-vs-stub-vs-fake)

> [↑ Back to Top](#top)

---

<a id="9-testing-exceptions-and-edge-cases"></a>
# 9. Testing Exceptions and Edge Cases

Think of edge cases like the corners of a table — most people never bump into them, but the ones who do really feel it. Testing only the "happy path" (valid inputs, normal flow) is like inspecting only the middle of a bridge. The failures happen at the edges: empty inputs, negative numbers, null values, maximum sizes, boundary conditions. A test suite that only tests success is only half a test suite.

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

# Test exact exception details:
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
    assert is_valid_age(0)    == True   # lower boundary
    assert is_valid_age(-1)   == False  # just below
    assert is_valid_age(150)  == True   # upper boundary
    assert is_valid_age(151)  == False  # just above
    assert is_valid_age(75)   == True   # middle

def test_type_errors():
    with pytest.raises(TypeError):
        add("1", 2)  # string + int

def test_overflow():
    result = add(float("inf"), 1)
    assert result == float("inf")
```

```
┌─────────────── Edge Cases Checklist ───────────────────────────────┐
│                                                                     │
│  For any function, test:                                            │
│  □ Empty input ([], "", None, 0)                                    │
│  □ Single item ([x], "a")                                          │
│  □ Maximum / minimum boundary values                               │
│  □ Value just above / below boundaries                             │
│  □ Wrong type (str where int expected)                             │
│  □ None where object expected                                      │
│  □ Duplicate values (sets, unique constraints)                     │
│  □ Very large input (performance boundary)                         │
│  □ Unicode / special characters (strings)                          │
│  □ Negative numbers (when input should be positive)                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

⚠️ **Common Mistake:** Writing `pytest.raises(Exception)` — the broad base class. This passes even if your code raises a completely different exception than expected. Always assert the specific exception type.

💡 **Hint:** The `match=` parameter in `pytest.raises` takes a regex. Use it to verify not just the type but the message: `pytest.raises(ValueError, match=r"must be positive")` — this prevents tests from passing when the right exception type is raised for the wrong reason.

📝 **Practice:** [Q5 — pytest.raises](./practice.md#q5--pytest--pytestrasies)

> [↑ Back to Top](#top)

---

<a id="10-testing-classes-and-stateful-objects"></a>
# 10. Testing Classes and Stateful Objects

Think of testing a stateful class like testing a vending machine. You don't just test "does it accept money" — you test the full sequence: insert coins → select item → get change → item dispensed. Each state transition matters. For classes, this means testing initial state, valid transitions, invalid transitions, and interactions with dependencies (like a payment service).

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
        if before == len(self.items):
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

💡 **Hint:** Use fixtures to set up initial state, then test each method independently. Never rely on test execution order — each test must be able to run in isolation. If `test_remove_item` depends on `test_add_item` having run first, you have a fragile test suite.

📝 **Practice:** [Q35 — Capstone end-to-end suite](./practice.md#q35--capstone--end-to-end-test-suite)

> [↑ Back to Top](#top)

---

<a id="11-async-testing--pytest-asyncio"></a>
# 11. Async Testing — pytest-asyncio

Testing async code is like testing a restaurant kitchen where multiple dishes cook simultaneously. The challenge isn't the food itself — it's coordinating the timing. `pytest-asyncio` gives you an event loop for each test so you can `await` coroutines directly in tests, mock async functions with `AsyncMock`, and write async fixtures that set up and tear down async resources cleanly.

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

⚠️ **Common Mistake:** Using `Mock()` for async functions instead of `AsyncMock()`. A regular `Mock` returns a non-awaitable object — when your code tries to `await mock_function()`, it raises `TypeError: object Mock can't be used in 'await' expression`. Always use `AsyncMock` for async functions.

💡 **Hint:** Set `asyncio_mode = auto` in `pytest.ini` so you don't need `@pytest.mark.asyncio` on every async test. This is the recommended setting for projects that use async throughout.

📝 **Practice:** [Q9 — Async testing](./practice.md#q9--pytest--async-testing)

> [↑ Back to Top](#top)

---

<a id="12-code-coverage"></a>
# 12. Code Coverage

Think of code coverage like a heat map of your test suite — it shows you which lines of your code have been executed during tests and which have never been touched. A line that's never run could be hiding a bug that will only surface in production. Coverage doesn't guarantee your tests are good (they could execute a line without asserting anything useful), but it does tell you where you haven't looked at all.

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

```
┌─────────────── Interpreting Coverage Numbers ──────────────────────┐
│                                                                     │
│  <50%   → clear warning sign: most code untested                   │
│  50-70% → getting started, needs significant work                  │
│  70-80% → reasonable for many projects                             │
│  80-90% → table stakes for production code                         │
│  >90%   → high confidence, but diminishing returns above ~95%      │
│                                                                     │
│  100% coverage can still miss:                                      │
│  - Wrong algorithm (tests pass but logic is incorrect)             │
│  - Missing edge cases (path covered but not all inputs)            │
│  - Race conditions (concurrent code hard to cover)                 │
│                                                                     │
│  Coverage is a proxy metric — what matters is what you ASSERT.     │
└─────────────────────────────────────────────────────────────────────┘
```

⚠️ **Common Mistake:** Chasing 100% coverage by writing "empty" tests that execute code without asserting anything. `def test_foo(): foo()` gives you line coverage but proves nothing. Coverage measures execution, not correctness.

💡 **Hint:** Enable branch coverage (`--cov-branch`) alongside line coverage. A function with `if condition: return X` can show 100% line coverage if only the `return X` path is hit — but branch coverage reveals the `else` path was never tested.

📝 **Practice:** [Q33 — Coverage analysis](./practice.md#q33--capstone--coverage-analysis)

> [↑ Back to Top](#top)

---

<a id="13-test-organization-and-naming"></a>
# 13. Test Organization and Naming

Think of test organization like a well-labeled filing cabinet. When a test fails at 3am in CI, you need to find the relevant test file, understand what it's testing, and diagnose the failure — in under a minute. Good naming and structure make this possible. Bad naming (`test_1`, `test_func`, `test_misc`) means every CI failure starts with a scavenger hunt.

<a id="file-structure"></a>
## File Structure

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

<a id="naming-conventions"></a>
## Naming Conventions

```python
# File:     test_<module_name>.py
# Class:    Test<ClassName>
# Method:   test_<method>_<scenario>_<expected>

# ❌ Bad names — tell you nothing:
def test_discount(): ...
def test_error(): ...
def test_1(): ...

# ✅ Good names — self-documenting:
def test_calculate_discount_zero_items_returns_zero(): ...
def test_calculate_discount_above_threshold_applies_20_percent(): ...
def test_user_register_duplicate_email_raises_conflict(): ...
def test_payment_process_insufficient_funds_raises_error(): ...
```

<a id="marks"></a>
## Marks

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

💡 **Hint:** Use marks to split your test suite into fast and slow runs. `pytest -m "not slow and not integration"` gives you a sub-second feedback loop during development. `pytest -m ""` (all tests) runs in CI before merge.

📝 **Practice:** [Q34 — Test organization](./practice.md#q34--capstone--test-organization)

> [↑ Back to Top](#top)

---

<a id="14-tdd--test-driven-development"></a>
# 14. TDD — Test-Driven Development

Think of TDD like writing a recipe before cooking. You first write down exactly what the finished dish should taste like (the test), then you cook until it matches (the implementation), then you clean up the kitchen (refactor). The key discipline: you never write code without a failing test waiting for it. This forces you to think about the interface before the implementation — which almost always leads to better design.

The Red-Green-Refactor cycle:

```
┌──────────────────── TDD Cycle ──────────────────────────────────────┐
│                                                                      │
│  RED     → Write a failing test for the feature you're about to     │
│            build. Run it. Confirm it fails (not errors).            │
│               │                                                      │
│               ▼                                                      │
│  GREEN   → Write the MINIMUM code to make the test pass.            │
│            Don't worry about elegance yet.                          │
│               │                                                      │
│               ▼                                                      │
│  REFACTOR → Clean up the code while keeping all tests green.        │
│             Extract duplication, improve names, simplify logic.     │
│               │                                                      │
│               └──────────────────────► back to RED for next feature │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
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
- Each feature is testable by design (loosely coupled by necessity)
- Provides a regression suite automatically as a side effect
- Small, incremental changes — easier to debug when something breaks

⚠️ **Common Mistake:** Skipping the RED step — writing code first, then writing tests to pass it. This defeats the design benefit of TDD. The test must fail first to prove it's actually testing something.

💡 **Hint:** TDD shines most for pure functions and business logic. For UI, database migrations, and infrastructure code, a lighter approach (write code, then test) is often more practical.

📝 **Practice:** [Q29 — TDD Red-Green-Refactor](./practice.md#q29--patterns--tdd-red-green-refactor)

> [↑ Back to Top](#top)

---

<a id="15-property-based-testing--hypothesis"></a>
# 15. Property-Based Testing — Hypothesis

Standard tests use hand-picked examples — they're only as good as the examples you thought of. Hypothesis is a library that generates thousands of random inputs automatically, shrinks failures to the smallest reproducing example, and finds edge cases that no human would think to test. Instead of writing "test that sort([3,1,2]) == [1,2,3]", you write "for any list, the sorted output must be ordered and contain the same elements" — and Hypothesis tries to break it.

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
    assert sorted(sort_list(lst)) == sorted(lst)

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

💡 **Hint:** Hypothesis remembers inputs that caused failures across runs (stored in a `.hypothesis/` directory). Once it finds a failing example, it will always re-test that specific case — even if you randomize everything else.

📝 **Practice:** [Q32 — Property-based testing with Hypothesis](./practice.md#q32--patterns--property-based-testing-with-hypothesis)

> [↑ Back to Top](#top)

---

<a id="16-common-pitfalls-and-anti-patterns"></a>
# 16. Common Pitfalls and Anti-Patterns

Every test suite accumulates bad habits over time. Tests that are too tightly coupled to implementation break when code is refactored correctly. Tests that share state fail randomly based on execution order. Tests with too many mocks prove nothing about real behavior. Recognizing these patterns early saves enormous debugging time later.

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

⚠️ **Common Mistake:** Letting tests share mutable global state (module-level lists, dicts, singletons). Tests that pass individually but fail when run together are a nightmare — they pass in local dev but fail in CI because CI runs all tests.

📝 **Practice:** [Q31 — Test isolation](./practice.md#q31--patterns--test-isolation)

> [↑ Back to Top](#top)

---

<a id="17-cicd-integration"></a>
# 17. CI/CD Integration

Think of CI as an automatic inspector who runs every time you propose a change. Before any code reaches production, the inspector runs the full test suite, checks coverage thresholds, and blocks the merge if anything fails. Without CI, tests only run when developers remember to run them — which is never under deadline pressure. CI makes the test suite automatically enforced.

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

💡 **Hint:** Use `-x` (stop on first failure) in CI — there's no point running 500 more tests once one fails. Fix the first failure, then re-run. This also keeps CI feedback faster.

🔍 **Good to Know:** `pytest --cov-fail-under=80` causes pytest to exit with a non-zero code if coverage drops below 80%. CI treats non-zero exit codes as failures — so coverage drops automatically block merges.

📝 **Practice:** [Q35 — End-to-end test suite](./practice.md#q35--capstone--end-to-end-test-suite)

> [↑ Back to Top](#top)

---

<a id="-subfolder-deep-dives"></a>
## 📂 Subfolder Deep Dives

This theory file covers all topics at survey depth. Each subfolder contains a full deep-dive with advanced patterns, production examples, and edge cases:

| Subfolder | What's Inside |
|---|---|
| [01_pytest/theory.md](./01_pytest/theory.md) | **pytest deep dive** — test discovery internals, conftest scoping rules, fixture factories, plugin ecosystem (`pytest-xdist`, `pytest-mock`, `pytest-benchmark`), custom marks, advanced parametrize patterns |
| [02_unittest/theory.md](./02_unittest/theory.md) | **unittest deep dive** — TestCase lifecycle, all assertion methods, `subTest()`, `mock.patch` in unittest context, migrating from unittest to pytest |
| [03_mocking/theory.md](./03_mocking/theory.md) | **Mocking deep dive** — `patch` vs `patch.object` vs `patch.dict`, `spec=` and `autospec=`, `AsyncMock`, call tracking, `create_autospec`, common pitfalls, `pytest-mock` plugin |

---

<a id="-summary"></a>
## 🔥 Summary

```
┌──────────────────── Testing Mental Model ──────────────────────────┐
│                                                                     │
│  CHOOSE YOUR TOOL:                                                  │
│  ─────────────────                                                  │
│  pytest           → default choice for all new projects            │
│  unittest         → legacy codebases, stdlib-only constraint       │
│  hypothesis       → when you need to test invariants at scale      │
│  pytest-asyncio   → any async code                                 │
│  pytest-cov       → coverage tracking in CI                        │
│                                                                     │
│  CHOOSE YOUR DOUBLE:                                                │
│  ──────────────────                                                 │
│  Fake    → simplest: real logic, simplified storage                │
│  Stub    → returns canned data, no verification                    │
│  Mock    → verifies that specific calls were made                  │
│  Spy     → wraps real impl, records what happened                  │
│                                                                     │
│  REMEMBER:                                                          │
│  - Patch WHERE IT'S USED, not where it's defined                   │
│  - Use AsyncMock for async functions, not Mock                     │
│  - Coverage measures execution, not correctness                    │
│  - Hard-to-test code is a design smell                             │
│  - Each test must be independent — no shared mutable state         │
│  - Test behavior, not implementation                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

<a id="-navigation"></a>
## 🔁 Navigation

**This folder:**
[theory.md](./theory.md) · [cheetsheet.md](./cheetsheet.md) · [interview.md](./interview.md) · [practice.md](./practice.md)

**Subfolders:**
[01_pytest/theory.md](./01_pytest/theory.md) · [02_unittest/theory.md](./02_unittest/theory.md) · [03_mocking/theory.md](./03_mocking/theory.md)

**Related modules:**
[16 — Design Patterns (DI pattern)](../16_design_patterns/theory.md) · [13 — Concurrency (async testing)](../13_concurrency/theory.md) · [12 — Context Managers (with in tests)](../12_context_managers/theory.md)

**Jump to specific topics:**
[pytest Fixtures](#5-fixtures--the-heart-of-pytest) · [Mock vs MagicMock](#mock-object) · [patch — WHERE it's used](#patch--the-standard-tool) · [Test Doubles comparison](#8-test-doubles--mock-vs-stub-vs-fake-vs-spy) · [TDD Cycle](#14-tdd--test-driven-development) · [Anti-Patterns](#16-common-pitfalls-and-anti-patterns)

---

| | |
|---|---|
| ⬅ Prev Module | [16 — Design Patterns](../16_design_patterns/theory.md) |
| ➡ Next Module | [18 — Performance Optimization](../18_performance_optimization/theory.md) |

**[🏠 Back to README](../../README.md)**

