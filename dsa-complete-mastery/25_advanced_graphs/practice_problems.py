# =============================================================================
# MODULE 25 — ADVANCED GRAPHS: Practice Problems
# =============================================================================
# Run: python3 practice_problems.py
#
# Covers: Dijkstra's shortest path, Bellman-Ford (negative edges),
#         Floyd-Warshall (all-pairs), Kruskal's MST, Prim's MST,
#         topological sort (Kahn's algorithm),
#         strongly connected components (Kosaraju's)
#
# Algorithm selection cheat-sheet:
#   Non-negative weights, single source   → Dijkstra  O(E log V)
#   Negative weights / detect neg-cycle   → Bellman-Ford  O(VE)
#   All-pairs shortest path               → Floyd-Warshall  O(V³)
#   Minimum spanning tree, edge-centric   → Kruskal  O(E log E)
#   Minimum spanning tree, node-centric   → Prim  O(E log V)
#   Dependency ordering (DAG)             → Topological sort (Kahn's)  O(V+E)
#   Mutual reachability groups            → SCC (Kosaraju's)  O(V+E)
# =============================================================================

import heapq
from collections import deque, defaultdict


# =============================================================================
# PROBLEM 1 — Dijkstra's Shortest Path (non-negative weights)
# =============================================================================
#
# Given a weighted directed graph and a source node, return the shortest
# distance from source to every other node.
#
# Key idea: greedy BFS with a priority queue (min-heap).
#   - Always process the currently closest unvisited node.
#   - When we pop a node, its distance is FINAL (no shorter path can exist
#     because all edge weights are non-negative).
#
# Why does greedy work?
#   If all weights >= 0, a node's distance can only increase as we add more
#   edges.  The node at the top of the heap already has the smallest known
#   distance, so it must be optimal.
#
# Adjacency list format: graph[u] = [(v, weight), ...]
#
# Time:  O((V + E) log V)
# Space: O(V + E)
# =============================================================================

def dijkstra(graph, n, source):
    """
    Shortest distances from source to all nodes using Dijkstra's algorithm.

    graph: dict {node: [(neighbour, weight), ...]}
    n: number of nodes (labeled 0..n-1)
    Returns: dist list where dist[v] = shortest distance from source to v

    >>> g = {0:[(1,4),(2,1)], 1:[(3,1)], 2:[(1,2),(3,5)], 3:[]}
    >>> dijkstra(g, 4, 0)
    [0, 3, 1, 4]
    """
    dist = [float('inf')] * n
    dist[source] = 0
    heap = [(0, source)]   # (distance, node)

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue    # stale entry — a shorter path was already found
        for v, weight in graph.get(u, []):
            new_dist = dist[u] + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))

    return dist


# =============================================================================
# PROBLEM 2 — Bellman-Ford (handles negative edge weights)
# =============================================================================
#
# Find shortest paths from source, even with negative edge weights.
# Also detect negative cycles (where no shortest path is well-defined).
#
# Key idea: relax ALL edges V-1 times.
#   A shortest path with no cycles visits at most V-1 edges (it can't revisit
#   a node in an optimal path).  After V-1 relaxations, all shortest paths are
#   correctly set.
#
# Negative cycle detection:
#   Run a V-th relaxation pass.  If ANY distance decreases, a negative cycle
#   exists (you could loop it forever to get arbitrarily small distances).
#
# Edge list format: [(u, v, weight), ...]
#
# Time:  O(V * E)
# Space: O(V)
# =============================================================================

def bellman_ford(n, edges, source):
    """
    Shortest distances from source using Bellman-Ford.
    Returns (dist, has_negative_cycle).

    n: number of nodes (0..n-1)
    edges: list of (u, v, weight)

    >>> d, neg = bellman_ford(5, [(0,1,6),(0,2,7),(1,2,8),(1,3,-4),(2,4,-3),(3,0,2),(4,3,7)], 0)
    >>> d[3]
    -2
    >>> neg
    False
    """
    dist = [float('inf')] * n
    dist[source] = 0

    # V-1 relaxation passes
    for _ in range(n - 1):
        updated = False
        for u, v, weight in edges:
            if dist[u] != float('inf') and dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                updated = True
        if not updated:
            break   # early exit: no changes means all shortest paths found

    # V-th pass to detect negative cycle
    has_negative_cycle = False
    for u, v, weight in edges:
        if dist[u] != float('inf') and dist[u] + weight < dist[v]:
            has_negative_cycle = True
            break

    return dist, has_negative_cycle


# =============================================================================
# PROBLEM 3 — Floyd-Warshall (all-pairs shortest paths)
# =============================================================================
#
# Compute shortest distances between EVERY pair of nodes simultaneously.
#
# Key idea: dynamic programming with intermediate node relaxation.
#   dist[i][j] = shortest path from i to j using only nodes 0..k as intermediates.
#   For each new intermediate node k, update:
#       dist[i][j] = min(dist[i][j],  dist[i][k] + dist[k][j])
#                      direct so far    go through k
#
# After iterating k over all nodes, dist[i][j] holds the true shortest path.
#
# When to use:
#   - V is small (typically V <= 400-500; O(V³) is feasible)
#   - You need all-pairs distances, not just single-source
#
# Negative cycle: if dist[i][i] < 0 for any i after completion.
#
# Time:  O(V³)
# Space: O(V²)
# =============================================================================

def floyd_warshall(n, edges):
    """
    All-pairs shortest paths using Floyd-Warshall.

    n: number of nodes (0..n-1)
    edges: list of (u, v, weight)
    Returns dist matrix, or None if a negative cycle is detected.

    >>> dist = floyd_warshall(4, [(0,1,3),(1,2,1),(2,3,2),(0,3,10)])
    >>> dist[0][3]
    6
    >>> dist[0][0]
    0
    """
    INF = float('inf')
    dist = [[INF] * n for _ in range(n)]

    for i in range(n):
        dist[i][i] = 0

    for u, v, weight in edges:
        dist[u][v] = min(dist[u][v], weight)   # handle parallel edges

    # Relax through every intermediate node k
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    # Detect negative cycle: a negative self-loop would mean infinite negative path
    for i in range(n):
        if dist[i][i] < 0:
            return None

    return dist


# =============================================================================
# PROBLEM 4 — Kruskal's Minimum Spanning Tree
# =============================================================================
#
# Connect all n nodes with minimum total edge weight (no cycles).
# Edge-centric: sort edges, greedily add cheapest edge that doesn't form cycle.
# Cycle check: Union-Find (DSU).
#
# Best when: graph is sparse (few edges relative to nodes).
#
# Time:  O(E log E) — dominated by sort
# Space: O(V) for DSU
# =============================================================================

class _UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank   = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True


def kruskal_mst(n, edges):
    """
    Kruskal's MST. edges = [(weight, u, v), ...]
    Returns (total_weight, mst_edge_list).

    >>> w, e = kruskal_mst(4, [(1,0,1),(2,1,3),(3,1,2),(4,0,2),(5,2,3)])
    >>> w
    6
    >>> len(e)
    3
    """
    uf = _UnionFind(n)
    mst_weight = 0
    mst_edges  = []
    for weight, u, v in sorted(edges):       # sort ascending by weight
        if uf.union(u, v):
            mst_weight += weight
            mst_edges.append((weight, u, v))
            if len(mst_edges) == n - 1:
                break
    return mst_weight, mst_edges


# =============================================================================
# PROBLEM 5 — Prim's Minimum Spanning Tree
# =============================================================================
#
# Build MST by starting from one node and always expanding via the cheapest
# edge that leaves the current tree.
# Node-centric: use a min-heap to track the cheapest edge to each unvisited node.
#
# Best when: graph is dense (many edges; E close to V²).
#
# Approach:
#   1. Start: push (0, source) onto heap; dist[source] = 0.
#   2. Pop minimum-cost node u not yet in MST.
#   3. Add u's cost to MST weight.
#   4. Relax all neighbours of u: if cheaper path found, push to heap.
#   5. Repeat until all nodes visited.
#
# Time:  O(E log V) with binary heap
# Space: O(V + E)
# =============================================================================

def prim_mst(graph, n):
    """
    Prim's MST starting from node 0.

    graph: dict {node: [(neighbour, weight), ...]}
    Returns (total_weight, edges_in_mst)

    >>> g = {0:[(1,2),(3,6)], 1:[(0,2),(2,3),(3,8),(4,5)],
    ...      2:[(1,3),(4,7)], 3:[(0,6),(1,8),(4,9)], 4:[(1,5),(2,7),(3,9)]}
    >>> w, _ = prim_mst(g, 5)
    >>> w
    16
    """
    in_mst  = [False] * n
    min_cost = [float('inf')] * n
    parent  = [-1] * n
    min_cost[0] = 0
    heap = [(0, 0)]     # (cost, node)
    total_weight = 0
    mst_edges    = []

    while heap:
        cost, u = heapq.heappop(heap)
        if in_mst[u]:
            continue    # already processed — stale heap entry
        in_mst[u] = True
        total_weight += cost
        if parent[u] != -1:
            mst_edges.append((cost, parent[u], u))

        for v, weight in graph.get(u, []):
            if not in_mst[v] and weight < min_cost[v]:
                min_cost[v] = weight
                parent[v]   = u
                heapq.heappush(heap, (weight, v))

    return total_weight, mst_edges


# =============================================================================
# PROBLEM 6 — Topological Sort (Kahn's Algorithm / BFS)
# =============================================================================
#
# Given a directed acyclic graph (DAG), produce a linear ordering of nodes
# such that for every edge u → v, u appears before v.
#
# Kahn's algorithm (BFS-based):
#   1. Compute in-degree (number of incoming edges) for every node.
#   2. Seed a queue with all nodes of in-degree 0 (no prerequisites).
#   3. Process queue: pop a node, add to order, decrement neighbours' in-degrees.
#      When a neighbour's in-degree hits 0, add it to the queue.
#   4. If result has all V nodes → valid topological order.
#      If result has fewer → graph has a cycle (no valid topological sort).
#
# Common use cases: build systems, course prerequisites, task scheduling.
#
# Time:  O(V + E)
# Space: O(V)
# =============================================================================

def topological_sort_kahns(graph, n):
    """
    Kahn's topological sort on a directed graph.

    graph: dict {node: [neighbours]}
    n: number of nodes (labeled 0..n-1)
    Returns: ordered list, or [] if cycle detected.

    >>> topological_sort_kahns({0:[1,2], 1:[3], 2:[3], 3:[]}, 4)
    [0, 1, 2, 3]
    >>> topological_sort_kahns({0:[1], 1:[2], 2:[0]}, 3)
    []
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

    return order if len(order) == n else []    # shorter → cycle exists


# =============================================================================
# PROBLEM 7 — Strongly Connected Components (Kosaraju's Algorithm)
# =============================================================================
#
# Find all Strongly Connected Components (SCCs) in a directed graph.
# An SCC is a maximal set of nodes where every node can reach every other node.
#
# Kosaraju's algorithm (two DFS passes):
#   Pass 1: Run DFS on the original graph, push nodes to a stack in FINISH order.
#           Nodes that finish last have the most outgoing connectivity.
#   Pass 2: Reverse all edges.  Process nodes from the stack (most-finished first).
#           Each DFS on the reversed graph from an unvisited node discovers exactly
#           one SCC (because the reversed edges now "can't escape" the component).
#
# Why does reversing work?
#   In the original graph, if you can reach B from A, in the reversed graph you
#   can reach A from B.  An SCC looks the same after reversal (it's mutually
#   reachable in both directions).  Running DFS in reverse from the highest-finish
#   node ensures you stay within that SCC.
#
# Time:  O(V + E) — two DFS passes
# Space: O(V + E) — for reversed graph + visited sets
# =============================================================================

def kosaraju_scc(graph, n):
    """
    Find all Strongly Connected Components using Kosaraju's algorithm.

    graph: dict {node: [neighbours]}
    n: number of nodes (0..n-1)
    Returns: list of SCCs, each SCC is a list of node indices.

    >>> sccs = kosaraju_scc({0:[1], 1:[2], 2:[0], 3:[1]}, 4)
    >>> sorted([sorted(s) for s in sccs])
    [[0, 1, 2], [3]]
    """
    visited = [False] * n
    finish_stack = []

    # --- Pass 1: DFS on original graph, record finish order ---
    def dfs1(u):
        visited[u] = True
        for v in graph.get(u, []):
            if not visited[v]:
                dfs1(v)
        finish_stack.append(u)   # push AFTER all neighbours are done

    for i in range(n):
        if not visited[i]:
            dfs1(i)

    # --- Build reversed graph ---
    rev_graph = defaultdict(list)
    for u in range(n):
        for v in graph.get(u, []):
            rev_graph[v].append(u)   # reverse direction of every edge

    # --- Pass 2: DFS on reversed graph in reverse finish order ---
    visited2 = [False] * n
    sccs = []

    def dfs2(u, component):
        visited2[u] = True
        component.append(u)
        for v in rev_graph.get(u, []):
            if not visited2[v]:
                dfs2(v, component)

    while finish_stack:
        node = finish_stack.pop()    # process in reverse finish order
        if not visited2[node]:
            scc = []
            dfs2(node, scc)
            sccs.append(scc)

    return sccs


# =============================================================================
# TEST RUNNER
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MODULE 25 — ADVANCED GRAPHS: Practice Problems")
    print("=" * 60)

    # --- Problem 1: Dijkstra ---
    print("\n[1] Dijkstra's Shortest Path")
    g1 = {0: [(1,4),(2,1)], 1: [(3,1)], 2: [(1,2),(3,5)], 3: []}
    dist1 = dijkstra(g1, 4, 0)
    print(f"  Graph: {g1}")
    print(f"  Distances from 0: {dist1}")
    assert dist1 == [0, 3, 1, 4], dist1
    # Unreachable node
    g2 = {0: [(1,2)], 1: [], 2: []}
    dist2 = dijkstra(g2, 3, 0)
    assert dist2[2] == float('inf')
    print("  All assertions passed.")

    # --- Problem 2: Bellman-Ford ---
    print("\n[2] Bellman-Ford (Negative Edges)")
    edges_bf = [(0,1,6),(0,2,7),(1,2,8),(1,3,-4),(2,4,-3),(3,0,2),(4,3,7)]
    d_bf, neg = bellman_ford(5, edges_bf, 0)
    print(f"  Distances from 0: {d_bf}")
    print(f"  Negative cycle: {neg}")
    assert d_bf[3] == 2    # 0→2→4→3: 7+(-3)+7=11, but 0→1→3: 6+(-4)=2
    assert d_bf[4] == 4    # 0→2→4: 7+(-3)=4
    # Negative cycle detection
    neg_cycle_edges = [(0,1,1),(1,2,-3),(2,0,1)]
    _, has_neg = bellman_ford(3, neg_cycle_edges, 0)
    assert has_neg == True
    print("  All assertions passed.")

    # --- Problem 3: Floyd-Warshall ---
    print("\n[3] Floyd-Warshall (All-Pairs Shortest Paths)")
    fw_edges = [(0,1,3),(1,2,1),(2,3,2),(0,3,10)]
    dist_fw = floyd_warshall(4, fw_edges)
    print(f"  dist[0][3] = {dist_fw[0][3]} (expected 6 via 0→1→2→3)")
    assert dist_fw[0][3] == 6
    assert dist_fw[0][0] == 0
    assert dist_fw[1][0] == float('inf')   # no path back in directed graph
    # Negative cycle returns None
    assert floyd_warshall(2, [(0,1,-1),(1,0,-1)]) is None
    print("  All assertions passed.")

    # --- Problem 4: Kruskal's MST ---
    print("\n[4] Kruskal's Minimum Spanning Tree")
    kr_edges = [(1,0,1),(2,1,3),(3,1,2),(4,0,2),(5,2,3)]
    w_kr, e_kr = kruskal_mst(4, kr_edges)
    print(f"  MST weight: {w_kr}, edges: {e_kr}")
    assert w_kr == 6
    assert len(e_kr) == 3
    print("  All assertions passed.")

    # --- Problem 5: Prim's MST ---
    print("\n[5] Prim's Minimum Spanning Tree")
    pr_graph = {
        0: [(1,2),(3,6)],
        1: [(0,2),(2,3),(3,8),(4,5)],
        2: [(1,3),(4,7)],
        3: [(0,6),(1,8),(4,9)],
        4: [(1,5),(2,7),(3,9)],
    }
    w_pr, e_pr = prim_mst(pr_graph, 5)
    print(f"  MST weight: {w_pr}, edges: {e_pr}")
    assert w_pr == 16
    assert len(e_pr) == 4
    print("  All assertions passed.")

    # --- Problem 6: Topological Sort ---
    print("\n[6] Topological Sort (Kahn's Algorithm)")
    dag = {0:[1,2], 1:[3], 2:[3], 3:[]}
    order = topological_sort_kahns(dag, 4)
    print(f"  DAG: {dag}")
    print(f"  Topological order: {order}")
    # Validate order: every edge u->v should have u before v
    pos = {node: i for i, node in enumerate(order)}
    for u in dag:
        for v in dag[u]:
            assert pos[u] < pos[v], f"Order violation: {u} should be before {v}"
    assert topological_sort_kahns({0:[1],1:[2],2:[0]}, 3) == []   # cycle
    print("  All assertions passed.")

    # --- Problem 7: Kosaraju's SCC ---
    print("\n[7] Strongly Connected Components (Kosaraju's)")
    scc_graph = {0:[1], 1:[2], 2:[0], 3:[1,4], 4:[5], 5:[3]}
    sccs = kosaraju_scc(scc_graph, 6)
    print(f"  SCCs: {[sorted(s) for s in sccs]}")
    assert len(sccs) == 2
    scc_sets = [frozenset(s) for s in sccs]
    assert frozenset([0,1,2]) in scc_sets
    assert frozenset([3,4,5]) in scc_sets
    # Single-node graph
    single = kosaraju_scc({0:[]}, 1)
    assert single == [[0]]
    print("  All assertions passed.")

    print("\n" + "=" * 60)
    print("All problems completed successfully.")
    print("=" * 60)
