# 11 — FastAPI Advanced Features

> 📝 **Practice:** [Q42 · fastapi-middleware](../api_practice_questions_100.md#q42--normal--fastapi-middleware)

> 📝 **Practice:** [Q40 · fastapi-async-endpoints](../api_practice_questions_100.md#q40--thinking--fastapi-async-endpoints)

> "The basics get you to production. The advanced features keep you there."

> 📝 **Practice:** [Q50 · fastapi-lifespan](../api_practice_questions_100.md#q50--thinking--fastapi-lifespan)

---

## Where We Are

You know how to define routes, validate request bodies with Pydantic, connect a database,
and wire up dependency injection. That covers 80% of what most FastAPI services need.

The remaining 20% is what separates a simple CRUD API from a production system that
handles real-time connections, large file transfers, background jobs, and thousands of
requests per second without falling over.

This chapter covers seven features you will reach for once your API starts doing serious
work.

---

## 1. WebSockets — Real-Time Bidirectional Communication

HTTP is request-response. The client sends a request, the server sends a response, the
connection closes. There is no way for the server to push data to a client that isn't
asking.

WebSockets fix this. After an initial HTTP handshake, the connection upgrades to a
persistent, bidirectional channel. Either side can send messages at any time. This is
what powers chat applications, live dashboards, collaborative editing, and anything that
needs sub-second updates.

### The Connection Manager Pattern

When you have multiple WebSocket clients connected simultaneously, you need something to
track them and coordinate broadcasts. The `ConnectionManager` is the standard pattern:

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A user disconnected")
```

Walk through what happens here:

1. Client connects to `/ws/chat` — the HTTP connection upgrades to WebSocket
2. `manager.connect()` accepts the handshake and adds the socket to the active list
3. The `while True` loop waits for messages from this client
4. Each message is broadcast to every connected client
5. `WebSocketDisconnect` is raised when the client closes the connection — we clean up and
   notify others

### Chat With Username Tracking

Real chat needs to know who's who. Pass data in the URL or headers during the handshake:

```python
from fastapi import WebSocket, WebSocketDisconnect, Query
from typing import Dict

class ChatManager:
    def __init__(self):
        # Map of websocket -> username
        self.connections: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.connections[websocket] = username
        await self.broadcast(f"[{username} joined]", exclude=websocket)

    def disconnect(self, websocket: WebSocket) -> str:
        username = self.connections.pop(websocket, "unknown")
        return username

    async def broadcast(self, message: str, exclude: WebSocket = None):
        for ws in self.connections:
            if ws != exclude:
                await ws.send_text(message)


chat = ChatManager()


@app.websocket("/ws/chat/{username}")
async def chat_endpoint(websocket: WebSocket, username: str):
    await chat.connect(websocket, username)
    try:
        while True:
            message = await websocket.receive_text()
            await chat.broadcast(f"{username}: {message}")
    except WebSocketDisconnect:
        left = chat.disconnect(websocket)
        await chat.broadcast(f"[{left} left]")
```

### Sending JSON Over WebSockets

Text is fine for chat. For structured data, send JSON:

```python
import json
from datetime import datetime

@app.websocket("/ws/live-data")
async def live_data(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive a JSON command from the client
            raw = await websocket.receive_text()
            command = json.loads(raw)

            if command["action"] == "subscribe":
                symbol = command["symbol"]
                # Stream price updates
                price = await get_price(symbol)  # your data source
                await websocket.send_text(json.dumps({
                    "symbol": symbol,
                    "price": price,
                    "timestamp": datetime.utcnow().isoformat()
                }))
    except WebSocketDisconnect:
        pass
```

### What WebSockets Are Not Good For

WebSockets are stateful — each connection is held open and tied to one server process.
This makes horizontal scaling complicated. If you have four app servers and user A is
connected to server 1 but user B is connected to server 3, a broadcast from B won't
reach A unless you add a message broker (Redis pub/sub, for example) between servers.

Use WebSockets when you genuinely need server-push. For polling patterns where the client
checks for updates every few seconds, Server-Sent Events (SSE) are simpler and work over
plain HTTP.

---

## 2. File Uploads — Handling Binary Data

APIs that deal with user avatars, document uploads, video submissions, or any binary
content need to handle file uploads correctly. FastAPI uses `UploadFile` for this.

### Basic Upload

```python
from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload/photo")
async def upload_photo(file: UploadFile = File(...)):
    # 1. Validate content type
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(400, f"Only JPEG, PNG, or WebP allowed. Got: {file.content_type}")

    # 2. Validate file size — read into memory only if small
    contents = await file.read()
    if len(contents) > 5_000_000:  # 5 MB
        raise HTTPException(413, "File too large. Maximum size is 5 MB.")

    # 3. Save to disk (reset pointer after reading)
    await file.seek(0)
    save_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"filename": file.filename, "size": len(contents), "url": f"/files/{file.filename}"}
```

### Upload to S3

Saving to local disk doesn't survive server restarts or scale to multiple instances.
Upload to S3 instead:

```python
import boto3
from fastapi import UploadFile, File, HTTPException
import uuid

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name="us-east-1"
)
BUCKET = "my-app-uploads"


@app.post("/upload/photo")
async def upload_photo(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(400, "Only JPEG/PNG allowed")

    # Generate a unique key to avoid collisions
    ext = file.filename.rsplit(".", 1)[-1]
    s3_key = f"photos/{uuid.uuid4()}.{ext}"

    # Stream directly to S3 — no need to load entire file into memory
    s3.upload_fileobj(
        file.file,
        BUCKET,
        s3_key,
        ExtraArgs={"ContentType": file.content_type}
    )

    cdn_url = f"https://cdn.example.com/{s3_key}"
    return {"url": cdn_url, "key": s3_key}
```

### Multiple File Upload

```python
from typing import List

@app.post("/upload/gallery")
async def upload_gallery(files: List[UploadFile] = File(...)):
    if len(files) > 10:
        raise HTTPException(400, "Maximum 10 files per upload")

    results = []
    for file in files:
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(400, f"{file.filename}: only JPEG/PNG allowed")

        s3_key = f"gallery/{uuid.uuid4()}.{file.filename.rsplit('.', 1)[-1]}"
        s3.upload_fileobj(file.file, BUCKET, s3_key)
        results.append({"filename": file.filename, "url": f"https://cdn.example.com/{s3_key}"})

    return {"uploaded": len(results), "files": results}
```

### File Upload With Form Data

Sometimes you need both file and form fields in the same request. Use `Form` alongside
`File`:

```python
from fastapi import Form, File, UploadFile

@app.post("/upload/document")
async def upload_document(
    title: str = Form(...),
    description: str = Form(default=""),
    file: UploadFile = File(...)
):
    # Note: when mixing File and Form, you cannot use JSON body
    # The request must be multipart/form-data
    s3_key = f"documents/{uuid.uuid4()}_{file.filename}"
    s3.upload_fileobj(file.file, BUCKET, s3_key)

    return {
        "title": title,
        "description": description,
        "url": f"https://cdn.example.com/{s3_key}"
    }
```

---

## 3. Streaming Responses — Don't Buffer What You Can Stream

When a response is large — a CSV export, a generated PDF, a log file, live event data —
loading it entirely into memory before sending is wasteful. Streaming responses send data
to the client as it's generated or read.

### Server-Sent Events (SSE) for Live Updates

SSE is a lightweight alternative to WebSockets for one-directional server-to-client
streaming. It works over plain HTTP and reconnects automatically if the connection drops.

```python
from fastapi.responses import StreamingResponse
import asyncio


@app.get("/stream/events")
async def stream_events():
    async def generate():
        for i in range(100):
            # SSE format: "data: <payload>\n\n"
            yield f"data: {{'count': {i}, 'timestamp': '{asyncio.get_event_loop().time():.2f}'}}\n\n"
            await asyncio.sleep(0.5)
        yield "data: {\"done\": true}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # disable nginx buffering
        }
    )
```

The client connects with `EventSource` in the browser:

```javascript
const source = new EventSource("/stream/events");
source.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
};
```

### Streaming Large File Downloads

Never load a 500 MB file into memory to serve a download. Read and stream it in chunks:

```python
import os
from fastapi.responses import StreamingResponse


@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"files/{filename}"

    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found")

    file_size = os.path.getsize(file_path)

    def iter_file():
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):  # 64 KB chunks
                yield chunk

    return StreamingResponse(
        iter_file(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(file_size)
        }
    )
```

### Streaming a Database Export as CSV

Generating a CSV from a database query? Stream rows as they come from the database rather
than building the entire CSV in memory first:

```python
import csv
import io
from sqlalchemy.orm import Session


@app.get("/export/users.csv")
async def export_users_csv(db: Session = Depends(get_db)):
    def generate_csv():
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        writer.writerow(["id", "name", "email", "created_at"])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        # Stream rows in batches of 1000
        offset = 0
        batch_size = 1000
        while True:
            batch = db.query(User).offset(offset).limit(batch_size).all()
            if not batch:
                break
            for user in batch:
                writer.writerow([user.id, user.name, user.email, user.created_at])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)
            offset += batch_size

    return StreamingResponse(
        generate_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users.csv"}
    )
```

---

## 4. Background Tasks With Celery — Offload Heavy Work

FastAPI has built-in `BackgroundTasks` for lightweight post-response work (sending an
email after registration, writing an audit log). But if the work is genuinely heavy —
video transcoding, sending bulk notifications, generating large reports — you need a
proper task queue.

Celery is the standard Python choice: a distributed task queue that runs jobs
asynchronously on separate worker processes, backed by Redis or RabbitMQ as a broker.

> 📝 **Practice:** [Q41 · fastapi-background-tasks](../api_practice_questions_100.md#q41--normal--fastapi-background-tasks)

### Setting Up Celery

```python
# tasks.py
from celery import Celery
import time

celery = Celery(
    "tasks",
    broker="redis://localhost:6379/0",   # Redis as the message broker
    backend="redis://localhost:6379/1"  # Redis also stores results
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,  # let us query "started" status
)


@celery.task(bind=True)
def process_video(self, video_id: int):
    """Long-running task: transcoding, thumbnail generation, etc."""
    try:
        # Simulate work
        for step in range(10):
            time.sleep(2)
            # Update progress — clients can poll for this
            self.update_state(
                state="PROGRESS",
                meta={"current": step + 1, "total": 10, "step": f"Transcoding pass {step + 1}"}
            )
        return {"video_id": video_id, "status": "complete", "url": f"https://cdn.example.com/videos/{video_id}.mp4"}
    except Exception as exc:
        # Retry up to 3 times with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries, max_retries=3)


@celery.task
def send_bulk_email(recipient_ids: list, template_id: str):
    """Send an email to a list of users."""
    for user_id in recipient_ids:
        user = fetch_user(user_id)
        send_email(user.email, template_id)
    return {"sent": len(recipient_ids)}
```

### Wiring Celery Into FastAPI Routes

```python
# main.py
from fastapi import FastAPI
from tasks import process_video, send_bulk_email, celery

app = FastAPI()


@app.post("/videos/{video_id}/process")
def trigger_video_processing(video_id: int):
    """Queue the video processing job and return immediately."""
    task = process_video.delay(video_id)
    return {
        "task_id": task.id,
        "status": "queued",
        "poll_url": f"/tasks/{task.id}"
    }


@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    """Poll for task progress and result."""
    task = celery.AsyncResult(task_id)

    if task.state == "PENDING":
        return {"status": "pending", "task_id": task_id}

    if task.state == "PROGRESS":
        return {
            "status": "in_progress",
            "task_id": task_id,
            "progress": task.info  # the meta dict from update_state()
        }

    if task.state == "SUCCESS":
        return {
            "status": "complete",
            "task_id": task_id,
            "result": task.result
        }

    if task.state == "FAILURE":
        return {
            "status": "failed",
            "task_id": task_id,
            "error": str(task.result)
        }

    return {"status": task.state, "task_id": task_id}
```

### Running the Worker

```bash
# In a separate terminal (or container):
celery -A tasks worker --loglevel=info --concurrency=4

# With flower for a web UI to monitor tasks:
celery -A tasks flower --port=5555
```

The pattern here is important: the FastAPI route returns in milliseconds with a task ID.
The client polls `/tasks/{task_id}` to check progress. The actual work happens in a
separate process that can take as long as it needs. Your HTTP server stays responsive.

---

## 5. Caching With Redis — Stop Hitting the Database for the Same Data

The first time you serve `/products/42`, you query the database. The second time — and the
ten thousandth time — the data is identical. Why hit the database every time?

A cache stores recent query results and serves them for subsequent identical requests.
Redis is fast (sub-millisecond), simple, and the standard choice.

### Cache-Aside Pattern

The most common caching pattern: try the cache first; on a miss, fetch from the database
and populate the cache.

```python
import redis
import json
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

app = FastAPI()
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


@app.get("/products/{product_id}")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    cache_key = f"product:{product_id}"

    # 1. Try cache first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. Cache miss — fetch from database
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")

    # 3. Serialize and cache with a TTL
    product_data = {
        "id": product.id,
        "name": product.name,
        "price": float(product.price),
        "category": product.category
    }
    redis_client.setex(cache_key, 300, json.dumps(product_data))  # 300 second TTL

    return product_data
```

### Cache Invalidation — The Hard Part

When a product is updated, the cached version is stale. Delete it:

```python
@app.patch("/products/{product_id}")
async def update_product(
    product_id: int,
    update: ProductUpdate,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Not found")

    for field, value in update.dict(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    # Invalidate the cache for this product
    redis_client.delete(f"product:{product_id}")

    return product
```

### Caching a Computed Result — Leaderboard Example

Some data is expensive to compute but doesn't change frequently. Cache the computation:

```python
@app.get("/leaderboard")
async def get_leaderboard(db: Session = Depends(get_db)):
    cache_key = "leaderboard:top50"

    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Expensive aggregation query
    scores = (
        db.query(User.id, User.name, func.sum(Score.points).label("total"))
        .join(Score)
        .group_by(User.id)
        .order_by(desc("total"))
        .limit(50)
        .all()
    )

    result = [{"rank": i + 1, "user_id": s.id, "name": s.name, "score": s.total}
              for i, s in enumerate(scores)]

    # Cache for 60 seconds — leaderboard can be slightly stale
    redis_client.setex(cache_key, 60, json.dumps(result))
    return result
```

---

## 6. Rate Limiting With Redis

Rate limiting protects your API from abuse — whether accidental (a client in an infinite
loop) or intentional (a DDoS or credential-stuffing attack). Without it, one misbehaving
client can take down your service for everyone.

### Fixed Window Rate Limiter

```python
from fastapi import Request, HTTPException, Depends
import time


async def rate_limit(
    request: Request,
    limit: int = 100,
    window: int = 60
):
    """
    Dependency that limits to `limit` requests per `window` seconds per IP.
    Raises 429 if exceeded.
    """
    # Identify the caller — use user ID in authenticated routes instead of IP
    identifier = request.client.host
    window_key = int(time.time() // window)
    key = f"rate:{identifier}:{window_key}"

    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, window * 2)  # expire after 2 windows for safety

    # Set rate limit headers on the response regardless of pass/fail
    remaining = max(0, limit - current)
    reset_at = (window_key + 1) * window
    request.state.rate_limit_headers = {
        "X-RateLimit-Limit": str(limit),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(reset_at)
    }

    if current > limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {reset_at - int(time.time())} seconds.",
            headers={"Retry-After": str(reset_at - int(time.time()))}
        )


# Apply to a single route:
@app.get("/api/search", dependencies=[Depends(rate_limit)])
async def search(q: str):
    return {"query": q, "results": [...]}
```

### Tighter Limits on Expensive Endpoints

Not all endpoints cost the same. Apply tighter limits to costly ones:

```python
from functools import partial

# 10 requests per minute for ML inference (expensive)
tight_rate_limit = partial(rate_limit, limit=10, window=60)

# 1000 requests per minute for static reads (cheap)
loose_rate_limit = partial(rate_limit, limit=1000, window=60)


@app.post("/ai/generate", dependencies=[Depends(tight_rate_limit)])
async def ai_generate(prompt: str):
    result = await call_openai(prompt)
    return {"result": result}


@app.get("/products", dependencies=[Depends(loose_rate_limit)])
async def list_products():
    return cached_product_list()
```

### Propagating Rate Limit Headers to Responses

Use a middleware to attach the headers from each request to the final response:

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        headers = getattr(request.state, "rate_limit_headers", {})
        for key, value in headers.items():
            response.headers[key] = value
        return response


app.add_middleware(RateLimitHeaderMiddleware)
```

---

## 7. Async vs Sync — Choosing the Right Function Signature

FastAPI supports both `async def` and `def` routes. Choosing the wrong one can silently
hurt performance.

### The Rule

**Use `async def` when** your handler does I/O that has an async interface: async
database drivers, `httpx` for async HTTP calls, async file I/O, Redis with `aioredis`.

**Use `def` when** your handler calls synchronous libraries (like standard SQLAlchemy
with synchronous sessions) or does CPU-bound work.

FastAPI is smart about both:
- `async def` routes run on the event loop directly — no thread overhead
- `def` routes run in a thread pool — so they don't block the event loop

```python
# CORRECT: async database driver (asyncpg, databases library, SQLAlchemy async)
@app.get("/users/{user_id}")
async def get_user_async(user_id: int):
    user = await async_db.fetch_one(
        "SELECT * FROM users WHERE id = :id", values={"id": user_id}
    )
    return user


# CORRECT: standard synchronous SQLAlchemy
@app.get("/users/{user_id}")
def get_user_sync(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    return user


# WRONG: calling a blocking sync operation inside async def
# This blocks the event loop and freezes all other requests
@app.get("/users/{user_id}")
async def get_user_broken(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()  # sync — blocks event loop!
    return user
```

### Mixing Async and Sync in the Same App

You will almost certainly have both in the same application. That is fine. FastAPI
handles each correctly at the router level.

```python
import httpx
import asyncio


# Async: making an outbound HTTP call (use httpx async client)
@app.get("/weather/{city}")
async def get_weather(city: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}")
        return resp.json()


# Sync: CPU-bound work (running in a thread pool is fine)
@app.post("/process/image")
def process_image(file: UploadFile = File(...)):
    from PIL import Image
    import io
    img = Image.open(file.file)
    img = img.resize((800, 600))
    output = io.BytesIO()
    img.save(output, format="JPEG")
    return {"size": output.tell()}


# Explicitly running sync code in a thread pool from async context:
@app.get("/expensive-sync")
async def expensive_sync_route():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, some_blocking_function)
    return {"result": result}
```

### Quick Decision Guide

```
Your handler calls...                        Use
─────────────────────────────────────────────────────
async DB driver (asyncpg, aioredis)         async def
httpx AsyncClient                           async def
asyncio.sleep, websocket operations         async def
Standard SQLAlchemy (Session)               def
requests library (sync HTTP)                def
PIL, numpy, pandas (CPU work)               def
```

If you are unsure, use `def`. FastAPI will run it in a thread pool, which is safe.
Using `async def` with sync blocking calls is worse than using `def`.

---

## Putting It Together — A Real-World Service Structure

A FastAPI service that uses all seven features looks roughly like this:

```
app/
├── main.py               ← FastAPI app, routes, middleware
├── tasks.py              ← Celery task definitions
├── dependencies.py       ← get_db, rate_limit, auth dependencies
├── routers/
│   ├── users.py          ← user CRUD routes (sync, SQLAlchemy)
│   ├── uploads.py        ← file upload routes (async, S3)
│   ├── streaming.py      ← SSE and download routes
│   └── websockets.py     ← WebSocket routes
├── cache.py              ← Redis client, cache helpers
└── models.py             ← SQLAlchemy models
```

The boundaries are clean: routes that do DB work use sync SQLAlchemy; routes that call
external services use async httpx; uploads stream directly to S3; heavy work gets queued
to Celery. Each piece uses the right tool for its job.

---

## Summary

```
WebSockets
  → Persistent bidirectional connections
  → ConnectionManager tracks active sockets
  → Use WebSocketDisconnect to handle clean disconnects
  → Use SSE for one-directional streaming (simpler, HTTP-native)

File Uploads
  → UploadFile + File(...) for multipart uploads
  → Always validate content_type and size before accepting
  → Stream directly to S3 — don't load large files into memory
  → Mix File and Form for metadata + file in one request

Streaming Responses
  → StreamingResponse with a generator function
  → SSE format: "data: <payload>\n\n" with media_type="text/event-stream"
  → Stream large downloads in chunks (65 KB default chunk size)
  → Stream database exports in batches — never SELECT all rows into memory

Background Tasks (Celery)
  → Route returns immediately with task_id
  → Worker processes the job in a separate process
  → Client polls /tasks/{task_id} for status and result
  → Use for: video processing, bulk email, report generation

Caching (Redis)
  → Cache-aside: try cache → miss → DB → populate cache
  → Always set a TTL — stale cache is better than no cache
  → Invalidate cache on write (delete the key)
  → Cache expensive computed results, not just DB rows

Rate Limiting (Redis)
  → INCR + EXPIRE per identifier + time window
  → Per-IP for unauthenticated, per-user for authenticated
  → Return X-RateLimit-* headers on every response
  → Tighter limits on expensive endpoints

Async vs Sync
  → async def: for async DB drivers, httpx, websockets
  → def: for SQLAlchemy sync, PIL, pandas, requests
  → Never call blocking sync code inside async def
  → FastAPI runs def routes in a thread pool automatically
```

---

## 📝 Practice Questions

> 📝 **Practice:** [Q93 · predict-dependency-chain](../api_practice_questions_100.md#q93--logical--predict-dependency-chain)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← FastAPI & Databases](../07_fastapi/database_guide.md) &nbsp;|&nbsp; **Next:** [API Versioning →](../08_versioning_standards/versioning_strategy.md)

**Related Topics:** [FastAPI Core Guide](../07_fastapi/core_guide.md) · [WebSockets & Real-Time APIs](../17_websockets/realtime_apis.md) · [Production Deployment](../12_production_deployment/deployment_guide.md) · [OpenTelemetry](../19_opentelemetry/opentelemetry_guide.md)
