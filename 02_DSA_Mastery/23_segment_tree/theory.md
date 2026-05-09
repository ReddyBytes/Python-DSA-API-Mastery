<a id="top"></a>
# Segment Tree — The Power of Efficient Range Queries

> Suppose you have an array.
>
> You must:
> - Query sum of range many times
> - Update elements frequently
>
> Brute force becomes too slow.
>
> Segment Tree solves this efficiently.

Segment Tree is a data structure designed for:

- Fast range queries
- Fast updates

## 📖 Table of Contents

1. [Real Life Story — Warehouse Inventory](#1-real-life-story)
2. [Problem Without Segment Tree](#2-problem-without-segment-tree)
3. [Core Idea of Segment Tree](#3-core-idea)
4. [Building Segment Tree](#4-building-segment-tree)
5. [Querying Range](#5-querying-range)
6. [Updating Element](#6-updating-element)
7. [Why Segment Tree Is Powerful](#7-why-powerful)
8. [Lazy Propagation (Advanced)](#8-lazy-propagation)
9. [When to Use Segment Tree](#9-when-to-use)
10. [When NOT to Use](#10-when-not-to-use)
11. [Compare With Other Structures](#11-compare-with-other-structures)
12. [Real-World Applications](#12-real-world-applications)
13. [Common Mistakes Reference](#13-common-mistakes-reference)
14. [Mental Model](#14-mental-model)
15. [Final Understanding](#15-final-understanding)
16. [Fenwick Tree (Binary Indexed Tree)](#16-fenwick-tree)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
segment tree structure · range query · point update · O(log n) operations

**Should Learn** — Important for real projects, comes up regularly:
lazy propagation · Fenwick tree (BIT) as simpler alternative

**Good to Know** — Useful in specific situations, not always tested:
when to use over prefix sum · build complexity O(n)

**Reference** — Know it exists, look up syntax when needed:
persistent segment tree · 2D segment trees · square root decomposition

<a id="1-real-life-story"></a>
# 1. Real Life Story — Warehouse Inventory

Imagine a warehouse with 1000 shelves.

Each shelf has number of products.

You need to answer:

"How many products between shelf 200 and 450?"

And shelves keep changing.

Brute force:
Loop every time → O(n)

Too slow if queries are frequent.

Segment Tree:
Preprocess and answer in O(log n).

## Visual: The Tournament Bracket Analogy

Think of a segment tree like a sports tournament with 8 players. You want to find the strongest player overall. Round 1: players compete in pairs. Winners advance.

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

8 is the overall champion. Makes sense.

But here's the key difference between this and a regular tournament: the bracket REMEMBERS all the intermediate results.

So if someone asks "what's the max score among players 2 through 5?", you don't re-run the tournament. You look up the stored results for the relevant bracket sections. That's the entire idea behind a segment tree.

> [↑ Back to Top](#top)

<a id="2-problem-without-segment-tree"></a>
# 2. Problem Without Segment Tree

Array:

[1, 3, 5, 7, 9, 11]

Query:
Sum from index 1 to 4.

Without optimization:
Add manually → O(n)

If 10⁵ queries:
Very slow.

> [↑ Back to Top](#top)

<a id="3-core-idea"></a>
# 3. Core Idea of Segment Tree

Break array into segments.

Store sum of segments in tree nodes.

Each node represents:

Sum of a range.

Tree structure:

```
                [0-5]
              /        \
         [0-2]          [3-5]
        /     \        /     \
    [0-1]    [2-2]  [3-4]   [5-5]
```

Each node stores sum of its range.

## Visual: Full Sum Tree for [4, 2, 7, 1, 5, 3, 8, 6]

Let's build a sum segment tree using array `[4, 2, 7, 1, 5, 3, 8, 6]` (indices 0 through 7). Each node is labeled `[range]: value`.

```
                          [0,7]: 36
                        /             \
              [0,3]: 14               [4,7]: 22
             /        \              /         \
         [0,1]: 6   [2,3]: 8    [4,5]: 8    [6,7]: 14
         /    \     /    \      /    \       /     \
       [0]:4 [1]:2 [2]:7 [3]:1 [4]:5 [5]:3 [6]:8  [7]:6
```

Reading the tree:
- Root `[0,7]: 36` covers the entire array. Sum = 4+2+7+1+5+3+8+6 = 36.
- `[0,3]: 14` covers indices 0-3. Sum = 4+2+7+1 = 14.
- `[4,7]: 22` covers indices 4-7. Sum = 5+3+8+6 = 22.
- Leaf nodes are the original array values.

Building rule: each parent = sum of its two children. Build bottom-up.

**Common mistake — non-associative merge:** Using average as the merge function silently produces wrong answers. `avg(avg(a,b), c)` does NOT equal the true average of `[a,b,c]` when sub-ranges have unequal sizes. Only use associative operations: sum, max, min, GCD, XOR, AND, OR. If you need average, store `(sum, count)` pairs instead.

> 📝 **Practice:** [Q2 — Tree Node Relationships](./practice.md#q2--structure--tree-node-relationships)

## Visual: What Else Can Segment Trees Store?

The structure works for any operation where you can combine answers from sub-ranges.

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

> [↑ Back to Top](#top)

<a id="4-building-segment-tree"></a>
# 4. Building Segment Tree

Build bottom-up.

Leaf nodes:
Store individual elements.

Parent:
Sum of children.

Time:
O(n)

Space:
O(4n) safe allocation.

**Common mistake — wrong tree size:** Allocating `2*n` instead of `4*n` causes an `IndexError` for certain array sizes (e.g., `n=3`). The worst case occurs when `n` is just above a power of 2, where the recursion can reach indices up to `4*n`. Always allocate `4*n`.

```
n=1:   tree needs  2 nodes  (4*1=4, safe)
n=5:   tree needs 16 nodes  (4*5=20, safe) ← 2*n=10 is NOT enough!
n=9:   tree needs 32 nodes  (4*9=36, safe)
```

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

**Common mistake — indexing convention mixing:** Segment trees have two valid systems: 1-indexed (root at 1, children at `2*i` and `2*i+1`) and 0-indexed (root at 0, children at `2*i+1` and `2*i+2`). Both work. Mixing them — building with one and querying with the other — produces silently wrong results. Pick one and use it everywhere. Add a comment at the top of every implementation stating which convention it uses.

```
1-Indexed Layout (most tutorials use this):
              [1]
            /     \
          [2]     [3]
         /   \   /   \
       [4]  [5] [6]  [7]

0-Indexed Layout:
              [0]
            /     \
          [1]     [2]
         /   \   /   \
       [3]  [4] [5]  [6]
```

> 📝 **Practice:** [Q1 — Segment Tree Size Allocation](./practice.md#q1--structure--segment-tree-size-allocation) · [Q3 — Build From Array](./practice.md#q3--build--build-from-array)

> [↑ Back to Top](#top)

<a id="5-querying-range"></a>
# 5. Querying Range

Suppose query [1,4]

Three cases:

1. Complete overlap → return node value.
2. No overlap → return 0.
3. Partial overlap → query both children.

Each query:
O(log n)

Because tree height ≈ log n.

## Visual: Range Query Traversal for [2, 5]

The query is: `sum(arr[2..5])` = 7+1+5+3 = **16**

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

Nodes visited: [0,7], [0,3], [0,1], [2,3], [4,7], [4,5], [6,7] = 7 nodes.
For a 1,000,000-element array, a range query visits at most **4 × log₂(n) ≈ 80 nodes**.

**Common mistake — not handling partial overlap:** In partial overlap, you MUST recurse into BOTH children. Only going to the child where `l <= mid` misses the portion of the range in the other child. The no-overlap base case will stop branches that don't apply.

```
Range update [1, 2] on array [0, 0, 0, 0]:

Tree covering [0, 3]:
         [0,3]
        /     \
    [0,1]     [2,3]
    /   \     /   \
  [0]  [1]  [2]  [3]

Update [1, 2]:
  Root [0,3]: partial overlap
    → recurse LEFT to [0,1]: partial overlap (only index 1 in range)
      → recurse RIGHT to [1]: FULL overlap → update
    → recurse RIGHT to [2,3]: partial overlap (only index 2 in range)
      → recurse LEFT to [2]: FULL overlap → update

WRONG approach: only going left from [0,3] misses index 2 entirely.
```

**Common mistake — off-by-one in boundaries:** The leaf condition `start == end` assumes inclusive boundaries. The no-overlap check must be `r < start` (strict less-than), and the full-overlap check must be `end <= r` (inclusive). Using `r <= start` or `end < r` causes missed leaves or infinite recursion.

> 📝 **Practice:** [Q4 — Range Sum Query](./practice.md#q4--query--range-sum-query) · [Q6 — Three Overlap Cases](./practice.md#q6--query--three-overlap-cases)

> [↑ Back to Top](#top)

<a id="6-updating-element"></a>
# 6. Updating Element

If arr[2] changes:

Update leaf.
Update all parents on path.

Time:
O(log n)

Efficient for frequent updates.

## Visual: Point Update Traversal

Updating index 3 (value 1 → 9). Difference = +8.

```
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

After update:

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

**Common mistake — point update vs range update confusion:** Calling `range_add(i, i, val)` on a lazy tree ADDS `val` to the element, it does not SET it to `val`. These are different operations with different APIs. Mixing them silently corrupts values. Use a clearly named `point_set` for setting a single element and `range_add` for adding to a range.

> 📝 **Practice:** [Q5 — Point Update](./practice.md#q5--update--point-update)

> [↑ Back to Top](#top)

<a id="7-why-powerful"></a>
# 7. Why Segment Tree Is Powerful

Operations:

Build → O(n)
Query → O(log n)
Update → O(log n)

Without it:

Query → O(n)

Huge improvement for many queries.

## Visual: Segment Tree vs Prefix Sum

Both structures answer range sum queries. Choose the right one.

Prefix Sum — build a running sum array: `prefix[i]` = sum of all elements from index 0 to i.

```
Array:   [4, 2, 7, 1, 5, 3, 8, 6]
Prefix:  [4, 6, 13, 14, 19, 22, 30, 36]

Query sum(2..5): prefix[5] - prefix[1] = 22 - 6 = 16. Correct! ← O(1) query

Update arr[3] from 1 to 9:
  All 5 positions after index 3 must be updated. ← O(n) update
```

```
Operation     | Prefix Sum    | Segment Tree
──────────────|───────────────|──────────────
Build         | O(n)          | O(n)
Range Query   | O(1)          | O(log n)
Point Update  | O(n)          | O(log n)
Space         | O(n)          | O(4n)
```

Real-world analogy:
- Prefix sum is like a printed phonebook. Fast lookups, but every time someone's number changes, you reprint the whole book.
- Segment tree is like a live database. Slower for a single lookup, but updates are fast and everything stays current.

> [↑ Back to Top](#top)

<a id="8-lazy-propagation"></a>
# 8. Lazy Propagation (Advanced)

Problem:

Update entire range.

Example:
Add +5 to range [1,4]

Naively:
Update each element → O(n)

Lazy propagation:
Delay update.
Mark node as lazy.
Propagate when needed.

Time:
O(log n)

Very important for range updates.

## Visual: Lazy Tag Behavior

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
If you query left child: 22 ✓
If you query left-left child WITHOUT pushing left child's lazy first:
  → returns tree[left-left] = 1, NOT 11  ← WRONG!
```

**Common mistake — forgetting to push lazy before recursing:** The lazy tag is like a sticky note on a manager's board — a deferred instruction to all subordinates. If you query or update a child before pushing the lazy tag down, the child returns stale values. The fix: call `_push_down(node, start, end)` before EVERY recursive call into children, both in `query` and in `range_update`.

```python
def _push_down(self, node, start, end):
    """Push pending lazy update to children. MUST call before recursing."""
    if self.lazy[node] != 0:
        mid = (start + end) // 2
        left, right = 2 * node, 2 * node + 1
        self.tree[left]  += self.lazy[node] * (mid - start + 1)
        self.tree[right] += self.lazy[node] * (end - mid)
        self.lazy[left]  += self.lazy[node]
        self.lazy[right] += self.lazy[node]
        self.lazy[node] = 0  # Clear after push
```

> 📝 **Practice:** [Q15 — Lazy Propagation Range Add and Range Sum](./practice.md#q15--lazy--lazy-propagation-range-add-and-range-sum) · [Q16 — Push-Down Mechanics](./practice.md#q16--lazy--push-down-mechanics)

> [↑ Back to Top](#top)

<a id="9-when-to-use"></a>
# 9. When to Use Segment Tree

Use when:

- Many range queries
- Many updates
- Need fast performance
- Query type associative (sum, min, max, gcd)

> 📝 **Practice:** [Q10 — Segment Tree vs Prefix Sum vs BIT](./practice.md#q10--tradeoffs--segment-tree-vs-prefix-sum-vs-bit)

> [↑ Back to Top](#top)

<a id="10-when-not-to-use"></a>
# 10. When NOT to Use

Avoid when:

- Queries are few
- No updates
- Simpler prefix sum works
- Small input size

Segment tree adds complexity.

**Common mistake — using segment tree when BIT is sufficient:** For point update + prefix sum queries, a Fenwick (Binary Indexed) tree solves the problem in ~15 lines with half the memory and faster constant factors. A segment tree for this use case is like using a Swiss Army knife to open a can of soup — technically possible, but unnecessarily complex.

```
                 Fenwick Tree        Segment Tree
─────────────────────────────────────────────────
Code complexity     Simple (10 lines)   Moderate (30+ lines)
Memory              O(n)                O(4n)
Point update        O(log n)            O(log n)
Range sum           O(log n)            O(log n)
Range min/max       Not supported       Supported
Lazy propagation    Not supported       Supported

Use Fenwick when: only prefix sum queries + point updates needed
Use Segment when: range min/max, lazy propagation, or range updates
```

> [↑ Back to Top](#top)

<a id="11-compare-with-other-structures"></a>
# 11. Compare With Other Structures

Prefix Sum:
Fast queries O(1)
No updates O(n)

Fenwick Tree:
Simpler than segment tree
Handles prefix queries

Segment Tree:
More flexible
Handles range queries + updates

Choose wisely.

> 📝 **Practice:** [Q11 — Fenwick Tree Point Update and Prefix Sum](./practice.md#q11--bit--fenwick-tree-point-update-and-prefix-sum) · [Q12 — Fenwick Range Update With Difference Array](./practice.md#q12--bit--fenwick-range-update-with-difference-array)

> [↑ Back to Top](#top)

<a id="12-real-world-applications"></a>
# 12. Real-World Applications

- Financial data range queries
- Real-time analytics
- Gaming leaderboards
- Database aggregation queries
- CPU monitoring ranges

Segment trees power range analytics systems.

> [↑ Back to Top](#top)

<a id="13-common-mistakes-reference"></a>
# 13. Common Mistakes Reference

Quick reference for all segment tree pitfalls:

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

> 📝 **Practice:** [Q13 — Wrong Tree Size Crash](./practice.md#q13--mistakes--wrong-tree-size-crash) · [Q14 — Indexing Convention Consistency](./practice.md#q14--mistakes--indexing-convention-consistency) · [Q17 — Missing Push-Down Bug](./practice.md#q17--lazy--lazy-propagation-missing-push-down-bug)

> [↑ Back to Top](#top)

<a id="14-mental-model"></a>
# 14. Mental Model

Think of segment tree as:

Breaking big problem into halves repeatedly.

Each node stores summary of its segment.

Instead of recalculating range,
you combine precomputed segments.

> [↑ Back to Top](#top)

<a id="15-final-understanding"></a>
# 15. Final Understanding

Segment Tree is:

- Tree over array
- Stores range information
- Supports fast range query
- Supports fast updates
- O(log n) operations
- Advanced but powerful

Mastering segment tree prepares you for:

- Competitive programming
- Advanced algorithm interviews
- High-performance systems
- Range aggregation problems

A segment tree is a tournament bracket that stores every intermediate result, letting you answer range queries and process updates in O(log n) — the sweet spot when your data changes and you need both fast queries and fast updates.

## Visual: Full Code Reference

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

> 📝 **Practice:** [Q67 · segment-tree-range-query](../dsa_practice_questions_100.md#q67--thinking--segment-tree-range-query)

Segment Tree is a power tool.
Use when necessary.

> [↑ Back to Top](#top)

<a id="16-fenwick-tree"></a>
# 16. Fenwick Tree (Binary Indexed Tree) — Simpler Range Queries

> If a segment tree is a full surgical kit, a Fenwick tree is a pocket knife — less powerful, but faster to code and half the memory when point updates and prefix sums are all you need.

A **Fenwick tree** (also called a **Binary Indexed Tree** or BIT) supports two operations on an array in O(log n):
1. **Point update** — change a single element
2. **Prefix sum query** — sum from index 1 to i

Unlike a segment tree, a Fenwick tree cannot handle range minimum/maximum queries, but for prefix sums and point updates it requires less code and half the memory.

```python
class FenwickTree:
    def __init__(self, n):
        self.n = n
        self.tree = [0] * (n + 1)   # ← 1-indexed

    def update(self, i, delta):
        """Add delta to position i (1-indexed)."""
        while i <= self.n:
            self.tree[i] += delta
            i += i & (-i)           # ← move to next responsible node (lowbit trick)

    def query(self, i):
        """Prefix sum from 1 to i (inclusive)."""
        total = 0
        while i > 0:
            total += self.tree[i]
            i -= i & (-i)           # ← move to parent (remove lowbit)
        return total

    def range_query(self, l, r):
        """Sum from l to r inclusive (1-indexed)."""
        return self.query(r) - self.query(l - 1)


# Build from existing array in O(n log n):
def build(arr):
    ft = FenwickTree(len(arr))
    for i, val in enumerate(arr):
        ft.update(i + 1, val)       # ← convert to 1-indexed
    return ft
```

> 📝 **Practice:** [Q68 · fenwick-tree](../dsa_practice_questions_100.md#q68--normal--fenwick-tree)

**The lowbit trick explained:**
```
i & (-i)  extracts the lowest set bit of i

i = 6  →  binary: 110  →  lowbit = 010 = 2
i = 12 →  binary: 1100 →  lowbit = 0100 = 4

Each index i is responsible for a range of lowbit(i) elements
```

**Fenwick tree vs Segment tree:**

```
                 Fenwick Tree        Segment Tree
─────────────────────────────────────────────────
Code complexity     Simple (10 lines)   Moderate (30+ lines)
Memory              O(n)                O(4n)
Point update        O(log n)            O(log n)
Range sum           O(log n)            O(log n)
Range min/max       ✗ Not supported     ✓ Supported
Lazy propagation    ✗ Not supported     ✓ Supported
Range update        ✓ With trick        ✓ Native
─────────────────────────────────────────────────
Use Fenwick when: only prefix sum queries + point updates needed
Use Segment when: range min/max, lazy propagation, or range updates
```

**Range update with Fenwick (difference array trick):**

```python
# To support range update [l, r] += val:
# Use two Fenwick trees (advanced pattern)
# Or: maintain difference array in Fenwick tree
ft.update(l, val)        # ← add val at l
ft.update(r + 1, -val)   # ← subtract at r+1
# Then point query at i = ft.query(i)
```

**Complexity:** O(n) build, O(log n) update and query, O(n) space

> [↑ Back to Top](#top)

# Navigation

Previous:
[22_bit_manipulation/interview.md](/02_DSA_Mastery/22_bit_manipulation/interview.md)

Next:
[23_segment_tree/interview.md](/02_DSA_Mastery/23_segment_tree/interview.md)
[24_disjoint_set_union/theory.md](/02_DSA_Mastery/24_disjoint_set_union/theory.md)

**[🏠 Back to README](../README.md)**

**Prev:** [← Bit Manipulation — Interview Q&A](../22_bit_manipulation/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)
