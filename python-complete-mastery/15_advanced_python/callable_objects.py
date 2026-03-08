# Callable Objects — Theory + Practice

# =============================================================================
# THEORY: The __call__ protocol
# =============================================================================
#
# In Python, anything with a __call__ method can be called like a function:
#   obj(args)  →  type(obj).__call__(obj, args)
#
# Functions themselves are just objects with __call__. That's why you can
# pass functions around, store them in lists, and call them later.
#
# WHY USE CALLABLE OBJECTS OVER PLAIN FUNCTIONS?
#
#   1. STATE — callable objects can remember things between calls
#      (counters, caches, configuration)
#
#   2. CONFIGURATION — create a "family" of related callables by
#      passing different params to __init__
#
#   3. INTROSPECTION — richer than functions:
#      obj.count, obj.reset(), obj.config — not possible with plain functions
#
#   4. INHERITANCE — callable objects can inherit behavior cleanly
#
# CHECKING CALLABILITY:
#   callable(obj)  → True if type(obj) has __call__
#
# Note: callable() checks for __call__ on the TYPE, not the instance.
# Instance __call__ monkey-patches don't make the object callable!
# =============================================================================


# =============================================================================
# SECTION 1: Stateful callable — counter and accumulator
# =============================================================================

class Counter:
    """
    Callable that counts how many times it's been called.
    Can be used as a drop-in replacement for a function that tracks usage.
    """

    def __init__(self, start: int = 0, step: int = 1):
        self.value = start
        self.step  = step

    def __call__(self) -> int:
        """Increment and return the current count."""
        self.value += self.step
        return self.value

    def reset(self):
        self.value = 0
        return self

    def __repr__(self):
        return f"Counter(value={self.value}, step={self.step})"

c = Counter(step=2)
print(c(), c(), c())   # 2 4 6
print(c)               # Counter(value=6, step=2)
c.reset()
print(c())             # 2


class RunningTotal:
    """
    Accumulates values over multiple calls.
    Useful as a reduce-style aggregator.
    """

    def __init__(self):
        self.total = 0.0
        self.count = 0

    def __call__(self, value: float) -> float:
        self.total += value
        self.count += 1
        return self.total

    @property
    def mean(self) -> float:
        if self.count == 0:
            raise ZeroDivisionError("No values accumulated yet")
        return self.total / self.count

    def __repr__(self):
        return f"RunningTotal(total={self.total:.2f}, count={self.count})"

rt = RunningTotal()
for v in [10, 20, 30, 40]:
    print(f"  add {v}: total = {rt(v)}")
print(f"Mean: {rt.mean:.1f}")


# =============================================================================
# SECTION 2: Configurable callable — factory pattern
# =============================================================================

class Multiplier:
    """
    Returns a callable that multiplies by a fixed factor.
    Cleaner than partial(operator.mul, factor) for readable code.
    """

    def __init__(self, factor: float):
        self.factor = factor

    def __call__(self, x: float) -> float:
        return x * self.factor

    def __repr__(self):
        return f"Multiplier(factor={self.factor})"

double = Multiplier(2)
triple = Multiplier(3)
negate = Multiplier(-1)

print(list(map(double, [1, 2, 3, 4, 5])))   # [2, 4, 6, 8, 10]
print(list(map(triple, [1, 2, 3])))          # [3, 6, 9]


class Threshold:
    """
    Creates a callable predicate — usable with filter(), any(), all().
    Much clearer than lambda x: x > 50.
    """

    def __init__(self, lo: float = None, hi: float = None):
        self.lo = lo
        self.hi = hi

    def __call__(self, value: float) -> bool:
        if self.lo is not None and value < self.lo:
            return False
        if self.hi is not None and value > self.hi:
            return False
        return True

    def __repr__(self):
        return f"Threshold({self.lo!r} ≤ x ≤ {self.hi!r})"

is_valid_port   = Threshold(lo=1, hi=65535)
is_adult        = Threshold(lo=18)
is_small_number = Threshold(hi=100)

ports = [0, 80, 443, 8080, 65536, 99999]
print(list(filter(is_valid_port, ports)))   # [80, 443, 8080]


# =============================================================================
# SECTION 3: Memoization callable
# =============================================================================

class Memoized:
    """
    Wraps any callable and caches its results.
    A callable class version of functools.lru_cache.
    """

    def __init__(self, func):
        self.func    = func
        self._cache  = {}
        self.hits    = 0
        self.misses  = 0
        # Preserve original function metadata:
        self.__doc__  = func.__doc__
        self.__name__ = getattr(func, '__name__', str(func))

    def __call__(self, *args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key in self._cache:
            self.hits += 1
            return self._cache[key]
        self.misses += 1
        result = self.func(*args, **kwargs)
        self._cache[key] = result
        return result

    def clear_cache(self):
        self._cache.clear()
        self.hits = self.misses = 0

    def cache_info(self):
        return {
            "hits": self.hits,
            "misses": self.misses,
            "size": len(self._cache),
        }

    def __repr__(self):
        return f"Memoized({self.__name__}, {self.cache_info()})"

@Memoized
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

import time
start = time.perf_counter()
print(fibonacci(40))   # 102334155
elapsed = time.perf_counter() - start
print(f"Elapsed: {elapsed*1000:.2f}ms")
print(fibonacci.cache_info())


# =============================================================================
# SECTION 4: Retry callable
# =============================================================================

import random
import time as _time

class Retry:
    """
    Wraps a callable and retries it on failure with configurable backoff.
    Demonstrates a callable that manages complex execution policies.
    """

    def __init__(
        self,
        func,
        max_attempts: int = 3,
        exceptions: tuple = (Exception,),
        delay: float = 0.1,
        backoff: float = 2.0,
    ):
        self.func         = func
        self.max_attempts = max_attempts
        self.exceptions   = exceptions
        self.delay        = delay
        self.backoff      = backoff
        self.__name__     = getattr(func, '__name__', str(func))
        self.__doc__      = func.__doc__
        self.attempts_log = []

    def __call__(self, *args, **kwargs):
        current_delay = self.delay
        last_exc = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                result = self.func(*args, **kwargs)
                self.attempts_log.append(("success", attempt))
                return result
            except self.exceptions as e:
                last_exc = e
                self.attempts_log.append(("fail", attempt, str(e)))
                if attempt < self.max_attempts:
                    print(f"  Attempt {attempt} failed: {e}. Retrying in {current_delay:.2f}s...")
                    _time.sleep(current_delay)
                    current_delay *= self.backoff

        raise RuntimeError(
            f"{self.__name__} failed after {self.max_attempts} attempts"
        ) from last_exc

    def __repr__(self):
        return f"Retry({self.__name__!r}, max={self.max_attempts})"

# Simulate a flaky function:
call_count = 0
def flaky_api():
    global call_count
    call_count += 1
    if call_count < 3:
        raise ConnectionError(f"Connection refused (attempt {call_count})")
    return {"status": "ok", "data": [1, 2, 3]}

resilient_api = Retry(flaky_api, max_attempts=5, delay=0.01)
result = resilient_api()
print(f"Got: {result}")
print(f"Log: {resilient_api.attempts_log}")


# =============================================================================
# SECTION 5: Pipeline callable
# =============================================================================

class Pipeline:
    """
    A callable that composes multiple functions into a pipeline.
    Each function's output feeds into the next function's input.
    Supports | operator for adding steps.
    """

    def __init__(self, *funcs):
        self.funcs = list(funcs)

    def __call__(self, value):
        for func in self.funcs:
            value = func(value)
        return value

    def __or__(self, func):
        """pipe | func → new Pipeline"""
        if callable(func):
            return Pipeline(*self.funcs, func)
        return NotImplemented

    def __ror__(self, value):
        """value | pipe → apply pipeline"""
        return self(value)

    def __len__(self):
        return len(self.funcs)

    def __repr__(self):
        names = [getattr(f, '__name__', str(f)) for f in self.funcs]
        return f"Pipeline({' → '.join(names)})"

# Build a text normalization pipeline:
normalize = (
    Pipeline()
    | str.strip
    | str.lower
    | (lambda s: " ".join(s.split()))  # collapse whitespace
)

texts = ["  Hello World  ", "  PYTHON   PROGRAMMING  ", "   data   science  "]
for t in texts:
    print(repr(normalize(t)))


# =============================================================================
# SECTION 6: Callable class hierarchy
# =============================================================================

class Transform:
    """Abstract base for data transforms — callable objects."""

    def __call__(self, data):
        raise NotImplementedError

    def __or__(self, other: Transform) -> Transform:
        """Compose: transform1 | transform2"""
        return ComposedTransform(self, other)

class ComposedTransform(Transform):
    def __init__(self, first: Transform, second: Transform):
        self.first  = first
        self.second = second

    def __call__(self, data):
        return self.second(self.first(data))

class Normalize(Transform):
    """Normalize numeric list to [0, 1] range."""
    def __call__(self, data: list) -> list:
        lo, hi = min(data), max(data)
        if lo == hi:
            return [0.5] * len(data)
        return [(x - lo) / (hi - lo) for x in data]

class RoundValues(Transform):
    def __init__(self, decimals: int = 2):
        self.decimals = decimals
    def __call__(self, data: list) -> list:
        return [round(x, self.decimals) for x in data]

class FilterOutliers(Transform):
    def __init__(self, sigma: float = 2.0):
        self.sigma = sigma
    def __call__(self, data: list) -> list:
        mean = sum(data) / len(data)
        std  = (sum((x-mean)**2 for x in data) / len(data)) ** 0.5
        return [x for x in data if abs(x - mean) <= self.sigma * std]

# Build and use a transform pipeline:
pipeline = FilterOutliers(sigma=2.0) | Normalize() | RoundValues(3)
raw = [10, 12, 11, 100, 13, 10, 12, 200, 11]  # 100 and 200 are outliers
print(f"Raw:       {raw}")
print(f"Processed: {pipeline(raw)}")


# =============================================================================
# PRACTICE PROBLEMS
# =============================================================================

# ── Problem 1 ──────────────────────────────────────────────────────────────
# Build a RateLimiter callable class that:
#   - wraps a function
#   - allows at most N calls per second
#   - blocks (sleep) if the rate would be exceeded
#   - tracks how many calls were delayed
# Tests:
#   @RateLimiter(calls_per_second=5)
#   def fetch(url): ...

# ── Problem 2 ──────────────────────────────────────────────────────────────
# Implement a Validator callable that:
#   - takes a dict of field_name → validator_function
#   - when called with a dict, validates each field
#   - returns (is_valid: bool, errors: dict[str, str])
# Tests:
#   validate = Validator({
#       "age": lambda v: v > 0 or "must be positive",
#       "email": lambda v: "@" in v or "invalid email",
#   })
#   validate({"age": -1, "email": "bad"})
#   → (False, {"age": "must be positive", "email": "invalid email"})

# ── Problem 3 ──────────────────────────────────────────────────────────────
# Create a Scheduler callable that:
#   - stores a list of (time_offset, callable) pairs
#   - when called with a "start time", returns results of all scheduled calls
#     in time order
# (Time can be simulated integers, not real time)
# Tests:
#   sched = Scheduler()
#   sched.at(0, lambda: "init")
#   sched.at(5, lambda: "tick")
#   sched.at(2, lambda: "setup")
#   sched.run() → ["init", "setup", "tick"]  (in time order)


# =============================================================================
# SOLUTION: Validator
# =============================================================================

class Validator:
    def __init__(self, rules: dict):
        self.rules = rules

    def __call__(self, data: dict) -> tuple[bool, dict]:
        errors = {}
        for field, rule in self.rules.items():
            value = data.get(field)
            result = rule(value)
            if result is not True and result is not None and result is not "":
                errors[field] = result if isinstance(result, str) else "invalid"
        return len(errors) == 0, errors

    def __repr__(self):
        return f"Validator({list(self.rules.keys())})"

validate_user = Validator({
    "age":   lambda v: v > 0       if isinstance(v, int) else "must be a positive integer",
    "email": lambda v: "@" in str(v) if v else "required",
    "name":  lambda v: len(str(v or "")) >= 2 or "must be at least 2 characters",
})

ok, errors = validate_user({"age": -1, "email": "bad", "name": "A"})
print(f"Valid: {ok}")
print(f"Errors: {errors}")

ok2, errors2 = validate_user({"age": 25, "email": "alice@x.com", "name": "Alice"})
print(f"Valid: {ok2}")
