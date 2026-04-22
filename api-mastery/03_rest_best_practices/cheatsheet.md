# ⚡ REST Best Practices — Cheatsheet

## Learning Priority

| Priority | Topics |
|---|---|
| Must Learn | URL naming rules · pagination (offset vs cursor) · error response structure · URL versioning |
| Should Learn | idempotency keys · HTTP caching (ETag/Cache-Control) · filtering safety |
| Good to Know | sparse fieldsets · rate limiting headers · response envelopes |
| Reference | request signing · response compression · backward compatibility testing |

---

## URL Naming Rules Table

| Rule | Good | Bad | Why |
|---|---|---|---|
| Lowercase | `/payment-methods` | `/paymentMethods` | URLs are case-sensitive; avoid errors |
| Hyphens, not underscores | `/payment-methods` | `/payment_methods` | Underscores hide in links; search engines see hyphenated words separately |
| Plural nouns for collections | `/users` | `/user` | Consistency; collections are plural |
| No verbs in paths | `DELETE /users/42` | `POST /deleteUser` | HTTP method is the verb |
| Max 2 nesting levels | `/users/42/orders` | `/users/42/orders/7/items/3` | Beyond 2 = design smell |
| Version at path start | `/v1/users` | `/users?version=1` | Visible, cacheable, easy to route |

---

## Versioning Strategies Comparison

| Strategy | Example | Pros | Cons | Use when |
|---|---|---|---|---|
| URL versioning | `/v1/users` | Visible, easy to test, cache-friendly | URL "should" identify resource, not version | Default choice for most APIs |
| Header versioning | `API-Version: 2024-01-01` | Clean URLs, fine-grained control | Invisible, harder to test, needs `Vary` header | Sophisticated devs (Stripe-style) |
| Query param | `/users?version=2` | Simple | Pollutes query string, bad caching | Avoid |

**Recommendation: use URL versioning unless you have a strong reason not to.**

---

## Pagination Patterns

| Pattern | Query syntax | Use for | Weakness |
|---|---|---|---|
| Offset/page | `?page=2&limit=20` | Admin UIs, reports, "jump to page" | Page shift when rows are added/deleted |
| Raw offset | `?offset=40&limit=20` | Same as above | Same page shift problem |
| Cursor | `?after=eyJpZCI6MjB9&limit=20` | Feeds, timelines, large live datasets | Can't jump to arbitrary page |

```python
# Offset response shape
{
  "data": [...],
  "pagination": {
    "total": 500, "page": 2, "limit": 20,
    "total_pages": 25, "has_next": true, "has_prev": true
  }
}

# Cursor response shape
{
  "data": [...],
  "pagination": {
    "has_next": true, "has_prev": true,
    "next_cursor": "eyJpZCI6NDB9",
    "prev_cursor": "eyJpZCI6MjF9"
  }
}
```

**Rule of thumb:** offset for admin UIs, cursor for feeds/timelines and 100k+ rows.

---

## Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {"field": "email", "message": "must be a valid email address"},
      {"field": "age",   "message": "must be at least 18"}
    ]
  }
}
```

| Layer | Purpose | Who uses it |
|---|---|---|
| `code` | Machine-readable string constant | Client code switches on this |
| `message` | Human-readable description | Developers reading logs |
| `details` | Field-level errors (validation only) | Form UIs, debugging |

### Standard Error Codes
```
VALIDATION_ERROR         → 400  schema/business validation failed
AUTHENTICATION_REQUIRED  → 401  no valid credentials
PERMISSION_DENIED        → 403  authenticated but not allowed
NOT_FOUND                → 404  resource doesn't exist
CONFLICT                 → 409  would create a duplicate
RATE_LIMIT_EXCEEDED      → 429  too many requests
INTERNAL_ERROR           → 500  server-side bug
```

---

## HTTP Method Selection Guide

```
Reading data?                         → GET
Creating a new resource?              → POST   (non-idempotent; use idempotency key for payments)
Replacing an entire resource?         → PUT    (idempotent; send ALL fields)
Updating specific fields only?        → PATCH  (send only changed fields)
Deleting something?                   → DELETE
Triggering an action (not pure CRUD)? → POST /resource/id/action
```

---

## Response Envelope Convention

```json
// Single resource
{ "data": { "id": 42, "name": "Alice" } }

// Collection with pagination
{ "data": [...], "meta": { "total": 153, "page": 2, "limit": 20 } }

// Error
{ "error": { "code": "NOT_FOUND", "message": "User 42 not found" } }
```

Why the `data` wrapper? A bare array `[...]` can't be extended with pagination metadata without breaking clients.

---

## Filtering and Sorting

```
# Filtering — query parameters, one per filterable field
GET /orders?status=pending&customer_id=42
GET /products?category=electronics&min_price=100&max_price=500
GET /users?role=admin&active=true&created_after=2024-01-01

# Sorting
GET /products?sort=price&order=asc
GET /products?sort=price&order=desc
GET /products?sort=-price              (minus = descending alternative)

# Multi-field sort
GET /products?sort=category,-price     (category asc, price desc)
```

**Only expose filters you have indexes for.** Unindexed filter columns = full table scans.

---

## Idempotency Keys (for safe POST retries)

```
POST /payments
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{ "amount": 5000, "currency": "usd" }
```

How it works:
1. Client sends UUID key with request
2. Server processes and stores response keyed by UUID
3. Client retries with same key after network failure
4. Server returns stored response — no double processing

**Use for:** payments, order creation, any "runs twice = double billing" scenario.

---

## Caching Headers Quick Reference

```
Cache-Control: public, max-age=86400   → CDNs + browser can cache 24h
Cache-Control: private, max-age=300    → only browser cache, 5 min
Cache-Control: no-store                → never cache (auth tokens, financial)
Cache-Control: no-cache                → revalidate before using cached copy

ETag: "abc123"                         → fingerprint (hash) of response
If-None-Match: "abc123"                → "send only if changed" (client request)
→ 304 Not Modified if unchanged (no body = bandwidth saved)
```

| Data type | Recommended Cache-Control |
|---|---|
| Static catalog data | `public, max-age=3600` or longer |
| User-specific data | `private, max-age=300` |
| Auth tokens, financial | `no-store` |
| Frequently updated | short `max-age` or `no-cache` |

---

## Rate Limiting Headers

```
Response headers (always include):
  X-RateLimit-Limit: 1000        → allowed per window
  X-RateLimit-Remaining: 842     → remaining this window
  X-RateLimit-Reset: 1609459200  → Unix ts when window resets

On 429 Too Many Requests:
  Retry-After: 60                → seconds until retry is safe
```

---

## Deprecation Headers (RFC 8594)

```
Deprecation: true
Sunset: Sat, 01 Jan 2025 00:00:00 GMT
Link: <https://api.example.com/v2/users>; rel="successor-version"
```

---

## Navigation

**[Back to README](../README.md)**

**Theory:** [patterns.md](./patterns.md)

**Prev:** [← REST Fundamentals](../02_rest_fundamentals/cheatsheet.md) &nbsp;|&nbsp; **Next:** [Data Formats →](../04_data_formats/cheatsheet.md)

**Related:** [02 REST Fundamentals](../02_rest_fundamentals/cheatsheet.md) · [06 Error Handling](../06_error_handling_standards/cheatsheet.md) · [08 Versioning](../08_versioning_standards/cheatsheet.md)
