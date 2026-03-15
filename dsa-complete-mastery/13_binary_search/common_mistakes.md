# Binary Search — Common Mistakes & Error Prevention Guide

> **Who this is for:** Engineers who understand binary search conceptually but keep writing infinite loops, off-by-one bugs, or getting wrong answers on edge cases under interview pressure.

---

## Mistake #1: Integer Overflow in Mid Calculation

Computing `mid` with naive addition can overflow in languages with fixed-size integers. Python doesn't overflow, but the pattern matters for interviews where you discuss C++/Java solutions.

**WRONG (overflows in C++/Java, fine in Python):**
```python
mid = (left + right) // 2
# In C++ with 32-bit ints: left=1_000_000_000, right=1_500_000_000
# left + right = 2_500_000_000 — overflows signed 32-bit int (max ~2.1B)
```

**CORRECT (safe in all languages):**
```python
mid = left + (right - left) // 2
# right - left is always <= right, so no overflow
# Algebraically identical: left + (right - left)//2 == (left + right)//2
```

**Why it matters in Python:** It doesn't overflow, but writing it the safe way in interviews signals you understand cross-language considerations — an important signal for senior roles. You will lose marks for the naive version in a C++ context.

**Demonstration:**
```python
left, right = 10**9, 2 * 10**9

safe_mid = left + (right - left) // 2
naive_mid = (left + right) // 2

assert safe_mid == naive_mid   # Both correct in Python
# But only safe_mid is portable
```

---

## Mistake #2: Infinite Loop from Wrong Loop Condition

Choosing `while left < right` vs `while left <= right` incorrectly causes the loop to never terminate.

**WRONG (infinite loop):**
```python
def search(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:                    # Exits when left == right
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid                     # BUG: if left=0, right=1, mid=0
            # left stays 0 forever — infinite loop
        else:
            right = mid - 1
```

**CORRECT:**
```python
def search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:                   # Allows left == right (single element)
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1                 # Advance past mid
        else:
            right = mid - 1               # Retreat before mid
    return -1
```

**Why it fails:** When `left=0, right=1`, `mid=0`. If the target is greater, we set `left = mid = 0` — no progress. The search space never shrinks and the loop runs forever. The fix is `left = mid + 1` to guarantee the search space shrinks by at least one element per iteration.

**Test case that exposes the bug:**
```python
nums = [1, 3]
print(search(nums, 3))   # Hangs forever with the wrong version
```

---

## Mistake #3: Wrong Boundary Update

Using `left = mid` instead of `left = mid + 1` (or vice versa) either causes infinite loops or skips the answer.

**WRONG:**
```python
def search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] < target:
            left = mid      # BUG: should be mid + 1
        else:
            right = mid - 1
    return left

# [1, 2, 3, 4, 5], target=3
# left=0, right=4, mid=2, nums[2]=3 — goes to else, right=1
# left=0, right=1, mid=0, nums[0]=1 < 3 — left = mid = 0
# left=0, right=1, mid=0 ... infinite loop
```

**CORRECT:**
```python
def search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1   # mid is confirmed not the target — skip it
        else:
            right = mid - 1  # mid is confirmed not the target — skip it
    return -1
```

**Rule of thumb:**
- Use `left = mid + 1` and `right = mid - 1` for standard exact-match search.
- Use `right = mid` (not `mid - 1`) only when you are preserving mid as a candidate answer (first occurrence patterns).

**Test case:**
```python
nums = [1, 2, 3, 4, 5]
assert search(nums, 1) == 0
assert search(nums, 5) == 4
assert search(nums, 6) == -1
```

---

## Mistake #4: Returning the Wrong Pointer After the Loop

After the loop exits, `left`, `right`, and `mid` point to different positions. Returning the wrong one gives an incorrect answer.

**WRONG:**
```python
def first_occurrence(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid
    return right   # BUG: should be left (they're equal here, but the intent matters)
                   # More dangerously: returning mid from last iteration is wrong
```

**CORRECT:**
```python
def first_occurrence(nums, target):
    left, right = 0, len(nums) - 1
    result = -1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            result = mid     # Record candidate and keep searching left
            right = mid - 1
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return result
```

**Why it fails:** When `while left < right` exits, `left == right` and they are equal. When `while left <= right` exits, `left > right` and `left` is one past the last searched position. Returning `mid` from the last iteration is especially dangerous — mid is stale and may be nowhere near the answer.

**Test case:**
```python
nums = [1, 2, 2, 2, 3]
assert first_occurrence(nums, 2) == 1   # Not 2 or 3
assert first_occurrence(nums, 5) == -1
```

---

## Mistake #5: Applying Binary Search to an Unsorted Array

Binary search requires a sorted (or monotonic) search space. On unsorted data it produces silently wrong answers with no error.

**WRONG:**
```python
nums = [3, 1, 4, 1, 5, 9, 2, 6]   # Unsorted

def search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

print(search(nums, 4))   # Returns -1 even though 4 is at index 2
```

**CORRECT:**
```python
# Option 1: sort first (O(n log n) total)
nums_sorted = sorted(nums)
result = search(nums_sorted, 4)

# Option 2: assert sorted before searching
def safe_search(nums, target):
    assert all(nums[i] <= nums[i+1] for i in range(len(nums)-1)), "Array must be sorted"
    # ... binary search ...
```

**Why it fails:** Binary search works by eliminating half the search space based on whether `nums[mid]` is too small or too large. This reasoning is only valid if elements are ordered. On unsorted data, discarding a half may discard the answer.

**Test case that exposes the bug:**
```python
unsorted = [3, 1, 4, 1, 5, 9, 2, 6]
# 4 is in the array but binary search may return -1
assert 4 in unsorted          # True — element exists
assert search(unsorted, 4) == -1  # Wrong answer, no exception
```

---

## Mistake #6: Wrong Condition for First vs Last Occurrence

Finding the first or last occurrence of a target in an array with duplicates requires different boundary updates. Using the wrong one finds *an* occurrence, not the right one.

**WRONG (finds any occurrence, not first):**
```python
def first_occurrence(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid          # Stops immediately — may be middle of a run
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

**CORRECT (first occurrence):**
```python
def first_occurrence(nums, target):
    left, right = 0, len(nums) - 1
    result = -1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            result = mid        # Record and continue searching LEFT
            right = mid - 1
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return result

def last_occurrence(nums, target):
    left, right = 0, len(nums) - 1
    result = -1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            result = mid        # Record and continue searching RIGHT
            left = mid + 1
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return result
```

**Test case:**
```python
nums = [1, 2, 2, 2, 2, 3]
assert first_occurrence(nums, 2) == 1
assert last_occurrence(nums, 2)  == 4
```

---

## Mistake #7: Not Checking Whether the Target Exists

After binary search, the position `left` may point to a valid index but hold a different value. Forgetting this check produces wrong answers for missing targets.

**WRONG:**
```python
import bisect

def search_insert(nums, target):
    pos = bisect.bisect_left(nums, target)
    return pos   # Returns insertion point — could be where ANY value sits
```

**CORRECT:**
```python
import bisect

def search_insert(nums, target):
    pos = bisect.bisect_left(nums, target)
    if pos < len(nums) and nums[pos] == target:
        return pos          # Found
    return -1               # Or return pos for "insert here" semantics
```

**Why it fails:** `bisect_left` returns the leftmost position where `target` could be inserted to keep the array sorted. If `target` is not present, that position exists but holds a different (larger) value. Without the bounds check `pos < len(nums)` you also risk an index-out-of-bounds error.

**Test case:**
```python
nums = [1, 3, 5, 7]
assert search_insert(nums, 5) == 2
assert search_insert(nums, 4) == -1   # Not present — must return -1, not 2
assert search_insert(nums, 9) == -1   # Past end — without bounds check: IndexError
```

---

## Mistake #8: Binary Search on Answer — Violating the Monotonicity Assumption

"Binary search on the answer" works only when the validation function is monotonic: all values below the answer are invalid and all values at/above it are valid (or vice versa). Using a non-monotonic function gives silent wrong answers.

**WRONG (non-monotonic validation):**
```python
# Problem: find the minimum number of days to make m bouquets
# Bug: validation function has a non-monotonic edge case due to logic error

def can_make(nums, days, m, k):
    count = bouquets = 0
    for bloom in nums:
        if bloom <= days:
            count += 1
            if count == k:
                bouquets += 1
                count = 0   # BUG: should NOT reset if bouquets already >= m
        else:
            count = 0
    return bouquets >= m    # May return True, False, True as days increases — non-monotonic
```

**CORRECT:**
```python
def can_make(nums, days, m, k):
    count = bouquets = 0
    for bloom in nums:
        if bloom <= days:
            count += 1
        else:
            bouquets += count // k   # Tally complete groups
            count = 0
    bouquets += count // k           # Handle trailing group
    return bouquets >= m             # Strictly monotonic: more days => same or more bouquets

def min_days(nums, m, k):
    if m * k > len(nums):
        return -1
    left, right = min(nums), max(nums)
    while left < right:
        mid = left + (right - left) // 2
        if can_make(nums, mid, m, k):
            right = mid
        else:
            left = mid + 1
    return left
```

**Why it fails:** Binary search eliminates half the space based on the monotonicity invariant. If `can_make(days=5)` is True but `can_make(days=6)` is False and `can_make(days=7)` is True, binary search may converge on the wrong boundary. Always verify: "Is it true that if X days works, X+1 days also works?"

---

## Mistake #9: Using bisect_left vs bisect_right Incorrectly

`bisect_left` and `bisect_right` return different positions when the target is present in the array.

**WRONG:**
```python
import bisect

nums = [1, 2, 2, 2, 3]
target = 2

# Want: count of elements equal to target
count = bisect.bisect_left(nums, target) - bisect.bisect_right(nums, target)
# bisect_left=1, bisect_right=4 => 1 - 4 = -3   WRONG sign
```

**CORRECT:**
```python
import bisect

nums = [1, 2, 2, 2, 3]
target = 2

right_boundary = bisect.bisect_right(nums, target)   # 4: insertion point AFTER all 2s
left_boundary  = bisect.bisect_left(nums, target)    # 1: insertion point BEFORE first 2
count = right_boundary - left_boundary               # 3: correct

# bisect_left  — index of first element >= target
# bisect_right — index of first element >  target (one past last occurrence)
```

**Reference table:**
```
Array: [1, 2, 2, 2, 3]
Index:  0  1  2  3  4

bisect_left(arr, 2)  = 1   (first position where 2 fits on the left)
bisect_right(arr, 2) = 4   (first position where 2 fits on the right)
bisect_left(arr, 0)  = 0   (before everything)
bisect_right(arr, 5) = 5   (after everything)
```

**Test cases:**
```python
nums = [1, 2, 2, 2, 3]
assert bisect.bisect_left(nums, 2)  == 1
assert bisect.bisect_right(nums, 2) == 4
assert bisect.bisect_right(nums, 2) - bisect.bisect_left(nums, 2) == 3   # count of 2s
```

---

## Pre-Submission Checklist

Before submitting any binary search solution, answer these 6 questions:

- [ ] **1. Is the search space sorted (or monotonic)?**
  Binary search on unsorted data gives silent wrong answers. Confirm ordering before applying it.

- [ ] **2. Is mid computed safely?**
  Use `mid = left + (right - left) // 2`. Safe in all languages, not just Python.

- [ ] **3. Which loop condition — `left <= right` or `left < right`?**
  Use `left <= right` for exact-match search. Use `left < right` for boundary-finding patterns where you preserve mid as a candidate.

- [ ] **4. Are boundary updates `mid+1`/`mid-1` or `mid`?**
  In exact-match search, always `left = mid + 1` and `right = mid - 1`.
  In first/last occurrence, one boundary stays at `mid` (to preserve the candidate).

- [ ] **5. What is returned after the loop?**
  `left`, `right`, and `mid` have different meanings post-loop. State which you return and why. Check the value at `left` before returning it as "found."

- [ ] **6. Is `bisect_left` or `bisect_right` the right tool?**
  `bisect_left` gives the index of the first element `>= target`.
  `bisect_right` gives the index of the first element `> target` (one past the last occurrence).
  The count of a target is always `bisect_right - bisect_left`.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Real World Usage](./real_world_usage.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)
