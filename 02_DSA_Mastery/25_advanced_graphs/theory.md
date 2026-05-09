<a id="top"></a>
# Advanced Graph Algorithms — Mastering Complex Network Problems

> Meet **Pushpa** — a smuggler who navigates complex network routes through mountains.
> His world is a graph of hidden trails, border checkpoints, and river crossings.
> Every route has a cost. Every wrong turn means capture. Every decision matters.
>
> Basic graphs taught you how to walk through trails.
> Advanced graphs teach you how to find the cheapest path, the strongest alliances,
> the minimum infrastructure to connect all hideouts, and the maximum cargo flow.
>
> This is where Pushpa's survival depends on algorithmic mastery.

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

## 📖 Table of Contents

- [1. Topological Sort — Ordering Dependencies](#1-topological-sort)
  - [Real Life Example](#1-real-life)
  - [Visual: Course Prerequisites](#1-visual-prereqs)
  - [Core Idea](#1-core-idea)
  - [Kahn's Algorithm (BFS + Indegree)](#1-kahns)
  - [Visual: Kahn's Step-by-Step Trace](#1-kahns-trace)
  - [DFS-Based Topological Sort](#1-dfs-topo)
  - [Detecting Cycles](#1-cycles)
- [2. Strongly Connected Components (SCC)](#2-scc)
  - [Real Life Example](#2-real-life)
  - [Visual: The Mutual Follow Problem](#2-visual-mutual)
  - [Kosaraju's Algorithm](#2-kosaraju)
  - [Visual: Kosaraju's Two-Pass Walkthrough](#2-kosaraju-trace)
  - [Tarjan's Algorithm](#2-tarjan)
  - [Where SCC Used](#2-scc-used)
- [3. Minimum Spanning Tree (MST)](#3-mst)
  - [Real Life Example](#3-real-life)
  - [Kruskal's Algorithm](#3-kruskal)
  - [Visual: Kruskal's Step-by-Step](#3-kruskal-trace)
  - [Prim's Algorithm](#3-prim)
  - [Difference](#3-difference)
- [4. Network Flow — Maximum Flow in Graph](#4-network-flow)
  - [Real Life Example](#4-real-life)
  - [Ford-Fulkerson Algorithm](#4-ford-fulkerson)
  - [Edmonds-Karp](#4-edmonds-karp)
  - [Dinic's Algorithm](#4-dinic)
  - [Applications](#4-applications)
- [5. Shortest Path Algorithms](#5-shortest-path)
  - [Dijkstra — The GPS That Never Backtracks](#5-dijkstra)
  - [Visual: Dijkstra Step-by-Step Trace](#5-dijkstra-trace)
  - [Bellman-Ford — Shortest Path with Negative Weights](#5-bellman-ford)
  - [Visual: Bellman-Ford Round-by-Round Trace](#5-bellman-trace)
  - [Python Implementation (Bellman-Ford)](#5-bellman-python)
  - [Detecting Negative Cycles](#5-neg-cycles)
  - [Bellman-Ford vs Dijkstra](#5-bellman-vs-dijkstra)
  - [Floyd-Warshall — All-Pairs Shortest Path](#5-floyd)
  - [Python Implementation (Floyd-Warshall)](#5-floyd-python)
  - [Floyd-Warshall vs Bellman-Ford](#5-floyd-vs-bellman)
- [6. When to Use What?](#6-when-to-use)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
topological sort (Kahn's + DFS) · Dijkstra's algorithm · Bellman-Ford

**Should Learn** — Important for real projects, comes up regularly:
SCC (Kosaraju's/Tarjan's) · MST (Kruskal's/Prim's) · Floyd-Warshall

**Good to Know** — Useful in specific situations, not always tested:
negative cycle detection · all-pairs shortest path

**Reference** — Know it exists, look up syntax when needed:
Dinic's max flow · A* search · bidirectional Dijkstra · Eulerian path · bipartite matching

<a id="1-topological-sort"></a>
# 1. Topological Sort — Ordering Dependencies

Pushpa has a supply chain. Before he can move cargo across the border, he must:
first acquire the goods, then load them onto mules, then bribe the checkpoint guard,
then cross the river, then deliver to the buyer. You cannot bribe the guard before
you have cargo — that would raise suspicion. You cannot cross the river before the
guard is bribed — that means capture.

This is a Directed Acyclic Graph (DAG) of dependencies.
Topological sort gives Pushpa the valid execution order for his smuggling operation.

<a id="1-real-life"></a>
## Real Life Example

Imagine building software.

Tasks:

- Write code
- Compile
- Test
- Deploy

You cannot deploy before testing.

This forms a Directed Acyclic Graph (DAG).

Topological sort gives valid execution order.

<a id="1-visual-prereqs"></a>
## Visual: Course Prerequisites

You are advising a CS student on which courses to take. Some courses have
prerequisites — you must take Data Structures before Algorithms, you must take
Calculus before Machine Learning, etc.

```
  Courses and prerequisites:
  Intro CS (0 prereqs)
  Math      (0 prereqs)
  Data Struct (needs Intro CS)
  Algorithms  (needs Data Struct)
  Calc        (needs Math)
  ML          (needs Algorithms + Calc)
  Capstone    (needs ML)

  DAG:
  IC = Intro CS, DS = Data Struct, AL = Algorithms
  MA = Math,     CA = Calc,        ML = Machine Learning, CAP = Capstone

  IC ──► DS ──► AL ──┐
                      ▼
  MA ──► CA ─────► ML ──► CAP
```

A valid topological order: IC, MA, DS, CA, AL, ML, CAP

<a id="1-core-idea"></a>
## Core Idea

Only works on:

Directed Acyclic Graph (DAG)

Produces linear ordering such that:

For every edge u → v,
u comes before v.

<a id="1-kahns"></a>
## Kahn's Algorithm (BFS + Indegree)

1. Calculate indegree of each node.
2. Add nodes with indegree 0 to queue.
3. Remove node, reduce neighbors' indegree.
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

<a id="1-kahns-trace"></a>
## Visual: Kahn's Step-by-Step Trace

```
  In-degree map: {IC:0, MA:0, DS:1, CA:1, AL:1, ML:2, CAP:1}

  Queue: [IC, MA]

  Iteration 1: Pop IC → Result: [IC]
    DS in-degree: 1→0 → add DS to queue
  Queue: [MA, DS]

  Iteration 2: Pop MA → Result: [IC, MA]
    CA in-degree: 1→0 → add CA to queue
  Queue: [DS, CA]

  Iteration 3: Pop DS → Result: [IC, MA, DS]
    AL in-degree: 1→0 → add AL to queue
  Queue: [CA, AL]

  Iteration 4: Pop CA → Result: [IC, MA, DS, CA]
    ML in-degree: 2→1 → NOT zero yet
  Queue: [AL]

  Iteration 5: Pop AL → Result: [IC, MA, DS, CA, AL]
    ML in-degree: 1→0 → add ML!
  Queue: [ML]

  Iteration 6: Pop ML → Result: [IC, MA, DS, CA, AL, ML]
    CAP in-degree: 1→0 → add CAP
  Queue: [CAP]

  Iteration 7: Pop CAP → Result: [IC, MA, DS, CA, AL, ML, CAP]
  DONE!
```

**Common mistake — missing cycle check:** Kahn's silently returns a partial ordering if a cycle exists. Always check `len(order) == V` before returning. If you skip this, callers receive an incomplete ordering with no error and skip nodes in the cycle entirely.

> 📝 **Practice:** [Q7 · Kahn's basics](./practice.md#q7--topological-sort--kahns-algorithm-basics) · [Q8 · cycle detection](./practice.md#q8--topological-sort--cycle-detection-via-kahns) · [Q9 · DFS post-order](./practice.md#q9--topological-sort--dfs-post-order) · [Q10 · course schedule](./practice.md#q10--topological-sort--course-schedule)

<a id="1-dfs-topo"></a>
## DFS-Based Topological Sort

1. DFS traversal.
2. Push node to stack after exploring neighbors.
3. Reverse stack.

**Key insight:** Add a node to the stack AFTER all its descendants are finished (post-order). When you pop the stack, prerequisites come before dependents.

```
  DFS Call Stack Trace (starting from IC):

  call DFS(IC)
  │  explore DS
  │  │  call DFS(DS)
  │  │  │  explore AL
  │  │  │  │  call DFS(AL)
  │  │  │  │  │  explore ML
  │  │  │  │  │  │  call DFS(ML)
  │  │  │  │  │  │  │  explore CAP
  │  │  │  │  │  │  │  │  *** PUSH CAP to stack ***
  │  │  │  │  │  │  │  *** PUSH ML to stack ***
  │  │  │  │  │  │  *** PUSH AL to stack ***
  │  │  │  *** PUSH DS to stack ***
  │  *** PUSH IC to stack ***

  Stack (bottom to top): [CAP, ML, AL, DS, IC, CA, MA]
  Pop to get order: MA, CA, IC, DS, AL, ML, CAP
```

Also:
O(V + E)

<a id="1-cycles"></a>
## Detecting Cycles

If topological sort does not include all nodes,
cycle exists.

```
  Suppose we add edge DS → IC (circular prerequisite):
  IC → DS → IC → DS ...

  In Kahn's: IC in-degree becomes 2, DS in-degree stays 1.
  Neither ever reaches in-degree 0.
  Queue empties with only 5 of 7 nodes processed.
  len(order) < total_nodes → CYCLE DETECTED!

  ┌────────────────────────────────────────────────────────────┐
  │  "I need Data Structures before Intro CS, but              │
  │   I need Intro CS before Data Structures."                 │
  │   → No valid schedule. Cycle detected.                     │
  └────────────────────────────────────────────────────────────┘
```

**Common mistake — Union-Find for directed cycle detection:** Union-Find does not track edge direction and will falsely report a cycle in a DAG like `0→1, 1→2, 0→2` (it sees 0 and 2 in the same set and cries "cycle"). For directed graphs, use DFS with WHITE/GRAY/BLACK coloring: GRAY means "in current DFS stack" — hitting a GRAY node is a true back edge and a real cycle.

> [↑ Back to Top](#top)

<a id="2-scc"></a>
# 2. Strongly Connected Components (SCC)

Pushpa's smuggling network spans multiple mountain regions. Within each region,
his runners can reach each other through a web of trails — if Runner A can get a
message to Runner B, then Runner B can always get a message back to Runner A.
These tight-knit regional cells are Strongly Connected Components. But between
regions, messages only flow one way — the mountain pass from Region 1 to Region 2
is one-directional. Pushpa needs to identify these cells to know which groups can
coordinate internally and which need special one-way courier routes.

> 📝 **Practice:** [Q11 · Kosaraju's algorithm](./practice.md#q11--scc--kosarajus-algorithm) · [Q12 · count SCCs](./practice.md#q12--scc--count-strongly-connected-components) · [Q13 · condensation graph](./practice.md#q13--scc--condensation-graph)

<a id="2-real-life"></a>
## Real Life Example

Imagine cities where:

If you can travel from A to B,
and from B to A,
they form a strong group.

SCC = maximal set of nodes reachable mutually.

<a id="2-visual-mutual"></a>
## Visual: The Mutual Follow Problem

In a social network, a Strongly Connected Component is a tight-knit clique where
information can flow in all directions. Two nodes are in the same SCC if you can
get from A to B AND from B to A.

```
  SCC1 = {A, B, C}: A→B, B→C, C→A
  SCC2 = {D, E}:    D→E, E→D
  SCC3 = {F, G, H}: F→G, G→H, H→F

  Inter-SCC edges (one direction only): C→D, E→F

  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │   SCC 1      │     │   SCC 2      │     │   SCC 3      │
  │              │     │              │     │              │
  │  A ──► B    │     │   D ◄──► E   │     │  F ──► G    │
  │  ▲      │   │     │              │     │  ▲      │   │
  │  │      ▼   │─C→D─│              │─E→F─│  │      ▼   │
  │  └──── C    │     │              │     │  └──── H    │
  │              │     │              │     │              │
  └──────────────┘     └──────────────┘     └──────────────┘
```

<a id="2-kosaraju"></a>
## Kosaraju's Algorithm

Steps:

1. DFS and push nodes by finish time.
2. Reverse graph.
3. DFS in order of stack.

Time:
O(V + E)

<a id="2-kosaraju-trace"></a>
## Visual: Kosaraju's Two-Pass Walkthrough

**Pass 1 — DFS on original graph, record finish order:**

```
  DFS from A:
    Visit B (A→B)
      Visit C (B→C)
        C→A is back edge (A already visited)
        *** FINISH C → push: [C] ***
      *** FINISH B → push: [C, B] ***
    *** FINISH A → push: [C, B, A] ***

  DFS from D:
    Visit E (D→E)
      E→D is back edge
      *** FINISH E → push: [C, B, A, E] ***
    *** FINISH D → push: [C, B, A, E, D] ***

  DFS from F:
    Visit G → Visit H → H→F back edge
    *** FINISH: [C, B, A, E, D, H, G, F] ***

  Finish stack top → F, G, H, D, E, A, B, C
  (Last finished = most "source-like" in the SCC DAG)
```

**Pass 2 — DFS on REVERSED graph in reverse finish order:**

```
  Reversed edges: B→A, C→B, A→C | E→D, D→E | G→F, H→G, F→H | D→C, F→E

  Pop F: DFS(F) on reversed → visits F, G, H (cycle in reversed graph)
    SCC #3 = {F, G, H} ✓

  Pop G: already visited, skip
  Pop H: already visited, skip

  Pop D: DFS(D) on reversed → visits D, E
    SCC #2 = {D, E} ✓

  Pop A: DFS(A) on reversed → visits A, B, C
    SCC #1 = {A, B, C} ✓

  ┌──────────┐   ┌──────────┐   ┌──────────┐
  │  {A,B,C} │   │  {D,E}   │   │  {F,G,H} │
  └──────────┘   └──────────┘   └──────────┘
```

**Common mistake — second DFS on the original graph:** The entire point of Pass 2 is to use the REVERSED graph. If you run both DFS passes on the original graph, DFS from the last-finished node freely crosses SCC boundaries and merges multiple SCCs into one. Always build `radj` (reversed adjacency list) before Pass 2.

<a id="2-tarjan"></a>
## Tarjan's Algorithm

Single DFS traversal.
Uses:

- Discovery time
- Low link value
- Stack

More advanced.
Also O(V + E)

<a id="2-scc-used"></a>
## Where SCC Used

- Social network clustering
- Compiler optimizations
- Detecting cycles in directed graph
- Graph condensation

**Common mistake — single-source BFS/DFS on disconnected graphs:** Starting BFS or DFS from node 0 only visits the component containing node 0. If the graph has multiple disconnected components, the other components are silently missed. Always wrap your traversal in an outer loop: `for i in range(n): if not visited[i]: bfs/dfs(i)`.

**Common mistake — missing reverse edge in undirected adjacency list:** For undirected graphs, every edge `(u, v)` must add both `adj[u].append(v)` and `adj[v].append(u)`. Omitting the second line makes some nodes unreachable — DFS from node 4 in a broken adjacency list returns only `{4}` instead of the full component.

> [↑ Back to Top](#top)

<a id="3-mst"></a>
# 3. Minimum Spanning Tree (MST)

Pushpa needs to connect all his mountain hideouts with supply trails. Each trail
between two hideouts has a construction cost — clearing brush, bribing locals,
building rope bridges. He wants ALL hideouts connected so cargo can flow anywhere,
but he wants to spend the absolute minimum on trail construction. He needs exactly
N-1 trails for N hideouts. Any fewer and some hideouts are cut off. Any more and
he is wasting money that could buy more cargo.

This is the Minimum Spanning Tree problem.

> 📝 **Practice:** [Q14 · Kruskal's MST](./practice.md#q14--kruskals-mst--minimum-spanning-tree-weight) · [Q15 · Prim's MST](./practice.md#q15--prims-mst--minimum-spanning-tree-weight) · [Q16 · Kruskal vs Prim](./practice.md#q16--mst--kruskal-vs-prim-decision)

> 📝 **Practice:** [Q53 · minimum-spanning-tree](../dsa_practice_questions_100.md#q53--interview--minimum-spanning-tree)

<a id="3-real-life"></a>
## Real Life Example

Connecting cities with minimum cable cost.

Want:

All cities connected
Minimum total cost

That is MST.

Key constraint: you need exactly N-1 roads for N cities. Any fewer and some cities
are disconnected. Any more and you are wasting money.

<a id="3-kruskal"></a>
## Kruskal's Algorithm

1. Sort edges by weight.
2. Use DSU.
3. Add edge if no cycle.

Time:
O(E log E)

<a id="3-kruskal-trace"></a>
## Visual: Kruskal's Step-by-Step (6 Cities)

```
  Cities: 1, 2, 3, 4, 5, 6
  All edges sorted by cost:
    4─6: 2  |  3─5: 3  |  1─2: 4  |  2─5: 5
    5─6: 6  |  3─4: 7  |  2─3: 8  |  1─3: 9  |  ...
```

```
  Step 1: Edge 4─6 (cost 2) — different groups → ADD
    Groups: {1} {2} {3} {4,6} {5}     MST cost: 2

  Step 2: Edge 3─5 (cost 3) — different groups → ADD
    Groups: {1} {2} {3,5} {4,6}       MST cost: 5

  Step 3: Edge 1─2 (cost 4) — different groups → ADD
    Groups: {1,2} {3,5} {4,6}         MST cost: 9

  Step 4: Edge 2─5 (cost 5) — different groups → ADD
    Groups: {1,2,3,5} {4,6}           MST cost: 14

  Step 5: Edge 5─6 (cost 6) — different groups → ADD
    Groups: {1,2,3,4,5,6}  ALL CONNECTED!   MST cost: 20

  Step 6: Edge 3─4 (cost 7) — SAME group → SKIP (would create cycle)

  Final MST:
  [1]───4───[2]
             │
             5
             │
  [3]───3───[5]───6───[6]───2───[4]

  Total cost: 2+3+4+5+6 = 20
  ┌─────────────────────────────────────────────────────────────┐
  │  Kruskal's: Sort edges O(E log E), Union-Find ≈ O(E)        │
  │  Use when: edges given explicitly, sparse graphs            │
  └─────────────────────────────────────────────────────────────┘
```

<a id="3-prim"></a>
## Prim's Algorithm

1. Start from node.
2. Use min heap.
3. Pick smallest edge expanding tree.

Time:
O(E log V)

**Common mistake — mixing Prim's and Kruskal's logic:** Prim's is vertex-based — it grows a tree from a starting node, always picking the cheapest edge that connects an unvisited vertex to the current tree via a min-heap on `(weight, vertex)`. Kruskal's is edge-based — it sorts all edges globally and uses Union-Find to skip cycles. Mixing them (e.g., doing a global edge sort inside Prim's framework) breaks the "only expand from current tree" invariant and produces wrong MSTs on some inputs.

<a id="3-difference"></a>
## Difference

Kruskal:
Edge-based. Use when edges are given explicitly, sparse graphs.

Prim:
Node-based. Use when graph is dense or given as adjacency matrix.

Choose based on graph density.

> [↑ Back to Top](#top)

<a id="4-network-flow"></a>
# 4. Network Flow — Maximum Flow in Graph

Pushpa has multiple smuggling routes from his source warehouse to the final buyer.
Each route (pipe) has a maximum capacity — only so many mules can travel that trail
per night. Some trails are narrow (low capacity), some are wide highways (high capacity).
Pushpa wants to maximize the total cargo delivered per night across ALL routes combined.
This is the Maximum Flow problem — finding how much "flow" can be pushed from source to sink.

> 📝 **Practice:** [Q17 · max flow Edmonds-Karp](./practice.md#q17--network-flow--max-flow-via-edmonds-karp) · [Q18 · bipartite matching](./practice.md#q18--network-flow--bipartite-matching-via-max-flow)

<a id="4-real-life"></a>
## Real Life Example

Water flows through pipes.

Each pipe has capacity.

Goal:
Maximize water flow from source to sink.

<a id="4-ford-fulkerson"></a>
## Ford-Fulkerson Algorithm

Find augmenting path.
Increase flow.

Time:
Depends on implementation.

<a id="4-edmonds-karp"></a>
## Edmonds-Karp

BFS-based Ford-Fulkerson.

Time:
O(VE²)

<a id="4-dinic"></a>
## Dinic's Algorithm

Optimized approach.

Time:
O(E√V) (for some cases)

Used in competitive programming.

<a id="4-applications"></a>
## Applications

- Maximum bipartite matching
- Airline scheduling
- Resource allocation
- Network bandwidth optimization

> [↑ Back to Top](#top)

<a id="5-shortest-path"></a>
# 5. Shortest Path Algorithms

Pushpa stands at his mountain base camp, staring at a map of trails leading to
the border crossing 200 km away. There are dozens of paths — some short but
dangerous (negative cost: allies along the way actually GIVE him supplies), some
long but safe. He needs the cheapest route. Sometimes he needs to know the cheapest
route between EVERY pair of hideouts so any runner can reach any other runner optimally.

This is the domain of shortest path algorithms.

> 📝 **Practice:** [Q1 · Dijkstra basics](./practice.md#q1--dijkstra--single-source-shortest-path) · [Q2 · path reconstruction](./practice.md#q2--dijkstra--path-reconstruction) · [Q4 · Bellman-Ford](./practice.md#q4--bellman-ford--shortest-path-with-negative-edges) · [Q5 · negative cycles](./practice.md#q5--bellman-ford--negative-cycle-detection) · [Q6 · Floyd-Warshall](./practice.md#q6--floyd-warshall--all-pairs-shortest-path)

> 📝 **Practice:** [Q100 · design-shortest-path-constraints](../dsa_practice_questions_100.md#q100--design--design-shortest-path-constraints)

Dijkstra (covered in module 18) handles non-negative weights.
But what if edges have negative weights?
What if you need ALL pairs of shortest paths?

<a id="5-dijkstra"></a>
## Dijkstra — The GPS That Never Backtracks

Think of Dijkstra as a GPS that always explores the cheapest known route next.
It keeps a priority queue (min-heap) of `(cost, city)` pairs and greedily commits
to the cheapest next step — called greedy relaxation.

**Edges:**
- A -> B (cost 4), A -> C (cost 2), C -> B (cost 1)  [A→C→B costs 3, cheaper than A→B!]
- B -> D (cost 5), C -> D (cost 8), B -> E (cost 3)
- D -> E (cost 2), D -> F (cost 2), E -> G (cost 4), F -> G (cost 3)

```
         4         5         2
    A ──────► B ──────► D ──────► F
    │         ▲         │         │
    │ 2     1 │         │ 2       │ 3
    │         │         │         │
    ▼         │         ▼         ▼
    C ────────┘         E ──────► G
    │                   ▲
    │ 8                 │ 4
    │                   │
    └───────────► D     E (same node)
```

<a id="5-dijkstra-trace"></a>
## Visual: Dijkstra Step-by-Step Trace

```
Initial: dist = {A:0, B:INF, C:INF, D:INF, E:INF, F:INF, G:INF}
Queue: [(0,A)]

Step 1: Extract (0,A)
  A→B(4): dist[B]=4   A→C(2): dist[C]=2
  dist = {A:0, B:4, C:2, ...}   Queue: [(2,C),(4,B)]

Step 2: Extract (2,C)
  C→B(1): dist[B]=min(4,3)=3  C→D(8): dist[D]=10
  Queue: [(3,B),(4,B),(10,D)]   ← (4,B) is now stale

Step 3: Extract (3,B)
  B→D(5): dist[D]=min(10,8)=8  B→E(3): dist[E]=6
  Queue: [(4,B),(6,E),(8,D),(10,D)]

Step 4: Extract (4,B) — B already visited → SKIP stale entry

Step 5: Extract (6,E)
  E→G(4): dist[G]=10
  Queue: [(8,D),(10,D),(10,G)]

Step 6: Extract (8,D)
  D→E(2): 10 NOT < 6 → no update   D→F(2): dist[F]=10
  Queue: [(10,D),(10,G),(10,F)]

Step 7: Extract (10,D) — stale → SKIP

Step 8: Extract (10,G) — destination reached, cost 10.

Final shortest paths from A:
  B=3 (A→C→B)  C=2 (A→C)  D=8 (A→C→B→D)
  E=6 (A→C→B→E)  F=10 (A→C→B→D→F)  G=10 (A→C→B→E→G)
```

**Common mistake — Dijkstra with negative edges:** Dijkstra's greedy invariant — "once a node is popped, its shortest distance is final" — is only valid when all edge weights are non-negative. With negative edges, a later-discovered path through more hops may be shorter than a path Dijkstra already finalized. Use Bellman-Ford when negative edges exist.

**Common mistake — not skipping stale Dijkstra entries:** Python's `heapq` does not support priority updates, so when a shorter path is found, the old `(higher_cost, node)` entry stays in the heap. Always add `if d > dist[u]: continue` immediately after popping. Without this, the algorithm reprocesses nodes with outdated distances, causing O(E²) degradation in worst case instead of O(E log V).

> 📝 **Practice:** [Q51 · dijkstra-algorithm](../dsa_practice_questions_100.md#q51--normal--dijkstra-algorithm)

<a id="5-bellman-ford"></a>
## Bellman-Ford — Shortest Path with Negative Weights

> 📝 **Practice:** [Q89 · production-negative-cycles](../dsa_practice_questions_100.md#q89--design--production-negative-cycles)

Pushpa discovers that some trails actually GAIN him resources — allied villages along
the way top up his supplies (negative-weight edges). Dijkstra cannot handle this because
it greedily commits to distances. Bellman-Ford is the patient approach: it relaxes ALL
edges V-1 times, guaranteeing correctness even with negative weights.

## The Problem Dijkstra Can't Solve

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

## The Core Idea

Bellman-Ford is the patient mathematician. He doesn't trust any single pass.
He relaxes ALL edges V-1 times. After V-1 passes, all shortest paths are found.

Why V-1? The shortest path in a graph with V nodes can have at most V-1 edges.

```
Relaxation: if dist[u] + weight(u,v) < dist[v]:
                dist[v] = dist[u] + weight(u,v)
```

## Why N-1 Rounds?

```
In a graph with N nodes, the longest simple path has at most N-1 edges.

Round 1: correctly compute shortest paths using at most 1 edge
Round 2: correctly compute shortest paths using at most 2 edges
...
Round N-1: correctly compute shortest paths using at most N-1 edges

After N-1 rounds: ALL shortest paths found (assuming no negative cycles).
```

<a id="5-bellman-trace"></a>
## Visual: Bellman-Ford Round-by-Round Trace

```
  Nodes: A B C D E
  Edges: A→B(6), A→D(7), B→C(5), B→D(8), B→E(-4), D→E(9), D→B(-3), E→C(7), C→A(2)
  Source: A

  Initial: dist = { A:0, B:INF, C:INF, D:INF, E:INF }

  Round 1:
    A→B(6):  0+6=6   → dist[B]=6
    A→D(7):  0+7=7   → dist[D]=7
    B→C(5):  6+5=11  → dist[C]=11
    B→D(8):  6+8=14  NOT < 7
    B→E(-4): 6-4=2   → dist[E]=2
    D→E(9):  7+9=16  NOT < 2
    D→B(-3): 7-3=4   < 6 → dist[B]=4
    E→C(7):  2+7=9   < 11 → dist[C]=9
  After Round 1: { A:0, B:4, C:9, D:7, E:2 }

  Round 2:
    B→E(-4): 4-4=0   < 2 → dist[E]=0
    E→C(7):  0+7=7   < 9 → dist[C]=7
  After Round 2: { A:0, B:4, C:7, D:7, E:0 }

  Round 3: No changes.
  Final: A=0, B=4, C=7, D=7, E=0
```

<a id="5-bellman-python"></a>
## Python Implementation (Bellman-Ford)

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

<a id="5-neg-cycles"></a>
## Detecting Negative Cycles

After V-1 passes, run one more pass. If any dist still decreases, a negative cycle exists.
(A negative cycle means "shortest path" = -∞ — you can loop forever decreasing distance.)

```
Negative cycle: A →(1)→ B →(-3)→ C →(1)→ A
  Sum of cycle = 1 + (-3) + 1 = -1 < 0
  You could loop this cycle forever to reach -∞ distance
```

**Common mistake — Bellman-Ford stopping at V-1 passes:** Running V-1 iterations finds shortest paths but does NOT detect negative cycles. You must run one additional (Nth) pass. If any distance still improves, a negative cycle exists in the reachable graph. Stopping early returns plausible-looking but meaningless finite distances for nodes caught in a negative cycle.

<a id="5-bellman-vs-dijkstra"></a>
## Bellman-Ford vs Dijkstra

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

<a id="5-floyd"></a>
## Floyd-Warshall — All-Pairs Shortest Path

Pushpa doesn't just need the cheapest route from base camp to the border.
He needs to know the cheapest route between EVERY pair of hideouts so any runner
can reach any other runner optimally. Floyd-Warshall gives him this complete map.

## The Problem

Dijkstra and Bellman-Ford find shortest paths FROM one source.
Floyd-Warshall finds shortest paths BETWEEN ALL pairs of nodes simultaneously.

**Real-world use:** "What is the shortest route between EVERY city pair in a road network?"

## The Core Idea

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
  dist[2][1]: min(∞, dist[2][0]+dist[0][1]) = min(∞, 2+5) = 7  ← improved!

After k=1 (using node 1 as intermediate):
  dist[0][2]: min(∞, dist[0][1]+dist[1][2]) = min(∞, 5+3) = 8  ← improved!

After k=2 (using node 2 as intermediate):
  dist[1][0]: min(∞, dist[1][2]+dist[2][0]) = min(∞, 3+2) = 5  ← improved!

Final: all-pairs shortest distances computed in O(V³)
```

**Common mistake — Floyd-Warshall wrong loop order:** The `k` loop (intermediate node) MUST be the outermost loop. If `k` is innermost, you ask "does node k help path i→j?" before `dist[i][k]` and `dist[k][j]` are fully optimized through earlier intermediates. This produces wrong shortest paths silently. The correct order is always `for k → for i → for j`.

<a id="5-floyd-python"></a>
## Python Implementation (Floyd-Warshall)

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

<a id="5-floyd-vs-bellman"></a>
## Floyd-Warshall vs Bellman-Ford

```
Use Floyd-Warshall when: all-pairs shortest path needed, V is small (V ≤ 500)
Use Bellman-Ford when:   single-source, negative edges, negative cycle detection
Time: Floyd = O(V³),  Bellman = O(VE)
```

> [↑ Back to Top](#top)

<a id="6-when-to-use"></a>
# 6. When to Use What?

Pushpa stares at a new problem. The terrain varies — sometimes he needs ordering,
sometimes connectivity, sometimes cheapest path. Here is how he decides which
algorithm to deploy:

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

> [↑ Back to Top](#top)

## 🔥 Summary

Advanced graph algorithms solve three categories of problems:

**Structure problems** — ordering (topological sort) and grouping (SCC)
**Flow problems** — maximizing throughput (network flow)
**Optimization problems** — minimum cost connectivity (MST) and shortest paths (Dijkstra/Bellman-Ford/Floyd-Warshall)

They are layered over basic BFS/DFS. Without strong basics, advanced graphs become confusing.

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

```
  Pushpa's Algorithm Selection Flowchart:

  ┌─────────────────────────────────────────────────────────────────┐
  │  "What does the problem ask?"                                   │
  ├─────────────────────────────────────────────────────────────────┤
  │                                                                 │
  │  Order tasks?          ──► Topological Sort (Kahn's or DFS)     │
  │  Find tight groups?    ──► SCC (Kosaraju's or Tarjan's)         │
  │  Connect everything    ──► MST (Kruskal's or Prim's)            │
  │    cheaply?                                                     │
  │  Max throughput?       ──► Network Flow (Edmonds-Karp/Dinic's)  │
  │  Cheapest single path? ──► Dijkstra (no neg) / Bellman (neg)    │
  │  All-pairs cheapest?   ──► Floyd-Warshall                       │
  │                                                                 │
  └─────────────────────────────────────────────────────────────────┘
```

> [↑ Back to Top](#top)

## 📂 Navigation

**[Back to README](../README.md)**

**Prev:** [Disjoint Set Union — Theory](../24_disjoint_set_union/theory.md) | **Next:** None (last module)

**Related Topics:** [Graphs — Theory](../18_graphs/theory.md) · [Disjoint Set Union — Theory](../24_disjoint_set_union/theory.md) · [Greedy — Theory](../19_greedy/theory.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

> [↑ Back to Top](#top)
