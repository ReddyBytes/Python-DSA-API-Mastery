# Introspection — Theory + Practice

# =============================================================================
# THEORY: Python Introspection
# =============================================================================
#
# Introspection means examining objects at runtime to discover their structure,
# type, methods, and documentation — without reading the source code.
#
# Python is particularly powerful here because EVERYTHING is an object:
# functions, classes, modules, and even code objects themselves can be
# inspected and manipulated at runtime.
#
# KEY BUILT-INS:
#   type(obj)           → obj's class
#   isinstance(obj, T)  → is obj an instance of T (or T subclass)?
#   issubclass(A, B)    → is A a subclass of B?
#   dir(obj)            → list all accessible names
#   vars(obj)           → obj's __dict__ (or class's namespace)
#   hasattr(obj, name)  → does obj have this attribute?
#   getattr(obj, name)  → get attribute (with optional default)
#   setattr(obj, name, v) → set attribute
#   delattr(obj, name)  → delete attribute
#   callable(obj)       → does obj have __call__?
#   id(obj)             → unique object identity (memory address in CPython)
#
# THE inspect MODULE:
#   inspect.getmembers(obj)        → all (name, value) pairs
#   inspect.signature(func)        → parameter signature
#   inspect.getsource(obj)         → source code as string
#   inspect.getdoc(obj)            → cleaned docstring
#   inspect.isfunction/isclass/ismodule/ismethod(obj)
#   inspect.getmro(cls)            → method resolution order tuple
#   inspect.isabs/isdatadescriptor/isgetsetdescriptor(obj)
# =============================================================================

import inspect
import types
import sys
from typing import Any


# =============================================================================
# SECTION 1: Basic introspection built-ins
# =============================================================================

class Animal:
    """Base class for all animals."""

    species: str = "Unknown"

    def __init__(self, name: str, weight: float):
        self.name   = name
        self.weight = weight

    def speak(self) -> str:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict) -> "Animal":
        return cls(data["name"], data["weight"])

    @staticmethod
    def is_valid_weight(w: float) -> bool:
        return w > 0

    @property
    def description(self) -> str:
        return f"{self.name} ({type(self).__name__})"


class Dog(Animal):
    """A dog that barks."""

    species = "Canis lupus familiaris"

    def __init__(self, name: str, weight: float, breed: str):
        super().__init__(name, weight)
        self.breed = breed

    def speak(self) -> str:
        return f"Woof! I'm {self.name}"


dog = Dog("Rex", 30.0, "Husky")

# --- type ---
print("=== type() ===")
print(type(dog))                 # <class 'Dog'>
print(type(dog).__name__)        # Dog
print(type(dog).__bases__)       # (<class 'Animal'>,)
print(type(dog).__mro__)         # [Dog, Animal, object]

# --- isinstance vs type ---
print("\n=== isinstance ===")
print(isinstance(dog, Dog))      # True
print(isinstance(dog, Animal))   # True  — works for inheritance!
print(type(dog) is Animal)       # False — strict equality, misses inheritance

# --- dir ---
print("\n=== dir() ===")
public_attrs = [name for name in dir(dog) if not name.startswith("_")]
print(public_attrs)

# --- vars ---
print("\n=== vars() ===")
print(vars(dog))    # {'name': 'Rex', 'weight': 30.0, 'breed': 'Husky'}
print(vars(Dog))    # class namespace (mappingproxy)

# --- getattr with default ---
print("\n=== getattr ===")
print(getattr(dog, "breed", "unknown"))      # Husky
print(getattr(dog, "color", "not set"))      # not set  (default)


# =============================================================================
# SECTION 2: inspect module — deep introspection
# =============================================================================

print("\n=== inspect.getmembers ===")
# Filter to only methods (not dunder methods):
methods = [
    (name, obj)
    for name, obj in inspect.getmembers(dog, predicate=inspect.ismethod)
    if not name.startswith("_")
]
for name, method in methods:
    print(f"  {name}: {method}")

print("\n=== inspect.signature ===")
sig = inspect.signature(Dog.__init__)
print(f"Dog.__init__ signature: {sig}")

for param_name, param in sig.parameters.items():
    print(f"  {param_name}:")
    print(f"    kind:    {param.kind.name}")
    print(f"    default: {param.default!r}")
    if param.annotation is not inspect.Parameter.empty:
        print(f"    type:    {param.annotation}")

print("\n=== inspect.getdoc ===")
print(inspect.getdoc(Dog))   # cleaned docstring
print(inspect.getdoc(dog.speak))

print("\n=== inspect.isX checks ===")
print(f"isfunction(Dog.speak):    {inspect.isfunction(Dog.speak)}")     # True
print(f"ismethod(dog.speak):      {inspect.ismethod(dog.speak)}")       # True
print(f"isclass(Dog):             {inspect.isclass(Dog)}")              # True
print(f"isclass(dog):             {inspect.isclass(dog)}")              # False
print(f"isbuiltin(len):           {inspect.isbuiltin(len)}")            # True

print("\n=== MRO ===")
print(inspect.getmro(Dog))   # (Dog, Animal, object)


# =============================================================================
# SECTION 3: Function introspection
# =============================================================================

def process_data(
    data: list[int],
    *,
    normalize: bool = False,
    scale: float = 1.0,
    output_format: str = "list",
) -> list | dict:
    """
    Process a list of integers.

    Args:
        data: Input data to process.
        normalize: If True, normalize to [0,1].
        scale: Scaling factor.
        output_format: 'list' or 'dict'.

    Returns:
        Processed data in the requested format.
    """
    pass

print("=== Function introspection ===")
sig = inspect.signature(process_data)

# Check if all params have type annotations:
for name, param in sig.parameters.items():
    annotated = param.annotation is not inspect.Parameter.empty
    has_default = param.default is not inspect.Parameter.empty
    print(f"  {name}: annotated={annotated}, optional={has_default}")

# Get return annotation:
print(f"Return type: {sig.return_annotation}")

# Count required parameters:
required = [
    p for p in sig.parameters.values()
    if p.default is inspect.Parameter.empty
    and p.kind not in (inspect.Parameter.VAR_POSITIONAL,
                       inspect.Parameter.VAR_KEYWORD)
]
print(f"Required params: {[p.name for p in required]}")


# =============================================================================
# SECTION 4: Class introspection utilities
# =============================================================================

def class_info(cls: type) -> dict:
    """
    Return a comprehensive dict of information about a class.
    Demonstrates practical use of introspection.
    """
    members = inspect.getmembers(cls)

    methods       = [n for n, v in members if inspect.isfunction(v) and not n.startswith("_")]
    class_methods = [n for n, v in members if isinstance(v, classmethod) or
                     (inspect.ismethod(v) and v.__self__ is cls)]
    properties    = [n for n, v in members if isinstance(inspect.getattr_static(cls, n), property)]
    class_vars    = {n: v for n, v in vars(cls).items()
                     if not n.startswith("_")
                     and not callable(v)
                     and not isinstance(v, (property, classmethod, staticmethod))}

    return {
        "name":        cls.__name__,
        "module":      cls.__module__,
        "bases":       [b.__name__ for b in cls.__bases__],
        "mro":         [c.__name__ for c in inspect.getmro(cls)],
        "docstring":   inspect.getdoc(cls),
        "methods":     methods,
        "properties":  properties,
        "class_vars":  class_vars,
        "slots":       list(getattr(cls, "__slots__", [])),
        "has_dict":    "__dict__" not in getattr(cls, "__slots__", ["__dict__"]),
    }

info = class_info(Dog)
for key, value in info.items():
    print(f"  {key}: {value}")


# =============================================================================
# SECTION 5: Dynamic attribute access patterns
# =============================================================================

class ConfigLoader:
    """
    Loads config dict as object attributes using introspection.
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> dict:
        return dict(vars(self))

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get(self, name: str, default: Any = None) -> Any:
        return getattr(self, name, default)

    def has(self, name: str) -> bool:
        return hasattr(self, name)

    def __repr__(self) -> str:
        pairs = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"Config({pairs})"

cfg = ConfigLoader(host="localhost", port=8080, debug=True)
print(cfg)
print(cfg.get("host"))
print(cfg.has("timeout"))

# Reflect config from another config:
other_cfg = {"max_connections": 100, "timeout": 30.0}
cfg.update(**other_cfg)
print(cfg.to_dict())


# =============================================================================
# SECTION 6: Object comparison via introspection
# =============================================================================

def deep_diff(obj1: Any, obj2: Any) -> dict:
    """
    Compare two objects field-by-field using introspection.
    Returns a dict of {field: (old_val, new_val)} for changed fields.
    """
    d1 = vars(obj1) if hasattr(obj1, "__dict__") else {}
    d2 = vars(obj2) if hasattr(obj2, "__dict__") else {}

    all_keys = set(d1) | set(d2)
    diff = {}
    for key in all_keys:
        v1 = d1.get(key, "<missing>")
        v2 = d2.get(key, "<missing>")
        if v1 != v2:
            diff[key] = (v1, v2)
    return diff

class UserState:
    def __init__(self, name, email, age):
        self.name  = name
        self.email = email
        self.age   = age

before = UserState("Alice", "alice@old.com", 29)
after  = UserState("Alice", "alice@new.com", 30)
changes = deep_diff(before, after)
for field, (old, new) in changes.items():
    print(f"  {field}: {old!r} → {new!r}")


# =============================================================================
# SECTION 7: Module introspection
# =============================================================================

def list_module_contents(module) -> dict:
    """List all public classes, functions, and constants in a module."""
    classes   = [(n, v) for n, v in inspect.getmembers(module, inspect.isclass)
                  if not n.startswith("_")]
    functions = [(n, v) for n, v in inspect.getmembers(module, inspect.isfunction)
                  if not n.startswith("_")]
    return {
        "classes":   [n for n, _ in classes],
        "functions": [n for n, _ in functions],
    }

import collections
contents = list_module_contents(collections)
print("\ncollections module:")
print(f"  Classes:   {contents['classes'][:5]}...")
print(f"  Functions: {contents['functions'][:5]}...")


# =============================================================================
# PRACTICE PROBLEMS
# =============================================================================

# ── Problem 1 ──────────────────────────────────────────────────────────────
# Write an auto_repr(cls) decorator that uses introspection to generate
# __repr__ based on __init__ parameters:
#
# @auto_repr
# class Point:
#     def __init__(self, x, y): self.x, self.y = x, y
#
# repr(Point(1, 2)) → "Point(x=1, y=2)"
# Hint: use inspect.signature to get parameter names

# ── Problem 2 ──────────────────────────────────────────────────────────────
# Write a validate_call(func) decorator that:
#   - Inspects func's annotations at decoration time
#   - At call time, validates each argument against its type annotation
#   - Raises TypeError with a helpful message if types don't match
# Tests:
#   @validate_call
#   def add(x: int, y: int) -> int: return x + y
#   add(1, 2)    → 3
#   add(1, "2")  → TypeError: y must be int, got str

# ── Problem 3 ──────────────────────────────────────────────────────────────
# Build an object diff tool: record_snapshot(obj) → dict of current state,
# apply_diff(obj, diff) → restores previous state using setattr.
# Useful for undo systems, change tracking, audit logs.


# =============================================================================
# SOLUTIONS
# =============================================================================

# Solution 1: auto_repr decorator
def auto_repr(cls):
    params = list(inspect.signature(cls.__init__).parameters.keys())
    params = [p for p in params if p != "self"]

    def __repr__(self):
        pairs = ", ".join(f"{p}={getattr(self, p, '?')!r}" for p in params)
        return f"{type(self).__name__}({pairs})"

    cls.__repr__ = __repr__
    return cls

@auto_repr
class Rectangle:
    def __init__(self, width: float, height: float, color: str = "black"):
        self.width  = width
        self.height = height
        self.color  = color

r = Rectangle(10, 5, color="red")
print(repr(r))   # Rectangle(width=10, height=5, color='red')

# Solution 2: validate_call
def validate_call(func):
    hints = {
        name: hint
        for name, hint in func.__annotations__.items()
        if name != "return"
    }

    @__import__("functools").wraps(func)
    def wrapper(*args, **kwargs):
        bound = inspect.signature(func).bind(*args, **kwargs)
        bound.apply_defaults()
        for param_name, value in bound.arguments.items():
            if param_name in hints:
                expected = hints[param_name]
                if not isinstance(value, expected):
                    raise TypeError(
                        f"{param_name} must be {expected.__name__}, "
                        f"got {type(value).__name__}"
                    )
        return func(*args, **kwargs)

    return wrapper

@validate_call
def add(x: int, y: int) -> int:
    return x + y

print(add(1, 2))   # 3
try:
    add(1, "2")    # TypeError
except TypeError as e:
    print(f"Caught: {e}")

print("Introspection tests passed!")
