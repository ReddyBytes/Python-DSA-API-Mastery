# ⚡ FastAPI — Cheatsheet

## Learning Priority

| Priority | Topics |
|---|---|
| Must Learn | Pydantic models (Field/validators/nested) · dependency injection · route decorators |
| Should Learn | APIRouter (prefixes/tags) · custom exception handlers · background tasks · middleware |
| Good to Know | yield pattern for DB sessions · chaining dependencies |
| Reference | response streaming · custom OpenAPI schema |

---

## Route Decorators

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items")           # GET
@app.post("/items")          # POST
@app.put("/items/{id}")      # PUT (full replace)
@app.patch("/items/{id}")    # PATCH (partial update)
@app.delete("/items/{id}")   # DELETE
```

### Decorator Options

```python
@app.post(
    "/items",
    status_code=201,                  # override default 200
    response_model=ItemResponse,      # shape of the response (filters + documents)
    response_model_exclude_unset=True, # omit unset optional fields
    tags=["items"],                   # Swagger grouping
    summary="Create an item",
    deprecated=True,                  # marks as deprecated in Swagger
)
async def create_item(body: CreateItem):
    ...
```

---

## Path, Query, and Body Parameters

```python
from fastapi import FastAPI, Path, Query, Body
from pydantic import BaseModel

app = FastAPI()

class UpdateItem(BaseModel):
    name: str
    price: float

# Path parameter
@app.get("/items/{item_id}")
def get_item(item_id: int = Path(gt=0, description="Item ID")):
    ...

# Query parameters (from URL ?name=foo&active=true)
@app.get("/items")
def list_items(
    name: str | None = Query(None, min_length=1),
    active: bool = Query(True),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    ...

# Request body
@app.patch("/items/{item_id}")
def update_item(item_id: int, body: UpdateItem):
    ...

# Multiple sources at once
@app.post("/items/{category_id}")
def create_item(
    category_id: int,                    # path
    source: str = Query("web"),          # query
    body: CreateItem = Body(...),        # body
):
    ...
```

---

## Pydantic Request / Response Models

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum

class ItemStatus(str, Enum):
    active   = "active"
    inactive = "inactive"

# Request body — what client sends
class CreateItemRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    price: Decimal = Field(gt=0)
    status: ItemStatus = ItemStatus.active
    tags: list[str] = []

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v):
        return v.strip()

# Response — what API returns (filters out fields not listed here)
class ItemResponse(BaseModel):
    id: int
    name: str
    price: Decimal
    status: ItemStatus
    created_at: datetime

    class Config:
        from_attributes = True          # read from ORM objects


@app.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(body: CreateItemRequest):
    # body is validated before this runs
    # return value is filtered through ItemResponse
    ...
```

---

## Dependency Injection

```python
from fastapi import Depends

# Pagination dependency — reused across many routes
def get_pagination(page: int = 1, limit: int = 20) -> dict:
    if limit > 100:
        limit = 100
    return {"page": page, "offset": (page - 1) * limit, "limit": limit}

# Database session dependency (yield pattern)
def get_db():
    db = SessionLocal()
    try:
        yield db             # injected into route
    finally:
        db.close()           # always runs — even if route raises

# Auth dependency
def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    user = verify_jwt(token)
    if not user:
        raise HTTPException(401, "Invalid token")
    return user

# Chained: admin requires active user requires any user
def get_admin_user(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(403, "Admin required")
    return user


@app.get("/items")
def list_items(
    pagination: dict = Depends(get_pagination),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    ...
```

---

## APIRouter — Organizing Large Apps

```python
# routers/users.py
from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_user)]   # all routes require auth
)

@router.get("/")
def list_users(): ...

@router.get("/{user_id}")
def get_user(user_id: int): ...

@router.post("/", status_code=201)
def create_user(body: CreateUserRequest): ...
```

```python
# main.py
from fastapi import FastAPI
from routers.users import router as users_router
from routers.orders import router as orders_router

app = FastAPI(title="My API", version="1.0.0")
app.include_router(users_router)
app.include_router(orders_router)
# Resulting routes: GET /users/, GET /users/{id}, POST /users/, etc.
```

---

## Common Decorators Table

| Decorator | Source | Purpose |
|---|---|---|
| `@app.get(...)` | FastAPI | GET route |
| `@app.post(...)` | FastAPI | POST route |
| `@app.put(...)` | FastAPI | PUT route |
| `@app.patch(...)` | FastAPI | PATCH route |
| `@app.delete(...)` | FastAPI | DELETE route |
| `@app.middleware("http")` | FastAPI | HTTP middleware |
| `@app.exception_handler(...)` | FastAPI | Custom error handler |
| `@router.get(...)` | APIRouter | Route on a sub-router |
| `@field_validator(...)` | Pydantic | Single field validation |
| `@model_validator(mode="after")` | Pydantic | Cross-field validation |

---

## Background Tasks

```python
from fastapi import BackgroundTasks

def send_welcome_email(email: str):
    # Runs AFTER response is sent — non-blocking
    print(f"Sending welcome email to {email}")

@app.post("/users", status_code=201)
def create_user(body: CreateUserRequest, background_tasks: BackgroundTasks):
    user = save_to_db(body)
    background_tasks.add_task(send_welcome_email, body.email)   # queued, not awaited
    return user  # response delivered immediately
```

**Use for:** emails, webhooks, analytics, cache invalidation.
**Not for:** work that takes >seconds, must survive restart, or must be retried reliably. Use Celery for those.

---

## Middleware

```python
import time
from fastapi import Request

# Timing middleware
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)       # everything after = response path
    duration = time.time() - start
    response.headers["X-Process-Time"] = f"{duration:.4f}"
    return response

# CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Note:** Add middleware before defining routes. Middleware runs in reverse-registration order on requests.

---

## Custom Exception Handlers

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class NotFoundError(Exception):
    def __init__(self, resource: str, id: int):
        self.resource = resource
        self.id = id

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "NOT_FOUND",
                "message": f"{exc.resource} {exc.id} not found"
            }
        }
    )

# Usage in route
@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = db.get(user_id)
    if not user:
        raise NotFoundError("User", user_id)
    return user
```

---

## Router Prefix + Auto-docs Endpoints

```
GET /docs         → Swagger UI (interactive)
GET /redoc        → ReDoc (alternative UI)
GET /openapi.json → raw OpenAPI schema
```

```python
# Disable docs in production
app = FastAPI(docs_url=None, redoc_url=None)  # hide docs
app = FastAPI(docs_url="/docs", openapi_url="/openapi.json")  # custom paths
```

---

## Common Patterns Quick Reference

```python
# Return 201 with Location header
from fastapi import Response

@app.post("/items", status_code=201)
def create_item(body: CreateItem, response: Response):
    item = save(body)
    response.headers["Location"] = f"/items/{item.id}"
    return item

# Streaming response
from fastapi.responses import StreamingResponse

@app.get("/export")
def export_csv():
    def generate():
        yield "id,name\n"
        for row in get_rows():
            yield f"{row.id},{row.name}\n"
    return StreamingResponse(generate(), media_type="text/csv")

# ORJSONResponse for faster serialization
from fastapi.responses import ORJSONResponse

app = FastAPI(default_response_class=ORJSONResponse)
```

---

## Navigation

**[Back to README](./README.md)**

**Theory:** [core_guide.md](./core_guide.md) · [first_api.md](./first_api.md) · [advanced_guide.md](./advanced_guide.md)

**Prev:** [← Error Handling](../06_error_handling_standards/cheatsheet.md) &nbsp;|&nbsp; **Next:** [Versioning →](../08_versioning_standards/cheatsheet.md)

**Related:** [05 Authentication](../05_authentication/cheatsheet.md) · [06 Error Handling](../06_error_handling_standards/cheatsheet.md) · [09 Performance](../09_api_performance_scaling/cheatsheet.md)
