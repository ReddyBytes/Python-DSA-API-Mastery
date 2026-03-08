# Binary Search — Cheatsheet

---

## Variants Overview Table

| Variant              | Returns              | Loop condition | Left update    | Right update   | Answer         |
|----------------------|----------------------|----------------|----------------|----------------|----------------|
| Exact match          | index or -1          | left <= right  | mid + 1        | mid - 1        | return mid     |
| Left bound           | first occurrence     | left < right   | mid + 1        | mid            | return left    |
| Right bound          | last occurrence      | left < right   | mid            | mid - 1        | return left    |
| Search on answer     | min/max satisfying   | left < right   | mid + 1        | mid            | return left    |

---

## Mid Calculation (Overflow-Safe)

```python
mid = left + (right - left) // 2      # ALWAYS use this
# NOT: mid = (left + right) // 2      # can overflow in other languages
# Python ints don't overflow, but good habit for interviews
```

---

## Template 1: Standard (Exact Match)

```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:               # <= because right is inclusive
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid                 # found
        elif arr[mid] < target:
            left = mid + 1             # target is to the right
        else:
            right = mid - 1            # target is to the left
    return -1                          # not found
```

---

## Template 2: Left Bound (First Occurrence)

Finds the leftmost index where `arr[i] >= target` (or first occurrence of target).

```python
def left_bound(arr, target):
    left, right = 0, len(arr)          # right = len(arr) — open interval
    while left < right:                # strict < — loop ends when left==right
        mid = left + (right - left) // 2
        if arr[mid] < target:
            left = mid + 1             # too small — move right
        else:
            right = mid                # could be answer — keep mid
    # left == right — this is the answer index
    if left < len(arr) and arr[left] == target:
        return left
    return -1
```

### Equivalent using bisect

```python
import bisect
i = bisect.bisect_left(arr, target)
if i < len(arr) and arr[i] == target:
    return i
return -1
```

---

## Template 3: Right Bound (Last Occurrence)

```python
def right_bound(arr, target):
    left, right = 0, len(arr)
    while left < right:
        mid = left + (right - left) // 2
        if arr[mid] <= target:
            left = mid + 1             # could be answer but keep searching right
        else:
            right = mid
    # left - 1 is the rightmost index <= target
    if left - 1 >= 0 and arr[left - 1] == target:
        return left - 1
    return -1
```

### Equivalent using bisect

```python
import bisect
i = bisect.bisect_right(arr, target) - 1
if i >= 0 and arr[i] == target:
    return i
return -1
```

---

## Template 4: Search on Answer (Monotonic Predicate)

Use when: "find minimum X such that condition(X) is True"

```
condition:  F F F F T T T T T
                    ^
                  answer = left bound of True
```

```python
def search_on_answer(lo, hi, condition):
    # condition(x) returns True/False, monotonically non-decreasing
    left, right = lo, hi
    while left < right:
        mid = left + (right - left) // 2
        if condition(mid):
            right = mid                # mid could be answer, narrow right
        else:
            left = mid + 1             # mid not answer, narrow left
    return left                        # left == right == answer
```

### Example: Minimum days to make m bouquets

```python
def min_days(bloomDay, m, k):
    def can_make(day):
        bouquets = flowers = 0
        for d in bloomDay:
            flowers = flowers + 1 if d <= day else 0
            if flowers == k:
                bouquets += 1
                flowers = 0
        return bouquets >= m

    left, right = min(bloomDay), max(bloomDay)
    while left < right:
        mid = left + (right - left) // 2
        if can_make(mid):
            right = mid
        else:
            left = mid + 1
    return left if can_make(left) else -1
```

### Example: Koko Eating Bananas

```python
def min_eating_speed(piles, h):
    import math
    def can_eat(speed):
        return sum(math.ceil(p / speed) for p in piles) <= h

    left, right = 1, max(piles)
    while left < right:
        mid = left + (right - left) // 2
        if can_eat(mid):
            right = mid
        else:
            left = mid + 1
    return left
```

---

## Python bisect Module Reference

```python
import bisect

arr = [1, 2, 2, 3, 4, 4, 5]

bisect.bisect_left(arr, 2)   # → 1   (leftmost position to insert 2)
bisect.bisect_right(arr, 2)  # → 3   (rightmost position to insert 2)
bisect.bisect(arr, 2)        # → 3   (alias for bisect_right)

bisect.insort_left(arr, x)   # inserts x keeping arr sorted
bisect.insort_right(arr, x)  # same but inserts to the right of existing

# Count occurrences of x in sorted arr
count = bisect.bisect_right(arr, x) - bisect.bisect_left(arr, x)

# Find floor (largest element <= x)
i = bisect.bisect_right(arr, x) - 1
floor_val = arr[i] if i >= 0 else None

# Find ceiling (smallest element >= x)
i = bisect.bisect_left(arr, x)
ceil_val = arr[i] if i < len(arr) else None
```

---

## Recognition Signals

```
"sorted array"                         → binary search (exact or bound)
"O(log n) required"                    → binary search
"find first/last/leftmost/rightmost"   → left/right bound templates
"find minimum X satisfying condition"  → search on answer (Template 4)
"find maximum X satisfying condition"  → search on answer (reversed)
"rotated sorted array"                 → modified binary search
"matrix search" (sorted rows/cols)     → treat as 1D or two-step BS
```

---

## Common Problems Reference

| Problem                              | Template           | Notes                                    |
|--------------------------------------|--------------------|------------------------------------------|
| Binary Search (LC 704)               | T1: Exact          | Basic                                    |
| First Bad Version (LC 278)           | T2: Left bound     | Minimize first True                      |
| Find First/Last in Sorted Array      | T2 + T3            | Two passes                               |
| Search in Rotated Sorted Array       | T1 modified        | Determine which half is sorted           |
| Find Minimum in Rotated (LC 153)     | T2 variation       | Compare mid to right                     |
| Sqrt(x) (LC 69)                      | T4: Search answer  | Find max k where k*k <= x                |
| Koko Eating Bananas (LC 875)         | T4: Search answer  | Min speed, condition = feasible          |
| Split Array Largest Sum (LC 410)     | T4: Search answer  | Min largest sum for m subarrays          |
| Median of Two Sorted Arrays (LC 4)   | T1 hard variant    | Binary search on partition               |
| Find Peak Element (LC 162)           | T1 modified        | Move toward larger neighbor              |

---

## Rotated Sorted Array Template

```python
def search_rotated(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        # left half is sorted
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        # right half is sorted
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
```

---

## Binary Search on Real Numbers

```python
def binary_search_real(lo, hi, condition, eps=1e-9):
    # Use iteration count instead of epsilon comparison
    for _ in range(100):               # 100 iterations → precision ~2^-100
        mid = (lo + hi) / 2
        if condition(mid):
            hi = mid
        else:
            lo = mid
    return lo
# Example: find cube root of x
# condition = lambda m: m*m*m >= x
```

---

## Common Mistakes

| Mistake                                   | Fix                                                   |
|-------------------------------------------|-------------------------------------------------------|
| `left <= right` vs `left < right`         | Exact match: `<=`. Bound templates: `<`              |
| `right = mid` vs `right = mid - 1`        | Bound templates use `right = mid` (mid stays candidate)|
| Infinite loop: left never advances        | Ensure `left = mid + 1` when condition fails          |
| Wrong mid when right=len(arr)             | `mid = left + (right - left) // 2` handles open right |
| Forgetting to validate answer at end      | After loop: `arr[left] == target` check              |
| Using `//` vs `/` for real number search  | Use `/` for floats, `//` for integer search           |
| Off-by-one on search_on_answer bounds     | lo/hi should cover all possible answers              |

---

## Complexity Reference

| Operation                  | Time       | Space  |
|----------------------------|------------|--------|
| Standard binary search     | O(log n)   | O(1)   |
| Search on answer           | O(log(hi-lo) * T(condition)) | O(1) |
| bisect.bisect_left/right   | O(log n)   | O(1)   |
| bisect.insort              | O(n)       | O(1)   |
