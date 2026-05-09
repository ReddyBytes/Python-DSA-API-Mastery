<a id="top"></a>
# 📦 07 — Modules & Packages

> *"The moment your codebase outgrows one file, you need to think architecturally.*
> *Modules are not just a way to split files — they're how you design a system."*

Day 1: You start a project. One file. 50 lines. Perfect.

Day 30: 500 lines. Still manageable.

Day 90: 3,000 lines. You need to scroll 10 minutes to find a function.
Five teammates are editing the same file. Git conflicts every hour.
Nobody knows which function does what. Test coverage is zero.

This is the **monolith trap**.

Every real project eventually faces it.
The solution: split code into **modules** and **packages** — each with a clear responsibility.

This chapter teaches you not just the syntax, but the *design thinking* behind it.

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. What Is a Module, Really?](#1-what-is-a-module-really)
- [2. The Import Machinery (What Really Happens)](#2-the-import-machinery-what-really-happens)
- [3. All Import Styles, When to Use Each](#3-all-import-styles-when-to-use-each)
  - [Style 1 — import module](#style-1-import-module)
  - [Style 2 — from module import name](#style-2-from-module-import-name)
  - [Style 3 — import module as alias](#style-3-import-module-as-alias)
  - [Style 4 — from module import name as alias](#style-4-from-module-import-name-as-alias)
  - [Style 5 — from module import *](#style-5-from-module-import-star)
- [4. Packages: Organizing Modules Into a System](#4-packages-organizing-modules-into-a-system)
- [5. __init__.py: The Package Controller](#5-__init__py-the-package-controller)
  - [Job 1 — Define the Public API](#job-1-define-public-api)
  - [Job 2 — Control Wildcard Imports with __all__](#job-2-control-wildcard-imports)
  - [Job 3 — Package Initialization](#job-3-package-initialization)
  - [Empty vs Populated __init__.py](#empty-vs-populated-init)
- [6. Absolute vs Relative Imports](#6-absolute-vs-relative-imports)
  - [Absolute Imports — The Safe Default](#absolute-imports)
  - [Relative Imports — Inside a Package](#relative-imports)
- [7. __name__ and the "__main__" Pattern](#7-__name__-and-the-__main__-pattern)
- [8. Circular Imports: The Design Warning](#8-circular-imports-the-design-warning)
  - [How It Breaks](#how-it-breaks)
  - [Fix 1 — Extract Shared Code to a Third Module](#fix-1-extract-shared-code)
  - [Fix 2 — Move the Import Inside the Function](#fix-2-move-import-inside-function)
  - [Fix 3 — Import the Module, Not the Name](#fix-3-import-the-module)
- [9. __all__: Defining the Public API](#9-__all__-defining-the-public-api)
- [10. Dynamic Imports with importlib](#10-dynamic-imports-with-importlib)
- [11. Lazy Imports: Speed Up Startup](#11-lazy-imports-speed-up-startup)
- [12. Real Project Structure](#12-real-project-structure)
  - [Small Project](#small-project)
  - [Medium/Large Project (Production)](#medium-large-project)
- [13. Virtual Environments: Dependency Isolation](#13-virtual-environments-dependency-isolation)
  - [The Problem Without Virtual Environments](#the-problem-without-venv)
  - [Virtual Environment Solution](#virtual-environment-solution)
  - [Modern Alternative — pyproject.toml with Poetry](#modern-alternative-pyproject)
- [14. sys.path: How Python Finds Modules](#14-syspath-how-python-finds-modules)
- [15. Namespace Packages (Python 3.3+)](#15-namespace-packages-python-33)
- [🎯 Key Takeaways](#key-takeaways)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`import` statement · `from X import Y` · `__name__ == "__main__"` · Package structure (`__init__.py`) · `sys.modules`

**Should Learn** — Important for real projects, comes up regularly:
Relative imports · `__all__` · `importlib.import_module()` · Circular imports (and how to fix them)

**Good to Know** — Useful in specific situations:
`importlib.reload()` · Lazy imports · `__package__` attribute

**Reference** — Know it exists, look up when needed:
Import hooks · Namespace packages · `importlib.resources`

<a id="1-what-is-a-module-really"></a>
# 1. What Is a Module, Really?

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

> 📝 **Practice:** [Q1 — Module vs Package](./practice.md#q1--ch1--module-vs-package)

> [↑ Back to Top](#top)

<a id="2-the-import-machinery-what-really-happens"></a>
# 2. The Import Machinery (What Really Happens)

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

> 📝 **Practice:** [Q2 — Import machinery](./practice.md#q2--ch2--import-machinery) · [Q3 — sys.modules](./practice.md#q3--ch2--sysmodules)

> [↑ Back to Top](#top)

<a id="3-all-import-styles-when-to-use-each"></a>
# 3. All Import Styles, When to Use Each

<a id="style-1-import-module"></a>
## Style 1 — `import module`

**Use when:** you want to be explicit about where things come from. Best for clarity.

```python
import math
import os
import json

# Access everything via the module namespace:
result = math.sqrt(16)
path   = os.path.join("folder", "file.txt")
data   = json.dumps({"key": "value"})
```

<a id="style-2-from-module-import-name"></a>
## Style 2 — `from module import name`

**Use when:** you're using specific items frequently and the name won't clash.

```python
from math import sqrt, pi
from os.path import join, exists
from datetime import datetime, timedelta

# Access directly — no prefix needed:
result = sqrt(16)
path   = join("folder", "file.txt")
now    = datetime.now()
```

<a id="style-3-import-module-as-alias"></a>
## Style 3 — `import module as alias`

**Use when:** the module name is long or has a well-known alias convention.

```python
import numpy as np              # industry standard alias
import pandas as pd             # industry standard alias
import matplotlib.pyplot as plt # industry standard alias

arr = np.array([1, 2, 3])
df  = pd.DataFrame({"a": [1, 2, 3]})
```

<a id="style-4-from-module-import-name-as-alias"></a>
## Style 4 — `from module import name as alias`

**Use when:** the name conflicts with something in your scope or is very long.

```python
from datetime import datetime as dt
from collections import OrderedDict as OD
from typing import Optional as Opt

now: Opt[dt] = dt.now()
```

<a id="style-5-from-module-import-star"></a>
## Style 5 — `from module import *` (⚠️ Usually Avoid)

The star import pulls every name from a module's `__all__` (or all non-underscore names if `__all__` is absent) directly into your namespace.

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

> 📝 **Practice:** [Q4 — import styles](./practice.md#q4--ch3--import-style-1) · [Q5 — import *](./practice.md#q5--ch3--import-star) · [Q6 — all 5 styles](./practice.md#q6--ch3--all-5-styles)

> [↑ Back to Top](#top)

<a id="4-packages-organizing-modules-into-a-system"></a>
# 4. Packages: Organizing Modules Into a System

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

> 📝 **Practice:** [Q39 · imports](../python_practice_questions_100.md#q39--normal--imports)

> 📝 **Practice:** [Q41 · __all__](../python_practice_questions_100.md#q41--normal--__all__)

> 📝 **Practice:** [Q7 — Package structure](./practice.md#q7--ch4--package-structure)

> [↑ Back to Top](#top)

<a id="5-__init__py-the-package-controller"></a>
# 5. __init__.py: The Package Controller

`__init__.py` runs when the package is first imported. Its job:

<a id="job-1-define-public-api"></a>
## Job 1 — Define the Public API

`__init__.py` re-exports the classes you want users to reach directly, so callers use `from myapp.models import User` instead of navigating internal file paths.

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

<a id="job-2-control-wildcard-imports"></a>
## Job 2 — Control Wildcard Imports with `__all__`

Setting `__all__` in `__init__.py` restricts which names get exported on `from package import *`, keeping internal helpers out of the caller's namespace.

```python
# myapp/utils/__init__.py

__all__ = ["validate_email", "format_currency", "slugify"]
# Only these are exported when someone does: from myapp.utils import *
```

<a id="job-3-package-initialization"></a>
## Job 3 — Package Initialization

The package-level `__init__.py` is the right place for metadata (`__version__`, `__author__`) and one-time setup like attaching a `NullHandler` to silence logging until the caller configures it.

```python
# myapp/__init__.py

__version__ = "1.2.3"
__author__  = "Your Name"

# Initialize logging for the whole package:

import logging
logging.getLogger("myapp").addHandler(logging.NullHandler())
```

> 📝 **Practice:** [Q99 · open-ended-logging](../python_practice_questions_100.md#q99--critical--open-ended-logging)

<a id="empty-vs-populated-init"></a>
## Empty vs Populated `__init__.py`

An empty `__init__.py` simply marks the directory as a package. A populated one controls the public surface — Django and Flask both use rich `__init__.py` files to expose a clean top-level API.

```python
# Minimal __init__.py — just marks the directory as a package:
# (file can be empty)

# Rich __init__.py — controls the public API (Django, Flask style):
from .models   import User, Product
from .services import UserService
from .config   import Settings
```

> 📝 **Practice:** [Q8–Q10 — __init__.py jobs](./practice.md#q8--ch5--__init__py-job-1) · [Deep dive →](./01_sys_module/theory.md)

> [↑ Back to Top](#top)

<a id="6-absolute-vs-relative-imports"></a>
# 6. Absolute vs Relative Imports

<a id="absolute-imports"></a>
## Absolute Imports — The Safe Default

Absolute imports spell out the full path from the project root, making it immediately clear where any name comes from regardless of which file you're reading.

```python
# Full path from the project root:
from myapp.models.user    import User
from myapp.services.auth  import authenticate
from myapp.utils          import validate_email

# ✅ Always clear where things come from
# ✅ Works from anywhere
# ✅ Preferred in large projects
```

<a id="relative-imports"></a>
## Relative Imports — Inside a Package

Relative imports use dots to express position: `.` means the current package, `..` the parent package. They are shorter inside a package but break when the file is run directly as a script.

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

> 📝 **Practice:** [Q11 — Relative imports](./practice.md#q11--ch6--relative-imports)

> [↑ Back to Top](#top)

<a id="7-__name__-and-the-__main__-pattern"></a>
# 7. __name__ and the "__main__" Pattern

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

> 📝 **Practice:** [Q12 — __name__ guard](./practice.md#q12--ch7--__name__-guard) · [Q13 — dual-use file](./practice.md#q13--ch7--dual-use-file)

> [↑ Back to Top](#top)

<a id="8-circular-imports-the-design-warning"></a>
# 8. Circular Imports: The Design Warning

A circular import happens when module A imports module B, and module B (directly or indirectly) imports module A.

> 📝 **Practice:** [Q40 · circular-imports](../python_practice_questions_100.md#q40--critical--circular-imports)

<a id="how-it-breaks"></a>
## How It Breaks

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

<a id="fix-1-extract-shared-code"></a>
## Fix 1 — Extract Shared Code to a Third Module

The cleanest solution: if A and B both need something, that shared logic doesn't belong to either. Move it to a third module that neither A nor B imports.

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

<a id="fix-2-move-import-inside-function"></a>
## Fix 2 — Move the Import Inside the Function

Deferring the import to function call time means both modules finish loading before either needs the other — the circular dependency exists in the source but is never triggered at import time.

```python
# a.py
def greet_a():
    return "Hello from A"

def use_b():
    from b import greet_b    # ← import deferred until function is called
    return greet_b()         # ← by then, both modules are fully loaded
```

<a id="fix-3-import-the-module"></a>
## Fix 3 — Import the Module, Not the Name

Importing the module object (`import b`) rather than a name from it (`from b import greet_b`) delays attribute lookup until call time, after both modules are fully initialised.

```python
# a.py
import b    # ← importing the module is safer; access b.greet_b() later

def use_b():
    return b.greet_b()   # ← deferred attribute access, works after both load
```

> **Circular imports are a design smell.** They mean your module boundaries are wrong. If A and B need each other, they probably belong in the same module, or their shared logic belongs in a third module.

> 📝 **Practice:** [Q14 — circular import](./practice.md#q14--ch8--circular-import) · [Q15 — fix circular](./practice.md#q15--ch8--fix-circular)

> [↑ Back to Top](#top)

<a id="9-__all__-defining-the-public-api"></a>
# 9. __all__: Defining the Public API

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

> 📝 **Practice:** [Q16 — __all__](./practice.md#q16--ch9--__all__) · [Q17 — without __all__](./practice.md#q17--ch9--without-__all__)

> [↑ Back to Top](#top)

<a id="10-dynamic-imports-with-importlib"></a>
# 10. Dynamic Imports with importlib

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

> 📝 **Practice:** [Q18 — importlib](./practice.md#q18--ch10--importlib) · [Q19 — plugin registry](./practice.md#q19--ch10--plugin-registry) · [Q31 — reload](./practice.md#q31--ch10--importlibreload)

> [↑ Back to Top](#top)

<a id="11-lazy-imports-speed-up-startup"></a>
# 11. Lazy Imports: Speed Up Startup

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

> 📝 **Practice:** [Q20 — lazy import](./practice.md#q20--ch11--lazy-import) · [Q21 — class-level lazy](./practice.md#q21--ch11--class-level-lazy)

> [↑ Back to Top](#top)

<a id="12-real-project-structure"></a>
# 12. Real Project Structure

<a id="small-project"></a>
## Small Project

For projects under ~500 lines, flat structure works fine — one file per concern at the root level, no sub-packages needed.

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

<a id="medium-large-project"></a>
## Medium/Large Project (Production)

As the codebase grows, the `src/` layout isolates importable code from project-level config files, preventing accidental imports from the repo root during development.

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

> 📝 **Practice:** [Q22 — project layout](./practice.md#q22--ch12--project-layout)

> [↑ Back to Top](#top)

<a id="13-virtual-environments-dependency-isolation"></a>
# 13. Virtual Environments: Dependency Isolation

<a id="the-problem-without-venv"></a>
## The Problem Without Virtual Environments

Without isolation, every project on the machine shares one Python environment — installing a new version of any package can silently break other projects.

```
Your machine:
  Project A needs: Django==3.2, requests==2.25
  Project B needs: Django==4.2, requests==2.28

If both installed globally:
  pip install Django==3.2  → installs 3.2
  pip install Django==4.2  → OVERWRITES 3.2!
  Project A now breaks.
```

<a id="virtual-environment-solution"></a>
## Virtual Environment Solution

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

<a id="modern-alternative-pyproject"></a>
## Modern Alternative — `pyproject.toml` with Poetry

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

> 📝 **Practice:** [Q23 — venv creation](./practice.md#q23--ch13--venv-creation) · [Q24 — why venv](./practice.md#q24--ch13--why-venv) · [Deep dive →](./04_virtual_environments/theory.md)

> [↑ Back to Top](#top)

<a id="14-syspath-how-python-finds-modules"></a>
# 14. sys.path: How Python Finds Modules

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

> 📝 **Practice:** [Q25 — sys.path order](./practice.md#q25--ch14--syspath-order) · [Q26 — modify sys.path](./practice.md#q26--ch14--modify-syspath) · [Deep dive →](./01_sys_module/theory.md)

> [↑ Back to Top](#top)

<a id="15-namespace-packages-python-33"></a>
# 15. Namespace Packages (Python 3.3+)

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

> 📝 **Practice:** [Q29 — namespace packages](./practice.md#q29--ch15--namespace-packages)

> [↑ Back to Top](#top)

<a id="key-takeaways"></a>
# 🎯 Key Takeaways

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

<a id="navigation"></a>
# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [06 — Exceptions & Error Handling → theory.md](../06_exceptions_error_handling/theory.md) |
| ➡ Next Module | [08 — File Handling → theory.md](../08_file_handling/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Practice Local](./practice_local.py) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[01 sys module →](./01_sys_module/theory.md) · [02 argparse →](./02_argparse/theory.md) · [03 subprocess →](./03_subprocess/theory.md) · [04 Virtual Environments →](./04_virtual_environments/theory.md)

**Jump to specific topics:**
- Import machinery (sys.modules) → [#2-the-import-machinery-what-really-happens](#2-the-import-machinery-what-really-happens)
- __init__.py Public API → [#5-__init__py-the-package-controller](#5-__init__py-the-package-controller)
- Circular imports fixes → [#8-circular-imports-the-design-warning](#8-circular-imports-the-design-warning)
- sys.path search order → [#14-syspath-how-python-finds-modules](#14-syspath-how-python-finds-modules)
- Virtual environments → [#13-virtual-environments-dependency-isolation](#13-virtual-environments-dependency-isolation)

> [↑ Back to Top](#top)
