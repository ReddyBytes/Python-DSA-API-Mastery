# 🎯 Real-World API Patterns — Interview Preparation

> This file prepares you to discuss real-world API patterns like a working engineer.
> Not just definitions — but real-world usage, trade-offs, and production scenarios.

---

# 🔹 Basic Level Questions (0–2 Years)

**Q1: What is cursor pagination and why is it preferred over offset pagination for large or real-time datasets?**

<details>
<summary>💡 Show Answer</summary>

Offset pagination uses `LIMIT 20 OFFSET 200` to skip to a page. This has two problems: the database must scan and discard the first 200 rows every time (slow at large offsets), and new rows inserted while a user paginates cause items to shift, producing duplicates or skipped entries between pages. Cursor pagination instead uses the last seen item's value (e.g., `WHERE created_at < cursor_time ORDER BY created_at DESC LIMIT 20`) — this is always index-efficient regardless of depth, and unaffected by new inserts. The cursor is typically an opaque base64-encoded string encoding the sort key and item ID. Clients cannot manipulate it, which also prevents parameter tampering.

</details>

<br>

**Q2: What is typed ID prefixing (like `usr_`, `pay_`) and why do APIs like Stripe use it?**

<details>
<summary>💡 Show Answer</summary>

Typed ID prefixes embed the resource type into the ID string itself. Stripe uses `cus_`, `pay_`, `ref_` etc. Benefits: a developer glancing at a log line or database row immediately knows what type of object an ID refers to without looking up the endpoint. It prevents accidental misuse — passing a payment ID to an endpoint expecting a customer ID will immediately look wrong. It simplifies debugging in distributed systems where you see raw IDs in logs. It also reduces API misuse: if you see `usr_` in a payment API response, you know it is a user reference, not a payment. The prefix is typically 3–4 characters followed by an underscore, then a random base62 or base58 string for global uniqueness.

</details>

<br>

**Q3: What is the event envelope pattern used by Stripe and GitHub webhooks?**

<details>
<summary>💡 Show Answer</summary>

The event envelope is a standard wrapper shape for all webhook payloads. Instead of sending the raw resource object, the provider wraps it in a consistent structure containing: a unique event ID (for deduplication), a dot-namespaced event type (`payment.succeeded`, `user.created`), the API version that generated the event, a timestamp, a `data.object` containing the affected resource, and optionally `data.previous_attributes` showing what changed. This consistency means webhook consumers can handle all event types with the same parsing code, deduplicate events using the event ID, and replay events with the correct schema version. Always acknowledge receipt with a fast 200 response and process the event asynchronously — never do slow work in the webhook handler itself.

</details>

<br>

**Q4: How should an API key be stored in a database, and why?**

<details>
<summary>💡 Show Answer</summary>

Never store the raw API key in plain text. On key creation, hash it with SHA-256 and store the hash. The database row contains the hash, the key prefix (e.g., `sk_live_Abc1` — the first 8 characters shown to the user so they can identify which key it is), the scopes, rate limit, and metadata. On each request, hash the incoming key and compare to the stored hash — constant-time comparison with `hmac.compare_digest` to prevent timing attacks. This way, a database breach does not expose any live keys. The original key is shown only once at creation time and never again. This is the same pattern used by GitHub, Stripe, and AWS for access keys.

</details>

<br>

**Q5: What is webhook signature verification and why is timestamp validation important?**

<details>
<summary>💡 Show Answer</summary>

Webhook signature verification proves that the webhook payload was sent by the legitimate provider and not forged by a third party. The provider computes an HMAC-SHA256 signature over the concatenation of a timestamp and the raw request body, using a shared secret. The signature is sent in a header. The consumer recomputes the same HMAC with their secret and compares signatures using constant-time comparison. Timestamp validation prevents replay attacks: an attacker who captures a valid webhook payload cannot replay it later, because the timestamp in the header will be too old. The standard tolerance is 5 minutes — reject any webhook where the timestamp differs from the current time by more than 300 seconds.

</details>

<br>

---

# 🔹 Intermediate Level Questions (2–5 Years)

**Q6: How do you implement API key scoping and what scopes would you define for a multi-tenant e-commerce API?**

<details>
<summary>💡 Show Answer</summary>

API key scoping means each key carries a set of permissions and can only call endpoints within those permissions. Define scopes with a `resource:action` format: `read:orders`, `write:orders`, `read:users`, `write:users`, `admin:billing`. When creating a key, the user selects which scopes to grant. Every endpoint declares which scope is required. The middleware resolves the incoming key, loads its scopes from cache or database, and returns 403 if the required scope is missing. This enables least-privilege access: a read-only reporting integration gets `read:orders` only. A fulfillment system gets `read:orders` and `write:orders`. An analytics pipeline gets read scopes only. No integration ever gets `admin:billing` unless explicitly needed.

</details>

<br>

**Q7: What is the expansion pattern (as used by Stripe) and when should you avoid it?**

<details>
<summary>💡 Show Answer</summary>

The expansion pattern lets clients request related objects to be embedded inline in a response using a query parameter: `GET /payments/pay_xxx?expand=customer`. Without expansion, the response contains only the customer ID (`"customer": "cus_xxx"`). With `?expand=customer`, the full customer object is inlined. This avoids a second request to fetch the customer. Implementation: after fetching the payment, check if `customer` is in the expand list and fetch the customer object if so. Avoid expansion when the related object is always needed — embed it directly in the default response instead. Also avoid deep expansion chains (expand within expand) as they add latency and complexity. Only offer expansion for fields that are sometimes needed, not always.

</details>

<br>

**Q8: How does the `Retry-After` header help clients behave correctly during rate limiting and service unavailability?**

<details>
<summary>💡 Show Answer</summary>

`Retry-After` tells clients exactly how long to wait before retrying, in seconds. Without it, clients must guess: some implement aggressive retries that worsen the problem, others give up unnecessarily. For 429 Too Many Requests, `Retry-After` is the time until the rate limit window resets. For 503 Service Unavailable (planned maintenance or transient overload), it tells clients when the service will be back. Well-behaved SDKs and API clients read this header and implement automatic backoff. When building client SDKs, always read `Retry-After` before applying your own backoff logic — the server knows better than the client how long to wait.

</details>

<br>

**Q9: Walk through cursor pagination for a feed that uses `(created_at, id)` as the cursor. Why are both fields needed?**

<details>
<summary>💡 Show Answer</summary>

Using only `created_at` fails when multiple items have the same timestamp — a common case at high insert rates. If you have 5 posts all created at the same millisecond and your cursor is that timestamp, the query `WHERE created_at < cursor_time` would skip all 5. By including the `id` as a tiebreaker, the cursor becomes `WHERE created_at < cursor_time OR (created_at = cursor_time AND id < cursor_id)` — this uniquely identifies a position in the result set even when timestamps collide. Both fields are encoded together in the opaque cursor string. The query remains efficient because the compound index on `(created_at, id)` covers both the equality and range conditions.

</details>

<br>

**Q10: What is the difference between at-least-once and exactly-once webhook delivery, and how do you handle the former safely?**

<details>
<summary>💡 Show Answer</summary>

At-least-once delivery means the provider will retry until they get a 200 response — if the consumer processes the event but crashes before responding, the event will be delivered again. Exactly-once is very hard to guarantee across distributed systems and most providers (including Stripe) implement at-least-once. To handle it safely, implement idempotent event consumers: before processing an event, check if its event ID has already been processed (stored in a `processed_events` table or Redis set). If yes, return 200 immediately without reprocessing. If no, process and store the event ID atomically. This makes the consumer idempotent: receiving the same event twice has the same effect as receiving it once. Always return 200 quickly and process asynchronously — a slow handler may time out and trigger unnecessary retries.

</details>

<br>

---

# 🔹 Advanced Level Questions (5+ Years)

**Q11: How would you design a webhook delivery system that guarantees at-least-once delivery with exponential backoff and auditability?**

<details>
<summary>💡 Show Answer</summary>

Components: an event log (append-only database table storing every event with its payload, target URL, and delivery status), a delivery worker queue (each delivery attempt is a job), and a retry scheduler. On event creation, write to the event log and enqueue a delivery job. The worker calls the target URL with a timeout. On success (2xx), mark the delivery as succeeded. On failure (non-2xx, timeout, connection error), schedule a retry with exponential backoff: 30s, 2m, 10m, 1h, 6h, 24h, then mark as permanently failed after the final retry. Store every attempt with its response code and body in a `webhook_deliveries` table — expose this to customers in a developer dashboard so they can debug failures. Allow customers to manually replay any event from the log. Alert on sustained delivery failures to a customer endpoint. Use message signing (HMAC) on all deliveries so customers can verify origin.

</details>

<br>

**Q12: How do you design a public API that supports both simple clients and power users who need fine-grained field control, without maintaining two separate endpoints?**

<details>
<summary>💡 Show Answer</summary>

Use a combination of the expansion pattern and field masks. The default response returns a curated set of fields adequate for most use cases — not everything, but the common fields. Power users can request specific fields with `?fields=id,email,orders.id,orders.total` (field mask) — this reduces payload size for clients that only need a subset. They can also request related objects with `?expand=orders,customer` — this prevents N+1 request patterns. Implementation: parse the `fields` parameter into a set, then filter the serialized response to only include requested paths. Parse `expand` into a set of relation names, fetch them, and embed them. Both parameters can be combined. This is the approach used by LinkedIn's API and Facebook Graph API. Document the default field set clearly — fields added to the default set are a non-breaking change, fields removed from it are breaking.

</details>

<br>

**Q13: A large customer reports that their integration is making 5,000 requests per minute to your API but the rate limit is 1,000. How do you handle this conversation and what do you build?**

<details>
<summary>💡 Show Answer</summary>

First, diagnose: is this a misconfigured client (retrying on every response, not reading Retry-After), a legitimate usage growth, or a code bug (infinite loop). Check the request logs for the request distribution — are they all the same endpoint, same parameters, evenly spread or bursty? If legitimate growth, the solution is a combination of: offering a bulk endpoint that replaces N individual calls with one (e.g., GET /users/bulk?ids=1,2,3 instead of N individual GETs), offering webhooks so they can receive push notifications instead of polling, reviewing their integration pattern for N+1 request bugs (fetching related objects in a loop), and potentially offering a higher-tier rate limit. Also ensure your SDK implements proper retry logic with exponential backoff and respects Retry-After. Finally, add rate limit analytics to your developer dashboard so customers can see their usage patterns before hitting limits.

</details>

<br>

**Q14: How would you version a production API when a breaking change is unavoidable, ensuring no consumer breaks?**

<details>
<summary>💡 Show Answer</summary>

A breaking change must never silently change behavior for existing consumers. The approach: deploy v2 alongside v1, never remove v1 immediately. Announce the change with a deprecation notice in the API response via a `Deprecation` header (RFC 8594) and a `Sunset` header indicating the removal date — give at least 6 months. In v1 responses, log which consumers are still using deprecated endpoints so you can proactively contact them. Provide a migration guide with before/after examples. For the API gateway, route `/v1/*` to the v1 codebase and `/v2/*` to v2 — both run simultaneously. Once traffic to v1 drops to near zero (or the sunset date passes), return 410 Gone from v1 endpoints with a helpful error message and migration link rather than 404. Never make a breaking change in the same version — always bump the major version.

</details>

<br>
