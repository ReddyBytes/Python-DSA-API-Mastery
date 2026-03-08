# Backtracking — Quick Reference Cheatsheet

## Core Mental Model

```
CHOOSE   → make a decision (add to path, mark visited, etc.)
EXPLORE  → recurse with updated state
UNCHOOSE → undo the decision (backtrack — restore previous state)

Key insight: backtracking is DFS on a decision tree.
Prune branches early to avoid exploring invalid/suboptimal states.
```

---

## Universal Backtracking Template

```python
def backtrack(state, choices, result):
    # BASE CASE: valid complete solution
    if is_complete(state):
        result.append(state[:])    # copy state — don't store reference
        return

    for choice in choices:
        if is_valid(state, choice):     # PRUNING — skip invalid choices
            # CHOOSE
            state.append(choice)
            mark_used(choice)

            # EXPLORE
            backtrack(state, updated_choices, result)

            # UNCHOOSE
            state.pop()
            unmark_used(choice)

result = []
backtrack([], all_choices, result)
```

---

## When to Use Backtracking

```
- Generate ALL permutations / combinations / subsets
- Constraint satisfaction (Sudoku, N-Queens, crossword)
- Path finding with constraints (maze, word search)
- Partition problems (divide into groups meeting criteria)
- String problems (generate valid parentheses, palindrome partitioning)
- Decision problems where you must explore all options
```

---

## Time & Space Complexity

```
General: O(b^d) where b = branching factor, d = depth (recursion depth)

Pattern-specific:
  Subsets of n items:     O(2^n)     — each item: include or exclude
  Permutations of n:      O(n!)      — n choices, n-1, n-2, ...
  Combinations C(n,k):    O(C(n,k))  — n choose k
  N-Queens:               O(n!)      — pruning reduces in practice

Space: O(d) for recursion stack + O(result size) for output
```

---

## Pattern 1: Subsets (Include / Exclude)

```python
def subsets(nums):
    result = []

    def backtrack(index, current):
        result.append(current[:])       # every node is a valid subset

        for i in range(index, len(nums)):
            current.append(nums[i])     # CHOOSE: include nums[i]
            backtrack(i + 1, current)   # EXPLORE: move forward (no repeats)
            current.pop()               # UNCHOOSE

    backtrack(0, [])
    return result

# State space tree for [1, 2, 3]:
#              []
#           /  |  \
#         [1] [2] [3]
#        /  \   \
#     [1,2][1,3][2,3]
#       |
#    [1,2,3]
```

### Subsets with Duplicates

```python
def subsets_with_dups(nums):
    nums.sort()                         # sort to group duplicates
    result = []

    def backtrack(index, current):
        result.append(current[:])
        for i in range(index, len(nums)):
            if i > index and nums[i] == nums[i-1]:  # skip duplicate at same level
                continue
            current.append(nums[i])
            backtrack(i + 1, current)
            current.pop()

    backtrack(0, [])
    return result
```

---

## Pattern 2: Permutations (Swap / Used Array)

```python
def permutations(nums):
    result = []

    def backtrack(current, used):
        if len(current) == len(nums):
            result.append(current[:])
            return

        for i in range(len(nums)):
            if used[i]:
                continue            # PRUNE: already in current path
            used[i] = True
            current.append(nums[i])
            backtrack(current, used)
            current.pop()
            used[i] = False

    backtrack([], [False] * len(nums))
    return result

# Alternate: swap-based (in-place, modifies input)
def permutations_swap(nums):
    result = []

    def backtrack(start):
        if start == len(nums):
            result.append(nums[:])
            return
        for i in range(start, len(nums)):
            nums[start], nums[i] = nums[i], nums[start]   # CHOOSE
            backtrack(start + 1)                           # EXPLORE
            nums[start], nums[i] = nums[i], nums[start]   # UNCHOOSE

    backtrack(0)
    return result
```

---

## Pattern 3: Combinations (With Index, No Repeats)

```python
def combinations(n, k):
    result = []

    def backtrack(start, current):
        if len(current) == k:
            result.append(current[:])
            return

        # Pruning: need k - len(current) more; max start = n - (k - len(current)) + 1
        for i in range(start, n - (k - len(current)) + 2):
            current.append(i)
            backtrack(i + 1, current)
            current.pop()

    backtrack(1, [])
    return result

# Combination Sum (can reuse elements)
def combination_sum(candidates, target):
    result = []

    def backtrack(index, current, remaining):
        if remaining == 0:
            result.append(current[:])
            return
        if remaining < 0:               # PRUNE: exceeded target
            return

        for i in range(index, len(candidates)):
            current.append(candidates[i])
            backtrack(i, current, remaining - candidates[i])    # i (not i+1) to reuse
            current.pop()

    backtrack(0, [], target)
    return result
```

---

## Pruning Techniques

```
1. RANGE PRUNING: Limit loop range early.
   combinations(n, k): stop loop at n - (k - len(path)) + 1

2. CONSTRAINT CHECK: Validate before recursing.
   if remaining < 0: return   (combination sum)

3. SORTED INPUT: Sort to enable early termination.
   if candidates[i] > remaining: break  (after sorting)

4. VISITED SET: Avoid revisiting same state.
   if (row, col) in visited: continue  (grid problems)

5. DUPLICATE SKIP: Skip identical choices at same level.
   if i > start and nums[i] == nums[i-1]: continue

6. SYMMETRY BREAKING: Place queen in first half only (N-Queens variant).
```

---

## N-Queens Template

```python
def solve_n_queens(n):
    result = []
    cols = set()
    diag1 = set()   # row - col (top-left to bottom-right diagonal)
    diag2 = set()   # row + col (top-right to bottom-left diagonal)

    board = [['.'] * n for _ in range(n)]

    def backtrack(row):
        if row == n:
            result.append([''.join(r) for r in board])
            return

        for col in range(n):
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue            # PRUNE: conflicts

            # CHOOSE
            cols.add(col)
            diag1.add(row - col)
            diag2.add(row + col)
            board[row][col] = 'Q'

            backtrack(row + 1)      # EXPLORE

            # UNCHOOSE
            cols.remove(col)
            diag1.remove(row - col)
            diag2.remove(row + col)
            board[row][col] = '.'

    backtrack(0)
    return result
# Time: O(n!)  |  Each row: progressively fewer valid columns
```

---

## Sudoku Solver Template

```python
def solve_sudoku(board):
    def is_valid(row, col, num):
        box_r, box_c = 3 * (row // 3), 3 * (col // 3)
        for i in range(9):
            if board[row][i] == num: return False       # row conflict
            if board[i][col] == num: return False       # col conflict
            if board[box_r + i//3][box_c + i%3] == num: return False   # box
        return True

    def backtrack():
        for r in range(9):
            for c in range(9):
                if board[r][c] == '.':
                    for num in '123456789':
                        if is_valid(r, c, num):
                            board[r][c] = num           # CHOOSE
                            if backtrack():
                                return True             # EXPLORE — propagate success
                            board[r][c] = '.'           # UNCHOOSE
                    return False                        # no valid num → backtrack
        return True                                     # board full — solved

    backtrack()
```

---

## State Space Visualization

```
Permutations of [1, 2, 3] — depth = 3, branching = n - depth

              start=[]
          /       |        \
       [1]       [2]       [3]
      /   \     /   \     /   \
   [1,2][1,3][2,1][2,3][3,1][3,2]
    |     |    |    |    |    |
 [1,2,3][1,3,2]...           [3,2,1]
   ✓      ✓                    ✓

Nodes visited: n! leaves + internal nodes = O(n * n!)
With pruning: eliminate subtrees when constraint violated early
```

---

## Word Search on Grid Template

```python
def word_search(board, word):
    ROWS, COLS = len(board), len(board[0])

    def dfs(r, c, idx):
        if idx == len(word):
            return True
        if not (0 <= r < ROWS and 0 <= c < COLS):
            return False
        if board[r][c] != word[idx]:
            return False

        temp, board[r][c] = board[r][c], '#'    # CHOOSE: mark visited
        found = any(dfs(r+dr, c+dc, idx+1)
                    for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)])
        board[r][c] = temp                       # UNCHOOSE: restore

        return found

    return any(dfs(r, c, 0) for r in range(ROWS) for c in range(COLS))
```

---

## Common Backtracking Problems

```
Subsets:           Subsets, Subsets II (with dups), Power Set
Permutations:      Permutations, Permutations II (with dups), Next Permutation
Combinations:      Combination Sum I/II/III, Letter Combinations of Phone Number
Partitioning:      Palindrome Partitioning, Restore IP Addresses
String:            Generate Parentheses, Word Break II
Grid:              Word Search, Unique Paths with obstacles
Constraint:        N-Queens, Sudoku Solver
Other:             Beautiful Arrangement, Partition Equal Subset Sum (DP too)
```

---

## Common Mistakes

```
MISTAKE 1: Not copying state before appending to result
  Wrong:  result.append(current)       # appends reference — mutates later
  Right:  result.append(current[:])    # copy at leaf node

MISTAKE 2: Forgetting to unchoose (backtrack)
  Always pair: state.append(x) with state.pop()
              visited.add(x) with visited.remove(x)
              board[r][c] = val with board[r][c] = original

MISTAKE 3: Missing duplicate handling
  Sort input first, then skip: if i > start and nums[i] == nums[i-1]: continue
  The condition i > start (not i > 0) prevents skipping first occurrence

MISTAKE 4: Wrong base case — off by one
  Combinations: if len(current) == k → append and return
  Not len(current) >= k (though usually equivalent, be explicit)

MISTAKE 5: Re-using index wrong (combination sum)
  Allow reuse: backtrack(i, ...)      # same index
  No reuse:    backtrack(i + 1, ...) # next index
```
