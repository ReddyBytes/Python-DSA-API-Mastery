"""
12_context_managers/custom_context_manager.py
===============================================
CONCEPT: Context managers — the `with` statement and the __enter__/__exit__
protocol that powers it.
WHY THIS MATTERS: Context managers guarantee cleanup. Files get closed,
locks get released, DB transactions commit or rollback, timers stop —
regardless of whether an exception occurred. They're the "RAII pattern"
of Python, and are the correct solution to any "acquire → use → release" problem.

Prerequisite: Modules 01–11
"""

import time
import threading
import tempfile
from contextlib import contextmanager, suppress, ExitStack
from pathlib import Path

# =============================================================================
# SECTION 1: Class-based context managers — __enter__ and __exit__
# =============================================================================

# CONCEPT: Any class with __enter__ and __exit__ works with `with`.
# __enter__: called at the start of the `with` block, returns the `as` value
# __exit__(exc_type, exc_val, exc_tb): called at end, even if exception occurred
# If __exit__ returns True, the exception is suppressed. Return None/False to let it propagate.

print("=== Section 1: Class-Based Context Manager ===")

class Timer:
    """
    Context manager that measures execution time of a code block.
    WHY: timing any block of code without boilerplate.
    """

    def __init__(self, label: str = ""):
        self.label    = label or "Block"
        self.elapsed  = None

    def __enter__(self):
        """Called when entering the `with` block. Returns self (the timer)."""
        self._start = time.perf_counter()
        return self   # becomes the `as` target: `with Timer() as t:`

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called when leaving the `with` block — always, even if exception.
        exc_type, exc_val, exc_tb: exception info (all None if no exception)
        Return True to SUPPRESS the exception. Return None/False to let it propagate.
        """
        self.elapsed = time.perf_counter() - self._start
        print(f"  [{self.label}] elapsed: {self.elapsed*1000:.2f}ms")
        return False   # don't suppress exceptions


with Timer("database query") as t:
    time.sleep(0.05)   # simulate DB work
    result = sum(range(100_000))

print(f"  result: {result:,}")
print(f"  elapsed attribute: {t.elapsed*1000:.2f}ms")


# Context manager that handles exceptions
class ManagedFile:
    """
    File context manager that logs access and handles errors.
    Better version of what `open()` does internally.
    """

    def __init__(self, path: str, mode: str = "r"):
        self.path = path
        self.mode = mode
        self._file = None

    def __enter__(self):
        print(f"  Opening {self.path}")
        self._file = open(self.path, self.mode)
        return self._file   # the file object is the `as` value

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file:
            self._file.close()
            print(f"  Closed {self.path}")

        if exc_type is FileNotFoundError:
            print(f"  Handled FileNotFoundError for {self.path}")
            return True   # suppress this specific exception

        return False   # let other exceptions propagate

tmp = Path(tempfile.mkdtemp()) / "test.txt"
tmp.write_text("Hello from context manager")

with ManagedFile(str(tmp)) as f:
    content = f.read()
    print(f"  Read: {content}")

# Test exception suppression
with ManagedFile("/nonexistent/file.txt") as f:
    pass  # FileNotFoundError suppressed


# =============================================================================
# SECTION 2: Generator-based context managers with @contextmanager
# =============================================================================

# CONCEPT: @contextmanager turns a generator function into a context manager.
# Code BEFORE yield = __enter__. Code AFTER yield = __exit__.
# The yield value becomes the `as` target.
# This is cleaner than writing a class for most cases.

print("\n=== Section 2: @contextmanager ===")

@contextmanager
def managed_temp_dir(prefix: str = "cm_"):
    """
    Creates a temp directory, provides it, then cleans up.
    yield: what the `as` variable receives
    finally: runs regardless of exception — guaranteed cleanup
    """
    import tempfile, shutil
    tmpdir = Path(tempfile.mkdtemp(prefix=prefix))
    print(f"  Created temp dir: {tmpdir.name}")
    try:
        yield tmpdir   # caller gets the path
    finally:
        shutil.rmtree(tmpdir)   # ALWAYS clean up, even if exception
        print(f"  Cleaned up: {tmpdir.name}")

with managed_temp_dir("work_") as work_dir:
    (work_dir / "output.txt").write_text("Processing result")
    (work_dir / "log.txt").write_text("DEBUG: completed")
    files = list(work_dir.iterdir())
    print(f"  Files created: {[f.name for f in files]}")

# tmpdir is gone after the with block


@contextmanager
def database_transaction(connection_name: str):
    """
    Simulates a database transaction context manager.
    Commits on success, rolls back on exception.
    This is what SQLAlchemy's session.begin() does.
    """
    ops = []
    print(f"  BEGIN TRANSACTION [{connection_name}]")
    try:
        yield ops   # caller appends operations to this list
        # No exception? Commit
        print(f"  COMMIT [{connection_name}] ({len(ops)} operations)")
    except Exception as e:
        print(f"  ROLLBACK [{connection_name}] (cause: {type(e).__name__}: {e})")
        raise   # re-raise — don't swallow exceptions silently!
    finally:
        print(f"  CONNECTION CLOSED [{connection_name}]")

# Success case
print("\nSuccessful transaction:")
with database_transaction("users_db") as ops:
    ops.append("INSERT user Alice")
    ops.append("INSERT user Bob")

# Failure case
print("\nFailed transaction:")
try:
    with database_transaction("payments_db") as ops:
        ops.append("INSERT payment $99")
        raise ConnectionError("DB server unreachable")
except ConnectionError:
    print("  Caller caught the re-raised exception")


# =============================================================================
# SECTION 3: contextlib utilities — suppress, redirect, ExitStack
# =============================================================================

# CONCEPT: contextlib provides pre-built context managers for common patterns.

print("\n=== Section 3: contextlib Utilities ===")

# suppress: silently ignore specific exceptions
print("contextlib.suppress:")
with suppress(FileNotFoundError, PermissionError):
    open("/nonexistent/path.txt")
print("  No exception — FileNotFoundError suppressed")

# redirect_stdout: capture print output
import io
from contextlib import redirect_stdout

print("\nredirect_stdout (capture output):")
output_buffer = io.StringIO()
with redirect_stdout(output_buffer):
    print("This goes to the buffer, not console")
    print("So does this")

captured = output_buffer.getvalue()
print(f"  Captured: {captured.splitlines()}")

# ExitStack: manage a dynamic number of context managers
print("\nExitStack (dynamic context managers):")
from contextlib import ExitStack

files_to_process = ["a.txt", "b.txt", "c.txt"]
tmp_dir = Path(tempfile.mkdtemp())
for name in files_to_process:
    (tmp_dir / name).write_text(f"Content of {name}")

with ExitStack() as stack:
    # Open an unknown number of files — ExitStack ensures all are closed
    file_handles = [
        stack.enter_context(open(tmp_dir / name))
        for name in files_to_process
    ]
    contents = [f.read() for f in file_handles]
    print(f"  Opened {len(file_handles)} files simultaneously")
    print(f"  Contents: {contents}")
# All files closed when ExitStack exits


# =============================================================================
# SECTION 4: Real-world context managers
# =============================================================================

print("\n=== Section 4: Real-World Patterns ===")

# 1. Lock context manager (thread safety)
_lock = threading.Lock()

@contextmanager
def locked_operation(resource_name: str):
    """Acquire a lock, perform operation, release regardless of outcome."""
    print(f"  Acquiring lock for {resource_name}")
    acquired = _lock.acquire(timeout=2.0)
    if not acquired:
        raise TimeoutError(f"Could not acquire lock for {resource_name}")
    try:
        yield
    finally:
        _lock.release()
        print(f"  Released lock for {resource_name}")

with locked_operation("shared_counter"):
    print("  Doing thread-safe work...")

# 2. HTTP session context manager (retryable)
@contextmanager
def managed_api_session(base_url: str, timeout: float = 30.0):
    """
    Manages an HTTP session lifecycle.
    Ensures session is closed even if requests fail.
    WHY: unclosed sessions = connection pool exhaustion in production.
    """
    session_id = f"sess_{int(time.time())}"
    print(f"  Session [{session_id}] opened → {base_url}")
    try:
        # In real code: yield requests.Session() or httpx.AsyncClient()
        yield {"session_id": session_id, "base_url": base_url}
    except Exception as e:
        print(f"  Session [{session_id}] error: {e}")
        raise
    finally:
        print(f"  Session [{session_id}] closed")

with managed_api_session("https://api.example.com") as session:
    print(f"  Making request via {session['session_id']}")

# 3. Context manager for audit logging
@contextmanager
def audit_log(action: str, user_id: int):
    """
    Wraps an operation with audit trail logging.
    Logs start, completion, and any failure.
    """
    import datetime
    started_at = datetime.datetime.utcnow()
    print(f"  AUDIT: {action} started by user {user_id} at {started_at.isoformat()}")
    try:
        yield
        completed_at = datetime.datetime.utcnow()
        duration_ms = (completed_at - started_at).total_seconds() * 1000
        print(f"  AUDIT: {action} COMPLETED in {duration_ms:.1f}ms")
    except Exception as e:
        print(f"  AUDIT: {action} FAILED: {type(e).__name__}: {e}")
        raise

with audit_log("delete_user", user_id=1):
    time.sleep(0.01)   # simulate operation


print("\n=== Context managers complete ===")
print("When to build a context manager:")
print("  1. Any resource that needs cleanup: files, locks, DB connections")
print("  2. Transactions: begin → commit/rollback")
print("  3. Timers and benchmarks")
print("  4. Temporary state changes (redirect stdout, mock patches)")
print("  5. Audit logging around operations")
print()
print("Quick guide:")
print("  Simple, with cleanup logic → @contextmanager (generator)")
print("  Needs to store state between enter/exit → class-based")
print("  Many pre-built patterns → contextlib.suppress, redirect_stdout, ExitStack")
