# Project Structure & Packaging — Theory

---

**[🏠 Back to README](../../README.md)** · **[⬆️ Root Theory](../theory.md)**

---

## Learning Priority

**Must Learn**: src/ layout, pyproject.toml, __init__.py, entry_points
**Should Learn**: Makefile/invoke tasks, MANIFEST.in, build + twine
**Good to Know**: namespace packages, editable installs (pip install -e .)
**Reference**: flit, hatch, setuptools legacy

---

## 1. Standard Project Layout

Think of project layout like a well-organized kitchen — everything in the right drawer so any cook can work efficiently without asking where things are. A new engineer joining your project should be able to find the business logic, the tests, and the config in under 30 seconds.

There are two main conventions.

**Flat layout** — your package sits at the project root:

```
my_project/
├── my_package/          # ← importable package at root
│   ├── __init__.py
│   └── core.py
├── tests/
├── pyproject.toml
└── README.md
```

**Src layout** — package is nested under `src/`:

```
my_project/
├── src/
│   └── my_package/      # ← importable package under src/
│       ├── __init__.py
│       └── core.py
├── tests/
├── pyproject.toml
└── README.md
```

**Why src layout wins for libraries:** With flat layout, running `pytest` from the root adds your local directory to `sys.path`, so tests import the raw source folder — not the installed wheel. This hides packaging bugs until after you ship. Src layout forces `pip install -e .` first, making your dev environment mirror the user's environment exactly.

**Decision guide:**

| Scenario | Layout |
|---|---|
| Library published to PyPI | Src layout |
| Internal service used by other packages | Src layout |
| Web app or CLI tool (not distributed) | Flat layout |
| Quick prototype | Flat layout |
| Monorepo with multiple packages | Src layout |

**Full real-world src layout:**

```
payment_service/
├── src/
│   └── payment_service/
│       ├── __init__.py          # ← package marker + version
│       ├── main.py              # ← app entry point
│       ├── config.py            # ← pydantic Settings
│       ├── models/              # ← data structures (no business logic)
│       ├── services/            # ← business logic
│       ├── repositories/        # ← database access layer
│       ├── api/                 # ← HTTP layer: routes, schemas
│       └── utils/               # ← shared helpers
├── tests/
│   ├── conftest.py              # ← shared pytest fixtures
│   ├── unit/
│   └── integration/
├── migrations/                  # ← Alembic DB migrations
├── scripts/                     # ← one-off utility scripts
├── .env.example                 # ← template — always commit
├── .env                         # ← real secrets — NEVER commit
├── .pre-commit-config.yaml
├── pyproject.toml
├── Dockerfile
└── README.md
```

---

## 2. pyproject.toml

`pyproject.toml` is the modern replacement for `setup.py`. It is the single file that defines your package metadata, dependencies, and tool configuration. Every modern Python tool reads it.

**Minimal pyproject.toml (setuptools backend):**

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "my_package"
version = "0.1.0"
description = "A production-ready service"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110",
    "pydantic-settings>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "black>=24.0",
    "ruff>=0.4",
    "mypy>=1.10",
]
```

**Tool configuration in the same file:**

```toml
[tool.black]
line-length = 88
target-version = ["py311"]

[tool.ruff]
line-length = 88
select = ["E", "F", "I"]

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
```

Before `pyproject.toml`, you needed `setup.py`, `setup.cfg`, `tox.ini`, `.flake8`, and `.mypy.ini` as separate files. Now one file handles everything.

---

## 3. `__init__.py`

`__init__.py` marks a directory as a Python package. Without it, Python does not treat the directory as importable.

**What to put in `__init__.py`:**

```python
# src/my_package/__init__.py

__version__ = "1.2.0"          # ← expose version for introspection

# Re-export public API so users write:
# from my_package import create_app
# instead of:
# from my_package.main import create_app
from .main import create_app
from .config import settings

__all__ = ["create_app", "settings"]  # ← declares public API
```

**What NOT to put in `__init__.py`:**
- Heavy imports that slow startup (keep it minimal)
- Business logic (it belongs in modules)
- Side effects (don't run code just from importing)

**Subpackage `__init__.py` files** can be empty — they just mark the directory as a package.

---

## 4. Entry Points

**Entry points** are how Python packages expose command-line tools. When you install a package with `pip install`, entry points become runnable commands on your `PATH`.

**In pyproject.toml:**

```toml
[project.scripts]
my-tool = "my_package.cli:main"   # ← "my-tool" runs my_package/cli.py main()
```

**The `cli.py` module:**

```python
# src/my_package/cli.py
import argparse

def main() -> None:
    parser = argparse.ArgumentParser(description="My tool")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    # ... do work

if __name__ == "__main__":
    main()
```

After `pip install my_package`, users run `my-tool` directly from the command line — no `python -m` needed.

---

## 5. Building and Publishing

**The two distribution formats:**
- **sdist** (source distribution): tarball of your source code — `.tar.gz`
- **wheel**: pre-built binary — `.whl` — installs faster, no build step needed

Build both with `build`:

```bash
pip install build
python -m build                   # ← creates dist/ with .tar.gz and .whl
```

**Publish to TestPyPI first** (always test before the real thing):

```bash
pip install twine
twine upload --repository testpypi dist/*
```

Then install from TestPyPI to verify it works:

```bash
pip install --index-url https://test.pypi.org/simple/ my_package
```

**Publish to the real PyPI:**

```bash
twine upload dist/*
```

You need a PyPI account and an API token. Set `TWINE_USERNAME=__token__` and `TWINE_PASSWORD=pypi-...` as environment variables.

---

## 6. Makefile / invoke — Task Automation

A **Makefile** gives your project a standard set of one-word commands for common tasks. New engineers do not need to memorize long commands.

```makefile
.PHONY: install test lint format build clean

install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

lint:
	ruff check src/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

build:
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info .pytest_cache __pycache__
```

Usage:

```bash
make install        # install project in editable mode with dev deps
make test           # run tests
make lint           # check types and style
make format         # auto-format everything
```

---

## 7. Common Mistakes

**Using `setup.py` for new projects:** `pyproject.toml` is the modern standard (PEP 517/518). New projects should not use `setup.py`.

**Importing too much in `__init__.py`:** Heavy top-level imports slow down every `import my_package` call. Keep `__init__.py` minimal.

**Not using editable installs for development:**

```bash
# Wrong: run from source without installing
python src/my_package/main.py

# Right: install editable first, then import normally
pip install -e .
python -c "from my_package import create_app"
```

**Forgetting `py.typed` for typed packages:** If you want mypy to respect your type hints when your package is used as a library, add an empty `py.typed` file in your package root and declare it in `pyproject.toml`:

```toml
[tool.setuptools.package-data]
my_package = ["py.typed"]
```

**Mixing dev and prod dependencies in `dependencies`:** Runtime deps go in `[project.dependencies]`. Dev tools (pytest, black) go in `[project.optional-dependencies.dev]`.

---

## Navigation

| | |
|---|---|
| ⬆️ Root Theory | [../theory.md](../theory.md) |
| 💻 Practice | [practice.md](./practice.md) |
| 📏 Coding Standards | [../01_coding_standards/theory.md](../01_coding_standards/theory.md) |
| 🌿 Environment | [../03_environment_management/theory.md](../03_environment_management/theory.md) |
