# =============================================================================
# MODULE 16 — HEAPS: Practice Problems
# =============================================================================
# Run: python3 practice_problems.py
#
# Covers: heapify, top-K elements, merge K sorted lists, median of data stream,
#         task scheduler, sliding window maximum, K closest points to origin
#
# Key insight: Python's heapq is a MIN heap.
#   - For max-heap behaviour: negate values on push, negate again on pop.
#   - heapq.heapify(lst)   → O(n) in-place heap build (not O(n log n)!)
# =============================================================================

import heapq
from collections import Counter


# =============================================================================
# PROBLEM 1 — Heapify an array and extract sorted order
# =============================================================================
#
# Given an unsorted array, use heapq.heapify to build a min-heap in O(n),
# then extract elements in sorted (ascending) order.
#
# Why heapify is O(n) — not O(n log n):
#   Half the nodes are leaves (no work needed).
#   Each level does less sifting than the one above.
#   The total work sums to O(n) by the geometric series argument.
#
# Approach: heapify in-place, then heappop repeatedly.
# Time:  O(n) build + O(n log n) extraction = O(n log n) total
# Space: O(1) extra (in-place heap)
# =============================================================================

def heap_sort(arr):
    """
    Return a new sorted list using heap operations only.

    >>> heap_sort([5, 3, 8, 1, 9, 2])
    [1, 2, 3, 5, 8, 9]
    >>> heap_sort([])
    []
    >>> heap_sort([42])
    [42]
    """
    heap = arr[:]           # copy so we don't mutate the input
    heapq.heapify(heap)     # O(n) — rearranges in-place to satisfy min-heap property
    return [heapq.heappop(heap) for _ in range(len(heap))]  # O(n log n)


# =============================================================================
# PROBLEM 2 — Top-K Largest Elements
# =============================================================================
#
# Given an array and integer k, return the k largest elements (any order).
#
# Naive approach: sort descending → O(n log n)
# Better approach: maintain a min-heap of size k.
#   - If the heap already has k elements and the new element is larger than
#     the heap's minimum, pop the minimum and push the new element.
#   - After scanning the whole array the heap contains exactly the k largest.
#
# Why a MIN-heap of size k for "top-k LARGEST"?
#   The heap's root is always the *smallest* of the top-k candidates.
#   When a larger element arrives, we discard that smallest candidate.
#
# Time:  O(n log k) — each push/pop on a size-k heap costs O(log k)
# Space: O(k)
# =============================================================================

def top_k_largest(nums, k):
    """
    Return the k largest numbers in nums.

    >>> sorted(top_k_largest([3, 1, 5, 12, 2, 11], 3))
    [5, 11, 12]
    >>> top_k_largest([1], 1)
    [1]
    """
    min_heap = []
    for num in nums:
        heapq.heappush(min_heap, num)           # push current element
        if len(min_heap) > k:
            heapq.heappop(min_heap)             # discard the smallest so far
    # heap now holds exactly the k largest
    return min_heap


# =============================================================================
# PROBLEM 3 — Merge K Sorted Lists
# =============================================================================
#
# Given k sorted lists, merge them into one sorted list.
#
# Approach: use a min-heap to always pick the globally smallest remaining element.
#   - Push the first element of each list into the heap as (value, list_idx, elem_idx).
#   - Pop the minimum, add to result, push the next element from the same list.
#
# Why store (value, list_index, element_index)?
#   The heap needs to compare tuples. list_index and element_index act as
#   tie-breakers and let us locate the *next* element in that list.
#
# Time:  O(N log k) where N = total elements across all lists
# Space: O(k) for the heap
# =============================================================================

def merge_k_sorted_lists(lists):
    """
    Merge k sorted lists into one sorted list.

    >>> merge_k_sorted_lists([[1, 4, 7], [2, 5, 8], [3, 6, 9]])
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> merge_k_sorted_lists([[1], [], [2]])
    [1, 2]
    >>> merge_k_sorted_lists([])
    []
    """
    result = []
    heap = []

    # Seed the heap with each list's first element
    for i, lst in enumerate(lists):
        if lst:
            # (value, list_index, element_index_within_list)
            heapq.heappush(heap, (lst[0], i, 0))

    while heap:
        val, list_i, elem_i = heapq.heappop(heap)
        result.append(val)
        # If the same list has a next element, push it
        next_elem_i = elem_i + 1
        if next_elem_i < len(lists[list_i]):
            heapq.heappush(heap, (lists[list_i][next_elem_i], list_i, next_elem_i))

    return result


# =============================================================================
# PROBLEM 4 — Median of a Data Stream
# =============================================================================
#
# Design a data structure that supports:
#   add_num(val) — add a number to the stream
#   find_median() — return the median of all numbers seen so far
#
# Insight: maintain two heaps that split the stream at the median:
#   - lower_half: MAX heap (negate values) — holds the smaller half
#   - upper_half: MIN heap — holds the larger half
#
# Invariants to maintain after every insert:
#   1. Every element in lower_half <= every element in upper_half.
#   2. |lower_half| == |upper_half|  OR  |lower_half| == |upper_half| + 1
#      (i.e. lower half may have at most one extra element)
#
# Median:
#   - Even total: average of both tops
#   - Odd total: top of lower_half (which is the middle element)
#
# Time:  O(log n) per add, O(1) per median query
# Space: O(n)
# =============================================================================

class MedianFinder:
    def __init__(self):
        self.lower = []     # max-heap (store negatives): holds smaller half
        self.upper = []     # min-heap: holds larger half

    def add_num(self, num):
        # Step 1: push to lower half (negate for max-heap behaviour)
        heapq.heappush(self.lower, -num)

        # Step 2: ensure ordering invariant — max of lower <= min of upper
        if self.upper and (-self.lower[0]) > self.upper[0]:
            val = -heapq.heappop(self.lower)
            heapq.heappush(self.upper, val)

        # Step 3: rebalance sizes so lower has at most 1 extra element
        if len(self.lower) > len(self.upper) + 1:
            val = -heapq.heappop(self.lower)
            heapq.heappush(self.upper, val)
        elif len(self.upper) > len(self.lower):
            val = heapq.heappop(self.upper)
            heapq.heappush(self.lower, -val)

    def find_median(self):
        if len(self.lower) > len(self.upper):
            return -self.lower[0]                               # middle element
        return (-self.lower[0] + self.upper[0]) / 2.0          # average of two middles


# =============================================================================
# PROBLEM 5 — Task Scheduler (CPU Cooldown)
# =============================================================================
#
# Given a list of CPU tasks (each represented by a letter) and an integer n
# (cooldown period), find the minimum time to execute all tasks.
#
# Rule: the same task cannot run within n intervals of its last run.
#       You may insert idle cycles to satisfy the constraint.
#
# Greedy insight:
#   Always schedule the most frequent remaining task first.
#   Use a max-heap to track task frequencies.
#   Use a queue to hold tasks on cooldown: (available_at_time, frequency).
#
# Time:  O(T log k) where T = total task count, k = unique task types
# Space: O(k)
# =============================================================================

from collections import deque

def least_interval(tasks, n):
    """
    Return the minimum CPU intervals needed to finish all tasks with cooldown n.

    >>> least_interval(["A","A","A","B","B","B"], 2)
    8
    >>> least_interval(["A","A","A","B","B","B"], 0)
    6
    >>> least_interval(["A"], 2)
    1
    """
    count = Counter(tasks)
    # max-heap: negate frequencies because Python has a min-heap
    max_heap = [-freq for freq in count.values()]
    heapq.heapify(max_heap)

    time = 0
    cooldown_queue = deque()   # entries: (next_available_time, neg_frequency)

    while max_heap or cooldown_queue:
        time += 1

        if max_heap:
            freq = heapq.heappop(max_heap) + 1     # run one instance (freq is negative, so +1)
            if freq < 0:                            # task still has remaining runs
                cooldown_queue.append((time + n, freq))
        else:
            # No tasks available — must idle until next task is off cooldown
            time = cooldown_queue[0][0]             # jump to when first task is ready

        # Release tasks whose cooldown has expired
        if cooldown_queue and cooldown_queue[0][0] <= time:
            _, freq = cooldown_queue.popleft()
            heapq.heappush(max_heap, freq)

    return time


# =============================================================================
# PROBLEM 6 — Sliding Window Maximum
# =============================================================================
#
# Given an array and a window size k, return the maximum in each window.
#
# Approach (max-heap with lazy deletion):
#   - Push (value, index) onto a max-heap (negate value for max behaviour).
#   - After each window advance, peek the heap's top.
#     If the top element's index is outside the current window, pop it (lazy).
#   - The heap's top is always the window maximum.
#
# Why "lazy deletion"?
#   We don't immediately remove out-of-window elements.
#   Instead we check the index when we peek the top and skip stale entries.
#   This avoids O(n) scanning to remove specific elements from the heap.
#
# Time:  O(n log n) worst case (each element pushed/popped once)
# Space: O(n) for the heap
#
# Note: O(n) is achievable with a monotonic deque (module 12 pattern).
#       The heap approach is simpler to remember and still interview-acceptable.
# =============================================================================

def max_sliding_window(nums, k):
    """
    Return the max of each sliding window of size k.

    >>> max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3)
    [3, 3, 5, 5, 6, 7]
    >>> max_sliding_window([1], 1)
    [1]
    >>> max_sliding_window([9, 8], 2)
    [9]
    """
    if not nums or k == 0:
        return []

    max_heap = []   # entries: (-value, index)
    result = []

    for i, val in enumerate(nums):
        heapq.heappush(max_heap, (-val, i))

        # Remove elements outside the current window [i-k+1 .. i]
        while max_heap[0][1] < i - k + 1:
            heapq.heappop(max_heap)

        # Window is complete — record maximum
        if i >= k - 1:
            result.append(-max_heap[0][0])

    return result


# =============================================================================
# PROBLEM 7 — K Closest Points to Origin
# =============================================================================
#
# Given a list of (x, y) points, return the k closest to the origin (0, 0).
# Distance is Euclidean: sqrt(x² + y²).
# (We skip sqrt since it's monotone — comparing x²+y² is sufficient.)
#
# Approach: maintain a MAX-heap of size k.
#   - Push (distance, point) onto the heap (negate distance for max-heap).
#   - If the heap grows beyond k, pop the farthest point.
#   - Remaining heap contains the k closest points.
#
# Why MAX-heap of size k for "k CLOSEST"?
#   The root is always the farthest of our current candidates.
#   When a closer point arrives, we discard that farthest candidate.
#   (Mirror of top-k largest using a min-heap.)
#
# Time:  O(n log k)
# Space: O(k)
# =============================================================================

def k_closest_points(points, k):
    """
    Return the k closest points to the origin.

    >>> sorted(k_closest_points([[1,3],[-2,2],[5,8],[0,1]], 2))
    [[-2, 2], [0, 1]]
    >>> k_closest_points([[1,1]], 1)
    [[1, 1]]
    """
    max_heap = []

    for x, y in points:
        dist_sq = x * x + y * y
        # Push negative distance for max-heap behaviour
        heapq.heappush(max_heap, (-dist_sq, [x, y]))
        if len(max_heap) > k:
            heapq.heappop(max_heap)     # discard the farthest point seen so far

    return [point for _, point in max_heap]


# =============================================================================
# TEST RUNNER
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MODULE 16 — HEAPS: Practice Problems")
    print("=" * 60)

    # --- Problem 1: Heap Sort ---
    print("\n[1] Heap Sort")
    arr = [5, 3, 8, 1, 9, 2, 7, 4, 6]
    print(f"  Input:  {arr}")
    print(f"  Sorted: {heap_sort(arr)}")
    assert heap_sort([]) == []
    assert heap_sort([1]) == [1]
    assert heap_sort([3, 1, 2]) == [1, 2, 3]
    print("  All assertions passed.")

    # --- Problem 2: Top-K Largest ---
    print("\n[2] Top-K Largest Elements")
    nums = [3, 1, 5, 12, 2, 11, 7]
    k = 3
    result = sorted(top_k_largest(nums, k))
    print(f"  Input: {nums}, k={k}")
    print(f"  Top-{k} largest: {result}")
    assert result == [7, 11, 12]
    print("  All assertions passed.")

    # --- Problem 3: Merge K Sorted Lists ---
    print("\n[3] Merge K Sorted Lists")
    lists = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
    merged = merge_k_sorted_lists(lists)
    print(f"  Input: {lists}")
    print(f"  Merged: {merged}")
    assert merged == list(range(1, 10))
    assert merge_k_sorted_lists([]) == []
    assert merge_k_sorted_lists([[], [1]]) == [1]
    print("  All assertions passed.")

    # --- Problem 4: Median of Data Stream ---
    print("\n[4] Median of Data Stream")
    mf = MedianFinder()
    stream = [5, 10, 1, 4, 8]
    for num in stream:
        mf.add_num(num)
        print(f"  Added {num:3d} → median = {mf.find_median()}")
    assert mf.find_median() == 5.0
    mf2 = MedianFinder()
    for n in [1, 2]:
        mf2.add_num(n)
    assert mf2.find_median() == 1.5
    print("  All assertions passed.")

    # --- Problem 5: Task Scheduler ---
    print("\n[5] Task Scheduler (CPU Cooldown)")
    tasks1, n1 = ["A", "A", "A", "B", "B", "B"], 2
    tasks2, n2 = ["A", "A", "A", "B", "B", "B"], 0
    print(f"  Tasks={tasks1}, n={n1} → {least_interval(tasks1, n1)} intervals")
    print(f"  Tasks={tasks2}, n={n2} → {least_interval(tasks2, n2)} intervals")
    assert least_interval(tasks1, n1) == 8
    assert least_interval(tasks2, n2) == 6
    print("  All assertions passed.")

    # --- Problem 6: Sliding Window Maximum ---
    print("\n[6] Sliding Window Maximum")
    nums2 = [1, 3, -1, -3, 5, 3, 6, 7]
    k2 = 3
    result2 = max_sliding_window(nums2, k2)
    print(f"  Input: {nums2}, k={k2}")
    print(f"  Window maxima: {result2}")
    assert result2 == [3, 3, 5, 5, 6, 7]
    print("  All assertions passed.")

    # --- Problem 7: K Closest Points ---
    print("\n[7] K Closest Points to Origin")
    points = [[1, 3], [-2, 2], [5, 8], [0, 1]]
    k3 = 2
    closest = sorted(k_closest_points(points, k3))
    print(f"  Points: {points}, k={k3}")
    print(f"  {k3} closest: {closest}")
    assert closest == [[-2, 2], [0, 1]]
    print("  All assertions passed.")

    print("\n" + "=" * 60)
    print("All problems completed successfully.")
    print("=" * 60)
