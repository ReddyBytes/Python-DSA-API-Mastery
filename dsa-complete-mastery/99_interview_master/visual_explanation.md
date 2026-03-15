# Interview Problem Patterns — Visualized

> "A pattern is not a solution. It is a lens. Once you see the right lens, the solution becomes obvious."

Most developers struggle with algorithm interviews not because they lack intelligence, but because they lack pattern recognition. They see a new problem and try to solve it from scratch. Experienced interviewers see a new problem and immediately think: "This is a sliding window problem with a hash map" or "This is BFS on an implicit graph."

This file builds that pattern-recognition muscle through visuals. Not math. Not abstract definitions. Actual ASCII pictures of data structures moving, trees being traversed, windows sliding, waves spreading. Because your brain is much better at recognizing pictures than memorizing rules.

Read slowly. Trace each diagram with your finger. Rebuild the pictures on paper. Then you will own these patterns for good.

---

## Algorithm Selection Flowchart

When you read a problem, run it through this decision tree before writing a single line of code. This is your compass.

```
                        NEW PROBLEM
                            │
                  ┌─────────▼─────────┐
                  │  What is the      │
                  │  input type?      │
                  └─────────┬─────────┘
        ┌──────────┬────────┴────────┬──────────┐
        ▼          ▼                 ▼           ▼
    ARRAY/      STRING            TREE /      NUMBERS /
    LIST                          GRAPH        MATH
        │          │                 │           │
        ▼          ▼                 ▼           ▼
  Is it sorted?  Anagram/         Any path?   Optimize
        │        pattern?             │        value?
     Yes│No        │              Yes│No          │
        │  │       ▼                 │  │         ▼
        │  │  Freq map /         DFS │  │  Overlapping
    Binary│  Sliding             (bottom-  subproblems?
    search│  window              up if     │
        │  │                   aggregating)│
        │  ▼                        │  BFS for     Yes→DP
        │ Find pair/               │  level/     No→Greedy
        │ triplet?                 │  shortest   All paths→
        │   │                     │  path       Backtrack
        │   ▼                     │
        │ Has duplicates?    Weighted
        │ Hash map O(1)      graph?
        │ No duplicates:     Dijkstra /
        │ Two pointers       Bellman-Ford
        │ after sort
        │
    "Longest/shortest
     subarray where..."
        → Sliding Window
    "Subarray sum = k"
        → Prefix Sum
    "Max/min subarray"
        → Kadane's / DP
```

Keep this flowchart in mind as you work through each pattern below.

---

## 1. The Two-Sum Family

### The Story

You are given a sorted array and a target. Find two numbers that add up to the target.

The naive approach: check every pair. For each element at index i, check all elements after it. That is O(n²) — two nested loops.

The insight: the array is sorted. If the sum is too big, move the right pointer left. If too small, move the left pointer right. You never need to go back. One pass. O(n).

### ASCII Trace: Two Sum on Sorted Array

```
Array: [1, 2, 3, 4, 5, 6, 7, 8]    Target = 9
        L                    R

Step 1:
        [1, 2, 3, 4, 5, 6, 7, 8]
         L                    R
         1 + 8 = 9 ✓ FOUND!

Let us try a harder example. Target = 11:

Step 1:
        [1, 2, 3, 4, 5, 6, 7, 8]
         L                    R
         1 + 8 = 9 < 11  →  move L right

Step 2:
        [1, 2, 3, 4, 5, 6, 7, 8]
            L                 R
            2 + 8 = 10 < 11  →  move L right

Step 3:
        [1, 2, 3, 4, 5, 6, 7, 8]
               L              R
               3 + 8 = 11 ✓ FOUND!

Key mental model:
  Sum too small → L moves right  (makes sum bigger)
  Sum too big   → R moves left   (makes sum smaller)
  Sum exact     → FOUND

L and R can never "miss" the pair because:
  If arr[L] + arr[R] > target, any arr[L'] where L' > L would make it even bigger.
  So we can safely shrink from R. The same logic applies in reverse.
```

### The Code Pattern

```python
def two_sum_sorted(nums, target):
    """
    O(n) time, O(1) space.
    Works only on SORTED arrays.
    """
    left, right = 0, len(nums) - 1

    while left < right:
        current_sum = nums[left] + nums[right]

        if current_sum == target:
            return [left, right]
        elif current_sum < target:
            left += 1   # sum too small, move left pointer right
        else:
            right -= 1  # sum too big, move right pointer left

    return []


def two_sum_unsorted(nums, target):
    """
    O(n) time, O(n) space.
    Works on UNSORTED arrays using a hash map.
    For each number, check if (target - number) is already seen.
    """
    seen = {}  # value → index

    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i

    return []
```

### Extension: 3Sum

3Sum transforms into multiple Two Sum problems. Sort the array, fix one element, then use two pointers for the remaining two.

```
Array: [-4, -1, -1, 0, 1, 2]    Target sum = 0

Fix arr[0] = -4:
  Need two numbers summing to 4
  Two pointers on [-1, -1, 0, 1, 2]:
  -1 + 2 = 1 < 4 → move left
  -1 + 2 = 1 < 4 → move left
   0 + 2 = 2 < 4 → move left
   1 + 2 = 3 < 4 → move left
   → L meets R, no solution with -4

Fix arr[1] = -1:
  Need two numbers summing to 1
  Two pointers on [-1, 0, 1, 2]:
  -1 + 2 = 1 ✓ Found: [-1, -1, 2]
   0 + 1 = 1 ✓ Found: [-1, 0, 1]
  → L meets R, done with -1

Fix arr[3] = 0:
  Need two numbers summing to 0
  Two pointers on [1, 2]:
  1 + 2 = 3 > 0 → move right
  → L meets R, no solution with 0
```

### Two Sum Family Summary

| Variant | Constraint | Approach | Complexity |
|---|---|---|---|
| Two Sum I | Unsorted, return indices | Hash map | O(n) time, O(n) space |
| Two Sum II | Sorted, return 1-indexed | Two pointers | O(n) time, O(1) space |
| Two Sum BST | Two BSTs, find pair | Inorder + two pointers | O(n) time |
| 3Sum | All unique triplets | Sort + Two Pointers | O(n²) time |
| 4Sum | All unique quadruplets | Sort + Two Pointers × 2 | O(n³) time |

---

## 2. The Sliding Window Family

### The Mental Model

Imagine a physical window sliding across a table covered in cards. The window frame covers exactly k cards at a time (for fixed-size windows) or expands and shrinks (for variable-size windows). You are always looking at the cards inside the window.

The key insight: when the window slides one step right, you do not recompute from scratch. You just add the new card on the right and remove the old card on the left. This is what converts O(n×k) to O(n).

### Visual: Fixed-Size Window (Maximum Sum Subarray of Size K)

```
Array: [2, 1, 5, 1, 3, 2]    k = 3
Find the maximum sum of any subarray of length 3.

Step 1: Initial window
        [2, 1, 5, 1, 3, 2]
         ├───────┤
         sum = 2+1+5 = 8

Step 2: Slide right (add 1, remove 2)
        [2, 1, 5, 1, 3, 2]
            ├───────┤
            sum = 8 - 2 + 1 = 7

Step 3: Slide right (add 3, remove 1)
        [2, 1, 5, 1, 3, 2]
               ├───────┤
               sum = 7 - 1 + 3 = 9   ← new max!

Step 4: Slide right (add 2, remove 5)
        [2, 1, 5, 1, 3, 2]
                  ├───────┤
                  sum = 9 - 5 + 2 = 6

Answer: 9 (subarray [5, 1, 3])

Key operation:
  new_sum = old_sum - arr[window_start] + arr[window_end + 1]
  O(1) per slide instead of O(k) per slide
```

### Visual: Variable-Size Window (Longest Substring Without Repeating Characters)

This is the most common sliding window interview question. The window expands on the right when the new character is unique, and shrinks from the left when we encounter a repeat.

```
String: "a b c a b c b b"
         0 1 2 3 4 5 6 7

State: left=0, right=0, seen={}

right=0, char='a':  seen={a:0}     window=[a]         len=1
         ┌─┐
         a b c a b c b b

right=1, char='b':  seen={a:0,b:1} window=[a,b]       len=2
         ┌───┐
         a b c a b c b b

right=2, char='c':  seen={a:0,b:1,c:2}  window=[a,b,c]   len=3
         ┌─────┐
         a b c a b c b b

right=3, char='a':  'a' already in window at index 0!
  → move left past 0: left=1, remove 'a' from seen
         ┌─────┐                window=[b,c,a]  len=3
         a b c a b c b b
           ├─────┤

right=4, char='b':  'b' already in window at index 1!
  → move left past 1: left=2, remove 'b' from seen
         window=[c,a,b]  len=3
         a b c a b c b b
             ├─────┤

right=5, char='c':  'c' already in window at index 2!
  → move left past 2: left=3, remove 'c' from seen
         window=[a,b,c]  len=3
         a b c a b c b b
               ├─────┤

right=6, char='b':  'b' already in window at index 4!
  → move left past 4: left=5, remove 'a','b' from path
         window=[c,b]  len=2
         a b c a b c b b
                   ├───┤

right=7, char='b':  'b' already in window at index 6!
  → move left past 6: left=7
         window=[b]  len=1

Maximum window length seen: 3  (subarray "abc")
```

### The Universal Sliding Window Template

```python
def sliding_window_template(arr, condition_func):
    """
    Universal template for variable-size sliding window problems.

    Expand right always. Shrink left when the window violates a condition.
    """
    left = 0
    result = 0
    # window state (problem-specific)
    window_state = {}  # or a counter, integer, etc.

    for right in range(len(arr)):
        # 1. EXPAND: add arr[right] to window
        # (update window_state with arr[right])
        item = arr[right]
        window_state[item] = window_state.get(item, 0) + 1

        # 2. SHRINK: while window is invalid, remove arr[left]
        while condition_func(window_state):
            left_item = arr[left]
            window_state[left_item] -= 1
            if window_state[left_item] == 0:
                del window_state[left_item]
            left += 1

        # 3. RECORD: current window [left..right] is valid
        current_window_size = right - left + 1
        result = max(result, current_window_size)

    return result


def longest_no_repeat(s):
    """Longest substring without repeating characters."""
    seen = {}
    left = 0
    max_len = 0

    for right, char in enumerate(s):
        # If char is in window, shrink from left
        if char in seen and seen[char] >= left:
            left = seen[char] + 1
        seen[char] = right
        max_len = max(max_len, right - left + 1)

    return max_len


def max_fruit_in_baskets(fruits):
    """
    You have two baskets. Each basket holds only one fruit type.
    Find longest subarray with at most 2 distinct values.
    """
    basket = {}
    left = 0
    max_fruits = 0

    for right, fruit in enumerate(fruits):
        basket[fruit] = basket.get(fruit, 0) + 1

        # More than 2 fruit types → shrink window
        while len(basket) > 2:
            left_fruit = fruits[left]
            basket[left_fruit] -= 1
            if basket[left_fruit] == 0:
                del basket[left_fruit]
            left += 1

        max_fruits = max(max_fruits, right - left + 1)

    return max_fruits
```

### Four Sub-Types of Sliding Window

```
TYPE 1: Fixed size window
─────────────────────────
Pattern: "maximum/minimum of all subarrays of size k"
Clue: k is given as a fixed parameter
Approach: slide window of exact size k
Example: Max Average Subarray of Size K

TYPE 2: Variable size, maximize window
───────────────────────────────────────
Pattern: "longest subarray/substring satisfying condition"
Clue: maximize length
Approach: expand right, shrink left when condition violated
Example: Longest Substring Without Repeat

TYPE 3: Variable size, minimize window
───────────────────────────────────────
Pattern: "shortest subarray/substring satisfying condition"
Clue: minimize length
Approach: expand right until condition met, then shrink left
Example: Minimum Window Substring

TYPE 4: Count windows satisfying condition
──────────────────────────────────────────
Pattern: "number of subarrays with property"
Clue: count, not max/min
Approach: Often use "at most k" helper: f(k) - f(k-1)
Example: Subarrays with K Distinct Integers
```

---

## 3. Tree DFS — Top-Down vs Bottom-Up

### The Two Travelers Mental Model

Imagine a binary tree as an organization chart. There are two ways to send information through it:

**Top-Down (like a manager sending memos):**
The information starts at the root and travels downward. Each node receives a memo from its parent, does some work, and passes an updated memo to its children. The useful result is usually computed AT the leaves or accumulated along the path.

**Bottom-Up (like employees sending reports):**
The information starts at the leaves and travels upward. Each leaf sends a report to its parent. The parent combines the reports from both children and sends a combined report upward. The result is at the root.

### Side-by-Side Visualization

```
Tree:
           1
          / \
         2   3
        / \
       4   5

TOP-DOWN EXAMPLE: Has Path Sum = 8 (root-to-leaf)

Root sends down remaining_sum = 8

         1 (remaining: 8)
        / \
      2    3 (remaining: 8-1=7)
(remaining: 7)
    / \
   4   5 (remaining: 7-2=5)
(remaining: 5)

At leaf 4: remaining = 5-4 = 1 ≠ 0 → False
At leaf 5: remaining = 5-5 = 0 → True! PATH FOUND

Message flows: ROOT → children (parent passes info DOWN)

def has_path_sum(node, remaining):
    if not node:
        return False
    remaining -= node.val
    if not node.left and not node.right:
        return remaining == 0
    return (has_path_sum(node.left, remaining) or
            has_path_sum(node.right, remaining))

─────────────────────────────────────────────────────────

BOTTOM-UP EXAMPLE: Diameter of Binary Tree

Each node reports to parent: (max_depth_below_me)

Leaf 4: reports depth = 1
Leaf 5: reports depth = 1

         1
        / \
       2   3
      / \
     4   5
     ↑   ↑
     1   1  ← reports going up

Node 2 receives:
  left_depth = 1 (from node 4)
  right_depth = 1 (from node 5)
  diameter_through_2 = 1 + 1 = 2
  reports to parent: depth = max(1,1) + 1 = 2

Node 3: leaf, reports depth = 1

Node 1 receives:
  left_depth = 2 (from node 2)
  right_depth = 1 (from node 3)
  diameter_through_1 = 2 + 1 = 3
  reports to parent (none, it's root): depth = max(2,1) + 1 = 3

Answer: 3 (path: 4→2→1→3 or 5→2→1→3)

Message flows: leaves → parents (children send info UP)
```

### Code Comparison

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


# ── TOP-DOWN DFS ──────────────────────────────────────────────────────────────
# Pattern: parent passes context (state/accumulator) DOWN to children
# Use when: the answer depends on what came BEFORE this node (path from root)

def has_path_sum(root, target_sum):
    """
    Does any root-to-leaf path sum equal target_sum?
    Classic top-down: pass remaining sum downward.
    """
    def dfs(node, remaining):
        if not node:
            return False
        remaining -= node.val
        # At a leaf: check if we hit exactly zero
        if not node.left and not node.right:
            return remaining == 0
        # Pass remaining down to children
        return dfs(node.left, remaining) or dfs(node.right, remaining)

    return dfs(root, target_sum)


def max_depth_topdown(root):
    """
    Maximum depth — pass current depth downward.
    """
    self_max = [0]

    def dfs(node, depth):
        if not node:
            return
        self_max[0] = max(self_max[0], depth)
        dfs(node.left, depth + 1)
        dfs(node.right, depth + 1)

    dfs(root, 1)
    return self_max[0]


# ── BOTTOM-UP DFS ─────────────────────────────────────────────────────────────
# Pattern: children return results to parent, parent combines them
# Use when: the answer depends on BOTH subtrees (aggregation)

def diameter_of_binary_tree(root):
    """
    Longest path between any two nodes.
    Classic bottom-up: each node returns its depth to parent,
    parent computes diameter through itself.
    """
    max_diameter = [0]

    def dfs(node):
        """Returns the depth of this subtree (used by parent)."""
        if not node:
            return 0

        left_depth = dfs(node.left)    # get depth of left subtree
        right_depth = dfs(node.right)  # get depth of right subtree

        # Diameter through this node = left_depth + right_depth
        max_diameter[0] = max(max_diameter[0], left_depth + right_depth)

        # Report OWN depth to parent
        return max(left_depth, right_depth) + 1

    dfs(root)
    return max_diameter[0]


def max_path_sum(root):
    """
    Maximum path sum between any two nodes.
    Bottom-up: each node returns max "contribution" to parent.
    """
    max_sum = [float('-inf')]

    def dfs(node):
        """Returns max gain this node can contribute to its parent."""
        if not node:
            return 0

        # Only take positive contributions from children
        left_gain = max(dfs(node.left), 0)
        right_gain = max(dfs(node.right), 0)

        # Best path THROUGH this node
        price_newpath = node.val + left_gain + right_gain
        max_sum[0] = max(max_sum[0], price_newpath)

        # Return best SINGLE-SIDE contribution to parent
        return node.val + max(left_gain, right_gain)

    dfs(root)
    return max_sum[0]
```

### When to Use Each

```
Top-Down:                           Bottom-Up:
────────────────────────            ────────────────────────
✓ Path from root to leaf            ✓ Aggregating from leaves
✓ "Has a path with property"        ✓ Diameter, max path sum
✓ "Count nodes at depth k"          ✓ Height, balance check
✓ Context needed from above         ✓ Both subtrees needed

Signal phrases:                     Signal phrases:
  "root to leaf path"                 "between any two nodes"
  "at depth k"                        "height/depth of tree"
  "max sum path from root"            "balanced tree check"
  "all paths"                         "LCA (Lowest Common Ancestor)"
```

---

## 4. BFS — The Wave Front

### The Mental Model

Drop a stone in a still pond. Rings of ripples spread outward — first the ring at distance 1, then distance 2, then distance 3. BFS works exactly like this. It visits all nodes at distance 1 before any node at distance 2. It visits all at distance 2 before any at distance 3.

This wavefront property is precisely what makes BFS the right tool for finding **shortest paths** (in unweighted graphs) and for any **level-by-level** processing.

### ASCII: BFS Spreading Through a Graph

```
Graph:
        1
       / \
      2   3
     / \   \
    4   5   6
             \
              7

BFS from node 1:

Initial: Queue = [1]
Visited: {1}

Wave 1 (distance 0):
  Process 1 → add neighbors 2, 3
  Queue = [2, 3]

  ┌───┐
  │ 1 │   ← processed (wave 0)
  └───┘
  / \
 2   3     ← discovered (wave 1)

Wave 2 (distance 1):
  Process 2 → add neighbors 4, 5
  Process 3 → add neighbor 6
  Queue = [4, 5, 6]

  ┌───┐
  │ 1 │
  └───┘
  / \
┌─┐ ┌─┐   ← processed (wave 1)
│2│ │3│
└─┘ └─┘
/ \   \
4  5   6   ← discovered (wave 2)

Wave 3 (distance 2):
  Process 4 → no unvisited neighbors
  Process 5 → no unvisited neighbors
  Process 6 → add neighbor 7
  Queue = [7]

Order visited: 1, 2, 3, 4, 5, 6, 7
Distances:     0, 1, 1, 2, 2, 2, 3
```

### BFS Code Template

```python
from collections import deque


def bfs_template(graph, start):
    """
    Standard BFS template.
    Time: O(V + E) — visits every vertex and edge once
    Space: O(V) — queue and visited set
    """
    queue = deque([start])
    visited = {start}
    distance = {start: 0}
    level_order = [[start]]  # nodes grouped by level

    while queue:
        node = queue.popleft()

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                distance[neighbor] = distance[node] + 1
                queue.append(neighbor)

    return distance


def level_order_traversal(root):
    """
    BFS on binary tree: process nodes level by level.
    Returns list of lists, one list per level.
    """
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)    # number of nodes at THIS level
        current_level = []

        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        result.append(current_level)

    return result


def shortest_path_grid(grid, start, end):
    """
    BFS on a 2D grid. Find shortest path from start to end.
    grid[r][c] = 0 means open, 1 means blocked.
    Time: O(rows × cols)
    """
    rows, cols = len(grid), len(grid[0])
    queue = deque([(start, 0)])   # (position, steps)
    visited = {start}
    directions = [(0,1), (0,-1), (1,0), (-1,0)]

    while queue:
        (r, c), steps = queue.popleft()

        if (r, c) == end:
            return steps

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and grid[nr][nc] == 0
                    and (nr, nc) not in visited):
                visited.add((nr, nc))
                queue.append(((nr, nc), steps + 1))

    return -1  # no path found


def word_ladder(begin_word, end_word, word_list):
    """
    Classic BFS on an implicit graph.
    Each word is a node. Two words are connected if they differ by one letter.
    Find shortest transformation sequence.
    """
    word_set = set(word_list)
    if end_word not in word_set:
        return 0

    queue = deque([(begin_word, 1)])
    visited = {begin_word}

    while queue:
        word, length = queue.popleft()

        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                new_word = word[:i] + c + word[i+1:]

                if new_word == end_word:
                    return length + 1

                if new_word in word_set and new_word not in visited:
                    visited.add(new_word)
                    queue.append((new_word, length + 1))

    return 0
```

### BFS vs DFS Quick Visual

```
Same graph:    A - B - C
                   |
                   D

BFS order (queue — uses FIFO):
  Start: [A]
  Process A, add B:  [B]
  Process B, add C,D: [C, D]
  Process C: [D]
  Process D: []
  Visit order: A → B → C → D
  (breadth first — horizontal sweep)

DFS order (stack — uses LIFO):
  Start: [A]
  Process A, push B: [B]
  Process B, push D, C: [C, D]  ← C pushed last, popped first
  Process D: [C]
  Process C: []
  Visit order: A → B → D → C
  (depth first — goes deep before wide)

          A
  BFS:    ─────► B ─────► C
                  └──────► D

  DFS:    ─────► B ─────► D
                  └──────► C
```

---

## 5. Dynamic Programming — The Table-Filling Story

### The Story

DP is not about filling tables. That is just the implementation. DP is about one insight:

**If I have already solved a sub-problem, I should remember the answer instead of solving it again.**

The "table" is just a convenient way to remember those answers. The skill is identifying WHICH sub-problems to remember and HOW they connect.

### ASCII Grid: Longest Common Subsequence (LCS)

LCS of "ABCBDAB" and "BDCAB":

```
Build dp[i][j] = length of LCS of first i chars of s1 and first j chars of s2.

     ""  B  D  C  A  B
  ""  0  0  0  0  0  0
  A   0  0  0  0  1  1
  B   0  1  1  1  1  2
  C   0  1  1  2  2  2
  B   0  1  1  2  2  3
  D   0  1  2  2  2  3
  A   0  1  2  2  3  3
  B   0  1  2  2  3  4

Answer: dp[7][5] = 4

How to fill each cell:
  If s1[i] == s2[j]:
    dp[i][j] = dp[i-1][j-1] + 1   ← diagonal + 1 (characters match)
               ↖
  Else:
    dp[i][j] = max(dp[i-1][j], dp[i][j-1])   ← take best of up or left
               ↑              ←

Let us trace filling dp[4][5] where s1[4]='B', s2[5]='B' (match):

     ""  B  D  C  A  B
  ""  0  0  0  0  0  0
  A   0  0  0  0  1  1
  B   0  1  1  1  1  2
  C   0  1  1  2  2  2
  B   0  1  1  2  2  ?
                     ↖ diagonal = dp[3][4] = 2
                     dp[4][5] = 2 + 1 = 3

Arrows tell the story:
  ↖  Characters matched here
  ←  Took best from left (included s2 char, skipped s1)
  ↑  Took best from above (included s1 char, skipped s2)
```

### The Three Steps to Solve Any DP Problem

```
STEP 1: Define the subproblem clearly
─────────────────────────────────────
Ask: "dp[i] represents ___"
     "dp[i][j] represents ___"

For LCS: dp[i][j] = "LCS length using first i chars of s1, first j of s2"

STEP 2: Write the recurrence (how smaller → larger)
────────────────────────────────────────────────────
Ask: "How does dp[i] relate to dp[i-1], dp[i-2], etc.?"

For LCS:
  if s1[i] == s2[j]: dp[i][j] = dp[i-1][j-1] + 1
  else:              dp[i][j] = max(dp[i-1][j], dp[i][j-1])

STEP 3: Identify base cases
────────────────────────────
Ask: "What is the smallest subproblem I can answer directly?"

For LCS: dp[0][j] = 0 and dp[i][0] = 0 (empty string has LCS of 0)
```

### Common DP Patterns

```python
# ── 1D DP: Coin Change ────────────────────────────────────────────────────────
def coin_change(coins, amount):
    """
    dp[i] = minimum coins to make amount i
    Recurrence: dp[i] = min(dp[i - coin] + 1) for each coin
    """
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0  # base case: 0 coins for amount 0

    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)

    return dp[amount] if dp[amount] != float('inf') else -1


# ── 1D DP: Longest Increasing Subsequence ────────────────────────────────────
def lis(nums):
    """
    dp[i] = length of LIS ending at index i
    Recurrence: dp[i] = max(dp[j] + 1) for all j < i where nums[j] < nums[i]
    """
    n = len(nums)
    dp = [1] * n

    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)

    return max(dp)


# ── 2D DP: LCS ────────────────────────────────────────────────────────────────
def lcs(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    return dp[m][n]
```

---

## 6. Backtracking — The Decision Tree

### The Story

Backtracking is systematic trial and error. You are exploring a decision tree: at each node, you make a choice. You go as deep as you can along that choice. When you hit a dead end (or a solution), you **back up** to the previous decision point and try the next option.

The power of backtracking is **pruning** — when you realize a branch cannot possibly lead to a solution, you cut it off entirely instead of exploring every dead-end leaf.

### ASCII: All Subsets of {1, 2, 3}

```
Decision at each step: include this number or not?

Root: []
│
├── Include 1: [1]
│   ├── Include 2: [1,2]
│   │   ├── Include 3: [1,2,3] ← SOLUTION
│   │   └── Exclude 3: [1,2]   ← SOLUTION
│   │
│   └── Exclude 2: [1]
│       ├── Include 3: [1,3]   ← SOLUTION
│       └── Exclude 3: [1]     ← SOLUTION
│
└── Exclude 1: []
    ├── Include 2: [2]
    │   ├── Include 3: [2,3]   ← SOLUTION
    │   └── Exclude 3: [2]     ← SOLUTION
    │
    └── Exclude 2: []
        ├── Include 3: [3]     ← SOLUTION
        └── Exclude 3: []      ← SOLUTION

Total subsets: 8 = 2³ ✓

The "Choose → Explore → Unchoose" cycle:

  def backtrack(start, current):
      solutions.append(current[:])  ← record current state

      for i in range(start, n):
          current.append(nums[i])   ← CHOOSE
          backtrack(i + 1, current) ← EXPLORE
          current.pop()             ← UNCHOOSE (backtrack)
```

### ASCII: Pruning in N-Queens

```
4-Queens: place 4 queens on 4×4 board, none attacking each other.

Row 0: Try column 0
  ┌─┬─┬─┬─┐
  │Q│ │ │ │   Queen at (0,0)
  └─┴─┴─┴─┘

Row 1: Try column 0 → conflicts with (0,0) ✗ PRUNE
Row 1: Try column 1 → on same diagonal ✗ PRUNE
Row 1: Try column 2 → OK
  ┌─┬─┬─┬─┐
  │Q│ │ │ │
  │ │ │Q│ │   Queen at (1,2)
  └─┴─┴─┴─┘

Row 2: Try column 0 → diagonal conflict ✗ PRUNE
Row 2: Try column 1 → no conflict, try it
  ┌─┬─┬─┬─┐
  │Q│ │ │ │
  │ │ │Q│ │
  │ │Q│ │ │   Queen at (2,1)?
  └─┴─┴─┴─┘

Row 3: All columns conflict → DEAD END, backtrack to row 2
...

Pruning means: as soon as we know a branch is invalid,
we stop exploring it. This transforms O(n^n) into something
much smaller in practice.
```

### Backtracking Template

```python
def backtrack_template(candidates, target, result, current, start):
    """
    Universal backtracking template.
    Adapt 'is_valid', 'is_solution', and 'make_choice/undo_choice'.
    """
    # Base case: found a valid solution
    if is_solution(current, target):
        result.append(current[:])  # save a copy
        return

    for i in range(start, len(candidates)):
        # Pruning: skip invalid choices early
        if not is_valid(candidates[i], current, target):
            continue

        # CHOOSE
        current.append(candidates[i])

        # EXPLORE
        backtrack_template(candidates, target, result, current, i + 1)

        # UNCHOOSE (backtrack)
        current.pop()


def combination_sum(candidates, target):
    """Find all combinations summing to target. Can reuse elements."""
    result = []

    def backtrack(start, remaining, current):
        if remaining == 0:
            result.append(current[:])
            return
        if remaining < 0:
            return  # pruning

        for i in range(start, len(candidates)):
            current.append(candidates[i])
            backtrack(i, remaining - candidates[i], current)  # i (not i+1) = reuse allowed
            current.pop()

    candidates.sort()
    backtrack(0, target, [])
    return result


def permutations(nums):
    """Generate all permutations of nums."""
    result = []
    used = [False] * len(nums)

    def backtrack(current):
        if len(current) == len(nums):
            result.append(current[:])
            return

        for i in range(len(nums)):
            if used[i]:
                continue  # already in current permutation
            used[i] = True
            current.append(nums[i])
            backtrack(current)
            current.pop()
            used[i] = False

    backtrack([])
    return result
```

---

## 7. Binary Search — The "Guess a Number" Game

### The Story

Remember the number guessing game? "I'm thinking of a number between 1 and 100." You guess 50. "Too high." You guess 25. "Too low." You guess 37. "Too high." And so on.

Each guess eliminates half the remaining possibilities. That is binary search. After 7 guesses, you have covered all 128 possibilities (2^7 = 128 > 100). Log base 2 of 100 is about 6.6 — so 7 guesses is provably optimal.

### ASCII: Pointer Convergence

```
Array: [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
Target: 7

Initial:
         L                                R
         0   1   2   3   4   5   6   7   8   9
        [1,  3,  5,  7,  9, 11, 13, 15, 17, 19]
         mid = (0+9)//2 = 4 → arr[4] = 9

Step 1:
         L               R
         0   1   2   3   4
        [1,  3,  5,  7,  9]
         arr[4]=9 > 7 → R = mid-1 = 3
         mid = (0+3)//2 = 1 → arr[1] = 3

Step 2:
                 L   R
                 2   3
                [5,  7]
         arr[1]=3 < 7 → L = mid+1 = 2
         mid = (2+3)//2 = 2 → arr[2] = 5

Step 3:
                     L=R
                      3
                     [7]
         arr[2]=5 < 7 → L = mid+1 = 3
         mid = (3+3)//2 = 3 → arr[3] = 7

Step 4: arr[3] = 7 == target ✓ FOUND at index 3

Total comparisons: 4 (vs 10 for linear scan)
```

### The Three Binary Search Templates

The classic binary search finds an exact match. But many interview problems require variations: find the leftmost match, the rightmost match, or "search on answer" (binary search on the result space, not the array).

```python
# ── TEMPLATE 1: Exact Match ───────────────────────────────────────────────────
def binary_search_exact(nums, target):
    """Find target in sorted array. Returns index or -1."""
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (right - left) // 2  # avoid integer overflow

        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


# ── TEMPLATE 2: Find Leftmost (Lower Bound) ───────────────────────────────────
def lower_bound(nums, target):
    """
    Find the leftmost index where nums[i] >= target.
    If target doesn't exist, returns index of first element > target.
    Use for: "find first occurrence", "count elements < target"
    """
    left, right = 0, len(nums)  # Note: right = len(nums), not len-1

    while left < right:  # Note: strict <, not <=
        mid = left + (right - left) // 2
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid  # Note: right = mid, not mid-1

    return left  # left == right when loop ends


# ── TEMPLATE 3: Search on Answer ─────────────────────────────────────────────
def search_on_answer_template(lo, hi, feasibility_check):
    """
    Binary search over the ANSWER SPACE, not the array.
    Use when: "find minimum X such that condition(X) is True"
    The condition must be monotonic: False...False...True...True

    Examples:
    - "Minimum speed to arrive on time"
    - "Koko eating bananas — minimum piles per hour"
    - "Split array — minimum largest sum"
    """
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if feasibility_check(mid):
            hi = mid       # mid might be the answer, don't exclude it
        else:
            lo = mid + 1   # mid is too small

    return lo  # lo == hi == the minimum feasible answer


def koko_eating_bananas(piles, h):
    """
    Minimum eating speed to eat all bananas in h hours.
    Binary search on the speed (1 to max(piles)).
    """
    import math

    def can_eat(speed):
        hours_needed = sum(math.ceil(p / speed) for p in piles)
        return hours_needed <= h

    lo, hi = 1, max(piles)
    return search_on_answer_template(lo, hi, can_eat)
```

### The "Hot/Cold" Mental Model

```
Problem: Find minimum speed k such that can_finish(k) is True.

Speeds:    1   2   3   4   5   6   7   8   9   10
can_eat:   F   F   F   F   T   T   T   T   T   T
                       │
                       └─── answer is here (first True)

Binary search converges:
  lo=1, hi=10, mid=5  → can_eat(5)=True  → hi=5
  lo=1, hi=5,  mid=3  → can_eat(3)=False → lo=4
  lo=4, hi=5,  mid=4  → can_eat(4)=False → lo=5
  lo=5, hi=5 → loop ends, return 5

The key: MONOTONICITY. Once the condition becomes True, it stays True.
If can_eat(k) is True, then can_eat(k+1) is also True.
```

---

## 8. Graph — BFS vs DFS Visual

### Side-by-Side Traversal on the Same Graph

```
Graph (undirected):
    1 ─── 2 ─── 5
    │     │
    3 ─── 4
          │
          6

Adjacency list:
  1: [2, 3]
  2: [1, 4, 5]
  3: [1, 4]
  4: [2, 3, 6]
  5: [2]
  6: [4]

─────────────────────────────────────────────────────────
BFS from node 1 (uses QUEUE):

Queue: [1]        Visited: {1}
  Process 1 → add 2, 3
Queue: [2, 3]     Visited: {1,2,3}
  Process 2 → add 4, 5 (1 already visited)
Queue: [3, 4, 5]  Visited: {1,2,3,4,5}
  Process 3 → add nothing new (1,4 already visited)
Queue: [4, 5]
  Process 4 → add 6 (2,3 already visited)
Queue: [5, 6]
  Process 5 → nothing new
Queue: [6]
  Process 6 → nothing new
Queue: []

BFS Order: 1 → 2 → 3 → 4 → 5 → 6
           ^   ↑   ↑   ↑       ↑
          d=0  d=1 d=1 d=2    d=3

BFS gives SHORTEST PATH distances from start node.

─────────────────────────────────────────────────────────
DFS from node 1 (uses STACK / recursion):

Stack: [1]        Visited: {1}
  Push neighbors of 1 → push 2, push 3 (3 pushed last = first out)
Stack: [2, 3]
  Pop 3 → visited. Push neighbors: 4 (1 visited)
Stack: [2, 4]
  Pop 4 → visited. Push neighbors: 6 (2,3 visited)
Stack: [2, 6]
  Pop 6 → visited. No unvisited neighbors.
Stack: [2]
  Pop 2 → visited. Push neighbors: 5 (1,4 visited)
Stack: [5]
  Pop 5 → visited. No unvisited neighbors.
Stack: []

DFS Order: 1 → 3 → 4 → 6 → 2 → 5
           (goes deep before going wide)

─────────────────────────────────────────────────────────
COMPARISON:

BFS:   1 ─── 2 ─── 4 ─── 6
              └─── 5
       └─── 3

DFS:   1 ─── 3 ─── 4 ─── 6
              └─── 2 ─── 5

BFS visits ALL nodes at distance 1 before distance 2.
DFS goes as DEEP as possible before backtracking.
```

### Code Templates

```python
from collections import deque


def bfs(graph, start):
    """BFS: explores level by level. Use for shortest paths."""
    visited = {start}
    queue = deque([start])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order


def dfs_iterative(graph, start):
    """DFS with explicit stack: explores deep paths first."""
    visited = set()
    stack = [start]
    order = []

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)

        # Add neighbors (in reverse for consistent order)
        for neighbor in reversed(graph[node]):
            if neighbor not in visited:
                stack.append(neighbor)

    return order


def dfs_recursive(graph, node, visited=None, order=None):
    """DFS with recursion: more elegant but risks stack overflow."""
    if visited is None:
        visited = set()
        order = []

    visited.add(node)
    order.append(node)

    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited, order)

    return order
```

---

## 9. Interval Problems Pattern

### The Visual Problem

Intervals feel abstract until you draw them on a timeline. Once you draw them, merging, insertion, and overlap detection become visual and obvious.

```
Intervals: [[1,3], [2,6], [8,10], [15,18]]

Draw on timeline:
0    1    2    3    4    5    6    7    8    9    10   15   18
     ├────────┤
          ├───────────────┤
                               ├────────┤
                                             ├──────────┤

Overlap check:
  [1,3] and [2,6]: 2 <= 3 → OVERLAP → merge to [1,6]
  [1,6] and [8,10]: 8 > 6 → NO OVERLAP → keep separate
  [8,10] and [15,18]: 15 > 10 → NO OVERLAP → keep separate

After merge:
0    1    2    3    4    5    6    7    8    9    10   15   18
     ├───────────────────────┤
                               ├────────┤
                                             ├──────────┤

Result: [[1,6], [8,10], [15,18]]
```

### ASCII: Merge Intervals Step by Step

```
Sorted intervals: [[1,3], [2,6], [8,10], [15,18]]

Step 1: result = []
        Take [1,3]: result = [[1,3]]

Step 2: Take [2,6]
        Last in result = [1,3]
        Start of new = 2 <= end of last = 3 → OVERLAP
        Merge: new end = max(3, 6) = 6
        result = [[1,6]]

Step 3: Take [8,10]
        Last in result = [1,6]
        Start of new = 8 > end of last = 6 → NO OVERLAP
        Add new interval
        result = [[1,6], [8,10]]

Step 4: Take [15,18]
        Last in result = [8,10]
        Start of new = 15 > end of last = 10 → NO OVERLAP
        Add new interval
        result = [[1,6], [8,10], [15,18]]

KEY INVARIANT: Always sort by start time first.
Then greedy: merge if overlap, else add new.
```

### Interval Code Patterns

```python
def merge_intervals(intervals):
    """
    Merge overlapping intervals.
    Sort by start, then greedily merge.
    Time: O(n log n) for sort + O(n) for merge = O(n log n)
    """
    if not intervals:
        return []

    intervals.sort(key=lambda x: x[0])
    result = [intervals[0]]

    for start, end in intervals[1:]:
        last_end = result[-1][1]
        if start <= last_end:
            # Overlap: extend the last interval's end
            result[-1][1] = max(last_end, end)
        else:
            # No overlap: start a new interval
            result.append([start, end])

    return result


def insert_interval(intervals, new_interval):
    """
    Insert new_interval into sorted non-overlapping intervals.
    Three phases: before, during (merge), after.
    Time: O(n)
    """
    result = []
    i = 0
    n = len(intervals)
    new_start, new_end = new_interval

    # Phase 1: add all intervals that end before new_interval starts
    while i < n and intervals[i][1] < new_start:
        result.append(intervals[i])
        i += 1

    # Phase 2: merge all overlapping intervals with new_interval
    while i < n and intervals[i][0] <= new_end:
        new_start = min(new_start, intervals[i][0])
        new_end = max(new_end, intervals[i][1])
        i += 1
    result.append([new_start, new_end])

    # Phase 3: add remaining intervals
    while i < n:
        result.append(intervals[i])
        i += 1

    return result


def meeting_rooms_ii(intervals):
    """
    Minimum meeting rooms needed for all intervals.
    Classic: sort by start, use min-heap to track end times.
    Time: O(n log n)
    """
    import heapq

    if not intervals:
        return 0

    intervals.sort(key=lambda x: x[0])
    heap = []  # min-heap of end times

    for start, end in intervals:
        if heap and heap[0] <= start:
            # Reuse a room (earliest-ending meeting is done)
            heapq.heapreplace(heap, end)
        else:
            # Need a new room
            heapq.heappush(heap, end)

    return len(heap)
```

---

## 10. Monotonic Stack

### The Story

Imagine you are standing in a line of people, and you want to know: "Who is the first taller person standing behind me?"

You could turn around and scan everyone behind you — O(n) per person, O(n²) total. Or you could use a smarter trick.

As you process people from left to right, maintain a stack. When a new (taller) person arrives, they are the answer for everyone in the stack who is shorter. Pop those shorter people — they have found their answer. Then push the new person.

This is the **monotonic stack**: a stack that maintains elements in a monotonically increasing (or decreasing) order.

### ASCII: Next Greater Element

```
Array: [4, 5, 2, 10, 8]
Find: for each element, what is the next greater element to its right?

Process 4:
  Stack: []  → push 4
  Stack: [4]

Process 5:
  5 > stack top (4) → 4's answer is 5, pop 4
  Stack: [] → push 5
  Stack: [5]
  answer[0] = 5  (next greater for element 4 is 5)

Process 2:
  2 < stack top (5) → push 2
  Stack: [5, 2]

Process 10:
  10 > stack top (2) → 2's answer is 10, pop 2
  Stack: [5]
  10 > stack top (5) → 5's answer is 10, pop 5
  Stack: [] → push 10
  Stack: [10]
  answer[2] = 10  (next greater for element 2 is 10)
  answer[1] = 10  (next greater for element 5 is 10)

Process 8:
  8 < stack top (10) → push 8
  Stack: [10, 8]

End of array: remaining elements in stack have no greater element
  answer[3] = -1  (10 has no next greater)
  answer[4] = -1  (8 has no next greater)

Final answers:
  Index:    0   1   2   3   4
  Value:    4   5   2  10   8
  NGE:      5  10  10  -1  -1

Visual walkthrough:
      4   5   2  10   8
  →   ↑   │       │
      └───┘       │
          ↑   ↑───┘
          └───┘
  (arrows point to next greater element)
```

### Decreasing Stack Visualization

```
The stack always maintains DECREASING order (bigger elements at bottom).
If new element is bigger, we pop smaller elements first (they found their answer).
If new element is smaller, just push.

                 STACK (bottom → top)
Start:           []
Push 4:          [4]
Push 5>4:        pop 4 (answer=5), push 5   → [5]
Push 2<5:        [5, 2]
Push 10>2:       pop 2 (answer=10), pop 5 (answer=10), push 10 → [10]
Push 8<10:       [10, 8]
End:             10 → answer=-1, 8 → answer=-1
```

### Monotonic Stack Patterns

```python
def next_greater_element(nums):
    """
    For each element, find the next greater element to its right.
    Monotonic decreasing stack.
    Time: O(n) — each element pushed and popped at most once.
    """
    n = len(nums)
    result = [-1] * n
    stack = []  # stores indices, maintains decreasing values

    for i in range(n):
        # Pop elements that are smaller than current
        while stack and nums[stack[-1]] < nums[i]:
            idx = stack.pop()
            result[idx] = nums[i]  # current element is the "next greater"
        stack.append(i)

    # Remaining elements in stack have no next greater → result stays -1
    return result


def largest_rectangle_in_histogram(heights):
    """
    Find the largest rectangle in a histogram.
    Classic monotonic stack problem.
    Time: O(n)
    """
    stack = []  # stores indices, maintains increasing heights
    max_area = 0
    heights = heights + [0]  # sentinel to flush remaining stack

    for i, h in enumerate(heights):
        start = i
        while stack and heights[stack[-1]] > h:
            idx = stack.pop()
            width = i - (stack[-1] + 1 if stack else 0)
            area = heights[idx] * width
            max_area = max(max_area, area)
            start = idx  # the rectangle extends back to here
        stack.append(i)

    return max_area


def daily_temperatures(temperatures):
    """
    For each day, how many days until a warmer temperature?
    Monotonic decreasing stack.
    """
    n = len(temperatures)
    result = [0] * n
    stack = []  # indices

    for i, temp in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < temp:
            idx = stack.pop()
            result[idx] = i - idx
        stack.append(i)

    return result
```

---

## Putting It All Together: Pattern Recognition Table

When you see this in a problem description... think this pattern:

```
╔════════════════════════════════════════╦════════════════════════════════╗
║  Problem Signal                        ║  Think Pattern                 ║
╠════════════════════════════════════════╬════════════════════════════════╣
║  "sorted array" + "find pair"          ║  Two Pointers                  ║
║  "sorted array" + "find value"         ║  Binary Search                 ║
║  "unsorted" + "find pair with sum"     ║  Hash Map (complement trick)   ║
║  "longest/shortest subarray where..."  ║  Sliding Window (variable)     ║
║  "max/min of all windows of size k"    ║  Sliding Window (fixed)        ║
║  "subarray sum equals k"               ║  Prefix Sum + Hash Map         ║
║  "root to leaf path"                   ║  DFS Top-Down                  ║
║  "diameter / max path between nodes"   ║  DFS Bottom-Up                 ║
║  "level by level"                      ║  BFS (level-order)             ║
║  "shortest path, unweighted"           ║  BFS                           ║
║  "shortest path, weighted"             ║  Dijkstra                      ║
║  "minimum spanning tree"               ║  Kruskal / Prim                ║
║  "connected components"                ║  Union-Find or DFS/BFS         ║
║  "topological order / dependency"      ║  Topological Sort (Kahn's)     ║
║  "cycle in directed graph"             ║  DFS with color (white/gray/black) ║
║  "overlapping subproblems"             ║  Dynamic Programming           ║
║  "all possible combinations/subsets"   ║  Backtracking                  ║
║  "locally optimal choice works"        ║  Greedy                        ║
║  "how many ways to..."                 ║  DP (count paths)              ║
║  "intervals / meetings / ranges"       ║  Sort + Greedy or Heap         ║
║  "next greater / previous smaller"     ║  Monotonic Stack               ║
║  "stream / real-time median"           ║  Two Heaps (min + max)         ║
║  "find k-th largest"                   ║  Min Heap of size k            ║
║  "prefix matching / autocomplete"      ║  Trie                          ║
║  "O(1) space constraint"               ║  Two Pointers / Floyd's Cycle  ║
║  "minimum speed/capacity to achieve"   ║  Binary Search on Answer       ║
╚════════════════════════════════════════╩════════════════════════════════╝
```

---

## Final Mental Model: Each Pattern as a Shape

Before finishing, here is a spatial way to remember each pattern:

```
Two Pointers:      ←─── ───→   (two ends moving toward each other)
                   or
                   ─→  ─→      (two pointers moving same direction)

Sliding Window:    [════]────   (a frame moving across the array)

Top-Down DFS:      ↓↓↓↓        (information flows from root to leaves)

Bottom-Up DFS:     ↑↑↑↑        (reports flow from leaves to root)

BFS:               ◉◉◉◉        (expanding rings/wavefronts)

DP:                ┌─┬─┬─┐    (table being filled cell by cell)
                   ├─┼─┼─┤
                   └─┴─┴─┘

Backtracking:      ├── ├──     (branching tree, branches pruned)
                   │   └──
                   └── ├──

Binary Search:     ←L  M  R→  (halving the search space)

Monotonic Stack:   ┃▊▊▊▊      (stack with decreasing/increasing height)
```

Each of these shapes represents a computational movement. When you encounter a problem, ask: which movement makes sense here? Does information need to flow inward (two pointers)? Does it need to spread outward (BFS)? Does it need to aggregate upward (bottom-up DFS)?

The answer tells you the pattern. The pattern tells you the code.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← 3-5 Years Experience](./3_5_years.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [0-2 Years Experience](./0_2_years.md) · [3-5 Years Experience](./3_5_years.md) · [Cheat Sheet](./cheatsheet.md) · [FAANG Level Questions](./faang_level_questions.md) · [Patterns](./patterns.md)
