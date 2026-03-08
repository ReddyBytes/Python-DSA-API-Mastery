# ⚡ Modules & Packages — Cheatsheet

> Quick reference: imports, packages, sys.path, __init__.py, project structure.

---

## 📌 All Import Styles

```python
import math                      # access via math.sqrt()
from math import sqrt, pi        # direct access: sqrt()
import numpy as np               # alias: np.array()
from datetime import datetime as dt  # rename: dt.now()
from module import *             # ⚠️ avoid — namespace pollution
```

---

## 🔍 Import Machinery — What Happens

```
import X:
  1. Check sys.modules["X"]  → return cached (done)
  2. Search sys.path in order → find X.py
  3. Compile to bytecode (__pycache__/X.cpython-3xx.pyc)
  4. Execute module top-level code ONCE
  5. Store in sys.modules["X"]
  6. Bind name X in current namespace
```

---

## 🗺️ sys.path — Search Order

```python
import sys
sys.path
# ['',                                    ← current working directory
#  '/usr/lib/python311.zip',
#  '/usr/lib/python3.11',                 ← standard library
#  '/usr/lib/python3.11/lib-dynload',
#  '/path/to/venv/lib/python3.11/site-packages']  ← pip packages

# Modify at runtime (use sparingly):
sys.path.insert(0, "/custom/path")    # highest priority
sys.path.append("/custom/path")       # lowest priority

# Better: install your project properly:
# pip install -e .   ← editable install, permanent entry in site-packages
```

---

## 📦 Package Structure

```
myapp/
├── __init__.py          ← runs on import, defines public API
├── config.py
├── models/
│   ├── __init__.py      ← re-exports User, Product
│   ├── user.py
│   └── product.py
├── services/
│   ├── __init__.py
│   └── user_service.py
└── utils/
    ├── __init__.py
    └── validators.py
```

---

## 🔑 `__init__.py` — Public API Control

```python
# myapp/models/__init__.py

from .user    import User       # re-export from submodule
from .product import Product

__all__ = ["User", "Product"]   # controls from models import *

# Now users write:
from myapp.models import User   # ✓ clean
# Not:
from myapp.models.user import User  # leaks internal structure
```

---

## 🔄 Absolute vs Relative Imports

```python
# Absolute (preferred — unambiguous, works anywhere):
from myapp.models.user import User
from myapp.services    import PaymentService

# Relative (inside packages only):
from .         import utils          # current package
from .models   import User           # same package, different module
from ..models  import User           # parent package
from ...shared import something      # grandparent package

# . = current package
# .. = parent package
# ... = grandparent package
```

---

## 🔒 `__all__` — Export Control

```python
# In a module:
__all__ = ["PublicClass", "public_function"]
# Names NOT in __all__ are still importable explicitly — just "private by convention"
# Controls what from module import * exports

# Common pattern — re-export in __init__.py:
from .module import SomeClass
__all__ = ["SomeClass"]
```

---

## 🎭 `__name__` Guard

```python
def main():
    print("Running!")

if __name__ == "__main__":
    main()    # runs only with: python script.py
              # NOT when: import script
```

---

## 🔴 Circular Imports — Cause & Fixes

```python
# CAUSE: a.py imports b.py; b.py imports a.py → a is partially loaded when b tries to use it

# FIX 1 — Extract shared logic to third module (best):
# shared.py → both a.py and b.py import from shared.py

# FIX 2 — Defer import inside function:
def use_b():
    from b import something   # imports when called, not at load time
    return something()

# FIX 3 — Import module instead of name:
import b
def use_b(): return b.something()
```

---

## 😴 Lazy Imports

```python
# Heavy module — import only when needed:
def process(data):
    import numpy as np       # only imported when process() is called
    return np.array(data)

# When to use:
# ✓ Optional features / heavy deps (numpy, tensorflow)
# ✓ CLI tools where startup time matters
# ✗ Modules used on every call — overhead adds up
```

---

## 🔬 Dynamic Imports

```python
import importlib

# Import module by name string:
mod = importlib.import_module("json")
mod.dumps({"key": "val"})

# Import from package by string:
User = getattr(importlib.import_module("myapp.models.user"), "User")

# Reload (dev only):
importlib.reload(mod)

# Use case: plugin systems, framework extensibility
```

---

## 🌐 Virtual Environments

```bash
# Create:
python -m venv venv

# Activate (macOS/Linux):
source venv/bin/activate

# Activate (Windows):
venv\Scripts\activate

# Install:
pip install requests django

# Freeze:
pip freeze > requirements.txt

# Restore:
pip install -r requirements.txt

# Deactivate:
deactivate
```

---

## 🌍 Namespace Packages (Python 3.3+)

```python
# Directory WITHOUT __init__.py → namespace package
# Can span multiple directories / repos
# Python merges them into one namespace

# repo1/mycompany/auth/
# repo2/mycompany/billing/   ← no __init__.py in mycompany/
# Both on sys.path → from mycompany.auth import ...  ✓
#                    from mycompany.billing import ...  ✓
```

---

## 🔴 Gotchas

```python
# 1 — Modules run only once:
import mymod
mymod.x = 99
import mymod        # returns cache — mymod.x is still 99!

# 2 — from X import name creates a local binding copy:
from config import DEBUG   # DEBUG = local copy of config.DEBUG
config.DEBUG = True        # changes config module
print(DEBUG)               # still False! local copy didn't update
print(config.DEBUG)        # True — module attribute updated

# 3 — Relative imports only inside packages:
from . import utils   # ← ImportError if run as script directly
                      # use: python -m package.module

# 4 — Name shadowing stdlib:
# Don't create files named: json.py, os.py, datetime.py, math.py, string.py
# They shadow stdlib modules with the same name!

# 5 — Circular import symptom:
# ImportError: cannot import name 'X' from partially initialized module 'Y'
# → Fix: extract shared code, defer imports, or restructure
```

---

## 🏠 Production Project Structure

```
src/
└── myapp/
    ├── __init__.py
    ├── config.py
    ├── exceptions.py          ← domain exceptions
    ├── models/                ← data shapes
    ├── repositories/          ← data access
    ├── services/              ← business logic
    ├── api/                   ← HTTP handlers
    └── utils/                 ← shared helpers (no upward imports)

Layer rule: api → services → repositories → models → utils
           (arrows = "imports from")
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| ➡️ Next | [08 — File Handling](../08_file_handling/theory.md) |
