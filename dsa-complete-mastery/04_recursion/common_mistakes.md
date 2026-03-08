# Recursion — Common Mistakes & Error Prevention Guide

> **Who this is for:** Engineers who understand *what* recursion is but keep shipping bugs in recursive solutions under interview pressure.

---

## Mistake #1: Missing Base Case

The function recurses forever because there is no condition that stops it.

**WRONG:**
```python
def countdown(n):
    print(n)
    countdown(n - 1)   # No base case — runs until Python kills it

countdown(5)
# 5, 4, 3, 2, 1, 0, -1, -2 ... RecursionError: maximum recursion depth exceeded
```

**CORRECT:**
```python
def countdown(n):
    if n <= 0:          # Base case: stop here
        return
    print(n)
    countdown(n - 1)

countdown(5)   # 5, 4, 3, 2, 1
```

**Why it fails:** Python maintains a call stack. Each recursive call adds a frame. Without a base case the stack grows until Python's default limit (~1000 frames) is hit and raises `RecursionError`.

**Test case that exposes the bug:**
```python
countdown(3)   # Crashes without base case
```

---

## Mistake #2: Wrong Base Case

The base case exists but returns the wrong value, corrupting every result that builds on it.

**WRONG:**
```python
def factorial(n):
    if n == 0:
        return 0    # WRONG: 0! = 1, not 0

    return n * factorial(n - 1)

print(factorial(5))   # 0 — everything gets multiplied by 0
```

**CORRECT:**
```python
def factorial(n):
    if n == 0:
        return 1    # 0! = 1 by definition

    return n * factorial(n - 1)

print(factorial(5))   # 120
```

**Why it fails:** The base case is the seed value. Every recursive call multiplies its result by the child call's result. A wrong seed (0 instead of 1) propagates through all multiplications and zeroes out the answer.

**Test cases that expose the bug:**
```python
assert factorial(0) == 1    # Direct base case test
assert factorial(1) == 1    # n=1 reduces to base case
assert factorial(5) == 120  # Full chain test
```

---

## Mistake #3: Not Returning the Recursive Call

The recursive call happens but its return value is discarded — the function silently returns `None`.

**WRONG:**
```python
def sum_list(nums, i=0):
    if i == len(nums):
        return 0
    nums[i] + sum_list(nums, i + 1)   # Result computed but never returned

print(sum_list([1, 2, 3]))   # None
```

**CORRECT:**
```python
def sum_list(nums, i=0):
    if i == len(nums):
        return 0
    return nums[i] + sum_list(nums, i + 1)   # Must propagate return value up

print(sum_list([1, 2, 3]))   # 6
```

**Why it fails:** In Python, a function with no `return` statement returns `None`. The arithmetic `nums[i] + sum_list(...)` evaluates to a number, but without `return`, that number is thrown away. The caller receives `None`, and `None + something` raises `TypeError` on the way back up — or everything silently becomes `None` if the base case is the first thing hit.

**Test case that exposes the bug:**
```python
result = sum_list([1, 2, 3])
assert result is not None, f"Got None instead of 6"
assert result == 6
```

---

## Mistake #4: Modifying Shared (Global) State

A global or outer-scope variable is mutated during recursion, causing results to be wrong on repeated calls or during backtracking.

**WRONG:**
```python
count = 0   # Global state

def count_nodes(node):
    global count
    if node is None:
        return
    count += 1
    count_nodes(node.left)
    count_nodes(node.right)

# First call works. Second call starts from the previous count.
count_nodes(root)   # count = 7
count_nodes(root)   # count = 14 — accumulated, not reset
```

**CORRECT:**
```python
def count_nodes(node):
    if node is None:
        return 0
    return 1 + count_nodes(node.left) + count_nodes(node.right)

# Each call is independent, returns a fresh result
result = count_nodes(root)   # 7, every time
```

**Why it fails:** Recursion inherently calls itself multiple times. Any side effect (mutating a global, appending to an outer list) accumulates across all those calls. The function is no longer pure and its output depends on call history.

**Test case that exposes the bug:**
```python
r1 = count_nodes(root)
r2 = count_nodes(root)
assert r1 == r2, f"Results differ: {r1} vs {r2}"
```

---

## Mistake #5: Off-by-One in Tree Recursion (Height of Leaf)

Inconsistent definition of "height" — does a leaf have height 0 or 1? Mixing both in the same function corrupts the result.

**WRONG (mixed convention):**
```python
def height(node):
    if node is None:
        return 0
    if node.left is None and node.right is None:
        return 1    # Leaf = 1, but None = 0. Now the +1 in the recursive case double-counts.

    return 1 + max(height(node.left), height(node.right))

# Single-node tree: height = 1 (correct)
# Two-node tree:   height = 2 ... but that's wrong if your problem defines it as 1
```

**CORRECT (height = number of edges, leaf = 0):**
```python
def height(node):
    if node is None:
        return -1   # Sentinel: None contributes -1 so leaf gets 0

    return 1 + max(height(node.left), height(node.right))

# Single-node tree: 1 + max(-1, -1) = 0   (leaf has 0 edges above it)
# Two-node tree:    1 + max(0, -1)   = 1
```

**CORRECT (height = number of nodes, leaf = 1):**
```python
def height(node):
    if node is None:
        return 0

    return 1 + max(height(node.left), height(node.right))

# Single-node tree: 1 + max(0, 0) = 1
# Two-node tree:    1 + max(1, 0) = 2
```

**Why it fails:** The two conventions are each internally consistent, but mixing them (leaf = 1 base AND None = 0 base in the same function) creates an incorrect +1 somewhere. Pick one convention and use it everywhere.

**Test case that exposes the bug:**
```python
# Single node
root = TreeNode(1)
assert height(root) == 0    # Edge-based convention
# OR
assert height(root) == 1    # Node-based convention
# The test must match your chosen convention consistently
```

---

## Mistake #6: Forgetting Python's Recursion Limit

Python's default recursion limit is ~1000. Deep inputs crash with `RecursionError` even when the logic is correct.

**WRONG (crashes on deep input):**
```python
def sum_range(n):
    if n == 0:
        return 0
    return n + sum_range(n - 1)

print(sum_range(10000))   # RecursionError: maximum recursion depth exceeded
```

**CORRECT option A — raise the limit (use sparingly):**
```python
import sys
sys.setrecursionlimit(20000)   # Only if you know the max depth

def sum_range(n):
    if n == 0:
        return 0
    return n + sum_range(n - 1)
```

**CORRECT option B — convert to iterative (preferred for production):**
```python
def sum_range(n):
    total = 0
    while n > 0:
        total += n
        n -= 1
    return total

print(sum_range(10000))   # 50005000, no crash
```

**Why it fails:** Python does not perform tail-call optimization. Every recursive call allocates a stack frame. At depth ~1000 Python raises `RecursionError` to prevent a true stack overflow. For interview problems, mention this trade-off even if you write the recursive version first.

**Test case that exposes the bug:**
```python
import sys
print(sys.getrecursionlimit())   # 1000 by default

# This will crash without limit adjustment:
sum_range(2000)
```

---

## Mistake #7: Redundant Recomputation (No Memoization)

The same subproblem is solved exponentially many times because results are never cached.

**WRONG (exponential time):**
```python
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)   # fib(n-2) recomputed by both branches

# fib(50) takes minutes — T(n) = T(n-1) + T(n-2) = O(2^n)
```

**CORRECT (linear time with memoization):**
```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

# fib(50) = 12586269025, instant
```

**Or manually:**
```python
def fib(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib(n - 1, memo) + fib(n - 2, memo)
    return memo[n]
```

**Why it fails:** Without caching, `fib(n)` recomputes `fib(n-2)` once directly AND again as part of computing `fib(n-1)`. This doubles work at every level, yielding O(2^n) time. With caching, each unique argument is computed exactly once: O(n) time.

**Test case that exposes the bug:**
```python
import time

start = time.time()
fib(40)   # Without memo: ~20 seconds. With memo: microseconds.
print(f"Elapsed: {time.time() - start:.3f}s")
```

---

## Mistake #8: Mutable Default Argument

Using a mutable object (list, dict) as a default parameter causes it to persist and accumulate across calls.

**WRONG:**
```python
def collect_paths(node, path=[], result=[]):   # BUG: mutable defaults
    if node is None:
        return
    path.append(node.val)
    if not node.left and not node.right:
        result.append(list(path))
    collect_paths(node.left, path, result)
    collect_paths(node.right, path, result)
    path.pop()
    return result

# First call: correct
# Second call: result already contains paths from the first call!
```

**CORRECT:**
```python
def collect_paths(node, path=None, result=None):
    if path is None:
        path = []
    if result is None:
        result = []

    if node is None:
        return result
    path.append(node.val)
    if not node.left and not node.right:
        result.append(list(path))
    collect_paths(node.left, path, result)
    collect_paths(node.right, path, result)
    path.pop()
    return result
```

**Why it fails:** Python evaluates default argument values once at function definition time, not at call time. The same list object is reused across all calls. Mutations (`.append`, `.pop`) made in one call are visible in every subsequent call.

**Test case that exposes the bug:**
```python
r1 = collect_paths(root)
r2 = collect_paths(root)
assert r1 == r2, "Results differ between calls — mutable default bug"
assert len(r2) == len(r1), f"r2 has {len(r2)} paths, expected {len(r1)}"
```

---

## Pre-Submission Checklist

Before submitting any recursive solution, answer these 5 questions:

- [ ] **1. Is there a base case for every terminal condition?**
  Check: empty input, `n=0`, `None` node, empty string, index out of bounds.

- [ ] **2. Does every code path return a value?**
  Trace the call manually. Confirm that the result of the recursive call is `return`ed, not just called.

- [ ] **3. Does the recursive call make progress toward the base case?**
  Each call must reduce `n`, advance an index, or move to a child node. If not, you have infinite recursion.

- [ ] **4. Could the input depth exceed ~1000?**
  If yes: either use `sys.setrecursionlimit`, convert to iterative, or mention this trade-off explicitly.

- [ ] **5. Are there repeated subproblems?**
  If the same arguments could appear more than once (e.g., Fibonacci, grid paths), add memoization. Otherwise you may have O(2^n) time.

**Bonus — mutable state check:**
  If you pass a list or dict as a parameter, confirm you are not using it as a default argument value. Use `None` as the default and initialize inside the function.
