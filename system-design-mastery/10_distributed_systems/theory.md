# 🌐 Distributed Systems

> The science of making multiple computers work as one reliable system.
> Understanding distributed systems is what separates senior engineers
> from developers who "just use microservices."

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
fallacies of distributed computing · Raft consensus · replication modes (leader-follower/multi-leader/leaderless) · CAP implications

**Should Learn** — Important for real projects, comes up regularly:
vector clocks · quorum reads/writes · consistent hashing · distributed transactions (2PC/Saga/Outbox)

**Good to Know** — Useful in specific situations, not always tested:
gossip protocols · CRDTs · split-brain and fencing · leader election

**Reference** — Know it exists, look up syntax when needed:
Byzantine fault tolerance · partial synchrony assumptions · causality tracking

---

## 📋 Contents

```
1.  Why distributed systems are hard
2.  The fallacies of distributed computing
3.  Time in distributed systems
4.  Replication — keeping copies in sync
5.  Consensus — agreeing on one truth
6.  Partitioning (Sharding)
7.  Distributed transactions
8.  Vector clocks and causality
9.  Leader election
10. Gossip protocols
11. Consistent hashing
12. Quorum reads and writes
13. Split-brain and fencing
14. Distributed patterns summary
```

---

## 1. Why Distributed Systems Are Hard

```
In a single process, you can assume:
  ✓ Operations are atomic
  ✓ State is consistent
  ✓ No partial failures
  ✓ Time is linear and shared
  ✓ Memory is shared

In a distributed system, NONE of these hold:
  ✗ Network calls can fail partway through
  ✗ Nodes have independent, unsynchronized clocks
  ✗ A node can be slow but not "down" (partial failure)
  ✗ You can't observe global state atomically
  ✗ Messages can be delayed, duplicated, or reordered
```

The core challenge:
```
You want a distributed system to behave like a single reliable computer.
But the physical reality is multiple unreliable, asynchronous computers.
The gap between appearance and reality is where bugs live.
```

---

## 2. The Fallacies of Distributed Computing

Assumptions that will hurt you (Peter Deutsch, L. Peter Deutsch, 1994):

```
1. The network is reliable.
   Reality: packets drop, connections timeout, TCP retransmits

2. Latency is zero.
   Reality: network hops, queuing, congestion add ms to every call

3. Bandwidth is infinite.
   Reality: saturate links with enough data or chattiness

4. The network is secure.
   Reality: MITM, eavesdropping, injection — encrypt everything

5. Topology doesn't change.
   Reality: servers restart, IPs change, DNS updates propagate slowly

6. There is one administrator.
   Reality: multiple teams, orgs, and cloud providers involved

7. Transport cost is zero.
   Reality: serialization, compression, connection pooling — all have cost

8. The network is homogeneous.
   Reality: different OS, hardware, protocols, MTUs
```

---

## 3. Time in Distributed Systems

### The clock problem

```
Each node has its own clock. Clocks drift.
NTP synchronizes clocks but cannot guarantee agreement better than ~100ms.

Implication: you CANNOT use wall-clock time to order events.
If node A records event at 10:00:000 and node B at 10:00:001,
you don't know which happened first!
```

### Logical Clocks (Lamport Clock)

Each node maintains a counter. Every event increments it. Messages carry the sender's counter.

```python
class LamportClock:
    def __init__(self):
        self._time = 0

    def tick(self) -> int:
        self._time += 1
        return self._time

    def send(self) -> int:
        return self.tick()

    def receive(self, sender_time: int) -> int:
        self._time = max(self._time, sender_time) + 1
        return self._time
```

```
Rule:  If A → B (A happened before B), then clock(A) < clock(B)
       But: clock(A) < clock(B) does NOT mean A happened before B
       (concurrent events can have any clock ordering)
```

### Vector Clocks

Track per-node counters to capture causality precisely.

```python
class VectorClock:
    def __init__(self, node_id: str, nodes: list[str]):
        self.node_id = node_id
        self.clock = {n: 0 for n in nodes}

    def tick(self):
        self.clock[self.node_id] += 1

    def send(self) -> dict:
        self.tick()
        return dict(self.clock)

    def receive(self, other: dict):
        for node, time in other.items():
            self.clock[node] = max(self.clock.get(node, 0), time)
        self.tick()

    def happens_before(self, a: dict, b: dict) -> bool:
        """Does a happen before b?"""
        return (all(a.get(n, 0) <= b.get(n, 0) for n in b) and
                any(a.get(n, 0) < b.get(n, 0) for n in b))

    def concurrent(self, a: dict, b: dict) -> bool:
        return not self.happens_before(a, b) and not self.happens_before(b, a)
```

```
Usage: DynamoDB, Riak use vector clocks to detect conflicts
If two updates are concurrent → conflict detected → resolve (LWW or merge)
```

---

## 4. Replication

Keeping copies of data on multiple nodes for fault tolerance and read scaling.

### Single-Leader Replication

```
                    ┌─────────────┐
 Writes ──────────→ │   Leader    │
                    └──────┬──────┘
         Replication log   │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Follower │ │ Follower │ │ Follower │
        └──────────┘ └──────────┘ └──────────┘
              └──────── Reads ────────┘

Properties:
  + Simple: single write path
  + Easy to reason about
  - Leader is a bottleneck for writes
  - Leader failure requires failover (election)
  - Followers may lag (replication lag = source of stale reads)
```

### Synchronous vs Asynchronous Replication

```
Synchronous (semi-sync):
  Leader waits for at least 1 follower to confirm before acking client
  + Durability: data is safe even if leader dies immediately
  - Higher write latency (waits for follower)
  Example: PostgreSQL synchronous_commit

Asynchronous:
  Leader acks client immediately, replicates in background
  + Low write latency
  - Follower lag: reads from follower may be stale
  - Data loss if leader dies before replication
  Example: MySQL async replication (default)
```

### Replication Lag Problems

```
1. Read-your-own-writes:
   You write → read from lagging replica → see old data
   Fix: read your own writes from the leader

2. Monotonic reads:
   You read new data from replica A, then read old data from replica B
   Fix: sticky session — always read from same replica per user

3. Consistent prefix reads:
   Causal dependencies arrive out of order at replica
   Fix: replicas apply writes in the same order as leader
```

### Multi-Leader Replication

```
Multiple nodes accept writes. Used for:
  - Multi-datacenter (each DC has a leader)
  - Offline clients (each device is a "leader")

Problem: WRITE CONFLICTS
  Node A: user changes title to "A" at 10:00
  Node B: user changes title to "B" at 10:01
  Both replicate to the other node → conflict!

Conflict resolution:
  Last Write Wins (LWW): timestamp determines winner
    → data loss if clocks are off
  Custom merge: application-level merge (e.g., CRDT)
  Conflict-free: design writes to be commutative (add-only)
```

### Leaderless Replication (Dynamo-style)

```
Any node can accept writes. Quorum determines success.

Write: send to N nodes, wait for W acks
Read:  send to N nodes, wait for R responses

Quorum condition: W + R > N guarantees overlap
Example: N=3, W=2, R=2
  Strong consistency: W=2, R=2 (overlap of 1)
  High availability:  W=1, R=1 (no overlap — eventual)
  High durability:    W=3, R=1

Read repair: on read, detect stale versions → update the stale node
Anti-entropy: background process syncs nodes
Used by: Cassandra, DynamoDB, Riak
```

### CRDTs — Conflict-Free Replicated Data Types

In eventual consistency, different replicas may receive updates in different orders. **CRDTs (Conflict-free Replicated Data Types)** are data structures mathematically designed to merge conflicting updates automatically — no coordinator needed, no conflicts possible.

**The key insight:** instead of storing raw values, store operations in a way that merging is always commutative, associative, and idempotent.

**Common CRDTs:**

```
G-Counter (grow-only counter):
  Each node increments only its own slot.
  Value = sum of all slots.

  Node A: [3, 0, 0]    Node B: [0, 5, 0]
  Merge:  [3, 5, 0]  ← take max per slot — no conflict!

OR-Set (observed-remove set):
  Add: generate unique tag (uuid) for each element.
  Remove: track which tags are "removed."
  Merge: union of all adds and removes — deterministic.

LWW-Register (last-write-wins register):
  Attach a timestamp to each value.
  Merge: always keep the higher timestamp.
  Risk: clock skew can cause incorrect merges.
```

**Where CRDTs are used:**
- Redis (CRDT-based geo-distributed mode)
- Riak KV (distributed database)
- Collaborative editors (Google Docs uses OT, Figma uses CRDTs)
- Shopping carts (Amazon Dynamo paper)

**Trade-off:** CRDTs restrict what operations are possible — only operations that are mathematically mergeable. For arbitrary business logic, you still need coordination or conflict resolution rules.

---

## 5. Consensus

Multiple nodes must agree on a single value, even with failures.

### Why it's hard (FLP Impossibility)

```
Fischer-Lynch-Paterson (1985):
  In an asynchronous system where even ONE node can fail,
  there is no deterministic consensus algorithm that always terminates.

Practice: Real systems use timeouts (make asynchrony bounded)
→ This is why Paxos and Raft require leader elections with timeouts
```

### Raft Consensus Algorithm

```
Three roles: Leader, Follower, Candidate

Normal operation:
  1. Leader receives client write
  2. Leader appends to its log
  3. Leader sends AppendEntries to all followers
  4. Followers append to their logs, send ack
  5. Leader commits when quorum acks
  6. Leader notifies followers of commit
  7. Leader responds to client

Election:
  1. Follower doesn't hear from leader for election_timeout (150-300ms)
  2. Follower becomes Candidate, increments term, votes for itself
  3. Sends RequestVote to all nodes
  4. First node with majority votes becomes new Leader
  5. New leader starts sending heartbeats

Properties:
  + Strong consistency: only committed entries are visible
  + Leader always has most up-to-date log
  + At most one leader per term (guaranteed by quorum)

Used by: etcd, CockroachDB, TiKV, Consul
```

### Paxos

```
The original consensus algorithm (Lamport, 1989).
More complex than Raft but widely used in theory.

Two phases:
  Phase 1 (Prepare): Proposer asks acceptors to promise
                     not to accept proposals with lower ID
  Phase 2 (Accept):  Proposer sends value to acceptors,
                     acceptors accept if promise holds

Multi-Paxos: elect a distinguished proposer (leader) to skip Phase 1
Used by: Chubby (Google), Zookeeper (ZAB variant)
```

---

## 6. Partitioning (Sharding)

Split data across multiple nodes so no single node holds it all.

### Hash Partitioning

```python
def get_partition(key: str, num_partitions: int) -> int:
    return hash(key) % num_partitions

# Problem: adding/removing a node → almost all keys remapped
# Solution: consistent hashing
```

### Range Partitioning

```
Users A-F → Shard 1
Users G-M → Shard 2
Users N-Z → Shard 3

+ Natural range scans (find all users A-C)
- Hotspots if data is skewed (everyone's name starts with S)
```

### Consistent Hashing

```
Imagine a ring 0..2^32. Hash nodes onto ring.
Hash key onto ring. Walk clockwise to find node.

        Node A (pos 10)
           /
  0 ──────────────────── 2^32
          ▲       ▲
     key=5  key=15
     → Node A  → Node B

Adding node C between A and B:
  Only keys between A and C move to C
  All other keys unaffected

Result: adding/removing a node moves only K/N keys
  (K = total keys, N = number of nodes)
```

### Sharding Considerations

```
Choosing shard key:
  Bad:  created_at (all writes go to "latest" shard — hotspot)
  Bad:  user_id if one user has 80% of data
  Good: hash(user_id) — even distribution
  Good: geographic region + hash — locality-aware

Cross-shard queries:
  Scatter-gather: query all shards, merge results
  → Expensive: avoid or handle on application layer

Rebalancing:
  Fixed partitions: assign partitions to nodes, move partitions when adding
  Dynamic: split partition when too large
```

---

## 7. Distributed Transactions

Making operations span multiple services/databases atomically.

### Two-Phase Commit (2PC)

```
Phase 1 (Prepare):
  Coordinator sends PREPARE to all participants
  Each participant: acquire locks, write to local WAL, respond YES/NO

Phase 2 (Commit or Abort):
  If all YES → Coordinator sends COMMIT to all
  If any NO  → Coordinator sends ABORT to all

Problems:
  - Blocking: if coordinator dies after prepare, participants wait forever
  - Single point of failure: coordinator
  - Poor performance: 2 round trips + locks held during

Use when: must have atomicity, can tolerate blocking, small number of participants
Used by: databases with distributed transactions (PostgreSQL FDW, MySQL NDB)
```

### Saga Pattern

```
Sequence of local transactions + compensating transactions.
If step N fails, run compensating actions for steps 1..N-1.

Order Saga:
  1. Reserve inventory      (compensate: release inventory)
  2. Charge payment         (compensate: issue refund)
  3. Create shipment        (compensate: cancel shipment)
  4. Send confirmation      (no compensation needed)

If step 3 fails:
  → Run compensate(step 2): issue refund
  → Run compensate(step 1): release inventory

Choreography: each service publishes events, next step triggered by event
Orchestration: central saga orchestrator calls each step

Trade-off:
  + No distributed locks, works across services
  - Eventual consistency (not atomic)
  - Complex compensating logic
  - ACD but NOT ACID (no Isolation between steps)
```

### Outbox Pattern

```
Problem: write to DB + publish event must be atomic

Solution: write event to "outbox" table in same DB transaction,
          separate process reads outbox and publishes to Kafka.

           Application
               │
        ┌──────▼───────────────────┐
        │ BEGIN TRANSACTION         │
        │   INSERT INTO orders ...  │
        │   INSERT INTO outbox ...  │ ← both in same TX
        │ COMMIT                    │
        └───────────────────────────┘
                    │
           ┌────────▼────────┐
           │  Outbox Poller  │ → Kafka → Consumers
           │  (reads & acks) │
           └─────────────────┘

Guarantees: at-least-once delivery (idempotent consumers required)
```

---

## 8. Leader Election

How distributed systems choose a single coordinator.

### Bully Algorithm

```
When a node detects the leader is dead:
  1. Send ELECTION message to all nodes with higher ID
  2. If no response → you are the new leader (send VICTORY)
  3. If higher node responds → it takes over election
  4. Highest ID that is alive becomes leader

Simple but: highest ID node always wins.
Not used in practice (many better algorithms).
```

### ZooKeeper / etcd Based Election

```
Nodes create ephemeral sequential znodes in a /leader directory:
  /leader/node-000001
  /leader/node-000002 ← lowest = current leader
  /leader/node-000003

If leader dies → its ephemeral node deleted
Each follower watches the node just below its own
When the next node disappears → that follower attempts leadership

This prevents "herd effect": only one node wakes up on each death
```

---

## 9. Gossip Protocols

```
How to disseminate information to all nodes without central coordinator.

Like "hot gossip" — each node periodically selects random peer,
shares its state, peer updates and shares further.

Properties:
  + Scales to thousands of nodes
  + Self-healing (nodes that missed updates eventually get them)
  + No central broker
  + Eventually consistent spread

Math: with N nodes, after O(log N) rounds, all nodes have the info
  With 1000 nodes → ~10 rounds to full propagation

Used by:
  Cassandra: membership, schema changes, topology
  Consul: health checks, service discovery
  Amazon S3: cluster membership
```

---

## 10. Consistent Hashing (Deep Dive)

```python
import hashlib
from bisect import bisect, insort

class ConsistentHashRing:
    """Consistent hashing with virtual nodes for even distribution."""

    def __init__(self, virtual_nodes: int = 150):
        self._ring: list[int] = []
        self._node_map: dict[int, str] = {}
        self._vnodes = virtual_nodes

    def add_node(self, node: str) -> None:
        for i in range(self._vnodes):
            key = self._hash(f"{node}:vnode:{i}")
            insort(self._ring, key)
            self._node_map[key] = node

    def remove_node(self, node: str) -> None:
        for i in range(self._vnodes):
            key = self._hash(f"{node}:vnode:{i}")
            self._ring.remove(key)
            del self._node_map[key]

    def get_node(self, key: str) -> str:
        if not self._ring:
            raise ValueError("No nodes in ring")
        h = self._hash(key)
        idx = bisect(self._ring, h) % len(self._ring)
        return self._node_map[self._ring[idx]]

    def _hash(self, value: str) -> int:
        return int(hashlib.md5(value.encode()).hexdigest(), 16)
```

---

## 11. Quorum Reads and Writes

```
N = total replicas
W = write quorum (must succeed)
R = read quorum (must succeed)

W + R > N → guaranteed to see latest write (overlap exists)

Common configs (N=3):
  W=3, R=1 → Strong write, fast read (wait for all)
  W=1, R=3 → Fast write, strong read
  W=2, R=2 → Balanced (Cassandra QUORUM)
  W=1, R=1 → Eventual consistency (Cassandra ONE)

Read repair:
  On quorum read, if versions differ → write latest to stale replica
  Ensures slow repair even without explicit sync job
```

---

## 12. Split-Brain and Fencing

```
Split-brain: network partition causes two nodes to both think
             they are the leader and accept writes independently.

Result: data diverges on both sides — a corrupted system state.

Prevention techniques:

1. Quorum fence:
   Leader requires quorum to accept any write.
   If it can't reach quorum → steps down.
   Prevents stale leader from accepting writes.

2. STONITH (Shoot The Other Node In The Head):
   New leader sends command to physically kill old leader
   before becoming active.
   Ensures only one leader can operate.

3. Fencing tokens:
   Each leader lease has a monotonically increasing token.
   Storage systems reject writes from tokens lower than current.
   Old leader's writes get rejected even if it doesn't know it's deposed.
```

---

## 13. Distributed Patterns Summary

```
Pattern              Problem Solved                    Key Trade-off
─────────────────────────────────────────────────────────────────────
Raft/Paxos           Consensus, leader election        Performance vs safety
Two-Phase Commit     Atomic cross-node transaction     Availability (blocking)
Saga                 Long-running distributed tx        No isolation between steps
Outbox               DB write + event publish atomicity At-least-once delivery
Gossip               Membership / config propagation   Eventual consistency
Consistent Hashing   Even data distribution            Complex implementation
Quorum               Read/write consistency tuning     Latency vs consistency
Vector Clocks        Causal ordering of events         Storage overhead
CRDT                 Conflict-free concurrent updates  Limited data structures
Sidecar              Add cross-cutting concerns        Extra process overhead
```

---

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ← Previous | [09 — Message Queues](../09_message_queues/theory.md) |
| ➡️ Next | [11 — Scalability Patterns](../11_scalability_patterns/theory.md) |
| 🏠 Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Message Queues — Interview Q&A](../09_message_queues/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
