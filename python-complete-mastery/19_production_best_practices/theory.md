# Production Best Practices — Theory

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Performance Optimization](../18_performance_optimization/profiling.md) &nbsp;|&nbsp; **Next:** [Project Structure →](./project_structure.md)

**Related Topics:** [Project Structure](./project_structure.md) · [Coding Standards](./coding_standards.md) · [Environment Management](./environment_management.md) · [Packaging](./packaging.md) · [Interview Q&A](./interview.md)

---

## Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`src` layout · `.env` files + `python-dotenv` · `venv` + `pip` · PEP 8 + Black · structured logging · graceful error handling

**Should Learn** — Important for real projects, comes up regularly:
Pydantic `Settings` · `pre-commit` hooks · `pyenv` + Poetry · JSON log format · correlation IDs · retry with backoff

**Good to Know** — Useful in specific situations:
12-factor app · `pip-tools` · circuit breaker pattern · AWS Secrets Manager · `/health` endpoint · `conda` for data science

**Reference** — Know it exists, look up when needed:
`bandit` security scanning · OpenTelemetry tracing · Vault secrets · readiness vs liveness probes

---

## 1. Project Layout

### The Analogy

Think of a Python project like a professional kitchen.

A home cook might keep utensils scattered across the counter — it works, but only for one person. A restaurant kitchen has strict zones: prep area, grill, plating, storage. Every tool has a place. Anyone can step in and know where things are.

Project layout is your kitchen's floor plan. Get it right once, and everyone who joins the team immediately knows where to look.

---

### Flat Layout vs Src Layout

There are two dominant conventions in the Python world.

**Flat layout** — your package sits directly in the project root:

```
my_project/
├── my_package/          # ← importable package lives here at root
│   ├── __init__.py
│   └── core.py
├── tests/
├── pyproject.toml
└── README.md
```

**Src layout** — your package is nested under a `src/` directory:

```
my_project/
├── src/
│   └── my_package/      # ← importable package lives under src/
│       ├── __init__.py
│       └── core.py
├── tests/
├── pyproject.toml
└── README.md
```

---

### Why Src Layout Wins for Libraries

The flat layout has a subtle trap: when you run tests from the project root, Python finds your local `my_package/` directory before the installed version. This means your tests might pass locally but fail after packaging — because you were testing the source folder, not the installed wheel.

Src layout forces you to install the package (`pip install -e .`) before importing it. This means your test environment matches your user's environment exactly.

**Rule of thumb:**
- Building a library or package meant for distribution? Use src layout.
- Writing a standalone application or simple script? Flat layout is fine.
- Monorepo with multiple packages? Use src layout with one subfolder per package.

---

### Full Real-World Src Layout

```
payment_service/
├── src/
│   └── payment_service/
│       ├── __init__.py          # ← marks this as a package
│       ├── main.py              # ← application entry point
│       ├── config.py            # ← settings and configuration
│       ├── models/
│       │   ├── __init__.py
│       │   ├── transaction.py   # ← domain models
│       │   └── user.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── payment.py       # ← business logic
│       │   └── notification.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── routes.py        # ← HTTP route handlers
│       │   └── middleware.py
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # ← shared pytest fixtures
│   ├── unit/
│   │   └── test_payment.py
│   └── integration/
│       └── test_api.py
├── docs/
├── scripts/
│   └── seed_db.py               # ← one-off utility scripts
├── .env.example                 # ← template, commit this
├── .env                         # ← real secrets, NEVER commit
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
├── Dockerfile
└── README.md
```

---

## 2. Configuration Management

### The Analogy

A vending machine works in Tokyo and New York. The machine itself (code) is identical. What changes is the configuration: local currency, language, product prices. The machine reads these from external settings at startup — it does not hardcode "price = 120 yen" into its circuit board.

Your application should work the same way. The code is the machine. The environment is the city.

---

### The 12-Factor App Principle

The **12-factor app** is a methodology for building modern, deployable software. Factor III states:

> "Store config in the environment. Config is everything likely to vary between deploys (staging, production, developer environments)."

This means: no hardcoded URLs, passwords, or feature flags in source code. All of it goes in environment variables.

---

### .env Files

In development, managing dozens of environment variables manually is painful. The convention is to store them in a `.env` file and load them at startup.

```bash
# .env  ← never commit this file
DATABASE_URL=postgresql://localhost:5432/mydb
SECRET_KEY=dev-secret-not-for-production
DEBUG=true
LOG_LEVEL=DEBUG
```

```bash
# .env.example  ← always commit this (no real values)
DATABASE_URL=postgresql://host:port/dbname
SECRET_KEY=your-secret-key-here
DEBUG=false
LOG_LEVEL=INFO
```

Load with `python-dotenv`:

```python
from dotenv import load_dotenv
import os

load_dotenv()                              # ← reads .env into os.environ

db_url = os.getenv("DATABASE_URL")        # ← reads from environment
```

---

### Pydantic Settings — The Production Pattern

Raw `os.getenv()` has problems: missing variables silently return `None`, types are always strings, and there is no central documentation of what config your app needs.

**Pydantic Settings** solves all three:

```python
from pydantic_settings import BaseSettings  # ← pip install pydantic-settings
from pydantic import Field

class Settings(BaseSettings):
    # ← each field documents a required config variable
    database_url: str = Field(..., description="PostgreSQL connection string")
    secret_key: str = Field(..., min_length=32)
    debug: bool = False                   # ← automatic type coercion from env
    log_level: str = "INFO"
    max_retries: int = 3

    class Config:
        env_file = ".env"                 # ← loads .env automatically
        case_sensitive = False            # ← DATABASE_URL matches database_url

# Singleton pattern — create once, import everywhere
settings = Settings()
```

Usage:

```python
from payment_service.config import settings

print(settings.database_url)             # ← type-safe, validated at startup
print(settings.debug)                    # ← bool, not the string "true"
```

If `DATABASE_URL` is missing, Pydantic raises a `ValidationError` at startup with a clear message — not a cryptic `AttributeError` buried in your request handler.

---

## 3. Environment Management

### The Analogy

Imagine every Python project is a science experiment. Each experiment needs specific reagents (libraries) at specific concentrations (versions). If you run all experiments on the same bench without separating them, reagents contaminate each other. One experiment's "flask v1" collides with another's "flask v3".

Virtual environments are your isolated lab benches. One project, one bench.

---

### The Tool Landscape

| Tool | What it solves |
|---|---|
| `venv` | Built-in isolation — creates a project-local Python |
| `virtualenv` | Older, faster version of `venv`, still widely used |
| `pyenv` | Manages multiple Python versions on one machine |
| `poetry` | Dependency management + packaging in one tool |
| `pip-tools` | Locks `requirements.in` → `requirements.txt` |
| `conda` | Environment + package manager for data science |

---

### venv — The Standard

```bash
python -m venv .venv                     # ← creates .venv/ in project root
source .venv/bin/activate                # ← activates (Mac/Linux)
.venv\Scripts\activate                   # ← activates (Windows)
pip install -r requirements.txt          # ← install deps
deactivate                               # ← exit environment
```

Always add `.venv/` to `.gitignore`. Never commit it.

---

### Dependency Pinning

**requirements.txt without pinning** (dangerous):
```
requests
flask
sqlalchemy
```

Every `pip install` might pull different versions. Works today, breaks next week.

**requirements.txt with pinning** (safe):
```
requests==2.31.0
flask==3.0.3
sqlalchemy==2.0.30
```

Exact version locks mean reproducible installs everywhere.

**pip-tools** automates the pinning workflow:

```bash
# requirements.in  ← you write this (abstract deps)
requests>=2.28
flask

# Generate locked file:
pip-compile requirements.in            # ← produces requirements.txt with exact pins
pip-sync requirements.txt             # ← installs exactly those pins
```

---

### Poetry — Modern All-in-One

**Poetry** combines dependency management, virtual environment creation, and packaging:

```bash
poetry new my_project                  # ← scaffolds a new project
poetry add requests flask              # ← adds deps to pyproject.toml
poetry add --group dev pytest black    # ← dev-only deps
poetry install                         # ← installs all deps, creates .venv
poetry run python src/main.py          # ← runs in the managed venv
poetry build                           # ← builds wheel + sdist
```

`pyproject.toml` under Poetry:

```toml
[tool.poetry]
name = "my_project"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.11"
requests = "^2.31"
flask = "^3.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
black = "^24.0"
```

Poetry generates `poetry.lock` — the exact equivalent of a pinned `requirements.txt`.

---

### When to Use What

| Scenario | Recommendation |
|---|---|
| Simple app, team knows pip | `venv` + `pip-tools` |
| Library you'll publish to PyPI | Poetry |
| Data science / Jupyter / ML | `conda` or `mamba` |
| Legacy project, large team | Keep existing tool, standardize it |
| Multiple Python versions locally | `pyenv` + anything above |

---

## 4. Coding Standards

### The Analogy

A newspaper has a style guide. Not because there is only one right way to write English, but because consistency across 200 journalists makes the paper readable and professional. No reader should be jolted by a sudden change in tone, capitalization, or paragraph structure.

PEP 8 is Python's style guide. The tools enforce it automatically.

---

### PEP 8 — The Baseline

**PEP 8** is the official Python style guide. Key rules:

- 4 spaces for indentation (never tabs)
- Lines max 79 characters (Black defaults to 88)
- Two blank lines between top-level functions/classes
- One blank line between methods inside a class
- `snake_case` for variables and functions
- `PascalCase` for classes
- `UPPER_CASE` for constants
- Imports at the top, grouped: stdlib → third-party → local

---

### The Formatter Trio

**Black** — the opinionated auto-formatter. No configuration debates. Run it, code is formatted.

```bash
black src/ tests/                        # ← formats all Python files
black --check src/                       # ← CI mode: exit 1 if any file needs formatting
```

**isort** — sorts and groups imports automatically.

```bash
isort src/ tests/
```

**Ruff** — a modern replacement for flake8 + isort, written in Rust, extremely fast. Many teams now use Ruff instead of flake8:

```bash
ruff check src/                          # ← lint
ruff check --fix src/                   # ← auto-fix where possible
```

---

### Type Hints and mypy

Type hints document intent and catch bugs before runtime:

```python
def process_payment(
    amount: float,
    currency: str,
    user_id: int,
) -> dict[str, str]:                     # ← return type documented
    ...
```

**mypy** is the static type checker:

```bash
mypy src/                                # ← checks all type annotations
```

Common mypy config in `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.11"
strict = true                            # ← enables all checks
ignore_missing_imports = true            # ← suppress errors for untyped libs
```

---

### Pre-commit Hooks

**Pre-commit hooks** run automatically before every `git commit`. They catch formatting and lint issues before they reach the repo.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
```

Setup:

```bash
pip install pre-commit
pre-commit install                       # ← installs hooks into .git/hooks/
pre-commit run --all-files               # ← run manually on everything
```

---

## 5. Logging in Production

### The Analogy

An airplane's black box records everything: altitude, speed, control inputs, system states. After an incident, investigators replay exactly what happened. Without it, they are guessing.

Production logs are your black box. If something goes wrong at 3 AM, logs let you replay the incident without needing to reproduce it.

---

### What Bad Logging Looks Like

```python
print("payment failed")                  # ← no timestamp, no context, no level
print(f"error: {e}")                     # ← unstructured, hard to query
```

You cannot filter this. You cannot search it. You cannot correlate it with other services.

---

### Structured Logging with JSON

**Structured logging** emits each log line as a JSON object. Every field is queryable.

```python
import logging
import json
import sys
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    """Formats log records as JSON lines."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        # ← include extra fields passed via extra={}
        if hasattr(record, "correlation_id"):
            log_obj["correlation_id"] = record.correlation_id
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)  # ← stdout for container envs
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
```

Usage:

```python
logger = get_logger(__name__)

logger.info(
    "payment processed",
    extra={"correlation_id": "req-abc-123", "amount": 99.99}  # ← queryable fields
)
```

Output (one JSON line per log event):
```json
{"timestamp": "2024-01-15T10:23:45Z", "level": "INFO", "message": "payment processed", "correlation_id": "req-abc-123", "amount": 99.99}
```

---

### Correlation IDs

A **correlation ID** is a unique identifier attached to every log line for a single request, across all services. When user "Alice" hits an error, you search `correlation_id=req-abc-123` and see every log line from every service that touched her request.

```python
import uuid
from contextvars import ContextVar

# ← thread-safe storage for the current request's correlation ID
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

def generate_correlation_id() -> str:
    return str(uuid.uuid4())

# In your middleware (FastAPI example):
# correlation_id.set(request.headers.get("X-Correlation-ID") or generate_correlation_id())
```

---

### Log Levels by Environment

```python
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(level=getattr(logging, LOG_LEVEL))
```

| Environment | Recommended level |
|---|---|
| Development | `DEBUG` — see everything |
| Staging | `DEBUG` or `INFO` |
| Production | `INFO` — avoid `DEBUG` (too verbose, expensive) |
| Incident investigation | Temporarily `DEBUG`, revert after |

Never log sensitive data at any level: passwords, tokens, PII, card numbers.

---

## 6. Error Handling Patterns

### The Analogy

A surgeon does not stop an operation because one instrument is unavailable. They adapt: use a backup instrument, escalate to the attending, or close safely and reschedule. They never just crash.

Production services need the same discipline: handle failure gracefully, degrade safely, and never expose internals to callers.

---

### Graceful Degradation

When a non-critical dependency fails, return a degraded but valid response instead of a 500 error.

```python
def get_product_with_recommendations(product_id: int) -> dict:
    product = get_product(product_id)            # ← critical — must succeed

    try:
        recommendations = get_recommendations(product_id)  # ← nice-to-have
    except Exception:
        logger.warning("recommendations service unavailable, returning empty")
        recommendations = []                     # ← degrade gracefully

    return {"product": product, "recommendations": recommendations}
```

---

### Retry with Exponential Backoff

Transient failures (network blips, rate limits) often resolve if you wait and try again. The pattern is: retry, but wait longer between each attempt.

```python
import time
import random
from functools import wraps
from typing import Callable, TypeVar

T = TypeVar("T")

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """Decorator: retry on specified exceptions with exponential backoff + jitter."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        raise                    # ← final attempt, re-raise
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    jitter = random.uniform(0, delay * 0.1)  # ← avoid thundering herd
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.1f}s"
                    )
                    time.sleep(delay + jitter)
            raise RuntimeError("unreachable")   # ← type checker appeasement
        return wrapper
    return decorator


@retry_with_backoff(max_retries=3, exceptions=(ConnectionError, TimeoutError))
def call_payment_api(payload: dict) -> dict:
    ...
```

---

### Circuit Breaker Pattern

A **circuit breaker** monitors failures to an external service. After N failures, it "opens" — subsequent calls fail immediately without even trying, giving the failing service time to recover.

```
CLOSED state → normal operation, failures counted
     ↓ (failure_count >= threshold)
OPEN state → calls fail immediately (fast fail)
     ↓ (after timeout period)
HALF-OPEN state → allow one probe call
     ↓ success → back to CLOSED
     ↓ failure → back to OPEN
```

The `tenacity` library provides production-ready retry + circuit breaker logic:

```bash
pip install tenacity
```

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),                       # ← max 3 attempts
    wait=wait_exponential(multiplier=1, min=1, max=10),  # ← 1s, 2s, 4s...
    retry=retry_if_exception_type(ConnectionError),   # ← only retry these
)
def fetch_exchange_rate(currency: str) -> float:
    ...
```

---

## 7. Secrets Management

### The Analogy

A hotel gives guests a keycard, not a master key. The keycard expires. It can be deactivated instantly if lost. It grants access only to specific rooms. Nobody writes the master key combination on a sticky note on the front desk.

Secrets are your master keys. Treat them accordingly.

---

### The Cardinal Rule

Never hardcode secrets in source code. Not even "just for now." Not even "only in tests."

```python
# NEVER do this
DATABASE_URL = "postgresql://admin:super_secret_password@prod-db:5432/payments"
API_KEY = "sk-live-abc123xyz..."
```

Secrets in source code are:
- Visible to everyone with repo access
- Stored forever in git history
- Exposed in every build artifact, container image, and log

---

### The Environment Variable Pattern

```python
import os
from dotenv import load_dotenv

load_dotenv()                                        # ← reads .env in development

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is required")
```

In production (containers, cloud), inject secrets as environment variables from your deployment platform — never from a `.env` file.

---

### AWS Secrets Manager Pattern

For production workloads, environment variables alone are not enough — they are visible in process listings and pod specs. Use a secrets manager.

```python
import boto3
import json
from functools import lru_cache

@lru_cache(maxsize=None)                             # ← cache — avoid repeated API calls
def get_secret(secret_name: str) -> dict:
    """Fetch a secret from AWS Secrets Manager."""
    client = boto3.client("secretsmanager", region_name="us-east-1")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])      # ← returns dict of key:value pairs


# Usage at startup:
db_creds = get_secret("prod/payment_service/db")
DATABASE_URL = (
    f"postgresql://{db_creds['username']}:{db_creds['password']}"
    f"@{db_creds['host']}:5432/{db_creds['dbname']}"
)
```

The IAM role attached to your compute (EC2, ECS, Lambda) grants access to specific secrets — no hardcoded credentials anywhere.

---

### Secrets Hierarchy (Most to Least Secure)

```
AWS Secrets Manager / HashiCorp Vault   ← production, audited, rotatable
          ↓
Kubernetes Secrets (base64 encoded)     ← better than env vars, not encrypted at rest by default
          ↓
Environment variables                   ← acceptable for non-critical config
          ↓
.env file (never committed)             ← development only
          ↓
Hardcoded in source                     ← NEVER
```

---

## 8. Health Checks and Readiness

### The Analogy

Before a pilot takes off, they run a pre-flight checklist: fuel levels, flaps, instruments, radio. They do not just assume everything is fine. The checklist confirms the plane is ready to fly.

Health endpoints are your application's pre-flight checklist, run continuously by your deployment platform.

---

### /health vs /ready

Modern deployment platforms (Kubernetes, ECS, load balancers) poll two endpoints:

| Endpoint | Purpose | Fails when |
|---|---|---|
| `/health` (liveness) | Is the process alive? | Deadlock, crash, infinite loop |
| `/ready` (readiness) | Can it serve traffic? | DB not connected, cache not warmed |

If `/health` fails, the platform restarts the container.
If `/ready` fails, the platform stops routing traffic to that instance — but does not restart it.

---

### FastAPI Health Endpoint Pattern

```python
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
import time

app = FastAPI()

START_TIME = time.time()                             # ← track uptime

@app.get("/health")
async def health_check() -> JSONResponse:
    """Liveness probe — always returns 200 if the process is running."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ok", "uptime_seconds": int(time.time() - START_TIME)},
    )

@app.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    """Readiness probe — checks all dependencies before accepting traffic."""
    checks: dict[str, str] = {}

    # ← check database
    try:
        await db.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"

    # ← check cache (example)
    try:
        await redis_client.ping()
        checks["cache"] = "ok"
    except Exception as e:
        checks["cache"] = f"error: {e}"

    all_ok = all(v == "ok" for v in checks.values())
    return JSONResponse(
        status_code=status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "ready" if all_ok else "degraded", "checks": checks},
    )
```

The readiness endpoint returns 503 if any dependency is unhealthy — the load balancer stops sending traffic to this instance until it recovers.

---

## Putting It All Together

Production-ready Python is not one big thing — it is a collection of small disciplines, each solving a specific failure mode:

| Discipline | Failure mode it prevents |
|---|---|
| Src layout | "works on my machine" packaging bugs |
| Pydantic Settings | missing config causing runtime crashes |
| Virtual environments | dependency version conflicts |
| PEP 8 + Black | inconsistency slowing code review |
| Structured logging | inability to debug production incidents |
| Retry + backoff | transient network failures causing outages |
| Secrets management | credential leaks and security breaches |
| Health endpoints | traffic routed to broken instances |

Apply them consistently and your codebase becomes the kind that junior developers learn from, senior developers trust, and on-call engineers do not fear.

---

## Navigation

**[🏠 Back to README](../README.md)**

**Prev:** [← Performance Optimization](../18_performance_optimization/profiling.md) &nbsp;|&nbsp; **Next:** [Project Structure →](./project_structure.md)

**Related Topics:** [Project Structure](./project_structure.md) · [Coding Standards](./coding_standards.md) · [Environment Management](./environment_management.md) · [Packaging](./packaging.md) · [Interview Q&A](./interview.md)
