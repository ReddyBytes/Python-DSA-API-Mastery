# Coding Standards — Theory

---

**[🏠 Back to README](../../README.md)** · **[⬆️ Root Theory](../theory.md)**

---

## Learning Priority

**Must Learn**: PEP 8 basics, type hints, black formatter, isort
**Should Learn**: flake8/pylint, pre-commit hooks, docstring formats
**Good to Know**: mypy strict mode, bandit (security linting), vulture
**Reference**: pyproject.toml lint config, ruff all-in-one linter

---

## 1. PEP 8 Essentials

Think of PEP 8 like a house style guide for writing — everyone agrees on one style so the codebase reads like one person wrote it, even when 20 engineers touch it every day.

**PEP 8** is Python's official style guide. These are the rules you must know cold.

**Naming rules:**

```python
# Variables and functions → snake_case
user_name = "alice"
def process_payment(amount: float) -> bool: ...

# Classes → PascalCase
class PaymentService: ...

# Constants → UPPER_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30.0

# Private members → leading underscore
_internal_counter = 0
```

**Spacing rules:**

```python
# Two blank lines between top-level definitions
class ServiceA:
    pass


class ServiceB:            # ← two blank lines above
    def method_one(self):
        pass

    def method_two(self):  # ← one blank line between methods
        pass
```

**Import order (3 groups, blank line between each):**

```python
import os                  # ← group 1: stdlib
import sys

import requests            # ← group 2: third-party
from fastapi import FastAPI

from my_package import config  # ← group 3: local
```

**Line length:** Black defaults to 88 characters. PEP 8 says 79. Pick one and stick to it.

---

## 2. Type Hints in Practice

Type hints are like labels on boxes in a warehouse — you know what is inside without opening it. They do not change runtime behavior, but they let tools catch bugs before code runs.

**Basic annotations:**

```python
def greet(name: str, times: int = 1) -> str:
    return f"Hello, {name}! " * times

def get_user(user_id: int) -> dict[str, str] | None:
    ...                    # ← dict[str, str] or None
```

**Common patterns:**

```python
from typing import Optional, Union

# Optional[X] is shorthand for X | None
def find_item(item_id: int) -> Optional[str]:
    ...

# Union when multiple types are valid
def parse_id(value: Union[str, int]) -> int:
    return int(value)
```

**When to add type hints:**
- All public function signatures — always
- Class attributes — always
- Private helpers — when non-obvious
- Simple one-liners — optional

---

## 3. Docstrings

A docstring is the first string literal inside a function, class, or module. It becomes the `.__doc__` attribute and shows up in `help()`.

**Always include:**
- What the function does (one sentence)
- Args: name, type, description
- Returns: type and meaning
- Raises: which exceptions and when

**Google style (recommended for most teams):**

```python
def process_payment(amount: float, currency: str) -> dict:
    """Process a payment and return a transaction record.

    Args:
        amount: Payment amount in the given currency. Must be > 0.
        currency: ISO 4217 currency code (e.g., "USD", "EUR").

    Returns:
        dict with keys: transaction_id, status, timestamp.

    Raises:
        ValueError: If amount is <= 0.
        PaymentError: If the payment gateway rejects the transaction.
    """
    ...
```

**NumPy style (common in data science):**

```python
def normalize(arr, axis=0):
    """
    Normalize array values to zero mean, unit variance.

    Parameters
    ----------
    arr : np.ndarray
        Input array to normalize.
    axis : int, optional
        Axis along which to normalize. Default is 0.

    Returns
    -------
    np.ndarray
        Normalized array with same shape as input.
    """
    ...
```

Pick one style per project — never mix.

---

## 4. Code Formatters

**Black** is the auto-formatter that ends all debates. It reformats your code to one consistent style with zero configuration needed. You just run it.

```bash
black src/ tests/          # format all Python files in place
black --check src/         # CI mode: exit 1 if any file would change
```

**isort** sorts and groups your imports automatically:

```bash
isort src/ tests/
```

**Configure both in pyproject.toml** so they agree on line length:

```toml
[tool.black]
line-length = 88
target-version = ["py311"]

[tool.isort]
profile = "black"          # ← isort follows black's import style
line_length = 88
```

The `profile = "black"` setting makes isort format imports in a way that black will never reformat.

---

## 5. Linters

Linters read your code without running it and flag problems: unused variables, undefined names, wrong argument counts. Think of them as a second pair of eyes.

**Ruff** is the modern choice — it replaces flake8, isort, and more, written in Rust so it's 100x faster:

```bash
ruff check src/            # lint and report issues
ruff check --fix src/      # auto-fix what it can
```

Configure in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
target-version = "py311"
select = ["E", "F", "I", "UP"]  # ← E=pycodestyle, F=pyflakes, I=isort, UP=pyupgrade
ignore = ["E501"]               # ← ignore line-too-long (black handles it)
```

**mypy** adds static type checking — it verifies your type hints are consistent:

```bash
mypy src/
```

```toml
[tool.mypy]
python_version = "3.11"
strict = true              # ← enables all checks
ignore_missing_imports = true
```

**Common rule codes to know:**
- `E501` — line too long
- `F401` — imported but unused
- `F841` — local variable assigned but never used
- `E711` — comparison to None (use `is` not `==`)

---

## 6. Pre-commit Hooks

Pre-commit hooks run automatically before every `git commit`. They act like a checkpoint: if black needs to reformat a file, the commit is blocked until you fix it. This means formatting problems never enter the repo.

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

Setup once per machine:

```bash
pip install pre-commit
pre-commit install          # ← installs hooks into .git/hooks/
pre-commit run --all-files  # ← run manually on everything (first time)
```

After `pre-commit install`, every `git commit` runs black + ruff + mypy automatically.

---

## 7. Common Mistakes

**camelCase function names:** Python is not Java. `processPayment()` should be `process_payment()`.

**No type hints on public APIs:** Type hints are free documentation and enable tool support. Always annotate public functions.

**Docstrings that only restate the function name:**

```python
# BAD
def get_user(user_id: int) -> dict:
    """Gets the user."""  # ← useless

# GOOD
def get_user(user_id: int) -> dict:
    """Fetch user by ID from the database.

    Args:
        user_id: Primary key of the user record.

    Returns:
        dict with keys: id, name, email, created_at.

    Raises:
        UserNotFoundError: If no user with this ID exists.
    """
```

**Star imports:** `from module import *` pollutes the namespace and makes it impossible to know where names come from.

**Skipping pre-commit in CI:** Pre-commit should also run in your CI pipeline (`pre-commit run --all-files`), not just locally. Local-only enforcement is optional; CI enforcement is mandatory.

---

## Navigation

| | |
|---|---|
| ⬆️ Root Theory | [../theory.md](../theory.md) |
| 💻 Practice | [practice.md](./practice.md) |
| 🏗️ Project Structure | [../02_project_structure_packaging/theory.md](../02_project_structure_packaging/theory.md) |
| 🌿 Environment | [../03_environment_management/theory.md](../03_environment_management/theory.md) |
