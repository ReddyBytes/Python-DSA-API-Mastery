# API Design Patterns — Practice

> 12 questions covering REST conventions, pagination, versioning, error design, idempotency, and rate limiting headers.

---


## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| [Q1](#q1) | REST Resource Naming — Name REST endpoints | 🟢 |
| [Q2](#q2) | HTTP Methods & Status Codes — Map CRUD to HTTP | 🟢 |
| [Q3](#q3) | Offset Pagination — Implement offset pagination | 🟡 |
| [Q4](#q4) | Cursor Pagination — Implement cursor-based pagination | 🟡 |
| [Q5](#q5) | API Versioning — Add URL versioning to existing endpoints | 🟡 |
| [Q6](#q6) | Error Response Design — Design error response envelope | 🟡 |
| [Q7](#q7) | Idempotency — Add idempotency key to POST endpoint | 🟡 |
| [Q8](#q8) | Rate Limit Headers — Write rate limit headers | 🟡 |
| [Q9](#q9) | API Deprecation — Design deprecation strategy with Sunset header | 🟠 |
| [Q10](#q10) | Content Negotiation — Implement content negotiation (JSON vs XML) | 🟠 |
| [Q11](#q11) | Versioned Migration Plan — Design versioned API migration plan | 🟠 |
| [Q12](#q12) | Capstone — Design complete REST API for e-commerce orders | 🟠 |

---

<a id="q1"></a>

### Q1 · REST Resource Naming — Name REST endpoints 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


Design the REST endpoints for a blog API with `posts` and `comments`. List all endpoints for CRUD operations on posts, plus endpoints for comments nested under posts.


<details><summary>💡 Hint</summary>Use plural nouns. Comments are a sub-resource of posts: /posts/{id}/comments</details>

<details><summary>✅ Answer</summary>

```python
# Posts
GET    /posts              # list all posts
POST   /posts              # create a post
GET    /posts/{id}         # get a specific post
PUT    /posts/{id}         # replace a post
PATCH  /posts/{id}         # update fields on a post
DELETE /posts/{id}         # delete a post

# Comments (nested under post)
GET    /posts/{id}/comments       # list comments for a post
POST   /posts/{id}/comments       # add a comment
GET    /posts/{id}/comments/{cid} # get specific comment
DELETE /posts/{id}/comments/{cid} # delete a comment
```
**Why:** Nested resources show ownership. Plural nouns + HTTP methods replace verbs in URLs.
</details>

---

<a id="q2"></a>

### Q2 · HTTP Methods & Status Codes — Map CRUD to HTTP 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


For each operation below, give the HTTP method AND the success status code:
1. Create a new user
2. Fetch a user's profile
3. Update a user's email (partial update)
4. Replace an entire user record
5. Delete a user
6. Action results in "not found"
7. Action results in "duplicate email" (conflict)


<details><summary>💡 Hint</summary>Create = 201, read = 200, delete = 204 (no body), conflict = 409</details>

<details><summary>✅ Answer</summary>

```python
# 1. Create user
POST /users  →  201 Created

# 2. Fetch user
GET /users/42  →  200 OK

# 3. Partial update
PATCH /users/42  →  200 OK

# 4. Full replace
PUT /users/42  →  200 OK

# 5. Delete
DELETE /users/42  →  204 No Content

# 6. Not found
GET /users/999  →  404 Not Found

# 7. Conflict
POST /users (duplicate email)  →  409 Conflict
```
**Why:** Correct status codes let clients handle responses programmatically without parsing the body.
</details>

---

<a id="q3"></a>

### Q3 · Offset Pagination — Implement offset pagination 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


Write a function `paginate_users(offset, limit)` that returns a paginated response dict with `data`, `pagination.offset`, `pagination.limit`, and `pagination.total`. Assume a `USERS` list is available.


<details><summary>💡 Hint</summary>slice = USERS[offset:offset+limit]; total = len(USERS)</details>

<details><summary>✅ Answer</summary>

```python
USERS = [{"id": i, "name": f"User_{i}"} for i in range(1, 101)]

def paginate_users(offset: int = 0, limit: int = 10) -> dict:
    page = USERS[offset: offset + limit]
    return {
        "data": page,
        "pagination": {
            "offset": offset,
            "limit":  limit,
            "total":  len(USERS),
        }
    }

# GET /users?offset=20&limit=5
print(paginate_users(offset=20, limit=5))
```
**Why:** Offset lets clients jump to any page, but is unstable under concurrent inserts.
</details>

---

<a id="q4"></a>

### Q4 · Cursor Pagination — Implement cursor-based pagination 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


Write `paginate_with_cursor(cursor, limit)` that returns `data` and `next_cursor` (base64-encoded last item id). Accept `cursor=None` to start from the beginning. Use the same `USERS` list.


<details><summary>💡 Hint</summary>base64.b64encode(json.dumps({"id": last_id}).encode()).decode()</details>

<details><summary>✅ Answer</summary>

```python
import base64, json

USERS = [{"id": i, "name": f"User_{i}"} for i in range(1, 101)]

def encode_cursor(last_id: int) -> str:
    return base64.b64encode(json.dumps({"id": last_id}).encode()).decode()

def decode_cursor(cursor: str) -> int:
    return json.loads(base64.b64decode(cursor.encode()))["id"]

def paginate_with_cursor(cursor: str = None, limit: int = 10) -> dict:
    if cursor:
        last_id = decode_cursor(cursor)
        start   = next((i for i, u in enumerate(USERS) if u["id"] == last_id), -1) + 1
    else:
        start = 0

    page = USERS[start: start + limit]
    next_cursor = encode_cursor(page[-1]["id"]) if len(page) == limit else None

    return {"data": page, "next_cursor": next_cursor, "has_more": next_cursor is not None}
```
**Why:** Cursor is stable under inserts/deletes. Used by GitHub, Stripe, Twitter.
</details>

---

<a id="q5"></a>

### Q5 · API Versioning — Add URL versioning to existing endpoints 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Given a FastAPI app with `GET /users/{id}`, add URL versioning so:
- `/v1/users/{id}` returns `{"id": id, "name": "Alice"}`
- `/v2/users/{id}` returns `{"user": {"id": id, "name": "Alice"}}`


<details><summary>💡 Hint</summary>Use APIRouter(prefix="/v1") and APIRouter(prefix="/v2"), then include both in the app</details>

<details><summary>✅ Answer</summary>

```python
from fastapi import FastAPI, APIRouter

app = FastAPI()
v1 = APIRouter(prefix="/v1")
v2 = APIRouter(prefix="/v2")

@v1.get("/users/{user_id}")
def get_user_v1(user_id: int):
    return {"id": user_id, "name": "Alice"}   # ← flat format

@v2.get("/users/{user_id}")
def get_user_v2(user_id: int):
    return {"user": {"id": user_id, "name": "Alice"}}  # ← envelope format

app.include_router(v1)
app.include_router(v2)
```
**Why:** URL versioning is the most discoverable approach — visible in browser, curl, logs.
</details>

---

<a id="q6"></a>

### Q6 · Error Response Design — Design error response envelope 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


Write a `problem_detail()` helper that returns a JSON response following RFC 7807 (Problem Details). Fields: `type`, `title`, `status`, `detail`. Use it to return a 422 validation error for "email is required".


<details><summary>💡 Hint</summary>RFC 7807 fields: type (URL), title (human string), status (int), detail (specific message)</details>

<details><summary>✅ Answer</summary>

```python
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

# Usage
response = problem_detail(
    status=422,
    title="Validation Error",
    detail="email is required"
)
# {"type": "https://...", "title": "Validation Error", "status": 422, "detail": "..."}
```
**Why:** Consistent error shape means clients can parse errors without checking message strings.
</details>

---

<a id="q7"></a>

### Q7 · Idempotency — Add idempotency key to POST endpoint 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


Write a FastAPI route `POST /payments` that accepts an `Idempotency-Key` header. If the same key is used twice, return the cached response instead of processing again. Use a simple dict as the store.


<details><summary>💡 Hint</summary>Store {key: response_dict} in a module-level dict; check before processing</details>

<details><summary>✅ Answer</summary>

```python
from fastapi import FastAPI, Header
import uuid

app = FastAPI()
_store = {}    # in production: use Redis

@app.post("/payments")
def create_payment(
    amount: float,
    idempotency_key: str = Header(None)
):
    if idempotency_key and idempotency_key in _store:
        return _store[idempotency_key]   # ← replay, no double charge

    result = {
        "payment_id": str(uuid.uuid4()),
        "amount":     amount,
        "status":     "processed",
    }

    if idempotency_key:
        _store[idempotency_key] = result

    return result
```
**Why:** Idempotency keys prevent double charges when clients retry on network timeout.
</details>

---

<a id="q8"></a>

### Q8 · Rate Limit Headers — Write rate limit headers 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


Write a FastAPI middleware (or route dependency) that adds `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `Retry-After` headers to responses. Limit = 5 requests per minute per client IP.


<details><summary>💡 Hint</summary>Use request.client.host as the client key; return 429 + Retry-After when limit exceeded</details>

<details><summary>✅ Answer</summary>

```python
from fastapi import FastAPI, Request, Response
import time, collections

app = FastAPI()
LIMIT   = 5
WINDOW  = 60   # seconds
_counts = collections.defaultdict(list)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client = request.client.host
    now    = time.time()
    window = [t for t in _counts[client] if now - t < WINDOW]
    _counts[client] = window

    remaining = max(0, LIMIT - len(window))

    if len(window) >= LIMIT:
        return Response(
            status_code=429,
            headers={
                "X-RateLimit-Limit":     str(LIMIT),
                "X-RateLimit-Remaining": "0",
                "Retry-After":           str(int(WINDOW - (now - window[0]))),
            }
        )

    _counts[client].append(now)
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"]     = str(LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(remaining - 1)
    return response
```
**Why:** Rate limit headers tell clients exactly how much quota they have left, enabling polite backoff.
</details>

---

<a id="q9"></a>

### Q9 · API Deprecation — Design deprecation strategy with Sunset header 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


Add `Deprecation`, `Sunset`, and `Link` headers to a `/v1/users/{id}` endpoint. The v1 sunset date is 2026-01-01. The successor is `/v2/users/{id}`.


<details><summary>💡 Hint</summary>Deprecation: true, Sunset: RFC 7231 date string, Link: rel="successor-version"</details>

<details><summary>✅ Answer</summary>

```python
from fastapi import APIRouter, Response

v1 = APIRouter(prefix="/v1")

@v1.get("/users/{user_id}")
def get_user_v1(user_id: int, response: Response):
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"]      = "Thu, 01 Jan 2026 00:00:00 GMT"
    response.headers["Link"]        = f'</v2/users/{user_id}>; rel="successor-version"'
    return {"id": user_id, "name": "Alice"}
```
**Why:** Sunset header is a machine-readable shutdown date. API clients and monitoring tools can alert teams automatically.
</details>

---

<a id="q10"></a>

### Q10 · Content Negotiation — Implement content negotiation (JSON vs XML) 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


Write a FastAPI route that checks the `Accept` header and returns either JSON or plain-text XML. If the client sends `Accept: application/xml`, return XML. Otherwise return JSON.


<details><summary>💡 Hint</summary>Check request.headers.get("accept", ""). Return Response(content=xml_str, media_type="application/xml") for XML.</details>

<details><summary>✅ Answer</summary>

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int, request: Request):
    user = {"id": user_id, "name": "Alice"}
    accept = request.headers.get("accept", "application/json")

    if "application/xml" in accept:
        xml = f'<user><id>{user["id"]}</id><name>{user["name"]}</name></user>'
        return Response(content=xml, media_type="application/xml")

    return JSONResponse(content=user)   # ← default JSON
```
**Why:** Content negotiation lets one endpoint serve multiple formats without separate URLs.
</details>

---

<a id="q11"></a>

### Q11 · Versioned Migration Plan — Design versioned API migration plan 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


Design a 4-step migration plan to move clients from `/v1/users` to `/v2/users` without downtime. Consider: announcement, parallel support, monitoring, and sunset.


<details><summary>💡 Hint</summary>Plan: launch v2 → deprecation headers on v1 → track v1 usage → sunset date → remove v1</details>

<details><summary>✅ Answer</summary>

```python
"""
Migration plan: v1 → v2

Step 1 — Launch v2 (parallel):
  - Deploy /v2/users alongside /v1/users
  - No changes to v1 — existing clients unaffected

Step 2 — Announce deprecation:
  - Add Deprecation + Sunset headers to all v1 responses
  - Notify API consumers via email / changelog
  - Set Sunset date 6+ months out

Step 3 — Monitor v1 usage:
  - Log all requests to v1 endpoints by API key
  - Identify which API key holders still hit v1
  - Reach out individually to straggler clients

Step 4 — Sunset:
  - On Sunset date, return 410 Gone with body:
    {"message": "v1 API removed. Migrate to /v2/"}
  - Keep 410 response for 30 days, then remove route
"""
```
**Why:** Parallel support + monitoring prevents surprise breakage. 6-month window respects slow-moving clients (mobile apps).
</details>

---

<a id="q12"></a>

### Q12 · Capstone — Design complete REST API for e-commerce orders 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


Design the complete REST API for an e-commerce order system. Include:
- All endpoints (list, create, get, update status, cancel)
- HTTP methods + status codes
- Pagination approach
- Idempotency for order creation
- Rate limit headers
- Error envelope format


<details><summary>💡 Hint</summary>Think: what resources exist? What actions on each? What can go wrong? How do you prevent double orders?</details>

<details><summary>✅ Answer</summary>

```python
"""
Order API Design

Endpoints:
  GET    /v1/orders              → 200, paginated list (cursor-based)
  POST   /v1/orders              → 201, creates order
  GET    /v1/orders/{id}         → 200, single order
  PATCH  /v1/orders/{id}/status  → 200, update status
  POST   /v1/orders/{id}/cancel  → 200, cancel order

Pagination:
  GET /v1/orders?cursor=...&limit=20
  Response: {data: [...], next_cursor: "...", has_more: true}

Idempotency (POST /v1/orders):
  Header: Idempotency-Key: <uuid>
  Same key → same response, no duplicate order

Rate limiting:
  Headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset

Error format (RFC 7807):
  {type: "...", title: "...", status: 422, detail: "quantity must be > 0"}

Status codes:
  201 — order created
  404 — order not found
  409 — order already cancelled
  422 — invalid quantity/items
  429 — rate limit exceeded
"""
```
**Why:** Good API design answers: what can clients do, how do they page through data, how are errors communicated, and how are retries safe.
</details>

---

## 🧭 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 💻 Practice Local | [practice_local.py](./practice_local.py) |
| ⬆️ Root Practice | [../practice.md](../practice.md) |
| ⚡ Scalability | [../02_scalability_caching_patterns/practice.md](../02_scalability_caching_patterns/practice.md) |

---

**[🏠 Back to README](../../README.md)**

**Prev:** [← Theory](./theory.md) | **Next:** [Scalability Practice →](../02_scalability_caching_patterns/practice.md)

**Related Topics:** [API Design Theory](./theory.md) · [Root Theory](../theory.md) · [Interview Q&A](../interview.md)
