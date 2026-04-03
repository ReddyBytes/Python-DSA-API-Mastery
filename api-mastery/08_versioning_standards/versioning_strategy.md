# 12 — API Versioning

> "Every client relies on your current behavior. How do you change anything without breaking the world?"

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
breaking change definition · URL versioning (/v1/ /v2/) · deprecation headers (RFC 8594)

**Should Learn** — Important for real projects, comes up regularly:
header versioning trade-offs · API lifecycle (alpha/beta/v1/deprecated/sunset) · migration guides

**Good to Know** — Useful in specific situations, not always tested:
query parameter versioning · version sunset communication

**Reference** — Know it exists, look up syntax when needed:
canary deployment coordination · backward compatibility testing in CI

---

## 1. Why Versioning is Hard

Your API is a public contract. The moment you ship it and a client integrates, every behavior becomes load-bearing. The field name, the data type, the status code for an error — changing any of it can silently break a mobile app that you don't control, a partner integration you didn't know existed, or a script running in a customer's CI pipeline.

The challenge: you have to evolve your API (fix mistakes, add features, retire old designs) while keeping existing clients working.

Versioning is not primarily a technical problem. It is a communication and discipline problem. The technical mechanism is easy. The hard part is:

- Deciding what counts as a breaking change
- Committing to a deprecation timeline and sticking to it
- Actually telling your consumers about changes before they happen

---

## 2. What Counts as a Breaking Change

**Breaking changes** — existing clients will fail or behave incorrectly without code changes on their end:

```
Removing a field from a response
Renaming a field  (user_name → username)
Changing a field's type  (int → string, string → array)
Changing a field from optional to required in a request
Removing an endpoint
Changing an endpoint's URL
Changing authentication mechanisms
Changing the meaning of a status code
Making validation stricter  (previously accepted "2024/01/15", now requires ISO 8601)
Changing pagination behavior  (offset to cursor)
```

**Non-breaking changes** — existing clients continue to work without any changes:

```
Adding a new field to a response  (clients that don't know about it ignore it)
Adding a new optional parameter to a request
Adding a new endpoint
Adding a new enum value  (be careful — strict enum parsers may break)
Relaxing validation  (accepting more formats)
Adding a new HTTP method to an existing resource
Improving error messages  (as long as the error code/status doesn't change)
```

When in doubt, treat it as breaking. The cost of a false negative (silent breakage) is much higher than the cost of a false positive (unnecessary version bump).

---

## 3. Versioning Strategies

### URL Versioning — `/v1/users`, `/v2/users`

The most common approach. The version is in the URL path.

```
GET /v1/users/42
GET /v2/users/42
```

Pros:
- Immediately visible in logs, browser history, network traces
- Easy to test by changing the URL
- Easy to route at the API gateway level
- Simple for developers to understand and use

Cons:
- Breaks the REST principle that a URL identifies a resource (the resource didn't change, just its representation)
- Duplicate routes in your codebase if you maintain both versions

**This is the right default.** Use URL versioning unless you have a specific reason not to.

### Header Versioning

Version is passed in a custom request header or the `Accept` header.

```
GET /users/42
API-Version: 2024-01-01
```

```
GET /users/42
Accept: application/vnd.myapi.v2+json
```

Stripe uses date-based header versioning. Each API key is pinned to the version active when it was created. You can upgrade explicitly.

Pros:
- URLs stay clean and stable
- Can version at a fine-grained level (per-request, not per-client)

Cons:
- Not visible in browser — harder to test manually
- Requires custom header handling in every client
- Logs don't show version unless you explicitly propagate it
- Caching is harder (Vary header required)

**Use this when:** you have a sophisticated developer audience, you want fine-grained version control per request, or you are Stripe.

### Query Parameter Versioning — `?version=2`

```
GET /users/42?version=2
```

Avoid this. It pollutes the query string, interferes with caching, and mixes routing concerns with filter concerns. Some legacy APIs use it; don't design new ones this way.

### When to Use Each

| Scenario | Recommendation |
|---|---|
| Public API, broad audience | URL versioning |
| Internal API, controlled consumers | URL versioning or no versioning (just coordinate) |
| SDK-based API (like Stripe) | Header versioning with per-key pinning |
| Microservices internal calls | URL versioning or contract testing instead of versioning |

---

## 4. Deprecation Strategy

Removing a version is as important as adding one. Without a deprecation process, you accumulate dead weight forever.

**Step 1 — Signal deprecation in the response headers.** Start adding these headers the moment you decide a version or endpoint will be retired:

```
Deprecation: true
Sunset: Sat, 01 Jun 2025 00:00:00 GMT
Link: <https://api.example.com/docs/migration/v1-to-v2>; rel="successor-version"
```

`Deprecation` and `Sunset` are IETF standards (RFC 8594). Well-built API clients can detect them and surface warnings to developers automatically.

**Step 2 — Return a warning in the response body** for developers who aren't watching headers:

```json
{
  "data": { ... },
  "_warnings": [
    {
      "code": "endpoint_deprecated",
      "message": "GET /v1/users is deprecated. Migrate to GET /v2/users by 2025-06-01.",
      "docs": "https://api.example.com/docs/migration/v1-to-v2"
    }
  ]
}
```

**Step 3 — Notify registered developers directly.** Email every developer who has made a call to the deprecated endpoint in the last 30 days. Give them the migration guide. Give them the deadline.

**Step 4 — Maintain a minimum deprecation window.** Internal APIs: 3 months minimum. Public APIs: 6–12 months minimum. High-profile public APIs (like Twitter, Stripe): 12–24 months. The window should reflect how long it realistically takes your consumers to notice, prioritize, and ship the migration.

**Step 5 — Log and monitor usage.** Track which clients are still calling deprecated endpoints as the sunset date approaches. Reach out individually to the top consumers.

---

## 5. Version Lifecycle

```
alpha → beta → v1 → deprecated → sunset
```

**Alpha:** Internal use only. Breaking changes without notice. Not advertised publicly.

**Beta:** Available to early access developers. Breaking changes possible, but communicated. Use beta to gather real-world feedback before locking in a contract.

**v1 (stable):** Public, versioned, stable contract. Breaking changes require a new major version. This is when the deprecation policy applies.

**Deprecated:** Still functional. Headers and warnings signal that retirement is coming. Migration guide is available.

**Sunset:** Endpoint removed or returns `410 Gone`. Clients must have migrated.

Communicate the lifecycle clearly in your docs. Developers need to know what to expect from a "beta" endpoint vs a "v1" endpoint.

---

## 6. Migration Guide

When you release v2, write a migration guide before you announce it. The guide should contain:

```markdown
## Migrating from v1 to v2

### What changed
- `user_name` renamed to `username` on all user objects
- Pagination changed from offset to cursor-based on all list endpoints
- `GET /v1/users` removed — use `GET /v2/users`
- Authentication changed from API key query param to Bearer token header

### Step-by-step migration

#### 1. Update authentication
v1:  GET /v1/users?api_key=YOUR_KEY
v2:  GET /v2/users
     Authorization: Bearer YOUR_KEY

#### 2. Update field references
Find every place in your code that reads `user.user_name` and
replace with `user.username`.

#### 3. Update pagination
v1 offset-based:
  GET /v2/users?page=2&per_page=20

v2 cursor-based:
  GET /v2/users?cursor=eyJpZCI6MjB9&limit=20
  # cursor comes from the previous response: response.next_cursor

### Timeline
- v1 deprecated: 2024-03-01
- v1 sunset: 2025-03-01
- Questions: api-support@example.com
```

A migration guide that is honest about the changes (including breaking ones) builds trust even when the changes are painful.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← FastAPI Advanced](../07_fastapi/advanced_guide.md) &nbsp;|&nbsp; **Next:** [API Performance & Scaling →](../09_api_performance_scaling/performance_guide.md)

**Related Topics:** [REST Best Practices](../03_rest_best_practices/patterns.md) · [Error Handling Standards](../06_error_handling_standards/error_guide.md) · [API Design Patterns](../16_api_design_patterns/design_guide.md)
