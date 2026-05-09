<a id="top"></a>
# System Design Patterns — From Algorithms to Real Systems

> Data Structures solve problems.
> System Design scales them.
>
> This is where DSA meets the real world.

In this section, we study:

1. LRU Cache
2. LFU Cache
3. Rate Limiter
4. Consistent Hashing
5. Caching Strategies
6. Bloom Filter

These are extremely common in backend and system design interviews.

## 📖 Table of Contents

1. [LRU Cache — Least Recently Used](#1-lru-cache)
2. [LFU Cache — Least Frequently Used](#2-lfu-cache)
3. [Rate Limiter — Controlling Traffic](#3-rate-limiter)
4. [Consistent Hashing](#4-consistent-hashing)
5. [Caching Strategies](#5-caching-strategies)
6. [Bloom Filter](#6-bloom-filter)
7. [Trade-Off Discussion](#7-trade-off-discussion)
8. [Connecting DSA to System Design](#8-connecting-dsa-to-system-design)
9. [Mental Model](#9-mental-model)
10. [Final Understanding](#10-final-understanding)

## 📌 Learning Priority

These are extremely common in backend and system design interviews.

- LRU Cache: Must know cold
- Rate Limiter: Must know trade-offs between algorithms
- Consistent Hashing: Critical for distributed systems interviews
- Bloom Filter: Bonus — shows depth

<a id="1-lru-cache"></a>
# 1. LRU Cache — Least Recently Used

## Real Life Example

Picture a small bookshelf in your office. It holds exactly 3 books. You're a
developer who keeps reference books on hand. Whenever you need a book, you grab
it from the shelf (fast!). If the book isn't on the shelf, you have to go to the
library (slow — a cache miss) and bring it back.

But the shelf only holds 3 books. When you bring a new book and the shelf is
full, you put back the book you haven't opened in the longest time. That's
the Least Recently Used eviction policy.

When memory is full, it deletes apps you haven't used recently.

That is LRU policy.

## Problem

Design a cache that:

- Stores key-value pairs
- Has fixed capacity
- Removes least recently used item when full
- Supports get and put in O(1)

## Data Structures Used

To achieve O(1):

Use:

- Hashmap (for fast lookup)
- Doubly linked list (for order tracking)

Why?

Hashmap:
O(1) access.

Linked list:
O(1) insert/delete.

Together:
Perfect combination.

## Visual: Internal Structure

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

## Operations

### get(key)

- If exists:
  Move node to front.
- Else:
  Return -1.

### put(key, value)

- If key exists:
  Update value.
  Move to front.
- If capacity exceeded:
  Remove tail node.

## Visual: Operations Trace

**Initial State:**

```
  Cache capacity: 3
  Hash map: {}
  List: DUMMY_HEAD ↔ DUMMY_TAIL
```

**put(1, "Book A")**

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

**put(2, "Book B") then put(3, "Book C")**

```
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

**get(1) — cache hit, moves to front**

```
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
```

**put(4, "Book D") — cache is FULL, must EVICT**

```
  Must evict LRU item: that's [2] (the tail of our list, before DUMMY_TAIL).

  Steps:
    1. Find LRU = node before DUMMY_TAIL = node 2
    2. Remove node 2 from list (O(1) — doubly linked!)
    3. Remove key 2 from hash map (O(1))
    4. Insert new node 4 at HEAD

  After eviction + insert:
    HEAD ↔ [4] ↔ [1] ↔ [3] ↔ TAIL

  Cache state:
  ┌────────────────────────────────────┐
  │  [4] ← MRU (just inserted)         │
  │  [1]                               │
  │  [3] ← LRU                         │
  └────────────────────────────────────┘
  Hash map: {1 → node1, 3 → node3, 4 → node4}
  (key 2 has been evicted — gone!)
```

**Common mistake — dict + O(n) reorder:** Using a regular dict and rebuilding it to reorder elements costs O(n) per access. Use `OrderedDict.move_to_end()` or a doubly-linked list + dict for true O(1).

**Common mistake — no MRU move on get or existing-key put:** Both `get` and `put` (for an existing key) count as accesses and must move the node to the MRU position. Forgetting either causes recently-accessed keys to be wrongly evicted.

## Visual: Code Skeleton

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

## Time Complexity

get → O(1)
put → O(1)

## Real-World Usage

- Browser caching
- Database query caching
- CDN
- Memory management
- OS page replacement

LRU is extremely common.

📝 Practice: [Q1 LRU OrderedDict](./practice.md#q1--lru-cache--ordereddict-implementation) · [Q2 Eviction trace](./practice.md#q2--lru-cache--what-gets-evicted) · [Q3 MRU bug fix](./practice.md#q3--lru-cache--move-to-mru-on-get-and-put) · [Q4 DLL implementation](./practice.md#q4--lru-cache--doubly-linked-list-implementation)

> [↑ Back to Top](#top)

<a id="2-lfu-cache"></a>
# 2. LFU Cache — Least Frequently Used

## Real Life Example

LFU (Least Frequently Used) is the strict librarian who tracks not just WHEN
you used a book, but HOW MANY TIMES total. When the shelf is full, out goes
the book you've accessed the fewest times overall. If two books have the same
access count, the tiebreaker is recency (LRU among equals).

## LRU vs LFU

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

## Internal Structure

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

## Visual: LFU Operations Trace

**Initial State:**

```
  capacity = 3
  node_map = {}
  freq_map = {}
  min_freq = 0
```

**put(1, 'a') then put(2, 'b')**

```
  Both new keys inserted with frequency 1.

  freq_map = {1: OrderedDict([(1,node1), (2,node2)])}
  min_freq = 1

  Frequency buckets:
  freq=1: [1, 2]    ← 1 inserted first (LRU), 2 inserted second
```

**get(1) — cache hit, freq of key 1 goes 1→2**

```
  Step 1: Find node 1 in node_map (freq=1).
  Step 2: Remove key 1 from freq_map[1].
  Step 3: Increment node 1's freq to 2.
  Step 4: Add node 1 to freq_map[2].
  Step 5: If freq_map[1] is now empty AND min_freq was 1 → min_freq becomes 2.

  freq_map[1]: OrderedDict([(2, node2)])   ← only key 2 remains at freq 1
  freq_map[2]: OrderedDict([(1, node1)])   ← key 1 moved to freq 2

  Frequency buckets:
  freq=1: [2]       ← key 2 is the least frequently used
  freq=2: [1]       ← key 1 has been accessed twice
```

**put(3, 'c') fills cache, then put(4, 'd') forces eviction**

```
  After put(3,'c') — cache full at 3/3:
  freq=1: [2, 3]    ← both at freq 1; key 2 is LRU of this group
  freq=2: [1]
  min_freq = 1

  put(4,'d') — FULL, must evict:
  Look at freq_map[min_freq] = freq_map[1]
  The LRU node in freq=1 bucket is the FIRST entry = key 2.
  EVICT key 2.

  ┌──────────────────────────────────────────────────────┐
  │  FREQ=2  │  key 1 (val='a') — accessed twice         │
  │  FREQ=1  │  key 3, key 4    — accessed once each     │
  │                                                      │
  │  key 2 is GONE                                       │
  └──────────────────────────────────────────────────────┘
```

**Common mistake — removing from wrong frequency bucket:** When a key's frequency goes from f to f+1, you must remove it from `freq_map[f]` (the OLD bucket), not `freq_map[f+1]`. Deleting from the new bucket leaves a ghost entry in the old one, causing wrong evictions.

**Common mistake — min_freq not reset after inserting new key:** Any new key always starts at frequency 1. After inserting a new key, `min_freq` must be reset to 1, regardless of what it was before. Forgetting this causes eviction from an empty or wrong bucket.

## Visual: LFU Code Skeleton

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

> [↑ Back to Top](#top)

<a id="3-rate-limiter"></a>
# 3. Rate Limiter — Controlling Traffic

## Real Life Example

A toll gate allows only 10 cars per minute.

If more cars arrive,
some must wait.

That is rate limiting.

The Token Bucket algorithm: imagine a bucket that holds at most N tokens (the
"burst capacity"), fills at a steady rate of R tokens per second, and each API
request costs 1 token. If the bucket is empty, the request is rejected.

This allows short bursts of traffic while enforcing a long-term average rate.

## Problem

Limit number of requests per user per time window.

Example:
100 requests per minute.

## Common Algorithms

### Fixed Window Counter

Track:

Count per time window.

Simple but bursty.

### Sliding Window Log

Store timestamps.

Remove old timestamps.

More accurate.

### Token Bucket

Bucket fills at steady rate.

Each request consumes token.

If no tokens → reject.

Allows bursts.

### Leaky Bucket

Processes at constant rate.

Queue-based.

## Visual: Token Bucket Trace

**Setup:** Bucket capacity = 5 tokens. Refill rate = 2 tokens/second.

```
  t=0s: Bucket starts full.
  ┌─────────────────────────────┐
  │  Bucket: ████████████ 5/5  │  (full)
  └─────────────────────────────┘

  t=0s: Requests 1–5 arrive immediately.
  → Each takes 1 token. All allowed.
  ┌─────────────────────────────┐
  │  Bucket:               0/5 │  (EMPTY!)
  └─────────────────────────────┘
  5 requests at t=0 — all allowed (burst capacity = 5).

  t=0s: Request 6 arrives.
  → No tokens! REJECTED.
  ┌─────────────────────────────┐
  │  Bucket:               0/5 │  Request 6: ✗ DENIED
  └─────────────────────────────┘

  t=0.5s: +1 token refilled (rate=2/sec → 1 per 0.5s).
  ┌─────────────────────────────┐
  │  Bucket: ██            1/5 │
  └─────────────────────────────┘

  t=0.5s: Request 7 arrives. → Take 1 token. Allowed.

  t=2.5s: Full refill in progress.
  ┌─────────────────────────────┐
  │  Bucket: ████████████ 4/5  │  (refilling toward full)
  └─────────────────────────────┘
```

## Visual: Token Bucket vs Sliding Window

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

**Common mistake — Leaky Bucket for burst-ok APIs:** Leaky Bucket enforces a constant output rate with no burst tolerance. Use Token Bucket when clients should be allowed to burst after periods of low usage (e.g., GitHub API hourly quota). Use Leaky Bucket only when downstream services need a strictly steady input rate.

## Visual: Token Bucket Code Sketch

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

## Time Complexity

Depends on implementation.

Usually O(1) or O(log n).

## Real-World Usage

- API gateways
- Payment systems
- Login attempts
- Cloud services
- Microservices

Rate limiting protects systems.

📝 Practice: [Q6 Token Bucket](./practice.md#q6--token-bucket--allow-burst-traffic) · [Q9 Sliding Window](./practice.md#q9--sliding-window-rate-limiter) · [Q10 Leaky vs Token Bucket](./practice.md#q10--leaky-bucket-vs-token-bucket-trade-offs)

> [↑ Back to Top](#top)

<a id="4-consistent-hashing"></a>
# 4. Consistent Hashing

## Real Life Example

Imagine a food delivery service. You have drivers (servers) handling orders
(keys). Each order is assigned to a driver based on the order's ID.

The naive approach: `driver = order_id % num_drivers`

Works fine... until you add or remove a driver.

```
  3 drivers: order_id % 3

  Now you hire a 4th driver: order_id % 4

  Order 3  → driver 3%4 = 3  (was 0, now 3) CHANGED
  Order 4  → driver 4%4 = 0  (was 1, now 0) CHANGED
  Order 5  → driver 5%4 = 1  (was 2, now 1) CHANGED

  3 out of 5 orders (60%) had to be reassigned!
  In a real system: cache misses, data migration, chaos.
```

The consistent hashing solution: almost no reassignment when you add/remove
a node. Only the keys between the new node and its predecessor move.

## Visual: The Ring

```
  Imagine a clock face — a ring with positions 0 to 2^32-1.

  Step 1: Hash each SERVER to a position on the ring.
    hash("ServerA") = position 60
    hash("ServerB") = position 150
    hash("ServerC") = position 270

  Step 2: Hash each KEY to a position on the ring.
  Step 3: A key is handled by the FIRST SERVER clockwise from the key's position.

  Ring positions:
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
  K1 @ 20  → ServerA @ 60   → K1 served by A
  K2 @ 80  → ServerB @ 150  → K2 served by B
  K3 @ 130 → ServerB @ 150  → K3 served by B
  K4 @ 200 → ServerC @ 270  → K4 served by C
  K5 @ 310 → ServerA @ 60   → K5 served by A
             (wraps around: 310 → passes 360/0 → hits A at 60)
```

## Visual: Adding a New Server

```
  We add ServerD at position 100.

  New assignment:
  K1 @ 20  → ServerA @ 60    → K1 still served by A  (no change)
  K2 @ 80  → ServerD @ 100   → K2 NOW served by D    ← MOVED
  K3 @ 130 → ServerB @ 150   → K3 still served by B  (no change)

  Only K2 moved! (1 out of 5 = 20%)
  With naive hashing, it was ~60%.

  ┌──────────────────────────────────────────────────────────────┐
  │  Adding a server only affects keys in the "arc" between      │
  │  the new server and its predecessor.                         │
  │  Everything else is completely unaffected.                   │
  └──────────────────────────────────────────────────────────────┘
```

## Visual: Virtual Nodes

```
  Problem: With only 3 servers, the arcs might be very uneven.
  ServerA might handle 50% of the ring, ServerB 10%, ServerC 40%.
  This causes load imbalance.

  Solution: Virtual nodes — each PHYSICAL server maps to MULTIPLE
  positions on the ring.

  Example: Each server gets 3 virtual nodes:
    ServerA: positions  60, 180, 300
    ServerB: positions  30, 140, 250
    ServerC: positions  80, 200, 330

  Virtual node ring (positions sorted):
    30=B,  60=A,  80=C,  140=B,  180=A,  200=C,  250=B,  300=A,  330=C

  More virtual nodes = smoother load distribution.
  Typical real systems use 100-200 virtual nodes per physical server.
  (Used by Cassandra, Amazon DynamoDB, Riak, and others.)
```

**Common mistake — too few virtual nodes:** With only 1 node per server on the ring, load distribution is wildly uneven and removing one server dumps all its traffic onto a single neighbor. Use 150+ virtual nodes per server to ensure even distribution and graceful failover.

> [↑ Back to Top](#top)

<a id="5-caching-strategies"></a>
# 5. Caching Strategies

Caching improves performance.

But strategy matters.

## Cache Aside (Lazy Loading)

Application:

1. Check cache.
2. If miss:
   Fetch from DB.
   Store in cache.

Most common.

## Write Through

Write to cache and DB simultaneously.

Strong consistency.

## Write Back (Write Behind)

Write to cache first.
Later update DB.

High performance.
Risky.

## Refresh Ahead

Update cache before expiration.

Used for hot data.

📝 Practice: [Q11 Caching strategies](./practice.md#q11--caching-strategy--cache-aside-write-through-write-back) · [Q12 Eviction policies](./practice.md#q12--cache-eviction-policies--lru-lfu-fifo-random)

> [↑ Back to Top](#top)

<a id="6-bloom-filter"></a>
# 6. Bloom Filter

## Real Life Example

You're building a web crawler. Before fetching a URL, you want to know: "have
we already visited this URL?" You have billions of URLs in your history. Storing
all of them in a hash set would require gigabytes of RAM.

The Bloom filter is a space-efficient probabilistic data structure that
answers: "Have we seen this before?" with:
- Definitely NO — if the answer is no, it's 100% certain you've never seen it.
- Probably YES — if the answer is yes, there's a small chance it's wrong (false positive).

It uses a bit array and multiple hash functions. No false negatives.
Some false positives. Massive memory savings.

## Visual: Bit Array and Hash Functions

```
  Setup:
    Bit array of size 16 (indexes 0–15), all initially 0.
    3 hash functions: h1, h2, h3

  Initial state:
  Index: 0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
  Bits:  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0

  INSERT "apple":
    h1("apple") = 3,  h2("apple") = 7,  h3("apple") = 12
    Set bits at positions 3, 7, 12 to 1.

  Index: 0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
  Bits:  0  0  0  1  0  0  0  1  0  0  0  0  1  0  0  0
                  ▲           ▲              ▲

  INSERT "grape":
    h1("grape") = 1,  h2("grape") = 5,  h3("grape") = 12
    (pos 12 already 1 — fine, leave it)

  Index: 0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
  Bits:  0  1  0  1  0  1  0  1  0  0  0  0  1  0  0  0
```

## Visual: Query — Definitely Not vs False Positive

```
  QUERY "banana":
    h1=3, h2=4, h3=9
    bit[3]=1 ✓  bit[4]=0 ✗
    ANY bit is 0 → "banana" is DEFINITELY NOT in the set.

  QUERY "cherry":
    h1=3, h2=7, h3=12
    bit[3]=1 ✓  bit[7]=1 ✓  bit[12]=1 ✓
    ALL bits are 1 → Bloom filter says "PROBABLY in the set."
    But "cherry" was NEVER inserted! Same hash positions as "apple".
    This is a FALSE POSITIVE.

  ┌──────────────────────────────────────────────────────────────┐
  │  The Bloom filter can LIE and say "probably yes" for items   │
  │  it never saw. This is a false positive.                     │
  │                                                              │
  │  It can NEVER lie and say "definitely no" for items it SAW.  │
  │  This is called "no false negatives."                        │
  └──────────────────────────────────────────────────────────────┘
```

## Visual: Tuning the False Positive Rate

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

  ┌────────────────────────────────────────────────────────────┐
  │  Bloom filters CANNOT delete items.                        │
  │  (Setting a bit to 0 might affect other items too.)        │
  │  Solution: Counting Bloom filter (store counts, not bits). │
  └────────────────────────────────────────────────────────────┘
```

**Common mistake — wrong number of hash functions:** Using k=1 regardless of m and n gives ~9.5% false positive rate when the optimal k=7 would give ~0.8%. Use `k = (m/n) * ln(2)` to compute the optimal number of hash functions for your bit array size and expected element count.

## Real-World Uses

```
  ┌─────────────────────────────────────────────────────────────┐
  │  Google Chrome Safe Browsing:                               │
  │    Chrome keeps a Bloom filter of known malicious URLs.     │
  │    "Definitely not malicious" → go ahead (no server call)   │
  │    "Probably malicious" → contact Google to verify          │
  │                                                             │
  │  Apache Cassandra:                                          │
  │    Before reading a row from disk (expensive!),             │
  │    Cassandra checks a Bloom filter: "is this row on disk?"  │
  │    "Definitely not" → skip the disk read. Huge speedup.     │
  │                                                             │
  │  Bitcoin:                                                   │
  │    SPV clients use Bloom filters to download only relevant  │
  │    transactions without revealing their wallet addresses.   │
  └─────────────────────────────────────────────────────────────┘
```

> [↑ Back to Top](#top)

<a id="7-trade-off-discussion"></a>
# 7. Trade-Off Discussion

| Strategy | Pros | Cons |
|----------|------|------|
| Cache Aside | Simple | Stale data risk |
| Write Through | Consistent | Slower writes |
| Write Back | Fast | Data loss risk |
| Token Bucket | Smooth bursts | Implementation complexity |
| LRU | Simple O(1) | Doesn't account for frequency |
| LFU | Frequency-aware eviction | More complex, higher memory |
| Consistent Hashing | Minimal redistribution on change | Virtual nodes add complexity |
| Bloom Filter | Massive memory savings | False positives, no deletion |

Interviewers expect trade-off reasoning.

> [↑ Back to Top](#top)

<a id="8-connecting-dsa-to-system-design"></a>
# 8. Connecting DSA to System Design

LRU:
Uses hashmap + linked list.

LFU:
Uses freq_map (OrderedDict buckets) + node_map.

Rate limiter:
Uses queue, hashmap, timestamps.

Consistent hashing:
Uses sorted array + binary search on ring positions.

Bloom filter:
Uses bit array + multiple hash functions.

Caching:
Uses hashing, TTL logic.

DSA knowledge directly applies.

> [↑ Back to Top](#top)

<a id="9-mental-model"></a>
# 9. Mental Model

Think of system design as:

Applying DSA under real-world constraints:

- Memory limit
- Concurrency
- Failures
- Network delay
- Data consistency

System design is applied DSA at scale.

📝 Practice: [Q13 Consistent Hashing](./practice.md#q13--consistent-hashing--ring-with-virtual-nodes) · [Q15 Bloom Filter](./practice.md#q15--bloom-filter--insert-and-query) · [Q16 Top-K Min-Heap](./practice.md#q16--top-k--min-heap-of-size-k) · [Q20 System Composition](./practice.md#q20--system-composition--rate-limiter--lru--consistent-hashing)

> [↑ Back to Top](#top)

<a id="10-final-understanding"></a>
# 10. Final Understanding

System Design Patterns are:

- Real-world extensions of DSA
- Used in backend systems
- Critical for senior interviews
- About trade-offs and scaling

Mastering this prepares you for:

- Backend interviews
- Infrastructure roles
- Senior software engineer roles
- System architecture discussions

This is where coding meets real engineering.

## Navigation

Previous:
[25_advanced_graphs/interview.md](/02_DSA_Mastery/25_advanced_graphs/interview.md)

Next:
[26_system_design_patterns/interview.md](/02_DSA_Mastery/26_system_design_patterns/interview.md)
[99_interview_master/0_2_years.md](/02_DSA_Mastery/99_interview_master/0_2_years.md)

**[Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheetsheet.md) &nbsp;|&nbsp; **Next:** [Real World Usage →](./real_world_usage.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)

> [↑ Back to Top](#top)
