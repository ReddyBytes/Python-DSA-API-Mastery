# Heaps — Quick Reference Cheatsheet

## Core Properties

```
MIN-HEAP: parent <= children       MAX-HEAP: parent >= children
         1                                  9
        / \                                / \
       3   2                              7   8
      / \ / \                            / \ / \
     5  4 6  7                          2  3 4  1

Parent of i: (i-1)//2
Left child:  2*i + 1
Right child: 2*i + 2
```

---

## Complexity Table

| Operation        | Time       | Notes                              |
|------------------|------------|------------------------------------|
| heappush         | O(log n)   | Sift up                            |
| heappop          | O(log n)   | Sift down, returns min             |
| heapify          | O(n)       | NOT O(n log n) — build from list   |
| peek (h[0])      | O(1)       | Min element only                   |
| heappushpop      | O(log n)   | Push then pop — more efficient     |
| heapreplace      | O(log n)   | Pop then push — more efficient     |
| nlargest(k, h)   | O(n log k) | Returns k largest                  |
| nsmallest(k, h)  | O(n log k) | Returns k smallest                 |

---

## Python heapq Quick Reference

```python
import heapq

h = []
heapq.heappush(h, 3)            # push
val = heapq.heappop(h)          # pop min
min_val = h[0]                  # peek min (no pop)

heapq.heapify(lst)              # in-place, O(n)

# Top K: O(n log k) — better than sort when k << n
heapq.nlargest(k, iterable)     # returns list, largest first
heapq.nsmallest(k, iterable)    # returns list, smallest first

# Optimized push+pop combos (avoid extra sift operations)
heapq.heappushpop(h, x)         # push x, then pop min (min of x and current min)
heapq.heapreplace(h, x)         # pop min, then push x (heap must be non-empty)
# heapreplace is faster than heappop + heappush when x > current min
```

### Max-Heap Trick (heapq only provides min-heap)

```python
# Push negated values, negate on pop
heapq.heappush(h, -x)
max_val = -heapq.heappop(h)

# With tuples: negate the priority field only
heapq.heappush(h, (-priority, item))
priority, item = heapq.heappop(h)
priority = -priority
```

---

## Custom Heap with Tuples

```python
# (priority, item) — Python compares tuples lexicographically
heapq.heappush(h, (1, 'low'))
heapq.heappush(h, (0, 'high'))
priority, item = heapq.heappop(h)   # (0, 'high')

# Tie-breaking: add a counter to avoid comparing non-comparable items
import itertools
counter = itertools.count()
heapq.heappush(h, (priority, next(counter), item))
```

---

## Key Patterns

### Top K Elements (min-heap of size K)

```python
def top_k_largest(nums, k):
    heap = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)     # evict smallest — keep K largest
    return list(heap)               # heap[0] = k-th largest

# One-liner (only if full scan is acceptable)
return heapq.nlargest(k, nums)
```

### K-th Largest Element

```python
def kth_largest(nums, k):
    heap = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0]                  # root = k-th largest
```

### Merge K Sorted Lists

```python
def merge_k_sorted(lists):
    heap = []
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))   # (val, list_idx, elem_idx)

    result = []
    while heap:
        val, i, j = heapq.heappop(heap)
        result.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j+1], i, j+1))
    return result
# Time: O(N log k) where N = total elements, k = number of lists
```

### Median from Data Stream (Two Heaps)

```python
class MedianFinder:
    def __init__(self):
        self.lo = []    # max-heap (negated) — lower half
        self.hi = []    # min-heap — upper half

    def addNum(self, num):
        heapq.heappush(self.lo, -num)           # push to max-heap
        heapq.heappush(self.hi, -heapq.heappop(self.lo))  # balance

        if len(self.hi) > len(self.lo):         # keep lo >= hi size
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def findMedian(self):
        if len(self.lo) > len(self.hi):
            return -self.lo[0]
        return (-self.lo[0] + self.hi[0]) / 2.0
# Invariant: lo holds lower half (max at top), hi holds upper half (min at top)
```

---

## Heap Sort Template

```python
def heap_sort(arr):
    heapq.heapify(arr)              # O(n)
    return [heapq.heappop(arr) for _ in range(len(arr))]   # O(n log n)

# In-place (max-heap manual):
def heap_sort_inplace(arr):
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):    # build max-heap
        _sift_down(arr, i, n)
    for i in range(n - 1, 0, -1):           # extract max to end
        arr[0], arr[i] = arr[i], arr[0]
        _sift_down(arr, 0, i)
```

---

## When Heap Beats Sorting

| Scenario                          | Use Heap  | Reason                          |
|-----------------------------------|-----------|---------------------------------|
| Streaming data (no full dataset)  | YES       | Sort requires all data upfront  |
| Top-K, K << N                     | YES       | O(N log K) vs O(N log N)        |
| Repeated min/max queries          | YES       | O(log n) per op vs O(n) rescan  |
| Need full sorted order            | NO        | Sort is cleaner                 |
| K is close to N                   | NO        | Sort comparable or better       |

---

## heappushpop vs heapreplace

```python
# heappushpop(h, x): push x THEN pop min
# Safe on empty heap. Returns min(x, current_min).
val = heapq.heappushpop(h, x)

# heapreplace(h, x): pop min THEN push x
# UNSAFE on empty heap. Faster when x >= h[0].
# Use for sliding window min-heap where you know new value is larger.
val = heapq.heapreplace(h, x)

# Use case: maintain fixed-size heap efficiently
# heapreplace is ~15% faster than heappop + heappush
```

---

## Common Mistakes

```
MISTAKE 1: Forgetting max-heap negation
  Wrong:  heappush(h, x)  then  heappop(h)  for max
  Right:  heappush(h, -x) then -heappop(h)

MISTAKE 2: Assuming heapify is O(n log n)
  heapify() is O(n) — safe to use on large lists

MISTAKE 3: Using nlargest/nsmallest for large K
  For k ~ n, just sort. nlargest is O(n log k).
  Rule of thumb: k < n/10 → use heap; else → sort

MISTAKE 4: Modifying heap elements directly
  Never do h[i] = new_val — breaks heap invariant
  Must pop and re-push (or use lazy deletion pattern)

MISTAKE 5: Comparing non-comparable items in tuples
  heappush(h, (1, [1,2,3]))  →  crashes if priorities tie
  Fix: add unique counter as tiebreaker

MISTAKE 6: heapreplace on empty heap → IndexError
  Always check: if h: heapreplace(h, x)
```

---

## Interview Signals → Use Heap

```
"K largest / K smallest"         → min-heap of size K
"K-th largest / smallest"        → min-heap of size K
"Merge K sorted ..."             → heap with (val, list_idx, elem_idx)
"Median / running median"        → two heaps (lo max-heap, hi min-heap)
"Task scheduler / priority"      → max-heap on frequency
"Sliding window maximum"         → deque (not heap — O(n))
"Continuous stream, top-K"       → heap beats full sort
```
