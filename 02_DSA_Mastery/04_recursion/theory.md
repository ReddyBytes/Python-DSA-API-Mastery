<a id="top"></a>
# 📘 04 – Recursion in Python

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. What Is Recursion?](#1-what-is-recursion)
- [2. Base Case and Recursive Case](#2-base-case-and-recursive-case)
  - [Base Case](#base-case)
  - [Recursive Case](#recursive-case)
- [3. The Call Stack](#3-the-call-stack)
  - [Visual: Call Stack for factorial(4)](#visual-call-stack)
- [4. Time Complexity and Recurrence](#4-time-complexity)
  - [Linear Recursion](#linear-recursion)
  - [Binary Recursion](#binary-recursion)
  - [Recursion Shapes and Their Complexities](#recursion-shapes)
  - [Recurrence Relations and Master Theorem](#recurrence-relations)
- [5. Space Complexity and Tail Recursion](#5-space-complexity)
  - [Tail vs Non-Tail Stack Behaviour](#tail-vs-non-tail)
- [6. When to Use and Avoid Recursion](#6-when-to-use)
  - [When Recursion Is Natural](#when-natural)
  - [When NOT to Use Recursion](#when-not-to-use)
  - [Converting to Iteration](#converting-to-iteration)
- [7. Common Recursion Patterns](#7-common-patterns)
  - [Linear Recursion](#pattern-linear)
  - [Binary Recursion](#pattern-binary)
  - [Divide and Conquer](#pattern-divide-conquer)
  - [Backtracking](#pattern-backtracking)
  - [Tree Recursion](#pattern-tree)
- [8. Recursion Tree and Memoization](#8-recursion-tree)
  - [Visual: fib(5) Full Tree](#visual-fib-tree)
  - [Shape Comparison](#shape-comparison)
  - [Memoization](#memoization)
- [9. Recursion vs Iteration](#9-recursion-vs-iteration)
- [10. Real-World Impact](#10-real-world-impact)
- [🔥 Summary](#summary)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
base case · recursive case · call stack · recurrence relations · recursion tree

**Should Learn** — Important for real projects, comes up regularly:
memoization as bridge to DP · time complexity analysis · recursion vs iteration

**Good to Know** — Useful in specific situations, not always tested:
tail recursion · space complexity of recursion

**Reference** — Know it exists, look up syntax when needed:
Master Theorem · mutual recursion · trampolining

Nadia is a puzzle solver. She works at a puzzle factory where every large puzzle is made of smaller copies of itself — open the big box and inside is the same puzzle, just smaller. She keeps opening smaller and smaller boxes until she reaches one so tiny she can solve it by hand. That smallest box is the **base case**. Then she works her way back up, assembling each solution into the next larger one. That process — breaking a problem into smaller identical versions of itself — is **recursion**.

<a id="1-what-is-recursion"></a>
# 1. What Is Recursion?

Nadia receives a puzzle labeled "solve(5)." Inside, she finds a note: "To solve this, first solve(4), then combine." She opens solve(4) and finds the same note pointing to solve(3). She keeps going until she reaches solve(1), which she can answer directly. Then she works backwards, assembling each answer.

Recursion is a technique where a function calls itself to solve a smaller version of the same problem.

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

<a id="2-base-case-and-recursive-case"></a>
# 2. Base Case and Recursive Case

Every puzzle Nadia opens must eventually reach a smallest box she can solve by hand. If there is no smallest box, she opens boxes forever and never finishes. Every recursive function needs exactly two things.

<a id="base-case"></a>
## Base Case

The condition where recursion stops. Without it — infinite recursion.

> 📝 **Practice:** [Q1 — Identify the Base Case](./practice.md#q1--identify-base-case) · [Q4 — Countdown — Add the Missing Base Case](./practice.md#q4--countdown-base-case)

**Common mistake — missing base case:** The function recurses forever because there is no stopping condition. Python's call stack grows until the default limit (~1000 frames) is hit, raising `RecursionError`.

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

**Common mistake — wrong base case:** The base case exists but returns the wrong value, corrupting every result that builds on it. A wrong seed propagates through all recursive multiplications.

```python
# WRONG — 0! = 1, not 0
def factorial(n):
    if n == 0:
        return 0        # everything gets multiplied by 0!
    return n * factorial(n - 1)
# factorial(5) → 0

# CORRECT
def factorial(n):
    if n == 0:
        return 1        # 0! = 1 by definition
    return n * factorial(n - 1)
# factorial(5) → 120
```

<a id="recursive-case"></a>
## Recursive Case

Nadia opens the current box and finds a smaller version. The function calls itself with smaller input.

```python
def print_numbers(n):
    if n == 0:       # base case
        return
    print(n)
    print_numbers(n-1)  # recursive call — smaller input
```

> 📝 **Practice:** [Q3 — Write Factorial Recursively](./practice.md#q3--write-factorial) · [Q5 — Sum a List Recursively](./practice.md#q5--sum-list-recursively)

**Common mistake — not returning the recursive call:** The recursive call happens but its return value is discarded — the function silently returns `None`.

```python
# WRONG — result computed but never returned
def sum_list(nums, i=0):
    if i == len(nums):
        return 0
    nums[i] + sum_list(nums, i + 1)   # missing return!
# sum_list([1, 2, 3]) → None

# CORRECT
def sum_list(nums, i=0):
    if i == len(nums):
        return 0
    return nums[i] + sum_list(nums, i + 1)
# sum_list([1, 2, 3]) → 6
```

> [↑ Back to Top](#top)

<a id="3-the-call-stack"></a>
# 3. The Call Stack

When Nadia opens box 5, she sets it aside and opens box 4. She sets 4 aside and opens 3. By the time she reaches box 1, she has a stack of open boxes beside her — that is the call stack. Each box is a **stack frame** holding the local variables and the place to return to.

When a function is called, Python:
- Creates a stack frame
- Stores local variables
- Stores return address

<a id="visual-call-stack"></a>
## Visual: Call Stack for factorial(4)

```python
def factorial(n):
    if n == 1:
        return 1
    return n * factorial(n-1)
```

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

Space complexity = O(n) because n frames live on the stack simultaneously. Recursion uses **implicit stack memory**.

> 📝 **Practice:** [Q2 — Trace Factorial Call Stack](./practice.md#q2--trace-factorial-stack) · [Q19 — Debug — Missing Return Value](./practice.md#q19--missing-return-bug)

> [↑ Back to Top](#top)

<a id="4-time-complexity"></a>
# 4. Time Complexity and Recurrence

Nadia wants to know: "If I have a puzzle of size n, how many total boxes will I open?" The answer depends on the shape of the puzzle — does each box contain one smaller box (linear), two smaller boxes (binary), or does it split in half (divide and conquer)?

To analyze recursion:
1. Count number of calls
2. Multiply by work done per call

<a id="linear-recursion"></a>
## Linear Recursion

```python
def func(n):
    if n == 0:
        return
    func(n-1)
```

Number of calls → n. Work per call → O(1). Total → O(n).

> 📝 **Practice:** [Q9 — Linear vs Binary Recursion — Classify These Functions](./practice.md#q9--linear-vs-binary-recursion)

<a id="binary-recursion"></a>
## Binary Recursion

```python
def func(n):
    if n <= 1:
        return
    func(n-1)
    func(n-1)
```

Number of calls grows exponentially. Time → O(2ⁿ). Dangerous for large n.

> 📝 **Practice:** [Q10 — Naive Fibonacci — Why Is It Slow?](./practice.md#q10--naive-fibonacci)

<a id="recursion-shapes"></a>
## Recursion Shapes and Their Complexities

## Shape 1 — Linear: T(n) = T(n-1) + O(1)

```
Call 1 ──► Call 2 ──► Call 3 ──► ... ──► Call n ──► BASE

Work per level: O(1)
Number of levels: n
Total: O(n)
```

Examples: factorial, linked-list traversal, reverse a string

## Shape 2 — Linear with O(n) work: T(n) = T(n-1) + O(n)

```
Call 1 ████████████████████  (n work)
  Call 2 ████████████████    (n-1 work)
    Call 3 ██████████████    (n-2 work)
      ...
        Call n █             (1 work)

Total: n + (n-1) + ... + 1 = O(n²)
```

Examples: insertion sort (recursive), bubble sort (recursive)

## Shape 3 — Divide and conquer: T(n) = 2T(n/2) + O(n)

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

## Shape 4 — Exponential: T(n) = 2T(n-1) + O(1)

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

## Summary Table

```
Pattern               Recurrence             Complexity
─────────────────────────────────────────────────────────
Linear work           T(n) = T(n-1) + O(1)   O(n)
Linear + linear work  T(n) = T(n-1) + O(n)   O(n²)
Binary divide         T(n) = 2T(n/2) + O(n)  O(n log n)
Binary divide cheap   T(n) = 2T(n/2) + O(1)  O(n)
Exponential branches  T(n) = 2T(n-1) + O(1)  O(2^n)
```

<a id="recurrence-relations"></a>
## Recurrence Relations and Master Theorem

Nadia discovers a formula that predicts the total work for any divide-and-conquer puzzle without tracing every box.

```
T(n) = aT(n/b) + f(n)

Let  c = log_b(a)

Case 1:  f(n) = O(n^(c-ε))    → T(n) = Θ(n^c)
Case 2:  f(n) = Θ(n^c)        → T(n) = Θ(n^c · log n)
Case 3:  f(n) = Ω(n^(c+ε))    → T(n) = Θ(f(n))

Merge sort:    a=2, b=2, c=1, f(n)=n  → Case 2 → O(n log n)
Binary search: a=1, b=2, c=0, f(n)=1 → Case 2 → O(log n)
```

Understanding recurrence is essential for senior-level roles.

> [↑ Back to Top](#top)

<a id="5-space-complexity"></a>
# 5. Space Complexity and Tail Recursion

Nadia notices that every open box stays on her desk until the smallest one is solved. If the puzzle has 1000 layers, she has 1000 open boxes piled up. That pile is the stack — and it takes space even if Nadia uses no extra tools.

Even if no extra arrays are created, recursion consumes stack space.

If recursion depth = n → Space = O(n)
If divide-and-conquer depth = log n → Space = O(log n)

<a id="tail-vs-non-tail"></a>
## Tail vs Non-Tail Stack Behaviour

Nadia discovers a trick: if she can compute the answer BEFORE opening the next box (passing the accumulated result forward), she does not need to keep the current box open. She can throw it away immediately. That is **tail recursion**.

A function is **tail-recursive** when the recursive call is the very last operation — there is no pending computation after it returns.

## Non-Tail-Recursive Factorial

```python
def factorial(n):
    if n == 1: return 1
    return n * factorial(n-1)   # ← multiplication PENDING after call returns
                                 #   must keep frame on stack
```

## Tail-Recursive Factorial (Accumulator Pattern)

```python
def tail_factorial(n, result=1):
    if n == 1:
        return result
    return tail_factorial(n-1, result*n)   # ← nothing pending, frame can be reused
```

## Stack Behaviour Side-by-Side

```
NON-TAIL                         TAIL (with TCO)

[fact(4)]  n=4, pending *4       [fact(4, acc=1)]   → reuse frame
[fact(3)]  n=3, pending *3       [fact(3, acc=4)]   → reuse frame
[fact(2)]  n=2, pending *2       [fact(2, acc=12)]  → reuse frame
[fact(1)]  n=1, returns 1        [fact(1, acc=24)]  → returns 24

Stack depth: O(n)                Stack depth: O(1)  (constant!)
```

Equivalent iterative loop (what the compiler emits with TCO):

```python
def factorial_iter(n):
    acc = 1
    while n > 1:
        acc *= n
        n  -= 1
    return acc
```

**Common mistake — expecting Python to do TCO:** CPython does NOT perform tail-call optimization. Even a perfectly tail-recursive function still allocates a new frame per call. Use explicit iteration in Python for large n.

> 📝 **Practice:** [Q18 — Rewrite Factorial as Tail-Recursive](./practice.md#q18--tail-recursion-rewrite)

> [↑ Back to Top](#top)

<a id="6-when-to-use"></a>
# 6. When to Use and Avoid Recursion

Nadia has learned that recursion is powerful — but it is not always the right tool. Some puzzles have a natural nested structure that begs for recursion. Others are better solved with a simple loop.

<a id="when-natural"></a>
## When Recursion Is Natural

Recursion is ideal for problems with **self-similar structure**:

- Tree traversal (each subtree is a smaller tree)
- Divide-and-conquer (merge sort, quick sort)
- Backtracking (try → explore → undo)
- DFS in graphs
- Expression evaluation (nested expressions)
- Nested structures (JSON, XML, file systems)

<a id="when-not-to-use"></a>
## When NOT to Use Recursion

Avoid recursion when:
- Depth can be very large (risk of stack overflow)
- Iterative solution is simpler and clearer
- Performance-critical path (function call overhead)
- Memory-constrained systems

Python default recursion limit is ~1000. You can increase it:

```python
import sys
sys.setrecursionlimit(2000)
```

But not recommended in production blindly.

**Common mistake — forgetting Python's recursion limit:** Deep inputs crash with `RecursionError` even when the logic is correct. Python does not perform tail-call optimization — every recursive call allocates a stack frame.

```python
# WRONG — crashes on deep input
def sum_range(n):
    if n == 0: return 0
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

<a id="converting-to-iteration"></a>
## Converting to Iteration

Recursion can always be converted to:
- A loop (for linear recursion)
- An explicit stack (for tree/graph recursion)

Example: Recursive DFS → iterative DFS using a stack. Understanding this conversion shows deeper mastery.

> [↑ Back to Top](#top)

<a id="7-common-patterns"></a>
# 7. Common Recursion Patterns

Nadia categorizes every puzzle she has solved into five shapes. Once she recognizes the shape, she knows the complexity before she even starts solving.

<a id="pattern-linear"></a>
## Linear Recursion

One recursive call per function. Examples: factorial, linked-list traversal.

<a id="pattern-binary"></a>
## Binary Recursion

Two recursive calls. Examples: Fibonacci, binary tree traversals.

<a id="pattern-divide-conquer"></a>
## Divide and Conquer

Split into subproblems, solve each, combine results. Examples: merge sort, quick sort.

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

<a id="pattern-backtracking"></a>
## Backtracking

Try → explore → undo. Nadia tries placing a puzzle piece, explores all possibilities from there, and if none work, she removes the piece and tries another.

> 📝 **Practice:** [Q22 — Backtracking — Generate All Subsets](./practice.md#q22--backtracking-subsets) · [Q23 — Backtracking — Generate All Permutations](./practice.md#q23--backtracking-permutations)

**Common mistake — mutable default argument in backtracking:** Using a mutable object (list, dict) as a default parameter causes it to persist and accumulate across calls. Python evaluates default argument values once at function definition time.

```python
# WRONG — mutable defaults accumulate
def collect_paths(node, path=[], result=[]):
    if node is None: return
    path.append(node.val)
    if not node.left and not node.right:
        result.append(list(path))
    collect_paths(node.left, path, result)
    collect_paths(node.right, path, result)
    path.pop()
    return result

# CORRECT — initialize inside the function
def collect_paths(node, path=None, result=None):
    if path is None: path = []
    if result is None: result = []
    if node is None: return result
    path.append(node.val)
    if not node.left and not node.right:
        result.append(list(path))
    collect_paths(node.left, path, result)
    collect_paths(node.right, path, result)
    path.pop()
    return result
```

<a id="pattern-tree"></a>
## Tree Recursion

Multiple recursive calls — each node spawns calls to its children.

> 📝 **Practice:** [Q14 — Binary Tree Inorder Traversal](./practice.md#q14--tree-traversal) · [Q15 — Height of a Binary Tree](./practice.md#q15--tree-height) · [Q24 — Count Root-to-Leaf Paths with Target Sum](./practice.md#q24--tree-recursion-count-paths)

**Common mistake — off-by-one in tree height:** Inconsistent definition of "height" — does a leaf have height 0 or 1? Pick one convention and use it everywhere.

```python
# Convention A — height = number of edges, leaf = 0
def height(node):
    if node is None: return -1
    return 1 + max(height(node.left), height(node.right))

# Convention B — height = number of nodes, leaf = 1
def height(node):
    if node is None: return 0
    return 1 + max(height(node.left), height(node.right))
```

> [↑ Back to Top](#top)

<a id="8-recursion-tree"></a>
# 8. Recursion Tree and Memoization

Nadia draws out the full tree of boxes she opens for a Fibonacci puzzle. She notices something alarming — she is opening the exact same boxes over and over. The solution: keep a notebook. Once she solves a box, she writes down the answer. If the same box appears again, she looks it up instead of solving it again.

<a id="visual-fib-tree"></a>
## Visual: fib(5) Full Recursion Tree

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

<a id="shape-comparison"></a>
## Shape Comparison

```
Linear recursion (factorial)     Binary tree recursion (fib)

factorial(5)                               fib(5)
    │                                    /        \
factorial(4)                         fib(4)        fib(3)
    │                                /    \        /    \
factorial(3)                     fib(3)  fib(2) fib(2) fib(1)
    │                            / \      / \    / \
factorial(2)                   ...  ... ...  ... ...
    │
factorial(1)  ← base case

Shape: a straight line             Shape: a binary tree
Depth: O(n)                        Depth:  O(n)
Calls: O(n)                        Calls:  O(2^n) ← exponential blowup
```

```
Divide-and-conquer (merge sort)

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

<a id="memoization"></a>
## Memoization

Nadia's notebook — store results so each subproblem is solved only once.

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

Time improves: From O(2ⁿ) → O(n). This bridges recursion and dynamic programming.

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

**Common mistake — redundant recomputation:** Without caching, `fib(n)` recomputes `fib(n-2)` once directly and again as part of computing `fib(n-1)`. This doubles work at every level, yielding O(2^n).

```python
# WRONG — exponential time
def fib(n):
    if n <= 1: return n
    return fib(n - 1) + fib(n - 2)
# fib(50) takes minutes

# CORRECT — linear time with lru_cache
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n <= 1: return n
    return fib(n - 1) + fib(n - 2)
# fib(50) = 12586269025, instant
```

> 📝 **Practice:** [Q11 — Memoized Fibonacci](./practice.md#q11--memoized-fibonacci) · [Q25 — Memoization vs Tabulation](./practice.md#q25--memoization-vs-tabulation)

> [↑ Back to Top](#top)

<a id="9-recursion-vs-iteration"></a>
# 9. Recursion vs Iteration

Nadia can solve every puzzle two ways: opening nested boxes (recursion) or lining them up and processing one at a time (iteration). Each approach has trade-offs — clarity vs safety, elegance vs memory.

| Feature | Recursion | Iteration |
|----------|------------|------------|
| Code clarity | Often cleaner for nested structures | Sometimes verbose |
| Memory usage | Uses stack — O(n) or O(log n) | Usually O(1) |
| Risk | Stack overflow on deep input | Safer |
| Performance | Function call overhead | Slightly faster |

Choose based on clarity and constraints. For interviews, write recursive first (cleaner to explain), then mention you could convert to iterative if depth is a concern.

> 📝 **Practice:** [Q8 — Recursion vs Iteration — Pick the Right Tool](./practice.md#q8--recursion-vs-iteration-tradeoff)

**Common mistake — modifying shared state across recursive calls:** A global or outer-scope variable is mutated during recursion, causing results to accumulate across calls. Prefer returning values rather than mutating shared state.

```python
# WRONG — global state accumulates across calls
count = 0
def count_nodes(node):
    global count
    if node is None: return
    count += 1
    count_nodes(node.left)
    count_nodes(node.right)
# First call: count = 7. Second call: count = 14 — accumulated!

# CORRECT — pure return value
def count_nodes(node):
    if node is None: return 0
    return 1 + count_nodes(node.left) + count_nodes(node.right)
```

> [↑ Back to Top](#top)

<a id="10-real-world-impact"></a>
# 10. Real-World Impact

Nadia finishes the puzzle factory and joins a software team. She discovers recursion everywhere in production code — not as an academic exercise, but as the natural solution to inherently nested problems.

## File System Traversal

Folders inside folders — a directory tree is naturally recursive. `os.walk()` and `pathlib.rglob()` use recursion internally.

## Parsing Nested JSON

JSON objects contain nested objects and arrays. A recursive parser naturally mirrors the structure: parse an object, and for each value, recursively parse its contents.

## Compilers

Expression evaluation trees. `2 + 3 * (4 - 1)` parses into a tree where each node recursively evaluates its children.

## Tree-Based Databases

Hierarchical data — file systems (inodes), DOM trees (HTML), B-trees (database indexes) — all use recursive traversal and manipulation.

## Backtracking Algorithms

Sudoku solvers, N-Queens, crossword generators — try a choice, recurse to see if it leads to a solution, undo if it does not.

> [↑ Back to Top](#top)

<a id="summary"></a>
## 🔥 Summary

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

| Concept | Key Takeaway |
|---------|-------------|
| Base case | The stopping condition — without it, infinite recursion |
| Recursive case | Calls itself with smaller input — must make progress |
| Call stack | Each call = one frame; depth = space cost |
| Linear recursion | O(n) time, O(n) space |
| Binary recursion | O(2^n) time — dangerous without memoization |
| Divide and conquer | O(n log n) time, O(log n) space |
| Memoization | Cache results → O(2^n) becomes O(n) |
| Tail recursion | No pending work after call — Python does NOT optimize it |

**Pre-Submission Checklist:**

- [ ] Is there a base case for every terminal condition?
- [ ] Does every code path return a value?
- [ ] Does the recursive call make progress toward the base case?
- [ ] Could the input depth exceed ~1000? (If yes: iterative or mention trade-off)
- [ ] Are there repeated subproblems? (If yes: add memoization)
- [ ] Mutable state check: no mutable default arguments?

**Performance estimation:**
- n = 30 with O(2^n) → 1 billion calls → too slow
- n = 10⁵ with linear recursion → stack overflow
- Always analyze: depth, branching factor, work per call

**Advanced topics for senior roles:**
- Tail recursion elimination (language dependent)
- Tabulation (iterative DP — bottom-up version of memoization)
- Recursion tree analysis
- Backtracking pruning
- Divide-and-conquer parallelization
- Ability to convert recursion to DP

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [03_strings → theory.md](../03_strings/theory.md) |
| ➡ Next Module | [05_sorting → theory.md](../05_sorting/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[03 Strings →](../03_strings/theory.md) · [05 Sorting →](../05_sorting/theory.md) · [14 Trees →](../14_trees/theory.md) · [20 Backtracking →](../20_backtracking/theory.md) · [21 Dynamic Programming →](../21_dynamic_programming/theory.md)

**Jump to specific topics in other files:**
- Merge sort (D&C applied) → [05_sorting § Merge Sort](../05_sorting/theory.md)
- Tree traversals (recursion applied) → [14_trees § Traversals](../14_trees/theory.md)
- Backtracking problems → [20_backtracking § theory.md](../20_backtracking/theory.md)
- Memoization → DP bridge → [21_dynamic_programming § theory.md](../21_dynamic_programming/theory.md)

> [↑ Back to Top](#top)
