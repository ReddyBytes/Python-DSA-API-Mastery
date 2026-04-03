# 09 — FastAPI Core Concepts: The Features That Make It Powerful

> You've built your first FastAPI routes. Now it's time to understand the machinery that makes FastAPI genuinely different from every other Python web framework.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
Pydantic models (Field/validators/nested) · dependency injection · middleware

**Should Learn** — Important for real projects, comes up regularly:
APIRouter (organization/prefixes/tags) · custom exception handlers · background tasks

**Good to Know** — Useful in specific situations, not always tested:
chaining dependencies · yield pattern for DB sessions

**Reference** — Know it exists, look up syntax when needed:
response streaming · custom OpenAPI schema · vendor extensions

---

## The Story So Far

In the previous stage you built routes, handled path parameters, returned JSON, and watched Swagger UI generate itself automatically. That alone is impressive. But you were still writing "CRUD in a function" — routes that do everything themselves: validate input, run business logic, manage resources, return responses.

Real applications can't work that way. When you have 50 endpoints, you can't copy-paste validation logic everywhere. When every route needs to check authentication, you can't repeat that check 50 times. When a database connection needs to open and close cleanly around every request, you need a pattern for that.

This stage covers the six features that solve these problems — and together they're what makes FastAPI the right choice for serious Python backends.

---

## 1. Pydantic Models — Deep Dive

You've seen basic Pydantic models. Now let's understand what they can actually do.

Pydantic isn't just a way to describe data shapes. It's a full validation and serialization library. FastAPI uses it for everything that crosses the API boundary: request bodies, response shapes, and query parameters.

### The Full Power of Fields

```python
from pydantic import BaseModel, validator, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"


class OrderItem(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0, description="Must be positive")
    price: float


class Order(BaseModel):
    id: Optional[int] = None
    customer_email: str
    items: List[OrderItem]
    status: OrderStatus = OrderStatus.PENDING
    created_at: Optional[datetime] = None

    @validator("customer_email")
    def email_must_be_valid(cls, v):
        if "@" not in v:
            raise ValueError("Must be a valid email")
        return v.lower()

    @property
    def total(self) -> float:
        return sum(item.price * item.quantity for item in self.items)
```

Let's unpack every piece:

**`Field(..., gt=0, description="...")`**

The `...` means the field is required (no default). `gt=0` means "greater than zero" — Pydantic will reject any value of zero or below before your code even runs. Other common constraints:

| Constraint | Meaning |
|------------|---------|
| `gt=0` | greater than 0 |
| `ge=1` | greater than or equal to 1 |
| `lt=100` | less than 100 |
| `le=100` | less than or equal to 100 |
| `min_length=3` | for strings, minimum length |
| `max_length=255` | for strings, maximum length |
| `regex="^[a-z]+"` | must match pattern |

The `description` shows up directly in the Swagger UI — your API documents itself.

**Enums as string subclasses**

`class OrderStatus(str, Enum)` makes the enum values both proper Python enums AND plain strings. This matters because when FastAPI serializes the response to JSON, it will output `"pending"` not `<OrderStatus.PENDING: 'pending'>`. Always use `(str, Enum)` for string enums in FastAPI.

**Nested models**

`items: List[OrderItem]` means each order contains a list of `OrderItem` objects. Pydantic will validate the entire nested structure. If one item in the list has an invalid `quantity`, the whole request is rejected with a detailed error pointing to exactly which field failed.

**Validators**

```python
@validator("customer_email")
def email_must_be_valid(cls, v):
    if "@" not in v:
        raise ValueError("Must be a valid email")
    return v.lower()
```

`@validator("customer_email")` runs your custom logic after the type check. The function receives the raw value as `v`. You can:
- Raise `ValueError` to reject it (FastAPI turns this into a 422 response)
- Return a transformed value (here we normalize to lowercase)
- Return `v` unchanged if it's valid

**Properties on models**

```python
@property
def total(self) -> float:
    return sum(item.price * item.quantity for item in self.items)
```

A `@property` is computed, not stored. Pydantic won't include it in validation or in the auto-generated schema, but you can use it freely in your Python code. This keeps business logic close to the data it operates on.

### How This Looks in Swagger UI

When you use a model with nested structure, Field descriptions, and enums, Swagger UI renders all of it. The `OrderStatus` enum shows a dropdown with all valid values. The `description` on `quantity` appears as a tooltip. The nested `OrderItem` schema is shown inline.

This is one of FastAPI's core selling points: your validation code and your documentation are the same code.

### Pydantic in Practice — Request and Response Models

A common pattern is to have separate input and output models:

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class OrderCreate(BaseModel):
    """What the client sends when creating an order."""
    customer_email: str
    items: List[OrderItem]

    @validator("customer_email")
    def email_must_be_valid(cls, v):
        if "@" not in v:
            raise ValueError("Must be a valid email")
        return v.lower()


class OrderResponse(BaseModel):
    """What the API returns — includes server-generated fields."""
    id: int
    customer_email: str
    items: List[OrderItem]
    status: OrderStatus
    created_at: datetime
    total: float

    class Config:
        from_attributes = True  # allows reading from ORM objects


from fastapi import FastAPI

app = FastAPI()

@app.post("/orders", response_model=OrderResponse, status_code=201)
def create_order(order: OrderCreate):
    # FastAPI validates `order` against OrderCreate before this runs
    # FastAPI serializes the return value against OrderResponse
    ...
```

The `response_model=OrderResponse` on the route does two things:
1. It filters the return value — if your function returns extra fields, they're stripped
2. It generates the response schema in Swagger UI

---

## 2. Dependency Injection — FastAPI's Superpower

Dependency Injection (DI) sounds academic. The practical meaning is simple:

> Instead of creating objects inside your functions, you declare what you need, and FastAPI creates and provides them for you.

Without DI, every route that needs pagination would duplicate this logic:

```python
# WITHOUT dependency injection
@app.get("/users")
def list_users(page: int = 1, limit: int = 20):
    if limit > 100:
        limit = 100
    offset = (page - 1) * limit
    # ... use offset and limit

@app.get("/orders")
def list_orders(page: int = 1, limit: int = 20):
    if limit > 100:
        limit = 100
    offset = (page - 1) * limit
    # ... duplicated again
```

With DI, you write the logic once:

```python
from fastapi import Depends


def get_current_page(page: int = 1, limit: int = 20):
    if limit > 100:
        limit = 100  # cap the limit
    return {"page": page, "offset": (page - 1) * limit, "limit": limit}


@app.get("/users")
def list_users(pagination: dict = Depends(get_current_page)):
    # pagination is already resolved with validated values
    return {"users": [], "page": pagination["page"]}


@app.get("/orders")
def list_orders(pagination: dict = Depends(get_current_page)):
    return {"orders": [], "page": pagination["page"]}
```

`Depends(get_current_page)` tells FastAPI: "call `get_current_page` with the request parameters, and inject the result here." FastAPI also extracts `page` and `limit` from the query string automatically because `get_current_page` declares them as parameters — the same way route functions do.

### The Most Important Use Case: Authentication

In almost every real application, you need to know who is making a request. Without DI, you'd call `verify_token(request)` at the start of every protected route. With DI, you declare it once:

```python
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_jwt_token(token: str):
    # In real code: decode the JWT, verify signature, check expiry
    # Returns a user dict or None
    if token == "valid-token":
        return {"id": 1, "email": "user@example.com"}
    return None


def get_current_user(token: str = Depends(oauth2_scheme)):
    user = verify_jwt_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


@app.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    return current_user


@app.get("/dashboard")
def get_dashboard(current_user: dict = Depends(get_current_user)):
    return {"message": f"Welcome, {current_user['email']}"}
```

`OAuth2PasswordBearer` is a FastAPI utility that:
- Looks for an `Authorization: Bearer <token>` header on every request
- Extracts the token string
- Returns it to whatever depends on it

The `get_current_user` dependency then validates that token. Every route that declares `Depends(get_current_user)` is automatically protected — no boilerplate, no forgetting.

Swagger UI also reads `OAuth2PasswordBearer` and adds an "Authorize" button to the interface automatically.

### Chaining Dependencies

Dependencies can depend on other dependencies:

```python
def get_current_active_user(
    current_user: dict = Depends(get_current_user)
):
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_admin_user(
    current_user: dict = Depends(get_current_active_user)
):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not an admin")
    return current_user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, admin: dict = Depends(get_admin_user)):
    # Only admins can reach this code
    return {"deleted": user_id}
```

FastAPI resolves the whole chain: `get_admin_user` → `get_current_active_user` → `get_current_user` → `oauth2_scheme`. Each step runs in order, and any `HTTPException` raised in the chain short-circuits the request immediately.

### Dependency with Yield — For Database Sessions

The `yield` pattern lets a dependency run code both before and after the route handler:

```python
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db        # FastAPI injects this into the route
    finally:
        db.close()      # always runs after the route completes


@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    return user
```

The flow is:
1. `get_db` runs: opens the database connection
2. `yield db` pauses `get_db` and gives `db` to the route
3. Route handler runs with the live session
4. After the route returns (or raises an exception), `get_db` resumes from `yield`
5. `finally: db.close()` always runs — even if the route raised an error

This guarantees database connections are never leaked, regardless of what happens in the route.

---

## 3. Middleware

Middleware sits between the web server and your route handlers. Every request passes through middleware on the way in, and every response passes through on the way out.

The most common use cases: logging, timing, adding headers, and CORS.

### Timing Middleware

```python
import time
from fastapi import Request


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

`call_next(request)` passes the request down to the actual route handler and awaits the response. Everything before `call_next` runs on the way in. Everything after runs on the way out.

The `X-Process-Time` header will now appear on every response. Your frontend or monitoring tools can read it to track latency.

### CORS Middleware — Almost Always Required

When a browser makes a request to a different origin (different domain, port, or protocol) than the page it's on, browsers enforce the Same-Origin Policy and block the request unless the server explicitly permits it via CORS headers.

If your React frontend at `localhost:3000` calls your FastAPI backend at `localhost:8000`, every request will be blocked unless you add CORS middleware:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://myapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

`allow_origins` is the list of domains that are allowed to make requests. In development, you typically add `localhost:3000` (or whatever port your frontend runs on). In production, add your actual domain.

`allow_methods=["*"]` permits GET, POST, PUT, DELETE, PATCH — everything.

`allow_headers=["*"]` permits any request headers (including `Authorization` for JWT tokens).

**Important:** Add middleware before defining routes. Middleware is applied in reverse order of registration — the last one added runs first on incoming requests.

### Logging Middleware

```python
import logging

logger = logging.getLogger(__name__)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
```

This gives you a log entry for every request without touching any route handler.

---

## 4. Routers — Organizing Large Applications

As your application grows, putting every route in `main.py` becomes unmanageable. FastAPI's `APIRouter` lets you split routes into separate files organized by feature.

### Project Structure

```
myapp/
├── main.py
├── routers/
│   ├── users.py
│   ├── orders.py
│   └── products.py
├── models.py
├── schemas.py
└── database.py
```

### Defining a Router

```python
# routers/users.py
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
def list_users():
    return {"users": []}


@router.get("/{user_id}")
def get_user(user_id: int):
    if user_id == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user_id, "name": "Alice"}


@router.post("/", status_code=201)
def create_user():
    return {"id": 99, "name": "New User"}
```

```python
# routers/orders.py
from fastapi import APIRouter

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/")
def list_orders():
    return {"orders": []}


@router.get("/{order_id}")
def get_order(order_id: int):
    return {"id": order_id, "status": "pending"}
```

### Registering Routers in main.py

```python
# main.py
from fastapi import FastAPI
from routers.users import router as users_router
from routers.orders import router as orders_router

app = FastAPI(title="My API", version="1.0.0")

app.include_router(users_router)
app.include_router(orders_router)
```

The `prefix="/users"` on the router means every route inside it starts with `/users`. The `tags=["users"]` groups them together in Swagger UI.

After `include_router`, your app has:
- `GET /users/`
- `GET /users/{user_id}`
- `POST /users/`
- `GET /orders/`
- `GET /orders/{order_id}`

All defined across two clean files, not one massive one.

### Router-Level Dependencies

You can apply a dependency to every route in a router at once:

```python
# Every route in this router requires authentication
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_admin_user)]
)

@router.get("/stats")
def get_stats():
    # get_admin_user already ran before this
    return {"total_users": 1000}

@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    # get_admin_user already ran before this too
    return {"deleted": user_id}
```

One line protects every admin route. No individual `Depends(get_admin_user)` needed on each endpoint.

---

## 5. Error Handling — Custom Exception Handlers

FastAPI automatically handles `HTTPException` and Pydantic validation errors. But in large applications, you want to define your own domain-specific exceptions and control exactly how they're formatted.

### Custom Exceptions

```python
from fastapi import Request
from fastapi.responses import JSONResponse


class NotFoundError(Exception):
    def __init__(self, resource: str, id: int):
        self.resource = resource
        self.id = id


class ConflictError(Exception):
    def __init__(self, resource: str, field: str, value: str):
        self.resource = resource
        self.field = field
        self.value = value


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


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(
        status_code=409,
        content={
            "error": {
                "code": "CONFLICT",
                "message": f"{exc.resource} with {exc.field}={exc.value} already exists"
            }
        }
    )
```

Now in your route handlers, raise your domain exceptions instead of constructing `HTTPException` inline:

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = db.get(user_id)
    if not user:
        raise NotFoundError("User", user_id)
    return user


@app.post("/users")
def create_user(user: UserCreate):
    if db.email_exists(user.email):
        raise ConflictError("User", "email", user.email)
    return db.create(user)
```

The error response shape is now consistent across all endpoints, because it's defined once in the handler.

### Overriding FastAPI's Default Validation Error Format

When Pydantic validation fails (a required field is missing, a value fails a constraint), FastAPI returns a 422 with its own format. You can override this:

```python
from fastapi.exceptions import RequestValidationError


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "fields": exc.errors()
            }
        }
    )
```

This keeps your error format consistent whether the problem is a validation error or a business logic error.

---

## 6. Background Tasks

Some work doesn't need to be done before responding to the client. Sending a welcome email, updating analytics, triggering a webhook — these can happen after the response is already delivered.

`BackgroundTasks` lets you do exactly that:

```python
from fastapi import BackgroundTasks


def send_welcome_email(email: str):
    # This runs after the response is sent
    # In real code: call your email service here
    print(f"Sending welcome email to {email}")


def update_user_stats(user_id: int):
    print(f"Updating stats for user {user_id}")


@app.post("/users", status_code=201)
def create_user(user: UserCreate, background_tasks: BackgroundTasks):
    new_user = db.create(user)
    background_tasks.add_task(send_welcome_email, user.email)
    background_tasks.add_task(update_user_stats, new_user.id)
    return new_user  # returned immediately, tasks run after
```

The client receives the `201 Created` response as soon as `return new_user` executes. The email and stats update run immediately after, in the same process, without blocking the response.

**When to use `BackgroundTasks`:**
- Sending emails or notifications
- Logging to external services
- Triggering webhooks
- Cache invalidation
- Analytics events

**When not to use `BackgroundTasks`:**
- Work that takes more than a few seconds (use Celery or similar)
- Work that must survive a server restart (use a message queue)
- Work that must be reliably retried on failure (use a proper job queue)

`BackgroundTasks` is best for fast, fire-and-forget work where occasional failures are acceptable.

---

## Putting It All Together — A Complete Example

Here's a minimal but realistic API that uses all six features:

```python
from fastapi import FastAPI, APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import time


# ── App setup ────────────────────────────────────────────────────────────────

app = FastAPI(title="Order Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Middleware ────────────────────────────────────────────────────────────────

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 4))
    return response


# ── Schemas ───────────────────────────────────────────────────────────────────

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"


class OrderItem(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0, description="Must be positive")
    price: float = Field(..., gt=0)


class OrderCreate(BaseModel):
    customer_email: str
    items: List[OrderItem]

    @validator("customer_email")
    def email_must_be_valid(cls, v):
        if "@" not in v:
            raise ValueError("Must be a valid email")
        return v.lower()


class OrderResponse(BaseModel):
    id: int
    customer_email: str
    items: List[OrderItem]
    status: OrderStatus
    created_at: datetime


# ── Custom Exceptions ─────────────────────────────────────────────────────────

class NotFoundError(Exception):
    def __init__(self, resource: str, id: int):
        self.resource = resource
        self.id = id


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": {"code": "NOT_FOUND",
                           "message": f"{exc.resource} {exc.id} not found"}}
    )


# ── Dependencies ──────────────────────────────────────────────────────────────

def get_pagination(page: int = 1, limit: int = 20):
    if limit > 100:
        limit = 100
    return {"page": page, "offset": (page - 1) * limit, "limit": limit}


# ── Background task ───────────────────────────────────────────────────────────

def send_order_confirmation(email: str, order_id: int):
    print(f"Sending order #{order_id} confirmation to {email}")


# ── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/orders", tags=["orders"])

# In-memory store for the example
orders_db: dict = {}
next_id = 1


@router.post("/", status_code=201)
def create_order(order: OrderCreate, background_tasks: BackgroundTasks):
    global next_id
    record = {
        "id": next_id,
        "customer_email": order.customer_email,
        "items": [item.dict() for item in order.items],
        "status": OrderStatus.PENDING,
        "created_at": datetime.utcnow(),
    }
    orders_db[next_id] = record
    background_tasks.add_task(send_order_confirmation, order.customer_email, next_id)
    next_id += 1
    return record


@router.get("/")
def list_orders(pagination: dict = Depends(get_pagination)):
    all_orders = list(orders_db.values())
    offset = pagination["offset"]
    limit = pagination["limit"]
    return {
        "orders": all_orders[offset : offset + limit],
        "page": pagination["page"],
        "total": len(all_orders),
    }


@router.get("/{order_id}")
def get_order(order_id: int):
    if order_id not in orders_db:
        raise NotFoundError("Order", order_id)
    return orders_db[order_id]


app.include_router(router)
```

Run it with `uvicorn main:app --reload`, open `http://localhost:8000/docs`, and you have a fully documented, validated, structured API with CORS, timing headers, error handling, pagination, and background tasks — all working together.

---

## Summary

| Feature | What It Solves |
|---------|----------------|
| **Pydantic models** | Input validation, output serialization, auto-documentation |
| **Dependency injection** | Shared logic (auth, pagination, DB sessions) without duplication |
| **Middleware** | Cross-cutting concerns (logging, timing, CORS) without touching routes |
| **Routers** | Organizes large apps into maintainable, feature-based files |
| **Custom error handlers** | Consistent error format across all endpoints |
| **Background tasks** | Non-blocking work after the response is delivered |

These six features are what separate "a FastAPI script" from "a FastAPI application." Master them and you can build production-quality backends without hitting architecture walls.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← FastAPI First Steps](../07_fastapi/first_api.md) &nbsp;|&nbsp; **Next:** [FastAPI & Databases →](../07_fastapi/database_guide.md)

**Related Topics:** [FastAPI First Steps](../07_fastapi/first_api.md) · [FastAPI & Databases](../07_fastapi/database_guide.md) · [FastAPI Advanced](../07_fastapi/advanced_guide.md) · [Authentication & Authorization](../05_authentication/securing_apis.md)
