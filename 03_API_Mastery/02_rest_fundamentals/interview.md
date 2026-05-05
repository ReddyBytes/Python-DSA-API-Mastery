# 🎯 REST Fundamentals — Interview Preparation

> This file prepares you to discuss REST like a working engineer.
> Not just definitions — but real-world usage, trade-offs, and production scenarios.

---

# 🔹 Basic Level Questions (0–2 Years)

**Q1: What are the 6 REST constraints?**

<details>
<summary>💡 Show Answer</summary>

The 6 constraints defined by Roy Fielding are: (1) Client-Server — client and server are separate and develop independently. (2) Stateless — every request contains all information needed; no session stored on the server. (3) Cacheable — responses declare whether they can be cached. (4) Uniform Interface — consistent, predictable resource design. (5) Layered System — a client can't tell if it's talking to a CDN, load balancer, or origin server. (6) Code on Demand (optional) — server can send executable code like JavaScript.

In practice, constraints 1, 2, and 4 matter most. Statelessness is the one that most directly affects architecture decisions.

</details>

<br>

**Q2: What does "stateless" mean in REST and why does it matter?**

<details>
<summary>💡 Show Answer</summary>

Stateless means the server stores no client session state between requests. Every request must include everything the server needs to process it — including auth credentials (usually a Bearer token). The server does not remember "Alice logged in 5 minutes ago."

This matters because it enables horizontal scaling. Any server in a cluster can handle any request — you can add servers freely without sticky session routing. Stateful APIs require load balancer affinity (all of Alice's requests go to the same server), which breaks under server failure and limits scaling options.

</details>

<br>

**Q3: What is wrong with this URL design: `POST /getUserOrders?userId=42`?**

<details>
<summary>💡 Show Answer</summary>

Three problems: (1) It uses a verb (`getUser`) in the URL — REST URLs should be nouns identifying resources. The HTTP method is the verb. (2) It uses POST instead of GET for a read operation — POST implies creating something, not reading. (3) The resource hierarchy is wrong — orders belong to a user, so the URL should express that with nesting.

The correct REST URL is `GET /users/42/orders`. If you want a specific order: `GET /users/42/orders/7`.

</details>

<br>

**Q4: What is the difference between PUT and PATCH?**

<details>
<summary>💡 Show Answer</summary>

PUT is a full replacement — you send the entire resource and the server replaces what's stored. If you omit a field in a PUT request, that field gets cleared or nulled out. PUT is idempotent.

PATCH is a partial update — you send only the fields you want to change, and the server merges them. This is safer when a resource has many fields, because you don't risk accidentally clearing fields you didn't intend to touch.

Production gotcha: some teams use PATCH for everything because it's safer, even when REST purists prefer PUT for full replacements.

</details>

<br>

**Q5: How should you design URLs for filtering and sorting?**

<details>
<summary>💡 Show Answer</summary>

Filters and sort options belong in query parameters, not in the URL path. Good: `GET /orders?status=pending&sort=created_at&order=desc`. Bad: `GET /orders/pending/sorted-by-date`.

Why: URL paths identify resources. Query params modify how you retrieve them. Embedding filters in paths creates an explosion of endpoint combinations, breaks REST semantics, and makes the API unmaintainable. Query params also compose naturally — you can combine any filter with any sort without creating new routes.

</details>

<br>

---

# 🔹 Intermediate Level Questions (2–5 Years)

**Q6: Explain idempotency and why it matters for distributed systems.**

<details>
<summary>💡 Show Answer</summary>

Idempotency means performing an operation N times has the same effect as performing it once. GET, PUT, and DELETE are idempotent. POST is not.

In distributed systems, networks are unreliable — requests time out, connections drop, retries happen. If a client retries a non-idempotent operation (POST to create a payment), it creates a duplicate. Idempotent operations are safe to retry blindly.

To make POST idempotent, use idempotency keys: the client generates a UUID, includes it as `Idempotency-Key: <uuid>` in the header, and the server stores the result keyed by that UUID. On retry, the server returns the stored result instead of processing again. Stripe, Braintree, and most payment APIs require this.

</details>

<br>

**Q7: What is HATEOAS and is it used in practice?**

<details>
<summary>💡 Show Answer</summary>

HATEOAS (Hypermedia as the Engine of Application State) is REST constraint #4 taken to its fullest — API responses include links to available next actions, so clients discover capabilities at runtime rather than hardcoding URLs.

In theory: a response to GET /users/42 would include `_links` for `self`, `orders`, `deactivate`, etc. Clients follow links instead of constructing URLs.

In practice: almost no production APIs implement HATEOAS. The tooling overhead is high and most client developers find it confusing. Pagination links (`next`, `prev`, `first`, `last`) are the most common partial implementation you'll actually see. Know the concept for interviews, but don't over-engineer around it.

</details>

<br>

**Q8: What is the difference between offset pagination and cursor pagination? When do you use each?**

<details>
<summary>💡 Show Answer</summary>

Offset pagination uses `?page=2&limit=20`. Easy to implement and supports jumping to arbitrary pages. Problem: if rows are added or deleted between page requests, pages shift — you get duplicates or skip records. Works fine for admin UIs and reports where data changes slowly.

Cursor pagination uses an opaque cursor token (usually a base64-encoded ID or composite key). You get the next page by passing the cursor from the previous response. There's no concept of "page 5" — you can only go forward/backward from where you are. Stable under concurrent inserts. Required for feeds, timelines, and any dataset over 100k rows where live inserts are common (Twitter-style timelines, activity feeds).

</details>

<br>

**Q9: How do caching headers work in a REST API and what is the 304 response?**

<details>
<summary>💡 Show Answer</summary>

The server returns an `ETag` header with each response — a hash or version identifier of the response content. The client stores the ETag alongside the cached response. On the next request for the same resource, the client sends `If-None-Match: <etag>`. If the content hasn't changed, the server returns 304 Not Modified with no body — the client uses the cached copy. This saves bandwidth and reduces backend load significantly for read-heavy APIs.

`Cache-Control` handles time-based caching: `max-age=3600` tells caches to reuse the response for 1 hour without checking. `public` allows CDN caching. `private` means only the browser may cache (not shared caches). `no-store` prevents all caching — use for auth and financial endpoints.

</details>

<br>

**Q10: What is a "layered system" in REST and what are examples of layers a request passes through?**

<details>
<summary>💡 Show Answer</summary>

A layered system means clients cannot tell whether they are talking directly to the origin server or an intermediary. This enables transparent infrastructure composition.

In practice, a request from a browser might pass through: a CDN (Cloudflare, CloudFront) that handles caching and DDoS protection, a load balancer that distributes traffic, an API gateway that handles auth, rate limiting, and routing, and finally the application server. The client code doesn't know or care about any of these layers. This is why statelessness is so important — it makes every layer independently scalable and replaceable.

</details>

<br>

---

# 🔹 Advanced Level Questions (5+ Years)

**Q11: When would you break REST conventions (use verbs in URLs) and how do you handle "actions" in REST?**

<details>
<summary>💡 Show Answer</summary>

Some operations don't map cleanly to CRUD on a single resource. Sending an invoice, deactivating a user, or triggering a payment retry are actions, not resource replacements.

The accepted pattern is `POST /resource/{id}/action` — for example, `POST /invoices/9/send`, `POST /users/42/deactivate`, `POST /payments/15/retry`. The POST method signals a non-idempotent state change. This is widely accepted and even endorsed by API design guides at Stripe and Google.

Avoid creating a fake noun to force CRUD semantics — `POST /invoice-dispatch` is less clear than `POST /invoices/9/send`. Clarity for the consumer is more important than strict REST purity.

</details>

<br>

**Q12: How does the stateless constraint affect authentication design in a microservices system?**

<details>
<summary>💡 Show Answer</summary>

Statelessness means no server-side sessions. Authentication state must travel with every request. JWTs handle this well — the token is self-contained (user ID, roles, expiry are in the payload) and any service can verify it with the public key or shared secret without calling a central auth database.

In microservices, the auth service issues JWTs. Downstream services validate the token locally — no inter-service call needed for auth on every request. This is why RS256 (asymmetric) is preferred over HS256 in microservices: the auth service holds the private key, all other services hold only the public key for verification. If a downstream service only has the public key, it can verify tokens but cannot forge new ones.

</details>

<br>

**Q13: A team proposes returning `200 OK` with `{"success": false, "error": "not found"}` for all responses to avoid clients handling different status codes. How do you respond?**

<details>
<summary>💡 Show Answer</summary>

This is an anti-pattern called "200 Everything." It breaks HTTP semantics that the entire ecosystem (CDNs, proxies, monitoring, load balancers, APM tools) relies on. A CDN will cache a 200 response and serve the error to every subsequent client. Monitoring tools counting 2xx rates will show 100% success when half your calls are failing. curl, httpie, and testing tools check status codes to signal failure.

The fix is to use correct HTTP status codes (404, 400, 401, 500) and put a machine-readable error code in the body for clients that need to handle specific cases: `{"error": {"code": "NOT_FOUND", "message": "..."}}`. This gives both machine-readability and HTTP compliance. Clients that want to switch on error type use the `code` field; infrastructure uses the HTTP status code.

</details>

<br>

**Q14: What are the trade-offs between deep URL nesting vs flat URLs with query parameters?**

<details>
<summary>💡 Show Answer</summary>

Deep nesting (`/users/42/orders/7/items/3/reviews`) creates tight coupling between resource hierarchy and URL structure. Beyond 2 levels it becomes unwieldy and implies clients must traverse the hierarchy to get a leaf resource. It also makes the API fragile — moving a resource in the hierarchy breaks all existing URLs.

Flat URLs with query params (`/reviews?item_id=3&order_id=7`) decouple the resource from ownership. It's easier to support multiple access patterns (get all reviews for an item, all reviews by a user) without creating multiple deep paths.

The pragmatic rule: max 2 levels of nesting for natural ownership (`/users/42/orders`). For deeper relationships, use flat collection endpoints with filtering (`/order-items?order_id=7`). Resources like reviews that have multiple natural parents are especially good candidates for flat endpoints.

</details>

<br>
