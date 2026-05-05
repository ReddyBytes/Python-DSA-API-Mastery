# API & Backend Practice — 100 Questions

> From HTTP basics to production system design — work through all 100 without skipping.

---

## How to Use This File

1. Read the question. Stop. Think for at least 60 seconds before clicking the answer.
2. Use the "How to think through this" block — it teaches the reasoning pattern, not just the answer.
3. Do not rush. Finishing all 100 with real thought is worth more than skimming 300 questions passively.

---

## How to Think: The 5-Step Framework

1. **Restate** — What is the question actually asking? What is the context (client, server, DB)?
2. **Identify the concept** — Which API/backend concept is being tested?
3. **Recall the rule** — What is the correct behaviour, standard, or pattern?
4. **Apply** — Walk through a concrete example or scenario.
5. **Trade-off check** — What are the pros and cons? What breaks under scale?

---

## Progress Tracker

- [ ] Tier 1 — HTTP & REST Foundations (Q1–Q25)
- [ ] Tier 2 — FastAPI, Auth & Data (Q26–Q50)
- [ ] Tier 3 — Advanced API Patterns (Q51–Q75)
- [ ] Tier 4 — Interview & Scenario (Q76–Q90)
- [ ] Tier 5 — Critical Thinking (Q91–Q100)

---

## Question Types

| Tag | What it tests |
|---|---|
| `[Normal]` | Recall and apply — straightforward |
| `[Thinking]` | Requires reasoning about trade-offs or behaviour |
| `[Logical]` | Trace through a request lifecycle or predict outcome |
| `[Critical]` | Edge case or tricky gotcha |
| `[Interview]` | Explain or compare in interview style |
| `[Debug]` | Find the bug or problem in given code/design |
| `[Design]` | Architecture or API design decision |

---

## Tier 1 — HTTP & REST Foundations · Q1–Q25

> Focus: HTTP methods, status codes, headers, REST principles, request lifecycle, URL design

---

### Q1 · [Normal] · `http-methods-semantics`

> **What is the difference between GET, POST, PUT, PATCH, and DELETE? Which are idempotent and which are safe?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

| Method | Purpose | Safe? | Idempotent? |
|---|---|---|---|
| GET | Retrieve resource | Yes | Yes |
| POST | Create resource / trigger action | No | No |
| PUT | Replace resource entirely | No | Yes |
| PATCH | Partially update resource | No | No* |
| DELETE | Delete resource | No | Yes |

- **Safe**: no server-side state change (GET, HEAD, OPTIONS).
- **Idempotent**: calling n times has same effect as calling once (GET, PUT, DELETE). PUT replaces the whole resource — calling it twice with the same body produces the same result. DELETE on an already-deleted resource should return 404 but the server state is the same.
- POST is neither — two POST /orders creates two orders.
- PATCH *can* be idempotent if it sets absolute values (e.g. `{"status": "active"}`) but is not required to be.

**How to think through this:**
1. Safe = read-only. Idempotent = repeatable without side effects.
2. PUT replaces the entire resource; PATCH modifies only specified fields.
3. POST is the only non-idempotent write method — use idempotency keys for retry safety.

**Key takeaway:** GET=safe+idempotent, PUT/DELETE=idempotent, POST=neither. Idempotency is critical for retry logic.

</details>

> 📖 **Theory:** [HTTP Methods](./02_rest_fundamentals/rest_explained.md)

---

### Q2 · [Thinking] · `post-vs-put-vs-patch`

> **When should you use POST vs PUT vs PATCH? Give a real API example for each.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- **POST /orders** — create a new order. The server assigns the ID. Not idempotent — retrying creates duplicate orders.
- **PUT /users/42** — replace the entire user object with a new representation. Client provides the full resource. Idempotent — same body, same result.
- **PATCH /users/42** — update only the supplied fields. Client sends `{"email": "new@email.com"}`. Other fields unchanged.

```http
POST /articles
{"title": "New Post", "body": "..."}    → 201 Created, Location: /articles/99

PUT /articles/99
{"title": "Updated", "body": "new body", "author": "Alice"}  → 200 OK (full replace)

PATCH /articles/99
{"title": "Just the title changed"}    → 200 OK (partial update)
```

**How to think through this:**
1. POST: "I don't know the ID yet — server assigns it."
2. PUT: "I'm sending the complete new version of this resource."
3. PATCH: "I'm sending only the fields I want to change."

**Key takeaway:** POST=create (server assigns ID), PUT=full replace (client provides complete body), PATCH=partial update (client provides only changed fields).

</details>

> 📖 **Theory:** [PUT vs PATCH](./02_rest_fundamentals/rest_explained.md)

---

### Q3 · [Critical] · `idempotency-keys`

> **A payment API uses POST to charge a customer. The network times out — you don't know if the charge succeeded. How do idempotency keys solve this?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The client generates a unique idempotency key (UUID) and sends it with every request:

```http
POST /charges
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
{"amount": 100, "currency": "USD", "customer_id": "cus_123"}
```

The server stores the key + response. If the same key arrives again (retry), it returns the stored response without re-processing. This makes POST effectively idempotent for that operation.

**How it solves the problem:**
1. Network timeout — client retries with the same idempotency key.
2. If charge succeeded: server returns the stored success response.
3. If charge failed: server re-processes and returns the result.
4. Either way: no duplicate charge.

**Implementation:** Server stores `{idempotency_key: response}` in a fast store (Redis). TTL of 24 hours is typical. Check key existence before processing.

**How to think through this:**
1. The problem: POST is not idempotent, but payments must not double-charge.
2. Idempotency key = client-generated unique token that de-duplicates retries server-side.
3. Stripe, PayPal, and all major payment APIs require idempotency keys on write endpoints.

**Key takeaway:** Idempotency keys make non-idempotent POST requests safe to retry — the server deduplicates by storing the response against the key.

</details>

> 📖 **Theory:** [Idempotency](./02_rest_fundamentals/rest_explained.md)

---

### Q4 · [Normal] · `status-codes-2xx`

> **What is the difference between 200, 201, 202, and 204? When do you use each?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- **200 OK** — request succeeded, response body contains the result. Use for GET, PUT, PATCH responses with a body.
- **201 Created** — a new resource was created (POST). Include `Location: /resource/123` header pointing to the new resource.
- **202 Accepted** — request received and will be processed asynchronously. The work is not done yet. Return a job ID or polling URL.
- **204 No Content** — request succeeded but there is no response body. Use for DELETE (resource gone, nothing to return) or PUT/PATCH when you don't return the updated resource.

```http
POST /users → 201 Created, Location: /users/42, Body: {user object}
DELETE /users/42 → 204 No Content, Body: empty
POST /reports/generate → 202 Accepted, Body: {"job_id": "abc", "status_url": "/jobs/abc"}
```

**How to think through this:**
1. 200 = success with body. 201 = success and something new was made. 204 = success, no body.
2. Always include `Location` header with 201 so clients know where to find the new resource.
3. 202 is underused — it's the right code for long-running async operations.

**Key takeaway:** 200=success+body, 201=created+location, 202=async accepted, 204=success+no body. Use 201 for POST creates, 204 for DELETE.

</details>

> 📖 **Theory:** [Success Status Codes](./06_error_handling_standards/error_guide.md)

---

### Q5 · [Critical] · `status-codes-4xx`

> **When do you use 400, 401, 403, 404, 409, and 422? What is the difference between 401 and 403?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- **400 Bad Request** — malformed request syntax, invalid parameters (e.g. `age: "abc"` where integer expected).
- **401 Unauthorized** — authentication required or failed. The client is not authenticated. (Despite the name "Unauthorized", it means "unauthenticated".)
- **403 Forbidden** — authenticated but not permitted. The client is known but lacks permission.
- **404 Not Found** — resource does not exist at this URL.
- **409 Conflict** — request conflicts with current state (e.g. creating a user with an email that already exists, optimistic locking conflict).
- **422 Unprocessable Entity** — request is syntactically correct but semantically invalid (e.g. end_date before start_date).

**401 vs 403:**
- 401 = "Who are you?" — send credentials and try again. Response includes `WWW-Authenticate` header.
- 403 = "I know who you are, but you can't do this." — sending different credentials won't help.

**How to think through this:**
1. 4xx = client error. 5xx = server error.
2. 400: wrong format. 422: right format, wrong business logic.
3. 401: not logged in. 403: logged in but forbidden.

**Key takeaway:** 401=not authenticated (retry with credentials), 403=authenticated but forbidden (permission denied). 422=valid JSON but invalid business logic.

</details>

> 📖 **Theory:** [Error Status Codes](./06_error_handling_standards/error_guide.md)

---

### Q6 · [Thinking] · `http-404-security`

> **Should you return 404 or 403 when an authenticated user requests a resource they don't have permission to see? What are the security implications of each choice?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
This is a security vs transparency trade-off:

**Return 403 (transparent):**
- Tells the client: "This resource exists, but you can't access it."
- Pro: Semantically correct. Client knows the URL is valid.
- Con: Information leak — an attacker learns that the resource exists, even if they can't access it. Useful for enumeration attacks.

**Return 404 (security through obscurity):**
- Tells the client: "Nothing here." — same response whether the resource doesn't exist OR the user lacks permission.
- Pro: Prevents resource enumeration — attacker can't distinguish "doesn't exist" from "forbidden."
- Con: Misleading. Makes debugging harder.

**Best practice:** Return 404 for sensitive resources (private user data, internal admin routes). Return 403 for public resources where existence is not sensitive (e.g. a public API endpoint that requires auth).

GitHub uses 404 for private repos instead of 403 to prevent repo name enumeration.

**How to think through this:**
1. Ask: "Does the existence of this resource reveal sensitive information?"
2. If yes → 404 (hide existence). If no → 403 (be transparent).
3. Document your choice in the API spec so clients understand the pattern.

**Key takeaway:** For sensitive resources, return 404 instead of 403 to prevent enumeration — the attacker shouldn't learn that the resource exists.

</details>

> 📖 **Theory:** [404 vs 403](./06_error_handling_standards/error_guide.md)

---

### Q7 · [Normal] · `rest-statelessness`

> **What does "stateless" mean in REST? What are the implications for session management?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Stateless means each request must contain **all information necessary to process it** — the server holds no session state between requests. The server treats every request as if it came from a new client.

Implications:
- No server-side sessions. The server doesn't remember the previous request.
- Authentication credentials (API key, JWT token) must be included in **every** request.
- Session data (user ID, permissions) must be encoded in the request (JWT) or looked up from a shared store (Redis) on every request.

**Benefits of statelessness:**
- **Scalability**: any server can handle any request — no sticky sessions needed.
- **Reliability**: if a server crashes, the client retries against any other server.
- **Simplicity**: server logic is simpler without session tracking.

**How to think through this:**
1. Contrast with stateful (e.g. FTP): server remembers your current directory between commands.
2. REST stateless: each HTTP request is independent. Include auth token every time.
3. JWTs enable stateless auth — the token itself carries user identity and is verified on each request without DB lookup.

**Key takeaway:** REST statelessness = every request is self-contained. No server-side session means any server can handle any request — critical for horizontal scaling.

</details>

> 📖 **Theory:** [REST Statelessness](./02_rest_fundamentals/rest_explained.md)

---

### Q8 · [Normal] · `rest-resource-naming`

> **What are the URL design rules for RESTful APIs? What makes a URL "RESTful"?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
RESTful URL rules:
1. **Nouns, not verbs** — `/users`, `/orders/42`, not `/getUser`, `/createOrder`.
2. **Plural nouns** — `/users` (not `/user`). Consistent pluralisation.
3. **Lowercase, hyphen-separated** — `/order-items` (not `/orderItems` or `/order_items`).
4. **Hierarchy for relationships** — `/users/42/orders` for orders belonging to user 42.
5. **HTTP method conveys the action** — GET /users = list, POST /users = create, DELETE /users/42 = delete.
6. **No file extensions** — `/users/42`, not `/users/42.json`. Use `Accept` header for format negotiation.

```
GET    /users          → list all users
POST   /users          → create a user
GET    /users/42       → get user 42
PUT    /users/42       → replace user 42
PATCH  /users/42       → update user 42 partially
DELETE /users/42       → delete user 42
GET    /users/42/posts → posts belonging to user 42
```

**How to think through this:**
1. URLs identify resources (things), HTTP methods describe actions (verbs).
2. Nesting beyond 2 levels (`/a/b/c/d`) becomes unwieldy — flatten if possible.
3. Query params for filtering/sorting: `GET /users?role=admin&sort=name`.

**Key takeaway:** REST URLs = nouns (resources) + HTTP methods (actions). Never put verbs in URLs.

</details>

> 📖 **Theory:** [Resource Naming](./03_rest_best_practices/patterns.md)

---

### Q9 · [Thinking] · `rest-hateoas`

> **What is HATEOAS? Is it actually used in practice?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
HATEOAS (Hypermedia As The Engine Of Application State) is a REST constraint where API responses include **links to related actions and resources**, allowing clients to discover the API dynamically without hardcoded URLs.

```json
{
  "id": 42,
  "name": "Alice",
  "_links": {
    "self": {"href": "/users/42"},
    "orders": {"href": "/users/42/orders"},
    "deactivate": {"href": "/users/42/deactivate", "method": "POST"}
  }
}
```

**In practice:** HATEOAS is rarely implemented fully. Most APIs are "REST-ish" (use nouns + HTTP methods) but don't include hypermedia links. Reasons:
- Clients typically hardcode URLs anyway.
- Adds response payload size.
- Client libraries need extra code to follow links.

**Where it is used:** HAL (Hypertext Application Language), JSON:API, and some large APIs (PayPal, GitHub) include partial hypermedia. The GitHub API includes `_links` for pagination.

**How to think through this:**
1. Roy Fielding (REST inventor) considers an API without HATEOAS "not really REST."
2. In practice, REST has been adopted selectively — most "REST APIs" don't fully implement HATEOAS.
3. Pagination links in responses (`_links.next`) are the most common HATEOAS usage.

**Key takeaway:** HATEOAS is theoretically elegant but rarely fully implemented — the most common practical use is including pagination links in collection responses.

</details>

> 📖 **Theory:** [HATEOAS](./02_rest_fundamentals/rest_explained.md)

---

### Q10 · [Normal] · `content-type-header`

> **What does the `Content-Type` header do? What is the difference between `Content-Type` and `Accept`?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- **`Content-Type`**: describes the format of the **request body** being sent. Tells the server how to parse the body.
- **`Accept`**: tells the server what format(s) the **client can receive** in the response.

```http
POST /users
Content-Type: application/json     ← body is JSON, parse it as JSON
Accept: application/json           ← I want a JSON response

{"name": "Alice", "email": "alice@example.com"}
```

Common Content-Type values:
- `application/json` — JSON body
- `application/x-www-form-urlencoded` — HTML form data
- `multipart/form-data` — file uploads
- `text/plain`, `text/html`

If `Content-Type` is missing or wrong, the server may return **415 Unsupported Media Type**.
If the server can't produce the format in `Accept`, it returns **406 Not Acceptable**.

**How to think through this:**
1. `Content-Type` = "here's what I'm sending you."
2. `Accept` = "here's what I want back."
3. In REST APIs, both are almost always `application/json`.

**Key takeaway:** Content-Type describes the request body format; Accept describes the desired response format. Both go in the request headers.

</details>

> 📖 **Theory:** [Content-Type Header](./04_data_formats/serialization_guide.md)

---

### Q11 · [Normal] · `cors-basics`

> **What is CORS and why does it exist? What does the `Access-Control-Allow-Origin` header do?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
CORS (Cross-Origin Resource Sharing) is a browser security mechanism that restricts web pages from making requests to a **different origin** (domain + protocol + port) than the one that served the page.

Without CORS: a malicious website could use your browser to make requests to your bank's API using your stored cookies.

**How it works:**
1. Browser sends a `Origin: https://myapp.com` header with the request.
2. Server responds with `Access-Control-Allow-Origin: https://myapp.com` (or `*` for public APIs).
3. If the header is missing or doesn't match, the browser **blocks** the response (the request was made, but the browser won't let JavaScript read it).

For non-simple requests (PUT, DELETE, custom headers), the browser sends a **preflight OPTIONS request** first.

```python
# FastAPI CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["https://myapp.com"],
                   allow_methods=["*"], allow_headers=["*"])
```

**How to think through this:**
1. CORS is enforced by the BROWSER, not the server. Server-to-server calls bypass CORS entirely.
2. `*` allows any origin — fine for public APIs, dangerous for authenticated APIs.
3. Always specify exact origins for APIs that use cookies or sensitive data.

**Key takeaway:** CORS is a browser-side restriction. The server opts in to cross-origin requests via `Access-Control-Allow-Origin`. Non-browser clients (curl, server code) are never affected by CORS.

</details>

> 📖 **Theory:** [CORS](./11_api_security_production/security_hardening.md)

---

### Q12 · [Thinking] · `cache-control-header`

> **What does `Cache-Control: max-age=3600` mean? What is the difference between `no-cache` and `no-store`?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- `Cache-Control: max-age=3600` — the response can be cached for 3600 seconds (1 hour). After that, a fresh request must be made.
- `no-cache` — the response can be stored in cache, but the cache **must revalidate** with the origin server before using it (sends a conditional request with `If-None-Match` or `If-Modified-Since`). If the server says "not modified" (304), the cached response is used.
- `no-store` — **never store** the response in any cache at all. Use for sensitive data (banking, medical records).
- `private` — only the client browser can cache, not intermediate proxies/CDNs.
- `public` — any cache (CDN, proxy, browser) can store the response.

```http
Cache-Control: public, max-age=86400         ← CDN can cache for 1 day
Cache-Control: private, max-age=300          ← browser caches 5 min, CDN cannot
Cache-Control: no-store                      ← never cache (sensitive data)
Cache-Control: no-cache, must-revalidate     ← cache but always check freshness
```

**How to think through this:**
1. `no-store` = most restrictive. Use for auth tokens, personal data.
2. `no-cache` ≠ "don't cache." It means "cache but verify freshness every time."
3. For static assets (CSS, JS with content hash in filename): `max-age=31536000, immutable`.

**Key takeaway:** `no-store`=never cache; `no-cache`=cache but always revalidate; `max-age`=cache for N seconds. `no-cache` does NOT mean "don't cache."

</details>

> 📖 **Theory:** [Cache-Control](./09_api_performance_scaling/performance_guide.md)

---

### Q13 · [Normal] · `url-path-vs-query`

> **When should a value go in the URL path vs a query parameter? Give examples of both.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Path parameter** — identifies a specific resource. Required, part of the resource identity.
```
GET /users/42          → user 42 specifically
GET /orders/99/items   → items of order 99
```

**Query parameter** — filters, sorts, paginates, or configures the response. Optional.
```
GET /users?role=admin&sort=name&page=2&limit=20
GET /products?category=electronics&min_price=100&max_price=500
```

**Rules:**
- Path: "Which resource?" — required, hierarchical, identifies the resource.
- Query: "How to filter/sort/format it?" — optional, modifiers.
- Never put sensitive data in URLs — they are logged by servers, proxies, and browsers.
- Search/filter always → query params. Resource ID always → path.

**Edge case: actions on resources:**
```
POST /users/42/activate   ← acceptable (action as path segment)
POST /users/42?action=activate   ← avoid mixing
```

**How to think through this:**
1. Can I bookmark this URL and always get the same resource? → path parameter.
2. Am I narrowing down a collection? → query parameter.

**Key takeaway:** Path = resource identity (required). Query = filter/sort/paginate (optional). Never put sensitive data in URLs.

</details>

> 📖 **Theory:** [Path vs Query Params](./03_rest_best_practices/patterns.md)

---

### Q14 · [Thinking] · `api-versioning-url`

> **What are the three main API versioning strategies? What are the trade-offs of URL path versioning vs header versioning?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Three strategies:**
1. **URL path**: `/v1/users`, `/v2/users`
2. **Request header**: `API-Version: 2` or `Accept: application/vnd.myapi.v2+json`
3. **Query parameter**: `/users?version=2`

**URL path versioning** (most common):
- Pros: explicit, visible, easy to test in browser, simple routing, bookmarkable.
- Cons: "unRESTful" (version is not part of the resource identity), clients must update base URLs, harder to deprecate gracefully.

**Header versioning:**
- Pros: clean URLs, RESTful purists prefer it, same URL for all versions.
- Cons: harder to test (can't just paste URL in browser), less discoverable, harder to cache at CDN level.

**Query parameter:**
- Pros: easy to test, doesn't change URL structure.
- Cons: can be accidentally omitted, awkward with caching.

**Best practice for most teams:** URL path versioning (`/v1/`, `/v2/`) for its simplicity and testability. Only bump the version on breaking changes.

**How to think through this:**
1. "What's easiest for clients to consume and test?" → URL path wins.
2. Header versioning is theoretically cleaner but practically harder to work with.
3. Stripe uses URL versioning (`/v1/`). GitHub uses URL. Most public APIs do.

**Key takeaway:** URL path versioning is the most practical — visible, testable, easy to route. Only introduce a new version for breaking changes.

</details>

> 📖 **Theory:** [API Versioning](./08_versioning_standards/versioning_strategy.md)

---

### Q15 · [Normal] · `pagination-strategies`

> **Compare offset pagination and cursor pagination. When does offset pagination break down?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Offset pagination:**
```
GET /posts?offset=20&limit=10   → skip 20, return next 10
```
Implementation: `SELECT * FROM posts LIMIT 10 OFFSET 20`

Problems:
1. **Inconsistent results**: if items are inserted/deleted while paginating, pages overlap or skip items.
2. **Performance**: large offsets require the DB to scan and discard O(offset) rows — `OFFSET 100000` is slow.

**Cursor pagination:**
```
GET /posts?cursor=eyJpZCI6IDEwMH0&limit=10   → items after cursor (opaque token)
```
Implementation: `SELECT * FROM posts WHERE id > 100 LIMIT 10`

Advantages:
1. **Consistent**: new items don't shift pages. The cursor points to a specific row.
2. **Fast**: index seek to cursor position, no scanning.

Disadvantages: can't jump to page 5 directly. Forward-only (usually). Cursor must be opaque (base64 encode the sort key).

**How to think through this:**
1. Offset: simple, allows random page access, breaks under concurrent modifications.
2. Cursor: robust, fast, but no random access and cursor must be serialised.
3. For real-time feeds (Twitter, Instagram): always cursor-based.

**Key takeaway:** Cursor pagination is more robust and performant than offset for large datasets and real-time data — use offset only for admin UIs where exact page numbers matter.

</details>

> 📖 **Theory:** [Pagination](./09_api_performance_scaling/performance_guide.md)

---

### Q16 · [Normal] · `request-lifecycle`

> **Describe the full lifecycle of an HTTP request from the moment you type a URL in your browser to receiving the response.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
1. **URL parsing** — browser parses scheme, host, path, query.
2. **DNS resolution** — browser checks local cache → OS cache → ISP resolver → authoritative DNS server → returns IP address.
3. **TCP connection** — 3-way handshake (SYN → SYN-ACK → ACK) to establish connection on port 80/443.
4. **TLS handshake** (HTTPS) — negotiate cipher, exchange certificates, verify server identity, derive session keys. Adds ~1–2 RTTs.
5. **HTTP request sent** — browser sends `GET /path HTTP/1.1` with headers (Host, Cookie, Accept, etc.).
6. **Server processing** — load balancer routes to a server, application logic runs, DB queries execute, response prepared.
7. **HTTP response** — server sends status line + headers + body.
8. **TCP teardown** — connection closed (or kept alive for reuse in HTTP/1.1, multiplexed in HTTP/2).
9. **Rendering** — browser parses HTML, fires additional requests for CSS/JS/images.

**How to think through this:**
1. Each step adds latency: DNS (~20ms), TCP handshake (~50ms), TLS (~50ms), server processing, data transfer.
2. HTTP/2 solves head-of-line blocking with multiplexing. HTTP/3 uses QUIC (UDP) to eliminate TCP handshake.
3. CDNs reduce latency by handling DNS+TCP+TLS at edge nodes close to the user.

**Key takeaway:** URL → DNS → TCP → TLS → HTTP → server → response. CDNs and keep-alive connections eliminate repeated DNS/TCP/TLS overhead.

</details>

> 📖 **Theory:** [Request Lifecycle](./01_what_is_an_api/story.md)

---

### Q17 · [Thinking] · `http2-vs-http1`

> **What problems does HTTP/2 solve that HTTP/1.1 couldn't? What is multiplexing?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**HTTP/1.1 problems:**
1. **Head-of-line blocking**: requests are processed in order per connection — slow request blocks all subsequent ones.
2. **Multiple connections**: browsers open 6 connections per domain to work around blocking — wasteful.
3. **Header overhead**: large uncompressed headers sent with every request (cookies, User-Agent, etc.).
4. **No server push**: server can only respond to requests, never proactively send resources.

**HTTP/2 solutions:**
1. **Multiplexing**: multiple requests/responses interleaved on a single TCP connection. No head-of-line blocking at the HTTP layer.
2. **Header compression** (HPACK): compresses headers, especially repeated ones. Significant savings for cookie-heavy APIs.
3. **Server push**: server can push CSS/JS before the browser asks for it.
4. **Binary framing**: more efficient than text-based HTTP/1.1.

```
HTTP/1.1: Req1 → Resp1 → Req2 → Resp2 (sequential per connection)
HTTP/2:   Req1 + Req2 interleaved → Resp1 + Resp2 interleaved (one connection)
```

**How to think through this:**
1. The key win: one connection, many concurrent streams. No blocking.
2. HTTP/2 is transparent to application code — same headers/methods/status codes.
3. HTTP/3 (QUIC) solves TCP-level head-of-line blocking using UDP.

**Key takeaway:** HTTP/2 multiplexing allows concurrent requests on one connection, eliminating HTTP/1.1's head-of-line blocking and reducing connection overhead.

</details>

> 📖 **Theory:** [HTTP/2 vs HTTP/1](./01_what_is_an_api/story.md)

---

### Q18 · [Normal] · `http-connection-keepalive`

> **What is HTTP keep-alive? How does it reduce latency?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Keep-alive (persistent connections) reuses a TCP connection for multiple HTTP requests instead of opening a new connection for each request.

Without keep-alive: `TCP handshake → request → response → TCP teardown` for every request. Each TCP handshake adds ~1 RTT (round-trip time, e.g. 50ms).

With keep-alive: `TCP handshake → request1 → response1 → request2 → response2 → ... → TCP teardown`. One handshake amortised over many requests.

```http
Connection: keep-alive    ← client requests persistent connection (default in HTTP/1.1)
Connection: close         ← client/server signals end after this response
Keep-Alive: timeout=5, max=100   ← idle timeout 5s, max 100 requests
```

HTTP/1.1 enables keep-alive by default. HTTP/2 always uses a persistent connection with multiplexing (making keep-alive headers redundant).

**How to think through this:**
1. TCP handshake cost: ~1 RTT. For a 50ms RTT, opening a new connection per request wastes 50ms per request.
2. Connection pooling in DB clients and HTTP clients uses the same principle.
3. Load balancers need to be aware of persistent connections (sticky sessions may be needed).

**Key takeaway:** Keep-alive reuses TCP connections, eliminating per-request handshake overhead. Critical for high-throughput APIs — one handshake per multiple requests.

</details>

> 📖 **Theory:** [Keep-Alive](./01_what_is_an_api/story.md)

---

### Q19 · [Critical] · `pagination-response-format`

> **Design a standard paginated response format for a REST API. What fields should it always include?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```json
{
  "data": [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
  ],
  "pagination": {
    "page": 2,
    "per_page": 20,
    "total": 157,
    "total_pages": 8,
    "has_next": true,
    "has_prev": true
  },
  "_links": {
    "self": "/users?page=2&per_page=20",
    "next": "/users?page=3&per_page=20",
    "prev": "/users?page=1&per_page=20",
    "first": "/users?page=1&per_page=20",
    "last": "/users?page=8&per_page=20"
  }
}
```

For cursor-based:
```json
{
  "data": [...],
  "cursor": {
    "next_cursor": "eyJpZCI6IDIwfQ==",
    "has_next": true
  }
}
```

**Must-have fields:** `data` (the items), `has_next` (does next page exist), cursor or page/limit info.
**Nice-to-have:** `total`, `_links` with next/prev URLs.

**How to think through this:**
1. Always wrap results in `data` — allows adding metadata without breaking clients.
2. Include navigation info so clients don't have to reconstruct URLs.
3. For large datasets, omit `total` (requires expensive COUNT(*)) unless clients need it.

**Key takeaway:** Standard pagination response = `data` array + pagination metadata + navigation links. Wrap in `data` key from day one for forward compatibility.

</details>

> 📖 **Theory:** [Pagination Response](./09_api_performance_scaling/performance_guide.md)

---

### Q20 · [Normal] · `error-response-format`

> **What should a well-designed API error response look like? What fields should it always include?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
RFC 7807 (Problem Details for HTTP APIs) defines a standard:

```json
{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "The request body contains invalid fields.",
  "instance": "/orders/99",
  "errors": [
    {"field": "email", "message": "Invalid email format"},
    {"field": "age", "message": "Must be a positive integer"}
  ],
  "request_id": "550e8400-e29b-41d4-a716"
}
```

**Always include:**
- `status` (HTTP status code, mirrored in body for easy parsing)
- `title` (short human-readable summary)
- `detail` (longer explanation)
- `errors` (list of field-level errors for validation failures)
- `request_id` (correlation ID for debugging — client includes this when reporting issues)

**Avoid:**
- Stack traces in production
- Internal system details (DB column names, server paths)
- Inconsistent formats across endpoints

**How to think through this:**
1. Errors should be as actionable as the success responses — clients need to know what went wrong and how to fix it.
2. `request_id` is critical for support — clients report it, you search logs.
3. Validation errors need field-level detail, not just a generic message.

**Key takeaway:** Consistent error format with status, title, detail, field-level errors, and request_id. Never expose internal details (stack traces, DB errors) in production.

</details>

> 📖 **Theory:** [Error Response Format](./06_error_handling_standards/error_guide.md)

---

### Q21 · [Thinking] · `etag-conditional-requests`

> **What is an ETag? How do conditional requests use it to reduce bandwidth?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
An **ETag** (Entity Tag) is a unique identifier (hash or version) for a specific version of a resource. The server sends it in the response:

```http
HTTP/1.1 200 OK
ETag: "33a64df5"
Content-Type: application/json

{"id": 42, "name": "Alice", "updated_at": "2026-01-01"}
```

On subsequent requests, the client sends the ETag back:
```http
GET /users/42
If-None-Match: "33a64df5"
```

If the resource hasn't changed: `304 Not Modified` — no body. Client uses cached version.
If changed: `200 OK` with new body and new ETag.

**Bandwidth savings:** The full response body is only transferred when the resource actually changed. For large responses (lists, documents), this can be significant.

**ETags also enable optimistic locking:**
```http
PUT /users/42
If-Match: "33a64df5"    ← "only update if this version"
```
If ETag doesn't match (someone else modified it): `412 Precondition Failed`.

**How to think through this:**
1. ETag = version fingerprint of a resource.
2. Conditional GET: "give me the body only if it changed."
3. Conditional PUT/PATCH: "update only if my version is still current" — prevents lost updates.

**Key takeaway:** ETags enable conditional requests — 304 Not Modified saves bandwidth when resources haven't changed, and If-Match enables optimistic concurrency control.

</details>

> 📖 **Theory:** [ETags](./09_api_performance_scaling/performance_guide.md)

---

### Q22 · [Normal] · `rest-vs-rpc`

> **What is the difference between REST and RPC-style APIs? When would you choose an RPC approach?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- **REST**: resource-oriented. URLs represent nouns (things). HTTP methods represent actions. `GET /users/42`, `DELETE /orders/99`.
- **RPC (Remote Procedure Call)**: action-oriented. URLs represent verbs (operations). `POST /sendEmail`, `POST /calculateTax`, `POST /getUserById`.

**REST is preferred when:**
- The domain naturally maps to resources (CRUD operations on entities).
- External/public APIs where discoverability matters.
- Cache-ability is important.

**RPC is preferred when:**
- Operations don't map cleanly to CRUD (e.g. `sendEmail`, `calculateShipping`, `startVideoCall`).
- Internal microservice communication (gRPC is a typed RPC framework).
- Performance is critical and you control both client and server.

**Example of the tension:**
- REST: `POST /users/42/deactivate` (action as nested path — a compromise).
- RPC: `POST /deactivateUser` with `{"user_id": 42}`.
- gRPC: `rpc DeactivateUser(UserRequest) returns (UserResponse);`

**How to think through this:**
1. If operations are mostly CRUD on resources → REST.
2. If operations are complex actions not fitting CRUD → RPC or action endpoints.
3. gRPC is strongly typed RPC with protobuf — excellent for internal microservice communication.

**Key takeaway:** REST = noun-centric (resource URLs). RPC = verb-centric (action URLs). Use REST for public APIs; consider gRPC for internal microservice communication.

</details>

> 📖 **Theory:** [REST vs RPC](./02_rest_fundamentals/rest_explained.md)

---

### Q23 · [Normal] · `http-methods-safe`

> **A CDN is caching your API responses. Which HTTP methods should it cache and which should it never cache?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Cache-able (safe, idempotent reads):**
- `GET` — the primary cacheable method. Response can be cached by CDN, browser, and proxies.
- `HEAD` — same as GET but no body. CDN can cache.

**Never cache:**
- `POST` — creates/modifies state. Caching would return stale response for different inputs.
- `PUT` / `PATCH` / `DELETE` — write operations. Must reach the origin server.
- `OPTIONS` — preflight requests. Short TTL acceptable but generally not cached.

**CDN caching rules:**
- Cache only when `Cache-Control` allows it (e.g. `public, max-age=3600`).
- Don't cache responses with `Set-Cookie` (session cookies are user-specific).
- Don't cache responses with `Authorization` header in the request (user-specific data).
- `Vary: Accept-Encoding` tells CDN to cache separate copies for gzip vs non-gzip.

**How to think through this:**
1. Only safe methods (GET, HEAD) can be cached — they don't change state.
2. POST responses *can* technically be cached but almost never should be.
3. Always set explicit `Cache-Control` headers — don't rely on CDN defaults.

**Key takeaway:** CDNs should only cache GET/HEAD responses. Always set explicit Cache-Control headers — never cache authenticated or user-specific responses at the CDN level.

</details>

> 📖 **Theory:** [Safe HTTP Methods](./02_rest_fundamentals/rest_explained.md)

---

### Q24 · [Thinking] · `api-rate-limiting-headers`

> **What response headers should a rate-limited API return? What should the client do when it receives a 429?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Standard rate limiting headers:
```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100          ← max requests allowed in window
X-RateLimit-Remaining: 0        ← requests left in current window
X-RateLimit-Reset: 1714000000   ← Unix timestamp when limit resets
Retry-After: 30                 ← seconds until client can retry
```

**Client behaviour on 429:**
1. Read `Retry-After` header.
2. Stop all requests until the reset time.
3. Implement **exponential backoff with jitter** if `Retry-After` is not provided.
4. Do NOT immediately retry in a loop — this makes the rate limiting worse.

```python
import time, random

def retry_with_backoff(func, max_retries=5):
    for attempt in range(max_retries):
        result = func()
        if result.status_code == 429:
            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
            continue
        return result
```

**How to think through this:**
1. 429 = slow down. The `Retry-After` header tells you exactly how long to wait.
2. Exponential backoff prevents thundering herd — all clients backing off simultaneously and retrying simultaneously.
3. Jitter adds randomness to avoid synchronized retries.

**Key takeaway:** On 429, wait for `Retry-After` seconds then retry with exponential backoff + jitter. Never immediately retry in a tight loop.

</details>

> 📖 **Theory:** [Rate Limiting Headers](./09_api_performance_scaling/performance_guide.md)

---

### Q25 · [Normal] · `rest-response-envelope`

> **Should REST API responses always be wrapped in an envelope (e.g. `{"data": ..., "status": "success"}`)? What are the arguments for and against?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Arguments for envelopes:**
- Consistent structure: every response has the same shape regardless of content.
- Easy to add metadata (pagination, request_id, warnings) without breaking clients.
- Easier for some clients to handle (always parse `response.data`).

**Arguments against envelopes:**
- Redundant: HTTP already has status codes, headers for metadata. Wrapping duplicates this.
- Wastes bandwidth: extra JSON nesting for every response.
- HTTP-native clients (curl, browsers) already handle status codes — envelope adds no value.
- JSON:API and OpenAPI specs prefer direct resource representations.

**Modern best practice (most large APIs):**
- Successful responses: return the resource directly (no envelope).
  ```json
  {"id": 42, "name": "Alice"}          ← preferred for single resource
  {"data": [...], "pagination": {...}}  ← envelope useful for collections with metadata
  ```
- Error responses: always use a consistent envelope (RFC 7807).

**How to think through this:**
1. For single resources: no envelope needed — return the object directly.
2. For collections: light envelope useful for pagination metadata.
3. Never use `{"status": "success", "data": {...}}` on success — HTTP status code is already doing that job.

**Key takeaway:** Don't wrap single resources in envelopes — use HTTP status codes. Light envelope for collections (pagination metadata). Always wrap errors consistently.

</details>

> 📖 **Theory:** [Response Envelope](./03_rest_best_practices/patterns.md)

---

## 🔌 Tier 2 — FastAPI, Auth & Databases

---

### Q26 · [Normal] · `fastapi-dependency-injection`

> **What is dependency injection in FastAPI? Show how `Depends()` works with a simple example: a database session dependency injected into a route.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Dependency injection (DI)** is a pattern where FastAPI automatically calls a function and passes its return value into your route handler. `Depends()` is FastAPI's DI mechanism — you declare what a route needs, and the framework resolves it.

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal

def get_db():
    db = SessionLocal()       # ← open session
    try:
        yield db              # ← hand it to the route
    finally:
        db.close()            # ← always close, even on error

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):  # ← injected
    return db.query(User).filter(User.id == user_id).first()
```

**How to think through this:**
1. FastAPI sees `Depends(get_db)` and calls `get_db()` before your route runs.
2. The `yield` makes it a context manager — setup before yield, teardown after.
3. Dependencies can depend on other dependencies, forming a tree that FastAPI resolves automatically.

**Key takeaway:** `Depends()` decouples cross-cutting concerns (DB sessions, auth, config) from route logic — routes declare what they need, not how to build it.

</details>

> 📖 **Theory:** [Dependency Injection](./07_fastapi/core_guide.md)

---

### Q27 · [Thinking] · `pydantic-validation`

> **How does Pydantic validate request data in FastAPI? What happens when validation fails? What HTTP status code is returned and why?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
FastAPI passes raw incoming JSON to the **Pydantic model** constructor. Pydantic inspects every field's type annotation and validator, coercing where safe (e.g. `"42"` → `int`) and rejecting where not. On failure, FastAPI catches the `ValidationError` and returns a **422 Unprocessable Entity** — not 400, because the request was syntactically valid JSON (parseable) but semantically invalid (wrong shape or types).

**How to think through this:**
1. 400 Bad Request means the server could not parse the message at all (e.g., malformed JSON). The data arrived intact here — FastAPI could read it.
2. 422 specifically means "I understood the request, but the content fails business/type rules." This is the correct semantic distinction per HTTP spec.
3. Pydantic's `ValidationError` includes a structured list of field-level errors, which FastAPI forwards directly to the client as the response body.

**Key takeaway:** Pydantic catches type and constraint violations before your route code runs; FastAPI converts these into 422 responses with field-level error detail automatically.

</details>

> 📖 **Theory:** [Pydantic Validation](./07_fastapi/core_guide.md)

---

### Q28 · [Normal] · `fastapi-path-vs-query`

> **What is the difference between path parameters and query parameters in FastAPI? Give an example of each and when you'd use one vs the other.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **path parameter** is part of the URL path and identifies a specific resource. A **query parameter** is appended after `?` and filters or modifies the request.

```python
@app.get("/users/{user_id}")           # ← path param: identifies the resource
def get_user(user_id: int):
    ...

@app.get("/users")                     # ← query params: filter the collection
def list_users(active: bool = True, page: int = 1):
    ...
# Called as: GET /users?active=true&page=2
```

**How to think through this:**
1. Use a path parameter when the value uniquely identifies a resource — `/orders/99` leaves no ambiguity about which order.
2. Use query parameters for optional filters, pagination, sorting, or search — things that narrow a collection without changing the resource identity.
3. Path parameters are always required (they're part of the route match). Query parameters are typically optional with defaults.

**Key takeaway:** Path params identify; query params filter — if removing the value makes the URL meaningless, it's a path param.

</details>

> 📖 **Theory:** [Path vs Query Parameters](./07_fastapi/core_guide.md)

---

### Q29 · [Normal] · `fastapi-request-body`

> **How does FastAPI parse a JSON request body? Show a Pydantic model definition and how it maps to a POST endpoint. What happens if a required field is missing?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
FastAPI reads the raw request body, parses it as JSON, and passes it to the **Pydantic model** constructor. Any field without a default value is required. If a required field is missing, Pydantic raises a `ValidationError` and FastAPI returns a 422 with a body listing exactly which fields are missing.

```python
from pydantic import BaseModel
from fastapi import FastAPI

class CreateUserRequest(BaseModel):
    name: str                  # ← required (no default)
    email: str                 # ← required
    age: int = 18              # ← optional, defaults to 18

app = FastAPI()

@app.post("/users")
def create_user(body: CreateUserRequest):   # ← FastAPI detects BaseModel → reads body
    return {"name": body.name, "email": body.email}

# POST /users {"name": "Alice"}  →  422, "email" field required
```

**How to think through this:**
1. FastAPI distinguishes body from path/query params by type: a `BaseModel` subclass → body; a plain `int` or `str` → path or query.
2. Required fields are those with no default — Pydantic enforces this at instantiation time, before your route code runs.
3. The 422 response body names the missing field and its location (`body > email`), making client debugging straightforward.

**Key takeaway:** Declare a Pydantic model, type-hint the parameter with it, and FastAPI handles parsing, validation, and error responses automatically.

</details>

> 📖 **Theory:** [Request Body](./07_fastapi/core_guide.md)

---

### Q30 · [Thinking] · `fastapi-response-models`

> **What is the purpose of a `response_model` in FastAPI? How does it differ from the function's return type annotation? What does it protect against?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
`response_model` tells FastAPI to **filter and validate the output** before sending it to the client. The function's return type annotation is a Python hint for static analysis only — FastAPI does not enforce it at runtime. `response_model` actively strips any fields not declared in the model, protecting against accidental data leakage.

**How to think through this:**
1. Imagine your route returns an ORM `User` object that has a `hashed_password` field. If you return it directly without a `response_model`, that field goes to the client.
2. Setting `response_model=UserPublic` (a model without `hashed_password`) causes FastAPI to serialize through that model, silently dropping sensitive fields.
3. The return type annotation (e.g., `-> UserPublic`) is purely for IDEs and mypy — FastAPI does not call Pydantic on it at request time.

**Key takeaway:** `response_model` is a security filter at the serialization boundary — use it to guarantee what your API reveals, not just what it intends to reveal.

</details>

> 📖 **Theory:** [Response Models](./07_fastapi/core_guide.md)

---

### Q31 · [Normal] · `http-auth-schemes`

> **Name and explain three HTTP authentication schemes: Basic, Bearer token, and API Key. What are the security tradeoffs of each?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Basic Auth**: sends `username:password` base64-encoded in the `Authorization` header on every request. Simple but credentials travel with every call — requires HTTPS, no revocation without password change.

**Bearer token** (JWT or opaque): sends a token in `Authorization: Bearer <token>`. Short-lived, revocable (if opaque + server-side lookup), stateless (if JWT). Dominant for modern APIs.

**API Key**: a static secret sent in a header (`X-API-Key`) or query param. Simple to implement, but keys are long-lived and hard to rotate without breaking clients. Best for server-to-server or developer tool access.

**How to think through this:**
1. Basic Auth exposes credentials on every request — acceptable only for internal tooling or simple scripts, never for user-facing flows.
2. Bearer tokens decouple identity from credentials — the token proves prior authentication without re-sending the password.
3. API keys are credentials themselves — if leaked they grant full access until manually revoked, so they need secure storage and rotation policies.

**Key takeaway:** Bearer tokens balance security and statelesness for user APIs; API keys suit machine-to-machine access with explicit rotation policies.

</details>

> 📖 **Theory:** [Auth Schemes](./05_authentication/securing_apis.md)

---

### Q32 · [Normal] · `jwt-structure`

> **What are the three parts of a JWT? What is stored in each part? Why is the payload not encrypted by default, and what does this mean for what you should store in it?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **JWT** has three Base64URL-encoded parts separated by dots: `header.payload.signature`.

- **Header**: token type (`JWT`) and signing algorithm (`HS256`, `RS256`)
- **Payload**: **claims** — `sub` (subject/user ID), `exp` (expiry), `iat` (issued at), plus any custom claims
- **Signature**: HMAC or RSA signature over `header + payload`, verifying integrity and authenticity

The payload is **encoded, not encrypted** — anyone with the token can decode it with `base64url_decode()`. The signature only proves it wasn't tampered with, not that it's secret.

**How to think through this:**
1. Never store sensitive data in the payload: passwords, SSNs, credit card numbers — these are readable by anyone who intercepts or holds the token.
2. Store only what you need for authorization decisions: user ID, roles, tenant ID.
3. If you need confidential claims, use JWE (JSON Web Encryption) — a separate standard on top of JWT.

**Key takeaway:** JWT payloads are public — sign them to prove authenticity, but never treat encoding as encryption.

</details>

> 📖 **Theory:** [JWT Structure](./05_authentication/securing_apis.md)

---

### Q33 · [Thinking] · `jwt-access-refresh-tokens`

> **Why use two tokens (access + refresh) instead of one long-lived token? What is the typical lifetime for each and why? Where should each be stored on the client?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A single long-lived token is a security liability — if stolen, the attacker has access for days or weeks. The **access + refresh** pattern solves this with separation of concerns: the **access token** is short-lived (15 minutes typical) and sent on every API call; the **refresh token** is long-lived (7–30 days) and used only to get a new access token.

**How to think through this:**
1. Short access token lifetime limits the blast radius of theft — a stolen token expires quickly without any server-side action needed.
2. The refresh token never travels to the API server directly, reducing its exposure surface. It goes only to the auth endpoint.
3. Storage: access token in memory (JavaScript variable) — fast, not persisted; refresh token in an `HttpOnly` cookie — inaccessible to JavaScript, protecting against XSS. Never store either in `localStorage` for sensitive applications.

**Key takeaway:** Short-lived access tokens limit theft damage; refresh tokens extend sessions without re-authentication — keep them in HttpOnly cookies, not localStorage.

</details>

> 📖 **Theory:** [Access & Refresh Tokens](./05_authentication/securing_apis.md)

---

### Q34 · [Normal] · `oauth2-authorization-code`

> **Explain the OAuth2 authorization code flow in 4 steps. What is the authorization code and why is it short-lived? When would you use this flow vs client credentials?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The **authorization code flow** delegates user login to an identity provider:

1. Your app redirects the user to the auth server with `client_id`, `redirect_uri`, `scope`, and a `state` nonce.
2. User authenticates and consents; auth server redirects back to your `redirect_uri` with a short-lived **authorization code**.
3. Your backend exchanges the code for access + refresh tokens via a server-to-server POST (includes `client_secret`).
4. Your backend uses the access token to call the resource server on the user's behalf.

The **authorization code** is short-lived (seconds to minutes) because it travels through the browser (URL redirect) — limiting exposure if intercepted. The actual tokens are exchanged server-to-server, never exposed in the browser.

Use **client credentials** for machine-to-machine flows where there is no human user — background jobs, microservices calling internal APIs.

**How to think through this:**
1. The code is a one-time voucher — it proves the user consented but has no power itself.
2. The `client_secret` is only added at step 3, server-side — never exposed to the browser.
3. `state` parameter prevents CSRF attacks on the redirect.

**Key takeaway:** Authorization code flow = user-facing login via browser; client credentials = machine-to-machine with no user involved.

</details>

> 📖 **Theory:** [OAuth2 Flow](./05_authentication/securing_apis.md)

---

### Q35 · [Interview] · `api-key-vs-jwt`

> **Compare API keys vs JWTs for API authentication. What are the tradeoffs? When would you use each in production?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**API keys** are opaque static strings — simple to issue, simple to check (database lookup), easy to revoke instantly. They carry no information themselves. **JWTs** are self-contained tokens — they encode claims (user ID, roles, expiry) and are verified cryptographically without a database lookup.

**How to think through this:**
1. API keys require a DB lookup on every request to resolve identity and permissions — adds latency but enables instant revocation. JWTs are verified locally (signature check only) — faster, but revoking requires a denylist or waiting for expiry.
2. JWTs scale better horizontally: any server with the public key can verify — no shared session store needed. API keys need all servers to reach the same key store.
3. Use API keys when: developer/partner access, long-lived machine clients, when instant revocation is non-negotiable. Use JWTs when: user sessions, microservice auth, short-lived tokens where statelessness matters.

**Key takeaway:** API keys for simple revocable machine access; JWTs for stateless distributed auth — the tradeoff is instant revocability vs. zero-lookup verification speed.

</details>

> 📖 **Theory:** [API Key vs JWT](./05_authentication/securing_apis.md)

---

### Q36 · [Thinking] · `db-connection-pooling`

> **Why does every API need database connection pooling? What happens without it at high traffic? What parameters does a pool have and what do they control?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Opening a database connection is expensive — TCP handshake, authentication, session setup — typically 20–100ms. A **connection pool** maintains a set of open, reusable connections so requests grab one instantly and return it when done.

Without pooling at high traffic: each request opens a new connection, the DB hits its `max_connections` limit, new connection attempts fail or queue indefinitely, latency spikes, and the DB process memory is exhausted.

Key pool parameters:
- `pool_size`: number of persistent connections kept open
- `max_overflow`: extra connections allowed above `pool_size` under burst load
- `pool_timeout`: how long to wait for a connection before raising an error
- `pool_recycle`: max lifetime of a connection (prevents stale/dropped connections)

**How to think through this:**
1. Think of the pool as a taxi rank — cabs wait for passengers rather than being summoned from the garage on every trip.
2. `pool_size` should match your steady-state concurrency, not your peak — overflow handles spikes.
3. `pool_recycle` is critical in cloud environments where network appliances silently kill idle TCP connections after a few minutes.

**Key takeaway:** Connection pools trade memory (idle connections) for latency and DB stability — size them for steady state, not peak, and always set a recycle time.

</details>

> 📖 **Theory:** [DB Connection Pooling](./07_fastapi/database_guide.md)

---

### Q37 · [Interview] · `orm-vs-raw-sql`

> **Compare using an ORM (SQLAlchemy) vs raw SQL in an API. What are the tradeoffs in terms of: safety, performance, flexibility, maintainability?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**SQLAlchemy ORM** maps Python objects to tables, generates SQL automatically, and handles parameterization. **Raw SQL** means writing queries as strings and executing them directly.

**How to think through this:**
1. **Safety**: ORMs parameterize by default — SQL injection requires deliberate effort. Raw SQL requires explicit parameterization discipline; one `f"...{user_input}"` and you're vulnerable.
2. **Performance**: ORMs generate portable but sometimes suboptimal SQL. Complex queries (window functions, CTEs, bulk upserts) are faster and cleaner in raw SQL. ORMs can also cause N+1 problems silently.
3. **Flexibility**: Raw SQL has none of the ORM's constraints — any query the DB supports, you can write. ORMs abstract the DB dialect but leak abstractions on complex queries.
4. **Maintainability**: ORMs keep schema and code in sync via migrations (Alembic). Raw SQL scatters schema knowledge across query strings, making refactors painful.

Use ORM for standard CRUD and relationship navigation. Drop to raw SQL (or SQLAlchemy Core) for complex analytics, bulk operations, or performance-critical paths.

**Key takeaway:** Start with ORM for safety and maintainability; reach for raw SQL only where the ORM's generated queries become a bottleneck or limitation.

</details>

> 📖 **Theory:** [ORM vs Raw SQL](./07_fastapi/database_guide.md)

---

### Q38 · [Critical] · `n-plus-one-query`

> **What is the N+1 query problem in APIs? Show a code example that triggers it and explain how to fix it with eager loading.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The **N+1 problem** occurs when fetching a list of N records triggers N additional queries — one per record — to fetch related data. Total: N+1 queries instead of 2.

```python
# BAD — N+1 problem
@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()          # ← 1 query: fetch all orders
    result = []
    for order in orders:
        result.append({
            "id": order.id,
            "user": order.user.name         # ← N queries: lazy loads user per order
        })
    return result

# GOOD — eager loading with joinedload
from sqlalchemy.orm import joinedload

@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).options(
        joinedload(Order.user)              # ← JOIN in a single query
    ).all()
    return [{"id": o.id, "user": o.user.name} for o in orders]
```

**How to think through this:**
1. Lazy loading is SQLAlchemy's default — accessing `.user` on an `Order` fires a new `SELECT` on the spot.
2. With 1000 orders, you fire 1001 queries. Each has network round-trip cost to the DB — this is the silent killer of API performance.
3. `joinedload` or `selectinload` tells SQLAlchemy to fetch relationships upfront in one (or two) queries regardless of collection size.

**Key takeaway:** Any time you iterate over a collection and access a relationship inside the loop, you have an N+1 — fix it with eager loading at the query level.

</details>

> 📖 **Theory:** [N+1 Query Problem](./07_fastapi/database_guide.md)

---

### Q39 · [Thinking] · `db-transactions-rest`

> **When should a REST endpoint use a database transaction? What are the ACID properties and which one prevents partial writes if the server crashes mid-request?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Use a transaction whenever an endpoint performs **multiple writes that must succeed or fail together** — e.g., debit one account and credit another, create an order and decrement inventory. A partial write leaves the database in an inconsistent state.

**ACID properties:**
- **Atomicity**: all operations in the transaction commit together, or none do
- **Consistency**: the DB moves from one valid state to another, never an invalid intermediate
- **Isolation**: concurrent transactions don't see each other's uncommitted changes
- **Durability**: once committed, data survives crashes

**Atomicity** is the property that prevents partial writes on crash — if the server dies after the debit but before the credit, the transaction is rolled back on recovery.

**How to think through this:**
1. Single-row updates don't need explicit transactions — most DBs wrap single statements in an implicit transaction.
2. Any endpoint that touches 2+ tables or 2+ rows in a cause-and-effect relationship needs an explicit `BEGIN ... COMMIT` block.
3. In SQLAlchemy: use `db.begin()` or rely on the session's unit-of-work pattern — `db.commit()` on success, `db.rollback()` in the `except` block.

**Key takeaway:** Atomicity is the ACID property that saves you from partial writes — if two writes must both happen or neither happen, wrap them in a transaction.

</details>

> 📖 **Theory:** [Transactions](./07_fastapi/database_guide.md)

---

### Q40 · [Thinking] · `fastapi-async-endpoints`

> **In FastAPI, when should you use `async def` vs `def` for an endpoint? What happens if you use `async def` with a blocking database call inside it?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Use `async def` when your endpoint calls **async-native libraries** (e.g., `asyncpg`, `httpx` async client, `aioredis`). Use plain `def` when using synchronous libraries (e.g., standard SQLAlchemy ORM with `psycopg2`).

If you use `async def` with a **blocking call** inside (e.g., a synchronous SQLAlchemy query that does network I/O), you block the entire event loop — all other concurrent requests stall until your DB call returns.

**How to think through this:**
1. FastAPI runs `def` endpoints in a thread pool automatically, so synchronous blocking calls don't touch the event loop.
2. `async def` runs on the event loop directly — blocking it is catastrophic for throughput because the event loop is single-threaded.
3. If you must mix: wrap blocking calls in `asyncio.run_in_executor()` to offload them to a thread, or switch to an async DB driver (SQLAlchemy 2.0 async mode with `asyncpg`).

**Key takeaway:** `async def` + blocking I/O = event loop starvation; use `async def` only with truly async-native libraries, or use `def` and let FastAPI thread-pool it safely.

</details>

> 📖 **Theory:** [Async Endpoints](./07_fastapi/advanced_guide.md)

---

### Q41 · [Normal] · `fastapi-background-tasks`

> **What are FastAPI BackgroundTasks? Give a use case where you'd use them instead of a task queue like Celery. What is the limitation?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**BackgroundTasks** let you schedule a function to run after the response is sent to the client — the request returns immediately without waiting for the task to finish.

```python
from fastapi import FastAPI, BackgroundTasks

def send_welcome_email(email: str):
    # slow email-sending logic here
    ...

@app.post("/users")
def create_user(user: CreateUserRequest, background_tasks: BackgroundTasks):
    db_create_user(user)
    background_tasks.add_task(send_welcome_email, user.email)  # ← runs after response
    return {"status": "created"}
```

Use BackgroundTasks for: sending a welcome email, logging analytics events, triggering a lightweight webhook notification — tasks that are fast, non-critical, and don't need retry logic.

**Limitation**: the task runs in the same process as your API server. If the server restarts mid-task, the task is lost. No retry, no persistence, no queue. For reliability, use Celery + Redis/RabbitMQ.

**How to think through this:**
1. BackgroundTasks are appropriate when losing the occasional task is acceptable.
2. They don't scale independently — you can't add workers without adding API servers.
3. Celery is the right tool when tasks are slow (>1s), need retries, or must be auditable.

**Key takeaway:** BackgroundTasks for fire-and-forget lightweight work; Celery for durable, retryable, scalable task execution.

</details>

> 📖 **Theory:** [Background Tasks](./07_fastapi/advanced_guide.md)

---

### Q42 · [Normal] · `fastapi-middleware`

> **What is middleware in FastAPI? Give three real use cases for middleware. How does the request/response flow through middleware layers?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Middleware** is a function that wraps every request/response cycle — it runs before your route handler and again after it returns. Think of it as a pipeline each request passes through in both directions.

```python
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)          # ← passes to next layer / route
    duration = time.time() - start
    response.headers["X-Process-Time"] = str(duration)
    return response
```

Flow: Client → Middleware 1 (in) → Middleware 2 (in) → Route Handler → Middleware 2 (out) → Middleware 1 (out) → Client

Three real use cases:
1. **Request timing / logging** — capture method, path, status code, duration on every call
2. **CORS headers** — add `Access-Control-Allow-Origin` before any route runs
3. **Request ID injection** — generate a UUID per request, attach to headers and logging context for traceability

**How to think through this:**
1. Middleware stacks like an onion — first registered is outermost (first in, last out).
2. `call_next` hands control to the next middleware or the route; everything after it is the "response" side.
3. Don't do heavy blocking work in middleware — it runs on every single request.

**Key takeaway:** Middleware is the right place for cross-cutting concerns that apply to every route: logging, auth headers, CORS, request tracing.

</details>

> 📖 **Theory:** [Middleware](./07_fastapi/advanced_guide.md)

---

### Q43 · [Critical] · `cors-fastapi`

> **You add CORS middleware to your FastAPI app with `allow_origins=["*"]`. A browser still gets a CORS error on a DELETE request. Why? What is a preflight request?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The browser is sending a **preflight request** — an `OPTIONS` request it fires automatically before "non-simple" methods (DELETE, PUT, PATCH, or any request with custom headers). `allow_origins=["*"]` permits origins but does not automatically permit all methods.

The fix: explicitly allow the method.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # ← must include DELETE explicitly
    allow_headers=["*"],
)
```

**How to think through this:**
1. "Simple" requests (GET, POST with standard content types) don't trigger a preflight — the browser just sends them.
2. DELETE, PUT, PATCH and any request with custom headers (e.g., `Authorization`) trigger a preflight `OPTIONS` call first.
3. The preflight asks: "Server, will you accept a DELETE from this origin?" If the CORS middleware doesn't include DELETE in `allow_methods`, it responds with no CORS headers, and the browser blocks the actual request.

**Key takeaway:** `allow_origins=["*"]` is not enough — you must also explicitly list allowed methods; DELETE/PUT/PATCH require a preflight that wildcards on origins don't automatically satisfy.

</details>

> 📖 **Theory:** [CORS in FastAPI](./11_api_security_production/security_hardening.md)

---

### Q44 · [Normal] · `validation-error-422`

> **When does FastAPI return a 422 Unprocessable Entity? What does the error response body look like? How would you customise the error format globally?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
FastAPI returns **422** when Pydantic validation fails on path params, query params, or request body — the request arrived correctly but its data fails type or constraint checks.

Default response body:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

To customise globally, override the exception handler:

```python
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_failed",
            "fields": [
                {"field": ".".join(str(l) for l in e["loc"]), "message": e["msg"]}
                for e in exc.errors()
            ]
        }
    )
```

**How to think through this:**
1. The `loc` array traces the exact location of the error: `["body", "email"]` means the `email` field in the request body.
2. You can map these to any format your clients expect — RFC 7807, a custom schema, etc.
3. Override only `RequestValidationError`, not the base `Exception`, to avoid catching unrelated errors.

**Key takeaway:** FastAPI's 422 includes structured per-field errors in `detail`; override `RequestValidationError` handler to reformat them to match your API's error contract.

</details>

> 📖 **Theory:** [Validation Errors](./07_fastapi/core_guide.md)

---

### Q45 · [Design] · `fastapi-router-organization`

> **How would you organise a FastAPI application with 50+ endpoints across 5 domains (users, orders, products, auth, admin)? Show the router structure.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Use **APIRouter** per domain, each in its own module, then include them in a central `main.py`.

```
app/
├── main.py
├── routers/
│   ├── users.py
│   ├── orders.py
│   ├── products.py
│   ├── auth.py
│   └── admin.py
├── models/
├── schemas/
└── dependencies/
    └── auth.py        # ← shared Depends() like get_current_user
```

```python
# routers/users.py
from fastapi import APIRouter, Depends
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}")
def get_user(user_id: int): ...

# main.py
from fastapi import FastAPI
from routers import users, orders, products, auth, admin

app = FastAPI()
app.include_router(auth.router)
app.include_router(users.router, dependencies=[Depends(require_auth)])    # ← auth on all user routes
app.include_router(orders.router, dependencies=[Depends(require_auth)])
app.include_router(admin.router, dependencies=[Depends(require_admin)])   # ← stricter for admin
app.include_router(products.router)                                       # ← public
```

**How to think through this:**
1. `prefix` on the router means you never repeat `/users` in every route decorator.
2. `dependencies` at `include_router` level applies auth to every route in that router — cleaner than decorating each endpoint.
3. `tags` groups endpoints in the auto-generated `/docs` Swagger UI.

**Key takeaway:** One APIRouter per domain with a shared prefix and tag; apply cross-cutting dependencies at `include_router` time to avoid repetition across 50+ routes.

</details>

> 📖 **Theory:** [Router Organization](./07_fastapi/core_guide.md)

---

### Q46 · [Design] · `dependency-injection-auth`

> **Show how to implement a `get_current_user` dependency in FastAPI that: reads the JWT from the Authorization header, validates it, and returns the user object. How do you use it across multiple routes?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

SECRET_KEY = "your-secret"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")  # ← tells /docs where to get tokens

def get_current_user(
    token: str = Depends(oauth2_scheme),   # ← extracts Bearer token from header
    db: Session = Depends(get_db)
):
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")   # ← extract subject claim
        if user_id is None:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exc
    return user                             # ← injected into route as-is

# Usage across routes
@app.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@app.delete("/account")
def delete_account(current_user: User = Depends(get_current_user)):
    ...
```

**How to think through this:**
1. `OAuth2PasswordBearer` is a convenience dependency that extracts the token from `Authorization: Bearer <token>` and integrates with FastAPI's `/docs` UI.
2. Decode first, then DB lookup — fail fast on invalid signatures before touching the database.
3. Any route that declares `current_user: User = Depends(get_current_user)` is automatically protected — no middleware needed.

**Key takeaway:** Encapsulate JWT validation in one `Depends()` function; inject it into any route that needs authentication — change auth logic once, applies everywhere.

</details>

> 📖 **Theory:** [Auth Dependency](./07_fastapi/core_guide.md)

---

### Q47 · [Normal] · `testing-fastapi-testclient`

> **How do you test a FastAPI endpoint with TestClient? Show a test for a POST /users endpoint. How do you override a dependency (e.g., the database) in tests?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**TestClient** wraps your FastAPI app with a `requests`-compatible interface — no server needed, runs in-process.

```python
from fastapi.testclient import TestClient
from main import app, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test DB setup
engine = create_engine("sqlite:///:memory:")
TestingSession = sessionmaker(bind=engine)

def override_get_db():           # ← replacement dependency for tests
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db   # ← swap real DB for test DB

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/users",
        json={"name": "Alice", "email": "alice@example.com"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "alice@example.com"

# Cleanup after tests
app.dependency_overrides.clear()
```

**How to think through this:**
1. `dependency_overrides` is a dict on the app — map the real dependency callable to the test replacement.
2. Use an in-memory SQLite DB for speed and isolation; recreate tables per test session with `Base.metadata.create_all(engine)`.
3. TestClient can also test auth by passing `headers={"Authorization": "Bearer <test_token>"}`.

**Key takeaway:** `app.dependency_overrides` is FastAPI's test seam — swap any `Depends()` with a test double without touching production code.

</details>

> 📖 **Theory:** [Testing FastAPI](./10_testing_documentation/testing_apis.md)

---

### Q48 · [Normal] · `pydantic-settings`

> **How does Pydantic Settings work for environment-based configuration? Show a Settings class that reads DATABASE_URL and SECRET_KEY from environment variables. Why is this better than `os.getenv()`?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Pydantic Settings** reads environment variables (and `.env` files) and validates them using the same Pydantic type system — you get type coercion, required-field enforcement, and IDE autocomplete for free.

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str                  # ← required; raises on startup if missing
    secret_key: str                    # ← required
    debug: bool = False                # ← optional with default
    token_expire_minutes: int = 30

    class Config:
        env_file = ".env"              # ← also loads from .env file in dev

@lru_cache                             # ← parse once, reuse everywhere
def get_settings() -> Settings:
    return Settings()

# Usage in route via dependency
@app.get("/info")
def info(settings: Settings = Depends(get_settings)):
    return {"debug": settings.debug}
```

Better than `os.getenv()` because:
1. `os.getenv("DATABASE_URL")` returns `None` silently if the variable is missing — you discover this at runtime, deep in a call stack.
2. Pydantic Settings fails loudly at startup with a clear error listing every missing variable.
3. Type coercion: `DATABASE_POOL_SIZE=10` (a string in env) is automatically cast to `int`.

**How to think through this:**
1. The problem with `os.getenv()`: it returns `None` silently, pushing config errors to runtime instead of startup.
2. Pydantic Settings solves this by treating config as a typed model — missing required vars cause an immediate startup failure with a clear message.
3. The `@lru_cache` pattern ensures the settings are parsed once and reused — no repeated env var reads.

**Key takeaway:** Pydantic Settings moves config failures from runtime surprises to startup-time validation with typed, documented settings as a first-class object.

</details>

> 📖 **Theory:** [Pydantic Settings](./07_fastapi/core_guide.md)

---

### Q49 · [Design] · `api-logging-patterns`

> **What should an API log on every request and response? Design a logging middleware that captures: method, path, status code, duration, and request ID. Why is a request ID important?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Every request/response log line should capture: timestamp, **request ID**, method, path, status code, duration (ms), and client IP. Optionally: user ID (from JWT), response size.

```python
import time, uuid, logging
from fastapi import Request

logger = logging.getLogger("api")

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())                        # ← unique per request
    request.state.request_id = request_id                 # ← available to route handlers

    start = time.monotonic()
    response = await call_next(request)
    duration_ms = (time.monotonic() - start) * 1000

    logger.info(
        "request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        }
    )

    response.headers["X-Request-ID"] = request_id        # ← return to client
    return response
```

A **request ID** is critical because: distributed systems process requests across multiple services and log aggregators. Without a shared ID, you cannot correlate the API log line, the DB query log, the downstream service call, and the error trace for a single user request. With one, you grep once and see the full story.

**How to think through this:**
1. Log at the middleware level so every route is covered without opt-in.
2. Use structured logging (JSON) rather than strings — log aggregators (Datadog, CloudWatch) can filter and aggregate on structured fields.
3. Return the request ID in the response header so clients can include it in support tickets.

**Key takeaway:** A request ID is the thread that stitches together all log lines for one transaction across services — without it, distributed debugging is archaeology.

</details>

> 📖 **Theory:** [API Logging](./12_production_deployment/deployment_guide.md)

---

### Q50 · [Thinking] · `fastapi-lifespan`

> **What is a FastAPI lifespan event? How do you use it to open a database connection pool on startup and close it on shutdown? Why is this better than using `@app.on_event`?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **lifespan** is a context manager that wraps the entire lifetime of the FastAPI application — code before `yield` runs on startup, code after `yield` runs on shutdown. It replaces the deprecated `@app.on_event("startup")` / `@app.on_event("shutdown")` decorators.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)   # ← create tables if not exist
    print("DB pool opened")
    yield                                    # ← app runs here
    # Shutdown
    engine.dispose()                         # ← close all pooled connections
    print("DB pool closed")

app = FastAPI(lifespan=lifespan)
```

**Why it's better than `@app.on_event`:**
1. `@app.on_event` is **deprecated** as of FastAPI 0.93 — lifespan is the official replacement.
2. Lifespan uses standard Python context manager semantics — easier to test, compose, and reason about.
3. Startup and shutdown logic live together in one function, not split across two decorated functions — the relationship between setup and teardown is explicit.
4. Works cleanly with `pytest` using `TestClient` as a context manager — the lifespan runs exactly once per test session.

**How to think through this:**
1. `engine.dispose()` on shutdown is critical — without it, connections stay open past the process lifecycle, leaking resources on the DB server.
2. Any resource that needs paired open/close (connection pools, HTTP client sessions, cache connections) belongs in the lifespan.
3. You can share state between startup and routes via `app.state`: `app.state.db_pool = pool` before yield, then access it in routes.

**Key takeaway:** FastAPI lifespan is a single context manager that owns startup and shutdown together — use it for all resource lifecycle management instead of the deprecated `on_event` hooks.

</details>

> 📖 **Theory:** [Lifespan Events](./07_fastapi/advanced_guide.md)

---

## ⚡ Tier 3 — Caching, Async, GraphQL & Advanced

---

### Q51 · [Normal] · `api-caching-strategies`

> **Name and explain three levels of API caching: client-side, CDN/edge, and server-side. What HTTP headers control client and CDN caching?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**Client-side caching** stores responses in the browser or HTTP client. The client reuses the response without hitting the network at all. Controlled by `Cache-Control: max-age=3600` (how long to cache) and `ETag` / `Last-Modified` (conditional revalidation).

**CDN/edge caching** stores responses at geographically distributed nodes close to users. Requests are served from the edge without reaching your origin server. CDN respects `Cache-Control: public, max-age=86400` and `Surrogate-Control` headers. `Vary` tells CDNs which request headers affect the response (e.g. `Vary: Accept-Encoding`).

**Server-side caching** sits inside your infrastructure — typically Redis or Memcached in front of your database. Your application code checks the cache before hitting the DB. Not visible to HTTP; controlled entirely by your application logic.

**Key HTTP headers:**
- `Cache-Control: max-age=N` — how long the response is fresh (client + CDN)
- `Cache-Control: public` — CDN may cache this; `private` — only the end client may cache
- `ETag` — fingerprint of the response; client sends `If-None-Match` on next request
- `Last-Modified` / `If-Modified-Since` — time-based conditional GET
- `Vary` — tells caches which request headers differentiate responses

**How to think through this:**
1. Think of caching as layers: furthest from your server = fastest and cheapest.
2. Client-side removes the network call entirely; CDN removes the origin server load; server-side removes the DB query.
3. Each layer needs different invalidation strategies — CDN purge APIs, TTL expiry, or event-driven cache busting.

**Key takeaway:** Cache at the earliest layer possible — every layer closer to the user is cheaper and faster than the one behind it.

</details>

> 📖 **Theory:** [Caching Strategies](./09_api_performance_scaling/performance_guide.md)

---

### Q52 · [Design] · `redis-caching-pattern`

> **Show the cache-aside pattern in Python using Redis for caching a user profile. Include: cache check, database fallback, cache write, and TTL. What is the risk of this pattern?**

```python
import json
import redis
import time

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def get_user_profile(user_id: int) -> dict:
    cache_key = f"user:profile:{user_id}"  # ← namespaced key prevents collisions

    cached = r.get(cache_key)              # ← Step 1: check cache first
    if cached:
        return json.loads(cached)          # ← cache hit: skip DB entirely

    # Step 2: cache miss — fall through to database
    user = db.query("SELECT * FROM users WHERE id = %s", user_id)
    if not user:
        return None

    # Step 3: write to cache with TTL
    r.setex(                               # ← setex = SET + EXpiry in one atomic call
        cache_key,
        300,                               # ← TTL: 300 seconds (5 minutes)
        json.dumps(user)
    )
    return user

def invalidate_user_cache(user_id: int):
    r.delete(f"user:profile:{user_id}")    # ← call this whenever user is updated
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**

The **cache-aside pattern** (also called lazy loading) means the application is responsible for loading data into the cache. The cache does not talk to the database itself.

Flow: check cache → on miss, read DB → write result to cache → return data.

**The main risks:**

1. **Cache stampede (thundering herd):** If the cache key expires and 1,000 requests arrive simultaneously, all 1,000 see a cache miss and hammer the DB at the same time. Mitigation: use a **mutex lock** (Redis `SET NX`) so only one request populates the cache; the others wait.

2. **Stale data:** The cache holds an old version of the user if the DB is updated but the cache is not invalidated. You must explicitly call `invalidate_user_cache()` on every write path — if you miss one write path, the cache serves stale data indefinitely until TTL expires.

3. **Cold start:** After a deployment or cache flush, every request is a cache miss until the cache warms up, causing a DB spike.

**How to think through this:**
1. Trace the happy path (cache hit) and the failure path (cache miss) separately.
2. Ask: what happens if two requests miss at the same time? → stampede risk.
3. Ask: what happens if a write occurs but the cache isn't invalidated? → stale data risk.

**Key takeaway:** Cache-aside is simple and widely used, but you must handle stampedes with locking and stale data with disciplined invalidation on every write path.

</details>

> 📖 **Theory:** [Redis Cache-Aside](./09_api_performance_scaling/performance_guide.md)

---

### Q53 · [Thinking] · `cache-invalidation`

> **Why is cache invalidation considered one of the hardest problems in computing? Describe three scenarios where stale data in an API cache causes real bugs.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

Phil Karlton's famous quote: "There are only two hard things in Computer Science: cache invalidation and naming things."

The difficulty is fundamental: a cache is a **copy** of data, and maintaining consistency between a copy and the source of truth requires knowing — at the moment data changes — every cache that holds a stale copy, and invalidating all of them immediately. In distributed systems, this is hard because:
- Multiple services may cache the same data independently
- Network partitions can prevent invalidation messages from arriving
- Invalidation logic is spread across many write paths and can be missed
- Time-based TTL is a blunt instrument — data may change before TTL expires or not change at all when it does

**Three scenarios where stale cache causes real bugs:**

1. **Permissions cache:** A user's role is cached for 10 minutes. An admin revokes their access at 9:58. For 2 more minutes, every request hits the cache and the user remains authorized. This is a **security bug**, not just a UX issue.

2. **Price cache on an e-commerce API:** Product prices are cached at the CDN level. A flash sale drops the price at 12:00. Users who hit cached nodes see the old price, pay the old price, but the order system writes the correct sale price. Now you have order/pricing inconsistency and refund logic to write.

3. **Idempotency record cache:** A payment service caches "this idempotency key was already processed = success." A DB failure causes the record to be lost, but the cache still returns "already processed." The retry that should succeed is silently dropped, and the user never gets charged — invisible revenue loss.

**How to think through this:**
1. For each cached piece of data, ask: who can change it, on what write paths, and does every write path invalidate the cache?
2. Consider time-to-live vs event-based invalidation — TTL is simple but imprecise; event-based is precise but adds coupling.
3. Security-sensitive data (permissions, tokens) should have very short TTLs or no caching at all.

**Key takeaway:** Cache invalidation is hard because correctness requires knowing every copy of stale data at the moment a write occurs — in distributed systems, that knowledge is never complete.

</details>

> 📖 **Theory:** [Cache Invalidation](./09_api_performance_scaling/performance_guide.md)

---

### Q54 · [Thinking] · `rate-limiting-algorithms`

> **Compare the token bucket and sliding window log rate-limiting algorithms. What are the tradeoffs in accuracy vs memory usage? Which do most production rate limiters use?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**Token bucket:** A bucket holds up to N tokens. Tokens refill at a fixed rate (e.g. 10/second). Each request consumes one token. If the bucket is empty, the request is rejected. This naturally allows **bursting** — if a client was quiet for 5 seconds, they can burst 50 requests immediately.

- Memory: O(1) per client — just store the token count and last refill timestamp
- Accuracy: approximate — burst window is fuzzy
- Burst-friendly: yes

**Sliding window log:** Record the exact timestamp of every request in a sorted log. On each new request, discard entries older than the window (e.g. last 60 seconds), then count remaining entries. If count >= limit, reject.

- Memory: O(requests per window per client) — stores every timestamp; expensive at high traffic
- Accuracy: exact — no boundary aliasing
- Burst-friendly: no, it precisely enforces the limit within any 60-second window

**Fixed window counter** (common simpler variant): increment a counter per time bucket (e.g. per minute). Fast, O(1) memory, but has the **boundary problem** — a client can send 100 requests at 11:59 and 100 at 12:00, getting 200 requests in a 2-second span while technically not violating the per-minute limit.

**Sliding window counter** (hybrid): combines fixed window counters with a weighted interpolation to approximate the sliding window. Solves the boundary problem with O(1) memory per client at the cost of slight approximation (~0.003% error in practice).

**Production choice:** Most production rate limiters (Redis-based, Nginx, API gateways like Kong) use the **token bucket** or **sliding window counter** hybrid. Stripe uses a token bucket. Redis's own rate limiting documentation uses sliding window counter. The sliding window log is rarely used at scale due to memory cost.

**How to think through this:**
1. Accuracy vs memory is the core tradeoff: log = exact but costly, bucket = approximate but cheap.
2. Ask whether bursting is desirable for your use case — APIs serving humans often want burst allowance; security rate limits should not.
3. In distributed systems, the algorithm must be implementable with atomic Redis operations to avoid race conditions.

**Key takeaway:** Token bucket is the practical production default — it allows natural bursting, is O(1) per client, and maps cleanly to atomic Redis operations.

</details>

> 📖 **Theory:** [Rate Limiting](./09_api_performance_scaling/performance_guide.md)

---

### Q55 · [Normal] · `circuit-breaker-pattern`

> **What is the circuit breaker pattern in microservices? What are its three states (closed, open, half-open)? When would you add one to an API client?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

The **circuit breaker pattern** wraps calls to an external service and stops making those calls when the service is failing, giving it time to recover. Named after the electrical circuit breaker: it trips when it detects overload, breaking the circuit before damage spreads.

**Three states:**

**Closed (normal operation):** All requests pass through. The breaker monitors for failures. If failures exceed a threshold (e.g. 5 failures in 10 seconds), the breaker trips to Open.

**Open (failing fast):** All requests are immediately rejected without attempting the call. The caller gets an instant error instead of waiting for a timeout. After a cooldown period (e.g. 30 seconds), the breaker transitions to Half-Open.

**Half-Open (probing recovery):** A limited number of test requests are allowed through. If they succeed, the breaker closes (service has recovered). If they fail, the breaker returns to Open.

**When to add a circuit breaker:**
- Any synchronous call to an external service or third-party API
- Any call where a slow or failing dependency would block your threads and cascade failures to your callers
- Payment processors, notification services, ML model endpoints — anything you don't control
- Internal microservice calls in a service mesh where one slow service can cause upstream timeouts

You would NOT add one to calls that are already async/fire-and-forget, or where failure is the expected path.

**How to think through this:**
1. Without a circuit breaker, one slow service drains your thread pool → your service slows → your callers slow → cascade failure.
2. A circuit breaker breaks the chain by failing fast the moment a dependency is known to be down.
3. The half-open state is what makes it self-healing, not just a kill switch.

**Key takeaway:** The circuit breaker converts slow cascading failures into fast local failures, protecting the rest of your system while giving the downstream service time to recover.

</details>

> 📖 **Theory:** [Circuit Breaker](./16_api_design_patterns/design_guide.md)

---

### Q56 · [Critical] · `retry-exponential-backoff`

> **You implement a retry loop for a flaky external API call. What is wrong with a fixed 1-second retry? Explain exponential backoff with jitter and why jitter is critical.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**The problem with fixed 1-second retry:**

If the external service is overloaded and 1,000 clients all fail at the same moment, they all retry exactly 1 second later — creating a **synchronized thundering herd**. The overloaded service gets hit by 1,000 simultaneous retries, fails again, and all 1,000 clients retry 1 second later again. This perpetuates the overload and prevents recovery.

**Exponential backoff:** Wait time doubles on each retry: 1s → 2s → 4s → 8s → 16s (up to a cap). This spreads retries over time and reduces load on the struggling service. Formula: `min(cap, base * 2^attempt)`.

**Jitter:** Add randomness to the wait time. Without jitter, all 1,000 clients that failed simultaneously still retry at exactly the same exponential intervals — just 2 seconds later instead of 1. They remain synchronized. Jitter **desynchronizes** them.

Common jitter strategies:
- **Full jitter:** `random(0, min(cap, base * 2^attempt))` — fully random within the window
- **Decorrelated jitter:** `min(cap, random(base, last_sleep * 3))` — AWS recommends this; produces the best spread in practice

```python
import random
import time

def retry_with_backoff(fn, max_attempts=5, base=1, cap=60):
    for attempt in range(max_attempts):
        try:
            return fn()
        except TransientError as e:
            if attempt == max_attempts - 1:
                raise
            wait = random.uniform(0, min(cap, base * (2 ** attempt)))  # ← full jitter
            time.sleep(wait)
```

**How to think through this:**
1. Fixed retry: all clients retry in lockstep → thundering herd perpetuates the outage.
2. Exponential backoff: retry intervals grow → buys the service time to recover.
3. Without jitter, exponential backoff clients that failed at the same time still retry together — jitter is what actually breaks synchronization.

**Key takeaway:** Exponential backoff reduces total retry pressure; jitter is what prevents synchronized clients from recreating the thundering herd at each retry interval.

</details>

> 📖 **Theory:** [Retry & Backoff](./16_api_design_patterns/design_guide.md)

---

### Q57 · [Normal] · `api-gateway-pattern`

> **What does an API gateway do? List five responsibilities an API gateway can take on instead of individual services. When does an API gateway become a bottleneck?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

An **API gateway** is a single entry point that sits in front of all your backend services. Clients talk to the gateway; the gateway routes requests to the appropriate service. It is the "front door" of your microservices architecture.

**Five responsibilities an API gateway handles centrally:**

1. **Authentication and authorization** — verify JWTs, API keys, OAuth tokens before the request reaches any service; no service needs its own auth logic
2. **Rate limiting and throttling** — enforce per-client or per-endpoint request limits at the edge
3. **Request routing** — map incoming URLs to backend services; support path rewriting, service discovery, load balancing
4. **SSL/TLS termination** — handle HTTPS at the gateway so internal services communicate over plain HTTP on a private network
5. **Observability** — centralized logging, metrics collection, and distributed trace injection for every inbound request

Other common responsibilities: request/response transformation, caching, API versioning, circuit breaking, CORS handling.

**When does it become a bottleneck?**

The gateway is in the critical path of every single request. It becomes a bottleneck when:
- It is deployed as a single instance with no horizontal scaling
- It performs expensive synchronous operations (e.g. DB lookups per request for auth)
- It aggregates (fan-out) many backend calls into one response, so its latency is the sum of all of them
- The gateway config is managed centrally, creating a deployment/config change bottleneck

Mitigation: make the gateway stateless, scale it horizontally, push auth to JWT validation (no DB call), and avoid using it as a backend-for-frontend aggregation layer at very high scale.

**How to think through this:**
1. The gateway's value is centralizing cross-cutting concerns so services don't duplicate them.
2. The risk is making it a single point of failure and a serialization point for all traffic.
3. High-scale teams often run multiple gateway tiers: a public edge gateway and internal service meshes for east-west traffic.

**Key takeaway:** An API gateway eliminates cross-cutting duplication across services, but it must be treated as critical infrastructure — stateless, horizontally scaled, and not overloaded with business logic.

</details>

> 📖 **Theory:** [API Gateway](./15_api_gateway/gateway_patterns.md)

---

### Q58 · [Interview] · `webhooks-vs-polling`

> **Compare webhooks vs polling for receiving external events. What are the tradeoffs? When is polling actually better than webhooks?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**Polling:** Your service periodically calls the external API to check if anything new has happened. Simple to implement, you control the request timing, and you don't need a public endpoint.

**Webhooks:** The external service pushes an HTTP POST to your registered endpoint when an event occurs. You receive events in near-real time without making repeated requests.

**Tradeoffs:**

| Dimension | Polling | Webhooks |
|---|---|---|
| Latency | Depends on interval — up to interval seconds of delay | Near real-time — seconds after event |
| Infrastructure | No public endpoint needed | Requires a publicly reachable HTTPS endpoint |
| Load | Constant load on external API even when nothing changes | Load proportional to actual events |
| Reliability | You control retries; if your service is down, you catch up on next poll | If your endpoint is down, you miss events unless the sender retries with backoff |
| Complexity | Simple GET loop | Must handle: signature verification, idempotency, failures, delivery order |
| Firewall friendly | Yes — outbound only | No — requires inbound from the internet |

**When polling is actually better:**

1. **Your service is behind a firewall or NAT** — no way to expose a public endpoint (internal enterprise tools, local development)
2. **Low event volume + low latency tolerance** — polling every 5 minutes for an end-of-day report is simpler and cheaper than setting up webhook infrastructure
3. **The external service does not support webhooks** — legacy APIs, some internal services
4. **You need guaranteed at-least-once processing** — polling gives you natural catch-up on restart; webhooks require the sender to implement reliable delivery, and many do not
5. **Debugging** — polling is trivial to test locally; webhooks require ngrok or equivalent tunneling

**How to think through this:**
1. Webhooks are push, polling is pull — the key question is who controls the schedule.
2. Webhooks are better at scale and for real-time needs; polling is better for simplicity, catch-up, and restricted network environments.
3. Many production systems use both: webhooks for fast-path delivery, polling as a reconciliation sweep to catch missed events.

**Key takeaway:** Webhooks win on efficiency and latency at scale, but polling is underrated for reliability, simplicity, and environments where you cannot accept inbound connections — many teams run both for resilience.

</details>

> 📖 **Theory:** [Webhooks vs Polling](./16_api_design_patterns/design_guide.md)

---

### Q59 · [Thinking] · `webhook-security-hmac`

> **How does HMAC signature verification secure a webhook endpoint? Walk through: how the sender signs the payload, how the receiver verifies it, and what attack it prevents.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**The problem:** Your webhook endpoint is a public URL. Anyone on the internet can POST to it with a fake payload. How do you know a request actually came from GitHub (or Stripe, etc.) and not an attacker?

**HMAC (Hash-based Message Authentication Code)** solves this using a **shared secret** that only you and the sender know.

**How the sender signs:**
1. You register your webhook and receive (or provide) a secret key — e.g. `secret = "whsec_abc123"`
2. When an event fires, the sender computes: `signature = HMAC-SHA256(secret, request_body_bytes)`
3. The signature is sent in a request header, e.g. `X-Hub-Signature-256: sha256=a1b2c3...`

**How the receiver verifies:**
1. Extract the raw request body bytes (before any JSON parsing — the body must be byte-for-byte identical)
2. Recompute the HMAC using the same secret: `expected = HMAC-SHA256(secret, body)`
3. Compare `expected` to the value in the header using a **timing-safe comparison** (not `==`)
4. If they match, the payload is authentic. If not, reject with 401.

**What attack it prevents:**

**Payload forgery:** An attacker can POST any JSON to your endpoint, but without the secret they cannot produce a valid signature. The HMAC proves the payload was created by someone who holds the secret.

**Why timing-safe comparison matters:** A naive string comparison (`==`) short-circuits on the first mismatched character — an attacker can measure response times to guess the signature one byte at a time (timing attack). `hmac.compare_digest()` in Python always runs in constant time regardless of where the mismatch is.

**What it does NOT prevent:** Replay attacks — an attacker who captures a legitimate webhook can re-send it. Mitigation: include a timestamp in the signed payload and reject requests older than 5 minutes.

**How to think through this:**
1. The HMAC is essentially a "fingerprint of the body, stamped with our shared secret."
2. If the body changes even one byte, the HMAC changes — so the signature also validates payload integrity.
3. The receiver must use the raw body bytes — if you parse JSON first and re-serialize, byte order may change and the HMAC will not match.

**Key takeaway:** HMAC webhook verification proves both the sender's identity and payload integrity — but you must use raw body bytes, constant-time comparison, and add timestamp validation to prevent replays.

</details>

> 📖 **Theory:** [Webhook Security](./11_api_security_production/security_hardening.md)

---

### Q60 · [Normal] · `event-driven-api`

> **What is an event-driven API pattern? Give a concrete example of converting a synchronous REST call to an async event-driven pattern. What problem does it solve?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

An **event-driven API pattern** decouples request handling from processing by having the API publish an event to a message broker (Kafka, RabbitMQ, SQS) rather than processing synchronously. The API returns immediately; consumers process the event asynchronously.

**Synchronous (before):**

```
POST /orders
→ validate order
→ charge payment (500ms)
→ update inventory (200ms)
→ send email (300ms)
→ return 201 Created   (1 second total, failure in any step fails the whole request)
```

**Event-driven (after):**

```
POST /orders
→ validate order
→ publish OrderCreated event to message broker
→ return 202 Accepted immediately (< 50ms)

// Independently:
PaymentService consumes OrderCreated → charges card → publishes PaymentCompleted
InventoryService consumes OrderCreated → reserves stock
EmailService consumes PaymentCompleted → sends confirmation
```

**Problems it solves:**

1. **Latency:** The client doesn't wait for downstream processing — the API responds in milliseconds not seconds.
2. **Resilience:** If the email service is down, it doesn't fail the order. Events queue up and are processed when the service recovers.
3. **Decoupling:** The order service doesn't know or care which services consume its events — you can add a new consumer (analytics, fraud detection) without changing the order service.
4. **Backpressure:** The broker absorbs traffic spikes; consumers process at their own rate.

**The tradeoff:** You lose immediate consistency — the client gets 202 Accepted but cannot know if payment succeeded until they poll or receive a webhook. This requires designing for **eventual consistency**.

**How to think through this:**
1. Identify which downstream operations are not needed for the immediate response to the client.
2. Those operations become event consumers — they are fire-and-forget from the API's perspective.
3. Design a status endpoint or webhook so the client can learn the final outcome.

**Key takeaway:** Event-driven APIs trade immediate consistency for dramatically lower latency and higher resilience — the API becomes a publisher, not an orchestrator.

</details>

> 📖 **Theory:** [Event-Driven APIs](./16_api_design_patterns/design_guide.md)

---

### Q61 · [Interview] · `graphql-vs-rest`

> **Compare GraphQL and REST. What are the core differences in: data fetching, versioning, type safety, and client control? When would you choose GraphQL over REST?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**Data fetching:**

REST uses fixed endpoints that return fixed shapes: `GET /users/1` always returns the full user object. The server decides what data is returned. This causes **over-fetching** (getting fields you don't need) and **under-fetching** (needing to call multiple endpoints to assemble a view).

GraphQL uses a single endpoint (`POST /graphql`) where the client sends a query specifying exactly which fields it needs. One request can traverse relationships and fetch nested data that would require multiple REST calls.

**Versioning:**

REST typically versions by URL (`/v1/`, `/v2/`) or headers. When a field is removed, you need a new version. GraphQL handles evolution by marking fields as `@deprecated` and adding new fields — clients that don't request old fields are unaffected. In practice, GraphQL schemas are often never versioned.

**Type safety:**

REST has no enforced schema by default (OpenAPI is opt-in and not enforced at runtime). GraphQL has a **strongly typed schema** that is the contract between client and server. Every query is validated against the schema before execution. This enables tooling: autocomplete in IDEs, automatic TypeScript type generation, query validation at build time.

**Client control:**

REST: server controls the response shape. GraphQL: the client controls exactly what data it receives. This is the defining philosophical difference.

**When to choose GraphQL over REST:**

- **Multiple client types with different data needs** (mobile app needs less data than web; dashboard needs aggregated data) — each client queries exactly what it needs
- **Rapid frontend iteration** where the API shape changes frequently — new fields don't break existing clients
- **Complex, interconnected data models** where REST would require many round trips to assemble a view
- **Strong type safety and tooling** requirements — generated types, query validation

**When to stay with REST:**

- Simple CRUD APIs with well-defined resources
- Public APIs where simplicity of consumption matters — REST is universally understood
- File uploads, streaming, simple webhook integrations
- Teams without GraphQL expertise — the N+1 problem, caching complexity, and schema design have real learning curves

**How to think through this:**
1. The core tradeoff is flexibility vs simplicity. REST is predictable and cacheable; GraphQL is flexible but requires more infrastructure.
2. GraphQL shifts complexity from the server to the client — clients can do powerful things, but the server must handle arbitrary query shapes securely and efficiently.
3. Many large systems use both: GraphQL for the client-facing API, REST for internal service communication.

**Key takeaway:** Choose GraphQL when you have diverse clients with different data needs and want the schema to be the contract; choose REST when simplicity, cacheability, and universal tooling matter more than query flexibility.

</details>

> 📖 **Theory:** [GraphQL vs REST](./13_graphql/graphql_story.md)

---

### Q62 · [Thinking] · `graphql-n-plus-one`

> **What is the N+1 problem in GraphQL (different from REST N+1)? How does DataLoader solve it? Explain the batching mechanism.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**The GraphQL N+1 problem:**

Consider this query:

```graphql
query {
  posts {          # fetches 10 posts → 1 query
    title
    author {       # for each post, fetches the author → 10 queries
      name
    }
  }
}
```

GraphQL resolvers are called independently for each field. The `author` resolver fires once per post — if there are 10 posts, it fires 10 times, each making a separate `SELECT * FROM users WHERE id = ?`. That's 1 + 10 = 11 queries. With 100 posts, it's 101. This is the **N+1 problem**.

The cause is that GraphQL's resolver model is inherently per-object — each resolver doesn't know what its siblings will need.

**DataLoader: the batching solution**

**DataLoader** is a utility (created by Facebook, now language-agnostic) that batches and caches individual load calls within a single request tick.

**Mechanism:**

1. Instead of directly querying the DB, each `author` resolver calls `userLoader.load(post.authorId)` — this is a deferred load, not an immediate query.
2. DataLoader collects all `.load()` calls that happen within the current event loop tick (the "batch window").
3. After the tick, DataLoader calls your batch function once with all collected IDs: `batchLoadUsers([1, 2, 3, 4, 5])`.
4. Your batch function executes `SELECT * FROM users WHERE id IN (1,2,3,4,5)` — a single query.
5. DataLoader distributes results back to each resolver that called `.load()`.

Result: 10 individual resolver calls → 1 batched DB query.

**Caching:** DataLoader also caches within the request — if two posts have the same author, the second `.load(authorId)` returns the cached result without re-fetching.

**How to think through this:**
1. The problem is that resolvers are isolated — each one doesn't know about its siblings' needs.
2. DataLoader acts as a "collect now, execute later" buffer that aggregates requests before they hit the DB.
3. The batch window is the current event loop tick — this works naturally in Node.js; other languages need explicit async coordination.

**Key takeaway:** DataLoader solves GraphQL's N+1 by deferring individual loads into a single-tick batch window, collapsing N separate queries into one `WHERE id IN (...)` query.

</details>

> 📖 **Theory:** [GraphQL N+1](./13_graphql/graphql_story.md)

---

### Q63 · [Interview] · `grpc-vs-rest`

> **Compare gRPC and REST. What are the advantages of gRPC for internal service communication? What are its disadvantages for public APIs?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**gRPC** (Google Remote Procedure Call) is a high-performance RPC framework that uses **Protocol Buffers** for serialization and **HTTP/2** as its transport. You define a service contract in a `.proto` file; code is generated for both client and server in any supported language.

**Advantages of gRPC for internal service communication:**

1. **Performance:** Protocol Buffers serialize to binary — typically 3-10x smaller than JSON and significantly faster to serialize/deserialize. HTTP/2 multiplexes multiple requests over a single connection, eliminating head-of-line blocking.

2. **Strongly typed contracts:** The `.proto` file is the contract. Code generation produces typed client stubs in any language. If the server changes the interface incompatibly, the build fails — no runtime surprises.

3. **Bi-directional streaming:** HTTP/2 supports server streaming, client streaming, and bi-directional streaming natively. REST over HTTP/1.1 requires workarounds (SSE, WebSockets) for streaming.

4. **Code generation:** Client libraries are generated automatically. No hand-writing HTTP clients, parsing responses, or managing serialization — the generated stub looks like a local function call.

5. **Native multi-language support:** One `.proto` definition generates clients in Go, Python, Java, etc. — critical for polyglot microservices.

**Disadvantages for public APIs:**

1. **Browser incompatibility:** Browsers cannot make raw HTTP/2 gRPC calls. gRPC-Web exists but requires a proxy layer (Envoy). REST + JSON works natively in any browser with `fetch`.

2. **Not human-readable:** Binary Protocol Buffers cannot be inspected with curl, browser devtools, or Postman without special plugins. Debugging is harder.

3. **Tooling ecosystem:** REST has a massive ecosystem (OpenAPI, Postman, curl, Swagger UI). gRPC tooling is improving but is less mature and less universally known.

4. **Firewall and proxy issues:** Some corporate firewalls block non-standard HTTP/2 traffic. REST over HTTP/1.1 passes through virtually everything.

5. **Third-party developer experience:** External developers building against your API expect REST + JSON. gRPC requires understanding Protocol Buffers and generated stubs.

**How to think through this:**
1. gRPC is optimized for the case where you control both client and server — internal microservices.
2. REST is optimized for the case where you do not control the client — public APIs, third-party integrations, browser apps.
3. Many systems use gRPC internally and REST externally, with the API gateway translating between them (grpc-gateway pattern).

**Key takeaway:** gRPC excels at internal service communication where performance, type safety, and polyglot code generation matter; REST is superior for public APIs where human readability, universal tooling, and browser compatibility are the priority.

</details>

> 📖 **Theory:** [gRPC vs REST](./14_grpc/grpc_guide.md)

---

### Q64 · [Normal] · `protocol-buffers`

> **What are Protocol Buffers? How do they differ from JSON? What are the tradeoffs in: size, speed, human-readability, schema evolution?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**Protocol Buffers** (protobuf) is a language-neutral, binary serialization format developed by Google. You define your data structure in a `.proto` schema file; the `protoc` compiler generates serialization/deserialization code in your target language.

```proto
message User {
  int32 id = 1;
  string name = 2;
  string email = 3;
}
```

**Protobuf vs JSON tradeoffs:**

**Size:**
- Protobuf: binary encoding, no field names transmitted (replaced by field numbers), varint encoding for integers. Typically 3-10x smaller than equivalent JSON.
- JSON: text-based, field names repeated in every object, verbose number encoding.

**Speed:**
- Protobuf: fast binary parse/serialize, strongly typed, minimal allocation. Benchmarks typically show 5-10x faster serialization than JSON.
- JSON: text parsing is slower; libraries vary widely in performance.

**Human-readability:**
- Protobuf: binary — not readable with curl, cat, or browser devtools. Requires schema to decode.
- JSON: human-readable, self-describing, can be inspected with any text tool. This is JSON's biggest practical advantage for debugging and external APIs.

**Schema evolution:**
- Protobuf: designed for forward and backward compatibility. Old clients ignore unknown field numbers; new fields with new numbers don't break old parsers. Fields can be marked `optional` or `reserved`. The schema is the enforced contract — field renaming is safe (only the number matters on the wire).
- JSON: no built-in schema evolution — you rely on consumers ignoring unknown keys (not always true) and careful API versioning. Schema is optional (OpenAPI, JSON Schema) and not enforced at runtime.

**Self-describing:**
- Protobuf: not self-describing — you need the `.proto` file to interpret a binary blob.
- JSON: self-describing — any parser can read it without a schema.

**How to think through this:**
1. For internal services where you control both ends and have the schema: protobuf wins on performance and type safety.
2. For external APIs or anywhere humans will inspect the wire format: JSON wins on debuggability.
3. Schema evolution in protobuf is safe if you follow the rules: never reuse field numbers, never change field types.

**Key takeaway:** Protocol Buffers trade human-readability for significant gains in size, speed, and enforced schema contracts — the right choice for internal service communication, wrong choice for public human-readable APIs.

</details>

> 📖 **Theory:** [Protocol Buffers](./14_grpc/grpc_guide.md)

---

### Q65 · [Interview] · `api-versioning-strategies`

> **Compare three API versioning strategies: URL versioning (`/v1/`), request header versioning (`API-Version: 2`), and content negotiation (`Accept: application/vnd.api+json;version=2`). What are the tradeoffs?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**URL versioning (`/v1/users`, `/v2/users`):**

The version is part of the URL path. This is by far the most common approach in public APIs (Stripe, Twitter, Twilio all use it).

Pros:
- Immediately obvious — you can see the version in browser address bar, logs, and curl commands
- Easy to route at the load balancer or gateway level by path prefix
- Different versions can be deployed as completely separate services or codebases
- Bookmarkable and shareable — a URL is a stable identifier

Cons:
- Violates REST purity — the resource (`/users`) shouldn't change identity based on version; the URL should represent the resource, not the API contract
- URL proliferation — `/v1`, `/v2`, `/v3` all live in the system simultaneously
- Cache keys are different per version, so `/v1/users/1` and `/v2/users/1` are cached separately even if identical

**Request header versioning (`API-Version: 2`):**

The version is specified in a custom request header.

Pros:
- "Cleaner" REST semantics — the resource URL stays stable; the version is part of the request metadata
- Easy to implement in middleware — inspect the header, route accordingly

Cons:
- Not visible in the URL — developers forget to include it, curl examples are more verbose
- Not bookmarkable or cacheable by default — proxies and CDNs route on URL, not custom headers; requires `Vary: API-Version` for correct caching
- Less discoverable — new developers don't know they need the header until they read the docs

**Content negotiation (`Accept: application/vnd.myapi+json;version=2`):**

Uses the HTTP `Accept` header with a vendor media type. The server responds with `Content-Type: application/vnd.myapi+json;version=2`.

Pros:
- "Most correct" by HTTP spec — the Accept header was designed for negotiating representations of a resource
- Allows genuinely different response formats, not just versions

Cons:
- Complex to implement correctly — parsing media type parameters, responding with correct `Content-Type`, setting `Vary: Accept`
- Least familiar to most API consumers — obscure syntax increases developer friction
- Poorly supported by some HTTP clients, proxies, and caching layers
- Almost never used outside of strict REST academia or hypermedia APIs (HAL, JSON:API)

**Practical recommendation:** URL versioning for public-facing APIs — it wins on discoverability, debuggability, and routing simplicity. Header versioning is reasonable for internal APIs where you control all clients.

**How to think through this:**
1. The core tradeoff is REST purity vs developer experience. URL versioning "pollutes" the URL but makes life easier for everyone.
2. CDN and proxy friendliness strongly favor URL versioning — cache keys and routing are URL-based.
3. The version you'll actually maintain long-term matters more than the strategy — have a clear deprecation policy regardless of approach.

**Key takeaway:** URL versioning wins in practice because it is visible, debuggable, cache-friendly, and universally understood — the theoretical REST purity of header versioning is rarely worth the operational complexity.

</details>

> 📖 **Theory:** [Versioning Strategies](./08_versioning_standards/versioning_strategy.md)

---

### Q66 · [Normal] · `openapi-benefits`

> **What is an OpenAPI specification? Name five concrete benefits it provides beyond documentation. How does FastAPI auto-generate it?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**OpenAPI** (formerly Swagger) is a language-agnostic, JSON/YAML specification that formally describes a REST API: its endpoints, request parameters, request/response schemas, authentication methods, and error codes. It is the industry standard for describing HTTP APIs.

**Five concrete benefits beyond documentation:**

1. **Automatic client SDK generation:** Tools like `openapi-generator` read the spec and produce typed client libraries in Python, TypeScript, Go, Java, etc. — no hand-writing HTTP clients.

2. **Contract testing:** The spec is a machine-readable contract. Tools like Dredd or Schemathesis can automatically generate and run tests that verify your API implementation matches the spec.

3. **Mock server generation:** Tools like Prism can spin up a mock server from an OpenAPI spec before the real API exists — enabling frontend development and consumer testing in parallel with backend development.

4. **Request/response validation middleware:** Libraries like `openapi-core` (Python) or `express-openapi-validator` (Node) can automatically validate incoming requests and outgoing responses against the schema at runtime, rejecting malformed requests before they hit your business logic.

5. **API gateway and infrastructure configuration:** Many API gateways (AWS API Gateway, Kong, Apigee) can import an OpenAPI spec to auto-configure routing, validation, rate limiting, and documentation — single source of truth for API behavior.

**How FastAPI auto-generates it:**

FastAPI reads Python type hints and Pydantic models at application startup to build the OpenAPI schema automatically. When you declare:

```python
@app.post("/users", response_model=UserResponse)
def create_user(body: CreateUserRequest):
    ...
```

FastAPI introspects `CreateUserRequest` (a Pydantic model) for request schema and `UserResponse` for response schema, inspects the path and HTTP method, and registers the route in an internal OpenAPI object. Accessing `/openapi.json` returns the full spec; `/docs` renders Swagger UI; `/redoc` renders ReDoc.

**How to think through this:**
1. The spec is a machine-readable contract, not just a human-readable document.
2. Every tool that reads the spec — client generators, validators, mock servers — multiplies the value of writing it once.
3. FastAPI's design philosophy (type hints as source of truth) means the spec and the code are always in sync — no drift.

**Key takeaway:** An OpenAPI spec is an executable contract — it generates clients, enables contract testing, powers mock servers, and drives gateway configuration, all from a single definition that FastAPI produces automatically from your type annotations.

</details>

> 📖 **Theory:** [OpenAPI Spec](./10_testing_documentation/docs_that_work.md)

---

### Q67 · [Thinking] · `contract-testing`

> **What is API contract testing? How does it differ from integration testing? Why is it valuable in a microservices architecture?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**Contract testing** verifies that a consumer and a provider agree on the shape of their API interaction. It tests the contract — the agreed-upon request/response structure — rather than the full end-to-end integration.

**Consumer-driven contract testing (the Pact model):**
1. The **consumer** (e.g. frontend, downstream service) writes tests that record what requests it makes and what response shape it expects. These are serialized into a **contract file** (a pact).
2. The **provider** (the API) runs the contract against itself: replay the consumer's expected requests and verify the response matches the shape in the contract.
3. If the provider's response breaks the contract (missing field, changed type), the test fails — before deployment.

**How it differs from integration testing:**

| | Integration testing | Contract testing |
|---|---|---|
| **What it tests** | Full system behavior, business logic, data flow | Only the API shape / interface boundary |
| **Requires both services running** | Yes — real network, real DB | No — consumer uses a mock; provider replays recorded interactions |
| **Speed** | Slow — spins up infrastructure | Fast — just validates schemas |
| **Failure signal** | "Something is broken somewhere" | "Service X's response no longer matches what Service Y expects" |
| **When it runs** | Pre-deploy in staging | In CI for each service independently |

**Why it is valuable in microservices:**

In a microservices architecture, teams deploy services independently. Without contract tests:
- Team A changes the `users` response shape (renames `userId` to `id`) and deploys
- Team B's service (which reads `userId`) breaks silently — they don't find out until integration testing or production
- Finding the bug requires running both services together, which may not happen until late in the pipeline

Contract testing catches this in Team A's own CI pipeline, before they deploy, by verifying that their change would break Team B's recorded contract. No coordination meeting required — the contract is the communication.

**How to think through this:**
1. Integration tests verify behavior; contract tests verify interfaces.
2. In a monolith, a compile error catches interface mismatches instantly. Contract tests provide the equivalent for independently deployed services.
3. Consumer-driven contracts are more powerful than provider-driven ones because they represent what consumers actually use, not what providers think they provide.

**Key takeaway:** Contract testing is compile-time type safety for service boundaries — it catches breaking API changes in CI before deployment, without requiring both services to run simultaneously.

</details>

> 📖 **Theory:** [Contract Testing](./10_testing_documentation/testing_apis.md)

---

### Q68 · [Normal] · `load-testing-apis`

> **What metrics do you measure when load testing an API? What is the difference between throughput and latency under load? What tool would you use?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**Key metrics to measure during load testing:**

1. **Throughput (RPS):** Requests per second the API successfully handles. The headline capacity metric — how much load can the system sustain?

2. **Latency percentiles:** Not average latency — percentiles. `p50` (median), `p95`, `p99`, `p99.9`. The p99 and p99.9 reveal the "long tail" — the worst experiences real users have. Averages hide outliers.

3. **Error rate:** Percentage of requests returning 4xx/5xx. At what load does the error rate start climbing? This is the breaking point.

4. **Latency under load:** How does p99 latency change as RPS increases? A healthy system maintains latency until near saturation, then latency spikes sharply (the "knee of the curve").

5. **Time to first byte (TTFB):** For streaming or large responses.

6. **Resource utilization:** CPU, memory, DB connection pool exhaustion, thread pool saturation on the server side. Correlate with the external metrics to find the bottleneck.

**Throughput vs latency under load:**

These are related but distinct. **Throughput** is how many requests per second the system handles. **Latency** is how long each request takes.

At low load, both are good. As you approach capacity, a critical relationship emerges: **latency rises before throughput drops**. This is Little's Law: `L = λW` (queue depth = arrival rate × wait time). As the system gets busy, requests queue up — latency climbs first, then requests start timing out and error rate rises, then throughput drops as the system spends resources on retries and error handling.

This means: **watch latency percentiles to find the safe operating point** — don't run at the RPS where throughput is maximized, because p99 latency is already terrible there.

**Tools:**

- **k6** — modern, scripted in JavaScript, excellent for CI integration and complex scenarios
- **Locust** — Python-based, good for complex user behavior simulation
- **Apache JMeter** — mature, GUI-driven, widely used in enterprise
- **wrk / wrk2** — low-level, minimal, best for raw HTTP benchmarking
- **Artillery** — YAML-based scenarios, good for teams that want declarative config

**How to think through this:**
1. Always look at percentiles, not averages — your slowest 1% of users represents real users with bad experiences.
2. Ramp load gradually and watch the latency curve — the point where p99 starts climbing is your sustainable capacity limit.
3. Correlate application metrics with infrastructure metrics to find whether the bottleneck is CPU, DB, network, or connection pool.

**Key takeaway:** Load testing reveals the latency-throughput tradeoff — monitor p95/p99 latency as you increase load, and define your capacity limit as the RPS where latency SLOs are still met, not the maximum possible RPS.

</details>

> 📖 **Theory:** [Load Testing](./09_api_performance_scaling/performance_guide.md)

---

### Q69 · [Normal] · `api-observability`

> **What are the three pillars of API observability? Give one specific example of what you'd measure/collect for each pillar in a production API.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

The **three pillars of observability** are metrics, logs, and traces. Together they answer the three core questions: "what is wrong?" (metrics), "what happened?" (logs), and "where is the bottleneck?" (traces).

**1. Metrics**

Numerical measurements aggregated over time. They are cheap to store and queryable as time series.

Example for a production API: `http_request_duration_seconds` histogram, labeled by `endpoint`, `method`, and `status_code`. This lets you query p95 latency per endpoint, error rate per endpoint, and RPS over time. Alert when `p99 latency > 2s` or `error_rate > 1%` for any endpoint. Tooling: Prometheus + Grafana.

**2. Logs**

Structured event records — one log line per request (or per significant event). Rich in detail but expensive to query at scale.

Example: a structured JSON log line per request containing `request_id`, `user_id`, `endpoint`, `status_code`, `duration_ms`, `db_query_count`, and any error details. When a metric alert fires, you use the logs to investigate the specific failing requests. Tooling: structured logging to stdout, collected by Fluentd or Datadog, queried in Splunk or CloudWatch Logs Insights.

**3. Traces**

Distributed traces follow a single request across multiple services, recording each operation as a **span** with start time, duration, and metadata.

Example: a trace for `POST /checkout` that shows the full call tree: API gateway (12ms) → order-service (45ms) → payment-service (320ms) → database query (280ms inside payment-service). The trace immediately shows that the DB query inside the payment service is consuming 87% of the total latency. Tooling: OpenTelemetry SDK for instrumentation, Jaeger or AWS X-Ray for storage and visualization.

**How to think through this:**
1. Metrics tell you something is wrong; logs tell you the details of what happened; traces tell you where in the distributed system the time was spent.
2. They work together: alert on metrics → investigate with logs → root cause with traces.
3. OpenTelemetry is the modern standard for instrumenting all three pillars with a single SDK.

**Key takeaway:** The three pillars work as a debugging funnel — metrics surface the problem, logs give the narrative, and traces pinpoint the exact service and line of code responsible.

</details>

> 📖 **Theory:** [API Observability](./19_opentelemetry/opentelemetry_guide.md)

---

### Q70 · [Thinking] · `distributed-tracing`

> **How does distributed tracing work across multiple services? What is a trace ID, span, and parent span? What does it help you find that logs alone cannot?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**The problem distributed tracing solves:**

In a microservices system, a single user request triggers calls across 5-10 services. Each service writes its own logs, but those logs are isolated — you cannot reconstruct the journey of a single request across services from logs alone without already knowing what to look for.

**Core concepts:**

A **trace** represents the complete journey of a single request from entry to completion across all services. It is identified by a **trace ID** — a globally unique identifier (e.g. a 128-bit UUID) generated at the entry point and propagated through every downstream call via HTTP headers (e.g. `traceparent` in the W3C Trace Context standard, or `X-B3-TraceId` in the older B3 format).

A **span** represents a single unit of work within a trace — one service handling a request, one DB query, one outbound HTTP call. A span records: operation name, start timestamp, end timestamp (duration), service name, status, and arbitrary key-value attributes.

A **parent span** is the span that caused the current span. When Service A calls Service B, Service A's span is the parent of Service B's span. The hierarchy of spans — parent → child → grandchild — forms a **call tree** that shows exactly which service called what and how long each step took.

**What distributed tracing finds that logs cannot:**

1. **Where time was spent across services:** Logs tell you what happened inside one service. A trace tells you that the 800ms total latency was: API gateway (10ms) + auth service (30ms) + product service (20ms) + recommendation service (740ms). Immediately obvious which service is the bottleneck.

2. **Cascade failures:** A trace shows that Service C failed because Service D timed out, because Service E's DB connection pool was exhausted. Logs from Service C just say "request failed" — the root cause is invisible.

3. **Parallel vs serial call patterns:** A trace visualizes whether Service A calls B and C in parallel or serial — a critical performance insight that is impossible to reconstruct from logs.

4. **Silent failures:** A child span may fail silently (caught exception, empty fallback result) without logging an error at the parent level. The trace shows the failed span even when no error log was written.

**How to think through this:**
1. Think of the trace ID as a thread that stitches together log lines across every service that touched the request.
2. Without the trace ID, finding all log lines related to one request requires knowing the user ID, request timestamp, and every service name — then manually joining logs.
3. Traces add a time dimension that logs lack — you see not just what happened but when and for how long in relation to other operations.

**Key takeaway:** Distributed tracing provides the call graph for a single request across all services — it turns "something is slow somewhere" into "this specific DB query in this specific service at this specific span is the bottleneck."

</details>

> 📖 **Theory:** [Distributed Tracing](./19_opentelemetry/opentelemetry_guide.md)

---

### Q71 · [Design] · `idempotency-implementation`

> **Show how to implement idempotency for a payment POST endpoint using an idempotency key. Cover: client sends key, server checks storage, stores result, returns cached on duplicate.**

```python
import hashlib
import json
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
import redis

app = FastAPI()
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

IDEMPOTENCY_TTL = 86400  # ← 24 hours: key valid for one day

@app.post("/payments")
async def create_payment(
    request: Request,
    idempotency_key: str = Header(..., alias="Idempotency-Key")  # ← required header
):
    # Step 1: Validate key format
    if len(idempotency_key) > 255:
        raise HTTPException(status_code=400, detail="Idempotency-Key too long")

    # Step 2: Check if we've seen this key before
    cache_key = f"idempotency:{idempotency_key}"
    cached_result = r.get(cache_key)

    if cached_result:
        stored = json.loads(cached_result)
        return JSONResponse(                             # ← return exact same response
            content=stored["body"],
            status_code=stored["status_code"],
            headers={"Idempotency-Replayed": "true"}    # ← signal to client it's a replay
        )

    # Step 3: Mark key as "in-flight" to handle concurrent duplicates
    lock_key = f"idempotency:lock:{idempotency_key}"
    acquired = r.set(lock_key, "1", nx=True, ex=30)     # ← nx=True: only set if not exists
    if not acquired:
        raise HTTPException(status_code=409, detail="Request in progress")

    try:
        body = await request.json()
        # Step 4: Execute the actual payment (your business logic)
        payment_result = process_payment(body)
        response_body = {"payment_id": payment_result.id, "status": "success"}
        status_code = 201

    except PaymentDeclinedError:
        response_body = {"error": "payment_declined"}
        status_code = 402                               # ← also cache failures: prevents retry storms
    finally:
        r.delete(lock_key)                              # ← always release the lock

    # Step 5: Store the result with TTL
    r.setex(
        cache_key,
        IDEMPOTENCY_TTL,
        json.dumps({"body": response_body, "status_code": status_code})
    )

    return JSONResponse(content=response_body, status_code=status_code)
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**Idempotency** means that making the same request multiple times produces the same result as making it once. For payment APIs, this is critical: a network timeout on the client side should not result in double-charging the user.

**Key design decisions in the implementation above:**

1. **Client-generated key:** The client creates a unique `Idempotency-Key` (UUID) before sending the request. If the request fails (network error, timeout), the client retries with the exact same key. Stripe uses this pattern.

2. **Cache the full response, not just "it happened":** Store both the response body and status code. Return the identical response on duplicate — the client should not be able to distinguish a fresh response from a replayed one (except via the `Idempotency-Replayed` header).

3. **Cache failures too:** If a payment is declined (402), cache that result. Otherwise, a client could retry a declined payment and get a different outcome — violating idempotency.

4. **Distributed lock for concurrent duplicates:** Without the lock, two simultaneous requests with the same key both miss the cache check and both execute the payment. The `SET NX` lock ensures only one proceeds; the other gets a 409.

5. **TTL:** Keys expire after 24 hours. After that, a new payment with the same key would be treated as a new request. Document this TTL in your API.

**What idempotency does NOT protect against:** If the payment succeeds but the response is lost before the client receives it, the client retries, the key is found in cache, and the cached success is returned — correct. But if your server crashes after processing but before writing to Redis, the key is never stored, and a retry will process again. This "exactly-once" guarantee requires two-phase commit or transactional outbox patterns.

**How to think through this:**
1. The idempotency key is the client's way of saying "this is the same logical operation, not a new one."
2. The server's job is to record the result of the first execution and replay it for duplicates.
3. The race condition between two concurrent identical requests requires a lock — the cache check alone is not atomic.

**Key takeaway:** Idempotency keys let clients safely retry on network failures without risk of duplicate operations — store the full response keyed by the client's UUID, cache failures as well as successes, and use a distributed lock to handle concurrent duplicates.

</details>

> 📖 **Theory:** [Idempotency Implementation](./16_api_design_patterns/design_guide.md)

---

### Q72 · [Design] · `async-job-api`

> **Design an API for a long-running operation (video encoding). Show: the initial POST endpoint, the job status polling endpoint, and the webhook callback approach. What are the tradeoffs?**

```python
import uuid
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from enum import Enum

app = FastAPI()

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class EncodeRequest(BaseModel):
    video_url: str
    output_format: str
    webhook_url: str | None = None  # ← optional: client registers for push notification

# --- Approach 1: Initial POST → 202 Accepted ---

@app.post("/videos/encode", status_code=202)
async def start_encoding(body: EncodeRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    
    # Store initial job record
    db.create_job(job_id, status=JobStatus.PENDING, webhook_url=body.webhook_url)
    
    # Queue the actual work — do NOT block the request
    background_tasks.add_task(encode_video_task, job_id, body.video_url, body.output_format)
    
    return {
        "job_id": job_id,
        "status": JobStatus.PENDING,
        "status_url": f"/videos/jobs/{job_id}",  # ← tell client where to poll
    }

# --- Approach 2: Polling endpoint ---

@app.get("/videos/jobs/{job_id}")
async def get_job_status(job_id: str):
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404)
    
    response = {"job_id": job_id, "status": job.status}
    
    if job.status == JobStatus.COMPLETED:
        response["output_url"] = job.output_url          # ← result only on completion
        response["Retry-After"] = None
    elif job.status in (JobStatus.PENDING, JobStatus.PROCESSING):
        response["Retry-After"] = 30                     # ← hint to client: poll in 30s
    
    return response

# --- Approach 3: Webhook callback (called internally when job finishes) ---

async def notify_webhook(job_id: str, webhook_url: str, result: dict):
    payload = {"job_id": job_id, "status": "completed", **result}
    signature = compute_hmac(payload)                    # ← always sign webhook payloads
    
    async with httpx.AsyncClient() as client:
        await client.post(
            webhook_url,
            json=payload,
            headers={"X-Signature": signature},
            timeout=10.0
        )
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**The core pattern: 202 Accepted**

A long-running operation (video encoding, PDF generation, ML inference) should never block the HTTP response. Return **202 Accepted** immediately with a `job_id` and a `status_url`. The HTTP 202 status explicitly means "the request has been accepted for processing, but processing has not been completed."

**Polling approach tradeoffs:**

Pros: Simple to implement and consume. The client controls the retry schedule. Works through firewalls. Easy to implement catch-up after client downtime (just poll again).

Cons: Wasted requests when nothing has changed (polling too frequently). Latency between completion and client awareness (polling too infrequently). At scale, many clients polling frequently creates load on your status endpoint. Mitigate with `Retry-After` header hints and exponential backoff.

**Webhook approach tradeoffs:**

Pros: Client gets notified immediately on completion — minimal latency. No wasted requests. Server controls the push timing.

Cons: Client needs a publicly reachable HTTPS endpoint. If the client is down when the webhook fires, the notification is lost — requires retry logic with backoff on the sender side. Requires webhook security (HMAC signing). Harder to test locally.

**Combining both (recommended):**

Accept an optional `webhook_url` in the POST body. If provided, fire the webhook on completion AND support polling as a fallback. Clients that can receive webhooks get fast notification; clients behind firewalls or doing batch reconciliation can always poll. This is how Stripe, Twilio, and most production systems work.

**Additional design considerations:**

- Job results should be retrievable for a reasonable TTL (e.g. 24-48 hours) after completion, not deleted immediately.
- The status endpoint should be idempotent and cheap — avoid expensive DB queries on every poll.
- Use a proper job queue (Celery, RQ, SQS + workers) rather than `BackgroundTasks` for production — `BackgroundTasks` does not survive server restarts.

**How to think through this:**
1. The client's contract is: POST gets you a job_id, the job_id is your receipt, use it to track progress.
2. Polling is the safe fallback; webhooks are the fast path.
3. The status endpoint must be lightweight — it will be called far more often than the initial POST.

**Key takeaway:** Long-running API operations should return 202 Accepted with a job ID immediately, then support both polling (for resilience and simplicity) and webhooks (for low latency) — use both together for production-grade async job APIs.

</details>

> 📖 **Theory:** [Async Job API](./16_api_design_patterns/design_guide.md)

---

### Q73 · [Normal] · `file-upload-api`

> **What are three ways to handle file uploads in a REST API? Compare: multipart form data, pre-signed S3 URLs, and base64 encoding. When would you use each?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**1. Multipart form data (`Content-Type: multipart/form-data`)**

The file is included in the request body alongside form fields. The browser's native `<input type="file">` uses this format. Your API server receives the bytes directly and is responsible for storing them (local disk, then S3).

Use when:
- Files are small (< 10MB) and you need the API to process/validate the file immediately (virus scan, image resize, parse CSV)
- You need transactional consistency — the file upload and metadata creation succeed or fail together
- Simple implementations where you control the full stack

Cons: your API server must handle all upload bandwidth and storage; large files tie up server memory; hard to scale without streaming.

**2. Pre-signed S3 URLs (direct-to-storage upload)**

Your API generates a **pre-signed URL** — a temporary, signed URL that grants the client permission to PUT a file directly to S3, without the request going through your server. The client uploads directly to S3; your server receives a callback (S3 event → Lambda/webhook) when the upload completes.

Use when:
- Files are large (video, images, archives) — keeps large uploads off your API servers entirely
- You want S3's reliability and bandwidth; your server only handles metadata
- Mobile or browser clients — S3 handles multipart upload resumption natively

Cons: more complex flow (two-step: get URL, then upload); client must support PUT with the pre-signed URL; you lose synchronous file access for immediate processing.

**3. Base64 encoding (inline in JSON body)**

The file bytes are base64-encoded and included as a JSON string field. `POST /images` with `{"filename": "photo.jpg", "data": "iVBORw0KGgo..."}`.

Use when:
- Files are very small (< 1MB) — icons, thumbnails, short audio clips
- The API is consumed by clients that cannot do multipart (some mobile SDKs, IoT devices)
- Simplicity is paramount — one JSON request, no multipart boundary parsing

Cons: base64 inflates file size by ~33%; the JSON parser must hold the entire encoded file in memory; poor performance at scale; not suitable for anything over a few hundred KB.

**Summary:**

| Method | Max practical size | Who handles bandwidth | Complexity |
|---|---|---|---|
| Multipart | < 10MB | Your API server | Low |
| Pre-signed S3 | Unlimited (5TB S3 limit) | S3 directly | Medium |
| Base64 JSON | < 1MB | Your API server | Lowest |

**How to think through this:**
1. Ask: who should receive the bytes? For anything large, your API server should never see the bytes — route direct to storage.
2. Ask: do you need the file immediately? Multipart gives you the bytes synchronously; pre-signed URL requires an async callback.
3. Base64 is a pragmatic hack for tiny files where you want to avoid multipart — know its 33% overhead and memory cost.

**Key takeaway:** Use multipart for small files needing immediate processing, pre-signed S3 URLs for large files to bypass your servers entirely, and base64 only for very small files in JSON-only clients — the choice is determined by file size and who should handle the upload bandwidth.

</details>

> 📖 **Theory:** [File Upload](./16_api_design_patterns/design_guide.md)

---

### Q74 · [Interview] · `api-security-owasp`

> **Name five OWASP API Security Top 10 risks. For each, give one concrete example of the vulnerability and one mitigation.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

The **OWASP API Security Top 10** (2023 edition) identifies the most critical API security risks.

**1. Broken Object Level Authorization (BOLA / IDOR)**

Example: `GET /invoices/1042` returns the invoice. An authenticated user changes the ID to `GET /invoices/1043` and receives another customer's invoice. The API checks authentication but not whether the authenticated user owns invoice 1043.

Mitigation: For every object access, check that the requesting user has permission to access that specific object, not just that they are authenticated. `if invoice.owner_id != current_user.id: raise 403`.

**2. Broken Authentication**

Example: A password reset endpoint accepts a `user_id` parameter directly — `POST /reset-password {"user_id": 99, "new_password": "..."}` — with no verification that the requester owns that account. Or: JWT tokens signed with `alg: none` (algorithm bypass) are accepted.

Mitigation: Use battle-tested authentication libraries. Never trust client-supplied identity in sensitive endpoints. Enforce algorithm validation in JWT verification (`algorithms=["RS256"]`, never accept `none`). Rate-limit authentication endpoints.

**3. Broken Object Property Level Authorization (Mass Assignment)**

Example: `PUT /users/me` accepts a JSON body and maps it directly to the user model. A client sends `{"role": "admin", "name": "Alice"}` and the API sets `user.role = "admin"` because it blindly applies all provided fields.

Mitigation: Use explicit allowlists of updatable fields. Never bind request bodies directly to your ORM model without filtering. Pydantic models with explicit fields (not `extra="allow"`) enforce this.

**4. Unrestricted Resource Consumption**

Example: An API endpoint with no rate limiting accepts `POST /reports/generate` — an attacker sends 10,000 concurrent requests, each triggering an expensive DB query, exhausting database connections and bringing the service down.

Mitigation: Rate limiting per client (token bucket or sliding window). Pagination with maximum page size limits. Request body size limits. Timeout for expensive operations. Quotas on compute-intensive endpoints.

**5. Security Misconfiguration**

Example: A staging API has verbose error responses enabled: a 500 error returns the full Python stack trace including database connection strings and internal file paths. Or: `Access-Control-Allow-Origin: *` on an endpoint that sets sensitive cookies, enabling cross-site request forgery from any domain.

Mitigation: Disable debug/verbose error responses in production (return generic error messages, log details server-side). Audit CORS policies — never use wildcard origins for credentialed endpoints. Regularly scan API endpoints for exposed internal paths, stack traces, and misconfigured headers. Use security headers (`Strict-Transport-Security`, `X-Content-Type-Options`).

**Honorable mentions from the Top 10:** Broken Function Level Authorization (users accessing admin endpoints), Server-Side Request Forgery (SSRF), Unsafe Consumption of APIs (trusting third-party API responses without validation).

**How to think through this:**
1. BOLA and Broken Authentication together account for the majority of real-world API breaches — they are the most critical to get right.
2. Authorization bugs (BOLA, mass assignment, function-level) are harder to catch with automated scanning — they require code review and explicit test cases for each endpoint.
3. Security misconfiguration is the easiest to fix: automated security header checks, error handling middleware, and environment-specific config validation catch most issues.

**Key takeaway:** The OWASP API Top 10 is dominated by authorization failures (BOLA, mass assignment) rather than encryption or injection attacks — always check not just "is the user authenticated?" but "is this specific user allowed to do this specific thing to this specific object?"

</details>

> 📖 **Theory:** [OWASP API Security](./11_api_security_production/security_hardening.md)

---

### Q75 · [Design] · `mobile-api-optimisation`

> **Design API responses optimised for mobile clients on slow networks. What techniques reduce payload size and round trips? How does sparse fieldsets (like GraphQL field selection) help?**

```python
from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI()

# --- Technique 1: Sparse fieldsets ---
@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    fields: Optional[str] = Query(None, description="Comma-separated fields: id,name,avatar_url")
):
    user = db.get_user(user_id)
    
    if fields:
        allowed = {"id", "name", "email", "avatar_url", "bio", "follower_count"}
        requested = set(fields.split(",")) & allowed     # ← intersection: only valid fields
        return {k: v for k, v in user.dict().items() if k in requested}
    
    return user                                          # ← full response for non-mobile clients

# --- Technique 2: Composite endpoint (reduces round trips) ---
@app.get("/mobile/feed")
async def get_mobile_feed(user_id: int):
    # One endpoint that returns everything the mobile home screen needs
    # Instead of: GET /user + GET /notifications + GET /posts + GET /stories
    user, notifications, posts, stories = await asyncio.gather(
        db.get_user(user_id),
        db.get_notifications(user_id, limit=5),
        db.get_feed_posts(user_id, limit=10),
        db.get_stories(user_id, limit=20),
    )
    return {                                             # ← one response, one round trip
        "user": user.dict(include={"id", "name", "avatar_url"}),
        "unread_notifications": len([n for n in notifications if not n.read]),
        "posts": [p.dict(exclude={"raw_html", "internal_tags"}) for p in posts],
        "stories": [s.dict(include={"id", "preview_url", "expires_at"}) for s in stories],
    }

# --- Technique 3: Pagination with cursor (avoids expensive OFFSET) ---
@app.get("/posts")
async def list_posts(
    cursor: Optional[str] = None,   # ← cursor encodes last seen id + timestamp
    limit: int = Query(20, le=50)   # ← cap max page size
):
    posts = db.get_posts_after_cursor(cursor, limit=limit)
    next_cursor = encode_cursor(posts[-1]) if len(posts) == limit else None
    return {"posts": posts, "next_cursor": next_cursor}
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**

Mobile clients face three constraints desktop APIs ignore: limited bandwidth (slow/metered connections), higher latency (cellular RTT is 50-200ms vs 1-5ms on LAN), and battery/CPU costs of parsing large payloads. Every optimization targets one of these.

**Techniques to reduce payload size:**

1. **Sparse fieldsets:** Return only the fields the client requests. A mobile list view needs `id`, `title`, `thumbnail_url` — not the 40-field full object. Reduces payload by 80-90% for list views. This is what GraphQL's field selection provides natively; REST achieves it with a `?fields=` query parameter (as shown above) or a separate "summary" endpoint.

2. **Response compression:** Enable `Content-Encoding: gzip` or `br` (Brotli) on your server. JSON compresses extremely well (70-80% reduction) because it is repetitive text. This is free performance — enable it by default in your web server or framework.

3. **Image optimization hints:** Return image URLs with size parameters (`avatar_url` pointing to a CDN with `?w=64&h=64&fmt=webp`) rather than original high-resolution images. Mobile screens don't need 4K avatars in a list view.

4. **Exclude null and empty fields:** Serialize with `exclude_none=True` in Pydantic. If 30% of fields are null, they still consume bytes in JSON.

**Techniques to reduce round trips:**

1. **Composite/aggregated endpoints (Backend for Frontend pattern):** Instead of requiring the mobile app to make 4 sequential requests to assemble the home screen, create one `/mobile/feed` endpoint that fetches all required data server-side (in parallel with `asyncio.gather`) and returns it in one response. One round trip at 150ms RTT vs four sequential at 600ms.

2. **HTTP/2:** Multiplexes multiple requests over one connection. If you cannot use a composite endpoint, HTTP/2 removes the cost of establishing new TCP connections for each request.

3. **Conditional requests (ETags):** Return an `ETag` header with responses. Mobile clients send `If-None-Match: <etag>` on subsequent requests. If data hasn't changed, server returns `304 Not Modified` with no body — saves bandwidth and battery.

4. **Cursor-based pagination:** Avoids large `OFFSET` queries that slow down as the user scrolls. The cursor encodes the position in the result set, enabling efficient DB queries and consistent results if new items are added.

**How sparse fieldsets help specifically:**

A mobile feed item in a social app might have 50 fields (for web, admin tools, analytics). The mobile list view needs 5 of them. Without sparse fieldsets: serialize 50 fields × 100 posts = large payload. With sparse fieldsets: serialize 5 fields × 100 posts = 90% smaller payload, faster parse time, less memory allocation on the mobile device.

The **Backend for Frontend (BFF) pattern** is the architectural version of this: a dedicated API layer for mobile that aggregates, filters, and shapes data specifically for mobile clients rather than exposing the same API as the web client.

**How to think through this:**
1. Every byte you don't send is cheaper than compression — design the response shape around what the client actually renders.
2. Every round trip at mobile latency is expensive — aggregate server-side, not client-side.
3. Caching at the client is the ultimate optimization — a 304 response is cheaper than any payload optimization.

**Key takeaway:** Mobile API optimization is fundamentally about reducing bytes (sparse fieldsets, compression, exclude nulls) and reducing round trips (composite endpoints, HTTP/2, conditional requests) — design response shapes around what the mobile UI renders, not what your data model contains.

</details>

> 📖 **Theory:** [Mobile API Optimization](./09_api_performance_scaling/performance_guide.md)

## 🏋️ Tier 4 — Interview / Scenario

---

### Q76 · [Interview] · `explain-rest-principles`

> **Explain REST to a junior developer who has only written function calls. Use an analogy and then map the REST constraints to concrete HTTP examples.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Think of a restaurant. You (the client) sit at a table and interact only through a waiter (the HTTP interface). You don't walk into the kitchen — you send requests using a menu (the API). The kitchen doesn't remember who you are between visits; every order is self-contained. That's REST.

**How to think through this:**
1. **Uniform Interface** — Every resource has a stable URL. Just as every dish has a menu item number, `/users/42` always means user 42. You interact through standard verbs: `GET /users/42`, `POST /users`, `DELETE /users/42`.
2. **Stateless** — The server holds no session memory. Every request carries everything needed: auth token, params, body. Like calling a support line where the agent has no call history — you re-introduce yourself every time.
3. **Client-Server separation** — The menu hides kitchen complexity. The client doesn't know if the server uses Postgres or MongoDB; it only knows the contract (URL + response shape).
4. **Cacheable** — The waiter can tell you "today's soup hasn't changed since yesterday" — that's a `Cache-Control: max-age=3600` header. The client can reuse the response.
5. **Layered System** — Between you and the kitchen there may be a head waiter, a manager, a food runner — the client doesn't care. In HTTP: load balancers, API gateways, CDNs are invisible to the caller.
6. **Code on Demand (optional)** — The kitchen can send you a recipe card (JavaScript) to execute client-side.

**Key takeaway:** REST is not a protocol — it's a set of architectural constraints that make HTTP APIs predictable, scalable, and decoupled.

</details>

> 📖 **Theory:** [REST Principles](./02_rest_fundamentals/rest_explained.md)

---

### Q77 · [Interview] · `explain-idempotency-analogy`

> **Explain idempotency using a non-technical analogy. Then map it to two concrete API examples: one idempotent, one not.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Pressing the elevator button is idempotent. Press it once — the elevator is called. Press it ten more times — still one elevator comes. The outcome after the first press doesn't change no matter how many times you repeat it.

**How to think through this:**
1. **The analogy in plain terms** — An operation is **idempotent** if running it N times produces the same result as running it once. The key is the *end state*, not the number of calls.
2. **Idempotent example — `PUT /users/42`** with body `{"name": "Alice"}`. Whether you send this once or five times, user 42's name is Alice. The server state is identical after each call.
3. **Non-idempotent example — `POST /payments`** with body `{"amount": 100}`. Send it five times and you've charged the customer $500. Each call creates a new resource and changes state additively.
4. **Why it matters** — Networks fail. Clients retry. If your endpoint isn't idempotent and clients retry on timeout, you get duplicate charges, duplicate records, or corrupted state. Design charge endpoints with an **idempotency key** header so retries are safe: `Idempotency-Key: uuid-abc123`.

**Key takeaway:** Idempotency makes retries safe — design any state-changing endpoint to be idempotent wherever possible, and use idempotency keys when you can't.

</details>

> 📖 **Theory:** [Idempotency](./02_rest_fundamentals/rest_explained.md)

---

### Q78 · [Interview] · `explain-jwt-vs-sessions`

> **Explain the difference between JWT and server-side sessions to a developer who has only used cookies. Cover: where state is stored, scalability implications, and revocation.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
With cookies and server-side sessions, the server is the librarian who holds your borrowing record. You carry a library card (session ID), and every time you visit, the librarian looks up your record in their filing cabinet (session store). With JWTs, the librarian stamps all your borrowing history directly onto your library card. You carry the full record; the librarian just checks the stamp is genuine.

**How to think through this:**
1. **Where state lives** — **Server-side sessions** store user data in a backend store (Redis, DB). The client cookie holds only a session ID — a pointer. **JWTs** encode the user data (claims) directly in the token. The server stores nothing; it decodes and verifies the signature on each request.
2. **Scalability** — Sessions require every server to reach the same session store. Add 10 servers and they all need Redis access. JWTs are **stateless** — any server can verify a token independently using the shared secret or public key. This makes horizontal scaling trivial.
3. **Revocation** — Sessions win here. To invalidate a session, delete it from the store — effective immediately. JWTs cannot be invalidated before expiry without a server-side blocklist, which reintroduces state. If a JWT is stolen, it's valid until `exp`. Mitigation: short expiry (15 min) + refresh token rotation.
4. **CSRF risk** — Cookies carrying session IDs are CSRF-vulnerable. JWTs stored in `Authorization` headers (not cookies) avoid this, but then you have XSS risk if stored in `localStorage`.

**Key takeaway:** Sessions are easier to revoke; JWTs scale better — the choice is a tradeoff between operational simplicity and distributed statelessness.

</details>

> 📖 **Theory:** [JWT vs Sessions](./05_authentication/securing_apis.md)

---

### Q79 · [Interview] · `explain-rate-limiting-pm`

> **A product manager asks why you need rate limiting — "can't we just trust our users?" Give a clear, non-technical explanation with a concrete risk example.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Imagine you run a coffee shop with one barista. Most customers order one coffee. But one day a customer walks in and orders 10,000 coffees in a minute — whether by accident (a bug in their app) or on purpose. Your barista collapses. Every other customer gets nothing. Rate limiting is the "one order at a time" sign on the door.

**How to think through this:**
1. **The trust problem** — It's not about bad intent. A developer's script with a misconfigured retry loop can accidentally hammer your API with thousands of requests. Their bug becomes your outage.
2. **Concrete risk — DDoS amplification** — Without rate limiting, an attacker sends 10,000 requests per second to `GET /search?q=*`. Your database falls over. Every user — including paying customers — gets 503 errors. Revenue stops.
3. **Financial risk** — If your API calls a paid third-party service (LLM, SMS, maps), one runaway client can exhaust your entire monthly budget in hours.
4. **Fairness** — One heavy user consuming 90% of capacity degrades experience for all other users. Rate limits enforce fair resource allocation.
5. **The "trust" reframe** — Rate limiting isn't distrust — it's a seatbelt. It protects users from their own mistakes and protects your system from cascading failures.

**Key takeaway:** Rate limiting protects the service from both malicious actors and accidental abuse — it's infrastructure safety, not a statement of distrust.

</details>

> 📖 **Theory:** [Rate Limiting](./09_api_performance_scaling/performance_guide.md)

---

### Q80 · [Interview] · `explain-backward-compatibility`

> **Explain backward compatibility in API design to a junior developer. Give an example of a breaking change vs a non-breaking change. Why does it matter in production?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A backward-compatible change is like rearranging your living room — guests who've been before can still find the sofa. A breaking change is like removing the front door — they can't get in at all.

**How to think through this:**
1. **Definition** — An API change is **backward compatible** if existing clients continue to work without modification after the change is deployed.
2. **Breaking change example** — Renaming a field in the response from `user_name` to `username`. Any client parsing `response.user_name` now gets `undefined` or an error. The contract is broken.
3. **Non-breaking change example** — Adding a new optional field `last_login` to the response. Old clients ignore the field they don't know about. New clients can use it. No existing code breaks.
4. **Other breaking changes** — Removing a field, changing a field's type (string → integer), changing HTTP status codes, making an optional parameter required, removing an endpoint.
5. **Why it matters in production** — You don't control client deploy schedules. External companies may have 500 clients consuming your API. A breaking change deployed without a migration path can take down production systems for those clients instantly and simultaneously. Backward compatibility buys migration time.

**Key takeaway:** Additive changes are safe; removals and renames are breaking — always version your API before introducing breaking changes.

</details>

> 📖 **Theory:** [Backward Compatibility](./08_versioning_standards/versioning_strategy.md)

---

### Q81 · [Interview] · `compare-rest-graphql`

> **A team is debating REST vs GraphQL for a new product. Give a structured comparison covering: client flexibility, server complexity, caching, tooling, and when each wins.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**How to think through this:**
1. **Client flexibility** — **GraphQL** wins. Clients specify exactly the fields they need in the query. A mobile client can request a minimal payload; a web client can request rich data — from the same endpoint. With **REST**, the server defines response shape. Under-fetching (need more fields) forces extra requests; over-fetching (too many fields) wastes bandwidth.
2. **Server complexity** — REST wins. REST endpoints are simple functions. GraphQL requires a schema definition, resolver functions per field, and a query parser/executor. N+1 query problems in resolvers are a real operational concern and require DataLoader patterns to fix.
3. **Caching** — REST wins clearly. HTTP caching (CDN, `Cache-Control`, ETags) works at the URL level. Every `GET /products/42` is cacheable identically. GraphQL uses `POST` for queries by default — standard HTTP caches can't cache POST bodies. Apollo and Relay have client-side caching, but it's application-layer, not infrastructure-level.
4. **Tooling** — REST has broader ecosystem maturity (Postman, OpenAPI/Swagger, widespread framework support). GraphQL tooling (GraphiQL, introspection, code generation) is excellent but narrower.
5. **When REST wins** — Simple CRUD APIs, public APIs consumed by unknown third parties, teams that need HTTP caching, or teams without GraphQL expertise.
6. **When GraphQL wins** — Products with multiple client types (mobile/web/TV) needing different data shapes, rapid frontend iteration, or when reducing network round-trips is critical.

**Key takeaway:** GraphQL is a client flexibility tool with operational tradeoffs — REST is the safer default unless your clients genuinely need query flexibility.

</details>

> 📖 **Theory:** [REST vs GraphQL](./13_graphql/graphql_story.md)

---

### Q82 · [Interview] · `compare-jwt-vs-sessions`

> **Compare JWTs and server-side sessions on: scalability, revocation, storage, CSRF risk, and implementation complexity. Which would you recommend for a stateless microservices architecture?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**How to think through this:**
1. **Scalability** — **JWTs** win. No shared state required. Any microservice can verify a token using the public key without a central lookup. Sessions require every service to reach a shared session store (Redis cluster), which becomes a bottleneck and single point of failure.
2. **Revocation** — **Sessions** win. Delete the session record and the user is immediately logged out. JWTs are self-contained and valid until expiry. Revocation requires a distributed blocklist, which reintroduces the stateful session problem you were trying to avoid.
3. **Storage** — Sessions store data server-side; the client holds only an opaque ID. JWTs store claims client-side (encoded, not encrypted by default — don't put secrets in JWT payloads). JWT size grows with claims and travels in every request header.
4. **CSRF risk** — Sessions stored in `HttpOnly` cookies are CSRF-vulnerable (browser attaches cookies automatically). JWTs in `Authorization: Bearer` headers are not CSRF-vulnerable but are XSS-vulnerable if stored in `localStorage`.
5. **Implementation complexity** — Sessions are simpler to implement and reason about. JWTs require key management, rotation strategy, and refresh token handling.
6. **Recommendation for microservices** — **JWTs** with short expiry (15 minutes) and refresh token rotation. The stateless verification across services is the decisive advantage. Mitigate revocation weakness with short-lived access tokens and a revocation list only for the refresh token layer.

**Key takeaway:** JWTs are the correct default for stateless microservices — but pair them with short expiry and refresh token rotation to manage the revocation tradeoff.

</details>

> 📖 **Theory:** [JWT vs Sessions](./05_authentication/securing_apis.md)

---

### Q83 · [Interview] · `compare-sync-async-api`

> **Compare synchronous and asynchronous API patterns. Give a concrete example where async is necessary (not just preferred). What does the client need to handle that it doesn't in sync APIs?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**How to think through this:**
1. **Synchronous** — Client sends request, connection stays open, server processes, client gets response. Simple request-response. Works when processing is fast (under a few seconds).
2. **Asynchronous** — Client sends request, server immediately returns a job ID (`202 Accepted`), processing happens in the background. Client polls a status endpoint or receives a webhook when done.
3. **Where async is necessary (not just preferred)** — Video transcoding. A user uploads a 2GB video. Transcoding takes 8 minutes. You cannot hold an HTTP connection open for 8 minutes — proxies time out (typically 30–60 seconds), mobile clients disconnect, and you tie up a server thread. The async pattern is the only viable design: `POST /transcode` → `202 {"job_id": "abc"}` → client polls `GET /jobs/abc` → eventually `{"status": "complete", "url": "..."}`.
4. **What the client must now handle** — Polling logic (with backoff to avoid hammering the server), job state management (`pending` / `processing` / `complete` / `failed`), timeout and retry for the poll itself, and handling partial failure (job failed after partial processing). In sync APIs, a single try-catch handles everything.
5. **Webhook alternative** — Instead of client polling, server calls the client's callback URL when done. Simpler for the client but requires the client to expose a public endpoint and handle delivery failures.

**Key takeaway:** Async APIs shift complexity from the server (blocking thread) to the client (state management) — use them when processing time exceeds HTTP timeout limits.

</details>

> 📖 **Theory:** [Sync vs Async API](./16_api_design_patterns/design_guide.md)

---

### Q84 · [Interview] · `compare-gateway-vs-mesh`

> **Compare an API gateway vs a service mesh. What does each handle? Is there overlap? Could you use both together?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**How to think through this:**
1. **API Gateway** — Sits at the **north-south boundary** (external client to internal services). Handles: auth/authz, rate limiting, request routing, SSL termination, request/response transformation, API versioning, developer portal. It's the front door. Examples: Kong, AWS API Gateway, NGINX.
2. **Service Mesh** — Operates **east-west** (service to service inside the cluster). Implemented as sidecar proxies (Envoy/Linkerd) injected into every pod. Handles: mTLS between services, load balancing, circuit breaking, retries, distributed tracing, traffic shaping. Examples: Istio, Linkerd, Consul Connect.
3. **Overlap** — Both can do: load balancing, retries, circuit breaking, observability. The duplication is real and can cause confusion if both are configured to handle the same concern.
4. **Can you use both?** — Yes, and it's common at scale. The gateway handles the external perimeter (auth, rate limiting, developer-facing concerns). The mesh handles internal service reliability (mTLS, retries, tracing). The division: gateway owns external policy, mesh owns internal reliability. The gateway talks to the mesh's ingress, not directly to pods.
5. **When you don't need both** — Small teams or early-stage products: a gateway alone is sufficient. Add a mesh when you have many services, need zero-trust networking (mTLS), or need fine-grained traffic control between services.

**Key takeaway:** API gateways control the perimeter; service meshes control the interior — at scale they complement each other, but only add the mesh when internal service complexity justifies it.

</details>

> 📖 **Theory:** [Gateway vs Service Mesh](./15_api_gateway/gateway_patterns.md)

---

### Q85 · [Interview] · `compare-webhook-vs-polling`

> **Your interviewer asks: "We need real-time notifications when an order ships. Should we use webhooks or polling?" Give a structured answer with the key question you'd ask first.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**How to think through this:**
1. **The key question first** — "Who controls the clients?" If you own both sides (internal microservice), webhooks are clean. If this is a public API used by external companies, the answer changes significantly — not all clients can receive inbound HTTP calls (firewalls, NAT, serverless consumers).
2. **Polling** — Client periodically calls `GET /orders/{id}/status`. Simple to implement on both sides. Works behind any network. Disadvantages: latency is at least one poll interval, generates load even when nothing changed, and at scale (millions of clients polling every 30s) can crush your server.
3. **Webhooks** — Server calls the client's registered callback URL when the event fires. Truly real-time. Zero wasted requests. Disadvantages: client must expose a public HTTPS endpoint, server must handle delivery failures with retry logic and dead-letter queues, client must handle duplicate deliveries (webhook retry on timeout may send twice — idempotency required).
4. **Recommendation for order shipping** — If clients are internal services: **webhooks** — fire-and-forget, real-time, clean decoupling via an event bus. If clients are external merchants: offer **webhooks as primary** (they're industry standard for e-commerce: Stripe, Shopify all use them), with a polling fallback endpoint for clients that can't receive inbound calls.
5. **Long polling as middle ground** — Client opens a request, server holds it open until an event fires (or 30s timeout). Real-time-ish, no inbound requirement. Used by Stripe's event API.

**Key takeaway:** Webhooks are more efficient and real-time but require reliable delivery infrastructure — polling is the simpler fallback when clients can't accept inbound connections.

</details>

> 📖 **Theory:** [Webhook vs Polling](./16_api_design_patterns/design_guide.md)

---

### Q86 · [Design] · `production-api-slow`

> **Your API's p99 latency jumps from 50ms to 2s after a deploy. What is your diagnostic process? List the first 5 things you'd check in order.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**How to think through this:**
1. **Check: was it this deploy?** — Immediately correlate the latency spike with the deploy timestamp in your monitoring (Datadog, Grafana). If the timing aligns, prepare to rollback. Don't investigate further before knowing rollback is an option.
2. **Check: which endpoints are slow?** — Isolate whether the degradation is global (all routes) or specific (one endpoint). If it's one endpoint, the blast radius is smaller and points to a code change in that route. Global degradation suggests infrastructure — DB connection pool, external dependency, memory pressure.
3. **Check: database query performance** — The most common cause of sudden latency regression. Look at slow query logs. Did the deploy introduce a missing index, an N+1 query, or a query that hits a larger dataset than in staging? Use `EXPLAIN ANALYZE` on suspicious queries.
4. **Check: external dependency latency** — If your route calls an external API (auth service, payment processor, third-party enrichment), check if that service's response time degraded. A slow external call propagates as your p99 spike.
5. **Check: resource saturation** — CPU, memory, DB connection pool exhaustion, thread pool saturation. A memory leak in the new code can cause GC pressure that shows up as latency spikes, not errors. Check pod/container metrics and connection pool metrics (active vs waiting).

**After these 5:** If none point to a clear cause, enable distributed tracing (if not already on) to trace the full request path and identify which span is slow.

**Key takeaway:** Correlate with the deploy first, then narrow by endpoint, then drill into DB → external deps → resources — in that order.

</details>

> 📖 **Theory:** [API Performance](./09_api_performance_scaling/performance_guide.md)

---

### Q87 · [Design] · `production-auth-bug`

> **Users report they can see other users' orders. You suspect a multi-tenancy bug in the auth middleware. How do you investigate, mitigate immediately, and then fix properly?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**How to think through this:**
1. **Immediate mitigation (first 5 minutes)** — This is a **P0 data breach**. Before investigating, take the affected endpoint offline or add a hard block. Notify your security/incident response team. Do not investigate casually while data is actively leaking.
2. **Preserve evidence** — Before any rollback, capture logs, request traces, and DB audit logs. A rollback may destroy the ability to understand scope.
3. **Investigate: reproduce in staging** — Try to reproduce: log in as User A, call `GET /orders`. Does the response contain User B's orders? If yes, the bug is in the query or the middleware that scopes it.
4. **Investigate: the auth middleware** — Check whether the middleware correctly sets `request.state.user` and whether the order query uses `WHERE user_id = request.state.user.id`. Common bugs: middleware runs but the route doesn't use `request.state.user` for filtering — it uses a query param or path param that the attacker controls. Or the middleware sets user only when a token is present but doesn't block the request when the token is absent.
5. **Investigate: scope of exposure** — Query DB audit logs or application logs: which user IDs were accessed by which authenticated users? How many records? This determines breach notification requirements.
6. **Proper fix** — Add a **scoping assertion** at the data layer, not just the middleware. Every query for user-owned resources must include `filter(Order.user_id == current_user.id)`. Never trust a client-supplied user ID. Add an integration test that verifies User A cannot access User B's orders.

**Key takeaway:** Multi-tenancy bugs require immediate containment first, then root cause analysis — and the fix must live at the data layer, not just the auth check.

</details>

> 📖 **Theory:** [Auth Security](./05_authentication/securing_apis.md)

---

### Q88 · [Design] · `production-stale-data`

> **Your API returns stale product prices even after the database is updated. The cache TTL is 5 minutes. How do you fix this without removing caching entirely?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**How to think through this:**
1. **Root cause** — Time-based TTL caching is passive invalidation. The cache doesn't know the DB changed; it only expires entries after a fixed duration. 5 minutes of stale pricing is unacceptable for commerce.
2. **Fix 1: Cache-aside with active invalidation (recommended)** — When a price is updated in the DB (via admin tool, service, or migration), also delete or update the corresponding cache key. The write path becomes: `UPDATE products SET price=X WHERE id=42` + `cache.delete("product:42")`. Next read repopulates the cache from fresh DB data. This is **write-through invalidation**.
3. **Fix 2: Publish invalidation events** — If the write path is separate (another service updates prices), use an event bus. Price update service publishes `PriceUpdated{product_id: 42}`. API service subscribes and deletes the cache key. Decoupled but requires messaging infrastructure.
4. **Fix 3: Reduce TTL for price-sensitive data** — A blunt fix: reduce TTL to 30 seconds for price keys specifically. Acceptable staleness window shrinks, cache still absorbs read load. Not ideal but fast to deploy while you implement proper invalidation.
5. **Fix 4: Cache versioning / ETag** — Include a version/hash in the cache key tied to the record's `updated_at`. When the DB record changes, the key changes, forcing a cache miss. Requires the read path to know the current version.
6. **Avoid** — Don't remove caching. Product reads likely far outnumber price updates. The cache is doing its job — you need to couple writes to invalidations.

**Key takeaway:** Time-based TTL caches go stale on writes — add active invalidation at the write path so the cache reflects reality within milliseconds.

</details>

> 📖 **Theory:** [Cache Freshness](./09_api_performance_scaling/performance_guide.md)

---

### Q89 · [Design] · `production-rate-limit-good-users`

> **Your rate limiter is blocking legitimate heavy users (enterprise customers) because it uses a single global rate limit. How do you redesign it to support tiered limits without a full rewrite?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**How to think through this:**
1. **Identify the key** — The current limiter likely uses IP or API key as the rate limit key with a hardcoded limit. The fix is to make the limit value dynamic, not change the algorithm.
2. **Step 1: Add a tier lookup** — When a request arrives with an API key, look up the tier for that key: `tier = db.get_tier(api_key)` (or from a cached mapping). Tiers: `free=100/min`, `pro=1000/min`, `enterprise=10000/min`.
3. **Step 2: Parameterize the limit** — Instead of `rate_limiter.check(key, limit=100)`, call `rate_limiter.check(key, limit=tier.limit)`. The limiter algorithm (token bucket, sliding window) doesn't change — only the cap value changes per key.
4. **Step 3: Cache the tier mapping** — Tier lookups on every request would add latency. Cache `api_key → tier_limit` in Redis or in-process with a short TTL (5 minutes). Tier changes propagate within one TTL window.
5. **Step 4: Add headers** — Return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers in every response so clients know their current limits and can implement backoff without guessing.
6. **Operational addition** — Allow manual override for specific API keys (e.g., an enterprise customer doing a one-time bulk migration). A `rate_limit_overrides` table with a per-key cap and expiry satisfies this without changing the core logic.

**Key takeaway:** Tiered rate limiting requires only a dynamic limit lookup per API key — the algorithm itself doesn't need to change, just the limit value fed into it.

</details>

> 📖 **Theory:** [Tiered Rate Limiting](./09_api_performance_scaling/performance_guide.md)

---

### Q90 · [Design] · `design-versioning-breaking-change`

> **You need to change a field name in a response from `user_name` to `username` — a breaking change. Design a versioning strategy that allows the change without breaking existing clients.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**How to think through this:**
1. **Never change v1 in place** — The first rule: `v1` responses are frozen. Changing `user_name` to `username` in v1 breaks every existing client immediately.
2. **Introduce v2 via URL versioning** — Create `/v2/users/{id}` that returns `username`. Keep `/v1/users/{id}` returning `user_name`. URL versioning is explicit, cacheable, and client-controlled: `GET /v2/users/42`.
3. **Dual-write during transition** — For a migration window (e.g., 12 months), the v1 response can include **both** fields: `{"user_name": "alice", "username": "alice"}`. This is backward compatible and gives clients a path to migrate without a hard cutover.
4. **Deprecation signaling** — Add headers to all v1 responses: `Deprecation: true` and `Sunset: Sat, 01 Jan 2026 00:00:00 GMT`. RFC 8594 (`Sunset`) and RFC 9512 (`Deprecation`) are the standards. Clients' HTTP clients can log these headers.
5. **Communication** — Email all registered API consumers with: the deprecation timeline, the v2 migration guide, a diff of the response change, and a sandbox to test v2. 12 months minimum for external APIs.
6. **Sunset enforcement** — On the sunset date, `/v1/users/{id}` returns `410 Gone` with a body pointing to the migration guide. Don't silently break — make the error message actionable.

**Key takeaway:** Breaking changes require a new version, a deprecation timeline with `Sunset` headers, and clear client communication — never mutate a live version's contract.

</details>

> 📖 **Theory:** [Breaking Changes](./08_versioning_standards/versioning_strategy.md)

---

## 🧠 Tier 5 — Critical Thinking

---

### Q91 · [Logical] · `predict-jwt-expiry`

> **A client has a valid JWT that expires in 30 seconds. The client makes a request. The server validates the token. 45 seconds later, the client makes another request with the same token. What happens and why? What should the client have done?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The first request succeeds. The second request fails with `401 Unauthorized`.

**How to think through this:**
1. **First request (t=0)** — Token has 30 seconds remaining. Server checks `exp` claim: `now < exp` is true. Token is valid. Request proceeds normally.
2. **Second request (t=45s)** — Same token. Server checks `exp`: `now > exp` by 15 seconds. The `exp` claim has passed. Server rejects with `401`. The token is **expired** — it doesn't matter that it was valid 45 seconds ago. JWTs are time-bounded by design.
3. **What the client should have done** — Implement a **refresh token flow**. Before the access token expires, the client should exchange a long-lived **refresh token** for a new access token: `POST /auth/refresh` with the refresh token in the body (not in a header — it's a secret). The server issues a new short-lived JWT. This should happen proactively (e.g., when `remaining_ttl < 60s`) or reactively (on `401`, retry once after refreshing).
4. **Common mistake** — Clients that only handle `401` reactively will fail on the second request, refresh, then retry. This works but causes one failed request per expiry cycle. Proactive refresh (check `exp` before sending) avoids the failed request entirely.

**Key takeaway:** JWTs are stateless time-bombs — clients must implement proactive refresh logic before expiry, not just reactive retry on 401.

</details>

> 📖 **Theory:** [JWT Expiry](./05_authentication/securing_apis.md)

---

### Q92 · [Critical] · `predict-concurrent-idempotent`

> **Two identical POST /payments requests with the same idempotency key arrive simultaneously (race condition). Your idempotency check is: `if key not in db: process_and_store()`. What is the bug? How do you fix it?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Both requests can pass the `if key not in db` check simultaneously — before either has written to the DB — resulting in two payments being processed for one idempotency key.

**How to think through this:**
1. **The race** — Thread A checks: `key not in db` → True. Thread B checks simultaneously: `key not in db` → True (A hasn't written yet). Both proceed to `process_and_store()`. Two charges. The idempotency guarantee is broken.
2. **Root cause** — The check-then-act is not atomic. Between the read check and the write, another thread can observe the same state.
3. **Fix 1: Database unique constraint + optimistic insert** — Insert the idempotency key into the DB *before* processing, with a `UNIQUE` constraint on the key column. Use an upsert or catch the unique constraint violation:
```python
try:
    db.execute("INSERT INTO idempotency_keys (key, status) VALUES (?, 'processing')", [key])  # ← atomic claim
    result = process_payment()
    db.execute("UPDATE idempotency_keys SET status='complete', result=? WHERE key=?", [result, key])
    return result
except UniqueConstraintError:
    # Another request already claimed this key
    return wait_for_result(key)  # ← poll until the first request completes
```
4. **Fix 2: Redis SET NX (set if not exists)** — `SET idempotency:{key} "processing" NX EX 300` — Redis executes this atomically. Only one request gets `True`; all others get `False` and wait/return the cached result.
5. **Edge case** — What if the first request crashes after claiming the key but before completing? The key is stuck in `processing`. Add a timeout: if a key has been in `processing` for more than N seconds, treat it as failed and allow retry.

**Key takeaway:** Idempotency requires atomic claim-before-process, not check-then-act — use a unique constraint or atomic Redis NX to prevent the race condition.

</details>

> 📖 **Theory:** [Idempotency Race Condition](./16_api_design_patterns/design_guide.md)

---

### Q93 · [Logical] · `predict-dependency-chain`

> **Trace the execution order: FastAPI route has `Depends(get_db)` and `Depends(get_current_user)`, where `get_current_user` also has `Depends(get_db)`. How many times is `get_db` called per request? Why?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
`get_db` is called **once** per request. FastAPI's dependency injection system caches resolved dependencies within a single request scope.

**How to think through this:**
1. **The dependency graph** — The route depends on: `get_db` (directly) and `get_current_user` (directly). `get_current_user` depends on `get_db`. So `get_db` appears twice in the dependency tree.
2. **FastAPI's caching behavior** — By default, FastAPI uses `use_cache=True` for dependencies. When it resolves the dependency graph, it calls each unique dependency **once per request** and reuses the resolved value for all dependents.
3. **Resolution order** — FastAPI resolves the tree bottom-up: `get_db` is called once → its result is passed to both the route and `get_current_user`. `get_current_user` receives the already-resolved `db` session. The route receives both the session and the current user.
4. **Why this matters** — This ensures all code in a single request uses the **same database session**, which is critical for transactional consistency. If `get_db` were called twice, the route and the auth check would use different DB connections — a transaction opened in the route would not be visible in the auth check.
5. **How to override** — If you explicitly need a fresh call each time: `Depends(get_db, use_cache=False)`. Rarely needed; know the option exists.

**Key takeaway:** FastAPI caches dependency results within a request — a dependency appearing N times in the tree is still called once, ensuring shared state like DB sessions is consistent.

</details>

> 📖 **Theory:** [Dependency Scoping](./07_fastapi/advanced_guide.md)

---

### Q94 · [Debug] · `debug-auth-middleware`

> **This authentication middleware has a security bug. Find it:**

```python
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token:
        user = verify_token(token)
        request.state.user = user
    response = await call_next(request)
    return response
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The bug is that requests **without a token are allowed through** with no `request.state.user` set. Any protected route that assumes `request.state.user` exists will either crash or silently allow unauthenticated access.

**How to think through this:**
1. **The bug** — The `if token:` block only runs when a token is present. If no `Authorization` header is sent, the middleware calls `call_next(request)` without setting `request.state.user` and without returning a `401`. The request passes to the route handler as if nothing happened.
2. **Secondary bug** — Even when a token is present, `verify_token(token)` may return `None` if the token is invalid or expired. The code doesn't check this — it blindly sets `request.state.user = None`, which is semantically wrong (an invalid token should not set a user at all).
3. **The fix:**
```python
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    PUBLIC_PATHS = {"/health", "/docs", "/openapi.json"}
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)  # ← allow public routes through

    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return Response("Missing token", status_code=401)  # ← reject missing token

    user = verify_token(token)
    if user is None:
        return Response("Invalid or expired token", status_code=401)  # ← reject bad token

    request.state.user = user
    return await call_next(request)
```
4. **Why this is dangerous** — A developer writes `current_user = request.state.user` in a route. If `user` was never set, this raises `AttributeError` — which FastAPI turns into a `500`. Depending on error handling, this may leak stack traces. Worse: if the route uses `getattr(request.state, "user", None)` as a guard, unauthenticated requests silently proceed.

**Key takeaway:** Auth middleware must explicitly reject requests with missing or invalid tokens — an absent token is not the same as a public route.

</details>

> 📖 **Theory:** [Auth Middleware](./11_api_security_production/security_hardening.md)

---

### Q95 · [Debug] · `debug-cors-prod`

> **CORS works fine in development but fails in production only for PUT and DELETE requests. Development uses `allow_origins=["http://localhost:3000"]`, production uses `allow_origins=["https://app.example.com"]`. What is the likely cause and fix?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The likely cause is missing `allow_methods` configuration — production is not allowing `PUT` and `DELETE` in the CORS preflight response, or the CORS middleware configuration is missing `allow_methods` entirely and defaulting to `GET` and `POST` only.

**How to think through this:**
1. **Why preflight matters** — Browsers send a CORS **preflight** `OPTIONS` request before `PUT` and `DELETE` (these are "non-simple" methods per the CORS spec). `GET` and `POST` with simple content types skip preflight — which is why those work fine. The preflight asks: "Is this method allowed from this origin?"
2. **Why it works in dev** — If development uses a proxy (Vite/CRA dev server proxying `/api` to the backend), the browser never sees a cross-origin request — the proxy makes it same-origin. So CORS is bypassed entirely in dev.
3. **The bug** — Production serves the API on a different domain (`api.example.com`) from the frontend (`app.example.com`), so CORS is real. The CORS middleware configuration may be:
```python
# Missing allow_methods — defaults to GET, POST only
app.add_middleware(CORSMiddleware, allow_origins=["https://app.example.com"])
```
4. **The fix:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],  # ← explicit methods
    allow_headers=["Authorization", "Content-Type"],  # ← explicit headers if using auth
)
```
5. **Verify** — In browser devtools, inspect the failed preflight `OPTIONS` request. The response should include `Access-Control-Allow-Methods: PUT, DELETE`. If it doesn't, the server is not returning the correct preflight response.

**Key takeaway:** CORS failures on PUT/DELETE but not GET/POST point to missing `allow_methods` — preflight only fires for non-simple methods, which is why the bug is invisible until production.

</details>

> 📖 **Theory:** [CORS Preflight](./11_api_security_production/security_hardening.md)

---

### Q96 · [Debug] · `debug-n-plus-one-load`

> **This endpoint works correctly but a load test reveals it makes 101 database queries for a list of 100 users. Find the N+1 bug and fix it:**

```python
@app.get("/users/{team_id}/members")
async def get_team_members(team_id: int, db: Session = Depends(get_db)):
    users = db.query(User).filter(User.team_id == team_id).all()
    return [{"id": u.id, "name": u.name, "role": u.role.name} for u in users]
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The bug is `u.role.name` inside the list comprehension. SQLAlchemy lazy-loads the `role` relationship for each user individually — 100 users = 100 separate `SELECT * FROM roles WHERE id = ?` queries, plus 1 query for the users list = 101 total.

**How to think through this:**
1. **The N+1 pattern** — The first query fetches N users. Then for each user, accessing `u.role` triggers a lazy-load: a new query to fetch that user's role. N users = N extra queries. Total: 1 + N.
2. **Why it's invisible in unit tests** — With 1 or 2 users in test data, the difference between 2 queries and 3 queries is imperceptible. Load tests with realistic data expose it.
3. **Fix — eager loading with `joinedload`:**
```python
from sqlalchemy.orm import joinedload

@app.get("/users/{team_id}/members")
async def get_team_members(team_id: int, db: Session = Depends(get_db)):
    users = (
        db.query(User)
        .options(joinedload(User.role))  # ← JOIN roles in the same query
        .filter(User.team_id == team_id)
        .all()
    )
    return [{"id": u.id, "name": u.name, "role": u.role.name} for u in users]
```
This generates one SQL query with a `JOIN` on the roles table. 100 users = 1 query.

4. **Alternative — `selectinload`** — For large result sets where a JOIN would produce wide rows, `selectinload` is often better: it issues 2 queries total (one for users, one `SELECT ... WHERE user_id IN (...)` for all roles), avoiding the Cartesian product of a JOIN.
```python
.options(selectinload(User.role))  # ← 2 queries total instead of N+1
```

**Key takeaway:** Any relationship access inside a loop is an N+1 smell — use `joinedload` or `selectinload` to eager-load relationships in the initial query.

</details>

> 📖 **Theory:** [N+1 Query Fix](./07_fastapi/database_guide.md)

---

### Q97 · [Design] · `design-rest-vs-graphql`

> **You are building a social media platform. The mobile app needs very different data from the web app (mobile: minimal fields, web: rich data). Would you choose REST or GraphQL? Justify the choice with concrete reasoning about your specific constraints.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
GraphQL is the correct choice for this specific scenario. The constraints map directly to GraphQL's core strength.

**How to think through this:**
1. **The concrete problem with REST here** — You have two clients with divergent data needs. REST options: (a) one endpoint returns the union of all fields — mobile over-fetches, wasting bandwidth on a cellular connection; (b) two separate endpoints (`/mobile/posts`, `/web/posts`) — now you maintain parallel endpoint families that diverge over time; (c) query parameters for field selection — you've reinvented a worse version of GraphQL.
2. **Why GraphQL solves this cleanly** — One schema, one endpoint. Mobile query requests `{ post { id, title, author { name } } }`. Web query requests `{ post { id, title, body, author { name, avatar, bio }, comments { text, likes }, media { url, type } } }`. The server returns exactly what's requested. One codebase, two clients, zero over-fetching.
3. **Caching concern** — GraphQL's caching disadvantage matters less here: social media feeds are personalized and change frequently, so CDN caching of REST responses wouldn't help much anyway. Per-user feeds don't benefit from shared HTTP cache.
4. **Tooling for a new product** — Apollo Server + Apollo Client (web) + Apollo Kotlin/iOS are mature. Code generation from schema gives you typed queries on the client. For a new product, this is a productivity advantage.
5. **When REST would win** — If the API were public (third parties, unknown clients), REST + OpenAPI documentation is more universally accessible. For internal clients you own, GraphQL's flexibility is worth the operational overhead.

**Key takeaway:** When you own multiple clients with genuinely different data shapes, GraphQL eliminates the REST over-fetch/under-fetch problem that would otherwise require either wasteful payloads or duplicated endpoints.

</details>

> 📖 **Theory:** [REST vs GraphQL Design](./13_graphql/graphql_story.md)

---

### Q98 · [Design] · `design-jwt-vs-sessions-mobile`

> **You are building a mobile app where: users stay logged in for 30 days, you need to remotely log out a user (lost device), and you have 5 backend servers behind a load balancer. Would you use JWTs or server-side sessions? Make the case.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Server-side sessions with a centralized store (Redis) — or a hybrid JWT approach with a short-lived access token + revocable refresh token. The remote logout requirement is the deciding constraint.

**How to think through this:**
1. **The decisive constraint: remote logout** — JWTs are self-validating. A 30-day JWT cannot be invalidated before expiry without a server-side blocklist. If a user loses their device, a pure JWT approach means the stolen token is valid for up to 30 days. This is unacceptable.
2. **Why pure JWT fails here** — A 30-day `exp` means 30 days of exposure if the token is stolen. A blocklist fixes this but turns JWTs into sessions with extra steps — you've added the complexity of JWTs while losing the statelessness benefit.
3. **Server-side sessions with Redis** — Store session data in Redis. All 5 servers connect to the same Redis cluster. On "log out lost device": `redis.delete(session_id)`. Effective immediately across all 5 servers. The load balancer constraint is handled: Redis is the shared state, not individual server memory.
4. **The hybrid (best of both worlds)** — Short-lived JWT access tokens (15 minutes, stateless verification) + long-lived refresh tokens stored in Redis (revocable). Remote logout: delete the refresh token from Redis. The access token remains valid for up to 15 minutes — acceptable exposure window. Mobile client transparently refreshes every 15 minutes using the refresh token.
5. **Recommendation** — The hybrid. Short JWT for request-level statelessness (no Redis hit per API call), Redis-backed refresh tokens for 30-day sessions with instant revocation. The 15-minute window is the tradeoff; if instant revocation is required for all requests, use pure sessions.

**Key takeaway:** The remote logout requirement makes pure stateless JWTs unviable — use server-side sessions or a hybrid with short-lived JWTs and revocable refresh tokens in Redis.

</details>

> 📖 **Theory:** [JWT vs Sessions Mobile](./05_authentication/securing_apis.md)

---

### Q99 · [Design] · `design-rate-limiter`

> **Design a rate limiter service that can enforce 1000 requests/minute per API key across 10 horizontally-scaled API servers. Redis is available. Show the data structure and algorithm (sliding window or token bucket — choose one and justify).**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Use the **sliding window log** algorithm backed by Redis sorted sets. Justification: it provides accurate per-minute counts without the burst-at-boundary problem of fixed windows, and Redis sorted sets make it atomic and distributed.

**How to think through this:**
1. **Why not fixed window** — Fixed window (counter per minute bucket) allows 2x the limit at bucket boundaries: 1000 requests at 00:59 + 1000 requests at 01:00 = 2000 requests in a 2-second window. Sliding window eliminates this.
2. **Why sliding window over token bucket here** — Token bucket is better for bursty traffic (you can spend accumulated tokens). For a public API with a per-minute SLA, sliding window gives more intuitive, contractually accurate limits.
3. **Data structure** — Redis sorted set per API key: `ratelimit:{api_key}`. Score = timestamp (unix ms). Member = unique request ID (or timestamp — use timestamp if uniqueness within ms is sufficient).
4. **Algorithm per request:**
```python
import time
import redis
import uuid

r = redis.Redis()

def is_allowed(api_key: str, limit: int = 1000, window_ms: int = 60_000) -> bool:
    key = f"ratelimit:{api_key}"
    now = int(time.time() * 1000)              # current time in ms
    window_start = now - window_ms              # 60 seconds ago

    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, window_start) # ← remove entries older than window
    pipe.zadd(key, {str(uuid.uuid4()): now})    # ← add current request
    pipe.zcard(key)                             # ← count requests in window
    pipe.expire(key, 70)                        # ← TTL slightly longer than window
    results = pipe.execute()

    request_count = results[2]
    return request_count <= limit
```
5. **Why this works across 10 servers** — All servers share the same Redis. The pipeline executes atomically (not fully atomic — use Lua script for strict atomicity). The sorted set always reflects all requests across all servers in the sliding window.
6. **Lua for strict atomicity** — The pipeline above has a small race between `zremrangebyscore` and `zcard`. For strict guarantees, wrap in a Lua script: Redis executes Lua atomically.
7. **Response headers** — Return `X-RateLimit-Limit: 1000`, `X-RateLimit-Remaining: {limit - count}`, `X-RateLimit-Reset: {window_start + window_ms}` on every response.

**Key takeaway:** Sliding window log in a Redis sorted set gives accurate distributed rate limiting across any number of servers — the shared Redis ensures all nodes see the same request count.

</details>

> 📖 **Theory:** [Rate Limiter Design](./09_api_performance_scaling/performance_guide.md)

---

### Q100 · [Design] · `design-api-versioning-system`

> **Design a versioning strategy for a public API used by 500 external companies. You need to: support breaking changes, give clients 12 months to migrate, and maintain two versions simultaneously. Design the strategy end to end: URL scheme, deprecation headers, sunset headers, and migration guide process.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**How to think through this:**

**1. URL Scheme**
Use path-based versioning: `/v1/` and `/v2/`. Reasons: explicit, cacheable at the CDN level, visible in logs, bookmarkable, and universally understood by developers. Header-based versioning (`API-Version: 2`) is elegant but breaks CDN caching and is invisible in browser tools.

```
https://api.example.com/v1/users/{id}   ← stable, deprecated after v2 ships
https://api.example.com/v2/users/{id}   ← new version with breaking changes
```

**2. Versioning Rules**
- **Non-breaking changes** (new optional fields, new endpoints) → deploy to current version without a new version number.
- **Breaking changes** (removed fields, renamed fields, changed types, changed behavior) → require a new version (`v2`, `v3`).
- Maximum two versions live simultaneously. When `v3` ships, `v1` enters sunset. Never support three versions — operational cost is too high.

**3. Deprecation Headers (RFC 9512)**
Add to all `v1` responses the day `v2` ships:
```
Deprecation: true
Link: <https://api.example.com/v2/users/{id}>; rel="successor-version"
```
Clients' HTTP clients and monitoring tools can detect and alert on `Deprecation: true`.

**4. Sunset Headers (RFC 8594)**
Add 12 months before the forced cutoff:
```
Sunset: Tue, 01 Apr 2026 00:00:00 GMT
```
This tells clients the exact date `v1` will stop responding. Tooling like `sunset-header` npm packages can parse this and alert developers automatically.

**5. On Sunset Date**
Return `410 Gone` with a machine-readable body:
```json
{
  "error": "API version deprecated",
  "code": "VERSION_SUNSET",
  "sunset_date": "2026-04-01",
  "migration_guide": "https://docs.example.com/migrate/v1-to-v2",
  "current_version": "https://api.example.com/v2/"
}
```
Never return `404` — `410` signals permanent removal, not a missing resource.

**6. Migration Guide Process**
- Publish a **diff document** at `/docs/changelog/v2` listing every breaking change with before/after examples.
- Provide a **migration checklist** (what each client must change).
- Offer a **compatibility mode** if feasible: a query param `?compat=v1` on v2 endpoints that returns v1-shaped responses for 90 days. Reduces migration friction for large clients.
- Announce via: API dashboard banner, email to all registered API key owners, developer newsletter, in-product warning if you have a portal.

**7. Monitoring**
Track `v1` vs `v2` traffic per API key. Proactively contact companies still on `v1` at 9 months, 11 months, and 2 weeks before sunset. Route this to their registered technical contact, not the billing contact.

**Key takeaway:** Public API versioning is as much a communication and operations problem as a technical one — the URL scheme is the easy part; the deprecation timeline, headers, and proactive client outreach are what determine whether 500 companies successfully migrate.

</details>

> 📖 **Theory:** [Versioning System Design](./08_versioning_standards/versioning_strategy.md)
