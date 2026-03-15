# Graphs — Visual Explanation

---

## 1. GRAPH REPRESENTATIONS — THE SAME GRAPH, 3 WAYS

```
  The graph (undirected):

       1 ──── 2
       |    / |
       |   /  |
       |  /   |
       3 ──── 4 ──── 5
```

### Edge List

```python
edges = [
    (1, 2),
    (1, 3),
    (2, 3),
    (2, 4),
    (3, 4),
    (4, 5),
]
# Simple, but slow to look up neighbors: O(E)
```

### Adjacency List (Python dict) — MOST COMMON

```python
graph = {
    1: [2, 3],
    2: [1, 3, 4],
    3: [1, 2, 4],
    4: [2, 3, 5],
    5: [4],
}
# Fast neighbor lookup: O(degree of node)
# Space: O(V + E)
```

### Adjacency Matrix

```
     1  2  3  4  5
  1 [0, 1, 1, 0, 0]
  2 [1, 0, 1, 1, 0]
  3 [1, 1, 0, 1, 0]
  4 [0, 1, 1, 0, 1]
  5 [0, 0, 0, 1, 0]

# matrix[i][j] = 1 means edge exists between i and j
# Fast edge lookup: O(1)
# Space: O(V^2) — bad for sparse graphs
```

### When to use which:

```
  Edge list       → when you just need to store edges (e.g. Kruskal's)
  Adjacency list  → DEFAULT for most graph problems (BFS, DFS, Dijkstra)
  Adjacency matrix→ dense graphs, or when you need O(1) edge lookup
```

---

## 2. BFS — WAVE EXPANSION

**Analogy:** Drop a stone in a pond. Ripples expand outward in perfect rings.
BFS explores all neighbors at distance d before exploring distance d+1.

```
  Graph:
         1
        / \
       2   3
      / \   \
     4   5   6

  Start at node 1.

  ┌──────────────────────────────────────────────────┐
  │ Step 0:  Queue = [1]          Visited = {1}      │
  │                                                  │
  │           [1]                                    │
  │                                                  │
  │ Step 1:  Pop 1, enqueue 2, 3  Visited = {1,2,3}  │
  │          Queue = [2, 3]                          │
  │                                                  │
  │           1                                      │
  │          ↙ ↘                                     │
  │         2   3                                    │
  │                                                  │
  │ Step 2:  Pop 2, enqueue 4, 5  Visited = {1..5}   │
  │          Queue = [3, 4, 5]                       │
  │                                                  │
  │ Step 3:  Pop 3, enqueue 6     Visited = {1..6}   │
  │          Queue = [4, 5, 6]                       │
  │                                                  │
  │ Step 4:  Pop 4 (no unvisited neighbors)          │
  │ Step 5:  Pop 5 (no unvisited neighbors)          │
  │ Step 6:  Pop 6 (no unvisited neighbors)          │
  └──────────────────────────────────────────────────┘

  Level 0:  [1]
  Level 1:  [2, 3]
  Level 2:  [4, 5, 6]

  BFS visit order: 1 → 2 → 3 → 4 → 5 → 6
```

**BFS guarantees shortest path in unweighted graphs.**

```python
from collections import deque

def bfs(graph, start):
    visited = {start}
    queue   = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

---

## 3. DFS — DIVE DEEP, THEN BACKTRACK

**Analogy:** Exploring a cave system. You always go as deep as possible down one tunnel before backing up and trying the next tunnel.

```
  Graph:          1
                 / \
                2   3
               / \   \
              4   5   6

  DFS from 1 (visiting left neighbors first):

  ┌──────────────────────────────────────────────────────┐
  │  CALL STACK         │  ACTION                        │
  │  ─────────          │  ──────                        │
  │  [dfs(1)]           │  visit 1, go to neighbor 2     │
  │  [dfs(1), dfs(2)]   │  visit 2, go to neighbor 4     │
  │  [dfs(1),dfs(2),    │  visit 4, no unvisited         │
  │   dfs(4)]           │  neighbors → BACKTRACK         │
  │  [dfs(1), dfs(2)]   │  back at 2, go to neighbor 5   │
  │  [dfs(1),dfs(2),    │  visit 5, no unvisited         │
  │   dfs(5)]           │  neighbors → BACKTRACK         │
  │  [dfs(1), dfs(2)]   │  2 exhausted → BACKTRACK       │
  │  [dfs(1)]           │  back at 1, go to neighbor 3   │
  │  [dfs(1), dfs(3)]   │  visit 3, go to neighbor 6     │
  │  [dfs(1),dfs(3),    │  visit 6, no unvisited         │
  │   dfs(6)]           │  neighbors → BACKTRACK         │
  │  []                 │  done                          │
  └──────────────────────────────────────────────────────┘

  DFS visit order: 1 → 2 → 4 → 5 → 3 → 6
```

---

## 4. BFS vs DFS — SIDE BY SIDE

```
  Same graph:
           1
          /|\
         2 3 4
        /|     \
       5  6     7

  ┌─────────────────────────┬─────────────────────────┐
  │         BFS             │          DFS             │
  ├─────────────────────────┼─────────────────────────┤
  │ Uses: QUEUE (FIFO)      │ Uses: STACK / recursion  │
  │                         │                          │
  │ Visit: 1                │ Visit: 1                 │
  │ Queue: [2, 3, 4]        │ Stack: [2, 3, 4]         │
  │                         │                          │
  │ Visit: 2                │ Visit: 4 (pop top)       │
  │ Queue: [3, 4, 5, 6]     │ Stack: [2, 3, 7]         │
  │                         │                          │
  │ Visit: 3                │ Visit: 7                 │
  │ Queue: [4, 5, 6]        │ Stack: [2, 3]            │
  │                         │                          │
  │ Visit: 4                │ Visit: 3                 │
  │ Queue: [5, 6, 7]        │ Stack: [2]               │
  │                         │                          │
  │ Visit: 5, 6, 7          │ Visit: 2, then 5, 6      │
  │                         │                          │
  │ Order: 1,2,3,4,5,6,7    │ Order: 1,4,7,3,2,6,5    │
  ├─────────────────────────┼─────────────────────────┤
  │ GOOD FOR:               │ GOOD FOR:                │
  │ Shortest path           │ Cycle detection          │
  │ Level-by-level          │ Topological sort         │
  │ "Closest node" queries  │ Connected components     │
  │                         │ Solving mazes            │
  └─────────────────────────┴─────────────────────────┘
```

---

## 5. TOPOLOGICAL SORT (Kahn's Algorithm — BFS-based)

**Only works on DAGs (Directed Acyclic Graphs).**
**Analogy:** Getting dressed. You can't put on shoes before socks.

```
  DAG (dependencies):
  A → C
  B → C
  B → D
  C → E
  D → E

  Drawn:
    A ──→ C ──→ E
    B ──↗   ↗
      ──→ D ──↗

  Step 1: Compute in-degrees (how many arrows point INTO each node)
  ┌────────┬──────────┐
  │  Node  │ In-degree│
  ├────────┼──────────┤
  │   A    │    0     │  ← nothing points to A
  │   B    │    0     │  ← nothing points to B
  │   C    │    2     │  ← A and B point to C
  │   D    │    1     │  ← B points to D
  │   E    │    2     │  ← C and D point to E
  └────────┴──────────┘

  Step 2: Enqueue all nodes with in-degree = 0
  Queue = [A, B]

  Step 3: Process queue
  ┌───────────────────────────────────────────────────────┐
  │ Pop A → output A, decrement in-degree of C (now 1)   │
  │ Pop B → output B, decrement C (now 0), D (now 0)     │
  │         enqueue C, D                                  │
  │ Queue = [C, D]                                        │
  │                                                       │
  │ Pop C → output C, decrement E (now 1)                 │
  │ Pop D → output D, decrement E (now 0), enqueue E      │
  │ Queue = [E]                                           │
  │                                                       │
  │ Pop E → output E                                      │
  └───────────────────────────────────────────────────────┘

  Topological order: A → B → C → D → E
  (Multiple valid orderings exist; B → A → D → C → E is also valid)

  If queue empties before all nodes are output → CYCLE EXISTS (not a DAG)
```

---

## 6. DIJKSTRA'S ALGORITHM — STEP-BY-STEP

**Analogy:** GPS routing. Always expand the shortest known path first.

```
  Weighted graph:
       2       3
  1 ──── 2 ──── 4
  |    / |       \
  |  1   | 1      \ 1
  |/     |         \
  3 ──── 5 ──────── 6
      2         4

  Start: node 1

  Priority Queue (min-heap): entries are (distance, node)

  ┌──────────────────────────────────────────────────────────────┐
  │ Init: dist = {1:0, 2:∞, 3:∞, 4:∞, 5:∞, 6:∞}                │
  │       pq   = [(0, 1)]                                        │
  ├──────────────────────────────────────────────────────────────┤
  │ Pop (0, 1). Process node 1.                                  │
  │   neighbor 2: 0+2=2  < ∞  → update dist[2]=2, push (2,2)   │
  │   neighbor 3: 0+1=1  < ∞  → update dist[3]=1, push (1,3)   │
  │ pq = [(1,3), (2,2)]                                          │
  │ dist= {1:0, 2:2, 3:1, 4:∞, 5:∞, 6:∞}                       │
  ├──────────────────────────────────────────────────────────────┤
  │ Pop (1, 3). Process node 3.                                  │
  │   neighbor 1: 1+1=2  > 0  → skip (already shorter)          │
  │   neighbor 2: 1+1=2  = 2  → no improvement                  │
  │   neighbor 5: 1+2=3  < ∞  → update dist[5]=3, push (3,5)   │
  │ pq = [(2,2), (3,5)]                                          │
  │ dist= {1:0, 2:2, 3:1, 4:∞, 5:3, 6:∞}                       │
  ├──────────────────────────────────────────────────────────────┤
  │ Pop (2, 2). Process node 2.                                  │
  │   neighbor 4: 2+3=5  < ∞  → update dist[4]=5, push (5,4)   │
  │   neighbor 5: 2+1=3  = 3  → no improvement                  │
  │ pq = [(3,5), (5,4)]                                          │
  │ dist= {1:0, 2:2, 3:1, 4:5, 5:3, 6:∞}                       │
  ├──────────────────────────────────────────────────────────────┤
  │ Pop (3, 5). Process node 5.                                  │
  │   neighbor 6: 3+4=7  < ∞  → update dist[6]=7, push (7,6)   │
  │ pq = [(5,4), (7,6)]                                          │
  │ dist= {1:0, 2:2, 3:1, 4:5, 5:3, 6:7}                       │
  ├──────────────────────────────────────────────────────────────┤
  │ Pop (5, 4). Process node 4.                                  │
  │   neighbor 6: 5+1=6  < 7  → update dist[6]=6, push (6,6)   │
  │ pq = [(6,6), (7,6)]                                          │
  │ dist= {1:0, 2:2, 3:1, 4:5, 5:3, 6:6}   ← FINAL DISTANCES   │
  └──────────────────────────────────────────────────────────────┘

  Final shortest distances from node 1:
  1→1: 0,  1→2: 2,  1→3: 1,  1→4: 5,  1→5: 3,  1→6: 6
```

---

## 7. CYCLE DETECTION — DIRECTED GRAPH

**Using DFS with two sets: `visited` (ever seen) and `in_stack` (current DFS path)**

```
  Graph WITH cycle:       Graph WITHOUT cycle:
  A → B → C              A → B → C
      ↑   |                      |
      └───┘                      ↓
                                 D

  DFS on cyclic graph starting at A:
  ┌──────────────────────────────────────────────────────┐
  │  Call     │  visited      │  in_stack  │  Action      │
  │  ───────  │  ──────────── │  ────────  │  ──────────  │
  │  dfs(A)   │  {A}          │  {A}       │  go to B     │
  │  dfs(B)   │  {A,B}        │  {A,B}     │  go to C     │
  │  dfs(C)   │  {A,B,C}      │  {A,B,C}   │  go to B     │
  │  visit B  │  B in visited │  B in      │  CYCLE!      │
  │           │               │  in_stack! │  return True │
  └──────────────────────────────────────────────────────┘

  Key distinction:
  visited   = "I have been here before (any time)"
  in_stack  = "I am currently on the active recursion path"

  A node in visited but NOT in_stack means:
    "I visited it in a previous DFS branch — no cycle through here"

  A node in BOTH visited AND in_stack means:
    "I am currently visiting it — I found a back edge — CYCLE!"
```

---

## 8. CONNECTED COMPONENTS

**Analogy:** Islands in an ocean. Each island is a connected component.

```
  Graph:
  1 ── 2     4 ── 5     7
       |          |
       3          6

  Component 1: {1, 2, 3}    ← all reachable from 1
  Component 2: {4, 5, 6}    ← all reachable from 4
  Component 3: {7}          ← isolated node

  Algorithm: run DFS/BFS from every unvisited node

  ┌─────────────────────────────────────────────────────┐
  │ visited = {}                                        │
  │                                                     │
  │ node 1: not visited → DFS from 1                    │
  │   marks {1, 2, 3} as visited → component 1 found   │
  │                                                     │
  │ node 2: already visited → skip                      │
  │ node 3: already visited → skip                      │
  │                                                     │
  │ node 4: not visited → DFS from 4                    │
  │   marks {4, 5, 6} as visited → component 2 found   │
  │                                                     │
  │ node 5: already visited → skip                      │
  │ node 6: already visited → skip                      │
  │                                                     │
  │ node 7: not visited → DFS from 7                    │
  │   marks {7} as visited → component 3 found         │
  └─────────────────────────────────────────────────────┘

  Result: 3 connected components
```

---

## MENTAL MODEL SUMMARY

```
┌───────────────────────────────────────────────────────────────┐
│  GRAPHS — MENTAL MODELS                                       │
├──────────────────┬────────────────────────────────────────────┤
│  Algorithm       │  Think of it as...                         │
├──────────────────┼────────────────────────────────────────────┤
│  BFS             │  Ripple from a stone in water              │
│  DFS             │  Spelunking a cave — deepest tunnel first  │
│  Topological     │  Getting dressed (order of dependencies)   │
│  Dijkstra        │  GPS: always take the shortest known road  │
│  Cycle detection │  Are you walking in circles?               │
│  Components      │  Count the islands                         │
├──────────────────┼────────────────────────────────────────────┤
│  Problem         │  Use...                                     │
├──────────────────┼────────────────────────────────────────────┤
│  Shortest path   │  BFS (unweighted), Dijkstra (weighted)     │
│  (unweighted)    │                                            │
│  Task ordering   │  Topological sort (Kahn's or DFS)          │
│  Detect cycle    │  DFS + in_stack set (directed)             │
│                  │  Union-Find or DFS visited (undirected)    │
│  All paths       │  DFS with backtracking                     │
│  Islands/regions │  DFS/BFS + visited set                     │
│  Min spanning    │  Kruskal (sort edges) or Prim (greedy)     │
└──────────────────┴────────────────────────────────────────────┘
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
