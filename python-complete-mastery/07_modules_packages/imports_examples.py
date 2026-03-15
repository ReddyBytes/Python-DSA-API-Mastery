"""
07_modules_packages/imports_examples.py
=========================================
CONCEPT: Python's import system — how modules find each other, best practices,
circular imports, and package structure.
WHY THIS MATTERS: Every Python project beyond a single file uses imports.
Understanding the import system prevents mysterious ModuleNotFoundError,
circular import bugs, and performance issues from heavy module loading.

Prerequisite: Modules 01–06
"""

import sys
import os
import importlib
import time

# =============================================================================
# SECTION 1: Import styles and what they mean
# =============================================================================

# CONCEPT: Python has several import styles. Each has a different effect on
# the current namespace and on what gets loaded vs what gets exposed.

print("=== Section 1: Import Styles ===")

# --- Style 1: import module ---
# Loads the module, binds the module object to its name
import math
# WHY: keeps namespace clean — must prefix with math.
print(f"math.pi = {math.pi}")
print(f"math.sqrt(16) = {math.sqrt(16)}")

# --- Style 2: from module import name ---
# Loads the module, binds only the named item
from math import pi, sqrt, floor
# WHY: cleaner for frequently used names
print(f"pi = {pi}")
print(f"sqrt(25) = {sqrt(25)}")
# RISK: can shadow existing names in your namespace

# --- Style 3: from module import name as alias ---
# Loads and binds with a different name
from math import factorial as fact
from datetime import datetime as dt
print(f"factorial(5) = {fact(5)}")
print(f"Current time: {dt.now().strftime('%H:%M:%S')}")

# --- Style 4: import module as alias ---
import collections as col
import json as j
counter = col.Counter("abracadabra")
print(f"Counter: {dict(counter)}")

# --- What NOT to do: from module import * ---
# This floods your namespace with unknown names, creates shadowing bugs,
# makes code harder to read (where does `parse` come from?),
# and prevents linters from catching undefined names.
# Exception: in __init__.py to control package public API.


# =============================================================================
# SECTION 2: How Python finds modules (sys.path)
# =============================================================================

# CONCEPT: When you write `import x`, Python searches for module `x` in this order:
# 1. sys.modules cache (already imported? return from cache)
# 2. Built-in modules (math, sys, os — compiled into the interpreter)
# 3. sys.path directories (searched left to right)
# sys.path starts with: script directory, PYTHONPATH env var, installation dirs

print("\n=== Section 2: Module Search Path ===")

print("sys.path (first 3 entries):")
for path in sys.path[:3]:
    print(f"  {path}")

# sys.modules: cache of already-loaded modules
print(f"\nIs 'math' already loaded: {'math' in sys.modules}")
print(f"Is 'json' already loaded: {'json' in sys.modules}")
# Importing the same module twice is free — second import returns from cache
import math as math2
print(f"math is math2: {math is math2}")   # True — same object from cache

# You can manipulate sys.path to load modules from custom directories
# (useful for project-specific shared utilities not in a package)
# sys.path.insert(0, "/path/to/my/library")


# =============================================================================
# SECTION 3: The __name__ guard — why it matters
# =============================================================================

# CONCEPT: When Python runs a file directly (`python myfile.py`), it sets
# __name__ to "__main__". When it's IMPORTED, __name__ is the module name.
# The `if __name__ == "__main__":` guard ensures code only runs when the
# file is the entry point, NOT when it's imported as a library.
#
# WHY THIS IS CRITICAL: without it, a file imported as a module would
# execute its script code — printing, connecting to DBs, starting servers.

print("\n=== Section 3: __name__ Guard ===")

print(f"This module's __name__: {__name__}")
# If run directly: "__main__"
# If imported:     "07_modules_packages.imports_examples" (or similar)

# Pattern: all "run as script" code should be guarded
def main():
    """Encapsulate script logic in main() for testability."""
    print("Running as main script")

if __name__ == "__main__":
    # This block only runs when file is executed directly
    # When imported as a module, this block is SKIPPED
    main()


# =============================================================================
# SECTION 4: Lazy imports — defer slow imports until needed
# =============================================================================

# CONCEPT: Some modules are slow to import (numpy, pandas, tensorflow can take
# 2-5 seconds). If your program only uses them conditionally, lazy imports
# ensure startup is fast and the heavy modules only load when needed.

print("\n=== Section 4: Lazy Imports ===")

def analyze_data(use_numpy: bool):
    """
    Only imports numpy if actually needed.
    WHY: the function might never be called, or be called with use_numpy=False.
    Importing at function level delays loading until the function runs.
    """
    if use_numpy:
        import numpy as np   # imported lazily — only when this branch runs
        data = np.array([1, 2, 3, 4, 5])
        return {"mean": float(np.mean(data)), "std": float(np.std(data))}
    else:
        data = [1, 2, 3, 4, 5]
        mean = sum(data) / len(data)
        return {"mean": mean}

start = time.perf_counter()
result = analyze_data(use_numpy=False)
elapsed = time.perf_counter() - start
print(f"  Without numpy (lazy): {result} in {elapsed*1000:.2f}ms")

# importlib.import_module: programmatic (runtime) imports
# Used when the module name is determined at runtime
def load_plugin(plugin_name: str):
    """
    Load a module by name computed at runtime — used in plugin systems.
    plugin_name comes from config file, CLI args, or database.
    """
    try:
        module = importlib.import_module(plugin_name)
        return module
    except ImportError:
        return None

json_module = load_plugin("json")
print(f"  Dynamically loaded: {json_module.__name__}")

# Programmatic module inspection after loading
print(f"  json module file: {json_module.__file__}")


# =============================================================================
# SECTION 5: __all__ — defining the public API of a module
# =============================================================================

# CONCEPT: __all__ is a list of names that `from module import *` will import.
# It also signals to readers (and IDEs) what the module's public API is.
# Anything not in __all__ is considered private/internal.
# Best practice: define __all__ in every module that is meant to be imported.

print("\n=== Section 5: __all__ and Public API ===")

# Simulate what defining __all__ looks like in a module
# (In a real module file, these would be at the top level)

def _internal_helper():
    """Private function — underscore prefix + not in __all__."""
    return "internal"

def public_function():
    """Public function — should be in __all__."""
    return "public"

def another_public():
    """Also public."""
    return "also public"

# What consumers see when they do `from mymodule import *`
# __all__ = ["public_function", "another_public"]
# Only these two would be imported, _internal_helper is excluded

# Explicit is better than implicit — __all__ communicates intent clearly
print(f"  Would export: public_function, another_public")
print(f"  Would hide:   _internal_helper (private by convention)")


# =============================================================================
# SECTION 6: Relative vs absolute imports (inside packages)
# =============================================================================

# CONCEPT: Inside a package, imports can be absolute (from the package root)
# or relative (relative to the current module's location).
#
# Absolute:  from myapp.utils.helpers import format_date
# Relative:  from ..utils.helpers import format_date  (two levels up)
#
# WHY: Relative imports make internal package organization refactoring easier
# (move a subpackage, relative imports still work). But absolute imports
# are clearer and preferred by most style guides (PEP 8 recommends absolute).

print("\n=== Section 6: Absolute vs Relative Imports ===")

# This is shown as comments since we can't demonstrate inside a real package here

example_structure = """
myapp/
├── __init__.py
├── api/
│   ├── __init__.py
│   └── routes.py
├── models/
│   ├── __init__.py
│   └── user.py
└── utils/
    ├── __init__.py
    └── helpers.py
"""
print(example_structure)

print("Inside myapp/api/routes.py:")
print("  Absolute: from myapp.models.user import User")
print("  Relative: from ..models.user import User")
print()
print("PEP 8 recommendation: prefer absolute imports")
print("Exception: large packages where internal structure changes often")


# =============================================================================
# SECTION 7: Circular imports — diagnosis and solutions
# =============================================================================

# CONCEPT: Circular imports happen when A imports B and B imports A.
# Python handles SOME circular imports (if the actual name is used after
# module loading is complete), but most cause ImportError or AttributeError.

print("\n=== Section 7: Circular Import Diagnosis ===")

# PROBLEM example (commented — would cause ImportError if run):
# --- module_a.py ---
# from module_b import func_b
# def func_a(): return "a"
#
# --- module_b.py ---
# from module_a import func_a   # circular! module_a is still loading
# def func_b(): return "b"

print("Circular import happens when:")
print("  A imports B at module level")
print("  B imports A at module level")
print("  Python starts loading A, hits `import B`, starts loading B,")
print("  hits `import A`, but A isn't finished loading yet → ImportError")

print("\nSolutions (in order of preference):")
print("  1. RESTRUCTURE: extract shared code into a third module C")
print("     A and B both import C — no cycle")
print("  2. MOVE import inside the function that needs it (lazy import)")
print("     def func_in_B():")
print("         from module_a import func_a   # imported at call time, not load time")
print("         return func_a()")
print("  3. Use TYPE_CHECKING guard for type annotations only:")
print("     from typing import TYPE_CHECKING")
print("     if TYPE_CHECKING:")
print("         from module_a import TypeA   # only for type checkers, not runtime")


# =============================================================================
# SECTION 8: Reloading modules (development use case)
# =============================================================================

# CONCEPT: importlib.reload() forces Python to re-execute a module.
# Used in development REPLs and plugin systems. Almost never used in
# production code — it's tricky (existing references to old objects remain).

print("\n=== Section 8: Module Reloading ===")

import json as json_mod
print(f"  json module loaded: {json_mod.__name__}")

# Reload re-executes the module file — updates the module object in place
importlib.reload(json_mod)
print(f"  json module reloaded (same object, fresh execution)")
print(f"  Use case: update a plugin without restarting the interpreter")
print(f"  Caution: existing references to old classes/functions still point to old code")


print("\n=== Import system mastery complete ===")
print("Import best practices:")
print("  1. Absolute imports preferred over relative (PEP 8)")
print("  2. `if __name__ == '__main__':` guards all script-level code")
print("  3. Use __all__ to define a module's public API explicitly")
print("  4. Lazy imports (inside functions) for slow or conditional dependencies")
print("  5. Circular imports → restructure by extracting shared code")
print("  6. sys.modules is the import cache — each module loads exactly once")
