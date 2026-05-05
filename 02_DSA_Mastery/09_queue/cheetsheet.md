## QUEUE — QUICK REFERENCE CHEATSHEET

```
┌────────────────────────────────────────────────┐
│  FIFO — First In, First Out                    │
│  Think: BFS, level-order, scheduling, streams  │
└────────────────────────────────────────────────┘
```

---

## OPERATIONS COMPLEXITY

```
┌───────────────┬─────────────────┬──────────────────┬──────────────────┐
│ Operation     │ deque           │ queue.Queue      │ list (BAD)       │
├───────────────┼─────────────────┼──────────────────┼──────────────────┤
│ enqueue       │ O(1) append     │ O(1) put()       │ O(1) append      │
│ dequeue       │ O(1) popleft()  │ O(1) get()       │ O(n) pop(0) !!!  │
│ peek front    │ O(1)  dq[0]     │ N/A              │ O(1)  lst[0]     │
│ peek back     │ O(1)  dq[-1]    │ N/A              │ O(1)  lst[-1]    │
│ isEmpty       │ O(1)  not dq    │ O(1) empty()     │ O(1)             │
│ Size          │ O(1)  len(dq)   │ O(1) qsize()     │ O(1)             │
│ Thread-safe   │ No              │ YES              │ No               │
└───────────────┴─────────────────┴──────────────────┴──────────────────┘
NEVER use list.pop(0) as queue — it's O(n). Always use deque.
```

---

## PYTHON QUEUE SYNTAX

```python
from collections import deque

q = deque()
q.append(x)         # enqueue (back)
q.popleft()         # dequeue (front) — O(1)
q[0]                # peek front
q[-1]               # peek back
if q: ...           # isEmpty

# Thread-safe alternative (slower — only for concurrency)
from queue import Queue
q = Queue()
q.put(x)
q.get()
q.empty()
```

---

## BFS TEMPLATE USING QUEUE

```python
from collections import deque

def bfs(graph, start):
    visited = {start}
    queue = deque([start])

    while queue:
        node = queue.popleft()
        # process node
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

# Level-order BFS (track levels separately)
def level_order(root):
    if not root: return []
    result = []
    queue = deque([root])

    while queue:
        level = []
        for _ in range(len(queue)):    # process entire level at once
            node = queue.popleft()
            level.append(node.val)
            if node.left:  queue.append(node.left)
            if node.right: queue.append(node.right)
        result.append(level)

    return result
```

---

## HEAPQ — PRIORITY QUEUE (MIN-HEAP)

```python
import heapq

heap = []
heapq.heappush(heap, val)     # push — O(log n)
heapq.heappop(heap)           # pop min — O(log n)
heap[0]                       # peek min — O(1), no removal
heapq.heapify(lst)            # convert list in-place — O(n)
heapq.nlargest(k, lst)        # top k largest — O(n log k)
heapq.nsmallest(k, lst)       # top k smallest — O(n log k)

# Max-heap: negate values
heapq.heappush(heap, -val)
max_val = -heapq.heappop(heap)

# Heap with tuples — sorted by first element
heapq.heappush(heap, (priority, item))
```

---

## PRIORITY QUEUE PATTERNS

### Top K Elements
```python
def top_k_frequent(nums, k):
    from collections import Counter
    import heapq
    count = Counter(nums)
    # min-heap of size k: keep k largest frequencies
    return heapq.nlargest(k, count, key=count.get)

    # Manual approach — heap of (freq, num)
    heap = []
    for num, freq in count.items():
        heapq.heappush(heap, (freq, num))
        if len(heap) > k:
            heapq.heappop(heap)        # evict smallest frequency
    return [num for freq, num in heap]
```

### K-th Largest Element
```python
def kth_largest(nums, k):
    heap = nums[:k]
    heapq.heapify(heap)                # min-heap of size k
    for n in nums[k:]:
        if n > heap[0]:
            heapq.heapreplace(heap, n) # pop + push in one step
    return heap[0]                     # min of top-k = k-th largest
```

### Merge K Sorted Lists
```python
def merge_k_lists(lists):
    heap = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    dummy = cur = ListNode(0)
    while heap:
        val, i, node = heapq.heappop(heap)
        cur.next = node
        cur = cur.next
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next
```

---

## MONOTONIC DEQUE (SLIDING WINDOW MAXIMUM)

```python
def max_sliding_window(nums, k):
    dq = deque()        # stores indices; front = max of current window
    result = []

    for i, n in enumerate(nums):
        # Remove indices outside window
        while dq and dq[0] < i - k + 1:
            dq.popleft()
        # Remove smaller elements from back (maintain decreasing order)
        while dq and nums[dq[-1]] < n:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])   # front = window maximum

    return result
# Time: O(n) — each element pushed/popped at most once
```

---

## DEQUE AS SLIDING WINDOW

```python
# Sliding window with fixed size using deque
def sliding_window_avg(nums, k):
    window = deque(maxlen=k)   # maxlen auto-evicts oldest element
    result = []
    total = 0
    for n in nums:
        if len(window) == k:
            total -= window[0]      # remove oldest before maxlen evicts
        window.append(n)
        total += n
        if len(window) == k:
            result.append(total / k)
    return result
```

---

## CIRCULAR QUEUE CONCEPT

```python
class CircularQueue:
    def __init__(self, k):
        self.q = [0] * k
        self.head = self.tail = -1
        self.size = k

    def enqueue(self, val):
        if self.is_full(): return False
        self.tail = (self.tail + 1) % self.size    # wrap around
        self.q[self.tail] = val
        if self.head == -1: self.head = 0
        return True

    def dequeue(self):
        if self.is_empty(): return False
        if self.head == self.tail: self.head = self.tail = -1
        else: self.head = (self.head + 1) % self.size
        return True

    def is_empty(self): return self.head == -1
    def is_full(self):  return (self.tail + 1) % self.size == self.head
```

---

## WHEN TO USE WHAT

```
┌─────────────────┬──────────────────────────────────────────────────┐
│ Need            │ Use                                              │
├─────────────────┼──────────────────────────────────────────────────┤
│ BFS traversal   │ collections.deque (FIFO)                         │
│ Shortest path   │ deque (unweighted) / heapq (weighted = Dijkstra) │
│ Priority order  │ heapq (min-heap) / negate for max-heap           │
│ Top K elements  │ heapq.nlargest / nsmallest or manual heap of k   │
│ Sliding window  │ deque (monotonic) or deque(maxlen=k)             │
│ Thread-safe     │ queue.Queue                                      │
│ Both ends O(1)  │ collections.deque                                │
└─────────────────┴──────────────────────────────────────────────────┘
```

---

## COMMON GOTCHAS

```
TRAP 1: list.pop(0) is O(n) — ALWAYS use deque.popleft()

TRAP 2: heap comparison on equal priority with non-comparable objects
  Use (priority, counter, item) — counter breaks ties deterministically.
  import itertools; counter = itertools.count()
  heapq.heappush(heap, (priority, next(counter), item))

TRAP 3: Modifying heap list directly — breaks heap invariant
  Only modify via heappush/heappop/heapreplace.

TRAP 4: Monotonic deque — wrong eviction order
  Evict expired indices from FRONT (popleft), evict smaller from BACK (pop).

TRAP 5: heapq.heapreplace vs heappushpop
  heapreplace: pop then push (heap must be non-empty)
  heappushpop: push then pop (slightly different semantics)
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Visual Explanation](./visual_explanation.md) &nbsp;|&nbsp; **Next:** [Real World Usage →](./real_world_usage.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
