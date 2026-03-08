# Heaps — Real-World Usage

A heap is a complete binary tree stored in an array where every parent is smaller
(min-heap) or larger (max-heap) than its children. The critical guarantee: the
minimum (or maximum) element is always at index 0, accessible in O(1), and can be
removed in O(log n). Python's `heapq` module is always a min-heap.

This simple guarantee shows up in an astonishing range of production systems.

---

## 1. OS Process Scheduler — CPU Task Scheduling

Every operating system scheduler maintains a priority queue of runnable processes.
Linux's Completely Fair Scheduler uses a red-black tree (BST with balance guarantees),
but conceptually it is a min-heap on "virtual runtime". Real-time operating systems
like FreeRTOS and Zephyr use explicit min-heaps for task scheduling.

**Real company example:** AWS Lambda's internal scheduler, Kubernetes's kube-scheduler,
and Celery (used by Instagram, Mozilla) all maintain priority queues of pending work.

```python
import heapq
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass(order=True)
class Task:
    priority:   int          # lower number = higher priority (like Linux nice values)
    arrival:    float = field(compare=False)
    name:       str   = field(compare=False)
    cpu_burst:  int   = field(compare=False)  # milliseconds of CPU needed
    preempted:  bool  = field(compare=False, default=False)


class PriorityTaskScheduler:
    """
    Non-preemptive priority scheduler backed by a min-heap.
    Mirrors the design of POSIX SCHED_RR and Celery's priority queue.

    Time complexity:
      add_task:  O(log n)
      run_next:  O(log n)
      preempt:   O(log n)
    """

    def __init__(self):
        self._heap: list[Task] = []
        self._clock: float = 0.0
        self._completed: list[Task] = []

    def add_task(self, name: str, priority: int, cpu_burst: int) -> None:
        task = Task(
            priority=priority,
            arrival=self._clock,
            name=name,
            cpu_burst=cpu_burst,
        )
        heapq.heappush(self._heap, task)
        print(f"  [t={self._clock:.0f}ms] QUEUED   '{name}' priority={priority}")

    def run_next(self) -> Optional[Task]:
        """
        Dequeue the highest-priority (lowest number) task and run it.
        This is exactly what the OS does on every context switch.
        """
        if not self._heap:
            print("  No tasks in queue.")
            return None
        task = heapq.heappop(self._heap)
        print(f"  [t={self._clock:.0f}ms] RUNNING  '{task.name}' "
              f"priority={task.priority} burst={task.cpu_burst}ms")
        self._clock += task.cpu_burst
        self._completed.append(task)
        return task

    def preempt(self, new_name: str, new_priority: int, cpu_burst: int) -> None:
        """
        A higher-priority task arrives mid-execution — push it to the front.
        The heap re-heapifies in O(log n).
        """
        print(f"  [t={self._clock:.0f}ms] PREEMPT  new high-priority task '{new_name}'")
        self.add_task(new_name, new_priority, cpu_burst)

    def queue_size(self) -> int:
        return len(self._heap)

    def stats(self) -> None:
        print(f"\nCompleted {len(self._completed)} tasks. "
              f"Remaining in queue: {self.queue_size()}")


if __name__ == "__main__":
    scheduler = PriorityTaskScheduler()

    # Batch jobs arrive
    scheduler.add_task("batch-report",    priority=10, cpu_burst=500)
    scheduler.add_task("user-request",    priority=2,  cpu_burst=50)
    scheduler.add_task("health-check",    priority=5,  cpu_burst=10)
    scheduler.add_task("email-send",      priority=7,  cpu_burst=100)

    print()
    scheduler.run_next()   # user-request runs first (priority 2)
    scheduler.run_next()   # health-check (priority 5)

    # Emergency task arrives mid-run
    scheduler.preempt("db-backup-urgent", new_priority=1, cpu_burst=200)
    scheduler.run_next()   # db-backup-urgent jumps the queue

    while scheduler.queue_size():
        scheduler.run_next()

    scheduler.stats()
```

---

## 2. Dijkstra's Algorithm — The Priority Queue IS the Heap

Dijkstra's shortest-path algorithm is the most important graph algorithm in
production. Without a heap it runs in O(V^2); with a min-heap it runs in
O((V + E) log V). Every navigation app, network router, and logistics optimizer
uses this algorithm.

**Real company example:** Google Maps, Uber routing, FedEx/UPS route optimization,
and BGP (the routing protocol that runs the internet) all use Dijkstra or its
variants.

```python
import heapq
from collections import defaultdict


def dijkstra(graph: dict[str, list[tuple[str, int]]], source: str) -> dict[str, int]:
    """
    Standard Dijkstra with a min-heap.

    graph: adjacency list — graph[u] = [(v, weight), ...]
    Returns: dist[v] = shortest distance from source to v

    The heap stores (distance, node) pairs.
    Every time we pop, we process the globally closest unvisited node.
    This greedy choice is safe because edge weights are non-negative.

    Time: O((V + E) log V)
    """
    dist: dict[str, int | float] = defaultdict(lambda: float("inf"))
    dist[source] = 0
    heap = [(0, source)]   # (cost, node)
    visited: set[str] = set()

    while heap:
        cost, u = heapq.heappop(heap)

        if u in visited:
            continue            # stale entry — skip
        visited.add(u)

        for v, weight in graph.get(u, []):
            new_cost = cost + weight
            if new_cost < dist[v]:
                dist[v] = new_cost
                heapq.heappush(heap, (new_cost, v))   # O(log V)

    return dict(dist)


def reconstruct_path(
    graph: dict[str, list[tuple[str, int]]],
    source: str,
    target: str,
) -> tuple[list[str], int]:
    """Returns (path, total_distance) from source to target."""
    dist: dict[str, int | float] = defaultdict(lambda: float("inf"))
    prev: dict[str, str | None] = {}
    dist[source] = 0
    heap = [(0, source)]
    visited: set[str] = set()

    while heap:
        cost, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        if u == target:
            break
        for v, weight in graph.get(u, []):
            new_cost = cost + weight
            if new_cost < dist[v]:
                dist[v] = new_cost
                prev[v] = u
                heapq.heappush(heap, (new_cost, v))

    path, node = [], target
    while node in prev:
        path.append(node)
        node = prev[node]
    path.append(source)
    return list(reversed(path)), dist[target]


if __name__ == "__main__":
    # Road network: (neighbour, distance_km)
    road_network = {
        "A": [("B", 4), ("C", 2)],
        "B": [("C", 1), ("D", 5)],
        "C": [("B", 1), ("D", 8), ("E", 10)],
        "D": [("E", 2)],
        "E": [],
    }
    distances = dijkstra(road_network, "A")
    print("Shortest distances from A:", distances)

    path, dist = reconstruct_path(road_network, "A", "E")
    print(f"\nShortest path A → E: {' → '.join(path)}  ({dist} km)")
```

---

## 3. Merge K Sorted Files — Log Merging in LSM-Trees

LevelDB (Chrome's IndexedDB), RocksDB (used by Facebook, LinkedIn, Uber), and Apache
Cassandra all use **Log-Structured Merge Trees** (LSM-trees). When compacting, they
must merge K sorted files (called SSTables) into one sorted output. The classic
algorithm uses a min-heap.

**Real company example:** Every write to Facebook's social graph, every Cassandra write
at Apple or Netflix goes through LSM compaction backed by a K-way merge heap.

```python
import heapq
from typing import Iterator


def merge_k_sorted_lists(lists: list[list[int]]) -> list[int]:
    """
    Merge K sorted lists into one sorted list.
    This is exactly how RocksDB's SSTable compaction works.

    Algorithm:
      1. Push the first element of each list onto the heap with its list index.
      2. Pop the minimum — this is the next output element.
      3. Push the next element from the same list.
      4. Repeat until heap is empty.

    Time:  O(N log K)  where N = total elements, K = number of lists
    Space: O(K)        only K elements in the heap at once
    """
    result = []
    # heap entries: (value, list_index, element_index)
    heap: list[tuple[int, int, int]] = []

    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))

    while heap:
        val, list_idx, elem_idx = heapq.heappop(heap)
        result.append(val)
        next_idx = elem_idx + 1
        if next_idx < len(lists[list_idx]):
            heapq.heappush(heap, (lists[list_idx][next_idx], list_idx, next_idx))

    return result


def merge_k_sorted_iterators(iterators: list[Iterator[int]]) -> Iterator[int]:
    """
    Memory-efficient streaming version using heapq.merge.
    In RocksDB, SSTables are too large to load into memory —
    you stream one block at a time. This is exactly that pattern.
    """
    yield from heapq.merge(*iterators)


if __name__ == "__main__":
    # Simulating 5 sorted SSTable files
    sstables = [
        [1, 10, 20, 35, 50],
        [3, 8,  25, 40, 60],
        [2, 15, 22, 45, 55],
        [7, 12, 30, 48, 70],
        [5, 18, 28, 42, 65],
    ]

    merged = merge_k_sorted_lists(sstables)
    print(f"Merged {len(sstables)} SSTables ({sum(len(s) for s in sstables)} total records):")
    print(merged)

    # Streaming version — processes huge files with O(K) memory
    print("\nStreaming merge (first 10 elements):")
    streams = [iter(s) for s in sstables]
    result = list(merge_k_sorted_iterators(streams))
    print(result[:10])
```

---

## 4. A* Pathfinding — Games and Robotics

A* extends Dijkstra by adding a heuristic function `h(n)` that estimates remaining
distance to the goal. The heap stores nodes ordered by `f(n) = g(n) + h(n)` where
`g(n)` is the actual cost so far. This dramatically reduces the number of nodes
explored compared to Dijkstra.

**Real company example:** Unity's NavMesh (used in thousands of game titles), Boston
Dynamics robot navigation, and Waymo's self-driving car path planner all use A* or
variants (D* Lite, Theta*) backed by min-heaps.

```python
import heapq
import math
from typing import Optional


GRID_BLOCKED = 1
GRID_FREE    = 0


def astar(
    grid: list[list[int]],
    start: tuple[int, int],
    goal:  tuple[int, int],
) -> Optional[list[tuple[int, int]]]:
    """
    A* on a 2D grid. 0 = passable, 1 = wall.
    Returns the shortest path or None if unreachable.

    The heap stores (f_score, g_score, position).
    Heuristic: Euclidean distance (admissible — never overestimates).
    """
    rows, cols = len(grid), len(grid[0])

    def heuristic(a: tuple[int, int], b: tuple[int, int]) -> float:
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def neighbours(pos: tuple[int, int]):
        r, c = pos
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == GRID_FREE:
                cost = 1.414 if dr != 0 and dc != 0 else 1.0  # diagonal costs more
                yield (nr, nc), cost

    g_score: dict[tuple, float] = {start: 0.0}
    came_from: dict[tuple, tuple] = {}
    heap = [(heuristic(start, goal), 0.0, start)]
    visited: set = set()

    while heap:
        f, g, pos = heapq.heappop(heap)
        if pos in visited:
            continue
        visited.add(pos)
        if pos == goal:
            path = []
            while pos in came_from:
                path.append(pos)
                pos = came_from[pos]
            path.append(start)
            return list(reversed(path))
        for nbr, cost in neighbours(pos):
            new_g = g + cost
            if nbr not in g_score or new_g < g_score[nbr]:
                g_score[nbr] = new_g
                came_from[nbr] = pos
                f_score = new_g + heuristic(nbr, goal)
                heapq.heappush(heap, (f_score, new_g, nbr))

    return None  # no path found


def visualise(grid, path):
    display = [row[:] for row in grid]
    for r, c in path:
        display[r][c] = 2
    symbols = {0: ".", 1: "#", 2: "*"}
    for row in display:
        print("  " + " ".join(symbols[cell] for cell in row))


if __name__ == "__main__":
    grid = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 1, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]
    start, goal = (0, 0), (6, 7)
    path = astar(grid, start, goal)

    if path:
        print(f"Path found ({len(path)} steps):")
        visualise(grid, path)
    else:
        print("No path found.")
```

---

## 5. Median Maintenance — Streaming Statistics

In real-time analytics you often need to compute the median of a sliding window of
events — CPU latency, request duration, payment amount — without storing all values.
The classic solution uses **two heaps**: a max-heap for the lower half and a min-heap
for the upper half. The median is always at the tops of the heaps.

**Real company example:** Datadog and Prometheus track p50/p95/p99 latency using
digest structures (DDSketch, t-Digest) which are approximations of this exact idea.
LeetCode's problem 295 "Find Median from Data Stream" is a real Google interview
question asked to SREs.

```python
import heapq


class MedianFinder:
    """
    Maintains the running median in O(log n) per insertion.

    Invariant:
      low  = max-heap of the smaller half (negate values for Python's min-heap)
      high = min-heap of the larger half
      len(low) >= len(high) (low can have at most one extra element)

    Used for: real-time latency percentiles, fraud score monitoring,
              stock price median over a rolling window.
    """

    def __init__(self):
        self._low:  list[int] = []  # max-heap (negated)
        self._high: list[int] = []  # min-heap

    def add_number(self, num: int | float) -> None:
        # Always push to low first
        heapq.heappush(self._low, -num)

        # Balance: low's max must be <= high's min
        if self._high and (-self._low[0]) > self._high[0]:
            heapq.heappush(self._high, -heapq.heappop(self._low))

        # Balance sizes: low can have at most 1 extra
        if len(self._low) > len(self._high) + 1:
            heapq.heappush(self._high, -heapq.heappop(self._low))
        elif len(self._high) > len(self._low):
            heapq.heappush(self._low, -heapq.heappop(self._high))

    def get_median(self) -> float:
        if len(self._low) > len(self._high):
            return float(-self._low[0])
        return (-self._low[0] + self._high[0]) / 2.0

    def get_p75(self) -> float:
        """
        Approximate 75th percentile: the minimum of the upper half.
        For exact percentiles, use the full array or a streaming digest.
        """
        if self._high:
            return float(self._high[0])
        return self.get_median()


def simulate_latency_stream() -> None:
    """
    Simulates monitoring API response latencies in real-time.
    After every 5 events, print the running median — like Datadog does.
    """
    import random
    random.seed(42)

    finder = MedianFinder()
    latencies = [random.randint(10, 500) for _ in range(20)]
    # Inject a few spikes
    latencies[7]  = 2000
    latencies[15] = 1800

    print("Streaming latency monitor (milliseconds):\n")
    for i, lat in enumerate(latencies, 1):
        finder.add_number(lat)
        status = " *** SPIKE ***" if lat > 1000 else ""
        if i % 5 == 0:
            print(f"  After {i:2d} events: median={finder.get_median():.1f}ms "
                  f"approx_p75={finder.get_p75():.1f}ms{status}")
        else:
            print(f"  event {i:2d}: {lat}ms{status}")


if __name__ == "__main__":
    mf = MedianFinder()
    for n in [5, 3, 8, 1, 9, 2, 7]:
        mf.add_number(n)
        print(f"  added {n} → median = {mf.get_median()}")

    print()
    simulate_latency_stream()
```

---

## 6. Top-K Trending Topics — Twitter/Instagram Trending

Finding the top-K most frequent items in a data stream (hashtags, search queries,
products) is one of the most common production analytics problems. A min-heap of
size K is optimal: maintain only K candidates, and whenever a new item could displace
the least popular current candidate, swap it in.

**Real company example:** Twitter's trending topics, Instagram's "Explore" page,
YouTube's trending videos, and Google Trends all use variations of this algorithm.
At scale they use Count-Min Sketch for frequency estimation, but the top-K heap
selection logic is identical.

```python
import heapq
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass(order=True)
class HashtagEntry:
    count:   int
    hashtag: str = field(compare=False)


class TrendingTopics:
    """
    Tracks the top-K hashtags in a live stream.

    Design:
      - count_map:  full frequency table  O(1) update
      - top_k_heap: min-heap of size K    O(log K) update

    The min-heap means the least popular of the top-K is always at index 0,
    making it easy to decide if a new item should enter the top-K.

    Space: O(U + K) where U = unique hashtags seen, K = desired top count.
    """

    def __init__(self, k: int = 10):
        self.k = k
        self._counts: dict[str, int] = defaultdict(int)
        self._heap: list[HashtagEntry] = []   # min-heap on count
        self._in_heap: set[str] = set()

    def process_tweet(self, hashtag: str) -> None:
        self._counts[hashtag] += 1
        count = self._counts[hashtag]

        if hashtag in self._in_heap:
            # Rebuild heap on count change — real systems use a Fibonacci heap
            # or lazy deletion; this simple rebuild is O(K log K)
            self._heap = [
                HashtagEntry(self._counts[e.hashtag], e.hashtag)
                for e in self._heap
            ]
            heapq.heapify(self._heap)
        elif len(self._heap) < self.k:
            heapq.heappush(self._heap, HashtagEntry(count, hashtag))
            self._in_heap.add(hashtag)
        elif count > self._heap[0].count:
            # New item beats the least popular current top-K member — swap
            removed = heapq.heapreplace(
                self._heap, HashtagEntry(count, hashtag)
            )
            self._in_heap.discard(removed.hashtag)
            self._in_heap.add(hashtag)

    def get_trending(self) -> list[tuple[str, int]]:
        """Returns top-K hashtags sorted by frequency, highest first."""
        return sorted(
            [(e.hashtag, e.count) for e in self._heap],
            key=lambda x: -x[1]
        )

    def process_batch(self, hashtags: list[str]) -> None:
        for tag in hashtags:
            self.process_tweet(tag)


if __name__ == "__main__":
    trending = TrendingTopics(k=5)

    # Simulate a tweet stream
    stream = [
        "#python", "#ai", "#python", "#webdev", "#ai",
        "#python", "#crypto", "#ai", "#webdev", "#python",
        "#rust", "#typescript", "#python", "#ai", "#docker",
        "#kubernetes", "#rust", "#ai", "#webdev", "#python",
        "#crypto", "#crypto", "#rust", "#typescript", "#ai",
        "#docker", "#docker", "#python", "#kubernetes", "#ai",
        "#rust", "#rust", "#typescript", "#python", "#webdev",
    ]

    print("Processing tweet stream...\n")
    trending.process_batch(stream)

    print(f"Top-{trending.k} trending hashtags:")
    for rank, (tag, count) in enumerate(trending.get_trending(), 1):
        bar = "#" * count
        print(f"  {rank}. {tag:20s} {count:3d} mentions  {bar}")
```

---

## Summary Table

| Use Case | Heap Type | Key Operation | Real Product |
|---|---|---|---|
| OS scheduler | Min-heap | Pop next task O(log n) | Linux CFS, Celery, k8s scheduler |
| Dijkstra / A* | Min-heap | Expand closest node O(log V) | Google Maps, Waymo, BGP routing |
| K-way merge | Min-heap | Stream merge O(N log K) | RocksDB, Cassandra, LevelDB |
| A* pathfinding | Min-heap | Expand best candidate | Unity NavMesh, Boston Dynamics |
| Median stream | Max+min heap | Insert O(log n) | Datadog, Prometheus p50 |
| Top-K trending | Min-heap of size K | Maintain top-K O(log K) | Twitter trends, Instagram Explore |

The heap's superpower: **O(1) access to the extremum (min or max) with O(log n)
insert/delete**. Whenever a problem says "always process the best/cheapest/closest
item next", reach for a heap.
