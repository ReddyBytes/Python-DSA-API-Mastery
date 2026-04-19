# 📘 Recursion in Python — Complete Theory (Zero to Advanced)

> This file builds a strong conceptual foundation of recursion,
> from first principles to advanced performance reasoning.
>  
> Focus: call stack behavior, recursion tree analysis, optimization,
> and when recursion is appropriate in real systems.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
base case · recursive case · call stack · recurrence relations · recursion tree

**Should Learn** — Important for real projects, comes up regularly:
memoization as bridge to DP · time complexity analysis · recursion vs iteration

**Good to Know** — Useful in specific situations, not always tested:
tail recursion · space complexity of recursion

**Reference** — Know it exists, look up syntax when needed:
Master Theorem · mutual recursion · trampolining

---

# 1️⃣ What Is Recursion?

Recursion is a technique where a function calls itself to solve a smaller version of the same problem.

Instead of solving a problem directly,
you reduce it into subproblems of the same type.

Core idea:

> A problem can often be defined in terms of itself.

---

# 2️⃣ The Two Mandatory Components of Recursion

Every recursive function must have:

## 1. Base Case

Condition where recursion stops.

Without base case → infinite recursion.

---

## 2. Recursive Case

Function calls itself with smaller input.

Example:

```python
def print_numbers(n):
    if n == 0:       # base case
        return
    print(n)
    print_numbers(n-1)  # recursive call
```

---

# 3️⃣ How Recursion Actually Works (Call Stack)

When a function is called:

- Python creates a stack frame.
- Stores local variables.
- Stores return address.

Example:

```python
def factorial(n):
    if n == 1:
        return 1
    return n * factorial(n-1)
```

Call stack for factorial(4):

```
factorial(4)
factorial(3)
factorial(2)
factorial(1)
```

Now returns happen in reverse order.

Important:

Recursion uses **implicit stack memory**.

---

# 4️⃣ Time Complexity in Recursion

To analyze recursion:

1. Count number of calls.
2. Multiply by work done per call.

---

## Example 1: Linear Recursion

```python
def func(n):
    if n == 0:
        return
    func(n-1)
```

Number of calls → n  
Work per call → O(1)

Total time → O(n)

---

## Example 2: Binary Recursion

```python
def func(n):
    if n <= 1:
        return
    func(n-1)
    func(n-1)
```

Number of calls grows exponentially.

Time → O(2ⁿ)

This is dangerous for large n.

---

# 5️⃣ Recurrence Relation

Recursion often forms recurrence:

Example:

```
T(n) = T(n-1) + O(1)
→ O(n)
```

Divide and conquer example:

```
T(n) = 2T(n/2) + O(n)
→ O(n log n)
```

Used in Merge Sort.

Understanding recurrence is essential for senior-level roles.

---

# 6️⃣ Space Complexity of Recursion

Even if no extra arrays are created,
recursion consumes stack space.

If recursion depth = n:

Space → O(n)

Example:

Factorial:
Depth = n
Space = O(n)

For divide-and-conquer:

Depth = log n
Space = O(log n)

---

# 7️⃣ Tail Recursion

Tail recursion:

Recursive call is last operation.

Example:

```python
def tail_factorial(n, result=1):
    if n == 1:
        return result
    return tail_factorial(n-1, result*n)
```

In some languages, tail recursion is optimized.

In Python:
No tail call optimization.

Stack still grows.

---

# 8️⃣ When Recursion Is Natural

Recursion is ideal for:

- Tree traversal
- Divide-and-conquer
- Backtracking
- DFS in graphs
- Expression evaluation
- Nested structures

When problem has self-similar structure,
recursion is intuitive.

---

# 9️⃣ When NOT to Use Recursion

Avoid recursion when:

- Depth can be very large (risk of stack overflow)
- Iterative solution is simpler
- Performance critical path
- Memory constrained systems

Python default recursion limit ~1000.

You can increase it:

```python
import sys
sys.setrecursionlimit(2000)
```

But not recommended in production blindly.

---

# 🔟 Converting Recursion to Iteration

Recursion can always be converted to:

- Loop
- Explicit stack

Example:

Recursive DFS → iterative DFS using stack.

Understanding conversion shows deeper mastery.

---

# 1️⃣1️⃣ Common Recursion Patterns

## 1. Linear Recursion
One recursive call per function.

## 2. Binary Recursion
Two recursive calls.

## 3. Divide & Conquer
Split into subproblems (merge sort, quick sort).

## 4. Backtracking
Try → explore → undo.

## 5. Tree Recursion
Multiple recursive calls.

---

# 1️⃣2️⃣ Recursion Tree Visualization

Example:

```python
fib(n) = fib(n-1) + fib(n-2)
```

Tree grows like:

```
        fib(4)
       /      \
    fib(3)    fib(2)
    /    \     /   \
```

Time grows exponentially.

This explains why naive Fibonacci is slow.

---

# 1️⃣3️⃣ Memoization (Optimization)

Instead of recomputing:

Store results.

```python
memo = {}

def fib(n):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib(n-1) + fib(n-2)
    return memo[n]
```

Time improves:
From O(2ⁿ) → O(n)

This bridges recursion and dynamic programming.

---

# 1️⃣4️⃣ Recursion vs Iteration

| Feature | Recursion | Iteration |
|----------|------------|------------|
| Code clarity | Often cleaner | Sometimes verbose |
| Memory usage | Uses stack | Usually constant |
| Risk | Stack overflow | Safer |
| Performance | Similar in many cases | Slightly faster |

Choose based on clarity and constraints.

---

# 1️⃣5️⃣ Real-World Usage of Recursion

Recursion is used in:

## 🔹 File System Traversal
Folder inside folder traversal.

## 🔹 Parsing Nested JSON
Recursive structure naturally fits.

## 🔹 Compilers
Expression evaluation trees.

## 🔹 Tree-Based Databases
Hierarchical data.

## 🔹 Backtracking Algorithms
Sudoku, N-Queens.

---

# 1️⃣6️⃣ Common Developer Mistakes

- Missing base case
- Incorrect base condition
- Infinite recursion
- Ignoring stack overflow risk
- Not analyzing exponential growth
- Forgetting space complexity

---

# 1️⃣7️⃣ Performance Estimation

If n = 30:

O(2ⁿ) → 1 billion calls → too slow.

If n = 10⁵:

Linear recursion → stack overflow.

Always analyze:
- Depth
- Branching factor
- Work per call

---

# 1️⃣8️⃣ Advanced Concepts

- Tail recursion elimination (language dependent)
- Memoization
- Tabulation (iterative DP)
- Recursion tree analysis
- Backtracking pruning
- Divide-and-conquer parallelization

Senior interviews expect:
Ability to convert recursion to DP.

---

# 📌 Final Summary

Recursion is:

- A problem-solving technique
- Based on self-similarity
- Implemented using call stack
- Powerful for hierarchical problems

But it:

- Uses extra stack space
- Can become exponential
- Needs careful base condition
- Requires complexity analysis

Master recursion deeply.
It unlocks trees, graphs, backtracking, and dynamic programming.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Strings — Interview Q&A](../03_strings/interview.md) &nbsp;|&nbsp; **Next:** [Visual Explanation →](./visual_explanation.md)

**Related Topics:** [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
