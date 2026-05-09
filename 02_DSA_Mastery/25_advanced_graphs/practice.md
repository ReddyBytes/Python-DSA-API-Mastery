# 💻 Practice — Advanced Graphs

## Quick Index

| Q# | Topic | Difficulty |
|---|---|---|
| [Q1](#q1) | Dijkstra — basic single-source shortest path | 🟢 Easy |
| [Q2](#q2) | Dijkstra — path reconstruction | 🟢 Easy |
| [Q3](#q3) | Dijkstra — detect unreachable nodes | 🟢 Easy |
| [Q4](#q4) | Bellman-Ford — shortest path with negative edges | 🟢 Easy |
| [Q5](#q5) | Bellman-Ford — negative cycle detection | 🟢 Easy |
| [Q6](#q6) | Floyd-Warshall — all-pairs shortest path | 🟢 Easy |
| [Q7](#q7) | Topological sort — Kahn's algorithm basics | 🟡 Medium |
| [Q8](#q8) | Topological sort — cycle detection via Kahn's | 🟡 Medium |
| [Q9](#q9) | Topological sort — DFS post-order | 🟡 Medium |
| [Q10](#q10) | Topological sort — course schedule (LeetCode 207 style) | 🟡 Medium |
| [Q11](#q11) | SCC — Kosaraju's algorithm | 🟡 Medium |
| [Q12](#q12) | SCC — count strongly connected components | 🟡 Medium |
| [Q13](#q13) | SCC — condensation graph | 🟡 Medium |
| [Q14](#q14) | Kruskal's MST — minimum spanning tree weight | 🟡 Medium |
| [Q15](#q15) | Prim's MST — minimum spanning tree weight | 🟡 Medium |
| [Q16](#q16) | MST — when to use Kruskal vs Prim | 🟡 Medium |
| [Q17](#q17) | Network flow — max flow via Edmonds-Karp | 🟠 Hard |
| [Q18](#q18) | Network flow — bipartite matching via max flow | 🟠 Hard |
| [Q19](#q19) | Floyd-Warshall — negative cycle via diagonal | 🟠 Hard |
| [Q20](#q20) | Floyd-Warshall — transitive closure | 🟠 Hard |
| [Q21](#q21) | Algorithm selection — choose the right algorithm | 🟠 Hard |
| [Q22](#q22) | Dijkstra — stale entry bug and fix | 🟠 Hard |
| [Q23](#q23) | Bellman-Ford — mark all nodes on negative cycles | 🟠 Hard |
| [Q24](#q24) | Bipartite checking via BFS 2-coloring | 🟠 Hard |
| [Q25](#q25) | Directed cycle detection — DFS WHITE/GRAY/BLACK | 🟠 Hard |

---

<a id="q1"></a>
### Q1 · Dijkstra — Single-Source Shortest Path

🟢 Easy

**Problem:** Given a weighted directed graph and a source node, return the shortest distance from the source to every other node. All edge weights are non-negative.

```
Graph (0 → 1: 4, 0 → 2: 1, 2 → 1: 2, 1 → 3: 1, 2 → 3: 5):
  0 ──4──> 1 ──1──> 3
  │        ^
  1        2
  v        │
  2 ───────┘
```

Expected output from source 0: `[0, 3, 1, 4]`

<details><summary>💡 Hint</summary>

Use a min-heap `(distance, node)`. Always process the node with the smallest known distance first. When you pop a node, check if the popped distance is stale (`d > dist[u]`). If so, skip it — a shorter path was already found.

</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

def dijkstra(graph, n, source):
    dist = [float('inf')] * n
    dist[source] = 0
    heap = [(0, source)]   # (distance, node)

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue   # stale entry — skip
        for v, weight in graph.get(u, []):
            new_dist = dist[u] + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))

    return dist

g = {0: [(1,4),(2,1)], 1: [(3,1)], 2: [(1,2),(3,5)], 3: []}
print(dijkstra(g, 4, 0))   # [0, 3, 1, 4]
```

**Why:** Dijkstra is greedy — once a node is popped, its distance is final (valid only because all weights are non-negative). The stale-entry check is critical for correctness and performance: without it, the heap can grow to O(E) and re-process already-finalized nodes.

</details>

> 💻 Try it: [practice_local.py → Q1](./practice_local.py)

---

<a id="q2"></a>
### Q2 · Dijkstra — Path Reconstruction

🟢 Easy

**Problem:** Extend Dijkstra to also return the actual shortest path from source to a given destination, not just the distance.

<details><summary>💡 Hint</summary>

Maintain a `prev` array where `prev[v] = u` means "we reached v via u on the shortest path." After running Dijkstra, walk backwards from the destination using `prev` until you reach the source, then reverse.

</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

def dijkstra_with_path(graph, n, source, dest):
    dist = [float('inf')] * n
    prev = [-1] * n
    dist[source] = 0
    heap = [(0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        if u == dest:
            break   # optional early exit
        for v, weight in graph.get(u, []):
            new_dist = dist[u] + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(heap, (new_dist, v))

    # Reconstruct path
    if dist[dest] == float('inf'):
        return float('inf'), []
    path = []
    curr = dest
    while curr != -1:
        path.append(curr)
        curr = prev[curr]
    path.reverse()
    return dist[dest], path

g = {0: [(1,4),(2,1)], 1: [(3,1)], 2: [(1,2),(3,5)], 3: []}
dist, path = dijkstra_with_path(g, 4, 0, 3)
print(dist, path)   # 4, [0, 2, 1, 3]
```

**Why:** Tracking predecessors adds O(V) space. The path reconstruction walks backwards in O(V) time. This pattern appears in navigation systems, network routing, and any problem where you need the path itself, not just its cost.

</details>

> 💻 Try it: [practice_local.py → Q2](./practice_local.py)

---

<a id="q3"></a>
### Q3 · Dijkstra — Unreachable Nodes

🟢 Easy

**Problem:** In a disconnected graph, some nodes may be unreachable from the source. Given the Dijkstra distance array, how do you identify them? What value do they hold and why?

**Example:** Graph has nodes 0, 1, 2 but only edge 0→1. Node 2 is isolated.

<details><summary>💡 Hint</summary>

Nodes that are never relaxed keep their initial value. What is the initial value of every distance in Dijkstra?

</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

def dijkstra(graph, n, source):
    dist = [float('inf')] * n   # unreachable nodes stay at inf
    dist[source] = 0
    heap = [(0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, weight in graph.get(u, []):
            new_dist = dist[u] + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))

    return dist

g = {0: [(1, 2)], 1: [], 2: []}   # node 2 is unreachable
dist = dijkstra(g, 3, 0)
print(dist)             # [0, 2, inf]
print(dist[2] == float('inf'))    # True — node 2 unreachable
```

**Why:** Unreachable nodes are never relaxed, so `dist[v]` stays at `float('inf')`. Always check `dist[v] != float('inf')` before using the distance value in further calculations. This also guards against the Bellman-Ford bug of relaxing through unreachable nodes.

</details>

> 💻 Try it: [practice_local.py → Q3](./practice_local.py)

---

<a id="q4"></a>
### Q4 · Bellman-Ford — Shortest Path with Negative Edges

🟢 Easy

**Problem:** Given a graph with negative edge weights (but no negative cycles), find shortest distances from a source node.

```
Edges: (0→1, w=5), (1→2, w=-6), (0→2, w=2)
Source: 0
Expected: dist = [0, 5, -1]
```

Why does Dijkstra fail here?

<details><summary>💡 Hint</summary>

Bellman-Ford relaxes ALL edges V-1 times. After V-1 passes, the shortest path (which uses at most V-1 edges) is fully settled. Unlike Dijkstra, it does not finalize any node early.

</details>

<details>
<summary>✅ Answer</summary>

```python
def bellman_ford(n, edges, source):
    """
    edges: list of (u, v, weight)
    Returns (dist, has_negative_cycle)
    """
    dist = [float('inf')] * n
    dist[source] = 0

    for _ in range(n - 1):
        updated = False
        for u, v, weight in edges:
            if dist[u] != float('inf') and dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                updated = True
        if not updated:
            break   # early exit: already optimal

    # V-th pass: detect negative cycle
    has_neg_cycle = False
    for u, v, weight in edges:
        if dist[u] != float('inf') and dist[u] + weight < dist[v]:
            has_neg_cycle = True
            break

    return dist, has_neg_cycle

edges = [(0,1,5), (1,2,-6), (0,2,2)]
dist, neg = bellman_ford(3, edges, 0)
print(dist, neg)   # [0, 5, -1], False
```

**Why Dijkstra fails:** Dijkstra finalizes node 2 at distance 2 (via 0→2) before it processes node 1. Then when it finds 1→2 with weight -6, giving distance 5+(-6)=-1, node 2 is already finalized and won't be updated. Bellman-Ford revisits all edges repeatedly so it correctly finds -1.

</details>

> 💻 Try it: [practice_local.py → Q4](./practice_local.py)

---

<a id="q5"></a>
### Q5 · Bellman-Ford — Negative Cycle Detection

🟢 Easy

**Problem:** Detect whether a graph contains a negative-weight cycle reachable from the source.

```
Edges: (0→1, w=1), (1→2, w=-3), (2→0, w=1)
Cycle weight: 1 + (-3) + 1 = -1 < 0  ← negative cycle!
```

<details><summary>💡 Hint</summary>

After V-1 relaxation passes, all shortest paths are settled. Run one more pass. If ANY edge can still be relaxed, a negative cycle exists — because you could loop it forever to keep decreasing distance.

Always guard with `dist[u] != float('inf')` to avoid spurious detections on unreachable edges.

</details>

<details>
<summary>✅ Answer</summary>

```python
def bellman_ford(n, edges, source):
    dist = [float('inf')] * n
    dist[source] = 0

    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w

    # The V-th pass is the cycle detector
    for u, v, w in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            return dist, True   # negative cycle found

    return dist, False

edges = [(0,1,1), (1,2,-3), (2,0,1)]
dist, has_cycle = bellman_ford(3, edges, 0)
print(has_cycle)   # True

edges2 = [(0,1,1), (0,2,4), (1,2,2), (1,3,5), (2,3,-3)]
dist2, has_cycle2 = bellman_ford(4, edges2, 0)
print(has_cycle2, dist2)   # False, [0, 1, 3, 0]
```

**Why:** The key insight: a shortest path can have at most V-1 edges (otherwise it revisits a node and the cycle can be removed for a shorter/equal path). After V-1 relaxations, any further improvement means infinite negative looping — a negative cycle.

</details>

> 💻 Try it: [practice_local.py → Q5](./practice_local.py)

---

<a id="q6"></a>
### Q6 · Floyd-Warshall — All-Pairs Shortest Path

🟢 Easy

**Problem:** Given a small directed weighted graph, compute the shortest distance between every pair of nodes.

```
Edges: (0→1, w=3), (1→2, w=1), (2→3, w=2), (0→3, w=10)
Expected: dist[0][3] = 6  (via 0→1→2→3 = 3+1+2)
```

<details><summary>💡 Hint</summary>

Initialize a V×V distance matrix. Set `dist[i][i] = 0`, direct edges to their weight, everything else to infinity. Then iterate: for each intermediate node `k`, check if `dist[i][k] + dist[k][j] < dist[i][j]`. The `k` loop MUST be outermost.

</details>

<details>
<summary>✅ Answer</summary>

```python
def floyd_warshall(n, edges):
    """
    Returns dist matrix, or None if negative cycle detected.
    """
    INF = float('inf')
    dist = [[INF] * n for _ in range(n)]

    for i in range(n):
        dist[i][i] = 0

    for u, v, w in edges:
        dist[u][v] = min(dist[u][v], w)   # handle parallel edges

    for k in range(n):          # intermediate node — MUST be outermost
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    for i in range(n):
        if dist[i][i] < 0:
            return None   # negative cycle

    return dist

edges = [(0,1,3),(1,2,1),(2,3,2),(0,3,10)]
dist = floyd_warshall(4, edges)
print(dist[0][3])   # 6 (0→1→2→3)
print(dist[1][0])   # inf (no path back in this directed graph)
```

**Why the k loop must be outermost:** Floyd-Warshall is DP where `dist[i][j]` = "shortest path using only nodes 0..k as intermediates." For this to be correct, we must fully settle all paths through nodes 0..k-1 before considering k as an intermediate. Putting k innermost breaks this ordering.

</details>

> 💻 Try it: [practice_local.py → Q6](./practice_local.py)

---

<a id="q7"></a>
### Q7 · Topological Sort — Kahn's Algorithm Basics

🟡 Medium

**Problem:** Given a DAG as an adjacency list, produce a valid topological ordering using Kahn's BFS-based algorithm.

```
Graph: 0→[1,2], 1→[3], 2→[3], 3→[]
One valid order: [0, 1, 2, 3]
```

What does it mean for an ordering to be "valid"?

<details><summary>💡 Hint</summary>

Valid means: for every directed edge `u → v`, node `u` appears before node `v`. Kahn's works by repeatedly removing nodes with no incoming edges (in-degree 0). Those nodes have all their prerequisites already satisfied.

</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import deque

def topological_sort_kahn(graph, n):
    """
    Returns valid topological order, or [] if cycle detected.
    """
    in_degree = [0] * n
    for u in range(n):
        for v in graph.get(u, []):
            in_degree[v] += 1

    queue = deque(i for i in range(n) if in_degree[i] == 0)
    order = []

    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph.get(u, []):
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    return order if len(order) == n else []   # shorter → cycle

g = {0: [1, 2], 1: [3], 2: [3], 3: []}
result = topological_sort_kahn(g, 4)
print(result)   # [0, 1, 2, 3] or [0, 2, 1, 3] — both valid

# Validate: every edge u→v must have u before v
pos = {node: i for i, node in enumerate(result)}
for u in g:
    for v in g[u]:
        assert pos[u] < pos[v]
```

**Why:** Kahn's key idea: nodes with in-degree 0 have no prerequisites — they're safe to place first. After adding a node, we remove its outgoing edges, which may free up other nodes. Time: O(V + E).

</details>

> 💻 Try it: [practice_local.py → Q7](./practice_local.py)

---

<a id="q8"></a>
### Q8 · Topological Sort — Cycle Detection via Kahn's

🟡 Medium

**Problem:** Use Kahn's algorithm to detect whether a directed graph contains a cycle. Return `True` if a cycle exists.

```
Cycle graph: 0→1, 1→2, 2→0   → has cycle
DAG:         0→1, 1→2, 0→2   → no cycle
```

<details><summary>💡 Hint</summary>

In a cycle, every node involved has at least one incoming edge from another cycle node. No node in the cycle ever reaches in-degree 0. So if the result list is shorter than the number of nodes, a cycle exists.

</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import deque

def has_cycle_directed(n, edges):
    """
    Returns True if the directed graph has a cycle.
    Uses Kahn's algorithm: if topo sort doesn't process all V nodes → cycle.
    """
    adj = [[] for _ in range(n)]
    in_degree = [0] * n

    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1

    queue = deque(i for i in range(n) if in_degree[i] == 0)
    processed = 0

    while queue:
        u = queue.popleft()
        processed += 1
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    return processed != n   # True if cycle exists

# Test
print(has_cycle_directed(3, [(0,1),(1,2),(2,0)]))   # True (cycle)
print(has_cycle_directed(3, [(0,1),(1,2),(0,2)]))   # False (DAG)
print(has_cycle_directed(4, [(0,1),(1,2),(2,3),(3,1)]))  # True (1→2→3→1)
```

**Why:** In a cycle, all nodes in the cycle keep each other's in-degrees above zero indefinitely. They never enter the queue. The cycle check `processed != n` catches this. This is simpler than DFS-based cycle detection and naturally combines with topological sort.

</details>

> 💻 Try it: [practice_local.py → Q8](./practice_local.py)

---

<a id="q9"></a>
### Q9 · Topological Sort — DFS Post-Order

🟡 Medium

**Problem:** Implement topological sort using DFS. How does the post-order traversal guarantee correct ordering?

```
Graph: 0→[1,2], 1→[3], 2→[3], 3→[]
DFS from 0: visit 0 → 1 → 3 (push 3) → (push 1) → 2 → 3 (already visited) → (push 2) → (push 0)
Stack: [3, 1, 2, 0]  → reversed: [0, 2, 1, 3]
```

<details><summary>💡 Hint</summary>

In DFS topological sort, a node is added to the result AFTER all of its descendants are processed. Track three states: 0 (unvisited), 1 (in progress — on current DFS stack), 2 (fully done). A back edge to a state-1 node means a cycle.

</details>

<details>
<summary>✅ Answer</summary>

```python
def topological_sort_dfs(n, edges):
    """
    DFS-based topological sort.
    Returns order list, or [] if cycle detected.
    """
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)

    # 0 = unvisited, 1 = in-progress (on DFS stack), 2 = done
    state = [0] * n
    result = []
    has_cycle = [False]

    def dfs(u):
        state[u] = 1   # mark as in-progress
        for v in adj[u]:
            if state[v] == 1:
                has_cycle[0] = True   # back edge → cycle
                return
            if state[v] == 0:
                dfs(v)
                if has_cycle[0]:
                    return
        state[u] = 2
        result.append(u)   # add AFTER all descendants

    for i in range(n):
        if state[i] == 0:
            dfs(i)
            if has_cycle[0]:
                return []

    result.reverse()   # post-order gives reverse topo order
    return result

edges = [(0,1),(0,2),(1,3),(2,3)]
print(topological_sort_dfs(4, edges))   # [0, 2, 1, 3] or similar valid order
print(topological_sort_dfs(3, [(0,1),(1,2),(2,0)]))  # [] (cycle)
```

**Why post-order works:** A node is appended after all its successors are done. So in the reversed result, a node always precedes its successors — exactly the topological property. The three-state system catches back edges (in-progress → in-progress), which indicate cycles in directed graphs.

</details>

> 💻 Try it: [practice_local.py → Q9](./practice_local.py)

---

<a id="q10"></a>
### Q10 · Topological Sort — Course Schedule

🟡 Medium

**Problem:** You are given `numCourses` and a list of `prerequisites` where `prerequisites[i] = [a, b]` means you must take course `b` before course `a`. Return a valid course order, or `[]` if impossible.

This is LeetCode 210 — Course Schedule II.

<details><summary>💡 Hint</summary>

This is direct topological sort. Convert prerequisites to edges: `b → a` (b must come before a). Run Kahn's algorithm. If result length equals `numCourses`, return the order; otherwise there's a cycle and return `[]`.

</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import deque

def find_order(num_courses, prerequisites):
    """
    prerequisites[i] = [a, b] means: take b before a → edge b→a
    Returns valid order or [] if cycle.
    """
    adj = [[] for _ in range(num_courses)]
    in_degree = [0] * num_courses

    for a, b in prerequisites:
        adj[b].append(a)   # b must come before a
        in_degree[a] += 1

    queue = deque(i for i in range(num_courses) if in_degree[i] == 0)
    order = []

    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    return order if len(order) == num_courses else []

# Test
print(find_order(4, [[1,0],[2,0],[3,1],[3,2]]))  # [0, 1, 2, 3] or [0, 2, 1, 3]
print(find_order(2, [[1,0],[0,1]]))               # [] — mutual prerequisite = cycle
print(find_order(1, []))                           # [0]
```

**Why:** Recognizing "prerequisites" as directed edges is the key modeling step. The direction `b → a` (b unlocks a) makes the edge direction match the natural reading. Cycle = impossible course order. This exact pattern applies to build systems, task schedulers, and dependency managers.

</details>

> 💻 Try it: [practice_local.py → Q10](./practice_local.py)

---

<a id="q11"></a>
### Q11 · SCC — Kosaraju's Algorithm

🟡 Medium

**Problem:** Find all Strongly Connected Components (SCCs) in a directed graph using Kosaraju's algorithm.

```
Graph: 0→1, 1→2, 2→0, 2→3, 3→4, 4→5, 5→3
Expected SCCs: {0,1,2} and {3,4,5}
```

<details><summary>💡 Hint</summary>

Two DFS passes: (1) DFS on original graph, push nodes onto a stack by finish time. (2) Build reversed graph. (3) DFS on reversed graph in reverse finish order (pop from stack). Each DFS tree in pass 2 = one SCC.

</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import defaultdict

def kosaraju_scc(graph, n):
    """
    graph: dict {node: [neighbours]}
    Returns: list of SCCs (each SCC is a list of nodes)
    """
    visited = [False] * n
    finish_stack = []

    # Pass 1: DFS on original graph, record finish order
    def dfs1(u):
        visited[u] = True
        for v in graph.get(u, []):
            if not visited[v]:
                dfs1(v)
        finish_stack.append(u)   # push AFTER all neighbours done

    for i in range(n):
        if not visited[i]:
            dfs1(i)

    # Build reversed graph
    rev = defaultdict(list)
    for u in range(n):
        for v in graph.get(u, []):
            rev[v].append(u)

    # Pass 2: DFS on reversed graph in reverse finish order
    visited2 = [False] * n
    sccs = []

    def dfs2(u, component):
        visited2[u] = True
        component.append(u)
        for v in rev.get(u, []):
            if not visited2[v]:
                dfs2(v, component)

    while finish_stack:
        node = finish_stack.pop()
        if not visited2[node]:
            scc = []
            dfs2(node, scc)
            sccs.append(scc)

    return sccs

g = {0:[1], 1:[2], 2:[0,3], 3:[4], 4:[5], 5:[3]}
sccs = kosaraju_scc(g, 6)
print(sorted([sorted(s) for s in sccs]))  # [[0,1,2], [3,4,5]]
```

**Why the reversed graph:** In the original graph, "sink" SCCs finish DFS last. After reversing edges, these sink SCCs become sources — DFS from them stays within the SCC (can't escape to other components because reversed edges point the other way). This is the elegant insight of Kosaraju's.

</details>

> 💻 Try it: [practice_local.py → Q11](./practice_local.py)

---

<a id="q12"></a>
### Q12 · SCC — Count Strongly Connected Components

🟡 Medium

**Problem:** Given a directed graph, count how many strongly connected components it has. A single node with no self-loop counts as one SCC.

<details><summary>💡 Hint</summary>

Run Kosaraju's (or Tarjan's) and count the resulting list length. A graph that is itself strongly connected has exactly 1 SCC. A DAG with no cycles has exactly V SCCs (each node is its own SCC).

</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import defaultdict

def count_sccs(n, edges):
    """
    edges: list of (u, v) directed edges
    Returns: number of SCCs
    """
    adj = defaultdict(list)
    radj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        radj[v].append(u)

    visited = [False] * n
    finish_order = []

    def dfs1(u):
        visited[u] = True
        for v in adj[u]:
            if not visited[v]:
                dfs1(v)
        finish_order.append(u)

    for i in range(n):
        if not visited[i]:
            dfs1(i)

    visited2 = [False] * n
    count = 0

    def dfs2(u):
        visited2[u] = True
        for v in radj[u]:
            if not visited2[v]:
                dfs2(v)

    while finish_order:
        node = finish_order.pop()
        if not visited2[node]:
            dfs2(node)
            count += 1

    return count

# Fully strongly connected (1 SCC)
print(count_sccs(3, [(0,1),(1,2),(2,0)]))      # 1
# Pure DAG (3 SCCs — each node is its own)
print(count_sccs(3, [(0,1),(1,2)]))             # 3
# Two separate SCCs
print(count_sccs(6, [(0,1),(1,2),(2,0),(3,4),(4,5),(5,3)]))  # 2
```

**Why:** The number of SCCs equals the number of separate "mutual reachability clusters." A DAG has the maximum possible SCCs (every node is isolated). Counting SCCs is the first step in condensation — converting a graph into its high-level DAG structure.

</details>

> 💻 Try it: [practice_local.py → Q12](./practice_local.py)

---

<a id="q13"></a>
### Q13 · SCC — Condensation Graph

🟡 Medium

**Problem:** After finding SCCs, build the "condensation graph" — contract each SCC into a single super-node. The result is always a DAG. Why?

Describe the algorithm and write code that returns the condensation's edges.

<details><summary>💡 Hint</summary>

Assign each node an SCC ID (which SCC it belongs to). For every original edge `u → v`, if `scc_id[u] != scc_id[v]`, add edge `scc_id[u] → scc_id[v]` to the condensation. Use a set to avoid duplicate edges.

</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import defaultdict

def condensation_graph(n, edges):
    """
    Returns (num_sccs, condensation_edges_set).
    Condensation is always a DAG.
    """
    adj = defaultdict(list)
    radj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        radj[v].append(u)

    # Kosaraju pass 1
    visited = [False] * n
    finish_order = []

    def dfs1(u):
        visited[u] = True
        for v in adj[u]:
            if not visited[v]:
                dfs1(v)
        finish_order.append(u)

    for i in range(n):
        if not visited[i]:
            dfs1(i)

    # Kosaraju pass 2 — assign SCC IDs
    scc_id = [-1] * n
    scc_count = 0
    visited2 = [False] * n

    def dfs2(u, sid):
        visited2[u] = True
        scc_id[u] = sid
        for v in radj[u]:
            if not visited2[v]:
                dfs2(v, sid)

    while finish_order:
        node = finish_order.pop()
        if not visited2[node]:
            dfs2(node, scc_count)
            scc_count += 1

    # Build condensation edges (deduplicated)
    cond_edges = set()
    for u, v in edges:
        if scc_id[u] != scc_id[v]:
            cond_edges.add((scc_id[u], scc_id[v]))

    return scc_count, cond_edges

n_scc, cond = condensation_graph(6, [(0,1),(1,2),(2,0),(2,3),(3,4),(4,5),(5,3)])
print(n_scc, cond)   # 2, {(0, 1)} — SCC0 connects to SCC1
```

**Why it's always a DAG:** If the condensation had a cycle between two SCCs, all nodes in those SCCs could reach each other — they would be the same SCC. By definition, no cycle can exist between different SCCs.

</details>

> 💻 Try it: [practice_local.py → Q13](./practice_local.py)

---

<a id="q14"></a>
### Q14 · Kruskal's MST — Minimum Spanning Tree Weight

🟡 Medium

**Problem:** Given an undirected weighted graph, find the minimum spanning tree using Kruskal's algorithm. Return the total weight and the list of MST edges.

```
5 nodes, edges: (0-1,w=1), (1-3,w=2), (0-2,w=4), (1-2,w=3), (2-3,w=5)
Expected MST weight: 6  (edges: 0-1, 1-3, 1-2)
```

<details><summary>💡 Hint</summary>

Sort edges by weight ascending. For each edge, use Union-Find to check if adding it would create a cycle (both endpoints already in same component). If not, add it to the MST. Stop when you have V-1 edges.

</details>

<details>
<summary>✅ Answer</summary>

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])   # path compression
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False   # same component — would create cycle
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True

def kruskal_mst(n, edges):
    """
    edges: list of (weight, u, v)
    Returns (total_weight, mst_edges)
    """
    uf = UnionFind(n)
    mst_weight = 0
    mst_edges = []

    for weight, u, v in sorted(edges):
        if uf.union(u, v):
            mst_weight += weight
            mst_edges.append((weight, u, v))
            if len(mst_edges) == n - 1:
                break   # MST complete

    return mst_weight, mst_edges

edges = [(1,0,1),(2,1,3),(4,0,2),(3,1,2),(5,2,3)]
w, mst = kruskal_mst(4, edges)
print(w, mst)   # 6, [(1,0,1),(2,1,3),(3,1,2)]
```

**Why:** Kruskal's greedy argument: the globally cheapest edge that doesn't form a cycle must be in the MST. Union-Find makes the "does this form a cycle?" check O(α(n)) ≈ O(1). Total: O(E log E) dominated by sorting.

</details>

> 💻 Try it: [practice_local.py → Q14](./practice_local.py)

---

<a id="q15"></a>
### Q15 · Prim's MST — Minimum Spanning Tree Weight

🟡 Medium

**Problem:** Given a dense undirected weighted graph as an adjacency list, find the MST weight using Prim's algorithm (node-centric approach).

<details><summary>💡 Hint</summary>

Start from node 0. Use a min-heap of `(weight, node)` for unvisited nodes. Pop the cheapest, add its cost to MST, then push all its unvisited neighbors. Skip nodes already in the MST — they're stale heap entries.

</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

def prim_mst(graph, n):
    """
    graph: dict {node: [(neighbour, weight), ...]}
    Returns (total_weight, mst_edges)
    """
    in_mst = [False] * n
    parent = [-1] * n
    heap = [(0, 0)]   # (cost, node) — start at node 0
    total_weight = 0
    mst_edges = []

    while heap:
        cost, u = heapq.heappop(heap)
        if in_mst[u]:
            continue   # stale entry
        in_mst[u] = True
        total_weight += cost
        if parent[u] != -1:
            mst_edges.append((cost, parent[u], u))

        for v, weight in graph.get(u, []):
            if not in_mst[v]:
                parent[v] = u
                heapq.heappush(heap, (weight, v))

    return total_weight, mst_edges

g = {
    0: [(1,2),(3,6)],
    1: [(0,2),(2,3),(3,8),(4,5)],
    2: [(1,3),(4,7)],
    3: [(0,6),(1,8),(4,9)],
    4: [(1,5),(2,7),(3,9)],
}
w, edges = prim_mst(g, 5)
print(w, edges)   # 16, edges forming the MST
```

**Why:** Prim's grows the MST one node at a time. At each step, it greedily picks the cheapest edge that connects a new node to the existing tree. The min-heap ensures this is efficient: O(E log V). For dense graphs (E ≈ V²), Prim's with an array instead of heap runs in O(V²), which beats Kruskal's O(E log E) = O(V² log V).

</details>

> 💻 Try it: [practice_local.py → Q15](./practice_local.py)

---

<a id="q16"></a>
### Q16 · MST — Kruskal vs Prim Decision

🟡 Medium

**Problem:** For each scenario below, state which MST algorithm is better and why:

1. A road network with 1,000 cities and 2,000 roads (sparse: E ≈ 2V)
2. A network with 500 cities and 120,000 roads (dense: E ≈ V²/2)
3. You already have all edges sorted by weight
4. You need to add one new city at a time and update the MST incrementally

<details><summary>💡 Hint</summary>

Kruskal's is O(E log E) — the sort dominates. Prim's (with heap) is O(E log V). For sparse graphs E is small, making Kruskal's sort cheap. For dense graphs, Prim's with a simple array runs in O(V²), matching the number of edges.

</details>

<details>
<summary>✅ Answer</summary>

```
1. Sparse (E ≈ 2V = 2000 edges):
   → Kruskal's wins
   Sorting 2000 edges is O(2000 × log 2000) ≈ fast
   Union-Find operations: nearly O(1) each

2. Dense (E ≈ 120,000 edges):
   → Prim's wins (with simple array, not heap)
   Prim's array version: O(V²) = 250,000 ops
   Kruskal's: O(E log E) = O(120,000 × 17) = 2,040,000 ops

3. Pre-sorted edges:
   → Kruskal's wins (sort step already done)
   Just iterate edges and union-find: O(E × α(V))

4. Incremental MST (add new cities one by one):
   → Prim's wins
   Prim's naturally grows from the existing tree — adding a new
   node means pushing its edges onto the heap. Kruskal's would
   need to re-sort all edges including the new ones.
```

**Summary rule:**
- Sparse graph → Kruskal (sort is cheap, DSU is near O(1))
- Dense graph → Prim with array (O(V²) matches the edge count)
- Prim with heap → general-purpose O(E log V), good default

</details>

> 💻 Try it: [practice_local.py → Q16](./practice_local.py)

---

<a id="q17"></a>
### Q17 · Network Flow — Max Flow via Edmonds-Karp

🟠 Hard

**Problem:** Implement Edmonds-Karp (BFS-based Ford-Fulkerson) to find the maximum flow from source to sink in a flow network. Return the maximum flow value.

```
Nodes: 0=source, 5=sink
Capacities (n×n matrix given in code below)
Expected max flow: 23
```

<details><summary>💡 Hint</summary>

Maintain a residual capacity matrix. Repeatedly find an augmenting path from source to sink using BFS (ensures shortest augmenting path, which is key to Edmonds-Karp's polynomial bound). For each path, find the bottleneck (minimum residual capacity), then update: reduce forward edge, increase backward edge (to allow "undoing" flow).

</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import deque

def edmonds_karp(n, source, sink, capacities):
    """
    n: number of nodes
    capacities: n×n matrix, capacities[u][v] = capacity of edge u→v
    Returns: maximum flow from source to sink
    """
    residual = [row[:] for row in capacities]   # deep copy

    def bfs_find_path():
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
        return None

    max_flow = 0

    while True:
        parent = bfs_find_path()
        if parent is None:
            break   # no more augmenting paths

        # Find bottleneck capacity along the path
        path_flow = float('inf')
        v = sink
        while v != source:
            u = parent[v]
            path_flow = min(path_flow, residual[u][v])
            v = u

        # Update residual capacities
        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= path_flow   # reduce forward
            residual[v][u] += path_flow   # increase backward (undo option)
            v = u

        max_flow += path_flow

    return max_flow

cap = [
    [0, 16, 13,  0,  0,  0],
    [0,  0,  4, 12,  0,  0],
    [0,  0,  0,  0, 14,  0],
    [0,  0,  9,  0,  0, 20],
    [0,  0,  0,  7,  0,  4],
    [0,  0,  0,  0,  0,  0],
]
print(edmonds_karp(6, 0, 5, cap))   # 23
```

**Why backward edges:** The backward edge allows the algorithm to "undo" a previous routing decision. Without it, the first set of augmenting paths might block a globally optimal solution. The backward edge of capacity f means "you can push up to f units back through this edge," effectively canceling previous flow.

</details>

> 💻 Try it: [practice_local.py → Q17](./practice_local.py)

---

<a id="q18"></a>
### Q18 · Network Flow — Bipartite Matching via Max Flow

🟠 Hard

**Problem:** You have N students and M projects. Each student lists projects they're willing to work on. At most one student per project. Find the maximum number of student-project assignments.

Model this as a max-flow problem and solve it.

```
Students: 0, 1, 2
Projects: 3, 4, 5
Student 0 → can do projects 3, 4
Student 1 → can do projects 4, 5
Student 2 → can do projects 3, 5
Expected max matching: 3 (all students assigned)
```

<details><summary>💡 Hint</summary>

Add a super-source (node n_students + n_projects) connected to every student with capacity 1. Add a super-sink connected from every project with capacity 1. Student-project edges have capacity 1. Max flow = max matching.

</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import deque

def bipartite_matching(n_students, n_projects, willing):
    """
    willing: list of (student, project) pairs
    Returns maximum matching count.
    """
    # Node layout:
    #   source = 0
    #   students = 1 to n_students
    #   projects = n_students+1 to n_students+n_projects
    #   sink = n_students + n_projects + 1

    total = n_students + n_projects + 2
    source = 0
    sink = total - 1

    cap = [[0] * total for _ in range(total)]

    # Source → each student (capacity 1)
    for s in range(n_students):
        cap[source][s + 1] = 1

    # Each project → sink (capacity 1)
    for p in range(n_projects):
        cap[n_students + 1 + p][sink] = 1

    # Student → project edges (capacity 1)
    for student, project in willing:
        cap[student + 1][n_students + 1 + project] = 1

    # Edmonds-Karp
    def bfs():
        visited = [False] * total
        visited[source] = True
        parent = [-1] * total
        queue = deque([source])
        while queue:
            u = queue.popleft()
            if u == sink:
                return parent
            for v in range(total):
                if not visited[v] and cap[u][v] > 0:
                    visited[v] = True
                    parent[v] = u
                    queue.append(v)
        return None

    max_match = 0
    while True:
        parent = bfs()
        if parent is None:
            break
        path_flow = float('inf')
        v = sink
        while v != source:
            u = parent[v]
            path_flow = min(path_flow, cap[u][v])
            v = u
        v = sink
        while v != source:
            u = parent[v]
            cap[u][v] -= path_flow
            cap[v][u] += path_flow
            v = u
        max_match += path_flow

    return max_match

willing = [(0,0),(0,1),(1,1),(1,2),(2,0),(2,2)]
print(bipartite_matching(3, 3, willing))   # 3 — all students assigned
```

**Why this works (max-flow = max-matching):** Each unit of flow represents one assignment. The source ensures each student is assigned at most once (capacity 1 to each student). The sink ensures each project gets at most one student (capacity 1 from each project). The max flow algorithm finds the maximum number of disjoint augmenting paths = maximum matching.

</details>

> 💻 Try it: [practice_local.py → Q18](./practice_local.py)

---

<a id="q19"></a>
### Q19 · Floyd-Warshall — Negative Cycle Detection via Diagonal

🟠 Hard

**Problem:** After running Floyd-Warshall, how do you detect if the graph contains a negative cycle? What does `dist[i][i] < 0` mean?

Given this graph: edges `(0→1, w=-1), (1→0, w=-1)`. Detect the negative cycle.

<details><summary>💡 Hint</summary>

`dist[i][i]` is initialized to 0 (distance from a node to itself). A negative cycle reachable from node i can eventually be used to create a path that returns to i with negative total cost, making `dist[i][i] < 0`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def floyd_warshall_with_neg_cycle(n, edges):
    """
    Returns (dist, has_negative_cycle).
    """
    INF = float('inf')
    dist = [[INF] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = min(dist[u][v], w)

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] != INF and dist[k][j] != INF:
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

    # If dist[i][i] < 0, node i is on a negative cycle
    has_neg_cycle = any(dist[i][i] < 0 for i in range(n))
    neg_cycle_nodes = [i for i in range(n) if dist[i][i] < 0]

    return dist, has_neg_cycle, neg_cycle_nodes

# Negative cycle: 0→1 (-1) and 1→0 (-1), total cycle = -2
dist, has_neg, nodes = floyd_warshall_with_neg_cycle(2, [(0,1,-1),(1,0,-1)])
print(has_neg)    # True
print(nodes)      # [0, 1] — both on the cycle

# No negative cycle
dist2, has_neg2, _ = floyd_warshall_with_neg_cycle(3, [(0,1,1),(1,2,2),(2,0,3)])
print(has_neg2)   # False (cycle 0→1→2→0 has weight 1+2+3=6 > 0)
```

**Why dist[i][i] works:** Initially 0. After Floyd-Warshall, `dist[i][i]` = shortest "round trip" from i to i. If a negative cycle exists on any path from i back to i, that cycle can be traversed to give a cost less than 0. This is the simplest negative cycle detection in all-pairs algorithms — O(V) check after O(V³) computation.

</details>

> 💻 Try it: [practice_local.py → Q19](./practice_local.py)

---

<a id="q20"></a>
### Q20 · Floyd-Warshall — Transitive Closure

🟠 Hard

**Problem:** Given a directed graph, determine for every pair (i, j) whether node i can reach node j. Return a boolean matrix `reachable[i][j]`.

This is called **transitive closure** — it answers "can i get to j by any path?"

<details><summary>💡 Hint</summary>

Replace Floyd-Warshall's `min(dist[i][j], dist[i][k] + dist[k][j])` with `reachable[i][j] or (reachable[i][k] and reachable[k][j])`. Initialize direct edges as True and self-loops as True.

</details>

<details>
<summary>✅ Answer</summary>

```python
def transitive_closure(n, edges):
    """
    Returns reachable[i][j] = True if node i can reach node j.
    """
    reach = [[False] * n for _ in range(n)]

    # Self-reachability
    for i in range(n):
        reach[i][i] = True

    # Direct edges
    for u, v in edges:
        reach[u][v] = True

    # Floyd-Warshall with boolean logic
    for k in range(n):
        for i in range(n):
            for j in range(n):
                reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])

    return reach

# Graph: 0→1, 1→2, 2→3 (linear chain)
r = transitive_closure(4, [(0,1),(1,2),(2,3)])
print(r[0][3])   # True  (0 can reach 3 via chain)
print(r[3][0])   # False (no reverse edges)
print(r[1][3])   # True  (1→2→3)

# Graph with cycle: 0→1, 1→2, 2→0
r2 = transitive_closure(3, [(0,1),(1,2),(2,0)])
print(r2[2][0])  # True (2→0)
print(r2[0][2])  # True (0→1→2)
print(all(r2[i][j] for i in range(3) for j in range(3)))  # True — all reachable
```

**Why:** Transitive closure is Floyd-Warshall with `or` and `and` instead of `min` and `+`. It's used for: access control (can user X access resource Y?), dependency analysis (does package A depend on B, transitively?), and reachability queries in compiler flow analysis.

</details>

> 💻 Try it: [practice_local.py → Q20](./practice_local.py)

---

<a id="q21"></a>
### Q21 · Algorithm Selection — Choose the Right Algorithm

🟠 Hard

**Problem:** For each scenario, choose the correct algorithm and justify why the alternatives fail:

1. Single-source shortest path, all weights ≥ 0, dense graph
2. Single-source shortest path, some weights < 0, detect negative cycle
3. All-pairs shortest path, V = 200 nodes
4. Task scheduling with dependencies, detect impossible schedule
5. Connect N servers with minimum cable cost, sparse network
6. Maximum simultaneous data transfers in a network (source → sink)
7. Find groups of mutually-reachable web pages

<details><summary>💡 Hint</summary>

The key discriminators: (a) negative edges → rules out Dijkstra, (b) single vs all-pairs, (c) sparse vs dense → Kruskal vs Prim, (d) DAG ordering → topological sort, (e) mutual reachability → SCC.

</details>

<details>
<summary>✅ Answer</summary>

```
1. Single-source, non-negative weights, dense graph:
   → Dijkstra O((V+E) log V)
   Why not Bellman-Ford: O(VE) = O(V³) for dense, much slower
   Why not Floyd-Warshall: O(V³), but gives all-pairs (wasteful for single-source)

2. Single-source, negative weights, detect negative cycle:
   → Bellman-Ford O(VE)
   Why not Dijkstra: FAILS with negative edges (greedy invariant breaks)
   Why not Floyd-Warshall: correct but O(V³), overkill for single-source

3. All-pairs shortest path, V = 200:
   → Floyd-Warshall O(V³) = 8,000,000 ops — feasible
   Alternative: run Dijkstra V times = O(V × (V+E) log V), often slower for small V
   Note: V > ~500-1000, prefer repeated Dijkstra (Floyd's V³ becomes too large)

4. Task scheduling, detect impossible schedule:
   → Topological Sort (Kahn's) O(V+E)
   If result length < V → cycle exists → impossible
   Why not DFS cycle detection: Kahn's gives the ordering AND cycle detection in one pass

5. Connect N servers, sparse (E ~ V or 2V):
   → Kruskal's MST O(E log E) — sorting few edges is cheap
   Why not Prim's: similar complexity but Kruskal's is simpler to implement for sparse

6. Maximum data transfers (source → sink):
   → Edmonds-Karp (BFS-based max flow) O(VE²)
   Why not Dijkstra/Bellman-Ford: shortest path ≠ max flow (different problems)

7. Groups of mutually-reachable web pages:
   → Kosaraju's / Tarjan's SCC O(V+E)
   Why not BFS/DFS: BFS finds what's reachable FROM one node, not mutual reachability
   Why not Union-Find: doesn't handle direction (undirected only)
```

</details>

> 💻 Try it: [practice_local.py → Q21](./practice_local.py)

---

<a id="q22"></a>
### Q22 · Dijkstra — Stale Entry Bug and Fix

🟠 Hard

**Problem:** Explain the "stale entry" problem in Dijkstra's priority queue. Write both the buggy version and the correct version. What is the performance impact of not handling stale entries?

<details><summary>💡 Hint</summary>

Python's `heapq` doesn't support updating priorities. When you find a shorter path to a node that's already in the heap, you push a new entry — the old one becomes "stale." Without the stale check, you process the node multiple times.

</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

# WRONG: no stale check — processes every heap entry
def dijkstra_wrong(graph, n, src):
    dist = [float('inf')] * n
    dist[src] = 0
    heap = [(0, src)]

    while heap:
        d, u = heapq.heappop(heap)
        # BUG: d might be > dist[u] (stale)
        # Re-processes u and re-relaxes all neighbors — wasted work
        for v, w in graph.get(u, []):
            if d + w < dist[v]:        # BUG: using stale d
                dist[v] = d + w
                heapq.heappush(heap, (dist[v], v))
    return dist

# CORRECT: skip stale entries
def dijkstra_correct(graph, n, src):
    dist = [float('inf')] * n
    dist[src] = 0
    heap = [(0, src)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue   # stale — a shorter path to u was already found
        for v, w in graph.get(u, []):
            new_dist = dist[u] + w     # use current best, not stale d
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))
    return dist

# Performance impact:
# Without stale check:
#   Heap can grow to O(E) entries (one per relaxation)
#   Each entry processed: O(log E) = O(log(V²)) = O(log V) work
#   But the SAME node may be re-processed O(degree) times
#   Worst case: O(E log E) which can be O(V² log V) for dense graphs
#
# With stale check:
#   Each NODE processed at most once (after that, d > dist[u] is always true)
#   True complexity: O((V + E) log V)

g = {0: [(1,10),(2,3)], 1: [(3,2)], 2: [(1,4),(3,8)], 3: []}
print(dijkstra_correct(g, 4, 0))   # [0, 7, 3, 9]
```

**Why this matters in interviews:** Many candidates write Dijkstra without the stale check. It often still produces correct results (the later, stale updates don't actually improve any distances), but the complexity degrades from O((V+E) log V) to potentially O(E log E) or worse. Knowing this detail separates senior candidates.

</details>

> 💻 Try it: [practice_local.py → Q22](./practice_local.py)

---

<a id="q23"></a>
### Q23 · Bellman-Ford — Mark All Nodes on Negative Cycles

🟠 Hard

**Problem:** Extend Bellman-Ford to not just detect negative cycles, but mark ALL nodes reachable through a negative cycle with distance `-inf`. This is useful in problems like "find all arbitrage opportunities" in currency exchange.

<details><summary>💡 Hint</summary>

Run V-1 passes to find shortest paths, then run V more passes. In the extra V passes, any node whose distance decreases is either on a negative cycle or reachable from one. Set those distances to `-inf` to propagate the effect.

</details>

<details>
<summary>✅ Answer</summary>

```python
def bellman_ford_mark_neg_cycles(n, edges, source):
    """
    Returns dist array where:
    - dist[v] = shortest distance (finite)
    - dist[v] = float('inf') if unreachable
    - dist[v] = float('-inf') if reachable via a negative cycle
    """
    dist = [float('inf')] * n
    dist[source] = 0

    # Standard V-1 passes
    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w

    # V more passes: propagate -inf through negative cycles
    for _ in range(n):
        for u, v, w in edges:
            # If this edge can still be relaxed, v is on or reachable from a neg cycle
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = float('-inf')

    return dist

# Test: cycle 0→1→2→0 with total weight -1, and node 3 reachable from it
edges = [(0,1,1),(1,2,-3),(2,0,1),(2,3,5)]
dist = bellman_ford_mark_neg_cycles(4, edges, 0)
print(dist)
# All 4 nodes are -inf: 0,1,2 are on the cycle, 3 is reachable from it

# Test: separate positive and negative paths
edges2 = [(0,1,1),(0,2,2),(1,3,-5),(3,1,4)]   # cycle 1→3→1, weight -1
dist2 = bellman_ford_mark_neg_cycles(4, edges2, 0)
print(dist2)
# dist2[1] and dist2[3] = -inf (on cycle), dist2[0] = 0 (source, not on cycle)
```

**Why propagate V more passes:** After V-1 passes, any node that can still be relaxed is on a negative cycle. But nodes REACHABLE from a negative cycle also have -inf distances (you can approach them through the cycle for arbitrarily small costs). The V extra passes ensure this -inf propagates through all reachable nodes.

</details>

> 💻 Try it: [practice_local.py → Q23](./practice_local.py)

---

<a id="q24"></a>
### Q24 · Bipartite Checking via BFS 2-Coloring

🟠 Hard

**Problem:** Given an undirected graph, determine if it is bipartite. A graph is bipartite if its nodes can be colored with 2 colors such that no two adjacent nodes have the same color.

```
Bipartite:     0 - 1 - 2 - 3 (alternating: R-B-R-B)
Not bipartite: 0 - 1 - 2 - 0 (triangle: impossible to 2-color)
```

<details><summary>💡 Hint</summary>

BFS 2-coloring: assign color 0 to source, then alternate colors for neighbors. If you ever try to assign a color to a node that already has the same color as the current node, the graph is not bipartite. Handle disconnected graphs by starting BFS from every unvisited node.

</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import deque

def is_bipartite(n, edges):
    """
    Returns True if graph is bipartite.
    Uses BFS 2-coloring (handles disconnected graphs).
    """
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)   # undirected — both directions

    color = [-1] * n   # -1 = unvisited, 0 or 1 = color

    for start in range(n):
        if color[start] != -1:
            continue   # already colored in a previous component

        color[start] = 0
        queue = deque([start])

        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if color[v] == -1:
                    color[v] = 1 - color[u]   # opposite color
                    queue.append(v)
                elif color[v] == color[u]:
                    return False   # same color = not bipartite

    return True

# Bipartite: even cycle
print(is_bipartite(4, [(0,1),(1,2),(2,3),(3,0)]))   # True (square)
# Bipartite: simple path
print(is_bipartite(4, [(0,1),(1,2),(2,3)]))           # True
# Not bipartite: odd cycle (triangle)
print(is_bipartite(3, [(0,1),(1,2),(2,0)]))           # False
# Not bipartite: odd cycle of length 5
print(is_bipartite(5, [(0,1),(1,2),(2,3),(3,4),(4,0)]))  # False
```

**Why bipartite matters:** Bipartite graphs model two-sided matching problems (students/projects, users/items). If a graph is bipartite, max matching via network flow is valid. Odd cycles make 2-coloring impossible — the key insight is that ALL odd cycles make a graph non-bipartite, and ALL even cycles preserve bipartiteness.

</details>

> 💻 Try it: [practice_local.py → Q24](./practice_local.py)

---

<a id="q25"></a>
### Q25 · Directed Cycle Detection — DFS WHITE/GRAY/BLACK

🟠 Hard

**Problem:** Detect whether a directed graph has a cycle using DFS with 3-color node marking. Why does Union-Find fail for directed graphs?

```
Directed graph: 0→1, 1→2, 0→2 (DAG — no cycle)
Cycle graph:    0→1, 1→2, 2→0 (cycle!)

Union-Find on "0→1, 1→2, 0→2":
  Union(0,1): OK. Union(1,2): OK. Union(0,2): same set! Reports CYCLE.
  BUT this is a DAG with no cycle — false positive!
```

<details><summary>💡 Hint</summary>

Track three states: WHITE (unvisited), GRAY (currently on the DFS call stack), BLACK (fully processed). A back edge — an edge to a GRAY node — means a cycle. An edge to a BLACK node is a cross/forward edge (no cycle). Outer loop over all nodes handles disconnected graphs.

</details>

<details>
<summary>✅ Answer</summary>

```python
def has_cycle_directed_dfs(n, edges):
    """
    Directed cycle detection via DFS WHITE/GRAY/BLACK coloring.
    Returns True if cycle exists.
    """
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)

    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n

    def dfs(u):
        color[u] = GRAY   # entering DFS subtree rooted at u

        for v in adj[u]:
            if color[v] == GRAY:
                return True   # back edge → cycle in directed graph
            if color[v] == WHITE:
                if dfs(v):
                    return True

        color[u] = BLACK   # fully processed — no cycle through u
        return False

    for i in range(n):
        if color[i] == WHITE:
            if dfs(i):
                return True

    return False

# Why Union-Find gives false positive on DAG:
#   0→1, 1→2, 0→2
#   UF merges 0+1, then 1+2 (now all in same set), then 0+2 → same set = "cycle"
#   But 0→2 is just two paths to 2, not a cycle. UF can't tell direction.

print(has_cycle_directed_dfs(3, [(0,1),(1,2),(0,2)]))  # False — DAG, no cycle
print(has_cycle_directed_dfs(3, [(0,1),(1,2),(2,0)]))  # True  — 0→1→2→0 cycle
print(has_cycle_directed_dfs(5, [(0,1),(1,2),(2,3),(3,1),(0,4)]))  # True (1→2→3→1)

# Union-Find DOES work correctly for undirected graphs:
#   undirected 0-1-2-0: UF(0,1), UF(1,2), UF(0,2) → same component → cycle (correct!)
#   undirected 0-1, 1-2, 0-2: same thing but it IS a cycle in undirected sense
```

**Why three colors:** GRAY marks "currently on the DFS path." An edge to a GRAY node means "we're still exploring this ancestor" — that's the defining characteristic of a cycle in a directed graph. BLACK means "explored and done" — edges to BLACK nodes are cross/forward edges and don't indicate cycles. Two colors (visited/unvisited) can't distinguish these two cases.

</details>

> 💻 Try it: [practice_local.py → Q25](./practice_local.py)

---

**[⬅️ Theory](./theory.md)** · **[💻 Local Practice](./practice_local.py)**

**Prev:** [← 24_disjoint_set_union](../24_disjoint_set_union/practice.md) | **Next:** [26_system_design_patterns →](../26_system_design_patterns/caching_strategies.md)
