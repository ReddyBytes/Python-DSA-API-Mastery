# Dynamic Programming — Cheatsheet

---

## DP Identification Checklist

Ask both questions — if YES to both, DP is likely the solution:
- **Overlapping subproblems?** Same subproblem solved multiple times?
- **Optimal substructure?** Optimal solution built from optimal sub-solutions?

Red flags that suggest DP:
- "number of ways to..."
- "minimum/maximum cost/path..."
- "can we achieve X?"
- "how many distinct..."
- Involves subsequences, subsets, or partitions

---

## Complexity Comparison

| Approach       | Time     | Space    | When to Use                     |
|----------------|----------|----------|---------------------------------|
| Recursion only | O(2^n)   | O(n)     | Never (exponential)             |
| Memoization    | O(states)| O(states)| Natural recursion, complex transitions |
| Tabulation     | O(states)| O(states)| Bottom-up, easier space optimization |
| Space-optimized| O(states)| O(1)~O(n)| When only last few rows needed  |

---

## Top-Down (Memoization) Template

```python
from functools import lru_cache

def solve(input):
    @lru_cache(maxsize=None)
    def dp(i, j, ...):           # state parameters
        # Base case
        if i == 0: return 0
        # Recurrence
        return min(dp(i-1, j), dp(i, j-1)) + cost[i][j]

    return dp(n, m)

# Manual memo dict (when state is unhashable or custom)
def solve_manual(input):
    memo = {}
    def dp(i, j):
        if (i, j) in memo: return memo[(i, j)]
        # Base case
        if i < 0: return 0
        # Recurrence
        memo[(i, j)] = dp(i-1, j) + dp(i, j-1)
        return memo[(i, j)]
    return dp(n, m)
```

**lru_cache vs manual dict:**
- `@lru_cache`: cleaner, auto-handles, can set maxsize; limited to hashable args
- `memo dict`: full control, can store any state, needed for mutable args

---

## Bottom-Up (Tabulation) Template

```python
def solve(n):
    dp = [0] * (n + 1)           # 1D example
    dp[0] = base_case_0
    dp[1] = base_case_1

    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]  # recurrence

    return dp[n]

# 2D tabulation
def solve_2d(m, n):
    dp = [[0] * (n+1) for _ in range(m+1)]
    # Initialize base cases
    for i in range(m+1): dp[i][0] = ...
    for j in range(n+1): dp[0][j] = ...

    for i in range(1, m+1):
        for j in range(1, n+1):
            dp[i][j] = f(dp[i-1][j], dp[i][j-1], ...)

    return dp[m][n]
```

---

## Space Optimization: 2D -> 1D

```python
# Original 2D: dp[i][j] depends only on dp[i-1][j] and dp[i][j-1]
# Replace with single 1D array, update in-place

dp = [0] * (n + 1)
for i in range(1, m + 1):
    new_dp = [0] * (n + 1)
    for j in range(1, n + 1):
        new_dp[j] = f(dp[j], new_dp[j-1])   # dp[j] = previous row
    dp = new_dp

# Or rolling two rows:
prev = [0] * (n + 1)
curr = [0] * (n + 1)
for i in range(1, m + 1):
    for j in range(1, n + 1):
        curr[j] = f(prev[j], curr[j-1])
    prev, curr = curr, [0] * (n + 1)
```

---

## DP Pattern Types

### Linear DP

| Problem             | State           | Transition                         |
|---------------------|-----------------|------------------------------------|
| Fibonacci           | dp[i]           | dp[i] = dp[i-1] + dp[i-2]         |
| Climbing Stairs     | dp[i]           | dp[i] = dp[i-1] + dp[i-2]         |
| House Robber        | dp[i]           | dp[i] = max(dp[i-1], dp[i-2]+nums[i]) |
| Max Subarray        | dp[i]           | dp[i] = max(nums[i], dp[i-1]+nums[i]) |

```python
# House Robber
def rob(nums):
    prev2, prev1 = 0, 0
    for n in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + n)
    return prev1
```

---

### Knapsack 0/1

```python
# dp[i][w] = max value using first i items with capacity w
def knapsack_01(weights, values, W):
    n = len(weights)
    dp = [0] * (W + 1)
    for i in range(n):
        for w in range(W, weights[i] - 1, -1):  # REVERSE to avoid reuse
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    return dp[W]
```

### Knapsack Unbounded

```python
def knapsack_unbounded(weights, values, W):
    dp = [0] * (W + 1)
    for w in range(1, W + 1):
        for i in range(len(weights)):
            if weights[i] <= w:
                dp[w] = max(dp[w], dp[w - weights[i]] + values[i])  # FORWARD
    return dp[W]
```

**Key difference:** 0/1 iterates weights in REVERSE; unbounded in FORWARD.

---

### LCS (Longest Common Subsequence)

```python
def lcs(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]
```

### LIS (Longest Increasing Subsequence)

```python
# O(n^2) DP
def lis_dp(nums):
    n = len(nums)
    dp = [1] * n
    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)

# O(n log n) — patience sort with bisect
from bisect import bisect_left
def lis_fast(nums):
    tails = []
    for n in nums:
        pos = bisect_left(tails, n)
        if pos == len(tails): tails.append(n)
        else: tails[pos] = n
    return len(tails)
```

---

### Interval DP

```python
# Matrix Chain Multiplication / Burst Balloons pattern
# dp[i][j] = optimal cost for interval [i, j]
def interval_dp(arr):
    n = len(arr)
    dp = [[0] * n for _ in range(n)]

    for length in range(2, n + 1):           # iterate over lengths
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float('inf')
            for k in range(i, j):            # split point
                dp[i][j] = min(dp[i][j], dp[i][k] + dp[k+1][j] + cost(i, k, j))

    return dp[0][n-1]
```

---

### Grid DP

```python
# Unique Paths / Minimum Path Sum
def min_path_sum(grid):
    m, n = len(grid), len(grid[0])
    dp = [[0]*n for _ in range(m)]
    dp[0][0] = grid[0][0]
    for i in range(1, m): dp[i][0] = dp[i-1][0] + grid[i][0]
    for j in range(1, n): dp[0][j] = dp[0][j-1] + grid[0][j]
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = min(dp[i-1][j], dp[i][j-1]) + grid[i][j]
    return dp[m-1][n-1]
```

---

### String DP (Edit Distance)

```python
def edit_distance(s, t):
    m, n = len(s), len(t)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1): dp[i][0] = i
    for j in range(n+1): dp[0][j] = j
    for i in range(1, m+1):
        for j in range(1, n+1):
            if s[i-1] == t[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j],    # delete
                                   dp[i][j-1],    # insert
                                   dp[i-1][j-1])  # replace
    return dp[m][n]
```

---

## State Definition Guide

| Pattern         | State Meaning                                | Base Case               |
|-----------------|----------------------------------------------|-------------------------|
| dp[i]           | answer for first i elements                  | dp[0] = 0 or 1          |
| dp[i][j]        | answer for s[i..j] or grid[i][j]             | diagonal or border      |
| dp[i][w]        | answer using i items with capacity w         | dp[0][*] = dp[*][0] = 0 |
| dp[i][j][k]     | answer at position i, j with state k         | varies                  |
| dp[mask]        | answer for subset encoded in bitmask         | dp[0] = 0               |

---

## Common DP Patterns at a Glance

| Pattern              | Key Idea                                      | Example Problem         |
|----------------------|-----------------------------------------------|-------------------------|
| Linear               | Each element depends on previous              | Fibonacci, Robber       |
| Two-sequence         | Match elements from two arrays                | LCS, Edit Distance      |
| Knapsack             | Include/exclude each item                     | 0/1 Knapsack, Coin Change |
| Interval             | Solve subintervals, combine                   | Burst Balloons           |
| Grid                 | Move through 2D grid with constraints         | Unique Paths             |
| Bitmask DP           | Track subset of items as binary mask          | TSP, Assignment          |
| State machine        | Multiple states with transitions              | Stock Buy/Sell           |

---

## Gotchas

- Off-by-one: `dp[i]` represents first `i` elements — index into array is `arr[i-1]`
- Reverse iteration in 0/1 knapsack inner loop (prevents item reuse)
- `@lru_cache` on nested function captures outer variables — be careful with mutation
- Clear cache between test cases: `dp.cache_clear()`
- `sys.setrecursionlimit(10**6)` for deep recursion in memoization
- Integer overflow not an issue in Python, but modular arithmetic: `dp[i] % MOD`
