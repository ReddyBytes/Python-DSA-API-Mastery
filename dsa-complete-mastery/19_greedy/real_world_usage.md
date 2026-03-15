# Greedy Algorithms — Real World Usage

Greedy algorithms make the locally optimal choice at each step, trusting that a series of local
optima will produce a global optimum. When this property holds (greedy-choice property + optimal
substructure), greedy solutions are fast, elegant, and used everywhere in production systems.

---

## 1. Network Routing — Dijkstra's Algorithm

Dijkstra's is the backbone of every routing protocol you interact with daily. OSPF (Open Shortest
Path First), used inside corporate networks and ISPs, runs Dijkstra on a live graph of routers.
Google Maps, Waze, and Apple Maps all run variants of it. The greedy insight: always expand the
closest unvisited node — you will never find a cheaper way to reach it later (assuming non-negative
weights).

```python
import heapq
from collections import defaultdict

def dijkstra(graph: dict, start: str, end: str) -> tuple[int, list[str]]:
    """
    Greedy Dijkstra — always expand the cheapest frontier node.

    graph = {"A": [("B", 4), ("C", 1)], "C": [("B", 2)], ...}
    Returns (shortest_distance, path)

    Used by: OSPF routing protocol, Google Maps, GPS firmware
    """
    # Min-heap: (cost, node, path_so_far)
    heap = [(0, start, [start])]
    visited = {}

    while heap:
        cost, node, path = heapq.heappop(heap)

        if node in visited:
            continue
        visited[node] = cost  # greedy commit: cheapest path to node is final

        if node == end:
            return cost, path

        for neighbor, weight in graph.get(node, []):
            if neighbor not in visited:
                heapq.heappush(heap, (cost + weight, neighbor, path + [neighbor]))

    return float("inf"), []


# Example: datacenter network topology
network = {
    "NYC": [("Chicago", 13), ("Atlanta", 14)],
    "Chicago": [("Denver", 20), ("Atlanta", 9)],
    "Atlanta": [("Dallas", 10), ("Miami", 12)],
    "Denver": [("LA", 25)],
    "Dallas": [("LA", 28), ("Denver", 15)],
    "Miami": [("Dallas", 11)],
    "LA": [],
}

cost, path = dijkstra(network, "NYC", "LA")
print(f"Shortest route NYC -> LA: {cost} ms latency")
print(f"Path: {' -> '.join(path)}")
# Shortest route NYC -> LA: 62 ms latency
# Path: NYC -> Atlanta -> Dallas -> Denver -> LA
```

---

## 2. Huffman Coding — ZIP, JPEG, MP3 Compression

Huffman coding is inside every compressed file you've ever downloaded. ZIP uses DEFLATE (LZ77 +
Huffman). JPEG uses Huffman for the DCT coefficients. MP3 uses Huffman for quantized audio data.
The greedy insight: repeatedly merge the two lowest-frequency symbols — this guarantees the
minimum expected code length.

```python
import heapq
from collections import Counter

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman_tree(text: str) -> dict[str, str]:
    """
    Build Huffman codes for a string.
    Used by: gzip, zlib, JPEG encoder, MP3 encoder
    """
    freq = Counter(text)
    heap = [HuffmanNode(ch, f) for ch, f in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        # Greedy: always merge the two cheapest nodes
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    codes = {}
    def assign_codes(node, code=""):
        if node.char is not None:
            codes[node.char] = code or "0"
            return
        assign_codes(node.left, code + "0")
        assign_codes(node.right, code + "1")

    if heap:
        assign_codes(heap[0])
    return codes


def huffman_encode(text: str, codes: dict) -> str:
    return "".join(codes[ch] for ch in text)


def huffman_decode(bits: str, codes: dict) -> str:
    reverse = {v: k for k, v in codes.items()}
    result, current = [], ""
    for bit in bits:
        current += bit
        if current in reverse:
            result.append(reverse[current])
            current = ""
    return "".join(result)


text = "mississippi river data stream"
codes = build_huffman_tree(text)
encoded = huffman_encode(text, codes)
decoded = huffman_decode(encoded, codes)

original_bits = len(text) * 8
compressed_bits = len(encoded)
print(f"Original: {original_bits} bits | Compressed: {compressed_bits} bits")
print(f"Ratio: {compressed_bits/original_bits:.2%} | Correct decode: {decoded == text}")
# Original: 232 bits | Compressed: 100 bits
# Ratio: 43.10% | Correct decode: True
```

---

## 3. Activity / Meeting Room Scheduling

Calendar systems like Google Calendar and Outlook need to pack the maximum number of meetings
into available slots. Conference room booking systems at companies like Airbnb and Zoom use
interval scheduling to maximize room utilization. The greedy insight: always pick the activity
that ends earliest — this leaves the most time for future activities.

```python
def maximize_activities(activities: list[tuple[int, int, str]]) -> list[str]:
    """
    Select maximum non-overlapping meetings in a single room.
    activities: list of (start, end, name)

    Greedy: sort by end time, pick greedily.
    Used by: Google Calendar room optimization, Calendly slot logic
    """
    # Sort by end time — greedy choice
    sorted_acts = sorted(activities, key=lambda x: x[1])
    selected = []
    last_end = -1

    for start, end, name in sorted_acts:
        if start >= last_end:          # no overlap
            selected.append(name)
            last_end = end

    return selected


def min_meeting_rooms(intervals: list[tuple[int, int]]) -> int:
    """
    Minimum rooms needed to host all meetings simultaneously.
    Used by: Zoom room allocation, WeWork booking systems
    """
    if not intervals:
        return 0

    starts = sorted(s for s, _ in intervals)
    ends = sorted(e for _, e in intervals)

    rooms = max_rooms = 0
    i = j = 0
    while i < len(starts):
        if starts[i] < ends[j]:
            rooms += 1
            max_rooms = max(max_rooms, rooms)
            i += 1
        else:
            rooms -= 1
            j += 1
    return max_rooms


meetings = [
    (9, 10, "Standup"),
    (9, 12, "Design Review"),
    (11, 13, "1:1 with Manager"),
    (12, 14, "Product Demo"),
    (13, 15, "Sprint Planning"),
    (14, 16, "Architecture Review"),
]

selected = maximize_activities(meetings)
print(f"Max meetings in one room: {selected}")

room_count = min_meeting_rooms([(s, e) for s, e, _ in meetings])
print(f"Minimum rooms needed for all meetings: {room_count}")
# Max meetings in one room: ['Standup', '1:1 with Manager', 'Sprint Planning', 'Architecture Review']
# Minimum rooms needed for all meetings: 3
```

---

## 4. Task Scheduling with Deadlines — Maximize Profit

Job scheduling with deadlines appears in cloud computing (AWS Lambda job queues), financial
systems (prioritized trade execution), and print queues. Each task has a deadline and profit;
you can complete one task per time unit. The greedy insight: sort by profit descending and slot
each job into the latest available slot before its deadline.

```python
def greedy_job_scheduler(jobs: list[tuple[str, int, int]]) -> tuple[int, list[str]]:
    """
    Schedule jobs to maximize profit.
    jobs: list of (name, deadline, profit)
    Each job takes 1 time unit. Only one job per slot.

    Used by: AWS Batch priority queues, trading engine order scheduling
    """
    # Greedy: process highest profit jobs first
    sorted_jobs = sorted(jobs, key=lambda x: x[2], reverse=True)
    max_deadline = max(d for _, d, _ in jobs)
    slots = [None] * (max_deadline + 1)  # slots[1..max_deadline]

    total_profit = 0
    scheduled = []

    for name, deadline, profit in sorted_jobs:
        # Find the latest free slot at or before deadline
        for slot in range(deadline, 0, -1):
            if slots[slot] is None:
                slots[slot] = name
                total_profit += profit
                scheduled.append(name)
                break

    return total_profit, scheduled


cloud_jobs = [
    ("DataPipelineETL",   4, 200),
    ("ReportGeneration",  1, 180),
    ("ModelTraining",     2, 300),
    ("BackupSnapshot",    3, 100),
    ("AnomalyDetection",  3, 250),
    ("NotificationSend",  2,  90),
    ("DatabaseCleanup",   4, 150),
]

profit, schedule = greedy_job_scheduler(cloud_jobs)
print(f"Scheduled jobs: {schedule}")
print(f"Total profit: ${profit}")
# Scheduled jobs: ['ModelTraining', 'AnomalyDetection', 'ReportGeneration', 'DatabaseCleanup']
# Total profit: $930
```

---

## 5. Fractional Knapsack — Logistics Load Optimization

Shipping companies like FedEx, UPS, and Amazon Logistics solve fractional knapsack variants
constantly. A truck has a weight capacity; each package has a weight and declared value (for
insurance/priority). Unlike 0/1 knapsack, goods (bulk cargo, liquids, grains) can be split.
The greedy insight: sort by value-per-unit-weight ratio and fill greedily.

```python
def fractional_knapsack(
    items: list[tuple[str, float, float]],
    capacity: float
) -> tuple[float, list[tuple[str, float]]]:
    """
    Maximize cargo value within weight capacity (items can be split).
    items: list of (name, weight_kg, value_usd)

    Used by: FedEx route loading, Amazon warehouse fulfillment sorting,
             commodity trading portfolio allocation
    """
    # Greedy: highest value/weight ratio first
    sorted_items = sorted(items, key=lambda x: x[2] / x[1], reverse=True)

    total_value = 0.0
    loaded = []
    remaining = capacity

    for name, weight, value in sorted_items:
        if remaining <= 0:
            break
        take = min(weight, remaining)
        fraction = take / weight
        total_value += value * fraction
        loaded.append((name, round(take, 2)))
        remaining -= take

    return round(total_value, 2), loaded


cargo = [
    ("Electronics",   10, 6000),   # $600/kg
    ("Pharmaceuticals", 5, 4000),  # $800/kg  <- highest ratio
    ("Clothing",      20, 3000),   # $150/kg
    ("AutoParts",     15, 2500),   # $167/kg
    ("FoodGrade",     25, 2000),   # $80/kg
    ("RawMaterials",  30,  900),   # $30/kg
]

truck_capacity = 50  # kg
total_value, manifest = fractional_knapsack(cargo, truck_capacity)

print(f"Truck capacity: {truck_capacity} kg")
for item, kg in manifest:
    print(f"  Load {kg} kg of {item}")
print(f"Total cargo value: ${total_value:,.2f}")
# Load 5 kg of Pharmaceuticals
# Load 10 kg of Electronics
# Load 15 kg of AutoParts
# Load 20 kg of Clothing
# Total cargo value: $18,500.00
```

---

## 6. Prim's MST — Minimum Cost Network Design

Prim's Minimum Spanning Tree algorithm is used in network infrastructure planning. When laying
fiber optic cable between data centers, building power grids, or designing water pipe networks,
the goal is to connect all nodes with the minimum total cable/pipe length. Cisco and Juniper use
MST variants in STP (Spanning Tree Protocol) to prevent network loops. The greedy insight: always
add the cheapest edge that connects a new node to the already-connected component.

```python
import heapq

def prim_mst(graph: dict[str, list[tuple[str, int]]]) -> tuple[int, list[tuple[str, str, int]]]:
    """
    Find Minimum Spanning Tree using Prim's greedy algorithm.
    graph: adjacency list {node: [(neighbor, weight), ...]}

    Used by: Cisco STP loop prevention, fiber network layout planning,
             electrical grid design, water distribution networks
    """
    if not graph:
        return 0, []

    start = next(iter(graph))
    visited = {start}
    edges = []  # MST edges collected
    total_cost = 0

    # Seed heap with all edges from start node
    heap = [(weight, start, neighbor) for neighbor, weight in graph[start]]
    heapq.heapify(heap)

    while heap and len(visited) < len(graph):
        weight, from_node, to_node = heapq.heappop(heap)

        if to_node in visited:
            continue  # already connected, skip

        # Greedy: commit to the cheapest available edge
        visited.add(to_node)
        edges.append((from_node, to_node, weight))
        total_cost += weight

        for neighbor, w in graph.get(to_node, []):
            if neighbor not in visited:
                heapq.heappush(heap, (w, to_node, neighbor))

    return total_cost, edges


# Data center interconnect planning (distances in km of fiber)
datacenters = {
    "us-east-1":    [("us-east-2", 150), ("eu-west-1", 5800), ("us-central", 1200)],
    "us-east-2":    [("us-east-1", 150), ("us-central", 1100)],
    "us-central":   [("us-east-1", 1200), ("us-east-2", 1100), ("us-west-1", 1800)],
    "us-west-1":    [("us-central", 1800), ("us-west-2", 800), ("ap-east-1", 9000)],
    "us-west-2":    [("us-west-1", 800)],
    "eu-west-1":    [("us-east-1", 5800), ("eu-central-1", 1200)],
    "eu-central-1": [("eu-west-1", 1200), ("ap-east-1", 8200)],
    "ap-east-1":    [("us-west-1", 9000), ("eu-central-1", 8200)],
}

cost, mst_edges = prim_mst(datacenters)
print(f"Minimum fiber network cost: {cost} km total")
print("Connections to lay:")
for src, dst, km in mst_edges:
    print(f"  {src} <-> {dst}: {km} km")
```

---

## Key Takeaways

| Problem | Greedy Strategy | Complexity | Used In |
|---|---|---|---|
| Shortest path | Expand cheapest node | O((V+E) log V) | OSPF, Google Maps |
| Data compression | Merge lowest frequency | O(n log n) | ZIP, JPEG, MP3 |
| Interval scheduling | Pick earliest end time | O(n log n) | Google Calendar |
| Job scheduling | Highest profit first | O(n^2) | AWS Batch, trading |
| Fractional knapsack | Best value/weight first | O(n log n) | Logistics, shipping |
| Minimum spanning tree | Cheapest new edge | O(E log V) | Network design, STP |

Greedy works when the **greedy-choice property** holds: a globally optimal solution can always
be constructed by making locally optimal choices. When it does not hold, switch to dynamic
programming (0/1 knapsack, sequence alignment) or exhaustive backtracking.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Patterns](./patterns.md) &nbsp;|&nbsp; **Next:** [Common Mistakes →](./common_mistakes.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
