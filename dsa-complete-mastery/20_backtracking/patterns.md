# Backtracking — Pattern Recognition Guide

> **Core Idea**: Systematically explore all possibilities by making choices, recursing into them,
> and undoing (backtracking) when a path fails or completes. It's a controlled brute-force
> that prunes invalid branches early.

---

## 1. The Universal Backtracking Template

Every backtracking problem maps onto this exact structure:

```python
def backtrack(state, choices, result):
    # BASE CASE: is this a complete solution?
    if is_complete(state):
        result.append(copy_of(state))   # IMPORTANT: copy, not reference
        return

    for choice in choices:
        # --- CHOOSE ---
        if not is_valid(choice, state):   # pruning: skip invalid choices
            continue
        make_choice(state, choice)         # add choice to current state

        # --- EXPLORE ---
        backtrack(state, next_choices(choices, choice), result)

        # --- UNCHOOSE (backtrack) ---
        undo_choice(state, choice)         # restore state for next iteration
```

**The three steps are sacred**:
1. **Choose**: add element to current path/state
2. **Explore**: recurse with updated state
3. **Unchoose**: remove element, restore state

**Why copy in base case?** Python list/dict are references. If you append `state` directly,
all entries in `result` will point to the same (empty) list at the end.

---

## 2. Pattern Recognition Signals

| Signal | Pattern |
|--------|---------|
| "Generate all…", "Find all…" | Backtracking (not DP) |
| "Combinations", "Subsets", "Permutations" | Backtracking |
| "Can you arrange/place such that…" | Constraint satisfaction |
| No duplicate solutions wanted | Need pruning / skip-duplicate trick |
| Count solutions (not enumerate) | Can use backtracking OR DP |
| Optimal solution only | Prefer DP (backtracking too slow) |

**Backtracking vs DP rule**:
```
Can the problem be broken into OVERLAPPING subproblems?
  → Yes: try DP first (memoization)
  → No / Need all solutions: Backtracking

Does the problem ask for ALL solutions (not just count/optimal)?
  → Always backtracking
```

---

## 3. Pattern 1: Generate All Subsets (Power Set)

**Decision model**: For each element, make a binary choice: include it or exclude it.
This creates a binary decision tree of depth n.

**State space**: 2^n subsets (every element independently in or out)

### Template

```python
def subsets(nums):
    result = []

    def backtrack(start, current):
        result.append(current[:])   # record every node (not just leaves)

        for i in range(start, len(nums)):
            current.append(nums[i])         # CHOOSE: include nums[i]
            backtrack(i + 1, current)       # EXPLORE: move to next elements
            current.pop()                   # UNCHOOSE: remove nums[i]

    backtrack(0, [])
    return result

# The `start` parameter is the key: it ensures we only look forward,
# never back, so each subset appears exactly once.
```

**Decision tree for [1,2,3]**:
```
                    []
           /        |        \
         [1]       [2]       [3]
        /   \        \
     [1,2] [1,3]    [2,3]
      /
  [1,2,3]
```

---

### Worked Example: Subsets II (with Duplicates)

**Problem**: Input may have duplicates. Return all unique subsets.

```python
def subsets_with_dup(nums):
    nums.sort()   # SORT FIRST: groups duplicates together
    result = []

    def backtrack(start, current):
        result.append(current[:])

        for i in range(start, len(nums)):
            # SKIP DUPLICATE: if same value as previous sibling, skip
            # This prevents [1,2a] and [1,2b] from both being generated
            if i > start and nums[i] == nums[i - 1]:
                continue

            current.append(nums[i])
            backtrack(i + 1, current)
            current.pop()

    backtrack(0, [])
    return result

# Key insight: skip when i > start (not i > 0)
# At the same recursion level (same start), duplicates produce identical subtrees
# We keep the FIRST occurrence, skip subsequent ones at the same level
```

---

### Worked Example: Subset Sum — Does Any Subset Sum to Target?

```python
def subset_sum_exists(nums, target):
    def backtrack(start, remaining):
        if remaining == 0:
            return True   # found a valid subset

        if remaining < 0 or start == len(nums):
            return False  # pruning: overshot or ran out of elements

        for i in range(start, len(nums)):
            if backtrack(i + 1, remaining - nums[i]):
                return True

        return False

    return backtrack(0, target)
```

---

## 4. Pattern 2: Generate All Permutations

**Decision model**: At each position, choose any unused element.
Unlike subsets, ORDER matters — [1,2,3] and [3,2,1] are different.

**State space**: n! permutations

### Template — Used-Array Approach

```python
def permutations(nums):
    result = []
    used = [False] * len(nums)

    def backtrack(current):
        if len(current) == len(nums):    # all elements placed
            result.append(current[:])
            return

        for i in range(len(nums)):
            if used[i]:                  # skip already-used elements
                continue

            used[i] = True               # CHOOSE
            current.append(nums[i])

            backtrack(current)           # EXPLORE

            current.pop()               # UNCHOOSE
            used[i] = False

    backtrack([])
    return result
```

### Template — Swap-Based Approach (in-place, slightly faster)

```python
def permutations_swap(nums):
    result = []

    def backtrack(start):
        if start == len(nums):
            result.append(nums[:])
            return

        for i in range(start, len(nums)):
            nums[start], nums[i] = nums[i], nums[start]   # CHOOSE: swap into position
            backtrack(start + 1)                           # EXPLORE
            nums[start], nums[i] = nums[i], nums[start]   # UNCHOOSE: swap back

    backtrack(0)
    return result
```

---

### Worked Example: Permutations II (with Duplicates)

```python
def permutations_unique(nums):
    nums.sort()
    result = []
    used = [False] * len(nums)

    def backtrack(current):
        if len(current) == len(nums):
            result.append(current[:])
            return

        for i in range(len(nums)):
            if used[i]:
                continue

            # Skip duplicate: same value, and previous occurrence not yet used
            # (means we already explored this "branch" via the previous occurrence)
            if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                continue

            used[i] = True
            current.append(nums[i])
            backtrack(current)
            current.pop()
            used[i] = False

    backtrack([])
    return result

# nums=[1,1,2]: without pruning generates [1a,1b,2] and [1b,1a,2] — identical!
# The condition `not used[i-1]` catches this: if 1a is unused at this level,
# we already finished exploring 1a's subtree, so 1b's subtree would be identical.
```

---

## 5. Pattern 3: Generate Combinations

**Decision model**: Choose exactly `k` elements from `n` elements, order does NOT matter.

**State space**: C(n, k) combinations

### Template

```python
def combinations(n, k):
    result = []

    def backtrack(start, current):
        if len(current) == k:       # found a complete combination
            result.append(current[:])
            return

        # PRUNING: not enough elements remaining to complete combination
        # Elements left: n - start + 1
        # Elements needed: k - len(current)
        # Skip if: n - start + 1 < k - len(current)
        remaining_needed = k - len(current)
        for i in range(start, n - remaining_needed + 2):   # pruned upper bound
            current.append(i)
            backtrack(i + 1, current)
            current.pop()

    backtrack(1, [])
    return result
```

---

### Worked Example: Combination Sum (Reuse Allowed)

**Problem**: Find all combinations that sum to target. Elements can be reused.

```python
def combination_sum(candidates, target):
    candidates.sort()   # sort enables early termination
    result = []

    def backtrack(start, current, remaining):
        if remaining == 0:
            result.append(current[:])
            return

        for i in range(start, len(candidates)):
            if candidates[i] > remaining:   # PRUNE: sorted, so rest are also too big
                break

            current.append(candidates[i])
            backtrack(i, current, remaining - candidates[i])   # i (not i+1): reuse allowed
            current.pop()

    backtrack(0, [], target)
    return result
```

### Worked Example: Combination Sum II (No Reuse, Possible Duplicates)

```python
def combination_sum_2(candidates, target):
    candidates.sort()
    result = []

    def backtrack(start, current, remaining):
        if remaining == 0:
            result.append(current[:])
            return

        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                break

            # Skip duplicates at the same recursion level
            if i > start and candidates[i] == candidates[i - 1]:
                continue

            current.append(candidates[i])
            backtrack(i + 1, current, remaining - candidates[i])  # i+1: no reuse
            current.pop()

    backtrack(0, [], target)
    return result
```

---

## 6. Pattern 4: Constraint Satisfaction

**Decision model**: Place/assign values to positions such that hard constraints are met.
Check validity BEFORE recursing to avoid exploring invalid branches.

**Key principle**: Write `is_valid()` efficiently — it should run in O(constraint_size), not O(n²).

**When to use**:
- N-Queens placement
- Sudoku solver
- Graph coloring
- Word search in grid

### Template

```python
def constraint_satisfaction(board, choices):
    result = []

    def backtrack(pos):
        if is_complete(board, pos):
            result.append(copy_board(board))
            return

        for choice in choices:
            if is_valid(board, pos, choice):   # check BEFORE recursing
                apply(board, pos, choice)      # CHOOSE
                backtrack(next_pos(pos))       # EXPLORE
                undo(board, pos, choice)       # UNCHOOSE

    backtrack(start_pos)
    return result
```

---

### Worked Example: N-Queens

```python
def solve_n_queens(n):
    result = []
    # Track occupied columns and diagonals for O(1) validity check
    cols = set()
    diag1 = set()   # row - col = constant for '/' diagonals
    diag2 = set()   # row + col = constant for '\' diagonals

    board = [['.' for _ in range(n)] for _ in range(n)]

    def backtrack(row):
        if row == n:
            result.append([''.join(r) for r in board])
            return

        for col in range(n):
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue  # PRUNE: conflicts

            # CHOOSE
            cols.add(col)
            diag1.add(row - col)
            diag2.add(row + col)
            board[row][col] = 'Q'

            # EXPLORE
            backtrack(row + 1)

            # UNCHOOSE
            cols.remove(col)
            diag1.remove(row - col)
            diag2.remove(row + col)
            board[row][col] = '.'

    backtrack(0)
    return result

# Key efficiency: using sets for O(1) conflict check instead of scanning board
```

---

### Worked Example: Sudoku Solver

```python
def solve_sudoku(board):
    def is_valid(row, col, num):
        # Check row
        if num in board[row]:
            return False
        # Check column
        if num in [board[r][col] for r in range(9)]:
            return False
        # Check 3x3 box
        box_r, box_c = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_r, box_r + 3):
            for c in range(box_c, box_c + 3):
                if board[r][c] == num:
                    return False
        return True

    def backtrack():
        for r in range(9):
            for c in range(9):
                if board[r][c] == '.':
                    for num in '123456789':
                        if is_valid(r, c, num):
                            board[r][c] = num          # CHOOSE
                            if backtrack():            # EXPLORE
                                return True
                            board[r][c] = '.'          # UNCHOOSE
                    return False   # no valid number works → backtrack
        return True   # no empty cell found → solved

    backtrack()
```

---

## 7. Pruning Strategies

Pruning is what separates a slow backtracking solution from a fast one.

### Strategy 1: Early Termination (Constraint Pruning)

```python
# Before entering a branch, check if it can possibly lead to a solution
for i in range(start, len(candidates)):
    if candidates[i] > remaining:   # sorted → rest are also too large
        break                       # prune entire remaining loop, not just this iteration
```

### Strategy 2: Skip Duplicates (Sort + Skip)

```python
# Always sort first, then skip same-value siblings
nums.sort()
for i in range(start, len(nums)):
    if i > start and nums[i] == nums[i - 1]:
        continue   # same subtree as previous sibling
```

### Strategy 3: Bound Checking (Feasibility Pruning)

```python
# "Can we even complete a valid solution from here?"
remaining_needed = k - len(current)
available = n - start + 1
if available < remaining_needed:
    return   # not enough elements left to fill k spots
```

### Strategy 4: Constraint Propagation (Sudoku / N-Queens)

Track which values are "taken" using sets or bitmasking for O(1) lookups:

```python
# Instead of scanning the board every time:
rows = [set() for _ in range(9)]
cols = [set() for _ in range(9)]
boxes = [set() for _ in range(9)]

# O(1) validity check:
def is_valid(r, c, num):
    box_id = (r // 3) * 3 + (c // 3)
    return num not in rows[r] and num not in cols[c] and num not in boxes[box_id]
```

---

## 8. Backtracking vs DP Decision Guide

```
Ask these questions:

1. Do you need ALL solutions (not just count/optimal)?
   → YES → Backtracking

2. Does the problem have overlapping subproblems?
   (Same sub-state reached via multiple paths?)
   → YES → DP (memoization)

3. Does the problem ask for OPTIMAL (max/min) or COUNT?
   → Optimal/Count + overlapping subproblems → DP
   → Optimal/Count without overlapping → Greedy or Backtracking + memo

4. Is the state space small enough to enumerate?
   → n ≤ 20 typically → Backtracking OK
   → n ≤ 1000 → Need DP or smarter algorithm

5. Does order matter in a non-trivial way?
   → Permutation-like → Backtracking
   → Interval/sequence → DP
```

| Problem | Backtracking | DP |
|---------|-------------|-----|
| Generate all subsets | Yes | No (need enumeration) |
| Does a subset summing to target exist? | Yes (small n) | Yes (larger n) |
| Count subsets summing to target | Yes (small n) | Yes (preferred) |
| All permutations | Yes | No |
| Longest common subsequence | Too slow | Yes |
| N-Queens (all solutions) | Yes | No |
| Coin change (min coins) | Too slow | Yes |
| Word search in grid | Yes | No |

---

## 9. State Space Complexity — Estimating Before Coding

Before writing a backtracking solution, estimate if it's feasible:

```
Subsets:       O(2^n × n)   — 2^n nodes, O(n) to copy each
               n=20: ~20M   operations → OK
               n=30: ~30B   operations → Too slow

Permutations:  O(n! × n)
               n=8:  ~320K  → OK
               n=12: ~5.7B  → borderline
               n=15: too slow

Combinations:  O(C(n,k) × k)
               Usually much better than 2^n

Constraint:    O(n^m × valid_prune_factor)
               N-Queens n=8: 8^8 = 16M, pruning → ~92 solutions
               Sudoku: 9^81 worst case, but pruning reduces drastically
```

**Rule of thumb**: If state space > 10^8 without aggressive pruning, reconsider approach.

---

## 10. Template Variants at a Glance

```python
# SUBSETS — record every node, use `start` to avoid revisiting
def subsets(nums, start=0, curr=[]):
    result.append(curr[:])
    for i in range(start, len(nums)):
        curr.append(nums[i]); backtrack(i+1, curr); curr.pop()

# PERMUTATIONS — record only leaves, use `used` array
def permutations(nums, used, curr=[]):
    if len(curr) == len(nums): result.append(curr[:]); return
    for i in range(len(nums)):
        if not used[i]:
            used[i]=True; curr.append(nums[i]); backtrack(nums,used,curr)
            curr.pop(); used[i]=False

# COMBINATIONS — record only leaves, use `start` + size check
def combinations(n, k, start=1, curr=[]):
    if len(curr) == k: result.append(curr[:]); return
    for i in range(start, n+1):
        curr.append(i); backtrack(i+1, curr); curr.pop()

# CONSTRAINT — check validity before placing, undo after
def constraint(board, pos):
    if complete(board): result.append(copy(board)); return
    for choice in choices:
        if valid(board, pos, choice):
            place(board, pos, choice); backtrack(next(pos)); undo(board, pos, choice)
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Real World Usage →](./real_world_usage.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
