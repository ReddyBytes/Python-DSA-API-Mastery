# Two Pointers — Real-World Usage

The two-pointer technique reduces problems that naively require O(n²) nested
loops down to O(n) by maintaining two indices that move through a data structure
in a coordinated way. It appears in database internals, compiler passes,
text processing, algorithm implementations, financial analytics, and simulation
engines. Every example below is grounded in real production scenarios.

---

## 1. Database Join Optimization — Sort-Merge Join

### The Production Problem

When PostgreSQL, MySQL, or any RDBMS must JOIN two large tables on a key
column, it has three strategies: nested-loop join (O(n * m)), hash join
(O(n + m) but requires memory), and sort-merge join (O(n log n + m log m),
low memory). Sort-merge join is the preferred strategy when both tables are
already indexed (pre-sorted) on the join key, or when memory is constrained.

The algorithm is two pointers: one for each sorted table. At each step, advance
the pointer pointing to the smaller key. When keys match, emit the joined row
and advance both. This is O(n + m) after sorting — far better than the O(n*m)
nested loop that beginners write.

```python
from typing import Any

# -----------------------------------------------------------------------
# Sort-Merge Join — how databases join large sorted result sets
# -----------------------------------------------------------------------

def merge_join(
    table_a: list[dict],
    table_b: list[dict],
    key: str
) -> list[dict]:
    """
    Sort-merge join on a shared key column.
    Both tables must be sorted by the key (or have an index on it).

    This is the algorithm PostgreSQL uses when the planner sees that
    both sides of a join are already sorted (e.g., both have a btree
    index on the join key, or a preceding ORDER BY sorts them).

    Time:  O(n + m) after sorting  — vs  O(n * m) nested loop
    Space: O(1) extra (output excluded)
    """
    # In production, tables arrive pre-sorted from index scans.
    # We sort here to show the full pipeline.
    sorted_a = sorted(table_a, key=lambda r: r[key])
    sorted_b = sorted(table_b, key=lambda r: r[key])

    result = []
    i, j = 0, 0

    while i < len(sorted_a) and j < len(sorted_b):
        key_a = sorted_a[i][key]
        key_b = sorted_b[j][key]

        if key_a == key_b:
            # Keys match — emit the joined row
            # Handle the case where multiple rows share the same key (one-to-many)
            # We collect all matching rows from both sides before advancing
            match_val = key_a

            # Collect all rows from A with this key
            a_group = []
            while i < len(sorted_a) and sorted_a[i][key] == match_val:
                a_group.append(sorted_a[i])
                i += 1

            # Collect all rows from B with this key
            b_group = []
            while j < len(sorted_b) and sorted_b[j][key] == match_val:
                b_group.append(sorted_b[j])
                j += 1

            # Cross-product of matching groups (cartesian join of equal keys)
            for row_a in a_group:
                for row_b in b_group:
                    joined = {**row_a}
                    for col, val in row_b.items():
                        if col != key:
                            joined[f"b_{col}"] = val
                    result.append(joined)

        elif key_a < key_b:
            i += 1  # A is behind — advance A pointer
        else:
            j += 1  # B is behind — advance B pointer

    return result


def nested_loop_join(table_a, table_b, key):
    """O(n * m) naive join — what you get without optimization."""
    result = []
    for row_a in table_a:
        for row_b in table_b:
            if row_a[key] == row_b[key]:
                joined = {**row_a}
                for col, val in row_b.items():
                    if col != key:
                        joined[f"b_{col}"] = val
                result.append(joined)
    return result


# -----------------------------------------------------------------------
# Demo: join orders with customers
# -----------------------------------------------------------------------
import time
import random

customers = [
    {"customer_id": i, "name": f"Customer_{i}", "tier": random.choice(["gold", "silver", "bronze"])}
    for i in range(1, 10001)
]

orders = [
    {"order_id": j, "customer_id": random.randint(1, 10000),
     "amount": round(random.uniform(10.0, 500.0), 2)}
    for j in range(1, 50001)
]

# Sort-merge join
start = time.perf_counter()
result_smj = merge_join(orders, customers, "customer_id")
smj_ms = (time.perf_counter() - start) * 1000

# Nested loop join on small subset for comparison
small_customers = customers[:100]
small_orders    = [o for o in orders if o["customer_id"] <= 100]

start = time.perf_counter()
result_nlj = nested_loop_join(small_orders, small_customers, "customer_id")
nlj_ms = (time.perf_counter() - start) * 1000

print(f"Tables: {len(orders):,} orders  x  {len(customers):,} customers")
print(f"Sort-merge join:   {smj_ms:.1f} ms  ({len(result_smj):,} joined rows)")
print(f"Nested-loop join (100-row subset): {nlj_ms:.1f} ms  ({len(result_nlj):,} joined rows)")
print(f"\nSample joined row: {result_smj[0]}")
```

---

## 2. Deduplication — Remove Duplicates from Sorted Log Files

### The Production Problem

Log aggregation systems (Splunk, Elasticsearch, Loki) ingest billions of log
lines per day. When multiple collectors send logs, duplicates are common — the
same line appears twice from two replicas. After sorting logs by timestamp and
content, deduplication is a two-pointer (slow/fast pointer) operation: the slow
pointer marks the last unique position, the fast pointer scans ahead. This is
O(n) time and O(1) extra space — critical when processing multi-gigabyte logs.

```python
from dataclasses import dataclass
from typing import Generator
import time

@dataclass
class LogEntry:
    timestamp: str
    level: str
    message: str
    source: str

    def __eq__(self, other):
        # Two log entries are duplicates if timestamp + level + message match
        # (source may differ — same event from two collectors)
        return (self.timestamp == other.timestamp and
                self.level    == other.level and
                self.message  == other.message)

    def __lt__(self, other):
        return (self.timestamp, self.message) < (other.timestamp, other.message)

    def __repr__(self):
        return f"[{self.timestamp}] {self.level}: {self.message} (from {self.source})"


def deduplicate_sorted_log(entries: list[LogEntry]) -> list[LogEntry]:
    """
    Remove duplicate log entries using slow/fast two-pointer technique.
    Assumes entries are sorted (by timestamp then message).

    The slow pointer `write_pos` tracks where the next unique entry goes.
    The fast pointer `read_pos` scans through all entries.

    This is analogous to LeetCode #26 (Remove Duplicates from Sorted Array)
    but applied to real log deduplication — used in log pipeline ETL jobs.

    Time:  O(n)  (single pass)
    Space: O(1)  (modifies in place, no extra list needed)
    """
    if not entries:
        return entries

    write_pos = 0  # slow pointer: position of last written unique entry

    for read_pos in range(1, len(entries)):  # fast pointer
        if entries[read_pos] != entries[write_pos]:
            # Found a new unique entry — advance write pointer and record it
            write_pos += 1
            entries[write_pos] = entries[read_pos]
        # If equal, fast pointer just advances — duplicate is skipped

    return entries[:write_pos + 1]


def deduplicate_sorted_log_generator(entries: list[LogEntry]) -> Generator[LogEntry, None, None]:
    """
    Memory-efficient generator version for streaming log processing.
    Yields unique entries one at a time — useful for huge log files
    processed line by line without loading all into memory.
    """
    if not entries:
        return

    prev = entries[0]
    yield prev

    for entry in entries[1:]:
        if entry != prev:
            yield entry
            prev = entry


# -----------------------------------------------------------------------
# Demo: deduplicate a batch of log entries from two collectors
# -----------------------------------------------------------------------

import random

def generate_log_batch(n_unique: int, duplicate_rate: float = 0.3) -> list[LogEntry]:
    levels = ["INFO", "WARN", "ERROR", "DEBUG"]
    messages = [
        "User login attempt", "Database query executed", "Cache miss",
        "Request timeout", "Connection pool exhausted", "Health check OK",
        "Config reloaded", "Scheduled job started", "Payment processed",
        "Email sent", "File uploaded", "Session expired",
    ]
    sources = ["collector-1", "collector-2"]

    # Generate unique entries
    unique = [
        LogEntry(
            timestamp=f"2024-01-15T{10 + i//3600:02d}:{(i%3600)//60:02d}:{i%60:02d}Z",
            level=random.choice(levels),
            message=random.choice(messages) + f" #{i}",
            source=random.choice(sources)
        )
        for i in range(n_unique)
    ]

    # Add duplicates (same event from second collector)
    duplicates = [
        LogEntry(e.timestamp, e.level, e.message, "collector-2")
        for e in unique
        if random.random() < duplicate_rate
    ]

    all_entries = sorted(unique + duplicates)
    return all_entries, len(duplicates)


N = 100_000
entries, num_dupes = generate_log_batch(N, duplicate_rate=0.3)

print(f"Total log entries (with duplicates): {len(entries):,}")
print(f"Injected duplicates: {num_dupes:,}")

start = time.perf_counter()
deduped = deduplicate_sorted_log(entries.copy())
elapsed_ms = (time.perf_counter() - start) * 1000

print(f"After deduplication: {len(deduped):,} unique entries")
print(f"Removed: {len(entries) - len(deduped):,} duplicates")
print(f"Processing time: {elapsed_ms:.1f} ms  (O(n) single pass)")
print(f"\nFirst 3 entries after dedup:")
for e in deduped[:3]:
    print(f"  {e}")
```

---

## 3. Text Processing — Longest Palindromic Substring

### The Production Problem

DNA sequence analysis, plagiarism detection, and text compression all need to
find palindromic substrings. Palindromes appear in biological sequences
(palindromic restriction sites for CRISPR), and the algorithm powering them is
the "expand around center" two-pointer technique. For every center position,
two pointers expand outward as long as the characters match. This runs in O(n)
per center, O(n²) total — far better than the O(n³) brute force approach.

```python
# -----------------------------------------------------------------------
# Longest palindromic substring — two pointers expand from center
# -----------------------------------------------------------------------

def longest_palindromic_substring(s: str) -> tuple[str, int, int]:
    """
    Find the longest palindromic substring using center-expansion.
    Two pointers `left` and `right` expand outward from each center.

    There are 2n-1 possible centers (n single chars + n-1 between chars).
    For each, we expand outward while s[left] == s[right].

    Time:  O(n²)  — O(n) centers × O(n) expansion each
    Space: O(1)   — no auxiliary data structure

    Used in:
      - Bioinformatics: finding palindromic restriction enzyme recognition sites
      - Text compression: palindromes indicate repeated structure
      - Anti-plagiarism: detecting reversed copied text
    """
    if not s:
        return "", 0, 0

    best_start = 0
    best_len   = 1

    def expand_from_center(left: int, right: int) -> tuple[int, int]:
        """Expand two pointers outward while characters match."""
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left  -= 1
            right += 1
        # When loop ends, s[left+1 : right] is the palindrome
        return left + 1, right - 1

    for i in range(len(s)):
        # Case 1: Odd-length palindrome — center is a single character
        l1, r1 = expand_from_center(i, i)
        if r1 - l1 + 1 > best_len:
            best_start = l1
            best_len   = r1 - l1 + 1

        # Case 2: Even-length palindrome — center is between characters i and i+1
        if i + 1 < len(s):
            l2, r2 = expand_from_center(i, i + 1)
            if r2 - l2 + 1 > best_len:
                best_start = l2
                best_len   = r2 - l2 + 1

    return s[best_start : best_start + best_len], best_start, best_start + best_len - 1


def find_all_palindromes(s: str, min_length: int = 3) -> list[tuple[str, int, int]]:
    """
    Find all distinct palindromic substrings of minimum length.
    Used in bioinformatics to find restriction sites.
    """
    found = set()
    results = []

    def expand_from_center(left: int, right: int):
        while left >= 0 and right < len(s) and s[left] == s[right]:
            substr = s[left:right + 1]
            if len(substr) >= min_length and substr not in found:
                found.add(substr)
                results.append((substr, left, right))
            left  -= 1
            right += 1

    for i in range(len(s)):
        expand_from_center(i, i)
        if i + 1 < len(s):
            expand_from_center(i, i + 1)

    return sorted(results, key=lambda x: -len(x[0]))


# -----------------------------------------------------------------------
# Demo 1: Classic string examples
# -----------------------------------------------------------------------

test_cases = [
    "babad",
    "cbbd",
    "racecar",
    "abacaba",
    "amanaplanacanalpanama",
    "forgeeksskeegfor",
]

print("Longest palindromic substrings:")
for s in test_cases:
    palindrome, start, end = longest_palindromic_substring(s)
    print(f"  {s!r:30s}  ->  {palindrome!r:20s}  at [{start}:{end+1}]")

# -----------------------------------------------------------------------
# Demo 2: DNA restriction site detection (bioinformatics)
# -----------------------------------------------------------------------

print("\nDNA palindromic restriction sites (min length 4):")

# EcoRI recognizes GAATTC (its complement CTTAAG is the reverse complement —
# for simplicity here we find exact palindromes in the sequence)
dna_sequences = {
    "E.coli promoter region" : "ATGCGAATTCGCATGCAATTGCATATGCGGATCCATGC",
    "CRISPR target region"   : "GCATGCAAGCTTGCATGCAATTGCATGCAATTGCATGC",
}

for name, dna in dna_sequences.items():
    sites = find_all_palindromes(dna, min_length=4)
    print(f"\n  Sequence: {name}")
    print(f"  Length: {len(dna)} bp")
    for palindrome, start, end in sites[:5]:
        print(f"    Found: {palindrome!r:12s}  at position {start}-{end}")
```

---

## 4. Partition in Quicksort — Two Pointer Approaches Compared

### The Production Problem

Quicksort is the foundation of `sorted()` in CPython (Timsort uses it for
small arrays), C++'s `std::sort`, and Java's `Arrays.sort`. The core operation
is partitioning an array around a pivot. Two classic two-pointer schemes exist:
Lomuto (simpler, used in teaching and some implementations) and Hoare (the
original, fewer swaps in practice). Understanding both reveals how the same
two-pointer idea can be applied differently.

```python
import random
import time

# -----------------------------------------------------------------------
# Lomuto partition — two pointers: i (slow) and j (fast)
# -----------------------------------------------------------------------

def lomuto_partition(arr: list[int], lo: int, hi: int) -> int:
    """
    Lomuto partition scheme.
    pivot = arr[hi]  (last element)
    i = boundary between "≤ pivot" region and "> pivot" region (slow pointer)
    j = scanner (fast pointer), walks from lo to hi-1

    When arr[j] <= pivot, we expand the left region by swapping arr[i+1] and arr[j],
    then advancing i.

    Used in: CLRS textbook, many teaching implementations, Python's heapq
    Swap count: roughly n swaps in the worst case per call
    """
    pivot = arr[hi]
    i = lo - 1  # slow pointer: right boundary of elements <= pivot

    for j in range(lo, hi):   # fast pointer: scanner
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    # Place pivot in its final sorted position
    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
    return i + 1


def quicksort_lomuto(arr: list[int], lo: int = 0, hi: int = None) -> None:
    if hi is None:
        hi = len(arr) - 1
    if lo < hi:
        p = lomuto_partition(arr, lo, hi)
        quicksort_lomuto(arr, lo, p - 1)
        quicksort_lomuto(arr, p + 1, hi)


# -----------------------------------------------------------------------
# Hoare partition — two pointers move inward from both ends
# -----------------------------------------------------------------------

def hoare_partition(arr: list[int], lo: int, hi: int) -> int:
    """
    Hoare partition scheme (original, C.A.R. Hoare, 1962).
    pivot = arr[lo]  (first element)
    i starts before lo (moves right), j starts after hi (moves left).
    They walk inward until they meet — no element is unnecessarily touched.

    Advantage over Lomuto: ~3x fewer swaps on average for random data.
    This is why production implementations (glibc qsort, many STL sorts)
    prefer Hoare-like partitioning.
    """
    pivot = arr[lo + (hi - lo) // 2]  # median-of-three variant for safety
    i = lo - 1   # left pointer (moves right)
    j = hi + 1   # right pointer (moves left)

    while True:
        i += 1
        while arr[i] < pivot:
            i += 1

        j -= 1
        while arr[j] > pivot:
            j -= 1

        if i >= j:
            return j  # partition index

        arr[i], arr[j] = arr[j], arr[i]


def quicksort_hoare(arr: list[int], lo: int = 0, hi: int = None) -> None:
    if hi is None:
        hi = len(arr) - 1
    if lo < hi:
        p = hoare_partition(arr, lo, hi)
        quicksort_hoare(arr, lo, p)
        quicksort_hoare(arr, p + 1, hi)


# -----------------------------------------------------------------------
# Swap counter — instrument partition to count swaps
# -----------------------------------------------------------------------

def count_swaps_lomuto(arr: list[int]) -> int:
    swaps = [0]
    arr = arr.copy()

    def partition(lo, hi):
        pivot = arr[hi]
        i = lo - 1
        for j in range(lo, hi):
            if arr[j] <= pivot:
                i += 1
                if i != j:
                    arr[i], arr[j] = arr[j], arr[i]
                    swaps[0] += 1
        arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
        swaps[0] += 1
        return i + 1

    def qs(lo, hi):
        if lo < hi:
            p = partition(lo, hi)
            qs(lo, p - 1)
            qs(p + 1, hi)

    qs(0, len(arr) - 1)
    return swaps[0]


def count_swaps_hoare(arr: list[int]) -> int:
    swaps = [0]
    arr = arr.copy()

    def partition(lo, hi):
        pivot = arr[lo + (hi - lo) // 2]
        i, j = lo - 1, hi + 1
        while True:
            i += 1
            while arr[i] < pivot:
                i += 1
            j -= 1
            while arr[j] > pivot:
                j -= 1
            if i >= j:
                return j
            arr[i], arr[j] = arr[j], arr[i]
            swaps[0] += 1

    def qs(lo, hi):
        if lo < hi:
            p = partition(lo, hi)
            qs(lo, p)
            qs(p + 1, hi)

    qs(0, len(arr) - 1)
    return swaps[0]


# -----------------------------------------------------------------------
# Benchmark: Lomuto vs Hoare
# -----------------------------------------------------------------------

random.seed(42)
sizes = [1_000, 5_000, 10_000]

print(f"{'Size':>8}  {'Lomuto swaps':>14}  {'Hoare swaps':>12}  {'Hoare advantage':>16}")
print("-" * 60)
for n in sizes:
    data = [random.randint(0, n) for _ in range(n)]
    lomuto_swaps = count_swaps_lomuto(data)
    hoare_swaps  = count_swaps_hoare(data)
    ratio = lomuto_swaps / hoare_swaps if hoare_swaps > 0 else float("inf")
    print(f"{n:>8,}  {lomuto_swaps:>14,}  {hoare_swaps:>12,}  {ratio:>15.1f}x fewer")

# Correctness check
test = [random.randint(0, 1000) for _ in range(500)]
a, b = test.copy(), test.copy()
quicksort_lomuto(a)
quicksort_hoare(b)
print(f"\nBoth produce correct sorted output: {a == b == sorted(test)}")
```

---

## 5. Two-Sum in Financial Data — Transaction Pair Finder

### The Production Problem

Fraud detection systems and accounting reconciliation tools must answer: "do any
two transactions sum to exactly $10,000?" (a common structuring detection
threshold). Anti-money-laundering (AML) systems at banks run this query
continuously on sorted transaction histories. The two-pointer approach on sorted
data finds all pairs in O(n) after sorting — vastly better than the O(n²)
double loop that a naive audit script would use.

```python
from decimal import Decimal
from dataclasses import dataclass
import random
import time

@dataclass
class Transaction:
    tx_id: str
    amount: Decimal
    account: str
    timestamp: str

    def __lt__(self, other):
        return self.amount < other.amount


def find_transaction_pairs(
    transactions: list[Transaction],
    target: Decimal,
    tolerance: Decimal = Decimal("0.01")
) -> list[tuple[Transaction, Transaction]]:
    """
    Find all pairs of transactions summing to `target` amount (± tolerance).
    Uses two-pointer on sorted transactions — O(n log n) total, O(n) after sort.

    This is how bank AML systems detect "structuring" — splitting large
    transactions into pairs that together hit a reporting threshold.

    The tolerance handles floating-point currency representation issues
    and intentional slight offsets used to evade exact-match filters.
    """
    sorted_txns = sorted(transactions, key=lambda t: t.amount)
    pairs = []
    left, right = 0, len(sorted_txns) - 1

    while left < right:
        current_sum = sorted_txns[left].amount + sorted_txns[right].amount
        diff = abs(current_sum - target)

        if diff <= tolerance:
            pairs.append((sorted_txns[left], sorted_txns[right]))
            # Move both pointers — look for more pairs
            # But handle duplicates: advance past all equal values
            left_val  = sorted_txns[left].amount
            right_val = sorted_txns[right].amount
            left  += 1
            right -= 1
            # Skip duplicate amounts on the left
            while left < right and sorted_txns[left].amount == left_val:
                left += 1
            # Skip duplicate amounts on the right
            while left < right and sorted_txns[right].amount == right_val:
                right -= 1
        elif current_sum < target:
            left  += 1  # sum too small — increase by moving left pointer right
        else:
            right -= 1  # sum too large — decrease by moving right pointer left

    return pairs


def find_k_sum_sets(
    transactions: list[Transaction],
    target: Decimal,
    k: int = 3
) -> list[list[Transaction]]:
    """
    Generalization: find k transactions summing to target.
    Uses recursion + two-pointer as base case (k=2).
    Used for more sophisticated structuring detection.
    """
    if k == 2:
        return [list(pair) for pair in find_transaction_pairs(transactions, target)]

    sorted_txns = sorted(transactions, key=lambda t: t.amount)
    results = []

    for i in range(len(sorted_txns) - k + 1):
        if i > 0 and sorted_txns[i].amount == sorted_txns[i-1].amount:
            continue  # skip duplicates

        remaining = sorted_txns[i+1:]
        sub_target = target - sorted_txns[i].amount
        sub_results = find_k_sum_sets(remaining, sub_target, k - 1)

        for group in sub_results:
            results.append([sorted_txns[i]] + group)

    return results


# -----------------------------------------------------------------------
# Demo: AML structuring detection
# -----------------------------------------------------------------------

random.seed(2024)

def make_transactions(n: int) -> list[Transaction]:
    txns = [
        Transaction(
            tx_id=f"TX{i:06d}",
            amount=Decimal(str(round(random.uniform(100, 12000), 2))),
            account=f"ACC{random.randint(1000, 9999)}",
            timestamp=f"2024-01-{random.randint(1,28):02d}T{random.randint(0,23):02d}:00:00Z"
        )
        for i in range(n)
    ]
    return txns

# Inject known structuring pairs (summing to exactly $10,000)
transactions = make_transactions(10_000)
THRESHOLD = Decimal("10000.00")

# Plant 5 structuring pairs
for k in range(5):
    amount_a = Decimal(str(round(random.uniform(3000, 7000), 2)))
    amount_b = THRESHOLD - amount_a
    transactions.append(Transaction(f"STRUCT_A_{k}", amount_a, "SUSPECT_ACC", "2024-01-15T10:00:00Z"))
    transactions.append(Transaction(f"STRUCT_B_{k}", amount_b, "SUSPECT_ACC", "2024-01-15T11:00:00Z"))

# Run detection
start = time.perf_counter()
pairs = find_transaction_pairs(transactions, THRESHOLD, tolerance=Decimal("0.50"))
elapsed_ms = (time.perf_counter() - start) * 1000

print(f"Transactions analyzed: {len(transactions):,}")
print(f"Target threshold: ${THRESHOLD}")
print(f"Suspicious pairs found: {len(pairs)}")
print(f"Detection time: {elapsed_ms:.1f} ms  (O(n log n) sort + O(n) scan)\n")

print("Top suspicious pairs:")
for tx_a, tx_b in sorted(pairs, key=lambda p: abs(p[0].amount + p[1].amount - THRESHOLD))[:5]:
    total = tx_a.amount + tx_b.amount
    print(f"  {tx_a.tx_id}(${tx_a.amount}) + {tx_b.tx_id}(${tx_b.amount}) = ${total}")
```

---

## 6. Water Container — Area Maximization (Civil Engineering Simulation)

### The Production Problem

The "container with most water" problem directly models the structural analysis
of retaining walls, reservoirs, and drainage channels in civil engineering
simulations. Given a cross-sectional height profile of terrain or walls, what
is the maximum volume of water that can be retained between any two walls? The
two-pointer greedy approach gives the O(n) optimal solution.

```python
# -----------------------------------------------------------------------
# Maximum water container — two pointer greedy approach
# -----------------------------------------------------------------------

def max_water_container(heights: list[int]) -> tuple[int, int, int, int]:
    """
    Find two walls that together contain the maximum volume of water.
    The area between wall at index i and wall at index j is:
        min(heights[i], heights[j]) * (j - i)

    Two-pointer greedy proof:
    Start with widest container (i=0, j=n-1). To find a better container,
    we must find a taller minimum wall — so we move the pointer at the
    shorter wall inward (moving the taller wall inward can only decrease area).

    Time:  O(n)
    Space: O(1)

    Real application: civil engineers use this to quickly find the optimal
    placement of two retaining walls along a terrain cross-section to
    maximize water storage capacity.

    Returns: (max_area, left_index, right_index, water_height)
    """
    left  = 0
    right = len(heights) - 1
    max_area  = 0
    best_left = 0
    best_right = len(heights) - 1

    while left < right:
        water_height = min(heights[left], heights[right])
        width        = right - left
        area         = water_height * width

        if area > max_area:
            max_area   = area
            best_left  = left
            best_right = right

        # Move the pointer at the shorter wall — the greedy choice.
        # Moving the taller wall can only keep or reduce the effective height,
        # and reduces width, so area can only decrease or stay the same.
        if heights[left] <= heights[right]:
            left  += 1
        else:
            right -= 1

    return max_area, best_left, best_right, min(heights[best_left], heights[best_right])


def visualize_container(heights: list[int], left: int, right: int) -> None:
    """ASCII visualization of the optimal container."""
    max_h = max(heights)
    water_level = min(heights[left], heights[right])

    print(f"\nTerrain cross-section ({len(heights)} measurement points):")
    for row in range(max_h, 0, -1):
        line = ""
        for i, h in enumerate(heights):
            if h >= row:
                line += "#"  # wall/terrain
            elif i > left and i < right and row <= water_level:
                line += "~"  # water
            else:
                line += " "
        print(f"  {row:3d} | {line}")

    print("      +" + "-" * len(heights))
    print("       " + "".join(str(i % 10) for i in range(len(heights))))
    print(f"\n  Optimal walls: position {left} (height {heights[left]}) "
          f"and position {right} (height {heights[right]})")
    print(f"  Water level: {water_level}  |  Width: {right - left}  |  Area: {water_level * (right - left)}")


# -----------------------------------------------------------------------
# Demo 1: Classic examples
# -----------------------------------------------------------------------

test_cases = [
    [1, 8, 6, 2, 5, 4, 8, 3, 7],
    [1, 1],
    [4, 3, 2, 1, 4],
    [1, 2, 1],
    [2, 3, 4, 5, 18, 17, 6],
]

print("Water container analysis:")
for heights in test_cases:
    area, l, r, wh = max_water_container(heights)
    print(f"  Heights: {heights}")
    print(f"  Max area: {area}  (walls at index {l} and {r}, water height {wh})\n")

# -----------------------------------------------------------------------
# Demo 2: Realistic terrain cross-section visualization
# -----------------------------------------------------------------------

terrain = [3, 1, 2, 4, 0, 1, 3, 2, 5, 2, 2, 1, 4, 3, 2]
area, l, r, wh = max_water_container(terrain)
visualize_container(terrain, l, r)

# -----------------------------------------------------------------------
# Demo 3: Scale test — large terrain survey (O(n) performance)
# -----------------------------------------------------------------------

import random
import time

random.seed(7)
large_terrain = [random.randint(0, 1000) for _ in range(1_000_000)]

start = time.perf_counter()
area, l, r, wh = max_water_container(large_terrain)
elapsed_ms = (time.perf_counter() - start) * 1000

print(f"\nLarge terrain: {len(large_terrain):,} measurement points")
print(f"Max water volume: {area:,} units²")
print(f"Optimal walls: position {l:,} and {r:,}, water level {wh}")
print(f"Computed in: {elapsed_ms:.1f} ms  (O(n) — single pass)")
```

---

## Summary Table

| Use Case | Pointer Movement | Key Insight | Complexity |
|---|---|---|---|
| Sort-merge join | Both advance on match, slower on mismatch | Sorted order eliminates nested loop | O(n + m) |
| Log deduplication | Slow writes, fast reads | Skip equal adjacent elements | O(n) |
| Palindrome detection | Expand outward from center | Symmetric matching | O(n²) |
| Quicksort partition | Lomuto: one-directional; Hoare: inward | Pivot placement in O(n) | O(n) |
| Transaction pair sum | Inward from both ends | Sorted order guides adjustment | O(n) |
| Water container | Inward from both ends | Move shorter wall to find better | O(n) |

The unifying idea: **two pointers eliminate the need to consider all pairs by
exploiting a structural property** — sorted order, symmetry, or monotonicity —
to prune invalid candidates at each step.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Patterns](./patterns.md) &nbsp;|&nbsp; **Next:** [Common Mistakes →](./common_mistakes.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
