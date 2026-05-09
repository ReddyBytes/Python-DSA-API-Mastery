<a id="top"></a>
# Graphs — The World of Connections

> A tree is a special case.
> A graph is the general case.
>
> Trees have one parent.
> Graphs can connect freely.
>
> Graphs represent networks.

Graphs model:

- Social networks
- Roads and maps
- Internet
- Flight routes
- Computer networks
- Dependencies
- Game maps

Graphs are everywhere.

## 📖 Table of Contents

1. [Real Life Story — City Map](#1-real-life-story)
2. [What Is a Graph?](#2-what-is-a-graph)
3. [Types of Graphs](#3-types-of-graphs)
4. [Graph Representation](#4-graph-representation)
5. [Graph Traversal](#5-graph-traversal)
6. [BFS — Level by Level](#6-bfs-level-by-level)
7. [DFS — Go Deep First](#7-dfs-go-deep-first)
8. [When to Use BFS vs DFS](#8-when-to-use-bfs-vs-dfs)
9. [Cycle Detection](#9-cycle-detection)
10. [Connected Components](#10-connected-components)
11. [Shortest Path (Unweighted)](#11-shortest-path-unweighted)
12. [Shortest Path (Weighted)](#12-shortest-path-weighted)
13. [Topological Sort — Ordering Dependencies](#13-topological-sort)
14. [Real-World Applications](#14-real-world-applications)
15. [Mental Model](#15-mental-model)
16. [Final Understanding](#16-final-understanding)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
graph representation (adjacency list vs matrix) · BFS · DFS · time complexity

**Should Learn** — Important for real projects, comes up regularly:
topological sort · cycle detection · connected components

**Good to Know** — Useful in specific situations, not always tested:
shortest path unweighted · directed vs undirected implications

**Reference** — Know it exists, look up syntax when needed:
Dijkstra · Bellman-Ford · MST (covered in 25_advanced_graphs)

<a id="1-real-life-story"></a>
# 1. Real Life Story — City Map

Imagine a city.

Intersections = Nodes
Roads = Edges

You can travel from one intersection to another.

That structure is a graph.

> [↑ Back to Top](#top)

<a id="2-what-is-a-graph"></a>
# 2. What Is a Graph?

A graph consists of:

- Nodes (vertices)
- Edges (connections between nodes)

Example:

```
A ----- B
|       |
C ----- D
```

Nodes: A, B, C, D
Edges: A-B, B-D, D-C, C-A

> [↑ Back to Top](#top)

<a id="3-types-of-graphs"></a>
# 3. Types of Graphs

## Undirected Graph

Edges have no direction.

```
A -- B
```

Travel both ways.

Example:
Friendship.

**Common mistake — one-directional adjacency list:** Building an undirected graph but only adding `graph[u].append(v)` without `graph[v].append(u)` turns it into a directed graph — nodes become unreachable and traversals give wrong results. Always add both directions.

> 📝 **Practice:** [Q3 · directed-vs-undirected-representation](./practice.md#q3--basic--directed-vs-undirected-representation)

## Directed Graph (Digraph)

Edges have direction.

```
A → B
```

One-way.

Example:
Twitter follow.

> 📝 **Practice:** [Q3 · directed-vs-undirected-representation](./practice.md#q3--basic--directed-vs-undirected-representation)

## Weighted Graph

Edges have weight (cost).

Example:
Distance between cities.

> 📝 **Practice:** [Q4 · weighted-graph-representation](./practice.md#q4--basic--weighted-graph-representation)

## Unweighted Graph

Edges just represent connection.

> [↑ Back to Top](#top)

<a id="4-graph-representation"></a>
# 4. Graph Representation

Two main ways:

## Adjacency List

Store neighbors for each node.

Example:

```
A: B, C
B: A, D
C: A, D
D: B, C
```

Efficient for sparse graphs.

> 📝 **Practice:** [Q1 · adjacency-list-vs-matrix](./practice.md#q1--basic--adjacency-list-vs-matrix) · [Q2 · build-adjacency-list](./practice.md#q2--basic--build-adjacency-list) · [Q46 · graph-representations](../dsa_practice_questions_100.md#q46--normal--graph-representations)

## Adjacency Matrix

2D matrix:

```
    A B C D
A   0 1 1 0
B   1 0 0 1
C   1 0 0 1
D   0 1 1 0
```

Efficient for dense graphs.

Space:
O(V²)

Adjacency list:
O(V + E)

## Visual: Graph Representations — The Same Graph, 3 Ways

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

> [↑ Back to Top](#top)

<a id="5-graph-traversal"></a>
# 5. Graph Traversal

We need ways to explore graph.

Two fundamental methods:

- BFS (Breadth-First Search)
- DFS (Depth-First Search)

These are foundation.

> [↑ Back to Top](#top)

<a id="6-bfs-level-by-level"></a>
# 6. BFS — Level by Level

Imagine ripple in water.

Start from node.
Explore all neighbors first.
Then neighbors of neighbors.

Uses queue.

Example:

```
A
/ \
B   C
|
D
```

BFS order:
A, B, C, D

Time:
O(V + E)

## Visual: BFS — Wave Expansion

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

**Common mistake — marking visited on pop:** If you mark a node visited only when you pop it from the queue, other nodes can add it multiple times before it's processed. In dense graphs this causes exponential redundant work; in graphs with cycles it causes an infinite loop. Always mark visited when pushing to the queue, not when popping.

> 📝 **Practice:** [Q5 · bfs-traversal](./practice.md#q5--basic--bfs-traversal) · [Q9 · bfs-shortest-path-unweighted](./practice.md#q9--intermediate--bfs-shortest-path-unweighted)

> [↑ Back to Top](#top)

<a id="7-dfs-go-deep-first"></a>
# 7. DFS — Go Deep First

Go as deep as possible before backtracking.

Uses recursion or stack.

DFS order:
A, B, D, C

DFS explores path fully before exploring sibling.

## Visual: DFS — Dive Deep, Then Backtrack

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

> 📝 **Practice:** [Q6 · dfs-traversal-recursive](./practice.md#q6--basic--dfs-traversal-recursive) · [Q7 · dfs-traversal-iterative](./practice.md#q7--basic--dfs-traversal-iterative) · [Q20 · find-all-paths](./practice.md#q20--intermediate--find-all-paths-source-to-target)

> [↑ Back to Top](#top)

<a id="8-when-to-use-bfs-vs-dfs"></a>
# 8. When to Use BFS vs DFS

BFS:
- Shortest path (unweighted)
- Level-order exploration
- Distance problems

DFS:
- Cycle detection
- Topological sort
- Connected components
- Backtracking problems

Choose wisely.

**Common mistake — DFS for shortest path:** DFS finds a path, not the shortest path. The first path DFS discovers may be longer than optimal. BFS guarantees the shortest path in an unweighted graph because it expands nodes level by level. Always use BFS when you need minimum distance.

## Visual: BFS vs DFS — Side by Side

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

> 📝 **Practice:** [Q23 · when-bfs-vs-dfs](./practice.md#q23--advanced--when-bfs-vs-dfs) · [Q78 · dfs-vs-bfs-when](../dsa_practice_questions_100.md#q78--interview--dfs-vs-bfs-when) · [Q84 · bfs-vs-dfs-compare](../dsa_practice_questions_100.md#q84--interview--bfs-vs-dfs-compare)

> [↑ Back to Top](#top)

<a id="9-cycle-detection"></a>
# 9. Cycle Detection

In Undirected Graph:
Use DFS and track parent.

In Directed Graph:
Use visited + recursion stack.

Important interview pattern.

## Visual: Cycle Detection — Directed Graph

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

**Common mistake — visited set only for directed cycle detection:** In a directed graph, a node can be reachable via multiple paths sharing no edges. Using only a `visited` set flags a node as "in a cycle" just because it was seen before on a different path — this gives false positives. You need an `in_stack` set (or WHITE/GRAY/BLACK coloring) to detect back edges on the current path specifically.

```python
# Diamond graph: 0->1, 0->2, 1->3, 2->3 — NO cycle, but visited-only gives false positive
# Node 3 is reachable from both 1 and 2 — wrong code reports a cycle
# Correct code uses in_stack: only flags TRUE back edges
def has_cycle_directed_correct(graph, n):
    visited = set()
    in_stack = set()   # nodes on the CURRENT DFS path

    def dfs(node):
        visited.add(node)
        in_stack.add(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in in_stack:     # back edge — actual cycle
                return True

        in_stack.remove(node)   # leaving this node's DFS subtree
        return False

    for node in range(n):
        if node not in visited:
            if dfs(node):
                return True
    return False
```

> 📝 **Practice:** [Q12 · cycle-detection-undirected](./practice.md#q12--intermediate--cycle-detection-undirected) · [Q13 · cycle-detection-directed](./practice.md#q13--intermediate--cycle-detection-directed) · [Q25 · visited-set-trap](./practice.md#q25--advanced--detect-cycle-visited-set-trap) · [Q49 · graph-cycle-detection](../dsa_practice_questions_100.md#q49--thinking--graph-cycle-detection)

> [↑ Back to Top](#top)

<a id="10-connected-components"></a>
# 10. Connected Components

How many isolated groups exist?

Example:

```
A-B   C-D   E
```

Three components.

Use DFS/BFS.

Count components.

## Visual: Connected Components

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

**Common mistake — forgetting disconnected graphs:** Starting BFS or DFS from a single node only explores the component containing that node. If the graph is disconnected, other components are never visited. Always loop over all nodes and start a new traversal from each unvisited one.

> 📝 **Practice:** [Q10 · connected-components-count](./practice.md#q10--intermediate--connected-components-count) · [Q11 · number-of-islands](./practice.md#q11--intermediate--number-of-islands) · [Q48 · dfs-connected-components](../dsa_practice_questions_100.md#q48--normal--dfs-connected-components)

> [↑ Back to Top](#top)

<a id="11-shortest-path-unweighted"></a>
# 11. Shortest Path (Unweighted)

Use BFS.

Because BFS explores level by level.

First time reaching node gives shortest distance.

> 📝 **Practice:** [Q9 · bfs-shortest-path-unweighted](./practice.md#q9--intermediate--bfs-shortest-path-unweighted) · [Q47 · bfs-shortest-path](../dsa_practice_questions_100.md#q47--thinking--bfs-shortest-path)

> [↑ Back to Top](#top)

<a id="12-shortest-path-weighted"></a>
# 12. Shortest Path (Weighted)

Cannot use BFS.

Use:

- Dijkstra (non-negative weights)
- Bellman-Ford (negative weights)

Heaps come into play here.

**Common mistake — stale queue entries in Dijkstra:** When Dijkstra relaxes an edge and pushes a new (shorter) distance to the heap, the old (longer) distance entry for the same node remains in the heap. When that stale entry is eventually popped, it can incorrectly relax neighbors using an outdated distance. Always add `if d > dist[u]: continue` at the top of the loop to skip stale entries.

> 📝 **Practice:** [Q21 · dijkstras-algorithm](./practice.md#q21--advanced--dijkstras-algorithm) · [Q22 · network-delay-time](./practice.md#q22--advanced--network-delay-time)

> [↑ Back to Top](#top)

<a id="13-topological-sort"></a>
# 13. Topological Sort — Ordering Dependencies

> Think of course prerequisites: you must take Math 101 before Calculus, and Calculus before Differential Equations. Topological sort finds a valid ordering of tasks with dependencies.

**Topological sort** produces a linear ordering of vertices in a directed acyclic graph (DAG) such that for every edge u → v, u comes before v. It only works on DAGs — cycles make a valid ordering impossible.

**When to use:** Build systems, course scheduling, task pipelines, package dependency resolution.

> 📝 **Practice:** [Q14 · topological-sort-kahns](./practice.md#q14--intermediate--topological-sort-kahns-bfs) · [Q15 · topological-sort-dfs](./practice.md#q15--intermediate--topological-sort-dfs) · [Q16 · course-schedule-i](./practice.md#q16--intermediate--course-schedule-i) · [Q17 · course-schedule-ii](./practice.md#q17--intermediate--course-schedule-ii) · [Q50 · topological-sort](../dsa_practice_questions_100.md#q50--design--topological-sort)

## Visual: Topological Sort (Kahn's Algorithm — BFS-based)

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

## Kahn's Algorithm (BFS-based)

```python
from collections import deque, defaultdict

def topological_sort_kahn(n, edges):
    """
    n: number of nodes (0 to n-1)
    edges: list of (u, v) meaning u must come before v
    Returns: ordered list, or [] if cycle detected
    """
    graph = defaultdict(list)
    in_degree = [0] * n          # ← count incoming edges per node

    for u, v in edges:
        graph[u].append(v)
        in_degree[v] += 1

    # Start with all nodes that have no dependencies
    queue = deque([i for i in range(n) if in_degree[i] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)

        for neighbor in graph[node]:
            in_degree[neighbor] -= 1    # ← remove this dependency
            if in_degree[neighbor] == 0:  # ← all deps satisfied
                queue.append(neighbor)

    # If not all nodes processed → cycle exists
    return order if len(order) == n else []
```

## DFS-based Topological Sort

```python
def topological_sort_dfs(n, edges):
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)

    visited = [0] * n    # 0=unvisited, 1=in-progress, 2=done
    result = []
    has_cycle = [False]

    def dfs(node):
        if visited[node] == 1:    # ← back edge = cycle
            has_cycle[0] = True
            return
        if visited[node] == 2:    # ← already processed
            return

        visited[node] = 1         # ← mark in-progress
        for neighbor in graph[node]:
            dfs(neighbor)
        visited[node] = 2         # ← mark done
        result.append(node)       # ← append AFTER visiting all descendants

    for i in range(n):
        if visited[i] == 0:
            dfs(i)

    if has_cycle[0]: return []
    return result[::-1]           # ← reverse: DFS adds in reverse order
```

**Cycle detection — the key insight:**
```
Kahn's: if len(order) < n → some nodes never reached in_degree 0 → cycle
DFS:    if we revisit an in-progress node → back edge → cycle

Kahn's advantage:   easier cycle detection, natural BFS layer-by-layer order
DFS advantage:      can produce lexicographically smallest order with modification
```

**Classic applications:**
- Course schedule (LeetCode 207, 210)
- Alien dictionary (LeetCode 269)
- Task scheduling with dependencies

**Complexity:** O(V + E) time, O(V + E) space

> [↑ Back to Top](#top)

<a id="14-real-world-applications"></a>
# 14. Real-World Applications

- Google Maps
- Facebook friend suggestions
- Network routing
- Flight booking systems
- Web crawling
- Dependency resolution
- Recommendation systems

Graphs power the internet.

> [↑ Back to Top](#top)

<a id="15-mental-model"></a>
# 15. Mental Model

Think of graph as:

A network of roads.

Traversal = exploring roads.

Nodes can connect in complex ways.

Unlike trees:
Graphs can have cycles.
Graphs can have multiple paths.

Graph thinking is about connectivity.

## Visual: Mental Model Summary

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

> [↑ Back to Top](#top)

<a id="16-final-understanding"></a>
# 16. Final Understanding

Graph is:

- Set of nodes and edges
- Directed or undirected
- Weighted or unweighted
- Explored using BFS/DFS
- Foundation for many algorithms

Mastering graphs prepares you for:

- Dijkstra
- Topological sort
- Strongly connected components
- Minimum spanning tree
- Network flow
- Advanced system design

Graphs are one of the most important topics in DSA.

> [↑ Back to Top](#top)

## 🔁 Navigation

Previous:
[17_trie/interview.md](/02_DSA_Mastery/17_trie/interview.md)

Next:
[18_graphs/interview.md](/02_DSA_Mastery/18_graphs/interview.md)
[19_greedy/theory.md](/02_DSA_Mastery/19_greedy/theory.md)

**[🏠 Back to README](../README.md)**

**Prev:** [← Trie — Interview Q&A](../17_trie/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md) · [Practice](./practice.md)
