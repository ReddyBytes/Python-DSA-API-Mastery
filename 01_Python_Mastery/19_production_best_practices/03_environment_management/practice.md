# Environment Management — Practice

---

**[⬆️ Root Practice](../practice.md)** · **[📖 Theory](./theory.md)**

---

### Q1 · venv — Create and Activate a Virtual Environment 🟢

Show all commands to: create a venv called `.venv`, activate it on Mac/Linux, confirm Python is from the venv, install `requests`, and deactivate.

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

<details><summary>💡 Hint</summary>Use python -m venv; which python confirms the active interpreter.</details>
<details><summary>✅ Answer</summary>

```bash
# Create the virtual environment
python -m venv .venv

# Activate (Mac/Linux)
source .venv/bin/activate

# Confirm the active Python
which python      # → /path/to/project/.venv/bin/python
python --version  # → Python 3.11.x

# Install a package
pip install requests

# Deactivate
deactivate
```
**Why:** `.venv` is the conventional name; `which python` confirms you are using the venv interpreter, not the system Python.
</details>

---

### Q2 · Requirements — Freeze and Reproduce 🟢

Show the workflow to: install three packages, freeze to `requirements.txt`, delete the venv, recreate it, and reinstall from the lockfile.

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

<details><summary>💡 Hint</summary>pip freeze captures all installed packages including transitive deps.</details>
<details><summary>✅ Answer</summary>

```bash
# Install packages
pip install flask requests sqlalchemy

# Freeze current state
pip freeze > requirements.txt

# Delete and recreate the venv (simulates another machine)
deactivate
rm -rf .venv
python -m venv .venv
source .venv/bin/activate

# Reproduce exact environment
pip install -r requirements.txt
pip list  # verify same versions
```
**Why:** `pip freeze` captures every installed package with exact version pins. On another machine or in CI, `pip install -r requirements.txt` reproduces the exact same environment.
</details>

---

### Q3 · .env Files — Load with python-dotenv 🟡

Write a `.env` file with `DATABASE_URL`, `SECRET_KEY`, and `DEBUG=true`. Write Python code to load it and read all three variables with correct types.

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

<details><summary>💡 Hint</summary>All env var values are strings; DEBUG needs explicit bool conversion.</details>
<details><summary>✅ Answer</summary>

```bash
# .env
DATABASE_URL=postgresql://localhost:5432/mydb
SECRET_KEY=dev-secret-minimum-32-chars-here
DEBUG=true
```

```python
from dotenv import load_dotenv
import os

load_dotenv()  # reads .env into os.environ

database_url: str = os.getenv("DATABASE_URL", "")
secret_key: str = os.getenv("SECRET_KEY", "")
debug: bool = os.getenv("DEBUG", "false").lower() == "true"

print(database_url)  # → postgresql://localhost:5432/mydb
print(debug)         # → True (bool, not "true")
```
**Why:** `load_dotenv()` reads `.env` and sets environment variables; `os.getenv` returns strings so booleans need explicit conversion.
</details>

---

### Q4 · pyenv — Install a Specific Python Version 🟡

Show all commands to install Python 3.12.3 using pyenv, pin it for a project directory, verify it is active, then create a venv with that version.

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

<details><summary>💡 Hint</summary>pyenv local creates a .python-version file in the current directory.</details>
<details><summary>✅ Answer</summary>

```bash
# Install the version
pyenv install 3.12.3

# Pin this directory to 3.12.3
pyenv local 3.12.3
# → creates .python-version file with content "3.12.3"

# Verify
python --version          # → Python 3.12.3
cat .python-version        # → 3.12.3

# Create a venv using this version
python -m venv .venv
source .venv/bin/activate
python --version           # → Python 3.12.3
```
**Why:** `pyenv local` creates `.python-version` which pyenv reads whenever you enter the directory; committing this file ensures all developers use the same Python version.
</details>

---

### Q5 · Poetry — Write the Dependency Section 🟡

Write the Poetry `pyproject.toml` section for a web service that depends on `fastapi ^0.110`, `pydantic-settings ^2.0`, `sqlalchemy ^2.0`, and has dev deps: `pytest ^8.0`, `black ^24.0`, `httpx ^0.27` (for testing).

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

<details><summary>💡 Hint</summary>Dev deps go in [tool.poetry.group.dev.dependencies].</details>
<details><summary>✅ Answer</summary>

```toml
[tool.poetry]
name = "web_service"
version = "0.1.0"
description = "Production web service"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.110"
pydantic-settings = "^2.0"
sqlalchemy = "^2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
black = "^24.0"
httpx = "^0.27"   # needed for FastAPI TestClient

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```
**Why:** `^0.110` means `>=0.110, <1.0`; dev deps in a group means `poetry install --without dev` skips them in production.
</details>

---

### Q6 · Dependencies — Dev vs Prod 🟡

Explain the difference between dev and prod dependencies. List which of these belong in dev vs prod: `flask`, `pytest`, `black`, `sqlalchemy`, `mypy`, `gunicorn`, `ruff`.

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

<details><summary>💡 Hint</summary>Ask: is this needed when the application is running in production?</details>
<details><summary>✅ Answer</summary>

**Production dependencies** (needed at runtime):
- `flask` — your web framework
- `sqlalchemy` — database ORM
- `gunicorn` — production WSGI server

**Dev-only dependencies** (only needed during development/CI):
- `pytest` — runs tests, not needed at runtime
- `black` — code formatter, not needed at runtime
- `mypy` — type checker, not needed at runtime
- `ruff` — linter, not needed at runtime

**Why this matters:** Production Docker images should be small and contain only runtime deps. Including pytest and black in a production image adds ~50MB for no benefit and increases the attack surface.

```bash
# Production install
poetry install --without dev

# Full install (local dev + CI)
poetry install
```
</details>

---

### Q7 · Docker — Write a Minimal Dockerfile 🟡

Write a Dockerfile for a Python 3.12 web service. It should: use a slim base, copy and install dependencies before source (for layer caching), run as a non-root user, and use CMD to start the app.

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

<details><summary>💡 Hint</summary>Copy requirements.txt first, pip install, then copy src. This maximizes cache hits.</details>
<details><summary>✅ Answer</summary>

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy deps first — layer is cached until requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source after deps
COPY src/ ./src/

# Run as non-root for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Start the application
CMD ["python", "-m", "my_package.main"]
```
**Why:** Layer ordering matters — if source changes but requirements do not, Docker uses the cached pip install layer. `--no-cache-dir` reduces image size. Non-root reduces blast radius if the container is compromised.
</details>

---

### Q8 · Pinning — Lock Transitive Dependencies 🟡

What is a transitive dependency and why must it be pinned? Show the difference between a `requirements.in` and the compiled `requirements.txt`.

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

<details><summary>💡 Hint</summary>Transitive deps are deps of your deps — you don't list them directly but they still get installed.</details>
<details><summary>✅ Answer</summary>

A **transitive dependency** is a package that one of your dependencies depends on. You do not declare it — it gets installed automatically.

Example: you depend on `flask`. Flask depends on `werkzeug` and `click`. Those are transitive.

```
# requirements.in (what you write — direct deps only)
flask>=3.0
requests>=2.28

# requirements.txt (what pip-compile generates — everything pinned)
# Generated by pip-compile
flask==3.0.3
werkzeug==3.0.3       # ← transitive dep of flask
click==8.1.7          # ← transitive dep of flask
requests==2.31.0
certifi==2024.2.2     # ← transitive dep of requests
urllib3==2.2.1        # ← transitive dep of requests
```

```bash
pip-compile requirements.in   # generate requirements.txt
pip-sync requirements.txt     # install exactly those versions
```

**Why:** If you only pin flask but not werkzeug, a werkzeug release could break your app even though your flask version did not change.
</details>

---

### Q9 · tox — Multi-version Testing 🟠

Write a `tox.ini` that runs pytest against Python 3.10, 3.11, and 3.12, with a separate `lint` environment that runs ruff and mypy.

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

<details><summary>💡 Hint</summary>tox envlist defines which envs to run; each env gets its own deps.</details>
<details><summary>✅ Answer</summary>

```ini
[tox]
envlist = py310, py311, py312, lint
isolated_build = true

[testenv]
deps =
    pytest>=8.0
    httpx>=0.27
commands =
    pytest tests/ -v

[testenv:lint]
deps =
    ruff>=0.4
    mypy>=1.10
commands =
    ruff check src/
    mypy src/

[testenv:py310]
basepython = python3.10

[testenv:py311]
basepython = python3.11

[testenv:py312]
basepython = python3.12
```

```bash
tox                   # run all envs
tox -e py312          # run only Python 3.12
tox -e lint           # run only lint
```
**Why:** tox creates an isolated venv for each Python version, ensuring your package installs and tests pass on all supported versions.
</details>

---

### Q10 · Capstone — Migrate requirements.txt to Poetry 🟠

You have a project with this `requirements.txt`. Migrate it to Poetry: identify direct vs transitive deps, write the `pyproject.toml`, and show the migration commands.

```
flask==3.0.3
requests==2.31.0
sqlalchemy==2.0.30
werkzeug==3.0.3
urllib3==2.2.1
certifi==2024.2.2
pytest==8.1.1
black==24.4.2
```

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

<details><summary>💡 Hint</summary>Direct deps are the ones you actually use; transitive deps (werkzeug, urllib3, certifi) are managed by Poetry automatically.</details>
<details><summary>✅ Answer</summary>

**Step 1: Identify direct deps**
- Direct (runtime): `flask`, `requests`, `sqlalchemy`
- Direct (dev): `pytest`, `black`
- Transitive (auto-managed): `werkzeug`, `urllib3`, `certifi`

**Step 2: Install Poetry and init project**

```bash
pipx install poetry
poetry init          # interactive setup
# or manually create pyproject.toml:
```

```toml
[tool.poetry]
name = "my_project"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.11"
flask = "^3.0"
requests = "^2.31"
sqlalchemy = "^2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
black = "^24.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

**Step 3: Install and generate lock file**

```bash
poetry install          # creates poetry.lock with all exact pins
poetry lock --check     # verify lock file is up to date
```

**Why:** Poetry resolves and locks transitive deps automatically in `poetry.lock`. You only declare your direct deps in `pyproject.toml`. This separates the "what you need" from the "exact versions installed."
</details>

---

## Navigation

| | |
|---|---|
| ⬆️ Root Practice | [../practice.md](../practice.md) |
| 📖 Theory | [theory.md](./theory.md) |
| 💻 Solve Locally | [practice_local.py](./practice_local.py) |
| 📏 Coding Standards | [../01_coding_standards/practice.md](../01_coding_standards/practice.md) |
| 🏗️ Project Structure | [../02_project_structure_packaging/practice.md](../02_project_structure_packaging/practice.md) |
