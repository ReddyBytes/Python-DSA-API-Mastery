# 📦 07 — Modules & Packages
## From One Giant File to a Scalable Architecture

> *"The moment your codebase outgrows one file, you need to think architecturally.*
> *Modules are not just a way to split files — they're how you design a system."*

---

## 🎬 The Story

Day 1: You start a project. One file. 50 lines. Perfect.

Day 30: 500 lines. Still manageable.

Day 90: 3,000 lines. You need to scroll 10 minutes to find a function.
Five teammates are editing the same file. Git conflicts every hour.
Nobody knows which function does what. Test coverage is zero.

This is the **monolith trap**.

Every real project eventually faces it.
The solution: split code into **modules** and **packages** — each with a clear responsibility.

This chapter teaches you not just the syntax, but the *design thinking* behind it.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`import` statement · `from X import Y` · `__name__ == "__main__"` · Package structure (`__init__.py`) · `sys.modules`

**Should Learn** — Important for real projects, comes up regularly:
Relative imports · `__all__` · `importlib.import_module()` · Circular imports (and how to fix them)

**Good to Know** — Useful in specific situations:
`importlib.reload()` · Lazy imports · `__package__` attribute

**Reference** — Know it exists, look up when needed:
Import hooks · Namespace packages · `importlib.resources`

---

## 🧠 Chapter 1 — What Is a Module, Really?

A module is simultaneously **two things**:

```
1. A .py FILE on disk (source of truth)
2. A MODULE OBJECT in memory (what Python creates when you import it)
```

```python
# math_utils.py  ← file on disk
PI = 3.14159

def circle_area(r):
    return PI * r ** 2

def square_area(s):
    return s ** 2
```

```python
# main.py
import math_utils

print(type(math_utils))          # <class 'module'>
print(math_utils.PI)             # 3.14159
print(math_utils.circle_area(5)) # 78.53...
print(dir(math_utils))           # ['PI', '__builtins__', '__doc__', '__file__',
                                  #  '__loader__', '__name__', '__spec__',
                                  #  'circle_area', 'square_area']
```

> A module is a **namespace** — a container that holds names (variables, functions, classes).
> `math_utils.PI` means: "look up `PI` inside the `math_utils` namespace."

---

## 🔍 Chapter 2 — The Import Machinery (What Really Happens)

When Python sees `import math_utils`, here is the exact sequence (`sys.modules` is Python's [module-level cache](../01.1_memory_management/theory.md#-heap) — a dict on the heap that lives for the entire process):

```
STEP 1: Check sys.modules (the cache)
        ┌─────────────────────────────────────────┐
        │  "math_utils" in sys.modules?           │
        │  YES → return cached module (DONE)      │
        │  NO  → continue to step 2               │
        └─────────────────────────────────────────┘

STEP 2: Find the file — search sys.path in order:
        ┌─────────────────────────────────────────────────────────────────┐
        │  sys.path = [                                                   │
        │    '',                        ← current directory first         │
        │    '/usr/lib/python311.zip',  ← standard library               │
        │    '/usr/lib/python3.11',                                       │
        │    '/usr/lib/python3.11/lib-dynload',                           │
        │    '/home/user/.local/lib/python3.11/site-packages',  ← pip    │
        │    '/usr/lib/python3/dist-packages',                            │
        │  ]                                                              │
        └─────────────────────────────────────────────────────────────────┘

STEP 3: Load & compile
        .py file  → compile to .pyc bytecode (cached in __pycache__/)
        .pyc file → load compiled bytecode directly (faster)

STEP 4: Execute module top-level code
        All top-level statements run ONCE:
        - class definitions
        - function definitions
        - variable assignments
        - import statements in the module

STEP 5: Create module object + store in sys.modules
        sys.modules["math_utils"] = <module 'math_utils' from 'math_utils.py'>

STEP 6: Bind name in current namespace
        math_utils = sys.modules["math_utils"]
```

```python
import sys

import math_utils   # first import: runs all 5 steps
import math_utils   # second import: step 1 returns cache immediately!
                    # module code does NOT run twice

print("math_utils" in sys.modules)   # True
print(sys.modules["math_utils"])      # <module 'math_utils' from '...'>
```

---

## 📌 Chapter 3 — All Import Styles, When to Use Each

### Style 1 — `import module`

```python
import math
import os
import json

# Access everything via the module namespace:
result = math.sqrt(16)
path   = os.path.join("folder", "file.txt")
data   = json.dumps({"key": "value"})
```

**Use when:** you want to be explicit about where things come from. Best for clarity.

---

### Style 2 — `from module import name`

```python
from math import sqrt, pi
from os.path import join, exists
from datetime import datetime, timedelta

# Access directly — no prefix needed:
result = sqrt(16)
path   = join("folder", "file.txt")
now    = datetime.now()
```

**Use when:** you're using specific items frequently and the name won't clash.

---

### Style 3 — `import module as alias`

```python
import numpy as np              # industry standard alias
import pandas as pd             # industry standard alias
import matplotlib.pyplot as plt # industry standard alias

arr = np.array([1, 2, 3])
df  = pd.DataFrame({"a": [1, 2, 3]})
```

**Use when:** the module name is long or has a well-known alias convention.

---

### Style 4 — `from module import name as alias`

```python
from datetime import datetime as dt
from collections import OrderedDict as OD
from typing import Optional as Opt

now: Opt[dt] = dt.now()
```

**Use when:** the name conflicts with something in your scope or is very long.

---

### Style 5 — `from module import *` (⚠️ Usually Avoid)

```python
from math import *    # imports everything in math (or everything in __all__)

sqrt(16)     # works — but WHERE does sqrt come from? Hard to tell!
```

**When it's acceptable:**
- In interactive REPL sessions only
- In `__init__.py` to deliberately re-export a public API
- In test files occasionally

**Why to avoid in production code:**
```python
from os.path import *
from posixpath import *   # both export 'join' — which one did you get?!
                          # namespace pollution + silent shadowing bugs
```

---

## 🏗️ Chapter 4 — Packages: Organizing Modules Into a System

A **package** is a directory that Python treats as a module namespace.

```
myapp/                          ← root package
    __init__.py                 ← makes it a package (optional in Python 3.3+)
    config.py
    models/                     ← sub-package
        __init__.py
        user.py
        product.py
        order.py
    services/                   ← sub-package
        __init__.py
        user_service.py
        payment_service.py
    api/                        ← sub-package
        __init__.py
        routes.py
        middleware.py
    utils/                      ← sub-package
        __init__.py
        validators.py
        formatters.py
    tests/
        test_models.py
        test_services.py
```

```python
# Importing from a package:
from myapp.models.user      import User
from myapp.services.payment import PaymentService
from myapp.utils.validators import validate_email

# Or use the package's public API (if __init__.py exports it):
from myapp.models import User       # if models/__init__.py exports User
```

---

## 🔑 Chapter 5 — `__init__.py`: The Package Controller

`__init__.py` runs when the package is first imported. Its job:

### Job 1 — Define the Public API

```python
# myapp/models/__init__.py

# Import the classes you want users to access directly:
from .user    import User
from .product import Product
from .order   import Order

# Now users can do:
#   from myapp.models import User
# instead of:
#   from myapp.models.user import User
```

### Job 2 — Control Wildcard Imports with `__all__`

```python
# myapp/utils/__init__.py

__all__ = ["validate_email", "format_currency", "slugify"]
# Only these are exported when someone does: from myapp.utils import *
```

### Job 3 — Package Initialization

```python
# myapp/__init__.py

__version__ = "1.2.3"
__author__  = "Your Name"

# Initialize logging for the whole package:
import logging
logging.getLogger("myapp").addHandler(logging.NullHandler())
```

### Empty vs Populated `__init__.py`

```python
# Minimal __init__.py — just marks the directory as a package:
# (file can be empty)

# Rich __init__.py — controls the public API (Django, Flask style):
from .models   import User, Product
from .services import UserService
from .config   import Settings
```

---

## 🔄 Chapter 6 — Absolute vs Relative Imports

### Absolute Imports — The Safe Default

```python
# Full path from the project root:
from myapp.models.user    import User
from myapp.services.auth  import authenticate
from myapp.utils          import validate_email

# ✅ Always clear where things come from
# ✅ Works from anywhere
# ✅ Preferred in large projects
```

### Relative Imports — Inside a Package

```python
# Inside myapp/services/user_service.py:

from .           import utils           # . = current package (services)
from .payment    import process_payment # same package, different module
from ..models    import User            # .. = parent package (myapp)
from ..models.user import User          # same as above, more explicit
from ..utils     import validate_email  # sibling package

# Relative import legend:
# .    = current package
# ..   = parent package
# ...  = grandparent package
```

```
ABSOLUTE vs RELATIVE — when to use:
┌──────────────────────────────────────────────────────────────┐
│  Absolute   Use almost everywhere. Clear, unambiguous.       │
│  Relative   Use within a package for internal references.    │
│             Don't use from scripts — only from inside a pkg  │
└──────────────────────────────────────────────────────────────┘
```

---

## 🧬 Chapter 7 — `__name__` and the `"__main__"` Pattern

This is Python's most important idiom for dual-use files.

```python
# calculator.py

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b


# This block ONLY runs when you execute: python calculator.py
# It does NOT run when someone does: import calculator
if __name__ == "__main__":
    print(add(10, 5))       # 15
    print(subtract(10, 5))  # 5
```

```
HOW IT WORKS:
  When you run: python calculator.py
    → __name__ = "__main__"  → if block RUNS

  When you import: import calculator
    → __name__ = "calculator"  → if block DOES NOT run

WHY IT MATTERS:
  Without this guard:
    import calculator   ← also prints "15" and "5" — unexpected!
    import calculator   ← and again on first import!

  With this guard:
    import calculator   ← clean, no side effects
    calculator.add(3,4) ← use it safely
```

```python
# Real-world usage:
if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("a", type=float)
    parser.add_argument("b", type=float)
    args = parser.parse_args()

    print(f"Result: {add(args.a, args.b)}")
```

---

## ⚠️ Chapter 8 — Circular Imports: The Design Warning

A circular import happens when module A imports module B, and module B (directly or indirectly) imports module A.

### How It Breaks

```
a.py imports b.py
b.py imports a.py

Python tries to import a.py:
  → starts executing a.py
  → sees "import b"
  → starts executing b.py
  → sees "import a"
  → a is already being loaded (in sys.modules, but incomplete!)
  → b gets a PARTIAL/EMPTY module a
  → NameError or AttributeError at import time
```

```python
# a.py
from b import greet_b    # ← starts importing b.py...

def greet_a():
    return "Hello from A"


# b.py
from a import greet_a    # ← a is still being loaded! greet_a may not exist yet
                         # ImportError: cannot import name 'greet_a' from partially initialized 'a'

def greet_b():
    return "Hello from B"
```

### Fix 1 — Extract Shared Code to a Third Module

```python
# shared.py — no imports from a or b
def greet(name):
    return f"Hello from {name}"

# a.py
from shared import greet
def greet_a(): return greet("A")

# b.py
from shared import greet
def greet_b(): return greet("B")
```

### Fix 2 — Move the Import Inside the Function

```python
# a.py
def greet_a():
    return "Hello from A"

def use_b():
    from b import greet_b    # ← import deferred until function is called
    return greet_b()         # ← by then, both modules are fully loaded
```

### Fix 3 — Import the Module, Not the Name

```python
# a.py
import b    # ← importing the module is safer; access b.greet_b() later

def use_b():
    return b.greet_b()   # ← deferred attribute access, works after both load
```

> **Circular imports are a design smell.** They mean your module boundaries are wrong. If A and B need each other, they probably belong in the same module, or their shared logic belongs in a third module.

---

## 🔧 Chapter 9 — `__all__`: Defining the Public API

`__all__` is a list of strings that defines what gets exported when someone does `from module import *`. But it also signals to readers and IDEs what the **public interface** is.

```python
# validators.py

__all__ = ["validate_email", "validate_phone", "validate_age"]
# Everything NOT in __all__ is considered internal/private

def validate_email(email: str) -> bool:
    return "@" in email and "." in email

def validate_phone(phone: str) -> bool:
    return phone.isdigit() and len(phone) == 10

def validate_age(age: int) -> bool:
    return 0 < age < 150

def _normalize_phone(phone: str) -> str:    # ← private helper
    return phone.replace("-", "").replace(" ", "")


# from validators import * → only gets validate_email, validate_phone, validate_age
# _normalize_phone is excluded (starts with _ and not in __all__)
```

---

## 🔬 Chapter 10 — Dynamic Imports with `importlib`

When you need to load a module by name at runtime (plugin systems, frameworks).

```python
import importlib


# Load a module by string name:
module = importlib.import_module("math")
print(module.sqrt(16))   # 4.0

# Load a module from a package:
user_module = importlib.import_module("myapp.models.user")
User = user_module.User


# Plugin system pattern:
PLUGIN_REGISTRY = {}

def register_plugin(name: str, module_path: str):
    module = importlib.import_module(module_path)
    plugin_class = getattr(module, "Plugin")
    PLUGIN_REGISTRY[name] = plugin_class

register_plugin("audio", "plugins.audio_processor")
register_plugin("video", "plugins.video_processor")

# Load any plugin by name at runtime:
plugin = PLUGIN_REGISTRY["audio"]()
plugin.run()


# Reload a module (useful in development, hot-reload):
importlib.reload(module)   # re-executes module code, updates sys.modules
```

---

## 😴 Chapter 11 — Lazy Imports: Speed Up Startup

Heavy modules (numpy, pandas, tensorflow) take time to import.
If a function rarely needs them, import lazily.

```python
# ❌ Always imports numpy — even if process_numbers() never called:
import numpy as np

def process_numbers(data):
    return np.array(data).mean()


# ✅ Only imports numpy when the function is actually called:
def process_numbers(data):
    import numpy as np    # deferred import
    return np.array(data).mean()


# In a class:
class DataProcessor:
    _np = None

    @classmethod
    def _get_np(cls):
        if cls._np is None:
            import numpy as np
            cls._np = np
        return cls._np

    def process(self, data):
        np = self._get_np()
        return np.array(data).mean()
```

```
USE LAZY IMPORTS WHEN:
  ✓ Module is heavy (numpy, pandas, ML libraries)
  ✓ Feature is optional (not all users need it)
  ✓ Breaking a circular import is needed temporarily
  ✓ CLI tools where startup time matters

DON'T USE FOR:
  ✗ Modules used in every call (overhead adds up)
  ✗ As a permanent solution for circular imports (fix the design instead)
```

---

## 🏠 Chapter 12 — Real Project Structure

### Small Project

```
my_project/
├── main.py               ← entry point
├── config.py             ← configuration
├── models.py             ← data models
├── services.py           ← business logic
├── utils.py              ← helpers
├── requirements.txt      ← dependencies
└── tests/
    └── test_services.py
```

### Medium/Large Project (Production)

```
my_project/
├── pyproject.toml        ← project metadata + build config (modern)
├── requirements.txt      ← pinned dependencies for deployment
├── requirements-dev.txt  ← dev/test dependencies
├── README.md
├── .env.example          ← example environment variables
│
├── src/                  ← source layout (avoids import confusion)
│   └── myapp/
│       ├── __init__.py
│       ├── config.py          ← settings, environment vars
│       ├── exceptions.py      ← custom exceptions
│       │
│       ├── models/            ← data models (SQLAlchemy, Pydantic)
│       │   ├── __init__.py
│       │   ├── user.py
│       │   └── product.py
│       │
│       ├── repositories/      ← data access layer
│       │   ├── __init__.py
│       │   └── user_repo.py
│       │
│       ├── services/          ← business logic
│       │   ├── __init__.py
│       │   ├── user_service.py
│       │   └── payment_service.py
│       │
│       ├── api/               ← HTTP layer
│       │   ├── __init__.py
│       │   ├── routes.py
│       │   └── middleware.py
│       │
│       └── utils/             ← shared utilities
│           ├── __init__.py
│           ├── validators.py
│           └── formatters.py
│
└── tests/
    ├── conftest.py
    ├── unit/
    │   └── test_user_service.py
    └── integration/
        └── test_api.py
```

---

## 📦 Chapter 13 — Virtual Environments: Dependency Isolation

### The Problem Without Virtual Environments

```
Your machine:
  Project A needs: Django==3.2, requests==2.25
  Project B needs: Django==4.2, requests==2.28

If both installed globally:
  pip install Django==3.2  → installs 3.2
  pip install Django==4.2  → OVERWRITES 3.2!
  Project A now breaks.
```

### Virtual Environment Solution

```bash
# Create isolated environment:
python -m venv venv

# Activate (macOS/Linux):
source venv/bin/activate

# Activate (Windows):
venv\Scripts\activate

# Now pip installs go to venv/lib/python3.x/site-packages:
pip install django==4.2
pip install requests==2.28

# Freeze exact versions for reproducibility:
pip freeze > requirements.txt

# On another machine / in production:
pip install -r requirements.txt

# Deactivate:
deactivate
```

### Modern Alternative — `pyproject.toml` with Poetry

```toml
# pyproject.toml
[tool.poetry]
name = "myapp"
version = "0.1.0"

[tool.poetry.dependencies]
python   = "^3.11"
django   = "^4.2"
requests = "^2.28"

[tool.poetry.dev-dependencies]
pytest = "^7.0"
black  = "^23.0"
```

```bash
poetry install    # creates venv + installs
poetry add numpy  # adds dependency + updates pyproject.toml
poetry run python main.py
```

---

## 📤 Chapter 14 — `sys.path`: How Python Finds Modules

```python
import sys
print(sys.path)
# ['',
#  '/usr/lib/python311.zip',
#  '/usr/lib/python3.11',
#  '/usr/lib/python3.11/lib-dynload',
#  '/home/user/.local/lib/python3.11/site-packages']
```

```
SEARCH ORDER:
  1. '' (empty string) = current working directory
  2. PYTHONPATH env variable directories
  3. Standard library directories
  4. site-packages (where pip installs)
```

```python
# You CAN modify sys.path at runtime (use sparingly!):
import sys
sys.path.insert(0, "/path/to/my/library")   # ← insert at front (highest priority)
import my_library

# Or via environment variable (before Python starts):
# PYTHONPATH=/path/to/libs python main.py
```

> **Better approach:** Install your project properly so it's on `sys.path` automatically:
> `pip install -e .` (editable install) registers your package in site-packages.

---

## 🌐 Chapter 15 — Namespace Packages (Python 3.3+)

In Python 3.3+, a directory **without** `__init__.py` is still a valid package — a **namespace package**.

```
namespace_pkg/         ← no __init__.py!
    module_a.py
    module_b.py

# Still works:
from namespace_pkg import module_a
```

```
USE CASES FOR NAMESPACE PACKAGES:
  • Splitting a large package across multiple directories or repos
  • Plugin systems where each plugin adds to a shared namespace
  • Distributing parts of a package as separate pip packages

REGULAR PACKAGES vs NAMESPACE PACKAGES:
  Regular (with __init__.py):    explicit, full-featured, runs init code
  Namespace (no __init__.py):    implicit, lightweight, split across locations
```

---

## 🎯 Key Takeaways

```
• A module = a .py file + a module object in memory
• Import sequence: check sys.modules → find in sys.path → execute → cache
• Modules execute only ONCE — second import returns the cached object
• sys.modules is the import cache — stores all loaded modules by name
• sys.path is the search path — order matters (current dir first)
• Package = directory with (optionally) __init__.py
• __init__.py controls public API, exports, and initialization
• __all__ defines what from X import * exports — also signals public interface
• Absolute imports (from myapp.models import User) preferred for clarity
• Relative imports (.utils, ..models) useful inside packages
• __name__ == "__main__" prevents side effects during import
• Circular imports = design smell → fix by extracting shared logic
• Lazy imports defer heavy modules until needed (startup performance)
• Virtual environments isolate dependencies per project — always use them
• importlib.import_module() enables dynamic/plugin architectures
• Namespace packages (no __init__.py) work in Python 3.3+
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [06 — Exceptions](../06_exceptions_error_handling/theory.md) |
| 📖 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ➡️ Next | [08 — File Handling](../08_file_handling/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Exceptions Error Handling — Interview Q&A](../06_exceptions_error_handling/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
