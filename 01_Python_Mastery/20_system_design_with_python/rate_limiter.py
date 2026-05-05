"""
20_system_design_with_python/rate_limiter.py
==============================================
CONCEPT: Rate limiting — controlling how frequently an action can be performed.
WHY THIS MATTERS: Rate limiters protect APIs from abuse, prevent DB overload,
enforce fair use, and protect third-party quotas. Every production API has one.
This file implements the four standard algorithms:
  1. Fixed Window Counter  — simplest, boundary burst problem
  2. Sliding Window Log    — most accurate, highest memory
  3. Token Bucket          — smooth bursting, standard for APIs
  4. Leaky Bucket          — constant output rate, queues excess

Prerequisite: Modules 01–12 (OOP, decorators, context managers, threading)
"""

import time
import threading
import collections
from dataclasses import dataclass, field
from functools import wraps
from typing import Callable, Optional

# =============================================================================
# SECTION 1: Fixed Window Counter — simplest algorithm
# =============================================================================

# CONCEPT: Divide time into fixed windows (e.g., 1-second buckets).
# Count requests in the current window. Reset count when window rolls over.
# PROBLEM: boundary burst — a client can send max_requests at 11:59:59.999
# and max_requests again at 12:00:00.001, sending 2× quota in 2ms.

print("=== Section 1: Fixed Window Counter ===")

class FixedWindowRateLimiter:
    """
    Per-client fixed-window counter.
    Thread-safe via a Lock — safe for use in multi-threaded servers.
    """

    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests   = max_requests
        self.window_seconds = window_seconds
        self._clients: dict = {}   # client_id → [count, window_start]
        self._lock          = threading.Lock()

    def is_allowed(self, client_id: str) -> tuple[bool, dict]:
        """
        Returns (allowed, info_dict).
        allowed=True if the request is within the rate limit.
        """
        now = time.time()
        with self._lock:
            if client_id not in self._clients:
                self._clients[client_id] = [1, now]
                return True, {"count": 1, "limit": self.max_requests}

            count, window_start = self._clients[client_id]

            # Window expired — reset
            if now - window_start >= self.window_seconds:
                self._clients[client_id] = [1, now]
                return True, {"count": 1, "limit": self.max_requests}

            # Within window
            if count < self.max_requests:
                self._clients[client_id][0] += 1
                return True, {"count": count + 1, "limit": self.max_requests}

            # Over limit
            retry_after = self.window_seconds - (now - window_start)
            return False, {"count": count, "limit": self.max_requests,
                           "retry_after": round(retry_after, 3)}


limiter = FixedWindowRateLimiter(max_requests=3, window_seconds=1.0)

print("Fixed window (3 req/sec):")
for i in range(5):
    allowed, info = limiter.is_allowed("client_1")
    status = "ALLOW" if allowed else f"DENY (retry in {info.get('retry_after', '?')}s)"
    print(f"  Request {i+1}: {status}  | count={info['count']}/{info['limit']}")


# =============================================================================
# SECTION 2: Sliding Window Log — most accurate
# =============================================================================

# CONCEPT: Store the timestamp of every request in a log (deque).
# On each request, remove timestamps older than `window_seconds` (slide the
# window forward). Count = remaining entries. If count < limit → allow.
# ACCURATE but high memory (O(max_requests) per client).

print("\n=== Section 2: Sliding Window Log ===")

class SlidingWindowLogLimiter:
    """
    Sliding window log rate limiter.
    ACCURATE: no boundary burst problem.
    MEMORY: stores one timestamp per allowed request per client.
    """

    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests   = max_requests
        self.window_seconds = window_seconds
        self._logs: dict    = {}   # client_id → deque of timestamps
        self._lock          = threading.Lock()

    def is_allowed(self, client_id: str) -> tuple[bool, dict]:
        now = time.time()
        cutoff = now - self.window_seconds

        with self._lock:
            if client_id not in self._logs:
                self._logs[client_id] = collections.deque()

            log = self._logs[client_id]

            # Remove timestamps outside the window (slide left edge)
            while log and log[0] <= cutoff:
                log.popleft()

            count = len(log)

            if count < self.max_requests:
                log.append(now)
                return True, {"count": count + 1, "limit": self.max_requests}

            oldest = log[0]
            retry_after = oldest + self.window_seconds - now
            return False, {
                "count":       count,
                "limit":       self.max_requests,
                "retry_after": round(retry_after, 3),
            }


sw_limiter = SlidingWindowLogLimiter(max_requests=3, window_seconds=1.0)

print("Sliding window log (3 req/sec):")
for i in range(5):
    allowed, info = sw_limiter.is_allowed("user_42")
    status = "ALLOW" if allowed else f"DENY (retry in {info.get('retry_after','?')}s)"
    print(f"  Request {i+1}: {status}")

time.sleep(0.5)
print("  ... 0.5s pause ...")
for i in range(3):
    allowed, info = sw_limiter.is_allowed("user_42")
    status = "ALLOW" if allowed else f"DENY"
    print(f"  Request {i+6}: {status}")


# =============================================================================
# SECTION 3: Token Bucket — standard algorithm for burst-tolerant APIs
# =============================================================================

# CONCEPT: A bucket holds tokens (capacity = max burst size).
# Tokens refill at `refill_rate` tokens/second. Each request consumes 1 token.
# If the bucket is empty → reject the request.
# WHY POPULAR: allows controlled bursting (bucket fills up during quiet periods)
# while maintaining a long-run average rate. Used by AWS API Gateway, Stripe, etc.

print("\n=== Section 3: Token Bucket ===")

class TokenBucket:
    """
    Token bucket rate limiter.
    capacity      = max burst size (tokens available immediately)
    refill_rate   = tokens added per second (long-run average rate)
    Thread-safe via a Lock.
    """

    def __init__(self, capacity: float, refill_rate: float):
        self.capacity    = capacity
        self.refill_rate = refill_rate
        self._tokens     = float(capacity)    # start full
        self._last_refill = time.time()
        self._lock        = threading.Lock()

    def _refill(self) -> None:
        """Add tokens based on elapsed time since last refill."""
        now     = time.time()
        elapsed = now - self._last_refill
        self._tokens = min(
            self.capacity,
            self._tokens + elapsed * self.refill_rate
        )
        self._last_refill = now

    def consume(self, tokens: float = 1.0) -> tuple[bool, dict]:
        """
        Try to consume `tokens` from the bucket.
        Returns (allowed, info).
        """
        with self._lock:
            self._refill()

            if self._tokens >= tokens:
                self._tokens -= tokens
                return True, {
                    "tokens_remaining": round(self._tokens, 2),
                    "capacity":         self.capacity,
                }

            # Not enough tokens — calculate wait time
            deficit    = tokens - self._tokens
            wait_time  = deficit / self.refill_rate
            return False, {
                "tokens_remaining": round(self._tokens, 2),
                "capacity":         self.capacity,
                "retry_after":      round(wait_time, 3),
            }


# Simulate burst traffic
bucket = TokenBucket(capacity=5, refill_rate=2.0)   # 5-token burst, 2/sec refill
print("Token bucket (capacity=5, refill=2/sec):")
print("Burst of 7 requests:")
for i in range(7):
    allowed, info = bucket.consume()
    status = f"ALLOW (tokens={info['tokens_remaining']})" if allowed else \
             f"DENY  (wait {info['retry_after']}s)"
    print(f"  Request {i+1}: {status}")

print("\nWait 1 second (2 tokens refill):")
time.sleep(1.0)
for i in range(3):
    allowed, info = bucket.consume()
    status = f"ALLOW (tokens={info['tokens_remaining']})" if allowed else "DENY"
    print(f"  Request {i+8}: {status}")


# =============================================================================
# SECTION 4: Leaky Bucket — constant output rate
# =============================================================================

# CONCEPT: Requests enter the top of the bucket (a queue). The bucket leaks
# (processes) at a constant rate. If the queue is full → reject.
# Difference from token bucket: leaky bucket produces CONSTANT OUTPUT RATE
# regardless of burst input. Token bucket allows controlled bursting.
# Use leaky bucket when downstream can only handle a fixed rate (e.g., a DB).

print("\n=== Section 4: Leaky Bucket ===")

class LeakyBucket:
    """
    Leaky bucket: queue requests, process at constant rate.
    capacity     = max queue size (rejects if exceeded)
    leak_rate    = requests processed per second (constant output)
    """

    def __init__(self, capacity: int, leak_rate: float):
        self.capacity  = capacity
        self.leak_rate = leak_rate
        self._queue: collections.deque = collections.deque()
        self._last_leak = time.time()
        self._lock = threading.Lock()

    def _leak(self) -> None:
        """Remove items that have 'leaked out' based on elapsed time."""
        now         = time.time()
        elapsed     = now - self._last_leak
        leaked      = int(elapsed * self.leak_rate)

        for _ in range(min(leaked, len(self._queue))):
            self._queue.popleft()

        if leaked > 0:
            self._last_leak = now

    def add(self, request_id: str) -> tuple[bool, dict]:
        with self._lock:
            self._leak()

            if len(self._queue) < self.capacity:
                self._queue.append(request_id)
                return True, {
                    "queue_size": len(self._queue),
                    "capacity":   self.capacity,
                }

            return False, {
                "queue_size": len(self._queue),
                "capacity":   self.capacity,
                "reason":     "queue full",
            }


leaky = LeakyBucket(capacity=4, leak_rate=2.0)   # max 4 queued, leaks 2/sec
print("Leaky bucket (capacity=4, leak_rate=2/sec):")
for i in range(6):
    allowed, info = leaky.add(f"req_{i+1}")
    status = f"QUEUED (queue={info['queue_size']}/{info['capacity']})" if allowed else \
             f"DROPPED ({info['reason']})"
    print(f"  req_{i+1}: {status}")

time.sleep(1.0)
print("  ... 1 second (2 items leaked) ...")
for i in range(3):
    allowed, info = leaky.add(f"req_{i+7}")
    status = f"QUEUED (queue={info['queue_size']})" if allowed else "DROPPED"
    print(f"  req_{i+7}: {status}")


# =============================================================================
# SECTION 5: Rate limiter as a decorator
# =============================================================================

# CONCEPT: Wrap any function with a rate limiter using a decorator.
# The decorator maintains per-caller limits transparently.
# This is the pattern used in API client libraries (e.g., tweepy, stripe-python).

print("\n=== Section 5: Rate Limiter Decorator ===")

def rate_limit(max_calls: int, period: float):
    """
    Decorator factory: limits a function to `max_calls` per `period` seconds.
    Uses sliding window log internally for accuracy.
    Raises RuntimeError if limit exceeded.
    """
    log   = collections.deque()
    lock  = threading.Lock()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            now    = time.time()
            cutoff = now - period

            with lock:
                while log and log[0] <= cutoff:
                    log.popleft()

                if len(log) >= max_calls:
                    oldest     = log[0]
                    retry_secs = round(oldest + period - now, 3)
                    raise RuntimeError(
                        f"{func.__name__}: rate limit exceeded "
                        f"({max_calls}/{period}s). "
                        f"Retry in {retry_secs}s."
                    )

                log.append(now)

            return func(*args, **kwargs)
        return wrapper
    return decorator


@rate_limit(max_calls=3, period=1.0)
def call_external_api(endpoint: str) -> dict:
    """Simulated API call with rate limiting."""
    return {"endpoint": endpoint, "status": 200}


print("Rate-limited decorator (3 calls/sec):")
for i in range(5):
    try:
        result = call_external_api(f"/data/{i}")
        print(f"  Call {i+1}: OK → {result}")
    except RuntimeError as e:
        print(f"  Call {i+1}: {e}")


# =============================================================================
# SECTION 6: Distributed rate limiter — Redis-style (simulated)
# =============================================================================

# CONCEPT: In-process rate limiters don't work across multiple server instances.
# For distributed systems, use an external store (Redis) with atomic operations.
# This simulates the Redis sliding window algorithm used in production.
# Real implementation: use `redis-py` with `pipeline()` for atomicity.

print("\n=== Section 6: Distributed Rate Limiter (Redis Simulation) ===")

class SimulatedRedis:
    """Simulates Redis ZADD / ZREMRANGEBYSCORE / ZCARD for rate limiting."""

    def __init__(self):
        self._sorted_sets: dict = {}   # key → list of (score, member)
        self._lock = threading.Lock()

    def zadd(self, key: str, score: float, member: str) -> None:
        with self._lock:
            if key not in self._sorted_sets:
                self._sorted_sets[key] = []
            self._sorted_sets[key].append((score, member))

    def zremrangebyscore(self, key: str, min_score: float, max_score: float) -> None:
        with self._lock:
            if key in self._sorted_sets:
                self._sorted_sets[key] = [
                    (s, m) for s, m in self._sorted_sets[key]
                    if not (min_score <= s <= max_score)
                ]

    def zcard(self, key: str) -> int:
        with self._lock:
            return len(self._sorted_sets.get(key, []))


class RedisRateLimiter:
    """
    Sliding window rate limiter backed by a simulated Redis.
    In production: replace SimulatedRedis with redis.Redis() and use
    a Lua script or pipeline for atomic operations.
    """

    def __init__(self, redis_client: SimulatedRedis, max_requests: int, window: float):
        self.redis       = redis_client
        self.max_requests = max_requests
        self.window      = window

    def is_allowed(self, client_id: str) -> bool:
        now    = time.time()
        key    = f"rate:{client_id}"
        member = f"{now}"

        # 1. Remove entries older than the window
        self.redis.zremrangebyscore(key, 0, now - self.window)

        # 2. Count remaining entries
        count = self.redis.zcard(key)

        if count < self.max_requests:
            # 3. Add current request
            self.redis.zadd(key, now, member)
            return True

        return False


redis = SimulatedRedis()
dist_limiter = RedisRateLimiter(redis, max_requests=3, window=1.0)

print("Redis-backed distributed limiter (3 req/sec):")
for i in range(5):
    allowed = dist_limiter.is_allowed("api_user_7")
    print(f"  Request {i+1}: {'ALLOW' if allowed else 'DENY'}")


print("\n=== Rate limiter complete ===")
print("Algorithm comparison:")
print("  Fixed Window   → simple; boundary burst problem; O(1) memory")
print("  Sliding Log    → accurate; no burst problem; O(max_requests) memory")
print("  Token Bucket   → burst-tolerant; smooth; standard for public APIs")
print("  Leaky Bucket   → constant output; protects downstream from bursts")
print("  Redis-backed   → distributed; scales across N servers")
print()
print("Choose:")
print("  Token Bucket   → most APIs (AWS, Stripe, GitHub)")
print("  Sliding Log    → strict per-second accuracy needed")
print("  Leaky Bucket   → protecting a fixed-capacity downstream service")
print("  Redis          → multi-instance/multi-region deployments")
