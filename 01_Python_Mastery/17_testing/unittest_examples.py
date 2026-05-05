"""
unittest examples — Python's built-in testing framework.
Run: python -m pytest unittest_examples.py -v
     python -m unittest unittest_examples -v
     python unittest_examples.py
"""
import unittest
from datetime import date
from typing import Optional
from io import StringIO
import sys


# ─────────────────────────────────────────────
# Code under test
# ─────────────────────────────────────────────

class TemperatureConverter:
    """Convert temperatures between Celsius, Fahrenheit, and Kelvin."""

    @staticmethod
    def celsius_to_fahrenheit(c: float) -> float:
        return (c * 9 / 5) + 32

    @staticmethod
    def fahrenheit_to_celsius(f: float) -> float:
        return (f - 32) * 5 / 9

    @staticmethod
    def celsius_to_kelvin(c: float) -> float:
        if c < -273.15:
            raise ValueError(f"Temperature {c}°C is below absolute zero")
        return c + 273.15

    @staticmethod
    def kelvin_to_celsius(k: float) -> float:
        if k < 0:
            raise ValueError(f"Kelvin {k} cannot be negative")
        return k - 273.15


class Stack:
    """Simple LIFO stack with bounded capacity."""

    def __init__(self, capacity: int = 10):
        if capacity < 1:
            raise ValueError("Capacity must be positive")
        self._data: list = []
        self._capacity = capacity

    def push(self, item) -> None:
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

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def is_full(self) -> bool:
        return len(self._data) >= self._capacity

    def size(self) -> int:
        return len(self._data)


class StudentGrade:
    """Manage student grades."""

    LETTER_SCALE = [
        (90, 'A'),
        (80, 'B'),
        (70, 'C'),
        (60, 'D'),
        (0,  'F'),
    ]

    def __init__(self, name: str):
        self.name = name
        self._grades: list[float] = []

    def add_grade(self, grade: float) -> None:
        if not (0 <= grade <= 100):
            raise ValueError(f"Grade {grade} must be between 0 and 100")
        self._grades.append(grade)

    def average(self) -> Optional[float]:
        if not self._grades:
            return None
        return sum(self._grades) / len(self._grades)

    def letter_grade(self) -> Optional[str]:
        avg = self.average()
        if avg is None:
            return None
        for threshold, letter in self.LETTER_SCALE:
            if avg >= threshold:
                return letter
        return 'F'

    def highest(self) -> Optional[float]:
        return max(self._grades) if self._grades else None

    def lowest(self) -> Optional[float]:
        return min(self._grades) if self._grades else None


# ─────────────────────────────────────────────
# 1. Basic TestCase
# ─────────────────────────────────────────────

class TestTemperatureConverter(unittest.TestCase):
    """unittest.TestCase — assert methods with meaningful messages."""

    def test_celsius_to_fahrenheit_freezing(self):
        self.assertEqual(TemperatureConverter.celsius_to_fahrenheit(0), 32.0)

    def test_celsius_to_fahrenheit_boiling(self):
        self.assertEqual(TemperatureConverter.celsius_to_fahrenheit(100), 212.0)

    def test_celsius_to_fahrenheit_body_temp(self):
        result = TemperatureConverter.celsius_to_fahrenheit(37)
        self.assertAlmostEqual(result, 98.6, places=1)

    def test_fahrenheit_to_celsius_freezing(self):
        self.assertEqual(TemperatureConverter.fahrenheit_to_celsius(32), 0.0)

    def test_fahrenheit_to_celsius_boiling(self):
        self.assertAlmostEqual(
            TemperatureConverter.fahrenheit_to_celsius(212), 100.0
        )

    def test_celsius_to_kelvin_absolute_zero(self):
        self.assertAlmostEqual(
            TemperatureConverter.celsius_to_kelvin(-273.15), 0.0, places=5
        )

    def test_celsius_to_kelvin_below_absolute_zero_raises(self):
        with self.assertRaises(ValueError):
            TemperatureConverter.celsius_to_kelvin(-300)

    def test_celsius_to_kelvin_error_message(self):
        with self.assertRaisesRegex(ValueError, "absolute zero"):
            TemperatureConverter.celsius_to_kelvin(-300)

    def test_kelvin_negative_raises(self):
        with self.assertRaises(ValueError):
            TemperatureConverter.kelvin_to_celsius(-1)

    def test_roundtrip_celsius_fahrenheit(self):
        original = 25.0
        converted = TemperatureConverter.celsius_to_fahrenheit(original)
        back = TemperatureConverter.fahrenheit_to_celsius(converted)
        self.assertAlmostEqual(back, original, places=10)


# ─────────────────────────────────────────────
# 2. setUp and tearDown
# ─────────────────────────────────────────────

class TestStack(unittest.TestCase):
    """Demonstrate setUp/tearDown for per-test setup."""

    def setUp(self):
        """Called before every test method."""
        self.stack = Stack(capacity=3)

    def tearDown(self):
        """Called after every test method (even if test fails)."""
        # Release resources, close connections, etc.
        # Nothing needed here, but shown for illustration
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
        self.assertEqual(self.stack.size(), 1)

    def test_peek_does_not_remove_item(self):
        self.stack.push(42)
        peeked = self.stack.peek()
        self.assertEqual(peeked, 42)
        self.assertEqual(self.stack.size(), 1)  # still there

    def test_pop_empty_raises_index_error(self):
        with self.assertRaises(IndexError):
            self.stack.pop()

    def test_peek_empty_raises_index_error(self):
        with self.assertRaises(IndexError):
            self.stack.peek()

    def test_push_to_full_stack_raises_overflow(self):
        self.stack.push(1)
        self.stack.push(2)
        self.stack.push(3)
        with self.assertRaises(OverflowError):
            self.stack.push(4)

    def test_is_full_after_capacity_reached(self):
        for i in range(3):
            self.stack.push(i)
        self.assertTrue(self.stack.is_full())

    def test_lifo_order(self):
        items = [1, 2, 3]
        for item in items:
            self.stack.push(item)
        result = [self.stack.pop() for _ in range(3)]
        self.assertEqual(result, [3, 2, 1])


# ─────────────────────────────────────────────
# 3. setUpClass and tearDownClass
# ─────────────────────────────────────────────

class TestStudentGrade(unittest.TestCase):
    """
    setUpClass: runs once before any test in the class.
    Use for expensive setup shared by all tests (DB connection, etc.)
    """

    @classmethod
    def setUpClass(cls):
        """Called once before all tests in this class."""
        cls.passing_student = StudentGrade("Alice")
        cls.passing_student.add_grade(85)
        cls.passing_student.add_grade(90)
        cls.passing_student.add_grade(78)

        cls.failing_student = StudentGrade("Bob")
        cls.failing_student.add_grade(45)
        cls.failing_student.add_grade(52)

    @classmethod
    def tearDownClass(cls):
        """Called once after all tests in this class."""
        pass

    def test_passing_student_average(self):
        avg = self.passing_student.average()
        self.assertAlmostEqual(avg, 84.33, places=2)

    def test_passing_student_letter_grade(self):
        self.assertEqual(self.passing_student.letter_grade(), 'B')

    def test_failing_student_letter_grade(self):
        self.assertEqual(self.failing_student.letter_grade(), 'F')

    def test_no_grades_returns_none_average(self):
        empty = StudentGrade("Charlie")
        self.assertIsNone(empty.average())

    def test_no_grades_returns_none_letter(self):
        empty = StudentGrade("Charlie")
        self.assertIsNone(empty.letter_grade())

    def test_highest_grade(self):
        self.assertEqual(self.passing_student.highest(), 90)

    def test_lowest_grade(self):
        self.assertEqual(self.failing_student.lowest(), 45)

    def test_invalid_grade_raises(self):
        student = StudentGrade("Test")
        with self.assertRaises(ValueError):
            student.add_grade(101)

    def test_negative_grade_raises(self):
        student = StudentGrade("Test")
        with self.assertRaises(ValueError):
            student.add_grade(-1)


# ─────────────────────────────────────────────
# 4. All assertion methods demonstrated
# ─────────────────────────────────────────────

class TestAssertionMethods(unittest.TestCase):
    """Reference for all major unittest assertion methods."""

    def test_equality_assertions(self):
        self.assertEqual(1 + 1, 2)
        self.assertNotEqual(1 + 1, 3)
        self.assertAlmostEqual(0.1 + 0.2, 0.3, places=10)
        self.assertNotAlmostEqual(0.1 + 0.2, 0.4, places=1)

    def test_boolean_assertions(self):
        self.assertTrue(1 == 1)
        self.assertFalse(1 == 2)

    def test_identity_assertions(self):
        x = [1, 2, 3]
        y = x
        z = [1, 2, 3]
        self.assertIs(x, y)        # same object
        self.assertIsNot(x, z)     # different object, equal value
        self.assertIsNone(None)
        self.assertIsNotNone(42)

    def test_membership_assertions(self):
        self.assertIn(3, [1, 2, 3])
        self.assertNotIn(4, [1, 2, 3])

    def test_type_assertion(self):
        self.assertIsInstance(42, int)
        self.assertIsInstance("hello", (str, bytes))
        self.assertNotIsInstance(42, str)

    def test_comparison_assertions(self):
        self.assertGreater(5, 3)
        self.assertGreaterEqual(5, 5)
        self.assertLess(3, 5)
        self.assertLessEqual(3, 3)

    def test_container_assertions(self):
        self.assertIn("key", {"key": "value"})
        self.assertSequenceEqual([1, 2, 3], [1, 2, 3])
        self.assertListEqual([1, 2], [1, 2])
        self.assertDictEqual({"a": 1}, {"a": 1})
        self.assertSetEqual({1, 2, 3}, {3, 1, 2})
        self.assertTupleEqual((1, 2), (1, 2))

    def test_string_assertions(self):
        self.assertRegex("hello world", r"hello \w+")
        self.assertNotRegex("hello world", r"^\d+")
        self.assertMultiLineEqual("line1\nline2", "line1\nline2")

    def test_raises_with_context(self):
        with self.assertRaises(ZeroDivisionError):
            _ = 1 / 0

    def test_raises_regex(self):
        with self.assertRaisesRegex(ValueError, "must be positive"):
            raise ValueError("amount must be positive")

    def test_warns(self):
        import warnings
        with self.assertWarns(DeprecationWarning):
            warnings.warn("old API", DeprecationWarning)

    def test_logs(self):
        import logging
        with self.assertLogs("mylogger", level="INFO") as cm:
            logging.getLogger("mylogger").info("test message")
        self.assertIn("test message", cm.output[0])


# ─────────────────────────────────────────────
# 5. Skipping and expected failures
# ─────────────────────────────────────────────

class TestSkipping(unittest.TestCase):

    @unittest.skip("demonstrating unconditional skip")
    def test_nothing(self):
        self.fail("should never run")

    @unittest.skipIf(sys.platform == "win32", "Linux/Mac only")
    def test_unix_specific_feature(self):
        import os
        self.assertTrue(os.path.exists("/"))

    @unittest.skipUnless(sys.version_info >= (3, 10), "Requires Python 3.10+")
    def test_match_statement(self):
        x = 5
        match x:
            case 5:
                result = "five"
            case _:
                result = "other"
        self.assertEqual(result, "five")

    @unittest.expectedFailure
    def test_known_broken_thing(self):
        self.assertEqual(1, 2)  # expected to fail — not reported as error


# ─────────────────────────────────────────────
# 6. Subtests — don't stop on first failure
# ─────────────────────────────────────────────

class TestSubtests(unittest.TestCase):
    """subTest lets you run multiple checks without stopping on first failure."""

    def test_temperature_conversions_with_subtests(self):
        test_cases = [
            (0,   32.0,  "freezing"),
            (100, 212.0, "boiling"),
            (37,  98.6,  "body temp"),
            (-40, -40.0, "same in both scales"),
        ]
        for celsius, expected_f, label in test_cases:
            with self.subTest(label=label, celsius=celsius):
                result = TemperatureConverter.celsius_to_fahrenheit(celsius)
                self.assertAlmostEqual(result, expected_f, places=1)

    def test_grade_boundaries_with_subtests(self):
        boundaries = [
            (95, 'A'), (90, 'A'), (85, 'B'), (80, 'B'),
            (75, 'C'), (70, 'C'), (65, 'D'), (60, 'D'),
            (55, 'F'), (0,  'F'),
        ]
        for score, expected_letter in boundaries:
            with self.subTest(score=score, expected=expected_letter):
                student = StudentGrade("Test")
                student.add_grade(score)
                self.assertEqual(student.letter_grade(), expected_letter)


# ─────────────────────────────────────────────
# 7. Testing output with captured stdout
# ─────────────────────────────────────────────

def greet(name: str) -> None:
    print(f"Hello, {name}!")

def print_multiplication_table(n: int) -> None:
    for i in range(1, 11):
        print(f"{n} x {i} = {n * i}")


class TestPrintedOutput(unittest.TestCase):

    def test_greet_outputs_correct_message(self):
        captured = StringIO()
        sys.stdout = captured
        try:
            greet("World")
        finally:
            sys.stdout = sys.__stdout__  # always restore
        self.assertEqual(captured.getvalue(), "Hello, World!\n")

    def test_multiplication_table_first_line(self):
        captured = StringIO()
        sys.stdout = captured
        try:
            print_multiplication_table(5)
        finally:
            sys.stdout = sys.__stdout__
        lines = captured.getvalue().strip().split("\n")
        self.assertEqual(lines[0], "5 x 1 = 5")
        self.assertEqual(len(lines), 10)


# ─────────────────────────────────────────────
# 8. Test suite composition
# ─────────────────────────────────────────────

def suite():
    """Manually compose a test suite — useful for selective running."""
    s = unittest.TestSuite()
    s.addTest(TestTemperatureConverter("test_celsius_to_fahrenheit_freezing"))
    s.addTest(TestTemperatureConverter("test_celsius_to_fahrenheit_boiling"))
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestStack))
    return s


# ─────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Option 1: run all tests
    unittest.main(verbosity=2)

    # Option 2: run specific suite
    # runner = unittest.TextTestRunner(verbosity=2)
    # runner.run(suite())
