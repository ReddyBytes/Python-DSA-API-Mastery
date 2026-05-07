# Mocking — Deep Dive

A flight simulator doesn't fly a real plane — it tests the pilot's reactions using a controlled replica. Mocking does the same for code: it replaces the external world (databases, APIs, email servers) with a controllable fake so you can test your logic without the real plane ever leaving the hangar.

---

## Learning Priority

**Must Learn** — daily use, interview essential:
`Mock` · `MagicMock` · `patch` (decorator form) · `assert_called_once_with` · `return_value`

**Should Learn** — important for real projects:
`side_effect` · `patch.object` · `spec` · `call_args_list`

**Good to Know** — useful in specific situations:
`patch.dict` · `AsyncMock` · MagicMock vs Mock differences

**Reference** — know it exists, look up when needed:
`create_autospec` · `PropertyMock` · patching multiple targets · `wraps`

---

## 1. Why Mock?

Your production code talks to things you can't control in tests:

```
External API   → slow, costs money, can be down
Database       → requires setup, modifies real data
File system    → leaves debris, platform-dependent
Time/random    → non-deterministic → flaky tests
Email/SMS      → sends real messages to real people!
```

**The contract:** mock at system boundaries (external I/O). Never mock your own business logic.

```python
# Without mock: test hits real API
def test_get_weather():
    result = fetch_weather("London")   # real HTTP call — slow, flaky, costs money
    assert result["temp"] > -50

# With mock: test the logic around the HTTP call
@patch("mymodule.requests.get")
def test_get_weather(mock_get):
    mock_get.return_value.json.return_value = {"temp": 22, "condition": "sunny"}
    mock_get.return_value.raise_for_status.return_value = None

    result = fetch_weather("London")

    assert result["temp"] == 22
    mock_get.assert_called_once_with("https://api.example.com/weather/London")
```

---

## 2. Mock and MagicMock — What's the Difference?

**`Mock`** is the base class. It accepts any attribute access and any method call without raising. It records everything.

**`MagicMock`** is a subclass of `Mock` that also implements Python's **dunder methods** (`__len__`, `__iter__`, `__enter__`, `__getitem__`, etc.).

```python
from unittest.mock import Mock, MagicMock

# Mock does NOT support dunder methods
plain = Mock()
len(plain)    # TypeError: object of type 'Mock' has no len()

# MagicMock does
magic = MagicMock()
len(magic)    # 0 by default — no error
magic[0]      # MagicMock() — __getitem__ implemented
list(magic)   # [] — __iter__ implemented

with magic:   # __enter__ and __exit__ implemented
    pass
```

**When to use which:**
- Use `MagicMock` for most cases — it works as a context manager, iterable, container
- Use `Mock` when you want explicit control and want an error if dunder methods are accidentally called

In practice, `MagicMock` is the default and is what `patch` creates by default.

---

## 3. patch — Decorator, Context Manager, Manual

**`patch`** temporarily replaces a name in a module with a `MagicMock`. The original is restored automatically.

**CRITICAL RULE: patch WHERE the name is USED, not where it's defined.**

```python
# In mymodule.py:
#   import requests         → use patch("mymodule.requests.get")
#   from requests import get → use patch("mymodule.get")

# WRONG — patches the original, not the imported copy
@patch("requests.get")

# RIGHT — patches the name as it exists in the module under test
@patch("mymodule.requests.get")
```

**Decorator form — most common:**

```python
from unittest.mock import patch, Mock
import pytest

@patch("mocking_examples.requests.get")
def test_fetch_weather(mock_get):
    # Arrange
    mock_response = Mock()
    mock_response.json.return_value = {"temp": 22}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Act
    result = fetch_weather("London")

    # Assert
    mock_get.assert_called_once_with("https://api.example.com/weather/London")
    assert result["temp"] == 22
```

Note: when stacking multiple `@patch` decorators, they apply bottom-up and inject top-down:

```python
@patch("module.ClassA")    # injected second → mock_a
@patch("module.ClassB")    # injected first  → mock_b
def test_multi(mock_b, mock_a):
    ...
```

**Context manager form:**

```python
def test_load_config():
    config_data = {"db_host": "localhost"}
    with patch("builtins.open", mock_open(read_data=json.dumps(config_data))):
        result = load_app_config()
    assert result["db_host"] == "localhost"
```

---

## 4. patch.object — Patch a Method on a Class or Instance

`patch.object` patches a specific attribute on an existing object or class, instead of a module-level name.

```python
from unittest.mock import patch

counter = Counter(10)

# Patch an instance method:
with patch.object(counter, "reset") as mock_reset:
    counter.reset()
    mock_reset.assert_called_once()

# After the context, real reset is restored:
counter.reset()
assert counter.value == 0


# Patch a class method (affects all instances):
with patch.object(Counter, "increment", return_value=42) as mock_inc:
    c = Counter()
    result = c.increment()
    assert result == 42
    mock_inc.assert_called_once()


# Patch datetime.now to control time:
from datetime import datetime

fixed_time = datetime(2024, 1, 15, 12, 0, 0)
with patch("mymodule.datetime") as mock_dt:
    mock_dt.now.return_value = fixed_time
    year = get_current_year()
assert year == 2024
```

---

## 5. side_effect — Raise Exceptions, Return Sequences, Call Real Function

`side_effect` replaces the return behavior of a mock with something dynamic.

**Raise an exception:**

```python
m = Mock()
m.connect.side_effect = ConnectionError("server down")

with pytest.raises(ConnectionError, match="server down"):
    m.connect()
```

**Return different values on successive calls:**

```python
m = Mock()
m.get_id.side_effect = [1, 2, 3]   # ← list: returns next item each call

assert m.get_id() == 1
assert m.get_id() == 2
assert m.get_id() == 3
# m.get_id() → StopIteration
```

**Call a function with the arguments (side effect as callable):**

```python
m = Mock()
m.double.side_effect = lambda x: x * 2   # ← function: processes real args

assert m.double(5) == 10
assert m.double(3) == 6
```

**Mixed: return None for some users, data for others:**

```python
def fake_find_user(uid):
    users = {
        1: {"name": "Alice", "email": "a@ex.com"},
        2: None,   # not found
        3: {"name": "Charlie", "email": "c@ex.com"},
    }
    return users.get(uid)

mock_repo.find_by_id.side_effect = fake_find_user
```

---

## 6. return_value — Control What Mock Returns

`return_value` is the value returned when the mock is called. For chained calls, set `return_value` on the chain.

```python
m = Mock()
m.fetch.return_value = {"id": 1, "name": "Alice"}

result = m.fetch(user_id=1)
assert result["name"] == "Alice"
```

**Chained calls — common with `requests`:**

```python
mock_get = Mock()
mock_get.return_value.json.return_value = {"temp": 22}
mock_get.return_value.raise_for_status.return_value = None

# When code does:
#   response = requests.get(url)   → mock_get() → mock_get.return_value
#   data = response.json()         → mock_get.return_value.json()
#   response.raise_for_status()    → mock_get.return_value.raise_for_status()
```

---

## 7. assert_called_once_with, assert_called_with, call_args

Mock records every call. You can assert on the exact arguments used.

```python
from unittest.mock import Mock, call

m = Mock()

# First call
m.method("a", key="b")
m.method.assert_called()                    # was called at all
m.method.assert_called_once()              # was called exactly once
m.method.assert_called_with("a", key="b") # last call had these args
m.method.assert_called_once_with("a", key="b")  # called once with exactly these args

# Second call
m.method("c")
m.method.assert_any_call("a", key="b")    # was called with these args at some point
m.method.assert_any_call("c")
assert m.method.call_count == 2

# Full call history:
assert m.method.call_args_list == [
    call("a", key="b"),
    call("c"),
]

# Assert never called:
m.other.assert_not_called()

# Reset call history:
m.method.reset_mock()
m.method.assert_not_called()
```

**`ANY` — match any value in an assertion:**

```python
from unittest.mock import ANY

m.log(42, "random message", timestamp=datetime.now())
m.log.assert_called_once_with(42, ANY, timestamp=ANY)  # ignore specific values
```

---

## 8. spec — Mock That Respects the Real Interface

A plain `Mock` accepts any attribute or method call — even typos. `spec` restricts the mock to the real class's interface.

```python
from unittest.mock import Mock, create_autospec

class UserRepository:
    def find_by_id(self, user_id: int) -> dict: ...
    def save(self, user: dict) -> dict: ...
    def count(self) -> int: ...


# Without spec — typos silently succeed
m = Mock()
m.fidn_by_id(1)   # typo! returns a Mock instead of raising — you'd never notice

# With spec — typos raise AttributeError
m = Mock(spec=UserRepository)
m.find_by_id(1)       # correct method — works
m.fidn_by_id(1)       # AttributeError: Mock object has no attribute 'fidn_by_id'


# create_autospec also checks method signatures:
m = create_autospec(UserRepository, instance=True)
m.find_by_id(user_id=1)     # correct
m.find_by_id(1, 2)          # TypeError: too many positional arguments
```

Use `spec` for injected dependencies — it catches refactoring drift early.

---

## 9. patch.dict — Mock os.environ and Config Dicts

`patch.dict` replaces values in a dictionary for the duration of the test, then restores the original.

```python
import os
from unittest.mock import patch

def test_env_override():
    with patch.dict(os.environ, {"API_KEY": "test-key-123"}):
        assert os.environ["API_KEY"] == "test-key-123"

    # Restored after context:
    assert "API_KEY" not in os.environ   # (assuming it wasn't set before)


# clear=True — replace entire dict, not just override
with patch.dict(os.environ, {"ONLY_THIS": "value"}, clear=True):
    assert list(os.environ.keys()) == ["ONLY_THIS"]


# Also works for config dicts:
config = {"debug": False, "db_host": "prod.db.example.com"}

with patch.dict(config, {"debug": True, "db_host": "localhost"}):
    assert config["debug"] is True
    assert config["db_host"] == "localhost"

assert config["db_host"] == "prod.db.example.com"  # restored
```

---

## 10. Common Mistakes

**1. Patching the wrong target — most common mocking mistake:**

```python
# mymodule.py
from os.path import exists

def file_exists(path):
    return exists(path)

# WRONG — patches the original, but mymodule.file_exists already holds a reference
@patch("os.path.exists")

# RIGHT — patch where the name lives in the module under test
@patch("mymodule.exists")
```

**2. Mock assertion order — `assert_called_with` checks the LAST call, not all calls:**

```python
m.method("a")
m.method("b")
m.method.assert_called_with("a")   # FAILS — last call was "b"

# RIGHT for checking any call:
m.method.assert_any_call("a")

# RIGHT for checking all calls in order:
assert m.method.call_args_list == [call("a"), call("b")]
```

**3. Not resetting mocks between tests:**

```python
# In setup_method:
self.mock_service = Mock()

# Tests share the same mock — call history accumulates
# Use setup_method or fixtures to create fresh mocks per test
```

**4. Over-mocking — mocking things that shouldn't be mocked:**

```python
# WRONG: you end up testing the mock, not the code
def test_process():
    mock_validator = Mock(return_value=True)
    mock_transformer = Mock(return_value={"clean": True})
    result = process(mock_validator, mock_transformer)
    assert result == {"clean": True}   # this always passes regardless of process logic

# RIGHT: only mock external I/O
def test_process(db):
    result = process(real_validator, real_transformer, db=db)
    assert result["status"] == "ok"
```

**5. Not using `spec` — silent typos in mock method names:**

Spend 30 seconds adding `spec=RealClass` to important mocks. It catches refactoring breakage immediately.

---

## Navigation

| | |
|---|---|
| Back to root | [17_testing/theory.md](../theory.md) |
| Practice questions | [practice.md](./practice.md) |
| Local practice | [practice_local.py](./practice_local.py) |
| Sibling: pytest | [../01_pytest/theory.md](../01_pytest/theory.md) |
| Sibling: unittest | [../02_unittest/theory.md](../02_unittest/theory.md) |

**[Back to README](../../README.md)**
