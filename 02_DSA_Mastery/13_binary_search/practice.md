# 📝 Binary Search — Practice Problems (25 Questions)

> Work through these in order. Basic locks in the mechanics. Intermediate builds
> the pattern library. Advanced requires combining ideas under pressure.

---

## Quick Index

### Basic (Q1–Q8)
| # | Title | Concept |
|---|-------|---------|
| [Q1](#q1) | [Classic Binary Search — Exact Match](#q1--classic-binary-search--exact-match) | Template 1: `lo <= hi` |
| [Q2](#q2) | [Binary Search — Recursive](#q2--binary-search--recursive) | Recursive call stack |
| [Q3](#q3) | [Search Insert Position](#q3--search-insert-position) | Where does target belong? |
| [Q4](#q4) | [bisect_left vs bisect_right](#q4--bisect_left-vs-bisect_right) | Module mechanics |
| [Q5](#q5) | [Count Occurrences with bisect](#q5--count-occurrences-with-bisect) | `bisect_right − bisect_left` |
| [Q6](#q6) | [First Occurrence of Target](#q6--first-occurrence-of-target) | Record ans, search left |
| [Q7](#q7) | [Last Occurrence of Target](#q7--last-occurrence-of-target) | Record ans, search right |
| [Q8](#q8) | [Floor and Ceiling](#q8--floor-and-ceiling) | bisect pointer position |

### Intermediate (Q9–Q20)
| # | Title | Concept |
|---|-------|---------|
| [Q9](#q9) | [Off-by-One: `lo <= hi` vs `lo < hi`](#q9--off-by-one-lo--hi-vs-lo--hi) | Loop condition choice |
| [Q10](#q10) | [Off-by-One: `mid+1` vs `mid`, `mid-1` vs `mid`](#q10--off-by-one-mid1-vs-mid-mid-1-vs-mid) | Boundary update rules |
| [Q11](#q11) | [Template Comparison — Three Templates](#q11--template-comparison--three-templates) | Side-by-side templates |
| [Q12](#q12) | [Search in Rotated Sorted Array](#q12--search-in-rotated-sorted-array) | One half always sorted |
| [Q13](#q13) | [Find Minimum in Rotated Sorted Array](#q13--find-minimum-in-rotated-sorted-array) | Compare mid to hi |
| [Q14](#q14) | [Find Peak Element](#q14--find-peak-element) | Climb the ascending slope |
| [Q15](#q15) | [Square Root via Binary Search (Integer)](#q15--square-root-via-binary-search-integer) | Maximize template |
| [Q16](#q16) | [Square Root via Binary Search (Float)](#q16--square-root-via-binary-search-float) | Epsilon-convergence |
| [Q17](#q17) | [Koko Eating Bananas](#q17--koko-eating-bananas) | Minimize: first feasible speed |
| [Q18](#q18) | [Capacity to Ship Packages](#q18--capacity-to-ship-packages) | Minimize: first feasible capacity |
| [Q19](#q19) | [Minimize Maximum (Split Array Largest Sum)](#q19--minimize-maximum-split-array-largest-sum) | Classic minimize-max |
| [Q20](#q20) | [Maximize Minimum (Allocate Minimum Pages)](#q20--maximize-minimum-allocate-minimum-pages) | Classic maximize-min |

### Advanced (Q21–Q25)
| # | Title | Concept |
|---|-------|---------|
| [Q21](#q21) | [Search in Rotated Array with Duplicates](#q21--search-in-rotated-array-with-duplicates) | Worst-case O(n) edge |
| [Q22](#q22) | [Smallest Divisor Given Threshold](#q22--smallest-divisor-given-threshold) | Ceiling-division predicate |
| [Q23](#q23) | [Find Bad Version (First True in Answer Space)](#q23--find-bad-version-first-true-in-answer-space) | Classic monotonic predicate |
| [Q24](#q24) | [Median of Two Sorted Arrays](#q24--median-of-two-sorted-arrays) | Partition binary search |
| [Q25](#q25) | [Off-by-One Bug Hunt](#q25--off-by-one-bug-hunt) | Fix four broken implementations |

---

## Basic (Q1–Q8)

---

<a id="q1"></a>
### Q1 — Classic Binary Search — Exact Match

Given a sorted array and a target, return its index. Return -1 if not found.

```
Input:  arr = [1, 3, 5, 7, 9, 11, 13],  target = 7
Output: 3

Input:  arr = [2, 4, 6, 8, 10],  target = 5
Output: -1
```

<details>
<summary>Hint</summary>

Template 1: `lo <= hi`. Mid is `lo + (hi - lo) // 2`. Three-way branch:
equal → return, too small → move `lo` right, too big → move `hi` left.

</details>

<details>
<summary>Answer</summary>

```python
def binary_search(arr: list[int], target: int) -> int:
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2      # overflow-safe
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

**Why:** `lo + (hi - lo) // 2` avoids integer overflow in C/Java (Python is immune
but writing it safely is a strong interview signal). `lo <= hi` (not `<`) is
critical — when `lo == hi` the single remaining element might be the answer.
If you write `<`, you miss it.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q2"></a>
### Q2 — Binary Search — Recursive

Implement binary search using recursion. Same signature: return index or -1.

```
Input:  arr = [2, 5, 8, 12, 16, 23, 38],  target = 23
Output: 5
```

<details>
<summary>Hint</summary>

Pass `lo` and `hi` as arguments defaulting to `0` and `len(arr) - 1`.
Base case: `lo > hi` means not found. Recursive cases match the iterative
three-way branch.

</details>

<details>
<summary>Answer</summary>

```python
def binary_search_recursive(arr: list[int], target: int,
                             lo: int = 0, hi: int = None) -> int:
    if hi is None:
        hi = len(arr) - 1
    if lo > hi:
        return -1
    mid = lo + (hi - lo) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, hi)
    else:
        return binary_search_recursive(arr, target, lo, mid - 1)
```

**Why:** Each recursive call cuts the search space in half, matching the
iterative approach exactly. The call stack depth is O(log n). The default
`hi=None` trick avoids exposing implementation details in the public
signature — callers just pass `(arr, target)`.

**Time:** O(log n) | **Space:** O(log n) call stack

</details>

---

<a id="q3"></a>
### Q3 — Search Insert Position

Given a sorted array with no duplicates and a target, return the index if found,
or the index where it would be inserted to keep the array sorted.

```
Input:  arr = [1, 3, 5, 6],  target = 5   →  Output: 2
Input:  arr = [1, 3, 5, 6],  target = 2   →  Output: 1
Input:  arr = [1, 3, 5, 6],  target = 7   →  Output: 4
```

<details>
<summary>Hint</summary>

After the standard binary search loop exits (when `lo > hi`), `lo` is the
first index where `arr[lo] >= target`. That is exactly where target belongs.

</details>

<details>
<summary>Answer</summary>

```python
def search_insert(arr: list[int], target: int) -> int:
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return lo    # lo > hi: lo is the insertion point
```

**Why:** When the loop exits, `lo` has crossed `hi` by exactly one. At that
moment `lo` points to the first position where all elements to the left are
strictly less than `target` — the correct insertion point. This is identical to
`bisect.bisect_left(arr, target)`.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q4"></a>
### Q4 — bisect_left vs bisect_right

Using Python's `bisect` module, find the first and last positions of `target`
in `arr = [1, 2, 2, 2, 3]` for `target = 2`.

```
Expected:  first = 1,  last = 3
```

<details>
<summary>Hint</summary>

`bisect_left` gives the leftmost insertion point (before existing copies).
`bisect_right` gives the rightmost insertion point (after existing copies).
The last occurrence is `bisect_right(arr, target) - 1`.

</details>

<details>
<summary>Answer</summary>

```python
import bisect

def first_last_bisect(arr: list[int], target: int) -> tuple[int, int]:
    left  = bisect.bisect_left(arr, target)
    right = bisect.bisect_right(arr, target) - 1

    if left > right or left >= len(arr) or arr[left] != target:
        return (-1, -1)    # target not present

    return (left, right)

arr = [1, 2, 2, 2, 3]
print(first_last_bisect(arr, 2))   # (1, 3)
print(first_last_bisect(arr, 5))   # (-1, -1)
```

**Why:** `bisect_left(arr, 2)` returns 1 — the first slot where 2 could be
inserted from the left. `bisect_right(arr, 2)` returns 4 — the first slot after
all the 2s. So last occurrence = 4 - 1 = 3. The guard `arr[left] != target`
handles the case where target is absent but `left` points to a different value.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q5"></a>
### Q5 — Count Occurrences with bisect

Given a sorted array, count how many times `target` appears. Use the `bisect`
module.

```
Input:  arr = [1, 2, 2, 2, 2, 3],  target = 2
Output: 4
```

<details>
<summary>Hint</summary>

`bisect_right - bisect_left` gives the count in one line. No looping needed.

</details>

<details>
<summary>Answer</summary>

```python
import bisect

def count_occurrences(arr: list[int], target: int) -> int:
    return bisect.bisect_right(arr, target) - bisect.bisect_left(arr, target)
```

**Why:** `bisect_left` returns the index of the first element `>= target`.
`bisect_right` returns the index of the first element `> target`. The range
`[bisect_left, bisect_right)` is exactly the span of equal elements. Subtracting
gives the count in O(log n) — no scan needed.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q6"></a>
### Q6 — First Occurrence of Target

In a sorted array with duplicates, return the index of the first occurrence of
`target`. Return -1 if absent. Do not use the `bisect` module.

```
Input:  arr = [1, 2, 4, 4, 4, 4, 7],  target = 4
Output: 2
```

<details>
<summary>Hint</summary>

When `arr[mid] == target`, record `mid` in a result variable and then push `hi`
left (set `hi = mid - 1`) to keep searching for an earlier match. Do NOT return
immediately.

</details>

<details>
<summary>Answer</summary>

```python
def first_occurrence(arr: list[int], target: int) -> int:
    lo, hi = 0, len(arr) - 1
    result = -1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            result = mid       # candidate found — but keep going left
            hi = mid - 1
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return result
```

**Why:** The key insight is to NOT return on first match. Instead, record the
index as the current best answer and shrink the window leftward with
`hi = mid - 1`. Any earlier match will overwrite `result`. After the loop,
`result` holds the leftmost occurrence (or -1 if never matched).

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q7"></a>
### Q7 — Last Occurrence of Target

In a sorted array with duplicates, return the index of the last occurrence of
`target`. Return -1 if absent. Do not use the `bisect` module.

```
Input:  arr = [1, 2, 4, 4, 4, 4, 7],  target = 4
Output: 5
```

<details>
<summary>Hint</summary>

Mirror of Q6. When `arr[mid] == target`, record `mid` and push `lo` right
(`lo = mid + 1`) to search for a later match.

</details>

<details>
<summary>Answer</summary>

```python
def last_occurrence(arr: list[int], target: int) -> int:
    lo, hi = 0, len(arr) - 1
    result = -1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            result = mid       # candidate — keep going right
            lo = mid + 1
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return result
```

**Why:** Symmetric to `first_occurrence`. When a match is found, we push `lo`
rightward so the search continues in the right half. Each later match overwrites
`result` with a larger index. After exhausting all possibilities, `result` is
the rightmost occurrence.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q8"></a>
### Q8 — Floor and Ceiling

Given a sorted array and a target, return `(floor, ceiling)` where:
- floor = largest element `<= target` (or `None` if all elements are larger)
- ceiling = smallest element `>= target` (or `None` if all elements are smaller)

```
Input:  arr = [1, 3, 5, 7, 9],  target = 6
Output: (5, 7)

Input:  arr = [1, 3, 5, 7, 9],  target = 5
Output: (5, 5)
```

<details>
<summary>Hint</summary>

`bisect_left(arr, target)` gives the ceiling index (first element `>= target`).
The floor is one position before it.

</details>

<details>
<summary>Answer</summary>

```python
import bisect

def floor_ceiling(arr: list[int], target: int) -> tuple:
    idx = bisect.bisect_left(arr, target)   # first index where arr[i] >= target

    ceil_val = arr[idx] if idx < len(arr) else None
    floor_val = arr[idx - 1] if idx > 0 else None

    return (floor_val, ceil_val)
```

**Why:** `bisect_left` returns `i` such that all elements before `i` are
`< target` and `arr[i] >= target`. So `arr[i]` is the ceiling (smallest
element `>= target`). The floor is the element just before it: `arr[i-1]`,
which is the largest element `< target`. If target is present, `arr[i] == target`
so floor equals ceiling.

**Time:** O(log n) | **Space:** O(1)

</details>

---

## Intermediate (Q9–Q20)

---

<a id="q9"></a>
### Q9 — Off-by-One: `lo <= hi` vs `lo < hi`

Explain the difference between `while lo <= hi` and `while lo < hi`. When does
each one cause a bug? Give a concrete failing test case for each misuse.

<details>
<summary>Hint</summary>

Think about the single-element window `lo == hi`. Does your loop inspect it?
What happens in Template 2 (left-boundary) if you use `lo <= hi` with `hi = mid`?

</details>

<details>
<summary>Answer</summary>

```python
# BUG: using `lo < hi` for exact-match search
def search_broken(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo < hi:              # exits when lo == hi — never checks last element
        mid = lo + (hi - lo) // 2
        if arr[mid] == target: return mid
        elif arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1

# Test: [7], target = 7 → returns -1 (BUG: should return 0)
print(search_broken([7], 7))    # -1 — wrong

# BUG: using `lo <= hi` in left-boundary pattern with `hi = mid`
def left_bound_broken(arr, target):
    lo, hi = 0, len(arr)
    while lo <= hi:             # lo can equal hi; if hi = mid = lo, infinite loop
        mid = lo + (hi - lo) // 2
        if arr[mid] < target: lo = mid + 1
        else: hi = mid          # hi never goes below lo → infinite loop when lo==hi
    return lo

# Any call → hangs forever
```

**Why:**
- Exact-match uses `lo <= hi` because `lo == hi` is a valid single-element
  search space that must be checked.
- Left/right-boundary patterns use `lo < hi` because `hi = mid` (not `mid-1`)
  means the window shrinks by at least one only when `lo < hi`. If `lo == hi`,
  `mid == lo` and `hi = mid` doesn't shrink anything — infinite loop.

**Rule:** Use `lo <= hi` when you can exit immediately on match.
Use `lo < hi` when the answer is the pointer position after the loop.

**Time:** O(1) for analysis | **Space:** O(1)

</details>

---

<a id="q10"></a>
### Q10 — Off-by-One: `mid+1` vs `mid`, `mid-1` vs `mid`

Explain when to use `lo = mid + 1` vs `lo = mid`, and `hi = mid - 1` vs
`hi = mid`. What goes wrong if you choose incorrectly?

<details>
<summary>Hint</summary>

The rule is: if `mid` is confirmed not the answer, skip it (`mid+1` or `mid-1`).
If `mid` could still be the answer, preserve it (`mid`).

</details>

<details>
<summary>Answer</summary>

```python
# Case A: mid is CONFIRMED not the answer → skip it
def exact_match(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target: return mid
        elif arr[mid] < target: lo = mid + 1   # mid is < target, definitely not answer
        else:                   hi = mid - 1   # mid is > target, definitely not answer

# Case B: mid COULD be the answer (first-True pattern)
def first_true(arr, target):
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] < target:
            lo = mid + 1   # mid is too small, skip it
        else:
            hi = mid       # mid >= target, could be the leftmost — KEEP it

# BUG: using hi = mid - 1 in first-True pattern
def first_true_broken(arr, target):
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] < target: lo = mid + 1
        else: hi = mid - 1    # BUG: discards the answer when arr[mid] == target

# arr = [1, 2, 3], target = 3
# Step: lo=0, hi=3, mid=1, arr[1]=2 < 3 → lo=2
# Step: lo=2, hi=3, mid=2, arr[2]=3 >= 3 → hi = 1 — now lo(2) > hi(1), exits
# Returns lo=2 but arr[2]=3 was the answer — wait, actually returns 2 which IS correct...
# Real bug appears when target is exactly at mid and hi=mid-1 skips it:
# arr = [3], target = 3 → lo=0, hi=1, mid=0, arr[0]=3 >= 3 → hi = -1, loop exits
# Returns lo=0 — actually correct by accident but the invariant is broken
```

**Rule summary:**
- `lo = mid + 1`: `mid` is confirmed too small, skip it.
- `hi = mid - 1`: `mid` is confirmed too large, skip it.
- `lo = mid`: `mid` works, maybe something larger works better (maximize pattern).
- `hi = mid`: `mid` works, maybe something smaller works better (minimize pattern).

**Time:** O(1) for analysis | **Space:** O(1)

</details>

---

<a id="q11"></a>
### Q11 — Template Comparison — Three Templates

Implement all three binary search templates for the same problem: find the first
index `i` where `arr[i] >= target` in a sorted array. Show that all three give
the same result.

```
Input:  arr = [1, 3, 3, 5, 7],  target = 3
Output: 1   (first index where arr[i] >= 3)
```

<details>
<summary>Hint</summary>

Template 1 (`lo <= hi`) returns immediately on match. Template 2 (`lo < hi`,
`hi = mid`) preserves mid as candidate. Template 3 uses `bisect_left` directly.
All three should converge on the same index.

</details>

<details>
<summary>Answer</summary>

```python
import bisect

# Template 1: Exact-match style adapted for left-boundary
def t1_left_boundary(arr: list[int], target: int) -> int:
    lo, hi = 0, len(arr) - 1
    result = len(arr)          # default: insertion after end
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] >= target:
            result = mid       # mid is a candidate — keep searching left
            hi = mid - 1
        else:
            lo = mid + 1
    return result

# Template 2: Left-boundary canonical form
def t2_left_boundary(arr: list[int], target: int) -> int:
    lo, hi = 0, len(arr)       # hi is exclusive upper bound
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid           # arr[mid] >= target: preserve as candidate
    return lo                  # lo == hi at the answer

# Template 3: bisect module
def t3_bisect(arr: list[int], target: int) -> int:
    return bisect.bisect_left(arr, target)

arr = [1, 3, 3, 5, 7]
for t in [t1_left_boundary, t2_left_boundary, t3_bisect]:
    print(t(arr, 3))   # all print 1
```

**Why:** All three implement the same invariant: find the leftmost index where
`arr[i] >= target`. Template 1 uses an explicit `result` variable to track the
best candidate. Template 2 uses the invariant `hi` always points to a valid
candidate or past the end. Template 3 is the built-in implementation.
`bisect_left` is Template 2 in C under the hood.

**Time:** O(log n) all | **Space:** O(1)

</details>

---

<a id="q12"></a>
### Q12 — Search in Rotated Sorted Array

A sorted array has been rotated at an unknown pivot. Given a target, return its
index, or -1.

```
Input:  arr = [4, 5, 6, 7, 0, 1, 2],  target = 0
Output: 4

Input:  arr = [4, 5, 6, 7, 0, 1, 2],  target = 3
Output: -1
```

<details>
<summary>Hint</summary>

At any `mid`, one of the two halves is always normally sorted. Compare `arr[lo]`
to `arr[mid]` to identify which half is sorted, then check if target falls
within that sorted half.

</details>

<details>
<summary>Answer</summary>

```python
def search_rotated(arr: list[int], target: int) -> int:
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid

        if arr[lo] <= arr[mid]:             # left half [lo..mid] is sorted
            if arr[lo] <= target < arr[mid]:
                hi = mid - 1               # target is in the sorted left half
            else:
                lo = mid + 1               # target is in the right half
        else:                               # right half [mid..hi] is sorted
            if arr[mid] < target <= arr[hi]:
                lo = mid + 1               # target is in the sorted right half
            else:
                hi = mid - 1               # target is in the left half

    return -1
```

**Why:** After any split at `mid`, exactly one side is sorted (no rotation break
inside it). Use the sorted side's boundaries to decide: if target falls within
those boundaries, search there; otherwise search the other side. The `<=` in
`arr[lo] <= arr[mid]` is critical for the single-element left-half edge case.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q13"></a>
### Q13 — Find Minimum in Rotated Sorted Array

Given a rotated sorted array with no duplicates, find the minimum element.

```
Input:  arr = [3, 4, 5, 1, 2]
Output: 1

Input:  arr = [4, 5, 6, 7, 0, 1, 2]
Output: 0
```

<details>
<summary>Hint</summary>

Compare `arr[mid]` to `arr[hi]`. If `arr[mid] > arr[hi]`, the minimum is in the
right half (the rotation break is there). Otherwise it's in the left half
(including mid).

</details>

<details>
<summary>Answer</summary>

```python
def find_min_rotated(arr: list[int]) -> int:
    lo, hi = 0, len(arr) - 1
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] > arr[hi]:
            lo = mid + 1    # minimum is in the right portion
        else:
            hi = mid        # minimum is here or to the left
    return arr[lo]          # lo == hi at the minimum
```

**Why:** The minimum is always in the "right (lower) portion" of the rotation.
Comparing `arr[mid]` to `arr[hi]` (not `arr[lo]`) is the key: if `arr[mid] >
arr[hi]`, the array decreases somewhere between `mid` and `hi`, so the minimum
is to the right. Otherwise, `arr[mid]` itself could be the minimum or the
minimum is to the left. Using `hi = mid` (not `mid-1`) preserves `mid` as a
candidate.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q14"></a>
### Q14 — Find Peak Element

A peak element is one that is strictly greater than its neighbors. Assume
`arr[-1] = arr[n] = -∞`. Find the index of any peak element.

```
Input:  arr = [1, 2, 3, 1]
Output: 2   (arr[2] = 3 is peak)

Input:  arr = [1, 2, 1, 3, 5, 6, 4]
Output: 5   (arr[5] = 6 is one valid peak)
```

<details>
<summary>Hint</summary>

Compare `arr[mid]` to `arr[mid+1]`. If `arr[mid] < arr[mid+1]`, the slope is
ascending — a peak exists to the right. Otherwise, a peak exists at mid or to
the left.

</details>

<details>
<summary>Answer</summary>

```python
def find_peak_element(arr: list[int]) -> int:
    lo, hi = 0, len(arr) - 1
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] < arr[mid + 1]:
            lo = mid + 1    # ascending slope: peak is to the right
        else:
            hi = mid        # descending slope: peak is here or to the left
    return lo               # lo == hi at a peak
```

**Why:** The invariant is: a peak always exists within `[lo, hi]`. If
`arr[mid] < arr[mid+1]`, moving right guarantees we stay on an ascending
path that must eventually peak (before falling off the array edge at `-∞`).
If `arr[mid] >= arr[mid+1]`, `mid` itself or something to its left is a peak.
Setting `hi = mid` preserves `mid` as a candidate.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q15"></a>
### Q15 — Square Root via Binary Search (Integer)

Return `floor(sqrt(n))` for a non-negative integer `n`. Do not use `math.sqrt`.

```
Input:  n = 8    →  Output: 2   (2*2=4 ≤ 8 < 3*3=9)
Input:  n = 16   →  Output: 4
Input:  n = 26   →  Output: 5
```

<details>
<summary>Hint</summary>

Use the maximize template: find the largest `k` such that `k*k <= n`. This is
"find last True" — use ceiling mid `(lo + hi + 1) // 2` to avoid infinite loop
when `lo + 1 == hi`.

</details>

<details>
<summary>Answer</summary>

```python
def integer_sqrt(n: int) -> int:
    if n < 2:
        return n
    lo, hi = 1, n // 2 + 1     # floor(sqrt(n)) <= n//2 for n >= 4
    while lo < hi:
        mid = lo + (hi - lo + 1) // 2   # ceiling mid — required for maximize
        if mid * mid <= n:
            lo = mid            # mid works, try larger
        else:
            hi = mid - 1        # mid too large, try smaller
    return lo
```

**Why:** This is the "find last True" (maximize) pattern. We want the largest
`k` where `k*k <= n`. The ceiling mid prevents an infinite loop: when
`lo=2, hi=3`, floor mid = 2, `lo = mid = 2` — no progress. Ceiling mid = 3,
either `lo` advances or `hi` retreats. Always terminates. `hi = n//2 + 1`
because `floor(sqrt(n)) <= n//2` for all `n >= 4`.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q16"></a>
### Q16 — Square Root via Binary Search (Float)

Compute `sqrt(n)` to 10 decimal places using epsilon-based binary search.

```
Input:  n = 2
Output: 1.4142135624   (matches math.sqrt to 10dp)
```

<details>
<summary>Hint</summary>

Set `lo = 0.0`, `hi = max(1.0, n)` (for `n < 1`, `sqrt(n) > n`). Loop while
`hi - lo > 1e-11`. Feasibility: `mid * mid <= n`.

</details>

<details>
<summary>Answer</summary>

```python
def float_sqrt(n: float) -> float:
    if n < 0:
        raise ValueError("Cannot take sqrt of negative number")
    if n == 0:
        return 0.0
    lo, hi = 0.0, max(1.0, float(n))   # hi = 1.0 handles n in (0, 1)
    while hi - lo > 1e-11:
        mid = (lo + hi) / 2
        if mid * mid <= n:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

import math
for x in [2, 9, 0.25, 100]:
    result = float_sqrt(x)
    assert abs(result - math.sqrt(x)) < 1e-9, f"Failed for {x}"
    print(f"sqrt({x}) = {result:.10f}")
```

**Why:** For real-number binary search, the interval `(hi - lo)` is the stopping
criterion instead of `lo < hi`. After enough iterations (or when gap < epsilon),
the answer is the midpoint. The `max(1.0, n)` bound is essential: `sqrt(0.25) =
0.5 > 0.25`, so `hi = n` would exclude the answer for `n < 1`.

**Time:** O(log(1/ε)) | **Space:** O(1)

</details>

---

<a id="q17"></a>
### Q17 — Koko Eating Bananas

Koko has `piles` of bananas and `h` hours to eat them. She eats at speed `k`
bananas/hour (one pile per hour). Find the minimum speed `k`.

```
Input:  piles = [3, 6, 7, 11],  h = 8
Output: 4

Input:  piles = [30, 11, 23, 4, 20],  h = 5
Output: 30
```

<details>
<summary>Hint</summary>

This is a "minimize: find first True" problem. Answer space: `[1, max(piles)]`.
Feasibility: can Koko finish all piles in `h` hours at speed `mid`?
Use `math.ceil(pile / speed)` for each pile.

</details>

<details>
<summary>Answer</summary>

```python
import math

def min_eating_speed(piles: list[int], h: int) -> int:
    def feasible(speed: int) -> bool:
        return sum(math.ceil(pile / speed) for pile in piles) <= h

    lo, hi = 1, max(piles)     # speed 1 = slowest; max(piles) = finishes any pile in 1hr
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if feasible(mid):
            hi = mid           # speed mid works, try slower
        else:
            lo = mid + 1       # speed mid too slow, try faster
    return lo
```

**Why:** The feasibility function is monotonic — if speed `k` works, speed `k+1`
also works (faster or equal time). So the answer space is `F F F F T T T T` and
we binary search for the first T. `lo = 1` (can always eat, just slowly).
`hi = max(piles)` because at that speed every pile takes at most 1 hour, so
total hours `= len(piles) <= h`.

**Time:** O(n log(max(piles))) | **Space:** O(1)

</details>

---

<a id="q18"></a>
### Q18 — Capacity to Ship Packages

Given package weights and `days`, find the minimum ship capacity to deliver
all packages in order within `days` days.

```
Input:  weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],  days = 5
Output: 15
```

<details>
<summary>Hint</summary>

Answer space: `[max(weights), sum(weights)]`. Feasibility: simulate loading
packages greedily — start a new day when adding the next package would exceed
capacity.

</details>

<details>
<summary>Answer</summary>

```python
def ship_within_days(weights: list[int], days: int) -> int:
    def feasible(capacity: int) -> bool:
        current = 0
        days_needed = 1
        for w in weights:
            if current + w > capacity:
                days_needed += 1
                current = 0
            current += w
        return days_needed <= days

    lo = max(weights)      # must carry the heaviest package
    hi = sum(weights)      # worst case: all in one day
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

**Why:** `lo = max(weights)` is the hard lower bound — if capacity is less than
the heaviest package, it can never be shipped. `hi = sum(weights)` guarantees
feasibility (everything in one day). The feasibility function is monotonic:
higher capacity never requires more days. Greedy loading works because packages
must stay in order — split whenever the next package would overflow the day.

**Time:** O(n log(sum - max)) | **Space:** O(1)

</details>

---

<a id="q19"></a>
### Q19 — Minimize Maximum (Split Array Largest Sum)

Split array into `m` non-empty contiguous subarrays to minimize the largest
subarray sum. Return that minimum possible largest sum.

```
Input:  nums = [7, 2, 5, 10, 8],  m = 2
Output: 18   (split: [7,2,5] and [10,8], largest sum = 18)
```

<details>
<summary>Hint</summary>

Answer space: `[max(nums), sum(nums)]`. Feasibility: can we split `nums` into
at most `m` subarrays such that each subarray sum `<= mid`?

</details>

<details>
<summary>Answer</summary>

```python
def split_array(nums: list[int], m: int) -> int:
    def feasible(max_sum: int) -> bool:
        parts = 1
        current = 0
        for n in nums:
            if current + n > max_sum:
                parts += 1
                current = 0
            current += n
        return parts <= m

    lo = max(nums)          # each subarray must hold at least its largest element
    hi = sum(nums)          # one subarray holds everything
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

**Why:** "Minimize the maximum" over splits is a classic binary search on answer
space. If a maximum sum of `mid` is achievable with `<= m` parts, any larger
limit is also achievable (monotonic). The greedy feasibility check greedily
extends each part as far as possible without exceeding `mid`. Identical
structure to Q18 — recognizing this family of problems is the key skill.

**Time:** O(n log(sum)) | **Space:** O(1)

</details>

---

<a id="q20"></a>
### Q20 — Maximize Minimum (Allocate Minimum Pages)

`n` books with page counts `pages[i]` must be allocated to `m` students in
order (each student gets a contiguous block). Minimize the maximum pages any
student reads.

```
Input:  pages = [12, 34, 67, 90],  m = 2
Output: 113   (allocate [12,34,67] to student 1, [90] to student 2)
```

<details>
<summary>Hint</summary>

Same structure as Q19. Answer space: `[max(pages), sum(pages)]`. Feasibility:
can we allocate to `m` students such that no student reads more than `mid` pages?

</details>

<details>
<summary>Answer</summary>

```python
def allocate_pages(pages: list[int], m: int) -> int:
    if m > len(pages):
        return -1     # impossible: more students than books

    def feasible(max_pages: int) -> bool:
        students = 1
        current = 0
        for p in pages:
            if p > max_pages:
                return False       # single book exceeds the cap
            if current + p > max_pages:
                students += 1
                current = 0
            current += p
        return students <= m

    lo = max(pages)
    hi = sum(pages)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

**Why:** "Minimize the maximum pages" is the same family as Q19 (minimize
the largest sum). The feasibility check is greedy: keep adding books to the
current student until adding the next would exceed `mid`, then give the next
book to a new student. The single-book check `p > max_pages` prevents infinite
loops when one book alone exceeds the candidate answer.

**Time:** O(n log(sum)) | **Space:** O(1)

</details>

---

## Advanced (Q21–Q25)

---

<a id="q21"></a>
### Q21 — Search in Rotated Array with Duplicates

Same as Q12 but the array may have duplicate values. Return `True` if target
exists, `False` otherwise.

```
Input:  arr = [2, 5, 6, 0, 0, 1, 2],  target = 0
Output: True

Input:  arr = [2, 5, 6, 0, 0, 1, 2],  target = 3
Output: False
```

<details>
<summary>Hint</summary>

When `arr[lo] == arr[mid] == arr[hi]`, you cannot determine which half is
sorted. Shrink both ends by one and continue. This degrades worst-case to O(n).

</details>

<details>
<summary>Answer</summary>

```python
def search_rotated_duplicates(arr: list[int], target: int) -> bool:
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return True

        if arr[lo] == arr[mid] == arr[hi]:
            # Cannot determine which side is sorted — shrink both ends
            lo += 1
            hi -= 1
        elif arr[lo] <= arr[mid]:           # left half sorted
            if arr[lo] <= target < arr[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                               # right half sorted
            if arr[mid] < target <= arr[hi]:
                lo = mid + 1
            else:
                hi = mid - 1

    return False
```

**Why:** Duplicates create ambiguity. When `arr[lo] == arr[mid] == arr[hi]`,
both `arr[lo..mid]` and `arr[mid..hi]` could contain the rotation point — we
cannot tell which side is sorted. The only safe move is to shrink from both
ends. This is correct but worst-case O(n) for arrays like `[1,1,1,1,0,1,1]`.
This is the key difference from the no-duplicates version.

**Time:** O(n) worst case, O(log n) average | **Space:** O(1)

</details>

---

<a id="q22"></a>
### Q22 — Smallest Divisor Given Threshold

Given an integer array and a threshold, find the smallest positive integer
divisor such that the sum of `ceil(num / divisor)` for all nums is `<= threshold`.

```
Input:  nums = [1, 2, 5, 9],  threshold = 6
Output: 5
  (divisor=5: ceil(1/5)+ceil(2/5)+ceil(5/5)+ceil(9/5) = 1+1+1+2 = 5 ≤ 6)
```

<details>
<summary>Hint</summary>

Answer space: `[1, max(nums)]`. Feasibility: `sum(ceil(n / mid)) <= threshold`.
This is identical in shape to Koko (Q17) with a ceiling-division predicate.

</details>

<details>
<summary>Answer</summary>

```python
import math

def smallest_divisor(nums: list[int], threshold: int) -> int:
    def feasible(d: int) -> bool:
        return sum(math.ceil(n / d) for n in nums) <= threshold

    lo, hi = 1, max(nums)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

**Why:** As the divisor increases, each `ceil(n / d)` term decreases or stays
the same — the total sum is non-increasing. So the feasibility function is
monotonic: once the sum `<= threshold`, larger divisors also satisfy it. This
is the "find first True" (minimize) pattern. Recognizing that this has the same
shape as Koko (speed replaces divisor) shows pattern mastery.

**Time:** O(n log(max(nums))) | **Space:** O(1)

</details>

---

<a id="q23"></a>
### Q23 — Find Bad Version (First True in Answer Space)

There are `n` versions `[1, 2, ..., n]`. Versions from some version `k` onward
are "bad" (monotonic). Given a function `is_bad(version) -> bool`, find the
first bad version using the minimum number of API calls.

```
Input:  n = 5,  first bad = 4
Output: 4
```

<details>
<summary>Hint</summary>

This is the canonical "find first True" pattern. Answer space: `[1, n]`.
The predicate is already given. Use the minimize template (`lo < hi`, `hi = mid`
when `is_bad(mid)` is True).

</details>

<details>
<summary>Answer</summary>

```python
def first_bad_version(n: int, is_bad) -> int:
    """
    is_bad(version) returns True if version is bad.
    Versions k, k+1, ..., n are all bad (monotonic).
    Find k using minimum calls to is_bad.
    """
    lo, hi = 1, n
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if is_bad(mid):
            hi = mid           # mid could be the first bad — preserve it
        else:
            lo = mid + 1       # mid is good, first bad is strictly later
    return lo                  # lo == hi at the first bad version

# Test
first_bad = 4
calls = [0]
def is_bad_fn(v):
    calls[0] += 1
    return v >= first_bad

result = first_bad_version(5, is_bad_fn)
print(result, f"({calls[0]} API calls)")   # 4 (3 API calls)
```

**Why:** This is the archetypal "binary search on answer" problem — LeetCode 278.
The answer space is `F F F T T` (good good good bad bad). We want the first T.
The minimize template finds the left boundary of the T region. Each call to
`is_bad` is an API call; binary search minimizes them to O(log n).

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q24"></a>
### Q24 — Median of Two Sorted Arrays

Given two sorted arrays `nums1` and `nums2` of sizes `m` and `n`, find the
median of their merged sorted array in O(log(m+n)) time.

```
Input:  nums1 = [1, 3],  nums2 = [2]
Output: 2.0

Input:  nums1 = [1, 2],  nums2 = [3, 4]
Output: 2.5
```

<details>
<summary>Hint</summary>

Binary search on the partition index in the smaller array. A valid partition
satisfies: `max_left1 <= min_right2` and `max_left2 <= min_right1`. Search on
the smaller array so the time is O(log(min(m, n))).

</details>

<details>
<summary>Answer</summary>

```python
def find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
    # Always binary search on the smaller array
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    half = (m + n) // 2

    lo, hi = 0, m
    while lo <= hi:
        i = lo + (hi - lo) // 2        # partition index in nums1
        j = half - i                   # partition index in nums2

        # Values around the partition (use ±inf for edge cases)
        max_left1  = nums1[i - 1] if i > 0 else float('-inf')
        min_right1 = nums1[i]     if i < m else float('inf')
        max_left2  = nums2[j - 1] if j > 0 else float('-inf')
        min_right2 = nums2[j]     if j < n else float('inf')

        if max_left1 <= min_right2 and max_left2 <= min_right1:
            # Valid partition found
            if (m + n) % 2 == 1:
                return float(min(min_right1, min_right2))
            return (max(max_left1, max_left2) + min(min_right1, min_right2)) / 2.0
        elif max_left1 > min_right2:
            hi = i - 1              # too many elements from nums1 on the left
        else:
            lo = i + 1              # too few elements from nums1 on the left

    raise ValueError("Input arrays are not sorted")
```

**Why:** The median is the midpoint of the merged array. We binary search for
a partition `(i, j)` such that `nums1[:i] + nums2[:j]` forms exactly the left
half of the merged array. The partition is valid when the largest left element
`<= smallest right element` on both sides. Searching on the smaller array gives
O(log(min(m, n))). This is the hardest binary search problem in interviews.

**Time:** O(log(min(m, n))) | **Space:** O(1)

</details>

---

<a id="q25"></a>
### Q25 — Off-by-One Bug Hunt

Each function below has one binary search bug. Identify and fix it.

**(A)** `binary_search_a` — sometimes returns a wrong index or -1 for present values.

**(B)** `binary_search_b` — sometimes hangs in an infinite loop.

**(C)** `first_occurrence_c` — returns any occurrence, not the first.

**(D)** `left_boundary_d` — can cause an IndexError.

```python
def binary_search_a(arr, target):
    lo, hi = 0, len(arr)        # BUG IS HERE
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target: return mid
        elif arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1

def binary_search_b(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] < target: lo = mid   # BUG IS HERE
        else: hi = mid
    return lo if arr[lo] == target else -1

def first_occurrence_c(arr, target):
    lo, hi = 0, len(arr) - 1
    result = -1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            result = mid
            lo = mid + 1      # BUG IS HERE
        elif arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return result

def left_boundary_d(arr, target):
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] < target: lo = mid + 1
        else: hi = mid
    return arr[lo]            # BUG IS HERE
```

<details>
<summary>Hint</summary>

(A) `hi = len(arr)` lets `mid` reach `len(arr)` — IndexError.
(B) `lo = mid` when `lo + 1 == hi` causes infinite loop.
(C) `lo = mid + 1` on match searches for the LAST occurrence, not first.
(D) `lo` can equal `len(arr)` after the loop — out of bounds.

</details>

<details>
<summary>Answer</summary>

```python
def binary_search_a(arr, target):
    lo, hi = 0, len(arr) - 1   # FIX: hi = len(arr) - 1 (inclusive upper bound)
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target: return mid
        elif arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1

def binary_search_b(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] < target: lo = mid + 1  # FIX: lo = mid + 1 (skip confirmed small)
        else: hi = mid
    return lo if arr[lo] == target else -1

def first_occurrence_c(arr, target):
    lo, hi = 0, len(arr) - 1
    result = -1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            result = mid
            hi = mid - 1    # FIX: hi = mid - 1 (search LEFT for earlier occurrence)
        elif arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return result

def left_boundary_d(arr, target):
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] < target: lo = mid + 1
        else: hi = mid
    # FIX: bounds check before indexing
    if lo < len(arr) and arr[lo] == target:
        return lo
    return -1
```

**Why:**
- (A) `hi = len(arr)` makes `mid` reach `len(arr)` when `lo = len(arr) - 1` and
  `hi = len(arr)` — direct IndexError.
- (B) When `lo = 4, hi = 5, mid = 4` and condition is True: `lo = mid = 4` —
  no progress, infinite loop. `lo = mid + 1` guarantees the window shrinks.
- (C) `lo = mid + 1` after a match searches right — that finds the LAST
  occurrence. `hi = mid - 1` searches left for the first.
- (D) `lo` can equal `len(arr)` when target is larger than all elements — must
  bounds-check before indexing `arr[lo]`.

**Time:** O(log n) each | **Space:** O(1)

</details>

---

## 📂 Navigation

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Visual Explanation →](./visual_explanation.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md) · [Practice Local](./practice_local.py)
