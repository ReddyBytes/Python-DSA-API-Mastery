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

# 🔁 Navigation

Previous:  
[17_trie/interview.md](/dsa-complete-mastery/17_trie/interview.md)

Next:  
[18_graphs/interview.md](/dsa-complete-mastery/18_graphs/interview.md)  
[19_greedy/theory.md](/dsa-complete-mastery/19_greedy/theory.md)

