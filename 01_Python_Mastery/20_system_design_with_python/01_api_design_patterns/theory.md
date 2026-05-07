# API Design Patterns — Theory

> Designing an API is like designing a restaurant menu: clear labels, consistent format, and no surprises. A customer (client) should know exactly what to order (endpoint), what they'll get back (response), and how much it costs (rate limit).

---

## 📌 Learning Priority

**Must Learn**: REST conventions, status codes, pagination, versioning
**Should Learn**: idempotency, HATEOAS basics, content negotiation
**Good to Know**: OpenAPI/Swagger generation, gRPC tradeoffs
**Reference**: JSON:API spec, JSON Patch

---

## 1. REST API Conventions

Think of HTTP methods as verbs and endpoints as nouns. You don't say "getUser" — you say "GET /users/42". The verb is the method, the noun is the URL.

**REST** (Representational State Transfer) is a set of rules for building predictable, consistent APIs.

### Resource naming

Use plural nouns. Never use verbs in URLs.

```
# Good
GET  /users           ← list all users
GET  /users/42        ← get user 42
POST /users           ← create a new user
PUT  /users/42        ← replace user 42
DELETE /users/42      ← remove user 42

# Bad — verbs in URL
GET /getUser/42
POST /createOrder
```

### HTTP methods

| Method | Action | Safe? | Idempotent? |
|--------|--------|-------|-------------|
| GET | Read | Yes | Yes |
| POST | Create | No | No |
| PUT | Replace | No | Yes |
| PATCH | Update fields | No | No |
| DELETE | Remove | No | Yes |

**Safe** means no side effects. **Idempotent** means calling it 10 times = same result as calling it once.

### HTTP status codes

```
2xx  Success
  200 OK            ← standard success
  201 Created       ← POST succeeded, resource created
  204 No Content    ← DELETE succeeded, nothing to return

4xx  Client error
  400 Bad Request   ← malformed input
  401 Unauthorized  ← not authenticated
  403 Forbidden     ← authenticated but no permission
  404 Not Found     ← resource doesn't exist
  409 Conflict      ← duplicate resource
  422 Unprocessable ← valid JSON but invalid business logic
  429 Too Many      ← rate limit hit

5xx  Server error
  500 Internal      ← unhandled server crash
  503 Unavailable   ← downstream service down
```

> 📝 **Practice:** [Q1 — Name REST endpoints](./practice.md#q1--rest-resource-naming---name-rest-endpoints-) · [Q2 — HTTP methods + status codes](./practice.md#q2--http-methods--status-codes---map-crud-to-http-)

---

## 2. Pagination

Imagine searching Google for "Python tutorials" — you don't get all 900 million results at once. You get page 1 of 10 results. That's pagination.

Without pagination, a single request for `/users` on a large system could return millions of rows — crashing the client and the server.

### Offset pagination

The simplest approach. Skip N records, return the next M.

```python
# GET /users?offset=20&limit=10
# Returns users 21-30

def get_users(offset: int = 0, limit: int = 10):
    return db.query(
        "SELECT * FROM users ORDER BY id LIMIT %s OFFSET %s",
        limit, offset
    )

# Response
{
    "data": [...],
    "pagination": {
        "offset": 20,
        "limit": 10,
        "total": 1500      # ← total count (expensive on large tables)
    }
}
```

Problem: if someone inserts a row while you paginate, you skip or duplicate records.

### Cursor-based pagination

Instead of "skip 20", use a pointer (cursor) to the last seen item.

```python
# GET /users?cursor=eyJ1c2VyX2lkIjogMjB9&limit=10
# cursor is base64-encoded {"user_id": 20}

import base64, json

def encode_cursor(user_id: int) -> str:
    return base64.b64encode(json.dumps({"user_id": user_id}).encode()).decode()

def decode_cursor(cursor: str) -> dict:
    return json.loads(base64.b64decode(cursor.encode()).decode())

# Response
{
    "data": [...],
    "next_cursor": "eyJ1c2VyX2lkIjogMzB9",   # ← pointer to next page
    "has_more": true
}
```

Cursor pagination is stable — no skip/duplicate problem. Used by GitHub, Twitter, Stripe.

| | Offset | Cursor |
|---|---|---|
| Simple to implement | Yes | No |
| Stable under inserts | No | Yes |
| Total count available | Yes | No |
| Works with random access (jump to page 5) | Yes | No |

> 📝 **Practice:** [Q3 — Offset pagination](./practice.md#q3--offset-pagination---implement-offset-pagination-) · [Q4 — Cursor pagination](./practice.md#q4--cursor-pagination---implement-cursor-based-pagination-)

---

## 3. Versioning

Imagine a mobile app your users installed 2 years ago. They haven't updated it. You want to change your API. How do you do that without breaking their app?

The answer is **API versioning** — you keep the old API working while building the new one.

### URL path versioning (most common)

```python
# Old version still works
GET /v1/users/42

# New version with breaking changes
GET /v2/users/42

# FastAPI example
from fastapi import APIRouter

v1_router = APIRouter(prefix="/v1")
v2_router = APIRouter(prefix="/v2")

@v1_router.get("/users/{user_id}")
def get_user_v1(user_id: int):
    return {"id": user_id, "name": "Alice"}   # ← old format

@v2_router.get("/users/{user_id}")
def get_user_v2(user_id: int):
    return {"user": {"id": user_id, "name": "Alice"}}  # ← new envelope format
```

### Header versioning

```
GET /users/42
Accept: application/vnd.myapi.v2+json
```

More REST-pure but harder to test in a browser.

### Query param versioning

```
GET /users/42?version=2
```

Easy to add but pollutes query params.

> 📝 **Practice:** [Q5 — URL versioning](./practice.md#q5--api-versioning---add-url-versioning-to-existing-endpoints-)

---

## 4. Request/Response Design

A consistent response envelope means clients always know where to find data, errors, and metadata — no guessing.

### Envelope pattern

```python
# Consistent success envelope
{
    "data": { ... },           # ← the actual payload
    "meta": {                  # ← pagination, timing
        "page": 1,
        "total": 150
    }
}

# Consistent error envelope (RFC 7807 Problem Details)
{
    "type":     "https://api.example.com/errors/validation",
    "title":    "Validation Error",
    "status":   422,
    "detail":   "email must be a valid address",
    "instance": "/users/create"
}
```

```python
# FastAPI: always return consistent errors
from fastapi import HTTPException
from fastapi.responses import JSONResponse

def problem_detail(status: int, title: str, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "type":   f"https://api.example.com/errors/{status}",
            "title":  title,
            "status": status,
            "detail": detail,
        }
    )
```

> 📝 **Practice:** [Q6 — RFC 7807 error envelope](./practice.md#q6--error-response-design---design-error-response-envelope-)

---

## 5. Idempotency

Imagine clicking "Pay" on a checkout page. The page hangs. Did it charge you? You click again. Did it charge you twice?

**Idempotency** means: running the same operation multiple times has the same effect as running it once.

- GET is always idempotent (reading doesn't change state)
- PUT is idempotent (setting a value 10 times = same as once)
- POST is NOT idempotent by default (calling it 10 times creates 10 orders)

### Idempotency keys

For POST endpoints that must be safe to retry (payments, order creation), clients send a unique key:

```python
# Client sends header:
# Idempotency-Key: a3f9-12bc-4d88-9001

from fastapi import Header, HTTPException
import hashlib

# Simple in-memory store (use Redis in production)
_idempotency_store = {}

def check_idempotency(key: str, result: dict = None) -> dict | None:
    if key in _idempotency_store:
        return _idempotency_store[key]   # ← replay cached response
    if result:
        _idempotency_store[key] = result
    return None

@app.post("/orders")
def create_order(
    order: OrderRequest,
    idempotency_key: str = Header(None)
):
    if idempotency_key:
        cached = check_idempotency(idempotency_key)
        if cached:
            return cached   # ← same response, no double-charge
    
    result = process_order(order)
    
    if idempotency_key:
        check_idempotency(idempotency_key, result)
    
    return result
```

> 📝 **Practice:** [Q7 — Idempotency key](./practice.md#q7--idempotency---add-idempotency-key-to-post-endpoint-)

---

## 6. Rate Limiting in API Design

A bouncer at a club only lets in 100 people per hour. The API equivalent is a rate limiter — it lets through N requests per time window, then sends 429.

### Rate limit headers

Always tell clients their current quota status:

```python
from fastapi import Response

@app.get("/data")
def get_data(response: Response, user_id: str = "anon"):
    allowed, limit_info = rate_limiter.check(user_id)
    
    # Always return rate limit headers
    response.headers["X-RateLimit-Limit"]     = "100"
    response.headers["X-RateLimit-Remaining"] = str(limit_info["remaining"])
    response.headers["X-RateLimit-Reset"]     = str(limit_info["reset_at"])
    
    if not allowed:
        response.headers["Retry-After"] = str(limit_info["retry_after"])
        return Response(status_code=429)   # ← Too Many Requests
    
    return {"data": "..."}
```

```
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1735000000
Retry-After: 42
```

> 📝 **Practice:** [Q8 — Rate limit headers](./practice.md#q8--rate-limit-headers---write-rate-limit-headers-)

---

## 7. API Versioning Migrations — Deprecation

You can't delete an API version overnight — mobile apps in the wild may still use it. Deprecation is a graceful shutdown process.

```python
# Add deprecation headers to old version responses
@v1_router.get("/users/{user_id}")
def get_user_v1(user_id: int, response: Response):
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"]      = "Sat, 01 Jan 2026 00:00:00 GMT"  # ← end date
    response.headers["Link"] = '</v2/users/{id}>; rel="successor-version"'
    
    return {"id": user_id, "name": "Alice"}   # ← old format still works
```

```
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sat, 01 Jan 2026 00:00:00 GMT
Link: </v2/users/42>; rel="successor-version"
```

Best practices:
- Announce deprecation at least 6 months ahead
- Keep v1 alive until Sunset date
- Log v1 usage so you know how many clients still use it
- Send email warnings to API key holders still hitting v1

> 📝 **Practice:** [Q9 — Deprecation with Sunset header](./practice.md#q9--api-deprecation---design-deprecation-strategy-with-sunset-header-)

---

## 8. Common Mistakes

```
Mistake                          Fix
─────────────────────────────────────────────────────────────
Verbs in URLs (/getUser)         Use nouns + HTTP methods
Inconsistent status codes        Use 201 for create, 204 for delete
No pagination on list endpoints  Always paginate; default limit=20
Returning 200 for errors         Use 4xx/5xx codes properly
No versioning from day 1         Start with /v1/ even for MVPs
Breaking changes without notice  Use deprecation + Sunset headers
No error envelope                Use RFC 7807 Problem Details
No idempotency on payments       Add Idempotency-Key header
```

---

## 🧭 Navigation

| | |
|---|---|
| ⬆️ Root Theory | [../theory.md](../theory.md) |
| 💻 Practice | [practice.md](./practice.md) |
| ⚡ Scalability | [../02_scalability_caching_patterns/theory.md](../02_scalability_caching_patterns/theory.md) |

---

**[🏠 Back to README](../../README.md)**

**Prev:** [← Root Theory](../theory.md) | **Next:** [Scalability & Caching →](../02_scalability_caching_patterns/theory.md)

**Related Topics:** [Root Theory](../theory.md) · [Scalability & Caching](../02_scalability_caching_patterns/theory.md) · [Interview Q&A](../interview.md)
