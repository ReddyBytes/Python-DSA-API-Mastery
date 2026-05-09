# 💻 Practice — System Design Patterns

## Quick Index

| Q# | Topic | Difficulty |
|---|---|---|
| [Q1](#q1) | LRU Cache — OrderedDict implementation | 🟢 Easy |
| [Q2](#q2) | LRU Cache — what gets evicted | 🟢 Easy |
| [Q3](#q3) | LRU Cache — move to MRU on get AND put | 🟢 Easy |
| [Q4](#q4) | LRU Cache — doubly linked list implementation | 🟢 Easy |
| [Q5](#q5) | LFU Cache — frequency bucket structure | 🟢 Easy |
| [Q6](#q6) | Token Bucket — allow burst traffic | 🟢 Easy |
| [Q7](#q7) | LFU Cache — correct eviction with min_freq | 🟡 Medium |
| [Q8](#q8) | LFU Cache — LRU vs LFU on same access pattern | 🟡 Medium |
| [Q9](#q9) | Sliding Window rate limiter | 🟡 Medium |
| [Q10](#q10) | Leaky Bucket vs Token Bucket trade-offs | 🟡 Medium |
| [Q11](#q11) | Caching Strategy — Cache-Aside, Write-Through, Write-Back | 🟡 Medium |
| [Q12](#q12) | Cache eviction policies — LRU, LFU, FIFO, Random | 🟡 Medium |
| [Q13](#q13) | Consistent Hashing — ring with virtual nodes | 🟡 Medium |
| [Q14](#q14) | Consistent Hashing — why virtual nodes | 🟡 Medium |
| [Q15](#q15) | Bloom Filter — insert and query | 🟡 Medium |
| [Q16](#q16) | Top-K — min-heap of size K | 🟠 Hard |
| [Q17](#q17) | Bloom Filter — optimal k and false positive rate | 🟠 Hard |
| [Q18](#q18) | Consistent Hashing — keys moved on server add/remove | 🟠 Hard |
| [Q19](#q19) | LFU Cache — min_freq reset bug | 🟠 Hard |
| [Q20](#q20) | System Composition — Rate Limiter + LRU + Consistent Hashing | 🟠 Hard |

---

<a id="q1"></a>
### Q1 · LRU Cache — OrderedDict Implementation

🟢 Easy

**Problem:** Implement an LRU Cache using Python's `OrderedDict`. Support `get(key)` and `put(key, value)`. Both operations must run in O(1). When the cache is full, evict the least recently used entry.

```
Operations on LRUCache(capacity=2):
  put(1, 10) → cache: {1:10}
  put(2, 20) → cache: {1:10, 2:20}
  get(1)     → 10, cache: {2:20, 1:10}  (1 is now MRU)
  put(3, 30) → evict LRU (key 2), cache: {1:10, 3:30}
  get(2)     → -1 (evicted)
```

<details>
<summary>💡 Hint</summary>

`OrderedDict.move_to_end(key)` moves an entry to the end in O(1) — this is the MRU side. `popitem(last=False)` removes the front entry in O(1) — this is the LRU side. Call `move_to_end` on EVERY `get` and on existing-key `put`.

</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)   # mark as MRU
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)   # update recency even on update
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # evict LRU (front)

# Test
lru = LRUCache(2)
lru.put(1, 10); lru.put(2, 20)
assert lru.get(1) == 10        # hit, 1 → MRU
lru.put(3, 30)                 # evict 2 (LRU)
assert lru.get(2) == -1        # 2 was evicted
assert lru.get(1) == 10        # still there
assert lru.get(3) == 30        # still there
print("LRU OrderedDict: passed")
```

**Why:** `OrderedDict` wraps a doubly-linked list internally. `move_to_end` and `popitem` are both O(1) because they just relink pointers — no scanning. This gives O(1) get and put, exactly what the LRU contract requires.

</details>

> 💻 Try it: [practice_local.py → Q1](./practice_local.py)

---

<a id="q2"></a>
### Q2 · LRU Cache — What Gets Evicted

🟢 Easy

**Problem:** Given these operations on `LRUCache(capacity=3)`, trace what is in the cache after each step, and predict what gets evicted when the 4th entry is added.

```
put(1, "a")
put(2, "b")
put(3, "c")
get(1)          ← accesses key 1
put(4, "d")     ← cache full, must evict
```

What key is evicted when `put(4, "d")` is called?

<details>
<summary>💡 Hint</summary>

After `get(1)`, key 1 becomes the most recently used. Work out the LRU order after each operation. The LRU is always the item that was accessed longest ago.

</details>

<details>
<summary>✅ Answer</summary>

```python
# Trace:
# put(1,"a") → order (LRU→MRU): [1]
# put(2,"b") → order: [1, 2]
# put(3,"c") → order: [1, 2, 3]    ← 1 is LRU
# get(1)     → 1 moves to MRU: [2, 3, 1]   ← 2 is now LRU
# put(4,"d") → full, evict LRU = key 2

from collections import OrderedDict

class LRUCache:
    def __init__(self, cap):
        self.cap = cap
        self.cache = OrderedDict()

    def get(self, k):
        if k not in self.cache: return -1
        self.cache.move_to_end(k)
        return self.cache[k]

    def put(self, k, v):
        if k in self.cache:
            self.cache.move_to_end(k)
        self.cache[k] = v
        if len(self.cache) > self.cap:
            self.cache.popitem(last=False)

lru = LRUCache(3)
lru.put(1, "a"); lru.put(2, "b"); lru.put(3, "c")
lru.get(1)          # key 1 → MRU, order: [2, 3, 1]
lru.put(4, "d")     # evicts key 2 (LRU)
assert lru.get(2) == -1   # evicted
assert lru.get(1) == "a"  # still there (it was MRU before put(4))
assert lru.get(3) == "c"
assert lru.get(4) == "d"
print("Key 2 was evicted. Correct.")
```

**Why:** After `get(1)`, the LRU order is `[2, 3, 1]` — key 2 is the least recently used. When `put(4,"d")` fills the cache, key 2 is evicted. The `get` call promoted key 1, saving it from eviction despite being the oldest insertion.

</details>

> 💻 Try it: [practice_local.py → Q2](./practice_local.py)

---

<a id="q3"></a>
### Q3 · LRU Cache — Move to MRU on Get AND Put

🟢 Easy

**Problem:** The following LRU implementation has a bug. Identify it, explain what goes wrong, and fix it.

```python
from collections import OrderedDict

class LRUBuggy:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        return self.cache[key]   # BUG

    def put(self, key, value):
        if key in self.cache:
            self.cache[key] = value  # BUG
        else:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
            self.cache[key] = value
```

<details>
<summary>💡 Hint</summary>

LRU policy: both `get` (reading a key) and `put` on an existing key (updating a key) count as accesses. Both must move the key to the MRU position. If you forget either one, a recently-accessed or recently-updated key could be wrongly evicted.

</details>

<details>
<summary>✅ Answer</summary>

```python
# Bug 1: get() returns value but does NOT call move_to_end(key).
#         A recently read key keeps its old position → may be evicted as "LRU."
#
# Bug 2: put() on an existing key updates the value but does NOT call move_to_end(key).
#         A recently updated key may still be evicted as "LRU."

from collections import OrderedDict

class LRUFixed:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)   # FIX: mark as MRU on read
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)   # FIX: mark as MRU on update
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

# Proof: accessing key 1 should prevent it from being evicted next
lru = LRUFixed(2)
lru.put(1, 10); lru.put(2, 20)
lru.get(1)           # key 1 → MRU; key 2 → LRU
lru.put(3, 30)       # evict key 2 (LRU), not key 1
assert lru.get(1) == 10   # key 1 survived because get() moved it to MRU
assert lru.get(2) == -1   # key 2 was evicted
print("Bug fixed. get() and put() both call move_to_end.")
```

**Why:** The LRU contract is "evict whoever was accessed least recently." Both reads and writes are accesses. Missing `move_to_end` on either breaks this contract — the cache evicts the wrong item, causing spurious cache misses for data that was recently used.

</details>

> 💻 Try it: [practice_local.py → Q3](./practice_local.py)

---

<a id="q4"></a>
### Q4 · LRU Cache — Doubly Linked List Implementation

🟢 Easy

**Problem:** Implement LRU Cache using an explicit doubly linked list and a dict (no `OrderedDict`). This is the approach required in interviews where library shortcuts are not allowed.

Use dummy head and tail sentinel nodes. Head = LRU side, tail = MRU side.

<details>
<summary>💡 Hint</summary>

You need three helpers: `_remove(node)` — unlink from wherever it is; `_insert_before_tail(node)` — place as MRU. For `get`: find via dict, call `_remove` then `_insert_before_tail`. For `put`: if capacity exceeded, evict `head.next` (the LRU node).

</details>

<details>
<summary>✅ Answer</summary>

```python
class Node:
    def __init__(self, key=0, val=0):
        self.key = key
        self.val = val
        self.prev = self.next = None

class LRUCacheDLL:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}                 # key → Node
        self.head = Node()              # dummy LRU sentinel
        self.tail = Node()              # dummy MRU sentinel
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_before_tail(self, node):
        node.prev = self.tail.prev
        node.next = self.tail
        self.tail.prev.next = node
        self.tail.prev = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._insert_before_tail(node)    # promote to MRU
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            node = self.cache[key]
            node.val = value
            self._remove(node)
            self._insert_before_tail(node)
        else:
            if len(self.cache) == self.capacity:
                lru = self.head.next          # LRU is just after dummy head
                self._remove(lru)
                del self.cache[lru.key]
            node = Node(key, value)
            self.cache[key] = node
            self._insert_before_tail(node)

# Test
lru = LRUCacheDLL(2)
lru.put(1, 1); lru.put(2, 2)
assert lru.get(1) == 1
lru.put(3, 3)                  # evict 2
assert lru.get(2) == -1
assert lru.get(3) == 3
print("LRU DLL: passed")
```

**Why:** A doubly linked list enables O(1) node removal from any position (because each node holds a pointer to both neighbors). Combined with a dict for O(1) lookup by key, you get O(1) get and put without any standard library shortcuts. Dummy sentinels eliminate edge-case checks for empty list or single-node removal.

</details>

> 💻 Try it: [practice_local.py → Q4](./practice_local.py)

---

<a id="q5"></a>
### Q5 · LFU Cache — Frequency Bucket Structure

🟢 Easy

**Problem:** Describe the three data structures needed for an O(1) LFU cache and explain the role of each. Then implement the structure (without full get/put) to show the state after:

```
put(1, "a")  → frequency 1
put(2, "b")  → frequency 1
get(1)       → key 1's frequency becomes 2
```

Show what `key_freq`, `freq_map`, and `min_freq` look like after each step.

<details>
<summary>💡 Hint</summary>

`key_freq[key]` tracks how many times each key has been accessed. `freq_map[f]` is an `OrderedDict` of all keys currently at frequency `f` (ordered by recency for LRU tiebreaking). `min_freq` is the smallest frequency present — the eviction target.

</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import defaultdict, OrderedDict

# After put(1, "a"):
# key_freq = {1: 1}
# freq_map = {1: OrderedDict([(1, "a")])}
# min_freq = 1

# After put(2, "b"):
# key_freq = {1: 1, 2: 1}
# freq_map = {1: OrderedDict([(1,"a"), (2,"b")])}
# min_freq = 1

# After get(1):  key 1 moves from freq=1 to freq=2
# key_freq = {1: 2, 2: 1}
# freq_map = {1: OrderedDict([(2,"b")]), 2: OrderedDict([(1,"a")])}
# min_freq = 1  (freq_map[1] still has key 2, so min stays at 1)

class LFUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.key_val  = {}
        self.key_freq = {}
        self.freq_map = defaultdict(OrderedDict)
        self.min_freq = 0

    def _increment_freq(self, key):
        freq = self.key_freq[key]
        del self.freq_map[freq][key]             # remove from old bucket
        if not self.freq_map[freq] and freq == self.min_freq:
            self.min_freq += 1                   # old min bucket now empty
        self.key_freq[key] = freq + 1
        self.freq_map[freq + 1][key] = self.key_val[key]  # add to new bucket

    def get(self, key: int) -> int:
        if key not in self.key_val: return -1
        self._increment_freq(key)
        return self.key_val[key]

    def put(self, key: int, value: int) -> None:
        if self.capacity <= 0: return
        if key in self.key_val:
            self.key_val[key] = value
            self.freq_map[self.key_freq[key]][key] = value
            self._increment_freq(key)
        else:
            if len(self.key_val) >= self.capacity:
                evict_key, _ = self.freq_map[self.min_freq].popitem(last=False)
                del self.key_val[evict_key]
                del self.key_freq[evict_key]
            self.key_val[key]     = value
            self.key_freq[key]    = 1
            self.freq_map[1][key] = value
            self.min_freq         = 1           # new key always starts at freq=1

lfu = LFUCache(2)
lfu.put(1, "a"); lfu.put(2, "b")
assert lfu.get(1) == "a"        # key 1 freq → 2
lfu.put(3, "c")                 # evict min_freq=1 → key 2 (LRU among freq-1 keys)
assert lfu.get(2) == -1
assert lfu.get(1) == "a"
print("LFU structure: passed")
```

**Why:** The `OrderedDict` inside each frequency bucket provides LRU tiebreaking in O(1): when two keys share the minimum frequency, the one inserted first into that bucket (oldest = LRU) is evicted via `popitem(last=False)`. `min_freq` ensures we always find the eviction target in O(1) without scanning.

</details>

> 💻 Try it: [practice_local.py → Q5](./practice_local.py)

---

<a id="q6"></a>
### Q6 · Token Bucket — Allow Burst Traffic

🟢 Easy

**Problem:** Implement a `TokenBucket` rate limiter with `capacity` (max tokens) and `rate` (tokens/second). Each call to `allow()` returns `True` if a request is permitted (and consumes one token), `False` otherwise. The bucket refills over time at the given rate.

```
TokenBucket(capacity=5, rate=2)
# Allow 5 rapid requests (burst)
# 6th request immediately → denied (no tokens)
# After 0.5s → 1 new token → allow 1 more
```

<details>
<summary>💡 Hint</summary>

Store `tokens` and `last_refill_time`. On each call to `allow()`, compute `elapsed = now - last_refill_time`, add `elapsed * rate` tokens (capped at capacity), update `last_refill_time`, then check if `tokens >= 1`.

</details>

<details>
<summary>✅ Answer</summary>

```python
import time

class TokenBucket:
    def __init__(self, capacity: float, rate: float):
        """capacity: max tokens (burst size). rate: tokens/second."""
        self.capacity = capacity
        self.rate     = rate
        self.tokens   = capacity            # start full
        self.last     = time.monotonic()

    def allow(self) -> bool:
        now     = time.monotonic()
        elapsed = now - self.last
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last   = now
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False

# Test burst
tb = TokenBucket(capacity=5, rate=2)
burst = [tb.allow() for _ in range(5)]
assert all(burst), "All 5 burst requests should be allowed"
assert not tb.allow(), "6th request should be denied (no tokens)"
print("Token bucket: burst of 5 allowed, 6th denied.")
```

**Why:** Token Bucket is the right choice when clients need "credit" for idle periods — unused capacity accumulates up to `max_tokens`. A user who is idle for 2 seconds at `rate=2` earns 4 tokens for a burst of 4 requests. This is how GitHub's API (5000 req/hour) and AWS API Gateway work: allow short bursts without penalizing bursty-but-infrequent clients.

</details>

> 💻 Try it: [practice_local.py → Q6](./practice_local.py)

---

<a id="q7"></a>
### Q7 · LFU Cache — Correct Eviction with min_freq

🟡 Medium

**Problem:** The following LFU `put` method has two bugs related to `min_freq`. Identify both, explain the failure mode, and fix them.

```python
def put(self, key, value):
    if self.capacity <= 0: return
    if key in self.key_val:
        self.key_val[key] = value
        self._increment_freq(key)
        return
    if len(self.key_val) >= self.capacity:
        evict_key, _ = self.freq_map[self.min_freq].popitem(last=False)
        del self.key_val[evict_key]
        del self.key_freq[evict_key]
    self.key_val[key]     = value
    self.key_freq[key]    = 1
    self.freq_map[1][key] = value
    # BUG: min_freq not reset here
```

<details>
<summary>💡 Hint</summary>

Every new key starts with frequency 1. After inserting a new key, what is the guaranteed minimum frequency in the cache? What happens if you try to evict again and `min_freq` still points to an empty or wrong bucket?

</details>

<details>
<summary>✅ Answer</summary>

```python
# Bug: NOT setting self.min_freq = 1 when inserting a new key.
#
# Failure mode:
#   Suppose min_freq = 3 before eviction (some key had freq=3 as minimum).
#   We evict that key. We insert a new key with freq=1.
#   min_freq is still 3 (old value, not updated).
#   Next eviction: freq_map[3] is now empty (we just evicted it).
#   popitem() on an empty OrderedDict raises KeyError → crash!
#   Or it evicts the wrong key if freq_map[3] still has remnants.
#
# Fix: after inserting a new key, always set min_freq = 1.
# This is correct because: the new key has freq=1, and 1 is always
# the lowest possible frequency, so 1 is always the new minimum.

from collections import defaultdict, OrderedDict

class LFUCacheFixed:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.key_val  = {}
        self.key_freq = {}
        self.freq_map = defaultdict(OrderedDict)
        self.min_freq = 0

    def _increment_freq(self, key):
        freq = self.key_freq[key]
        del self.freq_map[freq][key]
        if not self.freq_map[freq] and freq == self.min_freq:
            self.min_freq += 1
        self.key_freq[key] = freq + 1
        self.freq_map[freq + 1][key] = self.key_val[key]

    def get(self, key: int) -> int:
        if key not in self.key_val: return -1
        self._increment_freq(key)
        return self.key_val[key]

    def put(self, key: int, value: int) -> None:
        if self.capacity <= 0: return
        if key in self.key_val:
            self.key_val[key] = value
            self.freq_map[self.key_freq[key]][key] = value
            self._increment_freq(key)
            return
        if len(self.key_val) >= self.capacity:
            evict_key, _ = self.freq_map[self.min_freq].popitem(last=False)
            del self.key_val[evict_key]
            del self.key_freq[evict_key]
        self.key_val[key]     = value
        self.key_freq[key]    = 1
        self.freq_map[1][key] = value
        self.min_freq = 1   # FIX: always 1 for new keys — non-negotiable

lfu = LFUCacheFixed(2)
lfu.put(1, 1); lfu.put(2, 2)
assert lfu.get(1) == 1      # freq[1] = 2
lfu.put(3, 3)               # evict min_freq=1 → key 2
assert lfu.get(2) == -1
assert lfu.get(3) == 3
lfu.put(4, 4)               # evict min_freq=1 → key 3 (key 1 has freq=2)
assert lfu.get(3) == -1
assert lfu.get(1) == 1
assert lfu.get(4) == 4
print("LFU with min_freq fix: passed")
```

**Why:** `min_freq = 1` after new key insertion is a hard invariant. A freshly inserted key always has frequency 1, which is always the global minimum. Skipping this reset corrupts the eviction pointer, causing KeyError crashes or wrong evictions on the next `put` when the cache is full.

</details>

> 💻 Try it: [practice_local.py → Q7](./practice_local.py)

---

<a id="q8"></a>
### Q8 · LFU Cache — LRU vs LFU on Same Access Pattern

🟡 Medium

**Problem:** Given this access pattern on a cache with capacity 2, show what each policy evicts when key `"C"` is inserted.

```
put("A", 1)   ← A accessed 1 time
put("B", 2)   ← B accessed 1 time
get("A")      ← A accessed again (total 2 times)
get("A")      ← A accessed again (total 3 times)
# Cache is full: {"A" (freq=3), "B" (freq=1)}
put("C", 3)   ← must evict someone
```

What does LRU evict? What does LFU evict? Which is "correct" for a hot-data workload?

<details>
<summary>💡 Hint</summary>

LRU only cares about when something was last accessed. LFU cares about how many times total. After the two `get("A")` calls, which key was accessed more recently? Which was accessed more often?

</details>

<details>
<summary>✅ Answer</summary>

```python
# LRU eviction:
#   After get("A") twice: order = [B (oldest access), A (most recent)]
#   LRU evicts B (least recently used). Correct here.
#
# LFU eviction:
#   freq("A") = 3, freq("B") = 1
#   LFU evicts B (least frequently used). Also correct here.
#
# They agree in this case. The difference appears when a hot key
# hasn't been accessed recently:

# Scenario where they disagree:
# put("A") × 10, put("B") × 1, then get("B"), put("C")
# LRU: B was accessed most recently → evicts A (the hot item!)
# LFU: A has freq=10 >> B's freq=2 → evicts B (keeps the hot item)

from collections import OrderedDict

class LRUCache:
    def __init__(self, cap):
        self.cap = cap
        self.cache = OrderedDict()
    def get(self, k):
        if k not in self.cache: return -1
        self.cache.move_to_end(k); return self.cache[k]
    def put(self, k, v):
        if k in self.cache: self.cache.move_to_end(k)
        self.cache[k] = v
        if len(self.cache) > self.cap: self.cache.popitem(last=False)

# Hot article scenario
lru = LRUCache(2)
for _ in range(5): lru.put("A", "viral article")  # A as most recent
lru.put("B", "new article")                        # B is now MRU, A is LRU
lru.put("C", "another new")                        # evicts A (LRU) — WRONG for hot data!
print("LRU evicted A:", lru.get("A") == -1)   # True — hot item gone!

# LFU would keep A because freq(A)=5 >> freq(B)=1
print("Conclusion: LFU is better when access frequency matters more than recency.")
```

**Why:** LRU is better for workloads with temporal locality (recently used = likely to be used again). LFU is better for frequency locality (frequently used = likely to be used again, like a viral article or popular song). The trade-off: LFU can cause "cold-start" starvation for new items that haven't had time to build up frequency.

</details>

> 💻 Try it: [practice_local.py → Q8](./practice_local.py)

---

<a id="q9"></a>
### Q9 · Sliding Window Rate Limiter

🟡 Medium

**Problem:** Implement a sliding window log rate limiter. It allows at most `limit` requests per `window_seconds`. Unlike a fixed window, it uses exact timestamps — a request at `t=0.9s` and one at `t=1.1s` are 0.2s apart, both within any window of size >= 0.2s.

```
SlidingWindowRL(limit=3, window=1.0)
  allow() at t=0.0  → True   (1 in window)
  allow() at t=0.3  → True   (2 in window)
  allow() at t=0.6  → True   (3 in window)
  allow() at t=0.8  → False  (3 still in window, limit hit)
  allow() at t=1.1  → True   (t=0.0 expired, now only 2 in window)
```

<details>
<summary>💡 Hint</summary>

Use a `deque` of timestamps. On each request, first remove all timestamps older than `now - window`. Then check if `len(deque) < limit`. If so, append `now` and allow. The deque stores at most `limit` entries.

</details>

<details>
<summary>✅ Answer</summary>

```python
import time
from collections import deque

class SlidingWindowRL:
    def __init__(self, limit: int, window_seconds: float):
        self.limit  = limit
        self.window = window_seconds
        self.log    = deque()   # timestamps of allowed requests

    def allow(self) -> bool:
        now    = time.monotonic()
        cutoff = now - self.window
        # Evict expired timestamps
        while self.log and self.log[0] <= cutoff:
            self.log.popleft()
        if len(self.log) < self.limit:
            self.log.append(now)
            return True
        return False

# Test: 3 rapid requests allowed, 4th denied
sw = SlidingWindowRL(limit=3, window_seconds=1.0)
assert sw.allow()       # allowed
assert sw.allow()       # allowed
assert sw.allow()       # allowed
assert not sw.allow()   # denied — 3 already in window
print("Sliding window: 3 allowed, 4th denied correctly.")
```

**Why:** Sliding window log is the most accurate rate limiting algorithm — it never allows more than `limit` requests in any rolling window of `window_seconds`. The trade-off: memory grows with `limit` (stores up to `limit` timestamps per user). For `limit=1,000,000` this is impractical; use token bucket instead. For `limit <= 10,000`, sliding window log is standard (e.g., Twitter API: 300 requests per 15-minute window).

</details>

> 💻 Try it: [practice_local.py → Q9](./practice_local.py)

---

<a id="q10"></a>
### Q10 · Leaky Bucket vs Token Bucket Trade-offs

🟡 Medium

**Problem:** A payment processor needs to handle exactly 10 transactions per second to a downstream bank API (no more, no less). A mobile app API needs to allow users to send 5 messages instantly when they open the app after an idle period.

1. Which rate limiter should the payment processor use, and why?
2. Which should the mobile app use, and why?
3. Implement a leaky bucket that enforces a strict constant output rate.

<details>
<summary>💡 Hint</summary>

Token Bucket allows bursts (accumulated tokens). Leaky Bucket enforces a fixed rate regardless of past idle time. Think about what "burst" means for a bank: downstream systems have hard transaction-per-second limits. Think about what "burst" means for a messaging app: users expect fast delivery after opening the app.

</details>

<details>
<summary>✅ Answer</summary>

```python
# 1. Payment processor → Leaky Bucket
#    The bank API accepts exactly 10 tx/sec. Sending 50 at once would overwhelm it.
#    Leaky bucket smooths the output to a constant rate.
#    There is no "burst credit" for being idle — the bank doesn't care.

# 2. Mobile app → Token Bucket
#    Users should be able to send several messages at once after opening the app.
#    Token bucket accumulates credit during idle periods, enabling a burst.
#    Long-term average rate is still enforced (token refill rate).

import time

class LeakyBucket:
    """Enforces a constant output rate. No burst allowed."""
    def __init__(self, rate_per_second: float):
        self.rate         = rate_per_second
        self.min_interval = 1.0 / rate_per_second
        self.last_allowed = time.monotonic() - self.min_interval  # allow first immediately

    def allow(self) -> bool:
        now = time.monotonic()
        if now - self.last_allowed >= self.min_interval:
            self.last_allowed = now
            return True
        return False   # too soon — steady rate not yet recovered

class TokenBucket:
    """Allows bursts up to capacity. Refills at steady rate."""
    def __init__(self, capacity: float, rate: float):
        self.capacity = capacity
        self.rate     = rate
        self.tokens   = capacity
        self.last     = time.monotonic()

    def allow(self) -> bool:
        now = time.monotonic()
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last   = now
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False

# Leaky bucket: only 1 request per 0.1s (10/sec)
lb = LeakyBucket(rate_per_second=10)
assert lb.allow()         # first allowed immediately
assert not lb.allow()     # too soon (< 0.1s)
print("Leaky: constant rate enforced.")

# Token bucket: burst of 5 immediately
tb = TokenBucket(capacity=5, rate=10)
burst = [tb.allow() for _ in range(5)]
assert all(burst)         # full burst allowed
assert not tb.allow()     # 6th denied
print("Token: burst of 5 allowed, 6th denied.")
```

**Why:** Leaky Bucket is a queue that drains at a fixed rate — it smooths spiky input into steady output, ideal for downstream systems with hard rate limits. Token Bucket is a credit system — idle periods earn future burst capacity, ideal for end-user-facing APIs where bursty-but-infrequent usage is legitimate and expected.

</details>

> 💻 Try it: [practice_local.py → Q10](./practice_local.py)

---

<a id="q11"></a>
### Q11 · Caching Strategy — Cache-Aside, Write-Through, Write-Back

🟡 Medium

**Problem:** Describe the three main caching write strategies. For each one, write a pseudocode implementation of a `write(key, value)` operation that shows the difference. Then name one production use case where each strategy is preferred.

<details>
<summary>💡 Hint</summary>

The key question for each strategy is: when does data get written to the cache vs the database, and what happens if the system crashes between the two writes? Cache-Aside puts the app in control. Write-Through guarantees consistency. Write-Back prioritizes performance.

</details>

<details>
<summary>✅ Answer</summary>

```python
# ─── 1. Cache-Aside (Lazy Loading) ───────────────────────────────────────────
# App manages cache manually. On write: update DB only.
# On read miss: fetch from DB, then populate cache.
# Trade-off: simple, but cache can serve stale data between write and next read.

def cache_aside_read(cache, db, key):
    val = cache.get(key)          # check cache first
    if val is None:               # cache miss
        val = db.get(key)         # read from DB (slow)
        if val is not None:
            cache.set(key, val)   # populate cache for future reads
    return val

def cache_aside_write(cache, db, key, value):
    db.set(key, value)            # write directly to DB
    cache.delete(key)             # invalidate cache entry (force re-read next time)

# Use case: Redis with application-side logic. Most common pattern.


# ─── 2. Write-Through ─────────────────────────────────────────────────────────
# Write to cache AND DB synchronously on every write.
# Trade-off: strong consistency, but every write hits the DB (slower writes).

def write_through(cache, db, key, value):
    cache.set(key, value)         # write to cache
    db.set(key, value)            # write to DB immediately (synchronous)

# Use case: financial ledgers, user authentication data — consistency critical.


# ─── 3. Write-Back (Write-Behind) ─────────────────────────────────────────────
# Write to cache only. Flush to DB asynchronously later (batched).
# Trade-off: fastest writes, but data loss if cache crashes before flush.

dirty_keys = set()

def write_back(cache, db, key, value):
    cache.set(key, value)         # write to cache only
    dirty_keys.add(key)           # mark as dirty (needs DB flush)

def flush_dirty(cache, db):
    for key in list(dirty_keys):
        val = cache.get(key)
        if val is not None:
            db.set(key, val)      # async flush to DB
        dirty_keys.discard(key)

# Use case: high-throughput writes where eventual consistency is acceptable,
# e.g., view counters, analytics event ingestion.


# Summary table:
print("Strategy     | Write path           | Consistency | Write speed | Risk")
print("Cache-Aside  | DB only, cache inval | Eventual    | DB speed    | Stale reads")
print("Write-Through| Cache + DB sync      | Strong      | Slower      | Extra latency")
print("Write-Back   | Cache only, async DB | Eventual    | Fastest     | Data loss")
```

**Why:** Cache-Aside is dominant in practice (used by most Redis deployments) because it keeps the app in control and doesn't risk writing stale data into the cache on reads. Write-Through is used when cache misses are unacceptable (e.g., session stores). Write-Back is used in storage engines like RocksDB's MemTable, where batch writes to disk are far more efficient than individual writes.

</details>

> 💻 Try it: [practice_local.py → Q11](./practice_local.py)

---

<a id="q12"></a>
### Q12 · Cache Eviction Policies — LRU, LFU, FIFO, Random

🟡 Medium

**Problem:** Four cache eviction policies are listed below. For each access pattern, identify which policy gives the best hit rate and briefly explain why.

```
Pattern A: "The user is streaming a video — they access frames in order,
            and older frames are never re-watched."

Pattern B: "A news site — a few articles go viral and get millions of hits,
            while most articles are read once."

Pattern C: "A test environment — requests are totally random with no pattern."

Pattern D: "A web session — the last 10 pages visited are the most likely
            to be revisited (e.g., browser back button)."
```

Policies: LRU, LFU, FIFO, Random

<details>
<summary>💡 Hint</summary>

LRU assumes "recently used = likely reused." LFU assumes "frequently used = likely reused." FIFO evicts the oldest regardless of usage. Random makes no assumption. Match the assumption to the access pattern.

</details>

<details>
<summary>✅ Answer</summary>

```python
# Pattern A: Sequential streaming (video frames)
# → FIFO or Random
# Frames are accessed once in order. LRU would keep the last few frames.
# But the user is unlikely to go back — recency is meaningless.
# FIFO simply evicts in insertion order, which is fine. LRU actually performs
# POORLY here (Belady's anomaly with cyclic scans).

# Pattern B: Viral articles (frequency skewed)
# → LFU
# A few hot articles have thousands of accesses. LFU keeps them.
# LRU would evict a viral article that hasn't been fetched "recently" even
# if it still has 100 accesses/minute — a big miss.

# Pattern C: Totally random requests
# → Random (equivalent to any other in expectation, but simpler)
# With no pattern, LRU and LFU gain nothing. Random is optimal in the sense
# that it's O(1) and no policy can do better without knowing future accesses.

# Pattern D: Web session (temporal locality)
# → LRU
# Recently visited pages are most likely to be revisited.
# "Back button" pattern is textbook temporal locality. LRU is designed for this.

policy_guide = {
    "Pattern A (sequential/streaming)": "FIFO or Random — no recency/frequency benefit",
    "Pattern B (viral/frequency-skewed)": "LFU — keeps hot items regardless of recency",
    "Pattern C (random no pattern)": "Random — no policy advantage; simpler = better",
    "Pattern D (temporal locality)": "LRU — recently used = likely reused",
}

for pattern, recommendation in policy_guide.items():
    print(f"{pattern}:\n  → {recommendation}\n")
```

**Why:** Eviction policy choice matters in production. Redis supports `allkeys-lru`, `allkeys-lfu`, `allkeys-random`, and `volatile-*` variants. CDNs use LRU. CPU hardware caches use pseudo-LRU. Choosing the wrong policy for your access pattern can halve your hit rate and double your DB load.

</details>

> 💻 Try it: [practice_local.py → Q12](./practice_local.py)

---

<a id="q13"></a>
### Q13 · Consistent Hashing — Ring with Virtual Nodes

🟡 Medium

**Problem:** Implement a consistent hash ring that distributes keys across servers. Support `add_server`, `remove_server`, and `get_server`. Use 100 virtual nodes per server for even distribution.

Verify that adding a 4th server moves approximately 25% of keys (not all keys as naive `hash % n` would require).

<details>
<summary>💡 Hint</summary>

Hash each `"server#i"` virtual node string to a position. Keep a sorted list of ring positions. For `get_server(key)`, hash the key and use `bisect` to find the first position >= key's hash (wrap around if past the end).

</details>

<details>
<summary>✅ Answer</summary>

```python
import hashlib, bisect

class ConsistentHashRing:
    def __init__(self, virtual_nodes: int = 100):
        self.virtual_nodes = virtual_nodes
        self.ring          = {}    # hash_pos → server_name
        self.sorted_keys   = []    # sorted list of hash positions

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**32)

    def add_server(self, server: str):
        for i in range(self.virtual_nodes):
            h = self._hash(f"{server}#{i}")
            self.ring[h] = server
            bisect.insort(self.sorted_keys, h)

    def remove_server(self, server: str):
        for i in range(self.virtual_nodes):
            h = self._hash(f"{server}#{i}")
            del self.ring[h]
            idx = bisect.bisect_left(self.sorted_keys, h)
            if idx < len(self.sorted_keys) and self.sorted_keys[idx] == h:
                self.sorted_keys.pop(idx)

    def get_server(self, key: str) -> str:
        if not self.ring: return None
        h   = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, h) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[idx]]

# Verify: ~25% keys move when adding a 4th server
ring = ConsistentHashRing(virtual_nodes=100)
for s in ["A", "B", "C"]:
    ring.add_server(s)

keys = [f"user:{i}" for i in range(1000)]
before = {k: ring.get_server(k) for k in keys}

ring.add_server("D")
after = {k: ring.get_server(k) for k in keys}

moved = sum(1 for k in keys if before[k] != after[k])
pct   = moved / len(keys) * 100
print(f"Keys moved when adding server D: {moved}/1000 ({pct:.1f}%)")
assert 10 < pct < 50, f"Expected ~25%, got {pct:.1f}%"
print("Consistent hashing: ~25% keys moved as expected.")
```

**Why:** With consistent hashing, adding a server to an N-server ring moves only K/N keys on average (where K = total keys). With naive `hash(key) % N`, nearly all keys remap when N changes — causing a cache stampede where every client suddenly gets misses simultaneously. This is why Redis Cluster, Cassandra, and DynamoDB all use consistent hashing.

</details>

> 💻 Try it: [practice_local.py → Q13](./practice_local.py)

---

<a id="q14"></a>
### Q14 · Consistent Hashing — Why Virtual Nodes

🟡 Medium

**Problem:** A consistent hash ring with 3 physical servers (one position each) produces this load distribution on 10,000 keys:

```
ServerA: 6,200 keys
ServerB: 2,300 keys
ServerC: 1,500 keys
```

1. Why is the load so uneven with one node per server?
2. How do virtual nodes fix this?
3. What is the trade-off of using more virtual nodes?

Demonstrate by comparing distribution with 1 vs 150 virtual nodes per server.

<details>
<summary>💡 Hint</summary>

Think about arc sizes on the ring. With 3 physical nodes, you have 3 arcs. The probability of a key landing in an arc is proportional to the arc's length. With N virtual nodes per server, you have 3N arcs — each server's share is the sum of many small arcs, which by the law of large numbers converges to 1/3.

</details>

<details>
<summary>✅ Answer</summary>

```python
import hashlib, bisect
from collections import defaultdict

def build_ring(servers, vnodes):
    ring = {}; sorted_keys = []
    for s in servers:
        for i in range(vnodes):
            h = int(hashlib.md5(f"{s}#{i}".encode()).hexdigest(), 16) % (2**32)
            ring[h] = s
            bisect.insort(sorted_keys, h)
    return ring, sorted_keys

def get_server(ring, sorted_keys, key):
    h   = int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**32)
    idx = bisect.bisect(sorted_keys, h) % len(sorted_keys)
    return ring[sorted_keys[idx]]

servers = ["ServerA", "ServerB", "ServerC"]
keys    = [f"key_{i}" for i in range(10000)]

for vnodes in [1, 10, 50, 150]:
    ring, sk = build_ring(servers, vnodes)
    dist = defaultdict(int)
    for k in keys:
        dist[get_server(ring, sk, k)] += 1
    counts = sorted(dist.values())
    variance = max(counts) - min(counts)
    print(f"vnodes={vnodes:3d}: {dict(dist)}  spread={variance}")

# Expected output shows that variance shrinks dramatically with more virtual nodes:
# vnodes=  1: wildly uneven (spread > 5000)
# vnodes= 10: better (spread ~3000)
# vnodes= 50: good   (spread ~1000)
# vnodes=150: even   (spread ~300)  ← typical production value
```

**Why:** With 1 physical node per server, the 3 arc lengths are determined by where 3 random hashes land on a 2^32 ring — they're unlikely to be equal. The law of large numbers says: the more random positions a server holds, the closer its share of the ring approaches 1/(num_servers). 150 virtual nodes is the standard production value (used by Cassandra, Amazon, Riak) balancing distribution quality against memory overhead (150 × num_servers entries in the ring dict).

</details>

> 💻 Try it: [practice_local.py → Q14](./practice_local.py)

---

<a id="q15"></a>
### Q15 · Bloom Filter — Insert and Query

🟡 Medium

**Problem:** Implement a Bloom filter with `expected_items` and a target `false_positive_rate`. Use the optimal `m` (bit array size) and `k` (number of hash functions) formulas:

```
m = -n * ln(p) / (ln 2)^2
k = (m / n) * ln(2)
```

Verify: no false negatives for any inserted item. False positive rate on unseen items should be close to the target.

<details>
<summary>💡 Hint</summary>

Use double hashing to simulate k independent hash functions: `h_i(x) = (h1(x) + i * h2(x)) % m`. A single `bytearray` of `ceil(m/8)` bytes is more memory-efficient than a list of booleans. To set bit `pos`: `bits[pos//8] |= (1 << (pos%8))`. To read bit `pos`: `bool(bits[pos//8] & (1 << (pos%8)))`.

</details>

<details>
<summary>✅ Answer</summary>

```python
import math, hashlib

class BloomFilter:
    def __init__(self, expected_items: int, false_positive_rate: float = 0.01):
        n, p = expected_items, false_positive_rate
        self.m    = math.ceil(-n * math.log(p) / (math.log(2) ** 2))
        self.k    = max(1, round((self.m / n) * math.log(2)))
        self.bits = bytearray(math.ceil(self.m / 8))

    def _positions(self, item: str):
        h1 = int(hashlib.md5(item.encode()).hexdigest(), 16)
        h2 = int(hashlib.sha1(item.encode()).hexdigest(), 16)
        for i in range(self.k):
            yield (h1 + i * h2) % self.m

    def add(self, item: str):
        for pos in self._positions(item):
            self.bits[pos // 8] |= (1 << (pos % 8))

    def contains(self, item: str) -> bool:
        """False → definitely not in set. True → probably in set."""
        return all(self.bits[pos // 8] & (1 << (pos % 8)) for pos in self._positions(item))

# Test
bf = BloomFilter(expected_items=1000, false_positive_rate=0.01)
inserted = [f"item-{i}" for i in range(1000)]
for item in inserted:
    bf.add(item)

# Zero false negatives
false_negatives = sum(1 for item in inserted if not bf.contains(item))
assert false_negatives == 0, f"False negatives found: {false_negatives}"

# False positive rate ~1%
fps = sum(1 for i in range(1000, 5000) if bf.contains(f"item-{i}"))
fpr = fps / 4000
print(f"False positive rate: {fpr:.3%} (target ~1%)")
assert fpr < 0.05   # some tolerance
print(f"Bloom filter: m={bf.m} bits, k={bf.k} hash functions.")
```

**Why:** A Bloom filter uses O(m) bits instead of O(n * key_size) bytes — roughly 10 bytes per item at 1% FPR vs. 50-100 bytes for a hash set. This is why Cassandra uses Bloom filters before disk reads (avoid reading SSTables that definitely don't have a key), and Chrome uses them for malicious URL pre-filtering. The guarantee is one-way: zero false negatives, bounded false positives.

</details>

> 💻 Try it: [practice_local.py → Q15](./practice_local.py)

---

<a id="q16"></a>
### Q16 · Top-K — Min-Heap of Size K

🟠 Hard

**Problem:** Given a stream of 1,000,000 integers, find the top 10 largest values. Implement two approaches:

1. Sort all elements — O(N log N) time, O(N) space
2. Min-heap of size K — O(N log K) time, O(K) space

Compare performance and explain why approach 2 is essential for streaming data.

<details>
<summary>💡 Hint</summary>

For the min-heap approach: maintain a heap of exactly K elements. The root is always the smallest of the top-K candidates. For each new element, if it's larger than the root, replace the root (`heapreplace`). At the end, the heap contains the K largest elements.

</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq, random, time

def top_k_sort(nums, k):
    """O(N log N) time, O(N) space — baseline."""
    return sorted(nums, reverse=True)[:k]

def top_k_heap(nums, k):
    """O(N log K) time, O(K) space — optimal for large N, small K."""
    heap = []
    for num in nums:
        if len(heap) < k:
            heapq.heappush(heap, num)
        elif num > heap[0]:              # beats current minimum of top-K
            heapq.heapreplace(heap, num) # pop min + push new (one O(log K) op)
    return sorted(heap, reverse=True)    # final sort of K elements

# Benchmark
nums = list(range(1_000_000))
random.shuffle(nums)
k = 10

t0 = time.monotonic()
result_sort = top_k_sort(nums, k)
t_sort = time.monotonic() - t0

t0 = time.monotonic()
result_heap = top_k_heap(nums, k)
t_heap = time.monotonic() - t0

assert result_sort == result_heap, "Results must match"
print(f"Sort approach:     {t_sort:.4f}s")
print(f"Min-heap approach: {t_heap:.4f}s")
print(f"Speedup: {t_sort/t_heap:.1f}x faster")

# Top-K frequent words (common interview variant)
from collections import Counter

def top_k_frequent(words, k):
    counts = Counter(words)
    heap = []
    for word, count in counts.items():
        heapq.heappush(heap, (count, word))
        if len(heap) > k:
            heapq.heappop(heap)   # drop smallest count
    return [word for count, word in sorted(heap, key=lambda x: -x[0])]

words = ["the", "a", "is", "the", "a", "is", "is", "banana"]
print(f"Top-2 frequent: {top_k_frequent(words, 2)}")  # ['is', 'the'] or ['is', 'a']
```

**Why:** For N=1,000,000 and K=10: sort requires O(N log N) ≈ 20M comparisons and O(N) memory. Min-heap requires O(N log K) ≈ 3.3M comparisons and O(K)=O(10) memory — 6x faster and 100,000x less memory. For infinite streams (Kafka topic, live log tailing), the sort approach is impossible; the heap approach trivially handles infinite streams since it never stores more than K elements.

</details>

> 💻 Try it: [practice_local.py → Q16](./practice_local.py)

---

<a id="q17"></a>
### Q17 · Bloom Filter — Optimal k and False Positive Rate

🟠 Hard

**Problem:** Demonstrate empirically how the number of hash functions `k` affects the false positive rate. For a fixed bit array of size `m=100,000` and `n=10,000` inserted items, measure the false positive rate for `k = 1, 3, 7, 10, 20`.

The optimal `k = (m/n) * ln(2) ≈ 6.9 ≈ 7`. Show that k=7 gives the minimum FPR.

<details>
<summary>💡 Hint</summary>

The theoretical FPR formula is `(1 - e^(-k*n/m))^k`. Plot or print the values for different k. Both too few and too many hash functions increase FPR: too few = not enough positions marked to distinguish items; too many = bit array saturates, everything looks like it's in the set.

</details>

<details>
<summary>✅ Answer</summary>

```python
import math, hashlib

class BloomFilterFixedK:
    """Bloom filter with manually specified k (for experimentation)."""
    def __init__(self, m: int, k: int):
        self.m    = m
        self.k    = k
        self.bits = bytearray(math.ceil(m / 8))

    def _positions(self, item):
        h1 = int(hashlib.md5(item.encode()).hexdigest(), 16)
        h2 = int(hashlib.sha1(item.encode()).hexdigest(), 16)
        for i in range(self.k):
            yield (h1 + i * h2) % self.m

    def add(self, item):
        for pos in self._positions(item):
            self.bits[pos // 8] |= (1 << (pos % 8))

    def contains(self, item):
        return all(self.bits[pos // 8] & (1 << (pos % 8)) for pos in self._positions(item))

m, n = 100_000, 10_000
k_values = [1, 3, 7, 10, 20]

print(f"{'k':>4} | {'Theoretical FPR':>18} | {'Empirical FPR':>16}")
print("-" * 45)

for k in k_values:
    # Theoretical
    theoretical = (1 - math.exp(-k * n / m)) ** k

    # Empirical
    bf = BloomFilterFixedK(m, k)
    for i in range(n):
        bf.add(f"item_{i}")
    fps = sum(1 for i in range(n, n + 10000) if bf.contains(f"item_{i}"))
    empirical = fps / 10000

    marker = " ← optimal" if k == 7 else ""
    print(f"{k:>4} | {theoretical:>17.4%} | {empirical:>15.4%}{marker}")

# Expected:
# k= 1 → ~9.5% theoretical, high empirical
# k= 3 → ~3.5%
# k= 7 → ~0.82% (minimum — optimal)
# k=10 → ~1.3%  (worse than 7!)
# k=20 → ~4.2%  (much worse — array saturates)
```

**Why:** The optimal `k = (m/n) * ln(2)` minimizes `(1 - e^(-kn/m))^k`. With k too small, few bits are set per item — items look alike. With k too large, the bit array fills up (nearly all bits become 1) — every query returns "probably yes." The optimum balances these two failure modes. This formula is why production Bloom filters (Cassandra, Redis, HBase) compute k automatically from the target FPR and expected item count.

</details>

> 💻 Try it: [practice_local.py → Q17](./practice_local.py)

---

<a id="q18"></a>
### Q18 · Consistent Hashing — Keys Moved on Server Add/Remove

🟠 Hard

**Problem:** Prove empirically that consistent hashing moves only ~K/N keys when a server is added or removed, while naive modulo hashing moves ~(N-1)/N keys.

Use 3 initial servers and 10,000 keys. Add a 4th server. Compare the percentage of remapped keys between the two approaches.

<details>
<summary>💡 Hint</summary>

For naive hashing: `server = hash(key) % num_servers`. Record assignments before and after adding a server. For consistent hashing: use the ring from Q13. The fraction of keys that should move with consistent hashing is 1/(new_num_servers) = 25%. For naive hashing, most keys will remap.

</details>

<details>
<summary>✅ Answer</summary>

```python
import hashlib, bisect

# Naive modulo hashing
def naive_assign(key, n):
    h = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return h % n

# Consistent hash ring (reuse from Q13)
class Ring:
    def __init__(self, vnodes=100):
        self.vnodes = vnodes; self.ring = {}; self.sk = []
    def _h(self, k): return int(hashlib.md5(k.encode()).hexdigest(),16)%(2**32)
    def add(self, s):
        for i in range(self.vnodes):
            h = self._h(f"{s}#{i}"); self.ring[h]=s; bisect.insort(self.sk,h)
    def get(self, k):
        h=self._h(k); idx=bisect.bisect(self.sk,h)%len(self.sk); return self.ring[self.sk[idx]]

keys = [f"key:{i}" for i in range(10_000)]

# ── Naive hashing ──────────────────────────────────────────────────────────────
naive_before = {k: naive_assign(k, 3) for k in keys}
naive_after  = {k: naive_assign(k, 4) for k in keys}
naive_moved  = sum(1 for k in keys if naive_before[k] != naive_after[k])
naive_pct    = naive_moved / len(keys) * 100

# ── Consistent hashing ─────────────────────────────────────────────────────────
ring = Ring(vnodes=100)
for s in ["S1", "S2", "S3"]: ring.add(s)
ch_before = {k: ring.get(k) for k in keys}
ring.add("S4")
ch_after  = {k: ring.get(k) for k in keys}
ch_moved  = sum(1 for k in keys if ch_before[k] != ch_after[k])
ch_pct    = ch_moved / len(keys) * 100

print(f"Naive modulo:      {naive_moved:,} keys moved ({naive_pct:.1f}%)")
print(f"Consistent hashing:{ch_moved:,} keys moved ({ch_pct:.1f}%)")
print(f"  Expected naive:  ~75% (3 out of 4 change server with %N)")
print(f"  Expected CH:     ~25% (only keys from S4's new arc move)")

assert naive_pct > 50, "Naive should move most keys"
assert 10 < ch_pct < 40, "Consistent hashing should move ~25%"
```

**Why:** With naive `hash % N`, adding the 4th server changes the modulus from 3 to 4. A key that mapped to server 0 with modulus 3 now maps to `h % 4`, which is different for ~75% of keys. This causes a thundering herd — every client simultaneously gets cache misses, and the database gets slammed. Consistent hashing avoids this: only the keys "owned" by the new server's ring arc migrate, which is ~1/N of total keys.

</details>

> 💻 Try it: [practice_local.py → Q18](./practice_local.py)

---

<a id="q19"></a>
### Q19 · LFU Cache — min_freq Reset Bug

🟠 Hard

**Problem:** The `_increment_freq` function below has a subtle bug that causes `min_freq` to be stale in certain scenarios. Trace through this sequence to find when and how it fails:

```
LFUCache(capacity=3)
put(1, 1), put(2, 2), put(3, 3)   # all at freq=1, min_freq=1
get(1)                              # key 1 freq → 2, min_freq should stay 1
get(2)                              # key 2 freq → 2, min_freq should stay 1
get(3)                              # key 3 freq → 2, min_freq should go to 2
# Now: all keys at freq=2, min_freq=2
put(4, 4)   # must evict min_freq=2, then insert key 4 with freq=1
# What should min_freq be now?
get(4)      # is key 4 accessible?
```

```python
def _increment_freq(self, key):
    freq = self.key_freq[key]
    del self.freq_map[freq][key]
    if not self.freq_map[freq]:
        del self.freq_map[freq]
        if self.min_freq == freq:
            self.min_freq = freq + 1  # BUG: this is wrong after a new key insert
    self.key_freq[key] = freq + 1
    self.freq_map[freq + 1][key] = self.key_val[key]
```

<details>
<summary>💡 Hint</summary>

The bug is not in `_increment_freq` itself — it's in how `min_freq` interacts with new key insertion. When `put` inserts a new key with `freq=1`, it doesn't reset `min_freq`. After evicting from `min_freq=2` and inserting a new key at `freq=1`, what is the true minimum frequency? What does `min_freq` actually say?

</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import defaultdict, OrderedDict

class LFUBuggy:
    """LFU with the min_freq reset bug on new key insertion."""
    def __init__(self, capacity):
        self.capacity = capacity
        self.key_val  = {}; self.key_freq = {}
        self.freq_map = defaultdict(OrderedDict); self.min_freq = 0

    def _increment_freq(self, key):
        freq = self.key_freq[key]
        del self.freq_map[freq][key]
        if not self.freq_map[freq] and self.min_freq == freq:
            self.min_freq = freq + 1
        self.key_freq[key] = freq + 1
        self.freq_map[freq + 1][key] = self.key_val[key]

    def get(self, key):
        if key not in self.key_val: return -1
        self._increment_freq(key); return self.key_val[key]

    def put(self, key, value):
        if self.capacity <= 0: return
        if key in self.key_val:
            self.key_val[key] = value
            self.freq_map[self.key_freq[key]][key] = value
            self._increment_freq(key); return
        if len(self.key_val) >= self.capacity:
            evict_key, _ = self.freq_map[self.min_freq].popitem(last=False)
            del self.key_val[evict_key]; del self.key_freq[evict_key]
        self.key_val[key] = value; self.key_freq[key] = 1
        self.freq_map[1][key] = value
        # BUG: no self.min_freq = 1 here!

# Trace the failure:
lfu = LFUBuggy(3)
lfu.put(1,1); lfu.put(2,2); lfu.put(3,3)  # all freq=1, min_freq=1
lfu.get(1); lfu.get(2); lfu.get(3)         # all freq=2, min_freq→2
# State: freq_map={2:{1,2,3}}, min_freq=2

lfu.put(4, 4)
# Evict from min_freq=2 → evicts key 1 (or 2 or 3, LRU of freq=2)
# Insert key 4 with freq=1
# BUG: min_freq is still 2, but key 4 has freq=1!
# min_freq should be 1 (key 4 is the new minimum)

print("min_freq after put(4):", lfu.min_freq)   # 2 — WRONG, should be 1
print("get(4):", lfu.get(4))  # should return 4

# Next put will try to evict from min_freq=2
# freq_map[2] may still have keys → evicts the wrong key!

# The FIX: always self.min_freq = 1 after inserting a new key
class LFUFixed:
    def __init__(self, capacity):
        self.capacity = capacity
        self.key_val  = {}; self.key_freq = {}
        self.freq_map = defaultdict(OrderedDict); self.min_freq = 0

    def _increment_freq(self, key):
        freq = self.key_freq[key]
        del self.freq_map[freq][key]
        if not self.freq_map[freq] and self.min_freq == freq:
            self.min_freq = freq + 1
        self.key_freq[key] = freq + 1
        self.freq_map[freq + 1][key] = self.key_val[key]

    def get(self, key):
        if key not in self.key_val: return -1
        self._increment_freq(key); return self.key_val[key]

    def put(self, key, value):
        if self.capacity <= 0: return
        if key in self.key_val:
            self.key_val[key] = value
            self.freq_map[self.key_freq[key]][key] = value
            self._increment_freq(key); return
        if len(self.key_val) >= self.capacity:
            evict_key, _ = self.freq_map[self.min_freq].popitem(last=False)
            del self.key_val[evict_key]; del self.key_freq[evict_key]
        self.key_val[key] = value; self.key_freq[key] = 1
        self.freq_map[1][key] = value
        self.min_freq = 1   # FIX: always reset on new key insert

lfu2 = LFUFixed(3)
lfu2.put(1,1); lfu2.put(2,2); lfu2.put(3,3)
lfu2.get(1); lfu2.get(2); lfu2.get(3)
lfu2.put(4,4)
assert lfu2.min_freq == 1, f"min_freq should be 1 after inserting key 4"
assert lfu2.get(4) == 4
print("LFU min_freq bug traced and fixed.")
```

**Why:** After evicting from `min_freq=2` and inserting a new key with `freq=1`, the true minimum frequency in the cache is 1 — the new key. If `min_freq` remains 2, the next eviction targets `freq_map[2]` which may still contain valid high-frequency keys, causing incorrect eviction. The rule "always set `min_freq = 1` when inserting a new key" is an invariant: a freshly inserted key always has the lowest possible frequency.

</details>

> 💻 Try it: [practice_local.py → Q19](./practice_local.py)

---

<a id="q20"></a>
### Q20 · System Composition — Rate Limiter + LRU + Consistent Hashing

🟠 Hard

**Problem:** Design a minimal distributed cache system that:

1. Uses a **token bucket rate limiter** per client (5 req/sec, burst=10)
2. Routes each request to a server using **consistent hashing** (3 servers, 100 vnodes)
3. Each server maintains an **LRU cache** (capacity=100)
4. On cache miss, "fetches from DB" (simulated)

Show how the three patterns compose. For 5 clients each making 20 requests to random keys, print hit rate per server.

<details>
<summary>💡 Hint</summary>

Build the three components separately (you've implemented each in earlier questions), then wire them: incoming request → check rate limiter → route via consistent hash → check that server's LRU cache → on miss, populate cache.

</details>

<details>
<summary>✅ Answer</summary>

```python
import hashlib, bisect, time, random
from collections import OrderedDict

# Component 1: Token Bucket
class TokenBucket:
    def __init__(self, capacity, rate):
        self.capacity = capacity; self.rate = rate
        self.tokens = capacity; self.last = time.monotonic()
    def allow(self):
        now = time.monotonic()
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= 1: self.tokens -= 1; return True
        return False

# Component 2: LRU Cache
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity; self.cache = OrderedDict()
        self.hits = 0; self.misses = 0
    def get(self, key):
        if key not in self.cache: self.misses += 1; return None
        self.cache.move_to_end(key); self.hits += 1; return self.cache[key]
    def put(self, key, value):
        if key in self.cache: self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity: self.cache.popitem(last=False)

# Component 3: Consistent Hash Ring
class Ring:
    def __init__(self, vnodes=100):
        self.vnodes=vnodes; self.ring={}; self.sk=[]
    def _h(self,k): return int(hashlib.md5(k.encode()).hexdigest(),16)%(2**32)
    def add(self,s):
        for i in range(self.vnodes): h=self._h(f"{s}#{i}"); self.ring[h]=s; bisect.insort(self.sk,h)
    def get(self,k):
        h=self._h(k); idx=bisect.bisect(self.sk,h)%len(self.sk); return self.ring[self.sk[idx]]

# Wire together
ring = Ring(vnodes=100)
servers = {f"server-{i}": LRUCache(capacity=100) for i in range(3)}
for s in servers: ring.add(s)

clients = {f"client-{i}": TokenBucket(capacity=10, rate=5) for i in range(5)}
db = {f"key-{i}": f"value-{i}" for i in range(50)}  # simulated database

allowed = 0; throttled = 0

for client_id, rate_limiter in clients.items():
    for _ in range(20):
        key = f"key-{random.randint(0, 49)}"
        if not rate_limiter.allow():
            throttled += 1; continue
        allowed += 1
        server_name = ring.get(key)
        cache = servers[server_name]
        val = cache.get(key)
        if val is None:
            val = db.get(key, "NOT FOUND")
            cache.put(key, val)   # populate on miss

print(f"\nRequests: {allowed} allowed, {throttled} throttled")
print("\nServer stats:")
for name, cache in sorted(servers.items()):
    total = cache.hits + cache.misses
    rate = cache.hits / total * 100 if total else 0
    print(f"  {name}: {total} requests, {cache.hits} hits, {cache.misses} misses, hit rate {rate:.1f}%")
```

**Why:** This composition is the exact architecture behind production systems like Netflix's API tier: Zuul (rate limiter) → Ribbon (consistent-hash load balancer) → EVCache (LRU distributed cache). Each pattern solves a distinct problem — throttling protects the system, consistent hashing minimizes cache churn during scaling events, and LRU maximizes hit rate given limited memory. Understanding how these three interact (not just each in isolation) is what distinguishes a senior system design answer.

</details>

> 💻 Try it: [practice_local.py → Q20](./practice_local.py)

---

**[⬅️ Theory](./caching_strategies.md)** · **[💻 Local Practice](./practice_local.py)**

**Prev:** [← 25_advanced_graphs](../25_advanced_graphs/practice.md) | **Next:** [99_interview_master →](../99_interview_master/)
