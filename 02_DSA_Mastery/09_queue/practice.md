# Queue — Practice Problems

> 25 questions covering FIFO mechanics, deque operations, BFS, sliding window maximum,
> priority queues, task scheduling, and thread safety.
> Work through Basic first, then Intermediate, then Advanced.

---

## Quick Index

| # | Difficulty | Topic |
|---|-----------|-------|
| [Q1](#q1) | Basic | FIFO principle explained |
| [Q2](#q2) | Basic | list vs deque — why deque |
| [Q3](#q3) | Basic | Enqueue and dequeue with deque |
| [Q4](#q4) | Basic | Peek front and back |
| [Q5](#q5) | Basic | deque.appendleft and appendright |
| [Q6](#q6) | Basic | deque.rotate |
| [Q7](#q7) | Basic | Queue empty check |
| [Q8](#q8) | Basic | queue.Queue — thread-safe API |
| [Q9](#q9) | Intermediate | BFS on a graph |
| [Q10](#q10) | Intermediate | Level-order tree traversal |
| [Q11](#q11) | Intermediate | BFS shortest path |
| [Q12](#q12) | Intermediate | Rotten oranges (multi-source BFS) |
| [Q13](#q13) | Intermediate | Sliding window maximum |
| [Q14](#q14) | Intermediate | Queue vs stack — choose the right one |
| [Q15](#q15) | Intermediate | Implement stack using queue |
| [Q16](#q16) | Intermediate | Implement queue using two stacks |
| [Q17](#q17) | Intermediate | Circular queue implementation |
| [Q18](#q18) | Intermediate | Priority queue min-heap basics |
| [Q19](#q19) | Intermediate | Priority queue max-heap (negation trick) |
| [Q20](#q20) | Intermediate | Task scheduling with priority queue |
| [Q21](#q21) | Advanced | Sliding window minimum |
| [Q22](#q22) | Advanced | K closest points to origin |
| [Q23](#q23) | Advanced | Merge K sorted lists |
| [Q24](#q24) | Advanced | Design thread-safe bounded queue |
| [Q25](#q25) | Advanced | Reconstruct queue by height |

---

## Basic Questions (~Q1–Q8)

---

<a id="q1"></a>
**Q1 — What is the FIFO principle and why does it matter?**

<details>
<summary>Hint</summary>
Think of a supermarket checkout line. The first person to join leaves first.
</details>

<details>
<summary>Answer</summary>

**FIFO = First In, First Out.**

The element inserted earliest is the first to be removed.
It is the opposite of a stack (LIFO — Last In, First Out).

FIFO guarantees fairness: whoever arrived first is served first.
It is the foundation of BFS, task scheduling, request buffering, and message queues.

```python
from collections import deque

q = deque()
q.append("Alice")   # arrived first
q.append("Bob")
q.append("Carol")

print(q.popleft())  # "Alice" — first in, first out
print(q.popleft())  # "Bob"
print(q.popleft())  # "Carol"
```

**Why it matters:**
BFS relies on FIFO so that nodes closer to the source are processed before nodes farther away.
Violating FIFO (using a stack instead) turns BFS into DFS and breaks shortest-path guarantees.

Time: O(1) enqueue, O(1) dequeue with deque.
Space: O(n) for n elements.
</details>

---

<a id="q2"></a>
**Q2 — Why is `list.pop(0)` wrong for a queue? What should you use?**

<details>
<summary>Hint</summary>
A Python list is a dynamic array. Think about what happens when you remove the first element.
</details>

<details>
<summary>Answer</summary>

`list.pop(0)` is **O(n)** because Python must shift every remaining element one position left after removing the first.

For a BFS on a graph with V vertices: using `list.pop(0)` makes the total cost O(V²) instead of O(V + E).

```python
# WRONG — O(n) dequeue
queue = []
queue.append(1)
queue.append(2)
queue.pop(0)   # shifts every element — O(n)

# RIGHT — O(1) dequeue
from collections import deque
queue = deque()
queue.append(1)
queue.append(2)
queue.popleft()   # O(1) — only updates two pointers
```

`collections.deque` is a doubly-linked list internally. Both ends (`append`/`appendleft`, `pop`/`popleft`) are O(1).

**Why:** deque does not need to shift elements because it stores a linked chain of fixed-size blocks, not a contiguous array.

Time: list.pop(0) is O(n); deque.popleft() is O(1).
Space: O(n) for n elements in either case.
</details>

---

<a id="q3"></a>
**Q3 — Implement a basic queue with enqueue, dequeue, and size.**

<details>
<summary>Hint</summary>
Use collections.deque. enqueue = append, dequeue = popleft.
</details>

<details>
<summary>Answer</summary>

```python
from collections import deque

class Queue:
    def __init__(self):
        self._data = deque()

    def enqueue(self, val):
        self._data.append(val)       # add to rear

    def dequeue(self):
        if not self._data:
            raise IndexError("dequeue from empty queue")
        return self._data.popleft()  # remove from front

    def size(self):
        return len(self._data)

    def is_empty(self):
        return len(self._data) == 0


q = Queue()
q.enqueue(10)
q.enqueue(20)
q.enqueue(30)
print(q.dequeue())   # 10
print(q.size())      # 2
```

**Why:** Wrapping deque in a class gives a clean API and prevents callers from accidentally using list-style `.pop()` (which would remove from the wrong end) on the underlying deque.

Time: enqueue O(1), dequeue O(1), size O(1).
Space: O(n).
</details>

---

<a id="q4"></a>
**Q4 — How do you peek at the front and back of a deque without removing elements?**

<details>
<summary>Hint</summary>
deque supports index access. What index is front? What is back?
</details>

<details>
<summary>Answer</summary>

```python
from collections import deque

dq = deque([10, 20, 30, 40])

front = dq[0]    # peek front — O(1)
back  = dq[-1]   # peek back  — O(1)

print(front)     # 10
print(back)      # 40
print(len(dq))   # 4 — nothing was removed
```

**Why:** deque supports O(1) access to both ends via indexing. Accessing `dq[n]` for an arbitrary middle index is O(n), but the two endpoints are always O(1).

Time: O(1) for both peeks.
Space: O(1) extra.
</details>

---

<a id="q5"></a>
**Q5 — Demonstrate `appendleft` and `popleft` on a deque. When would you use `appendleft`?**

<details>
<summary>Hint</summary>
A deque is a double-ended queue. appendleft adds to the front. Use it when you need to insert at the front in O(1).
</details>

<details>
<summary>Answer</summary>

```python
from collections import deque

dq = deque([2, 3, 4])

dq.appendleft(1)    # insert at front: [1, 2, 3, 4]
dq.appendleft(0)    # insert at front: [0, 1, 2, 3, 4]

print(dq)           # deque([0, 1, 2, 3, 4])

dq.popleft()        # removes 0 from front
print(dq)           # deque([1, 2, 3, 4])
```

**When to use `appendleft`:**
- Building a result list in reverse order without calling `list.reverse()` afterwards
- Re-enqueueing a preempted process at the front of a scheduler
- Implementing a deque-based stack that pushes to the left

**Why list.insert(0, x) is wrong:** it is O(n) because every element shifts right.
`deque.appendleft` is O(1) — only pointer updates.

Time: appendleft O(1), popleft O(1).
Space: O(n).
</details>

---

<a id="q6"></a>
**Q6 — What does `deque.rotate(k)` do? Show an example with positive and negative k.**

<details>
<summary>Hint</summary>
rotate(k) moves elements from one end to the other. Positive = right rotation, negative = left rotation.
</details>

<details>
<summary>Answer</summary>

```python
from collections import deque

dq = deque([1, 2, 3, 4, 5])

dq.rotate(2)        # rotate right by 2 — last 2 elements move to front
print(dq)           # deque([4, 5, 1, 2, 3])

dq = deque([1, 2, 3, 4, 5])
dq.rotate(-2)       # rotate left by 2 — first 2 elements move to back
print(dq)           # deque([3, 4, 5, 1, 2])
```

`rotate(1)` is equivalent to `appendleft(pop())`.
`rotate(-1)` is equivalent to `append(popleft())`.

**Use cases:**
- Round-robin task scheduling (rotate to cycle through workers)
- Implementing a circular buffer
- Solving "rotate array" problems in O(n) without extra space

**Why:** rotate(k) is O(k) — it performs k individual moves, each O(1).

Time: O(k).
Space: O(1) extra.
</details>

---

<a id="q7"></a>
**Q7 — Write a safe `dequeue` function that handles an empty queue without raising an exception.**

<details>
<summary>Hint</summary>
Check `if not queue` before calling popleft. Decide what to return for empty (None, sentinel, or raise).
</details>

<details>
<summary>Answer</summary>

```python
from collections import deque
from typing import Optional

def safe_dequeue(queue: deque, default=None):
    """Return front element or default if empty."""
    if not queue:
        return default
    return queue.popleft()


q = deque([10, 20, 30])
print(safe_dequeue(q))          # 10
print(safe_dequeue(q))          # 20
print(safe_dequeue(q))          # 30
print(safe_dequeue(q))          # None — empty, no exception
print(safe_dequeue(q, -1))      # -1 — custom default
```

**Why:** In production code, silently returning a sentinel is common for non-blocking queue consumption. Raising an exception (as `deque.popleft()` does on empty) forces callers to handle it explicitly, which is also valid — choose based on your API contract.

Time: O(1).
Space: O(1) extra.
</details>

---

<a id="q8"></a>
**Q8 — When should you use `queue.Queue` instead of `collections.deque`? Show the API.**

<details>
<summary>Hint</summary>
Think about multi-threaded programs. deque is not thread-safe for concurrent put/get.
</details>

<details>
<summary>Answer</summary>

Use `queue.Queue` when **multiple threads** produce and consume from the same queue.

`collections.deque` is not thread-safe: two threads calling `append` and `popleft` simultaneously can corrupt the internal state without explicit locking.

`queue.Queue` uses a `threading.Lock` and `threading.Condition` internally, making `put()` and `get()` atomic.

```python
import queue
import threading

q = queue.Queue(maxsize=10)   # bounded: blocks put() when full

def producer():
    for i in range(5):
        q.put(i)              # blocks if queue is full
        print(f"produced {i}")

def consumer():
    for _ in range(5):
        item = q.get()        # blocks if queue is empty
        print(f"consumed {item}")
        q.task_done()         # signal that item is processed

t1 = threading.Thread(target=producer)
t2 = threading.Thread(target=consumer)
t1.start(); t2.start()
t1.join(); t2.join()
q.join()   # wait until all task_done() calls are made
```

**Key API differences:**

| | collections.deque | queue.Queue |
|--|--|--|
| Thread-safe | No | Yes |
| Enqueue | append | put() |
| Dequeue | popleft() | get() |
| Bounded | deque(maxlen=k) silently drops | Queue(maxsize=k) blocks |
| Peek | dq[0] | not supported directly |

**Why:** `queue.Queue` adds synchronisation overhead. Use `deque` for single-threaded algorithms; use `queue.Queue` for producer-consumer patterns.

Time: put/get O(1) amortised.
Space: O(n).
</details>

---

## Intermediate Questions (~Q9–Q20)

---

<a id="q9"></a>
**Q9 — Implement BFS on an adjacency list graph. Return nodes in traversal order.**

<details>
<summary>Hint</summary>
Mark nodes visited when enqueuing, not when dequeuing. Otherwise the same node can be enqueued multiple times.
</details>

<details>
<summary>Answer</summary>

```python
from collections import deque

def bfs(graph: dict, start: int) -> list:
    visited = {start}
    queue = deque([start])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)      # mark BEFORE enqueuing
                queue.append(neighbor)

    return order


graph = {0: [1, 2], 1: [3, 4], 2: [4], 3: [], 4: []}
print(bfs(graph, 0))   # [0, 1, 2, 3, 4]
```

**Why mark on enqueue:** if you mark on dequeue, the same node can be pushed by multiple parents before any of them are processed, bloating the queue and causing duplicate processing.

**Why:** BFS guarantees level-by-level traversal because the queue preserves FIFO order: all distance-1 nodes are processed before any distance-2 node.

Time: O(V + E).
Space: O(V) for queue and visited set.
</details>

---

<a id="q10"></a>
**Q10 — Level-order traversal of a binary tree. Return a list of lists, one per level.**

<details>
<summary>Hint</summary>
At the start of each level, snapshot len(queue). Process exactly that many nodes before moving to the next level.
</details>

<details>
<summary>Answer</summary>

```python
from collections import deque

class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def level_order(root: TreeNode) -> list:
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)    # snapshot — all nodes at this level
        level = []

        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            if node.left:  queue.append(node.left)
            if node.right: queue.append(node.right)

        result.append(level)

    return result


#       1
#      / \
#     2   3
#    / \
#   4   5
root = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3))
print(level_order(root))   # [[1], [2, 3], [4, 5]]
```

**Why snapshot `len(queue)`:** new children are appended during the loop. Snapshotting ensures you only process nodes belonging to the current level, not children added during this iteration.

Time: O(n) where n = number of nodes.
Space: O(w) where w = max width of the tree (worst case O(n/2) for a complete tree).
</details>

---

<a id="q11"></a>
**Q11 — BFS shortest path. Given an unweighted graph, find the minimum number of edges from source to target.**

<details>
<summary>Hint</summary>
Store distances in a dict alongside the queue, or use a separate distance array.
</details>

<details>
<summary>Answer</summary>

```python
from collections import deque

def shortest_path(graph: dict, source: int, target: int) -> int:
    if source == target:
        return 0

    dist = {source: 0}
    queue = deque([source])

    while queue:
        node = queue.popleft()
        for neighbor in graph.get(node, []):
            if neighbor not in dist:
                dist[neighbor] = dist[node] + 1
                if neighbor == target:
                    return dist[neighbor]   # found — guaranteed shortest
                queue.append(neighbor)

    return -1   # unreachable


graph = {0: [1, 2], 1: [3], 2: [3], 3: [4], 4: []}
print(shortest_path(graph, 0, 4))   # 3 (0→1→3→4 or 0→2→3→4)
print(shortest_path(graph, 0, 0))   # 0
print(shortest_path(graph, 0, 9))   # -1
```

**Why BFS guarantees shortest:** nodes are dequeued in non-decreasing order of distance. The first time you reach the target is always via the shortest path.

Time: O(V + E).
Space: O(V) for dist dict and queue.
</details>

---

<a id="q12"></a>
**Q12 — Rotten Oranges. Given a grid where 2=rotten, 1=fresh, 0=empty, find the minimum minutes until all fresh oranges rot. Return -1 if impossible.**

<details>
<summary>Hint</summary>
Multi-source BFS: start all rotten oranges in the queue simultaneously. Each BFS level = one minute.
</details>

<details>
<summary>Answer</summary>

```python
from collections import deque

def oranges_rotting(grid: list) -> int:
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh = 0

    # Seed queue with all initially rotten oranges
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c, 0))   # (row, col, minutes)
            elif grid[r][c] == 1:
                fresh += 1

    if fresh == 0:
        return 0

    minutes = 0
    directions = [(-1,0),(1,0),(0,-1),(0,1)]

    while queue:
        r, c, mins = queue.popleft()
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                grid[nr][nc] = 2          # mark rotten
                fresh -= 1
                minutes = mins + 1
                queue.append((nr, nc, mins + 1))

    return minutes if fresh == 0 else -1


grid1 = [[2,1,1],[1,1,0],[0,1,1]]
print(oranges_rotting(grid1))    # 4

grid2 = [[2,1,1],[0,1,1],[1,0,1]]
print(oranges_rotting(grid2))    # -1  (bottom-left unreachable)

grid3 = [[0,2]]
print(oranges_rotting(grid3))    # 0  (no fresh oranges)
```

**Why multi-source BFS:** all rotten oranges spread simultaneously, so they all start in the queue at minute 0. Single-source BFS would give wrong timings.

Time: O(rows * cols).
Space: O(rows * cols) for the queue.
</details>

---

<a id="q13"></a>
**Q13 — Sliding Window Maximum. Given an array and window size k, return the max of each window.**

<details>
<summary>Hint</summary>
Use a monotonic deque storing indices in decreasing value order. The front is always the window max.
</details>

<details>
<summary>Answer</summary>

```python
from collections import deque

def max_sliding_window(nums: list, k: int) -> list:
    dq = deque()   # stores indices; values are in decreasing order
    result = []

    for i, val in enumerate(nums):
        # Remove indices that have slid out of the window
        while dq and dq[0] < i - k + 1:
            dq.popleft()

        # Remove indices with smaller values from the back
        # (they can never be the max while this larger val exists in window)
        while dq and nums[dq[-1]] < val:
            dq.pop()

        dq.append(i)

        if i >= k - 1:                  # window is now full
            result.append(nums[dq[0]])  # front = index of window max

    return result


print(max_sliding_window([3,1,2,4,1,3], 3))     # [3, 4, 4, 4]
print(max_sliding_window([1,3,-1,-3,5,3,6,7], 3)) # [3,3,5,5,6,7]
print(max_sliding_window([1], 1))                 # [1]
```

**Why O(n):** each index is appended once and removed (either from front or back) at most once. Total operations = 2n = O(n), versus O(n*k) for a brute-force scan of each window.

**Why monotonic:** the back is cleared of smaller values because they are dominated — any future window containing both would prefer the larger, newer value.

Time: O(n).
Space: O(k) for the deque.
</details>

---

<a id="q14"></a>
**Q14 — Given these four problems, decide whether to use a stack or a queue and explain why.**

Problems: (a) undo/redo, (b) BFS, (c) browser back button, (d) CPU process scheduling (FIFO).

<details>
<summary>Hint</summary>
Stack = LIFO (most recent first). Queue = FIFO (oldest first). Match the access pattern.
</details>

<details>
<summary>Answer</summary>

```
(a) undo/redo          → STACK
    Reason: the most recent action is undone first. LIFO.

(b) BFS                → QUEUE
    Reason: nodes must be explored in order of discovery — FIFO guarantees
    level-by-level processing and shortest-path correctness.

(c) browser back button → STACK
    Reason: the last page you visited is the first one you go back to. LIFO.

(d) CPU process scheduling (FIFO) → QUEUE
    Reason: processes are served in arrival order — first submitted runs first.
    Round-robin scheduling uses deque.rotate() to cycle through processes.
```

**Rule of thumb:**
- "Most recent first" → Stack
- "Oldest first / fair order" → Queue
- "Highest priority first" → Priority Queue (heap)

Time: O(1) push/pop for stack; O(1) enqueue/dequeue for queue.
</details>

---

<a id="q15"></a>
**Q15 — Implement a stack using a single queue.**

<details>
<summary>Hint</summary>
On every push, rotate all existing elements to the back so the new element is at the front.
</details>

<details>
<summary>Answer</summary>

```python
from collections import deque

class StackUsingQueue:
    """
    Stack (LIFO) built on a single queue.
    Push is O(n): after appending the new element, rotate all previous
    elements behind it so the new element sits at the front (top).
    Pop is O(1): popleft always gives the most-recently-pushed element.
    """
    def __init__(self):
        self._q = deque()

    def push(self, val):
        self._q.append(val)
        # Rotate all elements except the one just pushed to the back
        for _ in range(len(self._q) - 1):
            self._q.append(self._q.popleft())

    def pop(self):
        if not self._q:
            raise IndexError("pop from empty stack")
        return self._q.popleft()

    def top(self):
        return self._q[0]

    def empty(self):
        return len(self._q) == 0


s = StackUsingQueue()
s.push(1); s.push(2); s.push(3)
print(s.pop())   # 3 — LIFO
print(s.top())   # 2
print(s.pop())   # 2
print(s.pop())   # 1
```

**Why:** after appending 3 to [1, 2], the queue is [1, 2, 3]. Rotate the first two to the back: append 1 → [2, 3, 1], append 2 → [3, 1, 2]. Now front is 3, the last pushed. This maintains LIFO via a FIFO structure.

Time: push O(n), pop O(1), top O(1).
Space: O(n).
</details>

---

<a id="q16"></a>
**Q16 — Implement a queue using two stacks.**

<details>
<summary>Hint</summary>
Use an inbox stack and an outbox stack. Pour inbox into outbox only when outbox is empty.
</details>

<details>
<summary>Answer</summary>

```python
class QueueUsingTwoStacks:
    """
    Queue (FIFO) using two stacks (lists).
    Inbox receives all enqueues.
    Outbox is filled from inbox (reversing order) only when empty.
    Amortised O(1) per operation — each element moves at most twice.
    """
    def __init__(self):
        self._inbox = []
        self._outbox = []

    def enqueue(self, val):
        self._inbox.append(val)   # always push to inbox

    def dequeue(self):
        if not self._outbox:
            # Pour entire inbox into outbox — reverses order (oldest at top)
            while self._inbox:
                self._outbox.append(self._inbox.pop())
        if not self._outbox:
            raise IndexError("dequeue from empty queue")
        return self._outbox.pop()

    def peek(self):
        if not self._outbox:
            while self._inbox:
                self._outbox.append(self._inbox.pop())
        return self._outbox[-1]

    def empty(self):
        return not self._inbox and not self._outbox


q = QueueUsingTwoStacks()
q.enqueue(1); q.enqueue(2); q.enqueue(3)
print(q.dequeue())   # 1 — FIFO
print(q.peek())      # 2
q.enqueue(4)
print(q.dequeue())   # 2
print(q.dequeue())   # 3
print(q.dequeue())   # 4
```

**Why amortised O(1):** each element is pushed to inbox once, popped from inbox once (when pouring), pushed to outbox once, and popped from outbox once. Four operations total per element = O(1) amortised.

Time: enqueue O(1), dequeue amortised O(1) worst O(n), peek amortised O(1).
Space: O(n).
</details>

---

<a id="q17"></a>
**Q17 — Implement a circular queue with a fixed-size array.**

<details>
<summary>Hint</summary>
Use head and tail pointers with modulo arithmetic. Track count separately to distinguish full from empty.
</details>

<details>
<summary>Answer</summary>

```python
class CircularQueue:
    """
    Fixed-capacity FIFO queue backed by a circular array.
    Uses modulo to wrap head and tail without shifting elements.
    Used in OS schedulers, embedded systems, ring buffers.
    """
    def __init__(self, k: int):
        self._data = [None] * k
        self._head = 0
        self._tail = 0
        self._count = 0
        self._capacity = k

    def enqueue(self, val) -> bool:
        if self.is_full():
            return False
        self._data[self._tail] = val
        self._tail = (self._tail + 1) % self._capacity
        self._count += 1
        return True

    def dequeue(self) -> bool:
        if self.is_empty():
            return False
        self._head = (self._head + 1) % self._capacity
        self._count -= 1
        return True

    def front(self):
        if self.is_empty(): return -1
        return self._data[self._head]

    def rear(self):
        if self.is_empty(): return -1
        return self._data[(self._tail - 1) % self._capacity]

    def is_empty(self) -> bool:
        return self._count == 0

    def is_full(self) -> bool:
        return self._count == self._capacity


cq = CircularQueue(3)
cq.enqueue(1); cq.enqueue(2); cq.enqueue(3)
print(cq.is_full())    # True
cq.dequeue()
cq.enqueue(4)
print(cq.front())      # 2
print(cq.rear())       # 4
```

**Why modulo:** `(index + 1) % capacity` wraps around to 0 when the end is reached, reusing freed space at the front. A linear array would waste that space after dequeues.

Time: enqueue O(1), dequeue O(1), front/rear O(1).
Space: O(k).
</details>

---

<a id="q18"></a>
**Q18 — Basic heapq usage. Push five tasks with priorities. Pop them in order.**

<details>
<summary>Hint</summary>
Python's heapq is a min-heap. heappush adds, heappop removes the smallest.
</details>

<details>
<summary>Answer</summary>

```python
import heapq

heap = []
tasks = [(5, "low priority"), (1, "critical"), (3, "medium"), (2, "high"), (4, "normal")]

for priority, name in tasks:
    heapq.heappush(heap, (priority, name))   # O(log n) per push

print("Processing order:")
while heap:
    priority, name = heapq.heappop(heap)     # O(log n) per pop
    print(f"  priority={priority}: {name}")

# Output:
# priority=1: critical
# priority=2: high
# priority=3: medium
# priority=4: normal
# priority=5: low priority
```

**Why tuples:** heapq compares tuples lexicographically. `(priority, name)` sorts by priority first, then alphabetically by name for ties.

**Key operations:**
- `heapq.heappush(heap, item)` — O(log n)
- `heapq.heappop(heap)` — O(log n), removes min
- `heap[0]` — O(1) peek, no removal
- `heapq.heapify(list)` — O(n) in-place

Time: push/pop O(log n), peek O(1).
Space: O(n).
</details>

---

<a id="q19"></a>
**Q19 — Max-heap with heapq. Find the 3 largest elements from a stream using a max-heap.**

<details>
<summary>Hint</summary>
heapq is always a min-heap. Negate values on push, negate again on pop.
</details>

<details>
<summary>Answer</summary>

```python
import heapq

def top_k_largest(nums: list, k: int) -> list:
    """
    Return k largest numbers using a max-heap (negation trick).
    """
    heap = []
    for n in nums:
        heapq.heappush(heap, -n)   # negate to simulate max-heap

    result = []
    for _ in range(k):
        result.append(-heapq.heappop(heap))   # negate back on pop

    return result


nums = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
print(top_k_largest(nums, 3))   # [9, 6, 5]

# Alternative: heapq.nlargest (simpler for static lists)
print(heapq.nlargest(3, nums))  # [9, 6, 5]
```

**Why negation:** Python only provides a min-heap. Negating turns the largest value into the most-negative (smallest), so the min-heap always pops the most-negative, which corresponds to the original maximum.

**Common mistake:** forgetting to negate on pop gives you the negative of the answer.

Time: push O(log n) per element, pop O(log k) for k pops.
Space: O(n) for full heap, O(k) if using a size-k heap.
</details>

---

<a id="q20"></a>
**Q20 — Task scheduling. Tasks arrive with deadlines (earlier deadline = higher priority). Schedule them using a priority queue.**

<details>
<summary>Hint</summary>
Push (deadline, task_name) tuples. Min-heap naturally gives earliest deadline first.
</details>

<details>
<summary>Answer</summary>

```python
import heapq
from dataclasses import dataclass, field

@dataclass(order=True)
class Task:
    deadline: int
    name: str = field(compare=False)
    duration: int = field(compare=False)

def schedule_tasks(tasks: list) -> list:
    """
    Earliest Deadline First (EDF) scheduling.
    Used in real-time OS kernels for deadline-sensitive workloads.
    """
    heap = []
    for task in tasks:
        heapq.heappush(heap, task)

    schedule = []
    current_time = 0

    while heap:
        task = heapq.heappop(heap)       # earliest deadline first
        schedule.append({
            "task": task.name,
            "start": current_time,
            "end": current_time + task.duration,
            "deadline": task.deadline,
            "met": current_time + task.duration <= task.deadline,
        })
        current_time += task.duration

    return schedule


tasks = [
    Task(deadline=10, name="render_frame", duration=3),
    Task(deadline=5,  name="heartbeat",    duration=1),
    Task(deadline=8,  name="db_write",     duration=2),
    Task(deadline=15, name="analytics",    duration=4),
]

for entry in schedule_tasks(tasks):
    status = "OK" if entry["met"] else "MISSED"
    print(f"  {entry['task']:15} start={entry['start']}  end={entry['end']}  deadline={entry['deadline']}  [{status}]")
```

**Why EDF:** scheduling by earliest deadline minimises the number of missed deadlines on a single-processor system (provably optimal for preemptive scheduling).

**Tie-breaking note:** if two tasks have the same deadline, the dataclass `order=True` will compare `name` strings. In production use a tie-breaker counter: `(deadline, counter, task)`.

Time: O(n log n) to schedule n tasks.
Space: O(n).
</details>

---

## Advanced Questions (~Q21–Q25)

---

<a id="q21"></a>
**Q21 — Sliding Window Minimum. Given an array and window size k, return the min of each window.**

<details>
<summary>Hint</summary>
Same as sliding window maximum but maintain an increasing (not decreasing) deque. The front holds the minimum.
</details>

<details>
<summary>Answer</summary>

```python
from collections import deque

def min_sliding_window(nums: list, k: int) -> list:
    """
    Monotonic deque maintaining increasing order (front = window minimum).
    Mirror of max sliding window: only the comparison direction flips.
    """
    dq = deque()   # stores indices; values in increasing order
    result = []

    for i, val in enumerate(nums):
        # Remove expired indices from front
        while dq and dq[0] < i - k + 1:
            dq.popleft()

        # Remove indices with LARGER values from back
        # (they can never be min while this smaller val is in window)
        while dq and nums[dq[-1]] > val:
            dq.pop()

        dq.append(i)

        if i >= k - 1:
            result.append(nums[dq[0]])   # front = index of window min

    return result


print(min_sliding_window([3,1,2,4,1,3], 3))     # [1, 1, 1, 1]
print(min_sliding_window([1,3,-1,-3,5,3,6,7], 3)) # [-1,-3,-3,-3,3,3]
print(min_sliding_window([1], 1))                 # [1]
```

**Why the only change is `>` instead of `<`:** for the maximum we evict smaller elements (they lose to the new larger one); for the minimum we evict larger elements (they lose to the new smaller one).

Time: O(n) — each index pushed and popped at most once.
Space: O(k) for the deque.
</details>

---

<a id="q22"></a>
**Q22 — K Closest Points to Origin. Given a list of points, return the k closest to (0,0).**

<details>
<summary>Hint</summary>
Use a max-heap of size k. Push (distance, point); when size exceeds k, pop the farthest. What remains is the k closest.
</details>

<details>
<summary>Answer</summary>

```python
import heapq

def k_closest(points: list, k: int) -> list:
    """
    Max-heap of size k: maintains the k smallest distances seen so far.
    Negating distance converts min-heap to max-heap.
    """
    heap = []   # stores (-distance_squared, point)

    for x, y in points:
        dist_sq = x*x + y*y   # no sqrt needed — monotonic transform
        heapq.heappush(heap, (-dist_sq, (x, y)))
        if len(heap) > k:
            heapq.heappop(heap)   # remove the farthest (most negative = largest dist)

    return [point for _, point in heap]


points = [[1,3],[-2,2],[5,8],[0,1]]
print(k_closest(points, 2))    # [(-2,2), (0,1)] — two closest to origin

# Alternative: sort by distance (O(n log n), simpler but less memory-efficient)
def k_closest_sort(points, k):
    return sorted(points, key=lambda p: p[0]**2 + p[1]**2)[:k]
```

**Why a max-heap of size k:** we want to track the k smallest. A max-heap lets us evict the current farthest point whenever the heap exceeds k, keeping only candidates. Final heap = k closest.

**Why skip sqrt:** comparing `x²+y²` preserves distance ordering. Taking sqrt is an extra O(1) per point but unnecessary.

Time: O(n log k) — n pushes, each O(log k).
Space: O(k) for the heap.
</details>

---

<a id="q23"></a>
**Q23 — Merge K Sorted Lists. Given k sorted linked lists, merge them into one sorted list.**

<details>
<summary>Hint</summary>
Use a min-heap. Seed it with the head of each list. Each heappop gives the globally smallest remaining element.
</details>

<details>
<summary>Answer</summary>

```python
import heapq

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
    def __lt__(self, other):
        return self.val < other.val   # needed for heap comparison

def merge_k_lists(lists: list) -> ListNode:
    """
    Min-heap seeded with one node per list.
    Each pop gives the smallest current head across all lists.
    Push the next node from that list immediately after.
    """
    heap = []
    for node in lists:
        if node:
            heapq.heappush(heap, node)   # ListNode.__lt__ handles comparison

    dummy = ListNode(0)
    cur = dummy

    while heap:
        node = heapq.heappop(heap)
        cur.next = node
        cur = cur.next
        if node.next:
            heapq.heappush(heap, node.next)

    return dummy.next


def list_to_linked(vals):
    dummy = ListNode(0)
    cur = dummy
    for v in vals:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next

def linked_to_list(node):
    result = []
    while node:
        result.append(node.val)
        node = node.next
    return result

lists = [list_to_linked([1,4,5]),
         list_to_linked([1,3,4]),
         list_to_linked([2,6])]

print(linked_to_list(merge_k_lists(lists)))   # [1,1,2,3,4,4,5,6]
```

**Why a heap of size k:** at any moment the heap holds one candidate from each list — the current minimum of each. We always know the globally smallest element is at the top.

**Why `__lt__`:** heapq compares elements directly. Without it, two ListNodes with equal val would raise TypeError during comparison. `__lt__` makes nodes comparable.

Time: O(N log k) where N = total nodes, k = number of lists.
Space: O(k) for the heap.
</details>

---

<a id="q24"></a>
**Q24 — Design a thread-safe bounded queue with `put` (blocking when full) and `get` (blocking when empty).**

<details>
<summary>Hint</summary>
Use threading.Lock and threading.Condition. Condition.wait() releases the lock and sleeps until notified.
</details>

<details>
<summary>Answer</summary>

```python
import threading
from collections import deque

class BoundedQueue:
    """
    Thread-safe FIFO queue with a maximum capacity.
    put() blocks when full; get() blocks when empty.
    Mirrors the semantics of queue.Queue(maxsize=k) from the standard library.

    Used in: producer-consumer pipelines, thread pool work queues,
             async task queues in web servers.
    """

    def __init__(self, maxsize: int):
        self._maxsize = maxsize
        self._data = deque()
        self._lock = threading.Lock()
        self._not_full  = threading.Condition(self._lock)
        self._not_empty = threading.Condition(self._lock)

    def put(self, item, timeout=None):
        """Add item. Blocks if queue is full until space is available."""
        with self._not_full:
            # wait() atomically releases the lock and sleeps
            if not self._not_full.wait_for(
                lambda: len(self._data) < self._maxsize, timeout=timeout
            ):
                raise TimeoutError("put() timed out — queue still full")
            self._data.append(item)
            self._not_empty.notify()   # wake a sleeping get() caller

    def get(self, timeout=None):
        """Remove and return front item. Blocks if empty."""
        with self._not_empty:
            if not self._not_empty.wait_for(
                lambda: len(self._data) > 0, timeout=timeout
            ):
                raise TimeoutError("get() timed out — queue still empty")
            item = self._data.popleft()
            self._not_full.notify()    # wake a sleeping put() caller
            return item

    def size(self):
        with self._lock:
            return len(self._data)


# Demo
import time

bq = BoundedQueue(maxsize=3)

def producer():
    for i in range(6):
        bq.put(i)
        print(f"  put {i}, size={bq.size()}")
        time.sleep(0.05)

def consumer():
    for _ in range(6):
        time.sleep(0.15)   # slower than producer — forces blocking
        item = bq.get()
        print(f"  got {item}")

t1 = threading.Thread(target=producer)
t2 = threading.Thread(target=consumer)
t1.start(); t2.start()
t1.join(); t2.join()
```

**Why two Conditions sharing one Lock:** `_not_full` unblocks put() callers; `_not_empty` unblocks get() callers. Sharing the lock ensures mutual exclusion: only one thread modifies `_data` at a time.

**Why `wait_for` instead of `while wait`:** `wait_for(predicate)` handles spurious wakeups automatically — it re-checks the predicate and sleeps again if the condition is not met.

Time: put/get amortised O(1) when not blocking.
Space: O(maxsize).
</details>

---

<a id="q25"></a>
**Q25 — Reconstruct Queue by Height. Given people described as `[height, k]` where k = number of taller-or-equal people in front, reconstruct the queue.**

<details>
<summary>Hint</summary>
Sort by height descending (tallest first), then by k ascending for ties. Insert each person at index k.
</details>

<details>
<summary>Answer</summary>

```python
def reconstruct_queue(people: list) -> list:
    """
    Greedy + queue insertion.
    Key insight: once taller people are placed, inserting a shorter person
    at index k does not affect the k-count of any taller person already placed
    (shorter people are invisible to them).

    Sort: tallest first; within same height, smaller k first.
    Insert: each person at their k index.
    """
    # Sort descending by height; ascending by k for ties
    people.sort(key=lambda x: (-x[0], x[1]))

    result = []
    for person in people:
        # person[1] = k = number of taller/equal people in front
        result.insert(person[1], person)   # O(n) insert — acceptable here

    return result


people = [[7,0],[4,4],[7,1],[5,0],[6,1],[5,2]]
print(reconstruct_queue(people))
# [[5,0],[7,0],[5,2],[6,1],[4,4],[7,1]]
```

**Why sort tallest first:** inserting at index k only works correctly if all people already in `result` are taller or equal. Shorter people do not affect the count for taller ones, so they can be inserted anywhere later without violating earlier placements.

**Why `result.insert(k, person)` is acceptable:** the list has at most n elements. While each insert is O(n) and total is O(n²), n is typically small (≤ 10,000 in contest settings). An O(n log n) solution using a Fenwick tree exists but is overkill here.

Time: O(n²) due to list inserts. Sorting is O(n log n).
Space: O(n) for result.
</details>

---

## Navigation

**[Back to README](../README.md)**

**Prev:** [Interview Q&A](./interview.md) &nbsp;|&nbsp; **Next:** [Hashing — Theory](../10_hashing/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheetsheet.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
