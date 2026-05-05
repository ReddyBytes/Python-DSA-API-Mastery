# Advanced Graphs — Cheatsheet

---

## Algorithm Selection Guide

| Problem                                     | Algorithm                     | Complexity          |
|---------------------------------------------|-------------------------------|---------------------|
| Shortest path, non-negative weights         | Dijkstra                      | O((V+E) log V)      |
| Shortest path, negative weights             | Bellman-Ford                  | O(VE)               |
| Shortest path, negative cycles detection    | Bellman-Ford                  | O(VE)               |
| Shortest path, unweighted                   | BFS                           | O(V+E)              |
| All-pairs shortest path                     | Floyd-Warshall                | O(V^3)              |
| Topological order, DAG                      | Kahn's (BFS) or DFS           | O(V+E)              |
| Minimum spanning tree                       | Kruskal's or Prim's           | O(E log E)          |
| Strongly connected components               | Kosaraju's or Tarjan's        | O(V+E)              |
| Maximum flow / min cut                      | Ford-Fulkerson / Edmonds-Karp | O(VE^2)             |
| Bridges / articulation points              | Tarjan's (DFS + low)          | O(V+E)              |
| Bipartite check                             | BFS/DFS 2-coloring            | O(V+E)              |

---

## Dijkstra's Algorithm

```python
import heapq
from collections import defaultdict

def dijkstra(graph, src, n):
    # graph: {u: [(v, weight), ...]}
    dist = [float('inf')] * n
    dist[src] = 0
    heap = [(0, src)]            # (cost, node)

    while heap:
        cost, u = heapq.heappop(heap)
        if cost > dist[u]: continue    # stale entry, skip
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))

    return dist                        # dist[i] = shortest from src to i

# Reconstruct path: track prev[] array
def dijkstra_with_path(graph, src, dst, n):
    dist = [float('inf')] * n
    prev = [-1] * n
    dist[src] = 0
    heap = [(0, src)]
    while heap:
        cost, u = heapq.heappop(heap)
        if cost > dist[u]: continue
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                heapq.heappush(heap, (dist[v], v))
    # Reconstruct
    path, node = [], dst
    while node != -1:
        path.append(node); node = prev[node]
    return dist[dst], path[::-1]
```

**Gotcha:** Does NOT work with negative edge weights.

---

## Bellman-Ford Algorithm

```python
def bellman_ford(n, edges, src):
    # edges: list of (u, v, weight)
    dist = [float('inf')] * n
    dist[src] = 0

    for _ in range(n - 1):            # relax all edges n-1 times
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w

    # Detect negative cycle: if any edge still relaxes, cycle exists
    for u, v, w in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            return None               # negative cycle detected

    return dist
```

**Use when:** negative edge weights, detecting negative cycles.
**Time:** O(VE) — slower than Dijkstra but handles negatives.

---

## Topological Sort — Kahn's Algorithm (BFS)

```python
from collections import deque

def topo_sort_kahn(n, edges):
    # edges: list of (u -> v) directed edges
    indegree = [0] * n
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        indegree[v] += 1

    queue = deque([i for i in range(n) if indegree[i] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != n:
        return []                     # cycle detected — no valid topo order
    return order
```

---

## Topological Sort — DFS

```python
def topo_sort_dfs(n, edges):
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)

    visited = [0] * n   # 0=unvisited, 1=in-stack, 2=done
    order = []
    has_cycle = [False]

    def dfs(node):
        if has_cycle[0]: return
        visited[node] = 1            # mark as in current DFS stack
        for neighbor in graph[node]:
            if visited[neighbor] == 1:
                has_cycle[0] = True; return
            if visited[neighbor] == 0:
                dfs(neighbor)
        visited[node] = 2
        order.append(node)           # append AFTER visiting all neighbors

    for i in range(n):
        if visited[i] == 0:
            dfs(i)

    return [] if has_cycle[0] else order[::-1]   # reverse for correct order
```

---

## Minimum Spanning Tree

### Kruskal's (Sort Edges + DSU)

```python
def kruskal(n, edges):
    # edges: [(weight, u, v)]
    edges.sort()
    parent = list(range(n))
    rank   = [0] * n

    def find(x):
        if parent[x] != x: parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry: return False
        if rank[rx] < rank[ry]: rx, ry = ry, rx
        parent[ry] = rx
        if rank[rx] == rank[ry]: rank[rx] += 1
        return True

    mst_cost = 0
    for w, u, v in edges:
        if union(u, v):
            mst_cost += w
    return mst_cost
# O(E log E)
```

### Prim's (Greedy + Heap)

```python
def prim(n, graph):
    # graph: {u: [(v, weight), ...]}
    visited = [False] * n
    min_heap = [(0, 0)]      # (cost, node), start from node 0
    total_cost = 0

    while min_heap:
        cost, u = heapq.heappop(min_heap)
        if visited[u]: continue
        visited[u] = True
        total_cost += cost
        for v, w in graph[u]:
            if not visited[v]:
                heapq.heappush(min_heap, (w, v))

    return total_cost
# O(E log V) with binary heap
```

**Kruskal vs Prim:**
- Kruskal: better for sparse graphs, needs edge list
- Prim: better for dense graphs, needs adjacency list

---

## Strongly Connected Components — Kosaraju's

```python
def kosaraju(n, graph):
    # Pass 1: DFS on original graph, record finish order
    visited = [False] * n
    finish_stack = []

    def dfs1(u):
        visited[u] = True
        for v in graph[u]:
            if not visited[v]: dfs1(v)
        finish_stack.append(u)

    for i in range(n):
        if not visited[i]: dfs1(i)

    # Build reversed graph
    rev = [[] for _ in range(n)]
    for u in range(n):
        for v in graph[u]:
            rev[v].append(u)

    # Pass 2: DFS on reversed graph in reverse finish order
    visited = [False] * n
    sccs = []

    def dfs2(u, component):
        visited[u] = True
        component.append(u)
        for v in rev[u]:
            if not visited[v]: dfs2(v, component)

    while finish_stack:
        u = finish_stack.pop()
        if not visited[u]:
            component = []
            dfs2(u, component)
            sccs.append(component)

    return sccs   # each inner list is one SCC
```

---

## Network Flow — Concept Only

```
Ford-Fulkerson: repeatedly find augmenting paths from source to sink,
               add flow equal to bottleneck (min capacity on path).
               Repeat until no augmenting path.
               Max flow = Min cut (max-flow min-cut theorem)

Edmonds-Karp:  Ford-Fulkerson with BFS to find augmenting paths.
               Time: O(VE^2)

Key terms:
- Residual graph: forward edge (remaining capacity) + backward edge (cancel flow)
- Augmenting path: any path from source to sink with positive residual capacity
- Min cut: minimum capacity set of edges whose removal disconnects source from sink
```

---

## Bridges and Articulation Points — Concept

```
Bridge: an edge whose removal disconnects the graph
Articulation point: a vertex whose removal disconnects the graph

Algorithm (Tarjan's): DFS + track discovery time (disc[]) and lowest
reachable time (low[]).
- Edge (u,v) is a bridge if low[v] > disc[u]
- Node u is articulation point if:
  - u is root with 2+ children, OR
  - u is non-root and low[child] >= disc[u]
```

---

## Floyd-Warshall (All-Pairs Shortest Path)

```python
def floyd_warshall(n, edges):
    INF = float('inf')
    dist = [[INF]*n for _ in range(n)]
    for i in range(n): dist[i][i] = 0
    for u, v, w in edges: dist[u][v] = min(dist[u][v], w)

    for k in range(n):
        for i in range(n):
            for j in range(n):
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

    # Check for negative cycles: dist[i][i] < 0
    return dist
# O(V^3), good for dense graphs or when all-pairs needed
```

---

## Common Algorithm Complexities

| Algorithm         | Time           | Space  | Notes                            |
|-------------------|----------------|--------|----------------------------------|
| BFS               | O(V+E)         | O(V)   | Unweighted shortest path         |
| DFS               | O(V+E)         | O(V)   | Topo sort, cycle, SCC            |
| Dijkstra          | O((V+E) log V) | O(V)   | Non-negative weights             |
| Bellman-Ford      | O(VE)          | O(V)   | Negative weights                 |
| Floyd-Warshall    | O(V^3)         | O(V^2) | All-pairs                        |
| Kruskal's         | O(E log E)     | O(V)   | Sparse graphs, MST               |
| Prim's            | O(E log V)     | O(V)   | Dense graphs, MST                |
| Kahn's Topo       | O(V+E)         | O(V)   | Detect cycle in directed graph   |
| Kosaraju's SCC    | O(V+E)         | O(V)   | Two DFS passes                   |
| Edmonds-Karp Flow | O(VE^2)        | O(V+E) | Max flow                         |

---

## Gotchas

- Dijkstra: skip stale heap entries with `if cost > dist[u]: continue`
- Bellman-Ford: run exactly n-1 iterations; nth iteration detects negative cycles
- Kahn's: output length < n means graph has a cycle
- DFS topo sort: append node AFTER visiting all neighbors, then reverse
- Kruskal's: sort edges by weight, not nodes
- Prim's: check `if visited[u]: continue` to handle stale heap entries
- Floyd-Warshall: intermediate vertex `k` must be the outermost loop

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Visual Explanation](./visual_explanation.md) &nbsp;|&nbsp; **Next:** [Patterns →](./patterns.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
