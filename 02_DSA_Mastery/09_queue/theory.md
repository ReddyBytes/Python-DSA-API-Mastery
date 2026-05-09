<a id="top"></a>
# 📘 09 – Queue in Python

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. What Is a Queue?](#1-what-is-a-queue)
  - [Visual: The Coffee Shop Line](#visual-coffee-shop)
- [2. Core Operations and Implementation](#2-operations)
  - [Proper Queue in Python](#proper-python)
- [3. Queue vs Stack](#3-queue-vs-stack)
- [4. Circular Queue](#4-circular-queue)
- [5. Double-Ended Queue (Deque)](#5-deque)
  - [Visual: The Hallway With Two Doors](#visual-hallway)
  - [Visual: Monotonic Deque — Sliding Window Maximum](#visual-monotonic-deque)
- [6. Priority Queue](#6-priority-queue)
  - [Visual: The VIP Hospital](#visual-hospital)
  - [Python heapq — Min-Heap](#heapq-min)
  - [Negation Trick for Max-Heap](#negation-trick)
  - [Handling Ties](#handling-ties)
- [7. Queue in Graph Algorithms](#7-graph-algorithms)
  - [Visual: BFS — The Spreading Infection](#visual-bfs-grid)
  - [Visual: BFS on a Graph](#visual-bfs-graph)
- [🔥 Summary](#summary)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
FIFO principle · deque (double-ended queue) · BFS usage

**Should Learn** — Important for real projects, comes up regularly:
circular queue · priority queue introduction · Python collections.deque

**Good to Know** — Useful in specific situations, not always tested:
queue in real systems · monotonic deque

**Reference** — Know it exists, look up syntax when needed:
blocking queue · bounded queue · double-ended priority queue

Tara works at an airport gate. Passengers line up to board — first in line boards first. That is a **queue**: First In, First Out (FIFO). If the stack is about reversal (last plate first), the queue is about fairness (first person first). Tara manages three types of lines every day: regular boarding (simple queue), priority passengers who skip ahead (priority queue), and gates where passengers can enter or exit from both ends (deque). Today she will learn how each one works and where they power real systems.

<a id="1-what-is-a-queue"></a>
# 1. What Is a Queue?

Tara sees queues everywhere in daily life. The supermarket checkout line — first person in line pays first. The traffic signal — cars pass in order. The printer queue — documents print in the order they were submitted. Every one follows the same rule: **First In, First Out (FIFO)**.

A queue has two ends:
- **Rear (back)** — where new elements enter (enqueue)
- **Front** — where elements leave (dequeue)

```
Enqueue (add) →  [ E | D | C | B | A ] → Dequeue (remove)
  rear                                      front

A entered first, A leaves first.
E entered last, E leaves last.
```

<a id="visual-coffee-shop"></a>
## Visual: The Coffee Shop Line

```
Coffee shop queue:

  NEW CUSTOMER                    SERVED NEXT
      ↓                               ↓
  [Eve] → [Dan] → [Carol] → [Bob] → [Alice]
   rear                               front

Alice ordered first → Alice gets her coffee first.
Eve just arrived → Eve waits for everyone ahead.

enqueue("Frank"):
  [Frank] → [Eve] → [Dan] → [Carol] → [Bob] → [Alice]
   rear                                          front

dequeue():
  [Frank] → [Eve] → [Dan] → [Carol] → [Bob]
   rear                                front
  Alice leaves with her coffee ☕
```

> [↑ Back to Top](#top)

<a id="2-operations"></a>
# 2. Core Operations and Implementation

Tara memorizes the four fundamental moves she can make with her boarding line. Each one is O(1) — constant time.

| Operation | What it does | Time |
|---|---|---|
| `enqueue(x)` | Add x to the rear | O(1) |
| `dequeue()` | Remove and return from the front | O(1) |
| `peek()` / `front()` | Look at the front without removing | O(1) |
| `is_empty()` | Check if queue is empty | O(1) |

<a id="proper-python"></a>
## Proper Queue in Python

**Never use `list` as a queue.** `list.pop(0)` is O(n) — it shifts every element. Use `collections.deque` which gives O(1) at both ends.

```python
from collections import deque

queue = deque()
queue.append("Alice")     # enqueue
queue.append("Bob")
queue.append("Carol")

next_person = queue[0]    # peek → "Alice"
served = queue.popleft()  # dequeue → "Alice"
print(queue)              # deque(['Bob', 'Carol'])
```

**Common mistake — using list.pop(0) as dequeue:** This is O(n) per call. With 100,000 elements, draining the queue takes O(n²). Always use `deque.popleft()`.

```python
# WRONG — O(n) per pop, O(n²) total
queue = list(range(100_000))
while queue:
    queue.pop(0)    # shifts all elements left each time

# RIGHT — O(1) per popleft, O(n) total
from collections import deque
queue = deque(range(100_000))
while queue:
    queue.popleft()
```

> [↑ Back to Top](#top)

<a id="3-queue-vs-stack"></a>
# 3. Queue vs Stack

Tara compares her boarding line (queue) with the plate stack in the airport cafeteria (stack). Same simplicity, opposite behavior.

```
Queue (FIFO):  A enters first → A leaves first
Stack (LIFO):  A enters first → A leaves LAST

Queue: fair — first come, first served
Stack: urgent — most recent item handled first

Queue use cases: BFS, task scheduling, message brokers
Stack use cases: DFS, undo/redo, function call stack
```

| Feature | Queue | Stack |
|---|---|---|
| Order | FIFO | LIFO |
| Add | Rear (enqueue) | Top (push) |
| Remove | Front (dequeue) | Top (pop) |
| Real-world | Waiting line | Plate stack |
| Algorithm | BFS | DFS |

> [↑ Back to Top](#top)

<a id="4-circular-queue"></a>
# 4. Circular Queue

Tara's airport has a circular conveyor belt for luggage. When the belt reaches the end, it wraps around to the beginning. No wasted space — every slot is reusable. That is a circular queue.

In a regular array-based queue, dequeuing from the front leaves empty slots that are never reused. A circular queue wraps around using modulo arithmetic: `index = (index + 1) % capacity`.

```
Regular queue waste:

  [_] [_] [_] [D] [E] [F]
   ↑ wasted space (front moved past these)

Circular queue:

  [G] [_] [_] [D] [E] [F]
   ↑ rear wraps around to reuse slot 0
```

Used in: audio buffers, network packet queues, embedded systems.

> 📝 **Practice:** [Q17 · circular queue implementation](./practice.md#q17--implement-a-circular-queue-with-a-fixed-size-array)

> [↑ Back to Top](#top)

<a id="5-deque"></a>
# 5. Double-Ended Queue (Deque)

Tara manages a VIP lane where passengers can be added or removed from BOTH ends. A regular queue is a hallway with one entrance and one exit. A **deque** is a hallway where you can enter and exit from both doors.

<a id="visual-hallway"></a>
## Visual: The Hallway With Two Doors

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

`list.insert(0, x)` and `list.pop(0)` require shifting every element. Deque uses a doubly linked structure internally so both ends are always O(1).

<a id="visual-monotonic-deque"></a>
## Visual: Monotonic Deque — The Sliding Window Maximum

Tara is driving past a row of houses. Her camera captures exactly **k=3 houses** at a time. As she moves one house forward, what is the tallest house visible at each position?

```
Houses: [3, 1, 2, 4, 1, 3]   k=3

Window positions:
  [3, 1, 2] → max = 3
  [1, 2, 4] → max = 4
  [2, 4, 1] → max = 4
  [4, 1, 3] → max = 4

Expected output: [3, 4, 4, 4]
```

The idea: maintain a deque of indices where values are in DECREASING order. The front always holds the window's maximum.

```
Trace through [3, 1, 2, 4, 1, 3] with k=3:

i=0, val=3:
  Deque empty. Add 0.
  Deque (indices): [0]  values: [3]
  Window not full yet.

i=1, val=1:
  1 < 3, keep. Add 1.
  Deque: [0, 1]  values: [3, 1]
  Window not full.

i=2, val=2:
  2 > 1? YES → pop 1.
  2 > 3? No → keep.
  Add 2.
  Deque: [0, 2]  values: [3, 2]
  Window full. Front=0, value=3.
  OUTPUT: 3 ✓

i=3, val=4:
  4 > 2? YES → pop 2.
  4 > 3? YES → pop 0.
  Add 3.
  Deque: [3]  values: [4]
  OUTPUT: 4 ✓

i=4, val=1:
  1 < 4 → keep. Add 4.
  Deque: [3, 4]  values: [4, 1]
  Front=3, still in window. OUTPUT: 4 ✓

i=5, val=3:
  3 > 1? YES → pop 4.
  3 > 4? No → keep.
  Add 5.
  Deque: [3, 5]  values: [4, 3]
  Front=3, still in window. OUTPUT: 4 ✓

Final: [3, 4, 4, 4] ✓
```

Why O(n)? Each index is added and removed at most once. Total: 2n operations.

```python
from collections import deque

def sliding_window_max(nums, k):
    dq = deque()
    result = []
    for i, val in enumerate(nums):
        while dq and dq[0] < i - k + 1:
            dq.popleft()
        while dq and nums[dq[-1]] < val:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
```

> 📝 **Practice:** [Q34 · queue-deque-ops](../dsa_practice_questions_100.md#q34--normal--queue-deque-ops)

> [↑ Back to Top](#top)

<a id="6-priority-queue"></a>
# 6. Priority Queue

Tara's airport has a VIP boarding lane. Unlike the regular queue where first-in-line boards first, the VIP lane boards by priority — business class before economy, regardless of who arrived first. That is a **priority queue**.

<a id="visual-hospital"></a>
## Visual: The VIP Hospital Waiting Room

A hospital emergency department. A sprained ankle waits. A heart attack skips the line. Priority, not arrival time, determines who is seen next. The item with the highest priority is always dequeued first.

<a id="heapq-min"></a>
## Python heapq — Min-Heap

Python's `heapq` is a MIN-heap — gives you the SMALLEST element first.

```python
import heapq

heap = []
heapq.heappush(heap, 5)
heapq.heappush(heap, 2)
heapq.heappush(heap, 8)
heapq.heappush(heap, 1)

heapq.heappop(heap)   # returns 1 (smallest!)
heapq.heappop(heap)   # returns 2
```

```
Min-heap visualization:

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

Push/pop complexity: O(log n).

**Common mistake — not negating for max-heap:** Python's `heapq` is always min-heap. For max-priority, negate values.

<a id="negation-trick"></a>
## Negation Trick for Max-Heap

```python
import heapq

heap = []
heapq.heappush(heap, -5)   # push 5 as -5
heapq.heappush(heap, -2)
heapq.heappush(heap, -8)
heapq.heappush(heap, -1)

-heapq.heappop(heap)   # pops -8, negate → returns 8 (largest!)
-heapq.heappop(heap)   # returns 5
```

```
Min-heap stores negated values:
         -8          (this is actually 8, the largest!)
        /  \
      -2   -5
      /
     -1
```

<a id="handling-ties"></a>
## Handling Ties

```python
import heapq

counter = 0
def push_task(heap, priority, task):
    global counter
    heapq.heappush(heap, (-priority, counter, task))
    counter += 1

heap = []
push_task(heap, 10, "taskA")
push_task(heap, 10, "taskB")   # same priority — counter breaks tie
_, _, name = heapq.heappop(heap)
print(name)   # "taskA" — FIFO for equal priorities
```

> 📝 **Practice:** [Q18 · heapq basics](./practice.md#q18--basic-heapq-usage-push-five-tasks-with-priorities-pop-them-in-order) · [Q19 · max-heap negation](./practice.md#q19--max-heap-with-heapq-find-the-3-largest-elements-from-a-stream-using-a-max-heap) · [Q20 · task scheduling](./practice.md#q20--task-scheduling-tasks-arrive-with-deadlines-earlier-deadline--higher-priority-schedule-them-using-a-priority-queue)

> [↑ Back to Top](#top)

<a id="7-graph-algorithms"></a>
# 7. Queue in Graph Algorithms

Tara learns that BFS — the algorithm that explores neighbors level by level — is powered entirely by a queue. Why? Because BFS must process all nodes at distance 1 before any node at distance 2. FIFO guarantees this order.

<a id="visual-bfs-grid"></a>
## Visual: BFS — The Spreading Infection

A 5x5 grid. One cell gets infected. Each second, the infection spreads to adjacent cells (up, down, left, right).

```
Second 0:         Second 1:         Second 2:         Second 3:
. . . . .         . . . . .         . . . . .         . 2 . . .
. . . . .         . . 1 . .         . 2 1 2 .         2 1 2 . .
. . X . .   →    . 1 X 1 .   →    2 1 X 1 2   →    . 2 1 2 .
. . . . .         . . 1 . .         . 2 1 2 .         . . 2 . .
. . . . .         . . . . .         . . . . .         . . . . .
```

This wave-like expansion is BFS. A queue makes it possible: process all cells at distance 1 before any at distance 2.

**Why BFS finds shortest path:** it processes cells in order of distance. First time you reach a cell = shortest path.

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

<a id="visual-bfs-graph"></a>
## Visual: BFS on a Graph

```
Graph: A-B, A-C, B-D, C-D, D-E

    A
   / \
  B   C
   \ /
    D
    |
    E

BFS from A:

Queue: [A]          Process A → enqueue B, C
Queue: [B, C]       Process B → enqueue D (C already queued)
Queue: [C, D]       Process C → D already visited
Queue: [D]          Process D → enqueue E
Queue: [E]          Process E → done

Visit order: A → B → C → D → E
Distances:   A=0, B=1, C=1, D=2, E=3
```

> [↑ Back to Top](#top)

<a id="summary"></a>
## 🔥 Summary

| Concept | Key Takeaway |
|---------|-------------|
| Queue (FIFO) | First in, first out — fairness |
| Deque | O(1) at both ends — use `collections.deque` |
| Circular queue | Wraps around — no wasted space |
| Priority queue | Highest priority first — uses heap, O(log n) |
| BFS | Queue-powered level-by-level exploration |
| Monotonic deque | O(n) sliding window max/min |

**Real systems that depend on queues:**
- **Operating systems** — process scheduling, interrupt handling
- **Web servers** — request queues, thread pools
- **Rate limiting** — token bucket, leaky bucket
- **Message brokers** — Kafka, RabbitMQ, SQS

**Common patterns:**
```
+-------------------------------+----------------------------------+
| Pattern                       | Key Idea                         |
+-------------------------------+----------------------------------+
| BFS traversal                 | Queue ensures level-order        |
| Sliding window max            | Monotonic deque, O(n)            |
| Task scheduling               | Priority queue (heapq)           |
| Producer-consumer              | Bounded queue as buffer          |
+-------------------------------+----------------------------------+
```

**When NOT to use queue:**
- Need LIFO order → use stack
- Need priority-based order → use priority queue (heap)
- Need random access → use array

Stack controls execution. Queue controls flow. Understanding both deeply prepares you for graph algorithms, system design, and concurrency.

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [08_stack → theory.md](../08_stack/theory.md) |
| ➡ Next Module | [10_hashing → theory.md](../10_hashing/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[08 Stack →](../08_stack/theory.md) · [10 Hashing →](../10_hashing/theory.md) · [16 Heaps →](../16_heaps/theory.md) · [18 Graphs →](../18_graphs/theory.md)

**Jump to specific topics in other files:**
- BFS in graphs → [18_graphs § theory.md](../18_graphs/theory.md)
- Heap data structure → [16_heaps § theory.md](../16_heaps/theory.md)
- Stack (LIFO counterpart) → [08_stack § theory.md](../08_stack/theory.md)
- Sliding window technique → [12_sliding_window § theory.md](../12_sliding_window/theory.md)

> [↑ Back to Top](#top)
