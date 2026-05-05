# 🎯 REST Best Practices — Interview Preparation

> This file prepares you to discuss REST API design like a working engineer.
> Not just definitions — but real-world usage, trade-offs, and production scenarios.

---

# 🔹 Basic Level Questions (0–2 Years)

**Q1: Why should URL paths use hyphens instead of underscores?**

<details>
<summary>💡 Show Answer</summary>

Underscores can be hidden when URLs are rendered as hyperlinks in browsers and documents — the underline formatting obscures them. Search engines also treat hyphenated words as separate tokens (better SEO), while underscored words are treated as a single token. URLs are also case-sensitive and underscores appear less consistent in mixed-case contexts.

The convention is lowercase, hyphen-separated: `/payment-methods`, not `/paymentMethods` and not `/payment_methods`. This is consistent across major API style guides (Google, Stripe, Twilio).

</details>

<br>

**Q2: Should REST API collections use singular or plural nouns?**

<details>
<summary>💡 Show Answer</summary>

Always plural for collections. `/users` not `/user`. `/orders` not `/order`. This is because a collection endpoint logically represents "all users" — plural makes that relationship clearer and consistent. Single resources are then natural: `/users/42` is "user 42 from the users collection."

Consistency matters more than any single rule. An API that mixes `/user` and `/orders` is more confusing than one that uses either convention throughout.

</details>

<br>

**Q3: What is the recommended error response structure for a REST API?**

<details>
<summary>💡 Show Answer</summary>

A good error response has three layers: a machine-readable `code` string that clients can switch on (e.g., `VALIDATION_ERROR`, `NOT_FOUND`), a human-readable `message` string for developers, and for validation errors, a `details` array with field-level errors. Example:

```json
{"error": {"code": "VALIDATION_ERROR", "message": "Request validation failed", "details": [{"field": "email", "message": "must be a valid email"}]}}
```

The `code` field decouples client logic from HTTP status codes — a client can handle `RATE_LIMIT_EXCEEDED` specifically without parsing the message string. Never return `{"success": false}` with a 200 status — that breaks all HTTP-aware infrastructure.

</details>

<br>

**Q4: What is an idempotency key and when do you use one?**

<details>
<summary>💡 Show Answer</summary>

An idempotency key is a UUID the client generates and sends in a request header (`Idempotency-Key: <uuid>`). The server processes the request the first time and stores the result keyed by the UUID. If the client retries (because of a network failure or timeout), the server returns the stored result without processing again.

Use idempotency keys for any POST operation where double-processing causes harm: payments, order creation, email sending. Without them, a client that retries after a timeout risks charging a customer twice. Stripe requires idempotency keys on all payment requests.

</details>

<br>

**Q5: What does a response envelope (`data` wrapper) give you over returning a bare array?**

<details>
<summary>💡 Show Answer</summary>

Returning a bare JSON array `[...]` is inflexible — you can't add pagination metadata, status fields, or links without breaking the response contract. Clients expecting an array break if you add a top-level key.

With an envelope like `{"data": [...], "meta": {"total": 500, "page": 2}}`, you can extend the response with pagination, request IDs, warnings, or deprecation notices without changing the shape clients already parse. It also makes collection and single-resource responses consistent — both are objects, just with different `data` values. This is the standard pattern used by Stripe, GitHub, and most well-designed public APIs.

</details>

<br>

---

# 🔹 Intermediate Level Questions (2–5 Years)

**Q6: What are the trade-offs between offset pagination and cursor pagination?**

<details>
<summary>💡 Show Answer</summary>

Offset pagination (`?page=2&limit=20`) is easy to implement and allows jumping to any page. The problem: it's unstable under concurrent writes. If a new record is inserted at the top while a client is paginating, every page shifts by one — the client gets a duplicate or skips a record.

Cursor pagination uses an opaque token (usually a base64-encoded ID or timestamp). Pages are always fetched relative to a stable position in the dataset. It's stable under inserts and deletes, and performs better at scale because the query uses an index range scan instead of `OFFSET N` which requires scanning and discarding N rows.

Use offset for admin dashboards and reports (data changes slowly, users want to jump to page 5). Use cursor for feeds, activity streams, and any dataset where inserts happen in real time.

</details>

<br>

**Q7: How do you prevent a sort parameter from being used for SQL injection or causing a full table scan?**

<details>
<summary>💡 Show Answer</summary>

Never pass the sort parameter value directly into a query. Two problems: injection risk (an attacker sends `sort=1;DROP TABLE users`) and performance risk (sorting on an unindexed column causes a full table scan).

The fix is a whitelist: define a set of allowed sort fields in code (`SORTABLE_FIELDS = {"id", "created_at", "price"}`) and validate the incoming parameter against that set before building the query. Return 400 Bad Request if the field is not in the whitelist. Additionally, only add fields to the whitelist if they have a database index — otherwise a sort on that field under load will kill query performance.

</details>

<br>

**Q8: Explain the HTTP versioning options and their trade-offs. Which do you recommend?**

<details>
<summary>💡 Show Answer</summary>

Three options: URL path versioning (`/v1/users`), header versioning (`API-Version: 2024-01-01`), and query param versioning (`?version=2`).

URL versioning is visible in logs, curl-testable, and cache-friendly (CDNs can cache `/v1` and `/v2` separately without a `Vary` header). The purist objection is that the URL should identify a resource, not a version. Header versioning (Stripe's approach) keeps URLs clean and allows date-based granular versioning, but it's invisible in browser navigation and requires `Vary: API-Version` for correct CDN behavior. Query param versioning pollutes the query string and has poor caching behavior.

Recommendation: URL versioning as the default. Header versioning only if you have sophisticated clients and strong URL stability requirements.

</details>

<br>

**Q9: How do you handle deprecating an API endpoint in production without breaking existing clients?**

<details>
<summary>💡 Show Answer</summary>

Deprecation has three phases: announce, deprecate, and sunset. Announce the change in docs and changelog well in advance. Add standard deprecation headers to responses from the old endpoint: `Deprecation: true` and `Sunset: <date>` (RFC 8594). Include a `Link` header pointing to the successor endpoint. Monitor traffic to the old endpoint — if clients are still hitting it near the sunset date, reach out directly.

Never remove an endpoint without a sunset period. How long depends on your API consumers: public APIs need months to years; internal APIs might be weeks. The `Sunset` header lets automated clients detect the deadline programmatically without scraping docs.

</details>

<br>

**Q10: When should you return a 409 Conflict versus a 422 Unprocessable Entity?**

<details>
<summary>💡 Show Answer</summary>

422 means the request is syntactically valid JSON, but the data fails business validation — for example, an email is not in email format, a required field is missing, or an integer is out of range. The problem is intrinsic to the data the client sent.

409 means the request is valid but conflicts with current server state — typically a uniqueness constraint violation. Creating a user with an email that already exists is a 409, not a 422. The distinction matters because the client fix is different: a 422 means fix the data; a 409 means the state on the server needs to change first (e.g., delete the existing record or log in instead of registering).

FastAPI returns 422 by default for Pydantic validation failures. You must raise HTTPException(409) explicitly for business-level conflicts.

</details>

<br>

---

# 🔹 Advanced Level Questions (5+ Years)

**Q11: How do you design an API for backward compatibility when adding new fields to a response?**

<details>
<summary>💡 Show Answer</summary>

Adding new fields to a response is generally safe — clients that don't know about the field ignore it. This is Postel's Law applied: be conservative in what you send, liberal in what you accept. But safe only if clients are written defensively (don't fail on unknown keys). Document this contract in your API style guide.

Dangerous changes (breaking): removing a field, renaming a field, changing a field's type, changing an error code string that clients switch on, changing the HTTP status for an existing operation. These require a new major version.

Production pattern: use a `response_model` (Pydantic or similar) that explicitly declares the contract. New internal fields not in the response model are never leaked. The model is the API contract.

</details>

<br>

**Q12: Describe a complete rate limiting implementation for a multi-tenant public API.**

<details>
<summary>💡 Show Answer</summary>

Multi-tenant rate limiting needs different limits per tier (free: 100/hr, pro: 10,000/hr, enterprise: custom). The identifier is usually the API key, not IP address (IPs are shared by proxies and NAT).

Implementation: use Redis with a sliding window counter. Key format: `ratelimit:{api_key}:{window_start_unix}`. On each request: increment the counter and set expiry. If count exceeds the tier limit, return 429 with `Retry-After` and the standard `X-RateLimit-*` headers.

Layer the limiting: implement coarse limits at the API gateway (Kong, AWS API Gateway) and fine-grained limits in application middleware for per-endpoint controls. Log all 429s with the api_key for abuse detection. Consider burst allowances (token bucket) so a client that's been idle can make 10 rapid requests without hitting rate limits.

</details>

<br>

**Q13: How do you design a REST API endpoint that needs to handle both synchronous and long-running asynchronous operations?**

<details>
<summary>💡 Show Answer</summary>

The standard pattern is the async job pattern. For operations that complete quickly (under ~2 seconds), respond synchronously with the result. For long-running operations, return 202 Accepted immediately with a job/task resource ID and a `Location` header pointing to where the client can poll for status: `Location: /jobs/abc-123`.

The job resource at `GET /jobs/abc-123` returns `{"status": "pending"}`, `{"status": "running", "progress": 40}`, or `{"status": "completed", "result": {...}}`. Return 200 when complete, 202 while running. Optionally add a callback/webhook URL the client can register to receive a push notification when done (avoids polling).

This pattern is used by GitHub Actions, AWS CloudFormation, Stripe (for async payment verification), and most ML inference APIs.

</details>

<br>

**Q14: What happens when a sorting or filtering query has no supporting index in production, and how do you detect and fix it?**

<details>
<summary>💡 Show Answer</summary>

Without an index, the database performs a full table scan for every filter or sort query. At small scale this is invisible. At 1M+ rows it causes queries to take seconds, CPU to spike, and the database to become the bottleneck for the entire service.

Detection: enable slow query logging in PostgreSQL (`log_min_duration_statement = 1000`). Use `EXPLAIN ANALYZE` to verify index usage — look for sequential scans on large tables in hot paths. APM tools (Datadog, New Relic) will show p99 latency spikes correlating with specific endpoints.

Fix: add a database index on all columns that appear in WHERE clauses or ORDER BY clauses exposed via the API. Use composite indexes for common filter+sort combinations. In your API code, only expose filterable fields that have indexes — enforce this with a whitelist, and add a code comment next to each whitelisted field documenting the index it depends on.

</details>

<br>
