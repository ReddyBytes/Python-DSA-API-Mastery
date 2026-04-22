# =============================================================================
# MODULE 23 — SEGMENT TREE: Practice Problems
# =============================================================================
# Run: python3 practice_problems.py
#
# Covers: range sum query, range min/max query, point update + range query,
#         range update with lazy propagation, count of elements in range
#
# Mental model: think of the segment tree as breaking a big problem in half
# repeatedly.  Every node stores the "summary" of its segment.
# Instead of recomputing a range from scratch, you combine precomputed halves.
#
# Array indexing used throughout: 0-based for input arrays, 1-based for the
# internal tree array (tree[1] = root; children of node i are 2i and 2i+1).
# =============================================================================


# =============================================================================
# PROBLEM 1 — Range Sum Query with Point Updates
# =============================================================================
#
# Build a segment tree over an array that supports:
#   query(l, r)     → sum of arr[l..r]  (0-indexed, inclusive)
#   update(i, val)  → set arr[i] = val, update the tree
#
# Why not just use a prefix-sum array?
#   Prefix sum gives O(1) query but O(n) update.
#   Segment tree gives O(log n) for BOTH query and update.
#   Use segment tree when you have many queries AND many updates.
#
# Time:  O(n) build · O(log n) query · O(log n) update
# Space: O(4n) — safe upper bound for tree array size
# =============================================================================

class RangeSumSegTree:
    """Segment tree for sum queries with point updates."""

    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)   # allocate 4n to be safe
        if self.n > 0:
            self._build(arr, 1, 0, self.n - 1)

    def _build(self, arr, node, start, end):
        """Build the tree bottom-up. Leaves store arr values; parents store sums."""
        if start == end:
            self.tree[node] = arr[start]    # leaf node stores the element itself
            return
        mid = (start + end) // 2
        self._build(arr, 2 * node, start, mid)          # build left child
        self._build(arr, 2 * node + 1, mid + 1, end)    # build right child
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]  # merge

    def update(self, i, val, node=1, start=0, end=None):
        """Point update: set arr[i] = val."""
        if end is None:
            end = self.n - 1
        if start == end:
            # Reached the leaf for index i
            self.tree[node] = val
            return
        mid = (start + end) // 2
        if i <= mid:
            self.update(i, val, 2 * node, start, mid)
        else:
            self.update(i, val, 2 * node + 1, mid + 1, end)
        # Recompute this node's value from updated children
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def query(self, l, r, node=1, start=0, end=None):
        """Range sum query: return sum of arr[l..r]."""
        if end is None:
            end = self.n - 1
        if r < start or end < l:
            return 0            # no overlap — identity for sum is 0
        if l <= start and end <= r:
            return self.tree[node]   # complete overlap — return node value directly
        # Partial overlap — recurse on both children and combine
        mid = (start + end) // 2
        left_sum  = self.query(l, r, 2 * node,     start, mid)
        right_sum = self.query(l, r, 2 * node + 1, mid + 1, end)
        return left_sum + right_sum


# =============================================================================
# PROBLEM 2 — Range Minimum Query
# =============================================================================
#
# Build a segment tree that answers:
#   query(l, r) → minimum value in arr[l..r]
#
# Almost identical to sum tree, but:
#   - Identity element changes to float('inf') (not 0)
#   - Merge operation changes to min() (not +)
#
# The three overlap cases stay exactly the same:
#   1. No overlap       → return infinity
#   2. Complete overlap → return node value
#   3. Partial overlap  → return min(left child result, right child result)
#
# Time:  O(n) build · O(log n) query · O(log n) update
# =============================================================================

class RangeMinSegTree:
    """Segment tree for minimum queries with point updates."""

    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [float('inf')] * (4 * self.n)
        if self.n > 0:
            self._build(arr, 1, 0, self.n - 1)

    def _build(self, arr, node, start, end):
        if start == end:
            self.tree[node] = arr[start]
            return
        mid = (start + end) // 2
        self._build(arr, 2 * node,     start, mid)
        self._build(arr, 2 * node + 1, mid + 1, end)
        self.tree[node] = min(self.tree[2 * node], self.tree[2 * node + 1])  # merge with min

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

    def query(self, l, r, node=1, start=0, end=None):
        """Return minimum in arr[l..r]."""
        if end is None:
            end = self.n - 1
        if r < start or end < l:
            return float('inf')          # no overlap → identity for min
        if l <= start and end <= r:
            return self.tree[node]       # complete overlap
        mid = (start + end) // 2
        return min(
            self.query(l, r, 2 * node,     start, mid),
            self.query(l, r, 2 * node + 1, mid + 1, end)
        )


# =============================================================================
# PROBLEM 3 — Range Maximum Query
# =============================================================================
#
# Same structure as minimum, but merge with max() and identity is -infinity.
# Demonstrating how trivially the template adapts by changing only 2 lines.
# =============================================================================

class RangeMaxSegTree:
    """Segment tree for maximum queries with point updates."""

    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [float('-inf')] * (4 * self.n)
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

    def query(self, l, r, node=1, start=0, end=None):
        if end is None:
            end = self.n - 1
        if r < start or end < l:
            return float('-inf')
        if l <= start and end <= r:
            return self.tree[node]
        mid = (start + end) // 2
        return max(
            self.query(l, r, 2 * node,     start, mid),
            self.query(l, r, 2 * node + 1, mid + 1, end)
        )


# =============================================================================
# PROBLEM 4 — Range Update with Lazy Propagation (Add delta to range)
# =============================================================================
#
# Problem: support
#   range_add(l, r, delta) → add delta to every element in arr[l..r]
#   range_sum(l, r)        → sum of arr[l..r]
#
# Without lazy propagation: each range_add would touch O(n) leaves → too slow.
#
# Lazy propagation insight:
#   When a node's segment is COMPLETELY inside the update range,
#   we don't immediately push the update down to children.
#   Instead we MARK the node with a "pending" (lazy) delta and update the
#   node's sum in O(1) using the formula:
#       new_sum = old_sum + delta * segment_length
#
#   We only PUSH the lazy value down when we need to visit children
#   (during a query or update that partially overlaps this node's segment).
#
# Time:  O(n) build · O(log n) range update · O(log n) range query
# Space: O(4n) tree + O(4n) lazy array
# =============================================================================

class LazySegTree:
    """Segment tree with lazy propagation for range add and range sum."""

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
        """Push the pending lazy value from node to its two children."""
        if self.lazy[node] != 0:
            mid = (start + end) // 2
            left_len  = mid - start + 1
            right_len = end - mid

            # Update left child's sum and mark it lazy
            self.tree[2 * node]     += self.lazy[node] * left_len
            self.lazy[2 * node]     += self.lazy[node]

            # Update right child's sum and mark it lazy
            self.tree[2 * node + 1] += self.lazy[node] * right_len
            self.lazy[2 * node + 1] += self.lazy[node]

            self.lazy[node] = 0     # clear the current node's lazy tag

    def range_add(self, l, r, delta, node=1, start=0, end=None):
        """Add delta to every element in arr[l..r]."""
        if end is None:
            end = self.n - 1
        if r < start or end < l:
            return                              # no overlap
        if l <= start and end <= r:
            # Complete overlap: update this node and mark lazy; stop recursion
            self.tree[node] += delta * (end - start + 1)
            self.lazy[node] += delta
            return
        # Partial overlap: push lazy down before visiting children
        self._push_down(node, start, end)
        mid = (start + end) // 2
        self.range_add(l, r, delta, 2 * node,     start, mid)
        self.range_add(l, r, delta, 2 * node + 1, mid + 1, end)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def range_sum(self, l, r, node=1, start=0, end=None):
        """Return sum of arr[l..r] after all updates."""
        if end is None:
            end = self.n - 1
        if r < start or end < l:
            return 0
        if l <= start and end <= r:
            return self.tree[node]
        # Partial overlap: push down before reading children
        self._push_down(node, start, end)
        mid = (start + end) // 2
        return (self.range_sum(l, r, 2 * node,     start, mid) +
                self.range_sum(l, r, 2 * node + 1, mid + 1, end))


# =============================================================================
# PROBLEM 5 — Count of Elements in Range
# =============================================================================
#
# Given a sorted array, count how many elements fall in [lo, hi].
#
# Approach 1 (binary search): O(log n) — simpler and faster for static arrays.
# Approach 2 (segment tree over value space): O(log M) per query/update where
#   M = value range — useful when elements are added dynamically.
#
# Here we implement the coordinate-compression + segment tree approach:
#   - Map all values to compressed indices.
#   - Build a frequency tree where each leaf stores count of that value.
#   - range_count(lo, hi) = sum of frequencies in [lo, hi].
#   - add(val) = increment the frequency at val's compressed position.
#
# Time:  O(n log n) build · O(log n) query · O(log n) insert
# Space: O(n) for compression + O(4n) for tree
# =============================================================================

from bisect import bisect_left, bisect_right

class CountInRangeSegTree:
    """
    Segment tree for counting elements in a value range [lo, hi].
    Supports dynamic insertion of new elements.
    """

    def __init__(self, values):
        """
        values: initial list of integers (will be sorted + deduplicated for
                coordinate compression)
        """
        self.sorted_vals = sorted(set(values))
        self.m = len(self.sorted_vals)
        self.tree = [0] * (4 * self.m)
        # Insert all initial values
        for v in values:
            self._update(self._compress(v), 1, 1, 0, self.m - 1)

    def _compress(self, val):
        """Map a value to its 0-based index in sorted_vals."""
        idx = bisect_left(self.sorted_vals, val)
        if idx >= self.m or self.sorted_vals[idx] != val:
            raise ValueError(f"{val} not in known value set")
        return idx

    def _update(self, ci, delta, node, start, end):
        """Add delta to frequency at compressed index ci."""
        if start == end:
            self.tree[node] += delta
            return
        mid = (start + end) // 2
        if ci <= mid:
            self._update(ci, delta, 2 * node, start, mid)
        else:
            self._update(ci, delta, 2 * node + 1, mid + 1, end)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def _query(self, cl, cr, node, start, end):
        """Count elements with compressed index in [cl, cr]."""
        if cr < start or end < cl:
            return 0
        if cl <= start and end <= cr:
            return self.tree[node]
        mid = (start + end) // 2
        return (self._query(cl, cr, 2 * node, start, mid) +
                self._query(cl, cr, 2 * node + 1, mid + 1, end))

    def count_in_range(self, lo, hi):
        """
        Return count of elements x where lo <= x <= hi.
        Uses bisect on sorted_vals so exact matches and boundary values work.
        """
        # Find compressed range
        cl = bisect_left(self.sorted_vals, lo)
        cr = bisect_right(self.sorted_vals, hi) - 1
        if cl > cr:
            return 0
        return self._query(cl, cr, 1, 0, self.m - 1)


# =============================================================================
# TEST RUNNER
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MODULE 23 — SEGMENT TREE: Practice Problems")
    print("=" * 60)

    # --- Problem 1: Range Sum ---
    print("\n[1] Range Sum Query with Point Updates")
    arr = [1, 3, 5, 7, 9, 11]
    st_sum = RangeSumSegTree(arr)
    print(f"  Array: {arr}")
    print(f"  sum(1, 4) = {st_sum.query(1, 4)}")   # 3+5+7+9 = 24
    assert st_sum.query(1, 4) == 24
    assert st_sum.query(0, 5) == sum(arr)
    assert st_sum.query(2, 2) == 5
    st_sum.update(2, 10)   # arr[2] = 10 (was 5)
    assert st_sum.query(1, 4) == 29
    print(f"  After update arr[2]=10, sum(1,4) = {st_sum.query(1, 4)}")
    print("  All assertions passed.")

    # --- Problem 2: Range Min ---
    print("\n[2] Range Minimum Query")
    arr2 = [4, 2, 7, 1, 9, 3, 8]
    st_min = RangeMinSegTree(arr2)
    print(f"  Array: {arr2}")
    assert st_min.query(0, 6) == 1
    assert st_min.query(0, 2) == 2
    assert st_min.query(4, 6) == 3
    st_min.update(3, 10)   # arr[3] = 10 (was 1)
    assert st_min.query(0, 6) == 2
    print(f"  min(0,6)={st_min.query(0,6)}, min(0,2)=2, min(4,6)=3")
    print("  All assertions passed.")

    # --- Problem 3: Range Max ---
    print("\n[3] Range Maximum Query")
    arr3 = [4, 2, 7, 1, 9, 3, 8]
    st_max = RangeMaxSegTree(arr3)
    print(f"  Array: {arr3}")
    assert st_max.query(0, 6) == 9
    assert st_max.query(0, 2) == 7
    assert st_max.query(3, 5) == 9
    st_max.update(4, 0)   # arr[4] = 0 (was 9)
    assert st_max.query(0, 6) == 8
    print(f"  max(0,6)={st_max.query(0,6)}, max(0,2)=7")
    print("  All assertions passed.")

    # --- Problem 4: Lazy Range Update ---
    print("\n[4] Range Update with Lazy Propagation")
    arr4 = [1, 2, 3, 4, 5]
    lazy_st = LazySegTree(arr4)
    print(f"  Array: {arr4}")
    assert lazy_st.range_sum(0, 4) == 15
    lazy_st.range_add(1, 3, 10)   # add 10 to indices 1..3
    # New array: [1, 12, 13, 14, 5]
    assert lazy_st.range_sum(0, 4) == 15 + 30    # 30 added in total
    assert lazy_st.range_sum(1, 3) == 12 + 13 + 14
    lazy_st.range_add(0, 4, -1)   # subtract 1 from all
    # After +10 to [1..3]: sum=45; after -1 to all 5 elements: sum=40
    assert lazy_st.range_sum(0, 4) == 40
    print(f"  After range_add(0,4,-1): sum(0,4) = {lazy_st.range_sum(0,4)}")
    print("  All assertions passed.")

    # --- Problem 5: Count in Range ---
    print("\n[5] Count of Elements in Range")
    values = [1, 3, 5, 7, 9, 3, 1, 5, 5]
    cst = CountInRangeSegTree(values)
    print(f"  Values: {values}")
    assert cst.count_in_range(1, 5) == 7    # 1,1,3,3,5,5,5
    assert cst.count_in_range(6, 9) == 2    # 7,9
    assert cst.count_in_range(4, 6) == 3    # 5,5,5
    assert cst.count_in_range(10, 20) == 0
    print(f"  count[1..5]={cst.count_in_range(1,5)}, count[6..9]={cst.count_in_range(6,9)}")
    print("  All assertions passed.")

    print("\n" + "=" * 60)
    print("All problems completed successfully.")
    print("=" * 60)
