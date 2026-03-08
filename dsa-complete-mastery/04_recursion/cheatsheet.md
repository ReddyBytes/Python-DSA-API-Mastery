# Recursion — Cheatsheet

## The Universal Recursion Template

```python
def solve(input, state):
    # 1. BASE CASE — stop recursion, return known answer
    if base_condition:
        return base_value

    # 2. RECURSIVE CASE — reduce problem, call self
    smaller_result = solve(smaller_input, updated_state)

    # 3. COMBINE — build answer from recursive result
    return combine(smaller_result, current_contribution)
```

```
Checklist before writing any recursive function:
  [ ] What is the base case? (empty input, n==0, single element)
  [ ] What does one recursive call return?
  [ ] Does each call make the problem strictly smaller?
  [ ] Will the base case always be reached?
```

---

## Call Stack Visualization

```
factorial(4)
  |
  +-- 4 * factorial(3)
            |
            +-- 3 * factorial(2)
                      |
                      +-- 2 * factorial(1)
                                |
                                +-- BASE: return 1
                      returns 2 * 1 = 2
            returns 3 * 2 = 6
  returns 4 * 6 = 24

Stack frames (LIFO) at deepest point:
  [ factorial(1) ]  <- top
  [ factorial(2) ]
  [ factorial(3) ]
  [ factorial(4) ]  <- bottom (first call)

Max depth = n => O(n) space on call stack
```

---

## Recursion vs Iteration Trade-offs

```
+---------------------+-------------------------------+----------------------------+
| Aspect              | Recursion                     | Iteration                  |
+---------------------+-------------------------------+----------------------------+
| Readability         | Often cleaner for trees/graphs| Clearer for simple loops   |
| Stack space         | O(depth) implicit call stack  | O(1) usually              |
| Python limit        | 1000 frames default           | No limit                   |
| Performance         | Function call overhead        | Slightly faster            |
| Tail call opt.      | NOT done by CPython           | N/A                        |
| Debugging           | Harder (deep stacks)          | Easier                     |
| Memoization         | Easy with @lru_cache          | Manual cache dict          |
+---------------------+-------------------------------+----------------------------+

Rule of thumb:
  Trees / graphs / divide-and-conquer => recursion is natural
  Simple linear scans / arithmetic    => iteration preferred
  Deep input (n > 10^4)               => convert to iteration or increase limit
```

---

## Tail Recursion

```python
# NOT tail-recursive (Python does not optimize this anyway):
def factorial(n):
    if n == 0: return 1
    return n * factorial(n - 1)   # multiplication AFTER recursive call

# Tail-recursive (accumulator pattern):
def factorial_tail(n, acc=1):
    if n == 0: return acc
    return factorial_tail(n - 1, n * acc)  # recursive call is LAST action

# CPython does NOT optimize tail calls — same O(n) stack depth.
# Convert to loop if stack depth is a concern:
def factorial_iter(n):
    acc = 1
    while n > 0:
        acc *= n
        n -= 1
    return acc
```

---

## Pattern 1 — Factorial / Fibonacci

```python
# Factorial — O(n) time, O(n) space (stack)
def factorial(n):
    if n <= 1: return 1
    return n * factorial(n - 1)

# Fibonacci — naive O(2^n) time (exponential — NEVER in interviews)
def fib_naive(n):
    if n <= 1: return n
    return fib_naive(n-1) + fib_naive(n-2)

# Fibonacci — memoized O(n) time, O(n) space
from functools import lru_cache
@lru_cache(maxsize=None)
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)

# Fibonacci — bottom-up DP O(n) time, O(1) space (best)
def fib_dp(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
```

---

## Pattern 2 — Tree Traversal

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# Inorder (left, root, right) — gives sorted order for BST
def inorder(node):
    if not node: return []
    return inorder(node.left) + [node.val] + inorder(node.right)

# Preorder (root, left, right) — useful for serialization
def preorder(node):
    if not node: return []
    return [node.val] + preorder(node.left) + preorder(node.right)

# Postorder (left, right, root) — useful for deletion, bottom-up info
def postorder(node):
    if not node: return []
    return postorder(node.left) + postorder(node.right) + [node.val]

# Tree height — classic divide and conquer
def height(node):
    if not node: return 0
    return 1 + max(height(node.left), height(node.right))
```

---

## Pattern 3 — Divide and Conquer

```python
# Template: split input, solve each half, merge results

def merge_sort(arr):
    if len(arr) <= 1:                   # base case
        return arr
    mid = len(arr) // 2
    left  = merge_sort(arr[:mid])       # solve left half
    right = merge_sort(arr[mid:])       # solve right half
    return merge(left, right)           # combine

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
# Time: O(n log n) | Space: O(n) + O(log n) stack
```

---

## Pattern 4 — Subsets (Power Set)

```python
# Generate all 2^n subsets — O(2^n) time and space

def subsets(nums):
    result = []

    def backtrack(start, current):
        result.append(current[:])      # add a copy of current subset

        for i in range(start, len(nums)):
            current.append(nums[i])    # choose
            backtrack(i + 1, current)  # explore
            current.pop()              # un-choose (backtrack)

    backtrack(0, [])
    return result

# Iterative (bit manipulation):
def subsets_iter(nums):
    n = len(nums)
    return [
        [nums[j] for j in range(n) if i & (1 << j)]
        for i in range(1 << n)         # 1<<n == 2^n
    ]
```

---

## Pattern 5 — Permutations

```python
# Generate all n! permutations — O(n * n!) time

def permutations(nums):
    result = []

    def backtrack(current, remaining):
        if not remaining:
            result.append(current[:])
            return
        for i in range(len(remaining)):
            current.append(remaining[i])
            backtrack(current, remaining[:i] + remaining[i+1:])
            current.pop()

    backtrack([], nums)
    return result

# Swap-based in-place (more efficient):
def permutations_swap(nums):
    result = []
    def backtrack(start):
        if start == len(nums):
            result.append(nums[:])
            return
        for i in range(start, len(nums)):
            nums[start], nums[i] = nums[i], nums[start]
            backtrack(start + 1)
            nums[start], nums[i] = nums[i], nums[start]
    backtrack(0)
    return result
```

---

## Memoization Template with lru_cache

```python
import sys
from functools import lru_cache

sys.setrecursionlimit(10**5)    # increase if needed (default = 1000)

# Decorator approach — automatically caches results by arguments
@lru_cache(maxsize=None)        # None = unlimited cache size
def dp(i, j, state):
    if base_condition:
        return base_value
    # arguments MUST be hashable (int, str, tuple — NOT list/dict)
    return min(dp(i-1, j, state), dp(i, j-1, state)) + cost[i][j]

# Clear cache if needed (e.g., between test cases):
dp.cache_clear()

# Manual memo dict (when args are unhashable or need more control):
memo = {}
def dp_manual(i, j):
    if (i, j) in memo:
        return memo[(i, j)]
    # ... compute result ...
    memo[(i, j)] = result
    return result
```

---

## Space Complexity of Recursion

```
+------------------------------+----------------+------------------------------+
| Recursion type               | Stack depth    | Example                      |
+------------------------------+----------------+------------------------------+
| Linear recursion             | O(n)           | factorial(n), fib(n)         |
| Binary tree (balanced)       | O(log n)       | height of balanced BST       |
| Binary tree (skewed)         | O(n)           | height of degenerate tree    |
| Merge sort                   | O(log n)       | depth of split tree          |
| Backtracking (subsets)       | O(n)           | depth = subset length        |
| DFS on graph                 | O(V)           | worst case all vertices      |
+------------------------------+----------------+------------------------------+

Stack frame holds: local variables, parameters, return address
=> Each frame is O(1) space, total = O(depth) * O(1) = O(depth)
```

---

## Python Recursion Limits & When Recursion Fails

```python
import sys
sys.getrecursionlimit()         # default: 1000
sys.setrecursionlimit(10**5)    # increase for deeper recursion

# Python DOES NOT optimize tail calls — always uses O(depth) stack space
# RecursionError: maximum recursion depth exceeded
```

```
When recursion will fail in interviews:
  - n > 10^4 and recursion depth is O(n) => likely RecursionError
  - Tree with n = 10^5 nodes, skewed => stack overflow
  - Fibonacci with n > 40 without memoization => TLE (2^n calls)

Fixes:
  1. sys.setrecursionlimit(n + 10)  — quick but fragile
  2. Convert to iterative + explicit stack  — robust
  3. Memoize with @lru_cache  — fixes TLE, not stack depth
  4. Use bottom-up DP  — avoids recursion entirely

Explicit stack (DFS without recursion):
  stack = [start]
  while stack:
      node = stack.pop()
      # process node
      stack.extend(node.children)
```

---

## Gotchas / Traps

```
1. Missing base case => infinite recursion => RecursionError
2. Base case never reached => same as above (check: does input always shrink?)
3. Mutable default argument in recursive call:
   WRONG:  def f(arr=[]):  — same list object reused across calls
   RIGHT:  def f(arr=None): arr = arr or []
4. @lru_cache requires hashable arguments — lists/dicts will raise TypeError
   Convert list to tuple before passing to memoized function
5. lru_cache does NOT reset between test runs — call dp.cache_clear()
6. Returning before appending (subsets pattern):
   Always append a COPY: result.append(current[:])  not result.append(current)
7. Forgetting to undo state in backtracking (the un-choose step):
   current.pop()  MUST be called after every recursive call that appended
```
