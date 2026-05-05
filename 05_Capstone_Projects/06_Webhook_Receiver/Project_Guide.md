# Project 06 — Webhook Receiver

> A webhook is a reverse API call — instead of your app asking "did anything happen?", the other service taps you on the shoulder the moment it does. Like a doorbell vs constantly checking if someone's at the door. The hard part isn't receiving the message — it's trusting it came from who it claims.

This is a fully guided project. Every step walks you through the concept, gives you time to think, then shows you exactly how to do it.

---

## What You're Building

A **FastAPI** webhook receiver that handles real-world webhook patterns used by GitHub and Stripe:

- `POST /webhook/github` — receives GitHub push event payloads, verifies HMAC signature
- `POST /webhook/stripe` — receives Stripe payment events, verifies Stripe signature
- `GET /events` — returns the last 10 received events
- Structured logging for every received event
- Idempotency: duplicate events are detected and ignored

```
                        POST /webhook/github
GitHub ─────────────────────────────────────────►  verify HMAC sig
                        X-Hub-Signature-256                │
                                                           │ ✓
                                                     parse payload
                                                           │
                                                     store in deque
                                                           │
                                                     return 200 OK
                                                           │
Stripe ─────────────────────────────────────────►  verify Stripe sig
                        POST /webhook/stripe               │
                        Stripe-Signature                   │ ✓
                                                     check idempotency
                                                           │
                                                     log + store
                                                           │
Client ─────────────────────────────────────────►  GET /events
                                                     return last 10
```

---

## What You Need Installed

```bash
pip install fastapi uvicorn python-dotenv
```

```bash
# Folder structure you'll build
webhook_receiver/
├── .env
├── main.py
├── security.py
├── models.py
└── storage.py
```

---

## Step 1 — What Is a Webhook?

Before writing a single line of code, understand what you're building and why.

**Push vs Pull:**

Most APIs are **pull** — your app asks the server "did anything change?" on a schedule. This wastes requests when nothing happened and adds latency when something did.

A **webhook** is **push** — the remote service calls *your* server the moment an event occurs. You register a URL ("call me here"), and they POST to it immediately.

**What a webhook receiver must do:**

1. **Receive** — accept the HTTP POST, read the raw body
2. **Verify** — prove the request came from the real sender, not an impersonator
3. **Parse** — extract the structured event data
4. **Act** — do something (log it, queue a job, update a DB)
5. **Respond fast** — return 200 quickly; do heavy work asynchronously

**Why verification matters:** Anyone on the internet can POST to your endpoint. Without signature verification, an attacker could fake a "payment succeeded" event and trigger your fulfillment logic for free.

**Real-world examples:**

| Service | Event | Your action |
|---------|-------|-------------|
| GitHub | Push to main | Trigger CI/CD pipeline |
| Stripe | `payment_intent.succeeded` | Fulfill the order |
| Slack | User sends message | Bot responds |
| Shopify | Order created | Send confirmation email |

No code in this step — make sure the mental model is clear before moving on.

---

## Step 2 — Project Setup

Think about it: what do you need before writing any route handlers?

- A FastAPI app instance
- A way to load secrets without hardcoding them (never put secrets in source code)
- A `.env` file for local development

<details>
<summary>💡 Hint</summary>

Use `python-dotenv` to load `.env`. The `os.getenv()` call reads the value after `load_dotenv()` runs. FastAPI app is just `app = FastAPI()`.

</details>

<details>
<summary>✅ Answer</summary>

**.env**
```bash
GITHUB_WEBHOOK_SECRET=my-github-secret
STRIPE_WEBHOOK_SECRET=whsec_my-stripe-secret
```

**main.py**
```python
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()  # ← reads .env file into os.environ before anything else runs

app = FastAPI(title="Webhook Receiver")

# Import routers after app is created (avoids circular imports)
from routes import github_router, stripe_router, events_router

app.include_router(github_router)
app.include_router(stripe_router)
app.include_router(events_router)
```

**Run it:**
```bash
uvicorn main:app --reload --port 8000
```

</details>

---

## Step 3 — Receive the Raw POST Body

Here is the trap almost every developer falls into on their first webhook implementation.

**The problem with Pydantic models:** When you define a route like `async def handler(payload: MyModel)`, FastAPI parses the JSON body *before* your handler runs. By then, the original bytes are gone — and HMAC signature verification requires the *exact* raw bytes that were transmitted. Even a single extra space invalidates the signature.

Think about it: why would parsing the JSON first break signature verification?

<details>
<summary>💡 Hint</summary>

HMAC is computed over a sequence of bytes. `{"a":1}` and `{"a": 1}` (note the space) are the same JSON but different byte sequences. GitHub signs the original bytes — you must verify against the same bytes, not a re-serialized version.

</details>

<details>
<summary>✅ Answer</summary>

```python
from fastapi import Request

@app.post("/webhook/github")
async def github_webhook(request: Request):
    raw_body = await request.body()    # ← bytes exactly as received, before any parsing
    payload = await request.json()     # ← parsed dict for extracting fields
    # Now you have both: raw_body for HMAC, payload for data
```

`request.body()` caches the bytes internally — calling it and then `request.json()` on the same request is safe. `request.json()` calls `request.body()` internally, so there's no double-read issue.

</details>

---

## Step 4 — HMAC Signature Verification (GitHub)

**What is HMAC?** A **keyed hash** — it mixes a secret key with the message to produce a signature. Only someone who knows the secret can produce the correct signature for a given message. It's like a wax seal — anyone can read the letter, but only the holder of the seal can produce a valid one.

The math: `HMAC(key, message) = Hash(key XOR opad || Hash(key XOR ipad || message))`

You don't need to know the math — just the guarantee: without the secret key, you cannot produce a valid HMAC.

**GitHub's scheme:**
- You set a secret when configuring the webhook
- GitHub computes `HMAC-SHA256(secret, raw_body)`
- GitHub sends the hex digest in the `X-Hub-Signature-256` header as `sha256=<hex>`
- You compute the same HMAC and compare

Think about it: why use `hmac.compare_digest()` instead of `==` for comparing the signatures?

<details>
<summary>💡 Hint</summary>

String comparison with `==` returns early the moment it finds a mismatch — character by character. This creates a **timing side-channel**: an attacker can measure how long the comparison takes to guess the correct signature byte by byte. `hmac.compare_digest()` always takes the same time regardless of where the mismatch is.

</details>

<details>
<summary>✅ Answer</summary>

```python
import hmac
import hashlib
import os

def verify_github_signature(raw_body: bytes, signature_header: str) -> bool:
    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "")  # ← read secret from env, never hardcode
    
    if not signature_header:
        return False
    
    # GitHub sends "sha256=<hex_digest>" — split off the prefix
    parts = signature_header.split("=", 1)     # ← split on first = only
    if len(parts) != 2 or parts[0] != "sha256":
        return False
    
    received_sig = parts[1]  # ← the hex digest GitHub sent
    
    # Compute the expected HMAC
    expected_sig = hmac.new(
        key=secret.encode("utf-8"),     # ← secret must be bytes
        msg=raw_body,                   # ← the exact raw bytes received
        digestmod=hashlib.sha256        # ← GitHub uses SHA-256
    ).hexdigest()
    
    # compare_digest is constant-time — prevents timing attacks
    return hmac.compare_digest(expected_sig, received_sig)
```

</details>

---

## Step 5 — Create a Dependency for Signature Verification

Writing `verify_github_signature(raw_body, header)` inside every route is repetitive and easy to forget. FastAPI's **dependency injection** system lets you declare a reusable function that runs before your route handler — perfect for authentication and verification.

Think about it: how does `Depends()` change what happens when the signature check fails? How do you make FastAPI automatically reject the request without returning from the route?

<details>
<summary>💡 Hint</summary>

Dependencies run before the route handler. Raise `HTTPException` inside the dependency — FastAPI catches it and returns the error response without ever calling your route function.

</details>

<details>
<summary>✅ Answer</summary>

```python
from fastapi import Request, Header, HTTPException, Depends
from typing import Optional

async def verify_github_dep(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None)  # ← FastAPI extracts header by name
) -> bytes:
    raw_body = await request.body()
    
    if not verify_github_signature(raw_body, x_hub_signature_256 or ""):
        raise HTTPException(status_code=401, detail="Invalid signature")  # ← stops the request here
    
    return raw_body  # ← returned value is injected into the route handler


# Usage in route — verification happens automatically
@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    raw_body: bytes = Depends(verify_github_dep)  # ← 401 if sig invalid, raw_body if valid
):
    payload = await request.json()
    # ... process payload
```

FastAPI evaluates `Depends(verify_github_dep)` before calling `github_webhook`. If it raises, the route never runs. If it returns `raw_body`, that value is passed in as the `raw_body` parameter.

</details>

---

## Step 6 — Parse the GitHub Push Payload

GitHub push events carry a lot of data. You need to extract the useful fields: which repo was pushed to, who pushed, and what commits were included.

Think about it: what fields would you expect in a push event payload? Before looking at the answer, sketch out the JSON structure you'd expect GitHub to send.

<details>
<summary>💡 Hint</summary>

GitHub push payloads are nested: `payload["repository"]["full_name"]`, `payload["pusher"]["name"]`, `payload["commits"]` is a list where each commit has `"id"`, `"message"`, and `"author"` (which itself is a dict with `"name"`).

</details>

<details>
<summary>✅ Answer</summary>

```python
from typing import Any

def parse_github_push(payload: dict[str, Any]) -> dict[str, Any]:
    commits = []
    
    for commit in payload.get("commits", []):  # ← .get() avoids KeyError if field missing
        commits.append({
            "id": commit.get("id", "")[:7],           # ← short SHA (first 7 chars)
            "message": commit.get("message", ""),
            "author": commit.get("author", {}).get("name", "unknown"),
        })
    
    return {
        "event_type": "github.push",
        "repo": payload.get("repository", {}).get("full_name", "unknown"),
        "pusher": payload.get("pusher", {}).get("name", "unknown"),
        "ref": payload.get("ref", ""),         # ← e.g. "refs/heads/main"
        "commits": commits,
        "commit_count": len(commits),
    }
```

**Example parsed output:**
```json
{
  "event_type": "github.push",
  "repo": "octocat/Hello-World",
  "pusher": "octocat",
  "ref": "refs/heads/main",
  "commits": [
    {"id": "abc1234", "message": "Fix typo", "author": "octocat"}
  ],
  "commit_count": 1
}
```

</details>

---

## Step 7 — Store Events with a Deque

You need to keep the last 10 events in memory. A plain list grows forever — you'd have to manually trim it. A **deque** (double-ended queue) with `maxlen` auto-evicts the oldest item whenever a new one is appended past capacity.

Think about it: why does `maxlen=10` mean you never have to manually delete old events?

<details>
<summary>💡 Hint</summary>

`deque(maxlen=10)` is a fixed-size ring buffer. When you `append()` an 11th item, the oldest item at the front is automatically removed. You never write cleanup logic.

</details>

<details>
<summary>✅ Answer</summary>

**storage.py**
```python
from collections import deque
from typing import Any

# Module-level storage — lives for the lifetime of the process
# deque with maxlen automatically drops the oldest item when full
event_store: deque[dict[str, Any]] = deque(maxlen=10)


def store_event(event: dict[str, Any]) -> None:
    event_store.appendleft(event)  # ← newest event at index 0


def get_events() -> list[dict[str, Any]]:
    return list(event_store)  # ← convert to list for JSON serialization
```

**Thread-safety note:** FastAPI runs on a single-threaded async event loop (unless you use `run_in_threadpool`). Appending to a deque from coroutines is safe because only one coroutine runs at a time — there's no concurrent write. If you ever add background threads or workers, wrap mutations in `asyncio.Lock`.

**GET /events route:**
```python
from storage import get_events

@app.get("/events")
async def list_events():
    return {"events": get_events(), "count": len(event_store)}
```

</details>

---

## Step 8 — Stripe Signature Verification

Stripe uses a different verification scheme than GitHub. Rather than a simple HMAC of the body, Stripe includes a **timestamp** in the signature header to prevent **replay attacks** — an attacker recording a valid webhook and re-sending it later.

**Stripe's `Stripe-Signature` header format:**
```
t=1614556800,v1=abc123...,v1=def456...
```

- `t` — Unix timestamp of when Stripe sent the webhook
- `v1` — one or more HMAC-SHA256 signatures (Stripe sometimes rotates secrets)

**Stripe's signing scheme:**
1. Build the **signed payload string**: `{timestamp}.{raw_body}`
2. Compute `HMAC-SHA256(webhook_secret, signed_payload_string)`
3. Compare against the `v1` value(s) in the header
4. Check the timestamp is within 5 minutes of now (replay window)

Think about it: why does including the timestamp in the signed payload prevent replay attacks?

<details>
<summary>💡 Hint</summary>

If the timestamp is inside the signed data, you can't change it without invalidating the signature. And if you can't change it, old webhooks will fail the "within 5 minutes" check. An attacker can't forge a new timestamp without knowing the secret.

</details>

<details>
<summary>✅ Answer</summary>

**security.py**
```python
import hmac
import hashlib
import os
import time
from typing import Optional

STRIPE_TOLERANCE_SECONDS = 300  # ← 5 minutes replay window


def verify_stripe_signature(
    raw_body: bytes,
    signature_header: str,
    tolerance: int = STRIPE_TOLERANCE_SECONDS
) -> Optional[str]:
    """
    Returns the event ID from the payload if valid, raises ValueError if not.
    """
    secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    if not signature_header:
        raise ValueError("Missing Stripe-Signature header")
    
    # Parse header: "t=1614556800,v1=abc123..."
    header_parts = {}
    for part in signature_header.split(","):
        key, _, value = part.partition("=")
        header_parts.setdefault(key.strip(), []).append(value.strip())
    
    timestamp_str = header_parts.get("t", [None])[0]
    signatures = header_parts.get("v1", [])
    
    if not timestamp_str or not signatures:
        raise ValueError("Malformed Stripe-Signature header")
    
    timestamp = int(timestamp_str)
    
    # Replay attack check — reject if event is older than tolerance
    age = abs(time.time() - timestamp)
    if age > tolerance:
        raise ValueError(f"Webhook too old: {age:.0f}s (max {tolerance}s)")
    
    # Build the signed payload: "{timestamp}.{raw_body}"
    signed_payload = f"{timestamp}.".encode() + raw_body
    
    # Compute expected HMAC
    expected = hmac.new(
        key=secret.encode("utf-8"),
        msg=signed_payload,              # ← timestamp is inside the signed data
        digestmod=hashlib.sha256
    ).hexdigest()
    
    # Check if any of the v1 signatures match (Stripe may send multiple during rotation)
    for sig in signatures:
        if hmac.compare_digest(expected, sig):  # ← constant-time comparison
            return timestamp_str
    
    raise ValueError("No matching Stripe signature found")
```

**Route using this:**
```python
from fastapi import Request, Header, HTTPException
from typing import Optional

@app.post("/webhook/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None)
):
    raw_body = await request.body()
    
    try:
        verify_stripe_signature(raw_body, stripe_signature or "")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    payload = await request.json()
    # ... process Stripe event
```

</details>

---

## Step 9 — Idempotency: Handle Duplicate Events

Webhooks are delivered **at least once** — the sending service will retry if your server doesn't respond with 200 in time (network blip, your server was briefly down). This means the same event can arrive multiple times. Processing a `payment.succeeded` event twice would charge the customer twice — catastrophic.

The fix is **idempotency**: remember which event IDs you've already processed, and skip duplicates.

Think about it: where in the handler should you check for duplicates — before or after parsing? What data structure gives O(1) lookup for "have I seen this ID?"

<details>
<summary>💡 Hint</summary>

Check for duplicates as early as possible — before any processing. A Python `set` has O(1) average-case `in` lookup. Store the event ID in the set after successful processing.

</details>

<details>
<summary>✅ Answer</summary>

**storage.py** (add to existing file)
```python
# Set of already-processed event IDs — O(1) lookup
processed_event_ids: set[str] = set()

# Note: in production, use Redis or a DB for this set
# An in-memory set is lost on restart — on restart, old events
# could be re-processed. For truly durable idempotency, persist to storage.


def is_duplicate(event_id: str) -> bool:
    return event_id in processed_event_ids


def mark_processed(event_id: str) -> None:
    processed_event_ids.add(event_id)
```

**In your Stripe route:**
```python
@app.post("/webhook/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None)
):
    raw_body = await request.body()
    
    try:
        verify_stripe_signature(raw_body, stripe_signature or "")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    payload = await request.json()
    event_id = payload.get("id", "")
    
    # Check for duplicate before any processing
    if is_duplicate(event_id):
        return {"status": "duplicate", "event_id": event_id}  # ← return 200, don't reprocess
    
    # Process the event
    event_type = payload.get("type", "unknown")
    parsed = {
        "event_type": f"stripe.{event_type}",
        "event_id": event_id,
        "amount": payload.get("data", {}).get("object", {}).get("amount"),
        "currency": payload.get("data", {}).get("object", {}).get("currency"),
    }
    
    store_event(parsed)
    mark_processed(event_id)          # ← only mark after successful processing
    
    return {"status": "ok", "event_id": event_id}
```

</details>

---

## Step 10 — Test with curl

You can simulate GitHub and Stripe webhooks locally without a real account — you just need to generate the correct HMAC signatures yourself.

Think about it: to generate a valid test signature, what do you need? (The same inputs GitHub uses.)

<details>
<summary>💡 Hint</summary>

You need the secret (from your `.env`) and the exact JSON body you're going to send. Compute the HMAC in Python, then paste the result into the `X-Hub-Signature-256` curl header.

</details>

<details>
<summary>✅ Answer</summary>

**Generate a test GitHub signature in Python:**
```python
import hmac
import hashlib

secret = "my-github-secret"           # ← must match GITHUB_WEBHOOK_SECRET in .env
body = b'{"ref":"refs/heads/main","repository":{"full_name":"user/repo"},"pusher":{"name":"octocat"},"commits":[{"id":"abc1234567890","message":"Fix bug","author":{"name":"octocat"}}]}'

sig = hmac.new(
    key=secret.encode(),
    msg=body,
    digestmod=hashlib.sha256
).hexdigest()

print(f"sha256={sig}")  # ← copy this output into the curl command below
```

**Send a test GitHub webhook:**
```bash
curl -X POST http://localhost:8000/webhook/github \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=PASTE_YOUR_GENERATED_SIG_HERE" \
  -d '{"ref":"refs/heads/main","repository":{"full_name":"user/repo"},"pusher":{"name":"octocat"},"commits":[{"id":"abc1234567890","message":"Fix bug","author":{"name":"octocat"}}]}'
```

**Generate a test Stripe signature:**
```python
import hmac
import hashlib
import time

secret = "whsec_my-stripe-secret"     # ← must match STRIPE_WEBHOOK_SECRET in .env
timestamp = str(int(time.time()))
body = b'{"id":"evt_test_001","type":"payment_intent.succeeded","data":{"object":{"amount":2000,"currency":"usd"}}}'

signed_payload = f"{timestamp}.".encode() + body

sig = hmac.new(
    key=secret.encode(),
    msg=signed_payload,
    digestmod=hashlib.sha256
).hexdigest()

header = f"t={timestamp},v1={sig}"
print(f"Stripe-Signature: {header}")
```

**Send a test Stripe webhook:**
```bash
curl -X POST http://localhost:8000/webhook/stripe \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: PASTE_YOUR_GENERATED_HEADER_HERE" \
  -d '{"id":"evt_test_001","type":"payment_intent.succeeded","data":{"object":{"amount":2000,"currency":"usd"}}}'
```

**Check stored events:**
```bash
curl http://localhost:8000/events
```

**Test invalid signature (expect 401):**
```bash
curl -X POST http://localhost:8000/webhook/github \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=badsignature" \
  -d '{"ref":"refs/heads/main"}'
```

</details>

---

## What You Built

```
                     POST /webhook/github
GitHub ─────────────────────────────────────────►
                     X-Hub-Signature-256 header
                                │
                     ┌──────────▼──────────┐
                     │  verify_github_dep  │ ← FastAPI Depends()
                     │  hmac.compare_digest│
                     └──────────┬──────────┘
                                │ 401 if invalid
                                │ raw_body if valid
                     ┌──────────▼──────────┐
                     │  parse_github_push  │ ← extract repo, pusher, commits
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │  deque(maxlen=10)   │ ← auto-evicts oldest
                     │  event_store        │
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
Stripe ─────────────►│  POST /webhook/stripe│ ← t=timestamp,v1=sig
                     │  replay attack check │ ← reject if > 5min old
                     │  idempotency check   │ ← skip if seen event_id
                     └──────────┬──────────┘
                                │
Client ─────────────────────────►  GET /events → last 10 events
```

## What You Learned

- Webhooks are push-based: the remote service calls your endpoint the moment an event occurs
- You must read raw bytes (`await request.body()`) before parsing JSON — HMAC is computed over exact bytes
- HMAC is a keyed hash — without the secret, you cannot forge a valid signature
- `hmac.compare_digest()` prevents timing attacks that `==` would allow
- FastAPI `Depends()` lets you extract verification logic into reusable middleware-like functions
- Stripe's scheme signs `{timestamp}.{body}` to embed a replay window directly in the signature
- `deque(maxlen=N)` is a bounded ring buffer — no manual cleanup needed
- Webhook services retry on failure, so idempotency (tracking processed event IDs) is not optional

## Extend It

- Add a retry queue: if processing fails, retry up to 3 times with exponential backoff
- Persist events to SQLite instead of in-memory deque — events survive server restarts
- Add a webhook registration endpoint: `POST /webhooks/register` to store URLs and send outbound webhooks
- Forward verified events to a Celery task (connects to Project 06) — return 200 immediately, process asynchronously
