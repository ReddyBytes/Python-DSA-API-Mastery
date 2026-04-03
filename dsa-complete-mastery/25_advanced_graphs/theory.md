# 📘 Advanced Graph Algorithms — Mastering Complex Network Problems

> Basic graphs teach you traversal.
> Advanced graphs teach you structure, flow, and optimization.
>
> This is where interviews become serious.

Advanced graph algorithms are used in:

- Dependency resolution
- Task scheduling
- Network design
- Internet routing
- Resource allocation
- Distributed systems

We now explore the four major pillars:

1. Topological Sort
2. Strongly Connected Components (SCC)
3. Minimum Spanning Tree (MST)
4. Network Flow

---

# 🧭 1️⃣ Topological Sort — Ordering Dependencies

## 📖 Real Life Example

Imagine building software.

Tasks:

- Write code
- Compile
- Test
- Deploy

You cannot deploy before testing.

This forms a Directed Acyclic Graph (DAG).

Topological sort gives valid execution order.

---

## 🧠 Core Idea

Only works on:

Directed Acyclic Graph (DAG)

Produces linear ordering such that:

For every edge u → v,
u comes before v.

---

## 🛠 Two Ways to Implement

### 🔹 Kahn’s Algorithm (BFS + Indegree)

1. Calculate indegree of each node.
2. Add nodes with indegree 0 to queue.
3. Remove node, reduce neighbors’ indegree.
4. Repeat.

```python
from collections import deque

def topological_sort_kahn(graph, V):
    """
    graph: adjacency list  {node: [neighbors]}
    V: number of vertices
    Returns: topological order list, or [] if cycle detected
    """
    indegree = [0] * V
    for u in graph:
        for v in graph[u]:
            indegree[v] += 1

    queue = deque([i for i in range(V) if indegree[i] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph.get(node, []):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    # If not all nodes included → cycle exists
    return order if len(order) == V else []

# Example: compile A before B before C
# A→B, A→C, B→C
graph = {0: [1, 2], 1: [2], 2: []}
print(topological_sort_kahn(graph, 3))   # [0, 1, 2]
```

Time:
O(V + E)

---

### 🔹 DFS-Based Topological Sort

1. DFS traversal.
2. Push node to stack after exploring neighbors.
3. Reverse stack.

Also:
O(V + E)

---

## ⚠️ Detecting Cycle

If topological sort does not include all nodes,
cycle exists.

Very common interview test.

---

# 🔄 2️⃣ Strongly Connected Components (SCC)

## 📖 Real Life Example

Imagine cities where:

If you can travel from A to B,
and from B to A,
they form strong group.

SCC = maximal set of nodes reachable mutually.

---

## 🛠 Kosaraju’s Algorithm

Steps:

1. DFS and push nodes by finish time.
2. Reverse graph.
3. DFS in order of stack.

Time:
O(V + E)

---

## 🛠 Tarjan’s Algorithm

Single DFS traversal.
Uses:

- Discovery time
- Low link value
- Stack

More advanced.
Also O(V + E)

---

## 🧠 Where SCC Used

- Social network clustering
- Compiler optimizations
- Detecting cycles in directed graph
- Graph condensation

---

# 🌳 3️⃣ Minimum Spanning Tree (MST)

## 📖 Real Life Example

Connecting cities with minimum cable cost.

Want:

All cities connected
Minimum total cost

That is MST.

---

## 🛠 Kruskal’s Algorithm

1. Sort edges by weight.
2. Use DSU.
3. Add edge if no cycle.

Time:
O(E log E)

---

## 🛠 Prim’s Algorithm

1. Start from node.
2. Use min heap.
3. Pick smallest edge expanding tree.

Time:
O(E log V)

---

## 🧠 Difference

Kruskal:
Edge-based.

Prim:
Node-based.

Choose based on graph density.

---

# 🌊 4️⃣ Network Flow — Maximum Flow in Graph

## 📖 Real Life Example

Water flows through pipes.

Each pipe has capacity.

Goal:
Maximize water flow from source to sink.

---

## 🛠 Ford-Fulkerson Algorithm

Find augmenting path.
Increase flow.

Time:
Depends on implementation.

---

## 🛠 Edmonds-Karp

BFS-based Ford-Fulkerson.

Time:
O(VE²)

---

## 🛠 Dinic’s Algorithm

Optimized approach.

Time:
O(E√V) (for some cases)

Used in competitive programming.

---

## 🧠 Applications

- Maximum bipartite matching
- Airline scheduling
- Resource allocation
- Network bandwidth optimization

---

# 🛣️ 5️⃣ Shortest Path Algorithms

Dijkstra (covered in module 18) handles non-negative weights.
But what if edges have negative weights?
What if you need ALL pairs of shortest paths?

---

## Bellman-Ford — Shortest Path with Negative Weights

### The Problem Dijkstra Can't Solve

```
Graph:
  A ─(6)─→ B
  A ─(7)─→ C
  B ─(5)─→ C
  B ─(-4)→ D        ← negative edge!
  C ─(-3)→ B
  D ─(2)─→ A
```

Dijkstra fails here — it greedily picks the shortest path and never revises.
With negative edges, a longer path might become shorter after traversal.

---

### The Core Idea

Bellman-Ford relaxes ALL edges V-1 times.

Why V-1? The shortest path in a graph with V nodes can have at most V-1 edges.
After V-1 relaxations, all shortest paths are found.

```
Relaxation: if dist[u] + weight(u,v) < dist[v]:
                dist[v] = dist[u] + weight(u,v)
```

```
Example: A→B→C with weights [1, -2]
Start: dist = {A:0, B:inf, C:inf}

Pass 1 (relax all edges):
  Relax A→B: dist[B] = 0+1 = 1
  Relax B→C: dist[C] = 1+(-2) = -1

After V-1 passes: dist = {A:0, B:1, C:-1}
```

---

### Python Implementation

```python
def bellman_ford(graph, source, V):
    """
    graph: list of (u, v, weight) tuples
    source: starting node
    V: number of vertices
    Returns: dist dict, or None if negative cycle exists
    """
    dist = {i: float('inf') for i in range(V)}
    dist[source] = 0

    # Relax all edges V-1 times
    for _ in range(V - 1):
        for u, v, weight in graph:
            if dist[u] != float('inf') and dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight

    # V-th pass: if any edge can still be relaxed → negative cycle
    for u, v, weight in graph:
        if dist[u] != float('inf') and dist[u] + weight < dist[v]:
            return None   # negative cycle detected!

    return dist

# Example:
edges = [(0,1,6), (0,2,7), (1,2,8), (1,3,-4), (2,3,9), (2,4,-3), (3,0,2), (4,3,7)]
result = bellman_ford(edges, source=0, V=5)
```

---

### Detecting Negative Cycles

After V-1 passes, run one more pass. If any dist still decreases, a negative cycle exists.
(A negative cycle means "shortest path" = -∞ — you can loop forever decreasing distance.)

```
Negative cycle: A →(1)→ B →(-3)→ C →(1)→ A
  Sum of cycle = 1 + (-3) + 1 = -1 < 0
  You could loop this cycle forever to reach -∞ distance
```

---

### Bellman-Ford vs Dijkstra

```
┌─────────────────┬──────────────────────────┬──────────────────────────┐
│                 │  Dijkstra                │  Bellman-Ford            │
├─────────────────┼──────────────────────────┼──────────────────────────┤
│  Time           │  O((V + E) log V)        │  O(V × E)                │
│  Negative edges │  ✗ Fails                │  ✓ Handles               │
│  Negative cycle │  ✗ Can't detect         │  ✓ Detects               │
│  When to use    │  Non-negative weights    │  Negative weights/cycles  │
└─────────────────┴──────────────────────────┴──────────────────────────┘
```

---

## Floyd-Warshall — All-Pairs Shortest Path

### The Problem

Dijkstra and Bellman-Ford find shortest paths FROM one source.
Floyd-Warshall finds shortest paths BETWEEN ALL pairs of nodes simultaneously.

**Real-world use:** "What is the shortest route between EVERY city pair in a road network?"

---

### The Core Idea

Use dynamic programming with a 3D state:

```
dp[i][j][k] = shortest path from i to j using only nodes 0..k as intermediates
```

For each intermediate node k, check: is going through k shorter?

```
dp[i][j] = min(dp[i][j],  dp[i][k] + dp[k][j])
             direct path    go through k
```

```
Example (3 nodes: 0, 1, 2):

Initial distances (direct edges):
  0→1: 5    0→2: ∞
  1→0: ∞    1→2: 3
  2→0: 2    2→1: ∞

After k=0 (using node 0 as intermediate):
  dist[1][2]: min(∞, dist[1][0]+dist[0][2]) = min(∞, ∞) = ∞   (no change)
  dist[2][1]: min(∞, dist[2][0]+dist[0][1]) = min(∞, 2+5) = 7  ← improved!

After k=1 (using node 1 as intermediate):
  dist[0][2]: min(∞, dist[0][1]+dist[1][2]) = min(∞, 5+3) = 8  ← improved!

After k=2 (using node 2 as intermediate):
  dist[1][0]: min(∞, dist[1][2]+dist[2][0]) = min(∞, 3+2) = 5  ← improved!

Final: all-pairs shortest distances computed in O(V³)
```

---

### Python Implementation

```python
def floyd_warshall(n, edges):
    """
    n: number of nodes (0 to n-1)
    edges: list of (u, v, weight)
    Returns: dist[i][j] = shortest distance from i to j
             float('inf') = unreachable
    """
    INF = float('inf')
    dist = [[INF] * n for _ in range(n)]

    for i in range(n):
        dist[i][i] = 0              # distance to self = 0

    for u, v, weight in edges:
        dist[u][v] = weight         # direct edge

    # Relax through every intermediate node k
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    # Detect negative cycle: if dist[i][i] < 0 for any i
    for i in range(n):
        if dist[i][i] < 0:
            return None   # negative cycle!

    return dist

# Usage:
edges = [(0,1,5), (1,2,3), (2,0,2)]
result = floyd_warshall(3, edges)
# result[0][2] = 8  (0→1→2)
# result[2][1] = 7  (2→0→1)
```

---

### Floyd-Warshall vs Bellman-Ford

```
Use Floyd-Warshall when: all-pairs shortest path needed, V is small (V ≤ 500)
Use Bellman-Ford when:   single-source, negative edges, negative cycle detection
Time: Floyd = O(V³),  Bellman = O(VE)
```

---

# ⚖️ When to Use What?

| Problem Type                                | Algorithm              | Time         |
|---------------------------------------------|------------------------|--------------|
| Task ordering, dependency resolution        | Topological sort       | O(V + E)     |
| Detect strongly connected groups            | Kosaraju / Tarjan SCC  | O(V + E)     |
| Connect all nodes with minimum total cost   | Kruskal / Prim MST     | O(E log E)   |
| Maximum flow through a network              | Edmonds-Karp           | O(VE²)       |
| Single-source shortest path (no neg edges)  | Dijkstra               | O(E log V)   |
| Single-source shortest path (neg edges)     | Bellman-Ford           | O(V × E)     |
| Detect negative cycles                      | Bellman-Ford           | O(V × E)     |
| All-pairs shortest path                     | Floyd-Warshall         | O(V³)        |

Pattern recognition crucial.

---

# ⚠️ Common Mistakes

- Trying topological sort on cyclic graph
- Forgetting to reverse graph in Kosaraju
- Not using DSU correctly in Kruskal
- Forgetting capacity updates in flow
- Confusing MST with shortest path

Advanced graph problems require careful modeling.

---

# 🧠 Mental Model

Advanced graph algorithms solve:

Structure problems
Flow problems
Optimization problems

They are layered over basic BFS/DFS.

Without strong basics,
advanced graphs become confusing.

---

# 📌 Final Understanding

Advanced graph mastery means:

- Recognizing DAG vs cyclic graph
- Handling strongly connected components
- Designing minimum cost connectivity
- Managing flows efficiently
- Choosing correct algorithm for structure

These topics appear in:

- FAANG interviews
- System design discussions
- Competitive programming
- Network optimization roles

Advanced graph algorithms represent high-level algorithmic maturity.

---

# 🔁 Navigation

Previous:  
[24_disjoint_set_union/interview.md](/dsa-complete-mastery/24_disjoint_set_union/interview.md)

Next:  
[25_advanced_graphs/interview.md](/dsa-complete-mastery/25_advanced_graphs/interview.md)  
[26_system_design_patterns/theory.md](/dsa-complete-mastery/26_system_design_patterns/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Disjoint Set Union — Interview Q&A](../24_disjoint_set_union/interview.md) &nbsp;|&nbsp; **Next:** [Visual Explanation →](./visual_explanation.md)

**Related Topics:** [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
