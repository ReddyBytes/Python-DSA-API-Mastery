# Graphs — Practice Questions

> 25 questions covering representations, traversal, cycle detection, topological sort,
> shortest paths, and classic LeetCode-style graph problems.
>
> Work through each question. Try to code before expanding the answer.

---

## Quick Index

| # | Topic | Level |
|---|-------|-------|
| [Q1](#q1) | Adjacency list vs matrix — when to use which | Basic |
| [Q2](#q2) | Build an adjacency list from an edge list | Basic |
| [Q3](#q3) | Directed vs undirected representation | Basic |
| [Q4](#q4) | Weighted graph representation | Basic |
| [Q5](#q5) | BFS traversal — visit all nodes in level order | Basic |
| [Q6](#q6) | DFS traversal — recursive | Basic |
| [Q7](#q7) | DFS traversal — iterative | Basic |
| [Q8](#q8) | Path exists between two nodes | Basic |
| [Q9](#q9) | BFS shortest path in unweighted graph | Intermediate |
| [Q10](#q10) | Count connected components | Intermediate |
| [Q11](#q11) | Number of islands (grid BFS/DFS) | Intermediate |
| [Q12](#q12) | Cycle detection — undirected graph | Intermediate |
| [Q13](#q13) | Cycle detection — directed graph | Intermediate |
| [Q14](#q14) | Topological sort — Kahn's BFS | Intermediate |
| [Q15](#q15) | Topological sort — DFS post-order | Intermediate |
| [Q16](#q16) | Course Schedule I — can you finish? | Intermediate |
| [Q17](#q17) | Course Schedule II — return order | Intermediate |
| [Q18](#q18) | Bipartite check — BFS 2-coloring | Intermediate |
| [Q19](#q19) | Clone graph | Intermediate |
| [Q20](#q20) | Find all paths from source to target | Intermediate |
| [Q21](#q21) | Dijkstra's algorithm — weighted shortest path | Advanced |
| [Q22](#q22) | Network delay time (Dijkstra application) | Advanced |
| [Q23](#q23) | When BFS vs DFS — decision framework | Advanced |
| [Q24](#q24) | Mark visited before or after adding to queue? | Advanced |
| [Q25](#q25) | Directed cycle — why `visited` alone is wrong | Advanced |

---

## Basic

---

<a id="q1"></a>
### Q1 · Basic · Adjacency List vs Matrix

**Question:** You have a sparse graph with 1000 nodes and 1200 edges. Your friend has a dense graph with 50 nodes and 2400 edges. Which representation would you recommend for each, and why?

<details>
<summary>Hint</summary>
Compare space complexity: adjacency list is O(V+E), matrix is O(V²). Then think about the edge-to-node ratio.
</details>

<details>
<summary>Answer</summary>

**Sparse graph (1000 nodes, 1200 edges):** Use adjacency list.
- List: O(V+E) = O(2200) space.
- Matrix: O(V²) = O(1,000,000) space — 450x more memory for nearly no gain.

**Dense graph (50 nodes, 2400 edges):** Either works; matrix is fine here.
- List: O(V+E) = O(2450) space.
- Matrix: O(V²) = O(2500) space — nearly identical, and matrix gives O(1) edge lookup.

```python
# Adjacency list — default for most problems
from collections import defaultdict
graph = defaultdict(list)
for u, v in edges:
    graph[u].append(v)
    graph[v].append(u)  # undirected

# Adjacency matrix — best for dense or when O(1) edge lookup needed
n = 50
matrix = [[0] * n for _ in range(n)]
for u, v in edges:
    matrix[u][v] = 1
    matrix[v][u] = 1  # undirected
```

**Why:** Adjacency list is O(V+E) space vs O(V²) for matrix. For sparse graphs the matrix wastes memory. For dense graphs the difference disappears, and matrix gives O(1) "does edge u→v exist?" queries.

**Time/Space:** List — add edge O(1), neighbor lookup O(degree). Matrix — add edge O(1), edge query O(1), neighbor lookup O(V).
</details>

---

<a id="q2"></a>
### Q2 · Basic · Build Adjacency List

**Question:** Given `n` nodes (0 to n-1) and a list of undirected edges, build an adjacency list. Then print all neighbors of node 2.

Input: `n=5, edges=[(0,1),(0,2),(1,3),(2,3),(3,4)]`

<details>
<summary>Hint</summary>
Each undirected edge (u,v) needs two entries: graph[u] gets v, and graph[v] gets u.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q2
from collections import defaultdict

def build_graph(n, edges):
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)  # undirected: both directions
    return graph

n = 5
edges = [(0,1),(0,2),(1,3),(2,3),(3,4)]
graph = build_graph(n, edges)

print("Neighbors of 2:", graph[2])  # [0, 3]
print("Neighbors of 3:", graph[3])  # [1, 2, 4]
```

**Why:** Undirected edges are bidirectional — omitting `graph[v].append(u)` makes the graph behave as directed. This is one of the top 3 graph bugs in interviews.

**Time/Space:** O(V+E) space, O(1) per edge insert.
</details>

---

<a id="q3"></a>
### Q3 · Basic · Directed vs Undirected Representation

**Question:** You have these directed edges: `A→B, B→C, C→A` (a cycle). Build the adjacency list. Then explain what happens if you mistakenly treat this as undirected.

<details>
<summary>Hint</summary>
Directed: add only one direction. Undirected: add both. The cycle A→B→C→A is detectable by directed cycle detection but not obvious in undirected representation.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q3
# Directed: A→B→C→A
directed = {'A': ['B'], 'B': ['C'], 'C': ['A']}

# If you treated it as undirected by mistake:
undirected = {'A': ['B', 'C'], 'B': ['A', 'C'], 'C': ['B', 'A']}
# Now every node connects to every other — complete graph K3
# You've added spurious back-edges that didn't exist in the original
```

**Why it matters:** Directed cycle detection uses `in_stack` (recursion stack). If you add reverse edges, you create false connections. In course scheduling, `A→B` means "A must come before B" — adding `B→A` would say the opposite too, making every pair appear as a mutual dependency (cycle), so no valid ordering would be found.

**Time/Space:** O(V+E) for both.
</details>

---

<a id="q4"></a>
### Q4 · Basic · Weighted Graph Representation

**Question:** Build an adjacency list for a weighted directed graph. Edges: `(0→1, weight=4), (0→2, weight=1), (2→1, weight=2), (1→3, weight=3)`. What is the cheapest path from 0 to 1?

<details>
<summary>Hint</summary>
Store `(neighbor, weight)` tuples. The cheapest path is 0→2→1 = 1+2 = 3, not 0→1 = 4.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q4
from collections import defaultdict

graph = defaultdict(list)
edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 3)]

for u, v, w in edges:
    graph[u].append((v, w))   # (neighbor, weight)

print(graph[0])  # [(1, 4), (2, 1)]
print(graph[2])  # [(1, 2)]

# Cheapest path 0→1:
# Direct:     0→1 = 4
# Via 2:      0→2→1 = 1 + 2 = 3  ← cheaper
# BFS won't find this — need Dijkstra for weighted shortest path
```

**Why:** BFS treats all edges as equal. When weights differ, you need Dijkstra (non-negative) or Bellman-Ford (allows negative) to find the true shortest weighted path.

**Time/Space:** Adjacency list O(V+E), Dijkstra O((V+E) log V).
</details>

---

<a id="q5"></a>
### Q5 · Basic · BFS Traversal

**Question:** Implement BFS on this graph starting from node 1. List the visit order.

```
Graph: 1-2, 1-3, 2-4, 2-5, 3-6
```

<details>
<summary>Hint</summary>
Use a deque. Mark visited when PUSHING to queue (not when popping). Process level by level.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q5
from collections import deque

graph = {1:[2,3], 2:[1,4,5], 3:[1,6], 4:[2], 5:[2], 6:[3]}

def bfs(graph, start):
    visited = {start}         # mark on push, not pop
    queue = deque([start])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)   # mark BEFORE pushing
                queue.append(neighbor)

    return order

print(bfs(graph, 1))  # [1, 2, 3, 4, 5, 6]
```

Visit order: 1 → 2 → 3 → 4 → 5 → 6 (level by level).

**Why:** BFS explores all nodes at distance 1 before distance 2. This guarantees that when you first reach a node, you've taken the shortest path.

**Time/Space:** O(V+E) time, O(V) space for visited + queue.
</details>

---

<a id="q6"></a>
### Q6 · Basic · DFS Traversal Recursive

**Question:** Implement recursive DFS on the same graph from Q5, starting from node 1.

<details>
<summary>Hint</summary>
Pass `visited` set through recursion. Mark node at entry. Return when no unvisited neighbors remain.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q6
graph = {1:[2,3], 2:[1,4,5], 3:[1,6], 4:[2], 5:[2], 6:[3]}

def dfs(graph, node, visited=None):
    if visited is None:
        visited = set()
    visited.add(node)
    print(node, end=' ')
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)

dfs(graph, 1)  # 1 2 4 5 3 6
```

Visit order: 1 → 2 → 4 → 5 → 3 → 6 (goes deep before exploring siblings).

**Why:** DFS commits to the first unvisited neighbor and follows it all the way down before backtracking. Contrast with BFS which fans out breadth-first.

**Time/Space:** O(V+E) time, O(V) stack depth in worst case.
</details>

---

<a id="q7"></a>
### Q7 · Basic · DFS Traversal Iterative

**Question:** Implement iterative DFS using an explicit stack. Why might you prefer this over recursive DFS in production?

<details>
<summary>Hint</summary>
Use a stack and pop (LIFO). Mark visited when you pop. Python's default recursion limit is 1000 — iterative avoids stack overflow on deep graphs.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q7
graph = {1:[2,3], 2:[1,4,5], 3:[1,6], 4:[2], 5:[2], 6:[3]}

def dfs_iterative(graph, start):
    visited = set()
    stack = [start]
    order = []

    while stack:
        node = stack.pop()        # LIFO
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                stack.append(neighbor)

    return order

print(dfs_iterative(graph, 1))   # [1, 3, 6, 2, 5, 4] — order depends on push order
```

**Why iterative is preferred in production:** Python's default recursion limit is 1000 (`sys.getrecursionlimit()`). A deep graph with 10,000 nodes would cause `RecursionError`. Iterative DFS uses heap memory (explicit stack) instead of the call stack, which is virtually unlimited.

**Time/Space:** O(V+E) time, O(V) space.
</details>

---

<a id="q8"></a>
### Q8 · Basic · Path Exists Between Two Nodes

**Question:** Given a graph and two nodes `src` and `dst`, return `True` if any path exists from `src` to `dst`.

Input: `graph = {0:[1,2], 1:[3], 2:[3], 3:[]}`, `src=0, dst=3`

<details>
<summary>Hint</summary>
BFS or DFS both work. If you reach dst during traversal, return True. If traversal ends without reaching dst, return False.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q8
from collections import deque

def has_path(graph, src, dst):
    if src == dst:
        return True
    visited = {src}
    queue = deque([src])

    while queue:
        node = queue.popleft()
        if node == dst:
            return True
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return False

graph = {0:[1,2], 1:[3], 2:[3], 3:[]}
print(has_path(graph, 0, 3))  # True
print(has_path(graph, 3, 0))  # False — directed graph, can't go backwards
```

**Why:** BFS/DFS both answer "is dst reachable from src?" in O(V+E). Use BFS if you also need the shortest path. Use DFS if you just need existence — slightly simpler to implement recursively.

**Time/Space:** O(V+E) time, O(V) space.
</details>

---

## Intermediate

---

<a id="q9"></a>
### Q9 · Intermediate · BFS Shortest Path Unweighted

**Question:** Find the shortest path (fewest edges) between two nodes in an unweighted graph. Return the path, not just the distance.

Input: `graph = {0:[1,2], 1:[0,3], 2:[0,3,4], 3:[1,2,5], 4:[2,5], 5:[3,4]}`, `start=0, end=5`

<details>
<summary>Hint</summary>
Store (node, path) in the queue instead of just (node, distance). The first time you reach `end`, the path is guaranteed to be shortest.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q9
from collections import deque

def bfs_shortest_path(graph, start, end):
    if start == end:
        return [start]

    visited = {start}
    queue = deque([(start, [start])])   # (node, path so far)

    while queue:
        node, path = queue.popleft()

        for neighbor in graph[node]:
            if neighbor not in visited:
                new_path = path + [neighbor]
                if neighbor == end:
                    return new_path          # first time = shortest
                visited.add(neighbor)
                queue.append((neighbor, new_path))

    return None  # no path

graph = {0:[1,2], 1:[0,3], 2:[0,3,4], 3:[1,2,5], 4:[2,5], 5:[3,4]}
print(bfs_shortest_path(graph, 0, 5))  # [0, 2, 4, 5] or [0, 2, 3, 5] — length 3
```

**Why:** BFS visits nodes in order of distance from the source. The first time you reach `end`, you've necessarily taken the shortest path. DFS can't guarantee this.

**Time/Space:** O(V+E) time, O(V * path_length) space for storing paths.
</details>

---

<a id="q10"></a>
### Q10 · Intermediate · Connected Components Count

**Question:** Given an undirected graph with `n` nodes (0 to n-1), count the number of connected components.

Input: `n=6, edges=[(0,1),(1,2),(3,4)]` → Expected: 3 (components: {0,1,2}, {3,4}, {5})

<details>
<summary>Hint</summary>
Loop over all nodes. If a node is unvisited, start a BFS/DFS from it and count that as one new component.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q10
from collections import defaultdict, deque

def count_components(n, edges):
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    visited = set()
    count = 0

    for node in range(n):
        if node not in visited:
            count += 1
            # BFS to mark entire component
            queue = deque([node])
            visited.add(node)
            while queue:
                curr = queue.popleft()
                for neighbor in graph[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

    return count

print(count_components(6, [(0,1),(1,2),(3,4)]))  # 3
```

**Why:** You must start BFS/DFS from EVERY unvisited node. Starting from only node 0 and calling it done is the most common bug — it misses disconnected components entirely.

**Time/Space:** O(V+E) time, O(V) space.
</details>

---

<a id="q11"></a>
### Q11 · Intermediate · Number of Islands

**Question:** Given a 2D grid of `'1'` (land) and `'0'` (water), count the number of islands. An island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically.

```
grid = [
  ["1","1","0","0","0"],
  ["1","1","0","0","0"],
  ["0","0","1","0","0"],
  ["0","0","0","1","1"]
]
```
Expected: 3

<details>
<summary>Hint</summary>
Treat the grid as a graph. Each land cell is a node; each adjacent land cell is an edge. Run DFS from every unvisited land cell and mark the whole island as visited. Count how many times you start a new DFS.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q11
def num_islands(grid):
    if not grid:
        return 0

    rows, cols = len(grid), len(grid[0])
    visited = set()
    count = 0

    def dfs(r, c):
        if (r < 0 or r >= rows or c < 0 or c >= cols
                or (r, c) in visited or grid[r][c] == '0'):
            return
        visited.add((r, c))
        dfs(r+1, c)
        dfs(r-1, c)
        dfs(r, c+1)
        dfs(r, c-1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1' and (r, c) not in visited:
                dfs(r, c)
                count += 1

    return count

grid = [
    ["1","1","0","0","0"],
    ["1","1","0","0","0"],
    ["0","0","1","0","0"],
    ["0","0","0","1","1"]
]
print(num_islands(grid))  # 3
```

**Why:** This is the connected components pattern applied to a 2D grid. Every land cell is a node; 4-directional adjacency defines edges. DFS "sinks" each island by marking it visited — no need for a separate visited grid if you mutate the input.

**Time/Space:** O(m×n) time and space.
</details>

---

<a id="q12"></a>
### Q12 · Intermediate · Cycle Detection Undirected

**Question:** Detect whether an undirected graph contains a cycle. Use DFS with parent tracking.

Input: `graph = {0:[1,2], 1:[0,2], 2:[0,1]}` → True (0-1-2-0)

<details>
<summary>Hint</summary>
In undirected DFS, each node has a parent (the node you came from). If you visit a neighbor that is already visited AND it's not your parent, you've found a back edge — a cycle.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q12
def has_cycle_undirected(graph, n):
    visited = set()

    def dfs(node, parent):
        visited.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor, node):
                    return True
            elif neighbor != parent:   # back edge to non-parent = cycle
                return True
        return False

    for node in range(n):
        if node not in visited:
            if dfs(node, -1):
                return True
    return False

graph = {0:[1,2], 1:[0,2], 2:[0,1]}
print(has_cycle_undirected(graph, 3))  # True

graph2 = {0:[1], 1:[0,2], 2:[1]}      # linear 0-1-2, no cycle
print(has_cycle_undirected(graph2, 3)) # False
```

**Why:** In undirected DFS, the edge back to your parent is not a cycle (you just came from there). A cycle only exists when you reach a VISITED node that is NOT your parent — that's a true back edge.

**Time/Space:** O(V+E) time, O(V) space.
</details>

---

<a id="q13"></a>
### Q13 · Intermediate · Cycle Detection Directed

**Question:** Detect a cycle in a DIRECTED graph. Why can't you use the same parent-tracking approach as undirected?

Input: `graph = {0:[1,2], 1:[2], 2:[0], 3:[]}` (cycle: 0→1→2→0)

<details>
<summary>Hint</summary>
You need an `in_stack` set that tracks nodes on the CURRENT DFS path. A visited node that is also in_stack = back edge = cycle. A visited node NOT in in_stack = already explored safely in a different branch.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q13
def has_cycle_directed(graph, n):
    visited = set()
    in_stack = set()    # nodes on the CURRENT DFS path

    def dfs(node):
        visited.add(node)
        in_stack.add(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in in_stack:   # back edge on current path = cycle
                return True

        in_stack.remove(node)   # leaving this path, remove from stack
        return False

    for node in range(n):
        if node not in visited:
            if dfs(node):
                return True
    return False

graph = {0:[1,2], 1:[2], 2:[0], 3:[]}
print(has_cycle_directed(graph, 4))   # True (0→1→2→0)

# Diamond — no cycle, but naive visited-only approach gives false positive
diamond = {0:[1,2], 1:[3], 2:[3], 3:[]}
print(has_cycle_directed(diamond, 4)) # False
```

**Why parent tracking fails for directed:** In `0→1, 0→2, 1→3, 2→3` (diamond), node 3 is reachable from both 1 and 2. When DFS reaches 3 via path 0→2→3, it sees "3 is already visited" and incorrectly reports a cycle. The `in_stack` set fixes this: 3 is visited but NOT on the current path, so it's not a cycle.

**Time/Space:** O(V+E) time, O(V) space.
</details>

---

<a id="q14"></a>
### Q14 · Intermediate · Topological Sort Kahn's BFS

**Question:** Implement Kahn's algorithm to topologically sort a DAG. Return empty list if a cycle exists.

`n=6, edges=[(5,2),(5,0),(4,0),(4,1),(2,3),(3,1)]`

<details>
<summary>Hint</summary>
1. Count in-degrees for all nodes. 2. Enqueue all nodes with in-degree 0. 3. Pop a node, append to result, decrement in-degree of its neighbors. If neighbor's in-degree hits 0, enqueue it. 4. If result length < n → cycle.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q14
from collections import deque, defaultdict

def topo_sort_kahn(n, edges):
    graph = defaultdict(list)
    in_degree = [0] * n

    for u, v in edges:
        graph[u].append(v)
        in_degree[v] += 1

    queue = deque([i for i in range(n) if in_degree[i] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return order if len(order) == n else []   # empty → cycle

edges = [(5,2),(5,0),(4,0),(4,1),(2,3),(3,1)]
print(topo_sort_kahn(6, edges))  # [4, 5, 0, 2, 3, 1] (one valid ordering)
```

**Why:** Kahn's processes nodes in dependency order — nodes with no remaining dependencies are always eligible next. If a cycle exists, the cyclic nodes never reach in-degree 0, so they never enter the queue and are absent from `order`.

**Time/Space:** O(V+E) time, O(V) space.
</details>

---

<a id="q15"></a>
### Q15 · Intermediate · Topological Sort DFS

**Question:** Implement DFS-based topological sort. How does this differ from Kahn's, and when would you choose one over the other?

<details>
<summary>Hint</summary>
In DFS topo sort, you append a node to result AFTER visiting all its descendants. Then reverse the result. The last node fully explored has no outgoing dependencies — it goes last.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q15
from collections import defaultdict

def topo_sort_dfs(n, edges):
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)

    visited = [0] * n    # 0=unvisited, 1=in-progress, 2=done
    result = []
    has_cycle = [False]

    def dfs(node):
        if visited[node] == 1:   # back edge = cycle
            has_cycle[0] = True
            return
        if visited[node] == 2:   # already fully processed
            return
        visited[node] = 1
        for neighbor in graph[node]:
            dfs(neighbor)
        visited[node] = 2
        result.append(node)      # append AFTER all descendants visited

    for i in range(n):
        if visited[i] == 0:
            dfs(i)

    if has_cycle[0]:
        return []
    return result[::-1]   # reverse: DFS appends in reverse topological order

edges = [(5,2),(5,0),(4,0),(4,1),(2,3),(3,1)]
print(topo_sort_dfs(6, edges))  # valid topological order
```

**Kahn's vs DFS:**
- Kahn's: natural BFS order, easier cycle detection (just check len), intuitive
- DFS: post-order traversal, slightly less code, finds lexicographically reverse order
- Both O(V+E) — choose Kahn's when cycle detection clarity matters

**Time/Space:** O(V+E) time, O(V) space.
</details>

---

<a id="q16"></a>
### Q16 · Intermediate · Course Schedule I

**Question (LeetCode 207):** Given `numCourses` and a list of `prerequisites` where `[a,b]` means "take b before a", return `True` if you can finish all courses.

Input: `numCourses=2, prerequisites=[[1,0]]` → True
Input: `numCourses=2, prerequisites=[[1,0],[0,1]]` → False (cycle)

<details>
<summary>Hint</summary>
Model as directed graph. If a cycle exists → impossible to finish. Use Kahn's: if topological sort produces all numCourses nodes, no cycle exists.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q16
from collections import deque

def can_finish(num_courses, prerequisites):
    graph = [[] for _ in range(num_courses)]
    in_degree = [0] * num_courses

    for a, b in prerequisites:
        graph[b].append(a)    # b must come before a
        in_degree[a] += 1

    queue = deque(i for i in range(num_courses) if in_degree[i] == 0)
    completed = 0

    while queue:
        course = queue.popleft()
        completed += 1
        for next_course in graph[course]:
            in_degree[next_course] -= 1
            if in_degree[next_course] == 0:
                queue.append(next_course)

    return completed == num_courses   # True = no cycle, all courses reachable

print(can_finish(2, [[1,0]]))      # True
print(can_finish(2, [[1,0],[0,1]])) # False — cycle
```

**Why:** Cycle in prerequisite graph = deadlock. Course A needs B, B needs A — impossible. Kahn's topological sort naturally detects this: cyclic nodes never reach in-degree 0 and are never counted as completed.

**Time/Space:** O(V+E) time, O(V+E) space.
</details>

---

<a id="q17"></a>
### Q17 · Intermediate · Course Schedule II

**Question (LeetCode 210):** Same as Q16, but return the order in which to take courses (or `[]` if impossible).

<details>
<summary>Hint</summary>
Same as Kahn's algorithm — collect nodes as you pop them. The pop order IS the valid course order.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q17
from collections import deque

def find_order(num_courses, prerequisites):
    graph = [[] for _ in range(num_courses)]
    in_degree = [0] * num_courses

    for a, b in prerequisites:
        graph[b].append(a)
        in_degree[a] += 1

    queue = deque(i for i in range(num_courses) if in_degree[i] == 0)
    order = []

    while queue:
        course = queue.popleft()
        order.append(course)          # collect the order
        for next_course in graph[course]:
            in_degree[next_course] -= 1
            if in_degree[next_course] == 0:
                queue.append(next_course)

    return order if len(order) == num_courses else []

print(find_order(4, [[1,0],[2,0],[3,1],[3,2]]))  # [0, 1, 2, 3] or [0, 2, 1, 3]
print(find_order(2, [[1,0],[0,1]]))               # []
```

**Why:** The output of Kahn's algorithm IS a valid topological order. Each node is appended only when all its prerequisites are satisfied — exactly the valid course order.

**Time/Space:** O(V+E) time, O(V+E) space.
</details>

---

<a id="q18"></a>
### Q18 · Intermediate · Bipartite Check

**Question:** Determine if a graph is bipartite (can be 2-colored such that no two adjacent nodes share a color).

Input: `graph = [[1,3],[0,2],[1,3],[0,2]]` → True
Input: `graph = [[1,2,3],[0,2],[0,1,3],[0,2]]` → False (odd cycle)

<details>
<summary>Hint</summary>
BFS 2-coloring: assign color 0 to start. Every neighbor gets color `1 - current_color`. If a neighbor already has the same color as the current node, the graph is not bipartite.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q18
from collections import deque

def is_bipartite(graph):
    n = len(graph)
    color = [-1] * n    # -1 = uncolored

    for start in range(n):
        if color[start] != -1:
            continue    # already colored in a previous component

        queue = deque([start])
        color[start] = 0

        while queue:
            node = queue.popleft()
            for neighbor in graph[node]:
                if color[neighbor] == -1:
                    color[neighbor] = 1 - color[node]   # flip color
                    queue.append(neighbor)
                elif color[neighbor] == color[node]:     # conflict
                    return False

    return True

print(is_bipartite([[1,3],[0,2],[1,3],[0,2]]))           # True
print(is_bipartite([[1,2,3],[0,2],[0,1,3],[0,2]]))       # False
```

**Why:** A graph is bipartite if and only if it contains no odd-length cycle. BFS alternates colors layer by layer (layer 0 = color 0, layer 1 = color 1, etc.). An odd cycle forces two adjacent nodes into the same layer → same color → conflict detected.

**Time/Space:** O(V+E) time, O(V) space.
</details>

---

<a id="q19"></a>
### Q19 · Intermediate · Clone Graph

**Question (LeetCode 133):** Given a node in a connected undirected graph, return a deep copy of the graph. Each node has `val` and `neighbors`.

<details>
<summary>Hint</summary>
Use a hashmap `{original_node: cloned_node}`. BFS the original graph; for each original node, create its clone if not already done, then wire up its neighbors' clones.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q19
from collections import deque

class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

def clone_graph(node):
    if not node:
        return None

    cloned = {node: Node(node.val)}   # original → clone mapping
    queue = deque([node])

    while queue:
        curr = queue.popleft()
        for neighbor in curr.neighbors:
            if neighbor not in cloned:
                cloned[neighbor] = Node(neighbor.val)
                queue.append(neighbor)
            cloned[curr].neighbors.append(cloned[neighbor])   # wire neighbor

    return cloned[node]
```

**Why:** The hashmap prevents creating multiple clones of the same node when a node has multiple paths to it. We create the clone node first, then separately wire its neighbors — this handles cycles without infinite loops.

**Time/Space:** O(V+E) time (visit every node and edge once), O(V) space for the hashmap.
</details>

---

<a id="q20"></a>
### Q20 · Intermediate · Find All Paths Source to Target

**Question (LeetCode 797):** Given a DAG (nodes 0 to n-1, node n-1 is target), find all paths from node 0 to node n-1.

Input: `graph = [[1,2],[3],[3],[]]` → `[[0,1,3],[0,2,3]]`

<details>
<summary>Hint</summary>
DFS with backtracking. At each node, try every neighbor. When you reach the target, record the path. Backtrack (pop) after each recursive call to explore other branches.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q20
def all_paths_source_target(graph):
    target = len(graph) - 1
    results = []

    def dfs(node, path):
        if node == target:
            results.append(path[:])   # snapshot of current path
            return
        for neighbor in graph[node]:
            path.append(neighbor)
            dfs(neighbor, path)
            path.pop()               # BACKTRACK

    dfs(0, [0])
    return results

print(all_paths_source_target([[1,2],[3],[3],[]]))  # [[0,1,3],[0,2,3]]
```

**Why DFS not BFS:** You need to explore each path in full. BFS processes nodes level by level and doesn't naturally track which complete paths have been taken. DFS with backtracking is the canonical pattern for "enumerate all paths."

**Time/Space:** O(2^V * V) worst case (exponential paths in a DAG), O(V) stack depth.
</details>

---

## Advanced

---

<a id="q21"></a>
### Q21 · Advanced · Dijkstra's Algorithm

**Question:** Implement Dijkstra's algorithm to find shortest distances from a source node to all other nodes. Graph has non-negative weights.

Input: `graph = {0:[(1,4),(2,1)], 1:[(3,1)], 2:[(1,2),(3,5)], 3:[]}`, `start=0`
Expected distances: `{0:0, 1:3, 2:1, 3:4}`

<details>
<summary>Hint</summary>
Use a min-heap (priority queue). Always process the node with the smallest current known distance. Skip stale entries where the popped distance exceeds the recorded best distance.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q21
import heapq

def dijkstra(graph, start):
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    heap = [(0, start)]    # (distance, node)

    while heap:
        d, u = heapq.heappop(heap)

        if d > dist[u]:    # stale entry — skip
            continue

        for v, weight in graph[u]:
            new_dist = d + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))

    return dist

graph = {0:[(1,4),(2,1)], 1:[(3,1)], 2:[(1,2),(3,5)], 3:[]}
print(dijkstra(graph, 0))   # {0:0, 1:3, 2:1, 3:4}
# Path to 1: 0→2→1 = 1+2 = 3 (cheaper than direct 0→1 = 4)
```

**Why BFS fails here:** BFS finds shortest path by edge count, not by weight. In this graph, 0→1 has 1 edge but costs 4. The path 0→2→1 has 2 edges but costs only 3. BFS would return 0→1 (1 hop) as "shortest," which is wrong.

**Why stale-entry skip matters:** When we find a shorter path to node v, we push a new entry to the heap. The old (larger) entry stays in the heap. Without the `d > dist[u]` check, we'd process v again with the stale larger distance and might push incorrect updates to its neighbors.

**Time/Space:** O((V+E) log V) time, O(V) space.
</details>

---

<a id="q22"></a>
### Q22 · Advanced · Network Delay Time

**Question (LeetCode 743):** Given a network of `n` nodes (1 to n) and directed weighted edges `times[i] = [u, v, w]` (signal travels from u to v in w milliseconds), find the minimum time for a signal sent from `k` to reach ALL nodes. Return -1 if impossible.

<details>
<summary>Hint</summary>
This is Dijkstra from source `k`. The answer is `max(dist.values())` — the time to reach the last node. If any node is unreachable (dist = infinity), return -1.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q22
import heapq
from collections import defaultdict

def network_delay_time(times, n, k):
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))

    dist = {i: float('inf') for i in range(1, n+1)}
    dist[k] = 0
    heap = [(0, k)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))

    max_dist = max(dist.values())
    return max_dist if max_dist < float('inf') else -1

print(network_delay_time([[2,1,1],[2,3,1],[3,4,1]], 4, 2))   # 2
print(network_delay_time([[1,2,1]], 2, 2))                    # -1 (2 can't reach 1)
```

**Why:** The minimum time for ALL nodes to receive the signal equals the shortest-path distance to the FARTHEST node. Dijkstra computes all shortest distances from k in one pass. If any node remains at infinity, the signal can never reach it.

**Time/Space:** O((V+E) log V) time, O(V+E) space.
</details>

---

<a id="q23"></a>
### Q23 · Advanced · When BFS vs DFS

**Question:** For each scenario, choose BFS or DFS and explain your reasoning:
1. Find the shortest route in a maze (unweighted)
2. Detect if a dependency chain has a circular reference
3. Find all possible solutions in a sudoku solver
4. Check if a social network user is within 2 hops of another
5. Find if a course ordering is possible given prerequisites

<details>
<summary>Hint</summary>
BFS: shortest path, level-order, proximity. DFS: all paths, cycle detection, topological order, backtracking problems.
</details>

<details>
<summary>Answer</summary>

```
1. MAZE SHORTEST ROUTE → BFS
   BFS explores cells level-by-level (by distance). The first time it reaches
   the exit is guaranteed to be via the shortest path. DFS might find a route
   but not the shortest one.

2. CIRCULAR DEPENDENCY → DFS (with in_stack)
   Cycle detection in directed graphs needs DFS with a recursion stack. When
   DFS revisits a node that's still on the current path (in_stack), it found
   a back edge = cycle. Kahn's BFS also works (len(order) < n check).

3. SUDOKU SOLVER → DFS + backtracking
   You need to explore full assignments and undo choices. DFS with backtracking
   is the canonical approach: place a number, recurse, undo if it leads to
   contradiction. BFS would be impractical — the branching factor is too high
   and you'd carry too many partial states.

4. WITHIN 2 HOPS → BFS
   "Hops" = level/distance. BFS naturally tracks distance. Run BFS from the
   source, stop at depth 2, check if target was reached. DFS has no natural
   notion of "hop count."

5. COURSE ORDERING (PREREQUISITES) → Topological Sort
   Specifically Kahn's BFS-based topological sort. Model courses as nodes,
   prerequisites as directed edges. If topo sort succeeds (outputs all nodes),
   return the order. If it fails (cycle detected), return impossible.
```

**Core decision rule:**
- Need shortest path / closest / fewest steps → BFS
- Need all paths / detect cycle / ordering / backtracking → DFS

**Time/Space:** O(V+E) for both BFS and DFS.
</details>

---

<a id="q24"></a>
### Q24 · Advanced · Mark Visited Before or After Queue

**Question:** Show with a concrete graph why marking visited when POPPING from the BFS queue (instead of when PUSHING) leads to incorrect or slow behavior. Fix the code.

<details>
<summary>Hint</summary>
Draw this graph: nodes 1,2,3 where 1→2, 1→3, 2→3. If you mark visited on pop, by the time you pop node 3 from 2's neighbors, 3 may already be in the queue from 1's neighbors too.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q24
from collections import deque

# Graph: 1 connects to 2 and 3; 2 also connects to 3
graph = {1:[2,3], 2:[1,3], 3:[1,2]}

# WRONG — mark visited when popping
def bfs_wrong(graph, start):
    visited = set()
    queue = deque([start])
    process_count = {}

    while queue:
        node = queue.popleft()
        visited.add(node)              # too late — node may already be in queue
        process_count[node] = process_count.get(node, 0) + 1

        for neighbor in graph[node]:
            if neighbor not in visited:
                queue.append(neighbor) # 3 gets added TWICE (by 1 and by 2)

    return process_count

# CORRECT — mark visited when pushing
def bfs_correct(graph, start):
    visited = {start}
    queue = deque([start])
    process_count = {}

    while queue:
        node = queue.popleft()
        process_count[node] = process_count.get(node, 0) + 1

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)  # mark immediately on discovery
                queue.append(neighbor)

    return process_count

print("Wrong BFS counts:", bfs_wrong(graph, 1))    # node 3 processed 2 times!
print("Correct BFS counts:", bfs_correct(graph, 1)) # each node processed exactly 1 time
```

**Why this matters:** In the wrong version, node 3 is pushed to the queue twice (once by node 1, once by node 2) because neither has marked it visited yet. This doubles processing. In dense graphs this cascades: one node can be pushed O(E) times, degrading O(V+E) to O(V*E) or causing infinite loops with cycles.

**Rule to remember:** "Mark when you discover, not when you process."

**Time/Space:** O(V+E) correct, O(V*E) wrong in worst case.
</details>

---

<a id="q25"></a>
### Q25 · Advanced · Detect Cycle Visited Set Trap

**Question:** This code claims to detect a cycle in a directed graph, but has a critical bug. Identify it, show a concrete graph that exposes it, and write the correct version.

```python
def has_cycle_BUGGY(graph, n):
    visited = set()
    def dfs(node):
        visited.add(node)
        for neighbor in graph.get(node, []):
            if neighbor in visited:
                return True    # BUG HERE
            if dfs(neighbor):
                return True
        return False
    for node in range(n):
        if node not in visited:
            if dfs(node): return True
    return False
```

<details>
<summary>Hint</summary>
The "diamond" graph 0→1, 0→2, 1→3, 2→3 has no cycle, but this code returns True. Why? Node 3 is reached from both 1 and 2. When DFS reaches 3 via the second path, it's "already visited" but that doesn't mean a cycle — the first visit was a different branch.
</details>

<details>
<summary>Answer</summary>

```python
# See practice_local.py → Q25

# Diamond graph — NO cycle, but buggy code returns True (false positive)
# 0→1, 0→2, 1→3, 2→3
diamond = {0:[1,2], 1:[3], 2:[3], 3:[]}

# The bug: node 3 is visited via 0→1→3. When DFS backtracks to 0 and goes
# 0→2→3, it sees "3 is already visited" and returns True. But 3 is not on
# the CURRENT path — it was a previously completed branch. No cycle exists.

# FIX: Track in_stack separately from visited
def has_cycle_correct(graph, n):
    visited = set()
    in_stack = set()   # nodes currently on the active DFS path

    def dfs(node):
        visited.add(node)
        in_stack.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in in_stack:  # on current path = back edge = cycle
                return True
        in_stack.remove(node)   # leaving this path
        return False

    for node in range(n):
        if node not in visited:
            if dfs(node):
                return True
    return False

# Test the fix
diamond = {0:[1,2], 1:[3], 2:[3], 3:[]}
print("Diamond (no cycle):", has_cycle_correct(diamond, 4))  # False ✓

# Actual cycle: 0→1→2→0
cycle = {0:[1], 1:[2], 2:[0]}
print("Actual cycle:", has_cycle_correct(cycle, 3))           # True ✓
```

**Root cause of the bug:** `visited` means "was ever seen in any DFS branch." `in_stack` means "is currently on the active recursion path." A cycle requires finding a back edge — a path back to a node on the CURRENT path. Seeing a previously-visited node from a different branch is just sharing, not a cycle.

**Memory rule:** `visited` = "have I been here?" | `in_stack` = "am I still here right now?"

**Time/Space:** O(V+E) time, O(V) space.
</details>

---

**[Back to README](../README.md)**

**Prev:** [Interview Q&A](./interview.md) &nbsp;|&nbsp; **Next:** [Greedy — Theory](../19_greedy/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
