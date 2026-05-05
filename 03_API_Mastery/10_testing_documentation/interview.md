# 🎯 API Testing & Documentation — Interview Preparation

> This file prepares you to discuss API testing and documentation like a working engineer.
> Not just definitions — but real-world usage, trade-offs, and production scenarios.

---

# 🔹 Basic Level Questions (0–2 Years)

**Q1: What is FastAPI's TestClient and how does it differ from making real HTTP requests in tests?**

<details>
<summary>💡 Show Answer</summary>

TestClient wraps the ASGI application and runs requests in-process without starting a real server or opening a network socket. It is built on top of httpx and calls the application directly, which makes tests fast and deterministic — no port conflicts, no network latency, no need to manage a server lifecycle.

The key difference from real HTTP: TestClient is synchronous even if your routes are async, which keeps test code simple. It also shares the same process memory as the app, so you can use monkeypatch and module-level overrides to swap dependencies. The limitation is that it does not test the full deployment stack — Nginx, TLS termination, load balancer behavior, and Uvicorn worker concurrency are not tested. For those you need a staging environment or an end-to-end test suite against a running server.

</details>

<br>

**Q2: What status codes should you test for a typical POST endpoint that creates a resource?**

<details>
<summary>💡 Show Answer</summary>

At minimum: 201 Created on success (with a Location header pointing to the new resource and the created object in the body), 400 or 422 for invalid input (missing required fields, wrong types, out-of-range values), 401 if the endpoint requires authentication and no token is provided, 403 if the authenticated user does not have permission to create this resource type, and 409 Conflict if the resource already exists (duplicate email, duplicate slug).

A common gap is forgetting to test the 422 path with several different invalid inputs — one test for "missing required field" is not enough. Test missing field, wrong type, and boundary violations separately. Also test that 500 errors do not leak stack traces or internal file paths in the response body.

</details>

<br>

**Q3: What is the purpose of a pytest fixture and give an example of one used in API testing?**

<details>
<summary>💡 Show Answer</summary>

A fixture provides reusable setup and teardown logic to tests. Instead of repeating database setup or client initialization in every test function, you define it once in a fixture and inject it as a parameter.

In API testing a common pattern is a database session fixture that rolls back after each test: it creates a session, sets a savepoint with begin_nested(), yields the session to the test, then calls rollback() regardless of pass or fail. This guarantees tests are isolated — no test leaves dirty data that affects the next test. Another common fixture is an auth_client that creates a test user, generates a valid JWT, and returns a TestClient with the Authorization header pre-set, so auth-protected tests do not need to repeat the login flow.

</details>

<br>

**Q4: What is the difference between 401 Unauthorized and 403 Forbidden, and how do you test for both?**

<details>
<summary>💡 Show Answer</summary>

401 means the request lacks valid credentials — the client is not authenticated. The server cannot determine who is making the request. In practice this means: no token provided, token is malformed, or token is expired.

403 means the client is authenticated but does not have permission to perform the action. The server knows who you are but says "no." For example: a regular user calling a DELETE /admin/users endpoint.

To test both: for 401, send a request with no Authorization header and another with a deliberately bad or expired token — both should return 401. For 403, generate a valid token for a user with the "viewer" or "user" role and call an endpoint that requires "admin" — expect 403. IDOR (Insecure Direct Object Reference) tests also belong here: authenticate as user 42 and request /users/99/orders — should return 403 or 404, never 200.

</details>

<br>

**Q5: Where does FastAPI auto-generate its documentation from and how can you customize it?**

<details>
<summary>💡 Show Answer</summary>

FastAPI generates its OpenAPI 3.x schema automatically by inspecting route function signatures, Pydantic models used as request bodies and response models, and the type annotations on parameters. The schema is served at /openapi.json. Swagger UI is served at /docs and ReDoc at /redoc.

Customization: add a description to endpoints via the docstring or the description parameter on the decorator. Add examples to Pydantic fields using Field(example="alice@example.com"). Tag endpoints with tags=["users"] to group them in the UI. Set response_model on the route decorator to document the exact response shape. In production you typically disable /docs and /redoc by passing docs_url=None, redoc_url=None to the FastAPI constructor — you do not want to expose the interactive UI to end users.

</details>

<br>

---

# 🔹 Intermediate Level Questions (2–5 Years)

**Q6: How do you mock an external API call in a test and what are the trade-offs between responses library and monkeypatch?**

<details>
<summary>💡 Show Answer</summary>

Both tools intercept external HTTP calls so tests do not make real network requests. The responses library (pip install responses) registers mock URLs at the HTTP layer — any call to that URL returns the configured mock response regardless of which HTTP library makes the call. This is framework-agnostic and works even if the production code uses requests, httpx, or urllib internally.

monkeypatch replaces the Python object directly — you swap the service function or the HTTP client method with a custom function that returns test data. It is simpler for unit tests and lets you assert on how the mock was called (which arguments, how many times). The limitation is that it is tightly coupled to the internal implementation — if the production code changes which function it calls, the monkeypatch target changes too.

Use responses (or httpretty/respx for async) for integration tests that should survive internal refactors. Use monkeypatch for unit tests where you want tight control over call arguments. Both approaches should verify that the mock was called — assert len(responses.calls) == 1 or check the called_with list.

</details>

<br>

**Q7: How do you test that your API does not leak internal information in 500 error responses?**

<details>
<summary>💡 Show Answer</summary>

The test pattern: use monkeypatch to inject a dependency that raises an uncaught exception, then assert that the 500 response body does not contain "traceback", "Traceback", file paths, or exception class names. The response should return a generic error object in your standard error schema with a request ID for tracing.

In production code, this is enforced by a global exception handler registered on the FastAPI app that catches all unhandled exceptions, logs the full traceback internally (with the request ID), and returns a sanitized 500 response to the client. The test verifies the handler is in place and working. A common failure mode: the handler is added to the app but a dependency is called before the handler is registered in the middleware stack — test with several injection points, not just one.

</details>

<br>

**Q8: What is load testing and what metrics should you collect during a Locust or k6 run?**

<details>
<summary>💡 Show Answer</summary>

Load testing drives a target API with simulated concurrent users to find the throughput and latency characteristics under realistic traffic. Locust uses Python to define user behavior; k6 uses JavaScript and is better for CI pipelines because it runs headlessly and produces structured output.

Metrics to collect: requests per second (throughput), p50/p95/p99 latency for each endpoint, error rate (4xx and 5xx), and resource utilization on the server (CPU, memory, DB connection pool saturation, Redis memory). During a load test you are looking for the point where latency starts climbing non-linearly — that is your saturation point. A common mistake is only running one endpoint — test the realistic mix of traffic, because a cache-warming read and a write-heavy endpoint have very different performance profiles.

</details>

<br>

**Q9: What is contract testing (Pact) and how does it differ from integration testing?**

<details>
<summary>💡 Show Answer</summary>

Integration testing runs both the consumer (client) and provider (API) together and verifies they communicate correctly. This requires both services to be available at test time, which is slow and requires coordinated deployments.

Contract testing decouples the two. The consumer team records a pact — a description of the requests they make and the responses they expect — and publishes it to a Pact broker. The provider runs these pacts against their own code in isolation, without the real consumer. Each side can deploy independently as long as both sides pass their contract tests.

The benefit is catching breaking changes early without running the full stack. The trade-off is maintenance: pacts must be kept current and the Pact broker infrastructure must be maintained. Contract testing is most valuable when multiple consumer teams depend on a shared API — it prevents the provider team from unknowingly breaking consumers with each deployment.

</details>

<br>

**Q10: How do you test pagination in a list endpoint thoroughly?**

<details>
<summary>💡 Show Answer</summary>

Pagination testing needs to cover several cases beyond the happy path. First, seed the test database with a known number of records (e.g., 25 records with page size 10). Then verify: first page returns 10 items with has_next=true and correct next cursor or next page link; second page returns 10 items; third page returns 5 items with has_next=false. Verify that the items across all pages are non-overlapping and together equal all 25 seeded records.

Edge cases: empty result set (0 records — returns empty data array with has_next=false, not a 404); exactly one page of results (25 records, page size 25 — has_next=false); requesting a page beyond the last page (returns empty data, not a 404 or 500). For cursor pagination, also test that providing a stale or invalid cursor returns a 400 with a clear error message rather than silently returning wrong results.

</details>

<br>

---

# 🔹 Advanced Level Questions (5+ Years)

**Q11: How would you design a test suite for a multi-tenant API where data isolation between tenants is critical?**

<details>
<summary>💡 Show Answer</summary>

The core requirement is verifying that tenant A cannot read or modify tenant B's data under any circumstances — not just through normal flows but through URL manipulation, token reuse, and race conditions.

Test design: create two tenant fixtures (tenant_a with users and data, tenant_b with users and data). For every endpoint that returns or modifies tenant-scoped data, write a cross-tenant test: authenticate as a tenant A user and attempt to access tenant B's resource IDs directly. The response should be 403 or 404 — never 200 with B's data. Test bulk endpoints too — a "get all orders" endpoint should never return orders from another tenant even if the query parameter is manipulated. Also test token reuse: a JWT issued to tenant A should not grant access to tenant B's namespace even if the path is correct.

In CI, run these tests in an isolated database transaction or schema per test to prevent tenant data leakage between tests themselves. A test that seeds tenant B's data and fails before cleanup could contaminate the next test run.

</details>

<br>

**Q12: What is property-based testing with Hypothesis and when does it catch bugs that example-based tests miss?**

<details>
<summary>💡 Show Answer</summary>

Property-based testing generates hundreds of random inputs automatically and checks that invariants hold for all of them. With Hypothesis you define the shape of valid inputs using strategies (integers in a range, strings matching a pattern, lists of a certain length) and assert a property that must always be true.

Example-based tests check the cases you thought of. Property-based tests find the cases you did not think of — especially boundary conditions and combinations. Common bugs caught: an API that handles price=0 correctly but crashes on price=-0.0 (floating point edge case), a pagination handler that works for all page sizes except 1, a search endpoint that hangs on inputs with only whitespace. For API testing, Hypothesis pairs well with Pydantic — generate valid model instances and verify that round-trip serialization/deserialization is lossless. It also works well for testing idempotency: generate a random valid request, call the endpoint twice with the same input, assert the response is identical and the database state is the same.

</details>

<br>

**Q13: How do you test auth token expiry and refresh token rotation in an automated test suite?**

<details>
<summary>💡 Show Answer</summary>

The challenge is that real token expiry requires waiting (15 minutes for an access token). The solution is to make the token expiry configurable via dependency injection and override it in tests to a very short duration (1 second) or to generate pre-expired tokens.

To generate an expired token: call jwt.encode with an exp claim set to a past timestamp. Use this token to call a protected endpoint and assert 401. For refresh token rotation: call the refresh endpoint with a valid refresh token, assert you receive a new access token and a new refresh token, then attempt to use the old refresh token again and assert 401 (token replay attack rejected). Testing token type enforcement: generate an access token and use it on the /token/refresh endpoint — should return 401 because a token with type="access" cannot be used as a refresh token. These tests verify the security properties that are easy to forget when only testing the happy path.

</details>

<br>

**Q14: How would you approach testing an API that calls three downstream services, where any one can fail independently?**

<details>
<summary>💡 Show Answer</summary>

The test matrix is each downstream service failing independently, in combination, and all together. With three services (payment, inventory, notifications) that is 7 failure combinations plus the success case — 8 tests minimum per endpoint.

Use a mock factory pattern: a fixture that takes a dict of service name to "success" or "fail" and configures all mocks accordingly. This makes the tests readable and the failure scenario explicit. For each failure case assert: the response status code, the error code in the response body, and which partial state was left (did the payment go through before inventory failed? is it rolled back?). Circuit breaker behavior needs its own tests — verify that after 5 consecutive failures the breaker opens and subsequent calls fail fast without hitting the mock, then verify the half-open probe behavior after the reset timeout. Use time mocking (freezegun) rather than sleeping in these tests to keep them fast.

</details>

<br>
