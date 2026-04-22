# ⚡ Cheatsheet: WebSockets & Real-Time APIs

---

## Learning Priority

**Must Learn** — core concepts for any real-time feature:
WebSocket handshake · connection lifecycle · REST vs WebSocket vs SSE comparison

**Should Learn** — needed for production real-time:
Python server/client snippets · broadcast pattern · ping/pong keepalive · authentication

**Good to Know** — scaling real-time systems:
Redis pub/sub for multi-instance broadcast · connection state management · backpressure

**Reference** — look up when needed:
RFC 6455 (WebSocket protocol) · Socket.IO protocol · STOMP over WebSocket

---

## WebSocket Handshake Headers

```
# Client → Server (HTTP Upgrade request)
GET /ws HTTP/1.1
Host: api.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==   # random base64 nonce
Sec-WebSocket-Version: 13
Sec-WebSocket-Protocol: chat, superchat         # optional: subprotocol negotiation
Origin: https://app.example.com                 # checked for CORS on the server

# Server → Client (101 Switching Protocols)
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=  # SHA-1 of key + GUID
Sec-WebSocket-Protocol: chat                          # chosen subprotocol
```

After the 101 response, the HTTP connection is hijacked — it is now a persistent bidirectional TCP channel.

---

## Connection Lifecycle Events

| Event | Fires When |
|-------|-----------|
| `open` | Handshake complete, connection established |
| `message` | A message (text or binary frame) is received |
| `error` | A connection error occurs |
| `close` | Connection is closed (either side) |

```python
# Close codes (RFC 6455)
1000  # Normal closure
1001  # Going away (server shutdown or browser navigating away)
1002  # Protocol error
1003  # Unsupported data type
1006  # Abnormal closure (no close frame sent — connection dropped)
1007  # Invalid frame payload data
1008  # Policy violation
1009  # Message too large
1011  # Internal server error
```

---

## Python WebSocket Server (FastAPI)

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict
import json

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        # room_id → list of websocket connections
        self.rooms: Dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.rooms:
            self.rooms[room_id] = []
        self.rooms[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.rooms:
            self.rooms[room_id].remove(websocket)
            if not self.rooms[room_id]:
                del self.rooms[room_id]

    async def send_personal(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict, room_id: str):
        if room_id not in self.rooms:
            return
        disconnected = []
        for ws in self.rooms[room_id]:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.rooms[room_id].remove(ws)

manager = ConnectionManager()

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Echo to all in room
            await manager.broadcast(
                {"from": data.get("user"), "text": data.get("text")},
                room_id
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast({"system": "A user disconnected"}, room_id)
```

---

## Python WebSocket Client

```python
import asyncio
import websockets
import json

async def ws_client():
    uri = "ws://localhost:8000/ws/room-42"

    # Optional: include auth token in headers
    headers = {"Authorization": "Bearer your-jwt-token"}

    async with websockets.connect(uri, extra_headers=headers) as websocket:
        # Send a message
        await websocket.send(json.dumps({"user": "alice", "text": "hello"}))

        # Receive messages
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data}")

            if data.get("text") == "bye":
                break

asyncio.run(ws_client())
```

```python
# With reconnect logic
async def ws_client_with_reconnect(uri: str, max_retries: int = 5):
    retries = 0
    backoff = 1.0
    while retries < max_retries:
        try:
            async with websockets.connect(uri) as ws:
                retries = 0  # reset on successful connection
                async for message in ws:
                    await handle_message(json.loads(message))
        except (websockets.ConnectionClosed, OSError) as e:
            retries += 1
            wait = backoff * (2 ** retries)
            print(f"Connection lost, retry {retries}/{max_retries} in {wait}s: {e}")
            await asyncio.sleep(wait)
    raise RuntimeError("Max retries exceeded")
```

---

## Ping/Pong Keepalive

```
# WebSocket protocol defines ping/pong control frames
# Server sends ping → client must respond with pong automatically
# If no pong in timeout window → close connection (dead client)

# Why needed: TCP connections can stay "alive" at the OS level even when
# the client is gone (behind NAT, crashed browser, etc.)
```

```python
# FastAPI WebSocket — send periodic pings
import asyncio
from fastapi import WebSocket

async def keepalive(websocket: WebSocket, interval: int = 30):
    """Send ping every N seconds to detect dead connections."""
    while True:
        await asyncio.sleep(interval)
        try:
            await websocket.send_json({"type": "ping"})
        except Exception:
            break  # connection is dead

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    keepalive_task = asyncio.create_task(keepalive(websocket))
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "pong":
                continue  # client is alive
            await handle_message(data)
    except WebSocketDisconnect:
        pass
    finally:
        keepalive_task.cancel()
```

---

## Broadcast Pattern with Redis Pub/Sub (Multi-Instance)

```python
# Problem: multiple server instances each hold their own connections.
# Broadcasting via ConnectionManager only reaches clients on the SAME instance.
# Fix: use Redis pub/sub as the shared message bus.

import redis.asyncio as aioredis
import asyncio

redis_client = aioredis.from_url("redis://localhost:6379")

# Publisher — any server instance can publish to a room
async def publish_to_room(room_id: str, message: dict):
    await redis_client.publish(f"room:{room_id}", json.dumps(message))

# Subscriber — runs in each server instance, routes to local connections
async def subscribe_and_forward(room_id: str):
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(f"room:{room_id}")
    async for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            # Forward to all local connections in this room
            await local_manager.broadcast(data, room_id)
```

---

## WebSocket Authentication Patterns

```python
# Option 1: Token in query parameter (simple, but visible in logs)
@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket, token: str = Query(None)):
    user = verify_jwt(token)
    if not user:
        await websocket.close(code=1008, reason="Unauthorized")
        return
    await websocket.accept()
    # ...

# Option 2: Token in first message after connect
@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Wait for auth message
    auth_msg = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
    if auth_msg.get("type") != "auth":
        await websocket.close(code=1008, reason="Expected auth message")
        return
    user = verify_jwt(auth_msg.get("token"))
    if not user:
        await websocket.close(code=1008, reason="Invalid token")
        return
    # Proceed with authenticated connection
```

---

## REST vs WebSocket vs SSE Comparison

| Dimension | REST | WebSocket | SSE |
|-----------|------|-----------|-----|
| Protocol | HTTP | TCP (after HTTP upgrade) | HTTP |
| Direction | Request/response | Bidirectional | Server → client only |
| Connection | New per request | Persistent | Persistent |
| Browser support | Native | Native | Native |
| Load balancer friendly | Yes | Needs sticky sessions or Redis | Yes |
| Auto-reconnect | Client handles | Client handles | Built-in |
| Multiplexing | HTTP/2 | No | No |
| Binary data | Base64 or multipart | Native binary frames | Text only |
| Message format | Any (JSON, etc.) | Any | Text (with `data:` prefix) |
| Authentication | Standard headers | Query param or first message | Standard headers |
| Firewall friendly | Yes | Usually (port 443) | Yes |
| Best for | CRUD operations | Chat, gaming, collaboration | Notifications, live feeds |

---

## When to Use / Avoid

| Technology | Use When | Avoid When |
|------------|----------|------------|
| WebSocket | Bidirectional real-time (chat, collaborative editing, gaming) | One-way server push (SSE is simpler) |
| SSE | Server push to browser (notifications, live feeds, progress) | Bidirectional — use WebSocket |
| Long polling | Simple job status, infrequent updates, no SSE support | High-frequency updates (use SSE/WS) |
| Short polling | Debugging/testing, extremely simple cases | Any production real-time feature |
| REST | All non-real-time operations | Anything needing <100ms push latency |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← API Design Patterns](../16_api_design_patterns/cheatsheet.md) &nbsp;|&nbsp; **Next:** [Real-World APIs →](../18_real_world_apis/cheatsheet.md)

**Related Topics:** [API Design Patterns](../16_api_design_patterns/) · [Real-World APIs](../18_real_world_apis/) · [API Performance](../09_api_performance_scaling/)
