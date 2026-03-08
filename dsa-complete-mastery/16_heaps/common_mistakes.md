# Heaps — Common Mistakes & Error Prevention

---

## Mistake 1: Python heapq Is Min-Heap Only — Forgetting to Negate for Max-Heap

### The Bug
`heapq` always maintains the smallest element at index 0. Using it directly for
"find K largest elements" gives you the K SMALLEST instead. You must negate values
to simulate a max-heap.

### Wrong Code
```python
import heapq

def k_largest_wrong(nums, k):
    heap = []
    for num in nums:
        heapq.heappush(heap, num)    # BUG: min-heap, smallest is at top

    result = []
    for _ in range(k):
        result.append(heapq.heappop(heap))   # pops smallest, not largest
    return result
```

### Correct Code — Option A: Negate Values
```python
import heapq

def k_largest_negate(nums, k):
    heap = []
    for num in nums:
        heapq.heappush(heap, -num)   # store negated value

    result = []
    for _ in range(k):
        result.append(-heapq.heappop(heap))  # negate again on the way out
    return result
```

### Correct Code — Option B: Use a Min-Heap of Size K (Most Efficient)
```python
def k_largest_min_heap(nums, k):
    # Keep a min-heap of the k largest seen so far.
    # The root is the SMALLEST of the top-k — easy to compare and evict.
    heap = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)   # evicts the smallest of the top-k candidates
    return sorted(heap, reverse=True)
```

### Test Cases That Expose the Bug
```python
import heapq

nums = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
k = 3

wrong_result = k_largest_wrong(nums, k)
correct_result = k_largest_negate(nums, k)
efficient_result = k_largest_min_heap(nums, k)

print("Wrong (gives smallest):", sorted(wrong_result))      # [1, 1, 2] — WRONG
print("Correct (negation):", sorted(correct_result))        # [5, 6, 9] — CORRECT
print("Correct (min-heap k):", efficient_result)            # [5, 6, 9] — CORRECT

assert sorted(wrong_result) != [5, 6, 9], "Wrong version should NOT give largest"
assert sorted(correct_result) == [5, 6, 9]
assert efficient_result == [9, 6, 5]
print("All max-heap tests passed")
```

### Memory Aid
> "Python heap = min-heap always. For max, flip the sign. Flip it back when you pop."
> Common pattern: `heappush(heap, (-priority, item))` for priority queues.

---

## Mistake 2: Tuple Ordering — Non-Comparable Items Cause TypeError

### The Bug
When two tuples have equal first elements, Python compares the second element.
If the second element is a custom object (or any non-comparable type like `dict`),
Python raises `TypeError: '<' not supported`.

### Wrong Code
```python
import heapq

def schedule_tasks_wrong(tasks):
    # tasks = list of (priority, task_dict)
    heap = []
    for priority, task in tasks:
        heapq.heappush(heap, (priority, task))   # BUG: if priorities tie,
                                                  # Python tries to compare task dicts
    results = []
    while heap:
        _, task = heapq.heappop(heap)
        results.append(task)
    return results

# This crashes when priorities are equal
tasks = [
    (1, {"name": "task_a", "duration": 5}),
    (1, {"name": "task_b", "duration": 3}),   # same priority!
]
# schedule_tasks_wrong(tasks)  # TypeError: '<' not supported between dict instances
```

### Correct Code — Use a Counter as Tiebreaker
```python
import heapq
import itertools

def schedule_tasks_correct(tasks):
    counter = itertools.count()        # unique, always-increasing integer
    heap = []
    for priority, task in tasks:
        # Tuple: (priority, unique_count, task)
        # If priorities tie, count breaks the tie — count is always unique,
        # so Python never needs to compare the task object.
        heapq.heappush(heap, (priority, next(counter), task))

    results = []
    while heap:
        _, _, task = heapq.heappop(heap)
        results.append(task)
    return results
```

### Correct Code — For Simple Cases, Use a Dataclass with `__lt__`
```python
from dataclasses import dataclass, field
from typing import Any
import heapq

@dataclass(order=False)
class HeapItem:
    priority: int
    item: Any = field(compare=False)    # excluded from comparisons

    def __lt__(self, other):
        return self.priority < other.priority

def schedule_with_dataclass(tasks):
    heap = []
    for priority, task in tasks:
        heapq.heappush(heap, HeapItem(priority, task))
    return [heapq.heappop(heap).item for _ in range(len(heap))]
```

### Test Cases That Expose the Bug
```python
import heapq, itertools

tasks = [
    (1, {"name": "deploy", "duration": 10}),
    (1, {"name": "test",   "duration": 5}),
    (2, {"name": "review", "duration": 3}),
]

# Wrong version raises TypeError — uncomment to see:
# schedule_tasks_wrong(tasks)

# Correct version works
results = schedule_tasks_correct(tasks)
assert results[0]["name"] in ("deploy", "test")   # both priority 1
assert results[2]["name"] == "review"             # priority 2 comes last
print("Tuple tiebreaker test passed:", [r["name"] for r in results])

# String objects ARE comparable, so strings don't hit this bug:
heap = []
heapq.heappush(heap, (1, "b"))
heapq.heappush(heap, (1, "a"))
assert heapq.heappop(heap) == (1, "a")   # "a" < "b" — works fine
print("String comparison test passed (strings are comparable)")
```

---

## Mistake 3: Calling heapify() on Streaming Data

### The Bug
`heapify()` runs in O(n) on a list that is ALREADY fully populated.
Calling `heapify()` inside a loop (after each new element) does O(n) work every
iteration — total cost O(n²) instead of O(n log n).
For streaming data, always use `heappush()`.

### Wrong Code
```python
import heapq

def build_heap_wrong(stream):
    heap = []
    for item in stream:
        heap.append(item)
        heapq.heapify(heap)    # BUG: O(n) work on every iteration = O(n²) total
    return heap
```

### Correct Code — heappush for Streaming
```python
import heapq

def build_heap_streaming(stream):
    heap = []
    for item in stream:
        heapq.heappush(heap, item)   # O(log n) per item = O(n log n) total
    return heap
```

### Correct Code — heapify for Batch (When You Have All Items Upfront)
```python
import heapq

def build_heap_batch(data):
    heap = list(data)           # copy or just use the list directly
    heapq.heapify(heap)         # O(n) — optimal when all data is available
    return heap
```

### When to Use Which
```
heapify(list)          O(n)        Use when ALL elements are already in a list
heappush(heap, item)   O(log n)    Use when elements arrive one at a time (streaming)

Building from scratch with n pushes = O(n log n)
Building with heapify on complete list = O(n)

If you have the data: heapify is 2-3x faster in practice.
If data streams in: heappush is the only correct option.
```

### Test Cases
```python
import heapq, time, random

data = list(range(100_000))
random.shuffle(data)

# Batch: use heapify
batch = list(data)
heapq.heapify(batch)
assert batch[0] == 0   # min element at root

# Streaming: use heappush
stream_heap = []
for item in data:
    heapq.heappush(stream_heap, item)
assert stream_heap[0] == 0

# Both produce valid heaps
assert heapq.heappop(batch) == 0
assert heapq.heappop(stream_heap) == 0
print("heapify vs heappush test passed")
```

---

## Mistake 4: heap[0] vs heappop() — Confusing Peek and Extract

### The Bug
`heap[0]` is a O(1) peek at the minimum WITHOUT removing it.
`heappop()` is O(log n) and REMOVES the minimum.
Using `heappop()` when you only want to look, or using `heap[0]` when you expect
removal, produces silent logic bugs.

### Wrong Code
```python
import heapq

def process_min_wrong(heap):
    # Intent: "if the smallest element is negative, process it"
    while heap[0] < 0:               # peek is fine here
        val = heap[0]                # BUG: looking at minimum but not removing it
        print(f"Processing {val}")
        # val is never removed — infinite loop!
```

### Wrong Code — Opposite Direction
```python
def get_running_minimum_wrong(nums):
    heap = list(nums)
    heapq.heapify(heap)
    minimums = []
    for _ in range(len(nums)):
        minimums.append(heapq.heappop(heap))   # BUG: destroys the heap for later use
    return minimums
    # After this function, heap is empty — cannot be used again
```

### Correct Code
```python
import heapq

def process_min_correct(heap):
    # To consume: use heappop
    while heap and heap[0] < 0:
        val = heapq.heappop(heap)     # removes and returns
        print(f"Processing {val}")

def peek_minimum(heap):
    # To inspect without consuming: use index 0
    if heap:
        return heap[0]                # O(1), heap unchanged
    return None

def get_sorted_copy(nums):
    # If you want sorted output AND want to keep the heap intact:
    heap = list(nums)
    heapq.heapify(heap)
    return [heapq.heappop(heap) for _ in range(len(heap))]
    # Note: original nums is unchanged; heap was a copy
```

### Test Cases
```python
import heapq

heap = [3, 1, 4, 1, 5, 9]
heapq.heapify(heap)

# Peek does not change heap
min_val = heap[0]
assert min_val == 1
assert len(heap) == 6    # still 6 elements

# Pop does change heap
popped = heapq.heappop(heap)
assert popped == 1
assert len(heap) == 5    # now 5 elements

# Verify heap still valid after pop
assert heap[0] == 1      # second minimum is now at root
print("Peek vs pop test passed")
```

---

## Mistake 5: Wrong Strategy — Max-Heap vs Min-Heap of Size K for Top-K

### The Bug
For streaming top-K, using a max-heap requires storing ALL n elements before extracting
the K largest. A min-heap of size K processes each element in O(log k) and never
stores more than K elements.

### Wrong Approach — Max-Heap Stores Everything
```python
import heapq

def top_k_max_heap_wrong(stream, k):
    # BUG: must store ALL elements before you can extract top-k
    # For n=10^9, k=10 — you store a billion items just to get 10
    max_heap = []
    for item in stream:
        heapq.heappush(max_heap, -item)    # negate for max behavior

    result = []
    for _ in range(k):
        result.append(-heapq.heappop(max_heap))
    return result
    # Space: O(n) — stores everything
    # Time:  O(n log n) — same as sorting
```

### Correct Approach — Min-Heap of Size K
```python
import heapq

def top_k_min_heap_correct(stream, k):
    # Maintain a min-heap of exactly k elements.
    # The root is the SMALLEST of our current top-k candidates.
    # Any new element larger than the root beats our weakest candidate.
    heap = []
    for item in stream:
        if len(heap) < k:
            heapq.heappush(heap, item)
        elif item > heap[0]:               # new item beats the current minimum
            heapq.heapreplace(heap, item)  # heapreplace is faster than pop+push
    return sorted(heap, reverse=True)
    # Space: O(k) — never stores more than k elements
    # Time:  O(n log k) — log k per comparison, not log n
```

### When Each Is Appropriate
```
STREAMING data, unknown size, memory-constrained:
    Use min-heap of size k
    Space O(k), Time O(n log k)

BATCH data, already in memory, need ALL sorted:
    Use sorted() or heapq.nlargest(k, data)
    heapq.nlargest is optimized and uses the min-heap approach internally

INTERACTIVE / priority queue (insert + extract-max repeatedly):
    Use max-heap (negate values in Python)
    Each insert/extract is O(log n)
```

### Performance Comparison Test
```python
import heapq, random, time

n = 1_000_000
k = 10
data = [random.randint(1, 10**9) for _ in range(n)]

# Method 1: min-heap of size k
start = time.time()
result_k = top_k_min_heap_correct(data, k)
time_k = time.time() - start

# Method 2: Python's built-in (uses heap internally)
start = time.time()
result_builtin = heapq.nlargest(k, data)
time_builtin = time.time() - start

assert result_k == result_builtin, f"{result_k} != {result_builtin}"
print(f"Min-heap size-k: {time_k:.3f}s")
print(f"heapq.nlargest:  {time_builtin:.3f}s")
print(f"Both correct: {result_k}")
```

---

## Mistake 6: Lazy Deletion — When It Helps and When It Hides Bugs

### What Lazy Deletion Is
Instead of removing an element from a heap (which requires O(n) to find it),
you mark it as "invalid" and skip it when it comes out. This is useful when
the element's priority changes in Dijkstra's algorithm.

### When Lazy Deletion Is Correct — Dijkstra's Algorithm
```python
import heapq

def dijkstra_with_lazy_deletion(graph, start):
    # graph[u] = [(weight, v), ...]
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    heap = [(0, start)]

    while heap:
        d, u = heapq.heappop(heap)

        # LAZY DELETION: if we already found a shorter path, skip this stale entry
        if d > dist[u]:     # this is the "lazy" check — correct and intentional
            continue

        for weight, v in graph.get(u, []):
            new_dist = d + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))   # old entry still in heap (stale)

    return dist
```

### When Lazy Deletion Causes Bugs — Median of a Stream
```python
import heapq

class MedianFinderBuggy:
    def __init__(self):
        self.low = []    # max-heap (negated): lower half
        self.high = []   # min-heap: upper half
        self.to_remove = {}   # lazy deletion map: value -> count to ignore

    def add_num(self, num):
        heapq.heappush(self.low, -num)
        # Balance heaps
        if self.low and self.high and (-self.low[0]) > self.high[0]:
            heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.low) > len(self.high) + 1:
            heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def find_median(self):
        # BUG: if you implement remove() with lazy deletion but forget to
        # account for "virtual size" (actual size minus pending removals),
        # the balance check above uses the WRONG sizes and the median is wrong.
        if len(self.low) > len(self.high):
            return -self.low[0]
        return (-self.low[0] + self.high[0]) / 2
```

### Correct Pattern — Lazy Deletion with Explicit Size Tracking
```python
import heapq
from collections import defaultdict

class MedianFinderWithLazyDelete:
    """Supports add and remove in O(log n), find_median in O(log n) worst case."""

    def __init__(self):
        self.low = []          # max-heap (negated)
        self.high = []         # min-heap
        self.to_remove = defaultdict(int)
        self._low_size = 0     # VIRTUAL size: actual heap minus pending removals
        self._high_size = 0

    def _purge_low(self):
        """Remove invalid (pending-deletion) elements from the top of low."""
        while self.low and self.to_remove[-self.low[0]] > 0:
            self.to_remove[-self.low[0]] -= 1
            heapq.heappop(self.low)

    def _purge_high(self):
        """Remove invalid elements from the top of high."""
        while self.high and self.to_remove[self.high[0]] > 0:
            self.to_remove[self.high[0]] -= 1
            heapq.heappop(self.high)

    def add_num(self, num):
        if not self.low or num <= -self.low[0]:
            heapq.heappush(self.low, -num)
            self._low_size += 1
        else:
            heapq.heappush(self.high, num)
            self._high_size += 1
        self._rebalance()

    def remove_num(self, num):
        self.to_remove[num] += 1   # mark for lazy removal
        if num <= -self.low[0]:
            self._low_size -= 1
            self._purge_low()
        else:
            self._high_size -= 1
            self._purge_high()
        self._rebalance()

    def _rebalance(self):
        if self._low_size > self._high_size + 1:
            self._purge_low()
            val = -heapq.heappop(self.low)
            self._low_size -= 1
            heapq.heappush(self.high, val)
            self._high_size += 1
            self._purge_high()
        elif self._high_size > self._low_size:
            self._purge_high()
            val = heapq.heappop(self.high)
            self._high_size -= 1
            heapq.heappush(self.low, -val)
            self._low_size += 1
            self._purge_low()

    def find_median(self):
        self._purge_low()
        self._purge_high()
        if self._low_size > self._high_size:
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2.0
```

### Test Cases
```python
# Dijkstra lazy deletion test
graph = {
    'A': [(1, 'B'), (4, 'C')],
    'B': [(2, 'C'), (5, 'D')],
    'C': [(1, 'D')],
    'D': []
}
dist = dijkstra_with_lazy_deletion(graph, 'A')
assert dist['D'] == 4, f"Expected 4, got {dist['D']}"  # A->B->C->D = 1+2+1
print("Dijkstra test passed:", dist)

# Median finder test
mf = MedianFinderWithLazyDelete()
for n in [5, 3, 8, 1, 9]:
    mf.add_num(n)
# Sorted: [1, 3, 5, 8, 9] — median is 5
assert mf.find_median() == 5.0

mf.remove_num(5)
# Remaining sorted: [1, 3, 8, 9] — median is (3+8)/2 = 5.5
assert mf.find_median() == 5.5
print("Lazy deletion median test passed")
```

### Lazy Deletion: Rules of Thumb
```
USE lazy deletion when:
  - Elements' priorities change (Dijkstra, A*)
  - Removals are rare compared to insertions
  - You track "virtual size" correctly alongside real heap size

AVOID lazy deletion when:
  - The median or any order-sensitive statistic depends on correct size
  - You forget to track virtual size separately
  - Stale entries accumulate and bloat memory (add a cleanup threshold)
```

---

## Quick Reference Summary

| Mistake | Root Cause | One-Line Fix |
|---|---|---|
| Min-heap used as max-heap | heapq always gives minimum | Negate values: `heappush(h, -val)` |
| TypeError on equal priorities | Python compares next tuple element | Add counter: `(priority, count, item)` |
| heapify in a loop | Batch operation misused on stream | Use `heappush` for streaming data |
| heappop when only peeking | Destroys element unintentionally | Use `heap[0]` for O(1) peek |
| Max-heap for top-K streaming | Stores all n elements | Min-heap of size K: O(n log k), O(k) space |
| Lazy deletion with wrong size | Virtual size not tracked | Maintain separate `_size` counter |
