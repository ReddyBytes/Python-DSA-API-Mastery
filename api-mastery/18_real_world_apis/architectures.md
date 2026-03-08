# 16 — Real-World API Architectures

> Theory is clean. Real systems are not. This chapter is four case studies of APIs that handle money, social graph, physical movement, and business software — each with unique constraints that force specific design decisions.

---

## Why Case Studies Matter

Every API tutorial shows you a to-do list API. The endpoints are simple, the data is tiny, and the only thing that can go wrong is returning a `400` when the input is missing a field.

Real APIs carry more weight. A payment API that charges someone twice is a legal problem. A social feed that breaks under load is a reputational problem. A ride-sharing API with stale location data is a physical safety problem.

The constraints are the interesting part. They force you to make specific architectural choices that would be overkill or wrong in a simpler system. Once you understand why each choice was made, you recognize the pattern and can apply it when you face the same constraint.

---

## Case 1: Payment System API (Stripe-style)

### The Core Constraint

Money is not just data. If you write a user record twice, you get a duplicate. If you charge a card twice, you get a lawsuit.

Every design decision in a payment API flows from this constraint: **the consequence of processing a payment twice is categorically different from the consequence of any ordinary bug.**

### The State Machine

Payments are not a boolean. They move through states, and not all state transitions are valid.

```
                      ┌─────────┐
                      │ created │
                      └────┬────┘
                           │  POST /payment-intents/{id}/confirm
                           ▼
                      ┌────────────┐
                      │ processing │
                      └─────┬──────┘
              ┌─────────────┼──────────────┐
              ▼             ▼              ▼
         ┌──────────┐  ┌─────────┐  ┌──────────┐
         │ succeeded│  │ failed  │  │ canceled │
         └──────────┘  └─────────┘  └──────────┘
```

Once a payment reaches `succeeded`, it cannot be changed to `failed`. Once it reaches `canceled`, it cannot be re-confirmed. The state machine is enforced in the database and the application layer, not trusted to the client.

### Core Endpoints

```python
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import uuid

app = FastAPI()

class PaymentStatus(str, Enum):
    CREATED = "created"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"

class CreatePaymentIntentRequest(BaseModel):
    amount: int = Field(gt=0, description="Amount in cents")
    currency: str = Field(min_length=3, max_length=3, pattern="^[a-z]{3}$")
    customer_id: int
    description: Optional[str] = Field(default=None, max_length=500)

@app.post("/payment-intents", status_code=201)
def create_payment_intent(
    body: CreatePaymentIntentRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    current_user = Depends(get_current_user),
):
    """
    Create a payment intent. This does not charge the card yet.
    The client must confirm with the card token.

    Idempotency-Key is REQUIRED. Two requests with the same key
    return the same payment intent — the card is never charged twice.
    """
    # Check if we've already processed this idempotency key
    existing = db.query(PaymentIntent).filter(
        PaymentIntent.idempotency_key == idempotency_key,
        PaymentIntent.user_id == current_user.id
    ).first()

    if existing:
        return existing  # Return the same response as the original request

    intent = PaymentIntent(
        id=f"pi_{uuid.uuid4().hex}",
        amount=body.amount,
        currency=body.currency,
        customer_id=body.customer_id,
        status=PaymentStatus.CREATED,
        idempotency_key=idempotency_key,
        user_id=current_user.id,
    )
    db.add(intent)
    db.commit()
    return intent

@app.post("/payment-intents/{payment_id}/confirm")
def confirm_payment_intent(
    payment_id: str,
    body: ConfirmPaymentRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    current_user = Depends(get_current_user),
):
    intent = db.query(PaymentIntent).filter(
        PaymentIntent.id == payment_id,
        PaymentIntent.user_id == current_user.id
    ).first()

    if not intent:
        raise HTTPException(status_code=404, detail="Payment intent not found")

    # Enforce valid state transitions
    if intent.status != PaymentStatus.CREATED:
        raise HTTPException(
            status_code=422,
            detail=f"Cannot confirm a payment in '{intent.status}' status"
        )

    # Transition to processing
    intent.status = PaymentStatus.PROCESSING
    db.commit()

    # Call the payment processor (Stripe, Adyen, etc.)
    try:
        result = payment_processor.charge(
            amount=intent.amount,
            currency=intent.currency,
            payment_method=body.payment_method_token,
        )
        intent.status = PaymentStatus.SUCCEEDED
        intent.processor_transaction_id = result.transaction_id
    except PaymentDeclinedError as e:
        intent.status = PaymentStatus.FAILED
        intent.failure_reason = str(e)

    db.commit()
    return intent
```

### Idempotency Keys — The Critical Detail

Every endpoint that creates or confirms a payment requires an `Idempotency-Key` header. The client generates a UUID and includes it. If the network drops mid-request and the client retries, the same key is sent again. The server returns the original result without re-executing the payment logic.

Without idempotency keys, a flaky mobile network + retry logic = double charges.

```
First attempt:
  POST /payment-intents/pi_abc/confirm
  Idempotency-Key: 7f3b2c1a-4d5e-6f7a-8b9c-0d1e2f3a4b5c
  → Network timeout. Client doesn't know if it succeeded.

Retry:
  POST /payment-intents/pi_abc/confirm
  Idempotency-Key: 7f3b2c1a-4d5e-6f7a-8b9c-0d1e2f3a4b5c  ← same key
  → Server finds the stored result, returns it without charging again
```

### Webhook System

When your payment processor (Stripe, etc.) processes a payment, they don't call your API synchronously. Instead, they send you an HTTP POST webhook after the fact:

```python
@app.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(..., alias="Stripe-Signature"),
):
    payload = await request.body()

    # 1. Verify the webhook signature
    # Stripe signs each webhook with your webhook secret using HMAC-SHA256
    # If you skip this, anyone on the internet can fake webhook events
    try:
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    # 2. Check the timestamp to prevent replay attacks
    # A replay attack: attacker captures a legitimate webhook and sends it again later
    # Stripe includes a timestamp in the signature — reject events older than 5 minutes
    timestamp = int(stripe_signature.split("t=")[1].split(",")[0])
    if abs(time.time() - timestamp) > 300:
        raise HTTPException(status_code=400, detail="Webhook timestamp too old")

    # 3. Process the event idempotently
    # Webhooks can be delivered more than once — your handler must be idempotent
    if event_already_processed(event.id):
        return {"status": "already processed"}

    if event.type == "payment_intent.succeeded":
        handle_payment_succeeded(event.data.object)
    elif event.type == "payment_intent.payment_failed":
        handle_payment_failed(event.data.object)

    mark_event_processed(event.id)
    return {"status": "ok"}
```

The signed webhook pattern (HMAC-SHA256 of the payload with a shared secret, verified on your end) is used by every major platform: Stripe, GitHub, Shopify, Twilio. Learn it once, recognize it everywhere.

### PCI Compliance: Tokenization

Never store, log, or transmit raw card numbers through your API. Your frontend sends the card number directly to the payment processor's JavaScript library (Stripe Elements, Braintree Drop-in UI), which returns a single-use token. Your API receives only that token.

```
Browser                    Stripe JS         Your API         Stripe API
   │                           │                │                 │
   │  User enters card number  │                │                 │
   │  ──────────────────────>  │                │                 │
   │                           │  Tokenize card │                 │
   │                           │  ───────────>  │                 │
   │                           │  tok_abc123    │                 │
   │  tok_abc123               │                │                 │
   │  <──────────────────────  │                │                 │
   │                           │                │                 │
   │  POST /payment-intents/pi_xyz/confirm       │                 │
   │  { payment_method: "tok_abc123" }           │                 │
   │  ────────────────────────────────────────>  │                 │
   │                           │                │  charge(tok)    │
   │                           │                │  ────────────>  │
```

The card number never passes through your servers, which means it never appears in your logs, your database, or your network traffic captures. This is the architecture that reduces PCI scope from "we handle card data" to "we handle tokens."

---

## Case 2: Social Media Platform API (Twitter-style)

### The Core Constraint

A social platform at scale has tens of millions of users, each with a timeline that is the merged, ordered output of potentially thousands of accounts they follow. Generating that timeline naively (query all tweets from all followed users, sort by time) becomes slower as the follow graph grows. At some threshold it breaks entirely.

The constraint is: **every user needs a personalized feed delivered quickly, and the write volume (new tweets) is enormous.**

### Core Endpoints

```python
class CreateTweetRequest(BaseModel):
    text: str = Field(min_length=1, max_length=280)
    reply_to_tweet_id: Optional[int] = None
    media_ids: list[int] = Field(default=[], max_items=4)

@app.post("/tweets", status_code=201)
def create_tweet(
    body: CreateTweetRequest,
    current_user = Depends(get_current_user),
):
    tweet = Tweet(
        user_id=current_user.id,
        text=body.text,
        reply_to_tweet_id=body.reply_to_tweet_id,
    )
    db.add(tweet)
    db.commit()

    # Fan-out: push this tweet ID to the timeline caches of all followers
    # This runs in a background task — the API response should not wait for it
    background_tasks.add_task(fan_out_tweet, tweet.id, current_user.id)

    return tweet

@app.get("/timeline")
def get_timeline(
    cursor: Optional[str] = None,
    limit: int = Query(default=20, le=100),
    current_user = Depends(get_current_user),
):
    """
    Returns the authenticated user's home timeline.
    Uses cursor-based pagination — see below for why.
    """
    return get_user_timeline(current_user.id, cursor=cursor, limit=limit)
```

### The Feed Challenge: Fan-Out vs. Fan-In

There are two approaches to building a social feed. Each has a different cost structure:

```
Fan-Out on Write (push model)
  When Alice posts a tweet:
  → Write the tweet to the DB
  → For each of Alice's followers (say, 1000 users):
     → Push tweet ID to that user's timeline cache (Redis list)
  When Bob loads his timeline:
  → Read the pre-built timeline cache: O(1), extremely fast

  Cost: Write amplification — one tweet = 1000 Redis writes
  Problem: Celebrities with 10M followers require 10M writes per tweet

Fan-In on Read (pull model)
  When Alice posts a tweet:
  → Write the tweet to the DB only
  When Bob loads his timeline:
  → Query: "give me recent tweets from all users Bob follows"
  → Sort and merge the results

  Cost: Read amplification — timeline load requires querying many users
  Problem: If Bob follows 5000 accounts, every timeline load is expensive

Real systems use a hybrid:
  → Regular users: fan-out (fast reads, acceptable write cost)
  → Celebrities (>1M followers): fan-in (read-time merge, avoids write storm)
  → Inactive users: skip fan-out (no point caching for someone who hasn't
    logged in for 6 months)
```

### Cursor-Based Pagination for Timelines

Offset-based pagination (`?page=2&limit=20`) breaks for real-time feeds. If 10 new tweets arrive while you're reading page 1 and you then request page 2, the dataset has shifted — you either miss tweets or see duplicates.

Cursor-based pagination solves this:

```python
def get_user_timeline(user_id: int, cursor: Optional[str], limit: int):
    """
    Cursor encodes the last tweet's timestamp + ID.
    Decoded, it represents "give me tweets older than this point."
    This is stable regardless of new tweets arriving at the top of the feed.
    """
    timeline_cache_key = f"timeline:{user_id}"

    if cursor:
        # Decode: cursor is base64(timestamp:tweet_id)
        decoded = base64.b64decode(cursor).decode()
        since_timestamp, since_id = decoded.split(":")
        tweets = redis_timeline.get_before(
            timeline_cache_key,
            before_timestamp=float(since_timestamp),
            limit=limit
        )
    else:
        tweets = redis_timeline.get_latest(timeline_cache_key, limit=limit)

    next_cursor = None
    if len(tweets) == limit:
        last = tweets[-1]
        next_cursor = base64.b64encode(
            f"{last.timestamp}:{last.id}".encode()
        ).decode()

    return {
        "tweets": tweets,
        "next_cursor": next_cursor,
        "has_more": next_cursor is not None,
    }
```

The cursor encodes a position in an ordered stream, not a page number. A client loading page 3 while new items arrive at the top will always get the correct next set of items.

### Rate Limiting Per Endpoint

Twitter's rate limits are differentiated by endpoint because different operations have different abuse vectors:

```python
RATE_LIMITS = {
    "/tweets": RateLimit(requests=300, window_minutes=180),  # 300 tweets per 3 hours
    "/follow": RateLimit(requests=400, window_minutes=1440), # 400 follows per day
    "/timeline": RateLimit(requests=180, window_minutes=15), # 180 timeline reads per 15 min
    "/search": RateLimit(requests=180, window_minutes=15),   # 180 searches per 15 min
}
```

Applying these limits at the endpoint level rather than globally prevents an automated spammer from exhausting the timeline API while using the follow limit, or vice versa.

### Media Upload Flow: Presigned URLs

A naive implementation: `POST /tweets/media` with the file in the request body. The problem: large files passing through your API server are expensive. The server has to receive the entire file, store it, then upload it to object storage (S3). At scale, this saturates your API server's network bandwidth.

The production pattern: presigned URLs.

```
Client                      Your API                    AWS S3
   │                            │                          │
   │  POST /media/upload-url    │                          │
   │  { content_type: "image/jpeg", size: 2048000 }        │
   │  ─────────────────────>    │                          │
   │                            │  generate presigned PUT  │
   │                            │  ────────────────────>   │
   │                            │  presigned_url           │
   │                            │  <────────────────────   │
   │  { upload_url, media_id }  │                          │
   │  <─────────────────────    │                          │
   │                            │                          │
   │  PUT presigned_url         │                          │
   │  [file bytes]              │                          │
   │  ───────────────────────────────────────────────────> │
   │  200 OK                                               │
   │  <───────────────────────────────────────────────────  │
   │                            │                          │
   │  POST /tweets              │                          │
   │  { text: "...", media_ids: [media_id] }               │
   │  ─────────────────────>    │                          │
```

The file goes directly from the client to S3. Your API server only handles metadata. Network bandwidth at the API layer scales independently from storage capacity.

```python
@app.post("/media/upload-url")
def get_upload_url(
    body: UploadUrlRequest,
    current_user = Depends(get_current_user),
):
    media_id = f"media_{uuid.uuid4().hex}"
    s3_key = f"uploads/{current_user.id}/{media_id}"

    presigned_url = s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.MEDIA_BUCKET,
            "Key": s3_key,
            "ContentType": body.content_type,
            "ContentLength": body.size,
        },
        ExpiresIn=300,  # URL valid for 5 minutes
    )

    # Store the media record as "pending" — it doesn't exist yet
    media = MediaRecord(
        id=media_id,
        s3_key=s3_key,
        user_id=current_user.id,
        status="pending",
    )
    db.add(media)
    db.commit()

    return {"upload_url": presigned_url, "media_id": media_id}
```

---

## Case 3: Ride-Sharing API (Uber-style)

### The Core Constraint

A ride-sharing API is a physical-world coordination system. The state it manages is not just data in a database — it includes the real-time location of vehicles on roads. Stale data is not just inconvenient; it can result in a driver being sent to the wrong location and a passenger being stranded.

The constraint is: **location data must be updated continuously and made available with very low latency.**

### The Full Request Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. Rider requests ride                                       │
│     POST /rides  { pickup_location, destination }            │
│     → ride created in "requesting" state                     │
├─────────────────────────────────────────────────────────────┤
│  2. Platform matches a nearby available driver               │
│     Background: query Redis GEO for drivers within 5km       │
│     Score by: distance, acceptance rate, car type            │
│     Send push notification to matched driver                 │
├─────────────────────────────────────────────────────────────┤
│  3. Driver accepts                                           │
│     POST /rides/{id}/accept                                  │
│     → ride transitions to "accepted"                         │
├─────────────────────────────────────────────────────────────┤
│  4. Real-time tracking begins                                │
│     Client opens WebSocket: ws://api.myapp.com/rides/{id}    │
│     Driver app pushes location updates every 3 seconds       │
│     Rider app receives them in real-time                     │
├─────────────────────────────────────────────────────────────┤
│  5. Ride completes                                           │
│     POST /rides/{id}/complete                                │
│     → ride transitions to "completed"                        │
│     → Webhook fired to payment service: charge the rider     │
└─────────────────────────────────────────────────────────────┘
```

### Geospatial Queries with Redis GEO

Finding available drivers within 5km of a pickup point is a geospatial query. Redis GEO provides O(N+log(M)) geospatial range queries using a sorted set with geohash-encoded scores.

```python
import redis
from dataclasses import dataclass

r = redis.Redis(host="localhost", port=6379)

@dataclass
class Location:
    latitude: float
    longitude: float

def update_driver_location(driver_id: int, location: Location):
    """Called every 3 seconds from the driver's mobile app."""
    r.geoadd(
        "available_drivers",
        [location.longitude, location.latitude, str(driver_id)]
    )
    # Also store the full location for display purposes
    r.setex(
        f"driver_location:{driver_id}",
        30,  # TTL: if no update in 30 seconds, driver is considered offline
        json.dumps({"lat": location.latitude, "lng": location.longitude})
    )

def find_nearby_drivers(pickup: Location, radius_km: float = 5.0) -> list[int]:
    """Returns list of driver IDs within radius_km of the pickup point."""
    results = r.geosearch(
        "available_drivers",
        longitude=pickup.longitude,
        latitude=pickup.latitude,
        radius=radius_km,
        unit="km",
        sort="ASC",       # nearest first
        count=10,         # consider the 10 nearest candidates
        withdist=True,
    )
    return [
        {"driver_id": int(driver_id), "distance_km": distance}
        for driver_id, distance in results
    ]

@app.post("/rides", status_code=201)
def request_ride(
    body: RequestRideRequest,
    current_user = Depends(get_current_user),
):
    ride = Ride(
        rider_id=current_user.id,
        pickup_lat=body.pickup.latitude,
        pickup_lng=body.pickup.longitude,
        destination_lat=body.destination.latitude,
        destination_lng=body.destination.longitude,
        status="requesting",
        surge_multiplier=calculate_surge_multiplier(body.pickup),
    )
    db.add(ride)
    db.commit()

    # Kick off driver matching in background (non-blocking)
    background_tasks.add_task(match_driver, ride.id, body.pickup)

    return ride
```

### WebSockets for Real-Time Location

The rider's app needs live updates as the driver approaches. Polling every few seconds introduces unacceptable latency and hammers the database. WebSockets are the right tool:

```python
from fastapi import WebSocket, WebSocketDisconnect
import json

# Connection manager for ride-specific WebSocket connections
class RideConnectionManager:
    def __init__(self):
        self.connections: dict[str, list[WebSocket]] = {}

    async def connect(self, ride_id: str, websocket: WebSocket):
        await websocket.accept()
        if ride_id not in self.connections:
            self.connections[ride_id] = []
        self.connections[ride_id].append(websocket)

    def disconnect(self, ride_id: str, websocket: WebSocket):
        if ride_id in self.connections:
            self.connections[ride_id].remove(websocket)

    async def broadcast_to_ride(self, ride_id: str, message: dict):
        """Send a message to all participants watching this ride."""
        dead_connections = []
        for ws in self.connections.get(ride_id, []):
            try:
                await ws.send_json(message)
            except Exception:
                dead_connections.append(ws)
        for ws in dead_connections:
            self.connections[ride_id].remove(ws)

manager = RideConnectionManager()

@app.websocket("/rides/{ride_id}/track")
async def track_ride(websocket: WebSocket, ride_id: str):
    """
    Rider connects here to get real-time driver location updates.
    Driver connects here to push their location updates.
    """
    # Authenticate: validate token passed as query param or first message
    token = websocket.query_params.get("token")
    user = authenticate_ws_token(token)
    if not user:
        await websocket.close(code=4001)
        return

    ride = get_ride_or_403(ride_id, user.id)
    await manager.connect(ride_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "location_update" and user.id == ride.driver_id:
                # Driver pushing their location
                update_driver_location(user.id, Location(**data["location"]))

                # Broadcast to all connected participants (rider, etc.)
                await manager.broadcast_to_ride(ride_id, {
                    "type": "driver_location",
                    "location": data["location"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

    except WebSocketDisconnect:
        manager.disconnect(ride_id, websocket)
```

### Surge Pricing

Surge pricing is a dynamic multiplier applied when demand exceeds supply in a geographic area. The calculation runs in a background job, not in the request path:

```python
import asyncio

async def surge_pricing_calculator():
    """Runs every 30 seconds, recalculates surge multipliers per zone."""
    while True:
        zones = get_all_active_zones()

        for zone in zones:
            # Demand: ride requests in this zone in the last 5 minutes
            pending_rides = count_pending_rides_in_zone(zone.id, minutes=5)
            # Supply: available drivers in this zone
            available_drivers = count_available_drivers_in_zone(zone)

            if available_drivers == 0:
                multiplier = 3.0
            else:
                ratio = pending_rides / available_drivers
                # Surge kicks in when demand > supply by more than 20%
                if ratio <= 1.2:
                    multiplier = 1.0
                elif ratio <= 2.0:
                    multiplier = 1.5
                elif ratio <= 3.0:
                    multiplier = 2.0
                else:
                    multiplier = min(3.0, 1.0 + (ratio * 0.5))

            # Store in Redis: fast reads from the request path
            r.setex(f"surge:{zone.id}", 60, multiplier)

        await asyncio.sleep(30)
```

When a rider requests a ride, `calculate_surge_multiplier()` reads the current multiplier from Redis (a single hash lookup). The multiplier is locked into the ride at request time — the rider sees exactly what they will be charged.

### Webhook to Payment at Completion

When the ride completes, the platform calls the payment service rather than processing payment directly:

```python
@app.post("/rides/{ride_id}/complete")
def complete_ride(
    ride_id: str,
    current_user = Depends(get_current_driver),
):
    ride = get_ride_or_403(ride_id, current_user.id)
    ride.status = "completed"
    ride.completed_at = datetime.now(timezone.utc)
    db.commit()

    # Fire-and-forget: call the payment service
    # This is a webhook to your own internal payment service,
    # or a direct call to Stripe if you don't have a separate service
    background_tasks.add_task(
        trigger_payment_webhook,
        event="ride.completed",
        payload={
            "ride_id": ride.id,
            "rider_id": ride.rider_id,
            "amount_cents": calculate_fare(ride),
            "surge_multiplier": ride.surge_multiplier,
        }
    )

    return {"status": "completed", "fare": calculate_fare(ride)}
```

---

## Case 4: SaaS Platform API

### The Core Constraint

A SaaS API serves multiple organizations (tenants) from the same codebase and infrastructure. Each tenant has users, data, and permissions that must be completely isolated from every other tenant — even though they share the same database and application servers.

The constraint is: **a bug that leaks tenant A's data to tenant B is an existential threat to the business.**

### Multi-Tenant Architecture

There are three common approaches to multi-tenancy at the database layer:

```
1. Separate databases per tenant
   → Perfect isolation
   → High operational cost at scale (hundreds of DBs)
   → Use for: enterprise SaaS with strict compliance requirements

2. Separate schemas per tenant (PostgreSQL)
   → Good isolation via schema-level access control
   → Moderate operational cost
   → Use for: mid-size SaaS with moderate tenant count

3. Shared tables with tenant_id column (most common)
   → Every table has a tenant_id column
   → Every query must filter by tenant_id
   → Lowest cost, highest risk (human error can leak data)
   → Mitigate: middleware that enforces tenant_id on every query
```

The shared-table approach with middleware enforcement is the most common production pattern:

```python
from fastapi import Request, HTTPException, Depends

async def get_current_tenant(
    request: Request,
    x_tenant_id: Optional[str] = Header(None),
    current_user = Depends(get_current_user),
) -> Tenant:
    """
    Identify the tenant from:
    1. X-Tenant-ID header (for API key access)
    2. Subdomain (tenant.myapp.com → tenant)
    3. The user's associated tenant (for user sessions)
    """
    if x_tenant_id:
        tenant = db.query(Tenant).filter(Tenant.id == x_tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        # Verify this user belongs to this tenant
        if current_user.tenant_id != tenant.id:
            raise HTTPException(status_code=403, detail="Access denied")
    else:
        tenant = db.query(Tenant).filter(
            Tenant.id == current_user.tenant_id
        ).first()

    # Attach to request state so middleware and handlers can access it
    request.state.tenant = tenant
    return tenant

@app.get("/projects")
def list_projects(
    current_tenant: Tenant = Depends(get_current_tenant),
):
    # The tenant is always scoped — it is impossible to return another tenant's projects
    return db.query(Project).filter(
        Project.tenant_id == current_tenant.id
    ).all()
```

### Plan-Based Feature Flags

Different subscription tiers unlock different features. Enforce this in middleware, not scattered through handlers:

```python
from functools import wraps
from enum import Enum

class Feature(str, Enum):
    API_ACCESS = "api_access"
    ADVANCED_ANALYTICS = "advanced_analytics"
    CUSTOM_DOMAINS = "custom_domains"
    SSO = "sso"
    AUDIT_LOG_EXPORT = "audit_log_export"

PLAN_FEATURES = {
    "free": {Feature.API_ACCESS},
    "starter": {Feature.API_ACCESS, Feature.ADVANCED_ANALYTICS},
    "professional": {Feature.API_ACCESS, Feature.ADVANCED_ANALYTICS,
                     Feature.CUSTOM_DOMAINS},
    "enterprise": {Feature.API_ACCESS, Feature.ADVANCED_ANALYTICS,
                   Feature.CUSTOM_DOMAINS, Feature.SSO,
                   Feature.AUDIT_LOG_EXPORT},
}

def require_feature(feature: Feature):
    """Dependency factory: raises 402 if tenant's plan doesn't include the feature."""
    async def check_feature(
        current_tenant: Tenant = Depends(get_current_tenant)
    ):
        plan_features = PLAN_FEATURES.get(current_tenant.plan, set())
        if feature not in plan_features:
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "feature_not_available",
                    "feature": feature,
                    "current_plan": current_tenant.plan,
                    "upgrade_url": f"https://myapp.com/upgrade?from={current_tenant.plan}",
                }
            )
        return current_tenant
    return check_feature

@app.get("/analytics/advanced")
def advanced_analytics(
    tenant = Depends(require_feature(Feature.ADVANCED_ANALYTICS)),
):
    return generate_advanced_analytics(tenant.id)

@app.post("/sso/configure")
def configure_sso(
    body: SSOConfigRequest,
    tenant = Depends(require_feature(Feature.SSO)),
):
    return save_sso_configuration(tenant.id, body)
```

### Team-Based RBAC

Within a tenant, different users have different roles. Owner > Admin > Member is the minimum set for a SaaS platform:

```python
class TeamRole(str, Enum):
    OWNER = "owner"      # Full control, including billing and tenant deletion
    ADMIN = "admin"      # Manage users, most settings
    MEMBER = "member"    # Standard access based on assigned projects

# Permission matrix
ROLE_PERMISSIONS = {
    TeamRole.OWNER: {
        "billing:manage", "tenant:delete", "users:manage",
        "api_keys:manage", "projects:manage", "data:read", "data:write"
    },
    TeamRole.ADMIN: {
        "users:manage", "api_keys:manage",
        "projects:manage", "data:read", "data:write"
    },
    TeamRole.MEMBER: {
        "data:read", "data:write"
    },
}

def require_permission(permission: str):
    async def check(
        current_user = Depends(get_current_user),
        current_tenant = Depends(get_current_tenant),
    ):
        membership = db.query(TenantMembership).filter(
            TenantMembership.user_id == current_user.id,
            TenantMembership.tenant_id == current_tenant.id,
        ).first()

        if not membership:
            raise HTTPException(status_code=403, detail="Not a member of this tenant")

        allowed = ROLE_PERMISSIONS.get(membership.role, set())
        if permission not in allowed:
            raise HTTPException(
                status_code=403,
                detail=f"Your role ('{membership.role}') does not have '{permission}' permission"
            )
        return membership
    return check

@app.delete("/team/members/{user_id}")
def remove_member(
    user_id: int,
    _permission = Depends(require_permission("users:manage")),
    current_tenant = Depends(get_current_tenant),
):
    # Only admins and owners reach this point
    remove_tenant_member(current_tenant.id, user_id)
    return {"status": "removed"}
```

### API Key Management for Programmatic Access

SaaS platforms need to support non-human clients — CI/CD pipelines, internal scripts, integrations. The pattern: each tenant can create named API keys, each scoped to specific permissions.

```python
class CreateApiKeyRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    permissions: list[str]
    expires_at: Optional[datetime] = None

@app.post("/api-keys", status_code=201)
def create_api_key(
    body: CreateApiKeyRequest,
    current_tenant = Depends(get_current_tenant),
    _permission = Depends(require_permission("api_keys:manage")),
):
    # Generate the key: prefix makes it identifiable in logs and code
    raw_key = f"sk_{current_tenant.id[:8]}_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    api_key = ApiKey(
        tenant_id=current_tenant.id,
        name=body.name,
        key_prefix=raw_key[:16],     # Store prefix for display (sk_abc12345...)
        key_hash=key_hash,           # Store hash for verification (never the raw key)
        permissions=body.permissions,
        expires_at=body.expires_at,
        created_by=request.state.user_id,
    )
    db.add(api_key)
    db.commit()

    # Return the raw key ONCE — it cannot be retrieved again after this response
    return {
        "id": api_key.id,
        "name": api_key.name,
        "key": raw_key,              # ← shown once, then never again
        "key_prefix": api_key.key_prefix,
        "permissions": api_key.permissions,
        "expires_at": api_key.expires_at,
        "warning": "Store this key securely. It will not be shown again."
    }

async def authenticate_api_key(request: Request) -> Optional[ApiKeyContext]:
    """Called from auth middleware to authenticate API key requests."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer sk_"):
        return None

    raw_key = auth_header.removeprefix("Bearer ")
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    api_key = db.query(ApiKey).filter(
        ApiKey.key_hash == key_hash,
        ApiKey.revoked_at.is_(None),
    ).first()

    if not api_key:
        return None

    if api_key.expires_at and api_key.expires_at < datetime.now(timezone.utc):
        return None

    return ApiKeyContext(
        tenant_id=api_key.tenant_id,
        permissions=api_key.permissions,
        key_id=api_key.id,
    )
```

### Usage Tracking for Billing

SaaS billing often ties to API usage. Track it in middleware:

```python
@app.middleware("http")
async def track_usage(request: Request, call_next):
    response = await call_next(request)

    # Only track successful API calls (not auth failures, not 4xx errors)
    if response.status_code < 400 and hasattr(request.state, "tenant"):
        tenant_id = request.state.tenant.id
        month_key = datetime.now(timezone.utc).strftime("%Y-%m")

        # Increment API call counter in Redis (atomic, O(1))
        r.hincrby(f"usage:{tenant_id}:{month_key}", "api_calls", 1)

        # Check if they've hit their plan limit
        usage = int(r.hget(f"usage:{tenant_id}:{month_key}", "api_calls") or 0)
        plan_limit = get_plan_api_limit(request.state.tenant.plan)

        if usage > plan_limit:
            # In production: send a billing webhook, downgrade or throttle
            # For now: add a warning header
            response.headers["X-Usage-Warning"] = (
                f"API call limit for your plan exceeded ({usage}/{plan_limit})"
            )

    return response
```

---

## Patterns That Appear Across All Four

Looking across the case studies, a few patterns appear in every serious production API:

```
Idempotency
  Payment: required on every charge operation
  Social: required on tweet creation (mobile retries)
  Ride: required on ride request (tap twice = two rides)
  SaaS: required on user creation, billing events

State Machines
  Payment: created → processing → succeeded/failed/canceled
  Ride:    requesting → accepted → in_progress → completed/canceled
  General: explicit transitions, invalid transitions rejected with 422

Background Tasks
  Payment: fan-out webhook delivery
  Social:  feed fan-out to follower caches
  Ride:    driver matching, surge calculation
  SaaS:    usage aggregation, billing webhooks
  Rule:    if it takes >100ms or involves external systems, run it async

Redis as Fast Layer
  Rate limiting, token revocation, location data, feed caches,
  usage counters, surge multipliers — all in Redis, all O(1)
  The database is the source of truth; Redis is the fast path

Webhook Signing
  Payment processor → your API: HMAC-SHA256 signed
  Your API → other services: same pattern
  Always verify the signature. Always check the timestamp. Always process idempotently.
```

These are not advanced patterns. They are the minimum bar for a production API in any domain where the cost of a bug is not just a wrong answer on a screen.

---

| Navigation | |
|---|---|
| Previous | [12 — Production Deployment](../12_production_deployment/deployment_guide.md) |
| Home | [README.md](../README.md) |
