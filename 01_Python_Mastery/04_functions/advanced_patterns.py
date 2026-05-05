"""
04_functions/advanced_patterns.py
====================================
CONCEPT: Advanced function patterns used in production Python code.
WHY THIS MATTERS: These patterns appear in every well-designed Python library.
Decorators wrap behavior without changing function signatures. Partial application
pre-fills arguments. Protocol dispatch routes to the right handler. These are
the patterns that separate intermediate from senior-level Python developers.
"""

import functools
import inspect
import time
from typing import Callable, Any

# =============================================================================
# SECTION 1: Decorators — the most-used advanced function pattern
# =============================================================================

# CONCEPT: A decorator is a function that takes a function, wraps it with
# additional behavior, and returns the enhanced function. The @syntax is
# just syntactic sugar: @my_decorator above def f means f = my_decorator(f).
# WHY: Add cross-cutting concerns (timing, logging, caching, auth) to many
# functions WITHOUT duplicating code or changing the function bodies.

print("=== Section 1: Building Decorators ===")

def timer(func):
    """
    Decorator that measures and prints how long `func` takes to run.
    @functools.wraps(func) preserves the original function's name and docstring.
    Without it, my_func.__name__ would show 'wrapper' — confusing in logs.
    """
    @functools.wraps(func)   # ALWAYS include this in real decorators
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)  # call the REAL function
        elapsed = time.perf_counter() - start
        print(f"  {func.__name__} took {elapsed*1000:.3f}ms")
        return result   # don't forget to return the result!
    return wrapper

def retry(max_attempts=3, delay=0.1):
    """
    Decorator FACTORY: returns a decorator configured with max_attempts/delay.
    This is the pattern for parameterized decorators.
    Two levels of nesting: outer function takes config, inner is the decorator.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts:
                        print(f"  Attempt {attempt} failed: {e}. Retrying...")
                        time.sleep(delay)
            raise last_error   # re-raise after all attempts exhausted
        return wrapper
    return decorator   # return the actual decorator

# Apply both decorators
call_count = [0]

@timer                 # applied second (outermost)
@retry(max_attempts=3, delay=0.0)   # applied first (innermost)
def unreliable_api_call(endpoint):
    """Simulates a flaky API endpoint."""
    call_count[0] += 1
    if call_count[0] % 3 != 0:   # fails 2 out of 3 calls
        raise ConnectionError(f"Timeout calling {endpoint}")
    return {"status": "success", "data": [1, 2, 3]}

result = unreliable_api_call("/api/users")
print(f"  Final result: {result}")


# =============================================================================
# SECTION 2: Memoization and caching with decorators
# =============================================================================

# CONCEPT: Memoization stores the result of expensive function calls and
# returns the cached result when called with the same arguments.
# The cache is stored in the closure of the wrapper function.
# Python's functools.lru_cache does this professionally with LRU eviction.

print("\n=== Section 2: Memoization ===")

def memoize(func):
    """
    Simple memoization: cache results keyed by (args, frozenset(kwargs)).
    Only works for hashable arguments — tuples, ints, strings (not dicts/lists).
    """
    cache = {}   # this lives in the closure — persists across all calls

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a hashable cache key from all arguments
        key = (args, frozenset(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)   # compute and store
        return cache[key]                         # return from cache

    wrapper.cache = cache   # expose cache for inspection
    return wrapper

@memoize
def slow_fibonacci(n):
    """Without memoization, this is O(2^n) — exponentially slow."""
    if n <= 1:
        return n
    return slow_fibonacci(n - 1) + slow_fibonacci(n - 2)

import time
start = time.perf_counter()
result = slow_fibonacci(35)
elapsed = time.perf_counter() - start
print(f"  fib(35) = {result}, computed in {elapsed*1000:.1f}ms")
print(f"  Cache size: {len(slow_fibonacci.cache)} entries")

# functools.lru_cache: production-grade memoization with LRU eviction
from functools import lru_cache

@lru_cache(maxsize=128)   # keep only the 128 most recent unique calls
def coin_change(coins: tuple, amount: int) -> int:
    """
    Count minimum coins to make `amount` (coin change DP).
    coins must be a TUPLE (not list) — lru_cache requires hashable args.
    WHY tuple: so the argument is hashable for use as cache key.
    """
    if amount == 0:
        return 0
    if amount < 0:
        return float('inf')
    return 1 + min(coin_change(coins, amount - c) for c in coins)

coins = (1, 5, 10, 25)
result = coin_change(coins, 41)
print(f"\n  Minimum coins for 41 cents: {result}")
print(f"  Cache info: {coin_change.cache_info()}")


# =============================================================================
# SECTION 3: Partial application — pre-fill function arguments
# =============================================================================

# CONCEPT: functools.partial creates a NEW function with some arguments
# pre-filled. This is useful for creating specialized versions of general
# functions, and for adapting functions to specific interfaces.
# "Partial application" comes from functional programming theory.

print("\n=== Section 3: Partial Application ===")

from functools import partial

def send_message(user_id, channel, message, priority=3):
    return f"[P{priority}] → user:{user_id} via {channel}: {message}"

# Create specialized version with channel pre-filled
send_email = partial(send_message, channel="email")
send_sms   = partial(send_message, channel="sms",   priority=1)
send_push  = partial(send_message, channel="push")

print(send_email(42, "Welcome to our platform"))
print(send_sms(42, "Your OTP is 1234"))
print(send_push(42, "You have a new message"))

# Real-world use: adapting functions for map/filter/sorted
round_2dp = partial(round, ndigits=2)   # partially apply `ndigits`
prices = [1.2345, 0.999, 2.0001, 15.5555]
rounded = list(map(round_2dp, prices))
print(f"\nRounded to 2dp: {rounded}")

# Partial with callbacks
def process_item(item, formatter, validator):
    if not validator(item):
        return None
    return formatter(item)

# Create a specialized processor for string data
process_username = partial(
    process_item,
    formatter=lambda s: s.strip().lower(),
    validator=lambda s: len(s) >= 3
)

usernames = ["  Alice  ", "Bob", "X", "  Carol  "]
processed = [process_username(u) for u in usernames]
print(f"Processed usernames: {processed}")   # short ones become None


# =============================================================================
# SECTION 4: Function composition and pipelines
# =============================================================================

# CONCEPT: Function composition chains multiple functions so the output of
# one becomes the input of the next. This creates clean, testable pipelines
# where each function does one thing. Common in data transformation, text
# processing, and ETL pipelines.

print("\n=== Section 4: Function Composition ===")

def compose(*functions):
    """
    compose(f, g, h)(x) = h(g(f(x)))
    Left-to-right pipeline: apply f first, then g, then h.
    """
    def pipeline(value):
        for func in functions:
            value = func(value)
        return value
    return pipeline

# Text normalization pipeline for user input
def strip_whitespace(s): return s.strip()
def to_lowercase(s):     return s.lower()
def remove_punctuation(s):
    return ''.join(c for c in s if c.isalnum() or c.isspace())
def tokenize(s):         return s.split()

normalize_text = compose(
    strip_whitespace,
    to_lowercase,
    remove_punctuation,
    tokenize,
)

raw_input = "  Hello, World! This is a Test.  "
tokens = normalize_text(raw_input)
print(f"Normalized: {tokens}")

# Data validation pipeline — each step can fail fast
def validate_pipeline(*validators):
    """
    Returns a function that runs all validators in order.
    Stops at the first failure and returns the error message.
    """
    def validate(value):
        for validator in validators:
            error = validator(value)
            if error:
                return False, error
        return True, "valid"
    return validate

def check_not_empty(v):
    return "Cannot be empty" if not v else None

def check_min_length(min_len):
    return lambda v: f"Must be at least {min_len} chars" if len(v) < min_len else None

def check_no_spaces(v):
    return "Cannot contain spaces" if " " in v else None

validate_username = validate_pipeline(
    check_not_empty,
    check_min_length(3),
    check_no_spaces,
)

test_names = ["", "ab", "alice smith", "alice_admin"]
for name in test_names:
    valid, msg = validate_username(name)
    status = "✓" if valid else "✗"
    print(f"  {status} '{name}' → {msg}")


# =============================================================================
# SECTION 5: Argument inspection and protocol-driven dispatch
# =============================================================================

# CONCEPT: Functions can inspect their own parameters using the inspect module.
# This is used by frameworks (FastAPI, Click) to auto-generate interfaces
# from function signatures — "describe what you want, not how to get it."

print("\n=== Section 5: Argument Inspection ===")

def auto_log(func):
    """
    Decorator that logs function name, ALL argument values (including defaults),
    and return value. Works by introspecting the function's signature.
    """
    sig = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Bind actual call args to the function's parameters
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()   # fill in default values
        args_repr = ", ".join(f"{k}={v!r}" for k, v in bound.arguments.items())
        print(f"  CALL: {func.__name__}({args_repr})")
        result = func(*args, **kwargs)
        print(f"  RETURN: {result!r}")
        return result

    return wrapper

@auto_log
def create_session(user_id: int, role: str = "user", ttl: int = 3600) -> dict:
    return {"user_id": user_id, "role": role, "expires_in": ttl}

create_session(42)
create_session(99, role="admin", ttl=86400)


# =============================================================================
# SECTION 6: Sentinel values and parameter overloading
# =============================================================================

# CONCEPT: Sentinel objects allow you to distinguish "argument not provided"
# from "argument provided as None." This is needed when None is a valid value
# the caller might intentionally pass.

print("\n=== Section 6: Sentinel Values ===")

# The problem: None can't distinguish "not provided" from "set to None"
def set_cache_value_broken(key, value=None):
    if value is None:
        return "Not updating — no value"    # BUG: can't SET value TO None
    return f"Setting {key} = {value}"

# Solution: use a unique sentinel object
_NOT_PROVIDED = object()   # unique object, not equal to anything else

def set_cache_value(key, value=_NOT_PROVIDED, ttl=_NOT_PROVIDED):
    """
    Can now distinguish `set_cache_value(k)` from `set_cache_value(k, None)`.
    None is a valid cache value (meaning "this key exists but is null").
    """
    if value is _NOT_PROVIDED:
        return f"Read {key} from cache"
    ttl_info = f", ttl={ttl}" if ttl is not _NOT_PROVIDED else ""
    return f"Setting {key} = {value!r}{ttl_info}"

print(set_cache_value("user:1"))             # read
print(set_cache_value("user:1", None))       # set to None (explicit null)
print(set_cache_value("user:1", {"name": "Alice"}, ttl=3600))


print("\n=== Advanced function patterns complete ===")
print("Patterns in this file appear in:")
print("  • @timer, @retry → logging/monitoring frameworks")
print("  • @memoize / @lru_cache → DP algorithms, expensive computations")
print("  • partial() → specialized functions, adapters, callback configuration")
print("  • compose() → ETL pipelines, text processing, data transformation")
print("  • inspect.signature → FastAPI, Click, argument-driven frameworks")
print("  • Sentinel → distinguishing 'not provided' from None")
