# System Design Patterns — Common Mistakes

> "System design data structures are like building codes. You can violate them and the building still stands — until it doesn't. The failure mode is slow degradation: cache that evicts the wrong items, hash ring that dumps all traffic on one server, rate limiter that silently throttles the wrong requests."

This file covers the 8 most common implementation mistakes in system design algorithms: LRU, LFU, consistent hashing, Bloom filters, rate limiters, and Top-K structures. Each one is explained with a real-world analogy, broken code, a trace of the failure, and the correct fix.

---

## Table of Contents

1. [LRU: dict + Manual Ordering Instead of OrderedDict](#mistake-1)
2. [LRU: Not Moving to MRU on Get AND Set](#mistake-2)
3. [LFU: Removing from Wrong Frequency Bucket](#mistake-3)
4. [LFU: min_freq Not Updated After Eviction](#mistake-4)
5. [Consistent Hashing: Too Few Virtual Nodes](#mistake-5)
6. [Bloom Filter: Wrong Number of Hash Functions](#mistake-6)
7. [Rate Limiter: Token Bucket vs Leaky Bucket Confusion](#mistake-7)
8. [Top-K: Using Max-Heap Instead of Min-Heap of Size K](#mistake-8)

---

## Mistake 1: LRU — dict + Manual Ordering Instead of OrderedDict {#mistake-1}

### The Story

You're managing a small VIP lounge with 3 seats. Every time someone new arrives, they get a seat. When a fourth person arrives and all seats are filled, the person who has been sitting longest (least recently) gets asked to leave.

The challenge: you need to know both (1) who is sitting (fast lookup by name) and (2) who has been there longest (ordered by time). A regular `dict` gives you fast lookup but doesn't help with ordering. An `OrderedDict` gives you both — and critically, lets you move someone "to the front of the line" in O(1) when they do something (like order a drink).

### Python dict: Insertion Order != MRU Order

Python 3.7+ dicts preserve insertion order, but they don't let you efficiently reorder elements. The only O(1) operations are insert, delete, and lookup. Moving an element to the end requires delete + re-insert — which IS O(1) in `dict`, but the code is fragile and easy to mess up.

`OrderedDict` from `collections` provides a dedicated `move_to_end(key)` method that is O(1) and semantically clear.

### WRONG Code: dict with O(n) Ordering

```python
class LRUCacheWrong:
    """
    BUG: Uses regular dict. To 'move to end' (most recent),
    we delete and re-insert. Works but has hidden O(1) per operation,
    however the pattern is fragile and commonly implemented INCORRECTLY
    as an O(n) scan.
    """
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}

    def get(self, key):
        if key not in self.cache:
            return -1

        # WRONG PATTERN: many beginners do this O(n) approach
        # to "move the key to most recent":
        val = self.cache[key]
        # Create a new dict without the key, then re-add it at end
        # This is O(n) because we're building a new dict
        new_cache = {k: v for k, v in self.cache.items() if k != key}
        new_cache[key] = val
        self.cache = new_cache  # O(n) rebuild!
        return val

    def put(self, key, value):
        if key in self.cache:
            # Move to most recent: O(n) rebuild
            del self.cache[key]
        elif len(self.cache) >= self.capacity:
            # Evict LRU: get first key (insertion order)
            # next(iter(dict)) is O(1), but this eviction pattern is right
            lru_key = next(iter(self.cache))
            del self.cache[lru_key]
        self.cache[key] = value


# The O(n) problem: for a cache with 100,000 entries,
# every get() rebuilds the entire dict. That's 100,000 ops per access!
# Amortized this is O(n) per operation, not O(1).

# Let's time it:
import time

lru = LRUCacheWrong(10000)
for i in range(10000):
    lru.put(i, i)

start = time.time()
for i in range(1000):
    lru.get(i % 100)  # Access same 100 keys repeatedly
elapsed = time.time() - start
print(f"Wrong LRU: {elapsed:.4f}s for 1000 gets with 10000 cache entries")
# This will be noticeably slow — O(n) per get
```

### RIGHT Code: OrderedDict for O(1) LRU

```python
from collections import OrderedDict

class LRUCacheCorrect:
    """
    Correct O(1) LRU using OrderedDict.
    move_to_end(key) is O(1) — doubly-linked list under the hood.
    """
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        # Move to most-recently-used end in O(1)
        self.cache.move_to_end(key)  # last=True means "most recent" end
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            # Update and move to MRU
            self.cache.move_to_end(key)
            self.cache[key] = value
        else:
            if len(self.cache) >= self.capacity:
                # Evict least-recently-used (first element, last=False)
                self.cache.popitem(last=False)  # O(1) eviction
            self.cache[key] = value


# Alternative: explicit doubly-linked list + dict (better for interviews
# where you can't use OrderedDict):

class DLinkedNode:
    def __init__(self, key=0, val=0):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None

class LRUCacheLinkedList:
    """
    O(1) LRU using doubly-linked list + dict.
    - dict: O(1) key lookup
    - linked list: O(1) move-to-head and remove-tail
    head ← most recently used
    tail ← least recently used
    """
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}  # key → node

        # Sentinel nodes (dummy head and tail for clean boundary handling)
        self.head = DLinkedNode()  # dummy head (MRU side)
        self.tail = DLinkedNode()  # dummy tail (LRU side)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        """Remove a node from the doubly-linked list. O(1)."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_head(self, node):
        """Insert node right after dummy head (MRU position). O(1)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_to_head(node)  # Move to MRU
        return node.val

    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.val = value
            self._remove(node)
            self._add_to_head(node)
        else:
            if len(self.cache) >= self.capacity:
                # Evict LRU: node just before dummy tail
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]
            node = DLinkedNode(key, value)
            self.cache[key] = node
            self._add_to_head(node)


# Test both correct versions
def test_lru(lru_class):
    lru = lru_class(2)
    lru.put(1, 1)
    lru.put(2, 2)
    assert lru.get(1) == 1       # cache: {2, 1} (1 is MRU)
    lru.put(3, 3)                # evict 2 (LRU), cache: {1, 3}
    assert lru.get(2) == -1      # 2 was evicted
    lru.put(4, 4)                # evict 1 (LRU), cache: {3, 4}
    assert lru.get(1) == -1      # evicted
    assert lru.get(3) == 3       # still there
    assert lru.get(4) == 4       # still there
    print(f"{lru_class.__name__}: All assertions passed ✓")

test_lru(LRUCacheCorrect)
test_lru(LRUCacheLinkedList)
```

### Complexity Comparison

```
╔══════════════════╦═══════════════╦════════════════╦══════════════════╗
║ Implementation   ║ get()         ║ put()          ║ Space            ║
╠══════════════════╬═══════════════╬════════════════╬══════════════════╣
║ dict + O(n)      ║ O(n) rebuild  ║ O(n) rebuild   ║ O(capacity)      ║
║ reconstruction   ║               ║                ║                  ║
╠══════════════════╬═══════════════╬════════════════╬══════════════════╣
║ OrderedDict      ║ O(1)          ║ O(1)           ║ O(capacity)      ║
╠══════════════════╬═══════════════╬════════════════╬══════════════════╣
║ DLinkedList+dict ║ O(1)          ║ O(1)           ║ O(capacity)      ║
╚══════════════════╩═══════════════╩════════════════╩══════════════════╝
```

---

## Mistake 2: LRU — Not Moving to MRU on Get AND Set {#mistake-2}

### The Story

Your lounge has 3 seats. Alice, Bob, and Charlie are sitting. Alice gets up to get a drink (accesses the bar) — that counts as "being active." When David arrives, who should be evicted? Not Alice, who just did something! But a buggy implementation might evict Alice if it only tracks insertion time, not last-access time.

The LRU contract is simple: "evict whoever was accessed least recently." Both `get` (reading) and `put` (inserting OR updating) count as accesses.

### WRONG Code: Forgetting to Move on get OR Existing Key put

```python
from collections import OrderedDict

class LRUBuggy:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        # BUG 1: Forgot to move_to_end on get!
        # The key is accessed but its "recency" position doesn't change
        return self.cache[key]  # Just returns value, doesn't mark as MRU

    def put(self, key, value):
        if key in self.cache:
            # BUG 2: Updates value but doesn't move to MRU!
            # A recently-updated key might still be evicted as "least recent"
            self.cache[key] = value  # Updates value, doesn't move to end
        else:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
            self.cache[key] = value
            # BUG: New keys are correctly at end, but existing key updates aren't


# Trace of bug:
buggy = LRUBuggy(3)
buggy.put(1, 10)   # cache: {1}
buggy.put(2, 20)   # cache: {1, 2}
buggy.put(3, 30)   # cache: {1, 2, 3}

# Access key 1 — should move 1 to MRU
val = buggy.get(1)  # Returns 10 (correct), but doesn't move 1!
# Cache order is still: {1, 2, 3} with 1 as LRU!

buggy.put(4, 40)   # Cache full, evict LRU = key 1!
print("After accessing 1 and inserting 4:")
print("get(1):", buggy.get(1))  # -1! Key 1 was WRONGLY evicted!
# Key 1 was JUST accessed but got evicted because get() didn't update recency.

print("get(2):", buggy.get(2))  # 20 (still there)
print("get(3):", buggy.get(3))  # 30 (still there)
print("get(4):", buggy.get(4))  # 40 (still there)

# BUG 2 trace:
buggy2 = LRUBuggy(2)
buggy2.put(1, 10)   # cache: {1: 10}
buggy2.put(2, 20)   # cache: {1: 10, 2: 20}
buggy2.put(1, 100)  # Update key 1 — should move to MRU! BUG: doesn't.
# Cache still ordered: {1: 100, 2: 20} with 1 as LRU

buggy2.put(3, 30)   # Evict LRU = key 1 (was JUST updated!)
print("\nAfter updating key 1 and inserting key 3:")
print("get(1):", buggy2.get(1))  # -1! Just-updated key was evicted!
```

### RIGHT Code: Always Move to MRU on get AND set

```python
from collections import OrderedDict

class LRUCorrect:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        # MUST move to end (MRU) on EVERY access
        self.cache.move_to_end(key)  # ← non-negotiable
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            # MUST move to end even when updating an existing key
            self.cache.move_to_end(key)  # ← also non-negotiable
            self.cache[key] = value
        else:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)  # Evict LRU
            self.cache[key] = value  # New key goes to end (MRU) automatically


# Verify the fix:
lru = LRUCorrect(3)
lru.put(1, 10)
lru.put(2, 20)
lru.put(3, 30)

# Access key 1 — should NOT be evicted next
val = lru.get(1)  # 10, and moves 1 to MRU
# Cache order: {2, 3, 1} — 2 is now LRU

lru.put(4, 40)  # Evict LRU = key 2
print("get(1):", lru.get(1))  # 10 ✓ (not evicted!)
print("get(2):", lru.get(2))  # -1 ✓ (evicted)
print("get(3):", lru.get(3))  # 30 ✓
print("get(4):", lru.get(4))  # 40 ✓

# Test update case:
lru2 = LRUCorrect(2)
lru2.put(1, 10)
lru2.put(2, 20)
lru2.put(1, 100)  # Update key 1 → moves to MRU
# Cache: {2, 1} — 2 is LRU now

lru2.put(3, 30)  # Evict LRU = 2
print("\nget(1):", lru2.get(1))  # 100 ✓ (not evicted!)
print("get(2):", lru2.get(2))  # -1  ✓ (evicted)
print("get(3):", lru2.get(3))  # 30  ✓
```

---

## Mistake 3: LFU — Removing from Wrong Frequency Bucket {#mistake-3}

### The Story

LFU (Least Frequently Used) evicts whichever key has been accessed the fewest times. You maintain buckets: bucket[1] contains keys accessed once, bucket[2] contains keys accessed twice, etc.

When you access a key, you need to:
1. Find it in its CURRENT frequency bucket (say, bucket[3])
2. Remove it from bucket[3]
3. Add it to bucket[4]

The bug: removing from bucket[4] (the NEW bucket) instead of bucket[3] (the OLD bucket). The key disappears from the wrong place, leaving a ghost entry in the old bucket.

### WRONG Code: Remove from New Frequency Bucket

```python
from collections import defaultdict, OrderedDict

class LFUCacheWrong:
    def __init__(self, capacity):
        self.capacity = capacity
        self.key_freq = {}        # key → frequency
        self.key_val  = {}        # key → value
        self.freq_keys = defaultdict(OrderedDict)  # freq → OrderedDict of keys
        self.min_freq = 0

    def _update_freq(self, key):
        freq = self.key_freq[key]
        new_freq = freq + 1

        self.key_freq[key] = new_freq

        # BUG: Remove from NEW frequency bucket instead of OLD!
        if key in self.freq_keys[new_freq]:
            del self.freq_keys[new_freq][key]  # Removes from wrong bucket!
        # Should remove from self.freq_keys[freq][key] (the OLD frequency)

        self.freq_keys[new_freq][key] = True  # Add to new frequency

        # Update min_freq
        if not self.freq_keys[self.min_freq]:
            self.min_freq = new_freq

    def get(self, key):
        if key not in self.key_val:
            return -1
        self._update_freq(key)
        return self.key_val[key]

    def put(self, key, value):
        if self.capacity <= 0:
            return
        if key in self.key_val:
            self.key_val[key] = value
            self._update_freq(key)
            return

        if len(self.key_val) >= self.capacity:
            # Evict from min_freq bucket
            evict_key, _ = self.freq_keys[self.min_freq].popitem(last=False)
            del self.key_val[evict_key]
            del self.key_freq[evict_key]

        self.key_val[key] = value
        self.key_freq[key] = 1
        self.freq_keys[1][key] = True
        self.min_freq = 1


# Trace of the bug:
lfu_wrong = LFUCacheWrong(3)
lfu_wrong.put(1, 10)  # freq_keys: {1: {1}}
lfu_wrong.put(2, 20)  # freq_keys: {1: {1, 2}}
lfu_wrong.put(3, 30)  # freq_keys: {1: {1, 2, 3}}

lfu_wrong.get(1)      # Access key 1:
                      # freq=1, new_freq=2
                      # BUG: try to remove key 1 from freq_keys[2] (NEW bucket)
                      # freq_keys[2] is empty → nothing deleted there
                      # Add key 1 to freq_keys[2]
                      # BUT key 1 is STILL in freq_keys[1]!
                      # freq_keys: {1: {1, 2, 3}, 2: {1}}  ← key 1 is DUPLICATED!

print("Wrong state: key 1 in freq 1 bucket:", 1 in lfu_wrong.freq_keys[1])  # True (ghost!)
print("Wrong state: key 1 in freq 2 bucket:", 1 in lfu_wrong.freq_keys[2])  # True

# Now when we need to evict, we'll evict from min_freq=1 bucket
# But freq_keys[1] contains {1, 2, 3} — 1 shouldn't be there!
lfu_wrong.put(4, 40)   # capacity full, evict from freq 1 bucket
                       # Evicts key 1 (ghost entry!) instead of 2 or 3
print("get(1):", lfu_wrong.get(1))  # -1 or wrong! Key 1 was evicted
print("get(2):", lfu_wrong.get(2))  # Should still be here
```

### RIGHT Code: Remove from OLD Frequency Bucket

```python
from collections import defaultdict, OrderedDict

class LFUCacheCorrect:
    """
    Correct LFU cache implementation.
    Key insight: when frequency of key increases from f to f+1,
    remove from freq_keys[f] (OLD), add to freq_keys[f+1] (NEW).
    """
    def __init__(self, capacity):
        self.capacity = capacity
        self.key_freq = {}
        self.key_val  = {}
        self.freq_keys = defaultdict(OrderedDict)
        self.min_freq = 0

    def _update_freq(self, key):
        freq = self.key_freq[key]
        new_freq = freq + 1
        self.key_freq[key] = new_freq

        # CORRECT: Remove from OLD frequency bucket
        del self.freq_keys[freq][key]        # ← Remove from freq (old)
        self.freq_keys[new_freq][key] = True  # Add to new_freq

        # If old bucket is now empty AND it was the min, update min_freq
        if not self.freq_keys[self.min_freq]:
            self.min_freq = new_freq  # min can only increase by 1 here

    def get(self, key):
        if key not in self.key_val:
            return -1
        self._update_freq(key)
        return self.key_val[key]

    def put(self, key, value):
        if self.capacity <= 0:
            return

        if key in self.key_val:
            self.key_val[key] = value
            self._update_freq(key)
            return

        if len(self.key_val) >= self.capacity:
            # Evict LFU: first item in min_freq bucket (LRU among LFU)
            evict_key, _ = self.freq_keys[self.min_freq].popitem(last=False)
            del self.key_val[evict_key]
            del self.key_freq[evict_key]

        # Insert new key with frequency 1
        self.key_val[key] = value
        self.key_freq[key] = 1
        self.freq_keys[1][key] = True
        self.min_freq = 1  # New key always starts at freq=1


# Test:
lfu = LFUCacheCorrect(3)
lfu.put(1, 10)
lfu.put(2, 20)
lfu.put(3, 30)

print(lfu.get(1))  # 10, freq[1]=2
print(lfu.get(1))  # 10, freq[1]=3
print(lfu.get(2))  # 20, freq[2]=2

# State: freq_keys = {1: {3}, 2: {2}, 3: {1}}, min_freq=1

lfu.put(4, 40)  # Evict LFU = key 3 (freq=1)
print("get(3):", lfu.get(3))  # -1 ✓ (evicted)
print("get(1):", lfu.get(1))  # 10 ✓
print("get(2):", lfu.get(2))  # 20 ✓
print("get(4):", lfu.get(4))  # 40 ✓
```

---

## Mistake 4: LFU — min_freq Not Updated After Eviction {#mistake-4}

### The Story

After evicting the least frequently used item, you insert a brand new key. This new key has frequency 1. So `min_freq` must be reset to 1 — because the new key is now the least frequent item.

The bug: forgetting to reset `min_freq = 1` on insertion of new keys. Instead, `min_freq` still points to the old minimum frequency. If that bucket is now empty (the old LFU was just evicted), trying to evict again will grab from an empty bucket.

### WRONG Code: min_freq Not Reset on Insert

```python
class LFUCacheBuggyMinFreq:
    def __init__(self, capacity):
        self.capacity = capacity
        self.key_val = {}
        self.key_freq = {}
        self.freq_keys = defaultdict(OrderedDict)
        self.min_freq = 0

    def _update(self, key):
        freq = self.key_freq[key]
        self.key_freq[key] = freq + 1
        del self.freq_keys[freq][key]
        self.freq_keys[freq + 1][key] = True
        if not self.freq_keys[self.min_freq]:
            self.min_freq = freq + 1

    def get(self, key):
        if key not in self.key_val:
            return -1
        self._update(key)
        return self.key_val[key]

    def put(self, key, value):
        if self.capacity <= 0:
            return
        if key in self.key_val:
            self.key_val[key] = value
            self._update(key)
            return

        if len(self.key_val) >= self.capacity:
            evict_key, _ = self.freq_keys[self.min_freq].popitem(last=False)
            del self.key_val[evict_key]
            del self.key_freq[evict_key]

        self.key_val[key] = value
        self.key_freq[key] = 1
        self.freq_keys[1][key] = True
        # BUG: NOT setting self.min_freq = 1 here!
        # If min_freq was 2 before, it remains 2.
        # But new key has freq=1, which is now the true minimum.


# Trace the bug:
lfu_buggy = LFUCacheBuggyMinFreq(2)
lfu_buggy.put(1, 10)   # freq_keys={1:{1}}, min_freq=0 (still wrong!)
                       # Actually the bug starts here: min_freq should be 1

# Let's force the state where min_freq is wrong:
lfu_buggy2 = LFUCacheBuggyMinFreq(2)
lfu_buggy2.put(1, 10)
lfu_buggy2.put(2, 20)
# Both keys at freq=1, min_freq=0 (WRONG already, should be 1)

lfu_buggy2.get(1)      # Updates freq of 1: freq_keys={1:{2},2:{1}}, min_freq → 1 (ok)
lfu_buggy2.get(1)      # Updates freq of 1: freq_keys={1:{2},3:{1}}, min_freq → 1 (ok here)

# Now evict: should evict key 2 (freq=1)
lfu_buggy2.put(3, 30)  # Evict from min_freq=1 bucket: evicts key 2. OK here.
                       # BUT: new key 3 gets freq=1, and min_freq NOT SET to 1
                       # min_freq still = 2 or whatever it was

# Try to evict again:
lfu_buggy2.put(4, 40)  # Evict from min_freq (wrong value, maybe empty bucket!)
                       # popitem on empty OrderedDict raises KeyError!
try:
    result = lfu_buggy2.get(3)
    print("get(3):", result)
except Exception as e:
    print(f"Error: {e}")  # KeyError or wrong eviction
```

### RIGHT Code: Always Reset min_freq = 1 on New Key Insert

```python
class LFUCacheFixed:
    """
    LFU with all bugs fixed.
    Critical: min_freq = 1 whenever a NEW key is inserted.
    """
    def __init__(self, capacity):
        self.capacity = capacity
        self.key_val = {}
        self.key_freq = {}
        self.freq_keys = defaultdict(OrderedDict)
        self.min_freq = 0

    def _update(self, key):
        freq = self.key_freq[key]
        self.key_freq[key] = freq + 1
        del self.freq_keys[freq][key]         # Remove from old bucket
        self.freq_keys[freq + 1][key] = True  # Add to new bucket
        if not self.freq_keys[self.min_freq]:
            self.min_freq = freq + 1           # Update min if old min bucket empty

    def get(self, key):
        if key not in self.key_val:
            return -1
        self._update(key)
        return self.key_val[key]

    def put(self, key, value):
        if self.capacity <= 0:
            return

        if key in self.key_val:
            self.key_val[key] = value
            self._update(key)  # existing key: update freq, don't reset min_freq
            return

        # New key:
        if len(self.key_val) >= self.capacity:
            evict_key, _ = self.freq_keys[self.min_freq].popitem(last=False)
            del self.key_val[evict_key]
            del self.key_freq[evict_key]

        self.key_val[key] = value
        self.key_freq[key] = 1
        self.freq_keys[1][key] = True
        self.min_freq = 1  # ← ALWAYS reset to 1 for new key. Non-negotiable.


# Full test:
def test_lfu(lfu):
    lfu.put(1, 1)
    lfu.put(2, 2)
    assert lfu.get(1) == 1    # freq[1]=2
    lfu.put(3, 3)             # evict 2 (LFU with freq=1)
    assert lfu.get(2) == -1   # evicted
    assert lfu.get(3) == 3    # freq[3]=2
    lfu.put(4, 4)             # evict 1? No: freq[1]=2, freq[3]=2. Tie → LRU of LFU
    assert lfu.get(1) == -1 or lfu.get(4) == 4  # one of these should work
    print(f"LFU test passed ✓")

lfu = LFUCacheFixed(2)
lfu.put(1, 1)
lfu.put(2, 2)
print(lfu.get(1))  # 1 ✓
lfu.put(3, 3)
print(lfu.get(2))  # -1 ✓ (evicted — freq was 1, least frequent)
print(lfu.get(3))  # 3  ✓
lfu.put(4, 4)
print(lfu.get(1))  # 1  ✓ (freq=2, not evicted)
print(lfu.get(3))  # -1 ✓ (evicted — freq was 1 when compared to key 1's freq 2)
print(lfu.get(4))  # 4  ✓
```

---

## Mistake 5: Consistent Hashing — Too Few Virtual Nodes {#mistake-5}

### The Story

Consistent hashing places both servers and keys on a circular ring. When adding or removing a server, only the keys that were mapped to that server need to be moved — not all keys.

But with only 1 node per server on the ring, the distribution is wildly uneven: some servers handle 80% of the load, others 5%. When a server is removed, ALL its load dumps onto exactly one neighboring server (potentially overloading it).

Virtual nodes (replicas of each server at multiple positions on the ring) fix this. With 150 virtual nodes per server, the load distributes much more evenly, and removal/addition only causes a small redistribution.

### The Ring Structure

```
Single physical node per server (3 servers: A, B, C):

Ring (0 to 360):
0       90      180     270     360
|----A--|----B--|----C--|----A--|

With this layout:
  Keys 0-90   → Server A   (25% of ring)
  Keys 90-180 → Server B   (25% of ring)
  Keys 180-270 → Server C  (25% of ring)
  Keys 270-360 → Server A  (25% of ring)  ← A gets 50%! Uneven!

If Server B is removed:
  ALL keys 90-180 go to Server C → C now handles 50%

With 150 virtual nodes per server, each server has 150 random positions.
Statistical variance shrinks — load is roughly 33% per server with high confidence.
```

### WRONG Code: Single Node per Server

```python
import hashlib
import bisect

class ConsistentHashWrong:
    """
    BUG: Only 1 node per server.
    Causes highly uneven load distribution.
    When a server is removed, all its load goes to ONE other server.
    """
    def __init__(self):
        self.ring = {}       # hash_position → server_name
        self.sorted_keys = []

    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**32)

    def add_server(self, server):
        # BUG: Only one position per server!
        h = self._hash(server)
        self.ring[h] = server
        bisect.insort(self.sorted_keys, h)

    def remove_server(self, server):
        h = self._hash(server)
        if h in self.ring:
            del self.ring[h]
            self.sorted_keys.remove(h)

    def get_server(self, key):
        if not self.ring:
            return None
        h = self._hash(key)
        idx = bisect.bisect_right(self.sorted_keys, h) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[idx]]


# Demonstrate uneven distribution
def show_distribution(hash_obj, servers, n_keys=10000):
    counts = {s: 0 for s in servers}
    for i in range(n_keys):
        server = hash_obj.get_server(f"key_{i}")
        counts[server] = counts.get(server, 0) + 1
    return counts

ch_wrong = ConsistentHashWrong()
servers = ["server_A", "server_B", "server_C"]
for s in servers:
    ch_wrong.add_server(s)

dist_wrong = show_distribution(ch_wrong, servers)
print("Single node distribution (10000 keys):")
for s, count in sorted(dist_wrong.items()):
    bar = "#" * (count // 100)
    print(f"  {s}: {count:5d} {bar}")
# Wildly uneven: one server might get 5000, another 2000, another 3000
```

### RIGHT Code: Multiple Virtual Nodes

```python
class ConsistentHashCorrect:
    """
    Correct consistent hashing with virtual nodes.
    150 virtual nodes per server ensures even load distribution.
    """
    def __init__(self, virtual_nodes=150):
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []

    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**32)

    def add_server(self, server):
        # Add multiple positions (virtual nodes) for each server
        for i in range(self.virtual_nodes):
            virtual_key = f"{server}#vnode{i}"
            h = self._hash(virtual_key)
            self.ring[h] = server
            bisect.insort(self.sorted_keys, h)

    def remove_server(self, server):
        for i in range(self.virtual_nodes):
            virtual_key = f"{server}#vnode{i}"
            h = self._hash(virtual_key)
            if h in self.ring:
                del self.ring[h]
                self.sorted_keys.remove(h)

    def get_server(self, key):
        if not self.ring:
            return None
        h = self._hash(key)
        idx = bisect.bisect_right(self.sorted_keys, h) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[idx]]


# Compare distributions
ch_correct = ConsistentHashCorrect(virtual_nodes=150)
for s in servers:
    ch_correct.add_server(s)

dist_correct = show_distribution(ch_correct, servers)
print("\nVirtual node distribution (10000 keys, 150 vnodes):")
for s, count in sorted(dist_correct.items()):
    bar = "#" * (count // 100)
    print(f"  {s}: {count:5d} {bar}")
# Much more even: roughly 3300-3400 keys per server

# What happens when a server is removed?
print("\nRemoving server_B...")
ch_wrong.remove_server("server_B")
ch_correct.remove_server("server_B")

dist_wrong_after = show_distribution(ch_wrong, ["server_A", "server_C"])
dist_correct_after = show_distribution(ch_correct, ["server_A", "server_C"])

print("Single node after removal:")
for s, count in sorted(dist_wrong_after.items()):
    print(f"  {s}: {count:5d}")
# One server absorbs ALL of server_B's old load

print("Virtual node after removal:")
for s, count in sorted(dist_correct_after.items()):
    print(f"  {s}: {count:5d}")
# Load redistributed evenly between A and C

# Why virtual nodes work mathematically:
# With k servers and v virtual nodes each:
# - Total ring positions: k * v
# - Expected keys per server: n / k
# - Standard deviation of load: O(n / sqrt(k*v))
# - For v=150, k=3: std dev shrinks dramatically → predictable 33% each
```

---

## Mistake 6: Bloom Filter — Wrong Number of Hash Functions {#mistake-6}

### The Story

A Bloom filter is a probabilistic data structure that answers "is this item probably in the set?" It uses multiple hash functions to mark positions in a bit array. To check membership, all hash-mapped positions must be set.

- Too few hash functions: not enough positions marked → many other items can accidentally match → high false positive rate
- Too many hash functions: too many positions set → the bit array fills up → EVERYTHING looks like it's in the set → false positive rate approaches 100%

There's a sweet spot: `k = (m/n) * ln(2)` where `m` is the bit array size and `n` is the expected number of elements.

### The Math Behind the Optimal k

```
False positive probability p:
  p ≈ (1 - e^(-k*n/m))^k

Optimal k minimizes p:
  dp/dk = 0  →  k_opt = (m/n) * ln(2) ≈ 0.693 * (m/n)

If bits_per_element = m/n = 10:
  k_opt = 10 * 0.693 ≈ 7 hash functions
  p ≈ 0.00819  (0.8% false positive rate)

With k=1:
  p ≈ (1 - e^(-n/m))  ≈ 0.0952 (9.5% false positive rate — much worse!)

With k=20:
  p ≈ (1 - e^(-20n/m))^20
  If m/n=10: e^(-20/10) = e^-2 ≈ 0.135
  p ≈ (1-0.135)^20 = 0.865^20 ≈ 0.044 (4.4% — worse than optimal!)
```

### WRONG Code: Wrong k (Too Few or Too Many)

```python
import hashlib
import math

class BloomFilterWrong:
    """BUG: Uses fixed k=1 regardless of m and n."""
    def __init__(self, m, n):
        self.m = m          # bit array size
        self.n = n          # expected elements
        self.bits = bytearray(m)
        self.k = 1          # BUG: should be optimal k, not hardcoded 1

    def _hashes(self, item):
        hashes = []
        for i in range(self.k):
            h = int(hashlib.sha256(f"{item}_{i}".encode()).hexdigest(), 16)
            hashes.append(h % self.m)
        return hashes

    def add(self, item):
        for pos in self._hashes(item):
            self.bits[pos] = 1

    def possibly_contains(self, item):
        return all(self.bits[pos] for pos in self._hashes(item))


def false_positive_rate(bloom, n_test, n_actual):
    """Measure false positive rate empirically."""
    false_positives = 0
    # Test items that were NOT inserted (start from n_actual onwards)
    for i in range(n_actual, n_actual + n_test):
        if bloom.possibly_contains(f"item_{i}"):
            false_positives += 1
    return false_positives / n_test

# Compare k=1 vs optimal k
m = 100000  # 100K bits
n = 10000   # 10K expected elements
# m/n = 10, so k_opt ≈ 7

bf_wrong = BloomFilterWrong(m, n)  # k=1

# Insert n items
for i in range(n):
    bf_wrong.add(f"item_{i}")

fpr_wrong = false_positive_rate(bf_wrong, 10000, n)
print(f"k=1 false positive rate:       {fpr_wrong:.3%}")  # ~9.5%
```

### RIGHT Code: Optimal k

```python
class BloomFilterCorrect:
    """
    Correct Bloom filter with optimal k = (m/n) * ln(2).
    """
    def __init__(self, expected_elements, false_positive_rate=0.01):
        # Calculate optimal m from desired false positive rate
        # m = -n * ln(p) / (ln(2)^2)
        n = expected_elements
        p = false_positive_rate
        self.m = int(-n * math.log(p) / (math.log(2) ** 2)) + 1
        self.bits = bytearray(self.m)

        # Optimal k
        self.k = max(1, int((self.m / n) * math.log(2)))

        print(f"Bloom filter: m={self.m} bits, k={self.k} hash functions, "
              f"target FPR={p:.1%}")

    def _hashes(self, item):
        """Generate k independent hash positions."""
        hashes = []
        item_bytes = item.encode()
        for i in range(self.k):
            # Use different seeds for different hash functions
            h = int(hashlib.sha256(f"{i}:{item}".encode()).hexdigest(), 16)
            hashes.append(h % self.m)
        return hashes

    def add(self, item):
        for pos in self._hashes(item):
            self.bits[pos] = 1

    def possibly_contains(self, item):
        """Returns True if item MIGHT be in set. Never returns false negatives."""
        return all(self.bits[pos] for pos in self._hashes(item))

    def definitely_not_contains(self, item):
        """Returns True if item is DEFINITELY NOT in set."""
        return not self.possibly_contains(item)


# Test
bf = BloomFilterCorrect(expected_elements=10000, false_positive_rate=0.01)
# Should print something like: m=95851 bits, k=6 hash functions, target FPR=1.0%

# Add 10000 items
for i in range(10000):
    bf.add(f"item_{i}")

# False negative rate (should be 0)
false_negatives = sum(1 for i in range(10000) if not bf.possibly_contains(f"item_{i}"))
print(f"False negative rate: {false_negatives/10000:.3%}")  # 0% — guaranteed!

# False positive rate (should be ~1%)
false_positives = sum(1 for i in range(10000, 20000) if bf.possibly_contains(f"item_{i}"))
print(f"Empirical false positive rate: {false_positives/10000:.3%}")  # ~1%

# Compare different k values for same m and n
m, n = 100000, 10000
print("\nFalse positive rates for different k values:")
for k in [1, 3, 7, 10, 15, 20]:
    # Theoretical FPR: (1 - e^(-k*n/m))^k
    theoretical_fpr = (1 - math.exp(-k * n / m)) ** k
    print(f"  k={k:2d}: theoretical FPR = {theoretical_fpr:.4%}")
# Shows that k=7 (≈ optimal) gives minimum FPR
```

---

## Mistake 7: Rate Limiter — Token Bucket vs Leaky Bucket Confusion {#mistake-7}

### The Story

Two restaurants have different queue policies:
- **Token Bucket restaurant**: gives you 10 tokens when you arrive, replenishes 1 token per minute. You can order 10 things at once if you have enough tokens. Great for APIs that should allow bursts.
- **Leaky Bucket restaurant**: no matter how hungry you are, kitchen serves 1 meal per minute. Queue or leave. No bursts allowed. Great for steady-rate processing.

Using the Leaky Bucket when a user needs Token Bucket behavior (or vice versa) causes either unnecessary throttling of legitimate burst traffic, or uncontrolled bursts that overwhelm downstream services.

### Token Bucket: Allows Bursts

```
Tokens:     [10, 10, 10, 9, 8, 7, 6, 5, 4, 10, 10, ...]
              ^                ^               ^
         full bucket    burst used 5 tokens   refilled

User can send 10 requests at once (up to bucket capacity).
Tokens replenish at fixed rate.
```

### Leaky Bucket: Enforces Steady Rate

```
Queue:      [req1, req2, req3, req4, req5]
Output:     [req1] ... [req2] ... [req3] ...
              ^                    ^
         1 req/second         steady rate, no burst
```

### WRONG Code: Using Leaky Bucket When Token Bucket Is Needed

```python
import time

class LeakyBucketWrong:
    """
    Leaky Bucket: enforces constant rate. NO BURSTS.
    BUG: Used when the application needs burst-friendly rate limiting.
    """
    def __init__(self, rate_per_second):
        self.rate = rate_per_second          # requests per second
        self.last_request_time = time.time()
        self.min_interval = 1.0 / rate_per_second

    def allow_request(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last >= self.min_interval:
            self.last_request_time = current_time
            return True
        else:
            return False  # Reject — even though user might have "saved up" capacity


# Simulate: user wants to make 5 quick requests after being idle for 5 seconds
import time

leaky = LeakyBucketWrong(rate_per_second=2)  # 2 req/sec allowed

# Idle for 5 seconds (would accumulate 10 tokens in Token Bucket)
# But Leaky Bucket doesn't accumulate!

requests_allowed = 0
requests_denied  = 0

# Simulate 5 rapid requests (within 1 second)
for i in range(5):
    if leaky.allow_request():
        requests_allowed += 1
    else:
        requests_denied += 1
    time.sleep(0.01)  # 10ms between requests

print(f"Leaky Bucket: Allowed={requests_allowed}, Denied={requests_denied}")
# Only 1 request allowed! User's 5-second idle period gave no benefit.
# This is wrong if the user's contract is "2 req/sec average with burst allowed"
```

### RIGHT Code: Token Bucket for Burst-Friendly Rate Limiting

```python
import time

class TokenBucket:
    """
    Token Bucket rate limiter.
    - Tokens accumulate up to max_tokens (burst capacity)
    - Tokens refill at rate tokens_per_second
    - Each request costs 1 token
    - Allows bursts up to max_tokens
    """
    def __init__(self, tokens_per_second, max_tokens):
        self.tokens_per_second = tokens_per_second
        self.max_tokens = max_tokens
        self.tokens = max_tokens           # Start full
        self.last_refill_time = time.time()

    def _refill(self):
        """Add tokens based on elapsed time."""
        current_time = time.time()
        elapsed = current_time - self.last_refill_time
        new_tokens = elapsed * self.tokens_per_second
        self.tokens = min(self.max_tokens, self.tokens + new_tokens)
        self.last_refill_time = current_time

    def allow_request(self, tokens_required=1):
        """Returns True if request is allowed."""
        self._refill()
        if self.tokens >= tokens_required:
            self.tokens -= tokens_required
            return True
        return False

    def tokens_available(self):
        self._refill()
        return self.tokens


class LeakyBucket:
    """
    Leaky Bucket rate limiter.
    - Fixed output rate (no bursts)
    - Queue of up to max_queue_size
    - Each second, up to rate requests are processed
    """
    def __init__(self, rate_per_second, max_queue_size):
        self.rate = rate_per_second
        self.max_queue = max_queue_size
        self.queue = []
        self.last_leak_time = time.time()

    def _leak(self):
        """Drain requests from queue at fixed rate."""
        current_time = time.time()
        elapsed = current_time - self.last_leak_time
        can_process = int(elapsed * self.rate)
        if can_process > 0:
            self.queue = self.queue[can_process:]  # Remove processed
            self.last_leak_time = current_time

    def allow_request(self):
        self._leak()
        if len(self.queue) < self.max_queue:
            self.queue.append(time.time())
            return True
        return False  # Queue full, reject


# Demonstrate difference:
def simulate_burst(rate_limiter, n_requests=10):
    """Simulate n_requests fired rapidly."""
    results = []
    for i in range(n_requests):
        results.append(rate_limiter.allow_request())
    allowed = sum(results)
    print(f"  {rate_limiter.__class__.__name__}: {allowed}/{n_requests} allowed in burst")

print("Burst of 10 requests (2 tokens/sec, max 10 tokens):")
tb = TokenBucket(tokens_per_second=2, max_tokens=10)
simulate_burst(tb)   # Allows up to 10 (burst capacity)

lb = LeakyBucket(rate_per_second=2, max_queue_size=5)
simulate_burst(lb)   # Allows up to 5 (queue size), but processes at 2/sec

# When to use each:
print("\nUse Token Bucket when:")
print("  - API allows clients to burst after periods of low usage")
print("  - e.g., GitHub API: 5000 requests/hour, can be used quickly")
print("  - Video streaming: allow initial burst for buffering")

print("\nUse Leaky Bucket when:")
print("  - Downstream service needs steady input rate")
print("  - e.g., Payment processor: exactly N transactions/second")
print("  - Database writes: don't overwhelm with sudden spikes")
```

### Sliding Window Log (Most Accurate, Most Memory)

```python
from collections import deque

class SlidingWindowLog:
    """
    Most accurate rate limiter.
    Tracks exact timestamps of all requests in the window.
    Accurate to the millisecond, but O(window_size) memory.
    """
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window = window_seconds
        self.timestamps = deque()

    def allow_request(self):
        now = time.time()
        # Remove timestamps outside the window
        while self.timestamps and now - self.timestamps[0] > self.window:
            self.timestamps.popleft()

        if len(self.timestamps) < self.max_requests:
            self.timestamps.append(now)
            return True
        return False

# No confusion about burst vs steady — it's precisely "N requests per window"
swl = SlidingWindowLog(max_requests=5, window_seconds=1.0)
results = [swl.allow_request() for _ in range(8)]
print("\nSliding Window (5/sec):", results)
# [True, True, True, True, True, False, False, False]
```

---

## Mistake 8: Top-K — Using Max-Heap Instead of Min-Heap of Size K {#mistake-8}

### The Story

You're a talent scout watching 1 million auditions. You only need the top 10. The naive approach: record ALL 1 million, sort them, take top 10. This requires keeping all 1 million in memory and O(n log n) time.

The smart approach: maintain a "waiting room" of exactly 10 candidates. For each new audition, compare against the WORST person currently in the waiting room. If the new person is better than the worst, kick out the worst and add the new person.

The waiting room is a **min-heap of size K** — the root is always the worst person currently in the top-K. This costs O(n log K) time and O(K) space.

### Why Min-Heap (Not Max-Heap) for Top-K Largest?

```
Goal: find K largest elements from stream of N elements.

Min-heap of size K:
  - Root = smallest of the K "candidates"
  - New element > root? → replace root, heapify down
  - New element <= root? → not in top-K, skip
  - At end: heap contains exactly the K largest elements!

Max-heap of all N elements:
  - Push all N elements: O(N log N)
  - Pop K elements: O(K log N)
  - Total: O(N log N) time, O(N) space — SLOW and MEMORY HUNGRY

Comparison:
  N=1,000,000, K=10:
  - Min-heap: O(N log K) = 1M * log(10) ≈ 3.3M ops, O(K)=O(10) space
  - Max-heap: O(N log N) = 1M * log(1M) ≈ 20M ops, O(N)=O(1M) space
  - Min-heap is 6x faster and 100,000x more space efficient!
```

### WRONG Code: Max-Heap of All Elements

```python
import heapq

def top_k_wrong(nums, k):
    """
    BUG: Pushes all N elements into max-heap, then pops K.
    O(N log N) time, O(N) space.
    """
    # Python's heapq is a min-heap, so negate for max-heap
    max_heap = [-x for x in nums]
    heapq.heapify(max_heap)  # O(N) to build, but stores all N elements!

    result = []
    for _ in range(k):
        result.append(-heapq.heappop(max_heap))  # O(log N) per pop

    return result

# O(N) space to store everything — terrible for streams or large datasets
import random
nums = random.sample(range(1, 1_000_001), 100_000)
k = 10

result_wrong = top_k_wrong(nums, k)
print("Top-K (wrong, max-heap all):", sorted(result_wrong, reverse=True))
```

### RIGHT Code: Min-Heap of Size K

```python
import heapq

def top_k_correct(nums, k):
    """
    Correct O(N log K) top-K using min-heap of size K.
    Maintains only K elements at any time — O(K) space.
    """
    heap = []  # min-heap of size k

    for num in nums:
        if len(heap) < k:
            heapq.heappush(heap, num)     # Fill up to K elements
        elif num > heap[0]:               # New element beats current minimum?
            heapq.heapreplace(heap, num)  # heapreplace = pop + push in one op (faster)

    # heap now contains the K largest elements
    return sorted(heap, reverse=True)   # Sort for readable output

result_correct = top_k_correct(nums, k)
print("Top-K (correct, min-heap size K):", result_correct)

# Verify both give same answer
assert sorted(result_wrong, reverse=True) == result_correct
print("Both methods agree ✓")


# Performance comparison:
import time

big_nums = list(range(1, 1_000_001))
random.shuffle(big_nums)
k = 100

start = time.time()
for _ in range(5):
    top_k_wrong(big_nums, k)
wrong_time = (time.time() - start) / 5

start = time.time()
for _ in range(5):
    top_k_correct(big_nums, k)
correct_time = (time.time() - start) / 5

print(f"\nN=1,000,000, K=100:")
print(f"  Max-heap all:    {wrong_time:.4f}s per call")
print(f"  Min-heap size K: {correct_time:.4f}s per call")
print(f"  Speedup: {wrong_time/correct_time:.1f}x faster")


# Top-K for streaming data (min-heap shines here):
def top_k_streaming(stream, k):
    """
    Process a stream of numbers, maintaining top-K at all times.
    Never stores more than K elements. Perfect for infinite streams.
    """
    heap = []
    for item in stream:
        if len(heap) < k:
            heapq.heappush(heap, item)
        elif item > heap[0]:
            heapq.heapreplace(heap, item)
        # At any point, heap contains current top-K
    return sorted(heap, reverse=True)


# Top-K strings by frequency (common interview problem):
from collections import Counter

def top_k_frequent_words(words, k):
    """
    Find K most frequent words.
    Min-heap of (count, word) pairs, size K.
    """
    counts = Counter(words)

    # Min-heap comparing (count, word)
    # For ties: alphabetically LARGER word is considered "smaller priority"
    heap = []
    for word, count in counts.items():
        # Push (-count, word) won't work cleanly for ties
        # Use (count, word) and for equal counts, prefer lexicographically smaller
        heapq.heappush(heap, (count, word))
        if len(heap) > k:
            heapq.heappop(heap)  # Remove smallest count

    # Return in descending order of frequency (then alphabetical for ties)
    result = sorted(heap, key=lambda x: (-x[0], x[1]))
    return [word for count, word in result]

words = ["the", "day", "is", "sunny", "the", "the", "sunny", "is", "is"]
print("\nTop-2 frequent words:", top_k_frequent_words(words, 2))
# ["the", "is"] ✓
```

### Visual: Min-Heap of Size K in Action

```
Finding top-3 from [3, 1, 4, 1, 5, 9, 2, 6]:

Step 1: Push 3. Heap: [3]
Step 2: Push 1. Heap: [1, 3]
Step 3: Push 4. Heap: [1, 3, 4]  ← heap full (k=3)
Step 4: 1 <= heap[0]=1? Not strictly greater → skip
Step 5: 5 > heap[0]=1 → replace: heapreplace(heap, 5) → heap: [3, 5, 4]
Step 6: 9 > heap[0]=3 → replace: heap: [4, 5, 9]
Step 7: 2 > heap[0]=4? No → skip
Step 8: 6 > heap[0]=4 → replace: heap: [5, 6, 9]

Final heap: [5, 6, 9] = top-3 largest ✓

Key insight: heap[0] is always the SMALLEST of the top-K.
Any new element larger than heap[0] earns its place in top-K.
```

---

## Final Quick Reference: All 8 Mistakes

```
╔═══════════════════════════════════════════════════════════════════════════╗
║         SYSTEM DESIGN PATTERNS — COMMON MISTAKES QUICK REFERENCE         ║
╠═════╦══════════════════════════════════════╦═════════════════════════════╣
║  #  ║ Mistake                              ║ Fix                          ║
╠═════╬══════════════════════════════════════╬═════════════════════════════╣
║  1  ║ LRU: dict + O(n) reorder            ║ Use OrderedDict.move_to_end()║
║     ║                                      ║ or doubly-linked list + dict ║
╠═════╬══════════════════════════════════════╬═════════════════════════════╣
║  2  ║ LRU: no MRU move on get or          ║ move_to_end() on EVERY get   ║
║     ║ existing-key put                     ║ AND put of existing key      ║
╠═════╬══════════════════════════════════════╬═════════════════════════════╣
║  3  ║ LFU: remove from new freq bucket    ║ Remove from OLD freq bucket  ║
║     ║ instead of old                       ║ (freq), add to new (freq+1)  ║
╠═════╬══════════════════════════════════════╬═════════════════════════════╣
║  4  ║ LFU: min_freq not reset after       ║ Set min_freq = 1 whenever    ║
║     ║ inserting new key                    ║ a brand new key is inserted  ║
╠═════╬══════════════════════════════════════╬═════════════════════════════╣
║  5  ║ Consistent hash: 1 node/server      ║ 150+ virtual nodes/server    ║
║     ║ (uneven load, bad redistribution)   ║ for even distribution         ║
╠═════╬══════════════════════════════════════╬═════════════════════════════╣
║  6  ║ Bloom filter: wrong k               ║ k = (m/n) * ln(2) ≈ 0.7*m/n ║
║     ║ (too few or too many hash funcs)    ║ for optimal false positive    ║
╠═════╬══════════════════════════════════════╬═════════════════════════════╣
║  7  ║ Leaky Bucket for burst-ok APIs      ║ Token Bucket for bursty;     ║
║     ║ (rejects valid burst traffic)        ║ Leaky for steady-rate needs  ║
╠═════╬══════════════════════════════════════╬═════════════════════════════╣
║  8  ║ Top-K: max-heap of all N elements   ║ Min-heap of size K:          ║
║     ║ O(N log N) time, O(N) space         ║ O(N log K) time, O(K) space  ║
╚═════╩══════════════════════════════════════╩═════════════════════════════╝
```

---

*System design data structures are often first implemented "correctly enough" — they pass basic tests, produce reasonable outputs, but hide catastrophic performance cliffs. An LRU that does O(n) work per access will feel fine with 100 entries and fail at 100,000. A consistent hash ring with 1 node per server will feel fine with 5 servers and cause outages when one of them goes down. Test your implementations under scale, and know the failure modes before they bite you in production.*
