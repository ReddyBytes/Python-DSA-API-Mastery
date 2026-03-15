# Advanced Graph Patterns — Algorithms and When to Use Them

---

## The Story First

Graphs are everywhere. Road networks, social connections, dependency chains, data pipelines, game states — almost every hard problem in computer science can be modeled as a graph problem.

The trouble is that different graph problems require different algorithms. Using Dijkstra on a graph with negative edges will give wrong answers. Using Floyd-Warshall on a 10,000-node graph will time out. Picking the wrong algorithm is a common interview mistake.

This document is your **decision guide**: for each advanced graph problem type, you'll learn what the algorithm does, when to use it, when NOT to use it, and how to implement it cleanly.

```
Graph Algorithm Selection:

Shortest path, single source?
  ├── No negative edges → Dijkstra
  └── Negative edges exist → Bellman-Ford

Shortest path, all pairs?
  └── Small graph → Floyd-Warshall

Ordering dependencies?
  └── Topological Sort (Kahn's BFS or DFS)

Groups where everyone can reach everyone?
  └── Strongly Connected Components (Kosaraju's)

Connect all nodes with minimum cost?
  ├── Sparse graph → Kruskal's (edge-sorted + DSU)
  └── Dense graph → Prim's (vertex-greedy + heap)

Max flow / bipartite matching?
  └── Edmonds-Karp (BFS-based Ford-Fulkerson)

Shortest path in grid with heuristic?
  └── A* Search
```

---

## Pattern 1: Shortest Path — Dijkstra (Non-negative Weights)

### The Story

You're a GPS. Given a city's road network, find the fastest route from point A to every other point in the city. Roads have different travel times (edge weights), all positive.

Dijkstra's algorithm is greedy: always extend the **shortest known path** first. It maintains a min-heap of (distance, node) pairs and a distance array initialized to infinity.

### The Key Invariant

When you pop a node from the min-heap, its distance is **final and optimal**. You never need to revisit it. This is why negative edges break Dijkstra: a negative edge could create a shorter path to an already-finalized node, violating the invariant.

### ASCII: Dijkstra in Action

```
Graph:
    0
   /|\
  4  1  2
 /   |   \
1    2    3
    / \
   9   4

Nodes: 0,1,2,3
Edges: 0→1(4), 0→2(1), 1→3(1), 2→1(2), 2→3(5)

Start: node 0
Initial: dist = [0, inf, inf, inf]
Heap: [(0, 0)]

Step 1: Pop (0, 0)  → process node 0, dist[0]=0 (final)
  Neighbors: 1 (cost 4), 2 (cost 1)
  Update dist[1] = 4, dist[2] = 1
  Heap: [(1, 2), (4, 1)]

Step 2: Pop (1, 2)  → process node 2, dist[2]=1 (final)
  Neighbors: 1 (via 2, cost 1+2=3), 3 (via 2, cost 1+5=6)
  Update dist[1] = 3 (improved from 4!), dist[3] = 6
  Heap: [(3, 1), (4, 1), (6, 3)]

Step 3: Pop (3, 1)  → process node 1, dist[1]=3 (final)
  Neighbors: 3 (via 1, cost 3+1=4)
  Update dist[3] = 4 (improved from 6!)
  Heap: [(4, 1), (4, 3), (6, 3)]

Step 4: Pop (4, 1)  → node 1 already final, SKIP (stale entry)

Step 5: Pop (4, 3)  → process node 3, dist[3]=4 (final)

Final distances: [0, 3, 1, 4]
Shortest paths:
  0→0: 0
  0→1: 0→2→1 = 1+2 = 3
  0→2: 0→2 = 1
  0→3: 0→2→1→3 = 1+2+1 = 4
```

### Template Code

```python
import heapq
from collections import defaultdict

def dijkstra(n: int, graph: dict, start: int) -> list:
    """
    n: number of nodes (0 to n-1)
    graph[u] = list of (v, weight) meaning edge u→v with given weight
    start: source node
    Returns: dist[i] = shortest distance from start to i (inf if unreachable)
    """
    dist = [float('inf')] * n
    dist[start] = 0
    heap = [(0, start)]   # (distance, node)

    while heap:
        d, u = heapq.heappop(heap)

        # Skip stale entries (we already found a shorter path to u)
        if d > dist[u]:
            continue

        for v, weight in graph.get(u, []):
            new_dist = dist[u] + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))

    return dist


# Test
graph = defaultdict(list)
edges = [(0,1,4),(0,2,1),(2,1,2),(1,3,1),(2,3,5)]
for u, v, w in edges:
    graph[u].append((v, w))

print(dijkstra(4, graph, 0))   # [0, 3, 1, 4]
```

### With Path Reconstruction

```python
def dijkstra_with_path(n: int, graph: dict, start: int, end: int):
    dist = [float('inf')] * n
    prev = [-1] * n
    dist[start] = 0
    heap = [(0, start)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        if u == end:
            break   # optional early exit
        for v, weight in graph.get(u, []):
            new_dist = dist[u] + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(heap, (new_dist, v))

    # Reconstruct path
    if dist[end] == float('inf'):
        return dist[end], []
    path = []
    curr = end
    while curr != -1:
        path.append(curr)
        curr = prev[curr]
    path.reverse()
    return dist[end], path
```

### Complexity

- Time: O((V + E) log V) — each node/edge processed once, heap operations are log V
- Space: O(V + E)

### When NOT to Use Dijkstra

- Negative edge weights → gives wrong answers (use Bellman-Ford)
- Negative weight cycles → infinite loop potential
- Need all-pairs shortest path → use Floyd-Warshall
- Unweighted graph → use BFS (O(V+E), faster)

---

## Pattern 2: Shortest Path — Bellman-Ford (Negative Weights)

### The Story

You're arbitraging currency exchange. Each exchange rate is an edge weight, and negative weights represent rates where you gain money. You want the most profitable path from one currency to another. But beware: if there's a cycle of exchanges that keeps gaining money (negative weight cycle), the "optimal" profit is infinite — the algorithm must detect this.

Bellman-Ford handles negative edge weights. Its strategy: relax every edge, V-1 times. After V-1 relaxations, all shortest paths (which can have at most V-1 edges) are found. One more pass: if any edge can still be relaxed → negative cycle exists.

### Why V-1 Relaxations?

The shortest path between any two nodes in a graph with V nodes uses at most V-1 edges (otherwise it would repeat a node, and we could remove the cycle to get a shorter path).

After k relaxations, `dist[v]` = shortest path using at most k edges.
After V-1 relaxations = shortest path using any number of edges.

### ASCII: Why Dijkstra Fails, Bellman-Ford Succeeds

```
Graph with negative edge:
  0 →(5)→ 1 →(-6)→ 2
  0 →(2)→ 2

Dijkstra:
  Pop (0,0): dist[0]=0. Relax: dist[1]=5, dist[2]=2
  Pop (2,2): dist[2]=2 (finalized). Neighbors: none.
  Pop (5,1): dist[1]=5 (finalized). Relax: dist[2] via 1 = 5+(-6) = -1
  BUT dist[2] was already finalized at 2! Dijkstra WON'T update it.
  WRONG ANSWER: Dijkstra gives dist[2]=2 instead of -1.

Bellman-Ford:
  Pass 1: Relax all edges:
    0→1: dist[1] = 0+5 = 5
    1→2: dist[2] = 5+(-6) = -1  (better than current 2)
    0→2: dist[2] = min(-1, 0+2) = -1
  After pass 1: dist = [0, 5, -1]  ← CORRECT

dist[2] = -1  ← Bellman-Ford gets it right
```

### Template Code

```python
def bellman_ford(n: int, edges: list, start: int):
    """
    n: number of nodes (0 to n-1)
    edges: list of (u, v, weight) directed edges
    Returns: (dist, has_negative_cycle)
      dist[i] = shortest distance from start to i
      has_negative_cycle = True if a negative cycle is reachable from start
    """
    dist = [float('inf')] * n
    dist[start] = 0

    # V-1 relaxation passes
    for _ in range(n - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated:
            break   # early exit if no updates (already optimal)

    # One more pass to detect negative cycles
    has_negative_cycle = False
    for u, v, w in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            has_negative_cycle = True
            break

    return dist, has_negative_cycle


# Test: graph from the ASCII above
edges = [(0,1,5), (1,2,-6), (0,2,2)]
dist, neg_cycle = bellman_ford(3, edges, 0)
print(dist)        # [0, 5, -1]
print(neg_cycle)   # False

# Test with negative cycle
edges_neg_cycle = [(0,1,1), (1,2,2), (2,0,-5)]
dist2, neg_cycle2 = bellman_ford(3, edges_neg_cycle, 0)
print(neg_cycle2)  # True (0→1→2→0 has total weight 1+2-5 = -2 per cycle)
```

### Complexity

- Time: O(V × E)
- Space: O(V)
- Much slower than Dijkstra for large graphs with non-negative weights

### When to Use Bellman-Ford

- Graph has negative edge weights
- Need to detect negative cycles
- Graph is sparse (E is small)
- For dense graphs with negative weights, still use Bellman-Ford (no alternative)

---

## Pattern 3: All-Pairs Shortest Path — Floyd-Warshall

### The Story

You're building a "six degrees of separation" tool. For any two users in a social network, find the shortest connection chain. You need shortest paths between ALL pairs, not just from one source.

Floyd-Warshall answers this with an elegant 3-nested-loop DP: "Can going through intermediate node k improve the path from i to j?"

### The Core Idea

After considering all k ∈ {0, 1, ..., n-1} as potential intermediate nodes:
`dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])`

The order matters: we process each intermediate k completely before moving to k+1. This ensures that when we compute "path from i to j through k", the sub-paths from i to k and k to j are already optimal (using intermediates 0 through k-1).

```
dist[i][j] via intermediate k:
  i ──────────────────────────── j   (current best)
  i ────── k ────────────────── j   (new candidate via k)
         ↑ k is being considered as a stepping stone
```

### Template Code

```python
def floyd_warshall(n: int, edges: list):
    """
    n: number of nodes (0 to n-1)
    edges: list of (u, v, weight) directed edges
    Returns: dist[i][j] = shortest distance from i to j
             (inf if unreachable, negative if negative cycle detected on diagonal)
    """
    INF = float('inf')
    dist = [[INF] * n for _ in range(n)]

    # Base cases
    for i in range(n):
        dist[i][i] = 0   # distance from i to itself is 0

    for u, v, w in edges:
        dist[u][v] = min(dist[u][v], w)   # handle multiple edges between same pair

    # Main DP: for each intermediate node k
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] != INF and dist[k][j] != INF:
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

    # Check for negative cycles: if dist[i][i] < 0, node i is on a negative cycle
    has_neg_cycle = any(dist[i][i] < 0 for i in range(n))

    return dist, has_neg_cycle


# Test
edges = [(0,1,3),(0,3,7),(1,0,8),(1,2,2),(2,0,5),(2,3,1),(3,0,2)]
dist, neg = floyd_warshall(4, edges)
for row in dist:
    print([x if x != float('inf') else 'inf' for x in row])
# Expected (shortest paths between all pairs):
# [0, 3, 5, 6]
# [5, 0, 2, 3]
# [3, 6, 0, 1]
# [2, 5, 7, 0]
```

### Application: Transitive Closure

"Given a directed graph, can node i reach node j?"

```python
def transitive_closure(n: int, edges: list) -> list:
    """Return reachable[i][j] = True if i can reach j."""
    reachable = [[False] * n for _ in range(n)]
    for i in range(n):
        reachable[i][i] = True
    for u, v, _ in edges:
        reachable[u][v] = True

    for k in range(n):
        for i in range(n):
            for j in range(n):
                reachable[i][j] = reachable[i][j] or (reachable[i][k] and reachable[k][j])

    return reachable
```

### Complexity and Limitations

- Time: O(V³) — three nested loops
- Space: O(V²)
- Practical limit: V ≤ 500 (500³ = 125 million operations)
- For large graphs (V > 1000), run Dijkstra from each node instead: O(V × (V+E) log V)

### When to Use Floyd-Warshall

- Need all-pairs shortest paths
- Graph is small (V ≤ ~500)
- May have negative edges (but no negative cycles for meaningful results)
- Need transitive closure

---

## Pattern 4: Topological Sort (Kahn's Algorithm)

### The Story

You're a build system. File A depends on file B and C. File B depends on file D. In what order should files be compiled so dependencies are always built before files that need them?

This is topological sort: given a DAG (Directed Acyclic Graph), find an ordering where every edge u → v means u comes before v in the ordering.

Two approaches:
1. **Kahn's Algorithm (BFS):** Start with all nodes that have no incoming edges (no dependencies). Process them, reduce in-degrees of their neighbors, add newly zero-in-degree nodes to queue.
2. **DFS post-order:** Do DFS, add nodes to result AFTER all their descendants are processed.

### ASCII: Kahn's Step by Step

```
Graph (course prerequisites):
  0 → 2 → 5
  1 → 2
  1 → 3 → 5
  0 → 4

In-degrees:
  0: 0   1: 0   2: 2   3: 1   4: 1   5: 2

Step 1: Queue = [0, 1] (in-degree 0 nodes)
  Process 0: reduce in-degree of 2 (→1), 4 (→0). Add 4 to queue.
  Process 1: reduce in-degree of 2 (→0), 3 (→0). Add 2, 3 to queue.
  Queue = [4, 2, 3], Result = [0, 1]

Step 2: Queue = [4, 2, 3]
  Process 4: no outgoing edges.
  Process 2: reduce in-degree of 5 (→1).
  Process 3: reduce in-degree of 5 (→0). Add 5 to queue.
  Queue = [5], Result = [0, 1, 4, 2, 3]

Step 3: Queue = [5]
  Process 5: no outgoing edges.
  Queue = [], Result = [0, 1, 4, 2, 3, 5]

Final order: [0, 1, 4, 2, 3, 5]
Each course appears after all its prerequisites. ✓
```

### Kahn's Algorithm (BFS-based)

```python
from collections import deque

def topological_sort_kahn(n: int, edges: list) -> list:
    """
    n: number of nodes (0 to n-1)
    edges: list of (u, v) directed edges (u must come before v)
    Returns: topological order, or [] if cycle detected (not a DAG)
    """
    in_degree = [0] * n
    adj = [[] for _ in range(n)]

    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1

    # Start with all zero-in-degree nodes
    queue = deque(i for i in range(n) if in_degree[i] == 0)
    result = []

    while queue:
        u = queue.popleft()
        result.append(u)

        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    if len(result) != n:
        return []   # cycle detected (some nodes never reached in-degree 0)

    return result


# Test: course schedule
print(topological_sort_kahn(6, [(0,2),(1,2),(0,4),(1,3),(2,5),(3,5)]))
# Possible output: [0, 1, 2, 3, 4, 5] (or other valid orderings)

# Test: cycle detection
print(topological_sort_kahn(3, [(0,1),(1,2),(2,0)]))
# Output: [] (cycle: 0→1→2→0)
```

### DFS Post-Order Topological Sort

```python
def topological_sort_dfs(n: int, edges: list) -> list:
    """DFS-based topological sort."""
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)

    visited = [0] * n   # 0=unvisited, 1=in-progress, 2=done
    result = []
    has_cycle = [False]

    def dfs(u):
        if visited[u] == 1:
            has_cycle[0] = True
            return
        if visited[u] == 2:
            return
        visited[u] = 1
        for v in adj[u]:
            dfs(v)
        visited[u] = 2
        result.append(u)   # append AFTER all descendants

    for i in range(n):
        if visited[i] == 0:
            dfs(i)

    if has_cycle[0]:
        return []

    result.reverse()   # post-order gives reverse topological order
    return result
```

### Application: Course Schedule II

```python
def findOrder(numCourses: int, prerequisites: list) -> list:
    """
    Return a course order where each course's prerequisites come first.
    Return [] if impossible (cycle).
    prerequisites[i] = [a, b] means 'must take b before a' (b → a edge)
    """
    edges = [(b, a) for a, b in prerequisites]   # b must come before a
    return topological_sort_kahn(numCourses, edges)


print(findOrder(4, [[1,0],[2,0],[3,1],[3,2]]))   # [0,1,2,3] or [0,2,1,3]
print(findOrder(2, [[1,0],[0,1]]))                # [] (cycle)
```

### Complexity

- Time: O(V + E)
- Space: O(V + E)

---

## Pattern 5: Strongly Connected Components (Kosaraju's Algorithm)

### The Story

In a web graph, a Strongly Connected Component (SCC) is a group of pages where you can get from any page to any other page by following links. Pages within an SCC are deeply interconnected; pages in different SCCs can only be reached in one direction.

Kosaraju's algorithm finds all SCCs in two DFS passes:
1. **First DFS** on original graph: record finish times (a stack of nodes in finish order)
2. **Second DFS** on reversed graph: process nodes in reverse finish order; each DFS tree = one SCC

### The Intuition

When you do DFS on the original graph and finish a node last (highest finish time), that node's SCC is the "most upstream" — you can reach all other SCCs from it, but not necessarily return.

If you reverse all edges, this SCC becomes "most downstream" — nothing can reach it in the reversed graph. So when you start the second DFS from this node in the reversed graph, the DFS only explores within the SCC (can't escape to other SCCs in the reversed graph).

### ASCII: Kosaraju's on 6 Nodes

```
Original Graph:
  0 → 1 → 4 → 3 → 5
  ↑   ↓       ↑
  3 ← 2       4

Actually let's use a clear example:
  0 → 1 → 2 → 0  (cycle: {0,1,2} form an SCC)
  2 → 3
  3 → 4 → 5 → 3  (cycle: {3,4,5} form an SCC)

Step 1: DFS on original graph, note finish order
  Start DFS from 0:
    Visit 0 → 1 → 2 → 0 (already visited, back edge)
    Finish 2 (push to stack)
    Finish 1
    Finish 0
    Then: 2 → 3 → 4 → 5 → 3 (already visited)
    Finish 5, Finish 4, Finish 3
  Stack (finish order): [2, 1, 0, 5, 4, 3] (3 on top)

Step 2: Reverse all edges
  Original:  0→1, 1→2, 2→0, 2→3, 3→4, 4→5, 5→3
  Reversed:  1→0, 2→1, 0→2, 3→2, 4→3, 5→4, 3→5

Step 3: DFS on reversed graph, pop from stack
  Pop 3: DFS from 3 in reversed graph
    3 → 5 → 4 → 3 (already visited)
    SCC #1: {3, 5, 4}
  Pop 4: already visited, skip
  Pop 5: already visited, skip
  Pop 0: DFS from 0 in reversed graph
    0 → 2 → 1 → 0 (already visited)
    SCC #2: {0, 2, 1}
  Result: 2 SCCs = [{3,4,5}, {0,1,2}]
```

### Template Code

```python
def kosaraju_scc(n: int, edges: list) -> list:
    """
    Find all SCCs using Kosaraju's algorithm.
    Returns: list of SCCs, each SCC is a list of node indices.
    """
    # Build adjacency lists
    adj = [[] for _ in range(n)]
    radj = [[] for _ in range(n)]   # reversed graph
    for u, v in edges:
        adj[u].append(v)
        radj[v].append(u)

    visited = [False] * n
    finish_stack = []   # nodes in finish order

    # Step 1: DFS on original graph, fill finish_stack
    def dfs1(u):
        visited[u] = True
        for v in adj[u]:
            if not visited[v]:
                dfs1(v)
        finish_stack.append(u)

    for i in range(n):
        if not visited[i]:
            dfs1(i)

    # Step 2: DFS on reversed graph, process in reverse finish order
    visited = [False] * n
    sccs = []

    def dfs2(u, scc):
        visited[u] = True
        scc.append(u)
        for v in radj[u]:
            if not visited[v]:
                dfs2(v, scc)

    while finish_stack:
        u = finish_stack.pop()
        if not visited[u]:
            scc = []
            dfs2(u, scc)
            sccs.append(scc)

    return sccs


# Test
edges = [(0,1),(1,2),(2,0),(2,3),(3,4),(4,5),(5,3)]
sccs = kosaraju_scc(6, edges)
print(sccs)   # [[0,1,2], [3,4,5]] or in some order
```

### Iterative Version (Avoids Recursion Depth Issues)

```python
def kosaraju_iterative(n: int, edges: list) -> list:
    adj = [[] for _ in range(n)]
    radj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        radj[v].append(u)

    # Step 1: Iterative DFS for finish order
    visited = [False] * n
    finish_stack = []

    for start in range(n):
        if visited[start]:
            continue
        stack = [(start, 0)]   # (node, neighbor_index)
        visited[start] = True
        while stack:
            u, idx = stack[-1]
            if idx < len(adj[u]):
                stack[-1] = (u, idx + 1)
                v = adj[u][idx]
                if not visited[v]:
                    visited[v] = True
                    stack.append((v, 0))
            else:
                stack.pop()
                finish_stack.append(u)

    # Step 2: Iterative DFS on reversed graph
    visited = [False] * n
    sccs = []

    while finish_stack:
        start = finish_stack.pop()
        if visited[start]:
            continue
        scc = []
        stack = [start]
        visited[start] = True
        while stack:
            u = stack.pop()
            scc.append(u)
            for v in radj[u]:
                if not visited[v]:
                    visited[v] = True
                    stack.append(v)
        sccs.append(scc)

    return sccs
```

### Applications

- **Condensation graph:** Contract each SCC into a single "super-node." The resulting DAG is the high-level structure of the original graph. Useful for dependency analysis.
- **2-SAT Problem:** Each variable and its negation are nodes; each clause creates two directed edges. Variables in the same SCC as their negation → unsatisfiable.
- **Strongly connected roads:** Can every city be reached from every other city? → One SCC.

### Complexity

- Time: O(V + E) — two DFS passes
- Space: O(V + E)

---

## Pattern 6: Minimum Spanning Tree

### The Story

You're laying fiber-optic cables between cities. Each potential cable segment has a cost. You want every city connected (directly or indirectly) with minimum total cable cost. No redundant cables needed.

Two algorithms solve this: Kruskal's and Prim's. Both produce the same MST (or one of several if there are ties), but they approach it differently.

### Kruskal's vs Prim's: When to Choose

```
Kruskal's (edge-based):
  → Sort edges by weight, greedily add cheapest edge that doesn't create a cycle
  → Uses DSU for cycle detection
  → Better for SPARSE graphs (few edges, E ~ V or E ~ V log V)
  → Time: O(E log E)

Prim's (vertex-based):
  → Grow the MST one vertex at a time, always adding the cheapest edge that extends the tree
  → Uses a min-heap
  → Better for DENSE graphs (many edges, E ~ V²)
  → Time: O(E log V) with heap, O(V²) with simple array (good for dense)
```

### Kruskal's Algorithm

(Full implementation in DSU patterns. Here's the summary version.)

```python
def kruskal(n: int, edges: list) -> int:
    """Kruskal's MST. edges = list of (weight, u, v)."""
    edges.sort()
    dsu = DSU(n)
    total = 0
    count = 0
    for w, u, v in edges:
        if dsu.union(u, v):
            total += w
            count += 1
            if count == n - 1:
                break
    return total if count == n - 1 else -1   # -1 if disconnected
```

### Prim's Algorithm

```python
import heapq

def prim(n: int, adj: list) -> int:
    """
    Prim's MST starting from node 0.
    adj[u] = list of (v, weight)
    Returns minimum spanning tree weight.
    """
    visited = [False] * n
    heap = [(0, 0)]   # (weight, node) — start with node 0, cost 0
    total = 0
    edges_used = 0

    while heap and edges_used < n:
        w, u = heapq.heappop(heap)

        if visited[u]:
            continue   # skip stale entries

        visited[u] = True
        total += w
        edges_used += 1

        for v, weight in adj[u]:
            if not visited[v]:
                heapq.heappush(heap, (weight, v))

    return total if edges_used == n else -1   # -1 if disconnected


# Test: 4-node graph
adj = {
    0: [(1,10),(2,6),(3,5)],
    1: [(0,10),(3,15)],
    2: [(0,6),(3,4)],
    3: [(0,5),(1,15),(2,4)],
}
print(prim(4, adj))   # 19: edges (0,3,5)+(2,3,4)+(0,1,10)
```

### ASCII: Prim's Step by Step

```
Graph:
  0 ─(10)─ 1
  │         │
 (6)       (15)
  │         │
  2 ─(4)──  3
   ╲       /
    ──(5)──0

Wait, let me use the adj above:
Edges: 0-1(10), 0-2(6), 0-3(5), 1-3(15), 2-3(4)

Start: heap=[(0,0)], visited={}

Step 1: Pop (0,0). Visit 0. Add neighbors: (10,1),(6,2),(5,3)
  heap = [(5,3),(6,2),(10,1)]
  MST so far: {0}, total=0

Step 2: Pop (5,3). Visit 3. Add neighbors: (10,0 skip),(15,1),(4,2)
  heap = [(4,2),(6,2),(10,1),(15,1)]
  MST edge: 0→3, weight 5. total=5

Step 3: Pop (4,2). Visit 2. Add neighbors: (6,0 skip),(4,3 skip)
  heap = [(6,2),(10,1),(15,1)]
  MST edge: 3→2, weight 4. total=9

Step 4: Pop (6,2). Node 2 already visited, SKIP.

Step 5: Pop (10,1). Visit 1.
  MST edge: 0→1, weight 10. total=19

All 4 nodes visited. MST weight = 19.
MST edges: 0-3(5), 3-2(4), 0-1(10)
```

### Complexity Summary

| Algorithm | Time | Space | Best For |
|---|---|---|---|
| Kruskal's | O(E log E) | O(V) | Sparse graphs |
| Prim's (heap) | O(E log V) | O(V + E) | General |
| Prim's (array) | O(V²) | O(V) | Dense graphs |

---

## Pattern 7: Maximum Flow (Edmonds-Karp)

### The Story

You're managing a water pipe network. Water flows from a source (pump) to a sink (reservoir). Each pipe has a maximum capacity. What's the maximum amount of water you can pump per second?

This is the **Maximum Flow** problem. Edmonds-Karp is Ford-Fulkerson using BFS to find augmenting paths — it's the most practical max flow algorithm for most interview scenarios.

### Core Concepts

- **Residual graph:** For each edge (u,v) with capacity c and current flow f, the residual has:
  - Forward edge: remaining capacity = c - f
  - Backward edge: "undo" capacity = f (allows pushing back previous flow)
- **Augmenting path:** A path from source to sink in the residual graph with available capacity
- **Max flow = sum of flows along all augmenting paths**

### Template Code

```python
from collections import deque

def edmonds_karp(n: int, source: int, sink: int, capacities: list) -> int:
    """
    n: number of nodes
    source: source node
    sink: sink node
    capacities: n×n matrix where capacities[u][v] = capacity of edge u→v
    Returns: maximum flow from source to sink
    """
    # Residual capacity matrix
    residual = [row[:] for row in capacities]   # deep copy

    def bfs_find_path():
        """BFS to find augmenting path. Returns parent array, or None if no path."""
        visited = [False] * n
        visited[source] = True
        parent = [-1] * n
        queue = deque([source])

        while queue:
            u = queue.popleft()
            if u == sink:
                return parent
            for v in range(n):
                if not visited[v] and residual[u][v] > 0:
                    visited[v] = True
                    parent[v] = u
                    queue.append(v)

        return None   # no augmenting path found

    max_flow = 0

    while True:
        parent = bfs_find_path()
        if parent is None:
            break   # no more augmenting paths → we're done

        # Find minimum residual capacity along the path
        path_flow = float('inf')
        v = sink
        while v != source:
            u = parent[v]
            path_flow = min(path_flow, residual[u][v])
            v = u

        # Update residual capacities along the path
        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= path_flow   # reduce forward capacity
            residual[v][u] += path_flow   # increase backward capacity (undo option)
            v = u

        max_flow += path_flow

    return max_flow


# Test: 6-node network
# Nodes: 0=source, 5=sink
cap = [
    [0, 16, 13,  0,  0,  0],
    [0,  0,  4, 12,  0,  0],
    [0,  0,  0,  0, 14,  0],
    [0,  0,  9,  0,  0, 20],
    [0,  0,  0,  7,  0,  4],
    [0,  0,  0,  0,  0,  0],
]
print(edmonds_karp(6, 0, 5, cap))  # 23
```

### Adjacency List Version (More Practical)

```python
def max_flow_adj(n: int, source: int, sink: int, edges: list) -> int:
    """
    edges: list of (u, v, capacity)
    Uses adjacency list with edge index trick for efficient residual updates.
    """
    graph = [[] for _ in range(n)]
    # Each edge stored as [to, capacity, rev_index]
    # For each edge, add forward + backward (residual) edge

    def add_edge(u, v, cap):
        graph[u].append([v, cap, len(graph[v])])
        graph[v].append([u, 0, len(graph[u]) - 1])   # backward edge with 0 capacity

    for u, v, cap in edges:
        add_edge(u, v, cap)

    def bfs():
        visited = [-1] * n
        visited[source] = source
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for i, (v, cap, _) in enumerate(graph[u]):
                if visited[v] == -1 and cap > 0:
                    visited[v] = u
                    if v == sink:
                        return visited
                    queue.append(v)
        return None

    total_flow = 0
    while True:
        parent = bfs()
        if parent is None:
            break
        # Find bottleneck
        path_flow = float('inf')
        v = sink
        while v != source:
            u = parent[v]
            for to, cap, _ in graph[u]:
                if to == v and cap > 0:
                    path_flow = min(path_flow, cap)
                    break
            v = u
        # Update flow
        v = sink
        while v != source:
            u = parent[v]
            for i, (to, cap, rev) in enumerate(graph[u]):
                if to == v and cap > 0:
                    graph[u][i][1] -= path_flow
                    graph[v][rev][1] += path_flow
                    break
            v = u
        total_flow += path_flow
    return total_flow
```

### Applications

- **Bipartite Matching:** Students (left) → Projects (right). Can all students be assigned? Max matching = max flow. Add super-source connected to all students, super-sink connected to all projects.
- **Network capacity:** Internet routing, traffic flow
- **Min-cut / Max-flow theorem:** The minimum cut (set of edges whose removal disconnects source from sink) equals the maximum flow

### Complexity

- Edmonds-Karp: O(V × E²)
- For competitive programming with larger flows, use Dinic's: O(V² × E)

---

## Pattern 8: A* Search (Heuristic Pathfinding)

### The Story

You're a game character on a grid. You need to get from position S to position E, avoiding walls. Dijkstra would explore in all directions equally — like a spreading ripple. A* is smarter: it uses a heuristic (an estimate of remaining distance to goal) to focus exploration toward the goal direction.

Think of it as Dijkstra with a compass. The compass doesn't tell you the exact remaining distance, but it gives a good estimate. A* uses this to prioritize paths that are heading in the right direction.

### The Formula: f = g + h

- **g(n):** actual cost from start to node n (known exactly)
- **h(n):** estimated cost from n to goal (heuristic, must be admissible: never overestimate)
- **f(n) = g(n) + h(n):** total estimated cost of path through n

A* uses a min-heap of (f, node) instead of Dijkstra's (g, node).

### Admissible Heuristics

- **Grid (4-directional):** Manhattan distance: `|x1-x2| + |y1-y2|`
- **Grid (8-directional):** Chebyshev distance: `max(|x1-x2|, |y1-y2|)`
- **General graph:** Euclidean distance (if coordinates exist)

If h is admissible, A* is guaranteed to find the optimal path.
If h = 0, A* degenerates to Dijkstra.
If h is very large (inadmissible), A* finds paths fast but not necessarily optimal — this is "greedy best-first search."

### ASCII: A* Focuses Search Toward Goal

```
Grid (S=start, E=end, #=wall):

S . . . . .
. # # # . .
. # . . . .
. . . . # E

Dijkstra explores (distance from S):
  Ripples outward in all directions equally:
  1 2 3 4 5 6
  2 # # # 6 7
  3 # 7 8 9 8  ← explores lots of cells far from E
  4 5 6 7 # 9

A* with Manhattan heuristic focuses toward E (top-right):
  Explores fewer cells by prioritizing those near E
  Many cells near the bottom-left are never explored!
  A* might explore only 60% of what Dijkstra would.

The heuristic "pulls" the search toward the goal.
```

### Template Code: A* on a Grid

```python
import heapq

def astar_grid(grid: list, start: tuple, end: tuple) -> int:
    """
    grid: 2D list, 0=open, 1=wall
    start, end: (row, col) tuples
    Returns: shortest path length, or -1 if no path
    """
    ROWS, COLS = len(grid), len(grid[0])
    sr, sc = start
    er, ec = end

    def heuristic(r, c):
        # Manhattan distance to end
        return abs(r - er) + abs(c - ec)

    # (f=g+h, g, row, col)
    heap = [(heuristic(sr, sc), 0, sr, sc)]
    dist = {start: 0}

    while heap:
        f, g, r, c = heapq.heappop(heap)

        if (r, c) == end:
            return g

        # Skip stale entries
        if g > dist.get((r, c), float('inf')):
            continue

        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] == 0:
                new_g = g + 1
                if new_g < dist.get((nr, nc), float('inf')):
                    dist[(nr, nc)] = new_g
                    new_h = heuristic(nr, nc)
                    heapq.heappush(heap, (new_g + new_h, new_g, nr, nc))

    return -1   # no path found


# Test
grid = [
    [0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0],
]
print(astar_grid(grid, (0,0), (3,5)))  # some path length
```

### A* with Weighted Moves

```python
def astar_weighted(graph: dict, start, end, heuristic_fn) -> float:
    """
    General A* for weighted graphs.
    graph[u] = list of (v, cost)
    heuristic_fn(node) = estimated cost from node to end
    """
    heap = [(heuristic_fn(start), 0, start)]   # (f, g, node)
    dist = {start: 0}
    prev = {}

    while heap:
        f, g, u = heapq.heappop(heap)

        if u == end:
            # Reconstruct path
            path = []
            curr = end
            while curr in prev:
                path.append(curr)
                curr = prev[curr]
            path.append(start)
            path.reverse()
            return g, path

        if g > dist.get(u, float('inf')):
            continue

        for v, cost in graph.get(u, []):
            new_g = g + cost
            if new_g < dist.get(v, float('inf')):
                dist[v] = new_g
                prev[v] = u
                heapq.heappush(heap, (new_g + heuristic_fn(v), new_g, v))

    return float('inf'), []   # no path
```

### When A* Outperforms Dijkstra

```
A* advantage depends on the quality of the heuristic:

Dijkstra explores:  ~1000 nodes to find path across large grid
A* explores:        ~300 nodes (with good heuristic)

A* is essentially Dijkstra + directional guidance.
On uniform grids, A* with Manhattan heuristic typically explores
4x fewer nodes than Dijkstra for long-range pathfinding.

When does A* not help?
  - Goal is very close to source (Dijkstra already fast)
  - Heuristic is weak (h ≈ 0 → just Dijkstra)
  - Dense obstacles force exploration of nearly all cells anyway
```

### Complexity

- Worst case: same as Dijkstra, O((V + E) log V)
- Average case with good heuristic: significantly fewer nodes explored
- Space: O(V) for heap and distance map

---

## Algorithm Selection Quick Reference

```
PROBLEM TYPE                           ALGORITHM
------------------------------------------------------------------
Single source, no negative weights     → Dijkstra
Single source, negative weights        → Bellman-Ford
All pairs, small graph                 → Floyd-Warshall
Dependency ordering / cycle detect     → Topological Sort (Kahn's)
Groups of mutual reachability          → Kosaraju's SCC
Connect all with minimum cost          → Kruskal's or Prim's
Maximum flow, min cut, bipartite match → Edmonds-Karp
Grid pathfinding with goal estimate    → A*

GRAPH PROPERTIES → ALGORITHM CHOICE
------------------------------------------------------------------
Undirected + connectivity queries      → DSU (Union-Find)
Directed + cycles                      → DFS with coloring / Topo sort
Directed + shortest path               → Dijkstra or Bellman-Ford
Directed + strongly connected groups   → Kosaraju / Tarjan
Weighted + minimum spanning tree       → Kruskal (sparse) / Prim (dense)
Flow network                           → Max flow algorithms

WHEN ALGORITHMS FAIL
------------------------------------------------------------------
Dijkstra + negative edges              → WRONG (use Bellman-Ford)
Topo sort on undirected graph          → Meaningless (use DFS)
Floyd-Warshall + large graph (V>1000)  → TLE (use Dijkstra per node)
DSU + directed graph cycles            → WRONG (use DFS coloring)
A* + inadmissible heuristic            → Sub-optimal path
```

---

## Common Bugs in Advanced Graph Problems

```python
# Bug 1: Dijkstra — not skipping stale heap entries
while heap:
    d, u = heapq.heappop(heap)
    # WRONG: process u every time it's popped
    # CORRECT:
    if d > dist[u]:
        continue   # stale, skip

# Bug 2: Bellman-Ford — checking negative cycle on unreachable nodes
# If dist[u] is still inf, u is unreachable.
# An update dist[u]+w < dist[v] where dist[u]=inf doesn't make sense.
for u, v, w in edges:
    if dist[u] != float('inf') and dist[u] + w < dist[v]:
        # ← always guard with dist[u] != inf

# Bug 3: Floyd-Warshall — wrong loop order (k must be outermost)
# WRONG:
for i in range(n):
    for j in range(n):
        for k in range(n):  # k is INNERMOST — WRONG!
            ...
# CORRECT:
for k in range(n):   # k = intermediate node, MUST be outermost
    for i in range(n):
        for j in range(n):
            ...

# Bug 4: Topological sort — not checking for cycle (result length < n)
result = topo_sort(n, edges)
if len(result) < n:
    # Cycle detected! Handle this case.

# Bug 5: Edmonds-Karp — forgetting to add backward edges in residual graph
# Every edge (u,v,cap) needs a backward edge (v,u,0) in the residual
# The backward edge allows "undoing" previously committed flow

# Bug 6: A* — using inadmissible heuristic
# Heuristic MUST NEVER OVERESTIMATE the true remaining distance
# If it overestimates, A* may not find the optimal path
# Manhattan distance is admissible for 4-directional grids
# Euclidean distance is admissible for any direct-path movement
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Real World Usage →](./real_world_usage.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
