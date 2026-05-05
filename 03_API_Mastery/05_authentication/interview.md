# 🎯 Authentication & Authorization — Interview Preparation

> This file prepares you to discuss API authentication and authorization like a working engineer.
> Not just definitions — but real-world usage, trade-offs, and production scenarios.

---

# 🔹 Basic Level Questions (0–2 Years)

**Q1: What is the difference between authentication and authorization?**

<details>
<summary>💡 Show Answer</summary>

Authentication answers "who are you?" — it verifies identity. Authorization answers "what are you allowed to do?" — it checks permissions. You must be authenticated before you can be authorized.

Example: logging into GitHub is authentication. Whether you can push to a private repo is authorization. An API returns 401 when it can't verify who you are (not authenticated), and 403 when it knows who you are but you lack permission (authenticated, not authorized). Mixing these up is a common mistake — returning 401 for a forbidden resource causes clients to retry auth unnecessarily.

</details>

<br>

**Q2: What are the three parts of a JWT and what does each contain?**

<details>
<summary>💡 Show Answer</summary>

A JWT is three base64url-encoded sections separated by dots: `header.payload.signature`.

The header contains the algorithm and token type: `{"alg": "HS256", "typ": "JWT"}`. The payload contains claims — the data about the user: `{"sub": "42", "email": "alice@example.com", "roles": ["admin"], "exp": 1709900000}`. The signature is a cryptographic hash of `base64(header) + "." + base64(payload)` using the secret or private key.

Critical point: the payload is NOT encrypted — it is base64-encoded, which is trivially reversible. Anyone who intercepts a JWT can read the payload. Never put passwords, secrets, or sensitive PII in a JWT.

</details>

<br>

**Q3: Why should you never put an API key in a URL query parameter?**

<details>
<summary>💡 Show Answer</summary>

URLs end up in server access logs, browser history, browser referrer headers, CDN logs, and load balancer logs — typically in plaintext. An API key in `?api_key=sk-abc123` is therefore logged in multiple places outside your control, and anyone with access to those logs has your key.

The correct location is the `Authorization` header (`Authorization: ApiKey sk-abc123` or a custom `X-API-Key: sk-abc123` header). Headers are not logged by default in most infrastructure. They are also not included in browser history or referrer headers. This is why every major API (OpenAI, Stripe, GitHub) puts credentials in headers.

</details>

<br>

**Q4: What is the purpose of an access token and a refresh token? Why are they different lifetimes?**

<details>
<summary>💡 Show Answer</summary>

The access token is short-lived (typically 15 minutes to 1 hour) and is sent with every API request. Because it's transmitted frequently, it has a higher risk of exposure. Short expiry limits the damage if it's stolen — an attacker has at most 15 minutes before the token is useless.

The refresh token is long-lived (days to weeks) and is only sent to a single endpoint (`/auth/refresh`) to get a new access token. It's stored securely (ideally in an HttpOnly cookie) and is never sent with normal API calls. When the access token expires, the client silently exchanges the refresh token for a new access token — the user never logs in again. Logout invalidates the refresh token on the server side.

</details>

<br>

**Q5: What is CORS and why do browsers enforce it?**

<details>
<summary>💡 Show Answer</summary>

CORS (Cross-Origin Resource Sharing) is a browser security mechanism that prevents JavaScript on `malicious.com` from making credentialed requests to `api.yourbank.com` using your stored cookies. Without it, a malicious site could make API calls on your behalf using your session.

Browsers enforce the Same-Origin Policy by default and only relax it when the server explicitly allows it via CORS headers: `Access-Control-Allow-Origin: https://yourapp.com`. For "non-simple" requests (PUT, DELETE, or requests with custom headers like Authorization), browsers send a preflight OPTIONS request first to check permissions. CORS is enforced by browsers only — curl and server-to-server calls are not affected.

</details>

<br>

---

# 🔹 Intermediate Level Questions (2–5 Years)

**Q6: What three checks must you perform when validating a JWT?**

<details>
<summary>💡 Show Answer</summary>

(1) Signature validity: verify the cryptographic signature against the expected key and algorithm. This confirms the token was issued by your auth server and hasn't been tampered with. (2) Expiry: check the `exp` claim — reject tokens past their expiry time. (3) Issuer: check the `iss` claim matches your expected issuer string. Also check `aud` (audience) if your system has multiple services.

Most libraries do these automatically if you specify them: `jwt.decode(token, secret, algorithms=["HS256"], issuer="api.myapp.com")`. The critical gotcha: always specify `algorithms=["HS256"]` explicitly. Libraries that accept the algorithm from the token header itself are vulnerable to the `alg:none` attack where an attacker forges a token with no signature.

</details>

<br>

**Q7: What is the difference between HS256 and RS256 JWT signing and when do you use each?**

<details>
<summary>💡 Show Answer</summary>

HS256 uses a single shared secret for both signing and verification. Any service with the secret can both create and verify tokens. This is simple to implement but risky in microservices — if any downstream service is compromised, an attacker gains the ability to forge tokens for the entire system.

RS256 uses asymmetric keys: the auth service holds the private key and signs tokens; all other services hold only the public key and can verify but not sign. A compromised downstream service cannot forge new tokens. The public key is often exposed at a well-known URL (JWKS endpoint) so services can fetch and rotate it automatically.

Use HS256 for single-service applications or trusted internal systems. Use RS256 for microservices or any system where multiple independent services need to verify tokens.

</details>

<br>

**Q8: Walk through the OAuth2 Authorization Code flow step by step.**

<details>
<summary>💡 Show Answer</summary>

(1) User clicks "Login with Google" on your app. (2) Your app redirects the user to Google's auth server with your `client_id`, `redirect_uri`, requested `scope`, and a random `state` value to prevent CSRF. (3) User authenticates with Google and approves the requested permissions. (4) Google redirects the user back to your `redirect_uri` with a short-lived `auth_code` and the `state` value. (5) Your backend server exchanges the `auth_code` for an `access_token` and `refresh_token` by calling Google's token endpoint directly (server-to-server) — the `client_secret` is never exposed to the browser. (6) Your server stores the tokens and creates a session for the user.

Key point: the auth code exchange happens server-to-server, never in the browser. This is what keeps the `client_secret` secret. PKCE extends this flow for mobile and single-page apps that can't store a `client_secret`.

</details>

<br>

**Q9: What are the four rate limiting algorithms and when do you choose each?**

<details>
<summary>💡 Show Answer</summary>

Token bucket: fills at a fixed rate up to a max capacity. Allows bursts (using accumulated tokens). Best for real users who occasionally burst — they can make 10 quick requests if they've been idle, then are throttled. Most public APIs use this.

Leaky bucket: requests enter a queue and are processed at a fixed rate regardless of arrival pattern. Smooths traffic completely — no bursts allowed. Best for protecting downstream services that need consistent input.

Fixed window: counts requests in a fixed time window (e.g., 1000/minute). Simple to implement but allows a burst at the window boundary — 1000 requests at 12:59:59 and another 1000 at 13:00:00.

Sliding window: more accurate — counts requests in a rolling window relative to now. Prevents the boundary burst. More expensive to implement (needs timestamps per request in Redis). Best for strict enforcement.

</details>

<br>

**Q10: How do you store API keys securely on the server side?**

<details>
<summary>💡 Show Answer</summary>

Never store raw API keys in the database. Store a one-way hash (SHA-256) of the key, similar to how passwords are handled. When the user generates a key, you display the raw key exactly once — if they lose it, they must regenerate.

On each API request, hash the provided key and compare against the stored hash. Use `secrets.compare_digest()` for the comparison (not `==`) to prevent timing attacks — `compare_digest` takes constant time regardless of where strings differ, which prevents attackers from measuring response time to guess keys character by character.

Additionally: prefix keys with a type identifier (`sk-` for secret, `pk-` for public) so leaked keys are instantly identifiable in code and logs. Stripe uses this pattern.

</details>

<br>

---

# 🔹 Advanced Level Questions (5+ Years)

**Q11: How do you implement JWT token revocation when JWTs are stateless by design?**

<details>
<summary>💡 Show Answer</summary>

JWTs are stateless — the server doesn't store them, so there's nothing to revoke. The standard workarounds:

Short expiry: access tokens expire in 15 minutes. You can't revoke them, but the damage window is small. Pair with refresh token revocation.

Refresh token blocklist: store issued refresh tokens in Redis or a DB. On logout or suspicious activity, add the refresh token's `jti` (JWT ID claim) to a blocklist. The access token still works until it expires, but no new access tokens can be minted. The blocklist only needs to hold entries until the refresh token's natural expiry.

Token versioning: store a `token_version` on the user record. Include the version in the JWT. On every validation, compare the JWT's version to the stored version. Incrementing the stored version instantly invalidates all existing tokens for that user. Requires one DB lookup per request — not stateless anymore, but acceptable for security-critical operations.

</details>

<br>

**Q12: Explain the CORS preflight mechanism and what server configuration it requires.**

<details>
<summary>💡 Show Answer</summary>

A preflight is an OPTIONS request the browser sends automatically before a "non-simple" cross-origin request. Non-simple means: method is PUT/DELETE/PATCH, or the request has custom headers (including `Authorization`). The browser won't send the actual request until the preflight succeeds.

The server must respond to OPTIONS with: `Access-Control-Allow-Origin` (the requesting origin), `Access-Control-Allow-Methods` (allowed methods), `Access-Control-Allow-Headers` (allowed request headers including `Authorization`), and optionally `Access-Control-Max-Age` (how long to cache the preflight — 86400 seconds avoids a preflight on every request).

Common production mistake: forgetting to add new custom headers to `Access-Control-Allow-Headers` after they're added to the API. This silently breaks the API for browser clients while server-to-server calls (which skip CORS) continue working — hard to debug.

</details>

<br>

**Q13: How would you design authentication for a microservices system where 20+ services need to verify identity?**

<details>
<summary>💡 Show Answer</summary>

Use a centralized auth service that issues JWTs signed with RS256. Each service fetches the auth service's public key (via a JWKS endpoint) at startup and caches it. Every incoming request is verified locally using the cached public key — no network call to the auth service per request. Key rotation is handled by the JWKS endpoint; services refresh the key on a schedule or when verification fails.

The JWT payload includes enough context for authorization (user ID, roles, org ID, plan tier) so downstream services don't need to call a user service for every request.

For service-to-service calls (no user context), use OAuth2 Client Credentials flow — each service has its own `client_id` and `client_secret` and fetches a short-lived access token from the auth service. This provides machine identity without sharing secrets.

The anti-pattern to avoid: having each service independently manage its own user auth or share a single master API key — both are security liabilities at scale.

</details>

<br>

**Q14: What is the OAuth2 Client Credentials flow and when does it replace Authorization Code?**

<details>
<summary>💡 Show Answer</summary>

Client Credentials is for machine-to-machine authentication where there is no human user involved. A backend service authenticates as itself, not on behalf of a user.

Flow: the service sends its `client_id` and `client_secret` to the token endpoint with `grant_type=client_credentials`. The auth server returns a short-lived access token. The service uses this token for all API calls until it expires, then fetches a new one.

Use Authorization Code when a user is delegating access to your app — the consent and identity belong to the human. Use Client Credentials for scheduled jobs, background workers, internal service-to-service communication, and webhook processing where there is no user in the loop.

Production pattern: cache the token and only fetch a new one when the current one is within 60 seconds of expiry. Token requests have latency and are rate-limited — don't fetch a new token on every request.

</details>

<br>
