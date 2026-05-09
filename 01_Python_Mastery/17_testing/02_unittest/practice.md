# unittest — Practice Questions

10 questions from basic TestCase to full Stack capstone.

> Navigation: [theory.md](./theory.md) · [practice_local.py](./practice_local.py) · [Root practice](../practice.md)

---

## Quick Index

| # | Concept | Level |
|---|---------|-------|
| [Q1](#q1) | basics — Write a TestCase with assertEqual | 🟢 |
| [Q2](#q2) | setUp/tearDown — File-Based Test | 🟡 |
| [Q3](#q3) | assertRaises — Context Manager Form | 🟡 |
| [Q4](#q4) | assertions — assertIn, assertIsNone, assertAlmostEqual | 🟡 |
| [Q5](#q5) | setUpClass — Shared Expensive Resource | 🟡 |
| [Q6](#q6) | skip and expectedFailure | 🟡 |
| [Q7](#q7) | subTest — Loop Without Stopping on First Failure | 🟡 |
| [Q8](#q8) | test suite — Run a Specific Subset of Tests | 🟠 |
| [Q9](#q9) | migration — Rewrite a unittest TestCase as pytest | 🟠 |
| [Q10](#q10) | Capstone — Full TestCase for a Stack Data Structure | 🟠 |

<a id="q1"></a>
### Q1 🟢 · basics — Write a TestCase with assertEqual

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

**Problem:** Write a `TemperatureConverter` class with a static method `celsius_to_fahrenheit(c)`. Write a `unittest.TestCase` subclass with three test methods: freezing point (0°C = 32°F), boiling point (100°C = 212°F), and body temperature (37°C ≈ 98.6°F).

<details>
<summary>💡 Hint</summary>

Inherit from `unittest.TestCase`. Every test method starts with `test_`. Use `assertEqual` for exact values and `assertAlmostEqual` for floating point comparisons.
</details>

<details>
<summary>✅ Answer</summary>

```python
import unittest

class TemperatureConverter:
    @staticmethod
    def celsius_to_fahrenheit(c):
        return (c * 9 / 5) + 32

class TestTemperatureConverter(unittest.TestCase):

    def test_freezing_point(self):
        self.assertEqual(TemperatureConverter.celsius_to_fahrenheit(0), 32.0)

    def test_boiling_point(self):
        self.assertEqual(TemperatureConverter.celsius_to_fahrenheit(100), 212.0)

    def test_body_temperature(self):
        result = TemperatureConverter.celsius_to_fahrenheit(37)
        self.assertAlmostEqual(result, 98.6, places=1)   # ← float equality


if __name__ == "__main__":
    unittest.main()
```

**Why:** `assertEqual` is the most common assertion — it checks `a == b` and shows both values on failure. `assertAlmostEqual` handles floating point by rounding to `places` decimal places before comparing.
</details>

---

<a id="q2"></a>
### Q2 🟡 · setUp/tearDown — File-Based Test

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

**Problem:** Write a `TestCase` with `setUp` that creates a temp file and writes "line one\nline two\n" to it, and `tearDown` that deletes the file. Write two test methods: one checks that `count_lines(path)` returns 2, another checks that appending a line makes it 3.

<details>
<summary>💡 Hint</summary>

Use `tempfile.mkstemp()` in `setUp`. Store the path as `self.temp_path`. In `tearDown`, call `os.remove(self.temp_path)`. `tearDown` runs even if the test fails.
</details>

<details>
<summary>✅ Answer</summary>

```python
import unittest
import tempfile
import os

def count_lines(path):
    with open(path) as f:
        return sum(1 for line in f if line.strip())

class TestFileOperations(unittest.TestCase):

    def setUp(self):
        fd, self.temp_path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        with open(self.temp_path, "w") as f:
            f.write("line one\nline two\n")

    def tearDown(self):
        os.remove(self.temp_path)   # always runs, even if test fails

    def test_initial_line_count(self):
        self.assertEqual(count_lines(self.temp_path), 2)

    def test_appended_line_count(self):
        with open(self.temp_path, "a") as f:
            f.write("line three\n")
        self.assertEqual(count_lines(self.temp_path), 3)
```

**Why:** `setUp`/`tearDown` guarantee fresh state per test. `tearDown` runs even when a test fails — essential for cleanup. Each test gets its own temp file.
</details>

---

<a id="q3"></a>
### Q3 🟡 · assertRaises — Context Manager Form

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

**Problem:** Write `validate_grade(grade)` that raises `ValueError` if grade is outside [0, 100]. Write a `TestCase` with four tests: valid grade (85) passes, grade -1 raises `ValueError`, grade 101 raises `ValueError`, and the error message for -1 contains "out of range" (use `assertRaisesRegex`).

<details>
<summary>💡 Hint</summary>

Use `with self.assertRaises(ValueError):` for testing that an exception is raised. Use `self.assertRaisesRegex(ValueError, "pattern")` to also match the message.
</details>

<details>
<summary>✅ Answer</summary>

```python
import unittest

def validate_grade(grade):
    if not (0 <= grade <= 100):
        raise ValueError(f"Grade {grade} is out of range [0, 100]")
    return True

class TestValidateGrade(unittest.TestCase):

    def test_valid_grade(self):
        self.assertTrue(validate_grade(85))

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            validate_grade(-1)

    def test_over_100_raises(self):
        with self.assertRaises(ValueError):
            validate_grade(101)

    def test_error_message(self):
        with self.assertRaisesRegex(ValueError, "out of range"):
            validate_grade(-1)
```

**Why:** `assertRaises` as a context manager is cleaner than try/except. `assertRaisesRegex` combines exception type and message check in one assertion — equivalent to `pytest.raises(Exc, match="pattern")`.
</details>

---

<a id="q4"></a>
### Q4 🟡 · assertions — assertIn, assertIsNone, assertAlmostEqual

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

**Problem:** Write a `TestCase` that demonstrates `assertIn`, `assertNotIn`, `assertIsNone`, `assertIsNotNone`, `assertAlmostEqual`, and `assertIsInstance` using simple data structures and computations.

<details>
<summary>💡 Hint</summary>

`assertIn(a, b)` checks `a in b`. `assertIsNone(x)` checks `x is None`. `assertAlmostEqual(a, b, places=N)` rounds to N decimal places. All these generate clearer error messages than plain `assert`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import unittest

class TestAssertions(unittest.TestCase):

    def test_membership(self):
        permissions = ["read", "write", "execute"]
        self.assertIn("read", permissions)
        self.assertNotIn("delete", permissions)

    def test_none_checks(self):
        result = {"a": 1}.get("missing_key")     # returns None
        self.assertIsNone(result)
        self.assertIsNotNone({"a": 1}.get("a"))

    def test_float_equality(self):
        self.assertAlmostEqual(1/3, 0.3333, places=4)
        self.assertAlmostEqual(0.1 + 0.2, 0.3, places=10)

    def test_type_check(self):
        self.assertIsInstance(42, int)
        self.assertIsInstance("hello", str)
        self.assertIsInstance([1, 2], (list, tuple))   # either type
```

**Why:** Named assertion methods provide targeted error messages. `assertAlmostEqual` solves the floating-point equality problem by rounding before comparing. `assertIsInstance` checks both exact type and subclasses.
</details>

---

<a id="q5"></a>
### Q5 🟡 · setUpClass — Shared Expensive Resource

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

**Problem:** Simulate an "expensive" database setup (a dict-based FakeDatabase that takes time to populate). Write a `TestCase` that uses `setUpClass` to create it once and `tearDownClass` to destroy it. Write three tests that read from the shared database without modifying it.

<details>
<summary>💡 Hint</summary>

`setUpClass` must be decorated with `@classmethod` and takes `cls` as its first parameter. Use `cls.attribute` to store shared data. Tests access it as `self.attribute`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import unittest

class FakeDatabase:
    def __init__(self, data):
        self._data = data

    def find(self, key):
        return self._data.get(key)

    def count(self):
        return len(self._data)

class TestSharedDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Runs ONCE. Simulates expensive DB initialization."""
        cls.db = FakeDatabase({
            "user:1": {"name": "Alice", "role": "admin"},
            "user:2": {"name": "Bob",   "role": "user"},
            "user:3": {"name": "Charlie","role": "user"},
        })

    @classmethod
    def tearDownClass(cls):
        cls.db = None

    def test_find_alice(self):
        user = self.db.find("user:1")
        self.assertEqual(user["name"], "Alice")

    def test_admin_role(self):
        user = self.db.find("user:1")
        self.assertEqual(user["role"], "admin")

    def test_user_count(self):
        self.assertEqual(self.db.count(), 3)
```

**Why:** `setUpClass` creates the expensive resource once for the entire class. All three tests share the same `cls.db` instance. This is ideal for read-only shared data — never for mutable objects that tests modify.
</details>

---

<a id="q6"></a>
### Q6 🟡 · skip and expectedFailure

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

**Problem:** Write a `TestCase` that demonstrates: `@unittest.skip("reason")`, `@unittest.skipIf(condition, reason)`, `@unittest.skipUnless(condition, reason)`, and `@unittest.expectedFailure`. Include a comment explaining when each is appropriate.

<details>
<summary>💡 Hint</summary>

`skip` — unconditional, use when feature is unimplemented. `skipIf` — skip when condition is True. `skipUnless` — only run when condition is True. `expectedFailure` — known broken, tracked until fixed.
</details>

<details>
<summary>✅ Answer</summary>

```python
import sys
import unittest

class TestSkippingExamples(unittest.TestCase):

    @unittest.skip("PDF export not yet implemented — Sprint 7")
    def test_export_to_pdf(self):
        # Unconditional skip — shown as 's' in output
        self.fail("should never run")

    @unittest.skipIf(sys.platform == "win32", "Uses POSIX paths — not valid on Windows")
    def test_unix_config_path(self):
        # Runs on Linux/Mac, skipped on Windows
        import os
        self.assertTrue(os.path.exists("/etc"))

    @unittest.skipUnless(sys.version_info >= (3, 10), "Requires Python 3.10+ match statement")
    def test_pattern_matching(self):
        # Only runs on Python 3.10+
        x = 5
        match x:
            case 5:
                result = "five"
        self.assertEqual(result, "five")

    @unittest.expectedFailure
    def test_known_float_bug(self):
        # Known issue: will be fixed when we upgrade the rounding library
        self.assertEqual(0.1 + 0.2, 0.3)   # fails as expected — shown as 'x'
```

**Why:** Use `expectedFailure` instead of commenting out tests — it documents known failures and alerts you if they're accidentally fixed (shown as 'u' for unexpected success).
</details>

---

<a id="q7"></a>
### Q7 🟡 · subTest — Loop Without Stopping on First Failure

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

**Problem:** Write a `TestCase` that tests `celsius_to_fahrenheit` with 5 cases using `subTest`. Show that if one case fails, the others still run. Compare what happens without `subTest`.

<details>
<summary>💡 Hint</summary>

Use `with self.subTest(label=label, celsius=celsius):` inside a loop. Each `subTest` is treated as an independent test case in output — all failures are reported.
</details>

<details>
<summary>✅ Answer</summary>

```python
import unittest

def celsius_to_fahrenheit(c):
    return (c * 9 / 5) + 32

class TestWithSubtests(unittest.TestCase):

    def test_temperature_conversions(self):
        cases = [
            (0,    32.0,  "freezing"),
            (100,  212.0, "boiling"),
            (37,   98.6,  "body-temp"),
            (-40,  -40.0, "same-in-both"),
            (20,   68.0,  "room-temp"),
        ]
        for celsius, expected_f, label in cases:
            with self.subTest(label=label, celsius=celsius):  # ← key
                result = celsius_to_fahrenheit(celsius)
                self.assertAlmostEqual(result, expected_f, places=1)

    # Without subTest: loop would stop at first failure
    # With subTest: all 5 cases run, all failures reported separately
```

**Why:** `subTest` is unittest's equivalent of `@pytest.mark.parametrize` for looped cases. Without it, a failing case stops the loop — you only see the first failure. With `subTest`, each case is independent.
</details>

---

<a id="q8"></a>
### Q8 🟠 · test suite — Run a Specific Subset of Tests

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

**Problem:** Write two `TestCase` classes (`TestMath` and `TestString`). Write a `suite()` function that builds a `TestSuite` with: all tests from `TestMath`, and only one specific test from `TestString`. Run it programmatically with `TextTestRunner`.

<details>
<summary>💡 Hint</summary>

Use `unittest.TestSuite()`. Add all tests from a class with `unittest.TestLoader().loadTestsFromTestCase(TestClass)`. Add a single test with `suite.addTest(TestClass("method_name"))`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import unittest

class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(1 + 1, 2)
    def test_multiply(self):
        self.assertEqual(3 * 4, 12)

class TestString(unittest.TestCase):
    def test_upper(self):
        self.assertEqual("hello".upper(), "HELLO")
    def test_lower(self):
        self.assertEqual("HELLO".lower(), "hello")
    def test_strip(self):
        self.assertEqual("  hi  ".strip(), "hi")

def suite():
    s = unittest.TestSuite()
    # All tests from TestMath:
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMath))
    # Only one specific test from TestString:
    s.addTest(TestString("test_upper"))
    return s

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())
    # Runs: test_add, test_multiply, test_upper (NOT test_lower or test_strip)
```

**Why:** Manual test suites let you run specific subsets for CI stages (smoke tests) or when tests have different requirements (needs-DB, needs-network). In pytest you'd use markers (`-m smoke`) instead.
</details>

---

<a id="q9"></a>
### Q9 🟠 · migration — Rewrite a unittest TestCase as pytest

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

**Problem:** Given this `unittest.TestCase` class, rewrite it as pytest-style tests (no class required). Preserve all test logic; replace `assertEqual` with `assert`, `assertRaises` with `pytest.raises`, and `setUp` with a pytest fixture.

```python
class TestStack(unittest.TestCase):
    def setUp(self):
        self.stack = Stack(capacity=3)

    def test_empty_stack(self):
        self.assertTrue(self.stack.is_empty())
        self.assertEqual(self.stack.size(), 0)

    def test_pop_empty_raises(self):
        with self.assertRaises(IndexError):
            self.stack.pop()
```

<details>
<summary>💡 Hint</summary>

Replace `self.setUp` with `@pytest.fixture`. Replace `self.assertTrue(x)` with `assert x`. Replace `with self.assertRaises(E):` with `with pytest.raises(E):`. Drop the class.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pytest

@pytest.fixture
def stack():
    return Stack(capacity=3)   # fresh stack per test — equivalent to setUp

def test_empty_stack(stack):
    assert stack.is_empty()    # assertTrue → assert x
    assert stack.size() == 0   # assertEqual → assert a == b

def test_pop_empty_raises(stack):
    with pytest.raises(IndexError):   # assertRaises → pytest.raises
        stack.pop()
```

**Why:** pytest runs unittest tests unchanged, but writing new tests in pytest style is cleaner. The fixture replaces `setUp`, plain `assert` replaces named methods, and `pytest.raises` replaces `assertRaises`.
</details>

---

<a id="q10"></a>
### Q10 🟠 · Capstone — Full TestCase for a Stack Data Structure

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

**Problem:** Implement a `Stack` class with `push(item)`, `pop()`, `peek()`, `is_empty()`, `is_full()`, `size()`, and a bounded `capacity`. Write a complete `TestCase` that covers: empty stack behavior, push/pop/peek operations, LIFO order, overflow (`OverflowError`), underflow (`IndexError`), and capacity edge cases. Use `setUp` for fresh state per test.

<details>
<summary>💡 Hint</summary>

A complete test suite tests happy path, error cases, and edge cases (empty, full, exactly capacity). Use `setUp` so each test gets a fresh `Stack(capacity=3)`. Test LIFO by pushing 1, 2, 3 and verifying pop order is 3, 2, 1.
</details>

<details>
<summary>✅ Answer</summary>

```python
import unittest

class Stack:
    def __init__(self, capacity=10):
        if capacity < 1:
            raise ValueError("Capacity must be positive")
        self._data = []
        self._capacity = capacity

    def push(self, item):
        if self.is_full():
            raise OverflowError("Stack is full")
        self._data.append(item)

    def pop(self):
        if self.is_empty():
            raise IndexError("Pop from empty stack")
        return self._data.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError("Peek at empty stack")
        return self._data[-1]

    def is_empty(self):
        return len(self._data) == 0

    def is_full(self):
        return len(self._data) >= self._capacity

    def size(self):
        return len(self._data)


class TestStack(unittest.TestCase):

    def setUp(self):
        self.stack = Stack(capacity=3)   # fresh stack per test

    def test_new_stack_is_empty(self):
        self.assertTrue(self.stack.is_empty())
        self.assertEqual(self.stack.size(), 0)

    def test_push_increases_size(self):
        self.stack.push(1)
        self.assertEqual(self.stack.size(), 1)
        self.assertFalse(self.stack.is_empty())

    def test_pop_returns_last_item(self):
        self.stack.push("a")
        self.stack.push("b")
        self.assertEqual(self.stack.pop(), "b")
        self.assertEqual(self.stack.size(), 1)

    def test_peek_does_not_remove(self):
        self.stack.push(42)
        self.assertEqual(self.stack.peek(), 42)
        self.assertEqual(self.stack.size(), 1)   # still there

    def test_lifo_order(self):
        for item in [1, 2, 3]:
            self.stack.push(item)
        result = [self.stack.pop() for _ in range(3)]
        self.assertEqual(result, [3, 2, 1])

    def test_overflow_raises(self):
        self.stack.push(1)
        self.stack.push(2)
        self.stack.push(3)
        with self.assertRaises(OverflowError):
            self.stack.push(4)   # over capacity

    def test_pop_empty_raises(self):
        with self.assertRaises(IndexError):
            self.stack.pop()

    def test_peek_empty_raises(self):
        with self.assertRaises(IndexError):
            self.stack.peek()

    def test_is_full_at_capacity(self):
        for i in range(3):
            self.stack.push(i)
        self.assertTrue(self.stack.is_full())

    def test_invalid_capacity_raises(self):
        with self.assertRaises(ValueError):
            Stack(capacity=0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

**Why:** A complete test suite covers the constructor, happy path for each method, error cases (over/underflow), and edge cases (capacity=1, exactly full). `setUp` ensures each test starts with a fresh stack — mutations in one test don't affect others.
</details>

---

## Navigation

| | |
|---|---|
| Deep dive | [theory.md](./theory.md) |
| Local practice | [practice_local.py](./practice_local.py) |
| Root practice (35 Qs) | [../practice.md](../practice.md) |
| Sibling: pytest | [../01_pytest/practice.md](../01_pytest/practice.md) |
| Sibling: mocking | [../03_mocking/practice.md](../03_mocking/practice.md) |

**[Back to README](../../README.md)**
