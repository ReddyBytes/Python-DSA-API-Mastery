<a id="top"></a>

# WebSockets — When the Server Needs to Talk First

> Sindhu builds live collaboration tools at a Telugu startup — whiteboards where ten designers draw simultaneously, chat systems where typing indicators flash in real time. She learned early: HTTP is a polite letter exchange, but WebSockets are a phone call that never hangs up.

<a id="toc"></a>

## Table of Contents

- [1. The Fundamental Limitation of HTTP](#1-the-fundamental-limitation-of-http)
- [2. Learning Priority](#2-learning-priority)
- [3. The Workarounds And Why They Are Painful](#3-the-workarounds-and-why-they-are-painful)
  - [Polling — Are We There Yet](#polling-are-we-there-yet)
  - [Long Polling — I Will Wait Right Here](#long-polling-i-will-wait-right-here)
  - [Server-Sent Events — One-Way Push](#server-sent-events-one-way-push)
- [4. Enter WebSockets — The Phone Call Model](#4-enter-websockets-the-phone-call-model)
- [5. The Handshake — How HTTP Becomes a WebSocket](#5-the-handshake-how-http-becomes-a-websocket)
- [6. Python WebSocket Example](#6-python-websocket-example)
- [7. Real-World Use Cases](#7-real-world-use-cases)
- [8. The Hard Part — Scaling WebSocket Connections](#8-the-hard-part-scaling-websocket-connections)
  - [The Sticky Session Problem](#the-sticky-session-problem)
  - [The Real Solution — Redis Pub/Sub](#the-real-solution-redis-pubsub)
- [9. WebSockets vs SSE vs Long Polling — The Comparison](#9-websockets-vs-sse-vs-long-polling-the-comparison)
- [10. WebSocket Security](#10-websocket-security)
- [11. Summary](#11-summary)

[Back to Top](#top)

<a id="1-the-fundamental-limitation-of-http"></a>

## 1. The Fundamental Limitation of HTTP

Everything you've learned so far — REST, GraphQL, gRPC — shares one characteristic:
the client initiates. Always. The server never speaks first. The server sits there,
waiting, until a client knocks.

That's not a flaw. It's a deliberate design choice that makes HTTP simple, scalable,
and stateless. But it creates a real constraint when you need the opposite:
when something happens on the server and you need to tell the client immediately.

Sindhu thinks of it like this: imagine you ordered biryani for delivery. With HTTP,
the only way to know if it arrived is to keep walking to the door and checking.
The delivery person will never ring the bell — you have to look.

Think about a few scenarios:

- You're tracking a food delivery on your phone. Your order was just picked up.
  How does your app know?

- You're playing a browser-based multiplayer game. Another player just moved.
  How does your screen update?

- You're watching a live stock ticker. AAPL just jumped $3. How does the price
  change without you refreshing the page?

With HTTP alone, there's only one way: the client has to ask.

[Back to Top](#top)

<a id="2-learning-priority"></a>

## 2. Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
WebSocket handshake, send/receive, connection lifecycle

**Should Learn** — Important for real projects:
broadcast patterns, reconnection

**Good to Know** — Useful in specific situations:
Socket.io

**Reference** — Know it exists, look up syntax when needed:
WebRTC differences

[Back to Top](#top)

<a id="3-the-workarounds-and-why-they-are-painful"></a>

## 3. The Workarounds And Why They Are Painful

Before WebSockets, developers had three imperfect approaches. Sindhu tried all
three before switching — here is what she learned.

<a id="polling-are-we-there-yet"></a>

**Polling — Are We There Yet**

The client asks the server every N seconds: "Did anything change?"

```
Client                              Server
  |                                   |
  |  GET /order/42/status             |
  |  ────────────────────────────>    |  No change.
  |  {status: "preparing"}            |
  |  <────────────────────────────    |
  |                                   |
  |  (wait 5 seconds)                 |
  |                                   |
  |  GET /order/42/status             |
  |  ────────────────────────────>    |  No change.
  |  {status: "preparing"}            |
  |  <────────────────────────────    |
  |                                   |
  |  (wait 5 seconds)                 |
  |                                   |
  |  GET /order/42/status             |
  |  ────────────────────────────>    |  Changed!
  |  {status: "out for delivery"}     |
  |  <────────────────────────────    |
```

Simple. Works with any HTTP server. But the problems are obvious:

- Every client is hammering the server constantly, even when nothing is happening.
  1000 clients polling every 5 seconds = 200 requests per second of pure overhead.
- Updates are delayed by up to the poll interval. If something happens 1 second after
  a poll, you don't know for 4 more seconds.
- It doesn't scale. The more clients, the more wasted requests.

<a id="long-polling-i-will-wait-right-here"></a>

**Long Polling — I Will Wait Right Here**

A cleverer approach: the client makes a request, but the server holds the connection
open and doesn't respond until it has something to say. When it does, it responds,
and the client immediately opens a new request.

```
Client                              Server
  |                                   |
  |  GET /order/42/updates            |
  |  ────────────────────────────>    |  [holds connection open]
  |                                   |  [holds connection open]
  |                                   |  [holds connection open]
  |                                   |  [order status changed!]
  |  {status: "out for delivery"}     |
  |  <────────────────────────────    |
  |                                   |
  |  GET /order/42/updates            |  (immediately re-opens)
  |  ────────────────────────────>    |  [holds connection open]
  |                                   |  ...
```

Better — near-real-time with no wasted empty responses. But still painful:
- Servers have to hold thousands of open connections. Connection state is resource-heavy.
- HTTP/1.1 wasn't designed for this. Each "waiting" connection ties up a socket.
- Error handling is tricky. What if the connection drops mid-wait?
- Feels like a hack because it is.

<a id="server-sent-events-one-way-push"></a>

**Server-Sent Events (SSE) — One-Way Push**

SSE is a proper HTTP standard for server-to-client push. The client opens one HTTP
connection, and the server streams events down it indefinitely.

```
Client                              Server
  |                                   |
  |  GET /order/42/stream             |
  |  Accept: text/event-stream        |
  |  ────────────────────────────>    |
  |                                   |  [connection stays open]
  |  data: {"status": "preparing"}    |
  |  <────────────────────────────    |
  |                                   |
  |  data: {"status": "picked up"}    |
  |  <────────────────────────────    |
  |                                   |
  |  data: {"status": "delivered"}    |
  |  <────────────────────────────    |
```

SSE is genuinely good for one-directional use cases — live feeds, log streaming,
progress updates. It's simple, works over standard HTTP, and browsers support it
natively.

But it's one-way. The server pushes; the client receives. If the client needs to
send something back, it has to open a separate HTTP request. For chat apps, games,
collaborative editing — anything where both sides send messages — SSE isn't enough.

Sindhu used SSE for her deployment progress dashboard — perfect fit. But when she
built the collaborative whiteboard, she needed both directions. That meant WebSockets.

[Back to Top](#top)

<a id="4-enter-websockets-the-phone-call-model"></a>

## 4. Enter WebSockets — The Phone Call Model

HTTP is like sending letters. You write a letter, send it, wait for a reply.
The other party can't just ring you up in the middle of the night.

WebSockets are like a phone call. Once connected, both parties can speak whenever
they want. The connection stays open. Either side sends, the other side receives,
immediately.

```
HTTP (request-response):

  Client ──letter──> Server
  Client <──letter── Server
  [connection closes]
  [to talk again, write another letter]


WebSocket (full-duplex):

  Client ──────────── Server
         <──────────>
  [persistent connection]
  [either side can send at any time]
  [messages flow both directions simultaneously]
```

This is called **full-duplex** communication — both sides can transmit simultaneously
over a single persistent connection.

Sindhu explains it to her junior developers: "REST is like texting — you send, you
wait for a reply, maybe they reply in 30 seconds. WebSockets are like being on a
phone call — you both talk whenever you want, no waiting."

[Back to Top](#top)

<a id="5-the-handshake-how-http-becomes-a-websocket"></a>

## 5. The Handshake — How HTTP Becomes a WebSocket

This is genuinely interesting to understand. WebSockets don't start as WebSockets.
They start as a regular HTTP request — the same kind your browser makes every day —
and then upgrade to the WebSocket protocol.

The upgrade handshake looks like this:

```
Step 1: Client sends an HTTP upgrade request

  GET /chat HTTP/1.1
  Host: chat.example.com
  Upgrade: websocket
  Connection: Upgrade
  Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==
  Sec-WebSocket-Version: 13


Step 2: Server agrees and completes the upgrade

  HTTP/1.1 101 Switching Protocols
  Upgrade: websocket
  Connection: Upgrade
  Sec-WebSocket-Accept: HSmrc0sMlYUkAGmm5OPpG2HaGWk=
```

Status code `101 Switching Protocols` is the only time you'll see a 1xx status code
in the wild. It means: "I understand you want to switch protocols. Done. We're
speaking WebSocket now."

After the handshake:
- The underlying TCP connection stays open
- HTTP is done — no more HTTP requests on this socket
- Both sides communicate using the WebSocket protocol: lightweight binary frames
- Either side can send a frame at any time
- The connection stays alive until explicitly closed by either side (or the network drops)

The `Sec-WebSocket-Key` / `Sec-WebSocket-Accept` exchange is a security mechanism
to prevent HTTP caches from accidentally treating WebSocket traffic as cacheable
HTTP responses. It's not actual authentication — that's done separately.

```
Sindhu's mental model of the handshake:

  Browser: "Hey server, I'd like to upgrade this HTTP connection to WebSocket."
  Server:  "Sure, I support that. Here's proof I understand your request."
  Both:    "Great. HTTP is done. We're on WebSocket now. Talk freely."

  ┌──────────┐     HTTP GET + Upgrade     ┌──────────┐
  │  Client  │ ─────────────────────────> │  Server  │
  │          │ <───────────────────────── │          │
  │          │     101 Switching          │          │
  │          │                            │          │
  │          │ ═══ WebSocket Frames ════> │          │
  │          │ <═══ WebSocket Frames ════ │          │
  └──────────┘                            └──────────┘
```

[Back to Top](#top)

<a id="6-python-websocket-example"></a>

## 6. Python WebSocket Example

Let's build a simple chat server. When one client sends a message, all connected
clients receive it. This is exactly what Sindhu built first when learning WebSockets.

```bash
pip install websockets fastapi uvicorn
```

**Simple broadcast server** (`chat_server.py`):
```python
import asyncio
import websockets
import json
from datetime import datetime

# Track all connected clients
connected_clients: set = set()

async def handle_connection(websocket):
    # Register this client
    connected_clients.add(websocket)
    client_addr = websocket.remote_address
    print(f"New connection from {client_addr}. Total: {len(connected_clients)}")

    try:
        async for raw_message in websocket:
            # Parse incoming message
            message = json.loads(raw_message)
            print(f"Message from {client_addr}: {message}")

            # Broadcast to ALL connected clients (including sender)
            broadcast = json.dumps({
                "from": message.get("username", "anonymous"),
                "text": message.get("text", ""),
                "timestamp": datetime.utcnow().isoformat()
            })

            # Send to everyone currently connected
            # (collect results to handle disconnected clients)
            results = await asyncio.gather(
                *[client.send(broadcast) for client in connected_clients],
                return_exceptions=True
            )

    except websockets.exceptions.ConnectionClosedOK:
        pass  # Normal close
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection error from {client_addr}: {e}")
    finally:
        connected_clients.discard(websocket)
        print(f"Connection closed. Total: {len(connected_clients)}")


async def main():
    print("Chat server starting on ws://localhost:8765")
    async with websockets.serve(handle_connection, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
```

**Client** (`chat_client.py`):
```python
import asyncio
import websockets
import json

async def chat():
    uri = "ws://localhost:8765"
    username = input("Your username: ")

    async with websockets.connect(uri) as websocket:
        print(f"Connected. Type messages to chat.")

        async def receive_messages():
            async for raw in websocket:
                msg = json.loads(raw)
                print(f"\n[{msg['timestamp'][:19]}] {msg['from']}: {msg['text']}")

        # Run receiver in background
        receive_task = asyncio.create_task(receive_messages())

        try:
            while True:
                text = await asyncio.get_event_loop().run_in_executor(None, input, "")
                if text.lower() == "/quit":
                    break
                await websocket.send(json.dumps({
                    "username": username,
                    "text": text
                }))
        finally:
            receive_task.cancel()

asyncio.run(chat())
```

Run in separate terminals:
```bash
# Terminal 1
python chat_server.py

# Terminal 2
python chat_client.py

# Terminal 3
python chat_client.py
```

Open two clients, type in one, see it appear in the other. That's WebSockets.

Sindhu remembers the first time she saw a message appear in another terminal without
refreshing anything — "That moment when you realize the server just talked to you
without you asking. That's the magic."

[Back to Top](#top)

<a id="7-real-world-use-cases"></a>

## 7. Real-World Use Cases

WebSockets shine in specific scenarios. Knowing them helps you recognize when to
reach for this tool.

**Chat applications** — the canonical example. Every message from every user needs
to reach every other user immediately. Polling would create terrible user experience
and hammer the server. WebSockets are the natural fit.

**Live sports scores and financial tickers** — prices and scores change constantly.
Users expect numbers to update the moment they change. A WebSocket connection from
the browser, receiving pushed updates from the server, is exactly right.

**Collaborative editing (Google Docs style)** — when Alice types a character, Bob
sees it immediately. When Bob selects a paragraph, Alice sees the cursor. This is
bidirectional and high-frequency — WebSockets handle it cleanly. (Google Docs
actually uses a custom protocol on top of WebSockets.)

**Multiplayer browser games** — player positions, game state, actions — all need
to be synchronized across multiple clients with low latency. REST's request-response
cycle is far too slow and creates too much overhead for game tick rates.

**Monitoring dashboards** — real-time server metrics, deployment status, log
streaming. Instead of the dashboard polling every second, the server pushes updates
when they happen.

```
Sindhu's decision flowchart:

  Does the server need to push data to the client?
    No  --> Use REST / GraphQL / gRPC
    Yes --> Is it bidirectional (client also sends frequently)?
              No  --> Use SSE (Server-Sent Events)
              Yes --> Is latency critical?
                        No  --> Consider long polling
                        Yes --> Use WebSockets
```

[Back to Top](#top)

<a id="8-the-hard-part-scaling-websocket-connections"></a>

## 8. The Hard Part — Scaling WebSocket Connections

Here's where real-world WebSocket deployments get complicated. And this is something
most introductory tutorials skip. Sindhu learned this the hard way when her whiteboard
app hit 500 concurrent users and messages started disappearing.

<a id="the-sticky-session-problem"></a>

**The Sticky Session Problem**

With regular REST APIs, any server can handle any request. The client sends a GET
request, any server in your load-balanced pool can respond — they all have access
to the same database.

With WebSockets, each client has a persistent connection to one specific server.
The connection lives in that server's memory. If the client connects to Server 1
and wants to send a message to another user connected to Server 2, Server 1 doesn't
know Server 2's client even exists.

```
Broken scenario (naive WebSocket deployment):

  User A ──WebSocket──> Server 1 (knows about User A)
  User B ──WebSocket──> Server 2 (knows about User B)

  User A sends message to User B.
  Server 1 receives it.
  Server 1 has no connection to User B.
  Message is lost.
```

One solution is **sticky sessions**: configure your load balancer to always route
the same user to the same server. This works, but it creates problems:

- If Server 1 crashes, all of Server 1's users are disconnected. They reconnect,
  but they might hit different servers this time.
- You can't easily scale down servers — you'd disconnect active users.
- Load balancing becomes uneven if some users are heavier than others.

<a id="the-real-solution-redis-pubsub"></a>

**The Real Solution — Redis Pub/Sub**

The better approach: don't keep connection state in server memory. Use a message
broker that all servers can read from and write to.

The most common solution is Redis pub/sub:

```
Scaled WebSocket Architecture:

  User A ──WebSocket──> Server 1
  User B ──WebSocket──> Server 2
  User C ──WebSocket──> Server 1


  User A sends a message to Room "general":

  1. Server 1 receives message from User A
  2. Server 1 publishes to Redis channel "room:general"
  3. Redis broadcasts to all subscribers of "room:general"
  4. Server 1 is subscribed -> forwards to User A (if needed), User C
  5. Server 2 is subscribed -> forwards to User B


  Flow diagram:

  User A -> Server 1 -> Redis "room:general"
                            |
              +-------------+--------------+
              v                            v
          Server 1                    Server 2
        (User A, User C)             (User B)
```

Every server subscribes to the Redis channels relevant to its connected users.
When a message needs to reach users on a different server, it flows through Redis.

Now servers are stateless (well, except for active WebSocket connections). You can
scale horizontally, restart servers, rebalance load — the Redis pub/sub layer handles
message routing.

```python
# Conceptual Redis pub/sub pattern for WebSocket broadcasting

import asyncio
import aioredis
import websockets

redis = aioredis.from_url("redis://localhost")

async def handle_connection(websocket, room_id):
    # Subscribe to this room's Redis channel
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"room:{room_id}")

    async def forward_redis_to_ws():
        async for msg in pubsub.listen():
            if msg["type"] == "message":
                await websocket.send(msg["data"])

    # Run Redis-to-WebSocket forwarding in background
    forward_task = asyncio.create_task(forward_redis_to_ws())

    try:
        async for message in websocket:
            # Broadcast through Redis (reaches all servers)
            await redis.publish(f"room:{room_id}", message)
    finally:
        forward_task.cancel()
        await pubsub.unsubscribe(f"room:{room_id}")
```

This pattern — WebSocket connections at the edges, Redis as the message bus in the
middle — is how production chat systems, collaboration tools, and real-time dashboards
actually scale. Sindhu uses exactly this architecture for her whiteboard app — each
drawing stroke publishes to a Redis channel, and every connected server forwards it
to its local clients.

[Back to Top](#top)

<a id="9-websockets-vs-sse-vs-long-polling-the-comparison"></a>

## 9. WebSockets vs SSE vs Long Polling — The Comparison

```
                   WebSocket        SSE              Long Polling
──────────────────────────────────────────────────────────────────────
Direction:         Full duplex      Server -> Client  Server -> Client
Protocol:          ws:// / wss://   HTTP             HTTP
Browser support:   Good             Good             Universal
Mobile support:    Good             Good             Good
Complexity:        High             Low              Low
Server resources:  Persistent conn  Persistent conn  Many connections
Binary support:    Yes              No (text only)   Yes (new request)
Auto-reconnect:    Manual           Built-in         Manual
Good for:          Chat, games,     Live feeds,      Simple updates,
                   collab editing,  dashboards,      legacy browsers,
                   real-time sync   log streaming    simple polling
Bad for:           Simple feeds,    Bidirectional,   High frequency,
                   high server      binary data      large scale
                   count scenarios
```

**When to use SSE instead of WebSockets:**
If your use case is genuinely one-directional — server pushes, client only receives —
SSE is often the right choice. It's simpler to implement, works over standard HTTP/2
(which means it plays well with load balancers and CDNs), has built-in reconnection,
and doesn't require the upgrade handshake complexity. Live news feeds, deployment
progress indicators, notification streams — SSE first.

**When to use Long Polling instead of WebSockets:**
When you need to support environments where WebSockets are blocked (some corporate
firewalls or proxy configurations block WebSocket traffic). Long polling works over
plain HTTP and gets through almost anything. It's also simpler for very low-frequency
updates where the overhead of a persistent WebSocket connection isn't justified.

**When WebSockets are the right tool:**
- Your app needs bidirectional, real-time communication
- Latency is critical (games, trading, collaborative editing)
- You're sending high-frequency messages from client to server AND server to client
- You need to maintain application-level state tied to the connection

Sindhu's rule: "Start with SSE. If you find yourself needing the client to send
messages back frequently, upgrade to WebSockets. Don't reach for WebSockets by
default — they're more complex to operate."

[Back to Top](#top)

<a id="10-websocket-security"></a>

## 10. WebSocket Security

WebSocket connections inherit the authentication problem of long-lived connections.
A few things to always do in production:

**Use `wss://` not `ws://`.** The `wss://` scheme runs WebSocket over TLS, just
like `https://` for HTTP. Without it, your messages are in plaintext.

**Authenticate before or during the handshake.** The upgrade request is an HTTP
request — you can authenticate it. Options:
- Pass a token as a query parameter during the handshake: `ws://server/chat?token=abc`
  (quick but the token ends up in logs)
- Pass a token in the first WebSocket message after connecting: connect unauthenticated,
  send `{"type": "auth", "token": "abc"}` as your first message, server validates before
  processing anything else

**Validate and sanitize all incoming messages.** A WebSocket connection is a channel
into your system. Treat incoming data the same way you'd treat HTTP request bodies —
never trust it, always validate it.

Sindhu adds one more: "Set a maximum message size. I once had a client send a 50MB
payload through a WebSocket — crashed the server. Always cap incoming frame sizes
in production."

```
WebSocket Security Checklist:

  [ ] Use wss:// (TLS) in production — never ws://
  [ ] Authenticate during handshake or first message
  [ ] Validate all incoming message payloads
  [ ] Set maximum message size limits
  [ ] Implement rate limiting per connection
  [ ] Handle reconnection with re-authentication
  [ ] Log connection/disconnection events for auditing
```

[Back to Top](#top)

<a id="11-summary"></a>

## 11. Summary

```
HTTP limitation:  Pull-only — client asks, server answers, server can't push
Polling:          Client asks repeatedly — simple but wasteful
Long polling:     Client waits, server holds — better latency, resource-heavy
SSE:              Server push over HTTP — good for one-directional feeds
WebSockets:       Full-duplex, persistent — both sides push at will

The handshake:    HTTP GET with Upgrade header -> 101 Switching Protocols
After upgrade:    TCP connection stays open, HTTP is done, WS frames flow
Scaling:          Persistent connections make horizontal scaling hard
The fix:          Redis pub/sub as message bus between servers

Use WebSockets when:   Bidirectional, real-time, low-latency
Use SSE when:          Server-to-client only, simpler setup
Use Long Polling when: Low frequency, legacy environments
```

WebSockets solve a real problem that REST, GraphQL, and gRPC all share: they can't
push. When your application genuinely needs the server to initiate communication —
when waiting for the client to ask next is too slow — WebSockets are the right answer.

The scaling challenge is real, but well-understood. Redis pub/sub solves it at most
scales. Beyond that, there are purpose-built WebSocket platforms (Pusher, Ably,
Socket.IO) that handle all the hard parts if you'd rather not operate the
infrastructure yourself.

Sindhu's final advice: "WebSockets feel magical the first time you use them. But
remember — every open WebSocket is a persistent connection your server is holding.
That's memory, that's file descriptors, that's state. Use them when you need them,
not because they're cool."

<a id="fire-summary"></a>

## Fire Summary

| Concept | One-Liner |
|---------|-----------|
| HTTP limitation | Client must always ask first — server cannot push |
| Polling | Repeated requests on interval — simple, wasteful, delayed |
| Long polling | Server holds connection until data ready — better latency, resource-heavy |
| SSE | Server-to-client streaming over HTTP — ideal for one-way push |
| WebSocket handshake | HTTP GET + Upgrade header results in 101 Switching Protocols |
| Full-duplex | Both sides send/receive simultaneously on one persistent connection |
| Scaling problem | Persistent connections are pinned to one server — cross-server messages lost |
| Redis pub/sub fix | All servers subscribe to Redis channels — messages route through broker |
| When to use WS | Bidirectional, low-latency, high-frequency client+server messaging |
| When to use SSE | Server-only push, simpler infra, built-in reconnection |
| Security | wss://, auth on handshake, validate payloads, cap message size |

[Back to Top](#top)

**[Back to README](../README.md)**

**Prev:** [API Design Patterns](../16_api_design_patterns/theory.md) | **Next:** [Real-World APIs](../18_real_world_apis/theory.md)

**Related Topics:** [GraphQL](../13_graphql/theory.md) | [FastAPI Advanced](../07_fastapi/theory.md) | [API Design Patterns](../16_api_design_patterns/theory.md)

**Section:** 03_API_Mastery | **Module:** 17_websockets
