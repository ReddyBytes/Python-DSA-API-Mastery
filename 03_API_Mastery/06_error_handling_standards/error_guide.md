# Error Handling, Pagination, Filtering & Sorting

## The Error That Told Me Nothing

It was a Friday afternoon. A mobile developer on another team filed a bug:

> "Your API returns an error when I try to create an account. I don't know what's wrong."

I looked at the endpoint. I looked at the server logs. I found the error.

The API was returning:

```json
{"error": "invalid input"}
```

That's it. What was invalid? Which field? What format did it expect? No one knew —
not the mobile developer, not the logs, not anything. Someone had to sit down, read
the source code, and guess what the mobile app was sending wrong.

It was a missing `@` in the email address. A validation error that would have taken
two seconds to fix if the error message had said "email: must be a valid email address."
Instead it took forty minutes of debugging across two teams.

Error handling is not a secondary concern. It's the interface your API has with
developers when things go wrong. Done well, it makes integrations fast. Done badly,
it creates silent suffering.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
error envelope structure (code/message/details) · HTTP status code selection · pagination patterns

**Should Learn** — Important for real projects, comes up regularly:
field-level validation errors · filtering and sorting with whitelist safety · 422 customization

**Good to Know** — Useful in specific situations, not always tested:
combining filtering/sorting/pagination in one endpoint

**Reference** — Know it exists, look up syntax when needed:
RFC 7807 ProblemDetails format · error metric tracking · machine-readable error catalogs

---

## 1. Error Response Design — One Consistent Structure

Every error from your API should follow the same shape. No surprises, no inconsistency.
Here's the structure that works:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {"field": "email", "message": "must be a valid email address"},
      {"field": "age", "message": "must be at least 18"}
    ]
  }
}
```

Three layers, each serving a different consumer:

> 📝 **Practice:** [Q20 · error-response-format](../api_practice_questions_100.md#q20--normal--error-response-format)

### Layer 1: Machine-Readable Code

```json
"code": "VALIDATION_ERROR"
```

A stable string constant your clients can switch on in code. Not a number. Numbers
are opaque — you have to look them up. String constants are self-documenting.

```python
# Client-side error handling becomes clean and readable:
match error["code"]:
    case "RATE_LIMIT_EXCEEDED":
        wait(error["retry_after"])
        retry()
    case "AUTHENTICATION_REQUIRED":
        refresh_token()
        retry()
    case "VALIDATION_ERROR":
        highlight_fields(error["details"])
    case "NOT_FOUND":
        show_404_page()
    case _:
        show_generic_error(error["message"])
```

Standard error codes to use consistently:

```
VALIDATION_ERROR         → 400  request data failed schema/business validation
AUTHENTICATION_REQUIRED  → 401  no valid token or API key
PERMISSION_DENIED        → 403  authenticated, but not allowed this action
NOT_FOUND                → 404  resource does not exist
CONFLICT                 → 409  would create a duplicate (email already taken, etc.)
RATE_LIMIT_EXCEEDED      → 429  too many requests
INTERNAL_ERROR           → 500  something broke on the server side
```

### Layer 2: Human-Readable Message

```json
"message": "Request validation failed"
```

For developers reading logs and error responses. Should be clear, helpful, and free
of internal implementation details (no stack traces, no SQL queries, no file paths
in production).

In development, you might log more — but the API response itself should never expose
your internals.

### Layer 3: Field-Level Details

```json
"details": [
  {"field": "email", "message": "must be a valid email address"},
  {"field": "age", "message": "must be at least 18"}
]
```

For validation errors only: tell the caller exactly which fields failed and why. The
`field` name must match the request body field name exactly. This allows:
- Form UIs to highlight specific input fields
- Developers to fix precisely the right thing
- Automated tests to assert on specific validation failures

---

## 2. FastAPI Validation Errors — Customizing the 422 Response

By default, FastAPI returns validation errors in its own format:

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "input": "not-an-email",
      "ctx": {}
    }
  ]
}
```

This is fine for development but inconsistent with your API's error envelope. Here
is how to override it so your 422 responses match your standard error structure:

```python
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    details = []
    for error in exc.errors():
        # loc is a tuple like ("body", "email") — we want just the field name
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        details.append({
            "field": field,
            "message": error["msg"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": details
            }
        }
    )
```

Now a request with `email="not-an-email"` returns your standard format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {"field": "email", "message": "value is not a valid email address"}
    ]
  }
}
```

For business logic errors (not schema errors), raise `HTTPException` with a custom
response body:

```python
from fastapi import HTTPException

@app.post("/users")
async def create_user(body: CreateUserRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": "CONFLICT",
                    "message": f"A user with email '{body.email}' already exists",
                    "details": [
                        {"field": "email", "message": "email address is already registered"}
                    ]
                }
            }
        )
    # ... create user
```

---

## 3. HTTP Status Codes — Quick Reference

> 📝 **Practice:** [Q5 · status-codes-4xx](../api_practice_questions_100.md#q5--critical--status-codes-4xx)

> 📝 **Practice:** [Q4 · status-codes-2xx](../api_practice_questions_100.md#q4--normal--status-codes-2xx)

Use the right status code. Clients — and monitoring systems — rely on them.

```
2xx — Success
  200 OK              → Standard successful GET, PATCH, PUT
  201 Created         → POST that created a resource (include Location header)
  204 No Content      → DELETE or action with no response body

4xx — Client Error (the request was wrong)
  400 Bad Request     → Malformed request, general validation error
  401 Unauthorized    → Missing or invalid credentials (name is misleading — it means
                        "not authenticated", not "not authorized")
  403 Forbidden       → Authenticated, but not allowed to do this action
  404 Not Found       → Resource does not exist (or you're hiding it for security)
  405 Method Not Allowed → Right URL, wrong HTTP method
  409 Conflict        → Would violate a uniqueness constraint
  410 Gone            → Resource existed but has been deleted (prefer 404 if unsure)
  422 Unprocessable Entity → Request is well-formed but fails validation
  429 Too Many Requests → Rate limit exceeded

5xx — Server Error (something broke on your end)
  500 Internal Server Error → Unexpected exception, bug, unhandled condition
  502 Bad Gateway           → Upstream service returned an invalid response
  503 Service Unavailable   → Server is down or overloaded (use for health check fails)
  504 Gateway Timeout       → Upstream service timed out
```

A common mistake: returning 200 with `{"success": false}` for errors. Don't do this.
Use the correct HTTP status code — that's what they're for. Client libraries, proxies,
monitoring systems, and CDNs all interpret status codes. Wrapping failures in 200
responses breaks all of them.

> 📝 **Practice:** [Q6 · http-404-security](../api_practice_questions_100.md#q6--thinking--http-404-security)

---

## 4. Pagination Patterns

Never return an unbounded list. A table with 50 rows is fine. A table with 500,000
rows returned in one response will crash your server, exhaust the client's memory, and
time out on slow connections.

Paginate every collection endpoint. Always.

### Offset Pagination

The simple approach. Works well for most use cases:

```python
from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(20, ge=1, le=100, description="Items per page (max 100)")

@app.get("/users")
def list_users(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    offset = (pagination.page - 1) * pagination.limit

    users = db.query(User).offset(offset).limit(pagination.limit).all()
    total = db.query(User).count()
    total_pages = (total + pagination.limit - 1) // pagination.limit

    return {
        "data": users,
        "pagination": {
            "page": pagination.page,
            "limit": pagination.limit,
            "total": total,
            "total_pages": total_pages,
            "has_next": pagination.page < total_pages,
            "has_prev": pagination.page > 1,
        }
    }
```

This powers the most common client behavior: "page 3 of 47" in admin UIs. Simple to
implement, simple to understand.

The one weakness: if rows are inserted at the top while a user is paginating, items
can shift between pages. Row 61 on page 4 becomes row 64 after three insertions — the
user misses rows 61-63. For most admin tools, this is acceptable.

### Cursor Pagination

For feeds, timelines, and large live datasets, cursor pagination is stable:

```python
import base64
import json
from typing import Optional

def encode_cursor(data: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(data).encode()).decode()

def decode_cursor(cursor: str) -> dict:
    return json.loads(base64.urlsafe_b64decode(cursor.encode()))

@app.get("/feed")
def list_feed(
    limit: int = Query(20, ge=1, le=100),
    after: Optional[str] = Query(None, description="Cursor from previous response"),
    db: Session = Depends(get_db)
):
    query = db.query(Post).order_by(Post.id.desc())

    if after:
        cursor_data = decode_cursor(after)
        query = query.filter(Post.id < cursor_data["id"])

    posts = query.limit(limit + 1).all()  # fetch one extra to check for next page
    has_next = len(posts) > limit
    posts = posts[:limit]

    next_cursor = encode_cursor({"id": posts[-1].id}) if has_next and posts else None
    prev_cursor = encode_cursor({"id": posts[0].id}) if posts else None

    return {
        "data": posts,
        "pagination": {
            "has_next": has_next,
            "next_cursor": next_cursor,
            "prev_cursor": prev_cursor,
        }
    }
```

The client passes `?after=<cursor>` to get the next page. The cursor encodes a
position (here, the last item's `id`). New items added to the top don't affect your
position in the feed — you always see exactly the items after your cursor.

Cursor pagination doesn't support "jump to page 47" — it's forward/backward only.
That's the tradeoff. Use it where stability matters more than random access.

---

## 5. Filtering and Sorting

Users want to find specific data. Filtering and sorting let them narrow down and
order the data they receive. Both live in query parameters.

### Filtering

```python
from enum import Enum
from typing import Optional
from fastapi import Query

class OrderStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

@app.get("/orders")
def list_orders(
    status: Optional[OrderStatus] = None,
    customer_id: Optional[int] = None,
    sort_by: str = Query("created_at", description="Field to sort by"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    query = db.query(Order)

    # Apply filters only when provided
    if status:
        query = query.filter(Order.status == status)
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)

    # Sorting — safely get the column, fall back to created_at
    sort_col = getattr(Order, sort_by, Order.created_at)
    query = query.order_by(
        sort_col.desc() if order == "desc" else sort_col.asc()
    )

    return query.all()
```

A request like `GET /orders?status=pending&customer_id=42&sort_by=total&order=asc`
filters to pending orders for customer 42, sorted by total ascending.

Using an `Enum` for `status` gives you automatic validation: passing `?status=invalid`
returns a 422 before your handler runs.

### Protecting Against Unsafe Sort Columns

The `getattr(Order, sort_by, Order.created_at)` pattern is convenient but dangerous
if `sort_by` can be any string — an attacker could sort by internal columns, trigger
expensive operations, or extract timing information.

Explicitly whitelist sortable fields:

```python
SORTABLE_FIELDS = {"id", "total", "created_at", "status"}

@app.get("/orders")
def list_orders(
    sort_by: str = Query("created_at"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    if sort_by not in SORTABLE_FIELDS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"Cannot sort by '{sort_by}'",
                    "details": [
                        {
                            "field": "sort_by",
                            "message": f"must be one of: {', '.join(sorted(SORTABLE_FIELDS))}"
                        }
                    ]
                }
            }
        )

    sort_col = getattr(Order, sort_by)
    query = db.query(Order).order_by(
        sort_col.desc() if order == "desc" else sort_col.asc()
    )
    return query.all()
```

### Combining Everything

Here's a production-style list endpoint that combines pagination, filtering,
and sorting into one cohesive handler:

```python
from fastapi import FastAPI, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class OrderStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

SORTABLE_ORDER_FIELDS = {"id", "total", "created_at", "status"}

@app.get("/v1/orders")
def list_orders(
    # Filters
    status: Optional[OrderStatus] = None,
    customer_id: Optional[int] = None,
    min_total: Optional[float] = None,
    max_total: Optional[float] = None,
    # Sorting
    sort_by: str = Query("created_at"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    # Pagination
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    if sort_by not in SORTABLE_ORDER_FIELDS:
        raise HTTPException(status_code=400, detail={
            "error": {"code": "VALIDATION_ERROR",
                      "message": f"Invalid sort field: {sort_by}"}
        })

    query = db.query(Order)

    if status:
        query = query.filter(Order.status == status)
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    if min_total is not None:
        query = query.filter(Order.total >= min_total)
    if max_total is not None:
        query = query.filter(Order.total <= max_total)

    sort_col = getattr(Order, sort_by)
    query = query.order_by(sort_col.desc() if order == "desc" else sort_col.asc())

    total = query.count()
    offset = (pagination.page - 1) * pagination.limit
    items = query.offset(offset).limit(pagination.limit).all()
    total_pages = (total + pagination.limit - 1) // pagination.limit

    return {
        "data": items,
        "pagination": {
            "page": pagination.page,
            "limit": pagination.limit,
            "total": total,
            "total_pages": total_pages,
            "has_next": pagination.page < total_pages,
        }
    }
```

A real request: `GET /v1/orders?status=pending&sort_by=total&order=desc&page=2&limit=10`
Returns page 2 of pending orders, sorted by total descending, 10 per page. The
response tells you how many total matching orders exist so the UI can render a
page count.

---

## The Complete Error Handling Pattern

Put it all together in a structured error handler you use across the whole application:

```python
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()

# Override validation errors → consistent format
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = [
        {
            "field": ".".join(str(loc) for loc in err["loc"] if loc != "body"),
            "message": err["msg"]
        }
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDATION_ERROR",
                            "message": "Request validation failed",
                            "details": details}}
    )

# Catch all unexpected exceptions → never leak internals
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Log the full exception server-side (with traceback)
    import logging
    logging.exception("Unhandled exception on %s %s", request.method, request.url)

    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR",
                            "message": "An unexpected error occurred"}}
    )
```

---

## Summary

```
Error Response Structure:
  { "error": { "code": "...", "message": "...", "details": [...] } }
  code    → machine-readable string constant clients switch on
  message → human-readable description for developers
  details → field-level errors for validation failures

FastAPI Customization:
  @app.exception_handler(RequestValidationError) → override 422 format
  @app.exception_handler(Exception) → catch-all for unhandled errors
  raise HTTPException(status_code=409, detail={...}) → business logic errors

Status Codes That Matter:
  200 OK, 201 Created, 204 No Content
  400 Bad Request, 401 Unauthorized, 403 Forbidden
  404 Not Found, 409 Conflict, 422 Unprocessable Entity
  429 Too Many Requests, 500 Internal Server Error

Pagination:
  Offset  → ?page=2&limit=20  → simple, jump to any page, not stable under inserts
  Cursor  → ?after=<cursor>   → stable, scales, forward/backward only
  Always return total, page, limit, has_next in response

Filtering:
  Query params for each filterable field → ?status=pending&customer_id=42
  Use Enum types for constrained string fields → automatic 422 on bad values

Sorting:
  ?sort_by=created_at&order=desc
  Whitelist allowed sort fields — never blindly getattr from user input
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Authentication & Authorization](../05_authentication/securing_apis.md) &nbsp;|&nbsp; **Next:** [Why FastAPI →](../07_fastapi/why_fastapi.md)

**Related Topics:** [REST Best Practices](../03_rest_best_practices/patterns.md) · [Authentication & Authorization](../05_authentication/securing_apis.md) · [Testing APIs](../10_testing_documentation/testing_apis.md)
