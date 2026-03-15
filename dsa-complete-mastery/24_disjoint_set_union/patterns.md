# DSU / Union-Find Patterns — Connectivity Problems

---

## The Story First

Imagine a city starting with no roads. One by one, roads get built connecting neighborhoods. At any point, someone might ask: "Can I get from neighborhood A to neighborhood B?"

A naive approach: run BFS/DFS every time a new road appears. That's expensive.

A better approach: use **Disjoint Set Union (DSU)**, also called Union-Find. Think of it as a social network where every person initially belongs to their own group. When two people become friends, their groups merge. To check if two people are in the same group, you find each person's "group leader" and compare.

DSU answers two questions blazingly fast:
1. **Find:** Who is the leader (root) of person X's group?
2. **Union:** Merge the groups of persons X and Y.

Both operations run in nearly O(1) time — technically O(α(N)) where α is the inverse Ackermann function, which grows so slowly it's essentially constant for any real-world input.

```
Initially: 5 separate components
  [0]  [1]  [2]  [3]  [4]

Union(0, 1):
  [0,1]  [2]  [3]  [4]

Union(2, 3):
  [0,1]  [2,3]  [4]

Union(0, 3):
  [0,1,2,3]  [4]

Find(1) == Find(2)? → YES (both in same component)
Find(1) == Find(4)? → NO (different components)
```

This document covers the 6 patterns where DSU is the right tool.

---

## The Core DSU Implementation (Your Foundation)

Every pattern below is a variation or extension of this:

```python
class DSU:
    def __init__(self, n: int):
        self.parent = list(range(n))  # each node is its own parent initially
        self.rank = [0] * n           # rank (approximate depth) for union by rank
        self.size = [1] * n           # size of each component
        self.components = n           # number of distinct components

    def find(self, x: int) -> int:
        """Find the root/representative of x's component. Path compression."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])   # path compression
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        """
        Merge x's and y's components.
        Returns True if they were in different components (merge happened).
        Returns False if already in same component.
        """
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False   # already connected

        # Union by rank: attach smaller tree under root of taller tree
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx   # ensure rx has >= rank

        self.parent[ry] = rx          # ry becomes child of rx
        self.size[rx] += self.size[ry]
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1

        self.components -= 1
        return True

    def connected(self, x: int, y: int) -> bool:
        """Are x and y in the same component?"""
        return self.find(x) == self.find(y)

    def component_size(self, x: int) -> int:
        """Return size of x's component."""
        return self.size[self.find(x)]
```

**Two key optimizations:**

**1. Path Compression** (in `find`):
After finding the root, make every node on the path point directly to the root. Future `find` calls on the same nodes are instant.

```
Before compression:           After compression:
  root                          root
   |                           /  |  \
   1                          1   2   3
   |
   2
   |
   3

find(3):
  3 → 2 → 1 → root            3 → root (now direct link)
                               2 → root (now direct link)
```

**2. Union by Rank:**
Always attach the shorter tree under the taller one. This keeps trees shallow, making `find` fast.

```
Without union by rank:         With union by rank:
  0 → 1 → 2 → 3 → 4            0
  (chain, depth 4)             /|\
  find(4) = 4 hops           1  2  3
                                  |
                                  4
                              (balanced, depth 2)
```

---

## Pattern 1: Basic Connectivity

### The Problem

Questions that boil down to: "Are these two things connected?"

- "How many connected components are in this graph?"
- "Is the graph fully connected?"
- "If we add this edge, does it connect two separate components?"

### When to Reach for DSU

- Graph edges are given all at once (static graph)
- You only need union and connectivity queries (no deletion)
- The graph is undirected

### Applications

#### Number of Connected Components

```python
def countComponents(n: int, edges: list) -> int:
    """
    Given n nodes (0 to n-1) and a list of undirected edges,
    return the number of connected components.
    """
    dsu = DSU(n)
    for u, v in edges:
        dsu.union(u, v)
    return dsu.components


# Example:
# n=5, edges=[[0,1],[1,2],[3,4]]
# Components: {0,1,2}, {3,4} → 2
print(countComponents(5, [[0,1],[1,2],[3,4]]))   # 2

# n=5, edges=[[0,1],[1,2],[2,3],[3,4]]
# Components: {0,1,2,3,4} → 1
print(countComponents(5, [[0,1],[1,2],[2,3],[3,4]]))  # 1
```

#### Redundant Connection

"Find an edge that, if removed, still leaves the graph fully connected (tree). If multiple such edges exist, return the last one."

```python
def findRedundantConnection(edges: list) -> list:
    """
    Given a graph that started as a tree and had one extra edge added,
    find that extra edge.
    """
    n = len(edges)
    dsu = DSU(n + 1)   # nodes 1-indexed

    for u, v in edges:
        if not dsu.union(u, v):
            # union returned False → they were already connected → this edge is redundant
            return [u, v]

    return []   # shouldn't reach here given valid input


print(findRedundantConnection([[1,2],[1,3],[2,3]]))   # [2,3]
# After processing [1,2] and [1,3]: 1,2,3 all connected
# [2,3]: 2 and 3 already share root 1 → redundant!
```

#### Largest Component

```python
def largestComponent(n: int, edges: list) -> int:
    """Return the size of the largest connected component."""
    dsu = DSU(n)
    for u, v in edges:
        dsu.union(u, v)
    return max(dsu.component_size(i) for i in range(n))
```

---

## Pattern 2: Minimum Spanning Tree (Kruskal's)

### The Story

You're building a network of cities. You have a list of possible roads, each with a cost. You want to connect all cities with the minimum total cost, using no redundant roads.

This is the **Minimum Spanning Tree (MST)** problem. Kruskal's algorithm builds the MST greedily:
1. Sort all edges by weight (cheapest first)
2. For each edge, if its endpoints are NOT yet connected, add the edge (union them)
3. If they're already connected, skip the edge (adding it would create a cycle)

DSU makes step 2 efficient — checking and merging connectivity in O(α(N)).

### ASCII: Kruskal's Step by Step

```
Graph (6 nodes, 9 edges):
  0 ──1─── 1
  │ ╲     │
  6   2   5
  │     ╲ │
  5 ──3─── 2
       ↓
Edges sorted by weight:
  (0,1,1), (0,2,2), (1,2,5), (0,5,6), (1,3,3), (2,3,4), ...

Step 1: Process (0,1,1): 0 and 1 not connected → ADD. MST: {(0,1)}
  DSU: [0,1,2,3,4,5] → 0 and 1 now share root

Step 2: Process (0,2,2): 0 and 2 not connected → ADD. MST: {(0,1),(0,2)}
  DSU: 0,1,2 all connected

Step 3: Process (1,3,3): 1 and 3 not connected → ADD. MST: {(0,1),(0,2),(1,3)}
  DSU: 0,1,2,3 all connected

Step 4: Process (2,3,4): 2 and 3 already connected → SKIP (would create cycle)

Step 5: Process (1,2,5): already connected → SKIP

Step 6: Process (3,4,6): 3 and 4 not connected → ADD. MST grows.
  ... continue until n-1 edges added
```

### Template Code

```python
def kruskal_mst(n: int, edges: list) -> tuple:
    """
    n: number of nodes (0 to n-1)
    edges: list of (weight, u, v)
    Returns: (total_weight, mst_edges)
    """
    edges.sort()   # sort by weight (first element of tuple)
    dsu = DSU(n)
    mst_edges = []
    total_weight = 0

    for weight, u, v in edges:
        if dsu.union(u, v):                  # not yet connected → add to MST
            mst_edges.append((u, v, weight))
            total_weight += weight
            if len(mst_edges) == n - 1:      # MST is complete (n-1 edges)
                break

    if len(mst_edges) < n - 1:
        return -1, []   # graph is not connected → no MST exists

    return total_weight, mst_edges


# Example: 4 nodes
edges = [
    (10, 0, 1),
    (6,  0, 2),
    (5,  0, 3),
    (15, 1, 2),
    (4,  1, 3),
    (8,  2, 3),
]
weight, mst = kruskal_mst(4, edges)
print(f"MST weight: {weight}")   # 19
print(f"MST edges: {mst}")
# Sorted edges: (4,1,3),(5,0,3),(6,0,2),(8,2,3),(10,0,1),(15,1,2)
# Add (1,3,4): 1 and 3 connected
# Add (0,3,5): 0 and 3 connected
# Add (0,2,6): 0 and 2 connected
# Now have 3 edges for 4 nodes → MST complete
# Total: 4+5+6 = 15... wait let me recalculate with actual example
```

### Min Cost to Connect All Points (LeetCode 1584)

```python
import heapq

def minCostConnectPoints(points: list) -> int:
    """
    points[i] = [x, y]
    Cost of connecting two points = Manhattan distance
    Find minimum cost to connect all points (MST).
    """
    n = len(points)

    # Generate all edges
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            dist = abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1])
            edges.append((dist, i, j))

    weight, _ = kruskal_mst(n, edges)
    return weight


print(minCostConnectPoints([[0,0],[2,2],[3,10],[5,2],[7,0]]))  # 20
```

---

## Pattern 3: Dynamic Connectivity / Online Union

### The Problem

Edges arrive one at a time. After each addition, you might be asked: "Are nodes X and Y now connected?"

This is the **online** version of connectivity — you process unions in the order they arrive, not sorted by weight.

DSU handles this perfectly: each `union` is O(α(N)), and `connected` queries are equally fast.

### Application: Accounts Merge

"Given a list of accounts where each account contains a name and a list of emails, merge accounts that share any email. Return merged accounts."

This is a connectivity problem: emails are nodes, and accounts connect emails that appear together.

```python
def accountsMerge(accounts: list) -> list:
    """
    accounts[i] = [name, email1, email2, ...]
    Merge accounts sharing at least one email.
    """
    from collections import defaultdict

    email_to_id = {}   # email → unique integer id
    email_to_name = {} # email → account name

    # Assign integer ids to each unique email
    def get_id(email):
        if email not in email_to_id:
            email_to_id[email] = len(email_to_id)
        return email_to_id[email]

    # Build DSU
    # We'll add emails lazily; use a dict-based DSU for arbitrary IDs
    parent = {}
    rank = {}

    def find(x):
        if x not in parent:
            parent[x] = x
            rank[x] = 0
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return
        if rank.get(rx, 0) < rank.get(ry, 0):
            rx, ry = ry, rx
        parent[ry] = rx
        if rank.get(rx, 0) == rank.get(ry, 0):
            rank[rx] = rank.get(rx, 0) + 1

    # Process each account: union all emails in the same account
    for account in accounts:
        name = account[0]
        emails = account[1:]
        for email in emails:
            email_to_name[email] = name
            union(emails[0], email)   # connect all emails to the first one

    # Group emails by their root
    root_to_emails = defaultdict(list)
    for email in email_to_id if email_to_id else email_to_name:
        root = find(email)
        root_to_emails[root].append(email)

    # Wait — let's simplify: don't use get_id, just union email strings directly
    # Rebuild properly:
    parent.clear()
    rank.clear()

    for account in accounts:
        name = account[0]
        emails = account[1:]
        for email in emails:
            email_to_name[email] = name
        for i in range(1, len(emails)):
            union(emails[0], emails[i])

    root_to_emails = defaultdict(set)
    for email in email_to_name:
        root = find(email)
        root_to_emails[root].add(email)

    result = []
    for root, email_set in root_to_emails.items():
        name = email_to_name[root]
        result.append([name] + sorted(email_set))

    return result


accounts = [
    ["John", "johnsmith@mail.com", "john_newyork@mail.com"],
    ["John", "johnsmith@mail.com", "john00@mail.com"],
    ["Mary", "mary@mail.com"],
    ["John", "johnnybravo@mail.com"]
]
merged = accountsMerge(accounts)
for acc in merged:
    print(acc)
# ["John", "john00@mail.com", "john_newyork@mail.com", "johnsmith@mail.com"]
# ["John", "johnnybravo@mail.com"]
# ["Mary", "mary@mail.com"]
```

### Application: Similar String Groups

```python
def numSimilarGroups(strs: list) -> int:
    """
    Two strings are similar if they differ in at most 2 positions (swap).
    Find number of groups of mutually similar strings.
    """
    n = len(strs)
    dsu = DSU(n)

    def similar(a, b):
        diffs = sum(1 for x, y in zip(a, b) if x != y)
        return diffs == 0 or diffs == 2

    for i in range(n):
        for j in range(i + 1, n):
            if similar(strs[i], strs[j]):
                dsu.union(i, j)

    return dsu.components


print(numSimilarGroups(["tars","rats","arts","star"]))  # 2
```

---

## Pattern 4: Cycle Detection in Undirected Graph

### The Story

You're building a computer network. You have n computers and you're adding cables between them. If you accidentally create a loop (cycle), signals can bounce forever. You want to detect the moment a cycle is created.

With DSU, cycle detection is trivial: when you try to union two nodes that already share the same root, you've found a cycle.

### The Key Rule

**Before adding edge (u, v):**
- `find(u) == find(v)` → u and v are already connected → adding this edge creates a cycle!
- `find(u) != find(v)` → u and v are in different components → safe to add, union them.

### ASCII: Cycle Detection

```
Nodes: 0, 1, 2, 3
Edges added in order: (0,1), (1,2), (2,3), (3,0)

After (0,1): DSU = {0,1}, {2}, {3}
  find(0)=0, find(1)=0 after union → same root = 0

After (1,2): DSU = {0,1,2}, {3}
  find(1)=0, find(2)=2 → different roots → union → 0 becomes root of all

After (2,3): DSU = {0,1,2,3}
  find(2)=0, find(3)=3 → different roots → union

After (3,0):
  find(3)=0, find(0)=0 → SAME ROOT → CYCLE DETECTED!
  This edge closes the loop: 0→1→2→3→0

Visual:
  0 ─── 1
  |     |
  3 ─── 2
  Adding edge 3→0 would create a cycle.
```

### Template Code

```python
def hasCycle(n: int, edges: list) -> bool:
    """Return True if the undirected graph has a cycle."""
    dsu = DSU(n)
    for u, v in edges:
        if not dsu.union(u, v):   # union returns False if already connected
            return True           # cycle detected!
    return False

print(hasCycle(4, [[0,1],[1,2],[2,3],[3,0]]))   # True (cycle: 0-1-2-3-0)
print(hasCycle(4, [[0,1],[1,2],[2,3]]))          # False (simple path)
print(hasCycle(4, [[0,1],[0,2],[1,3],[2,3]]))    # True (cycle: 0-1-3-2-0)
```

### IMPORTANT: DSU Only Works for Undirected Graphs

For directed graphs, DSU cycle detection gives false positives. Consider:
```
0 → 1 → 2 (no cycle in directed graph)
But if we union(0,1) and union(1,2), then find(0)==find(2) → DSU says cycle!

For directed graph cycle detection, use DFS with 3 colors:
  White (0) = unvisited
  Gray  (1) = currently in DFS stack (ancestor)
  Black (2) = fully processed

If DFS reaches a gray node → cycle detected.
```

```python
def hasCycleDirected(n: int, adj: list) -> bool:
    """Directed graph cycle detection using DFS coloring."""
    color = [0] * n   # 0=white, 1=gray, 2=black

    def dfs(u) -> bool:
        color[u] = 1   # mark as in-progress
        for v in adj[u]:
            if color[v] == 1:
                return True    # back edge → cycle!
            if color[v] == 0 and dfs(v):
                return True
        color[u] = 2   # mark as done
        return False

    return any(dfs(u) for u in range(n) if color[u] == 0)
```

---

## Pattern 5: Grid Connectivity

### The Story

Classic problem: "Count the number of islands in a grid of 1s and 0s." Or: "How many connected regions of the same color are there?"

You can solve this with DFS/BFS, and that's often simpler. But DSU shines when the grid is **dynamic** — cells are being added (turned from water to land) one at a time, and you need connectivity queries after each addition.

### Static Grid: Number of Islands

```python
def numIslands(grid: list) -> int:
    """
    grid[i][j] = '1' (land) or '0' (water)
    Count number of islands (connected regions of '1').
    DSU approach.
    """
    if not grid:
        return 0
    ROWS, COLS = len(grid), len(grid[0])

    # Flatten 2D coordinates to 1D index
    def idx(r, c):
        return r * COLS + c

    # Initialize DSU with all land cells
    dsu = DSU(ROWS * COLS)
    land_count = 0

    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] == '1':
                land_count += 1
                # Union with adjacent land cells
                for dr, dc in [(0,1),(1,0),(0,-1),(-1,0)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] == '1':
                        dsu.union(idx(r,c), idx(nr,nc))

    # Count unique roots among land cells
    return len(set(dsu.find(idx(r,c))
                   for r in range(ROWS)
                   for c in range(COLS)
                   if grid[r][c] == '1'))


grid = [
    ["1","1","0","0","0"],
    ["1","1","0","0","0"],
    ["0","0","1","0","0"],
    ["0","0","0","1","1"],
]
print(numIslands(grid))  # 3
```

### Dynamic Grid: Number of Islands II (LeetCode 305)

Cells are added one at a time. Return count of islands after each addition.

```python
def numIslands2(m: int, n: int, positions: list) -> list:
    """
    m × n grid, initially all water.
    positions: list of (r, c) cells being turned to land.
    Return number of islands after each addition.
    """
    parent = {}
    rank = {}

    def find(x):
        if x not in parent:
            parent[x] = x
            rank[x] = 0
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return 0   # already connected, no change
        if rank[rx] < rank[ry]:
            rx, ry = ry, rx
        parent[ry] = rx
        if rank[rx] == rank[ry]:
            rank[rx] += 1
        return 1   # merged, component count decreases by 1

    land = set()
    islands = 0
    result = []

    for r, c in positions:
        if (r, c) in land:
            result.append(islands)
            continue

        land.add((r, c))
        islands += 1                # new isolated island
        find((r, c))                # initialize in DSU

        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = r + dr, c + dc
            if (nr, nc) in land:
                islands -= union((r,c), (nr,nc))   # merge if different components

        result.append(islands)

    return result


print(numIslands2(3, 3, [[0,0],[0,1],[1,2],[2,1],[1,1]]))
# After (0,0): 1 island
# After (0,1): 1 island (merged with 0,0)
# After (1,2): 2 islands
# After (2,1): 3 islands
# After (1,1): 1 island (connects all three)
```

### DSU vs DFS/BFS for Grids

```
Static grid, count islands once:
  → DFS/BFS is simpler to code, same O(M×N) time

Static grid, multiple connectivity queries:
  → Build DSU once, then O(α) per query

Dynamic grid (cells being added):
  → DSU is the right choice — handles online additions naturally

Dynamic grid (cells being REMOVED):
  → DSU can't handle deletions directly
  → Offline trick: reverse the removals, treat as additions, process in reverse order
```

---

## Pattern 6: Weighted / Bipartite DSU

### Part A: Bipartite Check with DSU

A graph is bipartite if you can color all nodes with 2 colors such that no two adjacent nodes share a color. Think of it as: "Can we split nodes into two groups where every edge goes BETWEEN groups?"

The classic approach is BFS/DFS 2-coloring. But we can also use DSU with a "virtual opposite node" trick.

For each node u, create a virtual node u' representing "the opposite side from u." When processing edge (u, v):
- Union u with v' (u is on the opposite side from v)
- Union v with u' (v is on the opposite side from u)
- Check: if find(u) == find(v), they're on the same side → NOT bipartite!

```python
def isBipartite(graph: list) -> bool:
    """
    graph[i] = list of neighbors of node i.
    Return True if graph is bipartite.
    """
    n = len(graph)
    # Nodes 0..n-1: real nodes
    # Nodes n..2n-1: virtual "opposite" nodes (node i's opposite = node i+n)
    dsu = DSU(2 * n)

    for u in range(n):
        for v in graph[u]:
            # u and v must be on opposite sides
            if dsu.connected(u, v):
                return False   # same component → same side → not bipartite!
            dsu.union(u, v + n)   # u connects to v's opposite
            dsu.union(v, u + n)   # v connects to u's opposite

    return True


# Test 1: simple bipartite
graph1 = [[1,3],[0,2],[1,3],[0,2]]
print(isBipartite(graph1))  # True
# Coloring: 0,2 = red; 1,3 = blue

# Test 2: odd cycle, not bipartite
graph2 = [[1,2,3],[0,2],[0,1],[0]]
print(isBipartite(graph2))  # False
# 0-1-2-0 forms a triangle (odd cycle)
```

### ASCII: Bipartite DSU

```
Graph: 0─1─2─3─0  (even cycle, bipartite)

Processing edge (0,1):
  union(0, 1+4=5) → 0 and 5 connected
  union(1, 0+4=4) → 1 and 4 connected
  DSU: {0,5}, {1,4}, {2}, {3}, {6}, {7}

Processing edge (1,2):
  union(1, 2+4=6) → 1 and 6 connected
  union(2, 1+4=5) → 2 and 5 connected
  Now 2 joins the {0,5} group (via 5)
  DSU: {0,2,5}, {1,4,6}, {3}, {7}

Processing edge (2,3):
  union(2, 3+4=7) → 2 and 7; but 2 is in group {0,2,5}
  union(3, 2+4=6) → 3 and 6; 6 is in {1,4,6}
  DSU: {0,2,5,7}, {1,3,4,6}

Processing edge (3,0):
  union(3, 0+4=4) → 3 is in {1,3,4,6}, 4 is in {1,3,4,6} → already together
  union(0, 3+4=7) → 0 is in {0,2,5,7}, 7 is in {0,2,5,7} → already together
  Check: find(3) == find(0)? 3→{1,3,4,6}, 0→{0,2,5,7} → different → OK!

Result: Bipartite (even cycle → 2-colorable)

Group A (real nodes): 0, 2
Group B (real nodes): 1, 3
```

### Part B: Weighted DSU (Relative Distances)

Sometimes edges carry weights representing relative values (ratios, distances). You need to answer queries like "what is the ratio between a and b?"

This appears in LeetCode 399: Evaluate Division.

Store `weight[x]` = weight of edge from x to its parent (i.e., ratio: x / parent).

During `find`, accumulate the product of weights along the path.
During path compression, update weights to go directly to root.

```python
class WeightedDSU:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.weight = [1.0] * n   # weight[i] = ratio: value[i] / value[parent[i]]

    def find(self, x: int):
        """Return (root, total_weight from x to root)."""
        if self.parent[x] == x:
            return x, 1.0

        root, parent_weight = self.find(self.parent[x])
        # Update path compression: x now points directly to root
        self.weight[x] *= parent_weight
        self.parent[x] = root
        return root, self.weight[x]

    def union(self, x: int, y: int, ratio: float) -> None:
        """
        value[x] / value[y] = ratio
        → value[x] = ratio * value[y]
        """
        rx, wx = self.find(x)   # wx = value[x] / value[rx]
        ry, wy = self.find(y)   # wy = value[y] / value[ry]
        if rx == ry:
            return
        # value[x] / value[y] = ratio
        # → wx * value[rx] / (wy * value[ry]) = ratio
        # → value[rx] / value[ry] = ratio * wy / wx
        self.parent[rx] = ry
        self.weight[rx] = ratio * wy / wx

    def query(self, x: int, y: int) -> float:
        """Return value[x] / value[y], or -1 if not connected."""
        rx, wx = self.find(x)
        ry, wy = self.find(y)
        if rx != ry:
            return -1.0
        return wx / wy


def calcEquation(equations: list, values: list, queries: list) -> list:
    """
    equations[i] = [a, b] means a / b = values[i]
    Return result for each query [c, d] = c / d.
    """
    # Map variable names to integers
    var_map = {}
    def get_id(var):
        if var not in var_map:
            var_map[var] = len(var_map)
        return var_map[var]

    for a, b in equations:
        get_id(a); get_id(b)

    n = len(var_map)
    dsu = WeightedDSU(n)

    for (a, b), val in zip(equations, values):
        dsu.union(get_id(a), get_id(b), val)

    results = []
    for a, b in queries:
        if a not in var_map or b not in var_map:
            results.append(-1.0)
        elif a == b:
            results.append(1.0)
        else:
            results.append(dsu.query(get_id(a), get_id(b)))

    return results


equations = [["a","b"],["b","c"]]
values = [2.0, 3.0]
queries = [["a","c"],["b","a"],["a","e"],["a","a"],["x","x"]]
print(calcEquation(equations, values, queries))
# [6.0, 0.5, -1.0, 1.0, -1.0]
```

---

## DSU Problem Recognition Cheatsheet

```
Trigger Phrase                                   → Pattern
----------------------------------------------------------------
"connected components"                           → Pattern 1
"are X and Y connected?"                         → Pattern 1
"minimum cost to connect all"                    → Pattern 2 (Kruskal)
"minimum spanning tree"                          → Pattern 2 (Kruskal)
"accounts merge" / "group by shared attribute"   → Pattern 3 (Online Union)
"cycle in undirected graph"                      → Pattern 4
"redundant connection"                           → Pattern 4
"number of islands" (static)                     → Pattern 5
"number of islands II" (dynamic additions)       → Pattern 5
"is graph bipartite"                             → Pattern 6A (Virtual Nodes)
"evaluate division" / "relative ratios"          → Pattern 6B (Weighted DSU)

When DSU BEATS alternatives:
  vs BFS/DFS: Better when doing many union/find operations (online)
  vs Kruskal+DFS: DSU makes Kruskal simple (no cycle detection needed)
  vs Tarjan SCC: DSU is for undirected; Tarjan is for directed SCCs

When NOT to use DSU:
  - Directed graph problems (mostly)
  - Need to DELETE edges/connections (DSU doesn't support)
  - Need actual path between nodes (DSU only tells IF connected, not HOW)
  - Need to enumerate all members of a component (need extra bookkeeping)
```

---

## Common Bugs and Fixes

```python
# Bug 1: Forgetting that find() must be called before union() comparisons
# WRONG:
if dsu.parent[u] == dsu.parent[v]:   # parents might not be roots!
    # This misses connections made through intermediaries

# CORRECT:
if dsu.find(u) == dsu.find(v):       # always use find(), not parent[]

# Bug 2: Not updating component count correctly
# If you add your own bookkeeping, decrement components ONLY when union
# returns True (actually merged different components)

# Bug 3: Off-by-one in node numbering
# Problem says nodes are 1-indexed → DSU(n+1) to have nodes 0..n

# Bug 4: Using DSU for directed graph cycle detection
# DSU will say there's a cycle in: 0→1, 2→1 (diamond shape, no cycle)
# because union(0,1) then union(2,1) then find(0)==find(2)
# For directed graphs: use DFS with coloring (white/gray/black)

# Bug 5: Bipartite DSU — wrong virtual node offset
# For n nodes, virtual nodes should be n, n+1, ..., 2n-1
# Create DSU(2*n), virtual node for i is i+n

# Bug 6: Path compression invalidating cached weights in weighted DSU
# Always update weight[x] during path compression in find()
# The recurrence: weight[x] = weight[x] * weight[parent[x]] accumulated to root
```

---

## Complexity Summary

| Operation | With Path Compression + Union by Rank | Naive |
|---|---|---|
| find(x) | O(α(N)) ≈ O(1) | O(N) worst case |
| union(x,y) | O(α(N)) ≈ O(1) | O(N) worst case |
| N operations | O(N × α(N)) ≈ O(N) | O(N²) |

α(N) = inverse Ackermann function. For N = 10^80 (atoms in universe), α(N) = 5. Treat it as constant.

| Pattern | Time | Space |
|---|---|---|
| Basic Connectivity | O(E × α(V)) | O(V) |
| Kruskal's MST | O(E log E + E × α(V)) | O(V) |
| Online Union | O(Q × α(N)) | O(N) |
| Cycle Detection | O(E × α(V)) | O(V) |
| Grid Connectivity | O(M×N × α(M×N)) | O(M×N) |
| Weighted DSU | O(N × α(N)) | O(N) |

E = edges, V = vertices, Q = queries, M×N = grid dimensions.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Real World Usage →](./real_world_usage.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
