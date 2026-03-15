# Dynamic Programming — Visual Explanation

---

## 1. WHY DP? — THE CALL TREE EXPLOSION

**Problem: Fibonacci(5) = Fibonacci(4) + Fibonacci(3)**

### WITHOUT memoization — exponential work

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

### WITH memoization — linear work

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

---

## 2. MEMOIZATION vs TABULATION

**Same problem — two different DP styles.**

**Problem: Climbing stairs. n=5 stairs, take 1 or 2 steps at a time. How many ways?**

### Memoization (Top-Down) — Recursive + Cache

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

### Tabulation (Bottom-Up) — Iterative + Table

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

---

## 3. 1D DP — CLIMBING STAIRS (Dependency Arrows)

**Each cell depends on the previous two cells.**

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

---

## 4. 2D DP — LCS (Longest Common Subsequence)

**Find the longest subsequence common to both strings.**

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

---

## 5. KNAPSACK DP TABLE

**0/1 Knapsack: items with weights and values, maximize value in capacity W.**

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

---

## 6. EDIT DISTANCE TABLE

**Minimum operations (insert, delete, replace) to convert word1 → word2.**

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

---

## 7. LIS — PATIENCE SORTING ANALOGY

**Longest Increasing Subsequence. Analogy: sort playing cards into piles.**

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

```
  Standard DP approach for comparison (O(n^2)):
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

---

## 8. GRID DP — "WHERE CAN I COME FROM?" ARROWS

**Problem: Count unique paths from top-left to bottom-right.**
**(Can only move right or down.)**

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

---

## 9. SPACE OPTIMIZATION — 2D TABLE → 1D ROLLING ARRAY

**For problems where dp[i][j] only depends on row i-1, compress to 1D.**

### Before: 2D table (O(m×n) space)

```
  Unique paths, 3×4 grid:

  Row 0: [1, 1, 1, 1]   ← base case
  Row 1: [1, 2, 3, 4]   ← computed from row 0
  Row 2: [1, 3, 6, 10]  ← computed from row 1

  We keep all rows in memory, but we only ever
  look at the PREVIOUS row when computing the current row.
  Rows 0 and 1 are DEAD after row 2 is computed.
```

### After: 1D rolling array (O(n) space)

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

---

## MENTAL MODEL SUMMARY

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
└─────────────────────┴──────────────────────────────────────────┘

  The 3-step DP framework:
  1. DEFINE: What does dp[i] or dp[i][j] represent?
  2. TRANSITION: How does dp[i] relate to smaller subproblems?
  3. BASE CASE: What are the smallest inputs with known answers?
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
