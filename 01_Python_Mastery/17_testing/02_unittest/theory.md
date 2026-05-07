# unittest — Deep Dive

`unittest` is Python's built-in testing framework. Think of it as the formal rulebook: every test lives in a class, every assertion has a named method, and the ceremony makes it explicit. pytest is more popular today, but unittest is everywhere in the standard library, older codebases, and interview questions.

---

## Learning Priority

**Must Learn** — daily use, interview essential:
`TestCase` · `assertEqual` / `assertRaises` · `setUp` / `tearDown`

**Should Learn** — important for real projects:
`setUpClass` / `tearDownClass` · `assertIn` · `assertAlmostEqual` · `skip` / `expectedFailure`

**Good to Know** — useful in specific situations:
`subTest` · `TestSuite` · `TextTestRunner`

**Reference** — know it exists, look up when needed:
`unittest.mock` (lives here, used everywhere) · `load_tests` protocol

---

## 1. TestCase — Class-Based Tests

`unittest.TestCase` is the building block. Every class of tests inherits from it, and every test is a method starting with `test_`.

```python
import unittest

def add(a, b):
    return a + b

class TestMath(unittest.TestCase):

    def test_add_positive(self):
        self.assertEqual(add(2, 3), 5)    # ← specific assertion method

    def test_add_zero(self):
        self.assertEqual(add(0, 5), 5)

    def test_add_negative(self):
        self.assertEqual(add(-3, -7), -10)


if __name__ == "__main__":
    unittest.main()
```

**Running unittest:**

```bash
python -m unittest test_module          # run a module
python -m unittest test_module.TestClass  # run one class
python -m unittest test_module.TestClass.test_add  # run one test
python -m unittest discover             # discover test_*.py files
python -m unittest -v                   # verbose output
```

---

## 2. setUp and tearDown — Per-Test Lifecycle

`setUp` runs before every test method. `tearDown` runs after every test method — even if the test fails. Each test gets a fresh state.

```python
import unittest
import sqlite3

class TestStack(unittest.TestCase):

    def setUp(self):
        """Called before EACH test method."""
        self.stack = Stack(capacity=3)      # fresh stack per test

    def tearDown(self):
        """Called after EACH test method — even on failure."""
        # release resources: close files, connections, etc.
        pass

    def test_new_stack_is_empty(self):
        self.assertTrue(self.stack.is_empty())
        self.assertEqual(self.stack.size(), 0)

    def test_push_increases_size(self):
        self.stack.push(1)
        self.assertEqual(self.stack.size(), 1)

    def test_pop_returns_last_item(self):
        self.stack.push("a")
        self.stack.push("b")
        self.assertEqual(self.stack.pop(), "b")

    def test_pop_empty_raises(self):
        with self.assertRaises(IndexError):
            self.stack.pop()
```

Each `test_*` method gets a brand-new `self.stack`. A mutation in one test never affects another.

---

## 3. setUpClass / tearDownClass — Class-Level Lifecycle

`setUpClass` runs once before any test in the class. `tearDownClass` runs once after all tests in the class. Use for expensive shared resources: database connections, server startup, large file loading.

```python
import unittest

class TestStudentGrade(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Called ONCE before all tests in this class."""
        cls.passing_student = StudentGrade("Alice")
        cls.passing_student.add_grade(85)
        cls.passing_student.add_grade(90)
        cls.passing_student.add_grade(78)

        cls.failing_student = StudentGrade("Bob")
        cls.failing_student.add_grade(45)
        cls.failing_student.add_grade(52)

    @classmethod
    def tearDownClass(cls):
        """Called ONCE after all tests in this class."""
        cls.passing_student = None
        cls.failing_student = None

    def test_passing_average(self):
        avg = self.passing_student.average()
        self.assertAlmostEqual(avg, 84.33, places=2)

    def test_letter_grade_b(self):
        self.assertEqual(self.passing_student.letter_grade(), "B")

    def test_failing_letter_grade(self):
        self.assertEqual(self.failing_student.letter_grade(), "F")
```

**Important:** `setUpClass` is a classmethod — it receives `cls`, not `self`. Data set on `cls` is accessible as `self.attribute` in tests.

**When to use each:**

| Method | Runs | Use for |
|--------|------|---------|
| `setUp` | Before every test | Mutable state, fresh objects |
| `tearDown` | After every test | Cleanup after mutations |
| `setUpClass` | Once before class | Expensive, read-only shared setup |
| `tearDownClass` | Once after class | Cleanup shared resources |

---

## 4. Assert Methods — Complete Reference

unittest provides named assertion methods with clear error messages on failure.

```python
class TestAssertions(unittest.TestCase):

    def test_equality(self):
        self.assertEqual(1 + 1, 2)                    # a == b
        self.assertNotEqual(1 + 1, 3)                 # a != b
        self.assertAlmostEqual(0.1 + 0.2, 0.3, places=10)  # float equality
        self.assertNotAlmostEqual(0.1, 0.5, places=1)

    def test_boolean(self):
        self.assertTrue(1 == 1)                       # bool(x) is True
        self.assertFalse(1 == 2)                      # bool(x) is False

    def test_identity(self):
        x = [1, 2, 3]
        y = x
        z = [1, 2, 3]
        self.assertIs(x, y)                           # x is y (same object)
        self.assertIsNot(x, z)                        # x is not z
        self.assertIsNone(None)
        self.assertIsNotNone(42)

    def test_membership(self):
        self.assertIn(3, [1, 2, 3])                   # 3 in [1, 2, 3]
        self.assertNotIn(4, [1, 2, 3])

    def test_type(self):
        self.assertIsInstance(42, int)
        self.assertIsInstance("hello", (str, bytes))  # either type
        self.assertNotIsInstance(42, str)

    def test_comparison(self):
        self.assertGreater(5, 3)                      # a > b
        self.assertGreaterEqual(5, 5)                 # a >= b
        self.assertLess(3, 5)                         # a < b
        self.assertLessEqual(3, 3)                    # a <= b

    def test_containers(self):
        self.assertIn("key", {"key": "value"})
        self.assertListEqual([1, 2], [1, 2])
        self.assertDictEqual({"a": 1}, {"a": 1})
        self.assertSetEqual({1, 2, 3}, {3, 1, 2})    # order doesn't matter

    def test_strings(self):
        self.assertRegex("hello world", r"hello \w+")
        self.assertNotRegex("hello world", r"^\d+")

    def test_exception(self):
        with self.assertRaises(ZeroDivisionError):
            _ = 1 / 0

    def test_exception_message(self):
        with self.assertRaisesRegex(ValueError, "must be positive"):
            raise ValueError("amount must be positive")
```

**Quick comparison with pytest:**

| unittest | pytest equivalent |
|----------|-------------------|
| `assertEqual(a, b)` | `assert a == b` |
| `assertRaises(Exc)` | `pytest.raises(Exc)` |
| `assertAlmostEqual(a, b, places=5)` | `assert a == pytest.approx(b)` |
| `assertIn(a, b)` | `assert a in b` |
| `assertIsNone(x)` | `assert x is None` |

---

## 5. Test Discovery and Runner

unittest discovers tests automatically when you follow naming conventions:

```
Files:    test_*.py or *_test.py
Classes:  TestXxx (inherits unittest.TestCase)
Methods:  test_xxx
```

```bash
# Discover all tests from current directory:
python -m unittest discover

# Discover in specific directory, matching pattern:
python -m unittest discover -s tests/ -p "test_*.py"

# Verbose:
python -m unittest discover -v
```

**Custom test runner** — run programmatically:

```python
import unittest

suite = unittest.TestLoader().loadTestsFromTestCase(TestStack)
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
```

---

## 6. subTest — Loop Without Stopping on First Failure

Without `subTest`, one failing case in a loop stops all remaining cases. `subTest` runs them all and reports each failure independently.

```python
class TestConversions(unittest.TestCase):

    def test_temperature_cases(self):
        cases = [
            (0,    32.0,  "freezing"),
            (100,  212.0, "boiling"),
            (37,   98.6,  "body temp"),
            (-40,  -40.0, "same in both scales"),
        ]
        for celsius, expected_f, label in cases:
            with self.subTest(label=label, celsius=celsius):   # ← key
                result = celsius_to_fahrenheit(celsius)
                self.assertAlmostEqual(result, expected_f, places=1)
```

If "body temp" fails, "same in both scales" still runs. Without `subTest`, the loop stops at the first failure.

**When to use subTest vs parametrize:**
- `subTest` — when you already have a list and want to keep it in one method
- `@pytest.mark.parametrize` — when using pytest and want each case as an independent test in output

---

## 7. Skip and expectedFailure

```python
import unittest
import sys

class TestSkipping(unittest.TestCase):

    @unittest.skip("demonstrating unconditional skip")
    def test_nothing(self):
        self.fail("should never run")

    @unittest.skipIf(sys.platform == "win32", "Linux/Mac only")
    def test_unix_paths(self):
        import os
        self.assertTrue(os.path.exists("/"))

    @unittest.skipUnless(sys.version_info >= (3, 10), "Requires Python 3.10+")
    def test_match_statement(self):
        x = 5
        match x:
            case 5:
                result = "five"
        self.assertEqual(result, "five")

    @unittest.expectedFailure
    def test_known_broken_thing(self):
        self.assertEqual(1, 2)   # expected to fail — shown as xfail, not error
```

Output categories:
- `s` — skipped (expected)
- `x` — expected failure (counts as pass)
- `X` — unexpected success on an `@expectedFailure` test (counts as failure)

---

## 8. unittest vs pytest — When to Use Each

| Factor | unittest | pytest |
|--------|----------|--------|
| Stdlib dependency | Built-in — no install | Requires `pip install pytest` |
| Assertion style | Named methods (`assertEqual`) | Plain `assert` with rich diffs |
| Fixtures | `setUp`/`tearDown` per class | Flexible scope, composable, conftest |
| Parametrize | `subTest` in a loop | `@pytest.mark.parametrize` |
| Output | Basic | Rich: colors, diffs, plugins |
| Migration | Effort required | Runs existing unittest tests too |
| When to use | Legacy codebase, stdlib-only constraint | New projects, team preference |

pytest runs all unittest tests natively. You can mix both in one project.

```python
# pytest runs this without any changes
class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
```

---

## Common Mistakes

**1. Forgetting `@classmethod` on `setUpClass`:**

```python
# WRONG — crashes with TypeError
def setUpClass(self):
    self.db = create_db()

# RIGHT
@classmethod
def setUpClass(cls):
    cls.db = create_db()
```

**2. Mutating class-level state in tests (shared across all tests):**

```python
@classmethod
def setUpClass(cls):
    cls.cart = ShoppingCart()   # shared!

def test_add_item(self):
    self.cart.add_item("apple")  # mutation bleeds into next test!
```

Use `setUp` for anything that tests mutate.

**3. Using `assertEqual` for floats — use `assertAlmostEqual` instead:**

```python
# WRONG: may fail due to floating point
self.assertEqual(0.1 + 0.2, 0.3)

# RIGHT
self.assertAlmostEqual(0.1 + 0.2, 0.3, places=10)
```

**4. Missing `unittest.main()` guard:**

```python
# Without this, the file runs tests when imported as a module
if __name__ == "__main__":
    unittest.main()
```

---

## Navigation

| | |
|---|---|
| Back to root | [17_testing/theory.md](../theory.md) |
| Practice questions | [practice.md](./practice.md) |
| Local practice | [practice_local.py](./practice_local.py) |
| Sibling: pytest | [../01_pytest/theory.md](../01_pytest/theory.md) |
| Sibling: mocking | [../03_mocking/theory.md](../03_mocking/theory.md) |

**[Back to README](../../README.md)**
