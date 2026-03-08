# Disjoint Set Union (Union-Find) — Cheatsheet

---

## Use Cases

| Problem                            | DSU Application                          |
|------------------------------------|------------------------------------------|
| Connected components               | Union nodes, count unique roots          |
| Cycle detection (undirected)       | If find(u) == find(v) before union       |
| Kruskal's MST                      | Union edges in weight order, skip cycles |
| Number of provinces / islands      | Union adjacent cells/nodes               |
| Accounts merge                     | Union same-email accounts                |
| Redundant connection               | First edge where both endpoints share root |
| Smallest string with swaps         | Union swappable indices, sort each component |

---

## Complexity

| Operation         | Naive    | With Path Compression | With Both Optimizations |
|-------------------|----------|-----------------------|-------------------------|
| Find              | O(n)     | O(log n) amortized    | O(α(n)) ≈ O(1)          |
| Union             | O(n)     | O(log n) amortized    | O(α(n)) ≈ O(1)          |
| Space             | O(n)     | O(n)                  | O(n)                    |

α(n) = inverse Ackermann function — practically ≤ 4 for any realistic n.

---

## DSU Implementation Template

```python
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))   # each node is its own parent
        self.rank   = [0] * n          # or use size: self.size = [1] * n
        self.components = n            # track number of components

    def find(self, x):
        # Path compression: point all nodes directly to root
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False              # already connected (cycle!)
        # Union by rank: attach smaller tree under larger tree
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.components -= 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)
```

### Union by Size (alternative to rank)

```python
def union(self, x, y):
    rx, ry = self.find(x), self.find(y)
    if rx == ry: return False
    if self.size[rx] < self.size[ry]:
        rx, ry = ry, rx
    self.parent[ry] = rx
    self.size[rx] += self.size[ry]
    self.components -= 1
    return True
```

---

## Find Connected Components

```python
def count_components(n, edges):
    dsu = DSU(n)
    for u, v in edges:
        dsu.union(u, v)
    return dsu.components

# Get all components as groups
from collections import defaultdict
def get_component_groups(n, edges):
    dsu = DSU(n)
    for u, v in edges:
        dsu.union(u, v)
    groups = defaultdict(list)
    for i in range(n):
        groups[dsu.find(i)].append(i)
    return list(groups.values())
```

---

## Cycle Detection in Undirected Graph

```python
def has_cycle(n, edges):
    dsu = DSU(n)
    for u, v in edges:
        if not dsu.union(u, v):  # union returns False when already connected
            return True           # found cycle
    return False

# Find the redundant edge (LeetCode 684)
def find_redundant_connection(edges):
    n = len(edges)
    dsu = DSU(n + 1)
    for u, v in edges:
        if not dsu.union(u, v):
            return [u, v]
```

---

## Kruskal's MST with DSU

```python
def kruskal_mst(n, edges):
    # edges: list of (weight, u, v)
    edges.sort()                    # sort by weight ascending
    dsu = DSU(n)
    mst_weight = 0
    mst_edges = []

    for weight, u, v in edges:
        if dsu.union(u, v):         # no cycle
            mst_weight += weight
            mst_edges.append((u, v))
            if len(mst_edges) == n - 1:
                break               # MST complete (n-1 edges)

    return mst_weight, mst_edges
# Time: O(E log E) for sorting + O(E α(V)) for DSU ops
```

---

## Accounts Merge Pattern

```python
def accounts_merge(accounts):
    from collections import defaultdict
    email_to_id = {}
    dsu = DSU(len(accounts) * 10 + 1)  # over-allocate

    # Assign each unique email an ID, union all emails in same account
    email_id = 0
    for account in accounts:
        first_email_id = None
        for email in account[1:]:           # skip account name
            if email not in email_to_id:
                email_to_id[email] = email_id
                email_id += 1
            if first_email_id is None:
                first_email_id = email_to_id[email]
            else:
                dsu.union(first_email_id, email_to_id[email])

    # Group emails by root
    id_to_name = {}
    root_to_emails = defaultdict(set)
    for account in accounts:
        for email in account[1:]:
            eid = email_to_id[email]
            root = dsu.find(eid)
            root_to_emails[root].add(email)
            id_to_name[root] = account[0]  # may overwrite, same name

    return [[id_to_name[root]] + sorted(emails)
            for root, emails in root_to_emails.items()]
```

---

## Common Interview Patterns

```python
# Number of provinces (LeetCode 547)
def find_circle_num(is_connected):
    n = len(is_connected)
    dsu = DSU(n)
    for i in range(n):
        for j in range(i+1, n):
            if is_connected[i][j]:
                dsu.union(i, j)
    return dsu.components

# Number of islands using DSU (LeetCode 200)
def num_islands(grid):
    if not grid: return 0
    m, n = len(grid), len(grid[0])
    dsu = DSU(m * n)
    count = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == '1':
                count += 1
    for i in range(m):
        for j in range(n):
            if grid[i][j] == '1':
                for di, dj in [(0,1),(1,0)]:
                    ni, nj = i+di, j+dj
                    if 0<=ni<m and 0<=nj<n and grid[ni][nj]=='1':
                        if dsu.union(i*n+j, ni*n+nj):
                            count -= 1
    return count

# Smallest string with swaps (LeetCode 1202)
def smallest_string_with_swaps(s, pairs):
    from collections import defaultdict
    n = len(s)
    dsu = DSU(n)
    for u, v in pairs:
        dsu.union(u, v)
    groups = defaultdict(list)
    for i in range(n):
        groups[dsu.find(i)].append(i)
    res = list(s)
    for indices in groups.values():
        chars = sorted(res[i] for i in indices)
        for i, c in zip(sorted(indices), chars):
            res[i] = c
    return ''.join(res)
```

---

## Gotchas

- Always use `find()` (with path compression), never access `parent[]` directly
- Union by rank/size prevents degenerate linear chains — both needed for O(α(n))
- `union()` returns `False` if already connected — use this for cycle detection
- For grid problems: convert 2D index to 1D: `i * num_cols + j`
- Weighted DSU (for relative relationships): store weight/offset in parent edge
- After path compression, `parent[x]` points directly to root — intermediate parents may be stale
- DSU does not support splitting (unioning is permanent)
