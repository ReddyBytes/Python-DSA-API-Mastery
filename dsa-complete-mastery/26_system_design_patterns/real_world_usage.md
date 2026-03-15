# System Design Patterns — Real-World Usage Guide

These six patterns appear in virtually every large-scale production system. Understanding not just
the algorithm but the exact production context — why it is used, what problem it solves, and how
it behaves under load — is what separates strong system design interviews from weak ones. Each
section includes full working Python code, a real production example, and trade-off analysis.

---

## Pattern 1 — LRU Cache

### What It Is

Least Recently Used (LRU) cache evicts the entry that was accessed least recently when the cache
is full. The assumption is that items accessed recently are more likely to be accessed again soon.

### Where It Appears in Production

- **Redis** with `maxmemory-policy allkeys-lru`: when Redis runs out of memory, it evicts the
  least recently used key across all keys.
- **CDN edge nodes**: when a CDN cache server is full, it evicts the least recently served content.
  A video served 3 weeks ago gets evicted before one served 5 minutes ago.
- **CPU L1/L2/L3 caches**: hardware cache replacement is often LRU-approximated.
- **Operating system page cache**: the kernel evicts least recently used memory pages first.
- **Browser cache**: browsers often use LRU-like policies for cached HTTP responses.

### The Data Structure

An LRU cache needs O(1) for both get (lookup by key) and put (insert/update with eviction):
- Hash map for O(1) key lookup → returns a node
- Doubly linked list for O(1) move-to-front and remove-least-recent operations
- The two are combined: the hash map stores keys → nodes, and the nodes are in a doubly linked list
  ordered by recency (head = most recent, tail = least recent).

### Implementation

```python
from __future__ import annotations
from typing import Optional, Any


class DLinkedNode:
    """Node in the doubly linked list."""
    def __init__(self, key: int = 0, value: Any = None):
        self.key = key
        self.value = value
        self.prev: Optional[DLinkedNode] = None
        self.next: Optional[DLinkedNode] = None


class LRUCache:
    """
    LRU Cache with O(1) get and put operations.

    Uses a doubly linked list (for O(1) remove/move) combined with a
    hash map (for O(1) key lookup). The list is ordered: head.next is
    the most recently used, tail.prev is the least recently used.

    head <-> [most recent] <-> ... <-> [least recent] <-> tail
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: dict[int, DLinkedNode] = {}

        # Sentinel nodes to avoid null checks at boundaries
        self.head = DLinkedNode()   # dummy head (most recent side)
        self.tail = DLinkedNode()   # dummy tail (least recent side)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _add_to_front(self, node: DLinkedNode) -> None:
        """Add node right after the head (mark as most recently used)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _remove_node(self, node: DLinkedNode) -> None:
        """Remove a node from the linked list (but not from the hash map)."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _move_to_front(self, node: DLinkedNode) -> None:
        """Move an existing node to the front (mark it as recently used)."""
        self._remove_node(node)
        self._add_to_front(node)

    def _remove_lru(self) -> DLinkedNode:
        """Remove and return the least recently used node (just before tail)."""
        lru_node = self.tail.prev
        self._remove_node(lru_node)
        return lru_node

    def get(self, key: int) -> Any:
        """
        Return the value of the key if it exists, else return -1.
        Accessing a key marks it as most recently used.
        """
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._move_to_front(node)  # mark as recently used
        return node.value

    def put(self, key: int, value: Any) -> None:
        """
        Insert or update a key-value pair.
        If cache is full after insert, evict the least recently used entry.
        """
        if key in self.cache:
            # Update existing entry and move to front
            node = self.cache[key]
            node.value = value
            self._move_to_front(node)
        else:
            # Create new node
            new_node = DLinkedNode(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)

            if len(self.cache) > self.capacity:
                # Evict the least recently used item
                lru = self._remove_lru()
                del self.cache[lru.key]

    def __len__(self) -> int:
        return len(self.cache)

    def __contains__(self, key: int) -> bool:
        return key in self.cache

    def peek_order(self) -> list:
        """Return keys in order from most recent to least recent (for debugging)."""
        result = []
        curr = self.head.next
        while curr != self.tail:
            result.append(curr.key)
            curr = curr.next
        return result


class CacheLayer:
    """
    Application-level cache layer wrapping LRUCache.
    Simulates a system where the cache sits in front of a database.

    Flow:
        get(key):
            1. Check cache — if hit, return immediately (cache hit)
            2. If miss, fetch from database (slow)
            3. Store in cache for future requests
            4. If cache full, LRU entry is automatically evicted

        put(key, value):
            1. Write to database (write-through strategy)
            2. Update cache entry
    """

    def __init__(self, capacity: int, db: dict):
        self.lru = LRUCache(capacity)
        self.db = db  # simulated database
        self.hits = 0
        self.misses = 0

    def get(self, key: int) -> Any:
        cached = self.lru.get(key)
        if cached != -1:
            self.hits += 1
            print(f"  CACHE HIT  key={key} → {cached}")
            return cached
        else:
            self.misses += 1
            value = self.db.get(key)
            if value is not None:
                self.lru.put(key, value)
                print(f"  CACHE MISS key={key}, fetched from DB → {value}")
            else:
                print(f"  NOT FOUND  key={key}")
            return value

    def put(self, key: int, value: Any) -> None:
        self.db[key] = value           # write-through: always write to DB
        self.lru.put(key, value)       # update cache
        print(f"  WRITE      key={key} = {value}")

    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


# Demo: CDN-like cache with capacity 3
def demo_lru():
    print("=== LRU Cache Demo ===\n")

    # Simulate a database of user profiles
    database = {
        1: "Alice",
        2: "Bob",
        3: "Charlie",
        4: "Diana",
        5: "Eve"
    }

    cache = CacheLayer(capacity=3, db=database)

    print("Fetching users 1, 2, 3 (all misses — cold cache):")
    cache.get(1)  # miss → fetch Alice, cache: [1]
    cache.get(2)  # miss → fetch Bob,   cache: [2, 1]
    cache.get(3)  # miss → fetch Charlie, cache: [3, 2, 1]
    print(f"Cache order (MRU→LRU): {cache.lru.peek_order()}")

    print("\nFetching user 1 again (hit — already cached):")
    cache.get(1)  # hit → cache: [1, 3, 2] (1 moved to front)
    print(f"Cache order (MRU→LRU): {cache.lru.peek_order()}")

    print("\nFetching user 4 (miss — cache full, evict LRU which is user 2):")
    cache.get(4)  # miss → evict 2, cache: [4, 1, 3]
    print(f"Cache order (MRU→LRU): {cache.lru.peek_order()}")

    print("\nFetching user 2 again (miss — was evicted):")
    cache.get(2)  # miss — 2 was evicted, must fetch from DB again
    print(f"Cache order (MRU→LRU): {cache.lru.peek_order()}")

    print(f"\nHit rate: {cache.hit_rate():.1%}")  # 1 hit / 5 requests = 20%

demo_lru()
```

### LRU vs FIFO vs Random

| Policy | Evicts | Best for | Worst for |
|---|---|---|---|
| LRU | Least recently used | Temporal locality (recent = hot) | Cyclic access patterns |
| FIFO | Oldest insertion | Predictable eviction | Hot items aged out |
| LFU | Least frequently used | Frequency locality | New items starved (cold-start) |
| Random | Random entry | Simplicity, no ordering overhead | Unpredictable hit rate |

---

## Pattern 2 — LFU Cache

### What It Is

Least Frequently Used (LFU) cache evicts the entry with the lowest access count when the cache
is full. Among entries with equal access counts, it uses LRU as a tiebreaker (evict the one
that was accessed least recently among the least frequent).

### Where It Appears in Production

- **News platforms**: a viral article accessed 10,000 times today should stay cached even if
  it was published yesterday. LRU would evict it if a burst of new articles came in — LFU keeps it.
- **Music streaming**: frequently played songs should stay in cache regardless of when they were
  last played. A user's 100 most-played songs should be in cache; LFU achieves this naturally.
- **Search autocomplete**: frequently searched prefixes should persist in cache.

### Key Difference from LRU

```
Access pattern: A, B, C, A, B, A (cache capacity = 2)
After these accesses: A=3 times, B=2 times, C=1 time

LRU: most recent is A, then B → evicts C if new item comes
LFU: A=3, B=2 → evicts C (frequency=1) if new item comes
     → Same result here!

Access pattern: A×5, B×1, C×1, then fetch D (cache capacity = 2, has B and C):
LRU: C was accessed before B → evicts C
LFU: B and C both have freq=1 → evict the older one (LRU tiebreaker) → evicts B
     → Depends on who was accessed more recently among the least frequent

The real difference shows when a frequently-used item hasn't been accessed recently:
Cache has: [A×100, B×1]. Access C (cache full, capacity 2).
LRU: A was accessed earlier than B → evicts A! (Wrong — A is hot)
LFU: B has frequency 1 < A's 100 → evicts B. (Correct — B is cold)
```

### Implementation

```python
from collections import defaultdict
from typing import Any, Optional


class DLinkedNode2:
    def __init__(self, key=0, value=None):
        self.key = key
        self.value = value
        self.freq = 1
        self.prev: Optional[DLinkedNode2] = None
        self.next: Optional[DLinkedNode2] = None


class FreqList:
    """Doubly linked list for a specific frequency bucket."""

    def __init__(self):
        self.head = DLinkedNode2()
        self.tail = DLinkedNode2()
        self.head.next = self.tail
        self.tail.prev = self.head
        self.size = 0

    def add_to_front(self, node: DLinkedNode2) -> None:
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
        self.size += 1

    def remove(self, node: DLinkedNode2) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev
        self.size -= 1

    def remove_last(self) -> Optional[DLinkedNode2]:
        if self.size == 0:
            return None
        last = self.tail.prev
        self.remove(last)
        return last

    def is_empty(self) -> bool:
        return self.size == 0


class LFUCache:
    """
    LFU Cache with O(1) get and put operations.

    Data structures:
        - key_map: key → DLinkedNode (for O(1) key lookup)
        - freq_map: frequency → FreqList (doubly linked list of nodes at that frequency)
        - min_freq: tracks the current minimum frequency for O(1) eviction

    When a node's frequency increases (on access):
        1. Remove it from freq_map[old_freq]
        2. Add it to freq_map[new_freq] at the front (LRU tiebreaker)
        3. If min_freq list is now empty, increment min_freq

    On eviction: remove the LAST node from freq_map[min_freq] (least frequent + least recent)
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.key_map: dict[int, DLinkedNode2] = {}
        self.freq_map: dict[int, FreqList] = defaultdict(FreqList)
        self.min_freq = 0

    def _increment_freq(self, node: DLinkedNode2) -> None:
        """Move node from its current frequency bucket to the next one."""
        old_freq = node.freq
        self.freq_map[old_freq].remove(node)

        if self.freq_map[old_freq].is_empty() and old_freq == self.min_freq:
            self.min_freq += 1

        node.freq += 1
        self.freq_map[node.freq].add_to_front(node)

    def get(self, key: int) -> Any:
        if key not in self.key_map:
            return -1
        node = self.key_map[key]
        self._increment_freq(node)
        return node.value

    def put(self, key: int, value: Any) -> None:
        if self.capacity <= 0:
            return

        if key in self.key_map:
            node = self.key_map[key]
            node.value = value
            self._increment_freq(node)
        else:
            if len(self.key_map) >= self.capacity:
                # Evict the least frequent (and least recent among them)
                evicted = self.freq_map[self.min_freq].remove_last()
                if evicted:
                    del self.key_map[evicted.key]

            new_node = DLinkedNode2(key, value)
            self.key_map[key] = new_node
            self.freq_map[1].add_to_front(new_node)
            self.min_freq = 1  # new nodes always start with frequency 1


# Direct comparison: LRU vs LFU on the same access pattern
def compare_lru_lfu():
    print("=== LRU vs LFU Comparison ===\n")

    # Scenario: A is a viral article (accessed many times early in the day).
    # B and C are new articles that arrive later. Cache capacity = 2.

    # Build up history: A accessed 5 times, B accessed 1 time
    lru = LRUCache(capacity=2)
    lfu = LFUCache(capacity=2)

    print("Initial accesses: A×5, B×1")
    for _ in range(5):
        lru.put("A", "viral article")
        lfu.put("A", "viral article")
    lru.put("B", "new article 1")
    lfu.put("B", "new article 1")

    print(f"LRU cache order: {lru.peek_order()}")  # B, A (B is more recent)

    # Access A once more to make it recent in LRU
    # but NOT in LFU — B has freq=1, A has freq=5+1=6 wait...
    # Let's see what happens when C arrives and cache is full (A, B present)

    # New article C arrives — cache is full, must evict something
    print("\nNew article C arrives (cache full, capacity=2):")
    print("LRU will evict: the least RECENTLY used item")
    print("LFU will evict: the least FREQUENTLY used item")

    # In LRU: order is [B (most recent), A] → evicts A (older)
    # In LFU: B has freq=1, A has freq=5 (or 6) → evicts B (less frequent)

    lru.put("C", "new article 2")
    lfu.put("C", "new article 2")

    print(f"\nLRU: can get A? {lru.get('A') != -1}")   # False — A was evicted!
    print(f"LRU: can get B? {lru.get('B') != -1}")   # True — B is still there
    print(f"LFU: can get A? {lfu.get('A') != -1}")   # True — A survives (high frequency)
    print(f"LFU: can get B? {lfu.get('B') != -1}")   # False — B was evicted (low frequency)

    print("\nConclusion:")
    print("  LRU evicted the viral article A (wasn't accessed most recently)")
    print("  LFU correctly kept the viral article A (most frequently accessed)")

compare_lru_lfu()
```

---

## Pattern 3 — Consistent Hashing

### What It Is

In a distributed cache with `N` servers, the naive approach assigns key to server via
`server = hash(key) % N`. The problem: when you add or remove a server, `N` changes, and
almost every key remaps to a different server — all cache data is invalidated simultaneously
(cache stampede).

Consistent hashing solves this. Keys and servers are placed on a circular ring (hash space
0 to 2^32-1). A key is stored on the first server clockwise from the key's position.
When adding/removing a server, only K/N keys need to move (where K = total keys, N = servers).

### Where It Appears in Production

- **Redis Cluster**: uses consistent hashing with hash slots (16384 slots mapped to nodes)
- **Memcached**: client-side consistent hashing for key distribution across servers
- **DynamoDB**: uses consistent hashing for partitioning
- **Apache Cassandra**: uses consistent hashing for token distribution
- **Nginx upstream hashing**: `hash $request_uri consistent`

### Virtual Nodes

A simple ring has uneven distribution — some servers might get far more keys than others
(especially with few servers). Virtual nodes solve this: each physical server is placed at
multiple positions on the ring (e.g., 100-200 virtual nodes per server). Keys are distributed
more evenly because each server "owns" many small arcs instead of one large arc.

### Implementation

```python
import hashlib
from collections import defaultdict


class ConsistentHashRing:
    """
    Consistent hash ring with virtual nodes.

    Each physical server is placed at `replicas` positions on the ring.
    Keys are assigned to the first server clockwise from the key's hash.

    Virtual node count (replicas) trade-off:
        - More replicas → better load balance, more memory
        - Fewer replicas → uneven distribution, less memory
        - Common values: 100-200 replicas per server

    Time complexity:
        - add_server: O(replicas * log(replicas * num_servers))
        - remove_server: O(replicas * log(replicas * num_servers))
        - get_server: O(log(replicas * num_servers))
    """

    def __init__(self, replicas: int = 150):
        self.replicas = replicas
        self.ring: dict[int, str] = {}          # hash → server_name
        self.sorted_keys: list[int] = []         # sorted list of hash positions
        self.servers: set[str] = set()

    def _hash(self, key: str) -> int:
        """Return a 32-bit hash of the key using MD5."""
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2 ** 32)

    def _virtual_node_key(self, server: str, replica_idx: int) -> str:
        """Generate the key for a virtual node: 'server_name#replica_idx'"""
        return f"{server}#{replica_idx}"

    def add_server(self, server: str) -> None:
        """
        Add a server to the ring by placing `replicas` virtual nodes.
        Keys previously assigned to the successor server in the affected arcs
        now belong to the new server.
        """
        if server in self.servers:
            return
        self.servers.add(server)

        for i in range(self.replicas):
            virtual_key = self._virtual_node_key(server, i)
            h = self._hash(virtual_key)
            self.ring[h] = server

            # Insert h into sorted_keys maintaining sorted order
            import bisect
            bisect.insort(self.sorted_keys, h)

    def remove_server(self, server: str) -> None:
        """
        Remove a server from the ring.
        Its keys are automatically reassigned to the next clockwise server.
        """
        if server not in self.servers:
            return
        self.servers.discard(server)

        import bisect
        for i in range(self.replicas):
            virtual_key = self._virtual_node_key(server, i)
            h = self._hash(virtual_key)
            del self.ring[h]
            idx = bisect.bisect_left(self.sorted_keys, h)
            if idx < len(self.sorted_keys) and self.sorted_keys[idx] == h:
                self.sorted_keys.pop(idx)

    def get_server(self, key: str) -> str:
        """
        Find the server responsible for the given key.
        Returns the first server clockwise from the key's hash position.
        """
        if not self.ring:
            raise RuntimeError("No servers in the ring")

        import bisect
        h = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, h)

        # Wrap around: if key hash is beyond all server positions, use first server
        if idx == len(self.sorted_keys):
            idx = 0

        return self.ring[self.sorted_keys[idx]]

    def get_distribution(self, keys: list[str]) -> dict[str, int]:
        """Count how many of the given keys map to each server."""
        distribution: dict[str, int] = defaultdict(int)
        for key in keys:
            server = self.get_server(key)
            distribution[server] += 1
        return dict(distribution)


# Demo: show that adding a server moves only K/N keys
def demo_consistent_hashing():
    print("=== Consistent Hashing Demo ===\n")

    ring = ConsistentHashRing(replicas=150)

    # Start with 3 servers
    ring.add_server("server-1")
    ring.add_server("server-2")
    ring.add_server("server-3")

    # Generate 1000 sample keys
    keys = [f"user:{i}" for i in range(1000)]

    print("Initial distribution (3 servers, 150 virtual nodes each):")
    dist_before = ring.get_distribution(keys)
    for server, count in sorted(dist_before.items()):
        pct = count / len(keys) * 100
        print(f"  {server}: {count} keys ({pct:.1f}%)")
    # With 150 virtual nodes, expect roughly 33% each

    # Record where each key was before adding server-4
    assignments_before = {key: ring.get_server(key) for key in keys}

    # Add a new server
    ring.add_server("server-4")

    print("\nAfter adding server-4:")
    dist_after = ring.get_distribution(keys)
    for server, count in sorted(dist_after.items()):
        pct = count / len(keys) * 100
        print(f"  {server}: {count} keys ({pct:.1f}%)")

    # Count how many keys moved
    moved = sum(
        1 for key in keys
        if assignments_before[key] != ring.get_server(key)
    )
    print(f"\nKeys moved when adding server-4: {moved}/{len(keys)} ({moved/len(keys)*100:.1f}%)")
    print(f"Expected ~25% (K/N = 1000/4 = 250 keys)")
    # Compare to naive %N hashing: ~75% of keys would move!

    # Remove a server
    assignments_before_remove = {key: ring.get_server(key) for key in keys}
    ring.remove_server("server-2")

    moved_on_remove = sum(
        1 for key in keys
        if assignments_before_remove[key] != ring.get_server(key)
    )
    print(f"\nKeys moved when removing server-2: {moved_on_remove}/{len(keys)} ({moved_on_remove/len(keys)*100:.1f}%)")
    print(f"Expected ~25% (those that were on server-2 now move to successor)")

demo_consistent_hashing()
```

### The Math: Why Only K/N Keys Move

With N servers and K keys uniformly distributed:
- Adding 1 server: the new server takes 1/N fraction of the ring → K/N keys move
- Removing 1 server: its keys redistribute to neighbors → K/N keys move

With naive `hash(key) % N`:
- Adding server: N changes to N+1 → most keys change server (roughly (N-1)/N = ~67% at N=3)
- This means a sudden load surge when a new server joins — all clients suddenly cache-miss

---

## Pattern 4 — Rate Limiter

### What It Is

A rate limiter prevents clients from making too many requests in a time window. It is the
first line of defense against API abuse, DDoS attacks, and accidental runaway clients.

### Where It Appears in Production

- **AWS API Gateway**: `throttle` setting with burst limit and rate limit
- **Nginx**: `limit_req_zone` directive (leaky bucket algorithm)
- **Cloudflare**: rate limiting rules at the CDN edge
- **Stripe API**: 100 requests/second per API key
- **GitHub API**: 5000 requests/hour for authenticated users
- **Twitter API**: 300 requests per 15-minute window

### Token Bucket vs Sliding Window

**Token Bucket**: a bucket holds up to `capacity` tokens. Tokens refill at `rate` per second.
Each request consumes 1 token. If the bucket is empty, request is denied. Allows bursts up to
`capacity` in size.

**Sliding Window Log**: maintains a list of timestamps of recent requests. A request is allowed
if fewer than `limit` requests were made in the last `window_size` seconds. No bursting — exactly
`limit` per window regardless of timing.

**Fixed Window Counter**: count requests in a fixed time window (e.g., "100 per minute,
resetting at :00 each minute"). Simple but has edge case: 100 at 11:59 + 100 at 12:00 = 200
in a 2-second window around midnight.

### Implementation

```python
import time
from collections import deque
from threading import Lock


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter.

    Tokens accumulate over time at `refill_rate` tokens/second.
    Bucket capacity is capped at `capacity`.
    Each request consumes `cost` tokens (default 1).

    Allows bursting: if no requests have been made, the bucket fills
    up and then a burst of `capacity` requests is allowed instantly.

    Properties:
        - Long-term average rate: refill_rate requests/second
        - Short burst allowed: up to capacity requests instantly
        - Smooth over time — not hard window
    """

    def __init__(self, capacity: float, refill_rate: float):
        """
        capacity:    maximum tokens (and maximum burst size)
        refill_rate: tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity           # start with full bucket
        self.last_refill = time.monotonic()
        self.lock = Lock()

    def _refill(self) -> None:
        """Add tokens based on elapsed time since last refill."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        added = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + added)
        self.last_refill = now

    def allow_request(self, cost: float = 1.0) -> bool:
        """
        Attempt to consume `cost` tokens. Return True if allowed, False if denied.

        Thread-safe via lock.
        """
        with self.lock:
            self._refill()
            if self.tokens >= cost:
                self.tokens -= cost
                return True
            return False

    def tokens_available(self) -> float:
        """Return current number of available tokens (for monitoring/debugging)."""
        with self.lock:
            self._refill()
            return self.tokens


class SlidingWindowRateLimiter:
    """
    Sliding window log rate limiter.

    Maintains a log of request timestamps. On each request:
    1. Remove all timestamps older than window_size seconds
    2. If log size < limit: allow request, add timestamp
    3. Else: deny request

    This gives exact rate limiting with no fixed-window edge case.

    Trade-off: O(1) amortized per request, but stores all timestamps in the window.
    For limit=1000, stores up to 1000 timestamps. For limit=1,000,000, this is too much memory.
    In that case, use token bucket or fixed window counter.
    """

    def __init__(self, limit: int, window_size: float):
        """
        limit:       maximum requests allowed in window_size seconds
        window_size: size of the sliding window in seconds
        """
        self.limit = limit
        self.window_size = window_size
        self.requests: deque[float] = deque()  # timestamps of recent requests
        self.lock = Lock()

    def allow_request(self) -> bool:
        """Return True if request is allowed, False if rate limit exceeded."""
        with self.lock:
            now = time.monotonic()
            cutoff = now - self.window_size

            # Remove expired timestamps from the front of the deque
            while self.requests and self.requests[0] <= cutoff:
                self.requests.popleft()

            if len(self.requests) < self.limit:
                self.requests.append(now)
                return True
            return False

    def current_count(self) -> int:
        """Number of requests in the current window."""
        with self.lock:
            now = time.monotonic()
            cutoff = now - self.window_size
            while self.requests and self.requests[0] <= cutoff:
                self.requests.popleft()
            return len(self.requests)


# Demo: compare burst behavior
def demo_rate_limiters():
    print("=== Rate Limiter Comparison ===\n")
    print("Scenario: limit = 5 requests per second")
    print("Test 1: 10 rapid requests (burst)\n")

    # Token bucket: capacity=5, refill_rate=5/sec → allows burst of 5
    token_bucket = TokenBucketRateLimiter(capacity=5, refill_rate=5)

    # Sliding window: 5 requests per 1 second — no burst beyond 5
    sliding_window = SlidingWindowRateLimiter(limit=5, window_size=1.0)

    rapid_requests = 10

    tb_results = []
    sw_results = []

    for i in range(rapid_requests):
        tb_results.append(token_bucket.allow_request())
        sw_results.append(sliding_window.allow_request())

    print("Token Bucket results (10 rapid requests):")
    for i, allowed in enumerate(tb_results):
        status = "ALLOWED" if allowed else "DENIED"
        print(f"  Request {i+1:2d}: {status}")
    print(f"  Allowed: {sum(tb_results)}/10  ← burst of 5 allowed, rest denied")

    print("\nSliding Window results (10 rapid requests):")
    for i, allowed in enumerate(sw_results):
        status = "ALLOWED" if allowed else "DENIED"
        print(f"  Request {i+1:2d}: {status}")
    print(f"  Allowed: {sum(sw_results)}/10  ← exactly 5 allowed, rest denied")

    print("\n--- Both behave identically on bursts in this case ---")
    print("Key difference: after burst, token bucket refills gradually.")
    print("Token bucket allows next burst after 1 second (5 tokens refilled).")
    print("Sliding window allows 5 more only when the oldest request exits the window.")
    print("\nReal difference emerges in Test 2: 10 requests spread over 2 seconds")
    print("(Requests 1-5 at t=0, requests 6-10 at t=1.1 seconds)")
    print("  Token bucket: allows all 10 (5 refilled by t=1.0)")
    print("  Sliding window: allows all 10 (first 5 expired by t=1.1)")
    print("  → Both allow, but token bucket would also allow a burst at t=1.0,")
    print("    while sliding window counts from exact timestamps")

demo_rate_limiters()
```

---

## Pattern 5 — Top-K with Heap

### What It Is

Finding the K most common, K largest, or K most relevant items from a stream of events.
A min-heap of size K maintains the top K items: we push new items and if the heap exceeds
size K, we pop the minimum (smallest of the top K). At the end, the heap contains the top K.

### Where It Appears in Production

- **Twitter/X**: trending topics — top 10 hashtags from billions of tweets
- **YouTube**: trending videos, top comments
- **Google Analytics**: top 100 most visited pages
- **Stock trading**: top gainers/losers of the day
- **Log analysis**: most frequent error messages in production logs
- **Recommendation engines**: top K relevant products for a user

### Why Not Sort?

Sorting 1,000,000 items is O(n log n). Finding top K with a heap is O(n log K).
When K << n (e.g., K=10, n=1,000,000), this is O(n log 10) ≈ O(n) — much faster.

### Implementation

```python
import heapq
from collections import defaultdict
from typing import TypeVar, Hashable

T = TypeVar("T", bound=Hashable)


class TopKTracker:
    """
    Tracks the top K most frequent items in a stream of events.

    Internally uses:
    - A Counter (hash map) to count occurrences of each item
    - A min-heap of size K to maintain the current top K

    process_event: O(1) average (hash map update)
    get_top_k: O(n log K) where n = distinct items seen
               Can be made O(K log K) if called frequently by maintaining
               a sorted structure, but this simpler version is fine for
               batch top-K retrieval.

    Space: O(n) for the counter, O(K) for the heap
    """

    def __init__(self, k: int):
        self.k = k
        self.counts: dict[T, int] = defaultdict(int)
        self.total_events = 0

    def process_event(self, item: T) -> None:
        """Record one occurrence of item."""
        self.counts[item] += 1
        self.total_events += 1

    def process_batch(self, items: list[T]) -> None:
        """Process a batch of events efficiently."""
        for item in items:
            self.counts[item] += 1
        self.total_events += len(items)

    def get_top_k(self) -> list[tuple[T, int]]:
        """
        Return the K most frequent items as list of (item, count) tuples,
        sorted by count descending.

        Uses heapq.nlargest which is O(n log K) — more efficient than
        sorting all n items when K is small.
        """
        return heapq.nlargest(self.k, self.counts.items(), key=lambda x: x[1])

    def get_top_k_realtime(self) -> list[tuple[T, int]]:
        """
        Maintain a min-heap of size K for real-time top-K.
        This is the manual approach showing the heap mechanism.

        For each item in counts:
            - If heap size < K: push it
            - Else if item's count > heap minimum: pop minimum, push item

        Returns sorted list of (item, count) descending by count.
        """
        min_heap: list[tuple[int, T]] = []  # (count, item)

        for item, count in self.counts.items():
            if len(min_heap) < self.k:
                heapq.heappush(min_heap, (count, item))
            elif count > min_heap[0][0]:  # larger than current minimum
                heapq.heapreplace(min_heap, (count, item))

        # Sort the K results by count descending
        result = [(item, count) for count, item in min_heap]
        result.sort(key=lambda x: x[1], reverse=True)
        return result

    def top_k_percentage(self) -> list[tuple[T, float]]:
        """Return top K items with their percentage share of total events."""
        top = self.get_top_k()
        return [(item, count / self.total_events * 100) for item, count in top]


# Demo: Twitter trending topics
def demo_top_k():
    print("=== Top-K Trending Topics Demo ===\n")

    tracker = TopKTracker(k=10)

    # Simulate 1,000,000 tweet hashtags with skewed distribution
    # A few hashtags are very popular (viral), most are niche
    import random

    # Viral hashtags — appear many times
    viral = ["#WorldCup", "#TaylorSwift", "#BlackFriday", "#AI", "#Elections2026"]
    # Popular hashtags
    popular = [f"#Topic{i}" for i in range(20)]
    # Long tail — thousands of niche hashtags
    niche = [f"#Niche{i}" for i in range(5000)]

    print("Simulating 1,000,000 tweet hashtags...")
    all_hashtags = (
        viral * 50000 +      # viral: each appears ~50,000 times
        popular * 5000 +     # popular: each ~5,000 times
        niche * 10            # niche: each ~10 times
    )

    import random
    random.shuffle(all_hashtags)

    tracker.process_batch(all_hashtags)

    print(f"Total tweets processed: {tracker.total_events:,}")
    print(f"Distinct hashtags seen: {len(tracker.counts):,}")

    print("\nTop 10 Trending Hashtags:")
    print(f"{'Rank':<6} {'Hashtag':<25} {'Count':>10} {'Share':>8}")
    print("-" * 52)
    for rank, (hashtag, count) in enumerate(tracker.get_top_k(), 1):
        pct = count / tracker.total_events * 100
        print(f"{rank:<6} {hashtag:<25} {count:>10,} {pct:>7.2f}%")

    # Demonstrate real-time heap approach gives same results
    top_realtime = tracker.get_top_k_realtime()
    top_standard = tracker.get_top_k()
    assert [item for item, _ in top_realtime] == [item for item, _ in top_standard], \
        "Both methods should return same top-K"
    print("\nBoth heap approaches return identical results.")

demo_top_k()
```

---

## Pattern 6 — Skip List

### What It Is

A skip list is a probabilistic data structure that provides O(log n) average time for search,
insert, and delete — the same as a balanced BST. Unlike a BST, it is simpler to implement
correctly and naturally supports concurrent operations.

### Where It Appears in Production

- **Redis Sorted Sets** (`ZSET`): internally uses a skip list for rank operations.
  `ZRANK`, `ZRANGE`, `ZRANGEBYSCORE` — all run in O(log n) via the skip list.
  The Redis source code explicitly comments this: `zskiplistNode` is the skip list node.
- **LevelDB / RocksDB**: uses a skip list for the in-memory MemTable (before flushing to SSTable)
- **Apache Lucene**: skip list pointers in inverted index posting lists for fast intersection
- **CockroachDB**: skip list used in the MVCC layer

### How It Works

A skip list has multiple layers. The bottom layer (level 0) is a regular sorted linked list
containing all elements. Each higher level is a "fast lane" containing a subset of elements —
roughly half of the level below (promoted with 50% probability). Search starts at the top level
and drops down when the next element is too large:

```
Level 3: 1 ─────────────────────────────────────────── 50 ── NIL
Level 2: 1 ──────────── 12 ────────────────── 38 ───── 50 ── NIL
Level 1: 1 ──── 5 ────── 12 ── 17 ─────────── 38 ───── 50 ── NIL
Level 0: 1 ─ 3 ─ 5 ─ 9 ─ 12 ─ 17 ─ 21 ─ 25 ─ 38 ─ 42 ─ 50 ── NIL
```

Searching for 21: start at level 3 (1→50, 21<50, drop to 3), level 2 (1→12→38, 21<38, drop
after 12), level 1 (12→17→38, 21<38, drop after 17), level 0 (17→21, found!).
This took O(log n) steps instead of O(n).

### Implementation

```python
import random
from typing import Optional, Any


class SkipListNode:
    """A node in the skip list."""
    def __init__(self, key: float, value: Any, level: int):
        self.key = key
        self.value = value
        # forward[i] is the next node at level i
        self.forward: list[Optional[SkipListNode]] = [None] * (level + 1)


class SkipList:
    """
    Skip list implementation supporting O(log n) search, insert, delete.

    Parameters:
        max_level: maximum number of levels (log2(expected_n) is a good choice)
        p: probability of a node being promoted to the next level (typically 0.5)

    Space: O(n) average (each node has O(1/p) pointers on average = O(1) for p=0.5)
    """

    MAX_LEVEL = 16   # supports up to 2^16 = 65536 elements efficiently

    def __init__(self, max_level: int = MAX_LEVEL, p: float = 0.5):
        self.max_level = max_level
        self.p = p
        self.level = 0  # current maximum level in use

        # Sentinel head node with -inf key at all levels
        self.head = SkipListNode(float('-inf'), None, max_level)

    def _random_level(self) -> int:
        """
        Randomly determine the level for a new node.
        With probability p, promote to the next level.
        Returns a level in range [0, max_level].
        """
        level = 0
        while random.random() < self.p and level < self.max_level:
            level += 1
        return level

    def search(self, key: float) -> Optional[Any]:
        """
        Search for key. Return its value if found, else None.
        Time complexity: O(log n) average
        """
        curr = self.head

        # Start from the highest level and work down
        for i in range(self.level, -1, -1):
            while curr.forward[i] and curr.forward[i].key < key:
                curr = curr.forward[i]
            # curr.forward[i] is None or >= key — drop down one level

        # We are now at level 0 — check if next node is the target
        curr = curr.forward[0]
        if curr and curr.key == key:
            return curr.value
        return None

    def insert(self, key: float, value: Any) -> None:
        """
        Insert (key, value). If key exists, update its value.
        Time complexity: O(log n) average
        """
        # update[i] = the rightmost node at level i that is < key
        # We will update its forward pointers to point to the new node
        update = [None] * (self.max_level + 1)
        curr = self.head

        for i in range(self.level, -1, -1):
            while curr.forward[i] and curr.forward[i].key < key:
                curr = curr.forward[i]
            update[i] = curr

        # Check if key already exists (update value)
        curr = curr.forward[0]
        if curr and curr.key == key:
            curr.value = value
            return

        # New key — determine its level
        new_level = self._random_level()

        # If new node's level exceeds current max level, extend update array
        if new_level > self.level:
            for i in range(self.level + 1, new_level + 1):
                update[i] = self.head
            self.level = new_level

        new_node = SkipListNode(key, value, new_level)

        # Splice new node into the list at each level up to new_level
        for i in range(new_level + 1):
            new_node.forward[i] = update[i].forward[i]
            update[i].forward[i] = new_node

    def delete(self, key: float) -> bool:
        """
        Delete the node with the given key. Return True if found and deleted.
        Time complexity: O(log n) average
        """
        update = [None] * (self.max_level + 1)
        curr = self.head

        for i in range(self.level, -1, -1):
            while curr.forward[i] and curr.forward[i].key < key:
                curr = curr.forward[i]
            update[i] = curr

        curr = curr.forward[0]
        if not curr or curr.key != key:
            return False  # key not found

        # Remove node from each level where it appears
        for i in range(self.level + 1):
            if update[i].forward[i] != curr:
                break
            update[i].forward[i] = curr.forward[i]

        # Update level if top levels are now empty
        while self.level > 0 and self.head.forward[self.level] is None:
            self.level -= 1

        return True

    def range_query(self, lo: float, hi: float) -> list[tuple[float, Any]]:
        """
        Return all (key, value) pairs where lo <= key <= hi, in sorted order.
        Time complexity: O(log n + K) where K is the number of results.
        """
        result = []
        curr = self.head

        # Find the first node >= lo using skip list navigation
        for i in range(self.level, -1, -1):
            while curr.forward[i] and curr.forward[i].key < lo:
                curr = curr.forward[i]

        curr = curr.forward[0]  # first node >= lo

        # Collect all nodes up to hi
        while curr and curr.key <= hi:
            result.append((curr.key, curr.value))
            curr = curr.forward[0]

        return result

    def __str__(self) -> str:
        """Visualize the skip list level structure."""
        lines = []
        for lvl in range(self.level, -1, -1):
            curr = self.head.forward[lvl]
            keys = []
            while curr:
                keys.append(str(curr.key))
                curr = curr.forward[lvl]
            lines.append(f"Level {lvl}: {' → '.join(keys)}")
        return "\n".join(lines)


# Demo: Redis-like sorted set operations
def demo_skip_list():
    print("=== Skip List Demo (Redis ZSET Operations) ===\n")

    sl = SkipList()

    # Insert player scores (like Redis ZADD)
    players = [
        (1500, "Alice"),
        (2300, "Bob"),
        (890,  "Charlie"),
        (3100, "Diana"),
        (1750, "Eve"),
        (2800, "Frank"),
        (650,  "Grace"),
        (4200, "Henry"),
        (1200, "Iris"),
        (3500, "Jack"),
    ]

    for score, player in players:
        sl.insert(score, player)

    print("Skip list structure:")
    print(sl)

    # ZRANK equivalent: search for specific score
    print(f"\nSearch for score 2300: {sl.search(2300)}")   # Bob
    print(f"Search for score 9999: {sl.search(9999)}")    # None

    # ZRANGEBYSCORE equivalent: find players with scores 1000-2500
    print(f"\nPlayers with score 1000-2500 (ZRANGEBYSCORE):")
    for score, player in sl.range_query(1000, 2500):
        print(f"  {player}: {score}")

    # Update score (delete + insert)
    sl.delete(1500)
    sl.insert(1600, "Alice")
    print(f"\nAfter updating Alice's score to 1600:")
    print(f"  Search 1500: {sl.search(1500)}")  # None
    print(f"  Search 1600: {sl.search(1600)}")  # Alice

    # Delete a player
    removed = sl.delete(650)
    print(f"\nRemoved Grace (score 650): {removed}")
    print(f"  Search 650: {sl.search(650)}")  # None

    print("\n--- Skip List vs BST Comparison ---")
    comparison = [
        ("Search", "O(log n) avg", "O(log n) balanced"),
        ("Insert", "O(log n) avg", "O(log n) balanced"),
        ("Delete", "O(log n) avg", "O(log n) balanced"),
        ("Range query", "O(log n + K)", "O(log n + K)"),
        ("Rebalancing", "None needed (probabilistic)", "AVL/Red-Black rotations"),
        ("Concurrent access", "Easier to implement", "Complex rotation locking"),
        ("Memory", "O(n) avg pointers", "O(n) pointers"),
        ("Cache friendliness", "Moderate (linked nodes)", "Moderate (linked nodes)"),
        ("Implementation", "~100 lines", "~150-200 lines"),
    ]

    print(f"\n{'Operation':<25} {'Skip List':<35} {'BST (balanced)'}")
    print("-" * 85)
    for op, sl_val, bst_val in comparison:
        print(f"{op:<25} {sl_val:<35} {bst_val}")

demo_skip_list()
```

---

## Summary: When to Use Each Pattern

```
Problem characteristic                         → Pattern to use
──────────────────────────────────────────────────────────────
Cache with fixed size, evict oldest access     → LRU Cache
Cache where access frequency matters more      → LFU Cache
Distribute keys across N servers, add/remove   → Consistent Hashing
  servers with minimal data migration
Limit API calls per user per time window       → Token Bucket (allow bursts)
  with bursty traffic                            or Sliding Window (exact limit)
Find top K most frequent items in stream       → Min-Heap of size K (Top-K)
Sorted set with O(log n) rank + range queries  → Skip List (or BST)
```

### Production Reality: These Patterns Compose

In a real system, multiple patterns work together:

1. API Gateway uses **Rate Limiter** to allow 1000 req/sec per client
2. If request passes, check **LRU Cache** (Redis, maxmemory-policy = allkeys-lru)
3. Redis Cluster uses **Consistent Hashing** to distribute cache shards
4. If cache miss, query database; trending query results use **Top-K heap** to find hot items
5. Redis Sorted Sets for leaderboard use **Skip List** internally for ZRANGE operations

Understanding how these pieces fit together — not just each in isolation — is what makes a
senior engineer's system design answer compelling.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Caching Strategies](./caching_strategies.md) &nbsp;|&nbsp; **Next:** [Common Mistakes →](./common_mistakes.md)

**Related Topics:** [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Caching Strategies](./caching_strategies.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
