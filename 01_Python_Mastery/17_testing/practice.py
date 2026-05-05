# 💻 Testing in Python — Practice
# Run with: python3 practice.py  OR  pytest practice.py
#
# This file demonstrates testing CONCEPTS as runnable code.
# All "test_" functions run manually at the bottom via run_all_tests().
# Patterns shown: assert, unittest.TestCase, setUp/tearDown,
# unittest.mock (patch, Mock, MagicMock, side_effect),
# parametrized testing, testing exceptions, testing with temp files.

import unittest
import unittest.mock
from unittest.mock import Mock, MagicMock, patch, call
import io
import os
import tempfile


# =============================================================================
# SECTION 1: assert Basics — The Foundation of Every Test
# =============================================================================

# assert is Python's built-in assertion mechanism.
# pytest rewrites assert statements to show rich diffs on failure.
# In plain Python, a failing assert raises AssertionError.

print("=" * 60)
print("SECTION 1: assert basics")
print("=" * 60)

def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("cannot divide by zero")
    return a / b

def is_palindrome(s):
    s = s.lower().replace(" ", "")
    return s == s[::-1]

# Inline demo assertions
assert add(2, 3) == 5,        "2 + 3 should equal 5"
assert add(-1, 1) == 0,       "negative + positive"
assert add(0, 0) == 0,        "zero + zero"
assert is_palindrome("racecar"),              "racecar is a palindrome"
assert not is_palindrome("hello"),            "hello is not a palindrome"
assert is_palindrome("A man a plan a canal Panama"), "famous palindrome"

print("  All basic assertions passed.\n")


# =============================================================================
# SECTION 2: unittest.TestCase — Class-Based Testing
# =============================================================================

print("=" * 60)
print("SECTION 2: unittest.TestCase")
print("=" * 60)

class TestMathFunctions(unittest.TestCase):
    """Group related tests in a TestCase class.
    Each method starting with test_ is an independent test."""

    # setUp runs BEFORE each test method — fresh state every time
    def setUp(self):
        self.test_data = [1, 2, 3, 4, 5]
        self.empty     = []

    # tearDown runs AFTER each test method — cleanup
    def tearDown(self):
        # Release any resources acquired in setUp
        self.test_data = None

    def test_add_positive_numbers(self):
        # assertEqual checks a == b with a clear error message on failure
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(10, 20), 30)

    def test_add_with_zero(self):
        self.assertEqual(add(0, 5), 5)
        self.assertEqual(add(5, 0), 5)

    def test_add_negative_numbers(self):
        self.assertEqual(add(-3, -7), -10)
        self.assertEqual(add(-5, 5), 0)

    def test_divide_normal(self):
        # assertAlmostEqual for floating point (avoids 0.1 + 0.2 != 0.3 issues)
        self.assertAlmostEqual(divide(10, 3), 3.333, places=3)
        self.assertEqual(divide(10, 2), 5.0)

    def test_divide_by_zero_raises(self):
        # assertRaises as context manager — tests that exception IS raised
        with self.assertRaises(ZeroDivisionError):
            divide(10, 0)

    def test_divide_by_zero_message(self):
        # Check both the exception type AND the message
        with self.assertRaises(ZeroDivisionError) as ctx:
            divide(10, 0)
        self.assertIn("cannot divide by zero", str(ctx.exception))

    def test_palindrome_various(self):
        self.assertTrue(is_palindrome("racecar"))
        self.assertTrue(is_palindrome("madam"))
        self.assertFalse(is_palindrome("hello"))
        self.assertFalse(is_palindrome("python"))

    def test_setUp_provides_fresh_data(self):
        # setUp guarantees test_data is [1,2,3,4,5] — even if another test mutated it
        self.assertEqual(len(self.test_data), 5)
        self.test_data.append(99)  # mutation — but next test still gets fresh copy

    def test_empty_list_after_mutation_in_previous(self):
        # setUp ran again — test_data is fresh [1,2,3,4,5], not [1,2,3,4,5,99]
        self.assertEqual(self.test_data, [1, 2, 3, 4, 5])


# Run the TestCase and capture results
suite = unittest.TestLoader().loadTestsFromTestCase(TestMathFunctions)
runner = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0)
result = runner.run(suite)
print(f"  TestMathFunctions: {result.testsRun} tests run, "
      f"{len(result.failures)} failures, {len(result.errors)} errors")
if result.failures:
    for test, traceback in result.failures:
        print(f"  FAIL: {test}")
if result.wasSuccessful():
    print("  All TestCase tests passed.")
print()


# =============================================================================
# SECTION 3: Mock Objects — Replacing Dependencies
# =============================================================================

# Mocking replaces slow/external/unpredictable dependencies:
# - External APIs (HTTP calls)
# - Databases
# - File system
# - Time / randomness
# - Email / SMS senders

print("=" * 60)
print("SECTION 3: Mock objects")
print("=" * 60)

# --- Basic Mock ---
# Mock() accepts any attribute access and any call without raising.
m = Mock()
m.connect("localhost", 5432)    # recorded but does nothing
m.connect("localhost", 5432)    # second call
m.query("SELECT 1")

# Verify call history
m.connect.assert_called()                           # was it called at all?
m.connect.assert_called_with("localhost", 5432)     # last call had these args?
assert m.connect.call_count == 2                    # exactly 2 calls
assert m.query.call_args == call("SELECT 1")        # args of most recent call
m.close.assert_not_called()                         # .close() never called
print("  Basic Mock call tracking: PASSED")

# --- return_value ---
m_func = Mock(return_value={"id": 1, "name": "Alice"})
result = m_func(user_id=1)
assert result == {"id": 1, "name": "Alice"}
print("  Mock return_value: PASSED")

# --- side_effect — raises exception ---
m_fail = Mock(side_effect=ConnectionError("DB is down"))
try:
    m_fail()
except ConnectionError as e:
    print(f"  side_effect raises: {e}")

# --- side_effect — sequence of return values ---
m_seq = Mock(side_effect=[10, 20, 30])
assert m_seq() == 10
assert m_seq() == 20
assert m_seq() == 30
print("  side_effect sequence: PASSED")

# --- side_effect — function ---
m_fn = Mock(side_effect=lambda x: x * 2)
assert m_fn(5) == 10
assert m_fn(3) == 6
print("  side_effect function: PASSED")

# --- MagicMock — also supports dunder/magic methods ---
mm = MagicMock()
assert len(mm) == 0          # __len__ returns 0 by default
assert mm[0] is not None     # __getitem__ returns a MagicMock
mm.__str__.return_value = "my mock"
assert str(mm) == "my mock"
print("  MagicMock magic methods: PASSED")
print()


# =============================================================================
# SECTION 4: patch — Replacing Real Objects at Test Time
# =============================================================================

# patch() temporarily replaces a name in a module with a Mock.
# CRITICAL RULE: patch WHERE THE NAME IS USED, not where it's defined.
# If your_module.py does `import os`, patch "your_module.os".
# If it does `from os.path import exists`, patch "your_module.exists".

print("=" * 60)
print("SECTION 4: patch (decorator and context manager forms)")
print("=" * 60)

# System under test — a function that calls os.getenv
def get_api_key():
    """Returns API key from environment, raises if missing."""
    key = os.getenv("API_KEY")
    if not key:
        raise EnvironmentError("API_KEY not set")
    return key

# --- patch as context manager ---
with patch("os.getenv") as mock_getenv:
    mock_getenv.return_value = "test-key-abc123"
    key = get_api_key()
    assert key == "test-key-abc123"
    mock_getenv.assert_called_once_with("API_KEY")
print("  patch as context manager: PASSED")

# --- patch.dict — patch a dictionary (env vars, config dicts) ---
with patch.dict(os.environ, {"API_KEY": "env-patched-key"}, clear=False):
    # clear=False means we only add/override; existing vars remain
    assert os.environ["API_KEY"] == "env-patched-key"
print("  patch.dict for os.environ: PASSED")

# After the with block, os.environ is restored
assert "API_KEY" not in os.environ or os.environ.get("API_KEY") != "env-patched-key"
print("  patch.dict cleanup (restored after block): PASSED")


# --- patch as decorator ---
class EmailService:
    def send(self, to, subject, body):
        # Would send a real email in production
        raise RuntimeError("No real email in tests!")

class UserRegistration:
    def __init__(self, email_service):
        self.email = email_service

    def register(self, username, email_addr):
        # ... create user in DB ...
        self.email.send(
            to=email_addr,
            subject="Welcome!",
            body=f"Hi {username}, welcome aboard."
        )
        return {"username": username, "email": email_addr, "status": "created"}


def test_registration_sends_welcome_email():
    """Verify that register() calls email.send() with correct args."""
    mock_email = Mock()
    service = UserRegistration(email_service=mock_email)

    result = service.register("alice", "alice@example.com")

    assert result["status"] == "created"
    mock_email.send.assert_called_once_with(
        to="alice@example.com",
        subject="Welcome!",
        body="Hi alice, welcome aboard."
    )

test_registration_sends_welcome_email()
print("  test_registration_sends_welcome_email: PASSED\n")


# =============================================================================
# SECTION 5: Testing Exceptions
# =============================================================================

print("=" * 60)
print("SECTION 5: Testing exceptions")
print("=" * 60)

def validate_age(age):
    if not isinstance(age, int):
        raise TypeError(f"age must be int, got {type(age).__name__}")
    if age < 0 or age > 150:
        raise ValueError(f"age {age} is out of range [0, 150]")
    return True

def test_validate_age_happy_path():
    assert validate_age(25)  is True
    assert validate_age(0)   is True
    assert validate_age(150) is True

def test_validate_age_bad_type():
    try:
        validate_age("25")
        assert False, "Should have raised TypeError"
    except TypeError as e:
        assert "must be int" in str(e)

def test_validate_age_out_of_range():
    try:
        validate_age(-1)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "-1 is out of range" in str(e)

    try:
        validate_age(999)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "999 is out of range" in str(e)

test_validate_age_happy_path()
test_validate_age_bad_type()
test_validate_age_out_of_range()
print("  All exception tests passed.\n")


# =============================================================================
# SECTION 6: Parametrized Testing Pattern (without pytest)
# =============================================================================

# pytest.mark.parametrize is the idiomatic way.
# Without pytest we replicate the pattern: a list of (input, expected) tuples
# iterated over in a loop.

print("=" * 60)
print("SECTION 6: Parametrized testing pattern")
print("=" * 60)

PALINDROME_CASES = [
    ("racecar",                          True),
    ("hello",                            False),
    ("A man a plan a canal Panama",      True),
    ("",                                 True),   # empty string
    ("a",                                True),   # single char
    ("Madam",                            True),   # case insensitive
    ("not a palindrome",                 False),
]

failed = 0
for word, expected in PALINDROME_CASES:
    result = is_palindrome(word)
    status = "PASS" if result == expected else "FAIL"
    if status == "FAIL":
        failed += 1
    print(f"  [{status}] is_palindrome({word!r}) == {expected}")

print(f"\n  {len(PALINDROME_CASES) - failed}/{len(PALINDROME_CASES)} cases passed\n")


# =============================================================================
# SECTION 7: Testing with Temporary Files
# =============================================================================

print("=" * 60)
print("SECTION 7: Testing with temporary files")
print("=" * 60)

def count_lines(filepath):
    """Count non-empty lines in a text file."""
    with open(filepath) as f:
        return sum(1 for line in f if line.strip())

def append_to_file(filepath, text):
    """Append a line of text to a file."""
    with open(filepath, 'a') as f:
        f.write(text + "\n")

def test_count_lines_empty_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("\n\n\n")  # only blank lines
        path = f.name
    try:
        assert count_lines(path) == 0
        print("  test_count_lines_empty_file: PASSED")
    finally:
        os.remove(path)  # teardown — always remove

def test_count_lines_normal():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("line one\nline two\n\nline three\n")
        path = f.name
    try:
        assert count_lines(path) == 3  # blank line excluded
        print("  test_count_lines_normal: PASSED")
    finally:
        os.remove(path)

def test_append_to_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("existing line\n")
        path = f.name
    try:
        append_to_file(path, "new line")
        with open(path) as f:
            lines = f.readlines()
        assert len(lines) == 2
        assert lines[1].strip() == "new line"
        print("  test_append_to_file: PASSED")
    finally:
        os.remove(path)

test_count_lines_empty_file()
test_count_lines_normal()
test_append_to_file()
print()


# =============================================================================
# SECTION 8: Test Doubles — Stub, Fake, Spy
# =============================================================================

# Gerard Meszaros's taxonomy:
# Stub  — returns pre-set data, no verification
# Fake  — simplified real implementation (in-memory DB)
# Spy   — wraps real code, records interactions
# Mock  — pre-programmed with expectations (unittest.mock.Mock)

print("=" * 60)
print("SECTION 8: Test doubles — stub, fake, spy")
print("=" * 60)

# Stub — always returns canned data
class StubWeatherAPI:
    def get_temperature(self, city):
        return 22.5  # always sunny, for tests

# Fake — real logic, simplified storage
class FakeUserRepository:
    def __init__(self, seed=None):
        self._db = dict(seed or {})

    def save(self, user_id, user):
        self._db[user_id] = user

    def find(self, user_id):
        if user_id not in self._db:
            raise KeyError(f"User {user_id} not found")
        return self._db[user_id]

# Spy — records calls while delegating to real implementation
class SpyNotifier:
    def __init__(self):
        self.sent = []

    def notify(self, user_id, message):
        # record the interaction
        self.sent.append({"user_id": user_id, "message": message})
        # in a real spy you'd also call the real notifier here

# System under test
class AlertService:
    def __init__(self, weather, users, notifier):
        self.weather  = weather
        self.users    = users
        self.notifier = notifier

    def send_heat_alert(self, user_id, city, threshold=30):
        temp = self.weather.get_temperature(city)
        if temp > threshold:
            user = self.users.find(user_id)
            self.notifier.notify(user_id, f"Heat alert for {user['name']}: {temp}C")
            return True
        return False

def test_heat_alert_not_sent_below_threshold():
    stub    = StubWeatherAPI()     # returns 22.5
    fake_db = FakeUserRepository({1: {"name": "Alice"}})
    spy     = SpyNotifier()
    svc     = AlertService(stub, fake_db, spy)

    result = svc.send_heat_alert(user_id=1, city="London", threshold=30)
    assert result is False
    assert len(spy.sent) == 0
    print("  test_heat_alert_not_sent_below_threshold: PASSED")

def test_heat_alert_sent_above_threshold():
    class HotWeatherStub:
        def get_temperature(self, city):
            return 35.0  # very hot

    fake_db = FakeUserRepository({1: {"name": "Alice"}})
    spy     = SpyNotifier()
    svc     = AlertService(HotWeatherStub(), fake_db, spy)

    result = svc.send_heat_alert(user_id=1, city="Madrid", threshold=30)
    assert result is True
    assert len(spy.sent) == 1
    assert spy.sent[0]["user_id"] == 1
    assert "Alice" in spy.sent[0]["message"]
    print("  test_heat_alert_sent_above_threshold: PASSED")

test_heat_alert_not_sent_below_threshold()
test_heat_alert_sent_above_threshold()
print()


# =============================================================================
# SECTION 9: setUp/tearDown at Class Level — setUpClass / tearDownClass
# =============================================================================

# setUp/tearDown: run before/after EACH test method — expensive to repeat
# setUpClass/tearDownClass: run ONCE per class — for shared expensive setup

print("=" * 60)
print("SECTION 9: setUpClass / tearDownClass")
print("=" * 60)

class TestWithSharedResource(unittest.TestCase):
    """Demonstrates class-level setup for expensive shared resources."""

    @classmethod
    def setUpClass(cls):
        # Called once before any test in this class runs.
        # Use for: DB connections, server startup, large file loading.
        cls.shared_db = FakeUserRepository({
            1: {"name": "Alice", "role": "admin"},
            2: {"name": "Bob",   "role": "user"},
        })
        print("  [setUpClass] Shared DB initialized once.")

    @classmethod
    def tearDownClass(cls):
        # Called once after all tests in this class finish.
        cls.shared_db = None
        print("  [tearDownClass] Shared DB torn down.")

    def test_find_alice(self):
        user = self.shared_db.find(1)
        self.assertEqual(user["name"], "Alice")

    def test_find_bob(self):
        user = self.shared_db.find(2)
        self.assertEqual(user["role"], "user")

    def test_find_missing_raises(self):
        with self.assertRaises(KeyError):
            self.shared_db.find(999)


suite2 = unittest.TestLoader().loadTestsFromTestCase(TestWithSharedResource)
runner2 = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0)
result2 = runner2.run(suite2)
print(f"  TestWithSharedResource: {result2.testsRun} tests, "
      f"{len(result2.failures)} failures")
print()


# =============================================================================
# SECTION 10: doctest — Tests Embedded in Docstrings
# =============================================================================

print("=" * 60)
print("SECTION 10: doctest")
print("=" * 60)

def fibonacci(n):
    """Return the nth Fibonacci number (0-indexed).

    >>> fibonacci(0)
    0
    >>> fibonacci(1)
    1
    >>> fibonacci(7)
    13
    >>> fibonacci(10)
    55
    >>> fibonacci(-1)
    Traceback (most recent call last):
        ...
    ValueError: n must be >= 0
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

import doctest
# Test only the fibonacci function's docstring directly to avoid
# Python 3.9 inspect.unwrap bug when Mock objects are in module scope
results = doctest.run_docstring_examples(fibonacci, globs={"fibonacci": fibonacci},
                                         verbose=False, name="fibonacci")
# run_docstring_examples returns None; run tests manually to count
test_obj = doctest.DocTestFinder().find(fibonacci, name="fibonacci")
runner_obj = doctest.DocTestRunner(verbose=False)
for t in test_obj:
    runner_obj.run(t)
summary = runner_obj.summarize(verbose=False)
print(f"  doctest: {summary.attempted} examples, {summary.failed} failures")
if summary.failed == 0:
    print("  All doctest examples passed.\n")


# =============================================================================
# SECTION 11: Full unittest Run — All Test Classes Together
# =============================================================================

print("=" * 60)
print("SECTION 11: Full test suite run")
print("=" * 60)

# Collect all TestCase subclasses and run them
all_suites = unittest.TestSuite()
for tc in [TestMathFunctions, TestWithSharedResource]:
    all_suites.addTests(unittest.TestLoader().loadTestsFromTestCase(tc))

full_runner = unittest.TextTestRunner(verbosity=2)
final_result = full_runner.run(all_suites)

print()
if final_result.wasSuccessful():
    print("All tests passed.")
else:
    print(f"{len(final_result.failures)} failure(s), {len(final_result.errors)} error(s)")
