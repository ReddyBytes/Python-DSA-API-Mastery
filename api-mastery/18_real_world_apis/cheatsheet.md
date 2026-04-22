# ⚡ Cheatsheet: Real-World API Patterns

---

## Learning Priority

**Must Learn** — patterns from production APIs you will use or build:
Cursor pagination · idempotency in payments · webhook signature verification

**Should Learn** — appear in senior interviews, real production systems:
API key scoping · Stripe-style patterns · retry-after header

**Good to Know** — polish for API design discussions:
Expansion pattern · field masks · event envelope pattern

**Reference** — look up when needed:
Stripe API docs · GitHub API pagination headers · Twilio webhook security

---

## Stripe-Style API Patterns

```python
# 1. Consistent resource IDs with type prefix
user_id     = "usr_4xkP9mNq2L"
payment_id  = "pay_7hJq3rTv8K"
refund_id   = "ref_2mNb5pWx1Y"
# Prefix tells you the type at a glance — no need to check the endpoint

# 2. Consistent timestamps — always ISO 8601 UTC
{
    "id": "pay_7hJq3rTv8K",
    "created_at": "2024-01-25T10:30:00Z",
    "updated_at": "2024-01-25T10:31:22Z"
}

# 3. Uniform error object
{
    "error": {
        "type": "invalid_request_error",
        "code": "amount_too_small",
        "message": "Amount must be at least $0.50 USD",
        "param": "amount",
        "doc_url": "https://api.example.com/docs/errors/amount_too_small"
    }
}
# machine-readable code + human message + which param failed

# 4. Expansion pattern — embed related objects on demand
GET /payments/pay_7hJq3rTv8K
Response: {"id": "pay_7hJq3rTv8K", "customer": "cus_4xkP9mNq2L", ...}

GET /payments/pay_7hJq3rTv8K?expand=customer
Response: {"id": "pay_7hJq3rTv8K", "customer": {"id": "cus_4xkP9mNq2L", "email": "..."}, ...}
```

```python
# FastAPI expansion pattern
from typing import Optional

@app.get("/payments/{payment_id}")
async def get_payment(payment_id: str, expand: Optional[list[str]] = Query(None)):
    payment = await db.get_payment(payment_id)
    if expand and "customer" in expand:
        payment["customer"] = await db.get_customer(payment["customer_id"])
    if expand and "refunds" in expand:
        payment["refunds"] = await db.list_refunds(payment_id)
    return payment
```

---

## Cursor Pagination Pattern

```python
import base64
import json
from typing import Optional

def encode_cursor(data: dict) -> str:
    """Encode pagination state as opaque cursor string."""
    return base64.b64encode(json.dumps(data).encode()).decode()

def decode_cursor(cursor: str) -> dict:
    """Decode cursor back to pagination state."""
    return json.loads(base64.b64decode(cursor.encode()).decode())

@app.get("/feed")
async def get_feed(
    limit: int = 20,
    cursor: Optional[str] = None
):
    if cursor:
        state = decode_cursor(cursor)
        # Use cursor state to filter — always efficient regardless of depth
        rows = await db.fetchall(
            "SELECT * FROM posts WHERE created_at < %s ORDER BY created_at DESC LIMIT %s",
            (state["created_at"], limit + 1)  # fetch one extra to detect has_more
        )
    else:
        rows = await db.fetchall(
            "SELECT * FROM posts ORDER BY created_at DESC LIMIT %s",
            (limit + 1,)
        )

    has_more = len(rows) > limit
    items = rows[:limit]

    next_cursor = None
    if has_more and items:
        last = items[-1]
        next_cursor = encode_cursor({"created_at": str(last["created_at"]), "id": last["id"]})

    return {
        "data": items,
        "pagination": {
            "next_cursor": next_cursor,
            "has_more": has_more,
            "limit": limit
        }
    }
```

**Why cursor pagination for feeds:**
- Real-time inserts don't cause duplicate/skipped items
- `WHERE created_at < cursor_time` is always index-efficient
- Works at any depth — no `OFFSET N` performance cliff

---

## Webhook Signature Verification

```python
import hmac
import hashlib
import time
from fastapi import Request, HTTPException

WEBHOOK_SECRET = "whsec_loaded_from_env"
TIMESTAMP_TOLERANCE_SECONDS = 300  # reject webhooks older than 5 minutes

async def verify_webhook_signature(request: Request) -> dict:
    """
    Stripe-style signature verification:
    Header: Webhook-Signature: t=1706180460,v1=abc123...
    Payload signed: "{timestamp}.{body}"
    """
    signature_header = request.headers.get("Webhook-Signature")
    if not signature_header:
        raise HTTPException(400, "Missing Webhook-Signature header")

    # Parse header: t=timestamp,v1=signature
    parts = dict(p.split("=", 1) for p in signature_header.split(","))
    timestamp = parts.get("t")
    signature = parts.get("v1")

    if not timestamp or not signature:
        raise HTTPException(400, "Malformed signature header")

    # Replay attack protection — reject old webhooks
    if abs(time.time() - int(timestamp)) > TIMESTAMP_TOLERANCE_SECONDS:
        raise HTTPException(400, "Webhook timestamp too old")

    # Reconstruct and verify signature
    body = await request.body()
    signed_payload = f"{timestamp}.{body.decode()}"
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        signed_payload.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):  # constant-time comparison
        raise HTTPException(401, "Invalid webhook signature")

    return await request.json()

@app.post("/webhooks/payment")
async def handle_payment_webhook(request: Request):
    payload = await verify_webhook_signature(request)
    event_type = payload.get("type")
    if event_type == "payment.succeeded":
        await handle_payment_succeeded(payload["data"])
    elif event_type == "payment.failed":
        await handle_payment_failed(payload["data"])
    return {"received": True}  # always return 200 quickly; process async
```

---

## API Key Scoping

```python
# API keys carry scopes — fine-grained permission control
# Format: prefix_base62random
# Scopes: read:users write:orders admin:billing

from enum import Enum

class ApiKeyScope(str, Enum):
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    READ_ORDERS = "read:orders"
    WRITE_ORDERS = "write:orders"
    ADMIN_BILLING = "admin:billing"
    WEBHOOK_RECEIVE = "webhook:receive"

# Key stored in DB (hash the actual key — never store plaintext)
# {
#   "id": "key_id",
#   "key_hash": "sha256_of_key",
#   "key_prefix": "sk_live_Abc1",  # shown to user to identify the key
#   "scopes": ["read:users", "read:orders"],
#   "rate_limit_per_hour": 10000,
#   "created_at": "...",
#   "last_used_at": "..."
# }

from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

def require_scope(scope: ApiKeyScope):
    async def verify(api_key: str = Security(api_key_header)):
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        key_record = await db.get_api_key_by_hash(key_hash)
        if not key_record:
            raise HTTPException(401, "Invalid API key")
        if scope.value not in key_record["scopes"]:
            raise HTTPException(403, f"API key lacks scope: {scope.value}")
        return key_record
    return verify

@app.get("/users", dependencies=[Depends(require_scope(ApiKeyScope.READ_USERS))])
async def list_users():
    return await db.list_users()
```

---

## Retry-After Header

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import time

# 429 Too Many Requests — always include Retry-After
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    reset_time = exc.reset_at  # Unix timestamp of window reset
    retry_after = max(0, int(reset_time - time.time()))
    return JSONResponse(
        status_code=429,
        content={"error": "rate_limit_exceeded", "retry_after": retry_after},
        headers={
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": str(exc.limit),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(reset_time))
        }
    )

# 503 Service Unavailable — use Retry-After when you know when you'll be back
@app.get("/maintenance")
async def maintenance():
    return JSONResponse(
        status_code=503,
        content={"error": "service_unavailable", "message": "Scheduled maintenance"},
        headers={"Retry-After": "3600"}  # try again in 1 hour
    )
```

---

## Idempotency in Payments

```python
# Full payment processing flow with idempotency
import uuid
import hashlib
from fastapi import Header

@app.post("/payments")
async def create_payment(
    payment: PaymentRequest,
    idempotency_key: str = Header(None, alias="Idempotency-Key")
):
    if not idempotency_key:
        raise HTTPException(400, "Idempotency-Key header is required")

    # Scope key to customer to prevent cross-customer replay attacks
    scoped_key = f"{payment.customer_id}:{idempotency_key}"

    # Check for existing result
    cached = await redis.get(f"idem:{scoped_key}")
    if cached:
        existing = json.loads(cached)
        # Detect conflicting payloads with same key
        if existing["payload_hash"] != hash_payload(payment):
            raise HTTPException(422, "Idempotency key reused with different payload")
        return existing["result"]  # return stored result

    # Acquire lock
    locked = await redis.set(f"idem:{scoped_key}", '{"status":"processing"}',
                              nx=True, ex=86400)
    if not locked:
        raise HTTPException(409, "A request with this idempotency key is already processing")

    # Process — also pass key to payment processor for end-to-end idempotency
    try:
        result = await stripe.create_charge(
            amount=payment.amount,
            idempotency_key=idempotency_key  # Stripe deduplicates on their end too
        )
        stored = {"status": "complete", "payload_hash": hash_payload(payment), "result": result}
        await redis.set(f"idem:{scoped_key}", json.dumps(stored), ex=86400)
        return result
    except Exception as e:
        # On failure — remove lock so client can retry
        await redis.delete(f"idem:{scoped_key}")
        raise

def hash_payload(payment: PaymentRequest) -> str:
    return hashlib.sha256(payment.json(sort_keys=True).encode()).hexdigest()
```

---

## Event Envelope Pattern (Webhooks / Events)

```python
# Standard event shape — used by Stripe, GitHub, Twilio, etc.
{
    "id": "evt_1Nq7mXGJ3H",          # unique event ID — use for deduplication
    "type": "payment.succeeded",       # dot-namespaced event type
    "api_version": "2024-01-01",       # schema version
    "created_at": "2024-01-25T10:30:00Z",
    "livemode": true,
    "data": {                          # event payload — nested for extensibility
        "object": {                    # the resource that changed
            "id": "pay_7hJq3rTv8K",
            "amount": 5000,
            "currency": "usd",
            "status": "succeeded"
        },
        "previous_attributes": {       # what changed (Stripe pattern)
            "status": "processing"
        }
    },
    "metadata": {}
}
```

---

## When to Use / Avoid

| Pattern | Use When | Avoid When |
|---------|----------|------------|
| Cursor pagination | Feeds, real-time data, large datasets | Admin tables needing page numbers (use offset) |
| Typed ID prefixes | Multi-resource APIs, public developer APIs | Internal-only APIs (adds overhead) |
| Expansion pattern | Related resource needed sometimes | Always needed — embed directly |
| Webhook signature | Any webhook receiving sensitive events | Webhooks on private networks (still do it anyway) |
| API key scoping | Multi-tenant, different client types | Single-user personal projects |
| Idempotency keys | Payments, order creation, emails, any POST | GET/DELETE — already idempotent |
| Event envelope | Webhook systems, event-driven architectures | Simple synchronous APIs |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← WebSockets](../17_websockets/cheatsheet.md) &nbsp;|&nbsp; **Next:** [OpenTelemetry →](../19_opentelemetry/cheatsheet.md)

**Related Topics:** [API Design Patterns](../16_api_design_patterns/) · [API Security](../11_api_security_production/) · [API Gateway](../15_api_gateway/)
