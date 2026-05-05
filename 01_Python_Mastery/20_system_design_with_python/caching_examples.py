"""
20_system_design_with_python/caching_examples.py
==================================================
CONCEPT: Caching — storing computed or fetched results so you don't recompute
or re-fetch them on the next request.
WHY THIS MATTERS: Caches are the single most impactful performance optimization
in most production systems. A DB query that takes 50ms with cache miss takes
0.1ms on a cache hit. This file covers: in-process caches (LRU, TTL),
memoization, cache invalidation strategies, and a Redis-style cache simulation.

Prerequisite: Modules 01–12 (especially decorators, context managers, OOP)
"""

import time
import threading
import hashlib
import json
from collections import OrderedDict
from dataclasses import dataclass, field
from functools import lru_cache, wraps
from typing import Any, Callable, Optional

# =============================================================================
# SECTION 1: @lru_cache — Python's built-in memoization cache
# =============================================================================

# CONCEPT: @lru_cache caches function return values keyed on the arguments.
# LRU = Least Recently Used — when the cache is full, the least recently
# used entry is evicted. Arguments must be HASHABLE (no lists/dicts as args).
# maxsize=None disables eviction — unlimited cache (use for pure functions
# with small, finite input spaces like fibonacci, combinatorics).

print("=== Section 1: @lru_cache ===")

@lru_cache(maxsize=128)
def expensive_api_call(user_id: int, endpoint: str) -> dict:
    """
    Simulates an expensive external API call.
    With @lru_cache, repeated calls with the same args return cached result.
    """
    time.sleep(0.1)   # simulate 100ms network latency
    return {"user_id": user_id, "endpoint": endpoint, "data": f"result_{user_id}"}


# First call: slow (cache miss)
start = time.perf_counter()
r1 = expensive_api_call(42, "/profile")
print(f"  First call (miss):  {(time.perf_counter()-start)*1000:.1f}ms → {r1}")

# Second call: fast (cache hit)
start = time.perf_counter()
r2 = expensive_api_call(42, "/profile")   # same args → cache hit
print(f"  Second call (hit):  {(time.perf_counter()-start)*1000:.1f}ms → {r2}")

# Cache stats
info = expensive_api_call.cache_info()
print(f"  Cache stats: hits={info.hits}, misses={info.misses}, "
      f"maxsize={info.maxsize}, currsize={info.currsize}")

# Different args → new cache entry
expensive_api_call(99, "/settings")
print(f"  After different args: currsize={expensive_api_call.cache_info().currsize}")

# Invalidate cache
expensive_api_call.cache_clear()
print(f"  After cache_clear(): currsize={expensive_api_call.cache_info().currsize}")


# =============================================================================
# SECTION 2: TTL Cache — time-based expiration
# =============================================================================

# CONCEPT: @lru_cache never expires entries. For data that changes (user
# profiles, config, prices), you need TTL (time-to-live) expiration.
# After TTL seconds, the next call fetches fresh data.

print("\n=== Section 2: TTL Cache ===")

def ttl_cache(maxsize: int = 128, ttl_seconds: float = 60.0):
    """
    Decorator factory: caches results with time-to-live expiration.
    Each cached entry expires individually `ttl_seconds` after it was stored.
    Thread-safe via a Lock.
    """
    def decorator(func: Callable) -> Callable:
        cache: dict        = {}       # key → (value, expiry_timestamp)
        lock: threading.Lock = threading.Lock()

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build a hashable cache key from all arguments
            key = (args, tuple(sorted(kwargs.items())))

            with lock:
                if key in cache:
                    value, expiry = cache[key]
                    if time.time() < expiry:
                        wrapper.hits += 1
                        return value
                    else:
                        del cache[key]   # expired — remove stale entry

            # Cache miss or expired — call the real function (outside lock)
            result = func(*args, **kwargs)

            with lock:
                # Evict oldest entry if over maxsize (simple FIFO eviction)
                if len(cache) >= maxsize:
                    oldest_key = next(iter(cache))
                    del cache[oldest_key]
                cache[key] = (result, time.time() + ttl_seconds)
                wrapper.misses += 1

            return result

        wrapper.hits   = 0
        wrapper.misses = 0
        wrapper.cache  = cache
        wrapper.invalidate = lambda: cache.clear()
        return wrapper
    return decorator


@ttl_cache(maxsize=100, ttl_seconds=0.2)   # expires after 200ms
def get_user_profile(user_id: int) -> dict:
    """Simulates fetching a user profile from DB."""
    time.sleep(0.05)   # 50ms DB latency
    return {"user_id": user_id, "name": f"User_{user_id}", "fetched_at": time.time()}


# First call: miss
start = time.perf_counter()
p1 = get_user_profile(1)
print(f"  First call:   {(time.perf_counter()-start)*1000:.1f}ms")

# Second call within TTL: hit
start = time.perf_counter()
p2 = get_user_profile(1)
print(f"  Second call:  {(time.perf_counter()-start)*1000:.1f}ms (cached)")

# Wait for expiry
time.sleep(0.25)

# Call after TTL: miss again
start = time.perf_counter()
p3 = get_user_profile(1)
print(f"  After TTL:    {(time.perf_counter()-start)*1000:.1f}ms (expired, re-fetched)")

print(f"  Stats: hits={get_user_profile.hits}, misses={get_user_profile.misses}")
print(f"  fetched_at changed: {p1['fetched_at'] != p3['fetched_at']}")


# =============================================================================
# SECTION 3: LRU Cache from scratch — understanding the internals
# =============================================================================

# CONCEPT: LRU cache internals. An OrderedDict maintains insertion order AND
# supports move_to_end(), making it perfect for LRU. On access, move the
# entry to the end (most recently used). On eviction, pop from the front (LRU).

print("\n=== Section 3: LRU Cache Implementation ===")

class LRUCache:
    """
    Manual LRU cache — O(1) get and put.
    Uses OrderedDict: dict for O(1) lookup + doubly-linked list for O(1) ordering.
    WHY BUILD THIS: used in coding interviews + understanding cache internals.
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self._cache: OrderedDict = OrderedDict()
        self.hits   = 0
        self.misses = 0

    def get(self, key: Any) -> Optional[Any]:
        if key not in self._cache:
            self.misses += 1
            return None
        # Move to end — marks as most recently used
        self._cache.move_to_end(key)
        self.hits += 1
        return self._cache[key]

    def put(self, key: Any, value: Any) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self.capacity:
            # Remove least recently used — first item in OrderedDict
            evicted = self._cache.popitem(last=False)
            print(f"  [LRU evicted]: {evicted[0]!r}")

    def __len__(self) -> int:
        return len(self._cache)

    def __repr__(self) -> str:
        order = list(self._cache.keys())
        return f"LRUCache(cap={self.capacity}, items={order}, hits={self.hits}, misses={self.misses})"


cache = LRUCache(capacity=3)
cache.put("a", 1)
cache.put("b", 2)
cache.put("c", 3)
print(f"  {cache}")

cache.get("a")            # "a" moves to MRU
cache.put("d", 4)         # evicts "b" (LRU)
print(f"  After accessing 'a' and adding 'd': {cache}")

print(f"  get('b') = {cache.get('b')}")   # None — evicted
print(f"  get('a') = {cache.get('a')}")   # 1 — still in cache


# =============================================================================
# SECTION 4: Cache strategies — when and how to invalidate
# =============================================================================

# CONCEPT: Cache invalidation is famously hard. Three common strategies:
# 1. TTL: expire after a fixed duration (simple, eventually consistent)
# 2. Event-driven: invalidate when the underlying data changes (accurate)
# 3. Write-through: update cache AND storage simultaneously (no stale reads)

print("\n=== Section 4: Cache Invalidation Strategies ===")

class UserCache:
    """
    Demonstrates three invalidation strategies for a user data cache.
    In production, combine event-driven (primary) with TTL (safety net).
    """

    def __init__(self, ttl: float = 5.0):
        self._data: dict   = {}     # cache store: id → (user, expiry)
        self._ttl          = ttl
        self._db: dict     = {}     # simulated database

    # --- Write-through strategy ---
    def write_through(self, user_id: int, user: dict) -> None:
        """Write to BOTH DB and cache simultaneously — no stale reads."""
        self._db[user_id] = user                          # persist
        self._data[user_id] = (user, time.time() + self._ttl)   # cache
        print(f"  [write-through] user {user_id} saved to DB + cache")

    # --- Event-driven invalidation ---
    def invalidate(self, user_id: int) -> None:
        """Remove cache entry when we KNOW the data changed."""
        if user_id in self._data:
            del self._data[user_id]
            print(f"  [invalidated] cache cleared for user {user_id}")

    # --- TTL check on read ---
    def get(self, user_id: int) -> Optional[dict]:
        if user_id in self._data:
            user, expiry = self._data[user_id]
            if time.time() < expiry:
                print(f"  [cache hit] user {user_id}")
                return user
            del self._data[user_id]
            print(f"  [TTL expired] user {user_id}")

        # Cache miss — load from DB
        if user_id in self._db:
            user = self._db[user_id]
            self._data[user_id] = (user, time.time() + self._ttl)
            print(f"  [cache miss→DB] user {user_id}")
            return user

        return None


uc = UserCache(ttl=0.3)
uc.write_through(1, {"name": "Alice", "role": "admin"})
print(f"  get(1): {uc.get(1)}")
print(f"  get(1): {uc.get(1)}")   # hit

uc.invalidate(1)
print(f"  get(1): {uc.get(1)}")   # miss → DB

time.sleep(0.35)
print(f"  get(1) after TTL: {uc.get(1)}")  # expired → DB again


# =============================================================================
# SECTION 5: Caching in a web-style request pipeline
# =============================================================================

# CONCEPT: In web applications, caches live at multiple layers:
# - In-process cache: fastest, lost on restart, not shared between workers
# - Redis/Memcached: shared across workers, survives restart
# - CDN/HTTP cache: for static content and GET responses
# This example simulates a request pipeline with a multi-layer cache.

print("\n=== Section 5: Multi-Layer Cache (Request Pipeline) ===")

class RequestCache:
    """Simulates in-process cache keyed on request URL + params."""

    def __init__(self, ttl: float = 1.0):
        self._store: dict = {}
        self._ttl         = ttl

    def _make_key(self, url: str, params: dict) -> str:
        payload   = json.dumps({"url": url, "params": params}, sort_keys=True)
        return hashlib.md5(payload.encode()).hexdigest()[:12]

    def get(self, url: str, params: dict) -> Optional[Any]:
        key = self._make_key(url, params)
        if key in self._store:
            value, expiry = self._store[key]
            if time.time() < expiry:
                return value
            del self._store[key]
        return None

    def set(self, url: str, params: dict, value: Any) -> None:
        key = self._make_key(url, params)
        self._store[key] = (value, time.time() + self._ttl)

    def stats(self) -> dict:
        return {"entries": len(self._store)}


def simulate_db_query(user_id: int) -> dict:
    time.sleep(0.05)   # 50ms latency
    return {"user_id": user_id, "name": f"User_{user_id}", "role": "viewer"}


def handle_request(url: str, params: dict, cache: RequestCache) -> dict:
    """Request handler: check cache first, fall back to DB."""
    cached = cache.get(url, params)
    if cached is not None:
        return {"source": "cache", "data": cached}

    # Cache miss: call the DB
    data = simulate_db_query(params.get("user_id", 0))
    cache.set(url, params, data)
    return {"source": "db", "data": data}


req_cache = RequestCache(ttl=0.5)
requests  = [
    ("/api/user", {"user_id": 1}),
    ("/api/user", {"user_id": 2}),
    ("/api/user", {"user_id": 1}),   # cache hit
    ("/api/user", {"user_id": 2}),   # cache hit
    ("/api/user", {"user_id": 3}),
]

for url, params in requests:
    start = time.perf_counter()
    result = handle_request(url, params, req_cache)
    elapsed = (time.perf_counter() - start) * 1000
    print(f"  GET {url}?user_id={params['user_id']}: "
          f"source={result['source']:5}  {elapsed:.1f}ms")


print("\n=== Caching complete ===")
print("Cache selection guide:")
print("  @lru_cache          → pure functions with hashable args, permanent data")
print("  @ttl_cache          → data that changes over time (user profiles, prices)")
print("  LRU class           → shared cache with manual control (shared by many callers)")
print("  Write-through       → strong consistency requirement")
print("  Event invalidation  → accuracy when you know exactly when data changes")
print("  TTL                 → simple, eventual consistency is acceptable")
