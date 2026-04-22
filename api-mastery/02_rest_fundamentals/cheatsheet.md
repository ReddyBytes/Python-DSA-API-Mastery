# ⚡ REST Fundamentals — Cheatsheet

## Learning Priority

| Priority | Topics |
|---|---|
| Must Learn | 6 REST constraints · nouns not verbs in URLs · HTTP verb semantics · idempotency |
| Should Learn | HATEOAS concept · URL design patterns · statelessness pattern |
| Good to Know | Fielding dissertation background · cacheability headers |
| Reference | strict vs pragmatic REST · HATEOAS in practice |

---

## The 6 REST Constraints

| # | Constraint | Core idea | Practical impact |
|---|---|---|---|
| 1 | Client-Server | Client and server are separate | Frontend/backend develop independently |
| 2 | Stateless | Every request is self-contained | Auth token in every request; scales horizontally |
| 3 | Cacheable | Responses declare cache-ability | CDN caching; `Cache-Control` headers |
| 4 | Uniform Interface | Consistent, predictable resource design | Developers can guess endpoint behavior |
| 5 | Layered System | Client can't tell if it hits a CDN or origin | Load balancers/CDNs are transparent |
| 6 | Code on Demand | Server can send executable code (optional) | JavaScript delivery to browsers; rarely relevant for APIs |

**Minimum viable REST:** Constraints 1, 2, and 4 get you 90% of the benefit.

---

## REST vs Non-REST

| Style | URL design | Methods | Example |
|---|---|---|---|
| REST | `/users/42` (noun) | GET/POST/PUT/PATCH/DELETE | Good REST API |
| RPC-style (wrong) | `/getUser`, `/deleteUser` (verb) | POST everything | Legacy/internal APIs |

```
WRONG (RPC-style — not REST):
  POST /getUser?id=42
  POST /createUser
  POST /updateUser?id=42
  POST /deleteUser?id=42

RIGHT (REST):
  GET    /users/42
  POST   /users
  PATCH  /users/42
  DELETE /users/42
```

---

## URL Design Rules

| Rule | Good | Bad |
|---|---|---|
| Use nouns, not verbs | `/orders` | `/getOrders` |
| Use plural for collections | `/users` | `/user` |
| Use lowercase | `/payment-methods` | `/paymentMethods` |
| Use hyphens, not underscores | `/payment-methods` | `/payment_methods` |
| Max 2 nesting levels | `/users/42/orders` | `/users/42/orders/7/items/3` |
| Filters in query params | `/orders?status=pending` | `/orders/pending` |

---

## URL Pattern Reference

```
Collections:
  GET  /users              → list all users (paginated)
  POST /users              → create a user

Single items:
  GET    /users/42         → get user 42
  PUT    /users/42         → replace user 42 (full replacement)
  PATCH  /users/42         → update user 42 (partial)
  DELETE /users/42         → delete user 42

Nested resources:
  GET /users/42/orders     → orders belonging to user 42
  GET /users/42/orders/7   → order 7, belonging to user 42

Filtering:
  GET /users?role=admin&active=true

Sorting:
  GET /products?sort=price&order=desc

Pagination:
  GET /users?page=2&limit=20         (offset-based)
  GET /users?after=eyJpZCI6MjB9      (cursor-based)

Actions (exception to nouns-only):
  POST /users/42/deactivate
  POST /invoices/9/send
```

---

## Idempotency Table

| Method | Idempotent | Safe | What happens on retry |
|---|---|---|---|
| GET | Yes | Yes | Same result every time — safe to retry |
| PUT | Yes | No | Same state after N calls as after 1 |
| DELETE | Yes | No | First call deletes; subsequent → 404 (same final state) |
| PATCH | No* | No | May apply the change multiple times |
| POST | No | No | Creates a new resource every call — dangerous to retry |

**Idempotent = calling N times has the same effect as calling once.**

```
Idempotent scenario (DELETE):
  DELETE /users/42  → 204 (deleted)
  DELETE /users/42  → 404 (already gone)
  Final state: user 42 doesn't exist — same either way ✓

Non-idempotent scenario (POST):
  POST /payments amount=1000  → 201 (charged once)
  POST /payments amount=1000  → 201 (charged AGAIN!) ✗
```

---

## Statelessness Pattern

```
Stateful (BAD for APIs):
  Request 1: "I am Alice"
  Server: remembers session
  Request 2: "give me my orders"
  Server: knows who Alice is from session
  Problem: breaks with multiple servers, hard to scale

Stateless (REST):
  Every request includes identity:
  GET /orders
  Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...

  Server verifies token on every request
  Any server in the cluster handles any request
  Scale horizontally by adding servers
```

---

## HTTP Caching Headers (REST Cacheable Constraint)

```
Response headers:
  Cache-Control: public, max-age=3600    → anyone can cache for 1 hour
  Cache-Control: private, max-age=300   → only browser caches, 5 min
  Cache-Control: no-store               → never cache (sensitive data)
  ETag: "abc123"                        → fingerprint for conditional requests

Request headers (conditional):
  If-None-Match: "abc123"               → only send if ETag changed
  → Server responds 304 Not Modified if unchanged (no body sent)
```

---

## HATEOAS — Know It Exists

```json
{
  "id": 42,
  "name": "Alice",
  "_links": {
    "self":       { "href": "/users/42" },
    "orders":     { "href": "/users/42/orders" },
    "deactivate": { "href": "/users/42/deactivate", "method": "POST" }
  }
}
```

**Theory:** Responses include links to next actions — clients discover capabilities from the response.
**Practice:** Almost no production APIs implement HATEOAS fully. Know it exists; don't stress about it.

---

## Paginated Response Structure

```json
{
  "data": [
    {"id": 21, "name": "User 21"},
    {"id": 22, "name": "User 22"}
  ],
  "meta": {
    "total": 153,
    "page": 2,
    "limit": 20,
    "total_pages": 8,
    "has_next": true,
    "has_prev": true
  },
  "links": {
    "self":  "/users?page=2&limit=20",
    "next":  "/users?page=3&limit=20",
    "prev":  "/users?page=1&limit=20"
  }
}
```

---

## Navigation

**[Back to README](../README.md)**

**Theory:** [rest_explained.md](./rest_explained.md)

**Prev:** [← What is an API](../01_what_is_an_api/cheatsheet.md) &nbsp;|&nbsp; **Next:** [REST Best Practices →](../03_rest_best_practices/cheatsheet.md)

**Related:** [01 What is an API](../01_what_is_an_api/cheatsheet.md) · [03 REST Best Practices](../03_rest_best_practices/cheatsheet.md) · [06 Error Handling](../06_error_handling_standards/cheatsheet.md)
