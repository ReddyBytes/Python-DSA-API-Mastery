# 🎯 API Gateway — Interview Preparation

> This file prepares you to discuss API gateways like a working engineer.
> Not just definitions — but real-world usage, trade-offs, and production scenarios.

---

# 🔹 Basic Level Questions (0–2 Years)

**Q1: What is an API gateway and what problem does it solve?**

<details>
<summary>💡 Show Answer</summary>

An API gateway is a single entry point that sits in front of multiple backend services. Without it, each microservice would need to implement its own authentication, rate limiting, TLS, logging, and routing — duplicating that logic across every service. The gateway handles all of that centrally so services can focus on business logic. Clients talk to one hostname on port 443; the gateway routes their requests to the right service, validates their token, enforces rate limits, and terminates TLS. This is sometimes called the "doorman" pattern.

</details>

<br>

**Q2: What is TLS termination and why is it done at the gateway rather than at each service?**

<details>
<summary>💡 Show Answer</summary>

TLS termination means the gateway decrypts HTTPS traffic from clients and then forwards plain HTTP to backend services on the internal network. This is done at the gateway because: managing TLS certificates across dozens of services is operationally expensive, internal service communication over a private network (e.g., a VPC or Kubernetes pod network) can be trusted at the infrastructure level without per-service certs, and TLS termination allows the gateway to inspect request content for routing decisions. If compliance requires encryption in transit all the way to the service (e.g., PCI or HIPAA), you use mTLS end-to-end instead.

</details>

<br>

**Q3: What HTTP status code should an API return when a rate limit is exceeded, and what header must accompany it?**

<details>
<summary>💡 Show Answer</summary>

Return `429 Too Many Requests`. You must include a `Retry-After` header indicating how many seconds the client should wait before retrying. Most gateways also include `RateLimit-Limit` (the quota), `RateLimit-Remaining` (how many requests are left), and `RateLimit-Reset` (Unix timestamp of when the window resets). Without `Retry-After`, well-behaved clients have no guidance on when to retry and may immediately hammer the API again, making the situation worse.

</details>

<br>

**Q4: What is the difference between an API gateway and a reverse proxy like Nginx?**

<details>
<summary>💡 Show Answer</summary>

Both sit in front of backend services and route traffic, but an API gateway is purpose-built with API-specific features out of the box: JWT validation, API key management, rate limiting per consumer, a plugin system, developer portals, and analytics. Nginx is a general-purpose HTTP server and reverse proxy — it can do rate limiting and routing via configuration, but you write that logic yourself. Kong is built on top of Nginx and adds the API gateway layer. Use Nginx when you need simple reverse proxying or load balancing. Use a dedicated gateway (Kong, AWS API Gateway) when you need centralized auth, rate limiting policies, and extensibility without custom scripting.

</details>

<br>

**Q5: What is the Backend for Frontend (BFF) pattern?**

<details>
<summary>💡 Show Answer</summary>

BFF is a variant of the API gateway pattern where instead of one shared gateway, you create a dedicated gateway per client type: one for mobile, one for the web app, one for the admin dashboard. Each BFF is tailored to what that client needs — the mobile BFF returns compact payloads with fewer fields, the web BFF returns richer data, the admin BFF exposes bulk operations. The BFF aggregates calls to multiple internal microservices so the client makes one request instead of many. You use BFF when different clients have meaningfully different data needs. Avoid it for a single-client API or a small team — it adds a service to maintain per client type.

</details>

<br>

---

# 🔹 Intermediate Level Questions (2–5 Years)

**Q6: How does Kong implement rate limiting, and what is the difference between the `local` and `redis` policy options?**

<details>
<summary>💡 Show Answer</summary>

Kong's rate-limiting plugin tracks request counts within a time window (minute, hour, day) per consumer or per IP. The `local` policy stores counts in each Kong node's memory — fast but inaccurate when you have multiple Kong nodes, since a client can exceed the limit by hitting different nodes. The `redis` policy stores counts in a shared Redis instance — accurate across all Kong nodes and the correct choice for production clusters. The trade-off is that `redis` adds network latency on every request (typically sub-millisecond for a local Redis), and Redis becomes a dependency whose failure affects rate limiting. Configure sliding window rate limiting for more accurate enforcement than fixed windows.

</details>

<br>

**Q7: Walk through what happens when a client sends a JWT-authenticated request through an API gateway.**

<details>
<summary>💡 Show Answer</summary>

1. Client sends a request with `Authorization: Bearer <token>` header.
2. The gateway intercepts the request before routing.
3. The gateway's JWT plugin extracts the token and validates the signature using the public key (retrieved from the auth server's JWKS endpoint or pre-configured).
4. The gateway checks the token's expiry (`exp` claim), issuer (`iss`), and audience (`aud`).
5. If validation fails, the gateway returns 401 and the request never reaches the backend.
6. If valid, the gateway optionally strips the Authorization header (to avoid forwarding credentials downstream) and adds consumer identity headers like `X-Consumer-ID` for the backend.
7. The backend trusts that the gateway has already validated the token and uses the forwarded identity without re-validating.

</details>

<br>

**Q8: What is a circuit breaker at the gateway level and when does it activate?**

<details>
<summary>💡 Show Answer</summary>

A circuit breaker monitors the error rate or latency of requests to a backend service. When the failure threshold is exceeded (e.g., 50% of requests fail in a 10-second window), the circuit "opens" and the gateway stops routing requests to that backend entirely, immediately returning 503 to clients. After a configured timeout, the circuit transitions to "half-open" and allows a small probe of requests through. If those succeed, the circuit closes and normal routing resumes. Without a circuit breaker, a slow or failing service causes client requests to pile up waiting for timeouts, exhausting connection pools and cascading the failure to other services. The circuit breaker makes failure fast and contained rather than slow and contagious.

</details>

<br>

**Q9: How would you configure Kong to forward a request to different service versions based on a request header?**

<details>
<summary>💡 Show Answer</summary>

Use Kong's request-transformer or route-by-header approach. Define two separate services in Kong's declarative config — one pointing to `http://user-service-v1:8080` and one to `http://user-service-v2:8080`. Then create routes for each service with a `headers` match condition: `X-API-Version: v2` routes to the v2 service, and the default route (no header match) goes to v1. This is the pattern for canary deployments and A/B testing at the gateway layer. The application services themselves do not need to know about versioning routing — the gateway handles it transparently.

</details>

<br>

**Q10: What is the difference between an API gateway and a service mesh (like Istio)?**

<details>
<summary>💡 Show Answer</summary>

An API gateway handles north-south traffic — requests coming in from external clients to your services. A service mesh handles east-west traffic — requests between services inside your cluster. Practically: the gateway is the public entry point handling auth, rate limiting, and routing for external consumers. The service mesh handles mTLS between services, retries, load balancing, and observability for internal service calls. They solve different problems and are commonly used together: gateway at the edge for external traffic, service mesh for internal service communication. Using a service mesh as an API gateway substitute adds significant complexity and is generally not recommended unless you already run a mesh and have simple external auth needs.

</details>

<br>

---

# 🔹 Advanced Level Questions (5+ Years)

**Q11: How would you design rate limiting that is fair under a sudden burst of legitimate traffic vs. an attacker sending a flood?**

<details>
<summary>💡 Show Answer</summary>

Use a token bucket or leaky bucket algorithm rather than a fixed window counter. Fixed windows are vulnerable to burst attacks at window boundaries — a client can make 2x the quota by sending all requests just before and just after the window resets. Token buckets allow legitimate burst traffic up to the bucket capacity (e.g., 200 requests instant burst) while enforcing a sustained rate (e.g., 100 requests per minute). Pair this with: rate limiting at multiple granularities (per-IP for unauthenticated endpoints, per-API-key for authenticated), a bot detection layer upstream (WAF, Cloudflare), and progressive penalties — short backoff for first violation, exponential increase for repeated violations. Kong's `burst_refresh_rate` config option controls the token bucket refill rate.

</details>

<br>

**Q12: What are the latency costs of an API gateway and how do you minimize them?**

<details>
<summary>💡 Show Answer</summary>

AWS API Gateway adds approximately 10ms per request (the cost of Lambda authorizers, DynamoDB lookups for usage plans). Kong adds 1–3ms for plugin chains in typical deployments. Nginx as a proxy adds under 1ms. Strategies to minimize gateway latency: cache JWT public keys in memory (avoid JWKS fetch per request), use token introspection caching with a short TTL rather than live database lookups, configure plugin ordering carefully (fail-fast auth first, expensive plugins last), use connection pooling and keepalive for upstream connections, and run the gateway as close to the services as possible (same VPC, same availability zone). For latency-critical internal paths, consider bypassing the gateway entirely with direct service-to-service calls authenticated via mTLS.

</details>

<br>

**Q13: How would you handle a zero-downtime migration from one API version to another using a gateway?**

<details>
<summary>💡 Show Answer</summary>

The standard approach is weighted traffic splitting at the gateway, executed in stages. Deploy the v2 service alongside v1 — both live. Configure the gateway to route 0% to v2 initially. Run smoke tests against v2 by passing a specific header that the gateway routes to v2. Incrementally shift traffic: 5% → 10% → 25% → 50% → 100%, with monitoring at each step for error rate and latency regressions. The gateway handles this with weighted upstream configuration (Kong: `weight` on upstream targets; AWS API Gateway: stage variables and canary deployments). Maintain the ability to instantly shift back to 0% v2 if metrics degrade. Once v2 is at 100% and stable for a defined period, deprecate v1 routes with a sunset header and remove after the deprecation window.

</details>

<br>

**Q14: What are the security risks of centralizing authentication at the gateway, and how do you mitigate them?**

<details>
<summary>💡 Show Answer</summary>

The primary risk is that a misconfigured gateway route bypasses authentication — a backend service is exposed to unauthenticated traffic if the gateway rule is wrong. Mitigation: backend services should not implicitly trust all traffic just because it arrives on the internal network. Use defense in depth: services verify the gateway-forwarded identity header (e.g., `X-Consumer-ID`) against a known set of values, or better, implement service-to-service mTLS so only authenticated service identities can connect. Second risk: the gateway is a single point of failure for auth — if it goes down or the JWKS endpoint is unreachable, all authenticated requests fail. Mitigation: cache JWKS keys with a reasonable TTL (5–60 minutes) so a brief auth server outage does not immediately impact all requests.

</details>

<br>
