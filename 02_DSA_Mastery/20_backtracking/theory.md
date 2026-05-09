<a id="top"></a>
# Backtracking — The Art of Trying, Undoing, and Trying Again

> Backtracking is intelligent exploration.
>
> It tries a path.
> If it fails,
> it comes back and tries another.
>
> It is controlled brute force.

Backtracking is used when:

- We must explore all possibilities
- We need valid combinations
- We need all solutions
- We must satisfy constraints

It is powerful but can be slow.

## 📖 Table of Contents

1. [Real Life Story — Maze Explorer](#1-real-life-story)
2. [Decision Tree Visualization](#2-decision-tree)
3. [What Is Backtracking?](#3-what-is-backtracking)
4. [The Backtracking Template](#4-the-backtracking-template)
5. [Why Backtracking Is Powerful](#5-why-backtracking-is-powerful)
6. [Classic Backtracking Problems](#6-classic-problems)
7. [Pruning (Very Important)](#7-pruning)
8. [Time Complexity](#8-time-complexity)
9. [Backtracking vs DFS](#9-backtracking-vs-dfs)
10. [Backtracking vs Dynamic Programming](#10-backtracking-vs-dp)
11. [Real-World Applications](#11-real-world-applications)
12. [Mental Model](#12-mental-model)
13. [Final Understanding](#13-final-understanding)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
choose-explore-undo pattern · base case for backtracking · pruning

**Should Learn** — Important for real projects, comes up regularly:
subsets · permutations · combination sum · N-Queens · Sudoku solver

**Good to Know** — Useful in specific situations, not always tested:
backtracking vs DFS distinction · time complexity of backtracking

**Reference** — Know it exists, look up syntax when needed:
constraint propagation · intelligent backtracking · CSP heuristics

<a id="1-real-life-story"></a>
# 1. Real Life Story — Maze Explorer

> 📝 **Practice:** [Q6 · backtracking vs brute force](./practice.md#q6)

Imagine you are inside a maze.

You choose a path.

If it leads to dead end,
you go back.

Try another path.

That is backtracking.

You don't destroy maze.
You explore carefully.

> [↑ Back to Top](#top)

<a id="2-decision-tree"></a>
# 2. Decision Tree Visualization

> 📝 **Practice:** [Q3 · trace the subsets tree](./practice.md#q3)

Suppose we want to generate:

All subsets of [1, 2, 3]

Decision tree:

```
            []
         /         \
       [1]         []
      /   \        /   \
  [1,2]  [1]    [2]    []
   /  \         /  \
[1,2,3] [1,2] [2,3] [2]
```

Every decision:
Include or exclude.

Backtracking explores this tree.

## Visual: Subsets Tree — Full Expansion

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

## Visual: Include / Exclude Tree (Detailed)

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

**Common mistake — appending reference instead of copy:** When you do `result.append(current)` you store a reference to the same list object. Every pop/append during backtracking mutates all stored entries, leaving all results as empty lists. Always use `result.append(current[:])` to capture a snapshot at the moment of recording.

> [↑ Back to Top](#top)

<a id="3-what-is-backtracking"></a>
# 3. What Is Backtracking?

> 📝 **Practice:** [Q2 · write the universal template](./practice.md#q2)

Backtracking is:

A recursive algorithm
that builds solution step-by-step
and abandons (backtracks) when constraint fails.

Core idea:

- Choose
- Explore
- Undo

## Visual: State Restoration — Choose, Explore, Unchoose

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

> [↑ Back to Top](#top)

<a id="4-the-backtracking-template"></a>
# 4. The Backtracking Template

> 📝 **Practice:** [Q2 · write the universal template](./practice.md#q2) · [Q4 · why copy before appending](./practice.md#q4) · [Q5 · base case rules](./practice.md#q5)

```python
def backtrack(path):
    if solution_found:
        save_result
        return

    for choice in possible_choices:
        if valid(choice):
            make_choice
            backtrack(updated_path)
            undo_choice
```

Three key parts:

- Choose
- Recurse
- Undo

Undo is crucial.

## Visual: The Backtracking Recipe

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

**Common mistake — forgetting to undo choice:** If you skip the undo step, the shared `current` list accumulates garbage from previous branches. Every subsequent recursive call sees a corrupted state. The undo must mirror the choose exactly — if you `append`, you must `pop`; if you `add` to a set, you must `remove`.

**Common mistake — wrong base case:** The base case controls when to record a result and when to stop recursing. Too early and you miss valid solutions; too late and you get infinite recursion or index errors. For subsets, trigger at `index == len(nums)`. For permutations, trigger at `len(current) == len(nums)`.

> [↑ Back to Top](#top)

<a id="5-why-backtracking-is-powerful"></a>
# 5. Why Backtracking Is Powerful

> 📝 **Practice:** [Q8 · pruning](./practice.md#q8) · [Q23 · 5 pruning techniques](./practice.md#q23)

It explores all possibilities.

But intelligently:

Stops early if constraint fails.

This is pruning.

Without pruning:
Exponential explosion.

## Visual: Pruning — Subsets with Sum Constraint

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

### When to prune

```
  PRUNE when you can prove no valid solution exists in the subtree.
  Good pruning turns exponential into polynomial in practice.

  Weak pruning:   check one constraint at current node
  Strong pruning: project future constraints forward
                  (e.g., Arc Consistency in Sudoku)
```

**Common mistake — using `continue` instead of `break` in combination sum:** If candidates are sorted and the current candidate exceeds the remaining target, all subsequent candidates are also too large. Use `break` to exit the loop entirely, not `continue` which keeps checking larger values. Sort first, then `if candidates[i] > remaining: break`.

> [↑ Back to Top](#top)

<a id="6-classic-problems"></a>
# 6. Classic Backtracking Problems

> 📝 **Practice:** [Q9 · subsets](./practice.md#q9) · [Q10 · permutations](./practice.md#q10) · [Q11 · combinations](./practice.md#q11) · [Q12 · combination sum](./practice.md#q12) · [Q14 · palindrome partitioning](./practice.md#q14) · [Q15 · word search](./practice.md#q15)

## Subsets

Include/exclude each element.

Time:
O(2^n)

**Common mistake — not copying before appending:** `result.append(current)` stores a reference. All entries end up as the same mutated list. Fix: `result.append(current[:])`.

**Common mistake — duplicate subsets with repeated input:** When input contains duplicates like `[1, 1, 2]`, the same value at the same recursion level generates identical branches. Fix: sort the input first, then skip with `if i > start and nums[i] == nums[i-1]: continue`. Use `i > start` (not `i > 0`) — using `i > 0` incorrectly skips the first occurrence at deeper recursion levels, causing missed valid results like `[1, 1, 2]`.

## Permutations

Arrange elements.

Time:
O(n!)

Large quickly.

**Common mistake — using `start` index for permutations:** A `start` pointer enforces "pick from remaining tail", which generates combinations, not permutations. For `[1, 2, 3]` this produces only `[1, 2, 3]` instead of all 6 permutations. Fix: use a `used[]` boolean array and iterate `range(0, n)` on every call, skipping `used[i]` elements.

## Visual: Permutation Tree — All Permutations of [1, 2, 3]

At each level we pick which element goes in the current position. We swap it
into place, recurse, then swap back (restore).

```
Level 0: start = [1, 2, 3]

swap(0,0)→[1,2,3]    swap(0,1)→[2,1,3]    swap(0,2)→[3,2,1]
     │                    │                    │
Level 1: fix index 0

   [1, 2, 3]              [2, 1, 3]            [3, 2, 1]
   swap(1,1) swap(1,2)  swap(1,1) swap(1,2)  swap(1,1) swap(1,2)
   [1,2,3]  [1,3,2]    [2,1,3]  [2,3,1]    [3,2,1]  [3,1,2]
     │         │          │         │          │         │
Level 2: fix index 1 (only one element left = base case)

  [1,2,3]  [1,3,2]    [2,1,3]  [2,3,1]    [3,2,1]  [3,1,2]
     ✓        ✓          ✓        ✓          ✓        ✓
```

Six leaves = 3! = 6 permutations. Each path from root to leaf is one permutation.

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

## Combination Sum

Pick numbers that sum to target.

Prune when sum exceeds target.

## N-Queens

Place queens so no attacks.

Use:

- Row tracking
- Column tracking
- Diagonal tracking

Classic backtracking problem.

> 📝 **Practice:** [Q62 · backtracking-n-queens](../dsa_practice_questions_100.md#q62--design--backtracking-n-queens)

## Visual: N-Queens Decision Tree — 4-Queens on a 4x4 Board

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

**Common mistake — O(n) board scan for N-Queens conflict check:** Scanning the board for conflicts each placement is O(n) per call. A queen attacks along its column (`col`), its `\` diagonal (`row - col` = constant), and its `/` diagonal (`row + col` = constant). Maintain three sets — `cols`, `diag1`, `diag2` — for O(1) conflict detection. Always add to all three sets on place and remove from all three on backtrack.

## Sudoku Solver

Fill board.
If invalid → backtrack.

Constraint-heavy.

> [↑ Back to Top](#top)

<a id="7-pruning"></a>
# 7. Pruning (Very Important)

> 📝 **Practice:** [Q8 · pruning basics](./practice.md#q8) · [Q23 · 5 pruning techniques](./practice.md#q23)

Pruning means:

Stop exploring path early.

Example:

If sum > target:
Stop recursion.

This reduces time dramatically.

Pruning makes backtracking efficient.

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

> 📝 **Practice:** [Q63 · backtracking-pruning](../dsa_practice_questions_100.md#q63--interview--backtracking-pruning)

> [↑ Back to Top](#top)

<a id="8-time-complexity"></a>
# 8. Time Complexity

> 📝 **Practice:** [Q7 · time complexity of subsets and permutations](./practice.md#q7) · [Q20 · estimate feasibility](./practice.md#q20)

Backtracking often exponential:

Subsets → O(2^n)
Permutations → O(n!)
N-Queens → Complex but exponential

Worst-case large.

But pruning reduces actual runtime.

> [↑ Back to Top](#top)

<a id="9-backtracking-vs-dfs"></a>
# 9. Backtracking vs DFS

> 📝 **Practice:** [Q6 · backtracking vs brute force](./practice.md#q6) · [Q19 · backtracking vs DP](./practice.md#q19)

Backtracking is DFS with:

- State undoing
- Constraint checking

All backtracking uses DFS.
But not all DFS is backtracking.

> [↑ Back to Top](#top)

<a id="10-backtracking-vs-dp"></a>
# 10. Backtracking vs Dynamic Programming

> 📝 **Practice:** [Q19 · backtracking vs DP decision guide](./practice.md#q19)

Backtracking:
Explores all possibilities.

DP:
Stores intermediate results to avoid recomputation.

If problem has overlapping subproblems,
DP may be better.

> [↑ Back to Top](#top)

<a id="11-real-world-applications"></a>
# 11. Real-World Applications

- Puzzle solving
- Game solving
- Scheduling
- Path finding
- Constraint satisfaction
- Cryptography
- AI search problems

Backtracking used in AI systems.

> [↑ Back to Top](#top)

<a id="12-mental-model"></a>
# 12. Mental Model

Think of backtracking as:

Exploring branches of a tree.

If branch fails:
Cut it.
Go back.

Try next branch.

It is systematic exploration.

> [↑ Back to Top](#top)

<a id="13-final-understanding"></a>
# 13. Final Understanding

Backtracking is:

- Recursive
- Exploratory
- Constraint-driven
- Exponential in worst case
- Optimizable using pruning
- Template-based

Mastering backtracking prepares you for:

- Hard interview problems
- Puzzle-like questions
- Constraint-based challenges
- Competitive programming

Backtracking is disciplined exploration.

> [↑ Back to Top](#top)

# Navigation

Previous:
[19_greedy/interview.md](/02_DSA_Mastery/19_greedy/interview.md)

Next:
[20_backtracking/interview.md](/02_DSA_Mastery/20_backtracking/interview.md)
[21_dynamic_programming/theory.md](/02_DSA_Mastery/21_dynamic_programming/theory.md)

**[🏠 Back to README](../README.md)**

**Prev:** [← Greedy — Interview Q&A](../19_greedy/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md) · [Practice](./practice.md)
