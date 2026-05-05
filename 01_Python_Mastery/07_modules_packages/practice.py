"""
==============================================================================
MODULE 07 — Modules & Packages
==============================================================================
Run with: python3 practice.py

Story: Your team's single-file project has grown to 3,000 lines. Teammates
are stepping on each other. Nobody can find anything. This file walks you
through every import mechanism Python provides — from basic 'import' to
dynamic plugin loading — and shows you why each one exists.

Concepts covered:
  - import module, from x import y, import as, from x import *
  - __name__ == "__main__" — the dual-use pattern
  - sys.path and how Python finds modules
  - sys.modules — the import cache
  - dir(), help(), hasattr() for module introspection
  - Module attributes: __file__, __doc__, __name__, __spec__
  - __all__ — controlling public API
  - importlib.import_module() — dynamic imports
  - importlib.reload() — hot-reload in development
  - Circular import awareness and how to avoid it
  - Lazy imports for startup performance
==============================================================================
"""

import sys
import os

# ==============================================================================
# CONCEPT 1: All import styles — when to use each
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 1: Import styles")
print("="*60)

# --- Style 1: import module ---
# Best for: explicit namespacing, avoiding name clashes, clarity
import math
import json
import random

result = math.sqrt(144)         # clearly from 'math'
pi_val = math.pi
print(f"  math.sqrt(144) = {result}")
print(f"  math.pi = {pi_val:.6f}")

# --- Style 2: from module import name ---
# Best for: names you use heavily, when the module name is long
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Optional, List, Dict

now = datetime.now()
tomorrow = now + timedelta(days=1)
print(f"\n  datetime.now() = {now.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  Tomorrow      = {tomorrow.strftime('%Y-%m-%d')}")

# --- Style 3: import module as alias ---
# Best for: long module names, well-known community aliases
import collections as col
import itertools as it
import functools as ft

# Community aliases for reference (require pip install):
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt

chain = list(it.chain([1, 2], [3, 4], [5]))
print(f"\n  itertools.chain([1,2],[3,4],[5]) = {chain}")

# --- Style 4: from module import name as alias ---
# Best for: name conflicts, very long names
from os.path import join as path_join
from os.path import exists as path_exists
from datetime import datetime as dt

path = path_join("folder", "subfolder", "file.txt")
print(f"\n  path_join result = {path}")

# --- Style 5: from module import * (use sparingly) ---
# Imports all names in __all__ (or all public names if __all__ not defined)
# Avoid in production code — pollutes namespace, unclear where names come from
# Acceptable in: REPL sessions, __init__.py for deliberate re-export
from math import *      # gets sin, cos, pi, sqrt, etc.
print(f"\n  After 'from math import *': sin(pi/2) = {sin(pi/2):.1f}")
# After this, if you defined your own 'sqrt' it would be overwritten — the danger


# ==============================================================================
# CONCEPT 2: __name__ == "__main__" — the dual-use pattern
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 2: __name__ == '__main__'")
print("="*60)

"""
Every Python file has a __name__ attribute:
  - When you RUN it directly:  __name__ == "__main__"
  - When it's IMPORTED:        __name__ == "the_module_name"

This lets you write a file that is both:
  1. A reusable library (functions/classes others import)
  2. An executable script (runs when called directly)

Without this guard:
  import calculator  ← also executes the test code — unexpected side effect!
"""

def add(a: float, b: float) -> float:
    """Add two numbers. Importable utility."""
    return a + b

def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

# This block demonstrates the pattern — in a real module file, this would
# contain test runs, CLI argument parsing, or demo code
print(f"  This file's __name__ = '{__name__}'")

if __name__ == "__main__":
    # Only runs when: python3 practice.py
    # Does NOT run when: import practice (from another file)
    print("  Running as main script — executing demo code")
    print(f"  add(3, 4) = {add(3, 4)}")
else:
    # Only runs when imported
    print(f"  Imported as module '{__name__}' — demo code skipped")

# Because we ARE running this as main (python3 practice.py),
# __name__ == "__main__" is True here
print(f"  __name__ == '__main__' is: {__name__ == '__main__'}")


# ==============================================================================
# CONCEPT 3: sys.path — how Python finds modules
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 3: sys.path — module search path")
print("="*60)

"""
When you write 'import math', Python searches sys.path in ORDER:
  1. '' (empty string) = current working directory — FIRST
  2. Directories in PYTHONPATH environment variable
  3. Standard library directories
  4. site-packages (where pip installs third-party packages)

This means: a file named 'math.py' in your CWD would SHADOW the stdlib math!
"""

print("  sys.path entries:")
for i, p in enumerate(sys.path[:6]):  # show first 6 entries
    print(f"    [{i}] {p!r}")

print(f"\n  Current working dir = {os.getcwd()!r}")
print(f"  CWD in sys.path[0]  = {sys.path[0] == '' or os.getcwd() in sys.path}")

# You can modify sys.path at runtime — use sparingly, prefer pip install -e .
# sys.path.insert(0, "/path/to/my/library")   # highest priority
# sys.path.append("/path/to/fallback")        # lowest priority


# ==============================================================================
# CONCEPT 4: sys.modules — the import cache
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 4: sys.modules — the import cache")
print("="*60)

"""
Python caches every imported module in sys.modules (a dict).
Second import of the same module returns the CACHED object — module
code does NOT re-execute.

This is why:
  - Modules are singletons (only one instance per process)
  - Import order matters for circular imports
  - Module-level code runs exactly once
"""

print(f"  'math' in sys.modules: {'math' in sys.modules}")
print(f"  'json' in sys.modules: {'json' in sys.modules}")
print(f"  'numpy' in sys.modules: {'numpy' in sys.modules}")  # not imported yet

# Access the cached module object directly
cached_math = sys.modules["math"]
print(f"\n  sys.modules['math'] is math: {cached_math is math}")  # same object

# Count how many modules are currently loaded
print(f"\n  Total modules in sys.modules: {len(sys.modules)}")

# Peek at some interesting ones
interesting = ["builtins", "os", "os.path", "math", "json", __name__]
for name in interesting:
    if name in sys.modules:
        mod = sys.modules[name]
        print(f"  sys.modules[{name!r}] = {mod}")


# ==============================================================================
# CONCEPT 5: dir(), help(), hasattr() — module introspection
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 5: Module introspection")
print("="*60)

# dir(module) returns a sorted list of all names in the module's namespace
math_names = dir(math)
print(f"  dir(math) has {len(math_names)} entries")
# Show the non-dunder ones
public_names = [n for n in math_names if not n.startswith("_")]
print(f"  Public names: {public_names[:10]} ...")

# hasattr() — safe check before accessing
print(f"\n  hasattr(math, 'pi') = {hasattr(math, 'pi')}")
print(f"  hasattr(math, 'tau') = {hasattr(math, 'tau')}")       # added in 3.6
print(f"  hasattr(math, 'cosmic_constant') = {hasattr(math, 'cosmic_constant')}")

# getattr() — dynamic attribute access with a default
tau = getattr(math, "tau", 2 * math.pi)    # fallback if not present
print(f"  getattr(math, 'tau', 2*pi) = {tau:.6f}")

# help() — shows docstring (suppressed here, shown in REPL)
# help(math.sqrt)   ← great in the REPL, not useful in scripts


# ==============================================================================
# CONCEPT 6: Module dunder attributes
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 6: Module dunder attributes")
print("="*60)

"""
Every module object has special attributes set by the import machinery:

  __name__     : module name ('math', '__main__', 'myapp.models')
  __file__     : absolute path to the .py file on disk
  __doc__      : module-level docstring (the triple-quoted string at the top)
  __spec__     : ModuleSpec — contains name, origin, loader, submodule_search_locations
  __package__  : package name (empty string for top-level modules)
  __loader__   : the loader used to load the module
  __builtins__ : reference to the builtins module
"""

print(f"  math.__name__    = {math.__name__!r}")
print(f"  math.__file__    = {math.__file__!r}")
print(f"  math.__doc__[:60] = {(math.__doc__ or '')[:60]!r}...")
print(f"  math.__spec__    = {math.__spec__}")
print(f"  math.__package__ = {math.__package__!r}")

# This module's own attributes
print(f"\n  This module:")
print(f"  __name__    = {__name__!r}")
print(f"  __file__    = {__file__!r}")
print(f"  __doc__[:60] = {(__doc__ or '')[:60]!r}...")


# ==============================================================================
# CONCEPT 7: __all__ — defining and respecting public API
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 7: __all__ — public API contract")
print("="*60)

"""
__all__ = list of names that 'from module import *' exports.
It also signals to IDEs and human readers: "these are the public names."

If __all__ is NOT defined: 'from module import *' exports all names
that do NOT start with underscore.

If __all__ IS defined: ONLY names in __all__ are exported.
"""

# We'll simulate a validators module inline
_INTERNAL_REGEX_PATTERN = r"[^@]+"   # private helper — starts with _

def _normalize_email(email: str) -> str:
    """Private helper — not in __all__, not part of public API."""
    return email.strip().lower()

def validate_email(email: str) -> bool:
    """Public: validate email format."""
    email = _normalize_email(email)
    return "@" in email and "." in email.split("@")[-1]

def validate_phone(phone: str) -> bool:
    """Public: validate 10-digit phone number."""
    digits = "".join(c for c in phone if c.isdigit())
    return len(digits) == 10

def validate_age(age: int) -> bool:
    """Public: validate age is in a plausible range."""
    return isinstance(age, int) and 0 < age < 150

# Declaring public API
__all__ = ["validate_email", "validate_phone", "validate_age"]
# 'from this_module import *' would export ONLY these three
# _normalize_email and _INTERNAL_REGEX_PATTERN are excluded

print(f"  __all__ = {__all__}")
print(f"  validate_email('alice@example.com') = {validate_email('alice@example.com')}")
print(f"  validate_email('not-an-email')       = {validate_email('not-an-email')}")
print(f"  validate_phone('555-867-5309')        = {validate_phone('555-867-5309')}")
print(f"  validate_age(25)                      = {validate_age(25)}")
print(f"  validate_age(250)                     = {validate_age(250)}")

# Check that 'private' names are still accessible (__ is convention, not enforcement)
print(f"\n  _normalize_email is accessible (convention not enforcement): "
      f"{_normalize_email('  ALICE@EXAMPLE.COM  ')!r}")


# ==============================================================================
# CONCEPT 8: importlib — dynamic imports and reload
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 8: importlib — dynamic and runtime imports")
print("="*60)

import importlib

# --- Basic dynamic import by string name ---
"""
importlib.import_module(name) does exactly what 'import name' does,
but takes a string — so you can compute the module name at runtime.

Use cases:
  - Plugin systems (load plugins listed in a config file)
  - Feature flags (load different implementations based on environment)
  - Frameworks that discover modules automatically (Django apps, pytest plugins)
"""

module_names = ["math", "json", "os"]
loaded = {}
for name in module_names:
    mod = importlib.import_module(name)
    loaded[name] = mod
    print(f"  Dynamically loaded {name!r}: {mod}")

# Access attributes on dynamically loaded modules
dyn_math = importlib.import_module("math")
print(f"\n  dyn_math.factorial(10) = {dyn_math.factorial(10)}")

# --- importlib for submodule imports ---
# Equivalent to: from os.path import join
os_path = importlib.import_module("os.path")
print(f"  os.path loaded via importlib: {os_path.join('a', 'b', 'c')}")

# --- Simulated plugin registry ---
print("\n  Plugin registry pattern:")

PLUGIN_REGISTRY: Dict[str, object] = {}

def register_plugin(name: str, module_name: str, class_name: str) -> None:
    """Load a plugin class by string names — no hard import needed at top."""
    try:
        module = importlib.import_module(module_name)
        plugin_class = getattr(module, class_name)
        PLUGIN_REGISTRY[name] = plugin_class
        print(f"  Registered plugin '{name}' → {module_name}.{class_name}")
    except (ImportError, AttributeError) as e:
        print(f"  Failed to register plugin '{name}': {e}")

# Register stdlib modules as "plugins" for demonstration
register_plugin("json_handler", "json", "JSONDecodeError")  # exists
register_plugin("missing_plugin", "nonexistent_module", "SomeClass")  # will fail

# --- importlib.reload() ---
"""
reload() re-executes a module's code and updates sys.modules in place.
Useful during development for hot-reload without restarting the interpreter.
Production code should NOT use reload() — it creates subtle state inconsistencies
when objects hold references to old class definitions.
"""
import os as _os   # already imported — reload it
importlib.reload(_os)
print(f"\n  importlib.reload(os) completed — os module refreshed in place")


# ==============================================================================
# CONCEPT 9: Circular import awareness
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 9: Circular import awareness")
print("="*60)

"""
Circular imports happen when module A imports B, and B imports A.

    a.py: from b import greet_b
    b.py: from a import greet_a   ← a is still loading! greet_a may not exist yet
                                    → ImportError: cannot import name 'greet_a'

Why it breaks:
  Python starts loading a.py → adds a (incomplete) to sys.modules
  → encounters 'from b import greet_b' → loads b.py
  → b.py does 'from a import greet_a' → finds a in sys.modules
  → but a is INCOMPLETE (still being loaded) → greet_a doesn't exist yet

Three fixes:

Fix 1 — Extract shared logic to a third module (best, fixes the design)
Fix 2 — Move the import inside the function (deferred import)
Fix 3 — Import the module, not the name (attribute access deferred)
"""

# Demonstrating Fix 2: deferred import inside a function
print("  Circular import Fix 2: deferred import inside function")

# Simulate module B that would normally import from A at module level
class ModuleB:
    def do_work(self):
        # This import happens ONLY when do_work() is called,
        # by which time both modules are fully loaded
        from collections import OrderedDict   # using stdlib as stand-in
        return OrderedDict([("result", "computed"), ("source", "ModuleB")])

b = ModuleB()
result = b.do_work()
print(f"  Result from deferred import: {result}")

# Demonstrating Fix 3: import module, not name
print("\n  Circular import Fix 3: import the module (not the name)")
import json as _json_safe   # import the module — attribute access happens later
# By the time you call _json_safe.dumps(...), both modules are fully loaded
print(f"  json.dumps used safely: {_json_safe.dumps({'key': 'value'})}")


# ==============================================================================
# CONCEPT 10: Lazy imports — startup performance
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 10: Lazy imports")
print("="*60)

"""
Heavy modules (numpy, pandas, tensorflow) can take 100ms–1s to import.
A CLI tool that imports pandas at the top level pays that cost on EVERY
invocation — even when the user just does 'mycli --help'.

Lazy imports defer the cost to first use.
"""

# Bad: top-level import always costs the load time
# import pandas as pd   ← 200ms even if the user never needs it

# Good: import inside the function that needs it
def process_large_dataset(data: list) -> dict:
    """
    Only imports heavy deps when actually called.
    If this function is never called, the import never happens.
    """
    import hashlib   # cheap stdlib, but demonstrates the pattern
    # In real code: import pandas as pd, import numpy as np
    digest = hashlib.sha256(str(data).encode()).hexdigest()[:8]
    return {"count": len(data), "checksum": digest}

print("  Before calling process_large_dataset:")
print(f"  'hashlib' in sys.modules: {'hashlib' in sys.modules}")

result = process_large_dataset([1, 2, 3, 4, 5])
print(f"\n  After calling process_large_dataset:")
print(f"  Result: {result}")
print(f"  'hashlib' in sys.modules: {'hashlib' in sys.modules}")  # now cached

# Class-level lazy loading pattern
class DataProcessor:
    """
    Stores the heavy module as a class attribute — loaded once, reused forever.
    Avoids re-importing on every method call.
    """
    _hashlib = None

    @classmethod
    def _get_hashlib(cls):
        """Load once, cache on the class."""
        if cls._hashlib is None:
            import hashlib
            cls._hashlib = hashlib
        return cls._hashlib

    def compute_hash(self, data: str) -> str:
        hl = self._get_hashlib()    # fast no-op after first call
        return hl.md5(data.encode()).hexdigest()

dp = DataProcessor()
print(f"\n  DataProcessor.compute_hash('hello') = {dp.compute_hash('hello')}")
print(f"  DataProcessor.compute_hash('world') = {dp.compute_hash('world')}")


# ==============================================================================
# CONCEPT 11: Package __init__.py patterns
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 11: Package __init__.py patterns")
print("="*60)

"""
__init__.py has three jobs in a well-designed package:

1. Mark the directory as a package (can be empty)
2. Define the public API — re-export names so users do:
      from myapp.models import User
   instead of:
      from myapp.models.user import User
3. Initialize package-level state (version, logging setup)

Example of a good __init__.py for a models package:
    # myapp/models/__init__.py
    from .user    import User
    from .product import Product
    from .order   import Order

    __all__ = ["User", "Product", "Order"]
    __version__ = "1.0.0"

This is the 'facade' pattern — the __init__.py is the front door,
hiding internal file structure from consumers.
"""

# Simulate inspecting what a real package exposes
# We'll use 'collections' as a stand-in for a well-structured package
import collections
print(f"  collections package:")
print(f"    __file__    = {getattr(collections, '__file__', 'N/A')!r}")
print(f"    __version__ = {getattr(collections, '__version__', 'N/A')!r}")
public_api = [n for n in dir(collections) if not n.startswith("_")]
print(f"    Public names ({len(public_api)}): {public_api}")


# ==============================================================================
# CONCEPT 12: Module attributes as runtime information
# ==============================================================================
print("\n" + "="*60)
print("CONCEPT 12: Using module attributes at runtime")
print("="*60)

# Building a simple module registry / plugin discovery system
def describe_module(mod) -> dict:
    """Extract useful metadata from any module object."""
    return {
        "name":     getattr(mod, "__name__", "unknown"),
        "file":     getattr(mod, "__file__", "built-in"),
        "doc":      (getattr(mod, "__doc__", "") or "")[:50].strip(),
        "public":   len([n for n in dir(mod) if not n.startswith("_")]),
        "all":      getattr(mod, "__all__", None),
    }

modules_to_inspect = [math, json, os]
for mod in modules_to_inspect:
    info = describe_module(mod)
    print(f"  {info['name']:10s} | {info['public']:3d} public names | "
          f"has __all__: {info['all'] is not None} | {info['doc']!r}")


# ==============================================================================
# PART 2: importlib advanced — check module exists before importing
# ==============================================================================
print("\n" + "="*60)
print("PART 2: Safe optional imports and feature detection")
print("="*60)

def try_import(module_name: str):
    """
    Safely attempt to import a module.
    Returns the module if available, None if not installed.
    This is the correct way to handle optional dependencies.
    """
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None

# Check for optional heavy dependencies without crashing
optional_modules = ["numpy", "pandas", "requests", "flask", "fastapi"]
print("  Optional dependency check:")
for name in optional_modules:
    mod = try_import(name)
    status = f"available (v{getattr(mod, '__version__', '?')})" if mod else "not installed"
    print(f"    {name:12s}: {status}")

# Feature detection pattern — enable features based on what's available
numpy = try_import("numpy")
if numpy is not None:
    print("\n  numpy is available — enabling fast array operations")
    # In real code: use numpy for computation
else:
    print("\n  numpy not available — falling back to pure Python")
    # In real code: use list comprehensions as fallback


# ==============================================================================
# Summary
# ==============================================================================
print("\n" + "="*60)
print("Summary: What we covered")
print("="*60)
print("""
  import styles    : import, from X import Y, as alias, *
  __name__         : __main__ guard prevents side effects on import
  sys.path         : ordered search path — CWD first, then stdlib, then site-packages
  sys.modules      : import cache — modules are singletons
  dir() / hasattr(): introspect module contents at runtime
  __file__/__doc__ : module metadata available at runtime
  __all__          : controls public API for wildcard imports
  importlib        : dynamic imports, plugin systems, reload
  circular imports : design smell — fix by extracting shared code
  lazy imports     : defer heavy deps to first use for fast startup
  __init__.py      : package facade, public API, version info
""")

print("="*60)
print("MODULE 07 — All concepts demonstrated.")
print("="*60)
