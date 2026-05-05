# 🎯 Error Handling Standards — Interview Preparation

> This file prepares you to discuss API error handling like a working engineer.
> Not just definitions — but real-world usage, trade-offs, and production scenarios.

---

# 🔹 Basic Level Questions (0–2 Years)

**Q1: What is wrong with returning `200 OK` with `{"success": false}` for error responses?**

<details>
<summary>💡 Show Answer</summary>

It breaks HTTP semantics that the entire ecosystem depends on. CDNs and proxies see a 200 and cache the error response — subsequent clients get the cached error. Monitoring tools that track 2xx/4xx/5xx rates show 100% success even when half your calls are failing. Client libraries like `requests` only raise exceptions on non-2xx responses, so `raise_for_status()` silently passes on your errors. APM tools, load balancers, and circuit breakers all use HTTP status codes to detect failures.

The fix: use the correct HTTP status code (400, 401, 403, 404, 409, 422, 429, 500) and put a machine-readable `code` string in the body for clients that need to handle specific error types.

</details>

<br>

**Q2: What is the difference between a 400 and a 422 status code?**

<details>
<summary>💡 Show Answer</summary>

400 Bad Request is for malformed requests — the request itself is structurally wrong. Examples: invalid JSON syntax, missing a required header, a query param with an illegal value.

422 Unprocessable Entity means the request is syntactically valid (parseable JSON) but the data fails semantic validation. Examples: an email field that doesn't contain a valid email address, an age field set to -5, a date range where end is before start. FastAPI returns 422 by default for Pydantic validation failures.

The distinction tells the client why their request failed: a 400 means "you sent garbage," a 422 means "I understood you but the values don't make sense."

</details>

<br>

**Q3: What is the recommended error response structure and what does each field do?**

<details>
<summary>💡 Show Answer</summary>

The three-field structure: `code` (machine-readable string constant like `VALIDATION_ERROR`), `message` (human-readable description for developers), and `details` (array of field-level errors for validation failures).

`code` is what client code switches on — it decouples client logic from the HTTP status code and from the `message` string (which can change). `message` is for developers reading logs or the API response in a browser. `details` is specifically for validation errors and maps field names to error messages, enabling form UIs to highlight the specific field that failed.

</details>

<br>

**Q4: Which HTTP errors are retryable and which are not?**

<details>
<summary>💡 Show Answer</summary>

Not retryable: 400 (fix the request — it's a client bug), 403 (permissions won't change by retrying), 404 (resource doesn't exist). Retrying these wastes resources and never succeeds.

Retryable: 429 (rate limited — wait `Retry-After` seconds), 500 (server bug — retry with exponential backoff), 502 and 504 (upstream failure — temporary, retry with backoff), 503 (server overloaded — retry after waiting).

401 is special: sometimes retryable (refresh your token and try once more), but if refreshing also fails, stop — there's an auth problem that retrying won't fix.

</details>

<br>

**Q5: What should a 409 Conflict response look like in practice?**

<details>
<summary>💡 Show Answer</summary>

A 409 means the request is valid but conflicts with current server state — most commonly a uniqueness violation. Example: trying to register with an email that already exists.

The response should: use `status_code=409`, include the `CONFLICT` error code, a clear message explaining what conflicts, and ideally a `details` array pointing to the specific field. Example body: `{"error": {"code": "CONFLICT", "message": "Email address is already registered", "details": [{"field": "email", "message": "email address is already registered"}]}}`.

The field-level detail in `details` lets the frontend highlight the specific input. This is better than a generic "conflict occurred" message that leaves the client guessing which field caused the conflict.

</details>

<br>

---

# 🔹 Intermediate Level Questions (2–5 Years)

**Q6: How do you customize FastAPI's default 422 validation error format to match your API's error schema?**

<details>
<summary>💡 Show Answer</summary>

Register a custom exception handler for `RequestValidationError`. FastAPI's default 422 format looks nothing like a standard `{"error": {"code": ..., "details": [...]}}` structure.

In the handler, iterate `exc.errors()` to extract each validation failure. Each error has a `loc` (tuple showing location in the request), `msg` (error message), and `type`. Build your `details` array by joining the `loc` parts into a dotted field path. Return a `JSONResponse` with your standard error structure and `status_code=422`.

Also register a catch-all handler for `Exception` to prevent unhandled exceptions from leaking stack traces in production — return a generic `{"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}}` with status 500 and log the full exception internally.

</details>

<br>

**Q7: What is RFC 7807 Problem Details and when might you use it?**

<details>
<summary>💡 Show Answer</summary>

RFC 7807 is a standardized JSON error format for HTTP APIs. It uses fields: `type` (a URI identifying the error type), `title` (short human-readable description), `status` (the HTTP status code), `detail` (specific error detail for this occurrence), and `instance` (URI of the request that caused the error). Content-Type is `application/problem+json`.

It's worth knowing about because some enterprise and government APIs require it, and some frameworks implement it by default. The advantage over a custom format is interoperability — tooling that understands RFC 7807 can handle errors from any compliant API.

In practice most teams define their own consistent error format rather than adopting RFC 7807, unless they're building a platform that third parties will integrate with heavily.

</details>

<br>

**Q8: How do you handle errors from a downstream service call in your API without leaking internal details?**

<details>
<summary>💡 Show Answer</summary>

Never propagate raw downstream error messages or stack traces to your API clients. The downstream service's error schema, internal URLs, and infrastructure details are implementation details that clients should never see.

Pattern: catch the downstream exception, log the full error internally with enough context to debug (request ID, service name, status code, body), then return a sanitized error response to your client. If the downstream failure is temporary (5xx or timeout), return 503 Service Unavailable or 502 Bad Gateway to signal the client should retry. If the downstream failure is due to bad client input you passed through, return a 400 with a message about the input, not the downstream error.

Add a correlation ID (`X-Request-ID`) to all requests so you can trace a client-visible error ID back to the full internal log chain.

</details>

<br>

**Q9: What does a good validation error response look like for a form with multiple invalid fields?**

<details>
<summary>💡 Show Answer</summary>

Return all validation errors at once in a single response — not just the first one. Returning errors one at a time forces the client into a frustrating "fix one thing, resubmit, fix another" loop.

The `details` array should contain one entry per invalid field with the exact field name and a specific, actionable error message. Specific: "must be a valid email address" not "invalid." Actionable: "must be at least 8 characters" not "too short." The `field` value must match the request body key exactly so frontend code can highlight the right input without string parsing.

Also: validate all fields regardless of whether earlier fields failed, so the client sees everything wrong in one response.

</details>

<br>

**Q10: How does client-side error handling logic differ for 4xx vs 5xx responses?**

<details>
<summary>💡 Show Answer</summary>

4xx errors are client errors — retrying the same request will not help because the request itself is wrong. The client should handle them by user action or code fix: show a 400/422 to the developer or display field errors, show a 401 as a login prompt, show a 403 as a "you don't have permission" message, show a 404 as a not-found page. Do not retry 4xx.

5xx errors are server errors — the client's request may have been valid, and retrying might succeed. Use exponential backoff: wait 1 second, retry; wait 2 seconds, retry; wait 4 seconds — up to a max delay and max retry count. For 429, use the `Retry-After` header value instead of backoff. Circuit breakers are the production-grade version of this: if a service is failing consistently, stop sending traffic and give it time to recover.

</details>

<br>

---

# 🔹 Advanced Level Questions (5+ Years)

**Q11: Design an error handling architecture for a FastAPI service that needs consistent error format, unhandled exception safety, and observability.**

<details>
<summary>💡 Show Answer</summary>

Three layers: (1) Custom exception hierarchy — define application exceptions like `NotFoundError(resource, id)`, `ConflictError(field, value)`, `AuthError(reason)`. These carry structured context. (2) Exception handlers — register handlers for each custom exception class plus `RequestValidationError` and the catch-all `Exception`. Each handler formats the error into your standard schema and returns the correct status code. (3) Observability — the catch-all `Exception` handler logs the full traceback with a generated request ID (from middleware or the incoming `X-Request-ID` header). Return the request ID in the error response body so clients can report it to support.

Never let `Exception` reach the ASGI server unhandled — Uvicorn/Gunicorn will return a plain 500 with no body, losing all context and breaking your error schema contract.

</details>

<br>

**Q12: What are the trade-offs of including `value` (the bad input) in a validation error details array?**

<details>
<summary>💡 Show Answer</summary>

Including the submitted value helps developers debug — they can see exactly what was sent and why it failed, without re-inspecting their request. FastAPI's default validation errors include the value.

The risk: inadvertent data leakage. If a field contains a password, credit card number, or sensitive PII, echoing it back in the error response could expose it in client-side logs, browser developer tools, or error tracking services (Sentry, Datadog). Some security auditors flag this explicitly.

The practical rule: include the value for safe fields (enum choices, numeric ranges, string format violations). Strip the value for fields containing credentials, tokens, financial data, or any field where the value itself is sensitive. Implement this at the custom exception handler level with a field-level configuration or a naming convention (e.g., always strip fields named `password`, `token`, `secret`, `card_number`).

</details>

<br>

**Q13: How do you propagate errors correctly across a chain of microservices without losing context?**

<details>
<summary>💡 Show Answer</summary>

Use correlation IDs (also called trace IDs). The first service in the chain generates a UUID for each incoming request and attaches it to the request context. Every downstream service-to-service call includes this ID in the `X-Request-ID` (or `X-Correlation-ID`) header. Every log line from every service in the chain includes the ID. Every error response returned to the original caller includes the ID.

When an error propagates upward, each service translates the downstream error into an appropriate response for its own callers — it does not blindly relay internal errors. Log the full downstream error internally with the correlation ID. Return to the caller only what they need to know (503 if it's a temporary failure, 400 if it's their fault, etc.).

For full distributed tracing, use OpenTelemetry with spans — this gives you a visual trace of the entire call chain with timing, service names, and error annotations in tools like Jaeger, Zipkin, or Datadog APM.

</details>

<br>

**Q14: How does the sorting whitelist pattern prevent both SQL injection and accidental full table scans?**

<details>
<summary>💡 Show Answer</summary>

SQL injection: if you accept a sort field from the client and interpolate it directly into a query string (`ORDER BY {sort_field}`), an attacker can send `sort_field=1; DROP TABLE users` or a subquery. Parameterized queries protect against value injection but not column name injection — column names cannot be parameterized. The only safe option is to validate the field against a known-good list before using it in the query.

Full table scan: even with safe input, sorting on an unindexed column requires the database to sort all rows in memory before returning the page — for a 10M-row table, this can take seconds and spike CPU. The whitelist also enforces that only indexed columns are sortable, which is documented by the whitelist itself: `SORTABLE_FIELDS = {"id", "created_at", "price"}` — every field in this set should have a corresponding database index. Adding a new sort option without adding an index is a production performance incident waiting to happen.

</details>

<br>
