# Binary Search — Pattern Recognition Guide

Binary search is not just "find a number in a sorted array." It is a general technique for eliminating half
of the search space every step. The hard part is not the algorithm itself — it is recognizing which of the
five major patterns applies to your problem, setting the right loop invariant, and choosing the correct
boundary updates. This guide walks through every pattern with full templates, worked examples, pitfalls,
and decision logic.

---

## How to Use This Guide

Read the "Recognition signals" section for each pattern first. When you see a new problem, match its
description to those signals before writing any code. The wrong template with the right idea will still
produce off-by-one bugs that cost you points in interviews. The right template makes those bugs impossible
by construction.

---

## Pattern 1 — Exact Match

### What It Is

You want to know whether a specific target value exists in a sorted array, and if so, at which index.
You do not care about left-most or right-most occurrence. You just want any valid index.

### Recognition Signals

- "Find the index of target in a sorted array"
- "Search for X in sorted list, return -1 if not found"
- "Does this value exist?"
- "Binary search" with no mention of first/last/leftmost/rightmost

### Template

```python
def exact_match(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1

    while lo <= hi:                        # loop continues while search space is non-empty
        mid = lo + (hi - lo) // 2         # avoids integer overflow (matters in C++/Java)

        if nums[mid] == target:
            return mid                     # found — return immediately
        elif nums[mid] < target:
            lo = mid + 1                   # target is in right half
        else:
            hi = mid - 1                   # target is in left half

    return -1                             # lo > hi: search space exhausted, not found
```

### When Does the Loop End?

The loop runs as long as `lo <= hi`. When `lo > hi`, the search space is empty and target does not exist.
The invariant is: if target is present, it is somewhere in `nums[lo..hi]`. Each iteration shrinks this
range by at least one element. So the loop always terminates.

### Step-Through Example

Array: `[2, 5, 8, 12, 16, 23, 38, 56, 72, 91]`, target = 23

```
Step 1: lo=0, hi=9, mid=4, nums[4]=16  → 16 < 23 → lo = 5
Step 2: lo=5, hi=9, mid=7, nums[7]=56  → 56 > 23 → hi = 6
Step 3: lo=5, hi=6, mid=5, nums[5]=23  → FOUND at index 5
```

Array: `[2, 5, 8, 12, 16, 23, 38]`, target = 10

```
Step 1: lo=0, hi=6, mid=3, nums[3]=12  → 12 > 10 → hi = 2
Step 2: lo=0, hi=2, mid=1, nums[1]=5   → 5 < 10  → lo = 2
Step 3: lo=2, hi=2, mid=2, nums[2]=8   → 8 < 10  → lo = 3
Step 4: lo=3 > hi=2                    → return -1
```

### bisect Equivalent

Python's `bisect` module finds insertion points, not values directly. For exact match:

```python
import bisect

def exact_match_bisect(nums: list[int], target: int) -> int:
    idx = bisect.bisect_left(nums, target)
    # bisect_left returns the leftmost position where target could be inserted
    # If nums[idx] == target, it exists at idx
    # If idx == len(nums), target is larger than all elements
    if idx < len(nums) and nums[idx] == target:
        return idx
    return -1
```

`bisect_left(nums, target)` returns index `i` such that all elements before `i` are `< target`.
If `nums[i] == target`, the element exists.

### Pitfalls

1. Using `mid = (lo + hi) // 2` — this can overflow in languages with fixed-width integers. Python's ints
   are arbitrary precision so it works, but `lo + (hi - lo) // 2` is the safe universal habit.

2. Writing `while lo < hi` instead of `while lo <= hi` — this exits one step too early and misses the
   single-element search space `lo == hi`, causing false negatives.

3. Forgetting the `return -1` — if target is absent, the function silently returns `None` in Python,
   which is falsy but is not the same as -1. Always return explicitly.

4. Using this template when the problem asks for "first" or "last" occurrence — if the array has
   duplicates, `exact_match` returns any index, not the leftmost or rightmost.

---

## Pattern 2 — Left Boundary (First Occurrence)

### What It Is

You want the index of the first (leftmost) occurrence of target in a sorted array that may contain
duplicates. When you find a match, you do not stop — you record the answer and keep searching left
to see if there is an earlier occurrence.

### Recognition Signals

- "Find the first position of target"
- "Find the leftmost index"
- "How many times does X appear?" (combined with right boundary for count = right - left + 1)
- "Find the insertion point from the left"
- "Lower bound" (C++ STL terminology)

### Template

```python
def left_boundary(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1
    ans = -1                              # stores best answer found so far

    while lo <= hi:
        mid = lo + (hi - lo) // 2

        if nums[mid] == target:
            ans = mid                     # found a valid answer, but keep searching left
            hi = mid - 1                  # push hi LEFT to find earlier occurrence
        elif nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1

    return ans
```

### Why `hi = mid - 1` When Found?

When `nums[mid] == target`, `mid` is a valid answer. But there might be an equal element at `mid - 1`,
`mid - 2`, etc. By setting `hi = mid - 1`, we shrink the search space to the left side of `mid`.
The variable `ans` captures the best (leftmost) position found so far. After the loop, `ans` holds
the answer.

### Step-Through Example

Array: `[1, 2, 4, 4, 4, 4, 7, 9, 9]`, target = 4

```
lo=0, hi=8, mid=4, nums[4]=4  → match! ans=4, hi=3
lo=0, hi=3, mid=1, nums[1]=2  → 2 < 4 → lo=2
lo=2, hi=3, mid=2, nums[2]=4  → match! ans=2, hi=1
lo=2 > hi=1                   → loop ends
return ans = 2
```

Verify: `nums[2]=4` is the first 4. Correct.

Array: `[1, 2, 4, 4, 4, 4, 7, 9, 9]`, target = 9

```
lo=0, hi=8, mid=4, nums[4]=4  → 4 < 9 → lo=5
lo=5, hi=8, mid=6, nums[6]=7  → 7 < 9 → lo=7
lo=7, hi=8, mid=7, nums[7]=9  → match! ans=7, hi=6
lo=7 > hi=6                   → loop ends
return ans = 7
```

### bisect Equivalent

```python
import bisect

def left_boundary_bisect(nums: list[int], target: int) -> int:
    idx = bisect.bisect_left(nums, target)
    # bisect_left gives the leftmost insertion point for target
    # If nums[idx] == target, that IS the first occurrence
    if idx < len(nums) and nums[idx] == target:
        return idx
    return -1
```

`bisect_left` returns the index of the first element `>= target`. If that element equals target,
it is the first occurrence.

### Alternative: Cleaner Left Boundary Without `ans` Variable

Some people prefer this form, which merges the "found" and "too big" branches:

```python
def left_boundary_v2(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums)  # NOTE: hi = len(nums), not len(nums) - 1

    while lo < hi:          # NOTE: strict <, not <=
        mid = lo + (hi - lo) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:               # nums[mid] >= target
            hi = mid        # includes the equal case — shrink from right

    # lo == hi at this point
    # lo is the first index where nums[lo] >= target
    if lo < len(nums) and nums[lo] == target:
        return lo
    return -1
```

This version sets `hi = len(nums)` so the loop can naturally produce `lo = len(nums)` when
target is larger than all elements. The invariant is: `lo` is always a valid answer candidate
or points past the end.

### Counting Occurrences

To count how many times `target` appears, combine left and right boundaries:

```python
def count_occurrences(nums: list[int], target: int) -> int:
    left = left_boundary(nums, target)
    if left == -1:
        return 0
    right = right_boundary(nums, target)  # see Pattern 3
    return right - left + 1
```

### Pitfalls

1. Returning immediately when `nums[mid] == target` — this gives you any occurrence, not the first one.
   You must record `ans = mid` and then set `hi = mid - 1` to continue searching left.

2. Forgetting to initialize `ans = -1` — if target is not present, the function must return -1.
   Without initialization, it returns `None` or crashes.

3. Mixing up this template with the `while lo < hi` variant — they use different invariants and
   boundary updates. Do not mix `while lo <= hi` with `hi = mid` (that causes infinite loop when
   `lo == hi == mid`).

---

## Pattern 3 — Right Boundary (Last Occurrence)

### What It Is

You want the index of the last (rightmost) occurrence of target. When you find a match, you record it
and keep searching right.

### Recognition Signals

- "Find the last position of target"
- "Find the rightmost index"
- "Upper bound minus 1" (C++ STL terminology)
- Right side of count occurrences

### Template

```python
def right_boundary(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1
    ans = -1                              # stores best answer found so far

    while lo <= hi:
        mid = lo + (hi - lo) // 2

        if nums[mid] == target:
            ans = mid                     # found a valid answer, but keep searching right
            lo = mid + 1                  # push lo RIGHT to find later occurrence
        elif nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1

    return ans
```

### Why `lo = mid + 1` When Found?

Mirror logic of left boundary. When `nums[mid] == target`, we record `mid` in `ans` then push the
search window to the right by setting `lo = mid + 1`. Any match found later in the right half will
overwrite `ans` with a larger (rightward) index.

### Step-Through Example

Array: `[1, 2, 4, 4, 4, 4, 7, 9, 9]`, target = 4

```
lo=0, hi=8, mid=4, nums[4]=4  → match! ans=4, lo=5
lo=5, hi=8, mid=6, nums[6]=7  → 7 > 4 → hi=5
lo=5, hi=5, mid=5, nums[5]=4  → match! ans=5, lo=6
lo=6 > hi=5                   → loop ends
return ans = 5
```

Verify: `nums[5]=4` is the last 4. Correct.

### bisect Equivalent

```python
import bisect

def right_boundary_bisect(nums: list[int], target: int) -> int:
    idx = bisect.bisect_right(nums, target) - 1
    # bisect_right returns the rightmost insertion point for target
    # One position before that is the last element <= target
    # Check that it actually equals target (not just <= target)
    if idx >= 0 and nums[idx] == target:
        return idx
    return -1
```

`bisect_right(nums, target)` returns the index after the last occurrence of target. Subtract 1
to get the last occurrence, then verify it equals target.

### Full Example: Count Occurrences Using Both Boundaries

```python
import bisect

def count_occurrences(nums: list[int], target: int) -> int:
    left = bisect.bisect_left(nums, target)
    right = bisect.bisect_right(nums, target)
    # right - left = number of times target appears
    return right - left

# Example
nums = [1, 2, 4, 4, 4, 4, 7, 9, 9]
print(count_occurrences(nums, 4))   # Output: 4
print(count_occurrences(nums, 9))   # Output: 2
print(count_occurrences(nums, 5))   # Output: 0
```

### Pitfalls

1. Forgetting that `lo = mid + 1` when found is symmetric to Pattern 2's `hi = mid - 1`. Students often
   copy Pattern 2 and forget to flip the direction.

2. `bisect_right` returns an insertion point, not an index. Always subtract 1, then check bounds and
   equality.

3. When combining left and right boundaries for counting, verify that `left != -1` before computing
   `right - left + 1`. If target is absent, `bisect_right - bisect_left == 0` naturally, but the
   manual template returns `-1` for left, making the formula wrong.

---

## Pattern 4 — Search on Answer (Monotonic Predicate)

### What It Is

This is the most powerful and most frequently misunderstood binary search pattern. Instead of searching
for a value in an array, you binary search on the answer space itself. The trick: if you can define a
boolean function `feasible(x)` that is `False` for small x and `True` for large x (or vice versa),
you can binary search on x to find the transition point.

The answer space looks like: `F F F F F T T T T T`
Binary search finds the first T (or last F), which is the minimum value that satisfies the condition.

### Recognition Signals

- "Find the minimum X such that condition Y is satisfied"
- "Find the maximum X such that condition Y is still satisfied"
- "At least K items", "At most K operations"
- "Minimum time/speed/capacity/days to achieve something"
- The constraint is monotonic: if X works, then X+1 also works (or vice versa)
- The answer is a number in a range, not an index in an array

### Template: Minimize (Find First True)

```python
def search_on_answer_minimize(lo: int, hi: int, feasible) -> int:
    """
    Find the minimum value x in [lo, hi] such that feasible(x) is True.
    Assumes feasible is monotonic: False...False...True...True
    """
    while lo < hi:               # IMPORTANT: strict <, not <=
        mid = lo + (hi - lo) // 2
        if feasible(mid):
            hi = mid             # mid could be the answer, but maybe something smaller works
        else:
            lo = mid + 1         # mid definitely does not work, try bigger

    # After loop: lo == hi, and lo is the first value where feasible is True
    return lo
```

### Template: Maximize (Find Last True)

```python
def search_on_answer_maximize(lo: int, hi: int, feasible) -> int:
    """
    Find the maximum value x in [lo, hi] such that feasible(x) is True.
    Assumes feasible is monotonic: True...True...False...False
    """
    while lo < hi:
        mid = lo + (hi - lo + 1) // 2   # IMPORTANT: ceiling mid to avoid infinite loop
        if feasible(mid):
            lo = mid             # mid works, maybe something larger also works
        else:
            hi = mid - 1         # mid does not work, try smaller

    return lo
```

Note the ceiling mid `(lo + hi + 1) // 2` in the maximize template. This prevents infinite loop
when `lo + 1 == hi` and `feasible(mid)` is True — without the ceiling, `mid == lo`, `lo = mid == lo`,
and the loop never terminates.

---

### Worked Example A: Koko Eating Bananas (LeetCode 875)

**Problem:** Koko has `piles` of bananas. She must eat all bananas in `h` hours. She eats at speed `k`
bananas/hour (one pile per hour, leftover pile carries to next hour). Find the minimum `k`.

**Why binary search on answer?**
- If speed `k` works (can finish in `h` hours), then speed `k+1` also works. Monotonic!
- Answer space: `k` ranges from 1 (slowest) to `max(piles)` (can finish largest pile in 1 hour)

```python
import math
from typing import List

def min_eating_speed(piles: List[int], h: int) -> int:
    def feasible(speed: int) -> bool:
        # Can Koko eat all piles in h hours at this speed?
        total_hours = sum(math.ceil(pile / speed) for pile in piles)
        return total_hours <= h

    lo = 1                  # minimum possible speed
    hi = max(piles)         # maximum needed speed: finish largest pile in 1 hour

    while lo < hi:
        mid = lo + (hi - lo) // 2
        if feasible(mid):
            hi = mid        # speed mid works, try lower
        else:
            lo = mid + 1    # speed mid too slow, try higher

    return lo               # lo == hi: minimum speed that works

# Example
piles = [3, 6, 7, 11]
h = 8
print(min_eating_speed(piles, h))   # Output: 4
# At speed 4: ceil(3/4)=1 + ceil(6/4)=2 + ceil(7/4)=2 + ceil(11/4)=3 = 8 hours exactly
```

**How to determine lo and hi:**
- lo = 1 — the absolute minimum speed (eat 1 banana per hour)
- hi = max(piles) — at this speed, every pile takes exactly 1 hour, total = len(piles) hours

---

### Worked Example B: Minimum Days to Make M Bouquets (LeetCode 1482)

**Problem:** You have `bloomDay[i]` = day flower i blooms. To make one bouquet, you need `k` adjacent
bloomed flowers. Find the minimum day by which you can make `m` bouquets. Return -1 if impossible.

**Why binary search on answer?**
- If day D allows making m bouquets, then day D+1 also allows it (more flowers have bloomed). Monotonic!
- Answer space: day ranges from 1 to max(bloomDay)

```python
from typing import List

def min_days(bloomDay: List[int], m: int, k: int) -> int:
    # Edge case: impossible
    if m * k > len(bloomDay):
        return -1

    def feasible(day: int) -> bool:
        # Can we make m bouquets by this day?
        bouquets = 0
        consecutive = 0
        for bloom in bloomDay:
            if bloom <= day:
                consecutive += 1
                if consecutive == k:
                    bouquets += 1
                    consecutive = 0  # start new bouquet
            else:
                consecutive = 0  # non-bloomed flower breaks the streak
        return bouquets >= m

    lo = 1
    hi = max(bloomDay)

    while lo < hi:
        mid = lo + (hi - lo) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1

    return lo

# Example
bloomDay = [1, 10, 3, 10, 2]
m = 3   # need 3 bouquets
k = 1   # each bouquet needs 1 flower
print(min_days(bloomDay, m, k))   # Output: 3
# By day 3: flowers 0,2,4 have bloomed (days 1,3,2) → 3 single-flower bouquets ✓

bloomDay = [1, 10, 3, 10, 2]
m = 3
k = 2   # each bouquet needs 2 adjacent flowers
print(min_days(bloomDay, m, k))   # Output: -1
# Need 3*2=6 flowers but only 5 exist
```

**How to determine lo and hi:**
- lo = 1 — earliest possible day
- hi = max(bloomDay) — by this day all flowers have bloomed (maximum day you'd ever need)
- Note: you could also set hi = 10^9 if max is expensive to compute, at cost of extra iterations

---

### Worked Example C: Capacity to Ship Packages (LeetCode 1011)

**Problem:** Packages with weights `weights[i]` must be shipped in order within `days` days. A ship
carries at most `capacity` weight per day (consecutive packages, can't split). Find minimum capacity.

**Why binary search on answer?**
- If capacity C works, then C+1 also works. Monotonic!
- Answer space: capacity from max(weights) (must be able to carry heaviest single package) to sum(weights) (ship everything in one day)

```python
from typing import List

def ship_within_days(weights: List[int], days: int) -> int:
    def feasible(capacity: int) -> bool:
        current_load = 0
        days_needed = 1
        for weight in weights:
            if current_load + weight > capacity:
                days_needed += 1      # start new day
                current_load = 0
            current_load += weight
        return days_needed <= days

    lo = max(weights)     # must carry at least the heaviest package
    hi = sum(weights)     # worst case: ship everything in one day

    while lo < hi:
        mid = lo + (hi - lo) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1

    return lo

# Example
weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
days = 5
print(ship_within_days(weights, days))   # Output: 15
# Day 1: [1,2,3,4,5]=15, Day 2: [6,7]=13, Day 3: [8]=8, Day 4: [9]=9, Day 5: [10]=10
```

**How to determine lo and hi:**
- lo = max(weights) — ship cannot carry less than the heaviest package (would get stuck)
- hi = sum(weights) — ship carries everything in a single day (upper bound)
- This [lo, hi] range guarantees a valid answer always exists within it

---

### General Framework for "Search on Answer" Problems

Step 1: Identify the answer variable (speed, capacity, days, temperature, etc.)
Step 2: Determine the direction of monotonicity:
  - "minimum value that satisfies condition" → use minimize template
  - "maximum value that satisfies condition" → use maximize template
Step 3: Write `feasible(x)` — given a candidate answer, can we achieve the goal?
Step 4: Set lo = smallest possible answer, hi = largest possible answer
Step 5: Apply the template and return lo at the end

### Pitfalls

1. Using `while lo <= hi` with `hi = mid` — this causes an infinite loop when `lo == hi == mid`
   because `hi` never decreases below `lo`. Always use `while lo < hi` for this pattern.

2. In the maximize template, forgetting the ceiling mid. When `lo = 5, hi = 6` and `feasible(5)` is
   True: `lo = mid = 5` and the loop never terminates. Use `mid = lo + (hi - lo + 1) // 2`.

3. Setting wrong lo/hi bounds. If the true answer is outside `[lo, hi]`, the function returns a
   wrong value silently. Think carefully about what the minimum and maximum possible answers are.

4. Writing `feasible` incorrectly with off-by-one. Test your feasibility function on small examples
   before trusting the binary search wrapper.

5. Confusing "minimize" and "maximize" — in minimize, `feasible(mid)` being True means `hi = mid`
   (the answer might be mid or smaller). In maximize, it means `lo = mid` (the answer might be mid
   or larger). Mixing these up gives wrong answers that are 1 off.

---

## Pattern 5 — Search in Rotated Sorted Array

### What It Is

A sorted array has been rotated at an unknown pivot. For example, `[4, 5, 6, 7, 0, 1, 2]` is
`[0, 1, 2, 4, 5, 6, 7]` rotated at index 4. You need to find a target, or find the peak, or find
the rotation point.

### Recognition Signals

- "Rotated sorted array"
- "Array that was sorted but then cyclically shifted"
- "Find peak element" (local maximum where neighbors are smaller)
- "Find minimum in rotated sorted array"

### Key Insight

After splitting at any `mid`, at least one of the two halves `[lo..mid]` or `[mid..hi]` is
guaranteed to be normally sorted (no rotation break inside it). Use this sorted half to decide
which side to discard.

### Template: Find Target in Rotated Sorted Array

```python
def search_rotated(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1

    while lo <= hi:
        mid = lo + (hi - lo) // 2

        if nums[mid] == target:
            return mid

        # Determine which half is normally sorted
        if nums[lo] <= nums[mid]:
            # Left half [lo..mid] is sorted
            if nums[lo] <= target < nums[mid]:
                # Target is within the sorted left half
                hi = mid - 1
            else:
                # Target is not in the sorted left half, must be in right
                lo = mid + 1
        else:
            # Right half [mid..hi] is sorted
            if nums[mid] < target <= nums[hi]:
                # Target is within the sorted right half
                lo = mid + 1
            else:
                # Target is not in the sorted right half, must be in left
                hi = mid - 1

    return -1

# Example
nums = [4, 5, 6, 7, 0, 1, 2]
print(search_rotated(nums, 0))   # Output: 4
print(search_rotated(nums, 3))   # Output: -1
```

### Step-Through Example

Array: `[4, 5, 6, 7, 0, 1, 2]`, target = 0

```
lo=0, hi=6, mid=3, nums[3]=7
  nums[0]=4 <= nums[3]=7 → left half [4,5,6,7] is sorted
  Is 4 <= 0 < 7? No (0 < 4) → target not in sorted left half
  lo = 4

lo=4, hi=6, mid=5, nums[5]=1
  nums[4]=0 <= nums[5]=1 → left half [0,1] is sorted
  Is 0 <= 0 < 1? Yes → target in sorted left half
  hi = 4

lo=4, hi=4, mid=4, nums[4]=0 == target → return 4
```

### Template: Find Minimum in Rotated Sorted Array

```python
def find_min_rotated(nums: list[int]) -> int:
    lo, hi = 0, len(nums) - 1

    while lo < hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] > nums[hi]:
            # mid is in the left (larger) part of rotation, minimum is to the right
            lo = mid + 1
        else:
            # mid is in the right (smaller) part, minimum is here or to the left
            hi = mid

    return nums[lo]  # lo == hi at minimum

# Example
print(find_min_rotated([3, 4, 5, 1, 2]))    # Output: 1
print(find_min_rotated([4, 5, 6, 7, 0, 1])) # Output: 0
print(find_min_rotated([1]))                 # Output: 1
```

### Template: Find Peak Element

A peak element is one where `nums[i] > nums[i-1]` and `nums[i] > nums[i+1]`.
Assume `nums[-1] = nums[n] = -infinity`.

```python
def find_peak_element(nums: list[int]) -> int:
    lo, hi = 0, len(nums) - 1

    while lo < hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] > nums[mid + 1]:
            # We are on the descending slope — peak is at mid or left of mid
            hi = mid
        else:
            # We are on the ascending slope — peak is to the right of mid
            lo = mid + 1

    return lo  # lo == hi at the peak

# Example
print(find_peak_element([1, 2, 3, 1]))        # Output: 2 (nums[2]=3 is peak)
print(find_peak_element([1, 2, 1, 3, 5, 6, 4])) # Output: 5 (nums[5]=6 is peak)
```

### Handling Duplicates in Rotated Array

When the array has duplicates, the condition `nums[lo] <= nums[mid]` is ambiguous — you cannot
determine which half is sorted. The worst case becomes O(n):

```python
def search_rotated_with_duplicates(nums: list[int], target: int) -> bool:
    lo, hi = 0, len(nums) - 1

    while lo <= hi:
        mid = lo + (hi - lo) // 2

        if nums[mid] == target:
            return True

        if nums[lo] == nums[mid] == nums[hi]:
            # Cannot determine which side is sorted — shrink both ends
            lo += 1
            hi -= 1
        elif nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1

    return False
```

### Pitfalls

1. Using `nums[lo] < nums[mid]` (strict) instead of `nums[lo] <= nums[mid]`. When `lo == mid`
   (single element left half), equality is needed to correctly identify it as "sorted."

2. In `find_min_rotated`, comparing `nums[mid]` against `nums[hi]` (not `nums[lo]`). The minimum
   is always in the right portion relative to the rotation, so comparing against the right boundary
   is the correct signal.

3. Not handling the case where the array was not rotated at all — the template handles this
   correctly because one half will always be sorted, but it is worth verifying.

---

## Pattern 6 — Binary Search on Float (Continuous Space)

### What It Is

When the answer is a real number (not an integer), you cannot enumerate answer candidates.
Instead, you run the loop for a fixed number of iterations or until the interval is small enough.

### Recognition Signals

- "Find the square root / cube root / nth root"
- "Find a real number with precision 1e-6"
- "Continuous optimization: find the minimum of a unimodal function"

### Template: Fixed Iterations

```python
def binary_search_float(lo: float, hi: float, feasible, iterations: int = 100) -> float:
    """
    Run binary search for a fixed number of iterations.
    After 100 iterations, the interval has shrunk by factor 2^100 ≈ 10^30.
    """
    for _ in range(iterations):
        mid = (lo + hi) / 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid
    return lo
```

### Template: Epsilon-Based

```python
def binary_search_epsilon(lo: float, hi: float, feasible, eps: float = 1e-9) -> float:
    while hi - lo > eps:
        mid = (lo + hi) / 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid
    return lo
```

### Worked Example: Square Root

```python
def sqrt_binary_search(n: float) -> float:
    if n < 0:
        raise ValueError("Cannot take square root of negative number")
    if n == 0 or n == 1:
        return n

    lo, hi = 0.0, max(1.0, n)  # hi = n for n > 1, hi = 1 for 0 < n < 1

    while hi - lo > 1e-10:
        mid = (lo + hi) / 2
        if mid * mid <= n:
            lo = mid   # mid^2 <= n means mid might be the answer or too small
        else:
            hi = mid   # mid^2 > n means mid is too large

    return lo

print(f"{sqrt_binary_search(2):.10f}")    # 1.4142135624
print(f"{sqrt_binary_search(9):.10f}")    # 3.0000000000
print(f"{sqrt_binary_search(0.25):.10f}") # 0.5000000000
```

### Worked Example: Cube Root

```python
def cbrt_binary_search(n: float) -> float:
    negative = n < 0
    n = abs(n)

    lo, hi = 0.0, max(1.0, n)

    while hi - lo > 1e-10:
        mid = (lo + hi) / 2
        if mid ** 3 <= n:
            lo = mid
        else:
            hi = mid

    return -lo if negative else lo

print(f"{cbrt_binary_search(27):.10f}")   # 3.0000000000
print(f"{cbrt_binary_search(-8):.10f}")   # -2.0000000000
print(f"{cbrt_binary_search(2):.10f}")    # 1.2599210499
```

### Worked Example: Integer Square Root (Floor)

```python
def isqrt_binary_search(n: int) -> int:
    """Return floor(sqrt(n)) for non-negative integer n."""
    if n < 2:
        return n

    lo, hi = 1, n // 2 + 1  # answer is always <= n//2 for n >= 4

    while lo < hi:
        mid = lo + (hi - lo + 1) // 2  # ceiling mid (maximize template)
        if mid * mid <= n:
            lo = mid   # mid^2 <= n, mid could be the floor sqrt
        else:
            hi = mid - 1

    return lo

print(isqrt_binary_search(16))   # 4
print(isqrt_binary_search(17))   # 4
print(isqrt_binary_search(25))   # 5
print(isqrt_binary_search(26))   # 5
```

### Pitfalls

1. Setting `hi = n` when `0 < n < 1` — the square root of 0.25 is 0.5, which is greater than 0.25.
   For numbers in (0,1), sqrt is larger than the number itself. Always use `hi = max(1.0, n)`.

2. Using integer division `//` inside the loop — this destroys the continuous nature of the search
   and is only appropriate for the integer floor-sqrt variant.

3. Choosing too large an epsilon or too few iterations — the result will not be accurate enough.
   100 iterations is almost always sufficient: the interval shrinks from `hi - lo ≤ 10^9` to
   `10^9 / 2^100 ≈ 10^-21`, far beyond double precision.

4. Forgetting negative inputs for odd roots (cube root of -8 = -2). Handle the sign separately.

---

## Full Decision Guide: Which Pattern to Use?

```
Problem description says...
│
├─ "find index of X in sorted array" or "does X exist?"
│   └─ Pattern 1: Exact Match (while lo <= hi, return mid when found)
│
├─ "find FIRST/LEFTMOST occurrence" or "lower bound"
│   └─ Pattern 2: Left Boundary (record ans, set hi = mid - 1 when found)
│
├─ "find LAST/RIGHTMOST occurrence" or "upper bound"
│   └─ Pattern 3: Right Boundary (record ans, set lo = mid + 1 when found)
│
├─ "minimum/maximum value that satisfies condition" or "at least/at most K"
│   ├─ Check: is the answer a specific value in a RANGE (not an index)?
│   ├─ Check: can you write feasible(x) in O(n) or O(n log n)?
│   └─ Pattern 4: Search on Answer (while lo < hi, binary search on feasible())
│
├─ "rotated sorted array" or "find peak element" or "find rotation point"
│   └─ Pattern 5: Rotated Array (check which half is sorted, navigate accordingly)
│
└─ "find sqrt/cbrt" or "continuous precision" or "real-valued answer"
    └─ Pattern 6: Float Binary Search (while hi - lo > eps, use float mid)
```

---

## Quick Reference: All Templates Side by Side

```python
# Pattern 1: Exact Match
def exact(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] == target: return mid
        elif nums[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1

# Pattern 2: Left Boundary
def left(nums, target):
    lo, hi, ans = 0, len(nums) - 1, -1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] == target: ans = mid; hi = mid - 1
        elif nums[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return ans

# Pattern 3: Right Boundary
def right(nums, target):
    lo, hi, ans = 0, len(nums) - 1, -1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] == target: ans = mid; lo = mid + 1
        elif nums[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return ans

# Pattern 4: Search on Answer (Minimize)
def minimize(lo, hi, feasible):
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if feasible(mid): hi = mid
        else: lo = mid + 1
    return lo

# Pattern 4: Search on Answer (Maximize)
def maximize(lo, hi, feasible):
    while lo < hi:
        mid = lo + (hi - lo + 1) // 2
        if feasible(mid): lo = mid
        else: hi = mid - 1
    return lo

# Pattern 6: Float Binary Search
def float_search(lo, hi, feasible, eps=1e-9):
    while hi - lo > eps:
        mid = (lo + hi) / 2
        if feasible(mid): hi = mid
        else: lo = mid
    return lo
```

---

## Common Off-by-One Summary

| Mistake | Symptom | Fix |
|---|---|---|
| `while lo < hi` with exact match | Misses single-element arrays | Use `while lo <= hi` |
| `while lo <= hi` with `hi = mid` | Infinite loop | Use `while lo < hi` |
| `mid = (lo + hi) // 2` in maximize | Infinite loop when `lo + 1 == hi` | Use `(lo + hi + 1) // 2` |
| Return immediately on match | Finds any occurrence, not first/last | Record `ans`, keep searching |
| `parent = [0] * n` | Wrong component initialization | Use `parent = list(range(n))` |
| `hi = len(nums) - 1` in left-boundary v2 | Misses out-of-range check | Use `hi = len(nums)` |

---

## Practice Problems by Pattern

**Pattern 1 (Exact Match):**
- LeetCode 704: Binary Search
- LeetCode 374: Guess Number Higher or Lower

**Pattern 2 (Left Boundary):**
- LeetCode 34: Find First and Last Position (left half)
- LeetCode 278: First Bad Version

**Pattern 3 (Right Boundary):**
- LeetCode 34: Find First and Last Position (right half)

**Pattern 4 (Search on Answer):**
- LeetCode 875: Koko Eating Bananas
- LeetCode 1482: Minimum Number of Days to Make m Bouquets
- LeetCode 1011: Capacity to Ship Packages Within D Days
- LeetCode 410: Split Array Largest Sum
- LeetCode 1231: Divide Chocolate

**Pattern 5 (Rotated Array):**
- LeetCode 33: Search in Rotated Sorted Array
- LeetCode 153: Find Minimum in Rotated Sorted Array
- LeetCode 162: Find Peak Element
- LeetCode 81: Search in Rotated Sorted Array II (with duplicates)

**Pattern 6 (Float):**
- LeetCode 69: Sqrt(x)
- LeetCode 367: Valid Perfect Square

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Real World Usage →](./real_world_usage.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
