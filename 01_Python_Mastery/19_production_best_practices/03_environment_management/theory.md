# Environment Management — Theory

---

**[🏠 Back to README](../../README.md)** · **[⬆️ Root Theory](../theory.md)**

---

## Learning Priority

**Must Learn**: venv, pip freeze, requirements.txt, .env + python-dotenv
**Should Learn**: poetry, pyenv for Python version management
**Good to Know**: conda, pipenv, tox
**Reference**: direnv, nix, Docker as environment

---

## 1. venv — Python's Built-in Isolation

Each project is a separate apartment — they share the building (your OS) but never borrow each other's furniture (packages). If Project A needs `requests==2.28` and Project B needs `requests==2.31`, they cannot coexist in the same global Python. Virtual environments give each project its own private set of shelves.

`venv` is built into Python 3.3+. No installation needed.

```bash
python -m venv .venv           # ← create .venv/ in project root

# Activate (Mac/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

which python                   # ← confirms .venv/bin/python is active
deactivate                     # ← exit the environment
```

What `venv` creates:

```
.venv/
├── bin/
│   ├── python -> python3.11   # ← private Python interpreter
│   ├── pip
│   └── activate               # ← the activation script
├── lib/
│   └── python3.11/
│       └── site-packages/     # ← your installed packages live here
└── pyvenv.cfg                 # ← records which Python version this was created with
```

Always add `.venv/` to `.gitignore`. Never commit it — it is machine-specific and regeneratable.

---

## 2. pip and requirements.txt

**Pin versions for reproducibility.** An unpinned `requirements.txt` is a time bomb.

```
# BAD — unpinned
requests
flask
sqlalchemy
```

Run `pip install -r requirements.txt` today: flask 3.0.3. Run it six months later: flask 3.1.0 with a breaking change. Your CI passed; production broke.

```
# GOOD — pinned
flask==3.0.3
requests==2.31.0
sqlalchemy==2.0.30
werkzeug==3.0.3          # ← transitive dep, also pinned
```

**Generating a pinned requirements.txt:**

```bash
pip install flask requests sqlalchemy     # install what you need
pip freeze > requirements.txt            # ← captures everything installed
```

**Reproducing on another machine:**

```bash
pip install -r requirements.txt          # exact same versions
```

**The two-file pattern (best practice):**

```
requirements.in   ← you write this: direct deps, loose constraints
requirements.txt  ← machine-generated: all deps, exact pins
```

`pip-tools` automates this:

```bash
pip install pip-tools
pip-compile requirements.in    # ← writes requirements.txt with exact pins
pip-sync requirements.txt      # ← installs exactly those pins (removes extras)
```

---

## 3. .env Files

**Never put secrets in source code.** The pattern is: real values in `.env` (never committed), template in `.env.example` (always committed).

```bash
# .env  ← real values, NEVER commit this
DATABASE_URL=postgresql://localhost:5432/mydb
SECRET_KEY=dev-secret-not-for-production
DEBUG=true
LOG_LEVEL=DEBUG
```

```bash
# .env.example  ← template, always commit this
DATABASE_URL=postgresql://host:port/dbname
SECRET_KEY=your-secret-key-here
DEBUG=false
LOG_LEVEL=INFO
```

**Load .env with python-dotenv:**

```python
from dotenv import load_dotenv  # pip install python-dotenv
import os

load_dotenv()                    # ← reads .env into os.environ

db_url = os.getenv("DATABASE_URL")
debug = os.getenv("DEBUG", "false").lower() == "true"
```

**`.gitignore` rules (always include these):**

```
.env
.env.local
.env.production
*.env
```

In production (Docker, Kubernetes, ECS), inject secrets as real environment variables from your secrets manager — not from a `.env` file.

---

## 4. pyenv — Managing Multiple Python Versions

Your system might have Python 3.11, but a project requires 3.12. `pyenv` lets you install and switch between any Python version without touching your system Python.

```bash
# Install pyenv (Mac)
brew install pyenv
# Add to ~/.zshrc:
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

**Core commands:**

```bash
pyenv install 3.12.3       # install a Python version
pyenv install 3.10.14

pyenv global 3.12.3        # default for your entire user session
pyenv local 3.10.14        # pin THIS directory to 3.10.14
                           # ← creates a .python-version file
pyenv versions             # list all installed versions
python --version           # confirm what is active
```

**The `.python-version` file** is created by `pyenv local`. Commit it so every developer and CI machine uses the same Python version:

```
# .python-version
3.12.3
```

**Combine pyenv + venv:**

```bash
pyenv local 3.12.3         # use Python 3.12 for this project
python -m venv .venv       # creates venv with Python 3.12
source .venv/bin/activate
```

---

## 5. Poetry — Modern Dependency Management

Poetry replaces `pip`, `venv`, `pip-tools`, and part of `setuptools` with one unified tool. It manages dependencies, creates virtual environments, and builds/publishes packages.

```bash
pipx install poetry        # install poetry itself in isolation
```

**Key commands:**

```bash
poetry new my_project      # scaffold a new project with structure
poetry install             # install all deps, auto-creates .venv
poetry add requests        # add to [dependencies]
poetry add --group dev pytest black  # add to [dev] group only
poetry remove requests     # remove a dep
poetry run python src/main.py  # run in the managed venv
poetry shell               # spawn a shell with venv activated
poetry build               # creates .whl and .tar.gz in dist/
```

**pyproject.toml under Poetry:**

```toml
[tool.poetry]
name = "my_project"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.110"
pydantic-settings = "^2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
black = "^24.0"
ruff = "^0.4"
```

Poetry generates `poetry.lock` — exact pins for every package including transitive deps. Always commit `poetry.lock`.

**Dev vs prod dependencies:** Add runtime deps with `poetry add X`. Add tools only needed during development with `poetry add --group dev X`. When deploying to production, run `poetry install --without dev` to skip dev tools.

---

## 6. Docker as a Reproducible Environment

Docker packages your entire environment — Python version, system libraries, your code — into a single image that runs identically everywhere. No more "works on my machine."

**Dockerfile best practices:**

```dockerfile
# Use a specific version tag — never "latest"
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy and install deps first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source after deps (so dep changes don't invalidate source layer)
COPY src/ ./src/

# Run as non-root for security
RUN useradd -m appuser
USER appuser

CMD ["python", "-m", "my_package.main"]
```

**Layer caching principle:** Docker caches each layer. If you copy your entire source first, any code change invalidates the pip install layer. Copy `requirements.txt` first, install deps, then copy source — this way dep installs are only re-run when requirements change.

**.dockerignore** — always create this:

```
.venv
__pycache__
*.pyc
.env
.git
tests/
*.md
```

---

## 7. Common Mistakes

**Committing `.venv/`:** Contains thousands of machine-specific files. Add to `.gitignore` and share `requirements.txt` instead.

**Using `pip freeze` carelessly:** `pip freeze` captures dev tools and transitive deps mixed together. Use `pip-compile` from `requirements.in` for a clean locked file.

**Using system Python for projects:**

```bash
# BAD — installs into global Python
pip install flask

# GOOD — activate venv first
source .venv/bin/activate
pip install flask
```

**Committing `.env`:** This is the single most common way credentials end up in git. Add `.env` to `.gitignore` before creating the file, not after.

**Not pinning in production:** Unpinned dependencies break silently. A new minor version of a transitive dependency can change behavior. Always pin.

**Mixing Python versions without pyenv:** Different Python versions have different behavior for f-strings, walrus operators, match statements, and standard library changes. Pin your Python version with `.python-version`.

---

## Navigation

| | |
|---|---|
| ⬆️ Root Theory | [../theory.md](../theory.md) |
| 💻 Practice | [practice.md](./practice.md) |
| 📏 Coding Standards | [../01_coding_standards/theory.md](../01_coding_standards/theory.md) |
| 🏗️ Project Structure | [../02_project_structure_packaging/theory.md](../02_project_structure_packaging/theory.md) |
