# Interview Master Cheatsheet — Ultimate 1-Page Reference

---

## Algorithm Pattern Decision Tree

```
Is the input SORTED or can it be sorted?
├── YES → Binary Search, Two Pointers, Sliding Window
└── NO  →
    Is it a TREE or GRAPH?
    ├── Tree  → DFS (recursion), BFS (level order), DP on tree
    └── Graph →
        Has weights? → YES: Dijkstra / Bellman-Ford
                       NO:  BFS (shortest path) / DFS (connectivity)
    Is there OPTIMAL SUBSTRUCTURE?
    ├── YES → DP (overlapping) or Greedy (local optimal = global)
    └── NO  →
        Need ALL combinations/permutations?
        ├── YES → Backtracking
        └── NO  → Two Pointers / Sliding Window / Hash Map
```

---

## Data Structure Selection Guide

| Problem Characteristic                       | Best Data Structure         |
|----------------------------------------------|-----------------------------|
| Fast lookup by key                           | Hash Map / Set              |
| Need min or max quickly                      | Heap (heapq)                |
| Need both min and max                        | Two heaps                   |
| FIFO ordering                                | Queue (deque)               |
| LIFO / matching brackets / backtracking      | Stack                       |
| Sorted order + fast insert/delete            | Sorted List (sortedcontainers) |
| Range queries + updates                      | Segment Tree / BIT          |
| Connected components / cycle detection       | DSU (Union-Find)            |
| Prefix string matching                       | Trie                        |
| Sliding window of K elements                 | Monotonic deque             |
| Frequency counting                           | Counter / defaultdict       |
| LRU / ordered access                         | OrderedDict                 |
| Top K frequent elements                      | Min-heap of size K          |

---

## Time Complexity Requirements

| Constraint (n)    | Required Complexity    | Typical Algorithms                     |
|-------------------|------------------------|----------------------------------------|
| n ≤ 10            | O(n!) or O(2^n)        | Brute force, all permutations          |
| n ≤ 20            | O(2^n)                 | Bitmask DP, backtracking with pruning  |
| n ≤ 100           | O(n^3)                 | Floyd-Warshall, interval DP            |
| n ≤ 1,000         | O(n^2)                 | Nested loops, O(n^2) DP                |
| n ≤ 10,000        | O(n^2) borderline      | Be careful; optimize if TLE            |
| n ≤ 100,000       | O(n log n)             | Sorting, heaps, segment tree           |
| n ≤ 1,000,000     | O(n) or O(n log n)     | Linear scan, two pointers, hash map    |
| n ≤ 10^9          | O(log n) or O(sqrt(n)) | Binary search, math                    |

---

## Core Pattern One-Liners

| Pattern           | When to Use                                                    |
|-------------------|----------------------------------------------------------------|
| Two Pointers      | Sorted array, pair sum, palindrome, container with most water  |
| Sliding Window    | Subarray/substring with constraint (fixed or variable size)    |
| Binary Search     | Sorted input, "find minimum X that satisfies condition"        |
| BFS               | Shortest path (unweighted), level-order, minimum steps         |
| DFS               | All paths, connectivity, cycle, topo sort, tree traversal      |
| Backtracking      | Generate all subsets/permutations/combinations, constraint search |
| Dynamic Programming | Overlapping subproblems, optimization over choices            |
| Greedy            | Local optimal = global optimal, interval scheduling, Huffman   |
| Graph algorithms  | Connectivity, shortest path, MST, SCC                          |
| Monotonic Stack   | Next greater/smaller element, span, histogram                  |
| Union-Find        | Connected components, cycle detection, merging groups          |
| Trie              | Prefix search, autocomplete, word dictionary                   |
| Heap/Priority Q   | K-th element, merge K lists, running median                    |
| Segment Tree/BIT  | Range query + point/range update                               |

---

## Python Standard Library Cheat Sheet

```python
# heapq — min-heap
import heapq
heapq.heapify(lst)                   # convert list to heap in-place O(n)
heapq.heappush(heap, item)           # O(log n)
heapq.heappop(heap)                  # O(log n)
heapq.nlargest(k, iterable)          # O(n log k)
heapq.nsmallest(k, iterable)         # O(n log k)
heapq.heappushpop(heap, item)        # push then pop — more efficient
# Max-heap: negate values (-val, item)

# collections.deque — O(1) append/pop from both ends
from collections import deque
dq = deque(maxlen=k)                 # auto-evict old elements
dq.appendleft(x); dq.append(x)
dq.popleft(); dq.pop()
dq.rotate(k)                         # rotate right by k

# Counter
from collections import Counter
c = Counter("aabbcc")                # {'a':2,'b':2,'c':2}
c.most_common(k)                     # k most frequent elements
c1 + c2; c1 - c2; c1 & c2; c1 | c2 # set-like operations

# defaultdict
from collections import defaultdict
d = defaultdict(list)                # d[key] auto-creates []
d = defaultdict(int)                 # d[key] auto-creates 0
d = defaultdict(set)

# OrderedDict
from collections import OrderedDict
od = OrderedDict()
od.move_to_end(key, last=True)       # move to back (most recent)
od.popitem(last=False)               # pop from front (least recent)

# bisect — binary search on sorted list
import bisect
bisect.bisect_left(lst, x)           # leftmost insertion point for x
bisect.bisect_right(lst, x)          # rightmost insertion point
bisect.insort(lst, x)                # insert maintaining sorted order

# math
import math
math.inf                             # float('inf')
math.gcd(a, b)                       # greatest common divisor
math.lcm(a, b)                       # least common multiple (3.9+)
math.comb(n, k)                      # C(n,k) combinations
math.perm(n, k)                      # P(n,k) permutations
math.floor(x); math.ceil(x)
math.log(x, base)                    # log base; math.log2(x), math.log10(x)

# itertools
import itertools
itertools.combinations(lst, r)       # C(n,r), no repetition
itertools.permutations(lst, r)       # P(n,r)
itertools.combinations_with_replacement(lst, r)
itertools.product(lst, repeat=2)     # cartesian product
itertools.accumulate(lst)            # prefix sums
itertools.groupby(lst, key)          # group consecutive equal elements

# functools
from functools import lru_cache, cache
@lru_cache(maxsize=None)             # memoization decorator
@cache                               # simpler alias (Python 3.9+)

# sorted with key
sorted(lst, key=lambda x: x[1])
sorted(lst, key=lambda x: (-x[0], x[1]))  # multi-key sort

# string methods
s.split(), s.strip(), s.lower(), s.upper()
s.isdigit(), s.isalpha(), s.isalnum()
' '.join(lst)
ord('a') - ord('a')                  # 0
chr(ord('a') + k)                    # k-th letter from 'a'
```

---

## Interview Problem-Solving Framework (5 Steps)

```
1. UNDERSTAND (2-3 min)
   - Repeat problem in your own words
   - Clarify: input types? constraints? edge cases?
   - Ask: sorted? duplicates? negative numbers? overflow?

2. EXAMPLES (2-3 min)
   - Walk through given examples manually
   - Create your own edge cases: empty input, single element, all same

3. APPROACH (3-5 min)
   - State brute force first (even if O(n^2) or O(2^n))
   - Identify bottleneck; think aloud about optimization
   - Choose pattern; explain time/space complexity before coding

4. CODE (15-20 min)
   - Write clean, modular code — name variables clearly
   - Handle edge cases inline as you code
   - Talk through logic as you write

5. TEST & OPTIMIZE (5 min)
   - Trace through your example manually
   - Test edge cases: [], [1], all same, max constraints
   - Discuss: can we do better in space? time?
```

---

## Big-O Cheat Sheet

| Operation                          | Complexity    |
|------------------------------------|---------------|
| Array access                       | O(1)          |
| Array append (amortized)           | O(1)          |
| Array insert/delete (middle)       | O(n)          |
| Hash map get/set/delete            | O(1) avg      |
| Set add/lookup/remove              | O(1) avg      |
| Heap push/pop                      | O(log n)      |
| Heap build                         | O(n)          |
| BST search/insert/delete (balanced)| O(log n)      |
| Sorting (comparison)               | O(n log n)    |
| Counting sort / radix sort         | O(n+k)        |
| Binary search                      | O(log n)      |
| DFS / BFS                          | O(V+E)        |
| Dijkstra                           | O((V+E) log V)|
| String compare / hashing          | O(L) — L=length|

---

## Top 30 Most-Asked Patterns (Ranked by Frequency)

| Rank | Pattern                          | Representative Problems                        |
|------|----------------------------------|------------------------------------------------|
| 1    | Two Pointers                     | Two Sum (sorted), Container, Palindrome        |
| 2    | Sliding Window                   | Longest substring, Max sum subarray            |
| 3    | DFS / Tree Traversal             | Max depth, path sum, validate BST              |
| 4    | BFS / Level Order                | Shortest path, level order traversal           |
| 5    | Dynamic Programming (1D)         | Climbing stairs, house robber, coin change     |
| 6    | Binary Search                    | Search rotated, find peak, kth smallest        |
| 7    | Hash Map / Two Sum               | Two sum, group anagrams, subarray sum          |
| 8    | Backtracking                     | Subsets, permutations, N-queens, word search   |
| 9    | Merge Intervals                  | Merge intervals, meeting rooms, insert interval|
| 10   | Stack (monotonic)                | Next greater element, daily temperatures       |
| 11   | Heap / Top K                     | Kth largest, K closest, top K frequent         |
| 12   | Graph BFS/DFS                    | Number of islands, clone graph, word ladder    |
| 13   | Dynamic Programming (2D)         | LCS, edit distance, unique paths               |
| 14   | Fast & Slow Pointers             | Cycle detection, middle of list, happy number  |
| 15   | Prefix Sum                       | Range sum query, subarray sum equals k         |
| 16   | Greedy                           | Jump game, task scheduler, min platforms       |
| 17   | Trie                             | Word search II, implement trie, autocomplete   |
| 18   | Union-Find                       | Number of provinces, redundant connection      |
| 19   | Linked List Manipulation         | Reverse, merge K sorted, LRU cache             |
| 20   | Knapsack DP                      | 0/1 knapsack, partition equal subset, coin change |
| 21   | Topological Sort                 | Course schedule, alien dictionary              |
| 22   | Binary Tree DP                   | Diameter, max path sum, binary tree cameras    |
| 23   | Bit Manipulation                 | Single number, missing number, counting bits   |
| 24   | Matrix BFS/DFS                   | Rotting oranges, 01 matrix, walls and gates    |
| 25   | String DP                        | Longest palindromic substring, regex matching  |
| 26   | Divide and Conquer               | Merge sort, quickselect, Kth largest stream    |
| 27   | Segment Tree / BIT               | Range sum query mutable, count of smaller      |
| 28   | Dijkstra / Shortest Path         | Network delay time, cheapest flights           |
| 29   | Interval DP                      | Burst balloons, strange printer, palindrome partition |
| 30   | Bitmask DP                       | TSP, minimum XOR sum, assignment problems      |

---

## Common Gotchas & Red Flags

```
- Integer overflow: Python handles natively; Java/C++ use long
- Empty input: always check len(arr) == 0 or not arr
- Single element: dp[0] = base_case — don't index dp[-1]
- Off-by-one: sliding window [l, r] — size is r - l + 1
- Cycle in linked list: Floyd's fast/slow pointer
- DFS stack overflow: use iterative DFS or sys.setrecursionlimit(10**6)
- Modular arithmetic: (a * b) % MOD != (a % MOD) * b — always mod both
- Negative modulo: (-1) % n = n-1 in Python (correct), may differ in other langs
- 0-indexed vs 1-indexed DP: dp[i] = result for arr[i-1] — common source of bugs
- Mutable default args: def fn(memo={}): — BUG: shared across calls; use None+init
```
