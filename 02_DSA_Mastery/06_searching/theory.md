<a id="top"></a>
# 📘 06 – Searching in Python

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. The Two Worlds of Searching](#1-two-worlds)
- [2. Linear Search — The Baseline Strategy](#2-linear-search)
  - [Visual: Linear Search Trace](#visual-linear-trace)
- [3. Why Binary Search Is Powerful](#3-why-binary-search)
  - [Visual: Binary Search Step by Step](#visual-binary-step)
- [4. Binary Search — Core Mechanics](#4-core-mechanics)
- [5. Common Mistakes and Templates](#5-mistakes-templates)
  - [Template 1: lo <= hi — Exact Match](#template-1)
  - [Template 2: lo < hi — Boundary Finding](#template-2)
  - [Template 3: lo < hi - 1 — Avoid Infinite Loop](#template-3)
  - [Off-by-One Pointer Rules](#off-by-one)
- [6. Variations of Binary Search](#6-variations)
  - [First Occurrence](#first-occurrence)
  - [Last Occurrence](#last-occurrence)
  - [Lower Bound](#lower-bound)
  - [Upper Bound](#upper-bound)
- [7. Search on Answer](#7-search-on-answer)
  - [Visual: Koko Eating Bananas](#visual-koko)
- [8. Advanced Search Patterns](#8-advanced-patterns)
  - [Rotated Sorted Array](#rotated-array)
  - [2D Matrix Search](#2d-matrix)
- [9. Real-World Impact](#9-real-world)
- [🔥 Summary](#summary)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
binary search mechanics · O(log n) · monotonic property · loop invariant

**Should Learn** — Important for real projects, comes up regularly:
first/last occurrence · lower/upper bound · search on answer pattern

**Good to Know** — Useful in specific situations, not always tested:
search in rotated sorted array · search in 2D matrix

**Reference** — Know it exists, look up syntax when needed:
exponential search · interpolation search · jump search

Scout is an intelligence operative. Her job: find a target in hostile terrain. Sometimes she has no map — she must check every building, one by one. Other times she has a sorted directory — she can jump straight to the right neighborhood. Every search problem Scout faces begins with one critical question: **Is the data sorted?** Her entire strategy depends on the answer.

<a id="1-two-worlds"></a>
# 1. The Two Worlds of Searching

Scout learns on day one that all search problems fall into two categories — like two different terrains that require completely different tactics. In open wilderness (unsorted data), she must walk every path. In a numbered street (sorted data), she can skip ahead intelligently.

1. **Searching in Unsorted Data** — options are limited, linear scan required
2. **Searching in Sorted Data** — powerful optimizations become available

Understanding this distinction is fundamental. Your entire approach depends on it.

> [↑ Back to Top](#top)

<a id="2-linear-search"></a>
# 2. Linear Search — The Baseline Strategy

Scout comes home, reaches into her pocket — no keys. She starts checking every drawer in the house, one by one. Kitchen drawer... nope. Junk drawer... nope. Bedside table drawer... THERE they are. That is linear search. She checks every single item until she finds what she wants or runs out of places to look.

<a id="visual-linear-trace"></a>
## Visual: Linear Search Trace

```
Array: [14, 3, 27, 9, 51, 6, 33]
Target: 33

Step 1: Check index 0 → 14 ≠ 33
Step 2: Check index 1 →  3 ≠ 33
Step 3: Check index 2 → 27 ≠ 33
Step 4: Check index 3 →  9 ≠ 33
Step 5: Check index 4 → 51 ≠ 33
Step 6: Check index 5 →  6 ≠ 33
Step 7: Check index 6 → 33 = 33  ✓ FOUND at index 6
```

The harsh truth: whether Scout finds her keys on step 1 or step 7, the worst case is always going through everything. That is O(n).

Best case: O(1) — the first drawer. Average case: O(n/2) — which we still call O(n).

```python
def linear_search(arr, target):
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1
```

When to use: array is small, unsorted, or searched only once.
When NOT to use: array is large and sorted — that is where binary search comes in.

**Common mistake — linear search in a loop:** Using `if x in list` inside a loop is O(n) per call, making the whole loop O(n²). Convert the list to a `set` first for O(1) average lookups.

> 📝 **Practice:** [Q1 — Linear Search — Return Index](./practice.md#q1--linear-search--return-index) · [Q2 — All Occurrences](./practice.md#q2--linear-search--all-occurrences) · [Q8 — 2D Linear Search](./practice.md#q8--linear-search-on-2d-list)

> [↑ Back to Top](#top)

<a id="3-why-binary-search"></a>
# 3. Why Binary Search Is Powerful

Scout is looking up a name in a phone book. She does not start at page 1 and read every name. She flips to the middle — lands on "Morrison." She knows her target "Williams" comes after Morrison alphabetically, so she throws away the entire first half. Now she searches only the remaining half.

That is binary search. But here is the critical insight:

> Binary search only works because the phone book is SORTED.

If entries were in random order, opening to the middle tells Scout nothing.

```
SORTED book — middle gives useful information:
[A...] [B...] [C...] [MIDDLE → M] [...S] [...T] [...W] [...Z]
                           ↑
                    "Williams > M, so discard left half"

RANDOM book — middle tells you nothing:
[X...] [B...] [Z...] [MIDDLE → M] [...A] [...T] [...W] [...D]
                           ↑
                    "Williams > M, but Williams could be ANYWHERE"
```

<a id="visual-binary-step"></a>
## Visual: Binary Search Step by Step

Search for **37** in this sorted array:

```
Index: [0]  [1]  [2]  [3]  [4]  [5]  [6]  [7]  [8]  [9]
Value:   1    5   12   18   23   37   44   57   62   89
```

**Round 1:**

```
lo=0                          hi=9
 ↓                              ↓
  1    5   12   18   23   37   44   57   62   89
                    ↑
               mid = (0+9)//2 = 4
               arr[4] = 23

23 < 37, so target is in the RIGHT half.
Move lo = mid + 1 = 5
```

**Round 2:**

```
                         lo=5       hi=9
                          ↓          ↓
  1    5   12   18   23   37   44   57   62   89
                               ↑
                          mid = (5+9)//2 = 7
                          arr[7] = 57

57 > 37, so target is in the LEFT half.
Move hi = mid - 1 = 6
```

**Round 3:**

```
                         lo=5  hi=6
                          ↓     ↓
  1    5   12   18   23   37   44   57   62   89
                          ↑
                     mid = (5+6)//2 = 5
                     arr[5] = 37

37 == 37  ✓ FOUND at index 5
```

Three comparisons for 10 elements. For 1 billion elements, binary search needs at most 30 comparisons. Time: O(log n).

> 📝 **Practice:** [Q3 — Binary Search Iterative](./practice.md#q3--binary-search--iterative) · [Q4 — Binary Search Recursive](./practice.md#q4--binary-search--recursive)

> [↑ Back to Top](#top)

<a id="4-core-mechanics"></a>
# 4. Binary Search — Core Mechanics

Scout drills the exact procedure until it is muscle memory. Binary search requires two things: **sorted data** and **random access** (arrays, not linked lists). Get either wrong and the search silently produces wrong answers.

```python
lo, hi = 0, len(arr) - 1

while lo <= hi:
    mid = lo + (hi - lo) // 2

    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        lo = mid + 1
    else:
        hi = mid - 1
```

**Why check mid BEFORE moving?** So Scout does not skip right over the answer.

**What if lo > hi?** The window has collapsed — target is not present. Return -1.

**Common mistake — overflow in midpoint:** In Python, `(lo + hi) // 2` is safe (arbitrary precision). In Java/C++, it overflows. Prefer `lo + (hi - lo) // 2` everywhere.

```
Regular:   mid = (lo + hi) // 2
Safe:      mid = lo + (hi - lo) // 2

The intermediate value (hi - lo) is always <= hi,
bounded by the array size — no overflow risk.
```

**Common mistake — missing post-loop verification:** After a `while lo < hi` loop, `lo` points to the convergence point but that element may not equal the target. Always verify: `if lo < len(arr) and arr[lo] == target`.

> 📝 **Practice:** [Q6 — Insertion Point](./practice.md#q6--insertion-point) · [Q7 — When to Choose What](./practice.md#q7--complexity-analysis--when-to-choose-what)

> [↑ Back to Top](#top)

<a id="5-mistakes-templates"></a>
# 5. Common Mistakes and Templates

Scout discovers that binary search is simple in concept but error-prone in execution. Even Jon Bentley reported that only about 10% of professional programmers could write a correct one on the first try. The main failure modes: infinite loop, wrong boundary condition, overflow, off-by-one, forgetting sorted requirement.

<a id="template-1"></a>
## Template 1: lo <= hi — Exact Match Search

Use when you want to find a specific value and return its index.

```
Invariant: target (if it exists) is in the range [lo, hi]

Loop exits when:  lo > hi  (window is empty — not found)
                  OR we return early when arr[mid] == target

 lo=0                    hi=9
  ├────────────────────────┤
  │ search space           │
  └────────────────────────┘

Each step either:
  - Returns the found index
  - Shrinks the window by setting lo = mid+1 or hi = mid-1
```

The `lo <= hi` condition means we still check when the window is a single element (lo == hi).

<a id="template-2"></a>
## Template 2: lo < hi — Boundary Finding

Use when you want the LEFTMOST or RIGHTMOST position (first occurrence, insertion point).

```
Invariant: the answer is always inside [lo, hi]

Loop exits when:  lo == hi  (they converge ON the answer)

 lo=0                    hi=9
  ├────────────────────────┤
  At convergence: lo == hi == answer position
```

Key: when `arr[mid]` could be the answer, set `hi = mid` (not `mid-1`).

```python
def lower_bound(arr, target):
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid               # mid might be the answer, keep it
    return lo
```

<a id="template-3"></a>
## Template 3: lo < hi - 1 — Avoid Infinite Loop

Use when `mid` is assigned to `lo` (not `mid+1`). Without this guard, infinite loop.

```
The danger:
  lo=5, hi=6
  mid = (5+6)//2 = 5
  If we set lo = mid = 5... lo never advances!

The fix:
  Loop condition: lo < hi - 1
  Ensures at least 2 elements remain, so mid is always BETWEEN lo and hi.
```

When the loop exits, you have `hi = lo + 1`. Manually check both `arr[lo]` and `arr[hi]`.

<a id="off-by-one"></a>
## Off-by-One Pointer Rules

**`lo = mid + 1`:** When mid is CERTAIN not the answer (too small).

```
arr[mid] < target:
  ... [mid] [mid+1] ...
         ✗    ← lo starts here
```

**`hi = mid - 1`:** When mid is CERTAIN not the answer (too large, exact match search).

```
arr[mid] > target:
  ... [mid-1] [mid] ...
          ↑     ✗
       hi goes here
```

**`hi = mid`:** When doing boundary finding and mid might be the answer.

```
arr[mid] >= target:
  mid satisfies the condition but there might be an earlier one
  ... [mid-1] [mid] ...
               ↑
            hi stays here
```

**Common mistake — infinite loop with `lo = mid`:** When `lo=5, hi=6`, `mid = 5`. Setting `lo = mid = 5` never advances. Fix: use Template 1 with `lo = mid + 1`, or Template 3 with `lo < hi - 1` guard.

```
Two-element proof that Template 1 always terminates:

arr = [1, 2], target = 2

Iteration 1:
  lo=0, hi=1, mid=0, arr[0]=1 < 2 -> lo = mid+1 = 1

Iteration 2:
  lo=1, hi=1, mid=1, arr[1]=2 == target -> return 1  ✓

Template 1 ALWAYS terminates because:
  - arr[mid] < target: lo = mid+1 → lo strictly increases
  - arr[mid] > target: hi = mid-1 → hi strictly decreases
  - The interval [lo, hi] strictly shrinks each iteration.
```

**Common mistake — wrong template for boundary search:** Exact-match template returns ANY match. Boundary template returns FIRST match.

```
arr = [1, 1, 1, 2, 2, 2, 3, 3, 3]
idx:   0  1  2  3  4  5  6  7  8

Exact-match template, target=2:
  lo=0, hi=8, mid=4, arr[4]=2 -> return 4 immediately.
  But the first occurrence is at index 3!
```

Fix: record `result = mid` and keep searching left (`hi = mid - 1`).

**What the pointers mean after the loop:**

```
After Template 1 exits WITHOUT finding target:

    ...elements < target... | ...elements > target...
                            ^hi     ^lo

    lo  = index of first element > target (or len(arr))
    hi  = index of last element < target  (or -1)
```

> 📝 **Practice:** [Q25 — Off-by-One Bug Hunt](./practice.md#q25--off-by-one-bug-hunt)

> [↑ Back to Top](#top)

<a id="6-variations"></a>
# 6. Variations of Binary Search

Scout rarely gets asked "find this exact value." Real missions are subtler: "find the first occurrence," "find the insertion point," "find the boundary." These variations are the bread and butter of interviews.

<a id="first-occurrence"></a>
## First Occurrence

Find first index of target. Key: when found, keep searching left.

```python
def find_first(arr, target):
    lo, hi = 0, len(arr) - 1
    result = -1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            result = mid
            hi = mid - 1    # keep searching left
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return result
```

<a id="last-occurrence"></a>
## Last Occurrence

When found, keep searching right.

```python
def find_last(arr, target):
    lo, hi = 0, len(arr) - 1
    result = -1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            result = mid
            lo = mid + 1    # keep searching right
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return result
```

<a id="lower-bound"></a>
## Lower Bound

First element >= target.

```python
def lower_bound(arr, target):
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

<a id="upper-bound"></a>
## Upper Bound

First element > target.

```python
def upper_bound(arr, target):
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

**Common mistake — bisect_left vs bisect_right for duplicates:**

```
arr = [1, 1, 1, 2, 2, 2, 3, 3, 3]

bisect_left(arr, 2)  = 3   → index of FIRST 2
bisect_right(arr, 2) = 6   → index AFTER last 2

Count of 2s = bisect_right - bisect_left = 6 - 3 = 3  ✓
```

> 📝 **Practice:** [Q9 — First Occurrence](./practice.md#q9--first-occurrence) · [Q10 — Last Occurrence](./practice.md#q10--last-occurrence) · [Q11 — Count in Sorted Array](./practice.md#q11--count-of-target-in-sorted-array) · [Q5 — Count via bisect](./practice.md#q5--count-occurrences-in-sorted-array)

> [↑ Back to Top](#top)

<a id="7-search-on-answer"></a>
# 7. Search on Answer

Scout's friend thinks of a number between 1 and 1,000,000. She does not search through a list — she binary searches on the VALUE SPACE. "Is it more or less than 500,000?" Each question halves the search space. In 20 questions, she can find any number.

Many binary search problems are NOT about searching a position in an array — they are about searching the ANSWER ITSELF. The condition is monotonic:

```
False False False True True True
```

Binary search can find the transition point.

<a id="visual-koko"></a>
## Visual: Koko Eating Bananas

Koko has piles of bananas: `[3, 6, 7, 11]`. She has 8 hours. What is the minimum speed?

At speed `k`, pile of size `p` takes `ceil(p/k)` hours. If speed `k` works, then speed `k+1` also works — the condition is monotone.

```
Speed:   1    2    3    4    5    6    7    8    9   10   11
Works?:  ✗    ✗    ✗    ✓    ✓    ✓    ✓    ✓    ✓    ✓    ✓
                        ↑
                 first valid speed
```

```
lo=1, hi=11

Round 1: mid=6
  Speed 6: ceil(3/6)+ceil(6/6)+ceil(7/6)+ceil(11/6) = 1+1+2+2 = 6 ≤ 8 ✓
  Works! But maybe slower speed also works. hi = mid = 6

Round 2: lo=1, hi=6, mid=3
  Speed 3: 1+2+3+4 = 10 > 8 ✗
  Too slow. lo = mid + 1 = 4

Round 3: lo=4, hi=6, mid=5
  Speed 5: 1+2+2+3 = 8 ≤ 8 ✓
  Works! hi = mid = 5

Round 4: lo=4, hi=5, mid=4
  Speed 4: 1+2+2+3 = 8 ≤ 8 ✓
  Works! hi = mid = 4

lo == hi == 4. Answer: speed 4.
```

The template:

```python
def binary_search_on_answer(lo, hi, condition):
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if condition(mid):
            hi = mid       # mid satisfies, look for smaller
        else:
            lo = mid + 1   # mid doesn't satisfy, need larger
    return lo  # lo == hi == minimum satisfying value
```

This pattern appears in capacity, scheduling, minimum speed, and allocation problems.

**Common mistake — searching array index instead of answer range:** For "minimize X" problems, the search space is the VALUE of X (e.g., speed from 1 to max(piles)), not a position in the array.

> 📝 **Practice:** [Q18 — Integer Sqrt](./practice.md#q18--square-root-via-binary-search) · [Q19 — Koko Eating Bananas](./practice.md#q19--koko-eating-bananas) · [Q20 — Ship Packages](./practice.md#q20--ship-packages-within-d-days) · [Q22 — Smallest Divisor](./practice.md#q22--smallest-divisor-given-threshold) · [Q24 — Allocate Min Pages](./practice.md#q24--allocate-minimum-pages)

> [↑ Back to Top](#top)

<a id="8-advanced-patterns"></a>
# 8. Advanced Search Patterns

Scout encounters terrain that is not perfectly sorted — a rotated map, a 2D grid. Standard binary search does not work directly, but the principle of halving the search space still applies with modifications.

<a id="rotated-array"></a>
## Rotated Sorted Array

Array is sorted but rotated: `[4, 5, 6, 7, 0, 1, 2]`. Key insight: one half is always sorted. Identify the sorted half, decide where the target lies.

```python
def search_rotated(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        if arr[lo] <= arr[mid]:       # left half is sorted
            if arr[lo] <= target < arr[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                         # right half is sorted
            if arr[mid] < target <= arr[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
```

Time: O(log n). Common interview problem.

**Common mistake — applying standard binary search to rotated input:** Standard binary search silently produces wrong answers. It does not raise an error — it confidently returns -1 or a wrong index.

> 📝 **Practice:** [Q12 — Search Rotated Array](./practice.md#q12--search-in-rotated-sorted-array) · [Q13 — Find Min in Rotated](./practice.md#q13--find-minimum-in-rotated-sorted-array)

<a id="2d-matrix"></a>
## 2D Matrix Search

Matrix where rows and columns are sorted. Two approaches:

1. **Flatten + binary search** — treat m×n matrix as 1D array of size m*n. Time: O(log(mn))
2. **Start top-right, eliminate rows/columns** — if value is too large, move left; too small, move down. Time: O(n + m)

> 📝 **Practice:** [Q14 — Search 2D Matrix](./practice.md#q14--search-a-2d-matrix) · [Q15 — Search 2D Matrix II](./practice.md#q15--search-a-2d-matrix-ii-sorted-rowscols)

> [↑ Back to Top](#top)

<a id="9-real-world"></a>
# 9. Real-World Impact

Scout transitions from training to field operations and finds binary search principles everywhere in production systems.

## Databases

Index-based lookup in B-trees — every `WHERE` clause on an indexed column uses binary search internally. A query on 10 million rows completes in ~23 comparisons.

## File Systems

Directory lookups use sorted structures. `ls` on a directory with 100,000 files uses binary search on inodes.

## Search Engines

Inverted indexes enable fast retrieval. Google's index maps every word to sorted document lists — intersection uses binary merge.

## Networking

Routing tables use longest-prefix match — a form of binary search on IP ranges.

Binary search principles power every indexing structure in computing.

> [↑ Back to Top](#top)

<a id="summary"></a>
## 🔥 Summary

```
Quick Reference

+------------------+------------------+------------------+
| Template         | Condition        | Loop exits when  |
+------------------+------------------+------------------+
| Exact match      | lo <= hi         | lo > hi or found |
| Leftmost bound   | lo < hi          | lo == hi         |
| Avoid inf loop   | lo < hi - 1      | hi == lo + 1     |
+------------------+------------------+------------------+

+------------------+------------------+
| Situation        | Pointer move     |
+------------------+------------------+
| arr[mid] < tgt   | lo = mid + 1     |
| arr[mid] > tgt   | hi = mid - 1     |
| mid might be ans | hi = mid         |
| mid can't be ans | lo = mid + 1     |
+------------------+------------------+
```

| Concept | Key Takeaway |
|---------|-------------|
| Linear search | O(n) — unavoidable on unsorted data |
| Binary search | O(log n) — requires sorted + random access |
| Template choice | `<=` for exact, `<` for boundary, `< hi-1` for safety |
| Variations | First/last occurrence, lower/upper bound |
| Search on answer | Binary search on value space, not array index |
| Rotated array | One half always sorted — identify it |
| 2D matrix | Flatten or start top-right |

**When NOT to use binary search:**
- Data not sorted
- Data changes frequently (re-sorting cost outweighs search savings)
- Structure does not allow random access (linked list)
- Sorting just to binary search may not be optimal for single queries

**Space complexity:**
- Iterative binary search: O(1)
- Recursive binary search: O(log n) stack space

**Performance thinking:** If n = 10⁶ and you search repeatedly, sort once O(n log n) then search O(log n) each time. Often worth preprocessing.

**Common mistake — DFS for shortest path:** DFS returns the FIRST path, not the shortest. Use BFS (or Dijkstra for weighted graphs) for minimum steps.

Searching is where logic precision matters most. Mastering it prepares Scout for two pointers, sliding window, heaps, greedy problems, and optimization.

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [05_sorting → theory.md](../05_sorting/theory.md) |
| ➡ Next Module | [07_linked_list → theory.md](../07_linked_list/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[05 Sorting →](../05_sorting/theory.md) · [07 Linked List →](../07_linked_list/theory.md) · [13 Binary Search →](../13_binary_search/theory.md) · [11 Two Pointers →](../11_two_pointers/theory.md)

**Jump to specific topics in other files:**
- Binary search deep patterns → [13_binary_search § theory.md](../13_binary_search/theory.md)
- Two pointers (often after sorting) → [11_two_pointers § theory.md](../11_two_pointers/theory.md)
- B-tree index lookup → [15_binary_search_trees § theory.md](../15_binary_search_trees/theory.md)
- Sliding window (search variant) → [12_sliding_window § theory.md](../12_sliding_window/theory.md)

> [↑ Back to Top](#top)
