# Segment Tree — Cheatsheet

---

## When to Use Segment Tree

Use segment tree when you need **both**:
- Range queries (sum, min, max, XOR over [l, r])
- Point OR range updates

| Problem Type                        | Use              |
|-------------------------------------|------------------|
| Range sum query, point update       | BIT (Fenwick)    |
| Range sum query, range update       | Segment Tree + Lazy |
| Range min/max query, point update   | Segment Tree     |
| Range min/max query, range update   | Segment Tree + Lazy |
| Prefix sums only, no updates        | Prefix sum array |

---

## Complexity Table

| Operation      | Time      | Space  |
|----------------|-----------|--------|
| Build          | O(n)      | O(4n)  |
| Point query    | O(log n)  | —      |
| Range query    | O(log n)  | —      |
| Point update   | O(log n)  | —      |
| Range update (lazy) | O(log n) | —   |

---

## Segment Tree Structure

```
Array index (1-based):
              1
           /     \
          2       3
        /   \   /   \
       4     5 6     7

- Node 1: root (entire array)
- Left child of i: 2*i
- Right child of i: 2*i + 1
- Parent of i: i // 2
- Leaf nodes: indices n to 2n-1 (for 1-indexed, leaves at bottom)
- Array size: 4 * n (safe upper bound)
```

---

## Full Segment Tree Implementation (Range Sum)

```python
class SegmentTree:
    def __init__(self, data):
        self.n = len(data)
        self.tree = [0] * (4 * self.n)
        if self.n > 0:
            self._build(data, 1, 0, self.n - 1)

    def _build(self, data, node, start, end):
        if start == end:
            self.tree[node] = data[start]
        else:
            mid = (start + end) // 2
            self._build(data, 2*node,   start, mid)
            self._build(data, 2*node+1, mid+1, end)
            self.tree[node] = self.tree[2*node] + self.tree[2*node+1]

    def update(self, idx, val, node=1, start=0, end=None):
        if end is None: end = self.n - 1
        if start == end:
            self.tree[node] = val
        else:
            mid = (start + end) // 2
            if idx <= mid:
                self.update(idx, val, 2*node,   start, mid)
            else:
                self.update(idx, val, 2*node+1, mid+1, end)
            self.tree[node] = self.tree[2*node] + self.tree[2*node+1]

    def query(self, l, r, node=1, start=0, end=None):
        if end is None: end = self.n - 1
        if r < start or end < l:        # completely outside
            return 0                    # identity for sum
        if l <= start and end <= r:     # completely inside
            return self.tree[node]
        mid = (start + end) // 2
        left  = self.query(l, r, 2*node,   start, mid)
        right = self.query(l, r, 2*node+1, mid+1, end)
        return left + right

# Usage
st = SegmentTree([1, 3, 5, 7, 9, 11])
print(st.query(1, 3))   # sum of index 1..3 = 15
st.update(1, 10)        # set index 1 to 10
print(st.query(1, 3))   # now 22
```

---

## Range Min Segment Tree

```python
class MinSegTree:
    def __init__(self, data):
        self.n = len(data)
        self.tree = [float('inf')] * (4 * self.n)
        self._build(data, 1, 0, self.n - 1)

    def _build(self, data, node, s, e):
        if s == e:
            self.tree[node] = data[s]; return
        m = (s + e) // 2
        self._build(data, 2*node,   s, m)
        self._build(data, 2*node+1, m+1, e)
        self.tree[node] = min(self.tree[2*node], self.tree[2*node+1])

    def query(self, l, r, node=1, s=0, e=None):
        if e is None: e = self.n - 1
        if r < s or e < l: return float('inf')  # identity for min
        if l <= s and e <= r: return self.tree[node]
        m = (s + e) // 2
        return min(self.query(l, r, 2*node, s, m),
                   self.query(l, r, 2*node+1, m+1, e))
```

**Identity values by operation:**
- Sum: `0`
- Min: `float('inf')`
- Max: `float('-inf')`
- XOR: `0`
- Product: `1`

---

## Lazy Propagation (Range Update + Range Query)

```python
class LazySegTree:
    def __init__(self, data):
        self.n = len(data)
        self.tree = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        self._build(data, 1, 0, self.n - 1)

    def _build(self, data, node, s, e):
        if s == e:
            self.tree[node] = data[s]; return
        m = (s + e) // 2
        self._build(data, 2*node, s, m)
        self._build(data, 2*node+1, m+1, e)
        self.tree[node] = self.tree[2*node] + self.tree[2*node+1]

    def _push_down(self, node, s, e):
        if self.lazy[node] != 0:
            m = (s + e) // 2
            mid_len  = m - s + 1
            right_len = e - m
            self.tree[2*node]   += self.lazy[node] * mid_len
            self.tree[2*node+1] += self.lazy[node] * right_len
            self.lazy[2*node]   += self.lazy[node]
            self.lazy[2*node+1] += self.lazy[node]
            self.lazy[node] = 0

    def range_update(self, l, r, val, node=1, s=0, e=None):
        if e is None: e = self.n - 1
        if r < s or e < l: return
        if l <= s and e <= r:
            self.tree[node] += val * (e - s + 1)
            self.lazy[node] += val
            return
        self._push_down(node, s, e)
        m = (s + e) // 2
        self.range_update(l, r, val, 2*node,   s, m)
        self.range_update(l, r, val, 2*node+1, m+1, e)
        self.tree[node] = self.tree[2*node] + self.tree[2*node+1]

    def query(self, l, r, node=1, s=0, e=None):
        if e is None: e = self.n - 1
        if r < s or e < l: return 0
        if l <= s and e <= r: return self.tree[node]
        self._push_down(node, s, e)
        m = (s + e) // 2
        return (self.query(l, r, 2*node,   s, m) +
                self.query(l, r, 2*node+1, m+1, e))
```

---

## Fenwick Tree (BIT) — Simpler Alternative for Prefix Sums

```python
class BIT:
    def __init__(self, n):
        self.n = n
        self.tree = [0] * (n + 1)   # 1-indexed

    def update(self, i, delta):     # add delta to index i (1-indexed)
        while i <= self.n:
            self.tree[i] += delta
            i += i & (-i)           # move to next responsible node

    def query(self, i):             # prefix sum [1, i]
        total = 0
        while i > 0:
            total += self.tree[i]
            i -= i & (-i)           # move to parent
        return total

    def range_query(self, l, r):    # sum [l, r] (1-indexed)
        return self.query(r) - self.query(l - 1)

# Usage: O(n log n) build, O(log n) update and query
```

**BIT vs Segment Tree:**
- BIT: less code, lower constant factor, prefix sums + point updates only
- Segment Tree: range min/max, range updates, more flexible

---

## Common Patterns

```python
# Count inversions using BIT
def count_inversions(arr):
    n = len(arr)
    compressed = {v: i+1 for i, v in enumerate(sorted(set(arr)))}
    bit = BIT(n)
    inversions = 0
    for i in range(n - 1, -1, -1):
        rank = compressed[arr[i]]
        inversions += bit.query(rank - 1)
        bit.update(rank, 1)
    return inversions

# Coordinate compression (common with seg tree)
vals = sorted(set(arr))
compress = {v: i for i, v in enumerate(vals)}
arr_compressed = [compress[x] for x in arr]
```

---

## Gotchas

- Array size must be `4 * n` — not `2 * n` (needed for non-power-of-2 sizes)
- 1-indexed internally; convert 0-indexed input by passing `start=0, end=n-1`
- Lazy propagation: always push down before recursing into children
- Identity element depends on operation — wrong identity breaks queries outside range
- BIT is 1-indexed; off-by-one errors are common when converting from 0-indexed input
- Range update with lazy: track both the cumulative add AND update the tree value immediately

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Visual Explanation](./visual_explanation.md) &nbsp;|&nbsp; **Next:** [Real World Usage →](./real_world_usage.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
