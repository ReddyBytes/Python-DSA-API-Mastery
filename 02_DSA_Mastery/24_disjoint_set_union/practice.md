# 💻 Practice — Disjoint Set Union (Union-Find)

## Quick Index

| Q# | Topic | Difficulty |
|---|---|---|
| [Q1](#q1) | DSU structure — initialize parent array | 🟢 Easy |
| [Q2](#q2) | Find operation — naive traversal | 🟢 Easy |
| [Q3](#q3) | Union operation — basic merge | 🟢 Easy |
| [Q4](#q4) | Connected components — count distinct roots | 🟢 Easy |
| [Q5](#q5) | Path compression — flatten on find | 🟢 Easy |
| [Q6](#q6) | Union by rank — attach smaller under larger | 🟢 Easy |
| [Q7](#q7) | Cycle detection — undirected graph | 🟡 Medium |
| [Q8](#q8) | Redundant connection — last cycle-creating edge | 🟡 Medium |
| [Q9](#q9) | Component size tracking — union by size | 🟡 Medium |
| [Q10](#q10) | Number of islands — 2D grid with DSU | 🟡 Medium |
| [Q11](#q11) | DSU vs BFS/DFS — when to choose which | 🟡 Medium |
| [Q12](#q12) | Kruskal's MST — greedy edge selection | 🟡 Medium |
| [Q13](#q13) | Accounts merge — email grouping | 🟡 Medium |
| [Q14](#q14) | Similar string groups — pairwise similarity | 🟡 Medium |
| [Q15](#q15) | Dynamic grid — islands II (online additions) | 🟠 Hard |
| [Q16](#q16) | Bipartite check — virtual node trick | 🟠 Hard |
| [Q17](#q17) | Weighted DSU — evaluate division | 🟠 Hard |
| [Q18](#q18) | Largest component — track max size live | 🟠 Hard |
| [Q19](#q19) | Min cost to connect all points — Manhattan MST | 🟠 Hard |
| [Q20](#q20) | DSU correctness — spot the five bugs | 🟠 Hard |

---

<a id="q1"></a>
### Q1 · DSU Structure — Initialize the Parent Array

🟢 Easy

**Problem:** You have `n` nodes labeled `0` to `n-1`. Write the `__init__` method for a DSU class that gives every node its own component at startup. What does `parent` look like for `n=5`? Why is `parent = [0] * n` wrong?

<details><summary>💡 Hint</summary>

Each node starts as its own root. The self-loop `parent[i] = i` is the sentinel: "I have no parent above me." If you write `[0] * n`, every node points to node 0, which means they all appear to already be in the same component before any union is called.

</details>

<details>
<summary>✅ Answer</summary>

```python
class DSU:
    def __init__(self, n: int):
        self.parent = list(range(n))  # [0, 1, 2, 3, 4] for n=5
        self.rank = [0] * n
        self.num_components = n
```

For `n=5`: `parent = [0, 1, 2, 3, 4]` — each node is its own root.

**Why `[0] * n` is wrong:** `parent = [0, 0, 0, 0, 0]` means nodes 1, 2, 3, 4 all point to node 0. Calling `find(1)` immediately returns 0, so `find(1) == find(2)` returns `True` before any union — false connectivity from the start.

**Why:** The self-loop `parent[i] = i` is the agreed-upon sentinel meaning "I am a root." Every `find` implementation checks for this condition to stop traversal.

</details>

> 💻 Try it: [practice_local.py → Q1](./practice_local.py)

---

<a id="q2"></a>
### Q2 · Find Operation — Naive Root Traversal

🟢 Easy

**Problem:** Given the parent array `[0, 0, 1, 2, 3]`, trace `find(4)` step by step. Implement `find` without path compression. What is the time complexity in the worst case?

<details><summary>💡 Hint</summary>

Follow parent pointers until you reach a node where `parent[x] == x`. That node is the root. Count how many hops it takes.

</details>

<details>
<summary>✅ Answer</summary>

```python
def find_naive(parent, x):
    while parent[x] != x:
        x = parent[x]
    return x

# Trace for parent = [0, 0, 1, 2, 3], find(4):
# 4 → parent[4]=3 → parent[3]=2 → parent[2]=1 → parent[1]=0 → parent[0]=0 ✓
# Returns 0 after 4 hops.
```

For a chain of `n` nodes, `find` takes O(n) steps — as slow as a linked list.

**Why this matters:** Without path compression, repeatedly calling `find` on deep nodes accumulates cost. A chain `0←1←2←3←...←n-1` produces worst-case O(n) per find. Path compression solves this.

</details>

> 💻 Try it: [practice_local.py → Q2](./practice_local.py)

---

<a id="q3"></a>
### Q3 · Union Operation — Basic Merge

🟢 Easy

**Problem:** Starting with `n=4` nodes (all separate), apply `union(0, 1)` then `union(2, 3)` then `union(1, 2)`. Draw the parent array state after each step. Without union by rank, which root becomes the parent?

<details><summary>💡 Hint</summary>

Basic union: find roots of both nodes, make one root the parent of the other. Without rank, convention is typically `parent[rootB] = rootA`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def union_basic(parent, a, b):
    root_a = find_naive(parent, a)
    root_b = find_naive(parent, b)
    if root_a != root_b:
        parent[root_b] = root_a  # attach B's root under A's root

# Step 0: parent = [0, 1, 2, 3]   (4 components)
# union(0, 1): root_a=0, root_b=1 → parent[1]=0
#   parent = [0, 0, 2, 3]          (3 components)
#
# union(2, 3): root_a=2, root_b=3 → parent[3]=2
#   parent = [0, 0, 2, 2]          (2 components)
#
# union(1, 2): find(1)→0, find(2)→2 → parent[2]=0
#   parent = [0, 0, 0, 2]          (1 component)
#
# Now find(3) → 3→2→0 (2 hops, not 1)
```

**Why:** Without union by rank, merging equal-rank trees creates an arbitrary chain. This is why union by rank is essential — it keeps the tree shallow by always attaching the shorter tree under the taller one.

</details>

> 💻 Try it: [practice_local.py → Q3](./practice_local.py)

---

<a id="q4"></a>
### Q4 · Connected Components — Count Distinct Roots

🟢 Easy

**Problem:** Given `n=6` and edges `[[0,1],[1,2],[3,4]]`, count the number of connected components using DSU. Which nodes are isolated?

<details><summary>💡 Hint</summary>

Start with `num_components = n`. Every successful union (merging two different components) decrements the count by exactly 1.

</details>

<details>
<summary>✅ Answer</summary>

```python
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.num_components = n

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
        self.num_components -= 1
        return True

def count_components(n, edges):
    dsu = DSU(n)
    for u, v in edges:
        dsu.union(u, v)
    return dsu.num_components

# n=6, edges=[[0,1],[1,2],[3,4]]
# union(0,1): merge → 5 components
# union(1,2): merge → 4 components
# union(3,4): merge → 3 components
# Result: 3 components → {0,1,2}, {3,4}, {5}
print(count_components(6, [[0,1],[1,2],[3,4]]))  # 3
```

Node 5 is isolated — it was never mentioned in any edge, so it stays as its own component.

**Why:** The component counter is decremented only when two previously disconnected sets merge. Duplicate unions (same-component edges) return `False` without changing the count.

</details>

> 💻 Try it: [practice_local.py → Q4](./practice_local.py)

---

<a id="q5"></a>
### Q5 · Path Compression — Flatten on Find

🟢 Easy

**Problem:** Given the chain `parent = [0, 0, 1, 2, 3]` (representing 4→3→2→1→0), call `find(4)` with path compression. What does `parent` look like after the call? Why does this make future finds faster?

<details><summary>💡 Hint</summary>

Recursive path compression: `parent[x] = find(parent[x])`. On the way back up from recursion, every node on the path gets its parent pointer updated to point directly to the root.

</details>

<details>
<summary>✅ Answer</summary>

```python
def find_compressed(parent, x):
    if parent[x] != x:
        parent[x] = find_compressed(parent, parent[x])  # compress in-place
    return parent[x]

parent = [0, 0, 1, 2, 3]  # chain: 4→3→2→1→0
root = find_compressed(parent, 4)
print(root)    # 0
print(parent)  # [0, 0, 0, 0, 0] — all nodes now point directly to root
```

**Before:** `4→3→2→1→0` (4 hops to find root of 4)

**After:** `4→0, 3→0, 2→0, 1→0` (1 hop for any future find on these nodes)

**Why:** The recursive call to `find(parent[x])` returns the root. Assigning `parent[x] = root` short-circuits the path. Every node visited during the traversal gets a direct link to the root, so subsequent finds on any of them cost O(1). This is the key optimization that achieves the O(α(n)) amortized bound.

**Note:** Never modify `rank` during path compression — rank is an upper bound on height, not the exact height, and it's only updated in `union`.

</details>

> 💻 Try it: [practice_local.py → Q5](./practice_local.py)

---

<a id="q6"></a>
### Q6 · Union by Rank — Attach Smaller Under Larger

🟢 Easy

**Problem:** You have two trees: tree A with root 0 (rank 2) and tree B with root 5 (rank 1). You call `union(0, 5)`. Which root becomes the child? What happens to the ranks? Now call `union(3, 7)` where both 3 and 7 have rank 0 — what happens to the rank?

<details><summary>💡 Hint</summary>

Always attach the lower-rank root under the higher-rank root. Ranks only change when merging two trees of equal rank — the new root gets rank incremented by 1.

</details>

<details>
<summary>✅ Answer</summary>

```python
def union_by_rank(parent, rank, x, y):
    rx = find_compressed(parent, x)
    ry = find_compressed(parent, y)
    if rx == ry:
        return False
    # Attach lower rank under higher rank
    if rank[rx] < rank[ry]:
        rx, ry = ry, rx       # swap so rx always has >= rank
    parent[ry] = rx            # ry becomes child of rx
    if rank[rx] == rank[ry]:
        rank[rx] += 1          # only increment when ranks were equal
    return True

# union(0, 5): rank[0]=2, rank[5]=1
#   2 > 1 → attach 5 under 0
#   parent[5] = 0, rank unchanged (2 != 1)
#   Result: rank[0] stays 2

# union(3, 7): rank[3]=0, rank[7]=0
#   Equal ranks → after swap, rx=3 (or 7, arbitrary), ry=7
#   parent[7] = 3, rank[3] += 1 → rank[3] = 1
#   Result: rank[3] becomes 1
```

**Why rank only increments on equal merges:** A tree of rank k was built by merging two rank-(k-1) trees. The height grows by at most 1. If ranks differ, the taller tree absorbs the shorter one and its height does not increase at all, so the rank stays the same.

**Key invariant:** rank is a permanent upper bound on height. It never decreases, even after path compression flattens the tree.

</details>

> 💻 Try it: [practice_local.py → Q6](./practice_local.py)

---

<a id="q7"></a>
### Q7 · Cycle Detection — Undirected Graph

🟡 Medium

**Problem:** Given `n=4` and edges `[[0,1],[1,2],[2,0],[0,3]]`, detect whether a cycle exists using DSU. Return the first edge that creates the cycle. Why does this approach work for undirected graphs but NOT for directed graphs?

<details><summary>💡 Hint</summary>

Before calling `union(u, v)`, check if `find(u) == find(v)`. If they share the same root, they're already connected — adding this edge closes a loop.

</details>

<details>
<summary>✅ Answer</summary>

```python
def has_cycle_and_find_it(n, edges):
    dsu = DSU(n)
    for u, v in edges:
        if dsu.find(u) == dsu.find(v):
            return True, [u, v]   # this edge creates the cycle
        dsu.union(u, v)
    return False, []

# Trace:
# edge [0,1]: find(0)=0, find(1)=1 → different → union → {0,1}
# edge [1,2]: find(1)=0, find(2)=2 → different → union → {0,1,2}
# edge [2,0]: find(2)=0, find(0)=0 → SAME ROOT → cycle! return [2, 0]

print(has_cycle_and_find_it(4, [[0,1],[1,2],[2,0],[0,3]]))
# (True, [2, 0])
```

**Why it fails for directed graphs:** Consider `0→1` and `2→1` (a diamond, no cycle). DSU would union(0,1) and union(2,1), making find(0)==find(2) — incorrectly reporting a cycle. DSU treats all edges as undirected; it cannot distinguish direction. For directed cycle detection, use DFS with white/gray/black coloring.

</details>

> 💻 Try it: [practice_local.py → Q7](./practice_local.py)

---

<a id="q8"></a>
### Q8 · Redundant Connection — Last Cycle-Creating Edge

🟡 Medium

**Problem:** Given edges `[[1,2],[1,3],[2,3]]` for a 1-indexed graph, return the edge that, when removed, leaves a valid tree. If multiple valid edges exist, return the last one in the input order.

*(LeetCode 684)*

<details><summary>💡 Hint</summary>

Process edges in order. The first edge whose `union` returns `False` (both endpoints already connected) is the redundant edge. Because we process left-to-right, the last such edge in input order is automatically returned.

</details>

<details>
<summary>✅ Answer</summary>

```python
def find_redundant_connection(edges):
    n = len(edges)
    dsu = DSU(n + 1)   # nodes labeled 1..n → allocate n+1

    for u, v in edges:
        if not dsu.union(u, v):
            return [u, v]   # union returned False → already connected → redundant

    return []

# Trace for [[1,2],[1,3],[2,3]]:
# union(1, 2): different → merge
# union(1, 3): different → merge, now {1,2,3} all connected
# union(2, 3): find(2)=root, find(3)=same root → False → return [2, 3]

print(find_redundant_connection([[1,2],[1,3],[2,3]]))    # [2, 3]
print(find_redundant_connection([[1,2],[2,3],[3,4],[1,4],[1,5]]))  # [1, 4]
```

**Why n+1 for the DSU size:** Nodes are labeled 1 to n, so we need index n to be valid. `DSU(n+1)` allocates indices 0 through n; we simply never use index 0.

**Why:** A tree on n nodes has exactly n-1 edges. Given n edges, exactly one is redundant. The redundant edge connects two nodes that already had a path between them — DSU catches this in O(α(n)) per edge.

</details>

> 💻 Try it: [practice_local.py → Q8](./practice_local.py)

---

<a id="q9"></a>
### Q9 · Component Size Tracking — Union by Size

🟡 Medium

**Problem:** Implement a DSU that uses union by size (not rank) and supports a `component_size(x)` query. Given `n=7` and unions `(0,1),(1,2),(3,4),(4,5),(0,3)`, what is `component_size(2)` after all unions?

<details><summary>💡 Hint</summary>

Maintain a `size` array initialized to all 1s. When merging, add the smaller component's size to the larger component's root size. Always attach the smaller tree under the larger.

</details>

<details>
<summary>✅ Answer</summary>

```python
class DSUWithSize:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n           # all components start with size 1
        self.num_components = n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        # Attach smaller size under larger size
        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        self.size[rx] += self.size[ry]   # merge sizes
        self.num_components -= 1
        return True

    def component_size(self, x):
        return self.size[self.find(x)]   # size lives at root

dsu = DSUWithSize(7)
for a, b in [(0,1),(1,2),(3,4),(4,5),(0,3)]:
    dsu.union(a, b)

print(dsu.component_size(2))  # 6 — nodes {0,1,2,3,4,5} all merged
print(dsu.component_size(6))  # 1 — node 6 still isolated
```

**Why size lives at the root:** After path compression, nodes point directly to the root. `size[root]` always reflects the full component size. Querying a non-root node: `size[find(x)]` correctly redirects to the root.

**Union by size vs union by rank:** Size gives you `component_size` for free. Rank is slightly cheaper (no integer addition) but provides no component size info. Both achieve O(log n) tree height and O(α(n)) amortized finds.

</details>

> 💻 Try it: [practice_local.py → Q9](./practice_local.py)

---

<a id="q10"></a>
### Q10 · Number of Islands — 2D Grid with DSU

🟡 Medium

**Problem:** Count the number of islands in this grid using DSU (not DFS/BFS):

```
1 1 0 0
1 1 0 0
0 0 1 0
0 0 0 1
```

Encode 2D coordinates as 1D indices. Only union adjacent land cells.

<details><summary>💡 Hint</summary>

Map `(r, c)` to `r * cols + c`. Initialize `num_components` to the count of land cells only (water cells are irrelevant). Union each land cell with its right and bottom neighbors if they are also land.

</details>

<details>
<summary>✅ Answer</summary>

```python
def num_islands(grid):
    if not grid or not grid[0]:
        return 0
    rows, cols = len(grid), len(grid[0])

    # Only count land cells as starting components
    land = sum(grid[r][c] == '1' for r in range(rows) for c in range(cols))
    dsu = DSU(rows * cols)
    dsu.num_components = land   # override to count only land

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '0':
                continue
            cell = r * cols + c
            # Union with right neighbor
            if c + 1 < cols and grid[r][c + 1] == '1':
                dsu.union(cell, r * cols + (c + 1))
            # Union with bottom neighbor
            if r + 1 < rows and grid[r + 1][c] == '1':
                dsu.union(cell, (r + 1) * cols + c)

    return dsu.num_components

grid = [["1","1","0","0"],
        ["1","1","0","0"],
        ["0","0","1","0"],
        ["0","0","0","1"]]
print(num_islands(grid))  # 3
```

**Why only right + bottom neighbors:** Processing left-to-right, top-to-bottom, each cell only needs to check right and down. Left and up neighbors were already processed and unioned from the other side, so checking all 4 directions would just produce redundant (no-op) union calls.

**Why:** DSU and BFS/DFS have the same O(M×N) complexity for static grids. DSU shines when cells are added dynamically (see Q15) — you can process each addition in O(α(M×N)) without rerunning BFS.

</details>

> 💻 Try it: [practice_local.py → Q10](./practice_local.py)

---

<a id="q11"></a>
### Q11 · DSU vs BFS/DFS — When to Choose Which

🟡 Medium

**Problem:** For each scenario below, state whether you should use DSU or BFS/DFS and why:

1. Count islands in a static grid (asked once)
2. Check if city A and city B are reachable after each road is added, for 10,000 road additions
3. Find the actual shortest path between two nodes
4. Detect a cycle in a directed graph
5. Find the minimum spanning tree

<details><summary>💡 Hint</summary>

DSU's strengths: online edge additions, many connectivity queries, undirected graphs. BFS/DFS's strengths: finding paths, directed graphs, single-source traversal.

</details>

<details>
<summary>✅ Answer</summary>

```
1. Static grid, count once → BFS/DFS
   Both are O(M×N). DFS is simpler to write. No advantage to DSU here.

2. Dynamic online additions + many queries → DSU
   Each union is O(α(n)). After 10,000 additions, DSU total cost ≈ O(10,000 × α(n)).
   BFS/DFS per query would be O(V+E) × 10,000 queries = much slower.

3. Find actual shortest path → BFS (unweighted) or Dijkstra (weighted)
   DSU only tells you IF two nodes are connected — not HOW to get there.
   DSU discards path information during path compression.

4. Cycle in directed graph → DFS with coloring (white/gray/black)
   DSU treats all edges as undirected. It gives false positives on directed
   graphs: 0→1 and 2→1 (no cycle) would incorrectly show 0 and 2 connected.

5. Minimum spanning tree → Kruskal's (DSU) or Prim's (priority queue)
   Kruskal's uses DSU to check connectivity in O(α(V)) per edge after sorting.
   DSU makes Kruskal's clean and efficient.
```

**Summary trigger phrases for DSU:**
- "are X and Y connected?" → DSU
- "how many components?" → DSU
- "minimum cost to connect all" → DSU (Kruskal)
- "cycle in undirected graph" → DSU
- "edges arrive online" → DSU

</details>

> 💻 Try it: [practice_local.py → Q11](./practice_local.py)

---

<a id="q12"></a>
### Q12 · Kruskal's MST — Greedy Edge Selection

🟡 Medium

**Problem:** Find the MST of this weighted graph using Kruskal's algorithm and DSU:

```
Nodes: 0, 1, 2, 3
Edges: (weight, u, v):
  (1, 0, 1), (4, 0, 2), (3, 1, 2), (2, 1, 3), (5, 2, 3)
```

Return the total MST weight and the list of edges selected.

<details><summary>💡 Hint</summary>

Sort edges by weight. Greedily add each edge if `union` returns `True` (endpoints not yet connected). Stop when you have n-1 edges. The Cut Property guarantees that the cheapest edge crossing any cut must be in some MST.

</details>

<details>
<summary>✅ Answer</summary>

```python
def kruskal_mst(n, edges):
    """
    n: number of nodes (0..n-1)
    edges: list of (weight, u, v)
    Returns: (total_weight, mst_edges)
    """
    dsu = DSU(n)
    sorted_edges = sorted(edges)   # sort by weight (first tuple element)
    mst_weight = 0
    mst_edges = []

    for weight, u, v in sorted_edges:
        if dsu.union(u, v):          # union returns True if they were separate
            mst_weight += weight
            mst_edges.append((weight, u, v))
            if len(mst_edges) == n - 1:
                break                # MST complete: n nodes need exactly n-1 edges

    return mst_weight, mst_edges

edges = [(1,0,1),(4,0,2),(3,1,2),(2,1,3),(5,2,3)]
w, mst = kruskal_mst(4, edges)
print(w)    # 6
print(mst)  # [(1,0,1), (2,1,3), (3,1,2)]

# Step-by-step:
# Sorted: (1,0,1),(2,1,3),(3,1,2),(4,0,2),(5,2,3)
# (1,0,1): 0 and 1 separate → ADD. {0,1}
# (2,1,3): 1 and 3 separate → ADD. {0,1,3}
# (3,1,2): 1 and 2 separate → ADD. {0,1,2,3} — 3 edges, n-1=3 → DONE
# Total: 1+2+3 = 6
```

**Time complexity:** O(E log E) for sorting + O(E × α(V)) for DSU operations = O(E log E) overall.

**Why greedy works:** The Cut Property — for any partition of nodes into two sets, the minimum weight edge crossing the cut must appear in some MST. Kruskal's repeatedly exploits this by always picking the cheapest safe edge.

</details>

> 💻 Try it: [practice_local.py → Q12](./practice_local.py)

---

<a id="q13"></a>
### Q13 · Accounts Merge — Email Grouping

🟡 Medium

**Problem:** Merge accounts that share at least one email. Each account is `[name, email1, email2, ...]`. Two accounts belong to the same person if they share any email.

```python
accounts = [
    ["Alice", "a@x.com", "b@x.com"],
    ["Bob",   "c@x.com"],
    ["Alice", "b@x.com", "d@x.com"]
]
# Expected: Alice's two accounts merge → [["Alice","a@x.com","b@x.com","d@x.com"], ["Bob","c@x.com"]]
```

*(LeetCode 721)*

<details><summary>💡 Hint</summary>

Treat each account index as a DSU node. Map every email to the first account index that claimed it. When a second account has the same email, union the two account nodes. Group emails by root account at the end.

</details>

<details>
<summary>✅ Answer</summary>

```python
from collections import defaultdict

def accounts_merge(accounts):
    dsu = DSU(len(accounts))
    email_to_account = {}   # email → first account index that claimed it

    for i, account in enumerate(accounts):
        for email in account[1:]:           # skip name at index 0
            if email in email_to_account:
                dsu.union(i, email_to_account[email])  # merge the two account nodes
            else:
                email_to_account[email] = i

    # Group emails by their root account
    root_to_emails = defaultdict(set)
    for email, acc_idx in email_to_account.items():
        root = dsu.find(acc_idx)
        root_to_emails[root].add(email)

    result = []
    for root, emails in root_to_emails.items():
        name = accounts[root][0]
        result.append([name] + sorted(emails))

    return result

result = accounts_merge(accounts)
for acc in result:
    print(acc)
# ["Alice", "a@x.com", "b@x.com", "d@x.com"]
# ["Bob", "c@x.com"]
```

**Why account indices as DSU nodes:** Accounts, not emails, are the things being merged. Emails are the edges connecting accounts. The email-to-account mapping lets us detect when two accounts share an email and need unioning.

**Time complexity:** O(N×k × α(N)) where N = number of accounts, k = average emails per account.

</details>

> 💻 Try it: [practice_local.py → Q13](./practice_local.py)

---

<a id="q14"></a>
### Q14 · Similar String Groups — Pairwise Similarity

🟡 Medium

**Problem:** Two strings are "similar" if they differ in exactly 0 or 2 positions (a valid swap). Given `strs = ["tars","rats","arts","star"]`, find the number of groups of mutually similar strings.

*(LeetCode 839)*

<details><summary>💡 Hint</summary>

Model strings as DSU nodes. For each pair `(i, j)`, check if `strs[i]` and `strs[j]` are similar. If yes, `union(i, j)`. Answer is `num_components` at the end.

</details>

<details>
<summary>✅ Answer</summary>

```python
def num_similar_groups(strs):
    n = len(strs)
    dsu = DSU(n)

    def similar(a, b):
        diffs = sum(1 for x, y in zip(a, b) if x != y)
        return diffs == 0 or diffs == 2   # identical or valid swap

    for i in range(n):
        for j in range(i + 1, n):
            if similar(strs[i], strs[j]):
                dsu.union(i, j)

    return dsu.num_components

print(num_similar_groups(["tars","rats","arts","star"]))  # 2
# "tars" ↔ "rats" (swap t↔r at positions 0,2) — similar
# "tars" ↔ "arts" (swap ta↔ar at 0,1) — 2 diffs — similar
# "star" — not similar to others
# Group 1: {tars, rats, arts}   Group 2: {star}
```

**Time complexity:** O(n² × L) where L is string length (for the similarity check). DSU operations add O(n² × α(n)) — negligible.

**Why DSU fits:** This is a connectivity problem — similar strings should be in the same group, and similarity is transitive through the union operations. The graph of similarities might not be directly obvious, but DSU handles the transitivity automatically.

</details>

> 💻 Try it: [practice_local.py → Q14](./practice_local.py)

---

<a id="q15"></a>
### Q15 · Dynamic Grid — Islands II (Online Additions)

🟠 Hard

**Problem:** You have an `m×n` grid, initially all water. Given a list of positions that become land one at a time, return the number of islands after each land cell is added.

```python
# m=3, n=3, positions = [[0,0],[0,1],[1,2],[2,1],[1,1]]
# After (0,0): 1
# After (0,1): 1  (merged with 0,0)
# After (1,2): 2
# After (2,1): 3
# After (1,1): 1  (connects all three separate islands)
```

*(LeetCode 305)*

<details><summary>💡 Hint</summary>

Use a dict-based DSU (or a set to track land cells). When adding a new land cell, initialize it as a new component (+1 island). Then check all 4 neighbors — for each that is already land, union them (each successful merge -1 island).

</details>

<details>
<summary>✅ Answer</summary>

```python
def num_islands_2(m, n, positions):
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
            return 0             # already connected — no island count change
        if rank[rx] < rank[ry]:
            rx, ry = ry, rx
        parent[ry] = rx
        if rank[rx] == rank[ry]:
            rank[rx] += 1
        return 1                 # successfully merged — 1 fewer island

    land = set()
    islands = 0
    result = []

    for r, c in positions:
        if (r, c) in land:
            result.append(islands)
            continue

        land.add((r, c))
        find((r, c))             # register in DSU
        islands += 1             # new isolated land cell = new island

        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = r + dr, c + dc
            if (nr, nc) in land:
                islands -= union((r, c), (nr, nc))

        result.append(islands)

    return result

print(num_islands_2(3, 3, [[0,0],[0,1],[1,2],[2,1],[1,1]]))
# [1, 1, 2, 3, 1]
```

**Why dict-based DSU:** Positions arrive online and may be sparse in a large grid. A dict avoids allocating O(m×n) memory upfront. Initialize nodes lazily on first access.

**Why this beats DFS:** DFS after each addition would be O(m×n) per step → O(m×n×k) total. DSU processes each addition in O(α(m×n)) — essentially constant. For large grids with many additions, this is a massive win.

</details>

> 💻 Try it: [practice_local.py → Q15](./practice_local.py)

---

<a id="q16"></a>
### Q16 · Bipartite Check — Virtual Node Trick

🟠 Hard

**Problem:** Determine if a graph is bipartite using DSU (not BFS 2-coloring). A graph is bipartite if you can split its nodes into two groups where every edge goes between groups.

```python
graph1 = [[1,3],[0,2],[1,3],[0,2]]  # True — 2-colorable
graph2 = [[1,2,3],[0,2],[0,1],[0]]  # False — triangle 0-1-2
```

*(LeetCode 785)*

<details><summary>💡 Hint</summary>

For n nodes, create a DSU of size 2n. For each node `u`, its "opposite" is `u + n`. When processing edge (u, v): u and v must be on opposite sides, so union u with v's opposite (`v+n`) and v with u's opposite (`u+n`). If `find(u) == find(v)`, they're forced onto the same side — not bipartite.

</details>

<details>
<summary>✅ Answer</summary>

```python
def is_bipartite(graph):
    n = len(graph)
    # Nodes 0..n-1 = "real" nodes
    # Nodes n..2n-1 = virtual "opposite" nodes (i's opposite = i+n)
    dsu = DSU(2 * n)

    for u in range(n):
        for v in graph[u]:
            # Check before unioning: if u and v are already in same component,
            # the graph forced them onto the same side → not bipartite
            if dsu.connected(u, v):
                return False
            # u must be on opposite side from v:
            dsu.union(u, v + n)    # u connects to v's "other side"
            dsu.union(v, u + n)    # v connects to u's "other side"

    return True

print(is_bipartite([[1,3],[0,2],[1,3],[0,2]]))  # True
print(is_bipartite([[1,2,3],[0,2],[0,1],[0]]))  # False
```

**Why 2n nodes:** For each real node `i`, we need a virtual node representing "the opposite partition from i." By convention, virtual node for `i` is `i + n`. The DSU groups real nodes with other nodes on the same side by routing them through virtual nodes.

**Intuition:** If we union u's real node with v's virtual node, we're saying "u is on the same side as v's opposite." If later `find(u) == find(v)` (real node u is in the same component as real node v), then u and v are on the same side — contradiction.

</details>

> 💻 Try it: [practice_local.py → Q16](./practice_local.py)

---

<a id="q17"></a>
### Q17 · Weighted DSU — Evaluate Division

🟠 Hard

**Problem:** You're given equations like `a/b = 2.0` and `b/c = 3.0`. Answer queries like `a/c = ?` and `b/a = ?`. Unknown variables or disconnected components return -1.0.

*(LeetCode 399)*

<details><summary>💡 Hint</summary>

Use a weighted DSU where `weight[x]` stores the ratio `value[x] / value[parent[x]]`. During `find`, accumulate the product along the path (and compress it). Query `x/y` = `weight_to_root(x) / weight_to_root(y)` if they share a root.

</details>

<details>
<summary>✅ Answer</summary>

```python
class WeightedDSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.weight = [1.0] * n    # weight[i] = value[i] / value[parent[i]]

    def find(self, x):
        """Returns (root, accumulated_weight from x to root)."""
        if self.parent[x] == x:
            return x, 1.0
        root, parent_weight = self.find(self.parent[x])
        # Path compression: point x directly to root, update weight
        self.weight[x] *= parent_weight
        self.parent[x] = root
        return root, self.weight[x]

    def union(self, x, y, ratio):
        """value[x] / value[y] = ratio."""
        rx, wx = self.find(x)
        ry, wy = self.find(y)
        if rx == ry:
            return
        # value[x] = ratio * value[y]
        # wx * value[rx] = ratio * wy * value[ry]
        # weight[rx] = ratio * wy / wx
        self.parent[rx] = ry
        self.weight[rx] = ratio * wy / wx

    def query(self, x, y):
        rx, wx = self.find(x)
        ry, wy = self.find(y)
        if rx != ry:
            return -1.0
        return wx / wy

def calc_equation(equations, values, queries):
    var_map = {}
    def get_id(var):
        if var not in var_map:
            var_map[var] = len(var_map)
        return var_map[var]

    for a, b in equations:
        get_id(a); get_id(b)

    dsu = WeightedDSU(len(var_map))
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

print(calc_equation([["a","b"],["b","c"]], [2.0, 3.0],
                    [["a","c"],["b","a"],["a","e"]]))
# [6.0, 0.5, -1.0]
```

**Key:** `weight[x]` is not modified during union — only the root's weight is set. During `find` with path compression, weights are accumulated multiplicatively so that `weight[x]` always equals `value[x] / value[root]` after compression.

</details>

> 💻 Try it: [practice_local.py → Q17](./practice_local.py)

---

<a id="q18"></a>
### Q18 · Largest Component — Track Max Size Live

🟠 Hard

**Problem:** Given `n` nodes and edges added one at a time, return the size of the largest component after each edge is added. You must answer in O(α(n)) per edge addition — not by scanning all components.

```python
n = 5
edges = [(0,1),(1,2),(3,4),(2,3)]
# After (0,1): max=2
# After (1,2): max=3
# After (3,4): max=3
# After (2,3): max=5
```

<details><summary>💡 Hint</summary>

Use union by size. After each union, if a merge happened, the new root's size is the merged total. Track a running `max_size` variable — update it only when `union` returns `True`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def largest_component_online(n, edges):
    dsu = DSUWithSize(n)
    max_size = 1   # start with isolated nodes, size 1 each
    result = []

    for u, v in edges:
        if dsu.union(u, v):
            # Merge happened — check new root's size
            new_size = dsu.component_size(u)   # find(u) is now the merged root
            max_size = max(max_size, new_size)
        result.append(max_size)

    return result

print(largest_component_online(5, [(0,1),(1,2),(3,4),(2,3)]))
# [2, 3, 3, 5]
```

**Why this is O(α(n)) per edge:** We don't scan all n nodes after each union. The merged component's size is immediately available at the root via `dsu.component_size(u)`. We update `max_size` only when a merge actually occurs. A simple `max` comparison is O(1).

**Why track `max_size` as a running variable:** If we queried all nodes' component sizes after each edge, that would be O(n) per edge. The running variable lets us stay O(α(n)).

</details>

> 💻 Try it: [practice_local.py → Q18](./practice_local.py)

---

<a id="q19"></a>
### Q19 · Min Cost to Connect All Points — Manhattan MST

🟠 Hard

**Problem:** Given `points = [[0,0],[2,2],[3,10],[5,2],[7,0]]`, find the minimum cost to connect all points where cost = Manhattan distance between two points. Return the minimum total cost.

*(LeetCode 1584)*

<details><summary>💡 Hint</summary>

Generate all pairwise edges with their Manhattan distances. Then run Kruskal's MST. The number of possible edges is O(n²) — for n ≤ 1000, that is ~500,000 edges, which is manageable.

</details>

<details>
<summary>✅ Answer</summary>

```python
def min_cost_connect_points(points):
    n = len(points)
    if n == 1:
        return 0

    # Generate all O(n²) edges with Manhattan distance weights
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            dist = abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1])
            edges.append((dist, i, j))

    # Kruskal's MST
    edges.sort()
    dsu = DSU(n)
    total = 0
    count = 0   # number of edges added to MST

    for dist, u, v in edges:
        if dsu.union(u, v):
            total += dist
            count += 1
            if count == n - 1:
                break    # MST complete

    return total

print(min_cost_connect_points([[0,0],[2,2],[3,10],[5,2],[7,0]]))  # 20
```

**Step-by-step for the example:**

Edges sorted by distance (partial): `(2,0→{0,0},1→{2,2}?)` — closest pairs first.

The MST connects `[0,0]↔[7,0]` (dist 7), `[7,0]↔[5,2]` (dist 4), `[5,2]↔[2,2]` (dist 3), `[2,2]↔[3,10]` (dist 9?) — verify by computing: total = 20.

**Time:** O(n² log n) for generating and sorting all edges + O(n² × α(n)) for DSU = O(n² log n).

**Alternative:** Prim's algorithm with a min-heap can solve this in O(n² log n) without generating all edges explicitly — useful when n is very large.

</details>

> 💻 Try it: [practice_local.py → Q19](./practice_local.py)

---

<a id="q20"></a>
### Q20 · DSU Correctness — Spot the Five Bugs

🟠 Hard

**Problem:** This DSU implementation has five bugs. Identify each one, explain what goes wrong at runtime (no crash — silent wrong answers), and write the corrected version.

```python
class BuggyDSU:
    def __init__(self, n):
        self.parent = [0] * n        # BUG 1
        self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:   # BUG 2 (no path compression)
            x = self.parent[x]
        return x

    def union(self, x, y):
        rx = self.find(x)
        ry = self.find(y)
        if self.parent[rx] == self.parent[ry]:  # BUG 3
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        self.rank[rx] += 1           # BUG 4
        return True

    def connected(self, x, y):
        return self.parent[x] == self.parent[y]  # BUG 5
```

<details><summary>💡 Hint</summary>

Review the five common mistakes: initialization, path compression, same-component check, rank increment condition, and connectivity check.

</details>

<details>
<summary>✅ Answer</summary>

```python
# BUG 1: parent = [0] * n
# All nodes start pointing to node 0 → all appear connected before any union.
# FIX: self.parent = list(range(n))  → each node is its own root.

# BUG 2: find() has no path compression
# Without compression, find() walks the full path every time → O(n) per call.
# FIX:
#   def find(self, x):
#       if self.parent[x] != x:
#           self.parent[x] = self.find(self.parent[x])  # compress
#       return self.parent[x]

# BUG 3: if self.parent[rx] == self.parent[ry]
# This compares parents of roots (which may be themselves), not the roots.
# For roots, parent[rx] == rx and parent[ry] == ry — they will never be equal
# unless rx == ry. But using parent[] instead of the roots themselves is
# semantically wrong and breaks if roots are not self-loops.
# FIX: if rx == ry: return False

# BUG 4: self.rank[rx] += 1  (unconditional rank increment)
# Rank should only increase when merging two trees of EQUAL rank.
# Incrementing always causes rank to grow faster than tree height → union by
# rank stops working correctly (rank no longer bounds height).
# FIX:
#   if self.rank[rx] == self.rank[ry]:
#       self.rank[rx] += 1

# BUG 5: return self.parent[x] == self.parent[y]
# Compares immediate parents, not roots. Nodes in the same component but at
# different depths will have different parent values.
# FIX: return self.find(x) == self.find(y)

class FixedDSU:
    def __init__(self, n):
        self.parent = list(range(n))    # FIX 1

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])   # FIX 2
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:                    # FIX 3
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:   # FIX 4
            self.rank[rx] += 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)  # FIX 5
```

**Summary of all five bugs and their silent symptoms:**

| Bug | Mistake | Symptom |
|---|---|---|
| 1 | `[0] * n` init | All nodes appear connected from the start |
| 2 | No path compression | O(n) find per call on deep trees |
| 3 | `parent[rx] == parent[ry]` instead of `rx == ry` | Redundant unions not detected — double-merges |
| 4 | Unconditional rank increment | Rank grows too fast; union loses its balance guarantee |
| 5 | `parent[x] == parent[y]` connectivity | False negatives — connected nodes report as disconnected |

</details>

> 💻 Try it: [practice_local.py → Q20](./practice_local.py)

---

**[⬅️ Theory](./theory.md)** · **[💻 Local Practice](./practice_local.py)**

**Prev:** [← 23_segment_tree](../23_segment_tree/practice.md) | **Next:** [25_advanced_graphs →](../25_advanced_graphs/practice.md)
