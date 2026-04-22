# Scenario-Based API Interview Questions

> Open-ended scenario questions for senior API design interviews. Each question tests your ability to reason through a real system under pressure — not recall facts.

---

## Learning Priority

**Must Learn** — these scenarios appear most often at senior/staff interviews:
Rate limiting tiers · 401 debugging · webhook guaranteed delivery · API versioning deprecation

**Should Learn** — strong signal questions for system design rounds:
Multi-tenant auth · file upload at scale · FastAPI timeout diagnosis · REST-to-microservice migration

**Good to Know** — comes up at principal/architect level:
Intermittent 200 with wrong data · real-time pagination

---

## How to Use This

For each scenario, the format is:
- **What they're testing** — the underlying competency
- **Strong answer outline** — the points that make an answer stand out
- **Follow-up probes** — what interviewers push on after your first answer

Give your answer conversationally. These are not recitation prompts — they are calibration conversations. The interviewer will follow up until you hit your edge. That is the goal.

---

## Scenario 1: Design a Rate-Limited Public API (10K req/day free, paid tiers)

**Scenario:** You are launching a public REST API. The free tier gets 10,000 requests per day. Paid tiers get 500K/day and 5M/day. Design the rate limiting system.

**What they're testing:** Distributed systems thinking, Redis fundamentals, quota vs rate limits distinction, graceful degradation.

**Strong answer outline:**

1. **Two-layer limiting:** daily quota (business rule) + per-minute burst (traffic shaping). Free tier at 10K/day does not mean 10K in the first minute.

2. **Storage:** Redis for atomic counters. Key structure: `quota:{api_key}:{date}` for daily quota, `rate:{api_key}:{minute}` for burst limiting. TTL auto-cleans old keys.

3. **Enforcement at the gateway** — not in the app server. The gateway (Kong, API Gateway, Nginx) intercepts before the request hits your service.

4. **Tier lookup:** On each request, look up the API key's tier to get the quota limit. Cache tier data (TTL 60s) to avoid a DB hit per request.

5. **Headers:** Always return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`. On 429: include `Retry-After`.

6. **Tier enforcement:** On quota exceeded — return 429 with a clear message explaining which quota was hit and when it resets. Link to upgrade page.

7. **Quota reset time:** Daily quota resets at midnight UTC (simple) or on a rolling 24-hour window (fairer but harder to explain to users).

8. **Concurrency edge case:** Two requests arrive simultaneously, both see "1 request remaining." Use Redis `INCR` + check (atomic) to prevent double-counting.

**Follow-up probes:**
- What happens if Redis goes down? (fail open vs fail closed — choose and defend)
- How do you handle a paid customer who exceeds their quota mid-month? (grace period, soft limits, hard limits)
- How would you alert a customer at 80% quota usage?
- How do you prevent one burst user from starving others? (token bucket vs sliding window)

---

## Scenario 2: Debug — API Returns 200 but Wrong Data Intermittently

**Scenario:** Customers report your API sometimes returns correct data and sometimes returns stale or wrong data — but always HTTP 200. It's not reproducible consistently. Walk through your diagnosis.

**What they're testing:** Systematic debugging under ambiguity, distributed system awareness, caching knowledge.

**Strong answer outline:**

1. **Define "wrong"** — stale data (old values) or incorrect data (different user's data)? These are different problems with different root causes.

2. **If stale data:**
   - Caching layer: is there a CDN, reverse proxy, or app-level cache? Check cache TTL and cache key construction. Are you caching per-user or per-route without a user-specific key?
   - Read replicas: is the query hitting a read replica that lags behind the primary? Check replication lag metrics.
   - Worker state: are multiple Gunicorn workers holding in-memory caches that get stale independently?

3. **If wrong user's data:**
   - Cache key bug: is the cache keyed on a route without including the user ID? `GET /profile` cached at the route level instead of `user:{user_id}:profile`.
   - Session leak: are connection pools or middleware leaking request context between coroutines?
   - Race condition: two concurrent requests to the same endpoint returning cross-contaminated data (async context variable misuse).

4. **Investigation steps:**
   - Add trace IDs to every response header. Correlate the "wrong data" responses to specific server instances or workers.
   - Add detailed logging at the cache hit/miss decision point.
   - Check if the bug correlates with high load (cache under pressure) or specific time patterns.
   - Reproduce with a load test targeting the suspect endpoint.

5. **Immediate mitigation:** If wrong-user data — disable caching for that endpoint immediately. Stale data — reduce TTL or purge affected cache keys.

**Follow-up probes:**
- How would you reproduce this in a staging environment?
- If the issue only appears under load, what does that tell you?
- How would you prevent this class of bug in future code reviews?
- What monitoring would you add so you catch this before customers report it?

---

## Scenario 3: FastAPI Service Timing Out at High Load

**Scenario:** Your FastAPI service handles 50 req/s normally. Under a load test at 500 req/s, clients start getting 504 Gateway Timeout. Walk through your diagnosis.

**What they're testing:** Async I/O understanding, profiling methodology, infrastructure awareness, the difference between I/O-bound and CPU-bound bottlenecks.

**Strong answer outline:**

1. **First question:** is it the app or the infrastructure? Check gateway/load balancer metrics — is the timeout happening at the LB before reaching the app, or is the app receiving requests and taking too long?

2. **If the app is the problem — identify the bottleneck type:**
   - I/O bound: await calls blocking — check if you are using sync DB drivers in async code (e.g., `psycopg2` instead of `asyncpg`). One sync DB call blocks the entire event loop.
   - CPU bound: heavy computation in an async handler starves the event loop. Profile with `py-spy` to see where CPU time goes.
   - Worker exhaustion: not enough Gunicorn workers. Under high load, the worker pool is saturated. Add workers or scale horizontally.

3. **Specific FastAPI pitfalls:**
   - Mixing `def` (sync) endpoints with async workers. FastAPI runs sync endpoints in a thread pool, but that pool has a default limit of 40 threads.
   - `await asyncio.sleep()` is fine; `time.sleep()` in an async handler blocks the event loop entirely.
   - N+1 queries: an endpoint making 50 DB calls per request hits the DB connection pool limit under load.

4. **Investigation steps:**
   - `py-spy top --pid <gunicorn_worker_pid>` — live flame graph
   - Check DB connection pool metrics — are all connections in use?
   - Check memory — are workers being OOM-killed and respawning?
   - Use `uvloop` instead of default asyncio event loop (drop-in speed improvement)
   - Check Gunicorn `--timeout` — if workers take > timeout seconds they are killed and return 502/504

5. **Fixes in priority order:** Fix sync-in-async first (biggest gain). Then DB pool exhaustion. Then add workers. Then horizontal scaling.

**Follow-up probes:**
- How many Gunicorn workers should you run per CPU core?
- What is the difference between a 502 and 504 from the load balancer's perspective?
- How would you do zero-downtime load testing without affecting production?
- When would you move a CPU-intensive operation out of the API into a background worker?

---

## Scenario 4: Design Auth for a Multi-Tenant SaaS API

**Scenario:** You are building a SaaS API where different organizations (tenants) each have their own users and data. Users within an org have different roles (admin, member, read-only). Design the auth system.

**What they're testing:** RBAC understanding, JWT design, tenant isolation, scope modeling.

**Strong answer outline:**

1. **Two levels of identity:** tenant identity (which org) + user identity (which user within that org). Both must be present in every token.

2. **JWT payload design:**
   ```json
   {
     "sub": "usr_4xkP9mNq2L",
     "tenant_id": "org_7hJq3rTv8K",
     "roles": ["admin"],
     "scopes": ["read:users", "write:users", "read:billing"],
     "exp": 1706180460
   }
   ```

3. **Tenant isolation in every query:** every DB query must be scoped with `WHERE tenant_id = ?`. Never trust a client-provided tenant ID — always extract from the verified JWT.

4. **Role hierarchy:** define roles as sets of scopes. Admin gets all scopes. Member gets standard scopes. Read-only gets only read:* scopes. Store roles in DB (not in the JWT — they change frequently). Check roles on each request via a middleware or dependency.

5. **Cross-tenant operations:** super-admin role exists only internally (not issuable via OAuth). Audit log every cross-tenant action.

6. **Token issuance:** use an identity provider (Auth0, Cognito, or self-hosted) for user authentication. Issue short-lived access tokens (15 min) + refresh tokens. Refresh tokens are per-tenant-session.

7. **API key support:** for server-to-server within a tenant. API keys are scoped to a tenant and carry explicit scopes. Store hashed in DB.

**Follow-up probes:**
- What happens if a user changes roles? How quickly does the change take effect? (JWT caching problem)
- How do you handle a tenant being suspended? (token revocation)
- How do you prevent a user from one tenant accessing another tenant's data if your DB query accidentally omits the tenant_id filter?
- How would you design "user invited to multiple orgs" (one user, multiple tenant memberships)?

---

## Scenario 5: Migrate a Monolith REST API to Microservices

**Scenario:** You have a monolithic FastAPI app with 80 endpoints. Leadership wants to migrate to microservices. What breaks first and how do you approach it?

**What they're testing:** Strangler fig pattern knowledge, data decomposition challenges, distributed system realities.

**Strong answer outline:**

1. **What breaks first:** distributed transactions. In the monolith, `place_order()` calls `deduct_inventory()`, `charge_payment()`, and `send_confirmation()` in one function with one DB transaction. In microservices, these are three separate services. If payment succeeds but inventory deduction fails, you have inconsistent state. This requires saga pattern or at-minimum compensating transactions.

2. **Data decomposition is the real problem:** services cannot share a DB. You need to split a single database into per-service databases. Identifying the right data boundaries (following domain boundaries) is harder than splitting the code.

3. **Approach — strangler fig:**
   - Keep the monolith running. Build a new microservice for one bounded context (e.g., notifications).
   - Route traffic for that domain to the new service via the API gateway.
   - Over time, strangle more domains out of the monolith.
   - Never do a big bang rewrite.

4. **API contract:** the public API surface stays the same. The gateway routes `/orders/*` to the orders service, `/users/*` to the users service. Clients see no change.

5. **Other things that break:**
   - Shared auth middleware — now needs to be an API gateway concern or a shared library.
   - Shared in-memory caches — must be replaced with Redis.
   - Simple function calls become network calls — add timeouts, retries, circuit breakers.
   - Testing becomes harder — you need integration tests across service boundaries.

6. **When NOT to migrate:** if the team is small (< 10 engineers), the operational overhead of microservices (separate CI/CD, logging, tracing, service mesh) likely costs more than the coupling problem it solves.

**Follow-up probes:**
- How do you handle a feature that spans two services mid-migration?
- What is the strangler fig pattern and when does it not work?
- How do you ensure consistent authorization across services?
- What observability do you need before you can safely run microservices?

---

## Scenario 6: Client Reports "401 Randomly" — Walk Through All Possible Causes

**Scenario:** A client says their API requests randomly fail with 401 Unauthorized. It happens maybe 5% of the time. Walk through every possible cause.

**What they're testing:** Auth flow depth, clock skew awareness, token lifecycle understanding.

**Strong answer outline:**

1. **Token expiry race condition:** the client checks `exp` before sending the request. Token has 30 seconds left. The request takes 15 seconds to arrive. Token expires mid-flight. The check-then-use window is the problem. Fix: refresh when token has < 60 seconds remaining (not zero).

2. **Clock skew:** the client's clock is behind the server's clock. A token issued with `iat: now()` on the server appears to be "issued in the future" from the server's perspective on the next request if clocks diverge. Fix: use `nbf` tolerance in JWT validation (`leeway=5` seconds).

3. **Load balancer routing to a different server with a different secret:** if you have multiple API servers and they use different `SECRET_KEY` values to sign JWTs (misconfiguration), tokens signed by server A are rejected by server B. Fix: ensure all instances share the same secret (from environment/secrets manager).

4. **Token refresh race condition (concurrent requests):** client sends two requests simultaneously. Both detect token is near expiry. Both try to refresh at the same time. One gets a new token, the other gets the old token. The old refresh token may be invalidated by the first refresh (rotation). Fix: use a mutex around the refresh logic on the client side.

5. **Refresh token rotation:** each refresh issues a new refresh token and revokes the old one. If the client retries the same refresh token (network failure on the first attempt), the second attempt uses an already-revoked token → 401. Fix: server detects reuse of a revoked refresh token and returns a specific error code.

6. **Token in CDN cache:** the CDN is caching the `401` response and returning it to subsequent requests (e.g., CDN caches by URL, authentication is in the query param). Fix: never put auth tokens in URLs. Use headers.

7. **Deployment timing:** a rolling deploy is in progress. Old servers accept old token format. New servers accept new token format. Tokens issued during the transition fail on some servers. Fix: maintain backward compatibility for one deploy cycle during format migrations.

**Follow-up probes:**
- How would you instrument this to identify which cause is responsible?
- If the 401 rate correlates with a specific time of day, what would that suggest?
- What is the difference between 401 and 403 and why does it matter here?

---

## Scenario 7: Design a Webhook System with Guaranteed Delivery

**Scenario:** Your platform needs to send webhook events to customer endpoints. Design the system so events are never lost, even if the customer's endpoint is down.

**What they're testing:** Event durability, retry strategy, at-least-once vs exactly-once, dead letter queues.

**Strong answer outline:**

1. **Core architecture:** event → persistent queue (DB or SQS/Kafka) → worker → deliver to customer URL → mark delivered. Never fire-and-forget.

2. **Persistence first:** write the event to a `webhook_deliveries` table before attempting delivery. Status: `pending → in_flight → delivered | failed`.

3. **Retry strategy:** exponential backoff with jitter. Attempt 1 immediately. Then 1 min, 5 min, 30 min, 2 hr, 12 hr, 24 hr. Max 7 days (configurable). After max retries, move to dead letter queue and alert the customer.

4. **Idempotency:** include a unique `event_id` in every webhook payload. Customers should deduplicate on `event_id` on their side. Document this clearly.

5. **Signature verification:** sign the payload with HMAC-SHA256 using a per-customer secret. Include timestamp to prevent replay attacks. Customers verify on receipt.

6. **Failure detection:** treat any non-2xx response as a failure. Treat timeouts (> 10 seconds) as failures. Treat connection refused as failures.

7. **Customer portal:** let customers see delivery history — timestamp, payload, response code, retry count. Let them manually re-trigger failed deliveries.

8. **Circuit breaker per customer endpoint:** if an endpoint has failed 100 consecutive times over 24 hours, pause delivery, notify the customer, and let them re-enable. Prevents wasted retries to dead endpoints.

9. **Ordering:** by default, events are delivered in order of creation per resource (e.g., all `payment.*` events for `pay_123` are ordered). Across resources, ordering is best-effort.

**Follow-up probes:**
- What is the difference between at-least-once and exactly-once delivery? Which do you provide?
- How do you handle the case where a customer's endpoint is slow (10+ second responses)?
- How would you scale this to 10 million webhook deliveries per day?
- How do you prevent a slow customer endpoint from blocking delivery to other customers?

---

## Scenario 8: API Versioning for a Public API with 50,000 Active Clients — How to Deprecate v1?

**Scenario:** You have 50,000 clients using v1 of your API. You need to release v2 with breaking changes. How do you manage the v1 deprecation?

**What they're testing:** Versioning strategy, deprecation communication, traffic analysis, business context of API management.

**Strong answer outline:**

1. **Define "breaking change" precisely:** removing endpoints, removing/renaming response fields, changing field types, changing authentication. Adding fields is not breaking. Changing behavior (semantics) without changing schema can be breaking.

2. **Traffic analysis first:** before announcing anything, analyze v1 usage. Which endpoints are called? By how many clients? Which clients have not called in 90 days (likely safe to cut)? This tells you the real migration effort.

3. **Deploy v2 alongside v1:** both run simultaneously. The gateway routes `/v1/*` and `/v2/*` independently. Services can run v1 and v2 code from the same deployment (feature flags or separate handlers).

4. **Deprecation headers:** the day v2 launches, add to all v1 responses:
   ```
   Deprecation: true
   Sunset: Sat, 01 Jan 2026 00:00:00 GMT
   Link: <https://api.example.com/v2/docs>; rel="successor-version"
   ```

5. **Developer communication:** email to all registered API key holders. Dashboard warning on login. Developer blog post with migration guide. At least 6–12 months notice for public APIs.

6. **Active migration support:** publish a migration guide. Offer a compatibility layer where v2 can accept v1-shaped requests with a header for a transition period.

7. **Monitor the sunset:** track v1 usage weekly. Email clients still calling v1 with 30, 14, 7 day reminders. Show their API key and the specific endpoints still in use.

8. **Hard shutdown:** on sunset date, change v1 responses to `410 Gone` with a `Link` to v2 docs. Do not silently break — give a clear message.

**Follow-up probes:**
- What if 10% of clients never migrate — do you keep v1 running indefinitely?
- How would you handle an enterprise client that says they "cannot migrate for 18 months"?
- How do you detect if your v2 changes actually broke a client before they report it?
- What tooling would you use to detect breaking changes automatically in CI?

---

## Scenario 9: Design a File Upload API for Files up to 10GB

**Scenario:** Your platform needs to accept file uploads up to 10GB. Design the API.

**What they're testing:** Multipart upload, cloud storage patterns, resumable uploads, timeout handling.

**Strong answer outline:**

1. **Never stream 10GB through your API server.** The API server returns a presigned URL. The client uploads directly to object storage (S3, GCS). Your server never touches the file bytes.

2. **Small files (< 5MB) — direct upload:**
   ```
   POST /uploads/presign
   Body: {"filename": "report.csv", "size": 1048576, "content_type": "text/csv"}
   Response: {"upload_url": "https://s3.../...", "upload_id": "upl_xxx", "expires_in": 3600}
   
   Client → PUT {upload_url}   # direct to S3 with presigned URL
   
   POST /uploads/upl_xxx/complete   # notify API that upload finished
   ```

3. **Large files (> 5MB) — multipart upload:**
   - S3 multipart upload: client splits file into N chunks (5MB+ each)
   - API server creates the multipart upload, returns `upload_id` + presigned URLs per part
   - Client uploads each part directly to S3 in parallel
   - Client notifies API with the list of `ETag` values per part
   - API calls `CompleteMultipartUpload` on S3

4. **Resumable uploads:** store which parts are already uploaded. If upload is interrupted, client can GET the part status and resume from the last successful part.

5. **Post-upload processing:**
   - S3 event notification → SQS → Lambda/worker for virus scan, format validation, thumbnail generation
   - Upload status transitions: `pending → uploading → processing → ready | failed`
   - Client polls `/uploads/{upload_id}` for status (or receives webhook)

6. **Security considerations:**
   - Presigned URL expires after 1 hour (client must complete in time)
   - Presigned URL is scoped to one specific S3 key — client cannot upload to arbitrary locations
   - Content-Type validation before issuing presigned URL
   - File size limit enforced via S3 policy on the presigned URL

7. **Chunked API for non-S3 setups:**
   ```
   POST /uploads     → returns upload_id, chunk_size
   PUT  /uploads/{id}/chunks/{n}   → upload one chunk
   POST /uploads/{id}/complete     → finalize
   ```

**Follow-up probes:**
- How do you handle an upload that the client never completes? (S3 lifecycle rule to abort incomplete multipart uploads after N days)
- How do you stream a 10GB file to a client? (presigned download URL, same pattern)
- How would you enforce per-user storage quotas?
- What happens if the client loses internet mid-upload? (resumable upload, part tracking)

---

## Scenario 10: Pagination Strategy for a Feed API with Real-Time Inserts

**Scenario:** You are building a social feed API. New posts are inserted constantly. Users scroll through the feed. Design the pagination strategy so they do not see duplicates or skip items as they scroll.

**What they're testing:** Cursor pagination vs offset, keyset pagination, real-time data awareness, the "page drift" problem.

**Strong answer outline:**

1. **Offset pagination fails here.** If a user is on page 3 and 5 new posts are inserted at the top, the next page request shifts all items by 5. Items the user already saw appear again. Items they should see get skipped. Offset is completely wrong for real-time feeds.

2. **Cursor pagination with stable sort key:** use `created_at` (with `id` as tiebreaker) as the cursor. The query is `WHERE created_at < cursor_time ORDER BY created_at DESC LIMIT 20`. Inserts above the cursor do not affect what comes after it.

3. **Cursor encodes position, not a page number:**
   ```json
   {
     "data": [...],
     "next_cursor": "eyJjcmVhdGVkX2F0IjogIjIwMjQtMDEtMjVUMTA6MzA6MDBaIiwgImlkIjogIjQyIn0=",
     "has_more": true
   }
   ```
   The cursor is `base64({"created_at": "2024-01-25T10:30:00Z", "id": "42"})`.

4. **Anchor the session at load time:** when the user first opens the feed, record the current timestamp as `session_anchor`. The infinite scroll retrieves items `WHERE created_at <= session_anchor`. New posts are shown via a "N new posts — tap to refresh" banner, not injected into the scroll position.

5. **First-page problem:** the first load has no cursor. Use `WHERE created_at <= now() ORDER BY created_at DESC LIMIT 20`. Return the anchor timestamp in the response so the client pins it.

6. **Compound cursor for exact ordering:** if two posts have identical `created_at` (concurrent inserts), use `(created_at, id)` as the compound cursor: `WHERE (created_at, id) < (cursor_time, cursor_id)`.

7. **Caching considerations:** cache the first page aggressively (the hot path). Subsequent pages (deeper scroll) are not cacheable at the CDN level because they are user-specific cursor-based queries.

**Follow-up probes:**
- What happens if a post is deleted between scroll pages? (gap in the feed — acceptable, document it)
- How would you implement "pull to refresh" with this design?
- What if you need the total count for "showing X of Y posts"? (expensive with cursor pagination — consider an approximate count)
- How does Twitter's `since_id` and `max_id` approach compare to what you described?

---

## Scenario 11: Design Auth for a Machine-to-Machine (M2M) Integration

**Scenario:** A third-party partner system needs to call your API on a scheduled basis — no human in the loop, no browser. How do you design the auth?

**What they're testing:** OAuth2 client credentials flow, API key vs token trade-offs, secret rotation.

**Strong answer outline:**

1. **OAuth2 Client Credentials flow** — designed exactly for M2M. The partner sends their `client_id` + `client_secret` to your token endpoint, gets a short-lived access token, uses it for API calls.

2. **Token endpoint:**
   ```
   POST /oauth/token
   Content-Type: application/x-www-form-urlencoded
   Body: grant_type=client_credentials&client_id=...&client_secret=...&scope=read:orders
   
   Response: {"access_token": "...", "expires_in": 3600, "token_type": "Bearer"}
   ```

3. **Scopes on the token:** client credentials grant should include explicit scopes. The partner requests only what they need. You approve it during onboarding.

4. **API keys as a simpler alternative:** for lower-security integrations, a long-lived API key (hashed in your DB) is simpler. Trade-off: rotating it requires coordination. Token-based auth (client credentials) allows short-lived tokens and automatic rotation.

5. **Secret rotation:** provide a rotation endpoint or a grace period window where both old and new credentials are valid simultaneously. 24-hour overlap is the standard.

6. **IP allowlisting:** for high-security M2M, combine token auth with an IP allowlist for the partner's outbound IPs. Defense in depth.

**Follow-up probes:**
- How do you handle the partner's token expiring mid-operation? (client handles refresh — short token lifetime is a feature not a bug)
- What is the difference between client credentials flow and authorization code flow?
- How do you audit which partner is making which calls?

---

## Scenario 12: Your API Responses Are Inconsistent — Some Endpoints Return Camelcase, Some Snake_case

**Scenario:** You inherited a codebase with mixed naming conventions in JSON responses. Half the endpoints return `user_id`, the other half return `userId`. You have existing clients using both. How do you fix it?

**What they're testing:** API governance, backward compatibility, migration planning, client impact analysis.

**Strong answer outline:**

1. **Do not just pick one and change everything.** Changing `user_id` to `userId` on existing endpoints is a breaking change. Clients using SDKs or code that reads `user_id` will silently break.

2. **Audit first:** inventory every response field across all endpoints. Classify into: already snake_case, already camelCase, or mixed. Assess client impact by checking API key usage logs per endpoint.

3. **Decision on standard:** pick one convention and apply it going forward. Snake_case is Python convention and aligns with most JSON:API standards. CamelCase is JavaScript/JSON convention. Either is fine — consistency is what matters.

4. **New endpoints only:** apply the standard immediately to all new endpoints. Do not touch existing endpoints yet.

5. **Migration path for existing endpoints:** add a versioned endpoint with the corrected format (e.g., `/v2/users`). Return both `user_id` and `userId` with a `Deprecation` header on the old field. Run both for 6+ months. Remove the old field with a version bump.

6. **Content negotiation alternative:** support `Accept: application/json; naming=camelcase` to let clients opt into the new format without a version bump. More complex to implement but avoids proliferating versions.

7. **Serialization layer:** implement naming convention as a middleware or Pydantic alias generator, not field-by-field. That way you write snake_case in Python (natural) and the serializer converts to camelCase for output automatically.

**Follow-up probes:**
- What if you cannot find who owns some of these clients?
- How would you use OpenAPI spec to enforce naming convention in CI?
- How does Pydantic's `alias_generator` help here?

---

**[🏠 Back to README](../README.md)**

**Prev:** [← API Questions](./api_questions.md) &nbsp;|&nbsp; **Next:** —

**Related Topics:** [API Design Patterns](../16_api_design_patterns/) · [Real-World APIs](../18_real_world_apis/) · [API Security](../11_api_security_production/) · [API Gateway](../15_api_gateway/)
