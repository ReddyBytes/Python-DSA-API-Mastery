# Recursion — Practice Questions

> 25 questions covering base cases, call stack, all recursion patterns, memoization, and common mistakes.
> Work through these after reading `theory.md` and `visual_explanation.md`.

---

## Quick Index

| # | Title | Level |
|---|-------|-------|
| [Q1](#q1) | Identify the Base Case | Basic |
| [Q2](#q2) | Trace Factorial Call Stack | Basic |
| [Q3](#q3) | Write Factorial Recursively | Basic |
| [Q4](#q4) | Countdown — Add the Missing Base Case | Basic |
| [Q5](#q5) | Sum a List Recursively | Basic |
| [Q6](#q6) | Reverse a String Recursively | Basic |
| [Q7](#q7) | Recursive Power Function | Basic |
| [Q8](#q8) | Recursion vs Iteration — Pick the Right Tool | Basic |
| [Q9](#q9) | Linear vs Binary Recursion — Classify These Functions | Intermediate |
| [Q10](#q10) | Naive Fibonacci — Why Is It Slow? | Intermediate |
| [Q11](#q11) | Memoized Fibonacci | Intermediate |
| [Q12](#q12) | Binary Search Recursively | Intermediate |
| [Q13](#q13) | Flatten a Nested List | Intermediate |
| [Q14](#q14) | Binary Tree Inorder Traversal | Intermediate |
| [Q15](#q15) | Height of a Binary Tree | Intermediate |
| [Q16](#q16) | Count All Nodes in a Binary Tree | Intermediate |
| [Q17](#q17) | Flood Fill (Recursive Grid Paint) | Intermediate |
| [Q18](#q18) | Rewrite Factorial as Tail-Recursive | Intermediate |
| [Q19](#q19) | Debug — Missing Return Value | Intermediate |
| [Q20](#q20) | Debug — Wrong Base Case | Intermediate |
| [Q21](#q21) | Divide and Conquer — Merge Sort | Advanced |
| [Q22](#q22) | Backtracking — Generate All Subsets | Advanced |
| [Q23](#q23) | Backtracking — Generate All Permutations | Advanced |
| [Q24](#q24) | Tree Recursion — Count Root-to-Leaf Paths with Target Sum | Advanced |
| [Q25](#q25) | Memoization vs Tabulation — Convert fib to Bottom-Up DP | Advanced |

---

## Basic Questions

---

<a id="q1"></a>
### Q1 · identify-base-case

**What is a base case in recursion? Identify the base case(s) in the following function. Explain what would happen if you removed it.**

```python
def sum_down(n):
    if n == 0:
        return 0
    return n + sum_down(n - 1)
```

<details>
<summary>Hint</summary>

A base case is the condition that stops recursion. It is the smallest subproblem you can answer directly without another recursive call.

</details>

**Answer:**

The **base case** is `if n == 0: return 0`.

It is the condition where the function stops calling itself and returns a known value directly.

Without it:
```
sum_down(3) → sum_down(2) → sum_down(1) → sum_down(0) → sum_down(-1) → ...
```
The function recurses into negative integers forever, eventually crashing with `RecursionError: maximum recursion depth exceeded`.

**Why:** Every recursive function needs at least one base case — a point where the problem is small enough to answer directly. Removing it means the problem never bottoms out.

- Time: O(n)
- Space: O(n) — n stack frames at peak depth

---

<a id="q2"></a>
### Q2 · trace-factorial-stack

**Trace the exact call stack for `factorial(4)`. Show: (a) all frames when the stack is at peak depth, (b) the order in which frames are popped, (c) what value each frame returns.**

```python
def factorial(n):
    if n == 1:
        return 1
    return n * factorial(n - 1)
```

<details>
<summary>Hint</summary>

Draw the stack growing downward as calls are made, then show it shrinking as returns propagate back up.

</details>

**Answer:**

Phase 1 — stack grows (calls being pushed):
```
[ factorial(4) ]  n=4, waiting for factorial(3)
[ factorial(3) ]  n=3, waiting for factorial(2)
[ factorial(2) ]  n=2, waiting for factorial(1)
[ factorial(1) ]  n=1  ← base case, top of stack
```

Phase 2 — stack shrinks (returns propagating up):
```
factorial(1) returns 1
factorial(2) receives 1, computes 2*1=2, returns 2
factorial(3) receives 2, computes 3*2=6, returns 6
factorial(4) receives 6, computes 4*6=24, returns 24
```

**Why:** Each call is a **stack frame** storing local variables and a return address. The stack follows LIFO order — last pushed, first popped. Understanding this explains both the O(n) space cost and why results "bubble up" in reverse call order.

- Time: O(n)
- Space: O(n) — n frames live simultaneously at peak depth

---

<a id="q3"></a>
### Q3 · write-factorial

**Write a recursive factorial function that handles `n = 0` as well as `n >= 1`. Then write the same function iteratively. When would you prefer each version?**

<details>
<summary>Hint</summary>

0! = 1 by mathematical definition. Make sure your base case covers it. The iterative version uses a running product variable.

</details>

**Answer:**

```python
# Recursive
def factorial(n):
    if n == 0:          # ← base case: 0! = 1
        return 1
    return n * factorial(n - 1)

# Iterative
def factorial_iter(n):
    result = 1
    for i in range(2, n + 1):  # ← no stack frames, constant space
        result *= i
    return result
```

**Why:** The recursive version reads like the mathematical definition `n! = n * (n-1)!`. The iterative version avoids building n stack frames, making it safer for large n. In Python, which has no tail-call optimization, prefer iterative for n > 1000.

- Recursive Time: O(n) | Space: O(n)
- Iterative Time: O(n) | Space: O(1)

---

<a id="q4"></a>
### Q4 · countdown-base-case

**The following function is broken. Add the correct base case and explain why the original fails.**

```python
def countdown(n):
    print(n)
    countdown(n - 1)   # BUG: no base case
```

<details>
<summary>Hint</summary>

What value of n means "we're done counting down"? Add an `if` check before the recursive call.

</details>

**Answer:**

```python
def countdown(n):
    if n <= 0:          # ← base case: stop at zero
        return
    print(n)
    countdown(n - 1)
```

The original crashes with `RecursionError` because `n` decreases through 0, -1, -2, -3 … indefinitely. Python's call stack limit (~1000 frames) is hit almost instantly.

**Why:** The missing base case is the single most common recursion mistake. The fix is always: identify the smallest meaningful input and return directly for it, without another recursive call.

- Time: O(n)
- Space: O(n)

---

<a id="q5"></a>
### Q5 · sum-list-recursively

**Write a recursive function `sum_list(nums)` that returns the sum of all integers in a list. Do not use Python's built-in `sum()`. Then explain the recurrence relation.**

<details>
<summary>Hint</summary>

The sum of a list is: first element + sum of the rest. Base case: empty list = 0.

</details>

**Answer:**

```python
def sum_list(nums):
    if not nums:                        # ← base case: empty list
        return 0
    return nums[0] + sum_list(nums[1:]) # ← recursive case

# Alternatively, with an index (avoids list slicing overhead):
def sum_list_idx(nums, i=0):
    if i == len(nums):
        return 0
    return nums[i] + sum_list_idx(nums, i + 1)
```

Recurrence relation: `T(n) = T(n-1) + O(1)` which solves to O(n).

**Why:** This is a textbook example of **linear recursion** — one call per level, O(1) work per level. The index variant is preferred in production because list slicing `nums[1:]` creates a new list at each level, pushing space complexity to O(n²).

- Index variant Time: O(n) | Space: O(n) stack

---

<a id="q6"></a>
### Q6 · reverse-string

**Write a recursive function `reverse_str(s)` that reverses a string. Trace the call for `reverse_str("abc")`.**

<details>
<summary>Hint</summary>

Reversed string = last character + reversed(everything except last character). Or: first character goes to the end.

</details>

**Answer:**

```python
def reverse_str(s):
    if len(s) <= 1:                     # ← base case: single char or empty
        return s
    return s[-1] + reverse_str(s[:-1]) # ← last char + reverse of the rest
```

Trace for `"abc"`:
```
reverse_str("abc") = "c" + reverse_str("ab")
                           = "b" + reverse_str("a")
                                  = "a"  ← base case
                     = "b" + "a" = "ba"
           = "c" + "ba" = "cba"
```

**Why:** String slicing `s[:-1]` creates a new string each time, so stack depth equals the string length. This is clean and readable but O(n) space. For very long strings, `''.join(reversed(s))` is the production choice.

- Time: O(n²) due to string concatenation and slicing
- Space: O(n)

---

<a id="q7"></a>
### Q7 · power-function

**Implement `power(base, exp)` recursively. Then implement an optimized version using fast exponentiation (exponentiation by squaring). Show the time complexity of each.**

<details>
<summary>Hint</summary>

Naive: `power(b, n) = b * power(b, n-1)`. Fast: `power(b, n) = power(b, n//2)^2` when n is even, or `b * power(b, n-1)` when n is odd.

</details>

**Answer:**

```python
# Naive — O(n)
def power_naive(base, exp):
    if exp == 0:                          # ← base case: anything^0 = 1
        return 1
    return base * power_naive(base, exp - 1)

# Fast exponentiation — O(log n)
def power(base, exp):
    if exp == 0:
        return 1
    if exp % 2 == 0:                      # ← even: square the half-result
        half = power(base, exp // 2)
        return half * half
    return base * power(base, exp - 1)    # ← odd: reduce by 1
```

Example: `power(2, 8)` — naive makes 8 calls; fast makes `log₂(8) = 3` calls.

**Why:** Fast exponentiation is **divide and conquer** applied to multiplication. It is the algorithm behind Python's built-in `pow(base, exp, mod)` and RSA encryption. The key insight: `b^n = (b^(n/2))^2`, so each step halves the exponent.

- Naive Time: O(n) | Space: O(n)
- Fast Time: O(log n) | Space: O(log n)

---

<a id="q8"></a>
### Q8 · recursion-vs-iteration-tradeoff

**For each scenario below, decide whether recursion or iteration is the better choice and justify your answer.**

1. Compute the sum of integers 1 to n.
2. Traverse a binary tree in-order.
3. Walk a directory tree with unknown depth.
4. Find the nth Fibonacci number where n can be up to 10^6.

<details>
<summary>Hint</summary>

Consider stack depth, code clarity, and Python's recursion limit of ~1000 frames.

</details>

**Answer:**

| Scenario | Preferred | Reason |
|---|---|---|
| Sum 1 to n | Iteration | O(1) space; recursion adds O(n) frames for a trivial loop |
| Binary tree in-order | Recursion | Tree is a self-similar structure; recursive code mirrors the definition |
| Directory tree (unknown depth) | Iteration + explicit stack | Depth could exceed 1000; iterative DFS with a stack prevents RecursionError |
| Fibonacci n up to 10^6 | Iteration (bottom-up DP) | n=10^6 exceeds Python's recursion limit; O(n) loop with O(1) space is the only viable option |

**Why:** The guiding rule is: use recursion when the problem is **naturally self-similar** (trees, nested structures) and depth is bounded and small. Switch to iteration when depth can be large or when the iterative form is equally clear.

---

## Intermediate Questions

---

<a id="q9"></a>
### Q9 · linear-vs-binary-recursion

**Classify each function as linear recursion, binary recursion, or divide-and-conquer. State the time complexity of each.**

```python
# A
def func_a(n):
    if n <= 0: return
    func_a(n - 1)

# B
def func_b(n):
    if n <= 1: return
    func_b(n - 1)
    func_b(n - 1)

# C
def func_c(arr):
    if len(arr) <= 1: return arr
    mid = len(arr) // 2
    left = func_c(arr[:mid])
    right = func_c(arr[mid:])
    return sorted(left + right)
```

<details>
<summary>Hint</summary>

Count how many recursive calls each function makes per invocation. Divide-and-conquer splits the input size (n/2), binary tree recursion reduces by 1 with two branches.

</details>

**Answer:**

- **func_a** — **Linear recursion.** One call per level, depth n. Recurrence: `T(n) = T(n-1) + O(1)`. Time: O(n).
- **func_b** — **Binary recursion.** Two calls per level, each reducing n by 1. Recurrence: `T(n) = 2T(n-1) + O(1)`. Time: O(2^n). This grows exponentially — dangerous for large n.
- **func_c** — **Divide and conquer.** Splits the array in half each time. Recurrence: `T(n) = 2T(n/2) + O(n log n)`. Effectively merge sort. Time: O(n log n).

**Why:** The shape of the recursion tree determines complexity. A chain (linear) is O(n). A full binary tree where depth grows by 1 at each step (binary) is O(2^n). A balanced binary tree where input halves (divide-and-conquer) is O(n log n) or better.

---

<a id="q10"></a>
### Q10 · naive-fibonacci

**Explain why naive Fibonacci is O(2^n). Draw the partial recursion tree for `fib(5)` and count the number of times `fib(2)` is called. Then state what optimization fixes this.**

```python
def fib(n):
    if n <= 1: return n
    return fib(n - 1) + fib(n - 2)
```

<details>
<summary>Hint</summary>

Draw `fib(5)` expanding into `fib(4)` and `fib(3)`, then expand those. Mark every node where fib(2) appears.

</details>

**Answer:**

Partial tree for `fib(5)`:
```
                fib(5)
               /      \
          fib(4)        fib(3)
         /      \       /     \
     fib(3)   fib(2)* fib(2)* fib(1)
     /    \
 fib(2)* fib(1)
```

`fib(2)` is called **3 times**. `fib(3)` is called twice. Total calls for `fib(5)` = 15.

The recurrence is `T(n) = T(n-1) + T(n-2)`, which has the same growth rate as the Fibonacci sequence itself — O(φ^n) ≈ O(2^n).

The fix is **memoization**: cache each result the first time it is computed. Every unique argument is then computed once, reducing time to O(n).

**Why:** Overlapping subproblems are the signal that memoization (or dynamic programming) is needed. If the recursion tree has duplicate nodes, you are repeating work.

- Time: O(2^n) without memo
- Space: O(n) stack depth

---

<a id="q11"></a>
### Q11 · memoized-fibonacci

**Implement Fibonacci with memoization using a dictionary. Then implement it again using `@lru_cache`. Show the time complexity of each.**

<details>
<summary>Hint</summary>

With a dict: check the cache first, compute only if missing, store the result before returning. With `@lru_cache`: just add the decorator and the recursion stays the same.

</details>

**Answer:**

```python
# Manual memo dict
def fib_memo(n, memo=None):
    if memo is None:
        memo = {}                       # ← initialize fresh each top-level call
    if n in memo:
        return memo[n]                  # ← cache hit: O(1) lookup
    if n <= 1:
        return n
    memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]

# Using @lru_cache (cleaner)
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

`@lru_cache` stores results keyed by the function arguments. Arguments must be hashable. Call `fib.cache_clear()` between test cases if needed.

**Why:** Memoization converts an exponential recursion into a linear one by ensuring each unique subproblem is solved exactly once. This is the bridge between recursion and **dynamic programming**. The `@lru_cache` decorator is the idiomatic Python way to add memoization without changing the recursion logic.

- Time: O(n)
- Space: O(n) — both cache and call stack

---

<a id="q12"></a>
### Q12 · binary-search-recursively

**Implement binary search recursively. It should return the index of `target` in `nums`, or -1 if not found.**

<details>
<summary>Hint</summary>

Base case: `lo > hi` means the target is not present. Compare `mid` to target and recurse on the appropriate half.

</details>

**Answer:**

```python
def binary_search(nums, target, lo=0, hi=None):
    if hi is None:
        hi = len(nums) - 1

    if lo > hi:                         # ← base case: search space exhausted
        return -1

    mid = (lo + hi) // 2

    if nums[mid] == target:
        return mid                      # ← found
    if nums[mid] < target:
        return binary_search(nums, target, mid + 1, hi)  # ← right half
    return binary_search(nums, target, lo, mid - 1)      # ← left half
```

Example: `binary_search([1, 3, 5, 7, 9], 7)` → searches indices 0..4, then 3..4, returns index 3.

**Why:** Binary search is a classic **divide and conquer** algorithm. At each step it eliminates half the search space. The recurrence is `T(n) = T(n/2) + O(1)` → O(log n) time. The iterative version is preferred in production (avoids O(log n) stack frames), but the recursive form is common in interviews.

- Time: O(log n)
- Space: O(log n) — stack frames equal the number of halvings

---

<a id="q13"></a>
### Q13 · flatten-nested-list

**Write `flatten(nested)` that recursively flattens a list of arbitrarily nested lists into a single flat list.**

Example: `flatten([1, [2, [3, 4]], 5])` → `[1, 2, 3, 4, 5]`

<details>
<summary>Hint</summary>

For each element: if it is a list, recurse into it; if it is not a list, add it directly to the result. Base case is implicit in the loop finishing.

</details>

**Answer:**

```python
def flatten(nested):
    result = []
    for item in nested:
        if isinstance(item, list):      # ← recursive case: dig deeper
            result.extend(flatten(item))
        else:
            result.append(item)         # ← base case: scalar value
    return result
```

Alternative using a generator (more memory-efficient):
```python
def flatten_gen(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flatten_gen(item)
        else:
            yield item
```

**Why:** Nested lists are a self-similar structure — a list can contain lists. This is exactly the structure recursion is built for. The `isinstance(item, list)` check is the branching condition that decides whether to recurse or collect. Real-world use: JSON parsing, config file flattening, tree serialization.

- Time: O(n) where n is total number of scalar elements
- Space: O(d) where d is maximum nesting depth (call stack)

---

<a id="q14"></a>
### Q14 · tree-traversal

**Write recursive functions for all three depth-first tree traversals: inorder, preorder, and postorder. Demonstrate the output for the tree below.**

```
    4
   / \
  2   6
 / \ / \
1  3 5  7
```

<details>
<summary>Hint</summary>

Inorder: left → root → right (gives sorted order for BST). Preorder: root → left → right. Postorder: left → right → root.

</details>

**Answer:**

```python
class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def inorder(node):
    if node is None: return []          # ← base case
    return inorder(node.left) + [node.val] + inorder(node.right)

def preorder(node):
    if node is None: return []
    return [node.val] + preorder(node.left) + preorder(node.right)

def postorder(node):
    if node is None: return []
    return postorder(node.left) + postorder(node.right) + [node.val]
```

For the example tree:
- Inorder: `[1, 2, 3, 4, 5, 6, 7]` — sorted, because this is a BST
- Preorder: `[4, 2, 1, 3, 6, 5, 7]` — root first, used for serialization
- Postorder: `[1, 3, 2, 5, 7, 6, 4]` — children before parent, used for deletion

**Why:** Tree traversal is the canonical application of recursion. The recursive definition of a tree — "a node with left and right subtrees" — maps directly to the recursive calls. Each traversal variant just reorders when the current node's value is collected.

- Time: O(n) — every node visited once
- Space: O(h) — h is tree height; O(log n) balanced, O(n) skewed

---

<a id="q15"></a>
### Q15 · tree-height

**Write `tree_height(root)` that returns the height of a binary tree (number of nodes on the longest root-to-leaf path). Then explain the recurrence relation.**

<details>
<summary>Hint</summary>

Height of a tree = 1 + max(height of left subtree, height of right subtree). Base case: None returns 0.

</details>

**Answer:**

```python
def tree_height(root):
    if root is None:                    # ← base case: empty tree has height 0
        return 0
    left_h  = tree_height(root.left)
    right_h = tree_height(root.right)
    return 1 + max(left_h, right_h)    # ← combine: take the taller child
```

Recurrence: `T(n) = 2T(n/2) + O(1)` for a balanced tree.

For a single node: `tree_height = 1 + max(0, 0) = 1`.
For a leaf's parent: `1 + max(1, 0) = 2`.

**Why:** This is a classic **post-order** computation — you need both children's answers before you can compute the parent's answer. The `max()` at each node picks the longer path downward. Used in: AVL tree balancing, calculating tree diameter, React component depth analysis.

- Time: O(n)
- Space: O(h) — proportional to tree height

---

<a id="q16"></a>
### Q16 · count-tree-nodes

**Write `count_nodes(root)` that returns the total number of nodes in a binary tree. Then write a version that avoids global state (no global variable, no nonlocal).**

<details>
<summary>Hint</summary>

Count of a tree = 1 (current node) + count of left subtree + count of right subtree. Base case: None = 0.

</details>

**Answer:**

```python
# Clean version — no global state
def count_nodes(root):
    if root is None:                    # ← base case
        return 0
    return 1 + count_nodes(root.left) + count_nodes(root.right)
```

Common incorrect version using global state:
```python
count = 0                               # BUG: persists across calls
def count_bad(node):
    global count
    if node is None: return
    count += 1
    count_bad(node.left)
    count_bad(node.right)
```

The bad version returns 14 on the second call to the same tree because `count` is never reset.

**Why:** Recursive functions should return values, not accumulate into shared state. The clean version is a **pure function** — given the same input, it always returns the same output, with no side effects. This makes it safe to call multiple times and safe in multi-threaded code.

- Time: O(n)
- Space: O(h)

---

<a id="q17"></a>
### Q17 · flood-fill

**Implement `flood_fill(grid, row, col, new_color)`. Starting from `(row, col)`, change all connected cells of the same original color to `new_color` (4-directional). This is the algorithm behind the paint bucket tool.**

Example:
```
Input grid:          After flood_fill(grid, 1, 1, 3):
1 1 1                3 3 3
1 1 0                3 3 0
1 0 0                3 0 0
```

<details>
<summary>Hint</summary>

Base cases: out of bounds, already visited (wrong color), already new_color. Recursive step: paint the cell, then recurse in 4 directions.

</details>

**Answer:**

```python
def flood_fill(grid, row, col, new_color):
    rows, cols = len(grid), len(grid[0])
    original = grid[row][col]

    if original == new_color:           # ← already the target color: stop
        return grid

    def dfs(r, c):
        # Base cases
        if r < 0 or r >= rows or c < 0 or c >= cols:
            return                      # ← out of bounds
        if grid[r][c] != original:
            return                      # ← different color: boundary

        grid[r][c] = new_color          # ← paint this cell

        # Recursive step: 4 neighbors
        dfs(r + 1, c)                   # down
        dfs(r - 1, c)                   # up
        dfs(r, c + 1)                   # right
        dfs(r, c - 1)                   # left

    dfs(row, col)
    return grid
```

**Why:** Flood fill is **tree recursion on a 2D grid**. Each cell spawns up to 4 recursive calls, but cells are only painted once (the `grid[r][c] != original` check prevents revisiting). Used in: MS Paint, Photoshop bucket fill, island-counting problems (LeetCode 200), maze solving.

- Time: O(m * n) — each cell visited at most once
- Space: O(m * n) — worst case stack depth if entire grid is the same color

---

<a id="q18"></a>
### Q18 · tail-recursion-rewrite

**Rewrite `factorial(n)` as a tail-recursive function using an accumulator. Then explain whether Python benefits from this change and why.**

```python
# Original (non-tail-recursive)
def factorial(n):
    if n == 1: return 1
    return n * factorial(n - 1)     # ← multiplication is pending after call returns
```

<details>
<summary>Hint</summary>

Accumulator pattern: pass the running product as a second argument. When you reach the base case, return the accumulator directly.

</details>

**Answer:**

```python
def factorial_tail(n, acc=1):
    if n <= 1:
        return acc                      # ← return accumulated result directly
    return factorial_tail(n - 1, n * acc)  # ← nothing pending: this IS tail position
```

In a language with **tail call optimization (TCO)** like Scheme or Kotlin, the compiler reuses the current stack frame instead of pushing a new one — O(1) space.

In Python: CPython deliberately does not implement TCO. Guido van Rossum has stated this by design — stack traces should remain readable. So `factorial_tail(1000)` still crashes with RecursionError. The real fix is converting to a loop:

```python
def factorial_iter(n):
    acc = 1
    while n > 1:
        acc *= n
        n -= 1
    return acc
```

**Why:** Understanding tail recursion shows you know what the compiler can and cannot do. In interviews, mention TCO and Python's explicit lack of it. The accumulator pattern is still valuable as a step toward iterative conversion.

- Both versions: Time O(n), Space O(n) in Python

---

<a id="q19"></a>
### Q19 · missing-return-bug

**The following function always returns `None`. Identify the bug and fix it.**

```python
def sum_digits(n):
    if n < 10:
        return n
    sum_digits(n // 10) + (n % 10)     # BUG
```

<details>
<summary>Hint</summary>

The arithmetic expression is evaluated but its result is never returned. What keyword is missing?

</details>

**Answer:**

```python
def sum_digits(n):
    if n < 10:
        return n
    return sum_digits(n // 10) + (n % 10)   # ← added `return`
```

Without `return`, Python executes `sum_digits(n // 10) + (n % 10)`, computes a number, then silently discards it. The function falls off the end and returns `None`. When the caller tries to do arithmetic with `None`, it raises `TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'`.

**Why:** This is the third most common recursion mistake. Every code path in a recursive function that builds on a child result must `return` that result — not just call the function. The call stack propagates return values upward; if any frame drops the value, the chain breaks.

- Time: O(log n) — number of digits
- Space: O(log n)

---

<a id="q20"></a>
### Q20 · wrong-base-case-bug

**The following function returns 0 for any input. Identify the bug and fix it.**

```python
def factorial(n):
    if n == 0:
        return 0        # BUG
    return n * factorial(n - 1)
```

<details>
<summary>Hint</summary>

What is the correct mathematical value of 0!? Every multiplication by this base value will propagate through the entire call chain.

</details>

**Answer:**

```python
def factorial(n):
    if n == 0:
        return 1        # ← 0! = 1 by definition
    return n * factorial(n - 1)
```

With `return 0`: `factorial(5) = 5 * 4 * 3 * 2 * 1 * 0 = 0`. Every product chain hits zero at the base and zeroes out the whole result.

The base case value is the **seed** of the entire computation. Every recursive call multiplies its result by the seed's downstream chain. A wrong seed corrupts every answer.

**Why:** Test the base case explicitly before trusting any recursive function. `assert factorial(0) == 1` catches this in under a second. In interviews, always verify base cases with edge inputs first.

- Time: O(n)
- Space: O(n)

---

## Advanced Questions

---

<a id="q21"></a>
### Q21 · divide-and-conquer-merge-sort

**Implement merge sort from scratch. Label the three recursive phases: divide, conquer, combine. Derive the time complexity using the recurrence relation.**

<details>
<summary>Hint</summary>

Divide: find midpoint and split. Conquer: recursively sort each half. Combine: merge two sorted halves using a two-pointer technique.

</details>

**Answer:**

```python
def merge_sort(arr):
    # BASE CASE: a single element is already sorted
    if len(arr) <= 1:
        return arr

    # DIVIDE: split into two halves
    mid = len(arr) // 2
    left_half  = arr[:mid]
    right_half = arr[mid:]

    # CONQUER: recursively sort each half
    left_sorted  = merge_sort(left_half)
    right_sorted = merge_sort(right_half)

    # COMBINE: merge the two sorted halves
    return _merge(left_sorted, right_sorted)


def _merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])             # ← remaining elements
    result.extend(right[j:])
    return result
```

Recurrence: `T(n) = 2T(n/2) + O(n)`.

By the Master Theorem (Case 2: `a=2, b=2, f(n)=n, c=log₂2=1`): `T(n) = O(n log n)`.

Recursion tree: log n levels, each level processes O(n) total elements across all merge calls at that level.

**Why:** Merge sort is the canonical divide-and-conquer algorithm. It guarantees O(n log n) in all cases (unlike quicksort). Python's `timsort` is a hybrid merge sort. External sorting (datasets larger than RAM) uses merge sort exclusively. The merge step is what makes it O(n log n) rather than O(n).

- Time: O(n log n) — all cases
- Space: O(n) — temporary arrays during merge + O(log n) stack

---

<a id="q22"></a>
### Q22 · backtracking-subsets

**Implement `subsets(nums)` that returns all 2^n subsets of a list using backtracking. Walk through the execution for `[1, 2, 3]` and explain the choose-explore-unchoose pattern.**

<details>
<summary>Hint</summary>

At each position, you make a binary choice: include the element or skip it. Use a `current` list and append a copy when you record a subset. Use `pop()` to undo the choice.

</details>

**Answer:**

```python
def subsets(nums):
    result = []

    def backtrack(start, current):
        result.append(current[:])       # ← record a copy of current subset

        for i in range(start, len(nums)):
            current.append(nums[i])     # ← CHOOSE: include nums[i]
            backtrack(i + 1, current)   # ← EXPLORE: recurse with next elements
            current.pop()               # ← UNCHOOSE: remove nums[i] (backtrack)

    backtrack(0, [])
    return result
```

Execution tree for `[1, 2, 3]`:
```
backtrack(0, [])     → records []
  append 1 → backtrack(1, [1])  → records [1]
    append 2 → backtrack(2, [1,2]) → records [1,2]
      append 3 → backtrack(3, [1,2,3]) → records [1,2,3]
      pop 3 ← back to [1,2]
    pop 2 ← back to [1]
    append 3 → backtrack(3, [1,3]) → records [1,3]
    pop 3 ← back to [1]
  pop 1 ← back to []
  ... (continues for starting with 2, then 3)
```

Result: `[[], [1], [1,2], [1,2,3], [1,3], [2], [2,3], [3]]` — all 8 subsets.

**Why:** The **choose-explore-unchoose** pattern is the backbone of all backtracking. `current.pop()` is the "undo" step — it restores the state before the choice, so the next iteration starts from the same clean state. Forgetting `pop()` is the most common backtracking bug.

- Time: O(n * 2^n) — 2^n subsets, each copy takes O(n)
- Space: O(n) — maximum depth of the recursion tree

---

<a id="q23"></a>
### Q23 · backtracking-permutations

**Implement `permutations(nums)` that returns all n! orderings of the input list. Use the swap-based approach. Show why it is more space-efficient than the copy approach.**

<details>
<summary>Hint</summary>

Fix position `start` by trying every element from `start` to `end` there. Swap the chosen element to position `start`, recurse on the rest, then swap back.

</details>

**Answer:**

```python
def permutations(nums):
    result = []

    def backtrack(start):
        if start == len(nums):
            result.append(nums[:])      # ← record current arrangement
            return
        for i in range(start, len(nums)):
            nums[start], nums[i] = nums[i], nums[start]  # ← CHOOSE: swap to position
            backtrack(start + 1)                          # ← EXPLORE: fix next position
            nums[start], nums[i] = nums[i], nums[start]  # ← UNCHOOSE: swap back

    backtrack(0)
    return result
```

For `[1, 2, 3]`: produces `[[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,2,1], [3,1,2]]`.

Why swap-based is more efficient: the copy approach creates a new `remaining` list at each level — O(n) space per frame — totaling O(n²) across the depth. The swap-based approach works **in-place**: O(1) work per swap, O(n) total space for the stack.

**Why:** Permutations appear in: password brute-forcing, scheduling optimization, anagram detection, and combinatorics problems. The swap-based approach mirrors what backtracking compilers do — mutate state, recurse, restore state — all with minimal memory allocation.

- Time: O(n * n!) — n! permutations, each copy takes O(n)
- Space: O(n) — in-place swaps, depth n recursion

---

<a id="q24"></a>
### Q24 · tree-recursion-count-paths

**Write `path_sum(root, target)` that returns the count of all root-to-leaf paths whose values sum to `target`. Walk through the recursion for the tree below with target = 22.**

```
        5
       / \
      4   8
     /   / \
    11  13   4
   /  \       \
  7    2       1
```

<details>
<summary>Hint</summary>

At each node, subtract its value from the remaining target. At a leaf, check if remaining equals zero. Recurse into both children, summing their counts.

</details>

**Answer:**

```python
def path_sum(root, target):
    if root is None:
        return 0                        # ← base case: null node, no path

    remaining = target - root.val

    # Check if this is a leaf with exact match
    if root.left is None and root.right is None:
        return 1 if remaining == 0 else 0

    # Recurse into children, sum the counts
    return path_sum(root.left, remaining) + path_sum(root.right, remaining)
```

Trace for target=22:
```
path_sum(5, 22): remaining=17
  path_sum(4, 17): remaining=13
    path_sum(11, 13): remaining=2
      path_sum(7, 2): leaf, 2≠0 → 0
      path_sum(2, 2): leaf, 2==0 → 1   ← PATH FOUND: 5→4→11→2
  path_sum(8, 17): remaining=9
    path_sum(13, 9): leaf, 9≠0 → 0
    path_sum(4, 9): remaining=5
      path_sum(1, 5): leaf, 5≠0 → 0
Total: 1
```

**Why:** This is **tree recursion** — the problem branches at each node. The technique of passing a running `remaining` value (instead of computing the sum at leaves) keeps each frame O(1) space. This pattern generalizes to all "path with constraint" problems on trees.

- Time: O(n) — each node visited once
- Space: O(h) — h is tree height

---

<a id="q25"></a>
### Q25 · memoization-vs-tabulation

**Implement Fibonacci three ways: (1) naive recursion, (2) top-down memoization, (3) bottom-up tabulation (iterative DP). Compare time and space for each. Explain when you would choose each approach in production.**

<details>
<summary>Hint</summary>

Tabulation builds the answer from `fib(0)` up to `fib(n)` using a loop. It avoids recursion entirely — no stack frames, no RecursionError for large n.

</details>

**Answer:**

```python
# 1. Naive recursion — O(2^n) time, O(n) space
def fib_naive(n):
    if n <= 1: return n
    return fib_naive(n - 1) + fib_naive(n - 2)

# 2. Top-down memoization — O(n) time, O(n) space
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_memo(n):
    if n <= 1: return n
    return fib_memo(n - 1) + fib_memo(n - 2)

# 3. Bottom-up tabulation — O(n) time, O(1) space
def fib_dp(n):
    if n <= 1: return n
    a, b = 0, 1
    for _ in range(2, n + 1):          # ← build up from base cases
        a, b = b, a + b
    return b
```

Comparison:

| Approach | Time | Space | Stack Risk | Production Use |
|---|---|---|---|---|
| Naive | O(2^n) | O(n) | Yes | Never |
| Memoization | O(n) | O(n) | Yes (n > 1000) | Interviews, prototypes |
| Tabulation | O(n) | O(1) | No | Production, large n |

**When to choose each:**
- Naive: only to demonstrate the problem of exponential recursion
- Memoization: when the recurrence is complex and hard to flip bottom-up; n is bounded and small
- Tabulation: when n can be large (> 10^4), in production code, or when stack overflow is a risk

**Why:** Memoization and tabulation both solve the overlapping subproblem problem — they are two sides of dynamic programming. Memoization is top-down (recurse, cache), tabulation is bottom-up (loop, build). Tabulation is typically faster in practice (no function call overhead, no risk of RecursionError).

- Tabulation: Time O(n) | Space O(1) — the production winner

---

**[Back to README](../README.md)**

**Prev:** [← Interview Q&A](./interview.md) &nbsp;|&nbsp; **Next:** [Sorting — Theory →](../05_sorting/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheetsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
