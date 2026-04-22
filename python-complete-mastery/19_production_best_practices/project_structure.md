# Project Structure

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Coding Standards →](./coding_standards.md)

**Related Topics:** [Theory](./theory.md) · [Coding Standards](./coding_standards.md) · [Environment Management](./environment_management.md) · [Packaging](./packaging.md) · [Interview Q&A](./interview.md)

---

## The Analogy

Think of project structure like urban planning.

A city that grew without a plan — no zoning, no street grid, no consistent addresses — works fine when there are 50 people. Everyone knows where the bakery is. But scale to 500,000 people and it becomes chaos. Deliveries get lost. New residents cannot navigate. Nothing can be expanded without tearing something else down.

A well-planned city has districts: residential, commercial, industrial. Streets have consistent names and numbers. Everyone, including newcomers, can orient themselves.

Your project layout is your city's zoning plan. Good structure means a new engineer can navigate on day one.

---

## Learning Priority

**Must Know:**
- Difference between src layout and flat layout
- Where to put tests, config, and entry points
- What `__init__.py` does and when to create it

**Should Know:**
- `conftest.py` and pytest fixture organization
- Separating `models/`, `services/`, `api/` by responsibility
- Monorepo layout for multiple packages

**Good to Know:**
- `py.typed` marker for typed packages
- Cookiecutter project templates
- Namespace packages

---

## Flat Layout

In a **flat layout**, your importable package sits directly in the project root alongside your tooling files.

```
my_project/
├── my_package/          # ← importable package at root level
│   ├── __init__.py
│   ├── core.py
│   └── utils.py
├── tests/
│   └── test_core.py
├── pyproject.toml
├── README.md
└── .gitignore
```

### When to use flat layout

- Simple scripts or small applications not meant for distribution
- Quick prototypes or internal tooling
- When the project has a single top-level package and no packaging complexity

### The hidden trap

When you run `pytest` from the project root with a flat layout, Python adds the current directory to `sys.path`. This means it finds `my_package/` directly — the local source folder. Not an installed version. Your tests pass, you build a wheel, a user installs it, and they might get different behavior because their `sys.path` differs from yours during development.

For libraries intended for distribution, this is a reliability risk.

---

## Src Layout

In a **src layout**, your importable package is nested one level deeper under a `src/` directory.

```
my_project/
├── src/
│   └── my_package/      # ← importable package under src/
│       ├── __init__.py
│       ├── core.py
│       └── utils.py
├── tests/
│   └── test_core.py
├── pyproject.toml
├── README.md
└── .gitignore
```

### Why src layout is better for libraries

The `src/` directory is not a Python package (no `__init__.py`). So Python will never accidentally add it to `sys.path` and find your package there. The only way to import `my_package` is to have it properly installed.

This forces the discipline: `pip install -e .` before running tests. Which means your test environment is always a realistic approximation of what your users see.

**Advantages:**
- Clean separation of source from project tooling
- Forces proper installation (`pip install -e .`)
- Tests always run against the installed package, not raw source
- No accidental import of local source over installed package

---

## Full Real-World Src Layout — Web Service

```
payment_service/
├── src/
│   └── payment_service/
│       ├── __init__.py              # ← package marker; often defines __version__
│       ├── main.py                  # ← app entry point (creates FastAPI app)
│       ├── config.py                # ← pydantic Settings
│       ├── dependencies.py          # ← FastAPI dependency injection
│       │
│       ├── models/                  # ← data models (Pydantic, SQLAlchemy)
│       │   ├── __init__.py
│       │   ├── transaction.py
│       │   └── user.py
│       │
│       ├── services/                # ← business logic, no HTTP knowledge
│       │   ├── __init__.py
│       │   ├── payment_service.py
│       │   └── notification_service.py
│       │
│       ├── repositories/            # ← data access layer (DB queries)
│       │   ├── __init__.py
│       │   └── transaction_repo.py
│       │
│       ├── api/                     # ← HTTP layer: routes, schemas, middleware
│       │   ├── __init__.py
│       │   ├── v1/
│       │   │   ├── __init__.py
│       │   │   ├── payments.py
│       │   │   └── users.py
│       │   └── middleware.py
│       │
│       └── utils/                   # ← shared helpers, no domain knowledge
│           ├── __init__.py
│           ├── logging.py
│           └── datetime_utils.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # ← shared pytest fixtures (DB, client, mocks)
│   ├── unit/                        # ← test functions/classes in isolation
│   │   ├── test_payment_service.py
│   │   └── test_transaction_model.py
│   ├── integration/                 # ← test with real DB / external services
│   │   └── test_payment_api.py
│   └── e2e/                         # ← full end-to-end (optional)
│       └── test_checkout_flow.py
│
├── migrations/                      # ← Alembic DB migrations
│   ├── env.py
│   └── versions/
│
├── scripts/                         # ← one-off utility scripts, not imported
│   ├── seed_db.py
│   └── backfill_transactions.py
│
├── docs/                            # ← architecture docs, ADRs
│
├── .env.example                     # ← env var template — always commit
├── .env                             # ← real secrets — NEVER commit
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml                   # ← project metadata, deps, tool config
├── Dockerfile
├── docker-compose.yml               # ← local dev services (postgres, redis)
└── README.md
```

---

## What Each File and Folder Does

### `__init__.py`

Marks a directory as a Python package. Can be empty, or can expose a public API:

```python
# src/payment_service/__init__.py
__version__ = "1.2.0"

# optionally re-export public symbols:
from .main import create_app
```

### `config.py`

All configuration in one place using Pydantic Settings. Other modules import from here — they never call `os.getenv()` directly.

### `models/`

Data structures: Pydantic models for API request/response validation, SQLAlchemy models for DB, or plain dataclasses. No business logic here.

### `services/`

Business logic. Services orchestrate models and repositories. They know what the business rules are. They do not know about HTTP, SQL, or specific data stores.

### `repositories/`

Database access layer. Repositories execute queries and return domain objects. Services call repositories — they never write SQL themselves.

### `api/`

HTTP layer. Route handlers parse HTTP requests, call services, and return HTTP responses. They know about HTTP status codes and request/response shapes. They do not contain business logic.

### `tests/conftest.py`

Shared fixtures for all tests: database connections, authenticated clients, mock factories. Pytest discovers this file automatically.

### `scripts/`

One-off executable scripts. These are not imported by the main package. They import from the package and do something specific: seed data, run a migration, backfill records.

### `migrations/`

Database migration files (typically Alembic). Version-controlled alongside code so schema changes are reproducible.

---

## Flat vs Src — Decision Guide

| Scenario | Recommended layout |
|---|---|
| CLI tool or web app (not a library) | Flat layout |
| Library published to PyPI | Src layout |
| Package used by other internal services | Src layout |
| Quick prototype / personal script | Flat layout |
| Monorepo with multiple packages | Src layout (one package per subfolder) |

---

## Monorepo Layout

When you have multiple related packages in one repository:

```
company_platform/
├── packages/
│   ├── core/
│   │   ├── src/
│   │   │   └── core/
│   │   ├── tests/
│   │   └── pyproject.toml
│   ├── api_client/
│   │   ├── src/
│   │   │   └── api_client/
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── data_pipeline/
│       ├── src/
│       │   └── data_pipeline/
│       ├── tests/
│       └── pyproject.toml
├── .pre-commit-config.yaml
└── README.md
```

Each package has its own `pyproject.toml`. They can declare each other as dependencies:

```toml
# packages/api_client/pyproject.toml
[project]
dependencies = ["core>=1.0"]
```

Tools like **Poetry workspaces** or **uv workspaces** manage the cross-package dependencies automatically.

---

## Layer Responsibilities (Clean Architecture Alignment)

```
                        HTTP Request
                             │
                    ┌────────▼────────┐
                    │   api/ (routes) │  ← knows HTTP, calls services
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ services/       │  ← knows business rules, calls repos
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ repositories/   │  ← knows SQL/DB, returns domain objects
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ models/         │  ← pure data structures, no I/O
                    └─────────────────┘
```

Each layer only imports from layers below it. `api/` never imports from `repositories/` directly. Business logic stays in `services/`, not scattered across route handlers.

---

## Common Mistakes

**Putting business logic in route handlers:**

```python
# BAD — route handler doing business logic
@router.post("/payments")
async def create_payment(data: PaymentRequest, db: Session = Depends(get_db)):
    if data.amount <= 0:
        raise HTTPException(400, "Amount must be positive")
    user = db.query(User).filter_by(id=data.user_id).first()
    if not user.is_active:
        raise HTTPException(403, "User is inactive")
    # ... 50 more lines of logic
```

```python
# GOOD — route handler delegates to service
@router.post("/payments")
async def create_payment(data: PaymentRequest, service: PaymentService = Depends()):
    result = await service.process_payment(data)
    return result
```

**Flat `tests/` without sub-directories:**

Fine for small projects, but as test suites grow, separate unit tests (fast, no I/O) from integration tests (slow, real DB) so you can run them independently in CI.

---

## Navigation

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Coding Standards →](./coding_standards.md)

**Related Topics:** [Theory](./theory.md) · [Coding Standards](./coding_standards.md) · [Environment Management](./environment_management.md) · [Packaging](./packaging.md) · [Interview Q&A](./interview.md)
