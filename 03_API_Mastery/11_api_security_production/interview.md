# 🎯 API Security & Production Hardening — Interview Preparation

> This file prepares you to discuss API security like a working engineer.
> Not just definitions — but real-world usage, trade-offs, and production scenarios.

---

# 🔹 Basic Level Questions (0–2 Years)

**Q1: What is Broken Object Level Authorization (BOLA) and how do you prevent it?**

<details>
<summary>💡 Show Answer</summary>

BOLA (OWASP API1) is when an API exposes object identifiers in URLs or request bodies but does not verify that the authenticated user owns or has access to that specific object. For example: GET /orders/4892 returns an order even if order 4892 belongs to a different user. An attacker simply increments the ID to access any user's data.

Prevention: on every request that touches a specific object, verify ownership before returning data. In SQL: SELECT * FROM orders WHERE id = ? AND user_id = ? — the AND user_id = ? clause is the guard. Never query by ID alone for user-scoped resources. In code, check ownership in the service layer, not just the route handler, so the check is not accidentally bypassed by internal callers. BOLA is the number one API vulnerability in the OWASP Top 10 because it is easy to miss in code review — the endpoint looks correct but the ownership check is absent.

</details>

<br>

**Q2: Why should JWT access tokens be short-lived (15 minutes) and how does that work with refresh tokens?**

<details>
<summary>💡 Show Answer</summary>

JWTs are stateless — once issued, they cannot be invalidated server-side without a blocklist. If an access token is stolen (from a log, an XSS attack, or a compromised client), the attacker can use it until it expires. A 15-minute expiry limits the damage window.

Refresh tokens solve the usability problem: they have a longer lifetime (7–30 days) and are stored securely server-side. When the access token expires, the client sends the refresh token to a dedicated /token/refresh endpoint, which validates it against the database, issues a new access token, and rotates the refresh token (issues a new one and invalidates the old). If a refresh token is stolen and replayed after it has been rotated, the server detects the reuse and can revoke the entire session. The rotation pattern makes token theft detectable — if you see a refresh token used twice, one of those uses was an attacker.

</details>

<br>

**Q3: What is rate limiting and what HTTP headers should accompany a 429 response?**

<details>
<summary>💡 Show Answer</summary>

Rate limiting caps the number of requests a client can make in a time window to prevent abuse, denial of service, and resource exhaustion. It is applied per IP address, per API key, or per authenticated user depending on the use case.

On every response you should return informational headers: X-RateLimit-Limit (max requests per window), X-RateLimit-Remaining (requests left in the current window), and X-RateLimit-Reset (Unix timestamp when the window resets). On a 429 Too Many Requests response, add Retry-After with the number of seconds the client must wait before retrying. Without Retry-After, well-behaved clients have no signal and often retry immediately, creating a thundering herd that makes the problem worse.

</details>

<br>

**Q4: What is the danger of using allow_origins=["*"] in CORS configuration on an authenticated API?**

<details>
<summary>💡 Show Answer</summary>

A wildcard CORS origin (allow_origins=["*"]) tells the browser that any website can make cross-origin requests to your API. If your API uses cookies for authentication, this creates a cross-site request forgery (CSRF) risk — a malicious website can make requests that include the victim's cookies.

Browsers actually block allow_origins=["*"] combined with allow_credentials=True, but the real risk remains: even without credentials, a wildcard origin on an API key-authenticated endpoint allows any site to make requests on behalf of users who have granted your API access. The safe configuration is an explicit allowlist of trusted origins. In production this is typically your web app domain and your admin portal domain — nothing else. Review the list quarterly as domains change.

</details>

<br>

**Q5: What is the difference between SQL injection and how do parameterized queries prevent it?**

<details>
<summary>💡 Show Answer</summary>

SQL injection happens when user-supplied input is concatenated directly into a SQL string. An attacker can close the intended query and append arbitrary SQL — for example, injecting ' OR '1'='1 to bypass a WHERE clause, or ; DROP TABLE users -- to destroy data.

Parameterized queries (also called prepared statements) separate the SQL structure from the data. The query is compiled with placeholders (? or %s depending on the driver), and the data is passed separately. The database driver handles escaping automatically — the input is treated as a literal value, never as SQL syntax. The fix is always: cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,)) — never string formatting or f-strings to construct SQL. ORMs like SQLAlchemy use parameterized queries internally, but raw SQL in an ORM (session.execute(text(f"..."))) is vulnerable if you interpolate user input.

</details>

<br>

---

# 🔹 Intermediate Level Questions (2–5 Years)

**Q6: Walk through the JWT security rules — what are the critical don'ts?**

<details>
<summary>💡 Show Answer</summary>

The most dangerous mistake is accepting the algorithm from the token header itself (alg field). An attacker can change alg to "none" to bypass signature verification, or change it from RS256 to HS256 to sign a token with the public key (which is not secret). Always hardcode the expected algorithm in your verification call: jwt.decode(token, secret, algorithms=["HS256"]).

Other critical rules: always verify the exp claim — never skip expiry validation even in development or "trusted" environments. Never store sensitive data (passwords, payment info, PII) in the JWT payload — it is base64-encoded, not encrypted, and is readable by anyone who intercepts it. Use symmetric secrets of at least 32 bytes — short secrets are brute-forceable. Add a type claim ("access" or "refresh") and reject tokens of the wrong type to prevent refresh tokens from being used as access tokens.

</details>

<br>

**Q7: What is Server-Side Request Forgery (SSRF) in an API context and how do you prevent it?**

<details>
<summary>💡 Show Answer</summary>

SSRF happens when an API accepts a URL from user input and fetches that URL server-side. An attacker can provide an internal URL — http://169.254.169.254/latest/meta-data/ (AWS instance metadata), http://localhost:6379 (Redis), or http://internal-service.corp — causing your API server to make requests to services that should not be accessible from the internet.

Prevention has two layers. First, validate and allowlist URLs: only permit specific domains or URL patterns that your feature legitimately needs. Block all private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16), loopback addresses (127.0.0.0/8), and link-local addresses (169.254.0.0/16). Second, resolve the hostname before connecting and re-check the resolved IP against the blocklist — DNS rebinding attacks resolve a trusted hostname to a private IP after the initial validation check. In cloud environments, consider blocking the instance metadata service endpoint explicitly.

</details>

<br>

**Q8: How does OAuth2 + OIDC work and when should you use it instead of API keys?**

<details>
<summary>💡 Show Answer</summary>

OAuth2 is an authorization framework where a resource owner (user) delegates limited access to a third party (client application) without sharing credentials. OIDC (OpenID Connect) builds on OAuth2 to add authentication — it issues an ID token (a JWT) identifying the user in addition to the access token.

The flow: the client redirects the user to the authorization server (Google, Auth0, your own IdP). The user authenticates and grants consent. The auth server redirects back with an authorization code. The client exchanges the code for tokens at the token endpoint. The access token is then used to call your API.

Use OAuth2 + OIDC when: third-party applications need access on behalf of your users, you want single sign-on across multiple services, or you need fine-grained scope-based permissions. Use API keys when: it is server-to-server communication with no user context, the client is fully trusted, and the simplicity of a single credential outweighs the limitations. API keys are inappropriate for end-user auth because they appear in client code and logs and cannot be scoped to a specific user.

</details>

<br>

**Q9: What are security headers and which ones matter most for an API?**

<details>
<summary>💡 Show Answer</summary>

Security headers instruct browsers and intermediaries how to treat responses from your service. For APIs (as opposed to web pages) the most important are:

Strict-Transport-Security (HSTS): forces HTTPS for all future requests from this browser for the specified max-age. Prevents protocol downgrade attacks. Include includeSubDomains if all subdomains support HTTPS.

X-Content-Type-Options: nosniff — prevents browsers from MIME-sniffing the response type, stopping attacks that serve malicious scripts as innocuous content types.

X-Frame-Options: DENY — prevents your API responses from being embedded in iframes, blocking clickjacking.

For browser-facing APIs: Content-Security-Policy restricts what resources the browser can load. Referrer-Policy: no-referrer prevents URLs (potentially containing query parameters with sensitive data) from being sent in the Referer header to third parties.

Implement these in a single middleware that injects them on every response — do not rely on individual endpoint handlers to set them.

</details>

<br>

**Q10: What is the difference between authentication and authorization, and give an example of a system where they are separated?**

<details>
<summary>💡 Show Answer</summary>

Authentication answers "who are you?" — verifying identity through credentials (password, token, certificate). Authorization answers "what are you allowed to do?" — enforcing permissions based on the verified identity.

They are separate concerns and should be implemented in separate layers. In a FastAPI application: a get_current_user dependency handles authentication — it validates the JWT, decodes the user ID, and loads the user from the database. A require_role("admin") dependency handles authorization — it calls get_current_user first, then checks the user's role. Route handlers compose both: @app.delete("/admin/users/{id}", dependencies=[Depends(require_role("admin"))]).

A real example of separation: AWS IAM. Authentication is handled by signing requests with an access key (identity). Authorization is handled by IAM policies that specify which resources and actions the identity is allowed. A valid access key (authenticated) does not automatically mean permission to call every AWS API — the policy (authorization) is evaluated separately.

</details>

<br>

---

# 🔹 Advanced Level Questions (5+ Years)

**Q11: How would you implement and rotate API keys securely in a production system?**

<details>
<summary>💡 Show Answer</summary>

API keys must never be stored in plaintext — store a bcrypt or Argon2 hash of the key, exactly like a password. When a key is issued: generate a cryptographically random value (secrets.token_urlsafe(32)), display it once to the user (they must copy it), then store only the hash. On each request, hash the provided key and compare to the stored hash.

Rotation: give users the ability to generate a new key without immediately invalidating the old one. Run both keys in parallel for a transition window — typically 30 days for internal teams, longer for external partners. After the window, or when the user confirms migration, invalidate the old key. Automate rotation reminders: keys older than 90 days should generate a warning in the developer portal.

For zero-downtime rotation in automated systems: the rotation process generates the new key and updates the secret store (AWS Secrets Manager, Vault), then the consuming system picks up the new key at its next secret rotation poll without any deployment. Validate the new key works before revoking the old one — a rotation that breaks the integration is worse than a stale key.

</details>

<br>

**Q12: How do you design rate limiting that distinguishes between legitimate burst traffic and abuse?**

<details>
<summary>💡 Show Answer</summary>

A single fixed rate limit (100 requests per minute) treats all traffic the same. A token bucket algorithm is more nuanced: each client has a bucket with a maximum capacity and tokens refill at a steady rate. A burst of requests drains the bucket quickly, but a steady stream at the refill rate is always permitted. This allows legitimate clients to burst briefly (uploading a batch, retrying after a brief failure) without triggering the limit, while sustained high-rate abuse eventually empties the bucket.

Layer rate limits for different threat models: a per-IP limit catches bots using a single IP, a per-API-key limit catches legitimate clients that are consuming too many resources, and a per-endpoint limit catches scraping of a specific expensive endpoint. For auth endpoints use a separate stricter limit (5 attempts per minute per IP) with exponential backoff enforcement — leaked credentials are tried at high rate by automated scanners.

Store counters in Redis with atomic INCR and EXPIREAT for thread safety across workers. Use the sliding window log algorithm if exact accuracy is required, or the fixed window counter if performance under high load is the priority. Behavioral limits (OWASP API6) require pattern detection — flagging accounts that create hundreds of new accounts from the same IP range — which is outside simple rate limiting and requires a fraud detection layer.

</details>

<br>

**Q13: Explain mTLS and when it is appropriate for service-to-service communication.**

<details>
<summary>💡 Show Answer</summary>

Standard TLS (HTTPS) authenticates the server to the client — the client verifies the server's certificate. Mutual TLS (mTLS) adds the reverse: the server also verifies the client's certificate. Both sides present and validate certificates, establishing cryptographic proof of identity in both directions.

This is appropriate for internal microservice communication in a zero-trust network model. Rather than sharing API keys between services (which can be leaked or misconfigured), each service has a certificate issued by an internal certificate authority. The service mesh (Istio, Linkerd) or a sidecar proxy handles certificate management and rotation transparently, without changes to application code.

Avoid mTLS for public-facing APIs — client certificate management is complex for external developers, and the operational burden (certificate issuance, renewal, rotation) is high. The sweet spot is internal east-west traffic between services you own. The trade-off is the PKI infrastructure: you need an internal CA, certificate rotation automation, and a way to handle certificate revocation. Service meshes solve most of this, but they add their own operational complexity.

</details>

<br>

**Q14: How would you respond to a security incident where a production JWT secret key was exposed?**

<details>
<summary>💡 Show Answer</summary>

The immediate action is to rotate the secret key. Generate a new key, deploy it to all API servers simultaneously (or use a brief overlap window), and invalidate all existing tokens. Every currently authenticated user will be logged out and must re-authenticate — this is unavoidable and expected. Notify users with an explanation that does not reveal the nature of the incident.

Simultaneously: investigate how the secret was exposed (committed to git, logged, visible in error messages, leaked through a dependency). Check access logs for the time period after the exposure to identify any tokens signed with the old key that made requests — these may indicate active exploitation. If sensitive user data was accessed, you may have breach notification obligations depending on jurisdiction.

Post-incident: store secrets in a secrets manager (AWS Secrets Manager, HashiCorp Vault) with automatic rotation rather than in environment variables or config files. Scan the git history and all log archives for the exposed key. Add a pre-commit hook that detects secrets before they reach the repository. Review whether asymmetric signing (RS256) would reduce the blast radius of a future exposure — the private key signs tokens but the public key verifies them; exposing the public key to verify tokens does not enable an attacker to forge tokens.

</details>

<br>
