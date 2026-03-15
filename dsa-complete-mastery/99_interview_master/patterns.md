# Interview Pattern Recognition — The Master Guide

> "You cannot solve what you cannot name. Name the pattern, and the solution follows."

This is the complete pattern recognition guide. Its purpose is not to teach you algorithms from scratch — that is what the individual topic files are for. Its purpose is to answer the question you face every interview: "I see this problem. What do I reach for?"

Pattern recognition is the meta-skill that separates engineers who can solve problems they have seen before from those who can solve problems they have never seen before. It is built through two things: exposure to many problem types, and deliberate practice at recognizing their fingerprints.

This guide catalogs those fingerprints. For every major pattern, you will find the signals that announce it, the reasoning behind why it works, a full code template, worked examples, and common mistakes. No fluff. Everything you need.

---

## Table of Contents

1. Section 1 — Input Array Problems
2. Section 2 — String Problems
3. Section 3 — Tree and Graph Problems
4. Section 4 — Optimization Problems
5. Section 5 — Complexity and Space Signals
6. Section 6 — Classic Problem-to-Pattern Mapping Table (40+ problems)
7. Section 7 — Interview-Specific Tips

---

## Section 1: Input Array Problems

Arrays are the most common input type in interviews. The pattern you reach for depends on a few key questions: Is the array sorted? Are you looking for a pair, a subarray, or an element? Do you need all results or just one?

---

### Pattern 1.1 — Sorted Array → Binary Search

**The fingerprint:** The array is sorted (or can be sorted). You are asked to find a specific value, count elements meeting a condition, or determine the minimum/maximum value that satisfies some property.

**Why it works:** A sorted array has a monotone structure. Binary search exploits monotonicity to eliminate half the search space with each comparison. O(log n) instead of O(n).

**Signals in the problem text:**
- "Sorted array"
- "Find index of target"
- "Find minimum speed / capacity such that..."
- "Find first / last position of..."
- Answer is on a numeric range and the condition is monotone

**Template:**

```python
def binary_search(nums, target):
    """Exact match search. O(log n)."""
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (right - left) // 2  # safe midpoint (avoids overflow)

        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


def find_first_occurrence(nums, target):
    """
    Find the FIRST index where nums[i] == target.
    When match found, keep searching left half.
    """
    left, right = 0, len(nums) - 1
    result = -1

    while left <= right:
        mid = left + (right - left) // 2

        if nums[mid] == target:
            result = mid       # record, but keep searching left
            right = mid - 1
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return result


def find_last_occurrence(nums, target):
    """Find the LAST index where nums[i] == target."""
    left, right = 0, len(nums) - 1
    result = -1

    while left <= right:
        mid = left + (right - left) // 2

        if nums[mid] == target:
            result = mid       # record, but keep searching right
            left = mid + 1
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return result


def search_on_answer(lo, hi, is_feasible):
    """
    Binary search on the answer space.
    Use when: "find minimum X such that condition(X) is True"
    Requires: condition is False for X < answer, True for X >= answer (monotone)
    """
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if is_feasible(mid):
            hi = mid      # mid could be the answer, keep it
        else:
            lo = mid + 1  # mid too small, discard it

    return lo             # lo == hi == the minimum feasible value
```

**Example — Koko Eating Bananas:**

```python
import math

def min_eating_speed(piles, h):
    """
    Minimum speed k such that Koko can eat all piles in h hours.
    Binary search on speed from 1 to max(piles).
    """
    def can_finish(speed):
        return sum(math.ceil(p / speed) for p in piles) <= h

    return search_on_answer(1, max(piles), can_finish)
```

---

### Pattern 1.2 — Sorted Array + Find Pair → Two Pointers

**The fingerprint:** You have a sorted array and need to find a pair (or triplet, quadruplet) of elements satisfying some condition (usually a sum constraint). You want better than O(n²).

**Why it works:** With a sorted array, if your current sum is too small, you know moving the left pointer right will increase the sum (because you replace a smaller number with a larger one). If too big, moving the right pointer left will decrease it. This eliminates the need to check every pair.

**Signals:**
- "Sorted array" + "find two numbers that sum to target"
- "Two Sum II" (the sorted version)
- "Find a pair with minimum difference"
- "Container with most water"

**Template:**

```python
def two_pointers_sum(nums, target):
    """
    Two Sum II style: find pair summing to target in sorted array.
    O(n) time, O(1) space.
    """
    left, right = 0, len(nums) - 1

    while left < right:
        current_sum = nums[left] + nums[right]

        if current_sum == target:
            return [left + 1, right + 1]  # 1-indexed per Two Sum II
        elif current_sum < target:
            left += 1    # need bigger sum → move left pointer right
        else:
            right -= 1   # need smaller sum → move right pointer left

    return []


def three_sum(nums):
    """
    Find all unique triplets summing to zero.
    Sort first, then for each element, run Two Sum on remainder.
    O(n²) time, O(1) extra space.
    """
    nums.sort()
    result = []

    for i in range(len(nums) - 2):
        # Skip duplicates for the outer element
        if i > 0 and nums[i] == nums[i - 1]:
            continue

        left, right = i + 1, len(nums) - 1

        while left < right:
            total = nums[i] + nums[left] + nums[right]

            if total == 0:
                result.append([nums[i], nums[left], nums[right]])
                # Skip duplicates for inner elements
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1

    return result
```

---

### Pattern 1.3 — Unsorted Array, Find Pair → Hash Map

**The fingerprint:** Unsorted array. Find two elements satisfying a condition (e.g., sum to target, difference equals k). You want O(n) time.

**Why it works:** For each element x, you can compute what value y would complete the pair (e.g., y = target - x). Instead of searching for y linearly, store seen values in a hash map for O(1) lookup.

**Signals:**
- "Unsorted array" + "two sum"
- "Find two elements with difference k"
- "Count pairs with given sum"

```python
def two_sum_unsorted(nums, target):
    """
    Classic Two Sum: unsorted array, return indices of pair.
    O(n) time, O(n) space.
    """
    seen = {}  # value → index

    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i

    return []


def count_pairs_with_difference(nums, k):
    """Count pairs (i, j) where nums[j] - nums[i] == k and i < j."""
    count = 0
    seen = set()

    for num in nums:
        if num - k in seen:  # there exists a number that is k less than current
            count += 1
        if num + k in seen:  # there exists a number that is k more than current
            count += 1
        seen.add(num)

    return count // 2  # each pair counted twice
```

---

### Pattern 1.4 — "Longest/Shortest Subarray Where..." → Sliding Window

**The fingerprint:** You need the length (or content) of the longest or shortest contiguous subarray satisfying some condition. The condition must be something that can be maintained as the window expands or shrinks — usually related to counts, sums, or distinctness.

**Why it works:** Instead of checking all O(n²) subarrays, a window expands on the right and shrinks on the left. Each element enters and leaves the window at most once: O(n) total operations.

**Signals:**
- "Longest substring without..."
- "Shortest subarray with sum at least k"
- "Maximum fruits in two baskets" (at most 2 distinct)
- "Minimum window substring"

```python
def longest_subarray_with_at_most_k_distinct(arr, k):
    """
    Sliding window: variable size, maximize length.
    Condition: at most k distinct elements in window.
    """
    count = {}
    left = 0
    max_len = 0

    for right in range(len(arr)):
        # EXPAND: add arr[right] to window
        count[arr[right]] = count.get(arr[right], 0) + 1

        # SHRINK: while window is invalid (too many distinct)
        while len(count) > k:
            left_elem = arr[left]
            count[left_elem] -= 1
            if count[left_elem] == 0:
                del count[left_elem]
            left += 1

        # RECORD: window is now valid
        max_len = max(max_len, right - left + 1)

    return max_len


def minimum_window_substring(s, t):
    """
    Sliding window: variable size, minimize length.
    Condition: window contains all characters of t.
    """
    from collections import Counter

    need = Counter(t)
    have = {}
    formed = 0          # how many chars in `need` we have enough of
    required = len(need)
    left = 0
    min_len = float('inf')
    result = ""

    for right, char in enumerate(s):
        # EXPAND
        have[char] = have.get(char, 0) + 1
        if char in need and have[char] == need[char]:
            formed += 1

        # SHRINK: once we have a valid window, try to minimize it
        while formed == required:
            # Record current window
            if right - left + 1 < min_len:
                min_len = right - left + 1
                result = s[left:right+1]

            # Remove left character
            left_char = s[left]
            have[left_char] -= 1
            if left_char in need and have[left_char] < need[left_char]:
                formed -= 1
            left += 1

    return result
```

---

### Pattern 1.5 — "Subarray Sum Equals K" → Prefix Sum + Hash Map

**The fingerprint:** Find the number of contiguous subarrays with a sum equal to k. The key insight is NOT to use a sliding window here — sliding window fails when there are negative numbers. Use prefix sums instead.

**Why it works:** If prefix[j] - prefix[i] = k, then the subarray from i to j-1 has sum k. So for each prefix[j], you need to count how many previous prefix[i] values equal prefix[j] - k. A hash map gives O(1) lookup.

**Signals:**
- "Number of subarrays with sum equal to k"
- "Subarray sum divisible by k" (variant)
- "Count subarrays with equal 0s and 1s" (convert 0→-1, then sum=0)

```python
def subarray_sum_equals_k(nums, k):
    """
    Count subarrays with sum exactly k.
    O(n) time, O(n) space.
    Works with negative numbers (sliding window does not).
    """
    count = 0
    prefix_sum = 0
    prefix_counts = {0: 1}  # prefix sum 0 exists once (empty prefix)

    for num in nums:
        prefix_sum += num
        # We need prefix[j] - prefix[i] = k
        # i.e., prefix[i] = prefix[j] - k
        needed = prefix_sum - k
        count += prefix_counts.get(needed, 0)
        prefix_counts[prefix_sum] = prefix_counts.get(prefix_sum, 0) + 1

    return count


def contiguous_array_equal_0s_1s(nums):
    """
    Find the longest subarray with equal number of 0s and 1s.
    Convert: 0 → -1, then find longest subarray with sum = 0.
    """
    nums = [1 if x == 1 else -1 for x in nums]
    prefix_sum = 0
    first_seen = {0: -1}   # prefix sum → first index where we saw it
    max_len = 0

    for i, num in enumerate(nums):
        prefix_sum += num
        if prefix_sum in first_seen:
            max_len = max(max_len, i - first_seen[prefix_sum])
        else:
            first_seen[prefix_sum] = i

    return max_len
```

---

## Section 2: String Problems

String problems have their own ecosystem of patterns. The underlying data structure is often a frequency map (Counter or array of 26 letters), a two-pointer approach, or a specialized structure like KMP or Trie.

---

### Pattern 2.1 — Anagram / Permutation → Character Frequency Map

**The fingerprint:** Two strings, check if one is an anagram of the other. Or: find all anagram substrings. Or: check if string A is a permutation of string B.

**Why it works:** An anagram has exactly the same characters in the same quantities, just rearranged. A frequency map (character → count) captures this identity. Two strings are anagrams iff their frequency maps are equal.

**Signals:**
- "Anagram" or "permutation" in the problem
- "Is string A a rearrangement of string B?"
- "Find all anagram positions in string S"

```python
from collections import Counter


def is_anagram(s, t):
    """O(n) time, O(1) space (at most 26 letters)."""
    if len(s) != len(t):
        return False
    return Counter(s) == Counter(t)


def find_all_anagrams(s, p):
    """
    Find all starting indices in s where a substring is an anagram of p.
    Sliding window with fixed size = len(p).
    O(n) time using the "sliding counter" trick.
    """
    from collections import defaultdict

    result = []
    need = Counter(p)
    window = defaultdict(int)
    formed = 0
    required = len(need)   # number of distinct characters we need to match
    left = 0

    for right, char in enumerate(s):
        window[char] += 1
        if char in need and window[char] == need[char]:
            formed += 1

        # Window is exactly len(p) wide
        if right - left + 1 == len(p):
            if formed == required:
                result.append(left)

            # Shrink: remove left character
            left_char = s[left]
            if left_char in need and window[left_char] == need[left_char]:
                formed -= 1
            window[left_char] -= 1
            left += 1

    return result
```

---

### Pattern 2.2 — Palindrome → Two Pointers from Center

**The fingerprint:** Check if a string is a palindrome. Find the longest palindromic substring. Any problem where the "mirror" structure of a palindrome is key.

**Two approaches:**
1. Two pointers: expand from center. O(n²) worst case.
2. DP: dp[i][j] = is s[i..j] a palindrome. O(n²) time and space.
3. Manacher's algorithm: O(n) but complex. Usually not required.

```python
def is_palindrome(s):
    """Check if s is a palindrome. O(n), O(1) space."""
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True


def longest_palindromic_substring(s):
    """
    Expand from center technique.
    For each character (and each gap between characters), try to expand.
    O(n²) time, O(1) space.
    """
    def expand(l, r):
        while l >= 0 and r < len(s) and s[l] == s[r]:
            l -= 1
            r += 1
        return s[l+1:r]  # s[l] and s[r] failed, so back off by 1

    result = ""
    for i in range(len(s)):
        # Odd-length palindrome centered at i
        odd = expand(i, i)
        # Even-length palindrome centered between i and i+1
        even = expand(i, i + 1)
        result = max(result, odd, even, key=len)

    return result


def count_palindromic_substrings(s):
    """Count all palindromic substrings. O(n²)."""
    count = 0

    def expand_count(l, r):
        nonlocal count
        while l >= 0 and r < len(s) and s[l] == s[r]:
            count += 1
            l -= 1
            r += 1

    for i in range(len(s)):
        expand_count(i, i)      # odd length
        expand_count(i, i + 1)  # even length

    return count
```

---

### Pattern 2.3 — Multiple String Operations → Trie

**The fingerprint:** You have a set of words and need to support prefix queries ("autocomplete"), longest common prefix, or word existence checks efficiently.

**Why it works:** A Trie (prefix tree) stores words character by character. All words with the same prefix share the same path from the root. Lookups take O(m) where m is the word length — independent of the number of words.

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False


class Trie:
    """
    Prefix tree for string operations.
    Insert/Search/StartsWith: O(m) where m = word length.
    Space: O(total characters across all words).
    """

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def search(self, word):
        """Returns True if word exists in trie."""
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end

    def starts_with(self, prefix):
        """Returns True if any word starts with prefix."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True

    def autocomplete(self, prefix):
        """Return all words with given prefix."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        results = []
        self._dfs(node, prefix, results)
        return results

    def _dfs(self, node, current, results):
        if node.is_end:
            results.append(current)
        for char, child in node.children.items():
            self._dfs(child, current + char, results)
```

---

## Section 3: Tree and Graph Problems

Trees and graphs appear in a huge proportion of interview problems. The key decision: BFS or DFS? And if DFS, top-down or bottom-up?

---

### Pattern 3.1 — Any Path Problem on a Tree → DFS

**Rule:** Almost any problem involving paths on a binary tree uses DFS. The direction (top-down vs bottom-up) depends on what information flows:

- **Top-down:** parent passes information to children (e.g., remaining sum, current path)
- **Bottom-up:** children return information to parent (e.g., depths, subtree sums)

```python
# ── TOP-DOWN: Path Sum ────────────────────────────────────────────────────────
def has_path_sum(root, target):
    """Does any root-to-leaf path sum to target? Top-down DFS."""
    def dfs(node, remaining):
        if not node:
            return False
        remaining -= node.val
        if not node.left and not node.right:  # leaf
            return remaining == 0
        return dfs(node.left, remaining) or dfs(node.right, remaining)

    return dfs(root, target)


def path_sum_all_paths(root, target):
    """Find all root-to-leaf paths summing to target."""
    result = []

    def dfs(node, remaining, path):
        if not node:
            return
        path.append(node.val)
        remaining -= node.val
        if not node.left and not node.right and remaining == 0:
            result.append(path[:])  # copy of current path
        dfs(node.left, remaining, path)
        dfs(node.right, remaining, path)
        path.pop()  # backtrack

    dfs(root, target, [])
    return result


# ── BOTTOM-UP: Tree Diameter ──────────────────────────────────────────────────
def diameter_of_binary_tree(root):
    """Longest path between any two nodes. Bottom-up DFS."""
    max_diameter = [0]

    def dfs(node):
        if not node:
            return 0
        left = dfs(node.left)
        right = dfs(node.right)
        max_diameter[0] = max(max_diameter[0], left + right)
        return max(left, right) + 1

    dfs(root)
    return max_diameter[0]


# ── BOTTOM-UP: Check Balanced Tree ───────────────────────────────────────────
def is_balanced(root):
    """Is tree height-balanced? Bottom-up."""
    def dfs(node):
        """Returns height of subtree, or -1 if unbalanced."""
        if not node:
            return 0
        left = dfs(node.left)
        right = dfs(node.right)
        if left == -1 or right == -1 or abs(left - right) > 1:
            return -1
        return max(left, right) + 1

    return dfs(root) != -1
```

---

### Pattern 3.2 — Level-by-Level → BFS

**The fingerprint:** "Level order traversal", "print nodes at each depth", "right side view of tree", "minimum depth". Any problem where you process nodes layer by layer.

```python
from collections import deque


def level_order(root):
    """Return list of lists, one per level. O(n)."""
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        level = []

        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        result.append(level)

    return result


def right_side_view(root):
    """The last node visible at each level from the right."""
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        for i in range(level_size):
            node = queue.popleft()
            if i == level_size - 1:  # last node in level = rightmost
                result.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

    return result
```

---

### Pattern 3.3 — Shortest Path, Unweighted Graph → BFS

**The fingerprint:** Finding the minimum number of steps/edges/transformations between two states. The key word is "minimum" in an unweighted context.

**Why BFS is correct:** BFS visits nodes in order of increasing distance from the source. The FIRST time BFS reaches a node is guaranteed to be via the shortest path.

```python
def shortest_path_bfs(graph, start, end):
    """BFS shortest path in unweighted graph. O(V + E)."""
    if start == end:
        return 0

    queue = deque([(start, 0)])
    visited = {start}

    while queue:
        node, dist = queue.popleft()

        for neighbor in graph[node]:
            if neighbor == end:
                return dist + 1
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))

    return -1  # not reachable


def number_of_islands(grid):
    """
    Count disconnected groups of '1's.
    Classic DFS/BFS flood fill.
    O(rows × cols)
    """
    if not grid:
        return 0

    rows, cols = len(grid), len(grid[0])
    count = 0

    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != '1':
            return
        grid[r][c] = '0'  # mark as visited
        dfs(r+1, c); dfs(r-1, c); dfs(r, c+1); dfs(r, c-1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                dfs(r, c)
                count += 1

    return count
```

---

### Pattern 3.4 — Shortest Path, Weighted Graph → Dijkstra

**The fingerprint:** Shortest path where edges have different weights (all non-negative). Dijkstra's algorithm uses a min-heap to always process the node with the currently smallest known distance.

```python
import heapq


def dijkstra(graph, start, end):
    """
    Dijkstra's shortest path. O((V + E) log V).
    graph: adjacency list of (neighbor, weight) pairs.
    All weights must be non-negative.
    """
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    heap = [(0, start)]  # (distance, node)

    while heap:
        d, node = heapq.heappop(heap)

        if d > dist[node]:
            continue  # stale entry

        if node == end:
            return d

        for neighbor, weight in graph[node]:
            new_dist = dist[node] + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))

    return dist[end] if dist[end] != float('inf') else -1
```

---

### Pattern 3.5 — Connectivity / Union-Find

**The fingerprint:** "Are these two nodes connected?", "How many connected components?", "Detect cycle in undirected graph." Union-Find (Disjoint Set Union) handles these in near O(1) per operation.

```python
class UnionFind:
    """
    Union-Find with path compression and union by rank.
    Operations: O(α(n)) ≈ O(1) amortized per operation.
    """

    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.components = n

    def find(self, x):
        """Find root of x's component. Path compression."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x, y):
        """Merge components of x and y. Returns False if already connected."""
        px, py = self.find(x), self.find(y)
        if px == py:
            return False  # already in same component = cycle!

        # Union by rank
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        self.components -= 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)


def count_components(n, edges):
    """Count connected components using Union-Find."""
    uf = UnionFind(n)
    for u, v in edges:
        uf.union(u, v)
    return uf.components


def detect_cycle_undirected(n, edges):
    """Detect cycle in undirected graph. If union returns False, cycle exists."""
    uf = UnionFind(n)
    for u, v in edges:
        if not uf.union(u, v):
            return True  # u and v already connected = adding this edge creates cycle
    return False
```

---

### Pattern 3.6 — Topological Sort / Dependency Ordering

**The fingerprint:** "Course prerequisites", "build order", "task dependencies." You need to process nodes in an order where all dependencies come before dependents.

**Two algorithms:**
1. Kahn's (BFS): start with nodes of in-degree 0, process them, reduce in-degrees of neighbors. More intuitive. Also detects cycles (if result has fewer nodes than graph, there is a cycle).
2. DFS postorder: add nodes to result AFTER finishing their DFS. Reverse the result.

```python
from collections import deque, defaultdict


def topological_sort_kahn(n, prerequisites):
    """
    Topological sort using Kahn's algorithm (BFS).
    Also detects cycles: if result length < n, cycle exists.
    O(V + E).
    """
    graph = defaultdict(list)
    in_degree = [0] * n

    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    # Start with all nodes that have no prerequisites
    queue = deque([i for i in range(n) if in_degree[i] == 0])
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)

        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return result if len(result) == n else []  # empty = cycle


def can_finish_courses(num_courses, prerequisites):
    """Can all courses be finished? Detect cycle via topological sort."""
    return len(topological_sort_kahn(num_courses, prerequisites)) == num_courses
```

---

## Section 4: Optimization Problems

Optimization problems ask for the maximum or minimum of some value. The two dominant tools are Greedy and Dynamic Programming. Knowing which to reach for is a critical skill.

---

### Pattern 4.1 — Dynamic Programming

**The fingerprint:** Three conditions signal DP:
1. **Optimal substructure:** the optimal solution can be built from optimal solutions to subproblems.
2. **Overlapping subproblems:** the same subproblems appear again and again (unlike Divide and Conquer where subproblems are disjoint).
3. The problem asks: "minimum cost", "maximum value", "number of ways", "is it possible?"

**The recognition story:** Start with brute force recursion. Draw the recursion tree. If you see the same call appearing multiple times, that is the overlapping subproblems signal. Add memoization. Then, if needed, convert to bottom-up table.

```python
# ── COIN CHANGE (unbounded knapsack style) ────────────────────────────────────
def coin_change(coins, amount):
    """
    Minimum coins to make amount.
    dp[i] = minimum coins for amount i.
    """
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0

    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)

    return dp[amount] if dp[amount] != float('inf') else -1


# ── 0/1 KNAPSACK ──────────────────────────────────────────────────────────────
def knapsack_01(weights, values, capacity):
    """
    Maximum value fitting in bag of given capacity.
    Each item can be taken at most once.
    dp[i][w] = max value using first i items with capacity w.
    """
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(capacity + 1):
            # Option 1: don't take item i
            dp[i][w] = dp[i-1][w]
            # Option 2: take item i (if it fits)
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i][w], dp[i-1][w - weights[i-1]] + values[i-1])

    return dp[n][capacity]


# ── LONGEST INCREASING SUBSEQUENCE ───────────────────────────────────────────
def lis(nums):
    """
    Longest strictly increasing subsequence.
    dp[i] = length of LIS ending at index i.
    O(n²) time. (O(n log n) version uses binary search — see below)
    """
    if not nums:
        return 0

    dp = [1] * len(nums)

    for i in range(1, len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)

    return max(dp)


# ── WORD BREAK ────────────────────────────────────────────────────────────────
def word_break(s, word_dict):
    """
    Can s be segmented into words from word_dict?
    dp[i] = can we segment s[0:i]?
    """
    word_set = set(word_dict)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True  # empty string is always segmentable

    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break

    return dp[n]
```

---

### Pattern 4.2 — Greedy Algorithms

**The fingerprint:** Locally optimal choices lead to a globally optimal solution. Greedy works when you can PROVE that always making the best immediate choice never hurts the global solution.

**The proof technique (exchange argument):** Assume your greedy solution is NOT optimal. Show that you can swap any locally suboptimal choice for the greedy choice and the result cannot get worse. Therefore greedy is optimal.

**When greedy FAILS — a critical counterexample:**

```
Coin change with coins [1, 3, 4], target = 6.

Greedy (take largest coin first):
  Take 4 → remaining = 2
  Take 1 → remaining = 1
  Take 1 → remaining = 0
  Total coins: 3  (4 + 1 + 1)

Optimal (DP):
  Take 3 → remaining = 3
  Take 3 → remaining = 0
  Total coins: 2  (3 + 3)

Greedy gives the WRONG answer here.
Greedy works for standard US coins (1, 5, 10, 25) because of their
special structure (each coin is a multiple or factor of others).
For arbitrary coin sets, use DP.
```

```python
def jump_game_greedy(nums):
    """
    Can you reach the last index?
    Greedy: track the farthest reachable index.
    O(n) time.
    """
    max_reach = 0

    for i, jump in enumerate(nums):
        if i > max_reach:
            return False   # can't even reach position i
        max_reach = max(max_reach, i + jump)

    return True


def jump_game_ii_greedy(nums):
    """
    Minimum jumps to reach last index.
    Greedy: at each jump, choose the option that reaches farthest.
    """
    jumps = 0
    current_end = 0   # end of current jump's reach
    farthest = 0      # farthest reachable from current level

    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == current_end:
            jumps += 1
            current_end = farthest

    return jumps


def activity_selection(start_times, end_times):
    """
    Maximum number of non-overlapping activities.
    Greedy: sort by end time, always pick earliest-ending compatible activity.
    This is provably optimal via exchange argument.
    """
    activities = sorted(zip(start_times, end_times), key=lambda x: x[1])
    count = 0
    last_end = float('-inf')

    for start, end in activities:
        if start >= last_end:
            count += 1
            last_end = end

    return count
```

---

### Pattern 4.3 — "All Possible / Enumerate All" → Backtracking

**The fingerprint:** The problem asks for all combinations, all permutations, all subsets, all valid configurations. You need to enumerate every valid answer.

**The structure:** Every backtracking problem is a DFS on a decision tree. At each node, you make a choice. You recurse. Then you undo the choice (backtrack).

**Pruning is key:** The difference between a fast and slow backtracking solution is how early you prune dead branches. Prune as soon as you know a branch cannot lead to a valid solution.

```python
def subsets(nums):
    """All subsets. 2^n subsets."""
    result = []

    def backtrack(start, current):
        result.append(current[:])  # every state is a valid subset
        for i in range(start, len(nums)):
            current.append(nums[i])
            backtrack(i + 1, current)
            current.pop()

    backtrack(0, [])
    return result


def subsets_with_duplicates(nums):
    """All unique subsets (nums may have duplicates)."""
    nums.sort()
    result = []

    def backtrack(start, current):
        result.append(current[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i-1]:
                continue  # skip duplicate at same decision level
            current.append(nums[i])
            backtrack(i + 1, current)
            current.pop()

    backtrack(0, [])
    return result


def n_queens(n):
    """Place n queens on n×n board. Classic backtracking with pruning."""
    result = []
    cols = set()       # columns occupied
    pos_diag = set()   # (row + col) occupied
    neg_diag = set()   # (row - col) occupied
    board = ['.' * n for _ in range(n)]

    def backtrack(row):
        if row == n:
            result.append(board[:])
            return

        for col in range(n):
            if col in cols or (row + col) in pos_diag or (row - col) in neg_diag:
                continue  # PRUNING: this placement is invalid

            # CHOOSE
            cols.add(col)
            pos_diag.add(row + col)
            neg_diag.add(row - col)
            board[row] = '.' * col + 'Q' + '.' * (n - col - 1)

            # EXPLORE
            backtrack(row + 1)

            # UNCHOOSE
            cols.remove(col)
            pos_diag.remove(row + col)
            neg_diag.remove(row - col)
            board[row] = '.' * n

    backtrack(0)
    return result
```

---

## Section 5: Complexity and Space Signals

Sometimes the problem tells you the expected algorithm through the constraints themselves. This is one of the most under-taught skills in interview prep.

---

### Reading Constraints to Find the Algorithm

```
Constraint Signal          → Algorithm Hint
──────────────────────────────────────────────────────────────────
n ≤ 10                     → O(n!) backtracking is acceptable
n ≤ 20                     → O(2^n) bitmask DP or backtracking
n ≤ 100                    → O(n³) DP (Floyd-Warshall, matrix chain)
n ≤ 1,000                  → O(n²) is fine — nested loops, O(n²) DP
n ≤ 10,000                 → O(n²) is borderline — prefer O(n log n)
n ≤ 100,000                → Need O(n log n) — sort, heap, segment tree
n ≤ 1,000,000              → Need O(n) — linear scan, hash map, two pointers
n ≤ 10^9 (the answer range)→ Binary search on the answer
──────────────────────────────────────────────────────────────────
```

### O(1) Space Constraint

When the problem says "do it in O(1) extra space" (or "in-place"), your toolkit shrinks significantly:

- **Two pointers moving same direction:** sliding window, fast/slow pointer (Floyd's cycle detection)
- **Two pointers moving opposite directions:** reverse in place, partition
- **Bit manipulation:** XOR tricks, single number in array
- **Floyd's cycle detection:** find cycle in linked list or array
- **Morris traversal:** inorder traversal of tree without stack/recursion

```python
def find_duplicate_floyd(nums):
    """
    Find duplicate in array of 1..n integers.
    O(1) space: treat array as linked list, use Floyd's cycle detection.
    """
    slow = nums[0]
    fast = nums[0]

    # Phase 1: find meeting point inside cycle
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break

    # Phase 2: find cycle entrance (the duplicate)
    slow = nums[0]
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]

    return slow


def move_zeros_inplace(nums):
    """
    Move all zeros to end while maintaining relative order.
    O(1) space: two pointers.
    """
    write_pos = 0

    for read_pos in range(len(nums)):
        if nums[read_pos] != 0:
            nums[write_pos] = nums[read_pos]
            write_pos += 1

    # Fill remaining with zeros
    while write_pos < len(nums):
        nums[write_pos] = 0
        write_pos += 1


def single_number_xor(nums):
    """
    Find the number that appears only once (all others appear twice).
    XOR: a ^ a = 0, a ^ 0 = a. So XOR of all → duplicates cancel out.
    O(1) space.
    """
    result = 0
    for num in nums:
        result ^= num
    return result
```

---

## Section 6: Classic Problem-to-Pattern Mapping

This is the reference table you return to whenever you encounter a problem name and need to recall the technique.

```
╔══════════════════════════════════════╦═══════════════════════════╦══════════════════════════╦══════════════╗
║  Problem                             ║  Primary Pattern          ║  Key Idea                ║  Complexity  ║
╠══════════════════════════════════════╬═══════════════════════════╬══════════════════════════╬══════════════╣
║  Two Sum                             ║  Hash Map                 ║  complement lookup       ║  O(n)        ║
║  Two Sum II (sorted)                 ║  Two Pointers             ║  squeeze from both ends  ║  O(n)        ║
║  3Sum                                ║  Sort + Two Pointers      ║  fix one, two-ptr rest   ║  O(n²)       ║
║  Reverse Linked List                 ║  In-place pointer flip    ║  prev, curr, next        ║  O(n)        ║
║  Detect Cycle (linked list)          ║  Floyd's Two Pointers     ║  slow + fast meet        ║  O(n)        ║
║  Merge Two Sorted Lists              ║  Two Pointers             ║  merge step of merge sort ║ O(n+m)      ║
║  Valid Parentheses                   ║  Stack                    ║  push open, pop for close ║ O(n)        ║
║  Min Stack                           ║  Two Stacks / Augmented   ║  parallel min tracking   ║  O(1) ops    ║
║  Largest Rectangle Histogram         ║  Monotonic Stack          ║  increasing stack        ║  O(n)        ║
║  Trapping Rain Water                 ║  Two Pointers or Stack    ║  min of left/right max   ║  O(n)        ║
║  Maximum Subarray (Kadane's)         ║  DP / Greedy              ║  local max → global max  ║  O(n)        ║
║  Best Time to Buy/Sell Stock         ║  Greedy                   ║  track running min price ║  O(n)        ║
║  Climbing Stairs                     ║  DP (Fibonacci style)     ║  dp[i] = dp[i-1]+dp[i-2] ║ O(n)        ║
║  Coin Change                         ║  DP (Unbounded Knapsack)  ║  dp[i] = min over coins  ║  O(n×m)      ║
║  House Robber                        ║  DP (1D)                  ║  dp[i] = max(dp[i-1], dp[i-2]+val) ║ O(n) ║
║  Unique Paths                        ║  DP (2D grid)             ║  dp[i][j]=dp[i-1][j]+dp[i][j-1] ║ O(n×m) ║
║  Longest Common Subsequence          ║  DP (2D)                  ║  match→diag, else max    ║  O(n×m)      ║
║  Edit Distance                       ║  DP (2D)                  ║  insert/delete/replace   ║  O(n×m)      ║
║  Word Break                          ║  DP                       ║  dp[i] = can segment s[:i] ║ O(n²)      ║
║  Longest Increasing Subsequence      ║  DP or Binary Search      ║  patience sorting trick  ║  O(n log n)  ║
║  Number of Islands                   ║  DFS / BFS flood fill     ║  visit connected cells   ║  O(r×c)      ║
║  Course Schedule (cycle detection)   ║  Topo Sort / DFS coloring ║  Kahn's or 3-color DFS   ║  O(V+E)      ║
║  Course Schedule II (ordering)       ║  Topological Sort         ║  Kahn's BFS              ║  O(V+E)      ║
║  Clone Graph                         ║  BFS / DFS + Hash Map     ║  old node → new node map ║  O(V+E)      ║
║  Pacific Atlantic Water Flow         ║  Multi-source BFS/DFS     ║  flow backward from ocean ║ O(r×c)      ║
║  Minimum Spanning Tree               ║  Kruskal (Union-Find)     ║  sort edges, union if safe ║ O(E log E) ║
║  Shortest Path (weighted)            ║  Dijkstra                 ║  min-heap, relax edges   ║  O((V+E)logV) ║
║  All Pairs Shortest Path             ║  Floyd-Warshall           ║  dp[i][j][k] = through k ║ O(V³)       ║
║  Binary Search on Array              ║  Binary Search            ║  left/right pointers     ║  O(log n)    ║
║  Search Rotated Sorted Array         ║  Modified Binary Search   ║  find the pivot          ║  O(log n)    ║
║  Find Peak Element                   ║  Binary Search            ║  go toward uphill side   ║  O(log n)    ║
║  Median of Two Sorted Arrays         ║  Binary Search (partition) ║  balance partition halves ║ O(log n)   ║
║  Merge Intervals                     ║  Sort + Greedy            ║  sort by start, merge    ║  O(n log n)  ║
║  Meeting Rooms II                    ║  Sort + Min Heap          ║  track end times         ║  O(n log n)  ║
║  Top K Frequent Elements             ║  Min Heap or Quick Select ║  heap of size k          ║  O(n log k)  ║
║  Merge K Sorted Lists                ║  Min Heap                 ║  heap of (val, list_idx) ║  O(n log k)  ║
║  Serialize/Deserialize Tree          ║  BFS or DFS               ║  encode structure        ║  O(n)        ║
║  LCA of Binary Tree                  ║  DFS Bottom-Up            ║  return node if found    ║  O(n)        ║
║  Validate BST                        ║  DFS Top-Down (pass range) ║  min/max constraints    ║  O(n)        ║
║  Implement LRU Cache                 ║  Hash Map + Doubly Linked List ║ O(1) get and put  ║  O(1)        ║
║  Design Hit Counter                  ║  Circular Buffer / Deque  ║  window of recent hits   ║  O(1)/O(n)   ║
║  Regular Expression Matching         ║  DP (2D)                  ║  * can match 0 or more   ║  O(n×m)      ║
║  Next Greater Element                ║  Monotonic Stack          ║  decreasing stack        ║  O(n)        ║
║  Subsets / Combinations              ║  Backtracking             ║  choose-explore-unchoose ║  O(2^n)      ║
║  Permutations                        ║  Backtracking             ║  used[] array            ║  O(n!)       ║
║  N-Queens                            ║  Backtracking + Pruning   ║  col, diag constraints   ║  O(n!)       ║
╚══════════════════════════════════════╩═══════════════════════════╩══════════════════════════╩══════════════╝
```

---

## Section 7: Interview-Specific Tips

### How to Recognize DP: The Brute Force Path

Most people try to jump directly to the DP solution. That is backwards. The correct process:

```
Step 1: Write the brute force recursion.
        "What is the recursive structure of this problem?"

Step 2: Draw the recursion tree for a small input.
        "Are any subproblems being solved multiple times?"

Step 3: If yes → add memoization (top-down DP).
        "Store each result in a dict/array. Check before computing."

Step 4: Identify the order of subproblems.
        "Can I fill a table bottom-up instead of top-down?"

Step 5: Optimize space if possible.
        "Do I need the whole table, or just the previous row?"
```

**Worked example — Coin Change:**

```python
# Step 1: Brute force recursion
def coin_change_brute(coins, amount):
    if amount == 0: return 0
    if amount < 0: return float('inf')
    return 1 + min(coin_change_brute(coins, amount - c) for c in coins)

# Step 2: Draw recursion tree for coins=[1,2,5], amount=5
# We compute coin_change(3) when going 5→2→3 AND when going 5→2, 3→1→2→3
# REPEATED SUBPROBLEMS FOUND

# Step 3: Add memoization
from functools import lru_cache

def coin_change_memo(coins, amount):
    @lru_cache(maxsize=None)
    def dp(remaining):
        if remaining == 0: return 0
        if remaining < 0: return float('inf')
        return 1 + min(dp(remaining - c) for c in coins)
    result = dp(amount)
    return result if result != float('inf') else -1

# Step 4: Bottom-up table
def coin_change_dp(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1

# Step 5: Space already O(amount), which is optimal here.
```

---

### When Greedy Fails: The Counterexample Method

Before committing to greedy, always think about whether a counterexample exists.

**Greedy works for:**
- Activity selection (sort by end time)
- Huffman coding (always take two lowest-frequency nodes)
- Dijkstra (always process minimum distance node)
- Fractional knapsack (take highest value/weight ratio first)

**Greedy fails for:**
- 0/1 Knapsack (taking highest value item might block better combination)
- Coin change with arbitrary denominations (example above)
- Shortest path with negative weights (need Bellman-Ford)

**The exchange argument test:** To verify greedy, ask:
> "If I swap the greedy choice for any other choice, can the result get better?"

If the answer is always no, greedy is provably correct.

---

### How to Explain Time Complexity to an Interviewer

Do not just say "O(n log n)". Explain WHY it is O(n log n). Interviewers want to see your reasoning, not a memorized answer.

**The three-step explanation:**

```
1. State the dominant operations:
   "The outer loop runs n times. Inside, we do a binary search which is O(log n)."

2. State the complexity:
   "So the total is O(n × log n) = O(n log n)."

3. State the space:
   "Space is O(n) because we store at most n elements in the result array."
```

**Example for merge sort:**
> "We recursively split the array in half — that is O(log n) levels of recursion. At each level, we do O(n) work to merge all the subarrays at that level. Total: O(n log n). Space is O(n) for the temporary arrays used during merging."

---

### The "Think Out Loud" Framework

Good interviewers want to see your thought process, not just the final answer. Use this framework:

```
STEP 1 — Restate and clarify (1-2 minutes)
  "Let me restate the problem to make sure I understand..."
  "A few clarifying questions: Can input be empty? Can values be negative?
   Should I return the count or the values?"

STEP 2 — Examples (1-2 minutes)
  "Let me trace through a couple examples to build intuition..."
  Run the simplest possible case. Run an edge case. Talk through them.

STEP 3 — Brute force first (1-2 minutes)
  "The naive approach would be..."
  State it, give its complexity. Do not code it yet.
  This shows you can think before coding.

STEP 4 — Optimize (2-3 minutes)
  "I notice the brute force is O(n²). To improve it, I can..."
  Connect to a pattern: "This looks like a sliding window problem because..."
  State the optimized complexity before coding.

STEP 5 — Code (10-15 minutes)
  Write clean code, talking as you go.
  Name variables clearly. Write helper functions if needed.
  Check edge cases as you write (empty input, single element, etc.)

STEP 6 — Test (2-3 minutes)
  Walk through your code with the examples from step 2.
  "Let me trace: when i=0, left=0, right=4..."
  Catch bugs before the interviewer does.

STEP 7 — Complexity analysis (1-2 minutes)
  State time and space complexity with reasoning.
```

---

### The 10 Patterns and Their "One-Line Memory Aid"

When you are nervous in an interview and need to recall a pattern quickly:

```
Two Pointers:       "Squeeze from both ends of the sorted array."
Sliding Window:     "Expand right freely, shrink left when invalid."
Prefix Sum:         "Sum from i to j = prefix[j] - prefix[i]."
Hash Map:           "For each x, check if (target - x) was already seen."
Binary Search:      "Eliminate half the search space each step."
DFS Top-Down:       "Parent passes a memo to children on the way down."
DFS Bottom-Up:      "Children send a report to the parent on the way up."
BFS:                "Wavefront: process all nodes at distance d before d+1."
Dynamic Programming:"Remember answers to subproblems; never recompute."
Backtracking:       "Choose, explore, unchoose. Prune invalid branches early."
Union-Find:         "Are x and y connected? Union them if not."
Topological Sort:   "Start with no-dependency nodes, reduce others' counts."
Monotonic Stack:    "Pop smaller elements when a taller one arrives."
Greedy:             "Always pick the locally optimal choice; prove it works."
```

---

### Recognizing DP vs Greedy at a Glance

This is the most common confusion in optimization problems. Use this decision guide:

```
Ask: "If I make the locally optimal choice now, does it
      guarantee the globally optimal solution?"

YES, provably → Greedy (fast, O(n) or O(n log n))
NO, or unsure → DP (try brute force → memoize → tabulate)

Quick test — try a counterexample:
  Construct a small input where the greedy choice FAILS.
  If you can find one → DP.
  If you cannot (after genuinely trying) → likely Greedy.

Classic greedy problems (sorted by end time, greedy is provably optimal):
  - Activity selection
  - Task scheduler
  - Jump Game

Classic DP problems (greedy fails, overlapping subproblems exist):
  - Coin change (arbitrary coins)
  - 0/1 Knapsack
  - Edit distance
  - Longest increasing subsequence
```

---

### Edge Cases to Always Check

Before finishing any solution, run through this checklist:

```
Input validation:
  □ Empty input (empty array, empty string, null)
  □ Single element
  □ Two elements

Value ranges:
  □ All zeros or all same value
  □ Negative numbers (if applicable)
  □ Maximum integer value (overflow risk in languages without BigInt)
  □ Already sorted input (for sorting-based solutions)
  □ Reverse sorted input

Graph/Tree specific:
  □ Single node tree
  □ Linear chain (degenerate tree/graph)
  □ Disconnected graph

DP specific:
  □ Target = 0 (base case)
  □ No solution exists (should return -1 or 0 or empty, not infinity)
  □ Large inputs (check space complexity)

Pointer/index:
  □ Off-by-one errors at array boundaries
  □ left < right vs left <= right (know which you need)
  □ mid = left + (right - left) // 2 (not (left+right)//2 in languages with overflow)
```

---

### The Most Common Mistakes by Pattern

```
Binary Search:
  × Using left <= right when you need left < right (or vice versa)
  × Using mid = (left + right) // 2 (integer overflow in C/Java — not Python)
  × Forgetting to update bounds correctly (off-by-one)

Sliding Window:
  × Trying to use sliding window when array has negative numbers
    (prefix sum is correct there)
  × Not handling the "formed" counter correctly for character matching

DFS Backtracking:
  × Forgetting to copy the current state when adding to results
    (result.append(current) adds a reference, not a copy)
  × Not pruning early enough
  × Forgetting to undo (backtrack) after recursing

DP:
  × Not handling base cases (dp[0], dp[0][j], dp[i][0])
  × Wrong iteration order (computing dp[i] before dp[i-1] is ready)
  × Off-by-one in dp array size (need dp[n+1] not dp[n])

Graphs:
  × Not marking nodes as visited before pushing to queue (can visit twice in BFS)
  × Mixing up directed and undirected graph handling
  × Forgetting to handle disconnected graphs in DFS/BFS counting problems

Two Pointers:
  × Using two pointers on unsorted array when the logic requires sorted order
  × Not handling duplicates in 3Sum/4Sum problems
```

---

### Final Words: The Two Levels of Pattern Recognition

There are two levels at which you recognize patterns, and the best engineers operate at both.

**Level 1 — Surface patterns:** "The problem says 'two sum' and the input is sorted. Two pointers." This is what you get from memorizing patterns. It is necessary but not sufficient.

**Level 2 — Deep patterns:** "This problem asks for the minimum number of operations to transform one state to another, and the state space is a graph. BFS gives me the minimum path length." This is what you get from understanding WHY patterns work. It lets you solve problems you have never seen before.

To build Level 2 recognition, after solving any problem, ask yourself:
- Why does this approach work?
- What property of the problem does this algorithm exploit?
- What would break if I changed one thing about the problem?

The answer to those questions is the real pattern — not the name of the algorithm, but the structural property that makes the algorithm correct.

That is what this guide is really teaching: not "use sliding window here" but "sliding window works when the problem has the property that you can maintain a valid state by expanding right and shrinking left, and this is true because..."

Build that understanding, and no interview problem will catch you completely off guard again.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← FAANG Level Questions](./faang_level_questions.md) &nbsp;|&nbsp; **Next:** —

**Related Topics:** [0-2 Years Experience](./0_2_years.md) · [3-5 Years Experience](./3_5_years.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [FAANG Level Questions](./faang_level_questions.md)
