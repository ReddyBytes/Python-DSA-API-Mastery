# ⚡ Testing — Cheatsheet

---

## Pytest Quick Reference

```
pytest                          run all tests
pytest test_foo.py              single file
pytest test_foo.py::test_bar    single test
pytest -k "add or subtract"     keyword filter
pytest -x                       stop on first failure
pytest -v                       verbose output
pytest --tb=short               shorter tracebacks
pytest -s                       show print() output
pytest -n 4                     parallel (pytest-xdist)
pytest --cov=mypackage          coverage report
pytest --lf                     last-failed tests only
```

---

## Fixtures

```python
import pytest

@pytest.fixture                          # function scope (default)
@pytest.fixture(scope="class")
@pytest.fixture(scope="module")
@pytest.fixture(scope="session")

@pytest.fixture
def db():
    conn = connect()                     # setup
    yield conn                           # test runs here
    conn.close()                         # teardown

@pytest.fixture(autouse=True)            # runs for every test in scope
def reset_state(): ...

@pytest.fixture(params=[1, 2, 3])        # parametrized fixture
def value(request):
    return request.param
```

---

## Parametrize

```python
@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (0, 0, 0),
    pytest.param(-1, 1, 0, id="negatives"),
    pytest.param(1, 0, 1, marks=pytest.mark.xfail),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

---

## Assertions

```python
assert x == 5
assert x != 5
assert x in [1, 2, 3]
assert isinstance(x, int)
assert x is None
assert x is not None

# Exceptions
with pytest.raises(ValueError):
    risky()

with pytest.raises(ValueError, match="must be positive"):
    risky(-1)

# Floats
assert result == pytest.approx(3.14, rel=1e-3)  # 0.1% tolerance
assert result == pytest.approx(3.14, abs=0.01)  # absolute tolerance
```

---

## Mocking

```python
from unittest.mock import Mock, MagicMock, patch, call

# Basic mock
m = Mock()
m.method(1, 2)
m.method.assert_called_once_with(1, 2)

# MagicMock — supports dunder methods
m = MagicMock()
len(m)         # works (returns 0 by default)
m[0]           # works

# Return values / side effects
m.get.return_value = {"id": 1}
m.get.side_effect = ConnectionError("down")
m.get.side_effect = [1, 2, 3]          # different value each call

# Patch (decorator)
@patch("mymodule.requests.get")         # patch WHERE IT'S USED
def test_fetch(mock_get):
    mock_get.return_value.json.return_value = {"key": "val"}

# Patch (context manager)
with patch("mymodule.open", mock_open(read_data="hello")):
    ...

# patch.object
with patch.object(MyClass, "method", return_value=42):
    ...

# Assertions
m.assert_called()
m.assert_called_once()
m.assert_called_with(arg1, arg2)
m.assert_called_once_with(arg1)
m.assert_any_call(arg)
m.assert_not_called()
m.call_count == 3
m.call_args_list == [call(1), call(2)]
```

---

## monkeypatch (pytest built-in)

```python
def test_env(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setattr("module.func", lambda: 42)
    monkeypatch.delattr("module.attr")
    monkeypatch.setitem(config, "key", "value")
    # all automatically undone after test — no cleanup needed
```

---

## Markers

```python
@pytest.mark.skip(reason="not implemented yet")
@pytest.mark.skipif(sys.platform == "win32", reason="linux only")
@pytest.mark.xfail(reason="known bug")
@pytest.mark.xfail(strict=True)         # MUST fail (else error)
@pytest.mark.slow                        # custom marker
@pytest.mark.integration                 # custom marker

# Run only: pytest -m "not slow"
# Register custom markers in pytest.ini:
# [pytest]
# markers =
#     slow: tests that take > 1s
#     integration: require external services
```

---

## Async Testing

```python
import pytest
import pytest_asyncio

@pytest.mark.asyncio
async def test_async_func():
    result = await my_async_function()
    assert result == 42

# AsyncMock
from unittest.mock import AsyncMock, patch

@patch("module.fetch", new_callable=AsyncMock)
async def test_fetch(mock_fetch):
    mock_fetch.return_value = {"data": 1}
    result = await my_service.get_data()
    mock_fetch.assert_awaited_once()
```

---

## Coverage

```bash
pytest --cov=mypackage --cov-report=term-missing --cov-report=html
pytest --cov=mypackage --cov-fail-under=80

# .coveragerc
[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if TYPE_CHECKING:
```

```python
# Skip a line
x = complex_thing()  # pragma: no cover
```

---

## Test Organization

```
project/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       └── orders.py
└── tests/
    ├── conftest.py          ← shared fixtures
    ├── unit/
    │   └── test_orders.py
    ├── integration/
    │   └── test_db.py
    └── e2e/
        └── test_checkout.py

Naming:
  test_<what>_<condition>_<expected>
  test_add_two_positives_returns_sum
  test_withdraw_insufficient_funds_raises_error
```

---

## Test Doubles Taxonomy

```
Dummy    → passed but never used (fill parameter list)
Stub     → returns pre-canned values (no assertions)
Fake     → working but simplified (InMemoryRepository)
Mock     → records calls, verifies behavior (assert_called_with)
Spy      → real object + records calls (wraps=real_object)
```

| Double | Has logic? | Verifies calls? | When to use |
|--------|-----------|-----------------|-------------|
| Dummy  | No | No | Fill unused parameters |
| Stub   | No | No | Return controlled data |
| Fake   | Yes (simplified) | No | Realistic behavior, no I/O |
| Mock   | No | Yes | Verify interactions at boundary |
| Spy    | Yes (real) | Yes | Real + verify side effects |

---

## Testable Design

```python
# Untestable — hardcoded dependencies
class OrderService:
    def __init__(self):
        self._db = MySQLDatabase()     # can't swap!
        self._email = SMTPEmailer()    # can't swap!

# Testable — injected dependencies
class OrderService:
    def __init__(self, db: OrderRepository, emailer: Emailer):
        self._db = db
        self._email = emailer

# Test:
service = OrderService(
    db=InMemoryOrderRepository(),
    emailer=Mock()
)
```

---

## Hypothesis — Property-Based Testing

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sort_length_preserved(lst):
    assert len(sorted(lst)) == len(lst)

@given(st.integers(min_value=1), st.integers(min_value=1))
def test_addition_commutative(a, b):
    assert a + b == b + a

# Common strategies:
st.integers(min_value=0, max_value=100)
st.text(min_size=1)
st.lists(st.integers(), min_size=0, max_size=50)
st.floats(allow_nan=False, allow_infinity=False)
st.one_of(st.none(), st.integers())
st.builds(User, name=st.text(min_size=1), age=st.integers(18, 99))
```

---

## Key Rules

```
1. Patch WHERE IT'S USED, not where it's defined
   # module_under_test.py: from requests import get
   → patch("module_under_test.get")   ✓
   → patch("requests.get")             ✗

2. AAA pattern: Arrange → Act → Assert

3. One assertion per test (logical unit)

4. Tests must be independent (no shared mutable state)

5. Avoid testing implementation — test behavior

6. Deterministic: same input always same output
   → Mock time, randomness, external services

7. Fast: unit tests < 100ms each

8. Coverage is a floor, not a goal
   100% coverage doesn't mean correct code
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| 📝 Practice (35 Qs) | [practice.md](./practice.md) |
| 🧪 pytest Deep Dive | [01_pytest/theory.md](./01_pytest/theory.md) |
| 🔬 unittest Deep Dive | [02_unittest/theory.md](./02_unittest/theory.md) |
| 🎭 Mocking Deep Dive | [03_mocking/theory.md](./03_mocking/theory.md) |
| 🏠 Home | [README.md](../../01_Python_Mastery/README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Interview Q&A](./interview.md)
