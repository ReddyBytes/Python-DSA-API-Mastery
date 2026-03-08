# Graphs — Quick Reference Cheatsheet

## Graph Representations

### Adjacency List (most common in interviews)

```python
from collections import defaultdict
graph = defaultdict(list)
graph[0].append(1)
graph[0].append(2)
graph[1].append(3)
# graph = {0: [1, 2], 1: [3], 2: [], 3: []}
```

### Adjacency Matrix

```python
n = 4
graph = [[0]*n for _ in range(n)]
graph[0][1] = 1     # unweighted
graph[0][2] = 5     # weighted: store weight instead of 1
```

### Edge List

```python
edges = [(0,1), (0,2), (1,3)]               # unweighted
edges = [(0,1,4), (0,2,2), (1,3,7)]         # (u, v, weight)
```

### Comparison Table

| Representation  | Space    | Add Edge | Edge Query  | Neighbors | Best For                   |
|-----------------|----------|----------|-------------|-----------|----------------------------|
| Adjacency List  | O(V+E)   | O(1)     | O(degree)   | O(degree) | Sparse graphs (interviews) |
| Adjacency Matrix| O(V^2)   | O(1)     | O(1)        | O(V)      | Dense graphs, fast lookup  |
| Edge List       | O(E)     | O(1)     | O(E)        | O(E)      | Sorting edges (Kruskal)    |

---

## BFS Template (Iterative)

```python
from collections import deque

def bfs(graph, start):
    visited = set([start])
    queue = deque([start])
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return result

# BFS shortest path (unweighted)
def bfs_shortest(graph, start, end):
    visited = set([start])
    queue = deque([(start, 0)])         # (node, distance)
    while queue:
        node, dist = queue.popleft()
        if node == end:
            return dist
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
    return -1                           # unreachable
```

---

## DFS Templates

### Recursive DFS

```python
def dfs_recursive(graph, node, visited=None):
    if visited is None:
        visited = set()
    visited.add(node)
    result = [node]
    for neighbor in graph[node]:
        if neighbor not in visited:
            result += dfs_recursive(graph, neighbor, visited)
    return result
```

### Iterative DFS (Stack)

```python
def dfs_iterative(graph, start):
    visited = set()
    stack = [start]
    result = []

    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            result.append(node)
            for neighbor in graph[node]:     # reverse to match recursive order
                if neighbor not in visited:
                    stack.append(neighbor)
    return result
```

---

## BFS vs DFS Decision Guide

| Goal                              | BFS    | DFS    | Reason                               |
|-----------------------------------|--------|--------|--------------------------------------|
| Shortest path (unweighted)        | YES    | NO     | BFS explores level by level          |
| Detect cycle (undirected)         | YES    | YES    | Both work                            |
| Detect cycle (directed)           | NO     | YES    | Need recursion stack for back edges  |
| Topological sort                  | YES    | YES    | Kahn's (BFS) or post-order (DFS)     |
| Connected components              | YES    | YES    | Both work                            |
| Bipartite check                   | YES    | YES    | Color alternating layers             |
| Path exists between two nodes     | YES    | YES    | DFS is simpler                       |
| All paths from source to dest     | NO     | YES    | DFS with backtracking                |
| Level-order traversal             | YES    | NO     | BFS natural for levels               |
| Deep graph (avoid stack overflow) | YES    | NO     | BFS uses queue (heap memory)         |

---

## Dijkstra — Shortest Path (Weighted, Non-Negative)

```python
import heapq

def dijkstra(graph, start):
    # graph[u] = [(v, weight), ...]
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    heap = [(0, start)]            # (distance, node)

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:            # stale entry — skip
            continue
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))
    return dist
# Time: O((V + E) log V)  |  Space: O(V)
# FAILS with negative weights — use Bellman-Ford instead
```

---

## Bellman-Ford — Shortest Path (Handles Negative Weights)

```python
def bellman_ford(V, edges, start):
    # edges = [(u, v, weight), ...]
    dist = [float('inf')] * V
    dist[start] = 0

    for _ in range(V - 1):              # relax V-1 times
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w

    # Check for negative cycles
    for u, v, w in edges:
        if dist[u] + w < dist[v]:
            return None                 # negative cycle exists
    return dist
# Time: O(V * E)  |  Space: O(V)
```

---

## Floyd-Warshall — All Pairs Shortest Path

```python
def floyd_warshall(graph, V):
    dist = [[float('inf')] * V for _ in range(V)]
    for i in range(V):
        dist[i][i] = 0
    for u, v, w in graph:
        dist[u][v] = w

    for k in range(V):                  # intermediate node
        for i in range(V):
            for j in range(V):
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
    return dist
# Time: O(V^3)  |  Space: O(V^2)
# Use: small graphs, all-pairs distances, transitive closure
```

---

## Topological Sort

### Kahn's Algorithm (BFS — iterative)

```python
from collections import deque

def topo_sort_bfs(V, adj):
    in_degree = [0] * V
    for u in range(V):
        for v in adj[u]:
            in_degree[v] += 1

    queue = deque([i for i in range(V) if in_degree[i] == 0])
    order = []

    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    return order if len(order) == V else []  # empty → cycle exists
```

### DFS Post-Order

```python
def topo_sort_dfs(V, adj):
    visited = set()
    result = []

    def dfs(u):
        visited.add(u)
        for v in adj[u]:
            if v not in visited:
                dfs(v)
        result.append(u)            # append AFTER visiting all neighbors

    for i in range(V):
        if i not in visited:
            dfs(i)
    return result[::-1]             # reverse post-order
```

---

## Connected Components Template

```python
def count_components(n, edges):
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)          # undirected

    visited = set()
    count = 0

    def dfs(node):
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor)

    for i in range(n):
        if i not in visited:
            dfs(i)
            count += 1
    return count
```

---

## Bipartite Check Template

```python
def is_bipartite(graph):
    color = {}                          # node → 0 or 1

    for start in graph:
        if start in color:
            continue
        queue = deque([start])
        color[start] = 0
        while queue:
            node = queue.popleft()
            for neighbor in graph[node]:
                if neighbor not in color:
                    color[neighbor] = 1 - color[node]   # flip color
                    queue.append(neighbor)
                elif color[neighbor] == color[node]:    # same color = not bipartite
                    return False
    return True
```

---

## Cycle Detection

```python
# Undirected — DFS with parent tracking
def has_cycle_undirected(graph, V):
    visited = set()
    def dfs(node, parent):
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                if dfs(neighbor, node):
                    return True
            elif neighbor != parent:    # back edge to non-parent → cycle
                return True
        return False
    return any(dfs(i, -1) for i in range(V) if i not in visited)

# Directed — DFS with recursion stack
def has_cycle_directed(graph, V):
    visited, rec_stack = set(), set()
    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                if dfs(neighbor): return True
            elif neighbor in rec_stack:     # back edge → cycle
                return True
        rec_stack.remove(node)
        return False
    return any(dfs(i) for i in range(V) if i not in visited)
```

---

## Interview Signals

```
"connected / reachable"          → BFS/DFS + visited set
"shortest path (unweighted)"     → BFS
"shortest path (weighted)"       → Dijkstra
"negative weights"               → Bellman-Ford
"all pairs shortest path"        → Floyd-Warshall
"ordering with dependencies"     → Topological sort
"cycle detection"                → DFS with rec_stack (directed)
"number of islands"              → DFS/BFS on grid (treat as graph)
"bipartite / two-coloring"       → BFS with alternating colors
"minimum spanning tree"          → Kruskal (edges) / Prim (nodes)
"strongly connected components"  → Tarjan's / Kosaraju's
```

---

## Common Mistakes

```
MISTAKE 1: Not marking visited before entering queue (BFS)
  Wrong:  add to visited when popped
  Right:  add to visited when pushed — prevents duplicate queue entries

MISTAKE 2: Using Dijkstra with negative weights
  Must use Bellman-Ford or SPFA for negative edge weights

MISTAKE 3: Missing disconnected components
  Always loop over all nodes: for i in range(V): if i not in visited: dfs(i)

MISTAKE 4: Forgetting to handle directed vs undirected
  Undirected: add edge both ways in adjacency list
  Directed: add edge one way only

MISTAKE 5: Topological sort on graph with cycle
  Kahn's: len(order) < V → cycle; always validate output size
```
