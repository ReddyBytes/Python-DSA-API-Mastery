# 📘 Dynamic Programming — The Art of Remembering Smartly

> If backtracking tries everything,
> Dynamic Programming avoids repeating work.
>
> DP is not about intelligence.
> It is about memory.

Dynamic Programming (DP) is:

- One of the most powerful algorithmic techniques
- One of the most confusing for beginners
- One of the most important interview topics

Let’s break it slowly and clearly.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
overlapping subproblems · optimal substructure · state definition · recurrence relation

**Should Learn** — Important for real projects, comes up regularly:
memoization (top-down) vs tabulation (bottom-up) · 1D DP · 2D DP · classic problems (knapsack, LCS, LIS, coin change)

**Good to Know** — Useful in specific situations, not always tested:
space optimization · edit distance (string DP) · bitmask DP intro

**Reference** — Know it exists, look up syntax when needed:
digit DP · DP on trees · convex hull trick · profile DP

---

# 🧠 1️⃣ Real Life Story — Climbing Stairs

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

---

# 🌳 2️⃣ Why Normal Recursion Is Slow

Let’s solve climbing stairs recursively.

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

---

# 💡 3️⃣ Core Idea of DP

If subproblem repeats,
store result.

Reuse it.

That’s it.

DP = Recursion + Memory

---

# 🧩 4️⃣ Two Requirements for DP

DP works when:

1️⃣ Overlapping Subproblems  
2️⃣ Optimal Substructure  

Overlapping:
Same subproblem solved multiple times.

Optimal Substructure:
Optimal solution built from optimal subsolutions.

If these exist → use DP.

---

# 🔁 5️⃣ Two Ways to Implement DP

---

## 🔹 Memoization (Top-Down)

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

---

## 🔹 Tabulation (Bottom-Up)

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

---

# 🧠 6️⃣ How to Identify DP Problems

Look for:

- Count number of ways
- Minimum cost
- Maximum profit
- Longest subsequence
- Shortest path (with constraints)
- Subset problems
- Knapsack-like structure

If recursion has repeated calls → DP candidate.

---

# 📚 7️⃣ Classic DP Problems

---

## 🔹 Fibonacci

Base DP example.

---

## 🔹 Climbing Stairs

Same pattern as Fibonacci.

---

## 🔹 0/1 Knapsack

Max value with limited capacity.

State:
dp[i][w] = best using first i items and capacity w.

Important 2D DP.

---

## 🔹 Longest Common Subsequence (LCS)

Compare two strings.

State:
dp[i][j] = LCS of first i and j characters.

Classic 2D DP.

---

## 🔹 Longest Increasing Subsequence (LIS)

State:
dp[i] = longest increasing subsequence ending at i.

Advanced optimization possible.

---

## 🔹 Coin Change

Minimum coins to make amount.

State:
dp[amount] = minimum coins.

Greedy fails here sometimes.
DP required.

---

# 📐 8️⃣ Time and Space Complexity

DP often reduces:

Exponential → Polynomial

Example:

Fibonacci:
O(2^n) → O(n)

Knapsack:
O(nW)

DP trades space for speed.

---

# ⚖️ 9️⃣ DP vs Greedy

Greedy:
Makes local decision.

DP:
Explores all options but stores results.

If greedy fails,
DP usually works.

---

# 🔄 1️⃣0️⃣ DP vs Backtracking

Backtracking:
Explores all combinations.

DP:
Avoids recomputing overlapping subproblems.

DP is optimized backtracking.

---

# 🧠 1️⃣1️⃣ Common DP Patterns

---

## 🔹 1D DP

Example:
Climbing stairs.

---

## 🔹 2D DP

Example:
LCS, knapsack.

---

## 🔹 DP on Strings

Edit distance  
Palindrome partitioning  

---

## 🔹 DP on Grid

Unique paths  
Minimum path sum  

---

## 🔹 DP on Trees

Tree diameter  
House robber III  

---

## 🔹 DP on Subsequences

Subset sum  
Partition equal subset  

---

---

## DP Dimensions — Choosing the Right State

One of the hardest parts of DP is deciding how many dimensions your dp array needs.
The rule: **one dimension per independently varying parameter**.

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

**State Transition Diagram:**

Think of the DP table as a directed graph where each cell depends on others:

```
dp[i][j] depends on:
  - dp[i-1][j]     (skip current item)
  - dp[i-1][j-w]   (take current item)

Fill order: row by row, left to right
→ always fill cells before they are needed
```

---

# ⚠️ 1️⃣2️⃣ Common Mistakes

- Not defining state properly
- Incorrect transition formula
- Wrong base case
- Index errors
- Forgetting initialization
- Mixing memoization and tabulation incorrectly

DP requires careful state definition.

---

# 🧠 1️⃣3️⃣ Mental Model

Think of DP as:

Building solutions like Lego blocks.

Small blocks combine to form bigger blocks.

Each block stored for reuse.

---

# 🏗 1️⃣4️⃣ Step-by-Step DP Thinking Strategy

When solving DP problem:

1. Define state clearly.
2. Write recurrence relation.
3. Define base case.
4. Choose memo or tabulation.
5. Optimize space if possible.
6. Analyze complexity.

Never start coding before defining state.

---

# 🌍 1️⃣5️⃣ Real-World Applications

- Stock market prediction
- Route optimization
- Resource allocation
- DNA sequence alignment
- AI decision systems
- Game strategy engines

DP widely used in advanced systems.

---

# 📌 1️⃣6️⃣ Final Understanding

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

---

## ✏️ DP on Strings — Edit Distance

> Autocorrect works by measuring how "far apart" two words are. The edit distance (Levenshtein distance) counts the minimum operations to transform one string into another — a classic 2D DP problem.

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

**Visualizing the DP table:**
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

---

## 🔲 Bitmask DP — Tracking Subsets as States

> Imagine assigning employees to tasks. Each assignment changes which employees are "available." A bitmask tracks exactly which subset is available — and DP finds the optimal assignment across all possible subsets.

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

---

# 🔁 Navigation

Previous:  
[20_backtracking/interview.md](/dsa-complete-mastery/20_backtracking/interview.md)

Next:  
[21_dynamic_programming/interview.md](/dsa-complete-mastery/21_dynamic_programming/interview.md)  
[22_bit_manipulation/theory.md](/dsa-complete-mastery/22_bit_manipulation/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Backtracking — Interview Q&A](../20_backtracking/interview.md) &nbsp;|&nbsp; **Next:** [Visual Explanation →](./visual_explanation.md)

**Related Topics:** [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
