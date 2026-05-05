# 🎯 API Design Patterns — Interview Preparation

> This file prepares you to discuss API design patterns like a working engineer.
> Not just definitions — but real-world usage, trade-offs, and production scenarios.

---

# 🔹 Basic Level Questions (0–2 Years)

**Q1: What is an idempotency key and why is it required for payment APIs?**

<details>
<summary>💡 Show Answer</summary>

An idempotency key is a client-generated UUID included in a request header (typically `Idempotency-Key`) that lets the server detect and deduplicate retried requests. Without it, a network timeout on a POST /payments request leaves the client uncertain whether the charge succeeded — retrying without a key risks double-charging the customer. With a key, the server stores the result keyed to that UUID and returns the cached result on retry without processing again. Stripe requires idempotency keys for all POST requests. The key should be scoped to the customer (not globally unique) and have a 24-hour TTL, which is Stripe's convention.

</details>

<br>

**Q2: What is the difference between PATCH and PUT, and when should you use each?**

<details>
<summary>💡 Show Answer</summary>

PUT replaces the entire resource with the payload you send — fields you omit are deleted or set to their defaults. PATCH applies a partial update — only the fields you include are changed, and omitted fields are left as-is. In practice: use PUT when the client always sends the complete representation of the resource (e.g., a settings page that overwrites all settings at once). Use PATCH when clients need to update individual fields without re-sending everything (e.g., updating just a user's name). The most common PATCH implementation is merge patch (RFC 7396): send only the fields you want to change, and send null to delete a field.

</details>

<br>

**Q3: What does a 202 Accepted response mean, and what should the response body contain?**

<details>
<summary>💡 Show Answer</summary>

202 Accepted means the server received the request and will process it asynchronously — the result is not yet available. The response body should contain a job ID and a status URL where the client can poll for progress. The `Location` header should point to the polling endpoint. Example: a report generation request returns 202 with `{"job_id": "abc123", "status": "pending"}` and `Location: /jobs/abc123`. The client polls `/jobs/abc123` which returns `{"status": "running", "progress": 42}` until it becomes `{"status": "succeeded", "result_url": "/reports/abc123"}`. Use 202 for any operation that takes more than 1–2 seconds to complete.

</details>

<br>

**Q4: What is the difference between polling, webhooks, and SSE for receiving asynchronous results?**

<details>
<summary>💡 Show Answer</summary>

Polling: the client repeatedly calls a status endpoint on a timer. Simple to implement, but wastes requests and has latency equal to the poll interval.

Webhooks: the server calls a URL on the client's server when the result is ready. Very low latency and no wasted requests, but the client must expose a public HTTP endpoint, handle retries, and verify signatures.

SSE (Server-Sent Events): the client opens one persistent HTTP connection and the server pushes events over it. Low latency, browser-native, auto-reconnects. One-directional (server to client only). Best for browser clients receiving progress updates or live feeds.

Choice: webhooks for server-to-server async events; SSE for browser real-time updates; polling for simple job status checks or when webhook setup is not feasible.

</details>

<br>

**Q5: What is the 207 Multi-Status response code and when is it used?**

<details>
<summary>💡 Show Answer</summary>

207 Multi-Status is returned by a batch endpoint when the batch was processed but individual items within it had mixed results — some succeeded, some failed. Rather than returning 200 (which implies everything worked) or 400/500 (which implies the whole request failed), 207 signals that the caller must inspect per-item results. The response body contains an array of result objects, each with its own `status` (e.g., "sent", "failed") and any error details. Use 207 when partial success is acceptable and you want to return as much as succeeded rather than aborting on first error.

</details>

<br>

---

# 🔹 Intermediate Level Questions (2–5 Years)

**Q6: How does the ETag / If-Match pattern prevent lost updates in a concurrent API?**

<details>
<summary>💡 Show Answer</summary>

The lost update problem: two clients read the same resource, both make changes, and the second write silently overwrites the first. ETags prevent this. When the client GETs a resource, the server includes an `ETag` header containing a hash of the current resource state. When the client sends a PUT or PATCH, it includes `If-Match: "etag_value"`. The server recomputes the hash of the current resource — if it no longer matches, another client has modified it, and the server returns 412 Precondition Failed. The client must re-fetch and re-apply their change. This is optimistic concurrency control: no locks, no blocking, but conflicts are detected. Use it for collaborative editing, cached resource updates, or any resource with concurrent writers.

</details>

<br>

**Q7: You have a bulk email send endpoint. Should it return 200 or 207 if 3 out of 10 emails fail, and why?**

<details>
<summary>💡 Show Answer</summary>

Return 207 Multi-Status. Returning 200 is misleading — it implies all 10 succeeded. Returning 400 or 500 is also wrong — the 7 successful sends were real successes that should not be retried. 207 is the correct signal: the HTTP layer processed the batch, but callers must inspect the per-item results. The response body should include an array of 10 objects, each with the original item identifier, a `status` of "sent" or "failed", and an error detail for failed items. This lets the caller build a retry set from only the failed items without re-sending the successful ones. Document this behavior clearly in your API — many consumers expect a simple 200/400 contract and will need to handle 207 explicitly.

</details>

<br>

**Q8: What are the three common PATCH semantics (merge patch, JSON Patch, field mask) and when would you choose each?**

<details>
<summary>💡 Show Answer</summary>

Merge patch (RFC 7396): send only changed fields; null deletes a field. Simplest for clients — just send what changed. Works well for flat objects but has an ambiguity problem: you cannot distinguish "field not provided" from "field set to null" when null has business meaning. Most REST APIs use this.

JSON Patch (RFC 6902): explicit list of operations (add, remove, replace, move, copy, test). Verbose but unambiguous — every change is spelled out. Good for complex nested updates or when you need atomic test-then-update semantics. Content-Type is `application/json-patch+json`.

Field mask (Google AIP): send the full object plus an `update_mask` listing which fields to apply. Avoids the null ambiguity of merge patch while being more readable than JSON Patch. Used by Google APIs (Firestore, Cloud Tasks). Use in teams already following Google AIP style.

</details>

<br>

**Q9: How do you implement idempotency key storage safely to prevent race conditions on concurrent retries?**

<details>
<summary>💡 Show Answer</summary>

The naive approach (check if key exists, then process) has a TOCTOU race: two concurrent requests with the same key both check before either has stored the result. The safe approach uses a Redis SET with NX (only set if not exists) as an atomic lock: `redis.set(key, '{"status":"processing"}', nx=True, ex=86400)`. If the lock is not acquired, return 409 — a request with this key is already in flight. Once processing completes, overwrite the processing marker with the actual result. On failure, delete the key so the client can retry. The key is also scoped to the customer ID to prevent cross-customer replay attacks. Never store the idempotency key alone — always store it with a hash of the request payload so you can detect a key being reused with a different payload and return 422.

</details>

<br>

**Q10: Walk through the 202 + polling pattern for a long-running report generation job. What status codes are returned at each step?**

<details>
<summary>💡 Show Answer</summary>

Step 1 — client POST /reports: server accepts the request, creates a job record with status "pending", starts async processing in the background, returns 202 with `{"job_id": "abc123"}` and `Location: /jobs/abc123` header.

Step 2 — client polls GET /jobs/abc123 while running: returns 200 with `{"status": "running", "progress": 55}`. Always 200 from the polling endpoint — the job existing is a successful GET.

Step 3 — on completion: returns 200 with `{"status": "succeeded", "result_url": "/reports/abc123"}` and a `Location: /reports/abc123` header pointing to the result.

Step 4 — on failure: returns 200 with `{"status": "failed", "error": "Out of memory processing large dataset"}`. Still 200 — the job resource itself was retrieved successfully; the error is application-level inside the body.

Step 5 — client fetches result: GET /reports/abc123 returns 200 with the actual report data.

</details>

<br>

---

# 🔹 Advanced Level Questions (5+ Years)

**Q11: How would you design an idempotent API for a distributed payment system where the downstream payment processor also requires idempotency?**

<details>
<summary>💡 Show Answer</summary>

The key insight is that idempotency must be end-to-end, not just at your API layer. Your API deduplicates requests from clients. But if you receive a deduplicated request and need to call the payment processor (e.g., Stripe), you must pass the same idempotency key to Stripe so Stripe also deduplicates at their end. This handles the failure case where your API called Stripe, Stripe processed the charge, but your API crashed before storing the result — on retry, your API passes the same key to Stripe and gets the original result back without double-charging. Store the Stripe charge ID alongside the idempotency result so you have a complete audit trail. Also store a hash of the request payload with the key — if a client reuses a key with a different payload (a client bug), return 422 Unprocessable Entity rather than silently processing or rejecting.

</details>

<br>

**Q12: What are the failure modes of the webhook delivery pattern and how does a production webhook system handle them?**

<details>
<summary>💡 Show Answer</summary>

Failure modes: the client endpoint is temporarily down (5xx), the endpoint returns 200 but was too slow (timeout), the network drops the connection, or the client processed the event but the acknowledgment was lost (so the server retries an already-processed event).

Production handling: use an exponential backoff retry queue — retry after 30s, 5m, 30m, 2h, 24h before marking the delivery as failed. Store every delivery attempt with its response code in an audit log accessible via the developer dashboard. Require HTTPS endpoints with valid certificates — reject HTTP. Include an event ID in the envelope and document that deliveries are at-least-once — consumers must implement deduplication using the event ID. Include a `Webhook-Signature` header (HMAC-SHA256 of timestamp + body) so consumers can verify authenticity and reject replays older than 5 minutes. Allow consumers to disable endpoints temporarily and replay missed events from a log.

</details>

<br>

**Q13: How would you design the pagination strategy for a real-time social feed API that receives hundreds of new posts per second?**

<details>
<summary>💡 Show Answer</summary>

Offset pagination fails immediately: `OFFSET 1000` requires scanning 1000 rows, and new posts arriving during pagination cause items to shift, resulting in duplicates or skipped entries between pages. Use cursor pagination keyed on `(created_at, id)`. The cursor encodes the `created_at` timestamp and `id` of the last seen item as an opaque base64 string. Each page query uses `WHERE created_at < cursor_time OR (created_at = cursor_time AND id < cursor_id) ORDER BY created_at DESC, id DESC LIMIT N+1` — always index-efficient regardless of how deep into the feed the user is, and unaffected by new posts arriving at the top. Fetch N+1 items to detect if more pages exist without a separate COUNT query. For feeds requiring stable pages (no items shifting between fetches), snapshot the feed into a user-specific timeline table on write fanout rather than reading the global posts table directly.

</details>

<br>

**Q14: When would you combine the 202 + polling pattern with SSE rather than polling, and what changes in the implementation?**

<details>
<summary>💡 Show Answer</summary>

Use SSE instead of polling when: the operation has meaningful intermediate progress to report (e.g., a multi-stage ETL pipeline), you want to reduce client-side polling overhead for a browser-based UI, or you need sub-second progress updates that polling cannot efficiently provide. The change: the POST /jobs endpoint still returns 202 with a job ID. But instead of a polling endpoint, you expose GET /jobs/{id}/stream with `Content-Type: text/event-stream`. The server holds the connection open and writes `data:` lines as progress updates arrive. On completion, write a final event and close the connection. The client uses the EventSource API (browser) or an SSE library. Implementation gotcha: your web server must not buffer SSE responses — disable response buffering (e.g., `X-Accel-Buffering: no` for Nginx). Also handle reconnects: SSE has a built-in `Last-Event-ID` mechanism that lets clients resume from the last received event after a disconnect.

</details>

<br>
