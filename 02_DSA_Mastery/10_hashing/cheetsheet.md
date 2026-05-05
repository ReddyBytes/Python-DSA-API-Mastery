## HASHING — QUICK REFERENCE CHEATSHEET

```
┌───────────────────────────────────────────────────────────────────────┐
│  Core trade-off: O(n) extra space → O(1) average lookup/insert/delete │
└───────────────────────────────────────────────────────────────────────┘
```

---

## COMPLEXITY TABLE

```
┌──────────────────┬───────────────┬───────────────┬──────────────────┐
│ Operation        │ dict/set avg  │ dict/set worst │ Notes            │
├──────────────────┼───────────────┼───────────────┼──────────────────┤
│ Insert           │ O(1)          │ O(n)           │ worst=hash colls │
│ Delete           │ O(1)          │ O(n)           │                  │
│ Lookup           │ O(1)          │ O(n)           │                  │
│ Iteration        │ O(n)          │ O(n)           │ dicts keep order │
│ Space            │ O(n)          │ O(n)           │ (Python 3.7+)    │
└──────────────────┴───────────────┴───────────────┴──────────────────┘
```

---

## PYTHON DICT QUICK REFERENCE

```python
d = {}
d[key] = val                       # insert / update
d.get(key, default)                # safe get — no KeyError
d.setdefault(key, []).append(v)    # insert default if key missing, then use
key in d                           # O(1) membership
del d[key]                         # raises KeyError if missing
d.pop(key, None)                   # safe delete — returns None if missing
d.items()                          # (key, val) pairs
d.keys(), d.values()               # views — O(1) memory
len(d)                             # O(1)
```

---

## PYTHON SET OPERATIONS

```python
a = {1, 2, 3}
b = {2, 3, 4}

a | b            # union          {1,2,3,4}     O(len(a)+len(b))
a & b            # intersection   {2,3}         O(min(len(a),len(b)))
a - b            # difference     {1}           O(len(a))
a ^ b            # symmetric diff {1,4}         O(len(a)+len(b))

a.issubset(b)    # a <= b
a.issuperset(b)  # a >= b
a.isdisjoint(b)  # no common elements

s.add(x)         # O(1)
s.discard(x)     # O(1), no error if missing
s.remove(x)      # O(1), raises KeyError if missing
x in s           # O(1)
```

---

## COUNTER QUICK REFERENCE

```python
from collections import Counter

c = Counter("aabbbc")           # Counter({'b': 3, 'a': 2, 'c': 1})
c = Counter([1,1,2,3])
c[key]                          # 0 for missing keys (no KeyError)
c.most_common(k)                # top k (val, count) pairs — O(n log k)
c.most_common()                 # all, sorted by count desc

# Arithmetic
c1 + c2                         # sum counts (drops zero/negative)
c1 - c2                         # subtract, keep only positives
c1 & c2                         # min of each count (intersection)
c1 | c2                         # max of each count (union)

c.subtract(iterable)            # subtract in-place (keeps negatives)
sum(c.values())                 # total count
list(c.elements())              # expand: ['b','b','b','a','a','c']
```

---

## DEFAULTDICT PATTERNS

```python
from collections import defaultdict

# Group items
groups = defaultdict(list)
for key, val in pairs:
    groups[key].append(val)       # no KeyError on first access

# Count occurrences
freq = defaultdict(int)
for x in items:
    freq[x] += 1                  # no KeyError — default is 0

# Set-based grouping
groups = defaultdict(set)
for k, v in pairs:
    groups[k].add(v)

# Nested dict
nested = defaultdict(lambda: defaultdict(int))
nested['a']['b'] += 1
```

---

## KEY PATTERNS WITH TEMPLATES

### Two Sum with Hash Map
```python
def two_sum(nums, target):
    seen = {}                       # value → index
    for i, n in enumerate(nums):
        complement = target - n
        if complement in seen:
            return [seen[complement], i]
        seen[n] = i
    return []
# O(n) time, O(n) space
```

### Frequency Count with Counter
```python
def is_anagram(s, t):
    return Counter(s) == Counter(t)   # O(n)

def top_k_frequent(nums, k):
    return [v for v, _ in Counter(nums).most_common(k)]
```

### Group Anagrams
```python
def group_anagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        key = tuple(sorted(s))        # canonical key for anagram group
        # Alternative: key = ''.join(sorted(s))
        groups[key].append(s)
    return list(groups.values())
# O(n * k log k)  n=words, k=max word length
```

### Sliding Window + Hash Map
```python
def length_of_longest_substring(s):
    last_seen = {}
    left = max_len = 0
    for right, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= left:
            left = last_seen[ch] + 1   # shrink window past duplicate
        last_seen[ch] = right
        max_len = max(max_len, right - left + 1)
    return max_len
```

### Find Duplicate / Missing Number
```python
# Find duplicate using set
def find_duplicate(nums):
    seen = set()
    for n in nums:
        if n in seen: return n
        seen.add(n)

# Find missing using set difference
def missing_number(nums):
    return (set(range(len(nums) + 1)) - set(nums)).pop()

# Missing with XOR (O(1) space)
def missing_xor(nums):
    result = len(nums)
    for i, n in enumerate(nums):
        result ^= i ^ n
    return result
```

---

## GOTCHAS

```
TRAP 1: Mutable objects as keys
  Lists, dicts, sets CANNOT be dict keys or set elements — not hashable.
  Use tuples, strings, frozenset instead.
  BAD:  d[[1,2]] = val        ← TypeError: unhashable type: 'list'
  GOOD: d[(1,2)] = val        ← tuple is hashable

TRAP 2: Float keys are unreliable
  0.1 + 0.2 != 0.3 due to floating-point precision.
  Avoid floats as dict keys. Use round() or Fraction if needed.

TRAP 3: Modifying dict during iteration
  for k in d: del d[k]    ← RuntimeError
  for k in list(d.keys()): del d[k]    ← safe copy first

TRAP 4: Counter missing key returns 0 — not an error
  c = Counter(); c['x'] += 1    ← works fine (default = 0)

TRAP 5: defaultdict creates key on access
  if key in dd: ...    ← safe
  dd[key]              ← creates key with default value even if just reading
  Use dd.get(key) to read without creating.

TRAP 6: dict comparison ignores insertion order
  {1:1, 2:2} == {2:2, 1:1}  →  True  (order does not affect equality)
```

---

## FROZENSET — HASHABLE SET

```python
fs = frozenset([1, 2, 3])     # immutable set — can be used as dict key
d = {frozenset([1,2]): "pair"}

# Use case: group items where order doesn't matter
def group_pairs(pairs):
    groups = defaultdict(list)
    for a, b in pairs:
        groups[frozenset([a, b])].append((a, b))
```

---

## INTERVIEW MENTAL MODEL

```
Hash map trades:   O(n) space → O(1) lookup
Ask yourself:
  • "Have I seen X before?" → set
  • "How many times did X appear?" → Counter / defaultdict(int)
  • "What index/value was X at?" → dict
  • "Group items by shared property?" → defaultdict(list)
  • "Are two things equivalent?" → encode as hashable key, compare

Space optimization: sometimes XOR or math (Gauss sum) can replace hash map.
  Missing number:  n*(n+1)//2 - sum(nums)  → O(1) space
  Single number:   reduce(xor, nums)        → O(1) space
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Visual Explanation](./visual_explanation.md) &nbsp;|&nbsp; **Next:** [Collision Handling →](./collision_handling.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Collision Handling](./collision_handling.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
