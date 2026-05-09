# Practice — 01 Complexity Analysis

> 🟢 Basic · 🟡 Intermediate · 🟠 Advanced

---

## Quick Index

| # | Concept | Difficulty |
|---|---------|-----------|
| [Q1](#q1) | What Big-O measures | 🟢 |
| [Q2](#q2) | Constant time O(1) | 🟢 |
| [Q3](#q3) | Linear time O(n) | 🟢 |
| [Q4](#q4) | Quadratic time O(n²) — nested loops | 🟢 |
| [Q5](#q5) | Logarithmic time O(log n) | 🟢 |
| [Q6](#q6) | Drop constants rule | 🟢 |
| [Q7](#q7) | Drop lower-order terms rule | 🟢 |
| [Q8](#q8) | Best vs worst vs average case | 🟢 |
| [Q9](#q9) | Space complexity — O(1) vs O(n) | 🟡 |
| [Q10](#q10) | Consecutive loops — add or multiply? | 🟡 |
| [Q11](#q11) | Recognizing O(log n) from code | 🟡 |
| [Q12](#q12) | Recursion and stack space | 🟡 |
| [Q13](#q13) | O(n log n) — where it comes from | 🟡 |
| [Q14](#q14) | O(2ⁿ) — exponential growth | 🟡 |
| [Q15](#q15) | Amortized analysis — list.append | 🟡 |
| [Q16](#q16) | Hidden O(n) in library calls | 🟡 |
| [Q17](#q17) | Choosing algorithm from input size | 🟡 |
| [Q18](#q18) | Time-space tradeoff | 🟡 |
| [Q19](#q19) | String concatenation in a loop | 🟡 |
| [Q20](#q20) | Pattern recognition table | 🟡 |
| [Q21](#q21) | Analyze a recursive Fibonacci | 🟠 |
| [Q22](#q22) | Derive complexity from nested structure | 🟠 |
| [Q23](#q23) | Amortized analysis — dynamic array doubling | 🟠 |
| [Q24](#q24) | Real-world: database index complexity | 🟠 |
| [Q25](#q25) | Master Theorem — merge sort derivation | 🟠 |

---

<a id="q1"></a>
### Q1 · big-o-definition — What does Big-O actually measure? 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


You have two functions that both produce correct output. Your colleague says "one is O(n) and the other is O(n²)." What exactly does that mean? What is Big-O NOT measuring?

<details>
<summary>Hint</summary>
Think about what changes when input grows from 1,000 to 1,000,000 items.
</details>

<details>
<summary>Answer</summary>

Big-O measures **growth rate** — how the number of operations scales as input size `n` grows. It is not measuring:
- Actual seconds or milliseconds
- Performance on small inputs
- How fast your CPU is

```python
def linear(arr):        # O(n) — operations grow proportionally with n
    for x in arr:
        print(x)

def quadratic(arr):     # O(n²) — operations grow with n squared
    for x in arr:
        for y in arr:
            print(x, y)
```

**Why:** If `n` doubles, O(n) does 2x work. O(n²) does 4x work. At n=1,000,000, O(n²) is 1,000,000x more work than O(n) — not just "slower," but categorically different.
</details>

---

<a id="q2"></a>
### Q2 · constant-time — Identify all O(1) operations 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


Which of the following are O(1) and which are not? Explain each.

```python
arr = [10, 20, 30, 40, 50]

a = arr[2]           # line A
b = len(arr)         # line B
arr.append(99)       # line C
arr.insert(0, 1)     # line D
x = 42 in {1, 2, 3} # line E
y = 42 in [1, 2, 3]  # line F
```

<details>
<summary>Hint</summary>
Hash tables and direct memory addresses are O(1). Shifting elements and scanning are not.
</details>

<details>
<summary>Answer</summary>

```python
a = arr[2]           # O(1) — direct memory address: base + 2 * element_size
b = len(arr)         # O(1) — Python stores length as a separate integer attribute
arr.append(99)       # O(1) amortized — occasional resize is O(n), but rare enough to average O(1)
arr.insert(0, 1)     # O(n) — must shift every existing element one position right
x = 42 in {1,2,3}   # O(1) average — hash set computes hash(42), goes to that slot
y = 42 in [1,2,3]    # O(n) — scans each element until found or exhausted
```

**Why:** O(1) requires a direct computation to reach the answer — an address calculation or a hash. Anything requiring a scan or a shift is O(n).
</details>

---

<a id="q3"></a>
### Q3 · linear-time — Write a function and predict its complexity 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


What is the time and space complexity of this function? Justify both.

```python
def find_max(nums):
    best = nums[0]
    for n in nums:
        if n > best:
            best = n
    return best
```

<details>
<summary>Hint</summary>
Count how many times the loop body executes relative to input length.
</details>

<details>
<summary>Answer</summary>

- **Time: O(n)** — the loop visits every element exactly once
- **Space: O(1)** — only `best` is stored, regardless of input size

```python
def find_max(nums):
    best = nums[0]       # ← O(1) — one assignment
    for n in nums:       # ← runs n times
        if n > best:     # ← O(1) comparison each iteration
            best = n     # ← O(1) assignment each iteration
    return best          # ← O(1)
```

Total time: n × O(1) = O(n). Total extra space: 1 variable = O(1).

**Why:** Space complexity counts only extra memory beyond the input. `best` is a single integer no matter how large `nums` is.
</details>

---

<a id="q4"></a>
### Q4 · quadratic-time — Spot O(n²) in nested loops 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


What is the complexity of each snippet below?

```python
# Snippet A
for i in range(n):
    for j in range(n):
        print(i, j)

# Snippet B
for i in range(n):
    for j in range(i, n):
        print(i, j)

# Snippet C
for i in range(n):
    for j in range(10):
        print(i, j)
```

<details>
<summary>Hint</summary>
For snippet B, count total iterations: n + (n-1) + (n-2) + ... + 1. For snippet C, the inner bound is a constant.
</details>

<details>
<summary>Answer</summary>

```
Snippet A: O(n²) — outer n times, inner n times each → n × n = n²

Snippet B: O(n²) — inner loop runs n, n-1, n-2, ..., 1 times
           Total = n(n+1)/2 ≈ n²/2 → O(n²) after dropping constant

Snippet C: O(n)  — inner loop runs exactly 10 times (constant), not n times
           Total = n × 10 = 10n → O(n)
```

**Why:** The key rule is nested loops multiply only when both bounds depend on `n`. A constant inner bound makes the outer loop dominant.
</details>

---

<a id="q5"></a>
### Q5 · logarithmic-time — Trace through binary search 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Binary search on a sorted array of 1,000 elements. How many comparisons in the worst case? What about 1,000,000 elements?

```python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2     # ← halve the search space
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

<details>
<summary>Hint</summary>
Each iteration cuts the remaining search space in half. How many times can you halve n before reaching 1?
</details>

<details>
<summary>Answer</summary>

The number of steps is the number of times you can halve `n` before reaching 1, which is log₂(n).

```
n = 1,000:     log₂(1000) ≈ 10 comparisons
n = 1,000,000: log₂(1,000,000) ≈ 20 comparisons
```

Going from 1,000 to 1,000,000 elements (1,000x more data) adds only 10 more comparisons. That is the magic of O(log n).

**Why:** Every iteration eliminates half the remaining candidates. This halving pattern is the signature of O(log n) — look for `mid = (lo + hi) // 2` or `n = n // 2` in any loop.
</details>

---

<a id="q6"></a>
### Q6 · drop-constants — Simplify these Big-O expressions 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


Simplify each expression to its proper Big-O form:

```
a) O(5n)
b) O(100)
c) O(3n² + 10n + 500)
d) O(n/2)
e) O(2ⁿ + n³)
```

<details>
<summary>Hint</summary>
Drop all constants (multiplicative and additive). Keep only the dominant term.
</details>

<details>
<summary>Answer</summary>

```
a) O(5n)               → O(n)   — constant factor 5 is irrelevant to growth
b) O(100)              → O(1)   — 100 is a fixed constant, no growth
c) O(3n² + 10n + 500)  → O(n²)  — n² dominates; n and 500 are noise at scale
d) O(n/2)              → O(n)   — 1/2 is a constant factor
e) O(2ⁿ + n³)          → O(2ⁿ)  — exponential always dominates polynomial
```

**Why:** At large `n`, constants and lower-order terms become irrelevant. At n=1,000,000: `3n² = 3×10¹²`, `10n = 10⁷`, `500 = 500`. The `10n` term is 0.0003% of `3n²`.
</details>

---

<a id="q7"></a>
### Q7 · lower-order-terms — What does "dominant term" mean? 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


A function does three things: sorts an array O(n log n), then scans it once O(n), then does a hash lookup O(1). What is the total time complexity?

<details>
<summary>Hint</summary>
Add complexities for sequential steps, then keep only the biggest term.
</details>

<details>
<summary>Answer</summary>

```
O(n log n) + O(n) + O(1)
= O(n log n + n + 1)
= O(n log n)            ← n log n dominates
```

At n=1,000,000:
- `n log n ≈ 20,000,000`
- `n = 1,000,000` (5% of the dominant term)
- `1 = 1` (irrelevant)

**Why:** Sequential operations add. After adding, drop all non-dominant terms. The sort is the bottleneck — no matter how fast you make the scan, the overall complexity is still bounded by the sort.
</details>

---

<a id="q8"></a>
### Q8 · best-worst-average — Phone book search analysis 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


You search for "Williams" in a phone book with n entries using linear scan. Describe the best case, worst case, and average case. Which one does Big-O refer to by default?

<details>
<summary>Hint</summary>
Think about where "Williams" could be positioned in the book.
</details>

<details>
<summary>Answer</summary>

```
Best case:    O(1) — "Williams" is the very first entry checked
Average case: O(n/2) → O(n) — found roughly halfway through
Worst case:   O(n) — "Williams" is last, or not in the book at all
```

Big-O **by default refers to the worst case** — it is a guarantee that performance cannot get worse than this bound.

**Why:** The worst case is the most useful for system design. It tells you: "No matter what input you receive, the algorithm will not take longer than this." Average case matters too, but when Big-O is stated without qualification, assume worst case.
</details>

---

<a id="q9"></a>
### Q9 · space-complexity — Classify these by space usage 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


State the space complexity of each function and why:

```python
def sum_list(nums):
    total = 0
    for n in nums:
        total += n
    return total

def double_list(nums):
    return [n * 2 for n in nums]

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

<details>
<summary>Hint</summary>
Space complexity counts: variables created, data structures allocated, and call stack frames for recursion.
</details>

<details>
<summary>Answer</summary>

```python
def sum_list(nums):        # Space: O(1)
    total = 0              # ← one integer, fixed size
    for n in nums:
        total += n
    return total

def double_list(nums):     # Space: O(n)
    return [n*2 for n in nums]  # ← new list of same length as input

def factorial(n):          # Space: O(n)
    if n <= 1:             # ← n stack frames deep at maximum
        return 1
    return n * factorial(n-1)  # ← each call sits on the call stack until base case
```

**Why:** `sum_list` reuses one variable regardless of input size. `double_list` creates a copy of the entire input. `factorial` creates n nested call frames — each frame holds local variables and the return address on the call stack.
</details>

---

<a id="q10"></a>
### Q10 · consecutive-vs-nested — Add vs multiply loops 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


What is the complexity of each? Explain whether you add or multiply the loop costs.

```python
# Function A
def func_a(arr):
    for x in arr:       # loop 1
        print(x)
    for y in arr:       # loop 2
        print(y)

# Function B
def func_b(arr):
    for x in arr:       # outer
        for y in arr:   # inner
            print(x, y)
```

<details>
<summary>Hint</summary>
Are the loops sequential (one after the other) or nested (one inside the other)?
</details>

<details>
<summary>Answer</summary>

```
func_a:
  loop 1: O(n)
  loop 2: O(n)
  Sequential → ADD → O(n) + O(n) = O(2n) → O(n)

func_b:
  outer: O(n)
  inner: O(n) per outer iteration
  Nested → MULTIPLY → O(n) × O(n) = O(n²)
```

**Why:** Sequential steps add because you do them one after the other — total work is their sum. Nested loops multiply because for each outer iteration you complete all inner iterations — total work is their product.
</details>

---

<a id="q11"></a>
### Q11 · recognize-log-n — Spot logarithmic patterns in code 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


Which of these code patterns indicates O(log n) and why?

```python
# Pattern A
while n > 1:
    n = n // 2

# Pattern B
for i in range(n):
    i += 1

# Pattern C
lo, hi = 0, n
while lo < hi:
    mid = (lo + hi) // 2
    lo = mid + 1
```

<details>
<summary>Hint</summary>
O(log n) means the work is cut by a fraction (usually half) each iteration — not decremented by 1.
</details>

<details>
<summary>Answer</summary>

```
Pattern A: O(log n) — n is halved each iteration: n → n/2 → n/4 → ... → 1
           Number of steps = log₂(n)

Pattern B: O(n) — i increments by 1 each iteration, not divided
           Loop runs n times total

Pattern C: O(log n) — binary search pattern: search space halved each step
           hi - lo shrinks by half each iteration
```

The **halving fingerprint**: whenever you see `n //= 2`, `n >>= 1`, or `mid = (lo+hi)//2`, think O(log n).

**Why:** Halving is fundamentally different from decrementing. To go from 1,000,000 to 1 by halving takes 20 steps. By decrementing takes 1,000,000 steps.
</details>

---

<a id="q12"></a>
### Q12 · recursion-space — Stack frames and space complexity 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


What is the time and space complexity of this countdown function? Draw the call stack for `countdown(4)`.

```python
def countdown(n):
    if n == 0:
        return
    print(n)
    countdown(n - 1)
```

<details>
<summary>Hint</summary>
Each recursive call creates a new stack frame. How deep does the stack get?
</details>

<details>
<summary>Answer</summary>

**Time: O(n)** — n recursive calls, each doing O(1) work.
**Space: O(n)** — the call stack grows n frames deep before unwinding.

```
Call stack at deepest point (countdown(4)):

  countdown(0)  ← top of stack (base case)
  countdown(1)  ← waiting for countdown(0) to return
  countdown(2)  ← waiting for countdown(1) to return
  countdown(3)  ← waiting for countdown(2) to return
  countdown(4)  ← bottom (original call)
```

All 5 frames exist simultaneously in memory. At n=100,000, this is 100,000 frames on the stack — Python will raise `RecursionError` at its default limit of ~1,000.

**Why:** Recursion does not "clean up" each frame until the base case is reached and the stack unwinds. This is why recursive O(n) depth functions use O(n) space even when each frame is tiny.
</details>

---

<a id="q13"></a>
### Q13 · n-log-n — Where does O(n log n) come from? 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


Merge sort splits an array in half recursively, then merges. Explain intuitively why merge sort is O(n log n), not O(n) or O(n²).

```
Array: [5, 3, 8, 1, 9, 2, 7, 4]  — n = 8
```

<details>
<summary>Hint</summary>
How many levels of splitting are there? How much total work happens at each level?
</details>

<details>
<summary>Answer</summary>

```
Level 0 (1 array of 8):   [5,3,8,1,9,2,7,4]           — merge work: 8
Level 1 (2 arrays of 4):  [5,3,8,1]  [9,2,7,4]        — merge work: 8
Level 2 (4 arrays of 2):  [5,3][8,1] [9,2][7,4]       — merge work: 8
Level 3 (8 arrays of 1):  [5][3][8][1][9][2][7][4]    — merge work: 8
```

- There are `log₂(n)` levels of splitting (log₂(8) = 3)
- At each level, merging all sub-arrays costs O(n) total work
- Total: `log n` levels × `n` work per level = **O(n log n)**

**Why:** O(n²) would mean every element is compared to every other element. Merge sort avoids this by only merging sorted halves — each element participates in only O(log n) merges, not n merges.
</details>

---

<a id="q14"></a>
### Q14 · exponential-growth — Why O(2ⁿ) is practically unusable 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


The naive recursive Fibonacci is O(2ⁿ). Calculate the number of calls for n=10, n=20, n=40. At 10⁹ operations/second, how long does fib(40) take?

<details>
<summary>Hint</summary>
2ⁿ means each increase in n doubles the work. Use 2^n as the approximation.
</details>

<details>
<summary>Answer</summary>

```
fib(10):  2^10 =          1,024 calls  → ~0.000001 seconds
fib(20):  2^20 =      1,048,576 calls  → ~0.001 seconds
fib(40):  2^40 = 1,099,511,627,776 calls → ~1,100 seconds ≈ 18 minutes
fib(50):  2^50 ≈ 10^15 calls           → ~11 days
```

Each increase of 1 in `n` **doubles** the work. This is the definition of explosive growth.

**Why:** The naive Fibonacci recomputes the same sub-problems repeatedly. fib(3) is computed for every branch that needs it — which is exponentially many branches. The fix is memoization (O(n) time, O(n) space) or iteration (O(n) time, O(1) space).
</details>

---

<a id="q15"></a>
### Q15 · amortized-analysis — list.append is O(1)... sometimes O(n) 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


Python's `list.append()` is described as "O(1) amortized." What does that mean? When is it actually O(n), and why does the average still come out to O(1)?

<details>
<summary>Hint</summary>
Think about what happens when the underlying array runs out of space. How does doubling affect the total cost across many appends?
</details>

<details>
<summary>Answer</summary>

When a Python list runs out of capacity, it allocates a new array of **double the size** and copies all elements.

```
Capacity: 1 → 2 → 4 → 8 → 16 → 32 ...

Append 1:  no resize  — cost 1
Append 2:  resize!    — copy 1 element, cost 2
Append 3:  resize!    — copy 2 elements, cost 3
Append 5:  resize!    — copy 4 elements, cost 5
Append 9:  resize!    — copy 8 elements, cost 9
```

Total copy work for n appends: `1 + 2 + 4 + 8 + ... ≈ n` (geometric series sums to ≤ 2n).

So n appends cost O(n) total → O(1) amortized per append.

**Why:** Resizes happen exponentially rarely (after 1, 2, 4, 8, ... appends). By the time you resize again, you have "saved up" enough O(1) appends to pay for the O(n) copy. This is the banker's analogy — each cheap append deposits a coin; each resize withdraws them.
</details>

---

<a id="q16"></a>
### Q16 · hidden-costs — The invisible O(n) in your code 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


A developer writes this to build a queue. What is wrong with it, and what is the actual total complexity?

```python
queue = []
for item in data:           # n items
    queue.insert(0, item)   # add to front
```

<details>
<summary>Hint</summary>
What does `list.insert(0, x)` have to do before placing the new element?
</details>

<details>
<summary>Answer</summary>

`list.insert(0, item)` is **O(n)** because every existing element must be shifted one position right to make room at index 0.

```
Insert X at front of [A, B, C, D]:
  shift D → [A, B, C, _, D]
  shift C → [A, B, _, C, D]
  shift B → [A, _, B, C, D]
  shift A → [_, A, B, C, D]
  place X → [X, A, B, C, D]   — n shifts for n elements
```

Total: n inserts × O(n) each = **O(n²)** overall.

The fix:

```python
from collections import deque
queue = deque()
for item in data:
    queue.appendleft(item)  # O(1) — pointer manipulation, no shifting
```

**Why:** `deque` uses a doubly-linked list of blocks. Prepending is pointer manipulation — O(1). Use `deque` whenever you need O(1) operations on both ends.
</details>

---

<a id="q17"></a>
### Q17 · input-size-constraints — Pick the right algorithm from constraints 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


An interviewer gives you these problems. For each, state the maximum acceptable complexity and whether O(n²) is viable.

```
a) n ≤ 100
b) n ≤ 1,000
c) n ≤ 100,000
d) n ≤ 10,000,000
```

<details>
<summary>Hint</summary>
A modern computer runs ~10⁸ simple operations per second. Calculate operations at each n for O(n²) and O(n log n).
</details>

<details>
<summary>Answer</summary>

```
n ≤ 100:        O(n²) = 10,000 ops        → fine, even O(n³) is OK
n ≤ 1,000:      O(n²) = 1,000,000 ops     → acceptable (~0.01 sec)
n ≤ 100,000:    O(n²) = 10,000,000,000    → 100 seconds → NOT acceptable
                O(n log n) ≈ 1,700,000    → ~0.017 seconds → fine
n ≤ 10,000,000: O(n) = 10,000,000 ops     → fine
                O(n log n) ≈ 230,000,000  → borderline
```

**Why:** `n ≤ 10⁵` is the classic interview cutoff. It quietly tells you: O(n²) will TLE (Time Limit Exceeded). You need O(n log n) or better. Read constraints before you write a single line of code.
</details>

---

<a id="q18"></a>
### Q18 · time-space-tradeoff — When to trade memory for speed 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


You need to find if any two numbers in an array sum to a target value.

- Approach A: Check every pair — O(n²) time, O(1) space
- Approach B: Use a hash set — O(n) time, O(n) space

When would you choose A over B?

<details>
<summary>Hint</summary>
Consider: what if n is small? What if you are severely memory constrained (e.g., embedded systems)?
</details>

<details>
<summary>Answer</summary>

```python
# Approach A — O(n²) time, O(1) space
def two_sum_brute(nums, target):
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            if nums[i] + nums[j] == target:
                return True
    return False

# Approach B — O(n) time, O(n) space
def two_sum_hash(nums, target):
    seen = set()
    for n in nums:
        if target - n in seen:    # ← O(1) lookup
            return True
        seen.add(n)
    return False
```

Choose A (brute force) when:
- n is very small (≤ 100) and memory is critically constrained
- Running on embedded hardware with kilobytes of RAM
- Memory allocation overhead is unacceptable

Choose B (hash set) for every practical scenario in interviews and production.

**Why:** The time-space tradeoff is real engineering. Hashing buys O(n) time by spending O(n) space. Neither approach is universally correct — it depends on your system constraints.
</details>

---

<a id="q19"></a>
### Q19 · string-concatenation — Why `s += c` in a loop is O(n²) 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


This code builds a reversed string. What is its actual time complexity? Rewrite it to be O(n).

```python
def reverse_string(s):
    result = ""
    for ch in s:
        result = ch + result   # prepend each character
    return result
```

<details>
<summary>Hint</summary>
In Python, strings are immutable. Each `+` creates a brand-new string object. How many characters are copied in total across all iterations?
</details>

<details>
<summary>Answer</summary>

Each `ch + result` creates a new string by copying all characters of `result` plus `ch`. At iteration `i`, result has `i` characters — so `i` characters are copied.

```
Total copies = 0 + 1 + 2 + ... + (n-1) = n(n-1)/2 ≈ n²/2 → O(n²)
```

O(n) fix using a list:

```python
def reverse_string_fast(s):
    parts = []
    for ch in s:
        parts.append(ch)       # O(1) amortized — no copy
    parts.reverse()            # O(n) — one pass
    return "".join(parts)      # O(n) — one final copy

# Or simply:
def reverse_string_pythonic(s):
    return s[::-1]             # O(n) — one copy via slice
```

**Why:** `''.join(list)` copies each character exactly once at the end. Building with `+` in a loop copies the entire growing string on every iteration — classic O(n²) trap.
</details>

---

<a id="q20"></a>
### Q20 · pattern-recognition — Match code patterns to complexity 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


For each pattern, state the Big-O:

```python
# Pattern 1
while n > 0:
    n -= 1

# Pattern 2
while n > 1:
    n //= 3

# Pattern 3
for i in range(n):
    for j in range(i):
        print(i, j)

# Pattern 4
for i in range(n):
    for j in range(n):
        for k in range(n):
            print(i, j, k)

# Pattern 5 — recursive
def f(n):
    if n <= 0: return
    f(n // 2)
    f(n // 2)
```

<details>
<summary>Hint</summary>
Pattern 2: divide by 3 instead of 2 — still logarithmic. Pattern 5: draw the recursion tree.
</details>

<details>
<summary>Answer</summary>

```
Pattern 1: O(n)      — n decrements by 1 each time, so n steps total
Pattern 2: O(log n)  — n divided by 3 each step: log₃(n) steps
Pattern 3: O(n²)     — inner runs 0+1+2+...+(n-1) = n(n-1)/2 ≈ n²/2 → O(n²)
Pattern 4: O(n³)     — three nested loops, each over n → n×n×n = n³
Pattern 5: O(n)      — recurrence T(n) = 2T(n/2) + O(1)
                        By Master Theorem: a=2, b=2, d=0 → log₂(2)=1 > 0 → O(n^1) = O(n)
```

**Why:** Log n appears whenever you divide (not subtract). Three nested loops give cubic. The recursive case with two calls on half the input resolves to linear by the Master Theorem.
</details>

---

<a id="q21"></a>
### Q21 · recursive-fibonacci — Analyze naive vs memoized Fibonacci 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)


Analyze the time and space complexity of all three implementations. Explain why naive recursive Fibonacci is O(2ⁿ) using the call tree.

```python
def fib_naive(n):
    if n <= 1: return n
    return fib_naive(n-1) + fib_naive(n-2)

from functools import lru_cache
@lru_cache(maxsize=None)
def fib_memo(n):
    if n <= 1: return n
    return fib_memo(n-1) + fib_memo(n-2)

def fib_iter(n):
    if n <= 1: return n
    a, b = 0, 1
    for _ in range(2, n+1):
        a, b = b, a + b
    return b
```

<details>
<summary>Hint</summary>
For the call tree: fib(5) calls fib(4) and fib(3). fib(4) calls fib(3) and fib(2). How many times is fib(2) computed?
</details>

<details>
<summary>Answer</summary>

**fib_naive:**

```
Time: O(2ⁿ) — every call branches into two, forming a binary tree of depth n
              fib(n-2) is recomputed exponentially many times

Call tree for fib(5):
              fib(5)
            /        \
         fib(4)     fib(3)       ← fib(3) computed 2x
        /     \     /    \
     fib(3) fib(2) fib(2) fib(1) ← fib(2) computed 3x
     /   \
  fib(2) fib(1)

Space: O(n) — maximum stack depth is n frames
```

**fib_memo:**
```
Time:  O(n) — each value computed exactly once, then cached
Space: O(n) — cache holds n values + O(n) call stack depth
             (still hits recursion limit at large n!)
```

**fib_iter:**
```
Time:  O(n) — single loop, n iterations
Space: O(1) — only two variables a, b regardless of n
              no recursion, no stack growth, no cache
```

**Why:** Memoization eliminates recomputation but keeps the recursive call stack. Iteration eliminates both. For production code handling large n, `fib_iter` is the only safe choice — no stack overflow risk.
</details>

---

<a id="q22"></a>
### Q22 · complex-analysis — Derive complexity for mixed structures 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)


Analyze the time complexity of this function precisely. Justify each term.

```python
def process(matrix, queries):
    # matrix is n x n, queries is a list of m values
    result = []

    # Part 1: flatten matrix
    flat = []
    for row in matrix:
        for val in row:
            flat.append(val)

    # Part 2: sort the flattened list
    flat.sort()

    # Part 3: for each query, binary search flat
    for q in queries:
        lo, hi = 0, len(flat) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if flat[mid] == q:
                result.append(mid)
                break
            elif flat[mid] < q:
                lo = mid + 1
            else:
                hi = mid - 1

    return result
```

<details>
<summary>Hint</summary>
The matrix has n² total elements. Sort is O(k log k) where k is the number of elements. Binary search is O(log k). There are m queries.
</details>

<details>
<summary>Answer</summary>

```
Part 1: Flatten matrix
  n rows × n columns = n² elements visited
  Time: O(n²)
  Space: O(n²) — flat list holds all n² elements

Part 2: Sort flat list
  flat has n² elements, so k = n²
  Time: O(n² log n²) = O(n² × 2 log n) = O(n² log n)

Part 3: Binary search for m queries
  Each binary search on n² elements: O(log n²) = O(2 log n) = O(log n)
  m queries: O(m log n)

Total time: O(n²) + O(n² log n) + O(m log n)
           = O(n² log n + m log n)
           = O((n² + m) log n)

Total space: O(n²) for flat list
```

**Why:** When inputs are independent (n for matrix size, m for query count), keep them separate — do not collapse `m` into `n`. The dominant term in practice depends on whether `m` or `n²` is larger.
</details>

---

<a id="q23"></a>
### Q23 · dynamic-array-doubling — Prove O(1) amortized for append 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)


Prove rigorously that n appends to a Python list cost O(n) total, making each append O(1) amortized. Use the aggregate method.

<details>
<summary>Hint</summary>
Capacities double: 1, 2, 4, 8, 16, ..., n. Write out the copy costs at each resize. Sum the geometric series.
</details>

<details>
<summary>Answer</summary>

When capacity doubles, all current elements are copied. Resize events happen at sizes 1, 2, 4, 8, ..., n.

Copy costs at each resize:
```
At capacity 1  → copy 1 element
At capacity 2  → copy 2 elements
At capacity 4  → copy 4 elements
...
At capacity n  → copy n elements

Total copy cost = 1 + 2 + 4 + 8 + ... + n
```

This is a geometric series with ratio 2:
```
Sum = n × (1 - (1/2)^(log₂n)) / (1 - 1/2)
    ≤ 2n

More simply: 1 + 2 + 4 + ... + n/2 + n = 2n - 1  (geometric series formula)
```

Total work for n appends:
```
= n (the actual inserts) + (2n - 1) (the copies)
= 3n - 1
= O(n)
```

Per-append amortized cost: O(n) / n = **O(1)**

**Why:** The doubling strategy is key. If the array grew by a fixed amount instead of doubling, resizes would happen O(n) times and total copy work would be O(n²). Doubling makes resizes happen only O(log n) times — rare enough that the total copy work is still linear.
</details>

---

<a id="q24"></a>
### Q24 · database-index — Real-world O(log n) vs O(n) 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)


A `users` table has 10,000,000 rows. You run:

```sql
SELECT * FROM users WHERE email = 'alice@example.com';
```

Without an index, this takes 8 seconds. With a B-tree index on `email`, it takes under 1 millisecond. Calculate the theoretical speedup using complexity analysis. What is the space cost of the index?

<details>
<summary>Hint</summary>
Without index: full table scan O(n). With B-tree index: O(log n). Space for the index: O(n).
</details>

<details>
<summary>Answer</summary>

```
n = 10,000,000 rows

Without index (full scan):
  Operations: O(n) = 10,000,000 row reads
  Time: 8 seconds

With B-tree index:
  Operations: O(log₂ n) = log₂(10,000,000) ≈ 23 comparisons
  Time: ~23 operations × (time per operation) ≈ microseconds

Theoretical speedup:
  n / log₂(n) = 10,000,000 / 23 ≈ 435,000x fewer operations

  If full scan = 8 seconds:
  Indexed = 8 / 435,000 ≈ 0.000018 seconds ≈ 18 microseconds
```

**Space cost of the index:** O(n) — the B-tree stores one entry per row (the indexed column value + row pointer). For 10M rows with 50-byte email strings, that is ~500MB — a real cost worth paying.

**Why:** This is the fundamental database design tradeoff: O(n) extra space at write time buys O(log n) lookup at read time. The index is a precomputed sorted structure. Adding a row now costs O(log n) to update the index — but that is still fast. This pattern (pay at write, win at read) is everywhere in production systems.
</details>

---

<a id="q25"></a>
### Q25 · master-theorem — Derive merge sort's complexity formally 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)


Use the Master Theorem to formally derive the time complexity of merge sort. State the recurrence relation, identify a, b, d, and apply the correct case.

```
Merge sort recurrence:
  T(n) = 2 · T(n/2) + O(n)
```

<details>
<summary>Hint</summary>
Master Theorem: T(n) = a·T(n/b) + O(n^d). Compare d with log_b(a). Three cases determine the result.
</details>

<details>
<summary>Answer</summary>

**Master Theorem:** For `T(n) = a·T(n/b) + O(n^d)`:
- Case 1: d < log_b(a) → T(n) = O(n^(log_b a))
- Case 2: d = log_b(a) → T(n) = O(n^d · log n)
- Case 3: d > log_b(a) → T(n) = O(n^d)

**Merge sort:** `T(n) = 2·T(n/2) + O(n)`

```
a = 2  (two recursive subproblems)
b = 2  (each subproblem is half the size)
d = 1  (merge step is O(n) = O(n^1))

Compare d with log_b(a):
  log_b(a) = log₂(2) = 1
  d = 1

d == log_b(a) → Case 2

T(n) = O(n^d · log n) = O(n¹ · log n) = O(n log n)
```

**Intuitive verification:**
- `log₂(n)` levels of recursion (halving until size 1)
- Each level does O(n) total merge work
- Total: `log₂(n) × O(n)` = O(n log n)

**Why:** The Master Theorem is a shortcut for divide-and-conquer recurrences. The three cases capture whether the recursion, the top-level work, or both equally dominate. For merge sort, they are perfectly balanced — that is why Case 2 applies and the `log n` factor appears.
</details>

---

## Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 💻 Practice Local | [practice_local.py](./practice_local.py) |
| ⚡ Cheat Sheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| ➡️ Next | [../02_arrays/practice.md](../02_arrays/practice.md) |

**[Back to README](../README.md)**
