# System Design Patterns — Visual Explanation

> Story-based, diagram-heavy, step-by-step. No shortcuts.

---

## 1. LRU Cache — "The Bookshelf with Limited Space"

### The Story

Picture a small bookshelf in your office. It holds exactly **3 books**. You're a
developer who keeps reference books on hand. Whenever you need a book, you grab
it from the shelf (fast!). If the book isn't on the shelf, you have to go to the
library (slow — a cache miss) and bring it back.

But the shelf only holds 3 books. When you bring a new book and the shelf is
full, you put back **the book you haven't opened in the longest time**. That's
the Least Recently Used eviction policy.

This is LRU Cache: fast O(1) lookups, O(1) insertions, and when full, evict
the least recently used item.

---

### Internal Structure: Doubly Linked List + Hash Map

```
  Why two data structures?

  Hash Map:  key → node pointer
    ↳ gives us O(1) lookup: "is key in cache? where is it?"

  Doubly Linked List: ordered by recency (head=most recent, tail=least recent)
    ↳ gives us O(1) removal: we have a direct pointer to any node
    ↳ gives us O(1) move-to-front: unlink + relink at head
    ↳ gives us O(1) eviction: remove from tail

  Why DOUBLY linked (not singly)?
  Singly linked list: to remove a node, you need the PREVIOUS node's pointer.
  With a singly linked list, finding the previous node takes O(n).
  With a doubly linked list, every node has a "prev" pointer → O(1) removal.

  Structure:

  DUMMY_HEAD ↔ [most recent] ↔ ... ↔ [least recent] ↔ DUMMY_TAIL

  DUMMY_HEAD and DUMMY_TAIL are sentinel nodes (always present, never evicted).
  They make edge cases (empty list, single element) much cleaner to code.
```

---

### Trace: Operations on a Size-3 LRU Cache

**Initial State:**

```
  Cache capacity: 3
  Hash map: {}
  List: DUMMY_HEAD ↔ DUMMY_TAIL

  (HEAD and TAIL are sentinels, not real entries)
```

---

**Operation 1: put(1, "Book A")**

```
  Key 1 not in cache. Insert at HEAD (most recently used position).

  Hash map: {1 → nodeA}
  List:
    DUMMY_HEAD ↔ [1:"Book A"] ↔ DUMMY_TAIL
                  ▲ most recent

  Cache state:
  ┌────────────────────────────────────┐
  │  [1] ← MRU                         │
  │  (empty slot)                      │
  │  (empty slot)                      │
  └────────────────────────────────────┘
  Size: 1/3
```

---

**Operation 2: put(2, "Book B")**

```
  Key 2 not in cache. Insert at HEAD.

  Hash map: {1 → nodeA, 2 → nodeB}
  List:
    DUMMY_HEAD ↔ [2:"Book B"] ↔ [1:"Book A"] ↔ DUMMY_TAIL
                  ▲ most recent               ▲ least recent

  Cache state:
  ┌────────────────────────────────────┐
  │  [2] ← MRU                         │
  │  [1]                               │
  │  (empty slot)                      │
  └────────────────────────────────────┘
  Size: 2/3
```

---

**Operation 3: put(3, "Book C")**

```
  Key 3 not in cache. Insert at HEAD. Cache is now FULL.

  Hash map: {1 → nodeA, 2 → nodeB, 3 → nodeC}
  List:
    DUMMY_HEAD ↔ [3:"Book C"] ↔ [2:"Book B"] ↔ [1:"Book A"] ↔ DUMMY_TAIL
                  ▲ most recent                               ▲ least recent

  Cache state:
  ┌────────────────────────────────────┐
  │  [3] ← MRU                         │
  │  [2]                               │
  │  [1] ← LRU                         │
  └────────────────────────────────────┘
  Size: 3/3 (FULL)
```

---

**Operation 4: get(1)**

```
  Key 1 IS in cache → CACHE HIT! Return "Book A".
  But now we must move node 1 to the HEAD (it was just used).

  Steps:
    1. Find node 1 via hash map (O(1))
    2. Unlink node 1 from its current position (O(1) — doubly linked!)
    3. Re-insert node 1 at HEAD (O(1))

  Before:  HEAD ↔ [3] ↔ [2] ↔ [1] ↔ TAIL
  After:   HEAD ↔ [1] ↔ [3] ↔ [2] ↔ TAIL

  Cache state:
  ┌────────────────────────────────────┐
  │  [1] ← MRU (just accessed!)        │
  │  [3]                               │
  │  [2] ← LRU                         │
  └────────────────────────────────────┘
  Note: [2] is now LRU (we used 1, 3 was put more recently than 2)
```

---

**Operation 5: put(4, "Book D") — cache is FULL, must EVICT**

```
  Key 4 not in cache. Cache is full (3/3).
  Must evict LRU item: that's [2] (the tail of our list, before DUMMY_TAIL).

  Steps:
    1. Find LRU = node before DUMMY_TAIL = node 2
    2. Remove node 2 from list (O(1) — doubly linked!)
    3. Remove key 2 from hash map (O(1))
    4. Insert new node 4 at HEAD
    5. Add key 4 to hash map

  Before eviction:
    HEAD ↔ [1] ↔ [3] ↔ [2] ↔ TAIL
                          ▲ evict this (LRU)

  After eviction + insert:
    HEAD ↔ [4] ↔ [1] ↔ [3] ↔ TAIL
            ▲ just inserted

  Cache state:
  ┌────────────────────────────────────┐
  │  [4] ← MRU (just inserted)         │
  │  [1]                               │
  │  [3] ← LRU                         │
  └────────────────────────────────────┘
  Hash map: {1 → node1, 3 → node3, 4 → node4}
  (key 2 has been evicted — gone!)
```

---

**Operation 6: get(2) — key was evicted**

```
  Key 2 is NOT in hash map → CACHE MISS.
  Return -1 (or null). Would need to go to actual database/storage.

  Cache state: UNCHANGED (miss doesn't modify cache)
  ┌────────────────────────────────────┐
  │  [4] ← MRU                         │
  │  [1]                               │
  │  [3] ← LRU                         │
  └────────────────────────────────────┘
```

---

**Operation 7: put(5, "Book E") — evict again**

```
  Key 5 not in cache. Must evict LRU = node 3.

  Cache state after:
  ┌────────────────────────────────────┐
  │  [5] ← MRU                         │
  │  [4]                               │
  │  [1] ← LRU                         │
  └────────────────────────────────────┘
  (key 3 evicted)
```

---

**Operation 8: get(1) — hit, moves to front**

```
  Key 1 IS in cache → HIT!
  Move [1] to front.

  Cache state:
  ┌────────────────────────────────────┐
  │  [1] ← MRU (just accessed!)        │
  │  [5]                               │
  │  [4] ← LRU                         │
  └────────────────────────────────────┘
```

---

**Operation 9: get(4) — hit, moves to front**

```
  Key 4 IS in cache → HIT!
  Move [4] to front.

  Cache state:
  ┌────────────────────────────────────┐
  │  [4] ← MRU                         │
  │  [1]                               │
  │  [5] ← LRU                         │
  └────────────────────────────────────┘
```

---

### Code Skeleton

```python
class LRUCache:
    class Node:
        def __init__(self, key=0, val=0):
            self.key = key
            self.val = val
            self.prev = None
            self.next = None

    def __init__(self, capacity: int):
        self.cap = capacity
        self.map = {}                    # key → Node
        self.head = self.Node()          # dummy head (MRU side)
        self.tail = self.Node()          # dummy tail (LRU side)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        """Unlink node from list. O(1) because doubly linked."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_at_head(self, node):
        """Insert node right after dummy head (most recent position)."""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.map:
            return -1
        node = self.map[key]
        self._remove(node)               # unlink from current position
        self._insert_at_head(node)       # move to front (most recently used)
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.map:
            self._remove(self.map[key])  # remove old version
        node = self.Node(key, value)
        self.map[key] = node
        self._insert_at_head(node)
        if len(self.map) > self.cap:
            lru = self.tail.prev         # node just before dummy tail = LRU
            self._remove(lru)
            del self.map[lru.key]
```

---

## 2. LFU Cache — "The Least Popular Book Gets Thrown Out"

### The Story

LFU (Least Frequently Used) is the strict librarian who tracks not just WHEN
you used a book, but HOW MANY TIMES total. When the shelf is full, out goes
the book you've accessed the fewest times overall. If two books have the same
access count, the tiebreaker is recency (LRU among equals).

**LRU vs LFU:**
```
  LRU: "You haven't touched this book recently — OUT."
  LFU: "You've only ever opened this book once — OUT."

  LRU is about recency.  LFU is about frequency.

  Example of the difference:
    Cache size 3. You put(1), put(2), put(3).
    You access key 1 ten times in a row.
    You access key 2 once.
    You access key 3 once.
    Now you insert key 4.

    LRU would evict key 2 or 3 (whichever was accessed less recently).
    LFU would evict key 2 or 3 (freq=1), NOT key 1 (freq=10), even if
         key 1 hasn't been accessed recently.
```

---

### Internal Structure

```
  LFU needs to track three things simultaneously:

  1. node_map:  key → Node(key, val, freq)
     "Given a key, find its node instantly."

  2. freq_map:  freq → OrderedDict of nodes (ordered by insertion = recency)
     "Given a frequency, find all nodes with that frequency,
      in order from least-recently to most-recently used."

  3. min_freq:  the current minimum frequency
     "When evicting, which frequency bucket do we look in?"

  Why OrderedDict for freq buckets?
    An OrderedDict preserves insertion order.
    The OLDEST entry (first inserted) is the LRU among equal-frequency nodes.
    We can evict it in O(1) with popitem(last=False).
```

---

### Trace: Operations on a Size-3 LFU Cache

**Initial State:**

```
  capacity = 3
  node_map = {}
  freq_map = {}     # will be: {1: OrderedDict(), 2: OrderedDict(), ...}
  min_freq = 0
```

---

**put(1, 'a')**

```
  New key. Insert with frequency 1.

  node_map = {1: Node(1,'a', freq=1)}
  freq_map = {1: OrderedDict([(1, node1)])}
  min_freq = 1

  Frequency buckets:
  freq=1: [1]
  freq=2: (empty)
```

---

**put(2, 'b')**

```
  New key. Insert with frequency 1.

  node_map = {1: ..., 2: Node(2,'b', freq=1)}
  freq_map = {1: OrderedDict([(1,node1), (2,node2)])}
  min_freq = 1

  Frequency buckets:
  freq=1: [1, 2]    ← 1 inserted first (LRU), 2 inserted second
```

---

**get(1) — cache hit, freq of key 1 goes 1→2**

```
  Step 1: Find node 1 in node_map (freq=1).
  Step 2: Remove key 1 from freq_map[1].
  Step 3: Increment node 1's freq to 2.
  Step 4: Add node 1 to freq_map[2].
  Step 5: If freq_map[1] is now empty AND min_freq was 1 → min_freq becomes 2.

  freq_map[1]: OrderedDict([(2, node2)])   ← only key 2 remains at freq 1
  freq_map[2]: OrderedDict([(1, node1)])   ← key 1 moved to freq 2

  node_map[1].freq = 2  (updated)
  min_freq = 1  (freq_map[1] still has key 2, so min is still 1)

  Frequency buckets:
  freq=1: [2]       ← key 2 is the least frequently used
  freq=2: [1]       ← key 1 has been accessed twice
```

---

**put(3, 'c') — cache has room (size=2, cap=3), just insert**

```
  New key. Insert with frequency 1.
  min_freq resets to 1 (any new key starts at freq=1).

  freq_map[1]: OrderedDict([(2, node2), (3, node3)])
  freq_map[2]: OrderedDict([(1, node1)])

  Frequency buckets:
  freq=1: [2, 3]    ← both at freq 1; key 2 is LRU of this group
  freq=2: [1]

  min_freq = 1
  Size = 3/3  ← FULL
```

---

**put(4, 'd') — FULL, must evict!**

```
  Who gets evicted?
    Look at freq_map[min_freq] = freq_map[1]
    The LRU node in freq=1 bucket is the FIRST entry in the OrderedDict.
    That's key 2 (it was inserted into freq=1 before key 3).

  EVICT key 2.
    Remove key 2 from freq_map[1].
    Remove key 2 from node_map.

  Insert key 4 with freq=1.
  min_freq = 1 (new key always starts at 1).

  freq_map[1]: OrderedDict([(3, node3), (4, node4)])
  freq_map[2]: OrderedDict([(1, node1)])
  node_map = {1: node1(freq=2), 3: node3(freq=1), 4: node4(freq=1)}

  Frequency buckets:
  freq=1: [3, 4]    ← key 3 is LRU among freq-1 nodes
  freq=2: [1]
```

---

**Eviction Summary Diagram:**

```
  Initial (after all puts and the get(1)):

  ┌──────────────────────────────────────────────────────┐
  │  FREQ=2  │  key 1 (val='a') — accessed twice         │
  │  FREQ=1  │  key 2, key 3    — accessed once each     │
  │                                                      │
  │  When we need to evict: look at FREQ=1 (min_freq)   │
  │  Among freq=1 nodes, evict LRU = key 2              │
  └──────────────────────────────────────────────────────┘

  After eviction + put(4):

  ┌──────────────────────────────────────────────────────┐
  │  FREQ=2  │  key 1           — 2 accesses             │
  │  FREQ=1  │  key 3, key 4   — 1 access each           │
  │                                                      │
  │  key 2 is GONE                                       │
  └──────────────────────────────────────────────────────┘
```

---

### Code Skeleton

```python
from collections import OrderedDict

class LFUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.min_freq = 0
        self.node_map = {}                   # key → [val, freq]
        self.freq_map = {}                   # freq → OrderedDict{key: None}

    def _update_freq(self, key):
        val, freq = self.node_map[key]
        # Remove from current freq bucket
        del self.freq_map[freq][key]
        if not self.freq_map[freq]:
            del self.freq_map[freq]
            if self.min_freq == freq:
                self.min_freq += 1           # no more nodes at min_freq
        # Add to freq+1 bucket
        new_freq = freq + 1
        self.node_map[key] = [val, new_freq]
        if new_freq not in self.freq_map:
            self.freq_map[new_freq] = OrderedDict()
        self.freq_map[new_freq][key] = None

    def get(self, key: int) -> int:
        if key not in self.node_map:
            return -1
        self._update_freq(key)
        return self.node_map[key][0]

    def put(self, key: int, value: int) -> None:
        if self.cap == 0:
            return
        if key in self.node_map:
            self.node_map[key][0] = value    # update value
            self._update_freq(key)
        else:
            if len(self.node_map) >= self.cap:
                # Evict LFU (LRU among min-freq nodes)
                evict_key, _ = self.freq_map[self.min_freq].popitem(last=False)
                if not self.freq_map[self.min_freq]:
                    del self.freq_map[self.min_freq]
                del self.node_map[evict_key]
            # Insert new key at freq=1
            self.node_map[key] = [value, 1]
            if 1 not in self.freq_map:
                self.freq_map[1] = OrderedDict()
            self.freq_map[1][key] = None
            self.min_freq = 1                # new key always starts at freq=1
```

---

## 3. Consistent Hashing — "Adding a Delivery Driver Without Reassigning Everyone's Orders"

### The Story

Imagine a food delivery service. You have drivers (servers) handling orders
(keys). Each order is assigned to a driver based on the order's ID.

**The naive approach (regular hashing):** `driver = order_id % num_drivers`

Works fine... until you add or remove a driver.

```
  3 drivers: order_id % 3

  Order 1  → driver 1%3 = 1
  Order 2  → driver 2%3 = 2
  Order 3  → driver 3%3 = 0
  Order 4  → driver 4%3 = 1
  Order 5  → driver 5%3 = 2

  Now you hire a 4th driver: order_id % 4

  Order 1  → driver 1%4 = 1  ✓ same
  Order 2  → driver 2%4 = 2  ✓ same
  Order 3  → driver 3%4 = 3  ✗ CHANGED! (was 0, now 3)
  Order 4  → driver 4%4 = 0  ✗ CHANGED! (was 1, now 0)
  Order 5  → driver 5%4 = 1  ✗ CHANGED! (was 2, now 1)

  3 out of 5 orders (60%) had to be reassigned!
  In a real system: cache misses, data migration, chaos.
```

**The consistent hashing solution:** Almost no reassignment when you add/remove
a node. Only the keys between the new node and its predecessor move.

---

### The Ring

```
  Imagine a clock face — a ring with positions 0 to 359 degrees (or 0 to 2^32-1).

  Step 1: Hash each SERVER to a position on the ring.
    hash("ServerA") = position 60
    hash("ServerB") = position 150
    hash("ServerC") = position 270

  Step 2: Hash each KEY (order ID, cache key, etc.) to a position on the ring.
  Step 3: A key is handled by the FIRST SERVER clockwise from the key's position.

  The Ring (numbers are positions 0-360):

                    0/360
                      │
              300 ─── ┼ ─── 60
                    / │ \
               270/  │   \90
                 /   │    \
             240│    │     │120
                 \   │    /
               210\  │   /150
                    \ │ /
              180 ─── ┼ ─── ...

  With our 3 servers:
                    0/360
                      │
              300 ─── ╋ ─── [ServerA @ 60]
                    / │ \
      [ServerC   270  │   \90
        @ 270]  /     │    \
               /      │     │120
              │        │     │
               \       │    /
                \      │   /
                 [ServerB @ 150]

  Clean ring diagram:

         12 o'clock (0)
              │
     10 ──────┼────── 2  ← ServerA at "2 o'clock" (60°)
    /          │         \
   9           │           3
    \          │          /
     8 ── ServerC ────── 4
       (270°)  │
               ServerB (150°, about "5 o'clock")
```

**The ring with servers and keys:**

```
  Ring positions (approximate clock positions):

          [ 0 ]
         /     \
    [315]       [45]
       |           |
    [270]         [90]
    (ServerC)      |
       |         [135]
    [225]          |
         \      [150]
          [180] (ServerB)

  Servers:  A=60,  B=150,  C=270
  Keys:     K1=20, K2=80, K3=130, K4=200, K5=310

  Assignment (go clockwise to next server):
  K1 @ 20  → next server clockwise → ServerA @ 60   → K1 served by A
  K2 @ 80  → next server clockwise → ServerB @ 150  → K2 served by B
  K3 @ 130 → next server clockwise → ServerB @ 150  → K3 served by B
  K4 @ 200 → next server clockwise → ServerC @ 270  → K4 served by C
  K5 @ 310 → next server clockwise → ServerA @ 60   → K5 served by A
             (wraps around: 310 → passes 360/0 → hits A at 60)

  Summary:
  ServerA (@ 60):  K1, K5
  ServerB (@150):  K2, K3
  ServerC (@270):  K4
```

---

### Adding a New Server

```
  We add ServerD at position 100.

  New assignment:
  K1 @ 20  → ServerA @ 60    → K1 still served by A  (no change)
  K2 @ 80  → ServerD @ 100   → K2 NOW served by D    ← MOVED
  K3 @ 130 → ServerB @ 150   → K3 still served by B  (no change)
  K4 @ 200 → ServerC @ 270   → K4 still served by C  (no change)
  K5 @ 310 → ServerA @ 60    → K5 still served by A  (no change)

  Only K2 moved! (1 out of 5 = 20%)
  With naive hashing, it was ~60%.

  The rule: when you add ServerD at position 100,
  only keys between the PREVIOUS server (A @ 60) and D (@ 100) move.
  That's the range (60, 100]. Only K2 @ 80 falls there.

  ┌──────────────────────────────────────────────────────────────┐
  │  Adding a server only affects keys in the "arc" between      │
  │  the new server and its predecessor.                         │
  │  Everything else is completely unaffected.                   │
  └──────────────────────────────────────────────────────────────┘
```

---

### Virtual Nodes: Solving Uneven Distribution

```
  Problem: With only 3 servers, the arcs might be very uneven.
  ServerA might handle 50% of the ring, ServerB 10%, ServerC 40%.
  This causes load imbalance.

  Solution: Virtual nodes — each PHYSICAL server maps to MULTIPLE
  positions on the ring. These are "virtual" replicas.

  Example: Each server gets 3 virtual nodes:
    ServerA: positions  60, 180, 300
    ServerB: positions  30, 140, 250
    ServerC: positions  80, 200, 330

  Now the ring has 9 points for 3 servers.
  The arcs are much smaller and more evenly distributed.
  Each server handles roughly 1/3 of the ring on average.

  Virtual node ring (positions sorted):
    30=B,  60=A,  80=C,  140=B,  180=A,  200=C,  250=B,  300=A,  330=C

  Key @ position 100 → next clockwise = 140 (ServerB). Served by B.
  Key @ position 220 → next clockwise = 250 (ServerB). Served by B.

  More virtual nodes = smoother load distribution.
  Typical real systems use 100-200 virtual nodes per physical server.
  (Used by Cassandra, Amazon DynamoDB, Riak, and others.)
```

---

## 4. Rate Limiter (Token Bucket) — "A Bucket That Fills with Tokens Over Time"

### The Story

You're running an API. You want to allow users to make requests, but not
infinitely fast — that would crash your servers. You need rate limiting.

The **Token Bucket** algorithm is like this: imagine a bucket that:
- Holds at most **N tokens** (the "burst capacity")
- Fills at a steady rate of **R tokens per second**
- Each API request costs **1 token**
- If the bucket is empty → the request is **rejected** (or delayed)

This allows short bursts of traffic (use up tokens quickly) while enforcing
a long-term average rate (can't exceed R requests/second sustainably).

---

### Token Bucket Trace

**Setup:** Bucket capacity = 5 tokens. Refill rate = 2 tokens/second.

```
  Timeline:

  t=0s: Bucket starts full.
  ┌─────────────────────────────┐
  │  Bucket: ████████████ 5/5  │  (full)
  └─────────────────────────────┘

  t=0s: Request 1 arrives.
  → Take 1 token. Allowed.
  ┌─────────────────────────────┐
  │  Bucket: ████████████ 4/5  │
  └─────────────────────────────┘

  t=0s: Request 2 arrives immediately.
  → Take 1 token. Allowed.
  ┌─────────────────────────────┐
  │  Bucket: ████████████ 3/5  │
  └─────────────────────────────┘

  t=0s: Request 3 arrives immediately.
  → Take 1 token. Allowed.
  ┌─────────────────────────────┐
  │  Bucket: ████████████ 2/5  │
  └─────────────────────────────┘

  t=0s: Request 4 arrives immediately.
  → Take 1 token. Allowed.
  ┌─────────────────────────────┐
  │  Bucket: ████          1/5 │
  └─────────────────────────────┘

  t=0s: Request 5 arrives immediately.
  → Take 1 token. Allowed.
  ┌─────────────────────────────┐
  │  Bucket:               0/5 │  (EMPTY!)
  └─────────────────────────────┘

  5 requests came in at t=0. All allowed (burst capacity = 5).
  This is the "burst" feature of token bucket.

  t=0s: Request 6 arrives immediately.
  → No tokens! REJECTED.
  ┌─────────────────────────────┐
  │  Bucket:               0/5 │  Request 6: ✗ DENIED
  └─────────────────────────────┘

  t=0.5s: Half a second passes. +1 token refilled (rate=2/sec → 1 per 0.5s).
  ┌─────────────────────────────┐
  │  Bucket: ██            1/5 │
  └─────────────────────────────┘

  t=0.5s: Request 7 arrives.
  → Take 1 token. Allowed.
  ┌─────────────────────────────┐
  │  Bucket:               0/5 │
  └─────────────────────────────┘

  t=1.5s: 1 more second passes. +2 tokens refilled.
  ┌─────────────────────────────┐
  │  Bucket: ████          2/5 │
  └─────────────────────────────┘

  t=2.5s: Another second. +2 more tokens (capped at 5).
  ┌─────────────────────────────┐
  │  Bucket: ████████████ 4/5  │  (refilling toward full)
  └─────────────────────────────┘
```

---

### Token Bucket vs Sliding Window

```
  Token Bucket:
  ┌────────────────────────────────────────────────────────────┐
  │  ✓ Allows BURSTING — can fire all N tokens at once         │
  │  ✓ Simple — just track (tokens, last_refill_time)          │
  │  ✓ Smooth long-term rate                                   │
  │  ✗ A large burst at t=0 + another at t=window could        │
  │    exceed your "per window" intent                          │
  └────────────────────────────────────────────────────────────┘

  Sliding Window Log:
  ┌────────────────────────────────────────────────────────────┐
  │  Stores TIMESTAMPS of every request in the past window     │
  │  At each new request: evict timestamps older than window   │
  │  Count remaining = current request count in window         │
  │  ✓ Precise: never exceeds N requests per window           │
  │  ✗ Memory-heavy (stores all timestamps)                    │
  │  ✗ No burst handling                                       │
  └────────────────────────────────────────────────────────────┘

  Analogy:
  Token bucket = "here's 10 drink tickets for the night,
                  use them whenever you want"

  Sliding window = "you can only have 1 drink per hour,
                    tracked precisely"
```

---

### Code Sketch

```python
import time

class TokenBucketRateLimiter:
    def __init__(self, capacity: int, refill_rate: float):
        """
        capacity:    max tokens (burst size)
        refill_rate: tokens added per second
        """
        self.capacity = capacity
        self.tokens = capacity           # start full
        self.refill_rate = refill_rate
        self.last_refill = time.time()

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now

    def allow_request(self) -> bool:
        self._refill()
        if self.tokens >= 1:
            self.tokens -= 1
            return True    # ALLOWED
        return False       # DENIED — bucket empty
```

---

## 5. Bloom Filter — "A Quick 'Probably Yes / Definitely No' Checker"

### The Story

You're building a web crawler. Before fetching a URL, you want to know: "have
we already visited this URL?" You have billions of URLs in your history. Storing
all of them in a hash set would require gigabytes of RAM.

**The Bloom filter** is a space-efficient probabilistic data structure that
answers: **"Have we seen this before?"** with:
- **Definitely NO** — if the answer is no, it's 100% certain you've never seen it.
- **Probably YES** — if the answer is yes, there's a small chance it's wrong (false positive).

It uses a **bit array** and **multiple hash functions**. No false negatives.
Some false positives. Massive memory savings.

---

### The Bit Array and Hash Functions

```
  Setup:
    Bit array of size 16 (indexes 0–15), all initially 0.
    3 hash functions: h1, h2, h3

  Initial state:
  Index: 0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
  Bits:  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
```

---

### INSERT "apple"

```
  Compute hash positions:
    h1("apple") = 3
    h2("apple") = 7
    h3("apple") = 12

  Set bits at positions 3, 7, 12 to 1.

  Index: 0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
  Bits:  0  0  0  1  0  0  0  1  0  0  0  0  1  0  0  0
                  ▲           ▲              ▲
                 pos3        pos7           pos12
```

---

### INSERT "grape"

```
  h1("grape") = 1
  h2("grape") = 5
  h3("grape") = 12   ← 12 is already 1! That's fine, just leave it.

  Index: 0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
  Bits:  0  1  0  1  0  1  0  1  0  0  0  0  1  0  0  0
            ▲        ▲
           pos1     pos5   (pos12 already set, no change)
```

---

### QUERY "banana" — Definitely NOT in set

```
  h1("banana") = 3
  h2("banana") = 4
  h3("banana") = 9

  Check bits at positions 3, 4, 9:
    bit[3] = 1  ✓
    bit[4] = 0  ✗  ← this bit is 0!
    bit[9] = 0  ✗

  ANY bit is 0 → "banana" is DEFINITELY NOT in the set.

  Why definitely? Because if "banana" had been inserted, ALL of bits 3, 4, 9
  would have been set to 1. Since bit 4 is 0, "banana" was never inserted.

  Index: 0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
  Bits:  0  1  0  1  0  1  0  1  0  0  0  0  1  0  0  0
                    ▲  ↑
                   pos3=1  pos4=0 ← ZERO found! DEFINITELY NOT present.
```

---

### QUERY "cherry" — False Positive!

```
  h1("cherry") = 3
  h2("cherry") = 7
  h3("cherry") = 12

  Check bits at positions 3, 7, 12:
    bit[3] = 1  ✓
    bit[7] = 1  ✓
    bit[12] = 1  ✓

  ALL bits are 1 → Bloom filter says: "PROBABLY in the set."

  But wait — we NEVER inserted "cherry"! We only inserted "apple" and "grape".
  "cherry" has the same hash positions as "apple" (3,7,12).
  This is a FALSE POSITIVE.

  Index: 0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
  Bits:  0  1  0  1  0  1  0  1  0  0  0  0  1  0  0  0
                    ▲           ▲              ▲
                   pos3=1     pos7=1         pos12=1
                   All 1s → says "probably yes" → but it's WRONG!

  ┌──────────────────────────────────────────────────────────────┐
  │  The Bloom filter can LIE and say "probably yes" for items   │
  │  it never saw. This is a false positive.                     │
  │                                                              │
  │  It can NEVER lie and say "definitely no" for items it SAW.  │
  │  This is called "no false negatives."                        │
  └──────────────────────────────────────────────────────────────┘
```

---

### INSERT "mango" + QUERY to show more cases

```
  INSERT "mango":
    h1("mango") = 2
    h2("mango") = 9
    h3("mango") = 14

  Index: 0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
  Bits:  0  1  1  1  0  1  0  1  0  1  0  0  1  0  1  0
               ▲                    ▲             ▲
             pos2                 pos9          pos14

  QUERY "apple" (was inserted):
    h1=3, h2=7, h3=12
    bits[3]=1, bits[7]=1, bits[12]=1
    All 1. → "PROBABLY YES" → CORRECT (true positive)

  QUERY "kiwi":
    h1("kiwi") = 2
    h2("kiwi") = 5
    h3("kiwi") = 11
    bits[2]=1, bits[5]=1, bits[11]=0
    bit[11] = 0 → DEFINITELY NOT in set. Correct! (kiwi was never inserted)
```

---

### Final Bit Array State After All Inserts

```
  Inserted: "apple", "grape", "mango"

  Index: 0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
  Bits:  0  1  1  1  0  1  0  1  0  1  0  0  1  0  1  0
            │  │  │     │     │     │           │     │
           "grape" "apple" "grape" "mango"   "apple" "mango"
                  "apple"        "mango"

  (Some bits set by multiple items — e.g., bit 12 set by both "apple" AND "grape")
```

---

### Real-World Uses

```
  ┌─────────────────────────────────────────────────────────────┐
  │  Google Chrome Safe Browsing:                               │
  │    Chrome keeps a Bloom filter of known malicious URLs.     │
  │    Before visiting any URL, it checks the filter.           │
  │    "Definitely not malicious" → go ahead (fast, no server)  │
  │    "Probably malicious" → contact Google to verify          │
  │    Saves billions of server lookups per day.                 │
  │                                                             │
  │  Apache Cassandra:                                          │
  │    Before reading a row from disk (expensive!),             │
  │    Cassandra checks a Bloom filter: "is this row on disk?"  │
  │    "Definitely not" → skip the disk read. Huge speedup.     │
  │                                                             │
  │  Akamai CDN:                                                │
  │    Tracks which items to cache. Items seen only once         │
  │    (one-hit wonders) are filtered out via Bloom filter.     │
  │    Saves cache space for items that actually repeat.        │
  │                                                             │
  │  Bitcoin:                                                   │
  │    SPV clients use Bloom filters to download only relevant  │
  │    transactions without revealing their wallet addresses.   │
  └─────────────────────────────────────────────────────────────┘
```

---

### Tuning the False Positive Rate

```
  False positive rate (p) depends on:
    m = number of bits in the array
    n = number of items inserted
    k = number of hash functions

  Optimal formula:
    k = (m/n) * ln(2)     ← optimal number of hash functions
    p ≈ (1/2)^k           ← approximate false positive rate

  Practical tradeoffs:
  ┌──────────────┬────────────┬────────────┬────────────────────┐
  │  Bits/item   │ Hash funcs │ False pos  │ Example use case   │
  │  (m/n)       │ (k)        │ rate (p)   │                    │
  ├──────────────┼────────────┼────────────┼────────────────────┤
  │      5       │     3      │   9.2%     │ rough pre-filter    │
  │      8       │     5      │   2.1%     │ general use         │
  │     10       │     7      │   0.8%     │ low false pos need  │
  │     16       │    11      │   0.05%    │ very precise need   │
  └──────────────┴────────────┴────────────┴────────────────────┘

  A 10 million item Bloom filter at 8 bits/item:
    Memory: 10M * 8 bits = 10 MB  (vs 100+ MB for a hash set)
    False positive rate: ~2%
    Speed: O(k) per query — k hash computations, k bit lookups

  ┌────────────────────────────────────────────────────────────┐
  │  Bloom filters CANNOT delete items.                        │
  │  (Setting a bit to 0 might affect other items too.)        │
  │  Solution: Counting Bloom filter (store counts, not bits). │
  └────────────────────────────────────────────────────────────┘
```

---

### Code Sketch

```python
import hashlib
import math

class BloomFilter:
    def __init__(self, capacity: int, fp_rate: float):
        """
        capacity: expected number of items
        fp_rate:  desired false positive rate (e.g., 0.01 = 1%)
        """
        # Optimal bit array size
        self.size = self._optimal_size(capacity, fp_rate)
        # Optimal number of hash functions
        self.hash_count = self._optimal_k(self.size, capacity)
        self.bits = [0] * self.size

    def _optimal_size(self, n, p):
        return int(-n * math.log(p) / (math.log(2) ** 2))

    def _optimal_k(self, m, n):
        return int((m / n) * math.log(2))

    def _hashes(self, item: str):
        """Generate self.hash_count different hash positions."""
        positions = []
        for i in range(self.hash_count):
            h = hashlib.md5(f"{item}:{i}".encode()).hexdigest()
            positions.append(int(h, 16) % self.size)
        return positions

    def insert(self, item: str):
        for pos in self._hashes(item):
            self.bits[pos] = 1

    def query(self, item: str) -> bool:
        """
        Returns False → item is DEFINITELY NOT in set.
        Returns True  → item is PROBABLY in set (may be false positive).
        """
        return all(self.bits[pos] == 1 for pos in self._hashes(item))
```

---

## Quick Reference — All 5 Patterns

```
  Pattern              │ Core Idea                    │ Time   │ Space
  ─────────────────────┼──────────────────────────────┼────────┼────────────────
  LRU Cache            │ Evict least recently used    │ O(1)   │ O(capacity)
                       │ Doubly linked list + hashmap │        │
  LFU Cache            │ Evict least frequently used  │ O(1)   │ O(capacity)
                       │ freq_map + node_map          │        │
  Consistent Hashing   │ Keys on a ring, go to next   │ O(logN)│ O(nodes)
                       │ server clockwise             │ lookup │
  Token Bucket         │ Bucket fills at rate R,      │ O(1)   │ O(1) per user
  Rate Limiter         │ each request takes 1 token   │        │
  Bloom Filter         │ k hash functions, bit array  │ O(k)   │ O(m) bits
                       │ "probably yes/definitely no" │        │ (very small!)
```
