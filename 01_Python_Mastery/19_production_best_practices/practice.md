# Production Best Practices — Practice

---

**[🏠 Back to README](../README.md)** · **[📖 Theory](./theory.md)**

Covers all three subfolder topic areas plus the core theory content.

- Q1–Q8: Coding standards, PEP 8, type hints, formatters
- Q9–Q14: Project structure, pyproject.toml, packaging
- Q15–Q20: Virtual environments, requirements, .env
- Q21–Q25: Production patterns (logging, config, error handling)
- Q26–Q28: Docker, CI/CD basics
- Q29–Q30: Capstone problems

---

## Coding Standards

### Q1 · PEP 8 — Fix Naming and Spacing Violations 🟢

Fix all PEP 8 violations in this snippet.

```python
import sys,os
def getUserData(UserId,forceRefresh=False):
    userData={}
    if userData==None:
        return None
    return userData
```

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

<details><summary>💡 Hint</summary>Each import on its own line; snake_case for function and params; spaces around operators; `is None` not `== None`.</details>
<details><summary>✅ Answer</summary>

```python
import os
import sys


def get_user_data(user_id: int, force_refresh: bool = False) -> dict:
    user_data: dict = {}
    if user_data is None:
        return None
    return user_data
```
**Why:** Each import on its own line (E401); snake_case naming (N802/N803); spaces around `=` in assignment (E225); `is None` instead of `== None` (E711).
</details>

---

### Q2 · Type Hints — Annotate a Function 🟢

Add complete type hints to this function.

```python
def search_users(query, limit, active_only, fields):
    # returns list of matching user dicts
    ...
```

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

<details><summary>💡 Hint</summary>fields is a list of strings; return is list of dicts.</details>
<details><summary>✅ Answer</summary>

```python
def search_users(
    query: str,
    limit: int = 20,
    active_only: bool = False,
    fields: list[str] | None = None,
) -> list[dict[str, object]]:
    ...
```
**Why:** `list[str] | None` is Python 3.10+ union syntax; optional params with defaults; multi-line signature for readability.
</details>

---

### Q3 · Docstrings — Write a Complete Docstring 🟡

Write a Google-style docstring for `calculate_discount(price, discount_pct, max_discount)` that returns the discounted price, raises ValueError if discount_pct is not between 0 and 100.

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

<details><summary>💡 Hint</summary>Include: one-line summary, Args, Returns, Raises sections.</details>
<details><summary>✅ Answer</summary>

```python
def calculate_discount(
    price: float,
    discount_pct: float,
    max_discount: float | None = None,
) -> float:
    """Calculate the final price after applying a percentage discount.

    Args:
        price: Original price. Must be >= 0.
        discount_pct: Discount percentage (0–100 inclusive).
        max_discount: Cap on the absolute discount amount. None means no cap.

    Returns:
        Final price after discount, never below 0.

    Raises:
        ValueError: If discount_pct is not in range [0, 100].
    """
    ...
```
**Why:** One-sentence summary; blank line before Args; each arg describes constraints; Returns says what the value means, not just its type.
</details>

---

### Q4 · Formatters — Black and isort Config 🟡

Write the complete pyproject.toml configuration for black and isort targeting Python 3.11, line length 88. Explain what `profile = "black"` does for isort.

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

<details><summary>💡 Hint</summary>Without profile = "black", isort might format imports in a way black immediately reformats.</details>
<details><summary>✅ Answer</summary>

```toml
[tool.black]
line-length = 88
target-version = ["py311"]

[tool.isort]
profile = "black"
line_length = 88
```

`profile = "black"` tells isort to format imports to match black's style. Without it, black might reformat what isort just sorted, causing an infinite loop in pre-commit hooks.

**Why:** These two tools must agree on import block formatting. `profile = "black"` is the standard way to align them.
</details>

---

### Q5 · Ruff — Configure a Project Linter 🟡

Write the `[tool.ruff]` config that enables pycodestyle (E), pyflakes (F), isort (I), and bugbear (B) rules. Ignore line-length rule since black handles it.

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

<details><summary>💡 Hint</summary>E501 is the line-too-long rule.</details>
<details><summary>✅ Answer</summary>

```toml
[tool.ruff]
line-length = 88
target-version = "py311"
select = ["E", "F", "I", "B"]
ignore = ["E501"]

[tool.ruff.per-file-ignores]
"tests/*" = ["S101"]  # allow assert in tests
```
**Why:** `B` (bugbear) catches subtle bugs like mutable default args; `E501` is redundant when black enforces line length.
</details>

---

### Q6 · Pre-commit — Set Up and Install Hooks 🟡

Write the `.pre-commit-config.yaml` with black, ruff (auto-fix), mypy, and the `detect-private-key` hook. Show the setup commands.

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

<details><summary>💡 Hint</summary>detect-private-key is in the pre-commit/pre-commit-hooks repo.</details>
<details><summary>✅ Answer</summary>

```yaml
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

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: detect-private-key
```

```bash
pip install pre-commit
pre-commit install          # installs hooks into .git/hooks/
pre-commit run --all-files  # run once on all existing files
```
**Why:** After `pre-commit install`, every `git commit` automatically runs all hooks. Failed hooks block the commit.
</details>

---

### Q7 · mypy — Fix Type Errors 🟡

What does mypy strict mode flag in this code? Show the fixed version.

```python
def get_item(items, index):
    if index >= len(items):
        return None
    return items[index]

result = get_item(["a", "b", "c"], 1)
print(result.upper())
```

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

<details><summary>💡 Hint</summary>The return type is str | None — calling .upper() on it is unsafe.</details>
<details><summary>✅ Answer</summary>

```python
def get_item(items: list[str], index: int) -> str | None:
    if index >= len(items):
        return None
    return items[index]

result = get_item(["a", "b", "c"], 1)
if result is not None:            # ← mypy requires this guard
    print(result.upper())
```
**Why:** mypy detects that `result` could be `None` and calling `.upper()` on `None` raises `AttributeError` at runtime. The `is not None` guard makes the code type-safe.
</details>

---

### Q8 · Naming — Convert a Class to Python Conventions 🟡

Rewrite this class with correct Python naming throughout.

```python
class dataProcessor:
    MAX_BATCH_SIZE = 1000
    def processRecord(self, inputData, batchSize=100):
        numProcessed = 0
        return numProcessed
    def cleanData(self, rawData):
        return rawData
```

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

<details><summary>💡 Hint</summary>Class → PascalCase; methods/params/variables → snake_case; constants stay UPPER_CASE.</details>
<details><summary>✅ Answer</summary>

```python
class DataProcessor:
    MAX_BATCH_SIZE = 1000

    def process_record(
        self, input_data: dict, batch_size: int = 100
    ) -> int:
        num_processed = 0
        return num_processed

    def clean_data(self, raw_data: list) -> list:
        return raw_data
```
**Why:** `DataProcessor` is PascalCase; methods are snake_case; `MAX_BATCH_SIZE` stays UPPER_CASE (it is a class constant, not a variable).
</details>

---

## Project Structure and Packaging

### Q9 · Layout — Src vs Flat Layout 🟢

Explain the difference between src layout and flat layout. When does flat layout cause hidden bugs?

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

<details><summary>💡 Hint</summary>Think about what gets added to sys.path when running pytest from the project root.</details>
<details><summary>✅ Answer</summary>

**Flat layout:** your package sits in the project root. Running `pytest` from the root adds `.` to `sys.path`, so `import my_package` finds the local source directory — not an installed wheel.

**Src layout:** your package is at `src/my_package/`. The `src/` directory has no `__init__.py`, so Python never accidentally finds your package there without installation.

**The hidden bug with flat layout:** You build a wheel, install it on another machine, and something works differently — because your tests were running against the source directory, not the installed package. The difference only surfaces after distribution.

**Fix:** Use src layout for any package you distribute. Use `pip install -e .` during development.
</details>

---

### Q10 · pyproject.toml — Write a Complete Config 🟡

Write a complete `pyproject.toml` for a package `my_service` that: uses setuptools, targets Python 3.11+, has runtime deps (fastapi, pydantic-settings), dev deps (pytest, black, ruff), and configures black + ruff + pytest in the same file.

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

<details><summary>💡 Hint</summary>Tool configs go under [tool.X] sections. All in one file.</details>
<details><summary>✅ Answer</summary>

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "my_service"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110",
    "pydantic-settings>=2.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "black>=24.0", "ruff>=0.4"]

[tool.black]
line-length = 88
target-version = ["py311"]

[tool.ruff]
line-length = 88
select = ["E", "F", "I"]
ignore = ["E501"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
```
**Why:** `pyproject.toml` replaces `setup.py`, `setup.cfg`, `.flake8`, `pytest.ini` — one file for everything.
</details>

---

### Q11 · `__init__.py` — Public API Design 🟡

Write the `__init__.py` for a package `notifications` that exposes `EmailSender`, `SMSSender`, and `NotificationError`. Explain what `__all__` does.

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

<details><summary>💡 Hint</summary>__all__ controls what `from package import *` exposes.</details>
<details><summary>✅ Answer</summary>

```python
# src/notifications/__init__.py

__version__ = "1.0.0"

from .email_sender import EmailSender
from .sms_sender import SMSSender
from .exceptions import NotificationError

__all__ = ["EmailSender", "SMSSender", "NotificationError"]
```

`__all__` does two things:
1. Controls what `from notifications import *` exposes (only the listed names)
2. Documents the package's public API — anything not in `__all__` is considered internal

**Why:** Without `__all__`, `import *` would bring in everything including private helpers, leading to namespace pollution.
</details>

---

### Q12 · Entry Points — Add a CLI 🟡

Add an entry point `notify` that runs `notifications.cli:main`. Write a minimal `cli.py` with argument parsing.

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

<details><summary>💡 Hint</summary>Entry points live under [project.scripts] in pyproject.toml.</details>
<details><summary>✅ Answer</summary>

```toml
[project.scripts]
notify = "notifications.cli:main"
```

```python
# src/notifications/cli.py
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Send notifications")
    parser.add_argument("--to", required=True, help="Recipient address")
    parser.add_argument(
        "--channel",
        choices=["email", "sms"],
        default="email",
    )
    parser.add_argument("--message", required=True)
    args = parser.parse_args()
    print(f"Sending {args.channel} to {args.to}: {args.message}")
```
**Why:** After `pip install notifications`, users run `notify --to alice@example.com --message hello` — no `python -m` prefix needed.
</details>

---

### Q13 · Build — Build and Check a Distribution 🟡

List the commands to build both sdist and wheel, check the distributions, and explain what `twine check` verifies.

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)

<details><summary>💡 Hint</summary>Use the `build` package; twine check validates metadata before upload.</details>
<details><summary>✅ Answer</summary>

```bash
pip install build twine

# Build both sdist (.tar.gz) and wheel (.whl)
python -m build

# Check distributions for common problems
twine check dist/*
```

`twine check` verifies:
- README renders correctly on PyPI (no broken RST/Markdown)
- Package metadata is valid (name, version, description)
- No files that would cause upload failures

**Why:** It is far better to catch metadata errors locally than after uploading to PyPI where they appear on the public package page.
</details>

---

### Q14 · Editable Install — When and Why 🟡

Explain the difference between `pip install .` and `pip install -e .`. When would you use each?

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)

<details><summary>💡 Hint</summary>-e means editable — changes to source are immediately visible without reinstalling.</details>
<details><summary>✅ Answer</summary>

`pip install .` — copies your package into site-packages. Changes to source require reinstalling.

`pip install -e .` — creates a link to your source directory. Changes are immediately reflected without reinstalling.

**Use `pip install .`** when:
- Building a Docker image (you want a static copy)
- Running in CI after building a wheel

**Use `pip install -e .`** when:
- Actively developing (you change code constantly)
- Running tests locally (you want live source)

**Why this matters for src layout:** With src layout, you must install the package before you can import it. Editable install gives you installation benefits with development convenience.
</details>

---

## Virtual Environments and Requirements

### Q15 · venv — Create, Install, Freeze 🟢

Show the complete workflow: create venv, activate, install two packages, freeze to requirements.txt.

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)

<details><summary>💡 Hint</summary>python -m venv, source activate, pip install, pip freeze.</details>
<details><summary>✅ Answer</summary>

```bash
python -m venv .venv
source .venv/bin/activate

pip install flask sqlalchemy

pip freeze > requirements.txt
# requirements.txt now contains flask, sqlalchemy, and all transitive deps with exact pins

cat requirements.txt
# flask==3.0.3
# sqlalchemy==2.0.30
# werkzeug==3.0.3
# ...
```
**Why:** Freezing immediately after installing captures exact versions. Do not freeze after installing dev tools or you pollute your production requirements.
</details>

---

### Q16 · pip-tools — The Two-File Pattern 🟡

Explain the `requirements.in` / `requirements.txt` two-file pattern. Write a `requirements.in`, show the compile command, and explain what `pip-sync` does differently from `pip install -r`.

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)

<details><summary>💡 Hint</summary>pip-sync removes packages not in the lockfile; pip install only adds.</details>
<details><summary>✅ Answer</summary>

```
# requirements.in  (human-authored — direct deps, loose constraints)
flask>=3.0
requests>=2.28
sqlalchemy>=2.0
```

```bash
pip-compile requirements.in    # generates requirements.txt with exact pins
pip-sync requirements.txt      # install exactly those pins
```

`pip install -r requirements.txt` installs listed packages and leaves anything already installed.

`pip-sync requirements.txt` makes your environment match the file exactly — it installs missing packages AND removes packages not in the file.

**Why:** `pip-sync` is the correct command for CI environments where you want a perfectly clean, reproducible install.
</details>

---

### Q17 · .env — Best Practices 🟡

List 5 best practices for `.env` file handling. Show the `.gitignore` entries needed and the `.env.example` pattern.

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)

<details><summary>💡 Hint</summary>Think: what to commit, what not to commit, how to communicate required vars to teammates.</details>
<details><summary>✅ Answer</summary>

**5 best practices:**
1. Never commit `.env` — add to `.gitignore` before creating the file
2. Always commit `.env.example` with placeholder values
3. Never log env var values — log only "loaded" or "missing"
4. Validate required vars at startup (not lazily when first needed)
5. Use different `.env` files per environment: `.env.test`, `.env.staging`

```
# .gitignore
.env
.env.local
.env.production
*.env
```

```bash
# .env.example  (always committed)
DATABASE_URL=postgresql://host:port/dbname
SECRET_KEY=generate-a-32-char-random-string
DEBUG=false
LOG_LEVEL=INFO
```
**Why:** `.env.example` communicates to new developers what variables they need to set up. Without it, they get cryptic errors when running the app for the first time.
</details>

---

### Q18 · pyenv — Version Pinning 🟡

A project needs Python 3.10.14. Show all commands to install it with pyenv, pin it to the project, and verify the version in CI.

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)

<details><summary>💡 Hint</summary>.python-version file is committed; CI reads it via pyenv or setup-python action.</details>
<details><summary>✅ Answer</summary>

```bash
# Install the version
pyenv install 3.10.14

# Pin the project directory
pyenv local 3.10.14
# Creates .python-version file — commit this

# Verify
cat .python-version   # → 3.10.14
python --version      # → Python 3.10.14
```

In GitHub Actions CI:
```yaml
- uses: actions/setup-python@v5
  with:
    python-version-file: .python-version   # reads .python-version
```

**Why:** Committing `.python-version` makes the Python version requirement explicit and enforced — no "which Python should I use?" ambiguity.
</details>

---

### Q19 · Poetry — Daily Workflow 🟡

Show the Poetry commands for: adding a new dep, adding a dev-only dep, updating one dep, running tests, and checking if the lock file is up to date.

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)

<details><summary>💡 Hint</summary>poetry add, poetry add --group dev, poetry update, poetry run, poetry lock --check.</details>
<details><summary>✅ Answer</summary>

```bash
# Add a runtime dependency
poetry add httpx

# Add a dev-only dependency
poetry add --group dev pytest-asyncio

# Update one dependency to latest compatible version
poetry update httpx

# Run tests in the managed venv
poetry run pytest tests/ -v

# Verify lock file is consistent with pyproject.toml
poetry lock --check

# Install everything (fresh machine or CI)
poetry install

# Install without dev deps (production)
poetry install --without dev
```
**Why:** `poetry lock --check` should be a CI step — it fails if someone updated `pyproject.toml` without regenerating the lock file, which would cause non-reproducible installs.
</details>

---

### Q20 · Dependency Conflicts — Diagnose and Resolve 🟡

You run `pip install -r requirements.txt` and get a conflict error. Describe your debugging process. What command shows you the full dependency tree?

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)

<details><summary>💡 Hint</summary>pip-tree (pipdeptree) shows the full dependency graph.</details>
<details><summary>✅ Answer</summary>

```bash
# 1. See the full dependency graph
pip install pipdeptree
pipdeptree                        # shows tree of all installed packages
pipdeptree --reverse --packages httpx  # what requires httpx?

# 2. See what version pip would install
pip install --dry-run conflicting_package

# 3. Use pip's resolver with verbose output
pip install -r requirements.txt -v 2>&1 | grep "conflict"

# 4. With poetry: see why a dep is installed
poetry why requests
```

**Debugging steps:**
1. Read the error — it usually names the two conflicting packages and what versions they each need
2. Find which direct dep pulls in each conflicting transitive dep
3. Update the direct dep that has the looser constraint, or pin the transitive dep explicitly
4. Recompile: `pip-compile requirements.in`

**Why:** Understanding the dependency graph prevents solving conflicts blindly by pinning random versions.
</details>

---

## Production Patterns

### Q21 · Logging — Structured JSON Logging 🟡

Write a `JSONFormatter` class and a `get_logger` function that returns a logger with JSON output. Show an example log line.

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)

<details><summary>💡 Hint</summary>Extend logging.Formatter and override format(); output to stdout for container environments.</details>
<details><summary>✅ Answer</summary>

```python
import json
import logging
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
        if record.exc_info:
            obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(obj)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
```

Example output:
```json
{"ts": "2024-01-15T10:23:45Z", "level": "INFO", "logger": "app", "msg": "user logged in", "module": "auth", "line": 42}
```
**Why:** JSON logs are queryable by any log aggregator (Datadog, Splunk, CloudWatch). Plain text logs require regex parsing.
</details>

---

### Q22 · Config — Pydantic Settings Pattern 🟡

Write a `Settings` class using pydantic-settings that validates DATABASE_URL (required), SECRET_KEY (required, min 32 chars), DEBUG (bool, default False), LOG_LEVEL (default "INFO"). Add a cached `get_settings()` function.

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)

<details><summary>💡 Hint</summary>Use Field(...) for required fields; lru_cache on get_settings() avoids re-parsing env on every call.</details>
<details><summary>✅ Answer</summary>

```python
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(..., description="PostgreSQL DSN")
    secret_key: str = Field(..., min_length=32)
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

Usage:
```python
settings = get_settings()
print(settings.database_url)  # type-safe, validated at startup
print(settings.debug)          # bool, not the string "true"
```
**Why:** Pydantic Settings raises a clear `ValidationError` at startup if any required field is missing — not a cryptic `None` error buried in a request handler.
</details>

---

### Q23 · Error Handling — Graceful Degradation 🟡

Write a function `get_product_page` that fetches a product (critical) and recommendations (optional). If recommendations fail, return empty list and log a warning.

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)

<details><summary>💡 Hint</summary>Wrap the non-critical call in try/except; always return a valid response.</details>
<details><summary>✅ Answer</summary>

```python
import logging

logger = logging.getLogger(__name__)


def get_product_page(product_id: int) -> dict:
    """Fetch product with optional recommendations.

    Returns a valid response even if recommendations service is down.
    """
    product = get_product(product_id)  # ← critical: let exceptions propagate

    try:
        recommendations = get_recommendations(product_id)
    except Exception as exc:
        logger.warning(
            "Recommendations service unavailable, degrading gracefully",
            extra={"product_id": product_id, "error": str(exc)},
        )
        recommendations = []  # ← degrade: empty list is a valid response

    return {"product": product, "recommendations": recommendations}
```
**Why:** A single failed non-critical service should not return a 500 to the user. Graceful degradation returns a partial but valid response and logs the failure for investigation.
</details>

---

### Q24 · Retry — Exponential Backoff with tenacity 🟡

Write a function decorated with tenacity that retries up to 3 times on `ConnectionError` or `TimeoutError`, with exponential backoff (1s, 2s, 4s).

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)

<details><summary>💡 Hint</summary>Use stop_after_attempt, wait_exponential, retry_if_exception_type.</details>
<details><summary>✅ Answer</summary>

```python
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=30),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    reraise=True,
)
def call_payment_api(payload: dict) -> dict:
    """Call external payment API with automatic retry on transient failures."""
    ...
```
**Why:** `reraise=True` means after all retries are exhausted, the original exception propagates — not a tenacity-specific exception. `wait_exponential` uses 1s, 2s, 4s, 8s... capped at `max=30`.
</details>

---

### Q25 · Secrets — Hierarchy and Best Practices 🟡

Describe the secrets hierarchy from most to least secure. For each level, name the main risk.

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)

<details><summary>💡 Hint</summary>Five levels: Vault/AWS SM, K8s Secrets, env vars, .env file, hardcoded.</details>
<details><summary>✅ Answer</summary>

```
AWS Secrets Manager / HashiCorp Vault
  Risk: IAM misconfiguration grants broad access
  Benefit: audited, rotatable, encrypted at rest

Kubernetes Secrets
  Risk: not encrypted at rest by default (needs etcd encryption)
  Benefit: better than plain env vars, native K8s integration

Environment Variables
  Risk: visible in process listings, logs if printed
  Benefit: simple, works everywhere

.env file (gitignored, never committed)
  Risk: accidentally committed; stays in git history forever
  Benefit: convenient for local development

Hardcoded in source code
  Risk: visible to all repo access; forever in git history; in every build artifact
  Benefit: NONE — never do this
```
**Why:** The lower in the hierarchy, the wider the blast radius of a secret being compromised.
</details>

---

## Docker and CI/CD

### Q26 · Docker — Layer Caching Optimization 🟡

Explain why the order of COPY and RUN commands in a Dockerfile matters for caching. Show the correct order for a Python app.

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)

<details><summary>💡 Hint</summary>Each instruction is a layer. When a layer changes, all subsequent layers are invalidated.</details>
<details><summary>✅ Answer</summary>

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 1. Copy requirements FIRST — changes rarely
COPY requirements.txt .
# 2. Install deps — cached until requirements.txt changes
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy source LAST — changes often
COPY src/ ./src/
```

**Wrong order (slow):**
```dockerfile
COPY src/ ./src/        # every code change invalidates
COPY requirements.txt .
RUN pip install ...     # re-runs pip on EVERY code change
```

**Why:** Docker caches each layer until something above it changes. `requirements.txt` rarely changes; source code changes constantly. Putting the slow step (pip install) before the frequently-changing step means it gets cached almost every time.
</details>

---

### Q27 · Docker — .dockerignore 🟡

Write a `.dockerignore` file for a Python project and explain why each entry matters.

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)

<details><summary>💡 Hint</summary>Think: what should never be in a Docker image? (secrets, dev tools, git history)</details>
<details><summary>✅ Answer</summary>

```
# .dockerignore
.venv/               # machine-specific, large (~500MB), not needed
__pycache__/         # generated bytecache, regenerated at runtime
*.pyc                # compiled bytecode
.env                 # CRITICAL: secrets must never enter images
.env.*               # all env files
.git/                # git history is large and not needed
.pytest_cache/       # test cache
tests/               # tests not needed in production image
docs/                # documentation
*.md                 # markdown files
Dockerfile*          # no need to include Dockerfiles in images
.pre-commit-config.yaml
```
**Why:** Excluding `.env` is the most important rule — secrets in Docker images end up in registries, layer history, and logs. Excluding `.venv` keeps the image small and avoids using wrong package versions.
</details>

---

### Q28 · CI/CD — GitHub Actions Workflow 🟡

Write a minimal GitHub Actions workflow that: installs Python 3.11, installs dev deps, runs ruff, mypy, and pytest on every push.

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)

<details><summary>💡 Hint</summary>Use actions/setup-python and pip install ".[dev]".</details>
<details><summary>✅ Answer</summary>

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Lint
        run: ruff check src/

      - name: Type check
        run: mypy src/

      - name: Test
        run: pytest tests/ -v --tb=short
```
**Why:** Running lint before tests fails fast on style errors without spending time on the test suite. `cache: "pip"` caches pip downloads between runs for faster CI.
</details>

---

## Capstone

### Q29 · Capstone — Production App Checklist 🟠

You are shipping a new Python web service to production. List the 10 things you must verify before deploying. For each, name the tool or pattern.

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)

<details><summary>💡 Hint</summary>Cover: structure, deps, config, tests, logging, secrets, Docker, CI, health checks, error handling.</details>
<details><summary>✅ Answer</summary>

1. **Project structure** — src layout, clean separation of models/services/api
2. **Dependencies pinned** — `poetry.lock` or pinned `requirements.txt` committed
3. **No hardcoded secrets** — all secrets via env vars or AWS Secrets Manager
4. **Tests pass** — `pytest` with coverage ≥ 80%, unit + integration
5. **Linting clean** — `ruff check src/` and `mypy src/` both pass
6. **Structured logging** — JSON format, correct levels per environment
7. **Config validated at startup** — Pydantic Settings raises on missing required vars
8. **Health endpoints** — `/health` (liveness) and `/ready` (readiness) implemented
9. **Docker image built and tested** — `docker build` succeeds, non-root user, no secrets in image
10. **CI pipeline green** — all steps pass on the release branch

**Why:** Each item prevents a specific class of production failure. Skipping any one of them is a known risk you are consciously accepting.
</details>

---

### Q30 · Capstone — Debug a Production Issue 🟠

Your service has been running fine for 3 months. After a dependency update, it fails in production but passes locally. Walk through your diagnostic process using the production best practices from this module.

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)

<details><summary>💡 Hint</summary>Think about: dependency versions, environment differences, log comparison, src layout, config.</details>
<details><summary>✅ Answer</summary>

**Step 1: Compare environments**
```bash
# Local
pip list | grep failing_package

# Production (in the container)
docker exec -it container_name pip list | grep failing_package
```

**Step 2: Check what changed**
```bash
git diff HEAD~1 requirements.txt   # or poetry.lock
# Look for any version changes since last working deploy
```

**Step 3: Check logs for the actual error**
```bash
# Search structured logs for the error
# Example with CloudWatch: filter by level=ERROR, ts >= deployment_time
```

**Step 4: Reproduce with the production environment**
```bash
# Pull the exact image that runs in production
docker run -e DATABASE_URL=... my_service:latest python -c "from my_service import main; main()"
```

**Step 5: Narrow the failure**
- Is it a missing env var? (Pydantic Settings would catch this at startup)
- Is it a version incompatibility? (check pip-compile output)
- Is it a platform difference? (arm64 vs x86_64 packages)
- Is it a Python version difference? (`pyenv` / `.python-version`)

**Step 6: Fix and prevent recurrence**
- Pin the transitive dep that changed
- Add a test that covers the failing case
- Run `pre-commit run --all-files` before deploying

**Why:** The key insight is that most "works locally, fails in production" bugs come from environment differences — not code bugs. Structured logging, pinned deps, and identical Docker environments eliminate most of these.
</details>

---

## Navigation

**[🏠 Back to README](../README.md)** · **[📖 Theory](./theory.md)**

**Subfolder Practice:**
- [Coding Standards — 10 Qs](./01_coding_standards/practice.md)
- [Project Structure & Packaging — 10 Qs](./02_project_structure_packaging/practice.md)
- [Environment Management — 10 Qs](./03_environment_management/practice.md)

**Solve Locally:** [practice_local.py](./practice_local.py)
