# ⚡ Error Handling Standards — Cheatsheet

## Learning Priority

| Priority | Topics |
|---|---|
| Must Learn | error envelope structure (code/message/details) · HTTP status code selection · pagination |
| Should Learn | field-level validation errors · filtering/sorting with whitelist · 422 customization in FastAPI |
| Good to Know | combining filter/sort/pagination in one endpoint |
| Reference | RFC 7807 ProblemDetails · error metric tracking |

---

## Error Response JSON Schema

```json
{
  "error": {
    "code":    "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {"field": "email", "message": "must be a valid email address"},
      {"field": "age",   "message": "must be at least 18"}
    ]
  }
}
```

| Field | Type | Required | Purpose |
|---|---|---|---|
| `code` | string constant | Always | Machine-readable — clients switch on this |
| `message` | string | Always | Human-readable — developers reading logs |
| `details` | array of objects | Validation errors only | Field-level errors for form UIs |

---

## Standard Error Codes

| Code | HTTP Status | When |
|---|---|---|
| `VALIDATION_ERROR` | 400 | Request data failed schema or business validation |
| `AUTHENTICATION_REQUIRED` | 401 | No valid token or API key |
| `PERMISSION_DENIED` | 403 | Authenticated, but not allowed this action |
| `NOT_FOUND` | 404 | Resource does not exist |
| `CONFLICT` | 409 | Would create a duplicate (email already taken, etc.) |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server-side bug |

---

## HTTP Status Codes by Category

### 2xx — Success
| Code | Name | Use |
|---|---|---|
| 200 | OK | Standard success (GET, PATCH, PUT) |
| 201 | Created | POST that created a resource (include `Location` header) |
| 204 | No Content | DELETE or action with no response body |

### 4xx — Client Error
| Code | Name | Use |
|---|---|---|
| 400 | Bad Request | Malformed request, general validation failure |
| 401 | Unauthorized | Not authenticated ("who are you?") |
| 403 | Forbidden | Authenticated, but not allowed |
| 404 | Not Found | Resource doesn't exist |
| 405 | Method Not Allowed | Right URL, wrong HTTP method |
| 409 | Conflict | Uniqueness constraint violation |
| 410 | Gone | Resource deleted permanently (prefer 404 if unsure) |
| 422 | Unprocessable Entity | Well-formed request, fails validation |
| 429 | Too Many Requests | Rate limit exceeded |

### 5xx — Server Error
| Code | Name | Use |
|---|---|---|
| 500 | Internal Server Error | Unhandled exception |
| 502 | Bad Gateway | Upstream service returned bad response |
| 503 | Service Unavailable | Server down or overloaded |
| 504 | Gateway Timeout | Upstream timed out |

**Never return 200 with `{"success": false}` for errors. Use the correct HTTP status code.**

---

## RFC 7807 Problem Details Format

Alternative standard format (used by some APIs):

```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 400,
  "detail": "One or more fields failed validation.",
  "instance": "/users/create",
  "errors": [
    {"field": "email", "message": "must be a valid email"}
  ]
}
```

Content-Type: `application/problem+json`

---

## Retryable vs Non-Retryable Errors

| Status | Retryable? | Action |
|---|---|---|
| 400 | No | Fix the request — it's a client bug |
| 401 | Sometimes | Refresh token, then retry once |
| 403 | No | User doesn't have permission — don't retry |
| 404 | No | Resource doesn't exist |
| 429 | Yes | Wait `Retry-After` seconds, then retry |
| 500 | Yes | Retry with exponential backoff |
| 502 | Yes | Retry with backoff |
| 503 | Yes | Wait, then retry |
| 504 | Yes | Retry with backoff |

---

## Validation Error Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "must be a valid email address",
        "value": "not-an-email"
      },
      {
        "field": "quantity",
        "message": "must be greater than 0",
        "value": -1
      }
    ]
  }
}
```

**`field` must match the request body field name exactly** so form UIs can highlight the right input.

---

## FastAPI — Override 422 Validation Error Format

```python
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        details.append({"field": field, "message": error["msg"]})

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

# Catch-all for unhandled exceptions — never leak internals
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    import logging
    logging.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}}
    )
```

---

## FastAPI — Business Logic Errors

```python
from fastapi import HTTPException

@app.post("/users")
async def create_user(body: CreateUserRequest, db=Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": "CONFLICT",
                    "message": f"Email '{body.email}' is already registered",
                    "details": [
                        {"field": "email", "message": "email address is already registered"}
                    ]
                }
            }
        )
```

---

## Pagination Quick Reference

### Offset Pagination
```python
GET /users?page=2&limit=20

# Response
{
  "data": [...],
  "pagination": {
    "page": 2, "limit": 20, "total": 500,
    "total_pages": 25, "has_next": true, "has_prev": true
  }
}
```

### Cursor Pagination
```python
GET /feed?after=eyJpZCI6MjB9&limit=20

# Response
{
  "data": [...],
  "pagination": {
    "has_next": true, "has_prev": true,
    "next_cursor": "eyJpZCI6NDB9",
    "prev_cursor": "eyJpZCI6MjF9"
  }
}
```

---

## Filtering + Sorting Pattern

```python
from enum import Enum

class OrderStatus(str, Enum):
    pending   = "pending"
    shipped   = "shipped"
    delivered = "delivered"

SORTABLE_FIELDS = {"id", "total", "created_at", "status"}

@app.get("/orders")
def list_orders(
    status: Optional[OrderStatus] = None,
    customer_id: Optional[int] = None,
    sort_by: str = Query("created_at"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    if sort_by not in SORTABLE_FIELDS:      # whitelist — never blindly accept sort column
        raise HTTPException(400, ...)

    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    # ... apply sort, pagination
```

**Always whitelist sortable fields — never `getattr(Model, user_input)` without validation.**

---

## Client-Side Error Handling Pattern

```python
match error["code"]:
    case "RATE_LIMIT_EXCEEDED":
        time.sleep(error.get("retry_after", 60))
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

---

## Navigation

**[Back to README](../README.md)**

**Theory:** [error_guide.md](./error_guide.md)

**Prev:** [← Authentication](../05_authentication/cheatsheet.md) &nbsp;|&nbsp; **Next:** [FastAPI →](../07_fastapi/cheatsheet.md)

**Related:** [03 REST Best Practices](../03_rest_best_practices/cheatsheet.md) · [05 Authentication](../05_authentication/cheatsheet.md) · [10 Testing](../10_testing_documentation/cheatsheet.md)
