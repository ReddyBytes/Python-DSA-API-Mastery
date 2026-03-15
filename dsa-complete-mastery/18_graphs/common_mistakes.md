# Graphs — Common Mistakes & Error Prevention

---

## Mistake 1: Not Marking Nodes as Visited BEFORE Adding to Queue in BFS

### The Bug
If you mark a node as visited only when you POP it from the queue, other nodes
can add it to the queue multiple times before it gets popped. In dense graphs
this causes exponential redundant work, and in graphs with cycles it causes
an infinite loop.

### Wrong Code
```python
from collections import deque

def bfs_wrong(graph, start):
    visited = set()
    queue = deque([start])

    while queue:
        node = queue.popleft()
        visited.add(node)              # BUG: mark visited only when POPPED

        for neighbor in graph[node]:
            if neighbor not in visited:
                queue.append(neighbor) # neighbor might already be in queue!

    return visited
```

### Correct Code
```python
from collections import deque

def bfs_correct(graph, start):
    visited = set([start])             # mark BEFORE adding to queue
    queue = deque([start])

    while queue:
        node = queue.popleft()

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)  # mark when PUSHED, not when popped
                queue.append(neighbor)

    return visited
```

### Concrete Example Where This Causes Duplicates
```
Graph: 1 -- 2, 1 -- 3, 2 -- 3

Adjacency list:
1: [2, 3]
2: [1, 3]
3: [1, 2]

WRONG (mark on pop), starting at 1:
Queue: [1]
Pop 1, mark 1. Neighbors: 2, 3. Push 2, 3. Queue: [2, 3]
Pop 2, mark 2. Neighbors: 1 (visited), 3 (NOT visited yet). Push 3. Queue: [3, 3]
Pop 3, mark 3. Neighbors: 1 (visited), 2 (visited). Queue: [3]
Pop 3. Already visited, but we process it again! Neighbors checked again.

Node 3 was in the queue TWICE. In larger graphs this compounds into
O(n^2) or worse queue entries.

CORRECT (mark on push):
Queue: [1], visited: {1}
Pop 1. Neighbors: 2 (unvisited -> push, mark), 3 (unvisited -> push, mark)
Queue: [2, 3], visited: {1, 2, 3}
Pop 2. Neighbors: 1 (visited), 3 (visited). Nothing pushed.
Pop 3. Neighbors: 1 (visited), 2 (visited). Nothing pushed.
Done. Each node processed exactly once.
```

### Test Cases That Expose the Bug
```python
from collections import deque

graph = {
    1: [2, 3],
    2: [1, 3, 4],
    3: [1, 2, 4],
    4: [2, 3]
}

# Track how many times each node is processed
def bfs_count_wrong(graph, start):
    visited = set()
    queue = deque([start])
    process_count = {}

    while queue:
        node = queue.popleft()
        visited.add(node)
        process_count[node] = process_count.get(node, 0) + 1

        for neighbor in graph[node]:
            if neighbor not in visited:
                queue.append(neighbor)

    return process_count

def bfs_count_correct(graph, start):
    visited = set([start])
    queue = deque([start])
    process_count = {}

    while queue:
        node = queue.popleft()
        process_count[node] = process_count.get(node, 0) + 1

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return process_count

wrong_counts = bfs_count_wrong(graph, 1)
correct_counts = bfs_count_correct(graph, 1)

print("Wrong BFS process counts:", wrong_counts)     # some nodes > 1
print("Correct BFS process counts:", correct_counts) # all nodes = 1

# Every node should be processed exactly once
for node, count in correct_counts.items():
    assert count == 1, f"Node {node} processed {count} times"
print("BFS visited-before-push test passed")
```

---

## Mistake 2: Using DFS for Shortest Path in an Unweighted Graph

### The Bug
DFS explores paths in depth-first order. The first path it finds to a node might
not be the shortest. BFS guarantees the shortest path in an unweighted graph
because it expands nodes level by level (by distance from the source).

### Wrong Code
```python
def shortest_path_dfs_wrong(graph, start, end):
    """Returns A path, but NOT guaranteed to be the shortest."""
    def dfs(node, path, visited):
        if node == end:
            return path
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                result = dfs(neighbor, path + [neighbor], visited)
                if result:
                    return result   # BUG: returns first path found, not shortest
        return None

    return dfs(start, [start], set())
```

### Correct Code — BFS for Shortest Path
```python
from collections import deque

def shortest_path_bfs_correct(graph, start, end):
    """Returns the shortest path in an unweighted graph."""
    if start == end:
        return [start]

    visited = {start}
    queue = deque([(start, [start])])

    while queue:
        node, path = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                new_path = path + [neighbor]
                if neighbor == end:
                    return new_path          # first time we reach end = shortest path
                visited.add(neighbor)
                queue.append((neighbor, new_path))

    return None  # no path exists
```

### Concrete Graph Where DFS Gives Wrong Answer
```
Graph:
    1
   / \
  2   3
  |   |
  4   5
   \ /
    6

Edges: 1-2, 1-3, 2-4, 3-5, 4-6, 5-6

Shortest path from 1 to 6: 1->2->4->6 or 1->3->5->6 (length 3)

DFS might explore: 1->2->4->6 (length 3) -- happens to be correct here, BUT:

Modified graph where DFS fails:
    1 -- 2 -- 3 -- 4
    |              |
    +------5-------+

Shortest: 1->5->4 (length 2)
DFS might go: 1->2->3->4 (length 3) -- returns this FIRST, misses the shorter path.
```

### Test Cases That Expose the Bug
```python
from collections import deque

# Graph where DFS order gives a longer path than BFS
graph = {
    1: [2, 5],    # DFS explores 2 first (longer path)
    2: [1, 3],
    3: [2, 4],
    4: [3, 5],
    5: [1, 4]     # shorter path: 1->5->4
}

dfs_path = shortest_path_dfs_wrong(graph, 1, 4)
bfs_path = shortest_path_bfs_correct(graph, 1, 4)

print("DFS path:", dfs_path, "length:", len(dfs_path) - 1)
print("BFS path:", bfs_path, "length:", len(bfs_path) - 1)

assert len(bfs_path) - 1 == 2, f"BFS should give length 2, got {len(bfs_path)-1}"
assert len(dfs_path) - 1 >= 2, "DFS may give longer path"

# The BFS path is guaranteed shortest
if len(dfs_path) != len(bfs_path):
    print("BUG CONFIRMED: DFS gave a longer path than BFS")
else:
    print("Lucky: DFS happened to find shortest path this time (not guaranteed)")
```

---

## Mistake 3: Cycle Detection in Directed Graphs — visited Is Not Enough

### The Bug
In a directed graph, a node can be reachable via multiple paths that share no edges.
Using only a `visited` set flags a node as "in a cycle" just because it was seen
before, even if the current DFS path never touches it again. You need an `in_stack`
set (or WHITE/GRAY/BLACK coloring) to track whether a node is on the CURRENT path.

### Wrong Code
```python
def has_cycle_directed_wrong(graph, n):
    visited = set()

    def dfs(node):
        visited.add(node)
        for neighbor in graph.get(node, []):
            if neighbor in visited:
                return True            # BUG: fires on ANY revisit, even through
            if dfs(neighbor):          # a completely separate path
                return True
        return False

    for node in range(n):
        if node not in visited:
            if dfs(node):
                return True
    return False
```

### Wrong — Specific Example
```
Graph: 0->1, 0->2, 1->3, 2->3
No cycle! Node 3 is reachable from both 1 and 2, but there is no back edge.

Wrong DFS from 0:
  Visit 0, then 1, then 3. Mark all visited. Backtrack.
  From 0, visit 2. 2's neighbor is 3. 3 is in visited -> returns True (FALSE POSITIVE).
```

### Correct Code — Using in_stack
```python
def has_cycle_directed_correct(graph, n):
    visited = set()
    in_stack = set()   # nodes on the CURRENT DFS path (call stack)

    def dfs(node):
        visited.add(node)
        in_stack.add(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in in_stack:     # back edge — actual cycle
                return True

        in_stack.remove(node)   # leaving this node's DFS subtree
        return False

    for node in range(n):
        if node not in visited:
            if dfs(node):
                return True
    return False
```

### Correct Code — WHITE/GRAY/BLACK Coloring (Equivalent, More Readable)
```python
def has_cycle_coloring(graph, n):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n

    def dfs(node):
        color[node] = GRAY          # currently being processed

        for neighbor in graph.get(node, []):
            if color[neighbor] == GRAY:
                return True         # back edge to current path = cycle
            if color[neighbor] == WHITE:
                if dfs(neighbor):
                    return True

        color[node] = BLACK         # fully processed, no cycle through this node
        return False

    for node in range(n):
        if color[node] == WHITE:
            if dfs(node):
                return True
    return False
```

### Test Cases That Expose the Bug
```python
# Diamond graph -- no cycle, but wrong version gives false positive
# 0->1, 0->2, 1->3, 2->3
diamond = {0: [1, 2], 1: [3], 2: [3], 3: []}

assert has_cycle_directed_wrong(diamond, 4) == True   # FALSE POSITIVE (bug!)
assert has_cycle_directed_correct(diamond, 4) == False, "Diamond has no cycle"
assert has_cycle_coloring(diamond, 4) == False, "Diamond has no cycle"
print("Diamond (no cycle) test:")
print("  Wrong:", has_cycle_directed_wrong(diamond, 4))    # True (wrong!)
print("  Correct:", has_cycle_directed_correct(diamond, 4)) # False (correct)

# Actual cycle: 0->1->2->0
cycle_graph = {0: [1], 1: [2], 2: [0]}
assert has_cycle_directed_correct(cycle_graph, 3) == True
assert has_cycle_coloring(cycle_graph, 3) == True
print("Actual cycle test passed")

# No edges
no_edge = {}
assert has_cycle_directed_correct(no_edge, 3) == False
print("No-edge test passed")
```

---

## Mistake 4: Dijkstra — Processing Stale Queue Entries

### The Bug
When Dijkstra relaxes an edge and pushes a new (shorter) distance to the heap,
the OLD (longer) distance entry for the same node remains in the heap. When that
stale entry is eventually popped, processing it can incorrectly relax neighbors
using an outdated (larger) distance. Always skip entries where the popped distance
is greater than the known best distance.

### Wrong Code
```python
import heapq

def dijkstra_wrong(graph, start, n):
    dist = [float('inf')] * n
    dist[start] = 0
    heap = [(0, start)]

    while heap:
        d, u = heapq.heappop(heap)
        # BUG: no stale-entry check. If dist[u] was already improved
        # to something smaller, this entry is outdated but we still process it.

        for weight, v in graph.get(u, []):
            if dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                heapq.heappush(heap, (dist[v], v))

    return dist
```

### Why It's Wrong
```
Suppose we process node 3 with distance 10 (stale).
We already found dist[3] = 5 earlier and pushed (5, 3) which was already popped.
Now (10, 3) is popped. We try to relax neighbors with d=10, even though
the true shortest distance is 5. This might push worse distances for neighbors.

In simple graphs this produces correct results by accident -- but in
graphs where stale entries cause multiple updates to the same node,
correctness is not guaranteed and performance degrades to O(n^2).
```

### Correct Code
```python
import heapq

def dijkstra_correct(graph, start, n):
    dist = [float('inf')] * n
    dist[start] = 0
    heap = [(0, start)]

    while heap:
        d, u = heapq.heappop(heap)

        # SKIP stale entries -- this node was already processed with a shorter distance
        if d > dist[u]:
            continue

        for weight, v in graph.get(u, []):
            new_dist = d + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))

    return dist
```

### Test Cases That Expose the Bug
```python
import heapq

# Graph where multiple shorter paths are found for the same node
# 0 -> 1 (weight 10)
# 0 -> 2 (weight 1)
# 2 -> 1 (weight 1)
# Total shortest to 1: 0->2->1 = 2

graph = {
    0: [(10, 1), (1, 2)],
    1: [],
    2: [(1, 1)]
}

wrong_dist = dijkstra_wrong(graph, 0, 3)
correct_dist = dijkstra_correct(graph, 0, 3)

print("Wrong distances:", wrong_dist)
print("Correct distances:", correct_dist)

assert correct_dist[1] == 2, f"Expected 2, got {correct_dist[1]}"
assert correct_dist[2] == 1

# Larger graph to show the pattern holds
graph2 = {i: [(1, i+1), (100, i+2)] for i in range(100)}
dist2 = dijkstra_correct(graph2, 0, 103)
assert dist2[50] == 50
print("Dijkstra stale-skip test passed")
```

---

## Mistake 5: Forgetting to Handle Disconnected Graphs

### The Bug
Starting BFS or DFS from a single node only explores the connected component
containing that node. If the graph is disconnected, other components are never
visited and you miss nodes, get wrong counts, or give incorrect "no path" answers
for nodes in other components.

### Wrong Code
```python
from collections import deque

def count_components_wrong(graph, n):
    """Count the number of connected components."""
    visited = set()
    queue = deque([0])    # BUG: always starts from node 0
    visited.add(0)

    while queue:
        node = queue.popleft()
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return 1    # BUG: always returns 1, doesn't loop over all components
```

### Correct Code
```python
from collections import deque

def count_components_correct(graph, n):
    """Count connected components by starting BFS from every unvisited node."""
    visited = set()
    components = 0

    for start in range(n):
        if start not in visited:
            components += 1             # found a new unvisited component
            queue = deque([start])
            visited.add(start)

            while queue:
                node = queue.popleft()
                for neighbor in graph.get(node, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

    return components
```

### Correct Code — Find All Components with Contents
```python
def find_all_components(graph, n):
    """Returns a list of lists, each inner list is one connected component."""
    visited = set()
    components = []

    def dfs(node, component):
        visited.add(node)
        component.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, component)

    for node in range(n):
        if node not in visited:
            component = []
            dfs(node, component)
            components.append(sorted(component))

    return components
```

### Test Cases That Expose the Bug
```python
# Disconnected graph: {0,1,2} and {3,4} are separate components
graph = {
    0: [1, 2],
    1: [0, 2],
    2: [0, 1],
    3: [4],
    4: [3]
}
n = 5

wrong_count = count_components_wrong(graph, n)
correct_count = count_components_correct(graph, n)

print("Wrong component count:", wrong_count)     # 1 (misses {3,4})
print("Correct component count:", correct_count) # 2

assert wrong_count == 1, "Wrong version sees only 1 component (misses {3,4})"
assert correct_count == 2, f"Expected 2 components, got {correct_count}"

# Find all components
all_comp = find_all_components(graph, n)
assert sorted(all_comp) == [[0, 1, 2], [3, 4]], f"Got {all_comp}"
print("Component contents:", all_comp)

# Fully disconnected (no edges)
isolated = {}
assert count_components_correct(isolated, 4) == 4   # 4 isolated nodes
print("All disconnected graph tests passed")
```

---

## Mistake 6: Building Adjacency List Incorrectly for Undirected Graphs

### The Bug
An undirected edge between nodes u and v means you can traverse from u to v
AND from v to u. Forgetting to add both directions makes the graph behave as
directed — nodes become unreachable and traversals give wrong results.

### Wrong Code
```python
def build_graph_wrong(edges, n):
    graph = {i: [] for i in range(n)}
    for u, v in edges:
        graph[u].append(v)    # BUG: only one direction
        # Missing: graph[v].append(u)
    return graph
```

### Correct Code
```python
def build_graph_correct(edges, n):
    graph = {i: [] for i in range(n)}
    for u, v in edges:
        graph[u].append(v)    # forward direction
        graph[v].append(u)    # backward direction -- REQUIRED for undirected
    return graph
```

### Correct Code — For Weighted Undirected Graphs
```python
def build_weighted_graph(edges, n):
    # edges = [(u, v, weight), ...]
    graph = {i: [] for i in range(n)}
    for u, v, w in edges:
        graph[u].append((w, v))
        graph[v].append((w, u))    # both directions with same weight
    return graph
```

### Correct Code — Using defaultdict
```python
from collections import defaultdict

def build_graph_defaultdict(edges):
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    return graph
```

### Test Cases That Expose the Bug
```python
from collections import deque

edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
n = 4

wrong_graph = build_graph_wrong(edges, n)
correct_graph = build_graph_correct(edges, n)

print("Wrong graph:", dict(wrong_graph))
# {0: [1], 1: [2], 2: [3], 3: [0]} -- can only traverse in one direction!

print("Correct graph:", dict(correct_graph))
# {0: [1, 3], 1: [0, 2], 2: [1, 3], 3: [2, 0]} -- bidirectional

def bfs_reachable(graph, start):
    visited = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return visited

wrong_from_2 = bfs_reachable(wrong_graph, 2)
correct_from_2 = bfs_reachable(correct_graph, 2)
print("Wrong graph reachable from 2:", wrong_from_2)     # {2, 3, 0} -- misses 1!
print("Correct graph reachable from 2:", correct_from_2) # {0, 1, 2, 3}

assert correct_from_2 == {0, 1, 2, 3}
assert wrong_from_2 != {0, 1, 2, 3}, "Wrong graph should miss some nodes"
print("Undirected graph construction test passed")
```

---

## Quick Reference Summary

| Mistake | Root Cause | One-Line Fix |
|---|---|---|
| BFS marks visited on pop | Nodes added to queue multiple times | Mark visited when PUSHED to queue |
| DFS for shortest path | DFS finds A path, not the shortest | BFS guarantees shortest in unweighted graph |
| `visited` only for directed cycle | Sibling paths trigger false cycle detection | Use `in_stack` set for current DFS path |
| No stale-entry skip in Dijkstra | Old heap entries processed with wrong distance | `if d > dist[u]: continue` at top of loop |
| BFS from single source only | Misses disconnected components | Loop over all nodes, start from unvisited ones |
| One-directional adjacency list | Undirected graph becomes directed | Add both `adj[u].append(v)` and `adj[v].append(u)` |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Real World Usage](./real_world_usage.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)
