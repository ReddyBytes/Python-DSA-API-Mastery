# Backtracking — Visual Explanation

Backtracking is **systematic trial and error on a decision tree**. At each node
you make a choice, recurse deeper, and when you hit a dead end (or finish) you
**undo** that choice and try the next option. This section builds the mental
model through pictures.

---

## 1. The Backtracking Tree — Subsets of [1, 2, 3]

Every element has exactly two choices: **include** it or **exclude** it.
The complete exploration tree has 2^3 = 8 leaves, one per subset.

```
Decision variable:    element 1       element 2         element 3
                          │
                    ┌─────┴─────┐
                  INC(1)      EXC(1)
                  [1]           []
               ┌───┴───┐     ┌──┴──┐
           INC(2)  EXC(2)  INC(2) EXC(2)
           [1,2]    [1]     [2]     []
           ┌─┴─┐   ┌─┴─┐  ┌─┴─┐  ┌─┴─┐
         I(3) E(3) I(3) E(3) I(3) E(3) I(3) E(3)
        [1,2,3][1,2][1,3][1] [2,3][2]  [3]  []
           ✓    ✓    ✓   ✓    ✓   ✓    ✓    ✓
```

All 8 leaves are valid subsets — no pruning needed for the plain subsets problem.

---

## 2. Include / Exclude Tree (Detailed)

```
                            []
                    ┌───────┴───────┐
                 include 1        exclude 1
                   [1]               []
             ┌─────┴─────┐     ┌────┴────┐
          inc 2         exc 2  inc 2    exc 2
          [1,2]          [1]   [2]        []
         ┌──┴──┐       ┌─┴─┐  ┌─┴─┐    ┌─┴─┐
       inc 3 exc 3   inc 3 exc 3 inc 3 exc 3 inc 3 exc 3
      [1,2,3] [1,2] [1,3] [1] [2,3] [2] [3]  []
         ✓     ✓     ✓    ✓    ✓    ✓    ✓    ✓
```

The Python code mirrors this tree exactly:

```python
def subsets(nums):
    result = []

    def backtrack(index, current):
        if index == len(nums):
            result.append(list(current))   # leaf node — record answer
            return

        # Branch 1: INCLUDE nums[index]
        current.append(nums[index])
        backtrack(index + 1, current)

        # Branch 2: EXCLUDE nums[index]  (backtrack — undo the append)
        current.pop()
        backtrack(index + 1, current)

    backtrack(0, [])
    return result
```

---

## 3. Pruning Visualization — Subsets with Sum Constraint

Suppose we only want subsets that sum to <= 4, from [1, 2, 3].

```
                            []  sum=0
                    ┌───────┴───────┐
                  [1] sum=1        [] sum=0
             ┌────┴────┐      ┌────┴────┐
          [1,2] s=3  [1] s=1 [2] s=2  [] s=0
         ┌───┴───┐   ┌─┴─┐  ┌─┴─┐   ┌─┴─┐
      [1,2,3]  [1,2] [1,3][1] [2,3] [2] [3] []
       s=6✗    s=3✓  s=4✓ s=1✓ s=5✗ s=2✓ s=3✓ s=0✓
       PRUNED

Crosses (✗) = pruned branches (sum exceeded limit)
Ticks  (✓) = collected as valid answers

Pruned results: [1,2,3] and [2,3]
Collected:      [1,2], [1,3], [1], [2], [3], []
```

With a tighter bound, whole subtrees can be cut:

```
If current_sum + remaining_min > target  →  prune entire subtree
                                             (no need to go deeper)
```

---

## 4. N-Queens Decision Tree — 4-Queens on a 4x4 Board

We place one queen per column, left to right. Each row choice must not conflict
with previously placed queens (same row, or diagonal).

```
Column:         C0           C1              C2         C3
               Q in         Q in           Q in       Q in
              row ?         row ?          row ?      row ?

              row 0         row 2        ──row 0── ✗ (same diagonal)
              ┌──┐          ┌──┐         ──row 1── ✗ (same row/diag)
              │  │          │  │            row 3  → C3: row 1 ✓  SOLUTION
              │Q │  →       │ Q│  →
              │  │          │  │         row 0  → conflict ✗
              └──┘          └──┘         ──row 1── ✗
              .Q..          ..Q.

              row 1         row 3        ──row 1── ✗
              ┌──┐          ┌──┐            row 0 → C3: conflict ✗
              │  │          │  │          ──row 2── ✗
              │  │  →       │  │  →       BACKTRACK
              │Q │          │  Q│
              └──┘          └──┘
              ..Q.          ...Q          (continue exploring)

  One valid solution found: .Q.. / ...Q / Q... / ..Q.
```

Board state for the first solution:

```
  Col:  0  1  2  3
Row 0:  .  Q  .  .
Row 1:  .  .  .  Q
Row 2:  Q  .  .  .
Row 3:  .  .  Q  .
```

```python
def solve_n_queens(n):
    solutions = []
    cols, diag1, diag2 = set(), set(), set()
    board = [['.' ] * n for _ in range(n)]

    def backtrack(row):
        if row == n:
            solutions.append([''.join(r) for r in board])
            return
        for col in range(n):
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue                         # ← PRUNE: conflict detected
            # CHOOSE
            board[row][col] = 'Q'
            cols.add(col); diag1.add(row - col); diag2.add(row + col)
            # EXPLORE
            backtrack(row + 1)
            # UNCHOOSE
            board[row][col] = '.'
            cols.remove(col); diag1.remove(row - col); diag2.remove(row + col)

    backtrack(0)
    return solutions
```

---

## 5. State Restoration — Choose → Explore → Unchoose

This is the heartbeat of every backtracking algorithm.

```
BEFORE CHOOSING element 2:

  current = [1]
  remaining = [2, 3]

  ┌──────────┐
  │  [1]     │  ← current state
  └──────────┘

──────── CHOOSE: append 2 ────────

DURING EXPLORATION:

  current = [1, 2]
  remaining = [3]

  ┌──────────────┐
  │  [1, 2]      │  ← modified state
  └──────────────┘
         │
    recurse deeper...
    collect [1,2,3] and [1,2]

──────── UNCHOOSE: pop 2 ─────────

AFTER UNCHOOSE:

  current = [1]          ← RESTORED to exactly what it was before
  remaining = [2, 3]

  ┌──────────┐
  │  [1]     │  ← back to original state
  └──────────┘

Now try EXCLUDING 2 from [1] ...
```

The key rule: **every mutation made before the recursive call must be undone
after the recursive call returns**. The state must look identical before and
after as seen by the caller.

---

## 6. Permutation Tree — All Permutations of [1, 2, 3]

At each level we pick which element goes in the current position. We swap it
into place, recurse, then swap back (restore).

```
Level 0: start = [1, 2, 3]

swap(0,0)→[1,2,3]    swap(0,1)→[2,1,3]    swap(0,2)→[3,2,1]
     │                    │                    │
Level 1: fix index 0

   [1, 2, 3]              [2, 1, 3]            [3, 2, 1]
   swap(1,1) swap(1,2)  swap(1,1) swap(1,2)  swap(1,1) swap(1,2)
   [1,2,3]  [1,3,2]    [2,1,3]  [2,3,1]    [3,2,1]  [3,1,2]  ← wait, typo
     │         │          │         │          │         │
Level 2: fix index 1 (only one element left = base case)

  [1,2,3]  [1,3,2]    [2,1,3]  [2,3,1]    [3,2,1]  [3,1,2]
     ✓        ✓          ✓        ✓          ✓        ✓
```

Six leaves = 3! = 6 permutations. Each path from root to leaf is one
permutation.

```python
def permutations(nums):
    result = []

    def backtrack(start):
        if start == len(nums):
            result.append(list(nums))      # leaf: record current arrangement
            return
        for i in range(start, len(nums)):
            nums[start], nums[i] = nums[i], nums[start]   # CHOOSE (swap)
            backtrack(start + 1)                           # EXPLORE
            nums[start], nums[i] = nums[i], nums[start]   # UNCHOOSE (swap back)

    backtrack(0)
    return result
```

### Swap trace for permutations([1,2,3])

```
backtrack(start=0)
  i=0: swap(0,0) → [1,2,3]
    backtrack(start=1)
      i=1: swap(1,1) → [1,2,3]
        backtrack(start=2) → RECORD [1,2,3]
      swap back → [1,2,3]
      i=2: swap(1,2) → [1,3,2]
        backtrack(start=2) → RECORD [1,3,2]
      swap back → [1,2,3]
  swap back → [1,2,3]
  i=1: swap(0,1) → [2,1,3]
    ... (records [2,1,3] and [2,3,1])
  swap back → [1,2,3]
  i=2: swap(0,2) → [3,2,1]
    ... (records [3,2,1] and [3,1,2])
  swap back → [1,2,3]
```

---

## Summary — The Backtracking Recipe

```
function backtrack(state, choices):
    if is_solution(state):
        record(state)
        return

    for choice in choices:
        if is_valid(state, choice):      ← PRUNE invalid branches early
            apply(state, choice)         ← CHOOSE
            backtrack(new_state, ...)    ← EXPLORE
            undo(state, choice)          ← UNCHOOSE (restore state)
```

### When to prune

```
  PRUNE when you can prove no valid solution exists in the subtree.
  Good pruning turns exponential into polynomial in practice.

  Weak pruning:   check one constraint at current node
  Strong pruning: project future constraints forward
                  (e.g., Arc Consistency in Sudoku)
```

### Complexity overview

```
Problem              Worst-case tree size   With good pruning
─────────────────────────────────────────────────────────────
Subsets              O(2^n)                 O(2^n) — no improvement
Permutations         O(n!)                  O(n!) — order matters
N-Queens (n×n)       O(n^n)                 O(n!) in practice
Sudoku (9×9)         O(9^81)                ~microseconds with pruning
```

The gap between worst-case and practical performance is why backtracking is
used in production constraint solvers despite its theoretical exponential cost.
