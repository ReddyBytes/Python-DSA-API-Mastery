<a id="top"></a>

# Searching in Python — Complete Theory (Zero to Advanced)

> Searching is not just about finding an element.
> It is about choosing the right strategy based on data order and constraints.

Every search problem begins with one critical question:

Is the data sorted?

Your entire approach depends on this.

## 📖 Table of Contents

1. [The Two Worlds of Searching](#1-the-two-worlds-of-searching)
2. [Linear Search — The Baseline Strategy](#2-linear-search--the-baseline-strategy)
3. [Why Binary Search Is Powerful](#3-why-binary-search-is-powerful)
4. [Binary Search — Core Conditions](#4-binary-search--core-conditions)
5. [Common Binary Search Mistakes](#5-common-binary-search-mistakes)
6. [Variations of Binary Search](#6-variations-of-binary-search)
7. [Search on Answer (Advanced Pattern)](#7-search-on-answer-advanced-pattern)
8. [Time Complexity Comparison](#8-time-complexity-comparison)
9. [Searching in Rotated Sorted Array](#9-searching-in-rotated-sorted-array)
10. [Searching in 2D Matrix](#10-searching-in-2d-matrix)
11. [Searching in Real Systems](#11-searching-in-real-systems)
12. [When NOT to Use Binary Search](#12-when-not-to-use-binary-search)
13. [Space Complexity](#13-space-complexity)
14. [Performance Thinking](#14-performance-thinking)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
binary search mechanics · O(log n) · monotonic property · loop invariant

**Should Learn** — Important for real projects, comes up regularly:
first/last occurrence · lower/upper bound · search on answer pattern

**Good to Know** — Useful in specific situations, not always tested:
search in rotated sorted array · search in 2D matrix

**Reference** — Know it exists, look up syntax when needed:
exponential search · interpolation search · jump search

<a id="1-the-two-worlds-of-searching"></a>

# 1. The Two Worlds of Searching

Searching problems fall into two major categories:

1. Searching in Unsorted Data
2. Searching in Sorted Data

If unsorted → options are limited.
If sorted → powerful optimizations become available.

Understanding this distinction is fundamental.

> [↑ Back to Top](#top)

<a id="2-linear-search--the-baseline-strategy"></a>

# 2. Linear Search — The Baseline Strategy

When data is unsorted:

You must scan one-by-one.

Picture this. You come home, reach into your pocket — no keys. You start checking every
drawer in the house, one by one. Kitchen drawer... nope. Junk drawer... nope. Bedside
table drawer... THERE they are.

That is linear search. You check every single item until you find what you want (or run
out of places to look).

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

The harsh truth: whether you find your keys on step 1 or step 7, the worst case is always going through everything. That is O(n).

Best case? O(1) — the first drawer you check.
Average case? O(n/2) — which we still call O(n).

Linear search does not care whether the data is sorted or random. It just walks forward until it finds the item or falls off the end.

```python
def linear_search(arr, target):
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1
```

Time Complexity: O(n)
Best Case: O(1)
Worst Case: O(n)

Linear search is unavoidable in unsorted arrays.

When should you use it? When the array is small, unsorted, or you only search once.
When should you NOT use it? When the array is large and sorted — that is where binary search comes in.

**Common mistake — linear search in a loop:** Using `if x in list` inside a loop is O(n) per call, making the whole loop O(n²). If you need repeated membership tests, convert the list to a `set` first for O(1) average lookups. Only fall back to linear search when the data is genuinely unsorted and you search it just once.

> 📝 **Practice:** [Q1 — Linear Search — Return Index](./practice.md#q1--linear-search--return-index) · [Q2 — All Occurrences](./practice.md#q2--linear-search--all-occurrences) · [Q8 — 2D Linear Search](./practice.md#q8--linear-search-on-2d-list)

> [↑ Back to Top](#top)

<a id="3-why-binary-search-is-powerful"></a>

# 3. Why Binary Search Is Powerful

Binary search only works if data is sorted.

Key idea: reduce search space by half each step.

You are looking up "Williams" in a phone book (yes, a physical phone book).

Do you start at page 1 and read every name? Of course not. You flip to the middle — let's say you land on "Morrison." You know Williams comes after Morrison alphabetically, so you throw away the entire first half of the book. You are now searching half the remaining pages.

That is binary search. But here is the critical insight:

> Binary search only works because the phone book is SORTED.

If every phone book entry were in random order, opening to the middle tells you nothing. "Morrison" could have been placed anywhere. You cannot throw away half the book because the second half might contain entries starting with A through L.

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

Binary search is elimination. Every comparison lets you confidently throw away half the remaining candidates. Unsorted data never lets you do that.

## Visual: Binary Search Step by Step

Let's search for **37** in this sorted array:

```
Index: [0]  [1]  [2]  [3]  [4]  [5]  [6]  [7]  [8]  [9]
Value:   1    5   12   18   23   37   44   57   62   89
```

We start with `lo = 0`, `hi = 9`.

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

Three comparisons to search 10 elements. Linear search would have needed 6.
For an array of 1 billion elements, binary search needs at most 30 comparisons.

Time: O(log n)

> 📝 **Practice:** [Q3 — Binary Search Iterative](./practice.md#q3--binary-search--iterative) · [Q4 — Binary Search Recursive](./practice.md#q4--binary-search--recursive)

> [↑ Back to Top](#top)

<a id="4-binary-search--core-conditions"></a>

# 4. Binary Search — Core Conditions

Binary search requires:

- Sorted data
- Random access (arrays, not linked lists)

Basic structure:

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

**Why do we check mid BEFORE moving?**

We check `arr[mid] == target` first so we do not miss it. If we moved pointers first, we might skip right over the answer.

**What happens if lo > hi?**

The window has collapsed — we have exhausted all candidates without finding the target. Return -1.

**Common mistake — overflow in midpoint:** In Python, `(lo + hi) // 2` is safe because Python integers have arbitrary precision. In Java or C++, this overflows for large indices. Prefer `lo + (hi - lo) // 2` in all languages — it is safe everywhere and signals to interviewers that you know about this issue.

```
Regular:   mid = (lo + hi) // 2
Safe:      mid = lo + (hi - lo) // 2

Proof they are equal:
  lo + (hi - lo) // 2
= lo + hi/2 - lo/2
= lo/2 + hi/2
= (lo + hi) / 2  ✓

The intermediate value (hi - lo) is always <= hi,
bounded by the array size — no overflow risk.
```

**Common mistake — missing post-loop verification:** After a `while lo < hi` loop, `lo` points to the convergence point but that element may not equal the target. Always verify: `if lo < len(arr) and arr[lo] == target: return lo` — otherwise return -1. Returning `lo` unconditionally gives wrong answers when the target is absent.

> 📝 **Practice:** [Q6 — Insertion Point](./practice.md#q6--insertion-point) · [Q7 — When to Choose What](./practice.md#q7--complexity-analysis--when-to-choose-what)

> [↑ Back to Top](#top)

<a id="5-common-binary-search-mistakes"></a>

# 5. Common Binary Search Mistakes

Binary search is simple in concept, but error-prone in implementation. Even Jon Bentley reported that only about 10% of professional programmers could write a correct binary search on the first try.

The main failure modes:

1. Infinite loop (wrong boundary updates)
2. Using `lo < hi` instead of `<=` for exact match
3. Overflow in other languages (lo + hi issue)
4. Off-by-one errors
5. Forgetting sorted condition

## Visual: The Three Templates

Binary search has one of the most confusing sets of variations in DSA. Here is how to choose:

### Template 1: `lo <= hi` — Exact Match Search

Use this when you want to find a specific value and return its index.

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

The `lo <= hi` condition means we still check when the window is a single element (lo == hi). This is correct for exact match — that single element might be our answer.

### Template 2: `lo < hi` — Boundary Finding

Use this when you want to find the LEFTMOST or RIGHTMOST position (first occurrence, insertion point, etc.).

```
Invariant: the answer is always inside [lo, hi]

Loop exits when:  lo == hi  (they converge ON the answer)

 lo=0                    hi=9
  ├────────────────────────┤
  At convergence: lo == hi == answer position
```

Key difference: when `arr[mid]` could be the answer, set `hi = mid` (not `mid-1`) because you do not want to exclude mid from consideration.

```python
# Find leftmost position where arr[i] >= target
def lower_bound(arr, target):
    lo, hi = 0, len(arr)           # hi = len(arr) — one past the end!
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid               # mid might be the answer, keep it
    return lo                      # lo == hi at this point
```

### Template 3: `lo < hi - 1` — Avoids Infinite Loop Trap

Use this when `mid` is assigned to `lo` (not `mid+1`). Without the `lo < hi - 1` guard, you get an infinite loop.

```
The danger:
  lo=5, hi=6
  mid = (5+6)//2 = 5
  If we set lo = mid = 5... lo never advances!
  We are stuck forever.

The fix:
  Loop condition: lo < hi - 1
  This ensures at least 2 elements remain, so mid is always BETWEEN lo and hi.

 lo   mid   hi
  ├────┼─────┤
  This gap guarantees mid != lo when using integer division
```

When the loop exits with `lo < hi - 1` as the condition, you have `hi = lo + 1`. Then manually check both `arr[lo]` and `arr[hi]` after the loop.

## Visual: Off-by-One Pointer Rules

This trips up nearly everyone. Here is the rule in plain English:

**When to use `lo = mid + 1`:** When you are CERTAIN the answer is NOT at mid (you have already checked it and it is too small).

```
arr[mid] < target:
  mid is definitely not the answer
  Everything ≤ mid is too small
  Safe to move lo PAST mid

  ... [mid] [mid+1] ...
         ✗    ← lo starts here
```

**When to use `lo = mid`:** When mid COULD be the answer. Do not skip it. (Only safe if loop is `lo < hi - 1`.)

**When to use `hi = mid - 1`:** When arr[mid] is too large AND you are doing exact match search.

```
arr[mid] > target:
  mid is definitely not the answer
  Everything ≥ mid is too large

  ... [mid-1] [mid] ...
          ↑     ✗
       hi goes here
```

**When to use `hi = mid`:** When doing boundary finding and mid might be the answer.

```
arr[mid] >= target:
  mid satisfies the condition but there might be an earlier one
  Keep mid in the search space

  ... [mid-1] [mid] ...
               ↑
            hi stays here
```

**Common mistake — infinite loop with `lo = mid`:** When `lo` and `hi` are adjacent (`lo=5, hi=6`), `mid = (5+6)//2 = 5`. Setting `lo = mid = 5` means `lo` never advances — infinite loop. Fix: use Template 1 with `lo = mid + 1`, or use Template 3 with the `lo < hi - 1` guard.

```
Two-element proof that Template 1 always terminates:

arr = [1, 2], target = 2

Iteration 1:
  lo=0, hi=1, mid=0, arr[0]=1 < 2 -> lo = mid+1 = 1

Iteration 2:
  lo=1, hi=1, mid=1, arr[1]=2 == target -> return 1  ✓

Template 1 ALWAYS terminates because:
  - When arr[mid] < target: lo = mid+1 -> lo strictly increases
  - When arr[mid] > target: hi = mid-1 -> hi strictly decreases
  - Either way, the interval [lo, hi] strictly shrinks each iteration.
```

**Common mistake — wrong template for boundary search:** The "find any" template returns ANY match. The "find leftmost" template returns the FIRST match. Using exact-match template when asked for first/last occurrence returns the wrong index (whichever element happens to be in the middle of the duplicates block).

```
arr = [1, 1, 1, 2, 2, 2, 3, 3, 3]
idx:   0  1  2  3  4  5  6  7  8

Exact-match template, target=2:
  lo=0, hi=8, mid=4, arr[4]=2 -> return 4 immediately.
  But the first occurrence is at index 3!
```

Fix: when you find a match, record `result = mid` and keep searching left (`hi = mid - 1`) to find earlier occurrences.

**Common mistake — what the pointers mean after the loop:** After Template 1 exits without finding the target:

```
After Template 1 loop (while lo <= hi) exits WITHOUT finding target:

    ...elements < target... | ...elements > target...
                            ^hi     ^lo

    lo  = index of first element > target (or len(arr) if target > all)
    hi  = index of last element < target  (or -1 if target < all)

    Return lo  when you want: insertion point, ceiling
    Return hi  when you want: floor, last element < target
    Never return lo directly as "found" — always verify arr[lo] == target first
```

> 📝 **Practice:** [Q25 — Off-by-One Bug Hunt](./practice.md#q25--off-by-one-bug-hunt)

> [↑ Back to Top](#top)

<a id="6-variations-of-binary-search"></a>

# 6. Variations of Binary Search

Binary search is rarely asked directly.
Variations are common.

## First Occurrence

Find first index of target in sorted array.

Key idea: when found, move left to check earlier occurrence.

```python
def find_first(arr, target):
    lo, hi = 0, len(arr) - 1
    result = -1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            result = mid
            hi = mid - 1    # keep searching left for an earlier one
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return result
```

## Last Occurrence

When found, move right to check later occurrence.

```python
def find_last(arr, target):
    lo, hi = 0, len(arr) - 1
    result = -1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            result = mid
            lo = mid + 1    # keep searching right for a later one
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return result
```

## Lower Bound

First element ≥ target.

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

These are extremely common in interviews.

**Common mistake — bisect_left vs bisect_right for duplicates:** `bisect_left` returns the index of the first occurrence; `bisect_right` returns the index one past the last occurrence. Using them interchangeably with duplicate values causes off-by-one errors.

```
arr = [1, 1, 1, 2, 2, 2, 3, 3, 3]

bisect_left(arr, 2)  = 3   → index of FIRST 2
bisect_right(arr, 2) = 6   → index AFTER last 2

Count of 2s = bisect_right - bisect_left = 6 - 3 = 3  ✓

WRONG: bisect_right(arr, 2) returns 6; arr[6] = 3, not 2.
       Never use arr[bisect_right(...)] to check existence.
RIGHT: idx = bisect_left(arr, target)
       return idx < len(arr) and arr[idx] == target
```

> 📝 **Practice:** [Q9 — First Occurrence](./practice.md#q9--first-occurrence) · [Q10 — Last Occurrence](./practice.md#q10--last-occurrence) · [Q11 — Count in Sorted Array](./practice.md#q11--count-of-target-in-sorted-array) · [Q5 — Count via bisect](./practice.md#q5--count-occurrences-in-sorted-array)

> [↑ Back to Top](#top)

<a id="7-search-on-answer-advanced-pattern"></a>

# 7. Search on Answer (Advanced Pattern)

Instead of searching in array, you search in answer space.

Your friend thinks of a number between 1 and 1,000,000. You do not search through a list of numbers — you binary search on the VALUE SPACE. "Is it more or less than 500,000?" Each question halves the search space. In 20 questions, you can find any number.

Many binary search problems are NOT about searching a position in an array — they are about searching the ANSWER ITSELF.

Example: find minimum value that satisfies a condition.

The condition is monotonic:

```
False False False True True True
```

Binary search can find the transition point.

## Visual: Koko Eating Bananas

Koko has piles of bananas: `[3, 6, 7, 11]`. She has 8 hours to eat them all. What is the minimum speed (bananas/hour)?

At speed `k`, pile of size `p` takes `ceil(p/k)` hours.

If speed `k` works, then speed `k+1` also works. The "works" condition is monotone.

```
Speed:   1    2    3    4    5    6    7    8    9   10   11
Works?:  ✗    ✗    ✗    ✗    ✗    ✗    ✗    ✓    ✓    ✓    ✓
                                             ↑
                                      first valid speed
```

Wait — this trace uses speed 8 as first valid. Let's trace the binary search:

```
lo=1, hi=11

Round 1: mid=6
  Speed 6: ceil(3/6)+ceil(6/6)+ceil(7/6)+ceil(11/6) = 1+1+2+2 = 6 hours ≤ 8 ✓
  Works! But maybe slower speed also works. hi = mid = 6

Round 2: lo=1, hi=6, mid=3
  Speed 3: 1+2+3+4 = 10 hours > 8 ✗
  Too slow. lo = mid + 1 = 4

Round 3: lo=4, hi=6, mid=5
  Speed 5: 1+2+2+3 = 8 hours ≤ 8 ✓
  Works! hi = mid = 5

Round 4: lo=4, hi=5, mid=4
  Speed 4: 1+2+2+3 = 8 hours ≤ 8 ✓
  Works! hi = mid = 4

lo == hi == 4. Answer: speed 4.
```

We searched on the SPEED, not on a position in the array.

The template for "search on answer":

```
1. Identify the range [lo, hi] for the answer
2. Write a function: can_solve(k) → True/False
3. Make sure the True/False values are monotone (all False then all True)
4. Binary search for the boundary
```

```python
def binary_search_on_answer(lo, hi, condition):
    """
    Find the minimum value in [lo, hi] where condition(value) is True.
    Requires: condition is monotone — False below answer, True at and above.
    """
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if condition(mid):
            hi = mid       # mid satisfies, look for smaller
        else:
            lo = mid + 1   # mid doesn't satisfy, need larger
    return lo  # lo == hi == minimum satisfying value
```

This pattern appears in:

- Capacity problems
- Scheduling
- Minimum speed problems
- Allocation problems

Understanding monotonic behavior is critical.

**Common mistake — searching array index instead of answer range:** For "minimize X such that condition(X)" problems, beginners try to binary search on the array index. The search space is the VALUE of X (e.g., speed from 1 to max(piles)), not a position in the array. Identify the range `[lo, hi]` for the answer value, write `can_solve(k)`, verify it is monotone, then apply the template above.

> 📝 **Practice:** [Q18 — Integer Sqrt](./practice.md#q18--square-root-via-binary-search) · [Q19 — Koko Eating Bananas](./practice.md#q19--koko-eating-bananas) · [Q20 — Ship Packages](./practice.md#q20--ship-packages-within-d-days) · [Q22 — Smallest Divisor](./practice.md#q22--smallest-divisor-given-threshold) · [Q24 — Allocate Min Pages](./practice.md#q24--allocate-minimum-pages)

> [↑ Back to Top](#top)

<a id="8-time-complexity-comparison"></a>

# 8. Time Complexity Comparison

| Method | Requirement | Time |
|--------|------------|------|
| Linear | None | O(n) |
| Binary | Sorted | O(log n) |

Binary search is exponentially faster for large n.

Example:

n = 1,000,000

Linear → 1,000,000 checks
Binary → ~20 checks

Difference is massive.

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

Time:  O(log n)
Space: O(1)
```

> 📝 **Practice:** [Q7 — Complexity Analysis](./practice.md#q7--complexity-analysis--when-to-choose-what)

> [↑ Back to Top](#top)

<a id="9-searching-in-rotated-sorted-array"></a>

# 9. Searching in Rotated Sorted Array

Array is sorted but rotated.

Example:

```
[4, 5, 6, 7, 0, 1, 2]
```

Modified binary search required.

Key idea: one half is always sorted. Identify sorted half. Decide where target lies.

```python
def search_rotated(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        # Determine which half is sorted
        if arr[lo] <= arr[mid]:       # left half is sorted
            if arr[lo] <= target < arr[mid]:
                hi = mid - 1         # target is in sorted left half
            else:
                lo = mid + 1         # target is in right half
        else:                         # right half is sorted
            if arr[mid] < target <= arr[hi]:
                lo = mid + 1         # target is in sorted right half
            else:
                hi = mid - 1         # target is in left half
    return -1
```

**Common mistake — applying standard binary search to unsorted/rotated input:** Standard binary search silently produces wrong answers on unsorted data. It does not raise an error — it confidently returns -1 or a wrong index. For rotated arrays, use the modified template above that identifies which half is sorted at each step. For genuinely unsorted arrays, there is no shortcut: use linear search or sort first.

Time: O(log n)

Common interview problem.

> 📝 **Practice:** [Q12 — Search Rotated Array](./practice.md#q12--search-in-rotated-sorted-array) · [Q13 — Find Min in Rotated](./practice.md#q13--find-minimum-in-rotated-sorted-array)

> [↑ Back to Top](#top)

<a id="10-searching-in-2d-matrix"></a>

# 10. Searching in 2D Matrix

Matrix where:

- Rows sorted
- Columns sorted

Approaches:

1. Flatten + binary search
2. Start top-right and eliminate rows/columns

Time: O(n + m) or O(log(nm))

> 📝 **Practice:** [Q14 — Search 2D Matrix](./practice.md#q14--search-a-2d-matrix) · [Q15 — Search 2D Matrix II](./practice.md#q15--search-a-2d-matrix-ii-sorted-rowscols)

> [↑ Back to Top](#top)

<a id="11-searching-in-real-systems"></a>

# 11. Searching in Real Systems

Searching appears in:

## Databases

Index-based lookup → binary search in B-trees.

## File Systems

Directory lookups.

## Search Engines

Index structures enable fast retrieval.

## Networking

Routing tables.

Binary search principles power indexing structures.

> [↑ Back to Top](#top)

<a id="12-when-not-to-use-binary-search"></a>

# 12. When NOT to Use Binary Search

Avoid when:

- Data not sorted
- Data changes frequently
- Structure does not allow random access (linked list)

Sorting just to binary search may not always be optimal.

**Common mistake — DFS for shortest path:** When searching for the shortest path in a graph, DFS is wrong. DFS returns the FIRST path it finds, which is not necessarily shortest. BFS explores layer by layer and guarantees the first time it reaches the destination is via the shortest path. Use BFS (or Dijkstra for weighted graphs) whenever the problem asks for minimum steps or hops.

> [↑ Back to Top](#top)

<a id="13-space-complexity"></a>

# 13. Space Complexity

Iterative binary search: O(1)

Recursive binary search: O(log n) stack space

Be aware of this distinction.

> 📝 **Practice:** [Q4 — Recursive Binary Search](./practice.md#q4--binary-search--recursive)

> [↑ Back to Top](#top)

<a id="14-performance-thinking"></a>

# 14. Performance Thinking

If n = 10⁶:

Linear search: too slow if repeated many times.

Binary search: very efficient.

Repeated searching scenario:
Sort once → O(n log n)
Search multiple times → O(log n) each

Often worth preprocessing.

> [↑ Back to Top](#top)

# 📌 Final Perspective

Searching is about:

- Understanding data order
- Choosing strategy
- Avoiding unnecessary scanning
- Leveraging monotonic behavior
- Minimizing comparisons

Binary search is one of the most important algorithms in computer science.

Mastering searching prepares you for:

- Two pointers
- Sliding window
- Heaps
- Greedy problems
- Many optimization problems

Searching is where logic precision matters most.

**[🏠 Back to README](../README.md)**

**Prev:** [← Sorting — Interview Q&A](../05_sorting/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md) · [Practice](./practice.md)
