# =============================================================================
# MODULE 24 — DISJOINT SET UNION (UNION-FIND): Practice Problems
# =============================================================================
# Run: python3 practice_problems.py
#
# Covers: connected components, cycle detection in undirected graph,
#         number of islands (union-find approach), accounts merge,
#         redundant connection, minimum spanning tree (Kruskal's)
#
# Mental model: group leader system.
#   Each group has a representative (root/leader).
#   find(x) → who is x's leader?
#   union(a, b) → merge a and b's groups under one leader.
#
# Two critical optimisations:
#   1. Path compression  → flatten tree during find, making future finds O(1)
#   2. Union by rank     → always attach smaller tree under larger, keeping tree flat
#   Together: near O(1) per operation, formally O(α(n)) (inverse Ackermann)
# =============================================================================


# =============================================================================
# BASE UNION-FIND CLASS (used by all problems below)
# =============================================================================

class UnionFind:
    """
    Generic Union-Find with path compression and union by rank.

    Supports:
      find(x)           → return root/representative of x's component
      union(x, y)       → merge components of x and y; return False if already same
      connected(x, y)   → True if x and y are in the same component
      num_components    → number of distinct components
    """

    def __init__(self, n):
        """
        Initialise n elements, each as its own component.
        parent[i] = i  (self-loop means i is its own root)
        rank[i]   = 0  (height of the sub-tree rooted at i)
        """
        self.parent = list(range(n))    # parent[i] = i initially
        self.rank   = [0] * n
        self.num_components = n

    def find(self, x):
        """
        Return root of x with PATH COMPRESSION.
        While traversing to the root, point every visited node directly to root.
        This flattens the tree so future finds are O(1).
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # recursive compression
        return self.parent[x]

    def union(self, x, y):
        """
        Merge components of x and y using UNION BY RANK.
        The smaller-rank tree attaches under the larger-rank tree.
        Returns True if they were in different components (merge happened).
        """
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False    # already in the same component — no merge
        # Attach smaller tree under larger tree
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx    # ensure rx has the higher rank
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1     # only increase rank when merging equal-rank trees
        self.num_components -= 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)


# =============================================================================
# PROBLEM 1 — Connected Components
# =============================================================================
#
# Given n nodes (0-indexed) and a list of edges, count the number of connected
# components in the undirected graph.
#
# Approach: start with n components (everyone isolated).
#   For each edge (u, v), union the two components.
#   Every successful union reduces component count by 1.
#
# Time:  O(n + E · α(n)) ≈ O(n + E)
# Space: O(n)
# =============================================================================

def count_connected_components(n, edges):
    """
    Count connected components in an undirected graph.

    >>> count_connected_components(5, [[0,1],[1,2],[3,4]])
    2
    >>> count_connected_components(5, [])
    5
    >>> count_connected_components(4, [[0,1],[1,2],[2,3]])
    1
    """
    uf = UnionFind(n)
    for u, v in edges:
        uf.union(u, v)
    return uf.num_components


# =============================================================================
# PROBLEM 2 — Cycle Detection in Undirected Graph
# =============================================================================
#
# Given n nodes and edges, determine if a cycle exists.
#
# Key insight: when we try to union two nodes that are ALREADY in the same
# component, adding that edge would create a cycle.
#
# Why DSU instead of DFS here?
#   DFS is O(V+E) but requires visited tracking.
#   DSU is equally fast but also supports dynamic edge additions.
#
# Time:  O(E · α(n))
# Space: O(n)
# =============================================================================

def has_cycle_undirected(n, edges):
    """
    Return True if the undirected graph contains a cycle.

    >>> has_cycle_undirected(4, [[0,1],[1,2],[2,0]])
    True
    >>> has_cycle_undirected(4, [[0,1],[1,2],[2,3]])
    False
    >>> has_cycle_undirected(1, [])
    False
    """
    uf = UnionFind(n)
    for u, v in edges:
        if not uf.union(u, v):
            # union returned False → u and v already connected → cycle!
            return True
    return False


# =============================================================================
# PROBLEM 3 — Number of Islands (Union-Find approach)
# =============================================================================
#
# Given a 2D grid of '1' (land) and '0' (water), count the number of islands.
#
# Classic BFS/DFS solution is O(m*n). DSU solution is equally fast but
# shows how to apply DSU to a 2D grid.
#
# Encoding 2D → 1D: cell (r, c) maps to node r * cols + c.
#
# Approach:
#   1. Count initial land cells as starting component count.
#   2. For each land cell, union it with its land neighbours (right + down only
#      to avoid double-processing).
#   3. Answer = num_components at the end.
#
# Time:  O(m * n · α(m*n))
# Space: O(m * n)
# =============================================================================

def num_islands(grid):
    """
    Count islands in a binary grid using Union-Find.

    >>> num_islands([["1","1","1"],["0","1","0"],["0","0","0"]])
    1
    >>> num_islands([["1","0","1"],["0","0","0"],["1","0","1"]])
    4
    >>> num_islands([])
    0
    """
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])

    # Count land cells; water cells won't be part of DSU operations
    land_count = sum(grid[r][c] == '1' for r in range(rows) for c in range(cols))
    uf = UnionFind(rows * cols)
    # Adjust component count to reflect only land cells initially
    # (water cells are in their own "components" but we don't care about them)
    uf.num_components = land_count

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '0':
                continue
            cell = r * cols + c
            # Check right neighbour
            if c + 1 < cols and grid[r][c + 1] == '1':
                uf.union(cell, r * cols + (c + 1))
            # Check bottom neighbour
            if r + 1 < rows and grid[r + 1][c] == '1':
                uf.union(cell, (r + 1) * cols + c)

    return uf.num_components


# =============================================================================
# PROBLEM 4 — Accounts Merge
# =============================================================================
#
# Given a list of accounts where account[i] = [name, email1, email2, ...],
# merge accounts that share at least one email address.
# Return merged accounts sorted alphabetically within each group.
#
# Approach:
#   - Treat each account index as a node.
#   - Map every email to the first account index that owns it.
#   - When a second account claims the same email, union the two accounts.
#   - Finally, group all emails by root account and sort.
#
# Time:  O(N·k · α(N)) where N = accounts, k = avg emails per account
# Space: O(N·k)
# =============================================================================

from collections import defaultdict

def accounts_merge(accounts):
    """
    Merge accounts sharing at least one email.

    >>> result = accounts_merge([
    ...     ["Alice", "a@x.com", "b@x.com"],
    ...     ["Bob",   "c@x.com"],
    ...     ["Alice", "b@x.com", "d@x.com"]
    ... ])
    >>> len(result)
    2
    >>> sorted(result[0][1:]) == ["a@x.com", "b@x.com", "d@x.com"] or \
        sorted(result[0][1:]) == ["c@x.com"]
    True
    """
    uf = UnionFind(len(accounts))
    email_to_account = {}   # email → first account index that claimed it

    for i, account in enumerate(accounts):
        for email in account[1:]:          # skip name at index 0
            if email in email_to_account:
                uf.union(i, email_to_account[email])  # merge the two account nodes
            else:
                email_to_account[email] = i

    # Group emails by their root account
    root_to_emails = defaultdict(set)
    for email, acc_idx in email_to_account.items():
        root = uf.find(acc_idx)
        root_to_emails[root].add(email)

    result = []
    for root, emails in root_to_emails.items():
        name = accounts[root][0]
        result.append([name] + sorted(emails))

    return result


# =============================================================================
# PROBLEM 5 — Redundant Connection
# =============================================================================
#
# Given n nodes labeled 1..n and n edges (one more than a tree needs),
# find the edge that, if removed, turns the graph into a tree.
# If multiple valid answers exist, return the last one in the input.
#
# A tree has n-1 edges and is connected with no cycles.
# The "redundant" edge is the one whose addition creates the first cycle.
#
# Approach: process edges in order; use DSU to detect cycle.
#   The first edge that tries to connect two already-connected nodes is redundant.
#
# Time:  O(n · α(n))
# Space: O(n)
# =============================================================================

def find_redundant_connection(edges):
    """
    Return the last edge that creates a cycle.

    >>> find_redundant_connection([[1,2],[1,3],[2,3]])
    [2, 3]
    >>> find_redundant_connection([[1,2],[2,3],[3,4],[1,4],[1,5]])
    [1, 4]
    """
    n = len(edges)
    uf = UnionFind(n + 1)   # nodes labeled 1..n, so size n+1

    for u, v in edges:
        if not uf.union(u, v):
            return [u, v]    # this edge created a cycle

    return []   # should never reach here if input is valid


# =============================================================================
# PROBLEM 6 — Minimum Spanning Tree (Kruskal's Algorithm)
# =============================================================================
#
# Given a weighted undirected graph, find the minimum spanning tree (MST).
# Return the total weight and the list of edges in the MST.
#
# MST: connects all n nodes with n-1 edges at minimum total weight.
#
# Kruskal's algorithm:
#   1. Sort all edges by weight (ascending).
#   2. Greedily add the next cheapest edge IF it doesn't create a cycle.
#      (Use DSU to check: if both endpoints already connected → skip.)
#   3. Stop when n-1 edges added (MST complete).
#
# Why does the greedy choice work?
#   The Cut Property: for any cut of the graph, the minimum-weight crossing edge
#   must be in SOME MST. Kruskal exploits this repeatedly.
#
# Time:  O(E log E) for sorting + O(E · α(V)) for DSU = O(E log E)
# Space: O(V) for DSU
# =============================================================================

def kruskal_mst(n, edges):
    """
    Find MST of an undirected weighted graph using Kruskal's algorithm.

    n: number of nodes (labeled 0..n-1)
    edges: list of (weight, u, v)
    Returns: (total_weight, mst_edges)

    >>> w, e = kruskal_mst(4, [(1,0,1),(4,0,2),(3,1,2),(2,1,3),(5,2,3)])
    >>> w
    6
    >>> len(e)
    3
    """
    uf = UnionFind(n)
    sorted_edges = sorted(edges)   # sort by weight (first element of tuple)
    mst_weight = 0
    mst_edges  = []

    for weight, u, v in sorted_edges:
        if uf.union(u, v):
            # No cycle: include this edge in the MST
            mst_weight += weight
            mst_edges.append((weight, u, v))
            if len(mst_edges) == n - 1:
                break   # MST complete: a tree on n nodes has exactly n-1 edges

    return mst_weight, mst_edges


# =============================================================================
# TEST RUNNER
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MODULE 24 — DISJOINT SET UNION: Practice Problems")
    print("=" * 60)

    # --- Problem 1: Connected Components ---
    print("\n[1] Connected Components")
    n, edges = 6, [[0,1],[1,2],[3,4]]
    cc = count_connected_components(n, edges)
    print(f"  n={n}, edges={edges}")
    print(f"  Components: {cc}")
    assert cc == 3    # {0,1,2}, {3,4}, {5}
    assert count_connected_components(5, []) == 5
    assert count_connected_components(4, [[0,1],[1,2],[2,3]]) == 1
    print("  All assertions passed.")

    # --- Problem 2: Cycle Detection ---
    print("\n[2] Cycle Detection in Undirected Graph")
    edges_cycle    = [[0,1],[1,2],[2,0]]
    edges_no_cycle = [[0,1],[1,2],[2,3]]
    print(f"  {edges_cycle}    → cycle: {has_cycle_undirected(4, edges_cycle)}")
    print(f"  {edges_no_cycle} → cycle: {has_cycle_undirected(4, edges_no_cycle)}")
    assert has_cycle_undirected(4, edges_cycle) == True
    assert has_cycle_undirected(4, edges_no_cycle) == False
    assert has_cycle_undirected(1, []) == False
    print("  All assertions passed.")

    # --- Problem 3: Number of Islands ---
    print("\n[3] Number of Islands (Union-Find)")
    grid1 = [["1","1","0","0"],
             ["1","1","0","0"],
             ["0","0","1","0"],
             ["0","0","0","1"]]
    grid2 = [["1","0","1"],["0","0","0"],["1","0","1"]]
    print(f"  Grid 1 islands: {num_islands(grid1)}")
    print(f"  Grid 2 islands: {num_islands(grid2)}")
    assert num_islands(grid1) == 3
    assert num_islands(grid2) == 4
    assert num_islands([]) == 0
    print("  All assertions passed.")

    # --- Problem 4: Accounts Merge ---
    print("\n[4] Accounts Merge")
    accs = [
        ["Alice", "a@x.com", "b@x.com"],
        ["Bob",   "c@x.com"],
        ["Alice", "b@x.com", "d@x.com"],
    ]
    merged = accounts_merge(accs)
    print(f"  Input accounts: {accs}")
    print(f"  Merged result:  {merged}")
    assert len(merged) == 2   # Alice's two accounts merge; Bob stays separate
    # Find Alice's merged account
    alice = next(a for a in merged if a[0] == "Alice")
    assert sorted(alice[1:]) == ["a@x.com", "b@x.com", "d@x.com"]
    print("  All assertions passed.")

    # --- Problem 5: Redundant Connection ---
    print("\n[5] Redundant Connection")
    e1 = [[1,2],[1,3],[2,3]]
    e2 = [[1,2],[2,3],[3,4],[1,4],[1,5]]
    print(f"  {e1} → redundant: {find_redundant_connection(e1)}")
    print(f"  {e2} → redundant: {find_redundant_connection(e2)}")
    assert find_redundant_connection(e1) == [2, 3]
    assert find_redundant_connection(e2) == [1, 4]
    print("  All assertions passed.")

    # --- Problem 6: Kruskal's MST ---
    print("\n[6] Minimum Spanning Tree (Kruskal's)")
    # Graph: 4 nodes, 5 edges (weight, u, v)
    graph_edges = [(1,0,1),(4,0,2),(3,1,2),(2,1,3),(5,2,3)]
    total_w, mst = kruskal_mst(4, graph_edges)
    print(f"  Edges: {graph_edges}")
    print(f"  MST weight: {total_w}, MST edges: {mst}")
    assert total_w == 6       # edges (0-1,w=1), (1-3,w=2), (1-2,w=3)
    assert len(mst) == 3
    # Larger example — verify MST connects all nodes
    w2, e2 = kruskal_mst(5, [(2,0,1),(3,0,3),(1,1,2),(5,2,3),(4,3,4)])
    assert w2 == 10    # edges (1,2 w=1),(0,1 w=2),(0,3 w=3),(3,4 w=4)
    assert len(e2) == 4
    print("  All assertions passed.")

    print("\n" + "=" * 60)
    print("All problems completed successfully.")
    print("=" * 60)
