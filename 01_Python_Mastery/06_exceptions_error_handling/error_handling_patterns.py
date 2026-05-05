"""
06_exceptions_error_handling/error_handling_patterns.py
=========================================================
CONCEPT: Production-grade error handling patterns.
WHY THIS MATTERS: 90% of production bugs are in error handling code —
not in the happy path. Retry logic, circuit breakers, fallbacks, and
structured logging of errors are what separate a toy app from a real system.

Prerequisite: Modules 01–05, custom_exceptions.py
"""

import time
import functools
import logging
from typing import TypeVar, Callable, Optional, Any

T = TypeVar("T")

# =============================================================================
# SECTION 1: The try/except/else/finally quadrant
# =============================================================================

# CONCEPT: Python's try block has 4 clauses:
# try:      the code that might fail
# except:   what to do when it fails (can have multiple, specific first)
# else:     runs ONLY if no exception was raised (clean success path)
# finally:  ALWAYS runs — cleanup that must happen regardless of outcome
# WHY else: separates "this ran successfully" logic from error handling logic.
# WHY finally: ensures resources are released even if exceptions occur.

print("=== Section 1: try/except/else/finally ===")

def load_config(filepath: str) -> dict:
    """
    Demonstrates all four clauses with a real-world file loading scenario.
    """
    file_handle = None
    try:
        file_handle = open(filepath, "r")       # might raise FileNotFoundError
        content = file_handle.read()            # might raise IOError
        config = {}                             # parse simulation
        for line in content.splitlines():
            if "=" in line:
                key, _, value = line.partition("=")
                config[key.strip()] = value.strip()
        # No exception? Execution falls into `else`

    except FileNotFoundError:
        # SPECIFIC exception first — gives caller a clear error
        print(f"  Config file not found: {filepath}")
        return {}

    except PermissionError:
        print(f"  No permission to read: {filepath}")
        return {}

    except Exception as e:
        # GENERAL catch-all LAST — catches anything not handled above
        print(f"  Unexpected error reading config: {e}")
        return {}

    else:
        # Runs ONLY if NO exception occurred — the success path
        print(f"  Config loaded successfully: {len(config)} keys")
        return config

    finally:
        # ALWAYS runs — whether success or failure
        # Use for cleanup: close files, release locks, stop timers
        if file_handle:
            file_handle.close()
            print(f"  File handle closed (finally block)")

# Create a real test file
import tempfile, os
with tempfile.NamedTemporaryFile(mode="w", suffix=".cfg", delete=False) as f:
    f.write("host = localhost\nport = 5432\ndebug = true\n")
    tmp_path = f.name

result = load_config(tmp_path)
print(f"  Loaded: {result}")

result = load_config("/nonexistent/path/config.cfg")
print(f"  Missing file: {result}")
os.unlink(tmp_path)   # cleanup


# =============================================================================
# SECTION 2: Retry decorator with exponential backoff
# =============================================================================

# CONCEPT: Network calls, API requests, and DB queries can fail transiently.
# Retrying with exponential backoff (wait 1s, 2s, 4s...) is standard practice.
# The backoff prevents overwhelming a struggling service (thundering herd problem).
# This pattern is used by every HTTP client library.

print("\n=== Section 2: Retry with Exponential Backoff ===")

def retry(
    max_attempts: int = 3,
    exceptions: tuple = (Exception,),
    base_delay: float = 0.1,
    backoff: float = 2.0
):
    """
    Parameterized retry decorator.
    max_attempts: how many total tries (including the first)
    exceptions:   which exception types to retry on
    base_delay:   seconds to wait after first failure
    backoff:      multiply delay by this after each failure (exponential)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)   # try the call
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        break   # no more retries, fall through to re-raise
                    delay = base_delay * (backoff ** (attempt - 1))
                    print(f"  Attempt {attempt}/{max_attempts} failed: {e}. Retrying in {delay:.2f}s")
                    time.sleep(delay)
            print(f"  All {max_attempts} attempts exhausted.")
            raise last_exception   # re-raise the last exception
        return wrapper
    return decorator


# Simulate a flaky external service
_call_count = [0]

@retry(max_attempts=4, exceptions=(ConnectionError,), base_delay=0.01, backoff=2.0)
def call_payment_api(amount: float) -> dict:
    """Simulates a flaky API that succeeds on the 3rd attempt."""
    _call_count[0] += 1
    if _call_count[0] < 3:
        raise ConnectionError(f"Connection timeout (attempt {_call_count[0]})")
    return {"status": "success", "amount": amount, "transaction_id": "TXN-001"}

result = call_payment_api(99.99)
print(f"  Final result: {result}")


# =============================================================================
# SECTION 3: Circuit breaker pattern
# =============================================================================

# CONCEPT: After N consecutive failures, the circuit "opens" and IMMEDIATELY
# rejects all calls without trying. After a timeout, it "half-opens" to test
# if the service recovered. Used in microservices to prevent cascading failures.
# STATES: CLOSED (normal) → OPEN (rejecting) → HALF_OPEN (testing) → CLOSED

print("\n=== Section 3: Circuit Breaker ===")

class CircuitBreakerError(Exception):
    """Raised when the circuit is open — call rejected without trying."""
    pass

class CircuitBreaker:
    CLOSED    = "CLOSED"     # normal operation
    OPEN      = "OPEN"       # rejecting all calls
    HALF_OPEN = "HALF_OPEN"  # testing if service recovered

    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 5.0):
        self.threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._state = self.CLOSED
        self._failures = 0
        self._last_failure_time = 0.0

    @property
    def state(self): return self._state

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Wraps a function call with circuit breaker logic.
        OPEN state: raises CircuitBreakerError immediately (no call)
        HALF_OPEN: tries once — success → CLOSED, failure → OPEN again
        CLOSED: calls normally, tracks failures
        """
        if self._state == self.OPEN:
            # Check if recovery timeout has elapsed
            elapsed = time.time() - self._last_failure_time
            if elapsed >= self.recovery_timeout:
                print(f"  Circuit: OPEN → HALF_OPEN (testing recovery)")
                self._state = self.HALF_OPEN
            else:
                raise CircuitBreakerError(
                    f"Circuit is OPEN (retry in {self.recovery_timeout - elapsed:.1f}s)"
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        if self._state == self.HALF_OPEN:
            print(f"  Circuit: HALF_OPEN → CLOSED (service recovered)")
        self._state = self.CLOSED
        self._failures = 0

    def _on_failure(self):
        self._failures += 1
        self._last_failure_time = time.time()
        if self._failures >= self.threshold:
            if self._state != self.OPEN:
                print(f"  Circuit: {self._state} → OPEN (threshold reached)")
            self._state = self.OPEN


# Simulate a service that's down, then recovers
breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)

def unreliable_service(call_num):
    if call_num <= 4:
        raise RuntimeError(f"Service unavailable (call {call_num})")
    return f"Success! (call {call_num})"

for i in range(1, 9):
    try:
        result = breaker.call(unreliable_service, i)
        print(f"  Call {i}: {result} [circuit: {breaker.state}]")
    except CircuitBreakerError as e:
        print(f"  Call {i}: REJECTED (circuit open) — {e}")
    except RuntimeError as e:
        print(f"  Call {i}: FAILED — {e} [circuit: {breaker.state}]")
    if i == 5:
        time.sleep(0.15)   # wait for recovery timeout


# =============================================================================
# SECTION 4: Context managers for exception safety
# =============================================================================

# CONCEPT: Context managers (the `with` statement) guarantee cleanup even
# when exceptions occur. They're the right way to handle any "acquire → use → release"
# pattern: files, DB connections, locks, transactions.

print("\n=== Section 4: Exception-Safe Context Managers ===")

from contextlib import contextmanager, suppress

# contextlib.suppress: silently ignore specific exceptions
# WHY: sometimes you genuinely want to ignore an error (e.g., deleting a file
# that might not exist) and writing try/except just for pass is verbose.

print("suppress example:")
with suppress(FileNotFoundError):
    os.remove("/tmp/nonexistent_file_xyz.txt")
    # If file doesn't exist, FileNotFoundError is suppressed silently
print("  No error raised (suppress silenced FileNotFoundError)")

# Build a transaction context manager
@contextmanager
def database_transaction(db_name: str):
    """
    Simulates a DB transaction. Commits on success, rolls back on exception.
    The finally block runs in BOTH cases — essential for cleanup.
    """
    print(f"  BEGIN TRANSACTION ({db_name})")
    transaction_log = []
    try:
        yield transaction_log   # caller gets the transaction object
        # If we reach here, no exception was raised — commit
        print(f"  COMMIT ({len(transaction_log)} operations)")
    except Exception as e:
        # Exception occurred — roll back
        print(f"  ROLLBACK (due to: {e})")
        raise   # re-raise so caller knows it failed
    finally:
        print(f"  Connection closed (finally block always runs)")

# Success path
print("\nSuccessful transaction:")
try:
    with database_transaction("users_db") as txn:
        txn.append("INSERT user Alice")
        txn.append("INSERT user Bob")
        # No exception → COMMIT

except Exception:
    pass

# Failure path
print("\nFailed transaction:")
try:
    with database_transaction("payments_db") as txn:
        txn.append("INSERT payment $99")
        raise ValueError("Payment gateway timeout")
        txn.append("UPDATE balance")   # never reached
except ValueError:
    print("  Caller received the exception after rollback")


# =============================================================================
# SECTION 5: Structured error responses for APIs
# =============================================================================

# CONCEPT: In REST APIs, exceptions should become structured HTTP responses.
# This layer translates between Python exceptions and JSON error responses.
# Use a central handler to avoid duplicating error-to-response logic everywhere.

print("\n=== Section 5: API Error Handler Pattern ===")

# Simulate the AppError hierarchy from custom_exceptions.py
class APIError(Exception):
    def __init__(self, message, code="error", status=500):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status

class NotFoundError(APIError):
    def __init__(self, resource):
        super().__init__(f"{resource} not found", code="not_found", status=404)

class BadRequestError(APIError):
    def __init__(self, message, field=None):
        super().__init__(message, code="bad_request", status=400)
        self.field = field


def handle_api_error(func: Callable) -> Callable:
    """
    Decorator: catches domain exceptions and converts them to API response dicts.
    Applied to all route handlers — they can raise domain exceptions freely,
    and this layer ensures a clean JSON response always comes back.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return {"status": 200, "data": result}

        except NotFoundError as e:
            return {"status": 404, "error": {"code": e.code, "message": e.message}}

        except BadRequestError as e:
            error = {"code": e.code, "message": e.message}
            if hasattr(e, "field") and e.field:
                error["field"] = e.field
            return {"status": 400, "error": error}

        except APIError as e:
            return {"status": e.status, "error": {"code": e.code, "message": e.message}}

        except Exception as e:
            # Never let unexpected exceptions leak to users
            logging.exception("Unexpected error in route handler")
            return {"status": 500, "error": {"code": "internal_error",
                                             "message": "An unexpected error occurred"}}
    return wrapper

# Route handlers that raise domain exceptions freely
@handle_api_error
def get_user(user_id: int):
    if user_id == 0:
        raise BadRequestError("User ID must be positive", field="user_id")
    if user_id > 100:
        raise NotFoundError(f"User {user_id}")
    return {"id": user_id, "name": f"User_{user_id}"}

@handle_api_error
def delete_user(user_id: int):
    if user_id > 100:
        raise NotFoundError(f"User {user_id}")
    if user_id == 1:
        raise APIError("Cannot delete admin user", code="forbidden", status=403)
    return {"deleted": True, "user_id": user_id}

print("GET /users/42:", get_user(42))
print("GET /users/0: ", get_user(0))
print("GET /users/999:", get_user(999))
print("DELETE /users/200:", delete_user(200))
print("DELETE /users/1:",   delete_user(1))


print("\n=== Error handling patterns complete ===")
print("Production error handling checklist:")
print("  1. else: block for success-only logic, finally: for cleanup")
print("  2. Retry with exponential backoff for transient failures")
print("  3. Circuit breaker to stop hammering a broken service")
print("  4. Context managers for exception-safe resource management")
print("  5. Central error handler translates domain exceptions → API responses")
print("  6. Never catch Exception silently — always log or re-raise")
