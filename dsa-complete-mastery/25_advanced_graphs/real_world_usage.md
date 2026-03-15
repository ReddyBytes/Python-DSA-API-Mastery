# Advanced Graphs — Real World Usage

Advanced graph algorithms are the backbone of navigation, social networks, package managers,
network infrastructure, and logistics. Understanding these algorithms explains why your GPS
reroutes in real-time, why `npm install` resolves dependencies without conflicts, and how
airlines price seats across thousands of routes.

---

## 1. Navigation Systems — Dijkstra and A* in Google Maps

Google Maps processes over 1 billion routing requests per day. The core algorithm is Dijkstra's
with A* heuristics and bidirectional search for speed. Uber and Lyft use it for driver
matching and ETA calculation. Tesla's Autopilot uses A* for local path planning. The key
difference from basic Dijkstra: A* uses a heuristic (geographic distance to destination) to
prioritize nodes closer to the goal, dramatically reducing the search space.

```python
import heapq
from math import sqrt

def dijkstra_with_path(
    graph: dict[str, list[tuple[str, float]]],
    start: str,
    end: str
) -> tuple[float, list[str]]:
    """
    Dijkstra returning both distance and the actual path.
    Used by: Google Maps, Apple Maps, Waze, OSRM (OpenStreetMap routing)

    graph: {node: [(neighbor, weight), ...]}
    Returns: (total_distance, path_nodes)
    """
    heap = [(0.0, start, [start])]
    visited = {}

    while heap:
        dist, node, path = heapq.heappop(heap)
        if node in visited:
            continue
        visited[node] = dist

        if node == end:
            return dist, path

        for neighbor, weight in graph.get(node, []):
            if neighbor not in visited:
                heapq.heappush(heap, (dist + weight, neighbor, path + [neighbor]))

    return float("inf"), []


def astar(
    graph: dict[str, list[tuple[str, float]]],
    coords: dict[str, tuple[float, float]],
    start: str,
    end: str
) -> tuple[float, list[str]]:
    """
    A* search using geographic distance as heuristic.
    A* is ~3-5x faster than Dijkstra for road networks because it
    focuses the search toward the destination.

    Used by: Google Maps (bidirectional A*), Tesla Autopilot local planner,
             game pathfinding (Unity NavMesh, Unreal Engine)
    """
    def heuristic(node):
        x1, y1 = coords[node]
        x2, y2 = coords[end]
        return sqrt((x2 - x1)**2 + (y2 - y1)**2) * 0.9  # admissible: slightly underestimate

    heap = [(heuristic(start), 0.0, start, [start])]
    g_scores = {start: 0.0}

    while heap:
        f, g, node, path = heapq.heappop(heap)
        if node == end:
            return g, path
        if g > g_scores.get(node, float("inf")):
            continue

        for neighbor, weight in graph.get(node, []):
            new_g = g + weight
            if new_g < g_scores.get(neighbor, float("inf")):
                g_scores[neighbor] = new_g
                f_score = new_g + heuristic(neighbor)
                heapq.heappush(heap, (f_score, new_g, neighbor, path + [neighbor]))

    return float("inf"), []


# Manhattan street grid (simplified)
city_graph = {
    "Times_Sq":   [("Grand_Central", 1.2), ("Penn_Station", 0.8), ("Columbus_Circle", 2.1)],
    "Grand_Central": [("Times_Sq", 1.2), ("Union_Sq", 2.0), ("Wall_St", 4.5)],
    "Penn_Station": [("Times_Sq", 0.8), ("Union_Sq", 2.3), ("World_Trade", 3.8)],
    "Columbus_Circle": [("Times_Sq", 2.1), ("Central_Park_N", 1.5)],
    "Union_Sq":   [("Grand_Central", 2.0), ("Penn_Station", 2.3), ("Wall_St", 2.8)],
    "Wall_St":    [("Grand_Central", 4.5), ("Union_Sq", 2.8), ("World_Trade", 0.6)],
    "World_Trade": [("Penn_Station", 3.8), ("Wall_St", 0.6)],
    "Central_Park_N": [("Columbus_Circle", 1.5)],
}
city_coords = {
    "Times_Sq": (40.758, -73.985), "Grand_Central": (40.753, -73.977),
    "Penn_Station": (40.750, -73.993), "Columbus_Circle": (40.768, -73.982),
    "Union_Sq": (40.736, -73.991), "Wall_St": (40.707, -74.009),
    "World_Trade": (40.712, -74.013), "Central_Park_N": (40.800, -73.958),
}

dist, path = dijkstra_with_path(city_graph, "Columbus_Circle", "World_Trade")
print(f"Dijkstra: {' -> '.join(path)} ({dist:.1f} miles)")

dist_a, path_a = astar(city_graph, city_coords, "Columbus_Circle", "World_Trade")
print(f"A*:       {' -> '.join(path_a)} ({dist_a:.1f} miles)")
```

---

## 2. Social Network Analysis — Strongly Connected Components

Facebook's friend recommendation, LinkedIn's "2nd degree connections," and Twitter's "Who to
Follow" all analyze graph connectivity. Strongly Connected Components (SCCs) identify clusters
of mutual influence — people who can all reach each other through directed relationships
(follows, retweets, citations). Academic citation analysis, web crawling (Google's PageRank
preprocessing), and fraud detection all use SCC decomposition.

```python
from collections import defaultdict

def kosaraju_scc(graph: dict[int, list[int]]) -> list[list[int]]:
    """
    Kosaraju's algorithm for Strongly Connected Components.
    Time: O(V + E)

    Used by: Twitter "Who to Follow" cluster analysis,
             academic citation network analysis,
             Google web crawl SCC decomposition (before PageRank),
             compiler call graph optimization (inlining decisions)
    """
    n = max(max(graph.keys()), max(v for vs in graph.values() for v in vs)) + 1
    visited = [False] * n
    finish_order = []

    # Step 1: DFS on original graph, record finish times
    def dfs1(node):
        stack = [(node, iter(graph.get(node, [])))]
        while stack:
            v, neighbors = stack[-1]
            if not visited[v]:
                visited[v] = True
            try:
                w = next(neighbors)
                if not visited[w]:
                    stack.append((w, iter(graph.get(w, []))))
            except StopIteration:
                finish_order.append(v)
                stack.pop()

    for node in graph:
        if not visited[node]:
            dfs1(node)

    # Step 2: Build reversed graph
    rev_graph = defaultdict(list)
    for u, neighbors in graph.items():
        for v in neighbors:
            rev_graph[v].append(u)

    # Step 3: DFS on reversed graph in reverse finish order
    visited2 = [False] * n
    sccs = []

    def dfs2(node):
        component = []
        stack = [node]
        while stack:
            v = stack.pop()
            if visited2[v]:
                continue
            visited2[v] = True
            component.append(v)
            for w in rev_graph.get(v, []):
                if not visited2[w]:
                    stack.append(w)
        return component

    for node in reversed(finish_order):
        if not visited2[node]:
            scc = dfs2(node)
            if scc:
                sccs.append(scc)

    return sccs


# Simulated social network (directed follows)
# Nodes: 0=Alice, 1=Bob, 2=Carol, 3=Dave, 4=Eve, 5=Frank, 6=Grace
follow_graph = {
    0: [1, 2],    # Alice follows Bob, Carol
    1: [0, 3],    # Bob follows Alice, Dave
    2: [0],       # Carol follows Alice
    3: [4],       # Dave follows Eve
    4: [3, 5],    # Eve follows Dave, Frank
    5: [6],       # Frank follows Grace
    6: [5],       # Grace follows Frank
}
names = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace"]

sccs = kosaraju_scc(follow_graph)
print("Influence clusters (SCCs):")
for i, scc in enumerate(sccs):
    members = [names[n] for n in sorted(scc)]
    print(f"  Cluster {i+1}: {members}")
# Cluster 1: [Alice, Bob, Carol] — mutual follows
# Cluster 2: [Dave, Eve] — mutual follows
# Cluster 3: [Frank, Grace] — mutual follows
```

---

## 3. Package Dependency Resolution — Topological Sort

Every package manager — npm (Node.js), pip (Python), apt (Debian/Ubuntu), cargo (Rust), maven
(Java) — uses topological sort to determine installation order. If package A depends on B and
B depends on C, you must install C first, then B, then A. Kahn's algorithm also detects
circular dependencies (which npm treats as errors and pip resolves with special logic).

```python
from collections import defaultdict, deque

def resolve_dependencies(
    packages: dict[str, list[str]]
) -> tuple[list[str] | None, list[str] | None]:
    """
    Topological sort for package installation order using Kahn's algorithm.
    Returns (install_order, cycle) — cycle is None if no circular dependency.

    packages: {package_name: [dependency1, dependency2, ...]}

    Used by: npm, pip, cargo, apt, maven, gradle, bundler (Ruby)
    """
    # Build graph and in-degree count
    in_degree = defaultdict(int)
    dependents = defaultdict(list)   # dependency -> packages that need it

    all_packages = set(packages.keys())
    for pkg, deps in packages.items():
        for dep in deps:
            all_packages.add(dep)
            dependents[dep].append(pkg)
            in_degree[pkg] += 1

    # Initialize queue with packages that have no dependencies
    queue = deque([p for p in all_packages if in_degree[p] == 0])
    install_order = []

    while queue:
        pkg = queue.popleft()
        install_order.append(pkg)

        for dependent in dependents[pkg]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    if len(install_order) != len(all_packages):
        # Cycle detected — find it
        cycle_nodes = [p for p in all_packages if in_degree[p] > 0]
        return None, cycle_nodes

    return install_order, None


# Simulated npm package.json dependency tree
node_packages = {
    "my-app":           ["react", "react-dom", "axios", "lodash"],
    "react-dom":        ["react"],
    "react":            ["loose-envify", "object-assign"],
    "axios":            ["follow-redirects", "form-data"],
    "form-data":        ["asynckit", "mime-types"],
    "mime-types":       ["mime-db"],
    "follow-redirects": [],
    "asynckit":         [],
    "mime-db":          [],
    "loose-envify":     ["js-tokens"],
    "object-assign":    [],
    "lodash":           [],
    "js-tokens":        [],
}

order, cycle = resolve_dependencies(node_packages)
if order:
    print("Install order:")
    for i, pkg in enumerate(order, 1):
        print(f"  {i:2d}. {pkg}")
else:
    print(f"Circular dependency detected: {cycle}")

# Test cycle detection
cyclic_packages = {
    "A": ["B"],
    "B": ["C"],
    "C": ["A"],   # circular!
}
order2, cycle2 = resolve_dependencies(cyclic_packages)
print(f"\nCyclic packages detected: {cycle2}")
```

---

## 4. Network Flow — Max Flow for Capacity Planning

Ford-Fulkerson and Edmonds-Karp (BFS-based) max flow algorithms solve capacity planning
in telecommunications (how much data can flow from datacenter A to B through intermediate
hops), airline seat assignment, bipartite matching (job assignments, ad matching), and
hospital-patient matching. Google's data center network planning uses max-flow to determine
optimal traffic routing between regions.

```python
from collections import defaultdict, deque

def edmonds_karp(
    graph: dict[str, dict[str, int]],
    source: str,
    sink: str
) -> tuple[int, dict]:
    """
    Edmonds-Karp (BFS-based Ford-Fulkerson) for maximum network flow.
    Time: O(V * E^2)

    Used by: Google datacenter traffic engineering, airline seat allocation,
             ad impression matching (Google/Meta), bipartite job assignment
    """
    # Build residual graph as capacity remaining
    residual = defaultdict(lambda: defaultdict(int))
    for u, neighbors in graph.items():
        for v, cap in neighbors.items():
            residual[u][v] += cap

    def bfs_find_path():
        """Find augmenting path using BFS (key to Edmonds-Karp)."""
        visited = {source}
        parent = {source: None}
        queue = deque([source])
        while queue:
            node = queue.popleft()
            if node == sink:
                # Reconstruct path
                path = []
                cur = sink
                while cur is not None:
                    path.append(cur)
                    cur = parent[cur]
                return list(reversed(path))
            for neighbor, cap in residual[node].items():
                if cap > 0 and neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = node
                    queue.append(neighbor)
        return None  # no augmenting path

    max_flow = 0
    flow_paths = []

    while True:
        path = bfs_find_path()
        if not path:
            break

        # Find bottleneck capacity along this path
        path_flow = min(residual[path[i]][path[i+1]] for i in range(len(path)-1))

        # Update residual capacities
        for i in range(len(path) - 1):
            residual[path[i]][path[i+1]] -= path_flow
            residual[path[i+1]][path[i]] += path_flow  # reverse edge

        max_flow += path_flow
        flow_paths.append((path, path_flow))

    return max_flow, flow_paths


# Datacenter interconnect bandwidth (Gbps)
dc_network = {
    "us-east-source": {"us-east-1": 100, "us-east-2": 80},
    "us-east-1":      {"us-central": 60, "eu-west-1": 40},
    "us-east-2":      {"us-central": 70, "us-east-1": 20},
    "us-central":     {"us-west-1": 90, "eu-central": 50},
    "eu-west-1":      {"eu-central": 60, "us-west-sink": 30},
    "eu-central":     {"us-west-sink": 80},
    "us-west-1":      {"us-west-sink": 100},
    "us-west-sink":   {},
}

flow, paths = edmonds_karp(dc_network, "us-east-source", "us-west-sink")
print(f"Maximum bandwidth: {flow} Gbps")
print("Routing paths used:")
for path, gbps in paths:
    print(f"  {' -> '.join(path)}: {gbps} Gbps")
```

---

## 5. Game Map Generation — Kruskal's MST with Union-Find

Procedural dungeon generation in games like Spelunky, Nethack, and Minecraft uses spanning
trees to guarantee connectivity: every room must be reachable from every other room, with
no cycles (which would create redundant paths). Kruskal's algorithm with Union-Find builds
the minimum spanning tree and extra edges are then optionally added for loops. Unity's
ProBuilder and Unreal Engine's procedural tools use similar approaches.

```python
class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        px, py = self.find(x), self.find(y)
        if px == py:
            return False  # already connected
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True


def kruskal_mst(
    edges: list[tuple[int, int, int]],
    n: int
) -> tuple[int, list[tuple[int, int, int]]]:
    """
    Kruskal's MST using Union-Find.
    edges: list of (weight, node_a, node_b)
    n: total number of nodes

    Used by: Procedural dungeon generation (Spelunky, Nethack),
             network cable layout planning, circuit board routing,
             Minecraft structure generation, cluster analysis (single-linkage)
    """
    sorted_edges = sorted(edges)   # sort by weight
    uf = UnionFind(n)
    mst_edges = []
    total_weight = 0

    for weight, u, v in sorted_edges:
        if uf.union(u, v):    # add edge only if it doesn't create a cycle
            mst_edges.append((u, v, weight))
            total_weight += weight
            if len(mst_edges) == n - 1:
                break   # MST complete: always n-1 edges

    return total_weight, mst_edges


def generate_dungeon(num_rooms: int, seed: int = 42) -> list[tuple[int, int, int]]:
    """Generate a connected dungeon layout using Kruskal's MST."""
    import random
    random.seed(seed)

    # Random room positions
    room_pos = [(random.randint(0, 100), random.randint(0, 100))
                for _ in range(num_rooms)]

    # All possible corridors (complete graph)
    from math import sqrt
    all_corridors = []
    for i in range(num_rooms):
        for j in range(i + 1, num_rooms):
            x1, y1 = room_pos[i]
            x2, y2 = room_pos[j]
            dist = int(sqrt((x2-x1)**2 + (y2-y1)**2))
            all_corridors.append((dist, i, j))

    _, mst = kruskal_mst(all_corridors, num_rooms)

    print(f"Dungeon with {num_rooms} rooms — minimum corridors to connect all:")
    for u, v, dist in mst:
        print(f"  Room {u:2d} ({room_pos[u]}) <-> Room {v:2d} ({room_pos[v]}): {dist} units")
    return mst


generate_dungeon(8)
```

---

## 6. Airline Route Optimization — Floyd-Warshall All-Pairs

Airline pricing systems need the shortest path (lowest cost, or fewest hops) between every
pair of airports simultaneously. American Airlines' Sabre, United's Apollo, and Delta's
booking systems use all-pairs shortest path for fare calculation, codeshare routing, and
interline itinerary building. Floyd-Warshall computes all O(n²) distances in O(n³) time
and is used when n is manageable (hundreds of hubs, not all 40,000+ airports at once).

```python
def floyd_warshall(
    graph: dict[str, dict[str, float]]
) -> tuple[dict, dict]:
    """
    All-pairs shortest paths using Floyd-Warshall.
    Time: O(n^3), Space: O(n^2)

    Returns: (distance_matrix, next_hop_matrix) for path reconstruction

    Used by: Airline GDS systems (Sabre, Amadeus, Travelport),
             telecommunications routing tables,
             road network analysis (offline preprocessing),
             social network "degrees of separation" computation
    """
    nodes = list(graph.keys())
    n = len(nodes)
    idx = {node: i for i, node in enumerate(nodes)}

    INF = float("inf")
    dist = [[INF] * n for _ in range(n)]
    nxt = [[None] * n for _ in range(n)]

    # Initialize with direct edges
    for i in range(n):
        dist[i][i] = 0
    for u, neighbors in graph.items():
        for v, w in neighbors.items():
            i, j = idx[u], idx[v]
            dist[i][j] = w
            nxt[i][j] = v

    # Relax through every intermediate node k
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    nxt[i][j] = nxt[i][k]    # path goes through k first

    def get_path(src, dst):
        if nxt[idx[src]][idx[dst]] is None:
            return []
        path = [src]
        while path[-1] != dst:
            path.append(nxt[idx[path[-1]]][idx[dst]])
        return path

    # Return user-friendly result
    result = {}
    for u in nodes:
        result[u] = {}
        for v in nodes:
            result[u][v] = {
                "distance": dist[idx[u]][idx[v]],
                "path": get_path(u, v)
            }

    return result


# Major hub airports with direct route costs (arbitrary fare units)
airline_network = {
    "JFK": {"LAX": 350, "ORD": 180, "LHR": 650, "CDG": 700},
    "LAX": {"JFK": 350, "NRT": 800, "SYD": 950, "ORD": 280},
    "ORD": {"JFK": 180, "LAX": 280, "FRA": 750},
    "LHR": {"JFK": 650, "CDG": 120, "FRA": 180, "DXB": 500},
    "CDG": {"JFK": 700, "LHR": 120, "FRA": 150, "DXB": 480},
    "FRA": {"ORD": 750, "LHR": 180, "CDG": 150, "NRT": 900, "DXB": 400},
    "DXB": {"LHR": 500, "CDG": 480, "FRA": 400, "NRT": 700, "SYD": 850},
    "NRT": {"LAX": 800, "FRA": 900, "DXB": 700, "SYD": 400},
    "SYD": {"LAX": 950, "DXB": 850, "NRT": 400},
}

routes = floyd_warshall(airline_network)

# Find cheapest itineraries
queries = [
    ("JFK", "NRT"),
    ("ORD", "SYD"),
    ("JFK", "DXB"),
]
print("Optimal airline itineraries:")
for src, dst in queries:
    info = routes[src][dst]
    print(f"  {src} -> {dst}: cost={info['distance']}, route={' -> '.join(info['path'])}")
```

---

## Key Takeaways

| Algorithm | Problem Type | Complexity | Used In |
|---|---|---|---|
| Dijkstra / A* | Single-source shortest path | O((V+E) log V) | Google Maps, GPS, game AI |
| Kosaraju SCC | Strongly connected components | O(V + E) | Twitter clusters, PageRank |
| Kahn's topological sort | Dependency ordering + cycle detection | O(V + E) | npm, pip, apt, cargo |
| Edmonds-Karp max flow | Maximum network throughput | O(V * E^2) | Datacenter routing, ad matching |
| Kruskal + Union-Find | Minimum spanning tree | O(E log E) | Dungeon gen, network planning |
| Floyd-Warshall | All-pairs shortest paths | O(V^3) | Airline GDS, router tables |

The unifying theme: **real-world graphs are huge, sparse, and dynamic**. In production,
Dijkstra runs on pre-processed contraction hierarchies (Google Maps), SCCs are computed on
distributed graph engines (Facebook's Giraph), and topological sort happens incrementally as
packages are added. The algorithms here are the foundations — understanding them is how you
reason about, optimize, and debug the systems built on top of them.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Patterns](./patterns.md) &nbsp;|&nbsp; **Next:** [Common Mistakes →](./common_mistakes.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
