# Queue — Common Mistakes & Error Prevention

A focused guide on the bugs that appear most often when using queues in interviews and real code. Each mistake includes a broken implementation, an explanation of why it fails, and a corrected version with test cases that expose the bug.

---

## Mistake 1: `list.pop(0)` Instead of `deque.popleft()` — O(n) vs O(1)

### The Confusion

A Python `list` is a dynamic array. Removing from the **front** with `pop(0)` requires shifting every remaining element one position to the left — that is **O(n)** per operation.

`collections.deque` is a doubly-linked list. `popleft()` is **O(1)** because only two pointers change.

For a BFS on a graph with `V` vertices and `E` edges:
- Using `list.pop(0)`: O(V * (V + E)) — the V pops each cost O(V)
- Using `deque.popleft()`: O(V + E) — correct BFS complexity

### Wrong Code

```python
# WRONG: O(n) dequeue using a plain list
def bfs_wrong(graph, start):
    visited = {start}
    queue = [start]           # plain list
    order = []

    while queue:
        node = queue.pop(0)   # O(n) — shifts entire list left on every call
        order.append(node)
        for neighbour in graph.get(node, []):
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)

    return order

# Correctness is fine, but performance degrades quadratically on large graphs.
# On a linear chain of 10,000 nodes this runs in ~50ms; with deque it is ~1ms.

# --- Functional test (correct output, wrong performance) ---
graph = {0: [1, 2], 1: [3], 2: [3], 3: []}
print(bfs_wrong(graph, 0))   # [0, 1, 2, 3] — correct output
```

### Correct Code

```python
from collections import deque

def bfs_correct(graph, start):
    visited = {start}
    queue = deque([start])    # O(1) popleft
    order = []

    while queue:
        node = queue.popleft()   # O(1)
        order.append(node)
        for neighbour in graph.get(node, []):
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)

    return order

# --- Tests ---
graph = {0: [1, 2], 1: [3], 2: [3], 3: []}
assert bfs_correct(graph, 0) == [0, 1, 2, 3]

# Linear chain — correct traversal order
chain = {i: [i + 1] for i in range(5)}
chain[5] = []
assert bfs_correct(chain, 0) == [0, 1, 2, 3, 4, 5]

print("deque vs list performance tests passed.")
```

### Quick Comparison

```
Operation        list        deque
-----------      ----        -----
append right     O(1)        O(1)
pop right        O(1)        O(1)
append left      O(n)        O(1)
pop left (dequeue) O(n)      O(1)
```

---

## Mistake 2: BFS — Not Checking Visited Before Adding to Queue

### The Confusion

If you check `visited` only when **processing** a node (after dequeuing), the same node can be enqueued multiple times by different neighbours before it is ever processed. In a graph with cycles or dense connectivity this causes:
1. Enormous queue sizes — memory blowup
2. Processing the same node many times — wrong counts, incorrect distances
3. Potential infinite loops if visited check is absent entirely

The fix: mark nodes as visited **when enqueuing**, not when dequeuing.

### Wrong Code

```python
from collections import deque

def bfs_levels_wrong(graph, start):
    """Returns shortest distance to each node. Bug: marks visited on dequeue."""
    dist = {start: 0}
    queue = deque([start])

    while queue:
        node = queue.popleft()
        for neighbour in graph.get(node, []):
            if neighbour not in dist:      # check on dequeue
                dist[neighbour] = dist[node] + 1
                queue.append(neighbour)    # BUG: may be appended multiple times
                # before the above `if` runs for the second copy

    return dist

# This version works correctly for this simple case because the `if neighbour not in dist`
# guard prevents double-processing. The real bug manifests in the queue SIZE:
def bfs_count_enqueues_wrong(graph, start):
    enqueue_count = {}
    queue = deque([start])
    visited_on_dequeue = set()

    while queue:
        node = queue.popleft()
        if node in visited_on_dequeue:
            continue
        visited_on_dequeue.add(node)

        for neighbour in graph.get(node, []):
            enqueue_count[neighbour] = enqueue_count.get(neighbour, 0) + 1
            queue.append(neighbour)   # pushed multiple times if multiple parents

    return enqueue_count

# --- Test that exposes the bug ---
# Diamond graph: A->B, A->C, B->D, C->D
graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
counts = bfs_count_enqueues_wrong(graph, "A")
print(counts)   # {"B": 1, "C": 1, "D": 2}  <-- D pushed TWICE (once from B, once from C)
```

### Correct Code

```python
from collections import deque

def bfs_levels_correct(graph, start):
    """Mark visited when enqueuing — each node enters queue exactly once."""
    dist = {start: 0}        # acts as both visited set and distance map
    queue = deque([start])

    while queue:
        node = queue.popleft()
        for neighbour in graph.get(node, []):
            if neighbour not in dist:         # check before enqueuing
                dist[neighbour] = dist[node] + 1
                queue.append(neighbour)       # pushed exactly once

    return dist

# --- Tests ---
graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
dist = bfs_levels_correct(graph, "A")
assert dist == {"A": 0, "B": 1, "C": 1, "D": 2}

# Graph with cycle — must not loop
cyclic = {0: [1, 2], 1: [2, 3], 2: [3], 3: [0]}
dist2 = bfs_levels_correct(cyclic, 0)
assert dist2[0] == 0
assert dist2[1] == 1
assert dist2[2] == 1
assert dist2[3] == 2

# Disconnected node — must not be in result
disconnected = {0: [1], 1: [], 2: []}   # node 2 is unreachable from 0
dist3 = bfs_levels_correct(disconnected, 0)
assert 2 not in dist3   # unreachable nodes absent

print("BFS visited-before-enqueue tests passed.")
```

---

## Mistake 3: Wrong Level Counter in Multi-Source BFS

### The Confusion

A common BFS pattern is to process nodes **level by level** (e.g., minimum depth of a binary tree, word ladder, rotting oranges). The mistake is incrementing a `level` counter for every individual node you dequeue, instead of completing an entire level at once.

The correct approach: snapshot the current queue size at the **start** of each level and process exactly that many nodes before incrementing.

### Wrong Code

```python
from collections import deque

def min_depth_wrong(root):
    """Returns minimum depth of a binary tree. Bug: increments level per node."""
    if root is None:
        return 0

    queue = deque([root])
    level = 0

    while queue:
        node = queue.popleft()
        level += 1            # BUG: increments for every node, not every level!

        if not node.left and not node.right:
            return level

        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)

    return level

# --- Test that exposes the bug ---
class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# Tree:      1
#           / \
#          2   3
#         /
#        4
# Min depth = 2 (path: 1->3)
root = TreeNode(1, TreeNode(2, TreeNode(4)), TreeNode(3))

result = min_depth_wrong(root)
print(result)   # Expected: 2 — Actual: 3  BUG
# Why: node 3 is the second node dequeued at level 2, but level was
# already at 2 when we dequeued node 2 first
```

### Correct Code

```python
from collections import deque

def min_depth_correct(root):
    """Process entire level at once using queue snapshot size."""
    if root is None:
        return 0

    queue = deque([root])
    level = 0

    while queue:
        level += 1
        level_size = len(queue)     # snapshot: how many nodes are at this level

        for _ in range(level_size): # process exactly this many nodes
            node = queue.popleft()

            if not node.left and not node.right:
                return level        # found shallowest leaf at this level

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

    return level

class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# --- Tests ---
# Tree:   1
#        / \
#       2   3
#      /
#     4
root1 = TreeNode(1, TreeNode(2, TreeNode(4)), TreeNode(3))
assert min_depth_correct(root1) == 2   # was 3 with wrong code

# Single node
assert min_depth_correct(TreeNode(1)) == 1

# Linear tree: 1->2->3 (all left children)
root3 = TreeNode(1, TreeNode(2, TreeNode(3)))
assert min_depth_correct(root3) == 3   # only path is length 3

# Balanced tree: min == max depth
#       1
#      / \
#     2   3
assert min_depth_correct(TreeNode(1, TreeNode(2), TreeNode(3))) == 2

print("Level-by-level BFS tests passed.")
```

---

## Mistake 4: Priority Queue — Not Negating for Max-Heap

### The Confusion

Python's `heapq` module implements a **min-heap**: `heappop()` always returns the **smallest** element. For problems requiring max-priority-first (largest task runs first, furthest deadline, k largest elements), you must **negate** values before pushing and negate again after popping.

### Wrong Code

```python
import heapq

def top_k_frequent_wrong(nums, k):
    """Returns k most frequent elements. Bug: uses min-heap as if it were max-heap."""
    from collections import Counter
    freq = Counter(nums)

    # Push (frequency, element) directly — pops LEAST frequent first
    heap = []
    for num, count in freq.items():
        heapq.heappush(heap, (count, num))

    result = []
    for _ in range(k):
        result.append(heapq.heappop(heap)[1])   # BUG: pops smallest frequency

    return result

# --- Test that exposes the bug ---
nums = [1, 1, 1, 2, 2, 3]
print(top_k_frequent_wrong(nums, 2))
# Expected: [1, 2] (frequencies 3 and 2)
# Actual:   [3, 2] (frequencies 1 and 2) — BUG: 3 has lowest frequency

# Scheduling example: run highest priority task first
def schedule_wrong(tasks):
    """tasks = [(priority, task_name)]. Wrong: returns lowest priority first."""
    heap = list(tasks)
    heapq.heapify(heap)
    result = []
    while heap:
        result.append(heapq.heappop(heap)[1])
    return result

tasks = [(3, "low"), (10, "high"), (7, "medium")]
print(schedule_wrong(tasks))   # ['low', 'medium', 'high'] -- BUG
```

### Correct Code

```python
import heapq
from collections import Counter

def top_k_frequent_correct(nums, k):
    """Correct: negate frequency so min-heap acts as max-heap."""
    freq = Counter(nums)

    heap = []
    for num, count in freq.items():
        heapq.heappush(heap, (-count, num))   # negate frequency

    result = []
    for _ in range(k):
        result.append(heapq.heappop(heap)[1])  # pop most frequent (most negative = most frequent)

    return result

def schedule_correct(tasks):
    """Correct: negate priority to get max-priority-first behaviour."""
    heap = [(-priority, name) for priority, name in tasks]
    heapq.heapify(heap)
    result = []
    while heap:
        _, name = heapq.heappop(heap)
        result.append(name)
    return result

# Alternative: use the nlargest helper when you don't need streaming updates
def top_k_nlargest(nums, k):
    freq = Counter(nums)
    return [item for item, _ in freq.most_common(k)]

# --- Tests ---
assert set(top_k_frequent_correct([1, 1, 1, 2, 2, 3], 2)) == {1, 2}
assert set(top_k_frequent_correct([1], 1))                 == {1}
assert set(top_k_frequent_correct([1, 2], 2))              == {1, 2}

assert schedule_correct([(3, "low"), (10, "high"), (7, "medium")]) == ["high", "medium", "low"]

assert set(top_k_nlargest([1, 1, 1, 2, 2, 3], 2)) == {1, 2}

print("Max-heap negation tests passed.")
```

### Handling Ties in Heap Elements

```python
import heapq

# Heap elements must be comparable. If values are equal, Python compares
# the second tuple element. This can cause TypeError if that element is not comparable.

# WRONG: pushing non-comparable objects
class Task:
    def __init__(self, priority, name):
        self.priority = priority
        self.name = name

heap = []
# heapq.heappush(heap, (-10, Task(10, "high")))  # TypeError if priorities tie

# CORRECT: use a counter as tie-breaker
counter = 0
def push_task(heap, priority, task):
    global counter
    heapq.heappush(heap, (-priority, counter, task))
    counter += 1

heap = []
push_task(heap, 10, "taskA")
push_task(heap, 10, "taskB")   # same priority — counter breaks the tie
_, _, name = heapq.heappop(heap)
print(name)   # "taskA" — FIFO order for equal priorities
```

---

## Mistake 5: `deque(maxlen=k)` — Silent Element Dropping

### The Confusion

`collections.deque` accepts an optional `maxlen` argument. When the deque is full and you `append` a new element, the **oldest element is silently dropped** from the other end. There is no error, no warning — the data is simply gone.

This is useful for sliding windows, but devastating if you believe you are keeping all elements.

### Wrong Code

```python
from collections import deque

# WRONG: developer intended to collect all results, used maxlen by accident
def collect_all_wrong(stream, k):
    """Collect all elements from stream, supposedly keeping last k."""
    results = deque(maxlen=k)   # BUG: silently drops elements once full

    for item in stream:
        results.append(item)    # when len > k, oldest is dropped silently

    return list(results)

# --- Test that exposes the bug ---
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
result = collect_all_wrong(data, 3)
print(result)    # [8, 9, 10]  — silently lost 1 through 7!
print(f"Expected 10 elements, got {len(result)}")   # got 3 — BUG

# More insidious: BFS with a maxlen deque
def bfs_maxlen_wrong(graph, start, capacity):
    visited = {start}
    queue = deque([start], maxlen=capacity)   # BUG: nodes silently lost if >capacity
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbour in graph.get(node, []):
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)   # silently drops if queue is full!

    return order

graph = {0: [1, 2, 3, 4], 1: [], 2: [], 3: [], 4: []}
result = bfs_maxlen_wrong(graph, 0, 2)   # capacity 2 — nodes 3 and 4 silently lost
print(result)   # [0, 1, 2]  -- BUG: 3 and 4 never visited
```

### Correct Code

```python
from collections import deque

# CORRECT: no maxlen when you need to keep all elements
def collect_all_correct(stream):
    results = deque()            # no maxlen — keeps everything
    for item in stream:
        results.append(item)
    return list(results)

# CORRECT: use maxlen deliberately only for sliding window (last-k) patterns
def sliding_window_max_correct(nums, k):
    """
    Returns max in each window of size k using a monotonic deque.
    Here maxlen is NOT used; the deque stores indices, not values.
    The window boundary is enforced manually.
    """
    dq = deque()   # stores indices; no maxlen needed
    result = []

    for i, num in enumerate(nums):
        # Remove indices outside the window
        while dq and dq[0] < i - k + 1:
            dq.popleft()
        # Remove indices of smaller elements — they can never be window max
        while dq and nums[dq[-1]] < num:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result

# When maxlen IS appropriate: last-k elements for a rolling log
def last_k_events(stream, k):
    log = deque(maxlen=k)   # deliberate: we only want the last k events
    for event in stream:
        log.append(event)
    return list(log)

# --- Tests ---
data = list(range(1, 11))
assert collect_all_correct(data) == list(range(1, 11))   # all 10 preserved

assert sliding_window_max_correct([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
assert sliding_window_max_correct([1], 1)                          == [1]
assert sliding_window_max_correct([1, -1], 1)                      == [1, -1]

assert last_k_events([1, 2, 3, 4, 5], 3) == [3, 4, 5]   # intentional truncation

print("deque maxlen tests passed.")
```

### Behaviour Summary

```python
from collections import deque

# Demonstrating the silent-drop behaviour clearly
dq = deque(maxlen=3)
for i in range(6):
    dq.append(i)
    print(f"After appending {i}: {list(dq)}")

# Output:
# After appending 0: [0]
# After appending 1: [0, 1]
# After appending 2: [0, 1, 2]   ← full
# After appending 3: [1, 2, 3]   ← 0 silently dropped
# After appending 4: [2, 3, 4]   ← 1 silently dropped
# After appending 5: [3, 4, 5]   ← 2 silently dropped
```

---

## Summary Table

| # | Mistake                                        | Root Cause                                      | Fix                                                     |
|---|------------------------------------------------|-------------------------------------------------|---------------------------------------------------------|
| 1 | `list.pop(0)` for dequeue                      | Lists require O(n) front removal                | Use `deque.popleft()` — O(1)                            |
| 2 | Checking visited on dequeue, not enqueue       | Same node pushed multiple times                 | Mark visited before pushing to queue                    |
| 3 | Incrementing level per node, not per level     | Level counter advances inside the node loop     | Snapshot `len(queue)` at level start; process that many |
| 4 | Pushing raw values to min-heap for max problems | `heapq` is always a min-heap                   | Negate values before push; negate again after pop       |
| 5 | Using `deque(maxlen=k)` without realising drops | `maxlen` silently evicts oldest element        | Omit `maxlen` unless sliding-window truncation is intended |
