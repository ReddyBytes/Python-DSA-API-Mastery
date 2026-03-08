# Why FastAPI?

| Previous | [06 — Error Handling](../06_error_handling_standards/error_guide.md) |
|----------|-----------------------------------------------------------------------|
| Next     | [FastAPI Basics](../07_fastapi/first_api.md)              |
| Home     | [README.md](../README.md)                                             |

---

## The Problem You Are Going to Hit

You decide to build a Python API. You're smart. You've heard of Flask. You read the
five-minute quickstart, and sure enough, five minutes later you have:

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    return jsonify({"id": 1, "name": data["name"]}), 201
```

Clean. Simple. You ship it.

Then the requirements grow. Your teammate asks: "What fields does this endpoint
accept?" You write docs. Then the frontend hits it with a missing `name` field and
gets a Python `KeyError` traceback — in production. You add validation. Then someone
sends `age: "twenty-two"` instead of `age: 22` and you add type checking. Then you
need async database calls and Flask's sync model fights you the whole way. Then you
need automatic docs for your API consumers and you realize you have to maintain a
Swagger YAML file separately from your code, by hand, forever.

You've been writing the same boilerplate that every Python API developer has written
since 2010. And then someone on your team says: "Have you looked at FastAPI?"

You look. And something clicks.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserCreate(BaseModel):
    name: str
    age: int

@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    return {"id": 1, "name": user.name, "age": user.age}
```

That is it. Validation built in. Automatic docs at `/docs`. Type safety throughout.
Wrong types return a clean 422 with field-level error messages before your function
even runs.

This is what FastAPI solves. Let's understand exactly how.

---

## The Comparison Table

Before going deep, here is the honest comparison between the three main Python API
frameworks:

```
Feature               Flask           Django REST     FastAPI
─────────────────────────────────────────────────────────────────
Year introduced       2010            2011            2018
Async support         Bolted on        Bolted on       Native (ASGI)
Type safety           None            None            Core feature
Request validation    Manual          Serializers     Automatic (Pydantic)
API docs generation   Manual/plugin   drf-spectacular Automatic (built-in)
Performance           Moderate        Moderate        High (near Node/Go)
Learning curve        Low             High            Low-Medium
Batteries included    No              Yes             Selective
Best for              Small APIs      Large web apps  APIs, microservices
```

Flask is wonderful for small projects and when you want total control. But every
team that uses Flask on a real API ends up reinventing the same things: validation
libraries, serialization, documentation generation, async patterns.

Django REST Framework is powerful and battle-tested. But it carries the weight of
Django's ORM-first, synchronous-first heritage. Setting up a simple API requires
learning serializers, viewsets, routers, and a dozen other abstractions before you
write your first endpoint.

FastAPI was designed from scratch in 2018 with one question: "What would an API
framework look like if we designed it around modern Python — type hints, async/await,
Pydantic?" The answer is fast to write, fast to run, and nearly impossible to ship
with broken types.

---

## What FastAPI Actually Is

FastAPI is not a web framework in the traditional sense. It is a thin, clever layer
on top of three things that already existed and were already excellent:

```
┌─────────────────────────────────────────────────────────┐
│                      FastAPI                            │
│  (routing, dependency injection, OpenAPI generation,    │
│   type hint magic, developer-friendly API)              │
├───────────────────────┬─────────────────────────────────┤
│      Starlette        │           Pydantic              │
│  (ASGI web framework) │  (data validation from types)   │
│  - HTTP routing       │  - Parse request bodies         │
│  - Middleware         │  - Validate types and values    │
│  - WebSockets         │  - Serialize responses          │
│  - Static files       │  - Generate JSON Schema         │
├───────────────────────┴─────────────────────────────────┤
│                    Python Type Hints                    │
│         (the glue that makes everything automatic)      │
└─────────────────────────────────────────────────────────┘
```

### Starlette: The Engine

Starlette is an ASGI web framework. It handles the low-level web concerns: receiving
HTTP requests, routing them to the right function, running middleware, sending
responses back. If you removed all of FastAPI's magic, you would have something close
to Starlette.

Starlette is also where WebSocket support comes from, where background tasks live,
and where the test client originates. FastAPI inherits all of it.

### Pydantic: The Validator

Pydantic takes Python type hints and turns them into runtime validation. You define
a model using type annotations, and Pydantic enforces those annotations when data
comes in — coercing types where it can, raising detailed errors where it cannot.

```python
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(ge=18, le=120)

# This works:
user = User(name="Alice", email="alice@example.com", age=30)

# This raises a ValidationError with clear messages:
user = User(name="", email="not-an-email", age=15)
# ValidationError: 3 validation errors
#   name: String should have at least 1 character
#   email: value is not a valid email address
#   age: Input should be greater than or equal to 18
```

FastAPI takes your Pydantic models, automatically validates incoming request data
against them, and automatically serializes outgoing response data using them. One
model definition does double duty in both directions.

Pydantic also generates JSON Schema from your models, which FastAPI uses to build
the automatic API documentation.

### Python Type Hints: The Glue

Python type hints (`x: int`, `name: str`, `user: UserCreate`) were added in Python
3.5 and became practical with Python 3.9+. FastAPI reads your function signatures at
startup and uses the type annotations to understand:

- What path parameters exist and what type they should be
- What query parameters exist and what their defaults are
- What the request body shape should be
- What the response shape should be
- What dependencies to inject

This is what makes FastAPI feel magical. You write normal Python with type hints, and
the framework reads those hints to wire everything up automatically.

---

## ASGI vs WSGI: The Architecture That Changes Everything

This is the most important conceptual difference between FastAPI and Flask/Django.

### WSGI: The Old Model

WSGI stands for Web Server Gateway Interface. It was defined in 2003 (PEP 333). Flask
and traditional Django run on WSGI. The model looks like this:

```
WSGI Request Lifecycle
───────────────────────────────────────────────────────────

  HTTP Request
       │
       ▼
  Gunicorn (WSGI server)
       │
       │  Picks an available worker process
       ▼
  Worker Process 1  ← exclusively handles this request
       │
       │  def get_users():
       │      result = db.query(...)   ← BLOCKS HERE, waiting 50ms
       │      return result            ← worker is idle during wait
       ▼
  HTTP Response
       │
       Worker is free again
```

The crucial word: **blocking**. When a WSGI handler calls a database or makes an
HTTP request, the worker process sits and waits. It cannot handle any other request
while it waits. You need one worker per concurrent request.

To handle 100 concurrent requests, you need 100 worker processes (or threads). Each
process uses memory. Processes do not share memory. You hit OS-level limits quickly.

### ASGI: The New Model

ASGI stands for Asynchronous Server Gateway Interface. It was designed in 2019 as
the async successor to WSGI. FastAPI runs on ASGI (via Uvicorn).

```
ASGI Request Lifecycle
───────────────────────────────────────────────────────────

  HTTP Requests (many at once)
   Request A   Request B   Request C
       │            │           │
       └────────────┴───────────┘
                    │
                    ▼
            Uvicorn (ASGI server)
                    │
                    ▼
             Single Process
            ┌─────────────┐
            │ Event Loop  │
            │             │
            │  Coroutine A│──► await db.query() ─► suspends, yields
            │  Coroutine B│◄── resumes (A is waiting for DB)
            │  Coroutine C│──► await http.get() ─► suspends, yields
            │  Coroutine A│◄── resumes (DB responded)
            └─────────────┘
                    │
                    ▼
          HTTP Responses (as they complete)
```

While Coroutine A is waiting for the database, the event loop runs Coroutine B.
While B is waiting for an HTTP call, the event loop runs C. One process, one thread,
potentially thousands of in-flight requests. No wasted waiting.

### When ASGI Helps (and When It Does Not)

ASGI solves **I/O-bound** work. Waiting for a database query. Waiting for an HTTP
call. Waiting for a file to be read. During all of those waits, other coroutines run.

```
I/O-bound work (ASGI shines):
  await db.find_user(id)          ← waiting for network/disk
  await httpx.get("api.stripe.com") ← waiting for network
  await asyncio.sleep(1)          ← waiting for time
  await redis.get("cache_key")    ← waiting for network

CPU-bound work (ASGI does NOT help):
  result = [x**2 for x in range(10_000_000)]  ← pure computation
  image = process_image(raw_bytes)             ← CPU processing
  hash = bcrypt.hash(password)                 ← CPU hashing
```

For CPU-bound work, async/await does nothing. The event loop is still blocked because
Python is using the CPU for computation, not waiting on I/O. For CPU-heavy workloads,
you still need multiple processes — or worker threads, or a task queue like Celery.

In practice, most web APIs are heavily I/O-bound (they hit databases and other
services constantly), which is exactly why ASGI helps so much.

---

## Python's Event Loop: How Async Actually Works

You do not need to become an asyncio expert to use FastAPI. But understanding the
basic mental model helps you avoid the gotchas.

### The Event Loop

The event loop is a scheduler that runs coroutines. A coroutine is a function defined
with `async def`. When a coroutine hits an `await`, it tells the event loop: "I am
waiting for something. Run something else. Come back to me when my awaited thing
completes."

```python
import asyncio

# A coroutine (note: async def, not def)
async def fetch_user(user_id: int):
    # Simulate a 50ms database call
    await asyncio.sleep(0.05)
    return {"id": user_id, "name": "Alice"}

# Running three "requests" concurrently
async def main():
    # All three start at the same time
    results = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3),
    )
    # Total time: ~50ms, not 150ms
    # They overlapped — each yielded during their "DB wait"
    print(results)

asyncio.run(main())
```

Compare the blocking version:

```python
# Blocking code (WSGI style)
def get_users_blocking():
    result = db.query("SELECT * FROM users")  # BLOCKS for 50ms
    # Nothing else can happen during those 50ms
    return result

# Non-blocking code (ASGI style)
async def get_users_async():
    result = await db.query("SELECT * FROM users")  # yields during wait
    # Other coroutines run during those 50ms
    return result
```

### The Rules of Async in FastAPI

FastAPI handles both sync and async route functions:

```python
from fastapi import FastAPI

app = FastAPI()

# Sync route: FastAPI runs this in a thread pool (so it doesn't block the event loop)
@app.get("/sync")
def sync_route():
    result = some_blocking_call()  # OK in sync route
    return result

# Async route: runs directly in the event loop
@app.get("/async")
async def async_route():
    result = await some_async_call()  # must await async operations
    return result
```

The critical mistake to avoid: calling blocking code inside an async route.

```python
# WRONG: blocks the event loop, hurts all other requests
@app.get("/wrong")
async def wrong():
    import time
    time.sleep(1)          # blocks for 1 second, nothing else can run
    result = requests.get("https://api.example.com")  # sync HTTP, blocks
    return result.json()

# RIGHT: use async-compatible libraries
@app.get("/right")
async def right():
    await asyncio.sleep(1)  # yields, other requests run during this 1s
    async with httpx.AsyncClient() as client:
        result = await client.get("https://api.example.com")  # async HTTP
    return result.json()
```

When to use `async def` in FastAPI:
- You are calling an async database library (SQLAlchemy async, Motor, Tortoise ORM)
- You are making HTTP calls with `httpx` or `aiohttp`
- You are using any other async-aware library

When `def` is fine (and sometimes better):
- Pure computation
- Calls to synchronous libraries you cannot change (like `psycopg2`)
- Simple data transformation

FastAPI is smart enough to run sync route functions in a thread pool so they do not
block the event loop. You will not break anything by writing sync routes.

---

## FastAPI Request Lifecycle

Here is exactly what happens from the moment an HTTP request arrives to the moment
the response leaves:

```
HTTP Request arrives at the server
          │
          ▼
   ┌─────────────────────────────────┐
   │   Uvicorn (ASGI server)         │
   │   - Receives raw TCP bytes      │
   │   - Parses HTTP protocol        │
   │   - Creates ASGI scope/receive  │
   └────────────┬────────────────────┘
                │
                ▼
   ┌─────────────────────────────────┐
   │   Starlette Middleware Stack    │
   │   - CORS headers                │
   │   - Request logging             │
   │   - Authentication middleware   │
   │   (runs in order, outermost first) │
   └────────────┬────────────────────┘
                │
                ▼
   ┌─────────────────────────────────┐
   │   Starlette Router              │
   │   "Which route matches          │
   │    GET /users/42 ?"             │
   │   → get_user(user_id: int)      │
   └────────────┬────────────────────┘
                │
                ▼
   ┌─────────────────────────────────┐
   │   FastAPI Dependency Injection  │
   │   Resolve Depends() calls:      │
   │   - db: Session = Depends(...)  │
   │   - user: User = Depends(auth)  │
   │   - Any nested dependencies     │
   └────────────┬────────────────────┘
                │
                ▼
   ┌─────────────────────────────────┐
   │   Pydantic Validation           │
   │   - Parse path params           │
   │     user_id="42" → int(42)      │
   │   - Parse query params          │
   │   - Parse + validate body       │
   │   - If invalid: return 422      │
   └────────────┬────────────────────┘
                │
                ▼
   ┌─────────────────────────────────┐
   │   Your Route Function           │
   │   def get_user(user_id: int):   │
   │       return db.find(user_id)   │
   └────────────┬────────────────────┘
                │
                ▼
   ┌─────────────────────────────────┐
   │   Pydantic Response Serialization │
   │   - Filter to response_model    │
   │   - Convert Python → JSON       │
   │   - Apply aliases               │
   └────────────┬────────────────────┘
                │
                ▼
   ┌─────────────────────────────────┐
   │   Starlette Response            │
   │   - Set status code             │
   │   - Set Content-Type: application/json │
   │   - Set any extra headers       │
   └────────────┬────────────────────┘
                │
                ▼
       HTTP Response sent
```

The key insight in this flow: Pydantic validation happens **before** your function
runs. If the request data is bad, your function never executes. You never have to
write `if not isinstance(user_id, int)` inside your route handler. FastAPI rejected
the request before you even saw it.

---

## Automatic API Documentation — For Free

When you start a FastAPI app and navigate to `/docs`, you see a fully interactive
Swagger UI — without writing a single line of documentation code:

```
┌────────────────────────────────────────────────────┐
│  My API  v1.0.0                                    │
│  http://localhost:8000                             │
│                                                    │
│  ▼ users                                           │
│  ┌────────────────────────────────────────────┐   │
│  │ POST  /users  Create User              [▼] │   │
│  │ GET   /users  List Users               [▼] │   │
│  │ GET   /users/{user_id}  Get User       [▼] │   │
│  │ PATCH /users/{user_id}  Update User    [▼] │   │
│  │ DELETE /users/{user_id} Delete User    [▼] │   │
│  └────────────────────────────────────────────┘   │
│                                                    │
│  Click any endpoint to expand, try it live         │
└────────────────────────────────────────────────────┘
```

How does it work? FastAPI reads your type annotations at startup, converts your
Pydantic models to JSON Schema, combines that with the OpenAPI 3.0 specification
format, and serves the result at `/openapi.json`. The Swagger UI at `/docs` reads
that JSON and builds the interactive interface. ReDoc at `/redoc` reads the same
JSON and builds a clean reading view.

The docs update automatically whenever you change your code. No separate YAML files
to maintain. No decorators to add. If your code compiles, your docs are accurate.

This is genuinely not a small thing. API documentation that is always accurate because
it is derived from the code itself is one of the most significant developer-experience
improvements in modern API development.

---

## Performance Numbers

FastAPI consistently benchmarks near NodeJS and Go for I/O-bound work — a remarkable
achievement for Python:

```
Framework              Requests/sec (I/O-bound, rough numbers)
────────────────────────────────────────────────────────────────
Go (net/http)          ~100,000+
Node.js (fastify)      ~70,000+
FastAPI + Uvicorn      ~30,000-60,000
Flask + Gunicorn       ~5,000-10,000
Django + Gunicorn      ~3,000-8,000
```

These are rough benchmarks and vary enormously based on workload, but the order of
magnitude is consistent: FastAPI is 3-10x faster than Flask/Django for I/O-bound
API workloads.

Why? Because ASGI + async means one process handles many concurrent requests instead
of blocking per request. The same hardware does more work.

### Production Deployment

For production, FastAPI runs behind Uvicorn workers managed by Gunicorn:

```bash
# Development: single process, auto-reload on code changes
uvicorn main:app --reload

# Production: multiple Uvicorn workers, Gunicorn process manager
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Rule of thumb for worker count: 2 * CPU cores + 1
# 2 CPU cores → -w 5
# 4 CPU cores → -w 9
```

The Gunicorn process manager gives you worker restarts on crash, graceful shutdown,
worker health monitoring, and process-level isolation. The UvicornWorker class runs
ASGI within each worker. Together they give you a production-grade deployment.

---

## Summary

```
FastAPI = Starlette + Pydantic + Python type hints + developer-friendly API

Starlette  → ASGI web framework (routing, middleware, WebSockets)
Pydantic   → data validation and serialization from type annotations
Type hints → the bridge that connects your code to both frameworks

WSGI (Flask, Django): synchronous, 1 request per worker
ASGI (FastAPI):       asynchronous, many requests per process
                      Works well for: database calls, HTTP calls, I/O
                      Does not help:  CPU-bound computation

Request lifecycle:
  Uvicorn receives → Middleware → Router → Dependencies
  → Pydantic validates → Your function → Pydantic serializes → Response

Automatic docs: /docs (Swagger) and /redoc (ReDoc), always up to date

Performance: 3-10x faster than Flask/Django for I/O-bound APIs
```

FastAPI is not magic. It is a careful composition of well-designed pieces, connected
by Python's type system. Once you understand those pieces, everything makes sense and
nothing surprises you.

---

| Previous | [06 — Error Handling](../06_error_handling_standards/error_guide.md) |
|----------|-----------------------------------------------------------------------|
| Next     | [FastAPI Basics](../07_fastapi/first_api.md)              |
| Home     | [README.md](../README.md)                                             |
