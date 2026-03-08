# Dynamic Programming — Common Mistakes & Error Prevention Guide

> **Who this is for:** Engineers who understand memoization and tabulation conceptually but keep writing DP solutions that produce wrong answers, index errors, or TLE due to subtle state and transition mistakes.

---

## Mistake #1: Wrong State Definition

A vague or incorrect `dp[i]` definition means you cannot write a correct transition. The definition must be an unambiguous English sentence before you write a single line of code.

**WRONG (vague definition leads to wrong code):**
```python
# Problem: Longest Increasing Subsequence
# Bad definition: dp[i] = "something about the subsequence ending at i"

def lis(nums):
    n = len(nums)
    dp = [0] * n      # What does 0 mean? Unclear.
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)   # dp[j]=0 for first element is wrong
    return max(dp)    # Returns 3 for [10,9,2,5,3,7,101,18] — wrong, should be 4
```

**CORRECT (precise definition drives correct code):**
```python
# DEFINITION: dp[i] = length of the longest increasing subsequence
#             that ENDS at index i (nums[i] is the last element)

def lis(nums):
    n = len(nums)
    dp = [1] * n      # Every element alone is a subsequence of length 1

    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)

    return max(dp)    # Returns 4 for [10,9,2,5,3,7,101,18] — correct

# nums = [10,9,2,5,3,7,101,18]
# dp   = [ 1,1,1,2,2,3,  4, 4]
```

**Why it fails:** Without a precise definition, the base case initialization is guesswork. In the bad version, `dp[i] = 0` means "no subsequence" — but every element forms a length-1 subsequence, so the base value must be 1. Writing the definition first forces you to get the base case right.

**Test case:**
```python
assert lis([10, 9, 2, 5, 3, 7, 101, 18]) == 4
assert lis([0, 1, 0, 3, 2, 3]) == 4
assert lis([7, 7, 7, 7]) == 1
```

---

## Mistake #2: Wrong Base Case Initialization

Initializing `dp[0]` or `dp[1]` with the wrong value corrupts every state that depends on them, especially in 1-indexed problems.

**WRONG:**
```python
# Problem: Climbing stairs — reach step n using 1 or 2 steps
def climb_stairs(n):
    dp = [0] * (n + 1)
    dp[1] = 1
    # dp[0] stays 0 — but "0 ways to reach step 0" is wrong for the transition
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]   # dp[2] = dp[1] + dp[0] = 1 + 0 = 1 (wrong, should be 2)
    return dp[n]

print(climb_stairs(2))   # 1 — wrong, answer is 2
```

**CORRECT:**
```python
def climb_stairs(n):
    if n == 1:
        return 1
    dp = [0] * (n + 1)
    dp[1] = 1   # 1 way to reach step 1 (one single step)
    dp[2] = 2   # 2 ways to reach step 2 (1+1 or 2)
    for i in range(3, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]

# Or equivalently initialize dp[0] = 1 as "empty path":
def climb_stairs_v2(n):
    dp = [0] * (n + 1)
    dp[0] = 1   # 1 way to stand at ground (do nothing)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]

print(climb_stairs(2))    # 2
print(climb_stairs(5))    # 8
```

**Test case:**
```python
assert climb_stairs(1) == 1
assert climb_stairs(2) == 2
assert climb_stairs(3) == 3
assert climb_stairs(5) == 8
```

---

## Mistake #3: Transition Accesses Wrong Index

The transition formula looks correct but accesses `dp[i-2]` when `i=1`, causing an `IndexError` or using index 0 (which may be semantically wrong).

**WRONG:**
```python
def rob(nums):
    n = len(nums)
    dp = [0] * n
    dp[0] = nums[0]
    # No guard for i=1 — dp[i-2] = dp[-1] accesses the LAST element
    for i in range(1, n):
        dp[i] = max(dp[i-1], nums[i] + dp[i-2])
        #                              ^^^^^^^^ When i=1: dp[-1] = dp[n-1], WRONG value

print(rob([2, 7, 9, 3, 1]))   # May give wrong answer due to dp[-1] wrapping
```

**CORRECT:**
```python
def rob(nums):
    n = len(nums)
    if n == 1:
        return nums[0]
    dp = [0] * n
    dp[0] = nums[0]
    dp[1] = max(nums[0], nums[1])   # Handle i=1 explicitly
    for i in range(2, n):
        dp[i] = max(dp[i-1], nums[i] + dp[i-2])   # Now i>=2, so dp[i-2] is always valid
    return dp[-1]

assert rob([2, 7, 9, 3, 1]) == 12
```

**Rule:** Any time your transition uses `dp[i-k]` for `k >= 2`, either handle the first `k-1` iterations as special base cases or add `if i >= k else 0` guards.

**Test case:**
```python
assert rob([1, 2, 3, 1]) == 4
assert rob([2, 7, 9, 3, 1]) == 12
assert rob([1]) == 1       # Single element — avoid dp[-1] trap
assert rob([1, 2]) == 2    # Two elements — avoid dp[-1] trap
```

---

## Mistake #4: Forgetting the "Not Taking" Case in Knapsack

The 0/1 knapsack transition requires choosing the BETTER of taking the item or not taking it. Forgetting the "not take" branch computes the wrong maximum.

**WRONG:**
```python
def knapsack(weights, values, capacity):
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if weights[i-1] <= w:
                # Only considers taking the item — never considers skipping it
                dp[i][w] = values[i-1] + dp[i-1][w - weights[i-1]]
    return dp[n][capacity]
```

**CORRECT:**
```python
def knapsack(weights, values, capacity):
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            # Option 1: don't take item i
            dp[i][w] = dp[i-1][w]
            # Option 2: take item i (only if it fits)
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i][w], values[i-1] + dp[i-1][w - weights[i-1]])
    return dp[n][capacity]

weights = [1, 2, 3]
values  = [6, 10, 12]
assert knapsack(weights, values, 5) == 22
```

**Why it fails:** If item 1 fits but has low value, and item 2 (which doesn't fit but was already optimally used) is better, we need to carry forward the best answer seen so far. `dp[i-1][w]` is that carry-forward.

---

## Mistake #5: Wrong Loop Order in Knapsack

For 0/1 knapsack with space optimization (1D array), the inner loop MUST go from right to left. Going left to right re-uses items (converts it to unbounded knapsack).

**WRONG (acts as unbounded knapsack — item used multiple times):**
```python
def knapsack_1d_wrong(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for i in range(len(weights)):
        for w in range(weights[i], capacity + 1):  # Left to right: BUG
            dp[w] = max(dp[w], values[i] + dp[w - weights[i]])
    return dp[capacity]
```

**CORRECT (0/1 knapsack — each item used at most once):**
```python
def knapsack_1d(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for i in range(len(weights)):
        for w in range(capacity, weights[i] - 1, -1):  # Right to left: CORRECT
            dp[w] = max(dp[w], values[i] + dp[w - weights[i]])
    return dp[capacity]

weights = [1, 2, 3]
values  = [6, 10, 12]
assert knapsack_1d(weights, values, 5) == 22
```

**Why it fails:** When iterating left to right, `dp[w - weights[i]]` may already reflect item `i` being added at a smaller weight. This effectively allows item `i` to be added again. Iterating right to left ensures that when we update `dp[w]`, `dp[w - weights[i]]` still reflects the state WITHOUT item `i`.

**Memory aid:** 0/1 = right to left. Unbounded = left to right.

---

## Mistake #6: Modifying the Memo While Iterating

Using a memoization dictionary and invalidating or deleting entries mid-computation causes incorrect cache hits.

**WRONG:**
```python
memo = {}

def fib(n):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    result = fib(n-1) + fib(n-2)
    memo[n] = result
    memo.clear()   # BUG: clearing after each store defeats the purpose
    return result

print(fib(10))   # Exponential time — every call re-computes from scratch
```

**CORRECT:**
```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

# Or manual memo — never mutate or clear during a computation
memo = {}

def fib_manual(n):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib_manual(n-1) + fib_manual(n-2)
    return memo[n]
```

**Why it fails:** The memo is the whole point — it avoids recomputation. Clearing it during the same computation forces every subproblem to recompute, turning O(n) back into O(2^n).

---

## Mistake #7: 2D Grid DP — Missing Boundary Checks

Grid DP transitions access neighboring cells without verifying they are within bounds, causing `IndexError` on cells at the edges.

**WRONG:**
```python
def min_path_sum(grid):
    m, n = len(grid), len(grid[0])
    dp = [[0]*n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])
            # BUG: when i=0, dp[-1][j] = dp[m-1][j] (wrong row!)
            # BUG: when j=0, dp[i][-1] = dp[i][n-1] (wrong column!)
    return dp[m-1][n-1]
```

**CORRECT:**
```python
def min_path_sum(grid):
    m, n = len(grid), len(grid[0])
    dp = [[float('inf')]*n for _ in range(m)]
    dp[0][0] = grid[0][0]

    for i in range(m):
        for j in range(n):
            if i == 0 and j == 0:
                continue
            from_top  = dp[i-1][j] if i > 0 else float('inf')
            from_left = dp[i][j-1] if j > 0 else float('inf')
            dp[i][j] = grid[i][j] + min(from_top, from_left)

    return dp[m-1][n-1]

grid = [[1,3,1],[1,5,1],[4,2,1]]
assert min_path_sum(grid) == 7
```

**Test case:**
```python
assert min_path_sum([[1]]) == 1                     # Single cell
assert min_path_sum([[1,2],[3,4]]) == 7             # 2x2 grid
assert min_path_sum([[1,3,1],[1,5,1],[4,2,1]]) == 7 # Full example
```

---

## Mistake #8: Wrong Space Optimization — Rolling Array Overwrites Needed Values

Collapsing a 2D DP to 1D incorrectly can overwrite a value before it is read by the current row's transition.

**WRONG (for a grid DP where each cell needs values from above AND above-left):**
```python
def unique_paths_wrong(m, n):
    dp = [1] * n
    for i in range(1, m):
        for j in range(1, n):
            dp[j] = dp[j] + dp[j-1]
            # dp[j] = (paths from above) + (paths from left)
            # dp[j-1] was already UPDATED this row — it's paths[i][j-1], not paths[i-1][j-1]
            # This is actually CORRECT for this specific problem (no diagonal term needed)
            # But for problems needing dp[i-1][j-1], you must cache the old value:
```

**CORRECT (when you need the top-left diagonal value):**
```python
# Example: edit distance needs dp[i-1][j-1]
def edit_distance(word1, word2):
    m, n = len(word1), len(word2)
    dp = list(range(n + 1))   # dp[j] = edit distance for word1[:0] vs word2[:j]

    for i in range(1, m + 1):
        prev = dp[0]          # Cache dp[i-1][j-1] before it's overwritten
        dp[0] = i
        for j in range(1, n + 1):
            temp = dp[j]      # Save before overwriting (this is dp[i-1][j])
            if word1[i-1] == word2[j-1]:
                dp[j] = prev  # No operation needed — use dp[i-1][j-1]
            else:
                dp[j] = 1 + min(prev, dp[j], dp[j-1])
                #                prev=dp[i-1][j-1], dp[j]=dp[i-1][j], dp[j-1]=dp[i][j-1]
            prev = temp
    return dp[n]

assert edit_distance("horse", "ros") == 3
assert edit_distance("intention", "execution") == 5
```

---

## Mistake #9: Missing "No Solution" Case

`dp[n]` holds whatever was initialized (often 0 or infinity) when no valid path exists. Returning it directly gives a wrong answer.

**WRONG:**
```python
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for i in range(1, amount + 1):
        for c in coins:
            if c <= i:
                dp[i] = min(dp[i], dp[i-c] + 1)
    return dp[amount]   # Returns inf if no solution — caller gets inf, not -1
```

**CORRECT:**
```python
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for i in range(1, amount + 1):
        for c in coins:
            if c <= i:
                dp[i] = min(dp[i], dp[i-c] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1

assert coin_change([1, 5, 10], 11) == 2
assert coin_change([2], 3) == -1     # No solution — must return -1, not inf
assert coin_change([1], 0) == 0
```

---

## Mistake #10: Circular Dependency in State Transition

A state depends on itself (directly or indirectly), creating an infinite loop or always reading an uninitialized value.

**WRONG:**
```python
# Attempting to compute dp[i] using dp[i] itself
def bad_dp(n):
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i] + dp[i-1]   # dp[i] reads itself (always 0 on right side)
    return dp[n]
```

**CORRECT — ensure every state reads only already-computed states:**
```python
def good_dp(n):
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2] if i >= 2 else dp[i-1]
    return dp[n]
```

**Why it fails:** In tabulation, you must compute states in topological order — each state is computed only after all states it depends on. If state `i` depends on state `i`, there is no valid order. The fix is always to re-examine your recurrence and ensure it strictly moves backward in the state space.

**Diagnostic:** If your transition reads `dp[i]` while computing `dp[i]`, your recurrence is circular. Redefine the state or rewrite the transition.

---

## Pre-Submission Checklist

Before submitting any DP solution, answer these 7 questions:

- [ ] **1. Can I write the state definition in one precise English sentence?**
  e.g., "`dp[i]` = minimum cost to reach stair `i`." If you cannot, your state is wrong.

- [ ] **2. Are all base cases initialized correctly?**
  Check `dp[0]`, `dp[1]`, and `dp[0][0]`. Verify them by hand for `n=0`, `n=1`, and a 1-cell grid.

- [ ] **3. Does the transition access any index that could be negative or out of bounds?**
  If using `dp[i-2]`, guard with `if i >= 2`. If using `dp[i-1][j-1]`, guard with `if i > 0 and j > 0`.

- [ ] **4. For knapsack problems: does the inner loop go right-to-left (0/1) or left-to-right (unbounded)?**
  Mixing these up silently converts one problem type to the other.

- [ ] **5. If using a rolling array: do I cache the old `dp[j]` value before overwriting it?**
  Assign `prev = dp[j]` before the update when the transition needs the diagonal (top-left) value.

- [ ] **6. Is the "no solution" case handled?**
  If the answer could be "impossible," check whether `dp[n]` is still at its initial value (infinity or 0) and return -1 instead.

- [ ] **7. Are all states computed in the correct order?**
  Each `dp[i]` must be computed only after every state it depends on. Bottom-up iteration (small to large `i`) satisfies this for most problems. For 2D, ensure both `i` and `j` iterate in the right direction.
