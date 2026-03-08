# API Security

| Previous | [06 — WebSockets](../06_websockets/realtime_apis.md) |
|----------|------------------------------------------------------|
| Next     | [08 — API Gateway](../08_api_gateway/gateway_patterns.md) |
| Home     | [README.md](../README.md) |

---

## The Coffee Shop Scenario

Picture this. You're a senior engineer at a fintech startup. A junior dev on your team
just shipped a new `/payments` endpoint. Proud of the clean code, nice validation logic,
solid tests.

You pull up the PR and ask one question: "What happens if I call this from `curl` without
any credentials?"

Junior dev pauses. Pulls up a terminal. Runs it.

The payment goes through.

Anyone on the internet, with no credentials at all, can trigger a payment from your
system. That's what an unsecured API looks like.

This chapter is about making sure that never happens to you.

---

## The Three Questions Every API Must Answer

Before any request touches your business logic, your API needs to answer three questions:

```
┌────────────────────────────────────────────────────────────────┐
│                                                                  │
│   1. Who are you?        →  AUTHENTICATION                      │
│      (prove your identity)                                       │
│                                                                  │
│   2. What can you do?    →  AUTHORIZATION                       │
│      (what are you allowed to access?)                           │
│                                                                  │
│   3. Is this request valid?  →  INPUT VALIDATION                │
│      (is the data safe and well-formed?)                         │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

These three are distinct, and all three matter. Most security breaches come from
getting one of them wrong — often the second one.

- A system with no authentication lets anyone in.
- A system with authentication but no authorization lets authenticated users access
  everyone else's data. (This is called an IDOR — Insecure Direct Object Reference.
  Very common. Very bad.)
- A system that doesn't validate input is vulnerable to injection attacks, even if
  authentication and authorization are perfect.

Let's build up each layer.

---

## API Keys — The Simplest Form of Machine Identity

API keys are the oldest trick in the book, and for a lot of use cases, still the
right tool.

The concept is brutally simple: the server generates a random token, gives it to the
client, and the client sends it with every request. The server recognizes the token
and knows who's asking.

```
Server generates:  sk-abc123xyz789...  (a long random string)
                         │
                         ▼
              Client stores this key securely

Client makes request:
  GET /data
  Authorization: ApiKey sk-abc123xyz789...
                         │
                         ▼
              Server looks up the key → identifies the caller
              → checks permissions → serves the response
```

### When to use API keys

API keys are the right choice when:
- It's server-to-server communication (no human user involved)
- You need simple auth with no user context
- The client is a trusted application you control or that a developer registered
- Examples: calling OpenAI's API, calling Stripe from your backend, a webhook secret

API keys are the wrong choice when:
- You need per-user permissions (use OAuth/JWT instead)
- You need short-lived credentials that expire
- The key might end up in a mobile app binary (that's dangerous — anyone can extract it)

### Sending API keys

The right way — in the Authorization header:

```
Authorization: ApiKey sk-abc123xyz789
```

or using Bearer:

```
Authorization: Bearer sk-abc123xyz789
```

Some APIs use a custom header:

```
X-API-Key: sk-abc123xyz789
```

The wrong way — as a query parameter:

```
GET /data?api_key=sk-abc123xyz789   ← BAD: shows up in server logs, browser history,
                                       access logs. Keys leak everywhere.
```

Never put an API key in a URL. It will end up in a log file somewhere, guaranteed.

### Storing API keys on the server side

Here's a critical point that many developers miss: **you should never store API keys
in plain text on your server.**

Store a hash of the key:

```python
import hashlib
import secrets

def generate_api_key():
    # Generate a cryptographically random key
    raw_key = secrets.token_urlsafe(32)  # e.g., "sk-" + random bytes
    full_key = f"sk-{raw_key}"

    # Hash it for storage
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()

    # Store key_hash in the database (NOT full_key)
    # Return full_key to the user ONCE — they need to save it
    return full_key, key_hash

def verify_api_key(provided_key: str, stored_hash: str) -> bool:
    # Hash what the client sent and compare
    provided_hash = hashlib.sha256(provided_key.encode()).hexdigest()
    return secrets.compare_digest(provided_hash, stored_hash)
```

Why hash? Because if your database is ever breached, the attacker gets hashes —
useless without the originals. Same reason you hash passwords.

Use `secrets.compare_digest()` instead of `==` to prevent timing attacks.

Never log the raw key. Not in access logs, not in error logs, nowhere.

---

## OAuth 2.0 — The Delegation Protocol

Here's a scenario you've lived a hundred times: you click "Sign in with Google" on
some app. You get redirected to Google, you approve the app's permissions, and you're
logged in — without ever giving the app your Google password.

That's OAuth 2.0. It's a delegation protocol. You're delegating some of your
permissions to another application, without sharing your credentials.

The mental model: "You let Spotify access your Google contacts without giving
Spotify your Google password."

OAuth 2.0 has several "flows" (officially called grant types). Two matter most:

### Authorization Code Flow — for web apps with a user

This is the flow behind "Sign in with Google," "Login with GitHub," every social
login button you've ever clicked.

```
┌──────────┐        ┌──────────────┐        ┌─────────────────┐
│  User's  │        │  Your App    │        │  Auth Server    │
│ Browser  │        │  (Client)    │        │  (e.g. Google)  │
└────┬─────┘        └──────┬───────┘        └────────┬────────┘
     │                     │                          │
     │  1. Click "Login     │                          │
     │     with Google"    │                          │
     │ ──────────────────> │                          │
     │                     │  2. Redirect to Google   │
     │                     │     with client_id,      │
     │                     │     redirect_uri, scope  │
     │ <────────────────── │ ───────────────────────> │
     │                     │                          │
     │  3. User sees Google login page                │
     │ ──────────────────────────────────────────── > │
     │                     │                          │
     │  4. User approves   │                          │
     │ <──────────────────────────────────────────── │
     │                     │                          │
     │  5. Google redirects back with auth_code       │
     │ ──────────────────> │                          │
     │                     │  6. Exchange auth_code   │
     │                     │     for access_token     │
     │                     │ ───────────────────────> │
     │                     │                          │
     │                     │  7. Returns access_token │
     │                     │     + refresh_token      │
     │                     │ <─────────────────────── │
     │                     │                          │
     │  8. User logged in  │                          │
     │ <────────────────── │                          │
```

Why the two-step (auth code → token exchange)? Because step 5 happens in the browser's
URL bar, which is visible. The auth code is short-lived and useless without the client
secret. The actual token exchange (step 6) happens server-to-server, never touching
the browser. This is the security win.

Key terms:
- **client_id** — public identifier for your app (not secret)
- **client_secret** — your app's password (keep this server-side, never in a browser)
- **scope** — what permissions you're requesting (`read:email`, `write:calendar`, etc.)
- **auth_code** — temporary code, valid for ~10 minutes, one-time use
- **access_token** — what you actually use to make API calls, short-lived (1 hour typ.)
- **refresh_token** — long-lived token to get new access tokens without re-logging in

### Client Credentials Flow — for machine-to-machine

No user involved. Your backend service needs to call another backend service.

```
┌──────────────────┐                    ┌─────────────────┐
│   Your Service   │                    │  Auth Server    │
│   (Client)       │                    │                 │
└────────┬─────────┘                    └────────┬────────┘
         │                                        │
         │  POST /oauth/token                     │
         │  client_id=abc                         │
         │  client_secret=xyz                     │
         │  grant_type=client_credentials         │
         │ ─────────────────────────────────────> │
         │                                        │
         │  200 OK                                │
         │  { "access_token": "...",              │
         │    "expires_in": 3600 }                │
         │ <───────────────────────────────────── │
         │                                        │
         │  GET /api/resource                     │
         │  Authorization: Bearer <access_token>  │
         │ ─────────────────────────────────────> │ (resource server)
```

Simple. Trade your credentials for a token. Use the token. When it expires, get a
new one.

### Access token and refresh token lifecycle

```
┌──────────────────────────────────────────────────────────┐
│                                                            │
│  access_token  — short lived (15 min to 1 hour)           │
│                  sent with every API call                  │
│                  if expired → get a new one                │
│                                                            │
│  refresh_token — long lived (days to months)              │
│                  stored securely (DB, not localStorage)    │
│                  used only to exchange for new             │
│                  access_token                              │
│                  if this expires → user must log in again  │
│                                                            │
└──────────────────────────────────────────────────────────┘

Flow when access_token expires:

  1. API call returns 401 Unauthorized
  2. Client detects expired token
  3. POST /oauth/token
       grant_type=refresh_token
       refresh_token=<stored_refresh_token>
  4. Server returns new access_token (and sometimes new refresh_token)
  5. Retry original request with new token
  6. User never noticed anything
```

---

## JWT — Stateless Auth Tokens

Every time a user makes an API call, your server needs to verify who they are. The
naive approach: store a session ID in a database, look it up on every request. Works
fine until you have 10 servers and need to share session state across all of them.

JWT (JSON Web Token, pronounced "jot") solves this differently: the token itself
contains the user's identity. No database lookup needed.

### Structure: header.payload.signature

A JWT looks like this:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MiIsIm5hbWUiOiJBbGljZSIsImV4cCI6MTcwOTkwMDAwMH0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Three parts, separated by dots. Each part is base64url encoded:

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9                       │
│  └─────────────────── HEADER ───────────────────┘            │
│  {                                                            │
│    "alg": "HS256",   ← signing algorithm                     │
│    "typ": "JWT"                                               │
│  }                                                            │
│                                                               │
│  eyJzdWIiOiI0MiIsIm5hbWUiOiJBbGljZSIsImV4cCI6MTcwOTkwMDAwMH0│
│  └─────────────────── PAYLOAD ──────────────────┘            │
│  {                                                            │
│    "sub": "42",          ← subject (user ID)                  │
│    "name": "Alice",                                           │
│    "exp": 1709900000,    ← expiration (Unix timestamp)        │
│    "iat": 1709896400,    ← issued at                          │
│    "iss": "api.myapp.com", ← issuer                           │
│    "roles": ["user", "admin"]                                 │
│  }                                                            │
│                                                               │
│  SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c                │
│  └─────────────────── SIGNATURE ────────────────┘            │
│  HMAC-SHA256(base64(header) + "." + base64(payload), secret) │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

The signature is the key. The server signs the header + payload with a secret key.
When it receives a token, it re-computes the signature and checks it matches. If
anyone tampered with the payload, the signature won't match.

Important: the payload is **not encrypted**, it's just base64 encoded. Anyone can
decode and read it. Don't put secrets in the payload.

### What goes IN the payload

```python
# Standard claims (defined by the JWT spec)
{
    "sub": "user_42",           # subject — who the token is about
    "iss": "api.myapp.com",     # issuer — who created the token
    "aud": "myapp.com",         # audience — who should accept it
    "exp": 1709900000,          # expiration time (Unix timestamp)
    "iat": 1709896400,          # issued at
    "jti": "uuid-v4-here",      # JWT ID — unique identifier for this token
}

# Custom claims you might add
{
    "user_id": 42,
    "email": "alice@example.com",   # low-sensitivity info is ok
    "roles": ["admin", "user"],
    "plan": "pro",
    "org_id": 7,
}
```

### What does NOT go in the payload

```
NEVER put in JWT payload:
  - Passwords or password hashes
  - Full PII (SSN, credit card numbers, passport numbers)
  - Secrets or API keys
  - Anything you don't want the user to read (they can decode it)
  - Data that changes frequently (roles might be stale by the time token expires)
```

### Validating a JWT — three checks required

```python
import jwt  # PyJWT library: pip install PyJWT

def validate_token(token: str, secret: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],    # MUST specify — prevents alg:none attack
            options={
                "require": ["exp", "iss", "sub"]   # require these claims
            },
            issuer="api.myapp.com",  # validates iss claim
            audience="myapp.com",    # validates aud claim
        )
        # If we get here: signature valid, token not expired, iss/aud correct
        return payload

    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired")
    except jwt.InvalidSignatureError:
        raise AuthError("Invalid token signature")
    except jwt.DecodeError:
        raise AuthError("Malformed token")
    except jwt.InvalidIssuerError:
        raise AuthError("Token issued by wrong authority")
```

The three checks in order:
1. **Verify the signature** — was this token issued by someone with the secret?
2. **Check expiration** (`exp`) — has the token expired?
3. **Check issuer** (`iss`) — was this issued by who we expect?

### Generating a JWT

```python
import jwt
import datetime

SECRET_KEY = "your-256-bit-secret"  # in prod: load from env var, use RS256

def create_access_token(user_id: int, email: str, roles: list) -> str:
    now = datetime.datetime.utcnow()

    payload = {
        "sub": str(user_id),
        "email": email,
        "roles": roles,
        "iat": now,
        "exp": now + datetime.timedelta(minutes=15),  # short-lived!
        "iss": "api.myapp.com",
    }

    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def create_refresh_token(user_id: int) -> str:
    now = datetime.datetime.utcnow()

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": now,
        "exp": now + datetime.timedelta(days=30),
        "iss": "api.myapp.com",
    }

    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

### The refresh token pattern

```
  Login:
    POST /auth/login  {email, password}
    → 200 OK  {
        "access_token": "eyJ...",    ← valid 15 minutes
        "refresh_token": "eyJ...",   ← valid 30 days
      }

  Normal API call:
    GET /api/profile
    Authorization: Bearer <access_token>
    → 200 OK  {...}

  When access_token expires:
    API call → 401 Unauthorized
    POST /auth/refresh  {refresh_token: "eyJ..."}
    → 200 OK  {
        "access_token": "eyJ...",   ← brand new token
      }

  Logout:
    POST /auth/logout
    → Server invalidates the refresh_token (add to a blocklist)
    → Access tokens expire naturally after 15 min
```

The access token is short-lived so a stolen token has limited damage. The refresh
token is long-lived but only used in one endpoint, making it easier to monitor and
invalidate.

### JWT pitfalls

**The `alg: none` attack**

Early JWT libraries had a bug: if you set `alg: none` in the header, they'd skip
signature verification entirely. An attacker could forge any token.

```
# Malicious token with alg:none — DO NOT DO THIS
header = base64({"alg": "none", "typ": "JWT"})
payload = base64({"sub": "admin", "roles": ["superadmin"], "exp": 9999999999})
signature = ""  # empty!

token = header + "." + payload + "."
# Some old libraries would accept this!
```

The fix: always explicitly specify which algorithms are acceptable when decoding.
Never accept `alg: none`.

**HS256 vs RS256 — symmetric vs asymmetric**

```
HS256 (HMAC-SHA256) — symmetric
  - One shared secret key used to both sign and verify
  - Simple, fast
  - Problem: anyone who can verify tokens can also FORGE tokens
  - Use when: your auth server and resource server are the same service

RS256 (RSA-SHA256) — asymmetric
  - Private key to sign (only auth server has this)
  - Public key to verify (every service can have this)
  - A service that can verify tokens CANNOT forge them
  - Use when: multiple services need to verify tokens (microservices)
```

In production with multiple services, use RS256. Publish your public key at a
well-known URL (e.g., `/.well-known/jwks.json`). Each service fetches it and
verifies tokens locally. Your auth server's private key never leaves it.

---

## Rate Limiting — One Bad Actor Shouldn't Take Down Your API

Here's a real scenario: someone writes a scraper that hammers your `/search` endpoint
10,000 times per minute. Maybe it's malicious, maybe it's just a while loop with no
sleep. Either way, your API falls over for everyone.

Rate limiting says: "You get N requests per time window. After that, slow down."

### The Token Bucket Algorithm

The most popular algorithm for rate limiting. Intuitive once you visualize it.

```
Imagine a bucket that holds tokens.

┌────────────────────────────────────────┐
│                                         │
│   Bucket capacity: 100 tokens           │
│   Refill rate: 10 tokens/second         │
│                                         │
│   Current tokens: ████████░░  80       │
│                                         │
└────────────────────────────────────────┘

Each request consumes 1 token.
The bucket refills at 10 tokens/second (up to the max of 100).

If the bucket is empty → 429 Too Many Requests.
Burst allowed: up to 100 requests instantly (if bucket is full).
Sustained rate: 10 requests/second.
```

This is great for real users with occasional bursts — they can fire off several
quick requests (depleting the bucket), then the bucket refills for their next
activity.

### The Leaky Bucket Algorithm

Similar concept, different behavior.

```
Requests come IN at any rate.
Requests go OUT at a fixed rate.

   Incoming requests
         │
         ▼
  ┌──────────────┐   Requests queue up here
  │   bucket     │   Overflow → 429 (bucket full)
  │              │
  │   capacity   │
  └──────┬───────┘
         │
         │  Fixed output rate (e.g. 10 req/sec)
         ▼
    API handler
```

The leaky bucket smooths out bursts. Traffic is processed at a constant rate
regardless of how fast it comes in. Good for protecting downstream services from
traffic spikes.

Token bucket allows bursts. Leaky bucket eliminates them.

### Fixed Window vs Sliding Window

**Fixed window:** reset the counter every N seconds on a clock boundary.

```
Window: 60 seconds, limit: 100 requests

  |── 00:00 ─────────────── 01:00 ──|── 01:00 ─────── 02:00 ──|
  |  counter: 0...100               |  counter resets to 0     |

Problem: The edge case
  At 00:59, user sends 100 requests. Counter hits 100.
  At 01:00, window resets.
  At 01:01, user sends 100 more requests. All accepted.

  In 2 seconds, the user sent 200 requests.
  Your "100 per minute" limit is effectively 200 at the window boundary.
```

**Sliding window:** consider the last N seconds, not a fixed clock window.

```
Window: 60 seconds, limit: 100 requests

  Now: 01:30
  Look back 60 seconds: 00:30 → 01:30
  Count requests in that range: 47
  Remaining: 53

  At 01:31:
  Look back: 00:31 → 01:31
  The old requests from 00:30 dropped off.
  Remaining increases.
```

Sliding window is more accurate and eliminates the edge case, but requires
storing per-request timestamps (more memory, more complex). Redis sorted sets
work well for this.

### Implementing rate limiting with Redis

```python
import redis
import time

r = redis.Redis(host='localhost', port=6379)

def is_rate_limited(user_id: str, limit: int = 100, window_seconds: int = 60) -> bool:
    """
    Fixed window rate limiter using Redis INCR + EXPIRE.
    Returns True if the request should be blocked.
    """
    key = f"rate_limit:{user_id}:{int(time.time() // window_seconds)}"

    # Increment the counter for this window
    count = r.incr(key)

    # On first request in window, set the expiration
    if count == 1:
        r.expire(key, window_seconds * 2)  # 2x window for safety

    return count > limit

def get_rate_limit_status(user_id: str, limit: int = 100, window_seconds: int = 60):
    """Returns remaining requests and reset time."""
    window_key = int(time.time() // window_seconds)
    key = f"rate_limit:{user_id}:{window_key}"

    count = int(r.get(key) or 0)
    remaining = max(0, limit - count)
    reset_at = (window_key + 1) * window_seconds

    return {
        "limit": limit,
        "remaining": remaining,
        "reset": reset_at,
    }
```

### Rate limit response headers

When you reject or allow a request, include these headers so the client knows
what's happening:

```
HTTP/1.1 200 OK
X-RateLimit-Limit: 100         → total requests allowed in this window
X-RateLimit-Remaining: 47      → requests left in this window
X-RateLimit-Reset: 1709900060  → Unix timestamp when window resets

---

HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1709900060
Retry-After: 42                → seconds until they can try again
Content-Type: application/json

{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Try again in 42 seconds.",
  "retry_after": 42
}
```

A good client will read `Retry-After` and back off automatically. A bad client
will just retry immediately — which is why your rate limiter needs to handle this
gracefully.

Rate limit by what makes sense for your API:
- Per API key (for server-to-server)
- Per user ID (for authenticated endpoints)
- Per IP address (for public/unauthenticated endpoints)
- Per endpoint (expensive endpoints get tighter limits)

---

## CORS — Why Can JavaScript on evil.com Call Your API?

You've seen this error in the browser console:

```
Access to fetch at 'https://api.myapp.com/data' from origin
'https://evil.com' has been blocked by CORS policy: No
'Access-Control-Allow-Origin' header is present on the requested resource.
```

That's CORS doing its job. Let's understand why it exists and how to configure it
correctly.

### The Same-Origin Policy

Browsers enforce the same-origin policy: JavaScript can only make requests to the
same origin it was served from.

```
Origin = protocol + domain + port

https://myapp.com:443       ← one origin
https://api.myapp.com:443   ← DIFFERENT origin (different subdomain)
http://myapp.com:80         ← DIFFERENT origin (different protocol + port)
https://myapp.com:8080      ← DIFFERENT origin (different port)
https://evil.com:443        ← DIFFERENT origin (different domain)
```

Why does this policy exist? Without it, if you visit `evil.com`, the malicious
JavaScript there could silently call `https://your-bank.com/transfer` using your
browser's session cookies. That would be very bad.

### CORS: Relaxing the Same-Origin Policy

CORS (Cross-Origin Resource Sharing) is the mechanism that lets a server say:
"I trust requests from these other origins."

When a browser makes a cross-origin request, it adds an `Origin` header:

```
GET /api/data HTTP/1.1
Host: api.myapp.com
Origin: https://frontend.myapp.com
```

The server responds with headers that say whether the request is allowed:

```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://frontend.myapp.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Authorization, Content-Type
```

The browser sees `Access-Control-Allow-Origin` matches the origin of the page,
so it lets the JavaScript code access the response. If the header is missing or
doesn't match, the browser blocks the response (the request still reaches the
server — CORS is a browser enforcement mechanism, not a server-level block).

### The Preflight Request

For "non-simple" requests (anything with a custom header like `Authorization`,
or methods other than GET/POST), the browser sends a preflight OPTIONS request
before the actual request:

```
OPTIONS /api/data HTTP/1.1
Host: api.myapp.com
Origin: https://frontend.myapp.com
Access-Control-Request-Method: DELETE
Access-Control-Request-Headers: Authorization, Content-Type

      ↓ Server responds:

HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://frontend.myapp.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 86400    ← browser can cache this for 24 hours

      ↓ Browser then sends the actual request:

DELETE /api/data/42 HTTP/1.1
Authorization: Bearer eyJ...
```

If your API responds to the OPTIONS preflight correctly, the actual request
proceeds. If not, the browser blocks it.

Your framework probably handles this. In FastAPI:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://myapp.com",
        "https://www.myapp.com",
        # "http://localhost:3000",  # add for local dev
    ],
    allow_credentials=True,   # allows cookies/auth headers
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### Wildcard vs specific origins

```
Access-Control-Allow-Origin: *       ← allows any origin

  Use for: public read-only APIs (docs, public data APIs)
  Never use with: allow_credentials=True (browsers reject this combination)

Access-Control-Allow-Origin: https://myapp.com   ← specific origin

  Use for: any API that has authentication
           anything where you care who's calling
```

The wildcard `*` is fine for a truly public API with no user auth. The moment
you're dealing with cookies, sessions, or `Authorization` headers, use specific
origins. You can dynamically validate the incoming `Origin` header against an
allowlist and echo it back if it matches.

---

## Input Validation — Trust Nothing From the Client

Here's the mindset: every byte that comes from a client is potentially hostile.
Not because your users are evil, but because:
1. You don't know who's actually sending the request
2. Bugs in client apps can send malformed data
3. Someone might be probing your API on purpose

### SQL Injection — The Classic

You have a search endpoint:

```python
# DO NOT DO THIS
username = request.args.get("username")
query = f"SELECT * FROM users WHERE username = '{username}'"
db.execute(query)
```

A normal user sends: `username=alice` → works fine.

An attacker sends: `username='; DROP TABLE users; --`

Your query becomes:
```sql
SELECT * FROM users WHERE username = ''; DROP TABLE users; --'
```

Two statements. The first returns nothing. The second drops your users table.
This is SQL injection, and it's been the number one web vulnerability for decades.

The fix is parameterized queries — never concatenate user input into SQL:

```python
# CORRECT: parameterized query
username = request.args.get("username")
query = "SELECT * FROM users WHERE username = %s"
db.execute(query, (username,))

# Or with SQLAlchemy ORM (which handles this for you):
user = db.query(User).filter(User.username == username).first()
```

With parameterized queries, the database treats the user input as data, not as
SQL code. The injection attempt becomes a literal string search.

### Schema Validation with Pydantic

The best defense against malformed input is declaring exactly what you expect
and letting a schema validator enforce it:

```python
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re

class CreateUserRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r'^[a-zA-Z0-9_-]+$'  # only alphanumeric, underscore, dash
    )
    email: EmailStr  # validates email format
    age: int = Field(ge=13, le=120)  # must be 13-120
    bio: Optional[str] = Field(default=None, max_length=500)

    @validator('username')
    def username_not_reserved(cls, v):
        reserved = ['admin', 'root', 'system', 'api']
        if v.lower() in reserved:
            raise ValueError('Username is reserved')
        return v

# FastAPI automatically validates incoming requests against this model
@app.post("/users")
async def create_user(body: CreateUserRequest):
    # If we get here, all validation has passed
    # body.username is safe, body.email is a valid email, etc.
    pass
```

Pydantic validates the type, the shape, and the constraints all at once. If
anything fails, FastAPI returns a `422 Unprocessable Entity` with a detailed
error message before your code even runs.

### Other injection vectors to know about

```
SQL injection:        ''; DROP TABLE users; --
NoSQL injection:      {"$gt": ""}  (MongoDB operators in JSON)
Command injection:    ; rm -rf /   (user input passed to shell commands)
Path traversal:       ../../etc/passwd  (user input used in file paths)
XSS:                  <script>alert('xss')</script>  (user input echoed in HTML)
```

The pattern to prevent all of them is the same: validate and sanitize all input,
use parameterized queries or ORMs, never construct commands/queries by concatenating
user input.

---

## Common API Security Checklist

A quick reference for every API you ship:

```
AUTHENTICATION
  [ ] Every non-public endpoint requires authentication
  [ ] API keys are hashed (SHA-256) before storing
  [ ] API keys are never logged
  [ ] JWTs are validated: signature + expiration + issuer
  [ ] JWT algorithm explicitly specified (no alg:none)
  [ ] Access tokens are short-lived (15 min to 1 hour)
  [ ] Refresh tokens are stored securely, can be revoked

AUTHORIZATION
  [ ] Every endpoint checks what the caller is allowed to do
  [ ] Resource ownership verified (user can only access their own data)
  [ ] Admin endpoints require elevated roles
  [ ] IDOR protected: can user 42 access /users/43/data? Should be 403.

TRANSPORT
  [ ] HTTPS everywhere, HTTP redirects to HTTPS
  [ ] HSTS header set (Strict-Transport-Security)
  [ ] TLS 1.2 minimum, prefer TLS 1.3

RATE LIMITING
  [ ] Rate limiting on all public endpoints
  [ ] Rate limiting on auth endpoints (prevent brute force)
  [ ] Rate limit headers returned (X-RateLimit-*)
  [ ] 429 returned with Retry-After header

CORS
  [ ] CORS origin allowlist configured (not wildcard for auth'd APIs)
  [ ] Preflight OPTIONS handled correctly
  [ ] Credentials flag only set when needed

INPUT VALIDATION
  [ ] All input validated against schema (Pydantic, JSON Schema)
  [ ] Parameterized queries used everywhere
  [ ] File upload types validated
  [ ] Request size limits set (prevent huge payload attacks)

SECRETS
  [ ] No secrets in code or git
  [ ] Secrets loaded from environment variables or secret manager
  [ ] Secrets never in API responses or logs
  [ ] Rotate keys/secrets on suspected compromise

HEADERS
  [ ] X-Content-Type-Options: nosniff
  [ ] X-Frame-Options: DENY (prevents clickjacking)
  [ ] Content-Security-Policy set
  [ ] Server header not leaking version info
```

Security is not a feature you add at the end. It's a set of decisions you make
at every layer, from the first line of code.

---

## Summary

```
Authentication  — who are you?  (API keys, OAuth2, JWT)
Authorization   — what can you do?  (roles, resource ownership checks)
Input validation — is your data safe?  (Pydantic, parameterized queries)

API Keys:
  - Hash with SHA-256 before storing
  - Pass in Authorization header, never in URL
  - Best for server-to-server auth

OAuth 2.0:
  - Authorization Code Flow: user delegates permissions to an app
  - Client Credentials: service-to-service, no user involved
  - Short-lived access tokens + long-lived refresh tokens

JWT:
  - header.payload.signature (base64 encoded, not encrypted)
  - Validate: signature + exp + iss
  - Never store secrets in payload
  - Use RS256 in microservices (asymmetric)
  - Use short expiry on access tokens

Rate Limiting:
  - Token bucket: allows bursts, sustainable rate
  - Leaky bucket: smooths bursts, fixed output rate
  - Fixed window: simple but has edge case at window boundary
  - Sliding window: accurate, no edge case
  - Return X-RateLimit-* headers and Retry-After on 429

CORS:
  - Same-origin policy prevents cross-origin JS requests
  - CORS lets you whitelist trusted origins
  - Never use wildcard with authenticated APIs
```

---

| Previous | [06 — WebSockets](../06_websockets/realtime_apis.md) |
|----------|------------------------------------------------------|
| Next     | [08 — API Gateway](../08_api_gateway/gateway_patterns.md) |
| Home     | [README.md](../README.md) |
