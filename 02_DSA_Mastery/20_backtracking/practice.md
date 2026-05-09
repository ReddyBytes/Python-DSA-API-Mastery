# Backtracking — Practice Questions

> 25 questions covering the choose-explore-unchoose template, decision trees, pruning,
> classic problems, and the boundary between backtracking, brute force, and DP.

---

## Quick Index

| # | Topic | Level |
|---|-------|-------|
| [Q1](#q1) | Identify backtracking signals | Basic |
| [Q2](#q2) | Write the universal template | Basic |
| [Q3](#q3) | Subsets of [1,2,3] — trace the tree | Basic |
| [Q4](#q4) | Why must we copy before appending to result? | Basic |
| [Q5](#q5) | Base case rules | Basic |
| [Q6](#q6) | Backtracking vs brute force | Basic |
| [Q7](#q7) | Time complexity of subsets and permutations | Basic |
| [Q8](#q8) | What does "pruning" mean, and when do you prune? | Basic |
| [Q9](#q9) | Generate all subsets | Intermediate |
| [Q10](#q10) | Generate all permutations (used-array) | Intermediate |
| [Q11](#q11) | Combinations — choose k from n | Intermediate |
| [Q12](#q12) | Combination sum with repetition | Intermediate |
| [Q13](#q13) | Combination sum without repetition (duplicates in input) | Intermediate |
| [Q14](#q14) | Palindrome partitioning | Intermediate |
| [Q15](#q15) | Word search in grid | Intermediate |
| [Q16](#q16) | Generate valid parentheses | Intermediate |
| [Q17](#q17) | Subsets with duplicates in input | Intermediate |
| [Q18](#q18) | Permutations with duplicates | Intermediate |
| [Q19](#q19) | Backtracking vs DP decision guide | Intermediate |
| [Q20](#q20) | State space tree — estimate feasibility before coding | Intermediate |
| [Q21](#q21) | N-Queens — all solutions | Advanced |
| [Q22](#q22) | Sudoku solver | Advanced |
| [Q23](#q23) | Pruning conditions — cut branches early | Advanced |
| [Q24](#q24) | Letter combinations of phone number | Advanced |
| [Q25](#q25) | Restore IP addresses | Advanced |

---

## Basic (Q1–Q8)

---

<a id="q1"></a>
### Q1

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


**When you read a problem statement, what signals tell you to reach for backtracking?**

<details>
<summary>Hint</summary>
Look for "generate all", "find all", "combinations", "permutations", or "satisfying constraints".
</details>

<details>
<summary>Answer</summary>

Reach for backtracking when the problem:

- Asks for **all** solutions, not just one or an optimal one.
- Contains the words "generate", "find all", "enumerate", "combinations", "permutations", "subsets", or "arrangements".
- Involves placing items under constraints (N-Queens, Sudoku).
- Explores a path in a grid where you must not revisit cells.

**Why:** Backtracking systematically explores every branch of a decision tree and abandons branches early when they cannot lead to a valid solution. If the problem only asks for a count or an optimal value — and has overlapping sub-problems — DP is usually better.

**Time/Space:** Depends on the specific problem — see individual questions.
</details>

---

<a id="q2"></a>
### Q2

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


**Write the universal backtracking template in Python. Label each section.**

<details>
<summary>Hint</summary>
Three sacred sections: choose, explore, unchoose.
</details>

<details>
<summary>Answer</summary>

```python
def solve(input_data):
    result = []

    def backtrack(state, start_or_choices):
        # BASE CASE: complete solution found
        if is_complete(state):
            result.append(state[:])   # copy — never store reference
            return

        for choice in available_choices(start_or_choices):
            if not is_valid(state, choice):   # PRUNE invalid branches
                continue

            # CHOOSE
            state.append(choice)

            # EXPLORE
            backtrack(state, updated_choices)

            # UNCHOOSE (backtrack)
            state.pop()

    backtrack([], initial_choices)
    return result
```

**Why:** Every mutation applied before the recursive call must be undone after it returns. The caller must see identical state before and after — this is the invariant that makes backtracking correct.

**Time:** O(b^d) where b = branching factor, d = depth of recursion tree.
**Space:** O(d) recursion stack + O(result size).
</details>

---

<a id="q3"></a>
### Q3

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


**Trace the decision tree for generating all subsets of `[1, 2, 3]`. How many leaves are there?**

<details>
<summary>Hint</summary>
Each element has two choices: include or exclude. Draw a binary tree of depth 3.
</details>

<details>
<summary>Answer</summary>

```
                        []
              ┌─────────┴─────────┐
           include 1           exclude 1
             [1]                  []
         ┌────┴────┐          ┌────┴────┐
      inc 2      exc 2     inc 2      exc 2
      [1,2]       [1]       [2]         []
      ┌─┴─┐      ┌─┴─┐    ┌─┴─┐      ┌─┴─┐
    i3   e3    i3   e3  i3   e3    i3   e3
 [1,2,3][1,2][1,3] [1] [2,3] [2]  [3]  []
```

8 leaves = 2^3. Every element independently in or out.

**Why:** This is a binary decision tree of depth n. Backtracking explores it left-to-right using a `start` pointer so each subset is generated exactly once.

**Time:** O(2^n) to generate all subsets.
**Space:** O(n) recursion depth + O(2^n * n) for the result.
</details>

---

<a id="q4"></a>
### Q4

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


**Why do you need `result.append(current[:])` instead of `result.append(current)`?**

<details>
<summary>Hint</summary>
Python lists are objects. Appending a list appends a reference to that object.
</details>

<details>
<summary>Answer</summary>

```python
# WRONG — all entries in result point to the same list object
result.append(current)

# After backtracking finishes, current = []
# Every entry in result now shows [] because they all share the same reference.

# CORRECT — capture a snapshot at this moment
result.append(current[:])   # or list(current)
```

**Concrete demo:**
```python
current = []
result = []
result.append(current)   # appends reference
current.append(1)
print(result)            # [[1]] — not [[]] as you might expect!
```

**Why:** `current[:]` creates a shallow copy — a new list object with the same values. The original `current` can be mutated freely without affecting the stored copy. For lists of immutable values (ints, strings), a shallow copy is always sufficient.

**Time:** O(n) per copy (n = length of current).
**Space:** O(n) per snapshot.
</details>

---

<a id="q5"></a>
### Q5

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


**What are the two rules for a correct base case in a backtracking function?**

<details>
<summary>Hint</summary>
Think about what "done" means and what "invalid" means.
</details>

<details>
<summary>Answer</summary>

Rule 1 — **Solution complete:** The current state is a valid, full answer. Record it and return.

```python
if len(current) == k:          # combinations: filled k slots
    result.append(current[:])
    return
```

Rule 2 — **Dead end / pruning:** The current path cannot lead to any valid solution. Return without recording.

```python
if remaining < 0:   # combination sum: overshot target
    return
if start >= len(nums) and len(current) < required:
    return          # ran out of elements before filling requirement
```

**Why:** Missing the first rule means you never record answers. Missing the second rule means you explore impossible branches, leading to wrong answers or infinite recursion.

**Time/Space:** Base cases run in O(1); their existence is what limits the recursion depth.
</details>

---

<a id="q6"></a>
### Q6

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


**What is the difference between backtracking and brute force?**

<details>
<summary>Hint</summary>
Brute force generates everything then filters. Backtracking filters during generation.
</details>

<details>
<summary>Answer</summary>

| | Brute Force | Backtracking |
|---|---|---|
| When to filter | After generating all candidates | During generation (prune early) |
| Explores invalid branches? | Yes | No — cuts them immediately |
| Time | Always O(b^d) | O(b^d) worst case, much better in practice |
| Code style | Nested loops or itertools | Recursive with constraint checks |

**Example:** For combination sum with target=7 from [2,3,6,7]:

- Brute force: generate all 2^4=16 subsets, then filter those summing to 7.
- Backtracking: once current sum exceeds 7, stop exploring that branch immediately.

**Why:** Backtracking is "intelligent brute force." The constraint check inside the loop converts an exhaustive search into a pruned search. In the best case (tight constraints), it can run in polynomial time despite an exponential state space.

**Time:** Both O(b^d) worst case; backtracking wins in practice.
</details>

---

<a id="q7"></a>
### Q7

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


**State the time complexity of (a) generating all subsets and (b) generating all permutations. Explain why.**

<details>
<summary>Hint</summary>
For subsets: 2 choices per element. For permutations: n choices for position 0, n-1 for position 1, ...
</details>

<details>
<summary>Answer</summary>

**(a) Subsets — O(2^n * n)**

Each of n elements is independently included or excluded → 2^n subsets.
Copying each subset to result costs O(n).
Total: O(2^n * n).

**(b) Permutations — O(n! * n)**

n choices for first position, n-1 for second, ... → n! permutations.
Copying each permutation costs O(n).
Total: O(n! * n).

**Growth comparison:**
```
n=10:  subsets  = 1,024        permutations = 3,628,800
n=15:  subsets  = 32,768       permutations = 1.3 trillion
n=20:  subsets  = 1,048,576    permutations = 2.4 * 10^18
```

**Why n! grows so much faster:** Every additional element multiplies the permutation count by n, while subsets only double.

**Time:** Subsets O(2^n * n), Permutations O(n! * n).
**Space:** O(n) recursion stack in both cases (excluding result storage).
</details>

---

<a id="q8"></a>
### Q8

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


**Explain pruning. Give two concrete examples of pruning conditions.**

<details>
<summary>Hint</summary>
Pruning is detecting early that a branch cannot lead to a valid solution, then skipping it entirely.
</details>

<details>
<summary>Answer</summary>

**Pruning** means detecting — before recursing deeper — that the current partial solution can never lead to a valid complete solution. You skip (prune) the entire subtree rooted at that node.

**Example 1 — Combination Sum:**
```python
candidates.sort()                      # prerequisite: sort first
for i in range(start, len(candidates)):
    if candidates[i] > remaining:
        break                          # prune: all subsequent are also too large
```

**Example 2 — Combinations of size k:**
```python
remaining_needed = k - len(current)
available = n - start + 1
if available < remaining_needed:
    return                             # prune: not enough elements left to fill k slots
```

**Example 3 — N-Queens:**
```python
if col in cols or (row - col) in diag1 or (row + col) in diag2:
    continue                           # prune: this column conflicts with existing queens
```

**Why:** A good pruning condition turns an exponential explosion into a manageable search. Sudoku's worst case is 9^81 ≈ 10^77; with constraint propagation pruning, a typical puzzle solves in microseconds.

**Time/Space:** Pruning reduces the number of nodes explored; the improvement depends on how tight the constraints are.
</details>

---

## Intermediate (Q9–Q20)

---

<a id="q9"></a>
### Q9

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


**Implement `subsets(nums)` returning all 2^n subsets of a list of distinct integers.**

<details>
<summary>Hint</summary>
Use a `start` pointer to only look forward. Record the current path at every node, not just leaves.
</details>

<details>
<summary>Answer</summary>

```python
def subsets(nums: list[int]) -> list[list[int]]:
    result = []

    def backtrack(start: int, current: list[int]) -> None:
        result.append(current[:])          # record at every node (not just leaves)

        for i in range(start, len(nums)):
            current.append(nums[i])        # CHOOSE: include nums[i]
            backtrack(i + 1, current)      # EXPLORE: move forward only
            current.pop()                  # UNCHOOSE

    backtrack(0, [])
    return result

# subsets([1,2,3]) → [[], [1], [1,2], [1,2,3], [1,3], [2], [2,3], [3]]
```

**Why:** The `start` pointer ensures we never go backward, so each subset is generated exactly once. Recording at every node (not just leaves) gives us all partial paths, which are exactly the subsets.

**Time:** O(2^n * n) — 2^n subsets, O(n) copy each.
**Space:** O(n) recursion depth.
</details>

---

<a id="q10"></a>
### Q10

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


**Implement `permutations(nums)` returning all n! permutations of distinct integers.**

<details>
<summary>Hint</summary>
Use a boolean `used` array. Scan all indices each time, skipping those already in `current`.
</details>

<details>
<summary>Answer</summary>

```python
def permutations(nums: list[int]) -> list[list[int]]:
    result = []
    used = [False] * len(nums)

    def backtrack(current: list[int]) -> None:
        if len(current) == len(nums):
            result.append(current[:])
            return

        for i in range(len(nums)):
            if used[i]:
                continue            # skip elements already in current path
            used[i] = True          # CHOOSE
            current.append(nums[i])
            backtrack(current)      # EXPLORE
            current.pop()           # UNCHOOSE
            used[i] = False

    backtrack([])
    return result

# permutations([1,2,3]) → 6 permutations
```

**Why:** Unlike subsets, permutations require every element to be usable at every position. Using a `start` pointer would only move forward and produce combinations, not permutations. The `used` array lets us pick any unused element at each level.

**Time:** O(n! * n).
**Space:** O(n) recursion depth + O(n) for `used` array.
</details>

---

<a id="q11"></a>
### Q11

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


**Implement `combinations(n, k)` returning all C(n,k) combinations of numbers 1..n.**

<details>
<summary>Hint</summary>
Prune the loop upper bound: if fewer elements remain than needed, stop early.
</details>

<details>
<summary>Answer</summary>

```python
def combinations(n: int, k: int) -> list[list[int]]:
    result = []

    def backtrack(start: int, current: list[int]) -> None:
        if len(current) == k:
            result.append(current[:])
            return

        # Pruning: need (k - len(current)) more elements.
        # Available from start to n: n - start + 1 elements.
        # Stop if available < needed.
        for i in range(start, n - (k - len(current)) + 2):
            current.append(i)           # CHOOSE
            backtrack(i + 1, current)   # EXPLORE
            current.pop()               # UNCHOOSE

    backtrack(1, [])
    return result

# combinations(4, 2) → [[1,2],[1,3],[1,4],[2,3],[2,4],[3,4]]
```

**Why:** The upper bound `n - (k - len(current)) + 2` prunes branches where we cannot possibly fill `k` slots — instead of discovering that failure at a leaf, we detect it before recursing.

**Time:** O(C(n,k) * k).
**Space:** O(k) recursion depth.
</details>

---

<a id="q12"></a>
### Q12

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


**Implement `combination_sum(candidates, target)` where each candidate can be used any number of times.**

<details>
<summary>Hint</summary>
Sort candidates. Use `i` (not `i+1`) when recursing to allow reuse. Break when candidate exceeds remaining.
</details>

<details>
<summary>Answer</summary>

```python
def combination_sum(candidates: list[int], target: int) -> list[list[int]]:
    candidates.sort()           # sort enables break-pruning
    result = []

    def backtrack(start: int, current: list[int], remaining: int) -> None:
        if remaining == 0:
            result.append(current[:])
            return

        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                break           # PRUNE: sorted, so all subsequent are also too large
            current.append(candidates[i])
            backtrack(i, current, remaining - candidates[i])   # i not i+1: reuse allowed
            current.pop()

    backtrack(0, [], target)
    return result

# combination_sum([2,3,6,7], 7) → [[2,2,3],[7]]
```

**Why:** Passing `i` instead of `i+1` allows the same candidate to be reused in the same branch. Sorting + `break` (not `continue`) prunes entire remaining candidates once one exceeds the target.

**Time:** O(n^(T/min_candidate)) in worst case where T = target.
**Space:** O(T/min_candidate) recursion depth.
</details>

---

<a id="q13"></a>
### Q13

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


**Implement `combination_sum_2(candidates, target)` where each candidate can be used at most once, and the input may contain duplicates.**

<details>
<summary>Hint</summary>
Sort first. Use `i+1` in the recursive call. Skip duplicates at the same recursion level with `if i > start and candidates[i] == candidates[i-1]: continue`.
</details>

<details>
<summary>Answer</summary>

```python
def combination_sum_2(candidates: list[int], target: int) -> list[list[int]]:
    candidates.sort()
    result = []

    def backtrack(start: int, current: list[int], remaining: int) -> None:
        if remaining == 0:
            result.append(current[:])
            return

        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                break
            # Skip duplicate values at the same recursion level
            if i > start and candidates[i] == candidates[i - 1]:
                continue
            current.append(candidates[i])
            backtrack(i + 1, current, remaining - candidates[i])  # i+1: no reuse
            current.pop()

    backtrack(0, [], target)
    return result

# combination_sum_2([10,1,2,7,6,1,5], 8) → [[1,1,6],[1,2,5],[1,7],[2,6]]
```

**Why:** The duplicate skip `i > start and candidates[i] == candidates[i-1]` prevents generating the same combination via two different occurrences of the same value at the same tree level. The condition must be `i > start` (not `i > 0`) — using `i > 0` would incorrectly skip the first valid occurrence in deeper levels.

**Time:** O(2^n) worst case.
**Space:** O(n) recursion depth.
</details>

---

<a id="q14"></a>
### Q14

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


**Implement `palindrome_partitioning(s)` returning all ways to partition `s` such that every substring is a palindrome.**

<details>
<summary>Hint</summary>
At each position, try every possible end index. Only recurse if the substring from start to end is a palindrome.
</details>

<details>
<summary>Answer</summary>

```python
def palindrome_partitioning(s: str) -> list[list[str]]:
    result = []

    def is_palindrome(sub: str) -> bool:
        return sub == sub[::-1]

    def backtrack(start: int, current: list[str]) -> None:
        if start == len(s):
            result.append(current[:])   # reached end — valid partition
            return

        for end in range(start + 1, len(s) + 1):
            substring = s[start:end]
            if is_palindrome(substring):      # PRUNE: only recurse if palindrome
                current.append(substring)     # CHOOSE
                backtrack(end, current)       # EXPLORE from next position
                current.pop()                 # UNCHOOSE

    backtrack(0, [])
    return result

# palindrome_partitioning("aab") → [["a","a","b"],["aa","b"]]
```

**Why:** The palindrome check is the pruning condition — we only explore branches where the current cut produces a valid palindrome substring. Without this, every partition would be explored, and invalid ones would only be detected at the end.

**Time:** O(n * 2^n) — 2^n possible partitions, palindrome check O(n).
**Space:** O(n) recursion depth.
</details>

---

<a id="q15"></a>
### Q15

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


**Implement `word_search(board, word)` returning True if the word exists in the 2D grid (4-directional, no cell reuse).**

<details>
<summary>Hint</summary>
Mark the cell as visited before recursing. Unmark it after. Use `#` as a temporary marker to avoid a separate visited set.
</details>

<details>
<summary>Answer</summary>

```python
def word_search(board: list[list[str]], word: str) -> bool:
    ROWS, COLS = len(board), len(board[0])

    def dfs(r: int, c: int, idx: int) -> bool:
        if idx == len(word):
            return True          # base case: matched all characters
        if not (0 <= r < ROWS and 0 <= c < COLS):
            return False
        if board[r][c] != word[idx]:
            return False         # prune: wrong character

        temp, board[r][c] = board[r][c], '#'   # CHOOSE: mark visited

        found = any(
            dfs(r + dr, c + dc, idx + 1)
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]
        )

        board[r][c] = temp       # UNCHOOSE: restore cell

        return found

    return any(dfs(r, c, 0) for r in range(ROWS) for c in range(COLS))

# word_search([["A","B","C"],["S","F","C"],["A","D","E"]], "ABCCED") → True
```

**Why:** Replacing the cell with `#` temporarily marks it as "currently in the path." Restoring it after the call allows other search paths starting from different positions to reuse it. This is the choose-explore-unchoose pattern applied to a grid.

**Time:** O(ROWS * COLS * 4^len(word)).
**Space:** O(len(word)) recursion depth.
</details>

---

<a id="q16"></a>
### Q16

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


**Implement `generate_parentheses(n)` returning all valid combinations of n pairs of parentheses.**

<details>
<summary>Hint</summary>
Track `open` count and `close` count. You can add `(` if open < n. You can add `)` if close < open.
</details>

<details>
<summary>Answer</summary>

```python
def generate_parentheses(n: int) -> list[str]:
    result = []

    def backtrack(current: list[str], open_count: int, close_count: int) -> None:
        if len(current) == 2 * n:
            result.append("".join(current))
            return

        if open_count < n:
            current.append("(")           # CHOOSE open
            backtrack(current, open_count + 1, close_count)
            current.pop()                 # UNCHOOSE

        if close_count < open_count:
            current.append(")")           # CHOOSE close
            backtrack(current, open_count, close_count + 1)
            current.pop()                 # UNCHOOSE

    backtrack([], 0, 0)
    return result

# generate_parentheses(3) → ["((()))","(()())","(())()","()(())","()()()"]
```

**Why:** The two constraint checks (`open < n` and `close < open`) are the pruning conditions. They ensure we never add a `)` before a matching `(`, and never exceed n pairs. This prunes the tree down from 2^(2n) branches to the Catalan number C(n) — dramatically fewer.

**Time:** O(4^n / sqrt(n)) — the nth Catalan number.
**Space:** O(n) recursion depth.
</details>

---

<a id="q17"></a>
### Q17

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


**Implement `subsets_with_dup(nums)` when `nums` may contain duplicates. Return unique subsets only.**

<details>
<summary>Hint</summary>
Sort first. Skip when `i > start and nums[i] == nums[i-1]`.
</details>

<details>
<summary>Answer</summary>

```python
def subsets_with_dup(nums: list[int]) -> list[list[int]]:
    nums.sort()           # group duplicates together
    result = []

    def backtrack(start: int, current: list[int]) -> None:
        result.append(current[:])

        for i in range(start, len(nums)):
            # Skip duplicate value at the same recursion level
            if i > start and nums[i] == nums[i - 1]:
                continue
            current.append(nums[i])
            backtrack(i + 1, current)
            current.pop()

    backtrack(0, [])
    return result

# subsets_with_dup([1,1,2]) → [[],[1],[1,1],[1,1,2],[1,2],[2]]
```

**Why:** After sorting, duplicates are adjacent. At any recursion level, if we're about to pick the same value as the previous sibling branch (`i > start and nums[i] == nums[i-1]`), that entire subtree would generate identical subsets. We skip it. The `i > start` guard (not `i > 0`) ensures we don't skip elements that are legitimately first at a deeper level.

**Time:** O(2^n * n).
**Space:** O(n) recursion depth.
</details>

---

<a id="q18"></a>
### Q18

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


**Implement `permutations_unique(nums)` when `nums` may contain duplicates. Return unique permutations.**

<details>
<summary>Hint</summary>
Sort first. In the used-array approach, skip when `nums[i] == nums[i-1] and not used[i-1]`.
</details>

<details>
<summary>Answer</summary>

```python
def permutations_unique(nums: list[int]) -> list[list[int]]:
    nums.sort()
    result = []
    used = [False] * len(nums)

    def backtrack(current: list[int]) -> None:
        if len(current) == len(nums):
            result.append(current[:])
            return

        for i in range(len(nums)):
            if used[i]:
                continue
            # Skip duplicate: same value AND previous occurrence not yet used
            # means the previous occurrence's subtree is identical to this one
            if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                continue
            used[i] = True
            current.append(nums[i])
            backtrack(current)
            current.pop()
            used[i] = False

    backtrack([])
    return result

# permutations_unique([1,1,2]) → [[1,1,2],[1,2,1],[2,1,1]]
```

**Why:** `not used[i-1]` means element at `i-1` was already processed and its subtree fully explored at this recursion level. Exploring element at `i` (same value) would produce identical results — so we skip it. Without this guard, `[1a, 1b, 2]` and `[1b, 1a, 2]` both appear in the output.

**Time:** O(n! * n) worst case; fewer with pruning.
**Space:** O(n) recursion depth.
</details>

---

<a id="q19"></a>
### Q19

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


**When should you use backtracking vs DP? Give a decision framework.**

<details>
<summary>Hint</summary>
Key questions: Do you need ALL solutions? Are there overlapping subproblems?
</details>

<details>
<summary>Answer</summary>

```
Decision flowchart:

1. Do you need ALL solutions enumerated?
   YES → Backtracking (DP cannot enumerate)
   NO  → go to 2

2. Does the problem have overlapping subproblems?
   (Can the same sub-state be reached via multiple paths?)
   YES → DP (memoization/tabulation)
   NO  → go to 3

3. Is n small (≤ 20 for subsets, ≤ 12 for permutations)?
   YES → Backtracking is feasible
   NO  → Need greedy, DP, or a smarter algorithm
```

| Problem | Use |
|---|---|
| Generate all subsets | Backtracking |
| Does a subset summing to target exist? | Either (DP for large n) |
| Count subsets summing to target | DP (overlapping subproblems) |
| Generate all permutations | Backtracking |
| Longest common subsequence | DP |
| N-Queens all solutions | Backtracking |
| Coin change (min coins) | DP |
| Word search in grid | Backtracking |

**Why:** DP cannot enumerate; it only stores aggregated values (count, min, max). Backtracking cannot efficiently handle overlapping subproblems without memoization (which turns it into top-down DP).

**Time/Space:** Problem-specific; the framework helps you pick the right one before estimating.
</details>

---

<a id="q20"></a>
### Q20

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


**Before writing any code, how do you estimate whether a backtracking solution is feasible for a given n?**

<details>
<summary>Hint</summary>
Calculate the state space size. A solution touching more than ~10^8 nodes per second is too slow.
</details>

<details>
<summary>Answer</summary>

```
Estimate the number of nodes in the state space tree:

Pattern         Formula       n=10      n=15        n=20
─────────────────────────────────────────────────────────
Subsets         2^n           1,024     32,768      1,048,576    ← OK up to ~30
Permutations    n!            3.6M      1.3T        2.4*10^18   ← OK up to ~12
Combinations    C(n,k)        varies    varies      varies       ← usually fine
N-Queens        n!            fast      fast        with pruning
Sudoku          9^81          HUGE      —           pruning saves it
```

**Rule of thumb:** A Python backtracking solution processes roughly 10^6–10^7 nodes per second. If the unpruned state space exceeds 10^8, you need either:
- Aggressive pruning (reduce effective branching factor)
- Memoization (convert to DP)
- A fundamentally different algorithm

**Example decision:**
- n=25 subsets: 2^25 = 33M — borderline, likely OK with pruning.
- n=13 permutations: 13! = 6.2B — too slow without radical pruning.

**Why:** Estimating before coding saves time. Many interview candidates write a correct backtracking solution that TLEs on n=20; a complexity estimate beforehand avoids this.
</details>

---

## Advanced (Q21–Q25)

---

<a id="q21"></a>
### Q21

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)


**Implement `solve_n_queens(n)` returning all valid placements of n queens on an n×n board. Use O(1) conflict detection.**

<details>
<summary>Hint</summary>
Track three sets: `cols`, `diag1` (row-col constant), `diag2` (row+col constant). Check all three before placing.
</details>

<details>
<summary>Answer</summary>

```python
def solve_n_queens(n: int) -> list[list[str]]:
    result = []
    cols: set[int] = set()
    diag1: set[int] = set()   # row - col = constant along '\' diagonal
    diag2: set[int] = set()   # row + col = constant along '/' diagonal
    queens: list[int] = []    # queens[row] = column of queen in that row

    def backtrack(row: int) -> None:
        if row == n:
            board = ["." * q + "Q" + "." * (n - q - 1) for q in queens]
            result.append(board)
            return

        for col in range(n):
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue              # PRUNE: conflict with existing queen

            # CHOOSE
            cols.add(col)
            diag1.add(row - col)
            diag2.add(row + col)
            queens.append(col)

            # EXPLORE
            backtrack(row + 1)

            # UNCHOOSE
            cols.remove(col)
            diag1.remove(row - col)
            diag2.remove(row + col)
            queens.pop()

    backtrack(0)
    return result

# solve_n_queens(4) → 2 solutions
# Known counts: n=8 → 92 solutions, n=9 → 352 solutions
```

**Why the three sets work:**
```
A queen at (row, col) attacks:
  Same column:   col is constant          → store in cols
  '\' diagonal:  row - col is constant   → store in diag1
  '/' diagonal:  row + col is constant   → store in diag2

Checking all three is O(1) vs O(n) for scanning the board.
```

**Time:** O(n!) — n choices for row 0, at most n-1 for row 1, etc.
**Space:** O(n) for sets + O(n) recursion depth.
</details>

---

<a id="q22"></a>
### Q22

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)


**Implement `solve_sudoku(board)` that fills a 9x9 board in-place. Return True if solved.**

<details>
<summary>Hint</summary>
Find the first empty cell, try digits 1-9, validate row/col/box, recurse. If no digit works, return False to trigger backtracking.
</details>

<details>
<summary>Answer</summary>

```python
def solve_sudoku(board: list[list[str]]) -> bool:
    def is_valid(row: int, col: int, num: str) -> bool:
        # Check row
        if num in board[row]:
            return False
        # Check column
        if any(board[r][col] == num for r in range(9)):
            return False
        # Check 3x3 box
        box_r, box_c = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_r, box_r + 3):
            for c in range(box_c, box_c + 3):
                if board[r][c] == num:
                    return False
        return True

    def backtrack() -> bool:
        # Find next empty cell
        for r in range(9):
            for c in range(9):
                if board[r][c] == '.':
                    for num in "123456789":
                        if is_valid(r, c, num):
                            board[r][c] = num          # CHOOSE
                            if backtrack():            # EXPLORE
                                return True
                            board[r][c] = '.'          # UNCHOOSE
                    return False   # no valid digit → backtrack to previous cell
        return True   # no empty cell found → solved

    return backtrack()
```

**Why `return False` matters:** When no digit 1-9 works for the current empty cell, we must signal failure to the caller so it can undo its last placement. Without `return False`, the function would return `None` (falsy), which accidentally works — but `return False` is explicit and correct.

**Time:** O(9^m) where m = number of empty cells. With constraint pruning, typical puzzles are fast.
**Space:** O(m) recursion depth.
</details>

---

<a id="q23"></a>
### Q23

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)


**List and explain 5 distinct pruning techniques used in backtracking. Show code for each.**

<details>
<summary>Hint</summary>
Think: early termination by value, duplicate skipping, feasibility check, constraint sets, and visited state.
</details>

<details>
<summary>Answer</summary>

**Technique 1 — Sorted break (value exceeds limit):**
```python
candidates.sort()
for i in range(start, len(candidates)):
    if candidates[i] > remaining:
        break   # all subsequent also too large — exit loop entirely
```

**Technique 2 — Duplicate skip (same-level sibling):**
```python
nums.sort()
for i in range(start, len(nums)):
    if i > start and nums[i] == nums[i - 1]:
        continue   # identical subtree as previous sibling — skip
```

**Technique 3 — Feasibility check (not enough elements):**
```python
remaining_needed = k - len(current)
available = n - start + 1
if available < remaining_needed:
    return   # cannot fill k slots — prune this path
```

**Technique 4 — O(1) constraint sets (N-Queens):**
```python
if col in cols or (row - col) in diag1 or (row + col) in diag2:
    continue   # conflict detected in O(1) — prune this column
```

**Technique 5 — In-place visited marker (grid DFS):**
```python
temp, board[r][c] = board[r][c], '#'   # mark visited
dfs(r + 1, c, idx + 1)
board[r][c] = temp                      # unmark (unchoose)
# If board[r][c] == '#': prune — already on current path
```

**Why pruning matters:** Sudoku's theoretical O(9^81) search space runs in microseconds with constraint propagation. N-Queens with n=12 has 479M unconstrained nodes but only 14,200 valid solutions — pruning eliminates ~99.997% of the search.

**Time/Space:** Pruning reduces explored nodes; the more constraints, the greater the reduction.
</details>

---

<a id="q24"></a>
### Q24

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)


**Implement `letter_combinations(digits)` returning all possible letter combinations for a phone number string.**

<details>
<summary>Hint</summary>
Map each digit to its letters. For each digit, try every letter and recurse to the next digit.
</details>

<details>
<summary>Answer</summary>

```python
def letter_combinations(digits: str) -> list[str]:
    if not digits:
        return []

    phone_map = {
        "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"
    }

    result = []

    def backtrack(idx: int, current: list[str]) -> None:
        if idx == len(digits):
            result.append("".join(current))
            return

        for letter in phone_map[digits[idx]]:
            current.append(letter)           # CHOOSE
            backtrack(idx + 1, current)      # EXPLORE
            current.pop()                    # UNCHOOSE

    backtrack(0, [])
    return result

# letter_combinations("23") → ["ad","ae","af","bd","be","bf","cd","ce","cf"]
```

**Why:** This is a clean combination problem — at each position (digit), choose one of 3-4 letters. No pruning needed because every leaf is valid. The number of results is the product of letter counts per digit: 3^k or 4^k depending on digits used.

**Time:** O(4^n * n) where n = len(digits) (4 is max letters per digit).
**Space:** O(n) recursion depth.
</details>

---

<a id="q25"></a>
### Q25

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)


**Implement `restore_ip_addresses(s)` returning all valid IP addresses that can be formed from string `s`.**

<details>
<summary>Hint</summary>
An IP has exactly 4 parts, each 0-255. Prune: no leading zeros (except "0" itself), each part <= 255, remaining string must be completable.
</details>

<details>
<summary>Answer</summary>

```python
def restore_ip_addresses(s: str) -> list[str]:
    result = []

    def backtrack(start: int, parts: list[str]) -> None:
        if len(parts) == 4:
            if start == len(s):         # used all characters
                result.append(".".join(parts))
            return

        # Pruning: remaining characters must be completable
        remaining_parts = 4 - len(parts)
        remaining_chars = len(s) - start
        if remaining_chars < remaining_parts or remaining_chars > remaining_parts * 3:
            return

        for length in range(1, 4):     # each part is 1, 2, or 3 digits
            if start + length > len(s):
                break
            segment = s[start:start + length]

            # Prune: no leading zeros (e.g., "01" invalid), value <= 255
            if len(segment) > 1 and segment[0] == '0':
                break
            if int(segment) > 255:
                break

            parts.append(segment)                  # CHOOSE
            backtrack(start + length, parts)       # EXPLORE
            parts.pop()                            # UNCHOOSE

    backtrack(0, [])
    return result

# restore_ip_addresses("25525511135") → ["255.255.11.135","255.255.111.35"]
# restore_ip_addresses("0000") → ["0.0.0.0"]
```

**Why:** The feasibility pruning (`remaining_chars < remaining_parts or remaining_chars > remaining_parts * 3`) is critical — it immediately eliminates branches where the remaining string is too short or too long to form valid parts. The leading-zero and value checks prune invalid segments before recursion.

**Time:** O(3^4) = O(81) — at most 4 parts, each tries lengths 1-3.
**Space:** O(4) recursion depth (always exactly 4 levels).
</details>

---

## Navigation

**[Back to README](../README.md)**

**Prev:** [Interview Q&A](./interview.md) &nbsp;|&nbsp; **Next:** [Dynamic Programming — Theory](../21_dynamic_programming/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
