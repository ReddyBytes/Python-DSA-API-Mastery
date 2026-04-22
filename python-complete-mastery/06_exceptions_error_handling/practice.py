"""
==============================================================================
MODULE 06 — Exceptions & Error Handling
==============================================================================
Run with: python3 practice.py

Story: You are building payment infrastructure for an e-commerce platform.
A cascade of things can go wrong: bad input, network failure, insufficient funds,
missing records. This file walks you from basic exception mechanics all the way
to production-grade patterns used by teams processing millions of transactions.

Concepts covered:
  - try / except / else / finally anatomy
  - Catching multiple exceptions
  - Exception hierarchy (BaseException → Exception → specific)
  - raise, re-raise, raise ... from (exception chaining)
  - Custom exception class hierarchies
  - Context managers and __enter__ / __exit__
  - logging exceptions correctly
  - LBYL vs EAFP philosophy
  - Common anti-patterns and how to fix them
  - Retry / graceful degradation patterns
==============================================================================
"""

import logging
import time
import random

# ---------------------------------------------------------------------------
# Basic logging setup — used throughout to show proper exception logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)-8s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)


# ==============================================================================
# CONCEPT 1: The full try / except / else / finally anatomy
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 1: try / except / else / finally")
print("="*60)

def divide(a, b):
    """
    Shows the full four-block structure.

    - try:     code that might raise
    - except:  runs ONLY if an exception occurred
    - else:    runs ONLY if NO exception occurred (success path)
    - finally: ALWAYS runs — cleanup, release resources, etc.

    Why 'else' matters: anything placed inside 'else' cannot accidentally
    mask exceptions from the try block. If 'process(result)' also raises
    ValueError, you'd catch it unintentionally without 'else'.
    """
    try:
        result = a / b                  # only this line can raise ZeroDivisionError
    except ZeroDivisionError as e:
        print(f"  [except] Cannot divide by zero: {e}")
        return None
    else:
        # Runs only when try block succeeds
        print(f"  [else]   Success! {a} / {b} = {result:.4f}")
        return result
    finally:
        # Runs regardless of success or failure — like a lock release
        print(f"  [finally] Cleanup for divide({a}, {b})")

divide(10, 3)
print()
divide(10, 0)


# ==============================================================================
# CONCEPT 2: Catching multiple exception types
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 2: Catching multiple exceptions")
print("="*60)

def parse_and_compute(raw_value, divisor):
    """
    Two separate except blocks give you different recovery paths.
    Tuple syntax (ValueError, TypeError) shares one handler when recovery is identical.

    Order matters: put SPECIFIC exceptions BEFORE generic ones.
    Parent classes (like Exception) catch all children — if listed first,
    specific except clauses below become dead code.
    """
    # --- Two separate except clauses for different recovery logic ---
    try:
        number = int(raw_value)     # ValueError if raw_value is "abc"
        result = 100 / number       # ZeroDivisionError if number == 0
    except ValueError:
        print(f"  '{raw_value}' is not a valid integer — defaulting to 1")
        number = 1
        result = 100 / divisor
    except ZeroDivisionError:
        print(f"  Cannot divide by zero — returning None")
        return None
    except Exception as e:
        # Catch-all fallback: always log, never silently swallow
        logger.exception("Unexpected error in parse_and_compute")
        raise   # re-raise so caller knows something went wrong
    else:
        print(f"  Parsed {raw_value!r} → {number}, result = {result}")
    return result

parse_and_compute("5", 2)
parse_and_compute("abc", 2)
parse_and_compute("0", 2)

# --- Tuple syntax when both exceptions mean the same recovery ---
print()
def safe_lookup(data, key):
    """Tuple syntax: same handler for both lookup failures."""
    try:
        value = data[key]       # KeyError if missing
        return int(value)       # ValueError if value can't be cast
    except (KeyError, ValueError) as e:
        print(f"  Lookup failed ({type(e).__name__}): {e} — returning 0")
        return 0

inventory = {"apples": "42", "bananas": "bad_data"}
print(safe_lookup(inventory, "apples"))
print(safe_lookup(inventory, "grapes"))     # KeyError
print(safe_lookup(inventory, "bananas"))    # ValueError


# ==============================================================================
# CONCEPT 3: The exception hierarchy — what 'except Exception' really catches
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 3: Exception hierarchy")
print("="*60)

"""
BaseException
 ├── SystemExit          ← sys.exit() — do NOT catch unless intentional
 ├── KeyboardInterrupt   ← Ctrl+C — do NOT swallow
 └── Exception           ← everything else you normally handle
      ├── ArithmeticError
      │    └── ZeroDivisionError
      ├── LookupError
      │    ├── IndexError
      │    └── KeyError
      ├── ValueError
      ├── TypeError
      ├── OSError
      │    └── FileNotFoundError
      └── RuntimeError
           └── RecursionError
"""

def demonstrate_hierarchy():
    errors = [
        lambda: 1 / 0,                         # ZeroDivisionError
        lambda: int("abc"),                    # ValueError
        lambda: [1, 2, 3][99],                 # IndexError
        lambda: {"a": 1}["missing"],           # KeyError
        lambda: open("/no/such/file.txt"),     # FileNotFoundError
        lambda: "hello" + 5,                   # TypeError
    ]

    for fn in errors:
        try:
            fn()
        except ZeroDivisionError as e:
            # Most specific first — catches before ArithmeticError would
            print(f"  ZeroDivisionError: {e}")
        except LookupError as e:
            # Parent catches both IndexError and KeyError — useful when recovery is same
            print(f"  LookupError ({type(e).__name__}): {e}")
        except (ValueError, TypeError) as e:
            print(f"  {type(e).__name__}: {e}")
        except OSError as e:
            # FileNotFoundError, PermissionError, etc. all caught here
            print(f"  OSError ({type(e).__name__}): {e}")

demonstrate_hierarchy()


# ==============================================================================
# CONCEPT 4: raise, re-raise, and exception chaining (raise ... from)
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 4: raise, re-raise, raise...from")
print("="*60)

def withdraw(balance: float, amount: float) -> float:
    """
    raise with a message — stops execution, creates exception object.
    Always use specific exception types that describe the domain problem.
    """
    if amount <= 0:
        raise ValueError(f"Withdrawal amount must be positive, got {amount}")
    if amount > balance:
        raise ValueError(f"Insufficient funds: balance={balance:.2f}, requested={amount:.2f}")
    return balance - amount

try:
    withdraw(100.0, 200.0)
except ValueError as e:
    print(f"  Withdraw failed: {e}")


# --- Re-raise: log it and let the caller deal with it ---
def log_and_reraise(fn, *args):
    """
    'raise' with no arguments re-raises the CURRENT exception
    with its original traceback intact — nothing is lost.
    """
    try:
        return fn(*args)
    except ValueError as e:
        logger.warning("Validation error caught at boundary: %s", e)
        raise   # same exception, same traceback — caller sees the original


# --- Exception chaining: raise NewError from original_error ---
class DatabaseError(Exception):
    pass

class ServiceError(Exception):
    pass

def fetch_user_from_db(user_id: int):
    """Simulates a DB layer that raises low-level errors."""
    raise ConnectionError(f"TCP connection to db:5432 refused")

def get_user(user_id: int):
    """
    Service layer translates low-level DB errors into domain errors.
    'raise X from Y' preserves the original exception as .__cause__
    so the full chain appears in tracebacks — gold for debugging.
    """
    try:
        return fetch_user_from_db(user_id)
    except ConnectionError as e:
        # Without 'from e' the ConnectionError traceback would be lost
        raise ServiceError(f"Cannot load user {user_id}: database unreachable") from e

try:
    get_user(42)
except ServiceError as e:
    print(f"  ServiceError: {e}")
    print(f"  Caused by:    {e.__cause__}")   # the original ConnectionError

# --- Suppress the chain with 'from None' ---
def get_config(key: str):
    """
    'from None' explicitly suppresses the cause chain.
    Use only when the original error is an implementation detail
    that would confuse the caller.
    """
    try:
        config = {}
        return config[key]
    except KeyError:
        raise KeyError(f"Config key '{key}' not found") from None

try:
    get_config("DATABASE_URL")
except KeyError as e:
    print(f"  Config error (no cause chain): {e}")


# ==============================================================================
# CONCEPT 5: Custom exception class hierarchy
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 5: Custom exception hierarchy")
print("="*60)

# --- Base application exception carries structured data ---
class AppError(Exception):
    """
    Base class for all application-level errors.
    Carries a machine-readable error code and optional detail dict.
    This lets API handlers serialize errors without string-parsing.
    """
    def __init__(self, message: str, code: str = "APP_ERROR", details: dict = None):
        super().__init__(message)
        self.message = message
        self.code    = code
        self.details = details or {}

    def __str__(self):
        return f"[{self.code}] {self.message}"

    def to_dict(self) -> dict:
        return {"error": self.code, "message": self.message, "details": self.details}


class ValidationError(AppError):
    """Input failed validation — do NOT retry, fix the input."""
    def __init__(self, field: str, reason: str):
        super().__init__(
            message=f"Validation failed on '{field}': {reason}",
            code="VALIDATION_ERROR",
            details={"field": field}
        )

class NotFoundError(AppError):
    """Resource does not exist — 404 equivalent."""
    def __init__(self, resource: str, resource_id):
        super().__init__(
            message=f"{resource} with id={resource_id} not found",
            code="NOT_FOUND",
            details={"resource": resource, "id": resource_id}
        )

class PaymentError(AppError):
    """Any payment-related failure."""
    pass

class InsufficientFundsError(PaymentError):
    """Specific payment failure — balance too low."""
    def __init__(self, balance: float, required: float):
        super().__init__(
            message=f"Insufficient funds: has {balance:.2f}, needs {required:.2f}",
            code="INSUFFICIENT_FUNDS",
            details={"balance": balance, "required": required}
        )

class ExternalServiceError(AppError):
    """Third-party API or network failure — may be retryable."""
    pass


# --- Usage: raise specific exceptions ---
def process_order(order_id: int, amount: float, user_balance: float):
    if amount <= 0:
        raise ValidationError("amount", "must be positive")
    if user_balance < amount:
        raise InsufficientFundsError(user_balance, amount)
    return f"Order {order_id} processed — charged {amount:.2f}"


# --- Handling: catch at the right level of specificity ---
test_cases = [
    (1001, 50.00, 200.00),   # success
    (1002, -10.00, 200.00),  # ValidationError
    (1003, 500.00, 100.00),  # InsufficientFundsError
]

for order_id, amount, balance in test_cases:
    try:
        result = process_order(order_id, amount, balance)
        print(f"  OK: {result}")
    except InsufficientFundsError as e:
        # Most specific first — handles just this payment failure
        print(f"  InsufficientFunds: {e}  →  details={e.details}")
    except PaymentError as e:
        # Catches all other PaymentError subclasses
        print(f"  PaymentError: {e.message}")
    except ValidationError as e:
        print(f"  Validation: {e}")
    except AppError as e:
        # Fallback for any unrecognised app error
        print(f"  AppError: {e.to_dict()}")


# ==============================================================================
# CONCEPT 6: Context managers — safe resource handling with __enter__ / __exit__
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 6: Context managers and exceptions")
print("="*60)

class DatabaseTransaction:
    """
    Simulates a database transaction context manager.

    __enter__ runs at the start of the 'with' block.
    __exit__ runs at the end — even if an exception occurred.
      - exc_type, exc_val, exc_tb are None if no exception occurred
      - returning True from __exit__ SUPPRESSES the exception
      - returning False/None PROPAGATES it
    """
    def __init__(self, conn_name: str):
        self.conn_name = conn_name
        self.committed = False

    def __enter__(self):
        print(f"  [DB] BEGIN transaction on {self.conn_name}")
        return self     # bound to the 'as' variable

    def execute(self, sql: str):
        print(f"  [DB] Executing: {sql}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # No exception — commit
            print(f"  [DB] COMMIT transaction on {self.conn_name}")
            self.committed = True
        else:
            # Exception occurred — rollback
            print(f"  [DB] ROLLBACK due to {exc_type.__name__}: {exc_val}")
        return False    # do not suppress the exception


# Successful transaction
print("  -- Successful transaction --")
with DatabaseTransaction("orders_db") as tx:
    tx.execute("INSERT INTO orders VALUES (1001, 50.00)")
    tx.execute("UPDATE inventory SET qty = qty - 1 WHERE id = 5")

# Failed transaction — rollback happens automatically
print("\n  -- Failed transaction --")
try:
    with DatabaseTransaction("orders_db") as tx:
        tx.execute("INSERT INTO orders VALUES (1002, 500.00)")
        raise InsufficientFundsError(100.00, 500.00)   # simulated failure
        tx.execute("This line never runs")
except InsufficientFundsError as e:
    print(f"  Caught outside context: {e}")


# --- contextlib.contextmanager: easier decorator style ---
from contextlib import contextmanager

@contextmanager
def timer(label: str):
    """
    Context manager built with a generator.
    Code before 'yield' = __enter__.
    Code after 'yield' = __exit__.
    Exception handling works the same way.
    """
    start = time.perf_counter()
    try:
        yield   # control passes to the 'with' block here
    finally:
        elapsed = time.perf_counter() - start
        print(f"  [{label}] elapsed: {elapsed:.4f}s")

print()
with timer("hash computation"):
    # Simulating some work
    _ = sum(i * i for i in range(100_000))


# ==============================================================================
# CONCEPT 7: LBYL vs EAFP — Python's philosophy
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 7: LBYL vs EAFP")
print("="*60)

users = {"alice": {"balance": 200.0}, "bob": {"balance": 50.0}}

# LBYL — Look Before You Leap (more Java-like)
def get_balance_lbyl(user_id: str) -> float:
    """
    Checks first, then acts. Good when the check is cheap and atomic.
    Risk: race condition — 'user_id in users' is True, but by the time
    you access users[user_id], another thread might have deleted it.
    """
    if user_id in users:
        return users[user_id]["balance"]
    return 0.0

# EAFP — Easier to Ask Forgiveness than Permission (Pythonic)
def get_balance_eafp(user_id: str) -> float:
    """
    Tries first, handles failure after. Avoids the TOCTOU race condition.
    Single atomic operation — no window between check and use.
    """
    try:
        return users[user_id]["balance"]
    except KeyError:
        return 0.0

print(f"  LBYL alice: {get_balance_lbyl('alice')}")
print(f"  EAFP alice: {get_balance_eafp('alice')}")
print(f"  LBYL ghost: {get_balance_lbyl('ghost')}")
print(f"  EAFP ghost: {get_balance_eafp('ghost')}")


# ==============================================================================
# CONCEPT 8: Logging exceptions correctly
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 8: Logging exceptions")
print("="*60)

module_logger = logging.getLogger("payment")

def charge_card(amount: float) -> str:
    """Demonstrates four logging patterns for exceptions."""
    if amount > 1000:
        raise ExternalServiceError(f"Stripe timeout on amount={amount}", code="STRIPE_TIMEOUT")
    return f"Charged ${amount:.2f}"

# Pattern 1: logger.exception() — logs ERROR + full traceback automatically
print("  Pattern 1: logger.exception()")
try:
    charge_card(2000)
except ExternalServiceError:
    module_logger.exception("Card charge failed — full traceback below")

# Pattern 2: logger.error() with exc_info=True — same effect, different style
print("\n  Pattern 2: logger.error(..., exc_info=True)")
try:
    charge_card(2000)
except ExternalServiceError as e:
    module_logger.error("Charge failed: %s", e, exc_info=True)

# Pattern 3: Log then re-raise (most common in service layers)
print("\n  Pattern 3: log and re-raise")
try:
    try:
        charge_card(2000)
    except ExternalServiceError:
        module_logger.exception("Unexpected payment failure — re-raising for caller")
        raise   # caller handles the retry / fallback logic
except ExternalServiceError as e:
    print(f"  Caller caught: {e}")

# What NOT to do:
print("\n  Anti-pattern: silent pass")
try:
    charge_card(2000)
except ExternalServiceError as e:
    pass  # DON'T DO THIS — swallows the error, zero visibility


# ==============================================================================
# CONCEPT 9: finally edge cases
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 9: finally edge cases")
print("="*60)

# Edge case 1: return in finally SWALLOWS the exception
def dangerous_return():
    """
    A return inside finally discards any pending exception.
    This is almost always a bug — avoid returning from finally.
    """
    try:
        raise ValueError("something bad happened")
    finally:
        return 42   # silently discards the ValueError!

result = dangerous_return()
print(f"  dangerous_return() returned {result} (ValueError was silently swallowed!)")

# Edge case 2: return in try vs return in finally
def which_return():
    """finally's return overrides try's return."""
    try:
        return "from try"
    finally:
        return "from finally"   # this one wins

print(f"  which_return() → '{which_return()}'  (finally overrides try)")

# Safe use of finally — cleanup only, no control flow
def open_connection():
    acquired = True
    try:
        print("  [conn] Connection acquired")
        raise RuntimeError("network blip")
    except RuntimeError as e:
        print(f"  [conn] Handled: {e}")
    finally:
        # Only side effects here — no return, no raise, no break
        print("  [conn] Connection released")   # always runs

open_connection()


# ==============================================================================
# CONCEPT 10: Retry with exponential backoff (production pattern)
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 10: Retry with exponential backoff")
print("="*60)

def retry(max_attempts=3, exceptions=(Exception,), base_delay=0.05, backoff_factor=2.0):
    """
    Decorator: retries a function on transient failures.

    Exponential backoff math:
      attempt 1 fails → wait base_delay * factor^0  (0.05s)
      attempt 2 fails → wait base_delay * factor^1  (0.10s)
      attempt 3 fails → wait base_delay * factor^2  (0.20s)

    Jitter (random noise) prevents the "thundering herd" problem —
    without it, 100 clients that hit the same failure all retry at
    the same instant and overload the recovering service.
    """
    import functools

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt == max_attempts:
                        break
                    jitter = random.uniform(0, delay * 0.1)
                    wait = delay + jitter
                    print(f"  Attempt {attempt}/{max_attempts} failed: {e}. "
                          f"Retrying in {wait:.3f}s...")
                    time.sleep(wait)
                    delay *= backoff_factor
            raise last_exc
        return wrapper
    return decorator


# Simulate a flaky external service
_call_count = 0

@retry(max_attempts=4, exceptions=(ExternalServiceError,), base_delay=0.05)
def call_payment_gateway(amount: float) -> str:
    global _call_count
    _call_count += 1
    if _call_count < 3:
        raise ExternalServiceError(f"Gateway timeout (attempt {_call_count})", code="TIMEOUT")
    return f"Payment of ${amount:.2f} processed (took {_call_count} attempts)"

try:
    result = call_payment_gateway(99.99)
    print(f"  {result}")
except ExternalServiceError as e:
    print(f"  All retries exhausted: {e}")


# ==============================================================================
# CONCEPT 11: Graceful degradation
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 11: Graceful degradation")
print("="*60)

def get_recommendations(product_id: int) -> list:
    """Non-critical feature — simulates a flaky recommendation service."""
    raise ExternalServiceError("Recommendation engine is down", code="REC_DOWN")

def get_price_history(product_id: int) -> list:
    """Another non-critical feature."""
    raise ExternalServiceError("Analytics service unavailable", code="ANALYTICS_DOWN")

def get_product_page(product_id: int) -> dict:
    """
    Critical path: product data must work.
    Non-critical paths: use fallbacks, never crash the page.

    This is the graceful degradation pattern — degraded experience
    is infinitely better than a 500 error.
    """
    # Critical — if this fails, propagate the error (page cannot render)
    product = {"id": product_id, "name": "Laptop Pro", "price": 999.99}

    # Non-critical — use empty fallback on failure
    try:
        recommendations = get_recommendations(product_id)
    except Exception:
        logger.warning("Recommendation service unavailable — returning empty list",
                       exc_info=True)
        recommendations = []

    try:
        price_history = get_price_history(product_id)
    except Exception:
        logger.warning("Analytics service unavailable — omitting price chart",
                       exc_info=True)
        price_history = None

    return {
        "product": product,
        "recommendations": recommendations,   # [] — not None, still renderable
        "price_history": price_history,       # None — chart section hidden
    }

page = get_product_page(42)
print(f"  Product: {page['product']['name']}")
print(f"  Recommendations: {page['recommendations']} (fallback empty list)")
print(f"  Price history: {page['price_history']} (fallback None — chart hidden)")


# ==============================================================================
# CONCEPT 12: Anti-patterns — what NOT to do
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 12: Common anti-patterns")
print("="*60)

# Anti-pattern 1: Bare except / silent pass
print("  Anti-pattern 1: bare except / silent pass")
try:
    int("abc")
except:        # catches SystemExit, KeyboardInterrupt — NEVER do this
    pass       # silent swallow — impossible to debug in production
# FIX: always use specific exception types and always log

# Anti-pattern 2: Catching too broadly
print("  Anti-pattern 2: catching too broad")
def bad_handler():
    try:
        user = users["alice"]          # could fail
        balance = user["balance"]      # could fail for different reason
        result = 100 / balance         # could fail for yet another reason
    except Exception as e:
        print(f"    Bad: 'Error' — which line failed? {e}")  # you have no idea

def good_handler():
    try:
        user = users["alice"]
    except KeyError:
        print("    Good: user not found")
        return
    try:
        result = 100 / user["balance"]
    except ZeroDivisionError:
        print("    Good: balance is zero")
        return
    print(f"    Good: result={result:.2f}")

bad_handler()
good_handler()

# Anti-pattern 3: Losing original exception by not using 'from'
print("  Anti-pattern 3: losing original exception")
def bad_translation():
    try:
        raise ConnectionError("TCP refused")
    except ConnectionError:
        raise RuntimeError("Service failed")  # ConnectionError traceback GONE!
        # FIX: raise RuntimeError("Service failed") from e

def good_translation():
    try:
        raise ConnectionError("TCP refused")
    except ConnectionError as e:
        raise RuntimeError("Service failed") from e  # full chain preserved

try:
    good_translation()
except RuntimeError as e:
    print(f"    Good: {e}  ← caused by: {e.__cause__}")


# ==============================================================================
# PART 2: Custom context manager with suppress (uses contextlib)
# ==============================================================================
print("\n" + "="*60)
print("PART 2: contextlib.suppress and advanced patterns")
print("="*60)

from contextlib import suppress

# suppress() is a readable way to ignore specific exceptions intentionally
print("  contextlib.suppress — intentional exception suppression")
with suppress(FileNotFoundError):
    open("/tmp/nonexistent_practice_file_xyz.txt")
    print("  This line would only run if file existed")
print("  Execution continues — FileNotFoundError was intentionally suppressed")


# --- Exception groups (Python 3.11+) awareness ---
# ExceptionGroup allows raising multiple exceptions simultaneously
# Useful in concurrent contexts (asyncio.TaskGroup, etc.)
# Basic pattern shown for awareness:
print("\n  ExceptionGroup awareness (Python 3.11+)")
import sys
if sys.version_info >= (3, 11):
    # ExceptionGroup and except* syntax (Python 3.11+)
    # Allows raising and handling multiple exceptions simultaneously
    # Useful for asyncio.TaskGroup where multiple tasks may fail at once
    # Example (shown as string to avoid SyntaxError on older Python):
    code = '''
    try:
        raise ExceptionGroup("multiple failures", [
            ValueError("bad input"),
            TypeError("wrong type"),
        ])
    except* ValueError as eg:
        print(f"Caught ValueError group: {eg.exceptions}")
    except* TypeError as eg:
        print(f"Caught TypeError group: {eg.exceptions}")
    '''
    print(f"  Python 3.11+: ExceptionGroup + except* syntax available")
    print(f"  (exec'd to avoid SyntaxError on older Python parsers)")
    exec(code)
else:
    print(f"  Python {sys.version_info.major}.{sys.version_info.minor} — "
          f"ExceptionGroup requires 3.11+")


print("\n" + "="*60)
print("MODULE 06 — All concepts demonstrated.")
print("="*60)
