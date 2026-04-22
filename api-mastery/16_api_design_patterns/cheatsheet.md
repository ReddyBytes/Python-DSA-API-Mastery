# ⚡ Cheatsheet: API Design Patterns

---

## Learning Priority

**Must Learn** — core patterns every backend engineer needs:
Idempotency keys · 202 + polling pattern · PATCH semantics

**Should Learn** — appear in system design and API design interviews:
Polling vs webhook vs SSE comparison · bulk operations pattern · long-running operations

**Good to Know** — useful for advanced API work:
Conditional requests (ETag/If-Match) · partial response (field masks) · compound documents

**Reference** — look up when needed:
JSON:API spec · Google AIP (API Improvement Proposals) · OpenAPI extensions

---

## Idempotency Key Pattern

```
Problem: client sends payment request → network timeout →
         client doesn't know if it succeeded → unsafe to retry without idempotency

Solution: client generates a UUID per operation attempt, includes it as a header.
          Server stores (key → result). Retries return the stored result.
```

```python
# Client sends
POST /payments
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{"amount": 5000, "currency": "usd", "method": "card_xxx"}

# Server logic
async def process_payment(idempotency_key: str, payload: dict):
    # Check if already processed
    cached = await redis.get(f"idem:{idempotency_key}")
    if cached:
        return json.loads(cached)  # return stored result, do not reprocess

    # Mark as in-flight (prevent concurrent duplicates)
    acquired = await redis.set(
        f"idem:{idempotency_key}", '{"status":"processing"}',
        nx=True, ex=86400  # 24 hour TTL, NX = only set if not exists
    )
    if not acquired:
        raise HTTPException(409, "Request with this idempotency key is being processed")

    # Process the payment
    result = await charge_card(payload)

    # Store result (overwrite in-flight marker)
    await redis.set(f"idem:{idempotency_key}", json.dumps(result), ex=86400)
    return result
```

**Rules:**
- Key is client-generated (UUID), not server-generated
- Scope key to customer/API key — not globally unique across all customers
- TTL: 24 hours is Stripe's standard
- Return `409 Conflict` if same key is still in-flight
- Applies to: payments, order placement, email sends, any non-idempotent operation

---

## Polling vs Webhook vs SSE Comparison

| Dimension | Short Polling | Long Polling | Webhooks | SSE |
|-----------|--------------|-------------|----------|-----|
| Direction | Client pulls | Client pulls (held) | Server pushes | Server pushes |
| Connection | New HTTP per poll | HTTP held open | New HTTP per event | Persistent HTTP |
| Latency | High (poll interval) | Low | Very low | Very low |
| Server load | High (constant polls) | Medium | Low | Medium |
| Client simplicity | Simple | Simple | Complex (needs endpoint) | Simple |
| Firewall friendly | Yes | Yes | Requires open endpoint | Yes |
| Retry handling | Client responsibility | Client responsibility | Must implement | Auto-reconnect |
| State | Stateless | Stateless | Stateless | Stateful (conn) |
| Best for | Simple status checks | Job completion | Async events to servers | Browser real-time |

```python
# Short polling — client polls every N seconds
GET /jobs/abc123
Response: {"status": "running", "progress": 42}

# Long polling — server holds the connection open until there's an update
GET /jobs/abc123/wait?timeout=30

# Webhook — server calls client's URL when done
POST https://client.example.com/webhooks/job-complete
{"job_id": "abc123", "status": "succeeded", "result_url": "..."}

# SSE — server streams events over a persistent HTTP connection
GET /jobs/abc123/stream
Content-Type: text/event-stream

data: {"status": "running", "progress": 42}
data: {"status": "running", "progress": 87}
data: {"status": "succeeded", "result_url": "/results/abc123"}
```

---

## Partial Update (PATCH) Pattern

```python
# Three approaches to PATCH semantics

# 1. Merge patch (RFC 7396) — most common
# Send only the fields you want to change. Null = delete the field.
PATCH /users/42
{"name": "Alice", "bio": null}
# Result: name updated, bio deleted, all other fields unchanged

# 2. JSON Patch (RFC 6902) — explicit operations
PATCH /users/42
Content-Type: application/json-patch+json
[
  {"op": "replace", "path": "/name", "value": "Alice"},
  {"op": "remove", "path": "/bio"},
  {"op": "add", "path": "/tags/-", "value": "premium"}
]

# 3. Field mask (Google AIP style) — explicit list of fields to update
PATCH /users/42
{"name": "Alice", "update_mask": "name,settings.theme"}
# Only fields listed in update_mask are written; others ignored

# FastAPI implementation — merge patch
from typing import Optional
from pydantic import BaseModel

class UserUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[str] = None

@app.patch("/users/{user_id}")
async def update_user(user_id: int, update: UserUpdate):
    # Only update fields that were explicitly provided
    update_data = update.model_dump(exclude_unset=True)  # exclude fields not in request
    if not update_data:
        raise HTTPException(400, "No fields to update")
    await db.update("users", update_data, where={"id": user_id})
    return await db.get("users", user_id)
```

---

## Long-Running Operation Pattern (202 + Location)

```python
# Pattern: accept the request immediately, return a job to poll

# Step 1 — accept the request
@app.post("/reports", status_code=202)
async def create_report(request: ReportRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid4())
    await db.create_job(job_id, status="pending", request=request.dict())
    background_tasks.add_task(generate_report, job_id, request)

    return JSONResponse(
        status_code=202,
        content={"job_id": job_id, "status": "pending"},
        headers={"Location": f"/jobs/{job_id}"}  # where to poll
    )

# Step 2 — client polls
@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    job = await db.get_job(job_id)
    if not job:
        raise HTTPException(404)

    response = {
        "id": job_id,
        "status": job["status"],   # pending → running → succeeded → failed
        "progress": job.get("progress"),
        "created_at": job["created_at"],
    }
    if job["status"] == "succeeded":
        response["result_url"] = f"/reports/{job['result_id']}"
        return JSONResponse(response, headers={"Location": response["result_url"]})
    if job["status"] == "failed":
        response["error"] = job.get("error_message")

    return response
```

**Status code pattern:**
- `202 Accepted` — request accepted, processing async
- `Location` header — where to poll for status
- Final `200 OK` from job status endpoint — include `Location` to result when done
- `303 See Other` — redirect directly to result (alternative for simple cases)

---

## Bulk Operations Pattern

```python
# Pattern 1: Batch endpoint — single atomic operation
@app.post("/users/batch", status_code=200)
async def batch_create_users(users: list[UserCreate]):
    if len(users) > 100:
        raise HTTPException(400, "Batch size limited to 100")
    results = await db.bulk_insert("users", [u.dict() for u in users])
    return {"created": len(results), "ids": [r["id"] for r in results]}

# Pattern 2: Mixed-result batch — returns per-item status
@app.post("/emails/batch-send")
async def batch_send(requests: list[EmailRequest]):
    results = []
    for req in requests:
        try:
            msg_id = await email_service.send(req)
            results.append({"id": req.id, "status": "sent", "message_id": msg_id})
        except Exception as e:
            results.append({"id": req.id, "status": "failed", "error": str(e)})
    # Return 200 even if some failed — check per-item status
    all_ok = all(r["status"] == "sent" for r in results)
    return JSONResponse(
        status_code=200 if all_ok else 207,  # 207 Multi-Status
        content={"results": results}
    )

# Pattern 3: Async bulk — for large operations
@app.post("/users/import", status_code=202)
async def import_users(file: UploadFile):
    job_id = str(uuid4())
    data = await file.read()
    await queue.enqueue("import_users", job_id=job_id, data=data)
    return {"job_id": job_id, "status_url": f"/jobs/{job_id}"}
```

---

## Conditional Requests (Optimistic Concurrency)

```python
# ETag + If-Match pattern — prevents lost updates

# GET returns ETag
@app.get("/users/{user_id}")
async def get_user(user_id: int, response: Response):
    user = await db.get("users", user_id)
    etag = hashlib.md5(json.dumps(user).encode()).hexdigest()
    response.headers["ETag"] = f'"{etag}"'
    return user

# PUT/PATCH requires If-Match
@app.put("/users/{user_id}")
async def update_user(
    user_id: int,
    update: UserUpdate,
    if_match: str = Header(None)
):
    if not if_match:
        raise HTTPException(428, "Precondition Required — include If-Match header")

    current = await db.get("users", user_id)
    current_etag = f'"{hashlib.md5(json.dumps(current).encode()).hexdigest()}"'

    if if_match != current_etag:
        raise HTTPException(412, "Precondition Failed — resource was modified")

    return await db.update("users", update.dict(exclude_unset=True), where={"id": user_id})
```

---

## When to Use / Avoid

| Pattern | Use When | Avoid When |
|---------|----------|------------|
| Idempotency keys | Non-idempotent ops clients may retry (payments, orders) | GET/DELETE (already safe/idempotent) |
| Webhooks | Server needs to push events to external clients | Browser clients (no open port) — use SSE |
| SSE | Browser real-time updates, one-way stream | Bidirectional real-time — use WebSocket |
| Long polling | Job status with infrequent updates | High-frequency updates (SSE is better) |
| 202 + polling | Operations > 1–2 seconds | Fast operations — just return 200/201 |
| PATCH merge | Partial resource updates | Replacing entire resource — use PUT |
| Bulk endpoint | Clients need to create/update many records | Arbitrary combinations — separate calls |
| ETag / If-Match | Collaborative editing, cached resource updates | Internal APIs with no concurrency concerns |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← API Gateway](../15_api_gateway/cheatsheet.md) &nbsp;|&nbsp; **Next:** [WebSockets →](../17_websockets/cheatsheet.md)

**Related Topics:** [REST Best Practices](../03_rest_best_practices/) · [Real-World APIs](../18_real_world_apis/) · [WebSockets](../17_websockets/)
