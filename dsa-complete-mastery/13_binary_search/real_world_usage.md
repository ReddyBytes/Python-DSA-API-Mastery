# Binary Search — Real World Usage

Binary search reduces O(n) lookups to O(log n) by exploiting sorted order. That seemingly small
improvement is the difference between a query taking 1 second vs 20 microseconds at scale.
It appears in database engines, distributed systems, time-series stores, and anywhere a
monotonic condition lets you eliminate half the search space per step.

---

## 1. Database Indexes — B-Tree Binary Search

Every WHERE clause on an indexed column in PostgreSQL, MySQL, SQLite, and SQL Server ultimately
executes a binary search on a B-tree (a generalization of binary search trees optimized for
disk pages). When you run `SELECT * FROM users WHERE id = 42` on a table with 10 million rows,
the database does ~23 comparisons instead of 10 million. The `bisect` module in Python gives
you the same power for in-memory sorted data.

```python
import bisect
import time
import random

def simulate_db_index():
    """
    Simulate an in-memory sorted index (like a database B-tree leaf page).
    Demonstrates the real performance gap between indexed and full-table scan.
    """
    # Build a sorted "index" — like a database index on user_id
    index_size = 1_000_000
    sorted_ids = sorted(random.sample(range(1, 10_000_000), index_size))

    targets = random.sample(sorted_ids, 1000)

    # --- Full table scan (no index) ---
    start = time.perf_counter()
    for target in targets:
        _ = target in set(sorted_ids)    # O(1) for set, but build cost is O(n)
    # Simulate pure linear scan
    linear_count = 0
    for target in targets[:10]:          # only 10 to keep it fast
        for val in sorted_ids:
            linear_count += 1
            if val == target:
                break
    linear_time = time.perf_counter() - start

    # --- Binary search (indexed) ---
    start = time.perf_counter()
    for target in targets:
        idx = bisect.bisect_left(sorted_ids, target)
        found = idx < len(sorted_ids) and sorted_ids[idx] == target
    binary_time = time.perf_counter() - start

    print(f"Index size: {index_size:,} rows")
    print(f"Binary search (1000 lookups): {binary_time*1000:.2f} ms")
    print(f"Avg comparisons per lookup:  ~{index_size.bit_length()} (log2)")
    print(f"Linear scan comparisons (10 lookups): {linear_count:,} avg")


def range_query(sorted_events: list[tuple[int, str]], lo: int, hi: int) -> list[str]:
    """
    Simulate a database range scan: WHERE timestamp BETWEEN lo AND hi
    bisect_left/right is exactly how SQLite and PostgreSQL walk B-tree leaf pages.
    """
    left = bisect.bisect_left(sorted_events, (lo,))
    right = bisect.bisect_right(sorted_events, (hi, chr(255)))
    return [name for _, name in sorted_events[left:right]]


simulate_db_index()

events = sorted([
    (1700000100, "login"),
    (1700000200, "purchase"),
    (1700000500, "logout"),
    (1700001000, "login"),
    (1700001200, "cart_add"),
    (1700002000, "checkout"),
])
print(f"\nEvents in window: {range_query(events, 1700000150, 1700001100)}")
# ['purchase', 'logout', 'login']
```

---

## 2. Git Bisect — Find the Bug-Introducing Commit

`git bisect` is one of the most elegant real-world applications of binary search. Given a
range of commits where the first is known-good and the last is known-bad, it binary searches
the commit history to find the exact commit that introduced a regression. Large projects like
the Linux kernel (30,000+ commits per year) rely on this daily. The simulation below shows
the algorithm that `git bisect run` implements internally.

```python
def git_bisect(commits: list[str], test_function) -> str:
    """
    Binary search on commit history to find the first "bad" commit.
    Equivalent to: git bisect start && git bisect bad HEAD && git bisect good v1.0

    test_function(commit) -> True if commit is "bad" (bug is present)

    Used by: Linux kernel developers, Chrome team, every CI system with
             regression detection (GitHub Actions bisect workflows)
    """
    lo, hi = 0, len(commits) - 1
    steps = 0

    print(f"Searching {len(commits)} commits (~{len(commits).bit_length()} steps max)")

    while lo < hi:
        mid = (lo + hi) // 2
        steps += 1
        is_bad = test_function(commits[mid])
        status = "BAD" if is_bad else "GOOD"
        print(f"  Step {steps}: testing {commits[mid][:8]}... -> {status}")

        if is_bad:
            hi = mid         # bug present here, search earlier half
        else:
            lo = mid + 1     # bug not present, search later half

    print(f"First bad commit: {commits[lo]} (found in {steps} steps)")
    return commits[lo]


# Simulate 512 commits: bug introduced at commit 347
import hashlib

def make_commit_hash(i):
    return hashlib.sha1(str(i).encode()).hexdigest()

commits = [make_commit_hash(i) for i in range(512)]
bug_introduced_at = 347

def test_commit(commit_hash):
    # In real git bisect, this runs your test suite
    commit_index = next(i for i, h in enumerate(commits) if h == commit_hash)
    return commit_index >= bug_introduced_at

first_bad = git_bisect(commits, test_commit)
# Found in 9 steps instead of up to 512 linear checks
```

---

## 3. Consistent Hashing — Load Balancing with Binary Search

Consistent hashing is used by memcached, Redis Cluster, Apache Cassandra, DynamoDB, and
virtually every distributed cache. A sorted ring of server positions is maintained; to find
which server handles a given key, binary search the ring for the first server position >= the
key's hash. This is exactly `bisect_right` on the ring array.

```python
import bisect
import hashlib

class ConsistentHashRing:
    """
    Consistent hashing ring — used by Redis Cluster, Cassandra, Memcached.
    Binary search (bisect) is how the ring lookup is O(log n).

    Virtual nodes improve distribution: each physical server occupies
    multiple positions on the ring (used by Cassandra with 256 vnodes).
    """
    def __init__(self, replicas: int = 150):
        self.replicas = replicas     # virtual nodes per server
        self.ring: list[int] = []    # sorted hash positions
        self.nodes: dict[int, str] = {}  # position -> server name

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_server(self, server: str):
        for i in range(self.replicas):
            position = self._hash(f"{server}:{i}")
            self.ring.append(position)
            self.nodes[position] = server
        self.ring.sort()    # maintain sorted order for binary search

    def remove_server(self, server: str):
        for i in range(self.replicas):
            position = self._hash(f"{server}:{i}")
            self.ring.remove(position)
            del self.nodes[position]

    def get_server(self, key: str) -> str:
        if not self.ring:
            raise ValueError("No servers in ring")
        position = self._hash(key)
        # Binary search: find first server position >= key hash
        idx = bisect.bisect_right(self.ring, position) % len(self.ring)
        return self.nodes[self.ring[idx]]

    def distribution(self, keys: list[str]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for key in keys:
            server = self.get_server(key)
            counts[server] = counts.get(server, 0) + 1
        return counts


ring = ConsistentHashRing(replicas=150)
for server in ["cache-01", "cache-02", "cache-03", "cache-04"]:
    ring.add_server(server)

test_keys = [f"user:{i}" for i in range(10000)]
dist = ring.distribution(test_keys)
print("Key distribution across cache servers:")
for server, count in sorted(dist.items()):
    bar = "=" * (count // 50)
    print(f"  {server}: {count:5d} keys {bar}")

# Add a new server — minimal key reassignment
ring.add_server("cache-05")
dist2 = ring.distribution(test_keys)
print(f"\nAfter adding cache-05: {dist2}")
```

---

## 4. Time-Series Log Search — Finding Events in a Range

Datadog, Splunk, Prometheus, and ClickHouse all store time-series events in sorted timestamp
order. Finding all events in a time window is a binary search problem: locate the left boundary
with `bisect_left` and right boundary with `bisect_right`. This is O(log n + k) where k is
the number of results, vs O(n) for a full scan — critical when you have billions of log lines.

```python
import bisect
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LogEvent:
    timestamp: float
    level: str
    service: str
    message: str

    def __lt__(self, other):
        return self.timestamp < other.timestamp


def find_events_in_range(
    events: list[LogEvent],
    start_ts: float,
    end_ts: float,
    level_filter: str | None = None
) -> list[LogEvent]:
    """
    Find all log events in [start_ts, end_ts] using binary search.
    This is how Splunk, Datadog, and Loki implement time range queries
    on their in-memory sorted buffers before hitting disk/columnar stores.

    O(log n + k) vs O(n) linear scan — critical at billions of events.
    """
    # Create sentinel objects for boundary search
    left_sentinel = LogEvent(start_ts, "", "", "")
    right_sentinel = LogEvent(end_ts + 0.001, "", "", "")

    left_idx = bisect.bisect_left(events, left_sentinel)
    right_idx = bisect.bisect_left(events, right_sentinel)

    results = events[left_idx:right_idx]

    if level_filter:
        results = [e for e in results if e.level == level_filter]

    return results


# Simulate production log stream
import random
base_ts = datetime(2024, 1, 15, 9, 0).timestamp()
levels = ["INFO", "WARN", "ERROR", "DEBUG"]
services = ["auth-service", "payment-api", "user-service", "cart-service"]

logs = sorted([
    LogEvent(
        timestamp=base_ts + i * 0.1 + random.uniform(0, 0.05),
        level=random.choice(levels),
        service=random.choice(services),
        message=f"Request processed #{i}"
    )
    for i in range(100_000)
])

# Find all ERROR events in a 30-second window
window_start = base_ts + 3600    # 1 hour in
window_end = window_start + 30   # 30-second window

errors = find_events_in_range(logs, window_start, window_end, level_filter="ERROR")
print(f"Total events: {len(logs):,}")
print(f"Errors in 30s window: {len(errors)}")
print(f"Binary search checked ~{len(logs).bit_length()} positions to find boundaries")
```

---

## 5. Configuration Threshold Search — Binary Search on the Answer

Many capacity planning and optimization problems can be reframed as: "find the minimum value
of X such that condition(X) is true." If the condition is monotonic (once true, always true
for larger values), binary search on the answer works. Netflix uses this for adaptive bitrate
streaming, AWS uses it for auto-scaling triggers, and game servers use it for tick-rate tuning.

```python
def min_servers_for_sla(
    request_rates: list[int],
    max_latency_ms: int,
    capacity_per_server: int
) -> int:
    """
    Find the minimum number of servers to keep latency under SLA.
    Condition: is monotonic — if N servers are enough, N+1 is also enough.

    Used by: AWS Auto Scaling capacity planning, Netflix CDN node sizing,
             Kubernetes HPA (Horizontal Pod Autoscaler) calculations
    """
    def can_handle(num_servers: int) -> bool:
        total_capacity = num_servers * capacity_per_server
        peak_rate = max(request_rates)
        utilization = peak_rate / total_capacity
        # Simplified M/M/1 queue: latency spikes as utilization -> 1
        simulated_latency = 10 / (1 - utilization) if utilization < 1 else float("inf")
        return simulated_latency <= max_latency_ms

    lo, hi = 1, 1000
    while lo < hi:
        mid = (lo + hi) // 2
        if can_handle(mid):
            hi = mid          # mid works, try fewer
        else:
            lo = mid + 1      # mid not enough, need more

    return lo


def find_first_bad_deployment(versions: list[str], error_rate_fn) -> str:
    """
    Binary search on deployment versions — used in canary release pipelines.
    Equivalent to: PagerDuty deployment tracking, Datadog deployment markers.
    """
    lo, hi = 0, len(versions) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if error_rate_fn(versions[mid]) > 0.01:  # > 1% error rate = bad
            hi = mid
        else:
            lo = mid + 1
    return versions[lo]


# Production capacity planning example
hourly_traffic = [8500, 12000, 18000, 25000, 31000,  # morning ramp
                  35000, 38000, 40000, 37000, 34000,  # peak hours
                  28000, 22000, 15000, 10000, 8000]   # evening decline

min_pods = min_servers_for_sla(
    request_rates=hourly_traffic,
    max_latency_ms=200,
    capacity_per_server=5000   # requests/sec per pod
)
print(f"Peak traffic: {max(hourly_traffic):,} req/s")
print(f"Minimum pods for 200ms SLA: {min_pods}")
print(f"Binary search found answer in ~{(1000).bit_length()} steps")
```

---

## 6. Floating-Point Binary Search — Square Root and Newton's Method

Square root computation, floating-point precision thresholds, and convergence criteria all use
binary search under the hood. Python's `math.sqrt` ultimately calls the CPU's `fsqrt` instruction,
but the underlying algorithm is either Newton-Raphson (which converges quadratically) or
a binary search on real numbers. Understanding this matters in numerical computing, financial
pricing engines, and physics simulations.

```python
def sqrt_binary_search(n: float, precision: float = 1e-10) -> float:
    """
    Compute sqrt(n) using binary search on real numbers.
    Demonstrates convergence and precision control.

    The same pattern is used in:
    - Financial options pricing (finding implied volatility)
    - Physics engines (collision detection thresholds)
    - Machine learning (finding optimal learning rate)
    - Signal processing (finding filter cutoff frequencies)
    """
    if n < 0:
        raise ValueError("Cannot compute sqrt of negative number")
    if n == 0:
        return 0.0

    lo = 0.0
    hi = max(1.0, n)    # for n < 1, sqrt(n) > n, so cap at 1

    iterations = 0
    while (hi - lo) > precision:
        mid = (lo + hi) / 2
        if mid * mid < n:
            lo = mid
        else:
            hi = mid
        iterations += 1

    result = (lo + hi) / 2
    print(f"sqrt({n}) = {result:.10f} (converged in {iterations} iterations)")
    return result


def find_implied_volatility(
    option_price: float,
    pricing_fn,
    min_vol: float = 0.001,
    max_vol: float = 10.0,
    precision: float = 1e-6
) -> float:
    """
    Find implied volatility using binary search — Black-Scholes inversion.
    Used by: Bloomberg Terminal, every options trading desk, QuantLib.
    pricing_fn(vol) -> theoretical option price
    """
    lo, hi = min_vol, max_vol
    while (hi - lo) > precision:
        mid = (lo + hi) / 2
        if pricing_fn(mid) < option_price:
            lo = mid    # price too low, need higher vol
        else:
            hi = mid    # price too high, need lower vol
    return (lo + hi) / 2


import math
for n in [2, 9, 0.25, 1234567]:
    result = sqrt_binary_search(n)
    assert abs(result - math.sqrt(n)) < 1e-8, "Precision check failed"

# Implied volatility example (simplified Black-Scholes call price)
def simplified_call_price(vol):
    S, K, T, r = 100, 105, 0.5, 0.05
    d1 = (math.log(S/K) + (r + vol**2/2)*T) / (vol * math.sqrt(T))
    d2 = d1 - vol * math.sqrt(T)
    from statistics import NormalDist
    nd = NormalDist()
    return S * nd.cdf(d1) - K * math.exp(-r*T) * nd.cdf(d2)

market_price = 5.50
impl_vol = find_implied_volatility(market_price, simplified_call_price)
print(f"\nMarket option price: ${market_price}")
print(f"Implied volatility: {impl_vol:.4f} ({impl_vol*100:.2f}%)")
```

---

## Key Takeaways

| Use Case | Binary Search Variant | Complexity | System |
|---|---|---|---|
| DB index lookup | `bisect_left` on sorted array | O(log n) | PostgreSQL, SQLite B-tree |
| Git bisect | Binary search on commit array | O(log n) | Git, CI regression detection |
| Consistent hashing | `bisect_right` on sorted ring | O(log n) | Redis Cluster, Cassandra |
| Time-series range | `bisect_left` + `bisect_right` | O(log n + k) | Datadog, Splunk, Prometheus |
| Capacity planning | Binary search on the answer | O(log n * f(n)) | AWS Auto Scaling, K8s HPA |
| Floating-point search | Real-number bisection | O(log(1/ε)) | Bloomberg, options pricing |

The key insight: **binary search works on any monotonic condition**, not just sorted arrays.
If you can express your problem as "find the smallest X where condition(X) is true" and the
condition is monotonically non-decreasing, binary search applies. This "binary search on the
answer" pattern solves a vast range of optimization problems in O(log n) time.
