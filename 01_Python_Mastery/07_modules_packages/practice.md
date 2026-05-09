# 💻 Practice — Modules & Packages

> **This is the master practice file.** It covers the 15 root theory chapters at survey depth.
> For deep practice on specific tools, use the subfolder files:
> - [sys module →](./01_sys_module/practice.md)
> - [argparse →](./02_argparse/practice.md)
> - [subprocess →](./03_subprocess/practice.md)
> - [virtual environments →](./04_virtual_environments/practice.md)

---

## Quick Index

| Q# | Chapter | Concept | Difficulty |
|---|---|---|---|
| [Q1](#q1) | Ch1 | Module vs Package | 🟢 |
| [Q2](#q2) | Ch2 | Import machinery | 🟢 |
| [Q3](#q3) | Ch2 | sys.modules | 🟢 |
| [Q4](#q4) | Ch3 | Import style 1 | 🟢 |
| [Q5](#q5) | Ch3 | Import star | 🟢 |
| [Q6](#q6) | Ch3 | All 5 styles | 🟢 |
| [Q7](#q7) | Ch4 | Package structure | 🟡 |
| [Q8](#q8) | Ch5 | `__init__.py` job 1 | 🟡 |
| [Q9](#q9) | Ch5 | `__init__.py` job 2 | 🟡 |
| [Q10](#q10) | Ch5 | `__init__.py` job 3 | 🟡 |
| [Q11](#q11) | Ch6 | Relative imports | 🟡 |
| [Q12](#q12) | Ch7 | `__name__` guard | 🟡 |
| [Q13](#q13) | Ch7 | Dual-use file | 🟡 |
| [Q14](#q14) | Ch8 | Circular import | 🟡 |
| [Q15](#q15) | Ch8 | Fix circular | 🟡 |
| [Q16](#q16) | Ch9 | `__all__` | 🟡 |
| [Q17](#q17) | Ch9 | Without `__all__` | 🟡 |
| [Q18](#q18) | Ch10 | importlib | 🟡 |
| [Q19](#q19) | Ch10 | Plugin registry | 🟡 |
| [Q20](#q20) | Ch11 | Lazy import | 🟡 |
| [Q21](#q21) | Ch11 | Class-level lazy | 🟡 |
| [Q22](#q22) | Ch12 | Project layout | 🟡 |
| [Q23](#q23) | Ch13 | venv creation | 🟡 |
| [Q24](#q24) | Ch13 | Why venv | 🟡 |
| [Q25](#q25) | Ch14 | sys.path order | 🟡 |
| [Q26](#q26) | Ch14 | Modify sys.path | 🟡 |
| [Q27](#q27) | Ch8+Ch10 | Safe optional import | 🟠 |
| [Q28](#q28) | Ch5+Ch9 | API design | 🟠 |
| [Q29](#q29) | Ch15 | Namespace packages | 🟠 |
| [Q30](#q30) | Capstone | Full package design | 🟠 |
| [Q31](#q31) | Ch10 | importlib.reload | 🟡 |

---

<a id="q1"></a>

### Q1 🟢 · Ch1 · Module vs Package

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)



**Problem:** What is the difference between a module and a package? What makes a directory a package?

<details>
<summary>💡 Hint</summary>

Think about the file system. A module is a single file. A package is a directory. What does the directory need to be recognized as a package?

</details>

<details>
<summary>✅ Answer</summary>

```
MODULE:  a single .py file on disk
         math_utils.py  →  import math_utils

PACKAGE: a directory that contains Python modules
         myapp/         →  import myapp
         ├── __init__.py
         ├── models.py
         └── utils.py
```

**What makes a directory a package:**

In Python 3.3+, any directory can be imported as a "namespace package" — no `__init__.py` required. But a **regular package** requires an `__init__.py` file (even if empty).

```
myapp/
├── __init__.py   ← this file makes myapp a regular package
├── models.py
└── utils.py
```

```python
import myapp           # runs myapp/__init__.py
import myapp.models    # runs myapp/models.py
from myapp import utils
```

**Why:** A module is simultaneously a `.py` file on disk AND a module object in memory. A package is a namespace that groups related modules. The `__init__.py` signals intent: "this directory is a Python package with controlled initialization."

</details>

---

<a id="q2"></a>

### Q2 🟢 · Ch2 · Import Machinery

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)



**Problem:** List the 6 steps Python takes when you write `import math` for the first time.

<details>
<summary>💡 Hint</summary>

Python checks a cache first before doing any file I/O. After finding the file, it must create an object and execute the code.

</details>

<details>
<summary>✅ Answer</summary>

```
Step 1: CHECK sys.modules CACHE
        → Is "math" already imported?
        → If yes: return cached module object immediately. Done.
        → If no: continue.

Step 2: FIND the module
        → Search sys.path in order:
          1. Current directory (or script directory)
          2. PYTHONPATH entries
          3. Standard library directories
          4. Site-packages (third-party)

Step 3: CREATE a module object
        → Python creates an empty module object: <module 'math'>

Step 4: REGISTER in sys.modules
        → sys.modules["math"] = <module object>
        → (registered BEFORE execution to handle circular imports)

Step 5: EXECUTE the module code
        → Python runs the .py file top-to-bottom
        → All definitions (functions, classes, variables) are added
          as attributes of the module object

Step 6: RETURN the module object
        → The name "math" in your namespace points to the module object
```

**Why:** Understanding this order explains why modules run only once (step 1 short-circuits), why circular imports partially work (step 4 registers early), and why modifying `sys.modules` affects all future imports.

</details>

---

<a id="q3"></a>

### Q3 🟢 · Ch2 · sys.modules

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)



**Problem:** What is `sys.modules` and why does it mean module code runs only once per process?

<details>
<summary>💡 Hint</summary>

`sys.modules` is a dictionary. Python checks it before any file I/O. What happens on the second `import math`?

</details>

<details>
<summary>✅ Answer</summary>

```python
import sys
import math

# sys.modules is a dict: module_name -> module_object
print(type(sys.modules))        # <class 'dict'>
print("math" in sys.modules)    # True
print(sys.modules["math"])      # <module 'math' from '...'>

# Second import is instant — no file I/O
import math   # hits the cache, returns the same object
```

**Why code runs only once:**

```python
# counter.py
print("counter.py is running")
count = 0

# main.py
import counter    # prints: "counter.py is running"
import counter    # prints nothing — returns from sys.modules cache
import counter    # prints nothing

import sys
print(id(sys.modules["counter"]))  # same object every time
```

The first `import counter` executes the file and registers the result in `sys.modules["counter"]`. Every subsequent `import counter` finds it there and returns the cached object. The file never re-executes.

**Practical implication:** Module-level state (like `count = 0` above) is shared across all importers. If `module_a.py` and `module_b.py` both do `import counter`, they share the same `counter` object.

</details>

---

<a id="q4"></a>

### Q4 🟢 · Ch3 · Import Style 1

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)



**Problem:** When would you use `import math` vs `from math import sqrt`?

<details>
<summary>💡 Hint</summary>

Think about namespace clarity vs convenience. What happens in each case when you type the function name?

</details>

<details>
<summary>✅ Answer</summary>

```python
# Style 1: import math
import math
result = math.sqrt(16)   # explicit: you see where sqrt comes from
result = math.pi         # clear origin

# Style 2: from math import sqrt
from math import sqrt
result = sqrt(16)        # shorter, but origin is hidden
```

**Use `import math` when:**
- The module name adds useful context (`math.sqrt` vs just `sqrt`)
- You use many names from the module
- Avoiding name clashes with your own code matters
- Reading the code, you want origin to be obvious

```python
import math
import statistics
# Clear: math.sqrt vs statistics.mean — no ambiguity
```

**Use `from math import sqrt` when:**
- You use one or two names heavily in a file
- The name is unambiguous in context
- Saving keystrokes genuinely improves readability

```python
from math import sqrt, pi
# In a geometry file, sqrt and pi need no qualification
area = pi * sqrt(radius)
```

**Rule of thumb:** If a reader would ask "where does this come from?", use `import module`. If the answer is obvious from context, `from module import name` is fine.

</details>

---

<a id="q5"></a>

### Q5 🟢 · Ch3 · Import Star

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)



**Problem:** Why is `from module import *` dangerous in production code? When is it acceptable?

<details>
<summary>💡 Hint</summary>

What happens to your local namespace? What if two modules both export a function called `connect`?

</details>

<details>
<summary>✅ Answer</summary>

**Why it's dangerous:**

```python
# BAD: pollutes namespace, causes silent bugs
from os.path import *
from shutil import *

# Now: which "copy" function do you have? shutil.copy? No idea.
# If both export "copy", the second import silently wins.
copy(src, dst)  # which one? ambiguous, fragile
```

```python
# Another danger: accidental overwrite
x = 10
from some_module import *   # if some_module has x = 999, your x is gone silently
print(x)                    # 999, not 10
```

**Specific problems:**
1. **Name collisions** — two modules export the same name, second wins silently
2. **Polluted namespace** — `dir()` shows dozens of names you didn't explicitly import
3. **Broken grep** — you can't find where a name came from by searching imports
4. **Circular import risk** — star imports make circular detection harder
5. **IDE autocomplete breaks** — tools can't trace the origin of names

**When it's acceptable:**
```python
# 1. Interactive REPL / Jupyter notebooks — convenience wins
from numpy import *
from matplotlib.pyplot import *

# 2. Explicitly designed public API — module defines __all__ to control what exports
# In math_dsl/__init__.py:
from .operators import *    # __all__ = ["add", "sub", "mul"]
from .constants import *    # __all__ = ["PI", "E"]
```

**Rule:** In any `.py` file that goes to production or is reviewed by others, never use `import *`. Reserve it for throwaway scripts and notebooks.

</details>

---

<a id="q6"></a>

### Q6 🟢 · Ch3 · All 5 Styles

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)



**Problem:** Write an example of each of the 5 import styles.

<details>
<summary>💡 Hint</summary>

The 5 styles are: plain import, from-import, aliased import, from-import-as, and star import.

</details>

<details>
<summary>✅ Answer</summary>

```python
# Style 1: plain import
# Use when: you want namespace clarity, or using many names from the module
import math
print(math.sqrt(16))     # 4.0
print(math.pi)           # 3.14159...

# Style 2: from-import (named)
# Use when: you use a few names heavily and they're unambiguous
from math import sqrt, pi
print(sqrt(16))          # 4.0
print(pi)                # 3.14159...

# Style 3: aliased module import
# Use when: module name is long or conflicts with something in your scope
import numpy as np
import pandas as pd
arr = np.array([1, 2, 3])

# Style 4: from-import with alias
# Use when: imported name conflicts with a local name, or you want a shorter alias
from collections import defaultdict as ddict
from datetime import datetime as dt
now = dt.now()

# Style 5: star import
# Use when: REPL/notebooks only, or module defines __all__ for a clean public API
from math import *
print(sin(pi / 2))       # 1.0  — sin and pi come from math
```

**Summary table:**

```
Style                        | Namespace impact        | Readability
-----------------------------|-------------------------|------------------
import math                  | adds "math"             | explicit origin
from math import sqrt        | adds "sqrt"             | concise, clear
import numpy as np           | adds "np"               | industry standard
from datetime import dt      | adds "dt"               | short alias
from math import *           | adds EVERYTHING         | dangerous in prod
```

</details>

---

<a id="q7"></a>

### Q7 🟡 · Ch4 · Package Structure

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)



**Problem:** Draw the directory tree for a Flask-style web app package with models, services, api, utils sub-packages.

<details>
<summary>💡 Hint</summary>

Every sub-package needs its own `__init__.py`. Think about what lives in each layer: data definitions, business logic, HTTP handlers, shared utilities.

</details>

<details>
<summary>✅ Answer</summary>

```
myapp/
├── __init__.py              # package root: version, app factory
│
├── models/                  # data layer — ORM models, schemas
│   ├── __init__.py          # re-exports: User, Product, Order
│   ├── user.py
│   ├── product.py
│   └── order.py
│
├── services/                # business logic layer
│   ├── __init__.py
│   ├── user_service.py      # UserService class
│   ├── order_service.py     # OrderService class
│   └── payment_service.py   # PaymentService class
│
├── api/                     # HTTP layer — routes, request/response
│   ├── __init__.py          # registers blueprints
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── users.py         # /api/v1/users endpoints
│   │   └── orders.py        # /api/v1/orders endpoints
│   └── middleware.py        # auth, logging, rate limiting
│
├── utils/                   # shared helpers — no business logic
│   ├── __init__.py
│   ├── validators.py        # input validation helpers
│   ├── formatters.py        # date, currency formatting
│   └── exceptions.py        # custom exception classes
│
├── config.py                # environment-based configuration
└── app.py                   # application factory: create_app()
```

**Why this structure works:**
- **models** — pure data definitions, no HTTP knowledge
- **services** — business logic, imports from models only
- **api** — HTTP layer, calls services, never touches models directly
- **utils** — stateless helpers, imported by anyone
- Each layer has one direction of dependency: api → services → models

</details>

---

<a id="q8"></a>

### Q8 🟡 · Ch5 · `__init__.py` Job 1

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)



**Problem:** Rewrite an `__init__.py` for a `models/` package that re-exports User, Product, Order so callers can do `from myapp.models import User`.

<details>
<summary>💡 Hint</summary>

Without an `__init__.py` re-export, callers must know the internal file structure: `from myapp.models.user import User`. The `__init__.py` hides that detail.

</details>

<details>
<summary>✅ Answer</summary>

```python
# myapp/models/__init__.py

# Re-export public classes — callers don't need to know which file each lives in
from .user import User
from .product import Product
from .order import Order, OrderStatus, OrderItem

# Optional: also expose a list of all model classes for introspection/tooling
__all__ = ["User", "Product", "Order", "OrderStatus", "OrderItem"]
```

**Before (without re-export):**
```python
# caller must know internal structure — fragile
from myapp.models.user import User
from myapp.models.product import Product
from myapp.models.order import Order
```

**After (with re-export):**
```python
# caller sees a clean API — internal structure is hidden
from myapp.models import User, Product, Order
```

**Why this matters:** If you later split `user.py` into `user_model.py` and `user_schema.py`, callers are unaffected. The `__init__.py` is the stable public contract. Internal file layout is an implementation detail.

</details>

---

<a id="q9"></a>

### Q9 🟡 · Ch5 · `__init__.py` Job 2

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)



**Problem:** Add `__all__` to an `__init__.py` to control what `from models import *` exports.

<details>
<summary>💡 Hint</summary>

`__all__` is a list of strings. Only names in this list are exported by `import *`. Names not in `__all__` are still accessible by explicit import.

</details>

<details>
<summary>✅ Answer</summary>

```python
# myapp/models/__init__.py

from .user import User, _UserInternal         # _UserInternal is a private helper
from .product import Product, ProductDraft
from .order import Order, OrderStatus

# __all__ controls what "from myapp.models import *" exports
# Only the public models — not internal helpers or draft objects
__all__ = [
    "User",
    "Product",
    "Order",
    "OrderStatus",
]

# ProductDraft and _UserInternal are NOT in __all__
# "from myapp.models import *" will NOT include them
# But "from myapp.models import ProductDraft" still works explicitly
```

**Demonstration:**

```python
# consumer.py
from myapp.models import *

# Available: User, Product, Order, OrderStatus
# NOT available: ProductDraft, _UserInternal
# (unless explicitly imported)

# This still works:
from myapp.models import ProductDraft   # explicit import ignores __all__
```

**Why:** `__all__` is the package's promise: "these are the public names I support." It protects your users from accidentally depending on internal details.

</details>

---

<a id="q10"></a>

### Q10 🟡 · Ch5 · `__init__.py` Job 3

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)



**Problem:** Add `__version__` and a NullHandler logging setup to a package `__init__.py`.

<details>
<summary>💡 Hint</summary>

Library packages should never configure logging — that's the application's job. Adding a NullHandler prevents "No handlers could be found" warnings.

</details>

<details>
<summary>✅ Answer</summary>

```python
# mylib/__init__.py

import logging

# Job 1: version metadata — queryable at runtime and by package tools
__version__ = "2.4.1"
__author__ = "Your Name"

# Job 2: NullHandler for library logging
# Libraries should NEVER add handlers (StreamHandler, FileHandler, etc.)
# That is the APPLICATION's job.
# NullHandler prevents "No handlers could be found for logger 'mylib'" warnings.
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Job 3: re-export public API
from .core import DataProcessor
from .utils import validate_schema

__all__ = ["DataProcessor", "validate_schema", "__version__"]
```

**Usage by the library's internal code:**

```python
# mylib/core.py
import logging

logger = logging.getLogger(__name__)   # "mylib.core"

class DataProcessor:
    def process(self, data):
        logger.debug("Processing %d records", len(data))
        # ... actual work
```

**Usage by an application:**

```python
# app.py — the APPLICATION configures logging
import logging
logging.basicConfig(level=logging.DEBUG)   # now mylib's debug logs appear

import mylib
proc = mylib.DataProcessor()
```

**Why:** Without `NullHandler`, any application that imports your library but doesn't configure logging will see an ugly warning. `NullHandler` is the "polite library citizen" pattern.

</details>

---

<a id="q11"></a>

### Q11 🟡 · Ch6 · Relative Imports

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)



**Problem:** Inside `myapp/services/user_service.py`, write relative imports for: the sibling `payment.py`, the parent `models/user.py`, and the parent's `utils/validators.py`.

<details>
<summary>💡 Hint</summary>

A single dot (`.`) means "current package." Two dots (`..`) means "parent package." You are in `myapp/services/`, so `..` takes you to `myapp/`.

</details>

<details>
<summary>✅ Answer</summary>

```
myapp/
├── models/
│   └── user.py          ← User class lives here
├── services/
│   ├── user_service.py  ← WE ARE HERE
│   └── payment.py       ← sibling
└── utils/
    └── validators.py    ← cousin
```

```python
# myapp/services/user_service.py

# Sibling import: payment.py is in the same package (services/)
# Single dot = current package (myapp.services)
from . import payment
from .payment import process_payment

# Parent package import: models/user.py is in myapp/
# Double dot = parent package (myapp)
from ..models.user import User
from ..models import User    # same thing, via __init__.py re-export

# Cousin import: utils/validators.py is in myapp/utils/
# Double dot = parent (myapp), then navigate to utils/
from ..utils.validators import validate_email, validate_phone
```

**Why relative over absolute here?**

```python
# Absolute also works:
from myapp.models.user import User
from myapp.utils.validators import validate_email

# Relative is better when:
# 1. The package might be renamed (myapp → my_service)
# 2. You want to make clear this is an internal dependency
# 3. The import moves with the file if you reorganize
```

**Rule:** Use relative imports within a package. Use absolute imports for external packages and when the code might be run as a script.

</details>

---

<a id="q12"></a>

### Q12 🟡 · Ch7 · `__name__` Guard

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)



**Problem:** Explain why `if __name__ == "__main__":` is important. What happens without it when the file is imported?

<details>
<summary>💡 Hint</summary>

When Python imports a file, it runs all top-level code. What should happen when you `import utils` vs when you run `python utils.py` directly?

</details>

<details>
<summary>✅ Answer</summary>

**How `__name__` works:**

```python
# demo.py
print(f"__name__ is: {__name__}")
```

```bash
python demo.py          # prints: __name__ is: __main__
python -c "import demo" # prints: __name__ is: demo
```

When run directly: `__name__ == "__main__"`
When imported: `__name__ == "demo"` (the module name)

**Without the guard:**

```python
# dangerous_utils.py — NO guard
def helper():
    return 42

# This runs every time the file is imported:
print("Running setup...")
result = expensive_computation()   # runs on import!
send_email("ready@example.com")    # sends email on every import!
```

```python
# main.py
import dangerous_utils   # triggers all that code — BAD
```

**With the guard:**

```python
# safe_utils.py
def helper():
    return 42

def main():
    print("Running setup...")
    result = expensive_computation()

if __name__ == "__main__":
    main()   # only runs when executed directly, never on import
```

```python
import safe_utils      # clean: nothing executes, only functions are defined
safe_utils.helper()    # works fine
```

**Why:** The guard separates "define things" (always runs, safe) from "do things" (should only run when intentionally executed). It's the most fundamental Python idiom for reusable code.

</details>

---

<a id="q13"></a>

### Q13 🟡 · Ch7 · Dual-Use File

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)



**Problem:** Write a `calculator.py` that is both importable (exposes `add`, `subtract`) and runnable as a CLI script.

<details>
<summary>💡 Hint</summary>

The functions should be defined at module level. The CLI argument parsing and print statements go inside `if __name__ == "__main__":`.

</details>

<details>
<summary>✅ Answer</summary>

```python
# calculator.py

import sys


def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def main():
    """CLI entry point."""
    if len(sys.argv) != 4:
        print("Usage: python calculator.py <a> <op> <b>")
        print("  ops: add subtract multiply divide")
        sys.exit(1)

    a = float(sys.argv[1])
    op = sys.argv[2]
    b = float(sys.argv[3])

    ops = {
        "add": add,
        "subtract": subtract,
        "multiply": multiply,
        "divide": divide,
    }

    if op not in ops:
        print(f"Unknown operation: {op}")
        sys.exit(1)

    result = ops[op](a, b)
    print(f"{a} {op} {b} = {result}")


if __name__ == "__main__":
    main()
```

**As a module:**

```python
from calculator import add, subtract, multiply

total = add(10, 5)      # 15
diff = subtract(10, 5)  # 5
```

**As a CLI:**

```bash
python calculator.py 10 add 5        # 10.0 add 5.0 = 15.0
python calculator.py 20 divide 4     # 20.0 divide 4.0 = 5.0
python calculator.py 10 divide 0     # ValueError: Cannot divide by zero
```

</details>

---

<a id="q14"></a>

### Q14 🟡 · Ch8 · Circular Import

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)



**Problem:** Explain why `a.py imports b` and `b.py imports a` causes an `ImportError`. What does the error message say?

<details>
<summary>💡 Hint</summary>

Remember: Python registers a module in `sys.modules` before executing its code. What does `b.py` find when it tries to import `a` while `a` is still being executed?

</details>

<details>
<summary>✅ Answer</summary>

```python
# a.py
from b import B_VALUE   # triggers b.py to execute

A_VALUE = 10
```

```python
# b.py
from a import A_VALUE   # tries to import a — but a is still loading!

B_VALUE = 20
```

**Execution trace:**

```
1. Python starts executing a.py
2. Registers sys.modules["a"] = <partially initialized module>
3. Hits "from b import B_VALUE" — starts executing b.py
4. b.py hits "from a import A_VALUE"
5. Python checks sys.modules["a"] — found! (partially initialized)
6. BUT: A_VALUE hasn't been defined yet (a.py is still on line 1)
7. ImportError: cannot import name 'A_VALUE' from partially initialized module 'a'
```

**The error:**

```
ImportError: cannot import name 'A_VALUE' from partially initialized module 'a'
(most likely due to a circular import)
```

Or in some cases:

```
ImportError: cannot import name 'A_VALUE' from 'a' (/path/to/a.py)
```

**Key insight:** The module object exists in `sys.modules`, but it's empty — none of the names have been defined yet because execution hasn't finished. When `b.py` tries to access `A_VALUE`, it doesn't exist yet in the module object.

</details>

---

<a id="q15"></a>

### Q15 🟡 · Ch8 · Fix Circular

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)



**Problem:** Show all 3 ways to fix a circular import. Which one fixes the root design problem?

<details>
<summary>💡 Hint</summary>

The 3 fixes are: deferred import inside function, import the module (not names from it), and extract shared code to a third module. Only one addresses why the circle exists.

</details>

<details>
<summary>✅ Answer</summary>

**The problem:**

```python
# user.py
from order import Order   # circular!
class User:
    def get_orders(self): return Order.for_user(self)

# order.py
from user import User     # circular!
class Order:
    def get_user(self): return User.find(self.user_id)
```

---

**Fix 1: Deferred import (inside function)**

```python
# user.py
class User:
    def get_orders(self):
        from order import Order   # import at call time, not module load time
        return Order.for_user(self)
```

Works, but it's a band-aid. Import happens on every call (cached after first, so fast). Hides the architectural smell.

---

**Fix 2: Import the module, not names from it**

```python
# user.py
import order   # import the module object (always safe)

class User:
    def get_orders(self):
        return order.Order.for_user(self)   # access attribute at call time
```

Works because `import order` just registers the module object. Accessing `order.Order` happens later when the attribute exists.

---

**Fix 3: Extract shared code to a third module (fixes the root problem)**

```python
# base.py  ← new module with no dependencies
class UserBase:
    user_id: int
    name: str

class OrderBase:
    order_id: int
    user_id: int

# user.py
from base import UserBase
from order import Order

class User(UserBase):
    def get_orders(self): return Order.for_user(self)

# order.py
from base import OrderBase
from user import User

class Order(OrderBase):
    def get_user(self): return User.find(self.user_id)
```

Or better: use dependency injection instead of direct imports between peer modules.

---

**Which fixes the root problem?**

Fix 3. Circular imports are a symptom of **tangled dependencies** — two modules knowing too much about each other. The real fix is to restructure: extract shared types/interfaces to a base module, or redesign so the dependency flows one direction.

```
BAD:  user <---> order  (circular)
GOOD: base <--- user
      base <--- order   (both depend on base, not each other)
```

</details>

---

<a id="q16"></a>

### Q16 🟡 · Ch9 · `__all__`

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)



**Problem:** Write a `validators.py` with `__all__` that exports only public validators and hides 3 private helper functions.

<details>
<summary>💡 Hint</summary>

`__all__` is a list of strings. Functions named with a leading underscore are conventionally private, but `__all__` is the authoritative control for star imports.

</details>

<details>
<summary>✅ Answer</summary>

```python
# validators.py

import re

# __all__ declares the public API for this module
# Only these names are exported by "from validators import *"
__all__ = [
    "validate_email",
    "validate_phone",
    "validate_username",
    "ValidationError",
]


class ValidationError(ValueError):
    """Raised when validation fails."""
    pass


# ── Public validators ─────────────────────────────────────────────────────────

def validate_email(value: str) -> str:
    """Validate and normalize an email address."""
    value = value.strip().lower()
    if not _is_valid_email_format(value):
        raise ValidationError(f"Invalid email: {value!r}")
    if not _has_valid_domain(value):
        raise ValidationError(f"Invalid email domain: {value!r}")
    return value


def validate_phone(value: str) -> str:
    """Validate and normalize a phone number."""
    normalized = _strip_phone_formatting(value)
    if not _is_valid_phone_length(normalized):
        raise ValidationError(f"Invalid phone number: {value!r}")
    return normalized


def validate_username(value: str) -> str:
    """Validate a username (3-32 chars, alphanumeric + underscore)."""
    value = value.strip()
    if not re.match(r"^[a-zA-Z0-9_]{3,32}$", value):
        raise ValidationError(f"Invalid username: {value!r}")
    return value


# ── Private helpers (NOT in __all__) ─────────────────────────────────────────
# These are implementation details. Callers should not depend on them.

def _is_valid_email_format(email: str) -> bool:
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", email))


def _has_valid_domain(email: str) -> bool:
    domain = email.split("@")[1]
    return "." in domain and len(domain) > 3


def _strip_phone_formatting(phone: str) -> str:
    return re.sub(r"[\s\-\(\)\+]", "", phone)


def _is_valid_phone_length(digits: str) -> bool:
    return 10 <= len(digits) <= 15
```

**Result:**

```python
from validators import *
# Available: validate_email, validate_phone, validate_username, ValidationError
# NOT available: _is_valid_email_format, _has_valid_domain, etc.

# But explicit import still works:
from validators import _strip_phone_formatting   # works, just unconventional
```

</details>

---

<a id="q17"></a>

### Q17 🟡 · Ch9 · Without `__all__`

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)



**Problem:** If a module has no `__all__`, what does `from module import *` export?

<details>
<summary>💡 Hint</summary>

Python falls back to a naming convention. What does the underscore prefix mean for export behavior?

</details>

<details>
<summary>✅ Answer</summary>

**Without `__all__`, star import exports all names that don't start with an underscore:**

```python
# colors.py — no __all__

RED = "#FF0000"
GREEN = "#00FF00"
BLUE = "#0000FF"

_internal_cache = {}      # underscore prefix = NOT exported
__dunder__ = "skip me"    # dunder = NOT exported

def mix(c1, c2):
    return f"{c1}+{c2}"

def _validate(color):     # underscore = NOT exported
    return color.startswith("#")
```

```python
from colors import *

# Available: RED, GREEN, BLUE, mix
# NOT available: _internal_cache, _validate, __dunder__

print(dir())   # ['BLUE', 'GREEN', 'RED', 'mix', ...]
```

**The rule:**

```
With __all__:     exports exactly what __all__ lists
Without __all__:  exports everything that does NOT start with _
```

**Why this matters:**

The underscore convention is informal and accidental. Without `__all__`, you might export names you didn't intend to — for example, names imported from other modules:

```python
# utils.py — no __all__
import os                          # "os" is now a name in this module
from datetime import datetime      # "datetime" is now a name here

def my_function():
    pass
```

```python
from utils import *
# Exports: os, datetime, my_function  ← you probably didn't want os and datetime!
```

`__all__` prevents this "accidental re-export" problem.

</details>

---

<a id="q18"></a>

### Q18 🟡 · Ch10 · importlib

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)



**Problem:** Use `importlib.import_module()` to load a module by string name. When would you need this over a regular import?

<details>
<summary>💡 Hint</summary>

Regular imports require you to know the module name at write time. What if the module name only exists at runtime — for example, read from a config file or command-line argument?

</details>

<details>
<summary>✅ Answer</summary>

```python
import importlib

# Basic usage: load a module by string name
math = importlib.import_module("math")
print(math.sqrt(16))   # 4.0

# Load a submodule
json_encoder = importlib.import_module("json.encoder")
print(json_encoder.JSONEncoder)

# With package context (relative-style)
# Load "myapp.models.user" as if from inside "myapp"
user_mod = importlib.import_module(".models.user", package="myapp")
```

**When you need this:**

```python
# 1. Module name comes from config/environment
import importlib
import os

backend_name = os.environ.get("CACHE_BACKEND", "redis_backend")
cache_module = importlib.import_module(f"myapp.backends.{backend_name}")
cache = cache_module.CacheBackend()

# 2. Module name comes from user input or CLI
plugin_name = input("Enter plugin name: ")
plugin = importlib.import_module(f"myapp.plugins.{plugin_name}")

# 3. Lazy conditional loading (avoid ImportError if package not installed)
try:
    ujson = importlib.import_module("ujson")
    loads = ujson.loads
except ImportError:
    import json
    loads = json.loads

# 4. Framework plugin discovery
def load_handler(dotted_path: str):
    """Load 'myapp.handlers.csv_handler.CSVHandler' from a string."""
    module_path, class_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)

handler_class = load_handler("myapp.handlers.csv_handler.CSVHandler")
handler = handler_class()
```

**Rule:** If the module name is known at write time, use a regular import. If the module name is determined at runtime, use `importlib.import_module()`.

</details>

---

<a id="q19"></a>

### Q19 🟡 · Ch10 · Plugin Registry

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)



**Problem:** Write a `register_plugin(name, module_path, class_name)` function that loads a plugin class dynamically.

<details>
<summary>💡 Hint</summary>

You need `importlib.import_module()` to load the module from a string, then `getattr()` to get the class from the module.

</details>

<details>
<summary>✅ Answer</summary>

```python
# plugin_registry.py
import importlib
from typing import Any

# The registry: maps plugin name → class
_registry: dict[str, type] = {}


def register_plugin(name: str, module_path: str, class_name: str) -> None:
    """
    Load a plugin class and register it.

    Args:
        name:        friendly name ("csv_parser")
        module_path: dotted module path ("myapp.plugins.csv_parser")
        class_name:  class name inside the module ("CSVParser")
    """
    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        raise ImportError(f"Cannot load plugin '{name}': {e}") from e

    if not hasattr(module, class_name):
        raise AttributeError(
            f"Module '{module_path}' has no class '{class_name}'"
        )

    cls = getattr(module, class_name)
    _registry[name] = cls
    print(f"Registered plugin '{name}' → {module_path}.{class_name}")


def get_plugin(name: str) -> type:
    """Retrieve a registered plugin class by name."""
    if name not in _registry:
        raise KeyError(f"Plugin '{name}' not registered. Available: {list(_registry)}")
    return _registry[name]


def list_plugins() -> list[str]:
    """Return names of all registered plugins."""
    return list(_registry.keys())


# ── Usage ──────────────────────────────────────────────────────────────────────

# config.yaml might specify:
# plugins:
#   - name: csv_parser
#     module: myapp.plugins.csv_parser
#     class: CSVParser

plugins_config = [
    ("csv_parser",  "myapp.plugins.csv_parser",  "CSVParser"),
    ("json_parser", "myapp.plugins.json_parser", "JSONParser"),
]

for name, mod, cls in plugins_config:
    register_plugin(name, mod, cls)

# Later: use a plugin by name
ParserClass = get_plugin("csv_parser")
parser = ParserClass()
result = parser.parse("data.csv")
```

**Why:** This pattern powers every major framework's extension system — Django apps, Flask extensions, Airflow operators, pytest plugins. The key insight is separating the registry (which names exist) from the loader (loading on demand).

</details>

---

<a id="q20"></a>

### Q20 🟡 · Ch11 · Lazy Import

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)



**Problem:** Rewrite a top-level `import pandas as pd` as a lazy import inside the function that uses it. Why does this help CLI startup time?

<details>
<summary>💡 Hint</summary>

pandas takes ~200ms to import. If your CLI tool has 10 commands and only one uses pandas, you're paying that cost even for commands that don't need it.

</details>

<details>
<summary>✅ Answer</summary>

**Before (eager import):**

```python
# data_tool.py
import pandas as pd   # 200ms — always runs, even for --help

def analyze(filepath: str):
    df = pd.read_csv(filepath)
    return df.describe()

def greet(name: str):
    return f"Hello, {name}"
```

```bash
python data_tool.py greet Alice   # spends 200ms loading pandas for no reason
python data_tool.py --help        # same, 200ms wasted
```

**After (lazy import):**

```python
# data_tool.py

def analyze(filepath: str):
    import pandas as pd   # only loads when analyze() is actually called
    df = pd.read_csv(filepath)
    return df.describe()

def greet(name: str):
    return f"Hello, {name}"
```

```bash
python data_tool.py greet Alice   # instant: pandas never loaded
python data_tool.py analyze data.csv   # 200ms here, but that's acceptable
```

**Why it works:** The first call to `analyze()` triggers the import and caches it in `sys.modules`. Every subsequent call gets the cached module — the slow path only runs once, and only when actually needed.

**Real-world impact:**

```
CLI tool with 15 commands:
- 14 commands: instant (pandas not needed)
- 1 command: 200ms startup (pandas loaded once, then cached)

vs eager:
- All 15 commands: 200ms startup (pandas always loaded)
```

For tools like `pip`, `aws-cli`, or `kubectl`-style tools, lazy imports are essential for a snappy user experience.

</details>

---

<a id="q21"></a>

### Q21 🟡 · Ch11 · Class-Level Lazy

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)



**Problem:** Write a `DataProcessor` class that imports numpy lazily on first use and caches it as a class attribute.

<details>
<summary>💡 Hint</summary>

Store the module reference in a class attribute (e.g., `_np = None`). Check for it in methods that need it. Use a class method or property to implement the one-time load.

</details>

<details>
<summary>✅ Answer</summary>

```python
# data_processor.py

class DataProcessor:
    """Processes numerical data using numpy — loaded lazily on first use."""

    _np = None   # class-level cache: None means "not loaded yet"

    @classmethod
    def _get_np(cls):
        """Load numpy once and cache it. All instances share this."""
        if cls._np is None:
            import numpy as np
            cls._np = np
        return cls._np

    def normalize(self, data: list[float]) -> list[float]:
        """Normalize values to [0, 1] range."""
        np = self._get_np()
        arr = np.array(data)
        min_val, max_val = arr.min(), arr.max()
        if max_val == min_val:
            return [0.0] * len(data)
        return ((arr - min_val) / (max_val - min_val)).tolist()

    def mean(self, data: list[float]) -> float:
        """Compute mean of a list."""
        np = self._get_np()
        return float(np.mean(data))

    def std(self, data: list[float]) -> float:
        """Compute standard deviation."""
        np = self._get_np()
        return float(np.std(data))
```

**Usage:**

```python
# Instantiation is instant — numpy not loaded yet
proc = DataProcessor()

# First call loads numpy (slow once), caches it
result = proc.normalize([1, 2, 3, 4, 5])   # numpy loaded here

# Second call uses cache — fast
mean = proc.mean([1, 2, 3, 4, 5])           # instant, _np already set

# Multiple instances share the class-level cache
proc2 = DataProcessor()
mean2 = proc2.mean([10, 20, 30])            # instant, cache shared
```

**Why class attribute over instance attribute:**

```python
# If you used self._np = None on each instance:
# - Each new DataProcessor() would have its own _np
# - The cache only prevents reloading within one instance
# - Multiple instances would each trigger the import check

# Class attribute: one import, shared by all instances of the class
```

</details>

---

<a id="q22"></a>

### Q22 🟡 · Ch12 · Project Layout

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)



**Problem:** What is the difference between a "flat layout" and "src layout" for a Python project? When would you use src layout?

<details>
<summary>💡 Hint</summary>

In flat layout, the package is at the root. In src layout, it's nested inside a `src/` directory. The difference matters when running tests and building distributions.

</details>

<details>
<summary>✅ Answer</summary>

**Flat layout:**

```
myproject/
├── mylib/             ← package is at root
│   ├── __init__.py
│   └── core.py
├── tests/
│   └── test_core.py
├── pyproject.toml
└── README.md
```

**Src layout:**

```
myproject/
├── src/
│   └── mylib/         ← package is inside src/
│       ├── __init__.py
│       └── core.py
├── tests/
│   └── test_core.py
├── pyproject.toml
└── README.md
```

**The critical difference — import behavior during testing:**

```bash
# Flat layout: mylib/ is in the current directory
# Python adds "." to sys.path automatically
# "import mylib" finds the SOURCE CODE directly
# → you might be testing uninstalled code without knowing it

# Src layout: mylib/ is inside src/, NOT in sys.path by default
# "import mylib" only works if the package is installed (pip install -e .)
# → you always test the INSTALLED package, which matches what users get
```

**When to use src layout:**

1. Building a library/package for distribution (PyPI, internal pip)
2. You want `pip install -e .` to be the only way to import your code
3. You want to catch "works locally, fails when installed" bugs early
4. CI/CD pipelines that build and install before testing

**When flat layout is fine:**

1. Applications (not libraries) that aren't distributed as packages
2. Small projects where packaging isn't a concern
3. Scripts and data science notebooks

```bash
# Src layout workflow:
pip install -e .          # install in editable mode
pytest tests/             # tests import the installed package
```

</details>

---

<a id="q23"></a>

### Q23 🟡 · Ch13 · venv Creation

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)



**Problem:** Write the command sequence to create, activate, install deps, and freeze a virtual environment.

<details>
<summary>💡 Hint</summary>

Creation, activation, installation, and freezing are 4 separate steps. Activation differs between Unix and Windows.

</details>

<details>
<summary>✅ Answer</summary>

```bash
# Step 1: Create the virtual environment
# Convention: name it .venv (hidden in file listings)
python -m venv .venv

# Step 2: Activate (Unix/macOS)
source .venv/bin/activate

# Step 2: Activate (Windows)
.venv\Scripts\activate

# You'll see the prompt change:
# (.venv) $ ...

# Step 3: Upgrade pip (good habit — avoid old pip warnings)
pip install --upgrade pip

# Step 4: Install dependencies
pip install flask sqlalchemy pytest

# OR from a requirements file:
pip install -r requirements.txt

# Step 5: Verify what's installed
pip list
pip show flask

# Step 6: Freeze installed packages to requirements.txt
pip freeze > requirements.txt

# Step 7: Deactivate when done
deactivate
```

**What the files look like:**

```
myproject/
├── .venv/                  # virtual environment (add to .gitignore)
│   ├── bin/python          # project-local Python
│   ├── bin/pip             # project-local pip
│   └── lib/python3.11/     # installed packages
├── requirements.txt        # pinned deps (commit this)
└── requirements-dev.txt    # dev-only deps: pytest, black, mypy
```

**Best practices:**

```bash
# Always add .venv to .gitignore
echo ".venv/" >> .gitignore

# Separate runtime and dev requirements
pip install flask sqlalchemy          # runtime
pip install pytest black mypy         # dev only

pip freeze | grep -E "flask|sqlalchemy" > requirements.txt
pip freeze | grep -E "pytest|black|mypy" > requirements-dev.txt

# Install dev environment:
pip install -r requirements.txt -r requirements-dev.txt
```

</details>

---

<a id="q24"></a>

### Q24 🟡 · Ch13 · Why venv

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)



**Problem:** Two projects need different versions of Django. Without venv, what breaks? With venv, how is it solved?

<details>
<summary>💡 Hint</summary>

Python can only have one version of any package installed globally at a time. What happens when project A needs Django 3.2 and project B needs Django 4.2?

</details>

<details>
<summary>✅ Answer</summary>

**Without venv — the dependency conflict:**

```bash
# Global Python installation
pip install django==3.2    # project-alpha needs this

# Later...
pip install django==4.2    # project-beta needs this
# → pip UNINSTALLS django 3.2 and installs 4.2

# Now project-alpha is broken silently
cd project-alpha
python manage.py runserver
# ERROR: Your Django version (4.2) is not compatible...
# Or worse: silent behavior changes, no error at all
```

**The root problem:**

```
/usr/local/lib/python3.11/site-packages/
└── django/   ← only ONE django can live here
```

Python has one global site-packages directory. Only one version of any package can be installed at a time. Installing for one project breaks the other.

**With venv — isolated environments:**

```bash
# Project Alpha
cd project-alpha
python -m venv .venv
source .venv/bin/activate
pip install django==3.2     # lives in project-alpha/.venv/

# Project Beta
cd project-beta
python -m venv .venv
source .venv/bin/activate
pip install django==4.2     # lives in project-beta/.venv/
```

```
project-alpha/.venv/lib/site-packages/django/  ← Django 3.2
project-beta/.venv/lib/site-packages/django/   ← Django 4.2
```

Each project has its own `site-packages` directory. They never interact. Installing for one project has zero effect on the other.

**Real consequences of not using venv:**
- CI/CD builds fail when order of `pip install` matters
- "Works on my machine" bugs from version mismatches
- Upgrading for one project silently breaks another
- Impossible to reproduce exact environments across machines

</details>

---

<a id="q25"></a>

### Q25 🟡 · Ch14 · sys.path Order

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)



**Problem:** What is the search order in `sys.path`? What happens if you have a `math.py` file in your current directory?

<details>
<summary>💡 Hint</summary>

Python searches `sys.path` from first to last. The first match wins. What is the first entry in `sys.path`?

</details>

<details>
<summary>✅ Answer</summary>

```python
import sys
print(sys.path)
# ['', '/usr/lib/python311.zip', '/usr/lib/python3.11',
#  '/usr/lib/python3.11/lib-dynload',
#  '/home/user/.venv/lib/python3.11/site-packages']
```

**Search order (first match wins):**

```
1. '' (empty string) = current working directory
   OR the directory containing the script being run

2. PYTHONPATH environment variable entries
   (user-defined paths, in order listed)

3. Standard library directories
   /usr/lib/python3.11/
   /usr/lib/python3.11/lib-dynload/

4. Site-packages (third-party installed packages)
   .venv/lib/python3.11/site-packages/
   /usr/local/lib/python3.11/site-packages/
```

**What happens with a local `math.py`:**

```bash
echo "PI = 999" > math.py
```

```python
import math
print(math.pi)   # AttributeError: module 'math' has no attribute 'pi'
print(math.PI)   # 999  ← your file, not the standard library!
```

The current directory (`''`) is searched FIRST. Your `math.py` shadows the standard library `math` module completely.

**Common accidental shadows:**

```bash
# Files that shadow stdlib modules:
math.py        # shadows math
string.py      # shadows string
os.py          # shadows os — very dangerous
json.py        # shadows json
test.py        # shadows some test infrastructure
```

**Fix:** Never name your files the same as stdlib or popular third-party packages. Check for conflicts:

```python
import sys
import math
print(math.__file__)   # shows which math.py Python is actually using
```

</details>

---

<a id="q26"></a>

### Q26 🟡 · Ch14 · Modify sys.path

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)



**Problem:** Show two ways to add a custom directory to `sys.path`. Which is the "better" production approach and why?

<details>
<summary>💡 Hint</summary>

One way modifies `sys.path` in Python code. The other uses a `.pth` file or the `PYTHONPATH` environment variable. Think about maintainability and portability.

</details>

<details>
<summary>✅ Answer</summary>

**Way 1: Modify sys.path in Python code**

```python
# Prepend (search first) — use when you want to override installed packages
import sys
sys.path.insert(0, "/path/to/my/libs")

# Append (search last) — use when your code is a fallback
sys.path.append("/path/to/my/libs")

import my_custom_module   # now found in /path/to/my/libs
```

**Way 2: .pth file in site-packages**

```bash
# Find site-packages location
python -m site --user-site    # user site-packages
python -c "import site; print(site.getsitepackages())"

# Create a .pth file there
echo "/path/to/my/libs" > $(python -c "import site; print(site.getsitepackages()[0])")/mylibs.pth
```

Python automatically reads all `.pth` files in site-packages at startup and adds their paths to `sys.path`.

**Bonus: PYTHONPATH environment variable**

```bash
# Unix
export PYTHONPATH="/path/to/my/libs:$PYTHONPATH"
python my_script.py

# Windows
set PYTHONPATH=C:\path\to\my\libs
```

---

**Which is better for production?**

**Avoid `sys.path.insert()` in production code.** It's fragile for these reasons:

1. The path is hardcoded — breaks when you move the project
2. Order-dependent — inserting at 0 can shadow stdlib modules
3. Invisible — someone reading your imports can't tell where the module comes from
4. Doesn't survive packaging — breaks if code is installed as a package

**Better approaches for production:**

```bash
# Best: install your package properly
pip install -e .        # editable install during development
pip install .           # real install for production

# Second best: .pth file (set-it-once, no code changes)
# Third: PYTHONPATH env var (good for containerized/K8s deployments)
```

```python
# In Dockerfiles:
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

# In K8s manifests:
env:
  - name: PYTHONPATH
    value: /app/src
```

</details>

---

<a id="q27"></a>

### Q27 🟠 · Ch8+Ch10 · Safe Optional Import

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)



**Problem:** Write a `try_import(name)` function that returns the module or `None` if not installed. Show the feature detection pattern.

<details>
<summary>💡 Hint</summary>

Use `importlib.import_module()` inside a try/except. The feature detection pattern checks the result before using it — similar to checking if a command exists before running it.

</details>

<details>
<summary>✅ Answer</summary>

```python
# optional_deps.py
import importlib
from types import ModuleType


def try_import(name: str) -> ModuleType | None:
    """
    Attempt to import a module. Return None if not installed.

    Usage:
        pd = try_import("pandas")
        if pd:
            df = pd.DataFrame(...)
    """
    try:
        return importlib.import_module(name)
    except ImportError:
        return None


# ── Feature detection pattern ─────────────────────────────────────────────────

# Load optional dependencies once at module level
pd = try_import("pandas")
np = try_import("numpy")
ujson = try_import("ujson")


def load_data(filepath: str):
    """Load data — uses pandas if available, falls back to csv module."""
    if pd is not None:
        return pd.read_csv(filepath)
    else:
        import csv
        with open(filepath) as f:
            return list(csv.DictReader(f))


def fast_json_loads(text: str):
    """Parse JSON — uses ujson if available (10x faster), falls back to stdlib."""
    if ujson is not None:
        return ujson.loads(text)
    import json
    return json.loads(text)


def compute_mean(values: list[float]) -> float:
    """Compute mean — uses numpy if available, falls back to pure Python."""
    if np is not None:
        return float(np.mean(values))
    return sum(values) / len(values)


# ── Informative errors (better UX than AttributeError on None) ────────────────

def require_pandas():
    """Raise a helpful error if pandas is not installed."""
    if pd is None:
        raise ImportError(
            "pandas is required for this operation. "
            "Install it with: pip install pandas"
        )
    return pd


def analyze(filepath: str):
    """Analyze data file — requires pandas."""
    pandas = require_pandas()
    df = pandas.read_csv(filepath)
    return df.describe()
```

**Why:** This pattern is used extensively in production libraries:
- `requests` has optional `chardet` for encoding detection
- `sqlalchemy` has optional database drivers
- `pydantic` has optional `email-validator` for email fields

The key: fail gracefully with a helpful message, never with `AttributeError: 'NoneType' has no attribute 'read_csv'`.

</details>

---

<a id="q28"></a>

### Q28 🟠 · Ch5+Ch9 · API Design

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)



**Problem:** You are building a `mylib` package. Write the `__init__.py` that exposes a clean public API with `__all__`, `__version__`, and proper logging setup.

<details>
<summary>💡 Hint</summary>

Combine the 3 jobs of `__init__.py`: re-export public API, declare `__all__`, set `__version__`, and add `NullHandler`. The goal is that callers only need `from mylib import X`.

</details>

<details>
<summary>✅ Answer</summary>

```python
# mylib/__init__.py
"""
mylib — A data processing library.

Public API:
    DataPipeline  — build and run data transformation pipelines
    DataSource    — connect to various data sources
    Transform     — built-in transformation functions
    PipelineError — base exception for all mylib errors

Example:
    from mylib import DataPipeline, DataSource
    pipeline = DataPipeline(DataSource.from_csv("data.csv"))
    result = pipeline.run()
"""

import logging

# ── Package metadata ───────────────────────────────────────────────────────────
__version__ = "1.3.0"
__author__ = "Your Team"
__license__ = "MIT"

# ── Library logging: NullHandler prevents "no handlers" warnings ───────────────
# Applications configure their own logging; libraries never configure handlers.
logging.getLogger(__name__).addHandler(logging.NullHandler())

# ── Public API: re-export from internal modules ────────────────────────────────
# Callers use: from mylib import DataPipeline
# NOT:         from mylib.core.pipeline import DataPipeline

from .core.pipeline import DataPipeline
from .core.source import DataSource
from .transforms import Transform
from .exceptions import PipelineError, SourceError, TransformError

# ── __all__: authoritative declaration of the public API ──────────────────────
# Controls "from mylib import *"
# Documents intent: "these are the names we support and version with"
__all__ = [
    # Main classes
    "DataPipeline",
    "DataSource",
    "Transform",
    # Exceptions
    "PipelineError",
    "SourceError",
    "TransformError",
    # Metadata
    "__version__",
]
```

**What callers see:**

```python
# Clean, stable API regardless of internal file structure
from mylib import DataPipeline, DataSource, Transform
from mylib import PipelineError

# Version check
import mylib
print(mylib.__version__)   # "1.3.0"

# Star import is safe — __all__ controls exactly what comes in
from mylib import *
# Gets: DataPipeline, DataSource, Transform, PipelineError, SourceError,
#       TransformError, __version__
# Does NOT get: logging, internal helpers, submodule references
```

**The contract:** The names in `__all__` are the stable public API. Internal structure (which file each class lives in) is an implementation detail. Callers are insulated from internal refactoring.

</details>

---

<a id="q29"></a>

### Q29 🟠 · Ch15 · Namespace Packages

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)



**Problem:** What is a namespace package? How does it differ from a regular package? Give a real-world use case.

<details>
<summary>💡 Hint</summary>

Namespace packages (PEP 420) exist without an `__init__.py`. They allow a single package namespace to span multiple directories or even multiple installed distributions.

</details>

<details>
<summary>✅ Answer</summary>

**Regular package:** requires `__init__.py`, one directory, one location on disk.

**Namespace package:** no `__init__.py` required, can span multiple directories across `sys.path`.

```
# Regular package:
myapp/
├── __init__.py   ← required
└── core.py

# Namespace package:
myapp/            ← NO __init__.py
└── core.py       ← Python 3.3+ treats this as a namespace package
```

**How Python finds namespace packages:**

```python
# sys.path = ["/project_a", "/project_b"]

# /project_a/acme/billing.py
# /project_b/acme/shipping.py
# Neither /project_a/acme/ nor /project_b/acme/ has __init__.py

import acme.billing    # found in /project_a/acme/billing.py
import acme.shipping   # found in /project_b/acme/shipping.py

# Both work under the "acme" namespace — even though they're in different directories!
```

**Real-world use case: Plugin systems and monorepo namespaces**

```
# Company "acme" distributes separate pip packages:
# pip install acme-core
# pip install acme-billing
# pip install acme-analytics

# But all use the "acme" namespace:
site-packages/
├── acme/                  ← no __init__.py in any of them
│   ├── core/              ← from acme-core package
│   │   └── client.py
│   ├── billing/           ← from acme-billing package
│   │   └── invoice.py
│   └── analytics/         ← from acme-analytics package
│       └── reports.py
```

```python
# User installs only what they need:
pip install acme-core acme-billing

from acme.core import Client
from acme.billing import Invoice
# from acme.analytics import Report  ← ImportError: not installed
```

**Key differences:**

| | Regular Package | Namespace Package |
|---|---|---|
| `__init__.py` | Required | Not present |
| Location | Single directory | Can span multiple directories |
| Use case | Standard apps | Plugin systems, split packages |
| `__path__` | `['/path/to/pkg']` | List of all matching directories |
| `__init__.py` code | Runs on import | Nothing to run |

</details>

---

<a id="q30"></a>

### Q30 🟠 · Capstone

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)



**Problem:** Design the complete package structure for a data pipeline application with: ingestion, transformation, storage, API, and CLI layers. Write the directory tree, one `__init__.py`, and the main entry point.

<details>
<summary>💡 Hint</summary>

Think in layers: each layer depends only on layers below it. CLI and API are at the top (both depend on pipeline logic). Storage is at the bottom. Ingestion and transformation are in the middle.

</details>

<details>
<summary>✅ Answer</summary>

**Directory tree:**

```
datapipe/                          # project root (src layout)
├── src/
│   └── datapipe/                  # the package
│       ├── __init__.py            # public API, version, logging
│       │
│       ├── ingestion/             # data sources: read raw data
│       │   ├── __init__.py
│       │   ├── base.py            # BaseIngester ABC
│       │   ├── csv_ingester.py    # CSVIngester
│       │   ├── s3_ingester.py     # S3Ingester
│       │   └── db_ingester.py     # DatabaseIngester
│       │
│       ├── transform/             # data transformations: clean, reshape
│       │   ├── __init__.py
│       │   ├── base.py            # BaseTransform ABC
│       │   ├── clean.py           # NullDropper, TypeCaster
│       │   ├── aggregate.py       # Grouper, Pivot
│       │   └── pipeline.py        # TransformPipeline (chain transforms)
│       │
│       ├── storage/               # data sinks: write processed data
│       │   ├── __init__.py
│       │   ├── base.py            # BaseStorage ABC
│       │   ├── parquet.py         # ParquetWriter
│       │   ├── postgres.py        # PostgresWriter
│       │   └── s3.py              # S3Writer
│       │
│       ├── api/                   # HTTP API: expose pipeline operations
│       │   ├── __init__.py
│       │   ├── app.py             # FastAPI app factory
│       │   ├── routes/
│       │   │   ├── __init__.py
│       │   │   ├── pipelines.py   # POST /pipelines, GET /pipelines/{id}
│       │   │   └── jobs.py        # POST /jobs/run, GET /jobs/{id}/status
│       │   └── middleware.py      # auth, request logging
│       │
│       ├── cli/                   # CLI: run pipelines from terminal
│       │   ├── __init__.py
│       │   └── commands.py        # click commands: run, list, status
│       │
│       ├── models/                # shared data models (no business logic)
│       │   ├── __init__.py
│       │   ├── pipeline.py        # PipelineConfig, PipelineResult
│       │   └── job.py             # Job, JobStatus
│       │
│       └── config.py              # environment-based configuration
│
├── tests/
│   ├── test_ingestion.py
│   ├── test_transform.py
│   ├── test_storage.py
│   └── test_api.py
│
├── pyproject.toml                 # packaging + dependencies
└── README.md
```

**`datapipe/__init__.py`:**

```python
# src/datapipe/__init__.py
"""
datapipe — A composable data pipeline framework.

Quick start:
    from datapipe import Pipeline, CSVIngester, ParquetWriter

    pipeline = Pipeline(
        ingester=CSVIngester("data/input.csv"),
        transforms=[NullDropper(), TypeCaster({"age": int})],
        writer=ParquetWriter("data/output.parquet"),
    )
    result = pipeline.run()
"""

import logging

__version__ = "0.1.0"

logging.getLogger(__name__).addHandler(logging.NullHandler())

# Public API — stable contract
from .transform.pipeline import Pipeline
from .ingestion.csv_ingester import CSVIngester
from .ingestion.s3_ingester import S3Ingester
from .ingestion.db_ingester import DatabaseIngester
from .transform.clean import NullDropper, TypeCaster
from .transform.aggregate import Grouper
from .storage.parquet import ParquetWriter
from .storage.postgres import PostgresWriter
from .storage.s3 import S3Writer
from .models.pipeline import PipelineConfig, PipelineResult

__all__ = [
    "Pipeline",
    "PipelineConfig",
    "PipelineResult",
    "CSVIngester",
    "S3Ingester",
    "DatabaseIngester",
    "NullDropper",
    "TypeCaster",
    "Grouper",
    "ParquetWriter",
    "PostgresWriter",
    "S3Writer",
    "__version__",
]
```

**Main entry point — `pyproject.toml`:**

```toml
[project]
name = "datapipe"
version = "0.1.0"
dependencies = [
    "pandas>=2.0",
    "fastapi>=0.100",
    "click>=8.0",
    "pydantic>=2.0",
]

[project.scripts]
datapipe = "datapipe.cli.commands:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/datapipe"]
```

**`datapipe/cli/commands.py` — CLI entry point:**

```python
# src/datapipe/cli/commands.py
import click
from datapipe import Pipeline, PipelineConfig
from datapipe.config import load_config


@click.group()
@click.version_option()
def main():
    """datapipe — Run data transformation pipelines."""
    pass


@main.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Validate config without running")
def run(config_file: str, dry_run: bool):
    """Run a pipeline from a YAML config file."""
    config = load_config(config_file)
    pipeline = Pipeline.from_config(config)

    if dry_run:
        click.echo(f"Config valid: {config.name}")
        return

    result = pipeline.run()
    click.echo(f"Pipeline complete: {result.records_processed} records processed")


@main.command("list")
def list_pipelines():
    """List all configured pipelines."""
    # ... implementation
    pass


if __name__ == "__main__":
    main()
```

**Dependency flow (single direction, no circular imports):**

```
cli/api  →  transform/Pipeline  →  ingestion, transform, storage
                                →  models (shared data types)
                                →  config
```

</details>

---

<a id="q31"></a>

### Q31 🟡 · Ch10 · importlib.reload — Hot-reload a module

> 🛠️ **Solve locally:** [practice_local.py → Q31](./practice_local.py)




**Problem:** Use `importlib.reload()` to reload a module that has already been imported. Explain:
1. What reload does vs a second `import` statement
2. When you'd actually use it in a real project
3. The key danger with reload (why existing references to old objects remain)

<details>
<summary>💡 Hint</summary>

`importlib.reload(module)` re-executes the module's code and updates the module object in `sys.modules`. But any variable that holds a reference to a class or function from the old version still points to the old code.

</details>

<details>
<summary>✅ Answer</summary>

```python
import importlib
import json as json_mod

# Second import does nothing — returns from sys.modules cache:
import json as json_mod2
print(json_mod is json_mod2)   # True — exact same object

# reload() re-executes the module file and updates the module object in place:
importlib.reload(json_mod)
# json_mod is still the same object reference — updated in-place
# json_mod2 also reflects the changes (same object)

# The danger — stale references:
# old_JSONDecodeError = json_mod.JSONDecodeError
# importlib.reload(json_mod)
# isinstance(exc, old_JSONDecodeError)   # ← may be False! Different class object now
```

**When to use:**
- Development REPLs: edit a module file, reload without restarting the interpreter
- Plugin systems: hot-reload a plugin after the user updates it
- Interactive notebooks: reload a local utility module after editing it

**Why:** `import` after first load is a cache hit — the module code never re-runs. `reload()` forces re-execution. But objects created from old class definitions still have `type(obj).__module__` pointing to the old class — isinstance checks can break.

</details>

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🛠️ Practice Local | [practice_local.py](./practice_local.py) |
| ⬅️ Previous Module | [06 — Exceptions](../06_exceptions_error_handling/practice.md) |
| ➡️ Next Module | [08 — File Handling](../08_file_handling/practice.md) |
