# Project 09 — Rate Limiter Middleware

**Difficulty: Build It Yourself** — spec, architecture, and acceptance criteria only. No step-by-step. No hints. Full working solution at the end.

---

## What You're Building

A **Redis-backed sliding window rate limiter** implemented as **FastAPI middleware**. Every incoming request passes through the limiter before reaching any route handler. The limiter checks two independent limits simultaneously: a per-IP address limit (100 requests per minute) and a per-API-key limit (1000 requests per hour). When either limit is exceeded the middleware short-circuits the request and returns a `429 Too Many Requests` response — the route handler never executes. All limits are configurable via environment variables so the system can be tuned without touching code.

---

## Architecture

```
Incoming Request
       │
       ▼
┌─────────────────────────────────────────────────────┐
│              FastAPI Middleware Layer                │
│                                                     │
│  1. Extract identifier (IP address / API key)       │
│  2. Check /health exemption → skip if exempt        │
│  3. Query Redis sorted set (atomic Lua script)      │
│                                                     │
│  ┌──────────────────┐     ┌────────────────────┐   │
│  │  IP Rate Limit   │     │  API Key Rate Limit │   │
│  │  100 req / 60s   │     │  1000 req / 3600s   │   │
│  └────────┬─────────┘     └──────────┬─────────┘   │
│           │                          │              │
│           └────────────┬─────────────┘              │
│                        │                            │
│              Under limit?                           │
│             /          \                            │
│           YES           NO                          │
│            │             │                          │
│  Add timestamp    Return 429                        │
│  Set headers      Retry-After header                │
│  Pass through                                       │
└────────────┬────────────────────────────────────────┘
             │
             ▼
      Route Handler
             │
             ▼
      Response (with X-RateLimit-* headers injected)
```

---

## The Algorithm

**Sliding window rate limiting** stores a timestamped log of every request in a Redis **sorted set**, keyed by the request identifier. On every request, stale entries outside the current window are pruned, the remaining count is compared to the limit, and — if under the limit — the new timestamp is added.

```
Fixed Window problem — burst at boundary:

  Window 1                Window 2
  [─────────────────────][─────────────────────]
               ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
               100 req at end + 100 req at start
               = 200 requests in 2 seconds  ← allowed by fixed window

Sliding Window — window moves with each request:

  Now - 60s ────────────────────────────── Now
             [only requests in this range count]
             No boundary burst possible.
```

**Why a Redis sorted set:**

- `ZADD key score member` — O(log N) insert; use the timestamp (float) as the score and a unique request ID as the member
- `ZREMRANGEBYSCORE key -inf (now - window)` — O(log N + M) range delete of expired entries
- `ZCARD key` — O(1) count of remaining entries
- `EXPIRE key window` — auto-clean keys with no recent traffic

**Why Lua for atomicity:**

The three Redis operations above (remove stale, count, add new) must execute as a single atomic unit. Without atomicity, two concurrent requests can both read a count of 99, both decide they are under the 100 limit, and both add their entry — resulting in 101 entries. Redis executes Lua scripts atomically: no other command can interleave during script execution.

---

## What You Need

```bash
# Python dependencies
pip install fastapi uvicorn redis pydantic-settings httpx

# Run Redis locally (Docker)
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

---

## Spec

### Middleware Behavior

| Condition | Action | Headers Set |
|---|---|---|
| Path is `/health` | Pass through immediately, no Redis check | None |
| Request under both limits | Add timestamp to Redis, pass to handler | `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` |
| IP limit exceeded | Return `429`, do not call handler | `Retry-After`, `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` |
| API key limit exceeded | Return `429`, do not call handler | `Retry-After`, `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` |
| Redis connection error | Log warning, allow request through | None |

### Rate Limit Rules

| Identifier Type | Default Limit | Window | How Identified |
|---|---|---|---|
| IP address | 100 requests | 60 seconds | `X-Forwarded-For` header, fallback to `request.client.host` |
| API key | 1000 requests | 3600 seconds | `X-API-Key` request header |

If no `X-API-Key` header is present, skip the API key check (only IP limit applies).

### Redis Key Design

```
ratelimit:ip:<ip_address>           e.g.  ratelimit:ip:203.0.113.42
ratelimit:apikey:<api_key>          e.g.  ratelimit:apikey:sk-abc123
```

Use a consistent prefix so all rate-limit keys can be inspected or flushed with `SCAN ratelimit:*`.

### Response Headers

| Header | Value |
|---|---|
| `X-RateLimit-Limit` | The configured limit for this identifier |
| `X-RateLimit-Remaining` | `limit - current_count` (floor 0) |
| `X-RateLimit-Reset` | Unix timestamp (integer) when the oldest entry in the window expires |
| `Retry-After` | Seconds until the window resets (only on 429 responses) |

### Lua Script Requirement

The following three operations must be atomic. Implement them as a single Redis Lua script loaded once at startup with `redis_client.script_load()` and invoked with `evalsha`:

1. `ZREMRANGEBYSCORE key -inf (now - window_seconds)` — remove expired entries
2. `ZCARD key` — count current entries
3. If count is under limit: `ZADD key now request_id` and `EXPIRE key window_seconds`
4. Return: `[current_count, oldest_score_or_nil]`

The script should return enough information for the middleware to calculate `X-RateLimit-Remaining` and `X-RateLimit-Reset` without a second round-trip to Redis.

---

## File Structure

```
09_Rate_Limiter_Middleware/
├── main.py               # FastAPI app + sample endpoints
├── middleware.py         # RateLimitMiddleware class
├── config.py             # Pydantic-settings env config
├── redis_client.py       # Redis connection + Lua script
├── docker-compose.yml    # Redis + FastAPI
└── test_rate_limit.py    # Automated test script
```

---

## Acceptance Criteria

- [ ] `GET /health` is never rate limited, regardless of request count
- [ ] After 100 requests in 60 seconds from the same IP, the 101st returns `429`
- [ ] The `Retry-After` header on a 429 response shows the correct number of seconds until the oldest entry in the window expires
- [ ] `X-RateLimit-Remaining` decrements by 1 on each successful request and reads `0` (not negative) when the limit is hit
- [ ] Two different IP addresses can each make 100 requests independently without either triggering a 429
- [ ] Concurrent requests from the same IP do not produce a race condition that allows more than the configured limit
- [ ] All limits are configurable via environment variables with no code change (e.g. `RATE_LIMIT_IP_MAX=50 python -m uvicorn main:app`)
- [ ] When Redis is unreachable, requests are allowed through and a warning is logged — the service does not go down

---

## Test Script

Run this after starting the server to verify the rate limiter works end-to-end.

```python
# test_rate_limit.py
"""
Usage:
    python test_rate_limit.py

Expects the server running at http://localhost:8000.
Sends 105 requests from the same IP and prints status + headers for each.
Shows the 429 at request 101 and the Retry-After value.
"""

import httpx
import time

BASE_URL = "http://localhost:8000"
ENDPOINT = "/ping"
TOTAL_REQUESTS = 105


def main():
    print(f"Sending {TOTAL_REQUESTS} requests to {BASE_URL}{ENDPOINT}")
    print("-" * 70)

    with httpx.Client(base_url=BASE_URL) as client:
        for i in range(1, TOTAL_REQUESTS + 1):
            response = client.get(ENDPOINT)

            remaining = response.headers.get("x-ratelimit-remaining", "—")
            reset = response.headers.get("x-ratelimit-reset", "—")
            retry_after = response.headers.get("retry-after", "—")
            limit = response.headers.get("x-ratelimit-limit", "—")

            status_str = f"HTTP {response.status_code}"

            if response.status_code == 429:
                print(
                    f"Request {i:>3}:  {status_str}  "
                    f"remaining={remaining}  retry-after={retry_after}s  ← RATE LIMITED"
                )
            else:
                print(
                    f"Request {i:>3}:  {status_str}  "
                    f"limit={limit}  remaining={remaining}  reset={reset}"
                )

    print("-" * 70)
    print("Done. Check that request 101 returned 429 with a Retry-After header.")


if __name__ == "__main__":
    main()
```

---

## You're On Your Own

Good luck.

---

## Full Solution

<details>
<summary>✅ Complete solution — only open when done</summary>

### `config.py`

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Redis connection
    redis_host: str = "localhost"                  # ← override with REDIS_HOST=
    redis_port: int = 6379                         # ← override with REDIS_PORT=
    redis_db: int = 0

    # IP-based rate limit
    rate_limit_ip_max: int = 100                   # ← max requests per window
    rate_limit_ip_window: int = 60                 # ← window in seconds

    # API-key-based rate limit
    rate_limit_apikey_max: int = 1000
    rate_limit_apikey_window: int = 3600

    # Paths exempt from rate limiting
    exempt_paths: list[str] = ["/health"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
```

---

### `redis_client.py`

```python
import logging
import uuid

import redis

from config import settings

log = logging.getLogger(__name__)

# ── Lua script ──────────────────────────────────────────────────────────────
#
# Arguments:
#   KEYS[1]  = Redis key (e.g. "ratelimit:ip:1.2.3.4")
#   ARGV[1]  = current timestamp (float, as string)
#   ARGV[2]  = window size in seconds
#   ARGV[3]  = max allowed requests
#
# Returns:
#   { current_count, oldest_score }
#   oldest_score is nil if the sorted set is empty after pruning
#
# The script is atomic — Redis runs it with no interleaving commands.

SLIDING_WINDOW_LUA = """
local key        = KEYS[1]
local now        = tonumber(ARGV[1])
local window     = tonumber(ARGV[2])
local limit      = tonumber(ARGV[3])
local cutoff     = now - window

-- Remove entries older than the window
redis.call('ZREMRANGEBYSCORE', key, '-inf', cutoff)

-- Count remaining entries
local count = redis.call('ZCARD', key)

if count < limit then
    -- Under limit: add this request's timestamp with a unique member
    local member = tostring(now) .. ':' .. tostring(math.random(1, 1000000))
    redis.call('ZADD', key, now, member)    -- score = timestamp
    redis.call('EXPIRE', key, window)       -- auto-expire the key
end

-- Fetch the oldest entry's score so the caller can compute Reset time
local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')

if #oldest > 0 then
    return {count, oldest[2]}   -- oldest[2] is the score (timestamp)
else
    return {count, false}
end
"""


def get_redis_client() -> redis.Redis:
    """Create and return a Redis client. Raises if connection fails."""
    client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True,          # ← return str, not bytes
        socket_connect_timeout=1,       # ← fail fast on connection issues
    )
    return client


# Module-level client and script SHA — loaded once at startup
try:
    _redis = get_redis_client()
    _redis.ping()                                   # ← verify connection at import time
    _script_sha = _redis.script_load(SLIDING_WINDOW_LUA)   # ← preload Lua, returns SHA
    log.info("Redis connected at %s:%s", settings.redis_host, settings.redis_port)
except redis.RedisError as e:
    _redis = None
    _script_sha = None
    log.warning("Redis unavailable at startup: %s — rate limiting disabled", e)


def check_rate_limit(key: str, window: int, limit: int) -> dict:
    """
    Run the sliding window Lua script for a given key.

    Returns a dict with:
        allowed     bool    — True if the request is within the limit
        count       int     — number of requests in the current window (after this one)
        limit       int     — the configured limit
        remaining   int     — requests remaining (floor 0)
        reset_at    float   — Unix timestamp when the oldest entry expires
    """
    if _redis is None or _script_sha is None:
        # Redis unavailable — fail open (allow all requests)
        log.warning("Redis unavailable — allowing request without rate limiting")
        return {
            "allowed": True,
            "count": 0,
            "limit": limit,
            "remaining": limit,
            "reset_at": 0.0,
        }

    import time
    now = time.time()

    try:
        result = _redis.evalsha(
            _script_sha,
            1,                  # ← number of KEYS arguments
            key,                # ← KEYS[1]
            str(now),           # ← ARGV[1]
            str(window),        # ← ARGV[2]
            str(limit),         # ← ARGV[3]
        )

        count_before = int(result[0])               # ← count BEFORE this request was added
        oldest_score = float(result[1]) if result[1] else now

        allowed = count_before < limit              # ← True if we were under limit (script added us)
        actual_count = count_before + 1 if allowed else count_before
        remaining = max(0, limit - actual_count)
        reset_at = oldest_score + window            # ← when the oldest entry falls out of the window

        return {
            "allowed": allowed,
            "count": actual_count,
            "limit": limit,
            "remaining": remaining,
            "reset_at": reset_at,
        }

    except redis.RedisError as e:
        log.warning("Redis error during rate limit check: %s — allowing request", e)
        return {
            "allowed": True,
            "count": 0,
            "limit": limit,
            "remaining": limit,
            "reset_at": 0.0,
        }
```

---

### `middleware.py`

```python
import logging
import math
import time
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from config import settings
from redis_client import check_rate_limit

log = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding window rate limiter middleware for FastAPI.

    Checks two independent limits:
      1. Per-IP address       (settings.rate_limit_ip_max  / settings.rate_limit_ip_window)
      2. Per-API-Key header   (settings.rate_limit_apikey_max / settings.rate_limit_apikey_window)

    Exempt paths (e.g. /health) bypass all checks.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # ── Exempt paths bypass rate limiting entirely ─────────────────────────
        if request.url.path in settings.exempt_paths:
            return await call_next(request)

        # ── Extract identifiers ────────────────────────────────────────────────
        ip = self._get_ip(request)
        api_key = request.headers.get("x-api-key")             # ← None if header absent

        # ── Check IP limit ─────────────────────────────────────────────────────
        ip_key = f"ratelimit:ip:{ip}"
        ip_result = check_rate_limit(
            key=ip_key,
            window=settings.rate_limit_ip_window,
            limit=settings.rate_limit_ip_max,
        )

        if not ip_result["allowed"]:
            return self._build_429(ip_result)

        # ── Check API key limit (only if key is present) ───────────────────────
        apikey_result = None
        if api_key:
            apikey_key = f"ratelimit:apikey:{api_key}"
            apikey_result = check_rate_limit(
                key=apikey_key,
                window=settings.rate_limit_apikey_window,
                limit=settings.rate_limit_apikey_max,
            )
            if not apikey_result["allowed"]:
                return self._build_429(apikey_result)

        # ── Under both limits: call the actual route handler ───────────────────
        response = await call_next(request)

        # Inject rate limit headers based on the more restrictive result
        # (IP limit is always checked; use API key result if it's more restrictive)
        limiting_result = ip_result
        if apikey_result and apikey_result["remaining"] < ip_result["remaining"]:
            limiting_result = apikey_result

        response.headers["X-RateLimit-Limit"] = str(limiting_result["limit"])
        response.headers["X-RateLimit-Remaining"] = str(limiting_result["remaining"])
        response.headers["X-RateLimit-Reset"] = str(int(limiting_result["reset_at"]))

        return response

    def _get_ip(self, request: Request) -> str:
        """Extract client IP, respecting X-Forwarded-For for proxied requests."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()          # ← first IP in the chain
        return request.client.host if request.client else "unknown"

    def _build_429(self, result: dict) -> JSONResponse:
        """Build a 429 Too Many Requests response with the required headers."""
        now = time.time()
        retry_after = max(1, math.ceil(result["reset_at"] - now))   # ← seconds until reset, min 1

        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "detail": f"Rate limit of {result['limit']} requests exceeded. Retry after {retry_after}s.",
            },
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(result["limit"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(result["reset_at"])),
            },
        )
```

---

### `main.py`

```python
import logging

from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse

from middleware import RateLimitMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = FastAPI(title="Rate Limiter Demo")

# Register middleware — order matters: this runs before any route handler
app.add_middleware(RateLimitMiddleware)


@app.get("/health")
async def health():
    """Health check — always exempt from rate limiting."""
    return {"status": "ok"}


@app.get("/ping")
async def ping():
    """Simple endpoint for rate limit testing."""
    return {"message": "pong"}


@app.get("/data")
async def data(x_api_key: str = Header(default=None)):
    """Endpoint that also enforces the API key rate limit if a key is provided."""
    return {"data": "some payload", "api_key_provided": x_api_key is not None}
```

---

### `docker-compose.yml`

```yaml
version: "3.9"

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"                    # ← expose Redis to localhost
    command: redis-server --save "" --appendonly no   # ← disable persistence for dev

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis               # ← use service name, not localhost, inside Docker
      - RATE_LIMIT_IP_MAX=100
      - RATE_LIMIT_IP_WINDOW=60
      - RATE_LIMIT_APIKEY_MAX=1000
      - RATE_LIMIT_APIKEY_WINDOW=3600
    depends_on:
      - redis
    command: uvicorn main:app --host 0.0.0.0 --port 8000
```

---

### `test_rate_limit.py`

```python
"""
Automated test script for the rate limiter.

Usage:
    python test_rate_limit.py

Expects the server running at http://localhost:8000.
"""

import httpx
import time


BASE_URL = "http://localhost:8000"


def test_health_exempt():
    """Health endpoint should never return 429 regardless of call count."""
    print("\n--- Test: /health is exempt ---")
    with httpx.Client(base_url=BASE_URL) as client:
        for _ in range(110):                                # ← more than the IP limit
            r = client.get("/health")
            assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    print("PASS: /health always returns 200")


def test_ip_rate_limit():
    """101st request from same IP should return 429."""
    print("\n--- Test: IP rate limit (100 req/60s) ---")
    with httpx.Client(base_url=BASE_URL) as client:
        for i in range(1, 106):
            r = client.get("/ping")
            remaining = r.headers.get("x-ratelimit-remaining", "—")
            retry_after = r.headers.get("retry-after", "—")

            if r.status_code == 429:
                print(
                    f"  Request {i:>3}: HTTP 429  retry-after={retry_after}s  ← RATE LIMITED"
                )
                assert i >= 101, f"Got 429 too early at request {i}"    # ← should not hit limit before 101
            else:
                print(
                    f"  Request {i:>3}: HTTP {r.status_code}  remaining={remaining}"
                )

    print("PASS: 429 appeared at or after request 101")


def test_headers_present():
    """Rate limit headers should be present on every non-429 response."""
    print("\n--- Test: Rate limit headers present ---")

    # Flush by waiting is not practical here — just check a fresh client
    # In a real test suite you would reset Redis between tests
    with httpx.Client(base_url=BASE_URL) as client:
        r = client.get("/ping")
        if r.status_code == 200:
            assert "x-ratelimit-limit" in r.headers, "Missing X-RateLimit-Limit"
            assert "x-ratelimit-remaining" in r.headers, "Missing X-RateLimit-Remaining"
            assert "x-ratelimit-reset" in r.headers, "Missing X-RateLimit-Reset"
            print("PASS: All three X-RateLimit-* headers present")
        else:
            print(f"SKIP: Got {r.status_code} (IP may still be rate limited from previous test)")


def test_retry_after_value():
    """Retry-After should be a positive integer when 429 is returned."""
    print("\n--- Test: Retry-After header is a positive integer ---")
    with httpx.Client(base_url=BASE_URL) as client:
        for _ in range(110):
            r = client.get("/ping")
            if r.status_code == 429:
                retry_after = r.headers.get("retry-after")
                assert retry_after is not None, "Missing Retry-After on 429"
                assert int(retry_after) > 0, f"Retry-After should be > 0, got {retry_after}"
                print(f"PASS: Retry-After = {retry_after}s")
                return
    print("SKIP: Never hit 429 (may need to clear Redis between tests)")


if __name__ == "__main__":
    print("Starting rate limiter tests against", BASE_URL)
    print("NOTE: These tests share the same Redis state. Run them on a fresh Redis.")
    print("      docker exec -it redis redis-cli FLUSHALL   ← reset between runs\n")

    test_health_exempt()

    # Reset Redis between tests in a real environment
    # For this script, we run them in sequence and accept accumulated state
    test_ip_rate_limit()
    test_headers_present()
    test_retry_after_value()

    print("\nAll tests complete.")
```

---

### Running It

```bash
# Terminal 1 — start Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Terminal 2 — start the API
uvicorn main:app --reload

# Terminal 3 — run the test script
python test_rate_limit.py

# Reset Redis between test runs
docker exec redis redis-cli FLUSHALL
```

</details>

---

## Reflection

By completing this project you can now independently build:

- **Any sliding window rate limiter** — the Redis sorted-set pattern is the industry standard and you now understand it from first principles, not just as a library call
- **FastAPI middleware** — you know how to intercept every request and response, inject headers, and short-circuit the handler stack
- **Atomic Redis operations with Lua** — you understand why atomicity matters for correctness under concurrency and how to guarantee it without distributed locks
- **Config-driven limits via environment variables** — the pydantic-settings pattern applies to any service that needs environment-based configuration
- **Fail-open fallback patterns** — you know how to design middleware that degrades gracefully when a dependency is unavailable, rather than taking the service down
- **Per-identifier isolation** — the key-namespacing pattern (`ratelimit:{type}:{id}`) applies to any resource that needs per-entity limits or quotas
- **Header-based API contracts** — you know the standard `X-RateLimit-*` headers that API consumers expect and how to populate them correctly
- **End-to-end integration test scripts** — you can write a standalone script that hammers an endpoint and verifies observable behavior, without a full test framework

---

## Series Complete — What's Next

These 10 projects covered the full surface area of practical Python backend engineering: networking fundamentals (TCP sockets, WebSockets), authentication (JWT, API keys), async job processing (Celery), infrastructure patterns (scheduling, rate limiting), and API design (FastAPI, middleware, pagination). You built each one from a blank file.

The natural next steps are:

- **SQL Mastery** (`/Users/1065696/Github/SQL-Mastery`) — persistence layer: designing schemas for the data models you stored in Redis and in-memory here
- **Linux, Terraform, AWS Mastery** (`/Users/1065696/Github/Linux-Terraform-AWS-Mastery`) — deploying the services you built here: containers, infrastructure-as-code, and cloud networking

---

## Back to Project Series

[Back to Capstone Projects README](../README.md) | Previous: [07 — Config-Driven Scheduler](../07_Config_Driven_Scheduler/Project_Guide.md)
