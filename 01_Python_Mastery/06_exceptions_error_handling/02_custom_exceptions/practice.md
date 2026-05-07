# Custom Exceptions — Practice

> 12 problems · Exception hierarchy design, custom attributes, chaining, API patterns
> Write your answer in `practice_local.py` first, then use the dropdowns.

---

## Quick Index

| # | Concept | Level |
|---|---------|-------|
| Q1 | Define `AppError(Exception)` with message and code | 🟢 |
| Q2 | Build hierarchy: `PaymentError`, `InsufficientFundsError`, `CardDeclinedError` | 🟢 |
| Q3 | Custom `__init__`: add `transaction_id`, `amount`, `http_status` | 🟡 |
| Q4 | Catch at different levels: specific → broad | 🟡 |
| Q5 | `raise PaymentError from original_error` — traceback behavior | 🟡 |
| Q6 | `raise PaymentError from None` — when to suppress the chain | 🟡 |
| Q7 | Exception translation layer: `IntegrityError` → `UserAlreadyExists` | 🟡 |
| Q8 | `user_message` vs `dev_message` distinction | 🟡 |
| Q9 | Full `ValidationError` hierarchy with `field_name` and `constraint` | 🟠 |
| Q10 | REST API exceptions: HTTP status + `error_type` + `details` dict | 🟠 |
| Q11 | Retry-aware exceptions: `RetriableError` vs `NonRetriableError` | 🟠 |
| Q12 | Capstone: full 3-tier hierarchy for a microservices API | 🟠 |

---

### Q1 · Define AppError with message and code

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

**Problem:**
Define `AppError(Exception)` with two attributes: `message` and `code`. Both should be set via `__init__`. Make sure `str(e)` returns something readable. Raise it and verify both attributes are accessible.

```python
class AppError(Exception):
    # your code here
    pass

# Expected:
# e = AppError("something went wrong", code="E001")
# str(e)   → "something went wrong"
# e.code   → "E001"
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>Hint</summary>

Call `super().__init__(message)` so `str(e)` and `e.args[0]` work. Store `code` as `self.code`.

</details>

<details>
<summary>Answer</summary>

```python
class AppError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code

e = AppError("something went wrong", code="E001")
print(str(e))    # something went wrong
print(e.code)    # E001
print(e.args[0]) # something went wrong
```

**Why:** `super().__init__(message)` populates `self.args`, which is what `str(e)` reads. Without it, `str(e)` returns an empty string even if you set `self.message`. Always call `super().__init__` with the human-readable message.

</details>

---

### Q2 · Build the PaymentError hierarchy

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

**Problem:**
Using `AppError` from Q1 as root, create this hierarchy:

```
AppError
└── PaymentError
    ├── InsufficientFundsError
    └── CardDeclinedError
```

Verify that `except PaymentError` catches both leaf types, and `except AppError` catches all three.

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>Hint</summary>

Each class only needs `class X(Parent): pass` if it adds no new behavior. The hierarchy is what matters — `except PaymentError` works because `InsufficientFundsError` is a `PaymentError` via `isinstance`.

</details>

<details>
<summary>Answer</summary>

```python
class AppError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code

class PaymentError(AppError):
    pass

class InsufficientFundsError(PaymentError):
    pass

class CardDeclinedError(PaymentError):
    pass

# Verify hierarchy
for exc_class in [InsufficientFundsError, CardDeclinedError]:
    try:
        raise exc_class("test")
    except PaymentError:
        print(f"{exc_class.__name__} caught by except PaymentError")  # both print

try:
    raise InsufficientFundsError("low balance")
except AppError:
    print("caught by except AppError")  # also works
```

**Why:** Python exception matching uses `isinstance` under the hood. `InsufficientFundsError` inherits from `PaymentError` which inherits from `AppError`, so all three `except` clauses match it. This lets callers choose their level of specificity.

</details>

---

### Q3 · Custom __init__ with transaction_id, amount, http_status

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

**Problem:**
Give `PaymentError` a custom `__init__` that accepts `message`, `transaction_id`, `amount`, and `http_status` (default `402`). Override `__str__` to include the transaction ID.

```python
# Expected:
# e = PaymentError("Card declined", transaction_id="txn_abc123", amount=99.99)
# str(e)           → "PaymentError: Card declined [txn=txn_abc123, amount=99.99]"
# e.transaction_id → "txn_abc123"
# e.http_status    → 402
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>Hint</summary>

Define `__str__` returning a formatted string using `self.__class__.__name__`, `self.args[0]`, `self.transaction_id`, and `self.amount`. Remember to call `super().__init__(message)`.

</details>

<details>
<summary>Answer</summary>

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

e = PaymentError("Card declined", transaction_id="txn_abc123", amount=99.99)
print(str(e))            # PaymentError: Card declined [txn=txn_abc123, amount=99.99]
print(e.transaction_id)  # txn_abc123
print(e.http_status)     # 402
```

**Why:** `__str__` is what Python calls when you do `str(e)` or `print(e)`. It's separate from `args[0]`. Using `self.__class__.__name__` means subclasses get their own name in the string automatically — `CardDeclinedError: Card declined [...]` instead of always showing `PaymentError`.

</details>

---

### Q4 · Catch at different specificity levels

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

**Problem:**
Raise `CardDeclinedError` and show how three separate `except` clauses at different levels all catch it. Then show that order matters — put `AppError` first and observe what happens.

```python
# Demonstrate:
# 1. except CardDeclinedError  ← most specific
# 2. except PaymentError       ← catches both payment types
# 3. except AppError           ← catches everything
# 4. Wrong order: AppError first swallows the specific type
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>Hint</summary>

Python tries `except` clauses in order and stops at the first match. If `AppError` is listed before `CardDeclinedError`, the specific one never runs.

</details>

<details>
<summary>Answer</summary>

```python
def try_catch(exc, handlers):
    """Helper: raise exc, try each handler label in order."""
    try:
        raise exc
    except CardDeclinedError:
        print("caught by: CardDeclinedError")
    except PaymentError:
        print("caught by: PaymentError")
    except AppError:
        print("caught by: AppError")

try_catch(CardDeclinedError("declined"))          # caught by: CardDeclinedError
try_catch(InsufficientFundsError("low balance"))  # caught by: PaymentError
try_catch(AppError("generic"))                    # caught by: AppError

# Wrong order — AppError first:
try:
    raise CardDeclinedError("declined")
except AppError:
    print("AppError caught first — CardDeclinedError handler never reached")
except CardDeclinedError:
    print("this never runs")
```

**Why:** Exception clauses are tried top to bottom. Since `CardDeclinedError` is a subclass of `AppError`, putting `AppError` first means it always wins. Always put more specific exceptions above their parents.

</details>

---

### Q5 · raise PaymentError from original_error

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

**Problem:**
Simulate a Stripe API call that raises a `requests.HTTPError`. In an exception handler, catch it and raise `CardDeclinedError` using `raise X from Y`. Print the traceback and identify where `__cause__` is set.

```python
import requests

def charge_card(amount):
    try:
        # simulate Stripe returning a 402
        response = requests.Response()
        response.status_code = 402
        response.raise_for_status()
    except requests.HTTPError as e:
        raise CardDeclinedError(
            "Card declined by Stripe",
            transaction_id="txn_sim_001",
            amount=amount
        ) from e
```

What does the traceback show? Where is `__cause__`?

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>Hint</summary>

`raise X from Y` sets `X.__cause__ = Y` and `X.__suppress_context__ = True`. The traceback shows both errors with the phrase "The above exception was the direct cause of the following exception".

</details>

<details>
<summary>Answer</summary>

```python
import requests

class CardDeclinedError(PaymentError):
    pass

def charge_card(amount):
    try:
        response = requests.Response()
        response.status_code = 402
        response.raise_for_status()
    except requests.HTTPError as e:
        raise CardDeclinedError(
            "Card declined by Stripe",
            transaction_id="txn_sim_001",
            amount=amount
        ) from e

try:
    charge_card(99.99)
except CardDeclinedError as e:
    print(f"Domain error: {e}")
    print(f"Root cause:   {e.__cause__}")
    print(f"suppress_context: {e.__suppress_context__}")  # True
```

**Traceback shows:**
```
requests.exceptions.HTTPError: 402 Client Error

The above exception was the direct cause of the following exception:

CardDeclinedError: CardDeclinedError: Card declined by Stripe [txn=txn_sim_001, amount=99.99]
```

**Why:** `raise X from Y` explicitly documents the causal chain. `e.__cause__` holds the `HTTPError`. During debugging, you can inspect `e.__cause__` to see the original driver-level error even though your code raised a domain exception.

</details>

---

### Q6 · raise from None — suppress the chain

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

**Problem:**
You're building a public library. Your internal storage uses Redis, but callers should not see `redis.exceptions.ConnectionError` in their tracebacks. Raise a `StorageUnavailableError` using `from None` to produce a clean traceback.

Show the difference in traceback output between `raise X from e` and `raise X from None`.

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>Hint</summary>

`raise X from None` sets `__suppress_context__ = True` and `__cause__ = None`. The traceback only shows `X`, not the original exception. Use this at public API boundaries where the implementation detail (Redis, psycopg2, etc.) should not leak to callers.

</details>

<details>
<summary>Answer</summary>

```python
class StorageUnavailableError(AppError):
    pass

# Simulated Redis error
class FakeRedisError(Exception):
    pass

# With from e — shows full chain:
def get_value_verbose(key):
    try:
        raise FakeRedisError("connection refused on port 6379")
    except FakeRedisError as e:
        raise StorageUnavailableError("Storage is unavailable") from e

# With from None — hides implementation detail:
def get_value_clean(key):
    try:
        raise FakeRedisError("connection refused on port 6379")
    except FakeRedisError:
        raise StorageUnavailableError("Storage is unavailable") from None

try:
    get_value_clean("mykey")
except StorageUnavailableError as e:
    print(f"__cause__: {e.__cause__}")                  # None
    print(f"__suppress_context__: {e.__suppress_context__}")  # True
    # Traceback shows only StorageUnavailableError
```

**When to use `from None`:**
- Public library code where the caller should not depend on your internal tech stack
- API gateways translating backend errors to HTTP responses
- When the original error is a security concern (e.g., reveals internal hostnames)

**When NOT to:** Internal services, debugging phases, or when the original error helps the caller diagnose.

</details>

---

### Q7 · Exception translation layer

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

**Problem:**
Write a `create_user(email)` function that catches `psycopg2.IntegrityError` (simulate it) and raises a `UserAlreadyExists` domain exception. This is the repository-layer translation pattern.

```python
class UserAlreadyExists(AppError):
    def __init__(self, email):
        super().__init__(f"User with email '{email}' already exists", code="USER_EXISTS")
        self.email = email
```

Show the translation in a `create_user` function. Verify the chain is preserved.

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>Hint</summary>

Simulate `psycopg2.IntegrityError` with a plain `Exception` subclass. Catch it in `create_user` and `raise UserAlreadyExists(email) from e`. The caller sees a domain error; the DB error is preserved as `__cause__`.

</details>

<details>
<summary>Answer</summary>

```python
# Simulate psycopg2 for environments without it installed
class FakeIntegrityError(Exception):
    pass

class UserAlreadyExists(AppError):
    def __init__(self, email):
        super().__init__(
            f"User with email '{email}' already exists",
            code="USER_EXISTS"
        )
        self.email = email

def create_user(email):
    try:
        # Simulate DB rejecting duplicate email
        raise FakeIntegrityError(
            'duplicate key value violates unique constraint "users_email_key"'
        )
    except FakeIntegrityError as e:
        raise UserAlreadyExists(email) from e

try:
    create_user("alice@example.com")
except UserAlreadyExists as e:
    print(f"Domain error: {e}")           # User with email 'alice@example.com' already exists
    print(f"Error code:   {e.code}")      # USER_EXISTS
    print(f"Email attr:   {e.email}")     # alice@example.com
    print(f"Root cause:   {e.__cause__}") # the FakeIntegrityError
```

**Why this is the right pattern:** The repository layer owns the translation. The service and handler layers never need to import psycopg2 or know the DB schema. If you swap Postgres for MongoDB, only the repository layer changes — the exception types stay the same.

</details>

---

### Q8 · user_message vs dev_message

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

**Problem:**
Extend `AppError` to carry both a developer-facing `dev_message` (full detail, safe to log) and a `user_message` (safe to show end users). The default `user_message` should be `"An unexpected error occurred."`.

Demonstrate with a `PaymentError` that has a helpful dev message but a safe user message.

```python
# Expected:
# log.error(e.dev_message)    → "Card declined: CVV mismatch on txn_abc123"
# response["error"] = e.user_message  → "Your payment could not be processed."
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>Hint</summary>

Add `user_message` and an optional `dev_message` parameter to `AppError.__init__`. If `dev_message` is not provided, fall back to `message` (the one passed to `super().__init__`).

</details>

<details>
<summary>Answer</summary>

```python
class AppError(Exception):
    DEFAULT_USER_MESSAGE = "An unexpected error occurred."

    def __init__(self, message, code=None, user_message=None):
        super().__init__(message)
        self.code = code
        self.dev_message = message
        self.user_message = user_message or self.DEFAULT_USER_MESSAGE

class CardDeclinedError(AppError):
    DEFAULT_USER_MESSAGE = "Your payment could not be processed."

    def __init__(self, message, transaction_id=None, **kwargs):
        kwargs.setdefault("user_message", self.DEFAULT_USER_MESSAGE)
        super().__init__(message, **kwargs)
        self.transaction_id = transaction_id

# Usage
e = CardDeclinedError(
    "Card declined: CVV mismatch on txn_abc123",
    transaction_id="txn_abc123",
    code="CARD_DECLINED"
)

print(e.dev_message)   # Card declined: CVV mismatch on txn_abc123  (logs)
print(e.user_message)  # Your payment could not be processed.       (frontend)
print(e.code)          # CARD_DECLINED
```

**Why:** This separation is a security and UX requirement. Dev messages may contain internal IDs, SQL fragments, or stack hints that should never reach end users. User messages are pre-written, safe, and translatable.

</details>

---

### Q9 · Full ValidationError hierarchy with field_name and constraint

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

**Problem:**
Build a complete `ValidationError` hierarchy with custom attributes. Each validation error should carry `field_name`. Specific errors add their own context.

```
AppError
└── ValidationError(field_name)
    ├── MissingFieldError(field_name)
    └── InvalidFormatError(field_name, expected_format, received_value)
```

Show catching at each level and extracting the structured data.

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>Hint</summary>

`ValidationError.__init__` takes `message` and `field_name`. `InvalidFormatError.__init__` additionally takes `expected_format` and `received_value` — call `super().__init__` with a generated message and pass `field_name` up.

</details>

<details>
<summary>Answer</summary>

```python
class ValidationError(AppError):
    def __init__(self, message, field_name=None, code="VALIDATION_ERROR"):
        super().__init__(message, code=code)
        self.field_name = field_name

class MissingFieldError(ValidationError):
    def __init__(self, field_name):
        super().__init__(
            f"Required field '{field_name}' is missing",
            field_name=field_name,
            code="MISSING_FIELD"
        )

class InvalidFormatError(ValidationError):
    def __init__(self, field_name, expected_format, received_value):
        super().__init__(
            f"Field '{field_name}' has invalid format. "
            f"Expected: {expected_format}, got: {received_value!r}",
            field_name=field_name,
            code="INVALID_FORMAT"
        )
        self.expected_format = expected_format
        self.received_value = received_value

# Demonstrate
def validate_email(data):
    if "email" not in data:
        raise MissingFieldError("email")
    if "@" not in data["email"]:
        raise InvalidFormatError("email", "user@domain.com", data["email"])
    return data["email"]

for payload in [{"name": "Alice"}, {"email": "not-an-email"}, {"email": "alice@ex.com"}]:
    try:
        result = validate_email(payload)
        print(f"Valid: {result}")
    except InvalidFormatError as e:
        print(f"Format error on '{e.field_name}': got {e.received_value!r}")
    except MissingFieldError as e:
        print(f"Missing: {e.field_name}")
    except ValidationError as e:
        print(f"Validation failed: {e}")
```

**Why:** Attaching `field_name` to the exception lets API error responses pinpoint the exact field that failed. The calling handler can build a structured error response like `{"field": "email", "error": "Invalid format"}` without parsing strings.

</details>

---

### Q10 · REST API exceptions with HTTP status, error_type, details dict

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

**Problem:**
Design an exception hierarchy for a REST API. Every exception should carry:
- `http_status` — the HTTP response code
- `error_type` — a string code like `"validation_error"` or `"not_found"`
- `details` — a dict with any extra context

Map these to a JSON error response body.

```python
# Expected response body:
# {
#   "error_type": "not_found",
#   "message": "User 42 not found",
#   "details": {"user_id": 42}
# }
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>Hint</summary>

Put `http_status`, `error_type`, and `details` on `AppError`. Add a `to_response()` method that returns the dict. Subclasses set their own defaults for `http_status` and `error_type`.

</details>

<details>
<summary>Answer</summary>

```python
class AppError(Exception):
    http_status = 500
    error_type = "internal_error"

    def __init__(self, message, details=None, **kwargs):
        super().__init__(message)
        self.details = details or {}
        # Allow overriding class-level defaults per instance
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_response(self):
        return {
            "error_type": self.error_type,
            "message": self.args[0],
            "details": self.details,
        }

class NotFoundError(AppError):
    http_status = 404
    error_type = "not_found"

class ValidationError(AppError):
    http_status = 422
    error_type = "validation_error"

class ConflictError(AppError):
    http_status = 409
    error_type = "conflict"

class UnauthorizedError(AppError):
    http_status = 401
    error_type = "unauthorized"

# Simulate a handler
def get_user(user_id):
    raise NotFoundError(
        f"User {user_id} not found",
        details={"user_id": user_id}
    )

try:
    get_user(42)
except AppError as e:
    print(f"HTTP {e.http_status}")   # HTTP 404
    import json
    print(json.dumps(e.to_response(), indent=2))
```

**Why:** Putting `http_status` and `error_type` on the exception class (not just the instance) means the mapping is centralized. A single `except AppError` handler can return `e.http_status` and `e.to_response()` without any if/elif chains or lookups.

</details>

---

### Q11 · Retry-aware exceptions: RetriableError vs NonRetriableError

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

**Problem:**
Design an exception hierarchy that tells retry logic whether an error is worth retrying. A `RetriableError` (e.g., temporary network timeout) should be retried. A `NonRetriableError` (e.g., invalid credentials) should not.

Add a `retry_after` attribute on `RetriableError` for rate-limit-aware retries.

```python
# Retry logic should read:
# except AppError as e:
#     if isinstance(e, RetriableError):
#         time.sleep(e.retry_after or 1)
#         retry()
#     else:
#         fail_fast()
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>Hint</summary>

Create `RetriableError(AppError)` with `retry_after=None` and `NonRetriableError(AppError)`. Subclass each for specific cases: `RateLimitError(RetriableError)` sets a default `retry_after`. `AuthenticationError(NonRetriableError)` is never retried.

</details>

<details>
<summary>Answer</summary>

```python
import time

class RetriableError(AppError):
    """The operation failed but may succeed if retried."""
    def __init__(self, message, retry_after=None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after  # seconds to wait before retry

class NonRetriableError(AppError):
    """The operation failed and retrying will not help."""
    pass

# Specific retriable errors
class NetworkTimeoutError(RetriableError):
    def __init__(self, host, timeout_seconds):
        super().__init__(
            f"Connection to {host} timed out after {timeout_seconds}s",
            retry_after=2
        )
        self.host = host

class RateLimitError(RetriableError):
    def __init__(self, retry_after_seconds):
        super().__init__(
            f"Rate limit exceeded. Retry after {retry_after_seconds}s",
            retry_after=retry_after_seconds
        )

# Specific non-retriable errors
class AuthenticationError(NonRetriableError):
    pass

class InvalidInputError(NonRetriableError):
    pass

# Retry wrapper
def with_retry(fn, max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except RetriableError as e:
            if attempt == max_attempts:
                raise
            wait = e.retry_after or 1
            print(f"Attempt {attempt} failed ({e}). Retrying in {wait}s...")
            time.sleep(wait)
        except NonRetriableError as e:
            print(f"Non-retriable error — failing fast: {e}")
            raise

# Test
attempts = 0
def flaky_call():
    global attempts
    attempts += 1
    if attempts < 3:
        raise NetworkTimeoutError("api.example.com", 30)
    return "success"

result = with_retry(flaky_call)
print(result)  # success
```

**Why:** The distinction between retriable and non-retriable errors should live in the exception type, not in the retry logic. The retry layer doesn't need to know about specific error types — it just checks the base class. Adding a new retriable error type automatically participates in retry logic with no changes to the wrapper.

</details>

---

### Q12 · Capstone: full 3-tier exception hierarchy for a microservices API

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

**Problem:**
Design the complete exception hierarchy for a microservices order management API. It must support:

- Domain errors (validation, not found, conflict, payment failure)
- Infrastructure errors (database unavailable, external service down) — with retriable distinction
- All exceptions carry: `http_status`, `error_type`, `user_message`, `details`
- A single handler at the API boundary converts any `AppError` to a JSON response

Implement the hierarchy, demonstrate a realistic request flow (create order → validate → check inventory → charge payment → save), and show the API handler catching everything.

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>Hint</summary>

Layer 1: `AppError` with `http_status`, `error_type`, `user_message`, `details`, `to_response()`.
Layer 2: Domain — `ValidationError`, `NotFoundError`, `ConflictError`, `PaymentError`. Infrastructure — `RetriableError`, `NonRetriableError`.
Layer 3: Specific leaves — `InsufficientFundsError`, `InventoryUnavailableError`, `DatabaseError`, etc.
The API handler catches `AppError`, calls `e.to_response()`, returns `e.http_status`.

</details>

<details>
<summary>Answer</summary>

```python
# ── Layer 1: Root ──────────────────────────────────────────────
class AppError(Exception):
    http_status = 500
    error_type = "internal_error"
    _default_user_message = "An unexpected error occurred."

    def __init__(self, message, details=None, user_message=None):
        super().__init__(message)
        self.details = details or {}
        self.user_message = user_message or self._default_user_message

    def to_response(self):
        return {
            "error_type": self.error_type,
            "message": self.user_message,
            "details": self.details,
        }

# ── Layer 2: Domain ────────────────────────────────────────────
class ValidationError(AppError):
    http_status = 422
    error_type = "validation_error"
    _default_user_message = "The request contains invalid data."

class NotFoundError(AppError):
    http_status = 404
    error_type = "not_found"
    _default_user_message = "The requested resource was not found."

class ConflictError(AppError):
    http_status = 409
    error_type = "conflict"
    _default_user_message = "The request conflicts with existing data."

class PaymentError(AppError):
    http_status = 402
    error_type = "payment_error"
    _default_user_message = "Your payment could not be processed."

    def __init__(self, message, transaction_id=None, **kwargs):
        super().__init__(message, **kwargs)
        self.transaction_id = transaction_id

# ── Layer 2: Infrastructure ────────────────────────────────────
class RetriableError(AppError):
    http_status = 503
    error_type = "service_unavailable"
    _default_user_message = "Service temporarily unavailable. Please try again."

    def __init__(self, message, retry_after=5, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after

class NonRetriableError(AppError):
    http_status = 500
    error_type = "internal_error"

# ── Layer 3: Specific leaves ───────────────────────────────────
class MissingFieldError(ValidationError):
    def __init__(self, field_name):
        super().__init__(
            f"Required field '{field_name}' is missing",
            details={"field": field_name},
            user_message=f"'{field_name}' is required."
        )

class OrderNotFoundError(NotFoundError):
    def __init__(self, order_id):
        super().__init__(
            f"Order {order_id} not found",
            details={"order_id": order_id}
        )

class InsufficientFundsError(PaymentError):
    def __init__(self, transaction_id, amount, balance):
        super().__init__(
            f"Insufficient funds: need {amount}, have {balance}",
            transaction_id=transaction_id,
            details={"amount": amount, "balance": balance},
            user_message="Insufficient funds. Please update your payment method."
        )

class InventoryUnavailableError(RetriableError):
    def __init__(self, product_id):
        super().__init__(
            f"Inventory service unavailable for product {product_id}",
            retry_after=10,
            details={"product_id": product_id}
        )

class DatabaseError(RetriableError):
    def __init__(self, operation):
        super().__init__(
            f"Database unavailable during {operation}",
            retry_after=3
        )

# ── API handler ────────────────────────────────────────────────
import json

def api_create_order(request_data):
    """Simulated API handler — single catch at the boundary."""
    try:
        order = process_order(request_data)
        return {"status": 201, "body": {"order_id": order["id"]}}
    except AppError as e:
        return {"status": e.http_status, "body": e.to_response()}

def process_order(data):
    if "product_id" not in data:
        raise MissingFieldError("product_id")
    if data.get("fail") == "inventory":
        raise InventoryUnavailableError(data["product_id"]) 
    if data.get("fail") == "payment":
        raise InsufficientFundsError("txn_001", 99.99, 10.00)
    return {"id": "order_abc123"}

# Test scenarios
for scenario in [
    {},                                          # missing field
    {"product_id": "P1", "fail": "inventory"},  # retriable
    {"product_id": "P1", "fail": "payment"},    # payment error
    {"product_id": "P1"},                        # success
]:
    response = api_create_order(scenario)
    print(f"HTTP {response['status']}: {json.dumps(response['body'])}")
```

**Expected output:**
```
HTTP 422: {"error_type": "validation_error", "message": "'product_id' is required.", "details": {"field": "product_id"}}
HTTP 503: {"error_type": "service_unavailable", "message": "Service temporarily unavailable...", "details": {"product_id": "P1"}}
HTTP 402: {"error_type": "payment_error", "message": "Insufficient funds...", "details": {"amount": 99.99, "balance": 10.0}}
HTTP 201: {"order_id": "order_abc123"}
```

**Why this architecture works:** The API handler contains a single `except AppError` clause. Every domain and infrastructure error automatically carries its HTTP status and user message. Adding a new error type requires no changes to the handler — just define the class with the right base and attributes. This is the "open/closed principle" applied to exception design.

</details>

---

**[Back to 06_exceptions](../theory.md)** · **[Master Practice](../practice.md)**
