# API Design Patterns

> 📝 **Practice:** [Q72 · async-job-api](../api_practice_questions_100.md#q72--design--async-job-api)

> 📝 **Practice:** [Q60 · event-driven-api](../api_practice_questions_100.md#q60--normal--event-driven-api)

> 📝 **Practice:** [Q55 · circuit-breaker-pattern](../api_practice_questions_100.md#q55--normal--circuit-breaker-pattern)

> 📝 **Practice:** [Q73 · file-upload-api](../api_practice_questions_100.md#q73--normal--file-upload-api)

## The Patterns That Separate Good APIs from Great Ones

You've learned HTTP. You know REST. You understand auth, gateways, all of it.

Now comes the part that separates an API that's technically correct from one that
people actually enjoy building against. The patterns in this chapter are the
things you learn from getting burned — from the support ticket saying "your API
charged my customer twice," or the mobile app that grinds to a halt making 500
API calls to load a single screen.

These are the patterns senior engineers reach for instinctively. Let's build that
instinct.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
idempotency keys · long-running operations pattern

**Should Learn** — Important for real projects:
bulk operations · partial update

**Good to Know** — Useful in specific situations:
CQRS for APIs

**Reference** — Know it exists, look up syntax when needed:
Event-carried state transfer

---

## Idempotency — The Most Important Pattern

It's 2 AM. A user clicks "Pay Now" on your checkout page. The request goes out.
Three seconds pass. Nothing. The browser shows a spinner. The network is flaky.
The mobile app's retry logic kicks in and sends the payment request again.

Two requests, one intent: charge the customer once.

If your API isn't built for this, the customer gets charged twice. That's a support
ticket, a chargeback, a lost customer, and depending on your industry, a regulatory
problem.

**Idempotency** means: the same operation, applied multiple times, produces the
same result as applying it once.

```
GET    /users/42     → idempotent by nature (read, no side effects)
DELETE /users/42     → idempotent: deleting twice is same as deleting once
PUT    /users/42     → idempotent: replacing twice with same data = same result

POST   /payments     → NOT idempotent: two requests = two charges
POST   /orders       → NOT idempotent: two requests = two orders
POST   /emails/send  → NOT idempotent: two requests = two emails sent
```

For any operation with real-world side effects — charge a card, create an order,
send a notification, provision infrastructure — you need an idempotency key.

> 📝 **Practice:** [Q71 · idempotency-implementation](../api_practice_questions_100.md#q71--design--idempotency-implementation)

### The Idempotency Key Pattern

The client generates a unique ID (typically a UUID) and sends it in a header.
The server stores the result of the first execution. On any duplicate request
with the same key, the server returns the stored result without re-executing.

```
Client sends:
  POST /payments
  Idempotency-Key: 7f3b2c1a-4d5e-6f7a-8b9c-0d1e2f3a4b5c
  Content-Type: application/json

  {
    "amount": 5000,
    "currency": "usd",
    "customer_id": 42
  }

Server (first time seeing this key):
  → Executes the payment
  → Stores: key → response, status 201
  → Returns 201 Created

Network drops. Client retries.

Client sends (identical request, same key):
  POST /payments
  Idempotency-Key: 7f3b2c1a-4d5e-6f7a-8b9c-0d1e2f3a4b5c

Server (seen this key before):
  → Looks up stored response
  → Returns stored 201 Created (same response as first time)
  → Does NOT charge the customer again
```

The customer gets charged once. Both parties see a successful response.

### Implementation

```python
import hashlib
import json
from datetime import datetime, timedelta
import redis

r = redis.Redis(host='localhost', port=6379)

def handle_with_idempotency(idempotency_key: str, operation, ttl_hours: int = 24):
    """
    Wraps an operation with idempotency.
    Stores the result for ttl_hours after first execution.
    """
    cache_key = f"idempotency:{idempotency_key}"

    # Check if we've seen this key before
    cached = r.get(cache_key)
    if cached:
        stored = json.loads(cached)
        return stored["status_code"], stored["body"], True  # True = from cache

    # First time — execute the operation
    status_code, response_body = operation()

    # Store the result
    r.setex(
        cache_key,
        int(timedelta(hours=ttl_hours).total_seconds()),
        json.dumps({
            "status_code": status_code,
            "body": response_body,
            "created_at": datetime.utcnow().isoformat()
        })
    )

    return status_code, response_body, False  # False = fresh execution


# FastAPI example
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

app = FastAPI()

class PaymentRequest(BaseModel):
    amount: int
    currency: str
    customer_id: int

@app.post("/payments", status_code=201)
async def create_payment(
    body: PaymentRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    if not idempotency_key:
        raise HTTPException(
            status_code=400,
            detail="Idempotency-Key header is required for payment operations"
        )

    def execute_payment():
        # Your actual payment logic here
        result = charge_customer(body.customer_id, body.amount, body.currency)
        return 201, {"payment_id": result.id, "status": "succeeded"}

    status_code, response, from_cache = handle_with_idempotency(
        idempotency_key, execute_payment
    )

    return response  # same response whether fresh or cached
```

### When is idempotency required?

```
REQUIRED:
  - Payment processing / charges
  - Order creation
  - Email / SMS / notification sending
  - Infrastructure provisioning
  - Anything with real-world side effects that can't be undone

NICE TO HAVE:
  - Any state-changing POST endpoint

NOT NEEDED:
  - GET requests (already idempotent by nature)
  - PUT/PATCH with the same data (generally idempotent)
  - DELETE (already idempotent)
```

Stripe requires idempotency keys on all charge operations. It's a good model
to follow for any API that handles money or irreversible actions.

---

## Handling Long-Running Operations

Some operations just take time. Generating a 10,000-row CSV export. Processing a
video. Running a machine learning inference. Re-computing analytics for an entire
quarter. Sending 500,000 emails.

You can't make a client sit on an open HTTP connection for 5 minutes. Connections
timeout, mobile apps go to the background, users close their laptops.

The rule of thumb: **if it takes more than 5 seconds, it should be async.**

### The Async Polling Pattern

> 📝 **Practice:** [Q83 · compare-sync-async-api](../api_practice_questions_100.md#q83--interview--compare-sync-async-api)

> 📝 **Practice:** [Q58 · webhooks-vs-polling](../api_practice_questions_100.md#q58--interview--webhooks-vs-polling)

```
Step 1: Client submits the job
  POST /exports
  {"report_type": "annual_sales", "year": 2024}

  → 202 Accepted   ← NOT 201, NOT 200. 202 = "I got it, I'm working on it"
  {
    "job_id": "exp_abc123",
    "status": "queued",
    "status_url": "/exports/exp_abc123"
  }

Step 2: Client polls for status
  GET /exports/exp_abc123

  → 200 OK
  {
    "job_id": "exp_abc123",
    "status": "processing",
    "progress": 45,
    "message": "Processing rows 4500 of 10000",
    "created_at": "2024-01-15T10:30:00Z",
    "estimated_completion": "2024-01-15T10:32:00Z"
  }

Step 3: Eventually complete
  GET /exports/exp_abc123

  → 200 OK
  {
    "job_id": "exp_abc123",
    "status": "complete",
    "progress": 100,
    "result": {
      "url": "https://storage.myapp.com/exports/exp_abc123.csv",
      "expires_at": "2024-01-22T10:32:00Z",
      "row_count": 10000,
      "file_size_bytes": 2048000
    },
    "completed_at": "2024-01-15T10:31:47Z"
  }

Step 4 (if it fails):
  GET /exports/exp_abc123

  → 200 OK
  {
    "job_id": "exp_abc123",
    "status": "failed",
    "error": {
      "code": "insufficient_data",
      "message": "No sales data found for Q3 2024"
    }
  }
```

Job status values should form a clear state machine:

```
queued → processing → complete
                   └→ failed
                   └→ cancelled
```

Return `200 OK` for all status checks — the status field tells you what state the
job is in. Don't use different HTTP status codes for different job states.

How often should the client poll? Include guidance in your API:

```json
{
  "job_id": "exp_abc123",
  "status": "processing",
  "poll_interval_seconds": 5
}
```

Or use the `Retry-After` header:

```
HTTP/1.1 200 OK
Retry-After: 5
```

> 📝 **Practice:** [Q85 · compare-webhook-vs-polling](../api_practice_questions_100.md#q85--interview--compare-webhook-vs-polling)

### Webhook Callbacks — "Call Me When Done"

Polling means the client wakes up every N seconds to ask "are you done yet?"
That's inefficient when the job might take 20 minutes.

Webhooks flip the model: the client gives you a URL, and you call them when done.

```
Client registers a webhook:
  POST /exports
  {
    "report_type": "annual_sales",
    "year": 2024,
    "webhook_url": "https://myclient.com/callbacks/export-done"
  }

  → 202 Accepted
  { "job_id": "exp_abc123" }

Client goes about its business. No polling needed.

Job completes. Your server calls the webhook:
  POST https://myclient.com/callbacks/export-done
  Content-Type: application/json
  X-Webhook-Signature: sha256=abc123...  ← signature to prove it's really you

  {
    "event": "export.completed",
    "job_id": "exp_abc123",
    "result": {
      "url": "https://storage.myapp.com/exports/exp_abc123.csv"
    },
    "timestamp": "2024-01-15T10:31:47Z"
  }
```

Webhook best practices:
- Sign the payload so the receiver can verify it came from you
- Use a shared secret: `HMAC-SHA256(payload, secret)` in a header
- Expect failures — retry with exponential backoff if the receiver returns non-2xx
- Include the event type in the payload (`"event": "export.completed"`)
- Include a timestamp — receivers can reject stale webhooks
- The receiver should respond quickly (< 5 seconds) and process async

Polling is simpler to implement. Webhooks are more efficient for long jobs.
Offer both when possible — some clients can't receive webhooks (no public URL).

---

## Bulk Operations

Scenario: you're migrating a database. You need to create 50,000 users in your
new system. Each user creation is one POST request. At 100ms round-trip latency,
50,000 requests × 100ms = 83 minutes. That's before you even count per-request
overhead on the server side.

**Don't make 1,000 API calls to create 1,000 users.**

### Bulk Create

```
POST /users/bulk
Content-Type: application/json

{
  "users": [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob",   "email": "bob@example.com"},
    {"name": "Carol", "email": "carol@example.com"},
    ... (up to a reasonable limit, e.g., 500 per request)
  ]
}
```

What should the response look like? This is where most APIs get lazy and just
return 200 or 400. A good bulk response tells you exactly which items succeeded
and which failed.

```json
HTTP/1.1 207 Multi-Status

{
  "summary": {
    "total": 3,
    "succeeded": 2,
    "failed": 1
  },
  "results": [
    {
      "index": 0,
      "status": "created",
      "id": 1001,
      "data": {"name": "Alice", "email": "alice@example.com", "id": 1001}
    },
    {
      "index": 1,
      "status": "failed",
      "error": {
        "code": "duplicate_email",
        "message": "Email bob@example.com already exists"
      },
      "data": {"name": "Bob", "email": "bob@example.com"}
    },
    {
      "index": 2,
      "status": "created",
      "id": 1002,
      "data": {"name": "Carol", "email": "carol@example.com", "id": 1002}
    }
  ]
}
```

Notice: `207 Multi-Status` — not 200, not 400. Some succeeded, some failed. The
status code reflects the mixed result. The client can process the array and know
exactly which items need attention.

### All-or-Nothing vs Best-Effort

Two philosophies for handling partial failures:

```
ALL-OR-NOTHING (transactional):
  If any item in the batch fails, roll back the entire batch.
  → Use for: financial operations, anything that must be consistent
  → Pro: no partial state, easy to retry the whole batch
  → Con: one bad item blocks all others

BEST-EFFORT (partial success):
  Process what you can, report failures, continue with the rest.
  → Use for: user imports, notification batches, non-critical operations
  → Pro: maximum throughput, clear per-item results
  → Con: client must track which items succeeded

Document which behavior your API provides. Be explicit.
If using all-or-nothing, use a standard DB transaction.
If using best-effort, return 207 with per-item results.
```

Expose this as a parameter when sensible:

```json
POST /users/bulk
{
  "mode": "best_effort",   // or "transactional"
  "users": [...]
}
```

---

## Partial Updates with PATCH

You have a user with 15 fields. The user wants to update their email address.
Should they send all 15 fields, or just the one that changed?

```
PUT /users/42               PATCH /users/42
{                           {
  "name": "Alice",            "email": "new@example.com"
  "email": "new@...",       }
  "age": 30,
  "bio": "...",
  "website": "...",
  "phone": "...",
  ... (all 15 fields)
}
```

PUT replaces the entire resource. If you forget a field in a PUT, that field
gets wiped. PATCH updates only what you send.

### JSON Merge Patch (the simple one)

RFC 7396. The simplest PATCH semantics. You send an object with only the
fields you want to change. Null means "delete this field."

```
Current state:
{
  "name": "Alice",
  "email": "alice@example.com",
  "bio": "I love coffee",
  "phone": "+1-555-0100"
}

PATCH /users/42
{
  "email": "newemail@example.com",
  "bio": null,
  "phone": "+1-555-0200"
}

Result:
{
  "name": "Alice",            ← unchanged (not in patch)
  "email": "newemail@...",    ← updated
  "bio": null,                ← set to null (or removed, depending on your choice)
  "phone": "+1-555-0200"      ← updated
}
```

### JSON Patch (the powerful one)

RFC 6902. An array of operation objects. Supports add, remove, replace, move,
copy, and test operations. More expressive, more complex.

```
PATCH /users/42
Content-Type: application/json-patch+json

[
  {"op": "replace", "path": "/email",       "value": "newemail@example.com"},
  {"op": "remove",  "path": "/bio"},
  {"op": "add",     "path": "/tags/-",      "value": "premium"},
  {"op": "test",    "path": "/version",     "value": 5}  ← optimistic locking
]
```

JSON Merge Patch is right for 95% of use cases. Use JSON Patch when you need
atomic array operations or optimistic locking tests.

### The null vs omit distinction

This trips up a lot of developers:

```python
# PATCH body:
{"bio": null}      # ← explicitly setting bio to null (clear the field)
{}                 # ← omitting bio entirely (leave it unchanged)

# These are DIFFERENT. Your server must handle them differently.

# In Python with Pydantic, use Optional with a sentinel:
from typing import Optional
from pydantic import BaseModel

UNSET = object()  # sentinel

class UserPatchRequest(BaseModel):
    name: Optional[str] = None          # BAD: can't distinguish null from missing
    email: Optional[str] = ...          # BETTER with Pydantic v2

# Pydantic v2 approach:
from pydantic import BaseModel
from typing import Optional

class UserPatch(BaseModel):
    model_config = {"extra": "forbid"}

    name: Optional[str] = None   # if None → clear; if absent → keep
    email: Optional[str] = None

# Or use the explicit UNSET pattern:
from dataclasses import dataclass, field
from typing import Any

_UNSET = object()

@dataclass
class UserPatch:
    name: Any = _UNSET
    email: Any = _UNSET

    def get_updates(self) -> dict:
        updates = {}
        if self.name is not _UNSET:
            updates["name"] = self.name    # could be None (clear) or a value
        if self.email is not _UNSET:
            updates["email"] = self.email
        return updates
```

---

## Soft Delete vs Hard Delete

A user clicks "delete account." Your `DELETE /users/42` endpoint runs.
Six months later, a compliance team needs an audit trail. Six months later,
the user calls customer support saying they deleted their account by mistake.
Six months later, a financial regulator asks for all transactions made by
that account.

If you hard deleted the row, that data is gone.

### Soft Delete

Instead of removing the row, mark it as deleted:

```sql
-- Instead of DELETE FROM users WHERE id = 42;

UPDATE users SET deleted_at = NOW() WHERE id = 42;
```

```python
# SQLAlchemy model with soft delete
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    deleted_at = Column(DateTime, nullable=True)  # null = active

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()


# Always filter deleted records from queries
def get_users(db_session):
    return db_session.query(User).filter(User.deleted_at.is_(None)).all()

# Restore is possible
def restore_user(db_session, user_id: int):
    user = db_session.query(User).filter(User.id == user_id).first()
    if user:
        user.deleted_at = None
        db_session.commit()
```

Conventions when implementing soft delete:

```
GET /users             → returns only non-deleted users (deleted_at IS NULL)
GET /users/42          → returns 404 if deleted_at IS NOT NULL
DELETE /users/42       → sets deleted_at, returns 204 No Content
GET /users?include_deleted=true  → admin-only, returns all records

Consider:
  - Unique constraints: email must be unique among ACTIVE users
    (a deleted user's email should be reusable)
  - Foreign keys: orders for a deleted user still exist, still valid
  - Search indexes: exclude deleted records from search
  - Scheduled cleanup: purge records where deleted_at is older than N years
    (for GDPR compliance: "right to be forgotten")
```

### Hard Delete

Actually removes the row. Use when:
- GDPR "right to be forgotten" is exercised (you must hard delete PII)
- The data has no audit/compliance value
- You need to reclaim storage for high-volume data
- The user explicitly requests permanent deletion (as opposed to deactivation)

For GDPR, you often implement a two-phase deletion:
1. Soft delete immediately (hides the user, preserves data for compliance window)
2. Hard delete after 30 days, or immediately on explicit erasure request

---

## Versioning a Running API Without Breaking Clients

Your API is live. Clients are using it in production. You need to change
something. How do you do it without breaking existing integrations?

The key mental shift: **additive changes are safe, removal is a breaking change.**

### Safe (additive) changes — no new version needed

```
Adding a new field to a response:
  Before: {"id": 42, "name": "Alice"}
  After:  {"id": 42, "name": "Alice", "created_at": "2024-01-15"}
  → Existing clients ignore the new field. Safe.

Adding a new optional request parameter:
  GET /users?page=1  (existing)
  GET /users?page=1&sort=name  (new optional param, default: existing behavior)
  → Existing clients don't send it. Safe.

Adding a new endpoint:
  POST /users/bulk  (new)
  → Existing clients don't call it. Safe.

Adding a new status code (that clients should handle gracefully):
  429 Too Many Requests
  → Well-written clients handle unknown 4xx. Fine.
```

### Breaking changes — require a new version

```
Removing a field from a response:
  Before: {"id": 42, "name": "Alice", "username": "alice123"}
  After:  {"id": 42, "name": "Alice"}
  → Client code that reads .username now gets undefined/null. Breaking.

Renaming a field:
  Before: {"user_name": "alice"}
  After:  {"username": "alice"}
  → Same as removing. Breaking.

Changing a field's type:
  Before: {"count": "42"}   (string)
  After:  {"count": 42}     (integer)
  → Client code treating it as string breaks. Breaking.

Changing a URL structure:
  Before: GET /users/42/orders
  After:  GET /orders?user_id=42
  → Client code with the old URL gets 404. Breaking.

Changing required fields in a request:
  Before: POST /users requires {"name", "email"}
  After:  POST /users requires {"name", "email", "phone"}
  → Existing clients not sending phone get 400. Breaking.
```

### The Deprecation Header

When you do need to make a breaking change, give clients time to migrate. Use
the standard deprecation headers (RFC 8594):

```
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sat, 31 Dec 2025 23:59:59 GMT
Link: <https://docs.myapp.com/migration/v3>; rel="deprecation"

{...response body...}
```

Every response on a deprecated endpoint includes these headers. Good API clients
log deprecation warnings. The `Sunset` date tells clients when the endpoint dies.

In Python/FastAPI:

```python
from fastapi import Response
from datetime import datetime

@app.get("/v2/users")
async def get_users_v2(response: Response):
    # Mark this version as deprecated
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "Sat, 31 Dec 2025 23:59:59 GMT"
    response.headers["Link"] = (
        '<https://docs.myapp.com/migration/v3>; rel="deprecation"'
    )
    return {"users": [...]}
```

### Versioning strategies

There are two main camps:

**URL versioning** (most common, most explicit):

```
https://api.myapp.com/v1/users
https://api.myapp.com/v2/users

Pros: obvious, easy to test with curl, visible in logs
Cons: "ugly" URLs, clients must update base URLs
```

**Header versioning** (cleaner URLs):

```
GET /users
API-Version: 2024-01-01   ← date-based, Stripe's approach
API-Version: 2            ← number-based

Pros: clean URLs, base URL never changes
Cons: harder to test without tooling, less visible
```

Pick one and be consistent. URL versioning is more common for public APIs
because it's more transparent. Header versioning is used by Stripe and is
elegant when done well.

The practical rule: you don't need v2 until you have a breaking change. Most
APIs run on v1 for years with only additive changes. New versions are expensive —
you're maintaining two codebases simultaneously. Avoid it as long as possible.

---

## Summary

```
Idempotency
  The same request, sent multiple times = same result as once
  Needed for: payments, orders, anything with irreversible side effects
  Implementation: client sends Idempotency-Key header
                  server stores key → response for 24 hours
                  duplicate key returns stored response without re-executing

Long-Running Operations
  Synchronous: fine for < 5 seconds
  Async polling:
    POST /jobs          → 202 Accepted + { job_id }
    GET  /jobs/{id}     → { status: "processing", progress: 45 }
    GET  /jobs/{id}     → { status: "complete", result: {...} }
  Webhooks: register a URL, get called when done (better than polling for slow jobs)

Bulk Operations
  POST /resources/bulk with array body
  207 Multi-Status with per-item results
  Document: all-or-nothing (transactional) vs best-effort behavior

PATCH (Partial Updates)
  PATCH updates only specified fields; PUT replaces the whole resource
  JSON Merge Patch: simple, null = delete field
  JSON Patch: powerful, operation array
  Distinguish null (clear field) from omitted (leave unchanged)

Soft Delete
  Set deleted_at instead of removing the row
  GET /resources filters out soft-deleted by default
  Enables: audit trail, recovery, foreign key integrity
  Hard delete for GDPR erasure requests or after retention window

Versioning
  Additive changes = safe (new fields, new endpoints, new optional params)
  Removal/rename/type change = breaking change → new version
  Use Deprecation + Sunset headers to signal planned removal
  URL versioning (/v1/, /v2/) or header versioning — be consistent
```

---

## 📝 Practice Questions

> 📝 **Practice:** [Q92 · predict-concurrent-idempotent](../api_practice_questions_100.md#q92--critical--predict-concurrent-idempotent)

> 📝 **Practice:** [Q56 · retry-exponential-backoff](../api_practice_questions_100.md#q56--critical--retry-exponential-backoff)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← API Gateway Patterns](../15_api_gateway/gateway_patterns.md) &nbsp;|&nbsp; **Next:** [WebSockets & Real-Time APIs →](../17_websockets/realtime_apis.md)

**Related Topics:** [API Gateway Patterns](../15_api_gateway/gateway_patterns.md) · [Real-World Architectures](../18_real_world_apis/architectures.md) · [API Versioning](../08_versioning_standards/versioning_strategy.md) · [REST Best Practices](../03_rest_best_practices/patterns.md)
