# pytest — Deep Dive

pytest is like autocomplete for test discovery: you write a function named `test_something`, and pytest finds it, runs it, and tells you exactly what failed — no ceremony required.

---

## Learning Priority

**Must Learn** — daily use, interview essential:
`test_` naming convention · plain `assert` · fixtures · `@pytest.mark.parametrize`

**Should Learn** — important for real projects:
fixture scope (function / class / module / session) · `conftest.py` · `pytest.raises` · `xfail` / `skip`

**Good to Know** — useful in specific situations:
`pytest-asyncio` · custom markers · `pytest.ini` config · `tmp_path` / `monkeypatch`

**Reference** — know it exists, look up when needed:
`pytest-cov` · `pytest-benchmark` · `pytest-xdist` · `capsys` / `caplog`

---

## 1. Why pytest?

Think of unittest as a form you have to fill out in triplicate — class, setUp, assertEqual. pytest is plain Python: if the assertion fails, you see exactly what was wrong.

```python
# unittest way
class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

# pytest way — nothing to import, nothing to inherit
def test_add():
    assert add(2, 3) == 5
```

pytest rewrites your `assert` statements at collection time, so when they fail you get rich diffs:

```
AssertionError: assert [1, 2, 4] == [1, 2, 3]
  At index 2 diff: 4 != 3
```

**Test discovery rules** — pytest finds tests automatically:
- Files named `test_*.py` or `*_test.py`
- Functions named `test_*`
- Classes named `Test*` (with `test_*` methods)
- No `__init__.py` required

```bash
pytest                        # discover and run everything
pytest test_math.py           # single file
pytest test_math.py::test_add # single function
pytest -v                     # verbose: one line per test
pytest -x                     # stop on first failure
pytest -k "add"               # run tests whose name matches "add"
pytest --tb=short             # shorter tracebacks
pytest -s                     # show print() output
```

---

## 2. Basic Tests — assert and pytest.raises

Every test is a function. If it raises an exception, it fails. If it returns normally, it passes.

```python
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("cannot divide by zero")
    return a / b


def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, -1) == -2


def test_divide_by_zero():
    import pytest
    with pytest.raises(ZeroDivisionError):      # ← asserts exception IS raised
        divide(10, 0)

def test_divide_by_zero_message():
    import pytest
    with pytest.raises(ZeroDivisionError, match="cannot divide by zero"):  # ← checks message too
        divide(10, 0)
```

**Floating point — always use `pytest.approx`:**

```python
assert 0.1 + 0.2 == pytest.approx(0.3)          # passes
assert 0.1 + 0.2 == 0.3                          # AssertionError!

assert result == pytest.approx(1050.0, rel=1e-6) # relative tolerance
assert result == pytest.approx(3.14, abs=0.01)   # absolute tolerance
```

**Common mistakes:**
- Forgetting `import pytest` for `pytest.raises` (often at top of file)
- Testing `== True` instead of `is True` — use `assert result is True` for booleans

---

## 3. Fixtures — Setup and Teardown

A **fixture** is a function decorated with `@pytest.fixture`. pytest injects it into any test that names it as a parameter. It replaces setUp/tearDown without requiring a class.

```python
import pytest

@pytest.fixture
def empty_account():
    """A fresh BankAccount with zero balance."""
    return BankAccount("Test User")          # ← setup only

@pytest.fixture
def funded_account():
    return BankAccount("Test User", 1000)


def test_deposit(empty_account):             # ← pytest injects empty_account
    empty_account.deposit(500)
    assert empty_account.balance == 500

def test_withdraw(funded_account):
    funded_account.withdraw(1000)
    assert funded_account.balance == 0
```

**Fixtures with teardown — use `yield`:**

```python
@pytest.fixture
def db_connection():
    conn = sqlite3.connect(":memory:")                       # setup
    conn.execute("CREATE TABLE users (id INT, name TEXT)")
    yield conn                                               # test runs HERE
    conn.close()                                             # teardown — always runs

def test_insert_user(db_connection):
    db_connection.execute("INSERT INTO users VALUES (1, 'Alice')")
    count = db_connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert count == 1
```

**Fixture dependencies — fixtures can depend on other fixtures:**

```python
@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE items (id INT, name TEXT)")
    yield conn
    conn.close()

@pytest.fixture
def populated_db(db):          # ← depends on db fixture
    db.execute("INSERT INTO items VALUES (1, 'Widget')")
    db.commit()
    return db

def test_item_exists(populated_db):
    row = populated_db.execute("SELECT name FROM items WHERE id=1").fetchone()
    assert row[0] == "Widget"
```

**autouse — run a fixture for every test without requesting it:**

```python
@pytest.fixture(autouse=True)
def reset_global_cache():
    yield
    cache.clear()              # ← runs after every test in this file
```

---

## 4. Fixture Scope — How Often Setup Runs

**Scope** controls how many tests share one fixture instance. Think of it as the fixture's lifespan.

```
function  (default) → new instance for every test
class               → one instance shared by all tests in a class
module              → one instance shared by all tests in a file
package             → one instance shared by all tests in a package directory
session             → one instance for the entire pytest run
```

```python
@pytest.fixture(scope="function")   # default — fresh per test
def temp_dir(tmp_path):
    return tmp_path

@pytest.fixture(scope="module")     # created once per file — good for expensive setup
def shared_user():
    return User("alice smith", "alice@example.com", 25)

@pytest.fixture(scope="session")    # created once for entire run
def app_server():
    server = start_test_server()
    yield server
    server.stop()
```

**Scope rule:** a fixture can only use other fixtures of the same scope or a wider scope. A `function`-scoped fixture cannot depend on a `module`-scoped fixture that yields.

**Common mistake — using `scope="session"` for mutable objects:**

```python
# WRONG: session-scoped list shared across all tests — mutations leak
@pytest.fixture(scope="session")
def items():
    return []   # all tests append to this same list!

# RIGHT: use function scope for mutable state
@pytest.fixture
def items():
    return []
```

---

## 5. parametrize — Data-Driven Tests

`@pytest.mark.parametrize` runs one test function with multiple sets of inputs. Each set becomes an independent test case with its own pass/fail.

```python
import pytest

def is_valid_email(email):
    import re
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))


@pytest.mark.parametrize("email, expected", [
    ("user@example.com",     True),
    ("user.name@domain.co",  True),
    ("plainaddress",         False),
    ("@missing.com",         False),
    ("user@",                False),
    ("",                     False),
])
def test_email_validation(email, expected):
    assert is_valid_email(email) == expected
```

This runs 6 separate tests. One failure doesn't stop the others.

**Multiple parameters — all combinations:**

```python
@pytest.mark.parametrize("a", [1, 2])
@pytest.mark.parametrize("b", [10, 20])
def test_multiply(a, b):
    assert a * b == b * a   # 4 combinations: (1,10), (1,20), (2,10), (2,20)
```

**Custom test IDs — readable output:**

```python
@pytest.mark.parametrize("principal, rate, years, expected", [
    (1000, 0.05, 1,  pytest.approx(1050.0)),
    (1000, 0.05, 2,  pytest.approx(1102.5)),
    pytest.param(1000, 0.0, 5, pytest.approx(1000.0), id="zero-rate"),
    pytest.param(1000, 0.10, 10, pytest.approx(2593.74, rel=1e-3), id="decade"),
])
def test_compound_interest(principal, rate, years, expected):
    assert calculate_compound_interest(principal, rate, years) == expected
```

Output: `test_compound_interest[zero-rate]` instead of `test_compound_interest[1000-0.0-5-...]`.

**Combining fixtures and parametrize:**

```python
@pytest.mark.parametrize("amount", [1, 50, 999.99, 1000])
def test_deposit_valid(empty_account, amount):   # empty_account = fixture, amount = parametrize
    empty_account.deposit(amount)
    assert empty_account.balance == amount
```

---

## 6. Markers — skip, xfail, custom

**Markers** attach metadata to tests. Built-in markers control execution; custom markers let you filter tests.

```python
import pytest

@pytest.mark.skip(reason="Feature not yet implemented")
def test_unimplemented():
    assert False                   # never runs

@pytest.mark.skipif(sys.platform == "win32", reason="Linux/Mac only")
def test_unix_paths():
    assert os.path.exists("/")

@pytest.mark.xfail(reason="Known bug: issue #42")
def test_known_failure():
    assert 1 == 2                  # expected to fail — counts as xfail, not error

@pytest.mark.xfail(strict=True, reason="This MUST fail")
def test_strict_xfail():
    assert False                   # if this passes, pytest reports it as an error
```

**Custom markers — filter with `-m`:**

```python
@pytest.mark.slow
def test_expensive_operation():
    ...

@pytest.mark.integration
def test_database_query():
    ...
```

```bash
pytest -m slow                    # run only slow tests
pytest -m "not slow"              # skip slow tests
pytest -m "integration and not db"
```

Register custom markers in `pytest.ini` to avoid warnings:

```ini
[pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests requiring external services
```

---

## 7. conftest.py — Shared Fixtures

`conftest.py` is a special pytest file. Fixtures defined there are available to all tests in the same directory and all subdirectories — without importing.

```
project/
├── conftest.py          ← fixtures available to ALL tests
├── tests/
│   ├── conftest.py      ← fixtures for tests/ subtree only
│   ├── test_users.py
│   └── api/
│       ├── conftest.py  ← fixtures for api/ tests only
│       └── test_endpoints.py
```

```python
# conftest.py at project root
import pytest

@pytest.fixture(scope="session")
def app():
    from myapp import create_app
    app = create_app(testing=True)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    from myapp.database import db
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()
```

Any test file in the project can now use `client` and `db` fixtures without importing them.

---

## 8. pytest-asyncio — Testing Async Code

`pytest-asyncio` lets you write `async def` test functions and `async def` fixtures.

```bash
pip install pytest-asyncio
```

```python
import pytest

@pytest.mark.asyncio
async def test_fetch_user():
    result = await fetch_user(user_id=1)
    assert result["name"] == "Alice"

# Async fixture:
@pytest.fixture
async def async_db():
    db = await connect_async_db()
    yield db
    await db.close()

# Mock async functions with AsyncMock:
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_async_with_mock():
    mock_repo = AsyncMock()
    mock_repo.find_user.return_value = {"id": 1, "name": "Alice"}

    result = await fetch_user_async(mock_repo, 1)

    assert result["name"] == "Alice"
    mock_repo.find_user.assert_awaited_once_with(1)  # ← not assert_called, assert_awaited
```

**Auto mode** — mark all async tests automatically:

```ini
# pytest.ini
[pytest]
asyncio_mode = auto
```

With `asyncio_mode = auto`, you don't need `@pytest.mark.asyncio` on every test.

---

## Common Mistakes

**1. Fixture scope mismatch — test function uses session-scoped mutable data:**

```python
# WRONG: all tests share one list, mutations bleed through
@pytest.fixture(scope="session")
def user_list():
    return []

# RIGHT: function scope for mutable objects
@pytest.fixture
def user_list():
    return []
```

**2. Not using `pytest.approx` for floats:**

```python
assert 0.1 + 0.2 == 0.3           # FAILS — float precision
assert 0.1 + 0.2 == pytest.approx(0.3)  # PASSES
```

**3. Over-mocking — mocking your own business logic:**

```python
# WRONG: you're testing the mock, not the logic
def test_process():
    mock_validator = Mock(return_value=True)
    mock_calculator = Mock(return_value=99)
    result = process(mock_validator, mock_calculator)  # no real code runs!
    assert result == 99

# RIGHT: only mock external boundaries (DB, API, file I/O)
def test_process(db):
    result = process(real_validator, real_calculator, db=db)
    assert result == 99
```

**4. Missing `conftest.py` for shared fixtures — duplicating fixture code across test files.**

**5. Testing the fixture, not the behavior:**

```python
# WRONG: tests setup, not behavior
def test_fixture_not_none(empty_account):
    assert empty_account is not None

# RIGHT: test what the code does
def test_new_account_has_zero_balance(empty_account):
    assert empty_account.balance == 0
```

---

## Navigation

| | |
|---|---|
| Back to root | [17_testing/theory.md](../theory.md) |
| Practice questions | [practice.md](./practice.md) |
| Local practice | [practice_local.py](./practice_local.py) |
| Sibling: unittest | [../02_unittest/theory.md](../02_unittest/theory.md) |
| Sibling: mocking | [../03_mocking/theory.md](../03_mocking/theory.md) |

**[Back to README](../../README.md)**
