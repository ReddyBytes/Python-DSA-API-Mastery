# ⚡ Cheatsheet: API Security & Production Hardening

---

## Learning Priority

**Must Learn** — core security, daily practice, appears in every production codebase:
OWASP API Top 10 · HTTPS enforcement · JWT validation · input sanitization · rate limiting headers

**Should Learn** — important for real services, comes up in security reviews:
CORS configuration · auth flow security · API key rotation patterns

**Good to Know** — useful for hardening, less frequently tested:
Security headers (HSTS, CSP) · certificate pinning · mTLS

**Reference** — look up when needed:
OWASP full checklist · NIST password guidelines

---

## OWASP API Top 10

| # | Name | Quick Description | Common Fix |
|---|------|-------------------|------------|
| API1 | Broken Object Level Authorization | Accessing other users' objects via ID | Check ownership on every request |
| API2 | Broken Authentication | Weak tokens, no expiry, brute force | Short-lived JWTs, rate limit auth endpoints |
| API3 | Broken Object Property Level Auth | Returning/accepting fields you shouldn't | Allowlist fields; never expose internal fields |
| API4 | Unrestricted Resource Consumption | No rate limits; CPU/memory exhaustion | Rate limit + quota per key |
| API5 | Broken Function Level Authorization | Accessing admin endpoints without admin role | Role checks on every endpoint |
| API6 | Unrestricted Access to Sensitive Business Flows | Bulk account creation, scraping, abuse | Behavioral rate limits + CAPTCHA |
| API7 | Server-Side Request Forgery | API fetches URLs from user input — hits internal services | Validate/allowlist URLs |
| API8 | Security Misconfiguration | Debug mode on, default creds, open CORS | Production config checklist |
| API9 | Improper Inventory Management | Old API versions exposed, shadow endpoints | Version audit, retire old endpoints |
| API10 | Unsafe Consumption of APIs | Trusting third-party API responses blindly | Validate + sanitize all external data |

---

## HTTPS Config (FastAPI / Uvicorn)

```python
# Production: run behind Nginx or a load balancer that terminates TLS
# Force HTTPS redirect using middleware

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

app = FastAPI()

@app.middleware("http")
async def force_https(request: Request, call_next):
    if request.headers.get("x-forwarded-proto") == "http":
        url = request.url.replace(scheme="https")
        return RedirectResponse(url=str(url), status_code=301)
    return await call_next(request)
```

```nginx
# Nginx: redirect HTTP → HTTPS
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    ssl_certificate     /etc/ssl/certs/api.crt;
    ssl_certificate_key /etc/ssl/private/api.key;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

---

## Security Headers

```python
from fastapi import FastAPI, Response
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

---

## Input Sanitization Patterns

```python
from pydantic import BaseModel, validator, constr
import re

class UserInput(BaseModel):
    username: constr(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    email: str
    bio: constr(max_length=500) = ""

    @validator('email')
    def validate_email(cls, v):
        # Use email-validator library in production
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError('Invalid email format')
        return v.lower().strip()

    @validator('bio')
    def sanitize_bio(cls, v):
        # Strip HTML tags — use bleach library for full sanitization
        return re.sub(r'<[^>]+>', '', v)
```

```python
# SQL injection — always use parameterized queries
# NEVER: query = f"SELECT * FROM users WHERE id = {user_id}"
# ALWAYS:
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# Path traversal — sanitize file paths
import os
safe_path = os.path.basename(user_provided_filename)  # strips directory components
```

---

## Rate Limiting Headers

```
# Headers to send on every response
X-RateLimit-Limit: 1000          # max requests per window
X-RateLimit-Remaining: 847       # requests left this window
X-RateLimit-Reset: 1706180460    # Unix timestamp when window resets

# Headers to send on 429 Too Many Requests
Retry-After: 37                  # seconds until they can retry
```

```python
# FastAPI rate limiting with slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/data")
@limiter.limit("100/minute")
async def get_data(request: Request):
    return {"data": "..."}
```

---

## Auth Security Checklist

| Check | Pass Condition |
|-------|----------------|
| Passwords hashed with bcrypt/argon2 | Never store plaintext |
| Brute force protection on login | Lock after N failures or exponential backoff |
| JWT expiry set | `exp` claim present, access token ≤ 15 min |
| Refresh token rotation | Issue new refresh token on each use |
| Auth endpoints rate limited | Separate stricter limit (e.g. 5/minute) |
| HTTPS only for auth endpoints | No auth over HTTP |
| Token invalidation on logout | Blocklist or short-lived tokens |
| API keys hashed in DB | Never store raw API key |
| OAuth state parameter used | CSRF protection in OAuth flow |
| PKCE for public clients | Prevent auth code interception |

---

## JWT Security Rules

```python
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "loaded-from-env-never-hardcoded"
ALGORITHM = "HS256"

def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),  # short-lived
        "type": "access"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],          # always specify algorithm explicitly
            options={"verify_exp": True}     # always verify expiry
        )
        if payload.get("type") != "access":  # reject refresh tokens used as access
            raise ValueError("Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**JWT Don'ts:**
- Never set `alg: none` in header
- Never use symmetric secrets shorter than 32 bytes
- Never store sensitive data in JWT payload (it is base64-encoded, not encrypted)
- Never accept `algorithm` from the token header itself

---

## CORS Safe Config

```python
from fastapi.middleware.cors import CORSMiddleware

# PRODUCTION — explicit allowlist
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com", "https://admin.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    max_age=600,  # preflight cache seconds
)

# NEVER in production:
# allow_origins=["*"] with allow_credentials=True  — browser blocks this anyway
# allow_origins=["*"] on an authenticated API — allows any site to call your API
```

| Setting | Safe Value | Avoid |
|---------|-----------|-------|
| `allow_origins` | Explicit list of domains | `["*"]` on auth APIs |
| `allow_credentials` | `True` only with explicit origins | `True` + wildcard origins |
| `allow_methods` | Only methods your API uses | Unrestricted `["*"]` |
| `allow_headers` | Specific headers only | Unrestricted `["*"]` |

---

## When to Use / Avoid

| Pattern | Use When | Avoid When |
|---------|----------|------------|
| JWT (stateless) | Distributed systems, microservices, short sessions | Long-lived sessions needing instant revocation |
| API Keys | Server-to-server, no user context needed | End-user auth (keys get leaked in client code) |
| OAuth2 + OIDC | Third-party access, user delegation | Internal service-to-service calls |
| mTLS | Internal microservice auth, zero-trust networks | Public-facing APIs (client cert management is complex) |
| Session cookies | Traditional web apps with server-side rendering | Stateless microservices |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Testing & Documentation](../10_testing_documentation/) &nbsp;|&nbsp; **Next:** [Production Deployment →](../12_production_deployment/cheatsheet.md)

**Related Topics:** [Authentication](../05_authentication/securing_apis.md) · [Production Deployment](../12_production_deployment/) · [Real-World APIs](../18_real_world_apis/)
