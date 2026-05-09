<a id="top"></a>
# Queue — Order, Fairness, and Flow Control

> If Stack is about reversal,
> Queue is about fairness.
>
> Queue follows:
>
> **First In, First Out (FIFO)**

Queues control flow in real systems.
They are not just academic structures.
They model waiting systems.

## 📖 Table of Contents

1. [Daily Life: Where You Already Use Queue](#1-daily-life)
2. [What Is a Queue?](#2-what-is-a-queue)
3. [Visual Representation](#3-visual-representation)
4. [Core Operations Explained Deeply](#4-core-operations)
5. [Proper Queue Implementation in Python](#5-proper-implementation)
6. [Queue vs Stack (Deep Comparison)](#6-queue-vs-stack)
7. [Real Systems That Depend on Queue](#7-real-systems)
8. [Circular Queue — Efficient Space Usage](#8-circular-queue)
9. [Double-Ended Queue (Deque)](#9-deque)
10. [Priority Queue (Concept Introduction)](#10-priority-queue)
11. [Queue in Graph Algorithms](#11-queue-in-graph-algorithms)
12. [Common Queue Patterns](#12-common-patterns)
13. [When NOT to Use Queue](#13-when-not-to-use)
14. [Final Understanding](#14-final-understanding)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
FIFO principle · deque (double-ended queue) · BFS usage

**Should Learn** — Important for real projects, comes up regularly:
circular queue · priority queue introduction · Python collections.deque

**Good to Know** — Useful in specific situations, not always tested:
queue in real systems · monotonic deque

**Reference** — Know it exists, look up syntax when needed:
blocking queue · bounded queue · double-ended priority queue

<a id="1-daily-life"></a>
# 1. Daily Life: Where You Already Use Queue

### Supermarket Line

You enter the line first.
You leave first.

If someone behind you leaves before you,
system becomes unfair.

Queue guarantees fairness.

### Traffic Signal

Cars line up.

First car at signal moves first.

Traffic control is a queue system.

### Printer Jobs

If you send print request first,
it prints before later requests.

That is queue behavior.

> [↑ Back to Top](#top)

<a id="2-what-is-a-queue"></a>
# 2. What Is a Queue?

A queue is a linear data structure that follows:

**FIFO — First In, First Out**

Operations:

- Enqueue → Add element at rear
- Dequeue → Remove element from front
- Peek → View front element
- isEmpty → Check empty

Unlike stack:
Insertion and removal happen at opposite ends.

## Visual: The Coffee Shop Line

It is Monday morning. You walk into a coffee shop and join the line. The person who
arrived first gets served first. No cutting. No VIPs (for now). Everyone waits their
turn.

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

> 📝 **Practice:** [Q1 · FIFO principle](./practice.md#q1--what-is-the-fifo-principle-and-why-does-it-matter) · [Q3 · Basic queue class](./practice.md#q3--implement-a-basic-queue-with-enqueue-dequeue-and-size)

> [↑ Back to Top](#top)

<a id="3-visual-representation"></a>
# 3. Visual Representation

```
Front → [10] [20] [30] ← Rear
```

- Enqueue happens at rear
- Dequeue happens at front

Flow direction matters.

> [↑ Back to Top](#top)

<a id="4-core-operations"></a>
# 4. Core Operations Explained Deeply

Let n = number of elements.

| Operation | What Happens | Time |
|------------|--------------|------|
| Enqueue | Insert at rear | O(1) |
| Dequeue | Remove from front | O(1) |
| Peek | Return front | O(1) |

But careful:

In Python list:
pop(0) is O(n).

Because shifting occurs.

So Python's list is not ideal queue implementation.

**Common mistake — list.pop(0) for dequeue:** Using `list.pop(0)` requires shifting every remaining element left — that is O(n) per operation. For a BFS on a graph with V vertices and E edges, this degrades to O(V*(V+E)) instead of the correct O(V+E). Always use `deque.popleft()` which is O(1).

```
Operation        list        deque
-----------      ----        -----
append right     O(1)        O(1)
pop right        O(1)        O(1)
append left      O(n)        O(1)
pop left         O(n)        O(1)
```

> [↑ Back to Top](#top)

<a id="5-proper-implementation"></a>
# 5. Proper Queue Implementation in Python

Use collections.deque:

```python
from collections import deque

queue = deque()
queue.append(10)       # enqueue
queue.popleft()        # dequeue
```

Deque is optimized for:

- O(1) insertion at both ends
- O(1) removal at both ends

This is production-level knowledge.

Why `collections.deque` instead of a plain list? Because `list.pop(0)` is O(n) —
Python has to shift every remaining element left. `deque.popleft()` is O(1). Always
use deque for queues.

**Common mistake — deque(maxlen=k) silent element dropping:** `collections.deque` accepts an optional `maxlen` argument. When the deque is full and you `append` a new element, the oldest element is silently dropped with no error or warning. Omit `maxlen` for BFS or any use case where you need to keep all elements — only use it deliberately for sliding window (last-k) patterns.

```python
from collections import deque

# Demonstrating the silent-drop behaviour
dq = deque(maxlen=3)
for i in range(6):
    dq.append(i)
    # After appending 3: [1, 2, 3]  ← 0 silently dropped
    # After appending 4: [2, 3, 4]  ← 1 silently dropped
```

> 📝 **Practice:** [Q2 · list vs deque](./practice.md#q2--why-is-listpop0-wrong-for-a-queue-what-should-you-use) · [Q5 · appendleft & popleft](./practice.md#q5--demonstrate-appendleft-and-popleft-on-a-deque-when-would-you-use-appendleft) · [Q6 · deque.rotate](./practice.md#q6--what-does-dequerotatek-do-show-an-example-with-positive-and-negative-k)

> [↑ Back to Top](#top)

<a id="6-queue-vs-stack"></a>
# 6. Queue vs Stack (Deep Comparison)

| Feature | Stack | Queue |
|----------|--------|--------|
| Order | LIFO | FIFO |
| Insert | Top | Rear |
| Remove | Top | Front |
| Used in | DFS | BFS |

Stack reverses order.
Queue preserves order.

Choosing wrong one breaks logic.

> 📝 **Practice:** [Q14 · stack or queue decision](./practice.md#q14--given-these-four-problems-decide-whether-to-use-a-stack-or-a-queue-and-explain-why) · [Q15 · stack using queue](./practice.md#q15--implement-a-stack-using-a-single-queue) · [Q16 · queue using two stacks](./practice.md#q16--implement-a-queue-using-two-stacks)

> [↑ Back to Top](#top)

<a id="7-real-systems"></a>
# 7. Real Systems That Depend on Queue

## Operating Systems

Process scheduling.

Processes wait in ready queue.
CPU picks from front.

## Web Servers

Incoming HTTP requests queued before processing.

Prevents overload.

## Rate Limiting

Requests placed in queue.
Processed gradually.

## Message Brokers

Kafka, RabbitMQ — internally use queue structures.

> [↑ Back to Top](#top)

<a id="8-circular-queue"></a>
# 8. Circular Queue — Efficient Space Usage

Problem:

If we use simple array-based queue,
front shifts cause wasted space.

Circular queue solves this by wrapping around.

Imagine array of size 5:

```
Index: 0 1 2 3 4
```

When rear reaches end,
it wraps to beginning if space available.

Used in embedded systems.

> 📝 **Practice:** [Q17 · circular queue implementation](./practice.md#q17--implement-a-circular-queue-with-a-fixed-size-array)

> [↑ Back to Top](#top)

<a id="9-deque"></a>
# 9. Double-Ended Queue (Deque)

Deque allows:

- Insert at front
- Insert at rear
- Remove from front
- Remove from rear

More flexible than simple queue.

Used in:

- Sliding window problems
- Monotonic queue
- Cache algorithms

## Visual: The Hallway With Two Doors

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

## Visual: Monotonic Deque — The Sliding Window Maximum

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

The idea: maintain a deque of indices where the values are in DECREASING order.
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

The visual intuition: you keep a "leaderboard" of candidates for the maximum. When
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

> 📝 **Practice:** [Q34 · queue-deque-ops](../dsa_practice_questions_100.md#q34--normal--queue-deque-ops)

> [↑ Back to Top](#top)

<a id="10-priority-queue"></a>
# 10. Priority Queue (Concept Introduction)

Unlike normal queue:

Order is not based on arrival.
It is based on priority.

Example:

Emergency room patients.

Higher severity treated first.

In programming:
Implemented using heap.

Time complexity:
Insert → O(log n)
Remove → O(log n)

Priority queue is not FIFO.

## Visual: The VIP Hospital Waiting Room

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
Min-heap visualization (parent always <= children):

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

**Common mistake — not negating for max-heap:** Python's `heapq` is always a min-heap — `heappop()` returns the smallest element. For problems requiring max-priority-first (k largest elements, highest-priority task first), you must negate values before pushing and negate again after popping. Forgetting this causes the opposite ordering.

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

### Handling Ties in Heap Elements

```python
import heapq

# Heap elements must be comparable. If values are equal, Python compares
# the second tuple element. This can cause TypeError if that element is not comparable.

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

> 📝 **Practice:** [Q18 · heapq basics](./practice.md#q18--basic-heapq-usage-push-five-tasks-with-priorities-pop-them-in-order) · [Q19 · max-heap negation](./practice.md#q19--max-heap-with-heapq-find-the-3-largest-elements-from-a-stream-using-a-max-heap) · [Q20 · task scheduling](./practice.md#q20--task-scheduling-tasks-arrive-with-deadlines-earlier-deadline--higher-priority-schedule-them-using-a-priority-queue)

> [↑ Back to Top](#top)

<a id="11-queue-in-graph-algorithms"></a>
# 11. Queue in Graph Algorithms

Breadth-First Search (BFS) uses queue.

Why?

Because BFS explores level by level.

Nodes discovered first are processed first.

Queue ensures level-order traversal.

## Visual: BFS — The Spreading Infection

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

## Visual: BFS on a Graph — Filling the Distance Table

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

**Common mistake — checking visited on dequeue instead of enqueue:** If you check `visited` only when processing a node (after dequeuing), the same node can be enqueued multiple times by different neighbors before it is ever processed. In a diamond graph (A→B, A→C, B→D, C→D), node D gets pushed twice. Mark nodes as visited when enqueuing, not when dequeuing.

**Common mistake — wrong level counter in multi-source BFS:** A common error is incrementing a `level` counter for every individual node dequeued, instead of completing an entire level at once. The correct approach: snapshot `len(queue)` at the start of each level and process exactly that many nodes before incrementing. Otherwise, the level counter advances inside the node loop and produces wrong depth values.

```python
from collections import deque

def bfs_level_correct(root):
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
```

> 📝 **Practice:** [Q9 · BFS traversal](./practice.md#q9--implement-bfs-on-an-adjacency-list-graph-return-nodes-in-traversal-order) · [Q10 · level-order tree](./practice.md#q10--level-order-binary-tree-traversal-return-a-list-of-lists-one-per-level) · [Q11 · shortest path](./practice.md#q11--bfs-shortest-path-given-an-unweighted-graph-find-the-minimum-number-of-edges-from-source-to-target) · [Q12 · rotten oranges](./practice.md#q12--rotten-oranges-given-a-grid-where-2rotten-1fresh-0empty-find-the-minimum-minutes-until-all-fresh-oranges-rot-return--1-if-impossible)

> [↑ Back to Top](#top)

<a id="12-common-patterns"></a>
# 12. Common Queue Patterns

Most interview problems involve:

- BFS
- Sliding window maximum
- Task scheduling
- Rate limiting
- Level order traversal in tree
- Implement stack using queue
- Implement queue using stack

Pattern recognition is important.

```
+---------------------------+------------------------------------+
| Pattern                   | Data Structure                     |
+---------------------------+------------------------------------+
| Level-order traversal     | Queue (regular BFS)                |
| Shortest path (unweighted)| Queue (BFS)                        |
| Shortest path (weighted)  | Priority queue (Dijkstra)          |
| Top K elements            | Priority queue (heap)              |
| Sliding window max/min    | Monotonic deque                    |
+---------------------------+------------------------------------+
```

> 📝 **Practice:** [Q13 · sliding window max](./practice.md#q13--sliding-window-maximum-given-an-array-and-window-size-k-return-the-max-of-each-window) · [Q21 · sliding window min](./practice.md#q21--sliding-window-minimum-given-an-array-and-window-size-k-return-the-min-of-each-window) · [Q25 · reconstruct queue by height](./practice.md#q25--reconstruct-queue-by-height-given-people-described-as-height-k-where-k--number-of-taller-or-equal-people-in-front-reconstruct-the-queue)

> [↑ Back to Top](#top)

<a id="13-when-not-to-use"></a>
# 13. When NOT to Use Queue

Avoid queue when:

- You need LIFO behavior
- You need priority-based removal
- You need random access

Queue is specialized for ordered processing.

> [↑ Back to Top](#top)

<a id="14-final-understanding"></a>
# 14. Final Understanding

Queue represents:

- Order
- Fairness
- Controlled flow

It models real-world waiting systems.

Stack controls execution.
Queue controls flow.

Understanding both deeply prepares you for:

- Graph algorithms
- System design
- Concurrency problems
- Scheduling systems

**[🏠 Back to README](../README.md)**

**Prev:** [← Stack — Interview Q&A](../08_stack/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md) · [Practice](./practice.md)

> [↑ Back to Top](#top)
