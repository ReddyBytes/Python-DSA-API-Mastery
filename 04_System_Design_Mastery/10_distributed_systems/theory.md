<a id="top"></a>

# Distributed Systems

> "When I joined a team running five microservices across two data centers," Hari says, leaning back
> in his chair, "I thought the hardest part would be the algorithms. It wasn't. The hardest part was
> accepting that every assumption I held about single-process programming was a lie in distributed
> land. The network lies. Clocks lie. Even 'success' lies — because a timeout doesn't mean failure,
> it means you don't know."

> 📝 **Practice:** [Q47 - distributed-idempotency](../system_design_practice_questions_100.md#q47--normal--distributed-idempotency) | [Q52 - distributed-locks](../system_design_practice_questions_100.md#q52--critical--distributed-locks)

<a id="learning-priority"></a>

## Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
fallacies of distributed computing, Raft consensus, replication modes (leader-follower/multi-leader/leaderless), CAP implications

**Should Learn** — Important for real projects, comes up regularly:
vector clocks, quorum reads/writes, consistent hashing, distributed transactions (2PC/Saga/Outbox)

**Good to Know** — Useful in specific situations, not always tested:
gossip protocols, CRDTs, split-brain and fencing, leader election

**Reference** — Know it exists, look up syntax when needed:
Byzantine fault tolerance, partial synchrony assumptions, causality tracking

<a id="contents"></a>

## Table of Contents

- [1. Why Distributed Systems Are Hard](#1-why-distributed-systems-are-hard)
- [2. The Fallacies of Distributed Computing](#2-the-fallacies-of-distributed-computing)
- [3. Time in Distributed Systems](#3-time-in-distributed-systems)
  - [The Clock Problem](#the-clock-problem)
  - [Logical Clocks (Lamport Clock)](#logical-clocks-lamport-clock)
  - [Vector Clocks](#vector-clocks)
- [4. Replication](#4-replication)
  - [Single-Leader Replication](#single-leader-replication)
  - [Synchronous vs Asynchronous Replication](#synchronous-vs-asynchronous-replication)
  - [Replication Lag Problems](#replication-lag-problems)
  - [Multi-Leader Replication](#multi-leader-replication)
  - [Leaderless Replication (Dynamo-style)](#leaderless-replication-dynamo-style)
  - [CRDTs — Conflict-Free Replicated Data Types](#crdts--conflict-free-replicated-data-types)
- [5. Consensus](#5-consensus)
  - [Why It Is Hard (FLP Impossibility)](#why-it-is-hard-flp-impossibility)
  - [Raft Consensus Algorithm](#raft-consensus-algorithm)
  - [Paxos](#paxos)
- [6. Partitioning (Sharding)](#6-partitioning-sharding)
  - [Hash Partitioning](#hash-partitioning)
  - [Range Partitioning](#range-partitioning)
  - [Consistent Hashing](#consistent-hashing)
  - [Sharding Considerations](#sharding-considerations)
- [7. Distributed Transactions](#7-distributed-transactions)
  - [Two-Phase Commit (2PC)](#two-phase-commit-2pc)
  - [Saga Pattern](#saga-pattern)
  - [Outbox Pattern](#outbox-pattern)
- [8. Vector Clocks and Causality](#8-vector-clocks-and-causality)
- [9. Leader Election](#9-leader-election)
  - [Bully Algorithm](#bully-algorithm)
  - [ZooKeeper / etcd Based Election](#zookeeper--etcd-based-election)
- [10. Gossip Protocols](#10-gossip-protocols)
- [11. Consistent Hashing (Deep Dive)](#11-consistent-hashing-deep-dive)
- [12. Quorum Reads and Writes](#12-quorum-reads-and-writes)
- [13. Split-Brain and Fencing](#13-split-brain-and-fencing)
- [14. Distributed Patterns Summary](#14-distributed-patterns-summary)
- [Summary](#summary)

[Back to Top](#top)

<a id="1-why-distributed-systems-are-hard"></a>

# 1. Why Distributed Systems Are Hard

"Imagine you're a chef in one kitchen," Hari explains to a junior engineer. "You can see every pot,
every burner, every timer. Now imagine ten kitchens across the city, connected only by phone. You
call Kitchen B — no answer. Did they burn down? Is the phone line cut? Are they just busy? You
genuinely cannot tell. That uncertainty is the fundamental reality of distributed systems."

```
In a single process, you can assume:
  + Operations are atomic
  + State is consistent
  + No partial failures
  + Time is linear and shared
  + Memory is shared

In a distributed system, NONE of these hold:
  x Network calls can fail partway through
  x Nodes have independent, unsynchronized clocks
  x A node can be slow but not "down" (partial failure)
  x You can't observe global state atomically
  x Messages can be delayed, duplicated, or reordered
```

The core challenge:

```
You want a distributed system to behave like a single reliable computer.
But the physical reality is multiple unreliable, asynchronous computers.
The gap between appearance and reality is where bugs live.
```

[Back to Top](#top)

<a id="2-the-fallacies-of-distributed-computing"></a>

# 2. The Fallacies of Distributed Computing

"Every one of these fallacies," Hari says, tapping the whiteboard, "I've seen cause a production
incident. Number one — the network is reliable — cost us three hours of downtime when a switch
firmware upgrade silently started dropping 0.1% of packets. Our retry budget wasn't sized for it."

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

```
Impact in real systems:

Fallacy               What breaks                    Prevention
────────────────────────────────────────────────────────────────────
Network reliable      Silent data loss, timeouts     Retries + idempotency
Latency zero          Cascade failures, slow UX      Timeouts + circuit breakers
Bandwidth infinite    Queue backup, OOM              Backpressure + pagination
Network secure        Data leaks, injection          mTLS + encryption at rest
Topology stable       Stale DNS, lost connections    Service discovery + health checks
One admin             Config drift, blame storms     GitOps + ownership boundaries
Cost zero             CPU burn on serialization      Proto/Avro + connection pools
Homogeneous           Protocol mismatches            Contract testing + gateways
```

[Back to Top](#top)

<a id="3-time-in-distributed-systems"></a>

# 3. Time in Distributed Systems

"Time," Hari says with a grin, "is the first thing that betrays you. Your laptop clock and my
laptop clock disagree by milliseconds. In those milliseconds, entire transactions can happen.
So which event came first? Wall-clock time cannot answer that question reliably."

<a id="the-clock-problem"></a>

## The Clock Problem

```
Each node has its own clock. Clocks drift.
NTP synchronizes clocks but cannot guarantee agreement better than ~100ms.

Implication: you CANNOT use wall-clock time to order events.
If node A records event at 10:00:000 and node B at 10:00:001,
you don't know which happened first!
```

<a id="logical-clocks-lamport-clock"></a>

## Logical Clocks (Lamport Clock)

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
Rule:  If A -> B (A happened before B), then clock(A) < clock(B)
       But: clock(A) < clock(B) does NOT mean A happened before B
       (concurrent events can have any clock ordering)
```

<a id="vector-clocks"></a>

## Vector Clocks

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
If two updates are concurrent -> conflict detected -> resolve (LWW or merge)

Visual comparison:

  Lamport Clock:  A single counter — tells you "maybe before" but not "definitely before"
  Vector Clock:   Per-node counters — tells you exactly: before, after, or concurrent

  Node X: [3, 0, 0]   Node Y: [0, 2, 0]   -> Concurrent (neither dominates)
  Node X: [3, 2, 1]   Node Y: [3, 1, 0]   -> X happened after Y (X dominates)
```

[Back to Top](#top)

<a id="4-replication"></a>

# 4. Replication

"Why keep copies?" Hari asks rhetorically. "Two reasons: if a node dies, you haven't lost data.
And if a node is overloaded with reads, other copies can share the load. But replication is where
distributed systems get truly painful — because keeping copies in sync is the hard problem."

Keeping copies of data on multiple nodes for fault tolerance and read scaling.

<a id="single-leader-replication"></a>

## Single-Leader Replication

```
                    +-------------+
 Writes ----------> |   Leader    |
                    +------+------+
         Replication log   |
              +------------+------------+
              v            v            v
        +----------+ +----------+ +----------+
        | Follower | | Follower | | Follower |
        +----------+ +----------+ +----------+
              +-------- Reads --------+

Properties:
  + Simple: single write path
  + Easy to reason about
  - Leader is a bottleneck for writes
  - Leader failure requires failover (election)
  - Followers may lag (replication lag = source of stale reads)
```

<a id="synchronous-vs-asynchronous-replication"></a>

## Synchronous vs Asynchronous Replication

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

<a id="replication-lag-problems"></a>

## Replication Lag Problems

```
1. Read-your-own-writes:
   You write -> read from lagging replica -> see old data
   Fix: read your own writes from the leader

2. Monotonic reads:
   You read new data from replica A, then read old data from replica B
   Fix: sticky session — always read from same replica per user

3. Consistent prefix reads:
   Causal dependencies arrive out of order at replica
   Fix: replicas apply writes in the same order as leader
```

<a id="multi-leader-replication"></a>

## Multi-Leader Replication

```
Multiple nodes accept writes. Used for:
  - Multi-datacenter (each DC has a leader)
  - Offline clients (each device is a "leader")

Problem: WRITE CONFLICTS
  Node A: user changes title to "A" at 10:00
  Node B: user changes title to "B" at 10:01
  Both replicate to the other node -> conflict!

Conflict resolution:
  Last Write Wins (LWW): timestamp determines winner
    -> data loss if clocks are off
  Custom merge: application-level merge (e.g., CRDT)
  Conflict-free: design writes to be commutative (add-only)
```

<a id="leaderless-replication-dynamo-style"></a>

## Leaderless Replication (Dynamo-style)

```
Any node can accept writes. Quorum determines success.

Write: send to N nodes, wait for W acks
Read:  send to N nodes, wait for R responses

Quorum condition: W + R > N guarantees overlap
Example: N=3, W=2, R=2
  Strong consistency: W=2, R=2 (overlap of 1)
  High availability:  W=1, R=1 (no overlap — eventual)
  High durability:    W=3, R=1

Read repair: on read, detect stale versions -> update the stale node
Anti-entropy: background process syncs nodes
Used by: Cassandra, DynamoDB, Riak
```

<a id="crdts--conflict-free-replicated-data-types"></a>

## CRDTs — Conflict-Free Replicated Data Types

"Think of CRDTs like this," Hari says. "Instead of two people fighting over the same whiteboard
marker, you give each person their own marker and a mathematical rule for merging whatever they
write. No coordination needed — the merge always produces the same result regardless of order."

In eventual consistency, different replicas may receive updates in different orders. **CRDTs (Conflict-free Replicated Data Types)** are data structures mathematically designed to merge conflicting updates automatically — no coordinator needed, no conflicts possible.

**The key insight:** instead of storing raw values, store operations in a way that merging is always commutative, associative, and idempotent.

**Common CRDTs:**

```
G-Counter (grow-only counter):
  Each node increments only its own slot.
  Value = sum of all slots.

  Node A: [3, 0, 0]    Node B: [0, 5, 0]
  Merge:  [3, 5, 0]  <- take max per slot — no conflict!

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

[Back to Top](#top)

<a id="5-consensus"></a>

# 5. Consensus

"Consensus is the constitutional amendment process of distributed systems," Hari explains. "Getting
all nodes to agree on a single value sounds trivial until you realize that messages can be lost,
nodes can crash mid-vote, and you can never be sure if silence means 'no' or 'still thinking.'"

Multiple nodes must agree on a single value, even with failures.

<a id="why-it-is-hard-flp-impossibility"></a>

## Why It Is Hard (FLP Impossibility)

```
Fischer-Lynch-Paterson (1985):
  In an asynchronous system where even ONE node can fail,
  there is no deterministic consensus algorithm that always terminates.

Practice: Real systems use timeouts (make asynchrony bounded)
-> This is why Paxos and Raft require leader elections with timeouts
```

<a id="raft-consensus-algorithm"></a>

## Raft Consensus Algorithm

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

```
Raft state machine visual:

  +----------+    timeout    +-----------+   wins election   +--------+
  | Follower | -----------> | Candidate | ----------------> | Leader |
  +----------+              +-----------+                   +--------+
       ^                         |                              |
       |     discovers leader    |    discovers higher term     |
       +-------------------------+------------------------------+
```

> 📝 **Practice:** [Q50 - distributed-consensus](../system_design_practice_questions_100.md#q50--thinking--distributed-consensus)

<a id="paxos"></a>

## Paxos

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

[Back to Top](#top)

<a id="6-partitioning-sharding"></a>

# 6. Partitioning (Sharding)

"Sharding is like dividing a library across multiple buildings," Hari says. "Authors A through M
in Building 1, N through Z in Building 2. Great for parallel access — terrible when someone asks
for 'all books published in 2023' and you have to call every building."

Split data across multiple nodes so no single node holds it all.

<a id="hash-partitioning"></a>

## Hash Partitioning

```python
def get_partition(key: str, num_partitions: int) -> int:
    return hash(key) % num_partitions

# Problem: adding/removing a node -> almost all keys remapped
# Solution: consistent hashing
```

<a id="range-partitioning"></a>

## Range Partitioning

```
Users A-F -> Shard 1
Users G-M -> Shard 2
Users N-Z -> Shard 3

+ Natural range scans (find all users A-C)
- Hotspots if data is skewed (everyone's name starts with S)
```

<a id="consistent-hashing"></a>

## Consistent Hashing

```
Imagine a ring 0..2^32. Hash nodes onto ring.
Hash key onto ring. Walk clockwise to find node.

        Node A (pos 10)
           /
  0 ──────────────────── 2^32
          ^       ^
     key=5  key=15
     -> Node A  -> Node B

Adding node C between A and B:
  Only keys between A and C move to C
  All other keys unaffected

Result: adding/removing a node moves only K/N keys
  (K = total keys, N = number of nodes)
```

<a id="sharding-considerations"></a>

## Sharding Considerations

```
Choosing shard key:
  Bad:  created_at (all writes go to "latest" shard — hotspot)
  Bad:  user_id if one user has 80% of data
  Good: hash(user_id) — even distribution
  Good: geographic region + hash — locality-aware

Cross-shard queries:
  Scatter-gather: query all shards, merge results
  -> Expensive: avoid or handle on application layer

Rebalancing:
  Fixed partitions: assign partitions to nodes, move partitions when adding
  Dynamic: split partition when too large
```

[Back to Top](#top)

<a id="7-distributed-transactions"></a>

# 7. Distributed Transactions

"Single-database transactions are a luxury," Hari says. "ACID gave us this beautiful guarantee:
either everything happens or nothing does. Now stretch that across three services, two databases,
and a message broker. Suddenly 'atomicity' becomes a distributed problem, and distributed problems
don't have clean answers — only trade-offs."

Making operations span multiple services/databases atomically.

<a id="two-phase-commit-2pc"></a>

## Two-Phase Commit (2PC)

```
Phase 1 (Prepare):
  Coordinator sends PREPARE to all participants
  Each participant: acquire locks, write to local WAL, respond YES/NO

Phase 2 (Commit or Abort):
  If all YES -> Coordinator sends COMMIT to all
  If any NO  -> Coordinator sends ABORT to all

Problems:
  - Blocking: if coordinator dies after prepare, participants wait forever
  - Single point of failure: coordinator
  - Poor performance: 2 round trips + locks held during

Use when: must have atomicity, can tolerate blocking, small number of participants
Used by: databases with distributed transactions (PostgreSQL FDW, MySQL NDB)
```

```
2PC timeline visual:

  Coordinator         Participant A       Participant B
      |                    |                    |
      |--- PREPARE ------->|                    |
      |--- PREPARE -------------------------------->|
      |                    |                    |
      |<-- YES ------------|                    |
      |<-- YES ------------------------------------|
      |                    |                    |
      |--- COMMIT -------->|                    |
      |--- COMMIT --------------------------------->|
      |                    |                    |
```

> 📝 **Practice:** [Q45 - two-phase-commit](../system_design_practice_questions_100.md#q45--critical--two-phase-commit)

<a id="saga-pattern"></a>

## Saga Pattern

```
Sequence of local transactions + compensating transactions.
If step N fails, run compensating actions for steps 1..N-1.

Order Saga:
  1. Reserve inventory      (compensate: release inventory)
  2. Charge payment         (compensate: issue refund)
  3. Create shipment        (compensate: cancel shipment)
  4. Send confirmation      (no compensation needed)

If step 3 fails:
  -> Run compensate(step 2): issue refund
  -> Run compensate(step 1): release inventory

Choreography: each service publishes events, next step triggered by event
Orchestration: central saga orchestrator calls each step

Trade-off:
  + No distributed locks, works across services
  - Eventual consistency (not atomic)
  - Complex compensating logic
  - ACD but NOT ACID (no Isolation between steps)
```

<a id="outbox-pattern"></a>

## Outbox Pattern

```
Problem: write to DB + publish event must be atomic

Solution: write event to "outbox" table in same DB transaction,
          separate process reads outbox and publishes to Kafka.

           Application
               |
        +------v---------------------------+
        | BEGIN TRANSACTION                 |
        |   INSERT INTO orders ...         |
        |   INSERT INTO outbox ...         | <- both in same TX
        | COMMIT                           |
        +----------------------------------+
                    |
           +-------v---------+
           |  Outbox Poller  | -> Kafka -> Consumers
           |  (reads & acks) |
           +-----------------+

Guarantees: at-least-once delivery (idempotent consumers required)
```

[Back to Top](#top)

<a id="8-vector-clocks-and-causality"></a>

# 8. Vector Clocks and Causality

"We covered vector clocks in the Time section," Hari notes, "but let me emphasize the causality
angle. In a distributed system, you need to answer one question constantly: did event A cause
event B, or were they independent? Vector clocks give you that answer without requiring
synchronized clocks."

```
Causality tracking with vector clocks — decision tree:

  Compare VC(A) and VC(B):
    All entries in A <= B, at least one <  ->  A happened before B
    All entries in B <= A, at least one <  ->  B happened before A
    Neither dominates                      ->  A and B are concurrent

  Why this matters:
    - Concurrent writes = conflict (need resolution strategy)
    - Causal writes = safe to apply in order
    - Without causality tracking, you cannot distinguish the two
```

Real-world usage:
- **DynamoDB** uses vector clocks to detect conflicting writes on the same key
- **Riak** returns all concurrent versions to the client for application-level resolution
- **Git** uses a DAG of commits — conceptually similar to tracking causality

[Back to Top](#top)

<a id="9-leader-election"></a>

# 9. Leader Election

"Every distributed system eventually needs a boss," Hari says. "Someone has to decide the order
of operations, break ties, coordinate. The trick is: how do you elect a boss when the voters
can't reliably communicate with each other?"

How distributed systems choose a single coordinator.

> 📝 **Practice:** [Q51 - leader-election](../system_design_practice_questions_100.md#q51--normal--leader-election)

<a id="bully-algorithm"></a>

## Bully Algorithm

```
When a node detects the leader is dead:
  1. Send ELECTION message to all nodes with higher ID
  2. If no response -> you are the new leader (send VICTORY)
  3. If higher node responds -> it takes over election
  4. Highest ID that is alive becomes leader

Simple but: highest ID node always wins.
Not used in practice (many better algorithms).
```

<a id="zookeeper--etcd-based-election"></a>

## ZooKeeper / etcd Based Election

```
Nodes create ephemeral sequential znodes in a /leader directory:
  /leader/node-000001
  /leader/node-000002 <- lowest = current leader
  /leader/node-000003

If leader dies -> its ephemeral node deleted
Each follower watches the node just below its own
When the next node disappears -> that follower attempts leadership

This prevents "herd effect": only one node wakes up on each death
```

```
ZooKeeper election visual:

  /leader/
    node-000001  <- LEADER (ephemeral, dies with session)
    node-000002  <- watches node-000001
    node-000003  <- watches node-000002

  If node-000001 dies:
    node-000002 notified -> becomes leader
    node-000003 still watches node-000002 (no herd)
```

[Back to Top](#top)

<a id="10-gossip-protocols"></a>

# 10. Gossip Protocols

"Gossip protocols work exactly like office gossip," Hari laughs. "You tell two people, they each
tell two people, and within minutes everyone knows. Mathematically, it's O(log N) rounds to reach
all nodes. No central authority needed — just randomized peer-to-peer chatter."

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
  With 1000 nodes -> ~10 rounds to full propagation

Used by:
  Cassandra: membership, schema changes, topology
  Consul: health checks, service discovery
  Amazon S3: cluster membership
```

```
Gossip propagation (3 rounds, 8 nodes):

  Round 0:  [X] [ ] [ ] [ ] [ ] [ ] [ ] [ ]   (1 node knows)
  Round 1:  [X] [X] [X] [ ] [ ] [ ] [ ] [ ]   (3 nodes know)
  Round 2:  [X] [X] [X] [X] [X] [X] [ ] [ ]   (6 nodes know)
  Round 3:  [X] [X] [X] [X] [X] [X] [X] [X]   (all 8 know)
```

[Back to Top](#top)

<a id="11-consistent-hashing-deep-dive"></a>

# 11. Consistent Hashing (Deep Dive)

"We touched on consistent hashing in the partitioning section," Hari says. "Now let me show you
the real implementation. Virtual nodes are the key insight — without them, you get uneven
distribution because hash functions don't guarantee uniform spacing on the ring."

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

```
Why virtual nodes matter:

  Without vnodes (3 physical nodes on ring):
    Node A: owns 60% of ring   <- unbalanced!
    Node B: owns 25% of ring
    Node C: owns 15% of ring

  With 150 vnodes per physical node (450 points on ring):
    Node A: owns ~33% of ring  <- balanced!
    Node B: owns ~33% of ring
    Node C: owns ~34% of ring
```

[Back to Top](#top)

<a id="12-quorum-reads-and-writes"></a>

# 12. Quorum Reads and Writes

"The quorum formula is simple," Hari says, writing on the whiteboard: "W + R > N. That's it.
If your write reaches W nodes and your read touches R nodes, and W + R exceeds the total N,
then at least one node in your read set has the latest write. Guaranteed overlap."

```
N = total replicas
W = write quorum (must succeed)
R = read quorum (must succeed)

W + R > N -> guaranteed to see latest write (overlap exists)

Common configs (N=3):
  W=3, R=1 -> Strong write, fast read (wait for all)
  W=1, R=3 -> Fast write, strong read
  W=2, R=2 -> Balanced (Cassandra QUORUM)
  W=1, R=1 -> Eventual consistency (Cassandra ONE)

Read repair:
  On quorum read, if versions differ -> write latest to stale replica
  Ensures slow repair even without explicit sync job
```

```
Quorum overlap visual (N=3, W=2, R=2):

  Write goes to:     [Node1] [Node2]  ___
  Read comes from:    ___    [Node2] [Node3]
                              ^^^^
                        Overlap guarantees freshness
```

[Back to Top](#top)

<a id="13-split-brain-and-fencing"></a>

# 13. Split-Brain and Fencing

"Split-brain is the nightmare scenario," Hari says seriously. "Two nodes both think they're the
leader. Both accept writes. Data diverges. When the partition heals, you have two conflicting
histories and no automatic way to merge them. Prevention is everything."

```
Split-brain: network partition causes two nodes to both think
             they are the leader and accept writes independently.

Result: data diverges on both sides — a corrupted system state.

Prevention techniques:

1. Quorum fence:
   Leader requires quorum to accept any write.
   If it can't reach quorum -> steps down.
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

```
Fencing token visual:

  Old Leader (token=33)           Storage Layer
       |                               |
       |--- WRITE (token=33) --------->|
       |                               |  Current token = 34
       |<-- REJECTED (stale token) ----|  (new leader already has 34)
       |                               |

  New Leader (token=34)
       |--- WRITE (token=34) --------->|
       |<-- ACCEPTED ------------------|
```

[Back to Top](#top)

<a id="14-distributed-patterns-summary"></a>

# 14. Distributed Patterns Summary

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

```
Decision guide — when to use what:

  Need strong consistency across nodes?
    -> Raft/Paxos consensus

  Need atomic multi-service transaction?
    -> 2PC (if blocking OK) or Saga (if eventual OK)

  Need to detect causal ordering?
    -> Vector clocks

  Need cluster membership propagation?
    -> Gossip protocol

  Need even data distribution with minimal reshuffling?
    -> Consistent hashing with virtual nodes

  Need tunable consistency vs latency?
    -> Quorum reads/writes (adjust W and R)

  Need conflict-free concurrent updates?
    -> CRDTs (if your data model fits)
```

[Back to Top](#top)

<a id="practice-questions"></a>

# 15. Practice Questions

> 📝 **Practice:** [Q73 - designing-for-failure](../system_design_practice_questions_100.md#q73--design--designing-for-failure)

[Back to Top](#top)

<a id="summary"></a>

# 🔥 Summary

| Concept | One-Line Takeaway |
|---------|-------------------|
| Fallacies | Never assume the network is reliable, fast, or secure |
| Time/Clocks | Wall-clock ordering is unreliable; use logical or vector clocks |
| Replication | Trade-off between write latency, read freshness, and durability |
| Consensus | Raft/Paxos let nodes agree despite failures — at cost of performance |
| Partitioning | Split data for scale; consistent hashing minimizes reshuffling |
| 2PC | Atomic but blocking; use for small participant sets |
| Saga | Eventually consistent alternative to 2PC for multi-service flows |
| Outbox | Solves DB-write + event-publish atomicity gap |
| Gossip | O(log N) propagation without central coordination |
| Quorum | W + R > N = guaranteed freshness; tune for your latency needs |
| Split-brain | Fencing tokens prevent stale leaders from corrupting data |
| CRDTs | Math-guaranteed conflict-free merges — limited to mergeable operations |

"Distributed systems," Hari concludes, "are not about finding perfect solutions. They're about
choosing which imperfection you can live with. CAP theorem isn't a limitation — it's a design
compass. Once you accept that you cannot have everything, you start making intentional trade-offs
instead of accidental ones."

[Back to Top](#top)

## Navigation

| | |
|---|---|
| Back to README | [README.md](../README.md) |
| Interview Q&A | [interview.md](./interview.md) |
| Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| Previous | [09 - Message Queues](../09_message_queues/theory.md) |
| Next | [11 - Scalability Patterns](../11_scalability_patterns/theory.md) |
