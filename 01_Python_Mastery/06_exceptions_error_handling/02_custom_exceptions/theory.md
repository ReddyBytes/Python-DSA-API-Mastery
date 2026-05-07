# 02 — Custom Exceptions
## Designing Exceptions That Actually Help

> A bare `ValueError` tells the caller *something* is wrong. A `PaymentError` with a `transaction_id` and `decline_code` tells them *exactly what* is wrong and *what to do about it*.

---

## Learning Priority

| Priority | Topics |
|---|---|
| **Must Learn** | `Exception(Exception)` hierarchy · custom attributes · `raise X from Y` |
| **Should Learn** | Layered architecture catching · `raise X from None` · HTTP-mapped exceptions |
| **Good to Know** | `__cause__` vs `__context__` · exception notes (3.11+) |
| **Reference** | `ExceptionGroup` / `except*` syntax (3.11+) |

---

## Chapter 1 — Why Custom Exceptions

Imagine you're building a payment service. When a charge fails, you get back a raw `psycopg2.IntegrityError` or a `requests.HTTPError`. Your caller — some API endpoint handler — has no idea what to do with either of those. It doesn't know if the failure is retryable, whether to show the user an error, or which field was wrong.

A `ValueError` is marginally better. At least it's a standard Python type. But it carries no structured data.

A `PaymentError` with `.transaction_id`, `.decline_code`, and `.http_status` lets the handler:
1. Log the transaction ID for support tickets
2. Map the decline code to a user-facing message
3. Return the right HTTP status without guessing

Custom exceptions are the contract between your service and its callers.

```python
# Before: caller has no actionable information
raise ValueError("payment failed")

# After: caller knows exactly what happened and can respond appropriately
raise CardDeclinedError(
    message="Card declined by issuer",
    transaction_id="txn_abc123",
    decline_code="insufficient_funds",
    http_status=402
)
```

---

## Chapter 2 — Building the Hierarchy

Exceptions should form a tree. The root captures broad domain errors. Leaves carry specific context.

```
Exception
└── AppError
    ├── ValidationError
    │   ├── MissingFieldError
    │   └── InvalidFormatError
    └── PaymentError
        ├── InsufficientFundsError
        └── CardDeclinedError
```

The key design principle: **callers choose their specificity**. A payment handler that only cares whether it was a `PaymentError` (to retry differently) can catch at that level. An audit logger that wants full detail catches `CardDeclinedError`.

```python
class AppError(Exception):
    """Root for all application-level exceptions."""

class ValidationError(AppError):
    """Input did not pass validation."""

class MissingFieldError(ValidationError):
    """A required field was absent."""

class InvalidFormatError(ValidationError):
    """A field value had the wrong format."""

class PaymentError(AppError):
    """Something went wrong in the payment flow."""

class InsufficientFundsError(PaymentError):
    """Account balance too low to complete the transaction."""

class CardDeclinedError(PaymentError):
    """Card was declined by the issuer."""
```

With this hierarchy, `except PaymentError` catches both `InsufficientFundsError` and `CardDeclinedError`. `except AppError` catches everything. This is polymorphism applied to error handling.

---

## Chapter 3 — Custom Attributes

Subclassing `Exception` with a custom `__init__` is how you attach structured data.

```python
class PaymentError(AppError):
    def __init__(self, message, transaction_id=None, amount=None, http_status=402):
        super().__init__(message)
        self.transaction_id = transaction_id
        self.amount = amount
        self.http_status = http_status

    def __str__(self):
        return (
            f"{self.__class__.__name__}: {self.args[0]} "
            f"[txn={self.transaction_id}, amount={self.amount}]"
        )
```

Usage:

```python
raise CardDeclinedError(
    message="Card declined",
    transaction_id="txn_abc123",
    amount=99.99,
    http_status=402
)
```

The handler then reads structured fields, not a string it has to parse:

```python
except PaymentError as e:
    log.error("Payment failed", txn=e.transaction_id, amount=e.amount)
    return {"error": str(e), "code": e.http_status}
```

**User message vs dev message** is a useful distinction in public-facing systems:

```python
class AppError(Exception):
    def __init__(self, message, user_message=None):
        super().__init__(message)
        self.user_message = user_message or "An unexpected error occurred."
```

Callers can log `str(e)` (dev detail) and send `e.user_message` to the frontend.

---

## Chapter 4 — Exception Chaining: raise X from Y

Python preserves the full error chain when you use `raise X from Y`. This means: "X happened because of Y."

```python
import psycopg2

def create_user(email):
    try:
        db.execute("INSERT INTO users (email) VALUES (%s)", [email])
    except psycopg2.IntegrityError as e:
        raise UserAlreadyExists(f"Email already registered: {email}") from e
```

The traceback will show both errors:

```
psycopg2.IntegrityError: duplicate key value violates unique constraint "users_email_key"

The above exception was the direct cause of the following exception:

UserAlreadyExists: Email already registered: user@example.com
```

This is invaluable during debugging. You see your domain error at the top, but the original root cause is preserved below it.

**`__cause__` vs `__context__`:**

| Attribute | Set by | Meaning |
|---|---|---|
| `e.__cause__` | `raise X from Y` | Explicit chain — you declared the relationship |
| `e.__context__` | implicit chaining | Python set it because Y was active when X was raised |
| `e.__suppress_context__` | `raise X from None` | Hides `__context__` from the traceback |

---

## Chapter 5 — raise from None: Hiding Implementation Details

Sometimes you want to expose a clean domain error without leaking your internal stack. This is common in public library design or API boundaries.

```python
def get_user(user_id):
    try:
        return db.query("SELECT * FROM users WHERE id = %s", [user_id])
    except psycopg2.OperationalError as e:
        # We don't want callers to see psycopg2 internals
        raise UserNotFound(f"User {user_id} not found") from None
```

With `from None`, the traceback shows only `UserNotFound`. The `psycopg2.OperationalError` is suppressed.

**When to use it:**

- Library code where the caller should not depend on your internal storage technology
- Public APIs where leaking driver-level errors would expose implementation details
- When the original error is genuinely not useful to the caller

**When NOT to use it:**

- Internal service code where the full chain helps debugging
- Anywhere you're still figuring out root causes
- When the original error contains information the caller needs

---

## Chapter 6 — Where to Catch

The most common custom exception mistake is catching at every layer. This creates noise and loses the chain.

```
Request Handler
    └── Service Layer       ← catch here: translate to AppError, add context
        └── Repository      ← catch here: translate DB errors to domain errors
            └── Database    ← raw driver errors live here
```

**The rule:** catch at architectural boundaries, not at every call site.

```python
# Repository layer: translate DB error → domain error
def save_order(order):
    try:
        db.insert("orders", order.to_dict())
    except psycopg2.IntegrityError as e:
        raise DuplicateOrderError(order_id=order.id) from e

# Service layer: add business context, let domain errors propagate
def place_order(cart, user):
    if cart.is_empty():
        raise EmptyCartError("Cannot place order with empty cart")
    return order_repo.save_order(Order.from_cart(cart, user))

# Handler layer: catch AppError, map to HTTP response
def post_order(request):
    try:
        order = order_service.place_order(request.cart, request.user)
        return {"order_id": order.id}, 201
    except AppError as e:
        return {"error": e.user_message}, e.http_status
```

Each layer catches only what it owns and re-raises (or translates) everything else.

---

## Chapter 7 — ExceptionGroup (Python 3.11+)

`ExceptionGroup` lets you raise and handle multiple simultaneous errors. The main use case is concurrent operations where several tasks fail at once.

```python
# Python 3.11+
errors = []
for item in batch:
    try:
        process(item)
    except ValidationError as e:
        errors.append(e)

if errors:
    raise ExceptionGroup("batch validation failed", errors)
```

Handling with `except*` (note the asterisk — a new syntax):

```python
try:
    process_batch(items)
except* ValidationError as eg:
    for exc in eg.exceptions:
        log.warning("Validation failed", field=exc.field_name)
except* PaymentError as eg:
    for exc in eg.exceptions:
        log.error("Payment failed", txn=exc.transaction_id)
```

`except*` splits the `ExceptionGroup` by type. Each `except*` block handles all matching exceptions; non-matching ones propagate. This is distinct from `except` — you cannot use `except*` and `except` in the same `try` block.

---

## Chapter 8 — Common Mistakes

**Bare Exception subclass with no custom attributes:**

```python
# Bad: you defined a type, but callers still get a string-only error
class PaymentError(Exception):
    pass

raise PaymentError("something went wrong")  # no transaction ID, no status code
```

**Catching and re-raising the same type:**

```python
# Bad: this loses the original traceback and adds no value
try:
    process()
except PaymentError as e:
    raise PaymentError(str(e))  # ← wrong: creates a new exception, drops __cause__
```

If you need to add context and re-raise, use `raise X from e` or just `raise` (bare re-raise preserves context).

**Catching too broadly too early:**

```python
# Bad: swallows everything, caller sees nothing useful
def process_payment(card):
    try:
        charge(card)
    except Exception:
        pass  # ← silent failure: the worst kind
```

**Not calling `super().__init__(message)`:**

```python
# Bad: args tuple is empty, str(e) prints nothing
class MyError(Exception):
    def __init__(self, message):
        self.message = message  # ← forgot super().__init__

raise MyError("oops")
# str(e) → ""  (because args is empty)
```

Always call `super().__init__(message)` so `str(e)` and `e.args[0]` work as expected.

---

## Navigation

**[Back to 06_exceptions](../theory.md)**

**Prev:** [01 Exception Mechanics](../01_exception_mechanics/theory.md) &nbsp;|&nbsp; **Next:** [03 Production Patterns](../03_production_patterns/theory.md)

**Practice:** [practice.md](./practice.md) · [Master](../practice.md)
