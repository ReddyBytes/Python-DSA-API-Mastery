# Coding Standards — Practice

---

**[⬆️ Root Practice](../practice.md)** · **[📖 Theory](./theory.md)**

---

### Q1 · PEP 8 — Fix PEP 8 Violations 🟢

The snippet below has at least 5 PEP 8 violations. Find and fix them all.

```python
import sys,os
def ProcessPayment(Amount,currency):
    x=Amount*1.1
    if x==None:
        return False
    return x
```

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

<details><summary>💡 Hint</summary>Check import style, function name, parameter names, spacing, and None comparison.</details>
<details><summary>✅ Answer</summary>

```python
import os
import sys


def process_payment(amount: float, currency: str) -> float | bool:
    x = amount * 1.1
    if x is None:    # ← use `is` not `==` for None comparison
        return False
    return x
```
**Why:** Each import on its own line; snake_case for functions/params; spaces around operators; `is None` not `== None`; two blank lines before top-level def.
</details>

---

### Q2 · Type Hints — Annotate a Function Signature 🟢

Add type hints to all parameters and the return value.

```python
def get_users(page, page_size, active_only):
    # returns a list of user dicts
    ...
```

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

<details><summary>💡 Hint</summary>page and page_size are integers, active_only is bool, return is list of dicts.</details>
<details><summary>✅ Answer</summary>

```python
def get_users(
    page: int,
    page_size: int,
    active_only: bool = False,
) -> list[dict[str, object]]:
    ...
```
**Why:** Each parameter on its own line when there are many; trailing comma after last param; `list[dict[...]]` is the modern syntax (Python 3.9+).
</details>

---

### Q3 · Docstrings — Write a Google-Style Docstring 🟡

Write a complete Google-style docstring for this function.

```python
def transfer_funds(from_account: str, to_account: str, amount: float) -> dict:
    # Transfers amount from from_account to to_account.
    # Raises ValueError if amount <= 0 or accounts are the same.
    # Returns dict with transaction_id and timestamp.
    ...
```

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

<details><summary>💡 Hint</summary>Google-style: one-line summary, blank line, Args section, Returns section, Raises section.</details>
<details><summary>✅ Answer</summary>

```python
def transfer_funds(from_account: str, to_account: str, amount: float) -> dict:
    """Transfer funds between two accounts.

    Args:
        from_account: Account ID to debit. Must be an active account.
        to_account: Account ID to credit. Must differ from from_account.
        amount: Amount to transfer. Must be > 0.

    Returns:
        dict with keys: transaction_id (str), timestamp (str ISO 8601).

    Raises:
        ValueError: If amount <= 0 or from_account == to_account.
        AccountNotFoundError: If either account does not exist.
    """
    ...
```
**Why:** One-sentence summary; blank line before sections; Args/Returns/Raises each describe type + meaning.
</details>

---

### Q4 · Formatters — Configure black + isort in pyproject.toml 🟡

Write the `[tool.black]` and `[tool.isort]` sections for a Python 3.11 project with 88-character line length.

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

<details><summary>💡 Hint</summary>isort profile = "black" makes the two tools agree on import formatting.</details>
<details><summary>✅ Answer</summary>

```toml
[tool.black]
line-length = 88
target-version = ["py311"]

[tool.isort]
profile = "black"
line_length = 88
```
**Why:** `profile = "black"` tells isort to format imports in a way black will never reformat — prevents the two tools fighting each other.
</details>

---

### Q5 · Linters — Identify and Fix Flake8/Ruff Violations 🟡

What violations does this code have? List them and show the fix.

```python
import json
import os
import requests

def fetch(url,timeout=30):
    resp = requests.get(url,timeout=timeout)
    data = json.loads(resp.text)
    unused = "hello"
    return data
```

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

<details><summary>💡 Hint</summary>Look for: unused imports, missing spaces after commas, unused variables.</details>
<details><summary>✅ Answer</summary>

```python
import json

import requests


def fetch(url: str, timeout: int = 30) -> dict:
    resp = requests.get(url, timeout=timeout)
    data = json.loads(resp.text)
    return data
```
**Why:** `import os` was unused (F401); `unused` variable was F841; missing spaces after commas in function call and signature (E231); added type hints as a bonus.
</details>

---

### Q6 · Pre-commit — Write a Pre-commit Config 🟡

Write a `.pre-commit-config.yaml` that runs black, ruff (with auto-fix), and checks for accidentally committed private keys.

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

<details><summary>💡 Hint</summary>Use pre-commit-hooks repo for detect-private-key; ruff-pre-commit for ruff.</details>
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

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: detect-private-key
      - id: trailing-whitespace
      - id: end-of-file-fixer
```
**Why:** `detect-private-key` blocks commits containing PEM keys or other common secret patterns; `--fix` on ruff auto-resolves fixable lint errors.
</details>

---

### Q7 · Naming — Fix camelCase Violations 🟡

Rename all identifiers to follow Python conventions.

```python
class userService:
    def __init__(self, dbConnection, maxRetries=3):
        self.dbConnection = dbConnection
        self.maxRetries = maxRetries

    def getUserById(self, userId):
        ...

    def createNewUser(self, userData):
        ...
```

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

<details><summary>💡 Hint</summary>Classes → PascalCase; methods/variables → snake_case; constructor params → snake_case.</details>
<details><summary>✅ Answer</summary>

```python
class UserService:
    def __init__(self, db_connection, max_retries: int = 3):
        self.db_connection = db_connection
        self.max_retries = max_retries

    def get_user_by_id(self, user_id: int) -> dict:
        ...

    def create_new_user(self, user_data: dict) -> dict:
        ...
```
**Why:** Class name → `PascalCase`; all methods and variables → `snake_case`; bonus: added type hints.
</details>

---

### Q8 · mypy — Enable Strict Mode and Fix Errors 🟡

Given this function, write the mypy config and show what errors mypy strict mode would flag.

```python
def process(items, multiplier):
    result = []
    for item in items:
        result.append(item * multiplier)
    return result
```

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

<details><summary>💡 Hint</summary>Strict mode flags: missing annotations, implicit Any types.</details>
<details><summary>✅ Answer</summary>

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true
```

```python
# Fixed: all arguments and return type annotated
def process(items: list[float], multiplier: float) -> list[float]:
    result: list[float] = []
    for item in items:
        result.append(item * multiplier)
    return result
```
**Why:** mypy strict flags `error: Function is missing a type annotation` (missing-return-type) and `error: Argument of type has incompatible type "Any"` for unannotated parameters.
</details>

---

### Q9 · Ruff — Set Up Custom Rule Selection 🟠

Write a ruff configuration that enables: pycodestyle errors (E), pyflakes (F), import sorting (I), pyupgrade (UP), and flake8-bugbear (B). Ignore E501 (line too long, since black handles it).

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

<details><summary>💡 Hint</summary>Ruff uses `select` for enabled rules and `ignore` for disabled ones.</details>
<details><summary>✅ Answer</summary>

```toml
[tool.ruff]
line-length = 88
target-version = "py311"
select = [
    "E",    # pycodestyle errors
    "F",    # pyflakes
    "I",    # isort
    "UP",   # pyupgrade (modernize syntax)
    "B",    # flake8-bugbear (common bugs)
]
ignore = [
    "E501", # line too long — black handles this
]

[tool.ruff.per-file-ignores]
"tests/*" = ["S101"]  # allow assert in tests
```
**Why:** `B` (bugbear) catches common bugs like mutable default arguments and `assert` in non-test code; `UP` automatically upgrades old-style syntax like `List[str]` → `list[str]`.
</details>

---

### Q10 · Capstone — Apply Full Standards to a Module 🟠

The module below has multiple violations across PEP 8, type hints, docstrings, and lint. Apply all standards: fix naming, add type hints, write docstrings, fix lint violations.

```python
import json,os,sys
from datetime import datetime

class payment_processor:
    def __init__(self,apiKey,baseUrl):
        self.apiKey=apiKey
        self.baseUrl=baseUrl
        self.requestCount=0

    def makePayment(self,Amount,userId,currency="USD"):
        self.requestCount=self.requestCount+1
        payload={"amount":Amount,"user":userId,"currency":currency}
        result={"id":"txn-123","status":"ok","ts":datetime.now().isoformat()}
        return result

    def getStats(self):
        return {"total_requests":self.requestCount}
```

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

<details><summary>💡 Hint</summary>Fix: class name (PascalCase), method names (snake_case), spacing, unused imports, type hints, docstrings.</details>
<details><summary>✅ Answer</summary>

```python
import os
from datetime import datetime


class PaymentProcessor:
    """Processes payments via the payment gateway API."""

    def __init__(self, api_key: str, base_url: str) -> None:
        """Initialize the processor.

        Args:
            api_key: API key for the payment gateway.
            base_url: Base URL of the payment gateway.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.request_count = 0

    def make_payment(
        self,
        amount: float,
        user_id: int,
        currency: str = "USD",
    ) -> dict[str, str]:
        """Process a single payment.

        Args:
            amount: Payment amount. Must be > 0.
            user_id: ID of the user making the payment.
            currency: ISO 4217 currency code. Defaults to USD.

        Returns:
            dict with keys: id, status, ts.
        """
        self.request_count += 1
        return {
            "id": "txn-123",
            "status": "ok",
            "ts": datetime.now().isoformat(),
        }

    def get_stats(self) -> dict[str, int]:
        """Return processor statistics."""
        return {"total_requests": self.request_count}
```
**Why:** PascalCase class, snake_case methods, spaces around `=`, type hints everywhere, proper docstrings, removed unused `json/sys` imports, `+= 1` instead of `= x + 1`.
</details>

---

## Navigation

| | |
|---|---|
| ⬆️ Root Practice | [../practice.md](../practice.md) |
| 📖 Theory | [theory.md](./theory.md) |
| 💻 Solve Locally | [practice_local.py](./practice_local.py) |
| 🏗️ Project Structure | [../02_project_structure_packaging/practice.md](../02_project_structure_packaging/practice.md) |
