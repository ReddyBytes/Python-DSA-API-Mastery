# Graphs — Pattern Recognition Guide

> **Core Idea**: A graph is nodes (vertices) connected by edges. Every graph problem is
> fundamentally about traversal. The question is: *which traversal algorithm*, and *what
> information do you track while traversing?*

---

## 1. Pattern Recognition: Graph Problem Signals

Before choosing an algorithm, identify what the problem is actually asking:

```
SIGNAL                               PATTERN
----------------------------------------------------
"shortest path", "minimum steps"   → BFS (unweighted) or Dijkstra (weighted)
"minimum cost path"                → Dijkstra
"all paths from A to B"            → DFS with backtracking
"detect cycle"                     → DFS with recursion stack (directed)
                                     or DFS with parent (undirected)
"topological order", "prerequisite"→ Topological sort (Kahn's BFS or DFS)
"connected components", "islands"  → DFS/BFS over all unvisited nodes
"all start simultaneously"         → Multi-source BFS
"group", "merge", "same component" → Union-Find
"can split into two groups"        → Bipartite check (BFS coloring)
"minimum spanning tree"            → Kruskal (Union-Find) or Prim (heap)
"weighted", "cost"                 → Dijkstra (non-negative) or Bellman-Ford (negative)
```

---

## 2. BFS Pattern — Shortest Path, Level-by-Level

### When to Use BFS

- "Minimum number of moves/steps"
- "Shortest path in unweighted graph"
- "Minimum depth", "closest", "nearest"
- "Level by level" processing
- "Reach in fewest operations"

**Key insight**: BFS explores nodes in order of their distance from the source.
The FIRST time you reach a node is guaranteed to be the shortest path.

### Recognition Signals

```
"minimum moves to reach target"  → BFS
"shortest transformation sequence" → BFS (Word Ladder)
"minimum number of steps"        → BFS
"level by level"                 → BFS with level tracking
"nearest node with property X"   → BFS
```

### BFS Template (Annotated)

```python
from collections import deque

def bfs_shortest_path(graph, start, target):
    # Step 1: Initialize visited set and queue TOGETHER
    # CRITICAL: mark as visited when PUSHING, not when popping
    # If you mark when popping, duplicates enter the queue
    visited = {start}
    queue = deque([(start, 0)])       # (node, distance)

    while queue:
        node, dist = queue.popleft()  # FIFO — processes level by level

        # Step 2: Check goal condition
        if node == target:
            return dist               # first time = shortest path

        # Step 3: Explore neighbors
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor) # mark BEFORE pushing to queue
                queue.append((neighbor, dist + 1))

    return -1                         # target unreachable
```

### BFS with Level Tracking

```python
def bfs_by_level(graph, start):
    """Processes one full level at a time — useful when level number matters."""
    visited = {start}
    queue = deque([start])
    level = 0

    while queue:
        level_size = len(queue)           # snapshot of current level size

        for _ in range(level_size):       # process ALL nodes at current level
            node = queue.popleft()
            print(f"Level {level}: {node}")

            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        level += 1                        # only increment after full level
```

### BFS vs DFS for Shortest Path — Why BFS Wins

```
Graph:  A → B → D
        A → C → D

BFS from A to D:
  Level 0: [A]
  Level 1: [B, C]    ← visits B and C at same time
  Level 2: [D]       ← finds D, distance = 2
  CORRECT: distance 2

DFS from A to D (going A→B→D first):
  Path found: A→B→D, length = 2
  HAPPENS to be correct here, but...

DFS FAILURE CASE:
  Graph: A → B → C → D
         A → D          (direct connection, length 1)

  DFS might explore A→B→C→D first, returning length 3.
  It does NOT guarantee finding the shortest path.
  BFS would find A→D in level 1. ALWAYS correct.

RULE: For shortest path in UNWEIGHTED graphs, always use BFS.
      DFS may find A path, but not THE shortest path.
```

---

## 3. DFS Pattern — All Paths, Cycles, Components

### When to Use DFS

- "Find ALL paths from A to B"
- "Is there a cycle?"
- "Count connected components"
- "Topological ordering"
- "Can we color the graph?"

**Key insight**: DFS commits to one path fully before backtracking.
It naturally explores deep and is ideal when you need to track the entire path.

### Recognition Signals

```
"all paths", "enumerate paths"   → DFS + backtracking
"detect cycle"                   → DFS with in-progress tracking
"topological order"              → DFS post-order, then reverse
"number of islands/components"   → DFS from each unvisited node
"connected"                      → DFS from one node, check all visited
```

### Template Variation 1 — Recursive DFS (All Paths)

```python
def all_paths_dfs(graph, start, target):
    """Find ALL paths from start to target."""
    results = []

    def dfs(node, path):
        if node == target:
            results.append(path[:])   # copy current path
            return

        for neighbor in graph[node]:
            if neighbor not in path:          # avoid cycles
                path.append(neighbor)
                dfs(neighbor, path)
                path.pop()                    # BACKTRACK — undo the choice

    dfs(start, [start])
    return results
```

### Template Variation 2 — Iterative DFS (Using Stack)

```python
def dfs_iterative(graph, start):
    """Iterative DFS — avoids Python recursion limit for large graphs."""
    visited = set()
    stack = [start]
    result = []

    while stack:
        node = stack.pop()            # LIFO — goes deep first
        if node in visited:
            continue
        visited.add(node)
        result.append(node)

        for neighbor in graph[node]:  # push neighbors onto stack
            if neighbor not in visited:
                stack.append(neighbor)

    return result
```

### Template Variation 3 — DFS for Cycle Detection (Directed Graph)

```python
def has_cycle_directed(graph, V):
    """Detect cycle in directed graph using DFS + recursion stack."""
    visited = set()
    rec_stack = set()      # nodes currently in the DFS call stack

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)

        for neighbor in graph[node]:
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:    # back edge = cycle
                return True

        rec_stack.remove(node)            # leaving this DFS path
        return False

    return any(dfs(i) for i in range(V) if i not in visited)

# KEY INSIGHT: rec_stack tracks nodes in CURRENT path.
# A back edge (neighbor already in rec_stack) means a cycle.
# Unlike visited, rec_stack shrinks as we backtrack.
```

---

## 4. Multi-Source BFS — All Sources Start Simultaneously

### When to Use Multi-Source BFS

The problem has MULTIPLE starting points that all begin "spreading" at the same time.
All sources are treated as distance 0.

### Recognition Signals

```
"rotten oranges infect adjacent fresh oranges each minute"
"walls expanding outward simultaneously"
"multiple fires spreading at same rate"
"distance from nearest X"    ← nearest to ANY of multiple sources
"rooms closest to a gate"
```

**Key insight**: Instead of running BFS once per source (slow), initialize the queue
with ALL sources at once. They all start at distance 0 and spread together.

### Template — Multi-Source BFS

```python
from collections import deque

def multi_source_bfs(grid):
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    visited = set()

    # Step 1: Push ALL starting nodes into queue at once (distance 0)
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == ROTTEN:       # or whatever the "source" condition is
                queue.append((r, c, 0))    # (row, col, distance)
                visited.add((r, c))

    # Step 2: Standard BFS from all sources simultaneously
    max_dist = 0
    while queue:
        r, c, dist = queue.popleft()
        max_dist = max(max_dist, dist)

        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and (nr, nc) not in visited
                    and grid[nr][nc] == FRESH):
                visited.add((nr, nc))
                queue.append((nr, nc, dist + 1))

    return max_dist
```

### Worked Example — Rotting Oranges

```python
def oranges_rotting(grid):
    """
    Grid: 0=empty, 1=fresh, 2=rotten
    Each minute, rotten oranges infect all adjacent fresh oranges.
    Return minimum minutes until no fresh orange remains, or -1 if impossible.
    """
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh_count = 0

    # Find ALL rotten oranges — they ALL start at minute 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c, 0))   # (row, col, time)
            elif grid[r][c] == 1:
                fresh_count += 1

    if fresh_count == 0:
        return 0                          # already done

    time_elapsed = 0
    directions = [(0,1),(0,-1),(1,0),(-1,0)]

    while queue:
        r, c, time = queue.popleft()

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                grid[nr][nc] = 2          # infect (mutate grid = mark visited)
                fresh_count -= 1
                time_elapsed = time + 1
                queue.append((nr, nc, time + 1))

    return time_elapsed if fresh_count == 0 else -1

# WHY MULTI-SOURCE WORKS HERE:
# All rotten oranges infect simultaneously. A fresh orange's rot time
# = distance to nearest rotten orange.
# Multi-source BFS naturally computes this "nearest source" distance.
```

---

## 5. Topological Sort Pattern

### When to Use

- "Given dependencies, find a valid ordering"
- "Can we finish all courses?"
- "In what order should we build modules?"
- "Is there a circular dependency?"

### Recognition Signals

```
"prerequisites", "dependencies"     → topological sort
"course schedule"                   → topological sort + cycle check
"build order", "task ordering"      → topological sort
"if topo sort impossible"           → cycle detection via topo sort
```

### Template — Kahn's Algorithm (BFS-based)

```python
from collections import deque

def topological_sort(V, adj):
    """
    Kahn's BFS Topological Sort.
    adj[u] = list of nodes that depend on u (u must come before them).

    CYCLE DETECTION BONUS: if len(order) < V, a cycle exists.
    """
    # Step 1: Compute in-degrees
    in_degree = [0] * V
    for u in range(V):
        for v in adj[u]:
            in_degree[v] += 1

    # Step 2: Start BFS from all nodes with in-degree 0
    # These have no dependencies — can be scheduled first
    queue = deque([i for i in range(V) if in_degree[i] == 0])
    order = []

    while queue:
        u = queue.popleft()
        order.append(u)

        # "Remove" u from graph: reduce in-degree of its neighbors
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:    # all dependencies satisfied
                queue.append(v)

    # CRITICAL CYCLE CHECK:
    # If a cycle exists, some nodes' in-degrees never reach 0.
    # They are never added to queue → order is shorter than V.
    if len(order) == V:
        return order    # valid topological ordering
    else:
        return []       # cycle detected — no valid ordering exists

# Time: O(V + E)  |  Space: O(V)
```

### Worked Example — Course Schedule II (LeetCode 210)

```python
def find_order(num_courses, prerequisites):
    """
    prerequisites[i] = [a, b] means "take b before a" (b → a).
    Return a valid course order, or [] if impossible (cycle).
    """
    adj = [[] for _ in range(num_courses)]
    in_degree = [0] * num_courses

    for a, b in prerequisites:
        adj[b].append(a)        # b must come before a
        in_degree[a] += 1

    queue = deque([i for i in range(num_courses) if in_degree[i] == 0])
    order = []

    while queue:
        course = queue.popleft()
        order.append(course)
        for next_course in adj[course]:
            in_degree[next_course] -= 1
            if in_degree[next_course] == 0:
                queue.append(next_course)

    return order if len(order) == num_courses else []

# CYCLE CHECK EXPLANATION:
# If A→B→C→A (cycle), none of A, B, C ever reach in_degree=0.
# They're never added to queue. order will be missing them.
# len(order) < num_courses → return []
```

---

## 6. Dijkstra — Weighted Shortest Path

### When to Use

- Graph has WEIGHTED edges
- All weights are NON-NEGATIVE (if negative, use Bellman-Ford)
- "Minimum cost path", "cheapest route", "shortest weighted distance"

### Recognition Signals

```
"weighted graph"                     → Dijkstra
"minimum cost to reach node"         → Dijkstra
"cheapest flight within k stops"     → modified Dijkstra
"path with minimum total weight"     → Dijkstra
"network delay time"                 → Dijkstra from source
```

### Template — Dijkstra with Priority Queue

```python
import heapq

def dijkstra(graph, start, end=None):
    """
    graph[u] = [(v, weight), ...]   (adjacency list with weights)

    Uses a min-heap to always process the currently closest unvisited node.
    """
    # dist[node] = shortest known distance from start to node
    dist = {node: float('inf') for node in graph}
    dist[start] = 0

    # Min-heap: (distance, node)
    # Always pops the CLOSEST unvisited node
    heap = [(0, start)]

    while heap:
        d, u = heapq.heappop(heap)

        # Skip stale entries — we may have found a shorter path since pushing this
        # This happens because we push new entries instead of updating existing ones
        if d > dist[u]:
            continue

        if u == end:               # early termination if we only need one target
            return dist[end]

        for v, weight in graph[u]:
            new_dist = dist[u] + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))
                # We push a NEW entry rather than updating the old one.
                # Old entries become "stale" — handled by the d > dist[u] check above.

    return dist   # or dist[end] if querying one target

# Time: O((V + E) log V)  |  Space: O(V)
# FAILS with negative weights — use Bellman-Ford instead.
```

### Why Dijkstra Fails with Negative Weights

```
Graph:   A --5--> B
         A --2--> C --(-10)--> B

Dijkstra processes B first (distance 5, via A→B).
Later it discovers A→C→B = 2 + (-10) = -8. But B is already "finalized."
Dijkstra cannot re-open finalized nodes.

Bellman-Ford relaxes ALL edges V-1 times, always catching late updates.
```

---

## 7. Union-Find (Disjoint Set Union) Pattern

### When to Use

- "Are nodes X and Y in the same connected component?"
- "Merge these two groups"
- "Count the number of components"
- Efficiently handle dynamic connectivity

### Recognition Signals

```
"connected components" (with dynamic merging)  → Union-Find
"same group", "same island after merging"       → Union-Find
"redundant connection" (cycle in undirected)    → Union-Find
"accounts merge" (merge groups by key)          → Union-Find
"minimum spanning tree" (Kruskal)               → Union-Find
```

### Template — Union-Find with Path Compression + Union by Rank

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))  # each node is its own parent initially
        self.rank = [0] * n           # tree height approximation
        self.components = n           # number of components

    def find(self, x):
        """Find root with path compression — flattens the tree."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x, y):
        """Merge components containing x and y. Returns True if merged."""
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False              # already in same component

        # Union by rank: attach smaller tree under larger tree
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx           # ensure rx has higher rank
        self.parent[ry] = rx          # ry's root points to rx's root
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1

        self.components -= 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)

# Time: O(alpha(n)) per operation — effectively O(1)
# alpha = inverse Ackermann function, grows extremely slowly
```

### Worked Example — Redundant Connection (LeetCode 684)

```python
def find_redundant_connection(edges):
    """
    Find the edge that creates a cycle in an undirected graph.
    Return the LAST such edge in the input list.
    """
    n = len(edges)
    uf = UnionFind(n + 1)   # nodes are 1-indexed

    for u, v in edges:
        if not uf.union(u, v):    # union returns False if already connected
            return [u, v]         # this edge creates a cycle

    return []
```

---

## 8. Graph Coloring / Bipartite Check

### When to Use

- "Can we divide nodes into exactly 2 groups such that no edge is within a group?"
- "Is there a conflict?" (model conflicts as edges, check bipartiteness)
- "Can we 2-color the graph?"

### Recognition Signals

```
"bipartite graph"                    → BFS/DFS 2-coloring
"divide into two groups"             → bipartite check
"no two adjacent nodes same color"   → bipartite check
"students in two teams, no friends on same team" → bipartite check
```

### Template — BFS Bipartite Check

```python
from collections import deque

def is_bipartite(graph):
    """
    Try to 2-color the graph using BFS.
    A graph is bipartite if and only if it contains no odd-length cycle.
    """
    n = len(graph)
    color = [-1] * n         # -1 = unvisited, 0 or 1 = group

    for start in range(n):
        if color[start] != -1:
            continue          # already colored in a previous BFS

        # BFS from this component
        queue = deque([start])
        color[start] = 0

        while queue:
            node = queue.popleft()

            for neighbor in graph[node]:
                if color[neighbor] == -1:
                    color[neighbor] = 1 - color[node]   # flip color
                    queue.append(neighbor)
                elif color[neighbor] == color[node]:     # same group = conflict
                    return False

    return True

# KEY INSIGHT:
# Bipartite = can be 2-colored = no odd-length cycles.
# BFS colors layer 0 one color, layer 1 the other, layer 2 back to first, etc.
# If a neighbor has the SAME color as the current node, we have an odd cycle.
```

---

## 9. Problem → Pattern Decision Table

| Problem Description | Pattern | Algorithm | Complexity |
|---------------------|---------|-----------|------------|
| Shortest path, unweighted | BFS | Standard BFS | O(V+E) |
| Shortest path, weighted | Dijkstra | Min-heap BFS | O((V+E) log V) |
| Shortest path, negative weights | Bellman-Ford | Relax V-1 times | O(VE) |
| All paths from A to B | DFS + backtrack | Recursive DFS | O(V + E) |
| Cycle in directed graph | DFS | DFS + rec_stack | O(V+E) |
| Cycle in undirected graph | DFS | DFS + parent | O(V+E) |
| Task ordering / dependencies | Topological Sort | Kahn's BFS | O(V+E) |
| Circular dependency check | Topological Sort | Kahn's (len check) | O(V+E) |
| Count connected components | DFS/BFS | Loop over nodes | O(V+E) |
| Dynamic component merging | Union-Find | Path compress + rank | O(n alpha(n)) |
| Multiple simultaneous sources | Multi-source BFS | Init queue with all | O(V+E) |
| Can divide into 2 groups | Bipartite Check | BFS 2-coloring | O(V+E) |
| Minimum spanning tree | Kruskal / Prim | Union-Find / Heap | O(E log E) |

---

## 10. Common Interview Signals → Pattern Mapping

```
INTERVIEW SAYS                           YOU THINK
--------------------------------------------------------------------
"minimum steps/moves/operations"    →   BFS (unweighted shortest path)
"minimum cost / cheapest"           →   Dijkstra (add weights)
"ordering, dependencies, prereqs"   →   Topological Sort (Kahn's)
"possible to finish / no deadlock"  →   Topological Sort + cycle check
"all paths / enumerate paths"       →   DFS + backtracking
"connected / reachable"             →   DFS or BFS from source
"number of islands / components"    →   DFS/BFS loop over all nodes
"spreading simultaneously"          →   Multi-source BFS
"merge groups / same group"         →   Union-Find
"two groups, no same-group edge"    →   Bipartite BFS 2-coloring
"redundant connection"              →   Union-Find (cycle via union)
```

---

## 11. BFS Marking Pitfall — Most Common Bug

```
WRONG — mark visited when POPPING:
    while queue:
        node = queue.popleft()
        visited.add(node)           # TOO LATE
        ...

PROBLEM: The same node can be pushed into the queue multiple times
before it's popped and marked. This causes O(E) extra work or infinite loops.

CORRECT — mark visited when PUSHING:
    visited = {start}
    queue = deque([start])          # mark at init time too

    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)  # mark immediately when discovered
                queue.append(neighbor)
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Real World Usage →](./real_world_usage.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
