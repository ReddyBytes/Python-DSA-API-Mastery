# DSA Practice — 100 Questions

> From complexity basics to FAANG-level critical thinking — work through all 100 without skipping.

---

## How to Use This File

1. Read the question. Stop. Think for at least 60 seconds before clicking the answer.
2. Use the "How to think through this" block — it teaches the reasoning pattern, not just the answer.
3. Do not rush. Finishing all 100 with real thought is worth more than skimming 300 questions passively.

---

## How to Think: The 5-Step Framework

1. **Restate** — What is the problem actually asking? What are the inputs and outputs?
2. **Identify the pattern** — Which DSA pattern applies? (sliding window, two pointers, BFS, DP, etc.)
3. **Recall the algorithm** — What is the exact approach? What data structures are needed?
4. **Trace through** — Walk through a small example manually. Verify your approach.
5. **Complexity check** — What is the time and space complexity? Can you do better?

---

## Progress Tracker

- [ ] Tier 1 — Foundations (Q1–Q25)
- [ ] Tier 2 — Core Algorithms & Structures (Q26–Q50)
- [ ] Tier 3 — Advanced Topics (Q51–Q75)
- [ ] Tier 4 — Interview & Scenario (Q76–Q90)
- [ ] Tier 5 — Critical Thinking (Q91–Q100)

---

## Question Types

| Tag | What it tests |
|---|---|
| `[Normal]` | Recall and apply — straightforward |
| `[Thinking]` | Requires reasoning about complexity or trade-offs |
| `[Logical]` | Trace execution or predict output |
| `[Critical]` | Edge case or tricky gotcha |
| `[Interview]` | Explain or compare in interview style |
| `[Code]` | Write or fix an algorithm |
| `[Design]` | Choose the right data structure or approach |

---

## Tier 1 — Foundations · Q1–Q25

> Focus: Big O, arrays, strings, recursion, sorting, searching, hashing, two pointers, sliding window

---

### Q1 · [Normal] · `big-o-notation`

> **What is Big O notation? What does it measure, and what does it NOT measure?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Big O notation describes how an algorithm's **time or space requirements grow** relative to input size n — it captures the asymptotic upper bound. It describes the worst-case growth rate, not the exact runtime.

What it measures: growth rate as n → ∞.
What it does NOT measure:
- Actual wall-clock time (a O(n²) algo with tiny constants can beat O(n log n) for small n)
- Constants and lower-order terms (O(2n + 5) → O(n))
- Best-case performance (that's Big Ω)

Common complexities ranked: O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ) < O(n!)

**How to think through this:**
1. Ask: "If I double the input size, how much more work does the algorithm do?"
2. Drop constants and lower-order terms — focus on the dominant term.
3. O(1) = fixed steps regardless of n; O(n²) = nested loops iterating over n each.

**Complexity:** N/A — conceptual question

**Key takeaway:** Big O is a growth rate, not a runtime — always drop constants and focus on the dominant term.

</details>

> 📖 **Theory:** [Complexity Analysis](./01_complexity_analysis/theory.md#big-o-notation--the-language-of-speed)

---

### Q2 · [Thinking] · `time-space-tradeoff`

> **What is the time-space tradeoff? Give a concrete example where you trade memory for speed.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The time-space tradeoff means: you can often make an algorithm faster by using more memory, or use less memory at the cost of more computation.

Classic example — **Two Sum problem**:
- Brute force: O(n²) time, O(1) space — check every pair.
- Hash map: O(n) time, O(n) space — store each number in a dict, look up complement in O(1).

Other examples:
- **Memoisation (DP)**: cache subproblem results → O(n) time instead of O(2ⁿ), at the cost of O(n) space.
- **Lookup tables**: precompute answers for all inputs → O(1) lookup at the cost of O(n) storage.
- **Tries**: O(L) string lookup (L = length) at the cost of O(alphabet × nodes) space.

**How to think through this:**
1. Start with the brute-force approach and its complexity.
2. Ask: "What am I recomputing repeatedly? Can I store it?"
3. The stored intermediate result is the memory cost that buys speed.

**Complexity:** Varies by algorithm

**Key takeaway:** Trading space for time is one of the most common optimisation patterns — hash maps, caches, and precomputed tables all exploit this.

</details>

> 📖 **Theory:** [Complexity Analysis](./01_complexity_analysis/theory.md#time-complexity--the-speed-meter)

---

### Q3 · [Thinking] · `amortised-complexity`

> **What is amortised complexity? Why does `list.append()` in Python have O(1) amortised time even though it occasionally triggers an O(n) resize?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Amortised complexity spreads the cost of expensive operations over a sequence of operations, giving the average cost per operation rather than worst-case per operation.

Python's list doubles in capacity when full. A resize copies all n elements — O(n). But it only happens when the list is full (at sizes 1, 2, 4, 8, 16, ...). Total copy work for n appends: 1 + 2 + 4 + ... + n ≈ 2n = O(n). Spread over n appends: O(n) / n = **O(1) amortised**.

Analogy: You take a taxi every day. Mostly it's $10. Once a month there's a $100 surge. Average per ride ≈ $13 — the expensive outlier is amortised across many cheap rides.

**How to think through this:**
1. Track total cost across N operations, not cost of a single worst-case operation.
2. If total cost is O(N), each operation is O(1) amortised.
3. Dynamic arrays, hash table resizing, and stack-based algorithms commonly use amortised analysis.

**Complexity:** O(1) amortised per append

**Key takeaway:** Amortised O(1) means the average per-operation cost over a sequence is O(1), even if individual operations are occasionally expensive.

</details>

> 📖 **Theory:** [Amortised Complexity](./01_complexity_analysis/theory.md)

---

### Q4 · [Code] · `two-pointer-opposite-ends`

> **Given a sorted array, find two numbers that sum to a target. Write the two-pointer solution and explain why it works.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
def two_sum_sorted(nums: list[int], target: int) -> tuple[int, int]:
    left, right = 0, len(nums) - 1
    while left < right:
        s = nums[left] + nums[right]
        if s == target:
            return (left, right)
        elif s < target:
            left += 1    # sum too small — move left pointer right
        else:
            right -= 1   # sum too big — move right pointer left
    return (-1, -1)
```

Why it works: The array is sorted. Start with the widest window (leftmost + rightmost). If the sum is too small, the only way to increase it is to move the left pointer right (to a larger number). If too large, move right pointer left. Each step eliminates at least one candidate — no backtracking needed.

**How to think through this:**
1. Sorted array → two ends give the minimum and maximum possible sum.
2. Compare current sum to target: too small → increase left; too large → decrease right.
3. Each pointer moves at most n times total → O(n) guaranteed.

**Complexity:** Time: O(n) · Space: O(1)

**Key takeaway:** Two pointers on a sorted array eliminate candidates systematically — converge from both ends toward the answer.

</details>

> 📖 **Theory:** [Two Pointers](./11_two_pointers/theory.md#two-pointers--thinking-with-two-moving-hands)

---

### Q5 · [Thinking] · `in-place-operations`

> **What does "in-place" mean in algorithms? What is the tradeoff and when should you avoid it?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
An in-place algorithm modifies the input data structure directly without allocating extra space proportional to input size. Space complexity is O(1) auxiliary (ignoring the input itself).

Examples: bubble sort (swaps elements), reversing an array with two pointers, Dutch National Flag (partition in-place).

**Tradeoffs:**
- Pro: O(1) extra space — critical for memory-constrained environments.
- Con: Destroys the original input — if the caller needs the original data, you must copy first.

When to avoid:
- When the original data must be preserved (e.g. the caller reuses the input).
- When in-place logic is significantly more complex (harder to reason about, more bugs).
- In functional/immutable paradigms.

**How to think through this:**
1. Ask: "Does the caller need the original array after this call?"
2. In-place = constant extra space; out-of-place = O(n) extra space but original preserved.
3. In interviews, clarify whether in-place is required before choosing approach.

**Complexity:** Time: O(n) · Space: O(1) for in-place

**Key takeaway:** In-place saves space at the cost of mutating input — always clarify whether the original data needs to be preserved.

</details>

> 📖 **Theory:** [In-Place Operations](./02_arrays/theory.md#in-place-vs-out-of-place-thinking)

---

### Q6 · [Code] · `rotate-array`

> **Rotate an array of n elements to the right by k steps in O(1) space. Example: [1,2,3,4,5], k=2 → [4,5,1,2,3]**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
def rotate(nums: list[int], k: int) -> None:
    n = len(nums)
    k = k % n               # handle k > n

    def reverse(l, r):
        while l < r:
            nums[l], nums[r] = nums[r], nums[l]
            l += 1; r -= 1

    reverse(0, n - 1)       # reverse entire array
    reverse(0, k - 1)       # reverse first k elements
    reverse(k, n - 1)       # reverse remaining elements
```

Trace: [1,2,3,4,5], k=2
1. Reverse all: [5,4,3,2,1]
2. Reverse first 2: [4,5,3,2,1]
3. Reverse last 3: [4,5,1,2,3] ✓

**How to think through this:**
1. Naive: shift one by one k times = O(nk). Using extra array = O(n) space.
2. Key insight: rotation = three reversals. This is a classic trick worth memorising.
3. Always handle `k % n` to avoid redundant full rotations.

**Complexity:** Time: O(n) · Space: O(1)

**Key takeaway:** Array rotation in O(1) space = three reversals: whole → first k → last n-k.

</details>

> 📖 **Theory:** [Array Rotation](./02_arrays/theory.md#arrays-in-python--complete-theory-zero-to-advanced)

---

### Q7 · [Code] · `anagram-detection`

> **Check if two strings are anagrams of each other. What are two approaches and their complexities?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
from collections import Counter

# Approach 1: Counter comparison — O(n)
def is_anagram_counter(s: str, t: str) -> bool:
    return Counter(s) == Counter(t)

# Approach 2: Sort — O(n log n)
def is_anagram_sort(s: str, t: str) -> bool:
    return sorted(s) == sorted(t)

# Approach 3: frequency array (for lowercase a-z only) — O(n)
def is_anagram_array(s: str, t: str) -> bool:
    if len(s) != len(t): return False
    count = [0] * 26
    for c in s: count[ord(c) - ord('a')] += 1
    for c in t: count[ord(c) - ord('a')] -= 1
    return all(x == 0 for x in count)
```

**How to think through this:**
1. Anagram = same characters, same frequencies. Two strings must have equal length.
2. Counter approach: O(n) time and space — most readable.
3. Sort approach: O(n log n) — simple but slower.
4. Frequency array: O(n) time, O(1) space (fixed 26 chars) — fastest in practice for ASCII.

**Complexity:** Counter: Time O(n) · Space O(n) | Sort: Time O(n log n) · Space O(n)

**Key takeaway:** Anagram = equal character frequencies. Counter comparison is the cleanest O(n) solution.

</details>

> 📖 **Theory:** [Anagram Detection](./03_strings/theory.md)

---

### Q8 · [Thinking] · `palindrome-check`

> **Check if a string is a palindrome, ignoring non-alphanumeric characters and case. What is the optimal approach?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
def is_palindrome(s: str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True
```

Two-pointer approach: start from both ends, skip non-alphanumeric characters, compare case-insensitively. O(n) time, O(1) space — no new string created.

Alternative (simpler, O(n) space): `clean = [c.lower() for c in s if c.isalnum()]; return clean == clean[::-1]`

**How to think through this:**
1. A palindrome reads the same forward and backward.
2. Two pointers from ends: compare, skip non-alpha, converge.
3. The in-place two-pointer avoids creating a cleaned string.

**Complexity:** Time: O(n) · Space: O(1)

**Key takeaway:** Two pointers from both ends is the O(1) space palindrome check — skip non-matching character types on the fly.

</details>

> 📖 **Theory:** [Palindrome](./03_strings/theory.md#13-palindrome-checking)

---

### Q9 · [Code] · `substring-search`

> **Implement a function to check if string `needle` exists in `haystack` without using built-in `find`/`in`. Explain the naive approach and mention KMP.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
# Naive approach — O(n*m)
def str_str(haystack: str, needle: str) -> int:
    if not needle: return 0
    n, m = len(haystack), len(needle)
    for i in range(n - m + 1):
        if haystack[i:i+m] == needle:  # O(m) comparison
            return i
    return -1
```

Naive: for each position in haystack, compare m characters → O(n·m) worst case.

**KMP (Knuth-Morris-Pratt)**: Precompute a "failure function" (LPS array) that tells you how many characters you can skip after a mismatch. Avoids re-comparing characters already matched. O(n + m) time, O(m) space.

KMP is important to know conceptually for interviews even if you don't implement it from scratch — understand that it achieves O(n+m) by preprocessing the pattern.

**How to think through this:**
1. Naive: slide a window of size m across haystack. Simple but O(n·m).
2. KMP: use previously matched info to avoid redundant comparisons.
3. In Python, `needle in haystack` uses an optimised algorithm internally.

**Complexity:** Naive: Time O(n·m) · Space O(1) | KMP: Time O(n+m) · Space O(m)

**Key takeaway:** Naive string search is O(n·m); KMP achieves O(n+m) by precomputing a failure function to skip redundant comparisons.

</details>

> 📖 **Theory:** [Substring Search](./03_strings/theory.md#14-substring-search)

---

### Q10 · [Normal] · `recursion-base-case`

> **What are the two essential components of every recursive function? What happens if the base case is missing?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Every recursive function needs:
1. **Base case** — the condition where recursion stops and returns a direct result.
2. **Recursive case** — the call to itself with a smaller/simpler subproblem, moving toward the base case.

```python
def factorial(n):
    if n == 0: return 1          # base case
    return n * factorial(n - 1)  # recursive case — n decreases each call
```

If the base case is missing (or the recursive case never reaches it): the function calls itself infinitely → **RecursionError: maximum recursion depth exceeded** (Python default limit: 1000).

The call stack grows with each recursive call (each frame stores local variables and return address). Without a base case, the stack overflows.

**How to think through this:**
1. Ask: "What is the simplest version of this problem I can solve directly?" → base case.
2. Ask: "How do I reduce the problem by one step?" → recursive case.
3. Always verify the recursive case moves toward the base case.

**Complexity:** Depends on algorithm; each call adds O(1) to call stack depth

**Key takeaway:** Base case = stop condition; recursive case = reduce problem and call self. Missing base case = stack overflow.

</details>

> 📖 **Theory:** [Base Case](./04_recursion/theory.md#1-base-case)

---

### Q11 · [Thinking] · `recursion-vs-iteration`

> **What is the tradeoff between recursion and iteration? When does recursion become dangerous?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Recursion:**
- Pro: Elegant and natural for tree/graph traversal, divide-and-conquer, backtracking.
- Con: Each call adds a stack frame → O(depth) space. Python's default stack limit is ~1000 frames. Risk of stack overflow on deep inputs.

**Iteration:**
- Pro: O(1) space for simple loops (no call stack growth).
- Con: More complex for naturally recursive problems (e.g. tree traversal requires an explicit stack).

Recursion is dangerous when:
1. Input depth is unbounded (e.g. a tree with n=100,000 nodes in a degenerate chain).
2. Python's recursion limit (~1000) is exceeded — raises `RecursionError`.
3. Tail recursion is used (Python does not optimise tail calls, unlike some languages).

Fix: convert to iterative with an explicit stack, or use `sys.setrecursionlimit()` cautiously.

**How to think through this:**
1. Depth of recursion = max call stack size. For n=10^6, recursion likely fails.
2. DFS on trees: recursion is natural but iterative stack is safer for large inputs.
3. DP problems: always prefer bottom-up iterative tabulation over recursive memoisation for large n.

**Complexity:** Recursive: Space O(depth); Iterative: Space O(1) to O(n) depending on explicit data structures

**Key takeaway:** Recursion is elegant but uses O(depth) stack space — convert to iterative for deep inputs or Python's 1000-frame limit.

</details>

> 📖 **Theory:** [Recursion vs Iteration](./04_recursion/theory.md#14-recursion-vs-iteration)

---

### Q12 · [Code] · `recursion-fibonacci`

> **Write Fibonacci using recursion, then memoisation, then bottom-up DP. Compare their complexities.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
# 1. Naive recursion — O(2^n) time, O(n) space
def fib_naive(n):
    if n <= 1: return n
    return fib_naive(n-1) + fib_naive(n-2)

# 2. Memoisation (top-down DP) — O(n) time, O(n) space
from functools import lru_cache
@lru_cache(maxsize=None)
def fib_memo(n):
    if n <= 1: return n
    return fib_memo(n-1) + fib_memo(n-2)

# 3. Bottom-up DP (tabulation) — O(n) time, O(n) space
def fib_dp(n):
    if n <= 1: return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]

# 4. Optimised DP — O(n) time, O(1) space
def fib_opt(n):
    if n <= 1: return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
```

**How to think through this:**
1. Naive recursion recomputes the same subproblems exponentially → O(2ⁿ).
2. Memoisation stores results → each subproblem computed once → O(n).
3. Bottom-up avoids recursion overhead; space-optimised version uses only two variables.

**Complexity:** Naive: O(2ⁿ) | Memo/DP: O(n) time O(n) space | Optimised: O(n) time O(1) space

**Key takeaway:** Fibonacci is the canonical example of exponential → polynomial optimisation via DP. Always favour the O(1) space iterative version in production.

</details>

> 📖 **Theory:** [Fibonacci](./04_recursion/theory.md)

---

### Q13 · [Interview] · `merge-sort-vs-quicksort`

> **Compare merge sort and quicksort. When would you choose one over the other?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

| | Merge Sort | Quicksort |
|---|---|---|
| Best case | O(n log n) | O(n log n) |
| Average case | O(n log n) | O(n log n) |
| Worst case | O(n log n) | O(n²) (bad pivot) |
| Space | O(n) — needs extra array | O(log n) in-place (stack) |
| Stable | Yes | No (typically) |
| Cache performance | Poor (jumps memory) | Good (sequential access) |

**Choose merge sort when:**
- Stability matters (preserving equal-element order).
- Sorting linked lists (no random access needed).
- External sorting (data doesn't fit in memory — merge works chunk by chunk).
- Guaranteed O(n log n) worst case is required.

**Choose quicksort when:**
- Average performance matters more than worst-case guarantees.
- In-place sorting with O(log n) stack space is preferred.
- Cache efficiency matters (quicksort has better cache locality in practice).
- Use randomised pivot to avoid O(n²) worst case.

**How to think through this:**
1. Quicksort's O(n²) worst case (sorted input with bad pivot) is avoided with random pivot.
2. Merge sort's O(n) extra space is the main drawback.
3. Python's `sorted()` uses Timsort — hybrid of merge sort + insertion sort, stable, O(n log n).

**Complexity:** Merge: O(n log n) all cases · Space O(n) | Quick: O(n log n) avg · Space O(log n)

**Key takeaway:** Quicksort wins in practice (cache-friendly, in-place) but merge sort wins when stability or guaranteed worst-case matters.

</details>

> 📖 **Theory:** [Merge Sort vs Quicksort](./05_sorting/theory.md#6-merge-sort--divide-and-conquer-strategy)

---

### Q14 · [Thinking] · `sorting-stability`

> **What does "stable sort" mean? Why does it matter? Give a concrete example where instability causes a bug.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A stable sort preserves the **relative order of equal elements** in the original input.

Example where instability matters:
```python
students = [("Alice", 85), ("Bob", 92), ("Charlie", 85)]
# Sort by grade ascending
# Stable result: [("Alice", 85), ("Charlie", 85), ("Bob", 92)]
#   → Alice before Charlie (original order preserved)
# Unstable result might give: [("Charlie", 85), ("Alice", 85), ("Bob", 92)]
```

If you sort a table first by last name, then by first name, you need a stable second sort to preserve the last-name ordering among equal first names.

Real bug: Multi-key sorting with sequential single-key sorts. If the second sort is unstable, ties from the second sort randomly reorder what the first sort established.

Python's `sorted()` and `list.sort()` are stable (Timsort). Heapsort and quicksort are generally not stable.

**How to think through this:**
1. "Equal elements" — same sort key, different data.
2. Stability preserves the input ordering as a tiebreaker.
3. Multi-pass sorting (sort by A, then by B) requires stability to work correctly.

**Complexity:** N/A — property question

**Key takeaway:** Stable sort = equal elements keep their original relative order. Python's sort is stable; use it whenever tie-breaking by original position matters.

</details>

> 📖 **Theory:** [Sorting Stability](./05_sorting/theory.md#9-stability-explained-clearly)

---

### Q15 · [Normal] · `counting-sort`

> **When is counting sort faster than comparison-based sorts? What are its constraints?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Counting sort is O(n + k) where k is the range of values. It beats O(n log n) comparison sorts when k = O(n) — i.e. the value range is small relative to the input size.

```python
def counting_sort(arr: list[int], max_val: int) -> list[int]:
    count = [0] * (max_val + 1)
    for x in arr:
        count[x] += 1
    result = []
    for val, freq in enumerate(count):
        result.extend([val] * freq)
    return result
```

**Constraints:**
1. Elements must be non-negative integers (or mappable to integers).
2. Range k must be small — if k = 10^9, you need 10^9 buckets (not feasible).
3. Not comparison-based — bypasses the O(n log n) lower bound of comparison sorts.

Use cases: sort exam scores (0–100), sort ages, sort characters in a string.

**How to think through this:**
1. Comparison sort lower bound is Ω(n log n). Counting sort sidesteps this by using integer values directly as indices.
2. Time O(n+k), Space O(k). If k >> n, the space overhead is prohibitive.
3. Radix sort extends counting sort to handle large integers digit by digit.

**Complexity:** Time: O(n + k) · Space: O(k)

**Key takeaway:** Counting sort is O(n+k) — faster than O(n log n) when the value range k is small relative to n.

</details>

> 📖 **Theory:** [Counting Sort](./05_sorting/theory.md#counting-sort--on--k)

---

### Q16 · [Normal] · `binary-search-conditions`

> **What are the three conditions that must be true for binary search to be applicable?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
1. **Random access** — the data structure must support O(1) index access (arrays, not linked lists).
2. **Sorted order** — the search space must be ordered so you can determine which half to discard.
3. **A monotone condition** — there exists a property that is false for the first half and true for the second half (or vice versa), allowing you to eliminate half the search space at each step.

The third condition is key for "binary search on answer" problems — the array doesn't need to be sorted if you're searching for a value that satisfies a monotone predicate.

```python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2   # avoids integer overflow
        if arr[mid] == target: return mid
        elif arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1
```

**How to think through this:**
1. Sorted array → can compare middle element to target and discard half.
2. Use `lo + (hi - lo) // 2` instead of `(lo + hi) // 2` to avoid overflow (critical in C/Java).
3. Binary search on answer: search for smallest k where `f(k)` is true (e.g. minimum capacity, minimum days).

**Complexity:** Time: O(log n) · Space: O(1)

**Key takeaway:** Binary search needs sorted order (or a monotone condition) and random access — always use `lo + (hi - lo) // 2` to avoid overflow.

</details>

> 📖 **Theory:** [Binary Search](./13_binary_search/theory.md#binary-search--the-art-of-intelligent-guessing)

---

### Q17 · [Thinking] · `binary-search-on-answer`

> **What is "binary search on the answer"? Give an example problem where the array is not sorted but binary search still applies.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Binary search on the answer means searching over the **answer space** (not the input array) for the optimal value that satisfies a condition. The key is that the condition must be monotone: if some value k works, then all values > k (or < k) also work.

**Example — "Minimum Days to Make M Bouquets":**
- Given a blooming schedule, find the minimum number of days to collect m bouquets.
- The search space is [1, max_days]. For a given day d: can we make m bouquets? This is a yes/no function.
- Key insight: if day d works, day d+1 also works (more flowers bloom). Monotone → binary search applies.

```python
def min_days(bloomDay, m, k):
    def can_make(d):
        bouquets = flowers = 0
        for b in bloomDay:
            if b <= d: flowers += 1; bouquets += flowers // k; flowers %= k
            else: flowers = 0
        return bouquets >= m

    lo, hi = 1, max(bloomDay)
    while lo < hi:
        mid = (lo + hi) // 2
        if can_make(mid): hi = mid
        else: lo = mid + 1
    return lo
```

**How to think through this:**
1. Ask: "Is there a monotone yes/no function over some answer range?"
2. Binary search over the answer range, checking feasibility at each midpoint.
3. Common pattern: "minimum X such that condition holds" → binary search + greedy check.

**Complexity:** Time: O(n log(max_val)) · Space: O(1)

**Key takeaway:** Binary search on answer = search over the answer space using a monotone feasibility check, not over the input array.

</details>

> 📖 **Theory:** [Binary Search on Answer](./13_binary_search/theory.md#8-binary-search-on-answer-very-important)

---

### Q18 · [Normal] · `hash-map-internals`

> **How does a hash map work internally? What causes collisions and how are they handled?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A hash map stores key-value pairs in an array of buckets. To store a key:
1. Compute `hash(key)` → an integer.
2. Map to a bucket index: `index = hash(key) % num_buckets`.
3. Store the pair at that index.

**Collisions** occur when two different keys hash to the same bucket index.

**Collision handling:**
- **Chaining** (Python uses this): each bucket holds a linked list (or list) of pairs. Lookup: hash → bucket → scan chain for matching key.
- **Open addressing**: if bucket is occupied, probe the next bucket (linear, quadratic, or double hashing).

Python's dict uses open addressing with a perturbation scheme for probing. Load factor (entries/buckets) is kept below 2/3; when exceeded, the table doubles and all entries are rehashed.

**How to think through this:**
1. Hash function maps key → integer → bucket index.
2. Collision: two keys in same bucket → scan to find the right one.
3. Good hash functions spread keys uniformly; poor ones cause clustering → O(n) lookup in worst case.

**Complexity:** Average: O(1) get/set/delete · Worst case (all collide): O(n)

**Key takeaway:** Hash maps are O(1) average due to hash functions + collision handling; worst case O(n) if hash function is poor (rare in practice).

</details>

> 📖 **Theory:** [Hash Map Internals](./10_hashing/theory.md#hashing--the-power-of-instant-lookup)

---

### Q19 · [Code] · `frequency-counting`

> **Find the first non-repeating character in a string. What is the optimal approach?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
from collections import Counter, OrderedDict

# Approach 1: Counter — O(n) time, O(1) space (26 chars max)
def first_unique(s: str) -> str:
    count = Counter(s)
    for c in s:
        if count[c] == 1:
            return c
    return ""

# Approach 2: OrderedDict (preserves insertion order) — same complexity
def first_unique_ordered(s: str) -> str:
    freq = OrderedDict()
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    for c, cnt in freq.items():
        if cnt == 1:
            return c
    return ""
```

Two passes: first build frequency map, then scan string again to find first char with frequency 1. O(n) time, O(1) space (bounded alphabet).

**How to think through this:**
1. Need both frequency AND position — can't just find min-frequency character.
2. First pass: count all characters. Second pass: scan string in order, return first with count 1.
3. The second pass preserves order (unlike iterating the Counter which may not be ordered).

**Complexity:** Time: O(n) · Space: O(1) (alphabet size is constant)

**Key takeaway:** Two-pass frequency count: build the map first, then scan original order to find the first unique — order matters, so scan the string not the map.

</details>

> 📖 **Theory:** [Frequency Counting](./10_hashing/theory.md)

---

### Q20 · [Critical] · `hash-map-vs-hash-set`

> **What is the difference between a hash map and a hash set? When do you use each?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
- **Hash map** (dict): stores key-value pairs. O(1) lookup, insert, delete by key. Use when you need to associate data with a key.
- **Hash set** (set): stores unique keys only, no values. O(1) membership test. Use when you only need to track existence, not associated data.

In Python: `dict` = hash map, `set` = hash set. A `set` is essentially a `dict` with no values (same underlying hash table).

When to use:
- **Hash map**: word → frequency, user_id → user_object, cache key → result.
- **Hash set**: visited nodes in graph traversal, "have I seen this value?" deduplication, intersection/union of collections.

```python
# set for membership
visited = set()
if node not in visited:
    visited.add(node)

# dict for association
word_count = {}
word_count[word] = word_count.get(word, 0) + 1
```

**How to think through this:**
1. Do you need the value associated with a key? → dict.
2. Do you just need to know if something exists? → set (cheaper, cleaner).
3. Sets support set algebra: union `|`, intersection `&`, difference `-` — very useful.

**Complexity:** Both: O(1) average for insert/lookup/delete

**Key takeaway:** Set = existence check; dict = key-value association. Use sets for visited tracking and deduplication.

</details>

> 📖 **Theory:** [HashMap vs HashSet](./10_hashing/theory.md#6-hashing-in-python-dictionary--set)

---

### Q21 · [Code] · `two-pointer-fast-slow`

> **Detect a cycle in a linked list using O(1) space. How does Floyd's algorithm work?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val; self.next = next

def has_cycle(head: ListNode) -> bool:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next          # move 1 step
        fast = fast.next.next     # move 2 steps
        if slow is fast:          # they meet inside the cycle
            return True
    return False
```

**Floyd's Tortoise and Hare:**
- Slow pointer moves 1 step per iteration; fast moves 2.
- If there's no cycle, fast reaches None.
- If there's a cycle, fast laps slow inside the cycle — they must meet because fast gains 1 step per iteration and the cycle is finite.

**Extension — find cycle start:**
After detection, reset slow to head. Move both pointers 1 step at a time. They meet at the cycle start. (Mathematical proof involves cycle length modular arithmetic.)

**How to think through this:**
1. Two pointers at different speeds: if a cycle exists, the fast pointer will eventually catch the slow one.
2. Think of a circular track: a faster runner laps a slower one eventually.
3. O(1) space — no visited set needed.

**Complexity:** Time: O(n) · Space: O(1)

**Key takeaway:** Floyd's cycle detection = fast/slow pointer; they meet iff a cycle exists. Resetting slow to head finds the cycle entry point.

</details>

> 📖 **Theory:** [Fast-Slow Pointers](./11_two_pointers/theory.md)

---

### Q22 · [Code] · `two-pointer-3sum`

> **Find all unique triplets in an array that sum to zero. Explain the two-pointer approach after sorting.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
def three_sum(nums: list[int]) -> list[list[int]]:
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i-1]:
            continue                      # skip duplicate first element
        left, right = i + 1, len(nums) - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s == 0:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left+1]: left += 1   # skip dups
                while left < right and nums[right] == nums[right-1]: right -= 1
                left += 1; right -= 1
            elif s < 0: left += 1
            else: right -= 1
    return result
```

Key: sort first → fix one element (outer loop) → use two-pointer for the remaining pair. Deduplication via skip-same-element logic.

**How to think through this:**
1. Brute force = O(n³) — check all triples.
2. Sort + fix one + two-pointer = O(n²) — the fixed element reduces to a Two Sum problem.
3. Skip duplicates at every level to avoid duplicate triplets in output.

**Complexity:** Time: O(n²) · Space: O(1) extra (output space not counted)

**Key takeaway:** 3Sum = sort + fix one element + two-pointer Two Sum on the rest = O(n²). Skip duplicates carefully at each pointer.

</details>

> 📖 **Theory:** [Three Sum](./11_two_pointers/theory.md#5-example--two-sum-in-sorted-array)

---

### Q23 · [Thinking] · `two-pointer-partition`

> **What is the Dutch National Flag problem? How does it demonstrate the power of the three-way partition?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Sort an array containing only 0s, 1s, and 2s in O(n) time, O(1) space — without counting.

```python
def sort_colors(nums: list[int]) -> None:
    low = 0          # boundary: [0..low-1] = all 0s
    mid = 0          # current element
    high = len(nums) - 1  # boundary: [high+1..n-1] = all 2s

    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1; mid += 1
        elif nums[mid] == 1:
            mid += 1             # 1 is in correct region, just advance
        else:                    # nums[mid] == 2
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1            # don't advance mid — swapped element unexamined
```

Three pointers maintain three regions: [0s | 1s | unexamined | 2s]. The `mid` pointer scans and routes elements to the correct region.

**How to think through this:**
1. Classic Dijkstra problem. Three partitions, two boundary pointers.
2. When swapping from the right (`high`), don't advance `mid` — the swapped element is unseen.
3. When swapping from the left (`low`), advance `mid` — swapped element is a 1 (already processed).

**Complexity:** Time: O(n) · Space: O(1)

**Key takeaway:** Dutch National Flag = three-pointer partition. A single pass sorts three categories in O(n) time, O(1) space.

</details>

> 📖 **Theory:** [Partition](./11_two_pointers/theory.md#partitioning-problems)

---

### Q24 · [Code] · `sliding-window-fixed`

> **Find the maximum sum subarray of size k. Write the fixed sliding window solution.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
```python
def max_sum_subarray(nums: list[int], k: int) -> int:
    if len(nums) < k: return 0

    # Build first window
    window_sum = sum(nums[:k])
    max_sum = window_sum

    # Slide: add new element, remove leftmost
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]   # slide right
        max_sum = max(max_sum, window_sum)

    return max_sum
```

The window slides one step at a time: add the incoming element, subtract the outgoing element. O(n) instead of recomputing the sum from scratch each time (which would be O(n·k)).

**How to think through this:**
1. Brute force: for each position, sum k elements → O(n·k).
2. Sliding window: maintain a running sum, add right edge, remove left edge → O(n).
3. Key: `window_sum += nums[i] - nums[i-k]` is the slide operation.

**Complexity:** Time: O(n) · Space: O(1)

**Key takeaway:** Fixed sliding window = add new element, subtract the leftmost. O(n) vs O(n·k) brute force.

</details>

> 📖 **Theory:** [Fixed Sliding Window](./12_sliding_window/theory.md#fixed-size-window)

---

### Q25 · [Thinking] · `sliding-window-variable`

> **When do you use a variable-size sliding window instead of fixed? Describe the expand/shrink pattern.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Use a variable-size window when you're looking for a **subarray/substring satisfying a condition** and the optimal window size is unknown.

Pattern:
1. **Expand** right pointer to include more elements.
2. **Shrink** left pointer when the window violates the condition.
3. Track the answer at each valid state.

```python
# Longest substring without repeating characters
def length_of_longest_substring(s: str) -> int:
    char_set = set()
    left = max_len = 0

    for right in range(len(s)):
        while s[right] in char_set:    # shrink until valid
            char_set.remove(s[left])
            left += 1
        char_set.add(s[right])         # expand
        max_len = max(max_len, right - left + 1)

    return max_len
```

The key invariant: the window [left, right] always satisfies the condition. Expand right freely; shrink left only when violated.

**How to think through this:**
1. Fixed window: size is given. Variable window: size is what you're optimising.
2. Expand right unconditionally. Shrink left when the window breaks the constraint.
3. Common conditions: at most k distinct chars, sum ≤ target, no repeats.

**Complexity:** Time: O(n) · Space: O(k) where k = window/set size

**Key takeaway:** Variable sliding window = expand right freely, shrink left when constraint violated. The window always maintains a valid state.

</details>

> 📖 **Theory:** [Variable Sliding Window](./12_sliding_window/theory.md#variable-size-window)

---

## 🔗 Tier 2 — Data Structures Deep Dive

---

### Q26 · [Normal] · `linked-list-operations`

> **Given a singly linked list, what are the time complexities of: insert at head, insert at tail (without tail pointer), delete by value, search by value?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Insert at head: O(1). Insert at tail (no tail pointer): O(n). Delete by value: O(n). Search by value: O(n).

**How to think through this:**
1. Insert at head — you already hold a reference to head; just point new node to old head and update head. No traversal needed.
2. Insert at tail (no tail pointer) — you must walk every node to reach the last one before you can append.
3. Delete and search both require traversal to find the target node, so O(n) in the worst case.

**Key takeaway:** Linked lists are O(1) at the head only — every operation elsewhere requires traversal and costs O(n).

</details>

> 📖 **Theory:** [Linked List Operations](./07_linked_list/theory.md#singly-linked-list)

---

### Q27 · [Thinking] · `linked-list-cycle`

> **Floyd's tortoise-and-hare cycle detection: how does it work and why does the fast pointer eventually meet the slow pointer? What is the time and space complexity?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Two pointers move through the list: **slow** advances one node per step, **fast** advances two. If a cycle exists, fast enters it first and laps slow inside the cycle — they are guaranteed to meet. If no cycle exists, fast reaches null.

**How to think through this:**
1. Imagine a circular track: if two runners start at the same point and one runs twice as fast, the faster runner will eventually lap and meet the slower one.
2. Once both pointers are inside the cycle, the distance between them decreases by 1 each step (fast gains one node per step relative to slow). They must collide.
3. If the list has no cycle, fast reaches null in O(n) steps — no meeting ever occurs.

**Complexity:** Time: O(n) · Space: O(1)

**Key takeaway:** Fast pointer laps slow inside the cycle — the relative speed of 1 node/step guarantees convergence without any extra memory.

</details>

> 📖 **Theory:** [Cycle Detection](./07_linked_list/theory.md#detect-cycle)

---

### Q28 · [Logical] · `linked-list-reversal`

> **Trace the execution of iterative linked list reversal on [1→2→3→4→null]. What is the state of `prev`, `curr`, `next` at each step?**

```python
def reverse(head):
    prev = None
    curr = head
    while curr:
        next = curr.next   # ← save next before overwriting
        curr.next = prev   # ← reverse the pointer
        prev = curr        # ← advance prev
        curr = next        # ← advance curr
    return prev
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**

| Step | prev | curr | next (saved) | action |
|------|------|------|-------------|--------|
| init | None | 1 | — | — |
| 1 | None | 1 | 2 | 1.next = None |
| 2 | 1 | 2 | 3 | 2.next = 1 |
| 3 | 2 | 3 | 4 | 3.next = 2 |
| 4 | 3 | 4 | None | 4.next = 3 |
| end | 4 | None | — | return prev (4) |

Result: 4→3→2→1→null

**How to think through this:**
1. You must save `curr.next` before you overwrite it — otherwise you lose the rest of the list.
2. Each iteration rewires one pointer backward and advances both prev and curr forward.
3. When curr reaches null, prev sits at the old tail, which is the new head.

**Complexity:** Time: O(n) · Space: O(1)

**Key takeaway:** Three-pointer dance — save next, reverse pointer, advance both. Never touch fewer than three variables or you lose the list.

</details>

> 📖 **Theory:** [Reverse Linked List](./07_linked_list/theory.md#reverse-linked-list)

---

### Q29 · [Normal] · `merge-sorted-lists`

> **How do you merge two sorted linked lists into one sorted list in O(n+m) time? Write the algorithm.**

```python
def merge_sorted(l1, l2):
    dummy = ListNode(0)   # ← sentinel avoids edge-case on empty lists
    curr = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            curr.next = l1
            l1 = l1.next
        else:
            curr.next = l2
            l2 = l2.next
        curr = curr.next
    curr.next = l1 or l2  # ← attach whichever list has remaining nodes
    return dummy.next
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Use a **dummy head** and a running pointer. At each step compare the heads of both lists, attach the smaller node, and advance that list's pointer. When one list is exhausted, attach the remainder of the other.

**How to think through this:**
1. Both lists are already sorted, so the next smallest element is always at one of the two heads — no need to look further.
2. A dummy sentinel node eliminates the special case of an empty result list.
3. When one list runs out, the other is already sorted — splice it in directly.

**Complexity:** Time: O(n+m) · Space: O(1)

**Key takeaway:** Merge is a single linear scan — always compare heads, always advance the smaller one. The dummy node keeps the code clean.

</details>

> 📖 **Theory:** [Merge Sorted Lists](./07_linked_list/theory.md#merge-two-sorted-lists)

---

### Q30 · [Interview] · `linked-list-tradeoffs`

> **Compare singly linked list vs doubly linked list vs dynamic array. When would you choose each?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Each structure trades memory for access capability.

**How to think through this:**
1. **Singly linked list**: one pointer per node. O(1) insert/delete at head. O(n) for everything else. Cannot traverse backward. Choose when you only need a stack or queue-like structure with minimal memory overhead.
2. **Doubly linked list**: two pointers per node (prev + next). O(1) insert/delete if you already hold the node reference (e.g., LRU cache). Enables backward traversal. Costs more memory per node. Choose when you need O(1) deletion from the middle and hold node references (e.g., combined with a hash map).
3. **Dynamic array**: contiguous memory. O(1) random access by index. O(n) insert/delete in the middle. Cache-friendly due to spatial locality. Choose when you need indexed access or iteration performance matters.

**Key takeaway:** Dynamic array wins for random access; doubly linked list wins for O(1) mid-list deletion when you already have the node; singly linked list is the lean choice for head-only operations.

</details>

> 📖 **Theory:** [Linked List Types](./07_linked_list/theory.md#singly-linked-list)

---

### Q31 · [Normal] · `stack-lifo-uses`

> **Name four real-world programming problems where a stack (LIFO) is the natural data structure to reach for. Explain why in each case.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
1. **Balanced parentheses checking** — push opens, pop and match on closes. The last-opened bracket must be the first closed.
2. **Function call stack / recursion simulation** — each call frame must finish before the caller resumes. LIFO mirrors this nesting exactly.
3. **Undo/redo in text editors** — the most recent action must be undone first. Each action is pushed; undo pops.
4. **DFS (depth-first search)** — explore as deep as possible before backtracking. An explicit stack replaces the recursion call stack.

**How to think through this:**
1. The key signal for a stack is **nesting** or **reverse-order processing** — the last thing in must be the first thing out.
2. Any problem involving "finish the inner thing before the outer thing" maps naturally to LIFO.
3. If you find yourself writing a recursive solution, you can almost always replace it with an explicit stack.

**Key takeaway:** Reach for a stack whenever nesting, reversal, or "most recent first" processing appears in the problem.

</details>

> 📖 **Theory:** [Stack LIFO](./08_stack/theory.md#13-where-you-use-stack-without-knowing)

---

### Q32 · [Logical] · `valid-parentheses`

> **Trace execution of the valid parentheses checker on `"({[]})"` and on `"({)]"`. What does the stack look like at each step?**

```python
def is_valid(s):
    match = {')': '(', '}': '{', ']': '['}
    stack = []
    for ch in s:
        if ch in '({[':
            stack.append(ch)
        else:
            if not stack or stack[-1] != match[ch]:
                return False
            stack.pop()
    return len(stack) == 0
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**`"({[]})"`** — returns `True`:

| char | action | stack |
|------|--------|-------|
| `(` | push | `['(']` |
| `{` | push | `['(', '{']` |
| `[` | push | `['(', '{', '[']` |
| `]` | match `[`, pop | `['(', '{']` |
| `}` | match `{`, pop | `['(']` |
| `)` | match `(`, pop | `[]` |

Stack empty → valid.

**`"({)]"`** — returns `False`:

| char | action | stack |
|------|--------|-------|
| `(` | push | `['(']` |
| `{` | push | `['(', '{']` |
| `)` | top is `{`, expected `(` | mismatch → False |

**How to think through this:**
1. Push every opener. When a closer arrives, the top of the stack must be its matching opener.
2. Any mismatch means a bracket was closed in the wrong order.
3. A non-empty stack at the end means unclosed openers remain.

**Complexity:** Time: O(n) · Space: O(n)

**Key takeaway:** The stack enforces nesting order — the innermost opener must always be closed first.

</details>

> 📖 **Theory:** [Parentheses Validation](./08_stack/theory.md#9-parentheses-validation--real-life-analogy)

---

### Q33 · [Thinking] · `monotonic-stack`

> **What is a monotonic stack? How does it solve the "next greater element" problem in O(n) instead of O(n²)?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **monotonic stack** is a stack that maintains elements in strictly increasing or strictly decreasing order. For "next greater element," you maintain a decreasing stack: when a new element is larger than the top, the top has found its answer.

**How to think through this:**
1. Brute force: for each element, scan right until you find something larger. O(n) per element → O(n²) total.
2. Insight: when you see a new element `x`, every element in the stack that is smaller than `x` has just found its "next greater" — `x` itself.
3. Pop those elements off (recording `x` as their answer), then push `x`. Any element remaining in the stack at the end has no greater element to its right.
4. Each element is pushed once and popped once → O(n) total.

**Complexity:** Time: O(n) · Space: O(n)

**Key takeaway:** The monotonic stack turns O(n²) "scan right for each" into O(n) by processing answers lazily — an element only reveals itself as someone's answer when it arrives.

</details>

> 📖 **Theory:** [Monotonic Stack](./08_stack/theory.md#11-monotonic-stack--daily-scenario)

---

### Q34 · [Normal] · `queue-deque-ops`

> **What is a deque (double-ended queue)? How does it generalize both a stack and a queue? What are its time complexities for each operation?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **deque** supports O(1) insert and delete at both ends: `appendleft`, `append`, `popleft`, `pop`. A stack uses only one end (append/pop); a queue uses both ends but in one direction (append/popleft). A deque allows all four combinations.

**How to think through this:**
1. Stack = LIFO → use only `append` and `pop` (right end only).
2. Queue = FIFO → use `append` (right) and `popleft` (left).
3. Deque removes this restriction — both ends are O(1), enabling sliding-window maximum problems (where you need to push/pop from both ends).
4. Python's `collections.deque` is implemented as a doubly linked list of fixed-size blocks, giving O(1) amortised operations at both ends.

**Key takeaway:** A deque is the superset — it emulates both stack and queue, and unlocks sliding-window maximum in O(n) by allowing O(1) removal from the front and back.

</details>

> 📖 **Theory:** [Queue & Deque](./09_queue/theory.md#9-double-ended-queue-deque)

---

### Q35 · [Logical] · `binary-tree-traversal`

> **For the tree: root=1, left=2, right=3, 2.left=4, 2.right=5 — write out the results of: inorder, preorder, postorder traversal.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

```
        1
       / \
      2   3
     / \
    4   5
```

- **Inorder** (left → root → right): `[4, 2, 5, 1, 3]`
- **Preorder** (root → left → right): `[1, 2, 4, 5, 3]`
- **Postorder** (left → right → root): `[4, 5, 2, 3, 1]`

**How to think through this:**
1. Inorder: go as left as possible (reach 4), then visit root of that subtree (2), then right child (5), then climb to root (1), then right subtree (3).
2. Preorder: visit root before children — root (1), then left subtree entirely (2, 4, 5), then right subtree (3).
3. Postorder: visit both children before the root — children of 2 first (4, 5), then 2 itself, then right subtree (3), then root (1).

**Complexity:** Time: O(n) · Space: O(h) where h = tree height (call stack)

**Key takeaway:** The three traversals differ only in when you visit the node relative to its children — before (pre), between (in), or after (post).

</details>

> 📖 **Theory:** [Tree Traversal](./14_trees/theory.md#7-tree-traversal--exploring-the-tree)

---

### Q36 · [Normal] · `bfs-level-order`

> **How does BFS level-order traversal of a binary tree work? What data structure does it use and why?**

```python
from collections import deque

def level_order(root):
    if not root:
        return []
    result, queue = [], deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):   # ← process exactly one level
            node = queue.popleft()
            level.append(node.val)
            if node.left:  queue.append(node.left)
            if node.right: queue.append(node.right)
        result.append(level)
    return result
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
BFS uses a **queue** (FIFO). Enqueue the root. On each iteration, dequeue a node, record its value, and enqueue its children. Processing left-to-right ensures nodes are visited level by level.

**How to think through this:**
1. A queue enforces FIFO: nodes added at a given level are all processed before any of their children (which were added later).
2. A stack would give DFS (depth-first), not level-order.
3. To group nodes by level, snapshot `len(queue)` at the start of each round — that count equals the number of nodes on the current level.

**Complexity:** Time: O(n) · Space: O(w) where w = max width of the tree

**Key takeaway:** Queue = BFS = level-by-level. The FIFO property guarantees you finish a level before descending.

</details>

> 📖 **Theory:** [BFS Level Order](./14_trees/theory.md#level-order-traversal--bfs-on-trees)

---

### Q37 · [Critical] · `bst-properties`

> **What property must a BST maintain? Is this tree a valid BST: root=5, left=3, right=7, 3.left=2, 3.right=6? Why or why not?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The tree is **not a valid BST**. Node 6 is in the left subtree of root 5, but 6 > 5. Every node in the left subtree must be strictly less than all ancestor nodes — not just its immediate parent.

**How to think through this:**
1. The BST property: for any node N, every value in its left subtree must be less than N.val, and every value in its right subtree must be greater than N.val.
2. Common mistake: only checking parent–child pairs. Node 3's right child is 6, and 6 > 3 — that looks fine. But 6 also sits in the left subtree of 5, violating 6 < 5.
3. Correct validation passes a `(min, max)` bound down the tree: left child inherits `max = parent.val`; right child inherits `min = parent.val`.

**Key takeaway:** BST validation is not just parent-child comparison — every node must satisfy the bounds inherited from all its ancestors.

</details>

> 📖 **Theory:** [BST Properties](./15_binary_search_trees/theory.md#12-validate-bst)

---

### Q38 · [Normal] · `bst-search-insert`

> **What is the time complexity of search, insert, and delete in a BST in the average case vs worst case? What causes worst case?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Average case: O(log n) for all three. Worst case: O(n) for all three. Worst case is caused by an **unbalanced / degenerate tree** — inserting sorted data into a BST produces a linked-list-shaped tree with height n.

**How to think through this:**
1. BST operations walk from root to a target node. The number of steps equals the height of the tree.
2. A balanced tree has height O(log n) — each level roughly halves the remaining nodes.
3. Inserting [1, 2, 3, 4, 5] in order creates a right-skewed tree of height 5, degrading all operations to O(n).
4. Self-balancing trees (AVL, Red-Black) enforce O(log n) worst case by rebalancing after each insert/delete.

**Key takeaway:** BST performance depends entirely on tree height — sorted insertion is the silent killer that degrades it to O(n).

</details>

> 📖 **Theory:** [BST Operations](./15_binary_search_trees/theory.md#binary-search-tree-bst--the-organized-tree)

---

### Q39 · [Thinking] · `tree-height-balance`

> **What is the difference between a balanced binary tree and an unbalanced one? How does balance affect BST operation complexity?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **balanced binary tree** has the property that for every node, the heights of its left and right subtrees differ by at most 1 (AVL definition). This constrains total height to O(log n). An unbalanced tree can degrade to height O(n).

**How to think through this:**
1. BST search follows a path from root to leaf — length = height. So height directly determines operation cost.
2. With n nodes, a perfectly balanced tree has height ⌊log₂n⌋. A fully degenerate tree (one child per node) has height n−1.
3. The gap is dramatic: for n = 1,000,000, balanced = ~20 steps; degenerate = 1,000,000 steps.
4. Self-balancing BSTs (AVL, Red-Black) pay a small constant overhead per operation to maintain balance, keeping all operations at O(log n) guaranteed.

**Key takeaway:** Balance converts "worst case O(n)" into "guaranteed O(log n)" — it is the difference between a useful search tree and a linked list in disguise.

</details>

> 📖 **Theory:** [Tree Height & Balance](./14_trees/theory.md#11-balanced-vs-skewed-tree)

---

### Q40 · [Normal] · `heap-property`

> **What invariant does a max-heap maintain? After inserting a new element, what operation restores the invariant and what is its time complexity?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **max-heap** maintains: every node's value is greater than or equal to its children's values. The root always holds the maximum. After insertion, **bubble-up** (also called sift-up or heapify-up) restores the invariant in O(log n).

**How to think through this:**
1. Insert the new element at the next available position (bottom-right of the last level) to maintain the complete binary tree shape.
2. Compare the new element with its parent. If it is larger, swap them. Repeat until the element is smaller than its parent or reaches the root.
3. A complete binary tree of n nodes has height ⌊log₂n⌋, so at most log n swaps are needed.

**Complexity:** Time: O(log n) · Space: O(1)

**Key takeaway:** Heap insert = place at bottom, bubble up. The heap's complete-tree shape guarantees the path length is O(log n).

</details>

> 📖 **Theory:** [Heap Property](./16_heaps/theory.md#4-heap-property)

---

### Q41 · [Design] · `heap-kth-largest`

> **You have a stream of n numbers and need to find the kth largest at any point. What data structure and what size of heap would you use? Why not sort?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Use a **min-heap of size k**. The root of the heap is always the kth largest seen so far. For each incoming number: if it exceeds the root (current kth largest), pop the root and push the new number; otherwise discard it.

**How to think through this:**
1. Sorting solves a snapshot but not a stream — each new element would require a full re-sort at O(n log n).
2. A max-heap of all n elements would let you pop k times but costs O(n) space and O(n + k log n) time.
3. A min-heap of fixed size k keeps the k largest elements seen so far. The smallest of those k elements (the root) is the kth largest overall. Each insertion costs O(log k).
4. For a stream of n elements: O(n log k) total time, O(k) space.

**Complexity:** Time: O(n log k) · Space: O(k)

**Key takeaway:** Min-heap of size k = "keep only the top k; the smallest of those is the kth largest." The heap does the eviction work automatically.

</details>

> 📖 **Theory:** [Kth Largest](./16_heaps/theory.md)

---

### Q42 · [Interview] · `heap-vs-bst`

> **Compare a heap vs a BST. What can each do efficiently that the other can't? When would you pick one over the other?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
They solve overlapping but distinct problems.

**How to think through this:**
1. **Heap strengths**: O(1) find-max (or find-min), O(log n) insert and extract-max. Implemented as a compact array — cache-friendly. Ideal when you only care about the extreme value (priority queue, kth largest, scheduling).
2. **BST strengths**: O(log n) search by arbitrary value, ordered traversal, predecessor/successor queries, range queries. A heap has no fast arbitrary search — you'd have to scan all n elements.
3. **Heap weakness**: searching for a specific value is O(n) because the heap property only constrains parent vs children, not siblings.
4. **BST weakness**: finding the min/max requires traversal to a leaf; a heap does it in O(1).

Choose **heap** when: you repeatedly need the min or max (top-k, scheduling, Dijkstra's algorithm).
Choose **BST** when: you need ordered data, range queries, or arbitrary value lookup.

**Key takeaway:** Heap = fast extremes, no search. BST = fast search and order, O(log n) extremes.

</details>

> 📖 **Theory:** [Heap vs BST](./16_heaps/theory.md#12-heap-vs-bst)

---

### Q43 · [Normal] · `trie-insert-search`

> **How does a Trie store the words ["cat", "car", "card", "care"]? Draw the structure and explain insert/search operations and their complexity.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

```
root
 └── c
      └── a
           └── t  (end)
           └── r  (end)
                └── d  (end)
                └── e  (end)
```

Shared prefixes share nodes. "ca" is stored once, branching at the 3rd character.

**How to think through this:**
1. **Insert**: walk the trie character by character. If the next character's child node exists, move to it. If not, create it. Mark the final node as a word-end.
2. **Search**: same traversal. If at any point the next character has no child node, the word is not present. Return true only if you reach the end and the node is marked as a word-end.
3. Complexity: both operations are O(L) where L = length of the word, regardless of how many words are in the trie.

**Complexity:** Time: O(L) insert and search · Space: O(total characters across all words, with sharing)

**Key takeaway:** A Trie is a tree of characters — shared prefixes share nodes, making prefix-based operations O(word length) independent of vocabulary size.

</details>

> 📖 **Theory:** [Trie Insert & Search](./17_trie/theory.md#6-inserting-word-into-trie)

---

### Q44 · [Thinking] · `trie-prefix-matching`

> **Why is a Trie faster than a hash map for prefix search? What is the time complexity of "find all words with prefix 'ca'"?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **hash map** gives O(1) exact lookup but has no structural relationship between keys — you must scan all n keys to find those sharing a prefix. A Trie encodes shared prefixes structurally: navigate to the prefix node in O(P) steps, then collect all words in the subtree below it.

**How to think through this:**
1. Hash maps destroy prefix structure — "cat" and "car" hash to unrelated buckets. There is no fast way to ask "give me all keys starting with 'ca'."
2. In a Trie, navigating to node `a` (child of `c`) takes exactly P steps where P = prefix length. Every word in the subtree rooted there shares the prefix by construction.
3. After reaching the prefix node in O(P), a DFS/BFS of the subtree collects all matching words in O(W) where W = total characters of all matching words.
4. Total: O(P + W). For a hash map it would be O(n · L) — checking every stored word.

**Complexity:** Time: O(P + W) where P = prefix length, W = total output characters

**Key takeaway:** Tries give "free" prefix navigation — the tree structure is the index. Hash maps are blind to prefix relationships.

</details>

> 📖 **Theory:** [Prefix Matching](./17_trie/theory.md#8-searching-prefix)

---

### Q45 · [Interview] · `trie-vs-hashmap`

> **Trie vs hash map for storing a dictionary of 100,000 words. Compare: memory usage, exact lookup speed, prefix search capability.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Each structure has a distinct profile:

**How to think through this:**
1. **Memory**: Hash map stores each word as a complete string key — O(n · L) total, but compact per entry. A Trie shares prefix nodes, which saves space when the vocabulary has long common prefixes (e.g., "unbelievable", "unbelievably" share most nodes). However, each trie node carries a children array or dict, adding per-node overhead. In practice, tries can use more memory than hash maps for short, dissimilar words.
2. **Exact lookup**: Hash map wins — O(L) to hash the key, O(1) expected lookup. Trie is O(L) with higher constant (pointer traversal per character vs single hash computation).
3. **Prefix search**: Trie wins decisively — O(P + W) as shown in Q44. Hash map requires O(n · L) scan of all keys. No contest.
4. **Practical rule**: use a hash map when you only need exact lookup; use a Trie (or sorted structure with binary search) when autocomplete, spell-check, or prefix enumeration is required.

**Key takeaway:** Hash map = faster exact lookup, simpler implementation. Trie = the only practical choice for prefix search at scale.

</details>

> 📖 **Theory:** [Trie vs HashMap](./17_trie/theory.md#trie--the-tree-of-words)

---

### Q46 · [Normal] · `graph-representations`

> **Compare adjacency matrix vs adjacency list for representing a graph. When is each preferred? Give time/space complexity for: add edge, check edge, iterate neighbours.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

| Operation | Adjacency Matrix | Adjacency List |
|-----------|-----------------|----------------|
| Add edge | O(1) | O(1) |
| Check edge (u, v) | O(1) | O(degree(u)) |
| Iterate neighbours of u | O(V) | O(degree(u)) |
| Space | O(V²) | O(V + E) |

**How to think through this:**
1. **Adjacency matrix**: a V×V grid. `matrix[u][v] = 1` if edge exists. Immediate edge lookup, but wastes O(V²) space even if the graph is sparse (few edges). Scanning neighbours always costs O(V) even if a node has only 2 neighbours.
2. **Adjacency list**: each node stores only its actual neighbours. Space scales with edges, not vertices squared. Ideal for sparse graphs (most real-world graphs). Edge lookup requires scanning the list.
3. **Choose matrix** when: dense graph (E ≈ V²), or edge-existence checks are the dominant operation.
4. **Choose list** when: sparse graph, or neighbour iteration (BFS/DFS) is the dominant operation.

**Key takeaway:** Adjacency list is the default for sparse graphs and traversal. Matrix shines for dense graphs or when O(1) edge lookup is critical.

</details>

> 📖 **Theory:** [Graph Representations](./18_graphs/theory.md#adjacency-list)

---

### Q47 · [Thinking] · `bfs-shortest-path`

> **Why does BFS find the shortest path in an unweighted graph but DFS does not? Trace BFS on a small graph to show the level-by-level expansion.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
BFS explores nodes in order of their distance from the source — it processes all nodes at distance d before any at distance d+1. The first time BFS reaches the target, it has taken the fewest hops. DFS may reach the target via a long winding path before exploring a shorter one.

**How to think through this:**
1. Consider: `A — B — D` and `A — C — E — D`. BFS from A:
   - Level 0: `{A}`
   - Level 1: `{B, C}` — A's neighbours
   - Level 2: `{D, E}` — B's and C's neighbours. D is reached here with distance 2.
2. DFS from A might go A → C → E → D (distance 3) first and record that as the answer, never reaching B → D (distance 2).
3. BFS's queue (FIFO) enforces the level-by-level guarantee. DFS's stack (LIFO) dives deep with no distance ordering.

**Complexity:** Time: O(V + E) · Space: O(V)

**Key takeaway:** BFS = distance ordering by construction. The queue ensures you never reach a node via a longer path before you've tried all shorter paths.

</details>

> 📖 **Theory:** [BFS Shortest Path](./18_graphs/theory.md#11-shortest-path-unweighted)

---

### Q48 · [Normal] · `dfs-connected-components`

> **How do you use DFS to count connected components in an undirected graph? Write the algorithm using a visited set.**

```python
def count_components(n, edges):
    graph = {i: [] for i in range(n)}
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)       # ← undirected: add both directions

    visited = set()
    count = 0

    def dfs(node):
        visited.add(node)
        for neighbour in graph[node]:
            if neighbour not in visited:
                dfs(neighbour)

    for node in range(n):
        if node not in visited:  # ← unvisited node = new component
            dfs(node)
            count += 1

    return count
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Iterate over all nodes. When you encounter an unvisited node, launch a DFS from it — this DFS will mark every node in its connected component as visited. Each DFS launch = one new component. Count the launches.

**How to think through this:**
1. A connected component is a maximal set of nodes reachable from each other. DFS from any node in a component reaches every node in that component.
2. After DFS completes, all nodes in that component are in `visited`. The next unvisited node must belong to a different component.
3. Each node and each edge is processed once → O(V + E).

**Complexity:** Time: O(V + E) · Space: O(V)

**Key takeaway:** Connected components = count DFS launches. Each launch floods one component; the visited set prevents double-counting.

</details>

> 📖 **Theory:** [Connected Components](./18_graphs/theory.md#10-connected-components)

---

### Q49 · [Thinking] · `graph-cycle-detection`

> **How do you detect a cycle in an undirected graph? How does the algorithm differ for a directed graph? What data structures are used?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The two cases differ fundamentally because "visiting a neighbour you came from" is not a cycle in an undirected graph but a back-edge in a directed graph means something different.

**How to think through this:**
1. **Undirected graph**: run DFS, tracking the parent of each node. If DFS visits a neighbour that is already in `visited` and is not the immediate parent, a cycle exists (a back edge to a non-parent). Use a `visited` set and pass the parent node through recursion.
2. **Directed graph**: the parent trick fails — a node can have multiple paths leading to it legitimately. Instead, maintain two sets: `visited` (ever seen) and `rec_stack` (currently in the DFS call stack). If DFS reaches a node already in `rec_stack`, there is a cycle (we've followed a path back to a node still being processed).
3. **Union-Find** is an alternative for undirected graphs: for each edge (u, v), if u and v are already in the same component, adding this edge creates a cycle.

**Key takeaway:** Undirected cycles = back edge to non-parent. Directed cycles = back edge to a node still on the recursion stack. Same DFS, different bookkeeping.

</details>

> 📖 **Theory:** [Cycle Detection](./18_graphs/theory.md#9-cycle-detection)

---

### Q50 · [Design] · `topological-sort`

> **What is topological sort? What type of graph does it apply to? Describe Kahn's algorithm (BFS-based) and when you'd use topological sort in practice.**

```python
from collections import deque

def topo_sort(n, prerequisites):
    graph = {i: [] for i in range(n)}
    in_degree = [0] * n
    for u, v in prerequisites:
        graph[v].append(u)          # ← v must come before u
        in_degree[u] += 1

    queue = deque([i for i in range(n) if in_degree[i] == 0])  # ← start with no dependencies
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbour in graph[node]:
            in_degree[neighbour] -= 1
            if in_degree[neighbour] == 0:   # ← all prerequisites met
                queue.append(neighbour)

    return order if len(order) == n else []  # ← empty = cycle detected
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Topological sort** produces a linear ordering of nodes in a **directed acyclic graph (DAG)** such that for every directed edge u → v, u appears before v in the ordering. It applies only to DAGs — a cycle makes a valid ordering impossible.

**Kahn's algorithm:**
1. Compute in-degree (number of incoming edges) for every node.
2. Enqueue all nodes with in-degree 0 (no dependencies).
3. Dequeue a node, add it to the result, and decrement the in-degree of all its neighbours. If a neighbour's in-degree reaches 0, enqueue it.
4. If the result contains all n nodes, the sort succeeded. If not, a cycle exists.

**Practical uses:** build systems (compile order), course prerequisites, task scheduling, package dependency resolution, Makefiles.

**How to think through this:**
1. Topological sort requires a DAG — if you find a cycle, the problem is unsolvable (circular dependency).
2. Kahn's algorithm is intuitive: anything with no incoming edges (no dependencies) can be scheduled first. Process it, remove it, and repeat.
3. If the final result contains fewer than n nodes, a cycle was detected — the remaining nodes form the cycle.

**Complexity:** Time: O(V + E) · Space: O(V + E)

**Key takeaway:** Topological sort = peel the DAG layer by layer, always processing what has no remaining dependencies. A cycle makes it impossible and Kahn's algorithm detects this via the final count check.

</details>

> 📖 **Theory:** [Topological Sort](./18_graphs/theory.md#topological-sort--ordering-dependencies)

---

## ⚡ Tier 3 — Advanced Algorithms

---

### Q51 · [Normal] · `dijkstra-algorithm`

> **Explain Dijkstra's algorithm. What data structure does the optimal implementation use? What is the time complexity and what type of graph does it require?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Dijkstra's algorithm finds the shortest path from a source node to all other nodes in a weighted graph. It greedily picks the unvisited node with the smallest known distance, relaxes its neighbors, and repeats. It requires **non-negative edge weights**.

**How to think through this:**
1. Start with distance 0 for the source, infinity for everything else.
2. Use a **min-heap** (priority queue) to always process the closest unvisited node next — this is the key greedy choice.
3. For each popped node, relax each neighbor: if `dist[u] + weight(u,v) < dist[v]`, update `dist[v]` and push it to the heap.
4. A node's shortest distance is finalized the first time it's popped (because all edge weights are non-negative).

**Complexity:** Time: O((V + E) log V) with a binary min-heap · Space: O(V + E)

**Key takeaway:** Dijkstra = BFS with a priority queue instead of a plain queue — the min-heap ensures you always settle the globally cheapest node next.

</details>

> 📖 **Theory:** [Dijkstra's Algorithm](./25_advanced_graphs/theory.md#the-problem-dijkstra-cant-solve)

---

### Q52 · [Thinking] · `union-find`

> **What is Union-Find (Disjoint Set Union)? How do path compression and union by rank make it nearly O(1) per operation? Where is it used?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Union-Find** is a data structure that tracks a collection of elements partitioned into disjoint sets. It supports two operations: `find(x)` — which root does x belong to — and `union(x, y)` — merge the sets containing x and y.

**How to think through this:**
1. Naively, each node points to a parent. `find` walks up to the root — this can be O(n) in a degenerate chain.
2. **Path compression**: during `find`, make every node on the path point directly to the root. Future finds on those nodes are O(1).
3. **Union by rank**: always attach the shorter tree under the taller one. Without this, repeated unions create a chain; with it, tree height stays O(log n).
4. Together, both optimizations give **amortized O(α(n))** per operation, where α is the inverse Ackermann function — effectively constant for any realistic input size.
5. Used in: Kruskal's MST, detecting cycles in undirected graphs, network connectivity, image segmentation.

**Complexity:** Time: O(α(n)) amortized per operation · Space: O(n)

**Key takeaway:** Path compression flattens the tree after the fact; union by rank prevents it from getting tall in the first place — together they make Union-Find nearly free.

</details>

> 📖 **Theory:** [Union-Find (DSU)](./24_disjoint_set_union/theory.md#disjoint-set-union-union-find--managing-connected-groups-efficiently)

---

### Q53 · [Interview] · `minimum-spanning-tree`

> **Compare Kruskal's vs Prim's algorithm for MST. When would you prefer each? What data structures do they use?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Both algorithms find a **Minimum Spanning Tree** — a subset of edges connecting all V nodes with minimum total weight and no cycles. They differ in how they grow the MST.

**How to think through this:**
1. **Kruskal's**: Sort all edges by weight, then greedily add the cheapest edge that doesn't form a cycle (checked via Union-Find). Builds MST edge-by-edge globally.
   - Data structures: sorted edge list + Union-Find.
   - Time: O(E log E).
   - Best when: graph is sparse (E is small relative to V²), or edges are already sorted.

2. **Prim's**: Start from any node, greedily add the cheapest edge connecting the current MST to a new node. Builds MST by expanding a frontier.
   - Data structures: min-heap (priority queue) + visited set.
   - Time: O((V + E) log V) with a binary heap.
   - Best when: graph is dense (E close to V²), or given as adjacency matrix.

3. Key difference: Kruskal's thinks in edges, Prim's thinks in vertices. Kruskal's works naturally on disconnected graphs (produces a minimum spanning forest).

**Key takeaway:** Kruskal's for sparse graphs and edge lists; Prim's for dense graphs and adjacency matrices — both produce the same MST weight.

</details>

> 📖 **Theory:** [Minimum Spanning Tree](./25_advanced_graphs/theory.md#3-minimum-spanning-tree-mst)

---

### Q54 · [Thinking] · `dp-overlapping-subproblems`

> **What are the two properties that make a problem solvable by dynamic programming? Explain with an example that has overlapping subproblems.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A problem is solvable by **dynamic programming** when it has: (1) **optimal substructure** — the optimal solution can be built from optimal solutions to subproblems, and (2) **overlapping subproblems** — the same subproblems are solved repeatedly in the naive recursive approach.

**How to think through this:**
1. **Optimal substructure**: the solution to a larger problem depends only on optimal solutions to smaller versions — not on which path you took to get there. Fibonacci, shortest paths, and knapsack all have this.
2. **Overlapping subproblems**: contrast with divide-and-conquer (merge sort), where subproblems are independent and never repeated. In Fibonacci, `fib(5)` calls `fib(4)` and `fib(3)`; `fib(4)` also calls `fib(3)` — `fib(3)` is computed twice (and exponentially more so for larger inputs).
3. The fix: store each subproblem result the first time it's computed (**memoization** or **tabulation**), turning exponential time into polynomial.
4. The recursion tree for `fib(6)` has 25 calls naively but only 6 unique subproblems — the overlap is the waste DP eliminates.

**Key takeaway:** DP is just "don't solve the same subproblem twice" — memoize the overlapping parts of an optimal-substructure recursion.

</details>

> 📖 **Theory:** [DP Fundamentals](./21_dynamic_programming/theory.md)

---

### Q55 · [Normal] · `dp-memoization-tabulation`

> **Compare memoization (top-down) vs tabulation (bottom-up) DP. Write both approaches for Fibonacci. What are the tradeoffs?**

```python
# Top-down: memoization
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_memo(n):
    if n <= 1:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)  # ← cached on return


# Bottom-up: tabulation
def fib_tab(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]             # ← fills table left to right
    return dp[n]


# Space-optimized tabulation: O(1)
def fib_opt(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Memoization** is top-down: write the natural recursion, cache results. **Tabulation** is bottom-up: fill a table iteratively from base cases up to the target.

**How to think through this:**
1. Memoization only computes subproblems that are actually needed — good when the subproblem space is large but most states are unreachable.
2. Tabulation computes all subproblems in a fixed order — no recursion overhead, no call stack risk, easier to space-optimize (roll the array).
3. Memoization can hit Python's recursion limit for large n; tabulation does not.
4. For Fibonacci, tabulation can be reduced to two variables (O(1) space) because each state only depends on the previous two.

**Complexity:** Time: O(n) for both · Space: O(n) memo/table, reducible to O(1) with rolling variables in tabulation

**Key takeaway:** Memoization is easier to write (just add a cache to recursion); tabulation is faster in practice and easier to space-optimize.

</details>

> 📖 **Theory:** [Memoization vs Tabulation](./21_dynamic_programming/theory.md#memoization-top-down)

---

### Q56 · [Design] · `dp-01-knapsack`

> **Explain the 0/1 knapsack problem. Write the DP recurrence relation and the time/space complexity. How can you optimise space from O(n·W) to O(W)?**

```python
def knapsack(weights, values, W):
    n = len(weights)
    # 1D dp array — space optimized
    dp = [0] * (W + 1)

    for i in range(n):
        for w in range(W, weights[i] - 1, -1):  # ← iterate right-to-left!
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])

    return dp[W]
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The **0/1 knapsack problem**: given n items each with a weight and value, and a knapsack of capacity W, maximize total value without exceeding W. Each item is either taken (1) or not (0) — no fractions.

**How to think through this:**
1. Recurrence: `dp[i][w] = max(dp[i-1][w], dp[i-1][w - weight[i]] + value[i])` — either skip item i (take previous row's answer) or include it (subtract its weight, add its value).
2. Base case: `dp[0][w] = 0` for all w (no items = no value).
3. The 2D table is O(n·W) space. But each row only depends on the previous row — so you can use a single 1D array.
4. Critical: iterate the capacity **right-to-left** when using 1D. This ensures you're reading from the "previous item" state, not the updated current-item state (which would allow re-using the same item, turning it into unbounded knapsack).

**Complexity:** Time: O(n·W) · Space: O(W) with the 1D optimization

**Key takeaway:** The right-to-left sweep in the 1D optimization is the subtle trick — it prevents the current item from being counted twice.

</details>

> 📖 **Theory:** [0/1 Knapsack](./21_dynamic_programming/theory.md#01-knapsack)

---

### Q57 · [Normal] · `dp-lcs`

> **What is the Longest Common Subsequence problem? Write the recurrence relation and trace the DP table for "ABCD" and "ACDF".**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Longest Common Subsequence (LCS)**: given two strings, find the length of the longest subsequence present in both (characters don't need to be contiguous, but must be in order).

**How to think through this:**
1. Recurrence:
   - If `s1[i] == s2[j]`: `dp[i][j] = dp[i-1][j-1] + 1` — characters match, extend the LCS.
   - Else: `dp[i][j] = max(dp[i-1][j], dp[i][j-1])` — skip one character from either string.
2. DP table for "ABCD" (rows) vs "ACDF" (cols), 1-indexed:

```
    ""  A  C  D  F
""   0  0  0  0  0
A    0  1  1  1  1
B    0  1  1  1  1
C    0  1  2  2  2
D    0  1  2  3  3
```

3. Answer: `dp[4][4] = 3`. The LCS is "ACD".

**Complexity:** Time: O(m·n) · Space: O(m·n), reducible to O(min(m,n)) with row rolling

**Key takeaway:** When characters match, you extend a diagonal; when they don't, you inherit the better of "skip left" or "skip above."

</details>

> 📖 **Theory:** [LCS](./21_dynamic_programming/theory.md#longest-common-subsequence-lcs)

---

### Q58 · [Thinking] · `dp-lis`

> **What is the Longest Increasing Subsequence problem? What is the O(n²) DP solution? What change makes it O(n log n)?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Longest Increasing Subsequence (LIS)**: given an array, find the length of the longest subsequence where each element is strictly greater than the previous.

**How to think through this:**
1. O(n²) DP: `dp[i]` = length of LIS ending at index i. For each i, scan all j < i: if `arr[j] < arr[i]`, then `dp[i] = max(dp[i], dp[j] + 1)`. Answer is `max(dp)`.
2. This is O(n²) because for each element you scan all prior elements.
3. O(n log n) using **patience sorting** / binary search: maintain a `tails` array where `tails[i]` is the smallest tail element of all increasing subsequences of length i+1. For each new element, binary search for the first tail >= it and replace it (or append if larger than all tails).
4. The `tails` array stays sorted, enabling binary search. Its length at the end is the LIS length. (Note: `tails` itself is not the actual LIS — you need backtracking to reconstruct it.)

**Complexity:** O(n²) DP: Time O(n²) · Space O(n). Binary search: Time O(n log n) · Space O(n)

**Key takeaway:** The O(n log n) trick is maintaining a sorted "active tails" array — binary search replaces the inner O(n) scan with O(log n).

</details>

> 📖 **Theory:** [LIS](./21_dynamic_programming/theory.md#longest-increasing-subsequence-lis)

---

### Q59 · [Logical] · `dp-coin-change`

> **Trace the DP table for the coin change problem: coins=[1,3,4], amount=6. What is the minimum number of coins? Show the table fill order.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The minimum number of coins to make amount 6 is **2** (coins 3+3).

**How to think through this:**
1. Recurrence: `dp[a] = min(dp[a - c] + 1)` for each coin c where `c <= a`. Base: `dp[0] = 0`, all others = infinity.
2. Fill left to right, amount 0 to 6:

```
Amount:  0   1   2   3   4   5   6
dp:      0   1   2   1   1   2   2
```

3. Step-by-step:
   - `dp[1]`: coin 1 → `dp[0]+1 = 1`
   - `dp[2]`: coin 1 → `dp[1]+1 = 2`
   - `dp[3]`: coin 1 → `dp[2]+1 = 3`; coin 3 → `dp[0]+1 = 1` ← min = 1
   - `dp[4]`: coin 1 → `dp[3]+1 = 2`; coin 3 → `dp[1]+1 = 2`; coin 4 → `dp[0]+1 = 1` ← min = 1
   - `dp[5]`: coin 1 → 2; coin 3 → `dp[2]+1 = 3`; coin 4 → `dp[1]+1 = 2` ← min = 2
   - `dp[6]`: coin 1 → 3; coin 3 → `dp[3]+1 = 2`; coin 4 → `dp[2]+1 = 3` ← min = 2

**Complexity:** Time: O(amount × coins) · Space: O(amount)

**Key takeaway:** Coin change is unbounded knapsack — iterate amounts left-to-right and try every coin at each position; the left-to-right direction allows reuse of coins.

</details>

> 📖 **Theory:** [Coin Change](./21_dynamic_programming/theory.md#coin-change)

---

### Q60 · [Normal] · `backtracking-subsets`

> **How does backtracking generate all subsets of [1,2,3]? Draw the recursion tree. What is the time complexity?**

```python
def subsets(nums):
    result = []

    def backtrack(start, current):
        result.append(current[:])          # ← record every node in the tree
        for i in range(start, len(nums)):
            current.append(nums[i])
            backtrack(i + 1, current)      # ← move forward, never back
            current.pop()                  # ← undo choice

    backtrack(0, [])
    return result
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Backtracking generates all subsets by treating each element as a binary choice (include or skip), building candidates incrementally and recording every state — not just leaves.

**How to think through this:**
1. At each call, record the current path as a subset (so every node is a valid answer, unlike permutations where only leaves are valid).
2. Recursion tree for [1,2,3]:
```
[]
├── [1]
│   ├── [1,2]
│   │   └── [1,2,3]
│   └── [1,3]
├── [2]
│   └── [2,3]
└── [3]
```
3. The `start` parameter ensures each element is only considered once and in forward order — this prevents duplicates like [1,2] and [2,1] being counted separately.
4. Total subsets = 2^n (each element is either in or out).

**Complexity:** Time: O(2^n · n) — 2^n subsets, each copied in O(n) · Space: O(n) call stack depth

**Key takeaway:** Subsets = record every node; permutations = record only leaves. The `start` index is what prevents re-picking used elements.

</details>

> 📖 **Theory:** [Subsets](./20_backtracking/theory.md#backtracking--the-art-of-trying-undoing-and-trying-again)

---

### Q61 · [Thinking] · `backtracking-permutations`

> **How does backtracking generate all permutations of [1,2,3]? How does it differ from subsets? What is the time complexity?**

```python
def permutations(nums):
    result = []

    def backtrack(current, remaining):
        if not remaining:
            result.append(current[:])      # ← only record at leaves
            return
        for i in range(len(remaining)):
            current.append(remaining[i])
            backtrack(current, remaining[:i] + remaining[i+1:])  # ← remove used
            current.pop()

    backtrack([], nums)
    return result
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Permutations backtracking picks any unused element at each level (all positions matter, order matters), recording only the complete arrangements at the leaves.

**How to think through this:**
1. Key difference from subsets: in subsets you advance the `start` index (preserving order, no reuse); in permutations, at each level you can pick any remaining unused element — order is what makes [1,2] and [2,1] distinct outputs.
2. Recursion tree for [1,2,3] has 3 choices at depth 0, 2 at depth 1, 1 at depth 2 → 3! = 6 leaf nodes.
3. You must track which elements are "used" — either via a visited boolean array (in-place swap variant) or by passing the remaining pool.
4. The in-place swap approach avoids allocating a new remaining list: swap `nums[start]` with `nums[i]`, recurse with `start+1`, swap back.

**Complexity:** Time: O(n! · n) — n! permutations, each takes O(n) to copy · Space: O(n) call stack

**Key takeaway:** Subsets fix the pick order (only go forward); permutations allow any unused element at each step — that's what produces all orderings.

</details>

> 📖 **Theory:** [Permutations](./20_backtracking/theory.md#backtracking--the-art-of-trying-undoing-and-trying-again)

---

### Q62 · [Design] · `backtracking-n-queens`

> **Explain the N-Queens problem and the backtracking approach. What constraint check allows early pruning? How does pruning reduce work?**

```python
def solve_n_queens(n):
    result = []
    cols = set()
    diag1 = set()   # ← row - col (top-left to bottom-right)
    diag2 = set()   # ← row + col (top-right to bottom-left)

    def backtrack(row, board):
        if row == n:
            result.append(["".join(r) for r in board])
            return
        for col in range(n):
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue                  # ← prune: this cell is attacked
            cols.add(col)
            diag1.add(row - col)
            diag2.add(row + col)
            board[row][col] = 'Q'
            backtrack(row + 1, board)
            cols.remove(col)
            diag1.remove(row - col)
            diag2.remove(row + col)
            board[row][col] = '.'

    board = [['.' ] * n for _ in range(n)]
    backtrack(0, board)
    return result
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**N-Queens**: place N queens on an N×N chessboard so no two queens attack each other (no shared row, column, or diagonal). Backtracking places one queen per row and prunes columns where placement is invalid.

**How to think through this:**
1. By placing exactly one queen per row (iterate rows top-to-bottom), the row constraint is automatically satisfied. Only column and diagonal conflicts need checking.
2. Constraint check: a cell (row, col) is attacked if `col` appears in a used column set, or `row - col` (diagonal) or `row + col` (anti-diagonal) is already claimed. These are O(1) set lookups.
3. Pruning power: if column 0 at row 2 is attacked, the entire subtree of all arrangements built on that placement is skipped — potentially millions of states for large n.
4. Without pruning, the search space is n^n. With pruning, valid solutions for n=8 require visiting ~15,000 nodes vs 16 million brute-force.

**Complexity:** Time: O(n!) in the worst case, much better in practice · Space: O(n) for the tracking sets

**Key takeaway:** The three sets (cols, diag1, diag2) let you check any cell's validity in O(1) — making pruning cheap and the search fast.

</details>

> 📖 **Theory:** [N-Queens](./20_backtracking/theory.md#n-queens)

---

### Q63 · [Interview] · `backtracking-pruning`

> **What is constraint pruning in backtracking? Give two concrete examples where a pruning condition eliminates a large subtree early.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Constraint pruning** is the practice of checking validity conditions before recursing deeper, abandoning entire subtrees the moment a partial solution cannot possibly lead to a valid complete solution.

**How to think through this:**
1. Without pruning, backtracking is essentially brute-force — every combination is explored. Pruning is what makes it tractable.
2. Example 1 — **Sudoku**: before placing a digit in a cell, check if it already appears in the same row, column, or 3×3 box. If it does, skip this digit entirely. A single conflict at depth 3 eliminates all 9^(81-3) arrangements that extend from it.
3. Example 2 — **Combination sum** (find subsets summing to target): sort the candidates first. When the current running sum plus the next candidate already exceeds the target, break out of the loop entirely — all larger candidates will also exceed it. This prunes all right subtrees in one comparison.
4. The key insight: pruning works best when it fires early (near the root) and when the pruning condition is cheap to evaluate (O(1) or O(k) for depth k).

**Key takeaway:** A prune at depth d eliminates O(branching_factor^(max_depth - d)) nodes — the earlier and more aggressively you prune, the closer backtracking gets to optimal search.

</details>

> 📖 **Theory:** [Pruning](./20_backtracking/theory.md#7-pruning-very-important)

---

### Q64 · [Normal] · `bit-manipulation-basics`

> **What do these bit operations produce? AND, OR, XOR, left shift, right shift. Give one practical use case for each.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The five fundamental **bit operations** on integers, with examples using `a=5` (101) and `b=3` (011):

**How to think through this:**
1. **AND** (`a & b = 001 = 1`): bit is 1 only if both bits are 1. Use case: check if a number is even — `n & 1 == 0` means even (last bit is 0).
2. **OR** (`a | b = 111 = 7`): bit is 1 if either bit is 1. Use case: set a specific bit — `n | (1 << k)` sets bit k regardless of its current value.
3. **XOR** (`a ^ b = 110 = 6`): bit is 1 if bits differ. Use case: find the single non-duplicate in an array — XOR of all elements cancels pairs, leaving the lone value.
4. **Left shift** (`a << 1 = 1010 = 10`): multiply by 2 per shift. Use case: fast power-of-2 multiplication — `n << 3 = n * 8`.
5. **Right shift** (`a >> 1 = 010 = 2`): divide by 2 per shift (integer). Use case: extract individual bits — `(n >> k) & 1` reads bit k.

**Key takeaway:** AND masks/checks, OR sets, XOR toggles/finds differences, shifts multiply/divide by powers of 2 — all in O(1).

</details>

> 📖 **Theory:** [Bit Operations](./22_bit_manipulation/theory.md#3-bitwise-operators)

---

### Q65 · [Logical] · `xor-single-number`

> **Given array [4,1,2,1,2], use XOR to find the single non-duplicate number. Trace each XOR step and explain why this works.**

```python
def single_number(nums):
    result = 0
    for n in nums:
        result ^= n    # ← each pair cancels to 0; lone value survives
    return result
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The single non-duplicate number is **4**.

**How to think through this:**
1. XOR has two critical properties: `x ^ x = 0` (a number XORed with itself is 0) and `x ^ 0 = x` (XOR with 0 is identity). Also XOR is commutative and associative.
2. Trace through [4, 1, 2, 1, 2]:
   - `result = 0`
   - `0 ^ 4 = 4`
   - `4 ^ 1 = 5`
   - `5 ^ 2 = 7`
   - `7 ^ 1 = 6`  ← the second 1 cancels the first
   - `6 ^ 2 = 4`  ← the second 2 cancels the first
3. Because XOR is commutative, it doesn't matter what order elements appear — you can think of it as `4 ^ (1^1) ^ (2^2) = 4 ^ 0 ^ 0 = 4`.
4. Every duplicate pair XORs to 0; only the unpaired element remains.

**Complexity:** Time: O(n) · Space: O(1)

**Key takeaway:** XOR is a self-canceling operation — duplicates annihilate each other, leaving only the element with no pair.

</details>

> 📖 **Theory:** [XOR Trick](./22_bit_manipulation/theory.md#xor)

---

### Q66 · [Thinking] · `count-set-bits`

> **Explain Brian Kernighan's algorithm for counting set bits in an integer. Why does `n & (n-1)` clear the lowest set bit? What is the time complexity?**

```python
def count_set_bits(n):
    count = 0
    while n:
        n = n & (n - 1)   # ← drops the lowest set bit each iteration
        count += 1
    return count
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Brian Kernighan's algorithm** counts set bits by repeatedly clearing the lowest set bit until the number becomes 0. Each loop iteration removes exactly one set bit, so the loop runs exactly as many times as there are set bits.

**How to think through this:**
1. Why does `n & (n-1)` clear the lowest set bit? Subtracting 1 from n flips the lowest set bit to 0 and sets all lower bits to 1. For example, `n=12` (1100), `n-1=11` (1011). AND-ing them: `1100 & 1011 = 1000` — the lowest set bit (bit 2) is cleared.
2. This works because borrowing in binary propagates through all trailing zeros and flips exactly the lowest set bit.
3. Trace for n=13 (1101):
   - `1101 & 1100 = 1100` (count=1, cleared bit 0)
   - `1100 & 1011 = 1000` (count=2, cleared bit 2)
   - `1000 & 0111 = 0000` (count=3, cleared bit 3)
4. Compare to naive approach: checking each of 32 bits is always O(32). Kernighan's is O(k) where k = number of set bits — faster when k is small.

**Complexity:** Time: O(k) where k is the number of set bits · Space: O(1)

**Key takeaway:** `n & (n-1)` is the canonical trick to "pop" the lowest set bit — it appears in Kernighan's, power-of-two checks, and many other bit problems.

</details>

> 📖 **Theory:** [Count Set Bits](./22_bit_manipulation/theory.md#count-set-bits)

---

### Q67 · [Thinking] · `segment-tree-range-query`

> **What is a segment tree? What problems does it solve that a prefix sum array can't? What is the time complexity of build, query, and update?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **segment tree** is a binary tree where each node stores an aggregate (sum, min, max) over a contiguous subarray. The root covers the full array; leaves cover single elements.

**How to think through this:**
1. Prefix sums answer range sum queries in O(1) — but updating a value requires rebuilding the entire prefix array in O(n). They're read-optimized, write-expensive.
2. A segment tree handles both queries and point updates in O(log n). This is the key tradeoff: slightly slower queries but fast updates.
3. Problems prefix sums can't handle efficiently: range minimum/maximum queries (not just sum), and any scenario with frequent updates — e.g., "after these 10,000 updates, answer 10,000 range queries."
4. Tree structure for array [1, 3, 5, 7, 9, 11] (n=6): internal nodes store range aggregates. Querying [2,5] means combining O(log n) precomputed segments rather than re-scanning.
5. Build: O(n) — you fill 2n nodes bottom-up. Query: O(log n) — traverse at most 4 nodes per level. Update: O(log n) — update leaf and propagate up.

**Complexity:** Build: O(n) · Query: O(log n) · Update: O(log n) · Space: O(n)

**Key takeaway:** Segment trees are the go-to when you need both fast range queries and fast point updates — prefix sums are only faster when updates are rare.

</details>

> 📖 **Theory:** [Segment Tree](./23_segment_tree/theory.md#segment-tree--the-power-of-efficient-range-queries)

---

### Q68 · [Normal] · `fenwick-tree`

> **What is a Binary Indexed Tree (Fenwick Tree)? How does it differ from a segment tree in implementation and use cases? What is its time complexity?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **Fenwick Tree** (Binary Indexed Tree, BIT) is a flat array where each index stores a partial sum covering a range determined by the lowest set bit of that index. It supports prefix sum queries and point updates in O(log n) with a much simpler implementation than a segment tree.

**How to think through this:**
1. Implementation: a single array of size n+1. To update index i, add the delta to `tree[i]`, then jump to `i + (i & -i)` (add lowest set bit) and repeat. To query prefix sum up to i, sum `tree[i]`, then jump to `i - (i & -i)` and repeat until i=0.
2. The expression `i & -i` isolates the lowest set bit — this is the key operation that makes both traversals O(log n).
3. Fenwick tree vs segment tree:
   - Fenwick: simpler (5-10 lines), lower constant factor, only handles prefix queries natively (range queries = two prefix calls). Cannot do range min/max.
   - Segment tree: more complex, handles arbitrary range aggregates (min, max, GCD), supports lazy propagation for range updates.
4. Use Fenwick when you only need prefix sums/frequencies and want minimal code. Use segment tree for more complex aggregates or range updates.

**Complexity:** Build: O(n log n) or O(n) · Query: O(log n) · Update: O(log n) · Space: O(n)

**Key takeaway:** Fenwick tree is segment tree's leaner sibling — half the code, same O(log n) complexity, but limited to problems expressible as prefix aggregates.

</details>

> 📖 **Theory:** [Fenwick Tree](./23_segment_tree/theory.md#fenwick-tree-binary-indexed-tree--simpler-range-queries)

---

### Q69 · [Logical] · `monotonic-stack-nge`

> **Trace the monotonic stack algorithm on [2,1,5,6,2,3] to find the "next greater element" for each position. Show the stack state at each step.**

```python
def next_greater_element(nums):
    n = len(nums)
    result = [-1] * n
    stack = []  # stores indices

    for i in range(n):
        while stack and nums[stack[-1]] < nums[i]:  # ← current is greater
            idx = stack.pop()
            result[idx] = nums[i]                   # ← found NGE for idx
        stack.append(i)

    return result
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Result: `[5, 5, 6, -1, 3, -1]`

**How to think through this:**
1. The stack stores indices of elements waiting to find their next greater element (NGE). It stays **monotonically decreasing** in value — when a larger element arrives, it resolves pending smaller ones.
2. Trace (showing stack as values for clarity):

| i | nums[i] | Action | Stack (values) | result |
|---|---------|--------|----------------|--------|
| 0 | 2 | push | [2] | [-1,-1,-1,-1,-1,-1] |
| 1 | 1 | push (1<2) | [2,1] | [-1,-1,-1,-1,-1,-1] |
| 2 | 5 | pop 1→NGE=5, pop 2→NGE=5, push 5 | [5] | [5,5,-1,-1,-1,-1] |
| 3 | 6 | pop 5→NGE=6, push 6 | [6] | [5,5,6,-1,-1,-1] |
| 4 | 2 | push (2<6) | [6,2] | [5,5,6,-1,-1,-1] |
| 5 | 3 | pop 2→NGE=3, push 3 | [6,3] | [5,5,6,-1,3,-1] |

3. Remaining in stack [6,3] → indices 3 and 5 → NGE stays -1.

**Complexity:** Time: O(n) — each element is pushed and popped at most once · Space: O(n)

**Key takeaway:** A monotonic stack solves NGE in O(n) by deferring resolution — elements wait in the stack until a larger element arrives to "settle" them.

</details>

> 📖 **Theory:** [Monotonic Stack NGE](./08_stack/theory.md#pattern-1-next-greater-element)

---

### Q70 · [Thinking] · `sliding-window-deque`

> **How do you find the maximum in every window of size k in an array using a deque in O(n) time? Why can't you use a regular queue?**

```python
from collections import deque

def max_sliding_window(nums, k):
    dq = deque()   # ← stores indices; front is always the window maximum
    result = []

    for i in range(len(nums)):
        # remove indices outside window
        if dq and dq[0] < i - k + 1:
            dq.popleft()

        # remove smaller elements from back — they can never be the max
        while dq and nums[dq[-1]] < nums[i]:
            dq.pop()                       # ← maintain decreasing order

        dq.append(i)

        if i >= k - 1:
            result.append(nums[dq[0]])     # ← front is max of current window

    return result
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Use a **monotonic deque** that stores indices in decreasing order of their values. The front always holds the index of the current window's maximum.

**How to think through this:**
1. Why not a regular queue? A queue preserves insertion order but knows nothing about element values — to find the max of each window you'd scan all k elements per window: O(n·k).
2. The deque maintains a **decreasing monotonic order**: before pushing index i, pop all indices from the back whose values are less than `nums[i]`. Those smaller elements can never be a future window's maximum (they're both smaller AND older than i).
3. When the window slides forward, check if the front index is now out of bounds (`< i - k + 1`) and pop it.
4. The front of the deque at each step is the maximum of the current window.
5. Each index is added and removed at most once → O(n) total work.

**Complexity:** Time: O(n) · Space: O(k) for the deque

**Key takeaway:** The deque's monotonic invariant means useless elements (smaller AND older) are discarded immediately — you pay O(1) amortized per element, not O(k).

</details>

> 📖 **Theory:** [Sliding Window Maximum](./12_sliding_window/theory.md#sliding-window--the-magic-moving-frame)

---

### Q71 · [Thinking] · `kmp-string-matching`

> **What problem does the KMP algorithm solve with string matching? What is the "failure function" (partial match table) and how does it avoid redundant comparisons?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**KMP (Knuth-Morris-Pratt)** finds all occurrences of a pattern P in a text T in O(n + m) time, compared to O(n·m) for naive search. It avoids re-scanning text characters by using information about the pattern itself.

**How to think through this:**
1. Naive matching: when a mismatch occurs at position j in the pattern, reset j to 0 and advance i by 1 in the text — throwing away all match progress.
2. KMP's insight: when a mismatch occurs, some prefix of the pattern may match a suffix of what was already matched. We can skip ahead instead of restarting from zero.
3. The **failure function** `lps[i]` (longest proper prefix which is also a suffix) for the pattern encodes this: `lps[i]` = length of the longest prefix of `P[0..i]` that is also a suffix. Built in O(m).
4. Example: pattern "ABABC" → lps = [0, 0, 1, 2, 0]. If mismatch at index 4 (C), fall back to index `lps[3]=2` (AB already matched), not index 0.
5. During search: mismatch at pattern index j → set `j = lps[j-1]` (not j=0). Text pointer i never moves backward → O(n) search.

**Complexity:** Build lps: O(m) · Search: O(n) · Total: O(n + m) · Space: O(m)

**Key takeaway:** The failure function pre-computes how far to "rewind" the pattern on a mismatch — text characters are never revisited, making KMP linear.

</details>

> 📖 **Theory:** [KMP Algorithm](./03_strings/theory.md)

---

### Q72 · [Normal] · `rabin-karp-hash`

> **Explain the Rabin-Karp rolling hash approach to string search. What is a hash collision in this context and how is it handled?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Rabin-Karp** uses hashing to find a pattern in a text. It computes a hash of the pattern and slides a same-length window across the text, recomputing the window's hash efficiently via a **rolling hash** — only O(1) per slide.

**How to think through this:**
1. Naive hashing: computing a new hash for each window takes O(m) → total O(n·m), no better than brute force.
2. Rolling hash: treat the string as a base-d number modulo a prime p. When the window slides one position: `hash = (hash * d - outgoing_char * d^m + incoming_char) % p`. This is O(1) per slide.
3. When the window hash equals the pattern hash, do a **character-by-character verification** (O(m)). This handles **hash collisions** — two different strings that hash to the same value. The verification step ensures no false positives.
4. In the average case with a good hash, collisions are rare and verification seldom fires, giving O(n + m) expected time.
5. Rabin-Karp's real strength over KMP: it naturally extends to **multi-pattern search** — hash all patterns, check each window against a hash set.

**Complexity:** Average: O(n + m) · Worst case (many collisions): O(n·m) · Space: O(1)

**Key takeaway:** Rolling hash = O(1) per window slide; always verify on hash match because collisions can occur — the hash is a fast filter, not a proof.

</details>

> 📖 **Theory:** [Rabin-Karp](./03_strings/theory.md)

---

### Q73 · [Design] · `lru-cache-design`

> **Design an LRU cache with O(1) get and O(1) put. What data structures do you combine? Write the core implementation.**

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.cache = OrderedDict()      # ← maintains insertion/access order

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)    # ← mark as most recently used
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.cap:
            self.cache.popitem(last=False)  # ← evict least recently used (front)
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
An **LRU (Least Recently Used) cache** evicts the least recently accessed item when capacity is exceeded. The canonical implementation combines a **hash map** (O(1) key lookup) with a **doubly linked list** (O(1) move-to-front and remove-tail).

**How to think through this:**
1. Hash map alone: O(1) get/put but no way to track recency ordering without O(n) scan.
2. Linked list alone: O(1) reordering but O(n) lookup by key.
3. Combined: the hash map stores `key → node pointer`, the doubly linked list maintains LRU order (most recent at tail, least recent at head). Every get/put moves the node to the tail in O(1) using the pointer.
4. On capacity overflow, evict the head node — it's guaranteed to be the least recently used.
5. Python's `OrderedDict` wraps this pattern: `move_to_end` is O(1) and `popitem(last=False)` removes the front in O(1), making the implementation above correct and concise.

**Complexity:** get: O(1) · put: O(1) · Space: O(capacity)

**Key takeaway:** LRU cache = hash map for O(1) lookup + doubly linked list for O(1) recency reordering — neither structure alone is sufficient.

</details>

> 📖 **Theory:** [LRU Cache](./10_hashing/theory.md)

---

### Q74 · [Thinking] · `hashmap-from-scratch`

> **How would you implement a hash map from scratch? Cover: hash function, array of buckets, collision resolution (chaining), and dynamic resizing trigger.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **hash map** maps keys to values in O(1) average time by converting keys to array indices via a hash function, with collision resolution to handle index conflicts.

**How to think through this:**
1. **Hash function**: converts a key to a bucket index. `index = hash(key) % num_buckets`. A good hash function distributes keys uniformly. Python's built-in `hash()` works; for strings, polynomial rolling hash is common.
2. **Array of buckets**: an array of size m, where each slot holds a list (for chaining) or is empty.
3. **Collision resolution — chaining**: when two keys hash to the same index, store them both in a linked list (or Python list) at that bucket. Get/put scan the chain for the matching key. Average chain length = n/m (load factor).
4. **Dynamic resizing**: when load factor `n/m > threshold` (typically 0.75), allocate a new array of size 2m and **rehash** all existing keys. This keeps chains short and O(1) average access. Without resizing, a full table degrades to O(n) per operation.
5. Worst case: all keys collide into one bucket → O(n). Good hash functions make this astronomically unlikely.

**Complexity:** Average: O(1) get/put · Worst: O(n) · Resize: O(n) amortized O(1) per insertion · Space: O(n)

**Key takeaway:** A hash map is an array + a hash function + collision handling — resizing when the load factor exceeds ~0.75 is what keeps the "average O(1)" guarantee valid.

</details>

> 📖 **Theory:** [HashMap Implementation](./10_hashing/theory.md#hashing--the-power-of-instant-lookup)

---

### Q75 · [Critical] · `reservoir-sampling`

> **You have a stream of unknown length n. How do you select k items uniformly at random without knowing n in advance? Explain the reservoir sampling algorithm.**

```python
import random

def reservoir_sample(stream, k):
    reservoir = []

    for i, item in enumerate(stream):
        if i < k:
            reservoir.append(item)        # ← fill reservoir with first k items
        else:
            j = random.randint(0, i)      # ← random index in [0, i]
            if j < k:
                reservoir[j] = item       # ← replace with probability k/(i+1)

    return reservoir
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Reservoir sampling** selects k items from a stream of unknown length n such that each item has exactly `k/n` probability of being in the final sample — without ever knowing n.

**How to think through this:**
1. First k items: add all to the reservoir unconditionally. Each has probability 1 of being selected so far.
2. For item i (0-indexed, i >= k): generate a random integer j in [0, i]. If j < k, replace `reservoir[j]` with item i. The probability of replacement is `k / (i+1)`.
3. Proof of uniform probability: by induction. After seeing i+1 items, each item should be in the reservoir with probability `k/(i+1)`. Item i enters with probability `k/(i+1)`. An existing reservoir item survives if it is not the one replaced: probability = `1 - (k/(i+1)) * (1/k) = 1 - 1/(i+1) = i/(i+1)`. Combined with its prior probability of `k/i`, survival probability = `(k/i) * (i/(i+1)) = k/(i+1)`. Correct.
4. The critical edge case: what if the stream has fewer than k items? The reservoir contains all of them — which is the only valid "uniform sample" of a population smaller than k.
5. This is essential for: sampling from database cursors, log streams, or any iterator you can't rewind or count cheaply.

**Complexity:** Time: O(n) — one pass through the stream · Space: O(k) for the reservoir

**Key takeaway:** Each new item "bids" to enter the reservoir with probability k/(i+1) and evicts a random existing item if it wins — this simple rule guarantees uniform sampling without ever knowing n.

</details>

> 📖 **Theory:** [Reservoir Sampling](./02_arrays/theory.md)

## 🏋️ Tier 4 — Interview / Scenario

---

### Q76 · [Interview] · `explain-time-complexity`

> **A junior developer asks "why do we care about time complexity if modern computers are fast?" Give a concrete, convincing explanation using real numbers.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Speed matters at scale. A modern CPU can execute roughly 10^9 simple operations per second. An O(n²) algorithm on 1M records performs 10^12 operations — that's 1000 seconds, not milliseconds. No hardware upgrade fixes bad algorithmic choices at scale.

**How to think through this:**
1. Anchor with a concrete comparison: O(n log n) vs O(n²) on n = 1,000,000.
   - O(n log n): ~20,000,000 ops → ~0.02 seconds
   - O(n²): ~1,000,000,000,000 ops → ~1000 seconds
2. Hardware scaling is linear — doubling CPU speed halves time. But going from O(n²) to O(n log n) is a 50,000x improvement on that input.
3. Real-world anchor: if a database query scans 100M rows with a nested loop, no cluster on Earth can answer in under a second. The O(n²) algorithm gets 4x slower when data doubles — not 2x.

**Key takeaway:** Hardware scales linearly; bad complexity scales exponentially — at production scale, the algorithm always wins.

</details>

> 📖 **Theory:** [Complexity Analysis](./01_complexity_analysis/theory.md#time-complexity--the-speed-meter)

---

### Q77 · [Interview] · `explain-recursion-analogy`

> **Explain recursion to someone who has never seen it. Use a non-programming analogy, then show how it maps to code with a simple example.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Recursion is a function that solves a problem by solving a smaller version of the same problem, until it hits a case so small it can answer directly.

**How to think through this:**
1. **Analogy — Russian nesting dolls:** Open a doll, find a smaller doll. To find the smallest doll, you open each one and ask "are you the smallest?" You don't need to know how many dolls there are — you just keep asking until one says yes. That stopping point is the **base case**.
2. **Map to code — countdown:**

```python
def countdown(n):
    if n == 0:        # ← base case: stop here
        return
    print(n)
    countdown(n - 1)  # ← recursive call: same problem, smaller input
```

3. Every recursive function needs a **base case** (where it stops) and a **recursive case** (where it calls itself with a smaller input). Without the base case, it runs forever.

**Key takeaway:** Recursion trusts that if you can solve a smaller version of your problem, you can solve the whole thing — you just need to define when "small enough" means "just answer it directly."

</details>

> 📖 **Theory:** [Recursion](./04_recursion/theory.md#recursion-in-python--complete-theory-zero-to-advanced)

---

### Q78 · [Interview] · `dfs-vs-bfs-when`

> **In an interview you're asked: "when would you use DFS vs BFS?" Give a structured answer with at least 3 concrete scenarios for each.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The choice depends on what you're optimizing for — shortest path, full exploration, or memory.

**How to think through this:**

**Use BFS when:**
1. **Shortest path in an unweighted graph** — BFS visits nodes level by level; the first time it reaches the target is via the fewest edges.
2. **Social network degrees of separation** — finding all friends within 2 hops. BFS groups nodes by distance from source.
3. **Level-order tree traversal** — printing a tree row by row (org chart by hierarchy level).
4. **Web crawlers with depth limits** — crawl all pages 1 link away before going deeper.

**Use DFS when:**
1. **Cycle detection** — DFS tracks the current path via recursion stack, making it natural to detect back edges.
2. **Topological sort** — processing dependencies (build systems, package managers). DFS post-order gives a valid topological order.
3. **Maze solving / exhaustive path search** — explore one full path before backtracking.
4. **Memory-constrained scenarios** — DFS uses O(depth) memory vs BFS's O(width). For very wide graphs, BFS queue explodes.

**The key contrast:** BFS guarantees shortest path but burns memory on wide graphs. DFS is memory-efficient and natural for backtracking but may find a long path first.

**Key takeaway:** Default to BFS for shortest-path problems, DFS for structural analysis (cycles, topological order, exhaustive search).

</details>

> 📖 **Theory:** [DFS vs BFS](./18_graphs/theory.md#8-when-to-use-bfs-vs-dfs)

---

### Q79 · [Interview] · `explain-dynamic-programming`

> **Explain dynamic programming in simple terms. What is the difference between DP and brute force? Use a real problem to illustrate.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Dynamic programming (DP)** is brute force with memory. It solves a problem by breaking it into overlapping subproblems, solving each exactly once, and storing results so they're never recomputed.

**How to think through this:**
1. **The analogy:** Calculating the 10th Fibonacci number by brute force recursion recalculates fib(8) and fib(7) separately — but fib(8) itself recalculates fib(7) again. DP says: write the answer on a sticky note the first time, look it up after that.
2. **Brute force vs DP on Fibonacci:**
   - Brute force: O(2^n) time — exponential, recalculates everything
   - DP with memo: O(n) time, O(n) space — solve once, reuse always
3. **The two conditions for DP to apply:**
   - **Overlapping subproblems** — the same smaller problems repeat
   - **Optimal substructure** — the optimal big-problem answer is built from optimal subproblem answers
4. **Real example — Coin Change:** How many coins to make $11 with coins [1,5,6]? DP builds a table: `dp[i]` = minimum coins to make amount `i`. O(amount × coins) instead of exponential.

**Key takeaway:** DP is the realization that brute force wastes time solving the same subproblem repeatedly — memoize the results and brute force becomes polynomial.

</details>

> 📖 **Theory:** [Dynamic Programming](./21_dynamic_programming/theory.md#dynamic-programming--the-art-of-remembering-smartly)

---

### Q80 · [Interview] · `hash-collision-resolution`

> **Explain hash collisions to a junior dev. What are chaining and open addressing? What happens to performance as load factor increases?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
A **hash collision** occurs when two different keys produce the same hash index. Every hash table must handle this.

**How to think through this:**
1. **Why collisions are inevitable:** A hash function maps a large key space (all possible strings) to a small array. By the pigeonhole principle, two keys will eventually land in the same slot.
2. **Chaining:** Each slot holds a linked list. Multiple keys that hash to slot 3 both go into the list at slot 3. Average case O(1) if chains are short; worst case O(n) if everything hashes to one slot.
3. **Open addressing:** All entries live in the array itself. On collision, probe for the next available slot (linear probing: check slot+1, slot+2). Deletion requires marking slots as "deleted" not "empty" or probing breaks.
4. **Load factor impact:** **Load factor** = (entries) / (array size). As it approaches 1.0:
   - Chaining: chains get longer → O(n) lookup approaches
   - Open addressing: **clustering** forms → performance degrades sharply before full
   - Python dicts resize at ~67% load factor. Java HashMap at 75%.

**Key takeaway:** Collisions are unavoidable — the question is how gracefully the table degrades, and load factor is the single biggest lever on that.

</details>

> 📖 **Theory:** [Hash Collisions](./10_hashing/theory.md#open-addressing)

---

### Q81 · [Interview] · `array-vs-linked-list`

> **Compare arrays vs linked lists across: random access, insert at middle, append, memory layout, cache performance. When would you use each in production?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Arrays and linked lists are the two fundamental ways to sequence data — one contiguous, one linked by pointers.

**How to think through this:**

| Operation | Array | Linked List |
|---|---|---|
| Random access (index i) | O(1) — direct offset arithmetic | O(n) — must traverse from head |
| Insert at middle | O(n) — shift elements right | O(1) — change two pointers (if you have the node) |
| Append at end | O(1) amortized (dynamic array) | O(1) with tail pointer |
| Memory layout | Contiguous block | Scattered heap nodes + pointer overhead |
| Cache performance | Excellent — CPU prefetches sequential memory | Poor — pointer-chasing causes cache misses |

**Real-world guidance:**
- **Use arrays** when you need random access or iteration dominates (numerical computation, ML). Python lists, NumPy arrays — all arrays under the hood.
- **Use linked lists** when you have very frequent inserts/deletes in the middle (LRU cache eviction list, OS task scheduler, undo/redo). In Python, `collections.deque` covers most queue needs with better cache behavior.

**Key takeaway:** Arrays win on access speed and cache performance; linked lists win on insert/delete flexibility — but modern hardware makes arrays faster than theory suggests in nearly all real workloads.

</details>

> 📖 **Theory:** [Arrays](./02_arrays/theory.md#arrays-in-python--complete-theory-zero-to-advanced)

---

### Q82 · [Interview] · `stack-vs-queue`

> **A junior developer asks "stack and queue seem the same — they're both linear collections. What's the real difference?" Give a concrete answer with real use cases.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
The difference is entirely in **which end you remove from**. That single constraint makes them useful for completely different problems.

**How to think through this:**
1. **Stack — LIFO (Last In, First Out):** The last item pushed is the first popped. Think of a stack of plates.
   - Real uses: function call stack, undo/redo, bracket matching, DFS, expression evaluation.

2. **Queue — FIFO (First In, First Out):** The first item enqueued is first dequeued. Think of a coffee shop line.
   - Real uses: task queues (Celery, SQS), BFS traversal, print spoolers, request buffers.

3. **The key mental model:** Stack = reversal + backtracking. Queue = ordering + fairness. If you need things in the order they arrived, use a queue. If you need the most recent thing first (or to undo the last action), use a stack.

4. **Gotcha:** Python's `list` works as a stack (`append`/`pop`) but is a bad queue because `list.pop(0)` is O(n). Use `collections.deque` for O(1) queue operations.

**Key takeaway:** Same shape, opposite order — stack reverses order (LIFO) for backtracking; queue preserves order (FIFO) for fair scheduling.

</details>

> 📖 **Theory:** [Stack vs Queue](./08_stack/theory.md#12-stack-vs-queue-in-daily-life)

---

### Q83 · [Interview] · `heap-vs-bst-compare`

> **Your interviewer asks: "If I need to always get the minimum element quickly, should I use a heap or a BST?" Give the nuanced answer with tradeoffs.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
For get-min only: heap. For get-min plus arbitrary search/delete: BST. Heap wins on simplicity; BST wins on generality.

**How to think through this:**

| Operation | Min-Heap | Balanced BST (AVL/Red-Black) |
|---|---|---|
| Get minimum | O(1) — always at root | O(log n) — leftmost node |
| Insert | O(log n) | O(log n) |
| Delete minimum | O(log n) | O(log n) |
| Delete arbitrary element | O(n) — must find it first | O(log n) |
| Search for arbitrary key | O(n) | O(log n) |
| In-order traversal (sorted) | Not supported natively | O(n) |

**The nuanced answer:**
- If your only operations are insert + extract-min (or max), use a **heap**. It's simpler, cache-friendlier (stored as array), smaller constant factors. Python's `heapq`, Java's `PriorityQueue`.
- If you also need to search by value, delete arbitrary nodes, find predecessor/successor, or iterate in sorted order — use a **BST**. Java's `TreeMap`, C++ `std::set`.
- Heaps do NOT support arbitrary deletion efficiently. If you need to remove a specific non-minimum element, use a "lazy deletion" pattern or a different structure.

**Practical note:** Python has no built-in balanced BST. `sortedcontainers.SortedList` is the common workaround.

**Key takeaway:** Heap = priority queue (fast min, not searchable); BST = sorted dictionary (O(log n) everything, more powerful, more overhead).

</details>

> 📖 **Theory:** [Heap vs BST](./16_heaps/theory.md#12-heap-vs-bst)

---

### Q84 · [Interview] · `bfs-vs-dfs-compare`

> **Compare BFS and DFS on: memory usage, path found, implementation complexity, suitability for infinite graphs. Which is better for shortest path? Why?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
BFS is the correct choice for unweighted shortest path. DFS is better for memory-constrained deep exploration and structural analysis.

**How to think through this:**

| Dimension | BFS | DFS |
|---|---|---|
| Memory usage | O(w) — width at max depth; enormous for wide graphs | O(d) — depth of recursion/stack; efficient for deep narrow graphs |
| Path found | Shortest path (fewest edges) guaranteed | Arbitrary path — may not be shortest |
| Implementation | Iterative with a queue | Recursive (natural) or iterative with explicit stack |
| Infinite graphs | Dangerous — holds all neighbors of each level in memory | Safer with depth limit; used in iterative deepening DFS |
| Shortest path | Yes — first visit = shortest | No — may reach target via a long detour |

**Why BFS guarantees shortest path:**
BFS processes nodes in order of distance from source. It visits all nodes at distance 1 before distance 2, etc. The first time it reaches the target, it arrived via minimum edges. DFS commits to one path and may explore deep before finding the target.

**When BFS memory is a problem:**
On a graph where every node has 1000 neighbors, BFS level 3 holds up to 10^9 nodes. **Bidirectional BFS** or **A*** are practical solutions.

**Key takeaway:** BFS = shortest path + high memory; DFS = deep exploration + low memory — know which constraint dominates your problem.

</details>

> 📖 **Theory:** [BFS vs DFS](./18_graphs/theory.md#8-when-to-use-bfs-vs-dfs)

---

### Q85 · [Interview] · `memoization-vs-tabulation`

> **When would you prefer memoization over tabulation, and vice versa? Give tradeoffs in terms of: ease of implementation, space, stack overflow risk, performance.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
**Memoization** (top-down DP) and **tabulation** (bottom-up DP) both eliminate redundant recomputation — but they differ in direction, implementation style, and risk profile.

**How to think through this:**

| Dimension | Memoization (top-down) | Tabulation (bottom-up) |
|---|---|---|
| Implementation | Add cache to recursive solution — easier to write from brute force | Rewrite iteratively, fill table in dependency order — requires understanding subproblem order |
| Space | Only computes needed subproblems — good for sparse problems | Fills entire table — may compute unnecessary subproblems |
| Stack overflow risk | Yes — deep recursion can hit Python's ~1000 recursion limit | No — purely iterative |
| Performance | Slightly slower — function call overhead + dict lookup | Faster — tight loop over array, cache-friendly |

**When to choose memoization:**
- Sparse subproblems (not all states reached)
- Translating a known recursive solution quickly (interview)
- Recursion depth is bounded and small

**When to choose tabulation:**
- Large n (risk of RecursionError in Python)
- Maximum performance needed
- Problem requires all subproblem results (e.g., bottom-up knapsack)

**Key takeaway:** Memoization is easier to write; tabulation is faster and safer in production — write memoization first in interviews, then mention you'd convert to tabulation for scale.

</details>

> 📖 **Theory:** [DP Approaches](./21_dynamic_programming/theory.md#memoization-top-down)

---

### Q86 · [Design] · `production-wrong-data-structure`

> **A production service stores 50M user IDs in a Python list and checks membership with `if user_id in user_list`. p99 latency is 800ms. What is the problem and fix?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
`in` on a Python `list` is O(n) — it scans every element. On 50M entries, that's up to 50M comparisons per lookup. Fix: convert to a `set`.

**How to think through this:**
1. **Root cause:** Python's `list.__contains__` is a linear scan — no index. For 50M elements, worst case is 50M comparisons. At modern CPU speeds, that's ~50ms per lookup in pure Python, ballooning to 800ms at p99 with contention.
2. **Fix:** Convert to a `set`. Python `set` uses a hash table internally. `in` on a `set` is O(1) average case.

```python
# Before — O(n) per lookup
user_list = [...]            # 50M user IDs
if user_id in user_list:     # ← scans up to 50M elements

# After — O(1) per lookup
user_set = set(user_list)    # ← one-time O(n) conversion
if user_id in user_set:      # ← O(1) hash lookup
```

3. **Tradeoffs:** A set uses ~2–3x more memory than a list (~3–4GB for 50M ints). If memory is tight, a **bitarray** (for dense integer IDs) or a **Bloom filter** (if false positives are tolerable) cuts memory 10–50x.

**Complexity:** Time: O(1) lookup · Space: O(n)

**Key takeaway:** Every `if x in list` in a hot path is a latency time bomb — the moment the list grows, linear search dominates your p99.

</details>

> 📖 **Theory:** [Hash Set Membership](./10_hashing/theory.md#6-hashing-in-python-dictionary--set)

---

### Q87 · [Design] · `production-slow-sort`

> **A data pipeline sorts 10M records every hour. It uses Python's built-in sort and was fine until data volume tripled. What would you investigate and change?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Python's built-in Timsort is O(n log n) and extremely well-optimized. The real issues are almost always in what you're sorting and how you're doing it.

**How to think through this:**
1. **Check what's being sorted:** If sorting large Python objects (dicts, dataclasses), comparison is slow because Python's dynamic dispatch runs on every comparison. Use a **key function** to extract a single comparable value up front.

```python
# Slow — compares full dicts on every comparison
records.sort()

# Fast — extract key once, sort on primitive
records.sort(key=lambda r: r['timestamp'])  # ← key extracted once per element
```

2. **Check if full sort is necessary:** If you need only top-1000 of 30M records, use `heapq.nlargest(1000, records)` — O(n log k) instead of O(n log n).
3. **Check if data is partially sorted:** Timsort is O(n) on already-sorted data. If the tripled data is unsorted where old data was nearly sorted, consider incremental sorted merging instead of full re-sort.
4. **Consider columnar tools:** For 30M records, `pandas DataFrame.sort_values()` or a SQL `ORDER BY` outperforms Python list sort by 5–20x due to vectorized C execution.

**Key takeaway:** When sort performance degrades, the algorithm is rarely wrong — investigate data structure overhead, key extraction, and whether a full sort is even the right operation.

</details>

> 📖 **Theory:** [Sorting Optimisation](./05_sorting/theory.md#sorting-in-python--deep-conceptual-theory)

---

### Q88 · [Design] · `production-stack-overflow`

> **A recursive tree processing function crashes with RecursionError on production data but works fine in tests. What are the two root causes and what are the fixes?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Two root causes: (1) **tree depth exceeds Python's recursion limit**, and (2) **a cycle in the data** causes infinite recursion.

**How to think through this:**

**Root cause 1 — Depth exceeds recursion limit:**
Python's default recursion limit is 1000 frames. Test data uses shallow trees (depth ~10–20). Production may have degenerate trees — e.g., a linked-list-shaped BST from sorted inserts — reaching depth 100K.

Fix: **Convert recursion to iteration** using an explicit stack (heap memory, no limit):
```python
def process_tree(root):
    stack = [root]
    while stack:
        node = stack.pop()
        process(node)                  # ← do work here
        if node.right: stack.append(node.right)
        if node.left:  stack.append(node.left)  # ← left last → processed first
```

**Root cause 2 — Cycle in the graph treated as a tree:**
Production data from databases or user input may contain cycles that clean test fixtures don't. Recursion never reaches the base case.

Fix: maintain a `visited` set:
```python
def process_tree(node, visited=None):
    if visited is None: visited = set()
    if node is None or id(node) in visited:
        return
    visited.add(id(node))
    # recurse on children
```

**Key takeaway:** "Works in tests, crashes in production" on recursion almost always means either the data is deeper than test fixtures, or production data has cycles that test data doesn't.

</details>

> 📖 **Theory:** [Recursion Limits](./04_recursion/theory.md#3-how-recursion-actually-works-call-stack)

---

### Q89 · [Design] · `production-negative-cycles`

> **A shortest-path calculation on a road network starts returning incorrect distances. You discover some "distances" are negative (tolls as credits). What algorithm do you need and why?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Switch to **Bellman-Ford** for negative edge weights. Dijkstra's algorithm is incorrect with negative weights.

**How to think through this:**
1. **Why Dijkstra fails:** Dijkstra's greedy assumption is that once a node is "settled," its distance is final — no shorter path can exist because all remaining edges are non-negative. A negative edge can violate this: a settled node might be reachable via a cheaper path through a later-discovered negative edge.
2. **Bellman-Ford:** Relaxes all edges V-1 times (V = number of vertices). Guarantees finding the shortest path even with negative edges. Time complexity O(V × E) — slower than Dijkstra's O((V + E) log V) but correct.
3. **Negative cycle detection:** If a V-th relaxation pass still decreases distances, a **negative cycle** exists (e.g., A → B → C → A with total weight -5). In that case, "shortest path" is undefined — loop forever for arbitrarily short paths. Reject the query and flag the data.
4. **Johnson's algorithm:** For all-pairs shortest path with negative edges: use Bellman-Ford once to reweight all edges to non-negative, then run Dijkstra from every source.

**Key takeaway:** Negative edges break Dijkstra's greedy invariant — use Bellman-Ford, and always check for negative cycles before trusting the result.

</details>

> 📖 **Theory:** [Negative Cycles](./25_advanced_graphs/theory.md#bellman-ford--shortest-path-with-negative-weights)

---

### Q90 · [Design] · `design-autocomplete`

> **Design the data structure layer for an autocomplete system that needs to: store 500K words, support prefix queries in under 5ms, and rank results by frequency. What would you use?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Use a **Trie** (prefix tree) where each node caches the top-K suggestions sorted by frequency, pre-computed at insert time. This gives O(p) prefix lookup where p = prefix length — well within 5ms.

**How to think through this:**
1. **Core structure — Trie:** Traversing a path spells a word. Prefix lookup is O(p) regardless of vocabulary size. A hash map would need O(n) scan; a trie gives O(p).
2. **Ranking — top-K at each node:** Naive trie returns all words under a prefix then sorts. Instead, each node caches the top-K (e.g., top 10) words by frequency. Queries return top-K in O(p + K) time with no subtree traversal.
3. **Frequency updates:** When a word is searched, increment its frequency and propagate up, updating each ancestor's top-K list. Use a **min-heap of size K** at each node for efficient updates.
4. **Memory optimization:** A naive trie for 500K words with avg length 8 = ~4M nodes. A **Patricia trie / radix tree** compresses common prefixes → 10–50x node reduction.
5. **Alternative at scale:** Store prefix → top-K list in a key-value store (key = prefix string, value = top-K precomputed). Lookup is O(1) hash. Updated by a background job. Trades freshness for simplicity.

**Recommended:** Compressed trie with top-10 results cached per node. Updates O(p × K), queries O(p + K). Fits in memory for 500K words (~50–200MB).

**Key takeaway:** The trie's O(prefix-length) lookup is why autocomplete is fast — caching ranked results at each node means queries never traverse the subtree.

</details>

> 📖 **Theory:** [Autocomplete Design](./17_trie/theory.md#trie--the-tree-of-words)

---

## 🧠 Tier 5 — Critical Thinking

---

### Q91 · [Logical] · `predict-output-recursion`

> **What does this function print when called with `f(4)`? Trace the execution and explain the pattern.**

```python
def f(n):
    if n == 0:
        return
    f(n - 1)
    print(n)
    f(n - 1)
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Output (each on its own line): `1 2 1 3 1 2 1 4 1 2 1 3 1 2 1`

**How to think through this:**
1. The structure is: recurse left, print self, recurse right — this is an **in-order traversal** of an implicit binary tree.
2. Build up from small cases:
   - `f(1)` → `f(0)` (nothing) → print 1 → `f(0)` (nothing) → output: `1`
   - `f(2)` → `f(1)` → print 2 → `f(1)` → output: `1 2 1`
   - `f(3)` → `f(2)` → print 3 → `f(2)` → output: `1 2 1 3 1 2 1`
   - `f(4)` → `f(3)` → print 4 → `f(3)` → output: `1 2 1 3 1 2 1 4 1 2 1 3 1 2 1`
3. The output of `f(n)` is always `f(n-1)` + `n` + `f(n-1)` — a **palindrome** at each level. Total print statements = 2^n - 1 (15 for n=4).
4. This is the same move sequence as the **Tower of Hanoi** for n disks.

**Complexity:** Time: O(2^n) · Space: O(n) call stack depth

**Key takeaway:** Pre-order, in-order, and post-order positions of print in recursion produce dramatically different outputs — print between two recursive calls gives a symmetric, palindromic sequence.

</details>

> 📖 **Theory:** [Recursion Tracing](./04_recursion/theory.md#recursion-in-python--complete-theory-zero-to-advanced)

---

### Q92 · [Logical] · `predict-two-pointer-trace`

> **Trace the two-pointer approach on `arr = [1, 2, 3, 4, 5, 6]`, `target = 7` (find pair that sums to target). Show left/right pointer positions at each step and the final answer.**

```python
def two_sum_sorted(arr, target):
    left, right = 0, len(arr) - 1
    while left < right:
        current = arr[left] + arr[right]
        if current == target:
            return (arr[left], arr[right])
        elif current < target:
            left += 1
        else:
            right -= 1
    return None
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Returns `(1, 6)` on the first step. `arr[0] + arr[5] = 1 + 6 = 7 == target`.

**How to think through this:**

| Step | left | right | arr[left] | arr[right] | sum | action |
|---|---|---|---|---|---|---|
| 1 | 0 | 5 | 1 | 6 | 7 | == target → return (1, 6) |

**Why the algorithm works:**
1. Requires a **sorted array** — the algorithm depends on the invariant that moving left up increases the sum, moving right down decreases it.
2. If sum < target: the left value is too small, advance left to a larger value.
3. If sum > target: the right value is too large, retreat right to a smaller value.
4. This eliminates half the search space logically at each step — O(n) time vs O(n²) brute force.

**Extended trace if target were 9:**

| Step | left | right | sum | action |
|---|---|---|---|---|
| 1 | 0 | 5 | 1+6=7 | < 9, left++ |
| 2 | 1 | 5 | 2+6=8 | < 9, left++ |
| 3 | 2 | 5 | 3+6=9 | == 9, return (3,6) |

**Complexity:** Time: O(n) · Space: O(1)

**Key takeaway:** Two pointers work on sorted arrays because the ordering gives direction — you always know which pointer to move based on whether the sum overshoots or undershoots.

</details>

> 📖 **Theory:** [Two Pointer Tracing](./11_two_pointers/theory.md#two-pointers--thinking-with-two-moving-hands)

---

### Q93 · [Logical] · `predict-dp-table`

> **Trace the coin change DP table for `coins = [1, 2, 5]`, `amount = 5`. Fill the table row by row and identify the final answer. What does `dp[i]` represent?**

```python
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)  # ← use this coin, add 1
    return dp[amount] if dp[amount] != float('inf') else -1
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
`dp[5] = 1` (one coin of value 5). Final answer: **1**.

**How to think through this:**

`dp[i]` = the **minimum number of coins** needed to make exactly amount `i`. `dp[0] = 0` (zero coins to make amount 0).

**Table fill (coins = [1, 2, 5]):**

| i | coin=1: dp[i-1]+1 | coin=2: dp[i-2]+1 | coin=5: dp[i-5]+1 | dp[i] |
|---|---|---|---|---|
| 0 | — | — | — | 0 (base case) |
| 1 | dp[0]+1 = 1 | i<2, skip | i<5, skip | 1 |
| 2 | dp[1]+1 = 2 | dp[0]+1 = 1 | i<5, skip | 1 |
| 3 | dp[2]+1 = 2 | dp[1]+1 = 2 | i<5, skip | 2 |
| 4 | dp[3]+1 = 3 | dp[2]+1 = 2 | i<5, skip | 2 |
| 5 | dp[4]+1 = 3 | dp[3]+1 = 3 | dp[0]+1 = 1 | **1** |

Final `dp = [0, 1, 1, 2, 2, 1]`. Answer: `dp[5] = 1` (use the coin of value 5 once).

**The recurrence:** For each amount `i`, try every coin `c`. If we use coin `c`, we need `dp[i - c]` more coins. Take the minimum over all valid coins.

**Complexity:** Time: O(amount × len(coins)) · Space: O(amount)

**Key takeaway:** DP for coin change works bottom-up — you can only compute dp[5] correctly because dp[0] through dp[4] are already exact.

</details>

> 📖 **Theory:** [DP Table Tracing](./21_dynamic_programming/theory.md#3-core-idea-of-dp)

---

### Q94 · [Debug] · `debug-binary-search`

> **Find the bug:**

```python
def binary_search(arr, target):
    left, right = 0, len(arr)
    while left < right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid
        else:
            right = mid - 1
    return -1
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Two bugs: (1) `right = len(arr)` should be `len(arr) - 1` (out-of-bounds), and (2) `left = mid` causes an infinite loop — should be `left = mid + 1`.

**How to think through this:**

**Bug 1 — `right = len(arr)`:**
`len(arr)` is one past the last valid index. When `mid = (left + right) // 2`, it can produce `arr[len(arr)]` → `IndexError`. Fix: `right = len(arr) - 1`.

**Bug 2 — `left = mid` instead of `left = mid + 1`:**
This causes an **infinite loop**. Example: `arr = [1, 3]`, `target = 3`. `left=0, right=1, mid=0`. `arr[0]=1 < 3`, so `left = 0`. Now left=0, right=1, mid=0 forever. We already know `arr[mid] < target`, so mid itself is not the answer — start the next search after it.

**Fixed code:**
```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1   # ← fix 1: valid upper bound
    while left <= right:             # ← also fix: <= to handle single element
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1           # ← fix 2: advance past mid
        else:
            right = mid - 1
    return -1
```

**Complexity:** Time: O(log n) · Space: O(1)

**Key takeaway:** The two most common binary search bugs: off-by-one on bounds, and `left = mid` instead of `left = mid + 1` — the latter always causes an infinite loop when search space reduces to two elements.

</details>

> 📖 **Theory:** [Binary Search](./13_binary_search/theory.md#binary-search--the-art-of-intelligent-guessing)

---

### Q95 · [Debug] · `debug-recursion-limit`

> **This function causes a RecursionError on `n=1000`. Find all bugs:**

```python
def sum_to_n(n):
    if n == 1:
        return 1
    return n + sum_to_n(n)
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
One critical bug: `sum_to_n(n)` should be `sum_to_n(n - 1)`. The function calls itself with the same argument indefinitely — infinite recursion, not a depth-limit issue.

**How to think through this:**
1. **The bug:** The recursive call passes `n` unchanged. The base case `n == 1` is never reached for any `n > 1` because the input never decreases. This would crash on `n=2` just as fast as `n=1000`.
2. **Secondary issue — base case:** If called with `n=0` or negative `n`, the base case is never hit. A safer base case is `if n <= 0: return 0`.
3. **Fixed code:**

```python
def sum_to_n(n):
    if n <= 0:              # ← handle zero/negative inputs
        return 0
    if n == 1:
        return 1
    return n + sum_to_n(n - 1)  # ← fix: recurse with n-1
```

4. **Production-safe alternative:**

```python
def sum_to_n(n):
    return n * (n + 1) // 2  # ← O(1), no recursion at all
```

For sum 1..n, the closed-form formula is always the right answer in production.

**Complexity:** Time: O(n) recursive · O(1) with formula · Space: O(n) recursive stack · O(1) with formula

**Key takeaway:** Before writing recursion, verify the recursive call argument actually moves toward the base case — if it doesn't, you have infinite recursion regardless of stack depth.

</details>

> 📖 **Theory:** [Recursion Base Case](./04_recursion/theory.md#1-base-case)

---

### Q96 · [Debug] · `debug-cycle-detection`

> **This cycle detection is wrong. What is the bug?**

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next
        if slow == fast:
            return True
    return False
```

<details>
<summary>💡 Show Answer</summary>

**Answer:**
`fast` is only advanced by one step (`fast = fast.next`) instead of two (`fast = fast.next.next`). Floyd's cycle detection requires fast to move at 2× the speed of slow — same speed means they never converge in a cycle.

**How to think through this:**
1. **Floyd's algorithm requires:** `slow` moves 1 step, `fast` moves 2 steps per iteration. The speed difference is what guarantees that if a cycle exists, fast eventually laps slow and they meet inside the cycle.
2. **What the buggy code does:** Both pointers move one step. They start equal (both at head) and if the list has a cycle, they move together at the same rate — they'll always be the same distance apart and never re-converge.
3. **The equality check timing:** After the first iteration, both have moved one step. They're no longer equal (assuming list has ≥ 2 nodes). The algorithm then just traverses the list in tandem without ever detecting a cycle.

**Fixed code:**
```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next  # ← fix: fast moves 2 steps
        if slow == fast:
            return True
    return False
```

**Complexity:** Time: O(n) · Space: O(1)

**Key takeaway:** Floyd's cycle detection only works because of the speed differential — fast must move exactly twice as fast as slow; equal speed means they never meet in a cycle.

</details>

> 📖 **Theory:** [Cycle Detection](./07_linked_list/theory.md#detect-cycle)

---

### Q97 · [Design] · `design-cache-eviction`

> **Your in-memory cache is full. You must evict one entry. Compare LRU, LFU, and random eviction. Which would you choose for: (a) a web session cache, (b) a CPU instruction cache, (c) a DNS cache?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
No single policy wins universally — the right choice depends on the access pattern of the specific workload.

**How to think through this:**

**LRU (Least Recently Used):** Evict the entry accessed longest ago. Assumes recent access predicts future access. Works well for temporal locality. Implementation: doubly-linked list + hash map, O(1) get and put.

**LFU (Least Frequently Used):** Evict the entry with the lowest access count. Handles long-term popularity better than LRU but is slow to adapt to changing popularity. More complex to implement at O(1).

**Random eviction:** Evict a randomly chosen entry. Surprisingly competitive in practice — no metadata overhead, avoids adversarial access patterns that defeat LRU.

**Decisions by workload:**

**(a) Web session cache:** **LRU**. User sessions have strong temporal locality — if a user hasn't been active recently, their session is unlikely to be needed. LRU naturally ages out idle sessions.

**(b) CPU instruction cache:** **LRU** (or pseudo-LRU for hardware simplicity). CPU instruction access has strong temporal locality — loops cause repeated access to the same small set of instructions. LRU correctly retains the hot inner loop.

**(c) DNS cache:** **TTL-based expiration first**, then **LRU** for eviction when full. DNS entries have explicit TTLs from authoritative servers — this is the primary expiration mechanism. When the cache is full and all entries are TTL-valid, LRU is a reasonable secondary policy.

**Key takeaway:** LRU is the safe default for most caches; use LFU when your workload has stable long-term popularity patterns; use random eviction when simplicity matters more than optimality.

</details>

> 📖 **Theory:** [Cache Eviction](./10_hashing/theory.md)

---

### Q98 · [Design] · `design-sorting-choice`

> **You are building a leaderboard that re-ranks 10M players after every game (up to 100K games/second). Would you: (a) sort the full array each time, (b) use a heap, (c) use a sorted BST/skip list, or (d) use a bucket sort approach? Justify your choice.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Option **(c) sorted BST/skip list** for general purpose; option **(d) bucket sort** if scores are bounded integers and you need maximum throughput. Never option (a).

**How to think through this:**

**(a) Full sort each time:**
O(n log n) = O(10M × 23) ≈ 230M operations per game event. At 100K games/second = 23 trillion operations/second. Completely infeasible.

**(b) Heap:**
O(log n) insert/extract-min, O(1) get-max. Good for "top-K" queries only. A heap does NOT maintain full sorted order efficiently — iterating all 10M players in rank order requires O(n log n). Use only if you need top-K, not the full leaderboard.

**(c) Sorted BST / skip list:**
O(log n) per insert, delete, update (find + remove old score + insert new score). Full sorted traversal is O(n). At 100K updates/second: 100K × log(10M) ≈ 2.3M operations/second — very feasible. **Redis sorted sets** use a skip list for exactly this use case (`ZADD`/`ZRANGE`).

**(d) Bucket sort:**
If scores are integers in a bounded range (e.g., 0–10,000), maintain `bucket[score]` = count of players at that score. Score update = O(1). Range queries = O(range). For 10K score range, full rank computation is 10K operations — extremely fast. Only works with bounded integer scores.

**Recommended:** Use Redis sorted sets (skip list) for general purpose, or bucket array for bounded integer scores. Never re-sort the full array.

**Key takeaway:** Leaderboard updates are incremental — use a data structure that supports O(log n) point updates, not one that requires O(n log n) full rebuilds.

</details>

> 📖 **Theory:** [Sorting Choice](./05_sorting/theory.md#sorting-in-python--deep-conceptual-theory)

---

### Q99 · [Design] · `design-word-frequency`

> **Design a system that counts word frequency across 10GB of text files arriving as a stream. You have 2GB RAM. You need top-K frequent words at any point. Design the data structures and algorithm.**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Use a **hash map for counting** combined with a **min-heap of size K for top-K tracking**. For streaming with limited RAM, use **Count-Min Sketch** for approximate counts or **external merge sort** for exact counts.

**How to think through this:**

**Phase 1 — Counting (streaming, limited RAM):**
- **Exact counts:** Process stream in chunks. For each chunk, maintain `dict[word → count]` in memory. When memory approaches 2GB, flush partial counts to disk as a sorted file. After all chunks, **external merge sort** the partial files to get exact word counts.
- **Approximate counts (Count-Min Sketch):** A 2D array of counters with multiple hash functions. O(1) update, O(1) query, fixed memory (e.g., 50MB for high accuracy). Overestimates slightly, never underestimates. Use when 1–5% error is acceptable.

**Phase 2 — Top-K tracking:**
Maintain a **min-heap of size K** with the K highest-frequency words seen so far.
- For each word update: if word is already in heap, update its count and re-heapify. If its new count exceeds the current heap minimum, replace the minimum.
- O(log K) per update.
- At any point, the heap contains the current top-K words.

**Architecture:**
```
Stream → tokenize → hash map (in-memory chunk)
                  ↓ (chunk full)
           flush to disk (sorted by word)
                  ↓ (end of stream)
         external merge sort → final sorted file
                  ↓
         scan final file → min-heap(K) → top-K result
```

**Key takeaway:** When data exceeds RAM, the pattern is always: process in chunks, flush sorted partial results to disk, merge at the end — and track only what you need (top-K) with a heap, not the full sorted list.

</details>

> 📖 **Theory:** [Word Frequency](./10_hashing/theory.md)

---

### Q100 · [Design] · `design-shortest-path-constraints`

> **Design a shortest-path algorithm for a delivery routing system: 100K nodes, real-time edge weight updates (road closures), queries must complete under 100ms. What algorithm and data structure would you use and why?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**
Use **bidirectional Dijkstra** with an **indexed priority queue** for general use. For sub-10ms queries with infrequent updates, use **Contraction Hierarchies (CH)** — the algorithm Google Maps and OSRM use.

**How to think through this:**

**Why vanilla Dijkstra is borderline:**
Standard Dijkstra on 100K nodes + ~500K edges: O((V + E) log V) ≈ 3M operations. In Python: ~300–500ms. In C++: ~10ms. You need to reduce the search space.

**Option 1 — Bidirectional Dijkstra:**
Run simultaneously from source and target, meeting in the middle. Reduces search space from O(V) to O(√V) in practice. On 100K nodes, often achieves the 100ms target without preprocessing. Simple to implement.

**Option 2 — A* with Euclidean heuristic:**
Uses geographic coordinates to focus search toward the destination. Dramatically reduces nodes expanded. Requires coordinates — realistic for delivery routing.

**Option 3 — Contraction Hierarchies (CH):**
Offline preprocessing: rank nodes by "importance," add shortcut edges bypassing unimportant nodes. Query time on 100K nodes drops to ~1ms. This is what Google Maps uses. Updates (road closures) require local re-preprocessing.

**Handling real-time updates:**
- Use an **indexed priority queue** (supports decrease-key in O(log n)) so edge weight changes don't require rebuilding the entire queue.
- For road closures: mark edge as infinity-weight. Next query routes around it automatically.
- For frequent bulk updates: maintain a version counter per edge; queries skip stale entries.

**Recommended architecture:**
1. Build Contraction Hierarchies offline on the base graph.
2. Bidirectional CH query at runtime — typically < 1ms on 100K nodes.
3. For single road closure: invalidate affected shortcuts locally, re-contract the affected region (< 1 second for local neighborhood).
4. Data structures: adjacency list for graph, indexed min-heap for Dijkstra, hash map for edge-weight overrides.

**Key takeaway:** Static shortest path is solved — the challenge is dynamic updates. Contraction Hierarchies give microsecond queries but require preprocessing; the balance between query speed and update cost depends on your specific traffic update frequency.

</details>

> 📖 **Theory:** [Shortest Path](./25_advanced_graphs/theory.md#5-shortest-path-algorithms)
