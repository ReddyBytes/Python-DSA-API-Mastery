# Segment Tree — Common Mistakes

> "A segment tree is like a well-run government: every level delegates to the level below it, and if the communication breaks down anywhere, the whole system gives wrong answers."

This file walks through the 8 most painful, most common, most "I-spent-3-hours-on-this" mistakes people make when implementing segment trees. Each one is explained with a story, shown with broken code, traced through the failure, and then fixed.

---

## Table of Contents

1. [1-Indexed vs 0-Indexed Confusion](#mistake-1)
2. [Wrong Tree Size (2n Instead of 4n)](#mistake-2)
3. [Forgetting to Propagate Lazy Updates](#mistake-3)
4. [Off-by-One in Build and Query Range](#mistake-4)
5. [Not Handling Partial Overlap](#mistake-5)
6. [Using Segment Tree When BIT Is Sufficient](#mistake-6)
7. [Non-Associative Merge Function](#mistake-7)
8. [Point Update vs Range Update Confusion](#mistake-8)

---

## Mistake 1: 1-Indexed vs 0-Indexed Confusion {#mistake-1}

### The Story

Imagine you're in a library. The librarian uses a numbering system where shelf 1 is the first shelf. But you — having grown up programming in Python — keep trying to grab book from shelf 0. Sometimes you get the wrong book, sometimes you crash the whole system.

Segment trees have two valid "coordinate systems": 1-indexed (root at position 1, children at `2*i` and `2*i+1`) and 0-indexed (root at position 0, children at `2*i+1` and `2*i+2`). Both are valid. The catastrophic mistake is starting in one world and accidentally crossing over into the other.

### Why This Exists

The 1-indexed version is extremely elegant for tree navigation:

```
Node i's left child  → 2*i
Node i's right child → 2*i + 1
Node i's parent      → i // 2
```

This works because at index 1 (root), `2*1 = 2` (left) and `2*1+1 = 3` (right). The math is clean.

In 0-indexed:
```
Node i's left child  → 2*i + 1
Node i's right child → 2*i + 2
Node i's parent      → (i - 1) // 2
```

Slightly more complex, but also valid.

### ASCII Diagram: Tree Layouts

**1-Indexed Layout** (most tutorials use this):
```
Array: [_, root, L, R, LL, LR, RL, RR, ...]
Index:  0    1   2  3   4   5   6   7

Tree visual:
              [1]
            /     \
          [2]     [3]
         /   \   /   \
       [4]  [5] [6]  [7]
```

**0-Indexed Layout:**
```
Array: [root, L, R, LL, LR, RL, RR, ...]
Index:    0   1  2   3   4   5   6

Tree visual:
              [0]
            /     \
          [1]     [2]
         /   \   /   \
       [3]  [4] [5]  [6]
```

### WRONG Code: Mixing the Two Systems

```python
# WRONG: Building with 1-indexed logic, then querying with 0-indexed logic

def build_wrong(arr, tree, node, start, end):
    # This function uses 1-indexed (node starts at 1)
    if start == end:
        tree[node] = arr[start]
    else:
        mid = (start + end) // 2
        build_wrong(arr, tree, 2 * node, start, mid)      # left child at 2*node
        build_wrong(arr, tree, 2 * node + 1, mid + 1, end) # right child at 2*node+1
        tree[node] = tree[2 * node] + tree[2 * node + 1]

def query_wrong(tree, node, start, end, l, r):
    # BUG: This function accidentally uses 0-indexed child formula!
    if r < start or end < l:
        return 0
    if l <= start and end <= r:
        return tree[node]
    mid = (start + end) // 2
    # BUG: left child is 2*node+1, right is 2*node+2 (0-indexed formula)
    left  = query_wrong(tree, 2 * node + 1, start, mid, l, r)   # WRONG!
    right = query_wrong(tree, 2 * node + 2, mid + 1, end, l, r) # WRONG!
    return left + right

# Test it
arr = [1, 2, 3, 4]
n = len(arr)
tree = [0] * (4 * n)
build_wrong(arr, tree, 1, 0, n - 1)  # Build with 1-indexed root

print("Tree after build:", tree[:10])
# Tree looks correct:  [0, 10, 3, 7, 1, 2, 3, 4, 0, 0]
#                       ^                                 ^-- index 0 unused

result = query_wrong(tree, 1, 0, n - 1, 0, 3)  # sum of all
print("Sum of all (expected 10, got):", result)
# The query navigates to wrong indices because it uses 0-indexed children
# starting from node=1 (which should be 1-indexed root)
```

### Trace of the Bug

Let's trace `query_wrong(tree, 1, 0, 3, 0, 3)`:

```
Call: node=1, start=0, end=3, l=0, r=3
  → l<=start and end<=r? YES (0<=0 and 3<=3)
  → return tree[1] = 10   ← Actually this works here, but watch what happens
                            if we ask for a partial range...

Call: query_wrong(tree, 1, 0, 3, 0, 1)  # sum of first two elements
  mid = 1
  left  = query_wrong(tree, 2*1+1=3, 0, 1, 0, 1)  # node=3
  right = query_wrong(tree, 2*1+2=4, 2, 3, 0, 1)  # node=4

# But wait — in our 1-indexed tree, node 3 holds tree[3] = 7 (which is sum of [3,4])
# and node 4 holds tree[4] = 1 (which is arr[0] = 1)
# The LEFT subtree of the ROOT in 1-indexed is node 2, not node 3!

# So we read tree[3] (value 7) as the left subtree of root — WRONG!
# tree[3] = 7 = sum(arr[2], arr[3]) = 3 + 4
# But we want sum(arr[0], arr[1]) = 1 + 2 = 3

# Result will be 7 (wrong), expected 3
```

### RIGHT Code: Consistent 1-Indexed

```python
# CORRECT: Everything uses 1-indexed convention consistently

class SegmentTree1Indexed:
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)
        self.build(arr, 1, 0, self.n - 1)

    def build(self, arr, node, start, end):
        """Build tree. node starts at 1 (root)."""
        if start == end:
            self.tree[node] = arr[start]
        else:
            mid = (start + end) // 2
            # 1-indexed: left child = 2*node, right child = 2*node+1
            self.build(arr, 2 * node, start, mid)
            self.build(arr, 2 * node + 1, mid + 1, end)
            self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def query(self, node, start, end, l, r):
        """Query sum in range [l, r]. node starts at 1."""
        if r < start or end < l:
            return 0
        if l <= start and end <= r:
            return self.tree[node]
        mid = (start + end) // 2
        # 1-indexed: left child = 2*node, right child = 2*node+1
        left  = self.query(2 * node, start, mid, l, r)
        right = self.query(2 * node + 1, mid + 1, end, l, r)
        return left + right

    def update(self, node, start, end, idx, val):
        """Point update at index idx. node starts at 1."""
        if start == end:
            self.tree[node] = val
        else:
            mid = (start + end) // 2
            if idx <= mid:
                self.update(2 * node, start, mid, idx, val)
            else:
                self.update(2 * node + 1, mid + 1, end, idx, val)
            self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]


# CORRECT: Everything uses 0-indexed convention consistently

class SegmentTree0Indexed:
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)
        self.build(arr, 0, 0, self.n - 1)

    def build(self, arr, node, start, end):
        """Build tree. node starts at 0 (root)."""
        if start == end:
            self.tree[node] = arr[start]
        else:
            mid = (start + end) // 2
            # 0-indexed: left child = 2*node+1, right child = 2*node+2
            self.build(arr, 2 * node + 1, start, mid)
            self.build(arr, 2 * node + 2, mid + 1, end)
            self.tree[node] = self.tree[2 * node + 1] + self.tree[2 * node + 2]

    def query(self, node, start, end, l, r):
        """Query sum in range [l, r]. node starts at 0."""
        if r < start or end < l:
            return 0
        if l <= start and end <= r:
            return self.tree[node]
        mid = (start + end) // 2
        # 0-indexed: left child = 2*node+1, right child = 2*node+2
        left  = self.query(2 * node + 1, start, mid, l, r)
        right = self.query(2 * node + 2, mid + 1, end, l, r)
        return left + right


# Test both
arr = [1, 2, 3, 4]

st1 = SegmentTree1Indexed(arr)
print("1-indexed sum [0,3]:", st1.query(1, 0, 3, 0, 3))  # 10
print("1-indexed sum [0,1]:", st1.query(1, 0, 3, 0, 1))  # 3
print("1-indexed sum [2,3]:", st1.query(1, 0, 3, 2, 3))  # 7

st0 = SegmentTree0Indexed(arr)
print("0-indexed sum [0,3]:", st0.query(0, 0, 3, 0, 3))  # 10
print("0-indexed sum [0,1]:", st0.query(0, 0, 3, 0, 1))  # 3
print("0-indexed sum [2,3]:", st0.query(0, 0, 3, 2, 3))  # 7
```

### The Golden Rule

Pick one system. Tattoo it on your brain. Never mix. Add a comment at the top of every segment tree implementation stating which convention it uses.

---

## Mistake 2: Wrong Tree Size (Using 2n Instead of 4n) {#mistake-2}

### The Story

You're packing a suitcase. You measure the clothes and say "I need exactly this much space." But then you realize you also need room for the lining, the dividers, and a little extra for compression. Segment trees are the same — the tree array needs more space than you intuitively think.

### Why 4n?

Given an array of size `n`, the segment tree has at most `2 * 2^(ceil(log2(n)))` nodes.

Let's think about it:
- For `n = 4`: next power of 2 is 4, tree needs `2*4 = 8` nodes → fine with `2*n`
- For `n = 5`: next power of 2 is 8, tree needs `2*8 = 16` nodes → `2*n = 10` is NOT ENOUGH!
- For `n = 6`: next power of 2 is 8, tree needs `2*8 = 16` nodes → `2*n = 12` NOT ENOUGH!

The worst case is when `n` is just above a power of 2 (e.g., `n = 2^k + 1`). In that case, the tree depth is `k+1`, and the bottom level can have up to `2^(k+1)` nodes. That's almost `2*n`. Add the rest of the tree and you need up to `4*n`.

**Safe rule: always allocate `4*n`.**

```
n=1:   tree needs  2 nodes  (4*1=4, safe)
n=2:   tree needs  4 nodes  (4*2=8, safe)
n=3:   tree needs  8 nodes  (4*3=12, safe)
n=4:   tree needs  8 nodes  (4*4=16, safe)
n=5:   tree needs 16 nodes  (4*5=20, safe)
n=6:   tree needs 16 nodes  (4*6=24, safe)
n=7:   tree needs 16 nodes  (4*7=28, safe)
n=8:   tree needs 16 nodes  (4*8=32, safe)
n=9:   tree needs 32 nodes  (4*9=36, safe)
```

### ASCII Diagram: Why n=5 Needs 16 Nodes

```
Array: [a, b, c, d, e]  (n=5)
Next power of 2 above 5 = 8

Tree must accommodate as if n=8 at the bottom level:

Level 0 (root):          [0,4]                         <- 1 node
Level 1:         [0,2]           [3,4]                 <- 2 nodes
Level 2:     [0,1]   [2,2]   [3,3]   [4,4]             <- 4 nodes
Level 3:  [0,0][1,1]   -       -       -               <- up to 8 nodes

Tree indices used (1-indexed):
1, 2, 3, 4, 5, 6, 7, 8, 9, ...

But because of how recursion splits, node 12, 13 etc. can be reached
even though they correspond to "phantom" leaves.
```

### WRONG Code: Using 2n

```python
def build_wrong_size(arr, tree, node, start, end):
    if start == end:
        tree[node] = arr[start]  # IndexError lurking here for large n!
    else:
        mid = (start + end) // 2
        build_wrong_size(arr, tree, 2 * node, start, mid)
        build_wrong_size(arr, tree, 2 * node + 1, mid + 1, end)
        tree[node] = tree[2 * node] + tree[2 * node + 1]

arr = [1, 2, 3, 4, 5]  # n=5
n = len(arr)
tree = [0] * (2 * n)   # BUG: Only 10 slots! Need 20 (4*n)

try:
    build_wrong_size(arr, tree, 1, 0, n - 1)
except IndexError as e:
    print(f"IndexError: {e}")
    print("The tree tried to write to an index beyond 2*n!")

# Trace of what happens:
# build(1, 0, 4)
#   build(2, 0, 2)
#     build(4, 0, 1)
#       build(8, 0, 0)  → tree[8] = arr[0] ← index 8 in a size-10 array, OK
#       build(9, 1, 1)  → tree[9] = arr[1] ← index 9, OK
#     build(5, 2, 2)    → tree[5] = arr[2] ← OK
#   build(3, 3, 4)
#     build(6, 3, 3)    → tree[6] = arr[3] ← OK
#     build(7, 4, 4)    → tree[7] = arr[4] ← OK
# So n=5 actually works with 10 slots? Let's try n=6...

arr2 = [1, 2, 3, 4, 5, 6]  # n=6
n2 = len(arr2)
tree2 = [0] * (2 * n2)  # Only 12 slots

try:
    build_wrong_size(arr2, tree2, 1, 0, n2 - 1)
    print("n=6 worked (but got lucky with this specific split)")
except IndexError as e:
    print(f"n=6 IndexError: {e}")

# The real problem: for some n values, recursion reaches indices > 2*n
# n=1: max index = 1                (need 2, have 2: OK)
# n=2: max index = 3                (need 4, have 4: OK)
# n=3: max index = 7 (0,1 -> 2,3 -> 4,5,6,7)  (need 8, have 6: CRASH)
arr3 = [10, 20, 30]  # n=3
n3 = len(arr3)
tree3 = [0] * (2 * n3)  # Only 6 slots

try:
    build_wrong_size(arr3, tree3, 1, 0, n3 - 1)
    print("n=3 Result:", tree3)
except IndexError as e:
    print(f"n=3 IndexError at: {e}")
```

### Trace of n=3 Crash

```
build(node=1, start=0, end=2)
  mid = 1
  build(node=2, start=0, end=1)
    mid = 0
    build(node=4, start=0, end=0)  → tree[4] = arr[0] = 10
    build(node=5, start=1, end=1)  → tree[5] = arr[1] = 20
    tree[2] = tree[4] + tree[5] = 30
  build(node=3, start=2, end=2)    → tree[3] = arr[2] = 30
  tree[1] = tree[2] + tree[3] = 60

BUT tree3 only has indices 0..5 (size 6).
tree[4] and tree[5] are within bounds HERE,
but for n=3, we used index 5, which is 2*n-1 = 5. Tight!

Now consider n=3 with a differently shaped split where one branch
goes deeper: the indices 4 and 5 are already at the boundary.
If n were slightly different, you'd exceed the bound.

The SAFE rule: ALWAYS use 4*n.
```

### RIGHT Code: Using 4n

```python
def build_correct(arr, tree, node, start, end):
    if start == end:
        tree[node] = arr[start]
    else:
        mid = (start + end) // 2
        build_correct(arr, tree, 2 * node, start, mid)
        build_correct(arr, tree, 2 * node + 1, mid + 1, end)
        tree[node] = tree[2 * node] + tree[2 * node + 1]

def query_correct(tree, node, start, end, l, r):
    if r < start or end < l:
        return 0
    if l <= start and end <= r:
        return tree[node]
    mid = (start + end) // 2
    left  = query_correct(tree, 2 * node, start, mid, l, r)
    right = query_correct(tree, 2 * node + 1, mid + 1, end, l, r)
    return left + right

# Test with various sizes — all safe with 4*n
for arr in [[10, 20, 30], [1,2,3,4,5], [1,2,3,4,5,6,7], [42]]:
    n = len(arr)
    tree = [0] * (4 * n)  # ALWAYS 4*n
    build_correct(arr, tree, 1, 0, n - 1)
    total = query_correct(tree, 1, 0, n - 1, 0, n - 1)
    expected = sum(arr)
    print(f"n={n}, sum={total}, expected={expected}, OK={total == expected}")
```

---

## Mistake 3: Forgetting to Propagate Lazy Updates {#mistake-3}

### The Story

Imagine you're a manager with a team. You receive an order: "Give everyone a $100 raise." You note it on a sticky note on the department board but don't actually update individual records. Then someone queries "What is Alice's salary?" Your system checks Alice's record (which hasn't been updated) and returns the old value. The sticky note is just sitting there, ignored.

That sticky note is the lazy tag. And the mistake is forgetting to push it down before you look at children.

### What is Lazy Propagation?

In a segment tree with range updates, you often mark a whole segment as "add 5 to all elements in this range" without immediately updating all child nodes. This is the "lazy" part — you defer work.

When you later query or update a sub-range that overlaps, you must first "push down" the pending lazy update to the children. Forgetting this means children still show stale values.

### ASCII Diagram: Lazy Tag Not Pushed

```
Array: [1, 1, 1, 1]
Add 10 to range [0, 3] → lazy tag of +10 on root

BEFORE PUSH:
           [root: sum=4, lazy=+10]
           /                    \
    [sum=2, lazy=0]      [sum=2, lazy=0]
    /          \          /          \
[1, lazy=0] [1,lazy=0] [1,lazy=0] [1,lazy=0]

CORRECT AFTER PUSH:
           [root: sum=44, lazy=0]   ← root updated
           /                    \
  [sum=22, lazy=+10]    [sum=22, lazy=+10]   ← lazy pushed down
    /          \          /          \
[1, lazy=0] [1,lazy=0] [1,lazy=0] [1,lazy=0]  ← not yet pushed (deferred)

If you query root: 44 ✓
If you query left child: 22 ✓ (its lazy will push further when needed)
If you query left-left child WITHOUT pushing left child's lazy first:
  → returns tree[left-left] = 1, NOT 11  ← WRONG!
```

### WRONG Code: Missing Push-Down

```python
# WRONG: Lazy segment tree that forgets to push lazy before recursing

class LazySegTreeWrong:
    def __init__(self, n):
        self.n = n
        self.tree = [0] * (4 * n)
        self.lazy = [0] * (4 * n)

    def build(self, arr, node, start, end):
        if start == end:
            self.tree[node] = arr[start]
            return
        mid = (start + end) // 2
        self.build(arr, 2 * node, start, mid)
        self.build(arr, 2 * node + 1, mid + 1, end)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def range_update(self, node, start, end, l, r, val):
        if r < start or end < l:
            return
        if l <= start and end <= r:
            # Mark this node with lazy
            self.tree[node] += val * (end - start + 1)
            self.lazy[node] += val
            return

        # BUG: We recursed into children WITHOUT pushing lazy down first!
        # If this node has pending lazy, children are getting stale data
        mid = (start + end) // 2
        self.range_update(2 * node, start, mid, l, r, val)
        self.range_update(2 * node + 1, mid + 1, end, l, r, val)
        # BUG: We also don't apply self.lazy[node] before re-computing parent
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def query(self, node, start, end, l, r):
        if r < start or end < l:
            return 0
        if l <= start and end <= r:
            return self.tree[node]

        # BUG: No push-down here either! Children may have stale lazy
        mid = (start + end) // 2
        left  = self.query(2 * node, start, mid, l, r)
        right = self.query(2 * node + 1, mid + 1, end, l, r)
        return left + right


# Demonstrate the bug
arr = [1, 1, 1, 1]
n = 4
wrong_st = LazySegTreeWrong(n)
wrong_st.build(arr, 1, 0, n - 1)

print("Initial sum [0,3]:", wrong_st.query(1, 0, n-1, 0, 3))  # 4 ✓

# Add 10 to all elements
wrong_st.range_update(1, 0, n-1, 0, 3, 10)
print("After +10 to all, sum [0,3]:", wrong_st.query(1, 0, n-1, 0, 3))  # Should be 44

# Now add 5 to first two elements
wrong_st.range_update(1, 0, n-1, 0, 1, 5)
print("After +5 to [0,1], sum [0,3]:", wrong_st.query(1, 0, n-1, 0, 3))  # Should be 54

# Query individual elements
print("Element 0 (expected 16):", wrong_st.query(1, 0, n-1, 0, 0))  # May be wrong!
print("Element 1 (expected 16):", wrong_st.query(1, 0, n-1, 1, 1))  # May be wrong!
print("Element 2 (expected 11):", wrong_st.query(1, 0, n-1, 2, 2))  # May be wrong!
```

### RIGHT Code: With Proper Push-Down

```python
class LazySegTreeCorrect:
    def __init__(self, n):
        self.n = n
        self.tree = [0] * (4 * n)
        self.lazy = [0] * (4 * n)

    def build(self, arr, node, start, end):
        if start == end:
            self.tree[node] = arr[start]
            return
        mid = (start + end) // 2
        self.build(arr, 2 * node, start, mid)
        self.build(arr, 2 * node + 1, mid + 1, end)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def _push_down(self, node, start, end):
        """Push pending lazy update to children. MUST call before recursing."""
        if self.lazy[node] != 0:
            mid = (start + end) // 2
            left, right = 2 * node, 2 * node + 1

            # Apply lazy to both children
            self.tree[left]  += self.lazy[node] * (mid - start + 1)
            self.tree[right] += self.lazy[node] * (end - mid)

            # Propagate lazy tag to children
            self.lazy[left]  += self.lazy[node]
            self.lazy[right] += self.lazy[node]

            # Clear current node's lazy (it's been pushed down)
            self.lazy[node] = 0

    def range_update(self, node, start, end, l, r, val):
        if r < start or end < l:
            return
        if l <= start and end <= r:
            # Fully covered: update this node and mark lazy
            self.tree[node] += val * (end - start + 1)
            self.lazy[node] += val
            return

        # Partially covered: PUSH DOWN FIRST, then recurse
        self._push_down(node, start, end)  # ← THIS IS THE KEY LINE

        mid = (start + end) // 2
        self.range_update(2 * node, start, mid, l, r, val)
        self.range_update(2 * node + 1, mid + 1, end, l, r, val)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def query(self, node, start, end, l, r):
        if r < start or end < l:
            return 0
        if l <= start and end <= r:
            return self.tree[node]

        # PUSH DOWN BEFORE RECURSING INTO CHILDREN
        self._push_down(node, start, end)  # ← KEY LINE

        mid = (start + end) // 2
        left  = self.query(2 * node, start, mid, l, r)
        right = self.query(2 * node + 1, mid + 1, end, l, r)
        return left + right


# Test
arr = [1, 1, 1, 1]
n = 4
st = LazySegTreeCorrect(n)
st.build(arr, 1, 0, n - 1)

st.range_update(1, 0, n-1, 0, 3, 10)  # +10 to all
print("Sum [0,3]:", st.query(1, 0, n-1, 0, 3))  # 44 ✓

st.range_update(1, 0, n-1, 0, 1, 5)   # +5 to [0,1]
print("Sum [0,3]:", st.query(1, 0, n-1, 0, 3))  # 54 ✓

print("Element 0:", st.query(1, 0, n-1, 0, 0))  # 16 ✓ (1+10+5)
print("Element 1:", st.query(1, 0, n-1, 1, 1))  # 16 ✓ (1+10+5)
print("Element 2:", st.query(1, 0, n-1, 2, 2))  # 11 ✓ (1+10)
print("Element 3:", st.query(1, 0, n-1, 3, 3))  # 11 ✓ (1+10)
```

---

## Mistake 4: Off-by-One in Build and Query Range {#mistake-4}

### The Story

You're slicing a sandwich. "Give me slices 2 through 4." Does that mean slice 4 is included? Depends on who you ask. This ambiguity — inclusive vs exclusive — is the source of off-by-one bugs everywhere, and segment trees are no exception.

The key boundary moment in a segment tree is the leaf condition: `if start == end`. This assumes **inclusive** boundaries. If you accidentally use exclusive boundaries in one place, the recursion either bottoms out too early or too late.

### Walk-Through: Building [4, 2, 7, 1]

**Correct build with inclusive [start, end]:**

```
build(node=1, start=0, end=3)
  mid = (0+3)//2 = 1
  build(node=2, start=0, end=1)
    mid = (0+1)//2 = 0
    build(node=4, start=0, end=0) → LEAF: tree[4] = arr[0] = 4
    build(node=5, start=1, end=1) → LEAF: tree[5] = arr[1] = 2
    tree[2] = 4 + 2 = 6
  build(node=3, start=2, end=3)
    mid = (2+3)//2 = 2
    build(node=6, start=2, end=2) → LEAF: tree[6] = arr[2] = 7
    build(node=7, start=3, end=3) → LEAF: tree[7] = arr[3] = 1
    tree[3] = 7 + 1 = 8
  tree[1] = 6 + 8 = 14
```

```
Tree:      [_, 14,  6,  8,  4,  2,  7,  1]
Index:      0   1   2   3   4   5   6   7
```

### WRONG Code: Off-by-One in mid Calculation

```python
def build_offbyone(arr, tree, node, start, end):
    if start == end:
        tree[node] = arr[start]
        return
    # BUG: Wrong mid — this can cause unbalanced splits or infinite recursion
    mid = (start + end) // 2 + 1  # Off by one!
    build_offbyone(arr, tree, 2 * node, start, mid)        # left gets extra element
    build_offbyone(arr, tree, 2 * node + 1, mid + 1, end)  # right loses an element
    tree[node] = tree[2 * node] + tree[2 * node + 1]

arr = [4, 2, 7, 1]
n = len(arr)
tree = [0] * (4 * n)

# Trace with wrong mid:
# build(1, 0, 3): mid = 2 (instead of 1)
#   build(2, 0, 2): handles 3 elements [4,2,7]
#     mid = 2
#     build(4, 0, 2): handles 3 elements again! → infinite recursion risk
```

### WRONG Code: Wrong Query Boundary

```python
def query_offbyone(tree, node, start, end, l, r):
    # BUG: Using exclusive right boundary (r is exclusive)
    # but tree was built with inclusive boundaries
    if r <= start or end < l:   # BUG: should be r < start
        return 0
    if l <= start and end < r:  # BUG: should be end <= r (inclusive)
        return tree[node]
    mid = (start + end) // 2
    left  = query_offbyone(tree, 2 * node, start, mid, l, r)
    right = query_offbyone(tree, 2 * node + 1, mid + 1, end, l, r)
    return left + right

# This will miss the last element when querying full range
# query(1, 0, 3, 0, 3):
#   r <= start? 3 <= 0? No
#   end < l? 3 < 0? No
#   l <= start and end < r? 0 <= 0 and 3 < 3? NO (3 < 3 is false!)
#   So it won't return tree[1] directly, will recurse...
#   Eventually, query on node=7 (start=3, end=3):
#     l <= start and end < r? 0 <= 3 and 3 < 3? NO (3 < 3 is false!)
#     So it recurses on a leaf... causing infinite recursion or wrong result

arr = [4, 2, 7, 1]
n = len(arr)
tree = [0] * (4 * n)

def build_correct_for_test(arr, tree, node, start, end):
    if start == end:
        tree[node] = arr[start]
        return
    mid = (start + end) // 2
    build_correct_for_test(arr, tree, 2 * node, start, mid)
    build_correct_for_test(arr, tree, 2 * node + 1, mid + 1, end)
    tree[node] = tree[2 * node] + tree[2 * node + 1]

build_correct_for_test(arr, tree, 1, 0, n - 1)
# Now query with wrong boundaries:
# query_offbyone might return wrong sum or recurse infinitely
```

### RIGHT Code: Correct Inclusive Boundaries

```python
def build(arr, tree, node, start, end):
    """Build segment tree. start and end are INCLUSIVE."""
    if start == end:
        # Leaf node: single element
        tree[node] = arr[start]
        return
    mid = (start + end) // 2  # Split point: left=[start,mid], right=[mid+1,end]
    build(arr, tree, 2 * node, start, mid)
    build(arr, tree, 2 * node + 1, mid + 1, end)
    tree[node] = tree[2 * node] + tree[2 * node + 1]

def query(tree, node, start, end, l, r):
    """Query range [l, r] (INCLUSIVE on both ends)."""
    # No overlap: current segment is entirely outside [l, r]
    if r < start or end < l:
        return 0
    # Full overlap: current segment is entirely inside [l, r]
    if l <= start and end <= r:
        return tree[node]
    # Partial overlap: split and recurse
    mid = (start + end) // 2
    left  = query(tree, 2 * node, start, mid, l, r)
    right = query(tree, 2 * node + 1, mid + 1, end, l, r)
    return left + right

# Verify with [4, 2, 7, 1]
arr = [4, 2, 7, 1]
n = len(arr)
tree = [0] * (4 * n)
build(arr, tree, 1, 0, n - 1)

print("Tree:", tree[:8])      # [0, 14, 6, 8, 4, 2, 7, 1]
print("Sum [0,3]:", query(tree, 1, 0, n-1, 0, 3))  # 14 ✓
print("Sum [0,1]:", query(tree, 1, 0, n-1, 0, 1))  # 6  ✓
print("Sum [1,3]:", query(tree, 1, 0, n-1, 1, 3))  # 10 ✓
print("Sum [2,2]:", query(tree, 1, 0, n-1, 2, 2))  # 7  ✓
```

---

## Mistake 5: Not Handling Partial Overlap {#mistake-5}

### The Story

A restaurant takes a reservation for tables 3 through 7. Table 5 is already booked. The naive waiter says "well, some of tables 3-7 are available, let me just return the available ones." But they forget to check table 5! Partial overlaps require checking BOTH sides — you can't skip either branch.

### The Three Cases in Segment Tree Query/Update

Every recursive call falls into exactly one of three cases:

```
1. NO overlap:     [l, r] and [start, end] don't touch → return identity
2. FULL overlap:   [start, end] is entirely within [l, r] → use this node
3. PARTIAL overlap: some part overlaps → RECURSE INTO BOTH CHILDREN
```

The bug: handling case 3 by only recursing into one child (the one that "looks more relevant").

### WRONG Code: Skipping a Child in Partial Overlap

```python
def update_wrong_partial(tree, node, start, end, l, r, val):
    """Range update: add val to arr[l..r]. BUG: skips child on partial overlap."""
    if r < start or end < l:
        return
    if l <= start and end <= r:
        tree[node] += val * (end - start + 1)
        return

    # Partial overlap: BUG — only recurses into the child that starts with l
    mid = (start + end) // 2
    if l <= mid:
        # Only go left if l is in left half
        update_wrong_partial(tree, 2 * node, start, mid, l, r, val)
    else:
        # Only go right if l is in right half
        update_wrong_partial(tree, 2 * node + 1, mid + 1, end, l, r, val)

    # BUG: In partial overlap, BOTH children might be affected!
    # Example: update [1, 2] on tree covering [0, 3]
    #   mid = 1, l=1, r=2
    #   l <= mid? 1 <= 1? YES → only go left
    #   But the right half [2,3] is ALSO partly in [1,2]!
    tree[node] = tree[2 * node] + tree[2 * node + 1]

arr = [0, 0, 0, 0]
n = len(arr)
tree = [0] * (4 * n)

def build_zero(arr, tree, node, start, end):
    if start == end:
        tree[node] = arr[start]
        return
    mid = (start + end) // 2
    build_zero(arr, tree, 2*node, start, mid)
    build_zero(arr, tree, 2*node+1, mid+1, end)
    tree[node] = tree[2*node] + tree[2*node+1]

build_zero(arr, tree, 1, 0, n-1)

# Add 5 to range [1, 2] (indices 1 and 2)
update_wrong_partial(tree, 1, 0, n-1, 1, 2, 5)

def query_sum(tree, node, start, end, l, r):
    if r < start or end < l: return 0
    if l <= start and end <= r: return tree[node]
    mid = (start + end) // 2
    return query_sum(tree, 2*node, start, mid, l, r) + \
           query_sum(tree, 2*node+1, mid+1, end, l, r)

# Expected: arr[1] = 5, arr[2] = 5, total in [1,2] = 10
print("Sum [1,2] (expected 10):", query_sum(tree, 1, 0, n-1, 1, 2))
# BUG: Only index 1 got updated (5), index 2 was skipped → returns 5, not 10
```

### RIGHT Code: Always Recurse Both Children on Partial Overlap

```python
def update_correct_partial(tree, node, start, end, l, r, val):
    """Range update: add val to arr[l..r]. Correct partial overlap handling."""
    if r < start or end < l:
        return
    if l <= start and end <= r:
        tree[node] += val * (end - start + 1)
        return

    # Partial overlap: MUST recurse into BOTH children
    mid = (start + end) // 2
    update_correct_partial(tree, 2 * node, start, mid, l, r, val)      # LEFT
    update_correct_partial(tree, 2 * node + 1, mid + 1, end, l, r, val) # RIGHT
    # Both get called regardless; the no-overlap base case stops them if needed
    tree[node] = tree[2 * node] + tree[2 * node + 1]

arr = [0, 0, 0, 0]
n = len(arr)
tree = [0] * (4 * n)
build_zero(arr, tree, 1, 0, n-1)

update_correct_partial(tree, 1, 0, n-1, 1, 2, 5)
print("Sum [1,2] (expected 10):", query_sum(tree, 1, 0, n-1, 1, 2))  # 10 ✓
print("Sum [0,3] (expected 10):", query_sum(tree, 1, 0, n-1, 0, 3))  # 10 ✓
print("Element 0 (expected 0):", query_sum(tree, 1, 0, n-1, 0, 0))   # 0  ✓
print("Element 1 (expected 5):", query_sum(tree, 1, 0, n-1, 1, 1))   # 5  ✓
print("Element 2 (expected 5):", query_sum(tree, 1, 0, n-1, 2, 2))   # 5  ✓
print("Element 3 (expected 0):", query_sum(tree, 1, 0, n-1, 3, 3))   # 0  ✓
```

### Visual: Partial Overlap Must Go Both Ways

```
Range update [1, 2] on array [0, 0, 0, 0]:

Tree covering [0, 3]:
         [0,3]
        /     \
    [0,1]     [2,3]
    /   \     /   \
  [0]  [1]  [2]  [3]

Update [1, 2]:
  Root [0,3]: partial overlap with [1,2]
    → recurse LEFT to [0,1]: partial overlap (only index 1 in range)
      → recurse LEFT to [0]: no overlap → skip
      → recurse RIGHT to [1]: FULL overlap → update tree[1] += 5
    → recurse RIGHT to [2,3]: partial overlap (only index 2 in range)
      → recurse LEFT to [2]: FULL overlap → update tree[2] += 5
      → recurse RIGHT to [3]: no overlap → skip

WRONG approach would only go left from [0,3], missing index 2 entirely.
```

---

## Mistake 6: Using Segment Tree When BIT Is Sufficient {#mistake-6}

### The Story

You're trying to open a can of soup. A segment tree is a Swiss Army knife — versatile, powerful. A Fenwick (Binary Indexed) tree is a can opener — simple, fast, purpose-built. Using the Swiss Army knife to open soup is technically possible but unnecessarily complex. Know your tools.

### When to Use Each

| Operation | BIT (Fenwick) | Segment Tree |
|-----------|--------------|--------------|
| Point update, prefix sum query | Yes (simpler) | Yes (overkill) |
| Range update, range query | Possible but complex | Natural fit |
| Range min/max query | Not supported | Yes |
| Non-invertible aggregations (max, min) | No | Yes |
| Implementation complexity | ~15 lines | ~40 lines |
| Constant factor | Faster (bit ops) | Slower (recursion) |
| Space | O(n) | O(4n) |

### Complexity Comparison

```
                BIT         Segment Tree
Build:         O(n log n)   O(n)
Point Update:  O(log n)     O(log n)
Prefix Sum:    O(log n)     O(log n)
Range Sum:     O(log n)     O(log n)
Range Update:  O(log n)*    O(log n)*
Range Min/Max: NOT POSSIBLE O(log n)

*with difference array trick for BIT
```

### WRONG Code: Segment Tree for Pure Prefix Sum

```python
# WRONG: Over-engineering a simple prefix sum problem with segment tree

class HeavySegTree:
    """You don't need this for simple prefix sums."""
    def __init__(self, n):
        self.n = n
        self.tree = [0] * (4 * n)

    def update(self, node, start, end, idx, delta):
        if start == end:
            self.tree[node] += delta
            return
        mid = (start + end) // 2
        if idx <= mid:
            self.update(2*node, start, mid, idx, delta)
        else:
            self.update(2*node+1, mid+1, end, idx, delta)
        self.tree[node] = self.tree[2*node] + self.tree[2*node+1]

    def query(self, node, start, end, l, r):
        if r < start or end < l: return 0
        if l <= start and end <= r: return self.tree[node]
        mid = (start + end) // 2
        return self.query(2*node, start, mid, l, r) + \
               self.query(2*node+1, mid+1, end, l, r)

# 40+ lines, recursion overhead, 4x memory — for a problem BIT solves in 15 lines!
```

### RIGHT Code: BIT for Prefix Sums

```python
# CORRECT: Fenwick tree (BIT) for point update + range sum query

class BIT:
    """
    Fenwick Tree / Binary Indexed Tree.
    O(log n) point update, O(log n) prefix sum query.
    1-indexed internally.
    """
    def __init__(self, n):
        self.n = n
        self.tree = [0] * (n + 1)  # 1-indexed

    def update(self, i, delta):
        """Add delta to index i (0-indexed input)."""
        i += 1  # convert to 1-indexed
        while i <= self.n:
            self.tree[i] += delta
            i += i & (-i)  # move to parent

    def prefix_sum(self, i):
        """Sum of arr[0..i] inclusive (0-indexed input)."""
        i += 1  # convert to 1-indexed
        total = 0
        while i > 0:
            total += self.tree[i]
            i -= i & (-i)  # move to responsible ancestor
        return total

    def range_sum(self, l, r):
        """Sum of arr[l..r] inclusive."""
        if l == 0:
            return self.prefix_sum(r)
        return self.prefix_sum(r) - self.prefix_sum(l - 1)


# Same operations, much simpler:
bit = BIT(5)
arr = [3, 2, 1, 4, 5]
for i, v in enumerate(arr):
    bit.update(i, v)

print("Prefix sum [0,4]:", bit.range_sum(0, 4))  # 15 ✓
print("Range sum  [1,3]:", bit.range_sum(1, 3))  # 7  ✓

bit.update(2, 10 - 1)  # change arr[2] from 1 to 10 (add delta=9)
print("After update, range [0,4]:", bit.range_sum(0, 4))  # 24 ✓


# USE SEGMENT TREE WHEN YOU NEED:
def range_max_query_example():
    """BIT cannot do this. Segment tree is appropriate here."""
    arr = [3, 2, 1, 4, 5]
    n = len(arr)
    tree = [float('-inf')] * (4 * n)

    def build(node, start, end):
        if start == end:
            tree[node] = arr[start]
            return
        mid = (start + end) // 2
        build(2*node, start, mid)
        build(2*node+1, mid+1, end)
        tree[node] = max(tree[2*node], tree[2*node+1])  # MAX, not sum

    def query_max(node, start, end, l, r):
        if r < start or end < l: return float('-inf')
        if l <= start and end <= r: return tree[node]
        mid = (start + end) // 2
        return max(query_max(2*node, start, mid, l, r),
                   query_max(2*node+1, mid+1, end, l, r))

    build(1, 0, n-1)
    print("Max [1,3]:", query_max(1, 0, n-1, 1, 3))  # 4 ✓ (can't do with BIT)

range_max_query_example()
```

---

## Mistake 7: Non-Associative Merge Function {#mistake-7}

### The Story

A segment tree is essentially a tournament bracket. The champion at the top is the result of all the matches below. This only works if the "winning" rule is **consistent** regardless of order. If you define "winning" as the average of scores, you get a paradox: the average of two averages is NOT the same as the average of all participants. The bracket breaks.

### What Associativity Means

A binary operation `f` is associative if:
```
f(f(a, b), c) == f(a, f(b, c))
```

Examples:
- Addition: `(a+b)+c == a+(b+c)` ✓ Associative
- Max: `max(max(a,b),c) == max(a,max(b,c))` ✓ Associative
- GCD: `gcd(gcd(a,b),c) == gcd(a,gcd(b,c))` ✓ Associative
- Average: `avg(avg(a,b),c) != avg(a,avg(b,c))` in general ✗ NOT associative!
- Subtraction: `(a-b)-c != a-(b-c)` ✗ NOT associative

### WRONG Code: Average as Merge Function

```python
# WRONG: Using average as the merge function in a segment tree

def build_avg_wrong(arr, tree, node, start, end):
    if start == end:
        tree[node] = arr[start]
        return
    mid = (start + end) // 2
    build_avg_wrong(arr, tree, 2*node, start, mid)
    build_avg_wrong(arr, tree, 2*node+1, mid+1, end)
    # BUG: Average of averages is NOT the average of all elements
    tree[node] = (tree[2*node] + tree[2*node+1]) / 2

arr = [2, 4, 6, 8]   # True average = 5.0
n = len(arr)
tree = [0.0] * (4 * n)
build_avg_wrong(arr, tree, 1, 0, n-1)

# Let's trace:
# Level 2 nodes: avg(2,4)=3.0, avg(6,8)=7.0
# Level 1 (root): avg(3.0, 7.0) = 5.0
# OK in this case! But what about [1, 2, 3]?

arr2 = [1, 2, 3]  # True average = 2.0
n2 = len(arr2)
tree2 = [0.0] * (4 * n2)
build_avg_wrong(arr2, tree2, 1, 0, n2-1)

# Trace:
# build(1, 0, 2): mid=1
#   build(2, 0, 1): mid=0
#     build(4, 0, 0): tree[4] = 1
#     build(5, 1, 1): tree[5] = 2
#     tree[2] = avg(1, 2) = 1.5
#   build(3, 2, 2): tree[3] = 3
#   tree[1] = avg(1.5, 3) = 2.25   ← WRONG! True average = 2.0

print(f"Wrong average of [1,2,3]: {tree2[1]}")  # 2.25 (WRONG!)
print(f"True average of [1,2,3]: {sum([1,2,3])/3}")  # 2.0

# Even querying a sub-range [0,1] gives wrong results
def query_wrong_avg(tree, node, start, end, l, r):
    if r < start or end < l: return 0
    if l <= start and end <= r: return tree[node]
    mid = (start + end) // 2
    left  = query_wrong_avg(tree, 2*node, start, mid, l, r)
    right = query_wrong_avg(tree, 2*node+1, mid+1, end, l, r)
    return (left + right) / 2  # Still wrong for unequal-sized sub-ranges

# The fundamental issue: avg(L_avg, R_avg) only equals overall_avg when
# L and R have the SAME number of elements.
```

### RIGHT Code: Store Sum + Count, Compute Average

```python
# CORRECT: Store (sum, count) pairs — average can always be derived correctly

def build_avg_correct(arr, tree, node, start, end):
    """tree[node] = (sum, count) of the range [start, end]"""
    if start == end:
        tree[node] = (arr[start], 1)
        return
    mid = (start + end) // 2
    build_avg_correct(arr, tree, 2*node, start, mid)
    build_avg_correct(arr, tree, 2*node+1, mid+1, end)
    # Merge: sum sums, sum counts
    l_sum, l_cnt = tree[2*node]
    r_sum, r_cnt = tree[2*node+1]
    tree[node] = (l_sum + r_sum, l_cnt + r_cnt)

def query_avg_correct(tree, node, start, end, l, r):
    """Returns (sum, count) for range [l, r]."""
    if r < start or end < l: return (0, 0)
    if l <= start and end <= r: return tree[node]
    mid = (start + end) // 2
    l_sum, l_cnt = query_avg_correct(tree, 2*node, start, mid, l, r)
    r_sum, r_cnt = query_avg_correct(tree, 2*node+1, mid+1, end, l, r)
    return (l_sum + r_sum, l_cnt + r_cnt)

arr2 = [1, 2, 3]
n2 = len(arr2)
tree2 = [(0, 0)] * (4 * n2)
build_avg_correct(arr2, tree2, 1, 0, n2-1)

total_sum, total_count = query_avg_correct(tree2, 1, 0, n2-1, 0, n2-1)
print(f"Correct average of [1,2,3]: {total_sum/total_count}")  # 2.0 ✓

sub_sum, sub_count = query_avg_correct(tree2, 1, 0, n2-1, 0, 1)
print(f"Average of [1,2]: {sub_sum/sub_count}")  # 1.5 ✓


# CORRECT: GCD — genuinely associative, works naturally
import math

def build_gcd(arr, tree, node, start, end):
    if start == end:
        tree[node] = arr[start]
        return
    mid = (start + end) // 2
    build_gcd(arr, tree, 2*node, start, mid)
    build_gcd(arr, tree, 2*node+1, mid+1, end)
    tree[node] = math.gcd(tree[2*node], tree[2*node+1])

def query_gcd(tree, node, start, end, l, r):
    if r < start or end < l: return 0
    if l <= start and end <= r: return tree[node]
    mid = (start + end) // 2
    return math.gcd(query_gcd(tree, 2*node, start, mid, l, r),
                    query_gcd(tree, 2*node+1, mid+1, end, l, r))

arr_gcd = [12, 8, 6, 4]
n_gcd = len(arr_gcd)
tree_gcd = [0] * (4 * n_gcd)
build_gcd(arr_gcd, tree_gcd, 1, 0, n_gcd-1)

print("GCD [0,3]:", query_gcd(tree_gcd, 1, 0, n_gcd-1, 0, 3))  # 2 ✓
print("GCD [0,1]:", query_gcd(tree_gcd, 1, 0, n_gcd-1, 0, 1))  # 4 ✓
print("GCD [0,2]:", query_gcd(tree_gcd, 1, 0, n_gcd-1, 0, 2))  # 2 ✓
```

### Checklist: Is My Merge Function Valid?

```
Before using a function f as your segment tree merge:

1. Is f(f(a, b), c) == f(a, f(b, c))?  ← Must be YES (associativity)
2. Is there an identity element e such that f(a, e) == a? ← Needed for "no overlap" case
3. Does f operate only on the VALUES (not sizes) of sub-results? ← If no, store more info

Common safe operations: sum, max, min, GCD, LCM, XOR, AND, OR
Common unsafe operations: average, median, standard deviation, first-element
```

---

## Mistake 8: Point Update vs Range Update Confusion {#mistake-8}

### The Story

A barista takes orders. "Point update" is changing one customer's drink. "Range update" is telling everyone at table 5 that their drinks come with oat milk today. These are different operations and have different APIs. Calling the range-update function with point-update arguments — or vice versa — gives wrong results, no errors, just silent corruption.

### Two Different APIs

**Point update:** change a single element at index `i` to value `val`.
**Range update:** add `val` to all elements in range `[l, r]`.

The implementations are completely different. Point update traces a single path from root to leaf. Range update can mark entire segments with lazy tags.

### WRONG Code: Calling Range Update With Point-Update Semantics

```python
# This is the range update function (uses lazy propagation)
class LazyTree:
    def __init__(self, n):
        self.n = n
        self.tree = [0] * (4 * n)
        self.lazy = [0] * (4 * n)

    def build(self, arr, node, start, end):
        if start == end:
            self.tree[node] = arr[start]
            return
        mid = (start + end) // 2
        self.build(arr, 2*node, start, mid)
        self.build(arr, 2*node+1, mid+1, end)
        self.tree[node] = self.tree[2*node] + self.tree[2*node+1]

    def _push_down(self, node, start, end):
        if self.lazy[node]:
            mid = (start + end) // 2
            l, r = 2*node, 2*node+1
            self.tree[l] += self.lazy[node] * (mid - start + 1)
            self.tree[r] += self.lazy[node] * (end - mid)
            self.lazy[l] += self.lazy[node]
            self.lazy[r] += self.lazy[node]
            self.lazy[node] = 0

    def range_add(self, node, start, end, l, r, val):
        """Add val to ALL elements in [l, r]."""
        if r < start or end < l: return
        if l <= start and end <= r:
            self.tree[node] += val * (end - start + 1)
            self.lazy[node] += val
            return
        self._push_down(node, start, end)
        mid = (start + end) // 2
        self.range_add(2*node, start, mid, l, r, val)
        self.range_add(2*node+1, mid+1, end, l, r, val)
        self.tree[node] = self.tree[2*node] + self.tree[2*node+1]

    def query(self, node, start, end, l, r):
        if r < start or end < l: return 0
        if l <= start and end <= r: return self.tree[node]
        self._push_down(node, start, end)
        mid = (start + end) // 2
        return self.query(2*node, start, mid, l, r) + \
               self.query(2*node+1, mid+1, end, l, r)


arr = [1, 2, 3, 4, 5]
n = len(arr)
lt = LazyTree(n)
lt.build(arr, 1, 0, n-1)

# WRONG: User wants to SET arr[2] = 10 (point update)
# But calls range_add thinking it sets the value
# range_add(l=2, r=2, val=10) ADDS 10 to arr[2], not SETS it to 10
lt.range_add(1, 0, n-1, 2, 2, 10)  # User thinks: "set index 2 to 10"
# Actual effect: arr[2] = 3 + 10 = 13, not 10!

print("arr[2] (expected 10, got):", lt.query(1, 0, n-1, 2, 2))  # 13, not 10

# ALSO WRONG: Using point-update semantics on a lazy tree that expects range ops
def point_update_naive(tree, node, start, end, idx, new_val):
    """Wrong: sets the value, ignoring any pending lazy updates."""
    if start == end:
        tree[node] = new_val  # BUG: ignores lazy accumulated at this node!
        return
    mid = (start + end) // 2
    if idx <= mid:
        point_update_naive(tree, 2*node, start, mid, idx, new_val)
    else:
        point_update_naive(tree, 2*node+1, mid+1, end, idx, new_val)
    tree[node] = tree[2*node] + tree[2*node+1]  # BUG: lazy not pushed before this
```

### RIGHT Code: Two Separate Clean APIs

```python
class PointUpdateTree:
    """Segment tree for: point update + range sum query."""
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)
        self._build(arr, 1, 0, self.n - 1)

    def _build(self, arr, node, start, end):
        if start == end:
            self.tree[node] = arr[start]
            return
        mid = (start + end) // 2
        self._build(arr, 2*node, start, mid)
        self._build(arr, 2*node+1, mid+1, end)
        self.tree[node] = self.tree[2*node] + self.tree[2*node+1]

    def point_set(self, idx, new_val):
        """SET arr[idx] to new_val (not add — SET)."""
        self._update(1, 0, self.n-1, idx, new_val)

    def _update(self, node, start, end, idx, new_val):
        if start == end:
            self.tree[node] = new_val
            return
        mid = (start + end) // 2
        if idx <= mid:
            self._update(2*node, start, mid, idx, new_val)
        else:
            self._update(2*node+1, mid+1, end, idx, new_val)
        self.tree[node] = self.tree[2*node] + self.tree[2*node+1]

    def range_sum(self, l, r):
        return self._query(1, 0, self.n-1, l, r)

    def _query(self, node, start, end, l, r):
        if r < start or end < l: return 0
        if l <= start and end <= r: return self.tree[node]
        mid = (start + end) // 2
        return self._query(2*node, start, mid, l, r) + \
               self._query(2*node+1, mid+1, end, l, r)


class RangeUpdateTree:
    """Segment tree for: range add update + range sum query (with lazy)."""
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        self._build(arr, 1, 0, self.n - 1)

    def _build(self, arr, node, start, end):
        if start == end:
            self.tree[node] = arr[start]
            return
        mid = (start + end) // 2
        self._build(arr, 2*node, start, mid)
        self._build(arr, 2*node+1, mid+1, end)
        self.tree[node] = self.tree[2*node] + self.tree[2*node+1]

    def _push_down(self, node, start, end):
        if self.lazy[node]:
            mid = (start + end) // 2
            l, r = 2*node, 2*node+1
            self.tree[l] += self.lazy[node] * (mid - start + 1)
            self.tree[r] += self.lazy[node] * (end - mid)
            self.lazy[l] += self.lazy[node]
            self.lazy[r] += self.lazy[node]
            self.lazy[node] = 0

    def range_add(self, l, r, val):
        """ADD val to all elements in arr[l..r]."""
        self._update(1, 0, self.n-1, l, r, val)

    def _update(self, node, start, end, l, r, val):
        if r < start or end < l: return
        if l <= start and end <= r:
            self.tree[node] += val * (end - start + 1)
            self.lazy[node] += val
            return
        self._push_down(node, start, end)
        mid = (start + end) // 2
        self._update(2*node, start, mid, l, r, val)
        self._update(2*node+1, mid+1, end, l, r, val)
        self.tree[node] = self.tree[2*node] + self.tree[2*node+1]

    def range_sum(self, l, r):
        return self._query(1, 0, self.n-1, l, r)

    def _query(self, node, start, end, l, r):
        if r < start or end < l: return 0
        if l <= start and end <= r: return self.tree[node]
        self._push_down(node, start, end)
        mid = (start + end) // 2
        return self._query(2*node, start, mid, l, r) + \
               self._query(2*node+1, mid+1, end, l, r)


# Test both separately and clearly
arr = [1, 2, 3, 4, 5]

# Point update tree
pt = PointUpdateTree(arr[:])
print("Before point set:", pt.range_sum(0, 4))      # 15
pt.point_set(2, 10)   # SET arr[2] = 10 (was 3)
print("After point_set(2, 10):", pt.range_sum(0, 4)) # 22 ✓ (1+2+10+4+5)

# Range update tree
rt = RangeUpdateTree(arr[:])
print("Before range add:", rt.range_sum(0, 4))       # 15
rt.range_add(1, 3, 10)  # ADD 10 to arr[1..3]
print("After range_add(1,3,10):", rt.range_sum(0, 4)) # 45 ✓ (1+12+13+14+5)
print("Element 0:", rt.range_sum(0, 0))               # 1  ✓
print("Element 1:", rt.range_sum(1, 1))               # 12 ✓
print("Element 4:", rt.range_sum(4, 4))               # 5  ✓
```

---

## Quick Reference: All 8 Mistakes

```
╔══════════════════════════════════════════════════════════════════════╗
║              SEGMENT TREE COMMON MISTAKES — QUICK REFERENCE         ║
╠══════════╦═══════════════════════════════╦══════════════════════════╣
║ Mistake  ║ What Goes Wrong               ║ Fix                      ║
╠══════════╬═══════════════════════════════╬══════════════════════════╣
║ 1: Index ║ Children computed at wrong    ║ Pick 1-indexed OR        ║
║ mixing   ║ positions; wrong values       ║ 0-indexed, never mix     ║
╠══════════╬═══════════════════════════════╬══════════════════════════╣
║ 2: Size  ║ IndexError for certain n      ║ Always use 4*n           ║
╠══════════╬═══════════════════════════════╬══════════════════════════╣
║ 3: Lazy  ║ Stale values in children      ║ _push_down() before      ║
║ push     ║ after range updates           ║ every recurse            ║
╠══════════╬═══════════════════════════════╬══════════════════════════╣
║ 4: Off   ║ Wrong leaf detection;         ║ Use inclusive [l, r];    ║
║ by one   ║ infinite recursion            ║ r < start not r <= start ║
╠══════════╬═══════════════════════════════╬══════════════════════════╣
║ 5:       ║ One child skipped on partial  ║ ALWAYS recurse both      ║
║ Partial  ║ overlap; missing updates      ║ children on partial      ║
╠══════════╬═══════════════════════════════╬══════════════════════════╣
║ 6: BIT   ║ Complexity; code size         ║ Use BIT for point-update ║
║ enough   ║                               ║ + prefix sum             ║
╠══════════╬═══════════════════════════════╬══════════════════════════╣
║ 7: Non-  ║ Wrong aggregated values       ║ Only use associative ops;║
║ assoc.   ║ (average of averages ≠ avg)   ║ store (sum, count) pairs ║
╠══════════╬═══════════════════════════════╬══════════════════════════╣
║ 8: Point ║ Silent value corruption;      ║ Clear separate APIs for  ║
║ vs range ║ adds instead of sets or v/v   ║ point-set vs range-add   ║
╚══════════╩═══════════════════════════════╩══════════════════════════╝
```

---

## Final Test: Put It All Together

```python
import math

class RobustSegmentTree:
    """
    A clean, correct segment tree that avoids all 8 common mistakes:
    1. Consistent 1-indexed convention throughout
    2. Allocates 4*n space
    3. Pushes lazy before recursing
    4. Inclusive boundaries, correct leaf check
    5. Recurses both children on partial overlap
    6. (Use BIT instead when possible — but here we show range max, which needs ST)
    7. Uses max (associative) as merge function
    8. Clear separate point-update and range-query API
    """
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [float('-inf')] * (4 * self.n)  # Mistake 2: 4*n
        self._build(arr, 1, 0, self.n - 1)

    def _build(self, arr, node, start, end):
        if start == end:
            self.tree[node] = arr[start]
            return
        mid = (start + end) // 2  # Mistake 4: correct mid
        self._build(arr, 2 * node, start, mid)
        self._build(arr, 2 * node + 1, mid + 1, end)
        self.tree[node] = max(self.tree[2*node], self.tree[2*node+1])  # Mistake 7: max is associative

    def point_update(self, idx, val):
        """SET arr[idx] = val. Point update, not range."""  # Mistake 8: clear API
        self._update(1, 0, self.n-1, idx, val)

    def _update(self, node, start, end, idx, val):
        if start == end:
            self.tree[node] = val
            return
        mid = (start + end) // 2
        if idx <= mid:
            self._update(2 * node, start, mid, idx, val)      # Mistake 1: 1-indexed
        else:
            self._update(2 * node + 1, mid + 1, end, idx, val) # Mistake 1: 1-indexed
        self.tree[node] = max(self.tree[2*node], self.tree[2*node+1])

    def range_max(self, l, r):
        """Maximum in arr[l..r] inclusive."""  # Mistake 8: clear API
        return self._query(1, 0, self.n-1, l, r)

    def _query(self, node, start, end, l, r):
        if r < start or end < l:       # Mistake 4: strict <, not <=
            return float('-inf')
        if l <= start and end <= r:    # Mistake 4: inclusive end <= r
            return self.tree[node]
        mid = (start + end) // 2
        # Mistake 5: ALWAYS recurse both children
        left  = self._query(2 * node, start, mid, l, r)
        right = self._query(2 * node + 1, mid + 1, end, l, r)
        return max(left, right)


arr = [3, 1, 4, 1, 5, 9, 2, 6]
st = RobustSegmentTree(arr)

print("Max [0,7]:", st.range_max(0, 7))   # 9  ✓
print("Max [0,4]:", st.range_max(0, 4))   # 5  ✓
print("Max [4,7]:", st.range_max(4, 7))   # 9  ✓
print("Max [2,5]:", st.range_max(2, 5))   # 9  ✓

st.point_update(5, 0)  # Set arr[5] = 0 (was 9)
print("After update, Max [0,7]:", st.range_max(0, 7))  # 6 ✓
print("After update, Max [4,7]:", st.range_max(4, 7))  # 6 ✓
```

---

*Segment trees reward precision. Every node in the tree is a tiny contract: "I represent the aggregate of my range." Break the contract once — wrong index formula, missing push-down, wrong size — and the whole edifice of guarantees collapses. Keep these 8 mistakes on your mental checklist and your segment trees will be bulletproof.*
