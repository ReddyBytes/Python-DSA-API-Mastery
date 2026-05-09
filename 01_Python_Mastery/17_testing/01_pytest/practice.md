# pytest — Practice Questions

15 questions from first test to full CSV parser capstone.

> Navigation: [theory.md](./theory.md) · [practice_local.py](./practice_local.py) · [Root practice](../practice.md)

---

## Quick Index

| # | Concept | Level |
|---|---------|-------|
| [Q1](#q1) | basics — Write and Run a pytest Test Function | 🟢 |
| [Q2](#q2) | assert — Test Multiple Conditions | 🟢 |
| [Q3](#q3) | fixture — setUp Equivalent for a Database | 🟡 |
| [Q4](#q4) | fixture scope — Module-Level Fixture | 🟡 |
| [Q5](#q5) | parametrize — Test a Function with 5 Different Inputs | 🟡 |
| [Q6](#q6) | parametrize ids — Readable Test Names | 🟡 |
| [Q7](#q7) | pytest.raises — Assert an Exception Is Raised | 🟡 |
| [Q8](#q8) | conftest.py — Share a Fixture Across Test Files | 🟡 |
| [Q9](#q9) | skip and xfail — Mark Tests Appropriately | 🟡 |
| [Q10](#q10) | tmp_path — Write and Read Test Files | 🟡 |
| [Q11](#q11) | monkeypatch — Patch os.environ in a Test | 🟡 |
| [Q12](#q12) | pytest-asyncio — Test an Async Function | 🟠 |
| [Q13](#q13) | fixture teardown — yield vs return | 🟠 |
| [Q14](#q14) | parametrize + fixture — Combined | 🟠 |
| [Q15](#q15) | Capstone — Test a CSV Parser with Fixtures and parametrize | 🟠 |

<a id="q1"></a>
### Q1 🟢 · basics — Write and Run a pytest Test Function

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)



**Problem:** Write a function `add(a, b)` that returns the sum of two numbers. Write a pytest test function `test_add` that verifies: `add(2, 3) == 5`, `add(-1, 1) == 0`, and `add(0, 0) == 0`. Run it with `pytest -v`.

<details>
<summary>💡 Hint</summary>

A pytest test is just a Python function whose name starts with `test_`. Use plain `assert` statements — no class or special methods needed.
</details>

<details>
<summary>✅ Answer</summary>

```python
def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
```

**Why:** pytest discovers any function named `test_*` automatically. Plain `assert` gives rich diffs on failure — no need for `assertEqual`.
</details>

---

<a id="q2"></a>
### Q2 🟢 · assert — Test Multiple Conditions

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)



**Problem:** Write `is_palindrome(s)` that returns `True` if `s` (case-insensitive, ignore spaces) is a palindrome. Write `test_palindrome` that checks at least 4 different inputs including at least one False case.

<details>
<summary>💡 Hint</summary>

Lowercase and strip spaces before reversing. Test "racecar", "hello", "A man a plan a canal Panama", and "".
</details>

<details>
<summary>✅ Answer</summary>

```python
def is_palindrome(s):
    s = s.lower().replace(" ", "")
    return s == s[::-1]

def test_palindrome():
    assert is_palindrome("racecar") is True
    assert is_palindrome("hello") is False
    assert is_palindrome("A man a plan a canal Panama") is True
    assert is_palindrome("") is True
    assert is_palindrome("Madam") is True
```

**Why:** Multiple assert statements in one test function are fine when they test the same logical behavior. If you want each to be independently reportable, use `@pytest.mark.parametrize`.
</details>

---

<a id="q3"></a>
### Q3 🟡 · fixture — setUp Equivalent for a Database

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)



**Problem:** Write a pytest fixture `db` that creates an in-memory SQLite database with a `users` table (`id INTEGER, name TEXT`), yields the connection for the test, then closes it. Write two tests that use this fixture: one inserts a user and checks count, one checks the table starts empty.

<details>
<summary>💡 Hint</summary>

Use `yield conn` — code before yield is setup, code after yield is teardown. Import `sqlite3`. The `yield` is what makes teardown possible in pytest fixtures.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pytest
import sqlite3

@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    yield conn           # test runs here
    conn.close()         # teardown — always runs

def test_empty_table(db):
    count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert count == 0

def test_insert_user(db):
    db.execute("INSERT INTO users VALUES (1, 'Alice')")
    db.commit()
    count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert count == 1
```

**Why:** Fixtures replace setUp/tearDown without requiring a class. `yield` puts setup before and teardown after in a single function. Each test gets a fresh connection.
</details>

---

<a id="q4"></a>
### Q4 🟡 · fixture scope — Module-Level Fixture

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)



**Problem:** Write a module-scoped fixture `expensive_user` that creates a `User` dataclass instance with `name="alice smith"`, `email="alice@example.com"`, `age=25`. Write three tests using this fixture that verify: `display_name()` returns `"Alice Smith"`, `is_adult()` returns `True`, and `email` is lowercase.

<details>
<summary>💡 Hint</summary>

Use `@pytest.fixture(scope="module")`. The fixture is created once for all tests in the file. Make sure your tests only read, never mutate, the shared fixture.
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str
    age: int

    def is_adult(self):
        return self.age >= 18

    def display_name(self):
        return self.name.title()

@pytest.fixture(scope="module")
def expensive_user():
    return User("alice smith", "alice@example.com", 25)

def test_display_name(expensive_user):
    assert expensive_user.display_name() == "Alice Smith"

def test_is_adult(expensive_user):
    assert expensive_user.is_adult() is True

def test_email_lowercase(expensive_user):
    assert expensive_user.email == "alice@example.com"
```

**Why:** `scope="module"` creates the fixture once for all tests in the file. Good for read-only data that is expensive to construct. Never use module scope for mutable objects.
</details>

---

<a id="q5"></a>
### Q5 🟡 · parametrize — Test a Function with 5 Different Inputs

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)



**Problem:** Write `celsius_to_fahrenheit(c)`. Use `@pytest.mark.parametrize` to test it with 5 (Celsius, Fahrenheit) pairs: (0, 32), (100, 212), (-40, -40), (37, 98.6), (20, 68).

<details>
<summary>💡 Hint</summary>

Formula: `(c * 9/5) + 32`. Use `pytest.approx` for floating-point pairs. The parametrize decorator takes a string of comma-separated argument names and a list of value tuples.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pytest

def celsius_to_fahrenheit(c):
    return (c * 9 / 5) + 32

@pytest.mark.parametrize("celsius, fahrenheit", [
    (0,    32.0),
    (100,  212.0),
    (-40,  -40.0),
    (37,   pytest.approx(98.6, abs=0.1)),
    (20,   68.0),
])
def test_celsius_to_fahrenheit(celsius, fahrenheit):
    assert celsius_to_fahrenheit(celsius) == fahrenheit
```

**Why:** parametrize runs the same test 5 times with different data. Each is an independent test case — one failure doesn't stop the others. Use `pytest.approx` for float comparisons.
</details>

---

<a id="q6"></a>
### Q6 🟡 · parametrize ids — Readable Test Names

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)



**Problem:** Rewrite Q5 using `pytest.param(..., id="name")` to give each case a readable ID: "freezing", "boiling", "same-in-both", "body-temp", "room-temp".

<details>
<summary>💡 Hint</summary>

Replace plain tuples with `pytest.param(celsius, fahrenheit, id="name")`. The `id` appears in test output and `pytest -k` filtering.
</details>

<details>
<summary>✅ Answer</summary>

```python
@pytest.mark.parametrize("celsius, fahrenheit", [
    pytest.param(0,    32.0,                          id="freezing"),
    pytest.param(100,  212.0,                         id="boiling"),
    pytest.param(-40,  -40.0,                         id="same-in-both"),
    pytest.param(37,   pytest.approx(98.6, abs=0.1),  id="body-temp"),
    pytest.param(20,   68.0,                          id="room-temp"),
])
def test_celsius_to_fahrenheit_named(celsius, fahrenheit):
    assert celsius_to_fahrenheit(celsius) == fahrenheit
```

**Why:** `id` makes test output readable — `test_celsius_to_fahrenheit_named[boiling]` instead of `test_celsius_to_fahrenheit_named[100-212.0]`. Run a specific case with `pytest -k "boiling"`.
</details>

---

<a id="q7"></a>
### Q7 🟡 · pytest.raises — Assert an Exception Is Raised

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)



**Problem:** Write `validate_age(age)` that raises `TypeError` if age is not an int, and `ValueError` if age is outside [0, 150]. Write tests that: (1) verify the happy path, (2) check `TypeError` is raised for a string input, (3) check `ValueError` is raised for -1, and (4) check `ValueError` is raised for 999 with a `match` on the message.

<details>
<summary>💡 Hint</summary>

Use `with pytest.raises(ErrorType):` as a context manager. Add `match="pattern"` to also check the exception message with a regex.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pytest

def validate_age(age):
    if not isinstance(age, int):
        raise TypeError(f"age must be int, got {type(age).__name__}")
    if age < 0 or age > 150:
        raise ValueError(f"age {age} is out of range [0, 150]")
    return True

def test_valid_age():
    assert validate_age(25) is True
    assert validate_age(0) is True
    assert validate_age(150) is True

def test_string_raises_type_error():
    with pytest.raises(TypeError):
        validate_age("25")

def test_negative_raises_value_error():
    with pytest.raises(ValueError):
        validate_age(-1)

def test_out_of_range_message():
    with pytest.raises(ValueError, match="999 is out of range"):
        validate_age(999)
```

**Why:** `pytest.raises` as context manager is the canonical way to test exceptions. The `match` argument accepts a regex pattern and checks it against the exception message.
</details>

---

<a id="q8"></a>
### Q8 🟡 · conftest.py — Share a Fixture Across Test Files

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)



**Problem:** Describe (in code + explanation) how you would share a `db` fixture between `tests/test_users.py` and `tests/test_orders.py` without importing it in each file.

<details>
<summary>💡 Hint</summary>

Create a `conftest.py` file in the `tests/` directory. Fixtures defined there are automatically available to all test files in that directory and subdirectories.
</details>

<details>
<summary>✅ Answer</summary>

```python
# tests/conftest.py  ← no import needed in test files
import pytest
import sqlite3

@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    conn.execute("CREATE TABLE orders (id INTEGER, user_id INTEGER)")
    yield conn
    conn.close()


# tests/test_users.py
def test_user_count(db):          # db injected from conftest.py
    count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert count == 0


# tests/test_orders.py
def test_order_count(db):         # same fixture, no import
    count = db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    assert count == 0
```

**Why:** `conftest.py` is pytest's mechanism for sharing fixtures. It's discovered automatically by pytest — no import needed. You can have multiple `conftest.py` files at different directory levels; the fixture closest to the test file wins.
</details>

---

<a id="q9"></a>
### Q9 🟡 · skip and xfail — Mark Tests Appropriately

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)



**Problem:** Write three tests: (1) a test marked `@pytest.mark.skip` with a reason, (2) a test marked `@pytest.mark.xfail` for a known bug, (3) a test marked with `skipif` that skips on Windows. Show the correct output description for each.

<details>
<summary>💡 Hint</summary>

`skip` — never runs. `xfail` — runs but expected to fail (shown as `x`, not error). `skipif` — conditional skip. `strict=True` on xfail means "MUST fail; if it passes, that's an error".
</details>

<details>
<summary>✅ Answer</summary>

```python
import sys
import pytest

@pytest.mark.skip(reason="PDF export not yet implemented")
def test_export_to_pdf():
    assert False                          # never runs — shown as 's'

@pytest.mark.xfail(reason="Known bug: issue #42 — rounding error")
def test_compound_interest_precision():
    assert 0.1 + 0.2 == 0.3              # expected to fail — shown as 'x', not 'F'

@pytest.mark.skipif(sys.platform == "win32", reason="Uses POSIX paths")
def test_unix_config_path():
    import os
    assert os.path.exists("/etc")         # skipped on Windows, runs on Linux/Mac
```

**Why:** `skip` is for incomplete/irrelevant tests. `xfail` is for known failures — it communicates "this is a known issue, not a regression." `skipif` is conditional. Use `xfail` instead of commenting out tests so broken code is visible.
</details>

---

<a id="q10"></a>
### Q10 🟡 · tmp_path — Write and Read Test Files

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)



**Problem:** Write `read_config(path)` that reads a `KEY=VALUE` config file (one per line, skip `#` comments) and returns a dict. Use the built-in `tmp_path` fixture to write a temp config file and test that the function parses it correctly.

<details>
<summary>💡 Hint</summary>

`tmp_path` is a pytest built-in fixture that provides a unique temporary directory per test. Use `(tmp_path / "filename.cfg").write_text("content")` to create the file.
</details>

<details>
<summary>✅ Answer</summary>

```python
def read_config(path):
    config = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                config[k.strip()] = v.strip()
    return config

def test_read_config(tmp_path):
    config_file = tmp_path / "config.cfg"
    config_file.write_text("HOST=localhost\nPORT=5432\n# comment\nDB=mydb\n")

    result = read_config(str(config_file))

    assert result["HOST"] == "localhost"
    assert result["PORT"] == "5432"
    assert result["DB"] == "mydb"
    assert "#" not in result             # comments excluded

def test_empty_config(tmp_path):
    config_file = tmp_path / "empty.cfg"
    config_file.write_text("")
    assert read_config(str(config_file)) == {}
```

**Why:** `tmp_path` creates an isolated temp directory per test — no cleanup needed, no collisions between tests. It's the standard pytest fixture for file I/O tests.
</details>

---

<a id="q11"></a>
### Q11 🟡 · monkeypatch — Patch os.environ in a Test

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)



**Problem:** Write `get_api_key()` that reads `os.environ["API_KEY"]` and raises `EnvironmentError` if missing. Use `monkeypatch.setenv` to test the happy path and test the error path (with the env var absent).

<details>
<summary>💡 Hint</summary>

`monkeypatch.setenv("KEY", "value")` adds/overrides the env var for the duration of the test. All patches are auto-undone. To test the missing key, use `monkeypatch.delenv("API_KEY", raising=False)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import os

def get_api_key():
    key = os.environ.get("API_KEY")
    if not key:
        raise EnvironmentError("API_KEY environment variable not set")
    return key

def test_api_key_present(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key-abc123")
    assert get_api_key() == "test-key-abc123"

def test_api_key_missing(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)  # remove if exists
    with pytest.raises(EnvironmentError, match="not set"):
        get_api_key()
```

**Why:** `monkeypatch` is pytest's built-in alternative to `patch.dict`. All patches are automatically undone after the test — no cleanup needed. `raising=False` means "don't error if the key wasn't set to begin with."
</details>

---

<a id="q12"></a>
### Q12 🟠 · pytest-asyncio — Test an Async Function

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)



**Problem:** Write `async def fetch_user(repo, user_id)` that calls `await repo.find_user(user_id)` and returns the result. Write an async test using `pytest-asyncio` and `AsyncMock` to verify the function calls `repo.find_user` with the correct id and returns the expected data.

<details>
<summary>💡 Hint</summary>

`pip install pytest-asyncio`. Mark the test with `@pytest.mark.asyncio`. Use `from unittest.mock import AsyncMock`. For awaitable mocks, use `assert_awaited_once_with` not `assert_called_once_with`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pytest
from unittest.mock import AsyncMock

async def fetch_user(repo, user_id):
    return await repo.find_user(user_id)

@pytest.mark.asyncio
async def test_fetch_user():
    mock_repo = AsyncMock()
    mock_repo.find_user.return_value = {"id": 1, "name": "Alice"}

    result = await fetch_user(mock_repo, 1)

    assert result["name"] == "Alice"
    mock_repo.find_user.assert_awaited_once_with(1)  # ← awaited, not called
```

**Why:** `AsyncMock` creates a mock that returns a coroutine when called — so it can be awaited. Use `assert_awaited_once_with` to verify async calls (not `assert_called_once_with`).
</details>

---

<a id="q13"></a>
### Q13 🟠 · fixture teardown — yield vs return

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)



**Problem:** Write a fixture `managed_file` that creates a temp file (using `tempfile`), writes "initial content", yields the file path, then deletes the file. Write a test that appends to the file and verifies content. Show that teardown runs even if the test fails.

<details>
<summary>💡 Hint</summary>

Use `tempfile.mkstemp()` or `tmp_path`. Code after `yield` in a fixture runs as teardown — always, even if the test raises an exception. Use a try/finally pattern if teardown must be guaranteed.
</details>

<details>
<summary>✅ Answer</summary>

```python
import os
import tempfile
import pytest

@pytest.fixture
def managed_file():
    fd, path = tempfile.mkstemp(suffix=".txt")
    os.close(fd)
    with open(path, "w") as f:
        f.write("initial content\n")
    yield path              # test runs HERE
    os.remove(path)         # teardown — runs even if test fails

def test_append_to_managed_file(managed_file):
    with open(managed_file, "a") as f:
        f.write("appended line\n")

    with open(managed_file) as f:
        lines = f.readlines()

    assert len(lines) == 2
    assert "appended line" in lines[1]
```

**Why:** `yield` in a fixture is the pattern for combining setup and teardown. Everything before `yield` is setup, everything after is teardown. The teardown code runs even if the test fails or raises — equivalent to a `finally` block.
</details>

---

<a id="q14"></a>
### Q14 🟠 · parametrize + fixture — Combined

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)



**Problem:** Write a `BankAccount` class with `deposit(amount)` and `balance` property. Create a fixture `empty_account` and a parametrized test that uses both — testing that valid deposit amounts (1, 50, 999.99, 1000) set the balance correctly, and invalid amounts (0, -1, -100) raise `ValueError`.

<details>
<summary>💡 Hint</summary>

Use `@pytest.mark.parametrize` on the test function alongside a fixture parameter. pytest will call the fixture fresh for each parametrized case.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pytest

class BankAccount:
    def __init__(self):
        self._balance = 0.0

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError(f"Deposit amount must be positive, got {amount}")
        self._balance += amount

@pytest.fixture
def empty_account():
    return BankAccount()

@pytest.mark.parametrize("amount", [1, 50, 999.99, 1000])
def test_valid_deposit(empty_account, amount):
    empty_account.deposit(amount)
    assert empty_account.balance == pytest.approx(amount)

@pytest.mark.parametrize("amount", [0, -1, -100])
def test_invalid_deposit_raises(empty_account, amount):
    with pytest.raises(ValueError):
        empty_account.deposit(amount)
```

**Why:** When a test function has both a fixture parameter and `@pytest.mark.parametrize`, pytest creates one test instance for each parametrize value, each with a fresh fixture. The fixture is called once per parametrized case (with function scope).
</details>

---

<a id="q15"></a>
### Q15 🟠 · Capstone — Test a CSV Parser with Fixtures and parametrize

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)



**Problem:** Write `parse_csv(path)` that reads a CSV file and returns a list of dicts (using the header row as keys). Write:
- A fixture `csv_file(tmp_path)` that creates a temp CSV with 3 data rows.
- A test using that fixture that checks row count and field values.
- A parametrized test that checks `parse_csv` handles: a file with no data rows (header only), a file with one row, a file with 5 rows.

<details>
<summary>💡 Hint</summary>

Use `csv.DictReader`. The fixture can depend on `tmp_path` (a built-in fixture). For the parametrized test, write a helper that creates a CSV with N data rows using `tmp_path`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import csv
import pytest

def parse_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

@pytest.fixture
def csv_file(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\nCharlie,35,Chicago\n")
    return path

def test_parse_csv_row_count(csv_file):
    rows = parse_csv(str(csv_file))
    assert len(rows) == 3

def test_parse_csv_field_values(csv_file):
    rows = parse_csv(str(csv_file))
    assert rows[0]["name"] == "Alice"
    assert rows[0]["age"] == "30"       # CSV values are always strings
    assert rows[1]["city"] == "LA"

@pytest.mark.parametrize("n_rows", [0, 1, 5])
def test_parse_csv_various_sizes(tmp_path, n_rows):
    path = tmp_path / "data.csv"
    lines = ["name,value"] + [f"item{i},{i}" for i in range(n_rows)]
    path.write_text("\n".join(lines) + "\n")

    rows = parse_csv(str(path))
    assert len(rows) == n_rows
```

**Why:** Fixtures can depend on other fixtures (including built-ins like `tmp_path`). Combining a fixture with `parametrize` lets you vary the data while keeping setup logic in one place.
</details>

---

## Navigation

| | |
|---|---|
| Deep dive | [theory.md](./theory.md) |
| Local practice | [practice_local.py](./practice_local.py) |
| Root practice (35 Qs) | [../practice.md](../practice.md) |
| Sibling: unittest | [../02_unittest/practice.md](../02_unittest/practice.md) |
| Sibling: mocking | [../03_mocking/practice.md](../03_mocking/practice.md) |

**[Back to README](../../README.md)**
