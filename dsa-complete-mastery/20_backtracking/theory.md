# 📘 Backtracking — The Art of Trying, Undoing, and Trying Again

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

> 📝 **Practice:** [Q60 · backtracking-subsets](../dsa_practice_questions_100.md#q60--normal--backtracking-subsets) · [Q61 · backtracking-permutations](../dsa_practice_questions_100.md#q61--thinking--backtracking-permutations)

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
choose-explore-undo pattern · base case for backtracking · pruning

**Should Learn** — Important for real projects, comes up regularly:
subsets · permutations · combination sum · N-Queens · Sudoku solver

**Good to Know** — Useful in specific situations, not always tested:
backtracking vs DFS distinction · time complexity of backtracking

**Reference** — Know it exists, look up syntax when needed:
constraint propagation · intelligent backtracking · CSP heuristics

---

# 🧩 1️⃣ Real Life Story — Maze Explorer

Imagine you are inside a maze.

You choose a path.

If it leads to dead end,
you go back.

Try another path.

That is backtracking.

You don’t destroy maze.
You explore carefully.

---

# 🌳 2️⃣ Decision Tree Visualization

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

---

# 🧠 3️⃣ What Is Backtracking?

Backtracking is:

A recursive algorithm
that builds solution step-by-step
and abandons (backtracks) when constraint fails.

Core idea:

- Choose
- Explore
- Undo

---

# 🔁 4️⃣ The Backtracking Template

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

---

# 🔍 5️⃣ Why Backtracking Is Powerful

It explores all possibilities.

But intelligently:

Stops early if constraint fails.

This is pruning.

Without pruning:
Exponential explosion.

---

# 🧱 6️⃣ Classic Backtracking Problems

---

## 🔹 Subsets

Include/exclude each element.

Time:
O(2^n)

---

## 🔹 Permutations

Arrange elements.

Time:
O(n!)

Large quickly.

---

## 🔹 Combination Sum

Pick numbers that sum to target.

Prune when sum exceeds target.

---

## 🔹 N-Queens

Place queens so no attacks.

Use:

- Row tracking
- Column tracking
- Diagonal tracking

Classic backtracking problem.

> 📝 **Practice:** [Q62 · backtracking-n-queens](../dsa_practice_questions_100.md#q62--design--backtracking-n-queens)

---

## 🔹 Sudoku Solver

Fill board.
If invalid → backtrack.

Constraint-heavy.

---

# ⚡ 7️⃣ Pruning (Very Important)

Pruning means:

Stop exploring path early.

Example:

If sum > target:
Stop recursion.

This reduces time dramatically.

Pruning makes backtracking efficient.

> 📝 **Practice:** [Q63 · backtracking-pruning](../dsa_practice_questions_100.md#q63--interview--backtracking-pruning)

---

# 📏 8️⃣ Time Complexity

Backtracking often exponential:

Subsets → O(2^n)  
Permutations → O(n!)  
N-Queens → Complex but exponential

Worst-case large.

But pruning reduces actual runtime.

---

# 🔄 9️⃣ Backtracking vs DFS

Backtracking is DFS with:

- State undoing
- Constraint checking

All backtracking uses DFS.
But not all DFS is backtracking.

---

# ⚖️ 1️⃣0️⃣ Backtracking vs Dynamic Programming

Backtracking:
Explores all possibilities.

DP:
Stores intermediate results to avoid recomputation.

If problem has overlapping subproblems,
DP may be better.

---

# 🌍 1️⃣1️⃣ Real-World Applications

- Puzzle solving
- Game solving
- Scheduling
- Path finding
- Constraint satisfaction
- Cryptography
- AI search problems

Backtracking used in AI systems.

---

# ⚠️ 1️⃣2️⃣ Common Mistakes

- Forgetting to undo choice
- Not pruning early
- Modifying shared state incorrectly
- Forgetting base case
- Infinite recursion

Backtracking requires careful state control.

---

# 🧠 1️⃣3️⃣ Mental Model

Think of backtracking as:

Exploring branches of a tree.

If branch fails:
Cut it.
Go back.

Try next branch.

It is systematic exploration.

---

# 📌 1️⃣4️⃣ Final Understanding

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

---

# 🔁 Navigation

Previous:  
[19_greedy/interview.md](/dsa-complete-mastery/19_greedy/interview.md)

Next:  
[20_backtracking/interview.md](/dsa-complete-mastery/20_backtracking/interview.md)  
[21_dynamic_programming/theory.md](/dsa-complete-mastery/21_dynamic_programming/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Greedy — Interview Q&A](../19_greedy/interview.md) &nbsp;|&nbsp; **Next:** [Visual Explanation →](./visual_explanation.md)

**Related Topics:** [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
