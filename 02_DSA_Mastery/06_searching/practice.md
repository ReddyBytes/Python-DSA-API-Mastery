# 📝 Searching — Practice Problems (25 Questions)

> Work through these in order. Basic locks in the mechanics. Intermediate builds
> the pattern library. Advanced requires combining ideas under pressure.

---

## Quick Index

### Basic (Q1–Q8)
| # | Title | Concept |
|---|-------|---------|
| [Q1](#q1) | [Linear Search — Return Index](#q1--linear-search--return-index) | Scan every element |
| [Q2](#q2) | [Linear Search — All Occurrences](#q2--linear-search--all-occurrences) | Collect all matches |
| [Q3](#q3) | [Binary Search — Iterative](#q3--binary-search--iterative) | Standard Template 1 |
| [Q4](#q4) | [Binary Search — Recursive](#q4--binary-search--recursive) | Recursive call stack |
| [Q5](#q5) | [Count Occurrences in Sorted Array](#q5--count-occurrences-in-sorted-array) | bisect_right − bisect_left |
| [Q6](#q6) | [Insertion Point](#q6--insertion-point) | Where would target go? |
| [Q7](#q7) | [Complexity Analysis — When to Choose What](#q7--complexity-analysis--when-to-choose-what) | Decision reasoning |
| [Q8](#q8) | [Linear Search on 2D List](#q8--linear-search-on-2d-list) | Nested scan |

### Intermediate (Q9–Q20)
| # | Title | Concept |
|---|-------|---------|
| [Q9](#q9) | [First Occurrence](#q9--first-occurrence) | Keep searching left |
| [Q10](#q10) | [Last Occurrence](#q10--last-occurrence) | Keep searching right |
| [Q11](#q11) | [Count of Target in Sorted Array](#q11--count-of-target-in-sorted-array) | last − first + 1 |
| [Q12](#q12) | [Search in Rotated Sorted Array](#q12--search-in-rotated-sorted-array) | One half always sorted |
| [Q13](#q13) | [Find Minimum in Rotated Sorted Array](#q13--find-minimum-in-rotated-sorted-array) | Track the pivot |
| [Q14](#q14) | [Search a 2D Matrix](#q14--search-a-2d-matrix) | Flatten to virtual array |
| [Q15](#q15) | [Search a 2D Matrix II (sorted rows+cols)](#q15--search-a-2d-matrix-ii-sorted-rowscols) | Start top-right, eliminate |
| [Q16](#q16) | [Find Peak Element](#q16--find-peak-element) | Climb the slope |
| [Q17](#q17) | [Floor and Ceiling](#q17--floor-and-ceiling) | Off-by-one pointer position |
| [Q18](#q18) | [Square Root via Binary Search](#q18--square-root-via-binary-search) | Search on answer space |
| [Q19](#q19) | [Koko Eating Bananas](#q19--koko-eating-bananas) | Monotonic predicate |
| [Q20](#q20) | [Ship Packages Within D Days](#q20--ship-packages-within-d-days) | Classic search-on-answer |

### Advanced (Q21–Q25)
| # | Title | Concept |
|---|-------|---------|
| [Q21](#q21) | [Median of Two Sorted Arrays](#q21--median-of-two-sorted-arrays) | Partition binary search |
| [Q22](#q22) | [Smallest Divisor Given Threshold](#q22--smallest-divisor-given-threshold) | Ceiling-division predicate |
| [Q23](#q23) | [Find Duplicate in Array (Floyd or Binary)](#q23--find-duplicate-in-array-floyd-or-binary) | Binary search on value range |
| [Q24](#q24) | [Allocate Minimum Pages](#q24--allocate-minimum-pages) | Classic allocation problem |
| [Q25](#q25) | [Off-by-One Bug Hunt](#q25--off-by-one-bug-hunt) | Fix four broken implementations |

---

## Basic (Q1–Q8)

---

<a id="q1"></a>
### Q1 — Linear Search — Return Index

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


Given an unsorted list and a target, return the index of the first occurrence of
target, or -1 if not found.

```
Input:  arr = [4, 9, 2, 7, 1],  target = 7
Output: 3
```

<details>
<summary>Hint</summary>

Use `enumerate`. Walk forward and return as soon as you find the value.
No sorting needed — this is the point.

</details>

<details>
<summary>Answer</summary>

```python
def linear_search(arr: list, target: int) -> int:
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1
```

**Why:** Unsorted data leaves no shortcut. You must inspect every element
in the worst case. O(n) is unavoidable here — binary search would give
wrong answers on shuffled input.

**Time:** O(n) | **Space:** O(1)

</details>

---

<a id="q2"></a>
### Q2 — Linear Search — All Occurrences

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


Return a list of all indices where target appears. Return an empty list if none.

```
Input:  arr = [3, 1, 4, 1, 5, 9, 1],  target = 1
Output: [1, 3, 6]
```

<details>
<summary>Hint</summary>

Do not return early. Keep scanning and append every matching index.

</details>

<details>
<summary>Answer</summary>

```python
def linear_search_all(arr: list, target: int) -> list[int]:
    return [i for i, val in enumerate(arr) if val == target]
```

**Why:** A single pass with a list comprehension is clean and O(n). When you
need ALL matches — not just the first — you must scan the whole array. Binary
search gives you one match position; finding all requires an extra walk either
side, which is worse in duplicated data.

**Time:** O(n) | **Space:** O(k) where k = number of matches

</details>

---

<a id="q3"></a>
### Q3 — Binary Search — Iterative

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


Implement iterative binary search. Return the index of target in the sorted array,
or -1 if absent.

```
Input:  arr = [1, 3, 5, 7, 9, 11, 13],  target = 7
Output: 3
```

<details>
<summary>Hint</summary>

Use Template 1: `lo <= hi`. Mid should be `lo + (hi - lo) // 2`.
The three-way branch is: found / go right / go left.

</details>

<details>
<summary>Answer</summary>

```python
def binary_search(arr: list[int], target: int) -> int:
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2      # overflow-safe mid
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

**Why:** `lo + (hi - lo) // 2` avoids the integer overflow that `(lo + hi) // 2`
causes in C/Java. Python is immune but good practice. `lo <= hi` (not `<`) handles
the single-element window correctly — that last element might be the answer.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q4"></a>
### Q4 — Binary Search — Recursive

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


Implement the same binary search using recursion.

```
Input:  arr = [2, 4, 6, 8, 10],  target = 6
Output: 2
```

<details>
<summary>Hint</summary>

Pass `lo` and `hi` as parameters. Base case: `lo > hi` → return -1.
Each recursive call reduces the window by half.

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

**Why:** Each call reduces the problem to half the size — the recursive call stack
depth is O(log n). This is why recursive binary search costs O(log n) space while
iterative costs O(1). In Python, deep recursion can hit the default 1000-frame
limit; iterative is preferred for large arrays.

**Time:** O(log n) | **Space:** O(log n) stack

</details>

---

<a id="q5"></a>
### Q5 — Count Occurrences in Sorted Array

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Given a sorted array with possible duplicates, count how many times `target` appears.

```
Input:  arr = [1, 1, 2, 2, 2, 3, 4],  target = 2
Output: 3
```

<details>
<summary>Hint</summary>

`bisect_right(arr, target) - bisect_left(arr, target)` does this in two lines.
Or implement first/last occurrence and subtract.

</details>

<details>
<summary>Answer</summary>

```python
import bisect

def count_occurrences(arr: list[int], target: int) -> int:
    left = bisect.bisect_left(arr, target)
    right = bisect.bisect_right(arr, target)
    return right - left
```

**Why:** `bisect_left` gives the index of the first occurrence (or where target
would be inserted). `bisect_right` gives the index just past the last occurrence.
The gap between them is exactly the count. O(log n) total — far better than a
linear scan through duplicates.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q6"></a>
### Q6 — Insertion Point

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


Given a sorted array and a target, return the index where target should be inserted
to keep the array sorted. Do not insert — just return the index.

```
Input:  arr = [1, 3, 5, 7, 9],  target = 6
Output: 3   (inserted between 5 and 7)

Input:  arr = [1, 3, 5, 7, 9],  target = 5
Output: 2   (exact match — its own position)
```

<details>
<summary>Hint</summary>

When the loop exits without an exact match, `lo` holds the insertion point.
`bisect_left` gives the same result.

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
    return lo    # lo is the insertion point when target is absent
```

**Why:** After Template 1 exits without finding target, `lo > hi`. At that moment
`lo` points to the first element greater than target — the correct insertion slot.
`right` points to the last element less than target. Knowing both pointer meanings
after loop exit is essential for many boundary problems.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q7"></a>
### Q7 — Complexity Analysis — When to Choose What

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


No code required. Answer these four sub-questions:

1. Array has 1 million elements, unsorted. Single one-time lookup needed. What do you use?
2. Same array, 100,000 lookups needed. What do you use?
3. Array is sorted. Needs repeated range queries. What do you use?
4. Array is a linked list, sorted. What do you use?

<details>
<summary>Hint</summary>

Think about: (a) cost of preprocessing vs savings on repeated lookups,
(b) whether random access is available.

</details>

<details>
<summary>Answer</summary>

1. **Linear search O(n).** Sorting costs O(n log n) — more expensive than the
   single lookup you need.

2. **Sort once O(n log n), then binary search each query O(log n).** Total:
   O(n log n + 100,000 × log n) vs O(1,000,000 × 100,000) = O(10^11) for
   linear. The sort amortizes across repeated lookups.
   Alternative: build a hash set O(n), then O(1) per lookup — best for exact
   membership, but hash sets cannot do range queries.

3. **Binary search + bisect for range queries.** `bisect_left` / `bisect_right`
   bound both ends of the range in O(log n) each. A hash set cannot answer
   "all elements between 30 and 50" efficiently.

4. **Linear search.** Linked lists have O(n) random access — finding `mid`
   takes O(n) each step, making binary search O(n log n) overall. Worse than
   plain linear.

**Why:** Data structure choice gates algorithm choice. Sorted + random access
= binary search. Unsorted + exact membership = hash set. Linked = linear.

**Time:** varies | **Space:** varies

</details>

---

<a id="q8"></a>
### Q8 — Linear Search on 2D List

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


Given a 2D list (unsorted, rows unsorted), find the (row, col) of target.
Return (-1, -1) if not found.

```
Input:  matrix = [[9, 3], [2, 7], [5, 1]],  target = 7
Output: (1, 1)
```

<details>
<summary>Hint</summary>

Nest two loops: outer over rows, inner over columns.

</details>

<details>
<summary>Answer</summary>

```python
def search_2d_unsorted(matrix: list[list[int]], target: int) -> tuple[int, int]:
    for r, row in enumerate(matrix):
        for c, val in enumerate(row):
            if val == target:
                return (r, c)
    return (-1, -1)
```

**Why:** No ordering guarantee means no elimination is possible. Every cell is
a candidate. This is the 2D equivalent of linear search. When rows and columns
ARE sorted, Q14/Q15 show dramatically better approaches.

**Time:** O(n × m) | **Space:** O(1)

</details>

---

## Intermediate (Q9–Q20)

---

<a id="q9"></a>
### Q9 — First Occurrence

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


Find the index of the **first** occurrence of target in a sorted array with duplicates.
Return -1 if absent.

```
Input:  arr = [1, 2, 2, 2, 3, 4],  target = 2
Output: 1
```

<details>
<summary>Hint</summary>

When you find target at `mid`, record it and then narrow right (`hi = mid - 1`)
to keep searching left for an earlier occurrence.

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
            result = mid        # candidate found — keep searching left
            hi = mid - 1
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return result
```

**Why:** The moment you return on `arr[mid] == target` (like plain binary search)
you get *some* occurrence, not the *first*. Recording the candidate and moving
`hi` left ensures the loop continues until the leftmost occurrence is found.
The classic interview trap: using Template 1 for first-occurrence returns the
wrong index silently.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q10"></a>
### Q10 — Last Occurrence

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


Find the index of the **last** occurrence of target. Return -1 if absent.

```
Input:  arr = [1, 2, 2, 2, 3, 4],  target = 2
Output: 3
```

<details>
<summary>Hint</summary>

Mirror of Q9: when found, move `lo = mid + 1` to keep searching right.

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
            result = mid        # candidate found — keep searching right
            lo = mid + 1
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return result
```

**Why:** Same logic as Q9 but mirrored. Moving `lo = mid + 1` on a match
continues searching the right half. The result variable captures the rightmost
confirmed match before the pointers cross.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q11"></a>
### Q11 — Count of Target in Sorted Array

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


Using first/last occurrence (no bisect module), return how many times target
appears in a sorted array.

```
Input:  arr = [1, 2, 2, 2, 3, 4],  target = 2
Output: 3
```

<details>
<summary>Hint</summary>

Run first_occurrence and last_occurrence from Q9/Q10. The count is
`last - first + 1` (or 0 if first == -1).

</details>

<details>
<summary>Answer</summary>

```python
def count_target(arr: list[int], target: int) -> int:
    first = first_occurrence(arr, target)   # from Q9
    if first == -1:
        return 0
    last = last_occurrence(arr, target)     # from Q10
    return last - first + 1
```

**Why:** Two binary searches give both boundary indices. The difference plus one
is the count. This is O(log n) total — the same as `bisect_right - bisect_left`
but implemented from scratch, which is what interviewers want to see.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q12"></a>
### Q12 — Search in Rotated Sorted Array

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


A sorted array was rotated at an unknown pivot. Search for target.
Return its index or -1.

```
Input:  arr = [4, 5, 6, 7, 0, 1, 2],  target = 0
Output: 4
```

<details>
<summary>Hint</summary>

At every mid, one half is always fully sorted. Check if the target falls inside
the sorted half; if yes, narrow to that half. If no, narrow to the other half.

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
        if arr[lo] <= arr[mid]:                     # left half is sorted
            if arr[lo] <= target < arr[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                                       # right half is sorted
            if arr[mid] < target <= arr[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
```

**Why:** Rotation breaks the global sorted order but guarantees that one side
of any mid point is still sorted. The `arr[lo] <= arr[mid]` condition identifies
which side. From there, a simple range check (`arr[lo] <= target < arr[mid]`)
tells you whether the target is in the sorted half or must be in the unsorted
half. Note the `<=` in `arr[lo] <= arr[mid]` handles the case where `lo == mid`.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q13"></a>
### Q13 — Find Minimum in Rotated Sorted Array

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


Given a rotated sorted array with distinct elements, return the minimum value.

```
Input:  arr = [3, 4, 5, 1, 2]
Output: 1
```

<details>
<summary>Hint</summary>

If `arr[mid] > arr[hi]`, the minimum is in the right half (past the rotation
point). Otherwise it's in the left half (inclusive of mid).

</details>

<details>
<summary>Answer</summary>

```python
def find_min_rotated(arr: list[int]) -> int:
    lo, hi = 0, len(arr) - 1
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] > arr[hi]:
            lo = mid + 1        # minimum is to the right of mid
        else:
            hi = mid            # mid could be the minimum; keep it
    return arr[lo]
```

**Why:** The rotation creates exactly one "drop" where the array wraps around.
Comparing `arr[mid]` to `arr[hi]` (not `arr[lo]`) tells you which side the drop
is on. When `arr[mid] > arr[hi]`, the drop is in the right half — the minimum
lives there. When `arr[mid] <= arr[hi]`, the right side is already sorted and
the minimum is at `mid` or to the left.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q14"></a>
### Q14 — Search a 2D Matrix

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


Matrix where each row is sorted, and the first element of each row is greater than
the last element of the previous row (effectively a sorted 1D array folded into rows).
Return True if target exists.

```
Input:
  matrix = [[1, 3, 5],
            [7, 9, 11],
            [13, 15, 17]]
  target = 9
Output: True
```

<details>
<summary>Hint</summary>

Treat the matrix as a 1D array of length `n*m`. Map virtual index `k` to
`(k // cols, k % cols)`.

</details>

<details>
<summary>Answer</summary>

```python
def search_matrix(matrix: list[list[int]], target: int) -> bool:
    if not matrix or not matrix[0]:
        return False
    rows, cols = len(matrix), len(matrix[0])
    lo, hi = 0, rows * cols - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        val = matrix[mid // cols][mid % cols]
        if val == target:
            return True
        elif val < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False
```

**Why:** The "first element of each row > last of previous row" guarantee means
the whole matrix is a single sorted sequence. Flattening it virtually (without
actually allocating a new array) and running standard binary search is O(log(n*m)).
The index mapping `mid // cols` (row) and `mid % cols` (col) is the key insight.

**Time:** O(log(n·m)) | **Space:** O(1)

</details>

---

<a id="q15"></a>
### Q15 — Search a 2D Matrix II (sorted rows + cols)

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


Each row is sorted left to right. Each column is sorted top to bottom.
Rows do not need to start after the previous row ends.
Return True if target exists.

```
Input:
  matrix = [[1,  4,  7],
            [2,  5,  8],
            [3,  6,  9]]
  target = 5
Output: True
```

<details>
<summary>Hint</summary>

Start at the top-right corner. If value > target, move left. If value < target,
move down. Each step eliminates a full row or column.

</details>

<details>
<summary>Answer</summary>

```python
def search_matrix_ii(matrix: list[list[int]], target: int) -> bool:
    if not matrix or not matrix[0]:
        return False
    rows, cols = len(matrix), len(matrix[0])
    r, c = 0, cols - 1                     # start top-right
    while r < rows and c >= 0:
        val = matrix[r][c]
        if val == target:
            return True
        elif val > target:
            c -= 1                          # current col too large, go left
        else:
            r += 1                          # current row too small, go down
    return False
```

**Why:** The top-right corner is the unique position where moving in one
direction always increases the value (down) and the other always decreases it
(left). This means each comparison eliminates an entire row or column. The
virtual flattening trick from Q14 does NOT work here — rows are not globally
sorted relative to each other.

**Time:** O(n + m) | **Space:** O(1)

</details>

---

<a id="q16"></a>
### Q16 — Find Peak Element

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


A peak element is greater than its neighbors. Find any peak index.
Assume `arr[-1] = arr[n] = -infinity`.

```
Input:  arr = [1, 2, 3, 1]
Output: 2   (arr[2]=3 is a peak)
```

<details>
<summary>Hint</summary>

If `arr[mid] < arr[mid+1]`, the slope is going up — a peak exists to the right.
Otherwise, a peak exists at or to the left of mid.

</details>

<details>
<summary>Answer</summary>

```python
def find_peak_element(arr: list[int]) -> int:
    lo, hi = 0, len(arr) - 1
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] < arr[mid + 1]:
            lo = mid + 1        # ascending slope: peak is to the right
        else:
            hi = mid            # descending or flat: peak is here or left
    return lo
```

**Why:** The array does not need to be sorted. It only needs the "ascending
implies peak to the right" property — which is always true because the
boundaries are -∞. If you're going uphill, you must eventually crest. This
is binary search on a property (the slope direction) rather than a value.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q17"></a>
### Q17 — Floor and Ceiling

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


Given a sorted array and target, return:
- **floor**: the largest element ≤ target (or None if all > target)
- **ceiling**: the smallest element ≥ target (or None if all < target)

```
Input:  arr = [1, 3, 5, 7, 9],  target = 6
Output: floor=5, ceiling=7
```

<details>
<summary>Hint</summary>

After Template 1 exits: `lo` = first element > target, `hi` = last element < target.
Floor is `arr[hi]` (if hi >= 0), ceiling is `arr[lo]` (if lo < len(arr)).

</details>

<details>
<summary>Answer</summary>

```python
def floor_ceiling(arr: list[int], target: int):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return arr[mid], arr[mid]   # exact match: floor == ceiling
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    # Loop exits with hi < lo
    floor_val = arr[hi] if hi >= 0 else None
    ceil_val  = arr[lo] if lo < len(arr) else None
    return floor_val, ceil_val
```

**Why:** After the loop, the pointers have crossed: `hi` points to the
last element confirmed less than target; `lo` points to the first element
confirmed greater than target. These are exactly the floor and ceiling.
Off-by-one errors here — returning `arr[lo-1]` instead of `arr[hi]` — are
extremely common.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q18"></a>
### Q18 — Square Root via Binary Search

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


Return the integer floor of `sqrt(n)` without using `math.sqrt`.

```
Input:  n = 17
Output: 4   (because 4*4=16 <= 17 < 25=5*5)
```

<details>
<summary>Hint</summary>

Binary search on the answer space [1, n//2]. The predicate is `mid*mid <= n`.
When the loop ends, `hi` holds the floor.

</details>

<details>
<summary>Answer</summary>

```python
def integer_sqrt(n: int) -> int:
    if n < 2:
        return n
    lo, hi = 1, n // 2
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        sq = mid * mid
        if sq == n:
            return mid
        elif sq < n:
            lo = mid + 1
        else:
            hi = mid - 1
    return hi   # hi = floor(sqrt(n))
```

**Why:** The search space here is the set of candidate answers (1 to n//2),
not positions in an array. The predicate `mid*mid <= n` is monotone: all
values below the true sqrt satisfy it, all above do not. After the loop,
`hi` is the last value where `mid*mid <= n` — exactly the floor.

**Time:** O(log n) | **Space:** O(1)

</details>

---

<a id="q19"></a>
### Q19 — Koko Eating Bananas

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


Koko has piles of bananas. She has `h` hours. Each hour she picks one pile and
eats up to `k` bananas from it. Find the minimum integer `k` such that she can
finish all piles in `h` hours.

```
Input:  piles = [3, 6, 7, 11],  h = 8
Output: 4
```

<details>
<summary>Hint</summary>

The feasibility function `can_finish(k)` is monotone: False for small k, True
for large k. Binary search for the smallest k where it becomes True.
Range: `[1, max(piles)]`.

</details>

<details>
<summary>Answer</summary>

```python
import math

def min_eating_speed(piles: list[int], h: int) -> int:
    def can_finish(k: int) -> bool:
        return sum(math.ceil(p / k) for p in piles) <= h

    lo, hi = 1, max(piles)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if can_finish(mid):
            hi = mid        # mid works, but maybe less also works
        else:
            lo = mid + 1    # mid too slow, need faster
    return lo
```

**Why:** This is the canonical "search on answer" problem. The search space is
the speed value `k`, not an array index. `can_finish(k)` flips from False to
True exactly once as k increases — the monotone property that makes binary
search valid. The Template 2 (`lo < hi`) loop converges to the first True value.

**Time:** O(n log m) where m = max pile | **Space:** O(1)

</details>

---

<a id="q20"></a>
### Q20 — Ship Packages Within D Days

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


Given package weights and a number of days `d`, find the minimum ship capacity
such that all packages can be shipped within `d` days (maintaining order).

```
Input:  weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],  days = 5
Output: 15
```

<details>
<summary>Hint</summary>

Search space: `[max(weights), sum(weights)]`. The feasibility check simulates
loading packages day by day, starting a new day when adding the next package
would exceed capacity.

</details>

<details>
<summary>Answer</summary>

```python
def ship_within_days(weights: list[int], days: int) -> int:
    def can_ship(capacity: int) -> bool:
        day_count = 1
        current = 0
        for w in weights:
            if current + w > capacity:
                day_count += 1
                current = 0
            current += w
        return day_count <= days

    lo, hi = max(weights), sum(weights)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if can_ship(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

**Why:** The lower bound is `max(weights)` — the ship must fit the heaviest
package. The upper bound is `sum(weights)` — ship everything in one day.
Between them, the feasibility is monotone. This exact pattern (capacity /
allocation problems) appears repeatedly: allocate min pages, split array,
painter partition — all the same template.

**Time:** O(n log(sum − max)) | **Space:** O(1)

</details>

---

## Advanced (Q21–Q25)

---

<a id="q21"></a>
### Q21 — Median of Two Sorted Arrays

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)


Given two sorted arrays, find their median in O(log(min(n, m))) time.

```
Input:  nums1 = [1, 3],  nums2 = [2, 4]
Output: 2.5
```

<details>
<summary>Hint</summary>

Binary search on the partition point of the smaller array. For every partition of
nums1 at index `i`, the partition of nums2 at index `j = (n+m+1)//2 - i` is
determined. Adjust the partition until left halves contain all elements ≤ right
halves.

</details>

<details>
<summary>Answer</summary>

```python
def find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
    # Ensure nums1 is the shorter array
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    m, n = len(nums1), len(nums2)
    half = (m + n + 1) // 2

    lo, hi = 0, m
    while lo <= hi:
        i = lo + (hi - lo) // 2    # partition index in nums1
        j = half - i               # partition index in nums2

        max_left1  = nums1[i-1] if i > 0 else float('-inf')
        min_right1 = nums1[i]   if i < m else float('inf')
        max_left2  = nums2[j-1] if j > 0 else float('-inf')
        min_right2 = nums2[j]   if j < n else float('inf')

        if max_left1 <= min_right2 and max_left2 <= min_right1:
            # Correct partition found
            if (m + n) % 2 == 1:
                return float(max(max_left1, max_left2))
            return (max(max_left1, max_left2) + min(min_right1, min_right2)) / 2
        elif max_left1 > min_right2:
            hi = i - 1
        else:
            lo = i + 1

    raise ValueError("Input arrays are not sorted")
```

**Why:** Brute force merges both arrays O(n+m). The insight is that a median
splits the combined array in half. Binary search on where to "cut" nums1 (binary
search on partition position 0..m) determines the corresponding cut in nums2.
Binary search runs on the shorter array, giving O(log(min(m,n))). This is one
of the hardest binary search problems in interviews — the difficulty is setting
up the partition invariant correctly.

**Time:** O(log(min(n, m))) | **Space:** O(1)

</details>

---

<a id="q22"></a>
### Q22 — Smallest Divisor Given Threshold

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)


Given an array of integers and a threshold, find the smallest divisor such that
the sum of `ceil(arr[i] / divisor)` for all i is ≤ threshold.

```
Input:  arr = [1, 2, 5, 9],  threshold = 6
Output: 5
```

<details>
<summary>Hint</summary>

Search space: `[1, max(arr)]`. Predicate: `sum(ceil(x/d)) <= threshold`.
Same pattern as Koko — just a different feasibility function.

</details>

<details>
<summary>Answer</summary>

```python
import math

def smallest_divisor(arr: list[int], threshold: int) -> int:
    def feasible(d: int) -> bool:
        return sum(math.ceil(x / d) for x in arr) <= threshold

    lo, hi = 1, max(arr)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

**Why:** This is Koko's problem with a different feasibility check. The pattern
is: identify the answer range, write a O(n) feasibility check that is monotone,
apply Template 2 to find the boundary. Once you see one "search on answer"
problem, you recognise all of them. The divisor increasing → sum decreasing is
the monotone property.

**Time:** O(n log(max arr)) | **Space:** O(1)

</details>

---

<a id="q23"></a>
### Q23 — Find Duplicate in Array (Binary Search on Value Range)

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)


Given an array of n+1 integers where each value is in [1, n], find the duplicate
without modifying the array and using O(1) extra space.

```
Input:  arr = [1, 3, 4, 2, 2]
Output: 2
```

<details>
<summary>Hint</summary>

Binary search on the value range [1, n]. For any mid value, count elements in
arr that are ≤ mid. If count > mid, the duplicate is in [1, mid] by the pigeonhole
principle.

</details>

<details>
<summary>Answer</summary>

```python
def find_duplicate(arr: list[int]) -> int:
    lo, hi = 1, len(arr) - 1   # value range, not index range
    while lo < hi:
        mid = lo + (hi - lo) // 2
        count = sum(1 for x in arr if x <= mid)
        if count > mid:
            hi = mid            # duplicate is in [lo, mid]
        else:
            lo = mid + 1        # duplicate is in [mid+1, hi]
    return lo
```

**Why:** By pigeonhole: if n+1 numbers fit in [1, n] and all are distinct, that
is impossible — one must repeat. For any value `mid`, if more than `mid` numbers
in the array are ≤ `mid`, then the range [1, mid] contains more values than it
has slots — the duplicate is there. Binary search on this count condition is
O(n log n). Note: Floyd's cycle detection is O(n) and O(1) space but is much
harder to derive under pressure.

**Time:** O(n log n) | **Space:** O(1)

</details>

---

<a id="q24"></a>
### Q24 — Allocate Minimum Pages

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)


Given `n` books with page counts and `m` students, allocate contiguous books
to each student such that the maximum pages assigned to any student is minimized.

```
Input:  pages = [12, 34, 67, 90],  m = 2
Output: 113   (student1: [12,34,67]=113, student2: [90]=90 → max=113)
```

<details>
<summary>Hint</summary>

Search space: `[max(pages), sum(pages)]`. Predicate: can we allocate all books
to m students such that no student gets more than `limit` pages?

</details>

<details>
<summary>Answer</summary>

```python
def allocate_min_pages(pages: list[int], m: int) -> int:
    if m > len(pages):
        return -1   # not enough books

    def can_allocate(limit: int) -> bool:
        students = 1
        current = 0
        for p in pages:
            if p > limit:
                return False    # single book exceeds limit
            if current + p > limit:
                students += 1
                current = 0
            current += p
        return students <= m

    lo, hi = max(pages), sum(pages)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if can_allocate(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

**Why:** This is the "split array largest sum" / "painter partition" class of
problems. Binary search on the answer (the maximum allowed pages per student).
The feasibility check greedily assigns pages: keep adding to the current student
until adding the next book would exceed the limit, then start a new student.
If you need more students than m, the limit is too tight.

**Time:** O(n log(sum)) | **Space:** O(1)

</details>

---

<a id="q25"></a>
### Q25 — Off-by-One Bug Hunt

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)


Each of the four functions below has exactly one off-by-one or boundary bug.
Identify and fix each one.

```python
# Bug A: always returns -1 even when element exists
def search_a(arr, target):
    lo, hi = 0, len(arr)       # BUG IS HERE
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target: return mid
        elif arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1

# Bug B: infinite loop on [1, 2], target=2
def search_b(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] < target: lo = mid     # BUG IS HERE
        else: hi = mid
    return lo if arr[lo] == target else -1

# Bug C: first occurrence returns wrong index on [1,1,1,2]
def search_c(arr, target):
    lo, hi = 0, len(arr) - 1
    result = -1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            result = mid
            lo = mid + 1       # BUG IS HERE
        elif arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return result

# Bug D: missing bounds check after loop
def search_d(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target: return mid
        elif arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return lo                  # BUG IS HERE
```

<details>
<summary>Hint</summary>

A: `hi` initialization. B: pointer that never advances. C: direction of search
after match. D: returning without validating the index.

</details>

<details>
<summary>Answer</summary>

```python
# Fix A: hi should be len(arr) - 1 (not len(arr)) to avoid index-out-of-bounds
def search_a_fixed(arr, target):
    lo, hi = 0, len(arr) - 1   # FIXED: was len(arr)
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target: return mid
        elif arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1

# Fix B: lo = mid causes infinite loop when lo+1==hi; must use lo = mid + 1
def search_b_fixed(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] < target: lo = mid + 1  # FIXED: was lo = mid
        else: hi = mid
    return lo if arr[lo] == target else -1

# Fix C: after finding target, move hi = mid - 1 (left), not lo (right)
def search_c_fixed(arr, target):
    lo, hi = 0, len(arr) - 1
    result = -1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            result = mid
            hi = mid - 1       # FIXED: was lo = mid + 1
        elif arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return result

# Fix D: verify arr[lo] == target before returning; lo may point past end
def search_d_fixed(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target: return mid
        elif arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    # FIXED: validate before returning
    if lo < len(arr) and arr[lo] == target:
        return lo
    return -1
```

**Why:** These four bugs cover the most common binary search failure modes:
(A) hi off by one causes `arr[mid]` to access index `len(arr)` — IndexError
or wrong comparison. (B) Not advancing `lo` past `mid` causes an infinite loop
when only two elements remain. (C) Moving `lo` right after a match searches for
LAST occurrence, not first. (D) Returning `lo` without checking causes false
positives when the element is absent.

**Time:** O(log n) each | **Space:** O(1)

</details>

---

## 📂 Navigation

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Visual Explanation →](./visual_explanation.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheetsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md) · [Practice Local](./practice_local.py)
