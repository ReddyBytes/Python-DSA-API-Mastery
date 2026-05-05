# 99 — API Interview Master

> Common API design interview questions with model answers — Junior through Senior level.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
REST definition · PUT vs PATCH · idempotency · status code semantics · auth vs authz

**Should Learn** — Important for real projects, comes up regularly:
URL shortener design · pagination comparison · API versioning · distributed rate limiting

**Good to Know** — Useful in specific situations, not always tested:
GraphQL vs REST trade-offs · backward compatibility at scale

**Reference** — Know it exists, look up syntax when needed:
Stripe-style API design · Twitter API design patterns

---

## How to Use This

These are not essay prompts. Interviewers want to see that you understand the concepts, the trade-offs, and can reason under pressure. For each question, the model answer gives you the key points to hit. Expand on them conversationally — don't recite them.

---

## Junior Level

---

### What is REST? What makes an API RESTful?

REST (Representational State Transfer) is an architectural style for designing networked APIs, described by Roy Fielding in his 2000 dissertation.

Key constraints that make an API RESTful:

- **Client-server separation** — the client and server evolve independently
- **Statelessness** — every request contains all information needed to process it; the server holds no session state between requests
- **Uniform interface** — resources are identified by URLs; representations (JSON, XML) are separate from the resource itself; actions are expressed via HTTP methods
- **Layered system** — a client doesn't know if it's talking to the real server, a load balancer, or a cache
- **Cacheability** — responses indicate whether they can be cached

Most "REST" APIs in the real world are actually REST-ish — they use HTTP verbs and JSON but don't fully implement HATEOAS (hypermedia links in responses). That's fine. When an interviewer asks "is this RESTful?", the key points are statelessness, resource-based URLs, and proper use of HTTP verbs and status codes.

---

### What is the difference between PUT and PATCH?

**PUT** replaces the entire resource. If you send `PUT /users/42` with `{"name": "Alice"}`, and the user previously had `email`, `role`, and `name` fields, the resulting resource has only `name`. Everything else is gone (or reset to defaults).

**PATCH** applies a partial update. Send only the fields you want to change. `PATCH /users/42` with `{"name": "Alice"}` updates only the name; all other fields remain unchanged.

**Idempotency:** Both should be idempotent — calling them multiple times with the same data produces the same result.

**When to use which:**
- Use PUT when the client is replacing the entire resource (e.g., uploading a file)
- Use PATCH for partial updates (e.g., changing one field in a form)
- PATCH is more common in modern APIs because clients rarely want to send the entire resource

---

### What HTTP status code do you return when a resource is created?

`201 Created`.

Also include a `Location` header pointing to the new resource:

```
HTTP/1.1 201 Created
Location: /users/42
Content-Type: application/json

{"id": 42, "email": "alice@example.com"}
```

Common mistakes: returning `200 OK` for a creation (technically wrong — use 201), or returning `201` for an update (use `200`).

---

### What is idempotency? Give an example.

An operation is idempotent if applying it multiple times has the same effect as applying it once.

HTTP method idempotency:
- `GET` — idempotent (reading doesn't change state)
- `PUT` — idempotent (replacing a resource with the same data always results in the same state)
- `DELETE` — idempotent (deleting something that's already deleted is still "deleted" — return 404 but don't error catastrophically)
- `POST` — NOT idempotent by default (submitting an order twice creates two orders)
- `PATCH` — depends on implementation (setting `status = "shipped"` is idempotent; incrementing `quantity += 1` is not)

**Practical example:** A payment API must be idempotent. If a client sends a payment request and the network times out before receiving a response, they can't know if the payment was processed. If they retry and it's not idempotent, the customer gets charged twice. The solution: the client sends an `Idempotency-Key` header (a unique UUID per payment attempt). The server stores the key and the result. On retry, it returns the stored result without reprocessing.

---

### What is the difference between authentication and authorization?

**Authentication** — who are you? Verifying identity. "This request is from user ID 42."

**Authorization** — what are you allowed to do? Verifying permissions. "User 42 is allowed to read orders but not delete users."

HTTP status codes reflect this distinction:
- `401 Unauthorized` — actually means "unauthenticated." You haven't proved who you are.
- `403 Forbidden` — you are authenticated, but you don't have permission to do this.

**Example:** You call `DELETE /admin/users/1` with a valid JWT token. The server confirms who you are (authentication) — but your token has role: `user`, not role: `admin`. You get `403 Forbidden` (authorization failure), not `401`.

Common mechanisms:
- Authentication: API keys, JWT tokens, OAuth2 access tokens, session cookies
- Authorization: Role-based access control (RBAC), scope-based (OAuth2 scopes), attribute-based (ABAC)

---

## Mid Level

---

### Design the API for a URL shortener (create, redirect, analytics)

Core resources and endpoints:

```
POST   /links              — create a short link
GET    /{code}             — redirect to original URL (301 or 302)
GET    /links/{code}       — get link metadata (no redirect)
DELETE /links/{code}       — delete a link
GET    /links/{code}/stats — analytics for a link
```

**Creating a short link:**
```
POST /links
Body: {"url": "https://example.com/very/long/path", "custom_code": "mylink"}
Response 201: {"code": "mylink", "short_url": "https://sho.rt/mylink", "created_at": "..."}
```

**Redirect behavior:**
- `301 Moved Permanently` — cached by browsers; good for throughput, bad for analytics accuracy
- `302 Found` — not cached; every request hits your server; better for analytics
- Most URL shorteners use `302` so they can count clicks accurately

**Analytics endpoint:**
```
GET /links/mylink/stats?period=7d
Response: {
  "code": "mylink",
  "total_clicks": 1042,
  "unique_visitors": 831,
  "clicks_by_day": [...],
  "top_referrers": [...],
  "top_countries": [...]
}
```

Design considerations to mention:
- Rate limiting on `POST /links` to prevent abuse
- The `{code}` namespace conflicts with `/links/` — use a subdomain (`sho.rt/{code}`) or prefix (`/r/{code}`)
- Short code generation: random base62 (6 chars = 57 billion possibilities) vs sequential IDs
- Analytics data is eventually consistent — don't promise real-time counts

---

### How do you handle pagination in a REST API? Compare cursor vs offset.

**Offset pagination** — `?page=2&limit=20` or `?offset=40&limit=20`

```
GET /orders?offset=40&limit=20
Response: {
  "data": [...],
  "total": 342,
  "offset": 40,
  "limit": 20
}
```

Pros: easy to implement, easy to jump to arbitrary pages ("go to page 5 of 17")
Cons: if items are inserted or deleted between pages, you get duplicates or skip items. Heavy on the database for deep pages (`OFFSET 10000` scans 10,000 rows to discard them).

**Cursor pagination** — `?cursor=<opaque_token>&limit=20`

```
GET /orders?limit=20
Response: {
  "data": [...],
  "next_cursor": "eyJpZCI6IDIwfQ==",  // base64 encoded {id: 20}
  "has_more": true
}

GET /orders?cursor=eyJpZCI6IDIwfQ==&limit=20
```

The cursor encodes the position in the dataset (usually the last seen ID, or a timestamp+ID pair). The query becomes `WHERE id > 20 LIMIT 20` — always fast, regardless of depth.

Pros: consistent results even when data changes, efficient at any depth, safe for infinite scroll
Cons: cannot jump to an arbitrary page, cursor is opaque (can't tell users "page 5 of 17")

**Rule of thumb:** Use cursor pagination for large datasets, real-time feeds, and infinite scroll. Use offset when users need to jump to specific pages (admin UIs, search results with page numbers).

---

### When would you use GraphQL over REST?

Use GraphQL when:

- **You have multiple clients with different data needs.** A mobile app needs a summary, a desktop app needs full details, and a dashboard needs aggregated stats — all from the same data. REST over-fetches or under-fetches. GraphQL lets each client specify exactly what it needs.
- **You have a complex, interconnected domain.** Social graphs, CMS systems, e-commerce catalogs with many relationship types. GraphQL's nested queries naturally express these.
- **You are building a BFF (Backend for Frontend) layer** that aggregates data from multiple microservices into a single query.

Stick with REST when:
- You have a simple CRUD API
- You need HTTP caching (GraphQL uses POST for everything, which is not cacheable by default)
- You are building a public API (REST is more universally understood)
- File upload, real-time push, or binary data is a core requirement

The decision is not REST vs GraphQL — it is: does a flexible query language provide enough value to justify the added complexity of a schema, resolvers, and a DataLoader pattern to avoid N+1 queries?

---

### How do you version an API without breaking existing clients?

Three steps:

1. **Be precise about what is a breaking change.** Removing or renaming fields, changing types, removing endpoints — these are breaking. Adding fields or endpoints is not.

2. **Choose a versioning strategy.** URL versioning (`/v1/`, `/v2/`) is the standard default. Implement it in your router so both versions can run simultaneously. The old version is maintained until its sunset date.

3. **Deprecate before you remove.** Add `Deprecation: true` and `Sunset: <date>` response headers when you decide something will be retired. Publish a migration guide. Give at least 6 months for public APIs. Monitor who is still using the deprecated version and notify them.

The most important thing to say in an interview: versioning is a social/process problem as much as a technical one. The technical mechanism is trivial. The hard part is communicating, committing to a timeline, and actually turning off the old version.

---

### Design rate limiting for a public API. How do you handle distributed rate limiting?

**On a single server**, rate limiting is a sliding window or token bucket stored in memory per client API key.

For a distributed system (multiple API servers behind a load balancer), you cannot use local memory — a client can hit different servers on each request and bypass per-server limits.

**Distributed rate limiting with Redis:**

```
On each request:
1. Key: "rate_limit:{api_key}:{window}" (window = current minute)
2. INCR the key in Redis
3. SET TTL to 60 seconds on first increment
4. If count > limit → return 429 Too Many Requests
```

This works because Redis is a single shared store with atomic INCR operations.

Return useful headers so clients can implement backoff correctly:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 47
X-RateLimit-Reset: 1706180460
Retry-After: 37
```

**Algorithms to mention:**
- **Fixed window** — simple, but allows burst at window boundaries (1000 requests in last second of window + 1000 in first second of next = 2000 in a 2-second span)
- **Sliding window** — more accurate, counts requests in the true last N seconds
- **Token bucket** — allows controlled bursting up to a bucket size; replenishes at a fixed rate; used by most production systems

**Differentiated limits:** Rate limit by API key, not IP (proxies, NAT). Offer different tiers: free = 100/hour, paid = 10,000/hour, enterprise = custom. Exempt internal services or give them a very high limit.

---

## Senior Level

---

### Design the Stripe payment API. What makes Stripe's API design excellent?

**Core resources:**
```
POST /v1/payment_intents          — create a payment intent
POST /v1/payment_intents/{id}/confirm  — confirm/charge
POST /v1/refunds                  — issue a refund
GET  /v1/charges/{id}             — get charge details
POST /v1/customers                — create a customer
POST /v1/payment_methods          — tokenize card data
```

**What Stripe gets right:**

The Payment Intent object is the key insight. Rather than a single "charge the card" call, Stripe models the entire payment lifecycle as a state machine: `requires_payment_method` → `requires_confirmation` → `requires_action` → `processing` → `succeeded` / `canceled`. This handles 3D Secure, bank redirects, and asynchronous payment methods elegantly with a single API shape.

**Idempotency keys** — every write operation accepts `Idempotency-Key: <uuid>`. The server stores the result for 24 hours. If you retry due to a network timeout, you get the stored result, not a double charge. This is essential for payment APIs.

**Webhook design** — Stripe pushes events (webhooks) for every state transition. Clients should never poll. Stripe signs webhooks with HMAC so you can verify authenticity.

**Developer experience** — test mode/live mode separation with different key prefixes. Test card numbers for every failure scenario. The error object has a machine-readable `code`, a `decline_code`, and a human `message`.

**The broader lesson for interviews:** Stripe's API is excellent because it models the business domain accurately (payments are state machines, not simple transactions), it handles failure modes explicitly (idempotency, webhooks), and the developer experience is treated as a product.

---

### How do you design an API that supports both synchronous and asynchronous operations?

Some operations complete in milliseconds (synchronous). Others take seconds or minutes — sending a bulk email, generating a report, processing a video (asynchronous). A good API handles both without forcing synchronous timeouts.

**Pattern: Polymorphic response based on completion time**

For fast operations: respond with the result directly.

For slow operations: accept the request, return `202 Accepted` with a job/operation resource, and let the client poll or receive a webhook.

```
POST /reports
→ 202 Accepted
{
  "operation_id": "op_abc123",
  "status": "pending",
  "status_url": "/operations/op_abc123"
}

GET /operations/op_abc123
→ 200 OK
{
  "id": "op_abc123",
  "status": "running",    // pending → running → succeeded → failed
  "progress": 42,
  "result_url": null
}

GET /operations/op_abc123  (later)
→ 200 OK
{
  "id": "op_abc123",
  "status": "succeeded",
  "result_url": "/reports/rpt_xyz789"
}
```

**Push alternative:** Instead of polling, accept a `webhook_url` in the original request. Call it when the operation completes. Or use WebSockets / Server-Sent Events for real-time progress.

**Design considerations:**
- Make the synchronous/async threshold transparent — document which endpoints are async
- Operations should be idempotent — clients will retry on timeout
- Store operation state persistently — a server restart shouldn't lose it
- Set a TTL on completed operations (don't store results forever)
- Return estimated completion time when possible: `"estimated_seconds": 30`

---

### Design the Twitter API. What are the trade-offs in your design?

**Core resources:**
```
POST /tweets                      — post a tweet
GET  /tweets/{id}                 — get a tweet
DELETE /tweets/{id}               — delete a tweet
GET  /users/{id}/timeline         — user's own tweets
GET  /users/{id}/home_timeline    — feed (people you follow)
POST /users/{id}/follow           — follow a user
POST /tweets/{id}/like            — like a tweet
POST /tweets/{id}/retweets        — retweet
GET  /search/tweets?q=...         — search tweets
```

**The hard design problems to discuss:**

**Home timeline (fan-out problem)** — when someone with 10M followers posts, do you write to all 10M follower feeds immediately (fan-out on write), or compute each user's feed on read (fan-out on read)?

- Fan-out on write: writes are expensive at celebrity scale; reads are fast
- Fan-out on read: writes are cheap; reads are expensive (aggregate from everyone you follow)
- Twitter's actual approach: hybrid — fan-out on write for most users, fan-out on read for celebrities, cached timelines

**Search** — tweets require near-real-time search. This is typically a separate Elasticsearch/Lucene cluster, not your primary DB. The search API is a different system from the timeline API.

**Rate limits** — Twitter's public API is heavily rate limited because the data has value. Rate limits are per token, per endpoint, per 15-minute window.

**Pagination** — use cursor pagination with `since_id` and `max_id` (tweet IDs are time-ordered snowflakes). This handles the real-time insertion problem cleanly.

**Trade-offs to articulate:** consistency vs availability in a distributed feed, storage cost of fan-out vs compute cost of fan-in, the impossibility of a truly real-time globally consistent timeline.

---

### How would you design an API that can handle idempotent payment processing?

The core problem: a client sends a payment request. The network times out. The client doesn't know if the payment succeeded. If they retry without idempotency, the customer is charged twice.

**Solution: client-generated idempotency keys.**

The client generates a UUID for each payment attempt and sends it in the header:

```
POST /payments
Idempotency-Key: a1b2c3d4-e5f6-7890-abcd-ef1234567890

{"amount": 2000, "currency": "usd", "card_token": "tok_visa"}
```

The server:
1. Checks if this key has been seen before
2. If yes: return the stored response (do not process again)
3. If no: process the payment, store `(key → result)` atomically, return the result

**Implementation details:**
- Store idempotency keys in Redis with a 24-hour TTL (keys are per-customer, not global)
- The storage must be atomic with the payment processing — use a database transaction or two-phase approach
- If the original request is still in-flight and you receive a retry, return `409 Conflict` (or wait)
- The idempotency key is scoped to the customer/API key, not global

**Database-level idempotency for distributed systems:**

For payments that go through an external processor (Stripe, etc.), you also need idempotency at the processor level. Stripe's API accepts its own idempotency key — forward your key or derive one from it.

**Additional safeguards:**
- Unique constraint on `(customer_id, idempotency_key)` in the DB
- Two-phase processing: mark a payment as "in progress" before charging, then mark as "complete" — prevents duplicate processing even under race conditions

---

### How do you manage backward compatibility across API versions in a large team?

In a large team, the biggest risk is not "someone decided to make a breaking change" — it is "someone made a breaking change without realizing it."

**Tooling and process:**

**OpenAPI as the source of truth.** The API spec lives in source control. Every API change starts with a spec change. PRs that modify the spec require review from a platform or API governance team.

**Breaking change detection in CI.** Tools like `openapi-diff` or `oasdiff` compare the current spec against the previous version and fail the pipeline if breaking changes are detected without a version bump.

```bash
# In CI:
oasdiff breaking openapi-v1.yaml openapi-proposed.yaml --fail-on ERR
```

**Contract tests in CI.** Pact or similar — every consumer publishes a contract, every provider runs verification. A provider change that breaks a consumer contract fails the pipeline before it merges.

**Versioning discipline:**
- Increment the minor version for non-breaking additions
- Increment the major version for breaking changes, which triggers the deprecation process
- Automated tools prevent the "I forgot to bump the version" mistake

**Communication:**
- API changelog is generated from OpenAPI diffs, not written by hand
- Breaking changes are announced in a developer newsletter, Slack channel, and the dashboard
- Each API key shows which version it is pinned to; developers receive deprecation warnings in the console

**The cultural part to mention:** Backward compatibility in large teams is a cultural norm enforced by tooling. The conversation to have is: "We never make breaking changes without a version bump" should be as automatic as "we never push directly to main." The tooling makes the norm enforceable.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← OpenTelemetry](../19_opentelemetry/opentelemetry_guide.md) &nbsp;|&nbsp; **Next:** —

**Related Topics:** [REST Best Practices](../03_rest_best_practices/patterns.md) · [Authentication & Authorization](../05_authentication/securing_apis.md) · [GraphQL](../13_graphql/graphql_story.md) · [Real-World Architectures](../18_real_world_apis/architectures.md)
