# Graphs — Real-World Usage

Graph algorithms are among the most widely deployed data structures in
production software. Whenever you have entities (nodes) and relationships
(edges), you have a graph. This file covers nine engineering domains and shows
the specific algorithm used in each, along with a Python sketch.

---

## 1. Social Networks — Friend Recommendations and Community Detection

**Algorithms:** BFS for recommendations, Union-Find / DFS for communities

Facebook, LinkedIn, and Twitter model their social graphs as directed or
undirected graphs where each user is a node and each relationship is an edge.

### Friend recommendations via BFS

The idea: people two hops away from you (friends of friends) are strong
recommendation candidates. BFS from your node, collect all nodes at depth 2
that are not already your friends.

```python
from collections import deque

def friend_recommendations(graph: dict, user: str, depth: int = 2) -> set:
    visited = {user}
    queue   = deque([(user, 0)])
    candidates = set()

    while queue:
        node, d = queue.popleft()
        if d == depth:
            if node != user and node not in graph[user]:
                candidates.add(node)
            continue
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, d + 1))
    return candidates
```

### Community detection via connected components

```python
def find_communities(graph: dict) -> list[list]:
    visited = set()
    communities = []

    def dfs(node, component):
        visited.add(node)
        component.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor, component)

    for node in graph:
        if node not in visited:
            component = []
            dfs(node, component)
            communities.append(component)
    return communities
```

**Where it runs:** Facebook friend suggestions, LinkedIn "People You May Know",
Twitter community clustering, Reddit subreddit recommendation.

---

## 2. Google Maps / Waze — Shortest Path with Dynamic Weights

**Algorithm:** Dijkstra for static maps, dynamic re-routing on traffic updates

Every intersection is a node. Every road segment is a weighted edge. The weight
is travel time, which Waze updates every 30 seconds from crowd-sourced reports.

```python
import heapq

def dijkstra(graph: dict, start: str, end: str) -> tuple[float, list]:
    dist  = {node: float('inf') for node in graph}
    prev  = {node: None         for node in graph}
    dist[start] = 0
    heap  = [(0.0, start)]

    while heap:
        d, u = heapq.heappop(heap)
        if u == end:
            break
        if d > dist[u]:
            continue
        for v, weight in graph[u]:
            nd = dist[u] + weight
            if nd < dist[v]:
                dist[v], prev[v] = nd, u
                heapq.heappush(heap, (nd, v))

    # Reconstruct path
    path, node = [], end
    while node:
        path.append(node)
        node = prev[node]
    return dist[end], path[::-1]

# Real-world addition:
# - A* uses a heuristic (straight-line distance) to guide search faster
# - Contraction Hierarchies pre-process the graph so queries run in ~1ms
# - Edge weights are updated live from GPS probe data and incident reports
```

**Where it runs:** Google Maps, Apple Maps, Waze, Uber/Lyft dispatch,
FedEx route planning, Amazon delivery scheduling.

---

## 3. Internet Routing — BGP and OSPF

**Algorithm:** Dijkstra (OSPF) and Bellman-Ford / path-vector (BGP)

Inside a data centre or campus network (OSPF), each router runs Dijkstra over
the known network topology to build its forwarding table. Between autonomous
systems on the public internet (BGP), a distributed variant runs continuously.

```python
def build_routing_table(topology: dict, this_router: str) -> dict:
    """
    topology[u] = [(cost, v), ...]   — OSPF link-state database
    Returns: {destination: (cost, next_hop)}
    """
    dist = {r: float('inf') for r in topology}
    next_hop = {r: None for r in topology}
    dist[this_router] = 0
    heap = [(0, this_router, this_router)]

    while heap:
        cost, u, hop = heapq.heappop(heap)
        if cost > dist[u]:
            continue
        for link_cost, v in topology[u]:
            new_cost = dist[u] + link_cost
            if new_cost < dist[v]:
                dist[v]     = new_cost
                next_hop[v] = hop if u == this_router else next_hop[u]
                heapq.heappush(heap, (new_cost, v, next_hop[v]))

    return {dest: (dist[dest], next_hop[dest]) for dest in topology}

# Each router re-runs this every time it receives a topology update (LSA).
# The result is stored in the FIB (Forwarding Information Base) in hardware.
```

**Where it runs:** Every enterprise router running OSPF or IS-IS, every ISP
router running BGP, AWS VPC routing, Kubernetes CNI plugins (Calico, Cilium).

---

## 4. Package Managers — Dependency Resolution

**Algorithm:** Topological sort (Kahn's algorithm or DFS post-order)

When you run `npm install` or `pip install`, the package manager builds a
directed acyclic graph (DAG) of dependencies and topologically sorts it to
determine the installation order. A package must be installed before anything
that depends on it.

### Dependency graph example

```
  my-app
  ├── react (v18)
  │   └── loose-envify
  │       └── js-tokens
  └── axios
      ├── follow-redirects
      └── form-data
          └── asynckit

Install order (one valid topological sort):
js-tokens → loose-envify → react →
asynckit → form-data → follow-redirects → axios → my-app
```

```python
from collections import deque

def topological_sort(packages: dict) -> list[str]:
    # packages[p] = [dependencies of p]
    in_degree = {p: 0 for p in packages}
    for p in packages:
        for dep in packages[p]:
            in_degree[dep] = in_degree.get(dep, 0)   # ensure key exists
            in_degree[p]  += 0                        # p depends on dep
    # Recompute: in_degree[p] = how many packages need p first (reversed)
    in_degree = {p: 0 for p in packages}
    rev = {p: [] for p in packages}
    for p, deps in packages.items():
        for dep in deps:
            rev[dep].append(p)
            in_degree[p] += 1

    queue  = deque(p for p in packages if in_degree[p] == 0)
    result = []
    while queue:
        p = queue.popleft()
        result.append(p)
        for dependent in rev[p]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    if len(result) != len(packages):
        raise ValueError("Circular dependency detected!")
    return result
```

**Where it runs:** npm, yarn, pip, cargo, apt/dpkg, Gradle, Maven, Bazel.

---

## 5. Fraud Detection — Graph Anomaly Detection

**Algorithm:** Connected components, BFS/DFS, graph centrality

Banks and payment processors model transactions as a bipartite graph: accounts
on one side, transactions on the other. Fraudulent rings appear as tightly
connected clusters with unusual structural properties.

```python
def find_suspicious_clusters(transaction_graph: dict,
                              min_cluster_size: int = 5,
                              max_cluster_size: int = 20) -> list[list]:
    """
    Flag clusters that are suspiciously small but highly interconnected —
    hallmark of a money-mule ring or card-testing network.
    """
    visited = set()
    suspicious = []

    def bfs_component(start):
        component = []
        queue = deque([start])
        visited.add(start)
        while queue:
            node = queue.popleft()
            component.append(node)
            for neighbor in transaction_graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return component

    for node in transaction_graph:
        if node not in visited:
            cluster = bfs_component(node)
            if min_cluster_size <= len(cluster) <= max_cluster_size:
                edge_count = sum(len(transaction_graph[n]) for n in cluster)
                density = edge_count / (len(cluster) * (len(cluster) - 1))
                if density > 0.6:          # unusually dense = suspicious
                    suspicious.append(cluster)
    return suspicious
```

**Where it runs:** PayPal fraud detection, Stripe Radar, Visa/Mastercard
transaction screening, bank AML (anti-money-laundering) systems.

---

## 6. Search Engines — PageRank

**Algorithm:** Random walk on the directed web graph (power iteration)

PageRank models the web as a directed graph where a link from page A to page B
is an edge. A "random surfer" follows links at random; pages that attract more
surfers get higher rank. This is solved as an eigenvector computation, which
converges via repeated matrix-vector multiplication — effectively DP on the
graph.

```python
def pagerank(graph: dict, damping: float = 0.85,
             iterations: int = 100) -> dict:
    nodes = list(graph.keys())
    N     = len(nodes)
    rank  = {n: 1 / N for n in nodes}

    out_degree = {n: len(graph[n]) for n in nodes}

    for _ in range(iterations):
        new_rank = {}
        for n in nodes:
            # Sum of rank donated by all pages pointing to n
            incoming = sum(
                rank[m] / out_degree[m]
                for m in nodes
                if n in graph[m] and out_degree[m] > 0
            )
            new_rank[n] = (1 - damping) / N + damping * incoming
        rank = new_rank
    return rank

# Production: sparse matrix + numpy makes this orders of magnitude faster.
# Google now uses neural ranking (BERT-based) on top of link-graph signals.
```

**Where it runs:** Google Search (original algorithm, now one of 200+
signals), academic citation ranking, Twitter influence scoring, Wikipedia
article importance.

---

## 7. Airline and Rail Networks — Minimum Spanning Tree

**Algorithm:** Kruskal's or Prim's MST

Airlines and rail operators use MST to answer: "what is the minimum-cost set of
routes that keeps every city connected?" This guides infrastructure planning,
hub placement, and cable/fibre laying.

```python
class UnionFind:
    def __init__(self, nodes):
        self.parent = {n: n for n in nodes}
        self.rank   = {n: 0 for n in nodes}

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry: return False
        if self.rank[rx] < self.rank[ry]: rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]: self.rank[rx] += 1
        return True

def kruskal_mst(nodes: list, edges: list[tuple]) -> list[tuple]:
    # edges = [(cost, u, v), ...]
    uf     = UnionFind(nodes)
    result = []
    for cost, u, v in sorted(edges):
        if uf.union(u, v):
            result.append((cost, u, v))
        if len(result) == len(nodes) - 1:
            break
    return result

# Example: 10 cities, 45 possible direct routes
# MST gives the 9 cheapest routes that keep all cities connected
# Total infrastructure cost = sum of MST edge weights
```

**Where it runs:** Telecom fibre route planning, electrical grid design,
airline hub-and-spoke network planning, water pipe network optimisation.

---

## 8. Kubernetes and Microservices — Cycle Detection

**Algorithm:** DFS-based cycle detection in a directed dependency graph

In a microservice architecture, Service A may call B, B may call C. If C calls
back to A, you have a circular dependency — a deadlock waiting to happen.
Kubernetes uses topological sort and cycle detection for pod startup ordering
and for validating Helm chart dependencies.

```python
def detect_cycles(services: dict) -> list[list]:
    # services[s] = [services that s depends on]
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {s: WHITE for s in services}
    cycles_found = []

    def dfs(node, path):
        color[node] = GRAY
        path.append(node)
        for dep in services.get(node, []):
            if color[dep] == GRAY:
                # Found a back edge — extract the cycle
                cycle_start = path.index(dep)
                cycles_found.append(path[cycle_start:] + [dep])
            elif color[dep] == WHITE:
                dfs(dep, path)
        path.pop()
        color[node] = BLACK

    for service in services:
        if color[service] == WHITE:
            dfs(service, [])
    return cycles_found

# Kubernetes admission webhooks run this check before deploying new services.
# Helm uses topological sort to determine chart install order.
```

**Where it runs:** Kubernetes, Helm, Docker Compose, Istio service mesh
dependency analysis, CI/CD pipeline job ordering (GitHub Actions, Jenkins).

---

## 9. Circuit Board Design — DAG Scheduling and Planarity

**Algorithm:** Critical path (longest path in DAG) for scheduling; Kuratowski
planarity test for PCB layer minimisation

On a printed circuit board (PCB), manufacturing steps have dependencies (you
must etch before you can plate). The critical path through the dependency DAG
determines the minimum manufacturing time. Planarity testing determines whether
the circuit can be laid out on a single layer without wire crossings.

```python
def critical_path(dag: dict, durations: dict) -> tuple[int, list]:
    # dag[task] = [tasks that must complete before this task]
    # Returns: (total_time, critical_path_sequence)
    from collections import deque

    in_degree = {t: 0 for t in dag}
    successors = {t: [] for t in dag}
    for task, deps in dag.items():
        for dep in deps:
            successors[dep].append(task)
            in_degree[task] += 1

    earliest  = {t: 0 for t in dag}
    queue     = deque(t for t in dag if in_degree[t] == 0)
    topo_order = []

    while queue:
        t = queue.popleft()
        topo_order.append(t)
        for succ in successors[t]:
            earliest[succ] = max(earliest[succ],
                                  earliest[t] + durations[t])
            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                queue.append(succ)

    end_time = max(earliest[t] + durations[t] for t in dag)

    # Backtrack to find critical path (tasks with zero float)
    path, t = [], max(dag, key=lambda x: earliest[x] + durations[x])
    while t:
        path.append(t)
        predecessors = [d for d in dag[t]]
        t = max(predecessors, key=lambda p: earliest[p] + durations[p],
                default=None) if predecessors else None
    return end_time, path[::-1]

# Critical path method (CPM) is standard in semiconductor manufacturing,
# VLSI design, and FPGA synthesis pipelines.
```

**Where it runs:** EDA (electronic design automation) tools like Cadence and
Synopsys, VLSI synthesis and place-and-route tools, FPGA bitstream compilers,
IC manufacturing execution systems.

---

## Summary Table

```
Domain                   Algorithm               Graph Type
────────────────────────────────────────────────────────────────────
Social networks          BFS, Union-Find         Undirected, sparse
GPS routing              Dijkstra, A*            Weighted directed
Internet routing         Dijkstra (OSPF)         Weighted undirected
Package managers         Topological sort        DAG
Fraud detection          Connected components    Bipartite, dynamic
Search engines           PageRank (power iter.)  Directed (web graph)
Airline/rail networks    Kruskal's MST           Weighted undirected
Kubernetes/microservices Cycle detection (DFS)   Directed
Circuit board design     Critical path (DAG)     DAG
```

### Choosing the right algorithm

```
"Find shortest path between two nodes"      →  Dijkstra / A*
"Find all nodes in the same group"          →  Union-Find / BFS
"Order tasks with dependencies"             →  Topological sort
"Does a cycle exist?"                       →  DFS (color marking)
"Minimum cost to connect everything"        →  Kruskal's / Prim's MST
"Which nodes are most important/central?"   →  PageRank / Betweenness centrality
"Can I do X in parallel with Y?"            →  Critical path (DAG scheduling)
```

Graphs are the universal language of relationships. When you find yourself
thinking "things depend on other things" or "entities are connected", you are
already looking at a graph problem — the question is just which algorithm fits.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Patterns](./patterns.md) &nbsp;|&nbsp; **Next:** [Common Mistakes →](./common_mistakes.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
