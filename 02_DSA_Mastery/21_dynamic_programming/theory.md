<a id="top"></a>

# Dynamic Programming — The Art of Remembering Smartly

> If backtracking tries everything,
> Dynamic Programming avoids repeating work.
>
> DP is not about intelligence.
> It is about memory.

Dynamic Programming (DP) is:

- One of the most powerful algorithmic techniques
- One of the most confusing for beginners
- One of the most important interview topics

Let's break it slowly and clearly.

## 📖 Table of Contents

1. [Real Life Story — Climbing Stairs](#1-real-life-story)
2. [Why Normal Recursion Is Slow](#2-why-normal-recursion-is-slow)
3. [Core Idea of DP](#3-core-idea-of-dp)
4. [Two Requirements for DP](#4-two-requirements-for-dp)
5. [Two Ways to Implement DP](#5-two-ways-to-implement-dp)
6. [How to Identify DP Problems](#6-how-to-identify-dp-problems)
7. [Classic DP Problems](#7-classic-dp-problems)
8. [Time and Space Complexity](#8-time-and-space-complexity)
9. [DP vs Greedy](#9-dp-vs-greedy)
10. [DP vs Backtracking](#10-dp-vs-backtracking)
11. [Common DP Patterns](#11-common-dp-patterns)
12. [DP Dimensions — Choosing the Right State](#12-dp-dimensions)
13. [Mental Model](#13-mental-model)
14. [Step-by-Step DP Thinking Strategy](#14-step-by-step-dp-thinking-strategy)
15. [Real-World Applications](#15-real-world-applications)
16. [Final Understanding](#16-final-understanding)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
overlapping subproblems · optimal substructure · state definition · recurrence relation

**Should Learn** — Important for real projects, comes up regularly:
memoization (top-down) vs tabulation (bottom-up) · 1D DP · 2D DP · classic problems (knapsack, LCS, LIS, coin change)

**Good to Know** — Useful in specific situations, not always tested:
space optimization · edit distance (string DP) · bitmask DP intro

**Reference** — Know it exists, look up syntax when needed:
digit DP · DP on trees · convex hull trick · profile DP

<a id="1-real-life-story"></a>

# 1. Real Life Story — Climbing Stairs

Imagine you are climbing stairs.

You can take:

- 1 step
- 2 steps

Question:

In how many ways can you reach the top?

For 1 step:
1 way

For 2 steps:
(1+1) or (2)
2 ways

For 3 steps:

Ways to reach step 3 =
Ways to reach step 2 +
Ways to reach step 1

You reuse previous answers.

That is DP.

> 📝 **Practice:** [Q79 · explain-dynamic-programming](../dsa_practice_questions_100.md#q79--interview--explain-dynamic-programming)

> [↑ Back to Top](#top)

<a id="2-why-normal-recursion-is-slow"></a>

# 2. Why Normal Recursion Is Slow

Let's solve climbing stairs recursively.

```
f(n) = f(n-1) + f(n-2)
```

Recursion tree for n=5:

```
           f(5)
         /       \
      f(4)        f(3)
     /    \      /     \
  f(3)   f(2)  f(2)   f(1)
  /   \
f(2)  f(1)
```

Notice:

f(3) computed multiple times
f(2) computed multiple times

Redundant work.

Time becomes:
O(2^n)

Very slow.

## Visual: Call Tree Explosion

WITHOUT memoization — exponential work:

```
                        fib(5)
                       /       \
                   fib(4)       fib(3)
                  /     \       /    \
              fib(3)  fib(2) fib(2) fib(1)
              /    \    /  \   /  \
           fib(2) fib(1) fib(1) fib(0) fib(1) fib(0)
           /   \
        fib(1) fib(0)

  Nodes marked * are DUPLICATE computations:
  fib(3) computed 2×
  fib(2) computed 3×
  fib(1) computed 5×
  fib(0) computed 3×

  Total calls: 15  for fib(5)
  For fib(n): O(2^n) — doubles with each step!
```

WITH memoization — linear work:

```
                        fib(5)
                       /       \
                   fib(4)    [fib(3)=2] ← CACHE HIT
                  /     \
              fib(3)   [fib(2)=1] ← CACHE HIT
              /    \
           fib(2)  [fib(1)=1] ← CACHE HIT
           /    \
        fib(1)  fib(0)

  cache = {0:0, 1:1, 2:1, 3:2, 4:3, 5:5}

  Total NEW calls: 5  (one per unique subproblem)
  Time: O(n), Space: O(n)

  KEY INSIGHT: Store answers to subproblems.
               Never solve the same subproblem twice.
```

> [↑ Back to Top](#top)

<a id="3-core-idea-of-dp"></a>

# 3. Core Idea of DP

If subproblem repeats,
store result.

Reuse it.

That's it.

DP = Recursion + Memory

> 📝 **Practice:** [Q93 · predict-dp-table](../dsa_practice_questions_100.md#q93--logical--predict-dp-table)

> 📝 **Practice:** [Q6 — Two Requirements for DP](./practice.md#q6--identification--two-requirements-for-dp) · [Q7 — 6-Step Strategy](./practice.md#q7--dp-thinking--how-to-define-state)

> [↑ Back to Top](#top)

<a id="4-two-requirements-for-dp"></a>

# 4. Two Requirements for DP

DP works when:

1. Overlapping Subproblems
2. Optimal Substructure

Overlapping:
Same subproblem solved multiple times.

Optimal Substructure:
Optimal solution built from optimal subsolutions.

If these exist → use DP.

> [↑ Back to Top](#top)

<a id="5-two-ways-to-implement-dp"></a>

# 5. Two Ways to Implement DP

## Memoization (Top-Down)

Use recursion + cache.

Store result when first computed.

Example:

```python
memo = {}

def climb(n):
    if n <= 2:
        return n
    if n in memo:
        return memo[n]

    memo[n] = climb(n-1) + climb(n-2)
    return memo[n]
```

Time:
O(n)

**Common mistake — clearing the memo mid-computation:** Never call `memo.clear()` or delete entries while a recursive computation is in progress. Clearing the cache defeats memoization entirely and turns O(n) back into O(2^n). Use `@lru_cache(maxsize=None)` or a persistent dict that lives for the entire call.

> 📝 **Practice:** [Q55 · dp-memoization-tabulation](../dsa_practice_questions_100.md#q55--normal--dp-memoization-tabulation) · [Q85 · memoization-vs-tabulation](../dsa_practice_questions_100.md#q85--interview--memoization-vs-tabulation)

> 📝 **Practice:** [Q1 — Fibonacci Top-Down](./practice.md#q1--memoization--fibonacci-top-down)

## Tabulation (Bottom-Up)

Build solution from smallest case.

```python
dp = [0]*(n+1)
dp[1] = 1
dp[2] = 2

for i in range(3, n+1):
    dp[i] = dp[i-1] + dp[i-2]
```

Time:
O(n)

No recursion stack.

**Common mistake — wrong base case initialization:** If you set `dp[0] = 0` and rely on `dp[i] = dp[i-1] + dp[i-2]`, then `dp[2] = dp[1] + dp[0] = 1 + 0 = 1` — wrong, the answer is 2. Either set `dp[2] = 2` explicitly, or use `dp[0] = 1` as the "empty path" sentinel. Write the state definition first; it forces the correct base value.

> 📝 **Practice:** [Q2 — Climbing Stairs Bottom-Up](./practice.md#q2--tabulation--climbing-stairs-bottom-up) · [Q3 — O(1) Space](./practice.md#q3--space-optimization--climbing-stairs-o1-space)

## Visual: Memoization vs Tabulation

**Problem: Climbing stairs. n=5 stairs, take 1 or 2 steps at a time. How many ways?**

Memoization (Top-Down) — Recursive + Cache:

```
  ways(5) = ways(4) + ways(3)          ← "how do I reach 5?"
           ways(4) = ways(3) + ways(2)
                    ways(3) = ways(2) + ways(1)
                             ways(2) = ways(1) + ways(0)
                                      ways(1) = 1
                                      ways(0) = 1

  Fill in bottom-up as recursion unwinds:
  ways(0) = 1
  ways(1) = 1
  ways(2) = 2
  ways(3) = 3
  ways(4) = 5
  ways(5) = 8

  cache = {0:1, 1:1, 2:2, 3:3, 4:5, 5:8}
```

Tabulation (Bottom-Up) — Iterative + Table:

```
  Build the answer from the ground up, no recursion needed.

  stair:  0    1    2    3    4    5
  dp:    [1,   1,   ?,   ?,   ?,   ?]

  Fill left to right: dp[i] = dp[i-1] + dp[i-2]

  stair:  0    1    2    3    4    5
  dp:    [1,   1,   2,   ?,   ?,   ?]
                    ↑
                 1+1=2

  stair:  0    1    2    3    4    5
  dp:    [1,   1,   2,   3,   ?,   ?]
                         ↑
                      1+2=3

  stair:  0    1    2    3    4    5
  dp:    [1,   1,   2,   3,   5,   ?]
                              ↑
                           2+3=5

  stair:  0    1    2    3    4    5
  dp:    [1,   1,   2,   3,   5,   8]  ← Answer: 8
                                   ↑
                                3+5=8
```

```
┌─────────────────────┬─────────────────────────────┐
│  Memoization        │  Tabulation                  │
├─────────────────────┼─────────────────────────────┤
│  Top-down           │  Bottom-up                   │
│  Recursive          │  Iterative                   │
│  Lazy (only solves  │  Eager (solves all           │
│  needed subproblems)│  subproblems)                │
│  Natural if problem │  Better space optimization   │
│  structure is clear │  possible (rolling array)    │
└─────────────────────┴─────────────────────────────┘
```

> [↑ Back to Top](#top)

<a id="6-how-to-identify-dp-problems"></a>

# 6. How to Identify DP Problems

Look for:

- Count number of ways
- Minimum cost
- Maximum profit
- Longest subsequence
- Shortest path (with constraints)
- Subset problems
- Knapsack-like structure

If recursion has repeated calls → DP candidate.

> [↑ Back to Top](#top)

<a id="7-classic-dp-problems"></a>

# 7. Classic DP Problems

## Fibonacci

Base DP example.

## Climbing Stairs

Same pattern as Fibonacci.

## 0/1 Knapsack

Max value with limited capacity.

State:
dp[i][w] = best using first i items and capacity w.

Important 2D DP.

**Common mistake — forgetting the "not taking" branch:** The knapsack transition must compare taking item i against NOT taking it. Writing `dp[i][w] = values[i-1] + dp[i-1][w - weights[i-1]]` without the `max(dp[i-1][w], ...)` wrapper silently discards better solutions found by skipping the current item. Always set `dp[i][w] = dp[i-1][w]` first, then max it with the "take" option.

## Visual: Knapsack DP Table

```
  Items:
  ┌──────┬────────┬───────┐
  │ Item │ Weight │ Value │
  ├──────┼────────┼───────┤
  │  1   │   1    │   1   │
  │  2   │   3    │   4   │
  │  3   │   4    │   5   │
  │  4   │   5    │   7   │
  └──────┴────────┴───────┘
  Capacity W = 7

  dp[i][w] = max value using first i items with capacity w

  Rule:
    don't take item i: dp[i][w] = dp[i-1][w]
    take item i:       dp[i][w] = dp[i-1][w - weight[i]] + value[i]
    take the max of both options (only if w >= weight[i])

  Capacity:  0    1    2    3    4    5    6    7
  No items: [0,   0,   0,   0,   0,   0,   0,   0]
  Item 1:   [0,   1,   1,   1,   1,   1,   1,   1]
            ↑ wt=1,val=1: fits starting at w=1
  Item 2:   [0,   1,   1,   4,   5,   5,   5,   5]
            ↑ wt=3,val=4: at w=3, take item2(4) > don't(1)
  Item 3:   [0,   1,   1,   4,   5,   6,   6,   9]
            ↑ wt=4,val=5: at w=7, take3(dp[2][3]+5=4+5=9)>don't(5)
  Item 4:   [0,   1,   1,   4,   5,   7,   8,   9]
            ↑ wt=5,val=7: at w=5, take4(7) > don't(6)

  Answer: dp[4][7] = 9
  (Take item 2 with value 4 + item 3 with value 5 = 9, total weight = 3+4 = 7)
```

> 📝 **Practice:** [Q56 · dp-01-knapsack](../dsa_practice_questions_100.md#q56--design--dp-01-knapsack)

> 📝 **Practice:** [Q9 — 0/1 Knapsack 2D](./practice.md#q9--knapsack--01-knapsack-2d) · [Q10 — Space-Optimized](./practice.md#q10--knapsack--01-knapsack-space-optimized) · [Q17 — Partition Subset](./practice.md#q17--knapsack--partition-equal-subset-sum)

## Longest Common Subsequence (LCS)

Compare two strings.

State:
dp[i][j] = LCS of first i and j characters.

Classic 2D DP.

## Visual: LCS DP Table

```
  X = "ABCBDAB"   (rows)
  Y = "BDCAB"     (cols)

  Build dp[i][j] = length of LCS of X[0..i-1] and Y[0..j-1]

  Rule:
    if X[i-1] == Y[j-1]:  dp[i][j] = dp[i-1][j-1] + 1   ← diagonal + 1
    else:                  dp[i][j] = max(dp[i-1][j], dp[i][j-1])

        ""   B    D    C    A    B
   ""  [ 0,  0,   0,   0,   0,   0 ]
   A   [ 0,  0,   0,   0,   1,   1 ]
   B   [ 0,  1,   1,   1,   1,   2 ]
   C   [ 0,  1,   1,   2,   2,   2 ]
   B   [ 0,  1,   1,   2,   2,   3 ]
   D   [ 0,  1,   2,   2,   2,   3 ]
   A   [ 0,  1,   2,   2,   3,   3 ]
   B   [ 0,  1,   2,   2,   3,   4 ]  ← LCS length = 4

  Tracing back to find the actual LCS:
  Start at dp[7][5] = 4
    X[6]='B' == Y[4]='B' → take it, go diagonal to dp[6][4]
    X[5]='A' == Y[3]='A' → take it, go diagonal to dp[5][3]
    X[4]='D' == Y[1]='D' → take it, go diagonal to dp[4][1]
    X[3]='B' == Y[0]='B' → take it, go diagonal to dp[3][0]

  LCS = "BDAB"  (length 4)
```

> 📝 **Practice:** [Q57 · dp-lcs](../dsa_practice_questions_100.md#q57--normal--dp-lcs)

> 📝 **Practice:** [Q13 — LCS](./practice.md#q13--sequence-dp--longest-common-subsequence) · [Q20 — LCS Space-Optimized](./practice.md#q20--space-optimization--rolling-array-lcs)

## Longest Increasing Subsequence (LIS)

State:
dp[i] = longest increasing subsequence ending at i.

Advanced optimization possible.

## Visual: LIS — Patience Sorting Analogy

```
  Sequence: [10, 9, 2, 5, 3, 7, 101, 18]

  Patience Sorting Rules:
  - Place each card on the leftmost pile whose top card is >= current card
  - If no such pile exists, start a new pile

  Card 10: [10]
  Card  9: [9]          (9 < 10, replace 10)
  Card  2: [2]          (2 < 9, replace 9)
  Card  5: [2] [5]      (5 > 2, new pile)
  Card  3: [2] [3]      (3 < 5, replace 5)
  Card  7: [2] [3] [7]  (7 > 3, new pile)
  Card101: [2] [3] [7] [101]   (new pile)
  Card 18: [2] [3] [7] [18]    (18 < 101, replace)

  Number of piles = length of LIS = 4
  LIS = [2, 3, 7, 18] or [2, 3, 7, 101]

  The pile tops always form an increasing sequence.
  Binary search finds the right pile in O(log n).
  Total time: O(n log n)
```

Standard DP approach for comparison (O(n^2)):

```
  Sequence: [10, 9, 2, 5, 3, 7, 101, 18]
  Index:      0   1  2  3  4  5   6   7

  dp[i] = length of LIS ending at index i

  i=0: dp[0]=1               [10]→ LIS ending here: length 1
  i=1: dp[1]=1               [9] → nothing before < 9 that matters
  i=2: dp[2]=1               [2]
  i=3: dp[3]=2        2<5    [2,5]
  i=4: dp[4]=2        2<3    [2,3]
  i=5: dp[5]=3     2<7,3<7   [2,3,7] or [2,5,7]
  i=6: dp[6]=4  any<101      [2,3,7,101]
  i=7: dp[7]=4  7<18         [2,3,7,18]

  dp = [1, 1, 1, 2, 2, 3, 4, 4]
  Answer = max(dp) = 4
```

**Common mistake — wrong state definition for LIS:** Initializing `dp = [0] * n` instead of `dp = [1] * n` produces an answer of 3 instead of 4 for `[10,9,2,5,3,7,101,18]`. The definition is "LIS ending AT index i" — every single element alone is a valid subsequence of length 1, so every base value must be 1, not 0. Write the definition before the code.

> 📝 **Practice:** [Q58 · dp-lis](../dsa_practice_questions_100.md#q58--thinking--dp-lis)

> 📝 **Practice:** [Q14 — LIS O(n²)](./practice.md#q14--sequence-dp--longest-increasing-subsequence-on2) · [Q15 — LIS O(n log n)](./practice.md#q15--sequence-dp--lis-onlogn-patience-sorting)

## Coin Change

Minimum coins to make amount.

State:
dp[amount] = minimum coins.

Greedy fails here sometimes.
DP required.

**Common mistake — missing the "no solution" case:** When no combination of coins reaches the target, `dp[amount]` remains at `float('inf')`. Returning that directly gives the caller infinity instead of -1. Always guard: `return dp[amount] if dp[amount] != float('inf') else -1`.

> 📝 **Practice:** [Q59 · dp-coin-change](../dsa_practice_questions_100.md#q59--logical--dp-coin-change)

> 📝 **Practice:** [Q5 — Coin Change Min Coins](./practice.md#q5--linear-dp--coin-change-minimum-coins) · [Q8 — Count Ways](./practice.md#q8--linear-dp--coin-change-number-of-ways)

> [↑ Back to Top](#top)

<a id="8-time-and-space-complexity"></a>

# 8. Time and Space Complexity

DP often reduces:

Exponential → Polynomial

Example:

Fibonacci:
O(2^n) → O(n)

Knapsack:
O(nW)

DP trades space for speed.

> [↑ Back to Top](#top)

<a id="9-dp-vs-greedy"></a>

# 9. DP vs Greedy

Greedy:
Makes local decision.

DP:
Explores all options but stores results.

If greedy fails,
DP usually works.

> [↑ Back to Top](#top)

<a id="10-dp-vs-backtracking"></a>

# 10. DP vs Backtracking

Backtracking:
Explores all combinations.

DP:
Avoids recomputing overlapping subproblems.

DP is optimized backtracking.

> [↑ Back to Top](#top)

<a id="11-common-dp-patterns"></a>

# 11. Common DP Patterns

## 1D DP

Example:
Climbing stairs.

## Visual: 1D DP Dependency Arrows

Each cell depends on the previous two cells:

```
  dp[i] = dp[i-1] + dp[i-2]

  Index:   0    1    2    3    4    5    6    7
  dp:     [1,   1,   2,   3,   5,   8,  13,  21]

  Dependency arrows:
          ┌────┐ ┌────┐
          │    ↓ ↓    │
  [1,  1,  2,  3,  5,  8,  13,  21]
               ↑   ↑
               └───┤
                   │
          [1,  1,  2,  3,  ...]
                   ←  ←
          (dp[i] comes from dp[i-1] and dp[i-2])

  Space optimization: you only need the last 2 values!

  BEFORE (space O(n)):  [1, 1, 2, 3, 5, 8, 13, 21]
  AFTER  (space O(1)):  just keep prev=8, curr=13 → next=21
```

## 2D DP

Example:
LCS, knapsack.

## DP on Strings

Edit distance
Palindrome partitioning

> 📝 **Practice:** [Q16 — Edit Distance](./practice.md#q16--string-dp--edit-distance) · [Q25 — Palindrome Min Cuts](./practice.md#q25--string-dp--palindrome-minimum-cuts) · [Q29 — Word Break](./practice.md#q29--advanced--word-break)

## DP on Grid

Unique paths
Minimum path sum

## Visual: Grid DP — "Where Can I Come From?" Arrows

Problem: Count unique paths from top-left to bottom-right.
(Can only move right or down.)

```
  3×3 grid:

  ┌─────┬─────┬─────┐
  │  1  │  1  │  1  │   ← top row: only 1 way (always from left)
  ├─────┼─────┼─────┤
  │  1  │  2  │  3  │
  ├─────┼─────┼─────┤
  │  1  │  3  │  6  │
  └─────┴─────┴─────┘

  Filling dp[1][1]=2:         Filling dp[2][2]=6:

    ←  from (1,0)               ←  from (2,1) = 3
    ↑  from (0,1)               ↑  from (1,2) = 3
                                         total = 6
    [1] → [1] → [1]
     ↓  ↘  ↓  ↘  ↓
    [1] → [2] → [3]
     ↓  ↘  ↓  ↘  ↓
    [1] → [3] → [6]

  Every cell = sum of cell above + cell to the left.
  Arrows point FROM sources TO destination.
  "To reach me, I could have come from above or from the left."
```

**Common mistake — missing boundary checks in grid DP:** Writing `dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])` without guards causes `dp[-1][j]` to silently wrap to the last row when `i=0`. Always check `if i > 0` and `if j > 0` before reading neighbors, or initialize with `float('inf')` and handle the top-left corner separately.

> 📝 **Practice:** [Q11 — Unique Paths](./practice.md#q11--2d-dp--unique-paths-in-a-grid) · [Q12 — Minimum Path Sum](./practice.md#q12--2d-dp--minimum-path-sum)

## DP on Trees

Tree diameter
House robber III

## DP on Subsequences

Subset sum
Partition equal subset

> [↑ Back to Top](#top)

<a id="12-dp-dimensions"></a>

# 12. DP Dimensions — Choosing the Right State

One of the hardest parts of DP is deciding how many dimensions your dp array needs.
The rule: **one dimension per independently varying parameter**.

> 📝 **Practice:** [Q9 — 2D Knapsack](./practice.md#q9--knapsack--01-knapsack-2d) · [Q10 — 1D Optimized](./practice.md#q10--knapsack--01-knapsack-space-optimized) · [Q11 — Grid DP](./practice.md#q11--2d-dp--unique-paths-in-a-grid)

```
STATE DIMENSION GUIDE

1D dp[i]       → one varying parameter
               → "what's the best answer for the first i items?"
               Examples: Fibonacci, climbing stairs, house robber

2D dp[i][j]    → two varying parameters
               → "best answer for first i items with capacity j?"
               Examples: 0/1 knapsack, edit distance, longest common subsequence

3D dp[i][j][k] → three varying parameters
               → rare, usually means you need to reconsider your state
               Examples: some grid problems with a variable constraint
```

**1D Example — Climbing Stairs:**

```python
# State: dp[i] = number of ways to reach step i
# Varying parameter: current step i
dp = [0] * (n + 1)
dp[0] = 1
dp[1] = 1
for i in range(2, n + 1):
    dp[i] = dp[i-1] + dp[i-2]
```

**2D Example — 0/1 Knapsack:**

```python
# State: dp[i][w] = max value using first i items with weight limit w
# Two varying parameters: item index i, remaining capacity w
dp = [[0] * (W + 1) for _ in range(n + 1)]
for i in range(1, n + 1):
    for w in range(W + 1):
        if weights[i-1] <= w:
            dp[i][w] = max(dp[i-1][w], values[i-1] + dp[i-1][w - weights[i-1]])
        else:
            dp[i][w] = dp[i-1][w]
```

**Space Optimization Trick:**

Many 2D DP problems only look at the previous row — collapse to 1D:

```python
# 0/1 knapsack space-optimized: O(W) instead of O(n × W)
dp = [0] * (W + 1)
for i in range(n):
    for w in range(W, weights[i] - 1, -1):   # ← traverse BACKWARDS to avoid using item twice
        dp[w] = max(dp[w], values[i] + dp[w - weights[i]])
```

**Common mistake — wrong loop order in knapsack space optimization:** Iterating the inner loop left-to-right in the 1D knapsack silently converts 0/1 knapsack into unbounded knapsack — each item can be selected multiple times. Memory aid: 0/1 = right to left. Unbounded = left to right.

## Visual: Space Optimization — 2D Table to 1D Rolling Array

For problems where dp[i][j] only depends on row i-1, compress to 1D:

Before: 2D table (O(m×n) space):

```
  Unique paths, 3×4 grid:

  Row 0: [1, 1, 1, 1]   ← base case
  Row 1: [1, 2, 3, 4]   ← computed from row 0
  Row 2: [1, 3, 6, 10]  ← computed from row 1

  We keep all rows in memory, but we only ever
  look at the PREVIOUS row when computing the current row.
  Rows 0 and 1 are DEAD after row 2 is computed.
```

After: 1D rolling array (O(n) space):

```
  Use a single array, update it IN PLACE left-to-right:

  Start:   dp = [1, 1, 1, 1]  ← row 0

  Pass 1 (computing row 1):
    dp[0] stays 1  (leftmost column always 1)
    dp[1] = dp[1] + dp[0] = 1 + 1 = 2
    dp[2] = dp[2] + dp[1] = 1 + 2 = 3
    dp[3] = dp[3] + dp[2] = 1 + 3 = 4
  dp = [1, 2, 3, 4]  ← now represents row 1

  Pass 2 (computing row 2):
    dp[0] stays 1
    dp[1] = dp[1] + dp[0] = 2 + 1 = 3
    dp[2] = dp[2] + dp[1] = 3 + 3 = 6
    dp[3] = dp[3] + dp[2] = 4 + 6 = 10
  dp = [1, 3, 6, 10]  ← answer is dp[-1] = 10

  BEFORE optimization:  O(m × n) space
  AFTER  optimization:  O(n) space    (just one row)

  When can you do this?
  Only when dp[i][j] depends ONLY on dp[i-1][...] and dp[i][j-1].
  Does NOT work when you need values from 2+ rows back.
```

**Common mistake — rolling array overwrites needed values:** When the transition needs the diagonal value `dp[i-1][j-1]`, updating in place overwrites it before you read it. Save `prev = dp[j]` before the update and use `prev` wherever you need the old diagonal. This is required in edit distance space optimization but not in unique paths.

**State Transition Diagram:**

Think of the DP table as a directed graph where each cell depends on others:

```
dp[i][j] depends on:
  - dp[i-1][j]     (skip current item)
  - dp[i-1][j-w]   (take current item)

Fill order: row by row, left to right
→ always fill cells before they are needed
```

> [↑ Back to Top](#top)

<a id="13-mental-model"></a>

# 13. Mental Model

Think of DP as:

Building solutions like Lego blocks.

Small blocks combine to form bigger blocks.

Each block stored for reuse.

## Visual: Mental Model Summary

```
┌────────────────────────────────────────────────────────────────┐
│  DYNAMIC PROGRAMMING — MENTAL MODELS                           │
├─────────────────────┬──────────────────────────────────────────┤
│  Recognition        │  Look for...                             │
├─────────────────────┼──────────────────────────────────────────┤
│  "Count ways"       │  Probably DP (add subproblem results)    │
│  "Max/min value"    │  Probably DP (optimize subproblems)      │
│  Overlapping        │  Memoize! Don't recompute                │
│  subproblems        │                                          │
│  Optimal            │  DP works if optimal solution is         │
│  substructure       │  composed of optimal sub-solutions       │
├─────────────────────┼──────────────────────────────────────────┤
│  Problem Type       │  DP Pattern                              │
├─────────────────────┼──────────────────────────────────────────┤
│  Fibonacci/stairs   │  1D, dp[i] = f(dp[i-1], dp[i-2])        │
│  Grid paths         │  2D, dp[i][j] = dp[i-1][j] + dp[i][j-1] │
│  Two strings        │  2D grid (LCS, edit distance)            │
│  Subset/knapsack    │  2D: items × capacity                    │
│  Subsequence        │  1D or 2D depending on constraints       │
├─────────────────────┼──────────────────────────────────────────┤
│  Optimization       │  How to apply                            │
├─────────────────────┼──────────────────────────────────────────┤
│  Memo → table       │  Eliminate recursion overhead            │
│  2D → 1D array      │  Only if row i depends only on row i-1   │
│  2 variables        │  Only if dp[i] depends on dp[i-1] only   │
└─────────────────────┴─────────────────────────────────────────┘

  The 3-step DP framework:
  1. DEFINE: What does dp[i] or dp[i][j] represent?
  2. TRANSITION: How does dp[i] relate to smaller subproblems?
  3. BASE CASE: What are the smallest inputs with known answers?
```

> [↑ Back to Top](#top)

<a id="14-step-by-step-dp-thinking-strategy"></a>

# 14. Step-by-Step DP Thinking Strategy

When solving DP problem:

1. Define state clearly.
2. Write recurrence relation.
3. Define base case.
4. Choose memo or tabulation.
5. Optimize space if possible.
6. Analyze complexity.

Never start coding before defining state.

**Common mistake — wrong state definition leads to wrong code:** A vague `dp[i]` definition means the base case initialization becomes guesswork. Write the state definition as one precise English sentence before writing any code. For LIS: "dp[i] = length of the longest increasing subsequence that ends at index i." That sentence forces `dp = [1] * n` (not 0), because every element alone is a length-1 subsequence.

**Common mistake — transition accesses out-of-bounds index:** When a transition uses `dp[i-2]`, `dp[i-2]` is invalid at `i=1` and in Python silently accesses `dp[-1]` (the last element), corrupting the answer. Either handle the first `k-1` iterations as explicit base cases or guard with `if i >= k else 0`.

**Common mistake — circular state dependency:** If your transition reads `dp[i]` while computing `dp[i]`, the recurrence is circular — there is no valid fill order. Redefine the state so it strictly depends on previously computed states (smaller i for 1D, previous row for 2D).

**Pre-submission checklist:**

- Can I write the state definition in one precise English sentence? If not, the state is wrong.
- Are all base cases initialized correctly? Verify by hand for n=0, n=1, and a 1-cell grid.
- Does the transition access any index that could be negative or out of bounds?
- For knapsack: does the inner loop go right-to-left (0/1) or left-to-right (unbounded)?
- If using a rolling array: do I cache the old `dp[j]` value before overwriting it?
- Is the "no solution" case handled? Return -1 when `dp[n]` is still at its sentinel value.
- Are all states computed in the correct topological order?

> 📝 **Practice:** [Q7 — 6-Step Strategy Applied](./practice.md#q7--dp-thinking--how-to-define-state) · [Q30 — Design from Scratch](./practice.md#q30--advanced--design-a-dp-solution-from-scratch)

> [↑ Back to Top](#top)

<a id="15-real-world-applications"></a>

# 15. Real-World Applications

- Stock market prediction
- Route optimization
- Resource allocation
- DNA sequence alignment
- AI decision systems
- Game strategy engines

DP widely used in advanced systems.

> [↑ Back to Top](#top)

<a id="16-final-understanding"></a>

# 16. Final Understanding

Dynamic Programming is:

- Optimization of recursion
- Memory-based speed-up
- Used for complex optimization problems
- Often polynomial time
- Requires careful state modeling
- One of the most important interview topics

Mastering DP prepares you for:

- Hard interview rounds
- FAANG-level problems
- Competitive programming
- Real-world optimization systems

DP is not about memorizing formulas.
It is about learning to model problems correctly.

## DP on Strings — Edit Distance

> Autocorrect works by measuring how "far apart" two words are. The edit distance (Levenshtein distance) counts the minimum operations to transform one string into another — a classic 2D DP problem.

> 📝 **Practice:** [Q16 — Edit Distance](./practice.md#q16--string-dp--edit-distance) · [Q28 — Space-Optimized O(n)](./practice.md#q28--2d-dp--edit-distance-space-optimized-on)

**Edit distance** counts the minimum number of single-character operations (insert, delete, replace) to transform string `s` into string `t`.

```python
def edit_distance(s, t):
    m, n = len(s), len(t)

    # dp[i][j] = min operations to transform s[:i] into t[:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Base cases: empty string requires i insertions/deletions
    for i in range(m + 1): dp[i][0] = i   # ← delete all i chars of s
    for j in range(n + 1): dp[0][j] = j   # ← insert all j chars of t

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s[i-1] == t[j-1]:          # ← chars match — no cost
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],            # ← delete from s
                    dp[i][j-1],            # ← insert into s
                    dp[i-1][j-1]           # ← replace
                )

    return dp[m][n]

edit_distance("kitten", "sitting")  # 3
```

## Visual: Edit Distance Table

```
  word1 = "horse"  (rows)
  word2 = "ros"    (cols)

  dp[i][j] = edit distance between word1[0..i-1] and word2[0..j-1]

  Rule:
    if word1[i-1] == word2[j-1]:  dp[i][j] = dp[i-1][j-1]  (no op needed)
    else: dp[i][j] = 1 + min(
        dp[i-1][j],    ← DELETE from word1  (go up)
        dp[i][j-1],    ← INSERT into word1  (go left)
        dp[i-1][j-1]   ← REPLACE in word1   (go diagonal)
    )

         ""   r    o    s
   ""  [ 0,   1,   2,   3 ]   ← cost to build word2 from empty string
   h   [ 1,   1,   2,   3 ]   h≠r: 1+min(0,1,1)=1
   o   [ 2,   2,   1,   2 ]   o==o: dp[1][1]=1
   r   [ 3,   2,   2,   2 ]   r==r: dp[2][1]=2
   s   [ 4,   3,   3,   2 ]   s==s: dp[3][2]=2
   e   [ 5,   4,   4,   3 ]   e≠s: 1+min(2,3,2)=3

  Answer: dp[5][3] = 3
  Operations:
    horse → rorse  (replace h with r)
    rorse → rose   (delete r)
    rose  → ros    (delete e)
```

**Visualizing the DP table for "kitten" → "sitting":**
```
    ""  s  i  t  t  i  n  g
""  [0, 1, 2, 3, 4, 5, 6, 7]
k   [1, 1, 2, 3, 4, 5, 6, 7]
i   [2, 2, 1, 2, 3, 4, 5, 6]
t   [3, 3, 2, 1, 2, 3, 4, 5]
t   [4, 4, 3, 2, 1, 2, 3, 4]
e   [5, 5, 4, 3, 2, 2, 3, 4]
n   [6, 6, 5, 4, 3, 3, 2, 3]  ← dp[6][7] = 3
```

**Space optimization to O(n):**

```python
def edit_distance_optimized(s, t):
    m, n = len(s), len(t)
    prev = list(range(n + 1))   # ← previous row

    for i in range(1, m + 1):
        curr = [i] + [0] * n    # ← current row starts with i
        for j in range(1, n + 1):
            if s[i-1] == t[j-1]:
                curr[j] = prev[j-1]
            else:
                curr[j] = 1 + min(prev[j], curr[j-1], prev[j-1])
        prev = curr

    return prev[n]
```

**Related string DP problems:**
- Longest Common Subsequence (LCS): `dp[i][j] = dp[i-1][j-1]+1 if match else max(dp[i-1][j], dp[i][j-1])`
- Longest Common Substring: same but reset to 0 on mismatch
- Regex matching / Wildcard matching: 2D DP with pattern state

**Complexity:** O(m×n) time, O(m×n) space (or O(n) with optimization)

## Bitmask DP — Tracking Subsets as States

> Imagine assigning employees to tasks. Each assignment changes which employees are "available." A bitmask tracks exactly which subset is available — and DP finds the optimal assignment across all possible subsets.

> 📝 **Practice:** [Q26 — Bitmask Task Assignment](./practice.md#q26--bitmask-dp--minimum-cost-task-assignment)

**Bitmask DP** uses an integer whose bits represent whether each item in a small set is "included." It enables DP over subsets, turning problems with exponential naive complexity into O(2^n × n).

**The pattern:** `dp[mask][i]` = answer for state where `mask` represents the subset of items used, and `i` is the last item chosen.

```python
# Classic: Traveling Salesman Problem (TSP) — visit all n cities, minimum cost
def tsp(dist):
    n = len(dist)
    INF = float('inf')

    # dp[mask][i] = min cost to visit exactly the cities in mask, ending at city i
    dp = [[INF] * n for _ in range(1 << n)]   # ← 2^n states
    dp[1][0] = 0   # ← start at city 0, only city 0 visited (mask=0b0001)

    for mask in range(1 << n):
        for last in range(n):
            if dp[mask][last] == INF: continue
            if not (mask >> last & 1): continue  # ← last must be in mask

            for nxt in range(n):
                if mask >> nxt & 1: continue     # ← skip already-visited cities
                new_mask = mask | (1 << nxt)     # ← add nxt to visited set
                dp[new_mask][nxt] = min(
                    dp[new_mask][nxt],
                    dp[mask][last] + dist[last][nxt]
                )

    full_mask = (1 << n) - 1   # ← all cities visited
    return min(dp[full_mask][i] + dist[i][0] for i in range(n))
```

**Essential bitmask operations:**
```python
mask = 0b1011    # bits 0, 1, 3 are set

mask | (1 << i)   # set bit i (include item i)
mask & ~(1 << i)  # clear bit i (remove item i)
mask >> i & 1     # check if bit i is set (is item i included?)
(mask & (mask-1)) # clear lowest set bit
bin(mask).count('1')  # count items in subset (popcount)
range(1 << n)     # iterate over all 2^n subsets
```

**Assignment problem pattern:**
```python
# Assign n tasks to n workers, minimize total cost
# dp[mask] = min cost to complete the tasks in mask
# mask has exactly popcount(mask) bits set = assigned so far

def assignment(cost):
    n = len(cost)
    dp = [float('inf')] * (1 << n)
    dp[0] = 0

    for mask in range(1 << n):
        worker = bin(mask).count('1')   # ← next worker to assign
        if worker == n: continue
        for task in range(n):
            if mask >> task & 1: continue    # ← task already assigned
            dp[mask | (1 << task)] = min(
                dp[mask | (1 << task)],
                dp[mask] + cost[worker][task]
            )

    return dp[(1 << n) - 1]
```

**When to use bitmask DP:**
- n ≤ 20 (states = 2^n, must be feasible)
- Need to track "which items from a small set have been used"
- TSP variants, assignment problems, covering problems

**Complexity:** O(2^n × n) time, O(2^n × n) space — only feasible for n ≤ 20

> 📝 **Practice:** [Q54 · dp-overlapping-subproblems](../dsa_practice_questions_100.md#q54--thinking--dp-overlapping-subproblems)

> [↑ Back to Top](#top)

## 📂 Navigation

**[🏠 Back to README](../README.md)**

**Prev:** [← Backtracking — Interview Q&A](../20_backtracking/interview.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)
