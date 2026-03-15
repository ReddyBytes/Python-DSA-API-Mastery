# 🎯 Modules & Packages — Interview Questions

> *"Import questions reveal whether you understand Python as a system,*
> *not just as a scripting tool."*

---

## 📊 Question Map

```
LEVEL 1 — Junior (0–2 years)
  • What is a module / package
  • Import syntax and styles
  • __name__ == "__main__"
  • sys.modules basics

LEVEL 2 — Mid-Level (2–5 years)
  • Import machinery internals
  • Circular imports: cause + fix
  • Absolute vs relative imports
  • __init__.py and __all__
  • sys.path manipulation

LEVEL 3 — Senior (5+ years)
  • Project structure design
  • Lazy imports and performance
  • Dynamic imports / plugin systems
  • Virtual environments and packaging
  • Namespace packages
```

---

## 🟢 Level 1 — Junior Questions

---

### Q1: What is a module in Python?

**Weak answer:** "A module is a file."

**Strong answer:**

> A module is both a `.py` file on disk **and** a module object in memory. When you `import` a module, Python executes the file once, creates a module object (of type `<class 'module'>`), and stores it in `sys.modules`. Subsequent imports just retrieve the cached object — the file is not re-executed.

```python
import math
print(type(math))           # <class 'module'>
print(math.__file__)        # path to math.py / math.so
print("math" in sys.modules)  # True
```

---

### Q2: What is the difference between a module and a package?

**Strong answer:**

> A **module** is a single `.py` file. A **package** is a directory that contains modules (and sub-packages), optionally with an `__init__.py` file that runs when the package is imported.

```
module:   math_utils.py             → import math_utils
package:  myapp/                    → import myapp
             __init__.py
             models.py              → from myapp import models
             utils/                 → sub-package
                 __init__.py
                 validators.py      → from myapp.utils import validators
```

---

### Q3: What are the different ways to import in Python? When would you use each?

**Strong answer:**

```python
import math                      # access via math.sqrt() — most explicit
from math import sqrt, pi        # direct access — use when specific items needed frequently
import numpy as np               # alias — use for long names or standard conventions
from math import sqrt as sq      # rename — use to avoid name conflicts
from module import *             # ⚠️ avoid — pollutes namespace, debugging nightmare
```

> Best practice: prefer `import module` or `from module import specific_name`.
> Use `import *` only in `__init__.py` for controlled re-exports, never in application code.

---

### Q4: What does `if __name__ == "__main__":` mean and why is it important?

**Weak answer:** "It runs the code only when executed directly."

**Strong answer:**

> `__name__` is a special variable set by Python:
> - When a file is **run directly** (`python script.py`): `__name__ = "__main__"`
> - When a file is **imported**: `__name__ = "the_module_name"`
>
> The guard prevents code from executing as a side effect of importing. Without it, every import of your module would also run your test/main code.

```python
# calculator.py
def add(a, b): return a + b

# WITHOUT guard — this runs on every import:
print(add(1, 2))   # prints "3" when someone does `import calculator`!

# WITH guard:
if __name__ == "__main__":
    print(add(1, 2))   # only runs when: python calculator.py
```

---

### Q5: Why should you avoid `from module import *`?

**Strong answer:**

```python
# Problem 1: Namespace pollution — you don't know what names you got:
from os.path import *
from posixpath import *
# Both export 'join' — which version did you get? Silent override!

# Problem 2: Name shadowing:
from math import *      # imports 'pi', 'e', 'sqrt', etc.
pi = 3.14               # your variable
# Did you just shadow math.pi? Unclear.

# Problem 3: Traceability — IDEs and linters can't find where names come from
sqrt(16)    # which module is sqrt from? No way to tell without reading imports

# SOLUTION — always explicit:
from math import sqrt, pi
```

---

## 🔵 Level 2 — Mid-Level Questions

---

### Q6: Explain exactly what happens when Python imports a module.

**Strong answer:**

> 1. Python checks `sys.modules` — if the module is already there, return it immediately (no re-execution)
> 2. Python searches `sys.path` in order: current dir → `PYTHONPATH` → stdlib → site-packages
> 3. Python finds the `.py` file and compiles it to bytecode (`.pyc` in `__pycache__/`), or loads the cached bytecode
> 4. Python **executes all top-level code** in the module (class/function definitions, variable assignments, imports)
> 5. The module object is stored in `sys.modules` under its fully-qualified name
> 6. The name is bound in the importing namespace

```python
import sys

print(len(sys.modules))   # many modules already loaded (builtins etc.)
import json
print("json" in sys.modules)   # True
import json   # second import — nothing executes, just returns cache
```

---

### Q7: What is a circular import? How do you fix it?

**Weak answer:** "A imports B and B imports A — it causes an error."

**Strong answer:**

> A circular import occurs when module A imports from module B at the top level, and module B also imports from module A at the top level. Python partially loads A, switches to loading B, tries to import from A which is only partially initialized — `NameError` or missing attributes result.
>
> **Root cause:** circular imports are a design problem. The modules have a dependency cycle that shouldn't exist.

```python
# a.py                     # b.py
from b import greet_b      from a import greet_a   ← a is half-loaded!
def greet_a(): ...         def greet_b(): ...
```

**Three fixes:**

```python
# Fix 1: Extract shared code to a third module (best):
# shared.py → both a.py and b.py import from shared.py

# Fix 2: Defer import to inside a function:
def greet_a():
    from b import greet_b   # imports only when function is called, not at module load
    return greet_b()

# Fix 3: Import the module instead of the name:
import b                    # module import can handle partial loading better
def use_b(): return b.greet_b()
```

---

### Q8: What is the difference between absolute and relative imports? Which do you prefer?

**Strong answer:**

> **Absolute imports** use the full path from the project root: `from myapp.models.user import User`. They work from anywhere and are always unambiguous.
>
> **Relative imports** use dot notation relative to the current package: `from .models import User` (same package), `from ..utils import helpers` (parent package).
>
> I prefer absolute imports in almost all cases — they're explicit, work from any context, and are easier to understand when reading code. Relative imports are acceptable inside packages for internal cross-module references, but become confusing in deep hierarchies.

```python
# Absolute (preferred):
from myapp.services.payment import PaymentService

# Relative (acceptable inside package):
# inside myapp/services/user_service.py:
from ..models import User       # parent package's models
from .payment import process    # sibling module
```

---

### Q9: What is `__init__.py`? What can you put in it?

**Strong answer:**

> `__init__.py` is the initializer for a package. It runs when the package is first imported. Its main roles are:
> 1. **Define the public API**: re-export names so users access them via the package, not the submodule
> 2. **Control `__all__`**: what `from package import *` exports
> 3. **Run initialization code**: logging setup, configuration loading, etc.

```python
# myapp/models/__init__.py

# Control what's accessible at the package level:
from .user    import User
from .product import Product

__all__ = ["User", "Product"]   # explicit public API

# Now users can write:
from myapp.models import User       # clean
# Instead of:
from myapp.models.user import User  # leaks internal structure
```

---

### Q10: What is `__all__` and why would you define it?

**Strong answer:**

> `__all__` is a list of strings that controls two things:
> 1. What gets imported when someone does `from module import *`
> 2. What IDEs and tools consider the **public API** of the module

```python
# validators.py
__all__ = ["validate_email", "validate_phone"]

def validate_email(email): ...    # public
def validate_phone(phone): ...    # public
def _normalize(value): ...        # private — not in __all__, not exported

# from validators import *  → gets validate_email, validate_phone ONLY
# from validators import _normalize  → still possible explicitly, but signals "private"
```

> Even if you rarely use `from module import *`, defining `__all__` is good practice:
> it documents your intent and helps tools like `pydoc`, `sphinx`, and linters.

---

### Q11: What is `sys.path` and when would you modify it?

**Strong answer:**

> `sys.path` is a list of directory strings where Python searches for modules, in order. The first match wins.
>
> You can modify it but should do so carefully — it's a global mutable list.

```python
import sys
print(sys.path)
# ['', '/usr/lib/python3.11', ..., '/usr/lib/python3/dist-packages']

# Add a custom path:
sys.path.insert(0, "/path/to/my/libs")   # highest priority
import my_lib   # found in /path/to/my/libs/my_lib.py

# BETTER approach: install your package properly:
# pip install -e .   ← editable install, registers in site-packages
```

---

## 🔴 Level 3 — Senior Questions

---

### Q12: How would you structure a large Python project?

**Strong answer:**

> I'd organize around **architectural layers** with clean boundaries between them, where each layer only imports from layers below it (never upward).

```
src/
└── myapp/
    ├── models/          ← data shapes (no business logic, no imports upward)
    ├── repositories/    ← data access (imports models, no business logic)
    ├── services/        ← business logic (imports models + repositories)
    ├── api/             ← HTTP layer (imports services, maps to HTTP)
    └── utils/           ← shared helpers (no imports from above layers)

Key rules:
  1. Each package exposes its API via __init__.py
  2. No circular dependencies between layers
  3. Dependencies always point downward (api → services → repositories → models)
  4. utils/ imports nothing from the rest of myapp
```

---

### Q13: How do you implement a plugin system with dynamic imports?

**Strong answer:**

```python
import importlib
from typing import Type

class PluginBase:
    def run(self): raise NotImplementedError

REGISTRY: dict[str, Type[PluginBase]] = {}

def register(name: str, module_path: str):
    """Dynamically load and register a plugin."""
    module = importlib.import_module(module_path)
    cls = getattr(module, "Plugin")
    if not issubclass(cls, PluginBase):
        raise TypeError(f"{cls} must subclass PluginBase")
    REGISTRY[name] = cls

def get_plugin(name: str) -> PluginBase:
    if name not in REGISTRY:
        raise KeyError(f"No plugin registered: {name}")
    return REGISTRY[name]()

# Runtime registration — no hard-coded imports:
register("audio", "plugins.audio_processor")
register("video", "plugins.video_processor")

plugin = get_plugin("audio")
plugin.run()
```

---

### Q14: What are lazy imports and when should you use them?

**Strong answer:**

> Lazy imports defer the loading of a module until the first time it's actually needed. This reduces startup time for applications that don't always use every feature.

```python
# Heavy module that takes 500ms to import:
# import tensorflow as tf  ← 500ms on startup, even if we never use it!

class MLPredictor:
    def predict(self, data):
        import tensorflow as tf   # only imports when predict() is called
        model = tf.keras.models.load_model("model.h5")
        return model.predict(data)

# When to use lazy imports:
# ✓ Optional heavy dependencies (numpy, tensorflow, PIL)
# ✓ CLI tools where startup time matters
# ✓ Breaking a circular import temporarily (but fix the design!)
# ✓ Features behind feature flags

# Python 3.12+ has importlib.util for official lazy loading support
```

---

### Q15: What is the difference between regular packages and namespace packages?

**Strong answer:**

> A **regular package** has `__init__.py` — Python runs it on import, the package has a single physical location.
>
> A **namespace package** (Python 3.3+) has no `__init__.py` — it can span multiple directories and even multiple installed packages.

```python
# Namespace packages enable:
# company/                              company/
#   billing/                              billing/
#     __init__.py  ← regular             (no __init__.py) ← namespace

# SPLIT across repos:
# /repo1/mycompany/auth/
# /repo2/mycompany/billing/
# Both on sys.path → from mycompany.auth import ... works!
# Python merges them into one "mycompany" namespace package.
```

---

## ⚠️ Trap Questions

---

### Trap 1 — Modules Execute Only Once

```python
# counter.py
count = 0
print(f"Module loaded! count = {count}")

# main.py
import counter      # prints: "Module loaded! count = 0"
counter.count = 99
import counter      # prints NOTHING — cached in sys.modules
print(counter.count)  # 99 — same object, mutation persists!
```

---

### Trap 2 — `from X import name` Doesn't Stay Live

```python
# config.py
DEBUG = False

# app.py
from config import DEBUG   # DEBUG is now a LOCAL variable in app.py

import config
config.DEBUG = True        # changes config module's attribute

print(DEBUG)               # False! — local binding didn't update
print(config.DEBUG)        # True  — module attribute did update

# LESSON: `from X import name` creates a COPY of the binding.
# Reassigning the original doesn't affect the imported name.
```

---

### Trap 3 — Relative Import Outside a Package

```python
# script.py (run directly as python script.py)
from . import utils   # ImportError! Relative imports only work inside packages.
                      # When run directly, __package__ is None.

# FIX: use absolute import:
from utils import something

# Or run as a module:
# python -m mypackage.script   ← now relative imports work
```

---

### Trap 4 — Shadowing Standard Library Modules

```python
# If you create a file named: datetime.py or json.py in your project:
# import datetime  ← imports YOUR file, not the stdlib!
# This is a common beginner mistake.

# AVOID naming files after stdlib modules:
# datetime.py, json.py, os.py, math.py, string.py, etc.
```

---

## 🔥 Rapid-Fire Revision

```
Q: What is sys.modules?
A: A dict that caches all imported modules by name. Python checks it first on every import.

Q: Where does Python search for modules?
A: sys.path in order: current dir → PYTHONPATH → stdlib → site-packages.

Q: What does __init__.py do?
A: Runs when the package is imported. Used to define public API, set __all__,
   and run package initialization code.

Q: When does a module's code execute?
A: Only once — when first imported. Subsequent imports return the cached object.

Q: What is a namespace package?
A: A package without __init__.py (Python 3.3+). Can span multiple directories.

Q: What does importlib.import_module() do?
A: Imports a module by name string at runtime. Used for plugin systems.

Q: What is an editable install?
A: pip install -e . — installs your package in dev mode, linked to source.
   Changes to source are reflected immediately without reinstalling.

Q: What is the __pycache__ directory?
A: Where Python stores compiled bytecode (.pyc files) to speed up future imports.

Q: How do you reload a module after changes?
A: importlib.reload(module) — re-executes module code and updates the object.
   Note: existing references to old names are NOT updated.

Q: What's the difference between package and distribution package?
A: A Python package = directory of modules (import-level concept).
   A distribution package = what you install via pip (e.g., "requests").
   They can have different names (import: PIL, install: Pillow).
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ➡️ Next | [08 — File Handling](../08_file_handling/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [File Handling — Theory →](../08_file_handling/theory.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md)
