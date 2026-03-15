# Big-O in the Real World — Where Complexity Analysis Saves You

> "Big-O is not an academic exercise. It is the difference between a system that hums along at a million users and one that collapses at 3am while your phone won't stop ringing."

Most tutorials teach Big-O with toy examples — sorting a list of 10 numbers, searching through 5 items. That is fine for learning the notation. But it leaves you with a dangerous gap: you learn the symbols without feeling the weight behind them.

This file is about feeling the weight.

We will walk through six real scenarios — real problems that real engineers have faced, real production systems that buckled under poor complexity choices, and real fixes that saved the day. Each story starts small and scales up until the difference between O(n) and O(log n), or between O(n²) and O(n log n), becomes visceral and obvious.

By the end, you will never again write a nested loop over a large dataset without pausing to think.

---

## Table of Contents

1. Database Query Optimization — The Index Story
2. Algorithm Choice for Production Scale — The 3am Phone Call
3. Memory Complexity in Caching — 10 Gigabytes vs 100 Kilobytes
4. Recursive Algorithms and Stack Overflow — The Tower of Fibonacci
5. String Processing at Scale — Why Google Does Not Scan Every Document
6. Complexity Hidden in Library Calls — The Invisible Tax
7. Complexity Cheat Sheet — Python Data Structures
8. Amortized Analysis — The Dynamic Array's Secret

---

## 1. Database Query Optimization — The Index Story

### The Setup

Imagine you are a backend engineer at a mid-sized company. You have a `users` table with exactly 1,000,000 rows. A product manager comes to you and says, "The user profile page is loading in 8 seconds. Users are complaining. Fix it."

You look at the backend code. It runs a query like this:

```sql
SELECT * FROM users WHERE email = 'alice@example.com';
```

Simple enough. What could possibly be slow?

You run it yourself. It takes 6.3 seconds.

### What Is Actually Happening

Without an index, the database has no choice but to do what is called a **full table scan**. It reads every single row, one by one, checking whether the email column matches. With 1,000,000 rows, it is reading 1,000,000 rows to find one.

This is pure O(n) — linear time with respect to the number of rows.

```
Row 1:   alice123@example.com   → no match
Row 2:   bob@gmail.com          → no match
Row 3:   charlie@yahoo.com      → no match
...
Row 487,293: alice@example.com  → MATCH (but still reads to end for safety)
...
Row 1,000,000: last_user@...    → no match

Total reads: 1,000,000
```

For small tables this is fine. For a million rows, this is death by a thousand cuts — especially if you run this query hundreds of times per second.

### The Fix: A B-Tree Index

When you add a database index on the `email` column, the database builds a **B-tree** — a balanced tree structure that keeps the emails sorted in a way that allows binary-search-style lookups.

```sql
CREATE INDEX idx_users_email ON users(email);
```

Now the same query becomes O(log n) for an equality search.

```
B-Tree Index Lookup for 'alice@example.com'

Level 0 (root):    [m_______] → left half (a-m)
Level 1:           [g_______] → left half (a-g)
Level 2:           [c_______] → right half (c-g)
Level 3:           [e_______] → left half (c-e)
Level 4:           [al______] → found the leaf page

Total comparisons: ~20
(log₂(1,000,000) ≈ 20)
```

For a range query like `WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31'`, the complexity becomes O(log n + k) where k is the number of matching rows. The index gets you to the start of the range in O(log n), then reads k rows sequentially.

### The Numbers

| Rows in Table | Full Scan (O(n)) | B-Tree Lookup (O(log n)) | Speedup   |
|---------------|-------------------|--------------------------|-----------|
| 1,000         | 1,000 reads       | ~10 reads                | ~100x     |
| 10,000        | 10,000 reads      | ~13 reads                | ~770x     |
| 100,000       | 100,000 reads     | ~17 reads                | ~5,900x   |
| 1,000,000     | 1,000,000 reads   | ~20 reads                | ~50,000x  |
| 10,000,000    | 10,000,000 reads  | ~23 reads                | ~435,000x |

That is not a typo. At 10 million rows, you are looking at a 435,000x speedup. The index query takes microseconds while the full scan takes minutes.

### Python Simulation

Let us build a Python simulation to make this concrete. We will simulate both a linear scan and a B-tree-style binary search, and time them.

```python
import time
import bisect
import random
import string


def generate_emails(n):
    """Generate n fake email addresses."""
    emails = []
    for i in range(n):
        username = ''.join(random.choices(string.ascii_lowercase, k=8))
        domain = random.choice(['gmail.com', 'yahoo.com', 'outlook.com'])
        emails.append(f"{username}{i}@{domain}")
    return emails


class LinearScanDB:
    """
    Simulates a database table with no index.
    Every lookup is O(n) — scans every row.
    """
    def __init__(self, emails):
        # Store as a list of (id, email) tuples — unsorted
        self.rows = [(i, email) for i, email in enumerate(emails)]

    def find_by_email(self, target_email):
        """O(n) — scans every row until found."""
        comparisons = 0
        for row_id, email in self.rows:
            comparisons += 1
            if email == target_email:
                return row_id, comparisons
        return None, comparisons


class BTreeIndexDB:
    """
    Simulates a database table with a B-tree index on email.
    Uses sorted list + bisect as a simplified B-tree proxy.
    Equality lookup: O(log n)
    Range lookup: O(log n + k)
    """
    def __init__(self, emails):
        # Build the "index": sorted list of (email, id)
        self.rows = {i: email for i, email in enumerate(emails)}
        self.index = sorted((email, i) for i, email in enumerate(emails))
        self.emails_sorted = [item[0] for item in self.index]

    def find_by_email(self, target_email):
        """O(log n) — binary search through sorted index."""
        pos = bisect.bisect_left(self.emails_sorted, target_email)
        comparisons = int(len(self.emails_sorted).bit_length())  # log2(n) approximation

        if pos < len(self.emails_sorted) and self.emails_sorted[pos] == target_email:
            row_id = self.index[pos][1]
            return row_id, comparisons
        return None, comparisons

    def find_by_email_range(self, start_email, end_email):
        """O(log n + k) — find start, then scan k matching rows."""
        left = bisect.bisect_left(self.emails_sorted, start_email)
        right = bisect.bisect_right(self.emails_sorted, end_email)
        results = [self.index[i][1] for i in range(left, right)]
        log_cost = int(len(self.emails_sorted).bit_length())
        return results, log_cost + (right - left)


def benchmark_database_lookup(n_rows=1_000_000):
    print(f"\n{'='*60}")
    print(f"Database Lookup Benchmark: {n_rows:,} rows")
    print(f"{'='*60}")

    print("Generating data...")
    emails = generate_emails(n_rows)

    # Pick a target that exists in the middle-ish
    target = emails[n_rows // 2]

    print("Building LinearScanDB (no index)...")
    linear_db = LinearScanDB(emails)

    print("Building BTreeIndexDB (with index)...")
    btree_db = BTreeIndexDB(emails)

    # Time linear scan
    start = time.perf_counter()
    result_linear, comps_linear = linear_db.find_by_email(target)
    elapsed_linear = time.perf_counter() - start

    # Time B-tree lookup
    start = time.perf_counter()
    result_btree, comps_btree = btree_db.find_by_email(target)
    elapsed_btree = time.perf_counter() - start

    print(f"\nTarget email: {target}")
    print(f"\nLinear Scan (O(n)):")
    print(f"  Comparisons: {comps_linear:,}")
    print(f"  Time: {elapsed_linear*1000:.2f} ms")

    print(f"\nB-Tree Index (O(log n)):")
    print(f"  Comparisons (approx log2): {comps_btree}")
    print(f"  Time: {elapsed_btree*1000:.4f} ms")

    if elapsed_btree > 0:
        speedup = elapsed_linear / elapsed_btree
        print(f"\nSpeedup: {speedup:.0f}x faster with index")

    print(f"\nComplexity comparison:")
    print(f"  O(n)     = {n_rows:,} operations")
    print(f"  O(log n) = {n_rows.bit_length()} operations")
    print(f"  Ratio    = {n_rows // n_rows.bit_length():,}x fewer operations")


if __name__ == '__main__':
    benchmark_database_lookup(1_000_000)
```

### Sample Output

```
============================================================
Database Lookup Benchmark: 1,000,000 rows
============================================================
Generating data...
Building LinearScanDB (no index)...
Building BTreeIndexDB (with index)...

Target email: xvkplmrd500000@gmail.com

Linear Scan (O(n)):
  Comparisons: 500,001
  Time: 87.43 ms

B-Tree Index (O(log n)):
  Comparisons (approx log2): 20
  Time: 0.08 ms

Speedup: ~1,093x faster with index

Complexity comparison:
  O(n)     = 1,000,000 operations
  O(log n) = 20 operations
  Ratio    = 50,000x fewer operations
```

The takeaway: after adding an index, your 6-second query becomes a 6-millisecond query. The product manager is happy. The users are happy. You get to go home on time.

---

## 2. Algorithm Choice for Production Scale — The 3am Phone Call

### The Story

Picture a startup in its early days. The team is small, moving fast, and the product just launched. They have 100 users. Life is good.

The backend engineer writes a recommendation engine. It needs to sort a list of scores. She is tired and on a deadline, so she writes a quick selection sort. It is O(n²), but hey — 100 users. It runs in microseconds. Nobody notices.

The product gets featured on a popular newsletter. In two weeks, they have 100,000 users.

At 2:58am, the CTO's phone rings. The recommendation engine has been timing out for 40 minutes. Users are seeing blank screens. The on-call engineer is staring at a 99th-percentile response time of 47 seconds for a page that should load in under a second.

The culprit: that selection sort, now running on lists of 100,000 items.

### The Math, Made Tangible

O(n²) versus O(n log n) sounds abstract. Let us make it concrete with actual operation counts:

| Input Size (n) | O(n log n) operations | O(n²) operations | Ratio         |
|----------------|----------------------|-----------------|---------------|
| 100            | ~664                 | 10,000          | 15x           |
| 1,000          | ~9,966               | 1,000,000       | 100x          |
| 10,000         | ~132,877             | 100,000,000     | 753x          |
| 100,000        | ~1,660,964           | 10,000,000,000  | 6,024x        |
| 1,000,000      | ~19,931,569          | 1,000,000,000,000 | 50,171x     |

At 100,000 users: O(n²) runs 10 billion operations. O(n log n) runs 1.6 million. That is a 6,000x difference. If each operation takes 1 nanosecond, O(n log n) finishes in 1.6 milliseconds. O(n²) takes 10 seconds.

### Live Benchmark

```python
import time
import random


def selection_sort(arr):
    """
    O(n²) sorting algorithm.
    Fine for small arrays. A disaster at scale.
    """
    arr = arr.copy()
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


def merge_sort(arr):
    """
    O(n log n) sorting algorithm.
    Scales gracefully.
    """
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)


def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def run_timing_table():
    sizes = [100, 1_000, 10_000, 100_000]

    print(f"\n{'Input Size':>12} | {'Selection Sort O(n²)':>22} | {'Merge Sort O(n log n)':>22} | {'Speedup':>10}")
    print("-" * 80)

    for n in sizes:
        data = [random.random() for _ in range(n)]

        # Time selection sort (skip for very large n to avoid freezing)
        if n <= 10_000:
            start = time.perf_counter()
            selection_sort(data)
            t_selection = time.perf_counter() - start
            selection_str = f"{t_selection*1000:.2f} ms"
        else:
            # Extrapolate from n=10,000 (not accurate, illustrative)
            selection_str = "~estimated 10,000+ ms"
            t_selection = None

        # Time merge sort
        start = time.perf_counter()
        merge_sort(data)
        t_merge = time.perf_counter() - start
        merge_str = f"{t_merge*1000:.2f} ms"

        if t_selection is not None:
            speedup = f"{t_selection / t_merge:.0f}x"
        else:
            speedup = "~6000x+"

        print(f"{n:>12,} | {selection_str:>22} | {merge_str:>22} | {speedup:>10}")


def simulate_3am_incident():
    """
    Simulate what happens to the recommendation engine
    as user count scales from 100 to 100,000.
    """
    print("\n" + "="*60)
    print("SIMULATING THE STARTUP STORY")
    print("="*60)

    scenarios = [
        (100,    "Launch day — 100 users"),
        (1_000,  "2 weeks later — 1,000 users"),
        (10_000, "Featured in newsletter — 10,000 users"),
    ]

    for n, label in scenarios:
        data = [random.random() for _ in range(n)]

        start = time.perf_counter()
        if n <= 10_000:
            selection_sort(data)
        t_bad = time.perf_counter() - start

        start = time.perf_counter()
        merge_sort(data)
        t_good = time.perf_counter() - start

        print(f"\n{label}")
        print(f"  O(n²)     sort: {t_bad*1000:.3f} ms")
        print(f"  O(n logn) sort: {t_good*1000:.3f} ms")

        if t_bad < 1:
            print(f"  Status: Fine! Nobody notices the difference.")
        elif t_bad < 100:
            print(f"  Status: Slow but tolerable. A few users complain.")
        else:
            print(f"  Status: CRITICAL. Users are timing out. Phone is ringing.")


if __name__ == '__main__':
    run_timing_table()
    simulate_3am_incident()
```

### The Lesson

The engineer did not make a mistake because she was incompetent. She made a trade-off — speed of development over computational efficiency — that was perfectly correct at n=100 but catastrophically wrong at n=100,000.

This is the real lesson of complexity analysis in production: **the algorithm that works fine for your current scale may be a ticking time bomb for your next scale.** When you write O(n²) code, you are not just writing slow code — you are writing code that gets exponentially slower as your product succeeds.

The fix is simple: use Python's built-in `sorted()` (which uses Timsort, O(n log n)) or think carefully about algorithm choice from the start. The fix takes 30 seconds. The incident takes 4 hours.

---

## 3. Memory Complexity in Caching — 10 Gigabytes vs 100 Kilobytes

### The Story

An API team builds a caching layer to speed up expensive database queries. Their first instinct: cache everything. Every user profile query that comes in gets stored in a Python dictionary. The next time that user is looked up, you hit the cache instead of the database.

On day one, this works beautifully. Response times drop from 200ms to 2ms.

On day 30, the server runs out of RAM and crashes.

What happened? The cache had been growing the whole time. Each user profile is about 100 bytes. They have 100 million registered users. If even 10% of them get looked up...

```
10,000,000 users × 100 bytes = 1,000,000,000 bytes = 1 GB
100,000,000 users × 100 bytes = 10,000,000,000 bytes = 10 GB
```

A naive "cache everything" approach has **O(n) space complexity** where n is the number of distinct users ever queried. In a system with millions of users, this means unbounded memory growth.

### The LRU Cache Solution

The insight: you do not need to cache every user ever queried. You only need to cache the users who are likely to be queried again soon — the recently active users.

This is the **Least Recently Used (LRU) cache**: a fixed-size cache that evicts the least recently used entry when full.

**Space complexity: O(k)** where k is the cache size you choose. If k = 1,000, the cache uses at most 1,000 × 100 bytes = 100 KB, no matter how many total users exist.

```
Cache size k = 1,000:
Memory usage = 1,000 × 100 bytes = 100 KB

vs.

Naive cache for 100M users:
Memory usage = 100,000,000 × 100 bytes = 10 GB
```

That is a 100,000x reduction in memory usage.

### How LRU Works

The LRU cache is built from two data structures working together:

1. A **hash map** (Python dict) for O(1) key → value lookups
2. A **doubly linked list** for O(1) move-to-front and evict-from-back

```
LRU Cache (capacity = 4)

After accessing: A, B, C, D

Most Recent                           Least Recent
[HEAD] <-> [D] <-> [C] <-> [B] <-> [A] <-> [TAIL]

Now access E (cache is full):
  1. E is not in cache (miss)
  2. Evict least recent: A
  3. Add E to front

[HEAD] <-> [E] <-> [D] <-> [C] <-> [B] <-> [TAIL]

Now access C (cache hit):
  1. C is in cache
  2. Move C to front (most recent)

[HEAD] <-> [C] <-> [E] <-> [D] <-> [B] <-> [TAIL]
```

Every operation — get, put, evict — is O(1).

### Full LRU Implementation with Space Analysis

```python
from collections import OrderedDict
import sys
import time


class LRUCache:
    """
    LRU Cache with O(1) get and O(1) put.
    Space complexity: O(k) where k is capacity.

    Uses Python's OrderedDict which maintains insertion/access order
    and supports O(1) move-to-end and popitem(last=False).
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key):
        """O(1) — lookup and mark as recently used."""
        if key not in self.cache:
            self.misses += 1
            return None
        # Move to end = mark as most recently used
        self.cache.move_to_end(key)
        self.hits += 1
        return self.cache[key]

    def put(self, key, value):
        """O(1) — insert, evict LRU if over capacity."""
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value

        if len(self.cache) > self.capacity:
            # popitem(last=False) removes the FIRST item (least recently used)
            evicted_key, _ = self.cache.popitem(last=False)

    def memory_usage_bytes(self, value_size_bytes=100):
        """Estimate memory usage of the cache."""
        return len(self.cache) * (value_size_bytes + 50)  # +50 for key/overhead

    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0

    def __len__(self):
        return len(self.cache)

    def __repr__(self):
        keys = list(self.cache.keys())
        return f"LRU[{keys[-3:]} ... (most recent) | size={len(self.cache)}/{self.capacity}]"


class NaiveCache:
    """
    Naive 'cache everything' approach.
    Space complexity: O(n) — grows without bound.
    """

    def __init__(self):
        self.cache = {}
        self.hits = 0
        self.misses = 0

    def get(self, key):
        if key not in self.cache:
            self.misses += 1
            return None
        self.hits += 1
        return self.cache[key]

    def put(self, key, value):
        self.cache[key] = value

    def memory_usage_bytes(self, value_size_bytes=100):
        return len(self.cache) * (value_size_bytes + 50)

    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0


def simulate_user_access_pattern(total_users=10_000, active_users=500, n_requests=50_000):
    """
    Simulate a realistic access pattern:
    - 80% of requests come from a 'hot' set of active users (locality of reference)
    - 20% come from random users across the full user base
    """
    import random

    # The hot set: recently active users
    hot_users = list(range(active_users))
    all_users = list(range(total_users))

    requests = []
    for _ in range(n_requests):
        if random.random() < 0.80:
            requests.append(random.choice(hot_users))
        else:
            requests.append(random.choice(all_users))

    return requests


def fake_db_lookup(user_id):
    """Simulates an expensive database call (just returns fake data)."""
    return {
        'id': user_id,
        'name': f'User_{user_id}',
        'email': f'user{user_id}@example.com',
        'preferences': {'theme': 'dark', 'notifications': True}
    }


def benchmark_caches():
    print("\n" + "="*60)
    print("CACHE MEMORY & PERFORMANCE BENCHMARK")
    print("="*60)

    total_users = 100_000
    active_users = 1_000
    n_requests = 50_000
    lru_size = 1_000
    value_bytes = 100  # bytes per user profile

    print(f"\nSetup:")
    print(f"  Total registered users: {total_users:,}")
    print(f"  Active users (hot set): {active_users:,}")
    print(f"  Requests to simulate:   {n_requests:,}")
    print(f"  LRU cache size:         {lru_size:,}")
    print(f"  Profile size:           {value_bytes} bytes each")

    requests = simulate_user_access_pattern(total_users, active_users, n_requests)

    lru = LRUCache(capacity=lru_size)
    naive = NaiveCache()

    # Simulate serving requests
    for user_id in requests:
        # Try cache first
        val_lru = lru.get(user_id)
        if val_lru is None:
            # Cache miss: go to DB, store in cache
            user_data = fake_db_lookup(user_id)
            lru.put(user_id, user_data)

        val_naive = naive.get(user_id)
        if val_naive is None:
            user_data = fake_db_lookup(user_id)
            naive.put(user_id, user_data)

    print(f"\nResults after {n_requests:,} requests:")
    print(f"\n  LRU Cache (O(k) space, k={lru_size}):")
    print(f"    Cache size:   {len(lru):,} entries")
    print(f"    Memory used:  ~{lru.memory_usage_bytes(value_bytes) / 1024:.1f} KB")
    print(f"    Hit rate:     {lru.hit_rate():.1%}")

    print(f"\n  Naive Cache (O(n) space, unbounded):")
    print(f"    Cache size:   {len(naive.cache):,} entries")
    print(f"    Memory used:  ~{naive.memory_usage_bytes(value_bytes) / 1024:.1f} KB")
    print(f"    Hit rate:     {naive.hit_rate():.1%}")

    print(f"\n  Memory ratio: {naive.memory_usage_bytes() / lru.memory_usage_bytes():.0f}x more memory for naive cache")
    print(f"  Hit rate difference: {abs(lru.hit_rate() - naive.hit_rate()):.1%}")

    # Project to 100M users
    users_100m = 100_000_000
    naive_memory_gb = users_100m * value_bytes / 1e9
    lru_memory_kb = lru_size * value_bytes / 1e3
    print(f"\n  Projected at 100M total users:")
    print(f"    Naive cache: {naive_memory_gb:.0f} GB RAM needed")
    print(f"    LRU cache:   {lru_memory_kb:.0f} KB RAM needed")
    print(f"    Savings:     {naive_memory_gb * 1e6 / lru_memory_kb:.0f}x less memory")


if __name__ == '__main__':
    benchmark_caches()
```

### The Key Insight

The LRU cache exploits **temporal locality** — the observation that recently accessed data is likely to be accessed again soon. In practice, a well-sized LRU cache achieves 80-95% hit rates while using a tiny fraction of the memory that a naive cache would require.

Python's `functools.lru_cache` decorator uses this exact approach. When you use it, you are getting O(k) space instead of O(n) space, essentially for free.

---

## 4. Recursive Algorithms and Stack Overflow — The Tower of Fibonacci

### The Story

A junior developer is implementing a Fibonacci sequence calculator. She writes the most natural, intuitive implementation she can think of:

```python
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

It works perfectly for small values. `fib(10)` returns 55 instantly. `fib(30)` takes about half a second (already a warning sign). Then someone calls `fib(50)` in production, and the server hangs indefinitely.

### The Complexity Disaster

The naive recursive Fibonacci has **O(2^n) time complexity**. Each call branches into two calls, which each branch into two calls, forming a binary tree of calls.

```
Call tree for fib(6):

                        fib(6)
                       /      \
                  fib(5)        fib(4)
                 /    \         /    \
             fib(4)  fib(3)  fib(3)  fib(2)
             /  \    /  \    /  \    /  \
          fib(3) fib(2) fib(2) fib(1)  ...

Repeated work marked with (*):
  fib(4) is computed TWICE
  fib(3) is computed THREE times
  fib(2) is computed FIVE times
  fib(1) is computed EIGHT times

Total calls for fib(n) ≈ 2^n
For fib(50): ≈ 1,125,899,906,842,624 calls
```

But time is not the only problem. Each recursive call adds a frame to the **call stack**. Python's default recursion limit is 1,000. Call `fib(1500)` and you get:

```
RecursionError: maximum recursion depth exceeded in comparison
```

This is a **stack overflow** — not the website, but the actual error where you exhaust the call stack.

### Three Approaches Compared

```python
import sys
import time
from functools import lru_cache


# ── APPROACH 1: Naive Recursion ──────────────────────────────────────────────
# Time: O(2^n), Space: O(n) call stack
def fib_naive(n):
    """The intuitive but catastrophically slow version."""
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


# ── APPROACH 2: Memoized Recursion ───────────────────────────────────────────
# Time: O(n), Space: O(n) for memo + O(n) call stack = O(n) total
# But still hits recursion limit for large n!
@lru_cache(maxsize=None)
def fib_memo(n):
    """
    Cache results to avoid recomputation.
    Time: O(n) — each value computed exactly once.
    But still uses O(n) stack depth!
    """
    if n <= 1:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)


# ── APPROACH 3: Iterative ────────────────────────────────────────────────────
# Time: O(n), Space: O(1)
# No stack overflow possible. The correct production approach.
def fib_iterative(n):
    """
    The production-ready version.
    Time: O(n), Space: O(1) — no recursion at all.
    """
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_calls_naive(n, counter=None):
    """Count the actual number of calls made by naive recursion."""
    if counter is None:
        counter = [0]
    counter[0] += 1
    if n <= 1:
        return n, counter[0]
    fib_left, _ = count_calls_naive(n - 1, counter)
    fib_right, _ = count_calls_naive(n - 2, counter)
    return fib_left + fib_right, counter[0]


def benchmark_fibonacci():
    print("\n" + "="*60)
    print("FIBONACCI BENCHMARK: Three Approaches")
    print("="*60)

    # Count actual calls for small n
    print("\nActual call counts (naive recursion):")
    print(f"{'n':>6} | {'Calls':>15} | {'Expected ~2^n':>15} | {'Time (ms)':>12}")
    print("-" * 55)

    for n in [5, 10, 15, 20, 25, 30, 35]:
        start = time.perf_counter()
        result, calls = count_calls_naive(n, [0])
        elapsed = time.perf_counter() - start
        expected = 2 ** n
        print(f"{n:>6} | {calls:>15,} | {expected:>15,} | {elapsed*1000:>12.3f}")

    # Compare approaches at safe sizes
    print("\n\nPerformance comparison for fib(35):")
    n = 35

    # Naive
    fib_memo.cache_clear()
    start = time.perf_counter()
    result_naive = fib_naive(n)
    t_naive = time.perf_counter() - start

    # Memoized
    fib_memo.cache_clear()
    start = time.perf_counter()
    result_memo = fib_memo(n)
    t_memo = time.perf_counter() - start

    # Iterative
    start = time.perf_counter()
    result_iter = fib_iterative(n)
    t_iter = time.perf_counter() - start

    print(f"\n  Naive O(2^n):       {t_naive*1000:.3f} ms  (result: {result_naive})")
    print(f"  Memoized O(n):      {t_memo*1000:.4f} ms  (result: {result_memo})")
    print(f"  Iterative O(n),O(1): {t_iter*1000:.4f} ms  (result: {result_iter})")
    print(f"\n  Naive vs Iterative: {t_naive/t_iter:.0f}x slower")

    # Demonstrate stack overflow risk
    print(f"\n\nStack overflow demonstration:")
    print(f"  Default recursion limit: {sys.getrecursionlimit()}")
    print(f"  Trying fib_memo(900)...")

    try:
        sys.setrecursionlimit(1000)
        fib_memo.cache_clear()
        result = fib_memo(900)
        print(f"  fib_memo(900) = {str(result)[:20]}...  [succeeded]")
    except RecursionError:
        print(f"  RecursionError! Stack overflow at depth ~1000")
        print(f"  Even memoized recursion fails for large n!")

    print(f"\n  fib_iterative(900) = {str(fib_iterative(900))[:20]}...")
    print(f"  Iterative works perfectly — no stack involved.")

    print(f"\n  fib_iterative(10000) = {str(fib_iterative(10_000))[:15]}... [works!]")
    print(f"  fib_iterative(1000000): ", end="", flush=True)
    start = time.perf_counter()
    result = fib_iterative(1_000_000)
    elapsed = time.perf_counter() - start
    print(f"computed in {elapsed:.3f}s, {len(str(result)):,} digits")


if __name__ == '__main__':
    benchmark_fibonacci()
```

### The Lesson About Space Complexity

Time complexity gets all the attention, but space complexity — specifically **stack space** — causes its own class of production failures.

Recursive algorithms have an implicit O(depth) space requirement. For `fib(n)`, depth is n, so it is O(n) stack space. At n=1000, Python raises `RecursionError`. At n=10,000, even if you raise the recursion limit, you risk an actual OS-level stack overflow, which can crash the process entirely.

The iterative solution uses O(1) space — just two variables `a` and `b`. It can compute `fib(1,000,000)` without breaking a sweat.

**Rule of thumb**: if you can turn a recursive algorithm into an iterative one without significant code complexity cost, do it in production. Reserve recursion for cases where the recursion depth is bounded by something small (like tree height, which for balanced trees is O(log n)).

---

## 5. String Processing at Scale — Why Google Does Not Scan Every Document

### The Story

Imagine you are building a search engine. Your index contains 1 billion web pages. A user types "quantum computing tutorial" and expects results in under 200 milliseconds.

If you approach this naively — scanning every document for every query — how long would that take?

Average web page: ~5,000 words, ~30,000 characters.
Query: "quantum computing tutorial" — about 26 characters.

Naive substring search (e.g., checking if the query appears in each document) is O(n × m) per document, where n is the document length and m is the query length. But even if you just do a word-level scan:

```
1,000,000,000 documents × 5,000 words per document = 5,000,000,000,000 word comparisons

At 10^9 comparisons per second: ~5,000 seconds ≈ 83 minutes per query
```

Google serves billions of queries per day, each in under 200ms. They are obviously not scanning every document. The answer is the **inverted index**.

### The Inverted Index

An inverted index is the data structure that makes full-text search possible. Instead of mapping document → words, it maps word → list of documents containing that word.

```
Forward Index (what you have naturally):

doc_1: "Python is great for data science"
doc_2: "Data science uses Python and R"
doc_3: "Python tutorial for beginners"
doc_4: "R is used in statistics"

Inverted Index (what you build):

"python"    → [doc_1, doc_2, doc_3]
"data"      → [doc_1, doc_2]
"science"   → [doc_1, doc_2]
"great"     → [doc_1]
"tutorial"  → [doc_3]
"beginners" → [doc_3]
"statistics"→ [doc_4]
"r"         → [doc_2, doc_4]
```

Now, to answer the query "python tutorial":

1. Look up "python" → [doc_1, doc_2, doc_3]   — O(1) hash lookup
2. Look up "tutorial" → [doc_3]                — O(1) hash lookup
3. Intersect the two lists → [doc_3]           — O(min(k1, k2)) where k1, k2 are list sizes

Total: O(1) for the lookups + O(k) to process results, where k is the number of matching documents.

**Compare:**
- Naive scan: O(n × m) per query where n = total documents, m = query length
- Inverted index: O(1) lookup + O(k) intersection where k << n

### Python Implementation

```python
import time
import re
from collections import defaultdict
from typing import Dict, List, Set


class InvertedIndex:
    """
    Full-text search via inverted index.

    Build time: O(total words across all documents)
    Query time: O(query_terms + k) where k = result count
    Space: O(total unique words × avg posting list length)
    """

    def __init__(self):
        # Maps word → set of document IDs containing that word
        self.index: Dict[str, Set[int]] = defaultdict(set)
        self.documents: Dict[int, str] = {}
        self.word_count = 0

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer: lowercase, remove punctuation, split on whitespace."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return text.split()

    def add_document(self, doc_id: int, text: str):
        """
        Index a single document.
        O(d) where d is the number of words in the document.
        """
        self.documents[doc_id] = text
        words = self._tokenize(text)
        for word in words:
            self.index[word].add(doc_id)
            self.word_count += 1

    def search(self, query: str) -> List[int]:
        """
        Find all documents containing all query words (AND search).
        O(q × log n + k) where q = query words, k = result count.
        In practice: effectively O(1) per term lookup.
        """
        query_words = self._tokenize(query)
        if not query_words:
            return []

        # Start with the posting list for the first word
        # (Choose rarest word first for efficiency)
        result_set = self.index.get(query_words[0], set()).copy()

        # Intersect with remaining words
        for word in query_words[1:]:
            word_docs = self.index.get(word, set())
            result_set &= word_docs  # set intersection

        return sorted(result_set)

    def search_or(self, query: str) -> List[int]:
        """Find documents containing ANY query word (OR search)."""
        query_words = self._tokenize(query)
        result_set = set()
        for word in query_words:
            result_set |= self.index.get(word, set())
        return sorted(result_set)

    def stats(self):
        return {
            'total_documents': len(self.documents),
            'unique_terms': len(self.index),
            'total_word_occurrences': self.word_count,
            'avg_posting_list_size': sum(len(v) for v in self.index.values()) / max(len(self.index), 1)
        }


class NaiveSearch:
    """
    Naive full-text search: scan every document for every query.
    O(n × d × q) where n = docs, d = doc length, q = query length.
    """

    def __init__(self):
        self.documents: Dict[int, str] = {}

    def add_document(self, doc_id: int, text: str):
        self.documents[doc_id] = text

    def search(self, query: str) -> List[int]:
        """Scan every document for every query term. O(n × d)."""
        query_words = query.lower().split()
        results = []
        for doc_id, text in self.documents.items():
            text_lower = text.lower()
            # Check if ALL query words appear in document
            if all(word in text_lower for word in query_words):
                results.append(doc_id)
        return sorted(results)


def generate_fake_documents(n: int):
    """Generate n fake documents about various tech topics."""
    import random

    topics = {
        'python': ['python', 'programming', 'code', 'function', 'class', 'object'],
        'data': ['data', 'science', 'analysis', 'machine', 'learning', 'statistics'],
        'web': ['web', 'html', 'css', 'javascript', 'server', 'request', 'response'],
        'cloud': ['cloud', 'aws', 'server', 'deployment', 'docker', 'container'],
        'database': ['database', 'sql', 'query', 'index', 'table', 'schema'],
    }

    documents = {}
    topic_keys = list(topics.keys())

    for i in range(n):
        # Each doc is about 1-3 topics
        chosen_topics = random.sample(topic_keys, random.randint(1, 3))
        words = []
        for topic in chosen_topics:
            words.extend(random.choices(topics[topic], k=random.randint(10, 30)))
        random.shuffle(words)
        documents[i] = ' '.join(words)

    return documents


def benchmark_search(n_docs=10_000):
    print(f"\n{'='*60}")
    print(f"SEARCH ENGINE BENCHMARK: {n_docs:,} documents")
    print(f"{'='*60}")

    docs = generate_fake_documents(n_docs)
    query = "python data"

    # Build inverted index
    start = time.perf_counter()
    inv_index = InvertedIndex()
    for doc_id, text in docs.items():
        inv_index.add_document(doc_id, text)
    build_time = time.perf_counter() - start

    # Build naive search
    naive = NaiveSearch()
    for doc_id, text in docs.items():
        naive.add_document(doc_id, text)

    # Query inverted index
    times_inv = []
    for _ in range(100):
        start = time.perf_counter()
        results_inv = inv_index.search(query)
        times_inv.append(time.perf_counter() - start)

    # Query naive
    times_naive = []
    for _ in range(10):
        start = time.perf_counter()
        results_naive = naive.search(query)
        times_naive.append(time.perf_counter() - start)

    avg_inv = sum(times_inv) / len(times_inv)
    avg_naive = sum(times_naive) / len(times_naive)

    stats = inv_index.stats()
    print(f"\nIndex statistics:")
    print(f"  Documents indexed: {stats['total_documents']:,}")
    print(f"  Unique terms: {stats['unique_terms']:,}")
    print(f"  Index build time: {build_time*1000:.2f} ms")

    print(f"\nQuery: '{query}'")
    print(f"  Results found: {len(results_inv)} documents")

    print(f"\nSearch performance (avg over multiple runs):")
    print(f"  Inverted Index O(1+k): {avg_inv*1000:.4f} ms")
    print(f"  Naive scan O(n×d):     {avg_naive*1000:.3f} ms")
    if avg_inv > 0:
        print(f"  Speedup: {avg_naive/avg_inv:.0f}x faster")

    print(f"\nProjected for 1 billion documents:")
    scale = 1_000_000_000 / n_docs
    print(f"  Inverted Index: ~{avg_inv * 1000:.4f} ms (index lookup is O(1), constant)")
    print(f"  Naive scan:     ~{avg_naive * scale / 1000:.0f} seconds per query")
    print(f"  Google's actual latency: ~100-200 ms")
    print(f"  Naive scan would take: HOURS per query")


if __name__ == '__main__':
    benchmark_search(10_000)
```

### The Core Lesson

The inverted index illustrates a powerful pattern: **precompute work at write time to make read time fast**. Building the index is expensive (O(total words)), but you only do it once. Every query thereafter is O(1) per term.

This trade-off — paying more at write time for cheaper reads — is one of the most common architectural patterns in high-scale systems. Databases do it with indexes. Search engines do it with inverted indexes. Recommendation systems do it with precomputed embeddings.

---

## 6. Complexity Hidden in Library Calls — The Invisible Tax

### The Story

A developer is building a queue of tasks for a background job processor. She decides to use a Python list. She adds new tasks to the front of the list (highest priority) using `list.insert(0, item)` in a loop.

It works. Code passes review. Everyone goes home.

But six months later, the task queue occasionally spikes to 50,000 items. The insert operations, which take microseconds at queue size 100, now take milliseconds each. And they are happening tens of thousands of times per second.

Why? Because `list.insert(0, item)` is **O(n)**.

### The Hidden Cost of List Operations

Python's `list` is backed by a dynamic array. All elements are stored contiguously in memory. To insert at position 0, every single existing element must be shifted one position to the right.

```
Inserting 'X' at index 0 of [A, B, C, D, E]:

Before:  [A, B, C, D, E]
Step 1:  shift E right → [A, B, C, D, E, _]
Step 2:  shift D right → [A, B, C, D, _, E]
Step 3:  shift C right → [A, B, C, _, D, E]
Step 4:  shift B right → [A, B, _, C, D, E]
Step 5:  shift A right → [A, _, B, C, D, E]
Step 6:  place X at 0 → [X, A, B, C, D, E]

Total shifts = n (the entire list)
```

This is O(n) per insertion. If you do n insertions, you get O(n²) total — the same 3am nightmare from earlier.

### The Fix: `collections.deque`

Python's `collections.deque` (double-ended queue) is backed by a doubly linked list of fixed-size blocks. Appending to either end is **O(1) amortized**.

```
deque.appendleft('X'):

Before:  ... <-> [A] <-> [B] <-> [C] <-> ...
After:   ... <-> [X] <-> [A] <-> [B] <-> [C] <-> ...

No shifting. Just pointer manipulation.
O(1) always.
```

### Full Benchmark

```python
import time
from collections import deque


def benchmark_prepend_operations(n=10_000):
    print(f"\n{'='*60}")
    print(f"PREPEND BENCHMARK: {n:,} operations")
    print(f"{'='*60}")

    # Method 1: list.insert(0, x) — O(n) each, O(n²) total
    data_list = []
    start = time.perf_counter()
    for i in range(n):
        data_list.insert(0, i)
    t_list_insert = time.perf_counter() - start

    # Method 2: deque.appendleft(x) — O(1) each, O(n) total
    data_deque = deque()
    start = time.perf_counter()
    for i in range(n):
        data_deque.appendleft(i)
    t_deque = time.perf_counter() - start

    # Method 3: reverse list (insert at end O(1), then reverse O(n) once)
    data_list_end = []
    start = time.perf_counter()
    for i in range(n):
        data_list_end.append(i)
    data_list_end.reverse()
    t_list_end = time.perf_counter() - start

    print(f"\n  list.insert(0, x) × {n:,}:    {t_list_insert*1000:.2f} ms   O(n²) total")
    print(f"  deque.appendleft(x) × {n:,}:  {t_deque*1000:.2f} ms   O(n) total")
    print(f"  list.append + reverse:       {t_list_end*1000:.2f} ms   O(n) total")

    print(f"\n  deque is {t_list_insert/t_deque:.0f}x faster than list.insert(0, ...)")

    # Show how the gap grows with n
    print(f"\n  Scaling comparison:")
    print(f"  {'n':>8} | {'list.insert O(n²)':>20} | {'deque O(n)':>14} | {'Ratio':>8}")
    print(f"  {'-'*60}")

    for size in [1_000, 5_000, 10_000, 50_000]:
        lst = []
        start = time.perf_counter()
        for i in range(size):
            lst.insert(0, i)
        t_l = time.perf_counter() - start

        dq = deque()
        start = time.perf_counter()
        for i in range(size):
            dq.appendleft(i)
        t_d = time.perf_counter() - start

        print(f"  {size:>8,} | {t_l*1000:>18.2f} ms | {t_d*1000:>12.4f} ms | {t_l/t_d:>7.0f}x")


def benchmark_membership_check(n=100_000):
    """
    Demonstrate hidden O(n) cost of 'in' operator on list vs set.
    """
    print(f"\n{'='*60}")
    print(f"MEMBERSHIP CHECK BENCHMARK: 'x in collection'")
    print(f"{'='*60}")

    data = list(range(n))
    data_set = set(data)

    target = n - 1  # Worst case for list: it's the last element

    # Check membership many times
    iterations = 10_000

    # List: O(n) per check
    start = time.perf_counter()
    for _ in range(iterations):
        _ = target in data
    t_list = time.perf_counter() - start

    # Set: O(1) per check
    start = time.perf_counter()
    for _ in range(iterations):
        _ = target in data_set
    t_set = time.perf_counter() - start

    print(f"\n  Collection size: {n:,}")
    print(f"  Iterations: {iterations:,}")
    print(f"\n  'x in list' (O(n)):  {t_list*1000:.2f} ms total  |  {t_list/iterations*1e6:.2f} µs each")
    print(f"  'x in set'  (O(1)):  {t_set*1000:.2f} ms total  |  {t_set/iterations*1e6:.2f} µs each")
    print(f"\n  Set is {t_list/t_set:.0f}x faster for membership checks")
    print(f"\n  Real cost: if you check membership in a loop of 1M iterations:")
    print(f"    list: ~{t_list / iterations * 1_000_000:.0f} ms")
    print(f"    set:  ~{t_set / iterations * 1_000_000:.0f} ms")


# Other hidden complexities
HIDDEN_COSTS = """
HIDDEN COMPLEXITY CHEAT SHEET — Python Operations That Surprise People
=======================================================================

Operation                   | Complexity | Common Mistake
-----------------------------------------------------------------
list.insert(0, x)           | O(n)       | Use deque.appendleft(x) instead
list.pop(0)                 | O(n)       | Use deque.popleft() instead
'x in list'                 | O(n)       | Use 'x in set' for O(1)
sorted(list)                | O(n log n) | Fine, but don't call inside a loop
list.index(x)               | O(n)       | Use dict for O(1) by-value lookup
list + list (concatenation) | O(n+m)     | Use extend() to avoid copy
list * k (repetition)       | O(n*k)     | Creates a full copy
dict.keys() list(...)       | O(n)       | Just iterate dict directly
set.add(x)                  | O(1)*      | *Amortized; rare O(n) on resize
dict[key]                   | O(1)*      | *Amortized
list.append(x)              | O(1)*      | *Amortized (dynamic array)
list[-1] / list[i]          | O(1)       | Index access is always O(1)
len(list/dict/set/str)      | O(1)       | Length stored separately
str + str (in a loop)       | O(n²)!     | Use ''.join(list_of_strings)
str.split() / str.join()    | O(n)       | Fine, just be aware
"""

if __name__ == '__main__':
    benchmark_prepend_operations(10_000)
    benchmark_membership_check(100_000)
    print(HIDDEN_COSTS)
```

### The Most Dangerous Hidden Cost: String Concatenation

This deserves special mention. In a loop:

```python
# BAD: O(n²) — creates a new string on each iteration
result = ""
for word in words:
    result = result + word  # Each + copies the entire existing string!

# GOOD: O(n) — collect parts, join once
result = "".join(words)
```

If `words` has 10,000 items, the bad version creates 10,000 + 9,999 + 9,998 + ... + 1 character copies — that is approximately n²/2 = 50,000,000 character copies. The good version copies each character exactly once — n copies total. The difference at scale is enormous.

---

## 7. Complexity Cheat Sheet — Python Data Structures

This is your quick-reference guide. Keep it bookmarked.

```
╔══════════════════════════════════════════════════════════════════════════╗
║              PYTHON DATA STRUCTURE COMPLEXITY CHEAT SHEET               ║
╠══════════════════════════════════════════════════════════════════════════╣
║  LIST (Dynamic Array)                                                    ║
╠══════════════════════════════════════════════════╦═══════════╦══════════╣
║  Operation                                       ║  Average  ║  Worst   ║
╠══════════════════════════════════════════════════╬═══════════╬══════════╣
║  list[i] — Index access                          ║   O(1)    ║  O(1)    ║
║  list.append(x) — Append to end                  ║   O(1)*   ║  O(n)    ║
║  list.pop() — Remove from end                    ║   O(1)*   ║  O(n)    ║
║  list.insert(i, x) — Insert at index i           ║   O(n)    ║  O(n)    ║
║  list.pop(i) — Remove at index i                 ║   O(n)    ║  O(n)    ║
║  list.insert(0, x) — Prepend                     ║   O(n)    ║  O(n)    ║
║  list.pop(0) — Remove from front                 ║   O(n)    ║  O(n)    ║
║  x in list — Membership check                    ║   O(n)    ║  O(n)    ║
║  list.index(x) — Find index of x                 ║   O(n)    ║  O(n)    ║
║  list.remove(x) — Remove by value                ║   O(n)    ║  O(n)    ║
║  len(list) — Length                              ║   O(1)    ║  O(1)    ║
║  sorted(list) — Sort                             ║  O(n log n) ║ O(n log n) ║
║  list.sort() — Sort in place                     ║  O(n log n) ║ O(n log n) ║
║  list.reverse() — Reverse                        ║   O(n)    ║  O(n)    ║
║  list[a:b] — Slice                               ║   O(k)    ║  O(n)    ║
║  list1 + list2 — Concatenate                     ║  O(n+m)   ║  O(n+m)  ║
╠══════════════════════════════════════════════════╩═══════════╩══════════╣
║  DICT (Hash Table)                                                       ║
╠══════════════════════════════════════════════════╦═══════════╦══════════╣
║  dict[key] — Get                                 ║   O(1)*   ║  O(n)    ║
║  dict[key] = value — Set                         ║   O(1)*   ║  O(n)    ║
║  del dict[key] — Delete                          ║   O(1)*   ║  O(n)    ║
║  key in dict — Membership                        ║   O(1)*   ║  O(n)    ║
║  len(dict) — Length                              ║   O(1)    ║  O(1)    ║
║  dict.keys() / .values() / .items()              ║   O(1)    ║  O(1)    ║
║  Iterate over dict                               ║   O(n)    ║  O(n)    ║
╠══════════════════════════════════════════════════╩═══════════╩══════════╣
║  SET (Hash Set)                                                          ║
╠══════════════════════════════════════════════════╦═══════════╦══════════╣
║  set.add(x) — Add                                ║   O(1)*   ║  O(n)    ║
║  set.discard(x) / remove(x) — Remove             ║   O(1)*   ║  O(n)    ║
║  x in set — Membership                           ║   O(1)*   ║  O(n)    ║
║  len(set) — Length                               ║   O(1)    ║  O(1)    ║
║  set1 & set2 — Intersection                      ║ O(min(a,b)) ║ O(n)   ║
║  set1 | set2 — Union                             ║  O(a+b)   ║  O(n)    ║
║  set1 - set2 — Difference                        ║   O(a)    ║  O(n)    ║
║  set1 <= set2 — Subset check                     ║   O(a)    ║  O(n)    ║
╠══════════════════════════════════════════════════╩═══════════╩══════════╣
║  DEQUE (Double-Ended Queue — collections.deque)                          ║
╠══════════════════════════════════════════════════╦═══════════╦══════════╣
║  deque.append(x) — Append to right               ║   O(1)    ║  O(1)    ║
║  deque.appendleft(x) — Append to left            ║   O(1)    ║  O(1)    ║
║  deque.pop() — Remove from right                 ║   O(1)    ║  O(1)    ║
║  deque.popleft() — Remove from left              ║   O(1)    ║  O(1)    ║
║  deque[i] — Index access (random)                ║   O(n)    ║  O(n)    ║
║  x in deque — Membership                         ║   O(n)    ║  O(n)    ║
║  len(deque) — Length                             ║   O(1)    ║  O(1)    ║
╠══════════════════════════════════════════════════╩═══════════╩══════════╣
║  HEAPQ (Min Heap — heapq module)                                         ║
╠══════════════════════════════════════════════════╦═══════════╦══════════╣
║  heapq.heappush(h, x) — Insert                   ║ O(log n)  ║ O(log n) ║
║  heapq.heappop(h) — Remove minimum               ║ O(log n)  ║ O(log n) ║
║  h[0] — Peek minimum                             ║   O(1)    ║  O(1)    ║
║  heapq.heapify(list) — Build heap from list       ║   O(n)    ║  O(n)    ║
╠══════════════════════════════════════════════════╩═══════════╩══════════╣
║  STRING                                                                  ║
╠══════════════════════════════════════════════════╦═══════════╦══════════╣
║  s[i] — Index access                             ║   O(1)    ║  O(1)    ║
║  len(s) — Length                                 ║   O(1)    ║  O(1)    ║
║  s + t — Concatenation                           ║  O(n+m)   ║  O(n+m)  ║
║  s * k — Repetition                              ║   O(nk)   ║  O(nk)   ║
║  s in t — Substring check                        ║  O(n×m)   ║  O(n×m)  ║
║  s.split() / ''.join(list)                       ║   O(n)    ║  O(n)    ║
║  s + s + s (in loop, n times)                    ║   O(n²)!  ║  O(n²)   ║
╚══════════════════════════════════════════════════╩═══════════╩══════════╝

* Amortized O(1): occasionally O(n) due to resize, but average is O(1)
```

---

## 8. Amortized Analysis — The Dynamic Array's Secret

### The Question That Confuses Everyone

You know that `list.append(x)` is O(1) amortized. But occasionally it is O(n). How can something be both O(n) and O(1)?

The answer is **amortized analysis** — a way of analyzing algorithms by looking at the total cost of a sequence of operations, not just individual operations.

### The Dynamic Array Doubling Story

Python's list (like C++'s vector, Java's ArrayList) is backed by a dynamic array. When the array is full and you try to append, it must:

1. Allocate a new array of double the size
2. Copy all existing elements to the new array
3. Insert the new element

Step 2 is O(n). So why do we say append is O(1) amortized?

Because doublings are rare. Let us trace through the first 16 appends:

```
Capacity: 1 → 2 → 4 → 8 → 16 (doubles each time)

Append 1:  [1]           size=1, capacity=1   → copy cost = 0 (first element)
Append 2:  [1,2]         size=2, capacity=2   → must resize! copy 1 element
Append 3:  [1,2,3]       size=3, capacity=4   → must resize! copy 2 elements
Append 4:  [1,2,3,4]     size=4, capacity=4   → no resize
Append 5:  [1,2,3,4,5]   size=5, capacity=8   → must resize! copy 4 elements
Append 6:  [...]          size=6, capacity=8   → no resize
Append 7:  [...]          size=7, capacity=8   → no resize
Append 8:  [...]          size=8, capacity=8   → no resize
Append 9:  [...]          size=9, capacity=16  → must resize! copy 8 elements
...
Append 16: [...]          size=16, capacity=16 → no resize
Append 17: [...]          size=17, capacity=32 → must resize! copy 16 elements

Resizes and their costs: 1, 2, 4, 8, 16 = 31 total copy operations for 17 appends
```

For n appends, the total copy cost is:
```
1 + 2 + 4 + 8 + ... + n/2 = n - 1
```

That is, a geometric series that sums to approximately n. So for n appends, total copy work is O(n). Divided by n appends: O(1) amortized per append.

### The Banker's Analogy

Think of it like a savings account. Each "cheap" append (when no resize is needed) puts a coin in the bank. Each "expensive" append (with a resize) withdraws coins from the bank to pay for the copying.

Because the array doubles each time, by the time you resize again, you have twice as many "saved up" coins as the resize will cost. The bank never goes negative. The average cost per operation stays constant.

```python
def demonstrate_amortized_append():
    """
    Shows the actual resize events as you append to a Python list.
    Illustrates the doubling strategy.
    """
    import sys

    lst = []
    prev_size = sys.getsizeof(lst)
    resize_count = 0
    total_copy_work = 0
    current_logical_capacity = 0

    print(f"{'Items':>6} | {'List object size (bytes)':>24} | {'Resize?':>8} | {'Approx capacity':>16}")
    print("-" * 65)

    for i in range(65):
        lst.append(i)
        new_size = sys.getsizeof(lst)

        resized = "YES ← copy!" if new_size > prev_size else ""
        if new_size > prev_size:
            resize_count += 1
            # Approximate copy work
            total_copy_work += len(lst) - 1

        # Python's actual growth factor is slightly more than 2 for small lists
        # but approximates doubling for large ones
        if i < 20 or new_size > prev_size:
            print(f"{i+1:>6} | {new_size:>24} | {resized:>8} |")

        prev_size = new_size

    print(f"\nTotal appends: {len(lst)}")
    print(f"Total resize events: {resize_count}")
    print(f"Approximate total copy work: {total_copy_work}")
    print(f"Ratio (copy work / appends): {total_copy_work / len(lst):.2f}")
    print(f"\nConclusion: Total copy work ≈ O(n), so per append ≈ O(1) amortized")


if __name__ == '__main__':
    demonstrate_amortized_append()
```

### When Amortized Analysis Matters in Practice

Amortized analysis explains why:

- `list.append()` is faster in practice than its worst case suggests
- Building a list with repeated appends is O(n), not O(n²)
- You should **not** pre-size Python lists unless profiling shows it matters
- The difference between `list.append()` (O(1) amortized) and `list.insert(0, x)` (O(n) always) is stark — there is no "amortized rescue" for insert at front

---

## Final Summary: The Five Rules

After all these stories and benchmarks, here are the five rules that should guide every production engineer:

**Rule 1: The slowdown is non-linear.**
Going from O(n) to O(n²) does not just make things "slower." At n=10,000, it makes things 10,000x slower. Complexity matters exponentially at scale.

**Rule 2: Database indexes are O(log n) lookups.**
A table scan is O(n). An indexed lookup is O(log n). Adding an index is often a 1,000x–100,000x speedup. Always index the columns you filter on.

**Rule 3: Memory grows silently.**
O(n) space complexity does not cause an error. It causes the system to slowly consume RAM until it crashes at 3am. Bound your caches. Use LRU. Be explicit about memory.

**Rule 4: Recursion has a hidden O(depth) space cost.**
Every recursive call is a stack frame. For tree problems with depth O(log n), this is fine. For problems with depth O(n), consider iterative solutions or explicit stacks.

**Rule 5: Know your data structure's hidden costs.**
`list.insert(0, x)` is O(n). `'x' in list` is O(n). String concatenation in a loop is O(n²). These are not rare edge cases — they are things developers write every day without realizing the cost.

The goal of Big-O analysis is not to pass algorithm interviews. It is to write software that still works when the number of users multiplies by a thousand.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
