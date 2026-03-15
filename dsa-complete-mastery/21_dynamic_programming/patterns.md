# Dynamic Programming — Pattern Recognition Guide

> **Core Idea**: Break a problem into overlapping subproblems. Store the result of each
> subproblem (memoization or tabulation) so it's computed only once. Trade space for time.
> Key insight: the answer to the full problem is composed of answers to smaller versions.

---

## 1. DP Identification Checklist

Ask these 5 questions in order before writing any code:

```
1. OPTIMIZATION or COUNTING?
   "Find maximum/minimum", "count the number of ways" → likely DP
   "Find all solutions", "generate all"               → Backtracking

2. OVERLAPPING SUBPROBLEMS?
   Can the same sub-state be reached via multiple paths?
   e.g., Fibonacci: fib(5) calls fib(4) and fib(3), and fib(4) calls fib(3) again.
   → YES → DP (without memoization, recursion recomputes the same things)

3. OPTIMAL SUBSTRUCTURE?
   Does the optimal solution to the whole problem contain optimal solutions to subproblems?
   → YES → DP applies

4. WHAT IS THE STATE?
   What information do I need to uniquely describe a subproblem?
   → State = the parameters of your recursive function
   → Fewer dimensions = better. Only include what's needed for transitions.

5. WHAT ARE THE TRANSITIONS?
   How does dp[i] relate to dp[i-1], dp[i-2], or dp[i][j-1], etc.?
   → Write the recurrence relation BEFORE writing code.
   → Draw it as arrows: dp[i] ← dp[i-1] ← dp[i-2]
```

**If you can answer all 5, you can solve it.** Most DP problems become straightforward
once the state definition and recurrence are clear.

---

## 2. How to Define DP State — 3 Rules

**Rule 1**: The state should capture exactly what you need to make decisions.
```
dp[i]    = answer for subproblem ending at / considering index i
dp[i][j] = answer for subproblem on arr1[0..i] and arr2[0..j]
dp[i][j] = answer for subproblem on interval [i..j]
dp[mask] = answer for subset represented by bitmask
```

**Rule 2**: The state should be minimal — don't include information you don't need.
```
Bad:  dp[i][j][k] where k is always computable from i and j
Good: dp[i][j]
```

**Rule 3**: The answer should be easily derivable from the state.
```
Often: return dp[n] or dp[n-1] or max(dp) or dp[0][n-1] or dp[(1<<n)-1]
```

---

## 3. Pattern 1 — Linear DP (1D Sequence)

**Shape**: `dp[i]` depends on `dp[i-1]` and/or `dp[i-2]`.
Think of it as: "what is the best answer considering elements up to index i?"

**Transition arrow diagram**:
```
dp[0] → dp[1] → dp[2] → dp[3] → ... → dp[n]
         ↑        ↑↑       ↑↑
      from i-1  from i-1 and i-2
```

**When to use**:
- Fibonacci-like sequences
- House robber (can't take adjacent elements)
- Climbing stairs (1 or 2 steps at a time)
- Coin change (min coins to make amount)
- Decode ways (number of ways to decode a string)

### Template — Two-Back Dependency

```python
def linear_dp_2back(arr):
    n = len(arr)
    if n == 0: return 0
    if n == 1: return arr[0]

    dp = [0] * n
    dp[0] = base_case_0
    dp[1] = base_case_1

    for i in range(2, n):
        dp[i] = transition(dp[i-1], dp[i-2], arr[i])
        # Common forms:
        # dp[i] = dp[i-1] + dp[i-2]              (Fibonacci / climbing stairs)
        # dp[i] = max(dp[i-1], dp[i-2] + arr[i]) (House Robber)

    return dp[n-1]
```

### Space-Optimized Linear DP

When `dp[i]` only uses `dp[i-1]` and `dp[i-2]`, reduce to two variables:

```python
def linear_dp_optimized(arr):
    prev2, prev1 = base_case_0, base_case_1

    for i in range(2, len(arr)):
        curr = transition(prev1, prev2, arr[i])
        prev2, prev1 = prev1, curr

    return prev1
```

### Worked Example — House Robber

**State**: `dp[i]` = max money robbing houses 0 through i.
**Recurrence**: `dp[i] = max(dp[i-1], dp[i-2] + nums[i])`
*(Skip this house vs rob this house — can't rob adjacent)*

```python
def rob(nums):
    n = len(nums)
    if n == 1: return nums[0]

    # Space-optimized: only need last two values
    prev2 = nums[0]
    prev1 = max(nums[0], nums[1])

    for i in range(2, n):
        curr = max(prev1,           # skip house i (best so far)
                   prev2 + nums[i]) # rob house i (best from 2 ago + this)
        prev2, prev1 = prev1, curr

    return prev1

# Trace: nums=[2,7,9,3,1]
# prev2=2, prev1=max(2,7)=7
# i=2: curr=max(7, 2+9)=11  → prev2=7,  prev1=11
# i=3: curr=max(11,7+3)=11  → prev2=11, prev1=11
# i=4: curr=max(11,11+1)=12 → prev2=11, prev1=12
# return 12
```

### Worked Example — Coin Change (Minimum Coins)

**State**: `dp[i]` = minimum coins to make amount i.
**Recurrence**: `dp[i] = min(dp[i - coin] + 1)` for each coin where coin <= i.

```python
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0   # base case: 0 coins needed to make amount 0

    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i and dp[i - coin] != float('inf'):
                dp[i] = min(dp[i], dp[i - coin] + 1)

    return dp[amount] if dp[amount] != float('inf') else -1

# coins=[1,2,5], amount=11
# dp[0]=0, dp[1]=1, dp[2]=1(via coin 2), dp[3]=2, dp[5]=1, dp[10]=2, dp[11]=3
# return 3
```

---

## 4. Pattern 2 — Knapsack Variants

**Shape**: One dimension is items, other is capacity/target.
`dp[i][w]` = best answer using first `i` items with weight limit `w`.

### Key Distinction — The Direction of the Inner Loop

```
0/1 Knapsack (each item used AT MOST ONCE):
  → Iterate capacity RIGHT TO LEFT (decreasing)
  → Using dp[w - weight] from the SAME iteration would mean reusing the item
  → Going right-to-left ensures dp[w - weight] is still from the PREVIOUS item

Unbounded Knapsack (items REUSABLE):
  → Iterate capacity LEFT TO RIGHT (increasing)
  → Using dp[w - weight] from the SAME iteration is DESIRED (reuse allowed)

Visual:
  0/1:       for w in range(capacity, weight-1, -1):  ← ← ← (right to left)
  Unbounded: for w in range(weight, capacity+1):       → → → (left to right)
```

### Template — 0/1 Knapsack (Space Optimized)

```python
def knapsack_01(weights, values, capacity):
    dp = [0] * (capacity + 1)

    for i in range(len(weights)):
        # REVERSE: ensure each item counted at most once
        # If we go forward, dp[w - weights[i]] might already include item i
        for w in range(capacity, weights[i] - 1, -1):
            dp[w] = max(dp[w],                          # skip item i
                        dp[w - weights[i]] + values[i]) # take item i

    return dp[capacity]
```

### Template — Unbounded Knapsack (Space Optimized)

```python
def knapsack_unbounded(weights, values, capacity):
    dp = [0] * (capacity + 1)

    for w in range(capacity + 1):
        for i in range(len(weights)):
            if weights[i] <= w:
                dp[w] = max(dp[w],                          # skip item i
                            dp[w - weights[i]] + values[i]) # take item i (reuse ok)
                # Forward direction: dp[w - weights[i]] may already include item i
                # This is INTENTIONAL for unbounded (items are reusable)

    return dp[capacity]
```

### Worked Example — Partition Equal Subset Sum

**Problem**: Can we split array into two equal-sum subsets?
**Reduction**: Does any subset sum to `total // 2`? (This is a 0/1 knapsack problem.)

```python
def can_partition(nums):
    total = sum(nums)
    if total % 2 != 0:
        return False

    target = total // 2
    dp = [False] * (target + 1)
    dp[0] = True   # empty subset makes sum 0

    for num in nums:
        for j in range(target, num - 1, -1):   # REVERSE: 0/1 knapsack
            dp[j] = dp[j] or dp[j - num]

    return dp[target]
```

### Knapsack Variants at a Glance

```
"subset sum"                 → 0/1 knapsack (boolean dp)
"partition equal subsets"    → 0/1 knapsack (subset sum to total/2)
"target sum"                 → 0/1 knapsack (count ways)
"coin change (min coins)"    → unbounded knapsack (each coin reusable)
"coin change (count ways)"   → unbounded knapsack (counting variant)
"word break"                 → unbounded knapsack (words reusable)
```

---

## 5. Pattern 3 — LCS / LIS Variants

### LCS — Longest Common Subsequence

**Shape**: 2D grid where `dp[i][j]` = LCS of first i chars of s1 and first j chars of s2.

**Transition arrow diagram**:
```
       "" a b c
    "" [0  0  0  0]
    a  [0  ↖  ←  ←]   ← s1[i-1] == s2[j-1]: take diagonal + 1
    c  [0  ↑  ↑  ↖]   ← s1[i-1] != s2[j-1]: max(up, left)
    e  [0  ↑  ↑  ↑ ]
```

**Recurrence**:
```
if s1[i-1] == s2[j-1]: dp[i][j] = dp[i-1][j-1] + 1
else:                   dp[i][j] = max(dp[i-1][j], dp[i][j-1])
```

```python
def lcs(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1    # characters match: extend LCS
            else:
                dp[i][j] = max(dp[i-1][j],      # skip text1[i-1]
                               dp[i][j-1])       # skip text2[j-1]

    return dp[m][n]
```

### LIS — Longest Increasing Subsequence

**O(n²) DP approach**:

**State**: `dp[i]` = length of longest increasing subsequence ENDING at index i.
**Recurrence**: `dp[i] = max(dp[j] + 1)` for all j < i where `nums[j] < nums[i]`.

```python
def lis_n2(nums):
    n = len(nums)
    dp = [1] * n    # every element is a subsequence of length 1

    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:           # can extend subsequence ending at j
                dp[i] = max(dp[i], dp[j] + 1)

    return max(dp)

# Time: O(n²)  |  Space: O(n)
```

**O(n log n) approach — Patience Sorting**:

```python
from bisect import bisect_left

def lis_nlogn(nums):
    """
    Patience sorting approach.
    tails[i] = smallest tail element of all increasing subsequences of length i+1.

    For each number:
    - If it's larger than all tails, extend the longest subsequence.
    - Otherwise, replace the first tail that's >= num (maintain sorted order).

    tails is always sorted. Use binary search to find position.
    """
    tails = []   # tails[i] = smallest ending value for IS of length i+1

    for num in nums:
        pos = bisect_left(tails, num)   # find leftmost position where tails[pos] >= num

        if pos == len(tails):
            tails.append(num)           # num extends longest subsequence
        else:
            tails[pos] = num            # replace: smaller tail = more room to extend

    return len(tails)

# Time: O(n log n)  |  Space: O(n)

# Example: nums = [10, 9, 2, 5, 3, 7, 101, 18]
# num=10: tails=[]     → pos=0=len → append → tails=[10]
# num=9:  tails=[10]   → pos=0     → replace → tails=[9]
# num=2:  tails=[9]    → pos=0     → replace → tails=[2]
# num=5:  tails=[2]    → pos=1=len → append  → tails=[2,5]
# num=3:  tails=[2,5]  → pos=1     → replace → tails=[2,3]
# num=7:  tails=[2,3]  → pos=2=len → append  → tails=[2,3,7]
# num=101:tails=[2,3,7]→ pos=3=len → append  → tails=[2,3,7,101]
# num=18: tails=[2,3,7,101] → pos=3 → replace → tails=[2,3,7,18]
# return len(tails) = 4
```

### LCS/LIS Recognition

```
"longest common subsequence"     → LCS 2D DP
"edit distance"                  → LCS variant (two sequences)
"shortest common supersequence"  → LCS (length = m + n - LCS)
"longest increasing subsequence" → LIS O(n²) or O(n log n)
"patience sorting"               → LIS O(n log n)
"longest non-decreasing subseq"  → LIS (change strict < to <=)
```

---

## 6. Pattern 4 — Grid DP

**Shape**: `dp[i][j]` = answer for cell (i, j), built from top-left to bottom-right.
Transitions come from adjacent cells: up `dp[i-1][j]`, left `dp[i][j-1]`, diagonal `dp[i-1][j-1]`.

**Transition arrow diagram**:
```
(0,0) → (0,1) → (0,2) → (0,3)
  ↓       ↓       ↓       ↓
(1,0) → (1,1) → (1,2) → (1,3)   ← dp[i][j] comes from ↑ or ←
  ↓       ↓       ↓       ↓
(2,0) → (2,1) → (2,2) → (2,3)
```

**When to use**:
- Number of paths in a grid
- Minimum cost path (only right or down moves)
- Maximum path sum in a grid
- Grid with obstacles

### Template — Grid DP (Minimum Path Sum)

```python
def grid_dp(grid):
    m, n = len(grid), len(grid[0])
    dp = [[0] * n for _ in range(m)]

    # Base case: top-left cell
    dp[0][0] = grid[0][0]

    # First row: can only come from left
    for j in range(1, n):
        dp[0][j] = dp[0][j-1] + grid[0][j]

    # First column: can only come from above
    for i in range(1, m):
        dp[i][0] = dp[i-1][0] + grid[i][0]

    # Fill rest: min cost from above or from left
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = grid[i][j] + min(dp[i-1][j],   # from above
                                         dp[i][j-1])   # from left

    return dp[m-1][n-1]
```

### Boundary Handling — Three Approaches

```python
# Approach 1: Fill borders explicitly (shown above)

# Approach 2: Use (m+1) x (n+1) DP table with sentinel row/col
dp = [[0] * (n + 1) for _ in range(m + 1)]
# Start filling from dp[1][1], referencing dp[0][j] and dp[i][0] as 0

# Approach 3: Check bounds inline
for i in range(m):
    for j in range(n):
        from_top  = dp[i-1][j] if i > 0 else float('inf')
        from_left = dp[i][j-1] if j > 0 else float('inf')
        dp[i][j] = grid[i][j] + min(from_top, from_left)
```

### Worked Example — Unique Paths

```python
def unique_paths(m, n):
    """Count paths from top-left to bottom-right (only right or down moves)."""
    dp = [[1] * n for _ in range(m)]   # first row and col all have 1 path

    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i-1][j] + dp[i][j-1]   # from above + from left

    return dp[m-1][n-1]

# Space-optimized: only need previous row
def unique_paths_optimized(m, n):
    dp = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j-1]   # dp[j] (from above) + dp[j-1] (from left)
    return dp[n-1]
```

---

## 7. Pattern 5 — Interval DP

**Shape**: `dp[i][j]` = answer for subarray/substring from index `i` to `j`.
Fill the table DIAGONALLY — shorter intervals first, then longer.

**Transition arrow diagram** (fill order):
```
Length 1:  dp[0][0], dp[1][1], dp[2][2], dp[3][3]    ← base cases (diagonal)
Length 2:  dp[0][1], dp[1][2], dp[2][3]
Length 3:  dp[0][2], dp[1][3]
Length 4:  dp[0][3]                                    ← final answer
```

**When to use**:
- "Burst balloons" — last element to process in a range
- "Matrix chain multiplication" — split a range at position k
- "Palindrome partitioning" — split string at position k
- "Strange printer" — print range [i,j] optimally

### Template — Interval DP (Fill by Length)

```python
def interval_dp(arr):
    n = len(arr)
    dp = [[0] * n for _ in range(n)]

    # Base case: intervals of length 1
    for i in range(n):
        dp[i][i] = base_case(arr[i])

    # Fill by increasing interval length
    for length in range(2, n + 1):               # length of interval
        for i in range(n - length + 1):          # start of interval
            j = i + length - 1                   # end of interval

            dp[i][j] = float('inf')              # or -inf for max problems
            for k in range(i, j):                # split point
                dp[i][j] = min(dp[i][j],
                               dp[i][k] + dp[k+1][j] + cost(arr, i, j, k))

    return dp[0][n-1]
```

### Worked Example — Burst Balloons

```python
def max_coins(nums):
    """
    Burst balloons to maximize coins.
    Bursting balloon i with neighbors l and r gives nums[l]*nums[i]*nums[r].

    KEY TRICK: Think of k as the LAST balloon to burst in range (left, right).
    When k is last, its neighbors are still left and right (not burst yet).
    """
    nums = [1] + nums + [1]     # pad with 1s so boundary balloons "exist"
    n = len(nums)
    dp = [[0] * n for _ in range(n)]

    # dp[left][right] = max coins from bursting all balloons strictly between left and right
    for length in range(2, n):
        for left in range(n - length):
            right = left + length

            # Try each balloon as the LAST to burst in (left, right)
            for k in range(left + 1, right):
                dp[left][right] = max(
                    dp[left][right],
                    dp[left][k] + nums[left] * nums[k] * nums[right] + dp[k][right]
                )

    return dp[0][n-1]
```

---

## 8. Pattern 6 — Bitmask DP

**Shape**: `dp[mask]` or `dp[mask][i]` where mask is a bitmask representing a subset.
Each bit in the mask represents whether element i is included (1) or excluded (0).

**When to use**:
- Problems with small input size (n ≤ 20)
- "Optimize over all subsets"
- "Travelling Salesman Problem (TSP)"
- "Assign tasks to workers" with n ≤ 16
- "Cover all elements exactly once" (set cover)

### Recognition Signals

```
"n ≤ 20 with exponential-looking problem"   → bitmask DP
"all subsets", "every combination"          → bitmask DP
"TSP" or "visit all cities"                 → bitmask DP
"assign workers to jobs (small n)"          → bitmask DP
"cover all requirements"                    → bitmask DP
```

### Bitmask Fundamentals

```python
# Represent a subset of {0, 1, 2, ..., n-1} as an integer
mask = 0b1011   # elements 0, 1, 3 are included (bit i = 1 means element i included)

# Check if element i is in the subset
is_in = (mask >> i) & 1         # True if bit i is set

# Add element i to the subset
new_mask = mask | (1 << i)      # set bit i

# Remove element i from the subset
new_mask = mask & ~(1 << i)     # clear bit i

# Iterate over all subsets of n elements
for mask in range(1 << n):      # 0 to 2^n - 1
    for i in range(n):
        if (mask >> i) & 1:
            pass                # element i is in this subset

# Full set (all n elements included)
full_mask = (1 << n) - 1        # binary: 111...1 (n ones)
```

### Template — Bitmask DP (TSP-style)

```python
def bitmask_dp_template(n, cost):
    """
    Visit all n nodes exactly once, minimizing total cost.
    dp[mask][i] = min cost to have visited exactly the nodes in mask,
                  ending at node i.
    """
    INF = float('inf')
    full = (1 << n) - 1
    dp = [[INF] * n for _ in range(1 << n)]

    # Base case: start at node 0 (just visiting node 0)
    dp[1][0] = 0   # mask=0b0001: only node 0 visited, currently at node 0

    for mask in range(1 << n):
        for last in range(n):
            if dp[mask][last] == INF:
                continue
            if not (mask >> last) & 1:    # last must be in the mask
                continue

            # Try extending to next unvisited node
            for nxt in range(n):
                if (mask >> nxt) & 1:     # already visited
                    continue

                new_mask = mask | (1 << nxt)
                new_cost = dp[mask][last] + cost[last][nxt]
                dp[new_mask][nxt] = min(dp[new_mask][nxt], new_cost)

    # Answer: visited all nodes, ending at any node
    return min(dp[full][i] for i in range(n))
```

### Worked Example — Minimum Cost to Assign Tasks

```python
def assign_min_cost(workers, tasks, cost):
    """
    n workers, n tasks. cost[i][j] = cost for worker i to do task j.
    Assign each task to exactly one worker. Minimize total cost.
    n <= 15.

    dp[mask] = min cost to assign tasks represented by mask,
               using the first popcount(mask) workers.
    """
    n = len(workers)
    dp = [float('inf')] * (1 << n)
    dp[0] = 0   # no tasks assigned, zero cost

    for mask in range(1, 1 << n):
        # Count which worker we're assigning to (0-indexed worker = number of 1s so far - 1)
        worker_idx = bin(mask).count('1') - 1  # next worker to assign

        for task in range(n):
            if not (mask >> task) & 1:
                continue   # task not in this mask

            prev_mask = mask ^ (1 << task)   # mask with this task removed
            if dp[prev_mask] != float('inf'):
                dp[mask] = min(dp[mask],
                               dp[prev_mask] + cost[worker_idx][task])

    return dp[(1 << n) - 1]
```

---

## 9. Pattern 7 — State Machine DP

**Shape**: Multiple states represent different "modes" or "phases".
`dp[i][state]` = best value at index i while in `state`.

**Transition arrow diagram** (stock with cooldown):
```
         BUY             SELL            COOLDOWN ENDS
REST  ---------> HELD ----------> SOLD -----------> REST
 ↑                 ↑                                  |
 |_________________| (stay held)                      |
                                     (stay resting) ←─┘
```

**When to use**:
- Stock buy/sell with cooldown or k-transaction limits
- Problems with alternating rules (odd/even, on/off)
- "States with transition costs between them"

### Recognition Signals

```
"buy and sell stock with cooldown"     → state machine (HELD, SOLD, REST)
"at most k transactions"               → state machine with k states
"with transaction fee"                 → state machine (HELD, SOLD)
"alternating states"                   → state machine DP
```

### Template — State Machine DP

```python
def state_machine_dp(arr):
    """
    Step 1: Identify all states (draw on paper first!)
    Step 2: Identify transitions between states
    Step 3: Initialize states (often -inf for "not yet reached")
    Step 4: Update all states each step
    """
    # Example states: HOLD (holding stock), SOLD (just sold), REST (cooldown/idle)
    HOLD, SOLD, REST = 0, 1, 2

    states = {
        HOLD: float('-inf'),   # haven't bought yet
        SOLD: 0,
        REST: 0
    }

    for price in arr:
        prev = states.copy()   # snapshot of previous states

        # State transitions (draw arrows first!):
        states[HOLD] = max(prev[HOLD],           # stay holding (no action)
                           prev[REST] - price)   # buy from REST state
        states[SOLD] = prev[HOLD] + price        # sell (must have been holding)
        states[REST] = max(prev[REST],            # stay resting
                           prev[SOLD])            # come off cooldown

    return max(states[SOLD], states[REST])
```

### Worked Example — Stock with Cooldown (LeetCode 309)

```python
def max_profit_cooldown(prices):
    """
    States:
      held = holding stock (bought, not yet sold)
      sold = just sold today (tomorrow is forced cooldown)
      rest = cooldown or idle (can buy tomorrow)

    Transitions:
      held → held: do nothing
      rest → held: buy today (only from rest, NOT from sold)
      held → sold: sell today
      sold → rest: cooldown forces rest
      rest → rest: idle again
    """
    held = float('-inf')   # max profit while holding (start: haven't bought)
    sold = 0               # max profit on day of selling
    rest = 0               # max profit while in cooldown/idle

    for price in prices:
        prev_held = held
        prev_sold = sold
        prev_rest = rest

        held = max(prev_held,           # continue holding
                   prev_rest - price)   # buy today (only from rest state)
        sold = prev_held + price        # sell today (must have been holding)
        rest = max(prev_rest,           # continue resting
                   prev_sold)           # come off cooldown

    return max(sold, rest)

# prices=[1,2,3,0,2]
# Day p=1: held=-1,   sold=0,  rest=0
# Day p=2: held=-1,   sold=1,  rest=0
# Day p=3: held=-1,   sold=2,  rest=1
# Day p=0: held=1,    sold=-1, rest=2
# Day p=2: held=1,    sold=3,  rest=2
# return max(3, 2) = 3
```

---

## 10. Space Optimization Patterns

### When to Optimize

```
2D DP where dp[i][j] uses only row i-1           → rolling array: O(n) space
2D DP where dp[i][j] uses only dp[i-1][j-1]      → two variables: O(1) space
1D DP where only last 2 values matter             → two variables: O(1) space
```

### Pattern — Rolling Array (2D → 1D)

```python
# Original 2D: O(m*n) space
dp = [[0] * (n+1) for _ in range(m+1)]
for i in range(1, m+1):
    for j in range(1, n+1):
        dp[i][j] = f(dp[i-1][j], dp[i][j-1])

# Optimized 1D: O(n) space
dp = [0] * (n + 1)
for i in range(1, m + 1):
    new_dp = [0] * (n + 1)
    for j in range(1, n + 1):
        new_dp[j] = f(dp[j],         # dp[i-1][j]:   same col, previous row
                      new_dp[j-1])   # dp[i][j-1]:   same row, previous col
    dp = new_dp
```

### Pattern — Knapsack Direction (In-Place)

```python
# 0/1 knapsack: iterate RIGHT TO LEFT (avoid reusing item in same pass)
for item in items:
    for j in range(capacity, item.weight - 1, -1):   # right to left ←
        dp[j] = max(dp[j], dp[j - item.weight] + item.value)

# Unbounded: iterate LEFT TO RIGHT (allow reuse in same pass)
for item in items:
    for j in range(item.weight, capacity + 1):        # left to right →
        dp[j] = max(dp[j], dp[j - item.weight] + item.value)
```

---

## 11. Problem → Pattern Mapping Table

| Problem | Pattern | State Shape | Key Recurrence |
|---------|---------|-------------|----------------|
| Climbing stairs | Linear DP | `dp[i]` | `dp[i-1] + dp[i-2]` |
| House robber | Linear DP | `dp[i]` | `max(dp[i-1], dp[i-2]+nums[i])` |
| Coin change (min coins) | Linear DP | `dp[amount]` | `min` over coins |
| Word break | Unbounded knapsack | `dp[i]` | `dp[j]` for valid word `[j..i]` |
| 0/1 knapsack | Knapsack | `dp[w]` (1D) | take or skip, iterate ← |
| Coin change (count ways) | Unbounded knapsack | `dp[amount]` | `+= dp[amount-coin]`, iterate → |
| Subset sum / partition | 0/1 knapsack | `dp[target]` (bool) | `OR` of `dp[j-num]` |
| LCS | Sequence (2D) | `dp[i][j]` | match/skip |
| Edit distance | Sequence (2D) | `dp[i][j]` | insert/delete/replace |
| LIS O(n²) | Linear DP | `dp[i]` | `max(dp[j]+1)` for `j<i` |
| LIS O(n log n) | Patience sort | `tails[]` | binary search |
| Unique paths | Grid DP | `dp[i][j]` | `from above + from left` |
| Min path sum | Grid DP | `dp[i][j]` | `min(above, left) + cost` |
| Matrix chain multiply | Interval DP | `dp[i][j]` | min over split k |
| Burst balloons | Interval DP | `dp[i][j]` | last balloon to pop |
| Palindrome partitioning | Interval DP | `dp[i][j]` | split at k |
| TSP | Bitmask DP | `dp[mask][i]` | extend to unvisited node |
| Task assignment | Bitmask DP | `dp[mask]` | assign one task at a time |
| Stock with cooldown | State machine | held/sold/rest | state transitions |
| Stock with k transactions | State machine | `dp[k][0/1]` | buy/sell states |

---

## 12. Quick Reference — Recurrence Shapes

```
LINEAR (1D):
  dp[i] = dp[i-1] + dp[i-2]              ← Fibonacci / climbing stairs
  dp[i] = max(dp[i-1], dp[i-2]+val[i])   ← House Robber
  dp[i] = min(dp[i-coin]+1)              ← Coin Change (min)

KNAPSACK (2D → 1D):
  0/1:       dp[w] = max(dp[w], dp[w-wt]+val)    iterate w RIGHT TO LEFT ←
  Unbounded: dp[w] = max(dp[w], dp[w-wt]+val)    iterate w LEFT TO RIGHT →

SEQUENCE (2 strings):
  match:    dp[i][j] = dp[i-1][j-1] + 1
  mismatch: dp[i][j] = max/min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]+1)

GRID:
  dp[i][j] = grid[i][j] + min/max(dp[i-1][j], dp[i][j-1])

INTERVAL:
  for length in 2..n:
    for i: j = i+length-1
      for k in i..j: dp[i][j] = f(dp[i][k], dp[k+1][j])

BITMASK:
  for mask in range(1 << n):
    for last in range(n): if (mask >> last) & 1:
      for nxt: if not (mask >> nxt) & 1:
        dp[mask | (1<<nxt)][nxt] = min(..., dp[mask][last] + cost[last][nxt])

STATE MACHINE:
  for each item:
    new_states[s] = max(transition from each prev_state to s)
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Real World Usage →](./real_world_usage.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
