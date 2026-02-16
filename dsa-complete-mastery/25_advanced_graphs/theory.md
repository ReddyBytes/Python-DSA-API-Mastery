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

# ⚖️ When to Use What?

| Problem Type | Algorithm |
|--------------|-----------|
| Task ordering | Topological sort |
| Detect strongly connected groups | SCC |
| Connect graph with minimal cost | MST |
| Maximize flow | Network flow |

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

