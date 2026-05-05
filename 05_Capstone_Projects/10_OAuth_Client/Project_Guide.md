# Project 10 — OAuth Client: GitHub + Google Login

> Think of OAuth like a nightclub that accepts government-issued IDs instead of issuing their own. The bouncer (your app) doesn't verify you — they trust the government (GitHub/Google) to have already done that. You show your passport, the government stamps an approval, and the bouncer waves you in. Your app never sees your passport — only the stamp.

**Learning Format:** Fully Guided — Every step explained with complete code.
**What You Build:** A FastAPI app where users can "Login with GitHub" and "Login with Google", retrieve their profile, and receive a session JWT issued by your own app.
**Concepts Covered:** Authorization Code Flow, state parameter (CSRF protection), token exchange, profile fetch, OpenID Connect, JWT session issuance

---

## Prerequisites

- Completed: JWT Auth System (Project 05) — you will reuse JWT issuance logic
- Python packages: `fastapi`, `uvicorn[standard]`, `httpx`, `python-jose[cryptography]`, `python-dotenv`, `itsdangerous`
- GitHub OAuth App registered (instructions in Step 0a)
- Google OAuth Credentials registered (instructions in Step 0b)

Install all dependencies:

```bash
pip install fastapi "uvicorn[standard]" httpx "python-jose[cryptography]" python-dotenv itsdangerous
```

---

## 📋 Setup — Register OAuth Apps

### Step 0a — Create GitHub OAuth App

1. Go to [https://github.com/settings/developers](https://github.com/settings/developers)
2. Click **OAuth Apps** in the left sidebar
3. Click **New OAuth App**
4. Fill in the form:
   - **Application name:** `OAuth Demo App` (or anything you like)
   - **Homepage URL:** `http://localhost:8000`
   - **Authorization callback URL:** `http://localhost:8000/auth/github/callback`
5. Click **Register application**
6. On the next page, copy your **Client ID**
7. Click **Generate a new client secret** and copy the secret immediately (it will not be shown again)

### Step 0b — Create Google OAuth Credentials

1. Go to [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Navigate to **APIs & Services** → **OAuth consent screen**
   - Choose **External** user type
   - Fill in App name, support email, and developer contact email
   - Save and continue through the remaining screens (scopes and test users can be left at defaults)
4. Navigate to **APIs & Services** → **Credentials**
5. Click **+ Create Credentials** → **OAuth client ID**
6. Choose **Web application**
7. Under **Authorized redirect URIs**, add: `http://localhost:8000/auth/google/callback`
8. Click **Create**
9. Copy your **Client ID** and **Client Secret**

### Step 0c — .env file

Create a `.env` file in your project root:

```
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
JWT_SECRET=pick-a-long-random-string-here
STATE_SECRET=another-long-random-string-here
```

Add `.env` to your `.gitignore` — never commit secrets.

---

## Step 1 — Project Structure and FastAPI Base

### What we are building

The project lives in a single directory. The structure is intentionally flat — one `main.py` handles everything. For production you would split into routers, but for learning this keeps things clear.

```
10_OAuth_Client/
├── main.py          ← all routes and logic
├── .env             ← secrets (never commit this)
└── .gitignore
```

### Why httpx instead of requests?

FastAPI is async-native. The standard `requests` library is synchronous — it blocks the event loop while waiting for network responses. `httpx` has an identical API to `requests` but with an `AsyncClient` that plays nicely with `async def` route handlers. When your app calls GitHub's API or Google's token endpoint, it awaits the response without freezing other requests.

### The skeleton

`main.py` starts with configuration loading and a FastAPI instance. The routes will be added in later steps.

<details><summary>✅ Full Solution for Step 1</summary>

```python
# main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
import httpx
from jose import jwt, JWTError
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from datetime import datetime, timedelta, timezone

load_dotenv()

# ── Configuration ────────────────────────────────────────────────────────────
GITHUB_CLIENT_ID     = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
JWT_SECRET           = os.getenv("JWT_SECRET", "change-me")
STATE_SECRET         = os.getenv("STATE_SECRET", "change-me-too")

GITHUB_REDIRECT_URI  = "http://localhost:8000/auth/github/callback"
GOOGLE_REDIRECT_URI  = "http://localhost:8000/auth/google/callback"

# itsdangerous serializer — signs state tokens so we can verify they came from us
state_serializer = URLSafeTimedSerializer(STATE_SECRET)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="OAuth Client Demo")


@app.get("/")
async def root():
    return {
        "message": "OAuth Client Demo",
        "routes": [
            "/auth/github/login",
            "/auth/google/login",
            "/me  (requires Bearer JWT)",
        ],
    }
```

</details>

---

## Step 2 — The OAuth Flow (Theory First)

Before writing any more code, it is worth understanding every network hop. This diagram shows the Authorization Code Flow — the same flow used by both GitHub and Google.

```
┌─────────┐         ┌─────────────┐         ┌──────────────────┐
│ Browser │         │  Your App   │         │  GitHub / Google │
└────┬────┘         └──────┬──────┘         └────────┬─────────┘
     │                     │                          │
     │  GET /auth/github/  │                          │
     │  login              │                          │
     │────────────────────>│                          │
     │                     │  Build authorization URL │
     │                     │  (client_id, scope,      │
     │                     │   redirect_uri, state)   │
     │  302 Redirect to    │                          │
     │  github.com/login/  │                          │
     │  oauth/authorize    │                          │
     │<────────────────────│                          │
     │                     │                          │
     │  GET /login/oauth/authorize                    │
     │───────────────────────────────────────────────>│
     │                     │                          │
     │  GitHub login page  │                          │
     │<───────────────────────────────────────────────│
     │                     │                          │
     │  User approves      │                          │
     │───────────────────────────────────────────────>│
     │                     │                          │
     │  302 redirect to    │                          │
     │  /auth/github/callback?code=XYZ&state=ABC      │
     │<───────────────────────────────────────────────│
     │                     │                          │
     │  GET /auth/github/  │                          │
     │  callback?code=XYZ  │                          │
     │────────────────────>│                          │
     │                     │  POST /login/oauth/      │
     │                     │  access_token            │
     │                     │  {code, client_secret}   │
     │                     │─────────────────────────>│
     │                     │                          │
     │                     │  {access_token: "gho_…"} │
     │                     │<─────────────────────────│
     │                     │                          │
     │                     │  GET /user               │
     │                     │  Authorization: Bearer   │
     │                     │─────────────────────────>│
     │                     │                          │
     │                     │  {login, id, email, …}   │
     │                     │<─────────────────────────│
     │                     │                          │
     │                     │  Issue session JWT       │
     │  {access_token:     │  (sub=github_id,         │
     │   "eyJ…"}           │   provider=github)       │
     │<────────────────────│                          │
```

### What each arrow means

**Arrow 1-2 (login redirect):** Your app builds a URL pointing at GitHub's authorization endpoint and redirects the browser there. Your app never handles the user's GitHub password — it never even sees it.

**Arrow 3-4 (user approves):** The user logs into GitHub directly (in the browser, not through your app) and clicks "Authorize". GitHub records that your app has been granted the requested scopes.

**Arrow 5 (callback with code):** GitHub redirects the browser back to your `redirect_uri` with a short-lived `code` query parameter. This code is useless on its own — it can only be exchanged for a real token by a server that also knows the `client_secret`.

**Arrow 6-7 (token exchange):** Your server POSTs the `code` plus your `client_secret` to GitHub. This is a server-to-server call — the browser is not involved. GitHub returns an `access_token`.

**Arrow 8-9 (profile fetch):** Your server uses the `access_token` to call GitHub's user API and gets the user's identity.

**Arrow 10 (your JWT):** Your server issues its own JWT. From this point on, your app uses its own JWT — it never calls GitHub again until the user wants to re-authenticate.

---

## Step 3 — GitHub Login Redirect

### What this endpoint does

When a user visits `/auth/github/login`, your app must redirect them to GitHub's authorization page. The URL you build contains:

- `client_id` — tells GitHub which app is requesting access
- `redirect_uri` — where GitHub should send the user after approval (must match what you registered)
- `scope` — what permissions you are requesting (`read:user user:email` for profile and email)
- `state` — a random token that you generate, sign, and verify on the way back

### The state parameter

The state parameter exists to prevent Cross-Site Request Forgery (CSRF). Here is the attack without state:

1. An attacker crafts a GitHub callback URL: `http://yourapp.com/auth/github/callback?code=ATTACKERS_CODE`
2. The attacker tricks a logged-in user into visiting that URL (via an email link, img tag, etc.)
3. Your app exchanges the attacker's code for a token and logs the victim in as the attacker

With state:
1. Your app generates a random state token before the redirect and stores it
2. GitHub echoes the state back in the callback
3. Your app verifies the echoed state matches what it stored
4. If the state does not match, the request is rejected

`itsdangerous.URLSafeTimedSerializer` lets us sign the state value with a secret key and verify it on return — without needing a database or session store.

<details><summary>💡 Why do we need the state parameter?</summary>

Without state, a malicious website could link a user to `http://yourapp.com/auth/github/callback?code=evil_code`. Your app would exchange that code — which belongs to the attacker's GitHub account — and log the user in as the attacker. State ties each login attempt to a specific browser session by requiring that the value echoed back by GitHub must have been cryptographically signed by your server before the redirect.

</details>

<details><summary>✅ Full Solution for Step 3</summary>

```python
import secrets

@app.get("/auth/github/login")
async def github_login():
    """
    Build the GitHub authorization URL and redirect the browser there.
    The state token is signed with itsdangerous so we can verify it on return.
    """
    # Generate a random nonce, then sign it — this is our state token
    raw_nonce = secrets.token_urlsafe(32)
    signed_state = state_serializer.dumps(raw_nonce)

    params = {
        "client_id":    GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "scope":        "read:user user:email",
        "state":        signed_state,
    }

    # Build the query string manually (httpx can do this too)
    from urllib.parse import urlencode
    authorization_url = "https://github.com/login/oauth/authorize?" + urlencode(params)

    return RedirectResponse(url=authorization_url)
```

Add `import secrets` and `from urllib.parse import urlencode` to the top of `main.py`.

</details>

---

## Step 4 — GitHub Callback Handler

### What this endpoint does

After the user approves your app on GitHub, their browser is redirected back to your `redirect_uri` with two query parameters:

- `code` — a short-lived authorization code (expires in ~10 minutes, single-use)
- `state` — the signed state token you sent in Step 3

Your callback handler must:
1. Verify the state signature (CSRF protection)
2. POST the code to GitHub's token endpoint along with your client secret
3. Extract the `access_token` from the response

The code is useless to anyone without your `client_secret`, which is why the token exchange is a server-to-server call.

<details><summary>✅ Full Solution for Step 4</summary>

```python
@app.get("/auth/github/callback")
async def github_callback(code: str, state: str, request: Request):
    """
    GitHub redirects here after user approves (or denies) access.
    1. Verify state to prevent CSRF
    2. Exchange code for access_token
    3. Fetch user profile
    4. Issue session JWT
    """
    # ── 1. Verify state ──────────────────────────────────────────────────────
    try:
        # max_age=300 means the state token expires after 5 minutes
        state_serializer.loads(state, max_age=300)
    except SignatureExpired:
        raise HTTPException(status_code=400, detail="State token expired — please try logging in again")
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid state token — possible CSRF attack")

    # ── 2. Exchange code for access_token ────────────────────────────────────
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id":     GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code":          code,
                "redirect_uri":  GITHUB_REDIRECT_URI,
            },
        )

    token_data = token_response.json()

    if "error" in token_data:
        raise HTTPException(
            status_code=400,
            detail=f"GitHub token exchange failed: {token_data.get('error_description', token_data['error'])}",
        )

    access_token = token_data["access_token"]

    # ── 3. Fetch profile (Step 5) ─────────────────────────────────────────────
    profile = await fetch_github_profile(access_token)

    # ── 4. Issue session JWT (Step 6) ─────────────────────────────────────────
    session_jwt = issue_session_jwt(
        user_id=str(profile["id"]),
        provider="github",
        login=profile.get("login"),
        email=profile.get("email"),
        avatar_url=profile.get("avatar_url"),
    )

    return JSONResponse({
        "message":      "GitHub login successful",
        "access_token": session_jwt,
        "token_type":   "bearer",
        "profile":      profile,
    })
```

</details>

---

## Step 5 — Fetch GitHub User Profile

### What this endpoint does

The GitHub `access_token` grants read access to the user's GitHub account (within the scopes you requested). You call the GitHub `/user` endpoint, passing the token in the `Authorization` header, and get back a JSON object with the user's id, login (username), name, email, and avatar URL.

One edge case: GitHub users can set their email to private. When that happens, `/user` returns `email: null`. To reliably get the email you must also call `/user/emails` — which is included in the `user:email` scope you requested.

<details><summary>✅ Full Solution for Step 5</summary>

```python
async def fetch_github_profile(access_token: str) -> dict:
    """
    Call GitHub's /user API to get the authenticated user's profile.
    If email is null (user has private email), fetch from /user/emails.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept":        "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    async with httpx.AsyncClient() as client:
        # Primary profile
        user_resp = await client.get("https://api.github.com/user", headers=headers)
        user_resp.raise_for_status()
        profile = user_resp.json()

        # If email is private, fetch it from the emails endpoint
        if not profile.get("email"):
            emails_resp = await client.get("https://api.github.com/user/emails", headers=headers)
            if emails_resp.status_code == 200:
                emails = emails_resp.json()
                # Primary verified email takes precedence
                primary = next(
                    (e["email"] for e in emails if e.get("primary") and e.get("verified")),
                    None,
                )
                profile["email"] = primary

    return {
        "id":         profile["id"],
        "login":      profile.get("login"),
        "name":       profile.get("name"),
        "email":      profile.get("email"),
        "avatar_url": profile.get("avatar_url"),
        "provider":   "github",
    }
```

</details>

---

## Step 6 — Issue Session JWT

### Why your app issues its own JWT

After verifying the user's identity through GitHub, you have two options for subsequent requests:

Option A: Store the GitHub `access_token` and call GitHub on every request to verify the user.
Option B: Issue your own JWT, valid for a fixed window, and verify that locally.

Option A creates a hard dependency on GitHub — if GitHub is down, your app breaks. It also leaks GitHub tokens and makes every authenticated request to your app trigger a network call to GitHub.

Option B is stateless and fast. Your app is the authority on sessions. GitHub was only needed once — to prove who the user is. After that, your JWT carries the identity forward.

The JWT payload includes `sub` (subject = your user's ID from the provider), `provider` (so you know which OAuth service authenticated them), and standard claims like `exp` (expiry).

<details><summary>✅ Full Solution for Step 6</summary>

```python
def issue_session_jwt(
    user_id: str,
    provider: str,
    login: str | None = None,
    email: str | None = None,
    avatar_url: str | None = None,
    expires_minutes: int = 60,
) -> str:
    """
    Issue a session JWT that your app controls.
    The provider (GitHub/Google) is only used for initial authentication.
    All subsequent requests use this JWT.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub":        user_id,
        "provider":   provider,
        "login":      login,
        "email":      email,
        "avatar_url": avatar_url,
        "iat":        now,
        "exp":        now + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
```

</details>

---

## Step 7 — Google Login Redirect

### How Google differs from GitHub

GitHub implements plain OAuth 2.0. Google implements OAuth 2.0 plus OpenID Connect (OIDC).

The practical difference at the redirect stage is the scopes:

- GitHub: `read:user user:email` — provider-specific strings
- Google: `openid email profile` — standardized OIDC scopes

The `openid` scope is the signal that you want identity (not just resource access). When you include it, Google's token response will include an `id_token` — a JWT containing the user's identity information directly. This means you do not need to make a second API call to get the user's name and email (unlike GitHub, where you had to call `/user` after getting the token).

<details><summary>💡 What is OpenID Connect vs OAuth 2.0?</summary>

OAuth 2.0 answers: "Can this app access your files?"
OpenID Connect answers: "Who are you?"

OAuth 2.0 was designed for authorization — granting an app access to resources. It was never intended for authentication. OpenID Connect is a thin identity layer built on top of OAuth 2.0. It adds the `id_token`, a JWT that proves the user's identity, and standardizes how you get their name and email.

When you log in with Google, you are using OIDC. The `id_token` in Google's response is a JWT signed by Google. You can decode it locally (after verifying the signature against Google's public keys) to get the user's `sub` (stable unique ID), `email`, `name`, and `picture` — no extra API call required.

</details>

<details><summary>✅ Full Solution for Step 7</summary>

```python
@app.get("/auth/google/login")
async def google_login():
    """
    Build the Google authorization URL and redirect the browser there.
    Uses OpenID Connect scopes: openid email profile.
    """
    raw_nonce = secrets.token_urlsafe(32)
    signed_state = state_serializer.dumps(raw_nonce)

    params = {
        "client_id":             GOOGLE_CLIENT_ID,
        "redirect_uri":          GOOGLE_REDIRECT_URI,
        "response_type":         "code",
        "scope":                 "openid email profile",
        "state":                 signed_state,
        "access_type":           "online",   # "offline" would request a refresh token
        "prompt":                "select_account",  # always show account chooser
    }

    from urllib.parse import urlencode
    authorization_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)

    return RedirectResponse(url=authorization_url)
```

</details>

---

## Step 8 — Google Callback Handler

### Token exchange and id_token decoding

The Google callback is structurally identical to GitHub's: receive `code` + `state`, verify state, exchange code for tokens. The key difference is what comes back from Google's token endpoint.

GitHub returns: `{ "access_token": "gho_..." }`

Google returns: `{ "access_token": "...", "id_token": "eyJ..." }`

The `id_token` is a JWT signed by Google. Decoding it gives you the user's identity directly — no second API call needed. The claims inside include:

- `sub` — a stable, unique Google user ID (use this as your user's primary key, not email)
- `email` — the user's email address
- `email_verified` — whether Google has verified this email
- `name` — the user's full name
- `picture` — URL to their profile photo

For a production app you would verify the `id_token` signature against Google's JWKS (JSON Web Key Set) at `https://www.googleapis.com/oauth2/v3/certs`. For this demo we decode without verification — the token came directly from Google's HTTPS endpoint, so the transport layer provides sufficient assurance.

<details><summary>✅ Full Solution for Step 8</summary>

```python
@app.get("/auth/google/callback")
async def google_callback(code: str, state: str, request: Request):
    """
    Google redirects here after user approves (or denies) access.
    1. Verify state
    2. Exchange code for access_token + id_token
    3. Decode id_token to get user identity (no extra API call needed)
    4. Issue session JWT
    """
    # ── 1. Verify state ──────────────────────────────────────────────────────
    try:
        state_serializer.loads(state, max_age=300)
    except SignatureExpired:
        raise HTTPException(status_code=400, detail="State token expired — please try logging in again")
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid state token — possible CSRF attack")

    # ── 2. Exchange code for tokens ──────────────────────────────────────────
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id":     GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "code":          code,
                "redirect_uri":  GOOGLE_REDIRECT_URI,
                "grant_type":    "authorization_code",
            },
        )

    token_data = token_response.json()

    if "error" in token_data:
        raise HTTPException(
            status_code=400,
            detail=f"Google token exchange failed: {token_data.get('error_description', token_data['error'])}",
        )

    id_token_raw = token_data.get("id_token")
    if not id_token_raw:
        raise HTTPException(status_code=400, detail="Google did not return an id_token")

    # ── 3. Decode id_token ────────────────────────────────────────────────────
    # options={"verify_signature": False} skips JWKS verification.
    # For production: fetch Google's JWKS and verify the signature.
    claims = jwt.decode(
        id_token_raw,
        key="",                          # not used when verify_signature=False
        algorithms=["RS256"],
        options={"verify_signature": False},
    )

    profile = {
        "id":         claims["sub"],      # stable unique Google user ID
        "email":      claims.get("email"),
        "name":       claims.get("name"),
        "avatar_url": claims.get("picture"),
        "provider":   "google",
    }

    # ── 4. Issue session JWT ──────────────────────────────────────────────────
    session_jwt = issue_session_jwt(
        user_id=str(profile["id"]),
        provider="google",
        login=profile.get("email"),      # Google has no "login", use email
        email=profile.get("email"),
        avatar_url=profile.get("avatar_url"),
    )

    return JSONResponse({
        "message":      "Google login successful",
        "access_token": session_jwt,
        "token_type":   "bearer",
        "profile":      profile,
    })
```

</details>

---

## Step 9 — Protected Route Using Session JWT

### The /me endpoint

Once the user has a session JWT (from either GitHub or Google login), they use it as a Bearer token on all subsequent requests. The `/me` endpoint demonstrates this: it decodes the JWT, verifies the signature and expiry, and returns the user's stored identity.

This endpoint is completely provider-agnostic. It does not know or care whether the user authenticated via GitHub or Google. The `provider` field in the JWT payload tells you their origin, but the verification logic is identical.

<details><summary>✅ Full Solution for Step 9</summary>

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

bearer_scheme = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """
    Dependency that validates the session JWT and returns the decoded payload.
    Works regardless of whether the user authenticated via GitHub or Google.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid or expired session token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    """
    Protected endpoint. Requires a valid session JWT in the Authorization header.
    Returns the user's identity as stored in the JWT payload.
    """
    return {
        "user_id":    current_user["sub"],
        "provider":   current_user.get("provider"),
        "login":      current_user.get("login"),
        "email":      current_user.get("email"),
        "avatar_url": current_user.get("avatar_url"),
    }
```

</details>

---

## Step 10 — Complete main.py

Here is the complete, final `main.py` with all steps assembled in the correct order.

```python
# main.py
import os
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from jose import JWTError, jwt

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────
GITHUB_CLIENT_ID     = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
JWT_SECRET           = os.getenv("JWT_SECRET", "change-me")
STATE_SECRET         = os.getenv("STATE_SECRET", "change-me-too")

GITHUB_REDIRECT_URI  = "http://localhost:8000/auth/github/callback"
GOOGLE_REDIRECT_URI  = "http://localhost:8000/auth/google/callback"

state_serializer = URLSafeTimedSerializer(STATE_SECRET)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="OAuth Client Demo")

bearer_scheme = HTTPBearer()


# ── Helpers ───────────────────────────────────────────────────────────────────

def issue_session_jwt(
    user_id: str,
    provider: str,
    login: str | None = None,
    email: str | None = None,
    avatar_url: str | None = None,
    expires_minutes: int = 60,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub":        user_id,
        "provider":   provider,
        "login":      login,
        "email":      email,
        "avatar_url": avatar_url,
        "iat":        now,
        "exp":        now + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


async def fetch_github_profile(access_token: str) -> dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept":        "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    async with httpx.AsyncClient() as client:
        user_resp = await client.get("https://api.github.com/user", headers=headers)
        user_resp.raise_for_status()
        profile = user_resp.json()

        if not profile.get("email"):
            emails_resp = await client.get("https://api.github.com/user/emails", headers=headers)
            if emails_resp.status_code == 200:
                emails = emails_resp.json()
                primary = next(
                    (e["email"] for e in emails if e.get("primary") and e.get("verified")),
                    None,
                )
                profile["email"] = primary

    return {
        "id":         profile["id"],
        "login":      profile.get("login"),
        "name":       profile.get("name"),
        "email":      profile.get("email"),
        "avatar_url": profile.get("avatar_url"),
        "provider":   "github",
    }


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid or expired session token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "message": "OAuth Client Demo",
        "routes": [
            "GET /auth/github/login",
            "GET /auth/github/callback  (called by GitHub)",
            "GET /auth/google/login",
            "GET /auth/google/callback  (called by Google)",
            "GET /me  (requires Authorization: Bearer <jwt>)",
        ],
    }


@app.get("/auth/github/login")
async def github_login():
    raw_nonce = secrets.token_urlsafe(32)
    signed_state = state_serializer.dumps(raw_nonce)

    params = {
        "client_id":    GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "scope":        "read:user user:email",
        "state":        signed_state,
    }
    return RedirectResponse(url="https://github.com/login/oauth/authorize?" + urlencode(params))


@app.get("/auth/github/callback")
async def github_callback(code: str, state: str, request: Request):
    # 1. Verify state
    try:
        state_serializer.loads(state, max_age=300)
    except SignatureExpired:
        raise HTTPException(status_code=400, detail="State token expired — please try logging in again")
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid state token — possible CSRF attack")

    # 2. Exchange code for access_token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id":     GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code":          code,
                "redirect_uri":  GITHUB_REDIRECT_URI,
            },
        )
    token_data = token_response.json()
    if "error" in token_data:
        raise HTTPException(
            status_code=400,
            detail=f"GitHub token exchange failed: {token_data.get('error_description', token_data['error'])}",
        )
    access_token = token_data["access_token"]

    # 3. Fetch profile
    profile = await fetch_github_profile(access_token)

    # 4. Issue session JWT
    session_jwt = issue_session_jwt(
        user_id=str(profile["id"]),
        provider="github",
        login=profile.get("login"),
        email=profile.get("email"),
        avatar_url=profile.get("avatar_url"),
    )

    return JSONResponse({
        "message":      "GitHub login successful",
        "access_token": session_jwt,
        "token_type":   "bearer",
        "profile":      profile,
    })


@app.get("/auth/google/login")
async def google_login():
    raw_nonce = secrets.token_urlsafe(32)
    signed_state = state_serializer.dumps(raw_nonce)

    params = {
        "client_id":     GOOGLE_CLIENT_ID,
        "redirect_uri":  GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope":         "openid email profile",
        "state":         signed_state,
        "access_type":   "online",
        "prompt":        "select_account",
    }
    return RedirectResponse(
        url="https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    )


@app.get("/auth/google/callback")
async def google_callback(code: str, state: str, request: Request):
    # 1. Verify state
    try:
        state_serializer.loads(state, max_age=300)
    except SignatureExpired:
        raise HTTPException(status_code=400, detail="State token expired — please try logging in again")
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid state token — possible CSRF attack")

    # 2. Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id":     GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "code":          code,
                "redirect_uri":  GOOGLE_REDIRECT_URI,
                "grant_type":    "authorization_code",
            },
        )
    token_data = token_response.json()
    if "error" in token_data:
        raise HTTPException(
            status_code=400,
            detail=f"Google token exchange failed: {token_data.get('error_description', token_data['error'])}",
        )

    id_token_raw = token_data.get("id_token")
    if not id_token_raw:
        raise HTTPException(status_code=400, detail="Google did not return an id_token")

    # 3. Decode id_token (skip signature verification for demo — use JWKS in production)
    claims = jwt.decode(
        id_token_raw,
        key="",
        algorithms=["RS256"],
        options={"verify_signature": False},
    )

    profile = {
        "id":         claims["sub"],
        "email":      claims.get("email"),
        "name":       claims.get("name"),
        "avatar_url": claims.get("picture"),
        "provider":   "google",
    }

    # 4. Issue session JWT
    session_jwt = issue_session_jwt(
        user_id=str(profile["id"]),
        provider="google",
        login=profile.get("email"),
        email=profile.get("email"),
        avatar_url=profile.get("avatar_url"),
    )

    return JSONResponse({
        "message":      "Google login successful",
        "access_token": session_jwt,
        "token_type":   "bearer",
        "profile":      profile,
    })


@app.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    return {
        "user_id":    current_user["sub"],
        "provider":   current_user.get("provider"),
        "login":      current_user.get("login"),
        "email":      current_user.get("email"),
        "avatar_url": current_user.get("avatar_url"),
    }
```

---

## Step 11 — Test the Full Flow

### Start the server

```bash
uvicorn main:app --reload
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### GitHub flow

1. Open your browser and visit: `http://localhost:8000/auth/github/login`
2. You are redirected to GitHub's login/authorization page
3. Approve the app
4. Your browser lands back at the callback URL and you see a JSON response containing `access_token`
5. Copy the JWT value

```bash
# Call the protected /me endpoint with the JWT
curl -H "Authorization: Bearer <paste-your-jwt-here>" http://localhost:8000/me
```

Expected response:

```json
{
  "user_id": "12345678",
  "provider": "github",
  "login": "your-github-username",
  "email": "you@example.com",
  "avatar_url": "https://avatars.githubusercontent.com/u/12345678"
}
```

### Google flow

1. Visit: `http://localhost:8000/auth/google/login`
2. Select your Google account and approve
3. Copy the JWT from the response
4. Use the same curl command above — `/me` does not care which provider you used

### Verify JWT contents manually

Paste your JWT into [https://jwt.io](https://jwt.io) to inspect the decoded payload. You will see your user ID, provider, email, and expiry time in plain JSON.

---

## Step 12 — Common Pitfalls and What To Watch For

| Problem | Cause | Fix |
|---|---|---|
| `state mismatch` / `BadSignature` error | Browser cookies cleared between login and callback, or multiple tabs | Use a single browser tab for testing; in production, store state in a server-side session |
| `State token expired` | More than 5 minutes passed between login redirect and callback | Increase `max_age` in `state_serializer.loads()` |
| Google callback returns `redirect_uri_mismatch` | The callback URL in your code does not exactly match the one registered in Google Cloud Console | Verify `http://localhost:8000/auth/google/callback` is listed under Authorized redirect URIs |
| GitHub returns `{"error": "bad_verification_code"}` | The authorization code was already used (codes are single-use) or expired | Start the flow again from `/auth/github/login` |
| GitHub returns no email | User has private email in GitHub settings | The `user:email` scope + `/user/emails` API call handles this — see `fetch_github_profile` |
| `JWTError` on `/me` | Session JWT has expired (default 60 minutes) | Log in again to get a fresh JWT; adjust `expires_minutes` in `issue_session_jwt` |
| `CORS` error when calling from a browser app | FastAPI CORS middleware not configured | Add `from fastapi.middleware.cors import CORSMiddleware` and configure allowed origins |
| Google `id_token` decode fails with `DecodeError` | `python-jose` version mismatch or missing RS256 support | Ensure `python-jose[cryptography]` is installed (not just `python-jose`) |

---

## What You Learned

The Authorization Code Flow has the same shape for every provider: redirect the browser to the provider's authorization endpoint, receive a short-lived code on your callback URL, exchange the code server-to-server for an access token, then use that token to fetch identity.

The state parameter is not optional decoration — it is the only thing preventing an attacker from forcing a victim to authenticate as the attacker's account. Signing the state with `itsdangerous` lets you verify it without a database.

GitHub and Google both implement OAuth 2.0, but Google adds OpenID Connect on top. The `id_token` is the OIDC contribution: a JWT that carries the user's identity directly, signed by Google, so you can decode it without making another API call.

Your app issues its own JWT after authenticating via the provider. This is the right architecture: the provider proves identity once, then your JWT handles authorization for the rest of the session. Your app never calls GitHub or Google again unless the user needs to re-authenticate.

---

## Next Project

[Project 12 — OAuth Server: Build the authorization server yourself](../11_OAuth_Server/Project_Guide.md)
