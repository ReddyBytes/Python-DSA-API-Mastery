# REST Best Practices

## The Gap Between "Works" and "Good"

You can build an API that works while breaking every rule in this document. Requests
come in, data goes out, everyone's happy. For a while.

Then your API grows. Other teams start integrating with it. Mobile apps start depending
on it. You try to make a change and realize you can't because you'll break the iOS app.
You get a bug report: "your error messages are inconsistent and we can't tell what went
wrong." You get a performance complaint: "your endpoint returns 50 fields but we only
need 3."

The rules in this document exist because people built APIs, those APIs got used, they
discovered pain points, and they agreed on conventions to avoid those pain points. This
isn't theory. These are scars.

Let's go through them.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
URL naming conventions (lowercase/hyphens/plural nouns) · pagination (offset vs cursor) · error response structure · versioning strategies

**Should Learn** — Important for real projects, comes up regularly:
filtering and sorting safety · idempotency keys · HTTP caching headers (ETag/Cache-Control)

**Good to Know** — Useful in specific situations, not always tested:
sparse fieldsets · rate limiting headers · response envelopes

**Reference** — Know it exists, look up syntax when needed:
request signing · response compression · backward compatibility testing

---

## 1. URL Naming Rules

URLs are the public face of your API. They're what developers type into their code,
what shows up in logs, what gets bookmarked and shared. They should be clean,
predictable, and boring.

### Use lowercase

```
Good:   GET /users/42
Bad:    GET /Users/42
Bad:    GET /USERS/42
```

URLs are technically case-sensitive (RFC 3986). `/Users/42` and `/users/42` are
different URLs. Use lowercase everywhere, always. No exceptions. You don't want your
API to fail because someone Shift-typed a character.

### Use hyphens, not underscores

```
Good:   GET /payment-methods
Bad:    GET /payment_methods
Bad:    GET /paymentMethods
```

Why hyphens? Because underscores can be hidden by link underlines in browsers and some
docs renderers. Because hyphens are how human language separates words (`first-class`,
`two-factor`). Because search engines treat hyphen-separated words as separate words,
which matters for discoverability. Underscores read as a single token to search engines.

Camel case is especially bad in URLs — it requires developers to remember capitalization,
which is unnecessary cognitive load.

### Use plural nouns for collections

```
Good:   GET /users
Good:   GET /products
Good:   GET /payment-methods

Bad:    GET /user
Bad:    GET /product
Bad:    GET /paymentMethod
```

Collections are plural. Always. Yes, even when it feels weird
(`GET /media`, not `GET /medium`). Consistency beats correctness in naming.

The one exception where people debate: singleton resources. If there's only ever one
of something per user, you might see `GET /me` or `GET /settings` (singular). This is
acceptable.

### No verbs in URLs

```
Good:   DELETE /users/42
Good:   PATCH  /users/42
Good:   POST   /users

Bad:    POST /deleteUser
Bad:    POST /updateUser?id=42
Bad:    GET  /getUsers
Bad:    GET  /fetchProductById/42
```

The HTTP method is the verb. The URL is the noun. When you put verbs in URLs, you end
up with RPC-style APIs that aren't REST. You lose the predictability that makes REST
valuable.

### Avoid deeply nested URLs

```
Good:   GET /users/42/orders
Good:   GET /orders/7/items

Bad:    GET /users/42/orders/7/items/3/attachments
```

Maximum two levels of nesting. Beyond that, it gets unwieldy and usually indicates a
design problem. If you need `GET /users/42/orders/7/items/3`, ask whether
`GET /items/3` (with user and order IDs returned in the item object) is cleaner.

Nesting is appropriate when the child resource doesn't make sense without the parent
context. Otherwise, prefer a flat structure with filtering:

```
Instead of:   GET /users/42/orders/7/items
Use:          GET /items?order_id=7
```

### Version your API in the URL

```
GET /v1/users/42
GET /v2/users/42
```

More on versioning in the next section. The short answer: put `v1` at the start of
every URL path.

---

## 2. Versioning — The Eternal Debate

Your API will change. You will need to add fields, change behavior, rename things,
break backwards compatibility. The question isn't whether you'll need to version your
API — it's how.

There are two main approaches:

### URL Versioning

```
GET /v1/users/42
GET /v2/users/42
POST /v1/payments
```

The version is in the URL path. This is the most common approach.

**Why people use URL versioning:**
- Visible and explicit. You can see which version you're calling.
- Easy to test in a browser — just change the URL.
- Cache-friendly — `/v1/users/42` and `/v2/users/42` are different cache keys.
- Easy to route in your infrastructure — different URL prefixes can go to different
  services or handlers.
- Developers can run v1 and v2 side by side simultaneously.

**The argument against it:**
Purists say URLs should identify resources, not versions. `/users/42` is the user
regardless of version. Changing the URL for a version change violates the idea that
the URL is a stable identifier.

The purists are not wrong. But pragmatism wins here. URL versioning is what most APIs
use because it's the most practical.

### Header Versioning

```
GET /users/42
Accept: application/vnd.myapi.v2+json
```

Or with a custom header:
```
GET /users/42
API-Version: 2024-01-01
```

The version is in a header, not the URL.

**Why some APIs use header versioning:**
- "Cleaner" URLs — the resource identifier doesn't change.
- The URL `/users/42` always refers to user 42.
- Stripe does this with a date-based version header (`Stripe-Version: 2024-06-20`).
- GitHub uses `Accept: application/vnd.github.v3+json`.

**The argument against it:**
You can't test it in a browser by just typing a URL. You need to remember to include
the header in every single request. Caches don't differentiate by default (you have to
use `Vary: Accept` to make it work correctly with CDNs). It's less visible.

### Recommendation

**Use URL versioning unless you have a strong reason not to.**

If you're building a public API that will be used by many developers, URL versioning
is the safe choice. It's immediately visible, easy to test, and what developers expect.

```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

A few practical guidelines:
- Start at `v1`. Not `v0`. Not `v2024-01-01`. Just `/v1`.
- Never break backwards compatibility within a version. If you need to break something,
  create `v2`.
- Keep old versions alive long enough for clients to migrate — at minimum 6 months,
  ideally 1-2 years for public APIs. Give deprecation warnings in headers.
- A deprecation warning header is helpful:
  ```
  Deprecation: true
  Sunset: Sat, 01 Jan 2025 00:00:00 GMT
  Link: <https://api.example.com/v2/users>; rel="successor-version"
  ```

**When does versioning matter?** At scale. If you're building an internal API used by
one team, don't overthink it. If you're building a public API or an API shared across
multiple teams, version from day one. It's much harder to add later.

---

## 3. Pagination — Don't Return 1 Million Rows

Never return an unbounded list. Ever. If your database has 500,000 users and someone
calls `GET /users`, you do not return all 500,000 in one response.

You return a page. And you tell the client how to get the next page.

### Offset Pagination

The simple approach:

```
GET /users?page=2&limit=20
GET /users?offset=40&limit=20  (same thing, different naming)
```

The server calculates: `skip (page-1)*limit rows, return limit rows`.

**The response:**

```json
{
  "data": [
    {"id": 21, "name": "User 21"},
    {"id": 22, "name": "User 22"},
    ...20 items total...
  ],
  "pagination": {
    "total": 500,
    "page": 2,
    "limit": 20,
    "total_pages": 25,
    "has_next": true,
    "has_prev": true
  }
}
```

**Why offset pagination is fine for most cases:**
Simple to implement. Simple to understand. Users can jump to a specific page. Easy
to display "page 3 of 25" in a UI.

**Why offset pagination breaks at scale:**

Imagine a news feed. You're on page 3. You've seen items 41-60.

While you were reading, 3 new items were published at the top.

You go to page 4. But now the items have shifted — what was item 61 (the first item
on page 4) is now item 64 because 3 new items pushed everything down. You'll see
items 64-83, missing items 61-63 entirely. Or if items were deleted, you'll see
duplicates across pages.

This is the **page shift problem**. It's real and annoying.

### Cursor Pagination

The scalable approach:

```
GET /users?limit=20
GET /users?after=eyJpZCI6MjB9&limit=20   ← second page
GET /users?after=eyJpZCI6NDB9&limit=20   ← third page
```

The `after` parameter is a **cursor** — an opaque token that encodes a position in the
dataset. The server knows "return the 20 items that come after this position."

The cursor is usually a base64-encoded JSON object containing the sort key:
`eyJpZCI6MjB9` decodes to `{"id": 20}`. The client doesn't need to know this.

**The response:**

```json
{
  "data": [
    {"id": 21, "name": "User 21"},
    {"id": 22, "name": "User 22"},
    ...20 items total...
  ],
  "pagination": {
    "has_next": true,
    "has_prev": true,
    "next_cursor": "eyJpZCI6NDB9",
    "prev_cursor": "eyJpZCI6MjF9"
  }
}
```

**Why cursor pagination is better at scale:**
- Stable: new items added to the top don't affect your position
- Performant: the database query uses an indexed column (`WHERE id > 20 LIMIT 20`)
  instead of `OFFSET 40` which requires scanning and discarding 40 rows
- Works consistently regardless of data size

**Why cursor pagination is annoying:**
- Can't jump to page 47 — you can only go forward/backward
- Hard to display "page X of Y" (you don't know the total without a COUNT query)
- Cursors expire if the sort order changes

**Rule of thumb:**
- Use **offset pagination** for admin dashboards, reports, anything with "jump to page"
- Use **cursor pagination** for feeds, timelines, anywhere items are added frequently,
  or very large datasets (100k+ rows)

---

## 4. Filtering and Sorting

### Filtering

Filtering goes in query parameters:

```
GET /orders?status=pending
GET /orders?status=pending&customer_id=42
GET /products?category=electronics&min_price=100&max_price=500
GET /users?role=admin&active=true&created_after=2024-01-01
```

Keep filter parameter names clear and consistent:
- Use the field name directly when possible: `?status=pending` not `?filter_status=pending`
- For range filters, use `min_` and `max_` prefixes, or `_after` / `_before` for dates
- For boolean fields, use `true` and `false` strings: `?active=true`

**Be thoughtful about what you allow filtering on.** Every filter you support has to be
efficiently queryable in your database. If you let users filter on an unindexed column,
you'll get full table scans. Only expose filters you can back with proper indexes.

### Sorting

```
GET /products?sort=price              → ascending by default
GET /products?sort=price&order=asc    → explicitly ascending
GET /products?sort=price&order=desc   → descending
GET /products?sort=-price             → alternative: minus sign for descending
```

There's no universal standard. Pick one convention and be consistent.
Many APIs use `sort=-created_at` (minus for descending, no minus for ascending).
Others use `sort=created_at&order=desc`. Both work. Pick one.

**Multiple sort fields:**
```
GET /products?sort=category,price        → sort by category, then price
GET /products?sort=category,-price       → sort by category asc, price desc
```

### Sparse Fieldsets

Return only the fields the client asked for:

```
GET /users?fields=id,name,email
```

Response only includes those three fields, not the full user object.

This matters when:
- Your resource has many fields but the client only needs a few
- Mobile clients want to minimize response size
- Some fields are expensive to compute and not always needed

It's extra implementation work on the server side (you need to parse the `fields`
parameter and selectively serialize), so it's optional for most APIs. But for large
responses or high-traffic endpoints, it can meaningfully reduce bandwidth.

---

## 5. Error Response Design

This is where many APIs get lazy, and it costs their users hours of debugging.

Bad error response:

```json
{"error": "invalid input"}
```

What was invalid? Which field? What exactly is wrong? How should I fix it? This tells
you nothing useful.

Good error response:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "must be a valid email address",
        "value": "not-an-email"
      },
      {
        "field": "age",
        "message": "must be at least 18",
        "value": 15
      }
    ]
  }
}
```

The three layers of a good error response:

### 1. Machine-readable error code

```json
"code": "VALIDATION_ERROR"
```

A string constant your clients can switch on. Not a number (numbers are opaque).
Not the HTTP status code (that's already in the response). A specific, stable
identifier for the error type.

Common error codes:
```
VALIDATION_ERROR        → request data failed validation
AUTHENTICATION_REQUIRED → no valid token provided
PERMISSION_DENIED       → authenticated but not authorized
NOT_FOUND               → resource doesn't exist
CONFLICT                → would create a duplicate (e.g., email already taken)
RATE_LIMIT_EXCEEDED     → too many requests
INTERNAL_ERROR          → something broke on our end
```

Your clients can handle these in code:
```python
if error["code"] == "RATE_LIMIT_EXCEEDED":
    time.sleep(retry_after)
    retry()
elif error["code"] == "AUTHENTICATION_REQUIRED":
    refresh_token()
    retry()
```

### 2. Human-readable message

```json
"message": "Request validation failed"
```

For developers reading logs and error messages. Should be clear and helpful. Can
include context. But should not include internal system details (stack traces, SQL
queries, server paths) in production.

### 3. Field-level details for validation errors

```json
"details": [
  {"field": "email", "message": "must be a valid email address"},
  {"field": "age", "message": "must be at least 18"}
]
```

When validation fails, tell the client exactly which fields failed and why. This
allows form UIs to highlight specific fields. This allows developers to fix exactly
the right thing. This saves everyone time.

The `field` name should match the field name in the request body exactly. No surprises.

---

## 6. Consistent Response Envelope

Your API's response structure should be consistent. Every response should have the same
shape. No surprises.

Here's a simple convention:

**Single resource:**
```json
{
  "data": {
    "id": 42,
    "name": "Alice",
    "email": "alice@example.com"
  }
}
```

**Collection:**
```json
{
  "data": [
    {"id": 42, "name": "Alice"},
    {"id": 43, "name": "Bob"}
  ],
  "meta": {
    "total": 153,
    "page": 2,
    "limit": 20
  }
}
```

**Error:**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "User with ID 42 not found"
  }
}
```

**Why the `data` wrapper?**

Without the wrapper, a collection response would be a bare array:
```json
[{"id": 42, ...}, {"id": 43, ...}]
```

This looks fine until you need to add pagination metadata. You can't add `total` to
a bare array without breaking the response structure. With the `data` wrapper, you can
always add `meta` or `pagination` fields alongside `data` without any changes for
existing clients.

Pick a convention. Document it. Use it everywhere. Consistency dramatically reduces
the number of questions and bugs from API consumers.

---

## 7. Idempotency Keys — For Safe Retries on Non-Idempotent Operations

We established in the REST fundamentals module that POST is not idempotent. Call
`POST /payments` twice, charge the customer twice. That's a real problem.

Idempotency keys solve this:

```
POST /payments
Content-Type: application/json
Authorization: Bearer eyJhb...
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000

{
  "amount": 5000,
  "currency": "usd",
  "customer_id": 42
}
```

Here's how it works:

```
1. Client generates a unique key (UUID) for this operation.
2. Client sends the request with Idempotency-Key header.
3. Server processes the request and stores the response, keyed by the idempotency key.
4. Server returns the response.

If the connection drops and the client retries:

5. Client resends the exact same request with the same Idempotency-Key.
6. Server looks up the key — finds a stored response.
7. Server returns the stored response WITHOUT processing again.
8. Client gets the same response as the first attempt.
```

The customer is charged exactly once, regardless of how many times the client retried.

**Who uses idempotency keys:**
- Stripe requires them for creating charges, setting up subscriptions
- Twilio supports them for sending messages
- Braintree, Adyen, most payment processors support them
- Any API where "running twice = double billing" needs them

**Implementation notes:**
- Keys should be UUIDs (version 4) — random and unique
- Keys are typically scoped to the authenticated user (user A's key doesn't collide
  with user B's)
- Keys expire — usually after 24 hours. After expiry, the same key will process as a
  new request
- If you resend with the same key but a different body, most implementations return
  an error

---

## 8. HTTP Caching — How to Use It Correctly

HTTP has a built-in caching system. Most developers ignore it. That's a missed
opportunity — caching is one of the highest-leverage performance tools you have.

### Cache-Control — The Directive

Tell clients (and CDNs) how long a response is valid:

```
Cache-Control: max-age=3600          → cache for 1 hour (3600 seconds)
Cache-Control: max-age=0             → don't use cache without revalidating
Cache-Control: no-store              → never cache this, ever
Cache-Control: private               → browser can cache, CDNs cannot
Cache-Control: public                → anyone (browser, CDN, proxy) can cache
Cache-Control: public, max-age=86400 → CDNs can cache for 24 hours
```

**Practical guidelines:**
- Static data (product catalog, config): `public, max-age=3600` (1 hour or more)
- User-specific data: `private, max-age=300` (5 minutes, only in browser)
- Sensitive data (auth tokens, financial): `no-store`
- Data that changes frequently: short `max-age` or `no-cache`

### ETags — Conditional Requests

An ETag is a fingerprint (hash) of the response. The server includes it:

```
HTTP/1.1 200 OK
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
Cache-Control: private, max-age=300

{"id": 42, "name": "Alice", ...}
```

The client stores the ETag. On the next request, it asks: "has this changed?":

```
GET /users/42
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"
```

If the data hasn't changed:
```
HTTP/1.1 304 Not Modified
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
(empty body)
```

The server sends no body. The client uses its cached copy. You just saved transferring
the entire response body for free.

If the data has changed:
```
HTTP/1.1 200 OK
ETag: "new_hash_here"
Cache-Control: private, max-age=300

{"id": 42, "name": "Alice Johnson", ...}
```

Full response with the new data and a new ETag.

### Last-Modified — Alternative to ETags

Same concept, but uses a timestamp instead of a hash:

```
Response:
Last-Modified: Tue, 15 Jan 2024 09:30:00 GMT

Next request:
If-Modified-Since: Tue, 15 Jan 2024 09:30:00 GMT

If unchanged → 304 Not Modified
If changed   → 200 OK with new data
```

ETags are more precise (they detect any content change). Last-Modified is simpler to
implement. Either works. ETags are generally preferred.

### Where caching matters most

- High-traffic read endpoints that return the same data to many users
- Product listings, pricing, public content
- Any data that doesn't change per-request
- Mobile clients (where bandwidth and latency matter more)

---

## 9. Rate Limiting Headers

Rate limiting controls how many requests a client can make in a given time window.
Every public API has it. Your API should too.

The convention for communicating rate limit status in response headers:

```
X-RateLimit-Limit: 1000       → max requests per window
X-RateLimit-Remaining: 842    → requests remaining in current window
X-RateLimit-Reset: 1609459200 → Unix timestamp when window resets
```

When the client is rate limited (429 Too Many Requests):

```
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1609459200
Retry-After: 60

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. 1000 requests per hour allowed.",
    "retry_after": 60
  }
}
```

`Retry-After` tells the client exactly how many seconds to wait before trying again.
A well-behaved client reads this and waits, rather than hammering your API.

### What to rate limit on

There are several approaches:
- Per API key / per authenticated user
- Per IP address (for unauthenticated requests)
- Per endpoint (some endpoints are more expensive than others)
- Global (total requests across all users)

Most production systems use **per-user rate limiting** as the primary mechanism. This
ensures one badly-behaved client can't take down the whole service for everyone.

### Handling 429 in client code

```python
import requests
import time

def make_request_with_retry(url, headers, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            continue

        return response

    raise Exception("Max retries exceeded")
```

Always handle 429 gracefully. Never retry immediately on a 429 — that just makes things
worse and most APIs will penalize you for it.

---

## Putting It All Together — A Well-Designed API

Here's what a well-designed endpoint looks like when you apply all these principles:

```
GET /v1/orders?status=pending&customer_id=42&sort=created_at&order=desc&limit=20&after=eyJpZCI6MTAwfQ
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
Accept: application/json
If-None-Match: "abc123"
```

Response (data unchanged — 304):
```
HTTP/1.1 304 Not Modified
Cache-Control: private, max-age=60
ETag: "abc123"
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 998
```

Response (data changed — 200):
```
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: private, max-age=60
ETag: "def456"
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 997

{
  "data": [
    {
      "id": "ord_abc123",
      "status": "pending",
      "customer_id": 42,
      "total": 5999,
      "currency": "usd",
      "created_at": "2024-03-08T14:00:00Z"
    }
  ],
  "pagination": {
    "has_next": true,
    "has_prev": true,
    "next_cursor": "eyJpZCI6NX0=",
    "prev_cursor": "eyJpZCI6MTAxfQ=="
  }
}
```

What makes this good:
- Versioned URL (`/v1/`)
- Lowercase with hyphens (`/orders`)
- Filtering in query params (`status=pending&customer_id=42`)
- Sorting (`sort=created_at&order=desc`)
- Cursor pagination (stable at scale)
- Auth via Bearer token
- ETag for conditional requests
- Rate limit headers in response
- Consistent `data` + `pagination` envelope

---

## Quick Reference Checklist

Use this when reviewing an API design:

```
URL Design:
  [ ] Lowercase
  [ ] Hyphens not underscores
  [ ] Plural nouns for collections
  [ ] No verbs in paths (except action endpoints)
  [ ] Max 2 levels of nesting
  [ ] Versioned (/v1/)

HTTP Verbs:
  [ ] GET for reads, POST for creates
  [ ] PUT for full replacement, PATCH for partial updates
  [ ] DELETE for deletion
  [ ] Correct idempotency expectations documented

Response Codes:
  [ ] 200 for success, 201 for creation
  [ ] 204 for no-content (DELETE)
  [ ] 400 for validation errors
  [ ] 401 for not authenticated
  [ ] 403 for not authorized
  [ ] 404 for not found
  [ ] 429 for rate limited
  [ ] 500 for server errors

Responses:
  [ ] Consistent data envelope
  [ ] Structured error format with code + message + details
  [ ] Pagination for all list endpoints
  [ ] Rate limit headers

Performance:
  [ ] Cache-Control headers on all responses
  [ ] ETag headers for cacheable resources
  [ ] Pagination with sane default limits

Safety:
  [ ] Idempotency keys available for POST operations with side effects
  [ ] Sensitive data has Cache-Control: no-store
  [ ] Retry-After header on 429 responses
```

---

## Summary

```
URL Rules:
  lowercase, hyphens, plural nouns, no verbs, max 2 nesting levels

Versioning:
  Use URL versioning (/v1/) — visible, cache-friendly, easy to test
  Announce deprecations early with Sunset headers

Pagination:
  Offset (?page=2&limit=20) — simple, for most cases
  Cursor (?after=cursor&limit=20) — scalable, for large/live datasets
  Always paginate; never return unbounded lists

Filtering + Sorting:
  Query params for filtering (?status=pending)
  Sort field + order (?sort=price&order=desc)

Error Responses:
  Machine-readable code (VALIDATION_ERROR)
  Human-readable message
  Field-level details for validation errors

Response Envelope:
  { "data": ... } for success
  { "data": [...], "meta": {...} } for collections
  { "error": {...} } for errors

Idempotency Keys:
  For non-idempotent operations that must be safely retried
  Idempotency-Key: UUID in request header
  Server stores and replays response on duplicate key

Caching:
  Cache-Control: tell clients how long to cache
  ETag: let clients check if data has changed (304 Not Modified)
  no-store: for sensitive data

Rate Limiting:
  X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
  429 + Retry-After header when exceeded
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← REST Fundamentals](../02_rest_fundamentals/rest_explained.md) &nbsp;|&nbsp; **Next:** [Data Formats & Serialization →](../04_data_formats/serialization_guide.md)

**Related Topics:** [REST Fundamentals](../02_rest_fundamentals/rest_explained.md) · [API Versioning](../08_versioning_standards/versioning_strategy.md) · [Error Handling Standards](../06_error_handling_standards/error_guide.md) · [API Design Patterns](../16_api_design_patterns/design_guide.md)
