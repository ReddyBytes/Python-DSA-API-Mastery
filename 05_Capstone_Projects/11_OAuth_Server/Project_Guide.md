# Project 11 — OAuth Server: Build Your Own Authorization Server

> Analogy: In the previous project you were a citizen showing your government-issued ID at the door. Now you ARE the government — you print the IDs, you track who you issued them to, and you decide when they expire. Every other service trusts you because you're the issuing authority.

**Learning Format:** Partially Guided — Concepts explained fully, code structure shown, you complete the implementation.

**What You Build:** A working OAuth 2.0 Authorization Server with: client registration, authorization endpoint, token endpoint (Authorization Code grant + Client Credentials grant), token introspection, and refresh token rotation.

**Concepts Covered:** OAuth 2.0 flows, client registry, authorization codes (short-lived, one-time-use), access tokens (JWT), refresh tokens, token introspection endpoint (RFC 7662)

---

## Prerequisites

- Completed: Project 11 (OAuth Client) — you have seen the flow from the client side
- Packages: `fastapi`, `uvicorn`, `python-jose[cryptography]`, `bcrypt`, `python-dotenv`
- `sqlite3` is part of the Python standard library — no extra install needed

```bash
pip install fastapi uvicorn "python-jose[cryptography]" bcrypt python-dotenv
```

---

## Architecture Overview

OAuth has three parties. You are building the middle one.

```
┌──────────────┐        GET /authorize?client_id=&redirect_uri=        ┌────────────────────────┐
│              │ ────────────────────────────────────────────────────► │                        │
│  Client App  │                                                        │  Authorization Server  │
│  (browser /  │ ◄─────────────── redirect to redirect_uri?code= ───── │   (this project)       │
│   backend)   │                                                        │                        │
│              │        POST /token  {code, client_secret}             │  - /clients/register   │
│              │ ────────────────────────────────────────────────────► │  - GET  /authorize     │
│              │ ◄─────────── {access_token, refresh_token} ─────────  │  - POST /token         │
└──────────────┘                                                        │  - POST /introspect    │
                                                                        └────────────────────────┘
┌──────────────┐        POST /introspect  {token}
│   Resource   │ ──────────────────────────────────────────────────────────────────────────────►
│   Server     │ ◄─────────────── {active: true, sub: "user123", scope: "read", exp: ...} ──────
│  (your API)  │
└──────────────┘
```

The authorization code flow has two legs:

- **Leg 1:** Browser visits `/authorize` → server generates a short-lived code → redirects browser back to the client with `?code=xyz`
- **Leg 2:** Client backend calls `/token` with the code + its secret → server returns JWT access token

The client credentials flow collapses both legs into one: the client sends its `client_id` and `client_secret` directly to `/token` with no user involved. Used for service-to-service calls.

---

## Project File Structure

```
11_OAuth_Server/
├── main.py              ← FastAPI app, all routes
├── database.py          ← SQLite setup and connection helper
├── models.py            ← Pydantic request/response models
├── token_utils.py       ← JWT creation and verification helpers
├── .env                 ← JWT_SECRET, TOKEN_EXPIRE_MINUTES
└── oauth_server.db      ← created automatically on first run
```

---

## Step 1 — Database Schema

### Why SQLite here?

A real authorization server uses PostgreSQL or a dedicated store. SQLite is fine for this project because the goal is understanding OAuth flows, not database scaling. The schema is the same either way.

### The four tables

Every OAuth server needs to track:

1. **clients** — the apps that have registered with you (think: "apps that have enrolled in your OAuth program")
2. **authorization_codes** — short-lived codes issued during leg 1 of the auth code flow
3. **access_tokens** — JWTs you have issued (stored so you can introspect or revoke them)
4. **refresh_tokens** — long-lived tokens that let clients get new access tokens without re-asking the user

### Your task

Implement the `init_db()` function and the `get_db()` context manager in `database.py`. The `clients` table is given to you. You must add the other three.

<details><summary>💡 Hint — What columns does each table need?</summary>

```
clients:
  id INTEGER PRIMARY KEY
  client_id TEXT UNIQUE NOT NULL
  client_secret_hash TEXT NOT NULL   ← bcrypt hash, never store plaintext
  redirect_uris TEXT NOT NULL        ← store as JSON: '["https://app.example.com/cb"]'
  scopes TEXT NOT NULL               ← space-separated: "read write profile"
  grant_types TEXT NOT NULL          ← space-separated: "authorization_code client_credentials"

authorization_codes:
  code TEXT PRIMARY KEY              ← random urlsafe token, 32 bytes
  client_id TEXT NOT NULL
  user_id TEXT NOT NULL              ← whoever authorized (we'll fake this in tests)
  redirect_uri TEXT NOT NULL
  scope TEXT NOT NULL
  expires_at REAL NOT NULL           ← Unix timestamp (time.time() + 600)
  used INTEGER NOT NULL DEFAULT 0    ← 0 = fresh, 1 = already redeemed

access_tokens:
  token TEXT PRIMARY KEY             ← the JWT string itself
  client_id TEXT NOT NULL
  user_id TEXT                       ← NULL for client_credentials grant
  scope TEXT NOT NULL
  expires_at REAL NOT NULL

refresh_tokens:
  token TEXT PRIMARY KEY             ← random urlsafe token, 48 bytes
  client_id TEXT NOT NULL
  user_id TEXT
  scope TEXT NOT NULL
  expires_at REAL NOT NULL
  revoked INTEGER NOT NULL DEFAULT 0
```

The `used` flag on authorization_codes is critical — replay attacks work by stealing a code and redeeming it a second time. Check it and set it atomically.
</details>

<details><summary>✅ Show partial solution</summary>

```python
# database.py
import sqlite3
import json
from contextlib import contextmanager

DATABASE = "oauth_server.db"


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT UNIQUE NOT NULL,
                client_secret_hash TEXT NOT NULL,
                redirect_uris TEXT NOT NULL,
                scopes TEXT NOT NULL,
                grant_types TEXT NOT NULL
            );

            -- TODO: Create authorization_codes table
            -- Columns: code, client_id, user_id, redirect_uri, scope, expires_at, used

            -- TODO: Create access_tokens table
            -- Columns: token, client_id, user_id, scope, expires_at

            -- TODO: Create refresh_tokens table
            -- Columns: token, client_id, user_id, scope, expires_at, revoked
        """)


@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row   # rows behave like dicts: row["client_id"]
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_client(client_id: str):
    """Fetch a client row by client_id. Returns None if not found."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM clients WHERE client_id = ?", (client_id,)
        ).fetchone()
    return row


def get_authorization_code(code: str):
    """Fetch an authorization code row. Returns None if not found."""
    # TODO: implement
    pass


def mark_code_used(code: str):
    """Set used=1 on an authorization code."""
    # TODO: implement
    pass
```

</details>

---

## Step 2 — Client Registration Endpoint

### What is client registration?

Before any OAuth flow can happen, a client application must register with your server. This is like a company applying for a government-issued business license. Registration tells the server:

- Who is this client? (name, grant types it will use)
- Where should we send users after authorization? (redirect_uris — whitelist)
- What permissions is it allowed to request? (scopes)

At registration time, your server generates a `client_id` (public, like a username) and a `client_secret` (private, like a password). You return the plaintext secret **exactly once** — you never store it in plaintext, and the client must save it immediately.

### Hashing the client secret

`bcrypt` is the right tool here. It is deliberately slow (to resist brute-force) and includes a random salt automatically.

```python
import bcrypt

# Store this in the DB:
secret_hash = bcrypt.hashpw(plaintext_secret.encode(), bcrypt.gensalt()).decode()

# To verify later:
is_valid = bcrypt.checkpw(supplied_secret.encode(), stored_hash.encode())
```

### Your task

Implement `POST /clients/register` in `main.py`. Use the partial solution below as your starting point. You must add the database INSERT and return the response.

<details><summary>💡 Hint — Why return the plaintext secret at all?</summary>

The client needs the secret to authenticate itself at the `/token` endpoint. Since you only store the hash, this is the only moment the plaintext exists. If the client loses it, they must rotate (re-register or call a secret-rotation endpoint). This is the same reason AWS shows you a secret key exactly once when you create an IAM user.
</details>

<details><summary>✅ Show partial solution</summary>

```python
# models.py
from pydantic import BaseModel
from typing import List

class ClientRegistrationRequest(BaseModel):
    name: str
    redirect_uris: List[str]
    scopes: List[str]
    grant_types: List[str]   # valid values: "authorization_code", "client_credentials"

class ClientRegistrationResponse(BaseModel):
    client_id: str
    client_secret: str       # plaintext — shown once only
    name: str
    scopes: List[str]
    grant_types: List[str]
```

```python
# main.py (registration route)
import secrets
import bcrypt
import json
from fastapi import FastAPI, HTTPException
from database import init_db, get_db, get_client
from models import ClientRegistrationRequest, ClientRegistrationResponse

app = FastAPI(title="OAuth 2.0 Authorization Server")

@app.on_event("startup")
def startup():
    init_db()

VALID_GRANT_TYPES = {"authorization_code", "client_credentials", "refresh_token"}
VALID_SCOPES = {"read", "write", "profile", "email"}  # expand as needed

@app.post("/clients/register", response_model=ClientRegistrationResponse)
async def register_client(req: ClientRegistrationRequest):
    # Validate grant types
    invalid_grants = set(req.grant_types) - VALID_GRANT_TYPES
    if invalid_grants:
        raise HTTPException(400, f"Unsupported grant types: {invalid_grants}")

    # Generate credentials
    client_id = secrets.token_urlsafe(16)
    client_secret = secrets.token_urlsafe(32)
    secret_hash = bcrypt.hashpw(client_secret.encode(), bcrypt.gensalt()).decode()

    # TODO: Insert into clients table
    # Columns: client_id, client_secret_hash, redirect_uris (JSON), scopes (space-sep), grant_types (space-sep)
    # with get_db() as conn:
    #     conn.execute(...)

    # TODO: Return ClientRegistrationResponse with plaintext client_secret
    pass
```

</details>

---

## Step 3 — Authorization Endpoint (GET /authorize)

### What this endpoint does

The browser visits this endpoint directly — it is the start of the authorization code flow. Your server must:

1. Validate that `client_id` exists and is registered for `authorization_code` grant
2. Validate that `redirect_uri` is in the client's registered whitelist (security-critical — forged redirect URIs are a common attack)
3. Validate `response_type == "code"`
4. Validate that all requested `scope` values are in the client's allowed scopes
5. In a real server, show a login page and consent screen. We will fake this: accept a `user_id` query param to simulate an already-logged-in user
6. Generate a random authorization code, store it with a 10-minute expiry, then redirect to `redirect_uri?code=<code>&state=<state>`

### The state parameter

`state` is an opaque value the client includes in the authorization request. The server echoes it back in the redirect. The client uses it to prevent CSRF — it generates a random state, stores it in the session, and verifies the state in the callback matches. You must pass it through but do not need to validate it server-side.

### Your task

Implement `GET /authorize` as a FastAPI endpoint that returns a `RedirectResponse`.

<details><summary>💡 Hint — Generating and storing the code</summary>

```python
import time, secrets

code = secrets.token_urlsafe(32)
expires_at = time.time() + 600   # 10 minutes from now

# Store with: code, client_id, user_id, redirect_uri, scope, expires_at, used=0
```

For the redirect, use FastAPI's `RedirectResponse` with a 302 status:
```python
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode

params = {"code": code, "state": state}
return RedirectResponse(url=f"{redirect_uri}?{urlencode(params)}", status_code=302)
```
</details>

<details><summary>✅ Show partial solution</summary>

```python
# main.py — authorization endpoint
from fastapi import Query
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import time

@app.get("/authorize")
async def authorize(
    response_type: str = Query(...),
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    scope: str = Query(...),
    state: str = Query(default=""),
    user_id: str = Query(default="testuser"),   # simulates logged-in user
):
    # 1. Look up the client
    client = get_client(client_id)
    if not client:
        raise HTTPException(400, "Unknown client_id")

    # 2. Validate redirect_uri is in the registered whitelist
    registered_uris = json.loads(client["redirect_uris"])
    if redirect_uri not in registered_uris:
        # Do NOT redirect on this error — attacker controls redirect_uri
        raise HTTPException(400, "redirect_uri not registered")

    # 3. Validate response_type
    if response_type != "code":
        # TODO: redirect back with error=unsupported_response_type
        pass

    # 4. Validate scopes
    allowed_scopes = set(client["scopes"].split())
    requested_scopes = set(scope.split())
    if not requested_scopes.issubset(allowed_scopes):
        # TODO: redirect back with error=invalid_scope
        pass

    # 5. Generate and store authorization code
    code = secrets.token_urlsafe(32)
    expires_at = time.time() + 600

    # TODO: Insert into authorization_codes table
    # (code, client_id, user_id, redirect_uri, scope, expires_at, used=0)

    # 6. Redirect back to client with code
    params = {"code": code, "state": state}
    return RedirectResponse(
        url=f"{redirect_uri}?{urlencode(params)}",
        status_code=302
    )
```

</details>

---

## Step 4 — Token Endpoint: Authorization Code Grant

### The token exchange

This is leg 2 of the authorization code flow. The client's backend (not the browser) makes a server-to-server POST to `/token`. It sends:

- `grant_type=authorization_code`
- `code` — the code from the redirect
- `client_id` — its public identifier
- `client_secret` — its private secret
- `redirect_uri` — must match what was used in leg 1 (prevents code injection from a different redirect)

Your server must verify every field, mark the code as used (this is the replay-attack prevention step), then issue a signed JWT access token and a refresh token.

### Why mark the code used before issuing the token?

If you check-then-mark as two separate operations, a race condition lets two simultaneous requests both pass the check. Mark it used first, then issue the token. If something goes wrong during token generation, the code is already burned — the client must restart the flow. This is the correct tradeoff.

### JWT structure for the access token

```
Header:  { "alg": "HS256", "typ": "JWT" }
Payload: { "sub": "<user_id>", "client_id": "...", "scope": "...",
           "iat": <now>, "exp": <now + 3600>, "jti": "<unique id>" }
Signature: HMACSHA256(base64(header) + "." + base64(payload), JWT_SECRET)
```

`jti` (JWT ID) is a unique identifier per token — needed if you ever want to revoke individual tokens.

### Your task

Implement the `authorization_code` branch of `POST /token`. The token utility functions are given to you below — implement the database lookups and the grant logic.

<details><summary>💡 Hint — What to verify in order</summary>

```
1. grant_type == "authorization_code"
2. client = get_client(client_id)  → exists?
3. bcrypt.checkpw(client_secret, client["client_secret_hash"])  → valid?
4. "authorization_code" in client["grant_types"]
5. code_row = get_authorization_code(code)  → exists?
6. code_row["used"] == 0  → not already redeemed?
7. code_row["expires_at"] > time.time()  → not expired?
8. code_row["client_id"] == client_id  → belongs to this client?
9. code_row["redirect_uri"] == redirect_uri  → matches?
10. mark_code_used(code)  ← do this BEFORE issuing the token
11. create_access_token(...)
12. create_refresh_token(...)
13. store both in DB
14. return TokenResponse
```
</details>

<details><summary>✅ Show partial solution</summary>

```python
# token_utils.py
import os
import time
import secrets
from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 3600    # 1 hour
REFRESH_TOKEN_EXPIRE_SECONDS = 2592000  # 30 days


def create_access_token(client_id: str, user_id: str | None, scope: str) -> tuple[str, float]:
    """Returns (jwt_string, expires_at_unix_timestamp)."""
    now = time.time()
    expires_at = now + ACCESS_TOKEN_EXPIRE_SECONDS
    payload = {
        "sub": user_id or client_id,
        "client_id": client_id,
        "scope": scope,
        "iat": int(now),
        "exp": int(expires_at),
        "jti": secrets.token_urlsafe(16),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, expires_at


def decode_access_token(token: str) -> dict | None:
    """Decode and verify a JWT. Returns payload dict or None if invalid/expired."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def create_refresh_token() -> tuple[str, float]:
    """Returns (token_string, expires_at_unix_timestamp)."""
    token = secrets.token_urlsafe(48)
    expires_at = time.time() + REFRESH_TOKEN_EXPIRE_SECONDS
    return token, expires_at
```

```python
# main.py — token endpoint skeleton
from fastapi import Form
from models import TokenResponse

@app.post("/token", response_model=TokenResponse)
async def token_endpoint(
    grant_type: str = Form(...),
    # authorization_code params
    code: str = Form(default=None),
    redirect_uri: str = Form(default=None),
    # shared params
    client_id: str = Form(...),
    client_secret: str = Form(...),
    # refresh_token param
    refresh_token: str = Form(default=None),
    # client_credentials scope
    scope: str = Form(default="read"),
):
    if grant_type == "authorization_code":
        return await _authorization_code_grant(
            code, redirect_uri, client_id, client_secret
        )
    elif grant_type == "client_credentials":
        # TODO: implement in Step 5
        pass
    elif grant_type == "refresh_token":
        # TODO: implement in Step 7
        pass
    else:
        raise HTTPException(400, "unsupported_grant_type")


async def _authorization_code_grant(code, redirect_uri, client_id, client_secret):
    # Step 1: Validate client exists and secret matches
    client = get_client(client_id)
    if not client:
        raise HTTPException(401, "invalid_client")

    # TODO: verify client_secret against stored hash with bcrypt.checkpw

    # TODO: verify "authorization_code" in client["grant_types"]

    # Step 2: Validate the authorization code
    # TODO: code_row = get_authorization_code(code)
    # TODO: check code_row is not None
    # TODO: check code_row["used"] == 0
    # TODO: check code_row["expires_at"] > time.time()
    # TODO: check code_row["client_id"] == client_id
    # TODO: check code_row["redirect_uri"] == redirect_uri

    # Step 3: Mark code as used BEFORE issuing token
    # TODO: mark_code_used(code)

    # Step 4: Issue tokens
    # TODO: access_token, at_expires = create_access_token(client_id, code_row["user_id"], code_row["scope"])
    # TODO: refresh_tok, rt_expires = create_refresh_token()

    # Step 5: Persist tokens to DB
    # TODO: store access_token in access_tokens table
    # TODO: store refresh_tok in refresh_tokens table

    # Step 6: Return response
    # TODO: return TokenResponse(access_token=..., token_type="Bearer", expires_in=3600, refresh_token=..., scope=...)
    pass
```

```python
# models.py — add token response
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    refresh_token: str | None = None
    scope: str
```

</details>

---

## Step 5 — Token Endpoint: Client Credentials Grant

### What is the client credentials grant?

In the authorization code flow, a user is always involved — they authorize access on the consent screen. The client credentials grant removes the user entirely. The client authenticates directly with its own `client_id` and `client_secret` and receives an access token scoped to the client itself, not to any user.

Use cases:
- A cron job calling an internal API
- A microservice authenticating to another microservice
- Any machine-to-machine communication where there is no human session

The token's `sub` claim is set to the `client_id` rather than a user ID.

### Your task

Implement the `client_credentials` branch inside the `token_endpoint` function. It is simpler than the authorization code grant — there is no code to look up and no redirect URI to verify.

<details><summary>💡 Hint — What to verify</summary>

```
1. client = get_client(client_id)  → exists?
2. bcrypt.checkpw(client_secret, client["client_secret_hash"])  → valid?
3. "client_credentials" in client["grant_types"]
4. Validate that requested scope is subset of client's allowed scopes
5. create_access_token(client_id, user_id=None, scope=scope)
6. Store in access_tokens table  (user_id is NULL)
7. Return TokenResponse — no refresh_token for client credentials
```

RFC 6749 says refresh tokens SHOULD NOT be issued for the client credentials grant. The client can just re-authenticate directly — it does not need a long-lived token to avoid user re-prompting.
</details>

<details><summary>✅ Show partial solution</summary>

```python
# main.py — client credentials grant handler
async def _client_credentials_grant(client_id: str, client_secret: str, scope: str):
    # Validate client
    client = get_client(client_id)
    if not client:
        raise HTTPException(401, "invalid_client")

    # TODO: verify client_secret with bcrypt.checkpw

    # TODO: verify "client_credentials" in client["grant_types"].split()

    # Validate requested scopes are within what the client is allowed
    allowed_scopes = set(client["scopes"].split())
    requested_scopes = set(scope.split())
    if not requested_scopes.issubset(allowed_scopes):
        raise HTTPException(400, "invalid_scope")

    # Issue access token — no refresh token for this grant type
    access_token, expires_at = create_access_token(
        client_id=client_id,
        user_id=None,          # no user for client credentials
        scope=scope
    )

    # TODO: Store access_token in access_tokens table (user_id = NULL)

    return TokenResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=3600,
        refresh_token=None,    # intentionally omitted
        scope=scope
    )
```

</details>

---

## Step 6 — Token Introspection (POST /introspect)

### What is introspection?

A resource server (your API) receives a Bearer token from a client. It needs to know: is this token valid? Who does it belong to? What scopes does it have? Has it been revoked?

Rather than hardcoding JWT verification into every resource server, OAuth defines a standard endpoint (RFC 7662) on the authorization server: `POST /introspect`. The resource server sends the token; the authorization server replies with the token's metadata or `{"active": false}` if it is invalid.

This also enables token revocation — if a token has been revoked in your database, introspection returns `active: false` even if the JWT signature is still mathematically valid.

### The introspect response

```json
{
  "active": true,
  "sub": "user123",
  "client_id": "abc123",
  "scope": "read profile",
  "exp": 1714000000,
  "iat": 1713996400,
  "token_type": "Bearer"
}
```

If invalid or expired: `{"active": false}` — no other fields.

### Protecting the introspect endpoint

In production, only authorized resource servers should be able to call `/introspect`. You can protect it with HTTP Basic Auth using a separate set of "resource server credentials". For this project, keep it unprotected but add a TODO comment noting this.

### Your task

Implement `POST /introspect` that decodes the JWT, checks it exists in the `access_tokens` table and is not expired, then returns the full response or `{"active": false}`.

<details><summary>💡 Hint — Two-layer validation</summary>

You need both layers:

1. `decode_access_token(token)` — verifies the JWT signature and `exp` claim cryptographically
2. Check the `access_tokens` table — verifies the token has not been revoked and was actually issued by you

A token could have a valid signature but be revoked (deleted from DB). Always check both.
</details>

<details><summary>✅ Show partial solution</summary>

```python
# main.py — introspection endpoint
from fastapi import Form
import time

@app.post("/introspect")
async def introspect(token: str = Form(...)):
    # TODO: In production, authenticate the calling resource server here

    # Layer 1: Cryptographic verification
    payload = decode_access_token(token)
    if payload is None:
        return {"active": False}

    # Layer 2: Database check — was this token actually issued and not revoked?
    # TODO: Look up token in access_tokens table
    # token_row = ...
    # if not token_row:
    #     return {"active": False}

    # Layer 3: Expiry check against DB record (belt-and-suspenders)
    # TODO: if token_row["expires_at"] < time.time():
    #     return {"active": False}

    return {
        "active": True,
        "sub": payload.get("sub"),
        "client_id": payload.get("client_id"),
        "scope": payload.get("scope"),
        "exp": payload.get("exp"),
        "iat": payload.get("iat"),
        "token_type": "Bearer",
        # TODO: add "username" field if user_id is available
    }
```

</details>

---

## Step 7 — Refresh Token Flow

### Why refresh tokens exist

Access tokens are short-lived (1 hour) for security — if one is stolen, it stops working quickly. But asking the user to log in every hour would be terrible UX. Refresh tokens solve this: they are long-lived (30 days), stored securely by the client, and used only to get new access tokens from the authorization server.

The flow:

```
Client → POST /token  { grant_type=refresh_token, refresh_token=..., client_id=..., client_secret=... }
Server → verifies refresh token → issues new access_token + new refresh_token → revokes old refresh_token
```

### Refresh token rotation

Every time a refresh token is used, you issue a new one and revoke the old one. This is called **refresh token rotation**. If an attacker steals a refresh token and uses it, the next time the legitimate client tries to use it, you detect that the token has already been redeemed and can revoke the entire session.

### Your task

Implement the `refresh_token` branch of the token endpoint.

<details><summary>💡 Hint — What to verify</summary>

```
1. client exists and secret matches
2. refresh_token row exists in refresh_tokens table
3. refresh_token row: revoked == 0
4. refresh_token row: expires_at > time.time()
5. refresh_token row: client_id matches the requesting client
6. Mark old refresh token as revoked  (set revoked=1)
7. Issue new access_token
8. Issue new refresh_token (rotation)
9. Store both in DB
10. Return TokenResponse
```
</details>

<details><summary>✅ Show partial solution</summary>

```python
# database.py — add these helpers
def get_refresh_token(token: str):
    """Fetch a refresh token row. Returns None if not found."""
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM refresh_tokens WHERE token = ?", (token,)
        ).fetchone()


def revoke_refresh_token(token: str):
    """Mark a refresh token as revoked."""
    with get_db() as conn:
        conn.execute(
            "UPDATE refresh_tokens SET revoked = 1 WHERE token = ?", (token,)
        )
```

```python
# main.py — refresh token grant handler
async def _refresh_token_grant(refresh_token: str, client_id: str, client_secret: str):
    # Validate client
    client = get_client(client_id)
    if not client:
        raise HTTPException(401, "invalid_client")

    # TODO: verify client_secret with bcrypt.checkpw

    # Validate refresh token
    rt_row = get_refresh_token(refresh_token)
    if rt_row is None:
        raise HTTPException(400, "invalid_grant")

    if rt_row["revoked"] == 1:
        # Possible token theft — could revoke entire client session here
        raise HTTPException(400, "invalid_grant")

    if rt_row["expires_at"] < time.time():
        raise HTTPException(400, "invalid_grant")

    if rt_row["client_id"] != client_id:
        raise HTTPException(400, "invalid_grant")

    # Rotate: revoke old refresh token before issuing new one
    revoke_refresh_token(refresh_token)

    # Issue new tokens
    scope = rt_row["scope"]
    user_id = rt_row["user_id"]

    # TODO: new_access_token, at_expires = create_access_token(client_id, user_id, scope)
    # TODO: new_refresh_token, rt_expires = create_refresh_token()

    # TODO: Store new_access_token in access_tokens table
    # TODO: Store new_refresh_token in refresh_tokens table

    # TODO: return TokenResponse(...)
    pass
```

</details>

---

## Step 8 — Wire Everything Together and Test

### Start the server

```bash
# Create a .env file first
echo "JWT_SECRET=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" > .env

uvicorn main:app --reload --port 8000
```

### Manual test sequence

Work through these steps in order. Each one depends on the previous.

**Step 1 — Register a client**

```bash
curl -s -X POST http://localhost:8000/clients/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test App",
    "redirect_uris": ["http://localhost:9000/callback"],
    "scopes": ["read", "profile"],
    "grant_types": ["authorization_code", "client_credentials"]
  }' | python3 -m json.tool
```

Save the `client_id` and `client_secret` from the response.

**Step 2 — Get an authorization code**

Open this URL in your browser (replace values):

```
http://localhost:8000/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:9000/callback&scope=read&state=random123&user_id=alice
```

You will be redirected to `http://localhost:9000/callback?code=XXXX&state=random123`. Copy the `code` value from the URL.

**Step 3 — Exchange the code for a token**

```bash
curl -s -X POST http://localhost:8000/token \
  -d "grant_type=authorization_code" \
  -d "code=PASTE_CODE_HERE" \
  -d "redirect_uri=http://localhost:9000/callback" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" | python3 -m json.tool
```

**Step 4 — Introspect the access token**

```bash
curl -s -X POST http://localhost:8000/introspect \
  -d "token=PASTE_ACCESS_TOKEN_HERE" | python3 -m json.tool
```

Expected: `"active": true` with sub, scope, exp.

**Step 5 — Test client credentials flow end-to-end**

```bash
curl -s -X POST http://localhost:8000/token \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "scope=read" | python3 -m json.tool
```

**Step 6 — Test replay attack prevention**

Try submitting the same authorization code twice in Step 3. The second call should return `invalid_grant`.

**Step 7 — Use the refresh token**

```bash
curl -s -X POST http://localhost:8000/token \
  -d "grant_type=refresh_token" \
  -d "refresh_token=PASTE_REFRESH_TOKEN_HERE" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" | python3 -m json.tool
```

---

## Acceptance Criteria

- [ ] Client registration stores a bcrypt-hashed secret and returns the plaintext once
- [ ] `/authorize` rejects unknown `client_id` and unregistered `redirect_uri` values
- [ ] `/authorize` returns a code via redirect with correct `state` echo
- [ ] `/token` (authorization_code) exchanges a valid code for a JWT access token and refresh token
- [ ] `/token` rejects a code that has already been used (replay attack)
- [ ] `/token` rejects an expired authorization code
- [ ] `/token` (client_credentials) returns an access token with no refresh token
- [ ] `/introspect` returns `active: true` for a valid JWT that exists in the database
- [ ] `/introspect` returns `active: false` for an expired or tampered token
- [ ] `/token` (refresh_token) issues new access + refresh tokens and revokes the old refresh token
- [ ] Using a revoked refresh token returns `invalid_grant`

---

## What You Learned

The authorization server is the trust anchor in OAuth. Every other party — clients and resource servers — defer to it. This project shows you why:

- Authorization codes are one-time-use and short-lived. Stealing one after it is redeemed gives you nothing.
- The authorization server stores hashed secrets, never plaintext. Even a full DB dump is not catastrophic.
- The Client Credentials grant strips OAuth down to its simplest form: prove who you are, get a token. No browser, no user, no redirect — just machine-to-machine trust.
- Token introspection decouples resource servers from JWT verification logic. If you need to revoke a token mid-session, you delete it from the DB and the next introspect call returns `active: false` — no cryptographic rotation required.
- Refresh token rotation turns stolen refresh tokens into a detectable event: the original client presents a token you already know was used, which signals a breach.

---

## Next Project

[Project 13 — 2FA/TOTP Authentication](../12_2FA_TOTP/Project_Guide.md)
