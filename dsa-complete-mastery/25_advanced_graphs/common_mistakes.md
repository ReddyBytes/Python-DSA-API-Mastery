# Advanced Graphs — Common Mistakes

> "Graphs are deceptively simple to describe and deceptively hard to implement correctly. One wrong assumption about edge weights, one missed direction, one skipped iteration — and your algorithm confidently produces the wrong answer with no error messages."

This file is your field guide to the 10 most common, most interview-breaking mistakes in advanced graph algorithms: Dijkstra, Bellman-Ford, topological sort, Floyd-Warshall, Kosaraju's SCC, MST, BFS/DFS on disconnected graphs, adjacency list direction, Dijkstra stale entries, and cycle detection.

---

## Table of Contents

1. [Dijkstra with Negative Edges](#mistake-1)
2. [Bellman-Ford: Missing the Extra Pass for Negative Cycle Detection](#mistake-2)
3. [Topological Sort on a Graph with Cycles](#mistake-3)
4. [Floyd-Warshall: Wrong Loop Order](#mistake-4)
5. [Kosaraju's SCC: Wrong DFS Direction](#mistake-5)
6. [Prim's vs Kruskal's Confusion](#mistake-6)
7. [BFS/DFS on Disconnected Graph](#mistake-7)
8. [Directed vs Undirected Adjacency List](#mistake-8)
9. [Stale Entries in Dijkstra's Priority Queue](#mistake-9)
10. [Union-Find for Directed Graph Cycle Detection](#mistake-10)

---

## Mistake 1: Dijkstra with Negative Edges {#mistake-1}

### The Story

Dijkstra's algorithm is like a hiker who always takes the shortest path visible in front of them. They never backtrack. This works perfectly when paths only get longer as you go — you'll never find a shortcut by turning around.

But imagine a trail where some paths have negative length (maybe a downhill that actually puts you closer to the start). Suddenly, the hiker's "I never backtrack" rule fails. By the time they discover a negative-length shortcut, they've already committed to a path they declared final.

Dijkstra's greedy invariant: **"once a node is popped from the priority queue, its shortest distance is finalized."** This invariant is ONLY valid when all edge weights are non-negative.

### The Counterexample

```
4-node graph:
    A ---1--> B
    A ---4--> C
    B ---2--> C
    B ---5--> D
    C --(-3)--> D

Edge weights: A→B=1, A→C=4, B→C=2, B→D=5, C→D=-3

True shortest paths from A:
  A→B: 1
  A→C: min(4, 1+2) = 3
  A→D: min(1+5, 1+2-3) = min(6, 0) = 0  ← via A→B→C→D!
```

```
ASCII Diagram:
    A ──1──> B ──5──> D
    │        │        ^
    4        2        │
    │        v       -3
    └──────> C ──────/
```

### WRONG Code: Dijkstra with Negative Edges

```python
import heapq

def dijkstra_wrong(graph, src, n):
    """Dijkstra — WRONG for graphs with negative edges."""
    dist = [float('inf')] * n
    dist[src] = 0
    heap = [(0, src)]  # (distance, node)

    while heap:
        d, u = heapq.heappop(heap)

        # Once popped, Dijkstra says: "this is final"
        # BUG: This assumption is WRONG when negative edges exist
        if d > dist[u]:
            continue

        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))

    return dist

# Graph: 0=A, 1=B, 2=C, 3=D
graph = {
    0: [(1, 1), (2, 4)],   # A: A→B=1, A→C=4
    1: [(2, 2), (3, 5)],   # B: B→C=2, B→D=5
    2: [(3, -3)],           # C: C→D=-3
    3: []                   # D: no outgoing
}

wrong_dist = dijkstra_wrong(graph, 0, 4)
print("Dijkstra distances from A:", wrong_dist)
# Expected: [0, 1, 3, 0]  (A=0, B=1, C=3, D=0)
# Dijkstra gives:          [0, 1, 3, 1] or wrong value for D

# Trace of failure:
# heap: [(0, A)]
# Pop (0, A): dist[A]=0. Relax B to 1, C to 4. heap: [(1,B),(4,C)]
# Pop (1, B): dist[B]=1. Relax C to min(4, 1+2)=3. Relax D to 1+5=6.
#             heap: [(3,C),(4,C),(6,D)]
# Pop (3, C): dist[C]=3. Relax D to min(6, 3-3)=0. heap: [(0,D),(4,C),(6,D)]
# Pop (0, D): dist[D]=0. No outgoing edges.
# Pop (4, C): d=4 > dist[C]=3, skip. (stale entry)
# Pop (6, D): d=6 > dist[D]=0, skip. (stale entry)
# Final dist: [0, 1, 3, 0] — ACTUALLY CORRECT here!

# But try this graph where the negative edge creates a better path
# that's reachable only AFTER Dijkstra has "finalized" a node:
graph2 = {
    0: [(1, 10), (2, 1)],  # A→B=10, A→C=1
    1: [],                  # B: no outgoing
    2: [(1, -5)],           # C→B=-5 (negative!)
    3: []
}
# True shortest: A→B via C = 1 + (-5) = -4
# Dijkstra processes:
# heap: [(0,A)]
# Pop A: relax B to 10, C to 1. heap: [(1,C),(10,B)]
# Pop C (dist=1): relax B to min(10, 1-5)=-4. Push (-4,B). heap: [(-4,B),(10,B)]
# Pop (-4,B): d=-4 < dist[B]=10? -4 < 10, YES. So dist[B]=-4.
# Actually Dijkstra CAN get this right IF the negative edge is processed
# before B is finalized... but in other configurations it fails silently.

# The dangerous case: when a node is ALREADY POPPED (finalized) and then
# a negative edge could improve it — Dijkstra won't re-process it.
graph3 = {
    0: [(1, 2), (2, 6)],   # A
    1: [(2, 1)],            # B
    2: [(3, 1)],            # C
    3: [(1, -5)]            # D→B=-5 (negative cycle creates issues)
}
```

### RIGHT Code: Bellman-Ford for Graphs with Negative Edges

```python
def bellman_ford(graph_edges, n, src):
    """
    Bellman-Ford: handles negative edges. O(V*E).
    graph_edges: list of (u, v, weight)
    Returns dist array, or detects negative cycle.
    """
    dist = [float('inf')] * n
    dist[src] = 0

    # Relax all edges V-1 times
    for _ in range(n - 1):
        updated = False
        for u, v, w in graph_edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated:
            break  # Early termination: no changes, already optimal

    # Check for negative cycles (one more pass)
    for u, v, w in graph_edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            return None, True  # Negative cycle detected!

    return dist, False

# Test on the counterexample graph
edges = [
    (0, 1, 1),   # A→B=1
    (0, 2, 4),   # A→C=4
    (1, 2, 2),   # B→C=2
    (1, 3, 5),   # B→D=5
    (2, 3, -3),  # C→D=-3
]

dist, has_neg_cycle = bellman_ford(edges, 4, 0)
if has_neg_cycle:
    print("Negative cycle detected!")
else:
    print("Bellman-Ford distances from A:", dist)
    # [0, 1, 3, 0] — correct!
    # A=0, B=1, C=3, D=0 (via A→B→C→D = 1+2-3 = 0)

# When to use which:
# - All non-negative weights → Dijkstra O((V+E) log V)
# - Negative weights, no negative cycle → Bellman-Ford O(V*E)
# - Need to detect negative cycle → Bellman-Ford
# - Dense graph, all-pairs → Floyd-Warshall O(V^3)
```

---

## Mistake 2: Bellman-Ford — Missing the Extra Pass for Negative Cycle Detection {#mistake-2}

### The Story

Imagine you're counting laps on a racetrack. After V-1 laps, you've explored all possible paths. But if someone is running backwards on the track (a negative-weight edge that creates a cycle), you might NEVER settle — you can always go around the loop one more time to get a shorter "distance."

Bellman-Ford runs V-1 iterations to find shortest paths. To DETECT a negative cycle, you run one MORE iteration. If anything still improves, a negative cycle exists.

The mistake: stopping at V-1, reporting "no negative cycle found," when in fact one exists.

### WRONG Code: Stopping at V-1

```python
def bellman_ford_wrong_cycle_detection(edges, n, src):
    """BUG: Does not detect negative cycles correctly."""
    dist = [float('inf')] * n
    dist[src] = 0

    for i in range(n - 1):
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w

    # BUG: No extra pass! Just return dist as-is.
    # If there's a negative cycle, we return bogus distances
    return dist  # Claimed as correct, but may be wrong!

# Graph with negative cycle: 0→1→2→0 with weights 1, -2, 0
# Cycle weight: 1 + (-2) + 0 = -1 (negative!)
edges_neg_cycle = [
    (0, 1, 1),
    (1, 2, -2),
    (2, 0, 0),
    (0, 3, 5),  # Node 3 reachable from cycle
]
n = 4

wrong_dist = bellman_ford_wrong_cycle_detection(edges_neg_cycle, n, 0)
print("Wrong result (no cycle detection):", wrong_dist)
# Returns some finite values, claims everything is fine
# But dist[0], dist[1], dist[2] can be made arbitrarily negative
# by going around the cycle!

# How the wrong dist looks:
# After 3 iterations on 4-node graph:
# iter 1: dist = [0, 1, -1, 5]
# iter 2: dist = [0, -1, -3, 5] (going around cycle again)
# iter 3: dist = [0, -2, -4, 5] (still going!)
# Function returns [-2, -2, -4, 5] — these are MEANINGLESS
```

### RIGHT Code: Extra Pass Detects Negative Cycle

```python
def bellman_ford_correct(edges, n, src):
    """
    Correct Bellman-Ford with negative cycle detection.
    Returns (dist, True) if negative cycle exists affecting reachable nodes.
    """
    dist = [float('inf')] * n
    dist[src] = 0

    # V-1 iterations for shortest paths
    for i in range(n - 1):
        any_update = False
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                any_update = True
        if not any_update:
            break  # Converged early

    # ONE MORE PASS: if anything improves, negative cycle exists
    for u, v, w in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            # Found improvement after V-1 iterations → negative cycle!
            return dist, True

    return dist, False

# Test with negative cycle
edges_neg_cycle = [
    (0, 1, 1),
    (1, 2, -2),
    (2, 0, 0),
    (0, 3, 5),
]
dist, has_cycle = bellman_ford_correct(edges_neg_cycle, 4, 0)
print("Has negative cycle:", has_cycle)  # True ✓

# Test without negative cycle
edges_no_cycle = [
    (0, 1, 1),
    (0, 2, 4),
    (1, 2, 2),
    (1, 3, 5),
    (2, 3, -3),
]
dist, has_cycle = bellman_ford_correct(edges_no_cycle, 4, 0)
print("Has negative cycle:", has_cycle)  # False ✓
print("Distances:", dist)                # [0, 1, 3, 0] ✓


def bellman_ford_mark_negative_cycle(edges, n, src):
    """
    Advanced: mark all nodes affected by a negative cycle with -inf.
    """
    dist = [float('inf')] * n
    dist[src] = 0

    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w

    # Propagate -inf through negative cycle and all reachable nodes
    for _ in range(n):
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = float('-inf')  # Reachable via negative cycle

    return dist

dist_marked = bellman_ford_mark_negative_cycle(edges_neg_cycle, 4, 0)
print("Marked distances:", dist_marked)
# ['-inf', '-inf', '-inf', '-inf'] or similar
# All nodes reachable from the cycle are marked -inf
```

---

## Mistake 3: Topological Sort on a Graph with Cycles {#mistake-3}

### The Story

Topological sort is like scheduling tasks where some tasks must happen before others. If task A must happen before B, and B before C — fine. But if A must happen before B, and B before A — you're stuck. The schedule is impossible. Kahn's algorithm handles this by detecting when tasks are stuck (in-degree never reaches zero).

The mistake: ignoring the "did we process all nodes?" check at the end. If you skip it, you silently return a partial ordering that looks valid but isn't.

### WRONG Code: Kahn's Without Cycle Check

```python
from collections import deque

def topo_sort_wrong(n, edges):
    """
    Kahn's topological sort. BUG: doesn't check if all nodes were processed.
    """
    adj = [[] for _ in range(n)]
    in_degree = [0] * n

    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1

    queue = deque()
    for i in range(n):
        if in_degree[i] == 0:
            queue.append(i)

    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    # BUG: No check! If there's a cycle, 'order' is incomplete.
    # But we return it as if it's a valid topological order.
    return order

# Graph with cycle: 0→1→2→1 (cycle: 1→2→1)
# Plus: 0→3, 3→4
edges_with_cycle = [(0, 1), (1, 2), (2, 1), (0, 3), (3, 4)]
n = 5

wrong_order = topo_sort_wrong(n, edges_with_cycle)
print("Wrong topo order:", wrong_order)
# Returns [0, 3, 4] — only 3 of 5 nodes!
# The cycle (1, 2) is silently skipped.
# Caller might use this as a valid order: WRONG!

# The danger: if you're processing DAG-dependent operations,
# you'll skip tasks 1 and 2 entirely, with no error.
```

### RIGHT Code: Always Check Length of Result

```python
from collections import deque

def topo_sort_correct(n, edges):
    """
    Kahn's topological sort with cycle detection.
    Returns (order, has_cycle).
    """
    adj = [[] for _ in range(n)]
    in_degree = [0] * n

    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1

    queue = deque()
    for i in range(n):
        if in_degree[i] == 0:
            queue.append(i)

    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    # KEY CHECK: if we processed all n nodes, no cycle exists
    has_cycle = len(order) != n
    return order, has_cycle

# Test with cycle
order, has_cycle = topo_sort_correct(5, edges_with_cycle)
print("Has cycle:", has_cycle)   # True ✓
print("Partial order:", order)   # [0, 3, 4] — only processed 3 nodes

# Test without cycle
edges_dag = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)]
order, has_cycle = topo_sort_correct(5, edges_dag)
print("Has cycle:", has_cycle)   # False ✓
print("Topo order:", order)       # [0, 1, 2, 3, 4] or similar valid order

# The cycle detection logic explained:
# In a cycle, EVERY node in the cycle has in-degree >= 1 (from the other cycle nodes).
# None of them ever reach in-degree 0.
# So Kahn's queue never receives them.
# len(order) < n → cycle exists.
```

### Visualizing Why Cycles Block Progress

```
Graph: 0 → 1 → 2 → 1 (cycle between 1 and 2)
              ↓
              3 → 4

in_degree: [0, 1, 1, 1, 1]
                  ^   ^
                  |   |
           from cycle  from 1 or 3

Initial queue: [0] (only in-degree 0)
Process 0: remove 0, reduce in-degree of 1 to 0, queue 1. Also queue 3.
Process 1: remove 1, reduce in-degree of 2 to 0, queue 2.
Process 3: remove 3, reduce in-degree of 4 to 0, queue 4.
Process 2: remove 2, reduce in-degree of 1... but 1 already processed!
           Actually, 2 → 1 means in_degree[1] -= 1. But 1 already gone.

Wait, let me retrace with cycle 1→2→1:
in_degree: [0, 1, 1, 0, 1]
                        ^
                   in-degree of 3 is 0 (no incoming)

Queue: [0, 3]
Process 0: adj[0] = [1, 3]. in_degree[1]=1→0, queue 1. in_degree[3]=0→-1 (wait)

Actually: edges_with_cycle = [(0,1),(1,2),(2,1),(0,3),(3,4)]
in_degree: 0:0, 1:1(from 0 and 2)=2? No: from (0→1) and (2→1), so in_degree[1]=2
                2:1 (from 1→2), in_degree[2]=1
                3:1 (from 0→3), in_degree[3]=1
                4:1 (from 3→4), in_degree[4]=1
Wait: in_degree[0]=0. Queue: [0].
Process 0: push 1 (in_degree: 2→1), push 3 (in_degree: 1→0, queue [3]).
Process 3: push 4 (in_degree: 1→0, queue [4]).
Process 4: no outgoing.
Queue empty. order=[0,3,4]. len=3 ≠ 5. CYCLE DETECTED! ✓

Nodes 1 and 2 remain with in_degree > 0 (1 and 1 respectively)
because 2→1 and 1→2 keep each other's in_degrees alive.
```

---

## Mistake 4: Floyd-Warshall — Wrong Loop Order {#mistake-4}

### The Story

Floyd-Warshall finds shortest paths between ALL pairs of nodes. The insight is elegant: "Can I improve the path from i to j by going through node k?" If you try all intermediate nodes k, you get all shortest paths.

The catch: the `k` loop (the intermediate node) MUST be the outermost loop. Not innermost, not middle — outermost. Swapping loop order causes wrong results because you end up asking "does path i→j improve through node k?" before you've fully settled what paths go through nodes 0..k-1.

### WRONG Code: k Loop in Wrong Position

```python
def floyd_warshall_wrong(n, edges):
    """BUG: k loop is in the wrong position."""
    INF = float('inf')
    dist = [[INF] * n for _ in range(n)]

    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = w

    # BUG: i is outermost, k is innermost — WRONG ORDER!
    for i in range(n):
        for j in range(n):
            for k in range(n):  # k should be OUTERMOST, not innermost
                if dist[i][k] != INF and dist[k][j] != INF:
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

    return dist

def floyd_warshall_correct(n, edges):
    """Correct Floyd-Warshall: k is outermost loop."""
    INF = float('inf')
    dist = [[INF] * n for _ in range(n)]

    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = w

    # CORRECT: k is outermost
    for k in range(n):       # intermediate node
        for i in range(n):   # source
            for j in range(n): # destination
                if dist[i][k] != INF and dist[k][j] != INF:
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

    return dist


# 4-node example:
# 0 → 1 (weight 3)
# 0 → 2 (weight 8)
# 0 → 4 (does not exist here, using 4 nodes: 0,1,2,3)
# 1 → 3 (weight 1)
# 2 → 1 (weight 4)
# 3 → 0 (weight 2)
# 3 → 2 (weight -5)

edges = [
    (0, 1, 3),
    (0, 2, 8),
    (1, 3, 1),
    (2, 1, 4),
    (3, 0, 2),
    (3, 2, -5),
]
n = 4

wrong_result = floyd_warshall_wrong(n, edges)
correct_result = floyd_warshall_correct(n, edges)

print("Wrong dist[0][2]:", wrong_result[0][2])   # May be wrong
print("Correct dist[0][2]:", correct_result[0][2])  # Should be -1 (0→1→3→2)

# True shortest paths from 0:
# 0→0: 0
# 0→1: 3         (direct)
# 0→2: 3+1-5=-1  (0→1→3→2)
# 0→3: 3+1=4     (0→1→3)

print("\nCorrect all-pairs:")
for i in range(n):
    print(f"From {i}:", correct_result[i])
```

### Why Loop Order Matters: Intuition

```
Floyd-Warshall DP recurrence:
  dist[k][i][j] = min(dist[k-1][i][j], dist[k-1][i][k] + dist[k-1][k][j])

Meaning: "shortest path from i to j using only nodes {0, 1, ..., k} as intermediates"

When k is OUTERMOST:
  After iteration k=0: all paths using node 0 as intermediate are settled
  After iteration k=1: all paths using nodes {0,1} are settled
  ...
  After iteration k=n-1: all paths are settled

When k is INNERMOST (wrong):
  You're asking "does node k help i→j?" but dist[i][k] and dist[k][j]
  haven't been optimized yet for all intermediate nodes 0..k-1.
  You're trying to use intermediate node k before you know the best way
  to REACH node k!

It's like building a bridge — you must complete each support pillar
before laying the next span. Getting k order wrong is like trying to
use an incomplete pillar.
```

---

## Mistake 5: Kosaraju's SCC — Wrong DFS Direction {#mistake-5}

### The Story

Kosaraju's algorithm finds Strongly Connected Components (SCCs) in a directed graph. It's a two-DFS dance:
1. First DFS on the **original** graph to get finish-time ordering
2. Second DFS on the **reversed** graph in reverse finish-time order

The mistake: doing BOTH DFS passes on the original graph. Or reversing the order of passes. This gives wrong SCCs.

### Why the Reversed Graph?

```
If nodes A and B are in the same SCC:
  - Original graph: A can reach B AND B can reach A
  - Reversed graph: same (reversing all edges keeps A and B in the same SCC)

If A is in SCC_1 and B is in SCC_2, and there's an edge SCC_1 → SCC_2:
  - Original: from SCC_1 you can reach SCC_2
  - Reversed: from SCC_2 you can reach SCC_1

First DFS (original graph) gives finish order: nodes in "sink" SCCs
finish first (they have no outgoing edges in the SCC DAG).

Second DFS (reversed graph) starting from LAST-finished nodes:
  - In the reversed graph, the "sink" SCC of original becomes a "source"
  - Each DFS from a source explores exactly one SCC

If you do BOTH on original graph:
  Starting from the last-finished node in DFS2 might cross SCC boundaries!
```

### WRONG Code: Both DFS on Original Graph

```python
def kosaraju_wrong(n, adj):
    """BUG: Does second DFS on original graph instead of reversed graph."""
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

    # BUG: Should use reversed adjacency list!
    # This uses the ORIGINAL graph for DFS2
    visited = [False] * n
    sccs = []

    def dfs2_wrong(u, component):
        visited[u] = True
        component.append(u)
        for v in adj[u]:  # BUG: should be radj[u] (reversed graph)
            if not visited[v]:
                dfs2_wrong(v, component)

    for u in reversed(finish_order):
        if not visited[u]:
            component = []
            dfs2_wrong(u, component)
            sccs.append(component)

    return sccs

# 5-node SCC example:
# True SCCs: {0,1,2}, {3}, {4}
# Edges: 0→1, 1→2, 2→0 (cycle = SCC), 1→3, 3→4
adj = [
    [1],     # 0 → 1
    [2, 3],  # 1 → 2, 1 → 3
    [0],     # 2 → 0
    [4],     # 3 → 4
    []       # 4: sink
]

wrong_sccs = kosaraju_wrong(5, adj)
print("Wrong SCCs:", wrong_sccs)  # Will merge SCCs incorrectly
```

### RIGHT Code: Kosaraju with Reversed Graph

```python
def kosaraju_correct(n, adj):
    """
    Correct Kosaraju's SCC algorithm.
    adj: adjacency list for directed graph.
    """
    # Step 1: DFS on ORIGINAL graph, record finish order
    visited = [False] * n
    finish_order = []

    def dfs1(u):
        visited[u] = True
        for v in adj[u]:
            if not visited[v]:
                dfs1(v)
        finish_order.append(u)  # Add to order AFTER all descendants finished

    for i in range(n):
        if not visited[i]:
            dfs1(i)

    # Step 2: Build REVERSED graph
    radj = [[] for _ in range(n)]
    for u in range(n):
        for v in adj[u]:
            radj[v].append(u)  # Reverse edge: v → u instead of u → v

    # Step 3: DFS on REVERSED graph in reverse finish order
    visited = [False] * n
    sccs = []

    def dfs2(u, component):
        visited[u] = True
        component.append(u)
        for v in radj[u]:  # REVERSED graph ← the key difference
            if not visited[v]:
                dfs2(v, component)

    for u in reversed(finish_order):
        if not visited[u]:
            component = []
            dfs2(u, component)
            sccs.append(sorted(component))

    return sccs

# Test
adj = [
    [1],     # 0 → 1
    [2, 3],  # 1 → 2, 1 → 3
    [0],     # 2 → 0
    [4],     # 3 → 4
    []       # 4: sink
]

correct_sccs = kosaraju_correct(5, adj)
print("Correct SCCs:", sorted(correct_sccs))
# [[0, 1, 2], [3], [4]] ✓

# Larger example with 2 non-trivial SCCs:
adj2 = [
    [1],        # 0
    [2, 4],     # 1
    [0, 3],     # 2
    [],         # 3 (sink)
    [5],        # 4
    [4],        # 5 (4→5→4 cycle)
]
sccs2 = kosaraju_correct(6, adj2)
print("SCCs2:", sorted(sccs2))
# [{0,1,2}, {3}, {4,5}] ✓
```

---

## Mistake 6: Prim's vs Kruskal's Confusion {#mistake-6}

### The Story

Prim's algorithm grows a tree one vertex at a time, always adding the cheapest edge that connects a new vertex to the already-built tree. It's like growing a plant — you start from a root and expand outward, one branch at a time.

Kruskal's algorithm sorts ALL edges by weight and greedily picks the cheapest edge that doesn't create a cycle. It's like building a road network — you consider every possible road and pave the cheapest ones that connect new towns.

The confusion happens when people mix the two approaches: using edge-based logic inside Prim's (which should be vertex-based) or vertex-based logic inside Kruskal's (which should be edge-based).

### WRONG Code: Prim's with Edge-Based Logic (Kruskal's Thinking)

```python
# WRONG: Mixing Kruskal's edge-selection logic into Prim's framework

def prim_wrong(n, adj):
    """
    BUG: Sorts all edges globally (Kruskal thinking) but within Prim's structure.
    Missing the 'only connect to already-visited vertices' constraint.
    """
    import heapq

    # Collect all edges
    all_edges = []
    for u in range(n):
        for v, w in adj[u]:
            all_edges.append((w, u, v))
    all_edges.sort()  # BUG: Kruskal-style global sort, not Prim's local expansion

    in_mst = [False] * n
    in_mst[0] = True  # Start from node 0
    mst_edges = []
    mst_cost = 0

    # BUG: This picks cheapest edge overall, not cheapest edge from current tree
    for w, u, v in all_edges:
        if len(mst_edges) == n - 1:
            break
        # BUG: Doesn't properly check if one endpoint is in MST and other isn't
        if in_mst[u] and not in_mst[v]:
            mst_edges.append((u, v, w))
            in_mst[v] = True
            mst_cost += w
        # Missing: the edge might be u not in MST, v in MST (other direction)
        # Also missing: updating the priority queue as tree grows

    return mst_cost, mst_edges

# Test graph (5 nodes):
# 0-1: weight 2
# 0-3: weight 6
# 1-2: weight 3
# 1-3: weight 8
# 1-4: weight 5
# 2-4: weight 7
# 3-4: weight 9

adj = [
    [(1,2),(3,6)],
    [(0,2),(2,3),(3,8),(4,5)],
    [(1,3),(4,7)],
    [(0,6),(1,8),(4,9)],
    [(1,5),(2,7),(3,9)],
]

wrong_cost, wrong_edges = prim_wrong(5, adj)
print("Wrong Prim's MST cost:", wrong_cost)
# Might miss some optimal edges or include wrong ones
```

### RIGHT Code: Prim's (Vertex-Based, Priority Queue)

```python
def prim_correct(n, adj):
    """
    Correct Prim's MST algorithm.
    Uses min-heap on (weight, vertex) — vertex-based expansion.
    """
    import heapq

    in_mst = [False] * n
    min_edge = [float('inf')] * n  # cheapest edge to connect each vertex to MST
    parent = [-1] * n

    min_edge[0] = 0  # Start from vertex 0
    heap = [(0, 0)]  # (cost to include vertex, vertex)
    mst_cost = 0
    mst_edges = []

    while heap:
        w, u = heapq.heappop(heap)

        if in_mst[u]:
            continue  # Already in MST (stale entry)

        in_mst[u] = True
        mst_cost += w
        if parent[u] != -1:
            mst_edges.append((parent[u], u, w))

        # Expand: look at all neighbors of u
        for v, weight in adj[u]:
            if not in_mst[v] and weight < min_edge[v]:
                min_edge[v] = weight
                parent[v] = u
                heapq.heappush(heap, (weight, v))

    return mst_cost, mst_edges


def kruskal_correct(n, edges):
    """
    Correct Kruskal's MST algorithm.
    Uses Union-Find + sorted edges — edge-based.
    edges: list of (u, v, weight)
    """
    edges.sort(key=lambda x: x[2])  # Sort by weight

    parent = list(range(n))
    rank = [0] * n

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])  # Path compression
        return parent[x]

    def union(x, y):
        px, py = find(x), find(y)
        if px == py:
            return False  # Same component — would create cycle
        if rank[px] < rank[py]:
            px, py = py, px
        parent[py] = px
        if rank[px] == rank[py]:
            rank[px] += 1
        return True

    mst_cost = 0
    mst_edges = []

    for u, v, w in edges:
        if union(u, v):  # Add edge if it doesn't create cycle
            mst_cost += w
            mst_edges.append((u, v, w))
            if len(mst_edges) == n - 1:
                break

    return mst_cost, mst_edges


# Test both on same graph
adj = [
    [(1,2),(3,6)],
    [(0,2),(2,3),(3,8),(4,5)],
    [(1,3),(4,7)],
    [(0,6),(1,8),(4,9)],
    [(1,5),(2,7),(3,9)],
]
edges_list = [(0,1,2),(0,3,6),(1,2,3),(1,3,8),(1,4,5),(2,4,7),(3,4,9)]

prim_cost, prim_edges = prim_correct(5, adj)
kruskal_cost, kruskal_edges = kruskal_correct(5, edges_list)

print("Prim's MST cost:", prim_cost)      # Should be 2+3+5+6=16... let me verify
print("Kruskal's MST cost:", kruskal_cost) # Same result

# MST should include: 0-1(2), 1-2(3), 1-4(5), 0-3(6) = 16
print("Prim edges:", prim_edges)
print("Kruskal edges:", kruskal_edges)
```

---

## Mistake 7: BFS/DFS on Disconnected Graph {#mistake-7}

### The Story

You're searching a building for a missing person. You start at the front door and check every room connected to the front door. But the building has a completely separate wing with its own entrance. You finish your search and say "no one found" — but you never checked the other wing!

Graphs can be disconnected: multiple components with no edges between them. Starting BFS/DFS from a single node only visits the component that node belongs to.

### WRONG Code: Single-Source BFS

```python
from collections import deque

def bfs_wrong_disconnected(adj, n):
    """BUG: Only visits nodes reachable from node 0."""
    visited = [False] * n
    order = []

    # BUG: Starting from only node 0
    queue = deque([0])
    visited[0] = True

    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                queue.append(v)

    return order

# Disconnected graph: component {0,1,2} and component {3,4}
adj_disconnected = [
    [1, 2],  # 0 connects to 1, 2
    [0],     # 1 connects to 0
    [0],     # 2 connects to 0
    [4],     # 3 connects to 4 (separate component!)
    [3],     # 4 connects to 3
]

wrong_order = bfs_wrong_disconnected(adj_disconnected, 5)
print("Wrong BFS order:", wrong_order)  # [0, 1, 2] — misses nodes 3 and 4!
print("Nodes missed:", set(range(5)) - set(wrong_order))  # {3, 4}
```

### RIGHT Code: Multi-Source BFS for Disconnected Graph

```python
from collections import deque

def bfs_correct_disconnected(adj, n):
    """
    Correct BFS for potentially disconnected graphs.
    Starts a new BFS from each unvisited node.
    """
    visited = [False] * n
    all_components = []

    for start in range(n):
        if visited[start]:
            continue  # Already visited in a previous component

        # BFS from this unvisited starting node
        component = []
        queue = deque([start])
        visited[start] = True

        while queue:
            u = queue.popleft()
            component.append(u)
            for v in adj[u]:
                if not visited[v]:
                    visited[v] = True
                    queue.append(v)

        all_components.append(component)

    return all_components

adj_disconnected = [
    [1, 2],
    [0],
    [0],
    [4],
    [3],
]

components = bfs_correct_disconnected(adj_disconnected, 5)
print("Components:", components)  # [[0, 1, 2], [3, 4]] ✓

# Applications of this pattern:
# - Counting connected components
# - Checking if graph is connected
# - Finding all islands in a grid (2D BFS)

def count_components(adj, n):
    visited = [False] * n
    count = 0
    for i in range(n):
        if not visited[i]:
            count += 1
            # DFS/BFS from i
            stack = [i]
            while stack:
                u = stack.pop()
                if visited[u]:
                    continue
                visited[u] = True
                for v in adj[u]:
                    if not visited[v]:
                        stack.append(v)
    return count

print("Number of components:", count_components(adj_disconnected, 5))  # 2 ✓
```

---

## Mistake 8: Directed vs Undirected Adjacency List {#mistake-8}

### The Story

Imagine a highway system. You're building a map. You add "road from A to B" and forget that you can also drive from B to A. Now your GPS thinks B is a dead end.

In undirected graphs, every edge is bidirectional. When building the adjacency list, you must add BOTH directions. Missing this means DFS/BFS from some nodes can't "go back" — half the graph becomes unreachable from certain starting points.

### WRONG Code: Missing Reverse Edge

```python
def build_undirected_wrong(n, edges):
    """BUG: Only adds one direction for undirected graph."""
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)   # BUG: Only u→v, not v→u!
    return adj

edges = [(0,1), (0,2), (1,3), (2,3), (3,4)]
adj_wrong = build_undirected_wrong(5, edges)

# adj_wrong:
# 0: [1, 2]
# 1: [3]       ← Can't go 1→0!
# 2: [3]       ← Can't go 2→0!
# 3: [4]       ← Can't go 3→1 or 3→2!
# 4: []        ← DEAD END! Can't go anywhere from 4!

def dfs_from(adj, start, n):
    visited = set()
    stack = [start]
    while stack:
        u = stack.pop()
        if u in visited: continue
        visited.add(u)
        for v in adj[u]:
            if v not in visited:
                stack.append(v)
    return visited

# DFS from node 4 on wrong graph
reachable_from_4 = dfs_from(adj_wrong, 4, 5)
print("Reachable from 4 (wrong adj):", reachable_from_4)  # {4} — only itself!

# DFS from node 0 on wrong graph (one direction works fine)
reachable_from_0 = dfs_from(adj_wrong, 0, 5)
print("Reachable from 0 (wrong adj):", reachable_from_0)  # {0,1,2,3,4} fine

# The asymmetry is the bug: "reachable" depends on direction of data entry
```

### RIGHT Code: Both Directions for Undirected Graph

```python
def build_undirected_correct(n, edges, weighted=False):
    """
    Correct undirected graph: add BOTH directions.
    """
    adj = [[] for _ in range(n)]

    if weighted:
        for u, v, w in edges:
            adj[u].append((v, w))  # u → v with weight w
            adj[v].append((u, w))  # v → u with weight w (bidirectional!)
    else:
        for u, v in edges:
            adj[u].append(v)  # u → v
            adj[v].append(u)  # v → u ← THE MISSING LINE IN WRONG CODE

    return adj

edges = [(0,1), (0,2), (1,3), (2,3), (3,4)]
adj_correct = build_undirected_correct(5, edges)

# adj_correct:
# 0: [1, 2]
# 1: [0, 3]    ← Now 1 can go back to 0
# 2: [0, 3]    ← Now 2 can go back to 0
# 3: [1, 2, 4] ← Now 3 can go back to 1 and 2
# 4: [3]       ← Now 4 can go to 3

reachable_from_4 = dfs_from(adj_correct, 4, 5)
print("Reachable from 4 (correct adj):", reachable_from_4)  # {0,1,2,3,4} ✓

reachable_from_2 = dfs_from(adj_correct, 2, 5)
print("Reachable from 2 (correct adj):", reachable_from_2)  # {0,1,2,3,4} ✓

# For DIRECTED graphs, add only ONE direction:
def build_directed_correct(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)   # Only u→v (directed!)
    return adj
```

---

## Mistake 9: Stale Entries in Dijkstra's Priority Queue {#mistake-9}

### The Story

You're managing a task queue. A task comes in: "Deliver package to house 5, distance 10." You add it to your queue. Later, you find a better route: "Deliver to house 5, distance 3." You add THAT to the queue too. Now the old entry (distance 10) is still sitting in the queue. When it eventually gets processed, you re-process house 5 unnecessarily — or worse, overwrite the correct answer with a wrong one.

Python's `heapq` doesn't support updating priorities. So you can't remove the old (10, 5) entry. The solution: when you pop an entry, check if it's stale (the recorded distance is worse than what's already known). If so, skip it.

### WRONG Code: Processing Stale Entries

```python
import heapq

def dijkstra_stale_wrong(graph, src, n):
    """BUG: Processes stale heap entries, causing extra work and wrong answers."""
    dist = [float('inf')] * n
    dist[src] = 0
    heap = [(0, src)]

    while heap:
        d, u = heapq.heappop(heap)

        # BUG: No check for stale entry!
        # If d > dist[u], this is an old entry — we've already found better.
        # Without this check, we re-process u and re-relax all its neighbors.

        for v, w in graph[u]:
            new_dist = d + w  # BUG: Using stale d, not dist[u]
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))

    return dist

# Graph where many updates happen:
graph = {
    0: [(1, 10), (2, 3)],
    1: [(3, 2)],
    2: [(1, 4), (3, 8)],
    3: []
}

# Trace:
# Initial: heap=[(0,0)], dist=[0,inf,inf,inf]
# Pop (0,0): relax 1 to 10, relax 2 to 3. heap=[(3,2),(10,1)]
# Pop (3,2): relax 1 to min(10, 3+4)=7, relax 3 to 3+8=11.
#            heap=[(7,1),(10,1),(11,3)]
# Pop (7,1): relax 3 to min(11, 7+2)=9. heap=[(9,3),(10,1),(11,3)]
# Pop (9,3): no neighbors. heap=[(10,1),(11,3)]
# Pop (10,1): NO STALE CHECK! d=10, dist[1]=7. Re-relaxes 3!
#             new_dist = 10+2 = 12. Is 12 < dist[3]=9? No. OK here.
#             But for a bigger graph with more stale entries, this causes
#             O(E^2) work instead of O(E log V)

# The real danger: if stale entry has d <= dist[u] but d != dist[u],
# which happens when dist was updated after this entry was pushed.
# Without the check: O(E^2) in worst case (exponential slowdown!)

dist_wrong = dijkstra_stale_wrong(graph, 0, 4)
print("Result (may be correct but slow):", dist_wrong)
```

### RIGHT Code: Skip Stale Entries

```python
import heapq

def dijkstra_correct(graph, src, n):
    """
    Correct Dijkstra: always skip stale heap entries.
    O((V + E) log V) time complexity.
    """
    dist = [float('inf')] * n
    dist[src] = 0
    heap = [(0, src)]

    while heap:
        d, u = heapq.heappop(heap)

        # KEY CHECK: Skip stale entry
        # If d > dist[u], we already found a shorter path to u.
        # This entry is outdated — skip it!
        if d > dist[u]:
            continue

        for v, w in graph[u]:
            new_dist = dist[u] + w  # Use current best dist, not stale d
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))

    return dist

# Test
graph = {
    0: [(1, 10), (2, 3)],
    1: [(3, 2)],
    2: [(1, 4), (3, 8)],
    3: []
}

dist = dijkstra_correct(graph, 0, 4)
print("Distances from 0:", dist)  # [0, 7, 3, 9] ✓

# Why this is critical for performance:
# Without stale check: heap can grow to O(E) entries
#   Each entry processed: O(log E) work
#   Total: O(E log E) but can degrade to O(E^2) in adversarial cases
#   (keep pushing stale entries that trigger more pushes)
#
# With stale check: each VERTEX processed at most once
#   Total: O((V + E) log V) — true Dijkstra complexity

# Demonstration of heap size with/without stale skip:
def dijkstra_count_pops(graph, src, n, skip_stale):
    dist = [float('inf')] * n
    dist[src] = 0
    heap = [(0, src)]
    pops = 0

    while heap:
        d, u = heapq.heappop(heap)
        pops += 1
        if skip_stale and d > dist[u]:
            continue
        for v, w in graph[u]:
            new_dist = dist[u] + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))

    return pops

pops_with_skip    = dijkstra_count_pops(graph, 0, 4, skip_stale=True)
pops_without_skip = dijkstra_count_pops(graph, 0, 4, skip_stale=False)
print(f"Pops with stale skip: {pops_with_skip}")    # Fewer
print(f"Pops without skip:    {pops_without_skip}") # More (processes stale entries)
```

---

## Mistake 10: Union-Find for Directed Graph Cycle Detection {#mistake-10}

### The Story

Union-Find is perfect for detecting cycles in undirected graphs. Think of it as a "same team?" check: if two nodes are already on the same team (same component), adding an edge between them creates a cycle.

But in a directed graph, direction matters. An edge A→B is not the same as B→A. Union-Find doesn't track direction — it just says "same set or not." This means it can falsely claim a directed graph has a cycle when it doesn't, or miss a cycle entirely.

The correct tool for directed cycle detection: DFS with WHITE/GRAY/BLACK node coloring.
- WHITE: not yet visited
- GRAY: currently in DFS stack (visited but not yet finished)
- BLACK: completely finished

A cycle in a directed graph corresponds to encountering a GRAY node during DFS.

### WRONG Code: Union-Find for Directed Graph

```python
def has_cycle_directed_wrong(n, edges):
    """
    BUG: Uses Union-Find for DIRECTED graph cycle detection.
    Union-Find treats edges as undirected — gives wrong answers.
    """
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px == py:
            return True  # "Cycle detected" — but this might be wrong!
        parent[px] = py
        return False

    for u, v in edges:
        if union(u, v):
            return True  # False positive possible!
    return False

# Example: directed graph with no cycle
# 0 → 1, 1 → 2, 0 → 2
# This is a DAG (no cycle)! 0→2 and 0→1→2 are two paths, not a cycle.
dag_edges = [(0, 1), (1, 2), (0, 2)]
print("DAG has cycle (Union-Find, wrong):", has_cycle_directed_wrong(3, dag_edges))
# Returns True — FALSE POSITIVE!
# Union-Find sees: 0-1 same set? No, unite. 1-2 same set? No, unite. 0-2 same set? YES!
# But there's NO cycle in this directed graph!

# Example: directed graph WITH a cycle
# 0 → 1, 1 → 2, 2 → 0
cycle_edges = [(0, 1), (1, 2), (2, 0)]
print("Cycle graph (Union-Find):", has_cycle_directed_wrong(3, cycle_edges))
# Returns True — correct result, but for the wrong reason
```

### RIGHT Code: DFS with WHITE/GRAY/BLACK Coloring

```python
def has_cycle_directed_correct(n, edges):
    """
    Correct directed cycle detection using DFS with coloring.
    WHITE = 0 (unvisited)
    GRAY  = 1 (in current DFS path)
    BLACK = 2 (fully processed)

    A back edge (to a GRAY node) means a cycle exists.
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n

    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)

    def dfs(u):
        color[u] = GRAY  # Mark as "in progress"

        for v in adj[u]:
            if color[v] == GRAY:
                return True  # Back edge: cycle detected!
            if color[v] == WHITE:
                if dfs(v):  # Recurse into unvisited neighbor
                    return True

        color[u] = BLACK  # Mark as "done"
        return False

    for i in range(n):
        if color[i] == WHITE:
            if dfs(i):
                return True

    return False

# Test the DAG (no cycle)
dag_edges = [(0, 1), (1, 2), (0, 2)]
print("DAG has cycle (DFS coloring):", has_cycle_directed_correct(3, dag_edges))
# False ✓ (correct! Union-Find gave wrong answer)

# Test the cycle
cycle_edges = [(0, 1), (1, 2), (2, 0)]
print("Cycle has cycle (DFS coloring):", has_cycle_directed_correct(3, cycle_edges))
# True ✓

# Test a more complex case
# 0→1, 1→2, 2→3, 3→1 (cycle 1→2→3→1), 0→4 (no cycle here)
complex_edges = [(0,1),(1,2),(2,3),(3,1),(0,4)]
print("Complex has cycle:", has_cycle_directed_correct(5, complex_edges))
# True ✓ (cycle: 1→2→3→1)

# Visualize the coloring:
# DFS from 0:
#   color[0]=GRAY
#   Visit 1:
#     color[1]=GRAY
#     Visit 2:
#       color[2]=GRAY
#       Visit 3:
#         color[3]=GRAY
#         Visit 1: color[1]==GRAY → CYCLE! Return True

# For undirected: Union-Find is simpler and correct
def has_cycle_undirected_correct(n, edges):
    """Union-Find works correctly for UNDIRECTED graphs."""
    parent = list(range(n))
    rank = [0] * n

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        px, py = find(x), find(y)
        if px == py:
            return True  # Cycle!
        if rank[px] < rank[py]: px, py = py, px
        parent[py] = px
        if rank[px] == rank[py]: rank[px] += 1
        return False

    for u, v in edges:
        if union(u, v):
            return True
    return False

# Same DAG edges but treating as UNDIRECTED:
# 0-1, 1-2, 0-2 → forms triangle → has cycle in undirected sense
print("DAG as undirected (Union-Find):", has_cycle_undirected_correct(3, dag_edges))
# True ← correct for undirected interpretation (triangle is a cycle)
```

### Summary: Which Tool for Which Graph?

```
╔═══════════════════════════════════════════════════════════════════╗
║           CYCLE DETECTION — TOOL SELECTION GUIDE                 ║
╠══════════════════╦════════════════╦══════════════════════════════╣
║ Graph Type       ║ Correct Tool   ║ Why                          ║
╠══════════════════╬════════════════╬══════════════════════════════╣
║ Undirected       ║ Union-Find     ║ No direction to track;       ║
║                  ║                ║ same-set = cycle             ║
╠══════════════════╬════════════════╬══════════════════════════════╣
║ Directed         ║ DFS + coloring ║ Need to detect back edges;  ║
║                  ║ (WHITE/GRAY/   ║ direction matters for cycle  ║
║                  ║  BLACK)        ║ detection                    ║
╠══════════════════╬════════════════╬══════════════════════════════╣
║ Directed with    ║ Kahn's topo    ║ If topo sort doesn't process ║
║ toposort needed  ║ sort           ║ all nodes, cycle exists      ║
╚══════════════════╩════════════════╩══════════════════════════════╝
```

---

## Final Quick Reference: All 10 Mistakes

```
╔══════════════════════════════════════════════════════════════════════════╗
║           ADVANCED GRAPHS — COMMON MISTAKES QUICK REFERENCE             ║
╠═══════╦══════════════════════════════════════╦════════════════════════╣
║  #    ║ Mistake                              ║ Fix                     ║
╠═══════╬══════════════════════════════════════╬════════════════════════╣
║  1    ║ Dijkstra with negative edges         ║ Use Bellman-Ford        ║
╠═══════╬══════════════════════════════════════╬════════════════════════╣
║  2    ║ Bellman-Ford stops at V-1 iter       ║ One extra pass to       ║
║       ║ (misses negative cycle)              ║ detect neg cycle        ║
╠═══════╬══════════════════════════════════════╬════════════════════════╣
║  3    ║ Topo sort ignores len(order) != n    ║ Always check length     ║
╠═══════╬══════════════════════════════════════╬════════════════════════╣
║  4    ║ Floyd-Warshall: k not outermost      ║ k must be outermost     ║
╠═══════╬══════════════════════════════════════╬════════════════════════╣
║  5    ║ Kosaraju: second DFS on orig graph   ║ Second DFS on REVERSED  ║
╠═══════╬══════════════════════════════════════╬════════════════════════╣
║  6    ║ Mixing Prim's and Kruskal's logic    ║ Prim: vertex+heap;      ║
║       ║                                      ║ Kruskal: edge+DSU       ║
╠═══════╬══════════════════════════════════════╬════════════════════════╣
║  7    ║ Single-source on disconnected graph  ║ Outer loop over all     ║
║       ║                                      ║ unvisited nodes         ║
╠═══════╬══════════════════════════════════════╬════════════════════════╣
║  8    ║ Missing reverse edge in undirected   ║ Add both u→v AND v→u    ║
╠═══════╬══════════════════════════════════════╬════════════════════════╣
║  9    ║ Not skipping stale Dijkstra entries  ║ if d > dist[u]: continue║
╠═══════╬══════════════════════════════════════╬════════════════════════╣
║  10   ║ Union-Find for directed cycle        ║ DFS WHITE/GRAY/BLACK    ║
╚═══════╩══════════════════════════════════════╩════════════════════════╝
```

---

*Graph algorithms are tricky precisely because the bugs are often silent. The algorithm runs to completion, produces a result, and only a test case you carefully designed reveals the error. Every mistake above has burned programmers in real interviews. Keep this list close.*
