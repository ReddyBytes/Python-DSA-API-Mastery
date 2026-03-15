"""
10_decorators/function_decorators.py
=======================================
CONCEPT: Function decorators — wrapping functions to add behavior without
changing their implementation.
WHY THIS MATTERS: Decorators are everywhere in Python frameworks:
@app.route in Flask, @pytest.mark.parametrize, @property, @staticmethod,
@lru_cache, @dataclass. Understanding them means understanding Python frameworks.

Prerequisite: Modules 01–09 (especially closures from 04_functions)
"""

import functools
import time
import logging
from typing import Callable, TypeVar, Any

log = logging.getLogger(__name__)

# =============================================================================
# SECTION 1: What a decorator IS (from first principles)
# =============================================================================

# CONCEPT: A decorator is a function that TAKES a function and RETURNS a
# (usually enhanced) function. The @syntax is syntactic sugar:
#
#   @my_decorator
#   def greet(): ...
#
# is EXACTLY the same as:
#
#   def greet(): ...
#   greet = my_decorator(greet)
#
# WHY: you can add behavior (logging, timing, caching, auth) around a function
# without modifying the function itself — separation of concerns.

print("=== Section 1: Decorator Basics ===")

def simple_decorator(func):
    """
    The simplest possible decorator.
    Takes a function, wraps it, returns the wrapper.
    """
    @functools.wraps(func)   # ALWAYS use wraps — preserves func name/docstring
    def wrapper(*args, **kwargs):
        print(f"  Before {func.__name__}()")
        result = func(*args, **kwargs)   # call the original function
        print(f"  After  {func.__name__}()")
        return result   # MUST return the result!
    return wrapper

@simple_decorator
def greet(name: str) -> str:
    """Greets a person by name."""
    return f"Hello, {name}!"

result = greet("Alice")
print(f"  Result: {result}")
print(f"  Name preserved: {greet.__name__}")       # 'greet' (not 'wrapper')
print(f"  Doc preserved:  {greet.__doc__}")         # original docstring


# =============================================================================
# SECTION 2: Parameterized decorators (decorator factories)
# =============================================================================

# CONCEPT: When you want a decorator with configuration (like @retry(max=3)),
# you need another level of nesting: a function that RETURNS a decorator.
# Pattern: outer function takes config → returns actual decorator.

print("\n=== Section 2: Parameterized Decorators ===")

def retry(max_attempts: int = 3, delay: float = 0.1, exceptions: tuple = (Exception,)):
    """
    Decorator factory — returns a configured retry decorator.
    Usage: @retry(max_attempts=5, delay=0.5)
    Why factory: the decorator needs runtime configuration.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt < max_attempts:
                        print(f"  Attempt {attempt} failed, retrying in {delay}s...")
                        time.sleep(delay)
            print(f"  All {max_attempts} attempts failed.")
            raise last_exc
        return wrapper
    return decorator   # return the actual decorator

attempt_count = [0]

@retry(max_attempts=3, delay=0.0, exceptions=(ValueError,))
def flaky_operation():
    attempt_count[0] += 1
    if attempt_count[0] < 3:
        raise ValueError(f"Transient failure #{attempt_count[0]}")
    return "success"

result = flaky_operation()
print(f"  Result after retries: {result}")


# =============================================================================
# SECTION 3: Real decorator library: timer, logger, rate limiter
# =============================================================================

# CONCEPT: These are the decorators you'd find in any real Python service.
# Each adds one responsibility — they combine via stacking.

print("\n=== Section 3: Production Decorators ===")

def timer(func):
    """
    Measure and log how long a function takes.
    WHY: Performance monitoring without changing each function individually.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"  {func.__name__} took {elapsed_ms:.2f}ms")
        return result
    return wrapper


def log_calls(logger: logging.Logger = None, level: int = logging.INFO):
    """
    Log function calls with arguments and return values.
    WHY: Audit trail for important operations without boilerplate in every function.
    """
    def decorator(func):
        _logger = logger or logging.getLogger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            _logger.log(level, f"CALL {func.__name__}({signature})")
            try:
                result = func(*args, **kwargs)
                _logger.log(level, f"RETURN {func.__name__} → {result!r}")
                return result
            except Exception as e:
                _logger.exception(f"EXCEPTION in {func.__name__}: {e}")
                raise
        return wrapper
    return decorator


def validate_types(**type_checks):
    """
    Runtime type validation decorator.
    Usage: @validate_types(amount=float, user_id=int)
    WHY: Catch type errors at function boundary with clear messages.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check keyword arguments
            for param, expected_type in type_checks.items():
                if param in kwargs:
                    value = kwargs[param]
                    if not isinstance(value, expected_type):
                        raise TypeError(
                            f"{func.__name__}() parameter '{param}' must be "
                            f"{expected_type.__name__}, got {type(value).__name__}"
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Stack multiple decorators — applied bottom-up (timer wraps the validate-wrapped func)
@timer
@validate_types(amount=float, user_id=int)
def process_payment(user_id: int, amount: float) -> dict:
    """Process a payment for a user."""
    time.sleep(0.01)   # simulate work
    return {"user_id": user_id, "amount": amount, "status": "processed"}

print("\nStacked decorators:")
result = process_payment(user_id=42, amount=99.99)
print(f"  Result: {result}")

# Type validation error
try:
    process_payment(user_id="not-an-int", amount=50.0)
except TypeError as e:
    print(f"  TypeError: {e}")


# =============================================================================
# SECTION 4: Caching decorators
# =============================================================================

# CONCEPT: functools.lru_cache stores return values keyed by arguments.
# Subsequent calls with the same args return instantly from cache.
# Critical for: DP algorithms, expensive DB/API calls, computed properties.

print("\n=== Section 4: Caching ===")

from functools import lru_cache

@lru_cache(maxsize=256)
def fibonacci(n: int) -> int:
    """
    Without @lru_cache: O(2^n) — fib(40) takes ~50 seconds.
    With @lru_cache:    O(n)  — fib(40) is instant.
    WHY: Each unique argument combination computed only once.
    REQUIREMENT: Arguments must be hashable (no lists, dicts).
    """
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

start = time.perf_counter()
print(f"fibonacci(40) = {fibonacci(40)}")
print(f"Time: {(time.perf_counter()-start)*1000:.2f}ms")
print(f"Cache: {fibonacci.cache_info()}")

# Custom cache with TTL (time-to-live) — common for API caches
def ttl_cache(seconds: float):
    """
    Cache that expires entries after `seconds` seconds.
    WHY: For data that changes infrequently — cache for 60s, then refresh.
    """
    def decorator(func):
        cache = {}   # {args_key: (result, expiry_time)}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, frozenset(kwargs.items()))
            now = time.time()

            if key in cache:
                result, expiry = cache[key]
                if now < expiry:
                    print(f"  Cache HIT: {func.__name__}{args}")
                    return result
                else:
                    print(f"  Cache EXPIRED: {func.__name__}{args}")

            result = func(*args, **kwargs)
            cache[key] = (result, now + seconds)
            print(f"  Cache MISS: {func.__name__}{args}")
            return result

        wrapper.cache = cache   # expose for inspection/clearing
        return wrapper
    return decorator

@ttl_cache(seconds=0.1)
def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    """Simulates an expensive API call to get exchange rates."""
    rates = {"USD/EUR": 0.92, "USD/GBP": 0.79, "EUR/GBP": 0.86}
    return rates.get(f"{from_currency}/{to_currency}", 1.0)

print("\nTTL Cache:")
print(f"  Rate: {get_exchange_rate('USD', 'EUR')}")
print(f"  Rate: {get_exchange_rate('USD', 'EUR')}")  # HIT
time.sleep(0.11)  # expire
print(f"  Rate: {get_exchange_rate('USD', 'EUR')}")  # EXPIRED → re-fetches


# =============================================================================
# SECTION 5: Decorators that take or give access to the wrapped function
# =============================================================================

# CONCEPT: Some decorators need to inspect the wrapped function's signature
# (e.g., dependency injection, auto-documentation). functools.wraps copies
# __name__, __doc__, __annotations__, and __wrapped__ (original function).

print("\n=== Section 5: Decorator Metadata and Introspection ===")

import inspect

def require_auth(roles: list):
    """
    Authorization decorator: check if the current user has required roles.
    WHY: Instead of writing auth checks in every function, declare them.
    """
    def decorator(func):
        # Store auth requirements on the function object
        func._required_roles = roles   # metadata for other tools

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # In a real app, current_user would come from request context
            current_user_roles = kwargs.pop("_current_roles", ["user"])

            if not any(role in current_user_roles for role in roles):
                raise PermissionError(
                    f"Access denied: {func.__name__} requires {roles}"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@require_auth(["admin", "superuser"])
def delete_all_users():
    """Extremely destructive operation — admin only."""
    return "All users deleted"

# Normal user — denied
try:
    delete_all_users(_current_roles=["user"])
except PermissionError as e:
    print(f"  Blocked: {e}")

# Admin user — allowed
result = delete_all_users(_current_roles=["admin"])
print(f"  Allowed: {result}")

# Inspect what roles are required (metadata attached by decorator)
print(f"  Required roles: {delete_all_users._required_roles}")


print("\n=== Function decorators complete ===")
print("Decorator patterns used in production:")
print("  @functools.wraps     → always include — preserves function identity")
print("  @retry(max_attempts) → transient failures (network, DB, APIs)")
print("  @timer               → performance monitoring")
print("  @log_calls           → audit trails, debugging")
print("  @validate_types      → runtime type checking at boundaries")
print("  @lru_cache           → memoization for pure functions")
print("  @ttl_cache           → time-expiring caches for external data")
print("  @require_auth        → authorization without boilerplate")
