# 13 — API Security in Production

> Stage 5 covered the fundamentals: JWT, OAuth2, API keys, rate limiting basics. This chapter goes deeper. These are the things that separate an API that's "pretty secure" from one that can stand up to real-world attackers, regulatory audits, and the slow entropy of a production system.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
HTTPS/TLS enforcement · token security (short-lived/rotation/revocation) · input validation · security headers (HSTS/CSP/X-Frame-Options)

**Should Learn** — Important for real projects, comes up regularly:
CORS origin validation · advanced rate limiting (per-user/per-endpoint) · audit logging · file upload validation

**Good to Know** — Useful in specific situations, not always tested:
bot detection · httpOnly cookies · CSRF protection

**Reference** — Know it exists, look up syntax when needed:
WAF configuration · secrets rotation · DDoS patterns vs business logic rate limits

---

## The Threat Model Has Changed

In staging, the only people calling your API are you and your teammates. In production, the audience is everyone on the internet.

Some of them are legitimate users. Some are bots running credential stuffing attacks. Some are researchers poking at your headers. Some are scrapers. A small number are actively trying to find a way in.

This chapter is not about paranoia. It is about understanding exactly which controls exist at which layer, and making deliberate choices at each one.

```
Internet traffic arriving at your API:

┌─────────────────────────────────────────────────────────────┐
│  CDN / Edge (Cloudflare, CloudFront)                         │
│  → DDoS mitigation, bot detection, TLS termination          │
├─────────────────────────────────────────────────────────────┤
│  Load Balancer (NGINX, ALB)                                  │
│  → TLS termination (if not at CDN), HTTPS enforcement        │
├─────────────────────────────────────────────────────────────┤
│  API Gateway / Reverse Proxy                                 │
│  → Rate limiting, auth pre-checks, routing                   │
├─────────────────────────────────────────────────────────────┤
│  Your Application (FastAPI)                                  │
│  → Business logic auth, input validation, security headers   │
├─────────────────────────────────────────────────────────────┤
│  Database                                                    │
│  → Parameterized queries, least-privilege accounts           │
└─────────────────────────────────────────────────────────────┘
```

Every layer has a job. The mistake most teams make is expecting one layer to do all the work.

---

## 1. HTTPS — Non-Negotiable

You already know HTTPS matters. What is less obvious in production: exactly where TLS is terminated, and what happens to traffic after that point.

### TLS Termination at the Load Balancer

In most production deployments, your application servers never see raw TLS. The load balancer (NGINX, AWS ALB, GCP Load Balancer) terminates the TLS connection, decrypts the traffic, and forwards it to your app over plain HTTP on an internal private network.

```
Internet ──HTTPS──> Load Balancer ──HTTP──> App Servers
         (encrypted)              (plaintext, but private network)
```

This is the standard architecture. Your FastAPI app only needs to handle HTTP internally. The load balancer handles certificate management and TLS configuration.

The NGINX configuration looks like this:

```nginx
server {
    listen 443 ssl;
    server_name api.myapp.com;

    ssl_certificate     /etc/letsencrypt/live/api.myapp.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.myapp.com/privkey.pem;

    # Enforce TLS 1.2 minimum; prefer 1.3
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Forward to your app
    location / {
        proxy_pass http://app_servers;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect all HTTP to HTTPS — no exceptions
server {
    listen 80;
    server_name api.myapp.com;
    return 301 https://$host$request_uri;
}
```

### HSTS — Tell Browsers to Never Downgrade

HTTPS enforcement at the redirect level stops most accidental HTTP requests. HSTS (HTTP Strict Transport Security) tells browsers to never attempt HTTP to your domain, even if a link or redirect points there.

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

- `max-age=31536000` — remember this for one year
- `includeSubDomains` — apply to all subdomains too
- `preload` — browsers ship with your domain hardcoded in their HTTPS-only list

Set this header in your load balancer or in your application middleware. Once sent, the browser will refuse plain HTTP to your domain for the duration of `max-age`.

In FastAPI:

```python
@app.middleware("http")
async def enforce_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains; preload"
    )
    return response
```

### Certificate Management with Let's Encrypt

Let's Encrypt provides free TLS certificates with 90-day validity. The tooling (Certbot) automates renewal.

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Issue certificate (with NGINX plugin — handles config automatically)
sudo certbot --nginx -d api.myapp.com

# Test auto-renewal
sudo certbot renew --dry-run

# Certbot adds a cron job or systemd timer that runs twice daily
# and renews certificates when they have fewer than 30 days remaining
```

In AWS, ACM (AWS Certificate Manager) handles this automatically for ALB-terminted traffic — certificates are issued and renewed without any manual steps.

The critical point: never let a certificate expire in production. Configure monitoring alerts at 30 days and 14 days before expiry.

---

## 2. Input Validation and Sanitization

Every byte arriving from a client should be treated as potentially hostile. Not because users are attackers, but because:
- You don't know who is actually at the keyboard
- Client-side validation is trivially bypassed
- Bugs in client apps can produce unexpected payloads

### FastAPI + Pydantic: Your First Line of Defense

Pydantic handles most input validation automatically when you declare your request schemas. Type mismatches, missing required fields, and constraint violations all return `422 Unprocessable Entity` before your handler code runs.

```python
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

app = FastAPI()

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    age: int = Field(ge=13, le=120)
    bio: Optional[str] = Field(default=None, max_length=500)

@app.post("/users", status_code=201)
def create_user(body: CreateUserRequest):
    # If we reach here, all constraints have passed
    # body.username is alphanumeric only, 3–50 chars
    # body.email is a valid email address format
    # body.age is between 13 and 120
    return {"id": 1, **body.model_dump()}
```

For query parameters:

```python
@app.get("/search")
def search(q: str = Query(..., min_length=1, max_length=100)):
    # Pydantic validates the length constraint
    # SQLAlchemy parameterizes the query — SQL injection is prevented at the ORM level
    results = db.query(Product).filter(Product.name.ilike(f"%{q}%")).all()
    return results
```

### SQL Injection: ORM as Defense

String-concatenating user input into SQL is the classic path to injection attacks. SQLAlchemy's ORM prevents this automatically — query parameters are always passed as bind parameters, never interpolated into the query string.

```python
# UNSAFE — never do this, even inside a "secured" app
username = request.query_params.get("username")
db.execute(f"SELECT * FROM users WHERE username = '{username}'")
# Attacker sends: username='; DROP TABLE users; --

# SAFE — SQLAlchemy ORM parameterizes automatically
user = db.query(User).filter(User.username == username).first()
# Generates: SELECT * FROM users WHERE username = $1
# The username value is bound as a parameter, never interpreted as SQL
```

If you write raw SQL (for complex queries), use bound parameters explicitly:

```python
from sqlalchemy import text

# SAFE: explicit bind parameters
result = db.execute(
    text("SELECT * FROM users WHERE username = :username AND active = :active"),
    {"username": username, "active": True}
)
```

### File Upload Validation

File uploads are a particularly dangerous input vector. Always validate:

```python
from fastapi import UploadFile, File, HTTPException
import magic  # python-magic: pip install python-magic

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

@app.post("/profile/avatar")
async def upload_avatar(file: UploadFile = File(...)):
    # 1. Check declared content type (can be spoofed, so verify below too)
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported file type")

    # 2. Read the file and check actual size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 5 MB)")

    # 3. Verify the actual file magic bytes — never trust the declared type
    detected_type = magic.from_buffer(contents, mime=True)
    if detected_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"File content does not match declared type"
        )

    # 4. In production: send file to a virus scanner (ClamAV or cloud-based)
    # scan_result = virus_scanner.scan(contents)
    # if scan_result.infected:
    #     raise HTTPException(status_code=422, detail="File failed security scan")

    # 5. Store in object storage (S3, GCS), never on the app server's filesystem
    object_key = f"avatars/{current_user.id}/{uuid.uuid4()}.jpg"
    s3_client.put_object(Bucket="my-uploads", Key=object_key, Body=contents)

    return {"avatar_url": f"https://cdn.myapp.com/{object_key}"}
```

Never store uploaded files in your app server's local filesystem. Use object storage (S3, GCS, Azure Blob). Never execute uploaded files. Rename files on the server side — never trust the original filename.

---

## 3. Token Security

Stage 5 introduced JWTs and refresh tokens. Production systems need to harden the full token lifecycle.

### Short-Lived Access Tokens

Access tokens should expire in 15 minutes. This sounds inconvenient, but it is the right trade-off: a stolen access token is usable for at most 15 minutes before it expires.

```python
from datetime import datetime, timedelta, timezone
import jwt

def create_access_token(user_id: int, roles: list[str]) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "roles": roles,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=15),   # 15 minutes, not hours
        "jti": str(uuid.uuid4()),             # unique token ID, used for revocation
        "iss": "api.myapp.com",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="RS256")
```

### Refresh Token Rotation

Every time a refresh token is used to obtain a new access token, issue a new refresh token and invalidate the old one. This is called refresh token rotation.

Why it matters: if a refresh token is stolen, the attacker can use it to get an access token. But when the legitimate user next calls `/auth/refresh`, their old refresh token is already gone — they get a new one. The attacker's stolen refresh token is now dead. This gives you a detection signal (two refresh attempts with the same token indicates theft) and limits the damage window.

```python
import redis
from fastapi import HTTPException

r = redis.Redis(host="localhost", port=6379)

@app.post("/auth/refresh")
def refresh_token(body: RefreshTokenRequest):
    # Decode and validate the refresh token
    try:
        payload = jwt.decode(
            body.refresh_token,
            settings.SECRET_KEY,
            algorithms=["RS256"],
            options={"require": ["sub", "jti", "exp"]}
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    token_id = payload["jti"]
    user_id = int(payload["sub"])

    # Check the token is still valid (not rotated away or revoked)
    stored = r.get(f"refresh_token:{token_id}")
    if not stored:
        # Token not found — either already used (rotation) or revoked
        # This is a security signal: log it and investigate
        logger.warning(f"Refresh token reuse detected for user {user_id}")
        # Invalidate ALL refresh tokens for this user (assume compromise)
        revoke_all_user_tokens(user_id)
        raise HTTPException(status_code=401, detail="Refresh token already used")

    # Invalidate the old refresh token immediately
    r.delete(f"refresh_token:{token_id}")

    # Issue a new access token and a new refresh token
    new_access_token = create_access_token(user_id, payload.get("roles", []))
    new_refresh_token, new_token_id = create_refresh_token(user_id)

    # Store the new refresh token in Redis (30-day TTL)
    r.setex(
        f"refresh_token:{new_token_id}",
        int(timedelta(days=30).total_seconds()),
        user_id
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
```

### Token Revocation List in Redis

Access tokens are stateless: once issued, they are valid until expiry. But you need to be able to invalidate them immediately (user logs out, account compromised, admin revocation).

The standard approach: maintain a revocation list in Redis. On every request, check if the token's `jti` (JWT ID) is in the revocation list. Redis lookups are O(1) and add microseconds of overhead.

```python
REVOCATION_PREFIX = "revoked_token:"

def revoke_token(jti: str, expires_at: datetime):
    """Add a token to the revocation list until its natural expiry."""
    ttl = int((expires_at - datetime.now(timezone.utc)).total_seconds())
    if ttl > 0:
        r.setex(f"{REVOCATION_PREFIX}{jti}", ttl, "1")

def is_token_revoked(jti: str) -> bool:
    return r.exists(f"{REVOCATION_PREFIX}{jti}") > 0

# In your authentication dependency
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_and_validate_token(token)  # raises on invalid/expired

    # Check revocation list
    if is_token_revoked(payload["jti"]):
        raise HTTPException(status_code=401, detail="Token has been revoked")

    return payload
```

### Store Tokens in httpOnly Cookies for Browser Apps

If your API is consumed by a browser-based frontend, store tokens in `httpOnly` cookies rather than `localStorage`.

`localStorage` is accessible to any JavaScript on the page — an XSS vulnerability in your frontend exposes every token stored there. `httpOnly` cookies are not accessible to JavaScript at all. The browser sends them automatically with every request to your domain, and they cannot be read or stolen via XSS.

```python
@app.post("/auth/login")
def login(response: Response, body: LoginRequest):
    # Authenticate the user, create tokens...
    access_token = create_access_token(user.id, user.roles)
    refresh_token, token_id = create_refresh_token(user.id)

    # Store access token in httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,       # JavaScript cannot read this
        secure=True,         # Only sent over HTTPS
        samesite="strict",   # Only sent on same-site requests (CSRF protection)
        max_age=900,         # 15 minutes, matching token expiry
        path="/",
    )

    # Store refresh token in a separate httpOnly cookie, scoped to /auth
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=60 * 60 * 24 * 30,   # 30 days
        path="/auth/refresh",         # Only sent to the refresh endpoint
    )

    return {"message": "Login successful"}
```

The trade-off: `httpOnly` cookies require CSRF protection (handled automatically by `samesite="strict"`). For APIs consumed by mobile apps or non-browser clients, `Authorization: Bearer` headers remain appropriate.

---

## 4. Advanced Rate Limiting

Stage 5 introduced rate limiting with a fixed-window Redis counter. Production systems need more nuance.

### Per-User, Per-IP, Per-Endpoint

Different limits for different scenarios:

```python
from enum import Enum

class RateLimitTier(Enum):
    GLOBAL_IP = ("ip", 200, 60)         # 200 req/min by IP for anonymous traffic
    AUTH_ENDPOINT = ("ip", 10, 60)      # 10 login attempts/min (brute force defense)
    USER_STANDARD = ("user", 1000, 60)  # 1000 req/min for authenticated users
    USER_EXPENSIVE = ("user", 10, 60)   # 10/min for expensive endpoints (export, report)

def rate_limit_key(request: Request, tier: RateLimitTier) -> str:
    dimension, _, _ = tier.value
    window = int(time.time() // 60)

    if dimension == "ip":
        identifier = request.client.host
    elif dimension == "user":
        identifier = getattr(request.state, "user_id", request.client.host)

    endpoint = request.url.path.replace("/", "_")
    return f"rl:{tier.name}:{identifier}:{endpoint}:{window}"
```

Apply tighter limits to authentication endpoints specifically. Brute-force attacks against `/auth/login` are extremely common. Ten attempts per minute per IP is generous for real users and completely defeats automated credential stuffing.

### Sliding Window Rate Limiting

Fixed window has an edge case: a client can make 100 requests at 00:59 and 100 more at 01:00, effectively getting 200 requests in 2 seconds. Sliding window eliminates this.

```python
def sliding_window_rate_limit(
    key: str,
    limit: int,
    window_seconds: int
) -> tuple[bool, int]:
    """
    Sliding window using Redis sorted set.
    Returns (is_limited, requests_remaining).
    """
    now = time.time()
    window_start = now - window_seconds

    pipe = r.pipeline()
    # Remove entries outside the current window
    pipe.zremrangebyscore(key, 0, window_start)
    # Count requests in the window
    pipe.zcard(key)
    # Add current request with timestamp as score
    pipe.zadd(key, {str(uuid.uuid4()): now})
    # Set expiry to clean up keys automatically
    pipe.expire(key, window_seconds * 2)
    results = pipe.execute()

    request_count = results[1]
    is_limited = request_count >= limit
    remaining = max(0, limit - request_count - 1)

    return is_limited, remaining
```

The memory cost is O(requests_in_window) rather than O(1) for fixed window. For most APIs this is acceptable. At very high scale, use a probabilistic approach or a counter-based approximation.

### DDoS Mitigation at the Edge

Your application should not be the thing that absorbs a volumetric DDoS attack. By the time 50,000 requests per second reach your FastAPI application, your infrastructure is already struggling.

Layer the defense:

```
CloudFlare / AWS Shield
  → Absorbs volumetric DDoS at the network layer (Gbps-scale)
  → Bot scoring: identifies automated traffic patterns
  → Challenge pages: CAPTCHAs for suspicious clients
  → Rate limiting rules: IP-level blocks at CDN before traffic reaches your origin

Load Balancer
  → Connection rate limiting
  → HTTP/S-level inspection

Your Application
  → Per-user, per-endpoint rate limiting
  → Business logic enforcement
```

Configure Cloudflare (or equivalent) to rate limit by IP before requests reach your origin servers. A rule like "block IPs making more than 500 requests per minute" costs Cloudflare nothing and saves your servers from the majority of volumetric attacks.

### Bot Detection Signals

Legitimate humans have recognizable behavioral patterns that bots typically do not:

```python
def bot_detection_score(request: Request) -> int:
    """
    Return a score 0–100 indicating bot likelihood.
    Higher scores mean more likely to be a bot.
    This is a simple heuristic — production systems use ML models.
    """
    score = 0

    # No User-Agent or obviously fake one
    ua = request.headers.get("User-Agent", "")
    if not ua or ua in ("curl/7.x", "python-requests"):
        score += 30

    # No Accept-Language header (browsers always send this)
    if not request.headers.get("Accept-Language"):
        score += 20

    # Requests arriving at perfectly regular intervals
    # (check from Redis — look at timestamp distribution for this IP)
    if is_metronomic_pattern(request.client.host):
        score += 40

    # IP is in a known data center range (AWS, GCP, Azure) — unlikely to be a human
    if is_datacenter_ip(request.client.host):
        score += 10

    return score
```

This is heuristic. Production-grade bot detection (Cloudflare Bot Management, Akamai Bot Manager, DataDome) uses many more signals — TLS fingerprinting, mouse movement patterns, JavaScript execution analysis — and machine learning models trained on billions of requests.

---

## 5. CORS Configuration in Production

Wildcard CORS (`Access-Control-Allow-Origin: *`) is fine for public read-only APIs. It is wrong for any API that handles authentication or user data.

```python
from fastapi.middleware.cors import CORSMiddleware
import os

# Load allowed origins from environment — different per environment
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")
# Production .env: CORS_ORIGINS=https://myapp.com,https://www.myapp.com
# Development .env: CORS_ORIGINS=http://localhost:3000,http://localhost:5173

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,          # explicit list, never wildcard for auth'd APIs
    allow_credentials=True,                 # required for cookies and Authorization headers
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-RateLimit-Remaining", "X-RateLimit-Reset"],
    max_age=86400,                          # browser caches preflight for 24 hours
)
```

If you need to dynamically validate origins against a database allowlist (e.g., for a multi-tenant SaaS where each tenant has their own frontend domain):

```python
@app.middleware("http")
async def dynamic_cors(request: Request, call_next):
    origin = request.headers.get("origin")

    # Check the origin against a database or cached allowlist
    allowed = origin and is_allowed_origin(origin)

    if request.method == "OPTIONS" and "access-control-request-method" in request.headers:
        # Preflight request
        if allowed:
            return Response(
                status_code=204,
                headers={
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH",
                    "Access-Control-Allow-Headers": "Authorization, Content-Type",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Max-Age": "86400",
                }
            )
        return Response(status_code=403)

    response = await call_next(request)
    if allowed:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"

    return response
```

---

## 6. Security Headers

Every response from a production API should include a standard set of security headers. These cost nothing and defend against an entire class of browser-based attacks.

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    # Prevent MIME type sniffing
    # Without this, browsers might interpret a JSON response as HTML and execute scripts
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Prevent your API responses from being embedded in iframes (clickjacking)
    response.headers["X-Frame-Options"] = "DENY"

    # Content Security Policy — for an API that returns JSON, this is correct:
    # "I don't serve any content that should be executed"
    response.headers["Content-Security-Policy"] = "default-src 'none'"

    # Control what URL information is sent in the Referer header
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Prevent browsers from caching sensitive API responses
    # (Applied selectively — not all endpoints need this)
    if request.url.path.startswith("/auth") or request.url.path.startswith("/users/me"):
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"

    # HSTS — tell browsers to always use HTTPS for this domain
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )

    # Remove server version information
    # Don't tell attackers you're running uvicorn/0.24.0 or Python/3.11
    response.headers.pop("Server", None)
    response.headers.pop("X-Powered-By", None)

    return response
```

What each header does and why it matters:

```
X-Content-Type-Options: nosniff
  → Stops browsers from guessing content types
  → Without it: an attacker uploads a JSON file named "evil.html"
    and tricks the browser into rendering it as HTML

X-Frame-Options: DENY
  → Prevents your responses from being loaded in an iframe
  → Without it: clickjacking attacks (invisible frame over a button)
  → Less relevant for pure APIs but necessary for any hybrid page

Content-Security-Policy: default-src 'none'
  → For a JSON API, this says "there is nothing here that should execute"
  → Browsers will refuse to execute any scripts from your API's domain

Referrer-Policy: strict-origin-when-cross-origin
  → Controls what URL info is leaked in the Referer header
  → Prevents internal URLs and user data from leaking to third parties

Strict-Transport-Security: max-age=31536000
  → Browser never attempts HTTP to your domain again
  → Even if a user types "http://", the browser upgrades automatically
```

Validate your headers with securityheaders.com (a free tool that scores your headers and explains what is missing).

---

## 7. Audit Logging

Every significant action in a production system should be logged with enough context to reconstruct what happened, who did it, and when. This is not optional in regulated industries — PCI-DSS, HIPAA, SOC 2, and GDPR all require audit trails.

### The Audit Log Middleware

```python
import logging
import time
import json

audit_logger = logging.getLogger("audit")

@app.middleware("http")
async def audit_log(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)

    # Log all state-changing operations
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        audit_logger.info(json.dumps({
            "event": "api_call",
            "method": request.method,
            "path": request.url.path,
            "user_id": getattr(request.state, "user_id", None),
            "ip": request.client.host,
            "status": response.status_code,
            "duration_ms": duration_ms,
            "request_id": request.headers.get("X-Request-ID"),
            "user_agent": request.headers.get("User-Agent"),
        }))

    return response
```

### Structured Logging for Query-ability

Audit logs are only useful if you can query them. Use structured logging (JSON lines) so your log aggregator (Datadog, Elasticsearch, Splunk, CloudWatch Logs Insights) can parse and query them.

```python
import structlog

log = structlog.get_logger()

# When a sensitive action occurs (password change, payment, permission change):
log.info(
    "sensitive_action",
    action="password_changed",
    user_id=current_user.id,
    ip=request.client.host,
    request_id=request.headers.get("X-Request-ID"),
    timestamp=datetime.now(timezone.utc).isoformat(),
)

# Failed authentication — critical for detecting brute force attacks
log.warning(
    "auth_failure",
    reason="invalid_password",
    email_attempted=body.email,
    ip=request.client.host,
    attempt_count=get_failed_attempt_count(body.email),
)
```

### What to Log vs. What Never to Log

```
ALWAYS LOG:
  ✓ Authentication events (login, logout, failed login)
  ✓ Authorization failures (forbidden resource access attempts)
  ✓ All write operations (POST, PUT, DELETE, PATCH) + who did them
  ✓ Admin actions (permission changes, user role assignments)
  ✓ Data export / bulk operations
  ✓ Payment and billing events
  ✓ Account changes (email, password, 2FA)

NEVER LOG:
  ✗ Passwords (raw or hashed)
  ✗ Full credit card numbers, CVVs
  ✗ Access tokens or API keys (even partial can be dangerous)
  ✗ Session tokens or cookies
  ✗ Social security numbers, passport numbers
  ✗ Full PII in request bodies (log user_id, not the full address)
```

A useful mental test: if this log file were to leak, what would an attacker learn from it? If the answer is "they could impersonate users" or "they could commit fraud," you are logging too much.

### Log Retention and Alerting

Configure retention policies that match your compliance requirements:
- PCI-DSS: 12 months with 3 months immediately available
- HIPAA: 6 years
- GDPR: no maximum, but also right-to-erasure requirements

Set up real-time alerts for security-relevant patterns:
- More than 5 failed login attempts from the same IP in 5 minutes
- Admin actions outside business hours
- A single user making DELETE requests at a rate that looks like a script
- Any request that returns a 403 on an admin endpoint

---

## 8. The Production Security Checklist

Every API that reaches production should pass this checklist:

```
TRANSPORT
  [ ] HTTPS enforced everywhere, HTTP redirects to HTTPS
  [ ] HSTS header set (max-age ≥ 1 year)
  [ ] TLS 1.2 minimum, TLS 1.3 preferred
  [ ] Certificate auto-renewal configured and monitored

INPUT
  [ ] All inputs validated through Pydantic schemas
  [ ] Parameterized queries used everywhere (ORM or explicit bind params)
  [ ] File uploads: content type verified by magic bytes, not filename
  [ ] Request body size limits configured at load balancer level

TOKENS
  [ ] Access tokens expire in ≤ 15 minutes
  [ ] Refresh token rotation implemented
  [ ] Token revocation via Redis jti blocklist
  [ ] Tokens in httpOnly cookies for browser clients (not localStorage)
  [ ] RS256 used in multi-service environments (asymmetric signing)

RATE LIMITING
  [ ] Per-IP limits on public endpoints
  [ ] Per-user limits on authenticated endpoints
  [ ] Tight limits (≤ 10/min) on auth endpoints (login, password reset)
  [ ] DDoS mitigation at CDN/edge layer, not just application layer
  [ ] 429 responses include Retry-After header

CORS
  [ ] Explicit origin allowlist, not wildcard, for authenticated APIs
  [ ] allow_credentials=True only where cookies are actually used
  [ ] Preflight caching configured (max_age)

SECURITY HEADERS
  [ ] X-Content-Type-Options: nosniff
  [ ] X-Frame-Options: DENY
  [ ] Content-Security-Policy set
  [ ] Strict-Transport-Security set
  [ ] Server version header removed

AUDIT LOGGING
  [ ] All write operations logged with user_id, IP, timestamp
  [ ] Authentication events logged
  [ ] Authorization failures logged
  [ ] No secrets, tokens, or full PII in logs
  [ ] Log retention policy matches compliance requirements
  [ ] Alerts configured for anomalous patterns

SECRETS
  [ ] No secrets in git history or code
  [ ] Secrets loaded from environment variables or secrets manager (AWS SSM, Vault)
  [ ] Secrets rotated on any suspected exposure
  [ ] Database uses least-privilege accounts per service
```

Security is a continuous process, not a deployment step. Run this checklist on every significant release. Add it to your CI pipeline where you can automate the checks.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← API Documentation](../10_testing_documentation/docs_that_work.md) &nbsp;|&nbsp; **Next:** [Production Deployment →](../12_production_deployment/deployment_guide.md)

**Related Topics:** [Authentication & Authorization](../05_authentication/securing_apis.md) · [Error Handling Standards](../06_error_handling_standards/error_guide.md) · [Production Deployment](../12_production_deployment/deployment_guide.md) · [API Gateway Patterns](../15_api_gateway/gateway_patterns.md)
