# Disjoint Set Union (Union-Find) — Real-World Usage

DSU (also called Union-Find) answers one question efficiently: "are these two
elements in the same connected component?" With path compression and union by
rank, it answers in near O(1) — technically O(α(n)) where α is the inverse
Ackermann function, which is never more than 4 for any realistic input. It
powers network topology management, social graph analysis, infrastructure
planning, image processing, cycle detection, and data deduplication.

---

## 1. Network Connectivity — Are Two Servers in the Same Segment?

### The Production Problem

Data center network engineers and cloud platform teams (AWS, GCP, Azure) must
continuously answer: "are server A and server B in the same network segment?"
This arises when configuring security groups, VPC peering, firewall rules, and
load balancers. As network connections are added (cable installed, VLAN created,
VPC peer established), components merge into the same segment. DSU tracks this
incrementally in near O(1) per operation versus O(n+m) BFS/DFS per query.

```python
# -----------------------------------------------------------------------
# Core DSU implementation with path compression + union by rank
# -----------------------------------------------------------------------

class DSU:
    """
    Disjoint Set Union with path compression and union by rank.
    Near O(1) amortized per operation (O(α(n)) exact).

    Path compression: find() makes all nodes on the path point directly
                      to the root — flattens the tree over time.
    Union by rank:    always attach smaller tree under larger — keeps
                      trees shallow, preventing O(n) chains.
    """

    def __init__(self, n: int):
        self.parent = list(range(n))  # parent[i] = i means i is a root
        self.rank   = [0] * n         # upper bound on tree height
        self.size   = [1] * n         # size of each component
        self.count  = n               # number of distinct components

    def find(self, x: int) -> int:
        """
        Find the root of x's component with path compression.
        Two-pass path compression: first find root, then set all
        nodes on path to point directly to root.
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        """
        Merge x's and y's components.
        Returns True if they were in different components (merge happened).
        Returns False if they were already in the same component.
        """
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False  # already connected

        # Union by rank: attach smaller tree under larger
        if self.rank[root_x] < self.rank[root_y]:
            root_x, root_y = root_y, root_x

        self.parent[root_y] = root_x
        self.size[root_x]  += self.size[root_y]
        if self.rank[root_x] == self.rank[root_y]:
            self.rank[root_x] += 1

        self.count -= 1
        return True

    def connected(self, x: int, y: int) -> bool:
        """Are x and y in the same component?"""
        return self.find(x) == self.find(y)

    def component_size(self, x: int) -> int:
        """Number of elements in x's component."""
        return self.size[self.find(x)]


# -----------------------------------------------------------------------
# Network topology using DSU
# -----------------------------------------------------------------------

class NetworkTopology:
    """
    Models a data center or cloud network as a DSU.
    Nodes are servers/switches. Edges are physical or logical connections.

    Used by:
      - Network configuration management tools (NetBox, Nautobot)
      - SDN controllers (OpenDaylight, ONOS) for reachability queries
      - Cloud platform VPC connectivity validation
      - Kubernetes network policy enforcement

    Operations:
      add_connection(a, b): O(α(n)) — two servers are now directly connected
      are_connected(a, b): O(α(n)) — can these servers reach each other?
      get_components(): O(n)       — enumerate all isolated network segments
    """

    def __init__(self, servers: list[str]):
        self._servers    = servers
        self._index      = {srv: i for i, srv in enumerate(servers)}
        self._dsu        = DSU(len(servers))
        self._connections: list[tuple[str, str]] = []

    def add_connection(self, server_a: str, server_b: str) -> bool:
        """
        Establish a network link between two servers.
        Returns True if this connection bridges two previously isolated segments.
        """
        i = self._index[server_a]
        j = self._index[server_b]
        merged = self._dsu.union(i, j)
        self._connections.append((server_a, server_b))
        return merged

    def are_connected(self, server_a: str, server_b: str) -> bool:
        """Can server_a reach server_b through the network?"""
        return self._dsu.connected(
            self._index[server_a],
            self._index[server_b]
        )

    def get_components(self) -> list[list[str]]:
        """Return all network segments (connected components)."""
        from collections import defaultdict
        groups: dict[int, list[str]] = defaultdict(list)
        for server, idx in self._index.items():
            root = self._dsu.find(idx)
            groups[root].append(server)
        return sorted([sorted(g) for g in groups.values()], key=lambda g: -len(g))

    def segment_count(self) -> int:
        return self._dsu.count

    def segment_size(self, server: str) -> int:
        return self._dsu.component_size(self._index[server])


# -----------------------------------------------------------------------
# Demo: build a data center network topology
# -----------------------------------------------------------------------

servers = [f"server-{i:03d}" for i in range(1, 13)]
topology = NetworkTopology(servers)

print("Building data center network topology...")
print(f"Starting state: {topology.segment_count()} isolated servers\n")

# Connect servers in groups (simulating rack switches + inter-rack connections)
rack_connections = [
    # Rack 1 (servers 001-004)
    ("server-001", "server-002"),
    ("server-002", "server-003"),
    ("server-003", "server-004"),
    # Rack 2 (servers 005-008)
    ("server-005", "server-006"),
    ("server-006", "server-007"),
    ("server-007", "server-008"),
    # Rack 3 (servers 009-012)
    ("server-009", "server-010"),
    ("server-010", "server-011"),
    ("server-011", "server-012"),
]

print(f"{'Connection':<30} {'New Segment?':>12}  {'Segments':>8}")
print("-" * 55)
for a, b in rack_connections:
    merged = topology.add_connection(a, b)
    print(f"  {a} -- {b}  {'YES (merged)':>12}  {topology.segment_count():>8}")

print(f"\nAfter rack wiring: {topology.segment_count()} network segments")
for i, segment in enumerate(topology.get_components(), 1):
    print(f"  Segment {i}: {segment}")

# Connect racks together via spine switches
print(f"\nConnecting racks via spine switches...")
spine_connections = [("server-001", "server-005"), ("server-005", "server-009")]
for a, b in spine_connections:
    topology.add_connection(a, b)

print(f"After spine wiring: {topology.segment_count()} network segment(s)")

# Connectivity queries
print(f"\nConnectivity queries:")
queries = [
    ("server-001", "server-012"),
    ("server-003", "server-008"),
]
for a, b in queries:
    connected = topology.are_connected(a, b)
    print(f"  {a} reachable from {b}: {connected}")
```

---

## 2. Social Network Friend Groups

### The Production Problem

Social networks (Facebook, LinkedIn, WeChat) must answer: "are Alice and Bob in
the same friend circle?" and "how large is this person's connected community?"
As friendships form, the DSU merges components in real time. Facebook uses
this for friend suggestion (friends of friends), community detection, and the
"People You May Know" feature. LinkedIn uses it to compute degree of separation.

```python
from collections import defaultdict

class SocialNetwork:
    """
    Social network friend-group tracker using DSU.
    Supports O(α(n)) friendship addition and group membership queries.

    Used in:
      - Facebook's friend circle detection for privacy controls
      - LinkedIn's "degree of separation" computation
      - WhatsApp group analytics
      - Dating apps for mutual connection detection
    """

    def __init__(self):
        self._user_index: dict[str, int] = {}
        self._users: list[str] = []
        self._dsu: DSU | None  = None

    def _ensure_user(self, user: str) -> int:
        """Register user if new, return their index."""
        if user not in self._user_index:
            idx = len(self._users)
            self._user_index[user] = idx
            self._users.append(user)
            # Rebuild DSU with extended size
            # In production, DSU is pre-allocated for known user count
            old_dsu = self._dsu
            self._dsu = DSU(len(self._users))
            if old_dsu:
                # Restore previous connections by re-processing parents
                for i in range(len(self._users) - 1):
                    if old_dsu.parent[i] != i:
                        self._dsu.union(i, old_dsu.find(i))
        return self._user_index[user]

    def add_friendship(self, user_a: str, user_b: str) -> bool:
        """
        Add a friendship between two users.
        Returns True if they were in different friend circles (circles merged).
        """
        self._ensure_user(user_a)
        self._ensure_user(user_b)
        i = self._user_index[user_a]
        j = self._user_index[user_b]
        return self._dsu.union(i, j)

    def same_group(self, user_a: str, user_b: str) -> bool:
        """Are these two users in the same friend circle?"""
        if user_a not in self._user_index or user_b not in self._user_index:
            return False
        return self._dsu.connected(
            self._user_index[user_a],
            self._user_index[user_b]
        )

    def group_size(self, user: str) -> int:
        """How many people are in this user's friend circle?"""
        if user not in self._user_index:
            return 1
        return self._dsu.component_size(self._user_index[user])

    def group_members(self, user: str) -> list[str]:
        """Return all members of a user's friend circle."""
        if user not in self._user_index:
            return [user]
        user_root = self._dsu.find(self._user_index[user])
        return [
            self._users[i]
            for i in range(len(self._users))
            if self._dsu.find(i) == user_root
        ]

    def group_sizes(self) -> dict[int, int]:
        """Distribution of friend circle sizes."""
        roots = defaultdict(int)
        for i in range(len(self._users)):
            roots[self._dsu.find(i)] += 1
        from collections import Counter
        return dict(Counter(roots.values()))

    def num_communities(self) -> int:
        return self._dsu.count


# -----------------------------------------------------------------------
# Demo: social network friend group evolution
# -----------------------------------------------------------------------

network = SocialNetwork()

# Add friendships
friendships = [
    ("Alice",   "Bob"),
    ("Bob",     "Charlie"),
    ("David",   "Eve"),
    ("Eve",     "Frank"),
    ("Grace",   "Henry"),
    ("Charlie", "David"),    # This bridges two groups!
    ("Ivy",     "Jack"),
    ("Alice",   "Grace"),    # Another bridge!
]

print("Social Network Friend Group Evolution")
print("=" * 55)
print(f"{'Friendship':<25} {'Circles':>7}  {'Same Group?':>11}")
print("-" * 50)

for user_a, user_b in friendships:
    merged = network.add_friendship(user_a, user_b)
    same   = network.same_group(user_a, user_b)
    bridge = " *** CIRCLES MERGED ***" if merged else ""
    print(f"  {user_a} <-> {user_b:<15} {network.num_communities():>7}  {str(same):>11}{bridge}")

print(f"\nFinal state: {network.num_communities()} friend circle(s)")
print(f"\nAlice's group ({network.group_size('Alice')} members): {network.group_members('Alice')}")
print(f"Ivy's group   ({network.group_size('Ivy')} members): {network.group_members('Ivy')}")

print(f"\nGroup size distribution: {network.group_sizes()}")

# Connectivity queries
queries = [
    ("Alice", "Frank"),
    ("Alice", "Jack"),
    ("David", "Henry"),
]
print("\nConnectivity queries:")
for a, b in queries:
    deg = network.same_group(a, b)
    print(f"  {a} and {b} in same circle: {deg}")
```

---

## 3. Kruskal's MST — Minimum Cost Infrastructure Spanning Tree

### The Production Problem

Telecom companies, electrical utilities, and fiber optic network builders must
connect N cities with cables or fiber at minimum total cost. This is the
Minimum Spanning Tree (MST) problem. Kruskal's algorithm, which is the most
common solution in production, relies entirely on DSU: sort all possible
connections by cost, then greedily add the cheapest edge that connects two
currently disconnected components. DSU makes the "are these connected?" and
"connect them" operations near O(1), making the algorithm O(m log m) dominated
by the sort.

```python
from dataclasses import dataclass

@dataclass
class Edge:
    weight: float
    node_a: int
    node_b: int

    def __lt__(self, other):
        return self.weight < other.weight


def kruskal_mst(edges: list[Edge], n: int) -> tuple[list[Edge], float]:
    """
    Kruskal's Minimum Spanning Tree algorithm.

    Algorithm:
    1. Sort all edges by weight (cheapest first).
    2. Initialize DSU with n nodes (all disconnected).
    3. Process edges in order: if edge connects two different components,
       add it to MST and union the components.
    4. Stop after n-1 edges are added (MST is complete).

    The key insight: DSU's union() returns False if both ends are already
    connected (adding the edge would create a cycle), so we skip it.
    This is exactly cycle detection via DSU.

    Time:  O(m log m) — dominated by the sort; DSU ops are near O(1)
    Space: O(n + m)

    Used in:
      - Telecom: laying fiber/cable between cities at minimum cost
      - Power grids: electrical utility planning (NREL, grid operators)
      - Road planning: minimum road network connecting towns
      - Cluster analysis: single-linkage hierarchical clustering
      - Image segmentation: Felzenszwalb-Huttenlocher algorithm
    """
    sorted_edges = sorted(edges)
    dsu = DSU(n)
    mst_edges = []
    total_cost = 0.0

    for edge in sorted_edges:
        if dsu.union(edge.node_a, edge.node_b):
            # These two nodes were in different components — edge is safe to add
            mst_edges.append(edge)
            total_cost += edge.weight

            if len(mst_edges) == n - 1:
                break  # MST complete — exactly n-1 edges needed

    return mst_edges, total_cost


# -----------------------------------------------------------------------
# Demo: fiber optic network for 10 cities
# -----------------------------------------------------------------------

# Cities and their proposed fiber connections with costs (in $millions)
cities = ["NYC", "Boston", "Philadelphia", "Washington DC", "Atlanta",
          "Miami", "Chicago", "Detroit", "Minneapolis", "Dallas"]

city_index = {city: i for i, city in enumerate(cities)}

proposed_connections = [
    (0.8,  "NYC",           "Boston"),
    (1.2,  "NYC",           "Philadelphia"),
    (2.4,  "NYC",           "Chicago"),
    (0.9,  "Philadelphia",  "Washington DC"),
    (1.5,  "Washington DC", "Atlanta"),
    (1.8,  "Atlanta",       "Miami"),
    (1.1,  "Chicago",       "Detroit"),
    (1.4,  "Chicago",       "Minneapolis"),
    (2.1,  "Chicago",       "Dallas"),
    (0.7,  "Boston",        "Philadelphia"),
    (3.2,  "Miami",         "Dallas"),
    (2.5,  "Atlanta",       "Dallas"),
    (1.6,  "Detroit",       "NYC"),
    (1.3,  "Minneapolis",   "Detroit"),
    (1.9,  "Dallas",        "Washington DC"),
]

edges = [
    Edge(cost, city_index[a], city_index[b])
    for cost, a, b in proposed_connections
]

mst, total_cost = kruskal_mst(edges, len(cities))

print("Fiber Optic Network — Minimum Spanning Tree")
print(f"Cities: {len(cities)}  |  Candidate connections: {len(edges)}")
print(f"\nMST edges (cheapest network connecting all cities):")
print(f"{'Connection':<35} {'Cost':>8}")
print("-" * 45)

# Reverse index for display
idx_to_city = {v: k for k, v in city_index.items()}
total_all    = sum(e.weight for e in edges)

for edge in sorted(mst, key=lambda e: e.weight):
    a = idx_to_city[edge.node_a]
    b = idx_to_city[edge.node_b]
    print(f"  {a} -- {b:<25} ${edge.weight:.1f}M")

print(f"\n  MST total cost   : ${total_cost:.1f}M")
print(f"  All edges total  : ${total_all:.1f}M")
print(f"  Savings          : ${total_all - total_cost:.1f}M ({100*(total_all-total_cost)/total_all:.0f}% reduction)")
print(f"  Edges in MST     : {len(mst)} (= n-1 = {len(cities)-1})")
```

---

## 4. Image Segmentation — Count Islands Using DSU

### The Production Problem

Computer vision systems (autonomous vehicles, medical imaging, satellite
analysis) segment images by grouping connected pixels of the same color or
intensity. The classic "count islands" problem (LeetCode #200) is the
simplified version. DSU solves it without recursion (no stack overflow risk on
large images) and supports incremental union as pixels are processed — making
it suitable for streaming image data.

```python
def count_islands(grid: list[list[int]]) -> int:
    """
    Count connected islands (regions of 1s) in a binary grid using DSU.
    Alternative to BFS/DFS — avoids recursion depth limits for large grids.

    Used in:
      - Satellite imagery analysis (count distinct land masses)
      - Medical imaging (count distinct tissue regions in MRI)
      - Autonomous vehicles (identify separate obstacle regions in LIDAR)
      - PCB design (identify connected copper traces)

    Time:  O(m * n * α(m*n)) ≈ O(m * n)
    Space: O(m * n)
    """
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])

    # Flatten 2D grid to 1D DSU
    # Cell (r, c) maps to index r * cols + c
    dsu = DSU(rows * cols)
    island_count = 0

    def cell_id(r: int, c: int) -> int:
        return r * cols + c

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                island_count += 1  # assume this cell is a new island

                # Try to union with left neighbor
                if c > 0 and grid[r][c - 1] == 1:
                    if dsu.union(cell_id(r, c), cell_id(r, c - 1)):
                        island_count -= 1  # merged — one fewer island

                # Try to union with top neighbor
                if r > 0 and grid[r - 1][c] == 1:
                    if dsu.union(cell_id(r, c), cell_id(r - 1, c)):
                        island_count -= 1  # merged

    return island_count


def label_connected_components(
    grid: list[list[int]]
) -> tuple[list[list[int]], int]:
    """
    Label each cell with its component ID.
    Returns (labeled_grid, num_components).
    Used for pixel segmentation — each unique label is a distinct region.
    """
    if not grid or not grid[0]:
        return [], 0

    rows, cols = len(grid), len(grid[0])
    dsu = DSU(rows * cols)

    def cell_id(r: int, c: int) -> int:
        return r * cols + c

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                if c > 0 and grid[r][c - 1] == 1:
                    dsu.union(cell_id(r, c), cell_id(r, c - 1))
                if r > 0 and grid[r - 1][c] == 1:
                    dsu.union(cell_id(r, c), cell_id(r - 1, c))

    # Build label map: root -> sequential label
    label_map: dict[int, int] = {}
    labeled = [[0] * cols for _ in range(rows)]
    next_label = 1

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                root = dsu.find(cell_id(r, c))
                if root not in label_map:
                    label_map[root] = next_label
                    next_label += 1
                labeled[r][c] = label_map[root]

    return labeled, next_label - 1


# -----------------------------------------------------------------------
# Demo
# -----------------------------------------------------------------------

grids = [
    {
        "name": "Simple islands",
        "grid": [
            [1, 1, 0, 0, 0],
            [1, 1, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 1, 1],
        ]
    },
    {
        "name": "Complex coastline",
        "grid": [
            [1, 0, 0, 1, 1],
            [1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1],
            [0, 1, 0, 0, 1],
            [0, 1, 1, 0, 0],
        ]
    },
]

for example in grids:
    grid = example["grid"]
    n_islands = count_islands(grid)
    labeled, n_components = label_connected_components(grid)

    print(f"\n{example['name']} — {n_islands} island(s)")
    print("  Grid:")
    for row in grid:
        print("    " + " ".join("█" if c else "·" for c in row))
    print("  Labeled components:")
    for row in labeled:
        print("    " + " ".join(str(c) if c else "·" for c in row))

# Performance test on large grid
import random, time
random.seed(42)
large_grid = [[random.choice([0, 0, 1]) for _ in range(1000)] for _ in range(1000)]

start = time.perf_counter()
count = count_islands(large_grid)
elapsed_ms = (time.perf_counter() - start) * 1000

print(f"\nLarge grid (1000×1000 = 1,000,000 cells):")
print(f"  Islands found : {count:,}")
print(f"  Time          : {elapsed_ms:.1f} ms  (O(n*m) — no recursion)")
```

---

## 5. Detecting Cycles in Undirected Graphs

### The Production Problem

Build systems (Bazel, Gradle, Makefile), dependency resolvers (pip, npm, Cargo),
and topology planning tools must detect circular dependencies. A circular
dependency in a build graph means the build will deadlock. In infrastructure
planning, a cycle in an undirected dependency graph indicates a conflicting
requirement. DSU detects this in O(m * α(n)) — the moment you try to union two
nodes that are already connected, you have found a cycle.

```python
def has_cycle(edges: list[tuple[int, int]], n: int) -> tuple[bool, tuple[int, int] | None]:
    """
    Detect a cycle in an undirected graph using DSU.

    Algorithm: process edges one by one.
    For edge (u, v): if u and v are already in the same component, adding
    this edge creates a cycle. If they're in different components, union them.

    Returns (has_cycle: bool, cycle_edge: optional tuple)

    Time:  O(m * α(n)) ≈ O(m)
    Space: O(n)

    Used in:
      - Build systems: detect circular build dependencies (Bazel, Gradle)
      - Package managers: detect circular package dependencies
      - Database replication: detect replication cycle in topology
      - Electrical networks: detect unintended loops in power grids
    """
    dsu = DSU(n)
    for u, v in edges:
        if not dsu.union(u, v):  # union returns False if already connected
            return True, (u, v)  # this edge closes a cycle
    return False, None


def find_all_cycles_in_dependency_graph(
    packages: list[str],
    dependencies: list[tuple[str, str]]
) -> list[tuple[str, str]]:
    """
    Find all edges that would create a cycle in a package dependency graph.
    In a real package manager, these edges represent circular dependencies.
    Returns list of (package_a, package_b) pairs that create cycles.
    """
    index = {pkg: i for i, pkg in enumerate(packages)}
    dsu = DSU(len(packages))
    cycle_edges = []

    for pkg_a, pkg_b in dependencies:
        i, j = index[pkg_a], index[pkg_b]
        if not dsu.union(i, j):
            cycle_edges.append((pkg_a, pkg_b))

    return cycle_edges


# -----------------------------------------------------------------------
# Demo 1: simple graph cycle detection
# -----------------------------------------------------------------------

print("Cycle detection in undirected graphs:")

test_cases = [
    {
        "name": "No cycle (valid build graph)",
        "n": 5,
        "edges": [(0,1), (1,2), (2,3), (3,4)],
    },
    {
        "name": "Has cycle (deadlock risk)",
        "n": 4,
        "edges": [(0,1), (1,2), (2,3), (3,1)],
    },
    {
        "name": "Triangle",
        "n": 3,
        "edges": [(0,1), (1,2), (2,0)],
    },
    {
        "name": "Forest — multiple trees, no cycle",
        "n": 6,
        "edges": [(0,1), (2,3), (4,5)],
    },
]

for case in test_cases:
    cycle_found, cycle_edge = has_cycle(case["edges"], case["n"])
    status = f"CYCLE at edge {cycle_edge}" if cycle_found else "SAFE (no cycle)"
    print(f"  {case['name']:<40} -> {status}")

# -----------------------------------------------------------------------
# Demo 2: package dependency circular detection
# -----------------------------------------------------------------------

print("\nPackage manager circular dependency detection:")

packages = ["flask", "werkzeug", "jinja2", "markupsafe", "click",
            "itsdangerous", "blinker", "requests", "certifi"]

# Valid dependencies (flask depends on werkzeug, etc.)
valid_deps = [
    ("flask",     "werkzeug"),
    ("flask",     "jinja2"),
    ("flask",     "click"),
    ("flask",     "itsdangerous"),
    ("jinja2",    "markupsafe"),
    ("requests",  "certifi"),
    ("blinker",   "flask"),
]

# Add a circular dependency
bad_deps = valid_deps + [
    ("werkzeug", "flask"),   # flask -> werkzeug AND werkzeug -> flask = CYCLE
    ("certifi",  "requests"),# requests -> certifi AND certifi -> requests = CYCLE
]

cycles = find_all_cycles_in_dependency_graph(packages, bad_deps)
print(f"  Dependencies checked: {len(bad_deps)}")
print(f"  Circular dependencies found: {len(cycles)}")
for a, b in cycles:
    print(f"    CIRCULAR: {a} <-> {b}")
```

---

## 6. Accounts Merge — Grouping Emails by Person

### The Production Problem

Email service providers (Gmail, Outlook) and identity platforms (Okta, Auth0)
must merge user accounts when they detect that two accounts share an email
address — indicating the same person. Given a list of accounts (each with a
name and multiple email addresses), group all accounts belonging to the same
person. DSU unites accounts through shared emails: if accounts A and B both
have "alice@gmail.com", they belong to the same person.

```python
from collections import defaultdict

def merge_accounts(accounts: list[list[str]]) -> list[list[str]]:
    """
    Merge accounts that share at least one email address.
    Input: list of accounts, each as [name, email1, email2, ...]
    Output: merged list of accounts, each as [name, email1, email2, ...]
            with emails sorted alphabetically.

    Algorithm:
    1. Assign each account an index (0 to n-1).
    2. For each email, record the first account that claimed it.
    3. If a second account claims the same email, union those accounts.
    4. After processing all accounts, group by DSU root.
    5. For each group, collect all emails, sort, and prepend the name.

    Time:  O(n * k * α(n)) where k = avg emails per account
    Space: O(n * k)

    This is essentially LeetCode #721, used in production at:
      - Google Accounts: merging duplicate accounts in Google's identity system
      - Salesforce: deduplicating customer records with shared contact info
      - CRM systems: customer 360 view across multiple touchpoints
    """
    n = len(accounts)
    dsu = DSU(n)
    email_to_account: dict[str, int] = {}

    for i, account in enumerate(accounts):
        name = account[0]
        for email in account[1:]:
            if email in email_to_account:
                # This email was already seen in another account — same person!
                dsu.union(i, email_to_account[email])
            else:
                email_to_account[email] = i

    # Group account indices by their DSU root
    root_to_emails: dict[int, set[str]] = defaultdict(set)
    for i, account in enumerate(accounts):
        root = dsu.find(i)
        for email in account[1:]:
            root_to_emails[root].add(email)

    # Reconstruct merged accounts
    result = []
    for root, emails in root_to_emails.items():
        name = accounts[root][0]
        result.append([name] + sorted(emails))

    return sorted(result, key=lambda a: (a[0], a[1]))


# -----------------------------------------------------------------------
# Demo: real-world account deduplication
# -----------------------------------------------------------------------

accounts = [
    # Alice has two accounts, linked by shared email
    ["Alice",   "alice@gmail.com",   "alice@work.com"],
    ["Alice",   "alice@work.com",    "alice@school.edu"],

    # Bob has three accounts across different registrations
    ["Bob",     "bob123@yahoo.com"],
    ["Bob",     "bob@company.com",   "bob123@yahoo.com"],
    ["Bob",     "bob.smith@gmail.com","bob@company.com"],

    # Carol has one standalone account
    ["Carol",   "carol@example.com"],

    # David — two accounts with no overlap (stays separate)
    ["David",   "david.a@gmail.com"],
    ["David",   "david.b@outlook.com"],
]

print("Accounts Merge — Identity Resolution")
print(f"Input: {len(accounts)} accounts\n")
print("Input accounts:")
for i, account in enumerate(accounts):
    name, *emails = account
    print(f"  {i}: {name}: {emails}")

merged = merge_accounts(accounts)

print(f"\nOutput: {len(merged)} merged accounts")
print("Merged accounts:")
for account in merged:
    name, *emails = account
    print(f"  {name}: {emails}")

# -----------------------------------------------------------------------
# Scale demo: merge 10,000 accounts
# -----------------------------------------------------------------------

import random
import time

random.seed(42)

def generate_accounts(n: int, shared_email_rate: float = 0.3) -> list[list[str]]:
    """Generate accounts where some accounts share emails (same person, different registrations)."""
    all_emails = [f"user{i}@example.com" for i in range(int(n * 0.7))]
    accs = []
    for j in range(n):
        name = f"User_{j % 500}"  # 500 unique names, some duplicated
        n_emails = random.randint(1, 3)
        emails = random.sample(all_emails, min(n_emails, len(all_emails)))
        accs.append([name] + emails)
    return accs

large_accounts = generate_accounts(10_000)

start = time.perf_counter()
large_merged  = merge_accounts(large_accounts)
elapsed_ms    = (time.perf_counter() - start) * 1000

print(f"\nScale test: {len(large_accounts):,} accounts -> {len(large_merged):,} merged accounts")
print(f"Processing time: {elapsed_ms:.1f} ms")
print(f"Deduplication ratio: {(1 - len(large_merged)/len(large_accounts)) * 100:.1f}% reduction")
```

---

## Summary Table

| Use Case | Union Trigger | Find Query | Key Insight |
|---|---|---|---|
| Network connectivity | Cable/link added | Same segment? | Incremental O(α(n)) per link |
| Social network | Friendship formed | Same circle? | Merge communities as they grow |
| Kruskal's MST | Cheapest non-cycle edge | Different components? | Skip edges forming cycles |
| Image segmentation | Adjacent same-color pixels | Same region? | No recursion — safe for huge images |
| Cycle detection | Every edge processed | Already connected? | union() returning False IS the cycle |
| Accounts merge | Shared email found | Same person? | Email as bridge between account nodes |

The core invariant of DSU: **with path compression and union by rank, the
amortized cost of m operations on n elements is O(m * α(n)), where α(n) ≤ 4
for any n that can exist in the physical universe.** This is as close to O(1)
as any data structure ever gets.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Patterns](./patterns.md) &nbsp;|&nbsp; **Next:** [Common Mistakes →](./common_mistakes.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
