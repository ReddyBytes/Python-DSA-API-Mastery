# Queues — Visual Explanation

---

## Chapter 1: The Coffee Shop Line

It is Monday morning. You walk into a coffee shop and join the line. The person who
arrived first gets served first. No cutting. No VIPs (for now). Everyone waits their
turn.

This is a **queue**: FIFO, **First In, First Out.**

```
NEW ARRIVALS                                    SERVED
     ↓                                             ↑
     E → [ E | D | C | B | A ] → served first
     ↑                              ↑
  enqueue                        dequeue
  (add to back)               (remove from front)
```

The two operations:
- **enqueue**: join the back of the line
- **dequeue**: leave from the front (get your coffee)

```python
from collections import deque

queue = deque()
queue.append("Alice")    # enqueue
queue.append("Bob")      # enqueue
queue.append("Charlie")  # enqueue
queue.popleft()          # dequeue → returns "Alice" (first in, first out)
queue.popleft()          # dequeue → returns "Bob"
```

Why `collections.deque` instead of a plain list? Because `list.pop(0)` is O(n) —
Python has to shift every remaining element left. `deque.popleft()` is O(1). Always
use deque for queues.

---

## Chapter 2: BFS — The Spreading Infection

Picture a 5x5 grid. One cell gets infected (marked X). Each second, the infection
spreads to every adjacent cell (up, down, left, right). How does it expand?

```
Second 0:         Second 1:         Second 2:         Second 3:
. . . . .         . . . . .         . . . . .         . 2 . . .
. . . . .         . . 1 . .         . 2 1 2 .         2 1 2 . .
. . X . .   →    . 1 X 1 .   →    2 1 X 1 2   →    . 2 1 2 .
. . . . .         . . 1 . .         . 2 1 2 .         . . 2 . .
. . . . .         . . . . .         . . . . .         . . . . .

(numbers show which second each cell got infected)
```

This wave-like expansion is **Breadth-First Search**. A queue is what makes this
possible: process all cells at distance 1 before any cells at distance 2, and so on.

**The BFS algorithm on a grid:**

```
Start: X is at position (2,2)

Queue: [(2,2)]
Visited: {(2,2)}

--- Level 1 (distance 1) ---
Dequeue (2,2). Enqueue its unvisited neighbors:
  (1,2), (3,2), (2,1), (2,3)

Queue: [(1,2), (3,2), (2,1), (2,3)]
Visited: {(2,2), (1,2), (3,2), (2,1), (2,3)}

--- Level 2 (distance 2) ---
Dequeue (1,2). Enqueue its unvisited neighbors: (0,2), (1,1), (1,3)
Dequeue (3,2). Enqueue: (4,2), (3,1), (3,3)
Dequeue (2,1). Enqueue: (2,0), (1,1)... wait, (1,1) already visited? Skip.
Dequeue (2,3). Enqueue: (2,4), (1,3)... (1,3) already added? Skip.
```

**Why does BFS find the shortest path?**

Because it processes cells in order of their distance from the start. When you first
reach a cell, you have found the shortest path to it — any longer path would arrive
later and gets ignored (cell is already marked visited).

```
BFS "waves" guarantee:
  All distance-1 cells are processed before ANY distance-2 cell.
  All distance-2 cells are processed before ANY distance-3 cell.
  ...
  First time you reach a cell = shortest path.
```

```python
from collections import deque

def bfs_grid(grid, start):
    rows, cols = len(grid), len(grid[0])
    dist = {start: 0}
    queue = deque([start])
    while queue:
        r, c = queue.popleft()
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr,nc) not in dist:
                dist[(nr,nc)] = dist[(r,c)] + 1
                queue.append((nr,nc))
    return dist
```

---

## Chapter 3: BFS on a Graph — Filling the Distance Table

Let's trace BFS on a small graph and watch the distance table fill in.

**Graph:** `A-B, A-C, B-D, C-D, D-E`

```
    A
   / \
  B   C
   \ /
    D
    |
    E
```

**Starting from A. Goal: find distances from A to all nodes.**

```
Initial state:
  Queue:   [A]
  Visited: {A}
  Distances: {A:0, B:?, C:?, D:?, E:?}

--- Step 1: Dequeue A ---
  A's neighbors: B, C (both unvisited)
  Enqueue B and C. Mark distances.

  Queue:   [B, C]
  Visited: {A, B, C}
  Distances: {A:0, B:1, C:1, D:?, E:?}

--- Step 2: Dequeue B ---
  B's neighbors: A (visited), D (unvisited)
  Enqueue D.

  Queue:   [C, D]
  Visited: {A, B, C, D}
  Distances: {A:0, B:1, C:1, D:2, E:?}

--- Step 3: Dequeue C ---
  C's neighbors: A (visited), D (visited — already found shortest path!)
  Nothing to enqueue.

  Queue:   [D]
  Visited: {A, B, C, D}
  Distances: {A:0, B:1, C:1, D:2, E:?}

  (D was reached via B with distance 2. C would also give distance 2.
   Since D is already visited, we skip it — first arrival is shortest.)

--- Step 4: Dequeue D ---
  D's neighbors: B (visited), C (visited), E (unvisited)
  Enqueue E.

  Queue:   [E]
  Visited: {A, B, C, D, E}
  Distances: {A:0, B:1, C:1, D:2, E:3}

--- Step 5: Dequeue E ---
  E's neighbors: D (visited)
  Nothing to enqueue.

  Queue:   []
  DONE.

Final distances from A:
  A → A: 0
  A → B: 1
  A → C: 1
  A → D: 2
  A → E: 3
```

```python
from collections import deque

def bfs_graph(graph, start):
    dist = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in dist:
                dist[neighbor] = dist[node] + 1
                queue.append(neighbor)
    return dist
```

---

## Chapter 4: Priority Queue — The VIP Hospital Waiting Room

Back to the waiting room analogy, but now we are in a hospital emergency department.
A sprained ankle waits. A heart attack skips the line. Priority, not arrival time,
determines who is seen next.

This is a **priority queue**. The item with the highest priority is always dequeued
first, regardless of when it arrived.

### Python's heapq is a MIN-heap

This is crucial: Python gives you the SMALLEST element first.

```python
import heapq

heap = []
heapq.heappush(heap, 5)
heapq.heappush(heap, 2)
heapq.heappush(heap, 8)
heapq.heappush(heap, 1)

heapq.heappop(heap)   # returns 1 (smallest!)
heapq.heappop(heap)   # returns 2
heapq.heappop(heap)   # returns 5
heapq.heappop(heap)   # returns 8
```

```
Min-heap visualization (parent always ≤ children):

         1
        / \
       2   8
      /
     5

heappop removes 1 (root), restructures:

         2
        / \
       5   8
```

### The Negation Trick for Max-heap

Want to always get the LARGEST element first? Negate everything when pushing, negate
again when popping.

```python
import heapq

heap = []
heapq.heappush(heap, -5)   # push 5 as -5
heapq.heappush(heap, -2)   # push 2 as -2
heapq.heappush(heap, -8)   # push 8 as -8
heapq.heappush(heap, -1)   # push 1 as -1

-heapq.heappop(heap)   # pops -8, negate → returns 8 (largest!)
-heapq.heappop(heap)   # returns 5
-heapq.heappop(heap)   # returns 2
-heapq.heappop(heap)   # returns 1
```

```
Min-heap stores negated values:
         -8          (this is actually 8, the largest!)
        /  \
      -2   -5
      /
     -1
```

**Push/pop complexity:** O(log n) — the heap restructures itself.

---

## Chapter 5: Deque — The Hallway With Two Doors

A regular queue is a hallway with one entrance (back) and one exit (front). A
**deque** (double-ended queue) is a hallway where you can enter and exit from BOTH
ends.

```
Regular queue:
  add here →  [ E | D | C | B | A ] → remove here

Deque:
  add/remove  [ E | D | C | B | A ]  add/remove
  here →                              ← here
```

```python
from collections import deque

d = deque()
d.append(1)        # add to right: [1]
d.append(2)        # add to right: [1, 2]
d.appendleft(0)    # add to left:  [0, 1, 2]
d.pop()            # remove from right: [0, 1], returns 2
d.popleft()        # remove from left:  [1], returns 0
```

**Why not just use a list?**

```
Operation        list         deque
append right     O(1)         O(1)
pop right        O(1)         O(1)
append left      O(n) ✗       O(1) ✓
pop left         O(n) ✗       O(1) ✓
```

`list.insert(0, x)` and `list.pop(0)` require shifting every element by one position.
With a million elements, that is a million operations just to touch the front.
Deque uses a doubly linked structure internally so both ends are always O(1).

---

## Chapter 6: Monotonic Deque — The Sliding Window Maximum

You are driving down a street photographing houses. You have a camera that captures
exactly **k=3 houses** in its frame. As you move one house at a time, what is the
tallest house visible at each position?

```
Houses: [3, 1, 2, 4, 1, 3]   k=3

Window positions:
  [3, 1, 2] → max = 3
  [1, 2, 4] → max = 4
  [2, 4, 1] → max = 4
  [4, 1, 3] → max = 4

Expected output: [3, 4, 4, 4]
```

Brute force: for each window, scan all k elements → O(n*k).
Smart approach: **monotonic deque** → O(n).

**The idea:** maintain a deque of indices where the values are in DECREASING order.
The front of the deque always holds the index of the window's maximum element.

When a new element arrives:
1. Remove from the BACK of the deque any indices with smaller values (they can never
   be a future maximum while this new larger element exists).
2. Remove from the FRONT of the deque any index that has slid out of the window.
3. The FRONT of the deque is always the current window's maximum.

**Trace through `[3, 1, 2, 4, 1, 3]` with k=3:**

```
i=0, val=3:
  Deque is empty. Add index 0.
  Deque (indices): [0]   Deque (values): [3]
  Window not full yet (need 3 elements).

i=1, val=1:
  Back of deque = index 0, value 3. Is 1 > 3? No. Keep it.
  Add index 1.
  Deque (indices): [0, 1]   Deque (values): [3, 1]
  Window not full yet.

i=2, val=2:
  Back of deque = index 1, value 1. Is 2 > 1? YES. Pop index 1.
  Deque (indices): [0]   Deque (values): [3]
  Back of deque = index 0, value 3. Is 2 > 3? No. Keep it.
  Add index 2.
  Deque (indices): [0, 2]   Deque (values): [3, 2]
  Window [3,1,2] is full. Front of deque = index 0, value 3.
  OUTPUT: 3 ✓

i=3, val=4:
  Back of deque = index 2, value 2. Is 4 > 2? YES. Pop index 2.
  Deque (indices): [0]   Deque (values): [3]
  Back of deque = index 0, value 3. Is 4 > 3? YES. Pop index 0.
  Deque is empty. Add index 3.
  Deque (indices): [3]   Deque (values): [4]

  Check front: is index 3 still in window [1..3]? Yes.
  OUTPUT: 4 ✓

i=4, val=1:
  Back of deque = index 3, value 4. Is 1 > 4? No. Keep it.
  Add index 4.
  Deque (indices): [3, 4]   Deque (values): [4, 1]

  Check front: is index 3 still in window [2..4]? Yes (3 >= 2).
  OUTPUT: 4 ✓

i=5, val=3:
  Back of deque = index 4, value 1. Is 3 > 1? YES. Pop index 4.
  Deque (indices): [3]   Deque (values): [4]
  Back of deque = index 3, value 4. Is 3 > 4? No. Keep it.
  Add index 5.
  Deque (indices): [3, 5]   Deque (values): [4, 3]

  Check front: is index 3 still in window [3..5]? Yes (3 >= 3).
  OUTPUT: 4 ✓

Final output: [3, 4, 4, 4] ✓
```

**Why is this O(n)?** Each index is added to the deque once and removed once.
Total operations: 2n = O(n).

**The visual intuition:** you keep a "leaderboard" of candidates for the maximum. When
a new element arrives that is taller than some current candidates, those shorter
candidates can never win (the new one is taller AND it will be in the window longer).
So you evict them from the back immediately.

```python
from collections import deque

def sliding_window_max(nums, k):
    dq = deque()        # stores indices
    result = []
    for i, val in enumerate(nums):
        # remove indices outside the window from the front
        while dq and dq[0] < i - k + 1:
            dq.popleft()
        # remove indices with smaller values from the back
        while dq and nums[dq[-1]] < val:
            dq.pop()
        dq.append(i)
        # window is full starting at index k-1
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
```

---

## Quick Reference

```
Queue:    FIFO (First In, First Out)
          enqueue=append, dequeue=popleft
          Use collections.deque, NOT plain list

Priority Queue (heapq):
          Python's heapq is a MIN-heap
          heappush, heappop → O(log n)
          Max-heap trick: negate values on push, negate again on pop

Deque:
          O(1) at both ends
          append / appendleft / pop / popleft

+---------------------------+------------------------------------+
| Pattern                   | Data Structure                     |
+---------------------------+------------------------------------+
| Level-order traversal     | Queue (regular BFS)                |
| Shortest path (unweighted)| Queue (BFS)                        |
| Shortest path (weighted)  | Priority queue (Dijkstra)          |
| Top K elements            | Priority queue (heap)              |
| Sliding window max/min    | Monotonic deque                    |
+---------------------------+------------------------------------+

BFS guarantee:
  Nodes are visited in non-decreasing order of distance from source.
  First time you reach a node = shortest path to it.
```

---

*Next up: Trees — where hierarchies come alive.*

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
