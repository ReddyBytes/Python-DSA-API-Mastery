# ⚡ Authentication & Authorization — Cheatsheet

## Learning Priority

| Priority | Topics |
|---|---|
| Must Learn | API keys · JWT (structure/validation/refresh) · OAuth2 flows · rate limiting |
| Should Learn | CORS (same-origin/preflight) · input validation · RS256 vs HS256 |
| Good to Know | token bucket vs leaky bucket · CSRF protection |
| Reference | mTLS · FIDO2/WebAuthn · OAuth2 device flow |

---

## Auth Method Comparison

| Method | Best for | Token lifetime | Stateless? | Common use |
|---|---|---|---|---|
| API Key | Server-to-server, no user context | Long-lived / permanent | Yes | OpenAI, Stripe, webhooks |
| Basic Auth | Simple internal tools | Per-request | No | Admin APIs, legacy |
| Bearer Token | User-facing APIs | Short (15 min–1 hr) | Yes (JWT) | REST APIs with users |
| OAuth2 Auth Code | User delegates access to your app | Short access + long refresh | Yes (JWT) | "Sign in with Google" |
| OAuth2 Client Credentials | Machine-to-machine | Short (1 hr) | Yes | Service-to-service |

---

## How to Send Credentials

```
CORRECT:
  Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...   (most common)
  Authorization: ApiKey sk-abc123
  Authorization: Basic dXNlcjpwYXNz              (base64 of user:pass)
  X-API-Key: sk-abc123                            (custom header pattern)

WRONG (never do this):
  GET /data?api_key=sk-abc123                     (key in URL = ends up in logs!)
```

---

## JWT Structure — header.payload.signature

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9  . eyJzdWIiOiI0MiIsImV4cCI6MTcwOX0  . SflKxwRJSMe...
└─────────── HEADER ─────────────────┘   └───────── PAYLOAD ──────────────┘   └─ SIGNATURE ─┘
```

```json
// HEADER (decoded)
{
  "alg": "HS256",
  "typ": "JWT"
}

// PAYLOAD (decoded) — NOT encrypted, just base64
{
  "sub": "42",               // subject: user ID
  "email": "alice@example.com",
  "roles": ["admin", "user"],
  "plan": "pro",
  "iat": 1709896400,         // issued at (Unix timestamp)
  "exp": 1709900000,         // expiration (Unix timestamp)
  "iss": "api.myapp.com"     // issuer
}

// SIGNATURE
// HMAC-SHA256(base64(header) + "." + base64(payload), secret_key)
```

**The payload is readable by anyone. Never put passwords, secrets, or sensitive PII in JWT.**

---

## JWT — What Goes In / What Doesn't

| In payload (OK) | NOT in payload |
|---|---|
| User ID (`sub`) | Passwords or password hashes |
| Email (low sensitivity) | Credit card numbers, SSNs |
| Roles / permissions | API keys or other secrets |
| Plan / tier | Anything you don't want users to read |
| Org ID | Data that changes very frequently |

---

## JWT Validation — 3 Checks Required

```python
import jwt   # pip install PyJWT

def validate_token(token: str, secret: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],            # MUST specify — prevents alg:none attack
            options={"require": ["exp", "iss", "sub"]},
            issuer="api.myapp.com",
            audience="myapp.com",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError("Token expired")
    except jwt.InvalidSignatureError:
        raise AuthError("Invalid signature")
    except jwt.DecodeError:
        raise AuthError("Malformed token")
```

**3 required checks:** (1) signature valid · (2) not expired · (3) issuer matches

---

## JWT Generation

```python
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "your-256-bit-secret"   # load from env in production

def create_access_token(user_id: int, email: str, roles: list) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "roles": roles,
        "iat": now,
        "exp": now + timedelta(minutes=15),   # SHORT — 15 minutes
        "iss": "api.myapp.com",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def create_refresh_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=30),      # LONG — 30 days
        "iss": "api.myapp.com",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

---

## Access Token / Refresh Token Lifecycle

```
Login:
  POST /auth/login {email, password}
  → { "access_token": "eyJ...",   ← valid 15 minutes
      "refresh_token": "eyJ..." }  ← valid 30 days

Normal call:
  GET /api/profile
  Authorization: Bearer <access_token>
  → 200 OK

When access_token expires:
  API → 401 Unauthorized
  POST /auth/refresh { "refresh_token": "eyJ..." }
  → { "access_token": "eyJ..." }   ← new token
  Retry original request with new token

Logout:
  POST /auth/logout
  Server adds refresh_token to blocklist
  Access tokens expire naturally after 15 min
```

---

## HS256 vs RS256

| | HS256 (symmetric) | RS256 (asymmetric) |
|---|---|---|
| Key type | Single shared secret | Private key (sign) + Public key (verify) |
| Who can sign | Anyone with secret | Only auth server (holds private key) |
| Who can verify | Anyone with secret | Any service (public key is public) |
| Forgery risk | High if secret leaks | No — verifiers can't sign |
| Use when | Single service | Multiple services / microservices |

---

## OAuth2 Authorization Code Flow (Text Diagram)

```
Browser  ──1. Click "Login with Google"──▶  Your App
Your App ──2. Redirect to Google with──────▶  Google Auth Server
             client_id, redirect_uri, scope
Browser  ──3. User approves permissions──▶  Google Auth Server
Google   ──4. Redirect back with auth_code──▶  Browser
Browser  ──5. auth_code passed to app──────▶  Your App
Your App ──6. Exchange auth_code for tokens─▶  Google Auth Server
             (server-to-server, never in browser)
Google   ──7. Returns access_token + refresh_token──▶  Your App
```

**Key terms:**
- `client_id` — public app identifier
- `client_secret` — app's password (server-side only, never in browser)
- `scope` — permissions being requested (`read:email`, etc.)
- `auth_code` — short-lived one-time code (~10 minutes)
- `access_token` — short-lived (1 hour), sent with every API call
- `refresh_token` — long-lived (days/months), stored securely, used to get new access token

---

## OAuth2 Client Credentials (Machine-to-Machine)

```python
import requests

# Step 1: Get token
r = requests.post(
    "https://auth.example.com/oauth/token",
    data={
        "grant_type": "client_credentials",
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
    }
)
token = r.json()["access_token"]

# Step 2: Use token
r = requests.get(
    "https://api.example.com/resource",
    headers={"Authorization": f"Bearer {token}"}
)
```

---

## Token Storage Rules

| Storage location | Access tokens | Refresh tokens |
|---|---|---|
| Memory (JS variable) | OK for SPAs | Too risky — lost on refresh |
| HttpOnly cookie | Good | Best for refresh tokens |
| localStorage | Risky (XSS exposure) | Never |
| Database (server-side) | N/A | Yes, for revocation |

---

## CORS Headers

```
Server response headers:
  Access-Control-Allow-Origin: https://myapp.com     (specific origin)
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE, PATCH, OPTIONS
  Access-Control-Allow-Headers: Authorization, Content-Type
  Access-Control-Max-Age: 86400                      (cache preflight 24h)

Wildcard (for public read-only APIs only):
  Access-Control-Allow-Origin: *

NEVER combine wildcard + credentials:
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Credentials: true             ← browsers reject this
```

```python
# FastAPI CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## Rate Limiting Algorithms

| Algorithm | Allows bursts | Smooths traffic | Best for |
|---|---|---|---|
| Token bucket | Yes (up to bucket size) | No | Real users with occasional bursts |
| Leaky bucket | No | Yes (fixed rate) | Protecting downstream services |
| Fixed window | Technically yes (at boundary) | No | Simple implementation |
| Sliding window | No | Yes | Accurate enforcement |

---

## API Key Storage (Server Side)

```python
import hashlib, secrets

def generate_api_key():
    raw_key = f"sk-{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    # Store key_hash in DB — NOT raw_key
    # Return raw_key to user ONCE
    return raw_key, key_hash

def verify_api_key(provided_key: str, stored_hash: str) -> bool:
    h = hashlib.sha256(provided_key.encode()).hexdigest()
    return secrets.compare_digest(h, stored_hash)  # timing-safe comparison
```

---

## Navigation

**[Back to README](../README.md)**

**Theory:** [securing_apis.md](./securing_apis.md)

**Prev:** [← Data Formats](../04_data_formats/cheatsheet.md) &nbsp;|&nbsp; **Next:** [Error Handling →](../06_error_handling_standards/cheatsheet.md)

**Related:** [06 Error Handling](../06_error_handling_standards/cheatsheet.md) · [07 FastAPI](../07_fastapi/cheatsheet.md) · [11 API Security Production](../11_api_security_production/)
