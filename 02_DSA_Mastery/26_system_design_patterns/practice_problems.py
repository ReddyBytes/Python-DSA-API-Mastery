# =============================================================================
# MODULE 26 — SYSTEM DESIGN PATTERNS (DSA): Practice Problems
# =============================================================================
# Run: python3 practice_problems.py
#
# Covers: LRU Cache (OrderedDict + doubly linked list), LFU Cache,
#         Rate Limiter (token bucket + sliding window), consistent hashing,
#         bloom filter, skip list basics
#
# This is where DSA meets real engineering.
# Every design here is a direct application of data structures you've mastered.
# =============================================================================

import time
import math
import random
import hashlib
from collections import OrderedDict, defaultdict
from typing import Optional


# =============================================================================
# PROBLEM 1A — LRU Cache (using OrderedDict)
# =============================================================================
#
# Design a cache that evicts the Least Recently Used item when full.
#
# Python's OrderedDict preserves insertion order AND lets you move entries
# to the front or back in O(1).  This is the fastest way to code LRU in Python.
#
# Invariant: most recently used item is at the BACK (end) of the dict.
#            least recently used item is at the FRONT (start).
#
# Operations:
#   get(key)        → O(1): return value, move to back (mark as recently used)
#   put(key, value) → O(1): insert/update, move to back, evict front if full
#
# Time:  O(1) for both operations
# Space: O(capacity)
# =============================================================================

class LRUCache:
    """LRU Cache using Python's OrderedDict (interview-ready, minimal code)."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()   # key → value, ordered by recency

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)   # mark as most recently used
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)   # evict LRU (front of ordered dict)


# =============================================================================
# PROBLEM 1B — LRU Cache (doubly linked list + hashmap)
# =============================================================================
#
# The raw implementation — shows exactly how O(1) operations work.
#
# Data structures:
#   Hashmap (dict): key → DLL node          → O(1) lookup
#   Doubly linked list: tracks recency order → O(1) insert/delete
#
# Layout: head (dummy) ↔ [LRU nodes...] ↔ [MRU node] ↔ tail (dummy)
#   Most recently used is just before tail.
#   Least recently used is just after head.
#
# When we access a node, we cut it out of the list and re-insert before tail.
# When capacity exceeded, we remove the node just after head.
# =============================================================================

class DLLNode:
    __slots__ = ('key', 'val', 'prev', 'next')
    def __init__(self, key=0, val=0):
        self.key  = key
        self.val  = val
        self.prev = None
        self.next = None


class LRUCacheDLL:
    """LRU Cache using explicit doubly linked list + hashmap."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache    = {}   # key → DLLNode

        # Dummy sentinel nodes — simplify edge-case handling
        self.head = DLLNode()   # ← LRU end (evict from here)
        self.tail = DLLNode()   # ← MRU end (insert here)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: DLLNode):
        """Cut a node out of the doubly linked list in O(1)."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_before_tail(self, node: DLLNode):
        """Insert node just before tail (marks it as most recently used)."""
        node.prev        = self.tail.prev
        node.next        = self.tail
        self.tail.prev.next = node
        self.tail.prev   = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._insert_before_tail(node)   # promote to MRU position
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            node = self.cache[key]
            node.val = value
            self._remove(node)
            self._insert_before_tail(node)
        else:
            if len(self.cache) == self.capacity:
                # Evict LRU: the node just after head
                lru_node = self.head.next
                self._remove(lru_node)
                del self.cache[lru_node.key]
            node = DLLNode(key, value)
            self.cache[key] = node
            self._insert_before_tail(node)


# =============================================================================
# PROBLEM 2 — LFU Cache (Least Frequently Used)
# =============================================================================
#
# Like LRU but evicts the item accessed the FEWEST times.
# Tie-break: among items with the same frequency, evict the LEAST RECENTLY USED.
#
# Key insight: use a dict-of-OrderedDicts, indexed by frequency.
#   freq_map[f] = OrderedDict of {key: value} accessed exactly f times
#   key_freq[key] = current access count of key
#   min_freq = current minimum frequency (updated during operations)
#
# Why OrderedDict per frequency?
#   Within a frequency bucket, we still need LRU order.
#   OrderedDict gives O(1) removal of the oldest (LRU) entry in that bucket.
#
# Time:  O(1) amortised for both get and put
# Space: O(capacity)
# =============================================================================

class LFUCache:
    """LFU Cache with O(1) operations using frequency buckets."""

    def __init__(self, capacity: int):
        self.capacity  = capacity
        self.key_val   = {}                        # key → value
        self.key_freq  = {}                        # key → access frequency
        self.freq_map  = defaultdict(OrderedDict)  # freq → {key: value} ordered by recency
        self.min_freq  = 0

    def _increment_freq(self, key):
        """Move key from its current frequency bucket to the next."""
        freq = self.key_freq[key]
        val  = self.key_val[key]

        # Remove from current frequency bucket
        del self.freq_map[freq][key]
        if not self.freq_map[freq] and freq == self.min_freq:
            self.min_freq += 1   # current min bucket is now empty, so min goes up

        # Add to next frequency bucket
        new_freq = freq + 1
        self.key_freq[key] = new_freq
        self.freq_map[new_freq][key] = val   # appended to end = most recently used

    def get(self, key: int) -> int:
        if key not in self.key_val:
            return -1
        self._increment_freq(key)
        return self.key_val[key]

    def put(self, key: int, value: int) -> None:
        if self.capacity <= 0:
            return
        if key in self.key_val:
            self.key_val[key] = value
            # Update the value in the freq bucket too
            freq = self.key_freq[key]
            self.freq_map[freq][key] = value
            self._increment_freq(key)
        else:
            if len(self.key_val) == self.capacity:
                # Evict: LRU item in the minimum-frequency bucket
                evict_key, _ = self.freq_map[self.min_freq].popitem(last=False)
                del self.key_val[evict_key]
                del self.key_freq[evict_key]
            # Insert new key with frequency 1
            self.key_val[key]      = value
            self.key_freq[key]     = 1
            self.freq_map[1][key]  = value
            self.min_freq          = 1


# =============================================================================
# PROBLEM 3A — Rate Limiter: Token Bucket
# =============================================================================
#
# Allow up to `rate` requests per second on average, but permit short bursts
# up to `capacity` tokens.
#
# Mental model: a bucket that refills at a steady rate.
#   - Each second, `rate` tokens are added (up to `capacity`).
#   - Each request consumes one token.
#   - If bucket is empty → reject request.
#
# Key property: Token Bucket allows BURST traffic.
#   If no requests arrive for 5 seconds, 5*rate tokens accumulate (capped).
#   The next burst of requests can use those accumulated tokens.
#
# Time:  O(1) per request
# Space: O(1)
# =============================================================================

class TokenBucketRateLimiter:
    """Token bucket rate limiter — allows controlled burst traffic."""

    def __init__(self, capacity: float, rate: float):
        """
        capacity: maximum tokens (= max burst size)
        rate:     tokens added per second
        """
        self.capacity  = capacity
        self.rate      = rate
        self.tokens    = capacity   # start full
        self.last_time = time.monotonic()

    def allow(self) -> bool:
        """Return True if the request is allowed (consume one token)."""
        now = time.monotonic()
        elapsed = now - self.last_time
        # Refill tokens proportional to elapsed time
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_time = now

        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False


# =============================================================================
# PROBLEM 3B — Rate Limiter: Sliding Window Log
# =============================================================================
#
# More accurate than fixed-window counter: track the exact timestamp of every
# request in a deque. A request is allowed if fewer than `limit` requests
# occurred in the past `window_seconds`.
#
# Trade-off vs token bucket:
#   - Sliding window log: precise, but O(requests) memory per user.
#   - Token bucket: O(1) memory, allows bursts.
#
# Time:  O(requests in window) per request (amortised O(1) for steady traffic)
# Space: O(requests in window)
# =============================================================================

class SlidingWindowRateLimiter:
    """Sliding window log rate limiter — precise, no bursts beyond limit."""

    def __init__(self, limit: int, window_seconds: float):
        """
        limit:          max requests per window
        window_seconds: length of the sliding window
        """
        self.limit   = limit
        self.window  = window_seconds
        self.log     = deque()   # timestamps of recent requests

    def allow(self) -> bool:
        now = time.monotonic()
        cutoff = now - self.window
        # Remove timestamps older than the window
        while self.log and self.log[0] <= cutoff:
            self.log.popleft()
        if len(self.log) < self.limit:
            self.log.append(now)
            return True
        return False


# import needed for deque above
from collections import deque


# =============================================================================
# PROBLEM 4 — Consistent Hashing Ring
# =============================================================================
#
# Distribute keys across servers so that adding/removing a server only
# remaps a small fraction of keys (instead of rehashing everything).
#
# Virtual nodes: each physical server gets `num_replicas` positions on the
# ring, spreading load more evenly.
#
# Mental model: think of 0..2^32-1 as a circular ring.
#   Each server sits at multiple points on the ring.
#   A key maps to the server at the first ring position >= key's hash.
#   (Wrap around at the end of the ring.)
#
# Why consistent hashing?
#   With naive modulo hashing (key % n), adding/removing a server remaps
#   ALL keys.  With consistent hashing, only ~(1/n) of keys move.
#
# Time:  O(log(n * replicas)) per lookup (binary search on sorted ring)
# Space: O(n * replicas)
# =============================================================================

import bisect

class ConsistentHashRing:
    """Consistent hash ring with virtual nodes."""

    def __init__(self, num_replicas: int = 100):
        self.num_replicas = num_replicas
        self.ring         = []    # sorted list of (hash_value, server_name)
        self.hash_to_node = {}    # hash_value → server_name

    def _hash(self, key: str) -> int:
        """SHA-256 hash truncated to a 32-bit integer."""
        return int(hashlib.sha256(key.encode()).hexdigest(), 16) % (2 ** 32)

    def add_node(self, node: str):
        """Add a server to the ring at `num_replicas` virtual positions."""
        for i in range(self.num_replicas):
            virtual_key = f"{node}#{i}"
            h = self._hash(virtual_key)
            bisect.insort(self.ring, h)          # keep ring sorted
            self.hash_to_node[h] = node

    def remove_node(self, node: str):
        """Remove a server and all its virtual nodes from the ring."""
        for i in range(self.num_replicas):
            virtual_key = f"{node}#{i}"
            h = self._hash(virtual_key)
            idx = bisect.bisect_left(self.ring, h)
            if idx < len(self.ring) and self.ring[idx] == h:
                self.ring.pop(idx)
                del self.hash_to_node[h]

    def get_node(self, key: str) -> Optional[str]:
        """Return the server responsible for `key`."""
        if not self.ring:
            return None
        h   = self._hash(key)
        idx = bisect.bisect(self.ring, h) % len(self.ring)   # wrap around
        return self.hash_to_node[self.ring[idx]]


# =============================================================================
# PROBLEM 5 — Bloom Filter
# =============================================================================
#
# Probabilistic set membership structure:
#   - "definitely not in set" → 100% accurate (no false negatives)
#   - "probably in set"       → may produce false positives
#
# Mental model: a bit array of size m + k hash functions.
#   Add(x):      set k bits (the k hash positions for x) to 1.
#   Contains(x): return True only if ALL k bit positions are 1.
#
# Why is it useful?
#   Space-efficient — stores membership without the actual values.
#   Used in databases (avoid disk lookups for definitely-missing keys),
#   network routers (fast URL deduplication), spam filters.
#
# False positive rate:  (1 - e^(-kn/m))^k  where n = items inserted
# Optimal k:           k = (m/n) * ln(2)
#
# Time:  O(k) per operation where k = number of hash functions
# Space: O(m) bits — tiny compared to storing actual values
# =============================================================================

class BloomFilter:
    """Space-efficient probabilistic membership test."""

    def __init__(self, expected_items: int, false_positive_rate: float = 0.01):
        """
        expected_items:       n — how many items you plan to insert
        false_positive_rate:  desired false positive probability
        """
        # Optimal bit array size: m = -n * ln(p) / (ln2)^2
        self.m = math.ceil(
            -expected_items * math.log(false_positive_rate) / (math.log(2) ** 2)
        )
        # Optimal number of hash functions: k = (m/n) * ln(2)
        self.k = max(1, round((self.m / expected_items) * math.log(2)))
        self.bits = bytearray(math.ceil(self.m / 8))   # compact bit storage

    def _hash_positions(self, item: str):
        """Generate k independent hash positions for item."""
        # Double-hashing: simulate k hash functions using two base hashes
        h1 = int(hashlib.md5(item.encode()).hexdigest(), 16)
        h2 = int(hashlib.sha1(item.encode()).hexdigest(), 16)
        for i in range(self.k):
            yield ((h1 + i * h2) % self.m)

    def _set_bit(self, pos: int):
        self.bits[pos // 8] |= (1 << (pos % 8))

    def _get_bit(self, pos: int) -> bool:
        return bool(self.bits[pos // 8] & (1 << (pos % 8)))

    def add(self, item: str):
        """Insert item into the filter."""
        for pos in self._hash_positions(item):
            self._set_bit(pos)

    def contains(self, item: str) -> bool:
        """
        Return True if item is PROBABLY in the set.
        Return False if item is DEFINITELY NOT in the set.
        """
        return all(self._get_bit(pos) for pos in self._hash_positions(item))


# =============================================================================
# PROBLEM 6 — Skip List (basics)
# =============================================================================
#
# A probabilistic data structure that provides O(log n) average search, insert,
# and delete — like a balanced BST, but far simpler to implement.
#
# Mental model: multiple layers of linked lists.
#   - Layer 0: all elements in sorted order (like a regular sorted linked list).
#   - Layer 1: roughly half the elements (express lane — skip every other node).
#   - Layer 2: roughly quarter of elements (faster express lane).
#   - ...
#
# Search: start from the top (sparse) layer, move right while next < target,
#         drop down a layer when you overshoot.  You reach the element in
#         O(log n) steps on average.
#
# Insertion: search to find the position, then randomly decide how many layers
#            the new node participates in (coin flip per level).
#
# Why random height?
#   No need to rebalance like AVL/Red-Black trees.
#   Random promotion gives O(log n) expected height without complex rotations.
#
# Time:  O(log n) expected for search/insert/delete
# Space: O(n) expected (each element appears in ~2 layers on average)
# =============================================================================

class SkipListNode:
    __slots__ = ('val', 'forward')
    def __init__(self, val, level):
        self.val     = val
        self.forward = [None] * (level + 1)   # forward[i] = next node at level i


class SkipList:
    """
    Sorted skip list supporting search, insert, and delete.
    Supports integer values; easily extended to (key, value) pairs.
    """
    MAX_LEVEL = 16
    P         = 0.5    # probability of promoting to next level

    def __init__(self):
        self.level  = 0
        self.header = SkipListNode(float('-inf'), self.MAX_LEVEL)

    def _random_level(self) -> int:
        """Coin-flip promotion: new node gets level 0..MAX_LEVEL."""
        lvl = 0
        while random.random() < self.P and lvl < self.MAX_LEVEL:
            lvl += 1
        return lvl

    def search(self, target: int) -> bool:
        """Return True if target exists in the skip list."""
        curr = self.header
        for i in range(self.level, -1, -1):   # start from highest level
            # Move right while next node is still < target
            while curr.forward[i] and curr.forward[i].val < target:
                curr = curr.forward[i]
            # Drop down a level
        # Check level 0 (the base sorted list)
        curr = curr.forward[0]
        return curr is not None and curr.val == target

    def insert(self, val: int):
        """Insert val into the skip list."""
        update = [None] * (self.MAX_LEVEL + 1)
        curr   = self.header

        for i in range(self.level, -1, -1):
            while curr.forward[i] and curr.forward[i].val < val:
                curr = curr.forward[i]
            update[i] = curr   # remember last node at each level before val

        new_level = self._random_level()
        if new_level > self.level:
            # New levels introduced: header is the predecessor at those levels
            for i in range(self.level + 1, new_level + 1):
                update[i] = self.header
            self.level = new_level

        new_node = SkipListNode(val, new_level)
        for i in range(new_level + 1):
            new_node.forward[i]    = update[i].forward[i]
            update[i].forward[i]   = new_node

    def delete(self, val: int) -> bool:
        """Remove val from skip list. Return True if val was found."""
        update = [None] * (self.MAX_LEVEL + 1)
        curr   = self.header

        for i in range(self.level, -1, -1):
            while curr.forward[i] and curr.forward[i].val < val:
                curr = curr.forward[i]
            update[i] = curr

        target_node = curr.forward[0]
        if target_node is None or target_node.val != val:
            return False   # not found

        for i in range(self.level + 1):
            if update[i].forward[i] != target_node:
                break
            update[i].forward[i] = target_node.forward[i]

        # Shrink level if top layers are now empty
        while self.level > 0 and self.header.forward[self.level] is None:
            self.level -= 1

        return True

    def to_list(self):
        """Return all values in sorted order (level 0 traversal)."""
        result = []
        curr   = self.header.forward[0]
        while curr:
            result.append(curr.val)
            curr = curr.forward[0]
        return result


# =============================================================================
# TEST RUNNER
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MODULE 26 — SYSTEM DESIGN PATTERNS: Practice Problems")
    print("=" * 60)

    # --- Problem 1A: LRU Cache (OrderedDict) ---
    print("\n[1A] LRU Cache (OrderedDict)")
    lru = LRUCache(2)
    lru.put(1, 1)
    lru.put(2, 2)
    assert lru.get(1) == 1      # cache: {2:2, 1:1} (1 is MRU)
    lru.put(3, 3)               # evicts key 2 (LRU); cache: {1:1, 3:3}
    assert lru.get(2) == -1     # 2 was evicted
    lru.put(4, 4)               # evicts key 1; cache: {3:3, 4:4}
    assert lru.get(1) == -1
    assert lru.get(3) == 3
    assert lru.get(4) == 4
    print("  OrderedDict-based LRU: all assertions passed.")

    # --- Problem 1B: LRU Cache (DLL) ---
    print("\n[1B] LRU Cache (Doubly Linked List)")
    lru2 = LRUCacheDLL(2)
    lru2.put(1, 1); lru2.put(2, 2)
    assert lru2.get(1) == 1
    lru2.put(3, 3)              # evicts 2
    assert lru2.get(2) == -1
    lru2.put(4, 4)              # evicts 1
    assert lru2.get(1) == -1
    assert lru2.get(3) == 3
    assert lru2.get(4) == 4
    print("  DLL-based LRU: all assertions passed.")

    # --- Problem 2: LFU Cache ---
    print("\n[2] LFU Cache")
    lfu = LFUCache(2)
    lfu.put(1, 1); lfu.put(2, 2)
    assert lfu.get(1) == 1      # freq[1]=2, freq[2]=1
    lfu.put(3, 3)               # evicts key 2 (freq=1, LRU among freq-1 keys)
    assert lfu.get(2) == -1     # 2 was evicted
    assert lfu.get(3) == 3      # freq[3]=2
    lfu.put(4, 4)               # evicts key 1 or 3 (both freq=2); 1 is LRU → evict 1
    assert lfu.get(1) == -1
    assert lfu.get(3) == 3
    assert lfu.get(4) == 4
    print("  LFU Cache: all assertions passed.")

    # --- Problem 3A: Token Bucket ---
    print("\n[3A] Token Bucket Rate Limiter")
    tb = TokenBucketRateLimiter(capacity=5, rate=2)   # 2 tokens/sec, burst up to 5
    allowed = [tb.allow() for _ in range(5)]          # burst: all 5 should pass
    assert all(allowed), f"Expected all allowed, got {allowed}"
    blocked = tb.allow()                              # bucket empty, should block
    assert not blocked, "Expected block when bucket empty"
    print("  Token Bucket: all assertions passed.")

    # --- Problem 3B: Sliding Window ---
    print("\n[3B] Sliding Window Rate Limiter")
    sw = SlidingWindowRateLimiter(limit=3, window_seconds=1.0)
    assert sw.allow()    # request 1
    assert sw.allow()    # request 2
    assert sw.allow()    # request 3
    assert not sw.allow()  # 4th in same window → blocked
    print("  Sliding Window: all assertions passed.")

    # --- Problem 4: Consistent Hash Ring ---
    print("\n[4] Consistent Hashing Ring")
    ring = ConsistentHashRing(num_replicas=50)
    servers = ["server-A", "server-B", "server-C"]
    for s in servers:
        ring.add_node(s)
    # All keys should map to a known server
    keys = [f"user:{i}" for i in range(100)]
    assignments = {k: ring.get_node(k) for k in keys}
    assert all(v in servers for v in assignments.values())
    # After removing server-B, keys reassign to remaining servers
    ring.remove_node("server-B")
    for k in keys:
        node = ring.get_node(k)
        assert node in ["server-A", "server-C"], f"Key {k} mapped to unknown server {node}"
    print(f"  Consistent Hashing: all assertions passed.")
    # Show distribution
    dist = defaultdict(int)
    for k in keys:
        dist[ring.get_node(k)] += 1
    for s, count in sorted(dist.items()):
        print(f"    {s}: {count} keys")

    # --- Problem 5: Bloom Filter ---
    print("\n[5] Bloom Filter")
    bf = BloomFilter(expected_items=1000, false_positive_rate=0.01)
    items = [f"item-{i}" for i in range(500)]
    for item in items:
        bf.add(item)
    # No false negatives: every inserted item must return True
    for item in items:
        assert bf.contains(item), f"False negative for {item}"
    # Measure false positive rate on unseen items
    fp_count = sum(1 for i in range(500, 2000) if bf.contains(f"item-{i}"))
    fp_rate  = fp_count / 1500
    print(f"  Inserted 500 items. False positive rate on 1500 unseen: {fp_rate:.3f} (target ≤0.05)")
    assert fp_rate < 0.05, f"False positive rate {fp_rate:.3f} too high"
    print("  Bloom Filter: all assertions passed.")

    # --- Problem 6: Skip List ---
    print("\n[6] Skip List")
    sl = SkipList()
    values = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
    for v in values:
        sl.insert(v)
    sorted_vals = sl.to_list()
    print(f"  Inserted: {values}")
    print(f"  Sorted:   {sorted_vals}")
    assert sorted_vals == sorted(values), f"Expected {sorted(values)}, got {sorted_vals}"
    assert sl.search(5) == True
    assert sl.search(7) == False
    sl.delete(5)
    # One 5 removed; another 5 still present
    assert sl.search(5) == True
    sl.delete(5)
    assert sl.search(5) == False
    print("  Skip List: all assertions passed.")

    print("\n" + "=" * 60)
    print("All problems completed successfully.")
    print("=" * 60)
