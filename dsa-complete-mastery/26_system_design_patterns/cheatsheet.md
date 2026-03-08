# System Design Patterns — Cheatsheet

---

## Complexity Reference

| Data Structure / Pattern    | Access    | Search    | Insert    | Delete    | Space   |
|-----------------------------|-----------|-----------|-----------|-----------|---------|
| LRU Cache (get/put)         | O(1)      | O(1)      | O(1)      | O(1)      | O(k)    |
| LFU Cache (get/put)         | O(1)      | O(1)      | O(1)      | O(1)      | O(k)    |
| Priority Queue (heapq)      | O(1) top  | O(n)      | O(log n)  | O(log n)  | O(n)    |
| Skip List                   | O(log n)  | O(log n)  | O(log n)  | O(log n)  | O(n log n)|
| Bloom Filter                | —         | O(k)      | O(k)      | N/A       | O(m)    |
| Consistent Hashing (lookup) | —         | O(log n)  | O(log n)  | O(log n)  | O(n+v)  |

---

## LRU Cache

**Strategy:** Hash map (O(1) lookup) + Doubly-linked list (O(1) insert/delete).
Most-recently-used at head, least-recently-used at tail.

### Using OrderedDict (Pythonic — interview preferred)

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.cache = OrderedDict()   # maintains insertion order

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)  # mark as recently used
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.cap:
            self.cache.popitem(last=False)   # evict LRU (front)
```

### Doubly-Linked List + HashMap (explicit — shows deeper understanding)

```python
class Node:
    def __init__(self, key=0, val=0):
        self.key, self.val = key, val
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.cache = {}
        self.head, self.tail = Node(), Node()   # sentinel nodes
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_front(self, node):            # insert after head
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key not in self.cache: return -1
        node = self.cache[key]
        self._remove(node)
        self._insert_front(node)
        return node.val

    def put(self, key, value):
        if key in self.cache:
            self._remove(self.cache[key])
        node = Node(key, value)
        self.cache[key] = node
        self._insert_front(node)
        if len(self.cache) > self.cap:
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]
```

---

## LFU Cache

**Strategy:** Two hash maps + min-frequency tracker.
- `key_to_val_freq`: {key: (value, frequency)}
- `freq_to_keys`: {frequency: OrderedDict of keys (ordered by recency)}
- `min_freq`: current minimum frequency

```python
from collections import defaultdict, OrderedDict

class LFUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.min_freq = 0
        self.key_map = {}                          # key -> [val, freq]
        self.freq_map = defaultdict(OrderedDict)   # freq -> {key: None}

    def _update(self, key):
        val, freq = self.key_map[key]
        del self.freq_map[freq][key]
        if not self.freq_map[freq] and self.min_freq == freq:
            self.min_freq += 1
        self.key_map[key] = [val, freq + 1]
        self.freq_map[freq + 1][key] = None

    def get(self, key):
        if key not in self.key_map: return -1
        self._update(key)
        return self.key_map[key][0]

    def put(self, key, value):
        if self.cap <= 0: return
        if key in self.key_map:
            self.key_map[key][0] = value
            self._update(key)
        else:
            if len(self.key_map) >= self.cap:
                evict_key, _ = self.freq_map[self.min_freq].popitem(last=False)
                del self.key_map[evict_key]
            self.key_map[key] = [value, 1]
            self.freq_map[1][key] = None
            self.min_freq = 1
```

---

## Rate Limiter Patterns

### Token Bucket

```python
import time

class TokenBucket:
    def __init__(self, rate, capacity):
        self.rate = rate           # tokens added per second
        self.capacity = capacity   # max tokens
        self.tokens = capacity
        self.last_refill = time.time()

    def allow_request(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity,
                          self.tokens + elapsed * self.rate)
        self.last_refill = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
# Allows bursts up to capacity; smooth average rate
```

### Sliding Window Counter

```python
from collections import deque

class SlidingWindowRateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window = window_seconds
        self.timestamps = deque()

    def allow_request(self):
        now = time.time()
        # Remove timestamps outside window
        while self.timestamps and now - self.timestamps[0] > self.window:
            self.timestamps.popleft()
        if len(self.timestamps) < self.max_requests:
            self.timestamps.append(now)
            return True
        return False
# Exact but memory-heavy; each request stores timestamp
```

**Rate Limiter Comparison:**

| Pattern          | Memory     | Accuracy | Allows Burst | Notes               |
|------------------|------------|----------|--------------|---------------------|
| Fixed window     | O(1)       | Low      | Yes (edge)   | Simplest            |
| Sliding window   | O(requests)| High     | Controlled   | More accurate       |
| Token bucket     | O(1)       | High     | Yes          | Smooth average rate |
| Leaky bucket     | O(1)       | High     | No           | Strict output rate  |

---

## Priority Queue Patterns

```python
import heapq

# Min-heap (default in Python)
heap = []
heapq.heappush(heap, (priority, item))
priority, item = heapq.heappop(heap)

# Max-heap: negate priority
heapq.heappush(heap, (-priority, item))

# K largest elements
def k_largest(nums, k):
    return heapq.nlargest(k, nums)        # O(n log k)

# Merge K sorted lists
def merge_k_sorted(lists):
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(heap)
    result = []
    while heap:
        val, i, j = heapq.heappop(heap)
        result.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j+1], i, j+1))
    return result

# Lazy deletion (mark as deleted, skip on pop)
deleted = set()
def lazy_pop(heap, deleted):
    while heap and heap[0][1] in deleted:
        heapq.heappop(heap)
    return heapq.heappop(heap) if heap else None
```

---

## Consistent Hashing

```
Concept: Map both servers and keys to positions on a virtual ring [0, 2^32).
- Keys are assigned to the next clockwise server on the ring.
- Adding/removing a server only remaps ~K/n keys (K=total keys, n=servers).
- Virtual nodes: each server occupies multiple ring positions for balance.

Python sketch:
  ring = SortedDict()         # position -> server
  for server in servers:
      for replica in range(virtual_nodes):
          pos = hash(f"{server}:{replica}") % RING_SIZE
          ring[pos] = server

  def get_server(key):
      pos = hash(key) % RING_SIZE
      idx = ring.bisect_left(pos) % len(ring)
      return ring.peekitem(idx)[1]

Use cases: distributed caches, CDN routing, load balancers.
```

---

## Bloom Filter

```
Concept: Space-efficient probabilistic set membership test.
- Uses k hash functions, each mapping to one of m bits.
- Insert: set bits at all k hash positions.
- Lookup: check all k positions — if any is 0, element is DEFINITELY NOT in set.
          If all are 1, element is PROBABLY in set (false positives possible).

Properties:
- NO false negatives (if in set, always returns true)
- False positive rate: (1 - e^(-kn/m))^k  where n = inserted elements
- Cannot delete elements (use Counting Bloom Filter for deletion)
- Space: O(m) bits regardless of element size

Use cases: database query pre-filter, cache negative lookups, spam detection.

Python: pip install pybloom-live
from pybloom_live import BloomFilter
bf = BloomFilter(capacity=1000, error_rate=0.01)
bf.add("item"); "item" in bf
```

---

## Skip List

```
Concept: Probabilistic layered linked list providing O(log n) average operations.
- Level 0: complete sorted linked list
- Level i: subset of level i-1 (each node promoted with probability p=0.5)
- Search: start from top-left, go right until overshoot, drop down, repeat.

Properties:
- O(log n) average search, insert, delete (expected with high probability)
- O(n) worst case (degenerate — rare with random promotion)
- Simpler to implement than balanced BSTs
- Supports range queries naturally

Use cases: Redis sorted sets, in-memory databases, range query indexes.

Levels: ~log(n) expected levels, each node has a tower of forward pointers.
```

---

## Gotchas

- LRU with `OrderedDict`: `move_to_end(key, last=True)` moves to back (most recent); `popitem(last=False)` removes front (least recent)
- LFU: updating frequency must handle `min_freq` bump only when the old-freq bucket becomes empty
- Token bucket: compute elapsed time in `allow_request()`, not in a background thread
- Heap in Python is min-heap; for max-heap negate values (or use `(-priority, item)`)
- Bloom filter false positive rate increases as more elements are added — size upfront
- Consistent hashing without virtual nodes causes hotspots when server counts are small
- Priority queue with lazy deletion: heap size can grow — periodically rebuild if needed
