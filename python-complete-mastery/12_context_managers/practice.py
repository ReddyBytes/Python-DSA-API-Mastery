# 💻 Context Managers — Practice
# Run with: python3 practice.py

# =============================================================================
# SECTION 1: The Problem Context Managers Solve
# =============================================================================

# Without context managers, cleanup only runs if no exception occurs.
# Context managers make cleanup UNCONDITIONAL — it always runs.

# Simulated resource: a simple "connection" object
class FakeConnection:
    def __init__(self, name):
        self.name = name
        self.is_open = True
        print(f"  [FakeConnection] {name}: opened")

    def query(self, sql):
        if not self.is_open:
            raise RuntimeError("Connection is closed!")
        return f"result of: {sql}"

    def close(self):
        self.is_open = False
        print(f"  [FakeConnection] {self.name}: closed")


print("=" * 60)
print("SECTION 1: Without context managers — resource leak risk")
print("=" * 60)

conn = FakeConnection("no-cm-conn")
try:
    result = conn.query("SELECT 1")
    print(f"  Query result: {result}")
    # If an exception happened here, close() would never be called
    conn.close()
except Exception as e:
    conn.close()  # manual — easy to forget!
    raise

print()


# =============================================================================
# SECTION 2: Class-Based Context Manager — __enter__ / __exit__
# =============================================================================

# Any class that implements __enter__ and __exit__ is a context manager.
# __enter__ runs setup, __exit__ runs cleanup (always).

print("=" * 60)
print("SECTION 2: Class-based context manager (__enter__ / __exit__)")
print("=" * 60)

class ManagedConnection:
    """Context manager that guarantees connection.close() runs."""

    def __init__(self, name):
        self.name = name
        self.conn = None

    def __enter__(self):
        # Setup: create the resource, return it for 'as' binding
        self.conn = FakeConnection(self.name)
        return self.conn  # this becomes the 'as conn' variable

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup: ALWAYS runs, even if an exception occurred in the body.
        # exc_type is None when no exception; non-None when there's an error.
        if self.conn:
            self.conn.close()
        if exc_type:
            print(f"  [ManagedConnection] Exception suppressed? No — {exc_type.__name__}")
        # Return False (or None) to let exceptions propagate normally.
        # Return True to SUPPRESS the exception (use carefully!).
        return False

# Clean use: no exception
with ManagedConnection("cm-conn-1") as conn:
    print(f"  Query: {conn.query('SELECT name FROM users')}")
print("  Connection closed, no exception.\n")

# Demonstrates __exit__ is called even on exception
print("Demonstrating cleanup on exception:")
try:
    with ManagedConnection("cm-conn-2") as conn:
        print(f"  Query: {conn.query('SELECT 1')}")
        raise ValueError("Simulated error mid-block!")
except ValueError as e:
    print(f"  Caught: {e}")
print()


# =============================================================================
# SECTION 3: Suppressing Exceptions in __exit__
# =============================================================================

print("=" * 60)
print("SECTION 3: Suppressing exceptions — return True from __exit__")
print("=" * 60)

class SuppressErrors:
    """Context manager that swallows specified exception types.
    This is the pattern behind contextlib.suppress()."""

    def __init__(self, *exception_types):
        # Store which exceptions we are allowed to suppress
        self.exception_types = exception_types

    def __enter__(self):
        return self  # nothing to set up; return self for 'as' binding

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Only suppress if the exception is one we were told to handle
        if exc_type and issubclass(exc_type, self.exception_types):
            print(f"  [SuppressErrors] Suppressed: {exc_type.__name__}: {exc_val}")
            return True  # returning True tells Python: don't re-raise
        return False  # unknown exception: let it propagate


# FileNotFoundError is suppressed
print("Attempting to remove a nonexistent key:")
cache = {"a": 1, "b": 2}
with SuppressErrors(KeyError):
    del cache["nonexistent"]  # would raise KeyError without suppression
print("  Execution continued normally after suppressed KeyError")

# Other errors still propagate
print("\nOther exceptions still propagate:")
try:
    with SuppressErrors(KeyError):
        raise ValueError("This is NOT suppressed")
except ValueError as e:
    print(f"  Correctly propagated: {e}")
print()


# =============================================================================
# SECTION 4: @contextmanager — Generator-Based Context Managers
# =============================================================================

# The @contextmanager decorator transforms a generator function into a context
# manager. Code before `yield` = __enter__, code after `yield` = __exit__.
# The `try/finally` ensures cleanup runs even if the body raises.

from contextlib import contextmanager

print("=" * 60)
print("SECTION 4: @contextmanager decorator")
print("=" * 60)

@contextmanager
def managed_connection(name):
    """Generator-based equivalent of ManagedConnection class above."""
    conn = FakeConnection(name)  # setup (before yield)
    try:
        yield conn               # body runs here; conn = the 'as' variable
    finally:
        conn.close()             # cleanup (always runs, even on exception)

with managed_connection("gen-conn") as conn:
    print(f"  Query: {conn.query('SELECT * FROM orders')}")
print("  (Connection closed by finally)\n")


# Timer context manager — a classic real-world example
import time

@contextmanager
def timer(label):
    """Measure and print elapsed time for a block of code."""
    start = time.perf_counter()
    try:
        yield  # no value needed; we're just timing
    finally:
        elapsed = time.perf_counter() - start
        print(f"  [{label}] completed in {elapsed:.4f}s")

print("Using timer context manager:")
with timer("list comprehension"):
    result = [i ** 2 for i in range(10_000)]
print(f"  Generated {len(result)} squares\n")


# Transaction context manager — commit on success, rollback on failure
class FakeDB:
    """Minimal fake DB to demonstrate transaction management."""
    def __init__(self):
        self.log = []

    def execute(self, sql):
        self.log.append(sql)
        print(f"    DB.execute: {sql}")

@contextmanager
def transaction(db):
    """Auto-commit on clean exit; rollback if exception occurs."""
    db.execute("BEGIN")
    try:
        yield db
        db.execute("COMMIT")      # only reached if no exception
    except Exception:
        db.execute("ROLLBACK")    # exception path
        raise                     # re-raise — don't swallow the error

db = FakeDB()
print("Successful transaction:")
with transaction(db) as conn:
    conn.execute("INSERT INTO orders VALUES (1, 'widget')")
    conn.execute("UPDATE inventory SET qty = qty - 1 WHERE id = 1")
print()

print("Failed transaction (auto-rollback):")
try:
    with transaction(db) as conn:
        conn.execute("INSERT INTO orders VALUES (2, 'gadget')")
        raise RuntimeError("Payment declined!")
except RuntimeError as e:
    print(f"  Caught: {e}")
print()


# =============================================================================
# SECTION 5: contextlib Utilities — suppress, redirect_stdout, nullcontext
# =============================================================================

from contextlib import suppress, redirect_stdout, nullcontext
import io
import os

print("=" * 60)
print("SECTION 5: contextlib utilities")
print("=" * 60)

# suppress() — idiomatic way to ignore specific exceptions
print("contextlib.suppress:")
with suppress(FileNotFoundError):
    os.remove("/tmp/this_file_does_not_exist_12345.txt")
print("  os.remove silently skipped (file not found)")

with suppress(KeyError, IndexError):
    data = {}
    _ = data["missing_key"]
print("  Dict access silently skipped (key not found)\n")


# redirect_stdout — capture or redirect print() output
print("contextlib.redirect_stdout:")

def legacy_function_that_prints():
    print("  I am the legacy function speaking!")
    print("  I cannot be changed to return values.")

buffer = io.StringIO()
with redirect_stdout(buffer):
    legacy_function_that_prints()  # output goes to buffer, not console

captured = buffer.getvalue()
print(f"  Captured output: {captured.strip()!r}\n")


# nullcontext — useful when a context manager is optional
print("contextlib.nullcontext (optional locking pattern):")
import threading

lock = threading.Lock()

def process_data(data, use_lock=True):
    # nullcontext() is a no-op context manager — lets us write one path
    # that works with or without an actual context manager
    ctx = lock if use_lock else nullcontext()
    with ctx:
        return [x * 2 for x in data]

print(f"  With lock:    {process_data([1, 2, 3], use_lock=True)}")
print(f"  Without lock: {process_data([1, 2, 3], use_lock=False)}")
print()


# =============================================================================
# SECTION 6: Nested Context Managers
# =============================================================================

print("=" * 60)
print("SECTION 6: Nested and multiple context managers")
print("=" * 60)

import tempfile

# Old style — nested with blocks
print("Nested style (verbose):")
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f1:
    f1.write("line 1\nline 2\n")
    tmp_path = f1.name
print(f"  Wrote to: {tmp_path}")

# Modern one-liner — comma-separated in a single with
print("\nModern style (one-liner):")
buffer_a = io.StringIO("alpha content")
buffer_b = io.StringIO()

with redirect_stdout(buffer_b), suppress(AttributeError):
    # both context managers active simultaneously
    print("inside both context managers at once")

print(f"  Captured: {buffer_b.getvalue().strip()!r}")

# Cleanup temp file
with suppress(FileNotFoundError):
    os.remove(tmp_path)

# Exit order is LIFO — last opened, first closed
print("\nExit order demonstration (LIFO):")

class Tracked:
    def __init__(self, name):
        self.name = name
    def __enter__(self):
        print(f"  ENTER: {self.name}")
        return self
    def __exit__(self, *args):
        print(f"  EXIT:  {self.name}")

with Tracked("A") as a, Tracked("B") as b, Tracked("C") as c:
    print("  (inside with block)")
# Exit order: C, then B, then A
print()


# =============================================================================
# SECTION 7: ExitStack — Dynamic Context Manager Composition
# =============================================================================

from contextlib import ExitStack

print("=" * 60)
print("SECTION 7: ExitStack — dynamic number of context managers")
print("=" * 60)

# Use when you don't know how many context managers you need at write time.
# ExitStack tracks them all and cleans them up in reverse order.

def process_buffers(texts):
    """Open a dynamic number of StringIO buffers and process them."""
    with ExitStack() as stack:
        # enter_context() registers each one and returns the 'as' value
        buffers = [stack.enter_context(io.StringIO(t)) for t in texts]
        combined = " | ".join(b.read() for b in buffers)
    # All buffers are "closed" here
    return combined

texts = ["first", "second", "third"]
result = process_buffers(texts)
print(f"  Combined: {result!r}")

# ExitStack.callback() — register arbitrary cleanup functions
print("\nExitStack.callback() pattern:")
with ExitStack() as stack:
    stack.callback(print, "  [callback] first registered — runs last")
    stack.callback(print, "  [callback] second registered — runs first (LIFO)")
    print("  (inside ExitStack block)")
print()


# =============================================================================
# SECTION 8: Real-World Pattern — Managed Temp Directory
# =============================================================================

import shutil
import pathlib

print("=" * 60)
print("SECTION 8: Real-world — managed temporary directory")
print("=" * 60)

@contextmanager
def temp_directory():
    """Create a temporary directory and clean it up on exit.
    Useful for integration tests or processing pipelines that write scratch files."""
    path = pathlib.Path(tempfile.mkdtemp())
    print(f"  Created temp dir: {path}")
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
        print(f"  Cleaned up temp dir: {path}")

with temp_directory() as d:
    # Write a few files
    (d / "report.txt").write_text("Q4 results: 42\n")
    (d / "data.csv").write_text("name,score\nAlice,95\nBob,87\n")
    files = list(d.iterdir())
    print(f"  Files created: {[f.name for f in files]}")

print("  (temp dir no longer exists)\n")


# =============================================================================
# SECTION 9: Gotcha Showcase — Common Mistakes
# =============================================================================

print("=" * 60)
print("SECTION 9: Gotcha — missing try/finally in @contextmanager")
print("=" * 60)

# GOTCHA: forgetting try/finally means cleanup doesn't run on exception

@contextmanager
def leaky(name):
    conn = FakeConnection(name)
    yield conn             # If body raises, close() is NEVER called!
    conn.close()           # NOT reached on exception — resource leak!

@contextmanager
def safe(name):
    conn = FakeConnection(name)
    try:
        yield conn
    finally:
        conn.close()       # ALWAYS reached — no leak

print("Leaky (exception case — close() skipped):")
try:
    with leaky("leaky-conn") as conn:
        raise RuntimeError("boom")
except RuntimeError:
    pass
print("  (close() was never called — leak!)\n")

print("Safe (exception case — close() guaranteed):")
try:
    with safe("safe-conn") as conn:
        raise RuntimeError("boom")
except RuntimeError:
    pass
print("  (close() was called despite exception)\n")


# =============================================================================
# SECTION 10: Reentrant and One-Shot Context Managers
# =============================================================================

print("=" * 60)
print("SECTION 10: One-shot vs reentrant context managers")
print("=" * 60)

# Most context managers are one-shot — reusing them is undefined behavior.
# threading.Lock is a reentrant example (with RLock).
import threading

lock = threading.Lock()
rlock = threading.RLock()

# RLock can be acquired multiple times by the same thread
with rlock:
    with rlock:  # nested — works with RLock, deadlocks with Lock
        print("  RLock: nested acquisition succeeded")

print()
print("All context manager examples complete.")
