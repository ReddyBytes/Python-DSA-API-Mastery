<a id="top"></a>

# 📘 Recursion in Python — Complete Theory (Zero to Advanced)

> 📝 **Practice:** [Practice Questions](./practice.md)

> This file builds a strong conceptual foundation of recursion,
> from first principles to advanced performance reasoning.
>  
> Focus: call stack behavior, recursion tree analysis, optimization,
> and when recursion is appropriate in real systems.

## 📖 Table of Contents

1. [What Is Recursion?](#what-is-recursion)
2. [The Two Mandatory Components of Recursion](#the-two-mandatory-components-of-recursion)
3. [How Recursion Actually Works (Call Stack)](#how-recursion-actually-works-call-stack)
4. [Time Complexity in Recursion](#time-complexity-in-recursion)
5. [Recurrence Relation](#recurrence-relation)
6. [Space Complexity of Recursion](#space-complexity-of-recursion)
7. [Tail Recursion](#tail-recursion)
8. [When Recursion Is Natural](#when-recursion-is-natural)
9. [When NOT to Use Recursion](#when-not-to-use-recursion)
10. [Converting Recursion to Iteration](#converting-recursion-to-iteration)
11. [Common Recursion Patterns](#common-recursion-patterns)
12. [Recursion Tree Visualization](#recursion-tree-visualization)
13. [Memoization (Optimization)](#memoization-optimization)
14. [Recursion vs Iteration](#recursion-vs-iteration)
15. [Real-World Usage of Recursion](#real-world-usage-of-recursion)
16. [Performance Estimation](#performance-estimation)
17. [Advanced Concepts](#advanced-concepts)
18. [Final Summary](#final-summary)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
base case · recursive case · call stack · recurrence relations · recursion tree

**Should Learn** — Important for real projects, comes up regularly:
memoization as bridge to DP · time complexity analysis · recursion vs iteration

**Good to Know** — Useful in specific situations, not always tested:
tail recursion · space complexity of recursion

**Reference** — Know it exists, look up syntax when needed:
Master Theorem · mutual recursion · trampolining

<a id="what-is-recursion"></a>
# 1. What Is Recursion?

Recursion is a technique where a function calls itself to solve a smaller version of the same problem.

Instead of solving a problem directly,
you reduce it into subproblems of the same type.

Core idea:

> A problem can often be defined in terms of itself.

Think of nested Russian dolls (Matryoshka). To open the outermost doll you must first open the one inside it, and so on until you reach the smallest doll that has nothing inside — that smallest doll is the base case.

```
PROBLEM SIZE n=5

 ╔═══════════════════════════╗
 ║  solve(5)                 ║
 ║  ╔═══════════════════╗    ║
 ║  ║  solve(4)         ║    ║
 ║  ║  ╔═══════════╗    ║    ║
 ║  ║  ║  solve(3) ║    ║    ║
 ║  ║  ║  ╔═════╗  ║    ║    ║
 ║  ║  ║  ║ s(2)║  ║    ║    ║
 ║  ║  ║  ║ ╔═╗ ║  ║    ║    ║
 ║  ║  ║  ║ ║1║ ║  ║    ║    ║
 ║  ║  ║  ║ ╚═╝ ║  ║    ║    ║
 ║  ║  ║  ╚═════╝  ║    ║    ║
 ║  ║  ╚═══════════╝    ║    ║
 ║  ╚═══════════════════╝    ║
 ╚═══════════════════════════╝

Each shell represents one stack frame.
The innermost shell is the base case.
Results bubble OUT from the center.
```

The key insight: **trust that solve(n-1) already works, and build solve(n) on top of it**.

> [↑ Back to Top](#top)

<a id="the-two-mandatory-components-of-recursion"></a>
# 2. The Two Mandatory Components of Recursion

Every recursive function must have:

## Base Case

Condition where recursion stops.

Without base case → infinite recursion.

> 📝 **Practice:** [Q1 — Identify the Base Case](./practice.md#q1--identify-base-case) · [Q4 — Countdown — Add the Missing Base Case](./practice.md#q4--countdown-base-case)

**Common mistake — missing base case:** The function recurses forever because there is no condition that stops it. Python maintains a call stack; each recursive call adds a frame. Without a base case the stack grows until Python's default limit (~1000 frames) is hit and raises `RecursionError`. Always define at least one base case that returns without recursing.

```python
# WRONG — no base case
def countdown(n):
    print(n)
    countdown(n - 1)   # Runs until Python kills it

# CORRECT
def countdown(n):
    if n <= 0:          # Base case: stop here
        return
    print(n)
    countdown(n - 1)
```

**Common mistake — wrong base case:** The base case exists but returns the wrong value, corrupting every result that builds on it. The base case is the seed value — a wrong seed propagates through all recursive multiplications and zeroes out the answer.

```python
# WRONG — 0! = 1, not 0
def factorial(n):
    if n == 0:
        return 0
    return n * factorial(n - 1)
# factorial(5) → 0 (everything gets multiplied by 0)

# CORRECT
def factorial(n):
    if n == 0:
        return 1    # 0! = 1 by definition
    return n * factorial(n - 1)
# factorial(5) → 120
```

## Recursive Case

Function calls itself with smaller input.

Example:

```python
def print_numbers(n):
    if n == 0:       # base case
        return
    print(n)
    print_numbers(n-1)  # recursive call
```

> 📝 **Practice:** [Q3 — Write Factorial Recursively](./practice.md#q3--write-factorial) · [Q5 — Sum a List Recursively](./practice.md#q5--sum-list-recursively)

**Common mistake — not returning the recursive call:** The recursive call happens but its return value is discarded — the function silently returns `None`. In Python, a function with no `return` statement returns `None`; the arithmetic evaluates to a number but without `return` that number is thrown away.

```python
# WRONG — result computed but never returned
def sum_list(nums, i=0):
    if i == len(nums):
        return 0
    nums[i] + sum_list(nums, i + 1)
# sum_list([1, 2, 3]) → None

# CORRECT
def sum_list(nums, i=0):
    if i == len(nums):
        return 0
    return nums[i] + sum_list(nums, i + 1)
# sum_list([1, 2, 3]) → 6
```

> [↑ Back to Top](#top)

<a id="how-recursion-actually-works-call-stack"></a>
# 3. How Recursion Actually Works (Call Stack)

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

## Visual: Call Stack for factorial(4)

Every function call pushes a **stack frame** onto the call stack. When the function returns, its frame is popped. Recursion means a function pushes multiple frames before any of them pop.

```
PHASE 1: CALLS ARE PUSHED (stack grows downward)

  [factorial(4)]  n=4  ← top of stack (most recent call)
  [factorial(3)]  n=3
  [factorial(2)]  n=2
  [factorial(1)]  n=1  ← base case hit, starts returning


PHASE 2: RETURNS ARE POPPED (stack shrinks upward)

  factorial(1) returns 1
  factorial(2) gets 1, computes 2*1=2, returns 2
  factorial(3) gets 2, computes 3*2=6, returns 6
  factorial(4) gets 6, computes 4*6=24, returns 24
```

Tree view of the same execution:

```
CALL factorial(4)                        ─── returns 24
├── CALL factorial(3)                    ─── returns 6
│   ├── CALL factorial(2)               ─── returns 2
│   │   ├── CALL factorial(1)           ─── returns 1
│   │   │   └── BASE CASE: n==1, return 1
│   │   └── computes 2 * 1 = 2
│   └── computes 3 * 2 = 6
└── computes 4 * 6 = 24
```

Stack frame contents at peak depth:

```
┌─────────────────────┐  ← top (most recent)
│  factorial(1)       │  n=1, waiting to return 1
├─────────────────────┤
│  factorial(2)       │  n=2, waiting for factorial(1)
├─────────────────────┤
│  factorial(3)       │  n=3, waiting for factorial(2)
├─────────────────────┤
│  factorial(4)       │  n=4, waiting for factorial(3)
├─────────────────────┤
│  main()             │  the original caller
└─────────────────────┘  ← bottom (oldest frame)
```

Space complexity = O(n) because n frames live on the stack simultaneously.

Recursion uses **implicit stack memory**.

> 📝 **Practice:** [Q2 — Trace Factorial Call Stack](./practice.md#q2--trace-factorial-stack) · [Q19 — Debug — Missing Return Value](./practice.md#q19--missing-return-bug)

> [↑ Back to Top](#top)

<a id="time-complexity-in-recursion"></a>
# 4. Time Complexity in Recursion

To analyze recursion:

1. Count number of calls.
2. Multiply by work done per call.

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

> 📝 **Practice:** [Q9 — Linear vs Binary Recursion — Classify These Functions](./practice.md#q9--linear-vs-binary-recursion)

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

> 📝 **Practice:** [Q10 — Naive Fibonacci — Why Is It Slow?](./practice.md#q10--naive-fibonacci)

## Visual: Common Recursion Shapes and Their Complexities

### Shape 1 — Linear: T(n) = T(n-1) + O(1)

```
Call 1 ──► Call 2 ──► Call 3 ──► ... ──► Call n ──► BASE

Work per level: O(1)
Number of levels: n
Total: O(n)
```

Examples: factorial, linked-list traversal, reverse a string

### Shape 2 — Linear with O(n) work: T(n) = T(n-1) + O(n)

```
Call 1 ████████████████████  (n work)
  Call 2 ████████████████    (n-1 work)
    Call 3 ██████████████    (n-2 work)
      ...
        Call n █             (1 work)

Total: n + (n-1) + ... + 1 = O(n²)
```

Examples: insertion sort (recursive), bubble sort (recursive)

### Shape 3 — Divide and conquer: T(n) = 2T(n/2) + O(n)

```
Level 0:  [────────── n work ──────────]
Level 1:  [─── n/2 ───][─── n/2 ───]
Level 2:  [n/4][n/4][n/4][n/4]
...
Level log(n): n leaves of O(1)

Work per level: O(n)   (spreads across all calls)
Number of levels: O(log n)
Total: O(n log n)       ← Master Theorem Case 2
```

Examples: merge sort, closest pair of points

### Shape 4 — Exponential: T(n) = 2T(n-1) + O(1)

```
Level 0:        ●              (1 call)
Level 1:      ●   ●            (2 calls)
Level 2:    ● ● ● ●            (4 calls)
Level 3:  ●●●●●●●●             (8 calls)
...
Level n:  2^n leaves

Total calls: 1 + 2 + 4 + ... + 2^n = O(2^n)
```

Examples: naive Fibonacci, brute-force subsets, Tower of Hanoi

### Shape vs complexity — summary table

```
Pattern               Recurrence             Complexity
─────────────────────────────────────────────────────────
Linear work           T(n) = T(n-1) + O(1)   O(n)
Linear + linear work  T(n) = T(n-1) + O(n)   O(n²)
Binary divide         T(n) = 2T(n/2) + O(n)  O(n log n)
Binary divide cheap   T(n) = 2T(n/2) + O(1)  O(n)
Exponential branches  T(n) = 2T(n-1) + O(1)  O(2^n)
```

> [↑ Back to Top](#top)

<a id="recurrence-relation"></a>
# 5. Recurrence Relation

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

## Visual: Master Theorem Quick Reference

```
T(n) = aT(n/b) + f(n)

Let  c = log_b(a)

Case 1:  f(n) = O(n^(c-ε))    → T(n) = Θ(n^c)
Case 2:  f(n) = Θ(n^c)        → T(n) = Θ(n^c · log n)
Case 3:  f(n) = Ω(n^(c+ε))    → T(n) = Θ(f(n))

Merge sort:    a=2, b=2, c=1, f(n)=n  → Case 2 → O(n log n)
Binary search: a=1, b=2, c=0, f(n)=1 → Case 2 → O(log n)
```

> [↑ Back to Top](#top)

<a id="space-complexity-of-recursion"></a>
# 6. Space Complexity of Recursion

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

> [↑ Back to Top](#top)

<a id="tail-recursion"></a>
# 7. Tail Recursion

Tail recursion:

Recursive call is last operation.

A function is **tail-recursive** when the recursive call is the very last operation — there is no pending computation after it returns.

## Visual: Tail vs Non-Tail Stack Behaviour

### Non-tail-recursive factorial

```python
def factorial(n):
    if n == 1: return 1
    return n * factorial(n-1)   # ← multiplication PENDING after call returns
                                 #   must keep frame on stack
```

### Tail-recursive factorial (accumulator pattern)

```python
def tail_factorial(n, result=1):
    if n == 1:
        return result
    return tail_factorial(n-1, result*n)   # ← nothing pending, frame can be reused
```

### Stack behaviour side-by-side

```
NON-TAIL                         TAIL (with TCO)

[fact(4)]  n=4, pending *4       [fact(4, acc=1)]   → reuse frame
[fact(3)]  n=3, pending *3       [fact(3, acc=4)]   → reuse frame
[fact(2)]  n=2, pending *2       [fact(2, acc=12)]  → reuse frame
[fact(1)]  n=1, returns 1        [fact(1, acc=24)]  → returns 24

Stack depth: O(n)                Stack depth: O(1)  (constant!)
```

### Equivalent iterative loop (what the compiler emits with TCO)

```python
def factorial_iter(n):
    acc = 1
    while n > 1:
        acc *= n
        n  -= 1
    return acc
```

In some languages, tail recursion is optimized (TCO).

In Python: no tail call optimization. Stack still grows.

**Common mistake — expecting Python to do TCO:** CPython does NOT perform tail-call optimization. Even a perfectly tail-recursive function still allocates a new frame per call. Use explicit iteration in Python for large n.

> 📝 **Practice:** [Q18 — Rewrite Factorial as Tail-Recursive](./practice.md#q18--tail-recursion-rewrite)

> [↑ Back to Top](#top)

<a id="when-recursion-is-natural"></a>
# 8. When Recursion Is Natural

Recursion is ideal for:

- Tree traversal
- Divide-and-conquer
- Backtracking
- DFS in graphs
- Expression evaluation
- Nested structures

When problem has self-similar structure,
recursion is intuitive.

> [↑ Back to Top](#top)

<a id="when-not-to-use-recursion"></a>
# 9. When NOT to Use Recursion

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

**Common mistake — forgetting Python's recursion limit:** Python's default recursion limit is ~1000. Deep inputs crash with `RecursionError` even when the logic is correct. Python does not perform tail-call optimization — every recursive call allocates a stack frame. For interview problems, mention this trade-off even if you write the recursive version first.

```python
# WRONG — crashes on deep input
def sum_range(n):
    if n == 0:
        return 0
    return n + sum_range(n - 1)
# sum_range(10000) → RecursionError

# PREFERRED — convert to iterative for production
def sum_range(n):
    total = 0
    while n > 0:
        total += n
        n -= 1
    return total
```

> [↑ Back to Top](#top)

<a id="converting-recursion-to-iteration"></a>
# 10. Converting Recursion to Iteration

Recursion can always be converted to:

- Loop
- Explicit stack

Example:

Recursive DFS → iterative DFS using stack.

Understanding conversion shows deeper mastery.

> [↑ Back to Top](#top)

<a id="common-recursion-patterns"></a>
# 11. Common Recursion Patterns

## 1. Linear Recursion
One recursive call per function.

## 2. Binary Recursion
Two recursive calls.

## 3. Divide & Conquer
Split into subproblems (merge sort, quick sort).

> 📝 **Practice:** [Q21 — Divide and Conquer — Merge Sort](./practice.md#q21--divide-and-conquer-merge-sort)

## Visual: Merge Sort Divide and Conquer

```
SPLIT PHASE (top-down)

[5, 3, 8, 1, 9, 2, 7, 4]
         /          \
  [5, 3, 8, 1]   [9, 2, 7, 4]
    /      \        /      \
 [5, 3]  [8, 1]  [9, 2]  [7, 4]
  / \     / \     / \     / \
 [5][3]  [8][1]  [9][2]  [7][4]
          ↑ base cases (size 1)

MERGE PHASE (bottom-up)

 [5][3]  [8][1]  [9][2]  [7][4]
   ↓       ↓       ↓       ↓
 [3,5]  [1,8]  [2,9]  [4,7]
     \   /         \   /
  [1,3,5,8]     [2,4,7,9]
         \         /
     [1,2,3,4,5,7,8,9]
```

Each merge step does O(n) work across all calls at that level, and there are O(log n) levels, giving T(n) = O(n log n).

## 4. Backtracking
Try → explore → undo.

> 📝 **Practice:** [Q22 — Backtracking — Generate All Subsets](./practice.md#q22--backtracking-subsets) · [Q23 — Backtracking — Generate All Permutations](./practice.md#q23--backtracking-permutations)

**Common mistake — mutable default argument in backtracking:** Using a mutable object (list, dict) as a default parameter causes it to persist and accumulate across calls. Python evaluates default argument values once at function definition time — the same list object is reused across all calls, so mutations made in one call are visible in every subsequent call.

```python
# WRONG — mutable defaults
def collect_paths(node, path=[], result=[]):
    if node is None:
        return
    path.append(node.val)
    if not node.left and not node.right:
        result.append(list(path))
    collect_paths(node.left, path, result)
    collect_paths(node.right, path, result)
    path.pop()
    return result
# First call: correct. Second call: result already contains paths from first call!

# CORRECT
def collect_paths(node, path=None, result=None):
    if path is None:
        path = []
    if result is None:
        result = []
    if node is None:
        return result
    path.append(node.val)
    if not node.left and not node.right:
        result.append(list(path))
    collect_paths(node.left, path, result)
    collect_paths(node.right, path, result)
    path.pop()
    return result
```

## 5. Tree Recursion
Multiple recursive calls.

> 📝 **Practice:** [Q14 — Binary Tree Inorder Traversal](./practice.md#q14--tree-traversal) · [Q15 — Height of a Binary Tree](./practice.md#q15--tree-height) · [Q24 — Count Root-to-Leaf Paths with Target Sum](./practice.md#q24--tree-recursion-count-paths)

**Common mistake — off-by-one in tree height:** Inconsistent definition of "height" — does a leaf have height 0 or 1? Mixing both conventions in the same function corrupts the result. The two conventions are each internally consistent, but mixing them creates an incorrect +1 somewhere. Pick one convention and use it everywhere.

```python
# CORRECT — height = number of edges, leaf = 0
def height(node):
    if node is None:
        return -1   # Sentinel: None contributes -1 so leaf gets 0
    return 1 + max(height(node.left), height(node.right))

# CORRECT — height = number of nodes, leaf = 1
def height(node):
    if node is None:
        return 0
    return 1 + max(height(node.left), height(node.right))
```

> [↑ Back to Top](#top)

<a id="recursion-tree-visualization"></a>
# 12. Recursion Tree Visualization

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

## Visual: fib(5) Full Recursion Tree — Seeing Duplicate Work

```python
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)
```

```
                        fib(5)
                       /      \
                  fib(4)        fib(3)*
                 /      \       /     \
            fib(3)*    fib(2)^ fib(2)^ fib(1)
            /    \     /   \
        fib(2)^ fib(1) fib(1) fib(0)
        /    \
    fib(1)  fib(0)

  * = called TWICE (duplicate subtree)
  ^ = called THREE times total
```

Counting the calls:

```
fib(5)  called: 1
fib(4)  called: 1
fib(3)  called: 2   ← duplicate!
fib(2)  called: 3   ← triplicate!
fib(1)  called: 5
fib(0)  called: 3
─────────────────
Total:  15 calls to compute fib(5)

Without memoization: T(n) = T(n-1) + T(n-2) + O(1)  ≈  O(2^n)
With memoization:    T(n) = O(n)    (each subproblem solved once)
```

## Visual: Linear vs Tree Recursion Shape Comparison

### Linear recursion (e.g., factorial)

```
factorial(5)
    │
factorial(4)
    │
factorial(3)
    │
factorial(2)
    │
factorial(1)   ← base case

Shape: a straight line
Depth: O(n)
Calls: O(n)
```

### Binary tree recursion (e.g., Fibonacci)

```
              fib(5)
            /        \
        fib(4)        fib(3)
        /    \        /    \
    fib(3)  fib(2) fib(2) fib(1)
    / \      / \    / \
  ...  ... ...  ... ...

Shape: a binary tree
Depth:  O(n)
Calls:  O(2^n)   ← exponential blowup
```

### Divide-and-conquer (e.g., merge sort)

```
          mergeSort([8 elements])
          /                     \
 mergeSort([4])         mergeSort([4])
   /        \             /        \
ms([2])  ms([2])      ms([2])   ms([2])
  / \      / \          / \       / \
ms  ms   ms  ms       ms  ms    ms  ms

Shape: a balanced binary tree
Depth: O(log n)
Calls: O(n)      ← efficient!
```

> [↑ Back to Top](#top)

<a id="memoization-optimization"></a>
# 13. Memoization (Optimization)

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

## Visual: With Memo vs Without Memo

```
WITHOUT MEMO          WITH MEMO
O(2^n) calls          O(n) calls

fib(5)                fib(5)
├── fib(4)            ├── fib(4)
│   ├── fib(3)        │   ├── fib(3)
│   │   ├── fib(2)    │   │   ├── fib(2)
│   │   │   ├─ fib(1) │   │   │   ├─ fib(1) → 1
│   │   │   └─ fib(0) │   │   │   └─ fib(0) → 0
│   │   └── fib(1)    │   │   └─ fib(1) → 1 (cached)
│   └── fib(3)        │   └─ fib(3) → 2 (cached)
│       ├── fib(2)    └── fib(3) → 2 (cached)
│       │   ├─ fib(1)
│       │   └─ fib(0)
│       └── fib(1)
└── fib(3)  (again!)
    └── ... (entire subtree repeated)
```

**Common mistake — redundant recomputation (no memoization):** The same subproblem is solved exponentially many times because results are never cached. Without caching, `fib(n)` recomputes `fib(n-2)` once directly and again as part of computing `fib(n-1)`. This doubles work at every level, yielding O(2^n) time. With caching, each unique argument is computed exactly once: O(n) time.

```python
# WRONG — exponential time
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
# fib(50) takes minutes

# CORRECT — linear time with lru_cache
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
# fib(50) = 12586269025, instant
```

> 📝 **Practice:** [Q11 — Memoized Fibonacci](./practice.md#q11--memoized-fibonacci) · [Q25 — Memoization vs Tabulation](./practice.md#q25--memoization-vs-tabulation)

> [↑ Back to Top](#top)

<a id="recursion-vs-iteration"></a>
# 14. Recursion vs Iteration

| Feature | Recursion | Iteration |
|----------|------------|------------|
| Code clarity | Often cleaner | Sometimes verbose |
| Memory usage | Uses stack | Usually constant |
| Risk | Stack overflow | Safer |
| Performance | Similar in many cases | Slightly faster |

Choose based on clarity and constraints.

> 📝 **Practice:** [Q8 — Recursion vs Iteration — Pick the Right Tool](./practice.md#q8--recursion-vs-iteration-tradeoff)

**Common mistake — modifying shared state across recursive calls:** A global or outer-scope variable is mutated during recursion, causing results to be wrong on repeated calls or during backtracking. Recursion inherently calls itself multiple times — any side effect (mutating a global, appending to an outer list) accumulates across all those calls. Prefer returning values rather than mutating shared state.

```python
# WRONG — global state accumulates across calls
count = 0
def count_nodes(node):
    global count
    if node is None:
        return
    count += 1
    count_nodes(node.left)
    count_nodes(node.right)
# First call: count = 7. Second call: count = 14 — accumulated, not reset.

# CORRECT — pure return value
def count_nodes(node):
    if node is None:
        return 0
    return 1 + count_nodes(node.left) + count_nodes(node.right)
```

> [↑ Back to Top](#top)

<a id="real-world-usage-of-recursion"></a>
# 15. Real-World Usage of Recursion

Recursion is used in:

## File System Traversal
Folder inside folder traversal.

## Parsing Nested JSON
Recursive structure naturally fits.

## Compilers
Expression evaluation trees.

## Tree-Based Databases
Hierarchical data.

## Backtracking Algorithms
Sudoku, N-Queens.

> [↑ Back to Top](#top)

<a id="performance-estimation"></a>
# 16. Performance Estimation

If n = 30:

O(2ⁿ) → 1 billion calls → too slow.

If n = 10⁵:

Linear recursion → stack overflow.

Always analyze:
- Depth
- Branching factor
- Work per call

## Pre-Submission Checklist

Before submitting any recursive solution, answer these 5 questions:

- [ ] **1. Is there a base case for every terminal condition?**
  Check: empty input, `n=0`, `None` node, empty string, index out of bounds.

- [ ] **2. Does every code path return a value?**
  Trace the call manually. Confirm that the result of the recursive call is `return`ed, not just called.

- [ ] **3. Does the recursive call make progress toward the base case?**
  Each call must reduce `n`, advance an index, or move to a child node. If not, you have infinite recursion.

- [ ] **4. Could the input depth exceed ~1000?**
  If yes: either use `sys.setrecursionlimit`, convert to iterative, or mention this trade-off explicitly.

- [ ] **5. Are there repeated subproblems?**
  If the same arguments could appear more than once (e.g., Fibonacci, grid paths), add memoization. Otherwise you may have O(2^n) time.

**Bonus — mutable state check:**
  If you pass a list or dict as a parameter, confirm you are not using it as a default argument value. Use `None` as the default and initialize inside the function.

> [↑ Back to Top](#top)

<a id="advanced-concepts"></a>
# 17. Advanced Concepts

- Tail recursion elimination (language dependent)
- Memoization
- Tabulation (iterative DP)
- Recursion tree analysis
- Backtracking pruning
- Divide-and-conquer parallelization

Senior interviews expect:
Ability to convert recursion to DP.

> [↑ Back to Top](#top)

<a id="final-summary"></a>
# 18. Final Summary

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

The diagram to keep in mind:

```
             PROBLEM(n)
            /           \
   PROBLEM(n/2 or n-1)  ...
        |
   smaller and smaller
        |
    BASE CASE
        ↓
   answers bubble back up
```

Recursion is nothing more than **trusting your past self**: assume the smaller problem is already solved, write the one step that connects size n to size n-1, and define what "done" looks like. The call stack handles the rest.

> [↑ Back to Top](#top)

**[🏠 Back to README](../README.md)**

**Prev:** [← Strings — Interview Q&A](../03_strings/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md) · [Practice](./practice.md)
