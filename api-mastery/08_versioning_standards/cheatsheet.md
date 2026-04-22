# ⚡ API Versioning Standards — Cheatsheet

## Learning Priority

| Priority | Topics |
|---|---|
| Must Learn | breaking vs non-breaking changes · URL versioning (`/v1/`) · deprecation headers (RFC 8594) |
| Should Learn | header versioning trade-offs · API lifecycle stages · migration guide structure |
| Good to Know | query parameter versioning (when to avoid) · sunset communication |
| Reference | canary deployment coordination · backward compatibility testing in CI |

---

## Versioning Strategies Comparison

| Strategy | URL example | Pros | Cons | Use when |
|---|---|---|---|---|
| URL versioning | `GET /v1/users/42` | Visible, cache-friendly, easy to test, easy to route | URL "shouldn't" encode version (REST purists) | Default — public APIs, broad audience |
| Header versioning | `API-Version: 2024-01-01` | Clean URLs, fine-grained per-request control | Invisible, needs Vary header, harder to test | Stripe-style SDK APIs |
| Query param | `GET /users/42?version=2` | Simple | Pollutes query string, bad caching, mixes concerns | Avoid |

**Recommendation:** URL versioning for most cases.

---

## URL Versioning Rules

```
Start at v1:
  https://api.example.com/v1/users     ✓
  https://api.example.com/v0/users     ✗
  https://api.example.com/v2024/users  ✗ (unless doing date-based)

Never break within a version:
  /v1/users always behaves the same
  Breaking change → create /v2/users

Retire old versions with ample notice:
  Internal APIs:    3+ months
  Public APIs:      6–12 months
  Major public APIs: 12–24 months
```

---

## Breaking vs Non-Breaking Changes

### Breaking Changes (require new version)
```
Removing a field from a response
Renaming a field            user_name → username
Changing a field's type     int → string, string → array
Making an optional field required in a request
Removing an endpoint
Changing an endpoint's URL
Changing authentication mechanism
Changing the meaning of a status code
Making validation stricter
Changing pagination behavior (offset → cursor)
```

### Non-Breaking Changes (safe within current version)
```
Adding a new field to a response    (clients that don't know it just ignore it)
Adding a new optional request param
Adding a new endpoint
Adding a new enum value             (careful — strict parsers may break)
Relaxing validation                 (accepting more input formats)
Adding a new HTTP method to a resource
Improving error messages            (same code/status, better message)
```

**When in doubt, treat it as breaking.** False positive (unnecessary bump) costs less than false negative (silent breakage).

---

## Semantic Versioning in APIs

```
v1 → v2 → v3   (major versions for breaking changes)

Don't do: v1.1, v1.2 (minor/patch in URL)
Reason: minor changes should be non-breaking — clients don't need a new URL
```

---

## Deprecation Header Syntax (RFC 8594)

```
Deprecation: true
Sunset: Sat, 01 Jun 2025 00:00:00 GMT
Link: <https://api.example.com/docs/migration/v1-to-v2>; rel="successor-version"
```

```python
# FastAPI — add deprecation headers to all v1 responses
@app.middleware("http")
async def add_deprecation_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/v1/"):
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = "Sat, 01 Jun 2025 00:00:00 GMT"
        response.headers["Link"] = (
            '<https://api.example.com/v2/>; rel="successor-version"'
        )
    return response
```

---

## Response Body Warning Pattern (belt-and-suspenders)

```json
{
  "data": { "..." },
  "_warnings": [
    {
      "code": "endpoint_deprecated",
      "message": "GET /v1/users is deprecated. Migrate to GET /v2/users by 2025-06-01.",
      "docs": "https://api.example.com/docs/migration/v1-to-v2"
    }
  ]
}
```

---

## API Lifecycle Stages

```
alpha → beta → v1 (stable) → deprecated → sunset (410 Gone)

alpha:      internal only, breaking changes without notice
beta:       early access, changes communicated, gather feedback
v1:         public contract, breaking changes require v2
deprecated: functional, headers + body warn about sunset, migration guide available
sunset:     endpoint removed or returns 410 Gone
```

---

## Header Versioning Patterns (Stripe / GitHub style)

```
Stripe style — date-based, per API key:
  Stripe-Version: 2024-06-20
  (API key is pinned to the version active when created)

GitHub style — media type:
  Accept: application/vnd.github.v3+json

Custom header:
  API-Version: 2
```

Header versioning needs `Vary: Accept` (or your custom header) for correct CDN caching:
```
Vary: Accept
Vary: API-Version
```

---

## Migration Guide Structure

```markdown
## Migrating from v1 to v2

### What changed
- `user_name` renamed to `username`
- Pagination changed from offset to cursor on all list endpoints
- Auth changed: API key in query param → Bearer token in header

### Step-by-step

1. Update authentication
   v1: GET /v1/users?api_key=KEY
   v2: GET /v2/users
       Authorization: Bearer KEY

2. Update field references
   v1: response.user_name
   v2: response.username

3. Update pagination
   v1: GET /v1/users?page=2&per_page=20
   v2: GET /v2/users?cursor=eyJpZCI6MjB9&limit=20

### Timeline
- v1 deprecated: 2024-03-01
- v1 sunset: 2025-03-01
```

---

## When Versioning Matters

| Scenario | Recommendation |
|---|---|
| Public API, many consumers | Version from day 1 |
| Internal API, one team | Coordinate directly, versioning optional |
| Internal API, multiple teams | Version to avoid coupling |
| SDK-based API | Header versioning with per-key pinning |
| Microservices internal | URL versioning or contract testing |

---

## FastAPI — Multiple Versions Side by Side

```python
from fastapi import FastAPI
from routers.v1 import users as users_v1
from routers.v2 import users as users_v2

app = FastAPI()

app.include_router(users_v1.router, prefix="/v1")
app.include_router(users_v2.router, prefix="/v2")

# Results in:
# GET /v1/users, GET /v1/users/{id}  ← legacy, deprecated
# GET /v2/users, GET /v2/users/{id}  ← current
```

---

## Navigation

**[Back to README](../README.md)**

**Theory:** [versioning_strategy.md](./versioning_strategy.md)

**Prev:** [← FastAPI](../07_fastapi/cheatsheet.md) &nbsp;|&nbsp; **Next:** [Performance & Scaling →](../09_api_performance_scaling/cheatsheet.md)

**Related:** [03 REST Best Practices](../03_rest_best_practices/cheatsheet.md) · [06 Error Handling](../06_error_handling_standards/cheatsheet.md) · [07 FastAPI](../07_fastapi/cheatsheet.md)
