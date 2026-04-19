# 📘 Graphs — The World of Connections

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

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
graph representation (adjacency list vs matrix) · BFS · DFS · time complexity

**Should Learn** — Important for real projects, comes up regularly:
topological sort · cycle detection · connected components

**Good to Know** — Useful in specific situations, not always tested:
shortest path unweighted · directed vs undirected implications

**Reference** — Know it exists, look up syntax when needed:
Dijkstra · Bellman-Ford · MST (covered in 25_advanced_graphs)

---

# 🌍 1️⃣ Real Life Story — City Map

Imagine a city.

Intersections = Nodes  
Roads = Edges  

You can travel from one intersection to another.

That structure is a graph.

---

# 🧩 2️⃣ What Is a Graph?

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

---

# 🔄 3️⃣ Types of Graphs

---

## 🔹 Undirected Graph

Edges have no direction.

```
A -- B
```

Travel both ways.

Example:
Friendship.

---

## 🔹 Directed Graph (Digraph)

Edges have direction.

```
A → B
```

One-way.

Example:
Twitter follow.

---

## 🔹 Weighted Graph

Edges have weight (cost).

Example:
Distance between cities.

---

## 🔹 Unweighted Graph

Edges just represent connection.

---

# 📦 4️⃣ Graph Representation

Two main ways:

---

## 🔹 Adjacency List

Store neighbors for each node.

Example:

```
A: B, C
B: A, D
C: A, D
D: B, C
```

Efficient for sparse graphs.

---

## 🔹 Adjacency Matrix

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

---

# 🔍 5️⃣ Graph Traversal

We need ways to explore graph.

Two fundamental methods:

- BFS (Breadth-First Search)
- DFS (Depth-First Search)

These are foundation.

---

# 🌊 6️⃣ BFS — Level by Level

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

---

# 🌲 7️⃣ DFS — Go Deep First

Go as deep as possible before backtracking.

Uses recursion or stack.

DFS order:
A, B, D, C

DFS explores path fully before exploring sibling.

---

# 🧠 8️⃣ When to Use BFS vs DFS

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

---

# 🔄 9️⃣ Cycle Detection

In Undirected Graph:
Use DFS and track parent.

In Directed Graph:
Use visited + recursion stack.

Important interview pattern.

---

# 🧱 1️⃣0️⃣ Connected Components

How many isolated groups exist?

Example:

```
A-B   C-D   E
```

Three components.

Use DFS/BFS.

Count components.

---

# 🛣 1️⃣1️⃣ Shortest Path (Unweighted)

Use BFS.

Because BFS explores level by level.

First time reaching node gives shortest distance.

---

# 📏 1️⃣2️⃣ Shortest Path (Weighted)

Cannot use BFS.

Use:

- Dijkstra (non-negative weights)
- Bellman-Ford (negative weights)

Heaps come into play here.

---

# 🌍 1️⃣3️⃣ Real-World Applications

- Google Maps
- Facebook friend suggestions
- Network routing
- Flight booking systems
- Web crawling
- Dependency resolution
- Recommendation systems

Graphs power the internet.

---

# ⚠️ 1️⃣4️⃣ Common Mistakes

- Not marking visited
- Infinite loops in cycle
- Forgetting directed vs undirected difference
- Wrong graph representation
- Stack overflow in DFS (deep recursion)

Graphs require careful tracking.

---

# 🧠 1️⃣5️⃣ Mental Model

Think of graph as:

A network of roads.

Traversal = exploring roads.

Nodes can connect in complex ways.

Unlike trees:
Graphs can have cycles.
Graphs can have multiple paths.

Graph thinking is about connectivity.

---

# 📌 Final Understanding

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

---

## 🔢 Topological Sort — Ordering Dependencies

> Think of course prerequisites: you must take Math 101 before Calculus, and Calculus before Differential Equations. Topological sort finds a valid ordering of tasks with dependencies.

**Topological sort** produces a linear ordering of vertices in a directed acyclic graph (DAG) such that for every edge u → v, u comes before v. It only works on DAGs — cycles make a valid ordering impossible.

**When to use:** Build systems, course scheduling, task pipelines, package dependency resolution.

### Kahn's Algorithm (BFS-based)

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

### DFS-based Topological Sort

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

---

# 🔁 Navigation

Previous:  
[17_trie/interview.md](/dsa-complete-mastery/17_trie/interview.md)

Next:  
[18_graphs/interview.md](/dsa-complete-mastery/18_graphs/interview.md)  
[19_greedy/theory.md](/dsa-complete-mastery/19_greedy/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Trie — Interview Q&A](../17_trie/interview.md) &nbsp;|&nbsp; **Next:** [Visual Explanation →](./visual_explanation.md)

**Related Topics:** [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
