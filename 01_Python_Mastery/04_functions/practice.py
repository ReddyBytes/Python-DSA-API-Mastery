"""
04_functions/practice.py
==========================
CONCEPT: Functions — the fundamental unit of code reuse and abstraction.
WHY THIS MATTERS: Every function pattern here appears in real codebases daily.
Closures enable decorators and factories. *args/**kwargs enable flexible APIs.
Default arguments create clean interfaces. Understanding these deeply makes
you a significantly better Python developer.
"""

# =============================================================================
# SECTION 1: Function anatomy — parameters, defaults, return values
# =============================================================================

# CONCEPT: Parameters can be positional, keyword, or have defaults.
# Default values are evaluated ONCE at function definition — never use
# mutable defaults (list, dict) — use None and create inside the function.

print("=== Section 1: Parameter Patterns ===")

def send_notification(user_id, message, channel="email", priority=3):
    """
    Positional: user_id, message — must always be provided
    Keyword with default: channel, priority — optional, caller can override
    WHY defaults exist: most notifications are email with normal priority.
    Don't force callers to specify things that have sensible defaults.
    """
    return f"[P{priority}] → {user_id} via {channel}: {message}"

# Positional call
print(send_notification(42, "Welcome!"))

# Override specific defaults by name — order doesn't matter for keyword args
print(send_notification(42, "URGENT!", priority=1))
print(send_notification(42, "SMS test", channel="sms", priority=2))

# WRONG way: mutable default
def log_event_broken(event, history=[]):
    history.append(event)
    return history

print("\nMutable default bug:")
print(log_event_broken("login"))      # ['login']
print(log_event_broken("purchase"))   # ['login', 'purchase'] — wrong!

# RIGHT way: None sentinel
def log_event(event, history=None):
    """history=None means 'caller didn't provide one, create fresh list'."""
    if history is None:
        history = []
    history.append(event)
    return history

print("\nFixed with None default:")
print(log_event("login"))      # ['login']
print(log_event("purchase"))   # ['purchase'] — correctly isolated


# =============================================================================
# SECTION 2: *args and **kwargs — variadic functions
# =============================================================================

# CONCEPT: *args collects extra positional arguments into a tuple.
# **kwargs collects extra keyword arguments into a dict.
# Combined, they let you write functions that accept any arguments — critical
# for decorators, wrappers, and flexible APIs.

print("\n=== Section 2: *args and **kwargs ===")

def log(*args, **kwargs):
    """
    *args: positional arguments → tuple
    **kwargs: keyword arguments → dict
    This pattern is used by logging frameworks, test utilities, wrappers.
    """
    parts = [str(a) for a in args]
    kv_parts = [f"{k}={v}" for k, v in kwargs.items()]
    return "  " + " | ".join(parts + kv_parts)

print(log("INFO", "User logged in"))
print(log("ERROR", "Payment failed", user_id=42, amount=99.99))

# Forwarding args to another function (used heavily in decorators)
def create_user(name, email, role="user", active=True):
    return {"name": name, "email": email, "role": role, "active": active}

def create_admin(*args, **kwargs):
    """Override role to admin, pass everything else through."""
    kwargs["role"] = "admin"   # inject our override
    return create_user(*args, **kwargs)   # unpack and forward

print("\n" + str(create_admin("Alice", "alice@example.com")))
print(str(create_admin("Bob", "bob@example.com", active=False)))

# Unpacking at call site
def add(a, b, c):
    return a + b + c

nums = [1, 2, 3]
data = {"a": 10, "b": 20, "c": 30}
print(f"\nadd(*nums): {add(*nums)}")       # unpack list as positional args
print(f"add(**data): {add(**data)}")       # unpack dict as keyword args


# =============================================================================
# SECTION 3: First-class functions — functions as values
# =============================================================================

# CONCEPT: In Python, functions are objects — just like integers or strings.
# You can pass them to functions, return them from functions, store them in
# data structures. This unlocks decorator patterns, callbacks, and strategy patterns.

print("\n=== Section 3: First-Class Functions ===")

def square(x):      return x ** 2
def cube(x):        return x ** 3
def negate(x):      return -x
def add_one(x):     return x + 1

# Functions stored in a list — used to build transformation pipelines
transforms = [square, add_one, negate]   # list of function objects
value = 4
for fn in transforms:
    print(f"  {fn.__name__}({value}) = {fn(value)}")

# Function as argument — the "callback" pattern
def apply_twice(func, value):
    """Apply a function to a value twice. func is a first-class argument."""
    return func(func(value))

print(f"\napply_twice(square, 3) = {apply_twice(square, 3)}")   # (3²)² = 81
print(f"apply_twice(add_one, 5) = {apply_twice(add_one, 5)}")   # 5+1+1 = 7

# Higher-order function: takes functions, returns new function
def compose(*functions):
    """
    Create a pipeline: compose(f, g, h)(x) = h(g(f(x)))
    WHY: Builds reusable transformation chains from small, testable pieces.
    """
    def pipeline(value):
        for fn in functions:
            value = fn(value)
        return value
    return pipeline

double_then_negate = compose(lambda x: x * 2, negate)
print(f"\ncompose(double, negate)(5) = {double_then_negate(5)}")   # -(5*2) = -10

normalize = compose(str.strip, str.lower, lambda s: s.replace(" ", "_"))
print(f"normalize(' Hello World ') = '{normalize(' Hello World ')}'")


# =============================================================================
# SECTION 4: Closures — functions that remember their environment
# =============================================================================

# CONCEPT: A closure is a function that captures variables from its enclosing
# scope. The inner function "closes over" the outer function's variables —
# they remain accessible even after the outer function has returned.
# WHY: Closures enable stateful functions without classes, factory patterns,
# and are the foundation of how decorators work.

print("\n=== Section 4: Closures ===")

def make_counter(start=0, step=1):
    """
    Factory: returns a function that remembers and increments `count`.
    `count` and `step` are captured in the closure — they persist across calls.
    """
    count = start   # this variable lives in the closure

    def counter():
        nonlocal count   # tell Python: this `count` is from the enclosing scope
        count += step
        return count

    return counter   # return the inner function (which carries count with it)

counter_by_1 = make_counter()
counter_by_5 = make_counter(100, 5)

print(f"counter_by_1: {counter_by_1()}, {counter_by_1()}, {counter_by_1()}")
print(f"counter_by_5: {counter_by_5()}, {counter_by_5()}, {counter_by_5()}")
# Each closure has its own independent `count` variable


# =============================================================================
# SECTION 5: Lambda — anonymous functions for simple inline logic
# =============================================================================

# CONCEPT: Lambda creates a small anonymous function in one expression.
# Use for simple sorting keys, map/filter, callbacks — where naming would
# be more noise than signal. Avoid complex lambdas — use def instead.

print("\n=== Section 5: Lambda ===")

# Sorting with a key function
students = [
    {"name": "Alice", "grade": 92, "age": 20},
    {"name": "Bob",   "grade": 85, "age": 22},
    {"name": "Carol", "grade": 92, "age": 19},
    {"name": "Diana", "grade": 78, "age": 21},
]

# Sort by grade descending, then name ascending (multi-key sort)
sorted_students = sorted(students, key=lambda s: (-s["grade"], s["name"]))
for s in sorted_students:
    print(f"  {s['name']:6} grade={s['grade']}")

# min/max with key
youngest = min(students, key=lambda s: s["age"])
print(f"\nYoungest: {youngest['name']} (age {youngest['age']})")


# =============================================================================
# SECTION 6: Recursion — functions that call themselves
# =============================================================================

# CONCEPT: Recursion solves problems that have self-similar sub-problems.
# Base case stops the recursion. Recursive case reduces toward the base case.
# Python's default recursion limit is 1000 — use iterative approach or
# sys.setrecursionlimit() for deep recursion needs.

print("\n=== Section 6: Recursion ===")

def factorial(n):
    """
    Classic recursion. Base case: n==0 or n==1.
    Recursive case: n * factorial(n-1)
    Call stack depth = n, so avoid for n > 1000 without sys.setrecursionlimit.
    """
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(f"factorial(5) = {factorial(5)}")    # 120
print(f"factorial(10) = {factorial(10)}")  # 3628800

# Tree traversal — recursion shines on hierarchical data
def flatten(data):
    """
    Recursively flatten arbitrarily nested lists.
    If item is a list, recurse into it. Otherwise, yield the item.
    This is hard to do cleanly with a loop — recursion is the natural fit.
    """
    for item in data:
        if isinstance(item, list):
            yield from flatten(item)   # recurse, yield each item
        else:
            yield item

nested = [1, [2, [3, 4], 5], [6, 7], 8]
print(f"flatten: {list(flatten(nested))}")

# Fibonacci with memoization (avoiding redundant calls)
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    """
    Without cache: O(2^n) — catastrophically slow.
    With @lru_cache: O(n) — each fib(i) computed exactly once.
    lru_cache stores results keyed by arguments — transparent memoization.
    """
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

print(f"fib(10) = {fib(10)}")
print(f"fib(30) = {fib(30)}")
print(f"fib cache info: {fib.cache_info()}")


# =============================================================================
# SECTION 7: Function introspection
# =============================================================================

# CONCEPT: Functions are objects and carry metadata: name, docstring,
# argument info, annotations. Used by documentation generators, test
# frameworks, and decorator libraries.

print("\n=== Section 7: Function Introspection ===")

import inspect

def process_payment(amount: float, currency: str = "USD", method: str = "card") -> dict:
    """
    Process a payment of `amount` in `currency` using `method`.
    Returns a confirmation dict.
    """
    return {"amount": amount, "currency": currency, "method": method}

print(f"Name: {process_payment.__name__}")
print(f"Doc: {process_payment.__doc__.strip()[:60]}...")
print(f"Annotations: {process_payment.__annotations__}")

# inspect module — deeper introspection
sig = inspect.signature(process_payment)
print(f"\nSignature: {sig}")
for name, param in sig.parameters.items():
    default = "required" if param.default is inspect.Parameter.empty else param.default
    print(f"  {name}: default={default}, kind={param.kind.name}")


print("\n=== Functions practice complete ===")
print("Core function concepts:")
print("  1. Use None as default for mutable parameters")
print("  2. *args → tuple, **kwargs → dict; use for flexible/forwarding functions")
print("  3. Functions are objects — pass them around, store them, return them")
print("  4. Closures capture enclosing variables — use nonlocal to rebind them")
print("  5. Lambda: inline simple functions only; def for anything complex")
print("  6. Recursion: base case + reduction toward it; use @lru_cache for fib/dp")
