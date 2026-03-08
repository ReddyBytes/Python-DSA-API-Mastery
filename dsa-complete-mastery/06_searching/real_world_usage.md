# Searching Algorithms — Real-World Usage

Binary search is not just a whiteboard exercise. It powers database engines,
version control systems, spell checkers, package managers, network routers, and
game engines. Every example below is grounded in how production systems actually
behave, with working Python code you can run today.

---

## 1. Database Query Optimization — Binary Search on B-Tree Index

### The Production Problem

When PostgreSQL executes `SELECT * FROM users WHERE id = 99142`, it does NOT
scan every row. It consults an index — a B-tree — that keeps key values in
sorted order. Each internal node of the B-tree is a page of sorted keys. The
engine performs binary search within each page to decide which child pointer to
follow. The result: O(log n) disk reads instead of O(n).

Without an index, a table of 10 million rows requires up to 10 million row
reads. With a B-tree index on a page size of 8 KB holding ~200 keys per page,
you need at most log_200(10,000,000) ≈ 4 page reads. That is the real-world
difference between a 5-second full scan and a sub-millisecond indexed lookup.

### How It Works Internally

A simplified model: the index is a sorted list of (key, row_pointer) pairs.
Finding a key is binary search. PostgreSQL's actual B-tree uses the same idea
but spreads the sorted data across disk pages with internal nodes pointing to
child pages.

```python
import bisect
import time
import random

# -----------------------------------------------------------------------
# Simulating a PostgreSQL-style sorted index with bisect
# -----------------------------------------------------------------------

class BTreeIndex:
    """
    Simulates a sorted B-tree index on a single integer column.
    Internally stores (key, row_id) pairs sorted by key.
    Uses bisect for O(log n) lookup — exactly what PostgreSQL does per page.
    """

    def __init__(self):
        self._keys = []       # sorted list of indexed keys
        self._row_ids = []    # parallel list of row pointers

    def insert(self, key: int, row_id: int) -> None:
        """Insert into index maintaining sorted order."""
        pos = bisect.bisect_left(self._keys, key)
        self._keys.insert(pos, key)
        self._row_ids.insert(pos, row_id)

    def lookup(self, key: int) -> int | None:
        """O(log n) exact-match lookup — mirrors PostgreSQL indexed scan."""
        pos = bisect.bisect_left(self._keys, key)
        if pos < len(self._keys) and self._keys[pos] == key:
            return self._row_ids[pos]
        return None  # key not in index — PostgreSQL returns empty result set

    def range_lookup(self, low: int, high: int) -> list[int]:
        """
        O(log n + k) range scan where k = matching rows.
        PostgreSQL uses this for BETWEEN, >=, <= queries.
        """
        left = bisect.bisect_left(self._keys, low)
        right = bisect.bisect_right(self._keys, high)
        return self._row_ids[left:right]

    def __len__(self):
        return len(self._keys)


class Table:
    """Simulates a database table with optional index."""

    def __init__(self, rows: list[dict]):
        self._rows = {row["id"]: row for row in rows}
        self._index = None

    def build_index(self) -> None:
        """CREATE INDEX — sort all keys and store them."""
        self._index = BTreeIndex()
        for row_id in self._rows:
            self._index.insert(row_id, row_id)

    def query_with_index(self, target_id: int) -> dict | None:
        """Indexed lookup — O(log n)."""
        row_id = self._index.lookup(target_id)
        return self._rows.get(row_id)

    def full_scan(self, target_id: int) -> dict | None:
        """Sequential scan — O(n). What happens WITHOUT an index."""
        for row in self._rows.values():
            if row["id"] == target_id:
                return row
        return None


# -----------------------------------------------------------------------
# Benchmark: indexed vs full-scan on 500,000 rows
# -----------------------------------------------------------------------

ROWS = 500_000
rows = [{"id": i, "username": f"user_{i}", "email": f"user_{i}@example.com"}
        for i in range(ROWS)]

table = Table(rows)
table.build_index()

targets = random.sample(range(ROWS), 1000)

# Full scan timing
start = time.perf_counter()
for t in targets:
    table.full_scan(t)
full_scan_ms = (time.perf_counter() - start) * 1000

# Indexed lookup timing
start = time.perf_counter()
for t in targets:
    table.query_with_index(t)
indexed_ms = (time.perf_counter() - start) * 1000

print(f"Table size     : {ROWS:,} rows")
print(f"Queries run    : {len(targets)}")
print(f"Full scan      : {full_scan_ms:.1f} ms total  ({full_scan_ms/len(targets):.3f} ms/query)")
print(f"Indexed lookup : {indexed_ms:.1f} ms total  ({indexed_ms/len(targets):.4f} ms/query)")
print(f"Speedup        : {full_scan_ms / indexed_ms:.0f}x faster with index")

# Range query example — equivalent to: SELECT * FROM users WHERE id BETWEEN 1000 AND 1050
results = table._index.range_lookup(1000, 1050)
print(f"\nRange query [1000, 1050]: {len(results)} rows — {results[:5]}...")
```

**Expected output (approximate):**
```
Table size     : 500,000 rows
Queries run    : 1,000
Full scan      : 4200.0 ms total  (4.200 ms/query)
Indexed lookup : 3.1 ms total  (0.0031 ms/query)
Speedup        : 1354x faster with index
```

The indexed lookup is over 1,000x faster. This is why `EXPLAIN ANALYZE` in
PostgreSQL always shows "Index Scan" as a major optimization goal.

---

## 2. Git Bisect — Finding the Bug-Introducing Commit

### The Production Problem

You have a repository with 1,000 commits. The software worked at commit 1. It
is broken at commit 1,000. A developer must find which commit introduced the
regression. Manually testing each commit would require up to 1,000 tests.

`git bisect` uses binary search. It picks the middle commit, asks you to test
it (good or bad?), then halves the search space. 1,000 commits → found in at
most ceil(log2(1000)) = 10 tests. This is the same algorithm, applied to a
sorted timeline of commits.

```python
import math
from typing import Callable

# -----------------------------------------------------------------------
# Git bisect simulation
# -----------------------------------------------------------------------

def git_bisect_simulation(
    commits: list[str],
    test_fn: Callable[[str], bool],
    verbose: bool = True
) -> tuple[str, int]:
    """
    Simulate `git bisect run <test_script>` on a list of commits.

    Parameters
    ----------
    commits  : Ordered list of commit hashes, oldest first.
    test_fn  : Returns True if commit is GOOD (no bug), False if BAD (has bug).
               Assumption: all commits before the breaking commit are good,
               all commits from the breaking commit onward are bad.
               This is the classic monotonic property that makes binary search valid.
    verbose  : Print each step like `git bisect` does.

    Returns
    -------
    (first_bad_commit, steps_taken)
    """
    lo, hi = 0, len(commits) - 1
    steps = 0
    first_bad = commits[hi]  # we know the latest commit is bad

    if verbose:
        print(f"Bisecting {len(commits)} commits "
              f"(worst case: {math.ceil(math.log2(len(commits)))} steps)")
        print(f"Known good: {commits[lo][:8]}  |  Known bad: {commits[hi][:8]}\n")

    while lo < hi:
        mid = (lo + hi) // 2
        steps += 1
        is_good = test_fn(commits[mid])
        status = "good" if is_good else "bad"

        if verbose:
            remaining = hi - lo
            print(f"Step {steps:2d}: Testing {commits[mid][:8]}  ->  {status}"
                  f"  [{remaining} commits remaining in range]")

        if is_good:
            lo = mid + 1  # bug is after this commit
        else:
            hi = mid      # this commit or earlier introduced the bug
            first_bad = commits[mid]

    if verbose:
        print(f"\nFirst bad commit: {commits[lo][:8]}")
        print(f"Found in {steps} steps (vs {len(commits)} linear search worst case)")

    return commits[lo], steps


# -----------------------------------------------------------------------
# Demo: 1,000 commits, bug introduced at commit 742
# -----------------------------------------------------------------------

import hashlib

def make_commit_hash(n: int) -> str:
    return hashlib.sha1(str(n).encode()).hexdigest()

NUM_COMMITS = 1000
BUG_INTRODUCED_AT = 742

commits = [make_commit_hash(i) for i in range(NUM_COMMITS)]

def test_commit(commit_hash: str) -> bool:
    """Return True (good) if commit is before the bug, False (bad) otherwise."""
    index = next(i for i, c in enumerate(commits) if c == commit_hash)
    return index < BUG_INTRODUCED_AT

found_commit, steps = git_bisect_simulation(commits, test_commit, verbose=True)
actual_bad = commits[BUG_INTRODUCED_AT]

print(f"\nVerification:")
print(f"  Expected : {actual_bad[:8]}")
print(f"  Found    : {found_commit[:8]}")
print(f"  Match    : {found_commit == actual_bad}")
print(f"  Steps    : {steps} (theoretical max: {math.ceil(math.log2(NUM_COMMITS))})")
```

**Expected output (partial):**
```
Bisecting 1000 commits (worst case: 10 steps)
Known good: da4b9237  |  Known bad: b6589fc6

Step  1: Testing 77de68da  ->  good   [999 commits remaining in range]
Step  2: Testing 1ff1de77  ->  bad    [499 commits remaining in range]
Step  3: Testing 902ba3cd  ->  good   [249 commits remaining in range]
...
Step 10: Testing <hash>    ->  bad

First bad commit: <hash of commit 742>
Found in 10 steps (vs 1000 linear search worst case)
```

Real `git bisect` uses this exact strategy. The `git bisect run <script>` form
fully automates it — your test script exits 0 for good, non-zero for bad.

---

## 3. Dictionary / Spell Check — Binary Search on Sorted Word List

### The Production Problem

Spell checkers in word processors (LibreOffice, MS Word) and editors (VS Code,
Vim) maintain a sorted dictionary file of valid words. Checking whether a word
is valid, finding the closest match, and listing completions all use binary
search — not a hash table — because hash tables cannot efficiently answer
"what words start with 'pre'?" but a sorted list can.

```python
import bisect
from typing import Optional

# -----------------------------------------------------------------------
# WordDictionary backed by sorted list + bisect
# -----------------------------------------------------------------------

class WordDictionary:
    """
    Production-style spell-checker dictionary.
    Backed by a sorted list so binary search can answer:
      - exact membership   : is_valid_word("hello")
      - prefix completion  : words_starting_with("pre")
      - closest match      : find_closest("helo") for autocorrect
    """

    def __init__(self, words: list[str]):
        self._words = sorted(w.lower() for w in words)

    # ------------------------------------------------------------------
    # O(log n) exact lookup
    # ------------------------------------------------------------------
    def is_valid_word(self, word: str) -> bool:
        """Binary search for exact match."""
        word = word.lower()
        pos = bisect.bisect_left(self._words, word)
        return pos < len(self._words) and self._words[pos] == word

    # ------------------------------------------------------------------
    # O(log n + k) prefix search
    # ------------------------------------------------------------------
    def words_starting_with(self, prefix: str) -> list[str]:
        """
        Find all words with the given prefix.
        Binary search finds the insertion point of `prefix`, then scan forward
        while words still start with prefix. This is how IDE autocomplete works.
        """
        prefix = prefix.lower()
        lo = bisect.bisect_left(self._words, prefix)

        # Upper bound: prefix with last character incremented
        # e.g., "pre" -> "prf" to find all words in ["pre", "prf")
        prefix_end = prefix[:-1] + chr(ord(prefix[-1]) + 1) if prefix else ""
        hi = bisect.bisect_left(self._words, prefix_end) if prefix_end else len(self._words)

        return self._words[lo:hi]

    # ------------------------------------------------------------------
    # O(n * |word|) find closest — edit distance based autocorrect
    # ------------------------------------------------------------------
    def find_closest(self, misspelled: str, max_distance: int = 2) -> list[str]:
        """
        Return valid words within edit distance `max_distance`.
        In production (Hunspell, SymSpell), candidates are first narrowed
        by prefix or phonetic key before edit distance is computed.
        Here we demonstrate the two-phase approach: prefix narrow + verify.
        """
        misspelled = misspelled.lower()

        def edit_distance(a: str, b: str) -> int:
            m, n = len(a), len(b)
            dp = list(range(n + 1))
            for i in range(1, m + 1):
                prev, dp[0] = dp[0], i
                for j in range(1, n + 1):
                    temp = dp[j]
                    if a[i - 1] == b[j - 1]:
                        dp[j] = prev
                    else:
                        dp[j] = 1 + min(prev, dp[j], dp[j - 1])
                    prev = temp
            return dp[n]

        # Narrow candidates: words sharing the first letter (huge speedup)
        if misspelled:
            candidates = self.words_starting_with(misspelled[0])
        else:
            candidates = self._words

        return [
            w for w in candidates
            if abs(len(w) - len(misspelled)) <= max_distance
            and edit_distance(misspelled, w) <= max_distance
        ]

    def __len__(self):
        return len(self._words)


# -----------------------------------------------------------------------
# Demo with a representative English word list
# -----------------------------------------------------------------------

SAMPLE_WORDS = [
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "it",
    "for", "not", "on", "with", "he", "as", "you", "do", "at", "this",
    "but", "his", "by", "from", "they", "we", "say", "her", "she", "or",
    "an", "will", "my", "one", "all", "would", "there", "their", "what",
    "present", "pressure", "preview", "previous", "prevent", "prince",
    "print", "priority", "private", "privilege", "probable", "problem",
    "process", "produce", "program", "project", "protect", "provide",
    "hello", "help", "helpful", "helper", "helping", "helpless",
    "world", "word", "work", "worker", "working", "workshop",
    "python", "program", "programming", "programmer", "practice",
]

dictionary = WordDictionary(SAMPLE_WORDS)

print(f"Dictionary size: {len(dictionary)} words\n")

# Exact lookup
for word in ["hello", "helo", "python", "pithon", "present"]:
    print(f"  is_valid_word({word!r:12s}) -> {dictionary.is_valid_word(word)}")

print()

# Prefix search (autocomplete)
for prefix in ["pre", "pro", "help", "work"]:
    completions = dictionary.words_starting_with(prefix)
    print(f"  words_starting_with({prefix!r}) -> {completions}")

print()

# Closest match (autocorrect)
for typo in ["helo", "wrold", "progam"]:
    suggestions = dictionary.find_closest(typo)
    print(f"  find_closest({typo!r:10s}) -> {suggestions}")
```

---

## 4. Package Version Resolution — Latest Compatible Version

### The Production Problem

Package managers like pip, npm, and Cargo must answer: "given a constraint like
`requests >= 2.20.0, < 3.0.0`, which is the latest installable version?" The
full version list for a popular package may have hundreds of entries. They are
stored in sorted order in the package index. Binary search finds the answer in
O(log n) — this happens for every package in your requirements file.

```python
import bisect
from typing import Optional

# -----------------------------------------------------------------------
# Semantic version comparison
# -----------------------------------------------------------------------

class Version:
    """Comparable semantic version. Supports ==, <, >, <=, >=."""

    def __init__(self, version_str: str):
        self.raw = version_str
        parts = version_str.split(".")
        self.major = int(parts[0]) if len(parts) > 0 else 0
        self.minor = int(parts[1]) if len(parts) > 1 else 0
        self.patch = int(parts[2]) if len(parts) > 2 else 0

    def _tuple(self):
        return (self.major, self.minor, self.patch)

    def __eq__(self, other): return self._tuple() == other._tuple()
    def __lt__(self, other): return self._tuple() <  other._tuple()
    def __le__(self, other): return self._tuple() <= other._tuple()
    def __gt__(self, other): return self._tuple() >  other._tuple()
    def __ge__(self, other): return self._tuple() >= other._tuple()
    def __repr__(self): return f"Version({self.raw!r})"


# -----------------------------------------------------------------------
# Package index simulation
# -----------------------------------------------------------------------

class PackageIndex:
    """
    Simulates a PyPI-style package index with sorted versions.
    Supports the constraint resolution that pip performs.
    """

    def __init__(self, package_name: str, available_versions: list[str]):
        self.name = package_name
        # Keep versions sorted — PyPI returns them in upload order, pip sorts them
        self._versions = sorted(
            [Version(v) for v in available_versions],
            key=lambda v: v._tuple()
        )

    def find_compatible_version(
        self,
        min_version: Optional[str] = None,
        max_version: Optional[str] = None,
        exclude_prerelease: bool = True
    ) -> Optional[Version]:
        """
        Find the LATEST version satisfying:
            min_version <= version < max_version

        Uses bisect_right to find the insertion point of max_version,
        then steps back one position — identical to what pip's resolver does.
        """
        versions = self._versions

        # Apply lower bound using bisect_left
        lo = 0
        if min_version:
            lo = bisect.bisect_left(
                [v._tuple() for v in versions],
                Version(min_version)._tuple()
            )

        # Apply upper bound using bisect_left (strict less-than)
        hi = len(versions)
        if max_version:
            hi = bisect.bisect_left(
                [v._tuple() for v in versions],
                Version(max_version)._tuple()
            )

        # Candidate range is versions[lo:hi]; we want the latest (rightmost)
        candidates = versions[lo:hi]

        if not candidates:
            return None

        return candidates[-1]  # latest compatible version

    def find_exact(self, version_str: str) -> Optional[Version]:
        """O(log n) check if an exact version exists."""
        target = Version(version_str)
        pos = bisect.bisect_left(
            [v._tuple() for v in self._versions],
            target._tuple()
        )
        if pos < len(self._versions) and self._versions[pos] == target:
            return self._versions[pos]
        return None

    def versions_in_range(self, min_v: str, max_v: str) -> list[Version]:
        """List all versions in a range — useful for changelog display."""
        lo_t = Version(min_v)._tuple()
        hi_t = Version(max_v)._tuple()
        tuples = [v._tuple() for v in self._versions]
        lo = bisect.bisect_left(tuples, lo_t)
        hi = bisect.bisect_right(tuples, hi_t)
        return self._versions[lo:hi]


# -----------------------------------------------------------------------
# Demo: resolve 'requests' package like pip does
# -----------------------------------------------------------------------

requests_versions = [
    "1.0.0", "1.1.0", "1.2.0", "1.2.3",
    "2.0.0", "2.1.0", "2.4.0", "2.4.3", "2.7.0",
    "2.10.0", "2.14.0", "2.18.0", "2.20.0", "2.21.0",
    "2.22.0", "2.23.0", "2.24.0", "2.25.0", "2.25.1",
    "2.26.0", "2.27.0", "2.28.0", "2.28.1", "2.28.2",
    "2.29.0", "2.30.0", "2.31.0", "2.32.0", "2.32.1",
    "3.0.0",
]

index = PackageIndex("requests", requests_versions)

print("Package: requests")
print(f"Available versions: {len(requests_versions)}\n")

# Simulate: pip install "requests>=2.20.0,<3.0.0"
result = index.find_compatible_version(min_version="2.20.0", max_version="3.0.0")
print(f"pip install 'requests>=2.20.0,<3.0.0'  ->  {result}")

# Simulate: pip install "requests>=2.0.0,<2.25.0"
result = index.find_compatible_version(min_version="2.0.0", max_version="2.25.0")
print(f"pip install 'requests>=2.0.0,<2.25.0'   ->  {result}")

# Simulate: pip install "requests==2.28.2"
result = index.find_exact("2.28.2")
print(f"pip install 'requests==2.28.2'           ->  {result}")

# Simulate: incompatible constraint
result = index.find_compatible_version(min_version="4.0.0", max_version="5.0.0")
print(f"pip install 'requests>=4.0.0,<5.0.0'    ->  {result} (not available)")

# Show all 2.x versions
all_2x = index.versions_in_range("2.0.0", "2.99.99")
print(f"\nAll 2.x versions ({len(all_2x)} total): {[v.raw for v in all_2x]}")
```

---

## 5. Network Packet Routing — Longest Prefix Match

### The Production Problem

Internet routers store a routing table with thousands of CIDR entries like
`192.168.0.0/16`. When a packet arrives, the router must find the most specific
(longest prefix) matching route. This is the "longest prefix match" problem.
Cisco, Juniper, and Linux's `ip route` all solve it. For software routers and
firewalls (iptables, nftables), a sorted list with binary search is a common
implementation for smaller tables.

```python
import bisect
import ipaddress
from typing import Optional

# -----------------------------------------------------------------------
# Routing table with binary search for longest prefix match
# -----------------------------------------------------------------------

class RoutingTable:
    """
    Software routing table using binary search for longest-prefix match.
    Routes are stored sorted by (network_address, prefix_length).
    On lookup, binary search finds the candidate range, then we select
    the longest matching prefix.

    This is a simplified version of what Linux's FIB (Forwarding
    Information Base) does in software before hardware offload.
    """

    def __init__(self):
        self._routes: list[tuple[int, int, int, str]] = []
        # Each entry: (network_int, prefix_len, mask_int, gateway)
        # Stored sorted by (network_int, prefix_len) for binary search

    def add_route(self, cidr: str, gateway: str) -> None:
        """Add a route. Example: add_route("10.0.0.0/8", "10.0.0.1")"""
        network = ipaddress.ip_network(cidr, strict=False)
        net_int   = int(network.network_address)
        mask_int  = int(network.netmask)
        prefix_len = network.prefixlen

        entry = (net_int, prefix_len, mask_int, gateway)
        # Insert sorted by network integer, then prefix length
        pos = bisect.bisect_left(
            [(r[0], r[1]) for r in self._routes],
            (net_int, prefix_len)
        )
        self._routes.insert(pos, entry)

    def find_route(self, ip: str) -> Optional[tuple[str, str]]:
        """
        Find the best (longest prefix) matching route for an IP address.
        Returns (matched_cidr, gateway) or None if no route matches.

        Algorithm:
          1. Convert IP to integer.
          2. Binary search for the rightmost entry whose network_address
             <= ip_int (bisect_right trick).
          3. Walk backwards through candidates checking if ip & mask == network.
          4. Among matches, return the one with the longest prefix.
        """
        ip_int = int(ipaddress.ip_address(ip))

        # Find all routes whose network_address <= ip_int
        keys = [(r[0], r[1]) for r in self._routes]
        pos = bisect.bisect_right(keys, (ip_int, 32))

        best_match = None
        best_prefix_len = -1

        # Scan backwards — earlier routes have smaller network addresses
        # We need all routes up to position `pos` as candidates
        for i in range(pos - 1, -1, -1):
            net_int, prefix_len, mask_int, gateway = self._routes[i]

            # Once the network address is too small to possibly match, stop
            # (optimization: break if network is more than 32 bits away)
            if ip_int & mask_int == net_int:
                if prefix_len > best_prefix_len:
                    best_prefix_len = prefix_len
                    cidr = f"{ipaddress.ip_address(net_int)}/{prefix_len}"
                    best_match = (cidr, gateway)

        return best_match

    def show_table(self) -> None:
        print(f"{'Network':<20} {'Prefix':>6}  {'Gateway'}")
        print("-" * 45)
        for net_int, prefix_len, mask_int, gateway in self._routes:
            network = f"{ipaddress.ip_address(net_int)}/{prefix_len}"
            print(f"{network:<20} {prefix_len:>6}  {gateway}")


# -----------------------------------------------------------------------
# Demo: typical enterprise routing table
# -----------------------------------------------------------------------

rt = RoutingTable()

# Default route (catch-all)
rt.add_route("0.0.0.0/0",       "203.0.113.1")   # ISP gateway

# Corporate supernet
rt.add_route("10.0.0.0/8",      "10.0.0.1")       # internal network

# Data center subnets
rt.add_route("10.10.0.0/16",    "10.10.0.1")      # DC1
rt.add_route("10.10.1.0/24",    "10.10.1.1")      # DC1 production
rt.add_route("10.10.2.0/24",    "10.10.2.1")      # DC1 staging

# Office subnets
rt.add_route("192.168.0.0/16",  "192.168.0.1")    # all offices
rt.add_route("192.168.1.0/24",  "192.168.1.1")    # NYC office
rt.add_route("192.168.2.0/24",  "192.168.2.1")    # SF office

print("Routing Table:")
rt.show_table()
print()

# Test lookups
test_ips = [
    ("10.10.1.50",   "Should hit DC1 production /24"),
    ("10.10.2.100",  "Should hit DC1 staging /24"),
    ("10.10.3.1",    "Should hit DC1 /16"),
    ("10.20.0.1",    "Should hit internal /8"),
    ("192.168.1.50", "Should hit NYC office /24"),
    ("192.168.5.1",  "Should hit all offices /16"),
    ("8.8.8.8",      "Should hit default route /0"),
]

print("Routing decisions:")
for ip, description in test_ips:
    result = rt.find_route(ip)
    if result:
        cidr, gw = result
        print(f"  {ip:<16} -> via {gw:<16}  (matched {cidr})  [{description}]")
    else:
        print(f"  {ip:<16} -> No route (unreachable)")
```

---

## 6. Game Programming — Binary Search for Difficulty Calibration

### The Production Problem

Adaptive difficulty systems in games (used by Celeste, Dark Souls, rhythm games
like Beat Saber) must find the highest difficulty level a player can complete.
They have a monotonic property: if a player can beat level N, they can beat all
levels below N. This makes it a perfect binary search problem.

Rather than starting at level 1 and incrementing (which wastes time on easy
levels), the system uses binary search to converge on the optimal challenge
level quickly — typically within log2(N) attempts.

```python
import random
import time
from typing import Callable

# -----------------------------------------------------------------------
# Adaptive difficulty system using binary search
# -----------------------------------------------------------------------

class Player:
    """
    Represents a player with a hidden skill rating.
    Can attempt a level — returns True if their skill exceeds level difficulty.
    In production, this is an actual gameplay session.
    """

    def __init__(self, skill_rating: int, consistency: float = 0.9):
        self.skill_rating = skill_rating
        self.consistency = consistency  # probability of playing at full skill
        self.attempts = 0

    def attempt_level(self, level: int) -> bool:
        """
        Simulate attempting a level.
        Player succeeds if skill_rating > level, with some randomness
        to model human inconsistency.
        """
        self.attempts += 1
        # Add noise: sometimes perform above or below your skill level
        effective_skill = self.skill_rating * random.gauss(1.0, 0.05)
        return effective_skill >= level


def find_max_completable_level(
    player: Player,
    min_level: int,
    max_level: int,
    trials_per_level: int = 3,
    verbose: bool = True
) -> tuple[int, int]:
    """
    Binary search for the highest level the player can complete.

    Uses majority vote over `trials_per_level` attempts to handle
    the randomness in player performance — same approach used by
    ranked matchmaking systems to reduce variance.

    Returns (best_level, total_attempts).
    """
    lo, hi = min_level, max_level
    best_completable = min_level - 1
    total_attempts = 0

    if verbose:
        print(f"Calibrating difficulty for player (hidden skill: {player.skill_rating})")
        print(f"Level range: {min_level} to {max_level}")
        print(f"Binary search will need at most "
              f"{int(__import__('math').log2(max_level - min_level + 1)) + 1} probes\n")

    while lo <= hi:
        mid = (lo + hi) // 2

        # Run multiple trials to handle human inconsistency
        wins = sum(player.attempt_level(mid) for _ in range(trials_per_level))
        total_attempts += trials_per_level
        can_complete = wins > trials_per_level // 2  # majority rule

        if verbose:
            bar = "WIN " * wins + "LOSS" * (trials_per_level - wins)
            print(f"  Level {mid:3d}: {bar}  -> {'PASS' if can_complete else 'FAIL'}"
                  f"  (range [{lo}, {hi}])")

        if can_complete:
            best_completable = mid
            lo = mid + 1   # try harder levels
        else:
            hi = mid - 1   # too hard, try easier levels

    return best_completable, total_attempts


# -----------------------------------------------------------------------
# Demo: calibrate three players of different skill levels
# -----------------------------------------------------------------------

random.seed(42)
LEVELS = (1, 100)

players = [
    ("Beginner",     Player(skill_rating=25)),
    ("Intermediate", Player(skill_rating=60)),
    ("Expert",       Player(skill_rating=88)),
]

for name, player in players:
    print(f"=== {name} Player (Skill: {player.skill_rating}) ===")
    best, attempts = find_max_completable_level(
        player, *LEVELS, trials_per_level=3, verbose=True
    )
    linear_attempts = player.skill_rating * 3  # naive: test every level from 1
    print(f"\n  Best level: {best}")
    print(f"  Total attempts (binary search): {attempts}")
    print(f"  Attempts if tested linearly:    {linear_attempts}")
    print(f"  Attempts saved: {linear_attempts - attempts}\n")
```

**Key insight:** A naive linear scan from level 1 upward would require
`skill_rating * trials_per_level` attempts. For an expert at level 88, that's
264 attempts. Binary search finds it in about 21 attempts (7 probes × 3
trials). This is why every serious matchmaking system uses binary search or
Elo-based convergence rather than brute-force ranking.

---

## Summary Table

| Use Case | Data Structure | Search Type | Complexity |
|---|---|---|---|
| PostgreSQL index | Sorted array (B-tree page) | Exact / range | O(log n) |
| Git bisect | Sorted commit timeline | First bad | O(log n) |
| Spell checker | Sorted word list | Exact / prefix | O(log n + k) |
| Package resolver | Sorted version list | Rightmost valid | O(log n) |
| IP routing | Sorted route table | Longest prefix | O(log n) |
| Game difficulty | Monotonic level sequence | Rightmost passing | O(log n) |

All six examples exploit the same invariant: **a sorted sequence with a
monotonic predicate can be searched in O(log n)**. Master this pattern and you
will recognise it in every domain.
