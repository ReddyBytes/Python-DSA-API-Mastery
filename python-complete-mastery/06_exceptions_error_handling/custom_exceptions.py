"""
06_exceptions_error_handling/custom_exceptions.py
===================================================
CONCEPT: Building a custom exception hierarchy for production applications.
WHY THIS MATTERS: Custom exceptions communicate intent. `PaymentDeclinedError`
tells you instantly what went wrong — `ValueError` tells you nothing.
A well-designed exception hierarchy also lets callers catch at the right level
of specificity: catch `PaymentError` for all payment failures, or
`PaymentDeclinedError` specifically to handle the card-declined case.

Prerequisite: Modules 01–05 (fundamentals through OOP)
"""

# =============================================================================
# SECTION 1: Building a custom exception hierarchy
# =============================================================================

# CONCEPT: Custom exceptions should inherit from Exception (not BaseException).
# BaseException catches things like KeyboardInterrupt and SystemExit — you
# almost never want that. Inherit from the most specific standard exception
# that makes sense (ValueError, TypeError, RuntimeError) for context,
# or from your own base class for application-specific exceptions.

print("=== Section 1: Exception Hierarchy ===")

# Base exception for the whole application — all app errors inherit from this
class AppError(Exception):
    """
    Base class for all application-specific exceptions.
    WHY: Callers can catch `AppError` to handle any application error,
    or catch a specific subclass for granular handling.
    Adding a category field gives structured error info to callers.
    """
    def __init__(self, message: str, code: str = "APP_ERROR"):
        super().__init__(message)   # call Exception.__init__ with the message
        self.code = code            # machine-readable error code for APIs
        self.message = message      # human-readable message

    def to_dict(self) -> dict:
        """Useful for JSON API error responses."""
        return {"error": self.code, "message": self.message}


# Domain-specific exceptions — organized by subsystem
class ValidationError(AppError):
    """Input validation failed (invalid data format, missing fields, etc.)"""
    def __init__(self, message: str, field: str = None):
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field   # which field failed validation

    def to_dict(self) -> dict:
        d = super().to_dict()
        if self.field:
            d["field"] = self.field
        return d


class AuthError(AppError):
    """Authentication or authorization failure."""
    pass

class UnauthorizedError(AuthError):
    """User is not logged in."""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, code="UNAUTHORIZED")

class ForbiddenError(AuthError):
    """User is logged in but lacks permission."""
    def __init__(self, resource: str):
        super().__init__(f"Access denied: {resource}", code="FORBIDDEN")
        self.resource = resource


class PaymentError(AppError):
    """Base for all payment failures."""
    def __init__(self, message: str, code: str, amount: float = None):
        super().__init__(message, code=code)
        self.amount = amount

class PaymentDeclinedError(PaymentError):
    """Card was declined by the payment processor."""
    def __init__(self, amount: float, reason: str = "Card declined"):
        super().__init__(f"Payment of ${amount:.2f} declined: {reason}",
                         code="PAYMENT_DECLINED", amount=amount)
        self.reason = reason

class InsufficientFundsError(PaymentError):
    """User doesn't have enough balance."""
    def __init__(self, requested: float, available: float):
        super().__init__(
            f"Insufficient funds: requested ${requested:.2f}, available ${available:.2f}",
            code="INSUFFICIENT_FUNDS", amount=requested
        )
        self.requested = requested
        self.available = available


class DatabaseError(AppError):
    """Database operation failed."""
    def __init__(self, message: str, query: str = None):
        super().__init__(message, code="DATABASE_ERROR")
        self.query = query   # attach the failing query for debugging


# --- Demonstrate the hierarchy ---
exceptions = [
    ValidationError("Email is invalid", field="email"),
    UnauthorizedError(),
    ForbiddenError("/admin/users"),
    PaymentDeclinedError(99.99, "Insufficient credit"),
    InsufficientFundsError(500.0, 245.50),
    DatabaseError("Connection refused", query="SELECT * FROM users"),
]

for exc in exceptions:
    print(f"\n  {type(exc).__name__}:")
    print(f"    message: {exc.message}")
    print(f"    code:    {exc.code}")
    print(f"    dict:    {exc.to_dict()}")


# =============================================================================
# SECTION 2: Catching at different levels of specificity
# =============================================================================

# CONCEPT: Because all app exceptions inherit from AppError, callers can
# choose how specific to be in their catch. This is the primary reason
# to build a hierarchy — not just naming, but catching behavior.

print("\n=== Section 2: Catching at Different Levels ===")

def process_payment(amount: float, user_balance: float):
    """Simulates a payment flow that can fail in multiple ways."""
    if amount <= 0:
        raise ValidationError("Amount must be positive", field="amount")
    if user_balance < amount:
        raise InsufficientFundsError(amount, user_balance)
    if amount > 10_000:
        raise PaymentDeclinedError(amount, "Amount exceeds limit")
    return {"status": "success", "amount": amount}

test_cases = [
    (-50,    100.0),   # ValidationError
    (500,    245.0),   # InsufficientFundsError
    (15_000, 50_000.0),  # PaymentDeclinedError
    (99.99,  500.0),   # Success
]

for amount, balance in test_cases:
    try:
        result = process_payment(amount, balance)
        print(f"  ✓ Payment ${amount}: {result['status']}")

    except InsufficientFundsError as e:
        # Specific handling: suggest adding funds
        print(f"  ✗ Insufficient funds: need ${e.requested:.2f}, have ${e.available:.2f}")

    except PaymentDeclinedError as e:
        # Specific handling: suggest different payment method
        print(f"  ✗ Card declined (${e.amount}): {e.reason}")

    except PaymentError as e:
        # Mid-level: catches any payment failure not handled above
        print(f"  ✗ Payment error ({e.code}): {e.message}")

    except ValidationError as e:
        # Specific: show field-level error to user
        field_info = f" (field: {e.field})" if e.field else ""
        print(f"  ✗ Validation{field_info}: {e.message}")

    except AppError as e:
        # Catch-all for any unhandled app error
        print(f"  ✗ App error ({e.code}): {e.message}")


# =============================================================================
# SECTION 3: Exception chaining — preserving the root cause
# =============================================================================

# CONCEPT: When you catch one exception and raise another, use `raise X from Y`
# to chain them. This preserves the full cause chain in tracebacks.
# WHY: "Database error" without knowing WHY is useless for debugging.
# Chaining shows: ValidationError caused by → OperationalError caused by → ConnectionRefusedError

print("\n=== Section 3: Exception Chaining ===")

class UserRepository:
    def find_user(self, user_id: int):
        """Simulates a DB call that might fail."""
        if user_id == 999:
            # Simulate a low-level database error
            raise ConnectionError("TCP connection to db:5432 refused")
        return {"id": user_id, "name": "Alice"}

def get_user_profile(user_id: int):
    """
    Wraps the DB call. Catches low-level errors and raises
    domain-specific errors — but chains the original cause.
    """
    repo = UserRepository()
    try:
        return repo.find_user(user_id)
    except ConnectionError as original:
        # `raise X from Y` stores Y as the __cause__ of X
        # The traceback shows both exceptions
        raise DatabaseError(
            f"Could not load user {user_id}: database unavailable"
        ) from original   # preserves the original ConnectionError

try:
    get_user_profile(999)
except DatabaseError as e:
    print(f"  Caught: {type(e).__name__}: {e.message}")
    print(f"  Caused by: {type(e.__cause__).__name__}: {e.__cause__}")


# =============================================================================
# SECTION 4: Exception groups and context managers (Python 3.11+)
# =============================================================================

# CONCEPT: Python 3.11 introduced ExceptionGroup for handling multiple
# concurrent failures (e.g., when validating a whole form at once
# instead of stopping at the first error).

print("\n=== Section 4: Collecting Multiple Errors ===")

def validate_user_data(data: dict) -> list:
    """
    Validate all fields, collect ALL errors, don't stop at first failure.
    WHY: In form validation, you want to show ALL errors to the user,
    not just the first one. Stop-at-first makes for bad UX.
    """
    errors = []

    if not data.get("name") or len(data["name"].strip()) < 2:
        errors.append(ValidationError("Name must be at least 2 characters", field="name"))

    email = data.get("email", "")
    if "@" not in email or "." not in email.split("@")[-1]:
        errors.append(ValidationError("Email address is invalid", field="email"))

    age = data.get("age")
    if age is None:
        errors.append(ValidationError("Age is required", field="age"))
    elif not isinstance(age, int) or age < 0 or age > 150:
        errors.append(ValidationError("Age must be a valid integer between 0 and 150", field="age"))

    password = data.get("password", "")
    if len(password) < 8:
        errors.append(ValidationError("Password must be at least 8 characters", field="password"))

    return errors

bad_data = {"name": "A", "email": "not-an-email", "age": -5, "password": "abc"}
errors = validate_user_data(bad_data)

if errors:
    print(f"  Found {len(errors)} validation errors:")
    for err in errors:
        print(f"    [{err.field}] {err.message}")


print("\n=== Custom exceptions complete ===")
print("Exception hierarchy design rules:")
print("  1. One base class per domain (AppError, NetworkError, etc.)")
print("  2. Each exception carries the information needed to handle it")
print("  3. Catch at the right level — specific catches before general")
print("  4. `raise X from Y` chains exceptions — never lose the root cause")
print("  5. Collect ALL validation errors, don't stop at the first one")
