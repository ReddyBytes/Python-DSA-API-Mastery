# Production Best Practices — Cheatsheet

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Project Structure →](./project_structure.md)

**Related Topics:** [Theory](./theory.md) · [Project Structure](./project_structure.md) · [Environment Management](./environment_management.md) · [Packaging](./packaging.md)

---

## Project Structure Template (Src Layout)

```
my_project/
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── main.py              # entry point
│       ├── config.py            # settings (pydantic)
│       ├── models/              # domain models
│       ├── services/            # business logic
│       ├── api/                 # HTTP layer
│       └── utils/               # shared helpers
├── tests/
│   ├── conftest.py              # shared fixtures
│   ├── unit/
│   └── integration/
├── .env.example                 # template — always commit
├── .env                         # real values — NEVER commit
├── .pre-commit-config.yaml
├── pyproject.toml
├── Dockerfile
└── README.md
```

Use **src layout** for libraries/distributed packages.
Use **flat layout** for standalone apps or simple scripts.

---

## Environment Tool Comparison

| Tool | Install | Create env | Add dep | Lock deps | Build/publish |
|---|---|---|---|---|---|
| `venv` + `pip` | built-in | `python -m venv .venv` | `pip install X` | manual | separate |
| `pip-tools` | `pip install pip-tools` | `python -m venv .venv` | edit `requirements.in` | `pip-compile` | separate |
| `poetry` | `pipx install poetry` | `poetry install` | `poetry add X` | automatic | `poetry build` |
| `conda` | installer | `conda create -n env` | `conda install X` | `conda env export` | separate |

### Quick Commands

```bash
# venv
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
deactivate

# pip-tools
pip-compile requirements.in            # pin deps → requirements.txt
pip-sync requirements.txt             # install exactly those pins

# poetry
poetry new my_project                  # scaffold
poetry add requests                    # add dep
poetry add --group dev pytest          # dev dep
poetry install                         # install all
poetry run python src/main.py          # run in venv
poetry build                           # build wheel

# pyenv (Python version manager)
pyenv install 3.12.3                   # install a Python version
pyenv local 3.12.3                     # pin version for this directory
pyenv versions                         # list installed versions
```

---

## PEP 8 Rules Cheatsheet

| Rule | Do | Don't |
|---|---|---|
| Indentation | 4 spaces | tabs |
| Max line length | 88 chars (Black default) | 120+ |
| Function names | `process_payment` | `ProcessPayment` |
| Class names | `PaymentService` | `payment_service` |
| Constants | `MAX_RETRIES = 3` | `maxRetries = 3` |
| Two blank lines | between top-level defs | between methods |
| Import order | stdlib → third-party → local | mixed |
| Boolean comparisons | `if x is None:` | `if x == None:` |
| String quotes | consistent (Black picks `"`) | mixed |

---

## Formatter and Linter Commands

```bash
# Black — auto-format
black src/ tests/                       # format in place
black --check src/                     # CI: exit 1 if changes needed

# isort — sort imports
isort src/ tests/

# Ruff — lint + auto-fix (replaces flake8 + isort)
ruff check src/                        # lint only
ruff check --fix src/                  # auto-fix

# mypy — type checking
mypy src/                              # check all
mypy src/payment_service/config.py    # check one file

# pre-commit — run all hooks manually
pre-commit run --all-files
```

---

## Pre-commit Config Example

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
        additional_dependencies: [pydantic-settings]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-merge-conflict
      - id: detect-private-key             # ← blocks committing secrets
```

```bash
# Install hooks:
pip install pre-commit
pre-commit install
```

---

## Config Pattern — Pydantic Settings

```python
# src/my_package/config.py
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    # Required — will raise ValidationError at startup if missing
    database_url: str = Field(..., description="PostgreSQL DSN")
    secret_key: str = Field(..., min_length=32)

    # Optional with defaults
    debug: bool = False
    log_level: str = "INFO"
    max_retries: int = 3
    allowed_hosts: list[str] = ["localhost"]

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache
def get_settings() -> Settings:
    return Settings()                     # cached — only parses once

settings = get_settings()
```

Usage:
```python
from my_package.config import settings
print(settings.database_url)             # type-safe, validated
```

---

## Production Logging Setup

```python
# src/my_package/logging_config.py
import logging
import json
import sys
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        obj = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        for key in ("correlation_id", "user_id", "request_id"):
            if hasattr(record, key):
                obj[key] = getattr(record, key)
        if record.exc_info:
            obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(obj)

def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logging.basicConfig(level=level, handlers=[handler])

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
```

Usage:
```python
from my_package.logging_config import configure_logging, get_logger

configure_logging(level="INFO")          # call once at app startup
logger = get_logger(__name__)

logger.info("user logged in", extra={"user_id": 42, "correlation_id": "req-001"})
logger.error("payment failed", exc_info=True, extra={"amount": 99.99})
```

---

## Retry with Backoff (tenacity)

```bash
pip install tenacity
```

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=30),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    reraise=True,
)
def call_external_api(payload: dict) -> dict:
    ...
```

---

## Health Endpoint Pattern (FastAPI)

```python
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})

@app.get("/ready")
async def ready(db=Depends(get_db)) -> JSONResponse:
    checks = {}
    try:
        await db.execute("SELECT 1")
        checks["db"] = "ok"
    except Exception as e:
        checks["db"] = str(e)

    ok = all(v == "ok" for v in checks.values())
    code = status.HTTP_200_OK if ok else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse({"status": "ready" if ok else "degraded", "checks": checks}, status_code=code)
```

---

## 12-Factor App Checklist

| Factor | What it means |
|---|---|
| I. Codebase | One repo per app, multiple deploys from same codebase |
| II. Dependencies | Explicitly declared in `pyproject.toml` / `requirements.txt` |
| III. Config | All config from environment variables, not hardcoded |
| IV. Backing services | Treat DB, cache, queue as attached resources (URL-configured) |
| V. Build/release/run | Strictly separate build, release, and run stages |
| VI. Processes | Stateless processes — store state in backing services |
| VII. Port binding | Export services via port binding (not app servers) |
| VIII. Concurrency | Scale out via process model |
| IX. Disposability | Fast startup, graceful shutdown |
| X. Dev/prod parity | Keep development and production as similar as possible |
| XI. Logs | Treat logs as event streams — write to stdout |
| XII. Admin processes | Run admin tasks as one-off processes |

---

## Secrets Hierarchy (Most to Least Secure)

```
AWS Secrets Manager / HashiCorp Vault   production — audited, rotatable
Kubernetes Secrets                      better than plain env vars
Environment variables                   acceptable for non-critical config
.env file (gitignored)                  development only
Hardcoded in source                     NEVER
```

---

## pyproject.toml Reference

```toml
[project]
name = "my_package"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["fastapi>=0.110", "pydantic-settings>=2.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0", "black>=24.0", "ruff>=0.4", "mypy>=1.10"]

[tool.black]
line-length = 88
target-version = ["py311"]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
```

---

## Navigation

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Project Structure →](./project_structure.md)

**Related Topics:** [Theory](./theory.md) · [Project Structure](./project_structure.md) · [Environment Management](./environment_management.md) · [Packaging](./packaging.md)
