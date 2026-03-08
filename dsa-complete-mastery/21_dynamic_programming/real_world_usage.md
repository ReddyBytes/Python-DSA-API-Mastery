# Dynamic Programming — Real-World Usage

DP is not just a competitive-programming technique. It quietly powers the
software you use every day: your text editor, your GPS, your version control
system, your music streaming service. This file walks through nine real
engineering domains and shows the exact DP idea at work in each.

---

## 1. Text Editors — Spell Check and Autocorrect

**Algorithm:** Levenshtein edit distance (a 2-D DP table)

When you type "teh", your phone or editor computes the minimum number of
single-character edits (insertions, deletions, substitutions) needed to
transform it into every word in the dictionary. The word with the smallest
distance wins.

### How "teh" → "the" works (edit distance = 1)

```
     ""  t  h  e
""  [ 0, 1, 2, 3 ]
t   [ 1, 0, 1, 2 ]
e   [ 2, 1, 1, 1 ]
h   [ 3, 2, 1, 2 ]   ← edit_distance("teh", "the") = 2

     ""  t  e  h
""  [ 0, 1, 2, 3 ]
t   [ 1, 0, 1, 2 ]
e   [ 2, 1, 0, 1 ]
h   [ 3, 2, 1, 0 ]   ← edit_distance("teh", "teh") = 0
```

Wait — "teh" → "the" is a transposition, handled by Damerau-Levenshtein:

```python
def edit_distance(s1: str, s2: str) -> int:
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i          # delete all of s1
    for j in range(n + 1):
        dp[0][j] = j          # insert all of s2

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]          # characters match, free
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],    # delete from s1
                    dp[i][j-1],    # insert into s1
                    dp[i-1][j-1]   # substitute
                )
    return dp[m][n]

# Real-world sketch: rank dictionary words by edit distance to the typo
def autocorrect(typo: str, dictionary: list[str]) -> str:
    return min(dictionary, key=lambda word: edit_distance(typo, word))
```

**Where it runs:** iOS/Android keyboard, Google Docs, VS Code spell-check,
Gmail smart compose, search query correction ("Did you mean…?").

---

## 2. Google Maps / GPS Routing

**Algorithm:** Dijkstra (greedy + DP on shortest subpaths) + A*

The core DP principle: the shortest path from A to C through B is the shortest
path from A to B plus the shortest path from B to C. This **optimal substructure**
is what makes Dijkstra work.

For multi-stop routing (A → B → C → D), the full problem becomes:
`best(A→D) = min over all waypoint orderings` — a Traveling Salesman variant
solved approximately with DP bitmask on small sets.

```python
import heapq

def dijkstra(graph: dict, start: str) -> dict:
    # graph[u] = [(weight, v), ...]
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    heap = [(0, start)]    # (distance, node)

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue       # stale entry — DP table already has better answer
        for weight, v in graph[u]:
            new_dist = dist[u] + weight
            if new_dist < dist[v]:       # ← DP relaxation step
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))
    return dist

# Real-world addition: edge weights updated every 30 seconds from traffic data
# Bidirectional Dijkstra halves search space for long-distance routing
```

**Where it runs:** Google Maps, Apple Maps, Waze, Uber route planner,
FedEx delivery scheduling, airline hub routing.

---

## 3. Version Control — Git Diff (LCS)

**Algorithm:** Longest Common Subsequence (LCS)

When you run `git diff`, Git finds the LCS of the two file versions and displays
what was added (lines only in new) and deleted (lines only in old).

### Simple diff example

```
Old file:          New file:
──────────         ──────────
apple              apple
banana             cherry
cherry             banana
date               date

LCS = [apple, cherry, date]   (length 3)

Diff output:
  apple
+ cherry     ← inserted (in new, not in LCS position in old)
  banana     ← moved context
- banana     ← deleted (in old, not kept)
  cherry
  date
```

```python
def lcs(a: list, b: list) -> list:
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    # Backtrack to reconstruct the common subsequence
    result, i, j = [], m, n
    while i > 0 and j > 0:
        if a[i-1] == b[j-1]:
            result.append(a[i-1]); i -= 1; j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    return result[::-1]

def git_diff(old_lines: list, new_lines: list):
    common = set(lcs(old_lines, new_lines))
    for line in old_lines:
        print(f"- {line}" if line not in common else f"  {line}")
    # (simplified — real diff tracks positions, not just membership)
```

**Where it runs:** Git, Mercurial, SVN, code review tools (GitHub PR diff),
merge conflict resolution, wiki edit histories.

---

## 4. Trading and Finance — Stock Buy/Sell

**Algorithm:** 1-D DP over price array

The classic problem: given daily prices, find the maximum profit with at most k
transactions. Wall Street quant desks use generalised versions for options
pricing and trade scheduling.

```python
def max_profit_one_transaction(prices: list[int]) -> int:
    # dp: at each day, what is the best profit achievable?
    min_price = float('inf')
    max_profit = 0
    for price in prices:
        min_price  = min(min_price, price)      # best day to have bought
        max_profit = max(max_profit, price - min_price)
    return max_profit

def max_profit_k_transactions(k: int, prices: list[int]) -> int:
    n = len(prices)
    # dp[t][d] = max profit using at most t transactions up to day d
    dp = [[0] * n for _ in range(k + 1)]
    for t in range(1, k + 1):
        max_so_far = -prices[0]
        for d in range(1, n):
            dp[t][d] = max(dp[t][d-1], prices[d] + max_so_far)
            max_so_far = max(max_so_far, dp[t-1][d] - prices[d])
    return dp[k][n-1]
```

**Where it runs:** Algorithmic trading systems, portfolio optimisers,
options pricing engines, risk management dashboards.

---

## 5. Natural Language Processing — Viterbi Algorithm

**Algorithm:** Viterbi (DP over a Hidden Markov Model trellis)

Every time autocomplete predicts the next word, or a POS tagger labels
"bank" as NOUN vs VERB, a DP algorithm is running over a probability lattice.

The Viterbi algorithm finds the most likely sequence of hidden states
(e.g., POS tags) given observed outputs (words).

```python
def viterbi(obs: list, states: list, start_p: dict,
            trans_p: dict, emit_p: dict) -> list:
    T = len(obs)
    # dp[t][s] = max probability of any path ending in state s at time t
    dp   = [{} for _ in range(T)]
    path = [{} for _ in range(T)]

    for s in states:
        dp[0][s]   = start_p[s] * emit_p[s].get(obs[0], 1e-10)
        path[0][s] = None

    for t in range(1, T):
        for s in states:
            best_prob, best_prev = max(
                (dp[t-1][prev] * trans_p[prev][s] * emit_p[s].get(obs[t], 1e-10), prev)
                for prev in states
            )
            dp[t][s]   = best_prob
            path[t][s] = best_prev

    # Backtrack
    best_last = max(states, key=lambda s: dp[T-1][s])
    result = [best_last]
    for t in range(T-1, 0, -1):
        result.append(path[t][result[-1]])
    return result[::-1]

# Used in: POS tagging, speech recognition, gene finding, OCR
```

**Where it runs:** Google Translate, Siri speech recognition, spam filters,
named-entity recognition, DNA sequence annotation.

---

## 6. Bioinformatics — Sequence Alignment

**Algorithm:** Needleman-Wunsch (global) / Smith-Waterman (local)

Aligning two DNA or protein sequences to find evolutionary relationships is
a direct application of edit distance with custom scoring matrices.

```python
def needleman_wunsch(seq1: str, seq2: str,
                     match=1, mismatch=-1, gap=-2) -> tuple:
    m, n = len(seq1), len(seq2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1): dp[i][0] = i * gap
    for j in range(n + 1): dp[0][j] = j * gap

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            score = match if seq1[i-1] == seq2[j-1] else mismatch
            dp[i][j] = max(
                dp[i-1][j-1] + score,   # align (match or mismatch)
                dp[i-1][j]   + gap,      # gap in seq2
                dp[i][j-1]   + gap       # gap in seq1
            )
    return dp[m][n]

# Example: GATTACA vs GCATGCU
# Alignment score guides phylogenetic tree construction
```

**Where it runs:** NCBI BLAST, genome assemblers (e.g., Velvet, SPAdes),
protein structure prediction, CRISPR off-target analysis.

---

## 7. Game AI — Minimax with Memoization

**Algorithm:** Minimax DP (game-tree search with memoization)

Chess engines, checkers solvers, and Go programs represent the game state as a
DAG. DP (via memoization) avoids re-evaluating positions reached via different
move sequences.

```python
from functools import lru_cache

def minimax_ttt(board: tuple, is_max: bool) -> int:
    winner = check_winner(board)
    if winner ==  1: return  1    # maximiser wins
    if winner == -1: return -1    # minimiser wins
    if all(c != 0 for c in board): return 0   # draw

    @lru_cache(maxsize=None)
    def solve(state: tuple, maximising: bool) -> int:
        w = check_winner(state)
        if w !=  0: return w
        if all(c != 0 for c in state): return 0

        moves = [i for i, c in enumerate(state) if c == 0]
        if maximising:
            return max(solve(state[:i] + (1,) + state[i+1:], False) for i in moves)
        else:
            return min(solve(state[:i] + (-1,) + state[i+1:], True) for i in moves)

    return solve(board, is_max)

# In chess: alpha-beta pruning + transposition table (hash map memoisation)
# prunes ~50% of the minimax tree, enabling ~10-ply search in real time
```

**Where it runs:** Stockfish (chess), AlphaGo (Monte Carlo + DP),
game theory solvers, poker bots, automated game testing.

---

## 8. Compilers — Optimal Expression Evaluation (Matrix Chain)

**Algorithm:** Matrix Chain Multiplication DP (interval DP)

Compilers and query optimisers need to pick the cheapest order to evaluate
chained operations (joins, matrix multiplications). The order dramatically
changes the cost.

```python
def matrix_chain_order(dims: list[int]) -> int:
    # dims[i-1] x dims[i] is the shape of matrix i
    n = len(dims) - 1
    # dp[i][j] = min multiplications to compute matrices i..j
    dp = [[0] * n for _ in range(n)]

    for length in range(2, n + 1):          # sub-chain length
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float('inf')
            for k in range(i, j):           # split point
                cost = (dp[i][k] + dp[k+1][j]
                        + dims[i] * dims[k+1] * dims[j+1])
                dp[i][j] = min(dp[i][j], cost)
    return dp[0][n-1]

# Same pattern in SQL query planners:
# dp[subset of tables] = cheapest join order for that subset
# PostgreSQL's dynamic programming query planner uses exactly this.
```

**Where it runs:** PostgreSQL query planner, GCC expression tree optimiser,
TensorFlow/PyTorch graph optimiser (operation fusion), LLVM IR optimisations.

---

## 9. Video Streaming — Adaptive Bitrate (ABR)

**Algorithm:** DP over buffer state and bandwidth history

Netflix, YouTube, and Spotify's video/audio players constantly decide which
quality chunk to download next. The optimal policy balances current buffer
level, predicted bandwidth, and rebuffering penalty — a finite-horizon DP.

```python
def adaptive_bitrate(bandwidth_history: list[float],
                     bitrates: list[float],
                     buffer_size: int = 30) -> list[int]:
    # State: (time_step, buffer_level)
    # Action: which bitrate to select for next chunk
    # Reward: quality - rebuffering_penalty - quality_variation

    T = len(bandwidth_history)
    INF = float('inf')
    # dp[t][buf] = max future reward from time t with buffer level buf
    dp   = [[-INF] * (buffer_size + 1) for _ in range(T + 1)]
    choices = [[0]  * (buffer_size + 1) for _ in range(T)]

    for buf in range(buffer_size + 1):
        dp[T][buf] = 0    # terminal state: no future reward

    for t in range(T - 1, -1, -1):
        bw = bandwidth_history[t]
        for buf in range(buffer_size + 1):
            best_val, best_r = -INF, 0
            for r_idx, rate in enumerate(bitrates):
                download_time = rate / bw          # seconds to fetch chunk
                new_buf = max(0, buf - download_time) + 1   # 1s chunk added
                new_buf = min(new_buf, buffer_size)
                rebuffer_penalty = max(0, download_time - buf) * 10
                quality_reward   = r_idx           # higher index = better quality
                val = quality_reward - rebuffer_penalty + dp[t+1][int(new_buf)]
                if val > best_val:
                    best_val, best_r = val, r_idx
            dp[t][buf]      = best_val
            choices[t][buf] = best_r

    # Reconstruct policy
    policy, buf = [], buffer_size // 2
    for t in range(T):
        r = choices[t][buf]
        policy.append(r)
        bw = bandwidth_history[t]
        download_time = bitrates[r] / bw
        buf = max(0, buf - download_time) + 1
        buf = min(int(buf), buffer_size)
    return policy
```

**Where it runs:** Netflix BOLA/Pensieve ABR algorithm, YouTube buffer-based
ABR, Spotify audio quality switching, HLS/DASH players in browsers.

---

## Summary Table

```
Domain                   DP Algorithm               Key State
──────────────────────────────────────────────────────────────────────
Spell check / autocorrect Edit distance (2-D table)  dp[i][j] = min edits
GPS routing               Dijkstra relaxation        dist[node] = min dist
Git diff                  LCS (2-D table)            dp[i][j] = lcs length
Stock trading             1-D price scan             min_price, max_profit
NLP / speech recognition  Viterbi (trellis)          dp[t][state] = max prob
Bioinformatics alignment  Needleman-Wunsch (2-D)     dp[i][j] = align score
Game AI                   Minimax + memo             dp[board] = game value
Compiler optimisation     Matrix chain (interval)    dp[i][j] = min ops
Video streaming           Buffer-state DP            dp[t][buf] = max reward
```

The common thread: **every problem decomposes into overlapping subproblems
with optimal substructure**. Once you recognise that shape, DP is the tool.
