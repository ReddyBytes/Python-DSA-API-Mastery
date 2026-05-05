# 🎯 What is an API — Interview Preparation

> This file prepares you to discuss APIs like a working engineer.
> Not just definitions — but real-world usage, trade-offs, and production scenarios.

---

# 🔹 Basic Level Questions (0–2 Years)

**Q1: What is an API and why does it exist?**

<details>
<summary>💡 Show Answer</summary>

An API (Application Programming Interface) is a defined contract that lets two pieces of software communicate. It exists because systems need to share data without exposing their internals. A weather app doesn't build its own satellite — it calls a weather API. APIs enforce a stable interface so the server can change its database or language without breaking every client.

</details>

<br>

**Q2: What is the difference between GET, POST, PUT, PATCH, and DELETE?**

<details>
<summary>💡 Show Answer</summary>

GET reads data — no body, no side effects. POST creates a new resource. PUT fully replaces a resource (you send all fields). PATCH partially updates a resource (you send only the fields changing). DELETE removes a resource.

The key distinctions that matter in interviews: GET and DELETE have no body. PUT is idempotent (N calls = same result as 1 call). POST is not idempotent — calling it twice creates two records.

</details>

<br>

**Q3: What does a 401 status code mean versus a 403?**

<details>
<summary>💡 Show Answer</summary>

401 means the server doesn't know who you are — you're not authenticated. The fix is to provide valid credentials (login again, refresh your token).

403 means the server knows exactly who you are but you're not allowed to do what you asked. The fix is a permissions change, not a re-login. A common mistake is returning 401 when you should return 403, which confuses clients into retrying auth when it won't help.

</details>

<br>

**Q4: What are the Content-Type and Accept headers used for?**

<details>
<summary>💡 Show Answer</summary>

Content-Type tells the server what format the request body is in (e.g., `application/json`). Accept tells the server what format the client wants in the response. They work together for content negotiation. If you send JSON but forget `Content-Type: application/json`, many servers will reject the request or misparse the body. In practice, most REST APIs only support JSON, so both are typically `application/json`.

</details>

<br>

**Q5: What is the difference between a REST API and a GraphQL API?**

<details>
<summary>💡 Show Answer</summary>

REST is resource-based — each resource has its own URL and you use HTTP methods to interact with it. GraphQL is query-based — there is one endpoint and the client specifies exactly what fields it wants. REST can result in over-fetching (getting more fields than needed) or under-fetching (needing multiple calls). GraphQL solves both but adds complexity: schema management, N+1 query problems, and harder caching. For simple public APIs, REST is the default. GraphQL shines for complex UIs that need flexible, aggregated data.

</details>

<br>

---

# 🔹 Intermediate Level Questions (2–5 Years)

**Q6: What does idempotent mean and which HTTP methods are idempotent?**

<details>
<summary>💡 Show Answer</summary>

Idempotent means calling the operation N times produces the same result as calling it once. GET, PUT, and DELETE are idempotent. POST is not — two POST calls to `/payments` charge the user twice.

This matters in distributed systems because network failures cause retries. A client that retries a PUT is safe. A client that retries a POST can create duplicates. To make POST safe to retry, use idempotency keys (the client sends a UUID with the request and the server deduplicates on it — used by Stripe for payments).

</details>

<br>

**Q7: What is the difference between `204 No Content` and `200 OK` and when do you use each?**

<details>
<summary>💡 Show Answer</summary>

200 means success and there is a body in the response. 204 means success but there is nothing to return. Use 204 for DELETE operations and for actions where the result is just confirmation. Use 200 for GET, PATCH, and PUT where you return the resource. Returning 204 on a DELETE is preferred because forcing clients to parse an empty body is wasteful. Never return 200 with an empty body — use 204 instead.

</details>

<br>

**Q8: Walk me through the anatomy of an HTTP request and response.**

<details>
<summary>💡 Show Answer</summary>

A request has: a request line (method, path, HTTP version), headers (key-value metadata like Authorization, Content-Type, Accept), and optionally a body (for POST/PUT/PATCH).

A response has: a status line (HTTP version + status code + reason phrase), headers (Content-Type, Cache-Control, ETag, Location, etc.), and optionally a body.

The most commonly forgotten production detail: always include `Content-Type` in responses (even error responses), and always include the `Location` header on 201 Created so clients know where the new resource lives.

</details>

<br>

**Q9: What is the purpose of the ETag and Cache-Control headers?**

<details>
<summary>💡 Show Answer</summary>

Cache-Control tells caches (browsers, CDNs) how long a response is valid. `public, max-age=3600` allows anyone to cache for 1 hour. `private` restricts caching to the browser only. `no-store` prevents caching entirely — use this for auth tokens and financial data.

ETag is a fingerprint (usually a hash) of the response content. Clients send back the ETag on the next request as `If-None-Match`. If content hasn't changed, the server returns 304 Not Modified with no body — saving bandwidth. This is critical for high-traffic read APIs.

</details>

<br>

**Q10: How do you choose between REST, GraphQL, and gRPC for a new service?**

<details>
<summary>💡 Show Answer</summary>

Default to REST for public-facing APIs — broad tooling support, easy to cache, simple to document with OpenAPI.

Use GraphQL when you have a complex frontend with many different views that need different shapes of data, and you want to avoid creating multiple specialized endpoints.

Use gRPC for internal backend-to-backend communication where performance matters — it uses Protocol Buffers (binary, ~60–80% smaller than JSON) and requires both sides to share a schema. It's not practical for browser clients without a proxy layer. Google and Netflix use it internally at large scale.

</details>

<br>

---

# 🔹 Advanced Level Questions (5+ Years)

**Q11: How would you design rate limiting for a public API, and what headers should you expose?**

<details>
<summary>💡 Show Answer</summary>

Rate limiting algorithms: token bucket allows bursts (real users have natural bursts), leaky bucket smooths traffic (better for protecting downstream services), sliding window is the most accurate but expensive to compute.

At the infrastructure level, implement rate limiting in a reverse proxy (nginx, Kong, API Gateway) or in a shared store like Redis, not in application code — otherwise each pod enforces limits independently.

Expose these headers on every response: `X-RateLimit-Limit` (total requests allowed per window), `X-RateLimit-Remaining`, `X-RateLimit-Reset` (Unix timestamp when window resets). On 429 Too Many Requests, include `Retry-After` so clients know when to retry. Not exposing these headers forces clients to guess, which leads to hammering the API.

</details>

<br>

**Q12: A client is intermittently getting 502 errors from your API behind a load balancer. Walk me through how you'd diagnose it.**

<details>
<summary>💡 Show Answer</summary>

502 Bad Gateway means the load balancer received an invalid response from the upstream server — the app crashed, returned garbage, or closed the connection.

Diagnosis steps: check load balancer access logs to see which backend instances are generating the 502s. Check application logs on those instances for unhandled exceptions or OOM kills. Check if the 502s correlate with deployments (rolling restart hitting in-flight requests). Check if any backend pods are being terminated while handling requests — you need graceful shutdown with connection draining.

For Kubernetes: ensure `terminationGracePeriodSeconds` is long enough and your app handles SIGTERM by finishing in-flight requests before exiting.

</details>

<br>

**Q13: What is the `alg:none` vulnerability in JWTs and how do you prevent it?**

<details>
<summary>💡 Show Answer</summary>

The `alg:none` attack exploits JWT libraries that accept a token claiming no signature algorithm (`"alg": "none"` in the header). An attacker constructs a fake JWT with any payload and sets `alg` to `none`. Vulnerable libraries skip signature verification and accept the token.

Prevention: always explicitly specify allowed algorithms when validating a JWT — e.g., `algorithms=["HS256"]` in PyJWT. Never pass the algorithm from the token header itself into the decode call. Use libraries that default to rejecting `none` algorithm. Additionally: require `exp`, `iss`, and `sub` claims; reject tokens without them.

</details>

<br>

**Q14: How does HTTP/2 differ from HTTP/1.1 and when does it matter for API design?**

<details>
<summary>💡 Show Answer</summary>

HTTP/1.1 opens one request per TCP connection (pipelining exists but is rarely used). Browsers work around this by opening 6–8 parallel connections per domain. This means API clients making many small calls suffer from head-of-line blocking and connection overhead.

HTTP/2 multiplexes multiple requests over a single TCP connection, uses header compression (HPACK), and supports server push. This matters for browser-based apps making many API calls — fewer TCP handshakes, lower latency.

For backend-to-backend REST APIs, the impact is lower since connections are typically reused. gRPC runs on HTTP/2 natively and benefits from multiplexing for streaming. Most cloud load balancers and CDNs support HTTP/2 transparently; the API code doesn't change.

</details>

<br>

**Q15: What are the trade-offs of putting API versioning in the URL path versus a header?**

<details>
<summary>💡 Show Answer</summary>

URL versioning (`/v1/users`) is visible, easy to test with curl or a browser, and cache-friendly — CDNs can cache `/v1/users` and `/v2/users` independently. The purist argument against it is that the URL should identify a resource, not a version of an API.

Header versioning (`API-Version: 2024-01-01` like Stripe uses) keeps URLs clean and allows fine-grained per-date versioning. The downsides: it's invisible to developers browsing URLs, harder to test without tooling, and requires a `Vary: API-Version` header for caches to work correctly.

In practice, URL versioning is the right default — it's simpler to document, test, and route. Header versioning is appropriate for mature APIs with many sophisticated clients (Stripe, AWS) where URL stability matters more than convenience.

</details>

<br>
