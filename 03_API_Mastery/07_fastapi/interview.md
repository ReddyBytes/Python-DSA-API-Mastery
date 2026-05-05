# 🎯 FastAPI — Interview Preparation

> This file prepares you to discuss FastAPI like a working engineer.
> Not just definitions — but real-world usage, trade-offs, and production scenarios.

---

# 🔹 Basic Level Questions (0–2 Years)

**Q1: What makes FastAPI different from Flask for building REST APIs?**

<details>
<summary>💡 Show Answer</summary>

FastAPI is async-first (built on Starlette and ASGI), whereas Flask is sync-first (WSGI). FastAPI has native Pydantic integration — request bodies are automatically validated by declaring a Pydantic model as a parameter type. FastAPI auto-generates OpenAPI documentation (Swagger UI at `/docs`, ReDoc at `/redoc`) from your type annotations with no extra work.

Flask requires extensions (Flask-RESTX, Marshmallow, Flasgger) to get equivalent validation and docs. FastAPI is significantly faster than Flask for I/O-bound workloads because of async. Trade-off: FastAPI has a steeper learning curve (async/await, Pydantic, dependency injection) and the ecosystem is younger than Flask's.

</details>

<br>

**Q2: How does FastAPI handle request validation automatically?**

<details>
<summary>💡 Show Answer</summary>

You declare a Pydantic `BaseModel` as the type hint for the request body parameter. FastAPI reads the incoming JSON, attempts to construct your model from it, and if validation fails (missing required field, wrong type, constraint violation), it automatically returns a 422 Unprocessable Entity response with detailed field-level error information — before your handler function even runs.

Path parameters and query parameters are also validated: `def get_user(user_id: int = Path(gt=0))` ensures `user_id` is a positive integer. If a non-integer is passed, FastAPI returns 422 automatically. This eliminates an entire class of manual validation boilerplate.

</details>

<br>

**Q3: What is the difference between a path parameter, a query parameter, and a request body in FastAPI?**

<details>
<summary>💡 Show Answer</summary>

Path parameters are embedded in the URL path (`/users/{user_id}`) and are required — the URL won't match without them. Declare them with `Path(...)` or just as a plain typed parameter matching the path template variable name.

Query parameters come after the `?` in the URL (`/users?active=true&page=2`). They're declared as function parameters with defaults — optional ones get a default value, required ones use `Query(...)`.

Request body is JSON sent in the request body (POST/PUT/PATCH). Declare it by typing a parameter as a Pydantic model. FastAPI distinguishes body from query params by the type: Pydantic models are bodies, Python primitives with defaults are query params.

</details>

<br>

**Q4: What does `response_model` do on a FastAPI route decorator?**

<details>
<summary>💡 Show Answer</summary>

`response_model=SomeModel` does two things: it filters the response through the model (fields not on the model are stripped from output) and it generates the response schema in the OpenAPI docs.

The filtering behavior is the security-critical part. If your handler returns an ORM object or a dict with extra internal fields (like `hashed_password`, `internal_cost`, `deleted_at`), FastAPI strips any field not declared on the response model before sending the response. This prevents accidental data leakage without writing explicit serialization code. Use `response_model_exclude_unset=True` to also omit optional fields that were not set.

</details>

<br>

**Q5: What is dependency injection in FastAPI and why is it useful?**

<details>
<summary>💡 Show Answer</summary>

Dependency injection (`Depends()`) is a way to share reusable logic across route handlers. You define a function that returns something (a database session, a pagination object, the current user), then declare it as a parameter with `Depends(your_function)`. FastAPI calls the dependency function, passes the result to your handler, and handles cleanup if you use the `yield` pattern.

The key benefits: the same pagination logic, auth check, or database session can be shared across many routes without copy-paste. Dependencies can depend on other dependencies (chaining). In tests, you can override a dependency to inject a mock database or test user. It makes large apps testable and DRY without any framework magic or global state.

</details>

<br>

---

# 🔹 Intermediate Level Questions (2–5 Years)

**Q6: Explain the `yield` dependency pattern and why it matters for database sessions.**

<details>
<summary>💡 Show Answer</summary>

A dependency using `yield` has setup code before the yield and teardown code after — like a context manager. For a database session:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

FastAPI runs everything before `yield`, injects the session into the route, runs the route handler, then runs the `finally` block regardless of whether the handler raised an exception. Without this, an exception in the route handler could leave database connections open, eventually exhausting the connection pool.

The `yield` pattern ensures resource cleanup is guaranteed. It's also how you implement per-request transaction management — commit on success, rollback on exception, close always.

</details>

<br>

**Q7: How does APIRouter help organize a large FastAPI application?**

<details>
<summary>💡 Show Answer</summary>

`APIRouter` is a mini-application that holds routes, which you then mount onto the main `FastAPI` app. Each router gets a `prefix` (e.g., `/users`) and `tags` (for Swagger grouping). You can also declare dependencies on the router itself — any dependency declared on the router applies to all routes on that router.

This lets you split a large app into files by domain: `routers/users.py`, `routers/orders.py`, `routers/auth.py`. Each file imports its own router and defines its routes. The main `app.py` just includes the routers: `app.include_router(users_router)`. Adding auth to all routes in a module becomes one line on the router instead of adding `Depends(get_current_user)` to every single route function.

</details>

<br>

**Q8: What are FastAPI background tasks and when should you use Celery instead?**

<details>
<summary>💡 Show Answer</summary>

`BackgroundTasks` runs a function after the response is sent, in the same process. The response is returned to the client immediately, and the task runs concurrently. Use it for: sending a welcome email, firing a webhook, writing to an analytics store, cache invalidation — operations that are fast, low-stakes, and don't need persistence.

Use Celery (or equivalent: RQ, Dramatiq) instead when: the task takes more than a few seconds, the task must survive a server restart (Celery persists to Redis/RabbitMQ), the task needs retries with backoff, you need a task queue with prioritization and monitoring, or failure must be tracked and alerted. Background tasks die silently if the process restarts — Celery tasks survive restarts because they're persisted to the broker.

</details>

<br>

**Q9: How do you write and register a custom exception handler in FastAPI?**

<details>
<summary>💡 Show Answer</summary>

Define your custom exception class (inherit from `Exception`), then register a handler with `@app.exception_handler(YourException)`. The handler receives the `Request` and the exception instance, and must return a `Response` — typically `JSONResponse` with your standard error structure.

This is how you achieve consistent error responses across your entire API. Raise your custom exception anywhere (in routes, in dependencies, in nested function calls), and the handler catches it and formats the response. Pair this with a catch-all handler for `Exception` that logs the full traceback internally and returns a safe `INTERNAL_ERROR` response. The goal: no unhandled exception ever reaches the ASGI server as a raw 500 with no body.

</details>

<br>

**Q10: How does FastAPI middleware work and what are common use cases?**

<details>
<summary>💡 Show Answer</summary>

Middleware wraps every request/response cycle. You write an async function that receives the `Request` and a `call_next` callable. Call `call_next(request)` to get the response, then you can modify headers, log timing, or check authentication before returning.

Common use cases: request timing (`X-Process-Time` header), request ID injection (`X-Request-ID` for tracing), CORS (use `CORSMiddleware`), HTTPS redirect, rate limiting (basic), structured access logging. Middleware runs in reverse-registration order for requests (last added runs first) and forward order for responses.

Important caveat: middleware cannot use FastAPI's dependency injection system. Use `Depends()` for anything that needs FastAPI-level context (current user, DB session). Use middleware only for protocol-level cross-cutting concerns.

</details>

<br>

---

# 🔹 Advanced Level Questions (5+ Years)

**Q11: How do you structure a FastAPI application for a production microservice with auth, multiple routers, database sessions, and custom error handling?**

<details>
<summary>💡 Show Answer</summary>

Recommended structure: `app/main.py` (creates the `FastAPI` instance, registers middleware, includes routers, registers exception handlers), `app/routers/` (one file per domain — users, orders, auth), `app/models/` (Pydantic request/response models, separate from ORM models), `app/db/` (SessionLocal, engine, base), `app/dependencies.py` (get_db, get_current_user, get_pagination), `app/exceptions.py` (custom exception classes and handlers).

The dependency chain looks like: route declares `user=Depends(get_current_user)`, `get_current_user` calls `get_db` via its own `Depends`. APIRouter for each domain has `dependencies=[Depends(get_current_user)]` at the router level so all routes are protected. Exception handlers are registered in `main.py` on application startup. Lifespan events (`@asynccontextmanager` pattern in FastAPI 0.93+) handle startup/shutdown for connection pools.

</details>

<br>

**Q12: What is the performance difference between `async def` and `def` route handlers in FastAPI, and when do you use each?**

<details>
<summary>💡 Show Answer</summary>

`async def` handlers run in the event loop directly. Use for any I/O-bound work that has an async implementation: async database drivers (asyncpg, SQLAlchemy async), async HTTP clients (httpx async, aiohttp), Redis async clients. The event loop is not blocked — other requests are processed concurrently while this handler awaits I/O.

`def` handlers are run in a thread pool automatically by FastAPI/Starlette. Use when calling synchronous libraries (standard SQLAlchemy with psycopg2, requests library, blocking file I/O). FastAPI wraps them in `asyncio.run_in_executor` — they don't block the event loop, but they do consume a thread from the pool.

The anti-pattern: using `async def` but calling a synchronous blocking library inside it (e.g., `requests.get()`, synchronous SQLAlchemy). This blocks the event loop, degrading concurrency under load. If you must use sync libraries, use `def` or explicitly run blocking code in an executor with `await asyncio.get_event_loop().run_in_executor(None, sync_function)`.

</details>

<br>

**Q13: How do you write integration tests for FastAPI endpoints that use database dependencies?**

<details>
<summary>💡 Show Answer</summary>

Use `TestClient` from Starlette (synchronous) or `AsyncClient` from httpx for async tests. The key is dependency overrides — FastAPI's `app.dependency_overrides` dict lets you replace any dependency function with a test version for the duration of the test.

For database dependencies: create a test database (SQLite in-memory or a Postgres test database), create a `get_test_db()` dependency that yields a session connected to it, and override: `app.dependency_overrides[get_db] = get_test_db`. For auth: override `get_current_user` to return a test user dict directly, bypassing JWT validation.

Use pytest fixtures to create/drop the test schema per-test or per-session. Roll back each test in a transaction that's aborted at teardown (rather than deleting data) for speed. This gives you tests that exercise actual route logic, Pydantic validation, and exception handlers without touching production databases or auth infrastructure.

</details>

<br>

**Q14: FastAPI auto-generates OpenAPI docs. How do you keep the docs accurate and useful for API consumers?**

<details>
<summary>💡 Show Answer</summary>

Docs are only as good as your type annotations. Every route should have: a typed `response_model` (so the docs show response schema), `status_code` set correctly (so docs show the right success code), `summary` and `description` in the decorator (so endpoints have human-readable descriptions), and `tags` (for Swagger grouping by domain).

Add `Field(description="...", example="...")` to Pydantic model fields so the docs show field descriptions and inline examples. Add `openapi_extra={"examples": {...}}` for richer request body examples. Document all possible error responses with `responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}}` in the decorator.

In production: disable docs (`docs_url=None, redoc_url=None`) or restrict them to internal networks only — exposing a full interactive API explorer publicly is a reconnaissance risk. Generate a static copy of `openapi.json` in CI and diff it against the previous version to detect breaking schema changes before deployment.

</details>

<br>
