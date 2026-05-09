# 💻 Practice — Segment Tree

## Quick Index

| Q# | Topic | Difficulty |
|---|---|---|
| [Q1](#q1) | Tree size allocation | 🟢 |
| [Q2](#q2) | Node index relationships | 🟢 |
| [Q3](#q3) | Build from array | 🟢 |
| [Q4](#q4) | Range sum query | 🟢 |
| [Q5](#q5) | Point update | 🟢 |
| [Q6](#q6) | Three overlap cases | 🟢 |
| [Q7](#q7) | Range minimum query | 🟡 |
| [Q8](#q8) | Range maximum query | 🟡 |
| [Q9](#q9) | Range GCD query | 🟡 |
| [Q10](#q10) | Segment tree vs prefix sum vs BIT | 🟡 |
| [Q11](#q11) | Fenwick tree point update and prefix sum | 🟡 |
| [Q12](#q12) | Fenwick range update with difference array | 🟡 |
| [Q13](#q13) | Wrong tree size crash | 🟡 |
| [Q14](#q14) | Indexing convention consistency | 🟡 |
| [Q15](#q15) | Lazy propagation range add and range sum | 🟠 |
| [Q16](#q16) | Push-down mechanics | 🟠 |
| [Q17](#q17) | Missing push-down bug | 🟠 |
| [Q18](#q18) | Interval merge queries | 🟠 |
| [Q19](#q19) | Non-associative merge function trap | 🟠 |
| [Q20](#q20) | Coordinate compression count in range | 🟠 |

---

<a id="q1"></a>
### Q1 · structure — Segment Tree Size Allocation

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


🟢 Basic

**Problem:** Given an array of size `n`, what is the safe allocation size for the segment tree array? Why is `2*n` not always enough? Give the formula and explain the worst case.

<details>
<summary>💡 Hint</summary>

Think about what happens when `n` is just above a power of 2. A tree of depth `k` can have up to `2^k` nodes at the bottom level. What is the worst-case total node count?

</details>

<details>
<summary>✅ Answer</summary>

```python
# Always allocate 4 * n for the segment tree array.

n = 5
tree = [0] * (4 * n)   # safe: 20 slots
# tree = [0] * (2 * n) # WRONG: only 10 slots — crashes for n=3, n=5, n=6 etc.

# Why 4*n?
# For n just above a power of 2 (e.g. n = 2^k + 1), the tree has depth k+1.
# The bottom level can hold up to 2^(k+1) = ~2*n nodes.
# Add the rest of the tree above it and you reach ~4*n nodes total.
#
# Worst-case examples:
#   n=3: tree needs 8 nodes  → 2*n=6 NOT enough, 4*n=12 safe
#   n=5: tree needs 16 nodes → 2*n=10 NOT enough, 4*n=20 safe
#   n=6: tree needs 16 nodes → 2*n=12 NOT enough, 4*n=24 safe
#
# Golden rule: always allocate 4*n, no exceptions.
```

**Why:** When `n` is not a power of 2, the tree structure pads to the next power of 2 at the leaf level. This means the tree array can reach indices up to `4*n`. Using `2*n` causes silent IndexErrors or wrong-memory writes on certain input sizes.

</details>

> 💻 Try it: [practice_local.py → Q1](./practice_local.py)

---

<a id="q2"></a>
### Q2 · structure — Tree Node Relationships

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


🟢 Basic

**Problem:** In a 1-indexed segment tree (root at index 1), what are the formulas for a node's left child, right child, and parent? Draw the index layout for a 4-element array.

<details>
<summary>💡 Hint</summary>

The elegance of 1-indexed layout is that children of node `i` live at exactly `2*i` and `2*i+1`. There is no offset needed.

</details>

<details>
<summary>✅ Answer</summary>

```python
# 1-indexed segment tree node relationships:
#   Left child  of node i  →  2 * i
#   Right child of node i  →  2 * i + 1
#   Parent      of node i  →  i // 2

# Index layout for arr = [a, b, c, d]  (n=4):
#
#  tree index:   0   1    2    3    4    5    6    7
#  meaning:    [_] [root] [L] [R] [LL] [LR] [RL] [RR]
#
#  Tree visual:
#               [1: sum(a,b,c,d)]
#              /                 \
#   [2: sum(a,b)]            [3: sum(c,d)]
#      /      \                 /        \
# [4: a]   [5: b]          [6: c]     [7: d]
#
# Index 0 is unused — that is intentional and correct in 1-indexed layout.

def children(i):
    return 2 * i, 2 * i + 1

def parent(i):
    return i // 2

print(children(1))  # (2, 3) — root's children
print(children(2))  # (4, 5) — left child's children
print(parent(4))    # 2
print(parent(1))    # 0 — parent of root is 0 (out of tree, ignore)
```

**Why:** The 1-indexed formula `2*i` / `2*i+1` is the most common convention because the math is clean and easy to remember. Index 0 is deliberately left empty. Mixing 1-indexed and 0-indexed formulas in the same implementation is one of the most common segment tree bugs.

</details>

> 💻 Try it: [practice_local.py → Q2](./practice_local.py)

---

<a id="q3"></a>
### Q3 · build — Build From Array

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


🟢 Basic

**Problem:** Implement `build(arr, tree, node, start, end)` that constructs a segment tree storing range sums. After building `arr = [1, 3, 5, 7, 9, 11]`, what is `tree[1]` (the root)?

<details>
<summary>💡 Hint</summary>

Leaf nodes store individual elements. Parent nodes store the sum of their two children. Build bottom-up recursively by splitting at `mid = (start + end) // 2`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def build(arr, tree, node, start, end):
    """Build segment tree. node=1 is root. All boundaries inclusive."""
    if start == end:
        # Leaf: store the element itself
        tree[node] = arr[start]
        return
    mid = (start + end) // 2
    build(arr, tree, 2 * node,     start, mid)       # build left half
    build(arr, tree, 2 * node + 1, mid + 1, end)     # build right half
    tree[node] = tree[2 * node] + tree[2 * node + 1] # parent = sum of children


arr = [1, 3, 5, 7, 9, 11]
n = len(arr)
tree = [0] * (4 * n)
build(arr, tree, 1, 0, n - 1)

print("Root (sum of all):", tree[1])   # 36
assert tree[1] == sum(arr)             # 36

# Build complexity: O(n) — each element visited exactly once
# Space: O(4n) for the tree array
```

**Why:** The build visits every node exactly once (there are `2n - 1` nodes in a complete binary tree). Each internal node does O(1) work (one addition), so the total build time is O(n), not O(n log n).

</details>

> 💻 Try it: [practice_local.py → Q3](./practice_local.py)

---

<a id="q4"></a>
### Q4 · query — Range Sum Query

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


🟢 Basic

**Problem:** Given a built segment tree for `arr = [1, 3, 5, 7, 9, 11]`, implement `query(l, r)` to return the sum of elements from index `l` to `r` (inclusive). What does `query(1, 4)` return?

<details>
<summary>💡 Hint</summary>

There are three cases at every node: no overlap (return 0), complete overlap (return node value directly), partial overlap (recurse both children and combine). The no-overlap identity for sum is 0.

</details>

<details>
<summary>✅ Answer</summary>

```python
def query(tree, node, start, end, l, r):
    """Return sum of arr[l..r]. All boundaries inclusive."""
    if r < start or end < l:
        return 0                         # no overlap — identity for sum is 0
    if l <= start and end <= r:
        return tree[node]                # complete overlap — use precomputed value
    # partial overlap — recurse both children and combine
    mid = (start + end) // 2
    left_sum  = query(tree, 2 * node,     start, mid,     l, r)
    right_sum = query(tree, 2 * node + 1, mid + 1, end,   l, r)
    return left_sum + right_sum


arr = [1, 3, 5, 7, 9, 11]
n = len(arr)
tree = [0] * (4 * n)

def build(arr, tree, node, start, end):
    if start == end:
        tree[node] = arr[start]
        return
    mid = (start + end) // 2
    build(arr, tree, 2*node, start, mid)
    build(arr, tree, 2*node+1, mid+1, end)
    tree[node] = tree[2*node] + tree[2*node+1]

build(arr, tree, 1, 0, n - 1)

print(query(tree, 1, 0, n-1, 1, 4))  # 3+5+7+9 = 24
assert query(tree, 1, 0, n-1, 1, 4) == 24
assert query(tree, 1, 0, n-1, 0, 5) == 36
assert query(tree, 1, 0, n-1, 2, 2) == 5   # single element
```

**Why:** Each query descends the tree and at each level either returns immediately (complete/no overlap) or splits into two. The height is O(log n), so the query touches at most O(4 log n) = O(log n) nodes. This is the key advantage over a brute-force O(n) loop.

</details>

> 💻 Try it: [practice_local.py → Q4](./practice_local.py)

---

<a id="q5"></a>
### Q5 · update — Point Update

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


🟢 Basic

**Problem:** After building a segment tree for `arr = [1, 3, 5, 7, 9, 11]`, implement `update(i, val)` that sets `arr[i] = val` and keeps the tree consistent. After `update(2, 10)`, what should `query(1, 4)` return?

<details>
<summary>💡 Hint</summary>

A point update traces a single root-to-leaf path. At the leaf, set the new value. On the way back up, recompute each parent as the sum of its two children.

</details>

<details>
<summary>✅ Answer</summary>

```python
def update(tree, node, start, end, idx, val):
    """Set arr[idx] = val and update all ancestor nodes."""
    if start == end:
        # Reached the leaf for this index
        tree[node] = val
        return
    mid = (start + end) // 2
    if idx <= mid:
        update(tree, 2 * node,     start, mid,     idx, val)
    else:
        update(tree, 2 * node + 1, mid + 1, end,   idx, val)
    # Recompute this node from updated children (post-order)
    tree[node] = tree[2 * node] + tree[2 * node + 1]


# Using arr = [1, 3, 5, 7, 9, 11]
# After update(2, 10): array becomes [1, 3, 10, 7, 9, 11]
# query(1, 4) = 3 + 10 + 7 + 9 = 29

arr = [1, 3, 5, 7, 9, 11]
n = len(arr)
tree = [0] * (4 * n)
# (build as in Q3, then:)
# update(tree, 1, 0, n-1, 2, 10)
# assert query(tree, 1, 0, n-1, 1, 4) == 29

# Time: O(log n) — traces one path from root to leaf
# Key: always recompute parent AFTER recursing into the correct child
```

**Why:** The update only touches nodes on the direct path from root to the changed leaf — that path has length O(log n). The tree stays consistent because each parent is recomputed after its child is updated (post-order recomputation).

</details>

> 💻 Try it: [practice_local.py → Q5](./practice_local.py)

---

<a id="q6"></a>
### Q6 · query — Three Overlap Cases

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


🟢 Basic

**Problem:** Explain and code the three cases that every segment tree query (or update) must handle. Use `arr = [4, 2, 7, 1]` with query range `[1, 3]` and trace through the recursion.

<details>
<summary>💡 Hint</summary>

Case 1: the node's segment and the query range don't touch at all. Case 2: the node's segment is fully inside the query range. Case 3: partial overlap — they partially intersect. Only case 3 requires recursion into both children.

</details>

<details>
<summary>✅ Answer</summary>

```python
# The three cases — every query/update follows this exact pattern:
#
# Case 1 — NO overlap:       [start, end] and [l, r] don't touch
#   Condition: r < start or end < l
#   Action:    return identity (0 for sum, inf for min, -inf for max)
#
# Case 2 — COMPLETE overlap: [start, end] is entirely inside [l, r]
#   Condition: l <= start and end <= r
#   Action:    return tree[node] directly (use the precomputed value)
#
# Case 3 — PARTIAL overlap:  [start, end] partially intersects [l, r]
#   Condition: everything else
#   Action:    recurse into BOTH children and combine results

# Trace: arr=[4,2,7,1], query sum [1, 3]
#
# Tree:
#        [0,3]: 14
#       /          \
#   [0,1]: 6      [2,3]: 8
#   /    \        /    \
# [0]: 4 [1]: 2 [2]: 7 [3]: 1
#
# query(node=1, start=0, end=3, l=1, r=3):
#   r < start? 3 < 0? No
#   end < l?   3 < 1? No
#   l<=start and end<=r? 1<=0? No  — PARTIAL OVERLAP
#   mid = 1
#   LEFT: query(node=2, start=0, end=1, l=1, r=3):
#     PARTIAL OVERLAP, mid=0
#     LEFT:  query(node=4, 0, 0): end < l? 0 < 1? YES — NO OVERLAP → return 0
#     RIGHT: query(node=5, 1, 1): COMPLETE OVERLAP → return 2
#     return 0 + 2 = 2
#   RIGHT: query(node=3, start=2, end=3, l=1, r=3):
#     l<=start and end<=r? 1<=2 and 3<=3? YES — COMPLETE OVERLAP → return 8
#   return 2 + 8 = 10  (arr[1]+arr[2]+arr[3] = 2+7+1 = 10)  correct
```

**Why:** The three-case pattern is the entire beating heart of segment trees. Cases 1 and 2 are the base cases that stop recursion. Case 3 is where the "divide" in divide-and-conquer happens. Skipping either child in case 3 is the partial-overlap bug — it silently drops elements from the result.

</details>

> 💻 Try it: [practice_local.py → Q6](./practice_local.py)

---

<a id="q7"></a>
### Q7 · query — Range Minimum Query

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


🟡 Intermediate

**Problem:** Adapt the segment tree template to support range minimum queries. For `arr = [4, 2, 7, 1, 9, 3, 8]`, what does `query_min(0, 6)` and `query_min(0, 2)` return? What changes compared to the sum template?

<details>
<summary>💡 Hint</summary>

Only two things change from the sum template: the identity element (what to return on no-overlap) and the merge operation. For minimum, identity is `float('inf')` and merge is `min()`.

</details>

<details>
<summary>✅ Answer</summary>

```python
class RangeMinSegTree:
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [float('inf')] * (4 * self.n)  # identity for min
        if self.n > 0:
            self._build(arr, 1, 0, self.n - 1)

    def _build(self, arr, node, start, end):
        if start == end:
            self.tree[node] = arr[start]
            return
        mid = (start + end) // 2
        self._build(arr, 2 * node,     start, mid)
        self._build(arr, 2 * node + 1, mid + 1, end)
        self.tree[node] = min(self.tree[2 * node], self.tree[2 * node + 1])  # min, not +

    def query(self, l, r, node=1, start=0, end=None):
        if end is None:
            end = self.n - 1
        if r < start or end < l:
            return float('inf')           # identity for min (not 0)
        if l <= start and end <= r:
            return self.tree[node]
        mid = (start + end) // 2
        return min(
            self.query(l, r, 2 * node,     start, mid),
            self.query(l, r, 2 * node + 1, mid + 1, end)
        )                                  # min, not +

    def update(self, i, val, node=1, start=0, end=None):
        if end is None:
            end = self.n - 1
        if start == end:
            self.tree[node] = val
            return
        mid = (start + end) // 2
        if i <= mid:
            self.update(i, val, 2 * node, start, mid)
        else:
            self.update(i, val, 2 * node + 1, mid + 1, end)
        self.tree[node] = min(self.tree[2 * node], self.tree[2 * node + 1])


arr = [4, 2, 7, 1, 9, 3, 8]
st = RangeMinSegTree(arr)
print(st.query(0, 6))  # 1  (global min)
print(st.query(0, 2))  # 2  (min of [4, 2, 7])
print(st.query(4, 6))  # 3  (min of [9, 3, 8])
```

**Why:** The segment tree template is completely generic — only the identity value and the merge function change. Sum, min, max, GCD, XOR all share identical structure. The key requirement is that the merge function must be **associative** — order of combining sub-results must not matter.

</details>

> 💻 Try it: [practice_local.py → Q7](./practice_local.py)

---

<a id="q8"></a>
### Q8 · query — Range Maximum Query

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


🟡 Intermediate

**Problem:** Implement range maximum query. For `arr = [4, 2, 7, 1, 9, 3, 8]`, after `update(4, 0)` (change the 9 to 0), what is the new `query_max(0, 6)`?

<details>
<summary>💡 Hint</summary>

Compared to range min, only two values flip: the identity element becomes `float('-inf')` and the merge becomes `max()`.

</details>

<details>
<summary>✅ Answer</summary>

```python
class RangeMaxSegTree:
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [float('-inf')] * (4 * self.n)  # identity for max
        if self.n > 0:
            self._build(arr, 1, 0, self.n - 1)

    def _build(self, arr, node, start, end):
        if start == end:
            self.tree[node] = arr[start]
            return
        mid = (start + end) // 2
        self._build(arr, 2 * node,     start, mid)
        self._build(arr, 2 * node + 1, mid + 1, end)
        self.tree[node] = max(self.tree[2 * node], self.tree[2 * node + 1])

    def query(self, l, r, node=1, start=0, end=None):
        if end is None:
            end = self.n - 1
        if r < start or end < l:
            return float('-inf')          # identity for max
        if l <= start and end <= r:
            return self.tree[node]
        mid = (start + end) // 2
        return max(
            self.query(l, r, 2 * node,     start, mid),
            self.query(l, r, 2 * node + 1, mid + 1, end)
        )

    def update(self, i, val, node=1, start=0, end=None):
        if end is None:
            end = self.n - 1
        if start == end:
            self.tree[node] = val
            return
        mid = (start + end) // 2
        if i <= mid:
            self.update(i, val, 2 * node, start, mid)
        else:
            self.update(i, val, 2 * node + 1, mid + 1, end)
        self.tree[node] = max(self.tree[2 * node], self.tree[2 * node + 1])


arr = [4, 2, 7, 1, 9, 3, 8]
st = RangeMaxSegTree(arr)
print(st.query(0, 6))  # 9
st.update(4, 0)        # change 9 to 0
print(st.query(0, 6))  # 8  (new max after removing 9)
print(st.query(0, 2))  # 7
```

**Why:** After the update, the path from the changed leaf (index 4) back to the root is recomputed. The root now reflects 8 (at index 6) as the new maximum. The point update is O(log n) because it only touches one root-to-leaf path.

</details>

> 💻 Try it: [practice_local.py → Q8](./practice_local.py)

---

<a id="q9"></a>
### Q9 · query — Range GCD Query

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


🟡 Intermediate

**Problem:** Implement a segment tree that answers range GCD queries. For `arr = [12, 8, 6, 4]`, what is `gcd(0, 3)` and `gcd(0, 1)`? Why does GCD work as a merge function but average does not?

<details>
<summary>💡 Hint</summary>

GCD is associative: `gcd(gcd(a,b), c) == gcd(a, gcd(b,c))`. The identity element is 0 because `gcd(0, x) == x`. Average fails because `avg(avg(a,b), c) != avg(a,b,c)` when sub-ranges have unequal sizes.

</details>

<details>
<summary>✅ Answer</summary>

```python
import math

def build_gcd(arr, tree, node, start, end):
    if start == end:
        tree[node] = arr[start]
        return
    mid = (start + end) // 2
    build_gcd(arr, tree, 2 * node,     start, mid)
    build_gcd(arr, tree, 2 * node + 1, mid + 1, end)
    tree[node] = math.gcd(tree[2 * node], tree[2 * node + 1])  # associative merge

def query_gcd(tree, node, start, end, l, r):
    if r < start or end < l:
        return 0                  # identity: gcd(0, x) = x
    if l <= start and end <= r:
        return tree[node]
    mid = (start + end) // 2
    return math.gcd(
        query_gcd(tree, 2 * node,     start, mid,     l, r),
        query_gcd(tree, 2 * node + 1, mid + 1, end,   l, r)
    )


arr = [12, 8, 6, 4]
n = len(arr)
tree = [0] * (4 * n)
build_gcd(arr, tree, 1, 0, n - 1)

print(query_gcd(tree, 1, 0, n-1, 0, 3))  # gcd(12,8,6,4) = 2
print(query_gcd(tree, 1, 0, n-1, 0, 1))  # gcd(12,8) = 4

# Why average fails:
# avg(avg(1,2), 3) = avg(1.5, 3) = 2.25  WRONG
# true avg(1,2,3) = 2.0
# The two sub-averages have different-sized ranges; combining them
# with equal weight gives the wrong result.
# Fix: store (sum, count) pairs and compute avg = sum/count at query time.
```

**Why:** The segment tree merge function must be associative. GCD satisfies `gcd(gcd(a,b),c) == gcd(a,gcd(b,c))` for all integers. Average does not — it is a ratio and depends on segment length. The fix for average is to store (sum, count) tuples and derive the average at query time.

</details>

> 💻 Try it: [practice_local.py → Q9](./practice_local.py)

---

<a id="q10"></a>
### Q10 · tradeoffs — Segment Tree vs Prefix Sum vs BIT

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


🟡 Intermediate

**Problem:** You have an array of 10^5 integers. For each scenario, choose the right data structure and justify it:
1. 10^5 range sum queries, zero updates.
2. 10^5 range sum queries, 10^5 point updates.
3. 10^5 range minimum queries, 10^5 point updates.
4. 10^5 range sum queries, 10^5 range updates (add delta to entire range).

<details>
<summary>💡 Hint</summary>

Prefix sum: O(1) query, O(n) update — great when static. BIT: O(log n) point update + prefix sum, no range min/max. Segment tree: O(log n) everything including range min/max. Lazy segment tree: needed when you have range updates.

</details>

<details>
<summary>✅ Answer</summary>

```python
# Scenario 1: Range sum, no updates
# → Prefix Sum Array
# Build: O(n), Query: O(1), Update: O(n) — but there are no updates here
arr = [1, 3, 5, 7, 9]
prefix = [0] * (len(arr) + 1)
for i, v in enumerate(arr):
    prefix[i + 1] = prefix[i] + v
# range_sum(l, r) = prefix[r+1] - prefix[l]

# Scenario 2: Range sum + point updates
# → Fenwick Tree (BIT)
# Point update: O(log n), Range sum: O(log n), half the memory of segment tree
# Simpler to code than segment tree when only prefix sums are needed

# Scenario 3: Range minimum + point updates
# → Segment Tree
# BIT cannot support range min/max — it only supports invertible aggregations
# Segment tree: Build O(n), Query O(log n), Update O(log n)

# Scenario 4: Range sum + range updates (add delta to [l, r])
# → Lazy Segment Tree
# Range update without lazy: O(n) per update (touching every leaf) — too slow
# With lazy propagation: O(log n) range update, O(log n) range query

# Summary:
# ┌─────────────────────────────────────────────────────────────┐
# │             Prefix Sum  BIT       Segment   Lazy Segment    │
# │ Build         O(n)     O(n logn)  O(n)      O(n)            │
# │ Point update  O(n)     O(log n)   O(log n)  O(log n)        │
# │ Range query   O(1)     O(log n)   O(log n)  O(log n)        │
# │ Range min/max O(n)*    No         O(log n)  O(log n)        │
# │ Range update  O(n)     Trick**    O(n)*     O(log n)        │
# │ Code size     ~5 lines ~15 lines  ~30 lines ~50 lines       │
# └─────────────────────────────────────────────────────────────┘
# * naive, ** difference array trick
```

**Why:** Always reach for the simpler tool first: prefix sum if static, BIT if only point updates and prefix sums are needed, segment tree for range min/max, lazy segment tree for range updates. Segment trees are the most powerful but also the most code and memory.

</details>

> 💻 Try it: [practice_local.py → Q10](./practice_local.py)

---

<a id="q11"></a>
### Q11 · bit — Fenwick Tree Point Update and Prefix Sum

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


🟡 Intermediate

**Problem:** Implement a Fenwick Tree (BIT) that supports point update and range sum query. For `arr = [3, 2, 1, 4, 5]`, compute `range_sum(1, 3)`. After `update(2, +9)` (delta, not set), what is the new `range_sum(0, 4)`?

<details>
<summary>💡 Hint</summary>

The lowbit trick: `i & (-i)` extracts the lowest set bit of `i`. `update` moves forward by adding the lowbit; `query` moves backward by subtracting the lowbit. The tree is 1-indexed internally.

</details>

<details>
<summary>✅ Answer</summary>

```python
class FenwickTree:
    def __init__(self, n):
        self.n = n
        self.tree = [0] * (n + 1)   # 1-indexed; index 0 unused

    def update(self, i, delta):
        """Add delta to position i (0-indexed input)."""
        i += 1                       # convert to 1-indexed
        while i <= self.n:
            self.tree[i] += delta
            i += i & (-i)            # move to next responsible node

    def prefix_sum(self, i):
        """Prefix sum from index 0 to i inclusive (0-indexed input)."""
        i += 1                       # convert to 1-indexed
        total = 0
        while i > 0:
            total += self.tree[i]
            i -= i & (-i)            # move to parent by removing lowbit
        return total

    def range_sum(self, l, r):
        """Sum from l to r inclusive (0-indexed)."""
        if l == 0:
            return self.prefix_sum(r)
        return self.prefix_sum(r) - self.prefix_sum(l - 1)


arr = [3, 2, 1, 4, 5]
ft = FenwickTree(len(arr))
for i, v in enumerate(arr):
    ft.update(i, v)

print(ft.range_sum(1, 3))   # 2+1+4 = 7
print(ft.range_sum(0, 4))   # 15

ft.update(2, 9)              # arr[2] += 9  (delta, not set)
print(ft.range_sum(0, 4))   # 24  (was 15, added 9)

# Lowbit examples:
# i=6  → binary 110  → lowbit = 010 = 2
# i=12 → binary 1100 → lowbit = 0100 = 4
```

**Why:** The Fenwick tree exploits binary representation of indices to route updates and queries in O(log n). It uses half the memory of a segment tree and has smaller constant factors. Use it whenever only prefix sums and point updates are needed.

</details>

> 💻 Try it: [practice_local.py → Q11](./practice_local.py)

---

<a id="q12"></a>
### Q12 · bit — Fenwick Range Update With Difference Array

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


🟡 Intermediate

**Problem:** A Fenwick tree natively only does point updates. How can you support "add delta to all elements in range [l, r]" using a Fenwick tree? Implement it and verify: starting from `[0, 0, 0, 0, 0]`, after `range_add(1, 3, 5)` what is each element?

<details>
<summary>💡 Hint</summary>

Maintain a difference array inside the Fenwick tree. To add delta to [l, r]: `update(l, +delta)` and `update(r+1, -delta)`. Then a point query at index i becomes a prefix sum query (not a range sum).

</details>

<details>
<summary>✅ Answer</summary>

```python
class FenwickRangeUpdate:
    """
    Fenwick tree supporting:
      range_add(l, r, delta): add delta to arr[l..r]
      point_query(i): current value of arr[i]
    Uses the difference array trick internally.
    """
    def __init__(self, n):
        self.n = n
        self.bit = [0] * (n + 2)  # extra slot for r+1 boundary

    def _update(self, i, delta):
        i += 1
        while i <= self.n + 1:
            self.bit[i] += delta
            i += i & (-i)

    def _prefix(self, i):
        i += 1
        total = 0
        while i > 0:
            total += self.bit[i]
            i -= i & (-i)
        return total

    def range_add(self, l, r, delta):
        """Add delta to all elements in arr[l..r]."""
        self._update(l, delta)         # mark start of range
        self._update(r + 1, -delta)    # mark end of range (exclusive)

    def point_query(self, i):
        """Return current value of arr[i]."""
        return self._prefix(i)         # prefix sum = net delta applied at i


ft = FenwickRangeUpdate(5)
# Start: [0, 0, 0, 0, 0]
ft.range_add(1, 3, 5)
# Logical array: [0, 5, 5, 5, 0]

for i in range(5):
    print(f"arr[{i}] = {ft.point_query(i)}")
# arr[0] = 0, arr[1] = 5, arr[2] = 5, arr[3] = 5, arr[4] = 0
```

**Why:** The difference array trick converts range updates into two point updates. When you query position i, you take the prefix sum of the difference array, which gives the net accumulated delta at that position. This is a clever encoding that avoids needing lazy propagation for the range-update + point-query pattern.

</details>

> 💻 Try it: [practice_local.py → Q12](./practice_local.py)

---

<a id="q13"></a>
### Q13 · mistakes — Wrong Tree Size Crash

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


🟡 Intermediate

**Problem:** The following code uses `2*n` for the tree size. For which values of `n` does it crash with an IndexError, and why? Fix it.

```python
def build_broken(arr, tree, node, start, end):
    if start == end:
        tree[node] = arr[start]
        return
    mid = (start + end) // 2
    build_broken(arr, tree, 2 * node,     start, mid)
    build_broken(arr, tree, 2 * node + 1, mid + 1, end)
    tree[node] = tree[2 * node] + tree[2 * node + 1]

arr = [10, 20, 30]
tree = [0] * (2 * len(arr))   # BUG
build_broken(arr, tree, 1, 0, len(arr) - 1)
```

<details>
<summary>💡 Hint</summary>

Trace the recursion for n=3. What is the maximum node index that `build_broken` tries to write to? How does that compare to the size of the tree array?

</details>

<details>
<summary>✅ Answer</summary>

```python
# Trace for arr=[10,20,30] (n=3), tree size=6 (indices 0..5):
#
# build(node=1, 0, 2): mid=1
#   build(node=2, 0, 1): mid=0
#     build(node=4, 0, 0) → tree[4] = 10   (index 4, within bounds)
#     build(node=5, 1, 1) → tree[5] = 20   (index 5, last valid slot)
#     tree[2] = tree[4] + tree[5] = 30
#   build(node=3, 2, 2) → tree[3] = 30
# tree[1] = tree[2] + tree[3] = 60
#
# n=3 HAPPENS to fit in 2*n=6 slots — this is luck.
# For n=5: build tries to access tree[16] in a size-10 array → IndexError
# For n=6: build tries to access tree[16] in a size-12 array → IndexError
# General rule: for n just above 2^k, the tree needs up to 4*n nodes.

# FIX: always use 4*n
arr = [10, 20, 30]
n = len(arr)
tree_fixed = [0] * (4 * n)    # 12 slots — safe for any n

def build(arr, tree, node, start, end):
    if start == end:
        tree[node] = arr[start]
        return
    mid = (start + end) // 2
    build(arr, tree, 2 * node,     start, mid)
    build(arr, tree, 2 * node + 1, mid + 1, end)
    tree[node] = tree[2 * node] + tree[2 * node + 1]

build(arr, tree_fixed, 1, 0, n - 1)
print("Sum:", tree_fixed[1])  # 60

# n values that crash with 2*n:
# n=5: max index=16, 2*n=10 → CRASHES
# n=6: max index=16, 2*n=12 → CRASHES
# Always use 4*n. No exceptions.
```

**Why:** The `4*n` rule handles the worst case where `n` is just above a power of 2. The `2*n` allocation silently passes simple tests for some `n` values and only fails for others — making it a subtle production bug. Always allocate `4*n` with no exceptions.

</details>

> 💻 Try it: [practice_local.py → Q13](./practice_local.py)

---

<a id="q14"></a>
### Q14 · mistakes — Indexing Convention Consistency

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


🟡 Intermediate

**Problem:** The following build function uses 1-indexed child formulas, but the query function uses 0-indexed child formulas. Find the bug and explain what wrong answer it produces for `query(1, 0, 3, 0, 1)` on `arr = [1, 2, 3, 4]`.

```python
def build(arr, tree, node, start, end):
    if start == end:
        tree[node] = arr[start]; return
    mid = (start + end) // 2
    build(arr, tree, 2*node, start, mid)           # 1-indexed children
    build(arr, tree, 2*node+1, mid+1, end)
    tree[node] = tree[2*node] + tree[2*node+1]

def query_bug(tree, node, start, end, l, r):
    if r < start or end < l: return 0
    if l <= start and end <= r: return tree[node]
    mid = (start + end) // 2
    left  = query_bug(tree, 2*node+1, start, mid, l, r)  # 0-indexed! BUG
    right = query_bug(tree, 2*node+2, mid+1, end, l, r)  # 0-indexed! BUG
    return left + right
```

<details>
<summary>💡 Hint</summary>

The build stores data at 1-indexed positions (left child of root is at index 2). The buggy query navigates to index 3 (2*1+1) instead of index 2, reading wrong data.

</details>

<details>
<summary>✅ Answer</summary>

```python
# The bug: build stores data using 1-indexed formula (left child = 2*node)
# but query navigates using 0-indexed formula (left child = 2*node+1)
#
# For arr = [1, 2, 3, 4], after correct build:
#   tree[1] = 10  (root, sum of all)
#   tree[2] =  3  (sum of arr[0..1] = 1+2)
#   tree[3] =  7  (sum of arr[2..3] = 3+4)
#   tree[4] =  1  (arr[0])
#   tree[5] =  2  (arr[1])
#   tree[6] =  3  (arr[2])
#   tree[7] =  4  (arr[3])
#
# query_bug(1, 0, 3, 0, 1)  [expected: sum of arr[0..1] = 3]:
#   Partial overlap, mid=1
#   left  = query_bug(2*1+1=3, ...)  reads tree[3] = 7 (sum of [2..3]!) WRONG
#   right = query_bug(2*1+2=4, ...)  reads tree[4] = 1 (arr[0]!) WRONG
#   Returns a wrong value instead of 3

# FIX: use consistent 1-indexed formulas in query
def query_fixed(tree, node, start, end, l, r):
    if r < start or end < l: return 0
    if l <= start and end <= r: return tree[node]
    mid = (start + end) // 2
    left  = query_fixed(tree, 2 * node,     start, mid,     l, r)  # 1-indexed
    right = query_fixed(tree, 2 * node + 1, mid + 1, end,   l, r)  # 1-indexed
    return left + right

arr = [1, 2, 3, 4]
n = len(arr)
tree = [0] * (4 * n)
build(arr, tree, 1, 0, n - 1)
print(query_fixed(tree, 1, 0, n-1, 0, 1))  # 3 correct
```

**Why:** Mixing indexing conventions is one of the most common segment tree bugs because it produces wrong answers (not errors) for some queries, making it hard to detect. The golden rule: pick one convention (1-indexed is standard), write it in a comment at the top of the class, and never deviate.

</details>

> 💻 Try it: [practice_local.py → Q14](./practice_local.py)

---

<a id="q15"></a>
### Q15 · lazy — Lazy Propagation Range Add and Range Sum

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


🟠 Advanced

**Problem:** Implement a segment tree with lazy propagation that supports:
- `range_add(l, r, delta)`: add delta to every element in `arr[l..r]`
- `range_sum(l, r)`: return sum of `arr[l..r]`

Starting from `arr = [1, 2, 3, 4, 5]`, after `range_add(1, 3, 10)` what is `range_sum(0, 4)`?

<details>
<summary>💡 Hint</summary>

When a node's segment is completely inside the update range, update its sum with `delta * segment_length` and store the delta in `lazy[node]`. Before recursing into children (partial overlap), push the lazy value down first.

</details>

<details>
<summary>✅ Answer</summary>

```python
class LazySegTree:
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)   # pending delta for each node
        if self.n > 0:
            self._build(arr, 1, 0, self.n - 1)

    def _build(self, arr, node, start, end):
        if start == end:
            self.tree[node] = arr[start]
            return
        mid = (start + end) // 2
        self._build(arr, 2 * node,     start, mid)
        self._build(arr, 2 * node + 1, mid + 1, end)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def _push_down(self, node, start, end):
        """Push pending lazy value to children. Call before recursing."""
        if self.lazy[node] != 0:
            mid = (start + end) // 2
            left_len  = mid - start + 1
            right_len = end - mid

            self.tree[2 * node]     += self.lazy[node] * left_len
            self.lazy[2 * node]     += self.lazy[node]

            self.tree[2 * node + 1] += self.lazy[node] * right_len
            self.lazy[2 * node + 1] += self.lazy[node]

            self.lazy[node] = 0    # clear after pushing down

    def range_add(self, l, r, delta, node=1, start=0, end=None):
        if end is None:
            end = self.n - 1
        if r < start or end < l:
            return
        if l <= start and end <= r:
            # Complete overlap: update sum in O(1) using segment length
            self.tree[node] += delta * (end - start + 1)
            self.lazy[node] += delta
            return
        # Partial overlap: push lazy down first, then recurse
        self._push_down(node, start, end)
        mid = (start + end) // 2
        self.range_add(l, r, delta, 2 * node,     start, mid)
        self.range_add(l, r, delta, 2 * node + 1, mid + 1, end)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def range_sum(self, l, r, node=1, start=0, end=None):
        if end is None:
            end = self.n - 1
        if r < start or end < l:
            return 0
        if l <= start and end <= r:
            return self.tree[node]
        self._push_down(node, start, end)   # push before reading children
        mid = (start + end) // 2
        return (self.range_sum(l, r, 2 * node,     start, mid) +
                self.range_sum(l, r, 2 * node + 1, mid + 1, end))


arr = [1, 2, 3, 4, 5]
st = LazySegTree(arr)
print(st.range_sum(0, 4))   # 15
st.range_add(1, 3, 10)      # add 10 to indices 1, 2, 3 → [1, 12, 13, 14, 5]
print(st.range_sum(0, 4))   # 45  (15 + 10*3)
print(st.range_sum(1, 3))   # 39  (12+13+14)
```

**Why:** Without lazy propagation, `range_add` would visit every leaf in the range — O(n) per update. With lazy, a complete-overlap node gets updated in O(1) and the pending work is deferred. Only when children must be visited (partial overlap or query into sub-range) is the lazy tag pushed down. Total complexity stays O(log n) per operation.

</details>

> 💻 Try it: [practice_local.py → Q15](./practice_local.py)

---

<a id="q16"></a>
### Q16 · lazy — Push-Down Mechanics

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


🟠 Advanced

**Problem:** Explain the `_push_down` function in detail. Why must it be called before recursing into children in BOTH the `range_add` and `range_sum` functions? What happens if you forget it in `range_sum`?

<details>
<summary>💡 Hint</summary>

Think of the lazy tag as a sticky note on a manager's door: "everyone in my department gets a $100 raise." If you walk past the manager and knock directly on an employee's door, the employee never received the memo — they still report the old salary.

</details>

<details>
<summary>✅ Answer</summary>

```python
# Push-down: transfer a node's pending lazy update to its two children
#
# When does a node have a lazy tag?
#   range_add was called and this node's segment was COMPLETELY inside the range.
#   Instead of updating all leaves, we stopped here and recorded the pending delta.
#
# Why must we push BEFORE recursing?
#   When partial overlap forces us to visit children, those children may be
#   unaware of the parent's accumulated lazy. Reading a child directly returns stale data.

def _push_down_explained(tree, lazy, node, start, end):
    if lazy[node] == 0:
        return   # nothing pending, nothing to push

    mid = (start + end) // 2

    # Update LEFT child's stored sum:
    # The lazy delta applies to every element in left child's range.
    left_len = mid - start + 1
    tree[2 * node] += lazy[node] * left_len
    lazy[2 * node] += lazy[node]        # propagate tag to left child

    # Same for RIGHT child:
    right_len = end - mid
    tree[2 * node + 1] += lazy[node] * right_len
    lazy[2 * node + 1] += lazy[node]   # propagate tag to right child

    lazy[node] = 0   # clear current node's lazy — it has been pushed down

# What happens if you forget push_down in range_sum?
# arr = [1,1,1,1], range_add(0,3,10), then query range_sum(0,0):
#
# After range_add(0,3,10):
#   tree[root]=44, lazy[root]=10
#   Children: tree[left]=2, tree[right]=2  (stale — not yet updated)
#
# range_sum(0,0) without push_down:
#   root: partial overlap → recurse left child
#   left child (0,1): partial overlap → recurse left child
#   leaf (0,0): complete overlap → return tree[leaf] = 1
#   Returns 1 instead of 11  WRONG

# The invariant:
# tree[node] is ALWAYS correct (accounts for all lazy applied at or above this node).
# tree[child] may be STALE until push_down is called on node.
# Rule: before recursing into children, call _push_down first.
```

**Why:** The lazy tag is a deferred contract. `tree[node]` is always current, but `tree[child]` may lag behind. Every time you recurse through a node to reach its children — whether for a query or an update — you must honor the contract first by calling `_push_down`. This is the single rule that keeps the entire lazy system correct.

</details>

> 💻 Try it: [practice_local.py → Q16](./practice_local.py)

---

<a id="q17"></a>
### Q17 · lazy — Lazy Propagation Missing Push-Down Bug

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


🟠 Advanced

**Problem:** The following lazy segment tree is missing one push_down call. Identify exactly where it is missing, explain what wrong answer it produces, and fix it.

```python
class BuggyLazyTree:
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        self._build(arr, 1, 0, self.n - 1)

    def _build(self, arr, node, start, end):
        if start == end:
            self.tree[node] = arr[start]; return
        mid = (start + end) // 2
        self._build(arr, 2*node, start, mid)
        self._build(arr, 2*node+1, mid+1, end)
        self.tree[node] = self.tree[2*node] + self.tree[2*node+1]

    def _push_down(self, node, start, end):
        if self.lazy[node]:
            mid = (start + end) // 2
            l, r = 2*node, 2*node+1
            self.tree[l]  += self.lazy[node] * (mid - start + 1)
            self.tree[r]  += self.lazy[node] * (end - mid)
            self.lazy[l]  += self.lazy[node]
            self.lazy[r]  += self.lazy[node]
            self.lazy[node] = 0

    def range_add(self, l, r, delta, node=1, start=0, end=None):
        if end is None: end = self.n - 1
        if r < start or end < l: return
        if l <= start and end <= r:
            self.tree[node] += delta * (end - start + 1)
            self.lazy[node] += delta
            return
        self._push_down(node, start, end)  # correct placement
        mid = (start + end) // 2
        self.range_add(l, r, delta, 2*node, start, mid)
        self.range_add(l, r, delta, 2*node+1, mid+1, end)
        self.tree[node] = self.tree[2*node] + self.tree[2*node+1]

    def range_sum(self, l, r, node=1, start=0, end=None):
        if end is None: end = self.n - 1
        if r < start or end < l: return 0
        if l <= start and end <= r: return self.tree[node]
        # MISSING: self._push_down(node, start, end)
        mid = (start + end) // 2
        return (self.range_sum(l, r, 2*node, start, mid) +
                self.range_sum(l, r, 2*node+1, mid+1, end))
```

<details>
<summary>💡 Hint</summary>

Look at `range_sum`. When it hits partial overlap and recurses into children, are those children guaranteed to have up-to-date values?

</details>

<details>
<summary>✅ Answer</summary>

```python
# Bug location: range_sum is missing _push_down before recursing in partial overlap.
#
# Demonstration:
# arr = [1, 1, 1, 1]
# range_add(0, 3, 10) → root: tree=44, lazy=10
#                     → children: tree=2 each, lazy=0  (not yet pushed)
#
# range_sum(0, 0)  [should be 11]:
#   root: partial overlap → recurse left (NO push_down → children still stale)
#   left child (0,1): partial overlap → recurse left (still no push_down)
#   leaf (0,0): complete → return tree[leaf] = 1  WRONG, should be 11

# Fix: add _push_down in range_sum before recursing
def range_sum_fixed(self, l, r, node=1, start=0, end=None):
    if end is None:
        end = self.n - 1
    if r < start or end < l:
        return 0
    if l <= start and end <= r:
        return self.tree[node]
    self._push_down(node, start, end)   # THIS LINE WAS MISSING
    mid = (start + end) // 2
    return (self.range_sum_fixed(l, r, 2 * node,     start, mid) +
            self.range_sum_fixed(l, r, 2 * node + 1, mid + 1, end))

# Rule: any time you recurse into children in a lazy segment tree,
# call _push_down FIRST — whether it's a query or an update.
# The only exception: leaf nodes (start==end) have no children to push to.
```

**Why:** The `range_sum` function reads from children. If the parent has a pending lazy tag, those children hold stale sums. The fix is always the same: call `_push_down` before any recursion into children. This is the single most common lazy propagation bug — it produces wrong answers silently with no exception raised.

</details>

> 💻 Try it: [practice_local.py → Q17](./practice_local.py)

---

<a id="q18"></a>
### Q18 · merge — Interval Merge Queries

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


🟠 Advanced

**Problem:** Design a segment tree that tracks the maximum length of consecutive 1s in an array of 0s and 1s. Each node must store more than just one value. For `arr = [1, 1, 0, 1, 1, 1, 0, 1]`, what is the length of the longest run of 1s?

<details>
<summary>💡 Hint</summary>

Each node needs to store: the longest run in the range, the longest run starting from the left edge, the longest run ending at the right edge, and the total length of the segment. When merging two nodes, the new longest run is `max(left.max_run, right.max_run, left.suffix + right.prefix)`.

</details>

<details>
<summary>✅ Answer</summary>

```python
class NodeInfo:
    """Information stored at each segment tree node for consecutive-1s queries."""
    def __init__(self, prefix, suffix, max_run, length):
        self.prefix = prefix   # longest run of 1s starting at left edge
        self.suffix = suffix   # longest run of 1s ending at right edge
        self.max_run = max_run # longest run anywhere in this segment
        self.length = length   # total length of this segment

def merge(left, right):
    """Combine two NodeInfo objects into a parent NodeInfo."""
    new_prefix = left.prefix
    if left.prefix == left.length:       # left segment is ALL 1s
        new_prefix = left.length + right.prefix

    new_suffix = right.suffix
    if right.suffix == right.length:     # right segment is ALL 1s
        new_suffix = right.length + left.suffix

    # The crossing run connects left's trailing 1s with right's leading 1s
    new_max = max(left.max_run, right.max_run, left.suffix + right.prefix)
    return NodeInfo(new_prefix, new_suffix, new_max, left.length + right.length)

def build(arr, tree, node, start, end):
    if start == end:
        val = arr[start]
        tree[node] = NodeInfo(val, val, val, 1)
        return
    mid = (start + end) // 2
    build(arr, tree, 2 * node,     start, mid)
    build(arr, tree, 2 * node + 1, mid + 1, end)
    tree[node] = merge(tree[2 * node], tree[2 * node + 1])

def query(tree, node, start, end, l, r):
    if l <= start and end <= r:
        return tree[node]
    mid = (start + end) // 2
    if r <= mid:
        return query(tree, 2 * node, start, mid, l, r)
    if l > mid:
        return query(tree, 2 * node + 1, mid + 1, end, l, r)
    left_info  = query(tree, 2 * node,     start, mid,     l, r)
    right_info = query(tree, 2 * node + 1, mid + 1, end,   l, r)
    return merge(left_info, right_info)


arr = [1, 1, 0, 1, 1, 1, 0, 1]
n = len(arr)
tree = [None] * (4 * n)
build(arr, tree, 1, 0, n - 1)

result = query(tree, 1, 0, n - 1, 0, n - 1)
print("Longest run of 1s:", result.max_run)  # 3  (indices 3, 4, 5)
```

**Why:** This is an interval merge query — the answer at a parent cannot be derived from a single number at each child. The key insight is the crossing run `left.suffix + right.prefix`: two runs can merge across the split boundary. Storing prefix and suffix lengths at each node enables this crossing-run computation during the merge.

</details>

> 💻 Try it: [practice_local.py → Q18](./practice_local.py)

---

<a id="q19"></a>
### Q19 · merge — Non-Associative Merge Function Trap

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


🟠 Advanced

**Problem:** A developer uses `average` as the merge function to answer "average of range [l, r]". For `arr = [1, 2, 3]`, what wrong answer does the root produce, and why? What is the correct fix?

<details>
<summary>💡 Hint</summary>

`avg(avg(1,2), 3)` is not the same as `avg(1,2,3)` because the two sub-ranges have different sizes. The root would compute average of two averages as if they are equal-weight.

</details>

<details>
<summary>✅ Answer</summary>

```python
# Wrong approach: using average as merge function

def build_wrong_avg(arr, tree, node, start, end):
    if start == end:
        tree[node] = arr[start]
        return
    mid = (start + end) // 2
    build_wrong_avg(arr, tree, 2*node,   start, mid)
    build_wrong_avg(arr, tree, 2*node+1, mid+1, end)
    tree[node] = (tree[2*node] + tree[2*node+1]) / 2  # BUG

# For arr = [1, 2, 3]:
# build(node=2, 0, 1): tree[2] = avg(1, 2) = 1.5  (covers 2 elements)
# build(node=3, 2, 2): tree[3] = 3                 (covers 1 element)
# build(node=1, 0, 2): tree[1] = avg(1.5, 3) = 2.25  WRONG
# True average = (1+2+3)/3 = 2.0

# Why it fails: avg(L, R) treats both sub-results as equal weight,
# but the left covers 2 elements and the right covers 1 element.

# Correct approach: store (sum, count) — average is always derivable
def build_correct_avg(arr, tree, node, start, end):
    if start == end:
        tree[node] = (arr[start], 1)   # (sum, count)
        return
    mid = (start + end) // 2
    build_correct_avg(arr, tree, 2*node,   start, mid)
    build_correct_avg(arr, tree, 2*node+1, mid+1, end)
    l_sum, l_cnt = tree[2*node]
    r_sum, r_cnt = tree[2*node+1]
    tree[node] = (l_sum + r_sum, l_cnt + r_cnt)  # sum sums, sum counts

def query_avg(tree, node, start, end, l, r):
    if r < start or end < l: return (0, 0)
    if l <= start and end <= r: return tree[node]
    mid = (start + end) // 2
    l_sum, l_cnt = query_avg(tree, 2*node,   start, mid,   l, r)
    r_sum, r_cnt = query_avg(tree, 2*node+1, mid+1, end,   l, r)
    return (l_sum + r_sum, l_cnt + r_cnt)

arr = [1, 2, 3]
n = len(arr)
tree = [(0, 0)] * (4 * n)
build_correct_avg(arr, tree, 1, 0, n - 1)

total_sum, total_count = query_avg(tree, 1, 0, n-1, 0, n-1)
print(f"Average of [1,2,3]: {total_sum/total_count}")  # 2.0 correct

sub_sum, sub_count = query_avg(tree, 1, 0, n-1, 0, 1)
print(f"Average of [1,2]: {sub_sum/sub_count}")         # 1.5 correct
```

**Why:** Segment trees require that the merge function be **associative**: `merge(merge(a,b), c) == merge(a, merge(b,c))`. Average fails this because it is size-dependent. Valid merge operations: sum, min, max, GCD, LCM, XOR, AND, OR. Invalid: average, median, standard deviation. The fix is to store sufficient information (sum + count) so the correct result can always be computed.

</details>

> 💻 Try it: [practice_local.py → Q19](./practice_local.py)

---

<a id="q20"></a>
### Q20 · advanced — Coordinate Compression Count in Range

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


🟠 Advanced

**Problem:** Given a list of integers `values = [1, 3, 5, 7, 9, 3, 1, 5, 5]`, build a segment tree that answers: "how many values fall in range [lo, hi]?" What does `count_in_range(1, 5)` return?

<details>
<summary>💡 Hint</summary>

Compress the value space: sort and deduplicate the values to get compressed indices. Build a frequency tree where each leaf stores the count of that value. A range count query becomes a sum query over the compressed index range.

</details>

<details>
<summary>✅ Answer</summary>

```python
from bisect import bisect_left, bisect_right

class CountInRangeSegTree:
    """
    Segment tree over coordinate-compressed value space.
    Answers: how many elements x satisfy lo <= x <= hi?
    """
    def __init__(self, values):
        self.sorted_vals = sorted(set(values))  # coordinate compression
        self.m = len(self.sorted_vals)
        self.tree = [0] * (4 * self.m)
        for v in values:
            self._update(self._compress(v), 1, 1, 0, self.m - 1)

    def _compress(self, val):
        """Map a concrete value to its compressed 0-based index."""
        idx = bisect_left(self.sorted_vals, val)
        if idx >= self.m or self.sorted_vals[idx] != val:
            raise ValueError(f"{val} not in known value set")
        return idx

    def _update(self, ci, delta, node, start, end):
        if start == end:
            self.tree[node] += delta
            return
        mid = (start + end) // 2
        if ci <= mid:
            self._update(ci, delta, 2 * node,     start, mid)
        else:
            self._update(ci, delta, 2 * node + 1, mid + 1, end)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def _query(self, cl, cr, node, start, end):
        if cr < start or end < cl:
            return 0
        if cl <= start and end <= cr:
            return self.tree[node]
        mid = (start + end) // 2
        return (self._query(cl, cr, 2 * node,     start, mid) +
                self._query(cl, cr, 2 * node + 1, mid + 1, end))

    def count_in_range(self, lo, hi):
        cl = bisect_left(self.sorted_vals, lo)
        cr = bisect_right(self.sorted_vals, hi) - 1
        if cl > cr:
            return 0
        return self._query(cl, cr, 1, 0, self.m - 1)


values = [1, 3, 5, 7, 9, 3, 1, 5, 5]
cst = CountInRangeSegTree(values)

print(cst.count_in_range(1, 5))   # 7  (1,1,3,3,5,5,5)
print(cst.count_in_range(6, 9))   # 2  (7,9)
print(cst.count_in_range(4, 6))   # 3  (5,5,5)
print(cst.count_in_range(10, 20)) # 0
```

**Why:** Coordinate compression maps a potentially huge value space (0 to 10^9) to a compact range of size equal to the number of distinct values. The segment tree then operates on this compact space in O(log M) where M is the number of distinct values. This pattern appears in offline range counting problems, order statistics, and inversion counting.

</details>

> 💻 Try it: [practice_local.py → Q20](./practice_local.py)

---

**[⬅️ Theory](./theory.md)** · **[💻 Local Practice](./practice_local.py)**

**Prev:** [← 22_bit_manipulation](../22_bit_manipulation/practice.md) | **Next:** [24_disjoint_set_union →](../24_disjoint_set_union/practice.md)
