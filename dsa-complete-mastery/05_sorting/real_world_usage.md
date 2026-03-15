# Sorting — Real-World Usage

Sorting is one of the most universally applied algorithms in computing. Every time you
open a leaderboard, run a SQL query with ORDER BY, or process a log file, a sorting
algorithm is doing the heavy lifting. Here is where it actually shows up in production.

---

## 1. Database ORDER BY — TimSort in SQLite, External Merge Sort in PostgreSQL

When you write `SELECT * FROM orders ORDER BY created_at DESC`, the database engine
has to sort the result set. SQLite uses a variant of TimSort for in-memory sorts.
PostgreSQL uses external merge sort when the result set exceeds `work_mem` (default 4MB),
spilling sorted runs to disk and merging them back.

In Python, when you fetch rows and sort them yourself — or when an ORM like SQLAlchemy
returns results — you are using Python's built-in `sorted()`, which is also TimSort.

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Order:
    order_id: int
    customer_id: int
    total: float
    status: str
    created_at: datetime


# Simulate rows returned from a DB query (unsorted, as they come off disk)
orders: List[Order] = [
    Order(1, 42, 150.00, "shipped",   datetime(2024, 3, 5, 10, 0)),
    Order(2, 17, 89.99,  "pending",   datetime(2024, 3, 5,  9, 30)),
    Order(3, 42, 310.00, "delivered", datetime(2024, 3, 4, 15, 0)),
    Order(4,  9, 45.00,  "pending",   datetime(2024, 3, 5, 11, 0)),
    Order(5, 17, 200.00, "shipped",   datetime(2024, 3, 3,  8, 0)),
]

# Equivalent of: ORDER BY customer_id ASC, created_at DESC
sorted_orders = sorted(
    orders,
    key=lambda o: (o.customer_id, -o.created_at.timestamp())
)

for o in sorted_orders:
    print(f"customer={o.customer_id}  order={o.order_id}  "
          f"date={o.created_at.date()}  total=${o.total:.2f}")
```

Output shows orders grouped by customer, newest first within each group — exactly
what a paginated "my orders" screen needs.

**Why it matters:** Multi-key sorts like this let the application layer mirror what
the database does, useful when you need to sort in-memory after joining data from
multiple microservices that cannot share a single SQL query.

---

## 2. Python's TimSort — Why It's Fast on Nearly-Sorted Data

TimSort (Tim Peters, 2002) is a hybrid of merge sort and insertion sort. Its key
insight: real-world data is rarely random. Log files, timestamps, version numbers,
sensor readings — they arrive mostly in order with occasional out-of-order entries.

TimSort detects existing "runs" (already-sorted sequences) and merges them. On
nearly-sorted input it approaches O(n). On random input it falls back to O(n log n).

```python
import time
import random

# Simulate a production scenario: application logs that are 98% in timestamp order.
# A small percentage arrive slightly out of order due to distributed system clock skew.

def generate_activity_log(n: int, noise_fraction: float = 0.02) -> list:
    """
    Generate n log entries mostly sorted by timestamp.
    noise_fraction controls how many entries are swapped out of order.
    """
    base = list(range(n))  # perfectly sorted timestamps
    num_swaps = int(n * noise_fraction)
    for _ in range(num_swaps):
        i, j = random.randint(0, n - 1), random.randint(0, n - 1)
        base[i], base[j] = base[j], base[i]
    return base


def benchmark(data: list, label: str) -> None:
    copy = data.copy()
    start = time.perf_counter()
    copy.sort()
    elapsed = time.perf_counter() - start
    print(f"{label}: {elapsed * 1000:.2f} ms for {len(data):,} items")


n = 500_000
nearly_sorted = generate_activity_log(n, noise_fraction=0.02)
fully_random   = random.sample(range(n), n)

benchmark(nearly_sorted, "Nearly sorted (2% noise)")
benchmark(fully_random,  "Fully random             ")
```

You will observe the nearly-sorted case is noticeably faster. In practice, sorting
10 million application log lines from a fleet of servers (where each server's logs
are already sorted, but the merged stream has interleaving) is where TimSort shines.

**Custom key functions** let you sort complex objects without writing a comparator:

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass
class LogEntry:
    timestamp: datetime
    level: str      # DEBUG, INFO, WARNING, ERROR
    service: str
    message: str


LEVEL_PRIORITY = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}

logs = [
    LogEntry(datetime(2024, 3, 5, 10, 1, 5), "ERROR",   "auth-service",  "token expired"),
    LogEntry(datetime(2024, 3, 5, 10, 1, 0), "INFO",    "api-gateway",   "request received"),
    LogEntry(datetime(2024, 3, 5, 10, 1, 5), "WARNING", "db-service",    "slow query"),
    LogEntry(datetime(2024, 3, 5, 10, 0, 58),"DEBUG",   "cache-service", "cache miss"),
]

# Sort by timestamp, then by severity (ERROR first when timestamps tie)
sorted_logs = sorted(
    logs,
    key=lambda e: (e.timestamp, -LEVEL_PRIORITY[e.level])
)

for entry in sorted_logs:
    print(f"[{entry.timestamp.strftime('%H:%M:%S')}] [{entry.level:7}] "
          f"{entry.service}: {entry.message}")
```

---

## 3. Leaderboard and Ranking Systems

Every gaming platform, competitive programming site (LeetCode, Codeforces), and
e-commerce "best seller" list uses multi-key sorting. The primary key is score;
secondary key is timestamp (earlier submission wins on tie); tertiary key might be
username for deterministic ordering.

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Player:
    username: str
    score: int
    finished_at: datetime   # lower is better when score ties
    penalty_minutes: int    # used in ACM-style contests


def build_leaderboard(players: List[Player]) -> List[Player]:
    """
    Rank by:
      1. Score descending
      2. Penalty minutes ascending (less penalty = better)
      3. Finish time ascending (earlier = better)
      4. Username ascending (alphabetical tiebreaker for display stability)
    """
    return sorted(
        players,
        key=lambda p: (
            -p.score,
            p.penalty_minutes,
            p.finished_at.timestamp(),
            p.username,
        )
    )


players = [
    Player("alice",   2800, datetime(2024, 3, 5, 14, 32), 45),
    Player("bob",     2800, datetime(2024, 3, 5, 14, 28), 45),  # same score+penalty, earlier
    Player("charlie", 3100, datetime(2024, 3, 5, 13, 59), 30),
    Player("diana",   2800, datetime(2024, 3, 5, 14, 28), 50),  # same time as bob, more penalty
    Player("eve",     3100, datetime(2024, 3, 5, 14, 10), 25),  # same score as charlie, less penalty
]

leaderboard = build_leaderboard(players)
print(f"{'Rank':<6} {'Username':<10} {'Score':<8} {'Penalty':<10} {'Finished'}")
print("-" * 55)
for rank, p in enumerate(leaderboard, start=1):
    print(f"{rank:<6} {p.username:<10} {p.score:<8} {p.penalty_minutes:<10} "
          f"{p.finished_at.strftime('%H:%M')}")
```

This is essentially what LeetCode's weekly contest ranking does, and what chess
rating systems (ELO + tiebreakers) rely on.

---

## 4. Merge Sort for External Sorting — Files Too Large for RAM

Log aggregation systems (Splunk, Elasticsearch ingestion pipelines, AWS CloudTrail)
deal with files far too large to fit in memory. The standard approach is external
merge sort:

1. Read chunks that fit in RAM, sort each chunk, write to a temporary file.
2. Merge all sorted temporary files using a min-heap.

```python
import heapq
import os
import tempfile
from typing import Iterator


def sort_large_log_file(input_path: str, output_path: str, chunk_size: int = 10_000) -> None:
    """
    External merge sort for a log file where each line starts with a timestamp.
    chunk_size: number of lines to hold in memory at once.
    """
    temp_files = []

    # --- Phase 1: Sort chunks and write to temp files ---
    with open(input_path, "r") as f:
        while True:
            chunk = []
            for _ in range(chunk_size):
                line = f.readline()
                if not line:
                    break
                chunk.append(line)
            if not chunk:
                break
            chunk.sort()   # TimSort on a chunk that fits in RAM
            tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".tmp")
            tmp.writelines(chunk)
            tmp.close()
            temp_files.append(tmp.name)

    # --- Phase 2: K-way merge using a min-heap ---
    handles = [open(path, "r") for path in temp_files]

    def file_iterator(fh) -> Iterator[str]:
        for line in fh:
            yield line

    with open(output_path, "w") as out:
        iterators = [file_iterator(fh) for fh in handles]
        for line in heapq.merge(*iterators):
            out.write(line)

    for fh in handles:
        fh.close()
    for path in temp_files:
        os.unlink(path)


# Demo: create a small "large" file and sort it
import random, string

def _create_demo_file(path: str, n_lines: int = 50_000) -> None:
    with open(path, "w") as f:
        for i in range(n_lines):
            ts = random.randint(1_700_000_000, 1_710_000_000)
            msg = "".join(random.choices(string.ascii_lowercase, k=20))
            f.write(f"{ts} {msg}\n")

if __name__ == "__main__":
    with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as tmp_in:
        input_path = tmp_in.name
    output_path = input_path.replace(".log", "_sorted.log")

    _create_demo_file(input_path)
    sort_large_log_file(input_path, output_path, chunk_size=5_000)

    # Verify: first 5 lines should have ascending timestamps
    with open(output_path) as f:
        for _ in range(5):
            print(f.readline().strip())

    os.unlink(input_path)
    os.unlink(output_path)
```

This is the same strategy used by GNU sort, Hadoop MapReduce's shuffle phase, and
Spark's sort-based shuffle.

---

## 5. Sorting Networks in Parallel Computing

A sorting network is a fixed sequence of compare-and-swap operations that can be
executed in parallel. NVIDIA's CUDA uses bitonic sort for GPU-based sorting because
all comparisons at a given "step" are independent and can be executed by thousands
of CUDA cores simultaneously.

Key idea: unlike comparison-based sorts that branch based on data, a sorting network's
structure is determined entirely by the input size — no data-dependent branching.
This is why GPUs can sort 100 million integers in milliseconds.

Libraries like CUB (CUDA Unbound) and Thrust expose GPU sorting to CUDA programmers.
In Python, `cupy.sort()` offloads to a GPU sorting network.

**Practical takeaway:** When you need to sort massive arrays for ML feature pipelines
or financial market data, GPU sorting via CuPy/Thrust can be 50-100x faster than
CPU-based TimSort for random data.

---

## 6. B-Tree and B+ Tree — Why Sorted Order Enables O(log n) Database Queries

When PostgreSQL creates an index on `orders.created_at`, it builds a B+ tree. Each
node holds sorted keys and pointers to children. Because the data is always kept in
sorted order within the tree, a range query like
`WHERE created_at BETWEEN '2024-01-01' AND '2024-03-01'` becomes a single O(log n)
lookup to find the start key, then a linear scan along the leaf nodes.

Without sorted order, that same range query would require a full table scan: O(n).

```python
import bisect
from typing import List, Tuple, Any


class SimpleSortedIndex:
    """
    A simplified in-memory sorted index that mimics what a B-tree does for range queries.
    Uses bisect (binary search on a sorted list) to show the O(log n) principle.
    """

    def __init__(self):
        self._keys: List[Any] = []
        self._row_ids: List[int] = []

    def insert(self, key: Any, row_id: int) -> None:
        pos = bisect.bisect_left(self._keys, key)
        self._keys.insert(pos, key)
        self._row_ids.insert(pos, row_id)

    def range_query(self, low: Any, high: Any) -> List[int]:
        """Return all row_ids where low <= key <= high. O(log n + k)."""
        left  = bisect.bisect_left(self._keys, low)
        right = bisect.bisect_right(self._keys, high)
        return self._row_ids[left:right]


# Build an index on 'created_at' (represented as Unix timestamps)
import random

index = SimpleSortedIndex()
timestamps = sorted(random.randint(1_700_000_000, 1_710_000_000) for _ in range(1_000_000))
for row_id, ts in enumerate(timestamps):
    index.insert(ts, row_id)

# Range query: find all orders in a 24-hour window
window_start = 1_705_000_000
window_end   = window_start + 86_400

results = index.range_query(window_start, window_end)
print(f"Found {len(results):,} rows in range — using O(log n) binary search, "
      f"not a full scan of 1,000,000 rows.")
```

**The core insight:** maintaining sorted order at write time (at the cost of O(log n)
inserts) pays dividends at read time — range queries, ORDER BY without a sort step,
and MIN/MAX in O(log n) instead of O(n). This is the fundamental trade-off that makes
database indexes worth the storage cost.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Common Mistakes →](./common_mistakes.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
