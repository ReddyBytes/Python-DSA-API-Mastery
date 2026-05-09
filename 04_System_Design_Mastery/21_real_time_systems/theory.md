<a id="top"></a>

# Real-Time Systems — When Milliseconds Matter

> A chat message that takes 3 seconds to appear is a broken product. A stock trade that is 50ms stale is money lost. A live leaderboard that updates every 5 minutes is just a delayed batch report. Real-time systems are where architecture choices either feel invisible (when right) or infuriating (when wrong).

*Sirisha is a Telugu streaming engineer who builds event-driven systems. She spent years at a real-time gaming company before moving to financial trading infrastructure. Her lesson: "Every millisecond you add to delivery is a user who refreshes the page, a trade that loses money, or a gamer who rage-quits. The architecture must be invisible — users should never think about latency."*

## 📖 Table of Contents

- [1. What Real-Time Actually Means](#1-what-real-time-actually-means)
  - [Why HTTP Alone Cannot Solve This](#why-http-alone-cannot-solve-this)
- [2. Event-Driven Architecture — React, Don't Poll](#2-event-driven-architecture-react-dont-poll)
  - [Choreography vs Orchestration](#choreography-vs-orchestration)
- [3. WebSockets — Full Duplex Communication](#3-websockets-full-duplex-communication)
  - [Scaling WebSockets — The Hard Problem](#scaling-websockets-the-hard-problem)
- [4. Server-Sent Events — The Simpler Alternative](#4-server-sent-events-the-simpler-alternative)
- [5. Real-Time Chat — The Canonical Problem](#5-real-time-chat-the-canonical-problem)
  - [Message Persistence and Offline Delivery](#message-persistence-and-offline-delivery)
- [6. Live Leaderboards — Sorted Sets at Scale](#6-live-leaderboards-sorted-sets-at-scale)
- [7. Collaborative Editing — Handling Concurrent Changes](#7-collaborative-editing-handling-concurrent-changes)
- [8. Stream Processing — Events as They Arrive](#8-stream-processing-events-as-they-arrive)
  - [Windowing](#windowing)
  - [Stateful Processing](#stateful-processing)
- [9. Time-Series Databases — Metrics at Scale](#9-time-series-databases-metrics-at-scale)
- [10. Real-Time Gaming — Synchronizing Parallel Universes](#10-real-time-gaming-synchronizing-parallel-universes)
- [11. The Live Feed System — Putting It Together](#11-the-live-feed-system-putting-it-together)
- [12. WebRTC — Peer-to-Peer Audio and Video](#12-webrtc-peer-to-peer-audio-and-video)
- [Summary](#summary)

## Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
event-driven architecture, WebSocket scaling, pub-sub pattern, fan-out strategies, real-time vs near-real-time distinction

**Should Learn** — Important for real projects, comes up regularly:
Redis pub/sub, live leaderboard design, operational transforms for collaboration, time-series databases, backpressure in streaming

**Good to Know** — Useful in specific situations:
WebRTC for P2P, CRDT for conflict-free collaboration, Kafka for durable event streaming, real-time gaming architecture

**Reference** — Know it exists, look up when needed:
specific CRDT algorithms, WebRTC SDP/ICE details, InfluxDB query language, specific gaming engine patterns

<a id="1-what-real-time-actually-means"></a>

# 1. What Real-Time Actually Means

"People throw around 'real-time' like confetti," Sirisha says. "But a pacemaker engineer and a chat app developer mean completely different things. A pacemaker missing a deadline means someone dies. A chat message arriving 200ms late means someone waits. Both are 'real-time' — but the consequences of failure are worlds apart."

```
HARD REAL-TIME (embedded systems, aviation, medical devices):
  Missing a deadline = system failure.
  The ABS in your car must respond in < 1 millisecond.
  Missing that deadline means the car doesn't stop.
  --> Deterministic operating systems, no garbage collection, C/C++/Rust
  --> Not what web engineers mean when they say "real-time"

SOFT REAL-TIME (web applications):
  Missing a deadline = degraded user experience.
  A chat message arriving in 1.1 seconds instead of 1 second: user notices.
  A chat message arriving in 5 seconds: user is annoyed.
  A chat message arriving in 30 seconds: user reloads.
  --> No catastrophic failure, but quality matters
  --> This is what web engineers mean: sub-second to low-second latency

Most web "real-time" targets:
  Chat messages:          < 500ms
  Live prices/scores:     < 1 second
  Collaborative editing:  < 100ms (feels laggy if slower)
  Notifications:          < 2 seconds (user doesn't feel the delay)
  Gaming (competitive):   < 50ms (server tick + network)
```

<a id="why-http-alone-cannot-solve-this"></a>

## Why HTTP Alone Cannot Solve This

Standard HTTP has a fundamental limitation: the client always initiates.

```
HTTP request-response:

  Client: "Give me any new messages?"   --> Server: "None."
  Client: "Give me any new messages?"   --> Server: "None."
  Client: "Give me any new messages?"   --> Server: "1 new message!"

  This is called polling. Problems:
    --> Wastes server resources (99% of polls return nothing)
    --> Latency = polling interval (poll every 1s --> up to 1s delay)
    --> Doesn't scale: 1M users x 1 poll/second = 1M req/sec to your server

  Server CANNOT push to the client unprompted.
  You need a persistent connection for that.

Polling evolution:
  Short polling:   request, response, close. Repeat every N seconds.
  Long polling:    request, server holds until data is available, respond.
                   Immediately reconnect after response.
  SSE:            Server sends events over one persistent HTTP connection.
  WebSocket:      Full duplex — both sides send anytime over one connection.
```

> [↑ Back to Top](#top)

<a id="2-event-driven-architecture-react-dont-poll"></a>

# 2. Event-Driven Architecture — React, Don't Poll

"The old way: every 5 seconds, ask 'has anything changed?'" Sirisha explains. "It is like calling a restaurant every minute to ask if your food is ready. The new way: give them your number and they call YOU when it is ready. Event-driven architecture is the second approach — publish events when things happen, let interested parties react."

**Event-driven vs request-driven:**

```
Request-driven (polling):
  Client: "Any new messages?" --> Server: "No"   (every 5 seconds, forever)
  Wasted: 99% of requests return nothing

Event-driven (push):
  Server: "You have a new message!" --> Client: handles it
  Efficient: client notified only when something actually happened
```

**Core components:**

```
Event Producer  -->  Event Bus/Queue  -->  Event Consumer(s)
(user sends msg)     (Kafka/Redis/SNS)    (notification svc, analytics, search index)

Properties:
  Decoupled:     Producer doesn't know who consumes
  Async:         Producer doesn't wait for consumer
  Scalable:      Add consumers without changing producers
  Durable:       Events persist even if consumer is down (Kafka)
```

**Event types:**

```python
# Domain event — something happened in the business domain
{
    "event_type": "order.placed",
    "event_id": "evt_01H7X...",
    "timestamp": "2024-01-15T10:30:00Z",
    "data": {
        "order_id": "ord_123",
        "user_id": "usr_456",
        "total": 99.99
    }
}

# Commands vs Events:
# Command: "PlaceOrder" — instruction to do something (imperative)
# Event:   "OrderPlaced" — something that happened (past tense, immutable fact)
```

**Services talking through events:**

```
Direct call (synchronous):
  OrderService --> calls --> InventoryService.reserve()
              --> calls --> PaymentService.charge()
              --> calls --> EmailService.send()

  Problems:
    All three services must be available for OrderService to succeed.
    If Email is slow --> Order is slow.
    Tight coupling: OrderService knows about all downstream services.

Event-driven (asynchronous):
  OrderService --> publishes --> OrderPlaced event

  InventoryService  <-- subscribes --> hears OrderPlaced --> reserves stock
  PaymentService    <-- subscribes --> hears OrderPlaced --> charges card
  EmailService      <-- subscribes --> hears OrderPlaced --> sends email

  Benefits:
    OrderService does not know or care who reacts.
    Email being slow doesn't slow down the order.
    Add a new subscriber (SMS, analytics) without changing OrderService.
    Services can process at their own pace.
```

<a id="choreography-vs-orchestration"></a>

## Choreography vs Orchestration

```
CHOREOGRAPHY: each service knows what to do when it hears an event.
  No coordinator. Services are autonomous actors.

  OrderPlaced --> InventoryService (reserves stock, emits StockReserved)
  StockReserved --> PaymentService (charges, emits PaymentCharged)
  PaymentCharged --> FulfillmentService (ships, emits OrderShipped)

  + Loosely coupled: each service only knows its own step
  + Easy to add new services
  - Hard to visualize the full workflow
  - Debugging requires tracing events across services
  - Cycle detection: service A reacts to B's event which triggers A again?

ORCHESTRATION: a central process directs each step.
  One orchestrator knows the whole workflow.

  OrderOrchestrator:
    1. call InventoryService.reserve(orderId)
    2. call PaymentService.charge(orderId)
    3. call FulfillmentService.ship(orderId)
    4. call NotificationService.notify(userId)

  + Easy to understand the full flow (it's in one place)
  + Easy to add error handling and retry logic
  - Orchestrator is a dependency for all steps
  - Central bottleneck for complex workflows

In practice: choreography for simple event reactions,
             orchestration (e.g., AWS Step Functions) for long workflows.
```

> [↑ Back to Top](#top)

<a id="3-websockets-full-duplex-communication"></a>

# 3. WebSockets — Full Duplex Communication

"HTTP is like walkie-talkie," Sirisha says. "One person talks, then you say 'over', then the other talks. WebSocket is like a phone call — both people can talk at any time, interrupt, or stay silent. And the line stays open until someone hangs up."

**The Upgrade Handshake:**

A WebSocket connection starts as a regular HTTP request and upgrades:

```
1. Client sends HTTP request with special headers:

   GET /ws HTTP/1.1
   Host: app.example.com
   Upgrade: websocket
   Connection: Upgrade
   Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
   Sec-WebSocket-Version: 13

2. Server responds:

   HTTP/1.1 101 Switching Protocols
   Upgrade: websocket
   Connection: Upgrade
   Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=

3. The TCP connection remains open.
   Now BOTH sides can send messages anytime.

   Client --> Server: "Hello"
   Server --> Client: "World"
   Server --> Client: "New notification: you have a reply"  <-- unprompted push
   Client --> Server: "Thanks"
```

**Full Duplex: Both Directions, Anytime:**

```
HTTP:
  ────────────────────────────────────────────> (client --> server only to initiate)
  <──────────────────────────────────────────── (server --> client in response)

WebSocket (after upgrade):
  ────────────────────────────────────────────> (client --> server, any time)
  <────────────────────────────────────────────  (server --> client, any time)

  Both at the same time, on one TCP connection.
  True bidirectional, persistent channel.
```

**WebSocket use cases:**

```
EXCELLENT use cases:
  Live chat (Slack, WhatsApp Web)
  Real-time prices (stock tickers, crypto exchanges)
  Collaborative editing (Google Docs, Figma)
  Live sports scores / election results
  Multiplayer games
  Live auctions

NOT good use cases:
  Notification emails (no persistence, email is better)
  File uploads (multipart HTTP is designed for this)
  Standard REST APIs (request-response is simpler)
  One-time data fetches (just HTTP GET)
```

<a id="scaling-websockets-the-hard-problem"></a>

## Scaling WebSockets — The Hard Problem

A stateful connection. Users are pinned to a specific server.

```
Without coordination:
  User connects to Server A (WebSocket)
  User's friend connects to Server B (WebSocket)

  Friend sends message --> Server B handles it
  Server B tries to push to User --> User is on Server A!
  Server B has no connection to User.
  Message is lost.

Solution 1: Sticky Sessions
  Load balancer routes the same user to the same server always.

  ┌──────────────────┐
  │   Load Balancer  │ --> user 12345 always --> Server A
  │  (IP/cookie hash)│ --> user 67890 always --> Server B
  └──────────────────┘

  + Simple, works
  - If Server A dies, all its users lose connections and must reconnect
  - Uneven distribution if some users are more active
  - Cannot scale smoothly

Solution 2: Pub/Sub Message Bus (better)
  All WebSocket servers subscribe to a shared message bus (Redis Pub/Sub,
  Kafka). When Server B needs to push to a user on Server A, it publishes
  to the bus. Server A receives it and pushes to the user.

  ┌──────────┐   publishes message   ┌───────────┐
  │ Server B │ ─────────────────────> │ Redis     │
  │          │                        │ Pub/Sub   │
  └──────────┘                        └─────┬─────┘
                                            │ subscribes
                                      ┌─────v─────┐
                                      │ Server A  │ --> pushes to user 12345
                                      └───────────┘

  + Servers are stateless (mostly) — any server can handle any user message
  + Scales horizontally — add more servers freely
  + Resilient to server failures
  - Redis becomes a bottleneck at extreme scale
  - More infrastructure complexity
```

> [↑ Back to Top](#top)

<a id="4-server-sent-events-the-simpler-alternative"></a>

# 4. Server-Sent Events — The Simpler Alternative

"If you only need the server to push to clients — and the client never needs to send real-time data back — SSE is often the right choice," Sirisha advises. "It is simpler than WebSockets, works through HTTP/2, and has automatic reconnection built in. Do not overcomplicate when SSE is sufficient."

SSE uses a regular HTTP connection that stays open. The server streams `text/event-stream` formatted data down to the client continuously.

```
Client:  GET /notifications HTTP/1.1
         Accept: text/event-stream

Server:  HTTP/1.1 200 OK
         Content-Type: text/event-stream
         Cache-Control: no-cache

         (connection stays open, server sends events over time)

         data: {"type": "like", "post_id": 99, "liker": "Bob"}\n\n

         data: {"type": "comment", "post_id": 42}\n\n

         event: alert
         data: {"message": "Your order shipped!"}\n\n

         (client receives these as they arrive, auto-reconnects if disconnected)
```

**SSE vs WebSockets — When to use which:**

```
┌─────────────────────────────────┬──────────────────────────────────┐
│            SSE                  │           WebSocket              │
├─────────────────────────────────┼──────────────────────────────────┤
│ Server --> client ONLY          │ Bidirectional                    │
│ Plain HTTP (no upgrade needed)  │ Requires upgrade + protocol      │
│ Automatic reconnection built-in │ Must implement reconnect yourself│
│ Works through HTTP/2 mux        │ Separate TCP connection          │
│ Simpler to implement            │ More complex, more powerful      │
├─────────────────────────────────┼──────────────────────────────────┤
│ Good for:                       │ Good for:                        │
│  Live feed / timeline updates   │  Chat (bidirectional)            │
│  Dashboard metrics              │  Collaborative editing           │
│  Progress bars                  │  Games                           │
│  Breaking news ticker           │  Live trading (send + receive)   │
│  Order status updates           │  Interactive real-time features  │
└─────────────────────────────────┴──────────────────────────────────┘

Rule of thumb:
  Client never needs to send real-time data? --> SSE
  Client sends data too (messages, edits, moves)? --> WebSocket
```

> [↑ Back to Top](#top)

<a id="5-real-time-chat-the-canonical-problem"></a>

# 5. Real-Time Chat — The Canonical Problem

"WhatsApp has 2 billion users," Sirisha says. "When Alice sends a message, Bob should receive it in under 100ms — even if they are on different continents. This is the 'Hello World' of real-time architecture. If you can design chat well, you can design most real-time systems."

**Architecture for real-time messaging:**

```
Alice ──── WebSocket ────> Chat Server A
                               │
                           Redis Pub/Sub    <── fan-out to other servers
                               │
Bob ──── WebSocket ────── Chat Server B
Carol ── WebSocket ────── Chat Server B

Alice's message path:
1. Alice --> WebSocket --> Chat Server A
2. Server A publishes to Redis channel "room:123"
3. Redis delivers to all servers subscribed to "room:123"
4. Server B pushes to Bob and Carol's WebSocket connections
```

**Redis pub/sub for multi-server fan-out:**

```python
import asyncio
import aioredis
from fastapi import WebSocket

redis = aioredis.from_url("redis://localhost")

async def websocket_handler(websocket: WebSocket, room_id: str, user_id: str):
    await websocket.accept()

    # Subscribe to this room's Redis channel
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"room:{room_id}")

    async def send_messages():
        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_text(message["data"])   # push to client

    async def receive_messages():
        async for data in websocket.iter_text():
            # Publish to Redis --> delivered to ALL servers in the cluster
            await redis.publish(f"room:{room_id}",
                                f'{{"user":"{user_id}","text":"{data}"}}')

    await asyncio.gather(send_messages(), receive_messages())
```

<a id="message-persistence-and-offline-delivery"></a>

## Message Persistence and Offline Delivery

```
In-memory (Redis):    Fast. Lost on restart. Good for presence, ephemeral state.
Database (Cassandra): Persistent. Chat history. Partition by (conversation_id, time).
Hybrid:               Redis for live delivery + Cassandra for history + S3 for media.

Offline delivery:
  User offline --> store message in DB --> on reconnect, fetch missed messages
  Key: store "last_seen_message_id" per user per conversation
  On reconnect: SELECT * FROM messages WHERE id > last_seen AND conv_id = X
```

> [↑ Back to Top](#top)

<a id="6-live-leaderboards-sorted-sets-at-scale"></a>

# 6. Live Leaderboards — Sorted Sets at Scale

"A gaming leaderboard," Sirisha explains, "needs to answer two questions in microseconds: 'What are the top 10 players right now?' and 'Where does player number 847,293 rank?' This is a sorted ranking over millions of entries, updated in real-time. Redis sorted sets were literally designed for this."

**Redis Sorted Set — the right data structure:**

```python
import redis

r = redis.Redis()

# Update score (O(log n)):
r.zadd("leaderboard:global", {"user:12345": 9850})   # add or update score

# Top 10 (O(log n + k)):
top10 = r.zrevrange("leaderboard:global", 0, 9, withscores=True)
# --> [("user:100", 99999), ("user:200", 95000), ...]

# Player's rank (O(log n)):
rank = r.zrevrank("leaderboard:global", "user:12345")  # 0-indexed from top

# Players near me (surrounding window):
rank = r.zrevrank("leaderboard:global", "user:12345")
nearby = r.zrevrange("leaderboard:global",
                     max(0, rank - 5), rank + 5,
                     withscores=True)   # 5 above, 5 below
```

**Scaling to 100M+ players:**

```
Single Redis instance: handles ~100K zadd/s --> sufficient for most games.

For global leaderboards at massive scale:
  Sharded approach: leaderboard:shard:0 through leaderboard:shard:N
  Each user hashed to a shard for their score.
  Global rank = rank within shard + count of all higher-scoring shards.

Periodic global ranking: recompute every 15 seconds from all shards.
Real-time local ranking: within-shard ranking is always fresh.

Score update fan-out:
  Game event --> Kafka topic "score-updates"
             --> Leaderboard Service (updates Redis sorted set)
             --> Notification Service (pushes rank change via WebSocket)
             --> Analytics Service (records to data warehouse)
```

> [↑ Back to Top](#top)

<a id="7-collaborative-editing-handling-concurrent-changes"></a>

# 7. Collaborative Editing — Handling Concurrent Changes

"When Alice and Bob both edit the same Google Doc simultaneously," Sirisha says, "their changes must merge correctly — no data loss, no conflicts, no 'who wrote last wins.' This is one of the hardest problems in real-time systems. The naive approach (last write wins) destroys data."

**The conflict problem:**

```
Initial: "Hello World"

Alice deletes "World"  --> "Hello "
Bob   inserts "!"      --> "Hello World!"

Naive merge: depends on order of operations — broken.
Correct merge: "Hello !"  (Alice's delete applied, Bob's insert adjusted)
```

**Operational Transformation (OT) — Google Docs approach:**

```python
# OT: transform operations against each other before applying

# Operation types:
# Insert(pos, char)
# Delete(pos)

def transform(op1, op2):
    """Transform op1 assuming op2 has already been applied."""
    if isinstance(op1, Insert) and isinstance(op2, Insert):
        if op2.pos <= op1.pos:
            return Insert(op1.pos + 1, op1.char)  # shift right
        return op1  # no change needed
    # ... handle all combinations
```

**CRDT-based approach (Figma, many modern editors):**

```
Each character gets a globally unique ID (user_id + sequence_number).
Characters are ordered by their IDs, not positions.
Insertions: always reference the character they come "after."
Deletions:  mark as "tombstone" (still in structure, invisible).

Result: any order of applying operations gives the same final document.
No server coordination needed — merge is purely local.

OT vs CRDT:
  OT:   Requires central server to serialize operations.
        Simpler to understand. Google Docs, VS Code Live Share.
  CRDT: Works offline, peer-to-peer capable.
        More complex data structures. Figma, Notion.
```

> [↑ Back to Top](#top)

<a id="8-stream-processing-events-as-they-arrive"></a>

# 8. Stream Processing — Events as They Arrive

"Stream processing is about doing computation on a continuous flow of events," Sirisha explains, "as opposed to waiting for a batch of data to accumulate. Imagine a factory assembly line where each item is inspected as it passes by, versus a warehouse where you wait until 1000 items pile up, then inspect them all at once."

```
Batch processing:
  "Every night at midnight, process all of today's events."
  Latency: up to 24 hours from event to result.

Stream processing:
  "Process each event within milliseconds of it occurring."
  Latency: milliseconds to seconds.

Same question, different systems:
  "How many users clicked the Buy button in the last hour?"
  Batch: run at 1 AM --> results available at 1:15 AM
  Stream: continuously updated --> always current within seconds
```

**Kafka Streams and Apache Flink:**

```
KAFKA STREAMS:
  Library (not a separate cluster) for stream processing on Kafka topics.
  Your code runs inside your own Java/Scala application.
  Stateful: can maintain counts, windows, join streams.
  Good for: moderate volume, simpler pipelines, you want to stay in the JVM.

APACHE FLINK:
  Separate distributed processing cluster.
  True streaming (event by event, not micro-batches).
  Extremely low latency (milliseconds).
  Complex windowing, stateful operators, exactly-once guarantees.
  Good for: high volume, complex analytics, strict latency requirements.
  Used by: Netflix, Uber, Alibaba, Lyft for real-time analytics.

SPARK STREAMING:
  Micro-batch processing (collects events for 100ms-1s, then processes batch).
  Not true streaming but good throughput.
  Good for: you already use Spark, throughput matters more than latency.
```

<a id="windowing"></a>

## Windowing

An infinite stream has no natural "end." Windowing lets you compute aggregations over time-bounded segments.

```
TUMBLING WINDOWS (fixed, non-overlapping):
  Divide time into fixed chunks. Each event belongs to exactly one window.

  Window 1: [00:00 - 01:00]  --> process --> emit count
  Window 2: [01:00 - 02:00]  --> process --> emit count
  Window 3: [02:00 - 03:00]  --> process --> emit count

  Use case: "Clicks per minute" — one result per minute.

SLIDING WINDOWS (overlapping):
  Windows slide forward by a smaller step than their size.

  Window size: 5 minutes, slide: 1 minute:
  [00:00 - 05:00] --> emit
  [01:00 - 06:00] --> emit
  [02:00 - 07:00] --> emit

  Use case: "Rate of errors in the last 5 minutes, updated every minute"
            Smooths out spikes better than tumbling windows.

SESSION WINDOWS (activity-based):
  Group events that occur within an inactivity gap of each other.

  User events: click, click, [30 min gap], click, click
  --> Session 1: first two clicks
  --> Session 2: last two clicks (after inactivity timeout)

  Use case: user session analytics, e-commerce cart behavior.
```

<a id="stateful-processing"></a>

## Stateful Processing

```
Stateless: "For each payment event, send a notification email"
  --> Each event is independent. No memory of past events needed.

Stateful: "Alert if a user makes > 5 failed login attempts in 10 minutes"
  --> Must count failed attempts per user, within a rolling time window
  --> Must remember past events to evaluate the current one

Flink stateful example:
  "Count distinct users who visited the product page in the last 5 minutes"

  For each page view event:
    1. Get current state for this window (set of user_ids)
    2. Add current user_id to set
    3. Emit current count (size of set)
    4. At window close: clear state for that window

  Flink stores this state durably (in RocksDB by default).
  Even if a node fails, state is recovered from checkpoint.
```

> [↑ Back to Top](#top)

<a id="9-time-series-databases-metrics-at-scale"></a>

# 9. Time-Series Databases — Metrics at Scale

"Prometheus scrapes 100,000 metrics every 15 seconds," Sirisha says. "That is 6.7 million data points per minute. A general-purpose database would collapse under this write load. Time-series databases are purpose-built for this exact access pattern — high-frequency writes ordered by time, with queries that always ask 'what happened between time A and time B?'"

A **time-series database** (TSDB) optimizes for: high-frequency writes, time-range queries, automatic downsampling, and efficient compression of sequential numeric data.

**Why normal databases fail at metrics:**

```
PostgreSQL append:         ~50K rows/second
InfluxDB/Prometheus:       ~1M data points/second

PostgreSQL time-range:     full table scan or complex index use
TSDB time-range:           chunks stored by time — instant range scan
```

**Prometheus data model:**

```
metric_name{label1="value1", label2="value2"} value timestamp

http_requests_total{method="GET", status="200", service="api"} 1024 1704067200000

# Query: rate of 4xx errors per second over last 5 minutes:
rate(http_requests_total{status=~"4.."}[5m])
```

**InfluxDB line protocol:**

```python
# Write to InfluxDB
from influxdb_client import InfluxDBClient

client = InfluxDBClient(url="http://localhost:8086", token=TOKEN)
write_api = client.write_api()

write_api.write(
    bucket="metrics",
    record=f"cpu_usage,host=server01,region=us-east value=72.5 {timestamp_ns}"
    #       measurement  tags (indexed)          field (value)  timestamp
)
```

**Downsampling for retention:**

```
Raw (15s):    keep for 7 days    --> high resolution recent data
5m avg:       keep for 30 days   --> good for weekly trends
1h avg:       keep for 1 year    --> long-term capacity planning
1d avg:       keep forever       --> year-over-year comparison

Continuous query runs on schedule:
  INSERT INTO 5m_avg SELECT mean(*) FROM raw WHERE time > now()-5m GROUP BY time(5m)
```

> [↑ Back to Top](#top)

<a id="10-real-time-gaming-synchronizing-parallel-universes"></a>

# 10. Real-Time Gaming — Synchronizing Parallel Universes

"In a multiplayer game," Sirisha explains, "64 players all need to see the same game state — updated 60 times per second. With 200ms network latency, the player's client would always see the past. Without tricks, every action feels 200ms delayed — and that is unplayable. The solution is client-side prediction with server reconciliation."

**The latency problem:**

```
Player presses "move forward" at T=0
Server receives at T=100ms (network delay)
Server processes, broadcasts at T=105ms
All other clients receive at T=205ms

Without tricks: every action feels 200ms delayed = unplayable
```

**Client-side prediction:**

```python
# Client immediately applies action locally (don't wait for server)
class GameClient:
    def move(self, direction):
        # Apply movement locally NOW (optimistic update)
        self.local_state.apply(MoveAction(direction))
        self.pending_actions.append(MoveAction(direction))

        # Also send to server for authoritative confirmation
        self.network.send(MoveAction(direction))

    def on_server_state(self, server_state, last_processed_action_id):
        # Server is authoritative — correct any prediction errors
        self.local_state = server_state

        # Replay pending unconfirmed actions on top of server state
        for action in self.pending_actions:
            if action.id > last_processed_action_id:
                self.local_state.apply(action)   # re-apply unconfirmed moves
```

**Server authority model:**

```
Authoritative server:  Server validates all actions. Client cannot cheat.
                       Server state is truth. Clients predict, server corrects.

Peer-to-peer:          Players share state directly (no server).
                       Faster, but cheating is easy.
                       Used for: casual games, fighting games with rollback.

Hybrid:               Critical game state on server, visual effects P2P.

Tick rate:
  Server tick rate: how many times per second the server processes game state
  20 tick:   casual games (Minecraft)
  64 tick:   competitive FPS (CS:GO default)
  128 tick:  pro competitive (CS:GO pro servers)
  Higher tick rate = more accurate hit detection = more server CPU
```

> [↑ Back to Top](#top)

<a id="11-the-live-feed-system-putting-it-together"></a>

# 11. The Live Feed System — Putting It Together

"Let me show you how all these pieces combine," Sirisha says, drawing on the whiteboard. "A real-time sports scoreboard where teams score and millions of users see the update within 1 second."

```
SCORE UPDATE FLOW:

  Official scorer's app
        │
        │  POST /api/score   (authenticated)
        v
  ┌─────────────┐
  │  Score API  │  <-- validates, persists to DB
  │  Service    │
  └──────┬──────┘
         │
         │  publishes ScoreUpdated event
         v
  ┌─────────────┐
  │    Kafka    │  <-- durable buffer, topic: "score-events"
  │  topic      │
  └──────┬──────┘
         │
         │  consumes events
         v
  ┌─────────────────┐
  │  WebSocket      │  <-- fan-out service
  │  Server Pool    │  maintains ~100K WS connections each
  │  (N servers)    │
  └────────┬────────┘
           │  pushes to all connections
           │  subscribed to this game
           v
  ┌──────────────────────────────────────────────────────┐
  │  1M browser clients with open WebSocket connections  │
  │  See: "GOAL! 2-1 Real Madrid"                        │
  └──────────────────────────────────────────────────────┘

  Coordination between WebSocket servers:
  Each server subscribes to Redis Pub/Sub channel "game:{game_id}"
  Score API publishes to Redis --> all WS servers receive --> push to clients
```

**Twitter/X Timeline Refresh (similar pattern):**

```
User follows 500 accounts.
Any of those accounts can tweet at any time.
The user must see new tweets quickly without polling.

Architecture:
  Tweet created --> publish to Kafka topic "tweets"
  Fan-out service: for each tweet, look up author's followers
                   publish to each follower's personal queue
  WebSocket/SSE: client has open connection
                 when a tweet lands in their queue --> push it
  Client: receives tweet event --> prepends to timeline

This is the push-on-write model (fan-out at write time).
Contrast with pull-on-read (fan-in at read time — Instagram's old approach).

Push pros:  reads are instant (data already in your queue)
Push cons:  celebrities with 50M followers = 50M writes per tweet

Hybrid: push for users with < 1M followers, pull for celebrities.
```

> [↑ Back to Top](#top)

<a id="12-webrtc-peer-to-peer-audio-and-video"></a>

# 12. WebRTC — Peer-to-Peer Audio and Video

"For video calls," Sirisha explains, "you want audio/video data to flow directly between browsers without going through your servers. That is WebRTC. Your server only helps the two browsers find each other — after that, the actual media goes peer-to-peer."

**The three-stage problem:**

```
WebRTC solves three problems:

1. HOW DO PEERS FIND EACH OTHER? (Signaling)
   Peers start behind NAT/firewalls with no direct address.
   Solution: use your server (WebSocket or HTTP) to exchange connection
   parameters (called SDP — Session Description Protocol).

   Alice's browser --- "I want to call Bob, here are my params" --> Server
   Server --- "Bob, Alice wants to connect, here are her params" --> Bob
   Alice <----- "I accept, here are my params" ─────────────── Bob

   Your server only relays these tiny metadata messages.
   The actual audio/video NEVER goes through your server (ideally).

2. HOW DO PEERS PUNCH THROUGH NAT? (ICE / STUN)
   Both peers are behind NAT routers with private IPs.
   They need to discover their public IP/port.

   STUN server: a simple server that tells you "your public IP is X.X.X.X:Y"
   ICE: protocol that finds the best path between two peers,
        trying direct connection first, then STUN, then TURN as fallback.

3. WHAT IF DIRECT CONNECTION FAILS? (TURN)
   Some corporate firewalls block WebRTC.
   TURN server: relay server that forwards data when direct fails.
   Now your server carries the media --> bandwidth cost on you.

   +------------+
   | STUN/TURN  |  <-- Usually a free/cheap service
   +------------+
        | (only metadata / fallback relay)
   Alice ─────────────────────────────────── Bob
         Direct peer-to-peer media (ideal)
```

**When WebRTC vs When WebSockets for live video:**

```
WebRTC:
  + Peer-to-peer (server not in media path)
  + Low latency (< 200ms, designed for live communication)
  + Built-in adaptive bitrate, echo cancellation, jitter buffer
  - Complex to implement (ICE, STUN, TURN, signaling)
  - TURN relay costs if NAT traversal fails
  - Not suitable for 1-to-many broadcast (each peer = separate connection)

WebSocket for video:
  + Simple (server relays everything)
  + Works for server-side recording, moderation, AI processing
  - Higher latency (media goes through server)
  - Server pays all bandwidth costs
  - Doesn't scale to large numbers of participants easily

RTMP/HLS for live broadcast:
  + Great for 1-to-many (Twitch, YouTube Live)
  + Scales to millions of viewers via CDN
  - Higher latency (5-30 seconds for HLS)
  - Not interactive

Choose:
  1-on-1 or small group video call (< 10 people): WebRTC
  Large group with interaction: WebRTC via SFU (selective forwarding unit)
  Live broadcast to many viewers: RTMP ingest --> HLS via CDN
```

> [↑ Back to Top](#top)

<a id="summary"></a>

## 🔥 Summary

```
Real-Time Systems at a Glance:

  Component              Purpose                         Protocol/Tool
  ─────────────────────  ──────────────────────────────  ─────────────────
  Event-driven arch.     Decouple producers/consumers    Kafka, Redis Pub/Sub
  WebSockets             Full-duplex persistent conn.    ws:// protocol
  SSE                    Server-to-client push only      text/event-stream
  Stream processing      Compute on continuous events    Flink, Kafka Streams
  TSDB                   High-frequency metric storage   Prometheus, InfluxDB
  WebRTC                 Peer-to-peer audio/video        ICE/STUN/TURN
  Sorted sets            Real-time rankings              Redis ZSET

Sirisha's golden rules:
  1. "Real-time" for web = soft real-time = sub-second latency
  2. HTTP cannot push. Use WebSockets for bidirectional, SSE for push-only
  3. Scaling WebSockets requires coordination (Redis Pub/Sub or Kafka)
  4. Stream processing: windowing bounds the infinite stream into computable chunks
  5. For real-time feeds: write --> Kafka --> fan-out --> WebSocket/SSE --> client
  6. WebRTC = peer-to-peer media. Signaling through your server. Media ideally not.
  7. Client-side prediction masks latency in games — server remains authoritative
```

```
Common mistakes Sirisha sees in real-time system designs:

  WRONG: "We'll use WebSockets for everything"
  WHY:   If the client never sends real-time data, SSE is simpler
         and works better through proxies/load balancers.

  WRONG: "We'll poll the server every 100ms for updates"
  WHY:   At 1M users, that is 10M requests/sec. Use push instead.

  WRONG: "Each WebSocket server will maintain a local subscription map"
  WHY:   Users on different servers cannot reach each other.
         You need a shared pub/sub layer (Redis, Kafka).

  WRONG: "We'll use WebRTC for a live streaming concert to 1M viewers"
  WHY:   WebRTC is peer-to-peer. 1M peers = 1M connections per sender.
         Use HLS via CDN for 1-to-many broadcast.

  WRONG: "We'll store all stream processing state in-memory only"
  WHY:   Node failure = state loss. Use checkpointed state (Flink + RocksDB).

  WRONG: "Real-time means zero latency"
  WHY:   Physics prevents zero latency. Real-time means consistent
         sub-second latency that users perceive as instant.
```

```
Backpressure in streaming systems:

  Problem: producer generates events faster than consumer can process.
  Without backpressure: unbounded queues grow --> OOM crash.

  Solutions:
    Drop oldest:     Kafka consumer falls behind, skip old messages
    Drop newest:     If queue full, reject new events (rate limit producer)
    Buffer + spill:  Buffer in memory up to limit, then spill to disk
    Signal upstream: Flink/reactive streams signal "slow down" to producer
    Scale consumers: Auto-scale consumer group to match throughput

  Sirisha's rule: "Always design for the case where your consumer
  is slower than your producer. It WILL happen."
```

## Mini Exercises

**1.** Design a live stock price ticker for a trading platform.
100,000 users are watching prices simultaneously. Prices update 100 times/second.
Sketch the data flow from exchange feed to user's browser.
What is the bottleneck? How do you handle it?

**2.** You are building a collaborative document editor (like Google Docs).
Two users can type simultaneously. Both see each other's changes in real-time.
What protocol do you use? What happens if one user's connection drops for
5 seconds and then reconnects? How do you merge their changes?

**3.** A notification system sends alerts to users (new follower, new like).
Users are rarely active. Alerts can arrive any time.
Compare: (a) polling every 30 seconds, (b) SSE, (c) WebSockets.
What is the trade-off for each? Which would you choose?

**4.** Your WebSocket server handles 500,000 concurrent connections on 5 servers
(100,000 each). You need to send a message to all users subscribed to "topic:news".
There are 300,000 of them, spread across all 5 servers.
How does the message get from the publisher to all 300,000 connections?

## 📂 Navigation

| | |
|---|---|
| 📘 README | [Back to System Design README](../README.md) |

| ⬅ Previous | ➡ Next |
|---|---|
| [20 — Data Systems](../20_data_systems/theory.md) | [22 — Case Studies](../22_case_studies/theory.md) |

**This folder:** [theory.md](./theory.md) | [cheetsheet.md](./cheetsheet.md) | [interview.md](./interview.md) | [practice_local.py](./practice_local.py) | [real_time_guide.md](./real_time_guide.md)

**Related modules:** [09 — Message Queues](../09_message_queues/theory.md) | [10 — Distributed Systems](../10_distributed_systems/theory.md) | [20 — Data Systems](../20_data_systems/theory.md) | [01 — Networking Basics](../01_networking_basics/theory.md)

**Jump to topics:** [WebSocket Scaling](#scaling-websockets-the-hard-problem) | [Stream Processing](#8-stream-processing-events-as-they-arrive) | [Live Feed Design](#11-the-live-feed-system-putting-it-together) | [WebRTC](#12-webrtc-peer-to-peer-audio-and-video)
