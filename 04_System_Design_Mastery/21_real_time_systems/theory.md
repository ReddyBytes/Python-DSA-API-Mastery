# ⚡ Real-Time Systems — When Milliseconds Matter

> A chat message that takes 3 seconds to appear is a broken product. A stock trade that's 50ms stale is money lost. A live leaderboard that updates every 5 minutes is just a delayed batch report. Real-time systems are where the architecture choices either feel invisible (when right) or infuriating (when wrong).

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
event-driven architecture · WebSocket scaling · pub-sub pattern · fan-out strategies · real-time vs near-real-time distinction

**Should Learn** — Important for real projects, comes up regularly:
Redis pub/sub · live leaderboard design · operational transforms for collaboration · time-series databases · backpressure in streaming

**Good to Know** — Useful in specific situations:
WebRTC for P2P · CRDT for conflict-free collaboration · Kafka for durable event streaming · real-time gaming architecture

**Reference** — Know it exists, look up when needed:
specific CRDT algorithms · WebRTC SDP/ICE details · InfluxDB query language · specific gaming engine patterns

---

## 🌊 Chapter 1: Event-Driven Architecture — React, Don't Poll

> The old way: every 5 seconds, ask "has anything changed?" The new way: get notified the moment something changes. Event-driven architecture is the second approach — publish events when things happen, let interested parties react.

**Event-driven vs request-driven:**

```
Request-driven (polling):
  Client: "Any new messages?" → Server: "No"   (every 5 seconds, forever)
  Wasted: 99% of requests return nothing

Event-driven (push):
  Server: "You have a new message!" → Client: handles it
  Efficient: client notified only when something actually happened
```

**Core components:**

```
Event Producer  →  Event Bus/Queue  →  Event Consumer(s)
(user sends msg)   (Kafka/Redis/SNS)   (notification svc, analytics, search index)

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

---

## 💬 Chapter 2: Real-Time Chat — The Canonical Problem

> WhatsApp has 2 billion users. When Alice sends a message, Bob should receive it in under 100ms — even if they're on different continents. Here's how that works.

**Architecture for real-time messaging:**

```
Alice ──── WebSocket ────► Chat Server A
                               │
                           Redis Pub/Sub    ←── fan-out to other servers
                               │
Bob ──── WebSocket ────── Chat Server B
Carol ── WebSocket ────── Chat Server B

Alice's message path:
1. Alice → WebSocket → Chat Server A
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
                await websocket.send_text(message["data"])   # ← push to client

    async def receive_messages():
        async for data in websocket.iter_text():
            # Publish to Redis → delivered to ALL servers in the cluster
            await redis.publish(f"room:{room_id}",
                                f'{{"user":"{user_id}","text":"{data}"}}')

    await asyncio.gather(send_messages(), receive_messages())
```

**Message persistence:**

```
In-memory (Redis):    Fast. Lost on restart. Good for presence, ephemeral state.
Database (Cassandra): Persistent. Chat history. Partition by (conversation_id, time).
Hybrid:               Redis for live delivery + Cassandra for history + S3 for media.
```

**Offline delivery:**

```
User offline → store message in DB → on reconnect, fetch missed messages
Key: store "last_seen_message_id" per user per conversation
On reconnect: SELECT * FROM messages WHERE id > last_seen AND conv_id = X
```

---

## 🏆 Chapter 3: Live Leaderboards — Sorted Sets at Scale

> A gaming leaderboard needs to answer: "What is the top 10 players right now, and where does player #847,293 rank?" This is a sorted ranking over millions of entries, updated in real-time.

**Redis Sorted Set — the right data structure:**

```python
import redis

r = redis.Redis()

# Update score (O(log n)):
r.zadd("leaderboard:global", {"user:12345": 9850})   # ← add or update score

# Top 10 (O(log n + k)):
top10 = r.zrevrange("leaderboard:global", 0, 9, withscores=True)
# → [("user:100", 99999), ("user:200", 95000), ...]

# Player's rank (O(log n)):
rank = r.zrevrank("leaderboard:global", "user:12345")  # ← 0-indexed from top

# Players near me (surrounding window):
rank = r.zrevrank("leaderboard:global", "user:12345")
nearby = r.zrevrange("leaderboard:global",
                     max(0, rank - 5), rank + 5,
                     withscores=True)   # ← 5 above, 5 below
```

**Scaling to 100M+ players:**

```
Single Redis instance: handles ~100K zadd/s → sufficient for most games.

For global leaderboards at massive scale:
  Sharded approach: leaderboard:shard:0 through leaderboard:shard:N
  Each user hashed to a shard for their score.
  Global rank = rank within shard + count of all higher-scoring shards.

Periodic global ranking: recompute every 15 seconds from all shards.
Real-time local ranking: within-shard ranking is always fresh.
```

**Score update fan-out:**

```
Game event → Kafka topic "score-updates"
           → Leaderboard Service (updates Redis sorted set)
           → Notification Service (pushes rank change to player via WebSocket)
           → Analytics Service (records to data warehouse)
```

---

## ✏️ Chapter 4: Collaborative Editing — Handling Concurrent Changes

> When Alice and Bob both edit the same Google Doc simultaneously, their changes must merge correctly — no data loss, no conflicts, no "who wrote last wins." This is one of the hardest problems in real-time systems.

**The conflict problem:**

```
Initial: "Hello World"

Alice deletes "World"  → "Hello "
Bob   inserts "!"      → "Hello World!"

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
            return Insert(op1.pos + 1, op1.char)  # ← shift right
        return op1  # ← no change needed
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
```

**In practice:**
- Google Docs: OT (requires central server to serialize operations)
- Figma, Notion: CRDT (works offline, peer-to-peer capable)
- Code editors (VS Code Live Share): OT with central relay

---

## 📈 Chapter 5: Time-Series Databases — Metrics at Scale

> Prometheus scrapes 100,000 metrics every 15 seconds. That's 6.7M data points per minute. A general-purpose database would collapse under this write load. Time-series databases are purpose-built for this exact pattern.

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
    #       ↑ measurement  ↑ tags (indexed)          ↑ field (value) ↑ timestamp
)
```

**Downsampling for retention:**

```
Raw (15s):    keep for 7 days    → high resolution recent data
5m avg:       keep for 30 days   → good for weekly trends
1h avg:       keep for 1 year    → long-term capacity planning
1d avg:       keep forever       → year-over-year comparison

Continuous query runs on schedule: INSERT INTO 5m_avg SELECT mean(*) FROM raw WHERE time > now()-5m GROUP BY time(5m)
```

> 📝 **Practice:** [Q67 · fan-out-social-feed](../system_design_practice_questions_100.md#q67--design--fan-out-social-feed)

---

## 🎮 Chapter 6: Real-Time Gaming — Synchronizing Parallel Universes

> In a multiplayer game, 64 players all need to see the same game state — updated 60 times per second. With 200ms network latency, the player's client would always see the past. The solution is client-side prediction and server reconciliation.

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
                self.local_state.apply(action)   # ← re-apply unconfirmed moves
```

**Server authority model:**

```
Authoritative server:  Server validates all actions. Client cannot cheat.
                       Server state is truth. Clients predict, server corrects.

Peer-to-peer:          Players share state directly (no server).
                       Faster, but cheating is easy.
                       Used for: casual games, fighting games with rollback.

Hybrid:               Critical game state on server, visual effects P2P.
```

**Tick rate:**

```
Server tick rate: how many times per second the server processes game state
20 tick:   casual games (Minecraft)
64 tick:   competitive FPS (CS:GO default)
128 tick:  pro competitive (CS:GO pro servers)
Higher tick rate = more accurate hit detection = more server CPU
```

---

---

## 📝 Practice Questions

> 📝 **Practice:** [Q99 · design-notification-100m](../system_design_practice_questions_100.md#q99--design--design-notification-100m)

> 📝 **Practice:** [Q91 · design-twitter-feed](../system_design_practice_questions_100.md#q91--design--design-twitter-feed)

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Prev | [../20_data_systems/theory.md](../20_data_systems/theory.md) |
| ➡️ Next | [../22_case_studies/theory.md](../22_case_studies/theory.md) |
| 🎤 Interview | [interview.md](./interview.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Data Systems](../20_data_systems/theory.md) &nbsp;|&nbsp; **Next:** [Case Studies →](../22_case_studies/theory.md)

**Related Topics:** [Message Queues](../09_message_queues/theory.md) · [Distributed Systems](../10_distributed_systems/theory.md) · [Networking Basics](../01_networking_basics/theory.md)
