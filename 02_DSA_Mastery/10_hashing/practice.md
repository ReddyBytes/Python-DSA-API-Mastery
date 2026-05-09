# 💻 Hashing — Practice

> 25 questions covering hash function concepts, Python dict/set internals, collision resolution, classic patterns, and design from scratch.

---

## Quick Index

| # | Difficulty | Topic |
|---|---|---|
| [Q1](#q1) | 🟢 Basic | What does a hash function do |
| [Q2](#q2) | 🟢 Basic | Why dict lookup is O(1) average |
| [Q3](#q3) | 🟢 Basic | O(1) average vs O(n) worst case |
| [Q4](#q4) | 🟢 Basic | Hashability rules — what can be a key |
| [Q5](#q5) | 🟢 Basic | Frequency counting with a dict |
| [Q6](#q6) | 🟢 Basic | Set membership beats list lookup |
| [Q7](#q7) | 🟢 Basic | Seen-set pattern — duplicate detection |
| [Q8](#q8) | 🟢 Basic | Complement lookup — two sum |
| [Q9](#q9) | 🟡 Intermediate | Chaining vs open addressing |
| [Q10](#q10) | 🟡 Intermediate | Load factor and resizing |
| [Q11](#q11) | 🟡 Intermediate | Python dict internals — open addressing |
| [Q12](#q12) | 🟡 Intermediate | Python set operations — union/intersection/difference |
| [Q13](#q13) | 🟡 Intermediate | frozenset as dict key |
| [Q14](#q14) | 🟡 Intermediate | Anagram grouping |
| [Q15](#q15) | 🟡 Intermediate | Character mapping — isomorphic strings |
| [Q16](#q16) | 🟡 Intermediate | Subarray sum equals K — prefix + hash pattern |
| [Q17](#q17) | 🟡 Intermediate | Longest consecutive sequence |
| [Q18](#q18) | 🟡 Intermediate | Top-K frequent elements |
| [Q19](#q19) | 🟡 Intermediate | Two arrays — intersection and union |
| [Q20](#q20) | 🟡 Intermediate | Word frequency from text |
| [Q21](#q21) | 🔴 Advanced | Design hashmap from scratch |
| [Q22](#q22) | 🔴 Advanced | Design hashset from scratch |
| [Q23](#q23) | 🔴 Advanced | LRU cache — hashmap + doubly linked list |
| [Q24](#q24) | 🔴 Advanced | Consistent hashing concept |
| [Q25](#q25) | 🔴 Advanced | Hash table vulnerability — adversarial inputs |

---

<a id="q1"></a>
### Q1 🟢 · What does a hash function do

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)



**Problem:** Implement a simple hash function `simple_hash(key: str, table_size: int) -> int` that sums the ASCII values of each character and takes the result modulo `table_size`. Test it on `"apple"`, `"banana"`, and `"abc"` with `table_size=10`.

<details>
<summary>💡 Hint</summary>

Use `ord(char)` to get the ASCII value of a character. Sum all values, then apply `% table_size`. The result must always be in range `[0, table_size - 1]`.
</details>

<details>
<summary>✅ Answer</summary>

```python
def simple_hash(key: str, table_size: int) -> int:
    return sum(ord(ch) for ch in key) % table_size

print(simple_hash("apple", 10))   # 530 % 10 = 0
print(simple_hash("banana", 10))  # 609 % 10 = 9
print(simple_hash("abc", 10))     # 294 % 10 = 4
```

**Why:** A hash function must be deterministic (same input always gives same output) and bounded (output is a valid index). The modulo operation guarantees the index stays within the array bounds. This simple sum-of-ASCII approach has weaknesses (anagrams collide: `"abc"` and `"bca"` produce the same sum), but it illustrates the concept.

**Time:** O(k) where k = key length. **Space:** O(1).
</details>

---

<a id="q2"></a>
### Q2 🟢 · Why dict lookup is O(1) average

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)



**Problem:** Explain why `d["apple"]` is O(1) while scanning a list for `"apple"` is O(n). Then demonstrate the performance gap by timing a lookup in a `dict` vs a `list` at n=1,000,000.

<details>
<summary>💡 Hint</summary>

Use `time.time()` or `timeit`. For the dict, build `{str(i): i for i in range(n)}` and look up `str(999999)`. For the list, build `[str(i) for i in range(n)]` and use `in`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time

n = 1_000_000
d = {str(i): i for i in range(n)}
lst = [str(i) for i in range(n)]

t0 = time.perf_counter()
_ = d["999999"]
print(f"dict lookup:  {(time.perf_counter() - t0) * 1e6:.2f} μs")

t0 = time.perf_counter()
_ = "999999" in lst
print(f"list lookup:  {(time.perf_counter() - t0) * 1e6:.2f} μs")
```

**Why:** The dict computes `hash("999999")` to get an index directly — no scanning. The list must check every element from index 0 until it finds a match. For worst-case (last element), the list does 1,000,000 comparisons. The dict does approximately 1. This is the O(1) vs O(n) gap in practice.

**Time:** dict O(1) average, list O(n). **Space:** O(n) for both structures.
</details>

---

<a id="q3"></a>
### Q3 🟢 · O(1) average vs O(n) worst case

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)



**Problem:** Implement a class `BadHashClass` where every instance returns the same hash value (`42`), then insert 5 instances into a dict. Explain why this degrades performance and what the worst-case lookup time becomes.

<details>
<summary>💡 Hint</summary>

Override `__hash__` to always return `42` and `__eq__` to use object identity. When all keys hash to the same slot, the dict must probe through all of them on every lookup.
</details>

<details>
<summary>✅ Answer</summary>

```python
class BadHashClass:
    def __hash__(self):
        return 42  # every instance collides into the same slot

    def __eq__(self, other):
        return self is other

d = {}
keys = [BadHashClass() for _ in range(5)]
for i, k in enumerate(keys):
    d[k] = i

# All 5 keys collide at hash 42 — lookup must walk all 5 probes
print(len(d))  # 5 — they are distinct objects, so all 5 are stored
```

**Why:** With all keys hashing to the same bucket, the dict behaves like a linked list at that slot. Lookup must compare each stored key against the target. For n items all colliding, lookup is O(n). This is the theoretical worst case. Real hash functions use randomization (SipHash in CPython) to prevent adversarial inputs from triggering this.

**Time:** O(n) worst case with all collisions. **Space:** O(n).
</details>

---

<a id="q4"></a>
### Q4 🟢 · Hashability rules — what can be a key

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)



**Problem:** For each of the following, say whether it can be used as a dict key and why: `"hello"`, `42`, `3.14`, `(1, 2)`, `[1, 2]`, `{1, 2}`, `frozenset([1, 2])`, `{"a": 1}`. Then demonstrate the two common fixes when you have a list you want to use as a key.

<details>
<summary>💡 Hint</summary>

An object is hashable if it has a `__hash__` method that returns a consistent integer AND its value cannot change. Mutable containers (list, dict, set) are not hashable. Immutable containers (tuple, frozenset) are hashable if their contents are also hashable.
</details>

<details>
<summary>✅ Answer</summary>

```python
d = {}
d["hello"] = 1       # str — hashable (immutable)
d[42] = 2            # int — hashable
d[3.14] = 3          # float — hashable (but avoid as key due to precision)
d[(1, 2)] = 4        # tuple — hashable (immutable, elements are hashable)
d[frozenset([1,2])] = 5  # frozenset — hashable

# These raise TypeError: unhashable type
try:
    d[[1, 2]] = "list key"
except TypeError as e:
    print(e)  # unhashable type: 'list'

# Fix 1: convert to tuple (preserves order)
key = tuple([1, 2])
d[key] = "tuple key"

# Fix 2: convert to frozenset (order-independent)
key = frozenset([1, 2])
d[key] = "frozenset key"
```

**Why:** Python's dict requires `hash(key)` to be stable. If a list could change after insertion, its hash would change and the dict would lose the entry. Immutability is the contract that makes hashing safe. `tuple` and `frozenset` are the standard conversions.

**Time:** O(k) to hash a key of length k. **Space:** O(1) per key.
</details>

---

<a id="q5"></a>
### Q5 🟢 · Frequency counting with a dict

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)



**Problem:** Implement `char_frequency(s: str) -> dict` three ways: (1) using plain dict with `.get(k, 0)`, (2) using `defaultdict(int)`, (3) using `Counter`. Test all three on `"mississippi"` and confirm identical output.

<details>
<summary>💡 Hint</summary>

For approach 1: `counts[ch] = counts.get(ch, 0) + 1`. For approach 2: `counts[ch] += 1` with no pre-init needed. For approach 3: `Counter(s)` does it all in one call.
</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import defaultdict, Counter

def freq_plain(s: str) -> dict:
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    return counts

def freq_defaultdict(s: str) -> dict:
    counts = defaultdict(int)
    for ch in s:
        counts[ch] += 1
    return dict(counts)

def freq_counter(s: str) -> dict:
    return dict(Counter(s))

s = "mississippi"
print(freq_plain(s))       # {'m':1,'i':4,'s':4,'p':2}
print(freq_defaultdict(s)) # same
print(freq_counter(s))     # same
```

**Why:** All three are O(n) time. `Counter` is the most Pythonic for counting. `defaultdict(int)` is cleaner than `.get(k, 0)` when writing incremental loops. Never do `counts[k] += 1` on a plain dict without initializing first — it raises `KeyError`.

**Time:** O(n). **Space:** O(k) where k = number of unique characters.
</details>

---

<a id="q6"></a>
### Q6 🟢 · Set membership beats list lookup

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)



**Problem:** Write a function `filter_seen(items: list, banned: list) -> list` that returns only items not in `banned`. Implement it two ways: (A) using `if item not in banned` (list scan), (B) converting `banned` to a set first. Explain the complexity difference for n items and m banned words.

<details>
<summary>💡 Hint</summary>

`x in list` is O(len(list)) per check. `x in set` is O(1) per check. If you call this n times with m banned items, list approach is O(n*m), set approach is O(n+m).
</details>

<details>
<summary>✅ Answer</summary>

```python
def filter_seen_list(items: list, banned: list) -> list:
    return [x for x in items if x not in banned]  # O(n*m)

def filter_seen_set(items: list, banned: list) -> list:
    banned_set = set(banned)                       # O(m) one-time cost
    return [x for x in items if x not in banned_set]  # O(n)

items = list(range(10000))
banned = list(range(5000))

print(len(filter_seen_list(items, banned)))  # 5000
print(len(filter_seen_set(items, banned)))   # 5000
```

**Why:** Each `in` check on a list walks up to m elements. For n items, that's O(n*m). Converting to a set costs O(m) once, then each check is O(1), giving O(n+m) total — much faster when m is large. This is the single most common performance fix in Python code reviews.

**Time:** list O(n*m), set O(n+m). **Space:** O(m) for the set.
</details>

---

<a id="q7"></a>
### Q7 🟢 · Seen-set pattern — duplicate detection

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)



**Problem:** Implement `has_duplicate(nums: list[int]) -> bool` using a seen-set pattern. Then implement `first_duplicate(nums: list[int]) -> int | None` that returns the first element that appears more than once (in order of second occurrence). Return `None` if no duplicates exist.

<details>
<summary>💡 Hint</summary>

For `has_duplicate`: add each number to a set; if it's already there, return `True`. For `first_duplicate`: same pattern but return the number when you detect the second occurrence.
</details>

<details>
<summary>✅ Answer</summary>

```python
def has_duplicate(nums: list) -> bool:
    seen = set()
    for n in nums:
        if n in seen:
            return True
        seen.add(n)
    return False

def first_duplicate(nums: list):
    seen = set()
    for n in nums:
        if n in seen:
            return n
        seen.add(n)
    return None

print(has_duplicate([1, 2, 3, 4]))       # False
print(has_duplicate([1, 2, 3, 1]))       # True
print(first_duplicate([4, 3, 2, 4, 1]))  # 4
print(first_duplicate([1, 2, 3]))        # None
```

**Why:** The seen-set is the standard O(n) duplicate detection pattern. You build the set incrementally — each element is checked before being added, so the first repeat is caught immediately. The alternative (sorting) is O(n log n) and destroys original order.

**Time:** O(n). **Space:** O(n).
</details>

---

<a id="q8"></a>
### Q8 🟢 · Complement lookup — two sum

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)



**Problem:** Implement `two_sum(nums: list[int], target: int) -> list[int]` that returns `[i, j]` where `nums[i] + nums[j] == target` and `i != j`. Return `[]` if no solution exists. Must be O(n) — no nested loops. Edge case: `[3, 3]` with target `6` must return `[0, 1]`.

<details>
<summary>💡 Hint</summary>

Store `value → index` in a dict. For each element, check if `target - element` is already in the dict. Store the current element **after** the check — this prevents pairing an index with itself.
</details>

<details>
<summary>✅ Answer</summary>

```python
def two_sum(nums: list, target: int) -> list:
    seen = {}  # value -> index
    for i, n in enumerate(nums):
        complement = target - n
        if complement in seen:
            return [seen[complement], i]
        seen[n] = i  # store AFTER checking to prevent self-pairing
    return []

print(two_sum([2, 7, 11, 15], 9))   # [0, 1]
print(two_sum([3, 3], 6))           # [0, 1]
print(two_sum([1, 2, 3], 10))       # []
print(two_sum([3, 2, 4], 6))        # [1, 2]
```

**Why:** For each number, the complement `target - n` is the number we need. If it exists in `seen`, we have a valid pair. Storing the current index **after** the check is critical — it ensures we never return the same index twice. Without this ordering, `two_sum([3], 6)` would incorrectly pair index 0 with itself.

**Time:** O(n). **Space:** O(n).
</details>

---

<a id="q9"></a>
### Q9 🟡 · Chaining vs open addressing

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)



**Problem:** Implement a minimal hash table using **separate chaining**. The class `ChainedHashTable` should support `put(key, value)` and `get(key)` with a table size of 7. Then explain when chaining is preferred over open addressing and vice versa.

<details>
<summary>💡 Hint</summary>

Each slot in the array holds a list of `(key, value)` pairs. `put`: compute the index, scan the chain for an existing key to update, otherwise append. `get`: compute the index, scan the chain for the key.
</details>

<details>
<summary>✅ Answer</summary>

```python
class ChainedHashTable:
    def __init__(self, size: int = 7):
        self.size = size
        self.table = [[] for _ in range(size)]  # each slot = list of (key, val)

    def _index(self, key: str) -> int:
        return hash(key) % self.size

    def put(self, key: str, value) -> None:
        idx = self._index(key)
        for i, (k, v) in enumerate(self.table[idx]):
            if k == key:
                self.table[idx][i] = (key, value)  # update
                return
        self.table[idx].append((key, value))  # insert

    def get(self, key: str):
        idx = self._index(key)
        for k, v in self.table[idx]:
            if k == key:
                return v
        return None

ht = ChainedHashTable()
ht.put("apple", 10)
ht.put("banana", 20)
ht.put("apple", 99)   # update
print(ht.get("apple"))   # 99
print(ht.get("banana"))  # 20
print(ht.get("cherry"))  # None
```

**Why:** Chaining stores overflow in linked lists (or Python lists) at each bucket. It handles high load factors gracefully — the chain just grows. Open addressing stores everything in the array and probes for the next empty slot. Open addressing has better cache performance (data is contiguous) but degrades sharply at high load factors. Python's `dict` uses open addressing. Java's `HashMap` uses chaining.

**Time:** O(1) average, O(n) worst case for both. **Space:** O(n).
</details>

---

<a id="q10"></a>
### Q10 🟡 · Load factor and resizing

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)



**Problem:** Implement a `ResizingHashTable` that tracks its load factor and automatically doubles in size (and rehashes all entries) when load factor exceeds `0.7`. Support `put(key, value)` and `get(key)`. Print the table size before and after a resize.

<details>
<summary>💡 Hint</summary>

`load_factor = num_entries / table_size`. After inserting, check if load factor > 0.7. If so, create a new table of double the size and re-insert all existing entries using their new hash indices.
</details>

<details>
<summary>✅ Answer</summary>

```python
class ResizingHashTable:
    def __init__(self, size: int = 4):
        self.size = size
        self.count = 0
        self.table = [[] for _ in range(size)]

    def _index(self, key: str) -> int:
        return hash(key) % self.size

    def put(self, key: str, value) -> None:
        idx = self._index(key)
        for i, (k, v) in enumerate(self.table[idx]):
            if k == key:
                self.table[idx][i] = (key, value)
                return
        self.table[idx].append((key, value))
        self.count += 1
        if self.count / self.size > 0.7:
            self._resize()

    def _resize(self) -> None:
        old_table = self.table
        self.size *= 2
        self.table = [[] for _ in range(self.size)]
        self.count = 0
        print(f"Resizing to {self.size}")
        for bucket in old_table:
            for k, v in bucket:
                self.put(k, v)

    def get(self, key: str):
        for k, v in self.table[self._index(key)]:
            if k == key:
                return v
        return None

ht = ResizingHashTable(size=4)
for i in range(6):
    ht.put(f"key{i}", i)   # resize triggers when count/size > 0.7
```

**Why:** Without resizing, as more entries are added, collision chains grow and all operations degrade toward O(n). Doubling the table size keeps the load factor below threshold, maintaining O(1) average performance. The resize itself is O(n) — expensive once — but happens at most O(log n) times total, making individual insertions amortized O(1).

**Time:** O(1) amortized per insertion. **Space:** O(n).
</details>

---

<a id="q11"></a>
### Q11 🟡 · Python dict internals — open addressing

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)



**Problem:** Demonstrate three key behaviors of Python's dict implementation: (1) integer keys hash to themselves, (2) string keys use randomized SipHash (different per process), (3) dict preserves insertion order since Python 3.7. Also show that `{1: "a", 2: "b"} == {2: "b", 1: "a"}` is `True` — equality ignores order.

<details>
<summary>💡 Hint</summary>

Use `hash(1)`, `hash("hello")`, and build a dict with multiple keys inserted in a specific order, then iterate to confirm order is preserved. For equality, compare two dicts with same key-value pairs in different insertion order.
</details>

<details>
<summary>✅ Answer</summary>

```python
# 1. Integer keys hash to themselves
print(hash(0), hash(1), hash(42))   # 0, 1, 42

# 2. Strings use SipHash — randomized per process (PYTHONHASHSEED)
print(hash("hello"))  # changes every Python process run
print(hash("hello"))  # same within one process run

# 3. Insertion order preserved (Python 3.7+)
d = {}
d["first"] = 1
d["second"] = 2
d["third"] = 3
print(list(d.keys()))  # ['first', 'second', 'third'] — always in this order

# 4. Equality ignores insertion order
print({1: "a", 2: "b"} == {2: "b", 1: "a"})  # True

# 5. dict resizes at 2/3 load factor
import sys
d = {}
for i in range(20):
    d[i] = i
# dict grows in powers of 2 internally (8, 16, 32, ...)
```

**Why:** Python dicts use open addressing with pseudo-random probing (based on the hash value, not just +1). SipHash randomization was introduced in Python 3.3 to prevent hash-flooding DoS attacks. Insertion order preservation (Python 3.7+) is implemented via a compact indices array plus a separate dense entries array — the indices are scrambled for fast lookup, while the entries array preserves order.

**Time:** O(1) average for all operations. **Space:** O(n).
</details>

---

<a id="q12"></a>
### Q12 🟡 · Python set operations — union/intersection/difference

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)



**Problem:** Given two sets `a = {1, 2, 3, 4, 5}` and `b = {3, 4, 5, 6, 7}`, compute: (1) union, (2) intersection, (3) difference a-b, (4) symmetric difference. For each, state the time complexity. Then write `common_elements(list1, list2) -> list` using set intersection, and explain why it beats a nested loop.

<details>
<summary>💡 Hint</summary>

Use `|`, `&`, `-`, `^` operators or `.union()`, `.intersection()`, `.difference()`, `.symmetric_difference()` methods. Intersection is O(min(len(a), len(b))). The function `common_elements` should convert both lists to sets, intersect, and return a sorted list.
</details>

<details>
<summary>✅ Answer</summary>

```python
a = {1, 2, 3, 4, 5}
b = {3, 4, 5, 6, 7}

print(a | b)    # union:              {1,2,3,4,5,6,7}   O(len(a)+len(b))
print(a & b)    # intersection:       {3,4,5}            O(min(len(a),len(b)))
print(a - b)    # difference (a-b):   {1,2}              O(len(a))
print(a ^ b)    # symmetric diff:     {1,2,6,7}          O(len(a)+len(b))

def common_elements(list1: list, list2: list) -> list:
    return sorted(set(list1) & set(list2))

print(common_elements([1,2,3,4], [3,4,5,6]))  # [3, 4]
```

**Why:** A nested loop to find common elements is O(n*m). Converting to sets and intersecting is O(n+m) — build two sets O(n+m), then intersection scans the smaller set checking membership in the larger O(min(n,m)). The set `in` operator is O(1) average, making the total O(n+m) vs O(n*m) for the loop.

**Time:** O(n+m) for common_elements. **Space:** O(n+m).
</details>

---

<a id="q13"></a>
### Q13 🟡 · frozenset as dict key

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)



**Problem:** You have a list of undirected friendship pairs: `[("alice", "bob"), ("bob", "alice"), ("carol", "dave")]`. Using `frozenset` as a dict key, deduplicate this list so that `("alice", "bob")` and `("bob", "alice")` are treated as the same pair. Return the unique pairs as a list of sorted tuples.

<details>
<summary>💡 Hint</summary>

`frozenset(("alice", "bob")) == frozenset(("bob", "alice"))` is `True` — frozenset ignores order. Use a set of frozensets to deduplicate. To return sorted tuples, convert each frozenset back with `tuple(sorted(fs))`.
</details>

<details>
<summary>✅ Answer</summary>

```python
def unique_pairs(pairs: list) -> list:
    seen = set()
    for a, b in pairs:
        seen.add(frozenset((a, b)))
    return sorted(tuple(sorted(fs)) for fs in seen)

pairs = [("alice", "bob"), ("bob", "alice"), ("carol", "dave"), ("dave", "carol")]
print(unique_pairs(pairs))
# [('alice', 'bob'), ('carol', 'dave')]
```

**Why:** `frozenset` is an immutable, hashable set — perfect for representing unordered pairs as dict keys or set members. `frozenset({"alice", "bob"}) == frozenset({"bob", "alice"})` is `True`, so both orderings of the same pair hash to the same bucket. This is the canonical pattern for deduplicating bidirectional relationships.

**Time:** O(n) average. **Space:** O(n).
</details>

---

<a id="q14"></a>
### Q14 🟡 · Anagram grouping

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)



**Problem:** Implement `group_anagrams(words: list[str]) -> list[list[str]]` that groups words which are anagrams of each other. Input: `["eat","tea","tan","ate","nat","bat"]`. Expected: groups `["eat","tea","ate"]`, `["tan","nat"]`, `["bat"]` (order within group and order of groups can vary).

<details>
<summary>💡 Hint</summary>

Two words are anagrams if their sorted character sequences are identical. Use `tuple(sorted(word))` or `"".join(sorted(word))` as the grouping key. Use `defaultdict(list)` to accumulate groups.
</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import defaultdict

def group_anagrams(words: list) -> list:
    groups = defaultdict(list)
    for word in words:
        key = tuple(sorted(word))  # canonical form: ('a','e','t') for "eat","tea","ate"
        groups[key].append(word)
    return list(groups.values())

words = ["eat", "tea", "tan", "ate", "nat", "bat"]
result = group_anagrams(words)
for group in result:
    print(sorted(group))
# ['ate', 'eat', 'tea']
# ['nat', 'tan']
# ['bat']
```

**Why:** The canonical key idea — transform each word into a form where all anagrams produce the same key — is the core insight. `tuple(sorted(word))` works because sorting puts characters in the same order regardless of original arrangement. Using a tuple (not a list) as the key is essential — lists are not hashable. `defaultdict(list)` avoids KeyError on the first insertion to any group.

**Time:** O(n * k log k) where k = max word length. **Space:** O(n * k).
</details>

---

<a id="q15"></a>
### Q15 🟡 · Character mapping — isomorphic strings

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)



**Problem:** Implement `is_isomorphic(s: str, t: str) -> bool`. Two strings are isomorphic if characters in `s` can be replaced consistently to get `t`. Example: `"egg"` → `"add"` is `True` (e→a, g→d). `"foo"` → `"bar"` is `False` (o maps to both a and r).

<details>
<summary>💡 Hint</summary>

You need two dicts: one mapping `s → t` characters and one mapping `t → s` characters. Both mappings must be consistent. If `s[i]` already maps to a different `t[i]`, return False. If `t[i]` already maps from a different `s[i]`, return False.
</details>

<details>
<summary>✅ Answer</summary>

```python
def is_isomorphic(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    s_to_t = {}
    t_to_s = {}
    for cs, ct in zip(s, t):
        if cs in s_to_t and s_to_t[cs] != ct:
            return False   # s char maps to different t char
        if ct in t_to_s and t_to_s[ct] != cs:
            return False   # t char maps from different s char
        s_to_t[cs] = ct
        t_to_s[ct] = cs
    return True

print(is_isomorphic("egg", "add"))   # True
print(is_isomorphic("foo", "bar"))   # False
print(is_isomorphic("paper", "title"))  # True
print(is_isomorphic("ab", "aa"))     # False
```

**Why:** One dict alone is insufficient. With only `s→t`, the mapping `"ab"→"aa"` would pass (a→a, b→a) even though two distinct characters in s can't map to the same character in t. The reverse dict `t→s` enforces the one-to-one constraint. This bidirectional check is the standard character-mapping pattern.

**Time:** O(n). **Space:** O(1) — at most 26 entries for lowercase ASCII.
</details>

---

<a id="q16"></a>
### Q16 🟡 · Subarray sum equals K — prefix + hash pattern

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)



**Problem:** Implement `subarray_sum(nums: list[int], k: int) -> int` that returns the count of contiguous subarrays whose sum equals `k`. Example: `nums=[1,1,1], k=2` → `2`. Must be O(n).

<details>
<summary>💡 Hint</summary>

Compute a running `prefix_sum`. If `prefix_sum - k` has been seen before, there is a subarray ending at the current index with sum `k`. Store `{prefix_sum: frequency}` in a dict. Initialize with `{0: 1}` to handle subarrays starting from index 0.
</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import defaultdict

def subarray_sum(nums: list, k: int) -> int:
    count = 0
    prefix_sum = 0
    seen = defaultdict(int)
    seen[0] = 1  # empty prefix — handles subarrays starting at index 0

    for n in nums:
        prefix_sum += n
        count += seen[prefix_sum - k]  # subarrays ending here with sum k
        seen[prefix_sum] += 1

    return count

print(subarray_sum([1, 1, 1], 2))       # 2 (indices [0,1] and [1,2])
print(subarray_sum([1, 2, 3], 3))       # 2 ([0,1] sums to 3, [2] alone)
print(subarray_sum([-1, -1, 1], 0))     # 1
```

**Why:** For a subarray `nums[i..j]` to sum to `k`, we need `prefix[j] - prefix[i-1] == k`, i.e., `prefix[i-1] == prefix[j] - k`. If we store all previously seen prefix sums in a dict, we can check this in O(1). The `seen[0] = 1` initialization handles the case where the subarray starts at index 0 (no prior prefix exists, so we pretend there's a zero-sum prefix before the array).

**Time:** O(n). **Space:** O(n).
</details>

---

<a id="q17"></a>
### Q17 🟡 · Longest consecutive sequence

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)



**Problem:** Implement `longest_consecutive(nums: list[int]) -> int` that returns the length of the longest consecutive sequence. Example: `[100,4,200,1,3,2]` → `4` (sequence 1,2,3,4). Must be O(n) — no sorting.

<details>
<summary>💡 Hint</summary>

Convert to a set. For each number, only start counting if `num - 1` is NOT in the set — this ensures you only start a sequence at its beginning, avoiding redundant counting. Then count forward (`num+1`, `num+2`, ...) while the next number is in the set.
</details>

<details>
<summary>✅ Answer</summary>

```python
def longest_consecutive(nums: list) -> int:
    num_set = set(nums)
    best = 0

    for n in num_set:
        if n - 1 not in num_set:  # n is the start of a sequence
            length = 1
            while n + length in num_set:
                length += 1
            best = max(best, length)

    return best

print(longest_consecutive([100, 4, 200, 1, 3, 2]))  # 4
print(longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]))  # 9
print(longest_consecutive([]))  # 0
```

**Why:** The key insight is to only begin counting from the start of a sequence (`n-1 not in set`). Without this guard, we'd restart counting from every element in a sequence, making the inner while loop run O(length) times per element and the total O(n^2). With the guard, each element is visited at most twice (once as an outer loop candidate, once inside a while loop) — making the total O(n).

**Time:** O(n). **Space:** O(n) for the set.
</details>

---

<a id="q18"></a>
### Q18 🟡 · Top-K frequent elements

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)



**Problem:** Implement `top_k_frequent(nums: list[int], k: int) -> list[int]` that returns the k most frequent elements. Example: `nums=[1,1,1,2,2,3], k=2` → `[1, 2]`. Two approaches: (A) `Counter.most_common(k)` one-liner, (B) bucket sort approach for O(n) time.

<details>
<summary>💡 Hint</summary>

For approach A: `Counter(nums).most_common(k)` returns `(value, count)` pairs. For approach B: bucket sort by frequency — create an array of length `n+1` where index = frequency, then collect from the end.
</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import Counter

# Approach A: Counter — O(n log k)
def top_k_frequent_counter(nums: list, k: int) -> list:
    return [val for val, _ in Counter(nums).most_common(k)]

# Approach B: Bucket sort — O(n)
def top_k_frequent_bucket(nums: list, k: int) -> list:
    freq = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for val, count in freq.items():
        buckets[count].append(val)

    result = []
    for count in range(len(buckets) - 1, 0, -1):  # scan high freq to low
        for val in buckets[count]:
            result.append(val)
            if len(result) == k:
                return result
    return result

nums = [1, 1, 1, 2, 2, 3]
print(top_k_frequent_counter(nums, 2))  # [1, 2]
print(top_k_frequent_bucket(nums, 2))   # [1, 2]
```

**Why:** `Counter.most_common(k)` uses a heap internally — O(n log k). The bucket sort approach is O(n): frequency is bounded by n (max n occurrences), so we can use a frequency array of size n+1 as buckets and scan from high to low frequency. This trades the log factor for a guaranteed O(n) at the cost of O(n) extra space.

**Time:** Counter O(n log k), bucket sort O(n). **Space:** O(n) both.
</details>

---

<a id="q19"></a>
### Q19 🟡 · Two arrays — intersection and union

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)



**Problem:** Implement `array_intersection(a, b)` returning unique elements present in both arrays, and `array_union(a, b)` returning unique elements present in either. Then implement `intersection_with_duplicates(a, b)` that counts intersections with multiplicity — if `3` appears twice in `a` and three times in `b`, return two `3`s. Use `Counter` for the last one.

<details>
<summary>💡 Hint</summary>

For unique intersection/union: use Python set operators `&` and `|`. For intersection with duplicates: `Counter(a) & Counter(b)` gives the min of each count — convert back with `list(result.elements())`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import Counter

def array_intersection(a: list, b: list) -> list:
    return sorted(set(a) & set(b))

def array_union(a: list, b: list) -> list:
    return sorted(set(a) | set(b))

def intersection_with_duplicates(a: list, b: list) -> list:
    ca, cb = Counter(a), Counter(b)
    return sorted((ca & cb).elements())  # min counts, expanded

a = [1, 2, 2, 3, 3, 3]
b = [2, 3, 3, 4]

print(array_intersection(a, b))         # [2, 3]
print(array_union(a, b))                # [1, 2, 3, 4]
print(intersection_with_duplicates(a, b))  # [2, 3, 3]  (2 once, 3 twice — min)
```

**Why:** Set operations handle unique intersection/union in O(n+m). For the multiplicity case, `Counter(a) & Counter(b)` computes `min(count_a[x], count_b[x])` for each element — this is the "bag intersection". `.elements()` expands a Counter back to a list with each element repeated count times. This is the standard pattern for intersection-with-multiplicity problems.

**Time:** O(n+m). **Space:** O(n+m).
</details>

---

<a id="q20"></a>
### Q20 🟡 · Word frequency from text

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)



**Problem:** Implement `word_frequency(text: str) -> dict` that returns a frequency map of words (case-insensitive, punctuation stripped). Then use it to find the top 3 most common words in: `"To be or not to be, that is the question. To be is to exist."`. Ignore words in `stop_words = {"to", "be", "or", "not", "is", "that", "the"}`.

<details>
<summary>💡 Hint</summary>

Use `re.findall(r'[a-z]+', text.lower())` to extract clean words. Filter out stop words. Use `Counter.most_common(3)` for the top 3.
</details>

<details>
<summary>✅ Answer</summary>

```python
import re
from collections import Counter

def word_frequency(text: str) -> dict:
    words = re.findall(r'[a-z]+', text.lower())
    return dict(Counter(words))

def top_words(text: str, stop_words: set, k: int = 3) -> list:
    words = re.findall(r'[a-z]+', text.lower())
    filtered = [w for w in words if w not in stop_words]
    return [word for word, _ in Counter(filtered).most_common(k)]

text = "To be or not to be, that is the question. To be is to exist."
stop_words = {"to", "be", "or", "not", "is", "that", "the"}
print(top_words(text, stop_words, 3))  # ['question', 'exist'] (and others)
```

**Why:** `Counter` is designed for this pattern — it counts occurrences in O(n) and provides `.most_common(k)` in O(n log k). The set lookup for stop words is O(1) per word. This is the standard text-processing pipeline: tokenize → filter → count → rank. Real production systems (Elasticsearch, Lucene) follow the same conceptual pipeline with more sophisticated tokenizers.

**Time:** O(n log k). **Space:** O(n).
</details>

---

<a id="q21"></a>
### Q21 🔴 · Design hashmap from scratch

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)



**Problem:** Design a `HashMap` class supporting `put(key, value)`, `get(key) -> value | -1`, and `remove(key)`. Use separate chaining for collision resolution. Do not use Python's built-in dict or any hashing library. Use a fixed array of 1000 buckets.

<details>
<summary>💡 Hint</summary>

Use `hash(key) % 1000` as the index. Each bucket is a list of `[key, value]` pairs. For `put`: scan the chain for an existing key, update in place, or append a new pair. For `remove`: scan and pop from the chain. For `get`: scan and return the value or `-1`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class HashMap:
    def __init__(self):
        self.size = 1000
        self.buckets = [[] for _ in range(self.size)]

    def _bucket(self, key) -> int:
        return hash(key) % self.size

    def put(self, key, value) -> None:
        idx = self._bucket(key)
        for pair in self.buckets[idx]:
            if pair[0] == key:
                pair[1] = value
                return
        self.buckets[idx].append([key, value])

    def get(self, key) -> int:
        idx = self._bucket(key)
        for k, v in self.buckets[idx]:
            if k == key:
                return v
        return -1

    def remove(self, key) -> None:
        idx = self._bucket(key)
        self.buckets[idx] = [[k, v] for k, v in self.buckets[idx] if k != key]

hm = HashMap()
hm.put("apple", 1)
hm.put("banana", 2)
hm.put("apple", 99)    # update
print(hm.get("apple"))   # 99
print(hm.get("cherry"))  # -1
hm.remove("banana")
print(hm.get("banana"))  # -1
```

**Why:** This is a classic LeetCode design question (LeetCode 706). The key decisions are: (1) fixed array size for the index array, (2) chaining for collision resolution (simplest to implement correctly), (3) using mutable lists `[k, v]` so updates can be done in place without rebuilding the chain. In-place update is important — appending a new pair without checking for existing keys would cause duplicate keys in the same chain.

**Time:** O(n/k) average per operation where k=bucket count, O(n) worst case. **Space:** O(n).
</details>

---

<a id="q22"></a>
### Q22 🔴 · Design hashset from scratch

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)



**Problem:** Design a `HashSet` class supporting `add(key)`, `remove(key)`, and `contains(key) -> bool`. Use a fixed array of 1000 buckets with separate chaining. Do not use Python's built-in set.

<details>
<summary>💡 Hint</summary>

Similar to HashMap but each bucket stores a list of keys (no values). `add`: check if key already in chain before appending. `remove`: rebuild chain excluding the key. `contains`: scan the chain and return True/False.
</details>

<details>
<summary>✅ Answer</summary>

```python
class HashSet:
    def __init__(self):
        self.size = 1000
        self.buckets = [[] for _ in range(self.size)]

    def _bucket(self, key) -> int:
        return hash(key) % self.size

    def add(self, key) -> None:
        idx = self._bucket(key)
        if key not in self.buckets[idx]:  # avoid duplicates
            self.buckets[idx].append(key)

    def remove(self, key) -> None:
        idx = self._bucket(key)
        if key in self.buckets[idx]:
            self.buckets[idx].remove(key)

    def contains(self, key) -> bool:
        idx = self._bucket(key)
        return key in self.buckets[idx]

hs = HashSet()
hs.add(1)
hs.add(2)
hs.add(1)           # duplicate — no effect
print(hs.contains(1))   # True
print(hs.contains(3))   # False
hs.remove(2)
print(hs.contains(2))   # False
```

**Why:** A HashSet is a HashMap with no values — just key presence. The deduplication check on `add` (`if key not in bucket`) is critical: without it, the same key could appear multiple times in a chain, breaking the set semantics. This is LeetCode 705. The internal `in` check on a list is O(chain_length) — acceptable since chain lengths are short under low load factor.

**Time:** O(n/k) average, O(n) worst case. **Space:** O(n).
</details>

---

<a id="q23"></a>
### Q23 🔴 · LRU cache — hashmap + doubly linked list

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)



**Problem:** Design an `LRUCache` with `get(key) -> int` and `put(key, value)`. Both operations must be O(1). When the cache is full, evict the least recently used item. Test with capacity=2: put(1,1), put(2,2), get(1)→1, put(3,3) (evicts key 2), get(2)→-1, get(3)→3.

<details>
<summary>💡 Hint</summary>

Use a dict for O(1) lookup and a doubly linked list for O(1) eviction. The dict maps `key → node`. The linked list keeps items ordered by recency (most recent at head, least recent at tail). On `get`: move the node to head. On `put`: add to head, evict from tail if over capacity.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Node:
    def __init__(self, key=0, val=0):
        self.key = key
        self.val = val
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.cache = {}  # key -> Node
        # Sentinel head and tail (dummy nodes — simplify edge cases)
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_at_head(self, node: Node) -> None:
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._insert_at_head(node)  # mark as recently used
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self._remove(self.cache[key])
        node = Node(key, value)
        self.cache[key] = node
        self._insert_at_head(node)
        if len(self.cache) > self.cap:
            lru = self.tail.prev          # least recently used
            self._remove(lru)
            del self.cache[lru.key]

cache = LRUCache(2)
cache.put(1, 1)
cache.put(2, 2)
print(cache.get(1))    # 1 (moves key 1 to head)
cache.put(3, 3)        # evicts key 2 (LRU)
print(cache.get(2))    # -1 (evicted)
print(cache.get(3))    # 3
```

**Why:** The dict alone gives O(1) lookup but O(n) eviction (you'd have to scan for the LRU). The linked list alone gives O(1) eviction but O(n) lookup. Together they give O(1) for both: dict → find the node in O(1), linked list → reorder or evict in O(1). Dummy head/tail sentinels eliminate edge case checks for empty list or single-element operations. This is LeetCode 146 — a canonical system design + data structures problem.

**Time:** O(1) for both get and put. **Space:** O(capacity).
</details>

---

<a id="q24"></a>
### Q24 🔴 · Consistent hashing concept

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)



**Problem:** Explain why `server = hash(key) % N` fails when a server is added or removed from a cluster. Then implement a minimal `ConsistentHashRing` with `add_server(name)`, `remove_server(name)`, and `get_server(key)` that minimizes key remapping when the cluster changes.

<details>
<summary>💡 Hint</summary>

With `% N`: adding one server changes N, causing most keys to remap (cache stampede). In a consistent hash ring, servers and keys are placed on a circle. Each key maps to the first server clockwise. Adding/removing a server only affects keys in one arc (~1/N of all keys). Use `bisect` for the binary search on sorted ring positions.
</details>

<details>
<summary>✅ Answer</summary>

```python
import hashlib
import bisect

class ConsistentHashRing:
    def __init__(self, replicas: int = 50):
        self.replicas = replicas
        self.ring = {}          # hash_position -> server_name
        self.sorted_positions = []

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_server(self, name: str) -> None:
        for i in range(self.replicas):
            pos = self._hash(f"{name}:{i}")
            self.ring[pos] = name
            bisect.insort(self.sorted_positions, pos)

    def remove_server(self, name: str) -> None:
        for i in range(self.replicas):
            pos = self._hash(f"{name}:{i}")
            del self.ring[pos]
            self.sorted_positions.remove(pos)

    def get_server(self, key: str) -> str | None:
        if not self.ring:
            return None
        pos = self._hash(key)
        idx = bisect.bisect(self.sorted_positions, pos) % len(self.sorted_positions)
        return self.ring[self.sorted_positions[idx]]

ring = ConsistentHashRing()
ring.add_server("cache-1")
ring.add_server("cache-2")
ring.add_server("cache-3")
print(ring.get_server("user:1001"))    # deterministic server
ring.add_server("cache-4")             # only ~25% of keys remap
print(ring.get_server("user:1001"))    # may or may not change
```

**Why:** With `% N`: adding server 4 changes N from 3 to 4, remapping ~75% of keys in one instant — all those cache misses hit the database simultaneously (cache stampede). Consistent hashing places each server at multiple ring positions (virtual nodes via `replicas`). When adding server 4, only keys in the arcs adjacent to its positions remap (~1/N ≈ 25%). Virtual nodes also improve load distribution by spreading each server across the ring. Used in DynamoDB, Cassandra, Memcached, Nginx upstream.

**Time:** O(log n) per get_server (binary search). **Space:** O(servers * replicas).
</details>

---

<a id="q25"></a>
### Q25 🔴 · Hash table vulnerability — adversarial inputs

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)



**Problem:** Explain the hash-flooding DoS attack: how an attacker can craft inputs that all hash to the same bucket, degrading O(1) to O(n) lookups. Then explain how Python 3.3+ defends against it. Demonstrate that Python's `hash()` for strings is different across processes, and show how to create a stable hash for use cases like database sharding.

<details>
<summary>💡 Hint</summary>

Python randomizes string hashing using a secret seed (`PYTHONHASHSEED`) set at process start. To get a consistent/stable hash (same across processes), use `hashlib.md5()` or `hashlib.sha256()`. For an integer key space, xxhash or fnv32 are common choices.
</details>

<details>
<summary>✅ Answer</summary>

```python
import hashlib
import os

# Python's hash() — randomized per process (PYTHONHASHSEED)
# Run this script twice: you'll get different values each time
print(f"hash('hello') in this process: {hash('hello')}")

# Hash flooding: an attacker who knows the hash seed could generate
# thousands of strings that all map to the same bucket, turning all
# O(1) dict operations into O(n) — a DoS attack against web servers.
# Python 3.3 introduced random hash seeds to prevent this.

# For stable/reproducible hashing (database sharding, caching):
def stable_hash(key: str, buckets: int = 1000) -> int:
    """Same output across all processes and runs."""
    digest = hashlib.md5(key.encode()).hexdigest()
    return int(digest, 16) % buckets

print(stable_hash("user:1001"))  # always the same number

# Verify stability
assert stable_hash("user:1001") == stable_hash("user:1001")
assert stable_hash("user:1001", 10) != stable_hash("user:1001", 11)

# Python's defense: PYTHONHASHSEED randomization
# You can disable it for reproducibility in tests:
# PYTHONHASHSEED=0 python script.py
print(f"PYTHONHASHSEED env: {os.environ.get('PYTHONHASHSEED', 'random')}")
```

**Why:** Hash flooding exploits the fact that a server processes untrusted user input as dict keys. If the hash function is deterministic and public, an attacker generates many keys with the same hash, turning every dict lookup for those keys from O(1) to O(n). In 2011, this was used to DoS PHP, Java, and Python web servers. Python 3.3 fixed it with `PYTHONHASHSEED` — a per-process random seed that makes it impossible to predict hash values from outside. The tradeoff: `hash("x")` is no longer stable across restarts, so you cannot use it for persistent storage, database routing, or cache sharding — use `hashlib.md5` or `xxhash` instead.

**Time:** O(k) for stable_hash where k = key length. **Space:** O(1).
</details>

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Interview Q&A](./interview.md) &nbsp;|&nbsp; **Next:** [Two Pointers — Theory →](../11_two_pointers/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheetsheet.md) · [Collision Handling](./collision_handling.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
