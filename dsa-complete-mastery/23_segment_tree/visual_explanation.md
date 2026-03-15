# Segment Trees — The Tournament Bracket That Never Forgets

---

## The Sports Tournament Analogy

Imagine a sports tournament with 8 players. You want to find the strongest player overall.
Round 1: players compete in pairs. Winners advance.

```
Players (by score):   [4,  2,  7,  1,  5,  3,  8,  6]
                       P0  P1  P2  P3  P4  P5  P6  P7

Round 1 (pairs):
  P0 vs P1: max(4,2)=4    P2 vs P3: max(7,1)=7    P4 vs P5: max(5,3)=5    P6 vs P7: max(8,6)=8
               [4]                   [7]                      [5]                      [8]

Round 2:
  max(4,7)=7                          max(5,8)=8
     [7]                                 [8]

Final:
  max(7,8)=8
     [8]
```

**8 is the overall champion. Makes sense.**

But here's the key difference between this and a regular tournament:
**The bracket REMEMBERS all the intermediate results.**

So if someone asks you "what's the max score among players 2 through 5?", you don't need to
re-run the tournament. You just look up the stored results for the relevant bracket sections.
That's the entire idea behind a segment tree.

---

## Building the Segment Tree

Let's use our array: **[4, 2, 7, 1, 5, 3, 8, 6]** (indices 0 through 7)

We'll build a **sum** segment tree this time (same structure, sum instead of max).

Each node stores the sum of a range. The root stores the sum of the entire array.

```
Array:  [4,  2,  7,  1,  5,  3,  8,  6]
Index:   0   1   2   3   4   5   6   7
```

Here's the full tree. Each node is labeled `[range]: value`.

```
                          [0,7]: 36
                        /             \
              [0,3]: 14               [4,7]: 22
             /        \              /         \
         [0,1]: 6   [2,3]: 8    [4,5]: 8    [6,7]: 14
         /    \     /    \      /    \       /     \
       [0]:4 [1]:2 [2]:7 [3]:1 [4]:5 [5]:3 [6]:8  [7]:6
```

**Reading the tree:**
- Root `[0,7]: 36` covers the entire array. Sum = 4+2+7+1+5+3+8+6 = 36. Correct.
- `[0,3]: 14` covers indices 0-3. Sum = 4+2+7+1 = 14. Correct.
- `[4,7]: 22` covers indices 4-7. Sum = 5+3+8+6 = 22. Correct.
- Leaf nodes are the original array values.

**Building rule:** Each parent = sum of its two children. Build bottom-up.

```python
def build(arr, node, start, end):
    if start == end:
        tree[node] = arr[start]          # leaf: store array value
    else:
        mid = (start + end) // 2
        build(arr, 2*node,   start, mid)  # build left child
        build(arr, 2*node+1, mid+1, end)  # build right child
        tree[node] = tree[2*node] + tree[2*node+1]  # parent = sum of children
```

---

## Range Query: "What Is the Sum from Index 2 to 5?"

The query is: `sum(arr[2..5])` = 7+1+5+3 = **16**

Without a segment tree, you'd scan indices 2,3,4,5 — 4 operations.
For a range query on a million-element array, that could be 500,000 operations.
With a segment tree: O(log n) operations.

**How? By reusing pre-computed results.**

Here's the traversal for range [2, 5]:

```
                          [0,7]: 36              ← Query [2,5]. Does [0,7] overlap [2,5]? Yes but not fully.
                        /             \             Split and go both ways.
              [0,3]: 14               [4,7]: 22  ← [0,3] overlaps [2,5] partially. [4,7] overlaps partially.
             /        \              /         \    Keep going.
         [0,1]: 6   [2,3]: 8    [4,5]: 8    [6,7]: 14
         /    \     /    \      /    \       /     \
       [0]:4 [1]:2 [2]:7 [3]:1 [4]:5 [5]:3 [6]:8  [7]:6
```

Decision at each node:

```
[0,7]: Query [2,5]. Node covers [0,7]. Partial overlap → visit children.

  [0,3]: Query [2,5]. Node covers [0,3]. Partial overlap → visit children.

    [0,1]: Query [2,5]. Node covers [0,1]. NO overlap (1 < 2). Return 0.
    [2,3]: Query [2,5]. Node covers [2,3]. FULLY inside [2,5]. Return 8! ✓

  [4,7]: Query [2,5]. Node covers [4,7]. Partial overlap → visit children.

    [4,5]: Query [2,5]. Node covers [4,5]. FULLY inside [2,5]. Return 8! ✓
    [6,7]: Query [2,5]. Node covers [6,7]. NO overlap (6 > 5). Return 0.
```

Total result: 0 + 8 + 8 + 0 = **16**. Correct!

**Nodes visited:** [0,7], [0,3], [0,1], [2,3], [4,7], [4,5], [6,7] = 7 nodes.

For an 8-element array, we visited 7 nodes. Sounds like a lot! But for a 1,000,000-element array,
a range query visits at most **4 × log₂(n) ≈ 80 nodes**. That's the power.

**The three cases during a query:**
```
1. NO overlap:      This node's range is completely outside query range. Return 0 (identity).
2. FULL overlap:    This node's range is completely inside query range. Return stored value!
3. PARTIAL overlap: Split into children, query both, combine results.
```

---

## Point Update: "Change arr[3] from 1 to 9"

We want to update a single element. Which nodes in the tree need to change?

Only the nodes on the **path from the updated leaf to the root**.

```
Updating index 3 (value 1 → 9). Difference = +8.

Which nodes contain index 3 in their range?

                          [0,7]: 36  ← Contains index 3. NEEDS UPDATE.
                        /
              [0,3]: 14              ← Contains index 3. NEEDS UPDATE.
                        \
                        [2,3]: 8    ← Contains index 3. NEEDS UPDATE.
                              \
                              [3]:1  ← This IS index 3. NEEDS UPDATE.
```

Update path (leaf → root):

```
Step 1: Update leaf [3]: 1 → 9
Step 2: Update [2,3]: was 7+1=8, now 7+9=16
Step 3: Update [0,3]: was 4+2+7+1=14, now 4+2+7+9=22
Step 4: Update [0,7]: was 36, now 36+8=44
```

After update, the tree looks like:

```
                          [0,7]: 44              (was 36, now +8)
                        /             \
              [0,3]: 22               [4,7]: 22  (unchanged)
             /        \
         [0,1]: 6   [2,3]: 16         (was 8, now +8)
         /    \     /    \
       [0]:4 [1]:2 [2]:7 [3]:9        (was 1, now 9)
```

Nodes updated: 4 nodes. For a million-element array: at most **log₂(1,000,000) ≈ 20 nodes**.

```python
def update(node, start, end, idx, new_val):
    if start == end:
        tree[node] = new_val             # update the leaf
    else:
        mid = (start + end) // 2
        if idx <= mid:
            update(2*node, start, mid, idx, new_val)    # go left
        else:
            update(2*node+1, mid+1, end, idx, new_val)  # go right
        tree[node] = tree[2*node] + tree[2*node+1]      # update parent
```

---

## Segment Tree vs Prefix Sum: The Right Tool for the Job

Both structures answer range sum queries. Which one should you use?

### Prefix Sum

Build a running sum array: `prefix[i]` = sum of all elements from index 0 to i.

```
Array:   [4, 2, 7, 1, 5, 3, 8, 6]
Prefix:  [4, 6, 13, 14, 19, 22, 30, 36]

Query sum(2..5): prefix[5] - prefix[1] = 22 - 6 = 16. Correct! ← O(1) query
```

```
Update arr[3] from 1 to 9:
  prefix[3] changes from 14 to 22
  prefix[4] changes from 19 to 27
  prefix[5] changes from 22 to 30
  prefix[6] changes from 30 to 38
  prefix[7] changes from 36 to 44

All 5 positions after index 3 must be updated. ← O(n) update
```

### Comparison

```
Operation     | Prefix Sum    | Segment Tree
──────────────|───────────────|──────────────
Build         | O(n)          | O(n)
Range Query   | O(1)          | O(log n)
Point Update  | O(n)          | O(log n)
Space         | O(n)          | O(4n)
```

```
When to use Prefix Sum:
  ✓ You build the array once and never update it
  ✓ You need blazing-fast O(1) queries
  ✗ You can't handle updates efficiently

When to use Segment Tree:
  ✓ You have both queries AND updates mixed together
  ✓ O(log n) for both is acceptable
  ✓ The array changes frequently
  ✗ Overkill if you only have queries and no updates
```

**Real-world analogy:**
- **Prefix sum** is like a printed phonebook. Fast lookups, but every time someone's number changes, you reprint the whole book. Painful.
- **Segment tree** is like a live database. Slower than the phonebook for a single lookup, but updates are fast and everything stays current.

---

## What Else Can Segment Trees Store?

We used sum, but the structure works for any operation where you can combine answers from sub-ranges.

```
Common segment tree types:
──────────────────────────────────────────────────────────────
Type              | What leaf stores | How parent combines
──────────────────|──────────────────|──────────────────────
Sum tree          | arr[i]           | left + right
Min tree          | arr[i]           | min(left, right)
Max tree          | arr[i]           | max(left, right)
GCD tree          | arr[i]           | gcd(left, right)
Count tree        | count of 1s      | left + right
──────────────────────────────────────────────────────────────
```

Same code structure, just change the combine operation.

---

## Full Code Reference

```python
class SegmentTree:
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)    # 4n is safe upper bound for tree size
        self.build(arr, 1, 0, self.n - 1)

    def build(self, arr, node, start, end):
        if start == end:
            self.tree[node] = arr[start]
        else:
            mid = (start + end) // 2
            self.build(arr, 2*node,   start,   mid)
            self.build(arr, 2*node+1, mid+1,   end)
            self.tree[node] = self.tree[2*node] + self.tree[2*node+1]

    def query(self, node, start, end, l, r):
        if r < start or end < l:          # no overlap
            return 0
        if l <= start and end <= r:       # full overlap
            return self.tree[node]
        mid = (start + end) // 2          # partial overlap — split
        left  = self.query(2*node,   start, mid, l, r)
        right = self.query(2*node+1, mid+1, end, l, r)
        return left + right

    def update(self, node, start, end, idx, new_val):
        if start == end:
            self.tree[node] = new_val
        else:
            mid = (start + end) // 2
            if idx <= mid:
                self.update(2*node,   start, mid, idx, new_val)
            else:
                self.update(2*node+1, mid+1, end, idx, new_val)
            self.tree[node] = self.tree[2*node] + self.tree[2*node+1]

    def range_sum(self, l, r):
        return self.query(1, 0, self.n - 1, l, r)

    def point_update(self, idx, new_val):
        self.update(1, 0, self.n - 1, idx, new_val)


# Usage
arr = [4, 2, 7, 1, 5, 3, 8, 6]
st = SegmentTree(arr)

print(st.range_sum(2, 5))    # 7+1+5+3 = 16
st.point_update(3, 9)        # arr[3] = 9
print(st.range_sum(2, 5))    # 7+9+5+3 = 24
```

---

## The One-Sentence Summary

A segment tree is a tournament bracket that stores every intermediate result, letting you
answer range queries and process updates in O(log n) — the sweet spot when your data
changes and you need both fast queries and fast updates.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
