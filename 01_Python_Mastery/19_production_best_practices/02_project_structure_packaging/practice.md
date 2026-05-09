# Project Structure & Packaging — Practice

---

**[⬆️ Root Practice](../practice.md)** · **[📖 Theory](./theory.md)**

---


## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| [Q1](#q1) | Layout — Draw a Standard src/ Project Layout | 🟢 |
| [Q2](#q2) | pyproject.toml — Write a Minimal Package Config | 🟢 |
| [Q3](#q3) | `__init__.py` — Write the Public API | 🟡 |
| [Q4](#q4) | Entry Points — Add a CLI Console Script | 🟡 |
| [Q5](#q5) | Makefile — Write a Makefile with Standard Targets | 🟡 |
| [Q6](#q6) | Editable Install — Explain pip install -e . | 🟡 |
| [Q7](#q7) | Metadata — Add README and License to pyproject.toml | 🟡 |
| [Q8](#q8) | Publishing — Build and Publish to TestPyPI | 🟠 |
| [Q9](#q9) | Optional Dependencies — Multi-environment Deps | 🟠 |
| [Q10](#q10) | Capstone — Scaffold a Complete Project | 🟠 |

---

<a id="q1"></a>

### Q1 · Layout — Draw a Standard src/ Project Layout 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


Draw the complete directory tree for a Python library called `payment_sdk` using src layout. Include: source package, tests (unit + integration), pyproject.toml, .env.example, Dockerfile, and README.


<details><summary>💡 Hint</summary>src/ contains the package; tests/ sits at root level alongside pyproject.toml.</details>
<details><summary>✅ Answer</summary>

```
payment_sdk/
├── src/
│   └── payment_sdk/
│       ├── __init__.py
│       ├── client.py
│       ├── models.py
│       └── exceptions.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   └── test_client.py
│   └── integration/
│       └── test_api.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── Dockerfile
└── README.md
```
**Why:** `src/` prevents accidental imports of raw source; `tests/` at root keeps test code separate from package code; `conftest.py` holds shared fixtures.
</details>

---

<a id="q2"></a>

### Q2 · pyproject.toml — Write a Minimal Package Config 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


Write a complete `pyproject.toml` for a package named `payment_sdk` version `0.2.0` that requires Python 3.11+, depends on `httpx>=0.27` and `pydantic>=2.0`, and uses setuptools as the build backend.


<details><summary>💡 Hint</summary>You need [build-system], [project], and the requires-python field.</details>
<details><summary>✅ Answer</summary>

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "payment_sdk"
version = "0.2.0"
description = "Python SDK for the Payment Gateway API"
requires-python = ">=3.11"
dependencies = [
    "httpx>=0.27",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "black>=24.0",
    "ruff>=0.4",
]
```
**Why:** `build-system` is required for any buildable package; `requires-python` prevents installation on incompatible versions; dev deps in `optional-dependencies` so production installs stay lean.
</details>

---

<a id="q3"></a>

### Q3 · `__init__.py` — Write the Public API 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


Write the `__init__.py` for `payment_sdk` that: exposes `__version__ = "0.2.0"`, re-exports `PaymentClient` from `.client`, re-exports `PaymentError` from `.exceptions`, and declares `__all__`.


<details><summary>💡 Hint</summary>Use relative imports; __all__ is a list of strings.</details>
<details><summary>✅ Answer</summary>

```python
# src/payment_sdk/__init__.py

__version__ = "0.2.0"

from .client import PaymentClient
from .exceptions import PaymentError

__all__ = ["PaymentClient", "PaymentError", "__version__"]
```
**Why:** Re-exporting in `__init__.py` means users write `from payment_sdk import PaymentClient` instead of `from payment_sdk.client import PaymentClient`. `__all__` declares what `from payment_sdk import *` would expose.
</details>

---

<a id="q4"></a>

### Q4 · Entry Points — Add a CLI Console Script 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


Add a `payment-cli` command to `pyproject.toml` that runs the `main()` function from `payment_sdk.cli`. Show the function signature.


<details><summary>💡 Hint</summary>Entry points live under [project.scripts].</details>
<details><summary>✅ Answer</summary>

```toml
# in pyproject.toml
[project.scripts]
payment-cli = "payment_sdk.cli:main"
```

```python
# src/payment_sdk/cli.py
import argparse


def main() -> None:
    """Entry point for the payment-cli command."""
    parser = argparse.ArgumentParser(description="Payment SDK CLI")
    parser.add_argument("--version", action="version", version="0.2.0")
    parser.add_argument("--env", choices=["dev", "staging", "prod"], default="dev")
    args = parser.parse_args()
    print(f"Running in {args.env}")
```
**Why:** After `pip install payment_sdk`, running `payment-cli` executes `main()`. No `python -m` required.
</details>

---

<a id="q5"></a>

### Q5 · Makefile — Write a Makefile with Standard Targets 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Write a Makefile with targets: `install`, `test`, `lint`, `format`, `build`, `clean`.


<details><summary>💡 Hint</summary>Use .PHONY to mark targets that don't produce files.</details>
<details><summary>✅ Answer</summary>

```makefile
.PHONY: install test lint format build clean

install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --tb=short

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
	find . -name "*.pyc" -delete
```
**Why:** `.PHONY` prevents make from treating targets as filenames; `pip install -e ".[dev]"` installs the package in editable mode with dev extras.
</details>

---

<a id="q6"></a>

### Q6 · Editable Install — Explain pip install -e . 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


Explain what `pip install -e .` does, why it is used during development, and what problem it solves compared to running scripts directly from source.


<details><summary>💡 Hint</summary>Think about sys.path and the difference between testing installed code vs. raw source.</details>
<details><summary>✅ Answer</summary>

```bash
pip install -e .
# -e = editable mode
# .  = pyproject.toml in current directory
```

`pip install -e .` installs your package in "editable" mode — Python sees the package as installed, but any changes you make to the source files are immediately reflected without reinstalling.

Without it (flat layout): running `pytest` adds the project root to `sys.path`, so `import my_package` finds the raw source directory. This hides packaging problems — your tests might pass but the installed wheel might not import correctly.

With editable install (src layout): `import my_package` always resolves to the installed package. Your test environment mirrors the user's environment exactly.

**Why:** Editable installs are the standard workflow for developing libraries. They combine the convenience of live-reload with the correctness of installed packages.
</details>

---

<a id="q7"></a>

### Q7 · Metadata — Add README and License to pyproject.toml 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


Extend the `[project]` section to include: a README (Markdown), MIT license, author name and email, and PyPI classifiers for Python 3.11 and the MIT license.


<details><summary>💡 Hint</summary>readme field accepts a filename; license field has a text key; classifiers is a list of strings.</details>
<details><summary>✅ Answer</summary>

```toml
[project]
name = "payment_sdk"
version = "0.2.0"
description = "Python SDK for the Payment Gateway API"
readme = "README.md"
license = { text = "MIT" }
authors = [
    { name = "Alice Smith", email = "alice@example.com" },
]
requires-python = ">=3.11"
dependencies = ["httpx>=0.27", "pydantic>=2.0"]
classifiers = [
    "Programming Language :: Python :: 3.11",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
```
**Why:** Classifiers are used by PyPI to categorize and filter packages; `readme = "README.md"` causes the README to appear on the PyPI package page.
</details>

---

<a id="q8"></a>

### Q8 · Publishing — Build and Publish to TestPyPI 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


List all the commands to: install build tools, build the package, verify the wheel, and upload to TestPyPI. What should you verify after upload?


<details><summary>💡 Hint</summary>Tools needed: build, twine. Always test on TestPyPI before real PyPI.</details>
<details><summary>✅ Answer</summary>

```bash
# 1. Install build tools
pip install build twine

# 2. Build sdist and wheel
python -m build
# → creates dist/payment_sdk-0.2.0.tar.gz
# → creates dist/payment_sdk-0.2.0-py3-none-any.whl

# 3. Check the distribution before uploading
twine check dist/*

# 4. Upload to TestPyPI
twine upload --repository testpypi dist/*
# Uses TWINE_USERNAME=__token__ and TWINE_PASSWORD=pypi-testtoken...

# 5. Verify: install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ payment_sdk
python -c "import payment_sdk; print(payment_sdk.__version__)"
```
**Why:** `twine check` catches metadata problems before upload; TestPyPI is a sandbox — mistakes there don't affect real users.
</details>

---

<a id="q9"></a>

### Q9 · Optional Dependencies — Multi-environment Deps 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


Write a `pyproject.toml` with optional dependency groups: `dev` (pytest, black, ruff, mypy), `docs` (mkdocs, mkdocs-material), and `all` that installs both. Show how to install each group.


<details><summary>💡 Hint</summary>Groups can reference other groups using the package name with extras syntax.</details>
<details><summary>✅ Answer</summary>

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "black>=24.0",
    "ruff>=0.4",
    "mypy>=1.10",
]
docs = [
    "mkdocs>=1.5",
    "mkdocs-material>=9.0",
]
all = [
    "payment_sdk[dev]",
    "payment_sdk[docs]",
]
```

```bash
pip install -e ".[dev]"       # install with dev extras
pip install -e ".[docs]"      # install with docs extras
pip install -e ".[all]"       # install everything
pip install -e ".[dev,docs]"  # alternative: comma-separated
```
**Why:** Optional deps let you keep the base installation lean. CI installs `[dev]`; the docs server installs `[docs]`; production installs nothing extra.
</details>

---

<a id="q10"></a>

### Q10 · Capstone — Scaffold a Complete Project 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


Describe all the commands and files needed to scaffold a new Python library `data_validator` from scratch: project structure, pyproject.toml, __init__.py with version, a CLI entry point, Makefile, and pre-commit config.


<details><summary>💡 Hint</summary>Think: mkdir, pyproject.toml, __init__.py, cli.py, .pre-commit-config.yaml, Makefile, pre-commit install.</details>
<details><summary>✅ Answer</summary>

```bash
# 1. Create directories
mkdir -p data_validator/src/data_validator
mkdir -p data_validator/tests/{unit,integration}

# 2. Create package files
touch data_validator/src/data_validator/__init__.py
touch data_validator/src/data_validator/validator.py
touch data_validator/src/data_validator/cli.py
touch data_validator/tests/conftest.py
touch data_validator/.env.example
touch data_validator/.gitignore
touch data_validator/Dockerfile
touch data_validator/README.md
```

`pyproject.toml` with entry point:

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "data_validator"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[project.scripts]
data-validate = "data_validator.cli:main"

[project.optional-dependencies]
dev = ["pytest>=8.0", "black>=24.0", "ruff>=0.4"]
```

```bash
# 3. Install in editable mode
cd data_validator
pip install -e ".[dev]"

# 4. Set up pre-commit
pip install pre-commit
pre-commit install

# 5. Verify CLI works
data-validate --help
```
**Why:** This workflow — mkdir, pyproject.toml, editable install, pre-commit — is the standard starting point for any new Python library.
</details>

---

## Navigation

| | |
|---|---|
| ⬆️ Root Practice | [../practice.md](../practice.md) |
| 📖 Theory | [theory.md](./theory.md) |
| 💻 Solve Locally | [practice_local.py](./practice_local.py) |
| 📏 Coding Standards | [../01_coding_standards/practice.md](../01_coding_standards/practice.md) |
| 🌿 Environment | [../03_environment_management/practice.md](../03_environment_management/practice.md) |
