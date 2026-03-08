# Your First FastAPI

| Previous | [FastAPI Fundamentals](../07_fastapi/why_fastapi.md) |
|----------|------------------------------------------------------------------------|
| Next     | [FastAPI Core Concepts](../07_fastapi/core_guide.md)|
| Home     | [README.md](../README.md)                                              |

---

## Before We Write a Line of Code

You are going to build a real, working API in this module. Every code snippet runs.
By the end you will have a complete user CRUD API with proper validation, response
filtering, status codes, and docs — all generated automatically.

One mental shift before we start: **FastAPI trusts your type hints.** When you write
`user_id: int` in a function signature, FastAPI treats that as a contract. It will
enforce the type at the boundary (the HTTP request), coerce it where possible, and
reject it cleanly where not. Get comfortable with this idea. It is the source of
almost every FastAPI superpower.

---

## Installation and Project Setup

```bash
pip install fastapi uvicorn[standard]
```

The `uvicorn[standard]` installs Uvicorn with optional extras: `python-multipart`
for form data, `websockets` for WebSocket support, and `httptools` for faster HTTP
parsing. Always use `[standard]` in real projects.

For email validation (used later in this guide):

```bash
pip install "pydantic[email]"
```

Your project structure:

```
my-api/
├── main.py           ← your application code lives here
├── requirements.txt  ← pin your dependencies
└── .env              ← environment variables (never commit this)
```

`requirements.txt`:
```
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
pydantic[email]>=2.0.0
```

---

## Your First API

Create `main.py`:

```python
from fastapi import FastAPI

app = FastAPI(title="My First API", version="1.0.0")


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
```

Run it:

```bash
uvicorn main:app --reload
```

You will see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Application startup complete.
```

Now open three browser tabs:

- `http://localhost:8000/` — returns `{"message": "Hello, World!"}`
- `http://localhost:8000/health` — returns `{"status": "ok"}`
- `http://localhost:8000/docs` — Swagger UI, automatically generated

The Swagger UI shows your two endpoints. You can expand each one and click
"Try it out" to call them live from the browser. Zero extra work.

```
http://localhost:8000/docs
┌─────────────────────────────────────────────────────────┐
│  My First API  1.0.0                                    │
│                                                         │
│  ▼ default                                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │ GET  /        Read Root                   [▼]  │   │
│  │ GET  /health  Health Check                [▼]  │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### What `app = FastAPI(...)` Does

`FastAPI()` creates your application instance. The `title` and `version` show up in
the docs. You can also add:

```python
app = FastAPI(
    title="My First API",
    version="1.0.0",
    description="An API that does important things.",
    docs_url="/docs",        # default: /docs
    redoc_url="/redoc",      # default: /redoc
    openapi_url="/openapi.json",  # default: /openapi.json
)
```

To disable docs in production (for security), set `docs_url=None, redoc_url=None`.

---

## Path Parameters

Path parameters are parts of the URL itself, defined with `{braces}` in the route
decorator and matched by parameter name in the function signature:

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

The `: int` type annotation is not just for documentation. FastAPI enforces it:

```
GET /users/42    →  200  {"user_id": 42}        ← int(42), correct
GET /users/abc   →  422  {"detail": [{"type": "int_parsing", ...}]}
GET /users/3.14  →  422  (3.14 is not an int)
```

You never write `if not isinstance(user_id, int): raise ValueError(...)`. FastAPI
does it before your function runs.

String path parameters work the same way:

```python
@app.get("/users/{username}")
def get_user_by_username(username: str):
    return {"username": username}
```

Multiple path parameters:

```python
@app.get("/users/{user_id}/orders/{order_id}")
def get_user_order(user_id: int, order_id: int):
    return {"user_id": user_id, "order_id": order_id}
```

### Order Matters for Fixed vs Variable Paths

If you have a fixed path and a variable path at the same level, put the fixed one
first — FastAPI matches routes in declaration order:

```python
# CORRECT: fixed path defined before variable path
@app.get("/users/me")           # matches /users/me
def get_current_user():
    return {"user": "current"}

@app.get("/users/{user_id}")    # matches /users/42, /users/alice, etc.
def get_user(user_id: str):
    return {"user_id": user_id}

# WRONG (if reversed): /users/me would match user_id="me"
```

---

## Query Parameters

Query parameters are the `?key=value` parts of a URL. Any function parameter that
is not a path parameter is treated as a query parameter:

```python
@app.get("/users")
def list_users(
    page: int = 1,
    limit: int = 20,
    search: str | None = None,
    active: bool = True
):
    return {
        "page": page,
        "limit": limit,
        "search": search,
        "active": active
    }
```

```
GET /users
→ {"page": 1, "limit": 20, "search": null, "active": true}

GET /users?page=3&limit=5
→ {"page": 3, "limit": 5, "search": null, "active": true}

GET /users?search=alice&active=false
→ {"page": 1, "limit": 20, "search": "alice", "active": false}

GET /users?page=abc
→ 422 Unprocessable Entity (page must be an int)
```

Notice `active: bool = True`. FastAPI converts query strings to booleans:
- `?active=true`, `?active=1`, `?active=yes` → `True`
- `?active=false`, `?active=0`, `?active=no` → `False`

`str | None = None` means the parameter is optional (union with None, default None).
In Python 3.9 and earlier you write `Optional[str] = None` from `typing`:

```python
from typing import Optional

@app.get("/users")
def list_users(search: Optional[str] = None):
    return {"search": search}
```

Both are equivalent. The `str | None` syntax requires Python 3.10+.

### Required Query Parameters

Omit the default to make a query parameter required:

```python
@app.get("/search")
def search(q: str):  # no default — required
    return {"query": q}
```

```
GET /search        →  422 (q is required)
GET /search?q=api  →  {"query": "api"}
```

---

## Request Body with Pydantic

GET requests have query parameters. POST/PUT/PATCH requests have a body — the data
you send to the server. In FastAPI, you define the body shape with a Pydantic model:

```python
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field

app = FastAPI()


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=18, le=120)


@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    # user is already validated here — you can trust all values
    # user.name: str, 1-100 chars
    # user.email: valid email address
    # user.age: int, 18-120
    return {"id": 1, **user.model_dump()}
```

`Field(...)` — the `...` means required (no default). The keyword arguments are
validators:
- `min_length`, `max_length` — string length
- `ge` (greater than or equal), `le` (less than or equal) — numeric bounds
- `gt`, `lt` — strict greater/less than
- `pattern` — regex pattern for strings

What happens with invalid input:

```
POST /users
{"name": "", "email": "not-email", "age": 15}

→ 422 Unprocessable Entity
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "name"],
      "msg": "String should have at least 1 character",
      "input": ""
    },
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "input": "not-email"
    },
    {
      "type": "greater_than_equal",
      "loc": ["body", "age"],
      "msg": "Input should be greater than or equal to 18",
      "input": 15
    }
  ]
}
```

Three errors, all returned at once, with exact field locations and human-readable
messages. Your route function never ran. You did not write any of this validation.

### What Swagger Looks Like for This Model

When you open `/docs` and expand the `POST /users` endpoint, you see:

```
POST /users
─────────────────────────────────────────────────────────
Request body  application/json  required

{
  "name": "string",   ← required, 1-100 chars
  "email": "user@example.com",  ← required, valid email
  "age": 0            ← required, 18-120
}

Schema:
  name    string  minLength: 1, maxLength: 100
  email   string  format: email
  age     integer minimum: 18, maximum: 120
```

This schema is generated from your Pydantic model. No extra work.

---

## Response Models

By default, FastAPI returns whatever you return from your route function. If you
return a dictionary with a `password_hash` field, it goes in the response. That is
a security problem.

Use `response_model` to control exactly what goes in the response:

```python
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str  # taken on input


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    # no password field — it never leaves the server


@app.post("/users", status_code=201, response_model=UserResponse)
def create_user(user: UserCreate):
    # Imagine we hash the password and save to DB...
    db_user = {
        "id": 1,
        "name": user.name,
        "email": user.email,
        "password_hash": "argon2$hashed$etc",  # this field exists in DB object
    }
    # FastAPI will filter db_user to only UserResponse fields
    # password_hash is NOT in UserResponse, so it never appears in the response
    return db_user
```

```
POST /users
{"name": "Alice", "email": "alice@example.com", "password": "secret123"}

→ 201 Created
{"id": 1, "name": "Alice", "email": "alice@example.com"}
← password_hash was filtered out automatically
```

This is one of the most important patterns in FastAPI. Your internal objects can have
many more fields than your API responses. The `response_model` acts as a filter and
a contract.

Response models also appear in the Swagger docs, so API consumers know exactly what
shape to expect.

---

## HTTP Methods: Full CRUD Example

Let's build a complete user CRUD API. This is a working, runnable example:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

app = FastAPI(title="User API", version="1.0.0")


# ── Models ──────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=18, le=120)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=18, le=120)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: int


# ── In-memory "database" ─────────────────────────────────────────────────────
# Real apps use SQLAlchemy or similar — this keeps the example focused

db: dict[int, dict] = {}
next_id = 1


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/users", response_model=list[UserResponse])
def list_users():
    """Return all users."""
    return list(db.values())


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    """Return a single user by ID."""
    if user_id not in db:
        raise HTTPException(status_code=404, detail="User not found")
    return db[user_id]


@app.post("/users", status_code=201, response_model=UserResponse)
def create_user(user: UserCreate):
    """Create a new user."""
    global next_id
    new_user = {"id": next_id, **user.model_dump()}
    db[next_id] = new_user
    next_id += 1
    return new_user


@app.put("/users/{user_id}", response_model=UserResponse)
def replace_user(user_id: int, user: UserCreate):
    """Replace a user entirely (all fields required)."""
    if user_id not in db:
        raise HTTPException(status_code=404, detail="User not found")
    db[user_id] = {"id": user_id, **user.model_dump()}
    return db[user_id]


@app.patch("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate):
    """Partially update a user (only provided fields change)."""
    if user_id not in db:
        raise HTTPException(status_code=404, detail="User not found")

    current = db[user_id]
    updates = user.model_dump(exclude_unset=True)  # only provided fields
    current.update(updates)
    db[user_id] = current
    return current


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    """Delete a user. Returns 204 No Content on success."""
    if user_id not in db:
        raise HTTPException(status_code=404, detail="User not found")
    del db[user_id]
    # return nothing — 204 means no content
```

Run this and visit `/docs`. You will see all five endpoints, organized with their
request schemas and response schemas. Every field is documented.

### Testing the CRUD Manually

```bash
# Create a user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com", "age": 30}'
# → {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30}

# Get all users
curl http://localhost:8000/users
# → [{"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30}]

# Get one user
curl http://localhost:8000/users/1
# → {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30}

# Partial update (PATCH) — only change the name
curl -X PATCH http://localhost:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice Smith"}'
# → {"id": 1, "name": "Alice Smith", "email": "alice@example.com", "age": 30}

# Full replace (PUT) — all fields required
curl -X PUT http://localhost:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice J", "email": "alicej@example.com", "age": 31}'
# → {"id": 1, "name": "Alice J", "email": "alicej@example.com", "age": 31}

# Delete
curl -X DELETE http://localhost:8000/users/1
# → (empty body, status 204)

# Try to get deleted user
curl http://localhost:8000/users/1
# → {"detail": "User not found"} (status 404)
```

### `exclude_unset=True` — The PATCH Pattern

This line in the PATCH route deserves attention:

```python
updates = user.model_dump(exclude_unset=True)  # only provided fields
```

When a Pydantic model has `Optional` fields with `None` defaults, and a client sends
`{"name": "Alice"}`, we want to update only `name` — not set `email` and `age` to
`None`.

`exclude_unset=True` returns only the fields that were explicitly set in the request,
not the fields that defaulted to `None`. This is the standard pattern for PATCH
endpoints in FastAPI.

---

## Status Codes

FastAPI defaults to `200 OK` for all routes. Override with `status_code`:

```python
@app.post("/users", status_code=201)   # 201 Created for resource creation
def create_user(): ...

@app.delete("/users/{user_id}", status_code=204)  # 204 No Content for delete
def delete_user(): ...
```

The most common status codes you will set in FastAPI:

```
200  OK             → default for GET/PATCH/PUT (returned data)
201  Created        → POST that creates a resource
204  No Content     → DELETE, or actions that return nothing
400  Bad Request    → general client error (rare with Pydantic — use 422)
401  Unauthorized   → missing or invalid authentication
403  Forbidden      → authenticated but not permitted
404  Not Found      → resource does not exist
409  Conflict       → duplicate email, version conflict
422  Unprocessable  → validation failed (FastAPI uses this automatically)
500  Internal Error → something broke on your end
```

### HTTPException

Raise `HTTPException` to return any non-success status code:

```python
from fastapi import HTTPException

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user
```

The `detail` can be a string or any JSON-serializable object:

```python
raise HTTPException(
    status_code=422,
    detail={
        "code": "DUPLICATE_EMAIL",
        "message": "A user with this email already exists",
        "field": "email"
    }
)
```

---

## Adding Documentation to Your Routes

FastAPI automatically reads docstrings and the `summary` parameter:

```python
@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Get a user by ID",
    response_description="The requested user"
)
def get_user(user_id: int):
    """
    Retrieve a single user by their numeric ID.

    - **user_id**: the unique integer ID of the user
    - Returns 404 if the user does not exist
    """
    if user_id not in db:
        raise HTTPException(status_code=404, detail="User not found")
    return db[user_id]
```

The docstring becomes the description in Swagger. `summary` becomes the short
title. `response_description` labels the 200 response.

You can also add tags to group endpoints in the docs:

```python
@app.get("/users", tags=["users"])
def list_users(): ...

@app.post("/users", tags=["users"])
def create_user(): ...

@app.get("/products", tags=["products"])
def list_products(): ...
```

```
Swagger UI:
┌─────────────────────────────────────────────────────────┐
│  ▼ users                                                │
│     GET  /users                                         │
│     POST /users                                         │
│  ▼ products                                             │
│     GET  /products                                      │
└─────────────────────────────────────────────────────────┘
```

---

## A Complete, Runnable Example

Here is the full `main.py` from this guide, clean and ready to run:

```python
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(
    title="User API",
    version="1.0.0",
    description="A complete CRUD API for managing users.",
)


# ── Pydantic Models ──────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """Fields required when creating a user."""
    name: str = Field(..., min_length=1, max_length=100, examples=["Alice Smith"])
    email: EmailStr = Field(..., examples=["alice@example.com"])
    age: int = Field(..., ge=18, le=120, examples=[30])


class UserUpdate(BaseModel):
    """All fields optional for partial updates (PATCH)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=18, le=120)


class UserResponse(BaseModel):
    """Shape of every user in API responses."""
    id: int
    name: str
    email: EmailStr
    age: int


# ── Storage ───────────────────────────────────────────────────────────────────

_db: dict[int, dict] = {}
_next_id = 1


def _get_user_or_404(user_id: int) -> dict:
    """Shared helper — raises 404 if user not found."""
    if user_id not in _db:
        raise HTTPException(status_code=404, detail="User not found")
    return _db[user_id]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["meta"])
def health_check():
    """Liveness check — returns 200 if the app is running."""
    return {"status": "ok"}


@app.get("/users", response_model=list[UserResponse], tags=["users"])
def list_users():
    """Return all users."""
    return list(_db.values())


@app.get("/users/{user_id}", response_model=UserResponse, tags=["users"])
def get_user(user_id: int):
    """Return a single user by ID."""
    return _get_user_or_404(user_id)


@app.post("/users", status_code=201, response_model=UserResponse, tags=["users"])
def create_user(user: UserCreate):
    """Create a new user. Returns 201 with the created user."""
    global _next_id
    new_user = {"id": _next_id, **user.model_dump()}
    _db[_next_id] = new_user
    _next_id += 1
    return new_user


@app.put("/users/{user_id}", response_model=UserResponse, tags=["users"])
def replace_user(user_id: int, user: UserCreate):
    """Replace all user fields. All fields are required."""
    _get_user_or_404(user_id)
    _db[user_id] = {"id": user_id, **user.model_dump()}
    return _db[user_id]


@app.patch("/users/{user_id}", response_model=UserResponse, tags=["users"])
def update_user(user_id: int, user: UserUpdate):
    """Partially update a user. Only provided fields are changed."""
    current = _get_user_or_404(user_id)
    updates = user.model_dump(exclude_unset=True)
    current.update(updates)
    _db[user_id] = current
    return current


@app.delete("/users/{user_id}", status_code=204, tags=["users"])
def delete_user(user_id: int):
    """Delete a user. Returns 204 No Content on success."""
    _get_user_or_404(user_id)
    del _db[user_id]
```

Run it:

```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000/docs` — you have a fully documented, interactive API.

---

## Development vs Production

### Development

```bash
# --reload: watches for file changes, restarts automatically
# --port: defaults to 8000
# --host: defaults to 127.0.0.1 (localhost only)
uvicorn main:app --reload --port 8000

# To allow connections from other machines on your network:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Never use `--host 0.0.0.0` in production without a firewall or reverse proxy in
front. It opens the port to all network interfaces.

### Production

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple Uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# With host/port:
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Rule of thumb for worker count: 2 * (number of CPU cores) + 1
```

In a real production deployment, you would put Nginx or another reverse proxy in
front of Gunicorn. Nginx handles SSL termination, static files, and acts as a
buffer against slow clients. Gunicorn handles the Python application.

```
Internet
   │
   ▼
Nginx (port 443, SSL termination)
   │
   ▼
Gunicorn (port 8000, process manager)
   ├── Uvicorn Worker 1
   ├── Uvicorn Worker 2
   ├── Uvicorn Worker 3
   └── Uvicorn Worker 4
```

For containerized deployments (Docker, Kubernetes), the typical pattern is to skip
Gunicorn and run multiple container replicas, each running a single Uvicorn process:

```bash
# In your Dockerfile CMD:
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```

Container orchestration (Kubernetes, ECS, etc.) handles the multi-instance scaling
externally.

---

## What You Now Know

```
Installation:
  pip install fastapi uvicorn[standard] "pydantic[email]"
  uvicorn main:app --reload

Core patterns:
  @app.get("/path")             → GET endpoint
  @app.post("/path")            → POST endpoint
  @app.put("/path/{id}")        → PUT endpoint
  @app.patch("/path/{id}")      → PATCH endpoint
  @app.delete("/path/{id}")     → DELETE endpoint

Path parameters:   /users/{user_id}    → user_id: int (validated)
Query parameters:  def f(page: int = 1) → ?page=2 (with default)
Request body:      def f(user: UserCreate) → Pydantic model (validated)

Response control:
  status_code=201               → set non-200 status
  response_model=UserResponse   → filter/shape the response
  raise HTTPException(404, ...) → return error responses

PATCH pattern:
  user.model_dump(exclude_unset=True) → only changed fields

Automatic docs:
  /docs   → Swagger UI (interactive)
  /redoc  → ReDoc (reading view)

Production:
  gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

The patterns you learned here — Pydantic models for request and response, type hints
as validation, `response_model` for output filtering — are the foundation of
everything else in FastAPI. The next module goes deeper into dependency injection,
middleware, background tasks, and async database access.

---

| Previous | [FastAPI Fundamentals](../07_fastapi/why_fastapi.md) |
|----------|------------------------------------------------------------------------|
| Next     | [FastAPI Core Concepts](../07_fastapi/core_guide.md)|
| Home     | [README.md](../README.md)                                              |
